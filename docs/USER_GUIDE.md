# Project Fingerling — User Guide

This guide covers the parked detection/vaccination pipeline (see `docs/ARCH.md` for the module
map). The fingerprint tool it builds on, sketch-tastic, has its own documentation:
[drusifer/sketch-tastic](https://github.com/drusifer/sketch-tastic).

The pipeline runs offline once installed. The vaccination TUI demo additionally
needs Linux, root and `bpftrace`. There is still no live Kubernetes/KubeArmor integration —
policy enforcement is simulated.

## Contents

1. [Install](#install)
2. [The Pipeline at a Glance](#the-pipeline-at-a-glance)
3. [Module Reference](#module-reference)
   - [`fingerling.ringbuffer`](#fingerlingringbuffer) *(parked)*
   - [`fingerling.policy`](#fingerlingpolicy) *(parked)*
4. [End-to-End Pipeline](#end-to-end-pipeline) *(parked)*
5. [Interactive Vaccination TUI Demo](#interactive-closed-loop-vaccination-tui-demo) *(parked)*
6. [Known Gaps](#known-gaps-see-backlog)
7. [Troubleshooting / FAQ](#troubleshooting--faq)

## Install

```sh
pipx install uv # once per machine
make install    # builds .venv from pyproject.toml + uv.lock
make test       # full suite, offline
```

`make install` builds an isolated project virtualenv; nothing is installed into the system
Python. Dependencies are declared in `pyproject.toml` (`rich`, used only by the TUI demo, is the
`demo` extra). Every `make` target runs inside `.venv` and tells you to run `make install` if it
is missing. `make install` also fetches sketch-tastic from GitHub at the pinned commit, so it
needs network access. `make distclean` removes the environment.

## The Pipeline at a Glance

The first two stages are sketch-tastic (an external dependency). The last two belong to the
parked `fingerling` pipeline: they work and are tested, but are not being developed (see
`docs/SDLC.md`, Active scope).

```
raw JSONL telemetry
        │
        ▼
sketchtastic (Field, tokens)    — extract fields via JSONPath, collapse to stable string tokens
        │
        ▼
sketchtastic.Sketch — hash tokens into a skit id, upsert into the sketch
        │
        ▼
fingerling.ringbuffer  — feed the skit id stream into a sliding-window matcher
        │
        ▼           (score 1.0 = anomalous trajectory)
fingerling.policy      — compile a KubeArmorPolicy manifest for the anomaly
```

Full architectural rationale (including why each interface looks the way it does) is in
`docs/ARCH.md`; this guide is the "how do I actually call this" companion.

## Module Reference

The `Field`, `tokens`, `Aggregate`, `Sketch` and `skit_id` the pipeline uses are documented in
[sketch-tastic](https://github.com/drusifer/sketch-tastic).

### `fingerling.ringbuffer`

*Parked module.*

Feeds a stream of fingerprint IDs through a fixed-depth sliding window and scores each
resulting N-gram against a pre-compiled whitelist of "known good" N-grams.

```python
from fingerling.ringbuffer import SlidingWindowMatcher

matcher = SlidingWindowMatcher(n=2, whitelist={("fp_a", "fp_b"), ("fp_b", "fp_c")})

matcher.push("fp_a")   # -> 0.0 (warm-up, window not full yet)
matcher.push("fp_b")   # -> 0.0 ("fp_a", "fp_b") is whitelisted
matcher.push("fp_x")   # -> 1.0 ("fp_b", "fp_x") is NOT whitelisted
matcher.warm           # -> True once the window has filled at least once
```

`push()` always returns `0.0` or `1.0` — that's the contract STORY-FING-03 specifies, and it's
what `docs/sprints/USER_STORIES_SPRINT1.md` (STORY-FING-03) and the tests are written against. **A `0.0` during warm-up looks
identical to a genuine clean match** — check `matcher.warm` before trusting a `0.0` as "verified
safe" (see the HCI note in `docs/DECISIONS.md`).

One behavior worth knowing: once an anomalous fingerprint enters the window, every N-gram that
still contains it also scores `1.0` until it slides back out. The demo below shows this — a
single unexpected syscall makes both itself *and* the syscall right after it register as
anomalous.

### `fingerling.policy`

*Parked module.*

Compiles a `KubeArmorPolicy` Kubernetes manifest for an anomalous trajectory.

```python
from fingerling.policy import compile_policy

manifest_yaml = compile_policy(
    workload_name="checkout-backend",
    match_labels={"app": "checkout-backend"},
    anomalous_trajectory=("fp_x", "fp_y"),  # a tuple of fingerprint IDs, or a comma-joined string
    namespace="default",                 # optional, defaults to "default"
    action="Block",                      # optional, "Block" (default) or "Post"
    block_pattern=None,                  # optional; e.g. ";" adds a comprehensive
                                          # spec.process.matchPattern rule alongside the
                                          # exact-fingerprint trajectory match
)
```

`action` is always explicit — the compiler never infers Block vs. Post from workload metadata
(see `docs/DECISIONS.md` for why).

## End-to-End Pipeline

*Parked.*

The whole detection flow — telemetry → tokens → fingerprint → sequence score → policy — is
asserted in `tests/test_e2e.py`, which runs in `make test` on every change. A clean baseline
teaches the matcher what normal looks like; one unexpected syscall then scores `1.0` and is
compiled into a `KubeArmorPolicy`. Note that the syscall *after* an anomalous one also scores
`1.0`, because its window still contains the anomalous fingerprint.

To watch the same flow live, use the TUI demo below.

## Interactive Closed-Loop Vaccination TUI Demo

*Parked — last run before Sprint 8; not verified since (see `docs/SDLC.md` section 9).*

Project Fingerling provides a single, unified, flagship interactive TUI dashboard. It guides the user step-by-step through a full E2E trace vaccination cycle, displaying source code snippets, live telemetry transition maps, scrolling server stdout/stderr output logs, and detailed narrative guides inside a single terminal screen.

**Run Command (Requires Linux, root, & bpftrace)**:
```sh
make install          # once
sudo make demo-live
```
Run it through `make` so the project virtualenv is used; `sudo python3 -m examples.demo` will not
find `python-jsonpath`.

**Features & Layout**:
- **Target App Source Code**: Displays the vulnerable Python function and highlights the CWE-78 command execution bug line.
- **Narrative Guide & Pipeline Progress**: Rich, step-by-step narrative text guiding you through the vaccination sequence (Legitimate warmup, exploit detonation, anomaly scoring, GitOps policy commit, baseline traffic validation, and hot-patch enforcement).
- **eBPF Telemetry & Call Stack Fingerprints**: Visualizes captured process transitions, whitelist mappings, highlights anomalies in red, and renders the compiled KubeArmorPolicy manifest inline.
- **Raw Ingested Trace Feed**: Real-time scrolling JSON feed showing raw eBPF process execution events paired from the kernel.
- **Live Logs Pane**: Displays real-time stderr/stdout request logs piped directly from the background target application and webhook server.
- **Hot-Patch Proof**: Demonstrates policy enforcement while visually proving the server PID remains unchanged (hot-patched on-the-fly, zero downtime).
- **Narrow vs. Comprehensive Enforcement**: After the exact-fingerprint block, the demo shows a *different*, never-before-seen `;`-based payload slip past that narrow policy — then fingerling compiles a second, content-based policy (`spec.process.matchPattern`) that blocks any request containing `;`, closing the gap without touching the vulnerable handler's code.

**Strict eBPF Tracing Requirement**:
Fingerling requires standard Linux eBPF kprobes capabilities to monitor workloads:
- **Root Privileges:** The demo must be executed using `sudo` to JIT-compile and load eBPF tracing programs into the kernel space.
- **`bpftrace` Utility:** The JIT compilation of system call hooks (`tracepoint:syscalls:sys_enter_execve` / `tracepoint:syscalls:sys_exit_execve`) is handled via `bpftrace`. This tool must be installed and visible in the search path of the running root shell environment.

## Automated GitOps Delivery Pipeline

*Parked. This section has not been re-checked against the code since Sprint 3.*

Fingerling supports automated workload-bound GitOps delivery. When an anomaly is detected and a policy is compiled, the webhook server can write the policy and commit/merge it automatically to a target GitOps git repository to trigger git-reconciliation.

**Configuration**:
Run `run_server` with parameters:
- `gitops_repo_path`: Absolute path to a local GitOps git repository workspace.
- `gpg_sign`: Enable/disable cryptographically secure GPG signing for policy commits.
- `gpg_key_id`: (Optional) Local user GPG key ID used for GPG signed commits.

**Workflow**:
1. Server initializes/checks out hotfix branch `fingerling-policy-<workload>-<uuid>`.
2. Policy manifest is written to `policies/fingerling-<workload>.yaml` inside the workspace.
3. Commits the manifest (optionally signed with GPG user key).
4. Auto-merges the hotfix branch back to the target branch (e.g. `main`) using non-fast-forward merge (`git merge --no-ff`).
5. Cleans up/deletes the hotfix branch.

The result is reported back in the HTTP response under `"gitops_status": "success"` (or `"gitops_status": "failed: <reason>"` if GPG keys are invalid or merge conflicts occur).

## Controlled Exposure Sandbox (Vaccination)

*Parked. This section has not been re-checked against the code since Sprint 4.*

Fingerling features a "vaccination" engine to run target exploit simulations within isolated workspaces.

**Modules**:
- **Sandbox (`fingerling/sandbox.py`)**: Runs commands under a subprocess. If configured, writes process PIDs to `/sys/fs/cgroup/<cgroup_name>/cgroup.procs` for resource limits. If cgroups v2 is unconfigured or permissions are restricted, falls back gracefully to standard process isolation.
- **Vulnerable Target (`examples/vulnerable_app.py`)**: A standard library HTTP server exposing a command injection vulnerability at `/ping?host=<ip>` (CWE-78).
- **Vaccine Replay Engine (`fingerling/vaccine.py`)**: Sends baseline requests (`/ping?host=127.0.0.1`) and benign exploit requests (`/ping?host=127.0.0.1;echo%20boo`) to map execution paths and stream telemetry to the Webhook server.
- **Antibody Verification**: Once the policy is committed/merged via GitOps, restarting the vulnerable app with the target policy file path simulates the deployed cluster state. Retriggering the `echo boo` command injection is blocked with an HTTP `403 Forbidden` response, while standard `ping` calls remain fully allowed.

This closes the loop: triggering the exploit creates the anomalous trajectory which triggers policy compilation and GitOps hotfixes automatically.


## Known Gaps (see backlog)

These are known limits, not bugs. Planned work is listed in the backlog in `task.md`:

- **No real destination-port capture.** `tools/capture_syscalls.bt` traces `execve()` only, not
  `connect()`. This Pi's kernel has no BTF (`/sys/kernel/btf/vmlinux` absent), so bpftrace can't
  resolve named struct casts (`struct sockaddr_in`) to pull a real `dport` out of `connect()`'s
  sockaddr argument — raw pointer arithmetic on the user pointer was tested and reads back 0.
  Fixable later via `buf()` + Python-side byte parsing of the sockaddr layout, or by rebuilding
  the kernel with `CONFIG_DEBUG_INFO_BTF=y` (a multi-hour undertaking on a Pi, not attempted).
  Not a blocker: `examples/demo.py`'s anomaly signal is entirely execve-based.
- **Mock/Simulated cgroup limitations** — while cgroup assignments are attempted, full cgroup-level container runtime policies (like namespace restrictions or root filesystem mounts) are deferred.

## Troubleshooting / FAQ

**"Why does `push()` only return 0.0 or 1.0 instead of a real similarity score?"**
That's the STORY-FING-03 contract as written — a binary in-whitelist/not-in-whitelist check for
the POC, not the full Jaccard-similarity scoring described in `docs/SOURCE_SPEC.md`'s
architecture doc. Continuous Jaccard-based scoring is on the backlog but parked with the rest of
the sequence-analysis stage.

**"`fingerling: the python-jsonpath package is not installed for this Python`".**
You ran the system `python3`. Run `make install` once, then run the pipeline through `make`
targets or `.venv/bin/python`.

**"`ValueError: Unknown modifier"` when calling `tokenize()`.**
The modifier's `name` isn't one of `DEFAULT`, `IS_PRESENT`, `IS_NULL`, `IN_RANGE`, `ANY`,
`GLOB`, `REGEX` or `REGSUB` (names are case-sensitive), or a modifier that takes arguments was
written as a string instead of a mapping with `name`.

**"`ValueError: match_labels must not be empty`" from `compile_policy()`.**
This is intentional — an empty `matchLabels` selector would match every pod in the namespace.
Pass at least one label (e.g. `{"app": "your-workload"}`).
