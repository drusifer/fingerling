# Lessons Learned

## 2026-07-12 — POC Fingerling Sprint

**Lesson:** Architecture review should trace every acceptance criterion to a literal function
signature, not just a data-flow diagram.
**What happened:** `docs/ARCH.md`'s original §4.1 for STORY-FING-01 only specified
`tokenize(record: dict, ...)`. AC1 literally says "must accept a valid JSONL input string" —
a distinct, testable entry point that never got a signature in the architecture doc. It slipped
through Smith's Gate 2 review too (Smith checked HCI/UX concerns, not AC-to-signature
traceability — correctly outside Smith's remit). Trin caught it at Phase 1 UAT by checking the
AC text line-by-line against the actual code, not just running the existing test suite (which
passed 17/17 with the gap present).
**Applying it:** Trin's Artifact-Based Verification protocol ("never guess, check artifacts
first") is what caught this — worth reinforcing as the actual backstop for AC-to-code gaps,
since neither Smith's UX gate nor a green test suite alone will catch a missing entry point.
Morpheus should also do one AC-by-AC signature pass at code review, not just structural/smell
review, for stories with a literal "accepts X input format" clause.

**Lesson:** When an AC's wording is ambiguous about *when* an action happens (STORY-FING-02's
sample ring: "Drift State: ... insert into a ring buffer" vs. a Verification Task implying
ongoing rotation), check whether the literal reading makes the story's own Verification Task
testable at all. If it doesn't, the literal reading is probably wrong.
**Applying it:** This resolved the Warehouse sample-ring-growth ambiguity (see
`docs/DECISIONS.md`) without needing another round-trip through Cypher/Smith — Trin adjudicated
it directly against the story's own text, Morpheus endorsed at review. Good pattern for future
POCs with inherited/pre-written ACs where the original author isn't in the loop to clarify.
