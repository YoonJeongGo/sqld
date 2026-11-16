package kr.sqld.study

import kotlinx.serialization.Serializable
import java.security.MessageDigest
import java.util.UUID
import kotlin.math.hypot

/** Coordinates are in the SQL document's fixed 16-unit text / 24-unit line grid, never viewport percentages. */
@Serializable data class InkPoint(val x:Float,val y:Float,val pressure:Float=1f)
@Serializable data class InkStroke(val id:String,val tool:String="pen",val color:Long=0xff172d45L,val width:Float=2.5f,val opacity:Float=1f,val points:List<InkPoint>)
@Serializable data class InkEdit(val id:String,val stroke:InkStroke?=null,val erasedIds:List<String> = emptyList())
@Serializable data class InkDocument(val id:String,val sourceId:String,val sourceHash:String,val edits:List<InkEdit> = emptyList(),val cursor:Int=0,val updatedAt:Long=0)

object InkStore {
    const val MAX_DOCUMENTS=2000
    const val MAX_EDITS=2000
    const val MAX_POINTS_PER_STROKE=4000
    const val MAX_TOTAL_POINTS=200000
    const val MAX_TOTAL_EDITS=20000
    const val MAX_COORDINATE=100000f
    fun hash(text:String)=MessageDigest.getInstance("SHA-256").digest(text.toByteArray(Charsets.UTF_8)).joinToString(""){"%02x".format(it)}
    fun documentId(sourceId:String,sql:String)="sql-ink-"+hash(sourceId+"\u0000"+hash(sql))
    fun empty(sourceId:String,sql:String)=InkDocument(documentId(sourceId,sql),sourceId,hash(sql))
    fun matches(document:InkDocument,sourceId:String,sql:String)=document.sourceId==sourceId&&document.sourceHash==hash(sql)&&document.id==documentId(sourceId,sql)
    fun visibleStrokes(document:InkDocument):List<InkStroke> {
        val visible=linkedMapOf<String,InkStroke>()
        document.edits.take(document.cursor).forEach { edit -> edit.stroke?.let{visible[it.id]=it};edit.erasedIds.forEach(visible::remove) }
        return visible.values.toList()
    }
    fun append(document:InkDocument,edit:InkEdit,now:Long=System.currentTimeMillis()):InkDocument {
        val edits=document.edits.take(document.cursor)+edit
        return document.copy(edits=edits,cursor=edits.size,updatedAt=now).also(::validateDocument)
    }
    fun add(document:InkDocument,stroke:InkStroke,now:Long=System.currentTimeMillis())=append(document,InkEdit(UUID.randomUUID().toString(),stroke=stroke),now)
    fun erase(document:InkDocument,ids:List<String>,now:Long=System.currentTimeMillis()):InkDocument =
        if(ids.isEmpty())document else append(document,InkEdit(UUID.randomUUID().toString(),erasedIds=ids.distinct()),now)
    fun undo(document:InkDocument,now:Long=System.currentTimeMillis())=document.copy(cursor=(document.cursor-1).coerceAtLeast(0),updatedAt=now)
    fun redo(document:InkDocument,now:Long=System.currentTimeMillis())=document.copy(cursor=(document.cursor+1).coerceAtMost(document.edits.size),updatedAt=now)
    fun upsert(state:StudyState,document:InkDocument):StudyState {
        validateDocument(document)
        val documents=state.inkDocuments.filterNot{it.id==document.id}+document
        validate(documents)
        return state.copy(inkDocuments=documents)
    }
    fun validate(documents:List<InkDocument>) {
        require(documents.size<=MAX_DOCUMENTS){"필기 문서 수 한도를 넘었습니다."}
        require(documents.map{it.id}.distinct().size==documents.size){"중복된 필기 문서입니다."}
        var points=0L;var edits=0L
        documents.forEach { document ->
            validateDocument(document)
            edits+=document.edits.size
            points+=document.edits.sumOf{it.stroke?.points?.size?.toLong()?:0L}
        }
        require(points<=MAX_TOTAL_POINTS&&edits<=MAX_TOTAL_EDITS){"필기 저장 용량 한도를 넘었습니다. 백업 후 불필요한 필기를 정리해 주세요."}
    }
    fun validateDocument(document:InkDocument) {
        require(document.sourceId.isNotBlank()&&document.sourceId.length<=512&&document.sourceHash.matches(Regex("[0-9a-f]{64}"))){"필기 원문 연결이 올바르지 않습니다."}
        require(document.id=="sql-ink-"+hash(document.sourceId+"\u0000"+document.sourceHash)){"필기 문서 ID가 원문과 맞지 않습니다."}
        require(document.edits.size<=MAX_EDITS&&document.cursor in 0..document.edits.size&&document.updatedAt>=0){"필기 이력 한도를 벗어났습니다."}
        val editIds=hashSetOf<String>();val strokeIds=hashSetOf<String>();val visible=hashSetOf<String>()
        document.edits.forEach { edit ->
            require(edit.id.isNotBlank()&&edit.id.length<=100&&editIds.add(edit.id)){"중복되거나 잘못된 필기 이력 ID입니다."}
            require((edit.stroke!=null) xor edit.erasedIds.isNotEmpty()){"필기 변경 종류가 올바르지 않습니다."}
            edit.stroke?.let { stroke ->
                require(stroke.id.isNotBlank()&&stroke.id.length<=100&&strokeIds.add(stroke.id)){"중복된 획 ID입니다."}
                require(stroke.tool in listOf("pen","highlighter")&&stroke.color in 0..0xffffffffL){"잘못된 펜 종류나 색상입니다."}
                require(stroke.width.isFinite()&&stroke.width in 0.5f..24f&&stroke.opacity.isFinite()&&stroke.opacity in 0.05f..1f){"잘못된 펜 굵기나 불투명도입니다."}
                require(stroke.points.isNotEmpty()&&stroke.points.size<=MAX_POINTS_PER_STROKE){"획 좌표 수가 한도를 벗어났습니다."}
                require(stroke.points.all{it.x.isFinite()&&it.y.isFinite()&&it.pressure.isFinite()&&it.x in 0f..MAX_COORDINATE&&it.y in 0f..MAX_COORDINATE&&it.pressure in 0f..1f}){"잘못된 필기 좌표입니다."}
                visible+=stroke.id
            }
            require(edit.erasedIds.distinct().size==edit.erasedIds.size&&edit.erasedIds.all{it in visible}){"지운 획 참조가 올바르지 않습니다."}
            visible.removeAll(edit.erasedIds.toSet())
        }
    }
    /** Segment distance, so an eraser also hits between two sparse stylus samples. */
    fun hit(stroke:InkStroke,x:Float,y:Float,radius:Float):Boolean {
        val distance=radius+stroke.width/2
        if(stroke.points.size==1)return hypot(stroke.points[0].x-x,stroke.points[0].y-y)<=distance
        for(index in 1 until stroke.points.size) {
            val a=stroke.points[index-1];val b=stroke.points[index]
            val dx=b.x-a.x;val dy=b.y-a.y;val length=dx*dx+dy*dy
            val t=if(length==0f)0f else (((x-a.x)*dx+(y-a.y)*dy)/length).coerceIn(0f,1f)
            if(hypot(a.x+t*dx-x,a.y+t*dy-y)<=distance)return true
        }
        return false
    }
}
