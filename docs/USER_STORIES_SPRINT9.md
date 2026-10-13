# Sprint 9 User Stories: Fingerprint Package + SDLC Tooling

*   **Total Points**: 18 (Tier 1)
*   **Branch**: `sprint-9`
*   **Source**: Owner decisions of 2026-10-12, recorded in `docs/SDLC.md` section 11
*   **Status**: Gates 1 and 2 approved (Smith, 2026-10-12); FING-28 AC9-10 added at Gate 1

## Goal

Make the fingerprint tool a package someone can install from PyPI and trust, and put the
agreed development process in place around it. Only the fingerprint tool is in active scope;
the parked modules (n-gram matcher, policy, server, GitOps, sandbox/vaccine, capture, demo) must
keep working unchanged and get no new investment.

---

## STORY-FING-27: Reproducible, Gated Build Environment
**Points:** 5 · **Owner:** Tank (Phase 0)

**As a** contributor,
**I want** installs that are identical every time and gates that catch style, obvious bugs and
leaked secrets,
**so that** "it passed on my machine" means the same thing everywhere.

### Acceptance Criteria
1. `make install` builds the environment with `uv` from a committed `uv.lock`; a missing `uv`
   produces a one-line instruction, not a stack trace.
2. The project declares Python `>=3.10` and its test suite passes on 3.10, 3.11, 3.12 and 3.13.
3. `make lint` (ruff lint + format check) and `make format` exist; `make lint` passes on the
   whole repository.
4. `make secrets` runs `gitleaks` in git-aware mode and passes; a pre-commit hook scans staged
   changes and `make install` installs the hook.
5. `Makefile.prj` and `requirements.txt` are deleted and nothing references them.
6. `make distclean && make install && make test` passes; a second `make install` changes nothing.
7. `docs/SDLC.md` sections 1-5 describe the new toolchain and the items leave section 11.

---

## STORY-FING-28: Fingerprint Tool as Its Own Package
**Points:** 5

**As a** user who only wants to fingerprint event streams,
**I want** to install the fingerprint tool on its own,
**so that** I don't get eBPF, policy and demo code I have no use for.

### Acceptance Criteria
1. The fingerprint tool (tokenizer, aggregators, fingerprint set, profiles, CLI) is a separate
   installable package in this repository with its own manifest, version, README and tests.
2. Installed alone into an empty environment, it depends only on PyYAML and python-jsonpath, and
   its tests pass without the rest of the repository importable.
3. It provides its own command for merging a stream into a fingerprint set, with the same
   options, exit codes and messages as today's `fingerling fingerprint`.
4. Help and error text name commands that exist in that installation.
5. Existing fingerprint IDs, profile files and fingerprint set files are unchanged — a set
   written before the split merges cleanly after it.
6. The parked modules and their tests keep working with no behavioural change; existing imports
   such as `fingerling.tokenizer` and `fingerling.warehouse` still resolve.
7. `fingerling fingerprint ...` keeps working for existing users of this checkout.
8. Telemetry- and n-gram-specific helpers (`TELEMETRY_AGGREGATES`, `build_whitelist`) do not
   ship in the fingerprint package.
9. *(Smith Gate 1)* The package README is self-contained: a quickstart with a sample profile and
   sample events that works when pasted into a fresh environment, without files from this repo.
10. *(Smith Gate 1)* Running the tool the old way after the split never fails silently: any
    command that moved either still works or says what to run instead.

---

## STORY-FING-29: Continuous Integration and PyPI Publishing
**Points:** 4 · **Owner:** Tank

**As a** maintainer,
**I want** every push checked automatically and a tagged version published without handling
tokens,
**so that** nothing broken or unreviewed reaches users.

### Acceptance Criteria
1. A workflow runs on every push and pull request: install, lint, test (Python 3.10-3.13) and
   secret scan — each through the same `make` targets used locally.
2. A second workflow, triggered by a version tag, builds the fingerprint package and publishes it
   to PyPI by trusted publishing (no stored token), and only after the gates pass on that tag.
3. `make build` produces the package's wheel and sdist locally; the built wheel installs into a
   clean environment and its command runs.
4. The tag-to-version check: the publish workflow refuses to publish if the tag does not match
   the package version.
5. `docs/SDLC.md` documents both workflows and the one-time PyPI setup the owner must do.
6. Nothing is published and nothing is pushed by agents during the sprint.

---

## STORY-FING-30: Per-Phase Sprint Chat Report
**Points:** 4

**As a** project owner reading back over a sprint,
**I want** one document that walks through it phase by phase,
**so that** I can see what happened in each phase without reading the raw chat log.

### Acceptance Criteria
1. `bobp chat-report` produces a single document: the sprint description at the top, then for
   each phase in order its description followed by the chat diagram for that phase's messages.
2. Phases are delimited by marker messages Mouse posts at the start of each phase; messages
   before the first marker appear as a "Planning" section, and close-out activity after the last
   phase is marked the same way.
3. A chat log with no markers still produces a valid report (one undivided section), so older
   projects are unaffected.
4. The full chat text is still archived and `CHAT.md` is still reset, as today.
5. Existing `chat-report` options keep working; the tool's own tests pass.
6. The sprint and Mouse instructions tell Mouse how and when to post markers.
7. Sprint 9's own archive is produced in the new format.

*(This story changes `~/Projects/bob_protocol`, the source of the `bobp` tool. Those edits are
left uncommitted there for the owner's end-of-session bob update.)*

---

## Out of Scope
- Any new fingerprint feature (GLOB/REGEX, report view, event-time timestamps).
- Any work on parked modules beyond keeping them importable and their tests green.
- Renaming public classes (`Warehouse`, `MaskEntry`) — a separate, breaking decision.
- Actually publishing to PyPI or pushing to GitHub — the owner does both.

---

## Technical Architecture Design (Morpheus)

### D1. Repository layout — a uv workspace with two packages
```
pyproject.toml                      # root: "fingerling" (parked pipeline, unpublished) + workspace + tool config
uv.lock                             # one lockfile for the workspace
fingerling/                         # parked modules + thin compatibility shims
packages/fingerprint-sampler/
    pyproject.toml                  # the published package
    README.md                       # self-contained quickstart (shown on PyPI)
    src/fingerprint_sampler/        # tokenizer, aggregators, warehouse, profile, cli, __main__
    tests/                          # its own tests; must pass without `fingerling` importable
    examples/                       # access-log profile + events
tests/                              # parked-module tests + shim tests
```
`fingerling` depends on `fingerprint-sampler` through `[tool.uv.sources]` (`workspace = true`),
so a checkout always uses the in-repo copy. Both packages build with `hatchling`.

### D2. Names
| Thing | Name | Why |
|---|---|---|
| Distribution (PyPI) | `fingerprint-sampler` | `fingerling` and `fingerprint` are taken |
| Import package | `fingerprint_sampler` | matches the distribution; no clash with the `fingerprint` dist |
| Commands | `fingerprint` (and `fingerprint-sampler` as an unambiguous alias) | what a user will type |
| Subcommand | `merge` | leaves room for `show`/`report` later without breaking anyone |

`fingerprint merge -p PROFILE -s SET [EVENTS|-] [-o OUTPUT] [--force-profile]` is today's
`fingerling fingerprint` verbatim. `fingerling fingerprint ...` stays as a delegating alias.
Usage and hint text derive the program name from how the tool was invoked.

### D3. What moves, what stays
- **Moves to `fingerprint_sampler`:** `tokenizer`, `aggregators`, `profile`, `cli`, and from
  `warehouse`: `Warehouse`, `FingerprintRecord`, `fingerprint_id`, the error types, `SET_VERSION`.
- **Stays in `fingerling`:** `TELEMETRY_AGGREGATES` and `build_whitelist` (telemetry / n-gram
  concerns), in `fingerling/warehouse.py`, which also re-exports the moved names.
  `fingerling/tokenizer.py`, `aggregators.py`, `profile.py` become one-line re-export shims, so
  no parked module or parked test needs editing. No class is renamed.
- File formats, IDs and messages are untouched: this is a move, not a rewrite. Trin verifies with
  a set file written before the split.

### D4. Versioning with two packages
One version stream, the published package's: `fingerprint-sampler` starts at **0.1.0** (first
release under this name), bumped by SemVer, tagged `v<version>`. Root `fingerling` is marked
private (`Private :: Do Not Upload`), keeps a static version, and is never tagged or published.

### D5. Toolchain (FING-27)
- `uv` manages the environment and lockfile; installed per-user (`pipx install uv`), never sudo.
- `requires-python = ">=3.10"` in both packages; the 3.10-3.13 matrix runs locally through
  `make test-all` (uv-managed interpreters) and in CI.
- Dev tools live in a `[dependency-groups] dev` group: `ruff`; `rich` stays a `demo` extra.
- `ruff`: default lint rules plus import sorting; `ruff format` applied repo-wide once, as its own
  commit, so later diffs stay readable. Parked code is formatted but not otherwise touched.
- `gitleaks`: `make secrets` (`gitleaks detect --source .`, git-aware, banner kept) and
  `.githooks/pre-commit` (`gitleaks protect --staged`), installed by `make install`.
- Make targets: `install`, `test`, `test-all`, `lint`, `format`, `secrets`, `build`, `check`,
  `run`, `clean`, `distclean`, `help` + existing project targets.

### D6. CI and publishing (FING-29)
- `.github/workflows/ci.yml` — push + pull request; matrix 3.10-3.13; `make install lint test`;
  separate `make secrets` job with full history.
- `.github/workflows/publish.yml` — on tag `v*`; reruns the gates; checks tag == package version;
  `make build`; publishes via PyPI trusted publishing (`id-token: write`, environment `pypi`).
- Neither can be exercised before the owner pushes; both are reviewed statically and their
  commands are the same `make` targets verified locally.

### D7. Per-phase chat report (FING-30, in `~/Projects/bob_protocol`)
- **Marker:** a normal chat message from Mouse whose command is `phase <label>`, e.g.
  `bobp chat "<phase description>" --persona Mouse --cmd "phase 1"`. Labels are free-form
  (`0`, `1`, `close`). No change to `bobp chat` itself.
- **Report:** `CHAT_<MONIKER>.diagram.md` becomes the one document: summary heading, then one
  section per phase — heading, the marker's description, and a diagram rendered from just that
  phase's messages. Messages before the first marker form a `Planning` section.
- **No markers →** output identical to today's (single diagram), so other projects are unaffected.
- `CHAT_<MONIKER>.md` (full text), the CHAT.md reset, `--svg` (one image per phase), `--force`
  and `--combine` keep working.
- Edits are made in the bob_protocol working tree and left uncommitted for the owner.
