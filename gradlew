{
  "masterRun": "POST_N4_TO_N1_SINGLE_PASS",
  "startedAt": "2026-07-24T11:15:46+09:00",
  "updatedAt": "2026-07-26T17:27:30+09:00",
  "runControl": {
    "status": "running",
    "pausedAt": "2026-07-25T16:41:09+09:00",
    "resumedAt": "2026-07-26T17:27:30+09:00",
    "resumeCheckpoint": "docs/run/N2_WIP_PAUSE_CHECKPOINT_2026-07-25.md",
    "resumeInstruction": "Continue from the checkpoint when the user says 다시 진행해; do not regenerate completed artifacts."
  },
  "workspaceMigration": {
    "migratedAt": "2026-07-26T17:00:42+09:00",
    "previousWorkspace": "C:\\Users\\박강열\\Desktop\\JLPT 앱",
    "canonicalWorkspace": "D:\\JLPT앱",
    "sourceRetainedAsBackup": true,
    "verification": "51871 files copied; 0 failures; 0 mismatches; critical SHA-256 matched; D-drive typecheck PASS",
    "record": "docs/run/WORKSPACE_MIGRATION_2026-07-26.md"
  },
  "targetLevelSequence": ["N3", "N2", "N1"],
  "formalQaPolicy": "FINAL_ONLY",
  "git": {
    "available": false,
    "reason": ".git/HEAD is absent"
  },
  "storageSchemaVersion": 5,
  "backupSchemaVersion": 2,
  "phases": {
    "phase-00-current-n4-completion": {
      "status": "completed",
      "startedAt": "2026-07-24T11:15:46+09:00",
      "completedAt": "2026-07-24T11:24:39+09:00",
      "remaining": []
    },
    "phase-01-card-variant-v2": {
      "status": "completed",
      "startedAt": "2026-07-24T11:24:39+09:00",
      "completedAt": "2026-07-24T14:32:44+09:00",
      "audit": "docs/run/audits/PHASE01_CARDVARIANT_GAP.md",
      "checkpoint": "docs/checkpoints/CARD_VARIANT_V2_CHECKPOINT.md",
      "resolvedGaps": [
        "Ambiguous v1/v2 item-level reviews and queues migrate exactly once to legacy_mixed.",
        "SQLite v3/v4 data upgrades transactionally to v5 with rollback and idempotency coverage.",
        "Full backup import uses a durable before-image journal and a startup recovery gate."
      ]
    },
    "phase-02-learning-sets-v3": {
      "status": "completed",
      "startedAt": "2026-07-24T14:32:44+09:00",
      "completedAt": "2026-07-24T16:55:24+09:00",
      "audit": "docs/run/audits/PHASE02_LEARNING_SETS_GAP.md",
      "checkpoint": "docs/checkpoints/LEARNING_SETS_V3_CHECKPOINT.md",
      "resolvedGaps": [
        "Stable levelOrder now derives 50/25-item learning sets and dynamic 200-item kanji/vocabulary chapters independently of storage batches.",
        "Daily-new limits count unique ContentItems while due and remediation CardVariants retain queue priority.",
        "Selection v3 persists range coordinates while active legacy 100-item sessions retain their original selection and queue."
      ]
    },
    "phase-03-n3-content": {
      "status": "completed",
      "startedAt": "2026-07-24T16:55:24+09:00",
      "completedAt": "2026-07-25T14:15:42+09:00",
      "checkpoint": "docs/checkpoints/N3_COMPLETION_CHECKPOINT.md"
    },
    "phase-04-n2-content": {
      "status": "in_progress",
      "startedAt": "2026-07-25T14:15:42+09:00",
      "completedAt": null
    },
    "phase-05-n1-content": {
      "status": "not_started",
      "startedAt": null,
      "completedAt": null
    },
    "phase-06-final-all-level-qa": {
      "status": "not_started",
      "startedAt": null,
      "completedAt": null
    },
    "phase-07-final-build-and-report": {
      "status": "not_started",
      "startedAt": null,
      "completedAt": null
    }
  },
  "levels": {
    "N5": {
      "status": "completed_baseline",
      "contentVersion": "2026.07.23-n5-v1",
      "manifestContentHash": "6b0e969f47af35b92b8d393a77c34b762f9872ac29bd433adfd47362c8e78d10",
      "manifestFileSha256": "9386F85CA84B4180790EC8073AEC1E0E9885A6E85514D3EEB38C6B80407E1C38",
      "counts": {
        "kanji": 80,
        "vocabulary": 661,
        "grammar": 40,
        "total": 781,
        "examples": 1522,
        "storageBatches": 9
      }
    },
    "N4": {
      "status": "completed",
      "contentVersion": "2026.07.23-n4-v1",
      "manifestContentHash": "4abc43190fdc1f6a091e89a593e9af82cfc1eed1235af89de4f9c986096994d6",
      "manifestFileSha256": "1B23C26E4B387F0F99FAF6996B57E9C765DE0617F6E685E2991419EB3381C497",
      "counts": {
        "kanji": 166,
        "vocabulary": 634,
        "grammar": 50,
        "total": 850,
        "examples": 1584,
        "storageBatches": 10
      }
    },
    "N3": {
      "status": "completed",
      "contentVersion": "2026.07.24-n3-v1",
      "manifestContentHash": "84b3e7f4f1ad7fb9e49b8c92748cfbaded69c39cbbbc1fb928fcc0df22f69704",
      "manifestFileSha256": "A799D577760B72D70C7DB79BE34134127F093590EE5437480CA3FBB55485E072",
      "candidateCounts": {
        "vocabularyRaw": 1801,
        "vocabularyMerged": 1789,
        "vocabularyNew": 1640,
        "vocabularyReused": 130,
        "vocabularySplitSenses": 12,
        "vocabularyExcludedLowConfidence": 20,
        "kanjiNew": 367,
        "kanjiReused": 0,
        "grammarSelected": 62,
        "grammarNew": 59,
        "grammarReused": 3
      },
      "counts": {
        "kanji": 367,
        "vocabulary": 1770,
        "grammar": 62,
        "total": 2199,
        "new": 2066,
        "reused": 133,
        "examples": 4093,
        "cardVariants": 6230,
        "storageBatches": 23
      },
      "review": {
        "itemsAiCrossChecked": 2199,
        "examplesAiCrossChecked": 4093,
        "humanVerified": 0,
        "crossReviewFiles": 25,
        "crossReviewItems": 2196,
        "crossReviewExamples": 4084,
        "correctedItemDecisions": 524,
        "correctedExampleDecisions": 1185,
        "globalExactJapaneseDuplicates": 0,
        "globalDuplicateExampleIds": 0
      },
      "confidence": {
        "high": 1701,
        "medium": 498,
        "low": 0
      },
      "postProcessing": {
        "sourceCrosscheck": "completed",
        "metadata": "completed",
        "cloze": "completed",
        "usedIds": "completed",
        "tokens": "completed",
        "levelOrder": "completed",
        "manifestValidation": "completed",
        "contentIndex": "completed"
      },
      "batches": {
        "n3-grammar-batch-001": "completed",
        "n3-grammar-reuse-batch-001": "completed",
        "n3-kanji-batch-001": "completed",
        "n3-kanji-batch-002": "completed",
        "n3-kanji-batch-003": "completed",
        "n3-kanji-batch-004": "completed",
        "n3-vocabulary-batch-001": "completed",
        "n3-vocabulary-batch-002": "completed",
        "n3-vocabulary-batch-003": "completed",
        "n3-vocabulary-batch-004": "completed",
        "n3-vocabulary-batch-005": "completed",
        "n3-vocabulary-batch-006": "completed",
        "n3-vocabulary-batch-007": "completed",
        "n3-vocabulary-batch-008": "completed",
        "n3-vocabulary-batch-009": "completed",
        "n3-vocabulary-batch-010": "completed",
        "n3-vocabulary-batch-011": "completed",
        "n3-vocabulary-batch-012": "completed",
        "n3-vocabulary-batch-013": "completed",
        "n3-vocabulary-batch-014": "completed",
        "n3-vocabulary-batch-015": "completed",
        "n3-vocabulary-batch-016": "completed",
        "n3-vocabulary-batch-017": "completed",
        "n3-vocabulary-batch-018": "completed",
        "n3-vocabulary-reuse-batch-001": "completed",
        "n3-vocabulary-reuse-batch-002": "completed"
      }
    },
    "N2": {
      "status": "in_progress",
      "candidateCounts": {
        "vocabularyRaw": 1831,
        "vocabularyMerged": 1783,
        "vocabularyNew": 1727,
        "vocabularyReused": 56,
        "vocabularyExcludedLowConfidence": 28,
        "vocabularyHeldForSenseAudit": 12,
        "vocabularySuspiciousSenseJoins": 100,
        "vocabularyReviewedSenseRulesApplied": 35,
        "vocabularyReviewedSenseRulesConfigured": 35,
        "kanjiNew": 367,
        "kanjiReused": 0,
        "grammarSelected": 62,
        "grammarNew": 60,
        "grammarReused": 2,
        "grammarExcluded": 1
      },
      "batches": {
        "n2-vocabulary-batch-001": "ai_cross_checked",
        "n2-vocabulary-batch-002": "ai_cross_checked",
        "n2-vocabulary-batch-003": "ai_cross_checked",
        "n2-vocabulary-batch-004": "ai_cross_checked",
        "n2-vocabulary-batch-005": "ai_cross_checked",
        "n2-vocabulary-batch-006": "ai_cross_checked",
        "n2-vocabulary-batch-007": "ai_cross_checked",
        "n2-vocabulary-batch-008": "ai_cross_checked",
        "n2-vocabulary-batch-009": "ai_cross_checked_old_packet_reconcile_pending",
        "n2-vocabulary-batch-010": "ai_cross_checked_old_packet_reconcile_pending",
        "n2-vocabulary-batch-011": "ai_cross_checked_old_packet_reconcile_pending",
        "n2-vocabulary-batch-012": "ai_cross_checked_old_packet_rec