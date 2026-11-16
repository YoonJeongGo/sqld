package kr.sqld.study

import kotlinx.serialization.encodeToString
import org.junit.Assert.*
import org.junit.Test

class BackupCodecTest {
    private fun richState():StudyState {
        var state=EngineTestData.grade(EngineTestData.answer(EngineTestData.start(),choice="wrong-b"))
        state=StudyEngine.bookmark(state,"q",EngineTestData.day(1))
        return state.copy(contentVersion="old-content",revision=9,
            noteBookmarks=listOf(Bookmark("note",1)),
            annotations=listOf(Annotation("memo","note","block","NULL ≠ 0","한글 메모 <script>alert(1)</script>","underline",2,true)),
            notes=listOf(NoteProgress("note",true,175,listOf("block"))),
            issues=listOf(ContentIssue("issue","q","old-content","검토 요청",true,3)),
            settings=AppSettings(theme="dark",textScale=1.3f,noteView="recall",dailyCount=20,
                targetDate="2026-11-14",intervals=listOf(1,4,8,16),sound=false,vibration=false),
            lastNoteId="note")
    }
    private fun rejects(state:StudyState) {
        assertThrows(Exception::class.java){BackupCodec.decode(BackupCodec.encode(state,1))}
    }
    @Test fun roundTripPreservesEveryPersonalRecordAndSessionSnapshot() {
        val state=richState()
        assertEquals(state,BackupCodec.decode(BackupCodec.encode(state,123456)))
    }
    @Test fun importedStringsRemainDataIncludingScriptLookingMemo() {
        val state=BackupCodec.decode(BackupCodec.encode(richState(),1))
        assertEquals("한글 메모 <script>alert(1)</script>",state.annotations.single().memo)
        assertTrue(state.annotations.single().archived)
    }
    @Test fun checksumUsesPayloadBytesAndDetectsTampering() {
        val encoded=BackupCodec.encode(richState(),1)
        val envelope=Codec.decodeFromString<BackupEnvelope>(encoded)
        val modified=envelope.copy(payload=envelope.payload.replace("한글 메모","변조 메모"))
        assertThrows(IllegalArgumentException::class.java){BackupCodec.decode(Codec.encodeToString(modified))}
    }
    @Test fun malformedTruncatedBackupIsRejected() {
        val encoded=BackupCodec.encode(richState(),1)
        assertThrows(Exception::class.java){BackupCodec.decode(encoded.dropLast(12))}
        assertThrows(Exception::class.java){BackupCodec.decode("not-json")}
    }
    @Test fun futureEnvelopeAndFuturePayloadVersionsAreRejectedEvenWithCorrectChecksum() {
        val envelope=Codec.decodeFromString<BackupEnvelope>(BackupCodec.encode(richState(),1))
        assertThrows(IllegalArgumentException::class.java){BackupCodec.decode(Codec.encodeToString(envelope.copy(schemaVersion=BackupCodec.CURRENT_VERSION+1)))}
        rejects(richState().copy(schemaVersion=BackupCodec.CURRENT_VERSION+1))
    }
    @Test fun wrongBackupFormatIsRejected() {
        val envelope=Codec.decodeFromString<BackupEnvelope>(BackupCodec.encode(richState(),1))
        assertThrows(IllegalArgumentException::class.java){BackupCodec.decode(Codec.encodeToString(envelope.copy(format="unrelated-app")))}
    }
    @Test fun sizeLimitUsesUtf8BytesRatherThanCharacterCount() {
        val oversized="가".repeat(BackupCodec.MAX_BYTES/3+1)
        assertTrue(oversized.length<BackupCodec.MAX_BYTES)
        assertThrows(IllegalArgumentException::class.java){BackupCodec.decode(oversized)}
    }
    @Test fun duplicateAttemptIdsAndSessionQuestionPairsAreRejected() {
        val state=richState();val submission=state.submissions.single()
        rejects(state.copy(submissions=state.submissions+submission))
        rejects(state.copy(submissions=state.submissions+submission.copy(id="different-id")))
    }
    @Test fun duplicateSessionsBookmarksReviewsAndAnnotationsAreRejected() {
        val state=richState()
        rejects(state.copy(sessions=state.sessions+state.sessions.single()))
        rejects(state.copy(bookmarks=state.bookmarks+state.bookmarks.single()))
        rejects(state.copy(reviews=state.reviews+state.reviews.single()))
        rejects(state.copy(annotations=state.annotations+state.annotations.single()))
    }
    @Test fun danglingSubmissionAndChangedDraftCannotBeRestoredAsValidHistory() {
        val state=richState();val s=state.sessions.single()
        rejects(state.copy(submissions=emptyList()))
        rejects(state.copy(sessions=listOf(s.copy(items=s.items.map{it.copy(draft=listOf("right"))})) ))
        rejects(state.copy(submissions=state.submissions.map{it.copy(questionId="missing")}))
    }
    @Test fun tamperedOutcomeAndQuestionVersionAreRejected() {
        val state=richState()
        rejects(state.copy(submissions=state.submissions.map{it.copy(outcome="correct")}))
        rejects(state.copy(submissions=state.submissions.map{it.copy(questionVersion=999)}))
    }
    @Test fun changingChoiceOrderOfHistoricalSubmissionIsRejected() {
        val state=richState()
        rejects(state.copy(submissions=state.submissions.map{it.copy(choiceOrder=it.choiceOrder.reversed())}))
    }
    @Test fun completedSessionCannotHaveUngradedItems() {
        val state=EngineTestData.start()
        rejects(state.copy(sessions=state.sessions.map{it.copy(submittedAt=EngineTestData.day(1))}))
    }
    @Test fun questionOrderCurrentIndexAndDraftChoiceAreValidated() {
        val state=EngineTestData.start();val s=state.sessions.single()
        rejects(state.copy(sessions=listOf(s.copy(current=9))))
        rejects(state.copy(sessions=listOf(s.copy(items=s.items+s.items))))
        rejects(state.copy(sessions=listOf(s.copy(items=s.items.map{it.copy(draft=listOf("missing-choice"))})) ))
        rejects(state.copy(sessions=listOf(s.copy(items=s.items.map{it.copy(choiceOrder=listOf("right"))})) ))
    }
    @Test fun timerAndSettingsCannotRestoreInvalidValues() {
        val state=EngineTestData.start()
        rejects(state.copy(sessions=state.sessions.map{it.copy(remainingMillis=-1)}))
        rejects(state.copy(settings=AppSettings(textScale=Float.NaN)))
        rejects(state.copy(settings=AppSettings(dailyCount=0)))
        rejects(state.copy(settings=AppSettings(intervals=emptyList())))
        rejects(state.copy(settings=AppSettings(intervals=listOf(0,1))))
    }
    @Test fun repeatedDecodeDoesNotDuplicateAttemptsOrRewriteOriginalScore() {
        val encoded=BackupCodec.encode(richState(),1)
        val first=BackupCodec.decode(encoded);val second=BackupCodec.decode(encoded)
        assertEquals(first,second)
        assertEquals(1,second.submissions.size);assertEquals("wrong",second.submissions.single().outcome)
        assertEquals(1,second.reviews.single().wrongCount)
    }
    @Test fun duplicateChoiceIdentifiersAreRejectedEvenWhenOrderSetsMatch() {
        val state=EngineTestData.start();val s=state.sessions.single();val item=s.items.single()
        val malformed=item.question.copy(choices=listOf(
            Choice("right","yes","reason"),Choice("same","one","reason"),
            Choice("same","two","reason"),Choice("last","three","reason")))
        rejects(state.copy(sessions=listOf(s.copy(items=listOf(item.copy(question=malformed,
            choiceOrder=listOf("right","same","same","last")))))))
    }
    @Test fun restoredExamSpecificationMustNotContainImpossibleCountsOrDuration() {
        val state=EngineTestData.start()
        rejects(state.copy(sessions=state.sessions.map{it.copy(examSpec=it.examSpec.copy(modelCount=-1))}))
        rejects(state.copy(sessions=state.sessions.map{it.copy(examSpec=it.examSpec.copy(minutes=0))}))
    }
    @Test fun oldBackupWithoutCourseFieldsUpgradesWithoutChangingHistoricalRecords() {
        val old=richState().copy(schemaVersion=1)
        val payload=Codec.encodeToString(old).replace(",\"courseProgress\":[],\"lastLessonId\":null","")
        assertFalse(payload.contains("courseProgress"))
        val backup=Codec.encodeToString(BackupEnvelope(schemaVersion=1,createdAt=1,sha256=BackupCodec.hash(payload),payload=payload))
        assertEquals(old.copy(schemaVersion=BackupCodec.CURRENT_VERSION),BackupCodec.decode(backup))
    }
    @Test fun courseProgressIsPreservedByBackupAndCannotBeImportedByVersionOneReaders() {
        val progress=CourseProgress("2-1-15",readVersion=1,scroll=321,section="checks",
            exampleSteps=mapOf("2-1-15-E01" to 3),revealedResults=listOf("2-1-15-E01"),
            checks=listOf(CourseCheckProgress("2-1-15-Q1","NULL은 0과 다릅니다.",true,"review")),updatedAt=123)
        val state=richState().copy(courseProgress=listOf(progress),lastLessonId=progress.lessonId)
        val encoded=BackupCodec.encode(state,1)
        val envelope=Codec.decodeFromString<BackupEnvelope>(encoded)
        assertEquals(BackupCodec.CURRENT_VERSION,envelope.schemaVersion)
        assertEquals(BackupCodec.CURRENT_VERSION,Codec.decodeFromString<StudyState>(envelope.payload).schemaVersion)
        assertEquals(state,BackupCodec.decode(encoded))
    }
    @Test fun exportUpgradesOldPayloadBeforeWritingCurrentEnvelope() {
        val old=richState().copy(schemaVersion=1)
        val envelope=Codec.decodeFromString<BackupEnvelope>(BackupCodec.encode(old,1))
        assertEquals(BackupCodec.CURRENT_VERSION,envelope.schemaVersion)
        assertEquals(old.copy(schemaVersion=BackupCodec.CURRENT_VERSION),BackupCodec.decode(Codec.encodeToString(envelope)))
    }
    @Test fun corruptCourseRecordsFailBeforeRestore() {
        val progress=CourseProgress("lesson",checks=listOf(CourseCheckProgress("check","answer",true,"understood")))
        val state=richState().copy(courseProgress=listOf(progress),lastLessonId="lesson")
        rejects(state.copy(courseProgress=listOf(progress,progress)))
        rejects(state.copy(courseProgress=listOf(progress.copy(checks=progress.checks+progress.checks))))
        rejects(state.copy(courseProgress=listOf(progress.copy(checks=listOf(progress.checks.single().copy(rating="correct"))))))
        rejects(state.copy(courseProgress=listOf(progress.copy(exampleSteps=mapOf("example" to -1)))))
        rejects(state.copy(courseProgress=listOf(progress.copy(section="missing"))))
        rejects(state.copy(courseProgress=listOf(progress.copy(scroll=-1))))
        rejects(state.copy(courseProgress=listOf(progress.copy(checks=listOf(progress.checks.single().copy(draft="a".repeat(10_001)))))))
    }
}
