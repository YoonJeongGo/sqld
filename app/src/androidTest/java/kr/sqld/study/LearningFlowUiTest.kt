package kr.sqld.study

import android.app.Application
import android.graphics.Bitmap
import android.os.SystemClock
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.SoftwareKeyboardController
import androidx.compose.ui.graphics.asAndroidBitmap
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
import java.io.File

/** Real routes and bundled lessons, with an isolated database and no personal-record resets. */
@RunWith(AndroidJUnit4::class)
class LearningFlowUiTest {
    @get:Rule val compose=createComposeRule()
    private lateinit var app:Application
    private lateinit var repo:StudyRepository
    private lateinit var vm:StudyViewModel
    private lateinit var restoration:StateRestorationTester
    private var keyboard:SoftwareKeyboardController?=null

    @Before fun setup() {
        app=ApplicationProvider.getApplicationContext()
        repo=StudyRepository(app,Room.inMemoryDatabaseBuilder(app,StudyDatabase::class.java).build(),false)
        compose.runOnUiThread{vm=StudyViewModel(app,repo)}
        restoration=StateRestorationTester(compose)
        restoration.setContent{keyboard=LocalSoftwareKeyboardController.current;SqlNoteApp(vm)}
        compose.waitUntil(30_000){vm.ready.value}
        compose.waitForIdle()
    }
    @After fun cleanup()=runBlocking {
        vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin()
        repo.db.close()
    }
    private fun state()=repo.state.value
    private fun progress(id:String)=CourseStudy.progress(state(),id)
    private fun homeButton(tag:String) {
        compose.onNode(hasTestTag("home-compact") or hasTestTag("home-wide"))
            .performScrollToNode(hasTestTag(tag))
        compose.onNodeWithTag(tag).performScrollTo().assertIsDisplayed().performClick()
    }
    private fun waitSection(id:String,section:String) {
        compose.waitUntil(10_000){state().lastLessonId==id&&progress(id).section==section}
        compose.onNodeWithTag("lesson-section-$section").assertIsSelected()
        compose.onNodeWithTag("lesson-next-step").assertIsDisplayed()
    }
    private fun screenshot(name:String) {
        compose.waitForIdle()
        // Capture the rendered app root after synchronization. A display screenshot can
        // still contain the previous activity frame when the Compose host first opens.
        val bitmap=compose.onRoot().captureToImage().asAndroidBitmap()
        File(app.cacheDir,"flow-$name.png").outputStream().use {
            assertTrue(bitmap.compress(Bitmap.CompressFormat.PNG,100,it))
        }
        bitmap.recycle()
    }
    private fun hideKeyboard(){compose.runOnIdle{keyboard?.hide()};compose.waitForIdle()}
    private fun storedState():StudyState=runBlocking {
        Codec.decodeFromString(repo.db.dao().state()!!.payload)
    }

    @Test fun freshHomeAndCurriculumLeadThroughFourStagesToTheNextLesson() {
        val first=repo.course.lessons.first()
        val second=repo.course.lessons[1]
        assertTrue(state().courseProgress.isEmpty())
        compose.onNode(hasTestTag("home-compact") or hasTestTag("home-wide"))
            .performScrollToNode(hasTestTag("home-course-resume"))
        compose.onNodeWithTag("home-course-resume").performScrollTo().assertIsDisplayed()
        screenshot("home")
        homeButton("home-course-list")
        compose.onNodeWithTag("course-list").assertExists()
        screenshot("curriculum")
        val firstRow=hasText("1강") and hasText(first.title) and hasClickAction()
        compose.onNodeWithTag("course-list").performScrollToNode(firstRow)
        compose.onNode(firstRow).performScrollTo().performClick()
        waitSection(first.id,"overview")
        compose.onNodeWithTag("lesson-position").assertIsDisplayed()
        compose.onNodeWithTag("lesson-next-step").assertTextContains("다음: 개념 읽기")
        assertEquals(0,progress(first.id).readVersion)
        screenshot("lesson-overview")
        compose.onNodeWithTag("lesson-next-step").performClick()
        waitSection(first.id,"concepts")
        assertEquals(0,progress(first.id).readVersion)
        compose.onNodeWithTag("lesson-next-step").assertTextContains("읽기 완료 · 예제 보기")
        screenshot("lesson-concepts")
        compose.onNodeWithTag("lesson-next-step").performClick()
        waitSection(first.id,"examples")
        val persisted=CourseStudy.progress(storedState(),first.id)
        assertEquals(first.version,persisted.readVersion)
        assertEquals("examples",persisted.section)
        assertTrue("Reading alone must not reveal any example",persisted.revealedResults.isEmpty())
        compose.onNodeWithTag("lesson-next-step").assertIsNotEnabled()
        screenshot("lesson-examples")
        first.examples.forEach{example->
            repeat(example.steps.size){step->
                compose.onNodeWithTag("course-example-next-${example.id}").performScrollTo().performClick()
                compose.waitUntil(10_000){progress(first.id).exampleSteps[example.id]==step+1}
            }
            compose.onNodeWithTag("course-result-${example.id}").performScrollTo().assertIsEnabled().performClick()
            compose.waitUntil(10_000){example.id in progress(first.id).revealedResults}
        }
        compose.onNodeWithTag("lesson-next-step").assertIsEnabled().performClick()
        waitSection(first.id,"checks")
        compose.onNodeWithTag("lesson-next-step").assertIsNotEnabled()
        screenshot("lesson-checks")
        first.selfChecks.forEachIndexed{index,check->
            compose.onNodeWithTag("course-reveal-${check.id}").performScrollTo().performClick()
            val rating=if(index==0)"review"else"understood"
            compose.onNodeWithTag("course-rating-$rating-${check.id}").performScrollTo().performClick()
            compose.waitUntil(10_000){progress(first.id).checks.any{it.checkId==check.id&&it.rating==rating}}
            if(index<first.selfChecks.lastIndex)compose.onNodeWithTag("lesson-next-step").assertIsNotEnabled()
        }
        val completed=progress(first.id)
        assertTrue("A request to review is a valid self-check choice",completed.checks.any{it.rating=="review"})
        compose.onNodeWithTag("lesson-next-step").assertIsEnabled().performClick()
        waitSection(second.id,"overview")
        screenshot("lesson-next")
        assertEquals(completed.copy(scroll=progress(first.id).scroll,updatedAt=progress(first.id).updatedAt),progress(first.id))
        assertEquals(0,progress(second.id).readVersion)
        assertTrue(state().submissions.isEmpty())
        assertTrue(state().sessions.isEmpty())
        assertNull(vm.error.value)
    }

    @Test fun restoredReaderKeepsDraftsRatingsExamplesAndIndependentScoredRecords() {
        val lesson=repo.course.lessons.first()
        val firstCheck=lesson.selfChecks.first()
        val pendingCheck=lesson.selfChecks[1]
        val q=repo.pack.practice().first()
        val note=repo.pack.notes.first()
        val block=note.blocks.first()
        val now=System.currentTimeMillis()
        runBlocking{repo.update{original->
            val started=StudyEngine.createSession(original,repo.pack,listOf(q),"immediate","보존할 완료 연습",now,SystemClock.elapsedRealtime(),0,13)
            val sessionId=started.activeSessionId!!
            val selected=StudyEngine.select(started,sessionId,0,q.correctChoiceIds.single())
            StudyEngine.submit(selected,sessionId,now).copy(
                bookmarks=listOf(Bookmark(q.id,now)),
                annotations=listOf(Annotation("flow-kept-note",note.id,block.id,block.text.take(100),"유지할 개인 필기","memo",now)),
                notes=listOf(NoteProgress(note.id,read=true,scroll=17,readVersion=note.version)),
                courseProgress=listOf(CourseProgress(lesson.id,readVersion=lesson.version,section="checks",
                    exampleSteps=lesson.examples.associate{it.id to it.steps.size},
                    revealedResults=lesson.examples.map{it.id},
                    checks=listOf(CourseCheckProgress(firstCheck.id,"먼저 작성한 답안",true,"review")))),
                lastLessonId=lesson.id)
        }}
        val kept=state()
        homeButton("home-course-resume")
        waitSection(lesson.id,"checks")
        compose.onNodeWithTag("course-draft-${pendingCheck.id}").performScrollTo().performTextInput("복원할 작성 중 답안")
        hideKeyboard()
        compose.waitUntil(10_000){progress(lesson.id).checks.any{it.checkId==pendingCheck.id&&it.draft=="복원할 작성 중 답안"}}
        val before=progress(lesson.id)
        restoration.emulateSavedInstanceStateRestore()
        waitSection(lesson.id,"checks")
        compose.onNodeWithTag("course-draft-${pendingCheck.id}").performScrollTo().assertTextContains("복원할 작성 중 답안")
        compose.onNodeWithTag("course-rating-review-${firstCheck.id}").performScrollTo().assertIsSelected()
        compose.onNodeWithTag("lesson-next-step").assertIsNotEnabled()
        screenshot("lesson-restored")
        val after=progress(lesson.id)
        assertEquals(before.checks,after.checks)
        assertEquals(before.exampleSteps,after.exampleSteps)
        assertEquals(before.revealedResults,after.revealedResults)
        assertEquals(before.readVersion,after.readVersion)
        assertEquals(kept.submissions,state().submissions)
        assertEquals(kept.sessions,state().sessions)
        assertEquals(kept.reviews,state().reviews)
        assertEquals(kept.notes,state().notes)
        assertEquals(kept.annotations,state().annotations)
        assertEquals(kept.bookmarks,state().bookmarks)
        val stored=storedState()
        val saved=CourseStudy.progress(stored,lesson.id)
        assertEquals(after.checks,saved.checks)
        assertEquals(after.exampleSteps,saved.exampleSteps)
        assertEquals(after.revealedResults,saved.revealedResults)
        assertEquals(after.readVersion,saved.readVersion)
        assertEquals("checks",saved.section)
        val roundTrip=BackupCodec.decode(BackupCodec.encode(stored))
        assertEquals(stored.courseProgress,roundTrip.courseProgress)
        assertEquals(stored.submissions,roundTrip.submissions)
        assertNull(vm.error.value)
    }

    @Test fun foldedToolsRemainReachableWithoutMarkingProgressOrStartingQuestions() {
        val before=state()
        compose.openHomeTools()
        compose.onNode(hasTestTag("home-compact") or hasTestTag("home-wide"))
            .performScrollToNode(hasTestTag("home-study-plan"))
        compose.onNodeWithTag("home-study-plan").assertExists()
        compose.onNode(hasTestTag("home-compact") or hasTestTag("home-wide"))
            .performScrollToNode(hasText("노트 펼치기") and hasClickAction())
        compose.onNode(hasText("노트 펼치기") and hasClickAction()).assertExists()
        assertEquals(before,state())
        compose.onNode(hasTestTag("home-compact") or hasTestTag("home-wide"))
            .performScrollToNode(hasTestTag("home-tools-toggle"))
        compose.onNodeWithTag("home-tools-toggle").performScrollTo().performClick()
        compose.onNodeWithTag("home-tools-toggle")
            .assert(SemanticsMatcher.expectValue(SemanticsProperties.StateDescription,"접힘"))
        compose.onNodeWithTag("home-study-plan").assertDoesNotExist()
        homeButton("home-course-resume")
        val lesson=repo.course.lessons.first()
        waitSection(lesson.id,"overview")
        compose.onNodeWithTag("lesson-read-toggle").assertDoesNotExist()
        compose.openLessonTools()
        compose.onNodeWithTag("lesson-read-toggle").performScrollTo().assertExists()
        compose.onNodeWithTag("course-practice").performScrollTo().assertExists()
        compose.onNodeWithTag("lesson-tools-toggle").performScrollTo().performClick()
        compose.onNodeWithTag("lesson-read-toggle").assertDoesNotExist()
        assertEquals(0,progress(lesson.id).readVersion)
        assertTrue(progress(lesson.id).checks.isEmpty())
        assertEquals(before.submissions,state().submissions)
        assertEquals(before.sessions,state().sessions)
        assertNull(vm.error.value)
    }

    @Test fun largeTextKeepsCurrentPositionAndNextActionInsideTheReader() {
        val systemScale=app.resources.configuration.fontScale
        val appScale=(2f/systemScale).coerceIn(0.8f,2f)
        runBlocking{repo.update{it.copy(settings=it.settings.copy(textScale=appScale))}}
        homeButton("home-course-resume")
        waitSection(repo.course.lessons.first().id,"overview")
        compose.onNodeWithTag("lesson-position").assertIsDisplayed()
        val reader=compose.onNodeWithTag("lesson-reader").getUnclippedBoundsInRoot()
        val action=compose.onNodeWithTag("lesson-next-step").getUnclippedBoundsInRoot()
        assertTrue("Next action must fit vertically",action.top>=reader.top&&action.bottom<=reader.bottom)
        assertTrue("Next action must fit horizontally",action.left>=reader.left&&action.right<=reader.right)
        screenshot("lesson-large-text")
    }
}
