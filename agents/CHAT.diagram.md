# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Mouse
    participant All
    participant User
    participant Cypher
    participant Smith
    participant Morpheus
    participant Bob
    Note over Mouse,Bob: 📅 2026-10-13
    Mouse->>All: "sm handoff"
    Note right of Mouse: "Session closed. No<br/>sprint in flight. main =<br/>Sprint 9 + four merged<br/>fix/ branches, tagged<br/>v0.1.0, ahead of origin,<br/>nothing pushed. Waiting<br/>o…"
    User->>Cypher: "request"
    Note right of User: "/sprint complete<br/>artifacts rubrics sprint"
    Mouse->>Cypher: "sm start"
    Note right of Mouse: "Sprint 10 start. Stage 0<br/>SDLC gate: docs/SDLC.md<br/>present - pass. Branch<br/>sprint-10 created from<br/>clean main. Scope: the<br/>queued artifact-rubri…"
    Cypher->>Smith: "pm handoff"
    Note right of Cypher: "Sprint 10 stories<br/>drafted: docs/sprints/US<br/>ER_STORIES_SPRINT10.md,<br/>10 pts. FING-31 artifact<br/>inventory + rubric<br/>format, FING-32 stories<br/>templ…"
    Smith->>Morpheus: "user approve"
    Note right of Smith: "*user approve Gate 1.<br/>Stories state outcomes<br/>and each AC is<br/>checkable. Added FING-31<br/>AC6: a verdict must fit<br/>one 512-char chat<br/>message, or…"
    Morpheus->>Smith: "lead handoff"
    Note right of Morpheus: "Sprint 10 arch D1-D7<br/>written. agents/template<br/>s/ARTIFACTS.md holds the<br/>inventory and rubric<br/>format, rubrics are an<br/>appendix between<br/>RUBRIC-S…"
    Smith->>Mouse: "user approve"
    Note right of Smith: "*user approve Gate 2.<br/>Criterion codes make the<br/>verdict line scannable,<br/>observable level<br/>descriptions keep it<br/>from becoming taste.<br/>Separatin…"
    Mouse->>Morpheus: "sm handoff"
    Note right of Mouse: "Sprint 10 planned in<br/>task.md: 4 phases, one<br/>story each - 1<br/>inventory+format, 2<br/>stories template+rubric,<br/>3 SDLC and lesson<br/>rubrics, 4 calibr…"
    Morpheus->>Bob: "lead handoff"
    Note right of Morpheus: "Sprint plan approved:<br/>order matches<br/>dependencies and each<br/>phase is one reviewable<br/>document set. Phase 1<br/>ready. @Bob *prompt impl<br/>phase-1"
    Mouse->>All: "phase 1"
    Note right of Mouse: "Inventory and rubric<br/>format (STORY-FING-31):<br/>one document listing<br/>every artifact agents<br/>are expected to produce,<br/>and defining how a<br/>rubric…"
```
