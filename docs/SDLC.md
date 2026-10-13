# Fingerling — SDLC

How this project is built, tested, changed and released — the source of truth for change
management across the whole project. **Owned by Tank**; to change anything here, ask
`@Tank *devops sdlc <what and why>` — the mechanism and this document change together.

**Active scope:** only the fingerprint tool (tokenizer, aggregators, fingerprint set, profiles,
CLI) is under active development. The rest of the project — n-gram matcher, policy compiler,
webhook server, GitOps, sandbox/vaccine, eBPF capture, TUI demo — is parked: it must keep
importing and its existing tests must keep passing, but it gets no new gates or manual checks.

Process decisions below were made by the project owner on 2026-10-12. Tooling decisions that
are agreed but not yet built are listed in section 11; sections 1-5 and 8 describe what exists
today and are updated as each lands.

## 1. Toolchain

| | Python |
|---|---|
| Runtime version | 3.10 - 3.13 — `requires-python = ">=3.10"` in `pyproject.toml`; all four are tested |
| Manifest | `pyproject.toml` (PEP 621 `[project]`; dev tools in `[dependency-groups] dev`; tool config in `[tool.*]`) |
| Lockfile | `uv.lock` (committed) |
| Package manager | `uv` |
| Local environment | `.venv/` (gitignored, isolated from system site-packages) |

Other required tools:

- `make`.
- `uv` — install once per machine with `pipx install uv` (no sudo). It also supplies the
  interpreters for `make test-all`.
- `gitleaks` — on `PATH`; needed by `make secrets` and the pre-commit hook.
- `sudo` + `bpftrace` — only for `make demo-live` (parked).
- `bobp`, `via`, `rg` — team tooling behind `make chat`, `make via_index`, `make tldr`; not
  project dependencies.

## 2. Setup

From a clean checkout:

```sh
pipx install uv   # once per machine
make install      # uv sync --all-extras, and points git at .githooks/
make test
```

Nothing is installed into the system Python (it is externally managed, PEP 668). Never use
`sudo pip` or `--break-system-packages`. A target that needs root calls the venv interpreter by
path (`sudo .venv/bin/python ...`), never `sudo python3`.

## 3. Make targets

The Makefile is the only entry point. Environment-using recipes run tools from `.venv/bin/` and
stop with "No .venv - run 'make install' first" if it is missing. Agents invoke targets as
`bobp make <target>`.

| Target | Runs | Notes |
|---|---|---|
| `install` | `uv sync --all-extras` + `install-hooks` | exact install from `uv.lock`; idempotent |
| `install-hooks` | `git config core.hooksPath .githooks` | enables the gitleaks pre-commit hook |
| `test` | `.venv/bin/python -m unittest discover -s tests` | `ARGS="tests.test_cli"` runs one module |
| `test-all` | the suite on Python 3.10, 3.11, 3.12, 3.13 in throwaway uv environments | downloads interpreters on first use |
| `lint` | `ruff check .` and `ruff format --check .` | changes nothing |
| `format` | `ruff check --select I --fix .` and `ruff format .` | rewrites files |
| `secrets` | `gitleaks detect --source .` | git-aware: scans history and tree |
| `check` | `python -m compileall -q fingerling examples tests` | syntax check only |
| `run` | `.venv/bin/fingerling $(ARGS)` | the CLI |
| `fingerprint` | `.venv/bin/fingerling fingerprint $(ARGS)` | project-specific |
| `demo`, `demo-live` | `examples/demo.py` (the latter under `sudo`) | parked |
| `clean` | removes `__pycache__`, `*.egg-info`, `.ruff_cache`, `dist` | keeps `.venv` |
| `distclean` | `clean` + removes `.venv/` | |
| `help` | lists targets | default goal |
| `tldr`, `via_index`, `chat` | team tooling | use system tools, not `.venv` |

Standard targets deliberately absent: `build` — agreed, not yet built (section 11).

Lint rules are pinned in `[tool.ruff.lint] select` (`E4`, `E7`, `E9`, `F`, `I`); widening them
is a Mechanism-class change. `agents/` (BobProtocol tooling) and Markdown are excluded.

## 4. Dependencies

- **Add a runtime dependency:** `uv add <package>` (edits `[project] dependencies` and
  `uv.lock`).
- **Add a dev tool:** `uv add --dev <package>` (the `dev` dependency group).
- **Optional features:** `demo` extra = `rich`, needed only by `examples/demo.py`.
- **Upgrade / remove:** `uv lock --upgrade-package <package>` / `uv remove <package>`, then
  `make install`.
- **Commit afterwards:** `pyproject.toml` **and** `uv.lock`, together. Never hand-edit `uv.lock`.
- **Who:** Neo adds and bumps dependencies. A new package manager, language or Python version is
  a mechanism change — Tank's.

## 5. Quality gates

| Gate | Target | Required before |
|---|---|---|
| Lint + format | `make lint` | every handoff to Trin; sprint close |
| Tests | `make test` | every handoff to Trin; sprint close |
| Tests, all Pythons | `make test-all` | sprint close |
| Secret scan | `make secrets` | sprint close; staged changes are scanned on every commit by the hook |

## 6. Change management

This document is the project's source of truth for how a change gets from request to done.
Where another document, skill or habit disagrees with it, this one wins — and the disagreement
is reported to Tank so one of them gets fixed.

### Change classes

| Class | Examples | Proposed by | Approved by | Must pass | Recorded in |
|---|---|---|---|---|---|
| Routine | feature, fix, refactor, docs, adding a dependency via section 4 | the user, or a Cypher story | Trin UAT, then Morpheus review | section 5 gates | commit, `task.md`, sprint stories |
| Mechanism | toolchain, manifest layout, make targets, gates, CI, this document | anyone, via `@Tank *devops sdlc` | Tank; the project owner for a new policy | from-clean rebuild + section 5 gates | this file, `docs/DECISIONS.md` |
| Release | version bump, tag, publish | Cypher at sprint launch | project owner pushes the tag | section 5 gates on the merge commit | tag, sprint chat report |
| Emergency | fix outside a sprint | the user | the user | section 5 gates | commit; reviewed at next sprint close |

### Flow

1. **Request** — the user asks in the session; it is logged to `agents/CHAT.md`. Anything larger
   than one concrete change runs as a sprint (`sprint` skill; Tier 1 or 2 per `AGENTS.md`).
2. **Branch** — every sprint works on its own branch, `sprint-<N>`, created from an up-to-date,
   clean `main` when the sprint starts. An emergency fix uses `fix/<slug>`. Nothing is committed
   directly to `main`.
3. **Implement** — through `make` targets only; tests accompany behaviour changes.
4. **Gate** — the section 5 gates pass locally before each handoff.
5. **Review** — Trin verifies each acceptance criterion; Morpheus reviews the code; Smith tests
   user-facing behaviour at sprint close.
6. **Commit** — agents commit on the sprint branch as work passes review (at least once per
   phase), using Conventional Commits (below).
7. **Integrate** — after Tank's `*devops sdlc-check` passes and Cypher launches the sprint, agents
   merge to `main` with `git merge --no-ff sprint-<N>`, apply the version bump and tag (section 7),
   and delete the branch. **Agents never push**; the project owner pushes `main` and tags.
8. **Record** — the sprint chat report (below), `docs/DECISIONS.md` for decisions, user docs.

### Commit messages — Conventional Commits

```
<type>(<scope>)<!>: <summary in the imperative, no full stop>

<why, and the story id, e.g. STORY-FING-27>

BREAKING CHANGE: <what breaks and what to do>      (only when applicable)
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `build` (manifest, lockfile, Makefile), `ci`,
`chore`. Scope is the package or area (`fingerprint`, `cli`, `sdlc`, `agents`). A breaking change
carries `!` after the scope and a `BREAKING CHANGE:` footer. One logical change per commit.

### The record — sprint chat report

There is no `CHANGELOG.md`. The durable, human-readable record of a sprint is one document,
`agents/chat_archive/CHAT_<SPRINT>.md`, produced by `bobp chat-report` at sprint close:

1. the sprint description at the top;
2. then, for each phase in order: the phase description followed by the chat diagram for that
   phase.

Mouse posts a phase marker to `agents/CHAT.md` at the start of each phase so the report can be
split. *(The per-phase format is being built in Sprint 9; until then the report is a single
undivided diagram.)*

### Rules

- Never commit `.venv/`, build output, local settings, or secrets.
- A sprint merges to `main` only after Tank's `*devops sdlc-check` (section 10) passes.
- **Rollback:** `git revert -m 1 <merge commit>` on a `fix/` branch backs out a whole sprint;
  revert individual commits for anything smaller. Fingerprint set files written by an older
  format are not migrated — keep a copy before upgrading across a format change.
- **Changing this document:** only Tank edits it; every edit updates the Last verified line.

## 7. Versioning and release

- **Scheme:** Semantic Versioning, bumped according to what changed since the last tag:
  breaking change → major, new feature → minor, fixes only → patch. While the version is
  `0.x`, a breaking change bumps the minor instead. The Conventional Commit types on the sprint
  branch determine the bump; Cypher states it in the launch message.
- **Version lives in:** `[project] version` in `pyproject.toml` (currently `0.8.0`).
- **Bumped and tagged:** by Tank on `main` as part of the sprint merge — a `build: release
  v<version>` commit and an annotated tag `v<version>`.
- **CLI entry points:** `[project.scripts]` — `fingerling`, installed to `.venv/bin/`.
- **Artifact:** none yet. Publishing the fingerprint tool to PyPI is agreed (section 11).
- **Data format versions:** fingerprint set files carry `version: 1`; profiles carry
  `version: 1`. A format change is a breaking change.

## 8. CI / deploy

None — everything runs locally. `.github/` holds only editor instructions, no workflows.
There is no deploy target; KubeArmor enforcement in the demo is simulated.

If CI is added it must run `make install && make test`, not raw tool commands.

## 9. Known deviations

- **No CI yet** — agreed and scheduled; see section 11.
- **`uv` and `gitleaks` are machine prerequisites**, not installed by `make install`.
- **Parked modules are outside the manual gates.** `make demo-live` needs a terminal, root and
  `bpftrace` and has not been run since before Sprint 8; by the owner's decision no process is
  built around it while the fingerprint tool is the focus.

## 10. Conformance check

Run by Tank at sprint close (`*devops sdlc-check`):

1. `make distclean && make install && make lint && make test && make secrets` passes, and
   `make test-all` passes on every supported Python.
2. Every third-party import in `fingerling/`, `examples/` and `tests/` is declared in
   `pyproject.toml`, and `uv lock --check` reports the lockfile is up to date.
3. `.venv/pyvenv.cfg` still says `include-system-site-packages = false`.
4. Every target in section 3 exists and still does what the table says; new targets are listed.
5. No doc or script tells people to run bare `python3`/`pip` against the project.
6. `.venv/` and `*.egg-info/` are ignored; `requires-python` unchanged or deliberately bumped;
   `git config core.hooksPath` is `.githooks`.
7. This sprint's changes followed section 6: made on the sprint branch, Conventional Commit
   messages, right class and approval, chat report produced, nothing pushed by agents.
8. `.venv/bin/fingerling fingerprint --help` runs, and a second `make install` changes nothing.

## 11. Agreed changes not yet built

Decided by the project owner on 2026-10-12 and scheduled for Sprint 9. Tank moves each item
into the sections above, and off this list, when it lands.

| Change | Decision | Lands in |
|---|---|---|
| CI | GitHub Actions: `make install`, lint, test and gitleaks on every push and sprint branch | section 8 |
| Publishing | PyPI trusted publishing from a workflow triggered by a version tag, only if the gates pass; `make build` | sections 3, 7, 8 |
| Package split | The fingerprint tool becomes its own package in this repo, published on its own (the name `fingerling` is taken on PyPI; `fingerprint-sampler` is the working name). Parked modules stay unpublished and import it | sections 1, 7 |
| Per-phase chat report | `bobp chat-report` emits sprint description, then per-phase description + diagram, from phase markers | section 6 |

---
*Last verified: 2026-10-12 on branch `sprint-9` (Phase 0), by Tank — from-clean rebuild with uv,
lint clean, 178/178 tests on Python 3.10, 3.11, 3.12 and 3.13, gitleaks clean.*
