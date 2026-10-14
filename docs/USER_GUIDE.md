# Project Fingerling — User Guide

This guide covers the fingerprint sampling CLI, the library modules behind it, and the
detection/vaccination pipeline built on top (see `docs/ARCH.md` for the module map).

The fingerprint tool and its library run fully offline. The vaccination TUI demo additionally
needs Linux, root and `bpftrace`. There is still no live Kubernetes/KubeArmor integration —
policy enforcement is simulated.

## Contents

1. [Install](#install)
2. [Fingerprint CLI](#fingerprint-cli)
3. [The Pipeline at a Glance](#the-pipeline-at-a-glance)
4. [Module Reference](#module-reference)
   - [`fingerprint_sampler.tokenizer`](#fingerprint_samplertokenizer)
   - [`fingerprint_sampler.fingerprint_set`](#fingerprint_samplerfingerprint_set)
   - [`fingerling.ringbuffer`](#fingerlingringbuffer) *(parked)*
   - [`fingerling.policy`](#fingerlingpolicy) *(parked)*
5. [End-to-End Pipeline](#end-to-end-pipeline) *(parked)*
6. [Interactive Vaccination TUI Demo](#interactive-closed-loop-vaccination-tui-demo) *(parked)*
7. [Known Gaps](#known-gaps-see-backlog)
8. [Troubleshooting / FAQ](#troubleshooting--faq)

## Install

```sh
pipx install uv # once per machine
make install    # builds .venv from pyproject.toml + uv.lock
make test       # full suite, offline
```

`make install` builds an isolated project virtualenv; nothing is installed into the system
Python. Dependencies are declared in `pyproject.toml` (`rich`, used only by the TUI demo, is the
`demo` extra). Every `make` target runs inside `.venv` and tells you to run `make install` if it
is missing. Installing also creates the `fingerprint` command at `.venv/bin/fingerprint`. `make distclean` removes the environment.

## Fingerprint CLI

The fingerprint tool is its own package, `fingerprint-sampler`, in
`packages/fingerprint-sampler/` (import name `fingerprint_sampler`, command `fingerprint`). Its
[README](../packages/fingerprint-sampler/README.md) is the reference for people installing it on
its own; this section covers using it from a checkout.

`fingerprint` is a general-purpose sampler for JSONL event streams — logs, traces, audit events,
kernel telemetry, anything with one JSON object per line. It reduces each event to a
**fingerprint** (a stable ID for "this shape of event") and maintains a **fingerprint set**: one
entry per distinct fingerprint with a count, first/last seen, and whatever statistics and samples
you ask for. The set grows across runs:

```
existing set  +  stream of events  ->  updated set
```

```sh
# first run creates the set; every later run merges into it
make fingerprint ARGS="-p packages/fingerprint-sampler/examples/access_log.yaml -s web.fingerprints.yaml packages/fingerprint-sampler/examples/access_log.jsonl"

# read from a pipe ('-' or no EVENTS argument means stdin)
tail -n 1000 app.jsonl | .venv/bin/fingerprint merge -p app.yaml -s app.fingerprints.yaml -

# trial run: write the merged result elsewhere and leave the set untouched
.venv/bin/fingerprint merge -p app.yaml -s app.fingerprints.yaml -o /tmp/preview.yaml new.jsonl
```

| Option | Meaning |
|---|---|
| `-p`, `--profile PROFILE` | YAML profile (below). Required. |
| `-s`, `--set SET` | Fingerprint set to merge into. Created if missing, **updated in place**. Required. |
| `EVENTS` | JSONL file; `-` or omitted reads stdin. |
| `-o`, `--output OUTPUT` | Write the merged set here instead; `SET` is left unchanged. |
| `--force-profile` | Merge even though `SET` was built with a different profile. |

A summary goes to stderr; stdout is left empty. Exit status: `0` set written and every line used ·
`1` set written but some lines were skipped · `2` nothing written.

```
fingerprint: 8 events read from packages/fingerprint-sampler/examples/access_log.jsonl
  fingerprints: 4 new, 0 updated, 4 total in set
  skipped: 0 malformed lines, 0 aggregate values
  wrote web.fingerprints.yaml (profile 37087e1858c85f7cb976959311d01b65)
```

### Profiles

A profile says how to fingerprint one kind of event:

```yaml
version: 1

# fields define identity: events with the same tokens share one fingerprint
fields:
  - key: method
    path: "$.request.method"                 # modifier defaults to DEFAULT
  - key: status_class
    path: "$.response.status"
    modifier: {name: IN_RANGE, low: 200, high: 399}
  - key: slow_upstreams
    path: "$.upstreams[?(@.ms > 500)].name"  # full JSONPath, including filters

# aggregates are tracked per fingerprint and never affect identity
aggregates:
  - key: latency_ms
    path: "$.response.ms"
    fn: [MIN, MAX, AVG]
  - key: recent_paths
    path: "$.request.path"
    fn: {name: LAST, n: 3}
```

- **`fields`** — each entry extracts values with a JSONPath and turns them into one token with a
  modifier (see [`fingerling.tokenizer`](#fingerlingtokenizer)). Choose modifiers that collapse
  high-cardinality values (IDs, timestamps, sizes) so that similar events share a fingerprint.
- **`aggregates`** — computed across every event that lands on the same fingerprint, over all runs:

  | Function | Keeps |
  |---|---|
  | `SUM` | running sum of numbers |
  | `MIN`, `MAX` | smallest / largest — numbers, or text such as ISO-8601 times |
  | `AVG` | the average, plus the sum and count that make it mergeable |
  | `COUNT` | how many values the path selected |
  | `{name: FIRST, n: N}` | the `N` earliest values of the path |
  | `{name: LAST, n: N}` | the `N` most recent values of the path |

  One function stores its value directly; several store a map by function name. Numbers and
  numeric strings count as numbers. A value a function can't use, or an event where the path
  matches nothing, is skipped for that aggregate and counted in the summary.

Profiles are checked before any event is read, against a JSON Schema plus the checks a schema
cannot express (regexes, JSONPaths, ranges, duplicate keys). Every problem is listed with its
file and location, e.g. `app.yaml: fields[2] (key 'port') → modifier: 'values' is a required
property`. Run `fingerprint check app.yaml` to check a profile on its own (exit 0 valid, 1 not);
see the package README for using the schema in an editor.

Two profiles ship as starting points: `packages/fingerprint-sampler/examples/access_log.yaml`
(web access logs) and `examples/profiles/ebpf_telemetry.yaml` (the event shape `python -m fingerling.capture` emits).

### The fingerprint set file

```yaml
version: 3
profile_id: 37087e1858c85f7cb976959311d01b65
fingerprints:
  cc986aed647e7d173dcc791d402d3e89:
    tokens: {method: GET, route: "/items/{id}", status_class: 'TRUE'}
    aggregates:                             # from your profile
      latency_ms: {MIN: 9.0, MAX: 12.5, AVG: {avg: 10.83, sum: 32.5, count: 3}}
      recent_paths: [/items/17, /items/42, /items/3]     # one function: its value directly
    meta:                                   # built in, for every fingerprint
      count: 3
      first_seen: '2026-10-13T01:25:42.821783+00:00'
      last_seen: '2026-10-13T01:25:42.822552+00:00'
      first: [{meta: {seen: '2026-10-13T01:25:42.821783+00:00'}, record: {...}}, ...]
      last: [..., {meta: {seen: '2026-10-13T01:25:42.822552+00:00'}, record: {...}}]
```

- `tokens` shows what the ID stands for.
- **`aggregates`** is what your profile asked for; **`meta`** is built in for every fingerprint:
  `count`, `first_seen` / `last_seen` and the first and last 3 records. `meta` comes from a
  built-in profile (`builtin.yaml` in the package) that reads each record wrapped as
  `{meta: {seen: <time read>}, record: <the parsed record>}`, so injected fields never clash with the
  record's own. Times are wall clock; a time field inside the records belongs in `aggregates`.
- `profile_id` is derived from the profile's `fields`. A set can only be merged under the profile
  that built it, because fingerprints from different field definitions aren't comparable. Changing
  `aggregates` is always allowed: a new aggregate starts accumulating from that run, and changing
  `n` of `LAST` keeps the samples already collected.
- Splitting a stream over several runs gives the same set as one run over all of it.
- The file is replaced atomically; a failed or interrupted run leaves the previous set intact.

## The Pipeline at a Glance

The first two stages are the `fingerprint-sampler` package and are under active development.
The last two belong to the parked `fingerling` pipeline: they work and are tested, but are not
being developed while the fingerprint tool is finished (see `docs/SDLC.md`, Active scope).

```
raw JSONL telemetry
        │
        ▼
fingerprint_sampler.model       — extract fields via JSONPath, collapse to stable string tokens
        │
        ▼
fingerprint_sampler.fingerprint_set — hash tokens into a fingerprint ID, upsert into the set
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

### `fingerprint_sampler.model`

The profile's building blocks. A `Field` turns one event into one token: a JSONPath selects
values and a modifier collapses them. `tokens(event, fields)` applies a list of fields.

```python
from fingerprint_sampler.model import Field, tokens

fields = [
    Field("hook_syscall", "$.process_kprobe.function_name"),           # modifier: DEFAULT
    Field("dest_port", "$.process_kprobe.args[0].sock_arg.dport",
          {"name": "ANY", "values": [80, 443, 6379]}),
]
tokens(event, fields)    # {"hook_syscall": "sys_connect", "dest_port": "TRUE"}
```

For telemetry, `fingerling.tokenizer` adds `parse_jsonl(text)` and `tokenize(record, fields)`.

**Modifiers** (the third part of a `Field`): a bare name such as `"IS_PRESENT"`, or a mapping
with `name` and the modifier's arguments, e.g. `{"name": "IN_RANGE", "low": -999, "high": 0}`.
Each modifier is a `Rule` subclass, built and checked when the `Field` is created (`ValueError`
if wrong) — the same way aggregate functions are.

| Modifier | Arguments | Token |
|---|---|---|
| `DEFAULT` | — | the value as a string; `"NULL"` if absent |
| `IS_PRESENT` | — | `"TRUE"` if the key exists, even when its value is `null` |
| `IS_NULL` | — | `"TRUE"` only if the key exists and is set to `null` (a missing key is `"FALSE"`) |
| `IN_RANGE` | `low`, `high` (numbers) | `"TRUE"` if `low <= value <= high` |
| `ANY` | `values` (a list) | `"TRUE"` if the value is one of those listed |
| `GLOB` | `pattern` | `"TRUE"` if the whole value matches the shell-style pattern (`*`, `?`, `[a-z]`), case-sensitive |
| `REGEX` | `pattern`, optional `flags` | `"TRUE"` if the regular expression matches anywhere in the value; anchor with `^` and `$` |
| `REGSUB` | `pattern`, `replace`, optional `flags` | the value with every match replaced (`\1` refers to a group); `"NULL"` if absent |

In a YAML profile, write patterns in single quotes; see the package README for examples and flags.

A missing key and a key set to `null` are different, and `IS_PRESENT` / `IS_NULL` tell them
apart. No modifier ever raises on either: the others give a stable `"FALSE"`/`"NULL"` token.

**Paths** are full JSONPath, resolved by the `python-jsonpath` library: dot and bracket access,
`[*]`, slices (`[0:2]`), negative indexes, unions (`['a','b']`), recursive descent (`..`) and
filters (`[?(@.type == 'sock')]`). The token depends on how many values the path selects: none is
treated as missing; one is tokenized as-is; several are tokenized individually, deduplicated,
sorted and comma-joined, so array order can't change a fingerprint. An invalid path raises
`ValueError` when the `Path` (or the `Field`) is created.

### `fingerprint_sampler.fingerprint_set`

The fingerprint set as a library: hashes a token dict into a stable fingerprint ID and tracks
each one, with the aggregators you declare.

```python
from fingerprint_sampler.aggregators import Aggregate
from fingerprint_sampler.fingerprint_set import FingerprintSet

fingerprints = FingerprintSet(aggregates=[
    Aggregate("duration_ms", "$.duration_ms", ["MIN", "MAX"]),
])
fingerprint_id = fingerprints.upsert(tokens, records[0])

record = fingerprints.get(fingerprint_id)
record.tokens                               # the tokens behind the ID
record.meta["count"]                        # {"COUNT": n}: grows each time the tokens recur
record.aggregates["duration_ms"]["MAX"]
record.meta["last"]["LAST"]                 # up to 3 latest records, each {meta: {seen}, record}

fingerprints.save("fingerprints.yaml")         # atomic
fingerprints.load("fingerprints.yaml")         # continue folding from stored state
```

Two calls with the same tokens produce the same `fingerprint_id` and reuse one record (a
"match"); different tokens create a new record (a "drift"). `FingerprintSet()` with no aggregates
keeps only the count and first/last seen.
`fingerling.warehouse.TELEMETRY_AGGREGATES` is the duration-bounds-plus-last-3-events set the
parked telemetry pipeline uses. To load a profile file
instead of building entries in Python, use `fingerprint_sampler.profile.load_profile(path)` and pass its
`.aggregates` and `.profile_id` to `FingerprintSet`.

> **Changed in Sprint 8:** `upsert(tokens, duration_ms=..., raw_record=...)` is now
> `upsert(tokens, record)`, and `record.min_duration_ms` / `max_duration_ms` / `samples` moved
> under `record.aggregates`. Set files written before this change are not readable.

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
- **No event-time timestamps by default.** `meta` times are when the tool read the record; add a
  time field from the records to `aggregates` if you need event time.
- **Mock/Simulated cgroup limitations** — while cgroup assignments are attempted, full cgroup-level container runtime policies (like namespace restrictions or root filesystem mounts) are deferred.

## Troubleshooting / FAQ

**"Why does `push()` only return 0.0 or 1.0 instead of a real similarity score?"**
That's the STORY-FING-03 contract as written — a binary in-whitelist/not-in-whitelist check for
the POC, not the full Jaccard-similarity scoring described in `docs/SOURCE_SPEC.md`'s
architecture doc. Continuous Jaccard-based scoring is on the backlog but parked with the rest of
the sequence-analysis stage.

**"`fingerling: the python-jsonpath package is not installed for this Python`".**
You ran the system `python3`. Run `make install` once, then use `make fingerprint ARGS="..."` or
`.venv/bin/fingerprint merge ...`.

**"`... was built with profile X, but the current profile is Y`".**
The set file belongs to a different profile (its `fields` differ). Keep one set file per profile.
`--force-profile` merges anyway and stamps the set with the new profile, but the old and new
fingerprints in it will not be comparable.

**The command exits 1 but wrote the set.**
Some input lines weren't valid JSON objects; they are listed on stderr by line number and skipped.

**"`ValueError: Unknown modifier"` when calling `tokenize()`.**
The modifier's `name` isn't one of `DEFAULT`, `IS_PRESENT`, `IS_NULL`, `IN_RANGE`, `ANY`,
`GLOB`, `REGEX` or `REGSUB` (names are case-sensitive), or a modifier that takes arguments was
written as a string instead of a mapping with `name`.

**"`ValueError: match_labels must not be empty`" from `compile_policy()`.**
This is intentional — an empty `matchLabels` selector would match every pod in the namespace.
Pass at least one label (e.g. `{"app": "your-workload"}`).
