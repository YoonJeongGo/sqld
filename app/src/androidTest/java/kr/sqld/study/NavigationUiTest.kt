package kr.sqld.study

import android.app.Application
import android.os.SystemClock
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.lifecycle.viewModelScope
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Independent navigation fixtures; never opens or replaces the personal study database. */
@RunWith(AndroidJUnit4::class)
class NavigationUiTest {
    @get:Rule val compose=createComposeRule()
    private lateinit var vm:StudyViewModel
    private lateinit var repo:StudyRepository
    private fun question(id:String,subject:String="model",mock:String?=null)=Question(
        id=id,subjectId=subject,topicId="A",objectiveIds=listOf("M01"),familyId="nav-family-$id",
        kind=if(mock==null)"recall"else"mock",title="이동 검증 $id",stem="이동 검증 문제 $id",
        choices=listOf(Choice("a","첫 보기 $id","첫 보기 근거"),Choice("b","맞는 보기 $id","정답 근거"),Choice("c","셋째 보기 $id","셋째 보기 근거"),Choice("d","넷째 보기 $id","넷째 보기 근거")),
        correctChoiceIds=listOf("b"),explanation=Explanation("이동 검증 해설",steps=listOf(ExplanationStep("조건","조건 확인")),memory="조건 확인",relatedNoteId="note-M01"),mockSetId=mock)
    private fun state()=repo.state.value
    private fun create(title:String,questions:List<Question>,mode:String="batch",mock:String?=null):String {
        val created=runBlocking{repo.update{StudyEngine.createSession(it,repo.pack,questions,mode,title,System.currentTimeMillis(),SystemClock.elapsedRealtime(),0,42,mock)}}
        return created.activeSessionId!!
    }
    @Before fun setup(){
        val app=ApplicationProvider.getApplicationContext<Application>()
        repo=StudyRepository(app,Room.inMemoryDatabaseBuilder(app,StudyDatabase::class.java).build(),false)
        compose.runOnUiThread{vm=StudyViewModel(app,repo)}
        compose.setContent{SqlNoteApp(vm)}
        compose.waitUntil(20000){vm.ready.value}
        compose.waitForIdle()
    }
    @After fun cleanup()=runBlocking{vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin();repo.db.close()}

    @Test fun reopeningAnOlderUnfinishedSessionRecordsHelpOnTheViewedAttempt(){
        val older=create("먼저 시작한 연습",listOf(question("older")))
        val newer=create("나중에 시작한 연습",listOf(question("newer")))
        assertEquals(newer,state().activeSessionId)
        compose.openHomeTools()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("학습 기록 살펴보기"))
        compose.onNodeWithText("학습 기록 살펴보기").performClick()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("먼저 시작한 연습"))
        compose.onNodeWithText("먼저 시작한 연습").performClick()
        compose.waitUntil(10000){compose.onAllNodesWithText("이동 검증 문제 older").fetchSemanticsNodes().isNotEmpty()}
        assertEquals(older,state().activeSessionId)
        compose.onNodeWithText("맞는 보기 older").performScrollTo().performClick()
        compose.waitUntil{state().sessions.first{it.id==older}.items.single().draft==listOf("b")}
        compose.onNodeWithText("연결 개념 확인").assertDoesNotExist()
        compose.onNodeWithText("문제 정보·도움").performScrollTo().performClick()
        compose.onNodeWithText("연결 개념 확인").performScrollTo().performClick()
        compose.waitUntil(10000){compose.onAllNodesWithText("전체 설명").fetchSemanticsNodes().isNotEmpty()}
        val helps=state().exposures.filter{it.kind=="note"}
        assertEquals(1,helps.size)
        assertEquals(older,helps.single().sessionId)
        assertEquals("older",helps.single().questionId)
        assertTrue(state().submissions.isEmpty())
        compose.onNodeWithContentDescription("뒤로").performClick()
        compose.onNodeWithText("현재 문제만 채점").performClick()
        compose.waitUntil{state().submissions.size==1}
        assertEquals(older,state().submissions.single().sessionId)
        assertTrue(state().submissions.single().helped)
        assertNull(state().sessions.first{it.id==newer}.items.single().submissionId)
    }

    @Test fun strictNoteHelpConvertsOnceThenOpensTheNoteWithDraftPreserved(){
        val questions=(0 until 50).map{question("strict-$it",if(it<10)"model"else"sql","nav-mock")}
        val id=create("실전 전환 이동 검증",questions,"strict","nav-mock")
        compose.resumeProblem()
        compose.onNodeWithText("맞는 보기 strict-0").performScrollTo().performClick()
        compose.waitUntil{state().sessions.first{it.id==id}.items.first().draft==listOf("b")}
        compose.onNodeWithText("연결 개념 확인").assertDoesNotExist()
        compose.onNodeWithText("문제 정보·도움").performScrollTo().performClick()
        compose.onNodeWithText("연결 개념 확인").performScrollTo().performClick()
        compose.onNodeWithText("연습 모드로 전환할까요?").assertIsDisplayed()
        compose.onNodeWithText("연습으로 전환").performClick()
        compose.waitUntil(10000){compose.onAllNodesWithText("전체 설명").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithText("연습 모드로 전환할까요?").assertDoesNotExist()
        compose.onNodeWithText("전환하고 보기").assertDoesNotExist()
        val session=state().sessions.first{it.id==id}
        assertEquals("mixed",session.mode)
        assertNotNull(session.convertedAt)
        assertFalse(session.diagnosticEligible)
        assertEquals(listOf("b"),session.items.first().draft)
        assertEquals(1,state().exposures.count{it.sessionId==id&&it.questionId=="strict-0"&&it.kind=="note"})
        assertTrue(state().submissions.isEmpty())
    }
}
