# Project Fingerling — POC User Guide

This guide covers the 4 library modules delivered in the POC Fingerling sprint (see
`docs/USER_STORIES.md` and `docs/ARCH.md`) and walks through a real, runnable end-to-end demo.

**Scope reminder:** this is the pure-logic fingerprinting core only. There is no webhook
server, no live Kubernetes cluster, and no automated Git commit/PR flow yet — those are
next-sprint work (see the backlog in `docs/USER_STORIES.md` and `agents/CHAT.md`'s launch
message). Everything below runs offline, no infrastructure required.

## Contents

1. [Install](#install)
2. [The Pipeline at a Glance](#the-pipeline-at-a-glance)
3. [Module Reference](#module-reference)
   - [`fingerling.tokenizer`](#fingerlingtokenizer)
   - [`fingerling.warehouse`](#fingerlingwarehouse)
   - [`fingerling.ringbuffer`](#fingerlingringbuffer)
   - [`fingerling.policy`](#fingerlingpolicy)
4. [End-to-End Demo](#end-to-end-demo)
5. [Live Capture (Real eBPF)](#live-capture-real-ebpf)
6. [Known Gaps](#known-gaps-see-backlog)
7. [Troubleshooting / FAQ](#troubleshooting--faq)

## Install

```sh
pip install -r requirements.txt   # PyYAML is the only dependency
```

Run the test suite to confirm your environment is set up correctly:

```sh
make test    # 60/60 tests, fully offline
```

## The Pipeline at a Glance

```
raw JSONL telemetry
        │
        ▼
fingerling.tokenizer   — extract fields via JSONPath, collapse to stable string tokens
        │
        ▼
fingerling.warehouse   — hash tokens into a fingerprint ID, upsert into a bounded history
        │
        ▼
fingerling.ringbuffer  — feed the fingerprint ID stream into a sliding-window matcher
        │
        ▼           (score 1.0 = anomalous trajectory)
fingerling.policy      — compile a KubeArmorPolicy manifest for the anomaly
```

Full architectural rationale (including why each interface looks the way it does) is in
`docs/ARCH.md`; this guide is the "how do I actually call this" companion.

## Module Reference

### `fingerling.tokenizer`

Turns one telemetry record (or a JSONL stream of them) into a small dict of stable string
tokens, using a list of extraction rules (a "mask profile").

```python
from fingerling.tokenizer import MaskEntry, parse_jsonl, tokenize

mask_profile = [
    MaskEntry(key="hook_syscall", path="$.process_kprobe.function_name", modifier="DEFAULT"),
    MaskEntry(key="dest_port", path="$.process_kprobe.args[0].sock_arg.dport",
              modifier="ANY(80, 443, 6379)"),
]

records = parse_jsonl(jsonl_text)          # one dict per line
tokens = tokenize(records[0], mask_profile)  # {"hook_syscall": "sys_connect", "dest_port": "TRUE"}
```

**Modifiers** (the second positional part of a `MaskEntry`, e.g. `"IN_RANGE(-999, 0)"`):

| Modifier | Behavior |
|---|---|
| `DEFAULT` | Passes the literal value through as a string; `"NULL"` if absent/null |
| `IS_PRESENT` | `"TRUE"`/`"FALSE"` — is the field present and non-null? |
| `IS_NULL` | `"TRUE"`/`"FALSE"` — is the field absent or explicitly null? |
| `IN_RANGE(low, high)` | `"TRUE"` if `low <= value <= high`, else `"FALSE"` |
| `ANY(v1, v2, ...)` | `"TRUE"` if the value matches one of the listed options |

A missing or `null` field never raises — every modifier degrades to a stable `"FALSE"`/`"NULL"`
token instead.

### `fingerling.warehouse`

Hashes a token dict into a stable fingerprint ID and tracks how often each one has been seen.

```python
from fingerling.warehouse import Warehouse

warehouse = Warehouse()
fingerprint_id = warehouse.upsert(tokens, duration_ms=1.84, raw_record=records[0])

record = warehouse.get(fingerprint_id)
record.total_occurrences   # grows each time the same token set is seen again
record.samples             # up to 3 raw records, most recent last

warehouse.save("fingerprints.yaml")   # persist
warehouse.load("fingerprints.yaml")   # reload into a fresh Warehouse()
```

Two calls with the same tokens produce the same `fingerprint_id` and reuse one record (a
"match"); different tokens create a new record (a "drift"). See `docs/DECISIONS.md` for why the
sample ring grows on every call, not just on drift.

### `fingerling.ringbuffer`

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
what `docs/USER_STORIES.md` and the tests are written against. **A `0.0` during warm-up looks
identical to a genuine clean match** — check `matcher.warm` before trusting a `0.0` as "verified
safe" (see the HCI note in `docs/DECISIONS.md`).

One behavior worth knowing: once an anomalous fingerprint enters the window, every N-gram that
still contains it also scores `1.0` until it slides back out. The demo below shows this — a
single unexpected syscall makes both itself *and* the syscall right after it register as
anomalous.

### `fingerling.policy`

Compiles a `KubeArmorPolicy` Kubernetes manifest for an anomalous trajectory.

```python
from fingerling.policy import compile_policy

manifest_yaml = compile_policy(
    workload_name="checkout-backend",
    match_labels={"app": "checkout-backend"},
    anomalous_trajectory="fp_x,fp_y",   # a string; join a tuple of IDs yourself (see Known Gaps)
    namespace="default",                 # optional, defaults to "default"
    action="Block",                      # optional, "Block" (default) or "Post"
)
```

`action` is always explicit — the compiler never infers Block vs. Post from workload metadata
(see `docs/DECISIONS.md` for why).

## End-to-End Demo

A complete, runnable script lives at `examples/demo.py`. It simulates a "checkout-backend"
workload: a clean baseline window teaches the system what normal looks like, then a live
session with one unexpected syscall (`sys_execve`) gets flagged and turned into a policy.

Run it yourself:

```sh
make demo                    # preferred — routes through mkf, logs to build/build.out
python3 -m examples.demo     # equivalent, direct
```

**Actual output** (captured from a real run — nothing below is hand-written):

```
=== Stage 1: Baseline (training) telemetry ===
Warehouse learned 3 distinct fingerprints from the baseline.
Compiled whitelist of 3 whitelisted 2-grams.

=== Stage 2: Live telemetry, scored against the baseline ===
  syscall=sys_connect  fingerprint=55976bf9...  score=0.0  [clean/warm-up]
  syscall=sys_read     fingerprint=9605acfd...  score=0.0  [clean/warm-up]
  syscall=sys_execve   fingerprint=cb4b332e...  score=1.0  [ANOMALOUS]
  syscall=sys_write    fingerprint=d90c9f67...  score=1.0  [ANOMALOUS]

=== Stage 3: Compile a KubeArmorPolicy for the anomalous trajectory ===
apiVersion: security.kubearmor.com/v1
kind: KubeArmorPolicy
metadata:
  name: fingerling-checkout-backend
  namespace: default
  annotations:
    fingerling.io/anomalous-trajectory: cb4b332ec907fffa6326a078d2d2339f,d90c9f679e4c2102fb27e53f983d08fb
spec:
  selector:
    matchLabels:
      app: checkout-backend
  process:
    matchPaths: []
  action: Block
```

**Reading the output:** `sys_connect` and `sys_read` score `0.0` because the window hasn't
filled to depth 2 yet (warm-up). `sys_execve` was never in the baseline, so its 2-gram
(`sys_read → sys_execve`) scores `1.0`. `sys_write` also scores `1.0` — not because `sys_write`
itself is unusual, but because the window it's evaluated in (`sys_execve → sys_write`) still
contains the anomalous fingerprint. The two anomalous fingerprint IDs get joined and handed to
`compile_policy()`, producing the manifest in Stage 3.

The exact same flow, asserted rather than printed, lives in `tests/test_e2e.py` — that's what
runs in `make test` on every change, so this demo can't silently drift out of sync with the
real API.

## Live Capture (Real eBPF)

`examples/demo.py` above uses hand-authored JSONL. `examples/demo_live_exploit.py` runs the same
three-stage pipeline against **real syscalls captured from a real running process** via
[bpftrace](https://github.com/bpftrace/bpftrace), instead of synthetic fixtures.

**Prerequisites** (unlike everything else in this guide, this is not OS-agnostic or offline):
- Linux with kernel eBPF/tracepoint support.
- `bpftrace` installed (`apt install bpftrace` on Debian/Ubuntu/Raspberry Pi OS).
- Root — bpftrace needs root to attach kernel probes. Run with `sudo`.
- `flask` installed (`pip install flask`) — used only by the vulnerable demo target, not by the
  core `fingerling` library.

**Safety note:** the demo target (`examples/vuln_ping_app.py`) is a real, deliberately
vulnerable local web app (OS command injection, CWE-78). It binds to `127.0.0.1` only, the
"attack" is a single non-networked `curl` request, and the only side effect is a throwaway file
at `/tmp/pwned_poc` that the demo script removes itself. Do not expose this app beyond loopback.

```sh
sudo make demo-live                       # preferred — routes through mkf
sudo python3 -m examples.demo_live_exploit  # equivalent, direct
```

**What it does:**
1. Starts `examples/vuln_ping_app.py`, a Flask app with one intentionally vulnerable route:
   `/diagnostics?host=<x>` runs `os.system(f"ping -c 1 -W1 {x}")` — unsanitized shell
   interpolation.
2. Traces that process (and everything it forks) with `tools/capture_syscalls.bt`, a bpftrace
   script that follows the whole process subtree — necessary because each request forks a shell,
   which forks `ping` — and emits real `execve()` events as Tetragon-shaped JSONL via
   `fingerling.capture`.
3. Sends 3 clean baseline requests, builds a whitelist from the real captured `sh`/`ping` execve
   pattern.
4. Sends one attack request — `host=127.0.0.1; /bin/sh -c 'id > /tmp/pwned_poc'` — a real OS
   command injection that spawns a genuinely unexpected `execve(/bin/id)`.
5. Scores the real captured attack trajectory against the real captured baseline whitelist, and
   compiles a `KubeArmorPolicy` for the anomalous fingerprint — same `compile_policy()` call as
   the synthetic demo, just fed real data.

This demo's `MASK_PROFILE` tokenizes the execve target binary (`exec_target`), not a destination
port like `examples/demo.py` does — see Known Gaps below for why, and see
`fingerling/capture.py`/`tools/capture_syscalls.bt` for how the capture itself works (the pure
parsing logic in `capture.py` is unit tested in `tests/test_capture.py`; the bpftrace subprocess
plumbing is integration-only, exercised by this demo).

## Automated GitOps Delivery Pipeline

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

Fingerling features a "vaccination" engine to run target exploit simulations within isolated workspaces.

**Modules**:
- **Sandbox (`fingerling/sandbox.py`)**: Runs commands under a subprocess. If configured, writes process PIDs to `/sys/fs/cgroup/<cgroup_name>/cgroup.procs` for resource limits. If cgroups v2 is unconfigured or permissions are restricted, falls back gracefully to standard process isolation.
- **Vulnerable Target (`examples/vulnerable_app.py`)**: A standard library HTTP server exposing a command injection vulnerability at `/ping?host=<ip>` (CWE-78).
- **Vaccine Replay Engine (`fingerling/vaccine.py`)**: Sends baseline requests (`/ping?host=127.0.0.1`) and benign exploit requests (`/ping?host=127.0.0.1;echo%20boo`) to map execution paths and stream telemetry to the Webhook server.

This closes the loop: triggering the exploit creates the anomalous trajectory which triggers policy compilation and GitOps hotfixes automatically.

## Known Gaps (see backlog)

These are intentional POC-scope boundaries, not bugs — tracked in `docs/USER_STORIES_SPRINT4.md` and
`agents/CHAT.md`'s sprint-close message:

- **No real destination-port capture.** `tools/capture_syscalls.bt` traces `execve()` only, not
  `connect()`. This Pi's kernel has no BTF (`/sys/kernel/btf/vmlinux` absent), so bpftrace can't
  resolve named struct casts (`struct sockaddr_in`) to pull a real `dport` out of `connect()`'s
  sockaddr argument — raw pointer arithmetic on the user pointer was tested and reads back 0.
  Fixable later via `buf()` + Python-side byte parsing of the sockaddr layout, or by rebuilding
  the kernel with `CONFIG_DEBUG_INFO_BTF=y` (a multi-hour undertaking on a Pi, not attempted).
  Not a blocker: `examples/demo_live_exploit.py`'s anomaly signal is entirely execve-based.
- **Mock/Simulated cgroup limitations** — while cgroup assignments are attempted, full cgroup-level container runtime policies (like namespace restrictions or root filesystem mounts) are deferred.

## Troubleshooting / FAQ

**"Why does `push()` only return 0.0 or 1.0 instead of a real similarity score?"**
That's the STORY-FING-03 contract as written — a binary in-whitelist/not-in-whitelist check for
the POC, not the full Jaccard-similarity scoring described in `docs/SOURCE_SPEC.md`'s
architecture doc. The continuous Jaccard-based scoring is a next-sprint item.

**"`ValueError: Unknown modifier"` when calling `tokenize()`.**
Your `MaskEntry.modifier` string doesn't match one of `DEFAULT`, `IS_PRESENT`, `IS_NULL`,
`IN_RANGE(...)`, or `ANY(...)` exactly (case-sensitive, no extra whitespace before the `(`).

**"`ValueError: match_labels must not be empty`" from `compile_policy()`.**
This is intentional — an empty `matchLabels` selector would match every pod in the namespace.
Pass at least one label (e.g. `{"app": "your-workload"}`).
