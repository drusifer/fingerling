# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Mouse
    participant All
    Note over Mouse,All: 📅 2026-10-13
    Mouse->>All: "sm handoff"
    Note right of Mouse: "Shutdown hand-off. No<br/>sprint in flight,<br/>Sprints 8-10 closed.<br/>fingerling main is<br/>pushed, tag v0.1.0 is<br/>local only because<br/>pushing it publish…"
```
