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
    Note over User,Neo: 📅 2026-10-14
    User->>All: "request"
    Note right of User: "Owner (/sprint):<br/>lightweight history.<br/>Each merge also writes a<br/>file with just that<br/>run's data in a subdir,<br/>besides merging into the<br/>primary…"
    Cypher->>Smith: "pm handoff"
    Note right of Cypher: "Sprint 16 (Run History,<br/>Tier 2, 3 pts): FING-48<br/>a run file per merge in<br/><set>.history/, run:<br/>header, exit 3 if<br/>history fails.<br/>docs/sprints/…"
    Morpheus->>Smith: "lead handoff"
    Note right of Morpheus: "Arch D1-D5: run = second<br/>FingerprintSet fed the<br/>same events/timestamps,<br/>FingerprintSet.run<br/>header written by save,<br/>ignored by load,<br/>_histor…"
    Smith->>Cypher: "user reject"
    Note right of Smith: "*user reject REASON: AC8<br/>does not say which exit<br/>wins when lines were<br/>skipped (1) AND history<br/>failed (3). FIX: state 3<br/>takes precedence, si…"
    Cypher->>Smith: "pm handoff"
    Note right of Cypher: "Revised AC8: exit 3<br/>takes precedence over 1.<br/>@Smith *user review<br/>sprint-16"
    Smith->>Mouse: "user approve"
    Note right of Smith: "*user approve. rubric<br/>STORIES: OUT=S TEST=S<br/>FAIL=S SCOPE=S SIZE=A<br/>DESIGN=A. Arch approved:<br/>run files readable by<br/>show with no new<br/>command,…"
    Mouse->>Morpheus: "sm handoff"
    Note right of Mouse: "Sprint 16 planned in<br/>task.md: Phase 1 run set<br/>+ header (D1-D2), Phase<br/>2 history files, exit 3,<br/>docs (D3-D5), close with<br/>Tank sdlc-check. @M…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Plan approved: the data<br/>model lands before the<br/>file layout. @Neo *swe<br/>impl phase-1"
    Mouse->>All: "phase 1"
    Note right of Mouse: "Phase 1: the run as a<br/>set - run header and<br/>per-run fold (FING-48<br/>D1-D2)"
```
