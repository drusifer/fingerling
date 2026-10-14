# Project Fingerling — Architecture

Maintained by Morpheus. Module map current as of Sprint 9 (2026-10-13); sections 3-4 detail the
fingerprinting core. Per-sprint design rationale lives in `docs/sprints/USER_STORIES_SPRINT<N>.md`; how
the project is built, changed and released is in `docs/SDLC.md`.

## 1. System Overview

The repository is a uv workspace with two Python packages.

**`fingerprint-sampler`** (`packages/fingerprint-sampler/`, import `fingerprint_sampler`) — the
published, general-purpose tool for any JSONL event stream. **This is the active scope.**

| Module | Story | Responsibility |
|---|---|---|
| `fingerprint_sampler/tokenizer.py` | FING-01, -07, -23 | JSONPath extraction (via `python-jsonpath`, full syntax) + modifier engine |
| `fingerprint_sampler/aggregators.py` | FING-25 | Per-fingerprint `SUM`/`AVG`/`MIN`/`MAX`/`LAST(n)` state, mergeable across runs |
| `fingerprint_sampler/warehouse.py` | FING-02, -25 | The fingerprint set: MD5 IDs, stateful upsert, versioned atomic YAML file |
| `fingerprint_sampler/profile.py` | FING-24 | YAML profile loading + validation, `profile_id` |
| `fingerprint_sampler/cli.py`, `__main__.py` | FING-26, -28 | `fingerprint merge` — merge a stream into a set |

It depends only on PyYAML, python-jsonpath and jsonschema and never imports `fingerling`.

**`fingerling`** (`fingerling/`, repository root) — the detection-and-response pipeline built on
fingerprint IDs. **Parked** and unpublished: kept importable and tested, not developed.

| Module | Story | Responsibility |
|---|---|---|
| `fingerling/tokenizer.py`, `aggregators.py`, `profile.py` | FING-28 | One-line re-export shims over `fingerprint_sampler` |
| `fingerling/warehouse.py` | FING-05, -28 | Re-exports the fingerprint set; owns `TELEMETRY_AGGREGATES` and the N-gram `build_whitelist` helper |
| `fingerling/cli.py`, `__main__.py` | FING-28 | `fingerling fingerprint`, an alias for `fingerprint merge` |
| `fingerling/ringbuffer.py` | FING-03 | FIFO sliding-window N-gram anomaly matcher |
| `fingerling/policy.py` | FING-04, -06, -22 | KubeArmorPolicy YAML compiler (`block_pattern` adds `matchPattern`) |
| `fingerling/server.py` | FING-08 | stdlib HTTP webhook telemetry ingestion server |
| `fingerling/gitops.py` | Sprint 3 | Commit/merge compiled policies into a GitOps repo (optional GPG signing) |
| `fingerling/sandbox.py`, `vaccine.py` | Sprint 4 | Controlled-exposure sandbox and baseline/exploit replay |
| `fingerling/capture.py` | — | bpftrace `execve` capture → Tetragon-shaped JSONL |

N-gram analysis is deliberately a later stage: it sees only the fingerprint IDs
`Warehouse.upsert()` returns.

## 2. Architectural Principles

- **Few third-party dependencies.** `PyYAML` and, since Sprint 8, `python-jsonpath` (pure Python, no transitive deps) for full JSONPath syntax. The hand-rolled resolver from the POC is gone. Python's stdlib `http.server` is used for webhook ingestion. Dependencies are declared in `pyproject.toml` and install into a project `.venv` via `make install`.
- **Stable contracts over inferred behavior.** Ambiguities are resolved with explicit parameters.
- **Deterministic and Stable Tokens.** Token shape depends only on how many values a path selects: none → "missing", one → that value, several → each tokenized, deduplicated, sorted and comma-joined.
- **One fold path.** Aggregator state is plain data that is loaded and folded further; a set built over many runs equals one built in a single pass by construction.

## 3. Component Diagram

```mermaid
flowchart TD
    A[Raw JSONL telemetry] --> B[Webhook Server: POST /telemetry]
    B --> C[tokenizer.tokenize]
    C -- Mask Profile --> D[dict: key -> token]
    D --> E[warehouse.upsert]
    E -- fingerprint_id --> F[ringbuffer.push]
    F -- anomaly score --> G{score == 1.0 and warm?}
    G -- yes --> H[policy.compile_policy]
    H --> I[KubeArmorPolicy YAML returned in HTTP response]
    G -- no --> J[Return success response without policy]
```

## 4. Class & Data Structures

### 4.1 `fingerprint_sampler/tokenizer.py` (STORY-FING-01, -07, -23)

```python
@dataclass(frozen=True)
class MaskEntry:
    key: str
    path: str
    modifier: Modifier          # given as a bare name or mapping; normalised in __post_init__

@dataclass(frozen=True)
class Modifier:                 # STORY-FING-36
    name: str
    params: tuple[tuple[str, Any], ...]          # arguments, sorted by name
    @classmethod
    def of(cls, spec: Modifier | str | Mapping) -> Modifier: ...   # validates; ValueError
    @property
    def spec(self) -> str: ...  # bare name, or sorted compact JSON; feeds profile_id
    def __call__(self, value) -> str: ...

def compile_path(path: str) -> jsonpath.JSONPath: ...   # cached; ValueError if empty/invalid
def compile_regex(pattern: str, flags: str = "") -> re.Pattern: ...   # cached; flags from "imsx"
def find_values(record: Any, path: str) -> list[Any]: ...
def validate_modifier(modifier) -> None: ...
def apply_modifier(value, modifier) -> str: ...     # one value
def tokenize_values(values: list, modifier) -> str: ...  # match-count rule
def tokenize(record: dict, mask_profile: list[MaskEntry]) -> dict[str, str]: ...
def parse_jsonl(jsonl_text: str) -> list[dict]: ...
```

Paths use full JSONPath (RFC 9535 plus the `[?(@.x == 1)]` filter form): filters, slices, unions,
negative indexes, recursive descent. Empty/missing matches tokenize to `"FALSE"`/`"NULL"`, never
raising.

### 4.2 `fingerprint_sampler` set, aggregators and profiles (STORY-FING-02, -24, -25); `fingerling/warehouse.py` helpers (-05)

```python
@dataclass(frozen=True)
class AggregateEntry:
    key: str
    path: str
    fns: tuple[str, ...]            # e.g. ("MIN", "MAX", "LAST(3)")

def make_entry(key, path, fns) -> AggregateEntry: ...          # validated
def update(state: dict, entry: AggregateEntry, record) -> int: ...  # returns values skipped

def fingerprint_id(tokens: dict[str, str]) -> str: ...

@dataclass
class FingerprintRecord:
    tokens: dict[str, str]
    total_occurrences: int
    first_seen: str
    last_seen: str
    aggregates: dict[str, dict]     # aggregate key -> {"MIN": .., "AVG": {avg, sum, count}, "LAST": [..]}

class Warehouse:
    def __init__(self, aggregates: Sequence[AggregateEntry] = (), profile_id: str | None = None): ...
    def upsert(self, tokens: dict[str, str], record: Any, timestamp: str | None = None) -> str: ...
    def load(self, path: str, force: bool = False) -> None: ...   # ProfileMismatchError unless force
    def save(self, path: str) -> None: ...                         # temp file + os.replace

TELEMETRY_AGGREGATES   # in fingerling.warehouse: duration_ms MIN/MAX + LAST(3) raw events

@dataclass(frozen=True)
class Profile:
    fields: tuple[MaskEntry, ...]
    aggregates: tuple[AggregateEntry, ...]
    profile_id: str                 # property; MD5 over fields only

def load_profile(path: str) -> Profile: ...   # ProfileError names file + entry

def build_whitelist(records, mask_profile, n, warehouse=None) -> set[tuple[str, ...]]: ...  # in fingerling.warehouse
```

Aggregator state is keyed by function name, so changing `n` in `LAST(n)` keeps collected
samples. Numeric functions accept ints, floats and numeric strings; other values are skipped and
counted in `Warehouse.skipped_values`. The set file is version 1 (`version`, `profile_id`,
`fingerprints`); pre-Sprint-8 files are rejected with a clear error.

### 4.3 `ringbuffer.py` (STORY-FING-03)

```python
class SlidingWindowMatcher:
    def __init__(self, n: int, whitelist: set[tuple[str, ...]]): ...
    @property
    def warm(self) -> bool: ...
    def push(self, fingerprint_id: str) -> float: ...
```

### 4.4 `policy.py` (STORY-FING-04, STORY-FING-06)

```python
def compile_policy(
    workload_name: str,
    match_labels: dict[str, str],
    anomalous_trajectory: str | tuple[str, ...],
    namespace: str = "default",
    action: Literal["Block", "Post"] = "Block",
    block_pattern: str | None = None,
) -> str:
    """Compile KubeArmorPolicy CRD. anomalous_trajectory accepts tuples directly."""
```

### 4.5 `server.py` (STORY-FING-08)

```python
class TelemetryHTTPRequestHandler(BaseHTTPRequestHandler):
    """Handles POST /telemetry requests in-process."""
```
- Ingests JSONL payload batches.
- Invokes the pipeline sequentially.
- Responds with processing statistics and compiled policies.

## 5. Technical Stack

- **Language:** Python 3.14 and later (3.14 and 3.15 tested)
- **Stdlib:** `hashlib`, `dataclasses`, `collections.deque`, `http.server`, `json`, `argparse`
- **Third-party:** `PyYAML`, `python-jsonpath`; `rich` for the parked demo only
- **Tooling:** `uv` (workspace + lockfile), `hatchling`, `ruff`, `gitleaks`, GitHub Actions — see `docs/SDLC.md`
- **Test runner:** `unittest`

## 6. Decisions Log (Sprint 2 additions)

7. **Wildcard & Recursive Descent Path Resolution**: Hand-rolled recursive crawler in `tokenizer.py` to support `[*]` and `..` without adding external JSONPath library overhead.
8. **Token Aggregation Semantics**: Multiple resolved values are tokenized individually, sorted alphabetically, deduplicated, and joined with commas to maintain stable and deterministic tokens.
9. **Aligned Policy API**: The `compile_policy` function now accepts `tuple[str, ...]` directly, resolving the string-joining overhead and aligning it with the output structure of `SlidingWindowMatcher`.
10. **stdlib HTTP Ingestion**: Standard library `http.server` handles `POST /telemetry` to remain fully offline and lightweight.

## 7. Decisions Log (Sprint 8 additions)

11. **Library JSONPath** (supersedes #7): `python-jsonpath` replaces the hand-rolled resolver; full syntax was needed for complex events.
12. **Project venv**: the system Python is externally managed (PEP 668), so dependencies are declared in `pyproject.toml` and installed into an isolated `.venv`, and the Makefile selects it automatically.
13. **Declared aggregators replace hardcoded stats**: `upsert(duration_ms, raw_record)` became `upsert(tokens, record)`; duration bounds and sample ring are now `TELEMETRY_AGGREGATES`.
14. **Profile-bound sets**: a set records the `profile_id` of its `fields`; merging under another profile is refused unless forced.
15. **Sampling tool is independent of sequence analysis**: n-grams/scoring stay a downstream stage.

## 8. Decisions Log (Sprint 9 additions)

16. **Two packages, one repository**: the fingerprint tool is `fingerprint-sampler`, a uv workspace member published on its own; `fingerling` is private and depends on it.
17. **Move behind shims**: parked modules import the old `fingerling.*` paths, which re-export the same objects, so the split changed no parked code.
18. **`fingerprint merge`**: a subcommand, so later commands (`show`, `report`) can be added without breaking users; `fingerling fingerprint` is kept as an alias.
19. **One version stream**: only `fingerprint-sampler` is versioned, tagged (`v<version>`) and published.
