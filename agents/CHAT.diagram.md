# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Oracle
    participant All
    participant User
    participant Bob
    participant Tank
    participant Mouse
    participant Cypher
    participant Smith
    participant Morpheus
    participant Trin
    participant Neo
    Note over Oracle,Neo: 📅 2026-10-12
    Oracle->>All: "ora report"
    Note right of Oracle: "Sprint 8 chat archived<br/>to agents/chat_archive/C<br/>HAT_SPRINT_8.md (also<br/>contains the never-<br/>archived Sprint 1-7 log)<br/>and CHAT.md reset for<br/>the…"
    User->>Bob: "request"
    Note right of User: "Add a new skill for Tank<br/>to set up build envs for<br/>different languages<br/>(Python pyproject.toml,<br/>JavaScript package.json,<br/>etc). Tank does the…"
    Bob->>All: "prompt init"
    Note right of Bob: "Initializing Bob (Prompt<br/>Engineer). Creating a<br/>build-env skill for Tank<br/>per User request:<br/>initial build-<br/>environment setup per<br/>language conv…"
    Bob->>Tank: "prompt handoff"
    Note right of Bob: "New shared skill:<br/>agents/skills/build-env<br/>(triggers *devops<br/>bootstrap / *devops<br/>build-env). Tank does<br/>initial build-env setup<br/>per language…"
    User->>Tank: "request"
    Note right of User: "go for it - run @Tank<br/>*devops bootstrap python<br/>on fingerling"
    Tank->>All: "devops init"
    Note right of Tank: "Initializing Tank<br/>(DevOps). *devops<br/>bootstrap python,<br/>following the build-env<br/>skill: survey first,<br/>because the repo already<br/>has a requireme…"
    Tank->>All: "devops handoff"
    Note right of Tank: "Bootstrap done:<br/>pyproject.toml is the<br/>manifest (deps, demo/dev<br/>extras, 'fingerling'<br/>console script), .venv<br/>is isolated,<br/>requirements.txt is…"
    User->>Bob: "request"
    Note right of User: "OK to the loop edits.<br/>Also add a Tank check at<br/>sprint close so we don't<br/>drift from Tank's SDLC.<br/>Add to Tank's bootstrap<br/>skill that Tank is…"
    Bob->>All: "prompt init"
    Note right of Bob: "Initializing Bob. Wiring<br/>SDLC ownership into the<br/>loops: Tank defines<br/>docs/SDLC.md (build-env<br/>skill), sprint start is<br/>blocked without it, Ta…"
    User->>Bob: "request"
    Note right of User: "Come up with a basic<br/>template for the SDLC<br/>procedures document. We<br/>can have language or<br/>platform specific ones<br/>to make it easy."
    User->>Bob: "request"
    Note right of User: "Tank's SDLC doc will<br/>become the source of<br/>truth for change<br/>management for the<br/>entire project."
    Bob->>Tank: "prompt handoff"
    Note right of Bob: "SDLC wiring done. Tank<br/>owns docs/SDLC.md as the<br/>source of truth for<br/>change management<br/>(AGENTS.md guideline 4).<br/>build-env skill: SDLC<br/>sectio…"
    Tank->>All: "devops init"
    Note right of Tank: "Initializing Tank.<br/>*devops sdlc: writing<br/>docs/SDLC.md from templa<br/>tes/SDLC.python.md. The<br/>environment was verified<br/>from clean earlier<br/>today…"
    Tank->>All: "devops handoff"
    Note right of Tank: "docs/SDLC.md written<br/>from the Python<br/>template: toolchain,<br/>setup, make targets,<br/>dependency process,<br/>gates, change<br/>management, release, CI,<br/>d…"
    User->>Bob: "request"
    Note right of User: "Put the SDLC templates<br/>with the existing ones<br/>(agents/templates) so we<br/>don't bloat the skill."
    Bob->>All: "prompt update"
    Note right of Bob: "Moved the SDLC templates<br/>to agents/templates/ as<br/>_template_SDLC.md, _temp<br/>late_SDLC.python.md, _te<br/>mplate_SDLC.javascript.m<br/>d, matching the ex…"
    User->>All: "decision"
    Note right of User: "Decisions (Q&A): branch<br/>per sprint, agents<br/>branch/commit/merge<br/>(push stays with User),<br/>Conventional Commits,<br/>SemVer bump on change,<br/>ruff +…"
    Tank->>All: "devops sdlc"
    Note right of Tank: "SDLC revised from the<br/>owner's decisions:<br/>sprint-<N> branches,<br/>agents commit and merge<br/>(never push),<br/>Conventional Commits,<br/>SemVer bump + tag…"
    Mouse->>Cypher: "sm start"
    Note right of Mouse: "Sprint 9 start. Stage 0<br/>SDLC gate: docs/SDLC.md<br/>present - pass. Per SDLC<br/>section 6, created<br/>branch sprint-9 from a<br/>clean main (baseline<br/>0b1…"
    Cypher->>Smith: "pm handoff"
    Note right of Cypher: "Sprint 9 stories<br/>drafted: docs/USER_STORI<br/>ES_SPRINT9.md, 18 pts.<br/>FING-27 reproducible<br/>gated env (uv, 3.10+,<br/>ruff, gitleaks), FING-28<br/>fingerp…"
    Smith->>Morpheus: "user approve"
    Note right of Smith: "*user approve Gate 1.<br/>Stories are outcome-<br/>first and testable.<br/>Added FING-28 AC9<br/>(package README<br/>quickstart must work<br/>pasted into a fresh en…"
    Morpheus->>Smith: "lead handoff"
    Note right of Morpheus: "Sprint 9 arch D1-D7 in d<br/>ocs/USER_STORIES_SPRINT9<br/>.md. uv workspace, 2<br/>packages: fingerling<br/>(parked, private) +<br/>packages/fingerprint-<br/>sampler…"
    Smith->>Mouse: "user approve"
    Note right of Smith: "*user approve Gate 2.<br/>'fingerprint merge'<br/>reads as what it does<br/>and leaves room for<br/>show/report, keeping<br/>'fingerling fingerprint'<br/>as an ali…"
    Mouse->>Morpheus: "sm handoff"
    Note right of Mouse: "Sprint 9 planned in<br/>task.md: Phase 0 Tank<br/>build env (FING-27)<br/>first per the new Phase<br/>0 rule, Phase 1 Neo<br/>package split (FING-28),<br/>Phase 2…"
    Morpheus->>Tank: "lead handoff"
    Note right of Morpheus: "Sprint plan approved:<br/>order follows the<br/>dependency chain (env -><br/>split -> CI), each phase<br/>leaves lint+test green,<br/>and Phase 3 is<br/>independen…"
    Mouse->>All: "phase 0"
    Note right of Mouse: "Build environment<br/>(STORY-FING-27): move to<br/>uv with a committed<br/>lockfile, support Python<br/>3.10-3.13, add ruff<br/>lint/format and gitleaks<br/>as gat…"
    Tank->>All: "devops init"
    Note right of Tank: "Initializing Tank. Phase<br/>0 (STORY-FING-27) per<br/>build-env skill: survey<br/>done at bootstrap,<br/>mechanism change is pip<br/>-> uv. Installing uv<br/>per-…"
    Tank->>Trin: "devops handoff"
    Note right of Tank: "Phase 0 done (FING-27):<br/>uv + committed uv.lock,<br/>requires-python >=3.10,<br/>ruff (rules pinned<br/>E4/E7/E9/F/I) with make<br/>lint/format, gitleaks<br/>vi…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "UAT phase-0 PASSED. AC1<br/>uv.lock committed,<br/>missing uv prints the<br/>pipx hint (checked with<br/>a stripped PATH). AC2<br/>178/178 on 3.10, 3.11,<br/>3.12,…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 0 review PASSED.<br/>Pinning the ruff rule<br/>list is right: a tool<br/>upgrade must not move<br/>the gate. Format pass<br/>isolated in its own<br/>commit,…"
    Mouse->>All: "phase 1"
    Note right of Mouse: "Package split (STORY-<br/>FING-28): move the<br/>fingerprint tool into<br/>its own installable<br/>package,<br/>packages/fingerprint-<br/>sampler, with the<br/>command '…"
    Neo->>All: "swe init"
    Note right of Neo: "*swe impl phase-1: pure<br/>move into<br/>packages/fingerprint-<br/>sampler as a uv<br/>workspace member, shims<br/>in fingerling, no logic<br/>edits. Saving a pre-…"
```
