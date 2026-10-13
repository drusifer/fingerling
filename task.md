# Task Board — Sprint 9: Fingerprint Package + SDLC Tooling

**Status:** In progress
**Branch:** `sprint-9`
**Source:** `docs/USER_STORIES_SPRINT9.md` (stories + architecture D1-D7)
**Process:** `docs/SDLC.md` (branch per sprint, Conventional Commits, Tank check at close)
**Points:** 18 · **Tier:** 1

---

## Phase 0: Build environment (STORY-FING-27, 5 pts) — Tank
- [x] **0.1** `uv` + `uv.lock`; `requires-python >=3.10`; dev group with ruff; Makefile targets per D5. [Tank]
- [x] **0.2** `ruff` config, repo-wide format (own commit), lint clean; `make secrets` + pre-commit hook; delete `Makefile.prj`, `requirements.txt`. [Tank]
- [x] **0.3** From-clean verify, 3.10-3.13 matrix, SDLC sections 1-5 updated; UAT + review. [Tank, Trin, Morpheus]

## Phase 1: Package split (STORY-FING-28, 5 pts) — Neo
- [x] **1.1** Create `packages/fingerprint-sampler` (workspace member); move modules + tests + access-log example; `fingerprint merge` command. [Neo]
- [x] **1.2** `fingerling` shims + alias; parked tests untouched and green; package README quickstart. [Neo]
- [x] **1.3** UAT (isolated install, pre-split set file merges) + review. [Trin, Morpheus]

## Phase 2: CI and publishing (STORY-FING-29, 4 pts) — Tank
- [ ] **2.1** `make build`; wheel installs and runs in a clean env. [Tank]
- [ ] **2.2** `ci.yml` and `publish.yml`; SDLC sections 7-8 + owner's one-time PyPI setup. [Tank]
- [ ] **2.3** UAT + review. [Trin, Morpheus]

## Phase 3: Per-phase chat report (STORY-FING-30, 4 pts) — Neo (in `~/Projects/bob_protocol`)
- [ ] **3.1** Phase markers → per-phase sections in `chat-report`; tests. [Neo]
- [ ] **3.2** Mouse/sprint instructions for markers; UAT + review. [Neo, Trin, Morpheus]

## Close
- [ ] Tank `*devops sdlc-check` [Tank]
- [ ] Oracle groom [Oracle]
- [ ] Smith end-to-end user test [Smith]
- [ ] Retro + launch (states SemVer bump) [All, Cypher]
- [ ] Merge `--no-ff` to `main`, release commit + tag, chat report [Tank, Oracle]

## Definition of Done
- All ACs in `docs/USER_STORIES_SPRINT9.md` verified by Trin.
- `make lint`, `make test`, `make secrets` green on the sprint branch.
- Nothing pushed, nothing published.

## Queued requests (next up after Sprint 9)
- **Artifact rubrics** (User, 2026-10-13): inventory the output artifacts each persona and skill is expected to produce; for templated artifacts, add a rubric appendix to the template for qualitative judgement of agent-produced content; recommend which skills to pilot first.

## Backlog (unscheduled)
- Fingerprint tool: `GLOB`/`REGEX` modifiers; table/report view of a set (`fingerprint show`); reword "skipped aggregate values"; event-time timestamps; set-to-set merge.
- Parked (not scheduled while the fingerprint tool is the focus): n-gram/Jaccard stage, `examples/demo.py` markup sweep and smoke test, `sudo make demo-live` verification, `tests/test_server.py` private access, USER_GUIDE GitOps/sandbox sections.
