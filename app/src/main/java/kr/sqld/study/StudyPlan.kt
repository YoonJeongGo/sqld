package kr.sqld.study

import kotlinx.serialization.Serializable
import java.time.LocalDate
import java.time.temporal.ChronoUnit

@Serializable data class PlanLecture(val number:Int,val title:String,val minutes:Int,val kind:String)
@Serializable data class PlanPdf(val sectionId:String,val title:String,val fromPage:Int,val toPage:Int,val focus:List<String> = emptyList())
@Serializable data class PlanBlock(val title:String,val minutes:Int,val detail:String)
@Serializable data class PlanDay(
    val date:String,val studyDay:Int?=null,val title:String,val phase:String="",val restReason:String="",
    val lectures:List<PlanLecture> = emptyList(),val pdfs:List<PlanPdf> = emptyList(),
    val lessonIds:List<String> = emptyList(),val blocks:List<PlanBlock> = emptyList(),val extension:List<PlanBlock> = emptyList()
) { val isRest:Boolean get()=studyDay==null }
@Serializable data class StudyPlan(
    val schemaVersion:Int=1,val title:String,val startDate:String,val endDate:String,
    val notes:List<String> = emptyList(),val days:List<PlanDay>
) {
    val studyDays:List<PlanDay> get()=days.filterNot{it.isRest}
    val lectures:List<PlanLecture> get()=days.flatMap{it.lectures}.distinctBy{it.number}
    val videoMinutes:Int get()=lectures.sumOf{it.minutes}
    val baseMinutes:Int get()=days.sumOf{day->day.blocks.sumOf{it.minutes}}
    val extraMinutes:Int get()=days.sumOf{day->day.extension.sumOf{it.minutes}}

    fun initialDate(today:LocalDate):String=when {
        today<LocalDate.parse(startDate)->startDate
        today>LocalDate.parse(endDate)->endDate
        else->today.toString()
    }
    fun nextStudyDay(date:String):PlanDay?=studyDays.firstOrNull{it.date>date}

    /** The plan is bundled content, never a completion record or a StudyState migration. */
    fun validate(course:CoursePack):StudyPlan {
        require(schemaVersion==1){"지원하지 않는 학습 계획 형식입니다."}
        val start=LocalDate.parse(startDate);val end=LocalDate.parse(endDate)
        require(!end.isBefore(start)&&days.size.toLong()==ChronoUnit.DAYS.between(start,end)+1)
        require(days.map{it.date}==days.indices.map{start.plusDays(it.toLong()).toString()})
        require(studyDays.map{it.studyDay}==(1..studyDays.size).toList())
        val lessonIds=course.lessons.map{it.id}.toSet()
        days.forEach{day->
            require(day.title.isNotBlank()&&day.lessonIds.all{it in lessonIds})
            require(day.lessonIds.distinct().size==day.lessonIds.size)
            require(day.pdfs.all{it.sectionId in course.parts.map{p->p.id}&&it.fromPage>0&&it.toPage>=it.fromPage})
            require(day.lectures.all{it.number>0&&it.minutes>0&&it.title.isNotBlank()})
            require((day.blocks+day.extension).all{it.minutes>0&&it.title.isNotBlank()})
            if(day.isRest)require(day.restReason.isNotBlank()&&day.lectures.isEmpty()&&day.pdfs.isEmpty()&&day.lessonIds.isEmpty()&&day.blocks.isEmpty()&&day.extension.isEmpty())
            else require(day.blocks.sumOf{it.minutes}==300&&day.extension.sumOf{it.minutes}==60)
        }
        val allLectures=days.flatMap{it.lectures}
        require(allLectures.map{it.number}.distinct().size==allLectures.size)
        return this
    }
}

object PlanReview {
    fun lessons(day:PlanDay,course:CoursePack):List<CourseLesson> = day.lessonIds.mapNotNull{id->course.lessons.find{it.id==id}}
    fun notes(day:PlanDay,course:CoursePack,pack:ContentPack):List<Note> {
        val ids=lessons(day,course).flatMap{it.relatedNoteIds}.toSet()
        return pack.notes.filter{it.id in ids}
    }
    fun questions(day:PlanDay,course:CoursePack,pack:ContentPack,state:StudyState):List<Question> {
        val objectives=notes(day,course,pack).map{it.objectiveId}.toSet()
        // Even previously exposed mock questions stay out of this daily practice entry.
        // Session entry is exposure, not completion. Rotate only this plan entry;
        // keep existing session snapshots and the user's other review sort orders.
        val seen=state.exposures.filter{it.kind=="seen"}.groupBy{it.questionId}
        return StudyEngine.available(pack,state)
            .filter{q->q.kind!="mock"&&q.mockSetId==null&&q.objectiveIds.any{it in objectives}}
            .sortedWith(compareBy<Question>{seen[it.id]?.size?:0}
                .thenBy{seen[it.id]?.maxOfOrNull{event->event.at}?:Long.MIN_VALUE})
    }
}

fun planDuration(minutes:Int):String=when {
    minutes<60->"${minutes}분"
    minutes%60==0->"${minutes/60}시간"
    else->"${minutes/60}시간 ${minutes%60}분"
}
