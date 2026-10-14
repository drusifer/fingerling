# CHAT_SPRINT_16 — Sprint Archive

## Summary

Sprint 16, Run History (Tier 2, 3 pts, 0 fix cycles). Owner asked for lightweight history; clarified: <set>.history/ beside the set, always on, -o kept without history. FING-48: each merge also writes that run's own set with a run: header to <set>.history/<UTC start>.yaml; same-second runs get _2 (UAT caught -2 sorting first); exit 3 if the history write fails. Findings: run files ~6 MB on GH Archive, merge ~1.7x slower. No release (mainline).

---

## Planning

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
```

---

## Phase 1

Phase 1: the run as a set - run header and per-run fold (FING-48 D1-D2)

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Neo
    participant Trin
    participant Morpheus
    Note over Neo,Morpheus: 📅 2026-10-14
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 1 done, tests<br/>first:<br/>FingerprintSet.run<br/>header saved between<br/>profile_id and<br/>fingerprints, never<br/>loaded, _fold_stream<br/>feeds the primar…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "UAT phase 1 pass: header<br/>position and content,<br/>absent when unset, load<br/>ignores it (run None,<br/>records intact), all CLI<br/>tests unchanged so th…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 1 approved: D1-D2<br/>as designed, shared<br/>timestamp keeps run and<br/>set meta consistent.<br/>@Neo *swe impl phase-2"
```

---

## Phase 2

Phase 2: history files in <set>.history/, exit 3, docs (FING-48 D3-D5)

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Neo
    participant Trin
    participant Morpheus
    participant Tank
    Note over Neo,Tank: 📅 2026-10-14
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 2 done, tests<br/>first: _history_path (<s<br/>et>.history/<UTC>.yaml,<br/>makedirs),<br/>_write_history with run<br/>header after the set is<br/>saved, 'hist…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "UAT phase 2 pass after<br/>one design catch:<br/>collision suffix -2<br/>sorted BEFORE the base<br/>name ('-' < '.'),<br/>breaking run order, now<br/>_2 (AC4 revis…"
    Morpheus->>Tank: "lead handoff"
    Note right of Morpheus: "Phase 2 approved: D3-D5<br/>as designed with the _N<br/>suffix, history after<br/>the set keeps the<br/>primary set<br/>authoritative. All<br/>phases reviewed. @Ta…"
```

---

## Close

Close: Tank SDLC check, Oracle groom, Smith user test, retro, launch

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Tank
    participant Oracle
    participant Smith
    participant All
    participant Neo
    participant Cypher
    participant Trin
    participant Morpheus
    participant Mouse
    Note over Tank,Mouse: 📅 2026-10-14
    Tank->>Oracle: "devops handoff"
    Note right of Tank: "SDLC check passed: from-<br/>clean distclean/install/<br/>lint/test/secrets/build,<br/>test-all 3.14+3.15,<br/>smoke green, lock<br/>current, venv isolated,<br/>hook…"
    Oracle->>Smith: "ora handoff"
    Note right of Oracle: "Docs groomed: DECISIONS<br/>entry (history layout,<br/>always on, -o none, _N<br/>suffix and why, exit 3),<br/>ARCH table.<br/>README/USER_GUIDE done<br/>in phase.…"
    Smith->>All: "user approve"
    Note right of Smith: "*user approve. GH<br/>Archive x2 via make: two<br/>run files, run 2 shows<br/>82137 for the top<br/>fingerprint (set has<br/>2x), header self-<br/>explains, show re…"
    Neo->>Cypher: "retro"
    Note right of Neo: "Neo retro: run set<br/>reuses FingerprintSet<br/>whole, simple but<br/>doubles fold cost.<br/>Backlog items: fold once<br/>and derive the run (or<br/>skip sample c…"
    Trin->>Cypher: "retro"
    Note right of Trin: "Trin retro: +10 tests<br/>(194->204), the regex<br/>test on names caught<br/>'-2' sorting before the<br/>base name. Smoke made<br/>run-time tolerant.<br/>Backlog i…"
    Morpheus->>Cypher: "retro"
    Note right of Morpheus: "Morpheus retro: run file<br/>= set file kept history<br/>readerless, cost is size<br/>and time. Backlog items:<br/>slimmer run files (e.g.<br/>no sample record…"
    Oracle->>Cypher: "retro"
    Note right of Oracle: "Oracle retro: decision<br/>records the rejected -2<br/>suffix. Backlog items:<br/>none"
    Mouse->>Cypher: "retro"
    Note right of Mouse: "Mouse retro: 2 phases,<br/>3/3 pts, 1 Gate-1<br/>revision, 1 in-phase<br/>design fix, 0 fix<br/>cycles. Backlog items:<br/>none"
    Smith->>Cypher: "retro"
    Note right of Smith: "Smith retro: history<br/>works and needs no new<br/>tool, weight and speed<br/>are the open UX<br/>questions. Backlog<br/>items: run file size,<br/>merge speed"
    Cypher->>Cypher: "retro"
    Note right of Cypher: "Cypher retro: asking the<br/>owner first again saved<br/>rework. Backlog items:<br/>history size/speed<br/>(owner decision), -o<br/>revisit, show<br/>--sort/--top…"
    Cypher->>All: "pm launch"
    Note right of Cypher: "*pm launch sprint-16.<br/>Run history: every merge<br/>also writes its own<br/>fingerprints with a run:<br/>header to <set>.history/<br/><UTC>.yaml, show reads…"
```
