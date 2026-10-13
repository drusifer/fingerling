# Task Board — Sprint 8: Fingerprint Sampling CLI

**Status:** Sprint 8 complete — launched 2026-10-12 (16/16 pts, 178 tests)
**Source:** `docs/USER_STORIES_SPRINT8.md` (stories + architecture D1-D8)
**Sprint Log:** `agents/mouse/sprint_log.md`
**Points:** 16 · **Tier:** 1

Previous sprints (1-7) are closed; see `agents/mouse/sprint_log.md`.

---

## Phase 1: JSONPath library (STORY-FING-23, 3 pts)
- [x] **1.1** `make install` (.venv, `--system-site-packages`) + `python-jsonpath` in `requirements.txt`; Makefile uses the venv interpreter when present. [Neo]
- [x] **1.2** Replace hand-rolled resolver in `fingerling/tokenizer.py` with `compile_path` / `find_values`; match-count token semantics; tests for filters, slices, unions, descent, invalid paths. [Neo]
- [x] **1.3** UAT + code review. [Trin, Morpheus]

## Phase 2: Aggregators + fingerprint set (STORY-FING-25, 5 pts)
- [ ] **2.1** `fingerling/aggregators.py`: `AggregateEntry`, spec parsing, `SUM`/`AVG`/`MIN`/`MAX`/`LAST(n)` update. [Neo]
- [ ] **2.2** Refactor `fingerling/warehouse.py` to the versioned set (tokens, aggregates, profile_id, atomic save); migrate `server.py`, `build_whitelist`, examples and tests off `upsert(duration_ms, raw_record)`. [Neo]
- [ ] **2.3** UAT + code review. [Trin, Morpheus]

## Phase 3: Profile file (STORY-FING-24, 3 pts)
- [x] **3.1** `fingerling/profile.py`: `Profile`, `load_profile`, `profile_id`, load-time validation; example profile in repo. [Neo]
- [x] **3.2** UAT + code review. [Trin, Morpheus]

## Phase 4: `fingerprint` CLI (STORY-FING-26, 5 pts)
- [ ] **4.1** `fingerling/cli.py` + `__main__.py`: stream merge, `-o`, `--force-profile`, exit codes, stderr summary, TTY guard, friendly missing-dependency message. [Neo]
- [ ] **4.2** `make fingerprint` target; non-eBPF fixture test; batch-vs-split equivalence test. [Neo]
- [ ] **4.3** UAT + code review. [Trin, Morpheus]

## Close
- [x] Oracle groom (ARCH / DECISIONS / USER_GUIDE / README / LESSONS) [Oracle]
- [x] Smith end-to-end user test [Smith]
- [x] Retro + launch [All, Cypher]

## Definition of Done
- All ACs in `docs/USER_STORIES_SPRINT8.md` verified by Trin.
- `make test` green; existing fingerprint IDs unchanged for existing paths.
- No Tank tasks: no deploy/CI scope.

## Backlog (unscheduled, from Sprint 8 retro)
- Run `sudo make demo-live` on a real TTY — never verified in-session; 3 lines of `examples/demo.py` changed this sprint.
- `GLOB` / `REGEX` modifiers (spec gap).
- Table/report view of a fingerprint set; reword "skipped aggregate values".
- Event-time timestamps via an optional profile path.
- Set-to-set merge.
- N-gram baseline / Jaccard scoring stage on top of fingerprint IDs.
- `examples/demo.py` bracket-markup sweep; scripted smoke test for its step actions.
- `tests/test_server.py` reaches into `Warehouse._records`.
- Docs: verify USER_GUIDE GitOps/sandbox sections; `agents/oracle/memory.md` placeholders.

