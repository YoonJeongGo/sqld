package kr.sqld.study

import java.time.Instant
import java.time.ZoneId
import java.util.UUID
import kotlin.random.Random

/** Pure transitions. Persistence calls these inside a single Room transaction. */
object StudyEngine {
    fun score(modelCorrect:Int,sqlCorrect:Int,unanswered:Int=0,spec:ExamSpec=ExamSpec()):Score {
        require(modelCorrect in 0..spec.modelCount && sqlCorrect in 0..spec.sqlCount)
        val points=(modelCorrect+sqlCorrect)*spec.pointsPerQuestion
        val mf=modelCorrect*100 < spec.modelCount*spec.subjectMinimumPercent
        val sf=sqlCorrect*100 < spec.sqlCount*spec.subjectMinimumPercent
        return Score(modelCorrect,sqlCorrect,spec.modelCount,spec.sqlCount,unanswered,points,mf,sf,points>=spec.passPoints&&!mf&&!sf)
    }
    fun score(session:QuizSession, state:StudyState):Score {
        val records=state.submissions.filter { it.sessionId==session.id }.associateBy { it.questionId }
        fun correct(subject:String)=session.items.count { it.question.subjectId==subject && records[it.question.id]?.outcome=="correct" }
        val unanswered=session.items.count { records[it.question.id]?.outcome=="unanswered" }
        if(session.mockSetId!=null)return score(correct("model"),correct("sql"),unanswered,session.examSpec)
        return Score(correct("model"),correct("sql"),session.items.count{it.question.subjectId=="model"},session.items.count{it.question.subjectId=="sql"},unanswered,(correct("model")+correct("sql"))*session.examSpec.pointsPerQuestion,false,false,false)
    }
    fun available(pack:ContentPack,state:StudyState):List<Question> {
        val excluded=state.issues.filter { it.exclude }.map { it.contentId }.toSet()
        val exposed=state.exposures.map{it.questionId}.toSet()
        return pack.questions.filter { q -> q.status=="published" && q.verification !in listOf("draft","quarantined") && q.id !in excluded && ((q.mockSetId==null&&q.kind!="mock")||q.id in exposed) }
    }
    fun createSession(state:StudyState,pack:ContentPack,questions:List<Question>,mode:String,title:String,now:Long,elapsed:Long,boot:Int,seed:Int=Random.nextInt(),mockSetId:String?=null):StudyState {
        require(mode in listOf("immediate","batch","strict"))
        require(questions.isNotEmpty() && questions.map{it.id}.distinct().size==questions.size)
        require(questions.all { it.status=="published" && it.verification !in listOf("draft","quarantined") })
        if(mode=="strict") {
            require(mockSetId!=null && questions.all{it.mockSetId==mockSetId})
            require(questions.count{it.subjectId=="model"}==pack.examSpec.modelCount && questions.count{it.subjectId=="sql"}==pack.examSpec.sqlCount)
        }
        val id=UUID.randomUUID().toString()
        val random=Random(seed)
        val items=questions.map { SessionItem(it,it.choices.map{c->c.id}.shuffled(random)) }
        val exposedFamilies=state.exposures.map{it.familyId}.toSet()
        val repeat=mockSetId!=null && state.sessions.any{it.mockSetId==mockSetId}
        val session=QuizSession(id,title,mode,items,pack.version,pack.examSpec,now,seed,
            mockSetId=mockSetId,diagnosticEligible=mode=="strict"&&!repeat&&questions.none{it.familyId in exposedFamilies},repeat=repeat,
            remainingMillis=if(mode=="strict") pack.examSpec.minutes*60_000L else 0,lastWall=now,lastElapsed=elapsed,bootCount=boot)
        // Entry permanently records reservation exposure; eligibility was calculated before this event.
        val exposures=questions.map { Exposure("$id:${it.id}:seen",it.id,it.familyId,id,"seen",now) }
        return state.copy(sessions=state.sessions+session,exposures=state.exposures+exposures,activeSessionId=id)
    }
    private fun editSession(state:StudyState,id:String,fn:(QuizSession)->QuizSession)=state.copy(sessions=state.sessions.map{if(it.id==id)fn(it)else it})
    fun select(state:StudyState,id:String,index:Int,choiceId:String):StudyState=editSession(state,id) { s ->
        require(s.submittedAt==null)
        val item=s.items[index]
        require(item.submissionId==null && choiceId in item.choiceOrder)
        s.copy(items=s.items.mapIndexed{i,it->if(i==index)it.copy(draft=listOf(choiceId))else it})
    }
    fun confidence(state:StudyState,id:String,index:Int,value:String):StudyState=editSession(state,id) { s ->
        require(value in listOf("","sure","unsure","guess"))
        s.copy(items=s.items.mapIndexed{i,it->if(i==index && it.submissionId==null)it.copy(confidence=value)else it})
    }
    fun move(state:StudyState,id:String,index:Int):StudyState=editSession(state,id) { it.copy(current=index.coerceIn(0,it.items.lastIndex)) }
    fun scroll(state:StudyState,id:String,index:Int,pixels:Int):StudyState=editSession(state,id) { s -> s.copy(items=s.items.mapIndexed{i,it->if(i==index)it.copy(scroll=pixels.coerceAtLeast(0))else it}) }
    fun addTime(state:StudyState,id:String,index:Int,millis:Long):StudyState=editSession(state,id) { s -> s.copy(items=s.items.mapIndexed{i,it->if(i==index && it.submissionId==null)it.copy(activeMillis=it.activeMillis+millis.coerceIn(0,60_000))else it},elapsedMillis=s.elapsedMillis+millis.coerceIn(0,60_000)) }
    fun convert(state:StudyState,id:String,now:Long):StudyState=editSession(state,id) {
        require(it.submittedAt==null)
        it.copy(mode="mixed",diagnosticEligible=false,convertedAt=now)
    }
    fun help(state:StudyState,id:String,index:Int,kind:String,now:Long):StudyState {
        val s=state.sessions.first{it.id==id}; require(s.mode!="strict" || s.submittedAt!=null)
        val q=s.items[index].question
        val event=Exposure("$id:${q.id}:$kind",q.id,q.familyId,id,kind,now)
        return if(state.exposures.any{it.id==event.id})state else state.copy(exposures=state.exposures+event)
    }
    fun grade(state:StudyState,id:String,index:Int,now:Long,unanswered:Boolean=false,whole:Boolean=false):StudyState {
        val s=state.sessions.first{it.id==id}; val item=s.items[index]
        if(item.submissionId!=null)return state
        require(s.submittedAt==null)
        require(s.mode!="strict"||whole) { "실전 채점은 연습 전환 확인 또는 전체 제출이 필요합니다." }
        require(item.draft.isNotEmpty()||unanswered)
        val q=item.question
        val choices=if(unanswered)emptyList()else item.draft
        val outcome=if(choices.isEmpty())"unanswered" else if(choices.toSet()==q.correctChoiceIds.toSet())"correct" else "wrong"
        val helped=s.convertedAt!=null || state.exposures.any{it.sessionId==id && it.questionId==q.id && it.kind in listOf("note","hint","explanation") && it.at<=now}
        val submission=Submission("$id:${q.id}",id,q.id,q.version,choices,item.choiceOrder,outcome,helped,item.confidence,item.activeMillis,now,s.contentVersion,s.examSpec.id,
            state.submissions.none{it.questionId==q.id} && state.exposures.none{it.familyId==q.familyId && it.sessionId!=id})
        val old=state.reviews.find{it.questionId==q.id}?:ReviewState(q.id)
        val day=Instant.ofEpochMilli(now).atZone(ZoneId.systemDefault()).toLocalDate().toString()
        val independentCorrect=outcome=="correct"&&!helped&&item.confidence !in listOf("unsure","guess")
        // The user may shorten the interval list after a review on this same day.
        // Keep the stored history, but always index the current list with a valid stage.
        val stage=(if(!independentCorrect)0 else if(old.lastDay.isNotEmpty() && old.lastDay!=day)old.stage+1 else old.stage)
            .coerceIn(0,state.settings.intervals.lastIndex)
        val days=if(independentCorrect)state.settings.intervals[stage]else 1
        val review=old.copy(wrongCount=old.wrongCount+if(outcome=="wrong"||outcome=="unanswered")1 else 0,
            stage=stage,dueAt=now+days*86_400_000L,needsReview=!independentCorrect,lastDay=day,lastOutcome=outcome,
            reason=when { outcome=="unanswered"->"미응답을 다시 확인해요"; outcome=="wrong"->"오답 개념을 다시 확인해요"; helped->"도움 없이 다시 풀어봐요"; item.confidence in listOf("unsure","guess")->"헷갈렸던 근거를 확인해요"; else->"${days}일 간격 복습" })
        val next=editSession(state,id) { a -> a.copy(items=a.items.mapIndexed{i,it->if(i==index)it.copy(draft=choices,submissionId=submission.id)else it}) }
        return next.copy(submissions=state.submissions+submission,reviews=state.reviews.filterNot{it.questionId==q.id}+review)
    }
    fun submit(state:StudyState,id:String,now:Long):StudyState {
        val s=state.sessions.first{it.id==id}; if(s.submittedAt!=null)return state
        var result=state
        s.items.indices.forEach { i -> result=grade(result,id,i,now,unanswered=s.items[i].draft.isEmpty(),whole=true) }
        return editSession(result,id){it.copy(submittedAt=now)}
    }
    fun tick(state:StudyState,id:String,now:Long,elapsed:Long,boot:Int):StudyState {
        val s=state.sessions.first{it.id==id}
        if(s.mode!="strict" || s.submittedAt!=null)return state
        val wallDelta=now-s.lastWall
        val sameBoot=boot==s.bootCount && elapsed>=s.lastElapsed
        val monoDelta=if(sameBoot)elapsed-s.lastElapsed else wallDelta
        val anomaly=wallDelta < -2_000L || (sameBoot && kotlin.math.abs(wallDelta-monoDelta)>120_000)
        val delta=if(anomaly) s.remainingMillis else if(sameBoot) maxOf(monoDelta,wallDelta.coerceAtLeast(0)) else wallDelta.coerceAtLeast(0)
        val remaining=(s.remainingMillis-delta).coerceAtLeast(0)
        var next=editSession(state,id){it.copy(remainingMillis=remaining,lastWall=now,lastElapsed=elapsed,bootCount=boot,clockAnomaly=it.clockAnomaly||anomaly,diagnosticEligible=it.diagnosticEligible&&!anomaly)}
        if(remaining==0L)next=submit(next,id,now)
        return next
    }
    fun bookmark(state:StudyState,id:String,now:Long):StudyState=state.copy(bookmarks=if(state.bookmarks.any{it.id==id})state.bookmarks.filterNot{it.id==id}else state.bookmarks+Bookmark(id,now))
    fun reconcile(state:StudyState,pack:ContentPack):StudyState=state.copy(contentVersion=pack.version,
        notes=state.notes.map{n->if(n.read&&n.readVersion==0)pack.legacyNoteVersions[n.noteId]?.let{n.copy(readVersion=it)}?:n else n},
        annotations=state.annotations.map { a ->
        val note=pack.notes.find{it.id==a.noteId}; val block=note?.blocks?.find{it.id==a.blockId && a.quote in it.text} ?: note?.blocks?.find{a.quote.isNotEmpty()&&a.quote in it.text}
        if(block!=null)a.copy(blockId=block.id,archived=false)else a.copy(archived=true)
    })
    /** Ordered tuples preserve NULL, column positions, duplicate rows, and typed values. */
    fun <T> equalRows(expected:List<List<T>>,actual:List<List<T>>,ordered:Boolean):Boolean =
        if(ordered)expected==actual else expected.groupingBy{it}.eachCount()==actual.groupingBy{it}.eachCount()
}
