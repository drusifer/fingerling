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
    participant Cypher
    participant Smith
    participant Morpheus
    participant Tank
    Note over User,Tank: 📅 2026-10-14
    User->>All: "request"
    Note right of User: "fix then push main"
    Neo->>User: "swe fix"
    Note right of Neo: "README brought up to<br/>date for 0.2.0: what's<br/>new, real set-file<br/>layout, checking API in<br/>the library section,<br/>check_profile and<br/>Modifier expo…"
    User->>All: "request"
    Note right of User: "dont make tags anymore<br/>okay? we'll be doing<br/>mainline development for<br/>a while"
    Mouse->>User: "sm note"
    Note right of Mouse: "Recorded: no tags or<br/>releases during mainline<br/>development. SDLC<br/>section 7, DECISIONS,<br/>task.md and<br/>Mouse/Tank/Cypher state<br/>updated. Existing…"
    Mouse->>User: "sm status"
    Note right of Mouse: "Status: no sprint in<br/>flight. Sprint 11 closed<br/>(8/8 pts). main pushed,<br/>CI green on 3.14/3.15.<br/>Mainline development: no<br/>tags or releases. Que…"
    User->>All: "request"
    Note right of User: "/sprint refactor morph<br/>we need your polymorphic<br/>genius to consolidate<br/>all the validation.<br/>remove the tokenizer<br/>(belongs with the ebpf<br/>relat…"
    Cypher->>Smith: "pm plan sprint"
    Note right of Cypher: "Stories written: FING-38<br/>lint report (Tank),<br/>FING-39 one domain model<br/>+ one validation<br/>mechanism + tokenizer<br/>moved to fingerling,<br/>FING-40 s…"
    Smith->>Morpheus: "user approve"
    Note right of Smith: "Gate 1 approved. rubric<br/>STORIES: OUT=A TEST=S<br/>FAIL=A SCOPE=S SIZE=A<br/>DESIGN=A. FING-39 AC5<br/>(same fingerprints)<br/>protects users through<br/>the re…"
    Morpheus->>Smith: "lead arch"
    Note right of Morpheus: "Architecture D1-D7: Rule<br/>base class (registry,<br/>build from name or<br/>mapping, schema then<br/>check()) shared by<br/>Modifier and Aggregator,<br/>behaviou…"
    Smith->>Mouse: "user approve"
    Note right of Smith: "Gate 2 approved. User-<br/>visible change is small:<br/>fn mapping form, one<br/>command name, same check<br/>output. @Mouse *sm plan<br/>sprint"
    Mouse->>Morpheus: "sm plan"
    Note right of Mouse: "Board in task.md: P0<br/>Tank lint report, P1 Neo<br/>domain model + tokenizer<br/>move, P2 Neo<br/>smells/YAGNI. @Morpheus<br/>*lead review sprint plan"
    Morpheus->>Tank: "lead review"
    Note right of Morpheus: "Plan matches D1-D7,<br/>Phase 1 keeps tests<br/>green by moving the<br/>tokenizer in the same<br/>phase. @Tank *devops<br/>bootstrap quality"
    Mouse->>All: "phase 0"
    Note right of Mouse: "Phase 0: add a report-<br/>only make quality target<br/>(extended ruff, vulture,<br/>radon) and post the<br/>baseline smell list that<br/>drives the refactor."
```
