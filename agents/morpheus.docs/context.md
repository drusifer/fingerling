# Morpheus Context

## Recent Decisions
See `docs/ARCH.md` §7 Decisions Log for the full record. Summary:
1. Hand-rolled dot/bracket-index path resolver — no `jsonpath-ng` dependency for POC.
2. `SlidingWindowMatcher.warm` property added alongside spec's `push()` 0.0/1.0 contract —
   resolves Smith's Gate-1 HCI note without breaking the external contract.
3. `policy.compile_policy(..., action: Literal["Block","Post"] = "Block")` — explicit param,
   resolves Smith's Gate-1 note on STORY-FING-04 AC3 ambiguity.
4. Warehouse sample ring (cap 3) is a plain list, not `deque` — serializes cleanly to YAML.
5. Package layout: `fingerling/{tokenizer,warehouse,ringbuffer,policy}.py` + `tests/test_*.py`
   at repo root, matching existing `make test` (`unittest discover -s tests`).

## Key Findings
- `PyYAML` already available in the dev environment; only third-party dep needed. No
  `requirements.txt` exists yet — Neo must create one in Phase 1.
- No `tests/` directory exists yet.

## Important Notes
- Both of Smith's Gate-1 notes were resolved architecturally (not punted to Neo to improvise) —
  Gate 2 review should confirm these resolutions are acceptable before Mouse plans phases.

---
*Last updated: 2026-07-12T00:00*
