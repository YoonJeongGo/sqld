package kr.sqld.study

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ChevronRight
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.dp

private fun unitTypeLabel(type:String)=when(type){
    "concept","recall"->"개념 회상"
    "discriminate"->"조건 구분"
    "apply"->"상황 적용"
    "case"->"사례 판단"
    "review"->"개념 복습"
    else->type
}

@Composable fun UnitPracticeScreen(ui:StudyUi,partId:String="",initialLesson:String=""){
    val bank=ui.vm.repository.unitBank
    val part=bank.parts.find{it.id==partId}
    var selectedLesson by rememberSaveable(partId,initialLesson){mutableStateOf(initialLesson)}
    var selectedType by rememberSaveable(partId){mutableStateOf("all")}
    var filters by rememberSaveable(partId){mutableStateOf(false)}
    val busy by ui.vm.busy.collectAsState()
    val linked=remember(bank){bank.links.associateBy{it.questionId}}
    LazyColumn(Modifier.fillMaxSize().testTag("unit-practice"),contentPadding=PaddingValues(16.dp),verticalArrangement=Arrangement.spacedBy(16.dp)){
        item{PageTitle("단원별 복습",part?.let{"${it.id} ${it.title}"}?:"복습할 단원 선택")}
        if(part==null){
            item{StudyBodyText("필요한 강의와 문제 유형을 골라 복습해요.")}
            items(bank.parts,key={it.id}){p->UnitPartRow(p,"유형별 복습 ${p.reviewIds.size}문항",Modifier.testTag("unit-open-${p.id}")){ui.nav("unit:${p.id}")}}
        }else{
            val lessons=ui.course.lessons.filter{it.partId==part.id}
            val types=part.reviewIds.mapNotNull{linked[it]?.type}.distinct()
            val review=bank.questions(part.reviewIds,ui.state).filter{q->val link=linked[q.id];(selectedLesson.isBlank()||link?.lessonId==selectedLesson)&&(selectedType=="all"||link?.type==selectedType)}
            item{StudySection("강의별·유형별 복습"){
                TextButton(onClick={filters=!filters}){Text(if(filters)"복습 범위 접기"else"강의·유형 고르기")}
                if(filters){
                    FlowButtons(listOf("" to "단원 전체")+lessons.map{it.id to "${it.number}. ${it.title}"},selectedLesson,{selectedLesson=it})
                    FlowButtons(listOf("all" to "모든 유형")+types.map{it to unitTypeLabel(it)},selectedType,{selectedType=it})
                }
                val label=lessons.find{it.id==selectedLesson}?.let{"${it.number}. ${it.title}"}?:"단원 전체"
                Text("$label · ${if(selectedType=="all")"모든 유형"else unitTypeLabel(selectedType)} · ${review.size}문항")
                Button(enabled=review.isNotEmpty()&&!busy,onClick={ui.practice(review,"${part.id} 유형별 복습")},modifier=Modifier.fillMaxWidth().testTag("unit-review-start")){Text("선택한 범위 복습 시작")}
            }}
            item{TextButton(onClick={ui.nav("unit")}){Text("다른 단원 복습")}}
        }
    }
}

/** Unit mocks have their own entry: choose a part, choose a form, then solve. */
@Composable fun UnitMockScreen(ui:StudyUi,partId:String=""){
    val bank=ui.vm.repository.unitBank
    val part=bank.parts.find{it.id==partId}
    var selectedForm by remember(partId){mutableStateOf<UnitMockForm?>(null)}
    val busy by ui.vm.busy.collectAsState()
    LazyColumn(Modifier.fillMaxSize().testTag(if(part==null)"unit-mock-parts"else"unit-mock-forms"),
        contentPadding=PaddingValues(16.dp),verticalArrangement=Arrangement.spacedBy(8.dp)){
        if(part==null){
            item{PageTitle("","단원 모의고사","단원 선택 → 회차 선택 → 문제 풀기")}
            items(bank.parts,key={it.id}){p->UnitPartRow(p,"50문항 · 90분 · 3회",Modifier.testTag("mock-unit-${p.id}")){ui.nav("mock:${p.id}")}}
            item{TextButton(onClick={ui.nav("fullmock")},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp)){Text("SQLD 전체 범위 모의고사")}}
        }else{
            item{PageTitle("단원 모의고사","${part.id} ${part.title}","이 단원의 문제만 나와요. 풀 회차를 선택해 주세요.")}
            items(part.forms,key={it.id}){form->
                val complete=bank.questions(form.questionIds,ui.state).size==50
                val sessions=ui.state.sessions.filter{it.mockSetId==form.id}
                val active=sessions.lastOrNull{it.submittedAt==null}
                val finished=sessions.lastOrNull{it.submittedAt!=null}
                val startLabel=if(active!=null)"이어서 풀기"else if(sessions.isEmpty())"${form.number}회 시작"else"다시 응시"
                val status=if(active!=null)"풀이 중"else if(sessions.isEmpty())"미응시"else"응시 이력 ${sessions.size}회"
                Surface(modifier=Modifier.fillMaxWidth(),shape=MaterialTheme.shapes.medium,border=BorderStroke(1.dp,MaterialTheme.colorScheme.outlineVariant)){
                    Column(Modifier.padding(12.dp),verticalArrangement=Arrangement.spacedBy(8.dp)){
                        val start:@Composable ()->Unit={Button(enabled=(active!=null||complete)&&!busy,
                            onClick={if(active!=null)ui.nav("session:${active.id}")else selectedForm=form},
                            modifier=Modifier.heightIn(min=48.dp).testTag("unit-mock-${form.number}")){Text(startLabel)}}
                        val label:@Composable ()->Unit={Column(verticalArrangement=Arrangement.spacedBy(4.dp)){
                            Text("${form.number}회",style=MaterialTheme.typography.titleLarge)
                            Text("50문항 · 90분 · $status",style=MaterialTheme.typography.bodyMedium)
                        }}
                        BoxWithConstraints(Modifier.fillMaxWidth()){
                            if(maxWidth>=480.dp)Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(12.dp),verticalAlignment=Alignment.CenterVertically){
                                Box(Modifier.weight(1f)){label()};start()
                            }else Column(Modifier.fillMaxWidth(),verticalArrangement=Arrangement.spacedBy(8.dp)){label();start()}
                        }
                        if(!complete)Text("오류 표시로 제외한 문항이 있어 50문항 구성을 유지할 수 없어요.",color=MaterialTheme.colorScheme.error)
                        if(finished!=null)TextButton(onClick={ui.nav("unitanswers:${finished.id}")},modifier=Modifier.align(Alignment.End).heightIn(min=48.dp)){Text("제출한 답지·해설 보기")}
                    }
                }
            }
            item{TextButton(onClick={ui.nav("mock")},modifier=Modifier.heightIn(min=48.dp)){Text("다른 단원 선택")}}
            item{StudyBodyText("SQLD 수준을 목표로 만든 창작 문제예요. 실제 시험과 난이도가 같다고 검증된 자료는 아니에요.")}
        }
    }
    selectedForm?.let{form->
        val ongoing=ui.state.sessions.firstOrNull{it.mode=="strict"&&it.submittedAt==null}
        AlertDialog(onDismissRequest={selectedForm=null},title={Text(if(ongoing!=null)"진행 중인 시험 이어 풀기"else"${part!!.id} 단원 모의 ${form.number}회")},text={DialogBody(if(ongoing!=null)"이미 진행 중인 시험이 있어요. ${ongoing.title}로 돌아갑니다. 제출한 뒤 새 모의고사를 시작할 수 있어요."else"50문항·90분입니다. 전체 제출 전에는 정답·해설을 공개하지 않아요. 화면을 꺼도 시간이 흐르며, 만료 시 미응답을 포함해 자동 제출합니다. 기존 SQLD 전체 모의고사와 별도로 기록합니다.")},confirmButton={Button(enabled=!busy,onClick={ui.vm.startUnit(partId,form.number){ui.nav("session:$it")};selectedForm=null},modifier=Modifier.testTag("unit-mock-confirm")){Text(if(ongoing!=null)"이어서 풀기"else"시간 시작하고 응시")}},dismissButton={TextButton(onClick={selectedForm=null}){Text("돌아가기")}})
    }
}

@Composable private fun UnitPartRow(part:UnitPracticePart,description:String,modifier:Modifier=Modifier,onClick:()->Unit){
    Surface(onClick=onClick,modifier=modifier.fillMaxWidth().heightIn(min=72.dp),shape=MaterialTheme.shapes.medium,
        border=BorderStroke(1.dp,MaterialTheme.colorScheme.outlineVariant)){
        Row(Modifier.padding(horizontal=16.dp,vertical=10.dp),horizontalArrangement=Arrangement.spacedBy(12.dp),verticalAlignment=Alignment.CenterVertically){
            Column(Modifier.weight(1f),verticalArrangement=Arrangement.spacedBy(4.dp)){
                Text("${part.id} ${part.title}",style=MaterialTheme.typography.titleMedium)
                Text(description,style=MaterialTheme.typography.bodyMedium)
            }
            Icon(Icons.Outlined.ChevronRight,null,tint=MaterialTheme.colorScheme.primary)
        }
    }
}

/** Only immutable submissions unlock this separate answer screen; a route alone cannot reveal answers. */
@Composable fun UnitAnswersScreen(ui:StudyUi,sessionId:String){
    val session=ui.state.sessions.find{it.id==sessionId}?:return
    if(session.items.none{it.question.isUnitQuestion()}){Text("단원 문제의 답지가 아니에요.");return}
    val records=ui.state.submissions.filter{it.sessionId==sessionId}.associateBy{it.questionId}
    val visible=session.items.indices.filter{session.items[it].question.id in records}
    if(visible.isEmpty()||(session.mode=="strict"&&session.submittedAt==null)){
        Column(Modifier.padding(16.dp)){Text("풀이를 제출한 뒤 답지·해설을 확인할 수 있어요.");Button(onClick={ui.nav("session:$sessionId")}){Text("문제로 돌아가기")}}
        return
    }
    var index by rememberSaveable(sessionId){mutableIntStateOf(session.current.takeIf{it in visible}?:visible.first())}
    var details by rememberSaveable(sessionId){mutableStateOf(false)}
    val item=session.items[index];val q=item.question;val submission=records.getValue(q.id)
    val correct=item.choiceOrder.indexOf(q.correctChoiceIds.single())+1
    val chosen=item.draft.firstOrNull()?.let{item.choiceOrder.indexOf(it)+1}
    LazyColumn(Modifier.fillMaxSize().testTag("unit-answers"),contentPadding=PaddingValues(16.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
        item{PageTitle("답지·해설",session.title,"제출한 보기 순서를 기준으로 정답 번호를 표시해요.")}
        item{FlowButtons(listOf("key" to "빠른 답지","detail" to "상세 해설"),if(details)"detail"else"key",{details=it=="detail"})}
        if(!details){
            items(visible,key={it}){at->val saved=session.items[at];val r=records.getValue(saved.question.id);val n=saved.choiceOrder.indexOf(saved.question.correctChoiceIds.single())+1
                OutlinedButton(onClick={index=at;details=true},modifier=Modifier.fillMaxWidth().testTag("unit-answer-${at+1}")){Text("${at+1}번 · 정답 $n · ${when(r.outcome){"correct"->"맞음";"wrong"->"틀림";else->"미응답"}}",Modifier.weight(1f));Text("해설")}
            }
        }else{
            item{Text("${index+1}번 · 정답 $correct · 내 답 ${chosen?.toString()?:"미응답"}",style=MaterialTheme.typography.titleLarge);Text(q.stem,style=MaterialTheme.typography.bodyLarge)}
            if(!q.sql.isNullOrBlank())item{UnitSqlText(q.sql.orEmpty())}
            items(q.tables){StudyTable(it)}
            item{UnitExplanation(ui,q,submission)}
            item{Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(8.dp)){
                OutlinedButton(enabled=visible.any{it<index},onClick={index=visible.last{it<index}}){Text("이전 해설")}
                OutlinedButton(enabled=visible.any{it>index},onClick={index=visible.first{it>index}}){Text("다음 해설")}
            }}
        }
        item{Button(onClick={ui.vm.launchWork{ui.vm.repository.update{StudyEngine.move(it,sessionId,index)};ui.nav("session:$sessionId:review")}},modifier=Modifier.fillMaxWidth().testTag("unit-return-question")){Text("풀이 화면으로 돌아가기")}}
    }
}

@Composable private fun UnitExplanation(ui:StudyUi,q:Question,submission:Submission){
    Column(verticalArrangement=Arrangement.spacedBy(12.dp)){
        Text(when(submission.outcome){"correct"->"맞힌 근거 확인";"wrong"->"오답의 판단 기준";else->"미응답 문제의 풀이"},style=MaterialTheme.typography.titleLarge)
        val terms=remember(q){Regex("[A-Z][A-Z_]+(?:\\(\\*\\))?").findAll(q.sql.orEmpty()+" "+q.explanation.summary).map{it.value}.distinct().toList()}
        StudyBodyText(q.explanation.summary,emphasis=terms)
        q.explanation.steps.filter{it.table!=null||!q.explanation.summary.contains(it.text)}.distinctBy{it.text}.forEach{step->StudySection(step.title){StudyBodyText(step.text,emphasis=terms);step.table?.let{StudyTable(it)}}}
        Text("보기와 내 답안",style=MaterialTheme.typography.titleMedium)
        val item=ui.state.sessions.first{it.id==submission.sessionId}.items.first{it.question.id==q.id}
        item.choiceOrder.forEachIndexed{at,id->val choice=q.choices.first{it.id==id}
            Text("${at+1}. ${choice.text}${if(id in q.correctChoiceIds)" · 정답"else""}${if(id in submission.choiceIds)" · 내 답"else""}",style=MaterialTheme.typography.bodyLarge)
        }
        if(q.explanation.memory!="조건과 실제 값을 먼저 대조하고 결과를 판단한다.")StudyWarning(q.explanation.memory)
        OutlinedButton(onClick={ui.note(q.explanation.relatedNoteId)},modifier=Modifier.fillMaxWidth()){Text("연결 개념 노트로 복습")}
        TextButton(onClick={ui.issue(q.id)}){Text("내용 오류 표시")}
    }
}

@Composable internal fun UnitSqlText(sql:String){
    Surface(color=MaterialTheme.colorScheme.surfaceVariant,shape=MaterialTheme.shapes.small){
        Text(sql,Modifier.fillMaxWidth().padding(12.dp).horizontalScroll(rememberScrollState()),style=MaterialTheme.typography.bodyMedium,fontFamily=androidx.compose.ui.text.font.FontFamily.Monospace,softWrap=false)
    }
}

@Composable internal fun UnitQuestionMaterial(ui:StudyUi,q:Question){
    var pen by rememberSaveable(q.id){mutableStateOf(false)}
    Column(Modifier.fillMaxWidth().testTag("unit-question-material"),verticalArrangement=Arrangement.spacedBy(8.dp)){
        if(q.dialect!="conceptual")Text("문법 기준 · ${q.dialect} ${q.dialectVersion}",style=MaterialTheme.typography.labelMedium)
        Text(q.stem,style=MaterialTheme.typography.titleMedium)
        if(!q.sql.isNullOrBlank()){
            TextButton(onClick={pen=!pen}){Text(if(pen)"코드 읽기 보기"else"코드에 펜으로 필기")}
            if(pen)BoundInkSql(ui,WalkSource.from(q),emptyList(),Modifier.fillMaxWidth().height(320.dp))else UnitSqlText(q.sql.orEmpty())
        }
        ProblemTables(q.tables)
    }
}

/** Small source tables stay open beside their question; cells wrap without changing their values. */
@OptIn(ExperimentalLayoutApi::class)
@Composable internal fun ProblemTables(tables:List<DataTable>){
    if(tables.isEmpty())return
    BoxWithConstraints(Modifier.fillMaxWidth()){
        // Leave 2dp for rounding when the parent has an odd physical-pixel width.
        val tableWidth=(maxWidth-10.dp)/2
        val paired=tables.size>1&&maxWidth>=400.dp&&tables.all{56.dp*it.columns.size<=tableWidth}
        if(paired)FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(10.dp),maxItemsInEachRow=2){
            tables.forEach{ProblemTable(it,Modifier.width(tableWidth))}
        }else Column(verticalArrangement=Arrangement.spacedBy(10.dp)){tables.forEach{ProblemTable(it)}}
    }
}

@Composable internal fun ProblemTable(table:DataTable,modifier:Modifier=Modifier){
    val measurer=rememberTextMeasurer();val density=LocalDensity.current
    val style=MaterialTheme.typography.bodyMedium
    val headerStyle=MaterialTheme.typography.labelLarge
    Column(modifier.fillMaxWidth().testTag("problem-table"),verticalArrangement=Arrangement.spacedBy(4.dp)){
        Text(table.title,style=MaterialTheme.typography.titleSmall)
        BoxWithConstraints(Modifier.fillMaxWidth()){
            val natural=remember(table,style,headerStyle,density){table.columns.indices.map{column->
                val header=measurer.measure(table.columns[column],headerStyle,softWrap=false).size.width
                val value=table.rows.maxOfOrNull{row->measurer.measure(row[column]?:"NULL ∅",style,softWrap=false).size.width}?:0
                (with(density){maxOf(header,value).toDp()}+16.dp).coerceIn(56.dp,240.dp)
            }}
            val total=natural.fold(0.dp){a,b->a+b}
            val fits=maxWidth>=56.dp*table.columns.size
            val available=maxWidth
            val spare=available-56.dp*table.columns.size
            val widths=if(fits)natural.map{width->56.dp+spare*(width/total)}else natural
            val content:@Composable ()->Unit={
                Column(Modifier.border(1.dp,MaterialTheme.colorScheme.outlineVariant)){
                    Row(Modifier.background(MaterialTheme.colorScheme.surfaceVariant)){
                        table.columns.forEachIndexed{at,value->Text(value,Modifier.width(widths[at]).padding(horizontal=6.dp,vertical=6.dp),style=headerStyle)}
                    }
                    table.rows.forEachIndexed{rowAt,row->
                        Row(Modifier.background(if(rowAt%2==0)MaterialTheme.colorScheme.surface else MaterialTheme.colorScheme.surfaceVariant.copy(alpha=.35f))){
                            row.forEachIndexed{at,value->Text(value?:"NULL ∅",Modifier.width(widths[at]).padding(horizontal=6.dp,vertical=6.dp),style=style)}
                        }
                    }
                }
            }
            if(fits)content()else Column(Modifier.horizontalScroll(rememberScrollState())){content()}
        }
    }
}
