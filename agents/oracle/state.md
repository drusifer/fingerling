# Agent State

## Context
## Recent Decisions
- Moved root `Finglering Initial Docs.md` into `docs/SOURCE_SPEC.md` — no orphan docs in root
  per grooming standard. Updated the one prose reference in `docs/sprints/USER_STORIES_SPRINT1.md`.
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
  `agents/oracle/current_task.md` for the verification transcript).
- Found + flagged (not fixed) a real Makefile gap: `Makefile.prj` targets like `demo` don't
  route through this repo's target-interception layer via plain `make demo` — only
  `make MKF_ACTIVE=1 demo` works, because `_IS_BOB_ENTRY` checks for a literal `Makefile.bob`
  filename this repo doesn't use. Documented the working command instead of the broken one;
  logged the gap in `docs/LESSONS.md` for Tank.
- 2026-10-12 Sprint 8 groom done: ARCH.md, DECISIONS.md, LESSONS.md, USER_GUIDE.md, README.md, agents/oracle/lessons.md (venv rule). Docs backlog remaining: USER_GUIDE GitOps/sandbox sections unverified against code; DOCUMENTATION_INDEX.md not reviewed; agents/oracle/memory.md still has template placeholders.
- 2026-10-12 Sprint 8 chat archived: agents/chat_archive/CHAT_SPRINT_8.md (includes Sprints 1-7 history). CHAT.md reset.
- 2026-10-13 Sprint 9 groomed and archived to agents/chat_archive/CHAT_SPRINT_9*.md in per-phase format.

- 2026-10-13 SUPERSEDED: the `Makefile.prj` / `_IS_BOB_ENTRY` / `MKF_ACTIVE` gap noted above no
  longer exists — the project has a single Makefile (docs/SDLC.md section 3).
- 2026-10-13 2026-10-13 docs groom (branch fix/docs-groom): sprint stories moved to docs/sprints/USER_STORIES_SPRINT<N>.md (POC file renamed SPRINT1) with live references updated; removed tracked strays build-err.out and agents/CHAT.md.bak; README has a full documentation map; agents/DOCUMENTATION_INDEX.md rewritten for the current layout; memory.md filled in; USER_GUIDE uses fingerprint_sampler imports and labels parked sections; lessons files cross-linked; file:// and dead links fixed (0 broken). Not touched: persona Summary files (71), agents/tools stale copies, docs/SDLC.md (Tank's).

## Current Task
**Task:** docs groom (branch fix/docs-groom)
**Status:** Docs groom complete

## Next Steps
Open for the owner: USER_GUIDE GitOps and sandbox sections are labelled unverified, not re-checked; agents/PROJECT.md still says 'Project: bob_protocol' (generated file); cypher/SKILL.md names docs/USER_STORIES.md generically while this project uses docs/sprints/.

---
*Last updated: 2026-10-13T10:08:50-04:00*
