# Project Fingerling — POC Sprint User Stories

**Sprint:** POC Fingerling
**Target Velocity:** 18 Story Points
**Source:** Distilled from `docs/SOURCE_SPEC.md` (BRD/PRD/ARCH), owned by Cypher.

## Sprint Scope

**In scope (POC):** pure-logic core of the fingerprinting pipeline — telemetry parsing/tokenization,
stateful fingerprint warehouse, sliding-window sequence matcher, and KubeArmor policy compiler.
All four stories are self-contained library modules with no external infra dependencies (no real
eBPF probes, no live Kubernetes cluster, no GitOps commit/PR automation) — those are stubbed or
deferred so the POC can be built and verified entirely with unit tests.

**Out of scope (POC):** live webhook ingestion server, sandbox/cgroup provisioning, actual Nuclei/Metasploit
exploit execution, real GPG-signed Git commits / auto-merge PRs, AccuKnox/KubeArmor cluster deployment.
These remain architecture-documented (Morpheus) but unimplemented until a post-POC sprint.

---

## STORY-FING-01: eBPF Telemetry Parser & Plug-and-Play Modifier Engine
**Points:** 5 · **Epic:** Behavioral Tokenization Infrastructure

**As a** DevSecOps Engineer,
**I want** to parse streaming JSONL eBPF log lines through JSONPath targets and custom modifier expressions,
**so that** I can collapse high-cardinality fields (PIDs, timestamps) into predictable, low-cardinality tokens before hashing.

### Acceptance Criteria
1. Accepts a valid JSONL input string mimicking eBPF engine output.
2. Evaluates extraction configs using dot-notation JSONPath (`$.process_exec.process.binary`).
3. Implements an extensible modifier map: `DEFAULT`, `IS_PRESENT`, `IS_NULL`, `IN_RANGE(low, high)`, `ANY(v1, v2, ...)`.
4. Missing/null JSONPath targets resolve to a stable `"FALSE"`/`"NULL"` string token instead of raising.

### Verification Tasks
- `pid: 14205` + `IS_PRESENT` → token `"TRUE"`.
- kernel return `-110` vs `IN_RANGE(-999, 0)` → token `"TRUE"`.

---

## STORY-FING-02: Stateful Append-Only Upsert Data Warehouse Compiler
**Points:** 5 · **Epic:** Behavioral Tokenization Infrastructure

**As a** Platform Security Architect,
**I want** the fingerprint engine to alphabetically sort-serialize tokens and run a stateful upsert loop,
**so that** multi-day production traces continuously refine historical thresholds without metadata bloat.

### Acceptance Criteria
1. Sorts key-value evaluation arrays alphabetically by key before flattening (prevents serialization drift).
2. MD5-folds the flattened string into an immutable 32-char hex Fingerprint ID.
3. State Reconciliation Workflow:
   - **Match:** increment `total_occurrences`, update `last_seen_timestamp`, update moving `min/max_duration_ms`. No new record.
   - **Drift:** append a new record block to `fingerprints.yaml`; store the raw source row in a fixed-capacity (max 3) ring sample array.

### Verification Tasks
- Identical telemetry replayed sequentially → `total_occurrences` increments, entry count stays flat.
- Reference sample array caps at 3 rows (rotates/drops oldest).

---

## STORY-FING-03: Stateful Sliding Window Memory Ring Buffer Matcher
**Points:** 5 · **Epic:** Sequence Trajectory Enforcement

**As a** Core Security Engineer,
**I want** to feed streaming Fingerprint IDs into a stateful FIFO ring buffer of size N,
**so that** the system continuously builds and validates sequence trajectories independent of process block boundaries.

### Acceptance Criteria
1. Internal stateful FIFO models the sliding window.
2. Accepts a continuous stream of string Fingerprint IDs.
3. Withholds evaluations until the window fills to depth N (warm-up phase).
4. At each step past warm-up, extracts the contiguous N-gram tuple and checks it against a pre-compiled whitelist: `0.0` if present, `1.0` if unrecognized (anomaly).

### Verification Tasks
- N=3: first 2 pushed tokens return `0.0` (warm-up).
- A sequence departing the whitelisted trajectory → immediate `1.0`.

---

## STORY-FING-04: Automated Label-Bound KubeArmor Policy Compiler
**Points:** 3 · **Epic:** Automated GitOps Delivery

**As a** DevSecOps Automation Specialist,
**I want** the compiler to translate a validated anomaly trajectory into a declarative `KubeArmorPolicy` manifest bound to k8s label selectors,
**so that** defensive policy automatically follows the workload across autoscaling/node eviction.

### Acceptance Criteria
1. Ingests an anomalous trajectory string and generates a syntactically correct `KubeArmorPolicy` CRD.
2. Injects the target workload's identity tags via `matchLabels`.
3. Manifest defaults its action block to `Block` or `Post` per target spec.

### Verification Tasks
- Generated YAML validates against standard KubeArmor schema shape.
- `matchLabels` correctly maps to target workload id (e.g. `app: checkout-backend`).

---

## Definition of Done (POC)
- All 4 stories pass their Verification Tasks under automated unit tests (Trin UAT).
- Morpheus architecture review passed for each phase.
- No external infra required to run the test suite (`make test` runs fully offline).
