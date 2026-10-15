# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Neo
    participant All
    Note over Neo,All: 📅 2026-10-14
    Neo->>All: "swe fix"
    Note right of Neo: "Owner: built-in samples<br/>1 first + 1 last (was 3<br/>each). Done on fix/one-<br/>sample: builtin.yaml,<br/>test, README/USER_GUIDE,<br/>DECISIONS. GH Archive…"
    Neo->>All: "swe fix"
    Note right of Neo: "Owner *fix: run ids<br/>YYMMDD-SEQ (UTC date +<br/>per-set sequence). Set<br/>stores last_run,<br/>first_seen/last_seen =<br/>first/last run id,<br/>envelope {meta…"
```
