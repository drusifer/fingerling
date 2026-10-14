# Sprint 10 — Rubric Calibration

Each of the three rubrics applied to documents the project already has, to see whether it
separates stronger work from weaker and whether its criteria can be applied without guessing.
Levels: **W** weak, **A** acceptable, **S** strong. Rubrics are in the templates under
`agents/templates/`; the format is in `agents/templates/ARTIFACTS.md`.

## What this does and does not establish

- **It shows each rubric discriminates.** Every rubric found at least one Weak, and none found
  everything Weak.
- **It does not show reviewers would agree.** One assessor made every judgement, and that assessor
  is the same model that wrote several of the documents assessed (Sprints 8-10 stories, the SDLC,
  the Sprint 8-9 lessons). Scores for those are the least trustworthy here. Agreement between
  independent reviewers has not been tested.
- **Stories were chosen for spread**, not at random: an inherited POC document, two mid-project
  ones, and the two most recent.

---

## STORIES rubric

| Document | OUT | TEST | FAIL | SCOPE | SIZE | DESIGN | Verdict |
|---|---|---|---|---|---|---|---|
| Sprint 1 (POC, inherited from the source spec) | A | S | A | A | A | **W** | reject |
| Sprint 4 (sandbox / vaccination) | A | A | A | **W** | A | **W** | reject |
| Sprint 6 (TUI dashboard) | A | **W** | A | **W** | **W** | **W** | reject |
| Sprint 9 (package + tooling) | A | A | S | A | A | A | pass |
| Sprint 10 (this sprint) | A | A | A | A | A | A | pass |

Reasons for the levels that are not A:

- **Sprint 1 — TEST=S:** each story has "Verification Tasks" with concrete values
  (`pid: 14205` + `IS_PRESENT` → `"TRUE"`). **DESIGN=W:** criteria prescribe MD5, a FIFO queue
  and a `fingerprints.yaml` file — internals no user would observe. They came verbatim from the
  source specification, which is exactly the case the criterion's Strong level addresses (say
  *why* a constraint is required).
- **Sprint 4 — SCOPE=W:** no out-of-scope section. **DESIGN=W:** an acceptance criterion is a
  Python function signature (`run_in_sandbox(command: list[str], ...) -> subprocess.Popen`).
- **Sprint 6 — TEST=W:** the first criterion bundles six screen regions into one item, so
  partial delivery has no defined outcome. **SCOPE=W:** nothing is ruled out. **SIZE=W:** no
  points on either story. **DESIGN=W:** criteria name `rich.layout.Layout` and `rich.live.Live`.
- **Sprint 9 — FAIL=S:** failure criteria say what the user is told and what is left untouched
  (missing `uv` prints an instruction; a mismatched tag refuses to publish).

**What the pattern says.** DESIGN is the criterion that most separates early sprints from recent
ones: three of the first six sprint documents wrote design into acceptance criteria, leaving the
architecture step little to decide. That matches Morpheus's own Sprint 1 lesson about tracing
criteria to signatures — the stories had already fixed them.

### Criteria reworded as a result

| Criterion | Problem found | Change |
|---|---|---|
| `FAIL` | Sprint 10's stories produce documents and take no input; the criterion had no honest answer. | The question now says to report `n/a` for a story that takes no input and cannot be refused. |
| `SIZE` | Weak read "cannot be tested until another is finished", which would reject any ordered sprint (Sprint 9's CI story needs the package split first). | Weak is now "depends on another **without saying so**". |
| `DESIGN` | Sprint 4's function-signature criterion was not obviously covered; and Sprint 9 names `uv`, `ruff` and `gitleaks`, which the owner asked for. | Weak now lists "a function signature" and adds "and nobody asked for". |

---

## SDLC rubric

Only one SDLC document exists, so three committed versions of it were assessed from git history.

| Version | TRUE | WHOLE | CLEAN | CLASS | CHECK | GAPS | Verdict |
|---|---|---|---|---|---|---|---|
| Baseline commit `0b10273` — owner's decisions recorded, tooling not yet built | A | A | A | A | A | S | pass |
| Sprint 9 Phase 0 `cb0a86d` — uv, ruff and gitleaks in place | A | A | S | A | A | S | pass |
| Current (`main`, 2026-10-13) | **W** | A | S | A | A | S | reject |

- **Baseline — GAPS=S:** agreed-but-unbuilt tooling was listed in its own section with where
  each item would land.
- **Phase 0 — CLEAN=S:** prerequisites are listed with what each is for.
- **Current — TRUE=W:** section 8 says neither workflow has run "because nothing has been pushed
  since they were written". `main` was pushed on 2026-10-13, which starts the CI workflow, so the
  statement is no longer true. **This is a real defect found by the calibration**; it goes to
  Tank at this sprint's close check.

**A version that could not be assessed.** The first draft of the SDLC marked release handling and
branching as open questions. It was revised with the owner's answers before it was ever
committed, so it is not in git and is not scored here. From the session record it would have
been CLASS=W (a reader could not tell how to release, or even where to commit) — but that is a
recollection, not an assessment of a document anyone can open.

No SDLC criterion needed rewording.

---

## LESSON rubric

| Lesson | WHEN | WHAT | RULE | CAUSE | PLACE | Verdict |
|---|---|---|---|---|---|---|
| "Architecture review should trace every acceptance criterion to a literal function signature" (Sprint 1) | A | S | A | S | A | pass |
| "Fallback GPG signature checks simplify offline developer workflows" (Sprint 3) | **W** | A | A | A | A | reject |
| "Temporarily stopping/starting `Live` rendering contexts simplifies stdin read gates" (Sprint 6) | A | A | **W** | A | **W** | reject |
| "A shell pipe hides the exit status you care about" (Sprint 9) | A | S | S | A | A | pass |
| "Dependencies live in the project `.venv`" (`agents/oracle/lessons.md`) | A | A | S | A | A | pass |

- **Sprint 1 — CAUSE=S:** it records the wrong diagnosis that was tried first.
- **Sprint 3 — WHEN=W:** the title is an observation about GPG; nothing tells a future reader
  what situation should make them think of it.
- **Sprint 6 — RULE=W:** it has no "applying it" at all. **PLACE=W:** a later decision replaced
  the technique it recommends (a persistent `Live` context with raw key reads), and the lesson is
  not marked superseded.
- **Sprint 9 — RULE=S:** "capture output to a variable and test the command's own status" can be
  checked in a recipe afterwards.

No LESSON criterion needed rewording.

**A finding outside the rubric:** the lesson template's headings (Context / The Issue / The
Solution / The Rule) are used in `agents/oracle/lessons.md` but not in `docs/LESSONS.md`, which
uses Lesson / What happened / Applying it. The rubric's criteria apply to both shapes, so it was
left alone; aligning the two is a backlog item, not part of this sprint.

---

## Not done

- Existing documents found Weak were not rewritten — out of scope for this sprint. The one
  exception is the SDLC's stale sentence, which Tank corrects at close because the SDLC must stay
  true.
- No second reviewer applied any rubric, so inter-reviewer agreement is unknown.
- The architecture template has no rubric yet; it is the next candidate (see `ARTIFACTS.md`).
