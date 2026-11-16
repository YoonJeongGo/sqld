package kr.sqld.study

import android.graphics.BitmapFactory
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.rememberTransformableState
import androidx.compose.foundation.gestures.transformable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt

@Composable internal fun VisualText(text:String,emphasis:List<String> = emptyList()){
    if(text.isNotBlank()) StudyBodyText(text,emphasis=emphasis)
}

private data class LoadedVisual(val image:ImageBitmap?=null,val failed:Boolean=false)
@Composable private fun loadVisual(path:String,thumbnail:Boolean):LoadedVisual {
    val context=LocalContext.current
    val loaded by produceState(LoadedVisual(),path,thumbnail){
        value=withContext(Dispatchers.IO){
            runCatching {
                context.assets.open(path).use { stream ->
                    val options=BitmapFactory.Options().apply{inSampleSize=if(thumbnail)2 else 1}
                    LoadedVisual(requireNotNull(BitmapFactory.decodeStream(stream,null,options)).asImageBitmap())
                }
            }.getOrElse{LoadedVisual(failed=true)}
        }
    }
    return loaded
}

@Composable fun CourseVisualCard(pack:CourseVisualPack,visual:CourseVisual){
    var enlarged by rememberSaveable(visual.id){mutableStateOf(false)}
    var transcript by rememberSaveable(visual.id){mutableStateOf(false)}
    StudyPaper(modifier=Modifier.testTag("visual-card-${visual.id}")){
        Eyebrow("그림으로 먼저 이해하기 · 별도 예시 ${visual.number}")
        StudySection(visual.title){VisualText(visual.easy,listOf(visual.title))}
        if(visual.correction.isNotBlank())StudyWarning(visual.correction)
        BoxWithConstraints(Modifier.fillMaxWidth().aspectRatio(8f/5f).testTag("visual-thumbnail-${visual.id}"),contentAlignment=Alignment.Center){
            // Avoid upscaling a half-resolution preview on wide, high-density tablets.
            val thumbnail=with(LocalDensity.current){maxWidth.toPx()}<=visual.width/2f
            val loaded=loadVisual(visual.pngAsset,thumbnail)
            loaded.image?.let { bitmap -> Image(bitmap,visual.alt,Modifier.fillMaxSize().testTag("visual-thumbnail-image-${visual.id}").clickable(onClickLabel="그림 확대"){enlarged=true},contentScale=ContentScale.Fit) }
            if(loaded.failed)Text("그림을 읽을 수 없어요. 아래 글 설명을 확인해 주세요.")
            else if(loaded.image==null)CircularProgressIndicator()
        }
        OutlinedButton(onClick={enlarged=true},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("visual-open-${visual.id}")){Text("그림 확대 · 원본 크기 보기")}
        Text("정적인 그림이에요. 그림 속 화살표나 [다음] 글자는 누르는 버튼이 아니에요.",style=MaterialTheme.typography.bodySmall)
        StudySection("그림 읽는 순서"){
            visual.readingSteps.forEachIndexed{index,step->VisualText("${index+1}. $step",visual.labels.map{it.label})}
        }
        StudySection("결과와 이유"){VisualText(visual.resultReason,visual.labels.map{it.label})}
        if(visual.labels.isNotEmpty()){
            StudySection("표시가 뜻하는 것"){
                visual.labels.forEach{VisualText("${it.label} · ${it.meaning}",listOf(it.label))}
            }
        }
        visual.warnings.forEach{StudyWarning(it)}
        VisualText(visual.dataNotes)
        StudySection("한 줄 기억"){VisualText(visual.memory,listOf(visual.title))}
        TextButton(onClick={transcript=!transcript},modifier=Modifier.testTag("visual-transcript-${visual.id}")){Text(if(transcript)"그림의 표·글자 접기"else"그림의 표·글자를 텍스트로 보기")}
        if(transcript){
            StudySection("그림에 담긴 표"){visual.tables.forEach{StudyTable(it)}}
            StudySection("그림 속 전체 글자"){
                // A transcript includes diagram and SQL line structure; preserve it verbatim.
                SelectionContainer{Text(visual.transcript,style=MaterialTheme.typography.bodyLarge)}
            }
            StudySection("참고 자료"){
                pack.sources.filter{it.id in visual.sourceIds}.forEach{
                    SelectionContainer{Text("${it.title}\n${it.url}",style=MaterialTheme.typography.bodyMedium)}
                }
            }
        }
    }
    if(enlarged)CourseVisualViewer(visual){enlarged=false}
}

/** Fit preserves the 8:5 image; 100% means one source pixel per screen pixel. */
@OptIn(ExperimentalLayoutApi::class)
@Composable fun CourseVisualViewer(visual:CourseVisual,onClose:()->Unit){
    val loaded=loadVisual(visual.pngAsset,false)
    var zoom by rememberSaveable(visual.id){mutableFloatStateOf(1f)}
    var panX by rememberSaveable(visual.id){mutableFloatStateOf(0f)}
    var panY by rememberSaveable(visual.id){mutableFloatStateOf(0f)}
    var viewport by remember{mutableStateOf(IntSize.Zero)}
    val fit=if(viewport.width>0&&viewport.height>0)min(1f,min(viewport.width.toFloat()/visual.width,viewport.height.toFloat()/visual.height)) else 1f
    val maxZoom=max(8f,2f/fit)
    fun boundPan(x:Float,y:Float,scale:Float=zoom):Offset{
        val maxX=max(0f,(visual.width*fit*scale-viewport.width)/2f)
        val maxY=max(0f,(visual.height*fit*scale-viewport.height)/2f)
        return Offset(x.coerceIn(-maxX,maxX),y.coerceIn(-maxY,maxY))
    }
    fun changeZoom(value:Float){
        zoom=value.coerceIn(1f,maxZoom)
        val bounded=boundPan(panX,panY);panX=bounded.x;panY=bounded.y
    }
    val gestures=rememberTransformableState{factor,pan,_ ->
        val next=(zoom*factor).coerceIn(1f,maxZoom)
        val bounded=boundPan(panX+pan.x,panY+pan.y,next)
        zoom=next;panX=bounded.x;panY=bounded.y
    }
    LaunchedEffect(viewport){val bounded=boundPan(panX,panY);panX=bounded.x;panY=bounded.y}
    Dialog(onDismissRequest=onClose,properties=DialogProperties(usePlatformDefaultWidth=false)){
        Surface(Modifier.fillMaxSize(),color=MaterialTheme.colorScheme.background){
            Column(Modifier.fillMaxSize().safeDrawingPadding().padding(12.dp),verticalArrangement=Arrangement.spacedBy(8.dp)){
                FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){
                    TextButton(onClick=onClose,modifier=Modifier.heightIn(min=48.dp).testTag("visual-close")){Text("그림 닫기")}
                    OutlinedButton(onClick={zoom=1f;panX=0f;panY=0f},modifier=Modifier.heightIn(min=48.dp).testTag("visual-fit")){Text("화면 맞춤")}
                    OutlinedButton(onClick={changeZoom(1f/fit)},modifier=Modifier.heightIn(min=48.dp).testTag("visual-native")){Text("원본 크기")}
                    OutlinedButton(onClick={changeZoom(zoom/1.5f)},enabled=zoom>1f,modifier=Modifier.heightIn(min=48.dp).testTag("visual-zoom-out")){Text("− 축소")}
                    OutlinedButton(onClick={changeZoom(zoom*1.5f)},enabled=zoom<maxZoom,modifier=Modifier.heightIn(min=48.dp).testTag("visual-zoom-in")){Text("＋ 확대")}
                    // A percentage must not change wrapping and thereby the viewport that defines it.
                    Box(Modifier.width(100.dp).heightIn(min=48.dp),contentAlignment=Alignment.Center){
                        Text("${(fit*zoom*100).roundToInt()}%",style=MaterialTheme.typography.bodySmall,maxLines=1,softWrap=false,modifier=Modifier.testTag("visual-zoom-label"))
                    }
                }
                Text("${visual.number}. ${visual.title}",style=MaterialTheme.typography.titleSmall)
                Text("두 손가락 확대·축소 / 확대한 그림을 끌어 이동",style=MaterialTheme.typography.bodySmall)
                Box(Modifier.weight(1f).fillMaxWidth().clipToBounds().background(MaterialTheme.colorScheme.surfaceVariant)
                    .onSizeChanged{viewport=it}.transformable(gestures).testTag("visual-viewport")
                    .semantics{stateDescription="배율 ${(fit*zoom*100).roundToInt()}%, 가로 위치 ${panX.roundToInt()}, 세로 위치 ${panY.roundToInt()}"},contentAlignment=Alignment.Center){
                    loaded.image?.let { bitmap ->
                        Image(bitmap,visual.alt,Modifier.fillMaxSize().testTag("visual-image").graphicsLayer{scaleX=zoom;scaleY=zoom;translationX=panX;translationY=panY},contentScale=ContentScale.Inside)
                    }
                    if(loaded.failed)Text("그림을 읽을 수 없어요. 닫고 텍스트 설명을 확인해 주세요.")
                    else if(loaded.image==null)CircularProgressIndicator()
                }
            }
        }
    }
}
