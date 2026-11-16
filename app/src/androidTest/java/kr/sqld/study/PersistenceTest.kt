package kr.sqld.study

import android.content.Context
import android.content.ContextWrapper
import androidx.room.Room
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.encodeToString
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import java.util.UUID
import java.io.File

/** Uses isolated on-device Room files. Never clears the user's default sqlnote.db. */
@RunWith(AndroidJUnit4::class)
class PersistenceTest {
    private lateinit var context:Context
    private val databases=mutableListOf<StudyDatabase>()
    private val names=mutableListOf<String>()
    private fun open(name:String):StudyDatabase =
        Room.databaseBuilder(context,StudyDatabase::class.java,name).build().also{databases+=it}
    private fun newName():String="sqld-test-"+UUID.randomUUID()+".db"
    private fun question(id:String)=Question(id=id,subjectId="sql",topicId="C",objectiveIds=listOf("S02"),
        familyId="fixture-$id",kind="application",title="저장 검증",stem="테스트 입력",
        choices=listOf(Choice("right","정답","근거"),Choice("x","오답X","근거"),
            Choice("y","오답Y","근거"),Choice("z","오답Z","근거")),
        correctChoiceIds=listOf("right"),
        explanation=Explanation("근거",steps=listOf(ExplanationStep("1","내용")),memory="기억",relatedNoteId="note-S02"))
    private fun session(state:StudyState)=state.sessions.first{it.id==state.activeSessionId}
    private suspend fun repository():StudyRepository {
        val name=newName();names+=name
        return StudyRepository(context,open(name),projectPreferences=false).also{it.initialize()}
    }
    private suspend fun start(repo:StudyRepository,count:Int=1):StudyState=repo.update { state ->
        val questions=(1..count).map{question("q$it")}
        StudyEngine.createSession(state,repo.pack,questions,"batch","검증",1_000,100,1,42)
    }
    private suspend fun select(repo:StudyRepository,index:Int=0,choice:String="right")=repo.update{
        StudyEngine.select(it,session(it).id,index,choice)
    }
    private suspend fun grade(repo:StudyRepository,index:Int=0)=repo.update{
        StudyEngine.grade(it,session(it).id,index,2_000)
    }
    @Before fun before(){
        val target=InstrumentationRegistry.getInstrumentation().targetContext
        // The production DataStore projection must also stay out of the user's files.
        // This stable test-only directory is retained while DataStore's singleton is alive.
        context=object:ContextWrapper(target){
            override fun getApplicationContext():Context=this
            override fun getFilesDir():File=File(target.filesDir,"isolated-persistence-test-files").apply{mkdirs()}
        }
    }
    @After fun after(){
        databases.forEach{if(it.isOpen)it.close()}
        names.forEach{context.deleteDatabase(it)}
    }

    @Test fun reopenPreservesDraftBookmarkAnnotationSettingsAndReadingPosition()=runBlocking {
        val name=newName();names+=name
        val first=StudyRepository(context,open(name),projectPreferences=false);first.initialize()
        start(first);select(first,choice="x")
        val note=first.pack.notes.first();val block=note.blocks.first()
        val state=first.update { current ->
            StudyEngine.scroll(StudyEngine.bookmark(current,"q1",1_500),session(current).id,0,144).copy(
                annotations=listOf(Annotation("test-note",note.id,block.id,block.text.take(20),"보존 메모","underline",1_600)),
                notes=listOf(NoteProgress(note.id,true,256,listOf(block.id))),
                noteBookmarks=listOf(Bookmark(note.id,1_700)),lastNoteId=note.id,
                settings=current.settings.copy(theme="dark",textScale=1.25f,targetDate="2026-11-14"))
        }
        first.db.close()
        val second=StudyRepository(context,open(name),projectPreferences=false);second.initialize()
        val restored=second.state.value
        val expectedNotes=state.notes.map{it.copy(readVersion=first.pack.legacyNoteVersions.getValue(it.noteId))}
        assertEquals(state.copy(revision=restored.revision,notes=expectedNotes),restored)
        assertEquals(listOf("x"),session(restored).items.single().draft)
        assertEquals(144,session(restored).items.single().scroll)
        assertTrue(restored.submissions.isEmpty())
        assertEquals("보존 메모",restored.annotations.single().memo)
    }

    @Test fun rapidConcurrentGradeRequestsCommitOneSubmissionAndOneReview()=runBlocking {
        val repo=repository();start(repo);select(repo,choice="x")
        val before=repo.state.value.revision
        val id=session(repo.state.value).id
        coroutineScope {
            (1..20).map { async { repo.update{StudyEngine.grade(it,id,0,2_000)} } }.awaitAll()
        }
        assertEquals(1,repo.db.dao().submissionCount())
        assertEquals(1,repo.state.value.submissions.size)
        assertEquals(1,repo.state.value.reviews.single().wrongCount)
        assertEquals(before+1,repo.state.value.revision)
    }

    @Test fun individualThenWholeSubmissionSurvivesReopenWithoutDuplicateRows()=runBlocking {
        val name=newName();names+=name
        val repo=StudyRepository(context,open(name),projectPreferences=false);repo.initialize();start(repo,2)
        select(repo,0,"x");select(repo,1,"right");grade(repo,0)
        val first=repo.state.value.submissions.single()
        repo.update{StudyEngine.submit(it,session(it).id,3_000)}
        assertEquals(2,repo.db.dao().submissionCount())
        repo.db.close()
        val reopened=StudyRepository(context,open(name),projectPreferences=false);reopened.initialize()
        val before=reopened.state.value
        reopened.update{StudyEngine.submit(it,session(it).id,4_000)}
        assertEquals(before,reopened.state.value)
        assertEquals(first,reopened.state.value.submissions.first{it.id==first.id})
        assertEquals(2,reopened.db.dao().submissionCount())
        assertEquals(1,reopened.state.value.reviews.first{it.questionId=="q1"}.wrongCount)
    }

    @Test fun roomUniqueSessionQuestionConstraintRejectsDifferentSubmissionId()=runBlocking {
        val repo=repository();start(repo);select(repo);grade(repo)
        val row=repo.state.value.submissions.single()
        val failure=runCatching {
            repo.db.dao().submission(SubmissionRow("different-id",row.sessionId,row.questionId,"{}"))
        }.exceptionOrNull()
        assertNotNull("A second record for the same session/question must violate the unique index",failure)
        assertEquals(1,repo.db.dao().submissionCount())
    }

    @Test fun failureBeforeSavePreservesDatabaseAndPublishedInMemoryState()=runBlocking {
        val repo=repository();start(repo);select(repo,choice="x")
        val state=repo.state.value;val row=repo.db.dao().state()
        repo.failNextWrite=true
        val error=runCatching{grade(repo)}.exceptionOrNull()
        assertNotNull(error);assertEquals(state,repo.state.value)
        assertEquals(row,repo.db.dao().state());assertEquals(0,repo.db.dao().submissionCount())
        grade(repo)
        assertEquals(1,repo.db.dao().submissionCount())
        assertEquals(1,repo.state.value.reviews.single().wrongCount)
    }

    @Test fun lateConstraintFailureRollsBackEarlierInsertedSubmissionInSameTransaction()=runBlocking {
        val repo=repository();start(repo,2);select(repo,0);select(repo,1)
        val before=repo.state.value;val row=repo.db.dao().state()
        val id=session(before).id
        val transformed=StudyEngine.submit(before,id,2_000)
        val first=transformed.submissions.first()
        // Deliberately corrupt the second pair to force a DB constraint failure after first insert.
        val duplicate=transformed.submissions[1].copy(sessionId=first.sessionId,questionId=first.questionId)
        val error=runCatching{repo.update{transformed.copy(submissions=listOf(first,duplicate))}}.exceptionOrNull()
        assertNotNull(error)
        assertEquals(before,repo.state.value);assertEquals(row,repo.db.dao().state())
        assertEquals(0,repo.db.dao().submissionCount())
    }

    @Test fun exportRestoreIntoSeparateDatabaseAndRepeatedRestoreAreIdempotentForHistory()=runBlocking {
        val source=repository();start(source);select(source,choice="x");grade(source)
        source.update{StudyEngine.bookmark(it,"q1",2_500)}
        val exported=source.export();val candidate=BackupCodec.decode(exported)
        val destination=repository()
        destination.restore(candidate)
        val first=destination.state.value
        assertEquals(candidate.copy(contentVersion=destination.pack.version,revision=first.revision),first)
        assertEquals(1,destination.db.dao().submissionCount())
        destination.restore(candidate)
        val second=destination.state.value
        assertEquals(first.copy(revision=second.revision),second)
        assertEquals(1,second.submissions.size)
        assertEquals(1,second.reviews.single().wrongCount)
        assertEquals(1,destination.db.dao().submissionCount())
        val recovery=destination.recoveryCandidate()
        assertNotNull(recovery);assertEquals(first,recovery)
    }

    @Test fun restoreFailureAfterClearingLogRollsBackDataAndRecoveryPoint()=runBlocking {
        val repo=repository();start(repo);select(repo,choice="x");grade(repo)
        val original=repo.state.value;val row=repo.db.dao().state()
        val recoveryBefore=repo.recoveryCandidate()
        repo.failNextWrite=true
        val candidate=StudyState(settings=AppSettings(theme="dark"))
        val error=runCatching{repo.restore(candidate)}.exceptionOrNull()
        assertNotNull(error)
        assertEquals(original,repo.state.value);assertEquals(row,repo.db.dao().state())
        assertEquals(1,repo.db.dao().submissionCount())
        assertEquals(recoveryBefore,repo.recoveryCandidate())
    }

    @Test fun invalidRestoreDoesNotChangeAnyExistingData()=runBlocking {
        val repo=repository();start(repo);select(repo);grade(repo)
        val before=repo.state.value;val row=repo.db.dao().state()
        val invalid=before.copy(schemaVersion=99)
        assertNotNull(runCatching{repo.restore(invalid)}.exceptionOrNull())
        assertEquals(before,repo.state.value);assertEquals(row,repo.db.dao().state())
        assertEquals(1,repo.db.dao().submissionCount())
    }

    @Test fun strictTimerSnapshotRestoresAcrossDatabaseReopenAndExpiresOnlyOnce()=runBlocking {
        val name=newName();names+=name
        val first=StudyRepository(context,open(name),projectPreferences=false);first.initialize()
        val exam=ExamSpec(modelCount=1,sqlCount=1,pointsPerQuestion=50,minutes=1)
        val qs=listOf(question("model").copy(subjectId="model",kind="mock",mockSetId="test-mock"),
            question("sql").copy(kind="mock",mockSetId="test-mock"))
        first.update{StudyEngine.createSession(it,first.pack.copy(examSpec=exam),qs,"strict","시험",10_000,1_000,1,42,"test-mock")}
        val original=session(first.state.value)
        first.db.close()
        val reopened=StudyRepository(context,open(name),projectPreferences=false);reopened.initialize()
        assertEquals(original,session(reopened.state.value))
        reopened.update{StudyEngine.tick(it,original.id,80_000,71_000,1)}
        reopened.update{StudyEngine.tick(it,original.id,90_000,81_000,1)}
        assertEquals(2,reopened.db.dao().submissionCount())
        assertEquals(2,reopened.state.value.submissions.size)
        assertTrue(reopened.state.value.submissions.all{it.outcome=="unanswered"})
        assertEquals(0L,session(reopened.state.value).remainingMillis)
    }
}
