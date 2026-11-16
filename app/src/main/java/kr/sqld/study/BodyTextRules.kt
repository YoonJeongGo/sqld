package kr.sqld.study

/** Display-only annotations. Keys are exact source strings; edited content never inherits stale spans. */
internal data class BodyTextOverride(
    val strong:List<String> = emptyList(),
    val paragraphStarts:List<String> = emptyList(),
    val inlineCodes:List<String> = emptyList(),
    val softBreaks:List<String> = emptyList()
)
internal data class BodyTextPlan(val text:String,val paragraphs:List<IntRange>,val strong:List<IntRange>,val code:List<IntRange>,val active:List<IntRange>)

internal object BodyTextRules {
    private val codeWord=Regex("(?<![A-Za-z0-9_])[A-Z][A-Z0-9_]*(?:\\.[A-Z][A-Z0-9_]*)*")
    private val notCode=setOf("SQL","DB","DBMS","ERD","ANSI","ACID","DDL","DML","DCL","TCL","PDF","JAVA")
    private fun identifierChar(char:Char)=char in 'a'..'z'||char in 'A'..'Z'||char in '0'..'9'||char=='_'
    fun firstPhraseIndex(text:String,phrase:String):Int {
        if(phrase.isBlank())return -1
        var at=text.indexOf(phrase)
        while(at>=0){
            val end=at+phrase.length
            val validStart=!identifierChar(phrase.first())||at==0||!identifierChar(text[at-1])
            val validEnd=!identifierChar(phrase.last())||end==text.length||!identifierChar(text[end])
            if(validStart&&validEnd)return at
            at=text.indexOf(phrase,at+1)
        }
        return -1
    }
    private fun firstRanges(text:String,phrases:List<String>):List<IntRange> {
        val result=mutableListOf<IntRange>()
        phrases.filter(String::isNotBlank).distinct().forEach { phrase ->
            val at=firstPhraseIndex(text,phrase)
            if(at>=0){
                val range=at until at+phrase.length
                if(result.none{it.first<=range.last&&range.first<=it.last})result+=range
            }
        }
        return result.sortedBy{it.first}
    }
    fun plan(source:String,emphasis:List<String> = emptyList(),inlineCodes:List<String> = emptyList(),active:List<String> = emptyList(),preserveSource:Boolean=false):BodyTextPlan {
        val override=BodyTextOverrides.entries[source]
        // Never trim or collapse general whitespace: quotes, examples and transcripts are data too.
        var text=source
        if(!preserveSource)override?.softBreaks.orEmpty().forEach{fragment->
            if(fragment.contains('\n')&&source.indexOf(fragment)==source.lastIndexOf(fragment))
                text=text.replace(fragment,fragment.replace('\n',' '))
        }
        val breaks=if(preserveSource)emptyList() else override?.paragraphStarts.orEmpty().mapNotNull{start->
            text.indexOf(start).takeIf{it>0&&it==text.lastIndexOf(start)}
        }
        val boundaries=(listOf(0,text.length)+breaks+if(preserveSource)emptyList()else Regex("\\n[ \\t]*\\n+").findAll(text).flatMap{listOf(it.range.first,it.range.last+1)}.toList()).distinct().sorted()
        val paragraphs=boundaries.zipWithNext().mapNotNull{(start,end)->
            var a=start;var b=end
            // Only whitespace at an explicit paragraph boundary is represented by the paragraph gap.
            if(!preserveSource){while(a<b&&text[a].isWhitespace())a++;while(b>a&&text[b-1].isWhitespace())b--}
            if(a<b)a until b else null
        }
        val strong=if(override!=null)firstRanges(text,override.strong)else firstRanges(text,emphasis).take(3)
        val code=(codeWord.findAll(text).filter{it.value !in notCode&&it.value.length>1}.map{it.range}.toList()+firstRanges(text,inlineCodes+override?.inlineCodes.orEmpty())).distinct()
        // Blue is reserved for a direct connection to the current SQL fragment, once per phrase.
        val focused=firstRanges(text,active.take(2))
        return BodyTextPlan(text,paragraphs,strong,code,focused)
    }
}
