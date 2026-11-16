package kr.sqld.study

import java.io.File
import kotlinx.serialization.json.*
import org.junit.Assert.*
import org.junit.Test

class BodyTextRulesTest {
    private val assets=listOf(File("src/main/assets"),File("app/src/main/assets")).first{it.resolve("course-pack.json").isFile}
    private fun strings(value:JsonElement):List<String> = when(value){
        is JsonObject->value.values.flatMap(::strings)
        is JsonArray->value.flatMap(::strings)
        is JsonPrimitive->if(value.isString)listOf(value.content)else emptyList()
        else->emptyList()
    }
    @Test fun metadataRefersOnlyToExactExistingTextAndUniqueParagraphBoundaries(){
        val sources=assets.walkTopDown().filter{it.isFile&&it.extension=="json"}.flatMap{strings(Json.parseToJsonElement(it.readText())).asSequence()}.toSet()
        assertTrue(BodyTextOverrides.entries.isNotEmpty())
        BodyTextOverrides.entries.forEach{(source,rule)->
            assertTrue("Unknown source: $source",source in sources)
            (rule.strong+rule.inlineCodes+rule.paragraphStarts+rule.softBreaks).forEach{assertTrue("Missing phrase: $it in $source",it.isNotBlank()&&it in source)}
            rule.paragraphStarts.forEach{assertTrue(source.indexOf(it)>0);assertEquals(source.indexOf(it),source.lastIndexOf(it))}
            val plan=BodyTextRules.plan(source)
            assertEquals("Body characters changed",source.filterNot(Char::isWhitespace),plan.paragraphs.joinToString(""){plan.text.substring(it.first,it.last+1)}.filterNot(Char::isWhitespace))
        }
    }
    @Test fun sqlLikeWhitespaceQuotesAndMaskedPhonesAreNeverMarkdown(){
        val source="NAME은 ' A B '이고 PHONE은 '010-****-1003'이다.\nSELECT  'AB', ' A B '\n  FROM T;"
        val plan=BodyTextRules.plan(source,listOf("NAME"))
        assertEquals(source,plan.text)
        assertEquals(source,plan.paragraphs.joinToString(""){plan.text.substring(it.first,it.last+1)})
        assertTrue(plan.text.contains("010-****-1003"))
    }
    @Test fun repeatedTermIsEmphasizedOnceAndPlainProseHasNoBlue(){
        val source="외래키는 연결이다. 외래키를 다시 본다."
        val plan=BodyTextRules.plan(source,listOf("외래키","외래키"))
        assertEquals(listOf(0..2),plan.strong)
        assertTrue(plan.active.isEmpty())
        assertEquals(1,BodyTextRules.plan(source,active=listOf("외래키")).active.size)
    }
    @Test fun nativeNoteProjectionKeepsOriginalQuotesAndWhitespaceExactly(){
        BodyTextOverrides.entries.keys.forEach{source->
            val plan=BodyTextRules.plan(source,preserveSource=true)
            assertEquals(source,plan.text)
            assertEquals(source,plan.paragraphs.joinToString(""){source.substring(it.first,it.last+1)})
            plan.strong.forEach{assertTrue(source.substring(it.first,it.last+1) in source)}
        }
    }
    @Test fun modifiedSourceDoesNotInheritOldAuthoredParagraphs(){
        val source=BodyTextOverrides.entries.entries.first{it.value.paragraphStarts.isNotEmpty()}.key
        val changed=source+" 문장이 바뀌었다."
        val plan=BodyTextRules.plan(changed)
        assertTrue(plan.strong.isEmpty())
        assertEquals(changed,plan.text)
    }
    @Test fun identifiersAreNotHighlightedInsideDifferentColumnNames(){
        val text="e.id와 e.d, e.pid와 id를 비교한다."
        assertEquals(text.indexOf("e.d")+2,BodyTextRules.firstPhraseIndex(text,"d"))
        assertEquals(text.indexOf("e.id")+2,BodyTextRules.firstPhraseIndex(text,"id"))
        assertEquals(-1,BodyTextRules.firstPhraseIndex("e.pid","id"))
        assertEquals(-1,BodyTextRules.firstPhraseIndex("PHONE_NUMBER","NAME"))
    }
    @Test fun nativeSelectionAcrossDisplayParagraphsMapsBackToExactRawQuote(){
        BodyTextOverrides.entries.filterValues{it.paragraphStarts.isNotEmpty()}.forEach{(source,rule)->
            val display=NoteTextProjection.from(source)
            assertEquals(source,display.sourceQuote(0,display.text.length))
            rule.paragraphStarts.forEach{phrase->
                val at=source.indexOf(phrase)
                val raw=(at-8).coerceAtLeast(0) until at+phrase.length
                val range=display.displayRange(raw)
                assertEquals(source.substring(raw.first,raw.last+1),display.sourceQuote(range.first,range.last+1))
                assertTrue(display.text.contains("\n\n$phrase"))
            }
        }
        val quoted="SELECT  ' A B ', 'AB'\n  FROM T;"
        assertEquals(quoted,NoteTextProjection.from(quoted).text)
    }
}
