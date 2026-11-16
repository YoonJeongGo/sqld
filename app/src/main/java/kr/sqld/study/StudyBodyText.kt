package kr.sqld.study

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.*
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.LineBreak
import androidx.compose.ui.unit.dp

/** The source, SQL blocks and learner records are never rewritten by this renderer. */
@Composable internal fun StudyBodyText(
    text:String,modifier:Modifier=Modifier,emphasis:List<String> = emptyList(),
    inlineCodes:List<String> = emptyList(),active:List<String> = emptyList(),
    style:TextStyle=MaterialTheme.typography.bodyLarge
){
    val plan=remember(text,emphasis,inlineCodes,active){BodyTextRules.plan(text,emphasis,inlineCodes,active)}
    val ink=MaterialTheme.colorScheme.onSurface
    val annotated=remember(plan,ink){buildAnnotatedString{
        append(plan.text)
        plan.code.forEach{addStyle(SpanStyle(fontFamily=FontFamily.Monospace),it.first,it.last+1)}
        plan.strong.forEach{addStyle(SpanStyle(fontWeight=FontWeight.Bold),it.first,it.last+1)}
        plan.active.forEach{addStyle(SpanStyle(fontWeight=FontWeight.Bold,background=ReadingBlue,color=ReadingInk),it.first,it.last+1)}
    }}
    SelectionContainer {
        Column(modifier,verticalArrangement=Arrangement.spacedBy(10.dp)){
            plan.paragraphs.forEach { range ->
                Text(annotated.subSequence(range.first,range.last+1),color=ink,
                    style=style.copy(fontWeight=FontWeight.Normal,lineHeight=style.fontSize*1.6f,
                        lineBreak=LineBreak.Paragraph),softWrap=true)
            }
        }
    }
}

@Composable internal fun StudySection(title:String,modifier:Modifier=Modifier,content:@Composable ColumnScope.()->Unit){
    Column(modifier.fillMaxWidth(),verticalArrangement=Arrangement.spacedBy(8.dp)){
        Text(title,style=MaterialTheme.typography.titleMedium,color=MaterialTheme.colorScheme.onSurface)
        content()
    }
}

/** Compact spacing only for learning content; navigation and dashboard cards keep their design. */
@Composable internal fun StudyPaper(modifier:Modifier=Modifier,accent:Boolean=false,content:@Composable ColumnScope.()->Unit){
    Surface(modifier.fillMaxWidth(),color=if(accent)MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface,
        contentColor=MaterialTheme.colorScheme.onSurface,shape=RoundedCornerShape(20.dp),
        border=BorderStroke(1.dp,MaterialTheme.colorScheme.outlineVariant.copy(alpha=.7f))){
        Column(Modifier.padding(16.dp),verticalArrangement=Arrangement.spacedBy(8.dp),content=content)
    }
}

@Composable internal fun StudyWarning(text:String){
    Column(verticalArrangement=Arrangement.spacedBy(6.dp)){
        Text("주의",style=MaterialTheme.typography.labelLarge,color=MaterialTheme.colorScheme.secondary)
        StudyBodyText(text)
    }
}
