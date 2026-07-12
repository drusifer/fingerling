# Current Task

**Status:** Complete
**Assigned to:** Oracle
**Started:** 2026-07-12

## Task Description
User guide + documented end-to-end demo for POC Fingerling (`/oracle` command, post-sprint-close).

## Progress
- [x] Read all 4 module source files (`fingerling/tokenizer.py`, `warehouse.py`, `ringbuffer.py`,
      `policy.py`) and `tests/test_e2e.py` to ground every API claim in real code
- [x] Wrote `examples/demo.py` — runnable script: baseline training → live scoring → policy
      compilation, using the manual whitelist-building glue code a real caller needs today
- [x] Ran the demo for real, captured actual stdout (not fabricated) for the guide
- [x] Wrote `docs/USER_GUIDE.md`: install, pipeline diagram, module-by-module API reference,
      end-to-end demo walkthrough with real captured output, known-gaps section, FAQ
- [x] Verified every code snippet in the guide by executing it directly — see transcript below
- [x] Added `Makefile.prj` with a `demo` target (surfaces in `make help`)
- [x] Found `make demo` doesn't work via plain invocation (Makefile catch-all quirk) — did not
      silently paper over it; documented the working command (`python3 -m examples.demo`) and
      logged the gap in `docs/LESSONS.md` for Tank
- [x] Updated `README.md` — added USER_GUIDE.md as the top doc link + a "Try It" section
- [x] `make test` — 50/50 passing throughout, no regressions from any of the above

## Verification transcript (all guide snippets executed successfully)
```
tokenizer OK: {'hook_syscall': 'sys_connect', 'dest_port': 'TRUE'}
warehouse OK: 1 1
save/load OK
ringbuffer OK: 0.0 0.0 1.0 True
policy OK, len: 301
empty match_labels ValueError OK: match_labels must not be empty...
unknown modifier ValueError OK: Unknown modifier: 'NOT_A_REAL_MODIFIER'
```

## Blockers
None

## Oracle Consultations
N/A

---
*Last updated: 2026-07-12T00:30*
