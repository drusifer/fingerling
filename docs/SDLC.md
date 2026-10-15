# Fingerling — SDLC

How this project is built, tested, changed and released — the source of truth for change
management across the whole project. **Owned by Tank**; to change anything here, ask
`@Tank *devops sdlc <what and why>` — the mechanism and this document change together.

**Active scope:** none in this repository. The fingerprint tool moved to its own repository,
[drusifer/sketch-tastic](https://github.com/drusifer/sketch-tastic), on 2026-10-14 (Sprint 18);
it is developed, tested and released there. What remains here — n-gram matcher, policy compiler,
webhook server, GitOps, sandbox/vaccine, eBPF capture, TUI demo — is parked: it must keep
importing against sketch-tastic and its existing tests must keep passing, but it gets no new
gates or manual checks.

Process decisions below were made by the project owner on 2026-10-12. Tooling decisions that
are agreed but not yet built are listed in section 11.

## 1. Toolchain

| | Python |
|---|---|
| Runtime version | 3.14 and later — `requires-python = ">=3.14"`; 3.14 and 3.15 are tested; development uses 3.14 (`.python-version`) |
| Manifest | `pyproject.toml` at the root: the parked `fingerling` package, its dependencies (including `sketch-tastic` from git, section 4), dev tools in `[dependency-groups] dev`, tool config |
| Lockfile | `uv.lock` (committed) |
| Package manager | `uv`; build backend `hatchling` |
| Local environment | `.venv/` (gitignored, isolated from system site-packages) |

Other required tools:

- `make`.
- `uv` — install once per machine with `pipx install uv` (no sudo). It also supplies the
  interpreters for `make test-all`.
- `git` with network access to GitHub — `make install` fetches sketch-tastic at the pinned commit.
- `gitleaks` — on `PATH`; needed by `make secrets` and the pre-commit hook.
- `sudo` + `bpftrace` — only for `make demo-live` (parked).
- `bobp` — team tooling (`bobp make`, `bobp chat`, `bobp tldr`); wraps this Makefile but adds
  no targets to it. `via` — behind `make via_index`. Neither is a project dependency.

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

There is exactly one Makefile, at the repository root, and it is the only entry point: no
included or generated make files, no wrapper scripts. Environment-using recipes run tools from
`.venv/bin/` and stop with "No .venv - run 'make install' first" if it is missing. Agents invoke
targets as `bobp make <target>`.

| Target | Runs | Notes |
|---|---|---|
| `install` | `uv sync --all-extras` + `install-hooks` | exact install from `uv.lock`, including sketch-tastic from git; idempotent |
| `install-hooks` | `git config core.hooksPath .githooks` | enables the gitleaks pre-commit hook |
| `test` | `unittest discover -s tests` | the parked modules, against the installed sketch-tastic |
| `test-all` | the tests on Python 3.14 and 3.15 in throwaway uv environments | downloads interpreters on first use |
| `lint` | `ruff check .` and `ruff format --check .` | changes nothing |
| `format` | `ruff check --select I --fix .` and `ruff format .` | rewrites files |
| `secrets` | `gitleaks detect --source .` | git-aware: scans history and tree |
| `check` | `python -m compileall -q` over `fingerling`, `examples`, `tests` | syntax check only |
| `demo`, `demo-live` | `examples/demo.py` (the latter under `sudo`) | parked |
| `clean` | removes `__pycache__`, `*.egg-info`, `.ruff_cache`, `dist`, `data`, then directories left empty | keeps `.venv` |
| `distclean` | `clean` + removes `.venv/` | |
| `help` | lists targets | default goal |
| `via_index` | `via index .` | builds the code index for the `via` tool |

The tool's own targets (`build`, `smoke`, `quality`, `run`, `gharchive`, `release-check`) moved
to sketch-tastic with it. Lint rules are pinned in `[tool.ruff.lint] select` (`E4`, `E7`, `E9`,
`F`, `I`); widening them is a Mechanism-class change. `agents/` and Markdown are excluded.

## 4. Dependencies

- **sketch-tastic** is a git dependency pinned to one commit:
  `[tool.uv.sources] sketch-tastic = { git = "https://github.com/drusifer/sketch-tastic", rev = "<sha>" }`.
  To move to a newer version, set `rev` to a pushed commit, run `uv lock`, then `make install`
  and `make test`. The pin only moves on purpose — never to an unpushed commit.
- **Add a dependency:** `uv add <package>`; a dev tool: `uv add --dev <package>`.
- **Optional features:** `demo` extra = `rich`, needed only by `examples/demo.py`.
- **Upgrade / remove:** `uv lock --upgrade-package <package>` / `uv remove <package>`, then
  `make install`.
- **Commit afterwards:** `pyproject.toml` **and** `uv.lock`, together. Never hand-edit `uv.lock`.
- **Who:** Neo adds and bumps dependencies, including the sketch-tastic pin. A new package
  manager, language or Python version is a mechanism change — Tank's.

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
7. **Integrate** — after Tank's `*devops sdlc-check` passes and Cypher launches the sprint, and
   once the chat log is confirmed to hold every phase marker, Smith's approvals, the retro and
   the launch (a message `bobp chat` rejected was never recorded), agents
   merge to `main` with `git merge --no-ff sprint-<N>`, apply the version bump and tag (section 7;
   suspended during mainline development), and delete the branch. **Agents never push**; the project owner pushes `main` and tags.
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

Mouse posts a phase marker to `agents/CHAT.md` at the start of each phase —
`bobp chat "<phase description>" --persona Mouse --cmd "phase <N>"`, and `--cmd "phase close"`
when close-out begins — so the report can be split. Messages before the first marker appear
under "Planning". The full chat text is archived alongside as `CHAT_<SPRINT>.md`. Oracle runs
`bobp chat-report` on the sprint branch after Cypher's launch, and the archive is committed
before the merge.

### Rules

- Never commit `.venv/`, build output, local settings, or secrets.
- A sprint merges to `main` only after Tank's `*devops sdlc-check` (section 10) passes.
- **Rollback:** `git revert -m 1 <merge commit>` on a `fix/` branch backs out a whole sprint;
  revert individual commits for anything smaller. Fingerprint set files written by an older
  format are not migrated — keep a copy before upgrading across a format change.
- **Changing this document:** only Tank edits it; every edit updates the Last verified line.

## 7. Versioning and release

- **Nothing is released from this repository.** The `fingerling` package is private
  (`Private :: Do Not Upload`) and keeps a static version. The tool it builds on is versioned and
  released in sketch-tastic.
- **No backwards compatibility before 1.0** and **mainline development** (owner, 2026-10-13/14)
  still apply: no tags, version bumps or release commits. Existing local tags `v0.1.0` and
  `v0.2.0` belong to the moved package's history and are left as they are.

## 8. CI / deploy

| Workflow | Trigger | Does |
|---|---|---|
| `.github/workflows/ci.yml` | by hand only (`workflow_dispatch`); push and pull-request triggers disabled by the owner on 2026-10-14 | Matrix over Python 3.14 and 3.15: `make install`, `make lint`, `make test`. Separate job: `make secrets` over the full history. |

The publish workflow moved to sketch-tastic. There is no deploy target; KubeArmor enforcement in
the demo is simulated.

## 9. Known deviations

- **`uv`, `gitleaks` and network access to GitHub are machine prerequisites**, not installed by
  `make install`.
- **Parked modules are outside the manual gates.** `make demo-live` needs a terminal, root and
  `bpftrace` and has not been run since before Sprint 8; by the owner's decision no process is
  built around it.

## 10. Conformance check

Run by Tank at sprint close (`*devops sdlc-check`):

1. `make distclean && make install && make lint && make test && make secrets` passes, and
   `make test-all` passes on every supported Python.
2. Every third-party import is declared in `pyproject.toml`; `fingerling` gets the tool only
   through the `sketch-tastic` dependency (no `fingerprint_sampler`, no vendored copy), pinned to a
   pushed commit; `uv lock --check` reports the lockfile is up to date.
3. `.venv/pyvenv.cfg` still says `include-system-site-packages = false`.
4. Every target in section 3 exists and still does what the table says; there is still only one
   Makefile, with no team-tooling targets.
5. No doc or script tells people to run bare `python3`/`pip` against the project.
6. `.venv/` and `*.egg-info/` are ignored; `git config core.hooksPath` is `.githooks`.
7. This sprint's changes followed section 6: on the sprint branch, Conventional Commits, chat
   report with a section for every phase and for close, nothing pushed without the owner.
8. A second `make install` changes nothing.
9. The workflow invokes only `make` targets that exist.

## 11. Agreed changes not yet built

None. Everything decided on 2026-10-12 was built in Sprint 9. New decisions that are agreed but
not yet built are listed here until they land.

---
*Last verified: 2026-10-14 at Sprint 18 close (`*devops sdlc-check`), by Tank — from-clean
`make distclean install lint test secrets` and `make test-all` (3.14, 3.15) green with sketch-tastic
installed from GitHub at the pinned commit; lockfile current; venv isolated; hooks set; a second
install changes nothing; `ci.yml` calls existing targets only.*
