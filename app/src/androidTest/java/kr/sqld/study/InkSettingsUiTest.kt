package kr.sqld.study

import androidx.activity.ComponentActivity
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.Modifier
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.unit.dp
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class InkSettingsUiTest {
    @get:Rule val compose=createAndroidComposeRule<ComponentActivity>()
    @Test fun roundPenButtonOpensSettingsAndUndoRedoPreserveDocument(){
        val sql="SELECT COUNT(*) FROM T"
        val initial=InkStore.add(InkStore.empty("settings-test",sql),InkStroke("first",points=listOf(InkPoint(20f,20f),InkPoint(100f,20f))),1)
        val doc=mutableStateOf(initial)
        compose.setContent{SqlNoteTheme(false,1f){InkSqlSurface(sql,"settings-test",doc.value,listOf(7..14),{doc.value=it},Modifier.height(320.dp))}}
        compose.onNodeWithTag("ink-settings").performClick()
        compose.onNodeWithText("펜 설정").assertIsDisplayed()
        compose.onNodeWithTag("ink-finger-toggle").performScrollTo().performClick().assertIsOn()
        compose.onNodeWithTag("ink-hex").performScrollTo().performTextReplacement("E67C18")
        compose.onNodeWithTag("ink-undo").performScrollTo().performClick()
        compose.runOnIdle{assertTrue(InkStore.visibleStrokes(doc.value).isEmpty())}
        compose.onNodeWithTag("ink-redo").performScrollTo().performClick()
        compose.runOnIdle{assertEquals(InkStore.visibleStrokes(initial),InkStore.visibleStrokes(doc.value))}
        compose.onNodeWithText("완료").performClick()
        compose.onNodeWithTag("ink-settings").performClick()
        compose.onNodeWithTag("ink-finger-toggle").performScrollTo().assertIsOn()
        compose.onNodeWithTag("ink-hex").performScrollTo().assertTextContains("E67C18")
    }
}
