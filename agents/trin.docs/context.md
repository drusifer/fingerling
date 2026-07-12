# Trin Context

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

---
*Last updated: 2026-07-12T00:04*
