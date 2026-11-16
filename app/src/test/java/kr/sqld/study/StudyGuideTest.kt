package kr.sqld.study

import org.junit.Assert.*
import org.junit.Test

class StudyGuideTest {
    private fun note(id:String,version:Int=1)=Note("note-$id",version,id,id,"요약",blocks=listOf(ContentBlock("$id-old","remember","암기","기존 문장")))
    @Test fun originalVersionTwoNotesStayReadWhileNewVersionThreeNeedsReview(){
        val unchanged=note("S11",2);val expanded=note("S12",3)
        val state=StudyState(notes=listOf(NoteProgress(unchanged.id,true),NoteProgress(expanded.id,true)))
        val pack=ContentPack(notes=listOf(unchanged,expanded),legacyNoteVersions=mapOf(unchanged.id to 2,expanded.id to 2))
        val migrated=StudyEngine.reconcile(state,pack)
        assertTrue(StudyGuide.readCurrent(unchanged,migrated))
        assertFalse(StudyGuide.readCurrent(expanded,migrated))
        assertEquals(listOf(2,2),migrated.notes.map{it.readVersion})
        assertEquals(migrated,StudyEngine.reconcile(migrated,pack))
    }
    @Test fun contentUpgradeKeepsLegacyReadingAndAnnotationsButRequestsNewMaterial(){
        val legacy=Codec.decodeFromString<NoteProgress>("""{"noteId":"note-M01","read":true,"scroll":180,"collapsed":["old"]}""")
        val old=note("M01");val updated=old.copy(version=2,blocks=old.blocks+ContentBlock("new","example","보강","추가 내용"))
        val ann=Annotation("a",old.id,"M01-old","기존 문장","보존 메모","highlight",1)
        val state=StudyState(notes=listOf(legacy),annotations=listOf(ann))
        assertTrue(StudyGuide.readCurrent(old,state))
        assertFalse(StudyGuide.readCurrent(updated,state))
        val reconciled=StudyEngine.reconcile(state,ContentPack(notes=listOf(updated)))
        assertEquals(legacy,reconciled.notes.single())
        assertFalse(reconciled.annotations.single().archived)
        assertEquals("보강 내용 확인 전",StudyGuide.readingLabel(updated,reconciled))
        assertTrue(StudyGuide.readCurrent(updated,state.copy(notes=listOf(legacy.copy(readVersion=2)))))
    }
    @Test fun recommendationRespectsPrerequisitesBeforeUnseenCoreAndTerminatesCycles(){
        val notes=listOf(note("S01"),note("S10"),note("S12"))
        val pack=ContentPack(notes=notes,objectives=listOf(Objective("S01","sql","C","기초"),Objective("S10","sql","C","조인",listOf("S01")),Objective("S12","sql","D","서브쿼리",listOf("S10"))),studyPriorities=listOf(StudyPriority("S01","foundation"),StudyPriority("S10","important"),StudyPriority("S12","core")))
        assertEquals("note-S01",StudyGuide.next(pack,StudyState())?.id)
        assertEquals("note-S10",StudyGuide.next(pack,StudyState(notes=listOf(NoteProgress("note-S01",true))))?.id)
        val cycle=pack.copy(objectives=pack.objectives.map{if(it.id=="S01")it.copy(prerequisites=listOf("S12"))else it})
        assertNotNull(StudyGuide.next(cycle,StudyState()))
    }
    @Test fun repeatedOldHelpedAndMockAnswersDoNotInflateCoreCoverage(){
        val q=Question("q",2,"sql","C",listOf("S01"),"family","recall","문제","문제",listOf(Choice("a","답","이유")),listOf("a"),Explanation("이유",steps=emptyList(),memory="암기",relatedNoteId="note-S01"))
        fun answer(id:String,help:Boolean=false,version:Int=2,questionId:String="q")=Submission(id,"s",questionId,version,listOf("a"),listOf("a"),"correct",help,"",10,10,"v","exam",true)
        val pack=ContentPack(notes=listOf(note("S01")),questions=listOf(q,q.copy(id="mock",kind="mock",mockSetId="mock-1")),studyPriorities=listOf(StudyPriority("S01","core")))
        val excluded=StudyState(submissions=listOf(answer("old",version=1),answer("help",help=true),answer("mock",questionId="mock")))
        assertEquals(0,StudyGuide.coreProgress(pack,excluded).recall)
        val valid=excluded.copy(submissions=excluded.submissions+listOf(answer("valid"),answer("repeat")))
        assertEquals(CoreProgress(1,0,1,0),StudyGuide.coreProgress(pack,valid))
    }
}
