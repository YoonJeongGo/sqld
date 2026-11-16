package kr.sqld.study

import kotlinx.serialization.encodeToString
import org.junit.Assert.*
import org.junit.Test

class CourseJourneyTest {
    private fun lesson(id: String = "1-1-01", number: Int = 1, version: Int = 1) = CourseLesson(
        id = id, partId = id.substringBeforeLast('-'), number = number, title = id,
        lectureMinutes = 10, easy = "설명", why = "이유", concepts = emptyList(),
        examples = listOf(
            CourseExample("$id-E1", "예제 1", "질문", steps = listOf("풀이")),
            CourseExample("$id-E2", "예제 2", "질문", steps = listOf("풀이"))
        ),
        memory = "기억", traps = emptyList(),
        selfChecks = listOf(CourseCheck("$id-Q1", "질문", "답", "해설"), CourseCheck("$id-Q2", "질문", "답", "해설")),
        relatedNoteIds = emptyList(), sourceIds = emptyList(), version = version
    )

    private fun course(vararg lessons: CourseLesson) = CoursePack(
        version = "test", title = "강의", parts = emptyList(), lessons = lessons.toList(),
        sources = emptyList(), provenance = "테스트", reviewNote = "테스트"
    )

    private fun confirmed(lesson: CourseLesson) = CourseProgress(
        lesson.id, readVersion = lesson.version,
        revealedResults = lesson.examples.map { it.id },
        checks = lesson.selfChecks.map { CourseCheckProgress(it.id, rating = "understood") }
    )

    @Test fun freshLessonStartsWithReading() {
        assertEquals(CourseJourneyStatus(false, 0, 0, 0, false, "overview"), CourseJourney.status(lesson(), StudyState()))
    }

    @Test fun nextStepUsesReadingThenExamplesThenChecks() {
        val lesson = lesson()
        val read = CourseProgress(lesson.id, readVersion = lesson.version)
        val state = StudyState(courseProgress = listOf(read))
        assertEquals("examples", CourseJourney.status(lesson, state).nextSection)
        val examples = read.copy(revealedResults = lesson.examples.map { it.id })
        val checked = CourseJourney.status(lesson, state.copy(courseProgress = listOf(examples)))
        assertEquals("checks", checked.nextSection)
        assertFalse(checked.complete)
        assertTrue(CourseJourney.status(lesson, state.copy(courseProgress = listOf(confirmed(lesson)))).complete)
        assertEquals("overview", CourseJourney.status(lesson, state.copy(courseProgress = listOf(confirmed(lesson).copy(readVersion = 0)))).nextSection)
    }

    @Test fun bothSelfRatingsFinishTheStepButReviewRemainsVisible() {
        val lesson = lesson()
        val progress = confirmed(lesson).copy(checks = listOf(
            CourseCheckProgress(lesson.selfChecks[0].id, rating = "understood"),
            CourseCheckProgress(lesson.selfChecks[1].id, rating = "review")
        ))
        val result = CourseJourney.status(lesson, StudyState(courseProgress = listOf(progress)))
        assertTrue(result.complete)
        assertEquals(2, result.checksDone)
        assertEquals(1, result.needsReview)
    }

    @Test fun RevealingOrDraftingWithoutSelfRatingDoesNotFinishChecks() {
        val lesson = lesson()
        val progress = confirmed(lesson).copy(checks = lesson.selfChecks.map {
            CourseCheckProgress(it.id, draft = "내 답", revealed = true)
        })
        val result = CourseJourney.status(lesson, StudyState(courseProgress = listOf(progress)))
        assertFalse(result.complete)
        assertEquals(0, result.checksDone)
    }

    @Test fun hidingRatedAnswersKeepsCompletionButEditingClearedRatingReopensCheck() {
        val lesson = lesson()
        val hidden = confirmed(lesson).copy(checks = lesson.selfChecks.map {
            CourseCheckProgress(it.id, draft = "내 답", revealed = false, rating = "review")
        })
        assertTrue(CourseJourney.status(lesson, StudyState(courseProgress = listOf(hidden))).complete)
        val edited = hidden.copy(checks = hidden.checks.mapIndexed { index, check ->
            if (index == 0) check.copy(draft = "고친 답", rating = "") else check
        })
        val result = CourseJourney.status(lesson, StudyState(courseProgress = listOf(edited)))
        assertFalse(result.complete)
        assertEquals(1, result.checksDone)
        assertEquals(1, result.needsReview)
    }

    @Test fun exampleStepsAndAdditionalGuideStepsAreNotResultConfirmation() {
        val lesson = lesson()
        val progress = confirmed(lesson).copy(revealedResults = emptyList(), exampleSteps = mapOf(
            lesson.examples[0].id to 99, "guide:${lesson.examples[1].id}" to 99
        ))
        val result = CourseJourney.status(lesson, StudyState(courseProgress = listOf(progress)))
        assertEquals(0, result.examplesDone)
        assertEquals("examples", result.nextSection)
        assertFalse(result.complete)
    }

    @Test fun onlyCurrentLessonIdsCountAndRemovedRecordsAreNotDeleted() {
        val lesson = lesson()
        val progress = confirmed(lesson).copy(
            revealedResults = listOf(lesson.examples[0].id, "removed-example"),
            checks = listOf(CourseCheckProgress(lesson.selfChecks[0].id, rating = "review"),
                CourseCheckProgress("removed-check", rating = "review"))
        )
        val state = StudyState(courseProgress = listOf(progress, confirmed(lesson("other"))))
        val result = CourseJourney.status(lesson, state)
        assertEquals(1, result.examplesDone)
        assertEquals(1, result.checksDone)
        assertEquals(1, result.needsReview)
        assertEquals(progress, state.courseProgress.first())
        assertEquals(2, state.courseProgress.size)
    }

    @Test fun revisedReadingReopensWithoutLosingExistingExampleOrCheckConfirmation() {
        val previous = lesson()
        val revised = previous.copy(version = 2)
        val state = StudyState(courseProgress = listOf(confirmed(previous)))
        val result = CourseJourney.status(revised, state)
        assertFalse(result.read)
        assertFalse(result.complete)
        assertEquals("overview", result.nextSection)
        assertEquals(2, result.examplesDone)
        assertEquals(2, result.checksDone)
        assertTrue(CourseJourney.status(previous, state).complete)
        assertTrue(CourseJourney.status(previous, state.copy(courseProgress = listOf(confirmed(revised)))).read)
    }

    @Test fun lessonWithoutExamplesSkipsExampleStep() {
        val lesson = lesson().copy(examples = emptyList())
        val state = StudyState(courseProgress = listOf(CourseProgress(lesson.id, readVersion = lesson.version)))
        assertEquals("checks", CourseJourney.status(lesson, state).nextSection)
        assertTrue(CourseJourney.status(lesson, state.copy(courseProgress = listOf(confirmed(lesson)))).complete)
    }

    @Test fun resumeKeepsUnfinishedLastLessonEvenWithEarlierUnfinishedLesson() {
        val earlier = lesson("a")
        val last = lesson("b")
        val state = StudyState(lastLessonId = last.id, courseProgress = listOf(
            CourseProgress(last.id, readVersion = 1, section = "examples", scroll = 257)
        ))
        assertEquals(last, CourseJourney.resume(course(earlier, last), state))
        assertEquals("examples", state.courseProgress.single().section)
        assertEquals(257, state.courseProgress.single().scroll)
    }

    @Test fun completedLastLessonResumesForwardBeforeEarlierGap() {
        val earlier = lesson("a")
        val last = lesson("b")
        val alreadyDone = lesson("c")
        val next = lesson("d")
        val state = StudyState(lastLessonId = last.id, courseProgress = listOf(confirmed(last), confirmed(alreadyDone)))
        assertEquals(next, CourseJourney.resume(course(earlier, last, alreadyDone, next), state))
    }

    @Test fun completedEndWrapsToFirstUnfinishedLesson() {
        val first = lesson("a")
        val last = lesson("b")
        val state = StudyState(lastLessonId = last.id, courseProgress = listOf(confirmed(last)))
        assertEquals(first, CourseJourney.resume(course(first, last), state))
    }

    @Test fun missingOrRemovedLastLessonUsesFirstUnfinishedInArrayOrder() {
        val first = lesson("z", number = 8)
        val second = lesson("a", number = 1)
        val course = course(first, second)
        assertEquals(first, CourseJourney.resume(course, StudyState()))
        assertEquals(first, CourseJourney.resume(course, StudyState(lastLessonId = "removed", courseProgress = listOf(confirmed(lesson("removed"))))))
        assertEquals(second, CourseJourney.resume(course, StudyState(courseProgress = listOf(confirmed(first)))))
    }

    @Test fun completedAndEmptyCoursesHaveNoResumeRecommendation() {
        val lesson = lesson()
        assertNull(CourseJourney.resume(course(lesson), StudyState(lastLessonId = lesson.id, courseProgress = listOf(confirmed(lesson)))))
        assertNull(CourseJourney.resume(course(), StudyState(lastLessonId = "removed")))
    }

    @Test fun nextLessonUsesImmediateArrayNeighbourWithoutCompletionGate() {
        val first = lesson("z", number = 9)
        val second = lesson("a", number = 1)
        val course = course(first, second)
        assertEquals(second, CourseJourney.nextLesson(course, first.id))
        assertNull(CourseJourney.nextLesson(course, second.id))
        assertNull(CourseJourney.nextLesson(course, "missing"))
        assertNull(CourseJourney.nextLesson(course(), first.id))
    }

    @Test fun calculationsPreserveScoredRecordsNotesDraftsAndSavedPosition() {
        val lesson = lesson()
        val state = EngineTestData.grade(EngineTestData.answer(EngineTestData.start(), choice = "wrong-b"))
            .copy(notes = listOf(NoteProgress("note", true, 42)), lastNoteId = "note",
                courseProgress = listOf(confirmed(lesson).copy(section = "concepts", scroll = 333,
                    checks = confirmed(lesson).checks.map { it.copy(draft = "내 설명") })), lastLessonId = lesson.id)
        val before = Codec.encodeToString(state)
        CourseJourney.status(lesson, state)
        CourseJourney.resume(course(lesson), state)
        CourseJourney.nextLesson(course(lesson), lesson.id)
        assertEquals(before, Codec.encodeToString(state))
        assertEquals(1, state.submissions.size)
    }
}
