package kr.sqld.study

import android.app.Application
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.room.Room
import androidx.lifecycle.viewModelScope
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancelAndJoin
import org.junit.Assert.*
import org.junit.Before
import org.junit.After
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Rendered Compose tests use an isolated in-memory Room database, not the personal app DB. */
@RunWith(AndroidJUnit4::class)
class LearningUiTest {
    @get:Rule val compose=createComposeRule()
    private lateinit var vm:StudyViewModel
    private lateinit var repo:StudyRepository
    private fun question(index:Int,subject:String="model",mock:String?=null)=Question(
        id="ui-$index",subjectId=subject,topicId="A",objectiveIds=listOf("M01"),familyId="ui-family-$index",
        kind=if(mock==null)"recall"else"mock",title="테스트 문제 $index",stem="문제 $index: 업무 규칙을 고르세요.",
        choices=listOf(Choice("a","보기 A-$index","A 판단"),Choice("b","보기 B-$index","B 판단"),Choice("c","보기 C-$index","C 판단"),Choice("d","보기 D-$index","D 판단")),
        correctChoiceIds=listOf("b"),explanation=Explanation("비공개 해설 $index",steps=listOf(ExplanationStep("조건 확인","주어진 업무 규칙을 대조합니다.")),memory="조건부터 확인",relatedNoteId="note-M01"),mockSetId=mock)
    @Before fun setup(){
        val app=ApplicationProvider.getApplicationContext<Application>()
        repo=StudyRepository(app,Room.inMemoryDatabaseBuilder(app,StudyDatabase::class.java).build(),false)
        compose.runOnUiThread{vm=StudyViewModel(app,repo)}
        compose.setContent{SqlNoteApp(vm)}
        compose.waitUntil(20000){vm.ready.value}
        compose.waitForIdle()
    }
    @After fun cleanup()=runBlocking{vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin();repo.db.close()}
    private fun start(mode:String="batch",mock:Boolean=false){
        val qs=if(mock)(0 until 50).map{question(it,if(it<10)"model"else"sql","mock-ui")}else(0..2).map{question(it)}
        runBlocking{repo.update{StudyEngine.createSession(it,repo.pack,qs,mode,"화면 동작 검증",System.currentTimeMillis(),android.os.SystemClock.elapsedRealtime(),0,1,if(mock)"mock-ui"else null)}}
        compose.onNode(hasTestTag("home-compact") or hasTestTag("home-wide"))
            .performScrollToNode(hasText("풀던 문제 이어서") and hasClickAction())
        compose.resumeProblem()
        compose.waitUntil(10000){compose.onAllNodesWithText("보기 A-0").fetchSemanticsNodes().isNotEmpty()}
    }
    private fun state()=repo.state.value
    private fun session()=state().sessions.last()
    @Test fun searchKeepsQueryAndRefreshesWhenExcludedOrMockExposureChanges(){
        val question=repo.pack.practice().first()
        val mock=repo.pack.questions.first { it.kind=="mock" && it.status=="published" }
        fun result(title:String)=hasText(title) and hasClickAction() and !hasSetTextAction()
        compose.onNodeWithContentDescription("노트와 연습문제 검색").performClick()
        compose.onNode(hasSetTextAction()).performTextInput(question.title)
        compose.onNodeWithTag("notes-list").performScrollToNode(result(question.title))
        compose.onNode(result(question.title)).assertExists()
        runBlocking { repo.update { it.copy(issues=it.issues+ContentIssue("search-exclude",question.id,repo.pack.version,"검색 갱신 확인",true,1)) } }
        compose.waitUntil(10000){compose.onAllNodes(result(question.title)).fetchSemanticsNodes().isEmpty()}
        compose.onNodeWithTag("notes-list").performScrollToNode(hasSetTextAction())
        compose.onNode(hasSetTextAction()).assertTextContains(question.title).performTextReplacement(mock.title)
        compose.onNode(result(mock.title)).assertDoesNotExist()
        runBlocking { repo.update { it.copy(exposures=it.exposures+Exposure("search-seen",mock.id,mock.familyId,"prior-mock","seen",1)) } }
        compose.waitForIdle()
        compose.onNodeWithTag("notes-list").performScrollToNode(result(mock.title))
        compose.onNode(result(mock.title)).assertExists()
        runBlocking { repo.update { it.copy(exposures=emptyList()) } }
        compose.waitUntil(10000){compose.onAllNodes(result(mock.title)).fetchSemanticsNodes().isEmpty()}
        compose.onNodeWithTag("notes-list").performScrollToNode(hasSetTextAction())
        compose.onNode(hasSetTextAction()).assertTextContains(mock.title)
    }
    @Test fun prioritiesAreVisibleFilterableAndLinkedToTheirResearch(){
        assertTrue(repo.pack.studyPriorities.isNotEmpty())
        val priority=repo.pack.studyPriorities.first{it.level=="core"&&it.frequencyStatus=="educator_emphasis"}
        val note=repo.pack.notes.first{it.objectiveId==priority.objectiveId}
        compose.openHomeTools()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasTestTag("core-progress"))
        compose.onNodeWithTag("core-progress").assertIsDisplayed()
        compose.onNodeWithContentDescription("진도",useUnmergedTree=true).performClick()
        compose.onNodeWithTag("course-list").performScrollToNode(hasText("개념 찾기") and hasClickAction())
        compose.onNodeWithText("개념 찾기").performScrollTo().performClick()
        compose.onNodeWithText("핵심 개념").performClick()
        compose.onNodeWithTag("notes-list").performScrollToNode(hasText(note.title))
        compose.onNodeWithText(note.title).performClick()
        compose.onNodeWithText("학습 핵심").assertExists()
        compose.onNodeWithText("교재·강사 강조").assertExists()
        compose.onNodeWithText("중요도와 출제 근거").performScrollTo().performClick()
        compose.onNodeWithText(priority.frequencyNote).assertExists()
        compose.onNodeWithText("닫기").performClick()
        compose.onNodeWithText("암기 가리기").performScrollTo().performClick()
        compose.onNodeWithText("중요도와 출제 근거").assertDoesNotExist()
        compose.onNodeWithText(note.blocks.first{it.kind!="recall"}.title).assertDoesNotExist()
        assertEquals(0,state().submissions.size)
    }
    @Test fun expandedNotesKeepReadingHistoryUntilUserConfirmsTheNewVersion(){
        val note=repo.pack.notes.first{it.version>1}
        runBlocking{repo.update{it.copy(notes=listOf(NoteProgress(note.id,read=true,readVersion=note.version-1)),lastNoteId=note.id)}}
        compose.openHomeTools()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("노트 펼치기"))
        compose.onNodeWithText("노트 펼치기").performClick()
        compose.onNodeWithText("이전에 읽은 기록이 있어요. 새로 보강된 내용을 확인하고 읽음 표시를 갱신해 주세요.").performScrollTo().assertIsDisplayed()
        assertTrue(state().notes.single().read)
        compose.onNodeWithText("읽음 표시하고 개념 확인").performScrollTo().performClick()
        compose.waitUntil(10000){state().notes.first{it.noteId==note.id}.readVersion==note.version}
        assertEquals(0,state().submissions.size)
    }
    @Test fun historicalCorrectionDisplaysBothJudgmentsWithoutRewritingSubmission(){
        val current=repo.pack.practice().first()
        val oldAnswer=current.choices.first{it.id !in current.correctChoiceIds}.id
        val old=current.copy(version=0,correctChoiceIds=listOf(oldAnswer))
        runBlocking{repo.update{
            val created=StudyEngine.createSession(it,repo.pack,listOf(old),"batch","정정 이력 검증",System.currentTimeMillis(),android.os.SystemClock.elapsedRealtime(),0,5)
            val sid=created.sessions.last().id
            StudyEngine.grade(StudyEngine.select(created,sid,0,oldAnswer),sid,0,System.currentTimeMillis())
        }}
        compose.resumeProblem()
        compose.waitUntil(10000){compose.onAllNodesWithText("콘텐츠 정정 안내 · 과거 판정 보존").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithText("콘텐츠 정정 안내 · 과거 판정 보존").performScrollTo().assertIsDisplayed()
        compose.onNodeWithText("현재 정답 기준 참고: 오답. 이전 점수·오답 이력은 바꾸지 않았습니다.").performScrollTo().assertIsDisplayed()
        assertEquals("correct",state().submissions.single().outcome)
        assertEquals(listOf(oldAnswer),session().items.single().question.correctChoiceIds)
    }
    @Test fun changedQuestionConditionsPreventComparingReusedChoiceIds(){
        val current=repo.pack.practice().first()
        val old=current.copy(version=0,stem="조건이 달랐던 이전 문제")
        runBlocking{repo.update{
            val created=StudyEngine.createSession(it,repo.pack,listOf(old),"batch","조건 변경 이력 검증",System.currentTimeMillis(),android.os.SystemClock.elapsedRealtime(),0,5)
            val sid=created.sessions.last().id
            StudyEngine.grade(StudyEngine.select(created,sid,0,old.correctChoiceIds.single()),sid,0,System.currentTimeMillis())
        }}
        compose.resumeProblem()
        val warning="문제 조건이나 보기가 변경되어 과거 답안을 자동 재판정할 수 없습니다."
        compose.waitUntil(10000){compose.onAllNodesWithText(warning).fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithText(warning).performScrollTo().assertIsDisplayed()
        assertEquals("correct",state().submissions.single().outcome)
        assertEquals("조건이 달랐던 이전 문제",session().items.single().question.stem)
    }
    @Test fun choosingIsNotGradingAndIndividualThenWholeSubmissionIsIdempotent(){
        start()
        compose.onNodeWithText("비공개 해설 0").assertDoesNotExist()
        compose.onNodeWithText("보기 A-0").performScrollTo().performClick()
        compose.waitUntil{session().items[0].draft==listOf("a")}
        assertTrue(state().submissions.isEmpty())
        compose.onNodeWithText("보기 B-0").performClick()
        compose.waitUntil{session().items[0].draft==listOf("b")}
        compose.onNodeWithText("다음").performClick()
        compose.waitUntil(10000){session().current==1 && compose.onAllNodesWithText("보기 C-1").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithText("보기 C-1").performScrollTo().performClick()
        compose.waitUntil{session().items[1].draft==listOf("c")}
        compose.onNodeWithText("이전").performClick()
        compose.waitUntil(10000){session().current==0 && compose.onAllNodesWithText("보기 B-0").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithText("현재 문제만 채점").performClick()
        compose.waitUntil{state().submissions.size==1}
        assertEquals(listOf("c"),session().items[1].draft)
        assertNull(session().items[1].submissionId)
        compose.onNodeWithText("전체 제출").performClick()
        compose.onNodeWithText("전체 제출 확정").performClick()
        compose.waitUntil{session().submittedAt!=null}
        assertEquals(3,state().submissions.size)
        assertEquals(1,state().submissions.count{it.questionId=="ui-0"})
        assertEquals("unanswered",state().submissions.first{it.questionId=="ui-2"}.outcome)
    }
    @Test fun strictHidesIndividualGradingAndNoteHelpNeedsConfirmedPracticeConversion(){
        start("strict",true)
        compose.onNodeWithText("보기 B-0").performScrollTo().performClick()
        compose.waitUntil{session().items[0].draft.isNotEmpty()}
        compose.onNodeWithText("현재 문제만 채점").assertDoesNotExist()
        compose.onNodeWithText("모르겠어요").assertDoesNotExist()
        compose.onNodeWithText("문제 정보·도움").performScrollTo().performClick()
        compose.onNodeWithText("연결 개념 확인").performScrollTo().performClick()
        compose.onNodeWithText("연습 모드로 전환할까요?").assertIsDisplayed()
        assertTrue(state().submissions.isEmpty())
        compose.onNodeWithText("실전 유지").performClick()
        assertEquals("strict",session().mode)
        compose.onNodeWithText("연결 개념 확인").performScrollTo().performClick()
        compose.onNodeWithText("연습으로 전환").performClick()
        compose.waitUntil{session().mode=="mixed"}
        assertEquals("mixed",session().mode);assertFalse(session().diagnosticEligible)
        assertEquals(listOf("b"),session().items[0].draft)
        assertTrue(state().submissions.isEmpty())
        assertEquals(1,state().exposures.count{it.sessionId==session().id&&it.kind=="note"})
    }
    @Test fun starredQuestionStaysInFrozenSessionAfterRemovingStar(){
        start()
        compose.onNodeWithContentDescription("별표 저장").performClick()
        compose.waitUntil{state().bookmarks.any{it.id=="ui-0"}}
        compose.onNodeWithContentDescription("별표 해제").performClick()
        compose.waitUntil{state().bookmarks.none{it.id=="ui-0"}}
        assertEquals(3,session().items.size)
        compose.onNodeWithText("문제 0: 업무 규칙을 고르세요.").assertExists()
    }
    @Test fun unknownIsExplicitUnansweredAndDoesNotAutomaticallyAdvance(){
        start("immediate")
        compose.onNodeWithText("이 문제 채점").assertIsNotEnabled()
        compose.onNodeWithText("모르겠어요").performClick()
        compose.waitUntil{state().submissions.size==1}
        assertEquals("unanswered",state().submissions.single().outcome)
        assertEquals(0,session().current)
        compose.onNodeWithText("채점 완료",substring=true).assertExists()
    }
}
