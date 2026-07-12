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
5. [Known Gaps](#known-gaps-see-backlog)
6. [Troubleshooting / FAQ](#troubleshooting--faq)

## Install

```sh
pip install -r requirements.txt   # PyYAML is the only dependency
```

Run the test suite to confirm your environment is set up correctly:

```sh
make test    # 50/50 tests, fully offline
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

## Known Gaps (see backlog)

These are intentional POC-scope boundaries, not bugs — tracked in `docs/USER_STORIES.md` and
`agents/CHAT.md`'s sprint-close message:

- **No baseline-whitelist helper.** `examples/demo.py`'s `build_baseline_whitelist()` function
  is exactly the glue code a real caller has to write today — there's no library function that
  turns "here's a batch of clean telemetry" into "here's a compiled whitelist."
- **`compile_policy(anomalous_trajectory: str)`** expects a string; if your anomalous IDs come
  from the ring buffer as a tuple, join them yourself (`",".join(ids)`) as the demo does.
- **No webhook ingestion, sandbox provisioning, live exploit execution, or GitOps commit/PR
  automation** — those remain architecture-documented in `docs/SOURCE_SPEC.md` but unimplemented.

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
