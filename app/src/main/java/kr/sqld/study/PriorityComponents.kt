package kr.sqld.study

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.Alignment
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalLayoutApi::class)
@Composable fun PriorityBadge(priority:StudyPriority){
    val colors=MaterialTheme.colorScheme
    FlowRow(horizontalArrangement=Arrangement.spacedBy(6.dp),verticalArrangement=Arrangement.spacedBy(6.dp)){
        Surface(color=when(priority.level){"core"->colors.primaryContainer;"important"->colors.secondaryContainer;else->colors.surfaceVariant},shape=RoundedCornerShape(8.dp)){
            Row(Modifier.padding(horizontal=10.dp,vertical=6.dp),verticalAlignment=Alignment.CenterVertically,horizontalArrangement=Arrangement.spacedBy(5.dp)){
                Icon(if(priority.level=="core")Icons.Outlined.PriorityHigh else Icons.Outlined.Info,null,Modifier.size(16.dp))
                Text(StudyGuide.label(priority.level),style=MaterialTheme.typography.labelMedium)
            }
        }
        if(priority.frequencyStatus=="educator_emphasis")Surface(color=colors.tertiaryContainer,shape=RoundedCornerShape(8.dp)){
            Text("교재·강사 강조",Modifier.padding(horizontal=10.dp,vertical=6.dp),style=MaterialTheme.typography.labelMedium)
        }
    }
}

@Composable fun PriorityDetails(pack:ContentPack,priority:StudyPriority){
    var show by remember{mutableStateOf(false)}
    val uri=LocalUriHandler.current;val context=LocalContext.current
    Paper(accent=priority.level=="core"){
        PriorityBadge(priority)
        Text(priority.reason,style=MaterialTheme.typography.bodyMedium)
        if(priority.focusPoints.isNotEmpty()){
            Text("이것부터 확인하세요",style=MaterialTheme.typography.titleSmall)
            priority.focusPoints.forEach{Text("• $it",style=MaterialTheme.typography.bodyMedium)}
        }
        TextButton(onClick={show=true}){Text("중요도와 출제 근거")}
    }
    if(show)AlertDialog(onDismissRequest={show=false},title={Text("중요도와 출제 근거")},text={
        Column(Modifier.verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(12.dp)){
            Text(priority.frequencyNote)
            Text(pack.priorityMethodology)
            Text("자료 확인: ${pack.priorityCheckedAt}",style=MaterialTheme.typography.bodySmall)
            priority.sourceIds.mapNotNull{id->pack.sources.find{it.sourceId==id}}.forEach{source->
                Text(source.publisher+" · "+source.title,style=MaterialTheme.typography.titleSmall)
                if(source.url.startsWith("https://"))TextButton(onClick={runCatching{uri.openUri(source.url)}.onFailure{Toast.makeText(context,"자료 링크를 열 앱을 찾지 못했어요.",Toast.LENGTH_SHORT).show()}}){Text("자료 원문 열기")}
            }
        }
    },confirmButton={TextButton(onClick={show=false}){Text("닫기")}})
}

@Composable fun CoreProgressCard(ui:StudyUi){
    val progress=remember(ui.pack,ui.state.notes,ui.state.submissions){StudyGuide.coreProgress(ui.pack,ui.state)}
    if(progress.total==0)return
    val next=remember(ui.pack,ui.state.notes){StudyGuide.next(ui.pack,ui.state)}
    Paper(modifier=Modifier.testTag("core-progress")){
        Eyebrow("먼저 익힐 개념")
        Text("핵심 개념 진도",style=MaterialTheme.typography.titleLarge)
        Text("읽음 ${progress.read} / ${progress.total}",style=MaterialTheme.typography.titleMedium)
        LinearProgressIndicator(progress={progress.read.toFloat()/progress.total},modifier=Modifier.fillMaxWidth())
        Text("개념 확인 ${progress.recall} / ${progress.total} · 적용 확인 ${progress.application} / ${progress.total}")
        Text("확인은 현재 문항을 도움 없이 1개 이상 맞힌 주제 수예요. 모든 문제의 숙달을 뜻하지 않아요.",style=MaterialTheme.typography.bodySmall)
        if(next!=null){
            Text("다음 추천 · ${next.title}",style=MaterialTheme.typography.titleSmall)
            Text("필요한 선수 개념과 새로 보강된 내용도 함께 확인해요.",style=MaterialTheme.typography.bodySmall)
            OutlinedButton(onClick={ui.note(next.id)},modifier=Modifier.fillMaxWidth()){Text("추천 개념 펼치기")}
        }
    }
}
