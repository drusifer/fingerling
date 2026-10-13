# Sprint 8 User Stories: Fingerprint Sampling CLI

*   **Total Points**: 16 (Tier 1 — four stories, new dependency, breaking store schema)
*   **Status**: Gate 1 approved (Smith, 2026-10-12) with FING-26 AC10-13 added
*   **Source**: User direction in `agents/CHAT.md`, 2026-10-12

## Goal

Turn the fingerprint core into a standalone, general-purpose **sampling tool for JSONL event
streams of any kind** — not just eBPF telemetry. The tool maintains a growing **fingerprint set**
across many runs:

```
existing fingerprint set  +  stream of JSONL events  ->  updated fingerprint set
```

Each run loads the set built by earlier runs, fingerprints every incoming event, merges the new
observations into the fingerprints already seen, and writes the updated set back.

## Scope boundaries (decided with User, 2026-10-12)

- **Independent of capture.** The CLI reads JSONL from a file or stdin. It does not know about
  bpftrace, `fingerling/capture.py`, or any eBPF-specific event shape.
- **No sequence analysis.** N-grams, baselines/whitelists, and anomaly scoring are a later
  pipeline stage that *consumes* fingerprint IDs. They are not part of this tool, its profile
  format, or its stored set. `fingerling/ringbuffer.py` is untouched this sprint.
- **Aggregators work across events, per fingerprint** — e.g. `AVG($.duration_ms)` is the average
  over every event that hashed to that fingerprint, across all runs.
- **JSONPath comes from a library**, with full syntax (filters, slices, unions, recursive
  descent). The hand-rolled resolver is removed. This reverses the POC decision "no third-party
  JSONPath library" (`docs/DECISIONS.md`, 2026-07-12) — Oracle to record.

---

## STORY-FING-23: Library-Backed JSONPath Extraction
**Points:** 3 · **Epic:** Fingerprint Sampling Tool

**As a** user fingerprinting events with nested or irregular structure,
**I want** full JSONPath syntax in my extraction rules,
**so that** I can target the fields that matter without being limited to dots, indexes and `[*]`.

### Acceptance Criteria
1. `fingerling/tokenizer.py` resolves paths through a third-party JSONPath library; the
   hand-rolled `resolve_segments` / `resolve_path` logic is deleted, not kept as a fallback.
2. Filter expressions (e.g. `$.args[?(@.type == 'sock')].dport`), slices, unions and recursive
   descent all resolve correctly, each covered by a test.
3. Match-count semantics are explicit and independent of how the path is spelled:
   0 matches → treated as missing; 1 match → that value; 2+ matches → each tokenized, then
   deduplicated, sorted and comma-joined (today's wildcard behaviour).
4. Every path used by existing tests, examples and the demo yields the **same token** as before,
   so existing fingerprint IDs do not change.
5. A syntactically invalid path fails when the profile is loaded, with an error naming the
   offending entry — not midway through a stream.
6. A missing or null field still never raises during tokenization.
7. The dependency is added to `requirements.txt`. *(Library choice is Morpheus's call.)*

---

## STORY-FING-24: Fingerprint Profile File
**Points:** 3 · **Epic:** Fingerprint Sampling Tool

**As a** user with my own event format,
**I want** to describe how to fingerprint it in a file,
**so that** I can use the tool without writing Python.

### Acceptance Criteria
1. A YAML profile declares two lists: **fields** (define fingerprint identity) and
   **aggregates** (statistics tracked per fingerprint; never part of identity).

   ```yaml
   version: 1
   fields:
     - {key: syscall, path: "$.process_kprobe.function_name", modifier: DEFAULT}
     - {key: port_ok, path: "$.process_kprobe.args[*].sock_arg.dport", modifier: "ANY(80, 443)"}
   aggregates:
     - {key: duration, path: "$.duration_ms", fn: [MIN, MAX, AVG]}
     - {key: samples,  path: "$",             fn: "LAST(3)"}
   ```
2. A loader returns the in-memory profile; the existing `list[MaskEntry]` Python API keeps
   working for library callers.
3. Validation errors (unknown modifier, unknown aggregator, duplicate key, bad path, missing
   `fields`) are reported at load time with the entry's key and the reason.
4. A profile has a stable **profile ID** derived from its `fields` list, so a fingerprint set can
   record which profile produced it.
5. At least one example profile ships in the repo and is exercised by a test.

---

## STORY-FING-25: Mergeable Aggregators
**Points:** 5 · **Epic:** Fingerprint Sampling Tool

**As a** user sampling a high-volume stream,
**I want** per-fingerprint statistics and retained samples that I choose,
**so that** the set summarises what each fingerprint looks like without storing every event.

### Acceptance Criteria
1. Aggregators `SUM`, `AVG`, `MIN`, `MAX` and `LAST(n)` are available, each applied to the
   values its JSONPath selects from every event matching a fingerprint.
2. `LAST(n)` keeps the `n` most recent selected values, oldest dropped first. With path `$` it
   reproduces today's raw-sample ring; `n` is chosen in the profile, not hardcoded to 3.
3. Aggregator state is **mergeable**: folding events in across several runs gives the same result
   as folding them in one run. (`AVG` therefore stores sum and count, not just the mean.)
4. An event where the path has no match, or a numeric aggregator sees a non-numeric value, is
   skipped for that aggregator without failing the run; the number skipped is reported.
5. If a path matches several values in one event, all of them feed the aggregator.
6. Occurrence count and first/last-seen remain built in for every fingerprint.
7. The hardcoded `duration_ms` min/max and 3-sample ring are removed from the store; existing
   callers (webhook server, vaccine, demo) get them by declaring `MIN`/`MAX`/`LAST(3)` in their
   profile. *(Assumption — see Open Questions.)*

---

## STORY-FING-26: `fingerprint` CLI — Merge a Stream into a Fingerprint Set
**Points:** 5 · **Epic:** Fingerprint Sampling Tool

**As a** user collecting samples over many runs,
**I want** one command that folds a JSONL stream into my existing fingerprint set,
**so that** the set grows with everything I have ever observed.

### Acceptance Criteria
1. A command takes a profile, a fingerprint-set file, and JSONL events from a file or stdin, and
   writes the updated set. Illustrative shape (final flags are Morpheus/Smith's call):

   ```sh
   fingerling fingerprint --profile web.yaml --set web.fingerprints.yaml events.jsonl
   some-producer | fingerling fingerprint --profile web.yaml --set web.fingerprints.yaml -
   ```
2. If the set file does not exist it is created; if it exists it is loaded, merged into, and
   rewritten. Fingerprints already in the set keep their history: counts add, aggregates merge,
   `LAST(n)` continues from the stored samples, first-seen is preserved.
3. Running the same events as one batch or split across several runs produces an equivalent set.
4. The set records the profile ID that built it. Merging with a different profile is refused with
   a clear message unless the user explicitly overrides.
5. The set is written atomically — an interrupted or failed run leaves the previous set intact.
6. A malformed JSON line is reported with its line number and skipped; the run continues and the
   exit status reflects that lines were skipped.
7. On completion the command prints a short summary to stderr: events read, new fingerprints,
   existing fingerprints updated, lines skipped. Stdout stays clean for piping.
8. The command works on events that have nothing to do with eBPF — verified by a test using a
   non-telemetry fixture (e.g. web access-log or application events).
9. A `make` target runs the command, per project automation rules.
10. *(Smith Gate 1)* Run with no input file while stdin is a terminal, the command explains what
    it expects and exits — it never sits waiting silently.
11. *(Smith Gate 1)* `--help` includes a worked example and states plainly that the set file is
    updated in place.
12. *(Smith Gate 1)* The set file is readable by a person: aggregates appear under the names
    given in the profile, and `AVG` shows the average itself, not only its internal sum/count.
13. *(Smith Gate 1)* The profile-mismatch refusal names both profile IDs and the flag that
    overrides it.

---

## Out of Scope
- N-gram baselines, whitelists, anomaly/Jaccard scoring, and any `baseline` / `score` subcommand.
- Changes to `fingerling/capture.py` or `fingerling/ringbuffer.py`.
- `GLOB` / `REGEX` modifiers (still a spec gap; candidate for a follow-up).
- Within-event aggregation (e.g. summing several matches into one identity token).
- Non-JSONL input formats.

## Open Questions
1. **Replacing the hardcoded store fields (FING-25 AC7).** Assumed: aggregators become the only
   mechanism and the saved-set schema changes, with server/vaccine/demo updated to match. The
   alternative is a compatibility shim over the old `upsert(duration_ms, raw_record)` signature.
   Morpheus to confirm feasibility and blast radius.
2. **Entry point.** The repo has no packaging metadata, so `fingerling fingerprint` needs either
   a console script or `python -m fingerling`. Morpheus's call.
3. **Timestamps.** First/last-seen currently use wall-clock time at ingestion. For replayed
   streams an optional profile path to the event's own timestamp may be wanted — not included
   unless requested.

---

## Technical Architecture Design (Morpheus)

### D1. JSONPath library: `python-jsonpath`, installed into a project `.venv`
- **Library:** `python-jsonpath` (import name `jsonpath`), v2.x. Pure Python, zero transitive
  dependencies, RFC 9535 syntax plus the common `[?(@.x == 1)]` parenthesised filter form.
  Trialled on this box against every path the tests/examples use — identical results.
  Rejected `jsonpath-ng`: filters live in a separate `.ext` parser and it drags in `ply`.
- **Install:** the system Python here is externally managed (PEP 668; PyYAML and rich come from
  apt), so a bare `pip install` is refused. New `make install` creates `.venv` with
  `--system-site-packages` (keeps apt's PyYAML/rich visible) and installs `requirements.txt`.
  The Makefile uses `.venv/bin/python` when present, else `python3`. No system packages change.
  `sudo make demo-live` keeps working because it goes through the same interpreter variable.

### D2. Module layout
| Module | Change | Responsibility |
|---|---|---|
| `fingerling/tokenizer.py` | rewrite path half | `compile_path`, `find_values` over the lib; modifiers unchanged; `validate_modifier` |
| `fingerling/aggregators.py` | **new** | `AggregateEntry`, spec parsing, per-fingerprint state update |
| `fingerling/warehouse.py` | refactor | the fingerprint set: generic records, versioned file, atomic save |
| `fingerling/profile.py` | **new** | `Profile`, `load_profile`, `profile_id`, validation |
| `fingerling/cli.py`, `fingerling/__main__.py` | **new** | `python -m fingerling fingerprint …` |

`fingerling/ringbuffer.py`, `capture.py`, `policy.py`, `gitops.py` are not touched. The n-gram
stage keeps consuming fingerprint IDs returned by `Warehouse.upsert()`.

### D3. Extraction semantics (FING-23)
```python
def compile_path(path: str) -> jsonpath.JSONPath   # cached; ValueError on empty/invalid
def find_values(record: Any, path: str) -> list[Any]
def tokenize(record, mask_profile) -> dict[str, str]
```
Token rule depends only on match count: 0 → modifier applied to "missing"; 1 → modifier applied
to that value; 2+ → modifier applied to each, deduplicated, sorted, comma-joined. The old
"does the path string contain `*` or `..`" heuristic and `resolve_path`/`resolve_segments` are
deleted. `apply_modifier(value, modifier)` becomes scalar-only.

### D4. Aggregators (FING-25)
```python
@dataclass(frozen=True)
class AggregateEntry:
    key: str
    path: str
    fns: tuple[str, ...]        # normalised labels, e.g. ("MIN", "MAX", "LAST(3)")

def update(state: dict, entry: AggregateEntry, record: Any) -> int   # returns values skipped
```
State is plain YAML-friendly data, keyed by function name, stored under the aggregate's key
(so changing `n` in `LAST(n)` keeps collected samples; one `LAST` per aggregate):

| Fn | Stored state | Notes |
|---|---|---|
| `SUM` | number | |
| `MIN` / `MAX` | number | |
| `AVG` | `{avg, sum, count}` | `avg` is for readers; `sum`/`count` make it mergeable |
| `LAST(n)` | list, newest last | any JSON value; trimmed to `n` on every update |

Numeric functions accept ints, floats and numeric strings (same casting as `IN_RANGE`); bools,
nulls and other values are skipped and counted. Cross-run merge is simply "load state, keep
folding" — one code path, so batch-vs-split equivalence (FING-26 AC3) holds by construction.

### D5. Fingerprint set (FING-25 AC6/7, FING-26)
```python
class Warehouse:
    def __init__(self, aggregates: Sequence[AggregateEntry] = (), profile_id: str | None = None)
    def upsert(self, tokens: dict[str, str], record: Any, timestamp: str | None = None) -> str
    def load(self, path: str, force: bool = False) -> None   # ProfileMismatchError unless force
    def save(self, path: str) -> None                        # temp file + os.replace
```
**Open Question 1 resolved: replace outright.** `upsert(duration_ms=…, raw_record=…)` is gone.
Only one production caller exists (`server.py`), plus `build_whitelist` and tests, so a shim
would be more code than the migration. A shared `TELEMETRY_AGGREGATES` constant (duration
`MIN`/`MAX` on `$.duration_ms`, `LAST(3)` on `$`) gives the server/demo the same data as before.

Set file, version 1 — also newly stores each fingerprint's **tokens**, so a person reading the
file can see what a 32-char ID actually means:
```yaml
version: 1
profile_id: 9f2c…
fingerprints:
  55976bf9…:
    tokens: {syscall: sys_connect, port_ok: "TRUE"}
    total_occurrences: 42
    first_seen: "2026-10-12T20:00:00+00:00"
    last_seen: "2026-10-12T21:00:00+00:00"
    aggregates:
      duration: {MIN: 0.9, MAX: 3.1, AVG: {avg: 1.7, sum: 71.4, count: 42}}
      samples: {LAST: [ {…}, {…}, {…} ]}
```
Pre-Sprint-8 warehouse files are not migrated; loading one raises a clear "unrecognised
fingerprint set format" error. Nothing in the repo persists one today.

### D6. Profile (FING-24)
`profile_id` = MD5 over the sorted `key|path|modifier` triples of `fields` only. Changing
`aggregates` never invalidates a set — a new aggregate just starts accumulating from that run.
All validation (paths compile, modifiers and aggregator specs parse, keys unique, `fields`
non-empty) happens in `load_profile`, raising `ProfileError` naming the entry.

### D7. CLI (FING-26)
```
python -m fingerling fingerprint -p PROFILE -s SET [EVENTS|-] [-o OUTPUT] [--force-profile]
make fingerprint ARGS="-p PROFILE -s SET EVENTS"
```
- `EVENTS` omitted or `-` reads stdin; if stdin is a terminal the command prints usage guidance
  and exits 2 instead of blocking.
- `-o OUTPUT` writes the merged set elsewhere and leaves `SET` untouched (a safe trial run).
- Events are streamed line by line, never read whole.
- Exit codes: `0` clean · `1` set written but some lines were skipped · `2` nothing written
  (bad usage, profile, set file, or profile mismatch).
- Summary on stderr; stdout stays empty.
- **Entry point (Open Question 2):** `python -m fingerling` plus the make target. A `fingerling`
  console script needs packaging metadata the repo doesn't have — deferred, noted for backlog.

### D8. Timestamps (Open Question 3)
Unchanged: wall-clock at ingestion. An event-time path is not built this sprint.
