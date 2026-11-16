package kr.sqld.study

import android.os.SystemClock
import android.view.InputDevice
import android.view.MotionEvent
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith

/** Synthetic MotionEvents verify routing and coordinates, not a physical S Pen or palm sensor. */
@RunWith(AndroidJUnit4::class)
class InkSurfaceTest {
    private val instrumentation=InstrumentationRegistry.getInstrumentation()
    private fun event(action:Int,x:Float,y:Float,tool:Int,flags:Int=0):MotionEvent {
        val properties=MotionEvent.PointerProperties().apply{id=0;toolType=tool}
        val coords=MotionEvent.PointerCoords().apply{this.x=x;this.y=y;pressure=.75f;size=.1f}
        val now=SystemClock.uptimeMillis()
        return MotionEvent.obtain(now,now,action,1,arrayOf(properties),arrayOf(coords),0,0,1f,1f,0,0,if(tool==MotionEvent.TOOL_TYPE_STYLUS||tool==MotionEvent.TOOL_TYPE_ERASER)InputDevice.SOURCE_STYLUS else InputDevice.SOURCE_TOUCHSCREEN,flags)
    }
    private fun send(view:InkSqlView,action:Int,x:Float,y:Float,tool:Int=MotionEvent.TOOL_TYPE_STYLUS,flags:Int=0){event(action,x,y,tool,flags).also{view.dispatchTouchEvent(it);it.recycle()}}
    private fun configure(view:InkSqlView,doc:InkDocument,finger:Boolean=false,zoom:Float=1f,x:Float=0f,y:Float=0f,onChange:(InkDocument)->Unit){
        view.configure("SELECT COUNT(*) FROM T",doc,listOf(7..14),"pen",0xff172d45L,2.5f,1f,finger,zoom,x,y,onChange,{_,_->},{throw AssertionError(it)})
    }
    @Test fun stylusStrokeCommitsOnlyAtPenUpAndDefaultFingerDoesNotWrite(){instrumentation.runOnMainSync {
        val view=InkSqlView(instrumentation.targetContext);view.layout(0,0,600,300)
        var saved=InkStore.empty("test","SELECT COUNT(*) FROM T");configure(view,saved){saved=it}
        send(view,MotionEvent.ACTION_DOWN,30f,40f,MotionEvent.TOOL_TYPE_FINGER);send(view,MotionEvent.ACTION_MOVE,60f,50f,MotionEvent.TOOL_TYPE_FINGER);send(view,MotionEvent.ACTION_UP,70f,50f,MotionEvent.TOOL_TYPE_FINGER)
        assertTrue(saved.edits.isEmpty())
        send(view,MotionEvent.ACTION_DOWN,30f,40f);send(view,MotionEvent.ACTION_MOVE,60f,50f)
        assertTrue(saved.edits.isEmpty())
        send(view,MotionEvent.ACTION_UP,70f,50f)
        assertEquals(1,saved.cursor);assertEquals(.75f,InkStore.visibleStrokes(saved).single().points.first().pressure,.001f)
    }}
    @Test fun cancellationDiscardsPendingStrokeAndFingerOptInWrites(){instrumentation.runOnMainSync {
        val view=InkSqlView(instrumentation.targetContext);view.layout(0,0,600,300)
        var saved=InkStore.empty("test","SELECT COUNT(*) FROM T");configure(view,saved,true){saved=it}
        send(view,MotionEvent.ACTION_DOWN,30f,40f);send(view,MotionEvent.ACTION_MOVE,60f,50f);send(view,MotionEvent.ACTION_CANCEL,70f,50f)
        assertTrue(saved.edits.isEmpty())
        send(view,MotionEvent.ACTION_DOWN,30f,40f,MotionEvent.TOOL_TYPE_FINGER);send(view,MotionEvent.ACTION_UP,70f,50f,MotionEvent.TOOL_TYPE_FINGER)
        assertEquals(1,saved.cursor)
    }}
    @Test fun eraserUsesStrokeHitAndUndoCanRestoreIt(){instrumentation.runOnMainSync {
        val view=InkSqlView(instrumentation.targetContext);view.layout(0,0,600,300)
        var saved=InkStore.empty("test","SELECT COUNT(*) FROM T");configure(view,saved){saved=it}
        send(view,MotionEvent.ACTION_DOWN,30f,40f);send(view,MotionEvent.ACTION_UP,100f,40f)
        val original=InkStore.visibleStrokes(saved)
        send(view,MotionEvent.ACTION_DOWN,60f,40f,MotionEvent.TOOL_TYPE_ERASER);send(view,MotionEvent.ACTION_UP,60f,40f,MotionEvent.TOOL_TYPE_ERASER)
        assertTrue(InkStore.visibleStrokes(saved).isEmpty());assertEquals(original,InkStore.visibleStrokes(InkStore.undo(saved)))
    }}
    @Test fun zoomResizeAndHighlightChangeKeepDocumentCoordinates(){instrumentation.runOnMainSync {
        val view=InkSqlView(instrumentation.targetContext);view.layout(0,0,600,300)
        val density=instrumentation.targetContext.resources.displayMetrics.density
        var saved=InkStore.empty("test","SELECT COUNT(*) FROM T");configure(view,saved,zoom=2f){saved=it}
        send(view,MotionEvent.ACTION_DOWN,40f*density,60f*density);send(view,MotionEvent.ACTION_UP,80f*density,60f*density)
        val before=InkStore.visibleStrokes(saved)
        assertEquals(20f,before.single().points.first().x,.001f);assertEquals(30f,before.single().points.first().y,.001f)
        view.layout(0,0,300,600)
        view.configure("SELECT COUNT(*) FROM T",saved,listOf(16..19),"pen",0xff172d45L,2.5f,1f,false,1f,0f,0f,{saved=it},{_,_->},{throw AssertionError(it)})
        assertEquals(before,InkStore.visibleStrokes(saved))
    }}
    @Test fun longCodeInitialFocusBecomesVisibleAfterLayoutWithoutChangingInk(){instrumentation.runOnMainSync {
        val sql=(1..40).joinToString("\n"){"-- line $it"}+"\nWHERE n > 3"
        val doc=InkStore.empty("long-code",sql)
        val view=InkSqlView(instrumentation.targetContext)
        var panY=0f;var changes=0
        val start=sql.indexOf("WHERE")
        view.configure(sql,doc,listOf(start..sql.lastIndex),"pen",0xff172d45L,2.5f,1f,false,1f,0f,0f,{changes++},{_,y->panY=y},{throw AssertionError(it)})
        view.layout(0,0,600,300)
        assertTrue(panY>0f);assertEquals(0,changes);assertTrue(doc.edits.isEmpty())
    }}
    @Test fun platformCanceledPenUpDoesNotCommitAPalmRejectedStroke(){instrumentation.runOnMainSync {
        if(android.os.Build.VERSION.SDK_INT>=33){
            val view=InkSqlView(instrumentation.targetContext);view.layout(0,0,600,300)
            var saved=InkStore.empty("test","SELECT COUNT(*) FROM T");configure(view,saved){saved=it}
            send(view,MotionEvent.ACTION_DOWN,30f,40f);send(view,MotionEvent.ACTION_UP,70f,50f,flags=MotionEvent.FLAG_CANCELED)
            assertTrue(saved.edits.isEmpty())
        }
    }}
}
