package kr.sqld.study

import java.io.File
import org.junit.Assert.*
import org.junit.Test

class LessonGuideTest {
    private val assets=listOf(File("src/main/assets"),File("app/src/main/assets")).first{it.resolve("course-pack.json").isFile}
    private fun material(id:String)=Codec.decodeFromString<LessonGuide>(assets.resolve("lesson-guides/$id.json").readText())
    @Test fun everyGuideIsBoundToExactSourceAndAllOriginalExamplesAndChecks(){
        val course=Codec.decodeFromString<CoursePack>(assets.resolve("course-pack.json").readText())
        val files=assets.resolve("lesson-guides").listFiles()!!.filter{it.extension=="json"}
        assertEquals(course.lessons.map{it.id}.toSet(),files.map{it.nameWithoutExtension}.toSet())
        files.forEach{file->val guide=Codec.decodeFromString<LessonGuide>(file.readText());LessonGuideRules.validate(guide)
            assertTrue(guide.matches(course.lessons.single{it.id==guide.lessonId}))
        }
    }
    @Test fun editsToSourceOrRemovedExampleAreRejected(){
        val guide=material("2-1-10")
        assertFalse(guide.matches(guide.source.copy(examples=guide.source.examples.map{it.copy(sql=it.sql+" changed")})))
        assertFalse(guide.matches(guide.source.copy(selfChecks=guide.source.selfChecks.map{it.copy(answer="different answer")})))
        assertTrue(runCatching{LessonGuideRules.validate(guide.copy(examples=emptyList()))}.isFailure)
    }
    @Test fun supplementalForeignKeyDoesNotBecomeOriginalOrAStoredRow(){
        val guide=material("2-1-03")
        val fk=guide.supplementalExamples.single{it.example.id.endsWith("-fk")}
        assertTrue(fk.example.results.single().rows.isEmpty())
        assertTrue(guide.source.examples.none{it.id==fk.example.id})
        val walk=guide.walkthrough(fk.example,fk.guide)
        assertTrue(walk.source.sql!!.startsWith("CREATE TABLE EMPLOYEE"))
        assertFalse(walk.verification.oracleEngineExecuted)
    }
    @Test fun newReadingProgressPreservesOriginalCourseRecordsAndBackupRoundTrip(){
        val original=CourseProgress("2-1-10",readVersion=1,section="checks",exampleSteps=mapOf("2-1-10-E01" to 2),
            revealedResults=listOf("2-1-10-E01"),checks=listOf(CourseCheckProgress("2-1-10-Q1","내 기존 답",true,"review")))
        val state=StudyState(courseProgress=listOf(original))
        val key=LessonGuideRules.stepKey("2-1-10-E01")
        val next=CourseStudy.update(state,"2-1-10",{it.copy(exampleSteps=it.exampleSteps+(key to 4))},now=10)
        val p=next.courseProgress.single()
        assertEquals(original.checks,p.checks);assertEquals(original.revealedResults,p.revealedResults)
        assertEquals(original.readVersion,p.readVersion);assertEquals(original.section,p.section)
        assertEquals(2,p.exampleSteps["2-1-10-E01"]);assertEquals(4,p.exampleSteps[key])
        assertEquals(state.submissions,next.submissions);CourseStudy.validateState(next)
        val restored=Codec.decodeFromString<StudyState>(Codec.encodeToString(StudyState.serializer(),next))
        assertEquals(next,restored)
        assertEquals(BackupCodec.upgrade(next),BackupCodec.decode(BackupCodec.encode(next,now=20)))
    }
}
