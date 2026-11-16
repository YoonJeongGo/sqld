package kr.sqld.study

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.semantics.*
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.debounce
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.FlowPreview

/** Only the countdown reads the one-second clock; question content need not recompose for it. */
@Composable internal fun SessionCountdown(remainingMillis:Long,lastWall:Long,clock:StateFlow<Long>){
    val now by clock.collectAsState()
    val remaining=(remainingMillis-(now-lastWall).coerceAtLeast(0)).coerceAtLeast(0)
    Text("%02d:%02d".format(remaining/60000,remaining/1000%60),style=MaterialTheme.typography.titleMedium)
}

@OptIn(ExperimentalLayoutApi::class,FlowPreview::class)
@Composable fun SessionScreen(ui:StudyUi,id:String,startReview:Boolean=false,reviewRequest:Int=0){
    val s=ui.state.sessions.find{it.id==id}?:return
    val largeText=LocalDensity.current.fontScale*ui.state.settings.textScale>=1.6f
    val gradeLabel=if(s.mode in listOf("batch","strict","mixed"))"현재 문제만 채점"else"이 문제 채점"
    val item=s.items[s.current];val q=item.question
    val unit=q.isUnitQuestion()
    val solvingMaterial=unit||item.submissionId==null
    val modeLabel=if(item.submissionId!=null)"채점 완료"else when(s.mode){"strict"->"실전 모의고사";"mixed"->"전환된 연습";"batch"->"전체 풀이 후 채점";else->"한 문제씩 채점"}
    val submission=ui.state.submissions.find{it.id==item.submissionId}
    var confirmSubmit by remember{mutableStateOf(false)}
    var convertAction by remember{mutableStateOf<String?>(null)}
    var grid by remember{mutableStateOf(false)}
    var showResult by rememberSaveable(id){mutableStateOf(!startReview&&s.submittedAt!=null)}
    var appliedReviewRequest by rememberSaveable(id){mutableIntStateOf(reviewRequest)}
    var previousSubmittedAt by rememberSaveable(id){mutableStateOf(s.submittedAt)}
    var confidenceVisible by rememberSaveable(id,s.current){mutableStateOf(false)}
    val source=remember(q){WalkSource.from(q)}
    val sourceKey=remember(source){source.fingerprint()}
    var readerMode by rememberSaveable(id,q.id,sourceKey){mutableStateOf("walk")}
    var readerStep by rememberSaveable(id,q.id,sourceKey){mutableIntStateOf(0)}
    var foundations by rememberSaveable(id,q.id,sourceKey){mutableStateOf(false)}
    var detailVisible by rememberSaveable(id,q.id){mutableStateOf(false)}
    var walkthrough by remember(id,q.id,sourceKey){mutableStateOf<SqlWalkthrough?>(null)}
    var walkthroughReady by remember(id,q.id,sourceKey){mutableStateOf(false)}
    // Opening an unsolved question does not even parse the answer-bearing material.
    LaunchedEffect(id,q.id,sourceKey,submission?.id){
        if(submission!=null&&!q.sql.isNullOrBlank()&&!unit){
            walkthrough=runCatching{ui.vm.walkthroughs.question(q)}.getOrNull()
            walkthroughReady=true
        }
    }
    LaunchedEffect(s.submittedAt,startReview,reviewRequest){
        // Saveable-state restoration does not compare the old rememberSaveable inputs.
        // Consume an explicit new return request, while keeping a manually opened summary on rotation.
        if(startReview&&appliedReviewRequest!=reviewRequest){showResult=false;appliedReviewRequest=reviewRequest}
        else if(previousSubmittedAt==null&&s.submittedAt!=null)showResult=true
        previousSubmittedAt=s.submittedAt
    }
    val busy by ui.vm.busy.collectAsState()
    val lifecycle=LocalLifecycleOwner.current.lifecycle
    var foreground by remember{mutableStateOf(lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED))}
    DisposableEffect(lifecycle){val observer=LifecycleEventObserver{_,_->foreground=lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED)};lifecycle.addObserver(observer);onDispose{lifecycle.removeObserver(observer)}}
    LaunchedEffect(id,s.current,item.submissionId,foreground){if(foreground&&s.submittedAt==null&&item.submissionId==null)while(true){delay(5000);ui.vm.mutate{StudyEngine.addTime(it,id,s.current,5000)}}}
    if(showResult&&s.submittedAt!=null){ResultScreen(ui,s,{showResult=false});return}
    fun gradeCurrent(unknown:Boolean=false){if(s.mode=="strict")convertAction=if(unknown)"unknown"else"grade" else ui.vm.grade(id,s.current,unknown)}
    Column(Modifier.fillMaxSize()){
        Column(Modifier.fillMaxWidth().padding(horizontal=12.dp,vertical=2.dp),verticalArrangement=Arrangement.spacedBy(2.dp)){
            if(largeText)Text(modeLabel,style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.primary)
            Row(verticalAlignment=Alignment.CenterVertically,horizontalArrangement=Arrangement.spacedBy(8.dp)){
                if(largeText)Spacer(Modifier.weight(1f))else Text(modeLabel,Modifier.weight(1f),style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.primary)
                if(s.mode=="strict"&&s.submittedAt==null)SessionCountdown(s.remainingMillis,s.lastWall,ui.vm.now)
                StarButton(q.id,ui.state.bookmarks.any{it.id==q.id},{ui.vm.star(q.id)})
                TextButton(onClick={grid=true},modifier=Modifier.heightIn(min=48.dp)){Text("${s.current+1} / ${s.items.size}")}
            }
            LinearProgressIndicator(progress={s.items.count{it.submissionId!=null}.toFloat()/s.items.size},modifier=Modifier.fillMaxWidth(),color=MaterialTheme.colorScheme.primary)
            if(s.clockAnomaly)Text("기기 시간 변경이 감지되어 실전 진단에서 제외되었습니다.",color=MaterialTheme.colorScheme.error,style=MaterialTheme.typography.bodySmall)
        }
        BoxWithConstraints(Modifier.weight(1f).testTag("question-area")){
            val wide=maxWidth>=840.dp
            val scroll=key(q.id){rememberScrollState(item.scroll)}
            LaunchedEffect(q.id,scroll){snapshotFlow{scroll.value}.debounce(200).distinctUntilChanged().collect{value->ui.vm.mutate{StudyEngine.scroll(it,id,s.current,value)}}}
            val hasSql=!q.sql.isNullOrBlank()&&!unit
            val body:@Composable (Modifier)->Unit={modifier->
                Column(modifier.verticalScroll(scroll).padding(12.dp).testTag("question-body"),verticalArrangement=Arrangement.spacedBy(8.dp)){
                    if(solvingMaterial){if(!wide)UnitQuestionMaterial(ui,q)}else{
                        Text(q.stem,style=MaterialTheme.typography.titleMedium)
                        if(!hasSql)q.tables.forEach{StudyTable(it)}
                    }
                    item.choiceOrder.forEachIndexed{index,choiceId->
                        val choice=q.choices.first{it.id==choiceId};val selected=choiceId in item.draft
                        val correct=!unit&&submission!=null&&choiceId in q.correctChoiceIds
                        val status=when{unit&&submission!=null&&selected->"제출한 답안";correct->"정답";submission!=null&&selected->"내 답안 · 오답";selected->"선택됨";else->"선택 안 됨"}
                        Surface(shape=RoundedCornerShape(10.dp),color=if(correct)MaterialTheme.colorScheme.primaryContainer else if(selected)MaterialTheme.colorScheme.surfaceVariant else MaterialTheme.colorScheme.surface,border=BorderStroke(if(selected)2.dp else 1.dp,if(selected)MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outlineVariant),modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("session-choice-$choiceId").selectable(selected=selected,enabled=submission==null&&s.submittedAt==null,role=Role.RadioButton,onClick={ui.vm.mutate{StudyEngine.select(it,id,s.current,choiceId)}}).semantics{stateDescription=status}){
                            Row(Modifier.padding(horizontal=12.dp,vertical=10.dp),verticalAlignment=Alignment.Top,horizontalArrangement=Arrangement.spacedBy(10.dp)){
                                Text("${index+1}",style=MaterialTheme.typography.titleSmall,color=MaterialTheme.colorScheme.primary)
                                Column(Modifier.weight(1f),verticalArrangement=Arrangement.spacedBy(4.dp)){
                                    Text(choice.text,style=MaterialTheme.typography.bodyMedium)
                                    if(submission!=null&&(correct||selected))Text(status,style=MaterialTheme.typography.labelMedium,color=if(correct||unit)MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error)
                                }
                                if(selected)Icon(Icons.Outlined.CheckCircle,"선택한 보기",modifier=Modifier.size(20.dp))
                            }
                        }
                    }
                    if(submission==null){
                        TextButton(onClick={confidenceVisible=!confidenceVisible}){Text("확신도 남기기 (선택)")}
                        if(confidenceVisible)FlowButtons(listOf("sure" to "확실함","unsure" to "헷갈림","guess" to "찍음"),item.confidence,{c->ui.vm.mutate{StudyEngine.confidence(it,id,s.current,c)}})
                    }
                    TextButton(onClick={detailVisible=!detailVisible}){Text(if(detailVisible)"문제 정보·도움 접기"else"문제 정보·도움")}
                    if(detailVisible){
                        Row(verticalAlignment=Alignment.CenterVertically){
                            Text("${q.objectiveIds.joinToString()} · ${kindLabel(q)}",Modifier.weight(1f),style=MaterialTheme.typography.labelMedium)
                        }
                        if(q.dialect!="conceptual")Text("${q.dialect} ${q.dialectVersion} · ${if(q.verification=="engine_verified")"엔진 검증 기록 포함"else"문서 검토 기반"}",style=MaterialTheme.typography.bodySmall)
                        Text(when(q.sourceType){"original_practice"->"창작 연습문제";"original_mock"->"창작 모의문제";else->q.sourceType},style=MaterialTheme.typography.bodySmall)
                        Text("${q.id} · 버전 ${q.version}",style=MaterialTheme.typography.labelMedium)
                        if(submission==null)TextButton(onClick={if(s.mode=="strict")convertAction="note"else ui.note(q.explanation.relatedNoteId)}){Text("연결 개념 확인")}
                        TextButton(onClick={ui.issue(q.id)}){Text("내용 오류 표시")}
                    }
                    if(submission!=null&&unit)OutlinedButton(onClick={ui.nav("unitanswers:${s.id}")},modifier=Modifier.fillMaxWidth().testTag("unit-open-answers")){Text("별도 답지·해설 보기")}
                    if(submission!=null&&!hasSql&&!wide&&!unit)ExplanationPanel(ui,q,submission)
                    if(s.submittedAt!=null)TextButton(onClick={showResult=true}){Text("결과 요약으로")}
                }
            }
            if(solvingMaterial&&wide)Row(Modifier.fillMaxSize()){
                val materialScroll=key(q.id){rememberScrollState()}
                Column(Modifier.weight(1f).fillMaxHeight().verticalScroll(materialScroll).padding(12.dp)){UnitQuestionMaterial(ui,q)}
                VerticalDivider()
                body(Modifier.weight(1f).fillMaxHeight())
            }else if(solvingMaterial)body(Modifier.fillMaxSize())
            else if(hasSql){
                val material=walkthrough
                val selectedStep=material?.let{readerStep.coerceIn(it.steps.indices)}?:0
                val ranges=if(submission!=null&&readerMode=="walk"&&material!=null)WalkthroughRules.ranges(q.sql.orEmpty(),material.steps[selectedStep].codeFocus)else emptyList()
                SqlReadingLayout(ui,source,ranges,Modifier.fillMaxSize()){modifier->
                    if(submission==null)body(modifier)
                    else Column(modifier){
                        Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),verticalAlignment=Alignment.CenterVertically){
                            listOf("walk" to "따라 읽기","original" to "기존 해설","question" to "문제·답안").forEach{(mode,label)->
                                TextButton(onClick={readerMode=mode},modifier=Modifier.testTag("reader-mode-$mode"),colors=ButtonDefaults.textButtonColors(containerColor=if(readerMode==mode)ReadingBlue else androidx.compose.ui.graphics.Color.Transparent,contentColor=if(readerMode==mode)ReadingInk else MaterialTheme.colorScheme.primary)){Text(label,maxLines=1)}
                            }
                        }
                        if(readerMode=="question")body(Modifier.weight(1f).fillMaxWidth())
                        else if(readerMode=="walk"&&material!=null)WalkNarrative(material,selectedStep,{readerStep=it},foundations,{foundations=it},Modifier.weight(1f).fillMaxWidth()){QuestionGuideLinks(ui,q)}
                        else Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()).padding(12.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
                            if(readerMode=="walk")Text(if(walkthroughReady)"이 문제는 기존 해설로 확인해 주세요. 원문과 일치하는 단계별 검증 자료가 아직 없어요."else"단계별 해설을 여는 중이에요.",style=MaterialTheme.typography.bodySmall)
                            ExplanationPanel(ui,q,submission)
                        }
                    }
                }
            } else if(wide&&submission!=null)Row(Modifier.fillMaxSize()){
                Column(Modifier.weight(1f).fillMaxHeight().verticalScroll(rememberScrollState()).padding(12.dp)){ExplanationPanel(ui,q,submission)}
                VerticalDivider()
                body(Modifier.weight(1f).fillMaxHeight())
            } else body(Modifier.fillMaxSize())
        }
        Surface(tonalElevation=3.dp,shadowElevation=2.dp){BoxWithConstraints(Modifier.fillMaxWidth()){
            val strictSolving=s.mode=="strict"&&s.submittedAt==null
            val stackGrading=largeText||!actionRowFits(maxWidth-24.dp,listOf(gradeLabel,"모르겠어요"))
            val stackStrictActions=!actionRowFits(maxWidth-24.dp,listOf("이전","다음","전체 제출"))
            Column(Modifier.fillMaxWidth().padding(horizontal=12.dp,vertical=2.dp),verticalArrangement=Arrangement.spacedBy(2.dp)){
            if(strictSolving){
                // Strict exams keep draft selection and navigation separate from irreversible submission.
                // At narrow widths the same actions use two rows, without shrinking or clipping labels.
                if(stackStrictActions){
                    Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(8.dp),verticalAlignment=Alignment.CenterVertically){
                        TextButton(enabled=s.current>0&&!busy,onClick={ui.vm.mutate{StudyEngine.move(it,id,s.current-1)}},modifier=Modifier.weight(1f).heightIn(min=48.dp).testTag("session-previous")){Text("이전")}
                        Button(enabled=s.current<s.items.lastIndex&&!busy,onClick={ui.vm.mutate{StudyEngine.move(it,id,s.current+1)}},modifier=Modifier.weight(1f).heightIn(min=48.dp).testTag("session-next")){Text("다음")}
                    }
                    if(s.current==s.items.lastIndex)Button(enabled=!busy,onClick={confirmSubmit=true},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("session-submit")){Text("전체 제출")}
                    else OutlinedButton(enabled=!busy,onClick={confirmSubmit=true},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("session-submit")){Text("전체 제출")}
                }else Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(8.dp),verticalAlignment=Alignment.CenterVertically){
                    TextButton(enabled=s.current>0&&!busy,onClick={ui.vm.mutate{StudyEngine.move(it,id,s.current-1)}},modifier=Modifier.heightIn(min=48.dp).testTag("session-previous")){Text("이전")}
                    Spacer(Modifier.weight(1f))
                    Button(enabled=s.current<s.items.lastIndex&&!busy,onClick={ui.vm.mutate{StudyEngine.move(it,id,s.current+1)}},modifier=Modifier.heightIn(min=48.dp).testTag("session-next")){Text("다음")}
                    if(s.current==s.items.lastIndex)Button(enabled=!busy,onClick={confirmSubmit=true},modifier=Modifier.heightIn(min=48.dp).testTag("session-submit")){Text("전체 제출")}
                    else OutlinedButton(enabled=!busy,onClick={confirmSubmit=true},modifier=Modifier.heightIn(min=48.dp).testTag("session-submit")){Text("전체 제출")}
                }
            }else{
                if(submission==null && stackGrading){
                    Button(enabled=item.draft.isNotEmpty(),onClick={gradeCurrent()},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("session-grade")){Text(gradeLabel)}
                    TextButton(onClick={gradeCurrent(true)},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("session-unknown")){Text("모르겠어요")}
                }else if(submission==null)Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(8.dp)){
                    Button(enabled=item.draft.isNotEmpty(),onClick={gradeCurrent()},modifier=Modifier.weight(1f).heightIn(min=48.dp).testTag("session-grade")){Text(gradeLabel)}
                    OutlinedButton(onClick={gradeCurrent(true)},modifier=Modifier.heightIn(min=48.dp).testTag("session-unknown")){Text("모르겠어요")}
                }
                FlowRow(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(8.dp,Alignment.End),verticalArrangement=Arrangement.spacedBy(8.dp)){
                    TextButton(enabled=s.current>0,onClick={ui.vm.mutate{StudyEngine.move(it,id,s.current-1)}},modifier=Modifier.heightIn(min=48.dp).testTag("session-previous")){Text("이전")}
                    TextButton(enabled=s.current<s.items.lastIndex,onClick={ui.vm.mutate{StudyEngine.move(it,id,s.current+1)}},modifier=Modifier.heightIn(min=48.dp).testTag("session-next")){Text("다음")}
                    if(s.submittedAt==null)TextButton(onClick={confirmSubmit=true},modifier=Modifier.heightIn(min=48.dp).testTag("session-submit")){Text("전체 제출")}
                    else TextButton(onClick={ui.practice(listOf(q),"다시 풀기 · 새 시도")}){Text("다시 풀기")}
                }
            }
        }}}
    }
    if(confirmSubmit)AlertDialog(onDismissRequest={confirmSubmit=false},title={Text("전체 답안을 제출할까요?")},text={DialogBody("아직 미응답 ${s.items.count{it.draft.isEmpty()&&it.submissionId==null}}문항\n이미 채점 ${s.items.count{it.submissionId!=null}}문항\n\n미응답은 0점으로 기록합니다. 이미 채점한 문제는 다시 기록하지 않습니다.")},confirmButton={Button(onClick={ui.vm.submit(id);confirmSubmit=false}){Text("전체 제출 확정")}},dismissButton={TextButton(onClick={confirmSubmit=false}){Text("계속 풀기")}})
    convertAction?.let{action->AlertDialog(onDismissRequest={if(!busy)convertAction=null},title={Text("연습 모드로 전환할까요?")},text={DialogBody("기존 답안과 진행은 보존됩니다. 도움을 요청한 이 세션은 최초 실전 진단에서 영구 제외되고, 연습 모드로 기록됩니다.")},confirmButton={TextButton(enabled=!busy,onClick={ui.vm.launchWork{
        ui.vm.repository.update{s0->val s1=StudyEngine.convert(s0,id,System.currentTimeMillis());if(action=="note")StudyEngine.help(s1,id,s.current,"note",System.currentTimeMillis())else StudyEngine.grade(s1,id,s.current,System.currentTimeMillis(),action=="unknown")}
        convertAction=null
        if(action=="note")ui.nav("note:${q.explanation.relatedNoteId}")
    }}){Text("연습으로 전환")}},dismissButton={TextButton(enabled=!busy,onClick={convertAction=null}){Text("실전 유지")}})}
    if(grid)AlertDialog(onDismissRequest={grid=false},title={Text("문제 이동표")},text={Column(Modifier.verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(12.dp)){Text("✓ 채점 · ● 답안 선택 · ○ 미응답",style=MaterialTheme.typography.bodySmall);FlowRow(horizontalArrangement=Arrangement.spacedBy(6.dp),verticalArrangement=Arrangement.spacedBy(6.dp)){s.items.forEachIndexed{i,it->OutlinedButton(onClick={ui.vm.mutate{StudyEngine.move(it,id,i)};grid=false}){Text("${i+1} ${if(it.submissionId!=null)"✓"else if(it.draft.isNotEmpty())"●"else"○"}")}}}}},confirmButton={TextButton(onClick={grid=false}){Text("닫기")}})
}

@Composable fun ExplanationPanel(ui:StudyUi,q:Question,r:Submission){
    var step by rememberSaveable(q.id){mutableIntStateOf(0)};var all by rememberSaveable(q.id){mutableStateOf(false)}
    val expanded=ui.state.settings.explanationExpanded
    val terms=remember(q,ui.pack.objectives){q.explanation.prerequisites+ui.pack.objectives.filter{it.id in q.objectiveIds}.flatMap{listOf(it.title)+it.synonyms}}
    val columns=remember(q.tables){q.tables.flatMap{it.columns}.distinct()}
    Column(verticalArrangement=Arrangement.spacedBy(16.dp)){
        Eyebrow(when(r.outcome){"correct"->"✓ 정답이에요";"unanswered"->"○ 미응답으로 기록했어요";else->"다시 확인할 개념이에요"})
        StudyBodyText(q.explanation.summary,emphasis=terms,inlineCodes=columns)
        val current=ui.pack.questions.find{it.id==q.id&&it.version>q.version}
        if(current!=null)Paper{
            Eyebrow("콘텐츠 정정 안내 · 과거 판정 보존")
            Text("이 시도는 v${q.version} 기준 ${when(r.outcome){"correct"->"정답";"wrong"->"오답";else->"미응답"}}입니다. 현재 문항은 v${current.version}입니다.")
            val reason=ui.pack.corrections.lastOrNull{it.questionId==q.id}?.reason?:"변경 사유는 현재 콘텐츠 검수 보고서에서 확인하세요."
            StudyBodyText(reason)
            val comparable=q.stem==current.stem && q.sql==current.sql && q.tables==current.tables && q.familyId==current.familyId && q.choices.associate{it.id to it.text}==current.choices.associate{it.id to it.text}
            Text(if(!comparable)"문제 조건이나 보기가 변경되어 과거 답안을 자동 재판정할 수 없습니다."else"현재 정답 기준 참고: ${if(r.choiceIds.isEmpty())"미응답"else if(r.choiceIds.toSet()==current.correctChoiceIds.toSet())"정답"else"오답"}. 이전 점수·오답 이력은 바꾸지 않았습니다.",style=MaterialTheme.typography.bodySmall)
        }
        TextButton(onClick={ui.vm.settings{it.copy(explanationExpanded=!expanded)}}){Text(if(expanded)"자세한 해설 접기"else"자세한 해설 펼치기")}
        if(expanded){
            if(q.explanation.prerequisites.isNotEmpty())StudyBodyText("필요한 개념 · ${q.explanation.prerequisites.joinToString(" / ")}",emphasis=terms)
            if(q.explanation.conditions.isNotEmpty())StudyPaper{StudySection("먼저 볼 조건"){q.explanation.conditions.forEach{StudyBodyText("• $it",emphasis=terms,inlineCodes=columns)}}}
            if(q.explanation.steps.isNotEmpty()){
                StudySection("해설 단계"){
                    StudyBodyText("검토한 교육용 단계 자료입니다. 실제 DB 실행 추적 화면이 아닙니다.",style=MaterialTheme.typography.bodyMedium)
                }
                val steps=q.explanation.steps
                (if(all)steps else listOf(steps[step.coerceAtMost(steps.lastIndex)])).forEach{item->StudyPaper{
                    StudySection(item.title){
                        StudyBodyText(item.text,emphasis=terms,inlineCodes=columns)
                        item.table?.let{table->StudyTable(table)}
                    }
                }}
                @OptIn(ExperimentalLayoutApi::class)
                FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(8.dp)){TextButton(enabled=step>0&&!all,onClick={step--}){Text("이전 단계")};TextButton(enabled=step<steps.lastIndex&&!all,onClick={step++}){Text("다음 단계")};TextButton(onClick={step=0;all=false}){Text("처음으로")};TextButton(onClick={all=!all}){Text(if(all)"한 단계씩"else"전체 보기")}}
            }
            Text("보기별로 확인하기",style=MaterialTheme.typography.titleLarge)
            r.choiceOrder.forEachIndexed{i,cid->val c=q.choices.first{it.id==cid};Column(verticalArrangement=Arrangement.spacedBy(8.dp)){Text("${i+1}. ${if(cid in q.correctChoiceIds)"정답"else"오답"} · ${c.text}",style=MaterialTheme.typography.titleSmall);StudyBodyText(c.reason,emphasis=terms,inlineCodes=columns)}}
            if(r.outcome=="wrong")StudyBodyText("선택한 보기와 연결된 조건을 혼동했을 가능성이 있습니다. 위 근거와 지문의 조건을 나란히 확인해 보세요.")
            StudyPaper(accent=true){StudySection("기억할 한 문장"){StudyBodyText(q.explanation.memory,emphasis=terms,inlineCodes=columns)}}
            Text("근거 ${q.sourceIds.joinToString()}\n${q.validationEvidence.joinToString("\n")}",style=MaterialTheme.typography.bodySmall)
        }
        OutlinedButton(onClick={ui.note(q.explanation.relatedNoteId)},modifier=Modifier.fillMaxWidth()){Text("연결 개념 노트")}
        QuestionGuideLinks(ui,q)
        val next=StudyEngine.available(ui.pack,ui.state).filter{it.id!=q.id&&it.familyId!=q.familyId&&it.objectiveIds.any{obj->obj in q.objectiveIds}}
        if(next.isNotEmpty())TextButton(onClick={ui.practice(next.take(3),"새로운 확인 문제")}){Text("다른 상황에 적용해 보기")}
    }
}

@Composable fun ResultScreen(ui:StudyUi,s:QuizSession,review:()->Unit){
    val unit=s.items.all{it.question.isUnitQuestion()}
    val score=StudyEngine.score(s,ui.state)
    val records=ui.state.submissions.filter{it.sessionId==s.id}
    val wrong=s.items.map{it.question}.filter{q->records.any{it.questionId==q.id&&it.outcome!="correct"}}
    val unsure=s.items.map{it.question}.filter{q->records.any{it.questionId==q.id&&it.confidence in listOf("unsure","guess")}}
    val stars=s.items.map{it.question}.filter{q->ui.state.bookmarks.any{it.id==q.id}}
    val weak=wrong.flatMap{it.objectiveIds}.groupingBy{it}.eachCount().toList().sortedByDescending{it.second}
    LazyColumn(Modifier.fillMaxSize().testTag("session-result"),contentPadding=PaddingValues(20.dp),verticalArrangement=Arrangement.spacedBy(24.dp)){
        item{PageTitle("학습을 마쳤어요",if(s.mockSetId!=null)"${score.points}점"else"${records.count{it.outcome=="correct"}} / ${s.items.size}문항 정답",s.title)}
        item{Paper(accent=true){
            if(s.mockSetId!=null&&!unit){Text(if(score.passed)"설정된 합격 기준 충족"else"설정된 합격 기준 미달",style=MaterialTheme.typography.titleLarge);Text("${if(score.modelFail)"1과목 과락 · "else""}${if(score.sqlFail)"2과목 과락 · "else""}${if(score.points<s.examSpec.passPoints)"총점 미달"else""}");Text("공식 최신 기준 원문은 미확인입니다. 앱 내부 문제의 결과이며 합격 확률이 아닙니다.",style=MaterialTheme.typography.bodySmall)}
            if(unit)Text("이 단원 정답 ${score.modelCorrect+score.sqlCorrect} / ${s.items.size} · 미응답 ${score.unanswered}\nSQLD 전체 시험의 합격 판정과 구분하는 단원 연습 결과예요.")
            else Text("1과목 ${score.modelCorrect} / ${score.modelTotal} (${if(score.modelTotal==0)"—"else"${score.modelCorrect*100/score.modelTotal}%"})\n2과목 ${score.sqlCorrect} / ${score.sqlTotal} (${if(score.sqlTotal==0)"—"else"${score.sqlCorrect*100/score.sqlTotal}%"})\n미응답 ${score.unanswered}문항")
            Text("활성 풀이 ${s.elapsedMillis/60000}분 ${s.elapsedMillis/1000%60}초 · ${dateText(s.submittedAt!!)}",style=MaterialTheme.typography.bodySmall)
            if(s.mockSetId!=null)Text(when{ s.repeat->"재응시 · 반복 풀이 기록"; s.convertedAt!=null->"도움 요청으로 연습 전환 · 최초 실전 지표 제외";unit->"단원 학습용 모의 기록"; !s.diagnosticEligible->"이전 노출 또는 시간 이상 · 최초 실전 지표 제외";else->"새 모의고사 첫 제출 · 무도움 실전 기록"},style=MaterialTheme.typography.titleSmall)
        }}
        item{Text("제출을 구분한 기록",style=MaterialTheme.typography.titleLarge);Text("새 문제·무도움 ${records.count{it.firstEver&&!it.helped}}회\n반복·무도움 ${records.count{!it.firstEver&&!it.helped}}회\n도움 사용 ${records.count{it.helped}}회\n${if(records.size<20)"판단 자료 부족 · 더 다양한 문제의 첫 답안이 필요해요"else"개념의 숙달을 확정하는 지표는 아니에요"}",style=MaterialTheme.typography.bodyMedium)}
        item{Button(onClick={if(unit)ui.nav("unitanswers:${s.id}")else review()},modifier=Modifier.fillMaxWidth()){Text(if(unit)"별도 답지·해설 보기"else"모든 문제와 해설 보기")}}
        item{Text("다음에 볼 페이지",style=MaterialTheme.typography.titleLarge);if(weak.isEmpty())Text("이번에 틀린 문제는 없어요. 다른 상황의 문제로 적용 범위를 넓혀 보세요.");weak.take(5).forEach{(obj,count)->ui.pack.notes.find{it.objectiveId==obj}?.let{n->NoteRow(obj,n.title,"이번 세션 오답·미응답 ${count}문항",{ui.note(n.id)})}}}
        item{@OptIn(ExperimentalLayoutApi::class) FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp)){OutlinedButton(onClick={ui.practice(wrong,"오답 다시 풀기")},enabled=wrong.isNotEmpty()){Text("오답 ${wrong.size}")};OutlinedButton(onClick={ui.practice(unsure,"헷갈린 문제 다시 풀기")},enabled=unsure.isNotEmpty()){Text("헷갈림 ${unsure.size}")};OutlinedButton(onClick={ui.practice(stars,"별표 문제 다시 풀기")},enabled=stars.isNotEmpty()){Text("별표 ${stars.size}")}}}
        items(s.items,key={it.question.id}){item->val q=item.question;NoteRow(q.objectiveIds.first(),q.title,when(records.find{it.questionId==q.id}?.outcome){"correct"->"정답";"wrong"->"오답";else->"미응답"},{ui.vm.mutate{StudyEngine.move(it,s.id,s.items.indexOf(item))};review()},{StarButton(q.id,ui.state.bookmarks.any{it.id==q.id},{ui.vm.star(q.id)})})}
    }
}
