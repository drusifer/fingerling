# Sprint 7 (Fast-Track): "Comprehensive Input-Validation Policy Demo"

This document combines **User Stories** and **Architecture Design** for Sprint 7, per Cypher's
Tier 2 fast-track guidance (single story, minor scope).

*   **Total Points**: 3 Story Points
*   **Target Scenario**: The live demo currently shows fingerling blocking one *exact* attack
    fingerprint (the specific `; echo ...` payload captured during the attack step). This sprint
    adds a second demo scenario showing fingerling generate a *comprehensive* policy that blocks
    any request to `/ping` whose `host` parameter contains a shell metacharacter (`;`) — the
    input validation `examples/vulnerable_app.py`'s CWE-78-vulnerable handler never performs —
    entirely from the external enforcement layer, with **no change to the vulnerable line
    itself** (`cmd = f"ping -c 1 {host}"` / `subprocess.run(cmd, shell=True, ...)` stays as-is —
    that's the point of the demo).

---

## 📋 User Story & Acceptance Criteria

### STORY-FING-22: Pattern-Based Comprehensive Block Demo
**Points:** 3 · **Epic:** Live Demo Fidelity
**Role:** Security Engineer evaluating Project Fingerling

**As a** user watching the Fingerling live demo,
**I want** to see fingerling move beyond blocking one known-bad fingerprint to blocking an entire
*class* of injection attempts (any `;` in the vulnerable parameter),
**so that** I understand fingerling can do real input-validation-equivalent enforcement, not just
signature matching against traffic it has already seen.

#### Acceptance Criteria
1. **Narrow block still shown first (unchanged)**: existing Step 7 behavior (retrigger the exact
   captured attack, confirm 403 from the trajectory-fingerprint match) is unchanged.
2. **New demo step added after Step 7**: sends a *different* `;`-based payload never captured in
   baseline/attack (e.g. `127.0.0.1; id`) and shows it is **not** blocked by the narrow
   fingerprint policy — proving the narrow fix's blind spot.
3. **Comprehensive policy compiled and applied**: fingerling compiles a second policy rule that
   matches on the literal `;` character in the request parameter (not a specific fingerprint),
   and the demo shows this new policy being written/applied.
4. **Both payloads now blocked**: re-sending the original attack payload *and* the new
   never-before-seen `;` payload both return 403 under the comprehensive policy.
5. **Legitimate traffic unaffected**: a clean baseline ping (no `;`) still returns 200 after the
   comprehensive policy is active — proves the fix isn't a blunt "block everything."
6. **No change to the vulnerable line**: `examples/vulnerable_app.py`'s `cmd = f"ping -c 1
   {host}"` / `subprocess.run(cmd, shell=True, ...)` construction is untouched by this story —
   the fix lives entirely in the (already-existing, simulated) KubeArmor policy-enforcement block
   that wraps it, not in the vulnerable handler logic itself.
7. **Narrative clarity**: TUI narrative text explicitly contrasts "exact-fingerprint block
   (reactive, narrow)" vs. "pattern-based block (proactive, comprehensive)" so a user watching
   understands why both matter and neither alone is sufficient.

---

## 🛠️ Architecture & Technical Design

### `fingerling/policy.py` — `compile_policy()` extension
Add one new **optional, backward-compatible** parameter:

```python
def compile_policy(
    workload_name: str,
    match_labels: dict[str, str],
    anomalous_trajectory: str | tuple[str, ...],
    namespace: str = "default",
    action: Literal["Block", "Post"] = "Block",
    block_pattern: str | None = None,
) -> str:
```

When `block_pattern` is provided, the compiled manifest gains one new field:

```yaml
spec:
  process:
    matchPaths: []
    matchPattern: ";"      # new — only present when block_pattern is passed
```

`matchPaths` and all existing fields/behavior are untouched when `block_pattern` is omitted (the
4 existing `test_policy.py` cases keep passing unmodified — this is additive, not a schema
rewrite).

### `examples/vulnerable_app.py` — enforcement block extension
The existing "Simulated KubeArmor Policy Enforcement" section inside `do_GET` (this is the
demo's enforcement/defense layer, not the vulnerable business logic below it) gets one new,
independent check alongside the existing fingerprint-hash check:

```python
match_pattern = policy_data.get("spec", {}).get("process", {}).get("matchPattern")
if match_pattern and match_pattern in host:
    print(f"KubeArmor blocked process execution: pattern match {match_pattern!r}", file=sys.stderr)
    self.send_response(403)
    ...
```

This runs *before* the unsanitized `subprocess.run(cmd, shell=True, ...)` call, same as the
existing fingerprint check — it is a pure addition, no existing lines change.

### `examples/demo.py` — new TUI step
One new step inserted after the existing "retrigger blocked attack" step, before the
allowed-baseline-still-works step:
1. Compile a second policy via `compile_policy(..., block_pattern=";")`, write it alongside the
   existing policy file (or merge into the same YAML — merge is simpler, one policy file with
   both `anomalous-trajectory` annotation and `matchPattern` field).
2. Fire a GET request with a *novel* `;`-based host value not seen during baseline/attack
   capture, before the comprehensive rule is written — expect 200 (blind spot demonstrated) is
   **out of scope for this fast-track pass** if it meaningfully complicates step sequencing;
   Neo may instead show both the narrow-miss and comprehensive-catch in a single side-by-side
   comparison within one step if that's cleaner in the TUI narrative flow. Trin verifies whichever
   sequencing Neo picks still satisfies AC2-AC5 above.
3. Re-fire both the original and novel payload — expect 403 for both.
4. Fire the existing clean baseline ping — expect 200.
5. Narrative text updated per AC7.

### Out of scope
- No change to `vulnerable_app.py`'s vulnerable command construction/execution.
- No real KubeArmor/Kubernetes integration (matches existing POC scope — this is still the
  simulated enforcement layer already in place).
- No general-purpose "sanitize" mode (strip `;` and continue) — AC set above chose **block**,
  not silent sanitization, since a demo that silently rewrites attacker input is less legible
  than one that visibly rejects it. (Flagged for Smith gate — see below.)
