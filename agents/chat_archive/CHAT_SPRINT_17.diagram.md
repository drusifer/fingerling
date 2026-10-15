# CHAT_SPRINT_17 — Sprint Archive

## Summary

Sprint 17, Duplicate Protection (Tier 2, 5 pts). Owner asked for protection against re-runs and overlapping sources via a sequence path. FING-49: profile declares sequence: <JSONPath>. FING-50: the set keeps {path, max}; later runs drop events at or below the run-start mark; missing sequence is a line error. Tank's close check found tests/test_e2e.py broken by fix/run-id (already pushed); fixed, lesson recorded. No release (mainline).

---

## Planning

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
```

---

## Phase 1

Phase 1: sequence in the profile and the set (FING-49, D1-D2)

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Neo
    participant Trin
    participant Morpheus
    Note over Neo,Morpheus: 📅 2026-10-14
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 1 done, tests<br/>first: schema top-level<br/>sequence,<br/>Profile.sequence (Path,<br/>problem 'sequence:<br/><reason>'),<br/>FingerprintSet.sequence<br/>{path,…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "UAT phase 1 pass:<br/>FING-49 AC1 optional<br/>path, AC2 invalid<br/>JSONPath located under<br/>sequence, AC3 profile id<br/>unchanged, AC4 example<br/>passes sche…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 1 approved: D1-D2<br/>as designed. @Neo *swe<br/>impl phase-2"
```

---

## Phase 2

Phase 2: drop already-merged events (FING-50, D3-D4)

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
    Note right of Neo: "Phase 2 done, tests<br/>first: _Sequencer<br/>(keep/DROP/None vs run-<br/>start mark), path-change<br/>notice, set mark updated<br/>after the fold, dropped:<br/>sum…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "UAT phase 2 pass: AC1<br/>mark stored, AC2 3,5,6,8<br/>vs 5 merges 6,8 -> max<br/>8, AC3 dropped line<br/>(incl. no earlier mark),<br/>AC4 missing/abc/bool<br/>ids…"
    Morpheus->>Tank: "lead handoff"
    Note right of Morpheus: "Phase 2 approved: D3-D4<br/>as designed, _Sequencer<br/>keeps the fold readable.<br/>All phases reviewed.<br/>@Tank *devops sdlc-check"
```

---

## Close

Close: Tank SDLC check, Oracle groom, Smith user test, retro, launch

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Tank
    participant Neo
    participant Oracle
    participant Smith
    participant All
    participant Cypher
    participant Trin
    participant Morpheus
    participant Mouse
    Note over Tank,Mouse: 📅 2026-10-14
    Tank->>Neo: "devops reject"
    Note right of Tank: "SDLC check FAILED: make<br/>test-fingerling, 3<br/>errors in<br/>tests/test_e2e.py -<br/>upsert(timestamp=)<br/>removed by fix/run-id<br/>(already on<br/>origin/main,…"
    Neo->>Tank: "swe handoff"
    Note right of Neo: "Fix: tests/test_e2e.py<br/>upsert(timestamp=) -><br/>run=. make test 218+50<br/>OK, test-all OK on<br/>3.14+3.15. @Tank *devops<br/>sdlc-check"
    Tank->>Oracle: "devops handoff"
    Note right of Tank: "SDLC re-check passed:<br/>test + test-all green<br/>after the e2e fix, rest<br/>unchanged from the first<br/>pass (from-clean build,<br/>lint, secrets, build,…"
    Oracle->>Smith: "ora handoff"
    Note right of Oracle: "Docs groomed: DECISIONS<br/>entry (sequence dedup,<br/>run-start mark, line<br/>errors), LESSONS: run<br/>full make test when a<br/>signature changes<br/>(fix/run-…"
    Smith->>All: "user approve"
    Note right of Smith: "*user approve. GH<br/>Archive x2: run 2 read<br/>180387, dropped 180387<br/>(sequence <=<br/>34503170055), 0 new/0<br/>updated - AC5 holds.<br/>Summary explains th…"
    Neo->>Cypher: "retro"
    Note right of Neo: "Neo retro: _Sequencer<br/>kept the fold flat,<br/>radon caught _cmd_merge<br/>at C again (history step<br/>extracted). I broke<br/>test_e2e in fix/run-id<br/>by ru…"
    Trin->>Cypher: "retro"
    Note right of Trin: "Trin retro: +10 tests<br/>(208->218 fingerprint),<br/>Tank's from-clean run<br/>caught a pushed<br/>regression the per-<br/>package suite missed.<br/>Backlog items:…"
    Morpheus->>Cypher: "retro"
    Note right of Morpheus: "Morpheus retro: profile-<br/>declared sequence + run-<br/>start mark is simple and<br/>safe. Backlog items: in-<br/>run duplicate detection<br/>if a stream needs…"
    Oracle->>Cypher: "retro"
    Note right of Oracle: "Oracle retro: lesson<br/>recorded for the<br/>fix/run-id miss. Backlog<br/>items: none"
    Mouse->>Cypher: "retro"
    Note right of Mouse: "Mouse retro: 2 phases,<br/>5/5 pts, 1 close fix<br/>cycle (pre-existing<br/>break). Backlog items:<br/>none"
    Smith->>Cypher: "retro"
    Note right of Smith: "Smith retro: dedup is<br/>visible and explained.<br/>Backlog items: confirm<br/>missing-seq policy with<br/>owner"
    Cypher->>Cypher: "retro"
    Note right of Cypher: "Cypher retro: owner<br/>answers up front kept<br/>stories stable. Backlog<br/>items: in-run<br/>duplicates, missing-seq<br/>policy check"
    Cypher->>All: "pm launch"
    Note right of Cypher: "*pm launch sprint-17.<br/>Duplicate protection: a<br/>profile can declare<br/>sequence: $.id, the set<br/>keeps the highest merged<br/>and later runs drop<br/>even…"
```
