# Neo Context

## Recent Decisions
- Package layout: `fingerling/{tokenizer,warehouse,ringbuffer,policy}.py` + `tests/test_*.py`,
  per `docs/ARCH.md` §6. Only `make test` target exists in this repo (no `test-q`/`lint`/`install`
  yet despite SKILL.md mentioning them) — using `make test` for all phases; not adding the
  extra targets since nothing in this POC needs lint/coverage tooling yet (YAGNI).

## Key Findings
- Phase 1 (tokenizer): hand-rolled dot/bracket-index path resolver via regex, sentinel
  `_MISSING` object distinguishes "absent" from `None`. Modifier registry is a plain dict of
  callables keyed by name parsed from `NAME(args)` strings.

## Important Notes
- `apply_modifier` raises `ValueError` on unknown modifier names immediately (no separate
  profile-load validation step added — no persistent "engine" object exists to validate at
  load time for a stateless functional module, so validating at first use is equivalent).

---
*Last updated: 2026-07-12T00:03*
