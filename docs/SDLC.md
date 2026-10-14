# Fingerling — SDLC

How this project is built, tested, changed and released — the source of truth for change
management across the whole project. **Owned by Tank**; to change anything here, ask
`@Tank *devops sdlc <what and why>` — the mechanism and this document change together.

**Active scope:** only the fingerprint tool (tokenizer, aggregators, fingerprint set, profiles,
CLI) is under active development. The rest of the project — n-gram matcher, policy compiler,
webhook server, GitOps, sandbox/vaccine, eBPF capture, TUI demo — is parked: it must keep
importing and its existing tests must keep passing, but it gets no new gates or manual checks.

Process decisions below were made by the project owner on 2026-10-12. Tooling decisions that
are agreed but not yet built are listed in section 11.

## 1. Toolchain

| | Python |
|---|---|
| Runtime version | 3.14 and later — `requires-python = ">=3.14"` in both manifests; 3.14 and 3.15 are tested; development uses 3.14 (`.python-version`) |
| Manifest | root `pyproject.toml` (the parked `fingerling` package, the uv workspace, dev tools in `[dependency-groups] dev`, tool config) and `packages/fingerprint-sampler/pyproject.toml` (the published package) |
| Lockfile | `uv.lock` (committed; one for the whole workspace) |
| Package manager | `uv` (workspace: root + `packages/*`); build backend `hatchling` |
| Local environment | `.venv/` (gitignored, isolated from system site-packages) |

Other required tools:

- `make`.
- `uv` — install once per machine with `pipx install uv` (no sudo). It also supplies the
  interpreters for `make test-all`.
- `gitleaks` — on `PATH`; needed by `make secrets` and the pre-commit hook.
- `sudo` + `bpftrace` — only for `make demo-live` (parked).
- `bobp` — team tooling (`bobp make`, `bobp chat`, `bobp tldr`); wraps this Makefile but adds
  no targets to it. `via` — behind `make via_index`, and used by `bobp tldr` to list files.
  Neither is a project dependency.

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
included or generated make files, no wrapper scripts. Environment-using recipes run tools from `.venv/bin/` and
stop with "No .venv - run 'make install' first" if it is missing. Agents invoke targets as
`bobp make <target>`.

| Target | Runs | Notes |
|---|---|---|
| `install` | `uv sync --all-packages --all-extras` + `install-hooks` | exact install from `uv.lock`; idempotent |
| `install-hooks` | `git config core.hooksPath .githooks` | enables the gitleaks pre-commit hook |
| `test` | `test-fingerprint` then `test-fingerling` | both suites |
| `test-fingerprint` | `unittest discover` in `packages/fingerprint-sampler` | `ARGS` is passed to `unittest` in place of `discover`; it does not currently find a single module (backlog) |
| `test-fingerling` | `unittest discover -s tests` | parked modules + compatibility shims |
| `smoke` | `build`, then the `packages/fingerprint-sampler/smoke` suite inside a throwaway environment holding only the built wheel | runs the installed `fingerprint` command, the shipped examples and the README's own examples |
| `test-all` | both suites on Python 3.14 and 3.15 in throwaway uv environments | downloads interpreters on first use |
| `lint` | `ruff check .` and `ruff format --check .` | changes nothing |
| `quality` | extended `ruff` rules, `vulture`, `radon cc -nc` over `packages/fingerprint-sampler/src` | report only, always exits 0; Trin reads it at UAT |
| `format` | `ruff check --select I --fix .` and `ruff format .` | rewrites files |
| `secrets` | `gitleaks detect --source .` | git-aware: scans history and tree |
| `build` | `uv build --package fingerprint-sampler --out-dir dist`, then runs the built wheel in a clean environment | wheel + sdist in `dist/` (gitignored) |
| `release-check` | compares `TAG=v<x.y.z>` with the fingerprint-sampler version | used by the publish workflow |
| `check` | `python -m compileall -q` over all sources | syntax check only |
| `run` | `.venv/bin/fingerprint $(ARGS)` | the CLI |
| `fingerprint` | `.venv/bin/fingerprint merge $(ARGS)` | project-specific |
| `demo`, `demo-live` | `examples/demo.py` (the latter under `sudo`) | parked |
| `clean` | removes `__pycache__`, `*.egg-info`, `.ruff_cache`, `dist` | keeps `.venv` |
| `distclean` | `clean` + removes `.venv/` | |
| `help` | lists targets | default goal |
| `via_index` | `via index .` | builds the code index for the `via` tool; uses the system `via` |

Standard targets deliberately absent: none.

Lint rules are pinned in `[tool.ruff.lint] select` (`E4`, `E7`, `E9`, `F`, `I`); widening them
is a Mechanism-class change. `agents/` (BobProtocol tooling) and Markdown are excluded.

## 4. Dependencies

- **Add a runtime dependency:** `uv add --package fingerprint-sampler <package>` for the
  published package, or `uv add <package>` for the parked `fingerling` package. Anything added to
  fingerprint-sampler becomes an install requirement for PyPI users — keep it minimal.
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
| Smoke (installed wheel + README) | `make smoke` | every handoff to Trin; sprint close |
| Tests, all Pythons | `make test-all` | sprint close |
| Secret scan | `make secrets` | sprint close; staged changes are scanned on every commit by the hook |
| Package build | `make build` | sprint close; before any tag |

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

- **What is versioned:** one stream — the published package, `fingerprint-sampler`. Its version
  is `[project] version` in `packages/fingerprint-sampler/pyproject.toml` (currently `0.2.0`).
  The root `fingerling` package is private (`Private :: Do Not Upload`), keeps a static version,
  and is never tagged or published.
- **Scheme:** Semantic Versioning, bumped according to what changed in the published package
  since the last tag: breaking change → major, new feature → minor, fixes only → patch. While the
  version is `0.x`, a breaking change bumps the minor instead. The Conventional Commit types on
  the sprint branch determine the bump; Cypher states it in the launch message. A sprint that
  changes nothing in the published package makes no release.
- **No backwards compatibility before 1.0** (owner, 2026-10-13): while the version is `0.x`, no
  effort goes into compatibility — no shims, aliases, deprecation paths, migration messages or
  tests that pin old behaviour. Old forms are deleted outright; the minor bump and a line in
  `docs/DECISIONS.md` are the whole cost of a breaking change.
- **Currently suspended — mainline development** (owner, 2026-10-14): agents create no tags,
  make no version bumps and no release commits until the owner says otherwise. Sprints still
  merge to `main`; the version stays `0.2.0`. Existing local tags `v0.1.0` and `v0.2.0` were
  never pushed and are left as they are. The rules below apply again when releases resume.
- **Bumped and tagged:** by Tank on `main` as part of the sprint merge — a
  `build: release v<version>` commit (version field + `uv lock`) and an annotated tag
  `v<version>`. `make release-check TAG=v<version>` must pass.
- **Published:** pushing the tag triggers the publish workflow (section 8). Agents never push, so
  a release reaches PyPI only when the project owner pushes the tag.
- **Artifact:** wheel + sdist from `make build`. Distribution `fingerprint-sampler`, import
  package `fingerprint_sampler`, commands `fingerprint` and `fingerprint-sampler`.
- **Data format versions:** fingerprint set files carry `version: 1`; profiles carry
  `version: 1`. A format change is a breaking change.

## 8. CI / deploy

Both workflows call only `make` targets, so CI cannot drift from the local gates.

| Workflow | Trigger | Does |
|---|---|---|
| `.github/workflows/ci.yml` | every push (any branch) and pull request | Matrix over Python 3.14 and 3.15: `make install`, `make lint`, `make test`. Separate job: `make secrets` over the full history. |
| `.github/workflows/publish.yml` | push of a tag `v*` | Reruns the CI gates; `make release-check`; `make build`; publishes `dist/` to PyPI by trusted publishing (no stored token). |

**Exercised so far:** the CI workflow ran on the pushes of `main` on 2026-10-13 and passed
(Python 3.10-3.13 at the time, and the secret scan). The publish workflow has never run: no
version tag has been pushed.

**One-time setup by the project owner, before the first tag is pushed:**

1. On pypi.org → *Publishing* → add a **pending trusted publisher**: PyPI project name
   `fingerprint-sampler`, owner `drusifer`, repository `fingerling`, workflow `publish.yml`,
   environment `pypi`.
2. On GitHub → repository *Settings → Environments* → create an environment named `pypi`
   (optionally with yourself as a required reviewer, so each publish needs a click).

There is no deploy target; KubeArmor enforcement in the demo is simulated.

## 9. Known deviations

- **Publishing is unexercised** (section 8).
- **`uv` and `gitleaks` are machine prerequisites**, not installed by `make install`.
- **Parked modules are outside the manual gates.** `make demo-live` needs a terminal, root and
  `bpftrace` and has not been run since before Sprint 8; by the owner's decision no process is
  built around it while the fingerprint tool is the focus.

## 10. Conformance check

Run by Tank at sprint close (`*devops sdlc-check`):

1. `make distclean && make install && make lint && make test && make secrets && make build`
   passes, and `make test-all` passes on every supported Python.
2. Every third-party import is declared in the manifest of the package that uses it —
   `fingerprint_sampler` imports only PyYAML, python-jsonpath and jsonschema, and never imports `fingerling` —
   and `uv lock --check` reports the lockfile is up to date.
3. `.venv/pyvenv.cfg` still says `include-system-site-packages = false`.
4. Every target in section 3 exists and still does what the table says; new targets are listed;
   there is still only one Makefile, with no included make files and no team-tooling targets
   (`bobp chat` and `bobp tldr` replace `make chat` and `make tldr`).
5. No doc or script tells people to run bare `python3`/`pip` against the project.
6. `.venv/` and `*.egg-info/` are ignored; `requires-python` unchanged or deliberately bumped;
   `git config core.hooksPath` is `.githooks`.
7. This sprint's changes followed section 6: made on the sprint branch, Conventional Commit
   messages, right class and approval, chat report produced with a section for every phase and
   for close, nothing pushed by agents.
8. `make smoke` passes (it runs the installed `fingerprint` command), and a
   second `make install` changes nothing.
9. The workflows under `.github/workflows/` invoke only `make` targets that exist.

## 11. Agreed changes not yet built

None. Everything decided on 2026-10-12 was built in Sprint 9. New decisions that are agreed but
not yet built are listed here until they land.

---
*Last verified: 2026-10-13 at Sprint 11 close (`*devops sdlc-check`), by Tank — from-clean
rebuild on Python 3.14; lint clean; 154 + 59 tests on 3.14 and 3.15; gitleaks clean; `make build`
wheel (with `profile.schema.json`) runs in a clean 3.15 environment; lockfile current; one
Makefile. Section 7 gained the owner's no-backwards-compatibility-before-1.0 rule. Section 7: releases and tags
suspended for mainline development (owner, 2026-10-14).*
