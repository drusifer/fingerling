# fingerling
Project Fingerling provides an automated, self-learning, adaptive software immune system

## Documentation

| Doc | Purpose |
|---|---|
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | **Start here** — module reference + end-to-end demo |
| [docs/SOURCE_SPEC.md](docs/SOURCE_SPEC.md) | Original BRD/PRD/ARCH + source user stories |
| [docs/USER_STORIES.md](docs/USER_STORIES.md) | POC sprint backlog (STORY-FING-01..04) |
| [docs/ARCH.md](docs/ARCH.md) | Architecture: modules, data structures, decisions log |
| [docs/SDLC.md](docs/SDLC.md) | How the project is built, tested, changed and released — source of truth for change management |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Chronological record of architectural/product decisions |
| [docs/LESSONS.md](docs/LESSONS.md) | Lessons learned during sprint execution |
| [task.md](task.md) | Current sprint task board |

## Team (Bob Protocol)

Multi-persona coordination lives under `agents/` — see [AGENTS.md](AGENTS.md) for the protocol
and [agents/CHAT.md](agents/CHAT.md) for the team's live coordination log.

## Setup

```sh
pipx install uv  # once per machine
make install     # builds .venv from pyproject.toml + uv.lock
make test
```

## Fingerprint an event stream

`fingerprint` folds any JSONL event stream into a fingerprint set that grows across runs:

```sh
make fingerprint ARGS="-p packages/fingerprint-sampler/examples/access_log.yaml -s web.fingerprints.yaml packages/fingerprint-sampler/examples/access_log.jsonl"
some-producer | .venv/bin/fingerprint merge -p my-profile.yaml -s my.fingerprints.yaml -
```

See [docs/USER_GUIDE.md](docs/USER_GUIDE.md#fingerprint-cli) for the profile format and options.

## Vaccination demo

```sh
sudo make demo-live     # interactive TUI; needs Linux, root and bpftrace
```
