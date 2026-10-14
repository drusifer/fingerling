# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant User
    participant All
    participant Neo
    participant Trin
    participant Morpheus
    participant Smith
    Note over User,Smith: 📅 2026-10-14
    User->>All: "request"
    Note right of User: "/bloop time for some<br/>meta data for the<br/>profiles (aka freebies).<br/>these can be optional if<br/>there is a reasonable<br/>default. consolidate to<br/>diff…"
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Built-in metadata done<br/>(owner: count is per<br/>fingerprint): count,<br/>first_seen/last_seen,<br/>first/last 3 events with<br/>seen time, profile<br/>samples:…"
    Trin->>Morpheus: "qa uat"
    Note right of Trin: "UAT pass by make<br/>targets: lint, test (156<br/>+ 50), smoke (README<br/>examples run). New<br/>tests: first/last<br/>ordering, samples 1 and<br/>0, copies not a…"
    Morpheus->>Smith: "lead handoff"
    Note right of Morpheus: "Approved. Built-in<br/>metadata lives on<br/>Fingerprint, profile<br/>stuff stays in<br/>aggregates, one setting,<br/>no new rule types.<br/>@Smith *user test"
    Smith->>User: "user approve"
    Note right of Smith: "Approved. The set file<br/>now reads top to bottom:<br/>what it is, how often,<br/>when, your stats, real<br/>examples. samples: 0 is<br/>the off switch. Docs…"
    User->>All: "request"
    Note right of User: "try this, wrap the jsonl<br/>in an outer object that<br/>has the jsonl data in<br/>one and metadata in the<br/>other. we can inject<br/>fields like current tim…"
```
