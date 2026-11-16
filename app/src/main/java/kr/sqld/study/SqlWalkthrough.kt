package kr.sqld.study

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString

/** Separate teaching material. It never participates in grading or changes a session snapshot. */
@Serializable data class WalkSource(
    val id:String,val version:Int=1,val title:String,val stem:String,val sql:String?=null,
    val tables:List<DataTable> = emptyList(),val choices:List<Choice> = emptyList(),
    val correctChoiceIds:List<String> = emptyList(),val dialect:String="Oracle",val dialectVersion:String="19c"
) {
    fun matches(q:Question)=this==from(q)
    fun fingerprint()=BackupCodec.hash(Codec.encodeToString(this))
    companion object {
        fun from(q:Question)=WalkSource(q.id,q.version,q.title,q.stem,q.sql,q.tables,q.choices,q.correctChoiceIds,q.dialect,q.dialectVersion)
    }
}
@Serializable data class CodeFocus(val needle:String,val occurrence:Int=0)
@Serializable data class FocusCell(val row:Int,val column:Int)
@Serializable data class WalkStep(
    val id:String,val title:String,val text:String,val codeFocus:List<CodeFocus> = emptyList(),
    val highlights:List<String> = emptyList(),val table:DataTable?=null,
    val focusCells:List<FocusCell> = emptyList(),val focusRows:List<Int> = emptyList()
)
@Serializable data class SqlTerm(val token:String,val kind:String,val meaning:String,val role:String)
@Serializable data class WalkVerification(
    val method:String="",val engine:String="",val engineVersion:String="",val oracleEngineExecuted:Boolean=false,
    val queryMode:String="",val expectedRowsMatch:Boolean=false,val notes:List<String> = emptyList()
)
@Serializable data class SqlWalkthrough(
    val id:String,val source:WalkSource,val intro:String,val steps:List<WalkStep>,
    val terms:List<SqlTerm> = emptyList(),val verification:WalkVerification=WalkVerification(),val sourceUrls:List<String> = emptyList(),
    val narrativeLabel:String="학습용 논리 흐름"
)
@Serializable data class WalkRef(val questionId:String,val file:String)
@Serializable data class LearningWalkRef(val id:String,val title:String,val noteIds:List<String> = emptyList(),val file:String)
@Serializable data class WalkIndex(val schemaVersion:Int=1,val version:String="",val entries:List<WalkRef> = emptyList(),val learningExamples:List<LearningWalkRef> = emptyList())

object WalkthroughRules {
    fun ranges(sql:String,focus:List<CodeFocus>):List<IntRange> = focus.map { target ->
        require(target.needle.isNotEmpty()&&target.occurrence>=0)
        var from=0;var found=-1
        repeat(target.occurrence+1){found=sql.indexOf(target.needle,from);require(found>=0){"SQL emphasis no longer matches its source"};from=found+target.needle.length}
        found until found+target.needle.length
    }
    fun validate(w:SqlWalkthrough){
        require(w.steps.isNotEmpty()&&w.steps.size<=100)
        require(w.steps.map{it.id}.distinct().size==w.steps.size)
        w.steps.forEach { step ->
            require(step.title.isNotBlank()&&step.text.isNotBlank())
            ranges(w.source.sql.orEmpty(),step.codeFocus)
            require(step.highlights.all{it.isNotEmpty()&&step.text.contains(it)})
            step.table?.let { table ->
                require(table.columns.isNotEmpty()&&table.rows.all{it.size==table.columns.size})
                require(step.focusCells.all{it.row in table.rows.indices&&it.column in table.columns.indices})
                require(step.focusRows.all{it in table.rows.indices})
            } ?: require(step.focusCells.isEmpty()&&step.focusRows.isEmpty())
        }
    }
}

/** Only the small index is opened on demand; at most six full explanations stay cached. */
class WalkthroughCatalog(private val context:Context){
    private val mutex=Mutex()
    private var index:WalkIndex?=null
    private val cache=LinkedHashMap<String,SqlWalkthrough>()
    var materialReads:Int=0; private set
    private fun indexLocked():WalkIndex {
        index?.let{return it}
        return Codec.decodeFromString<WalkIndex>(context.assets.open("sql-walkthroughs/index.json").bufferedReader().use{it.readText()}).also{
            require(it.schemaVersion==1&&it.entries.map{e->e.questionId}.distinct().size==it.entries.size)
            index=it
        }
    }
    private fun loadLocked(file:String):SqlWalkthrough {
        require(file.matches(Regex("[A-Za-z0-9_.-]+\\.json"))&&!file.contains(".."))
        cache.remove(file)?.let{cache[file]=it;return it}
        val value=Codec.decodeFromString<SqlWalkthrough>(context.assets.open("sql-walkthroughs/$file").bufferedReader().use{it.readText()})
        WalkthroughRules.validate(value);materialReads++
        cache[file]=value
        if(cache.size>6)cache.remove(cache.keys.first())
        return value
    }
    suspend fun question(q:Question):SqlWalkthrough?=withContext(Dispatchers.IO){mutex.withLock{
        indexLocked().entries.find{it.questionId==q.id}?.let { loadLocked(it.file).takeIf{w->w.source.matches(q)} }
    }}
    suspend fun learningFor(noteId:String):List<LearningWalkRef> = withContext(Dispatchers.IO){mutex.withLock{indexLocked().learningExamples.filter{noteId in it.noteIds}}}
    suspend fun learning(id:String):SqlWalkthrough?=withContext(Dispatchers.IO){mutex.withLock{indexLocked().learningExamples.find{it.id==id}?.let{loadLocked(it.file)}}}
}
