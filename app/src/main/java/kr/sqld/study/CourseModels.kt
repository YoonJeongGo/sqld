package kr.sqld.study

import kotlinx.serialization.Serializable

@Serializable data class CoursePart(val id:String,val title:String)
@Serializable data class CourseSource(val id:String,val title:String,val url:String)
@Serializable data class CourseConcept(val term:String,val meaning:String,val example:String)
@Serializable data class CourseCheck(val id:String,val question:String,val answer:String,val explanation:String)
@Serializable data class CourseExample(
    val id:String,val title:String,val question:String,val tables:List<DataTable> = emptyList(),
    val sql:String="",val steps:List<String> = emptyList(),val results:List<DataTable> = emptyList(),
    val mode:String="theory",val verification:String="문서 기반 예제 · 앱에서 SQL을 실행하지 않습니다."
)
@Serializable data class CourseLesson(
    val id:String,val partId:String,val number:Int,val title:String,val lectureMinutes:Int,
    val easy:String,val why:String,val concepts:List<CourseConcept>,val examples:List<CourseExample>,
    val memory:String,val traps:List<String>,val selfChecks:List<CourseCheck>,val relatedNoteIds:List<String>,
    val sourceIds:List<String>,val bridge:String="",val diagramSvg:String="",val version:Int=1
)
@Serializable data class CoursePack(
    val schemaVersion:Int=1,val version:String,val title:String,val parts:List<CoursePart>,
    val lessons:List<CourseLesson>,val sources:List<CourseSource>,val provenance:String,
    val reviewNote:String
)
@Serializable data class CourseCheckProgress(val checkId:String,val draft:String="",val revealed:Boolean=false,val rating:String="")
@Serializable data class CourseProgress(
    val lessonId:String,val readVersion:Int=0,val scroll:Int=0,val section:String="overview",
    val exampleSteps:Map<String,Int> = emptyMap(),val revealedResults:List<String> = emptyList(),
    val checks:List<CourseCheckProgress> = emptyList(),val updatedAt:Long=0
)
