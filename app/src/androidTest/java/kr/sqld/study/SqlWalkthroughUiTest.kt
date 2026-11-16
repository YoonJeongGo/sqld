package kr.sqld.study

import android.app.Application
import android.os.SystemClock
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.StateRestorationTester
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

/** In-memory records only. Saved-instance restoration is distinct from physical Galaxy rotation. */
@RunWith(AndroidJUnit4::class)
class SqlWalkthroughUiTest {
    @get:Rule val compose=createComposeRule()
    private lateinit var app:Application
    private lateinit var repo:StudyRepository
    private lateinit var vm:StudyViewModel
    private lateinit var restoration:StateRestorationTester
    @Before fun setup(){
        app=ApplicationProvider.getApplicationContext()
        repo=StudyRepository(app,Room.inMemoryDatabaseBuilder(app,StudyDatabase::class.java).build(),false)
        compose.runOnUiThread{vm=StudyViewModel(app,repo)}
        restoration=StateRestorationTester(compose)
        restoration.setContent{SqlNoteApp(vm)}
        compose.waitUntil(20000){vm.ready.value};compose.waitForIdle()
    }
    @After fun cleanup()=runBlocking{vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin();repo.db.close()}
    private fun source()=repo.pack.questions.single{it.id=="S07-A02"}
    private fun material()=app.assets.open("sql-walkthroughs/S07-A02.json").bufferedReader().use{Codec.decodeFromString<SqlWalkthrough>(it.readText())}
    private fun session()=repo.state.value.sessions.last()
    private fun openQuestion(){
        runBlocking{repo.update{StudyEngine.createSession(it,repo.pack,listOf(source()),"immediate","SQL 따라읽기 검사",System.currentTimeMillis(),SystemClock.elapsedRealtime(),0,23)}}
        // Lazy children outside a narrow/large-font viewport must first be composed by parent scrolling.
        compose.onNode(hasTestTag("home-compact") or hasTestTag("home-wide"))
            .performScrollToNode(hasText("풀던 문제 이어서") and hasClickAction())
        compose.onNode(hasText("풀던 문제 이어서") and hasClickAction()).performScrollTo().performClick()
        compose.waitUntil(10000){compose.onAllNodesWithText("이 문제 채점").fetchSemanticsNodes().isNotEmpty()}
    }
    private fun gradeAndRead(){
        val answer=source().choices.single{it.id==source().correctChoiceIds.single()}
        compose.onNodeWithText(answer.text).performScrollTo().performClick()
        compose.waitUntil(10000){session().items.single().draft.isNotEmpty()}
        compose.onNodeWithText("이 문제 채점").performClick()
        compose.waitUntil(10000){repo.state.value.submissions.size==1&&compose.onAllNodesWithTag("reader-mode-walk").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithTag("reader-mode-walk").performScrollTo().performClick()
        compose.waitUntil(10000){compose.onAllNodesWithTag("walk-step-title").fetchSemanticsNodes().isNotEmpty()}
    }
    private fun title()=compose.onNodeWithTag("walk-step-title").fetchSemanticsNode().config[SemanticsProperties.Text].single().text

    @Test fun selectingAnAnswerDoesNotLoadOrRevealWalkthroughBeforeGrading(){
        openQuestion()
        assertEquals(0,vm.walkthroughs.materialReads)
        compose.onNodeWithTag("walk-next").assertDoesNotExist()
        compose.onNodeWithTag("walk-step-title").assertDoesNotExist()
        compose.onNodeWithTag("question-guide-links").assertDoesNotExist()
        assertEquals(0,vm.lessonGuides.materialReads)
        val answer=source().choices.single{it.id==source().correctChoiceIds.single()}
        compose.onNodeWithText(answer.text).performScrollTo().performClick()
        compose.waitUntil(10000){session().items.single().draft.isNotEmpty()}
        assertTrue(repo.state.value.submissions.isEmpty())
        assertEquals(0,vm.walkthroughs.materialReads)
        compose.onNodeWithTag("walk-step-title").assertDoesNotExist()
        compose.onNodeWithText("이 문제 채점").performClick()
        compose.waitUntil(10000){vm.walkthroughs.materialReads==1}
        assertEquals(source(),session().items.single().question)
        assertEquals(1,repo.state.value.submissions.size)
    }

    @Test fun gradedQuestionOpensSeparateLessonGuideAndReturnsWithoutChangingSubmission(){
        openQuestion();gradeAndRead()
        val original=repo.state.value.submissions
        compose.onNodeWithTag("question-guide-links").performScrollTo().performClick()
        val lesson=repo.course.lessons.first{source().explanation.relatedNoteId in it.relatedNoteIds}
        compose.onNode(hasText(lesson.title) and hasClickAction()).performScrollTo().performClick()
        compose.waitUntil(10000){compose.onAllNodesWithTag("lesson-guide-dialog").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithTag("guide-tab-read").performScrollTo().performClick()
        compose.onNode(hasTestTag("walk-next") and hasAnyAncestor(hasTestTag("lesson-guide-dialog"))).performClick()
        compose.onNodeWithTag("guide-close").performClick()
        assertEquals(original,repo.state.value.submissions)
        assertEquals(material().steps[0].title,title())
    }

    @Test fun codeViewportFitsFirstLineBeforeAndAfterGradingAtCurrentFontScale(){
        fun assertFirstLineFits(phase:String){
            val code=compose.onNodeWithTag("ink-code-surface").assertIsDisplayed()
            val bounds=code.fetchSemanticsNode().boundsInRoot
            // The native document draws its first baseline at 32 units; reserve 6 more for descent.
            // Merely finding a SQL accessibility node does not prove these glyphs fit in its viewport.
            val minimumHeightPx=(32f+6f)*app.resources.configuration.fontScale*
                app.resources.displayMetrics.density*repo.state.value.settings.textScale
            assertTrue("$phase: code height ${bounds.height}px must fit first-line baseline/descent ${minimumHeightPx}px",
                bounds.height+0.5f>=minimumHeightPx)
        }
        openQuestion()
        // Solving keeps source tables open; the document-coordinate ink surface opens on demand.
        compose.onNodeWithText("코드에 펜으로 필기").performScrollTo().performClick()
        assertFirstLineFits("before grading")
        gradeAndRead()
        assertFirstLineFits("after grading")
        compose.onNodeWithTag("reader-mode-walk").assertIsDisplayed()
        compose.onNodeWithTag("walk-step-title").assertIsDisplayed()
        compose.onNodeWithText("직접 따라 읽기").assertIsDisplayed()
        compose.onNodeWithTag("walk-next").assertIsDisplayed().performClick()
        compose.onNodeWithTag("walk-step-title").assertIsDisplayed()
        assertEquals(material().steps[1].title,title())
        assertFirstLineFits("after next step")
    }

    @Test fun nextPreviousAndModeRoundTripRestoreExactStepAndOpenFoundations(){
        openQuestion();gradeAndRead()
        val expected=material();assertEquals(expected.steps[0].title,title())
        compose.onNodeWithTag("walk-next").performClick()
        assertEquals(expected.steps[1].title,title())
        compose.onNodeWithTag("walk-previous").performClick()
        assertEquals(expected.steps[0].title,title())
        compose.onNodeWithTag("walk-next").performClick()
        compose.onNodeWithTag("walk-foundations-toggle").performScrollTo().performClick()
        compose.onNodeWithTag("walk-foundations").assertExists()
        compose.onNodeWithTag("walk-next").performClick()
        assertEquals(expected.steps[2].title,title())
        compose.onNodeWithTag("walk-foundations").assertExists()
        val answers=repo.state.value.submissions
        compose.onNodeWithTag("reader-mode-original").performScrollTo().performClick()
        compose.onNodeWithTag("walk-step-title").assertDoesNotExist()
        compose.onNodeWithTag("reader-mode-walk").performScrollTo().performClick()
        assertEquals(expected.steps[2].title,title())
        compose.onNodeWithTag("walk-foundations").assertExists()
        compose.onNodeWithTag("reader-mode-question").performScrollTo().performClick()
        compose.onNodeWithTag("reader-mode-walk").performScrollTo().performClick()
        assertEquals(expected.steps[2].title,title())
        assertEquals(answers,repo.state.value.submissions)
    }

    @Test fun savedInstanceRestorationKeepsCurrentStepAndFoundationExpansion(){
        openQuestion();gradeAndRead()
        compose.onNodeWithTag("walk-next").performClick()
        compose.onNodeWithTag("walk-foundations-toggle").performScrollTo().performClick()
        val selectedTitle=title();val answers=repo.state.value.submissions
        restoration.emulateSavedInstanceStateRestore()
        compose.waitUntil(10000){compose.onAllNodesWithTag("walk-step-title").fetchSemanticsNodes().isNotEmpty()}
        assertEquals(selectedTitle,title())
        compose.onNodeWithTag("walk-foundations").assertExists()
        assertEquals(answers,repo.state.value.submissions)
        assertEquals(1,vm.walkthroughs.materialReads)
    }

    @Test fun catalogIsLazyRejectsChangedSnapshotsAndKeepsAtMostSixRecentDocuments()=runBlocking {
        val index=app.assets.open("sql-walkthroughs/index.json").bufferedReader().use{Codec.decodeFromString<WalkIndex>(it.readText())}
        val catalog=WalkthroughCatalog(app)
        assertEquals(0,catalog.materialReads)
        val questions=index.entries.take(7).map{ref->repo.pack.questions.single{it.id==ref.questionId}}
        assertNotNull(catalog.question(questions[0]));assertEquals(1,catalog.materialReads)
        assertNotNull(catalog.question(questions[0]));assertEquals(1,catalog.materialReads)
        questions.drop(1).forEach{assertNotNull(catalog.question(it))}
        assertEquals(7,catalog.materialReads)
        assertNotNull(catalog.question(questions[0]));assertEquals(8,catalog.materialReads)
        assertNull(catalog.question(questions[0].copy(sql=questions[0].sql+" ")))
        assertNull(catalog.question(questions[0].copy(stem="수정된 조건")))
        assertEquals(8,catalog.materialReads)
        index.entries.forEach{ref->assertNotNull(catalog.question(repo.pack.questions.single{it.id==ref.questionId}))}
        index.learningExamples.forEach{assertNotNull(catalog.learning(it.id))}
        assertTrue(repo.state.value.submissions.isEmpty())
    }

    @Test fun olderFailedStrokeDoesNotLeaveAnErrorAfterNewerDraftIsSaved(){
        val empty=InkStore.empty("isolated-save-race","SELECT 1 FROM DUAL")
        val first=InkStore.add(empty,InkStroke("first",points=listOf(InkPoint(10f,20f))),1)
        val second=InkStore.add(first,InkStroke("second",points=listOf(InkPoint(30f,20f))),2)
        compose.runOnUiThread{
            repo.failNextWrite=true
            vm.saveInk(first)
            vm.saveInk(second)
        }
        compose.waitUntil(10000){repo.state.value.inkDocuments.singleOrNull()?.cursor==2&&vm.inkDrafts.value.isEmpty()}
        assertTrue(vm.inkErrors.value.isEmpty())
        assertEquals(second,repo.state.value.inkDocuments.single())
        assertTrue(repo.state.value.submissions.isEmpty())
    }
}
