package kr.sqld.study

import org.junit.Assert.*
import org.junit.Test
import java.time.LocalDate
import java.time.ZoneId
import kotlin.random.Random

/** Semantic fixtures intentionally use non-positional choice IDs. No production content answers. */
internal object EngineTestData {
    fun question(id:String="q", subject:String="sql", mock:String?=null, family:String=id):Question = Question(
        id=id, subjectId=subject, topicId=if(subject=="model")"A" else "C",
        objectiveIds=listOf(if(subject=="model")"M01" else "S02"), familyId=family,
        kind=if(mock==null)"application" else "mock", title="검증용", stem="검증용 독립 입력",
        choices=listOf(Choice("wrong-a","오답A","이유A"),Choice("right","정답","이유"),
            Choice("wrong-b","오답B","이유B"),Choice("wrong-c","오답C","이유C")),
        correctChoiceIds=listOf("right"),
        explanation=Explanation("이유",steps=listOf(ExplanationStep("단계","설명")),memory="기억",relatedNoteId="note"),
        mockSetId=mock
    )
    fun pack(questions:List<Question>,spec:ExamSpec=ExamSpec())=ContentPack(version="content-test-v1",examSpec=spec,questions=questions)
    fun start(questions:List<Question> = listOf(question()), state:StudyState=StudyState(), mode:String="batch",
              now:Long=day(1), elapsed:Long=10_000, boot:Int=7, seed:Int=42,
              spec:ExamSpec=ExamSpec(), mock:String?=null):StudyState =
        StudyEngine.createSession(state,pack(questions,spec),questions,mode,"검증",now,elapsed,boot,seed,mock)
    fun day(n:Int):Long=LocalDate.of(2026,9,n).atTime(12,0).atZone(ZoneId.systemDefault()).toInstant().toEpochMilli()
    fun session(state:StudyState)=state.sessions.first{it.id==state.activeSessionId}
    fun answer(state:StudyState,index:Int=0,choice:String="right")=
        StudyEngine.select(state,session(state).id,index,choice)
    fun grade(state:StudyState,index:Int=0,now:Long=day(1),unanswered:Boolean=false)=
        StudyEngine.grade(state,session(state).id,index,now,unanswered)
    fun strict(now:Long=day(1),elapsed:Long=10_000,boot:Int=7,prior:StudyState=StudyState()):StudyState {
        val spec=ExamSpec(modelCount=1,sqlCount=1,pointsPerQuestion=50,minutes=1)
        return start(listOf(question("m","model","mock-1"),question("s","sql","mock-1")),
            prior,"strict",now,elapsed,boot,spec=spec,mock="mock-1")
    }
}

class StudyEngineTest {
    @Test fun sixOfficialDraftScoreBoundaries() {
        data class Case(val m:Int,val s:Int,val points:Int,val mf:Boolean,val sf:Boolean,val pass:Boolean)
        val cases=listOf(Case(4,26,60,false,false,true),Case(4,25,58,false,false,false),
            Case(3,40,86,true,false,false),Case(10,15,50,false,true,false),
            Case(4,16,40,false,false,false),Case(10,40,100,false,false,true))
        cases.forEach { c ->
            val result=StudyEngine.score(c.m,c.s)
            assertEquals(c.points,result.points);assertEquals(c.mf,result.modelFail)
            assertEquals(c.sf,result.sqlFail);assertEquals(c.pass,result.passed)
        }
    }
    @Test fun numericScoreRejectsImpossibleCorrectCount() {
        assertThrows(IllegalArgumentException::class.java){StudyEngine.score(11,40)}
        assertThrows(IllegalArgumentException::class.java){StudyEngine.score(-1,0)}
    }
    @Test fun selectionIsOnlyADraftAndCanChangeBeforeExplicitGrading() {
        val state=EngineTestData.start()
        val changed=EngineTestData.answer(EngineTestData.answer(state,choice="wrong-a"))
        assertEquals(listOf("right"),EngineTestData.session(changed).items[0].draft)
        assertTrue(changed.submissions.isEmpty());assertTrue(changed.reviews.isEmpty())
        assertNull(EngineTestData.session(changed).items[0].submissionId)
    }
    @Test fun individualThenWholeSubmissionDoesNotCountOneWrongTwice() {
        val original=EngineTestData.start(listOf(EngineTestData.question("one"),EngineTestData.question("two")))
        var state=EngineTestData.answer(original,0,"wrong-a")
        state=EngineTestData.answer(state,1,"right")
        state=EngineTestData.grade(state,0)
        val first=state.submissions.single()
        val otherDraft=EngineTestData.session(state).items[1].draft
        assertEquals(listOf("right"),otherDraft)
        assertNull(EngineTestData.session(state).items[1].submissionId)
        state=StudyEngine.submit(state,EngineTestData.session(state).id,EngineTestData.day(1)+100)
        assertEquals(2,state.submissions.size)
        assertEquals(first,state.submissions.first{it.id==first.id})
        assertEquals(1,state.reviews.first{it.questionId=="one"}.wrongCount)
        val repeated=StudyEngine.submit(state,EngineTestData.session(state).id,EngineTestData.day(1)+200)
        assertEquals(state,repeated)
        assertEquals(state,StudyEngine.grade(state,EngineTestData.session(state).id,0,EngineTestData.day(1)+300))
    }
    @Test fun gradedDraftIsLockedAndRetryCreatesSeparateAttempt() {
        val first=EngineTestData.grade(EngineTestData.answer(EngineTestData.start(),choice="wrong-a"))
        val oldSubmission=first.submissions.single()
        assertThrows(IllegalArgumentException::class.java){
            StudyEngine.select(first,EngineTestData.session(first).id,0,"right")
        }
        val retry=EngineTestData.grade(EngineTestData.answer(EngineTestData.start(state=first)))
        assertEquals(2,retry.submissions.size)
        assertEquals(oldSubmission,retry.submissions.first())
        assertNotEquals(retry.submissions[0].sessionId,retry.submissions[1].sessionId)
        assertEquals(1,retry.reviews.single().wrongCount)
    }
    @Test fun unansweredRequiresExplicitIntentAndWholeSubmitRecordsZero() {
        val state=EngineTestData.start(listOf(EngineTestData.question("one"),EngineTestData.question("two")))
        assertThrows(IllegalArgumentException::class.java){EngineTestData.grade(state)}
        val single=EngineTestData.grade(state,unanswered=true)
        assertEquals("unanswered",single.submissions.single().outcome)
        assertTrue(single.submissions.single().choiceIds.isEmpty())
        val submitted=StudyEngine.submit(single,EngineTestData.session(single).id,EngineTestData.day(1))
        assertEquals(2,submitted.submissions.size)
        assertTrue(submitted.submissions.all{it.outcome=="unanswered"})
        assertTrue(submitted.reviews.all{it.wrongCount==1})
    }
    @Test fun explicitUnknownDiscardsExistingDraftWithoutPretendingItWasChosen() {
        val selected=EngineTestData.answer(EngineTestData.start())
        val state=EngineTestData.grade(selected,unanswered=true)
        assertTrue(state.submissions.single().choiceIds.isEmpty())
        assertEquals("unanswered",state.submissions.single().outcome)
    }
    @Test fun seededShufflePreservesChoiceIdentityAndReplayOrder() {
        val q=EngineTestData.question()
        val positions=mutableSetOf<Int>()
        (1..30).forEach { seed ->
            val state=EngineTestData.start(seed=seed)
            val same=EngineTestData.start(seed=seed)
            val order=EngineTestData.session(state).items.single().choiceOrder
            assertEquals(q.choices.map{it.id}.toSet(),order.toSet())
            assertEquals(order,EngineTestData.session(same).items.single().choiceOrder)
            positions+=order.indexOf("right")
            val graded=EngineTestData.grade(EngineTestData.answer(state))
            assertEquals("correct",graded.submissions.single().outcome)
            assertEquals(order,graded.submissions.single().choiceOrder)
        }
        assertTrue("Seeded shuffling must exercise multiple answer positions",positions.size>1)
    }
    @Test fun strictSessionRejectsMissingSubjectBalanceAndDuplicateItems() {
        val q=EngineTestData.question()
        assertThrows(IllegalArgumentException::class.java){EngineTestData.start(listOf(q,q))}
        assertThrows(IllegalArgumentException::class.java){
            EngineTestData.start(listOf(q.copy(mockSetId="mock-1",kind="mock")),mode="strict",mock="mock-1")
        }
    }
    @Test fun practiceSearchExcludesUnseenMocksDraftsQuarantineAndUserExcludedItems() {
        val good=EngineTestData.question("good")
        val excluded=EngineTestData.question("excluded")
        val pack=EngineTestData.pack(listOf(good,excluded,EngineTestData.question("reserved",mock="mock-1"),
            EngineTestData.question("draft").copy(verification="draft"),
            EngineTestData.question("quarantined").copy(status="quarantined")))
        val state=StudyState(issues=listOf(ContentIssue("issue","excluded","v","오류",true,1)))
        assertEquals(listOf("good"),StudyEngine.available(pack,state).map{it.id})
    }
    @Test fun exposedMockCanBeFoundForBookmarkAndReviewButUnseenSiblingStaysReserved() {
        val seen=EngineTestData.question("seen",mock="mock-1",family="shared-family")
        val unseen=EngineTestData.question("unseen",mock="mock-2",family="shared-family")
        val pack=EngineTestData.pack(listOf(seen,unseen,EngineTestData.question("practice")))
        val state=StudyState(
            exposures=listOf(Exposure("seen-record",seen.id,seen.familyId,"previous","seen",1)),
            bookmarks=listOf(Bookmark(seen.id,2)),
            reviews=listOf(ReviewState(seen.id,wrongCount=1,needsReview=true)))
        val available=StudyEngine.available(pack,state)
        assertEquals(listOf("seen","practice"),available.map{it.id})
        assertEquals(listOf("seen"),available.filter{q->state.bookmarks.any{it.id==q.id}}.map{it.id})
        assertEquals(listOf("seen"),available.filter{q->state.reviews.any{it.questionId==q.id}}.map{it.id})
        assertTrue("Reserved pool must not enter generic fresh-practice pack",pack.practice().none{it.kind=="mock"})
    }
    @Test fun exposureDoesNotBypassContentQuarantineDraftOrUserExclusion() {
        val questions=listOf(
            EngineTestData.question("quarantine",mock="mock-1").copy(status="quarantined"),
            EngineTestData.question("draft-status",mock="mock-1").copy(status="draft"),
            EngineTestData.question("draft-review",mock="mock-1").copy(verification="draft"),
            EngineTestData.question("excluded",mock="mock-1"))
        val state=StudyState(
            exposures=questions.map{Exposure("ex-${it.id}",it.id,it.familyId,"previous","seen",1)},
            issues=listOf(ContentIssue("issue","excluded","v","Excluded by user",true,2)))
        assertTrue(StudyEngine.available(EngineTestData.pack(questions),state).isEmpty())
    }
    @Test fun firstStrictSessionIsNewAndRetakeRemainsExposedAfterRestartSerialization() {
        val first=EngineTestData.strict()
        assertTrue(EngineTestData.session(first).diagnosticEligible)
        val restored=Codec.decodeFromString<StudyState>(Codec.encodeToString(StudyState.serializer(),first))
        val next=EngineTestData.strict(prior=restored)
        assertTrue(EngineTestData.session(next).repeat)
        assertFalse(EngineTestData.session(next).diagnosticEligible)
    }
    @Test fun priorNearFamilyExposureDisqualifiesFirstMockWithoutMarkingItAsRetake() {
        val state=StudyState(exposures=listOf(Exposure("earlier","variant","m","prior","seen",1)))
        val mock=EngineTestData.strict(prior=state)
        assertFalse(EngineTestData.session(mock).repeat)
        assertFalse(EngineTestData.session(mock).diagnosticEligible)
    }
    @Test fun strictHelpAndIndividualGradeAreBlockedUntilIrreversibleConversion() {
        var state=EngineTestData.answer(EngineTestData.strict())
        val id=EngineTestData.session(state).id
        assertThrows(IllegalArgumentException::class.java){StudyEngine.help(state,id,0,"note",EngineTestData.day(1))}
        assertThrows(IllegalArgumentException::class.java){StudyEngine.grade(state,id,0,EngineTestData.day(1))}
        state=StudyEngine.convert(state,id,EngineTestData.day(1))
        assertEquals(listOf("right"),EngineTestData.session(state).items.first().draft)
        assertEquals("mixed",EngineTestData.session(state).mode)
        assertFalse(EngineTestData.session(state).diagnosticEligible)
        state=StudyEngine.grade(state,id,0,EngineTestData.day(1)+1)
        assertTrue(state.submissions.single().helped)
    }
    @Test fun viewingExplanationAfterSubmissionCannotRetroactivelyChangeHelpFlag() {
        val state=EngineTestData.grade(EngineTestData.answer(EngineTestData.start()))
        val first=state.submissions.single()
        assertFalse(first.helped);assertTrue(first.firstEver)
        val exposed=StudyEngine.help(state,first.sessionId,0,"explanation",first.submittedAt+1)
        assertEquals(first,exposed.submissions.single())
        assertEquals(exposed,StudyEngine.help(exposed,first.sessionId,0,"explanation",first.submittedAt+2))
    }
    @Test fun helpBeforeSubmissionIsRecordedAndNotTreatedAsIndependentMastery() {
        var state=EngineTestData.answer(EngineTestData.start())
        state=StudyEngine.help(state,EngineTestData.session(state).id,0,"hint",EngineTestData.day(1)-1)
        state=EngineTestData.grade(state)
        assertTrue(state.submissions.single().helped)
        assertTrue(state.reviews.single().needsReview)
        assertEquals(0,state.reviews.single().stage)
    }
    @Test fun familyExposureAndExactRepeatAreNotCountedAsFirstEver() {
        val first=EngineTestData.grade(EngineTestData.answer(EngineTestData.start()))
        val repeated=EngineTestData.grade(EngineTestData.answer(EngineTestData.start(state=first)))
        assertFalse(repeated.submissions.last().firstEver)
        val related=EngineTestData.start(listOf(EngineTestData.question("variant",family="q")),state=first)
        val graded=EngineTestData.grade(EngineTestData.answer(related))
        assertFalse(graded.submissions.last().firstEver)
    }
    @Test fun sameDayRepeatDoesNotAdvanceSpacingButDifferentDayDoes() {
        var state=EngineTestData.grade(EngineTestData.answer(EngineTestData.start()))
        assertEquals(0,state.reviews.single().stage)
        state=EngineTestData.grade(EngineTestData.answer(EngineTestData.start(state=state)),now=EngineTestData.day(1)+1_000)
        assertEquals(0,state.reviews.single().stage)
        state=EngineTestData.grade(EngineTestData.answer(EngineTestData.start(state=state,now=EngineTestData.day(2))),now=EngineTestData.day(2))
        assertEquals(1,state.reviews.single().stage)
        assertEquals(EngineTestData.day(2)+3*86_400_000L,state.reviews.single().dueAt)
        assertEquals(1,state.reviews.size)
    }
    @Test fun wrongHistorySurvivesLaterSuccessAndGuessNeedsReview() {
        var state=EngineTestData.grade(EngineTestData.answer(EngineTestData.start(),choice="wrong-b"))
        state=EngineTestData.grade(EngineTestData.answer(EngineTestData.start(state=state,now=EngineTestData.day(2))),now=EngineTestData.day(2))
        assertEquals(1,state.reviews.single().wrongCount)
        assertFalse(state.reviews.single().needsReview)
        assertEquals("wrong",state.submissions.first().outcome)
        var guessed=EngineTestData.answer(EngineTestData.start(state=state))
        guessed=StudyEngine.confidence(guessed,EngineTestData.session(guessed).id,0,"guess")
        guessed=EngineTestData.grade(guessed)
        assertTrue(guessed.reviews.single().needsReview)
    }
    @Test fun shorteningIntervalsAfterTodaysReviewKeepsGradingAndHistoryValid() {
        var state=StudyState()
        (1..3).forEach { day ->
            state=EngineTestData.grade(EngineTestData.answer(EngineTestData.start(state=state,now=EngineTestData.day(day))),now=EngineTestData.day(day))
        }
        assertEquals(2,state.reviews.single().stage)
        val history=state.submissions
        listOf(listOf(1),listOf(1,3)).forEach { intervals ->
            val edited=state.copy(settings=state.settings.copy(intervals=intervals))
            val now=EngineTestData.day(3)+1_000
            val graded=EngineTestData.grade(EngineTestData.answer(EngineTestData.start(state=edited,now=now)),now=now)
            assertEquals(intervals.lastIndex,graded.reviews.single().stage)
            assertEquals(now+intervals.last()*86_400_000L,graded.reviews.single().dueAt)
            assertEquals(history,graded.submissions.take(history.size))
            assertEquals("correct",graded.submissions.last().outcome)
            assertEquals(4,graded.submissions.size)
            BackupCodec.validate(graded)
        }
    }
    @Test fun bookmarkRemovalDoesNotEraseHistoryOrChangeStartedSessionItems() {
        var state=EngineTestData.grade(EngineTestData.answer(EngineTestData.start(),choice="wrong-a"))
        state=StudyEngine.bookmark(state,"q",1)
        val session=EngineTestData.session(state)
        val unstarred=StudyEngine.bookmark(state,"q",2)
        assertTrue(unstarred.bookmarks.isEmpty())
        assertEquals(state.reviews,unstarred.reviews);assertEquals(state.submissions,unstarred.submissions)
        assertEquals(session,EngineTestData.session(unstarred))
    }
    @Test fun strictTimerUsesMonotonicClockAcrossProcessRestart() {
        val state=EngineTestData.strict()
        val restored=Codec.decodeFromString<StudyState>(Codec.encodeToString(StudyState.serializer(),state))
        val next=StudyEngine.tick(restored,EngineTestData.session(restored).id,EngineTestData.day(1)+30_000,40_000,7)
        assertEquals(30_000L,EngineTestData.session(next).remainingMillis)
        assertNull(EngineTestData.session(next).submittedAt)
    }
    @Test fun rebootUsesNonnegativeWallElapsedAndStillExpires() {
        val state=EngineTestData.strict()
        val next=StudyEngine.tick(state,EngineTestData.session(state).id,EngineTestData.day(1)+61_000,500,8)
        assertEquals(0L,EngineTestData.session(next).remainingMillis)
        assertNotNull(EngineTestData.session(next).submittedAt)
        assertEquals(2,next.submissions.size)
        assertTrue(next.submissions.all{it.outcome=="unanswered"})
    }
    @Test fun backwardWallClockCannotExtendExamAndFlagsDiagnosticAnomaly() {
        val state=EngineTestData.strict()
        val next=StudyEngine.tick(state,EngineTestData.session(state).id,EngineTestData.day(1)-10_000,20_000,7)
        assertEquals(0L,EngineTestData.session(next).remainingMillis)
        assertTrue(EngineTestData.session(next).clockAnomaly)
        assertFalse(EngineTestData.session(next).diagnosticEligible)
        assertNotNull(EngineTestData.session(next).submittedAt)
    }
    @Test fun largeForwardClockJumpAlsoFlagsDiagnosticAnomaly() {
        val state=EngineTestData.strict()
        val next=StudyEngine.tick(state,EngineTestData.session(state).id,EngineTestData.day(1)+500_000,11_000,7)
        assertTrue(EngineTestData.session(next).clockAnomaly)
        assertFalse(EngineTestData.session(next).diagnosticEligible)
    }
    @Test fun timeoutAndRepeatedTicksSubmitEveryQuestionExactlyOnce() {
        val state=EngineTestData.answer(EngineTestData.strict())
        val id=EngineTestData.session(state).id
        val expired=StudyEngine.tick(state,id,EngineTestData.day(1)+60_001,70_001,7)
        val retried=StudyEngine.tick(expired,id,EngineTestData.day(1)+90_000,100_000,7)
        assertEquals(expired,retried);assertEquals(2,expired.submissions.size)
        assertEquals(1,expired.submissions.count{it.outcome=="correct"})
        assertEquals(1,expired.submissions.count{it.outcome=="unanswered"})
        assertEquals(2,expired.reviews.size)
    }
    @Test fun practiceTimerDoesNotExpireOrChangeDraftInBackground() {
        val state=EngineTestData.answer(EngineTestData.start())
        assertEquals(state,StudyEngine.tick(state,EngineTestData.session(state).id,EngineTestData.day(20),Long.MAX_VALUE,22))
    }
    @Test fun contentUpdateKeepsSessionQuestionVersionChoicesAndExamSpecSnapshot() {
        val original=EngineTestData.answer(EngineTestData.start())
        val oldSession=EngineTestData.session(original)
        val newPack=EngineTestData.pack(listOf(EngineTestData.question().copy(version=2)),ExamSpec(version=2,minutes=100)).copy(version="v2")
        val reconciled=StudyEngine.reconcile(original,newPack)
        assertEquals(oldSession,EngineTestData.session(reconciled))
        assertEquals("v2",reconciled.contentVersion)
    }
    @Test fun annotationsReconnectByQuoteAndArchiveOrphansWithoutDeletingMemo() {
        val annotations=listOf(
            Annotation("stable","n","old","같은 문장","첫 메모","highlight",1),
            Annotation("moved","n","gone","이동 문장","둘째 메모","underline",2),
            Annotation("orphan","n","missing","삭제된 문장","보존 메모","note",3))
        val note=Note("n",2,"M01","노트","요약",blocks=listOf(
            ContentBlock("old","explain","블록","같은 문장 뒤에 추가"),
            ContentBlock("new","explain","새 블록","이동 문장")))
        val state=StudyEngine.reconcile(StudyState(annotations=annotations),ContentPack(version="v2",notes=listOf(note)))
        assertEquals("old",state.annotations[0].blockId);assertFalse(state.annotations[0].archived)
        assertEquals("new",state.annotations[1].blockId);assertFalse(state.annotations[1].archived)
        assertTrue(state.annotations[2].archived);assertEquals("보존 메모",state.annotations[2].memo)
        assertEquals(3,state.annotations.size)
    }
    @Test fun SQLComparisonPreservesDuplicatesNullTypesAndColumnPosition() {
        val rows:List<List<Any?>> = listOf(listOf(1,null),listOf(1,null),listOf(2,""))
        assertTrue(StudyEngine.equalRows(rows,rows.reversed(),false))
        assertFalse(StudyEngine.equalRows(rows,rows.reversed(),true))
        assertFalse(StudyEngine.equalRows(rows,rows.distinct(),false))
        assertFalse(StudyEngine.equalRows(rows,listOf(listOf("1",null),listOf(1,null),listOf(2,"")),false))
        assertFalse(StudyEngine.equalRows(rows,listOf(listOf(null,1),listOf(1,null),listOf(2,"")),false))
        assertFalse(StudyEngine.equalRows(listOf(listOf<String?>(null)),listOf(listOf("")),false))
    }
    @Test fun fiftyQuestionSingleSubjectPracticeResultMustNotCrash() {
        var state=EngineTestData.start((1..50).map{EngineTestData.question("sql-$it")})
        repeat(50){state=EngineTestData.answer(state,it)}
        state=StudyEngine.submit(state,EngineTestData.session(state).id,EngineTestData.day(1))
        val result=StudyEngine.score(EngineTestData.session(state),state)
        assertEquals(50,result.sqlCorrect)
        assertEquals(50,result.sqlTotal)
        assertEquals(0,result.modelTotal)
        assertFalse("Practice result must not assert official exam eligibility",result.passed)
    }
    @Test fun seededMixedActionsPreserveSubmittedHistoryAndReviewCounts() {
        listOf(7,42,20260914).forEach { seed ->
            val random=Random(seed)
            val questions=(1..6).map{EngineTestData.question("state-$it")}
            var state=EngineTestData.start(questions,seed=seed)
            val immutableHistory=mutableMapOf<String,Submission>()
            repeat(180) { step ->
                val now=EngineTestData.day(1)+(step*1_000L)
                val active=EngineTestData.session(state)
                val index=random.nextInt(active.items.size)
                val item=active.items[index]
                state=when(random.nextInt(7)) {
                    0 -> if(active.submittedAt==null && item.submissionId==null)
                        StudyEngine.select(state,active.id,index,item.choiceOrder.random(random)) else state
                    1 -> if(active.submittedAt==null && item.submissionId==null)
                        StudyEngine.grade(state,active.id,index,now,unanswered=item.draft.isEmpty()) else state
                    2 -> StudyEngine.bookmark(state,item.question.id,now)
                    3 -> StudyEngine.move(state,active.id,index)
                    4 -> StudyEngine.submit(state,active.id,now)
                    5 -> if(active.submittedAt!=null) EngineTestData.start(questions,state,now=now,seed=seed+step) else state
                    else -> StudyEngine.scroll(state,active.id,index,random.nextInt(500))
                }
                val location="seed=$seed step=$step"
                assertEquals(location,state.submissions.size,state.submissions.map{it.id}.distinct().size)
                assertEquals(location,state.submissions.size,state.submissions.map{it.sessionId to it.questionId}.distinct().size)
                state.submissions.forEach { submission ->
                    immutableHistory[submission.id]?.let{assertEquals(location,it,submission)}
                    immutableHistory.putIfAbsent(submission.id,submission)
                }
                state.reviews.forEach { review ->
                    val wrongs=state.submissions.count{it.questionId==review.questionId && it.outcome in listOf("wrong","unanswered")}
                    assertEquals(location,wrongs,review.wrongCount)
                }
                BackupCodec.validate(state)
            }
        }
    }
}
