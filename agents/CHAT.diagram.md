# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant User
    participant Tank
    participant All
    participant Oracle
    participant Bob
    Note over User,Bob: 📅 2026-10-13
    User->>Tank: "request"
    Note right of User: "Fix the Makefile now<br/>that we have bobp and<br/>the make skill: only one<br/>Makefile, no more<br/>Makefile.prj."
    Tank->>All: "devops init"
    Note right of Tank: "Initializing Tank.<br/>Makefile.prj was already<br/>deleted in Sprint 9, so<br/>the single-Makefile<br/>state exists, what is<br/>left is bob tooling<br/>still liv…"
    User->>Tank: "request"
    Note right of User: "The tldr tool should use<br/>the system-installed<br/>via."
    Tank->>All: "devops handoff"
    Note right of Tank: "Single Makefile<br/>confirmed and cleaned:<br/>removed the chat and<br/>tldr targets (bobp chat<br/>/ bobp tldr replace<br/>them, make chat called a<br/>stale copy…"
    User->>Oracle: "request"
    Note right of User: "/oracle groom docs"
    Oracle->>All: "ora init"
    Note right of Oracle: "Initializing Oracle.<br/>*ora groom docs:<br/>auditing the<br/>documentation tree after<br/>two sprints that moved a<br/>lot (package split,<br/>SDLC, uv) - lookin…"
    Oracle->>All: "ora groom"
    Note right of Oracle: "Docs groomed. Sprint<br/>stories now live in<br/>docs/sprints/ (9 files,<br/>references updated) so<br/>docs/ holds 6 core<br/>documents. README<br/>carries a full…"
    User->>Bob: "request"
    Note right of User: "Remove the redundant<br/>agents/tools/*.py now<br/>that we have bobp, and<br/>update the bob_protocol<br/>setup tool to do this on<br/>future upgrades."
    Bob->>All: "prompt update"
    Note right of Bob: "Initializing Bob.<br/>Removed the nine<br/>superseded<br/>agents/tools/*.py copies<br/>by running the updated<br/>bobp setup-agent-links<br/>here (it now does this…"
```
