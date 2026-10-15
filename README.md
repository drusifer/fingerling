# fingerling
Project Fingerling provides an automated, self-learning, adaptive software immune system.
Its fingerprinting core is **[sketch-tastic](https://github.com/drusifer/sketch-tastic)**, developed in its own repository.

## Documentation

| Doc | Purpose |
|---|---|
| [sketch-tastic](https://github.com/drusifer/sketch-tastic) | The fingerprint tool (sketches of JSONL event streams): quickstart, profiles, options |
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | The parked pipeline and demo; module reference |
| [docs/SDLC.md](docs/SDLC.md) | How the project is built, tested, changed and released — source of truth for change management |
| [docs/ARCH.md](docs/ARCH.md) | Architecture: modules and data structures of the parked pipeline |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Chronological record of architectural, product and process decisions |
| [docs/LESSONS.md](docs/LESSONS.md) | Engineering lessons learned during sprints |
| [docs/sprints/](docs/sprints/) | One stories-and-architecture document per sprint (`USER_STORIES_SPRINT<N>.md`) |
| [docs/SOURCE_SPEC.md](docs/SOURCE_SPEC.md) | Original BRD/PRD/architecture the project started from |
| [task.md](task.md) | Task board: last sprint, owner actions, queued requests, backlog |

## Team (Bob Protocol)

Multi-persona coordination lives under `agents/`:

| Path | Purpose |
|---|---|
| [AGENTS.md](AGENTS.md) | Shared instructions for every agent (also served as `AGENT.md`, `CHATGPT.md`, `GEMINI.md`, `.cursorrules`) |
| [agents/DOCUMENTATION_INDEX.md](agents/DOCUMENTATION_INDEX.md) | Index of personas, skills, templates and tools |
| [agents/CHAT.md](agents/CHAT.md) | Live coordination log for the current work |
| [agents/chat_archive/](agents/chat_archive/) | One per-phase report per closed sprint — the project's change record |
| `agents/<persona>/` | Each persona's instructions (`SKILL.md`), working memory (`state.md`) and work summaries |
| [agents/oracle/lessons.md](agents/oracle/lessons.md) | Standing rules agents must follow (process and tooling) |

## Setup

```sh
pipx install uv  # once per machine
make install     # builds .venv from pyproject.toml + uv.lock
make test
```

## The fingerprint tool

The tool that folds JSONL event streams into fingerprints moved to its own repository on
2026-10-14: **[sketch-tastic](https://github.com/drusifer/sketch-tastic)** (`pip install` name
`sketch-tastic`, commands `sketchtastic` and `skt`). fingerling installs it from GitHub at a
pinned commit (see `docs/SDLC.md` section 4).

## Vaccination demo (parked)

The rest of the repository — the `fingerling` pipeline built on fingerprint IDs — is parked while
the fingerprint tool is developed in sketch-tastic.

```sh
sudo make demo-live     # interactive TUI; needs Linux, root and bpftrace
```
