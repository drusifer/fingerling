# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant User
    participant All
    participant Cypher
    participant Smith
    participant Morpheus
    participant Mouse
    participant Neo
    participant Trin
    participant Tank
    Note over User,Tank: 📅 2026-10-14
    User->>All: "request"
    Note right of User: "Owner:<br/>SUM(SIZE(payload)) style<br/>weighted aggregates,<br/>agreed design is op:<br/>SIZE on the aggregate,<br/>not a SUM parameter.<br/>Sprint 14."
    Cypher->>Smith: "pm handoff"
    Note right of Cypher: "Sprint 14 (Weighted<br/>Aggregates, Tier 2, 2<br/>pts): FING-45 op: SIZE<br/>on aggregates. docs/spri<br/>nts/USER_STORIES_SPRINT1<br/>4.md. Self-check rubric<br/>ST…"
    Morpheus->>Smith: "lead handoff"
    Note right of Morpheus: "Arch D1-D4: Op rule<br/>family in<br/>aggregators.py, Size =<br/>UTF-8 bytes (str) or<br/>compact JSON bytes,<br/>schema $defs.op enum +<br/>not(op and type), Aggr…"
    Smith->>Mouse: "user approve"
    Note right of Smith: "*user approve. rubric<br/>STORIES: OUT=S TEST=S<br/>FAIL=A SCOPE=S SIZE=A<br/>DESIGN=A. Arch approved:<br/>op reads as<br/>SUM(SIZE(x)), worked<br/>example in AC1…"
    Mouse->>Morpheus: "sm handoff"
    Note right of Mouse: "Sprint 14 planned in<br/>task.md: one phase<br/>(FING-45), close-out<br/>with Tank sdlc-check.<br/>@Morpheus *lead review<br/>sprint plan"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Plan approved. Per<br/>Smith: the op+type<br/>message comes from a<br/>description on the<br/>schema's not-subschema,<br/>so it stays schema-<br/>driven. @Neo *swe…"
    Mouse->>All: "phase 1"
    Note right of Mouse: "Phase 1: op: SIZE on<br/>aggregates (FING-45)"
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 1 done, tests<br/>first: Op family + Size<br/>in aggregators.py,<br/>schema $defs.op,<br/>aggregate.op,<br/>not(op+type) with a<br/>description that<br/>schema_e…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "UAT phase 1 pass: AC1<br/>héllo+{a:1} = SUM 13/MAX<br/>7/AVG 6.5, AC2 LAST<br/>keeps sizes, AC3 null=4,<br/>absent adds 0 and no<br/>skip, AC4 BOGUS message<br/>ex…"
    Morpheus->>Tank: "lead handoff"
    Note right of Morpheus: "Phase 1 approved: D1-D4<br/>as designed. The not-<br/>description hook in<br/>schema_errors is<br/>generic, so future<br/>cross-key rules get<br/>readable messages…"
```
