package kr.sqld.study

import org.junit.Assert.*
import org.junit.Test

class CourseStudyTest {
    private val lesson=CourseLesson(id="1-1-01",partId="1-1",number=1,title="데이터베이스",lectureMinutes=19,
        easy="기본 개념",why="학습 이유",concepts=listOf(CourseConcept("데이터","값","예")),
        examples=listOf(CourseExample("1-1-01-E01","예제","입력을 확인하세요.",
            tables=listOf(DataTable("T",listOf("ID"),listOf(listOf("1")))),steps=listOf("첫 단계"))),
        memory="기억",traps=listOf("혼동"),selfChecks=listOf(CourseCheck("1-1-01-Q1","질문","답","해설")),
        relatedNoteIds=listOf("note"),sourceIds=listOf("source"))
    private val course=CoursePack(version="v1",title="강의",parts=listOf(CoursePart("1-1","모델링")),
        lessons=listOf(lesson),sources=listOf(CourseSource("source","문서","https://example.com")),
        provenance="사용자 자료",reviewNote="문서 검토")
    private val content=ContentPack(notes=listOf(Note("note",objectiveId="M01",title="노트",summary="요약",blocks=emptyList())))

    @Test fun readingCourseDoesNotChangeScoredHistoryOrExistingNoteProgress() {
        val state=EngineTestData.grade(EngineTestData.answer(EngineTestData.start(),choice="wrong-b"))
            .copy(notes=listOf(NoteProgress("note",true,33)),lastNoteId="note")
        val changed=CourseStudy.read(state,lesson,true)
        assertEquals(state,changed.copy(courseProgress=state.courseProgress,lastLessonId=state.lastLessonId))
        assertEquals(lesson.version,CourseStudy.progress(changed,lesson.id).readVersion)
        assertEquals(lesson.id,changed.lastLessonId)
        assertEquals(1,changed.submissions.size)
    }
    @Test fun changingOneLessonPreservesOtherLessonDraftAndExamplePosition() {
        val a=CourseProgress(lesson.id,scroll=33,exampleSteps=mapOf("example" to 2),
            checks=listOf(CourseCheckProgress("check","직접 작성한 설명",true,"review")))
        val b=CourseProgress("1-1-02",readVersion=1)
        val state=StudyState(courseProgress=listOf(a,b),lastLessonId=b.lessonId)
        val changed=CourseStudy.update(state,a.lessonId,{it.copy(readVersion=1)},now=123)
        assertEquals(listOf(a.copy(readVersion=1,updatedAt=123),b),changed.courseProgress)
        assertEquals(a.lessonId,changed.lastLessonId)
    }
    @Test fun repeatedSaveOfSameProgressDoesNotCreateDuplicateOrNewTimestamp() {
        val state=CourseStudy.update(StudyState(),lesson.id,{it.copy(scroll=50)},now=123)
        val again=CourseStudy.update(state,lesson.id,{it.copy(scroll=50)},now=456)
        assertEquals(state,again)
        assertEquals(1,again.courseProgress.size)
    }
    @Test fun readFlagCanBeClearedWithoutErasingSelfAssessmentOrDraft() {
        val previous=CourseProgress(lesson.id,readVersion=lesson.version,checks=listOf(CourseCheckProgress("check","답",true,"review")))
        val changed=CourseStudy.read(StudyState(courseProgress=listOf(previous)),lesson,false)
        assertEquals(0,changed.courseProgress.single().readVersion)
        assertEquals(previous.checks,changed.courseProgress.single().checks)
    }
    @Test fun oldReadVersionDoesNotBecomeCurrentOnLessonRevision() {
        val previous=CourseProgress(lesson.id,readVersion=1)
        val state=StudyState(courseProgress=listOf(previous))
        val updated=lesson.copy(version=2)
        assertNotEquals(updated.version,CourseStudy.progress(state,lesson.id).readVersion)
        assertEquals(2,CourseStudy.read(state,updated,true).courseProgress.single().readVersion)
    }
    @Test fun attemptingToChangeStableLessonIdIsRejected() {
        assertThrows(IllegalArgumentException::class.java){
            CourseStudy.update(StudyState(),lesson.id,{it.copy(lessonId="other")})
        }
    }
    @Test fun packRejectsMissingNoteSourceDuplicateCheckAndMalformedTable() {
        CourseStudy.validatePack(course,content)
        assertThrows(IllegalArgumentException::class.java){CourseStudy.validatePack(course,content.copy(notes=emptyList()))}
        assertThrows(IllegalArgumentException::class.java){CourseStudy.validatePack(course.copy(sources=emptyList()),content)}
        assertThrows(IllegalArgumentException::class.java){CourseStudy.validatePack(course.copy(lessons=listOf(lesson.copy(selfChecks=lesson.selfChecks+lesson.selfChecks))),content)}
        val bad=lesson.examples.single().copy(tables=listOf(DataTable("T",listOf("ID"),listOf(listOf("1","2")))))
        assertThrows(IllegalArgumentException::class.java){CourseStudy.validatePack(course.copy(lessons=listOf(lesson.copy(examples=listOf(bad)))),content)}
    }
}
