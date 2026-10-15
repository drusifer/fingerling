# Task Board

**No sprint in flight.** Last sprint: 16 (below).

## Sprint 16: Run History

**Status:** Complete — launched 2026-10-14 (3/3 pts); merged to `main`; no release (mainline)
**Branch:** `sprint-16` (merged and deleted)
**Record:** `agents/chat_archive/CHAT_SPRINT_16.diagram.md`
**Source:** `docs/sprints/USER_STORIES_SPRINT16.md` (story + architecture D1-D5)
**Points:** 3 · **Tier:** 2

### Phase 1: The run as a set (STORY-FING-48, D1-D2) — Neo
- [x] **1.1** `FingerprintSet.run` header (saved, ignored on load); `_fold_stream` feeds a run set with shared timestamps. [Neo]
- [x] **1.2** UAT + review. [Trin, Morpheus]

### Phase 2: History files (STORY-FING-48, D3-D5) — Neo
- [x] **2.1** `<set>.history/<UTC>.yaml` with suffixes; summary line; `-o` skips; exit 3; help, README, USER_GUIDE. [Neo]
- [x] **2.2** UAT + review. [Trin, Morpheus]

### Close
- [x] Tank `*devops sdlc-check` · Oracle groom · Smith user test · retro + launch · chat report · merge (no release) [Tank, Oracle, Smith, All]

## Sprint 15: Shares of the Set

**Status:** Complete — launched 2026-10-14 (5/5 pts); merged to `main`; no release (mainline)
**Branch:** `sprint-15` (merged and deleted)
**Record:** `agents/chat_archive/CHAT_SPRINT_15.diagram.md`
**Source:** `docs/sprints/USER_STORIES_SPRINT15.md` (stories + architecture D1-D5)
**Points:** 5 · **Tier:** 2

### Phase 1: Shares in the set file (STORY-FING-46, 3 pts) — Neo
- [x] **1.1** `Fingerprint.share`; `Aggregate.value`; shares computed in `save`; README. [Neo]
- [x] **1.2** UAT + review. [Trin, Morpheus]

### Phase 2: Shares in `show` (STORY-FING-47, 2 pts) — Neo
- [x] **2.1** `COUNT %` and value/% columns; help and README. [Neo]
- [x] **2.2** UAT + review. [Trin, Morpheus]

### Close
- [x] Tank `*devops sdlc-check` · Oracle groom · Smith user test · retro + launch · chat report · merge (no release) [Tank, Oracle, Smith, All]

## Sprint 14: Weighted Aggregates

**Status:** Complete — launched 2026-10-14 (2/2 pts); merged to `main`; no release (mainline)
**Branch:** `sprint-14` (merged and deleted)
**Record:** `agents/chat_archive/CHAT_SPRINT_14.diagram.md`
**Source:** `docs/sprints/USER_STORIES_SPRINT14.md` (story + architecture D1-D4)
**Points:** 2 · **Tier:** 2

### Phase 1: `op: SIZE` (STORY-FING-45, 2 pts) — Neo
- [x] **1.1** `Op` family + `Size`; schema `op` and op/type exclusion with a readable message; `Aggregate.op`; docs and GH Archive example. [Neo]
- [x] **1.2** UAT + review. [Trin, Morpheus]

### Close
- [x] Tank `*devops sdlc-check` · Oracle groom · Smith user test · retro + launch · chat report · merge (no release) [Tank, Oracle, Smith, All]

## Sprint 13: Fingerprint UX

**Status:** Complete — launched 2026-10-14 (5/5 pts); merged to `main`; no release (mainline)
**Branch:** `sprint-13` (merged and deleted)
**Record:** `agents/chat_archive/CHAT_SPRINT_13.diagram.md`
**Source:** `docs/sprints/USER_STORIES_SPRINT13.md` (stories + architecture D1-D4)
**Points:** 5 · **Tier:** 2

### Phase 1: Small fixes (STORY-FING-43, -44, 2 pts) — Neo
- [x] **1.1** Absent path adds 0 to the skipped count; wording "unusable aggregate values"; README/USER_GUIDE. [Neo]
- [x] **1.2** `schema_errors` says which rules need arguments; UAT + review. [Neo, Trin, Morpheus]

### Phase 2: `fingerprint show` (STORY-FING-42, 3 pts) — Neo
- [x] **2.1** `show` subcommand, table, errors, help; docs. [Neo]
- [x] **2.2** UAT + review. [Trin, Morpheus]

### Close
- [x] Tank `*devops sdlc-check` · Oracle groom · Smith user test · retro + launch · chat report · merge (no release) [Tank, Oracle, Smith, All]

## Since Sprint 12 (each on its own `fix/` branch, merged to `main`, pushed)
- [x] `fix/disable-ci` — CI runs by hand only (owner).
- [x] `fix/fingerprint-metadata`, `fix/builtin-profile` — built-in metadata is `builtin.yaml` over the envelope `{meta: {seen}, record}`, written to a `meta` section; new `COUNT`, `FIRST(n)`.
- [x] `fix/flat-aggregate-state` — one-function aggregates store the value directly; `MIN`/`MAX` order text; `first_seen`/`last_seen` = `MIN`/`MAX`.
- [x] `fix/date-types` — `type: DATETIME`/`DATE` (ISO only, UTC) and `TRUNC`.
- [x] `fix/is-present-vs-is-null` — missing key and explicit null are told apart.
- [x] `fix/gharchive-example` — `examples/gharchive.yaml` + `make gharchive`.
- [x] `fix/formats-v0` — profile and set formats stay `version: 0` until 1.0.
- [x] `fix/clean-data` — `make clean` removes downloaded `data/`.
- [x] `fix/fix-skill-diagnose-first` — `*fix` diagnoses and confirms with the owner first (also in bob_protocol).

## Sprint 12: Domain Model and Consolidated Validation

**Status:** Complete — launched 2026-10-14 (13/13 pts); merged to `main`; no release (mainline)
**Branch:** `sprint-12` (merged and deleted)
**Record:** `agents/chat_archive/CHAT_SPRINT_12.diagram.md`
**Source:** `docs/sprints/USER_STORIES_SPRINT12.md` (stories + architecture D1-D7)
**Points:** 13 · **Tier:** 1

### Phase 0: Lint report (STORY-FING-38, 2 pts) — Tank
- [x] **0.1** `vulture`, `radon` dev deps; `make quality`; SDLC section 3. [Tank]
- [x] **0.2** Baseline findings posted; UAT + review. [Trin, Morpheus]

### Phase 1: Domain model (STORY-FING-39, 5 pts) — Neo
- [x] **1.1** `Rule` base; Modifier and Aggregator families; Field, Aggregate, Path in `model.py`/`aggregators.py`; schema `aggregator` definition; `check_profile` loop. [Neo]
- [x] **1.2** Tokenizer moved to `fingerling`; parked code on `Field`; docs and examples; UAT + review. [Neo, Trin, Morpheus]

### Phase 2: Smells and YAGNI (STORY-FING-40, 3 pts) — Neo
- [x] **2.1** Shims, aliases and dead API deleted; `Warehouse` → `FingerprintSet`; `_cmd_merge` and `load` split. [Neo]
- [x] **2.2** `make quality` clean (or findings justified); UAT + review. [Neo, Trin, Morpheus]

### Phase 3: Smoke suite (STORY-FING-41, 3 pts) — Trin, Tank
- [x] **3.1** `smoke/test_smoke.py`: installed command, examples, invalid profile, README blocks. [Trin]
- [x] **3.2** `make smoke` + SDLC gate; UAT + review. [Tank, Morpheus]

### Close
- [x] Tank `*devops sdlc-check` · Oracle groom · Smith user test · retro + launch · chat report · merge (no release) [Tank, Oracle, Smith, All]


## Sprint 11: Structured Modifiers and Profile Checking

**Status:** Complete — launched 2026-10-13 (8/8 pts); merged to `main`; released 0.2.0 (tag `v0.2.0` local, not pushed)
**Branch:** `sprint-11` (merged and deleted)
**Record:** `agents/chat_archive/CHAT_SPRINT_11.diagram.md`
**Source:** `docs/sprints/USER_STORIES_SPRINT11.md` (stories + architecture D1-D7)
**Points:** 8 · **Tier:** 2 (fast-track)

### Phase 0: Current Python (STORY-FING-35, 2 pts) — Tank
- [x] **0.1** Floor 3.14 in both manifests, `.python-version`, `PYTHONS`, CI matrix, ruff target; `jsonschema` added and installs on 3.14/3.15. [Tank]
- [x] **0.2** SDLC sections 1, 3, 8 + DECISIONS entry; UAT + review. [Tank, Trin, Morpheus]

### Phase 1: Modifier arguments as YAML (STORY-FING-36, 3 pts) — Neo
- [x] **1.1** `Modifier` object, mapping form, flags; string parser deleted; parked code and tests moved to the mapping form. [Neo]
- [x] **1.2** Example profiles and docs; UAT + review. [Neo, Trin, Morpheus]

### Phase 2: Profile checking (STORY-FING-37, 3 pts) — Neo
- [x] **2.1** `profile.schema.json`, `check_profile`, hand-written structure checks deleted. [Neo]
- [x] **2.2** `fingerprint check`; `merge` uses it; editor hint in README and examples; UAT + review. [Neo, Trin, Morpheus]

### Close
- [x] Tank `*devops sdlc-check` · Oracle groom · Smith user test · retro + launch · chat report · merge, release 0.2.0 [Tank, Oracle, Smith, All]


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
- One-time PyPI setup (`docs/SDLC.md` section 8) — only needed when releases resume.
- Mainline development (owner, 2026-10-14): no tags or releases until the owner says so. Local tags `v0.1.0`/`v0.2.0` left as they are, never pushed.
- Confirm that any Weak rubric criterion should block a gate (assumed in Sprint 10).

## Queued requests (next up)
- **bob_protocol (`~/Projects/bob_protocol`), for Tank:** a dependency analysis tool for validating the third-party packages a project uses: scanning, reputation score, vulnerability checks and similar. Queued 2026-10-13 by the owner during Sprint 11; not started.
- **bob_protocol, for Trin:** a test strategy document Trin owns, laying out the project's testing practices and conventions: the test pyramid applied to the tools available in the project's ecosystem. Queued 2026-10-13 by the owner during Sprint 11; not started.

## Backlog (unscheduled)
- **Top priority (Sprint 15 retro):** `fingerprint show --sort KEY` (any column, including `%` columns, e.g. `payload_bytes.SUM %`) and `--top N`.
- **History weight (Sprint 16):** built-in samples cut to 1 first + 1 last (owner, 2026-10-14, `fix/one-sample`): run files 6.2 MB -> 2.1 MB on a GH Archive hour, the rest mostly the two sample events. Still open: merge ~1.7x slower (~115-119 s vs ~68 s), likely the second fold deep-copying each event for LAST; option: fold once and derive the run.
- **`-o`:** owner may revisit (keep or drop); it writes no history.
- Fingerprint tool: JSON Schema for set files, generated from the profile (offered 2026-10-14).
- **Move fingerprint-sampler to its own project** (its own repository, out of the fingerling workspace). Owner, 2026-10-14; the owner wrote "fingerprint-scanner", read as fingerprint-sampler.
- Rubrics: confirm with the owner that any Weak should block a gate (assumed); have a second reviewer apply each rubric to test agreement; add a rubric to the architecture template; write runnable checks for `state.md`, chat messages and TLDR blocks; align `docs/LESSONS.md` entries with the lesson template; revisit the existing documents the calibration found Weak (Sprint 3 and 6 lessons).
- Fingerprint tool: more aggregate ops (`LEN`, `ABS`); event-time timestamps (would make show's FIRST/LAST SEEN informative); set-to-set merge.
- Process: decide how chat logging between sprints should work (it modifies `agents/CHAT.md`, which the SDLC says must not be committed straight to `main`); `--svg`/mermaid lint of chat reports need Node.
- For Tank: `make test-fingerprint ARGS=test_cli` fails with ModuleNotFoundError although SDLC section 3 documents it; SDLC sections 8 and 9 still say the first CI result is unknown (it passed).
- CI: run `make smoke` in the workflow (Sprint 12 retro).
- Tooling (via): the index misses most project functions (e.g. `load_profile`) even after `via index --force .`, still lists deleted files, `--via calls` returns the anchor instead of callers, and the MCP tool's `--canned` queries are rejected. Found 2026-10-13 in Sprint 11; work fell back to grep.
- Tooling (bob_protocol): `bobp prep-tldr` is broken (imports `via` as a library), so Oracle's TLDR sweep cannot run.
- Parked (not scheduled while the fingerprint tool is the focus): n-gram/Jaccard stage, `examples/demo.py` markup sweep and smoke test, `sudo make demo-live` verification, `tests/test_server.py` private access, USER_GUIDE GitOps/sandbox sections.
