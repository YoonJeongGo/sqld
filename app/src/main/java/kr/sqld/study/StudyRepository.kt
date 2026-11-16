package kr.sqld.study

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import androidx.room.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import kotlinx.serialization.encodeToString
import java.io.File
import java.security.MessageDigest

@Entity(tableName="study_state") data class StateRow(@PrimaryKey val id:Int=1,val revision:Long,val payload:String)
@Entity(tableName="grading_submissions",indices=[Index(value=["sessionId","questionId"],unique=true)])
data class SubmissionRow(@PrimaryKey val id:String,val sessionId:String,val questionId:String,val payload:String)
@Entity(tableName="recovery_points") data class RecoveryRow(@PrimaryKey val id:Long,val payload:String)
@Dao interface StudyDao {
    @Query("SELECT * FROM study_state WHERE id=1") suspend fun state():StateRow?
    @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun save(row:StateRow)
    @Insert(onConflict=OnConflictStrategy.ABORT) suspend fun submission(row:SubmissionRow)
    @Query("DELETE FROM grading_submissions") suspend fun clearSubmissions()
    @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun recovery(row:RecoveryRow)
    @Query("SELECT * FROM recovery_points ORDER BY id DESC LIMIT 1") suspend fun latestRecovery():RecoveryRow?
    @Query("SELECT COUNT(*) FROM grading_submissions") suspend fun submissionCount():Int
}
@Database(entities=[StateRow::class,SubmissionRow::class,RecoveryRow::class],version=1,exportSchema=true)
abstract class StudyDatabase:RoomDatabase(){abstract fun dao():StudyDao}
private val Context.preferenceProjection by preferencesDataStore(name="display_preferences")

object BackupCodec {
    const val MAX_BYTES=32*1024*1024
    const val CURRENT_VERSION=3
    fun hash(text:String)=MessageDigest.getInstance("SHA-256").digest(text.toByteArray(Charsets.UTF_8)).joinToString(""){"%02x".format(it)}
    fun encode(state:StudyState,now:Long=System.currentTimeMillis()):String {
        val payload=Codec.encodeToString(upgrade(state))
        return Codec.encodeToString(BackupEnvelope(createdAt=now,sha256=hash(payload),payload=payload))
    }
    fun decode(text:String):StudyState {
        require(text.toByteArray(Charsets.UTF_8).size<=MAX_BYTES){"백업은 최대 32MB까지 지원합니다."}
        val envelope=Codec.decodeFromString<BackupEnvelope>(text)
        require(envelope.format=="sqlnote-backup" && envelope.schemaVersion in 1..CURRENT_VERSION){"지원하지 않는 백업 형식 또는 미래 버전입니다."}
        require(hash(envelope.payload)==envelope.sha256){"손상된 백업입니다. 검사값이 일치하지 않습니다."}
        val state=Codec.decodeFromString<StudyState>(envelope.payload)
        require(state.schemaVersion<=envelope.schemaVersion){"백업과 데이터 버전이 일치하지 않습니다."}
        return upgrade(state)
    }
    fun upgrade(state:StudyState):StudyState {
        validate(state)
        return state.copy(schemaVersion=CURRENT_VERSION)
    }
    fun validate(state:StudyState){
        require(state.schemaVersion in 1..CURRENT_VERSION){"미지원 데이터 버전"}
        CourseStudy.validateState(state)
        InkStore.validate(state.inkDocuments)
        require(state.sessions.map{it.id}.distinct().size==state.sessions.size)
        require(state.submissions.map{it.id}.distinct().size==state.submissions.size)
        require(state.submissions.map{it.sessionId to it.questionId}.distinct().size==state.submissions.size)
        require(state.bookmarks.map{it.id}.distinct().size==state.bookmarks.size)
        require(state.reviews.map{it.questionId}.distinct().size==state.reviews.size)
        require(state.annotations.map{it.id}.distinct().size==state.annotations.size)
        require(state.settings.textScale in 0.85f..1.5f && state.settings.dailyCount in 1..200)
        require(state.settings.intervals.isNotEmpty() && state.settings.intervals.size<=10 && state.settings.intervals.all{it in 1..365})
        val submissions=state.submissions.associateBy{it.id}
        val sessions=state.sessions.associateBy{it.id}
        val sessionItems=mutableMapOf<String,Map<String,SessionItem>>()
        state.sessions.forEach{s->
            if(s.isUnitMock())UnitPractice.validateSpec(s)
            else require(s.examSpec.modelCount>0 && s.examSpec.sqlCount>0)
            require(s.examSpec.minutes>0 && s.examSpec.pointsPerQuestion>0)
            require(s.examSpec.passPoints in 1..((s.examSpec.modelCount+s.examSpec.sqlCount)*s.examSpec.pointsPerQuestion) && s.examSpec.subjectMinimumPercent in 1..100)
            require(s.items.isNotEmpty() && s.current in s.items.indices)
            require(s.items.map{it.question.id}.distinct().size==s.items.size)
            require(s.mode in listOf("immediate","batch","strict","mixed"))
            require(s.remainingMillis>=0)
            s.items.forEach{i->
                require(i.question.choices.map{it.id}.distinct().size==i.question.choices.size && i.choiceOrder.distinct().size==i.choiceOrder.size)
                require(i.choiceOrder.toSet()==i.question.choices.map{it.id}.toSet() && i.choiceOrder.size==i.question.choices.size)
                require(i.question.correctChoiceIds.size==1 && i.question.correctChoiceIds.all{it in i.choiceOrder})
                require(i.draft.size<=1 && i.draft.all{it in i.choiceOrder})
                i.submissionId?.let { sid -> val r=submissions[sid] ?: error("제출 기록 참조 오류"); require(r.sessionId==s.id && r.questionId==i.question.id && r.choiceIds==i.draft) }
            }
            if(s.submittedAt!=null)require(s.items.all{it.submissionId!=null})
            sessionItems[s.id]=s.items.associateBy{it.question.id}
        }
        state.submissions.forEach{r->
            val session=sessions[r.sessionId]?:error("세션 참조 오류")
            val item=sessionItems.getValue(session.id)[r.questionId]?:error("문항 참조 오류")
            require(item.submissionId==r.id && r.choiceOrder==item.choiceOrder && r.questionVersion==item.question.version)
            val expected=if(r.choiceIds.isEmpty())"unanswered" else if(r.choiceIds.toSet()==item.question.correctChoiceIds.toSet())"correct" else "wrong"
            require(r.outcome==expected){"채점 기록 검사 실패"}
        }
    }
}

class StudyRepository(val context:Context, val db:StudyDatabase=Room.databaseBuilder(context,StudyDatabase::class.java,"sqlnote.db").build(),val projectPreferences:Boolean=true,
    private val settingsProjectionWriter:(suspend (AppSettings)->Unit)?=null) {
    private val mutex=Mutex()
    private val mutable=MutableStateFlow(StudyState())
    private var projectedSettings:AppSettings?=null
    val state:StateFlow<StudyState> = mutable
    lateinit var pack:ContentPack; private set
    lateinit var course:CoursePack; private set
    lateinit var courseVisuals:CourseVisualPack; private set
    var unitBank:UnitQuestionBank=UnitQuestionBank(); private set
    // Transient epoch prevents disposed readers from writing stale positions after replacement.
    // Read and compare inside an update transform; restore increments it under the same mutex.
    @Volatile var restoreGeneration:Long=0; private set
    var failNextWrite=false // Injectable storage failure, reachable only through tests.
    suspend fun initialize()=withContext(Dispatchers.IO){
        pack=Codec.decodeFromString(context.assets.open("content-pack.json").bufferedReader().use{it.readText()})
        require(pack.schemaVersion==1 && pack.notes.isNotEmpty()){"설치 콘텐츠를 읽을 수 없습니다."}
        course=Codec.decodeFromString(context.assets.open("course-pack.json").bufferedReader().use{it.readText()})
        CourseStudy.validatePack(course,pack)
        unitBank=Codec.decodeFromString(context.assets.open("unit-question-bank.json").bufferedReader().use{it.readText()})
        unitBank.validate(pack,course)
        pack=pack.copy(questions=pack.questions+unitBank.questions,sources=pack.sources+unitBank.sources)
        courseVisuals=Codec.decodeFromString(context.assets.open("course-visuals.json").bufferedReader().use{it.readText()})
        CourseVisuals.validate(courseVisuals,course)
        val row=db.dao().state()
        val initial=if(row==null)StudyState(contentVersion=pack.version)else Codec.decodeFromString<StudyState>(row.payload)
        BackupCodec.validate(initial)
        mutable.value=initial
        update{StudyEngine.reconcile(BackupCodec.upgrade(it),pack)}
    }
    suspend fun update(change:(StudyState)->StudyState):StudyState=mutex.withLock {
        withContext(Dispatchers.IO) {
            val next=db.withTransaction {
                val row=db.dao().state()
                val previous=row?.let{Codec.decodeFromString<StudyState>(it.payload)}?:mutable.value
                val transformed=change(previous)
                CourseStudy.validateState(transformed)
                if(transformed.inkDocuments!==previous.inkDocuments)InkStore.validate(transformed.inkDocuments)
                if(transformed==previous && row!=null)return@withTransaction previous
                if(failNextWrite){failNextWrite=false;error("저장 실패 주입: 기존 기록이 보존되었습니다.")}
                val next=transformed.copy(revision=previous.revision+1)
                val ids=previous.submissions.map{it.id}.toSet()
                next.submissions.filterNot{it.id in ids}.forEach{db.dao().submission(SubmissionRow(it.id,it.sessionId,it.questionId,Codec.encodeToString(it)))}
                db.dao().save(StateRow(revision=next.revision,payload=Codec.encodeToString(next)))
                next
            }
            mutable.value=next
            projectSettings(next.settings)
            next
        }
    }
    suspend fun export():String=withContext(Dispatchers.IO){mutex.withLock{BackupCodec.encode(mutable.value)}}
    suspend fun restore(candidate:StudyState)=mutex.withLock {
        withContext(Dispatchers.IO) {
            val reconciled=StudyEngine.reconcile(BackupCodec.upgrade(candidate),pack).copy(revision=mutable.value.revision+1)
            db.withTransaction {
                val previous=db.dao().state()?:StateRow(revision=mutable.value.revision,payload=Codec.encodeToString(mutable.value))
                db.dao().recovery(RecoveryRow(System.currentTimeMillis(),previous.payload))
                db.dao().clearSubmissions()
                if(failNextWrite){failNextWrite=false;error("복원 실패 주입")}
                reconciled.submissions.forEach{db.dao().submission(SubmissionRow(it.id,it.sessionId,it.questionId,Codec.encodeToString(it)))}
                db.dao().save(StateRow(revision=reconciled.revision,payload=Codec.encodeToString(reconciled)))
            }
            restoreGeneration++
            mutable.value=reconciled
            projectSettings(reconciled.settings)
        }
    }
    // This cache only skips the secondary settings projection; every update still reads Room.
    // Remember successful writes only so a failed projection is retried on the next update.
    private suspend fun projectSettings(settings:AppSettings){
        if(!projectPreferences || projectedSettings==settings)return
        runCatching {
            if(settingsProjectionWriter!=null)settingsProjectionWriter.invoke(settings)
            else context.preferenceProjection.edit{it[stringPreferencesKey("settings")]=Codec.encodeToString(settings)}
            projectedSettings=settings
        }
    }
    suspend fun recoveryCandidate():StudyState?=withContext(Dispatchers.IO){db.dao().latestRecovery()?.let{Codec.decodeFromString<StudyState>(it.payload)}}
}
