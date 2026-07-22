# Lessons Learned

## 2026-07-12 — POC Fingerling Sprint

**Lesson:** Architecture review should trace every acceptance criterion to a literal function
signature, not just a data-flow diagram.
**What happened:** `docs/ARCH.md`'s original §4.1 for STORY-FING-01 only specified
`tokenize(record: dict, ...)`. AC1 literally says "must accept a valid JSONL input string" —
a distinct, testable entry point that never got a signature in the architecture doc. It slipped
through Smith's Gate 2 review too (Smith checked HCI/UX concerns, not AC-to-signature
traceability — correctly outside Smith's remit). Trin caught it at Phase 1 UAT by checking the
AC text line-by-line against the actual code, not just running the existing test suite (which
passed 17/17 with the gap present).
**Applying it:** Trin's Artifact-Based Verification protocol ("never guess, check artifacts
first") is what caught this — worth reinforcing as the actual backstop for AC-to-code gaps,
since neither Smith's UX gate nor a green test suite alone will catch a missing entry point.
Morpheus should also do one AC-by-AC signature pass at code review, not just structural/smell
review, for stories with a literal "accepts X input format" clause.

**Lesson:** When an AC's wording is ambiguous about *when* an action happens (STORY-FING-02's
sample ring: "Drift State: ... insert into a ring buffer" vs. a Verification Task implying
ongoing rotation), check whether the literal reading makes the story's own Verification Task
testable at all. If it doesn't, the literal reading is probably wrong.
**Applying it:** This resolved the Warehouse sample-ring-growth ambiguity (see
`docs/DECISIONS.md`) without needing another round-trip through Cypher/Smith — Trin adjudicated
it directly against the story's own text, Morpheus endorsed at review. Good pattern for future
POCs with inherited/pre-written ACs where the original author isn't in the loop to clarify.

## 2026-07-12 — Documentation Pass (User Guide + Demo)

**Lesson:** `make demo` failed with "No rule to make target" after adding `demo` only to
`Makefile.prj`. My first diagnosis (Oracle persona) blamed `_IS_BOB_ENTRY`/`Makefile.bob`
detection — plausible-looking but wrong. The actual, documented root cause (per the `make`
skill and `make-discover` skill): **every target needs an explicit stub in both files** —
the real recipe in `Makefile.prj`, *and* a public stub (`target: ## comment` +
`@./agents/tools/mkf.py $(V) $@`) added to the `else` block's `.PHONY` line and target list in
the root `Makefile`. There is no generic catch-all for `Makefile.prj` targets; `make help`
lists them by reading `Makefile.prj` directly, which is why the target *looked* wired up
correctly even though invocation failed.
**Applying it (fixed 2026-07-12):** Added the missing `demo` stub to `Makefile`'s `else` block.
While fixing it, found `tldr` had the *same* bug — a pre-existing gap in the bob-protocol
Makefile itself (not introduced this sprint), silently broken because nothing had exercised
plain `make tldr` before. Fixed both; verified with `make help` (target appears twice: once
per file, per the skill's own verification instructions), `make demo`, `make tldr`, and a full
`make test` (50/50, no regressions). **Lesson under the lesson:** when diagnosing a tooling
failure, check the authoritative skill/doc for the *intended* design before inferring root
cause from symptoms — the real answer was one skill-read away, not a guess.

## 2026-07-21 — Sprint 2: Live Ingestion & Pipeline Polish

**Lesson:** In-process HTTP server tests must isolate their reference states.
**What happened:** During the first `make test` pass after implementing `fingerling/server.py`, the `test_post_valid_telemetry_returns_success` test failed because it was sharing the `Warehouse` and `SlidingWindowMatcher` instances with other tests. The state accumulated across tests, causing the matcher to warm up and trigger unexpected policy compilations.
**Applying it:** Reset shared states (e.g. `self.warehouse._records.clear()` and `self.matcher._window.clear()`) in `setUp()` to keep tests isolated.

**Lesson:** Use dynamic local imports to break circular dependencies in library utility helpers.
**What happened:** The new `build_whitelist` function in `warehouse.py` needed `tokenize` from `tokenizer.py`, which itself imported classes from other modules. Placing `from fingerling.tokenizer import tokenize` dynamically inside the function resolved the issue cleanly.
**Applying it:** Keep modularity high by using dynamic imports when a specific utility function needs cross-module capabilities.

## 2026-07-21 — Sprint 3: Automated GitOps Delivery Pipeline

**Lesson:** Fallback GPG signature checks simplify offline developer workflows.
**What happened:** GPG cryptographic signing requires local keys and a running gpg-agent, which is typically not present on standard test runner environments. Designing the module to raise clear exceptions on key absence and making it configurable allowed mock/offline repo tests to bypass signing while keeping logic verified.
**Applying it:** Ensure automated environment requirements fail gracefully and provide config toggles for localized test coverage.

## 2026-07-21 — Sprint 4: Controlled Exposure Sandbox (Vaccination)

**Lesson:** Implement runtime fallback mechanisms for infrastructure dependencies in test suites.
**What happened:** Writing process PIDs directly to `/sys/fs/cgroup/...` requires superuser access and system-level setup that is unavailable in sandbox container testing environments. Providing a subprocess fallback that logs warnings instead of hard-failing ensures test coverage stays green across all host environments.
**Applying it:** Fallback gracefully to simulated or process-level isolation when hardware/OS features (cgroups, network layers) are restricted.

**Lesson:** Prefer E2E verification tests that validate actual network loopbacks over pure telemetry mocks.
**What happened:** Warming up the sliding-window matcher was initially done via simulated direct JSON telemetry POSTs. By updating the tests and demos to execute actual HTTP GET requests (`/ping?host=127.0.0.1`) to the vulnerable application, we verified app server reachability, response codes, and actual HTTP behavior alongside pipeline telemetry.
**Applying it:** Ensure integration test warmups trace actual application routes whenever possible to uncover network-level failures early.



