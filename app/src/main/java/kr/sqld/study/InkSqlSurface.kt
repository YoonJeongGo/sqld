package kr.sqld.study

import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Typeface
import android.os.Build
import android.view.MotionEvent
import android.view.View
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.luminance
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import java.util.UUID
import kotlin.math.abs
import kotlin.math.ceil
import kotlin.math.floor
import kotlin.math.max
import kotlin.math.min

/** Caller supplies a bounded height and retains pending documents until the repository save succeeds. */
@OptIn(ExperimentalLayoutApi::class)
@Composable fun InkSqlSurface(
    sql:String,sourceId:String,ink:InkDocument?,activeRanges:List<IntRange> = emptyList(),
    onInkChange:(InkDocument)->Unit,modifier:Modifier=Modifier,textScale:Float=1f,
    saveStatus:String?=null,onRetrySave:(()->Unit)?=null
) {
    val id=remember(sourceId,sql){InkStore.documentId(sourceId,sql)}
    val document=remember(id,ink){ink?.takeIf{InkStore.matches(it,sourceId,sql)}?:InkStore.empty(sourceId,sql)}
    var settingsOpen by rememberSaveable(id){mutableStateOf(false)}
    var tool by rememberSaveable(id){mutableStateOf("pen")}
    var color by rememberSaveable(id){mutableLongStateOf(0xff172d45L)}
    var width by rememberSaveable(id){mutableFloatStateOf(2.5f)}
    var opacity by rememberSaveable(id){mutableFloatStateOf(1f)}
    var fingerInk by rememberSaveable(id){mutableStateOf(false)}
    var zoom by rememberSaveable(id){mutableFloatStateOf(1f)}
    var panX by rememberSaveable(id){mutableFloatStateOf(0f)}
    var panY by rememberSaveable(id){mutableFloatStateOf(0f)}
    var inputError by remember(id){mutableStateOf<String?>(null)}
    var temporaryErase by remember(id){mutableStateOf(false)}
    val systemScale=LocalDensity.current.fontScale
    val clipboard=LocalClipboardManager.current
    Surface(modifier,border=BorderStroke(1.dp,MaterialTheme.colorScheme.outlineVariant),shape=RoundedCornerShape(12.dp),color=Color.White) {
        Column {
            Row(Modifier.fillMaxWidth().heightIn(min=48.dp).background(MaterialTheme.colorScheme.surfaceContainer).padding(start=12.dp,end=4.dp),verticalAlignment=Alignment.CenterVertically) {
                Text("SQL",Modifier.weight(1f),style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.onSurface,maxLines=1,overflow=TextOverflow.Ellipsis)
                IconButton(onClick={clipboard.setText(AnnotatedString(sql))},modifier=Modifier.size(48.dp)){Icon(Icons.Outlined.ContentCopy,"SQL 복사")}
                IconButton(onClick={zoom=(zoom-.2f).coerceAtLeast(.6f)},enabled=zoom>.6f,modifier=Modifier.size(48.dp)){Icon(Icons.Outlined.Remove,"SQL 축소")}
                IconButton(onClick={zoom=(zoom+.2f).coerceAtMost(2.4f)},enabled=zoom<2.4f,modifier=Modifier.size(48.dp)){Icon(Icons.Outlined.Add,"SQL 확대")}
                IconButton(onClick={settingsOpen=true},modifier=Modifier.size(48.dp).testTag("ink-settings").semantics{contentDescription="펜 설정"}) {
                    Box(Modifier.size(34.dp).background(Color(color),CircleShape),contentAlignment=Alignment.Center){Icon(if(temporaryErase)Icons.Outlined.Backspace else Icons.Outlined.Edit,null,tint=if(Color(color).luminance()>.5f)Color.Black else Color.White,modifier=Modifier.size(19.dp))}
                }
            }
            AndroidView(factory={InkSqlView(it)},modifier=Modifier.fillMaxWidth().weight(1f).testTag("ink-code-surface"),update={view->
                view.configure(sql,document,activeRanges,tool,color,width,opacity,fingerInk,zoom*systemScale*textScale,panX,panY,
                    onChange={inputError=null;onInkChange(it)},onPan={x,y->panX=x;panY=y},onError={inputError=it},onTemporaryEraseChange={temporaryErase=it})
            })
            // Fixed height; the settings dialog keeps the full status available at large text sizes.
            Text(if(temporaryErase)"임시 획 지우개 · 원래 펜 설정 유지"else saveStatus?:if(tool=="eraser")"획 지우개 · 손가락으로 상하좌우 이동"else if(fingerInk)"손가락 필기 켜짐 · 두 손가락으로 이동" else "펜으로 필기 · 손가락으로 상하좌우 이동",
                Modifier.fillMaxWidth().height(32.dp).background(MaterialTheme.colorScheme.surfaceContainer).padding(horizontal=10.dp,vertical=4.dp),
                style=MaterialTheme.typography.labelSmall,color=MaterialTheme.colorScheme.onSurfaceVariant,maxLines=1,overflow=TextOverflow.Ellipsis)
        }
    }
    inputError?.let { message -> AlertDialog(onDismissRequest={inputError=null},title={Text("필기 안내")},text={Text(message)},confirmButton={TextButton(onClick={inputError=null}){Text("확인")}}) }
    if(settingsOpen)AlertDialog(onDismissRequest={settingsOpen=false},title={Text("펜 설정")},text={
        Column(Modifier.verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(10.dp)) {
            saveStatus?.let{Text(it,style=MaterialTheme.typography.bodySmall)}
            if(onRetrySave!=null)OutlinedButton(onClick=onRetrySave,modifier=Modifier.heightIn(min=48.dp).testTag("ink-retry-save")){Text("필기 저장 다시 시도")}
            FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(4.dp)) {
                listOf("pen" to "펜","highlighter" to "형광펜","eraser" to "획 지우개").forEach{(value,label)->
                    FilterChip(selected=tool==value,onClick={tool=value;if(value=="highlighter"){opacity=.3f;width=12f}else if(value=="pen"){opacity=1f;width=2.5f}},label={Text(label)},modifier=Modifier.heightIn(min=48.dp))
                }
            }
            FlowRow(horizontalArrangement=Arrangement.spacedBy(6.dp),verticalArrangement=Arrangement.spacedBy(4.dp)) {
                listOf(0xff172d45L,0xff1565c0L,0xffc62828L,0xff2e7d32L,0xff6a1b9aL,0xffffc107L).forEach{preset->
                    Box(Modifier.size(48.dp).clickable{color=preset}.semantics{contentDescription="펜 색상 #${preset.toString(16).takeLast(6).uppercase()}"},contentAlignment=Alignment.Center){
                        Box(Modifier.size(32.dp).background(Color(preset),CircleShape).border(if(color==preset)3.dp else 1.dp,if(color==preset)MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline,CircleShape))
                    }
                }
            }
            var hex by rememberSaveable{mutableStateOf(color.toString(16).takeLast(6).uppercase())}
            LaunchedEffect(color){hex=color.toString(16).takeLast(6).uppercase()}
            OutlinedTextField(value=hex,onValueChange={value->hex=value.removePrefix("#").take(6);if(hex.matches(Regex("[0-9A-Fa-f]{6}")))color=0xff000000L or hex.toLong(16)},label={Text("직접 색상 · HEX 6자리")},singleLine=true,modifier=Modifier.fillMaxWidth().testTag("ink-hex"))
            Text("굵기 ${"%.1f".format(width)}",style=MaterialTheme.typography.labelLarge)
            Slider(value=width,onValueChange={width=it},valueRange=.5f..24f,modifier=Modifier.testTag("ink-width"))
            Text("불투명도 ${(opacity*100).toInt()}%",style=MaterialTheme.typography.labelLarge)
            Slider(value=opacity,onValueChange={opacity=it},valueRange=.05f..1f,modifier=Modifier.testTag("ink-opacity"))
            Row(Modifier.fillMaxWidth(),verticalAlignment=Alignment.CenterVertically){Text("손가락으로도 필기",Modifier.weight(1f));Switch(checked=fingerInk,onCheckedChange={fingerInk=it},modifier=Modifier.testTag("ink-finger-toggle"))}
            Text("펜 옆 버튼을 누르는 동안만 지우개로 바뀌고, 떼면 선택한 펜·형광펜으로 돌아와요. 색상과 굵기는 그대로 유지해요.",style=MaterialTheme.typography.bodySmall)
            Text("획 지우개는 닿은 획 전체를 지웁니다. 펜 사용 중 손바닥 입력은 무시하며, 실제 기기에서의 인식은 기기 설정에도 영향을 받습니다.",style=MaterialTheme.typography.bodySmall)
            FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
                OutlinedButton(enabled=document.cursor>0,onClick={onInkChange(InkStore.undo(document))},modifier=Modifier.testTag("ink-undo")){Icon(Icons.Outlined.Undo,null);Text("되돌리기")}
                OutlinedButton(enabled=document.cursor<document.edits.size,onClick={onInkChange(InkStore.redo(document))},modifier=Modifier.testTag("ink-redo")){Icon(Icons.Outlined.Redo,null);Text("다시 하기")}
            }
        }
    },confirmButton={TextButton(onClick={settingsOpen=false}){Text("완료")}})
}

/** Canvas uses one document transform for text, highlights and ink. No viewport-based text reflow. */
internal class InkSqlView(context:Context):View(context) {
    private data class CodeLine(val start:Int,val raw:String,val display:String,val positions:FloatArray)
    private val textPaint=Paint(Paint.ANTI_ALIAS_FLAG).apply{color=0xff111827.toInt();textSize=16f;typeface=Typeface.MONOSPACE}
    private val markPaint=Paint(Paint.ANTI_ALIAS_FLAG).apply{color=0xffd9e9ff.toInt()}
    private val strokePaint=Paint(Paint.ANTI_ALIAS_FLAG).apply{strokeCap=Paint.Cap.ROUND;strokeJoin=Paint.Join.ROUND}
    private val guidePaint=Paint(Paint.ANTI_ALIAS_FLAG).apply{color=0xff78909c.toInt();strokeWidth=2f}
    private var code="";private var lines:List<CodeLine> = emptyList()
    private var document:InkDocument?=null;private var strokes:List<InkStroke> = emptyList();private var ranges:List<IntRange> = emptyList()
    private var tool="pen";private var inkColor=0xff172d45L;private var inkWidth=2.5f;private var inkOpacity=1f;private var finger=false
    private var zoom=1f;private var panX=0f;private var panY=0f;private var documentWidth=220f;private var documentHeight=180f
    private var onChange:(InkDocument)->Unit={};private var onPan:(Float,Float)->Unit={_,_->};private var onError:(String)->Unit={}
    private var activePointer=-1;private var activeIsStylus=false;private var erasing=false
    private var temporaryErase=false;private var modeChangedAt=0L
    private var onTemporaryEraseChange:(Boolean)->Unit={}
    private val pending=ArrayList<InkPoint>();private val pendingErase=linkedSetOf<String>()
    private var panPointer=-1;private var previousX=0f;private var previousY=0f;private var overflow=false
    private var gesturePanX=0f;private var gesturePanY=0f;private var pendingFocus=false
    private val scale get()=resources.displayMetrics.density*zoom
    init {isFocusable=true;setBackgroundColor(android.graphics.Color.WHITE);importantForAccessibility=IMPORTANT_FOR_ACCESSIBILITY_YES}
    fun configure(sql:String,ink:InkDocument,activeRanges:List<IntRange>,tool:String,color:Long,width:Float,opacity:Float,fingerInk:Boolean,zoom:Float,x:Float,y:Float,
        onChange:(InkDocument)->Unit,onPan:(Float,Float)->Unit,onError:(String)->Unit,onTemporaryEraseChange:(Boolean)->Unit={}) {
        if(code!=sql||lines.isEmpty()) {
            code=sql;var start=0
            lines=sql.split('\n').map{raw->
                val positions=FloatArray(raw.length+1);val display=StringBuilder();var cursor=0f
                raw.forEachIndexed{index,c->val part=if(c=='\t')"    " else c.toString();display.append(part);cursor+=textPaint.measureText(part);positions[index+1]=cursor}
                CodeLine(start,raw,display.toString(),positions).also{start+=raw.length+1}
            }
            contentDescription="SQL 코드. $sql"
        }
        val changedDocument=document?.id!=ink.id
        if(changedDocument)cancelPending()
        else if(this.tool!=tool&&activePointer!=-1)commitPending()
        if(document!=ink){document=ink;strokes=InkStore.visibleStrokes(ink);updateBounds()}
        val safeRanges=activeRanges.filter{it.first>=0&&it.last<sql.length&&it.first<=it.last}
        val changedFocus=this.ranges!=safeRanges||changedDocument
        this.ranges=safeRanges
        this.tool=tool;inkColor=color;inkWidth=width;inkOpacity=opacity;finger=fingerInk;this.zoom=zoom.coerceIn(.5f,5f);panX=x;panY=y
        this.onChange=onChange;this.onPan=onPan;this.onError=onError
        this.onTemporaryEraseChange=onTemporaryEraseChange;onTemporaryEraseChange(temporaryErase)
        erasing=tool=="eraser"||temporaryErase
        clampPan()
        if(changedFocus)pendingFocus=true
        if(pendingFocus&&this.width>0&&height>0){revealCurrentRange();pendingFocus=false}
        invalidate()
    }
    private fun revealCurrentRange(){
        val range=ranges.firstOrNull()?:return
        val index=lines.indexOfLast{it.start<=range.first}.coerceAtLeast(0)
        val line=lines.getOrNull(index)?:return
        val column=(range.first-line.start).coerceIn(0,line.raw.length)
        val targetX=16f+line.positions[column];val targetY=12f+index*24f
        val oldX=panX;val oldY=panY
        if(targetX<panX+8f||targetX>panX+width/scale-32f)panX=(targetX-16f).coerceAtLeast(0f)
        if(targetY<panY||targetY+24f>panY+height/scale)panY=(targetY-12f).coerceAtLeast(0f)
        clampPan()
        if(oldX!=panX||oldY!=panY)post{onPan(panX,panY)}
    }
    private fun updateBounds(){
        documentWidth=max(220f,(lines.maxOfOrNull{it.positions.last()}?:0f)+32f)
        documentHeight=max(180f,lines.size*24f+48f)
        strokes.forEach{stroke->stroke.points.forEach{p->documentWidth=max(documentWidth,p.x+24f);documentHeight=max(documentHeight,p.y+24f)}}
    }
    private fun clampPan(){panX=panX.coerceIn(0f,max(0f,documentWidth-width/scale));panY=panY.coerceIn(0f,max(0f,documentHeight-height/scale))}
    override fun onSizeChanged(w:Int,h:Int,oldw:Int,oldh:Int){clampPan();if(pendingFocus){revealCurrentRange();pendingFocus=false};onPan(panX,panY)}
    override fun onDraw(canvas:Canvas) {
        super.onDraw(canvas);canvas.save();canvas.scale(scale,scale);canvas.translate(-panX,-panY)
        // Draw only visible source lines. The source/advance cache is rebuilt only when SQL changes.
        val first=max(0,floor((panY-12f)/24f).toInt());val last=min(lines.lastIndex,ceil((panY+height/scale)/24f).toInt())
        for(index in first..last) {
            val line=lines[index];val baseline=32f+index*24f
            textPaint.typeface=Typeface.MONOSPACE;canvas.drawText(line.display,16f,baseline,textPaint)
            ranges.forEach { range ->
                val start=max(0,range.first-line.start);val end=min(line.raw.length,range.last-line.start+1)
                if(start<end){val left=16f+line.positions[start];val right=16f+line.positions[end]
                    canvas.drawRect(left,baseline-18f,right,baseline+5f,markPaint)
                    textPaint.typeface=Typeface.create(Typeface.MONOSPACE,Typeface.BOLD)
                    canvas.drawText(line.raw.substring(start,end).replace("\t","    "),left,baseline,textPaint)
                    textPaint.typeface=Typeface.MONOSPACE
                }
            }
        }
        strokes.filterNot{it.id in pendingErase}.forEach{drawStroke(canvas,it)}
        if(pending.isNotEmpty())drawStroke(canvas,InkStroke("pending",if(tool=="highlighter")"highlighter"else"pen",inkColor,inkWidth,inkOpacity,pending))
        canvas.restore()
        if(documentWidth>width/scale){val fraction=(width/scale)/documentWidth;val start=(panX/documentWidth)*width;canvas.drawLine(start,height-3f,start+width*fraction,height-3f,guidePaint)}
        if(documentHeight>height/scale){val fraction=(height/scale)/documentHeight;val start=(panY/documentHeight)*height;canvas.drawLine(width-3f,start,width-3f,start+height*fraction,guidePaint)}
    }
    private fun drawStroke(canvas:Canvas,stroke:InkStroke){
        val points=stroke.points
        if(points.isEmpty())return
        // Reject strokes outside the viewport before drawing their segments.
        if(points.all{it.y<panY-stroke.width}||points.all{it.y>panY+height/scale+stroke.width}||points.all{it.x<panX-stroke.width}||points.all{it.x>panX+width/scale+stroke.width})return
        strokePaint.color=stroke.color.toInt();strokePaint.alpha=(stroke.opacity*255).toInt();strokePaint.style=Paint.Style.STROKE
        if(points.size==1){strokePaint.style=Paint.Style.FILL;canvas.drawCircle(points[0].x,points[0].y,stroke.width/2,strokePaint);return}
        for(index in 1 until points.size){val a=points[index-1];val b=points[index];strokePaint.strokeWidth=stroke.width*(if(stroke.tool=="pen")(.55f+.45f*(a.pressure+b.pressure)/2)else 1f);canvas.drawLine(a.x,a.y,b.x,b.y,strokePaint)}
    }
    override fun onTouchEvent(event:MotionEvent):Boolean {
        if(event.actionMasked==MotionEvent.ACTION_CANCEL){cancelPending();if(panPointer!=-1){panX=gesturePanX;panY=gesturePanY;clampPan();onPan(panX,panY)};release();return true}
        val actionIndex=event.actionIndex
        when(event.actionMasked) {
            MotionEvent.ACTION_DOWN,MotionEvent.ACTION_POINTER_DOWN -> {
                if(event.actionMasked==MotionEvent.ACTION_DOWN){gesturePanX=panX;gesturePanY=panY}
                val kind=event.getToolType(actionIndex);val stylus=kind==MotionEvent.TOOL_TYPE_STYLUS||kind==MotionEvent.TOOL_TYPE_ERASER
                if(stylus){
                    cancelPending()
                    if(panPointer!=-1){panX=gesturePanX;panY=gesturePanY;clampPan();onPan(panX,panY)}
                    panPointer=-1;activePointer=event.getPointerId(actionIndex);activeIsStylus=true;syncStylusMode(event,actionIndex);modeChangedAt=event.eventTime;sample(event,actionIndex)
                }
                else if(!activeIsStylus){
                    resetTemporaryErase()
                    if(event.pointerCount>1){cancelPending();panPointer=event.getPointerId(actionIndex);previousX=event.getX(actionIndex);previousY=event.getY(actionIndex)}
                    else if(finger){activePointer=event.getPointerId(actionIndex);erasing=tool=="eraser";sample(event,actionIndex)}
                    else {panPointer=event.getPointerId(actionIndex);previousX=event.getX(actionIndex);previousY=event.getY(actionIndex)}
                }
                parent?.requestDisallowInterceptTouchEvent(true)
            }
            MotionEvent.ACTION_MOVE -> {
                if(activePointer!=-1){val index=event.findPointerIndex(activePointer);if(index>=0){
                    val changed=if(activeIsStylus)syncStylusMode(event,index)else false
                    // A batch has no historical button states. Never replay old points using a new tool.
                    if(!changed)for(history in 0 until event.historySize)if(event.getHistoricalEventTime(history)>=modeChangedAt)sample(event,index,history)
                    sample(event,index)
                }}
                else if(panPointer!=-1){val index=event.findPointerIndex(panPointer);if(index>=0){val x=event.getX(index);val y=event.getY(index);panX+=(previousX-x)/scale;panY+=(previousY-y)/scale;clampPan();previousX=x;previousY=y;onPan(panX,panY)}}
            }
            MotionEvent.ACTION_UP,MotionEvent.ACTION_POINTER_UP -> {
                val id=event.getPointerId(actionIndex)
                if(id==activePointer){
                    val canceled=Build.VERSION.SDK_INT>=33&&(event.flags and MotionEvent.FLAG_CANCELED)!=0
                    if(!canceled){
                        if(activeIsStylus)syncStylusMode(event,actionIndex)
                        // Releasing an erase button as the tip lifts must not leave a new pen dot.
                        if(erasing||pending.isNotEmpty())sample(event,actionIndex)
                        commitPending()
                    }else cancelPending()
                    activePointer=-1;activeIsStylus=false
                }
                if(id==panPointer)panPointer=-1
                if(event.actionMasked==MotionEvent.ACTION_UP){performClick();release()}
            }
        }
        invalidate();return true
    }
    private fun isStylus(event:MotionEvent,index:Int)=event.getToolType(index) in listOf(MotionEvent.TOOL_TYPE_STYLUS,MotionEvent.TOOL_TYPE_ERASER)
    private fun syncStylusMode(event:MotionEvent,index:Int):Boolean {
        if(!isStylus(event,index))return false
        val mask=MotionEvent.BUTTON_STYLUS_PRIMARY or MotionEvent.BUTTON_STYLUS_SECONDARY or MotionEvent.BUTTON_SECONDARY
        val temporary=event.getToolType(index)==MotionEvent.TOOL_TYPE_ERASER||(event.buttonState and mask)!=0
        val next=tool=="eraser"||temporary
        val changed=erasing!=next
        if(changed){
            // Save only the preceding contact segment; retain its active pointer for the new tool.
            if(activePointer!=-1)commitPending()
            erasing=next;modeChangedAt=event.eventTime
        }
        if(temporaryErase!=temporary){temporaryErase=temporary;onTemporaryEraseChange(temporary)}
        return changed
    }
    override fun onGenericMotionEvent(event:MotionEvent):Boolean {
        if(event.actionMasked==MotionEvent.ACTION_BUTTON_PRESS||event.actionMasked==MotionEvent.ACTION_BUTTON_RELEASE){
            if(activePointer!=-1&&!activeIsStylus)return super.onGenericMotionEvent(event)
            val index=if(activeIsStylus)event.findPointerIndex(activePointer)else (0 until event.pointerCount).firstOrNull{isStylus(event,it)}?:-1
            if(index>=0&&isStylus(event,index)){
                syncStylusMode(event,index)
                // Button events change tools, but are not additional contact samples.
                invalidate();return true
            }
        }
        return super.onGenericMotionEvent(event)
    }
    override fun onHoverEvent(event:MotionEvent):Boolean {
        val index=(0 until event.pointerCount).firstOrNull{isStylus(event,it)}?:return super.onHoverEvent(event)
        if(activePointer==-1){
            if(event.actionMasked==MotionEvent.ACTION_HOVER_EXIT)resetTemporaryErase()else syncStylusMode(event,index)
            invalidate();return true
        }
        return super.onHoverEvent(event)
    }
    private fun resetTemporaryErase(){if(temporaryErase){temporaryErase=false;onTemporaryEraseChange(false)};erasing=tool=="eraser"}
    override fun onWindowFocusChanged(hasWindowFocus:Boolean){super.onWindowFocusChanged(hasWindowFocus);if(!hasWindowFocus){cancelPending();release()}}
    override fun onDetachedFromWindow(){cancelPending();release();super.onDetachedFromWindow()}
    private fun sample(event:MotionEvent,index:Int,history:Int=-1){
        val px=if(history<0)event.getX(index)else event.getHistoricalX(index,history)
        val py=if(history<0)event.getY(index)else event.getHistoricalY(index,history)
        val rawPressure=if(history<0)event.getPressure(index)else event.getHistoricalPressure(index,history)
        val x=(px/scale+panX).coerceIn(0f,InkStore.MAX_COORDINATE);val y=(py/scale+panY).coerceIn(0f,InkStore.MAX_COORDINATE)
        if(!x.isFinite()||!y.isFinite())return
        if(erasing){strokes.filterNot{it.id in pendingErase}.filter{InkStore.hit(it,x,y,max(6f,inkWidth))}.forEach{pendingErase+=it.id};return}
        if(pending.size>=InkStore.MAX_POINTS_PER_STROKE){overflow=true;return}
        val previous=pending.lastOrNull();if(previous!=null&&abs(previous.x-x)+abs(previous.y-y)<.35f)return
        pending+=InkPoint(x,y,if(rawPressure.isFinite())rawPressure.coerceIn(0f,1f)else 1f)
    }
    private fun commitPending(){
        val current=document?:return
        if(overflow){onError("획이 너무 깁니다. 펜을 떼어 짧게 나눠 써 주세요.");clearSegment();return}
        runCatching {
            if(erasing)InkStore.erase(current,pendingErase.toList())
            else if(pending.isNotEmpty())InkStore.add(current,InkStroke(UUID.randomUUID().toString(),if(tool=="highlighter")"highlighter"else"pen",inkColor,inkWidth,inkOpacity,pending.toList()))
            else current
        }.onSuccess {next->if(next!=current){document=next;strokes=InkStore.visibleStrokes(next);updateBounds();onChange(next)}}.onFailure{onError(it.message?:"필기를 추가하지 못했습니다.")}
        clearSegment()
    }
    private fun clearSegment(){pending.clear();pendingErase.clear();overflow=false;invalidate()}
    private fun cancelPending(){clearSegment();activePointer=-1;activeIsStylus=false;resetTemporaryErase()}
    private fun release(){panPointer=-1;parent?.requestDisallowInterceptTouchEvent(false)}
    override fun performClick():Boolean {super.performClick();return true}
}
