package kr.sqld.study

import android.os.SystemClock
import android.view.InputDevice
import android.view.MotionEvent
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith

/** Actual View dispatch with SDK-created buttonState events; not physical Galaxy Tab/S Pen proof.
 * MotionEvent actionButton has no public setter; the app deliberately uses buttonState. */
@RunWith(AndroidJUnit4::class)
class StylusButtonTest {
    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val sql = "SELECT COUNT(*) FROM T"
    private val sourceId = "synthetic-stylus-button"
    private val density get() = instrumentation.targetContext.resources.displayMetrics.density

    private inner class Fixture(
        tool: String = "pen", color: Long = 0xff172d45L,
        penWidth: Float = 2.5f, opacity: Float = 1f, finger: Boolean = false
    ) {
        val original = InkStroke("existing-stroke", points = listOf(InkPoint(60f, 100f), InkPoint(100f, 100f)))
        var saved = InkStore.add(InkStore.empty(sourceId, sql), original, 1L)
        val view = InkSqlView(instrumentation.targetContext).apply {
            layout(0, 0, (600f * density).toInt(), (300f * density).toInt())
            configure(sql, saved, emptyList(), tool, color, penWidth, opacity, finger,
                1f, 0f, 0f, { saved = it }, { _, _ -> }, { throw AssertionError(it) })
        }
        fun visible() = InkStore.visibleStrokes(saved)
        fun send(action: Int, x: Float, y: Float, buttons: Int = 0,
                 tool: Int = MotionEvent.TOOL_TYPE_STYLUS, generic: Boolean = false) {
            event(action, listOf(Pointer(0, tool, x, y)), buttons).also {
                if (generic) view.dispatchGenericMotionEvent(it) else view.dispatchTouchEvent(it)
                it.recycle()
            }
        }
    }

    private data class Pointer(val id: Int, val tool: Int, val x: Float, val y: Float)
    private fun event(action: Int, pointers: List<Pointer>, buttons: Int = 0): MotionEvent {
        val properties = pointers.map { p -> MotionEvent.PointerProperties().apply { id = p.id; toolType = p.tool } }.toTypedArray()
        val coords = pointers.map { p -> MotionEvent.PointerCoords().apply {
            x = p.x * density; y = p.y * density; pressure = .75f; size = .1f
        } }.toTypedArray()
        val now = SystemClock.uptimeMillis()
        val stylus = pointers.any { it.tool == MotionEvent.TOOL_TYPE_STYLUS || it.tool == MotionEvent.TOOL_TYPE_ERASER }
        return MotionEvent.obtain(now, now, action, pointers.size, properties, coords,
            0, buttons, 1f, 1f, 0, 0,
            if (stylus) InputDevice.SOURCE_STYLUS else InputDevice.SOURCE_TOUCHSCREEN, 0)
    }

    @Test fun heldPrimaryButtonErasesAndNextContactWritesWithoutChangingSource() { instrumentation.runOnMainSync {
        val f = Fixture()
        f.send(MotionEvent.ACTION_DOWN, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY)
        assertEquals(listOf(f.original), f.visible()) // Pending erase is not a saved edit yet.
        f.send(MotionEvent.ACTION_UP, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY)
        assertTrue(f.visible().isEmpty())
        f.send(MotionEvent.ACTION_DOWN, 140f, 100f)
        f.send(MotionEvent.ACTION_UP, 170f, 100f)
        assertEquals("pen", f.visible().single().tool)
        assertEquals(140f, f.visible().single().points.first().x, .01f)
        assertTrue(InkStore.matches(f.saved, sourceId, sql))
    } }

    @Test fun secondaryAndLegacyStylusButtonMasksAlsoTemporarilyErase() { instrumentation.runOnMainSync {
        listOf(MotionEvent.BUTTON_STYLUS_SECONDARY, MotionEvent.BUTTON_SECONDARY).forEach { button ->
            val f = Fixture()
            f.send(MotionEvent.ACTION_DOWN, 80f, 100f, button)
            f.send(MotionEvent.ACTION_UP, 80f, 100f, button)
            assertTrue("Button mask $button must erase a stylus contact", f.visible().isEmpty())
            f.send(MotionEvent.ACTION_DOWN, 140f, 100f)
            f.send(MotionEvent.ACTION_UP, 170f, 100f)
            assertEquals("pen", f.visible().single().tool)
        }
    } }

    @Test fun genericPressAndReleaseDuringContactSplitSegmentsWithoutDrawingAcrossErase() { instrumentation.runOnMainSync {
        val f = Fixture()
        f.send(MotionEvent.ACTION_DOWN, 20f, 60f)
        f.send(MotionEvent.ACTION_MOVE, 40f, 60f)
        f.send(MotionEvent.ACTION_BUTTON_PRESS, 40f, 60f, MotionEvent.BUTTON_STYLUS_PRIMARY,
            generic = true)
        assertTrue("Written segment must survive pressing the button", f.visible().any { it.id != f.original.id })
        f.send(MotionEvent.ACTION_MOVE, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY)
        f.send(MotionEvent.ACTION_BUTTON_RELEASE, 140f, 100f, generic = true)
        f.send(MotionEvent.ACTION_MOVE, 160f, 100f)
        f.send(MotionEvent.ACTION_UP, 180f, 100f)
        val strokes = f.visible()
        assertEquals(2, strokes.size)
        assertFalse(strokes.any { it.id == f.original.id })
        assertTrue(strokes[0].points.all { it.x <= 40.01f && it.y < 70f })
        assertTrue("Released pen must not bridge back across erased coordinates", strokes[1].points.all { it.x >= 139.99f })
        assertEquals(listOf(f.original.id), f.saved.edits.single { it.erasedIds.isNotEmpty() }.erasedIds)
    } }

    @Test fun contactButtonStateAloneCanPressAndReleaseWithinOneStroke() { instrumentation.runOnMainSync {
        val f = Fixture()
        f.send(MotionEvent.ACTION_DOWN, 20f, 60f)
        f.send(MotionEvent.ACTION_MOVE, 40f, 60f)
        f.send(MotionEvent.ACTION_MOVE, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY)
        f.send(MotionEvent.ACTION_MOVE, 140f, 100f)
        f.send(MotionEvent.ACTION_UP, 180f, 100f)
        val strokes = f.visible()
        assertEquals(2, strokes.size)
        assertTrue(strokes[0].points.all { it.x <= 40.01f })
        assertTrue(strokes[1].points.all { it.x >= 139.99f })
        assertFalse(strokes.any { it.id == f.original.id })
    } }

    @Test fun hoverNeverErasesAndContactButtonStateOverridesStaleHover() { instrumentation.runOnMainSync {
        val f = Fixture()
        f.send(MotionEvent.ACTION_HOVER_ENTER, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY, generic = true)
        f.send(MotionEvent.ACTION_BUTTON_PRESS, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY,
            generic = true)
        f.send(MotionEvent.ACTION_HOVER_MOVE, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY, generic = true)
        assertEquals(1, f.saved.edits.size)
        f.send(MotionEvent.ACTION_DOWN, 80f, 100f)
        f.send(MotionEvent.ACTION_UP, 90f, 100f)
        assertTrue("Unpressed contact must write even after a pressed hover", f.visible().any { it.id == f.original.id })
        assertEquals(2, f.visible().size)

        val held = Fixture()
        held.send(MotionEvent.ACTION_HOVER_MOVE, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY, generic = true)
        held.send(MotionEvent.ACTION_DOWN, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY)
        held.send(MotionEvent.ACTION_UP, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY)
        assertTrue(held.visible().isEmpty())
    } }

    @Test fun nonStylusSecondaryButtonDoesNotEraseWithFingerInkEnabled() { instrumentation.runOnMainSync {
        val f = Fixture(finger = true)
        f.send(MotionEvent.ACTION_DOWN, 80f, 100f, MotionEvent.BUTTON_SECONDARY, MotionEvent.TOOL_TYPE_FINGER)
        f.send(MotionEvent.ACTION_UP, 90f, 100f, MotionEvent.BUTTON_SECONDARY, MotionEvent.TOOL_TYPE_FINGER)
        assertTrue(f.visible().any { it.id == f.original.id })
        assertEquals(2, f.visible().size)
        assertEquals("pen", f.visible().last().tool)
    } }

    @Test fun buttonReleaseRestoresHighlighterColorWidthAndOpacity() { instrumentation.runOnMainSync {
        val color = 0xff6a1b9aL
        val f = Fixture("highlighter", color, 11f, .25f)
        f.send(MotionEvent.ACTION_DOWN, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY)
        f.send(MotionEvent.ACTION_MOVE, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY)
        f.send(MotionEvent.ACTION_BUTTON_RELEASE, 140f, 100f, generic = true)
        f.send(MotionEvent.ACTION_MOVE, 160f, 100f)
        f.send(MotionEvent.ACTION_UP, 180f, 100f)
        val stroke = f.visible().single()
        assertEquals("highlighter", stroke.tool)
        assertEquals(color, stroke.color)
        assertEquals(11f, stroke.width, 0f)
        assertEquals(.25f, stroke.opacity, 0f)
        assertTrue(stroke.points.all { it.x >= 139.99f })
    } }

    @Test fun canceledHeldButtonEraseDiscardsOnlyThePendingErase() { instrumentation.runOnMainSync {
        val f = Fixture()
        val before = f.saved
        f.send(MotionEvent.ACTION_DOWN, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY)
        f.send(MotionEvent.ACTION_MOVE, 90f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY)
        f.send(MotionEvent.ACTION_CANCEL, 90f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY)
        assertEquals(before, f.saved)
        f.send(MotionEvent.ACTION_DOWN, 140f, 100f)
        f.send(MotionEvent.ACTION_UP, 170f, 100f)
        assertEquals(2, f.visible().size)
        assertEquals("pen", f.visible().last().tool)
    } }

    @Test fun undoAfterButtonEraseRestoresTheExactOriginalStroke() { instrumentation.runOnMainSync {
        val f = Fixture()
        f.send(MotionEvent.ACTION_DOWN, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY)
        f.send(MotionEvent.ACTION_UP, 80f, 100f, MotionEvent.BUTTON_STYLUS_PRIMARY)
        assertTrue(f.visible().isEmpty())
        val restored = InkStore.undo(f.saved, 3L)
        assertEquals(listOf(f.original), InkStore.visibleStrokes(restored))
        assertTrue(InkStore.matches(restored, sourceId, sql))
        InkStore.validateDocument(restored)
    } }

    @Test fun palmPointerWhileStylusWritesDoesNotCreateOrJoinAnotherStroke() { instrumentation.runOnMainSync {
        val f = Fixture()
        f.send(MotionEvent.ACTION_DOWN, 20f, 60f)
        fun pair(action: Int, stylusX: Float) {
            event(action, listOf(Pointer(0, MotionEvent.TOOL_TYPE_STYLUS, stylusX, 60f),
                Pointer(1, MotionEvent.TOOL_TYPE_FINGER, 80f, 100f))).also {
                f.view.dispatchTouchEvent(it); it.recycle()
            }
        }
        pair(MotionEvent.ACTION_POINTER_DOWN or (1 shl MotionEvent.ACTION_POINTER_INDEX_SHIFT), 30f)
        event(MotionEvent.ACTION_MOVE, listOf(Pointer(0, MotionEvent.TOOL_TYPE_STYLUS, 45f, 60f),
            Pointer(1, MotionEvent.TOOL_TYPE_FINGER, 80f, 100f))).also { f.view.dispatchTouchEvent(it); it.recycle() }
        pair(MotionEvent.ACTION_POINTER_UP or (1 shl MotionEvent.ACTION_POINTER_INDEX_SHIFT), 45f)
        f.send(MotionEvent.ACTION_MOVE, 60f, 60f)
        f.send(MotionEvent.ACTION_UP, 70f, 60f)
        assertEquals(2, f.visible().size)
        assertTrue(f.visible().any { it.id == f.original.id })
        val writing = f.visible().single { it.id != f.original.id }
        assertTrue(writing.points.all { it.y < 70f })
    } }

    @Test fun hoveringStylusButtonCannotTurnAnActiveFingerStrokeIntoAnEraser() { instrumentation.runOnMainSync {
        val f=Fixture(finger=true)
        f.send(MotionEvent.ACTION_DOWN,20f,60f,tool=MotionEvent.TOOL_TYPE_FINGER)
        f.send(MotionEvent.ACTION_BUTTON_PRESS,80f,100f,MotionEvent.BUTTON_STYLUS_PRIMARY,
            generic=true)
        f.send(MotionEvent.ACTION_MOVE,80f,100f,tool=MotionEvent.TOOL_TYPE_FINGER)
        f.send(MotionEvent.ACTION_UP,90f,100f,tool=MotionEvent.TOOL_TYPE_FINGER)
        assertEquals(2,f.visible().size)
        assertTrue(f.visible().any{it.id==f.original.id})
    } }

    @Test fun releasingButtonAsTipLiftsDoesNotLeaveAPenDot() { instrumentation.runOnMainSync {
        val f=Fixture()
        f.send(MotionEvent.ACTION_DOWN,80f,100f,MotionEvent.BUTTON_STYLUS_PRIMARY)
        f.send(MotionEvent.ACTION_UP,80f,100f)
        assertTrue(f.visible().isEmpty())
        assertEquals(1,f.saved.edits.count{it.erasedIds.isNotEmpty()})
    } }

    @Test fun focusLossCancelsPendingEraseAndNewContactUsesItsOwnButtonState() { instrumentation.runOnMainSync {
        val f=Fixture()
        val before=f.saved
        f.send(MotionEvent.ACTION_DOWN,80f,100f,MotionEvent.BUTTON_STYLUS_PRIMARY)
        f.view.onWindowFocusChanged(false)
        assertEquals(before,f.saved)
        f.send(MotionEvent.ACTION_DOWN,140f,100f)
        f.send(MotionEvent.ACTION_UP,170f,100f)
        assertEquals(2,f.visible().size)
        assertEquals("pen",f.visible().last().tool)
    } }
}
