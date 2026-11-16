package kr.sqld.study

import android.app.Application
import android.graphics.Bitmap
import android.os.SystemClock
import android.provider.Settings
import android.util.Log
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.SoftwareKeyboardController
import androidx.compose.ui.test.*
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
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

/** Actual app navigation and editing against the bundled packs and an isolated in-memory DB. */
@RunWith(AndroidJUnit4::class)
class CourseUiTest {
    @get:Rule val compose=createComposeRule()
    private lateinit var app:Application
    private lateinit var repo:StudyRepository
    private lateinit var vm:StudyViewModel
    private var keyboard:SoftwareKeyboardController?=null

    @Before fun setup(){
        app=ApplicationProvider.getApplicationContext()
        repo=StudyRepository(app,Room.inMemoryDatabaseBuilder(app,StudyDatabase::class.java).build(),false)
        compose.runOnUiThread { vm=StudyViewModel(app,repo) }
        compose.setContent { keyboard=LocalSoftwareKeyboardController.current;SqlNoteApp(vm) }
        compose.waitUntil(20000){vm.ready.value}
        compose.waitForIdle()
    }

    @After fun cleanup()=runBlocking {
        vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin()
        repo.db.close()
    }

    private fun state()=repo.state.value
    private fun progress(id:String)=CourseStudy.progress(state(),id)
    private fun homeButton(tag:String){
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasTestTag(tag))
        // A large-font Paper can be taller than the viewport. Bringing the lazy item
        // into composition does not yet guarantee its nested button is visible.
        compose.onNodeWithTag(tag).performScrollTo().assertIsDisplayed().performClick()
    }
    private fun openLesson(){
        homeButton("home-course-resume")
        compose.waitUntil(10000){compose.onAllNodesWithTag("lesson-reader").fetchSemanticsNodes().isNotEmpty()}
    }
    private fun hideKeyboard(){compose.runOnIdle { keyboard?.hide() };compose.waitForIdle()}
    private fun capture(name:String){
        compose.waitForIdle()
        val bitmap=InstrumentationRegistry.getInstrumentation().uiAutomation.takeScreenshot()
            ?:throw AssertionError("Could not capture course UI")
        val file=File(app.cacheDir,name)
        file.outputStream().use { assertTrue(bitmap.compress(Bitmap.CompressFormat.PNG,100,it)) }
        Log.i("CourseUiTest","Captured ${file.absolutePath}: ${bitmap.width}x${bitmap.height}, ${file.length()} bytes")
        bitmap.recycle()
    }
    private fun ratingNode(tag:String):SemanticsNodeInteraction {
        compose.waitUntil(10000){compose.onAllNodesWithTag(tag,useUnmergedTree=true).fetchSemanticsNodes().isNotEmpty()}
        return compose.onNodeWithTag(tag,useUnmergedTree=true)
    }
    private fun captureGuardFailure(){
        runCatching { capture("course-guard-font-failure.png") }
            .onFailure { Log.e("CourseUiTest","Failure screenshot unavailable",it) }
        runCatching {
            val roots=compose.onAllNodes(isRoot(),useUnmergedTree=true)
            val count=roots.fetchSemanticsNodes().size
            val file=File(app.cacheDir,"course-guard-font-failure-semantics.txt")
            file.writeText((0 until count).joinToString("\n\n") { roots[it].printToString() })
            Log.i("CourseUiTest","Captured ${file.absolutePath}")
        }.onFailure { Log.e("CourseUiTest","Failure semantics unavailable",it) }
    }

    @Test fun lessonDraftsRatingsReadAndExampleProgressSurviveReturningWithoutScoring(){
        val lesson=repo.course.lessons.first()
        val before=state()
        assertEquals(3,lesson.selfChecks.size)
        openLesson()
        compose.onNodeWithTag("lesson-section-checks").performClick()
        lesson.selfChecks.forEachIndexed { index,check ->
            val draft="직접 설명한 답안 ${index+1}"
            compose.onNodeWithTag("course-draft-${check.id}").performScrollTo().performTextInput(draft)
            hideKeyboard()
            compose.waitUntil(10000){progress(lesson.id).checks.any { it.checkId==check.id&&it.draft==draft }}
            compose.onNodeWithTag("course-reveal-${check.id}").performScrollTo().performClick()
            compose.waitUntil(10000){progress(lesson.id).checks.any { it.checkId==check.id&&it.revealed }}
            compose.waitForIdle()
            val rating=if(index==1)"review"else"understood"
            ratingNode("course-rating-$rating-${check.id}").performScrollTo().assertIsDisplayed().performClick()
            compose.waitUntil(10000){progress(lesson.id).checks.any { it.checkId==check.id&&it.rating==rating }}
        }
        compose.onNodeWithTag("lesson-section-examples").performClick()
        val example=lesson.examples.first()
        repeat(example.steps.size){index->
            compose.onNodeWithTag("course-example-next-${example.id}").performScrollTo().performClick()
            compose.waitUntil(10000){progress(lesson.id).exampleSteps[example.id]==index+1}
        }
        compose.onNodeWithTag("course-result-${example.id}").performScrollTo().assertIsEnabled().performClick()
        compose.waitUntil(10000){example.id in progress(lesson.id).revealedResults}
        compose.openLessonTools()
        compose.onNodeWithTag("lesson-read-toggle").performScrollTo().performClick()
        compose.waitUntil(10000){progress(lesson.id).readVersion==lesson.version}
        compose.onNodeWithContentDescription("뒤로").performClick()
        homeButton("home-course-list")
        compose.onNodeWithTag("course-list").performScrollToNode(hasText(lesson.title) and hasClickAction())
        compose.onNode(hasText(lesson.title) and hasClickAction()).performClick()
        compose.onNodeWithTag("lesson-section-examples").assertIsSelected()
        assertEquals(example.steps.size,progress(lesson.id).exampleSteps[example.id])
        assertEquals(listOf(example.id),progress(lesson.id).revealedResults)
        compose.onNodeWithTag("lesson-section-checks").performClick()
        lesson.selfChecks.forEachIndexed { index,check ->
            compose.onNodeWithTag("course-draft-${check.id}").performScrollTo().assertTextContains("직접 설명한 답안 ${index+1}")
            val rating=if(index==1)"review"else"understood"
            ratingNode("course-rating-$rating-${check.id}").performScrollTo().assertIsDisplayed().assertIsSelected()
        }
        assertEquals(lesson.id,state().lastLessonId)
        assertEquals(1,state().courseProgress.size)
        assertEquals(before.submissions,state().submissions)
        assertEquals(before.sessions,state().sessions)
        assertEquals(before.reviews,state().reviews)
        assertEquals(before.exposures,state().exposures)
        assertEquals(before.notes,state().notes)
        assertEquals(before.bookmarks,state().bookmarks)
        assertEquals(before.noteBookmarks,state().noteBookmarks)
        assertEquals(before.annotations,state().annotations)
        assertNull(vm.error.value)
    }

    @Test fun enteringCourseDuringStrictMockRequiresConversionAndKeepsDraft(){
        try {
        val mockId=repo.pack.questions.first { it.kind=="mock"&&it.mockSetId!=null }.mockSetId!!
        val questions=repo.pack.mock(mockId)
        assertEquals(50,questions.size)
        val created=runBlocking { repo.update { s -> StudyEngine.createSession(s,repo.pack,questions,"strict","강의 이동 실전 보호",System.currentTimeMillis(),SystemClock.elapsedRealtime(),Settings.Global.getInt(app.contentResolver,Settings.Global.BOOT_COUNT,0),9,mockId) } }
        val sessionId=created.activeSessionId!!
        compose.resumeProblem()
        val choice=questions.first().choices.first()
        compose.onNodeWithText(choice.text).performScrollTo().performClick()
        compose.waitUntil(10000){state().sessions.first { it.id==sessionId }.items.first().draft==listOf(choice.id)}
        compose.onNodeWithContentDescription("뒤로").performClick()
        homeButton("home-course-list")
        capture("course-guard-font.png")
        compose.waitUntil(10000){compose.onAllNodesWithText("연습 모드로 전환할까요?").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithText("연습 모드로 전환할까요?").assertIsDisplayed()
        compose.onNodeWithTag("course-list").assertDoesNotExist()
        assertEquals("strict",state().sessions.first { it.id==sessionId }.mode)
        compose.onNodeWithText("실전 유지").performClick()
        assertEquals("strict",state().sessions.first { it.id==sessionId }.mode)
        homeButton("home-course-list")
        compose.onNodeWithText("전환하고 보기").performClick()
        compose.waitUntil(10000){compose.onAllNodesWithTag("course-list").fetchSemanticsNodes().isNotEmpty()}
        val session=state().sessions.first { it.id==sessionId }
        assertEquals("mixed",session.mode)
        assertNotNull(session.convertedAt)
        assertFalse(session.diagnosticEligible)
        assertEquals(listOf(choice.id),session.items.first().draft)
        assertTrue(state().submissions.isEmpty())
        assertNull(vm.error.value)
        } catch(failure:Throwable) {
            captureGuardFailure()
            throw failure
        }
    }

    @Test fun linkedPracticeStartsOnlyOrdinaryQuestionsEvenAfterMockWasExposed(){
        val mockObjectives=repo.pack.questions.filter { it.kind=="mock" }.flatMap { it.objectiveIds }.toSet()
        val lesson=repo.course.lessons.first { lesson ->
            lesson.relatedNoteIds.any { noteId -> repo.pack.notes.any { it.id==noteId&&it.objectiveId in mockObjectives } }
        }
        val objectives=lesson.relatedNoteIds.mapNotNull { id -> repo.pack.notes.find { it.id==id }?.objectiveId }.toSet()
        val mock=repo.pack.questions.first { it.kind=="mock"&&it.objectiveIds.any { id->id in objectives } }
        // This is a previously seen mock question; it must still stay out of course practice.
        runBlocking { repo.update { it.copy(lastLessonId=lesson.id,exposures=listOf(Exposure("course-test-seen",mock.id,mock.familyId,"previous-mock","seen",System.currentTimeMillis()))) } }
        assertTrue(StudyEngine.available(repo.pack,state()).any { it.id==mock.id })
        val available=StudyEngine.available(repo.pack,state()).filter { q -> q.kind!="mock"&&q.mockSetId==null&&q.objectiveIds.any { it in objectives } }
        assertTrue(available.isNotEmpty())
        openLesson()
        compose.openLessonTools()
        compose.onNodeWithTag("course-practice").performScrollTo().performClick()
        compose.onNodeWithText("대상 ${available.size}문항 · 중복 없이 최대 ${available.size}문항").assertExists()
        val count=minOf(state().settings.dailyCount,available.size)
        compose.onNodeWithText("${count}문항 시작").performClick()
        compose.waitUntil(10000){state().sessions.isNotEmpty()}
        val questions=state().sessions.single().items.map { it.question }
        assertEquals(count,questions.size)
        assertTrue(questions.all { q -> q.kind!="mock"&&q.mockSetId==null&&q.id in available.map { it.id } })
        assertFalse(questions.any { it.id==mock.id })
        assertTrue(state().submissions.isEmpty())
        assertNull(vm.error.value)
    }
}
