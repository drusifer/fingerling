# Project Decisions

Architectural and product decisions, in chronological order. See `docs/ARCH.md` for the full
technical rationale behind each — this file is the index Oracle keeps current.

## 2026-07-12 — POC Fingerling Sprint

**Context:** First sprint in this repo. A full BRD/PRD/ARCH + 4 pre-written user stories already
existed in `docs/SOURCE_SPEC.md` (moved here from repo root during grooming — was `Finglering
Initial Docs.md`). Cypher formalized them into `docs/USER_STORIES.md` as the sprint backlog.

**Decision:** Scope the POC to the pure-logic fingerprinting core only — STORY-FING-01..04
(tokenizer, warehouse, ring-buffer matcher, policy compiler). Webhook ingestion, sandbox
provisioning, live exploit execution, and GitOps commit/PR automation are explicitly deferred;
none require external infra, so `make test` runs fully offline.
**Consequences:** Every module is a pure Python library function/class with no network,
filesystem-required-at-import, or cluster dependency. Makes the POC fast to build and verify,
but the infra pieces (webhook server, sandbox cgroups, GPG-signed auto-merge) remain unimplemented
and un-battle-tested — flagged as the natural next-sprint scope.

**Decision:** No third-party JSONPath library — hand-rolled dot/bracket-index resolver in
`fingerling/tokenizer.py`, limited to the subset the spec actually uses.
**Consequences:** Zero new dependency weight for the POC. Will need to grow (wildcards,
recursive descent) if a future sprint needs full JSONPath — flagged in `docs/ARCH.md` §8 as
anticipated technical debt, not silently reinvented under time pressure later.

**Decision:** `SlidingWindowMatcher.warm` property added alongside the spec-mandated `push()`
0.0/1.0 contract (`fingerling/ringbuffer.py`).
**Consequences:** Resolves a real HCI gap Smith caught at Gate 1 — a `0.0` score during warm-up
was indistinguishable from a genuine "confirmed clean" match (Nielsen Heuristic #1, Visibility
of System Status). The external `push()` contract Trin tests against is unchanged; `warm` is an
additive side-channel for callers (e.g. a future enforcement gate) that need to know the
difference before trusting a `0.0`.

**Decision:** `compile_policy(..., action: Literal["Block","Post"] = "Block")` is an explicit
caller parameter — no inference from workload metadata (`fingerling/policy.py`).
**Consequences:** Resolves Smith's Gate-1 ambiguity note on STORY-FING-04 AC3 ("defaults to
Block or Post based on the target specification" never said which field). Removes a guessing
game Neo would otherwise have had at implementation time.

**Decision:** Warehouse sample ring (`fingerling/warehouse.py`, cap 3) grows on every `upsert()`
call, not just on Drift.
**Consequences:** The story's own AC text ("Do not append a new record block" on Match) only
forbids a new top-level dict entry, not sample-ring growth. This is the only reading under which
the story's own Verification Task ("dropping or rotating older rows") is testable at all — Trin
caught this during Phase 2 UAT, Morpheus endorsed it, `docs/ARCH.md` §4.2/§7 updated to match.

**Decision:** `parse_jsonl(jsonl_text: str) -> list[dict]` added to `fingerling/tokenizer.py`
during Phase 1 UAT (not in the original architecture).
**Consequences:** STORY-FING-01 AC1 literally requires accepting "a valid JSONL input string,"
but the original architecture only specified `tokenize(record: dict, ...)`. Trin caught the gap
at UAT (tests only exercised pre-parsed dicts); Neo added a 4-line wrapper. Lesson: architecture
review should trace every AC to a literal function signature, not just a data-flow diagram — see
`docs/LESSONS.md`.
