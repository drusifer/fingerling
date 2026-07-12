# Current Task

**Status:** Complete
**Assigned to:** Neo
**Started:** 2026-07-12

## Task Description
`/neo fix up the Makefiles (see make skill)` — post-sprint task. `make demo` (added by Oracle
for the user guide) and `make tldr` (pre-existing bob-protocol target) both failed with "No
rule to make target" on plain invocation.

## Progress
- [x] Loaded the `make` and `make-discover` skills to get the authoritative two-file pattern
      before touching anything (real recipe in `Makefile.prj` + public stub in `Makefile`'s
      `else` block)
- [x] Confirmed root cause via direct reproduction: `make tldr` and `make demo` both failed
      with "No rule to make target" — neither had a stub in the `else` block's `.PHONY`/target
      list, only `Makefile.prj` (for `demo`) or the `ifdef MKF_ACTIVE` block (for `tldr`)
- [x] Added `tldr` and `demo` to the `else` block `.PHONY` line in `Makefile`
- [x] Added stub recipes for both (`@./agents/tools/mkf.py $(V) $@`), matching the exact
      pattern used by `test`/`via_index`
- [x] Verified: `make demo`, `make tldr V=-v`, `make help` (target appears twice, per the
      skill's own verification instructions), `make test` (50/50, no regressions)
- [x] Corrected `docs/USER_GUIDE.md` (removed stale "make demo doesn't work" FAQ entry, restored
      `make demo` as the preferred command) and `docs/LESSONS.md` (corrected my predecessor's
      wrong root-cause diagnosis — it wasn't `_IS_BOB_ENTRY`/`Makefile.bob`, it was a missing
      stub, straight out of the `make` skill's documented pattern)

## Blockers
None

## Oracle Consultations
None needed — root cause and fix pattern were both fully specified in the `make`/`make-discover`
skills; no ambiguity requiring Oracle's historical-decision context.

---
*Last updated: 2026-07-12T00:35*
