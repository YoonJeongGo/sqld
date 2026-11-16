package kr.sqld.study

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp

internal val ReadingBlue=Color(0xFFD9E9FF)
internal val ReadingInk=Color(0xFF111827)

@Composable internal fun ReadingText(text:String,highlights:List<String> = emptyList(),active:List<String> = emptyList()){
    StudyBodyText(text,emphasis=highlights,active=active)
}

/** Rows are rendered only inside this bounded viewport. SQL NULL is never the string "NULL". */
@Composable internal fun ReadingTable(table:DataTable,focusCells:List<FocusCell> = emptyList(),focusRows:List<Int> = emptyList(),modifier:Modifier=Modifier){
    val measurer=rememberTextMeasurer()
    val density=LocalDensity.current
    val bodyStyle=MaterialTheme.typography.bodyMedium
    val columnWidths=remember(table,bodyStyle,density){table.columns.indices.map{column->
        val values=listOf(table.columns[column])+table.rows.take(120).map{it[column]?:"NULL ∅"}
        val pixels=values.maxOf{measurer.measure(it,style=bodyStyle,softWrap=false).size.width}
        (with(density){pixels.toDp()}+20.dp).coerceIn(112.dp,260.dp)
    }}
    Column(modifier,verticalArrangement=Arrangement.spacedBy(6.dp)){
        Text(table.title,style=MaterialTheme.typography.titleSmall)
        if(table.rows.isEmpty())Text("결과 0행",style=MaterialTheme.typography.bodyMedium)
        Column(Modifier.horizontalScroll(rememberScrollState()).border(1.dp,MaterialTheme.colorScheme.outlineVariant)){
            Row(Modifier.background(MaterialTheme.colorScheme.surfaceVariant)){
                Text("행",Modifier.width(52.dp).padding(8.dp),style=MaterialTheme.typography.labelMedium)
                table.columns.forEachIndexed { column,name ->
                    val focused=focusCells.any{it.column==column}
                    Text(name,Modifier.width(columnWidths[column]).then(if(focused)Modifier.background(ReadingBlue)else Modifier).padding(8.dp),style=MaterialTheme.typography.labelLarge,color=if(focused)ReadingInk else MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
            if(table.rows.isNotEmpty())LazyColumn(Modifier.width(columnWidths.fold(52.dp){sum,width->sum+width}).heightIn(max=220.dp).testTag("reading-table-rows")){
                itemsIndexed(table.rows){row,values->
                    Row(Modifier.fillMaxWidth().background(if(row in focusRows)ReadingBlue else MaterialTheme.colorScheme.surface)){
                        Text(if(row in focusRows)"현재\n${row+1}"else"${row+1}",Modifier.width(52.dp).padding(8.dp),style=MaterialTheme.typography.labelMedium,color=if(row in focusRows)ReadingInk else MaterialTheme.colorScheme.onSurfaceVariant)
                        values.forEachIndexed { column,value ->
                            val focused=row in focusRows||FocusCell(row,column) in focusCells
                            Text(value?:"NULL ∅",Modifier.width(columnWidths[column]).then(if(focused)Modifier.background(ReadingBlue)else Modifier).padding(8.dp),style=MaterialTheme.typography.bodyMedium,fontWeight=if(focused)FontWeight.Bold else FontWeight.Normal,color=if(focused)ReadingInk else MaterialTheme.colorScheme.onSurface)
                        }
                    }
                    HorizontalDivider(color=MaterialTheme.colorScheme.outlineVariant)
                }
            }
        }
    }
}

@Composable internal fun BoundInkSql(ui:StudyUi,source:WalkSource,ranges:List<IntRange>,modifier:Modifier=Modifier){
    val sourceId=remember(source){"sql:${source.id}:${source.fingerprint()}"}
    val documentId=remember(sourceId,source.sql){InkStore.documentId(sourceId,source.sql.orEmpty())}
    val drafts by ui.vm.inkDrafts.collectAsState()
    val errors by ui.vm.inkErrors.collectAsState()
    val document=drafts[documentId]?:ui.state.inkDocuments.find{it.id==documentId}
    InkSqlSurface(source.sql.orEmpty(),sourceId,document,ranges,{ui.vm.saveInk(it)},modifier,textScale=ui.state.settings.textScale,
        saveStatus=when{documentId in errors->"저장 실패 · 초안 유지 · 펜 설정에서 재시도";documentId in drafts->"필기 저장 중";document!=null->"필기 저장됨";else->null},
        onRetrySave=if(documentId in errors)({drafts[documentId]?.let{ui.vm.saveInk(it)};Unit})else null)
}

@Composable internal fun SqlSourcePane(ui:StudyUi,source:WalkSource,ranges:List<IntRange>,wide:Boolean,modifier:Modifier=Modifier){
    var original by rememberSaveable(source.id){mutableStateOf(wide&&source.tables.isNotEmpty())}
    var originalDialog by rememberSaveable(source.id){mutableStateOf(false)}
    Column(modifier.padding(horizontal=12.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){
        BoundInkSql(ui,source,ranges,Modifier.weight(1f).fillMaxWidth())
        if(source.tables.isNotEmpty()){
            TextButton(onClick={if(wide)original=!original else originalDialog=true},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("reader-original-toggle")){
                Text(if(!wide)"원본 표 보기"else if(original)"문제·원본 테이블 접기"else"문제·원본 테이블 보기",Modifier.weight(1f))
                Icon(if(original&&wide)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,null)
            }
            if(original&&wide)Column(Modifier.fillMaxWidth().heightIn(max=230.dp).verticalScroll(rememberScrollState()).testTag("reader-original-tables"),verticalArrangement=Arrangement.spacedBy(12.dp)){
                Text(source.stem,style=MaterialTheme.typography.bodySmall)
                source.tables.forEach{ReadingTable(it.copy(title="원본 테이블 · ${it.title}"))}
            }
        }
    }
    if(originalDialog)AlertDialog(onDismissRequest={originalDialog=false},title={Text("문제·원본 테이블")},text={Column(Modifier.verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(12.dp)){
        Text(source.stem,style=MaterialTheme.typography.bodyMedium)
        source.tables.forEach{ReadingTable(it.copy(title="원본 테이블 · ${it.title}"))}
    }},confirmButton={TextButton(onClick={originalDialog=false}){Text("코드·해설로 돌아가기")}})
}

@OptIn(ExperimentalLayoutApi::class)
@Composable internal fun WalkNarrative(walk:SqlWalkthrough,stepIndex:Int,onStep:(Int)->Unit,foundations:Boolean,onFoundations:(Boolean)->Unit,modifier:Modifier=Modifier,extra:@Composable ()->Unit={}){
    val step=walk.steps[stepIndex.coerceIn(walk.steps.indices)]
    var evidence by rememberSaveable(walk.id){mutableStateOf(false)}
    val scroll=key(walk.id,step.id){rememberScrollState()}
    Column(modifier){
        Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(scroll).padding(12.dp).testTag("walk-narrative"),verticalArrangement=Arrangement.spacedBy(10.dp)){
            Column(verticalArrangement=Arrangement.spacedBy(4.dp)){
                Text(step.title,style=MaterialTheme.typography.titleLarge,modifier=Modifier.testTag("walk-step-title"))
                Text(walk.narrativeLabel,style=MaterialTheme.typography.labelMedium,color=MaterialTheme.colorScheme.onSurfaceVariant)
            }
            if(stepIndex==0)StudyBodyText(walk.intro)
            step.codeFocus.forEach{focus->Surface(color=ReadingBlue,contentColor=ReadingInk,shape=RoundedCornerShape(4.dp)){
                Text(focus.needle,Modifier.padding(8.dp).horizontalScroll(rememberScrollState()),style=MaterialTheme.typography.bodyMedium,fontWeight=FontWeight.Bold,softWrap=false)
            }}
            ReadingText(step.text,step.highlights,step.highlights.filter{phrase->step.codeFocus.any{BodyTextRules.firstPhraseIndex(it.needle,phrase)>=0}})
            step.table?.let{ReadingTable(it.copy(title=if(it.title.startsWith("학습용"))it.title else "학습용 중간·결과표 · ${it.title}"),step.focusCells,step.focusRows)}
            TextButton(onClick={onFoundations(!foundations)},modifier=Modifier.fillMaxWidth().testTag("walk-foundations-toggle")){
                Text("이 구문의 기초",Modifier.weight(1f));Icon(if(foundations)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,null)
            }
            if(foundations)Column(Modifier.testTag("walk-foundations"),verticalArrangement=Arrangement.spacedBy(12.dp)){
                walk.terms.forEach{term->
                    Column(verticalArrangement=Arrangement.spacedBy(4.dp)){
                        Text("${term.token} · ${term.kind}",style=MaterialTheme.typography.titleSmall,color=MaterialTheme.colorScheme.primary)
                        StudyBodyText(term.meaning,emphasis=listOf(term.token))
                        StudyBodyText("이 문제에서는 · ${term.role}",emphasis=listOf(term.token),style=MaterialTheme.typography.bodyMedium)
                    }
                }
            }
            extra()
            TextButton(onClick={evidence=!evidence}){Text(if(evidence)"검증 범위 접기"else"검증 범위 보기")}
            if(evidence){
                Text(walk.verification.method,style=MaterialTheme.typography.bodySmall)
                if(walk.verification.engine.isNotBlank())Text("별도 검산: ${walk.verification.engine} ${walk.verification.engineVersion} · ${walk.verification.queryMode}",style=MaterialTheme.typography.bodySmall)
                walk.verification.notes.forEach{Text(it,style=MaterialTheme.typography.bodySmall)}
            }
        }
        Surface(tonalElevation=2.dp){Row(Modifier.fillMaxWidth().heightIn(min=48.dp).padding(horizontal=8.dp),verticalAlignment=Alignment.CenterVertically){
            IconButton(enabled=stepIndex>0,onClick={onStep(stepIndex-1)},modifier=Modifier.testTag("walk-previous")){Icon(Icons.Outlined.ChevronLeft,"이전 해설 단계")}
            Text("${stepIndex+1} / ${walk.steps.size}",Modifier.weight(1f),style=MaterialTheme.typography.labelLarge)
            Text("직접 따라 읽기",style=MaterialTheme.typography.labelMedium)
            IconButton(enabled=stepIndex<walk.steps.lastIndex,onClick={onStep(stepIndex+1)},modifier=Modifier.testTag("walk-next")){Icon(Icons.Outlined.ChevronRight,"다음 해설 단계")}
        }}
    }
}

/** The state owners sit above the width branches, so rotate/split-screen does not reset a step. */
@Composable internal fun SqlReadingLayout(ui:StudyUi,source:WalkSource,ranges:List<IntRange>,modifier:Modifier=Modifier,left:@Composable (Modifier)->Unit){
    BoxWithConstraints(modifier){
        val wide=maxWidth>=840.dp||(maxWidth>=560.dp&&maxHeight<360.dp)
        val availableHeight=maxHeight
        val textScale=LocalDensity.current.fontScale*ui.state.settings.textScale
        val codeMinimum=80.dp+(if(source.tables.isEmpty())0.dp else 56.dp)+maxOf(48.dp,(44f*textScale).dp)
        if(wide)Row(Modifier.fillMaxSize().testTag("sql-reader-wide")){
            left(Modifier.weight(1f).fillMaxHeight())
            VerticalDivider()
            if(availableHeight<codeMinimum+24.dp)Column(Modifier.weight(1f).fillMaxHeight().verticalScroll(rememberScrollState())){
                SqlSourcePane(ui,source,ranges,false,Modifier.height(codeMinimum+24.dp).fillMaxWidth())
            }else SqlSourcePane(ui,source,ranges,availableHeight>=420.dp,Modifier.weight(1f).fillMaxHeight())
        } else if(availableHeight<codeMinimum+160.dp){
            // A very short split window cannot hold two useful viewports. Scroll fixed-height panes
            // instead of shrinking the native SQL canvas to zero beneath its pen toolbar.
            Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).testTag("sql-reader-compact")){
                SqlSourcePane(ui,source,ranges,false,Modifier.height(codeMinimum+24.dp).fillMaxWidth())
                HorizontalDivider()
                left(Modifier.height(260.dp).fillMaxWidth())
            }
        }else Column(Modifier.fillMaxSize().testTag("sql-reader-compact")){
            // Keep the first source line including its baseline/descent inside the canvas at large fonts.
            val codeHeight=maxOf(availableHeight*.43f,codeMinimum).coerceAtMost((availableHeight-80.dp).coerceIn(0.dp,availableHeight))
            SqlSourcePane(ui,source,ranges,false,Modifier.height(codeHeight).fillMaxWidth())
            HorizontalDivider()
            left(Modifier.weight(1f).fillMaxWidth())
        }
    }
}

@Composable internal fun LearningWalkLinks(ui:StudyUi,noteId:String){
    var examples by remember(noteId){mutableStateOf<List<LearningWalkRef>>(emptyList())}
    LaunchedEffect(noteId){examples=runCatching{ui.vm.walkthroughs.learningFor(noteId)}.getOrDefault(emptyList())}
    if(examples.isNotEmpty())Paper{
        Text("작은 표부터 SQL 따라 읽기",style=MaterialTheme.typography.titleMedium)
        examples.forEach{example->OutlinedButton(onClick={ui.nav("walk:${example.id}")},modifier=Modifier.fillMaxWidth()){Text(example.title)}}
    }
}

@Composable internal fun LearningWalkScreen(ui:StudyUi,id:String){
    var walk by remember(id){mutableStateOf<SqlWalkthrough?>(null)}
    var finished by remember(id){mutableStateOf(false)}
    var step by rememberSaveable(id){mutableIntStateOf(0)}
    var foundations by rememberSaveable(id){mutableStateOf(false)}
    LaunchedEffect(id){walk=runCatching{ui.vm.walkthroughs.learning(id)}.getOrNull();finished=true}
    val material=walk
    if(material==null){Column(Modifier.padding(20.dp)){Text(if(finished)"이 예시를 불러오지 못했어요. 기존 개념 노트는 그대로 사용할 수 있어요."else"학습 예시를 여는 중이에요.")};return}
    val selected=step.coerceIn(material.steps.indices)
    SqlReadingLayout(ui,material.source,WalkthroughRules.ranges(material.source.sql.orEmpty(),material.steps[selected].codeFocus),Modifier.fillMaxSize()) { modifier ->
        WalkNarrative(material,selected,{step=it},foundations,{foundations=it},modifier)
    }
}
