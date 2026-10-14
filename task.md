# Task Board

**No sprint in flight.** Last sprint: 10 (below). Next up: see *Owner actions* and *Queued requests*.

## Sprint 10: Artifact Rubrics

**Status:** Complete — launched 2026-10-13 (10/10 pts); merged to `main`; no release (published package unchanged); not pushed
**Branch:** `sprint-10` (merged and deleted)
**Record:** `agents/chat_archive/CHAT_SPRINT_10.diagram.md` (planning and phases 1-4) and `CHAT_SPRINT_10_CLOSE.diagram.md` (Phase 4 handoffs, close, retro and launch, posted late — see the lesson of 2026-10-13) · calibration: `docs/sprints/SPRINT10_RUBRIC_CALIBRATION.md`
**Source:** `docs/sprints/USER_STORIES_SPRINT10.md` (stories + architecture D1-D7)
**Points:** 10 · **Tier:** 1 · Implementer: Bob (templates and skills)

### Phase 1: Inventory and rubric format (STORY-FING-31, 2 pts)
- [x] **1.1** `agents/templates/ARTIFACTS.md`: inventory, rubric format, verdict line, how to add; link from the agents index. [Bob]
- [x] **1.2** UAT + review. [Trin, Morpheus]

### Phase 2: Stories template and rubric (STORY-FING-32, 3 pts)
- [x] **2.1** `_template_USER_STORIES.md` with rubric appendix. [Bob]
- [x] **2.2** Wire into Cypher, Smith Gate 1 and the sprint skill. [Bob]
- [x] **2.3** UAT + review. [Trin, Morpheus]

### Phase 3: SDLC and lesson rubrics (STORY-FING-33, 2 pts)
- [x] **3.1** SDLC rubric on the three SDLC templates; lessons rubric on the lesson template. [Bob]
- [x] **3.2** Wire into build-env, Tank, Oracle groom and Smith's close test. [Bob]
- [x] **3.3** UAT + review. [Trin, Morpheus]

### Phase 4: Calibration (STORY-FING-34, 3 pts)
- [x] **4.1** Apply each rubric to 3+ existing artifacts; reword criteria that do not apply cleanly. [Bob]
- [x] **4.2** `docs/sprints/SPRINT10_RUBRIC_CALIBRATION.md`; UAT + review. [Bob, Trin, Morpheus]

### Close
- [x] Tank `*devops sdlc-check` · Oracle groom · Smith user test · retro + launch · merge (no release) [Tank, Oracle, Smith, All]

## Sprint 9: Fingerprint Package + SDLC Tooling

**Status:** Sprint 9 complete — launched 2026-10-13 (18/18 pts); merged to `main`, tagged `v0.1.0`, not pushed
**Branch:** `sprint-9` (merged and deleted)
**Record:** `agents/chat_archive/CHAT_SPRINT_9.diagram.md`
**Source:** `docs/sprints/USER_STORIES_SPRINT9.md` (stories + architecture D1-D7)
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
- [x] **2.1** `make build`; wheel installs and runs in a clean env. [Tank]
- [x] **2.2** `ci.yml` and `publish.yml`; SDLC sections 7-8 + owner's one-time PyPI setup. [Tank]
- [x] **2.3** UAT + review. [Trin, Morpheus]

## Phase 3: Per-phase chat report (STORY-FING-30, 4 pts) — Neo (in `~/Projects/bob_protocol`)
- [x] **3.1** Phase markers → per-phase sections in `chat-report`; tests. [Neo]
- [x] **3.2** Mouse/sprint instructions for markers; UAT + review. [Neo, Trin, Morpheus]

## Close
- [x] Tank `*devops sdlc-check` [Tank]
- [x] Oracle groom [Oracle]
- [x] Smith end-to-end user test [Smith]
- [x] Retro + launch (states SemVer bump) [All, Cypher]
- [x] Merge `--no-ff` to `main`, release commit + tag, chat report [Tank, Oracle]

## Definition of Done
- All ACs in `docs/sprints/USER_STORIES_SPRINT9.md` verified by Trin.
- `make lint`, `make test`, `make secrets` green on the sprint branch.
- Nothing pushed, nothing published.

## Since Sprint 10 (maintenance, each on its own `fix/` branch, merged to `main`)
- [x] `fix/glob-regex-regsub` — `GLOB`, `REGEX` and `REGSUB` modifiers with quoted arguments (spec FR-MOD-01); Trin UAT, Morpheus review, Smith user test. CI for the 2026-10-13 pushes checked: green.
- [x] `fix/sprint-10-record` — Sprint 10's missing close record restored; SDLC requires checking the record before a merge.
- [x] `fix/remove-legacy-templates` — three retired state templates removed; stories template uses `STORY-{KEY}-{id}`.
- [x] `fix/sync-agents-md` — `agents/AGENTS.md` synced with upstream (SDLC guideline, single `state.md`, `bobp make`).
- [x] `fix/shutdown-prep` — board and state files for hand-off.

BobProtocol sync (2026-10-13): the tool changes, the `build-env` skill, SDLC and rubric templates,
skill and persona edits and the SDLC guideline are all committed and pushed in
`~/Projects/bob_protocol`, including its shipped templates. `agents/skills`, `agents/templates`
and `agents/AGENTS.md` here match it.

## Since Sprint 9 (maintenance, each on its own `fix/` branch, merged to `main`)
- [x] `fix/single-makefile` — one Makefile; `chat` and `tldr` targets removed in favour of `bobp chat` / `bobp tldr`.
- [x] `fix/docs-groom` — sprint stories moved to `docs/sprints/`; README documentation map; agents index and Oracle memory rewritten; dead links fixed.
- [x] `fix/remove-legacy-tools` — nine stale `agents/tools/*.py` copies of bobp tools removed.
- [x] `fix/session-close` — this board, state files and the post-sprint chat archive.

Record: `agents/chat_archive/CHAT_POST_SPRINT_9.md`. No release: the published package did not change.

## Owner actions (agents do not push or publish unless told)
- One-time PyPI setup: pending trusted publisher + GitHub `pypi` environment (`docs/SDLC.md` section 8).
- Then `git push origin v0.1.0` — publishes fingerprint-sampler 0.1.0. The tag exists locally only.
- Decide the release for the GLOB/REGEX/REGSUB feature: bump to 0.2.0 (SDLC section 7), or move the unpublished `v0.1.0` tag to include it. Not bumped or tagged.
- Confirm that any Weak rubric criterion should block a gate (assumed in Sprint 10).

## Queued requests (next up)
- None. (Artifact rubrics delivered in Sprint 10.)

## Backlog (unscheduled)
- Rubrics: confirm with the owner that any Weak should block a gate (assumed); have a second reviewer apply each rubric to test agreement; add a rubric to the architecture template; write runnable checks for `state.md`, chat messages and TLDR blocks; align `docs/LESSONS.md` entries with the lesson template; revisit the existing documents the calibration found Weak (Sprint 3 and 6 lessons).
- Fingerprint tool: `fingerprint show` (table/report view of a set); reword "skipped aggregate values"; event-time timestamps; set-to-set merge; rename `Warehouse` before 1.0.
- Process: decide how chat logging between sprints should work (it modifies `agents/CHAT.md`, which the SDLC says must not be committed straight to `main`); `--svg`/mermaid lint of chat reports need Node.
- For Tank: `make test-fingerprint ARGS=test_cli` fails with ModuleNotFoundError although SDLC section 3 documents it; SDLC sections 8 and 9 still say the first CI result is unknown (it passed).
- Tooling (bob_protocol): `bobp prep-tldr` is broken (imports `via` as a library), so Oracle's TLDR sweep cannot run.
- Parked (not scheduled while the fingerprint tool is the focus): n-gram/Jaccard stage, `examples/demo.py` markup sweep and smoke test, `sudo make demo-live` verification, `tests/test_server.py` private access, USER_GUIDE GitOps/sandbox sections.
