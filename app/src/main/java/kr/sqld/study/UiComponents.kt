package kr.sqld.study

import android.graphics.Typeface
import android.os.Build
import android.text.Layout
import android.graphics.text.LineBreakConfig
import android.graphics.text.LineBreaker
import java.util.Locale
import android.text.SpannableString
import android.text.Spanned
import android.text.style.BackgroundColorSpan
import android.text.style.UnderlineSpan
import android.text.style.StyleSpan
import android.text.style.TypefaceSpan
import android.text.style.LineHeightSpan
import android.graphics.Paint
import android.view.ActionMode
import android.view.Menu
import android.view.MenuItem
import android.widget.TextView
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.Alignment
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.semantics.*
import androidx.compose.ui.text.*
import androidx.compose.ui.text.font.*
import androidx.compose.ui.unit.*
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter

/** A display-only blank paragraph line is a small gap, not a full extra body line. */
private class NoteParagraphGap(private val at:Int,private val pixels:Int):LineHeightSpan {
    override fun chooseHeight(text:CharSequence,start:Int,end:Int,spanstartv:Int,v:Int,fm:Paint.FontMetricsInt){
        if(start==at&&end<=at+1){fm.ascent=-pixels;fm.descent=0;fm.top=fm.ascent;fm.bottom=0}
    }
}

fun dateText(value:Long)=Instant.ofEpochMilli(value).atZone(ZoneId.systemDefault()).format(DateTimeFormatter.ofPattern("M월 d일 HH:mm"))
fun kindLabel(q:Question)=when(q.kind){"recall"->"개념 확인";"mock"->"창작 모의문제";else->"적용 연습"}
/** Includes actual font scaling and each Material button's padding/touch width. */
@Composable internal fun actionRowFits(width:Dp,labels:List<String>,padding:Dp=24.dp,gap:Dp=8.dp):Boolean{
    val measurer=rememberTextMeasurer()
    val density=LocalDensity.current
    val style=MaterialTheme.typography.labelLarge
    val needed=labels.fold(0.dp){total,label->
        val textWidth=with(density){measurer.measure(label,style,softWrap=false).size.width.toDp()}
        total+maxOf(64.dp,textWidth+padding*2)
    }+gap*(labels.size-1).coerceAtLeast(0)
    return needed+2.dp<=width
}
@Composable fun DialogBody(text:String){Text(text,Modifier.verticalScroll(rememberScrollState()))}
@Composable fun Eyebrow(text:String){Text(text,style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.primary)}
@Composable fun PageTitle(kicker:String,title:String,description:String?=null){Column(verticalArrangement=Arrangement.spacedBy(6.dp)){if(kicker.isNotBlank())Eyebrow(kicker);Text(title,style=MaterialTheme.typography.headlineMedium);description?.takeIf{it.isNotBlank()}?.let{Text(it,style=MaterialTheme.typography.bodyMedium,color=MaterialTheme.colorScheme.onSurfaceVariant)}}}
@Composable fun Paper(modifier:Modifier=Modifier,accent:Boolean=false,content:@Composable ColumnScope.()->Unit){Surface(modifier.fillMaxWidth(),color=if(accent)MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface,contentColor=if(accent)MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurface,shape=RoundedCornerShape(20.dp),border=BorderStroke(1.dp,MaterialTheme.colorScheme.outlineVariant.copy(alpha=.7f))){Column(Modifier.padding(18.dp),verticalArrangement=Arrangement.spacedBy(12.dp),content=content)}}
@OptIn(ExperimentalLayoutApi::class)
@Composable fun NoteRow(index:String,title:String,subtitle:String,onClick:()->Unit,trailing:@Composable ()->Unit={Icon(Icons.Outlined.ChevronRight,null)}){
    val stacked=index.length>4||LocalDensity.current.fontScale*MaterialTheme.typography.titleMedium.fontSize.value/18f>=1.6f
    Column{Row(Modifier.fillMaxWidth().clickable(onClick=onClick).padding(vertical=16.dp),verticalAlignment=Alignment.CenterVertically,horizontalArrangement=Arrangement.spacedBy(12.dp)){
        if(!stacked)Text(index,Modifier.widthIn(min=28.dp),color=MaterialTheme.colorScheme.primary,style=MaterialTheme.typography.labelLarge)
        Column(Modifier.weight(1f),verticalArrangement=Arrangement.spacedBy(6.dp)){
            if(stacked)Text(index,color=MaterialTheme.colorScheme.primary,style=MaterialTheme.typography.labelMedium)
            Text(title,style=MaterialTheme.typography.titleMedium)
            FlowRow(horizontalArrangement=Arrangement.spacedBy(10.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){subtitle.split(" · ").forEach{part->Text(part,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)}}
        };trailing()
    };HorizontalDivider(color=MaterialTheme.colorScheme.outlineVariant)}
}
@Composable fun EmptyState(title:String,body:String,action:String,onAction:()->Unit){Paper{Text(title,style=MaterialTheme.typography.titleLarge);Text(body);Button(onClick=onAction){Text(action)}}}
@Composable fun StarButton(id:String,starred:Boolean,onToggle:()->Unit){IconToggleButton(checked=starred,onCheckedChange={onToggle()},modifier=Modifier.size(48.dp).semantics { contentDescription=if(starred)"별표 해제"else "별표 저장";stateDescription=if(starred)"별표됨"else"별표 안 됨" }){Icon(if(starred)Icons.Outlined.Star else Icons.Outlined.StarBorder,null,tint=if(starred)MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.onSurfaceVariant)}}
@Composable fun SqlBlock(sql:String,wrap:Boolean,onWrap:(Boolean)->Unit){
    val codeBackground=Color.White
    val codeForeground=Color(0xFF111827)
    val codeMuted=Color(0xFF4B5563)
    val codeKeyword=codeForeground
    val text=buildAnnotatedString { sql.lines().forEachIndexed { i,line ->
        withStyle(SpanStyle(color=codeMuted)){append("${i+1}  ")}
        val start=length;append(line)
        Regex("\\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|FULL|OUTER|INNER|ON|GROUP|BY|HAVING|ORDER|NULL|IS|NOT|IN|EXISTS|COUNT|SUM|AVG|OVER|PARTITION|AS|AND|OR|CASE|WHEN|THEN|ELSE|END|COMMIT|ROLLBACK)\\b",RegexOption.IGNORE_CASE).findAll(line).forEach { addStyle(SpanStyle(color=codeKeyword,fontWeight=FontWeight.Bold),start+it.range.first,start+it.range.last+1) }
        if(i<sql.lines().lastIndex)append('\n')
    } }
    Surface(color=codeBackground,contentColor=codeForeground,shape=RoundedCornerShape(16.dp),border=BorderStroke(1.dp,Color(0xFFD1D5DB))){Column(Modifier.padding(16.dp)){
        Row(Modifier.fillMaxWidth(),verticalAlignment=Alignment.CenterVertically){Text("SQL",Modifier.weight(1f),style=MaterialTheme.typography.labelMedium,color=codeMuted);TextButton(onClick={onWrap(!wrap)},colors=ButtonDefaults.textButtonColors(contentColor=codeKeyword)){Text(if(wrap)"가로로 보기"else"줄바꿈")}}
        SelectionContainer{Text(text,modifier=if(wrap)Modifier.fillMaxWidth()else Modifier.horizontalScroll(rememberScrollState()),style=MaterialTheme.typography.bodyMedium.copy(fontFamily=FontFamily.Monospace),softWrap=wrap)}
        if(!wrap)Text("↔ 좌우로 스크롤할 수 있어요",style=MaterialTheme.typography.bodySmall,color=codeMuted)
    }}
}
@Composable fun StudyTable(table:DataTable,expand:Boolean=true){
    var enlarged by remember{mutableStateOf(false)}
    val measurer=rememberTextMeasurer()
    val density=LocalDensity.current
    val cellStyle=MaterialTheme.typography.bodyMedium.copy(fontFamily=FontFamily.Monospace)
    val headerStyle=MaterialTheme.typography.labelLarge
    val widths=remember(table,cellStyle,headerStyle,density){table.columns.indices.map{column->
        val header=measurer.measure(table.columns[column],headerStyle,softWrap=false).size.width
        val value=table.rows.maxOfOrNull{row->measurer.measure(row[column]?:"NULL ∅",cellStyle,softWrap=false).size.width}?:0
        (with(density){maxOf(header,value).toDp()}+24.dp).coerceIn(112.dp,320.dp)
    }}
    Column(verticalArrangement=Arrangement.spacedBy(6.dp)){
        Row(verticalAlignment=Alignment.CenterVertically){Text(table.title,Modifier.weight(1f),style=MaterialTheme.typography.titleSmall);if(expand)IconButton(onClick={enlarged=true}){Icon(Icons.Outlined.OpenInFull,"표 크게 보기")}}
        Column(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).border(1.dp,MaterialTheme.colorScheme.outlineVariant,RoundedCornerShape(8.dp))){
            Row(Modifier.background(MaterialTheme.colorScheme.surfaceVariant)){table.columns.forEachIndexed { column,name -> Text(name,Modifier.width(widths[column]).padding(12.dp),style=headerStyle) }}
            table.rows.forEachIndexed { index,row -> Row(Modifier.background(if(index%2==0)MaterialTheme.colorScheme.surface else MaterialTheme.colorScheme.surfaceVariant.copy(alpha=.4f))){row.forEachIndexed { column,value ->Text(if(value==null)"NULL ∅"else if(value.isEmpty())"''"else value,Modifier.width(widths[column]).padding(12.dp),style=cellStyle,color=MaterialTheme.colorScheme.onSurface) }} }
        }
        Text("↔ 가로 스크롤 · NULL ∅는 값 없음 · 빈 문자열은 ''",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
    }
    if(enlarged)Dialog(onDismissRequest={enlarged=false},properties=DialogProperties(usePlatformDefaultWidth=false)){Surface(Modifier.fillMaxSize(),color=MaterialTheme.colorScheme.background){Column(Modifier.safeDrawingPadding().padding(20.dp).verticalScroll(rememberScrollState())){TextButton(onClick={enlarged=false}){Text("표 닫기")};StudyTable(table,false)}}}
}
@Composable fun SelectableNoteText(text:String,annotations:List<Annotation>,scale:Float,onAnnotate:(String,String)->Unit){
    SelectableNoteText(text,annotations,scale,onAnnotate,emptyList())
}
@Composable fun SelectableNoteText(text:String,annotations:List<Annotation>,scale:Float,onAnnotate:(String,String)->Unit,emphasis:List<String>){
    val foreground=MaterialTheme.colorScheme.onSurface.toArgb()
    val highlight=MaterialTheme.colorScheme.secondaryContainer.toArgb()
    val presentation=remember(text,emphasis){BodyTextRules.plan(text,emphasis,preserveSource=true)}
    val projection=remember(text){NoteTextProjection.from(text)}
    val currentProjection by rememberUpdatedState(projection)
    val currentAnnotate by rememberUpdatedState(onAnnotate)
    AndroidView(modifier=Modifier.fillMaxWidth(),factory={context->TextView(context).apply{
        setTextIsSelectable(true); setPadding(0,0,0,0); includeFontPadding=false; setLineSpacing(0f,1.45f)
        textLocale=Locale.KOREAN;breakStrategy=LineBreaker.BREAK_STRATEGY_BALANCED;hyphenationFrequency=Layout.HYPHENATION_FREQUENCY_NONE
        if(Build.VERSION.SDK_INT>=33){lineBreakStyle=LineBreakConfig.LINE_BREAK_STYLE_STRICT;lineBreakWordStyle=LineBreakConfig.LINE_BREAK_WORD_STYLE_PHRASE}
        customSelectionActionModeCallback=object:ActionMode.Callback{
            override fun onCreateActionMode(mode:ActionMode,menu:Menu):Boolean {menu.add(0,810,0,"형광펜");menu.add(0,811,1,"밑줄");menu.add(0,812,2,"메모");return true}
            override fun onPrepareActionMode(mode:ActionMode,menu:Menu)=false
            override fun onActionItemClicked(mode:ActionMode,item:MenuItem):Boolean {
                if(item.itemId !in 810..812)return false
                val start=minOf(selectionStart,selectionEnd).coerceIn(0,currentProjection.text.length)
                val end=maxOf(selectionStart,selectionEnd).coerceIn(0,currentProjection.text.length)
                if(end>start){
                    val quote=currentProjection.sourceQuote(start,end)
                    if(quote.isNotEmpty())currentAnnotate(quote,when(item.itemId){810->"highlight";811->"underline";else->"memo"})
                }
                mode.finish();return true
            }
            override fun onDestroyActionMode(mode:ActionMode){}
        }
    }},update={view->
        view.textSize=17f*scale;view.setTextColor(foreground)
        view.setLineSpacing((view.textSize*1.6f-view.paint.fontSpacing).coerceAtLeast(0f),1f)
        val styled=SpannableString(projection.text)
        val paragraphGap=(10f*view.resources.displayMetrics.density-view.lineSpacingExtra).toInt().coerceAtLeast(1)
        projection.paragraphGaps.forEach{at->styled.setSpan(NoteParagraphGap(at,paragraphGap),at,at+1,Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)}
        presentation.code.forEach{raw->val range=projection.displayRange(raw);styled.setSpan(TypefaceSpan("monospace"),range.first,range.last+1,Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)}
        presentation.strong.forEach{raw->val range=projection.displayRange(raw);styled.setSpan(StyleSpan(Typeface.BOLD),range.first,range.last+1,Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)}
        annotations.filterNot{it.archived}.forEach { a ->val from=text.indexOf(a.quote);if(from>=0 && a.quote.isNotEmpty()){
            val range=projection.displayRange(from until from+a.quote.length)
            styled.setSpan(if(a.style=="underline")UnderlineSpan()else BackgroundColorSpan(highlight),range.first,range.last+1,Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
        } }
        val renderedKey=Triple(annotations,highlight,presentation)
        if(view.text.toString()!=projection.text || view.tag!=renderedKey){view.text=styled;view.tag=renderedKey}
    })
}
@Composable fun FlowButtons(options:List<Pair<String,String>>,selected:String,onSelect:(String)->Unit){
    @OptIn(ExperimentalLayoutApi::class)
    FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(8.dp)){options.forEach{(id,label)->FilterChip(selected=selected==id,onClick={onSelect(id)},label={Text(label)},modifier=Modifier.heightIn(min=48.dp),colors=FilterChipDefaults.filterChipColors(selectedContainerColor=MaterialTheme.colorScheme.primaryContainer,selectedLabelColor=MaterialTheme.colorScheme.onPrimaryContainer))}}
}
