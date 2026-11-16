package kr.sqld.study

import android.app.Application
import android.graphics.Bitmap
import androidx.activity.ComponentActivity
import androidx.compose.runtime.*
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.junit4.StateRestorationTester
import androidx.lifecycle.viewModelScope
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

@RunWith(AndroidJUnit4::class)
class UnitPracticeUiTest {
    @get:Rule val compose=createAndroidComposeRule<ComponentActivity>()
    private lateinit var app:Application
    private lateinit var repo:StudyRepository
    private lateinit var vm:StudyViewModel
    private lateinit var restoration:StateRestorationTester
    private val page=mutableStateOf<(@Composable (StudyUi)->Unit)?>(null)
    @Before fun setup(){
        app=ApplicationProvider.getApplicationContext()
        repo=StudyRepository(app,Room.inMemoryDatabaseBuilder(app,StudyDatabase::class.java).build(),false)
        compose.runOnUiThread{vm=StudyViewModel(app,repo)}
        restoration=StateRestorationTester(compose)
        restoration.setContent{
            val custom=page.value
            if(custom==null)SqlNoteApp(vm)else{
                val state by repo.state.collectAsState()
                SqlNoteTheme(false,1f){custom(StudyUi(vm,state,repo.pack,{}, {},{_,_->},{},{_,_,_,_->}))}
            }
        }
        compose.waitUntil(30_000){vm.ready.value}
    }
    @After fun cleanup()=runBlocking{vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin();repo.db.close()}
    private fun capture(name:String){
        compose.waitForIdle()
        val bitmap=InstrumentationRegistry.getInstrumentation().uiAutomation.takeScreenshot()
        File(app.cacheDir,"unit-$name.png").outputStream().use{bitmap.compress(Bitmap.CompressFormat.PNG,100,it)}
        bitmap.recycle()
    }
    private fun createSession():String{
        val now=System.currentTimeMillis();val elapsed=android.os.SystemClock.elapsedRealtime()
        val boot=android.provider.Settings.Global.getInt(app.contentResolver,android.provider.Settings.Global.BOOT_COUNT,0)
        runBlocking{repo.update{UnitPractice.create(it,repo.pack,repo.unitBank,"2-1",1,now,elapsed,boot,7)}}
        return repo.state.value.activeSessionId!!
    }
    @Test fun mockMenuOpensFivePartsAndStartsAReservedFiftyQuestionForm(){
        compose.onNodeWithTag("nav-mock").performClick()
        compose.onNodeWithTag("unit-mock-parts").performScrollToNode(hasTestTag("mock-unit-2-1"))
        compose.onNodeWithTag("mock-unit-2-1").performScrollTo().performClick()
        capture("part")
        compose.onNodeWithTag("unit-mock-forms").performScrollToNode(hasTestTag("unit-mock-1"))
        compose.onNodeWithTag("unit-mock-1").performScrollTo().performClick()
        compose.onNodeWithTag("unit-mock-confirm").performClick()
        compose.waitUntil(15_000){repo.state.value.sessions.isNotEmpty()}
        val session=repo.state.value.sessions.last()
        assertEquals(50,session.items.size);assertEquals("unit:2-1:1",session.mockSetId)
        assertTrue(repo.state.value.submissions.isEmpty())
        compose.onNodeWithTag("unit-open-answers").assertDoesNotExist()
        val tableIndex=session.items.indices.filter{session.items[it].question.tables.isNotEmpty()&&!session.items[it].question.sql.isNullOrBlank()}
            .maxBy{at->session.items[at].question.tables.sumOf{it.columns.size*it.rows.size}}
        runBlocking{repo.update{StudyEngine.move(it,session.id,tableIndex)}}
        compose.waitUntil(10_000){compose.onAllNodesWithText(session.items[tableIndex].question.stem).fetchSemanticsNodes().isNotEmpty()}
        val config=app.resources.configuration
        if(config.screenWidthDp>=1000&&config.fontScale<=1.2f){
            val viewport=compose.onNodeWithTag("question-area").getUnclippedBoundsInRoot()
            val tables=compose.onAllNodesWithTag("problem-table").fetchSemanticsNodes()
            assertEquals(session.items[tableIndex].question.tables.size,tables.size)
            tables.indices.forEach{at->val bounds=compose.onAllNodesWithTag("problem-table")[at].getUnclippedBoundsInRoot();assertTrue("Full app table fits solving area",bounds.top>=viewport.top&&bounds.bottom<=viewport.bottom&&bounds.right<=viewport.right)}
        }
        capture("app-question")
    }
    @Test fun tableAndCodeStayWithTheQuestionAndAnswersAreSeparate(){
        val id=createSession();val session=repo.state.value.sessions.single()
        val index=session.items.indexOfFirst{it.question.tables.isNotEmpty()&&!it.question.sql.isNullOrBlank()}
        assertTrue("A realistic SQL+table question is required",index>=0)
        runBlocking{repo.update{StudyEngine.move(it,id,index)}}
        compose.runOnUiThread{page.value={ui->SessionScreen(ui,id)}}
        compose.onNodeWithTag("unit-question-material").assertExists()
        val q=session.items[index].question
        compose.onNodeWithText(q.stem).assertExists()
        compose.onAllNodesWithText(q.tables.first().title,substring=true)[0].assertExists()
        compose.onNodeWithTag("unit-open-answers").assertDoesNotExist()
        val config=app.resources.configuration
        if(config.screenWidthDp>=1000&&config.fontScale<=1.2f){
            val viewport=compose.onNodeWithTag("question-area").getUnclippedBoundsInRoot()
            compose.onAllNodesWithTag("problem-table").fetchSemanticsNodes().indices.forEach{at->
                val bounds=compose.onAllNodesWithTag("problem-table")[at].getUnclippedBoundsInRoot()
                assertTrue("Table must be fully visible with the question",bounds.top>=viewport.top&&bounds.bottom<=viewport.bottom&&bounds.right<=viewport.right)
            }
        }
        capture("question")
    }
    @Test fun unfinishedStrictFormCannotRevealAnswerViaAnswerRoute(){
        val id=createSession()
        compose.runOnUiThread{page.value={ui->UnitAnswersScreen(ui,id)}}
        compose.onNodeWithText("풀이를 제출한 뒤 답지·해설을 확인할 수 있어요.").assertExists()
        compose.onNodeWithTag("unit-answers").assertDoesNotExist()
        assertTrue(repo.state.value.submissions.isEmpty())
    }
    @Test fun submittedAnswerKeyUsesSavedChoiceOrderAndPreservesAllSubmissions(){
        val id=createSession();val s=repo.state.value.sessions.single();val q=s.items[0].question
        runBlocking{repo.update{StudyEngine.submit(StudyEngine.select(it,id,0,q.correctChoiceIds.single()),id,2000)}}
        val before=repo.state.value.submissions
        compose.runOnUiThread{page.value={ui->UnitAnswersScreen(ui,id)}}
        val number=s.items[0].choiceOrder.indexOf(q.correctChoiceIds.single())+1
        compose.onNodeWithText("1번 · 정답 $number · 맞음").assertExists()
        capture("answer-key")
        compose.onNodeWithTag("unit-answers").performScrollToNode(hasTestTag("unit-answer-1"))
        compose.onNodeWithTag("unit-answer-1").performScrollTo().performClick()
        compose.onAllNodesWithText(q.explanation.summary)[0].assertExists()
        q.explanation.steps.filter{it.table==null&&it.text!=q.explanation.summary&&q.explanation.summary.contains(it.text)}.forEach{step->
            // The same text belongs in the summary; only its repeated extra section is absent.
            compose.onNodeWithText(step.title).assertDoesNotExist()
        }
        capture("explanation")
        assertEquals(before,repo.state.value.submissions)
        assertEquals(50,before.size)
    }
    @Test fun submittedAnswerReturnsToTheSelectedQuestionInsteadOfTheResultSummary(){
        val id=createSession()
        compose.onNode(hasTestTag("home-compact") or hasTestTag("home-wide")).performScrollToNode(hasText("풀던 문제 이어서") and hasClickAction())
        compose.onNode(hasText("풀던 문제 이어서") and hasClickAction()).performScrollTo().performClick()
        compose.onNodeWithTag("question-area").assertExists()
        runBlocking{repo.update{StudyEngine.submit(it,id,System.currentTimeMillis())}}
        compose.onNodeWithTag("session-result").performScrollToNode(hasText("별도 답지·해설 보기") and hasClickAction())
        compose.onNodeWithText("별도 답지·해설 보기").performScrollTo().performClick()
        compose.onNodeWithTag("unit-answers").performScrollToNode(hasTestTag("unit-answer-2"))
        compose.onNodeWithTag("unit-answer-2").performClick()
        compose.onNodeWithTag("unit-answers").performScrollToNode(hasTestTag("unit-return-question"))
        val records=repo.state.value.submissions
        compose.onNodeWithTag("unit-return-question").performClick()
        compose.waitUntil(10_000){compose.onAllNodesWithTag("unit-question-material").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithTag("session-result").assertDoesNotExist()
        assertEquals(1,repo.state.value.sessions.single().current)
        assertEquals(records,repo.state.value.submissions)
        // Repeat after manually reopening the summary: a saved result flag must not override the return intent.
        compose.onNodeWithText("결과 요약으로").performScrollTo().performClick()
        restoration.emulateSavedInstanceStateRestore()
        compose.onNodeWithTag("session-result").assertExists()
        compose.onNodeWithTag("session-result").performScrollToNode(hasText("별도 답지·해설 보기") and hasClickAction())
        compose.onNodeWithText("별도 답지·해설 보기").performScrollTo().performClick()
        compose.onNodeWithTag("unit-answers").performScrollToNode(hasTestTag("unit-return-question"))
        compose.onNodeWithTag("unit-return-question").performClick()
        compose.waitUntil(10_000){compose.onAllNodesWithTag("unit-question-material").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithTag("session-result").assertDoesNotExist()
        assertEquals(1,repo.state.value.sessions.single().current)
        assertEquals(records,repo.state.value.submissions)
    }
    @Test fun excludedCurrentContentDoesNotDisableResumingAnExistingSnapshot(){
        createSession()
        val q=repo.state.value.sessions.single().items.first().question
        runBlocking{repo.update{it.copy(issues=listOf(ContentIssue("excluded",q.id,it.contentVersion,"검토 대기",true,1)))}}
        compose.runOnUiThread{page.value={ui->UnitMockScreen(ui,"2-1")}}
        compose.onNodeWithTag("unit-mock-forms").performScrollToNode(hasTestTag("unit-mock-1"))
        compose.onNodeWithTag("unit-mock-1").assertIsEnabled()
        assertEquals(50,repo.state.value.sessions.single().items.size)
    }
}
