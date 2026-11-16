package kr.sqld.study

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.saveable.Saver
import androidx.compose.runtime.saveable.rememberSaveableStateHolder
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.serialization.encodeToString
import java.io.ByteArrayOutputStream
import java.util.UUID

class MainActivity:ComponentActivity(){override fun onCreate(savedInstanceState:Bundle?){super.onCreate(savedInstanceState);enableEdgeToEdge();setContent{SqlNoteApp()}}}

data class StudyUi(val vm:StudyViewModel,val state:StudyState,val pack:ContentPack,val nav:(String)->Unit,val note:(String)->Unit,val practice:(List<Question>,String)->Unit,val issue:(String)->Unit,val annotate:(String,String,String,String)->Unit,val sidebarsExpanded:Boolean=true,val studyPlan:StudyPlan?=null) {
    val course:CoursePack get()=vm.repository.course
    val courseVisuals:CourseVisualPack get()=vm.repository.courseVisuals
}
private data class PracticeRequest(val questions:List<Question>,val title:String)
private data class AnnotationRequest(val noteId:String,val blockId:String,val quote:String,val style:String,val id:String=UUID.randomUUID().toString(),val generation:Long=0)
private val AnnotationRequestSaver=Saver<AnnotationRequest?,List<String>>(
    save={a->a?.let{listOf(it.noteId,it.blockId,it.quote,it.style,it.id,it.generation.toString())}},
    restore={AnnotationRequest(it[0],it[1],it[2],it[3],it[4],it[5].toLong())})
private data class IssueRequest(val contentId:String,val id:String=UUID.randomUUID().toString(),val generation:Long=0)
private val IssueRequestSaver=Saver<IssueRequest?,List<String>>(
    save={a->a?.let{listOf(it.contentId,it.id,it.generation.toString())}},
    restore={IssueRequest(it[0],it[1],it[2].toLong())})

@OptIn(ExperimentalMaterial3Api::class)
@Composable fun SqlNoteApp(vm:StudyViewModel=viewModel()){
    val state by vm.state.collectAsState();val ready by vm.ready.collectAsState();val busy by vm.busy.collectAsState();val error by vm.error.collectAsState();val message by vm.message.collectAsState()
    val dark=when(state.settings.theme){"dark"->true;"light"->false;else->isSystemInDarkTheme()}
    SqlNoteTheme(dark,state.settings.textScale){
        val colors=MaterialTheme.colorScheme
        var route by rememberSaveable{mutableStateOf("home")}
        var history by rememberSaveable{mutableStateOf<List<String>>(emptyList())}
        var navigationEpoch by rememberSaveable{mutableIntStateOf(0)}
        var questionReviewRequest by rememberSaveable{mutableIntStateOf(0)}
        var sidebarsExpanded by rememberSaveable{mutableStateOf(true)}
        val screenStates=key(navigationEpoch){rememberSaveableStateHolder()}
        var guardedNote by remember{mutableStateOf<String?>(null)}
        var guardedPop by remember{mutableStateOf(false)}
        fun needsConversion(to:String):Boolean {
            val strict=vm.state.value.sessions.find{it.mode=="strict"&&it.submittedAt==null}?:return false
            return to.substringBefore(':') in listOf("note","notes","course","lesson","walk","plan","search","review","history","annotations","unit","unitanswers") || (to.startsWith("session:")&&to.substringAfter(':').substringBefore(':')!=strict.id)
        }
        fun navigate(to:String,pop:Boolean=false){
            if(needsConversion(to)){guardedPop=pop;guardedNote=to;return}
            fun commit(){
                if(to.startsWith("session:")&&to.endsWith(":review"))questionReviewRequest++
                if(pop)history=ArrayList(history.dropLast(1))else if(to!=route)history=ArrayList(history+route)
                route=to
            }
            val sessionId=to.takeIf{it.startsWith("session:")}?.substringAfter(':')?.substringBefore(':')
            val noteId=to.takeIf{it.startsWith("note:")}?.substringAfter(':')
            val lessonId=to.takeIf{it.startsWith("lesson:")}?.substringAfter(':')
            val current=vm.state.value
            val selectSession=sessionId!=null&&current.activeSessionId!=sessionId&&current.sessions.any{it.id==sessionId&&it.submittedAt==null}
            val selectNote=vm.ready.value&&noteId!=null&&current.lastNoteId!=noteId&&vm.repository.pack.notes.any{it.id==noteId}
            val selectLesson=vm.ready.value&&lessonId!=null&&vm.repository.course.lessons.any{it.id==lessonId}
            val selectWalk=vm.ready.value&&to.startsWith("walk:")
            if(selectSession||selectNote||selectLesson||selectWalk){
                vm.launchWork{vm.repository.update{s->
                    val session=s.sessions.find{it.id==s.activeSessionId&&it.submittedAt==null}
                    val helped=if((selectLesson||selectWalk)&&session!=null)StudyEngine.help(s,session.id,session.current,"note",System.currentTimeMillis())else s
                    val selected=helped.copy(
                    activeSessionId=if(selectSession&&s.sessions.any{it.id==sessionId&&it.submittedAt==null})sessionId else s.activeSessionId,
                    lastNoteId=if(selectNote)noteId else s.lastNoteId
                    )
                    if(selectLesson)CourseStudy.update(selected,lessonId!!,change={it})else selected
                };commit()}
            }else commit()
        }
        fun nav(to:String)=navigate(to)
        fun back()=navigate(history.lastOrNull()?:"home",pop=true)
        BackHandler(route!="home"){back()}
        var practice by remember{mutableStateOf<PracticeRequest?>(null)}
        var annotation by rememberSaveable(stateSaver=AnnotationRequestSaver){mutableStateOf<AnnotationRequest?>(null)}
        var issue by rememberSaveable(stateSaver=IssueRequestSaver){mutableStateOf<IssueRequest?>(null)}
        var restoreCandidate by remember{mutableStateOf<StudyState?>(null)}
        val context=LocalContext.current
        val snackbar=remember{SnackbarHostState()}
        LaunchedEffect(message){message?.let{
            val undo=if(it=="별표 상태를 저장했어요")vm.undoStar.value else null
            val result=snackbar.showSnackbar(it,actionLabel=if(undo!=null)"실행 취소"else null,duration=SnackbarDuration.Short)
            if(result==SnackbarResult.ActionPerformed&&undo!=null)vm.mutate{s->StudyEngine.bookmark(s,undo,System.currentTimeMillis())}
            vm.message.value=null;vm.undoStar.value=null
        }}
        val backup=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")){uri->if(uri!=null)vm.launchWork{
            val encoded=vm.repository.export();context.contentResolver.openOutputStream(uri,"wt")?.bufferedWriter(Charsets.UTF_8)?.use{it.write(encoded)}?:error("파일을 열지 못했습니다.")
            vm.message.value="전체 학습 기록을 내보냈어요"
        }}
        val exportIssues=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")){uri->if(uri!=null)vm.launchWork{
            context.contentResolver.openOutputStream(uri,"wt")?.bufferedWriter(Charsets.UTF_8)?.use{it.write(Codec.encodeToString(state.issues))}?:error("파일을 열지 못했습니다.")
            vm.message.value="로컬 오류 검토 목록을 내보냈어요"
        }}
        val importBackup=rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()){uri->if(uri!=null)vm.launchWork{
            val bytes=context.contentResolver.openInputStream(uri)?.use{input->
                val output=ByteArrayOutputStream();val chunk=ByteArray(8192)
                while(true){val count=input.read(chunk);if(count<0)break;require(output.size()+count<=BackupCodec.MAX_BYTES){"백업은 최대 32MB까지 지원합니다."};output.write(chunk,0,count)};output.toByteArray()
            }?:error("파일을 읽지 못했습니다.")
            restoreCandidate=BackupCodec.decode(bytes.toString(Charsets.UTF_8))
        }}
        if(!ready){Surface(Modifier.fillMaxSize()){Column(Modifier.safeDrawingPadding().verticalScroll(rememberScrollState()).padding(28.dp),verticalArrangement=Arrangement.Center){
            Text("SQL 노트",style=MaterialTheme.typography.headlineLarge);Spacer(Modifier.height(20.dp))
            if(error==null){CircularProgressIndicator();Text("학습 자료를 펼치는 중이에요")}
            else{Text(error!!);Spacer(Modifier.height(16.dp));Button(onClick={vm.retryInitialization()}){Text("다시 열기")};Text("계속 실패하면 앱을 종료한 뒤 다시 열어 주세요. 저장된 기록을 지우거나 앱을 삭제하지 마세요.",style=MaterialTheme.typography.bodySmall)}
        }};return@SqlNoteTheme}
        val pack=vm.repository.pack
        val studyPlan=remember(context,vm.repository.course){runCatching{
            context.assets.open("study-plan.json").bufferedReader(Charsets.UTF_8).use{Codec.decodeFromString<StudyPlan>(it.readText())}.validate(vm.repository.course)
        }.getOrNull()}
        fun openNote(id:String){
            val current=vm.state.value
            val strict=current.sessions.find{it.mode=="strict"&&it.submittedAt==null}
            if(strict!=null){guardedPop=false;guardedNote="note:$id";return}
            val sessionId=if(route.startsWith("session:"))route.substringAfter(':').substringBefore(':')else current.activeSessionId
            vm.launchWork{
                vm.repository.update{saved->
                    val session=saved.sessions.find{it.id==sessionId&&it.submittedAt==null}
                    val helped=if(session!=null)StudyEngine.help(saved,session.id,session.current,"note",System.currentTimeMillis())else saved
                    helped.copy(lastNoteId=id)
                }
                nav("note:$id")
            }
        }
        val ui=StudyUi(vm,state,pack,{nav(it)},{openNote(it)},{q,title->practice=PracticeRequest(q,title)},{issue=IssueRequest(it,generation=vm.repository.restoreGeneration)},{n,b,q,s->annotation=AnnotationRequest(n,b,q,s,generation=vm.repository.restoreGeneration)},sidebarsExpanded,studyPlan)
        val sessionRoute=route.startsWith("session:")
        val sessionTopic=if(sessionRoute)state.sessions.find{it.id==route.substringAfter(':').substringBefore(':')}?.let{s->
            pack.notes.find{it.id==s.items[s.current].question.explanation.relatedNoteId}?.title
        }else null
        val tab=route.substringBefore(':')
        val focusedReader=sessionRoute||tab=="note"||tab=="lesson"||tab=="walk"
        val selectedTab=when {
            tab=="unit"->"review"
            tab=="unitanswers"->if(state.sessions.find{it.id==route.substringAfter(':')}?.isUnitMock()==true)"mock"else"review"
            tab=="fullmock"->"mock"
            tab in listOf("course","lesson","note","notes","walk")->"course"
            tab=="plan"->"home"
            else->tab
        }
        val compactNav=LocalDensity.current.fontScale*state.settings.textScale>=1.6f
        val tabs=listOf(Triple("home","홈",Icons.Outlined.Home),Triple("course","진도",Icons.Outlined.MenuBook),Triple("review","복습",Icons.Outlined.Bookmarks),Triple("mock","모의고사",Icons.Outlined.Timer),Triple("settings","설정",Icons.Outlined.Tune))
        BoxWithConstraints(Modifier.fillMaxSize()){
            val wide=maxWidth>=840.dp
            Row(Modifier.fillMaxSize()){
                if(wide&&!sessionRoute&&sidebarsExpanded)NavigationRail(modifier=Modifier.fillMaxHeight().testTag("study-sidebar"),containerColor=colors.surface,header={Surface(color=colors.tertiaryContainer,contentColor=colors.onTertiaryContainer,shape=RoundedCornerShape(14.dp),modifier=Modifier.padding(vertical=20.dp,horizontal=12.dp)){Text("SQL",Modifier.padding(horizontal=12.dp,vertical=14.dp),style=MaterialTheme.typography.titleSmall)}}){tabs.forEach{(id,label,icon)->NavigationRailItem(selected=selectedTab==id,onClick={nav(id)},modifier=Modifier.testTag("nav-$id"),icon={Icon(icon,label)},label={Text(label)},colors=NavigationRailItemDefaults.colors(indicatorColor=colors.primaryContainer,selectedIconColor=colors.primary,selectedTextColor=colors.primary))}}
                Scaffold(modifier=Modifier.weight(1f),containerColor=colors.background,snackbarHost={SnackbarHost(snackbar,Modifier.padding(bottom=if(sessionRoute)160.dp else 0.dp))},
                    topBar={TopAppBar(title={Text(sessionTopic?:if(sessionRoute)"문제 노트"else"SQL 노트",style=MaterialTheme.typography.titleMedium,maxLines=1,overflow=androidx.compose.ui.text.style.TextOverflow.Ellipsis)},navigationIcon={
                        Row(verticalAlignment=Alignment.CenterVertically){
                            if(route!="home")IconButton(onClick={back()}){Icon(Icons.Outlined.ArrowBack,"뒤로")}
                            if(wide&&!sessionRoute)TextButton(onClick={sidebarsExpanded=!sidebarsExpanded},modifier=Modifier.heightIn(min=48.dp).testTag("sidebar-toggle").semantics{stateDescription=if(sidebarsExpanded)"목록 펼쳐짐"else"목록 접힘"}){
                                Icon(if(sidebarsExpanded)Icons.Outlined.MenuOpen else Icons.Outlined.Menu,null)
                                Spacer(Modifier.width(6.dp));Text(if(sidebarsExpanded)"목록 접기"else"목록 펼치기")
                            }
                        }
                    },actions={if(!sessionRoute)IconButton(onClick={nav("search")}){Icon(Icons.Outlined.Search,"노트와 연습문제 검색")}},colors=TopAppBarDefaults.topAppBarColors(containerColor=colors.surface))},
                    bottomBar={if(!wide&&!focusedReader)NavigationBar(containerColor=colors.surface,tonalElevation=0.dp){tabs.forEach{(id,label,icon)->NavigationBarItem(selected=selectedTab==id,onClick={nav(id)},modifier=Modifier.testTag("nav-$id"),icon={Icon(icon,label)},label=if(compactNav)null else {{Text(label,style=MaterialTheme.typography.labelMedium)}},alwaysShowLabel=true,colors=NavigationBarItemDefaults.colors(indicatorColor=colors.primaryContainer,selectedIconColor=colors.primary,selectedTextColor=colors.primary))}}}
                ){padding->
                    Box(Modifier.fillMaxSize().padding(padding),contentAlignment=Alignment.TopCenter){
                        Box(Modifier.fillMaxSize()){
                            screenStates.SaveableStateProvider(route){when(tab){
                                "home"->HomeScreen(ui)
                                "plan"->StudyPlanScreen(ui)
                                "notes","search"->NotesScreen(ui,searchMode=tab=="search")
                                "note"->NoteScreen(ui,route.substringAfter(':'))
                                "course"->CourseScreen(ui,reviewOnly=route=="course:review")
                                "lesson"->CourseLessonScreen(ui,route.substringAfter(':'))
                                "walk"->LearningWalkScreen(ui,route.substringAfter(':'))
                                "unit"->UnitPracticeScreen(ui,route.split(':').getOrNull(1).orEmpty(),route.split(':').getOrNull(2).orEmpty())
                                "unitanswers"->UnitAnswersScreen(ui,route.substringAfter(':'))
                                "session"->SessionScreen(ui,route.substringAfter(':').substringBefore(':'),route.endsWith(":review"),if(route.endsWith(":review"))questionReviewRequest else 0)
                                "review"->ReviewScreen(ui)
                                "mock"->UnitMockScreen(ui,route.split(':').getOrNull(1).orEmpty())
                                "fullmock"->MockScreen(ui)
                                "history"->HistoryScreen(ui)
                                "annotations"->AnnotationsScreen(ui)
                                "sources"->SourcesScreen(ui)
                                "settings"->SettingsScreen(ui,{backup.launch("SQL-note-backup.json")},{importBackup.launch(arrayOf("application/json","text/plain","application/octet-stream"))},{vm.launchWork{restoreCandidate=vm.repository.recoveryCandidate();if(restoreCandidate==null)vm.message.value="아직 복원 전 복구 지점이 없어요"}},{exportIssues.launch("SQL-note-content-issues.json")})
                                else->HomeScreen(ui)
                            }}
                        }
                        if(busy)LinearProgressIndicator(Modifier.fillMaxWidth().align(Alignment.TopCenter))
                    }
                }
            }
        }
        error?.let{AlertDialog(onDismissRequest={vm.error.value=null},title={Text("저장을 확인해 주세요")},text={DialogBody(it)},confirmButton={TextButton(onClick={vm.error.value=null}){Text("확인")}})}
        practice?.let{request->
            val strict=state.sessions.find{it.mode=="strict"&&it.submittedAt==null}
            var count by remember(request){mutableStateOf(minOf(state.settings.dailyCount,request.questions.size).toString())}
            var mode by remember{mutableStateOf("immediate")}
            val actual=(count.toIntOrNull()?:0).coerceAtMost(request.questions.size)
            AlertDialog(onDismissRequest={practice=null},title={Text("연습 시작")},text={Column(Modifier.verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(12.dp)){
                Text(request.title,style=MaterialTheme.typography.titleSmall)
                Text("대상 ${request.questions.size}문항 · 중복 없이 최대 ${request.questions.size}문항")
                FlowButtons(listOf("10" to "10문항","20" to "20문항","50" to "50문항"),count,{count=it})
                OutlinedTextField(count,{count=it.filter(Char::isDigit).take(3)},label={Text("직접 개수")},modifier=Modifier.fillMaxWidth(),singleLine=true)
                FlowButtons(listOf("immediate" to "한 문제씩 채점","batch" to "전체 풀이 후 채점"),mode,{mode=it})
                Text("보기 선택만으로는 채점되지 않아요. 전체 풀이 중에도 현재 문제만 채점할 수 있어요.",style=MaterialTheme.typography.bodySmall)
                if(strict!=null)Text("진행 중인 실전 모의고사가 있습니다. 연습을 시작하면 해당 모의고사는 연습으로 전환되고 최초 실전 지표에서 영구 제외됩니다.",color=colors.error)
            }},confirmButton={Button(enabled=actual>0&&!busy,onClick={if(strict!=null)vm.mutate{StudyEngine.convert(it,strict.id,System.currentTimeMillis())};vm.start(request.questions.take(actual),mode,request.title){nav("session:$it")};practice=null}){Text(if(strict!=null)"연습 전환 후 ${actual}문항 시작"else"${actual}문항 시작")}},dismissButton={TextButton(onClick={practice=null}){Text("취소")}})
        }
        guardedNote?.let{target->AlertDialog(onDismissRequest={guardedNote=null},title={Text("연습 모드로 전환할까요?")},text={DialogBody("진행 중인 모의고사의 답안은 유지됩니다. 다른 학습 자료를 열면 이 세션은 최초 실전 진단에서 영구 제외됩니다.")},confirmButton={TextButton(onClick={vm.launchWork{vm.repository.update{s0->s0.sessions.filter{it.mode=="strict"&&it.submittedAt==null}.fold(s0){acc,s->StudyEngine.convert(acc,s.id,System.currentTimeMillis())}};val pop=guardedPop;guardedNote=null;navigate(target,pop)}}){Text("전환하고 보기")}},dismissButton={TextButton(onClick={guardedNote=null}){Text("실전 유지")}})}
        annotation?.let{a->
            var memo by rememberSaveable(a.id){mutableStateOf("")}
            // Observe the committed stable ID even if rotation replaced the old callback.
            LaunchedEffect(a.id,state.annotations){if(state.annotations.any{it.id==a.id})annotation=null}
            AlertDialog(onDismissRequest={if(!vm.busy.value)annotation=null},title={Text(if(a.style=="memo")"여백에 메모"else"선택한 문장 저장")},text={Column(Modifier.verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(12.dp)){
                Text("“${a.quote}”",style=MaterialTheme.typography.bodyMedium)
                OutlinedTextField(memo,{memo=it},enabled=!busy,label={Text("나의 메모 (선택)")},minLines=2)
            }},confirmButton={TextButton(enabled=!busy,onClick={if(!vm.busy.value){
                val saved=Annotation(a.id,a.noteId,a.blockId,a.quote,memo,a.style,System.currentTimeMillis())
                vm.launchWork{vm.repository.update{current->
                    require(vm.repository.restoreGeneration==a.generation){"기록이 복원되어 이 초안을 자동 저장하지 않았어요. 내용을 복사한 뒤 다시 열어 주세요."}
                    if(current.annotations.any{it.id==a.id})current else current.copy(annotations=current.annotations+saved)
                };vm.message.value="문장과 메모를 저장했어요"}
            }}){Text("저장")}},dismissButton={TextButton(enabled=!busy,onClick={annotation=null}){Text("취소")}})
        }
        issue?.let{request->
            val id=request.contentId
            var description by rememberSaveable(request.id){mutableStateOf("")}
            var exclude by rememberSaveable(request.id){mutableStateOf(!id.startsWith("note-"))}
            LaunchedEffect(request.id,state.issues){if(state.issues.any{it.id==request.id})issue=null}
            AlertDialog(onDismissRequest={if(!vm.busy.value)issue=null},title={Text("내용 오류 표시")},text={Column(Modifier.verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(12.dp)){
                Text("기기 안의 검토 목록에 저장됩니다. 외부로 전송하지 않아요.")
                OutlinedTextField(description,{description=it},enabled=!busy,label={Text("오류 내용")},minLines=3)
                if(!id.startsWith("note-"))Row(verticalAlignment=Alignment.Top){Checkbox(exclude,{exclude=it},enabled=!busy);Text("앞으로의 연습·복습에서 제외",Modifier.weight(1f).padding(top=10.dp))}
            }},confirmButton={TextButton(enabled=description.isNotBlank()&&!busy,onClick={if(!vm.busy.value){
                val saved=ContentIssue(request.id,id,pack.version,description,exclude,System.currentTimeMillis())
                vm.launchWork{vm.repository.update{current->
                    require(vm.repository.restoreGeneration==request.generation){"기록이 복원되어 이 초안을 자동 저장하지 않았어요. 내용을 복사한 뒤 다시 열어 주세요."}
                    if(current.issues.any{it.id==request.id})current else current.copy(issues=current.issues+saved)
                };vm.message.value="로컬 검토 목록에 저장했어요"}
            }}){Text("표시 저장")}},dismissButton={TextButton(enabled=!busy,onClick={issue=null}){Text("취소")}})
        }
        restoreCandidate?.let{candidate->AlertDialog(onDismissRequest={if(!vm.busy.value)restoreCandidate=null},title={Text("전체 기록을 복원할까요?")},text={Column(Modifier.verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(8.dp)){Text("현재 기록을 아래 파일의 기록으로 교체합니다. 자동 병합하지 않습니다. 적용 직전 현재 기록의 로컬 복구 지점을 보관합니다.");Text("시도 ${state.submissions.size} → ${candidate.submissions.size}\n별표 ${state.bookmarks.size} → ${candidate.bookmarks.size}\n텍스트 필기 ${state.annotations.size} → ${candidate.annotations.size}\nSQL 필기 문서 ${state.inkDocuments.size} → ${candidate.inkDocuments.size}\n학습 세션 ${state.sessions.size} → ${candidate.sessions.size}\n강의 진도 ${state.courseProgress.size} → ${candidate.courseProgress.size}강\n자기점검 기록 ${state.courseProgress.sumOf{it.checks.size}} → ${candidate.courseProgress.sumOf{it.checks.size}}개\n설정·노트 진도·복습 일정도 교체");Text("백업 콘텐츠 ${candidate.contentVersion}",style=MaterialTheme.typography.bodySmall)}},confirmButton={Button(enabled=!busy,onClick={if(!vm.busy.value)vm.launchWork{vm.repository.restore(candidate);vm.clearInkDrafts();restoreCandidate=null;navigationEpoch++;route="home";history=arrayListOf();vm.message.value="전체 기록을 복원했어요"}}){Text("검사한 기록으로 교체")}},dismissButton={TextButton(enabled=!busy,onClick={if(!vm.busy.value)restoreCandidate=null}){Text("기존 기록 유지")}})}
    }
}
