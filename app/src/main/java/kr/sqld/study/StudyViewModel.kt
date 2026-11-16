package kr.sqld.study

import android.app.Application
import android.os.SystemClock
import android.provider.Settings
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.launch

class StudyViewModel @JvmOverloads constructor(application:Application,val repository:StudyRepository=StudyRepository(application)):AndroidViewModel(application) {
    val state=repository.state
    val ready=MutableStateFlow(false)
    val busy=MutableStateFlow(false)
    val error=MutableStateFlow<String?>(null)
    val message=MutableStateFlow<String?>(null)
    val undoStar=MutableStateFlow<String?>(null)
    val now=MutableStateFlow(System.currentTimeMillis())
    val walkthroughs=WalkthroughCatalog(application)
    val lessonGuides=LessonGuideCatalog(application)
    // Keep a failed pen-up in memory across screen recreation; never replace unrelated records.
    val inkDrafts=MutableStateFlow<Map<String,InkDocument>>(emptyMap())
    val inkErrors=MutableStateFlow<Set<String>>(emptySet())
    fun saveInk(document:InkDocument){
        val generation=repository.restoreGeneration
        inkDrafts.value=inkDrafts.value+(document.id to document)
        inkErrors.value=inkErrors.value-document.id
        viewModelScope.launch {
            try {
                repository.update { state ->
                    check(repository.restoreGeneration==generation){"기록 복원 이후의 오래된 필기입니다."}
                    InkStore.upsert(state,document)
                }
                if(inkDrafts.value[document.id]==document){inkDrafts.value=inkDrafts.value-document.id;inkErrors.value=inkErrors.value-document.id}
            } catch(e:CancellationException){throw e
            } catch(e:Exception){
                if(repository.restoreGeneration!=generation){inkDrafts.value=inkDrafts.value-document.id;inkErrors.value=inkErrors.value-document.id}
                else if(inkDrafts.value[document.id]==document)inkErrors.value=inkErrors.value+document.id
            }
        }
    }
    fun clearInkDrafts(){inkDrafts.value=emptyMap();inkErrors.value=emptySet()}
    private fun boot()=Settings.Global.getInt(getApplication<Application>().contentResolver,Settings.Global.BOOT_COUNT,0)
    private var initializationJob:Job?=null
    init { retryInitialization(); viewModelScope.launch {
        var ticks=0
        while(true){delay(1000);now.value=System.currentTimeMillis();ticks++;if(ready.value&&ticks%5==0)runCatching{tick()}.onFailure{error.value="시간 저장 실패: ${it.message}"}}
    } }
    fun retryInitialization(){
        if(ready.value||initializationJob?.isActive==true)return
        error.value=null
        initializationJob=viewModelScope.launch{
            try{repository.initialize();ready.value=true;runCatching{tick()}.onFailure{error.value="시간 저장 실패: ${it.message}"}}
            catch(e:CancellationException){throw e}
            catch(e:Exception){error.value="학습 자료를 열 수 없습니다: ${e.message}. 기존 데이터는 초기화하지 않았습니다."}
        }
    }
    private suspend fun tick(){
        val ids=state.value.sessions.filter{it.mode=="strict"&&it.submittedAt==null}.map{it.id}
        if(ids.isNotEmpty())repository.update{s->ids.fold(s){acc,id->StudyEngine.tick(acc,id,System.currentTimeMillis(),SystemClock.elapsedRealtime(),boot())}}
    }
    fun mutate(success:String?=null,change:(StudyState)->StudyState){viewModelScope.launch{
        try {repository.update(change);if(success!=null)message.value=success}catch(e:Exception){error.value="저장하지 못했습니다. ${e.message}"}
    }}
    fun launchWork(block:suspend()->Unit){viewModelScope.launch{busy.value=true;try{block()}catch(e:Exception){error.value=e.message?:"작업에 실패했습니다."}finally{busy.value=false}}}
    fun start(questions:List<Question>,mode:String,title:String,mockSetId:String?=null,onStarted:(String)->Unit){launchWork{
        val result=repository.update{StudyEngine.createSession(it,repository.pack,questions,mode,title,System.currentTimeMillis(),SystemClock.elapsedRealtime(),boot(),mockSetId=mockSetId)}
        onStarted(result.activeSessionId!!)
    }}
    fun submit(id:String){mutate{StudyEngine.submit(it,id,System.currentTimeMillis())}}
    fun startUnit(partId:String,number:Int,onStarted:(String)->Unit){launchWork{
        val result=repository.update{UnitPractice.create(it,repository.pack,repository.unitBank,partId,number,System.currentTimeMillis(),SystemClock.elapsedRealtime(),boot(),kotlin.random.Random.nextInt())}
        onStarted(result.activeSessionId!!)
    }}
    fun grade(id:String,index:Int,unanswered:Boolean=false){mutate{StudyEngine.grade(it,id,index,System.currentTimeMillis(),unanswered)}}
    fun star(id:String){launchWork{repository.update{StudyEngine.bookmark(it,id,System.currentTimeMillis())};undoStar.value=id;message.value="별표 상태를 저장했어요"}}
    fun settings(change:(AppSettings)->AppSettings){mutate{it.copy(settings=change(it.settings))}}
}
