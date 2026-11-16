package kr.sqld.study

import android.app.Application
import android.graphics.Bitmap
import android.os.SystemClock
import androidx.compose.ui.graphics.asAndroidBitmap
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.junit4.StateRestorationTester
import androidx.compose.ui.unit.dp
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

/** Captures existing production routes with bundled content and an isolated empty database. */
@RunWith(AndroidJUnit4::class)
class UnitMockFlowCaptureTest {
    @get:Rule val compose = createComposeRule()
    private lateinit var app: Application
    private lateinit var repo: StudyRepository
    private lateinit var vm: StudyViewModel
    private lateinit var restoration: StateRestorationTester

    @Before fun setup() {
        app = ApplicationProvider.getApplicationContext()
        repo = StudyRepository(app, Room.inMemoryDatabaseBuilder(app, StudyDatabase::class.java).build(), false)
        compose.runOnUiThread { vm = StudyViewModel(app, repo) }
        restoration = StateRestorationTester(compose)
        restoration.setContent { SqlNoteApp(vm) }
        compose.waitUntil(30_000) { vm.ready.value }
        compose.waitForIdle()
    }

    @After fun cleanup() = runBlocking {
        vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin()
        repo.db.close()
    }

    private fun capture(name: String) {
        compose.waitForIdle()
        // AndroidView text and Compose choices may publish their display lists on
        // adjacent native frames. Let both draw before collecting a review image.
        compose.mainClock.advanceTimeByFrame()
        SystemClock.sleep(350)
        InstrumentationRegistry.getInstrumentation().waitForIdleSync()
        compose.waitForIdle()
        val bitmap = compose.onRoot().captureToImage().asAndroidBitmap()
        File(app.cacheDir, "mock-flow-$name.png").outputStream().use {
            assertTrue(bitmap.compress(Bitmap.CompressFormat.PNG, 100, it))
        }
        bitmap.recycle()
    }

    @Test fun currentUnitMockEntryToSolvingScreens() {
        compose.onNodeWithTag("nav-mock").performClick()
        compose.onNodeWithTag("unit-mock-parts").assertExists()
        compose.onNodeWithTag("unit-review-start").assertDoesNotExist()
        if(app.resources.configuration.screenWidthDp>=1000 && app.resources.configuration.fontScale<=1.2f) {
            repo.unitBank.parts.forEach { compose.onNodeWithTag("mock-unit-${it.id}").assertIsDisplayed() }
        }
        capture("01-parts")
        compose.onNodeWithTag("unit-mock-parts").performScrollToNode(hasTestTag("mock-unit-2-1"))
        compose.onNodeWithTag("mock-unit-2-1").performClick()
        compose.onNodeWithTag("unit-review-start").assertDoesNotExist()
        compose.onNodeWithTag("unit-mock-1").assertExists()
        capture("02-forms")
        restoration.emulateSavedInstanceStateRestore()
        compose.onNodeWithTag("unit-mock-forms").assertExists()
        compose.onNodeWithContentDescription("뒤로").performClick()
        compose.onNodeWithTag("unit-mock-parts").assertExists()
        compose.onNodeWithTag("unit-mock-parts").performScrollToNode(hasTestTag("mock-unit-2-1"))
        compose.onNodeWithTag("mock-unit-2-1").performClick()
        compose.onNodeWithTag("unit-mock-1").performScrollTo()
        compose.onNodeWithTag("unit-mock-1").performClick()
        compose.onNodeWithTag("unit-mock-confirm").assertIsDisplayed()
        compose.onNodeWithTag("unit-mock-confirm").performClick()
        compose.waitUntil(15_000) { repo.state.value.sessions.size == 1 }
        compose.onNodeWithTag("question-area").assertExists()
        val session = repo.state.value.sessions.single()
        assertEquals("unit:2-1:1", session.mockSetId)
        assertEquals(50, session.items.size)
        compose.onNodeWithTag("unit-open-answers").assertDoesNotExist()
        compose.onNodeWithTag("session-grade").assertDoesNotExist()
        compose.onNodeWithTag("session-unknown").assertDoesNotExist()
        assertFooterVisible()
        capture("03-first-question")
        val choiceId = session.items.first().question.correctChoiceIds.single()
        compose.onNodeWithTag("session-choice-$choiceId").performScrollTo().performClick()
        compose.waitUntil(10_000) { repo.state.value.sessions.single().items.first().draft == listOf(choiceId) }
        restoration.emulateSavedInstanceStateRestore()
        waitSelected(choiceId)
        compose.onNodeWithTag("session-choice-$choiceId").assertIsSelected()

        // Representative SQL/table item from the same actual form. No question or answer data is changed.
        val tableIndex = session.items.indexOfFirst { it.question.tables.isNotEmpty() && !it.question.sql.isNullOrBlank() }
        assertTrue(tableIndex >= 0)
        repeat(tableIndex) { index ->
            compose.onNodeWithTag("session-next").performClick()
            compose.waitUntil(10_000) { repo.state.value.sessions.single().current == index + 1 }
        }
        compose.waitUntil(10_000) { repo.state.value.sessions.single().current == tableIndex }
        compose.onNodeWithTag("unit-question-material").assertExists()
        val tableQuestion=repo.state.value.sessions.single().items[tableIndex].question
        try {
            compose.waitUntil(10_000) {
                tableQuestion.choices.all { choice ->
                    compose.onAllNodesWithTag("session-choice-${choice.id}").fetchSemanticsNodes().size==1
                }
            }
        } catch(error:Throwable) {
            File(app.cacheDir,"mock-flow-question-tree.json").writeText(
                org.json.JSONObject().put("expectedQuestion",tableQuestion.id)
                    .put("tree",compose.onRoot().printToString()).toString()
            )
            throw error
        }
        tableQuestion.choices.forEach { choice ->
            compose.onNodeWithTag("session-choice-${choice.id}").assertExists().assertTextContains(choice.text)
        }
        if(tableIndex!=0) {
            assertTrue(repo.state.value.sessions.single().items[tableIndex].draft.isEmpty())
            compose.onNodeWithTag("session-choice-$choiceId").assertDoesNotExist()
        }
        assertFooterVisible()
        capture("04-sql-table-question")
        val tableChoice=tableQuestion.correctChoiceIds.single()
        compose.onNodeWithTag("session-choice-$tableChoice").performScrollTo().performClick()
        compose.waitUntil(10_000) { repo.state.value.sessions.single().items[tableIndex].draft==listOf(tableChoice) }
        assertEquals(listOf(choiceId),repo.state.value.sessions.single().items.first().draft)
        repeat(tableIndex) { index ->
            compose.onNodeWithTag("session-previous").performClick()
            compose.waitUntil(10_000) { repo.state.value.sessions.single().current == tableIndex-index-1 }
        }
        waitSelected(choiceId)
        compose.onNodeWithTag("session-choice-$choiceId").assertIsSelected()
        assertEquals("strict",repo.state.value.sessions.single().mode)
        assertEquals(session.items.map{it.question},repo.state.value.sessions.single().items.map{it.question})
        assertEquals(session.items.map{it.choiceOrder},repo.state.value.sessions.single().items.map{it.choiceOrder})
        File(app.cacheDir, "mock-flow-capture.json").writeText(
            """{"appVersion":"0.11.0","unit":"2-1","form":1,"questionCount":50,"tableQuestionNumber":${tableIndex + 1},"isolatedInMemoryDatabase":true,"widthDp":${app.resources.configuration.screenWidthDp},"heightDp":${app.resources.configuration.screenHeightDp}}"""
        )
        assertTrue(repo.state.value.submissions.isEmpty())
        assertNull(vm.error.value)
    }

    private fun waitSelected(choiceId:String) {
        compose.waitUntil(10_000) {
            compose.onAllNodes(hasTestTag("session-choice-$choiceId") and isSelected()).fetchSemanticsNodes().size==1
        }
    }

    private fun assertFooterVisible() {
        val root = compose.onRoot().getUnclippedBoundsInRoot()
        listOf("session-previous","session-next","session-submit").forEach { tag ->
            compose.onNodeWithTag(tag).assertIsDisplayed()
            val box = compose.onNodeWithTag(tag).getUnclippedBoundsInRoot()
            assertTrue("$tag touch height",box.bottom-box.top>=48.dp)
            assertTrue("$tag is not clipped",box.left>=root.left && box.right<=root.right && box.bottom<=root.bottom && box.top>=root.top)
        }
    }

    private fun createForm(): QuizSession {
        val now=System.currentTimeMillis()
        val boot=android.provider.Settings.Global.getInt(app.contentResolver,android.provider.Settings.Global.BOOT_COUNT,0)
        runBlocking { repo.update { UnitPractice.create(it,repo.pack,repo.unitBank,"2-1",1,now,android.os.SystemClock.elapsedRealtime(),boot,7) } }
        return repo.state.value.sessions.single()
    }

    @Test fun unitReviewIsSeparateAndFullRangeMocksRemainReachable() {
        compose.onNodeWithTag("nav-review").performClick()
        compose.onNodeWithTag("nav-review").assertIsSelected()
        compose.onNodeWithTag("review-list").performScrollToNode(hasTestTag("review-unit-practice"))
        compose.onNodeWithTag("review-unit-practice").performClick()
        compose.onNodeWithTag("unit-practice").performScrollToNode(hasTestTag("unit-open-2-1"))
        compose.onNodeWithTag("unit-open-2-1").performClick()
        compose.onNodeWithTag("unit-review-start").assertExists()
        compose.onNodeWithTag("unit-mock-1").assertDoesNotExist()
        compose.onNodeWithTag("nav-review").assertIsSelected()
        capture("05-review")
        compose.onNodeWithTag("unit-review-start").performScrollTo().performClick()
        compose.onNodeWithText("연습 시작").assertIsDisplayed()
        compose.onNodeWithText("취소").performClick()
        assertTrue(repo.state.value.sessions.isEmpty())
        compose.onNodeWithTag("nav-mock").performClick()
        compose.onNodeWithTag("unit-mock-parts").performScrollToNode(hasText("SQLD 전체 범위 모의고사"))
        compose.onNodeWithText("SQLD 전체 범위 모의고사").performClick()
        compose.onNodeWithTag("full-mock-list").assertExists()
        compose.onNodeWithTag("nav-mock").assertIsSelected()
        compose.onNodeWithText("단원 모의고사로 이동").performScrollTo().performClick()
        compose.onNodeWithTag("unit-mock-parts").assertExists()
    }

    @Test fun unfinishedFormResumesItsSavedSnapshotAndDraftWithoutAnotherSession() {
        val original=createForm()
        val choice=original.items.first().choiceOrder.first()
        runBlocking { repo.update { StudyEngine.select(it,original.id,0,choice).copy(bookmarks=listOf(Bookmark(original.items.first().question.id,123))) } }
        val before=repo.state.value
        compose.onNodeWithTag("nav-mock").performClick()
        compose.onNodeWithTag("unit-mock-parts").performScrollToNode(hasTestTag("mock-unit-2-1"))
        compose.onNodeWithTag("mock-unit-2-1").performClick()
        compose.onNodeWithTag("unit-mock-1").performScrollTo().assertTextContains("이어서 풀기").performClick()
        compose.onNodeWithTag("unit-mock-confirm").assertDoesNotExist()
        compose.onNodeWithTag("session-choice-$choice").assertIsSelected()
        assertEquals(1,repo.state.value.sessions.size)
        assertEquals(original.id,repo.state.value.activeSessionId)
        assertEquals(before.bookmarks,repo.state.value.bookmarks)
        val after=repo.state.value.sessions.single()
        assertEquals(before.sessions.single().items.map{it.question},after.items.map{it.question})
        assertEquals(before.sessions.single().items.map{it.choiceOrder},after.items.map{it.choiceOrder})
        assertEquals(before.sessions.single().items.map{it.draft},after.items.map{it.draft})
        assertEquals(before.sessions.single().examSpec,after.examSpec)
        assertTrue(repo.state.value.submissions.isEmpty())
        compose.onNodeWithTag("session-grade").assertDoesNotExist()
    }

    @Test fun lastQuestionRequiresExplicitWholeSubmissionAndKeepsStableChoiceGrading() {
        val original=createForm()
        val last=original.items.last()
        runBlocking { repo.update { StudyEngine.move(it,original.id,49) } }
        compose.resumeProblem()
        compose.onNodeWithTag("session-next").assertIsNotEnabled()
        compose.onNodeWithTag("session-grade").assertDoesNotExist()
        compose.onNodeWithTag("session-choice-${last.question.correctChoiceIds.single()}").performScrollTo().performClick()
        compose.waitUntil(10_000) { repo.state.value.sessions.single().items.last().draft.isNotEmpty() }
        assertFooterVisible()
        capture("06-last-question")
        compose.onNodeWithTag("session-submit").performClick()
        compose.onNodeWithText("전체 제출 확정").assertIsDisplayed()
        compose.onNodeWithText("계속 풀기").performClick()
        assertTrue(repo.state.value.submissions.isEmpty())
        compose.onNodeWithTag("session-submit").performClick()
        compose.onNodeWithText("전체 제출 확정").performClick()
        compose.waitUntil(15_000) { repo.state.value.submissions.size==50 }
        val submission=repo.state.value.submissions.single { it.questionId==last.question.id }
        assertEquals(last.question.correctChoiceIds,submission.choiceIds)
        assertEquals("correct",submission.outcome)
        assertEquals(original.items.map{it.question},repo.state.value.sessions.single().items.map{it.question})
        assertEquals(original.items.map{it.choiceOrder},repo.state.value.sessions.single().items.map{it.choiceOrder})
    }
}
