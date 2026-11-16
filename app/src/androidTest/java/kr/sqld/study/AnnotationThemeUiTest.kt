package kr.sqld.study

import android.text.Spanned
import android.text.style.BackgroundColorSpan
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class AnnotationThemeUiTest {
    @get:Rule val compose=createAndroidComposeRule<ComponentActivity>()
    private fun textViews(view:View):List<TextView> = when(view){
        is TextView -> listOf(view)
        is ViewGroup -> (0 until view.childCount).flatMap{textViews(view.getChildAt(it))}
        else -> emptyList()
    }
    @Test fun changingThemeUpdatesAnExistingNativeHighlightWithoutChangingTheAnnotation(){
        val dark=mutableStateOf(false)
        val annotation=Annotation("theme-check","note-M01","M01-01","중요한 문장","","highlight",1)
        var expectedColor=0
        compose.setContent{SqlNoteTheme(dark.value,1f){
            expectedColor=MaterialTheme.colorScheme.secondaryContainer.toArgb()
            SelectableNoteText("중요한 문장을 다시 읽어요",listOf(annotation),1f){_,_->}
        }}
        lateinit var original:TextView
        var lightColor=0
        compose.runOnIdle{
            original=textViews(compose.activity.findViewById(android.R.id.content)).single{it.text.toString()=="중요한 문장을 다시 읽어요"}
            lightColor=(original.text as Spanned).getSpans(0,original.text.length,BackgroundColorSpan::class.java).single().backgroundColor
            assertEquals(expectedColor,lightColor)
            dark.value=true
        }
        compose.runOnIdle{
            val current=textViews(compose.activity.findViewById(android.R.id.content)).single{it.text.toString()=="중요한 문장을 다시 읽어요"}
            assertSame(original,current)
            val span=(current.text as Spanned).getSpans(0,current.text.length,BackgroundColorSpan::class.java).single()
            assertNotEquals(lightColor,expectedColor)
            assertEquals(expectedColor,span.backgroundColor)
            assertEquals("중요한 문장",annotation.quote)
        }
    }
}
