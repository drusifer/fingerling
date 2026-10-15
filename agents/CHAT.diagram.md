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
    participant Trin
    participant Tank
    Note over Neo,Tank: 📅 2026-10-14
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
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 1 done, tests<br/>first: schema top-level<br/>sequence,<br/>Profile.sequence (Path,<br/>problem 'sequence:<br/><reason>'),<br/>FingerprintSet.sequence<br/>{path,…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "UAT phase 1 pass:<br/>FING-49 AC1 optional<br/>path, AC2 invalid<br/>JSONPath located under<br/>sequence, AC3 profile id<br/>unchanged, AC4 example<br/>passes sche…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 1 approved: D1-D2<br/>as designed. @Neo *swe<br/>impl phase-2"
    Mouse->>All: "phase 2"
    Note right of Mouse: "Phase 2: drop already-<br/>merged events (FING-50,<br/>D3-D4)"
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 2 done, tests<br/>first: _Sequencer<br/>(keep/DROP/None vs run-<br/>start mark), path-change<br/>notice, set mark updated<br/>after the fold, dropped:<br/>sum…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "UAT phase 2 pass: AC1<br/>mark stored, AC2 3,5,6,8<br/>vs 5 merges 6,8 -> max<br/>8, AC3 dropped line<br/>(incl. no earlier mark),<br/>AC4 missing/abc/bool<br/>ids…"
    Morpheus->>Tank: "lead handoff"
    Note right of Morpheus: "Phase 2 approved: D3-D4<br/>as designed, _Sequencer<br/>keeps the fold readable.<br/>All phases reviewed.<br/>@Tank *devops sdlc-check"
```
