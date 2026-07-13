# Cypher Context

## Recent Decisions
- POC Fingerling sprint scoped to pure-logic core: 4 stories (STORY-FING-01..04) covering
  telemetry tokenization, stateful upsert warehouse, ring-buffer sequence matcher, KubeArmor
  policy compiler. Webhook ingestion, sandbox provisioning, live exploit execution, and real
  GitOps commit/PR automation are explicitly OUT of POC scope — stubbed/deferred.
- Sprint 2 ("Live Ingestion & Pipeline Polish") scoped: 3 POC-cleanup stories from Sprint 1
  retro (STORY-FING-05 baseline-whitelist helper, STORY-FING-06 trajectory API alignment,
  STORY-FING-07 JSONPath wildcards) + STORY-FING-08, the first of three deferred infra epics.
  Chose webhook ingestion over sandbox provisioning/GitOps automation because it needs no
  external cluster/signing infra and unblocks real telemetry for later stories. 13 pts total.
  See `docs/USER_STORIES_SPRINT2.md`.

## Key Findings
- Full BRD/PRD/ARCH + 4 pre-written user stories already existed in `Finglering Initial Docs.md`
  at repo root before sprint start.
  - Formalized/condensed them into `docs/USER_STORIES.md` as the sprint backlog of record.
- Target velocity: 18 story points (5+5+5+3).

## Important Notes
- Enforcement gate math (Jaccard-based anomaly score, threshold A <= 0.05) belongs to
  STORY-FING-03/architecture — flagged for Morpheus to formalize in arch doc.
- No Tank (*devops) acceptance criteria needed for POC — no new env vars/CI/deploy changes since
  infra pieces are out of scope.

---
*Last updated: 2026-07-12T00:00*
