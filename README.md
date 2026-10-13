# fingerling
Project Fingerling provides an automated, self-learning, adaptive software immune system.
Its fingerprinting core is packaged separately as **fingerprint-sampler** (not yet on PyPI).

## Documentation

| Doc | Purpose |
|---|---|
| [packages/fingerprint-sampler/README.md](packages/fingerprint-sampler/README.md) | **Start here** — the fingerprint tool: quickstart, profiles, options |
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | Using the tool from a checkout; module reference; the parked pipeline and demo |
| [docs/SDLC.md](docs/SDLC.md) | How the project is built, tested, changed and released — source of truth for change management |
| [docs/ARCH.md](docs/ARCH.md) | Architecture: the two packages, modules, data structures |
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

## Fingerprint an event stream

The fingerprint tool is its own package, [`fingerprint-sampler`](packages/fingerprint-sampler/)
— this is where active development happens. It folds any JSONL event stream into a fingerprint
set that grows across runs:

```sh
make fingerprint ARGS="-p packages/fingerprint-sampler/examples/access_log.yaml -s web.fingerprints.yaml packages/fingerprint-sampler/examples/access_log.jsonl"
some-producer | .venv/bin/fingerprint merge -p my-profile.yaml -s my.fingerprints.yaml -
```

See the [package README](packages/fingerprint-sampler/README.md) for a quickstart, the profile
format and options.

## Vaccination demo (parked)

The rest of the repository — the `fingerling` pipeline built on fingerprint IDs — is parked while
the fingerprint tool is finished.

```sh
sudo make demo-live     # interactive TUI; needs Linux, root and bpftrace
```
