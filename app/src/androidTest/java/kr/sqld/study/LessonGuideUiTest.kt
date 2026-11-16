package kr.sqld.study

import android.app.Application
import android.graphics.Bitmap
import androidx.compose.ui.semantics.SemanticsProperties
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
import org.junit.*
import org.junit.Assert.*
import org.junit.runner.RunWith
import java.io.File

@RunWith(AndroidJUnit4::class)
class LessonGuideUiTest {
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
        compose.waitUntil(20000){vm.ready.value}
    }
    @After fun cleanup()=runBlocking{vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin();repo.db.close()}
    private fun open(lid:String){
        runBlocking{repo.update{CourseStudy.update(it,lid,{it})}}
        compose.onNode(hasTestTag("home-compact") or hasTestTag("home-wide")).performScrollToNode(hasTestTag("home-course-resume"))
        compose.onNodeWithTag("home-course-resume").performScrollTo().performClick()
        compose.openLessonTools()
        compose.waitUntil(10000){compose.onAllNodesWithTag("lesson-guide-open").fetchSemanticsNodes().isNotEmpty()}
        compose.onNodeWithTag("lesson-guide-open").performScrollTo().performClick()
        compose.onNodeWithTag("lesson-guide-dialog").assertIsDisplayed()
    }
    private fun select(id:String){
        compose.onNodeWithTag("guide-tab-read").performScrollTo().performClick()
        compose.onNodeWithTag("guide-example-picker").performClick()
        compose.onNodeWithTag("guide-pick-$id").performScrollTo().performClick()
    }
    private fun title()=compose.onNodeWithTag("walk-step-title").fetchSemanticsNode().config[SemanticsProperties.Text].single().text
    private fun advance(count:Int){repeat(count){compose.onNodeWithTag("walk-next").performClick()}}
    private fun capture(name:String){
        compose.waitForIdle()
        val bitmap=InstrumentationRegistry.getInstrumentation().uiAutomation.takeScreenshot()?:error("No screenshot")
        File(app.cacheDir,name).outputStream().use{assertTrue(bitmap.compress(Bitmap.CompressFormat.PNG,100,it))};bitmap.recycle()
    }
    @Test fun foreignKeyOwnershipNextPreviousAndRotationPreserveStage(){
        open("2-1-03");select("supplemental-2-1-03-fk");advance(4)
        assertEquals("왼쪽 사원 열이 오른쪽 부서 키를 참조",title())
        capture("guide-pilot-fk.png")
        val before=title()
        compose.onNodeWithTag("walk-previous").performClick();compose.onNodeWithTag("walk-next").performClick();assertEquals(before,title())
        compose.onNodeWithTag("walk-foundations-toggle").performScrollTo().performClick()
        compose.onNodeWithTag("guide-tab-words").performScrollTo().performClick()
        compose.onNodeWithTag("guide-tab-read").performScrollTo().performClick();assertEquals(before,title())
        restoration.emulateSavedInstanceStateRestore()
        compose.waitUntil(10000){compose.onAllNodesWithTag("walk-step-title").fetchSemanticsNodes().isNotEmpty()}
        assertEquals(before,title())
        compose.onNodeWithTag("walk-foundations").assertExists()
        assertEquals(4,CourseStudy.progress(repo.state.value,"2-1-03").exampleSteps["guide:supplemental-2-1-03-fk"])
        assertTrue(repo.state.value.submissions.isEmpty())
        assertTrue(CourseStudy.progress(repo.state.value,"2-1-03").revealedResults.isEmpty())
    }
    @Test fun insertUsesNamedColumnOrderAndDoesNotRewriteOriginalProgress(){
        open("2-1-05");select("supplemental-2-1-05-order");advance(2)
        assertEquals("명시한 위치로 값을 연결",title())
        capture("guide-pilot-insert.png")
        val lesson=repo.course.lessons.single{it.id=="2-1-05"}
        val progress=CourseStudy.progress(repo.state.value,lesson.id)
        assertTrue(lesson.examples.none{it.id in progress.exampleSteps})
        assertEquals(0,progress.readVersion);assertTrue(progress.checks.isEmpty())
    }
    @Test fun mergeShowsAssignmentDirectionAndBothTables(){
        open("2-1-10");select("2-1-10-E01");advance(3)
        assertTrue(title().contains("오른쪽"))
        compose.onNodeWithTag("ink-code-surface").assertIsDisplayed()
        val codeBounds=compose.onNodeWithTag("ink-code-surface").fetchSemanticsNode().boundsInRoot
        val firstLine=(32f+6f)*app.resources.configuration.fontScale*app.resources.displayMetrics.density
        assertTrue("SQL canvas must retain a readable line",codeBounds.height+0.5f>=firstLine)
        compose.onNodeWithTag("walk-narrative").assertIsDisplayed()
        capture("guide-pilot-merge.png")
        advance(3);assertTrue(title().contains("최종 대상"))
        compose.onNodeWithTag("walk-previous").performClick();assertTrue(title().contains("유지"))
    }
    @Test fun checkReasoningIsHiddenUntilOriginalAnswerIsRevealed(){
        open("2-1-03");compose.onNodeWithTag("guide-close").performClick()
        compose.onNodeWithTag("lesson-section-checks").performClick()
        compose.onNodeWithTag("guide-check-answer-2-1-03-Q1").assertDoesNotExist()
        compose.onNodeWithTag("guide-hint-2-1-03-Q1").performScrollTo().performClick()
        compose.onNodeWithTag("guide-check-answer-2-1-03-Q1").assertDoesNotExist()
        compose.onNodeWithTag("course-reveal-2-1-03-Q1").performScrollTo().performClick()
        compose.onNodeWithTag("guide-check-answer-2-1-03-Q1").performScrollTo().assertIsDisplayed()
        assertTrue(repo.state.value.submissions.isEmpty())
    }
    @Test fun catalogRejectsChangedLessonAndReadsOnlyRequestedDocuments()=runBlocking {
        val catalog=LessonGuideCatalog(app)
        assertEquals(0,catalog.materialReads)
        val lesson=repo.course.lessons.single{it.id=="2-1-10"}
        val guide=catalog.lesson(lesson);assertNotNull(guide);assertEquals(1,catalog.materialReads)
        assertNull(catalog.lesson(lesson.copy(examples=lesson.examples.map{it.copy(sql=it.sql+" -- changed")})))
        assertEquals(1,catalog.materialReads)
        assertNotNull(catalog.lesson(lesson));assertEquals(1,catalog.materialReads)
    }
    @Test fun modelingGuideRetainsExistingPictureAndOriginalQuery(){
        open("1-1-01")
        val visual=repo.courseVisuals.forLesson("1-1-01").first()
        compose.onNode(hasTestTag("visual-open-${visual.id}") and hasAnyAncestor(hasTestTag("lesson-guide-dialog"))).performScrollTo().performClick()
        compose.waitUntil(10000){compose.onAllNodesWithTag("visual-image").fetchSemanticsNodes().isNotEmpty()}
        capture("guide-final-modeling-image.png")
        compose.onNodeWithTag("visual-close").performClick()
        compose.onNodeWithTag("guide-tab-read").performScrollTo().performClick()
        compose.onNodeWithTag("ink-code-surface").assertIsDisplayed()
        compose.onNodeWithTag("walk-next").performClick()
        compose.onNodeWithTag("walk-step-title").assertIsDisplayed()
        capture("guide-final-modeling-query.png")
    }
    @Test fun conceptualExampleDoesNotInventSqlAndKeepsOriginalTablesAccessible(){
        open("1-1-02")
        compose.onNodeWithTag("guide-tab-read").performScrollTo().performClick()
        compose.onNodeWithTag("ink-code-surface").assertDoesNotExist()
        compose.onNodeWithTag("walk-next").performClick()
        compose.onNodeWithTag("walk-step-title").assertIsDisplayed()
        if(compose.onAllNodesWithTag("guide-concept-original").fetchSemanticsNodes().isNotEmpty())
            compose.onNodeWithTag("guide-concept-original").performScrollTo().performClick()
        capture("guide-final-modeling-concept.png")
    }
}
