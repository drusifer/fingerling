# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant User
    participant All
    participant Neo
    participant Mouse
    Note over User,Mouse: 📅 2026-10-14
    User->>All: "request"
    Note right of User: "fix then push main"
    Neo->>User: "swe fix"
    Note right of Neo: "README brought up to<br/>date for 0.2.0: what's<br/>new, real set-file<br/>layout, checking API in<br/>the library section,<br/>check_profile and<br/>Modifier expo…"
    User->>All: "request"
    Note right of User: "dont make tags anymore<br/>okay? we'll be doing<br/>mainline development for<br/>a while"
    Mouse->>User: "sm note"
    Note right of Mouse: "Recorded: no tags or<br/>releases during mainline<br/>development. SDLC<br/>section 7, DECISIONS,<br/>task.md and<br/>Mouse/Tank/Cypher state<br/>updated. Existing…"
```
