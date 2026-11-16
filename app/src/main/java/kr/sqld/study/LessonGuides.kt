package kr.sqld.study

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable

@Serializable data class GuidePdfRef(val sectionId:String,val title:String,val fromPage:Int,val toPage:Int,val note:String)
@Serializable data class GuideQuestion(val question:String,val answer:String)
@Serializable data class GuideCheck(val checkId:String,val hint:String,val reasoning:String)
@Serializable data class ExampleGuide(
    val exampleId:String,val why:String,val effect:String,val prerequisites:List<String>,
    val steps:List<WalkStep>,val comparison:String,val verification:String,val terms:List<SqlTerm> = emptyList()
)
@Serializable data class SupplementalExample(val example:CourseExample,val guide:ExampleGuide)
@Serializable data class LessonGuide(
    val schemaVersion:Int=1,val lessonId:String,val source:CourseLesson,val purpose:String,val overview:String,
    val terms:List<SqlTerm>,val pitfalls:List<String>,val questions:List<GuideQuestion>,
    val pdfRefs:List<GuidePdfRef>,val examples:List<ExampleGuide>,val checkGuides:List<GuideCheck>,
    val sourceUrls:List<String> = emptyList(),val reviewNotes:List<String> = emptyList(),
    val supplementalExamples:List<SupplementalExample> = emptyList()
) {
    fun matches(lesson:CourseLesson)=source==lesson&&lessonId==lesson.id
    fun walkthrough(example:CourseExample,guide:ExampleGuide):SqlWalkthrough {
        val source=WalkSource(example.id,this.source.version,example.title,example.question,
            example.sql.takeIf{it.isNotBlank()},example.tables,dialect=if(example.mode=="oracle")"Oracle"else if(example.mode=="sqlite")"SQLite"else"conceptual",
            dialectVersion=if(example.mode=="oracle")"19c"else "")
        return SqlWalkthrough("guide-${example.id}",source,guide.why,
            listOf(WalkStep("guide-purpose","전체 코드의 목적과 전제",
                guide.effect+"\n\n"+guide.prerequisites.joinToString("\n")))+guide.steps+
                listOf(WalkStep("guide-comparison","헷갈리는 부분 비교",guide.comparison)),
            guide.terms.ifEmpty{terms.filter{term->example.sql.isBlank()||term.token.split(" / ").any{example.sql.contains(it,ignoreCase=true)}}},WalkVerification(method=guide.verification,notes=reviewNotes),sourceUrls,
            narrativeLabel="추가 해설 · 학습용 코드와 표 읽기")
    }
}

object LessonGuideRules {
    fun validate(guide:LessonGuide) {
        require(guide.schemaVersion==1&&guide.lessonId==guide.source.id)
        require(guide.purpose.isNotBlank()&&guide.overview.isNotBlank())
        require(guide.examples.map{it.exampleId}==guide.source.examples.map{it.id})
        require(guide.checkGuides.map{it.checkId}==guide.source.selfChecks.map{it.id})
        require(guide.checkGuides.all{it.hint.isNotBlank()&&it.reasoning.isNotBlank()})
        require(guide.terms.all{it.token.isNotBlank()&&it.meaning.isNotBlank()&&it.role.isNotBlank()})
        require(guide.pdfRefs.all{it.sectionId in setOf("1-1","1-2","2-1","2-2","2-3")&&it.fromPage>0&&it.toPage>=it.fromPage})
        val ids=guide.source.examples.map{it.id}+guide.supplementalExamples.map{it.example.id}
        require(ids.distinct().size==ids.size)
        (guide.source.examples.zip(guide.examples)+guide.supplementalExamples.map{it.example to it.guide}).forEach{(example,explanation)->
            require(explanation.exampleId==example.id&&explanation.why.isNotBlank()&&explanation.effect.isNotBlank())
            require(explanation.steps.isNotEmpty()&&explanation.prerequisites.isNotEmpty()&&explanation.comparison.isNotBlank())
            WalkthroughRules.validate(guide.walkthrough(example,explanation))
        }
    }
    fun stepKey(exampleId:String)="guide:$exampleId"
}

/** One lesson at a time; full source snapshots prevent attaching obsolete explanations. */
class LessonGuideCatalog(private val context:Context) {
    private val mutex=Mutex()
    private val cache=LinkedHashMap<String,LessonGuide>()
    var materialReads=0; private set
    suspend fun lesson(lesson:CourseLesson):LessonGuide?=withContext(Dispatchers.IO){mutex.withLock {
        require(lesson.id.matches(Regex("[0-9]-[0-9]-[0-9]{2}")))
        val guide=cache.remove(lesson.id)?:context.assets.open("lesson-guides/${lesson.id}.json").bufferedReader(Charsets.UTF_8).use{
            Codec.decodeFromString<LessonGuide>(it.readText()).also{material->LessonGuideRules.validate(material);materialReads++}
        }
        cache[lesson.id]=guide
        if(cache.size>3)cache.remove(cache.keys.first())
        guide.takeIf{it.matches(lesson)}
    }}
}
