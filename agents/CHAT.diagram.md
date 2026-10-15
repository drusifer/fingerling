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
    Note over Neo,Tank: 📅 2026-10-14
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
```
