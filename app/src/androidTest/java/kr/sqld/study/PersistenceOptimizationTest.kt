package kr.sqld.study

import android.content.Context
import android.util.Log
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.encodeToString
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import java.util.concurrent.Executor
import java.util.concurrent.atomic.AtomicInteger

/** In-memory Room and an isolated projection writer never touch the user's saved records. */
@RunWith(AndroidJUnit4::class)
class PersistenceOptimizationTest {
    private lateinit var context:Context
    private val databases=mutableListOf<StudyDatabase>()
    private fun database(reads:AtomicInteger?=null):StudyDatabase =
        Room.inMemoryDatabaseBuilder(context,StudyDatabase::class.java)
            .setQueryCallback(RoomDatabase.QueryCallback { sql,_ ->
                if(sql=="SELECT * FROM study_state WHERE id=1")reads?.incrementAndGet()
            },Executor { it.run() })
            .build().also{databases+=it}

    @Before fun before(){context=InstrumentationRegistry.getInstrumentation().targetContext}
    @After fun after(){databases.forEach{it.close()}}

    @Test fun noOpUsesOneAuthoritativeReadAndKeepsRevision()=runBlocking<Unit> {
        val reads=AtomicInteger()
        val repo=StudyRepository(context,database(reads),projectPreferences=false)
        repo.initialize()
        val before=repo.state.value
        reads.set(0)
        repeat(20){repo.update{it}}
        assertEquals(before,repo.state.value)
        assertEquals(20,reads.get())
        Log.i("PersistenceOptimization","20 no-op updates: ${reads.get()} state SELECTs; revision unchanged")
    }

    @Test fun updateStillReadsCommittedRoomStateInsteadOfUsingStaleMemory()=runBlocking<Unit> {
        val repo=StudyRepository(context,database(),projectPreferences=false)
        repo.initialize()
        val external=repo.state.value.copy(revision=repo.state.value.revision+1,
            bookmarks=listOf(Bookmark("external-record",123)),settings=AppSettings(theme="dark"))
        repo.db.dao().save(StateRow(revision=external.revision,payload=Codec.encodeToString(external)))
        assertNotEquals(external,repo.state.value)
        val actual=repo.update{it.copy(lastNoteId="note-S01")}
        assertEquals(external.copy(revision=external.revision+1,lastNoteId="note-S01"),actual)
    }

    @Test fun settingsProjectionRunsOnlyInitiallyOrWhenSettingsChangeIncludingRestore()=runBlocking<Unit> {
        val projected=mutableListOf<AppSettings>()
        val repo=StudyRepository(context,database(),settingsProjectionWriter={projected+=it})
        repo.initialize()
        assertEquals(listOf(AppSettings()),projected)
        repeat(20){i->repo.update{state->CourseStudy.update(state,"test-lesson",{it.copy(scroll=i)},now=i.toLong())}}
        repeat(20){repo.update{it}}
        assertEquals(1,projected.size)
        repo.update{it.copy(settings=it.settings.copy(theme="dark"))}
        assertEquals(listOf("system","dark"),projected.map{it.theme})
        repo.update{it.copy(settings=it.settings.copy())}
        repo.restore(repo.state.value.copy(settings=AppSettings(theme="light")))
        repo.restore(repo.state.value)
        assertEquals(listOf("system","dark","light"),projected.map{it.theme})
        Log.i("PersistenceOptimization","20 progress + 20 no-op updates: 0 additional settings projections; changes and restore each project once")
    }

    @Test fun failedInitialAndChangedSettingsProjectionsRetryWithoutLosingRoomWrites()=runBlocking<Unit> {
        var fail=true
        var attempts=0
        val projected=mutableListOf<AppSettings>()
        val repo=StudyRepository(context,database(),settingsProjectionWriter={
            attempts++
            if(fail)error("injected projection failure")
            projected+=it
        })
        repo.initialize()
        assertEquals(1,attempts)
        assertTrue(projected.isEmpty())
        fail=false
        val before=repo.state.value
        repo.update{it}
        assertEquals(before,repo.state.value)
        assertEquals(2,attempts)
        assertEquals(listOf("system"),projected.map{it.theme})
        fail=true
        repo.update{it.copy(settings=it.settings.copy(theme="dark"))}
        assertEquals("dark",repo.state.value.settings.theme)
        assertEquals(3,attempts)
        fail=false
        repo.update{it}
        assertEquals(4,attempts)
        assertEquals(listOf("system","dark"),projected.map{it.theme})
        repo.update{it}
        assertEquals(4,attempts)
    }

    @Test fun failedRoomWriteDoesNotProjectOrCacheUncommittedSettings()=runBlocking<Unit> {
        val projected=mutableListOf<AppSettings>()
        val repo=StudyRepository(context,database(),settingsProjectionWriter={projected+=it})
        repo.initialize()
        val before=repo.state.value
        repo.failNextWrite=true
        assertNotNull(runCatching{repo.update{it.copy(settings=AppSettings(theme="dark"))}}.exceptionOrNull())
        assertEquals(before,repo.state.value)
        assertEquals(listOf("system"),projected.map{it.theme})
        repo.update{it.copy(settings=AppSettings(theme="dark"))}
        assertEquals(listOf("system","dark"),projected.map{it.theme})
    }
}
