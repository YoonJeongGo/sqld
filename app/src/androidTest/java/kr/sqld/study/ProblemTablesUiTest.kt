package kr.sqld.study

import android.app.Application
import android.graphics.Bitmap
import androidx.activity.ComponentActivity
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.unit.dp
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

/** Source-table rendering only; no learner repository or personal records are opened. */
@RunWith(AndroidJUnit4::class)
class ProblemTablesUiTest {
    @get:Rule val compose=createAndroidComposeRule<ComponentActivity>()
    @Test fun representativeLargestOriginalTablesStayVisibleTogether(){
        val app=ApplicationProvider.getApplicationContext<Application>()
        val pack=Codec.decodeFromString<ContentPack>(app.assets.open("content-pack.json").bufferedReader().use{it.readText()})
        val candidates=pack.questions.filter{it.tables.isNotEmpty()}.sortedByDescending{q->q.tables.sumOf{it.rows.size*it.columns.size}}
            .take(10)+pack.questions.filter{it.tables.size==3}.take(2)
        val tables=mutableStateOf(candidates.first().tables)
        val width=mutableStateOf(600.dp)
        compose.setContent{SqlNoteTheme(false,1f){Surface{Box(Modifier.width(width.value).height(520.dp).testTag("source-tables-viewport")){ProblemTables(tables.value)}}}}
        listOf(600.dp,599.5.dp).forEach{testWidth->
        compose.runOnUiThread{width.value=testWidth}
        candidates.distinctBy{it.id}.forEach{q->
            compose.runOnUiThread{tables.value=q.tables};compose.waitForIdle()
            val viewport=compose.onNodeWithTag("source-tables-viewport").getUnclippedBoundsInRoot()
            val blocks=compose.onAllNodesWithTag("problem-table").fetchSemanticsNodes()
            assertEquals(q.tables.size,blocks.size)
            blocks.indices.forEach{at->
                val bounds=compose.onAllNodesWithTag("problem-table")[at].getUnclippedBoundsInRoot()
                assertTrue("${q.id} table right edge",bounds.right<=viewport.right)
                assertTrue("${q.id} table bottom",bounds.bottom<=viewport.bottom)
            }
            q.tables.forEach{table->table.columns.forEach{column->compose.onAllNodesWithText(column).fetchSemanticsNodes().forEach{node->
                assertTrue("${q.id} column $column",node.boundsInRoot.right<=compose.onNodeWithTag("source-tables-viewport").fetchSemanticsNode().boundsInRoot.right+1f)
            }}}
        }
        }
        val bitmap=InstrumentationRegistry.getInstrumentation().uiAutomation.takeScreenshot()
        File(app.cacheDir,"unit-source-tables.png").outputStream().use{bitmap.compress(Bitmap.CompressFormat.PNG,100,it)}
        bitmap.recycle()
    }
}
