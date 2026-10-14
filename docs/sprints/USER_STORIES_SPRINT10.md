# Sprint 10 User Stories: Artifact Rubrics

*   **Total Points**: 10 (Tier 1 — run as a full sprint at the owner's request)
*   **Branch**: `sprint-10`
*   **Source**: Owner request queued 2026-10-13 ("artifact rubrics")
*   **Status**: Gates 1 and 2 approved (Smith, 2026-10-13); FING-31 AC6 added at Gate 1

## Goal

Give the team a way to judge whether a document an agent produced is *good*, not merely present.
For each templated artifact, a rubric travels with the template and is applied at a review step
that already exists.

This sprint changes agent templates, skills and persona instructions only. It does not touch the
fingerprint tool or the parked pipeline, so it makes no release.

## Assumptions made for the owner (not confirmed)

1. **Pilot = three artifacts:** sprint stories, `docs/SDLC.md`, and lessons — the three
   recommended on 2026-10-13. The owner asked for the sprint without choosing among them.
2. **A rubric can block a gate.** Any criterion judged *Weak* by the independent reviewer is a
   rejection that names the criterion and the fix. Everything at *Acceptable* or better passes.
3. **Judgement, not scoring.** Rubrics guide a reviewer; nothing computes a number.

---

## STORY-FING-31: Artifact Inventory and Rubric Format
**Points:** 2

**As** the project owner,
**I want** one place that lists every artifact the agents are expected to produce and says how a
rubric is written and used,
**so that** I can see what is covered and extend it without reverse-engineering the skills.

### Acceptance Criteria
1. One document lists every expected artifact with its owner, where it lives, its template (or
   "none"), its rubric (or "none"), and who reviews it at which step.
2. The same document defines the rubric format: what a criterion is, the three levels, how a
   verdict is reached and how it is reported.
3. It says which artifacts are deliberately *not* given rubrics and why.
4. It explains how to add a rubric to another template.
5. It is linked from the agents documentation index.
6. *(Smith Gate 1)* A verdict can be reported inside one chat message (512 characters): the
   format has a compact one-line form, with fuller reasoning required only for a rejection.

---

## STORY-FING-32: Sprint Stories Template with Rubric
**Points:** 3

**As** Cypher writing stories, and Smith reviewing them,
**I want** a stories template with a rubric appended,
**so that** Gate 1 is judged against written criteria instead of taste.

### Acceptance Criteria
1. A stories template exists with the sections our sprint documents actually use.
2. Its appendix is a rubric in the standard format, with criteria specific to stories.
3. Cypher's instructions say to start from the template and self-check against the rubric before
   handing off.
4. Smith's Gate 1 and the sprint skill say to apply the rubric, cite each criterion's level in
   the verdict, and reject on any *Weak*.
5. The rubric is kept out of the finished stories document.

---

## STORY-FING-33: Rubrics for the SDLC and Lesson Templates
**Points:** 2

**As** Tank and Oracle,
**I want** rubrics on the SDLC and lesson templates,
**so that** those documents are reviewed for usefulness, not just existence.

### Acceptance Criteria
1. Each SDLC template carries the same SDLC rubric in an appendix.
2. The lesson template carries a lessons rubric in an appendix.
3. Each rubric names an independent reviewer and the existing step where it is applied, and the
   relevant skill or persona instructions say so.
4. The SDLC rubric judges the document; it does not duplicate Tank's conformance check, which
   judges whether the project matches the document.
5. Rubrics stay out of the finished documents.

---

## STORY-FING-34: Calibrate the Rubrics on Real Artifacts
**Points:** 3

**As** the project owner,
**I want** each rubric tried on documents we already have,
**so that** I know it separates strong work from weak work before the team relies on it.

### Acceptance Criteria
1. Each rubric is applied to at least three existing artifacts of differing quality, with a
   level and a one-line reason per criterion.
2. At least one existing artifact is judged *Weak* on at least one criterion per rubric — a
   rubric that passes everything is not discriminating — or the report says plainly that none was.
3. Any criterion that could not be applied consistently is reworded, and the change is noted.
4. The results are written up in one report, including what the calibration could not establish.
5. Sprint 10's own stories are among the artifacts assessed.

---

## Out of Scope
- Rubrics for untemplated artifacts (decisions, task board, work summaries, gate verdicts).
- Rubrics for chat messages and `state.md` — their failures are mechanical; a lint check fits better.
- Automated scoring or enforcement in tooling.
- Rewriting existing artifacts that the calibration finds weak.
- Upstreaming to the BobProtocol source — the owner syncs that separately.

---

## Technical Architecture Design (Morpheus)

No code, dependency or build change: nothing for a Tank Phase 0.

### D1. Files
| File | Purpose |
|---|---|
| `agents/templates/ARTIFACTS.md` (new) | Artifact inventory + the rubric format + how to add one |
| `agents/templates/_template_USER_STORIES.md` (new) | Sprint stories template with rubric appendix |
| `agents/templates/_template_SDLC.md`, `.python.md`, `.javascript.md` | Gain the same SDLC rubric appendix |
| `agents/templates/_template_LESSON.md` | Gains a lessons rubric appendix |
| `docs/sprints/SPRINT10_RUBRIC_CALIBRATION.md` (new) | Calibration report |

### D2. Rubric format
An appendix at the end of the template, between `<!-- RUBRIC-START -->` and `<!-- RUBRIC-END -->`:
one table, 4-6 criteria, each with a short **code**, the question it asks, and what *Weak*,
*Acceptable* and *Strong* look like in observable terms. Codes exist so a verdict fits a chat
message: `rubric STORIES: OUT=S TEST=A SCOPE=A FAIL=W SIZE=A DESIGN=A`.

**Verdict rule:** every criterion *Acceptable* or better → pass. Any *Weak* → reject, naming the
criterion and the fix. *Strong* is recognition, never a requirement.

### D3. Keeping rubrics out of finished artifacts
The template's opening instructions say to delete everything between the markers when
instantiating. Oracle's groom checks that no document outside `agents/templates/` has a line
beginning with the start marker (prose that merely mentions it is fine).

### D4. Who applies each rubric, and when
| Artifact | Author self-check | Independent reviewer | Step |
|---|---|---|---|
| Sprint stories | Cypher, before handoff | Smith | Gate 1 |
| `docs/SDLC.md` | Tank, on create/update | Oracle | Groom (Step 7), in sprints where the SDLC changed |
| Lessons | Oracle, on record | Smith | End-to-end test (Step 8), for lessons added that sprint |

The reviewer is never the author. The SDLC rubric judges the *document*; Tank's
`*devops sdlc-check` continues to judge whether the *project* matches it.

### D5. One SDLC rubric, three templates
The three SDLC templates carry byte-identical rubric appendices; Trin verifies they match.

### D6. Roles this sprint
Templates and skills are Bob's files, so **Bob implements** each phase in place of Neo. Trin
verifies, Morpheus reviews.

### D7. Calibration
Each rubric is applied to existing artifacts chosen for spread (an early sprint, a middle one, a
recent one). The assessor is the same model that wrote several of them, which the report must
state as a limit.
