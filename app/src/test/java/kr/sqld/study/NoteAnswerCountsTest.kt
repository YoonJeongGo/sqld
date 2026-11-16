package kr.sqld.study

import org.junit.Assert.*
import org.junit.Test

class NoteAnswerCountsTest {
    private fun question(id:String,kind:String="recall",objectives:List<String> = listOf("M01"))=Question(
        id=id,version=2,subjectId="model",topicId="A",objectiveIds=objectives,familyId="family-$id",kind=kind,
        title=id,stem=id,choices=listOf(Choice("a","답","이유")),correctChoiceIds=listOf("a"),
        explanation=Explanation("이유",steps=emptyList(),memory="요약",relatedNoteId="note-M01"))

    private fun answer(id:String,questionId:String,version:Int=2,outcome:String="correct",helped:Boolean=false)=Submission(
        id,"session",questionId,version,listOf("a"),listOf("a"),outcome,helped,"",10,10,"v1","exam",false)

    /** Independent copy of the note-row calculation before optimization. */
    private fun previousCounts(pack:ContentPack,submissions:List<Submission>,objectives:List<String>):Map<String,NoteAnswerCounts> =
        objectives.associateWith { objective ->
            val records=submissions.filter { record -> record.outcome=="correct" && !record.helped &&
                pack.questions.any { question -> question.id==record.questionId && objective in question.objectiveIds } }
            NoteAnswerCounts(
                records.count { record -> pack.questions.any { it.id==record.questionId && it.kind=="recall" } },
                records.count { record -> pack.questions.any { it.id==record.questionId && it.kind=="application" } })
        }

    @Test fun preservesHistoricalCountsWithoutApplyingMasteryOrAvailabilityRules(){
        val recall=question("recall",objectives=listOf("M01","M01","S01"))
        val application=question("application","application")
        val hidden=question("hidden").copy(status="draft",verification="quarantined")
        val reservedRecall=question("reserved-recall").copy(mockSetId="mock-1")
        val mock=question("mock","mock").copy(mockSetId="mock-1")
        val pack=ContentPack(questions=listOf(recall,application,hidden,reservedRecall,mock))
        val records=listOf(
            answer("old","recall",version=1),answer("repeat","recall"),answer("apply","application"),
            answer("hidden-answer","hidden"),answer("reserved-answer","reserved-recall"),answer("mock-answer","mock"),
            answer("helped","recall",helped=true),answer("wrong","application",outcome="wrong"),
            answer("unanswered","application",outcome="unanswered"),answer("missing","removed-question"))
        val state=StudyState(submissions=records,issues=listOf(ContentIssue("issue","recall","v1","제외",true,1)))
        val before=previousCounts(pack,state.submissions,listOf("M01","S01","empty"))
        val after=StudyGuide.noteAnswerCounts(pack,state.submissions)
        assertEquals(before,before.keys.associateWith { after[it]?:NoteAnswerCounts() })
        assertEquals(NoteAnswerCounts(4,1),after["M01"])
        assertEquals(NoteAnswerCounts(2,0),after["S01"])
        assertNull(after["empty"])
        assertEquals(records,state.submissions)
    }

    private class CountedList<T>(private val values:List<T>):AbstractList<T>() {
        var reads=0L
        override val size get()=values.size
        override fun get(index:Int):T { reads++;return values[index] }
    }

    @Test fun largeHistoryMatchesPreviousCountsWithOnePassAndReportsMedianTiming(){
        val objectiveIds=(0 until 41).map { "objective-$it" }
        val questions=(0 until 661).map { index -> question("question-$index",if(index%2==0)"recall"else"application",
            listOf(objectiveIds[index%objectiveIds.size])) }
        val submissions=(0 until 20_000).map { index -> answer("submission-$index",questions[index%questions.size].id,
            version=if(index%5==0)1 else 2,outcome=if(index%4==0)"wrong"else"correct",helped=index%7==0) }
        val countedQuestions=CountedList(questions)
        val countedSubmissions=CountedList(submissions)
        val pack=ContentPack(questions=countedQuestions)
        val expected=previousCounts(pack,countedSubmissions,objectiveIds)
        val beforeQuestionReads=countedQuestions.reads
        val beforeSubmissionReads=countedSubmissions.reads
        countedQuestions.reads=0;countedSubmissions.reads=0
        val actual=StudyGuide.noteAnswerCounts(pack,countedSubmissions)
        assertEquals(expected,actual)
        assertEquals(questions.size.toLong(),countedQuestions.reads)
        assertEquals(submissions.size.toLong(),countedSubmissions.reads)
        assertTrue(beforeQuestionReads>countedQuestions.reads)
        assertTrue(beforeSubmissionReads>countedSubmissions.reads)

        // Host-JVM observation only: no device speed claim or flaky wall-clock threshold.
        val plainPack=pack.copy(questions=questions)
        fun medianMillis(block:()->Map<String,NoteAnswerCounts>):Double {
            assertEquals(expected,block())
            return List(3){
                val start=System.nanoTime()
                val result=block()
                val elapsed=(System.nanoTime()-start)/1_000_000.0
                assertEquals(expected,result)
                elapsed
            }.sorted()[1]
        }
        val before=medianMillis { previousCounts(plainPack,submissions,objectiveIds) }
        val after=medianMillis { StudyGuide.noteAnswerCounts(plainPack,submissions) }
        println("NOTE_COUNTS_BENCHMARK questions=${questions.size} submissions=${submissions.size} objectives=${objectiveIds.size} " +
            "oldQuestionReads=$beforeQuestionReads newQuestionReads=${countedQuestions.reads} " +
            "oldSubmissionReads=$beforeSubmissionReads newSubmissionReads=${countedSubmissions.reads} " +
            "oldMedianMs=$before newMedianMs=$after")
    }
}
