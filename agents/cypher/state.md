# Agent State

## Context
## Recent Decisions
- Sprint 7 (fast-track, Tier 2): STORY-FING-22, 3 pts, "Comprehensive Input-Validation Policy
  Demo" — add a `;`-pattern-based comprehensive block alongside the existing exact-fingerprint
  block, entirely via fingerling's simulated KubeArmor enforcement layer, with zero changes to
  the vulnerable line in `vulnerable_app.py`. Chose **block** over silent **sanitize** (flagged
  explicitly for Smith gate — a demo that visibly rejects `;` payloads is more legible than one
  that silently rewrites them). See `docs/USER_STORIES_SPRINT7.md` for full stories+arch.
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
- 2026-10-12 fingerprint feature assessment (`*pm assess fingerprint`), from reading
  `fingerling/tokenizer.py`, `warehouse.py`, `ringbuffer.py`, `capture.py`:
  - Shipped: JSONPath subset (dot, [i], [*], ..), 5 modifiers (DEFAULT, IS_PRESENT, IS_NULL,
    IN_RANGE, ANY), wildcard token aggregation, parse_jsonl, MD5 fingerprint_id, Warehouse
    upsert/get/save/load with 3-sample ring, build_whitelist, SlidingWindowMatcher (binary score
    + warm), bpftrace execve capture CLI (`python -m fingerling.capture`).
  - Spec gaps: GLOB/REGEX modifiers, Jaccard anomaly score + 0.05 gate, environment-aware
    baselines / prod-drift-as-anomaly, friendly fingerprint names.
  - Product gaps (not in spec): no fingerprint CLI, mask profiles are hardcoded Python lists in
    examples (no file format), whitelist not persisted, one global stream (no per-PID/workload
    windows), no way to explain a fingerprint or diff two warehouses.
- 2026-10-12 Sprint 8 direction from User (fingerprint sampling CLI):
  - CLI is independent of eBPF capture; general-purpose sampler for any JSONL event stream.
  - Core contract: existing fingerprint set + JSONL stream -> updated set, merged across runs.
  - Replace hand-rolled JSONPath with a library, full syntax (reverses 2026-07-12 decision).
  - Aggregators SUM/AVG/MIN/MAX/LAST(n), across events per fingerprint; LAST(n) replaces the
    hardcoded 3-sample ring.
  - N-grams/baselines/scoring are a LATER stage — User was explicit: do not conflate them with
    the fingerprint sampling tool. ringbuffer.py untouched.
  - My assumption (not confirmed by User): hardcoded duration min/max + sample ring are removed
    outright rather than shimmed. Listed as Open Question 1 for Morpheus.
- 2026-10-12 User ran /sprint 'fingerprint cli till done' — Sprint 8 is go, full ceremony.
- 2026-10-12 Sprint 8 launched 2026-10-12: FING-23..26 delivered, 16/16 pts, 178 tests. Backlog recorded in task.md.

## Current Task
**Sprint:** 8 — Fingerprint Sampling CLI (`docs/USER_STORIES_SPRINT8.md`, board: `task.md`)
**Status:** Sprint 8 complete — launched

## Next Steps
No sprint in flight. Next fingerprint iteration candidates: GLOB/REGEX, set report view, event-time timestamps, then n-gram stage. Next story ID: STORY-FING-27.

---
*Last updated: 2026-10-12T21:29:12-04:00*
