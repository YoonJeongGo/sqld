package kr.sqld.study

import kotlinx.serialization.encodeToString
import org.junit.Assert.*
import org.junit.Test

class InkStoreTest {
    private fun document()=InkStore.empty("question:q1:source-fingerprint","SELECT COUNT(*) FROM T")
    private fun stroke(id:String="stroke-1")=InkStroke(id,points=listOf(InkPoint(10f,20f,.5f),InkPoint(100f,20f,1f)))
    @Test fun changedSqlAndChangedSourceBothGetNewDocumentIdentities(){
        val doc=document()
        assertTrue(InkStore.matches(doc,doc.sourceId,"SELECT COUNT(*) FROM T"))
        assertFalse(InkStore.matches(doc,doc.sourceId,"SELECT COUNT(value) FROM T"))
        assertFalse(InkStore.matches(doc,"question:q1:changed-table","SELECT COUNT(*) FROM T"))
    }
    @Test fun undoRedoAndEraseRestoreExactStrokeCoordinates(){
        val first=InkStore.add(document(),stroke(),1)
        val second=InkStore.add(first,stroke("stroke-2"),2)
        val erased=InkStore.erase(second,listOf("stroke-1"),3)
        assertEquals(listOf("stroke-2"),InkStore.visibleStrokes(erased).map{it.id})
        assertEquals(InkStore.visibleStrokes(second),InkStore.visibleStrokes(InkStore.undo(erased,4)))
        assertEquals(InkStore.visibleStrokes(erased),InkStore.visibleStrokes(InkStore.redo(InkStore.undo(erased,4),5)))
        val replacement=InkStore.add(InkStore.undo(erased,6),stroke("stroke-3"),7)
        assertEquals(3,replacement.cursor)
        assertEquals(listOf("stroke-1","stroke-2","stroke-3"),InkStore.visibleStrokes(replacement).map{it.id})
    }
    @Test fun sparseStrokeCanBeErasedBetweenSamples(){
        assertTrue(InkStore.hit(stroke(),50f,20f,2f))
        assertFalse(InkStore.hit(stroke(),50f,50f,2f))
    }
    @Test fun backupPreservesInkWithUndoHistoryAndExistingStudyRecords(){
        val ink=InkStore.undo(InkStore.add(InkStore.add(document(),stroke(),1),stroke("stroke-2"),2),3)
        val state=StudyState(annotations=listOf(Annotation("memo","note","block","quote","내 메모","memo",1)),bookmarks=listOf(Bookmark("q1",1)),inkDocuments=listOf(ink))
        val restored=BackupCodec.decode(BackupCodec.encode(state,1))
        assertEquals(state,restored)
        assertEquals(2,InkStore.visibleStrokes(InkStore.redo(restored.inkDocuments.single(),4)).size)
    }
    @Test fun versionTwoBackupWithoutInkUpgradesWithoutChangingOtherFields(){
        val old=StudyState(schemaVersion=2,bookmarks=listOf(Bookmark("old",7)),annotations=listOf(Annotation("a","n","b","q","기존 메모","memo",3)))
        val payload=Codec.encodeToString(old).replace(",\"inkDocuments\":[]","")
        val encoded=Codec.encodeToString(BackupEnvelope(schemaVersion=2,createdAt=1,sha256=BackupCodec.hash(payload),payload=payload))
        val next=BackupCodec.decode(encoded)
        assertEquals(old.copy(schemaVersion=BackupCodec.CURRENT_VERSION),next)
        assertTrue(next.inkDocuments.isEmpty())
    }
    @Test fun malformedCoordinatesIdsReferencesAndLimitsAreRejectedBeforeRestore(){
        val valid=InkStore.add(document(),stroke(),1)
        fun rejects(document:InkDocument){assertThrows(IllegalArgumentException::class.java){InkStore.validate(listOf(document))}}
        rejects(valid.copy(id="wrong"));rejects(valid.copy(cursor=2));rejects(valid.copy(sourceHash="bad"))
        listOf(Float.NaN,Float.POSITIVE_INFINITY,-1f,InkStore.MAX_COORDINATE+1f).forEach{bad->
            rejects(valid.copy(edits=listOf(valid.edits.single().copy(stroke=stroke().copy(points=listOf(InkPoint(bad,10f)))))))
        }
        rejects(valid.copy(edits=valid.edits+valid.edits))
        rejects(valid.copy(edits=valid.edits+InkEdit("bad-erase",erasedIds=listOf("missing"))))
        rejects(valid.copy(edits=listOf(valid.edits.single().copy(stroke=stroke().copy(points=List(InkStore.MAX_POINTS_PER_STROKE+1){InkPoint(1f,1f)})))))
        assertThrows(IllegalArgumentException::class.java){InkStore.validate(listOf(valid,valid))}
    }
    @Test fun upsertPreservesUnrelatedDocumentsAndDoesNotDuplicate(){
        val first=InkStore.add(document(),stroke(),1)
        val other=InkStore.empty("other","SELECT 2")
        val before=StudyState(inkDocuments=listOf(other,first),bookmarks=listOf(Bookmark("keep",1)))
        val next=InkStore.upsert(before,InkStore.undo(first,2))
        assertEquals(2,next.inkDocuments.size);assertEquals(other,next.inkDocuments.first());assertEquals(before.bookmarks,next.bookmarks)
    }
}
