package kr.sqld.study

import android.app.Application
import android.graphics.Bitmap
import android.util.Log
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.StateRestorationTester
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.lifecycle.viewModelScope
import androidx.room.withTransaction
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import java.io.File
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Failure injection and saved-instance restoration use only an isolated in-memory Room DB. */
@RunWith(AndroidJUnit4::class)
class FunctionalRecoveryUiTest {
    @get:Rule val compose=createComposeRule()
    private lateinit var repo:StudyRepository
    private lateinit var vm:StudyViewModel
    private lateinit var restoration:StateRestorationTester
    private lateinit var app:Application
    @Before fun setup(){
        app=ApplicationProvider.getApplicationContext()
        repo=StudyRepository(app,Room.inMemoryDatabaseBuilder(app,StudyDatabase::class.java).build(),false)
    }
    @After fun cleanup()=runBlocking{
        if(::vm.isInitialized)vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin()
        repo.db.close()
    }
    private fun launch(waitReady:Boolean=true){
        compose.runOnUiThread{vm=StudyViewModel(app,repo)}
        restoration=StateRestorationTester(compose)
        restoration.setContent{SqlNoteApp(vm)}
        if(waitReady)compose.waitUntil(20000){vm.ready.value}
        compose.waitForIdle()
    }
    private fun openNote(){
        compose.openHomeTools()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("노트 펼치기") and hasClickAction())
        compose.onNode(hasText("노트 펼치기") and hasClickAction()).performScrollTo().performClick()
        compose.waitUntil(10000){compose.onAllNodesWithTag("note-reader").fetchSemanticsNodes().isNotEmpty()}
    }
    private fun captureNavigation(label:String){
        runCatching{
            val bitmap=InstrumentationRegistry.getInstrumentation().uiAutomation.takeScreenshot()
                ?:throw AssertionError("Screenshot unavailable")
            try{File(app.cacheDir,"memo-nav-$label.png").outputStream().use{bitmap.compress(Bitmap.CompressFormat.PNG,100,it)}}
            finally{bitmap.recycle()}
            val roots=compose.onAllNodes(isRoot(),useUnmergedTree=true)
            File(app.cacheDir,"memo-nav-$label.txt").writeText((0 until roots.fetchSemanticsNodes().size).joinToString("\n\n"){roots[it].printToString()})
        }.onFailure{Log.e("FunctionalRecoveryUiTest","Navigation capture failed",it)}
    }
    private fun openAnnotations(){
        // At 200% the transient save Snackbar covers the merged row's click centre.
        // Wait for its normal dismissal; do not invoke navigation or clear UI state directly.
        compose.waitUntil(15000){vm.message.value==null}
        compose.waitForIdle()
        try{
            compose.onNodeWithContentDescription("설정",useUnmergedTree=true).performClick()
            compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("나의 필기와 북마크"))
            compose.onNodeWithText("나의 필기와 북마크").performScrollTo().assertIsDisplayed().performClick()
            compose.onNodeWithText("필기와 북마크").assertIsDisplayed()
            compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("메모 수정"))
        }catch(failure:Throwable){captureNavigation("failure");throw failure}
    }
    private fun failNextSave(button:String){
        compose.runOnIdle{repo.failNextWrite=true}
        compose.onNode(hasText(button) and hasClickAction()).performClick()
        compose.waitUntil(10000){vm.error.value!=null}
        compose.onNodeWithText("저장을 확인해 주세요").assertIsDisplayed()
        compose.onNode(hasText("확인") and hasClickAction()).performClick()
    }
    @Test fun initialReadFailureCanRetryWithoutResettingExistingRecords(){
        runBlocking{
            repo.initialize()
            repo.update{it.copy(contentVersion="prior-version",bookmarks=listOf(Bookmark(repo.pack.practice().first().id,1)))}
        }
        val before=repo.state.value
        repo.failNextWrite=true
        launch(false)
        compose.waitUntil(20000){vm.error.value!=null}
        assertFalse(vm.ready.value)
        assertEquals(before,repo.state.value)
        compose.onNodeWithText("다시 열기").performScrollTo().assertIsDisplayed().performClick()
        compose.waitUntil(20000){vm.ready.value}
        assertNull(vm.error.value)
        val after=repo.state.value
        assertEquals(before,after.copy(contentVersion=before.contentVersion,revision=before.revision))
        compose.onNodeWithText("내 공부").assertExists()
    }
    @Test fun lessonOnlySearchHasNoFalseEmptyStateAndOpensTheLesson(){
        launch()
        compose.onNodeWithContentDescription("노트와 연습문제 검색").performClick()
        compose.onNode(hasSetTextAction()).performTextInput("ANSI")
        compose.onNodeWithText("찾은 항목이 없어요").assertDoesNotExist()
        val lesson=repo.course.lessons.single{it.id=="2-1-25"}
        compose.onNodeWithTag("notes-list").performScrollToNode(hasText(lesson.title) and hasClickAction())
        compose.onNode(hasText(lesson.title) and hasClickAction()).performClick()
        compose.waitUntil(10000){repo.state.value.lastLessonId==lesson.id}
        compose.onNodeWithContentDescription("뒤로").performClick()
        compose.onNodeWithTag("notes-list").performScrollToNode(hasSetTextAction())
        compose.onNode(hasSetTextAction()).assertTextContains("ANSI").performTextReplacement("zzzz-no-such-lesson")
        compose.onNodeWithTag("notes-list").performScrollToNode(hasText("찾은 항목이 없어요"))
        compose.onNodeWithText("찾은 항목이 없어요").assertIsDisplayed()
    }
    @Test fun newMemoDraftSurvivesSavedStateAndWriteFailureThenSavesOnce(){
        launch();openNote()
        compose.onAllNodesWithText("이 단락에 메모").onFirst().performScrollTo().performClick()
        compose.onNode(hasSetTextAction()).performTextInput("보존할 메모 초안")
        restoration.emulateSavedInstanceStateRestore()
        compose.onNode(hasSetTextAction()).assertTextContains("보존할 메모 초안")
        failNextSave("저장")
        compose.onNode(hasSetTextAction()).assertTextContains("보존할 메모 초안")
        assertTrue(repo.state.value.annotations.isEmpty())
        compose.onNode(hasText("저장") and hasClickAction()).performClick()
        compose.waitUntil(10000){repo.state.value.annotations.size==1}
        assertEquals("보존할 메모 초안",repo.state.value.annotations.single().memo)
        compose.onNodeWithText("여백에 메모").assertDoesNotExist()
    }
    @Test fun editedMemoKeepsOriginalAndDraftOnFailureAndExplicitCancelDiscardsDraft(){
        runBlocking{
            repo.initialize()
            val note=repo.pack.notes.first();val block=note.blocks.first()
            repo.update{it.copy(annotations=listOf(Annotation("memo-qa",note.id,block.id,block.text,"기존 메모","memo",1)))}
        }
        launch()
        openAnnotations()
        compose.onNodeWithText("메모 수정").performScrollTo().performClick()
        compose.onNode(hasSetTextAction() and hasText("기존 메모",substring=true)).performTextReplacement("수정한 초안")
        restoration.emulateSavedInstanceStateRestore()
        compose.onNode(hasSetTextAction() and hasText("수정한 초안",substring=true)).assertExists()
        failNextSave("저장")
        assertEquals("기존 메모",repo.state.value.annotations.single().memo)
        compose.onNode(hasSetTextAction() and hasText("수정한 초안",substring=true)).assertExists()
        compose.onNode(hasText("취소") and hasClickAction()).performClick()
        assertEquals("기존 메모",repo.state.value.annotations.single().memo)
        compose.onNodeWithText("메모 수정").performClick()
        compose.onNode(hasSetTextAction() and hasText("기존 메모",substring=true)).performTextReplacement("저장한 수정")
        compose.onNode(hasText("저장") and hasClickAction()).performClick()
        compose.waitUntil(10000){repo.state.value.annotations.single().memo=="저장한 수정"}
        assertEquals("memo-qa",repo.state.value.annotations.single().id)
        assertEquals(1,repo.state.value.annotations.size)
    }
    @Test fun issueDraftSurvivesSavedStateAndFailureWithoutExcludingTheNote(){
        launch();openNote()
        compose.onNode(hasText("내용 오류 표시") and hasClickAction()).performScrollTo().performClick()
        compose.onNode(hasSetTextAction()).performTextInput("검토할 내용")
        restoration.emulateSavedInstanceStateRestore()
        compose.onNode(hasSetTextAction()).assertTextContains("검토할 내용")
        failNextSave("표시 저장")
        assertTrue(repo.state.value.issues.isEmpty())
        compose.onNode(hasSetTextAction()).assertTextContains("검토할 내용")
        compose.onNode(hasText("표시 저장") and hasClickAction()).performClick()
        compose.waitUntil(10000){repo.state.value.issues.size==1}
        assertEquals("검토할 내용",repo.state.value.issues.single().description)
        assertFalse(repo.state.value.issues.single().exclude)
    }
    private fun saveWhileRecreating(button:String){
        val held=CompletableDeferred<Unit>();val release=CompletableDeferred<Unit>()
        val lock=CoroutineScope(Dispatchers.IO).launch{repo.db.withTransaction{held.complete(Unit);release.await()}}
        try{
            runBlocking{held.await()}
            compose.onNode(hasText(button) and hasClickAction()).performClick()
            compose.waitUntil(10000){vm.busy.value}
            restoration.emulateSavedInstanceStateRestore()
            compose.onNode(hasText(button) and hasClickAction()).assertIsNotEnabled()
        }finally{release.complete(Unit);runBlocking{lock.join()}}
        compose.waitUntil(10000){!vm.busy.value}
        compose.waitForIdle()
    }
    @Test fun savingAndEditingMemoAcrossRecreationCommitOnceAndCloseTheRestoredDialog(){
        launch();openNote()
        compose.onAllNodesWithText("이 단락에 메모").onFirst().performScrollTo().performClick()
        compose.onNode(hasSetTextAction()).performTextInput("저장 중 회전")
        saveWhileRecreating("저장")
        compose.waitUntil(10000){repo.state.value.annotations.size==1}
        compose.onNodeWithText("여백에 메모").assertDoesNotExist()
        val id=repo.state.value.annotations.single().id
        compose.onNodeWithContentDescription("뒤로").performClick()
        openAnnotations()
        compose.onNodeWithText("메모 수정").performScrollTo().performClick()
        compose.onNode(hasSetTextAction() and hasText("저장 중 회전",substring=true)).performTextReplacement("수정 중 회전")
        saveWhileRecreating("저장")
        compose.onNodeWithText("나의 메모 수정").assertDoesNotExist()
        assertEquals(1,repo.state.value.annotations.size)
        assertEquals(id,repo.state.value.annotations.single().id)
        assertEquals("수정 중 회전",repo.state.value.annotations.single().memo)
    }
    @Test fun staleMemoDraftCannotWriteIntoReplacedRecords(){
        launch();openNote()
        compose.onAllNodesWithText("이 단락에 메모").onFirst().performScrollTo().performClick()
        compose.onNode(hasSetTextAction()).performTextInput("복원 전 초안")
        runBlocking{repo.restore(repo.state.value)}
        compose.onNode(hasText("저장") and hasClickAction()).performClick()
        compose.waitUntil(10000){vm.error.value?.contains("기록이 복원되어")==true}
        assertTrue(repo.state.value.annotations.isEmpty())
        compose.onNode(hasText("확인") and hasClickAction()).performClick()
        compose.onNode(hasSetTextAction()).assertTextContains("복원 전 초안")
    }
    @Test fun questionIssueKeepsExclusionChoiceAcrossRecreationAndOnlyAppliesOnSave(){
        runBlocking{
            repo.initialize()
            repo.update{StudyEngine.createSession(it,repo.pack,listOf(repo.pack.practice().first()),"immediate","오류 표시 확인",1,1,0,1)}
        }
        val question=repo.state.value.sessions.single().items.single().question
        launch()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("풀던 문제 이어서") and hasClickAction())
        compose.onNode(hasText("풀던 문제 이어서") and hasClickAction()).performScrollTo().performClick()
        // Question metadata/help is now collapsed to leave more room for the stem and choices.
        compose.onNode(hasText("내용 오류 표시") and hasClickAction()).assertDoesNotExist()
        compose.onNodeWithText("문제 정보·도움").performScrollTo().performClick()
        compose.onNode(hasText("내용 오류 표시") and hasClickAction()).performScrollTo().performClick()
        compose.onNode(hasSetTextAction()).performTextInput("문항 검토")
        compose.onNode(isToggleable() and hasAnyAncestor(isDialog())).performScrollTo().assertIsOn().performClick()
        restoration.emulateSavedInstanceStateRestore()
        compose.onNode(isToggleable() and hasAnyAncestor(isDialog())).assertIsOff()
        compose.onNode(hasSetTextAction()).assertTextContains("문항 검토")
        assertTrue(repo.state.value.issues.isEmpty())
        compose.onNode(isToggleable() and hasAnyAncestor(isDialog())).performScrollTo().performClick()
        saveWhileRecreating("표시 저장")
        assertTrue(repo.state.value.issues.single().exclude)
        assertEquals(question.id,repo.state.value.issues.single().contentId)
        assertFalse(StudyEngine.available(repo.pack,repo.state.value).any{it.id==question.id})
        assertTrue(repo.state.value.submissions.isEmpty())
    }

}
