# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Mouse
    participant All
    participant Bob
    Note over Mouse,Bob: 📅 2026-10-13
    Mouse->>All: "sm handoff"
    Note right of Mouse: "Sprint 10 closed, its<br/>record is in<br/>CHAT_SPRINT_10<br/>(planning, phases 1-4)<br/>and CHAT_SPRINT_10_CLOSE<br/>(the close, posted<br/>late). No sprint in fl…"
    Bob->>All: "prompt update"
    Note right of Bob: "Removed the three legacy<br/>state templates<br/>(_template_context,<br/>_template_current_task,<br/>_template_next_steps):<br/>they belong to the<br/>retired thre…"
    Bob->>All: "prompt update"
    Note right of Bob: "agents/AGENTS.md synced<br/>with the upstream copy,<br/>which now carries the<br/>SDLC guideline.<br/>Fingerling was behind<br/>upstream here: it still<br/>describ…"
```
