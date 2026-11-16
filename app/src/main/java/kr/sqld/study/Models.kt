package kr.sqld.study

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

val Codec = Json { ignoreUnknownKeys = true; encodeDefaults = true }

@Serializable data class ExamSpec(
    val id:String="sqld-provisional-2026-09-14", val version:Int=1,
    val title:String="SQLD 검토용 기준", val checkedAt:String="2026-09-14",
    val effectiveDate:String?=null, val sourceIds:List<String> = listOf("dataq-sqld","eduwill-sqld2026"),
    val verification:String="provisional_official_unavailable", val modelCount:Int=10,
    val sqlCount:Int=40, val pointsPerQuestion:Int=2, val minutes:Int=90,
    val passPoints:Int=60, val subjectMinimumPercent:Int=40
)
@Serializable data class Objective(val id:String,val subjectId:String,val topicId:String,val title:String,val prerequisites:List<String> = emptyList(),val synonyms:List<String> = emptyList(),val scopeStatus:String="provisional")
@Serializable data class ContentBlock(val id:String,val kind:String,val title:String,val text:String)
@Serializable data class Note(val id:String,val version:Int=1,val objectiveId:String,val title:String,val summary:String,val sourceIds:List<String> = emptyList(),val verification:String="document_review",val blocks:List<ContentBlock>,val recallQuestionIds:List<String> = emptyList())
@Serializable data class DataTable(val title:String="",val columns:List<String>,val rows:List<List<String?>>)
@Serializable data class Choice(val id:String,val text:String,val reason:String)
@Serializable data class ExplanationStep(val title:String,val text:String,val table:DataTable?=null)
@Serializable data class Explanation(val summary:String,val prerequisites:List<String> = emptyList(),val conditions:List<String> = emptyList(),val steps:List<ExplanationStep>,val memory:String,val relatedNoteId:String)
@Serializable data class SqlFixture(val schemaSql:String="",val setupSql:String="",val query:String="",val expectedRows:List<List<String?>> = emptyList(),val ordered:Boolean=false,val constraints:List<String> = emptyList(),val sessionSettings:List<String> = emptyList(),val verificationMethod:String="document_review",val evidence:String="")
@Serializable data class Question(
    val id:String,val version:Int=1,val subjectId:String,val topicId:String,val objectiveIds:List<String>,val familyId:String,
    val kind:String,val title:String,val stem:String,val choices:List<Choice>,val correctChoiceIds:List<String>,val explanation:Explanation,
    val sourceIds:List<String> = emptyList(),val sourceType:String="original_practice",val verification:String="document_review",val status:String="published",
    val dialect:String="conceptual",val dialectVersion:String="n/a",val difficulty:String="basic",val difficultyReason:String="",val importanceReason:String="",
    val fixture:SqlFixture?=null,val sql:String?=null,val tables:List<DataTable> = emptyList(),val mockSetId:String?=null,val validationEvidence:List<String> = emptyList()
)
@Serializable data class SourceRecord(val sourceId:String,val publisher:String="",val title:String="",val url:String="",val version:String?=null,val publicationDate:String?=null,val checkedAt:String="",val accessStatus:String="",val usageScope:String="",val license:String="")
@Serializable data class ContentCorrection(val questionId:String,val fromVersion:Int,val toVersion:Int,val reason:String,val at:String)
@Serializable data class StudyPriority(val objectiveId:String,val level:String="important",val reason:String="",val focusPoints:List<String> = emptyList(),val sourceIds:List<String> = emptyList(),val frequencyStatus:String="not_measured",val frequencyNote:String="단원별 출제 횟수는 확인하지 못했습니다.")
@Serializable data class ContentPack(val schemaVersion:Int=1,val version:String="2026.09.14.1",val examSpec:ExamSpec=ExamSpec(),val objectives:List<Objective> = emptyList(),val notes:List<Note> = emptyList(),val questions:List<Question> = emptyList(),val sources:List<SourceRecord> = emptyList(),val corrections:List<ContentCorrection> = emptyList(),val studyPriorities:List<StudyPriority> = emptyList(),val priorityCheckedAt:String="",val priorityMethodology:String="",val legacyNoteVersions:Map<String,Int> = emptyMap()) {
    fun practice() = questions.filter { it.status=="published" && it.verification !in listOf("draft","quarantined") && it.mockSetId==null && it.kind!="mock" }
    fun mock(id:String) = questions.filter { it.status=="published" && it.verification !in listOf("draft","quarantined") && it.mockSetId==id }
}
@Serializable data class SessionItem(val question:Question,val choiceOrder:List<String>,val draft:List<String> = emptyList(),val confidence:String="",val submissionId:String?=null,val scroll:Int=0,val activeMillis:Long=0)
@Serializable data class QuizSession(
    val id:String,val title:String,val mode:String,val items:List<SessionItem>,val contentVersion:String,val examSpec:ExamSpec,
    val startedAt:Long,val seed:Int,val current:Int=0,val submittedAt:Long?=null,val mockSetId:String?=null,
    val diagnosticEligible:Boolean=true,val repeat:Boolean=false,val convertedAt:Long?=null,
    val remainingMillis:Long=0,val lastWall:Long=0,val lastElapsed:Long=0,val bootCount:Int=0,
    val clockAnomaly:Boolean=false,val elapsedMillis:Long=0
)
@Serializable data class Submission(
    val id:String,val sessionId:String,val questionId:String,val questionVersion:Int,val choiceIds:List<String>,val choiceOrder:List<String>,
    val outcome:String,val helped:Boolean,val confidence:String,val activeMillis:Long,val submittedAt:Long,
    val contentVersion:String,val examSpecId:String,val firstEver:Boolean,val reviewApplied:Boolean=true
)
@Serializable data class Exposure(val id:String,val questionId:String,val familyId:String,val sessionId:String,val kind:String,val at:Long)
@Serializable data class ReviewState(val questionId:String,val wrongCount:Int=0,val stage:Int=0,val dueAt:Long=0,val needsReview:Boolean=false,val lastDay:String="",val reason:String="",val lastOutcome:String="")
@Serializable data class Bookmark(val id:String,val at:Long)
@Serializable data class Annotation(val id:String,val noteId:String,val blockId:String,val quote:String,val memo:String,val style:String,val at:Long,val archived:Boolean=false)
@Serializable data class NoteProgress(val noteId:String,val read:Boolean=false,val scroll:Int=0,val collapsed:List<String> = emptyList(),val readVersion:Int=0)
@Serializable data class ContentIssue(val id:String,val contentId:String,val contentVersion:String,val description:String,val exclude:Boolean,val at:Long)
@Serializable data class AppSettings(val theme:String="system",val textScale:Float=1f,val noteView:String="full",val explanationExpanded:Boolean=false,val dailyCount:Int=10,val targetDate:String="",val targetDateSource:String="user",val intervals:List<Int> = listOf(1,3,7,14,30),val reduceMotion:Boolean=true,val sound:Boolean=false,val vibration:Boolean=false,val wrapSql:Boolean=true)
@Serializable data class StudyState(
    val schemaVersion:Int=3,val contentVersion:String="",val revision:Long=0,
    val sessions:List<QuizSession> = emptyList(),val submissions:List<Submission> = emptyList(),
    val bookmarks:List<Bookmark> = emptyList(),val noteBookmarks:List<Bookmark> = emptyList(),
    val annotations:List<Annotation> = emptyList(),val notes:List<NoteProgress> = emptyList(),
    val reviews:List<ReviewState> = emptyList(),val exposures:List<Exposure> = emptyList(),val issues:List<ContentIssue> = emptyList(),
    val settings:AppSettings=AppSettings(),val lastNoteId:String?=null,val activeSessionId:String?=null,
    val courseProgress:List<CourseProgress> = emptyList(),val lastLessonId:String?=null,
    val inkDocuments:List<InkDocument> = emptyList()
)
@Serializable data class BackupEnvelope(val format:String="sqlnote-backup",val schemaVersion:Int=3,val createdAt:Long,val sha256:String,val payload:String)
@Serializable data class Score(val modelCorrect:Int,val sqlCorrect:Int,val modelTotal:Int,val sqlTotal:Int,val unanswered:Int,val points:Int,val modelFail:Boolean,val sqlFail:Boolean,val passed:Boolean)
