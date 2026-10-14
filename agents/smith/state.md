# Agent State

## Context
## Recent Decisions
- Sprint 7 end-to-end user test: **PASSED**. All 7 ACs verified live. Surfaced (not filed as
  blocking) a pre-existing bug: `examples/demo.py`'s narrative text uses `[bold red]...[/bold
  red]`-style bracket tags that `rich.text.Text.append()` does NOT parse — they render as
  literal bracket characters in the real TUI. Visible directly in Step 7 next to my new,
  correctly-rendered text. Already logged by Oracle as a lesson; filed to Cypher's backlog for a
  future full-file sweep, out of STORY-FING-22's 3pt scope.
- Sprint 7 fast-track gate (docs/sprints/USER_STORIES_SPRINT7.md, STORY-FING-22): **Approved with one
  non-blocking note**. Block-over-sanitize UX call endorsed (visible rejection > silent rewrite
  for a teaching demo). Note to Neo: keep the "narrow policy misses novel `;` payload" moment
  visible in whatever step sequencing is chosen — it's the pedagogical payoff of the story, not
  incidental detail.
- Gate 1 (POC Fingerling stories, docs/sprints/USER_STORIES_SPRINT1.md): **Approved with notes**. Not a
  blocking rejection — notes are forward to Morpheus/Neo for design-time consideration, not
  story rewrites, since the ambiguity originates in the user's own source BRD/PRD.

## Key Findings
- STORY-FING-03 (ring buffer): the AC (inherited verbatim from source BRD) has the warm-up
  phase return the *same* `0.0` value as a genuine "not anomalous" match. This conflates
  "insufficient data" with "verified safe" — Heuristic #1 (Visibility of System Status). A
  downstream consumer (e.g. the enforcement gate) can't distinguish "haven't seen enough yet"
  from "confirmed clean." Recommend Morpheus/Neo expose warm-up state distinctly in the
  return type (e.g. `None`/enum) even if the public score API still surfaces `0.0` for
  external callers, OR log/flag warm-up windows so gate decisions aren't silently made on
  partial data.
- STORY-FING-04: "defaults its action to Block or Post based on the target specification" is
  underspecified — what field of the target spec selects Block vs Post? Not blocking, but
  Morpheus should pin this down in architecture so Neo isn't guessing.
- Modifier DSL naming (`IS_PRESENT`, `IN_RANGE(low, high)`, `ANY(v1,v2,...)`) is consistent
  UPPER_SNAKE + paren-args style — good mental-model fit, matches how a security engineer
  would read a rule DSL. No consistency concerns.

## Important Notes
- This is a pre-implementation review (spec/AC quality only) — no running software to test yet.
  Runtime `*user test` happens at Stage 3 sprint close once phases are built.

## Gate 2 — Architecture Review (docs/ARCH.md)
- **Approved.** Both Gate-1 notes confirmed resolved:
  - `SlidingWindowMatcher.warm` property gives callers a distinct signal without changing the
    spec-mandated `push()` 0.0/1.0 contract. Good fix — keeps the tested public contract intact
    while restoring Heuristic #1 visibility for anyone who reads the state, not just the score.
  - `compile_policy(..., action: Literal["Block","Post"] = "Block")` is explicit, no implicit
    inference — Heuristic #5 Error Prevention win over the vague original AC.
- Minor non-blocking note for Neo: `Warehouse.upsert()` returns only the `fingerprint_id` string
  — a caller can't tell match vs. drift without a second lookup. Not required by any AC; flag if
  Trin's tests end up wanting that visibility, otherwise leave as designed.
- API naming is consistent snake_case throughout all 4 modules — no cross-module inconsistency.
- 2026-10-12 Sprint 8 Gate 1 approved; added FING-26 AC10-13 (TTY stdin guard, --help example, readable set file, actionable mismatch error).
- 2026-10-12 Sprint 8 Gate 2 approved. Required note for Neo: missing jsonpath dependency must produce a 'run make install' message, not a traceback.
- 2026-10-12 Sprint 8 user test passed; 1 cosmetic bug filed and fixed (usage prog). Backlog: 'skipped aggregate values' wording, table view of a set.
- 2026-10-12 Sprint 9 Gates 1+2 approved; added FING-28 AC9 (self-contained README quickstart), AC10 (no silent failure for moved commands).
- 2026-10-13 Sprint 9 user test passed (wheel in clean 3.11 env, README verbatim).
- 2026-10-13 Sprint 10 Gates 1+2 approved; added FING-31 AC6 (verdict fits one chat message).
- 2026-10-13 Sprint 10 closed. From now on: Gate 1 uses the STORIES rubric (verdict line, any Weak rejects); close test reviews new lessons with the LESSON rubric.

- 2026-10-13 User-tested GLOB/REGEX/REGSUB: approved. Residual risk: double-quoted YAML halves backslashes silently; documented in the package README only.

- 2026-10-13 Sprint 11 Gate 1 and user test approved. Backlog: bare `modifier: GLOB` error does not say a mapping is needed.

## Current Task
**Sprint:** 10 — Artifact rubrics (`docs/sprints/USER_STORIES_SPRINT10.md`, board: `task.md`)
**Status:** Sprint 10 complete

## Next Steps
No pending gates.

---
*Last updated: 2026-10-13T23:55:00-04:00*
