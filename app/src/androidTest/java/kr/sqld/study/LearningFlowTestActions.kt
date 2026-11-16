package kr.sqld.study

import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.ComposeTestRule

/** Navigate the real disclosure controls; never bypass the app route to reach legacy tools. */
internal fun ComposeTestRule.openHomeTools() {
    onNode(hasTestTag("home-compact") or hasTestTag("home-wide"))
        .performScrollToNode(hasTestTag("home-tools-toggle"))
    val toggle=onNodeWithTag("home-tools-toggle").performScrollTo()
    if(toggle.fetchSemanticsNode().config[SemanticsProperties.StateDescription]=="접힘")toggle.performClick()
    toggle.assert(SemanticsMatcher.expectValue(SemanticsProperties.StateDescription,"펼쳐짐"))
}

internal fun ComposeTestRule.openLessonTools() {
    waitUntil(10_000){onAllNodesWithTag("lesson-tools-toggle").fetchSemanticsNodes().isNotEmpty()}
    val toggle=onNodeWithTag("lesson-tools-toggle").performScrollTo()
    if(toggle.fetchSemanticsNode().config[SemanticsProperties.StateDescription]=="접힘")toggle.performClick()
    toggle.assert(SemanticsMatcher.expectValue(SemanticsProperties.StateDescription,"펼쳐짐"))
}

/** The home card may be below the first viewport on a phone or with large text. */
internal fun ComposeTestRule.resumeProblem() {
    onNode(hasTestTag("home-compact") or hasTestTag("home-wide"))
        .performScrollToNode(hasText("풀던 문제 이어서") and hasClickAction())
    onNode(hasText("풀던 문제 이어서") and hasClickAction()).performScrollTo().performClick()
}
