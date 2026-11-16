package kr.sqld.study

import android.annotation.SuppressLint
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.flow.debounce
import kotlinx.coroutines.flow.distinctUntilChanged
import java.io.ByteArrayInputStream

private val lessonSections = listOf(
    "overview" to "핵심 정리", "concepts" to "개념", "examples" to "예제", "checks" to "자기 점검"
)

private fun lessonPriority(ui:StudyUi,lesson:CourseLesson):StudyPriority? = lesson.relatedNoteIds
    .mapNotNull { id -> ui.pack.notes.find { it.id == id } }
    .mapNotNull { StudyGuide.priority(ui.pack,it.objectiveId) }
    .minByOrNull { StudyGuide.rank(it.level) }

private fun checkCount(lesson:CourseLesson,progress:CourseProgress,rating:String):Int =
    lesson.selfChecks.count { check -> progress.checks.any { it.checkId == check.id && it.rating == rating } }

private fun changeCourse(ui:StudyUi,generation:Long,change:(StudyState)->StudyState){
    ui.vm.mutate { state -> if(ui.vm.repository.restoreGeneration==generation)change(state)else state }
}

@Composable fun CourseScreen(ui:StudyUi,reviewOnly:Boolean=false){
    val course=ui.course
    var query by rememberSaveable { mutableStateOf("") }
    var filter by rememberSaveable(reviewOnly) { mutableStateOf(if(reviewOnly)"review"else"all") }
    var partFilter by rememberSaveable { mutableStateOf("all") }
    var showParts by rememberSaveable { mutableStateOf(false) }
    var showProgressGuide by rememberSaveable { mutableStateOf(false) }
    val normalized=query.trim().lowercase()
    val visualSearch=remember(ui.courseVisuals){course.lessons.associate{it.id to ui.courseVisuals.searchText(it.id).map(String::lowercase)}}
    val progressById=ui.state.courseProgress.associateBy { it.lessonId }
    fun progress(lesson:CourseLesson)=progressById[lesson.id]?:CourseProgress(lesson.id)
    val read=course.lessons.count { progress(it).readVersion >= it.version }
    val examples=course.lessons.sumOf { lesson -> lesson.examples.count { it.id in progress(lesson).revealedResults } }
    val understood=course.lessons.sumOf { checkCount(it,progress(it),"understood") }
    val toReview=course.lessons.sumOf { checkCount(it,progress(it),"review") }
    val lessons=course.lessons.filter { lesson ->
        val p=progress(lesson)
        (partFilter=="all" || lesson.partId==partFilter) &&
            (normalized.isBlank() || listOf(lesson.title,lesson.id,lesson.easy,lesson.memory)
                .plus(lesson.concepts.flatMap { listOf(it.term,it.meaning) }).any { it.lowercase().contains(normalized) } || visualSearch[lesson.id].orEmpty().any{it.contains(normalized)}) &&
            when(filter){
                "unread" -> p.readVersion < lesson.version
                "read" -> p.readVersion >= lesson.version
                "review" -> checkCount(lesson,p,"review") > 0
                else -> true
            }
    }
    val resume=CourseJourney.resume(course,ui.state)
    LazyColumn(Modifier.fillMaxSize().testTag("course-list"),contentPadding=PaddingValues(20.dp),verticalArrangement=Arrangement.spacedBy(20.dp)){
        item { PageTitle("", "학습 진도", "아래 강의 순서가 공부할 순서예요.") }
        item {
            Paper {
                Text("읽은 강의 $read / ${course.lessons.size}",style=MaterialTheme.typography.titleLarge)
                LinearProgressIndicator(progress={if(course.lessons.isEmpty())0f else read.toFloat()/course.lessons.size},modifier=Modifier.fillMaxWidth())
                if(toReview>0) Text("다시 볼 자기 점검 ${toReview}개",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.primary)
                TextButton(onClick={showProgressGuide=!showProgressGuide}){
                    Text(if(showProgressGuide)"진도 집계 안내 접기"else"진도 집계 안내")
                    Icon(if(showProgressGuide)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,null)
                }
                if(showProgressGuide){
                    Text("예제 확인 $examples / ${course.lessons.sumOf { it.examples.size }}개\n스스로 이해 확인 $understood / ${course.lessons.sumOf { it.selfChecks.size }}개",style=MaterialTheme.typography.bodySmall)
                    Text("읽은 강의는 자료 읽음을 직접 표시한 수예요. 예제와 확인 문제는 별도로 보존되며 시험 점수·숙달 판정이 아니에요.",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
        if(resume!=null) item {
            Paper(modifier=Modifier.testTag("course-resume"),accent=true){
                Eyebrow("지금 공부할 강의")
                Text("${course.lessons.indexOf(resume)+1}강 · ${resume.title}",style=MaterialTheme.typography.titleMedium)
                Text("${lessonSections.find { it.first==progress(resume).section }?.second?:"핵심 정리"}에서 계속해요.",style=MaterialTheme.typography.bodyMedium)
                Button(onClick={ui.nav("lesson:${resume.id}")},modifier=Modifier.fillMaxWidth()){Text("이 강의 계속하기")}
            }
        }
        item {
            OutlinedTextField(query,{query=it},modifier=Modifier.fillMaxWidth(),singleLine=true,label={Text("강의·개념 검색")},leadingIcon={Icon(Icons.Outlined.Search,null)})
            FlowButtons(listOf("all" to "전체","unread" to "읽기 전","read" to "읽음","review" to "다시 볼 점검"),filter,{filter=it})
            TextButton(onClick={showParts=!showParts}){Text(if(showParts)"단원 선택 접기"else"단원 선택");Icon(if(showParts)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,null)}
            if(showParts) FlowButtons(listOf("all" to "모든 단원")+course.parts.map { it.id to "${it.id} ${it.title}" },partFilter,{partFilter=it})
            if(!showParts&&partFilter!="all") Text(course.parts.find { it.id==partFilter }?.title.orEmpty(),style=MaterialTheme.typography.bodySmall)
            Text("${lessons.size}강",style=MaterialTheme.typography.titleSmall)
        }
        if(lessons.isEmpty()) item { EmptyState("조건에 맞는 강의가 없어요","검색어나 진도 조건을 바꾸어 보세요.","전체 강의 보기",{query="";filter="all";partFilter="all"}) }
        course.parts.forEach { part ->
            val inPart=lessons.filter { it.partId==part.id }
            if(inPart.isNotEmpty()){
                item(key="part:${part.id}"){
                    Column(verticalArrangement=Arrangement.spacedBy(6.dp)){
                        Eyebrow(part.id)
                        Text(part.title,style=MaterialTheme.typography.titleLarge)
                        val allPart=course.lessons.filter { it.partId==part.id }
                        Text("읽음 ${allPart.count { progress(it).readVersion>=it.version }} / ${allPart.size}강",style=MaterialTheme.typography.bodySmall)
                    }
                }
                items(inPart,key={it.id}) { lesson ->
                    val p=progress(lesson)
                    val exampleCount=lesson.examples.count { it.id in p.revealedResults }
                    Column(verticalArrangement=Arrangement.spacedBy(4.dp)){
                        lessonPriority(ui,lesson)?.let { PriorityBadge(it) }
                        NoteRow("${course.lessons.indexOf(lesson)+1}강",lesson.title,
                            "${if(p.readVersion>=lesson.version)"읽음"else if(p.readVersion>0)"보강 내용 확인 전"else"읽기 전"} · 예제 $exampleCount/${lesson.examples.size} · 이해 확인 ${checkCount(lesson,p,"understood")}/${lesson.selfChecks.size}"+
                                if(checkCount(lesson,p,"review")>0)" · 다시 볼 점검 ${checkCount(lesson,p,"review")}개"else"",
                            {ui.nav("lesson:${lesson.id}")})
                    }
                }
            }
        }
        item { TextButton(onClick={ui.nav("notes")}){Text("개념 찾기")} }
        item { OutlinedButton(onClick={ui.nav("unit")},modifier=Modifier.fillMaxWidth().testTag("course-unit-practice")){Text("단원별 복습 문제")}}
    }
}

@OptIn(ExperimentalLayoutApi::class,FlowPreview::class)
@Composable fun CourseLessonScreen(ui:StudyUi,id:String){
    val lesson=ui.course.lessons.find { it.id==id }?:return
    val additional=rememberLessonGuide(ui,lesson)
    val progress=CourseStudy.progress(ui.state,id)
    val generation=remember(id){ui.vm.repository.restoreGeneration}
    var section by rememberSaveable(id) { mutableStateOf(progress.section.takeIf { current -> lessonSections.any { it.first==current } }?:"overview") }
    val position=ui.course.lessons.indexOf(lesson)
    val previous=ui.course.lessons.getOrNull(position-1)
    val next=ui.course.lessons.getOrNull(position+1)
    val status=CourseJourney.status(lesson,ui.state)
    val busy by ui.vm.busy.collectAsState()
    var tools by rememberSaveable(id){mutableStateOf(false)}
    fun selectSection(value:String,markRead:Boolean=false){
        if(value==section&&!markRead)return
        ui.vm.launchWork{
            val result=ui.vm.repository.update { s ->
                check(ui.vm.repository.restoreGeneration==generation){"기록을 복원한 뒤에는 강의를 다시 열어 주세요."}
                CourseStudy.update(s,id,change={it.copy(section=value,scroll=0,readVersion=if(markRead)maxOf(it.readVersion,lesson.version) else it.readVersion)})
            }
            if(CourseStudy.progress(result,id).section==value)section=value
        }
    }
    fun advanceLesson(){
        ui.vm.launchWork{
            ui.vm.repository.update { state ->
                check(ui.vm.repository.restoreGeneration==generation){"기록을 복원한 뒤에는 강의를 다시 열어 주세요."}
                check(CourseJourney.status(lesson,state).complete){"예제 확인과 확인 문제의 이해·다시 보기 표시를 마친 뒤 이동해 주세요."}
                state
            }
            if(next!=null)ui.nav("lesson:${next.id}")else ui.nav("course")
        }
    }
    Column(Modifier.fillMaxSize().testTag("lesson-reader")){
        Surface(tonalElevation=1.dp){
            FlowRow(Modifier.fillMaxWidth().padding(horizontal=16.dp,vertical=6.dp),horizontalArrangement=Arrangement.spacedBy(6.dp),verticalArrangement=Arrangement.spacedBy(2.dp)){
                lessonSections.forEachIndexed { at,(key,_) ->
                    val label=listOf("설명","개념","예제","확인")[at]
                    FilterChip(selected=section==key,enabled=!busy,onClick={selectSection(key)},label={Text("${at+1} $label")},modifier=Modifier.heightIn(min=48.dp).testTag("lesson-section-$key"))
                }
            }
        }
        key(id,section){
            val scroll=rememberScrollState(if(progress.section==section)progress.scroll else 0)
            fun saveScroll(position:Int){
                changeCourse(ui,generation) { state ->
                    val current=CourseStudy.progress(state,id)
                    if(current.section!=section || current.scroll==position) state
                    else CourseStudy.update(state,id,change={it.copy(scroll=position)}).copy(lastLessonId=state.lastLessonId)
                }
            }
            LaunchedEffect(id,section,scroll){ snapshotFlow { scroll.value }.debounce(250).distinctUntilChanged().collect { saveScroll(it) } }
            DisposableEffect(id,section,scroll){ onDispose { saveScroll(scroll.value) } }
            Box(Modifier.weight(1f).fillMaxWidth(),contentAlignment=Alignment.TopCenter){
                Column(Modifier.fillMaxWidth().verticalScroll(scroll).padding(16.dp),verticalArrangement=Arrangement.spacedBy(16.dp)){
                    PageTitle("${ui.course.parts.find { it.id==lesson.partId }?.title.orEmpty()}",lesson.title)
                    Text("${position+1} / ${ui.course.lessons.size}강 · ${if(progress.readVersion>=lesson.version)"자료 읽음"else if(progress.readVersion>0)"보강 내용 확인 전 · 이전 읽음 기록 유지"else"자료 읽기 전"}",modifier=Modifier.testTag("lesson-position"),style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
                    when(section){
                        "overview" -> CourseOverview(ui,lesson)
                        "concepts" -> {
                            Text("이 강의의 개념 ${lesson.concepts.size}개",style=MaterialTheme.typography.titleLarge)
                            lesson.concepts.forEachIndexed { index,concept ->
                                StudyPaper {
                                    Eyebrow("개념 ${index+1}")
                                    StudySection(concept.term){CourseText(concept.meaning,listOf(concept.term))}
                                    if(concept.example.isNotBlank()){
                                        StudySection("예를 들면"){CourseText(concept.example,listOf(concept.term))}
                                    }
                                }
                            }
                        }
                        "examples" -> {
                            val guide=ui.courseVisuals.guide(id)
                            if(ui.courseVisuals.forLesson(id).isNotEmpty())StudyPaper(accent=true){
                                StudySection("기존 SQL 예제로 연습하기"){
                                    VisualText("앞에서 본 그림과 다른 데이터로 연습해요. 아래 입력표의 이름·식별자·값을 기준으로 풀이하고, 그림의 결과를 이 예제의 답으로 사용하지 마세요.",listOf("다른 데이터","아래 입력표의 이름·식별자·값"))
                                }
                            }
                            StudySection("단계별 예제 ${lesson.examples.size}개"){
                                StudyBodyText("입력 표와 SQL을 보고 결과를 예상한 뒤, 풀이 단계를 하나씩 확인해요.")
                            }
                            lesson.examples.forEach { example -> key(example.id){CourseExampleCard(ui,lesson,example,progress,generation,additional.material)} }
                            if(lesson.examples.isNotEmpty()&&lesson.examples.all{it.id in progress.revealedResults}){
                                guide?.exampleReadingGuide?.takeIf{it.isNotBlank()}?.let{explanation->
                                    StudyPaper(modifier=Modifier.testTag("course-example-comparison-${lesson.id}")){
                                        StudySection("그림과 예제 비교 해설"){VisualText(explanation,lesson.concepts.map{it.term})}
                                    }
                                }
                            }
                        }
                        "checks" -> {
                            StudySection("직접 설명해 보기"){
                                StudyBodyText("먼저 내 말로 답을 적고 예시 답안과 비교해요. 자동 채점 없이 스스로 이해 여부를 표시하며, 시험 점수에 합산하지 않아요.")
                            }
                            lesson.selfChecks.forEachIndexed { index,check -> key(check.id){CourseCheckCard(ui,lesson,check,index+1,progress,generation,additional.material?.checkGuides?.find{it.checkId==check.id})} }
                        }
                    }
                    TextButton(onClick={tools=!tools},modifier=Modifier.fillMaxWidth().testTag("lesson-tools-toggle").semantics{stateDescription=if(tools)"펼쳐짐"else"접힘"}){
                        Text(if(tools)"추가 학습 도구 접기"else"추가 해설·문제·학습 도구",Modifier.weight(1f))
                        Icon(if(tools)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,null)
                    }
                    if(tools){
                    LessonGuideEntry(ui,lesson,additional)
                    if(section=="overview"&&ui.courseVisuals.forLesson(id).isNotEmpty()){
                        OutlinedButton(onClick={selectSection("examples")},modifier=Modifier.fillMaxWidth().testTag("visual-to-examples")){Text("예제로 바로 이동")}
                    }
                    OutlinedButton(onClick={ui.nav("unit:${lesson.partId}:${lesson.id}")},modifier=Modifier.fillMaxWidth()){Text("이 강의 유형별 복습")}
                    Paper {
                        Text("강의 자료 진도",style=MaterialTheme.typography.titleMedium)
                        Text("내용을 읽었다면 직접 표시해 주세요. 개념 노트와 문제풀이 기록은 각각 유지돼요.",style=MaterialTheme.typography.bodySmall)
                        OutlinedButton(onClick={changeCourse(ui,generation) { s -> CourseStudy.read(s,lesson,CourseStudy.progress(s,id).readVersion<lesson.version) }},modifier=Modifier.fillMaxWidth().testTag("lesson-read-toggle")){
                            Icon(if(progress.readVersion>=lesson.version)Icons.Outlined.CheckCircle else Icons.Outlined.RadioButtonUnchecked,null)
                            Spacer(Modifier.width(8.dp));Text(if(progress.readVersion>=lesson.version)"읽음 표시됨 · 취소"else"이 강의 자료 읽음 표시")
                        }
                    }
                    CourseConnections(ui,lesson)
                    if(lesson.bridge.isNotBlank()) CourseText(lesson.bridge,lesson.concepts.map{it.term})
                    FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(6.dp)){
                        previous?.let { OutlinedButton(onClick={ui.nav("lesson:${it.id}")}){Text("이전 강의")} }
                        next?.let { OutlinedButton(onClick={ui.nav("lesson:${it.id}")}){Text("다음 강의로 바로 이동")} }
                        TextButton(onClick={ui.nav("course")}){Text("63강 전체 목차")}
                    }
                    }
                }
            }
        }
        val stage=lessonSections.indexOfFirst{it.first==section}+1
        val examplesReady=status.examplesDone==lesson.examples.size
        val checksReady=status.checksDone==lesson.selfChecks.size
        val ready=section!="examples"||examplesReady
        val canAdvance=ready&&(section!="checks"||!status.read||!examplesReady||checksReady)
        val label=when(section){
            "overview"->"다음: 개념 읽기"
            "concepts"->"읽기 완료 · 예제 보기"
            "examples"->"다음: 확인 문제"
            else->when{!status.read->"읽기 단계 확인하기";!examplesReady->"예제 마저 확인하기";next!=null->"다음 강의: ${next.title}";else->"전체 진도 확인"}
        }
        Surface(tonalElevation=3.dp,shadowElevation=2.dp){
            Column(Modifier.fillMaxWidth().padding(horizontal=16.dp,vertical=8.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){
                Text(when(section){
                    "examples"->"$stage / 4단계 · 예제 결과 ${status.examplesDone} / ${lesson.examples.size}개 확인"
                    "checks"->"$stage / 4단계 · 이해 또는 다시 보기 ${status.checksDone} / ${lesson.selfChecks.size}개 표시"
                    else->"$stage / 4단계 · ${if(section=="overview")"설명을 읽고 개념으로 이어가요."else"개념을 읽었으면 아래 버튼을 눌러요."}"
                },style=MaterialTheme.typography.bodySmall)
                Button(enabled=canAdvance&&!busy,modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("lesson-next-step"),onClick={
                    when(section){
                        "overview"->selectSection("concepts")
                        "concepts"->selectSection("examples",markRead=true)
                        "examples"->selectSection("checks")
                        else->when{!status.read->selectSection("concepts");!examplesReady->selectSection("examples");else->advanceLesson()}
                    }
                }){Text(label)}
            }
        }
    }
}

@Composable private fun CourseOverview(ui:StudyUi,lesson:CourseLesson){
    val guide=ui.courseVisuals.guide(lesson.id)
    val visuals=ui.courseVisuals.forLesson(lesson.id)
    val terms=lesson.concepts.map{it.term}
    StudyPaper(accent=true){
        Eyebrow("쉽게 이해하기")
        CourseText(lesson.easy,terms)
        guide?.easySupplement?.takeIf{it.isNotBlank()}?.let{VisualText(it,terms)}
        if(lesson.why.isNotBlank()){
            StudySection("왜 배우나요?"){CourseText(lesson.why,terms)}
        }
    }
    Text("인물·점수·금액은 학습용 가상 데이터예요.",style=MaterialTheme.typography.bodySmall)
    visuals.forEach{visual->key(visual.id){CourseVisualCard(ui.courseVisuals,visual)}}
    if(visuals.isNotEmpty()){
        VisualText("이 그림들은 개념을 이해하기 위한 별도 예시예요. 다음에는 기존 교재의 입력표와 SQL로 연습해요. 이름·식별자·숫자가 달라지므로 아래 예제의 표를 새로 확인하세요.")
    }
    lessonPriority(ui,lesson)?.let { priority ->
        PriorityDetails(ui.pack,priority)
        Text("연결된 개념 노트의 학습 중요도예요. 실제 시험 출제 횟수를 뜻하지 않아요.",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
    }
    StudyPaper {
        StudySection("기억할 내용"){CourseText(lesson.memory,terms)}
    }
    if(lesson.traps.isNotEmpty()) StudyPaper {
        StudySection("헷갈리기 쉬운 지점"){
            lesson.traps.forEachIndexed { index,trap -> CourseText("${index+1}. $trap",terms) }
        }
    }
    guide?.syntaxCaution?.takeIf{it.isNotBlank()}?.let{StudyPaper{StudySection("문법·변형·주의"){StudyWarning(it)}}}
    if(lesson.diagramSvg.isNotBlank()) CourseDiagram(lesson.diagramSvg)
    var details by rememberSaveable(lesson.id) { mutableStateOf(false) }
    TextButton(onClick={details=!details}){Text(if(details)"자료 안내 접기"else"강의 시간·자료 안내");Icon(if(details)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,null)}
    if(details) Paper {
        Text("원 강의 시간 안내: ${lesson.lectureMinutes}분",style=MaterialTheme.typography.titleSmall)
        Text("영상 강의의 안내 시간이며, 이 앱 자료의 예상 학습 시간이나 수강 기록은 아니에요.",style=MaterialTheme.typography.bodySmall)
        Text(ui.course.provenance,style=MaterialTheme.typography.bodySmall)
        Text(ui.course.reviewNote,style=MaterialTheme.typography.bodySmall)
        val sources=lesson.sourceIds.mapNotNull { id -> ui.course.sources.find { it.id==id } }
        if(sources.isNotEmpty()){
            Text("참고 자료",style=MaterialTheme.typography.titleSmall)
            sources.forEach { source -> Text(source.title,style=MaterialTheme.typography.bodySmall) }
        }
    }
}

@Composable private fun CourseExampleCard(ui:StudyUi,lesson:CourseLesson,example:CourseExample,progress:CourseProgress,generation:Long,guide:LessonGuide?=null){
    val shown=(progress.exampleSteps[example.id]?:0).coerceIn(0,example.steps.size)
    val revealed=example.id in progress.revealedResults
    StudyPaper {
        StudySection(example.title){SelectionContainer{Text(example.question,style=MaterialTheme.typography.bodyLarge)}}
        example.tables.forEach { StudyTable(it) }
        if(example.sql.isNotBlank()){
            Text(when(example.mode){"oracle"->"Oracle 문법 예제";"sqlite"->"SQLite 확인용 예제";else->"SQL 예제"},style=MaterialTheme.typography.labelLarge)
            SqlBlock(example.sql,ui.state.settings.wrapSql,{wrap->ui.vm.settings { it.copy(wrapSql=wrap) }})
        }
        if(example.steps.isNotEmpty()){
            GuideExampleLink(ui,lesson,guide,example)
            Text("풀이 단계 $shown / ${example.steps.size}",style=MaterialTheme.typography.titleMedium)
            example.steps.take(shown).forEachIndexed { index,step ->
                Column(verticalArrangement=Arrangement.spacedBy(6.dp)){
                    Eyebrow("${index+1}단계")
                    CourseText(step,lesson.concepts.map{it.term},example.tables.flatMap{it.columns})
                }
            }
            if(shown<example.steps.size) OutlinedButton(onClick={changeCourse(ui,generation) { s -> CourseStudy.update(s,lesson.id,change={p->p.copy(exampleSteps=p.exampleSteps+(example.id to minOf(example.steps.size,(p.exampleSteps[example.id]?:0)+1)))}) }},modifier=Modifier.fillMaxWidth().testTag("course-example-next-${example.id}")){Text(if(shown==0)"첫 풀이 단계 보기"else"다음 풀이 단계 보기")}
        }
        if(!revealed) Button(onClick={changeCourse(ui,generation) { s -> CourseStudy.update(s,lesson.id,change={p->p.copy(revealedResults=(p.revealedResults+example.id).distinct())}) }},enabled=shown>=example.steps.size,modifier=Modifier.fillMaxWidth().testTag("course-result-${example.id}")){Text(if(example.results.isEmpty())"예제 확인 완료"else"결과 표 확인")}
        if(revealed){
            Row(verticalAlignment=Alignment.CenterVertically,horizontalArrangement=Arrangement.spacedBy(8.dp)){
                Icon(Icons.Outlined.CheckCircle,null,tint=MaterialTheme.colorScheme.primary)
                Text("예제 확인함",style=MaterialTheme.typography.titleMedium)
            }
            example.results.forEach { StudyTable(it) }
        }
        Text(example.verification,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable private fun CourseCheckCard(ui:StudyUi,lesson:CourseLesson,check:CourseCheck,number:Int,progress:CourseProgress,generation:Long,guide:GuideCheck?=null){
    val saved=progress.checks.find { it.checkId==check.id }?:CourseCheckProgress(check.id)
    var draft by rememberSaveable(check.id) { mutableStateOf(saved.draft) }
    fun update(change:(CourseCheckProgress)->CourseCheckProgress){
        changeCourse(ui,generation) { s -> CourseStudy.update(s,lesson.id,change={p->
            val current=p.checks.find { it.checkId==check.id }?:CourseCheckProgress(check.id)
            p.copy(checks=p.checks.filterNot { it.checkId==check.id }+change(current))
        }) }
    }
    StudyPaper(modifier=Modifier.testTag("course-check-${check.id}")){
        Eyebrow("자기 점검 $number")
        SelectionContainer{Text(check.question,style=MaterialTheme.typography.bodyLarge)}
        OutlinedTextField(draft,{value->
            if(value.length<=10000){draft=value;update { it.copy(draft=value,rating="") }}
        },label={Text("내 말로 설명하기")},placeholder={Text("답을 떠올려 적어 보세요")},modifier=Modifier.fillMaxWidth().testTag("course-draft-${check.id}"),minLines=3,maxLines=8)
        Text("입력한 내용은 자동 저장돼요.",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
        if(!saved.revealed) OutlinedButton(onClick={update { it.copy(revealed=true) }},modifier=Modifier.fillMaxWidth().testTag("course-reveal-${check.id}")){Text("예시 답안 확인")}
        GuideCheckExplanation(guide,saved.revealed)
        if(saved.revealed){
            StudySection("예시 답안"){CourseText(check.answer,lesson.concepts.map{it.term})}
            if(check.explanation.isNotBlank()){
                StudySection("이유"){CourseText(check.explanation,lesson.concepts.map{it.term})}
            }
            Text("스스로 확인해 주세요",style=MaterialTheme.typography.labelLarge)
            FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){
                FilterChip(selected=saved.rating=="understood",onClick={update { it.copy(rating="understood") }},label={Text("이해했어요")},modifier=Modifier.heightIn(min=48.dp).testTag("course-rating-understood-${check.id}"))
                FilterChip(selected=saved.rating=="review",onClick={update { it.copy(rating="review") }},label={Text("다시 볼게요")},modifier=Modifier.heightIn(min=48.dp).testTag("course-rating-review-${check.id}"))
            }
            if(saved.rating=="review") Text("전체 목차의 ‘다시 볼 점검’에서 이 강의를 찾을 수 있어요.",style=MaterialTheme.typography.bodySmall)
            TextButton(onClick={update { it.copy(revealed=false) }}){Text("답안 가리고 다시 생각하기")}
        }
    }
}

@Composable private fun CourseConnections(ui:StudyUi,lesson:CourseLesson){
    val notes=remember(ui.pack,lesson){lesson.relatedNoteIds.distinct().mapNotNull { id -> ui.pack.notes.find { it.id==id } }}
    if(notes.isEmpty())return
    var walkthroughs by remember(lesson.id){mutableStateOf<List<LearningWalkRef>>(emptyList())}
    LaunchedEffect(lesson.id,notes){
        walkthroughs=runCatching{
            buildList { for(note in notes)addAll(ui.vm.walkthroughs.learningFor(note.id)) }.distinctBy{it.id}
        }.getOrDefault(emptyList())
    }
    val candidates=remember(ui.pack,notes){
        val objectives=notes.map { it.objectiveId }.toSet()
        ui.pack.practice().filter { q -> q.objectiveIds.any { it in objectives } }
    }
    val questions=remember(candidates,ui.state.issues){
        val excluded=ui.state.issues.filter { it.exclude }.map { it.contentId }.toSet()
        candidates.filter { it.id !in excluded }
    }
    Paper {
        Text("개념과 문제로 이어가기",style=MaterialTheme.typography.titleMedium)
        notes.forEach { note -> OutlinedButton(onClick={ui.note(note.id)},modifier=Modifier.fillMaxWidth()){Text("개념 노트 · ${note.title}")} }
        if(walkthroughs.isNotEmpty()){
            HorizontalDivider()
            Text("작은 표부터 SQL 따라 읽기",style=MaterialTheme.typography.titleSmall)
            walkthroughs.forEach{walk->OutlinedButton(onClick={ui.nav("walk:${walk.id}")},modifier=Modifier.fillMaxWidth()){Text(walk.title)}}
        }
        if(questions.isNotEmpty()) Button(onClick={ui.practice(questions,"${lesson.title} · 연결 연습")},modifier=Modifier.fillMaxWidth().testTag("course-practice")){Text("연결 연습문제 ${questions.size}개")}
    }
}

@Composable private fun CourseText(text:String,emphasis:List<String> = emptyList(),inlineCodes:List<String> = emptyList()){
    StudyBodyText(text,emphasis=emphasis,inlineCodes=inlineCodes)
}

@Composable private fun CourseDiagram(svg:String){
    var open by rememberSaveable(svg) { mutableStateOf(false) }
    OutlinedButton(onClick={open=true},modifier=Modifier.fillMaxWidth()){Icon(Icons.Outlined.Schema,null);Spacer(Modifier.width(8.dp));Text("개념도 크게 보기")}
    if(open) Dialog(onDismissRequest={open=false},properties=DialogProperties(usePlatformDefaultWidth=false)){
        Surface(Modifier.fillMaxSize(),color=MaterialTheme.colorScheme.background){
            Column(Modifier.fillMaxSize().safeDrawingPadding().padding(16.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
                TextButton(onClick={open=false}){Text("개념도 닫기")}
                Text("전체 개념도예요. 두 손가락으로 확대해서 볼 수 있어요.",style=MaterialTheme.typography.bodySmall)
                CourseDiagramView(svg,Modifier.fillMaxWidth().weight(1f))
            }
        }
    }
}

/** Displays only the validated bundled SVG. Every resource request and navigation is blocked. */
@SuppressLint("SetJavaScriptEnabled")
@Composable private fun CourseDiagramView(svg:String,modifier:Modifier){
    val html=remember(svg){"""<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'"><style>html,body{margin:0;width:100%;background:#f0f6f8}svg{display:block;width:100%;height:auto}</style></head><body>$svg</body></html>"""}
    AndroidView(modifier=modifier.clipToBounds(),factory={context->WebView(context).apply {
        settings.javaScriptEnabled=false
        settings.domStorageEnabled=false
        settings.allowFileAccess=false
        settings.allowContentAccess=false
        settings.blockNetworkLoads=true
        settings.mixedContentMode=android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW
        settings.useWideViewPort=true
        settings.loadWithOverviewMode=true
        settings.setSupportZoom(true)
        settings.builtInZoomControls=true
        settings.displayZoomControls=false
        webViewClient=object:WebViewClient(){
            override fun shouldOverrideUrlLoading(view:WebView?,request:WebResourceRequest?)=true
            override fun shouldInterceptRequest(view:WebView?,request:WebResourceRequest?):WebResourceResponse = WebResourceResponse("text/plain","UTF-8",ByteArrayInputStream(ByteArray(0)))
        }
        loadDataWithBaseURL(null,html,"text/html","UTF-8",null)
    }},onRelease={it.stopLoading();it.destroy()})
}
