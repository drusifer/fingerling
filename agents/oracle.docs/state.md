# Agent State

## Context
## Recent Decisions
- Moved root `Finglering Initial Docs.md` into `docs/SOURCE_SPEC.md` — no orphan docs in root
  per grooming standard. Updated the one prose reference in `docs/USER_STORIES.md`.
- Created `docs/DECISIONS.md` and `docs/LESSONS.md` (didn't exist before this sprint) — placed
  under `docs/` alongside ARCH.md/USER_STORIES.md rather than repo root, for consistency.

## Key Findings
- `agents/CHAT.md` is well under the 50-100 message archive threshold — no archive needed
  this sprint.
- No other orphan/misplaced markdown found at repo root — README.md, AGENTS.md (symlink),
  LICENSE are all expected there.

## Important Notes
- `docs/DECISIONS.md` and `docs/LESSONS.md` should be appended to (not replaced) in future
  sprints — chronological log format, most recent entry last.

## 2026-07-12 (post-launch): User Guide + Demo
- User requested (via `/oracle`, not part of the original sprint): a user guide and a
  documented end-to-end demo. Post-sprint-close task, done outside the Bloop cycle.
- Built `examples/demo.py` as a real, runnable script (not a hand-written transcript) and
  captured its actual stdout for `docs/USER_GUIDE.md`'s walkthrough — every code snippet in the
  guide was executed and verified against the real API before being written down (see
  `agents/oracle.docs/current_task.md` for the verification transcript).
- Found + flagged (not fixed) a real Makefile gap: `Makefile.prj` targets like `demo` don't
  route through this repo's target-interception layer via plain `make demo` — only
  `make MKF_ACTIVE=1 demo` works, because `_IS_BOB_ENTRY` checks for a literal `Makefile.bob`
  filename this repo doesn't use. Documented the working command instead of the broken one;
  logged the gap in `docs/LESSONS.md` for Tank.

## Current Task
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

## Next Steps
## Immediate Next Action
None — user guide + demo delivered. Nothing pending.

## Waiting On
Nothing.

## Planned Work
- [ ] Next sprint: if the baseline-whitelist helper or a real `tokenize`-accepting-a-tuple
      fix for `compile_policy` gets built, update `docs/USER_GUIDE.md`'s "Known Gaps" section
      to remove the now-resolved item.
- [ ] If Tank fixes the Makefile `_IS_BOB_ENTRY` routing gap, update the guide's FAQ entry and
      README to recommend `make demo` again.

---
*Last updated: 2026-08-07T13:17:52-04:00*
