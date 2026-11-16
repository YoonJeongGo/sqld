package kr.sqld.study

/** Only explicit prose paragraph boundaries are rendered differently; persisted quotes stay raw. */
internal class NoteTextProjection(val source:String,val text:String,private val sourceOffsets:IntArray,val paragraphGaps:List<Int> = emptyList()){
    fun sourceQuote(start:Int,end:Int):String {
        val a=sourceOffsets[start.coerceIn(0,text.length)]
        val b=sourceOffsets[end.coerceIn(0,text.length)]
        return source.substring(minOf(a,b),maxOf(a,b))
    }
    fun displayRange(range:IntRange):IntRange {
        val start=sourceOffsets.indexOfLast{it==range.first}.let{if(it<0)text.length else it}
        val end=sourceOffsets.indexOfFirst{it>=range.last+1}.let{if(it<0)text.length else it}
        return start until end
    }
    companion object {
        fun from(source:String):NoteTextProjection {
            val rule=BodyTextOverrides.entries[source]
            // No paragraph edits means a byte-for-byte identity projection, including original blanks.
            val cuts=rule?.paragraphStarts.orEmpty().mapNotNull{fragment->source.indexOf(fragment).takeIf{it>0&&it==source.lastIndexOf(fragment)}}.distinct().sorted()
            if(cuts.isEmpty())return NoteTextProjection(source,source,IntArray(source.length+1){it})
            val rendered=StringBuilder();val offsets=mutableListOf(0);val gaps=mutableListOf<Int>();var copied=0
            fun copyUntil(end:Int){for(index in copied until end){rendered.append(source[index]);offsets+=index+1};copied=end}
            cuts.forEach{next->
                copyUntil(next)
                rendered.append('\n');offsets+=next
                gaps+=rendered.length
                rendered.append('\n');offsets+=next
                copied=next
            }
            copyUntil(source.length)
            return NoteTextProjection(source,rendered.toString(),offsets.toIntArray(),gaps)
        }
    }
}
