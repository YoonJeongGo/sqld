package kr.sqld.study

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.debounce
import kotlinx.coroutines.FlowPreview
import java.time.LocalDate

@Composable fun HomeScreen(ui:StudyUi){
    val state=ui.state
    val colors=MaterialTheme.colorScheme
    val questions=remember(ui.pack,state.issues,state.exposures){StudyEngine.available(ui.pack,state)}
    val dueIds=state.reviews.filter{it.dueAt<=System.currentTimeMillis()||it.needsReview}.map{it.questionId}.toSet()
    val due=questions.filter{it.id in dueIds}
    val active=state.sessions.firstOrNull{it.mode=="strict"&&it.submittedAt==null}
        ?:state.sessions.find{it.id==state.activeSessionId&&it.submittedAt==null}
    val strict=active?.mode=="strict"
    var tools by rememberSaveable{mutableStateOf(false)}
    BoxWithConstraints(Modifier.fillMaxSize()){
        val wide=maxWidth>=900.dp&&LocalDensity.current.fontScale*state.settings.textScale<1.4f
        LazyColumn(Modifier.fillMaxSize().testTag(if(wide)"home-wide"else"home-compact"),
            contentPadding=PaddingValues(if(wide)24.dp else 16.dp),verticalArrangement=Arrangement.spacedBy(16.dp)){
            item{PageTitle("","내 공부","진도 순서대로 읽고, 확인한 뒤 다음 강의로 넘어가요.")}
            if(strict&&active!=null)item{HomeSessionCard(ui,active)}
            item{CourseHomeCard(ui)}
            if(!strict&&active!=null)item{HomeSessionCard(ui,active)}
            item{Paper(modifier=Modifier.testTag("home-review-card")){
                Text("배운 내용 복습",style=MaterialTheme.typography.titleMedium)
                Text(if(due.isEmpty())"진도를 공부한 뒤 헷갈린 문제를 여기서 다시 풀어요."else"다시 볼 문제 ${due.size}개 · 오늘 ${minOf(due.size,state.settings.dailyCount)}개",style=MaterialTheme.typography.bodyMedium)
                OutlinedButton(onClick={if(due.isEmpty())ui.nav("review")else ui.practice(due.take(state.settings.dailyCount),"오늘의 복습")},modifier=Modifier.fillMaxWidth()){
                    Text(if(due.isEmpty())"복습 목록 보기"else"짧게 복습하기")
                }
            }}
            item{TextButton(onClick={tools=!tools},modifier=Modifier.fillMaxWidth().testTag("home-tools-toggle").semantics{stateDescription=if(tools)"펼쳐짐"else"접힘"}){
                Text(if(tools)"학습 도구 접기"else"학습 도구 더보기",Modifier.weight(1f))
                Icon(if(tools)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,null)
            }}
            if(tools){
                item{Paper{
                    Text("찾아서 공부하기",style=MaterialTheme.typography.titleMedium)
                    Text("진도와 별도로 필요한 내용을 찾을 때 사용해요.",style=MaterialTheme.typography.bodySmall,color=colors.onSurfaceVariant)
                    OutlinedButton(onClick={ui.nav("notes")},modifier=Modifier.fillMaxWidth()){Text("전체 개념 노트")}
                    ui.pack.notes.find{it.id==state.lastNoteId}?.let{last->
                        Text("최근 개념 · ${last.title}",style=MaterialTheme.typography.bodySmall)
                        TextButton(onClick={ui.note(last.id)},modifier=Modifier.fillMaxWidth()){Text("노트 펼치기")}
                    }?:TextButton(onClick={ui.note(ui.pack.notes.first().id)},modifier=Modifier.fillMaxWidth()){Text("노트 펼치기")}
                    TextButton(onClick={ui.nav("unit")},modifier=Modifier.fillMaxWidth()){Text("단원별 복습 문제")}
                }}
                item{PlanHomeCard(ui)}
                item{CoreProgressCard(ui)}
                item{Paper(modifier=Modifier.testTag("home-goal-card")){
                    Text("하루 ${state.settings.dailyCount}문항",style=MaterialTheme.typography.titleMedium)
                    if(state.settings.targetDate.isNotBlank())Text("목표일 ${state.settings.targetDate}")
                    TextButton(onClick={ui.nav("settings")}){Text("학습량·목표일 조정")}
                    TextButton(onClick={ui.nav("history")},modifier=Modifier.fillMaxWidth()){Text("학습 기록 살펴보기")}
                    Text("개념 노트·문제풀이 기록은 강의 진도와 별도로 보존돼요.",style=MaterialTheme.typography.bodySmall,color=colors.onSurfaceVariant)
                }}
            }
        }
    }
}

@Composable private fun HomeSessionCard(ui:StudyUi,session:QuizSession){
    Paper(modifier=Modifier.testTag("home-resume-card"),accent=session.mode=="strict"){
        Eyebrow(if(session.mode=="strict")"시험 진행 중"else"풀던 문제")
        Text(session.title,style=MaterialTheme.typography.titleMedium)
        Text("${session.current+1} / ${session.items.size}문항 · 선택한 답안은 저장되어 있어요.",style=MaterialTheme.typography.bodyMedium)
        if(session.mode=="strict")Text("시험은 시간이 계속 흐르고 있어요. 먼저 이어서 풀어 주세요.",style=MaterialTheme.typography.bodySmall)
        OutlinedButton(onClick={ui.nav("session:${session.id}")},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp)){Text("풀던 문제 이어서")}
    }
}

@Composable private fun CourseHomeCard(ui:StudyUi){
    val course=ui.course
    val saved=ui.state.courseProgress.associateBy{it.lessonId}
    val read=course.lessons.count{(saved[it.id]?.readVersion?:0)>=it.version}
    val resume=CourseJourney.resume(course,ui.state)
    val current=resume?:course.lessons.last()
    val position=course.lessons.indexOf(current)+1
    val progress=CourseStudy.progress(ui.state,current.id)
    val section=when(progress.section){"concepts"->"2단계 · 개념 읽기";"examples"->"3단계 · 예제 확인";"checks"->"4단계 · 확인 문제";else->"1단계 · 쉬운 설명"}
    Paper(modifier=Modifier.testTag("home-course-card"),accent=true){
        Eyebrow("내 학습 진도")
        Text(if(resume==null)"63강의 학습 단계를 모두 확인했어요"else"${position}강 · ${current.title}",style=MaterialTheme.typography.headlineSmall)
        Text(if(resume==null)"헷갈린 내용을 복습하거나 목차에서 다시 읽을 수 있어요."else"${current.partId} ${course.parts.find{it.id==current.partId}?.title.orEmpty()}\n$section",style=MaterialTheme.typography.bodyMedium)
        Text("읽은 강의 $read / ${course.lessons.size}",style=MaterialTheme.typography.labelLarge)
        LinearProgressIndicator(progress={read.toFloat()/course.lessons.size},modifier=Modifier.fillMaxWidth())
        Button(onClick={if(resume==null)ui.nav("course")else ui.nav("lesson:${current.id}")},modifier=Modifier.fillMaxWidth().heightIn(min=52.dp).testTag("home-course-resume")){
            Text(if(resume==null)"전체 진도 확인"else if(position==1&&ui.state.courseProgress.isEmpty())"1강부터 공부하기"else"강의 공부 이어서")
            Spacer(Modifier.width(8.dp));Icon(Icons.Outlined.ArrowForward,null)
        }
        TextButton(onClick={ui.nav("course")},modifier=Modifier.fillMaxWidth().testTag("home-course-list")){Text("전체 진도 · 다른 강의 선택")}
    }
}

@Composable fun NotesScreen(ui:StudyUi,searchMode:Boolean=false){
    var query by rememberSaveable{mutableStateOf("")};var subject by rememberSaveable{mutableStateOf("all")}
    var importance by rememberSaveable{mutableStateOf("all")};var order by rememberSaveable{mutableStateOf("curriculum")}
    var filtersExpanded by rememberSaveable{mutableStateOf(false)}
    val normalized=query.trim().lowercase()
    val objectives=remember(ui.pack){ui.pack.objectives.associateBy{it.id}}
    val priorities=remember(ui.pack){ui.pack.studyPriorities.associateBy{it.objectiveId}}
    val objectiveText=remember(ui.pack){ui.pack.objectives.associate{it.id to (listOf(it.title)+it.synonyms).map(String::lowercase)}}
    val noteText=remember(ui.pack){ui.pack.notes.associate{it.id to (listOf(it.title)+it.blocks.map{block->block.text}).map(String::lowercase)}}
    val questionText=remember(ui.pack){ui.pack.questions.associate{it.id to listOf(it.title.lowercase(),it.stem.lowercase())}}
    val lessonText=remember(ui.course,ui.courseVisuals){ui.course.lessons.associate{lesson->lesson.id to (listOf(lesson.title,lesson.easy)+lesson.concepts.flatMap{listOf(it.term,it.meaning)}+ui.courseVisuals.searchText(lesson.id)).map(String::lowercase)}}
    fun matches(fields:List<String>?)=fields?.any{it.contains(normalized)}==true
    val objectiveIds=remember(ui.pack,normalized){ui.pack.objectives.filter{matches(objectiveText[it.id])}.map{it.id}.toSet()}
    fun priorityMatch(id:String)=importance=="all"||priorities[id]?.level==importance
    val notes=remember(ui.pack,normalized,subject,importance,order){
        ui.pack.notes.filter{note->priorityMatch(note.objectiveId)&&(subject=="all"||objectives[note.objectiveId]?.subjectId==subject)&&(normalized.isBlank()||note.objectiveId in objectiveIds||matches(noteText[note.id]))}
            .let{if(order=="priority")it.sortedBy{n->StudyGuide.rank(priorities[n.objectiveId]?.level?:"important")}else it}
    }
    val available=remember(ui.pack,ui.state.issues,ui.state.exposures){StudyEngine.available(ui.pack,ui.state)}
    val questions=remember(ui.pack,available,normalized,subject,importance){
        if(normalized.isBlank())emptyList()else available.filter{q->q.objectiveIds.any(::priorityMatch)&&(subject=="all"||q.subjectId==subject)&&(matches(questionText[q.id])||q.objectiveIds.any{it in objectiveIds})}
    }
    val lessons=remember(ui.course,normalized){
        if(normalized.isBlank())emptyList()else ui.course.lessons.filter{matches(lessonText[it.id])}
    }
    val answerCounts=remember(ui.pack,ui.state.submissions){StudyGuide.noteAnswerCounts(ui.pack,ui.state.submissions)}
    LazyColumn(Modifier.fillMaxSize().testTag("notes-list"),contentPadding=PaddingValues(20.dp),verticalArrangement=Arrangement.spacedBy(16.dp)){
        item{PageTitle("",if(searchMode)"검색"else"개념 노트")}
        if(!searchMode)item{FlowButtons(listOf("course" to "강의 순서","notes" to "개념별"),"notes",{if(it=="course")ui.nav("course")})}
        item{OutlinedTextField(query,{query=it},label={Text("검색어")},placeholder={Text("개념 또는 SQL 키워드")},leadingIcon={Icon(Icons.Outlined.Search,null)},modifier=Modifier.fillMaxWidth(),singleLine=true)}
        if(priorities.isNotEmpty())item{FlowButtons(listOf("all" to "모든 중요도","core" to "핵심 개념","important" to "중요 개념","foundation" to "기초 보충"),importance,{importance=it})}
        item{
            Text("노트 ${notes.size}개"+(if(questions.isNotEmpty())" · 연습문제 ${questions.size}개"else"")+(if(lessons.isNotEmpty())" · 강의 ${lessons.size}개"else""),style=MaterialTheme.typography.titleSmall)
            TextButton(onClick={filtersExpanded=!filtersExpanded},modifier=Modifier.testTag("notes-filter-toggle")){
                Text(if(filtersExpanded)"과목·정렬 접기"else"과목·정렬",style=MaterialTheme.typography.labelLarge)
                Icon(if(filtersExpanded)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,null)
            }
            if(filtersExpanded)Column(verticalArrangement=Arrangement.spacedBy(12.dp)){
                Text("과목",style=MaterialTheme.typography.labelLarge)
                FlowButtons(listOf("all" to "전체","model" to "1과목 모델링","sql" to "2과목 SQL"),subject,{subject=it})
                Text("정렬",style=MaterialTheme.typography.labelLarge)
                FlowButtons(listOf("curriculum" to "목차 순서","priority" to "중요도 순서"),order,{order=it})
                Text("중요도는 각 노트의 선정 이유와 출제 근거를 확인하세요.",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
            }else if(subject!="all"||order!="curriculum")Text("${if(subject=="model")"1과목 모델링"else if(subject=="sql")"2과목 SQL"else"전체 과목"} · ${if(order=="priority")"중요도 순서"else"목차 순서"}",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.primary)
        }
        if(notes.isEmpty()&&questions.isEmpty()&&lessons.isEmpty())item{EmptyState("찾은 항목이 없어요","검색어를 줄이거나 다른 용어로 찾아보세요.","검색 지우기",{query="";subject="all";importance="all"})}
        items(notes,key={it.id}){note->
            val counts=answerCounts[note.objectiveId]?:NoteAnswerCounts()
            Column(verticalArrangement=Arrangement.spacedBy(4.dp)){
                priorities[note.objectiveId]?.let{PriorityBadge(it)}
                NoteRow(note.objectiveId,note.title,"${StudyGuide.readingLabel(note,ui.state)} · 암기 정답 ${counts.recall}회 · 적용 정답 ${counts.application}회",{ui.note(note.id)})
            }
        }
        if(questions.isNotEmpty())item{Text("연결된 연습문제 ${questions.size}개",style=MaterialTheme.typography.titleLarge);Text("처음 풀 모의고사의 예약 문제는 검색하지 않아요.",style=MaterialTheme.typography.bodySmall)}
        items(questions,key={"q:${it.id}"}){q->NoteRow(kindLabel(q),q.title,q.objectiveIds.joinToString(" · "),{ui.practice(listOf(q),q.title)})}
        if(normalized.isNotBlank()){
            if(lessons.isNotEmpty())item{Text("강의 노트 ${lessons.size}개",style=MaterialTheme.typography.titleLarge)}
            items(lessons,key={"lesson:${it.id}"}){lesson->NoteRow(lesson.id,lesson.title,"강의별 개념·예제·자기점검",{ui.nav("lesson:${lesson.id}")})}
        }
    }
}

@OptIn(FlowPreview::class)
@Composable fun NoteScreen(ui:StudyUi,id:String){
    val note=ui.pack.notes.find{it.id==id}?:return
    val progress=ui.state.notes.find{it.noteId==id}?:NoteProgress(id)
    // A wider reader can have a smaller maximum scroll. Keep the expanded position
    // separate so that measuring the collapsed layout cannot clamp it permanently.
    val expandedScroll=rememberScrollState(progress.scroll)
    val collapsedScroll=rememberScrollState(progress.scroll)
    var wasExpanded by rememberSaveable(id){mutableStateOf(ui.sidebarsExpanded)}
    var hasExpandedPosition by rememberSaveable(id){mutableStateOf(ui.sidebarsExpanded)}
    val scroll=if(ui.sidebarsExpanded)expandedScroll else collapsedScroll
    var reveal by rememberSaveable(id){mutableStateOf(false)}
    val mode=ui.state.settings.noteView
    val linked=StudyEngine.available(ui.pack,ui.state).filter{note.objectiveId in it.objectiveIds}
    val objective=ui.pack.objectives.find{it.id==note.objectiveId}
    val next=ui.pack.notes.getOrNull(ui.pack.notes.indexOf(note)+1)
    val previous=ui.pack.notes.getOrNull(ui.pack.notes.indexOf(note)-1)
    LaunchedEffect(id,scroll,ui.sidebarsExpanded){
        // Only a user collapse copies the starting position. Recreating an already
        // collapsed screen must retain its own saved scroll rather than jump back.
        if(wasExpanded&&!ui.sidebarsExpanded)collapsedScroll.scrollTo(expandedScroll.value)
        if(ui.sidebarsExpanded&&!hasExpandedPosition){
            expandedScroll.scrollTo(collapsedScroll.value)
            hasExpandedPosition=true
        }
        wasExpanded=ui.sidebarsExpanded
        snapshotFlow{scroll.value}.debounce(250).distinctUntilChanged().collect{position->ui.vm.mutate{s->val old=s.notes.find{it.noteId==id}?:NoteProgress(id);s.copy(notes=s.notes.filterNot{it.noteId==id}+old.copy(scroll=position),lastNoteId=id)}}
    }
    BoxWithConstraints(Modifier.fillMaxSize()){
        val wide=maxWidth>=840.dp
        Row(Modifier.fillMaxSize()){
            if(wide&&ui.sidebarsExpanded)Column(Modifier.width(230.dp).fillMaxHeight().background(MaterialTheme.colorScheme.surfaceVariant).verticalScroll(rememberScrollState()).padding(20.dp).testTag("note-toc")){
                Eyebrow("이 노트의 목차");Spacer(Modifier.height(16.dp));note.blocks.forEachIndexed{index,block->Text(if(mode=="cover"&&!reveal&&block.kind!="recall")"설명 ${index+1} · 가림"else block.title,Modifier.padding(vertical=10.dp),style=MaterialTheme.typography.bodySmall)}
                TextButton(onClick={ui.nav("notes")}){Text("전체 목차")}
            }
            Box(Modifier.weight(1f),contentAlignment=Alignment.TopCenter){Column(Modifier.fillMaxWidth().verticalScroll(scroll).padding(16.dp).testTag("note-reader"),verticalArrangement=Arrangement.spacedBy(16.dp)){
                PageTitle("${if(objective?.subjectId=="model")"1과목"else"2과목"} · ${note.objectiveId}",note.title)
                Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(8.dp),verticalAlignment=Alignment.CenterVertically){Text("창작 학습 노트 · v${note.version}",Modifier.weight(1f),style=MaterialTheme.typography.bodySmall);IconToggleButton(checked=ui.state.noteBookmarks.any{it.id==id},onCheckedChange={ui.vm.mutate{s->s.copy(noteBookmarks=if(s.noteBookmarks.any{it.id==id})s.noteBookmarks.filterNot{it.id==id}else s.noteBookmarks+Bookmark(id,System.currentTimeMillis()))}}){Icon(if(ui.state.noteBookmarks.any{it.id==id})Icons.Outlined.Bookmark else Icons.Outlined.BookmarkBorder,"노트 북마크")}}
                FlowButtons(listOf("full" to "전체 설명","key" to "핵심만","cover" to "암기 가리기"),mode,{ui.vm.settings{s->s.copy(noteView=it)}})
                StudyGuide.priority(ui.pack,note.objectiveId)?.let{priority->if(mode=="cover"&&!reveal)PriorityBadge(priority)else PriorityDetails(ui.pack,priority)}
                if(progress.read&&!StudyGuide.readCurrent(note,ui.state))Text("이전에 읽은 기록이 있어요. 새로 보강된 내용을 확인하고 읽음 표시를 갱신해 주세요.",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.primary)
                Text("문장을 길게 선택하면 형광펜·밑줄·메모를 남길 수 있어요.",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
                if(objective?.prerequisites?.isNotEmpty()==true)Text("선수 개념: ${objective.prerequisites.joinToString { o->ui.pack.objectives.find{it.id==o}?.title?:o }}",style=MaterialTheme.typography.bodySmall)
                note.blocks.filter{mode!="key"||it.kind in listOf("definition","remember","misconception","recall")}.forEach{block->key(id,block.id){
                    val collapsed=block.id in progress.collapsed
                    val hide=mode=="cover"&&!reveal&&block.kind!="recall"
                    val ann=ui.state.annotations.filter{it.noteId==id&&it.blockId==block.id&&!it.archived}
                    Column(modifier=if(block.kind=="remember")Modifier.background(MaterialTheme.colorScheme.primaryContainer,RoundedCornerShape(12.dp)).padding(14.dp)else Modifier,verticalArrangement=Arrangement.spacedBy(8.dp)){
                        if(block.kind=="remember")Row(verticalAlignment=Alignment.CenterVertically,horizontalArrangement=Arrangement.spacedBy(6.dp)){Icon(Icons.Outlined.PriorityHigh,null,Modifier.size(18.dp));Text(if(StudyGuide.priority(ui.pack,note.objectiveId)?.level=="foundation")"기초 정리"else"단원 핵심",style=MaterialTheme.typography.labelLarge)}
                        Row(Modifier.fillMaxWidth().clickable{ui.vm.mutate{s->val old=s.notes.find{it.noteId==id}?:NoteProgress(id);s.copy(notes=s.notes.filterNot{it.noteId==id}+old.copy(collapsed=if(block.id in old.collapsed)old.collapsed-block.id else old.collapsed+block.id))}}.heightIn(min=48.dp),verticalAlignment=Alignment.CenterVertically){
                            Text(if(hide)"설명 가림"else block.title,Modifier.weight(1f),style=MaterialTheme.typography.titleMedium,color=if(block.kind=="remember")MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface);Icon(if(collapsed)Icons.Outlined.ExpandMore else Icons.Outlined.ExpandLess,if(collapsed)"펼치기"else"접기")
                        }
                        if(!collapsed){
                            if(hide)Surface(color=MaterialTheme.colorScheme.surfaceVariant,shape=RoundedCornerShape(10.dp)){Text("설명을 떠올린 뒤 확인해 보세요",Modifier.fillMaxWidth().padding(20.dp),style=MaterialTheme.typography.bodyMedium)}
                            else if(block.kind=="sql")SqlBlock(block.text,ui.state.settings.wrapSql,{wrap->ui.vm.settings{it.copy(wrapSql=wrap)}})
                            else SelectableNoteText(block.text,ann,ui.state.settings.textScale,{quote,style->ui.annotate(id,block.id,quote,style)},emphasis=listOf(note.title,block.title)+objective?.synonyms.orEmpty())
                            if(!hide)ann.filter{it.memo.isNotBlank()}.forEach{a->Surface(color=MaterialTheme.colorScheme.secondaryContainer,shape=RoundedCornerShape(8.dp)){Text("나의 메모 · ${a.memo}",Modifier.fillMaxWidth().padding(14.dp),color=MaterialTheme.colorScheme.onSecondaryContainer,style=MaterialTheme.typography.bodyMedium)}}
                            if(!hide)TextButton(onClick={ui.annotate(id,block.id,block.text,"memo")}){Text("이 단락에 메모")}
                        }
                    }
                }}
                if(mode=="cover")OutlinedButton(onClick={reveal=!reveal},modifier=Modifier.fillMaxWidth()){Text(if(reveal)"다시 가리기"else"설명 확인하기")}
                if(mode!="cover"||reveal){
                    LearningWalkLinks(ui,id)
                    val lessons=ui.course.lessons.filter{id in it.relatedNoteIds}
                    if(lessons.isNotEmpty())Paper{
                        Text("강의별로 더 살펴보기",style=MaterialTheme.typography.titleMedium)
                        Text("예제의 표와 풀이 단계를 보고, 직접 설명해 보세요.",style=MaterialTheme.typography.bodyMedium)
                        lessons.forEach{lesson->TextButton(onClick={ui.nav("lesson:${lesson.id}")},modifier=Modifier.fillMaxWidth()){Text("${lesson.id} · ${lesson.title}",Modifier.fillMaxWidth())}}
                    }
                }
                Paper(accent=true){Text("이해했다면, 떠올려 볼까요?",style=MaterialTheme.typography.titleLarge);Text("연결된 문제 ${linked.size}개 · 보기를 선택한 뒤 직접 채점해요.");Button(onClick={ui.vm.mutate{s->val old=s.notes.find{it.noteId==id}?:NoteProgress(id);s.copy(notes=s.notes.filterNot{it.noteId==id}+old.copy(read=true,readVersion=note.version))};ui.practice(linked.filter{it.kind=="recall"},"${note.title} · 개념 확인")},enabled=linked.any{it.kind=="recall"},modifier=Modifier.fillMaxWidth()){Text("읽음 표시하고 개념 확인")};OutlinedButton(onClick={ui.practice(linked.filter{it.kind=="application"},"${note.title} · 적용 연습")},enabled=linked.any{it.kind=="application"},modifier=Modifier.fillMaxWidth()){Text("테이블에 적용하기")}}
                FlowButtons(listOfNotNull(previous?.let{"prev" to "이전 개념"},next?.let{"next" to "다음 개념"}),"",{if(it=="prev")ui.note(previous!!.id)else ui.note(next!!.id)})
                Text("문서 검토 기반 · DBMS 실행·전문가 검수와 구분합니다.\n근거: ${note.sourceIds.joinToString()}",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
                TextButton(onClick={ui.issue(id)}){Text("내용 오류 표시")}
            }}
        }
    }
}

@Composable fun ReviewScreen(ui:StudyUi){
    var filter by rememberSaveable{mutableStateOf("due")};var subject by rememberSaveable{mutableStateOf("all")};var topic by rememberSaveable{mutableStateOf("all")};var order by rememberSaveable{mutableStateOf("recent")}
    var filtersExpanded by rememberSaveable{mutableStateOf(false)}
    val available=StudyEngine.available(ui.pack,ui.state)
    val reviews=ui.state.reviews.associateBy{it.questionId}
    val bookmarks=ui.state.bookmarks.associateBy{it.id}
    // Submissions append immutable attempts; associateBy keeps the latest recorded attempt.
    val latest=ui.state.submissions.associateBy{it.questionId}
    val topics=listOf("A" to "모델링의 이해","B" to "데이터 모델과 SQL","C" to "SQL 기본","D" to "SQL 활용","E" to "관리 구문")
        .filter{(id,_)->subject=="all"||ui.pack.objectives.any{it.topicId==id&&it.subjectId==subject}}
    val questions=available.filter{q->(subject=="all"||q.subjectId==subject)&&(topic=="all"||q.topicId==topic)&&when(filter){
        "star"->q.id in bookmarks;"wrong"->latest[q.id]?.outcome in listOf("wrong","unanswered");"history"->(reviews[q.id]?.wrongCount?:0)>0
        "unsure"->latest[q.id]?.confidence in listOf("unsure","guess")
        "new"->q.id !in latest
        else->reviews[q.id]?.let{it.dueAt<=System.currentTimeMillis()}==true
    }}.let{list->if(order=="wrong")list.sortedByDescending{reviews[it.id]?.wrongCount?:0}else list.sortedByDescending{
        if(filter=="star")bookmarks[it.id]?.at?:0L else maxOf(bookmarks[it.id]?.at?:0L,latest[it.id]?.submittedAt?:0L)
    }}
    val label=mapOf("due" to "오늘 예정","star" to "별표","wrong" to "현재 오답·미응답","history" to "과거 모든 오답","unsure" to "헷갈림·찍음","new" to "아직 안 푼 문제")[filter]!!
    LazyColumn(Modifier.fillMaxSize().testTag("review-list"),contentPadding=PaddingValues(20.dp),verticalArrangement=Arrangement.spacedBy(18.dp)){
        item{PageTitle("","복습")}
        item{OutlinedButton(onClick={ui.nav("unit")},modifier=Modifier.fillMaxWidth().heightIn(min=48.dp).testTag("review-unit-practice")){Text("단원별 복습 문제")}}
        val courseReview=ui.state.courseProgress.filter{p->p.checks.any{it.rating=="review"}}
        if(courseReview.isNotEmpty())item{Paper{
            Text("강의 자기점검 다시 보기",style=MaterialTheme.typography.titleMedium)
            Text("${courseReview.size}강 · ${courseReview.sumOf{p->p.checks.count{it.rating=="review"}}}개 항목을 다시 보도록 표시했어요.")
            OutlinedButton(onClick={ui.nav("course:review")},modifier=Modifier.fillMaxWidth()){Text("강의 복습 목록")}
        }}
        item{FlowButtons(listOf("due" to "오늘 예정","star" to "별표","wrong" to "현재 오답·미응답","history" to "과거 오답","unsure" to "헷갈림·찍음","new" to "새 문제"),filter,{filter=it})}
        item{
            TextButton(onClick={filtersExpanded=!filtersExpanded},modifier=Modifier.testTag("review-filter-toggle")){
                Text(if(filtersExpanded)"세부 조건 접기"else"과목·단원·정렬")
                Icon(if(filtersExpanded)Icons.Outlined.ExpandLess else Icons.Outlined.ExpandMore,null)
            }
            if(filtersExpanded)Column(verticalArrangement=Arrangement.spacedBy(12.dp)){
                Text("과목",style=MaterialTheme.typography.labelLarge)
                FlowButtons(listOf("all" to "전체 과목","model" to "1과목","sql" to "2과목"),subject,{subject=it;topic="all"})
                Text("단원",style=MaterialTheme.typography.labelLarge)
                FlowButtons(listOf("all" to "전체 단원")+topics,topic,{topic=it})
                Text("정렬",style=MaterialTheme.typography.labelLarge)
                FlowButtons(listOf("recent" to "최근 저장순","wrong" to "틀린 횟수순"),order,{order=it})
            }else Text("${if(subject=="model")"1과목"else if(subject=="sql")"2과목"else"전체 과목"} · ${topics.find{it.first==topic}?.second?:"전체 단원"}\n${if(order=="wrong")"틀린 횟수순"else"최근 저장순"}",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
        }
        item{Column(verticalArrangement=Arrangement.spacedBy(12.dp)){
            Text("${label} ${questions.size}문항",style=MaterialTheme.typography.titleMedium)
            if(questions.isNotEmpty())Button(onClick={ui.practice(questions,label)},modifier=Modifier.fillMaxWidth()){Text("골라 풀기")}
        }}
        if(questions.isEmpty())item{EmptyState("지금은 비어 있어요","문제를 풀거나 별표를 저장하면 이곳에서 다시 볼 수 있어요.","개념 노트로 이동",{ui.nav("notes")})}
        items(questions,key={it.id}){q->NoteRow(q.objectiveIds.first(),q.title,reviews[q.id]?.let{"${it.reason} · 과거 오답 ${it.wrongCount}회"}?:kindLabel(q),{ui.practice(listOf(q),label)},{StarButton(q.id,q.id in bookmarks,{ui.vm.star(q.id)})})}
    }
}
