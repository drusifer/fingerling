<!--
SDLC template — JavaScript / TypeScript (package.json + lockfile). Owned by Tank — see
agents/skills/build-env/SKILL.md. Copy to docs/SDLC.md, replace every {placeholder}, and
swap npm for the manager whose lockfile the repo has (pnpm: `pnpm install --frozen-lockfile`,
yarn: `yarn install --immutable`). Delete this comment.
-->
# {Project} — SDLC

How this project is built, tested, changed and released — the source of truth for change
management across the whole project. **Owned by Tank**; to change anything here,
ask `@Tank *devops sdlc <what and why>` — the mechanism and this document change together.

## 1. Toolchain

| | JavaScript / TypeScript |
|---|---|
| Runtime version | Node {version} — `engines.node` in `package.json` and `.nvmrc` |
| Manifest | `package.json` (tasks in `scripts`) |
| Lockfile | `package-lock.json` (committed) {or: `pnpm-lock.yaml` / `yarn.lock`} |
| Package manager | npm {or: pnpm / yarn — `packageManager` field} |
| Local environment | `node_modules/` (gitignored) |

Other required tools: `make`, Node at the pinned version{, others}.

## 2. Setup

From a clean checkout:

```sh
make install     # npm ci
make test
```

Nothing is installed globally. Run local tools with `npx`, never `npm install -g`.

## 3. Make targets

The Makefile is the only entry point; recipes call `package.json` scripts rather than
repeating their commands.

| Target | Runs | Notes |
|---|---|---|
| `install` | `npm ci` | exact lockfile install; idempotent |
| `test` | `npm run test -- $(ARGS)` | |
| `lint` | `npm run lint` | {eslint / tsc --noEmit} |
| `format` | `npm run format` | {prettier} |
| `build` | `npm run build` | output in `{dist}/` |
| `run` | `npm run {start/dev}` | |
| `clean` | removes `{dist}/`, caches | keeps `node_modules` |
| `distclean` | `clean` + removes `node_modules/` | |
| `help` | lists targets | |

Standard targets deliberately absent: {target — why} / None.

## 4. Dependencies

- **Add a runtime dependency:** `npm install {pkg}`; **dev tool:** `npm install -D {pkg}`.
- **Upgrade / remove:** `npm install {pkg}@{version}` / `npm uninstall {pkg}`.
- **Commit afterwards:** `package.json` **and** `package-lock.json`, together.
- **Who:** Neo adds and bumps dependencies. A different package manager, a Node version change
  or a new language is a mechanism change — Tank's.
- Never hand-edit the lockfile; never mix lockfiles from two package managers.

## 5. Quality gates

| Gate | Target | Required before |
|---|---|---|
| Tests | `make test` | every handoff to Trin; sprint close |
| Lint / types | `make lint` | {when} |
| {Secret scan} | `make {gitleaks}` | {when} |

## 6. Change management

This document is the project's source of truth for how a change gets from request to done.
Where another document, skill or habit disagrees with it, this one wins — and the disagreement
is reported to Tank so one of them gets fixed.

### Change classes

| Class | Examples | Proposed by | Approved by | Must pass | Recorded in |
|---|---|---|---|---|---|
| Routine | feature, fix, refactor, docs, adding a dependency via section 4 | {anyone / Cypher story} | {Morpheus review} | section 5 gates | {task board, commit} |
| Mechanism | toolchain, manifest layout, make targets, gates, CI, this document | anyone, via `@Tank *devops sdlc` | Tank{ + user} | from-clean rebuild + section 5 | this file, `{decisions log}` |
| Release / deploy | version bump, publish, deploy | {who} | {who} | {gates} | {changelog / tag} |
| Emergency | hotfix outside a sprint | {who} | {who — may be after the fact} | `make test` at minimum | {where}, reviewed at next sprint close |

### Flow

1. **Request** — {where changes are requested and how they are sized/planned}.
2. **Branch** — {default branch; branch naming; or "work directly on the default branch"}.
3. **Implement** — through `make` targets only; tests accompany behaviour changes.
4. **Gate** — the section 5 gates pass locally before handoff.
5. **Review** — {who reviews what; what counts as approval}.
6. **Integrate** — {who commits/merges/pushes, and when; commit message convention}.
7. **Record** — {what is updated: task board, decisions log, changelog, user docs}.

### Rules

- {Who may commit, push, tag — e.g. agents commit only when the user asks.}
- {What must never be committed: secrets, the local environment, generated artifacts.}
- **Rollback:** {how a bad change is backed out}.
- **Changing this document:** only Tank edits it; every edit updates the Last verified line.

## 7. Versioning and release

- **Version lives in:** `version` in `package.json`.
- **Bumped:** {when, by whom — e.g. `npm version`}
- **CLI entry points:** `bin` in `package.json`.
- **Artifact:** {bundle in `dist/`, published to ... / deployed to ...} / None — not shipped.

## 8. CI / deploy

{Workflow file, triggers, deploy target} / None — everything runs locally.

CI must run `make install && make test && make lint`, not raw tool commands.

## 9. Known deviations

{e.g. a tool that must be global, a postinstall script, a workspace/monorepo layout} / None.

## 10. Conformance check

Run by Tank at sprint close (`*devops sdlc-check`):

1. `make distclean && make install && make test && make lint` passes.
2. `npm ci` succeeds without modifying the lockfile (`git status` clean afterwards).
3. Every imported package is in `dependencies`/`devDependencies`; only one lockfile exists.
4. Every target in section 3 exists and maps to a `package.json` script; new scripts that
   people are expected to run have a target.
5. No doc or script tells people to install globally or bypass `make`.
6. `node_modules/` is ignored; `.nvmrc` and `engines.node` agree.
7. This sprint's changes followed section 6: right class, right approval, recorded where it says.
8. {Project-specific checks}

---
*Last verified: {YYYY-MM-DD} against {commit or sprint} by Tank.*
