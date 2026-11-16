package kr.sqld.study

import android.app.Application
import android.graphics.Bitmap
import android.text.Selection
import android.text.Spannable
import android.text.Spanned
import android.text.style.BackgroundColorSpan
import android.view.ActionMode
import android.view.Menu
import android.view.MenuInflater
import android.view.View
import android.view.ViewGroup
import android.widget.PopupMenu
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.TextLayoutResult
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
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
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

/**
 * Rendered checks run against the packaged material and an isolated in-memory learner database.
 * The caller sets the emulator window/font profile; PNG names are intentionally stable so the
 * caller can pull each run into a distinct profile directory. No personal DB is opened or reset.
 */
@RunWith(AndroidJUnit4::class)
class BodyReadabilityUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    private lateinit var app: Application
    private lateinit var repo: StudyRepository
    private lateinit var vm: StudyViewModel
    private val componentPage = mutableStateOf<(@Composable () -> Unit)?>(null)

    @Before fun setup() {
        app = ApplicationProvider.getApplicationContext()
        repo = StudyRepository(app, Room.inMemoryDatabaseBuilder(app, StudyDatabase::class.java).build(), false)
        compose.runOnUiThread { vm = StudyViewModel(app, repo) }
        compose.setContent {
            val page = componentPage.value
            if (page == null) SqlNoteApp(vm) else SqlNoteTheme(false, 1f) { page() }
        }
        compose.waitUntil(20_000) { vm.ready.value }
    }

    @After fun cleanup() = runBlocking {
        vm.viewModelScope.coroutineContext[Job]?.cancelAndJoin()
        repo.db.close()
    }

    private fun openGuide(lessonId: String) {
        runBlocking { repo.update { CourseStudy.update(it, lessonId, { it }) } }
        compose.onNode(hasTestTag("home-compact") or hasTestTag("home-wide"))
            .performScrollToNode(hasTestTag("home-course-resume"))
        compose.onNodeWithTag("home-course-resume").performScrollTo().performClick()
        compose.openLessonTools()
        compose.waitUntil(10_000) { compose.onAllNodesWithTag("lesson-guide-open").fetchSemanticsNodes().isNotEmpty() }
        compose.onNodeWithTag("lesson-guide-open").performScrollTo().performClick()
        compose.onNodeWithTag("lesson-guide-dialog").assertIsDisplayed()
    }

    private fun selectExample(id: String) {
        compose.onNodeWithTag("guide-tab-read").performScrollTo().performClick()
        compose.onNodeWithTag("guide-example-picker").performClick()
        compose.onNodeWithTag("guide-pick-$id").performScrollTo().performClick()
    }

    private fun stepTitle() = compose.onNodeWithTag("walk-step-title").fetchSemanticsNode()
        .config[SemanticsProperties.Text].single().text

    private fun advance(count: Int) = repeat(count) { compose.onNodeWithTag("walk-next").performClick() }

    private fun textInside(tag: String): List<AnnotatedString> = compose.onAllNodes(
        SemanticsMatcher.keyIsDefined(SemanticsProperties.Text) and hasAnyAncestor(hasTestTag(tag)),
        useUnmergedTree = true
    ).fetchSemanticsNodes().flatMap { it.config[SemanticsProperties.Text] }

    private fun assertBoldPhrase(tag: String, phrase: String) {
        val found = textInside(tag).any { text ->
            text.spanStyles.any { span ->
                (span.item.fontWeight?.weight ?: 0) >= FontWeight.SemiBold.weight &&
                    text.text.substring(span.start, span.end).contains(phrase)
            }
        }
        assertTrue("Expected an actual bold AnnotatedString span for '$phrase' inside $tag", found)
    }

    /** Checks text measurement, not arbitrary viewport visibility of scrollable long content. */
    private fun assertTextLayoutsDoNotClip(tag: String) {
        val nodes = compose.onAllNodes(
            SemanticsMatcher.keyIsDefined(SemanticsActions.GetTextLayoutResult) and hasAnyAncestor(hasTestTag(tag)),
            useUnmergedTree = true
        )
        val count = nodes.fetchSemanticsNodes().size
        assertTrue("No text layout results under $tag", count > 0)
        repeat(count) { index ->
            val layouts = mutableListOf<TextLayoutResult>()
            nodes[index].performSemanticsAction(SemanticsActions.GetTextLayoutResult) { it(layouts) }
            val bounds = nodes[index].fetchSemanticsNode().boundsInRoot
            layouts.forEach { layout ->
                val label = layout.layoutInput.text.text.take(90)
                val lines = (0 until layout.lineCount).map { line -> layout.getLineLeft(line) to layout.getLineRight(line) }
                val minimumLeft = lines.minOfOrNull { it.first } ?: 0f
                val maximumRight = lines.maxOfOrNull { it.second } ?: 0f
                val paragraphExcess = layout.multiParagraph.width - layout.size.width
                val lastLineEnd = if (layout.lineCount == 0) 0 else layout.getLineEnd(layout.lineCount - 1, visibleEnd = false)
                val diagnostics = JSONObject().apply {
                    put("tag", tag); put("text", label)
                    put("sizeWidth", layout.size.width); put("sizeHeight", layout.size.height)
                    put("multiParagraphWidth", layout.multiParagraph.width); put("multiParagraphHeight", layout.multiParagraph.height)
                    put("paragraphExcessPx", paragraphExcess)
                    put("lineLeftRight", JSONArray(lines.map { JSONArray(listOf(it.first, it.second)) }))
                    put("lastLineEnd", lastLineEnd); put("sourceLength", layout.layoutInput.text.length)
                    put("constraints", layout.layoutInput.constraints.toString())
                    put("boundsInRoot", bounds.toString())
                    put("didOverflowWidth", layout.didOverflowWidth); put("didOverflowHeight", layout.didOverflowHeight)
                    put("fontScale", app.resources.configuration.fontScale)
                    put("screenWidthDp", app.resources.configuration.screenWidthDp)
                    put("screenHeightDp", app.resources.configuration.screenHeightDp)
                }
                File(app.cacheDir, "body-layout-$tag-${label.hashCode()}.json").writeText(diagnostics.toString(2))
                // MultiParagraph can retain the parent's available width while the Text node
                // shrinks to its actual lines (measured: paragraph 775 px, Text/line 249 px).
                // Check every rendered line against the actual Text width, regardless of the
                // overflow flag; only float-to-pixel edge rounding gets a 1 physical-pixel margin.
                assertTrue("Rendered line exceeds actual Text bounds: $diagnostics", minimumLeft >= -1f && maximumRight <= layout.size.width + 1f)
                assertEquals("The last rendered line must include the whole source: $diagnostics", layout.layoutInput.text.length, lastLineEnd)
                assertFalse("Vertical text overflow: $label", layout.didOverflowHeight)
                repeat(layout.lineCount) { line -> assertFalse("Ellipsized content: $label", layout.isLineEllipsized(line)) }
            }
        }
    }

    private fun capture(name: String) {
        compose.waitForIdle()
        val bitmap = InstrumentationRegistry.getInstrumentation().uiAutomation.takeScreenshot() ?: error("No screenshot")
        File(app.cacheDir, "body-$name.png").outputStream().use { assertTrue(bitmap.compress(Bitmap.CompressFormat.PNG, 100, it)) }
        bitmap.recycle()
    }

    @Test fun modelingParagraphsHaveRealEmphasisAndStepRoundTripKeepsContent() {
        val original = repo.course.lessons.single { it.id == "1-1-02" }
        val guide = runBlocking { vm.lessonGuides.lesson(original)!! }
        val expected = guide.examples.first().steps.first().text
        openGuide(original.id)
        compose.onNodeWithTag("guide-tab-read").performScrollTo().performClick()
        advance(1)
        val title = stepTitle()
        assertEquals("문장에서 대상과 연결을 나누기", title)
        compose.onNodeWithTag("ink-code-surface").assertDoesNotExist()
        val displayed = textInside("walk-narrative").map { it.text }
        assertTrue(displayed.any { it.contains("학생은 사람을 관리하는 대상") })
        assertTrue(displayed.any { it.contains("이 업무에 필요한 사실을 뽑는 것") })
        assertBoldPhrase("walk-narrative", "학생")
        assertBoldPhrase("walk-narrative", "과목")
        capture("modeling")
        assertTextLayoutsDoNotClip("walk-narrative")
        val before = textInside("walk-narrative")
        compose.onNodeWithTag("walk-previous").performClick()
        compose.onNodeWithTag("walk-next").performClick()
        assertEquals(title, stepTitle())
        assertEquals(before, textInside("walk-narrative"))
        assertEquals(expected, guide.examples.first().steps.first().text)
        assertEquals(original, repo.course.lessons.single { it.id == original.id })
        compose.waitUntil(10_000) {
            CourseStudy.progress(repo.state.value, original.id).exampleSteps["guide:${original.examples.first().id}"] == 1
        }
        assertTrue(repo.state.value.submissions.isEmpty())
    }

    @Test fun insertPairingKeepsSqlValuesAndNavigationWhileEmphasizingColumns() {
        val original = repo.course.lessons.single { it.id == "2-1-05" }
        val guide = runBlocking { vm.lessonGuides.lesson(original)!! }
        val supplemental = guide.supplementalExamples.single { it.example.id == "supplemental-2-1-05-order" }
        val originalSql = supplemental.example.sql
        openGuide(original.id)
        selectExample(supplemental.example.id)
        advance(2)
        assertEquals("명시한 위치로 값을 연결", stepTitle())
        compose.onNodeWithTag("ink-code-surface").assertExists()
        listOf("NAME", "PHONE", "ID").forEach { assertBoldPhrase("walk-narrative", it) }
        val display = textInside("walk-narrative").joinToString("\n") { it.text }
        assertTrue(display.contains("양지훈"))
        assertTrue(display.contains("010-****-1003"))
        assertTrue(display.contains("1003"))
        capture("insert")
        assertTextLayoutsDoNotClip("walk-narrative")
        val before = textInside("walk-narrative")
        compose.onNodeWithTag("walk-next").performClick()
        compose.onNodeWithTag("walk-previous").performClick()
        assertEquals(before, textInside("walk-narrative"))
        assertEquals(originalSql, supplemental.example.sql)
        assertEquals(original, repo.course.lessons.single { it.id == original.id })
        val progress = CourseStudy.progress(repo.state.value, original.id)
        assertTrue(original.examples.none { it.id in progress.exampleSteps })
        assertTrue(progress.checks.isEmpty())
        assertEquals(0, progress.readVersion)
    }

    @Test fun guideTermsKeepMeaningsAndRolesVisibleWithoutClipping() {
        val lesson = repo.course.lessons.single { it.id == "2-1-05" }
        val guide = runBlocking { vm.lessonGuides.lesson(lesson)!! }
        openGuide(lesson.id)
        compose.onNodeWithTag("guide-tab-words").performScrollTo().performClick()
        val first = guide.terms.first()
        val texts = textInside("guide-details").joinToString("\n") { it.text }
        assertTrue(texts.contains(first.token))
        assertTrue(texts.contains(first.meaning))
        assertTrue(texts.contains(first.role))
        capture("terms")
        assertTextLayoutsDoNotClip("guide-details")
        compose.onNodeWithTag("guide-tab-sources").performScrollTo().performClick()
        capture("cautions")
        assertTextLayoutsDoNotClip("guide-details")
        assertTrue(repo.state.value.submissions.isEmpty())
    }

    private fun textViews(view: View): List<TextView> = when (view) {
        is TextView -> listOf(view)
        is ViewGroup -> (0 until view.childCount).flatMap { textViews(view.getChildAt(it)) }
        else -> emptyList()
    }

    @Test fun actualNoteRetainsNativeSelectionQuoteAndExistingStudyRecords() {
        val note = repo.pack.notes.first { it.id == "note-M01" }
        val block = note.blocks.first { it.kind == "definition" }
        val quote = block.text.take(20)
        val annotation = Annotation("body-preserved-highlight", note.id, block.id, quote, "기존 메모 보존", "highlight", 1)
        runBlocking { repo.update { it.copy(
            lastNoteId = note.id,
            notes = listOf(NoteProgress(note.id, read = true, readVersion = note.version)),
            annotations = listOf(annotation),
            noteBookmarks = listOf(Bookmark(note.id, 1)),
            reviews = listOf(ReviewState(repo.pack.practice().first().id, wrongCount = 2, stage = 1, dueAt = 99_000, needsReview = true))
        ) } }
        val before = repo.state.value
        compose.openHomeTools()
        compose.onNode(hasTestTag("home-compact") or hasTestTag("home-wide"))
            .performScrollToNode(hasText("노트 펼치기") and hasClickAction())
        compose.onNodeWithText("노트 펼치기").performClick()
        compose.waitUntil(10_000) { compose.onAllNodesWithTag("note-reader").fetchSemanticsNodes().isNotEmpty() }
        compose.onNode(hasText(block.title) and hasAnyAncestor(hasTestTag("note-reader"))).performScrollTo()
        compose.runOnIdle {
            val native = textViews(compose.activity.findViewById(android.R.id.content)).single { it.text.toString() == block.text }
            assertTrue(native.isTextSelectable)
            assertEquals(block.text, native.text.toString())
            val styled = native.text as Spanned
            assertTrue(styled.getSpans(0, styled.length, BackgroundColorSpan::class.java).any {
                styled.subSequence(styled.getSpanStart(it), styled.getSpanEnd(it)).toString() == quote
            })
            val selection = native.text as Spannable
            val start = block.text.indexOf(quote)
            Selection.setSelection(selection, start, start + quote.length)
            assertEquals(quote, native.text.subSequence(native.selectionStart, native.selectionEnd).toString())
            native.layout?.let { layout -> repeat(layout.lineCount) { assertEquals(0, layout.getEllipsisCount(it)) } }
            Selection.removeSelection(selection)
        }
        capture("note")
        assertEquals(before.annotations, repo.state.value.annotations)
        assertEquals(before.noteBookmarks, repo.state.value.noteBookmarks)
        assertEquals(before.reviews, repo.state.value.reviews)
        assertEquals(before.submissions, repo.state.value.submissions)
        assertEquals(note.version, repo.state.value.notes.single { it.noteId == note.id }.readVersion)
        assertEquals(block, repo.pack.notes.single { it.id == note.id }.blocks.single { it.id == block.id })
    }

    /** A real menu invokes the existing callback; no long-press timing or external mock library. */
    private class SelectionActionMode(private val native: TextView) : ActionMode() {
        private val items = PopupMenu(native.context, native).menu
        var finished = false
            private set
        override fun setTitle(title: CharSequence?) = Unit
        override fun setTitle(resId: Int) = Unit
        override fun setSubtitle(subtitle: CharSequence?) = Unit
        override fun setSubtitle(resId: Int) = Unit
        override fun setCustomView(view: View?) = Unit
        override fun invalidate() = Unit
        override fun finish() { finished = true }
        override fun getMenu(): Menu = items
        override fun getTitle(): CharSequence? = null
        override fun getSubtitle(): CharSequence? = null
        override fun getCustomView(): View? = null
        override fun getMenuInflater() = MenuInflater(native.context)
    }

    @Test fun projectedNoteParagraphsKeepCrossBoundaryAnnotationAndLatestSelectionCallback() {
        val first = repo.pack.notes.single { it.id == "note-M01" }.blocks.single { it.id == "M01-03" }
        val second = repo.pack.notes.single { it.id == "note-S03" }.blocks.single { it.id == "S03-supp-instr-example" }
        fun boundaryQuote(source: String): String {
            val startFragment = BodyTextOverrides.entries.getValue(source).paragraphStarts.first()
            val cut = source.indexOf(startFragment)
            assertTrue("Expected an interior editorial paragraph boundary", cut > 0)
            return source.substring((cut - 18).coerceAtLeast(0), (cut + 28).coerceAtMost(source.length))
        }
        val bodies = listOf(first.text, second.text)
        assertTrue(bodies.all { NoteTextProjection.from(it).text != it })
        val selectedSource = mutableStateOf(first.text)
        val callbacks = mutableListOf<Triple<String, String, String>>()
        compose.runOnUiThread { componentPage.value = {
            val source = selectedSource.value
            val quote = boundaryQuote(source)
            val annotation = Annotation("body-paragraph-highlight", "source-note", "source-block", quote, "경계에 걸친 기존 메모", "highlight", 1)
            Surface(Modifier.fillMaxSize()) {
                Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("문단 구분 · 기존 필기 보존", style = MaterialTheme.typography.titleLarge)
                    SelectableNoteText(source, listOf(annotation), 1f, { rawQuote, style ->
                        callbacks += Triple(source, rawQuote, style)
                    })
                }
            }
        } }
        compose.waitForIdle()
        lateinit var reusedView: TextView
        bodies.forEachIndexed { index, source ->
            if (index > 0) {
                compose.runOnUiThread { selectedSource.value = source }
                compose.waitForIdle()
            }
            compose.runOnIdle {
                val projection = NoteTextProjection.from(source)
                val native = textViews(compose.activity.findViewById(android.R.id.content)).single { it.text.toString() == projection.text }
                if (index == 0) reusedView = native else assertSame("Changing a body must exercise the existing TextView callback", reusedView, native)
                assertTrue(native.isTextSelectable)
                assertEquals(projection.text, native.text.toString())
                assertTrue("An editorial break must be visible in the native text", native.text.contains("\n\n"))
                val quote = boundaryQuote(source)
                val styled = native.text as Spanned
                val highlight = styled.getSpans(0, styled.length, BackgroundColorSpan::class.java).single()
                val from = styled.getSpanStart(highlight)
                val to = styled.getSpanEnd(highlight)
                assertTrue("The existing highlight should cross the added paragraph separator", styled.subSequence(from, to).contains("\n\n"))
                assertEquals(quote, projection.sourceQuote(from, to))
                assertEquals(source.indexOf(quote), source.indexOf(projection.sourceQuote(from, to)))
                Selection.setSelection(native.text as Spannable, from, to)
                val mode = SelectionActionMode(native)
                val callback = native.customSelectionActionModeCallback ?: error("Native selection callback is missing")
                assertTrue(callback.onCreateActionMode(mode, mode.menu))
                val actionId = if (index == 0) 812 else 811
                assertTrue(callback.onActionItemClicked(mode, mode.menu.findItem(actionId)))
                assertTrue(mode.finished)
                assertEquals(Triple(source, quote, if (index == 0) "memo" else "underline"), callbacks.last())
                assertFalse("Saved quote must not contain display-only paragraph newlines", callbacks.last().second.contains("\n\n"))
                // Selecting to the rendered end must map past every added newline to the original
                // end, including after this exact AndroidView has been rebound to a different body.
                Selection.setSelection(native.text as Spannable, 0, native.text.length)
                val selectAllMode = SelectionActionMode(native)
                assertTrue(callback.onCreateActionMode(selectAllMode, selectAllMode.menu))
                assertTrue(callback.onActionItemClicked(selectAllMode, selectAllMode.menu.findItem(810)))
                assertTrue(selectAllMode.finished)
                assertEquals(Triple(source, source, "highlight"), callbacks.last())
                native.layout?.let { layout -> repeat(layout.lineCount) { assertEquals(0, layout.getEllipsisCount(it)) } }
                Selection.removeSelection(native.text as Spannable)
            }
            capture(if (index == 0) "note-paragraphs" else "note-paragraphs-updated")
        }
        assertEquals(4, callbacks.size)
        assertEquals(first, repo.pack.notes.single { it.id == "note-M01" }.blocks.single { it.id == first.id })
        assertEquals(second, repo.pack.notes.single { it.id == "note-S03" }.blocks.single { it.id == second.id })
        assertTrue(repo.state.value.annotations.isEmpty())
        assertTrue(repo.state.value.submissions.isEmpty())
    }

    @Test fun existingQuestionExplanationRemainsHiddenUntilGradingAndKeepsSubmission() {
        val question = repo.pack.practice().first { it.sql.isNullOrBlank() && it.explanation.steps.isNotEmpty() }
        runBlocking { repo.update {
            StudyEngine.createSession(it, repo.pack, listOf(question), "batch", "본문 표시 검수", System.currentTimeMillis(), android.os.SystemClock.elapsedRealtime(), 0, 73)
                .let { s -> s.copy(settings = s.settings.copy(explanationExpanded = true)) }
        } }
        compose.onNode(hasTestTag("home-compact") or hasTestTag("home-wide"))
            .performScrollToNode(hasText("풀던 문제 이어서") and hasClickAction())
        compose.onNode(hasText("풀던 문제 이어서") and hasClickAction()).performClick()
        compose.onNodeWithText(question.explanation.summary).assertDoesNotExist()
        val beforeGrade = repo.state.value.sessions.last()
        runBlocking { repo.update { state ->
            StudyEngine.grade(StudyEngine.select(state, beforeGrade.id, 0, question.correctChoiceIds.first()), beforeGrade.id, 0, System.currentTimeMillis())
        } }
        compose.waitUntil(10_000) { compose.onAllNodesWithText(question.explanation.summary).fetchSemanticsNodes().isNotEmpty() }
        compose.onAllNodesWithText(question.explanation.summary)[0].performScrollTo().assertIsDisplayed()
        val submitted = repo.state.value.submissions.single()
        capture("question-explanation")
        compose.onNodeWithText(question.explanation.steps.first().title).performScrollTo().assertIsDisplayed()
        capture("question-step")
        assertEquals(submitted, repo.state.value.submissions.single())
        assertEquals(question, repo.state.value.sessions.last().items.single().question)
        assertEquals(question, repo.pack.questions.single { it.id == question.id })
    }

    @Test fun longInlineCodeWrapsAndWideTableScrollsWithoutChangingSqlSpaces() {
        val identifier = "VERY_LONG_STUDENT_CONTACT_PHONE_IDENTIFIER_20261013"
        val prose = "컬럼 $identifier 에 저장된 값은 ' A B '이다. 문자열 안의 앞뒤 공백과 사이 공백도 데이터다.\n\n결과를 확인할 때 원본은 변경되지 않는다."
        val sql = "SELECT ' A B ' AS NAME,\n       '010-****-1003' AS PHONE\nFROM STUDENT;"
        val table = DataTable("긴 컬럼과 전화번호", listOf(identifier, "PHONE", "ID", "원본 문자열"), listOf(listOf("양지훈", "010-****-1003", "1003", " A B ")))
        compose.runOnUiThread { componentPage.value = {
            Surface(Modifier.fillMaxSize()) {
                Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp).testTag("body-component-page"), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("좁은 본문 · 긴 코드와 표", style = MaterialTheme.typography.titleLarge)
                    StudyBodyText(prose, Modifier.fillMaxWidth().testTag("body-long-inline"), emphasis = listOf("원본은 변경되지 않는다"), inlineCodes = listOf(identifier, "' A B '"))
                    Box(Modifier.fillMaxWidth().testTag("body-wide-table")) { ReadingTable(table) }
                    Box(Modifier.fillMaxWidth().testTag("body-sql-source")) { SqlBlock(sql, false, {}) }
                }
            }
        } }
        compose.waitForIdle()
        assertBoldPhrase("body-long-inline", "원본은 변경되지 않는다")
        val visible = textInside("body-long-inline").joinToString("\n") { it.text }
        assertTrue(visible.contains(identifier))
        assertTrue(visible.contains("' A B '"))
        assertFalse(visible.contains("**"))
        assertTextLayoutsDoNotClip("body-long-inline")
        val viewport = compose.onNodeWithTag("body-wide-table").fetchSemanticsNode().boundsInRoot
        val page = compose.onNodeWithTag("body-component-page").fetchSemanticsNode().boundsInRoot
        assertTrue("A wide table must remain inside the page viewport", viewport.width <= page.width + 1f)
        val scrollables = compose.onAllNodes(SemanticsMatcher.keyIsDefined(SemanticsProperties.HorizontalScrollAxisRange) and hasAnyAncestor(hasTestTag("body-wide-table")), useUnmergedTree = true).fetchSemanticsNodes()
        assertTrue("The wide table needs its own horizontal scrolling surface", scrollables.isNotEmpty())
        capture("long-inline-table")
        compose.onNodeWithTag("body-sql-source").performScrollTo()
        val renderedSql = textInside("body-sql-source").map { it.text }.first { it.contains("SELECT ' A B '") }
        assertEquals(sql, renderedSql.lines().joinToString("\n") { it.replaceFirst(Regex("^\\d+  "), "") })
        capture("sql-whitespace")
        assertTrue(repo.state.value.submissions.isEmpty())
    }
}
