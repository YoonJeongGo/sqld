package kr.sqld.study

import androidx.compose.foundation.layout.Column
import androidx.compose.material3.Text
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.test.ext.junit.runners.AndroidJUnit4
import kotlinx.coroutines.flow.MutableStateFlow
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class CountdownOptimizationUiTest {
    @get:Rule val compose=createComposeRule()

    @Test fun secondTicksUpdateCountdownWithoutRecomposingQuestionParent(){
        val clock=MutableStateFlow(100_000L)
        var questionCompositions=0
        compose.setContent {
            SqlNoteTheme(false,1f) {
                Column {
                    SideEffect { questionCompositions++ }
                    Text("고정된 문제와 답안")
                    SessionCountdown(65_000L,100_000L,clock)
                }
            }
        }
        compose.onNodeWithText("01:05").assertIsDisplayed()
        val before=compose.runOnIdle { questionCompositions }
        repeat(6) { second ->
            compose.runOnIdle { clock.value=101_000L+second*1_000 }
            compose.waitForIdle()
        }
        compose.onNodeWithText("00:59").assertIsDisplayed()
        compose.onNodeWithText("고정된 문제와 답안").assertIsDisplayed()
        compose.runOnIdle { assertEquals("Clock must invalidate only its own composition",before,questionCompositions) }
    }

    @Test fun countdownRetainsExistingZeroAndBackwardClockDisplayBounds(){
        val clock=MutableStateFlow(100_000L)
        compose.setContent { SqlNoteTheme(false,1f) { SessionCountdown(65_000L,100_000L,clock) } }
        compose.onNodeWithText("01:05").assertIsDisplayed()
        compose.runOnIdle { clock.value=999_000L }
        compose.onNodeWithText("00:00").assertIsDisplayed()
        compose.runOnIdle { clock.value=95_000L }
        compose.onNodeWithText("01:05").assertIsDisplayed()
    }
}
