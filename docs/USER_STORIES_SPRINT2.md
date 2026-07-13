# Project Fingerling — Sprint 2 User Stories

**Sprint:** Fingerling Sprint 2 — "Live Ingestion & Pipeline Polish"
**Target Velocity:** 13 Story Points
**Source:** Retro backlog from POC Fingerling sprint (`agents/cypher.docs/current_task.md`),
owned by Cypher.

## Sprint Scope

**In scope:** Three POC-cleanup items identified during Sprint 1 UAT/retro (baseline-whitelist
helper, trajectory API friction, JSONPath wildcards), plus the first of three deferred
infra epics — **webhook telemetry ingestion**. Webhook ingestion is prioritized first among the
deferred epics because it's the natural continuation of the existing in-process pipeline
(telemetry -> tokenizer -> warehouse -> ringbuffer -> policy), requires no external cluster or
signing infra, and unblocks real (not hand-authored) telemetry for every story after it.

**Out of scope (deferred to Sprint 3+):** sandbox/cgroup provisioning, live Nuclei/Metasploit
exploit execution, GPG-signed Git commit/auto-merge PR automation, AccuKnox/KubeArmor cluster
deployment. These remain architecture-documented (Morpheus) but unimplemented.

---

## STORY-FING-05: Baseline Whitelist Compiler
**Points:** 3 · **Epic:** Behavioral Tokenization Infrastructure

**As a** DevSecOps Engineer,
**I want** a library function that observes a clean baseline telemetry stream and compiles it
directly into a whitelist of N-gram fingerprint trajectories,
**so that** I no longer have to hand-roll the whitelist-building loop that `examples/demo.py`
currently performs inline (flagged in Sprint 1 retro by Smith during e2e user testing).

### Acceptance Criteria
1. New public function (e.g. `fingerling.warehouse.build_whitelist(records, mask_profile, n)`)
   accepts raw JSONL-parsed records + a `MaskEntry` profile + window size `N`.
2. Internally tokenizes and upserts each record into a `Warehouse`, then returns the set of
   N-gram fingerprint-ID tuples observed, matching the shape `SlidingWindowMatcher` already
   expects as `whitelist`.
3. `examples/demo.py`'s `build_baseline_whitelist()` is replaced with a call into this new
   function (no behavior change to the demo's printed output).

### Verification Tasks
- Given the Sprint 1 demo's `BASELINE_JSONL` fixture, the new function returns the same
  whitelist set the hand-rolled version produced.
- Function is importable and independently unit-testable without `examples/demo.py`.

---

## STORY-FING-06: Trajectory API Alignment
**Points:** 2 · **Epic:** Behavioral Tokenization Infrastructure

**As a** Platform Security Architect,
**I want** `SlidingWindowMatcher` and `compile_policy` to agree on one trajectory representation,
**so that** callers don't have to manually join/split between a tuple and a comma-joined string
(flagged in Sprint 1 retro by Smith as API friction).

### Acceptance Criteria
1. `compile_policy`'s `anomalous_trajectory` parameter accepts the same type
   `SlidingWindowMatcher` produces internally (tuple of fingerprint IDs), not a pre-joined string.
2. Existing callers (`examples/demo.py`, tests) updated to pass the tuple directly — no
   `",".join(...)` at call sites.
3. Change is backward-compatible at the manifest level: generated YAML output is byte-for-byte
   identical to before for the same logical trajectory.

### Verification Tasks
- `compile_policy(..., anomalous_trajectory=("abc123...", "def456..."))` produces the same YAML
  as today's `compile_policy(..., anomalous_trajectory="abc123...,def456...")`.
- `examples/demo.py` runs with no string-joining glue code between ringbuffer and policy stages.

---

## STORY-FING-07: JSONPath Wildcard & Recursive Descent Support
**Points:** 3 · **Epic:** Behavioral Tokenization Infrastructure

**As a** Platform Security Architect,
**I want** the tokenizer's path resolver to support wildcard (`[*]`) and recursive descent (`..`)
JSONPath segments,
**so that** mask profiles can target fields inside variable-length arrays (e.g. every arg in
`process_kprobe.args[*]`) instead of only fixed indices like `args[0]`, which is required for
real (non-POC) eBPF payload shapes (flagged by Morpheus in Sprint 1 retro).

### Acceptance Criteria
1. Path resolver supports `[*]` to map a modifier over every element of an array, producing one
   token per matched element (or a stable aggregate token — Morpheus to specify exact semantics
   during architecture).
2. Path resolver supports `..` recursive descent to find a key at any depth.
3. Existing fixed-index paths (`args[0]`) continue to resolve identically — no regression to
   Sprint 1 mask profiles or tests.
4. Missing/empty wildcard matches still resolve to the stable `"FALSE"`/`"NULL"` token per
   STORY-FING-01's original AC4 (never raises).

### Verification Tasks
- A record with `args: [{"sock_arg": {"dport": 6379}}, {"sock_arg": {"dport": 443}}]` and path
  `$.process_kprobe.args[*].sock_arg.dport` resolves both ports.
- A record missing the `args` array entirely still resolves to `"NULL"`/`"FALSE"`, not an
  exception.

---

## STORY-FING-08: Webhook Telemetry Ingestion Server
**Points:** 5 · **Epic:** Live Ingestion (first of three deferred infra epics)

**As a** DevSecOps Engineer,
**I want** an HTTP endpoint that accepts streaming JSONL telemetry POSTs and feeds each record
through the existing tokenizer -> warehouse -> ringbuffer -> policy pipeline in-process,
**so that** Fingerling can run against real eBPF agent output instead of only static JSONL
fixtures, without yet requiring a live Kubernetes cluster or sandbox provisioning.

### Acceptance Criteria
1. A minimal stdlib-only (or already-approved dependency) HTTP server exposes a single ingestion
   endpoint (e.g. `POST /telemetry`) accepting one JSONL record (or a batch) per request.
2. Each accepted record is run through the full pipeline (tokenize -> upsert -> push ->
   conditionally compile_policy), reusing STORY-FING-05/06 outputs — no duplicate pipeline logic.
3. Server holds pipeline state (`Warehouse`, `SlidingWindowMatcher`, whitelist) in memory across
   requests for the life of the process — this is explicitly a POC ingestion server, not a
   production multi-tenant service.
4. Malformed/invalid JSON in a request returns a 4xx response with a clear error body; it does
   not crash the server process.
5. No real Kubernetes cluster, GitOps commit, or exploit execution is triggered — compiled
   policies are returned in the HTTP response body (or logged), not auto-applied.

### Verification Tasks
- POSTing the Sprint 1 demo's `BASELINE_JSONL` records one at a time, then `LIVE_JSONL`'s
  anomalous record, produces the same anomaly detection + policy YAML as `make demo` does today.
- POSTing malformed JSON returns 4xx, and a subsequent valid POST still succeeds (server state
  intact).

---

## Definition of Done (Sprint 2)
- All 4 stories pass their Verification Tasks under automated unit tests (Trin UAT).
- Morpheus architecture review passed for each phase, including formalizing wildcard-match
  token semantics (STORY-FING-07 AC1) and confirming no infra beyond a local HTTP server is
  required for STORY-FING-08.
- `make test` still runs fully offline (STORY-FING-08's server is tested via an in-process
  client/test harness, not a live network dependency).
