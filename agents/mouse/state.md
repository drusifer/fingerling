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
- 2026-10-13 Sprint 10 planned: 4 phases, Bob implements; markers posted per phase.
- 2026-10-13 Sprint 10 closed: 10/10 pts. Its chat record lost 12 messages to silent failures (over-length bobp chat calls with output discarded); posted late and archived as CHAT_SPRINT_10_CLOSE. Always confirm markers and handoffs were posted - check the bobp chat result and message length (512).
- 2026-10-13 Shutdown. Sprints 8-10 closed; maintenance branches merged; main pushed. bob_protocol fully synced and pushed.
- 2026-10-13 22:10 status report (cold start): CI checked with `gh run list` - all 3 runs on main from the 2026-10-13 pushes passed (lint + test on 3.10-3.13, secret scan). main is level with origin; tag v0.1.0 still local only. `task.md` Owner actions still lists the CI check - remove that line on the next branch that touches the board.

- 2026-10-13 GLOB/REGEX/REGSUB delivered outside a sprint on fix/glob-regex-regsub (Neo > Trin > Morpheus > Smith, 0 fix cycles). Not bumped or tagged: owner decides between 0.2.0 and moving the unpublished v0.1.0 tag.

- 2026-10-13 Sprint 11 closed: 8/8 pts, 3 phases (0 Tank, 1-2 Neo), 0 fix cycles, Tier 2. Released 0.2.0 (tag v0.2.0 local). Queued for bob_protocol: Tank dependency analysis tool; Trin test strategy doc.

- 2026-10-14 Sprint 12 closed: 13/13 pts (FING-38..41), 4 phases, 0 fix cycles; FING-41 smoke suite added mid-sprint and trimmed to 3 tests at close (owner: smoke sparingly). No release (mainline). Owner rules this sprint: no ad hoc testing; smoke sparingly; KISS.

- 2026-10-14 Sprint 13 closed: Fingerprint UX, 5/5 pts (FING-42..44), Tier 2, 2 phases, 0 fix cycles. Merged to main, not pushed. No release.
- 2026-10-14 Sprint 14 closed: Weighted Aggregates (op: SIZE), 2/2 pts (FING-45), Tier 2, 1 phase, 0 fix cycles. Merged to main, not pushed.

## Current Task
**Status:** No sprint in flight (Sprint 11 closed 2026-10-13).

## Next Steps
Cold start:
1. Read `task.md` (top: "Since Sprint 12"), `docs/SDLC.md`, and the last messages in `agents/CHAT.md`.
2. Owner rules in force: no backwards compatibility and formats at `version: 0` until 1.0; mainline development (no tags or releases); CI runs by hand only — never poll it; KISS; no ad hoc testing (tests and `bobp make` only, smoke sparingly at close); no `rm` (use `bobp make clean`); `*fix` diagnoses and asks before changing code.
3. State of the tool: profiles = fields (with modifiers and optional `type: DATE/DATETIME`) + aggregates; built-in `meta` from `builtin.yaml`; try it with `bobp make gharchive` (downloads one GH Archive hour).
4. Queued (bob_protocol repo): Tank dependency analysis tool; Trin test strategy doc. Backlog in `task.md`.
5. Next sprint is sprint-15, next story STORY-FING-46. Keep chat messages under 512 characters and check every `bobp chat` result.

---
*Last updated: 2026-10-14T17:40:00-04:00*
