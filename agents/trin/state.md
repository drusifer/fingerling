# Agent State

## Context
## Recent Decisions
- Phase 1 UAT (STORY-FING-01): **FAILED** on literal AC coverage — sent back to Neo, not
  forwarded to Morpheus. Scope is additive (2 small gaps), not a rewrite.

## Key Findings
- AC1 says "Must accept a valid JSONL input string mimicking standard eBPF engine outputs."
  `tokenizer.py` has no function that parses JSONL text at all — `tokenize()` only accepts an
  already-parsed `dict`. Checked `docs/ARCH.md` §4.1: the architected signature is also
  `tokenize(record: dict, ...)` with no JSONL-string entry point, so this isn't a Neo oversight
  of the spec, it's a gap in the architecture-to-story traceability. Per Cypher's AC1, a
  literal JSONL-string ingestion path (even a 3-line `parse_jsonl(text) -> list[dict]`
  wrapper using `json.loads` per line) must exist and be tested, or the AC isn't met.
- AC4 says "absent **or null**" must degrade gracefully. All 17 current tests exercise the
  *absent* path (`_MISSING` sentinel) but none exercise an actual JSON `null` value flowing
  through `resolve_path` → modifier. The code (`value is _MISSING or value is None` checks)
  looks correct by inspection, but per the Artifact-Based Verification protocol I don't sign
  off on unverified code paths — needs an explicit test with a `null` field in the sample record.
- Everything else is solid: dot/bracket-index resolver correctly tested (nested + array index +
  out-of-range), full modifier registry (DEFAULT/IS_PRESENT/IS_NULL/IN_RANGE/ANY) individually
  tested, both of Cypher's Verification Tasks covered exactly, unknown-modifier error path
  tested, code is clean/DRY/typed with no smells.

## Important Notes
- Not filing this as a Smith `*user bug` — it's a correctness/coverage gap against AC, squarely
  Trin's domain, not a usability issue.
- 2026-10-12 Sprint 8 P1 UAT passed. Reusable check: scratchpad diff of git-HEAD tokenizer vs new over every MaskEntry literal in repo (90 comparisons, 0 diffs). AC5 'fails at profile load' depends on Phase 3 calling compile_path in load_profile — verify then.
- 2026-10-12 Sprint 8 P3 UAT passed (155 tests).
- 2026-10-12 Sprint 8 closed at 178 tests. Outstanding verification gap: interactive sudo make demo-live.
- 2026-10-12 Sprint 9 P0 UAT passed.
- 2026-10-13 Sprint 9 P1 UAT passed: isolated wheel install on 3.10, sdist tests 127/127 without fingerling, pre-split set merge 0 new/4 updated, README quickstart verbatim.

## Current Task
**Sprint:** 9 — SDLC tooling + fingerprint package split (`docs/USER_STORIES_SPRINT9.md`, board: `task.md`)
**Status:** Phase 1 passed

## Next Steps
Phase 2 UAT: make build output installs clean; workflows call only make targets; tag/version check logic; nothing pushed. Phase 3 UAT: run bob_protocol tests; archive with and without markers.

---
*Last updated: 2026-10-13T00:04:02-04:00*
