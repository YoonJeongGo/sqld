package kr.sqld.study

data class CoreProgress(val total:Int,val read:Int,val recall:Int,val application:Int)
data class NoteAnswerCounts(val recall:Int=0,val application:Int=0)

/** Learning priorities are editorial guidance, never an estimated exam probability. */
object StudyGuide {
    /** Historical answer counts shown on note rows, not current-version mastery. */
    fun noteAnswerCounts(pack:ContentPack,submissions:List<Submission>):Map<String,NoteAnswerCounts> {
        val questions=pack.questions.associateBy { it.id }
        val counts=mutableMapOf<String,NoteAnswerCounts>()
        for(record in submissions){
            if(record.outcome!="correct" || record.helped)continue
            val question=questions[record.questionId]?:continue
            if(question.kind!="recall" && question.kind!="application")continue
            // A submission counts once per objective, even if an old record repeats the objective ID.
            for(objectiveId in question.objectiveIds.distinct()){
                val previous=counts[objectiveId]?:NoteAnswerCounts()
                counts[objectiveId]=if(question.kind=="recall")previous.copy(recall=previous.recall+1)
                    else previous.copy(application=previous.application+1)
            }
        }
        return counts
    }
    fun label(level:String)=when(level){"core"->"학습 핵심";"foundation"->"기초 보충";else->"중요"}
    fun rank(level:String)=when(level){"core"->0;"important"->1;else->2}
    fun priority(pack:ContentPack,objectiveId:String)=pack.studyPriorities.find{it.objectiveId==objectiveId}
    fun readCurrent(note:Note,state:StudyState):Boolean = state.notes.any{it.noteId==note.id&&it.read&&maxOf(1,it.readVersion)>=note.version}
    fun readingLabel(note:Note,state:StudyState)=when{
        readCurrent(note,state)->"읽음"
        state.notes.any{it.noteId==note.id&&it.read}->"보강 내용 확인 전"
        else->"읽기 전"
    }
    fun coreProgress(pack:ContentPack,state:StudyState):CoreProgress {
        val core=pack.studyPriorities.filter{it.level=="core"}.map{it.objectiveId}.toSet()
        val notes=pack.notes.filter{it.objectiveId in core}
        val questions=pack.practice().associateBy{it.id}
        val correct=state.submissions.filter{it.outcome=="correct"&&!it.helped}.mapNotNull{r->questions[r.questionId]?.takeIf{it.version==r.questionVersion}}
        fun covered(kind:String)=correct.filter{it.kind==kind}.flatMap{it.objectiveIds}.toSet().intersect(core).size
        return CoreProgress(notes.size,notes.count{readCurrent(it,state)},covered("recall"),covered("application"))
    }
    fun next(pack:ContentPack,state:StudyState):Note? {
        val ordered=pack.notes.sortedBy{rank(priority(pack,it.objectiveId)?.level?:"important")}
        val byObjective=pack.notes.associateBy{it.objectiveId}
        fun prerequisite(note:Note,seen:MutableSet<String>):Note? {
            if(!seen.add(note.objectiveId))return null
            val required=pack.objectives.find{it.id==note.objectiveId}?.prerequisites.orEmpty()
            for(id in required){val before=byObjective[id]?:continue;if(!readCurrent(before,state))return prerequisite(before,seen)?:before}
            return if(readCurrent(note,state))null else note
        }
        return ordered.firstOrNull{!readCurrent(it,state)}?.let{prerequisite(it,mutableSetOf())?:it}
    }
}
