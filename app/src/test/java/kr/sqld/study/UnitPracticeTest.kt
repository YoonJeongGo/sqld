package kr.sqld.study

import org.junit.Assert.*
import org.junit.Test

class UnitPracticeTest {
    private fun bank(partId:String="2-1"):UnitQuestionBank {
        val form=UnitMockForm("unit:$partId:1",1,(1..50).map{"unit-$partId-test-$it"})
        val qs=form.questionIds.map{EngineTestData.question(it,if(partId.startsWith("1-"))"model"else"sql",form.id)}
        return UnitQuestionBank(parts=listOf(UnitPracticePart(partId,"테스트",emptyList(),listOf(form))),questions=qs)
    }
    private fun start(part:String="2-1")=UnitPractice.create(StudyState(),ContentPack(),bank(part),part,1,1000,1000,1,13)
    @Test fun allFivePartsHaveFiftyStrictQuestionsAndSeparateExamSnapshots(){
        listOf("1-1","1-2","2-1","2-2","2-3").forEach{part->
            val state=start(part);val s=state.sessions.single()
            assertEquals(50,s.items.size);assertEquals("strict",s.mode)
            assertEquals(90*60_000L,s.remainingMillis);assertTrue(s.isUnitMock())
            assertFalse(s.diagnosticEligible)
            assertEquals(UnitPractice.spec(part,s.items.map{it.question}),s.examSpec);BackupCodec.validate(state)
            assertEquals(state,BackupCodec.decode(BackupCodec.encode(state,1000)))
        }
        assertEquals(ExamSpec(),ContentPack().examSpec)
    }
    @Test fun gradingFiftySqlItemsDoesNotUseTheFullExamFortyItemLimit(){
        var state=start();val s=state.sessions.single()
        s.items.indices.forEach{index->state=StudyEngine.select(state,s.id,index,s.items[index].question.correctChoiceIds.single())}
        state=StudyEngine.submit(state,s.id,2000)
        val score=StudyEngine.score(state.sessions.single(),state)
        assertEquals(100,score.points);assertEquals(50,score.sqlCorrect)
        assertEquals(50,state.submissions.size);assertEquals(state,StudyEngine.submit(state,s.id,3000))
        BackupCodec.validate(state)
    }
    @Test fun timeoutPreservesDraftAndCreatesOnlyOneSubmissionPerQuestion(){
        var state=start("1-1");val s=state.sessions.single()
        val answer=s.items[0].question.correctChoiceIds.single()
        state=StudyEngine.select(state,s.id,0,answer)
        state=StudyEngine.tick(state,s.id,1000+s.remainingMillis,1000+s.remainingMillis,1)
        assertNotNull(state.sessions.single().submittedAt)
        assertEquals(1,state.submissions.count{it.outcome=="correct"})
        assertEquals(49,state.submissions.count{it.outcome=="unanswered"})
        assertEquals(listOf(answer),state.sessions.single().items[0].draft)
    }
    @Test fun excludedItemBlocksStartingAnIncompleteForm(){
        val bank=bank();val question=bank.questions.first()
        val state=StudyState(issues=listOf(ContentIssue("issue",question.id,"v1","오류",true,1)))
        assertThrows(IllegalArgumentException::class.java){UnitPractice.create(state,ContentPack(),bank,"2-1",1,1000,1000,1,1)}
    }
    @Test fun invalidZeroSubjectSpecsRemainRejectedOutsideUnitSessions(){
        val state=start();val session=state.sessions.single()
        assertThrows(IllegalArgumentException::class.java){BackupCodec.validate(state.copy(sessions=listOf(session.copy(mockSetId="mock-1"))))}
        assertThrows(IllegalArgumentException::class.java){BackupCodec.validate(state.copy(sessions=listOf(session.copy(examSpec=session.examSpec.copy(minutes=1)))))}
    }
    @Test fun mixedSubjectUnitPreservesItsOwnDistribution(){
        val bank=bank("1-2").let{it.copy(questions=it.questions.mapIndexed{at,q->q.copy(subjectId=if(at%2==0)"model"else"sql")})}
        val state=UnitPractice.create(StudyState(),ContentPack(),bank,"1-2",1,1000,1000,1,3)
        assertEquals(25,state.sessions.single().examSpec.modelCount)
        assertEquals(25,state.sessions.single().examSpec.sqlCount)
        BackupCodec.validate(state)
    }
    @Test fun repeatedStartReturnsExistingStrictSessionWithoutNewItemsOrExposure(){
        val state=start()
        assertEquals(state,UnitPractice.create(state,ContentPack(),bank(),"2-1",1,2000,2000,1,14))
        val fullQuestions=(1..50).map{EngineTestData.question("full-$it",if(it<=10)"model"else"sql","mock-1")}
        val fullState=StudyEngine.createSession(StudyState(),ContentPack(),fullQuestions,"strict","기존 전체 모의",1000,1000,1,13,"mock-1")
        assertEquals(fullState,UnitPractice.create(fullState,ContentPack(),bank(),"2-1",1,2000,2000,1,14))
    }
    @Test fun packagedBankHasAllFifteenFormsAndEachCanBeSubmittedWithoutChangingBaseExam(){
        val assets=java.io.File("src/main/assets")
        val base=Codec.decodeFromString<ContentPack>(java.io.File(assets,"content-pack.json").readText())
        val course=Codec.decodeFromString<CoursePack>(java.io.File(assets,"course-pack.json").readText())
        val bank=Codec.decodeFromString<UnitQuestionBank>(java.io.File(assets,"unit-question-bank.json").readText())
        bank.validate(base,course)
        assertEquals(939,bank.questions.size);assertEquals(189,bank.parts.sumOf{it.reviewIds.size})
        bank.parts.forEach{part->part.forms.forEach{form->
            var state=UnitPractice.create(StudyState(),base,bank,part.id,form.number,1000,1000,1,15)
            val session=state.sessions.single()
            session.items.forEachIndexed{index,item->state=StudyEngine.select(state,session.id,index,item.question.correctChoiceIds.single())}
            state=StudyEngine.submit(state,session.id,2000)
            assertEquals(100,StudyEngine.score(state.sessions.single(),state).points)
            assertEquals(50,state.submissions.size);BackupCodec.validate(state)
        }}
        assertEquals(ExamSpec(),base.examSpec)
        assertEquals(661,base.questions.size)
    }
}
