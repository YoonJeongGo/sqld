package kr.sqld.study

/** Confirmation of learning steps, not a score or a claim of mastery. */
data class CourseJourneyStatus(
    val read: Boolean,
    val examplesDone: Int,
    val checksDone: Int,
    val needsReview: Int,
    val complete: Boolean,
    val nextSection: String
)

/** Derived only from existing records; never writes progress or changes a resume position. */
object CourseJourney {
    fun status(lesson: CourseLesson, state: StudyState): CourseJourneyStatus {
        val progress = CourseStudy.progress(state, lesson.id)
        val read = progress.readVersion >= lesson.version
        val confirmedExamples = progress.revealedResults.toSet()
        val examplesDone = lesson.examples.count { it.id in confirmedExamples }
        val checks = progress.checks.associateBy { it.checkId }
        // Hiding an answer preserves its rating. Editing a draft clears its rating.
        val checksDone = lesson.selfChecks.count {
            checks[it.id]?.rating in setOf("understood", "review")
        }
        val needsReview = lesson.selfChecks.count { checks[it.id]?.rating == "review" }
        val examplesComplete = examplesDone == lesson.examples.size
        val checksComplete = checksDone == lesson.selfChecks.size
        val complete = read && examplesComplete && checksComplete
        val nextSection = when {
            !read -> "overview"
            !examplesComplete -> "examples"
            else -> "checks"
        }
        return CourseJourneyStatus(read, examplesDone, checksDone, needsReview, complete, nextSection)
    }

    /**
     * Resume an unfinished last lesson. Otherwise continue forward in the supplied course order,
     * then wrap to the first unfinished lesson. A completed or empty course has no recommendation.
     * The caller opens the returned lesson normally so its saved section and scroll stay intact.
     */
    fun resume(course: CoursePack, state: StudyState): CourseLesson? {
        val lastIndex = course.lessons.indexOfFirst { it.id == state.lastLessonId }
        if (lastIndex >= 0) {
            val last = course.lessons[lastIndex]
            if (!status(last, state).complete) return last
            course.lessons.drop(lastIndex + 1).firstOrNull { !status(it, state).complete }
                ?.let { return it }
        }
        return course.lessons.firstOrNull { !status(it, state).complete }
    }

    /** Immediate navigation remains available even if the current lesson is unfinished. */
    fun nextLesson(course: CoursePack, lessonId: String): CourseLesson? {
        val index = course.lessons.indexOfFirst { it.id == lessonId }
        return if (index >= 0) course.lessons.getOrNull(index + 1) else null
    }
}
