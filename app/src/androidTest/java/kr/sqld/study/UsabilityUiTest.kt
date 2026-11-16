package kr.sqld.study

import android.app.Application
import android.os.SystemClock
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.SoftwareKeyboardController
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

/** Real rendered flows against isolated memory storage. Never opens the personal app database. */
@RunWith(AndroidJUnit4::class)
class UsabilityUiTest {
    @get:Rule val compose=createComposeRule()
    private lateinit var vm:StudyViewModel
    private lateinit var repo:StudyRepository
    private var keyboard:SoftwareKeyboardController?=null

    @Before fun setup(){
        val app=ApplicationProvider.getApplicationContext<Application>()
        repo=StudyRepository(app,Room.inMemoryDatabaseBuilder(app,StudyDatabase::class.java).build(),false)
        compose.runOnUiThread{vm=StudyViewModel(app,repo)}
        compose.setContent{keyboard=LocalSoftwareKeyboardController.current;SqlNoteApp(vm)}
        compose.waitUntil(20000){vm.ready.value}
        compose.waitForIdle()
    }

    @After fun cleanup()=runBlocking{
        vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin()
        repo.db.close()
    }

    private fun state()=repo.state.value
    private fun openNotes(){
        compose.onNodeWithContentDescription("진도",useUnmergedTree=true).performClick()
        compose.onNodeWithTag("course-list").performScrollToNode(hasText("개념 찾기") and hasClickAction())
        compose.onNodeWithText("개념 찾기").performScrollTo().performClick()
        compose.onNodeWithTag("notes-list").assertExists()
    }
    private fun listScroll()=compose.onNodeWithTag("notes-list").fetchSemanticsNode()
        .config[SemanticsProperties.VerticalScrollAxisRange].value()

    @Test fun noteReturnPreservesSearchAndPriority(){
        openNotes()
        compose.onNodeWithText("핵심 개념").performScrollTo().performClick()
        compose.onNode(hasSetTextAction()).performTextInput("sql")
        compose.runOnIdle{keyboard?.hide()}
        compose.waitForIdle()
        val note=repo.pack.notes.first{it.id=="note-S12"}
        compose.onNodeWithTag("notes-list").performScrollToNode(hasText(note.title))
        val before=listScroll()
        // The filtered results can fit a tablet without scrolling. Zero remains
        // a valid position; nonzero scroll restoration is exercised separately.
        compose.onNodeWithText(note.title).performClick()
        compose.onNodeWithText("전체 설명").assertExists()
        compose.onNodeWithContentDescription("뒤로").performClick()
        compose.onNodeWithTag("notes-list").assertExists()
        assertEquals("Back should return to the same list position",before,listScroll(),1f)
        compose.onNodeWithTag("notes-list").performScrollToNode(hasSetTextAction())
        compose.onNode(hasSetTextAction()).assertTextContains("sql")
        compose.onNodeWithTag("notes-list").performScrollToNode(hasText("핵심 개념"))
        compose.onNodeWithText("핵심 개념").assertIsSelected()
        assertTrue(state().submissions.isEmpty())
    }

    @Test fun noteReturnPreservesScrolledUnfilteredListPosition(){
        openNotes()
        // Use all 41 notes rather than three filtered results so the supported
        // phone and tablet viewports both need to scroll to this final entry.
        val note=repo.pack.notes.last()
        compose.onNodeWithTag("notes-list").performScrollToNode(hasText(note.title))
        val before=listScroll()
        assertTrue("The full note list must actually scroll before opening its final note",before>0f)
        val records=state().submissions
        compose.onNodeWithText(note.title).performClick()
        compose.onNodeWithText("전체 설명").assertExists()
        compose.onNodeWithContentDescription("뒤로").performClick()
        compose.onNodeWithTag("notes-list").assertExists()
        assertEquals("Back should restore the scrolled full list",before,listScroll(),1f)
        assertEquals(records,state().submissions)
    }

    private fun shortReviewUsesConfiguredDailyCount(daily:Int){
        val questions=repo.pack.practice().take(30)
        runBlocking{repo.update{s->s.copy(
            settings=s.settings.copy(dailyCount=daily),
            reviews=questions.map{ReviewState(it.id,dueAt=0)}
        )}}
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("짧게 복습하기"))
        compose.onNodeWithText("오늘 ${daily}개",substring=true).assertExists()
        compose.onNodeWithText("다시 볼 문제 30개",substring=true).assertExists()
        compose.onNodeWithText("짧게 복습하기").performClick()
        compose.onNodeWithText("대상 ${daily}문항 · 중복 없이 최대 ${daily}문항").assertExists()
        compose.onNodeWithText("${daily}문항 시작").assertIsEnabled().performClick()
        compose.waitUntil(10000){state().sessions.isNotEmpty()}
        assertEquals(daily,state().sessions.single().items.size)
        assertEquals(daily,state().sessions.single().items.map{it.question.id}.distinct().size)
        assertTrue(state().submissions.isEmpty())
    }

    @Test fun dailyFiveStartsFiveReviewQuestions()=shortReviewUsesConfiguredDailyCount(5)
    @Test fun dailyTwentyStartsTwentyReviewQuestions()=shortReviewUsesConfiguredDailyCount(20)

    @Test fun currentWrongAnswersDoNotIncludeCorrectHelpedOrGuessedAttempts(){
        val questions=repo.pack.practice().take(4)
        val now=System.currentTimeMillis()
        runBlocking{repo.update{original->
            var s=StudyEngine.createSession(original,repo.pack,questions,"batch","복습 분류 검증",now,SystemClock.elapsedRealtime(),0,9)
            val id=s.sessions.last().id
            s=StudyEngine.select(s,id,0,questions[0].correctChoiceIds.single())
            s=StudyEngine.help(s,id,0,"note",now)
            s=StudyEngine.grade(s,id,0,now+1)
            s=StudyEngine.select(s,id,1,questions[1].correctChoiceIds.single())
            s=StudyEngine.confidence(s,id,1,"guess")
            s=StudyEngine.grade(s,id,1,now+1)
            s=StudyEngine.select(s,id,2,questions[2].choices.first{it.id !in questions[2].correctChoiceIds}.id)
            s=StudyEngine.grade(s,id,2,now+1)
            s=StudyEngine.grade(s,id,3,now+1,unanswered=true)
            StudyEngine.submit(s,id,now+2)
        }}
        val preserved=state().submissions.toList()
        assertTrue(state().reviews.all{it.needsReview})
        compose.onNodeWithContentDescription("복습",useUnmergedTree=true).performClick()
        compose.onNodeWithText("현재 오답·미응답").performScrollTo().performClick()
        compose.onNodeWithText("현재 오답·미응답 2문항").performScrollTo().assertIsDisplayed()
        compose.onNodeWithText("골라 풀기").performClick()
        compose.onNodeWithText("2문항 시작").performClick()
        compose.waitUntil(10000){state().sessions.size==2}
        assertEquals(questions.drop(2).map{it.id}.toSet(),state().sessions.last().items.map{it.question.id}.toSet())
        assertEquals(preserved,state().submissions)
    }

    @Test fun searchCanOpenAResultBeyondTheFirstHundredMatches(){
        val matches=repo.pack.practice().filter{it.title.contains("이")||it.stem.contains("이")}
        assertTrue("The fixture must exercise the former 100 result cutoff",matches.size>100)
        val target=matches.last{q->repo.pack.practice().count{it.title==q.title}==1}
        assertTrue(matches.indexOf(target)>=100)
        openNotes()
        compose.onNode(hasSetTextAction()).performTextInput("이")
        compose.runOnIdle{keyboard?.hide()}
        compose.onNodeWithTag("notes-list").performScrollToNode(hasText(target.title))
        compose.onNodeWithText(target.title).performClick()
        compose.onNodeWithText("1문항 시작").performClick()
        compose.waitUntil(10000){state().sessions.isNotEmpty()}
        assertEquals(target.id,state().sessions.single().items.single().question.id)
        assertTrue(state().submissions.isEmpty())
    }
    @Test fun collapsedNoteFiltersKeepTheirSelectionAfterReadingAndReturning(){
        openNotes()
        compose.onNodeWithText("핵심 개념").performClick()
        compose.onNodeWithTag("notes-filter-toggle").performScrollTo().performClick()
        compose.onNodeWithText("1과목 모델링").performScrollTo().performClick()
        compose.onNodeWithText("중요도 순서").performScrollTo().performClick()
        compose.onNodeWithTag("notes-filter-toggle").performScrollTo().performClick()
        compose.onNodeWithText("1과목 모델링 · 중요도 순서").assertExists()
        val note=repo.pack.notes.first{it.id=="note-M04"}
        compose.onNodeWithTag("notes-list").performScrollToNode(hasText(note.title))
        compose.onNodeWithText(note.title).performClick()
        compose.onNodeWithText("전체 설명").assertExists()
        compose.onNodeWithContentDescription("뒤로").performClick()
        compose.onNodeWithTag("notes-list").performScrollToNode(hasTestTag("notes-filter-toggle"))
        compose.onNodeWithText("1과목 모델링 · 중요도 순서").assertExists()
        compose.onNodeWithTag("notes-filter-toggle").performClick()
        compose.onNodeWithText("1과목 모델링").performScrollTo().assertIsSelected()
        compose.onNodeWithText("중요도 순서").performScrollTo().assertIsSelected()
        assertTrue(state().submissions.isEmpty())
    }

    @Test fun reviewSubjectChangeResetsHiddenTopicAndStartsOnlyVisibleSelection(){
        val model=repo.pack.practice().filter{it.subjectId=="model"}.take(2)
        val sql=repo.pack.practice().first{it.subjectId=="sql"&&it.topicId=="C"}
        val stars=(model+sql).map{Bookmark(it.id,System.currentTimeMillis())}
        runBlocking{repo.update{it.copy(bookmarks=stars)}}
        compose.onNodeWithContentDescription("복습",useUnmergedTree=true).performClick()
        compose.onNodeWithText("별표",substring=false).performClick()
        compose.onNodeWithTag("review-filter-toggle").performScrollTo().performClick()
        compose.onNodeWithText("2과목").performScrollTo().performClick()
        compose.onNodeWithText("SQL 기본").performScrollTo().performClick()
        compose.onNodeWithText("1과목").performScrollTo().performClick()
        compose.onNodeWithText("전체 단원").performScrollTo().assertIsSelected()
        compose.onNodeWithTag("review-filter-toggle").performScrollTo().performClick()
        compose.onNodeWithText("별표 2문항").performScrollTo().assertIsDisplayed()
        compose.onNodeWithText("골라 풀기").performScrollTo().performClick()
        compose.onNodeWithText("2문항 시작").performClick()
        compose.waitUntil(10000){state().sessions.isNotEmpty()}
        assertEquals(model.map{it.id}.toSet(),state().sessions.single().items.map{it.question.id}.toSet())
        assertEquals(stars,state().bookmarks)
        assertTrue(state().submissions.isEmpty())
    }

}
