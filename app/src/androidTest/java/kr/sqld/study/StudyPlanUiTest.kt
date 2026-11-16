package kr.sqld.study

import android.app.Application
import android.os.SystemClock
import android.provider.Settings
import androidx.compose.ui.semantics.SemanticsProperties
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
import java.time.LocalDate

/** Uses the app routes with isolated records; no real learner database is touched. */
@RunWith(AndroidJUnit4::class)
class StudyPlanUiTest {
    @get:Rule val compose=createComposeRule()
    private lateinit var app:Application
    private lateinit var repo:StudyRepository
    private lateinit var vm:StudyViewModel
    @Before fun setup(){
        app=ApplicationProvider.getApplicationContext()
        repo=StudyRepository(app,Room.inMemoryDatabaseBuilder(app,StudyDatabase::class.java).build(),false)
        compose.runOnUiThread{vm=StudyViewModel(app,repo)}
        compose.setContent{SqlNoteApp(vm)}
        compose.waitUntil(20000){vm.ready.value}
        compose.waitForIdle()
    }
    @After fun cleanup()=runBlocking{vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin();repo.db.close()}
    private fun openPlan(){
        compose.openHomeTools()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasTestTag("home-study-plan"))
        compose.onNodeWithTag("home-study-plan").performScrollTo().performClick()
        compose.waitForIdle()
    }
    private fun planTarget(matcher:SemanticsMatcher):SemanticsNodeInteraction {
        compose.onNodeWithTag("study-plan-list").performScrollToNode(matcher)
        return compose.onNode(matcher).performScrollTo()
    }
    private fun planNode(tag:String)=planTarget(hasTestTag(tag))
    private fun selectDate(date:String){
        planNode("plan-date-picker").performClick()
        compose.onNodeWithTag("plan-date-list").performScrollToNode(hasTestTag("plan-date-$date"))
        compose.onNodeWithTag("plan-date-$date").performClick()
    }
    @Test fun dateAndBudgetSurviveNavigationAndHolidayDoesNotAddRecords(){
        val before=repo.state.value
        openPlan()
        selectDate("2026-10-05")
        planTarget(hasText("6시간 확장")).performClick()
        planNode("plan-time-budget").assertTextEquals("6시간 시간 배분")
        selectDate("2026-10-08")
        planNode("plan-rest-day").assertIsDisplayed()
        compose.onNodeWithContentDescription("뒤로").performClick()
        openPlan()
        planNode("plan-date-picker").assertTextContains("10/8 (목)",substring=true)
        planTarget(hasText("6시간 확장")).assertIsSelected()
        assertEquals(before,repo.state.value)
    }
    @Test fun foldingSectionsAndLessonRoundTripPreserveSelectionAndExistingRecords(){
        val plan=app.assets.open("study-plan.json").bufferedReader().use{Codec.decodeFromString<StudyPlan>(it.readText())}.validate(repo.course)
        val savedLesson=repo.course.lessons.first()
        val day=plan.studyDays.first{it.date!=plan.startDate&&it.lectures.isNotEmpty()&&it.pdfs.isNotEmpty()&&it.lessonIds.any{id->id!=savedLesson.id}}
        val targetLesson=day.lessonIds.first{it!=savedLesson.id}
        val question=repo.pack.practice().first()
        val note=repo.pack.notes.first{it.blocks.isNotEmpty()}
        val block=note.blocks.first()
        val now=System.currentTimeMillis()
        runBlocking{repo.update{initial->
            val started=StudyEngine.createSession(initial,repo.pack,listOf(question),"immediate","보존 확인용 완료 연습",now,SystemClock.elapsedRealtime(),0,7)
            val sessionId=started.activeSessionId!!
            val selected=StudyEngine.select(started,sessionId,0,question.correctChoiceIds.single())
            StudyEngine.submit(selected,sessionId,now).copy(
                bookmarks=listOf(Bookmark(question.id,now)),
                annotations=listOf(Annotation("plan-preserved-memo",note.id,block.id,block.text.take(100),"보존할 메모","memo",now)),
                courseProgress=listOf(CourseProgress(savedLesson.id,readVersion=savedLesson.version,
                    checks=listOf(CourseCheckProgress(savedLesson.selfChecks.first().id,"보존할 자기점검",true,"review")),updatedAt=now)),
                lastLessonId=savedLesson.id
            )
        }}
        compose.waitForIdle()
        val before=repo.state.value
        openPlan();selectDate(day.date)
        planTarget(hasText("6시간 확장")).performClick()
        val sections=listOf(
            "plan-block-details-toggle" to "plan-block-details",
            "plan-lectures-toggle" to "plan-lecture-list",
            "plan-pdfs-toggle" to "plan-pdf-list"
        )
        sections.forEach{(toggle,content)->
            planNode(toggle).assert(SemanticsMatcher.expectValue(SemanticsProperties.StateDescription,"접힘")).performClick()
            planNode(content).assertIsDisplayed()
            planNode(toggle).assert(SemanticsMatcher.expectValue(SemanticsProperties.StateDescription,"펼쳐짐")).performClick()
            compose.onNodeWithTag(content).assertDoesNotExist()
            planNode(toggle).assert(SemanticsMatcher.expectValue(SemanticsProperties.StateDescription,"접힘")).performClick()
            planNode(content).assertIsDisplayed()
            assertEquals(before,repo.state.value)
        }
        val date=LocalDate.parse(day.date)
        fun assertSelection(){
            planNode("plan-date-picker").assertTextContains("${date.monthValue}/${date.dayOfMonth} (",substring=true)
            planTarget(hasText("6시간 확장")).assertIsSelected()
            planNode("plan-time-budget").assertTextEquals("6시간 시간 배분")
        }
        assertSelection()
        planNode("plan-lesson-$targetLesson").performClick()
        compose.waitUntil(10000){compose.onAllNodesWithTag("lesson-reader").fetchSemanticsNodes().isNotEmpty()}
        assertEquals(targetLesson,repo.state.value.lastLessonId)
        compose.onNodeWithContentDescription("뒤로").performClick()
        assertSelection()
        sections.forEach{(toggle,content)->
            planNode(toggle).assert(SemanticsMatcher.expectValue(SemanticsProperties.StateDescription,"펼쳐짐"))
            planNode(content).assertIsDisplayed()
        }
        val after=repo.state.value
        assertEquals(before.courseProgress.single(),after.courseProgress.single{it.lessonId==savedLesson.id})
        assertEquals(setOf(savedLesson.id,targetLesson),after.courseProgress.map{it.lessonId}.toSet())
        val visited=after.courseProgress.single{it.lessonId==targetLesson}
        assertEquals(CourseProgress(targetLesson,scroll=visited.scroll,updatedAt=visited.updatedAt),visited)
        // Opening a reader records its position; it must not mark it read or alter any old record.
        assertEquals(before,after.copy(revision=before.revision,lastLessonId=before.lastLessonId,courseProgress=before.courseProgress))
    }
    @Test fun planPracticeUsesLinkedGeneralQuestionsAndLessonLinkOpensExistingReader(){
        val plan=app.assets.open("study-plan.json").bufferedReader().use{Codec.decodeFromString<StudyPlan>(it.readText())}.validate(repo.course)
        val day=plan.studyDays.first{PlanReview.questions(it,repo.course,repo.pack,repo.state.value).isNotEmpty()}
        val expected=PlanReview.questions(day,repo.course,repo.pack,repo.state.value).map{it.id}.toSet()
        openPlan();selectDate(day.date)
        planNode("plan-practice").performClick()
        compose.onNodeWithText("연습 시작").assertIsDisplayed()
        compose.onNodeWithText("취소").performClick()
        val lesson=day.lessonIds.first()
        planNode("plan-lesson-$lesson").performClick()
        compose.waitUntil(10000){compose.onAllNodesWithTag("lesson-reader").fetchSemanticsNodes().isNotEmpty()}
        assertEquals(lesson,repo.state.value.lastLessonId)
        assertTrue(repo.state.value.submissions.isEmpty())
        compose.onNodeWithContentDescription("뒤로").performClick()
        planNode("plan-practice").performClick()
        compose.onNode(hasText("문항 시작",substring=true) and hasClickAction()).performClick()
        compose.waitUntil(10000){repo.state.value.sessions.isNotEmpty()}
        val questions=repo.state.value.sessions.last().items.map{it.question}
        assertTrue(questions.isNotEmpty())
        assertTrue(questions.all{it.id in expected&&it.kind!="mock"&&it.mockSetId==null})
    }
    @Test fun strictMockMustConfirmBeforeOpeningPlanAndCancelPreservesIt(){
        val mockId=repo.pack.questions.first{it.kind=="mock"&&it.mockSetId!=null}.mockSetId!!
        val questions=repo.pack.mock(mockId)
        val created=runBlocking{repo.update{s->StudyEngine.createSession(s,repo.pack,questions,"strict","계획 이동 실전 보호",System.currentTimeMillis(),SystemClock.elapsedRealtime(),Settings.Global.getInt(app.contentResolver,Settings.Global.BOOT_COUNT,0),9,mockId)}}
        val id=created.activeSessionId!!
        compose.waitForIdle();openPlan()
        compose.onNodeWithText("연습 모드로 전환할까요?").assertIsDisplayed()
        compose.onNodeWithText("실전 유지").performClick()
        assertEquals("strict",repo.state.value.sessions.first{it.id==id}.mode)
        assertTrue(repo.state.value.submissions.isEmpty())
        openPlan()
        compose.onNodeWithText("전환하고 보기").performClick()
        compose.waitUntil(10000){compose.onAllNodesWithTag("study-plan-list").fetchSemanticsNodes().isNotEmpty()}
        assertEquals("mixed",repo.state.value.sessions.first{it.id==id}.mode)
        assertFalse(repo.state.value.sessions.first{it.id==id}.diagnosticEligible)
        assertTrue(repo.state.value.submissions.isEmpty())
    }
}
