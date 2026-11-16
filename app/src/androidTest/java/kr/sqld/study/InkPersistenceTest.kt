package kr.sqld.study

import androidx.room.Room
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.util.UUID

@RunWith(AndroidJUnit4::class)
class InkPersistenceTest {
    @Test fun reopenExportRestoreAndInjectedSaveFailurePreserveInkAndOldMemo()=runBlocking {
        val context=InstrumentationRegistry.getInstrumentation().targetContext
        val name="sql-ink-test-${UUID.randomUUID()}.db"
        var db=Room.databaseBuilder(context,StudyDatabase::class.java,name).build()
        try {
            val first=StudyRepository(context,db,projectPreferences=false);first.initialize()
            val note=first.pack.notes.first();val block=note.blocks.first()
            val ink=InkStore.add(InkStore.empty("question:ink-test","SELECT 1"),InkStroke("first",points=listOf(InkPoint(15f,25f),InkPoint(45f,25f))),1)
            val before=first.update{InkStore.upsert(it.copy(annotations=listOf(Annotation("keep",note.id,block.id,block.text.take(20),"기존 메모","memo",1))),ink)}
            first.failNextWrite=true
            val pending=InkStore.add(ink,InkStroke("second",points=listOf(InkPoint(25f,35f),InkPoint(55f,35f))),2)
            assertTrue(runCatching{first.update{InkStore.upsert(it,pending)}}.isFailure)
            assertEquals(before,first.state.value)
            // The caller can retry the same immutable draft, with no duplicate strokes.
            val saved=first.update{InkStore.upsert(it,pending)}
            val backup=first.export()
            db.close();db=Room.databaseBuilder(context,StudyDatabase::class.java,name).build()
            val reopened=StudyRepository(context,db,projectPreferences=false);reopened.initialize()
            assertEquals(saved.inkDocuments,reopened.state.value.inkDocuments)
            assertEquals(saved.annotations,reopened.state.value.annotations)
            val candidate=BackupCodec.decode(backup);reopened.restore(candidate)
            assertEquals(saved.inkDocuments,reopened.state.value.inkDocuments)
            assertEquals(saved.annotations,reopened.state.value.annotations)
            assertEquals(saved.inkDocuments,reopened.recoveryCandidate()!!.inkDocuments)
        } finally {if(db.isOpen)db.close();context.deleteDatabase(name)}
    }
}
