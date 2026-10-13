# Project Memory

A consolidated index of project-wide context, decisions and milestones. Maintained by the Oracle
and read by all agents. Detail lives in the linked documents; this file is the map.

## Project Context
- **Project Name:** Fingerling
- **Start Date:** 2026-07-12 (POC sprint)
- **What it is:** `fingerprint-sampler`, a tool that fingerprints and samples JSONL event
  streams, plus `fingerling`, a parked detection-and-response pipeline built on it.
- **Active scope (owner decision, 2026-10-12):** only the fingerprint tool. Everything else is
  parked until the fingerprint CLI is complete.
- **Process:** `docs/SDLC.md` (owned by Tank) is the source of truth for how changes are made.

## Major Decisions
| Date | Decision | Rationale | Consequences |
|------|----------|-----------|--------------|
| 2026-05-06 | Artifact-Based Verification | Chat latency and missed messages | Agents read docs directly; higher autonomy |
| 2026-10-12 | Fingerprint tool is the only active scope | Owner wants it finished first | No investment in parked modules |
| 2026-10-12 | `docs/SDLC.md` governs change management | One place for process rules | Branch per sprint, Conventional Commits, agents never push |
| 2026-10-13 | Fingerprint tool split into `fingerprint-sampler` | Installable on its own | Two packages in one uv workspace; `fingerling` re-exports it |

Full log: `docs/DECISIONS.md`.

## Milestones
| Sprint | Date | Delivered |
|---|---|---|
| 1 (POC) | 2026-07-12 | Tokenizer, warehouse, ring-buffer matcher, policy compiler |
| 2-4 | 2026-07-21 | Webhook server, GitOps delivery, sandbox/vaccination |
| 5-7 | 2026-07-22 to 08-08 | Interactive demos and TUI; pattern-based policy |
| 8 | 2026-10-12 | Fingerprint CLI, library JSONPath, aggregators, profiles |
| 9 | 2026-10-13 | `fingerprint-sampler` 0.1.0 (tagged, unpublished), uv, ruff, gitleaks, CI, per-phase chat report |

## Repository Structure Memory
- `packages/fingerprint-sampler/`: the fingerprint package (source, tests, examples, README).
- `fingerling/`, `examples/`, `tests/`: the parked pipeline, its demos and tests.
- `docs/`: project documentation; `docs/sprints/` holds one stories document per sprint
  (`USER_STORIES_SPRINT<N>.md`) — new sprint stories go there.
- `agents/`: persona instructions, state, skills, templates, chat log and archives
  (`agents/DOCUMENTATION_INDEX.md`).
- `task.md`: the task board (maintained by Mouse).
