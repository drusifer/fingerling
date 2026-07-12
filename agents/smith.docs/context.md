# Smith Context

## Recent Decisions
- Gate 1 (POC Fingerling stories, docs/USER_STORIES.md): **Approved with notes**. Not a
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

---
*Last updated: 2026-07-12T00:01*
