package kr.sqld.study

import org.junit.Assert.*
import org.junit.Test
import java.time.LocalDate

class StudyPlanTest {
    private val lesson=CourseLesson("lesson","1-1",1,"강의",20,"설명","이유",emptyList(),emptyList(),"기억",emptyList(),emptyList(),listOf("note"),emptyList())
    private val course=CoursePack(version="test",title="강의",parts=listOf(CoursePart("1-1","단원")),lessons=listOf(lesson),sources=emptyList(),provenance="test",reviewNote="test")
    private val day=PlanDay("2026-10-05",1,"첫 공부",lectures=listOf(PlanLecture(1,"첫 영상",20,"이론")),
        pdfs=listOf(PlanPdf("1-1","교재",1,4)),lessonIds=listOf("lesson"),
        blocks=listOf(PlanBlock("학습",300,"설명")),extension=listOf(PlanBlock("추가",60,"설명")))
    private val rest=PlanDay("2026-10-06",title="휴식",restReason="개인 일정")
    private val plan=StudyPlan(title="계획",startDate=day.date,endDate=rest.date,days=listOf(day,rest))

    @Test fun calendarKeepsRestDaysAndClampsDatesWithoutCompletingAnything() {
        plan.validate(course)
        assertEquals(day.date,plan.initialDate(LocalDate.parse("2026-01-01")))
        assertEquals(rest.date,plan.initialDate(LocalDate.parse(rest.date)))
        assertEquals(rest.date,plan.initialDate(LocalDate.parse("2027-01-01")))
        assertEquals(300,plan.baseMinutes)
        assertEquals(60,plan.extraMinutes)
        assertEquals(20,plan.videoMinutes)
        assertEquals(1,plan.studyDays.size)
        assertNull(plan.nextStudyDay(rest.date))
    }

    @Test fun validationRejectsCalendarHolesUnknownLinksAndRestAssignments() {
        assertThrows(IllegalArgumentException::class.java){plan.copy(days=listOf(day)).validate(course)}
        assertThrows(IllegalArgumentException::class.java){plan.copy(days=listOf(day.copy(lessonIds=listOf("missing")),rest)).validate(course)}
        assertThrows(IllegalArgumentException::class.java){plan.copy(days=listOf(day,rest.copy(lectures=day.lectures))).validate(course)}
        assertThrows(IllegalArgumentException::class.java){plan.copy(days=listOf(day.copy(blocks=listOf(PlanBlock("시간",299,"설명"))),rest)).validate(course)}
    }

    @Test fun reviewKeepsOnlyLinkedEligibleNonMockQuestionsAndDoesNotMutateHistory() {
        val normal=EngineTestData.question("normal")
        val excluded=normal.copy(id="excluded")
        val mock=EngineTestData.question("exposed-mock",mock="mock-1")
        val other=normal.copy(id="other",objectiveIds=listOf("S99"))
        val pack=ContentPack(notes=listOf(Note("note",objectiveId="S02",title="노트",summary="",blocks=emptyList())),
            questions=listOf(normal,excluded,mock,other,normal.copy(id="draft",status="draft"),normal.copy(id="quarantined",verification="quarantined")))
        val state=EngineTestData.grade(EngineTestData.answer(EngineTestData.start()))
            .copy(issues=listOf(ContentIssue("issue",excluded.id,"test","제외",true,1)),
                exposures=listOf(Exposure("exposure",mock.id,mock.familyId,"old","seen",1)),
                courseProgress=listOf(CourseProgress(lesson.id,readVersion=1)),
                annotations=listOf(Annotation("memo","note","block","문장","내 메모","memo",1)))
        val before=BackupCodec.encode(state,1)
        assertTrue(StudyEngine.available(pack,state).any{it.id==mock.id})
        assertEquals(listOf("normal"),PlanReview.questions(day,course,pack,state).map{it.id})
        assertTrue(PlanReview.questions(rest,course,pack,state).isEmpty())
        assertEquals(before,BackupCodec.encode(state,1))
    }

    @Test fun repeatedLectureNumbersAndWrongStudySequenceAreRejected() {
        val next=day.copy(date=rest.date,studyDay=2)
        assertThrows(IllegalArgumentException::class.java){plan.copy(days=listOf(day,next)).validate(course)}
        assertThrows(IllegalArgumentException::class.java){plan.copy(days=listOf(day.copy(studyDay=2),rest)).validate(course)}
    }

    @Test fun planRotatesThroughTheEntireRangeBeforeRepeatingTheFirstQuestions(){
        val questions=(1..24).map{EngineTestData.question("rotation-$it").copy(familyId="rotation-family-$it")}
        val pack=ContentPack(notes=listOf(Note("note",objectiveId="S02",title="노트",summary="",blocks=emptyList())),questions=questions)
        var state=StudyState()
        val selected=mutableListOf<String>()
        repeat(3){round->
            val before=BackupCodec.encode(state,1)
            val batch=PlanReview.questions(day,course,pack,state).take(10)
            assertEquals(before,BackupCodec.encode(state,1))
            assertEquals(10,batch.map{it.id}.distinct().size)
            selected+=batch.map{it.id}
            // Starting, even without submitting, exposes a session. Resume stays intact.
            state=StudyEngine.createSession(state,pack,batch,"immediate","계획",100L+round,0,0,round)
        }
        assertEquals(questions.map{it.id},selected.take(24))
        assertEquals(questions.take(6).map{it.id},selected.drop(24))
        assertEquals(3,state.sessions.size)
        assertTrue(state.submissions.isEmpty())
        assertEquals(questions.take(10),state.sessions.first().items.map{it.question})
    }

    @Test fun planExposureOrderIgnoresHintsAndKeepsPackOrderForTies(){
        val questions=(1..6).map{EngineTestData.question("order-$it").copy(familyId="order-family-$it")}
        val pack=ContentPack(notes=listOf(Note("note",objectiveId="S02",title="노트",summary="",blocks=emptyList())),questions=questions)
        fun exposure(n:Int,at:Long,kind:String="seen")=Exposure("$n-$at-$kind",questions[n-1].id,questions[n-1].familyId,"session-$at",kind,at)
        val state=StudyState(exposures=listOf(exposure(1,10),exposure(1,20),exposure(2,20),exposure(3,10),exposure(4,10),exposure(5,99,"hint"),exposure(5,100,"explanation")))
        assertEquals(listOf(5,6,3,4,2,1).map{"order-$it"},PlanReview.questions(day,course,pack,state).map{it.id})
    }
}
