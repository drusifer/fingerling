# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Mouse
    participant All
    participant User
    participant Neo
    participant Trin
    participant Morpheus
    participant Smith
    participant Cypher
    participant Tank
    Note over Mouse,Tank: 📅 2026-10-13
    Mouse->>All: "sm handoff"
    Note right of Mouse: "Shutdown hand-off. No<br/>sprint in flight,<br/>Sprints 8-10 closed.<br/>fingerling main is<br/>pushed, tag v0.1.0 is<br/>local only because<br/>pushing it publish…"
    User->>All: "request"
    Note right of User: "/bob-protocol init<br/>/mouse status report"
    Mouse->>User: "sm status"
    Note right of Mouse: "Status: no sprint in<br/>flight. Sprints 8-10<br/>closed (16, 18, 10 pts,<br/>1 fix cycle total). main<br/>is level with origin. CI<br/>checked: all 3 runs fro…"
    User->>All: "request"
    Note right of User: "/bloop GLOB/REGX/REGSUB"
    Mouse->>Neo: "sm handoff"
    Note right of Mouse: "Resolved: /bloop<br/>GLOB/REGX/REGSUB = *impl<br/>of three new tokenizer<br/>modifiers (backlog item,<br/>spec FR-MOD-01). One<br/>concrete change, so no<br/>sprin…"
    Neo->>Trin: "swe handoff"
    Note right of Neo: "GLOB(pattern),<br/>REGEX(pattern),<br/>REGSUB(pattern,<br/>replacement) added to<br/>the tokenizer. Arguments<br/>may now be quoted so a<br/>pattern can hold comma…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "UAT pass. Ran the CLI on<br/>the access-log example<br/>with all three<br/>modifiers: tokens<br/>correct, 3 fingerprints.<br/>Bad profiles exit 2 and<br/>name the…"
    Morpheus->>Smith: "lead handoff"
    Note right of Morpheus: "Review approved. Parser<br/>stays one function,<br/>modifiers stay table-<br/>driven, no new<br/>dependency. Noted: REGEX<br/>searches (anchor to<br/>match whole va…"
    Smith->>Mouse: "user approve"
    Note right of Smith: "User test approved.<br/>Errors name the file,<br/>entry and cause. Docs<br/>show a worked example of<br/>each modifier and say<br/>when to quote. One risk<br/>left…"
    Mouse->>User: "sm done"
    Note right of Mouse: "Done: GLOB/REGEX/REGSUB<br/>passed UAT, review and<br/>user test with no fix<br/>cycles. Committed on<br/>fix/glob-regex-regsub.<br/>Board updated. Owner<br/>decid…"
    Cypher->>Smith: "pm plan sprint"
    Note right of Cypher: "Sprint 11 stories<br/>written (Tier 2, owner<br/>said make it so):<br/>FING-35 Python 3.14+<br/>(Tank), FING-36 modifier<br/>arguments as YAML<br/>mappings, FING-3…"
    Morpheus->>Smith: "lead arch"
    Note right of Morpheus: "Architecture appended<br/>(D1-D7): jsonschema<br/>Draft 2020-12, schema<br/>shipped in the wheel,<br/>if/then per modifier<br/>instead of oneOf for<br/>readable er…"
    Smith->>Mouse: "user approve"
    Note right of Smith: "Gate 1 approved. rubric<br/>STORIES: OUT=S TEST=S<br/>FAIL=S SCOPE=A SIZE=A<br/>DESIGN=A. Criteria carry<br/>concrete examples,<br/>failure output and exit<br/>cod…"
    Mouse->>Tank: "sm plan"
    Note right of Mouse: "Board written to<br/>task.md: Phase 0 Tank<br/>(Python 3.14+,<br/>jsonschema dep), Phase 1<br/>Neo (mapping modifiers),<br/>Phase 2 Neo (schema +<br/>check). Close…"
    Mouse->>All: "phase 0"
    Note right of Mouse: "Phase 0: move the<br/>project to Python 3.14<br/>and later, test on 3.14<br/>and 3.15, and add the<br/>jsonschema dependency<br/>the profile checker will<br/>use."
    User->>All: "request"
    Note right of User: "*queue for bob-protocol<br/>project: tank needs a<br/>dependency analysis tool<br/>for validating 3rd party<br/>packages used in the<br/>project. think scannin…"
    Mouse->>Tank: "sm queue"
    Note right of Mouse: "Queued in task.md for<br/>the bob_protocol repo:<br/>Tank dependency analysis<br/>tool (scanning,<br/>reputation,<br/>vulnerability checks).<br/>Picked up after Sp…"
    Tank->>Trin: "devops handoff"
    Note right of Tank: "Phase 0 done: floor 3.14<br/>in both manifests and<br/>.python-version, test-<br/>all and CI on 3.14 +<br/>3.15, ruff py314<br/>(reformats except A,<br/>B:), jsonsc…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "Phase 0 UAT pass: AC1<br/>manifests + classifiers<br/>3.14/3.15 only, AC2<br/>test-all green on both,<br/>AC3 .venv is 3.14.8 from<br/>clean, AC4 uv refuses<br/>ol…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 0 approved. Build<br/>commit is Conventional<br/>with BREAKING CHANGE<br/>footer. @Neo *swe impl<br/>phase-1"
    Mouse->>All: "phase 1"
    Note right of Mouse: "Phase 1: modifier<br/>arguments are written as<br/>YAML mappings (name plus<br/>named arguments, flags<br/>for regexes), the string<br/>argument syntax and its…"
    User->>All: "request"
    Note right of User: "*queue another for bob<br/>protocol: trinity should<br/>have her own test<br/>strategy doc that lays<br/>out the testing<br/>practices and<br/>conventions for the…"
    Mouse->>Trin: "sm queue"
    Note right of Mouse: "Queued in task.md for<br/>the bob_protocol repo:<br/>Trin-owned test strategy<br/>doc (test pyramid mapped<br/>to ecosystem tools).<br/>Picked up after Sprint…"
    User->>All: "request"
    Note right of User: "make a note that until a<br/>semv project hits v1 -<br/>we never want to spend<br/>any effort maintaining<br/>backwards compatibility.<br/>it's a huge wasted e…"
    Mouse->>All: "sm note"
    Note right of Mouse: "Owner rule recorded: no<br/>backwards compatibility<br/>before 1.0. SDLC section<br/>7, DECISIONS, and a<br/>lasting memory. Applied<br/>now: FING-36 AC4 and A…"
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 1 done: Modifier<br/>object (bare name or<br/>mapping), flags imsx,<br/>string parser deleted,<br/>MaskEntry normalises.<br/>Examples, READMEs,<br/>guide, AR…"
    Trin->>Morpheus: "qa handoff"
    Note right of Trin: "Phase 1 UAT pass via<br/>CLI: IN_RANGE/GLOB/REGSU<br/>B/REGEX-with-flags<br/>mapping profile gives 4<br/>fingerprints with<br/>correct tokens, shipped<br/>example m…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 1 approved. Table-<br/>driven registry kept,<br/>regexes compiled once<br/>per pattern and flags,<br/>Modifier hashable via<br/>frozen params. The<br/>structu…"
    Mouse->>All: "phase 2"
    Note right of Mouse: "Phase 2: profiles are<br/>checked against a<br/>published JSON Schema,<br/>fingerprint check lists<br/>every problem with its<br/>location, merge runs the<br/>same…"
```
