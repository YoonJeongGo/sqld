package kr.sqld.study

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import java.time.LocalDate

@Composable fun MockScreen(ui:StudyUi){
    var selected by remember{mutableStateOf<String?>(null)}
    val spec=ui.pack.examSpec
    LazyColumn(Modifier.fillMaxSize().testTag("full-mock-list"),contentPadding=PaddingValues(20.dp),verticalArrangement=Arrangement.spacedBy(24.dp)){
        item{PageTitle("","SQLD 전체 모의고사","일반 학습에서 공개하지 않은 독립 창작 세트입니다.")}
        item{OutlinedButton(onClick={ui.nav("mock")},modifier=Modifier.fillMaxWidth()){Text("단원 모의고사로 이동")}}
        item{Paper(accent=true){Text("${spec.modelCount+spec.sqlCount}문항 · ${spec.minutes}분",style=MaterialTheme.typography.headlineSmall);Text("1과목 ${spec.modelCount}문항 / 2과목 ${spec.sqlCount}문항\n문항당 ${spec.pointsPerQuestion}점 · 총점 ${spec.passPoints}점 이상\n각 과목 ${spec.subjectMinimumPercent}% 이상 필요");Text("현재 구성은 출판사 안내로 교차 확인했습니다. 시행기관 최신 원문은 접근 실패로 미확인입니다.",style=MaterialTheme.typography.bodySmall)}}
        items((1..5).toList()){number->val id="mock-$number";val questions=ui.pack.mock(id);val complete=questions.count{it.subjectId=="model"}==spec.modelCount&&questions.count{it.subjectId=="sql"}==spec.sqlCount;val attempts=ui.state.sessions.count{it.mockSetId==id}
            Paper{Text("창작 모의고사 $number",style=MaterialTheme.typography.titleLarge);Text(if(attempts>0)"응시 이력 ${attempts}회 · 다시 풀면 재응시로 기록"else"미응시 · 문제를 미리 공개하지 않았어요",style=MaterialTheme.typography.bodyMedium);Text(if(complete)"${questions.size}문항 수록 · 문서 검토 기반"else"수록 ${questions.size} / ${spec.modelCount+spec.sqlCount}문항 · 검수·구성 조건 미충족으로 시작 제한",style=MaterialTheme.typography.bodySmall);Button(enabled=complete,onClick={selected=id},modifier=Modifier.fillMaxWidth()){Text(if(attempts>0)"재응시 안내 보기"else"응시 안내 보기")}}
        }
        item{Text("공식 공개 기출을 확보하지 못했습니다. 실제 시험 회차·연도를 붙이지 않은 독자 창작 문제입니다.",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)}
    }
    selected?.let{id->val questions=ui.pack.mock(id);val active=ui.state.sessions.find{it.submittedAt==null&&it.mode=="strict"};AlertDialog(onDismissRequest={selected=null},title={Text("실전 모의고사 시작")},text={Column(Modifier.verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(12.dp)){Text("${spec.minutes}분 동안 ${questions.size}문항을 풉니다. 다른 앱으로 이동하거나 화면을 꺼도 시간은 흐릅니다.");Text("만료 시 미응답을 포함해 한 번만 자동 제출합니다. 중간 해설·노트 확인은 연습 전환 확인 후 가능하며, 최초 실전 지표에서 제외됩니다.");if(active!=null)Text("진행 중인 모의고사가 있어 먼저 이어서 진행합니다.")}},confirmButton={Button(onClick={if(active!=null)ui.nav("session:${active.id}")else ui.vm.start(questions,"strict","창작 모의고사 ${id.substringAfter('-')}",id){ui.nav("session:$it")};selected=null}){Text(if(active!=null)"진행 중 시험으로"else"시간을 시작하고 응시")}},dismissButton={TextButton(onClick={selected=null}){Text("돌아가기")}})}
}

@Composable fun HistoryScreen(ui:StudyUi){
    val records=ui.state.submissions
    val groups=listOf("새 문제 첫 제출" to records.filter{it.firstEver&&!it.helped},"반복 풀이" to records.filter{!it.firstEver&&!it.helped},"도움 사용" to records.filter{it.helped})
    LazyColumn(Modifier.fillMaxSize(),contentPadding=PaddingValues(20.dp),verticalArrangement=Arrangement.spacedBy(24.dp)){
        item{PageTitle("","학습 기록","최초 확정 제출을 보존합니다. 다시 맞혀도 과거 오답을 지우지 않아요.")}
        item{Paper{groups.forEach{(title,rows)->Text("${title} · 정답 ${rows.count{it.outcome=="correct"}} / ${rows.size}",style=MaterialTheme.typography.titleMedium)};Text(if(records.size<20)"판단 자료 부족"else"내부 문제 풀이 기록 · 실제 시험 합격률로 해석하지 마세요",style=MaterialTheme.typography.bodySmall)}}
        if(ui.state.sessions.isEmpty())item{EmptyState("아직 제출한 기록이 없어요","첫 노트를 읽고 개념 확인을 시작해 보세요.","학습 시작",{ui.nav("notes")})}
        items(ui.state.sessions.reversed(),key={it.id}){s->NoteRow(if(s.submittedAt==null)"진행"else"완료",s.title,"${dateText(s.startedAt)} · ${s.items.count{it.submissionId!=null}}/${s.items.size} 제출${if(s.repeat)" · 재응시"else""}",{ui.nav("session:${s.id}")})}
    }
}

@Composable fun SettingsScreen(ui:StudyUi,backup:()->Unit,restore:()->Unit,recovery:()->Unit,exportIssues:()->Unit){
    val settings=ui.state.settings
    var count by rememberSaveable{mutableStateOf(settings.dailyCount.toString())}
    var date by rememberSaveable{mutableStateOf(settings.targetDate)}
    var intervals by rememberSaveable{mutableStateOf(settings.intervals.joinToString(","))}
    var settingsError by remember{mutableStateOf<String?>(null)}
    LazyColumn(Modifier.fillMaxSize(),contentPadding=PaddingValues(20.dp),verticalArrangement=Arrangement.spacedBy(20.dp)){
        item{PageTitle("","설정","회원가입 없이, 모든 기록은 기기 안에 저장됩니다.")}
        item{Column(verticalArrangement=Arrangement.spacedBy(12.dp)){Text("읽기 편한 화면",style=MaterialTheme.typography.titleLarge);FlowButtons(listOf("system" to "시스템 테마","light" to "밝게","dark" to "어둡게"),settings.theme,{theme->ui.vm.settings{it.copy(theme=theme)}});Text("앱 글자 크기 ${"%.0f".format(settings.textScale*100)}% · 시스템 글자 확대도 함께 적용");Slider(value=settings.textScale,onValueChange={scale->ui.vm.settings{it.copy(textScale=scale)}},valueRange=.85f..1.5f,steps=12);Text("SQL 노트는 장식 애니메이션과 자동 소리·진동을 사용하지 않습니다. 해설은 직접 단계 버튼으로 넘깁니다.",style=MaterialTheme.typography.bodySmall);Row(verticalAlignment=Alignment.CenterVertically){Text("SQL 줄바꿈",Modifier.weight(1f));Switch(settings.wrapSql,{wrap->ui.vm.settings{it.copy(wrapSql=wrap)}})} }}
        item{Column(verticalArrangement=Arrangement.spacedBy(12.dp)){Text("부담 없는 분량",style=MaterialTheme.typography.titleLarge);OutlinedTextField(count,{count=it.filter(Char::isDigit).take(3)},label={Text("하루 학습량")},supportingText={Text("1~200문항")},modifier=Modifier.fillMaxWidth(),singleLine=true);OutlinedTextField(date,{date=it.take(10)},label={Text("목표일 (선택)")},supportingText={Text("YYYY-MM-DD 형식")},modifier=Modifier.fillMaxWidth(),singleLine=true);Text("직접 입력한 목표일입니다. 공식 시험 일정으로 표시하지 않아요.",style=MaterialTheme.typography.bodySmall);OutlinedTextField(intervals,{intervals=it.take(60)},label={Text("복습 간격")},supportingText={Text("일 단위 · 쉼표로 구분")},modifier=Modifier.fillMaxWidth(),singleLine=true);Text("기본 1·3·7·14·30일은 초기 제품 규칙입니다. 모든 사람에게 최적이라고 가정하지 않습니다.",style=MaterialTheme.typography.bodySmall);settingsError?.let{Text(it,color=MaterialTheme.colorScheme.error)};OutlinedButton(onClick={
            val daily=count.toIntOrNull();val days=intervals.split(',').mapNotNull{it.trim().toIntOrNull()};val validDate=date.isBlank()||runCatching{LocalDate.parse(date)}.isSuccess
            if(daily==null||daily !in 1..200||days.size!=intervals.split(',').size||days.isEmpty()||days.size>10||days.any{it !in 1..365}||days!=days.distinct().sorted()||!validDate)settingsError="학습량, 날짜, 오름차순 복습 간격을 확인해 주세요."
            else{ui.vm.mutate("학습 설정을 저장했어요"){s->s.copy(settings=s.settings.copy(dailyCount=daily,targetDate=date,targetDateSource="user",intervals=days))};settingsError=null}
        }){Text("학습 설정 저장")}}}
        item{Paper{Text("기록을 안전하게 옮기기",style=MaterialTheme.typography.titleLarge);Text("별표·모든 시도·필기·노트와 강의 진도·자기점검 답안·진행 중 답안·설정이 포함됩니다. 복원은 미리 검사한 파일로 전체 교체하며 자동 병합하지 않습니다.",style=MaterialTheme.typography.bodyMedium);Button(onClick=backup,modifier=Modifier.fillMaxWidth()){Text("전체 기록 내보내기")};OutlinedButton(onClick=restore,modifier=Modifier.fillMaxWidth()){Text("백업 파일 검사·복원")};TextButton(onClick=recovery){Text("복원 전 로컬 복구 지점 열기")};Text("OS 자동 백업은 비활성화했습니다. 기기 이동 전 파일로 내보내세요. 백업은 암호화하지 않은 개인 기록 파일입니다.",style=MaterialTheme.typography.bodySmall)}}
        item{Column{NoteRow("01","나의 필기와 북마크","${ui.state.annotations.size}개 필기 · ${ui.state.annotations.count{it.archived}}개 재연결 보관함",{ui.nav("annotations")});NoteRow("02","학습 기록","최초·반복·도움 사용 기록",{ui.nav("history")});NoteRow("03","콘텐츠 버전과 출처","${ui.pack.version} · ${ui.pack.sources.size}개 자료",{ui.nav("sources")})}}
        item{if(ui.state.issues.isEmpty())Text("표시한 내용 오류가 없어요.",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)else Paper{Text("로컬 내용 검토 목록",style=MaterialTheme.typography.titleLarge);Text("표시한 항목 ${ui.state.issues.size}개 · 제외 ${ui.state.issues.count{it.exclude}}개");ui.state.issues.takeLast(10).reversed().forEach{issue->Text("${issue.contentId} · ${issue.description}",style=MaterialTheme.typography.bodyMedium);if(issue.exclude)TextButton(onClick={ui.vm.mutate{s->s.copy(issues=s.issues.map{if(it.id==issue.id)it.copy(exclude=false)else it})}}){Text("기록 유지하고 제외 해제")}};OutlinedButton(onClick=exportIssues,enabled=ui.state.issues.isNotEmpty()){Text("검토 목록 내보내기")}}}
        item{Text("SQL 노트 ${BuildConfig.VERSION_NAME} · 개인용 개발 빌드\n온라인 서비스·광고·결제·학습 기록 전송 없음\n사람 전문가 검수와 Galaxy 실기기 검증은 별도입니다.",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)}
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable fun AnnotationsScreen(ui:StudyUi){
    var query by rememberSaveable{mutableStateOf("")};var filter by rememberSaveable{mutableStateOf("all")};var editId by rememberSaveable{mutableStateOf<String?>(null)};var delete by remember{mutableStateOf<Annotation?>(null)}
    val edit=ui.state.annotations.find{it.id==editId}
    val busy by ui.vm.busy.collectAsState()
    val error by ui.vm.error.collectAsState()
    val annotations=ui.state.annotations.filter{(filter!="archive"||it.archived)&&(query.isBlank()||it.memo.contains(query,true)||it.quote.contains(query,true))}.sortedByDescending{it.at}
    LazyColumn(Modifier.fillMaxSize(),contentPadding=PaddingValues(20.dp),verticalArrangement=Arrangement.spacedBy(20.dp)){
        item{PageTitle("","필기와 북마크","연결이 달라진 문장도 보관함에 남겨 둡니다.")}
        item{OutlinedTextField(query,{query=it},label={Text("필기 검색")},placeholder={Text("메모 또는 인용 문장")},modifier=Modifier.fillMaxWidth());FlowButtons(listOf("all" to "모든 필기","archive" to "재연결 보관함","bookmark" to "노트 북마크"),filter,{filter=it})}
        if(filter=="bookmark"){
            val notes=ui.pack.notes.filter{n->ui.state.noteBookmarks.any{it.id==n.id}}
            if(notes.isEmpty())item{EmptyState("북마크한 노트가 없어요","노트 상단의 북마크를 눌러 보관할 수 있어요.","노트 펼치기",{ui.nav("notes")})}
            items(notes,key={it.id}){n->NoteRow(n.objectiveId,n.title,n.summary,{ui.note(n.id)})}
        }else{
            if(annotations.isEmpty())item{EmptyState("보관된 필기가 없어요","노트의 문장을 길게 선택하거나 단락 메모를 사용해 보세요.","노트로 이동",{ui.nav("notes")})}
            items(annotations,key={it.id}){a->Paper{Eyebrow(if(a.archived)"재연결 보관함"else when(a.style){"underline"->"밑줄";"highlight"->"형광펜";else->"메모"});Text("“${a.quote}”",style=MaterialTheme.typography.bodyMedium);if(a.memo.isNotBlank())Text(a.memo);Text(dateText(a.at),style=MaterialTheme.typography.bodySmall);FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){TextButton(onClick={editId=a.id}){Text("메모 수정")};TextButton(onClick={ui.note(a.noteId)},enabled=ui.pack.notes.any{it.id==a.noteId}){Text("노트 보기")};TextButton(onClick={delete=a}){Text("삭제")}}}}
        }
    }
    edit?.let{a->
        var text by rememberSaveable(a.id){mutableStateOf(a.memo)}
        var pending by rememberSaveable(a.id){mutableStateOf<String?>(null)}
        val generation=rememberSaveable(a.id){ui.vm.repository.restoreGeneration}
        LaunchedEffect(pending,busy,error,a.memo){
            if(pending!=null&&!busy){if(error!=null)pending=null else if(a.memo==pending)editId=null}
        }
        AlertDialog(onDismissRequest={if(!ui.vm.busy.value)editId=null},title={Text("나의 메모 수정")},text={OutlinedTextField(text,{text=it},enabled=!busy,minLines=3,label={Text("메모")})},confirmButton={TextButton(enabled=!busy,onClick={if(!ui.vm.busy.value){
            val savedText=text;pending=savedText
            ui.vm.launchWork{ui.vm.repository.update{current->
                require(ui.vm.repository.restoreGeneration==generation){"기록이 복원되어 이 초안을 자동 저장하지 않았어요. 내용을 복사한 뒤 다시 열어 주세요."}
                require(current.annotations.any{it.id==a.id}){"수정할 메모를 찾지 못했어요. 입력한 내용은 이 창에 남겨 두었어요."}
                current.copy(annotations=current.annotations.map{if(it.id==a.id)it.copy(memo=savedText)else it})
            };ui.vm.message.value="메모를 저장했어요"}
        }}){Text("저장")}},dismissButton={TextButton(enabled=!busy,onClick={editId=null}){Text("취소")}})
    }
    delete?.let{a->AlertDialog(onDismissRequest={delete=null},title={Text("이 필기만 삭제할까요?")},text={DialogBody("선택한 문장의 강조와 메모를 삭제합니다. 다른 필기와 학습 기록은 유지됩니다.")},confirmButton={TextButton(onClick={ui.vm.mutate{s->s.copy(annotations=s.annotations.filterNot{it.id==a.id})};delete=null}){Text("이 필기 삭제")}},dismissButton={TextButton(onClick={delete=null}){Text("유지")}})}
}

@Composable fun SourcesScreen(ui:StudyUi){
    val context=LocalContext.current
    LazyColumn(Modifier.fillMaxSize(),contentPadding=PaddingValues(20.dp),verticalArrangement=Arrangement.spacedBy(22.dp)){
        item{PageTitle("","출처와 검토 범위","콘텐츠 팩 ${ui.pack.version}")}
        item{Paper{Text("공식 SQLD 안내·출제기준·변경 공지·정오표: 접근 실패로 최신 원문 미확인\n\n수록 문항: 독자 창작\nSQL 정답: 공식 문서 대조·저술자 풀이 검토\n일부 문항: 별도 AI 블라인드 교차 검토 (검수 보고서에 ID 기록)\nOracle/SQL Server 실제 엔진 실행: 미실시\n사람 전문가 검수: 미실시",style=MaterialTheme.typography.bodyMedium)}}
        item{Paper{
            Text("63강 자료",style=MaterialTheme.typography.titleLarge)
            Text(ui.course.provenance,style=MaterialTheme.typography.bodyMedium)
            Text(ui.course.reviewNote,style=MaterialTheme.typography.bodySmall)
            Text("강의 노트 ${ui.course.lessons.size}개 · 자기점검은 별도 학습 기록",style=MaterialTheme.typography.bodySmall)
            TextButton(onClick={ui.nav("course")}){Text("강의 목차 보기")}
        }}
        items(ui.pack.sources,key={it.sourceId}){s->Column(verticalArrangement=Arrangement.spacedBy(6.dp)){Eyebrow(s.publisher);Text(s.title,style=MaterialTheme.typography.titleMedium);Text("${s.sourceId} · 확인일 ${s.checkedAt}\n${s.accessStatus}\n${s.usageScope}",style=MaterialTheme.typography.bodySmall);Text(s.license,style=MaterialTheme.typography.bodySmall);if(s.url.startsWith("https://"))TextButton(onClick={runCatching{context.startActivity(Intent(Intent.ACTION_VIEW,Uri.parse(s.url)))}.onFailure{ui.vm.error.value="브라우저를 열 수 없습니다."}}){Text("원문 웹사이트 열기 ↗")};HorizontalDivider()}}
    }
}
