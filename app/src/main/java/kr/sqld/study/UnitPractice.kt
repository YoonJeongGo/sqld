package kr.sqld.study

import kotlinx.serialization.Serializable

@Serializable data class UnitQuestionLink(val questionId:String,val lessonId:String,val type:String)
@Serializable data class UnitMockForm(val id:String,val number:Int,val questionIds:List<String>)
@Serializable data class UnitPracticePart(val id:String,val title:String,val reviewIds:List<String>,val forms:List<UnitMockForm>)
@Serializable data class UnitQuestionBank(val version:String="",val parts:List<UnitPracticePart> = emptyList(),val links:List<UnitQuestionLink> = emptyList(),val questions:List<Question> = emptyList(),val sources:List<SourceRecord> = emptyList()) {
    fun validate(base:ContentPack,course:CoursePack){
        require(parts.map{it.id}==course.parts.map{it.id})
        require(questions.map{it.id}.distinct().size==questions.size)
        require(links.map{it.questionId}.toSet()==questions.map{it.id}.toSet())
        require(links.size==questions.size)
        val ids=questions.associateBy{it.id};val lessonIds=course.lessons.map{it.id}.toSet()
        val baseIds=base.questions.map{it.id}.toSet();val linksById=links.associateBy{it.questionId}
        require(questions.none{it.id in baseIds})
        require(links.all{it.lessonId in lessonIds})
        parts.forEach{part->
            require(part.forms.size==3 && part.forms.map{it.number}==listOf(1,2,3))
            require(part.forms.all{it.id=="unit:${part.id}:${it.number}"&&it.questionIds.size==50&&it.questionIds.distinct().size==50})
            val assigned=part.reviewIds+part.forms.flatMap{it.questionIds}
            require(assigned.distinct().size==assigned.size)
            require(assigned.all{id->id in ids&&linksById.getValue(id).lessonId.startsWith(part.id+"-")})
            require(part.reviewIds.all{ids.getValue(it).mockSetId==null})
            part.forms.forEach{form->require(form.questionIds.all{ids.getValue(it).mockSetId==form.id})}
        }
        require(parts.flatMap{it.reviewIds+it.forms.flatMap{f->f.questionIds}}.toSet()==ids.keys)
        val noteIds=base.notes.map{it.id}.toSet();val objectiveIds=base.objectives.map{it.id}.toSet()
        questions.forEach{q->
            require(q.id.startsWith("unit-")&&q.status=="published"&&q.verification=="independent_ai_review")
            require(q.choices.size==4&&q.choices.map{it.id}.distinct().size==4&&q.choices.map{it.text}.distinct().size==4)
            require(q.correctChoiceIds.size==1&&q.correctChoiceIds.single() in q.choices.map{it.id})
            require(q.objectiveIds.isNotEmpty()&&q.objectiveIds.all{it in objectiveIds}&&q.explanation.relatedNoteId in noteIds)
            require(q.validationEvidence.any{it.startsWith("independent-review:")})
        }
    }
    fun questions(ids:List<String>,state:StudyState):List<Question>{
        val excluded=state.issues.filter{it.exclude}.map{it.contentId}.toSet()
        val byId=questions.associateBy{it.id}
        return ids.mapNotNull{byId[it]}.filter{it.id !in excluded}
    }
}

fun Question.isUnitQuestion()=id.startsWith("unit-")
fun QuizSession.isUnitMock()=mockSetId?.startsWith("unit:")==true

object UnitPractice {
    fun spec(partId:String,questions:List<Question>)=ExamSpec(id="unit-$partId-20261015",title="$partId 단원 연습 기준",checkedAt="2026-10-15",sourceIds=emptyList(),
        verification="original_unit_practice",modelCount=questions.count{it.subjectId=="model"},sqlCount=questions.count{it.subjectId=="sql"})
    fun validateSpec(session:QuizSession){
        val partId=session.mockSetId?.split(':')?.getOrNull(1)?:error("단원 정보 없음")
        require(partId in listOf("1-1","1-2","2-1","2-2","2-3"))
        require(session.mockSetId in (1..3).map{"unit:$partId:$it"})
        require(session.examSpec==spec(partId,session.items.map{it.question}))
        require(session.items.size==50&&session.items.all{it.question.isUnitQuestion()&&it.question.mockSetId==session.mockSetId})
        require(session.examSpec.modelCount+session.examSpec.sqlCount==50)
        require(session.items.count{it.question.subjectId=="model"}==session.examSpec.modelCount)
        require(session.items.count{it.question.subjectId=="sql"}==session.examSpec.sqlCount)
    }
    fun create(state:StudyState,pack:ContentPack,bank:UnitQuestionBank,partId:String,number:Int,now:Long,elapsed:Long,boot:Int,seed:Int):StudyState{
        // Called inside the repository transaction, so repeated taps cannot start parallel clocks.
        state.sessions.firstOrNull{it.mode=="strict"&&it.submittedAt==null}?.let{return state.copy(activeSessionId=it.id)}
        val part=bank.parts.first{it.id==partId};val form=part.forms.first{it.number==number}
        val questions=bank.questions(form.questionIds,state)
        require(questions.size==50){"제외된 문항이 있어 50문항 구성을 유지할 수 없습니다."}
        val created=StudyEngine.createSession(state,pack.copy(examSpec=spec(partId,questions)),questions,"strict","$partId ${part.title} · 단원 모의 $number",now,elapsed,boot,seed,form.id)
        // A focused unit test is never a diagnostic of the full SQLD exam.
        return created.copy(sessions=created.sessions.map{if(it.id==created.activeSessionId)it.copy(diagnosticEligible=false)else it})
    }
}
