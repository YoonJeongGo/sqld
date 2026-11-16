package kr.sqld.study

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.saveable.rememberSaveableStateHolder
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties

internal data class LoadedLessonGuide(val material:LessonGuide?=null,val finished:Boolean=false)
@Composable internal fun rememberLessonGuide(ui:StudyUi,lesson:CourseLesson):LoadedLessonGuide {
    val loaded by produceState(LoadedLessonGuide(),lesson){
        value=LoadedLessonGuide(runCatching{ui.vm.lessonGuides.lesson(lesson)}.getOrNull(),true)
    }
    return loaded
}

@Composable internal fun LessonGuideEntry(ui:StudyUi,lesson:CourseLesson,loaded:LoadedLessonGuide){
    var open by rememberSaveable(lesson.id){mutableStateOf(false)}
    val guide=loaded.material
    if(guide!=null)StudyPaper(accent=true){
        Eyebrow("원본에 연결한 추가 해설")
        GuideText(guide.purpose,guide.terms.map{it.token})
        Button(onClick={open=true},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("lesson-guide-open")){
            Icon(Icons.Outlined.MenuBook,null);Spacer(Modifier.width(8.dp));Text("대상·값·방향부터 따라 읽기")
        }
    }else if(loaded.finished)Text("추가 해설이 현재 원본과 맞지 않거나 열리지 않아요. 기존 강의와 해설은 그대로 볼 수 있어요.",style=MaterialTheme.typography.bodySmall)
    if(open&&guide!=null)LessonGuideDialog(ui,lesson,guide){open=false}
}

@Composable internal fun GuideExampleLink(ui:StudyUi,lesson:CourseLesson,guide:LessonGuide?,example:CourseExample){
    if(guide==null)return
    var open by rememberSaveable(example.id){mutableStateOf(false)}
    OutlinedButton(onClick={open=true},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("example-guide-${example.id}")){
        Text("추가 해설 보기 · 코드와 표 함께 읽기")
    }
    if(open)LessonGuideDialog(ui,lesson,guide,example.id){open=false}
}

/** Visible only inside the existing post-submission explanation; these are separate teaching examples. */
@Composable internal fun QuestionGuideLinks(ui:StudyUi,q:Question){
    val lessons=remember(q.explanation.relatedNoteId,ui.course){ui.course.lessons.filter{q.explanation.relatedNoteId in it.relatedNoteIds}}
    var expanded by rememberSaveable(q.id){mutableStateOf(false)}
    var selected by rememberSaveable(q.id){mutableStateOf<String?>(null)}
    if(lessons.isNotEmpty()){
        TextButton(onClick={expanded=!expanded},modifier=Modifier.fillMaxWidth().testTag("question-guide-links")){
            Text("대상·용어부터 다시 배우기",Modifier.weight(1f));Icon(if(expanded)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,null)
        }
        if(expanded){
            Text("아래는 이 문제의 답안과 별개인 강의 예제예요. 각 예제의 표와 값을 새로 확인하세요.",style=MaterialTheme.typography.bodySmall)
            lessons.forEach{lesson->OutlinedButton(onClick={selected=lesson.id},modifier=Modifier.fillMaxWidth()){Text(lesson.title)}}
        }
    }
    selected?.let{id->ui.course.lessons.find{it.id==id}?.let{lesson->
        val loaded=rememberLessonGuide(ui,lesson)
        loaded.material?.let{LessonGuideDialog(ui,lesson,it){selected=null}}
        if(loaded.finished&&loaded.material==null)AlertDialog(onDismissRequest={selected=null},title={Text("추가 해설을 열 수 없어요")},text={Text("현재 강의 원본과 일치하는 해설을 찾지 못했어요. 기존 해설은 그대로 사용할 수 있어요.")},confirmButton={TextButton(onClick={selected=null}){Text("기존 해설로")}})
    }}
}

@Composable internal fun GuideCheckExplanation(guide:GuideCheck?,revealed:Boolean){
    if(guide==null)return
    var hint by rememberSaveable(guide.checkId){mutableStateOf(false)}
    if(!revealed){
        TextButton(onClick={hint=!hint},modifier=Modifier.testTag("guide-hint-${guide.checkId}")){Text(if(hint)"읽기 출발점 접기"else"어디부터 생각할까?")}
        if(hint)StudyBodyText(guide.hint)
    }else{
        StudySection("대상과 값으로 다시 확인"){
            StudyBodyText(guide.reasoning,modifier=Modifier.testTag("guide-check-answer-${guide.checkId}"))
        }
    }
}

@Composable internal fun LessonGuideDialog(ui:StudyUi,lesson:CourseLesson,guide:LessonGuide,initialExample:String?=null,onClose:()->Unit){
    var mode by rememberSaveable(lesson.id,initialExample){mutableStateOf(if(initialExample==null)"prepare"else"read")}
    val examples=remember(guide){lesson.examples.zip(guide.examples)+guide.supplementalExamples.map{it.example to it.guide}}
    var selected by rememberSaveable(lesson.id,initialExample){mutableStateOf(initialExample?:examples.firstOrNull()?.first?.id.orEmpty())}
    var picker by rememberSaveable(lesson.id){mutableStateOf(false)}
    val readerStates=rememberSaveableStateHolder()
    val terms=remember(guide){guide.terms.map{it.token}}
    Dialog(onDismissRequest=onClose,properties=DialogProperties(usePlatformDefaultWidth=false)){
        Surface(Modifier.fillMaxSize(),color=MaterialTheme.colorScheme.background){
            Column(Modifier.fillMaxSize().safeDrawingPadding().testTag("lesson-guide-dialog")){
                Row(Modifier.fillMaxWidth().padding(horizontal=12.dp),verticalAlignment=Alignment.CenterVertically){
                    Column(Modifier.weight(1f)){
                        Text(lesson.title,style=MaterialTheme.typography.titleMedium)
                        Text("추가 해설 · 표와 코드의 대상·값·방향",style=MaterialTheme.typography.labelSmall)
                    }
                    IconButton(onClick=onClose,modifier=Modifier.testTag("guide-close")){Icon(Icons.Outlined.Close,"추가 해설 닫기")}
                }
                Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(horizontal=8.dp),horizontalArrangement=Arrangement.spacedBy(6.dp)){
                    listOf("prepare" to "읽기 준비","read" to "예제 따라 읽기","words" to "용어·질문","sources" to "원본·주의").forEach{(id,label)->
                        FilterChip(selected=mode==id,onClick={mode=id},label={Text(label)},modifier=Modifier.heightIn(min=48.dp).testTag("guide-tab-$id"))
                    }
                }
                if(mode=="read"){
                    val chosen=examples.find{it.first.id==selected}?:examples.firstOrNull()
                    TextButton(onClick={picker=true},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("guide-example-picker")){
                        Text((if(chosen?.first?.id in lesson.examples.map{it.id})"원본 예제 · "else"가상 보충 예제 · ")+chosen?.first?.title.orEmpty().removePrefix("가상 보충: "),Modifier.weight(1f))
                        Icon(Icons.Outlined.UnfoldMore,null)
                    }
                    if(chosen!=null)readerStates.SaveableStateProvider(chosen.first.id){GuideReading(ui,lesson,guide,chosen.first,chosen.second,Modifier.weight(1f))}
                }else key(mode){
                    Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()).padding(16.dp).testTag("guide-details"),verticalArrangement=Arrangement.spacedBy(16.dp)){
                        when(mode){
                            "prepare"->{
                                StudySection("왜 배우는가"){GuideText(guide.purpose,terms)}
                                StudySection("전체 뜻과 바뀌는 것"){GuideText(guide.overview,terms)}
                                Button(onClick={mode="read"},modifier=Modifier.fillMaxWidth()){Text("전체 코드와 표부터 보기")}
                                val visuals=ui.courseVisuals.forLesson(lesson.id)
                                if(visuals.isNotEmpty()){
                                    StudySection("그림으로 먼저 확인"){
                                        StudyBodyText("그림은 별도 데이터의 예시예요. 그림의 이름·값을 예제 정답에 섞지 마세요.",emphasis=listOf("별도 데이터"))
                                    }
                                    visuals.forEach{CourseVisualCard(ui.courseVisuals,it)}
                                }
                            }
                            "words"->{
                                Text("단어의 뜻과 지금 하는 일",style=MaterialTheme.typography.titleLarge)
                                guide.terms.forEach{term->StudyPaper{
                                    StudySection(term.token+" · "+term.kind){
                                        GuideText(term.meaning,listOf(term.token))
                                        GuideText(term.role,listOf(term.token))
                                    }
                                }}
                                Text("자주 막히는 질문",style=MaterialTheme.typography.titleLarge)
                                guide.questions.forEachIndexed{index,question->key(index){
                                    var open by rememberSaveable(lesson.id,index){mutableStateOf(false)}
                                    OutlinedButton(onClick={open=!open},modifier=Modifier.fillMaxWidth()){Text(question.question,Modifier.weight(1f));Icon(if(open)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,null)}
                                    if(open)GuideText(question.answer,terms)
                                }}
                            }
                            "sources"->{
                                StudySection("원본 교재에서 찾기"){
                                    StudyBodyText("아래는 제공한 흥달쌤 원본 PDF의 파일 쪽수예요. 앱의 창작 63강 예제와 원본 교재의 예제를 같은 문제로 취급하지 않아요.")
                                }
                                guide.pdfRefs.forEach{ref->StudyPaper{
                                    StudySection("${ref.sectionId} ${ref.title} · ${ref.fromPage}~${ref.toPage}쪽"){GuideText(ref.note)}
                                }}
                                StudySection("헷갈리는 조건"){guide.pitfalls.forEach{StudyWarning(it)}}
                                if(guide.reviewNotes.isNotEmpty())StudySection("원문 검토·별도 주의"){guide.reviewNotes.forEach{StudyWarning(it)}}
                                StudySection("검증 근거"){
                                    guide.sourceUrls.forEach{SelectionContainer{Text(it,style=MaterialTheme.typography.bodyMedium)}}
                                }
                            }
                        }
                    }
                }
            }
        }
        if(picker)AlertDialog(onDismissRequest={picker=false},title={Text("예제 선택")},text={Column(Modifier.verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(8.dp)){
            examples.forEach{(example,_)->OutlinedButton(onClick={selected=example.id;picker=false},modifier=Modifier.fillMaxWidth().testTag("guide-pick-${example.id}")){
                Text((if(example.id in lesson.examples.map{it.id})"원본 · "else"가상 보충 · ")+example.title)
            }}
        }},confirmButton={TextButton(onClick={picker=false}){Text("돌아가기")}})
    }
}

@Composable private fun GuideText(text:String,emphasis:List<String> = emptyList()){
    StudyBodyText(text,emphasis=emphasis)
}

@Composable private fun GuideReading(ui:StudyUi,lesson:CourseLesson,guide:LessonGuide,example:CourseExample,detail:ExampleGuide,modifier:Modifier){
    val walk=remember(guide,example){guide.walkthrough(example,detail)}
    val progressKey=LessonGuideRules.stepKey(example.id)
    val generation=remember{ui.vm.repository.restoreGeneration}
    var step by rememberSaveable(lesson.id,example.id){mutableIntStateOf(CourseStudy.progress(ui.state,lesson.id).exampleSteps[progressKey]?:0)}
    var foundations by rememberSaveable(lesson.id,example.id){mutableStateOf(false)}
    val chosen=step.coerceIn(walk.steps.indices)
    fun change(value:Int){
        step=value
        ui.vm.mutate{state->if(ui.vm.repository.restoreGeneration!=generation)state else CourseStudy.update(state,lesson.id,{it.copy(exampleSteps=it.exampleSteps+(progressKey to value))})}
    }
    val narrative:@Composable (Modifier)->Unit={m->WalkNarrative(walk,chosen,::change,foundations,{foundations=it},m)}
    if(example.sql.isNotBlank())SqlReadingLayout(ui,walk.source,WalkthroughRules.ranges(example.sql,walk.steps[chosen].codeFocus),modifier.fillMaxWidth(),narrative)
    else BoxWithConstraints(modifier.fillMaxWidth()){
        if(maxWidth>=840.dp&&example.tables.isNotEmpty())Row(Modifier.fillMaxSize()){
            narrative(Modifier.weight(1f).fillMaxHeight());VerticalDivider()
            Column(Modifier.weight(1f).fillMaxHeight().verticalScroll(rememberScrollState()).padding(16.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
                StudySection("원본 예제 · 개념과 표"){
                    SelectionContainer{Text(example.question,style=MaterialTheme.typography.bodyLarge)}
                    example.tables.forEach{ReadingTable(it)}
                }
            }
        }else WalkNarrative(walk,chosen,::change,foundations,{foundations=it},Modifier.fillMaxSize()){
            var original by rememberSaveable(example.id){mutableStateOf(false)}
            TextButton(onClick={original=!original},modifier=Modifier.fillMaxWidth().testTag("guide-concept-original")){
                Text(if(original)"원본 개념·표 접기"else"원본 개념·표 함께 보기")
            }
            if(original){SelectionContainer{Text(example.question,style=MaterialTheme.typography.bodyLarge)};example.tables.forEach{ReadingTable(it)}}
        }
    }
}
