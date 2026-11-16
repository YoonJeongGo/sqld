package kr.sqld.study

import android.app.Application
import android.graphics.Bitmap
import android.os.SystemClock
import android.util.Log
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.SoftwareKeyboardController
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.StateRestorationTester
import androidx.compose.ui.test.junit4.createComposeRule
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
import org.junit.Assume.assumeTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

/** Run separately at 1280 x 800 dp. Each test uses its own in-memory study database. */
@RunWith(AndroidJUnit4::class)
class SidebarUiTest {
    @get:Rule val compose=createComposeRule()
    private lateinit var repo:StudyRepository
    private lateinit var vm:StudyViewModel
    private lateinit var restoration:StateRestorationTester
    private var keyboard:SoftwareKeyboardController?=null

    @Before fun setup(){
        val app=ApplicationProvider.getApplicationContext<Application>()
        // Both the global rail and the note's nested 840 dp layout need room.
        // Phone suite runs report these tests as skipped, not as tablet coverage.
        assumeTrue("Sidebar UI requires a tablet viewport of at least 1100 dp",app.resources.configuration.screenWidthDp>=1100)
        repo=StudyRepository(app,Room.inMemoryDatabaseBuilder(app,StudyDatabase::class.java).build(),false)
        compose.runOnUiThread { vm=StudyViewModel(app,repo) }
        restoration=StateRestorationTester(compose)
        restoration.setContent { keyboard=LocalSoftwareKeyboardController.current;SqlNoteApp(vm) }
        compose.waitUntil(20000){vm.ready.value}
        compose.waitForIdle()
    }

    @After fun cleanup()=runBlocking {
        if(::vm.isInitialized)vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin()
        if(::repo.isInitialized)repo.db.close()
    }

    private fun state()=repo.state.value
    private fun hideKeyboard(){compose.runOnIdle { keyboard?.hide() };compose.waitForIdle()}
    private fun toggle(){
        try {
            // Compose idle does not include the platform IME's hide/pan animation.
            // Require the real button to become visible before the same assertion/click.
            compose.waitUntil(10000){compose.onNodeWithTag("sidebar-toggle").isDisplayed()}
            compose.onNodeWithTag("sidebar-toggle").assertIsDisplayed().performClick()
            compose.waitForIdle()
        } catch(failure:Throwable) {
            captureToggleFailure()
            throw failure
        }
    }
    private fun captureToggleFailure(){
        val app=ApplicationProvider.getApplicationContext<Application>()
        runCatching {
            val bitmap=InstrumentationRegistry.getInstrumentation().uiAutomation.takeScreenshot()
                ?:throw AssertionError("Could not capture sidebar toggle failure")
            try {
                val file=File(app.cacheDir,"sidebar-toggle-failure.png")
                file.outputStream().use { assertTrue(bitmap.compress(Bitmap.CompressFormat.PNG,100,it)) }
                Log.i("SidebarUiTest","Captured ${file.absolutePath}: ${bitmap.width}x${bitmap.height}")
            } finally { bitmap.recycle() }
        }.onFailure { Log.e("SidebarUiTest","Failure screenshot unavailable",it) }
        runCatching {
            val roots=compose.onAllNodes(isRoot(),useUnmergedTree=true)
            val count=roots.fetchSemanticsNodes().size
            val file=File(app.cacheDir,"sidebar-toggle-failure-semantics.txt")
            file.writeText((0 until count).joinToString("\n\n") { roots[it].printToString() })
            Log.i("SidebarUiTest","Captured ${file.absolutePath}")
        }.onFailure { Log.e("SidebarUiTest","Failure semantics unavailable",it) }
    }
    private fun readerScroll()=compose.onNodeWithTag("note-reader").fetchSemanticsNode().config[SemanticsProperties.VerticalScrollAxisRange].value()
    private fun readerMaximum()=compose.onNodeWithTag("note-reader").fetchSemanticsNode().config[SemanticsProperties.VerticalScrollAxisRange].maxValue()
    private fun logReaderPosition(stage:String){
        Log.i("SidebarUiTest","$stage value=${readerScroll()} max=${readerMaximum()}")
    }
    private fun homeButton(tag:String){
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasTestTag(tag))
        compose.onNodeWithTag(tag).performScrollTo().assertIsDisplayed().performClick()
    }

    @Test fun collapsingAndReopeningBothListsPreservesNotePositionAndAnswers(){
        compose.openHomeTools()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("노트 펼치기") and hasClickAction())
        compose.onNode(hasText("노트 펼치기") and hasClickAction()).performScrollTo().performClick()
        compose.waitUntil(10000){compose.onAllNodesWithTag("note-reader").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithTag("study-sidebar").assertIsDisplayed()
        compose.onNodeWithTag("note-toc").assertIsDisplayed()
        // The end of a long note exercises the width-change clamp, not only an
        // offset that happens to fit both layouts at the original tablet size.
        val initialMaximum=readerMaximum()
        compose.onNodeWithTag("note-reader").performSemanticsAction(SemanticsActions.ScrollBy){it(0f,initialMaximum)}
        compose.waitForIdle()
        val position=readerScroll()
        logReaderPosition("before collapse")
        assertTrue("The reader must actually be scrolled before toggling",position>0)
        compose.waitUntil(10000){state().notes.any { it.noteId==state().lastNoteId&&it.scroll==position.toInt() }}

        val questions=StudyEngine.available(repo.pack,state()).take(2)
        assertEquals(2,questions.size)
        // Preserve both a committed answer and an unfinished draft while resizing.
        val before=runBlocking { repo.update { initial ->
            val created=StudyEngine.createSession(initial,repo.pack,questions,"batch","목록 접기 기록 검증",System.currentTimeMillis(),SystemClock.elapsedRealtime(),0,13)
            val id=created.activeSessionId!!
            val selected=StudyEngine.select(created,id,0,questions[0].choices.first().id)
            val graded=StudyEngine.grade(selected,id,0,System.currentTimeMillis())
            StudyEngine.select(graded,id,1,questions[1].choices.last().id)
        } }
        compose.waitForIdle()

        toggle()
        compose.onNodeWithTag("sidebar-toggle").assertTextContains("목록 펼치기")
        compose.onNodeWithTag("study-sidebar").assertDoesNotExist()
        compose.onNodeWithTag("note-toc").assertDoesNotExist()
        assertTrue("Closing the lists must not restart the reader",readerScroll()>0)
        logReaderPosition("collapsed")
        val collapsedPosition=readerScroll()
        restoration.emulateSavedInstanceStateRestore()
        compose.waitUntil(10000){compose.onAllNodesWithTag("note-reader").fetchSemanticsNodes().isNotEmpty()}
        assertEquals("Recreating a collapsed reader must keep its own position",collapsedPosition,readerScroll(),1f)
        toggle()
        compose.onNodeWithTag("sidebar-toggle").assertTextContains("목록 접기")
        compose.onNodeWithTag("study-sidebar").assertIsDisplayed()
        compose.onNodeWithTag("note-toc").assertIsDisplayed()
        logReaderPosition("reopened")
        assertEquals(position,readerScroll(),1f)
        compose.waitUntil(10000){state().notes.any{it.noteId==state().lastNoteId&&it.scroll==position.toInt()}}
        assertEquals(before.sessions,state().sessions)
        assertEquals(before.submissions,state().submissions)
        assertEquals(before.reviews,state().reviews)
        assertEquals(before.exposures,state().exposures)
        assertEquals(before.annotations,state().annotations)
        assertEquals(before.notes,state().notes)
        assertNull(vm.error.value)
    }

    @Test fun collapsedStateAndSearchQuerySurviveNavigationAndSavedStateRestoration(){
        compose.onNodeWithContentDescription("노트와 연습문제 검색").performClick()
        compose.onNode(hasSetTextAction()).performTextInput("JOIN")
        hideKeyboard()
        toggle()
        compose.onNodeWithTag("study-sidebar").assertDoesNotExist()
        compose.onNode(hasSetTextAction()).assertTextContains("JOIN")

        restoration.emulateSavedInstanceStateRestore()
        compose.waitForIdle()
        compose.onNodeWithTag("sidebar-toggle").assertTextContains("목록 펼치기")
        compose.onNodeWithTag("study-sidebar").assertDoesNotExist()
        compose.onNode(hasSetTextAction()).assertTextContains("JOIN")

        compose.onNodeWithContentDescription("뒤로").performClick()
        compose.onNodeWithText("내 공부").assertIsDisplayed()
        compose.onNodeWithTag("study-sidebar").assertDoesNotExist()
        compose.onNodeWithContentDescription("노트와 연습문제 검색").performClick()
        compose.onNode(hasSetTextAction()).assertTextContains("JOIN")
        toggle()
        compose.onNodeWithTag("study-sidebar").assertIsDisplayed()
        compose.onNode(hasSetTextAction()).assertTextContains("JOIN")
        assertTrue(state().sessions.isEmpty())
        assertTrue(state().submissions.isEmpty())
        assertNull(vm.error.value)
    }

    @Test fun togglingListsKeepsTheTypedCourseSelfCheckAndSelectedSection(){
        val lesson=repo.course.lessons.first()
        val check=lesson.selfChecks.first()
        val draft="목록을 접어도 남아야 하는 자기점검 답안"
        homeButton("home-course-resume")
        compose.waitUntil(10000){compose.onAllNodesWithTag("lesson-reader").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithTag("lesson-section-checks").performClick()
        compose.onNodeWithTag("course-draft-${check.id}").performScrollTo().performTextInput(draft)
        hideKeyboard()
        compose.waitUntil(10000){CourseStudy.progress(state(),lesson.id).checks.any { it.checkId==check.id&&it.draft==draft }}
        val before=state()

        toggle()
        compose.onNodeWithTag("study-sidebar").assertDoesNotExist()
        compose.onNodeWithTag("lesson-section-checks").assertIsSelected()
        compose.onNodeWithTag("course-draft-${check.id}").performScrollTo().assertTextContains(draft)
        toggle()
        compose.onNodeWithTag("study-sidebar").assertIsDisplayed()
        compose.onNodeWithTag("lesson-section-checks").assertIsSelected()
        compose.onNodeWithTag("course-draft-${check.id}").performScrollTo().assertTextContains(draft)
        assertEquals(before.courseProgress.single().checks,CourseStudy.progress(state(),lesson.id).checks)
        assertEquals(before.sessions,state().sessions)
        assertEquals(before.submissions,state().submissions)
        assertNull(vm.error.value)
    }
}
