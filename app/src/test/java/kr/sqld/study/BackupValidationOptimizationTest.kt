package kr.sqld.study

import org.junit.Assert.*
import org.junit.Test

/** Repeated question IDs in different snapshots must resolve within their own session. */
class BackupValidationOptimizationTest {
    private fun history(sessionCount:Int=24,questionCount:Int=20):StudyState {
        val sessions=(0 until sessionCount).map { sessionIndex ->
            val sessionId="session-$sessionIndex"
            val correct=if(sessionIndex%2==0)"a"else"b"
            val items=(0 until questionCount).map { questionIndex ->
                val questionId="question-$questionIndex"
                val question=Question(questionId,version=sessionIndex+1,subjectId="sql",topicId="test",objectiveIds=listOf("S01"),
                    familyId=questionId,kind="application",title="검증",stem="검증",
                    choices=listOf("a","b","c","d").map{Choice(it,it,"이유")},correctChoiceIds=listOf(correct),
                    explanation=Explanation("해설",steps=listOf(ExplanationStep("단계","설명")),memory="기억",relatedNoteId="note-S01"))
                val order=if(sessionIndex%2==0)listOf("a","b","c","d")else listOf("d","c","b","a")
                SessionItem(question,order,draft=listOf(correct),submissionId="$sessionId:$questionId")
            }
            QuizSession(sessionId,"검증","batch",items,"snapshot-$sessionIndex",ExamSpec(),1_000,42,submittedAt=2_000)
        }
        val submissions=sessions.flatMap { session ->session.items.map { item ->
            Submission(item.submissionId!!,session.id,item.question.id,item.question.version,item.draft,item.choiceOrder,
                "correct",false,"sure",123,2_000,session.contentVersion,session.examSpec.id,true)
        } }
        return StudyState(sessions=sessions,submissions=submissions)
    }
    private fun rejects(state:StudyState){assertThrows(Exception::class.java){BackupCodec.validate(state)}}

    @Test fun sessionScopedLookupPreservesDifferentVersionsAnswersAndChoiceOrders() {
        val state=history()
        BackupCodec.validate(state)
        assertEquals(state,BackupCodec.decode(BackupCodec.encode(state,123)))
        assertEquals(480,state.submissions.size)
    }

    @Test fun duplicateSessionOrItemCannotBeHiddenByIndexOverwrite() {
        val state=history(2,2)
        rejects(state.copy(sessions=state.sessions+state.sessions.first()))
        val first=state.sessions.first()
        rejects(state.copy(sessions=listOf(first.copy(items=first.items+first.items.first()))+state.sessions.drop(1)))
    }

    @Test fun wrongSessionReferencesAndOrphanSubmissionsRemainRejected() {
        val state=history(2,2)
        rejects(state.copy(submissions=state.submissions.mapIndexed{i,r->if(i==0)r.copy(sessionId="missing")else r}))
        rejects(state.copy(submissions=state.submissions.mapIndexed{i,r->if(i==0)r.copy(sessionId=state.sessions.last().id)else r}))
        rejects(state.copy(submissions=state.submissions+state.submissions.first().copy(id="orphan",questionId="missing")))
    }

    @Test fun indexedLookupStillChecksImmutableGradingSnapshot() {
        val state=history(2,2)
        val first=state.submissions.first()
        listOf(first.copy(questionVersion=99),first.copy(outcome="wrong"),first.copy(choiceOrder=first.choiceOrder.reversed())).forEach{changed->
            rejects(state.copy(submissions=listOf(changed)+state.submissions.drop(1)))
        }
    }
}
