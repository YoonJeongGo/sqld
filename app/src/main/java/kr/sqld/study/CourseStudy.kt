package kr.sqld.study

/** Course reading and self-assessment are deliberately independent of scored attempts. */
object CourseStudy {
    private val ratings=setOf("", "understood", "review")

    fun progress(state:StudyState,lessonId:String):CourseProgress =
        state.courseProgress.firstOrNull{it.lessonId==lessonId} ?: CourseProgress(lessonId)

    fun update(state:StudyState,lessonId:String,change:(CourseProgress)->CourseProgress,
        now:Long=System.currentTimeMillis()):StudyState {
        require(lessonId.isNotBlank() && now>=0)
        val previous=progress(state,lessonId)
        val changed=change(previous)
        require(changed.lessonId==lessonId){"강의 진도 식별자는 변경할 수 없습니다."}
        if(changed==previous && state.lastLessonId==lessonId && state.courseProgress.any{it.lessonId==lessonId})return state
        val next=changed.copy(updatedAt=now)
        validateProgress(next)
        val records=if(state.courseProgress.any{it.lessonId==lessonId})
            state.courseProgress.map{if(it.lessonId==lessonId)next else it}
        else state.courseProgress+next
        return state.copy(courseProgress=records,lastLessonId=lessonId)
    }

    fun read(state:StudyState,lesson:CourseLesson,value:Boolean):StudyState =
        update(state,lesson.id,{it.copy(readVersion=if(value)lesson.version else 0)})

    fun validateState(state:StudyState) {
        require(state.courseProgress.map{it.lessonId}.distinct().size==state.courseProgress.size){"중복된 강의 진도입니다."}
        require(state.lastLessonId==null || state.lastLessonId.isNotBlank())
        state.courseProgress.forEach(::validateProgress)
    }

    private fun validateProgress(progress:CourseProgress) {
        require(progress.lessonId.isNotBlank() && progress.readVersion>=0 && progress.scroll>=0 && progress.updatedAt>=0)
        require(progress.section in setOf("overview","concepts","examples","checks"))
        require(progress.exampleSteps.all{(id,step)->id.isNotBlank() && step>=0})
        require(progress.revealedResults.all{it.isNotBlank()} && progress.revealedResults.distinct().size==progress.revealedResults.size)
        require(progress.checks.map{it.checkId}.distinct().size==progress.checks.size)
        progress.checks.forEach {
            require(it.checkId.isNotBlank() && it.draft.length<=10_000 && it.rating in ratings){"자기 점검 기록을 읽을 수 없습니다."}
        }
    }

    fun validatePack(course:CoursePack,content:ContentPack) {
        require(course.schemaVersion==1 && course.version.isNotBlank() && course.title.isNotBlank()){"강의 자료 형식이 올바르지 않습니다."}
        require(course.parts.isNotEmpty() && course.lessons.isNotEmpty())
        require(course.parts.map{it.id}.distinct().size==course.parts.size)
        require(course.lessons.map{it.id}.distinct().size==course.lessons.size)
        require(course.sources.map{it.id}.distinct().size==course.sources.size)
        require(course.parts.all{it.id.isNotBlank() && it.title.isNotBlank()})
        require(course.sources.all{it.id.isNotBlank() && it.title.isNotBlank() && it.url.startsWith("https://")})
        val parts=course.parts.map{it.id}.toSet()
        val notes=content.notes.map{it.id}.toSet()
        val sources=course.sources.map{it.id}.toSet()
        val exampleIds=course.lessons.flatMap{it.examples}.map{it.id}
        val checkIds=course.lessons.flatMap{it.selfChecks}.map{it.id}
        require(exampleIds.distinct().size==exampleIds.size && checkIds.distinct().size==checkIds.size)
        course.lessons.forEach { lesson ->
            require(lesson.id.isNotBlank() && lesson.partId in parts && lesson.number>0 && lesson.version>0 && lesson.lectureMinutes>0)
            require(lesson.title.isNotBlank() && lesson.easy.isNotBlank() && lesson.why.isNotBlank() && lesson.memory.isNotBlank())
            require(lesson.relatedNoteIds.isNotEmpty() && lesson.relatedNoteIds.all{it in notes})
            require(lesson.sourceIds.isNotEmpty() && lesson.sourceIds.all{it in sources})
            require(lesson.concepts.isNotEmpty() && lesson.concepts.all{it.term.isNotBlank() && it.meaning.isNotBlank()})
            lesson.examples.forEach { example ->
                require(example.id.isNotBlank() && example.title.isNotBlank() && example.question.isNotBlank())
                require(example.mode in setOf("theory","sqlite","oracle"))
                require(example.steps.isNotEmpty() && example.steps.all{it.isNotBlank()} && example.verification.isNotBlank())
                (example.tables+example.results).forEach { table ->
                    require(table.columns.isNotEmpty() && table.columns.all{it.isNotBlank()})
                    require(table.rows.all{it.size==table.columns.size})
                }
            }
            require(lesson.selfChecks.isNotEmpty())
            lesson.selfChecks.forEach { check ->
                require(check.id.isNotBlank() && check.question.isNotBlank() && check.answer.isNotBlank() && check.explanation.isNotBlank())
            }
        }
    }
}
