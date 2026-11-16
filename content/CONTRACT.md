# Content pack contract v1

## 2026-09-14 extension (app 0.2.0)

The original IDs, 600 question objects, and 308 existing note blocks are preserved. The current pack extends the IDs to M01..M13 and S01..S28: 41 notes and 661 published questions (178 recall, 233 application, 250 reserved mock questions). Original author allocations and targets below describe the initial pack, not a cap on the extension.

`study-priorities.json` provides one reviewed priority per objective: `core`, `important`, or `foundation`, with reasons, focus points, source IDs, and attributed educator emphasis where supported. These levels are study recommendations, not verified official exam probabilities. `legacy-note-versions.json` records the initial deployed versions for preserving read history when notes are expanded. New question publication requires recorded answer-masked review and explanation review; additions must pass `verify_priority_update.py` preservation checks.

UTF-8 JSON. Independent authored content; no copied exam questions. Root merges part-a.json and part-b.json into app assets. Every part: {"objectives": [...], "notes": [...], "questions": [...]}. Additional provenance fields allowed. Keep identifiers stable.

Objective: {id: "M01", subjectId: "model" or "sql", topicId: "A".."E", title, prerequisites: [objectiveId], synonyms: [string], scopeStatus: "provisional"}.

Note: {id:"note-M01", version:1, objectiveId:"M01", title, summary, sourceIds:[string], verification:"document_review", blocks:[{id:"M01-definition",kind:"definition|explain|example|compare|remember|misconception|recall|sql|table",title,text}], recallQuestionIds:[questionId]}. Each note must include substantive definition, easy explanation, precise conditions, concrete example, comparison, exceptions, misconception/counterexample, recall prompts. Blocks are selectable real text. SQL/table examples can be readable plain text; step tables use Table model below.

Question: {id,version:1,subjectId,topicId,objectiveIds:[id],familyId,kind:"recall|application|mock",title,stem,choices:[{id:"a",text,reason},... b/c/d],correctChoiceIds:["a"],explanation:{summary,prerequisites:[string],conditions:[string],steps:[{title,text,table?:Table}],memory,relatedNoteId},sourceIds:[string],sourceType:"original_practice|original_mock",verification:"document_review|engine_verified|cross_reviewed|draft",status:"published|quarantined|draft",dialect:"conceptual|Oracle|SQL Server",dialectVersion:"19c|2022|n/a",difficulty:"basic|intermediate",difficultyReason,importanceReason,fixture?:{schemaSql,setupSql,query,expectedRows:[[string|null]],ordered:boolean,constraints:[string],sessionSettings:[string],verificationMethod,evidence},sql?:string,tables:[Table],mockSetId?:"mock-1".."mock-5",validationEvidence:[string]}.

Table: {title,columns:[string],rows:[[string|null]]}. Null JSON means SQL NULL, empty string stays distinct. Do not label document-reviewed Oracle as engine tested.

All answers one choice, four plausible options, detailed option reasons. No position-dependent options. Unseen mock families strictly disjoint from practice; same template number/name variants don't count as independent. For now reserve all mock questions, not searchable before a mock is entered. All 5 sets must each total model=10/sql=40 before enabled. No incomplete sets enabled.

IDs: M01..M10 model topics per source agent; S01..S24 SQL. Q ids: M01-R01 / M01-A01 / mock-1-M01 etc; choose stable descriptive suffixes for multiple scenarios. Entire content goal recall=150 application=200 mock=250, quality gate takes priority. Honest count and gaps in report. If author review only, state that; never mark AI/expert independent review not performed. Questions drafted in published can be downgraded by validator/reviewer before pack build.

Part A owns M01-M10 and S01-S08; Part B owns S09-S24. Proposed practice target each 75 recall +100 application. Mock A owns 10 model questions and 12 SQL questions per set (110 total), B owns 28 SQL questions per set (140 total). In each set use new scenarios/families, not repetitions of practice or another set. Write in reviewed batches; do not pad counts by swapping values/names. Notes and representative working flow first, breadth second, quantities third. Generator helpers may serialize authored tuples; do not fabricate AI independent review.
