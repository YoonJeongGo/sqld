package kr.sqld.study

import org.junit.Assert.*
import org.junit.Test
import java.io.File

class SqlWalkthroughTest {
    private fun question()=Question(
        id="reader-test",subjectId="sql",topicId="C",objectiveIds=listOf("S02"),familyId="reader-test-family",
        kind="application",title="조건을 읽기",stem="현재 입력의 결과를 고르세요.",
        choices=listOf(Choice("a","1","조건을 통과"),Choice("b","0","조건을 제외")),
        correctChoiceIds=listOf("a"),explanation=Explanation("기존 해설",steps=emptyList(),memory="원문 보존",relatedNoteId="note-S02"),
        sql="SELECT x FROM T WHERE x=1",tables=listOf(DataTable("T",listOf("x"),listOf(listOf("1")))),dialect="Oracle",dialectVersion="19c")

    @Test fun sameIdWithChangedSqlTablesChoicesOrConditionsRejectsOldMaterial(){
        val original=question();val source=WalkSource.from(original)
        assertTrue(source.matches(original))
        val changed=listOf(
            original.copy(sql="SELECT x FROM T WHERE x=2"),
            original.copy(tables=listOf(DataTable("T",listOf("x"),listOf(listOf("2"))))),
            original.copy(stem="입력 조건을 바꾼 문제"),original.copy(version=2),
            original.copy(choices=listOf(original.choices[0].copy(text="새 보기"),original.choices[1])),
            original.copy(correctChoiceIds=listOf("b")),original.copy(dialectVersion="23c")
        )
        changed.forEach{assertFalse(source.matches(it));assertNotEquals(source.fingerprint(),WalkSource.from(it).fingerprint())}
        assertEquals(source.fingerprint(),WalkSource.from(original.copy()).fingerprint())
    }

    @Test fun literalFocusKeepsExactOccurrenceAndRejectsMissingOrNegativeRanges(){
        val sql="SELECT 'FROM T' AS label FROM T WHERE x=1"
        val ranges=WalkthroughRules.ranges(sql,listOf(CodeFocus("FROM T",1),CodeFocus("x=1")))
        assertEquals(sql.lastIndexOf("FROM T"),ranges[0].first)
        assertEquals("FROM T",sql.substring(ranges[0]))
        assertEquals("x=1",sql.substring(ranges[1]))
        assertTrue(runCatching{WalkthroughRules.ranges(sql,listOf(CodeFocus("FROM T",2)))}.isFailure)
        assertTrue(runCatching{WalkthroughRules.ranges(sql,listOf(CodeFocus("",0)))}.isFailure)
        assertTrue(runCatching{WalkthroughRules.ranges(sql,listOf(CodeFocus("x=1",-1)))}.isFailure)
    }

    @Test fun invalidCellAnchorAndDuplicateStepIdsAreRejected(){
        val source=WalkSource.from(question())
        val step=WalkStep("step-1","현재 행","x=1을 확인합니다.",listOf(CodeFocus("x=1")),listOf("x=1"),
            DataTable("학습용",listOf("x"),listOf(listOf("1"))),listOf(FocusCell(0,0)))
        val walk=SqlWalkthrough("reader-test",source,"논리 흐름",listOf(step))
        WalkthroughRules.validate(walk)
        val invalidCell=walk.copy(steps=listOf(step.copy(focusCells=listOf(FocusCell(1,0)))))
        val duplicate=walk.copy(steps=listOf(step,step))
        val absentText=walk.copy(steps=listOf(step.copy(highlights=listOf("없는 표현"))))
        assertTrue(runCatching{WalkthroughRules.validate(invalidCell)}.isFailure)
        assertTrue(runCatching{WalkthroughRules.validate(duplicate)}.isFailure)
        assertTrue(runCatching{WalkthroughRules.validate(absentText)}.isFailure)
    }

    @Test fun everyBundledDocumentDecodesAndMatchesItsExactOriginalQuestion(){
        val assets=listOf(File("src/main/assets"),File("app/src/main/assets")).first{it.resolve("content-pack.json").isFile}
        val pack=Codec.decodeFromString<ContentPack>(assets.resolve("content-pack.json").readText())
        val index=Codec.decodeFromString<WalkIndex>(assets.resolve("sql-walkthroughs/index.json").readText())
        assertEquals(133,index.entries.size)
        assertEquals(index.entries.size,index.entries.map{it.questionId}.distinct().size)
        index.entries.forEach{ref->
            val material=Codec.decodeFromString<SqlWalkthrough>(assets.resolve("sql-walkthroughs/${ref.file}").readText())
            WalkthroughRules.validate(material)
            assertTrue(ref.questionId,material.source.matches(pack.questions.single{it.id==ref.questionId}))
            assertFalse(material.verification.oracleEngineExecuted)
            material.steps.forEach{step->
                listOf("FROM","GROUP BY","ORDER BY").forEach{clause->
                    if(step.title.startsWith("$clause ·"))assertTrue("${ref.questionId}: ${step.title}",step.codeFocus.any{it.needle.startsWith("$clause ")})
                }
            }
        }
        assertEquals(1,index.learningExamples.size)
        index.learningExamples.forEach{ref->WalkthroughRules.validate(Codec.decodeFromString(assets.resolve("sql-walkthroughs/${ref.file}").readText()))}
    }
}
