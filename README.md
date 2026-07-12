# fingerling
Project Fingerling provides an automated, self-learning, adaptive software immune system

## Documentation

| Doc | Purpose |
|---|---|
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | **Start here** — module reference + end-to-end demo |
| [docs/SOURCE_SPEC.md](docs/SOURCE_SPEC.md) | Original BRD/PRD/ARCH + source user stories |
| [docs/USER_STORIES.md](docs/USER_STORIES.md) | POC sprint backlog (STORY-FING-01..04) |
| [docs/ARCH.md](docs/ARCH.md) | POC architecture: modules, data structures, decisions log |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Chronological record of architectural/product decisions |
| [docs/LESSONS.md](docs/LESSONS.md) | Lessons learned during sprint execution |
| [task.md](task.md) | Current sprint task board |

## Team (Bob Protocol)

Multi-persona coordination lives under `agents/` — see [AGENTS.md](AGENTS.md) for the protocol
and [agents/CHAT.md](agents/CHAT.md) for the team's live coordination log.

## Running Tests

```sh
make test
```

## Try It

```sh
python3 -m examples.demo
```

See [docs/USER_GUIDE.md](docs/USER_GUIDE.md) for a walkthrough of the output.
