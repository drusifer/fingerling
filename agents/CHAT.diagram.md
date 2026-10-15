# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Neo
    participant All
    participant User
    participant Cypher
    participant Smith
    participant Morpheus
    participant Mouse
    Note over Neo,Mouse: 📅 2026-10-14
    Neo->>All: "swe fix"
    Note right of Neo: "Owner: built-in samples<br/>1 first + 1 last (was 3<br/>each). Done on fix/one-<br/>sample: builtin.yaml,<br/>test, README/USER_GUIDE,<br/>DECISIONS. GH Archive…"
    Neo->>All: "swe fix"
    Note right of Neo: "Owner *fix: run ids<br/>YYMMDD-SEQ (UTC date +<br/>per-set sequence). Set<br/>stores last_run,<br/>first_seen/last_seen =<br/>first/last run id,<br/>envelope {meta…"
    User->>All: "request"
    Note right of User: "Owner: duplicate<br/>protection via a<br/>sequence path, drop<br/>events <= captured max.<br/>Clarified: in the<br/>profile, compare to the<br/>mark at run start,…"
    Cypher->>Smith: "pm handoff"
    Note right of Cypher: "Sprint 17 (Duplicate<br/>Protection, Tier 2, 5<br/>pts): FING-49 sequence<br/>in profile, FING-50 drop<br/><= stored max, report,<br/>history header.<br/>docs/spri…"
    Morpheus->>Smith: "lead handoff"
    Note right of Morpheus: "Arch D1-D4:<br/>Profile.sequence Path<br/>(schema top-level, id<br/>unchanged),<br/>FingerprintSet.sequence<br/>{path,max} saved/loaded,<br/>_Sequencer in _fold_st…"
    Smith->>Mouse: "user approve"
    Note right of Smith: "*user approve. rubric<br/>STORIES: OUT=S TEST=S<br/>FAIL=S SCOPE=S SIZE=S<br/>DESIGN=A. Arch approved:<br/>the dropped line states<br/>the mark, so a user<br/>sees…"
    Mouse->>Morpheus: "sm handoff"
    Note right of Mouse: "Sprint 17 planned in<br/>task.md: Phase 1 FING-49<br/>+ set mark storage,<br/>Phase 2 FING-50<br/>filtering and reporting,<br/>close with Tank sdlc-<br/>check. @Mor…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Plan approved. @Neo *swe<br/>impl phase-1"
    Mouse->>All: "phase 1"
    Note right of Mouse: "Phase 1: sequence in the<br/>profile and the set<br/>(FING-49, D1-D2)"
```
