package kr.sqld.study

import kotlinx.serialization.Serializable

/** Additional teaching material; never part of attempts, scores, or saved progress. */
@Serializable data class VisualLabel(val label:String,val meaning:String)
@Serializable data class CourseVisual(
    val id:String,val number:Int,val title:String,val subtitle:String,val lessonIds:List<String>,
    val pngAsset:String,val svgAsset:String,val width:Int,val height:Int,val alt:String,
    val easy:String,val readingSteps:List<String>,val resultReason:String,
    val labels:List<VisualLabel>,val dataNotes:String,val warnings:List<String>,val memory:String,
    val sourceIds:List<String>,val tables:List<DataTable>,val transcript:String,val correction:String=""
)
@Serializable data class LessonReadingGuide(
    val lessonId:String,val classification:String,val reason:String,
    val easySupplement:String="",val exampleReadingGuide:String="",val syntaxCaution:String="",
    val unlinkedReason:String=""
)
@Serializable data class CourseVisualPack(
    val schemaVersion:Int=1,val version:String,val provenance:String,
    val sources:List<CourseSource>,val visuals:List<CourseVisual>,val guides:List<LessonReadingGuide>
){
    fun forLesson(id:String)=visuals.filter{ id in it.lessonIds }
    fun guide(id:String)=guides.firstOrNull{it.lessonId==id}
    fun searchText(id:String):List<String> = forLesson(id).flatMap {
        listOf(it.title,it.subtitle,it.easy,it.resultReason,it.memory,it.dataNotes,it.transcript,it.correction)+
            it.readingSteps+it.warnings+it.labels.flatMap{label->listOf(label.label,label.meaning)}
    }+listOfNotNull(guide(id)?.let{listOf(it.easySupplement,it.exampleReadingGuide,it.syntaxCaution).joinToString(" ")})
}

object CourseVisuals {
    private val asset=Regex("course-visuals/visual-[0-9]{2}\\.(png|svg)")
    fun validate(pack:CourseVisualPack,course:CoursePack){
        require(pack.schemaVersion==1 && pack.version.isNotBlank() && pack.provenance.isNotBlank())
        val lessons=course.lessons.map{it.id}.toSet()
        require(pack.visuals.map{it.id}.distinct().size==pack.visuals.size)
        require(pack.visuals.map{it.number}.distinct().size==pack.visuals.size)
        require(pack.guides.map{it.lessonId}.distinct().size==pack.guides.size)
        require(pack.sources.map{it.id}.distinct().size==pack.sources.size)
        require(pack.sources.all{it.title.isNotBlank() && it.url.startsWith("https://")})
        val sources=pack.sources.map{it.id}.toSet()
        pack.visuals.forEach { visual ->
            require(visual.id=="visual-${visual.number.toString().padStart(2,'0')}" && visual.number in 1..27)
            require(asset.matches(visual.pngAsset) && visual.pngAsset.endsWith(".png"))
            require(asset.matches(visual.svgAsset) && visual.svgAsset.endsWith(".svg"))
            require(visual.width>0 && visual.height>0 && visual.width*5==visual.height*8)
            require(visual.lessonIds.isNotEmpty() && visual.lessonIds.all{it in lessons} && visual.lessonIds.distinct()==visual.lessonIds)
            require(listOf(visual.title,visual.alt,visual.easy,visual.resultReason,visual.dataNotes,visual.memory,visual.transcript).all{it.isNotBlank()})
            require(visual.readingSteps.size>=3 && visual.readingSteps.all{it.isNotBlank()})
            require(visual.sourceIds.isNotEmpty() && visual.sourceIds.all{it in sources})
            require(visual.labels.all{it.label.isNotBlank() && it.meaning.isNotBlank()})
            visual.tables.forEach { table -> require(table.columns.isNotEmpty() && table.rows.all{it.size==table.columns.size}) }
        }
        pack.guides.forEach { require(it.lessonId in lessons && it.classification.isNotBlank() && it.reason.isNotBlank()) }
    }
}
