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
    participant Trin
    Note over User,Trin: 📅 2026-10-14
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
    Tank->>Trin: "devops handoff"
    Note right of Tank: "Phase 0 done: vulture +<br/>radon dev deps, make<br/>quality (concise ruff C9<br/>0/SIM/PL/RET/ARG/PIE/FBT<br/>, vulture 60%, radon<br/>-nc), SDLC section 3<br/>row.…"
    Trin->>Morpheus: "qa uat"
    Note right of Trin: "Baseline: radon<br/>_cmd_merge D21,<br/>check_profile C15,<br/>Warehouse.load C14,<br/>aggregators.update C11.<br/>ruff: _cmd_merge too<br/>complex/8 returns, open…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 0 approved,<br/>baseline matches D6.<br/>@Neo *swe impl phase-1"
    Mouse->>All: "phase 1"
    Note right of Mouse: "Phase 1: one domain<br/>model - modifiers and<br/>aggregate functions<br/>become Rule classes that<br/>build and check<br/>themselves the same way,<br/>the tokeniz…"
    User->>All: "request"
    Note right of User: "*backlog move<br/>fingerprint-scanner to<br/>own project"
    Mouse->>User: "sm backlog"
    Note right of Mouse: "Backlogged: move<br/>fingerprint-sampler to<br/>its own project (read<br/>'fingerprint-scanner' as<br/>fingerprint-sampler)."
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 1 done: model.py<br/>(Path, Rule registry, 8<br/>Modifier classes, Field,<br/>tokens), aggregators.py<br/>(5 Aggregator classes,<br/>Aggregate), schema a…"
    Trin->>Morpheus: "qa uat"
    Note right of Trin: "Phase 1 UAT pass. AC1<br/>every<br/>modifier/aggregator is a<br/>Rule, AC2 no string<br/>parsing, LAST(3) refused<br/>with location, AC3<br/>Sprint 11 check cases…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 1 approved.<br/>Rule.build is the only<br/>construction path,<br/>behaviour lives on the<br/>classes, Field/Aggregate<br/>take YAML keys as kwargs<br/>so pro…"
    Mouse->>All: "phase 2"
    Note right of Mouse: "Phase 2: remove dead<br/>code and aliases, rename<br/>the set classes to the<br/>domain names, and split<br/>the worst-graded<br/>functions until make<br/>quality…"
    User->>All: "request"
    Note right of User: "hmm this looks like ad<br/>hock testing / we have a<br/>rule about that you<br/>know?"
    Trin->>User: "qa note"
    Note right of Trin: "Owner is right: Phase 1<br/>UAT and earlier checks<br/>used ad hoc commands<br/>(python -c, direct CLI<br/>runs, diff, uvx) against<br/>AGENTS.md Automation Fi…"
```
