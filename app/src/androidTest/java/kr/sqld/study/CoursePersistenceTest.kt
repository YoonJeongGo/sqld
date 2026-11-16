package kr.sqld.study

import android.content.Context
import androidx.room.Room
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.encodeToString
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import java.util.UUID

/** Separate test databases protect the installed app's personal records. */
@RunWith(AndroidJUnit4::class)
class CoursePersistenceTest {
    private lateinit var context:Context
    private val databases=mutableListOf<StudyDatabase>()
    private val names=mutableListOf<String>()
    private fun newName()="sqld-course-test-${UUID.randomUUID()}.db".also{names+=it}
    private fun open(name:String)=Room.databaseBuilder(context,StudyDatabase::class.java,name).build().also{databases+=it}
    private suspend fun repository(name:String=newName())=StudyRepository(context,open(name),projectPreferences=false).also{it.initialize()}
    private suspend fun graded(repo:StudyRepository) {
        repo.update { StudyEngine.createSession(it,repo.pack,listOf(repo.pack.practice().first()),"immediate","보존 검사",1_000,100,1,42) }
        repo.update { state ->
            val session=state.sessions.first{it.id==state.activeSessionId}
            StudyEngine.grade(StudyEngine.select(state,session.id,0,session.items.single().question.correctChoiceIds.single()),session.id,0,2_000)
        }
    }
    private fun progress(repo:StudyRepository):CourseProgress {
        val lesson=repo.course.lessons.first()
        val example=lesson.examples.first()
        val check=lesson.selfChecks.first()
        return CourseProgress(lesson.id,readVersion=lesson.version,scroll=256,section="examples",
            exampleSteps=mapOf(example.id to 1),revealedResults=listOf(example.id),
            checks=listOf(CourseCheckProgress(check.id,"내 말로 적은 답: NULL ≠ 0",true,"review")),updatedAt=3_000)
    }
    @Before fun before(){context=InstrumentationRegistry.getInstrumentation().targetContext}
    @After fun after(){databases.forEach{if(it.isOpen)it.close()};names.forEach{context.deleteDatabase(it)}}

    @Test fun versionOneDatabaseUpgradesInPlacePreservingQuizSnapshotsAndAnnotations()=runBlocking {
        val name=newName();val first=repository(name);graded(first)
        val note=first.pack.notes.first();val block=note.blocks.first()
        val old=first.state.value.copy(schemaVersion=1,
            annotations=listOf(Annotation("old-annotation",note.id,block.id,block.text.take(15),"이전 메모","underline",2_500)),
            lastNoteId=note.id)
        val oldJson=Codec.encodeToString(old).replace(",\"courseProgress\":[],\"lastLessonId\":null","")
        assertFalse(oldJson.contains("courseProgress"))
        first.db.dao().save(StateRow(revision=old.revision,payload=oldJson))
        first.db.close()
        val second=repository(name)
        val restored=second.state.value
        assertEquals(BackupCodec.CURRENT_VERSION,restored.schemaVersion)
        assertEquals(old.sessions,restored.sessions)
        assertEquals(old.submissions,restored.submissions)
        assertEquals(old.annotations,restored.annotations)
        assertEquals(1,second.db.dao().submissionCount())
        assertTrue(restored.courseProgress.isEmpty())
        assertEquals(BackupCodec.CURRENT_VERSION,Codec.decodeFromString<StudyState>(second.db.dao().state()!!.payload).schemaVersion)
    }

    @Test fun reopenedDatabaseKeepsSeparateCoursePositionDraftSelfRatingAndAllQuizRecords()=runBlocking {
        val name=newName();val first=repository(name);graded(first)
        val courseProgress=progress(first)
        val saved=first.update { state ->CourseStudy.update(state,courseProgress.lessonId,{courseProgress},now=3_000) }
        first.db.close()
        val second=repository(name)
        assertEquals(saved,second.state.value)
        assertEquals(courseProgress,second.state.value.courseProgress.single())
        assertEquals(saved.submissions,second.state.value.submissions)
        assertEquals(1,second.db.dao().submissionCount())
        assertEquals(saved,BackupCodec.decode(second.export()))
    }

    @Test fun failedCourseSaveAndRestoreLeaveOriginalCourseAndQuizRecordsUntouched()=runBlocking {
        val repo=repository();graded(repo)
        val courseProgress=progress(repo)
        val before=repo.update { CourseStudy.update(it,courseProgress.lessonId,{courseProgress},now=3_000) }
        val row=repo.db.dao().state();val recovery=repo.recoveryCandidate()
        val generation=repo.restoreGeneration
        repo.failNextWrite=true
        assertNotNull(runCatching{repo.update{CourseStudy.update(it,courseProgress.lessonId,{p->p.copy(scroll=999)},now=4_000)}}.exceptionOrNull())
        assertEquals(before,repo.state.value)
        assertEquals(row,repo.db.dao().state())
        repo.failNextWrite=true
        val candidate=StudyState(courseProgress=listOf(courseProgress.copy(scroll=999)),lastLessonId=courseProgress.lessonId)
        assertNotNull(runCatching{repo.restore(candidate)}.exceptionOrNull())
        assertEquals(before,repo.state.value)
        assertEquals(row,repo.db.dao().state())
        assertEquals(1,repo.db.dao().submissionCount())
        assertEquals(recovery,repo.recoveryCandidate())
        assertEquals(generation,repo.restoreGeneration)
    }

    @Test fun queuedReaderSaveFromBeforeRestoreCannotOverwriteRestoredPositionOrRecords()=runBlocking {
        val repo=repository();graded(repo)
        val courseProgress=progress(repo)
        repo.update { CourseStudy.update(it,courseProgress.lessonId,{courseProgress},now=3_000) }
        val capturedGeneration=repo.restoreGeneration
        // The UI captures this epoch before a restore can dispose the reader. The callback
        // runs later, as a pending onDispose/auto-save would, and checks inside the mutex.
        val staleReaderSave:(StudyState)->StudyState={ current ->
            if(repo.restoreGeneration!=capturedGeneration)current
            else CourseStudy.update(current,courseProgress.lessonId,{it.copy(scroll=999)},now=4_000)
        }
        val replacement=repo.state.value.copy(courseProgress=listOf(courseProgress.copy(scroll=42,
            checks=courseProgress.checks.map{it.copy(draft="복원한 답안",rating="understood")})))
        repo.restore(replacement)
        val restored=repo.state.value
        assertEquals(capturedGeneration+1,repo.restoreGeneration)
        repo.update(staleReaderSave)
        assertEquals(restored,repo.state.value)
        assertEquals(42,repo.state.value.courseProgress.single().scroll)
        assertEquals("복원한 답안",repo.state.value.courseProgress.single().checks.single().draft)
        assertEquals(replacement.submissions,repo.state.value.submissions)
        assertEquals(1,repo.db.dao().submissionCount())
    }

    @Test fun successfulReplacementSavesRecoveryWithCourseAndQuizHistoryThenRestoresVersionOneBackup()=runBlocking {
        val repo=repository();graded(repo)
        val courseProgress=progress(repo)
        val original=repo.update { CourseStudy.update(it,courseProgress.lessonId,{courseProgress},now=3_000) }
        val old=original.copy(schemaVersion=1,courseProgress=emptyList(),lastLessonId=null)
        repo.restore(old)
        assertEquals(BackupCodec.CURRENT_VERSION,repo.state.value.schemaVersion)
        assertTrue(repo.state.value.courseProgress.isEmpty())
        assertEquals(original.submissions,repo.state.value.submissions)
        assertEquals(original,repo.recoveryCandidate())
        repo.restore(repo.recoveryCandidate()!!)
        assertEquals(original.copy(revision=repo.state.value.revision),repo.state.value)
        assertEquals(1,repo.db.dao().submissionCount())
    }
}
