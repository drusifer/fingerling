# Agent State

## Context
## Recent Decisions
- Sprint 7 (fast-track, 1 phase, STORY-FING-22, 3 pts) planned 2026-08-08 and launched same day.
  Board for Sprint 7 was `docs/sprints/USER_STORIES_SPRINT7.md`, not `task.md` (1-phase sprint).
- No Tank tasks in any sprint so far — no deploy/infra/CI scope.

## Key Findings (as of 2026-10-12 status check)
- No active sprint. Sprints 1-7 all closed; last commit b91470b (2026-08-08) shipped Sprint 7.
- Tests at last verified run: 88/88 (Cypher's correction, 2026-08-08). Not re-run on 2026-10-12.
- `task.md` is STALE: header says Sprint 6, all 13 boxes unchecked despite "Complete (Launched)",
  and it points at the old `agents/mouse.docs/sprint_log.md` path. Sprint 7 never written to it.
- Working tree has a large uncommitted bob-protocol migration: `agents/<persona>.docs/` -> 
  `agents/<persona>/` (107 deletions, 9 untracked persona dirs), `SKILL.md.txt` files removed,
  plus untracked `.claude/`, `.cursorrules`, `.github/`, root `AGENT.md`.
- Open backlog (1 item, unscheduled): bracket-markup sweep in `examples/demo.py` narrative text —
  rich `Text()`/`Text.append()` print `[bold red]..[/bold red]` literally. Filed by Smith to Cypher.
- Never done: interactive `sudo make demo-live` pass on a real TTY for Sprint 7 (Neo flagged, no TTY).

## Important Notes
- Board of record is root `task.md` per Global Agent Standard #11 — no secondary sprint file.
- 2026-10-12 Sprint 8 planned: task.md rewritten (was stale Sprint 6 board), 4 phases one story each, order FING-23 -> 25 -> 24 -> 26.
- 2026-10-12 Sprint 8 closed: 16/16 pts, 4 phases, 1 fix cycle. task.md shows it complete with the retro backlog.
- 2026-10-12 Sprint 9 planned (task.md): P0 Tank env, P1 Neo split, P2 Tank CI/publish, P3 Neo chat-report. Post a phase marker (--cmd 'phase N') at each phase start and 'phase close' at close.
- 2026-10-13 Sprint 9 closed: 18/18 pts, 4 phases, 0 fix cycles; phase markers posted for 0-3 and close.
- 2026-10-13 Session close. After Sprint 9: fix/single-makefile, fix/docs-groom,
  fix/remove-legacy-tools, fix/session-close — all merged to main with --no-ff. main is ahead of
  origin and tagged v0.1.0; nothing pushed. Post-sprint chat archived as CHAT_POST_SPRINT_9.

## Current Task
**Status:** No sprint in flight. Sprint 9 closed; post-sprint maintenance closed.

## Next Steps
Cold start:
1. Read `task.md` (board), `docs/SDLC.md` (how changes are made) and the last message in
   `agents/CHAT.md`.
2. Waiting on the owner: PyPI one-time setup, `git push origin main`, `git push origin v0.1.0`,
   and the bob_protocol sync (see task.md, Owner actions).
3. Next request in the queue: **artifact rubrics** — the owner still has to choose the pilot
   (stories alone, or stories + SDLC + lessons). Inventory and recommendation were given
   2026-10-13; start by writing a stories template with a rubric appendix once they choose.
4. Starting any sprint: confirm `docs/SDLC.md` exists, create `sprint-<N>` from a clean `main`
   before Cypher writes stories (next is sprint-10, next story STORY-FING-31), post a
   `--cmd "phase <N>"` marker at each phase start and `phase close` at close-out.
5. Active scope is the fingerprint tool only; do not schedule work on parked modules.

---
*Last updated: 2026-10-13T20:02:25-04:00*
