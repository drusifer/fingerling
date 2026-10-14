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
    Note right of User: "Owner (/sprint): add %s<br/>for aggregate values.<br/>Clarified: stored in the<br/>set file AND shown by<br/>fingerprint show, for<br/>SUM and COUNT (incl.<br/>bui…"
    Cypher->>Smith: "pm handoff"
    Note right of Cypher: "Sprint 15 (Shares of the<br/>Set, Tier 2, 5 pts):<br/>FING-46 share section in<br/>the set file for<br/>SUM/COUNT, FING-47 show<br/>prints values + %<br/>columns.…"
    Morpheus->>Smith: "lead handoff"
    Note right of Morpheus: "Arch D1-D5:<br/>Fingerprint.share<br/>(derived, overwritten on<br/>save),<br/>FingerprintSet.save<br/>computes SUM/COUNT<br/>shares for meta +<br/>profile aggregates v…"
    Smith->>Mouse: "user approve"
    Note right of Smith: "*user approve. rubric<br/>STORIES: OUT=S TEST=S<br/>FAIL=A SCOPE=S SIZE=S<br/>DESIGN=A. Arch approved:<br/>share mirrors the layout<br/>users already read, 'CO…"
    Mouse->>Morpheus: "sm handoff"
    Note right of Mouse: "Sprint 15 planned in<br/>task.md: Phase 1 FING-46<br/>(stored shares), Phase 2<br/>FING-47 (show columns),<br/>close with Tank sdlc-<br/>check. @Morpheus *lead…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Plan approved: storage<br/>before display, so Phase<br/>2 reads real shares.<br/>@Neo *swe impl phase-1"
    Mouse->>All: "phase 1"
    Note right of Mouse: "Phase 1: shares of SUM<br/>and COUNT stored in the<br/>set file (FING-46)"
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 1 done, tests<br/>first:<br/>Fingerprint.share,<br/>FingerprintSet.save<br/>recomputes SUM/COUNT<br/>shares for meta +<br/>profile aggregates via<br/>Aggregate.v…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "UAT phase 1 pass: AC1-2<br/>exact 66.67/33.33 and<br/>SUM 40/60, MAX unshared,<br/>single-fn COUNT direct,<br/>AC3 merge into existing<br/>set recomputes (25/7…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 1 approved: D1-D3<br/>as designed, _store<br/>promoted to store() and<br/>value() added so share<br/>and fold share one<br/>layout rule. @Neo *swe<br/>impl p…"
    Mouse->>All: "phase 2"
    Note right of Mouse: "Phase 2: shares in<br/>fingerprint show<br/>(FING-47)"
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 2 done, tests<br/>first: show adds COUNT %<br/>after COUNT and a value<br/>+ % column per shared<br/>SUM/COUNT (key or<br/>key.FN), read from<br/>stored shar…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "UAT phase 2 pass: AC1<br/>exact column order<br/>(COUNT %, size.SUM,<br/>size.SUM %, n, n %,<br/>tokens last), AC2 66.7<br/>one decimal, '-' for<br/>missing, AC3 c…"
    Morpheus->>Tank: "lead handoff"
    Note right of Morpheus: "Phase 2 approved: D4 as<br/>designed, show<br/>recomputes nothing,<br/>helpers small and named.<br/>All phases reviewed.<br/>@Tank *devops sdlc-check"
```
