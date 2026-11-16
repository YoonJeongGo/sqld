package kr.sqld.study

import android.app.Application
import android.graphics.BitmapFactory
import android.os.SystemClock
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.SoftwareKeyboardController
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
import kotlin.math.abs

/** Native course flow, using bundled assets and an isolated DB on both phone and tablet. */
@RunWith(AndroidJUnit4::class)
class CourseVisualUiTest {
    @get:Rule val compose=createComposeRule()
    private lateinit var repo:StudyRepository
    private lateinit var vm:StudyViewModel
    private lateinit var restoration:StateRestorationTester
    private var keyboard:SoftwareKeyboardController?=null

    @Before fun setup(){
        val app=ApplicationProvider.getApplicationContext<Application>()
        repo=StudyRepository(app,Room.inMemoryDatabaseBuilder(app,StudyDatabase::class.java).build(),false)
        compose.runOnUiThread { vm=StudyViewModel(app,repo) }
        restoration=StateRestorationTester(compose)
        restoration.setContent { keyboard=LocalSoftwareKeyboardController.current;SqlNoteApp(vm) }
        compose.waitUntil(20000){vm.ready.value}
        compose.waitForIdle()
    }

    @After fun cleanup()=runBlocking<Unit> {
        if(::vm.isInitialized)vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin()
        if(::repo.isInitialized)repo.db.close()
    }

    private fun state()=repo.state.value
    private fun progress(id:String)=CourseStudy.progress(state(),id)
    private fun homeButton(tag:String){
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasTestTag(tag))
        compose.onNodeWithTag(tag).performScrollTo().assertIsDisplayed().performClick()
    }
    private fun openLesson(id:String){
        runBlocking { repo.update { it.copy(lastLessonId=id) } }
        compose.waitForIdle()
        homeButton("home-course-resume")
        compose.waitUntil(10000){compose.onAllNodesWithTag("lesson-reader").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithTag("lesson-section-overview").assertIsSelected()
    }
    private fun openVisual(id:String){
        compose.onNodeWithTag("visual-card-$id").assertExists()
        compose.onNodeWithTag("visual-open-$id").performScrollTo().assertIsDisplayed().performClick()
        waitForImage()
    }
    private fun waitForImage(){
        // Compose idleness alone does not wait for the IO bitmap decoder.
        compose.waitUntil(20000){compose.onAllNodesWithTag("visual-image",useUnmergedTree=true).fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithTag("visual-image",useUnmergedTree=true).assertIsDisplayed()
    }
    private fun viewerState():Triple<Int,Int,Int> {
        val description=compose.onNodeWithTag("visual-viewport").fetchSemanticsNode().config[SemanticsProperties.StateDescription]
        val values=Regex("-?\\d+").findAll(description).map{it.value.toInt()}.toList()
        assertEquals("Viewport exposes zoom and both pan coordinates: $description",3,values.size)
        return Triple(values[0],values[1],values[2])
    }
    private fun clickViewer(tag:String){
        compose.onNodeWithTag(tag).assertIsDisplayed().assertIsEnabled().performClick()
        compose.waitForIdle()
    }
    private fun assertScoredAndNoteRecordsUnchanged(before:StudyState){
        assertEquals(before.sessions,state().sessions)
        assertEquals(before.submissions,state().submissions)
        assertEquals(before.reviews,state().reviews)
        assertEquals(before.exposures,state().exposures)
        assertEquals(before.bookmarks,state().bookmarks)
        assertEquals(before.noteBookmarks,state().noteBookmarks)
        assertEquals(before.annotations,state().annotations)
        assertEquals(before.notes,state().notes)
        assertEquals(before.issues,state().issues)
        assertEquals(before.settings,state().settings)
        assertNull(vm.error.value)
    }

    @Test fun allTwentySevenPackagedImagesDecodeOnAndroidAtTheirDeclaredOriginalSize(){
        val app=ApplicationProvider.getApplicationContext<Application>()
        val visuals=repo.courseVisuals.visuals
        assertEquals((1..27).toSet(),visuals.map{it.number}.toSet())
        assertEquals(27,visuals.size)
        val expectedPaths=(1..27).map{"course-visuals/visual-${it.toString().padStart(2,'0')}.png"}.toSet()
        assertEquals(expectedPaths,visuals.map{it.pngAsset}.toSet())
        assertEquals(expectedPaths,app.assets.list("course-visuals").orEmpty().filter{it.endsWith(".png")}.map{"course-visuals/$it"}.toSet())
        visuals.forEach { visual ->
            val bitmap=app.assets.open(visual.pngAsset).use { stream ->
                BitmapFactory.decodeStream(stream,null,BitmapFactory.Options().apply{inScaled=false})
            } ?: throw AssertionError("Android could not decode ${visual.pngAsset}")
            try {
                assertEquals("${visual.id} original width",visual.width,bitmap.width)
                assertEquals("${visual.id} original height",visual.height,bitmap.height)
                assertEquals("${visual.id} must preserve 8:5",bitmap.width*5,bitmap.height*8)
                assertTrue("${visual.id} must decode pixel storage",bitmap.byteCount>0)
            } finally { bitmap.recycle() }
            // The companion SVG is retained even though the native viewer displays PNG.
            app.assets.open(visual.svgAsset).use { assertTrue("Missing SVG ${visual.id}",it.read()!=-1) }
        }
        assertTrue(state().submissions.isEmpty())
        assertNull(vm.error.value)
    }

    @Test fun allThreePilotLessonsKeepOriginalExampleStepsAndResultsSeparateFromPictures(){
        val before=state()
        listOf("2-1-04" to "visual-11","2-1-23" to "visual-14","2-1-20" to "visual-18").forEach { (lessonId,visualId) ->
            val lesson=repo.course.lessons.single{it.id==lessonId}
            assertTrue(repo.courseVisuals.forLesson(lessonId).any{it.id==visualId})
            openLesson(lessonId)
            val thumbnail=compose.onNodeWithTag("visual-thumbnail-$visualId")
            thumbnail.performScrollTo().assertIsDisplayed()
            // A full-width tablet picture can be taller than the scroll viewport.
            val size=thumbnail.fetchSemanticsNode().size
            assertEquals("The full thumbnail keeps its 8:5 ratio",1.6f,size.width.toFloat()/size.height,0.02f)
            openVisual(visualId)
            val fitted=viewerState().first
            clickViewer("visual-native")
            assertEquals("Original size is one source pixel per screen pixel",100,viewerState().first)
            clickViewer("visual-zoom-in")
            assertTrue(viewerState().first>100)
            clickViewer("visual-zoom-out")
            assertEquals(100,viewerState().first)
            clickViewer("visual-fit")
            assertEquals(Triple(fitted,0,0),viewerState())
            compose.onNodeWithTag("visual-zoom-out").assertIsNotEnabled()
            clickViewer("visual-close")
            compose.onNodeWithTag("visual-viewport").assertDoesNotExist()
            assertTrue("Viewing a picture does not complete an example",progress(lessonId).revealedResults.isEmpty())

            compose.openLessonTools()
            compose.onNodeWithTag("visual-to-examples").performScrollTo().assertIsDisplayed().performClick()
            compose.onNodeWithTag("lesson-section-examples").assertIsSelected()
            compose.onNodeWithText("앞에서 본 그림과 다른 데이터로 연습해요.",substring=true).assertExists()
            val example=lesson.examples.first()
            val result=compose.onNodeWithTag("course-result-${example.id}")
            result.performScrollTo().assertIsNotEnabled()
            example.steps.indices.forEach { index ->
                compose.onNodeWithTag("course-example-next-${example.id}").performScrollTo().performClick()
                compose.waitUntil(10000){progress(lessonId).exampleSteps[example.id]==index+1}
                if(index<example.steps.lastIndex)result.assertIsNotEnabled()
            }
            result.performScrollTo().assertIsEnabled().performClick()
            compose.waitUntil(10000){example.id in progress(lessonId).revealedResults}
            compose.onNodeWithTag("course-result-${example.id}").assertDoesNotExist()
            assertScoredAndNoteRecordsUnchanged(before)
            compose.onNodeWithContentDescription("뒤로").performClick()
        }
    }

    @Test fun textInsidePictureFindsTheLessonAndSearchSurvivesReturning(){
        val query="학년 NUMBER(1)"
        val lesson=repo.course.lessons.single{it.id=="2-1-04"}
        // This phrase is in the additional picture, not the existing searched course fields.
        assertFalse((listOf(lesson.title,lesson.id,lesson.easy,lesson.memory)+lesson.concepts.flatMap{listOf(it.term,it.meaning)}).any{it.contains(query)})
        assertTrue(repo.courseVisuals.searchText(lesson.id).any{it.contains(query)})
        homeButton("home-course-list")
        compose.onNodeWithTag("course-list").performScrollToNode(hasSetTextAction())
        compose.onNode(hasSetTextAction()).performScrollTo().performTextInput(query)
        compose.runOnIdle { keyboard?.hide() }
        compose.waitForIdle()
        compose.onNodeWithTag("course-list").performScrollToNode(hasText(lesson.title))
        compose.onNodeWithText(lesson.title).performClick()
        compose.waitUntil(10000){compose.onAllNodesWithTag("lesson-reader").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithTag("visual-card-visual-11").assertExists()
        compose.onNodeWithContentDescription("뒤로").performClick()
        compose.onNodeWithTag("course-list").performScrollToNode(hasSetTextAction())
        compose.onNode(hasSetTextAction()).assertTextContains(query)
        assertTrue(state().submissions.isEmpty())
        assertNull(vm.error.value)
    }

    @Test fun comparisonExplanationDoesNotRevealAnswersBeforeAllOriginalExamplesAreOpened(){
        val lesson=repo.course.lessons.single{it.id=="2-1-23"}
        val guide=repo.courseVisuals.guide(lesson.id)!!
        assertTrue("Use a multi-example lesson to check the final reveal gate",lesson.examples.size>1)
        assertTrue(guide.exampleReadingGuide.isNotBlank())
        val comparisonTag="course-example-comparison-${lesson.id}"
        openLesson(lesson.id)
        compose.onNodeWithTag("lesson-section-examples").performClick()
        // The neutral transition notice stays visible, but computed answers stay hidden.
        compose.onNodeWithText("앞에서 본 그림과 다른 데이터로 연습해요.",substring=true).assertExists()
        compose.onNodeWithTag(comparisonTag).assertDoesNotExist()
        compose.onNodeWithText(guide.exampleReadingGuide).assertDoesNotExist()

        lesson.examples.forEachIndexed { exampleIndex,example ->
            val result=compose.onNodeWithTag("course-result-${example.id}")
            result.performScrollTo().assertIsNotEnabled()
            example.steps.indices.forEach { stepIndex ->
                compose.onNodeWithTag("course-example-next-${example.id}").performScrollTo().performClick()
                compose.waitUntil(10000){progress(lesson.id).exampleSteps[example.id]==stepIndex+1}
            }
            // Revealing every step alone must not unlock the cross-example answer summary.
            compose.onNodeWithTag(comparisonTag).assertDoesNotExist()
            result.performScrollTo().assertIsEnabled().performClick()
            compose.waitUntil(10000){example.id in progress(lesson.id).revealedResults}
            if(exampleIndex<lesson.examples.lastIndex){
                compose.onNodeWithTag(comparisonTag).assertDoesNotExist()
                compose.onNodeWithText(guide.exampleReadingGuide).assertDoesNotExist()
            }
        }
        compose.onNodeWithTag(comparisonTag).performScrollTo().assertIsDisplayed()
        compose.onNodeWithText("그림과 예제 비교 해설").assertExists()
        compose.onNodeWithText(guide.exampleReadingGuide).assertExists()
        assertTrue(state().submissions.isEmpty())
        assertNull(vm.error.value)
    }

    @Test fun panningAndRestoringViewerKeepsStoredAnswersNotesAndUnrelatedCourseProgress(){
        val lesson=repo.course.lessons.single{it.id=="2-1-04"}
        val other=repo.course.lessons.first()
        val check=lesson.selfChecks.first()
        val question=repo.pack.practice().first()
        val note=repo.pack.notes.first()
        val now=System.currentTimeMillis()
        val draft="학년 항목을 추가해도 박보성과 이승현의 정보 두 줄은 남는다."
        val before=runBlocking { repo.update { initial ->
            val created=StudyEngine.createSession(initial,repo.pack,listOf(question),"batch","그림 열람 기록 보존",now,SystemClock.elapsedRealtime(),0,47)
            val sessionId=created.activeSessionId!!
            val wrongChoice=question.choices.first{it.id !in question.correctChoiceIds}.id
            val selected=StudyEngine.select(created,sessionId,0,wrongChoice)
            StudyEngine.submit(selected,sessionId,now+1).copy(
                activeSessionId=null,
                bookmarks=listOf(Bookmark(question.id,now)),
                noteBookmarks=listOf(Bookmark(note.id,now)),
                annotations=listOf(Annotation("visual-test-memo",note.id,note.blocks.first().id,note.blocks.first().text.take(30),"그림을 보기 전 남긴 메모","memo",now)),
                notes=listOf(NoteProgress(note.id,read=true,scroll=150,readVersion=note.version)),
                courseProgress=listOf(
                    CourseProgress(lesson.id,readVersion=lesson.version,exampleSteps=mapOf(lesson.examples.first().id to 1),checks=listOf(CourseCheckProgress(check.id,draft,true,"review")),updatedAt=now),
                    CourseProgress(other.id,readVersion=other.version,scroll=144,section="concepts",updatedAt=now)
                ),lastLessonId=lesson.id
            )
        } }
        assertTrue(before.submissions.isNotEmpty()&&before.reviews.isNotEmpty()&&before.annotations.isNotEmpty())
        openLesson(lesson.id)
        openVisual("visual-11")
        clickViewer("visual-native")
        clickViewer("visual-zoom-in")
        assertEquals(150,viewerState().first)
        compose.onNodeWithTag("visual-viewport").performTouchInput { swipeLeft() }
        compose.waitForIdle()
        val panned=viewerState()
        assertTrue("An enlarged image must actually pan",abs(panned.second)>0)
        assertEquals(150,panned.first)

        restoration.emulateSavedInstanceStateRestore()
        waitForImage()
        compose.waitForIdle()
        assertEquals("Selected picture remains enlarged after saved-state restoration",panned,viewerState())
        clickViewer("visual-close")
        compose.onNodeWithTag("visual-viewport").assertDoesNotExist()
        restoration.emulateSavedInstanceStateRestore()
        compose.waitForIdle()
        compose.onNodeWithTag("visual-viewport").assertDoesNotExist()
        compose.onNodeWithTag("lesson-section-overview").assertIsSelected()
        compose.onNodeWithTag("lesson-section-checks").performClick()
        compose.onNodeWithTag("course-draft-${check.id}").performScrollTo().assertTextContains(draft)
        compose.onNodeWithTag("course-rating-review-${check.id}",useUnmergedTree=true).performScrollTo().assertIsSelected()

        val saved=before.courseProgress.single{it.lessonId==lesson.id}
        assertEquals(saved.readVersion,progress(lesson.id).readVersion)
        assertEquals(saved.checks,progress(lesson.id).checks)
        assertEquals(saved.exampleSteps,progress(lesson.id).exampleSteps)
        assertEquals(saved.revealedResults,progress(lesson.id).revealedResults)
        assertEquals(before.courseProgress.single{it.lessonId==other.id},progress(other.id))
        assertScoredAndNoteRecordsUnchanged(before)
    }
}
