package kr.sqld.study

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowForward
import androidx.compose.material.icons.outlined.ChevronLeft
import androidx.compose.material.icons.outlined.ChevronRight
import androidx.compose.material.icons.outlined.ExpandLess
import androidx.compose.material.icons.outlined.ExpandMore
import androidx.compose.material.icons.outlined.Storage
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.style.LineBreak
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.dp
import java.time.LocalDate

private fun planDateLabel(value:String):String {
    val date=LocalDate.parse(value)
    val weekday=listOf("월","화","수","목","금","토","일")[date.dayOfWeek.value-1]
    return "${date.monthValue}/${date.dayOfMonth} ($weekday)"
}

/** Keep topic separators inside a line instead of leaving a middle dot at its start. */
@Composable private fun PlanTopicHeading(title:String,compact:Boolean=false){
    val measurer=rememberTextMeasurer()
    val density=LocalDensity.current
    BoxWithConstraints(Modifier.fillMaxWidth()){
        val style=if(compact&&maxWidth<360.dp)MaterialTheme.typography.titleMedium else MaterialTheme.typography.titleLarge
        val width=with(density){maxWidth.roundToPx()}
        val lines=mutableListOf<String>()
        title.split('·').map(String::trim).filter(String::isNotEmpty).forEach{topic->
            val candidate=lines.lastOrNull()?.let{"$it · $topic"}?:topic
            if(lines.isNotEmpty()&&measurer.measure(candidate,style,softWrap=false).size.width<=width)lines[lines.lastIndex]=candidate
            else lines.add(topic)
        }
        Text(lines.joinToString("\n"),style=style.copy(lineBreak=LineBreak.Heading))
    }
}

@Composable fun PlanHomeCard(ui:StudyUi,today:LocalDate=LocalDate.now()) {
    val plan=ui.studyPlan
    val day=plan?.days?.firstOrNull{it.date==today.toString()}
    val next=plan?.nextStudyDay(today.toString())
    val colors=MaterialTheme.colorScheme
    val largeText=LocalDensity.current.fontScale*ui.state.settings.textScale>=1.35f
    Surface(Modifier.fillMaxWidth(),shape=RoundedCornerShape(20.dp),color=colors.tertiaryContainer,contentColor=colors.onTertiaryContainer) {
        BoxWithConstraints(Modifier.padding(20.dp)) {
            val showIllustration=maxWidth>=420.dp&&!largeText
            Row(horizontalArrangement=Arrangement.spacedBy(18.dp),verticalAlignment=Alignment.Top) {
                if(showIllustration)Surface(color=colors.primaryContainer,contentColor=colors.onPrimaryContainer,shape=CircleShape) {
                    Icon(Icons.Outlined.Storage,contentDescription=null,modifier=Modifier.padding(18.dp).size(34.dp))
                }
                Column(Modifier.weight(1f),verticalArrangement=Arrangement.spacedBy(12.dp)) {
                    Text("${today.year}년 ${planDateLabel(today.toString())}",style=MaterialTheme.typography.labelLarge,color=colors.onTertiaryContainer)
                    Text(when {
                        day!=null&&!day.isRest->"오늘 배울 내용 · 공부 ${day.studyDay}일차"
                        day?.isRest==true->"오늘은 휴식일"
                        next!=null->"다음 공부 · ${planDateLabel(next.date)}"
                        plan!=null->"학습 계획 돌아보기"
                        else->"오늘의 공부를 한눈에"
                    },style=MaterialTheme.typography.bodySmall,color=colors.onTertiaryContainer)
                    PlanTopicHeading(when {
                        day!=null&&!day.isRest->day.title
                        day?.isRest==true->"쉬어 가며 다음 공부를 준비해요"
                        next!=null->next.title
                        else->"강의와 PDF, 복습을 한 흐름으로"
                    },compact=true)
                    if(day!=null&&!day.isRest) {
                        Text("영상 ${day.lectures.size}강 · ${planDuration(day.lectures.sumOf{it.minutes})} · PDF ${day.pdfs.size}권",style=MaterialTheme.typography.bodySmall,color=colors.onTertiaryContainer)
                        val lessons=PlanReview.lessons(day,ui.course)
                        if(lessons.isNotEmpty()) {
                            val read=lessons.count{lesson->(ui.state.courseProgress.find{it.lessonId==lesson.id}?.readVersion?:0)>=lesson.version}
                            Text("앱 노트 읽음 $read / ${lessons.size}강",style=MaterialTheme.typography.bodySmall,color=colors.onTertiaryContainer)
                        }
                    } else if(next!=null)Text("다음 공부일 ${planDateLabel(next.date)}",style=MaterialTheme.typography.bodySmall,color=colors.onTertiaryContainer)
                    else if(plan!=null)Text("${planDateLabel(plan.startDate)} ~ ${planDateLabel(plan.endDate)} · 공부 ${plan.studyDays.size}일",style=MaterialTheme.typography.bodySmall,color=colors.onTertiaryContainer)
                    Button(onClick={ui.nav("plan")},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("home-study-plan"),colors=ButtonDefaults.buttonColors(containerColor=colors.primary,contentColor=colors.onPrimary)) {
                        Text("학습 계획 보기",Modifier.weight(1f))
                        Icon(Icons.Outlined.ArrowForward,contentDescription=null)
                    }
                }
            }
        }
    }
}

@Composable fun StudyPlanScreen(ui:StudyUi) {
    val plan=ui.studyPlan
    if(plan==null) {
        Column(Modifier.fillMaxSize().padding(20.dp)) {
            EmptyState("학습 계획을 불러오지 못했어요","기존 강의 노트와 학습 기록은 계속 사용할 수 있어요.","강의 노트 보기",{ui.nav("course")})
        }
        return
    }
    StudyPlanContent(plan,ui.course,ui.pack,ui.state,
        onLesson={ui.nav("lesson:$it")},onNote=ui.note,
        onPractice={questions,title->ui.practice(questions,title)})
}

@Composable internal fun StudyPlanContent(
    plan:StudyPlan,course:CoursePack,pack:ContentPack,state:StudyState,
    onLesson:(String)->Unit,onNote:(String)->Unit,onPractice:(List<Question>,String)->Unit,
    today:LocalDate=LocalDate.now()
) {
    var date by rememberSaveable(plan.startDate,plan.endDate){mutableStateOf(plan.initialDate(today))}
    var extended by rememberSaveable{mutableStateOf(false)}
    var chooseDate by rememberSaveable{mutableStateOf(false)}
    var showOverview by rememberSaveable{mutableStateOf(false)}
    var showNotes by rememberSaveable(date){mutableStateOf(false)}
    var showBlockDetails by rememberSaveable(date){mutableStateOf(false)}
    var showLectures by rememberSaveable(date){mutableStateOf(false)}
    var showPdfs by rememberSaveable(date){mutableStateOf(false)}
    val day=plan.days.firstOrNull{it.date==date}?:plan.days.first()
    val index=plan.days.indexOf(day)
    val lessons=PlanReview.lessons(day,course)
    val notes=PlanReview.notes(day,course,pack)
    val questions=PlanReview.questions(day,course,pack,state)
    val largeText=LocalDensity.current.fontScale*state.settings.textScale>=1.35f
    BoxWithConstraints(Modifier.fillMaxSize()) {
        val wide=maxWidth>=840.dp&&!largeText
        LazyColumn(Modifier.fillMaxSize().testTag("study-plan-list"),contentPadding=PaddingValues(if(wide)24.dp else 16.dp),verticalArrangement=Arrangement.spacedBy(16.dp)) {
            item {
                Column(verticalArrangement=Arrangement.spacedBy(4.dp)) {
                    Text("학습 계획",style=MaterialTheme.typography.titleLarge)
                    Text("공부 ${plan.studyDays.size}일 · 휴식 ${plan.days.count{it.isRest}}일",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
                    TextButton(onClick={showOverview=!showOverview},modifier=Modifier.testTag("plan-overview-toggle").semantics{stateDescription=if(showOverview)"펼쳐짐"else"접힘"}) {
                        Text(if(showOverview)"전체 학습량 접기"else"전체 학습량과 이용 안내",Modifier.weight(1f,fill=false))
                        Icon(if(showOverview)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,contentDescription=null)
                    }
                    if(showOverview)Paper {
                        Text(plan.title,style=MaterialTheme.typography.titleMedium)
                        Text("영상 강의 ${plan.lectures.size}강 · ${planDuration(plan.videoMinutes)}",style=MaterialTheme.typography.bodyMedium)
                        Text(plan.lectures.groupBy{it.kind}.entries.joinToString(" · "){(kind,lectures)->"$kind ${lectures.size}강"})
                        Text("5시간 기본: ${planDuration(plan.baseMinutes)}\n6시간 확장: ${planDuration(plan.baseMinutes+plan.extraMinutes)}")
                        Text("영상 시간은 하루 학습 시간에 포함돼요. PDF 풀이·오답 정리·앱 복습 시간과 구분해 배치했어요.",style=MaterialTheme.typography.bodySmall)
                        plan.notes.forEach{Text(it,style=MaterialTheme.typography.bodySmall)}
                    }
                }
            }
            item {
                PlanDateControls(day,index,plan,today,extended,
                    onDate={date=it},onChooseDate={chooseDate=true},onExtended={extended=it})
            }
            item {
                Column(verticalArrangement=Arrangement.spacedBy(8.dp)) {
                    if(day.phase.isNotBlank())Eyebrow(day.phase)
                    PlanTopicHeading(day.title)
                    Text("이 화면은 일정표예요. 강의 시청·PDF 풀이 완료를 자동으로 기록하지 않아요.",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
            if(day.isRest) {
                item { Paper {
                    Text("휴식일",style=MaterialTheme.typography.titleLarge,modifier=Modifier.testTag("plan-rest-day"))
                    Text(day.restReason)
                    Text("오늘 배정된 학습은 없어요.")
                    plan.nextStudyDay(day.date)?.let{next->OutlinedButton(onClick={date=next.date},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp)){Text("다음 공부일 ${planDateLabel(next.date)} 보기")}}
                } }
            } else {
                if(wide)item {
                    Row(Modifier.fillMaxWidth().testTag("plan-wide-columns"),horizontalArrangement=Arrangement.spacedBy(20.dp),verticalAlignment=Alignment.Top) {
                        Column(Modifier.weight(1f)) {
                            PlanTimeline(day,extended,showBlockDetails){showBlockDetails=!showBlockDetails}
                        }
                        Column(Modifier.weight(1f),verticalArrangement=Arrangement.spacedBy(16.dp)) {
                            PlanPracticeCard(day,questions,onPractice)
                            PlanResources(day,lessons,notes,state,showLectures,showPdfs,showNotes,
                                {showLectures=!showLectures},{showPdfs=!showPdfs},{showNotes=!showNotes},onLesson,onNote)
                        }
                    }
                } else {
                    item { PlanPracticeCard(day,questions,onPractice) }
                    item { PlanTimeline(day,extended,showBlockDetails){showBlockDetails=!showBlockDetails} }
                    item {
                        PlanResources(day,lessons,notes,state,showLectures,showPdfs,showNotes,
                            {showLectures=!showLectures},{showPdfs=!showPdfs},{showNotes=!showNotes},onLesson,onNote)
                    }
                }
            }
        }
    }
    if(chooseDate)AlertDialog(onDismissRequest={chooseDate=false},title={Text("날짜 선택")},text={
        LazyColumn(Modifier.fillMaxWidth().heightIn(max=420.dp).testTag("plan-date-list")) {
            items(plan.days,key={it.date}){candidate->
                ListItem(
                    headlineContent={Text("${planDateLabel(candidate.date)} · ${candidate.studyDay?.let{"${it}일차"}?:"휴식"}")},
                    supportingContent={Text(if(candidate.isRest)candidate.restReason else candidate.title)},
                    modifier=Modifier.fillMaxWidth().heightIn(min=56.dp).semantics{selected=candidate.date==date}.testTag("plan-date-${candidate.date}").clickable(role=Role.Button){date=candidate.date;chooseDate=false})
            }
        }
    },confirmButton={TextButton(onClick={chooseDate=false}){Text("닫기")}})
}

@OptIn(ExperimentalLayoutApi::class)
@Composable private fun PlanDateControls(
    day:PlanDay,index:Int,plan:StudyPlan,today:LocalDate,extended:Boolean,
    onDate:(String)->Unit,onChooseDate:()->Unit,onExtended:(Boolean)->Unit
) {
    Column(verticalArrangement=Arrangement.spacedBy(8.dp)) {
        BoxWithConstraints(Modifier.fillMaxWidth()){
        val dateLabel=planDateLabel(day.date)
        val studyLabel=day.studyDay?.let{"${it}일차"}?:"휴식일"
        val splitDate=!actionRowFits(maxWidth-112.dp,listOf("$dateLabel · $studyLabel"),padding=12.dp)
        Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(8.dp),verticalAlignment=Alignment.CenterVertically) {
            IconButton(enabled=index>0,onClick={onDate(plan.days[index-1].date)},modifier=Modifier.testTag("plan-previous-day")) {
                Icon(Icons.Outlined.ChevronLeft,contentDescription="이전 날짜")
            }
            OutlinedButton(onClick=onChooseDate,modifier=Modifier.weight(1f).heightIn(min=48.dp).testTag("plan-date-picker"),contentPadding=PaddingValues(horizontal=12.dp,vertical=8.dp)) {
                if(splitDate)Column(horizontalAlignment=Alignment.CenterHorizontally,verticalArrangement=Arrangement.spacedBy(4.dp)){
                    Text(dateLabel)
                    Text(studyLabel,style=MaterialTheme.typography.labelMedium)
                }else Text("$dateLabel · $studyLabel")
            }
            IconButton(enabled=index<plan.days.lastIndex,onClick={onDate(plan.days[index+1].date)},modifier=Modifier.testTag("plan-next-day")) {
                Icon(Icons.Outlined.ChevronRight,contentDescription="다음 날짜")
            }
        }}
        FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(8.dp),modifier=Modifier.fillMaxWidth()) {
            if(plan.days.any{it.date==today.toString()})TextButton(onClick={onDate(today.toString())},modifier=Modifier.heightIn(min=48.dp).testTag("plan-today")){Text("오늘")}
            FilterChip(selected=!extended,onClick={onExtended(false)},label={Text("5시간 기본")},modifier=Modifier.heightIn(min=48.dp),colors=FilterChipDefaults.filterChipColors(selectedContainerColor=MaterialTheme.colorScheme.primaryContainer,selectedLabelColor=MaterialTheme.colorScheme.onPrimaryContainer))
            FilterChip(selected=extended,onClick={onExtended(true)},label={Text("6시간 확장")},modifier=Modifier.heightIn(min=48.dp),colors=FilterChipDefaults.filterChipColors(selectedContainerColor=MaterialTheme.colorScheme.primaryContainer,selectedLabelColor=MaterialTheme.colorScheme.onPrimaryContainer))
        }
    }
}

@Composable private fun PlanPracticeCard(day:PlanDay,questions:List<Question>,onPractice:(List<Question>,String)->Unit) {
    Paper {
        Text("앱으로 다시 확인하기",style=MaterialTheme.typography.titleMedium)
        Text("이날 범위의 개념을 떠올리고, 표의 결과를 직접 계산해 보세요.",style=MaterialTheme.typography.bodyMedium)
        Text("연결된 일반 연습 ${questions.size}문항 · 모의고사 문제 제외",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
        Text("이 범위에서 덜 본 문제부터 골라요. 시작한 문제는 미응답이어도 본 문제로 기록돼요.",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
        Button(enabled=questions.isNotEmpty(),onClick={onPractice(questions,"${planDateLabel(day.date)} 학습 계획 복습")},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("plan-practice")) {
            Text("이 범위 연습문제 풀기",Modifier.weight(1f))
            Icon(Icons.Outlined.ArrowForward,contentDescription=null)
        }
    }
}

@Composable private fun PlanTimeline(day:PlanDay,extended:Boolean,showDetails:Boolean,onDetails:()->Unit) {
    Paper {
        Text("${if(extended)"6시간"else"5시간"} 시간 배분",style=MaterialTheme.typography.titleMedium,modifier=Modifier.testTag("plan-time-budget"))
        TextButton(onClick=onDetails,modifier=Modifier.testTag("plan-block-details-toggle").semantics{stateDescription=if(showDetails)"펼쳐짐"else"접힘"},contentPadding=PaddingValues(horizontal=0.dp,vertical=4.dp)) {
            Text(if(showDetails)"활동 설명 접기"else"활동 설명 펼치기",Modifier.weight(1f,fill=false))
            Icon(if(showDetails)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,contentDescription=null)
        }
        Column(if(showDetails)Modifier.testTag("plan-block-details")else Modifier,verticalArrangement=Arrangement.spacedBy(12.dp)) {
            day.blocks.forEachIndexed{index,block->
                if(index>0)HorizontalDivider(color=MaterialTheme.colorScheme.outlineVariant)
                PlanTimelineRow(block,index+1,false,showDetails)
            }
            if(extended) {
                HorizontalDivider(color=MaterialTheme.colorScheme.outlineVariant)
                Text("추가 60분 · 같은 진도, 약점 보완",style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.primary)
                day.extension.forEachIndexed{index,block->PlanTimelineRow(block,day.blocks.size+index+1,true,showDetails)}
            }
        }
    }
}

@Composable private fun PlanTimelineRow(block:PlanBlock,number:Int,extra:Boolean,showDetails:Boolean) {
    val fontScale=LocalDensity.current.fontScale*MaterialTheme.typography.titleSmall.fontSize.value/16f
    BoxWithConstraints((if(extra)Modifier.testTag("plan-extension")else Modifier).fillMaxWidth()){
    if(maxWidth<320.dp||fontScale>=1.35f){
        Column(Modifier.fillMaxWidth().padding(vertical=4.dp),verticalArrangement=Arrangement.spacedBy(8.dp)){
            Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween){
                Text(number.toString().padStart(2,'0'),style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.primary)
                Text("${block.minutes}분",style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.primary)
            }
            Text(block.title,style=MaterialTheme.typography.titleSmall)
            if(showDetails)Text(block.detail,style=MaterialTheme.typography.bodyMedium,color=MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }else{
    Row(Modifier.fillMaxWidth().padding(vertical=4.dp),horizontalArrangement=Arrangement.spacedBy(12.dp),verticalAlignment=Alignment.Top) {
        Text(number.toString().padStart(2,'0'),Modifier.widthIn(min=28.dp),style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.primary)
        Column(Modifier.weight(1f),verticalArrangement=Arrangement.spacedBy(8.dp)) {
            Row(horizontalArrangement=Arrangement.spacedBy(12.dp),verticalAlignment=Alignment.Top) {
                Text(block.title,Modifier.weight(1f),style=MaterialTheme.typography.titleSmall)
                Text("${block.minutes}분",style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.primary)
            }
            if(showDetails)Text(block.detail,style=MaterialTheme.typography.bodyMedium,color=MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
    }}
}

@Composable private fun PlanResources(
    day:PlanDay,lessons:List<CourseLesson>,notes:List<Note>,state:StudyState,
    showLectures:Boolean,showPdfs:Boolean,showNotes:Boolean,
    onLectures:()->Unit,onPdfs:()->Unit,onNotes:()->Unit,
    onLesson:(String)->Unit,onNote:(String)->Unit
) {
    Column(Modifier.fillMaxWidth(),verticalArrangement=Arrangement.spacedBy(16.dp)) {
        if(day.lectures.isNotEmpty())PlanExpandableSection("시청할 강의","${day.lectures.size}강 · ${planDuration(day.lectures.sumOf{it.minutes})}",showLectures,onLectures,"plan-lectures-toggle") {
            Column(Modifier.testTag("plan-lecture-list"),verticalArrangement=Arrangement.spacedBy(12.dp)) {
                day.lectures.forEach{lecture->
                    HorizontalDivider(color=MaterialTheme.colorScheme.outlineVariant)
                    Column(verticalArrangement=Arrangement.spacedBy(4.dp)) {
                        Text("${lecture.kind} · 전체 ${lecture.number}강 · ${lecture.minutes}분",style=MaterialTheme.typography.labelMedium,color=MaterialTheme.colorScheme.primary)
                        Text(lecture.title,style=MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }
        if(day.pdfs.isNotEmpty())PlanExpandableSection("PDF 학습 범위","${day.pdfs.size}권 · 보유한 파일에서 확인",showPdfs,onPdfs,"plan-pdfs-toggle") {
            Column(Modifier.testTag("plan-pdf-list"),verticalArrangement=Arrangement.spacedBy(12.dp)) {
                day.pdfs.forEach{pdf->
                    HorizontalDivider(color=MaterialTheme.colorScheme.outlineVariant)
                    Column(verticalArrangement=Arrangement.spacedBy(6.dp)) {
                        Text("${pdf.sectionId} · ${pdf.fromPage}~${pdf.toPage}쪽",style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.primary)
                        Text(pdf.title,style=MaterialTheme.typography.titleSmall)
                        pdf.focus.forEach{Text("• $it",style=MaterialTheme.typography.bodyMedium)}
                    }
                }
            }
        }
        if(lessons.isNotEmpty()||notes.isNotEmpty())Paper {
            Text("앱 강의 노트 · ${lessons.size}강",style=MaterialTheme.typography.titleMedium)
            lessons.forEach{lesson->
                val read=(state.courseProgress.find{it.lessonId==lesson.id}?.readVersion?:0)>=lesson.version
                HorizontalDivider(color=MaterialTheme.colorScheme.outlineVariant)
                Row(Modifier.fillMaxWidth().heightIn(min=56.dp).testTag("plan-lesson-${lesson.id}").clickable(role=Role.Button,onClickLabel="강의 노트 열기"){onLesson(lesson.id)}.padding(vertical=8.dp),horizontalArrangement=Arrangement.spacedBy(12.dp),verticalAlignment=Alignment.CenterVertically) {
                    Column(Modifier.weight(1f),verticalArrangement=Arrangement.spacedBy(4.dp)) {
                        Text("${lesson.id} · ${lesson.title}",style=MaterialTheme.typography.bodyMedium)
                        Text(if(read)"앱 강의 노트 읽음"else"앱 강의 노트 읽기",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Icon(Icons.Outlined.ChevronRight,contentDescription=null,tint=MaterialTheme.colorScheme.primary)
                }
            }
            if(notes.isNotEmpty()) {
                TextButton(onClick=onNotes,modifier=Modifier.fillMaxWidth().testTag("plan-notes-toggle").semantics{stateDescription=if(showNotes)"펼쳐짐"else"접힘"}) {
                    Text(if(showNotes)"개념 노트 접기"else"연결된 개념 노트 ${notes.size}개",Modifier.weight(1f))
                    Icon(if(showNotes)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,contentDescription=null)
                }
                if(showNotes)notes.forEach{note->
                    OutlinedButton(onClick={onNote(note.id)},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("plan-note-${note.id}")){Text("${note.objectiveId} · ${note.title}",Modifier.fillMaxWidth())}
                }
            }
        }
    }
}

@Composable private fun PlanExpandableSection(
    title:String,summary:String,expanded:Boolean,onToggle:()->Unit,tag:String,
    content:@Composable ColumnScope.()->Unit
) {
    Paper {
        Row(Modifier.fillMaxWidth().heightIn(min=48.dp).testTag(tag).semantics{stateDescription=if(expanded)"펼쳐짐"else"접힘"}.clickable(role=Role.Button,onClickLabel=if(expanded)"$title 접기"else"$title 펼치기",onClick=onToggle),horizontalArrangement=Arrangement.spacedBy(12.dp),verticalAlignment=Alignment.CenterVertically) {
            Column(Modifier.weight(1f),verticalArrangement=Arrangement.spacedBy(4.dp)) {
                Text(title,style=MaterialTheme.typography.titleMedium)
                Text(summary,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
            }
            Icon(if(expanded)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,contentDescription=null,tint=MaterialTheme.colorScheme.primary)
        }
        if(expanded)content()
    }
}
