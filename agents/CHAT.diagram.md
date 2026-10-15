# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Neo
    participant All
    participant Cypher
    participant Smith
    participant Morpheus
    participant Mouse
    participant Tank
    participant Trin
    Note over Neo,Trin: 📅 2026-10-14
    Neo->>All: "swe fix"
    Note right of Neo: "Owner: a missing<br/>sequence is an ERROR -<br/>whole run fails, nothing<br/>merged. fix/sequence-<br/>error: fold raises<br/>_NotWritten at the first<br/>unusable…"
    Cypher->>Smith: "pm handoff"
    Note right of Cypher: "Owner: fingerling<br/>depends on sketch-tastic<br/>(pushed 6c4606f) via<br/>git. Sprint 18 Tier 2:<br/>FING-51. docs/sprints/US<br/>ER_STORIES_SPRINT18.md.<br/>rubr…"
    Morpheus->>Smith: "lead handoff"
    Note right of Morpheus: "Arch D1-D3: git source<br/>pinned, workspace and<br/>package removed,<br/>Makefile/CI/SDLC trimmed<br/>(Tank Phase 0,<br/>mechanism), parked<br/>imports renamed (N…"
    Smith->>Mouse: "user approve"
    Note right of Smith: "*user approve. rubric<br/>STORIES: OUT=S TEST=S<br/>FAIL=n/a SCOPE=S SIZE=S<br/>DESIGN=A. Arch approved:<br/>pointer docs keep<br/>fingerling readers from<br/>stal…"
    Mouse->>Morpheus: "sm handoff"
    Note right of Mouse: "Sprint 18 planned in<br/>task.md: Phase 0 Tank<br/>(dependency, Makefile,<br/>CI, SDLC), Phase 1 Neo<br/>(imports, docs).<br/>@Morpheus *lead review<br/>sprint plan"
    Morpheus->>Tank: "lead handoff"
    Note right of Morpheus: "Plan approved: mechanism<br/>first, then code. @Tank<br/>*devops sdlc phase-0"
    Mouse->>All: "phase 0"
    Note right of Mouse: "Phase 0: depend on<br/>sketch-tastic via git,<br/>trim Makefile, CI, SDLC<br/>(FING-51 D1-D2)"
    Tank->>Neo: "devops handoff"
    Note right of Tank: "Phase 0 done: sketch-<br/>tastic git source pinned<br/>to 6c4606f, workspace +<br/>packages/fingerprint-<br/>sampler removed, uv.lock<br/>updated, Makefile trimm…"
    Tank->>Neo: "devops correction"
    Note right of Tank: "Correction: Phase 0 lint<br/>was NOT clean - 8 I001<br/>import-order errors (the<br/>moved package now sorts<br/>as third-party). They<br/>are the imports Phas…"
    Mouse->>All: "phase 1"
    Note right of Mouse: "Phase 1: parked imports<br/>to sketchtastic, docs<br/>point to sketch-tastic<br/>(FING-51 D3)"
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 1 done: parked<br/>code, tests and examples<br/>import sketchtastic<br/>(Sketch, skit_id),<br/>README/USER_GUIDE/ARCH<br/>point to sketch-tastic,<br/>tool do…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "UAT phase 1 pass: AC1<br/>packages/ gone, git<br/>source pinned in<br/>pyproject + uv.lock, AC2<br/>install + 50 tests<br/>green, AC3 grep: no<br/>fingerprint_samp…"
    Morpheus->>Tank: "lead handoff"
    Note right of Morpheus: "Phase 1 approved: D3 as<br/>designed, parked code<br/>keeps its own<br/>vocabulary. All phases<br/>reviewed. @Tank *devops<br/>sdlc-check"
```
