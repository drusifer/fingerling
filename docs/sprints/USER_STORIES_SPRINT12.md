# Sprint 12 User Stories: Domain Model and Consolidated Validation

*   **Total Points**: 13 (Tier 1 — the owner invoked `/sprint`; FING-41 added mid-sprint)
*   **Branch**: `sprint-12`
*   **Source**: Owner, 2026-10-14 (`/sprint refactor …`, plus "Input is strictly jsonl. do we have a
    domain model?" and the answer "Move whole module out" for the tokenizer). Logged in `agents/CHAT.md`.
*   **Status**: Gates 1 and 2 approved (Smith, 2026-10-14)

## Goal

fingerprint-sampler gets an explicit domain model in which every configurable piece validates
itself through one mechanism, so there is one way to define, check and extend a modifier or an
aggregate function. The eBPF-era tokenizer leaves the published package. Code that exists only
for compatibility or that nothing uses is deleted. Qualitative lints show where the smells are,
and the sprint ends with them resolved.

## Assumptions made for the owner

1. **No backwards compatibility** (standing rule): profiles, the Python API and command names
   may change; nothing is migrated. No release (mainline development).
2. **Aggregate functions use the modifier convention**: a bare name (`MIN`) or a mapping
   (`{name: LAST, n: 3}`). This removes the last string mini-language (`"LAST(3)"`).
   Wrong → keep `"LAST(3)"`; it costs one extra parser.
3. **Set files keep their on-disk layout** (`total_occurrences`, `first_seen`, …). Renaming
   fields on disk buys nothing.
4. **Input is strictly JSONL** (owner): no input abstraction, readers or formats.
5. **Lints are a report, not a gate**: `make quality` shows where to look; Trin uses it at UAT.
   The parked `fingerling` code is excluded, as the SDLC exempts it from new gates.

---

## STORY-FING-38: Qualitative lint report
**Points:** 2 · **Owner:** Tank

**As** the QA lead,
**I want** one command that lists complexity, dead code and smell findings for the published package,
**so that** refactoring targets come from evidence, not taste.

### Acceptance Criteria
1. `make quality` runs extended ruff rules (complexity, simplification, refactor, returns,
   unused arguments, boolean traps), `vulture` (dead code) and `radon cc` (complexity grade C or
   worse) over `packages/fingerprint-sampler/src`, and always exits 0.
2. The tools are dev dependencies installed by `make install`; the SDLC lists the target.
3. Trin posts the baseline findings before Phase 1 starts.

## STORY-FING-39: One domain model, one way to validate
**Points:** 5

**As** a maintainer of fingerprint-sampler,
**I want** profile pieces to be objects that build and check themselves the same way,
**so that** adding or changing a modifier or aggregate function touches one class.

### Acceptance Criteria
1. Every modifier and every aggregate function is a class; each is built from a bare name or a
   mapping, its structure is checked by the JSON Schema, and only checks a schema cannot express
   live in the class.
2. There is no string-argument parsing anywhere in the package: `fn: [MIN, {name: LAST, n: 3}]`
   works and `fn: "LAST(3)"` is refused by `fingerprint check` with a located message.
3. `fingerprint check` output and exit codes are unchanged for every case in the Sprint 11 tests
   other than aggregate functions.
4. The `tokenizer` module is gone from fingerprint-sampler; `fingerling` holds the eBPF-facing
   `tokenize` and `parse_jsonl`, built on fingerprint-sampler's field model, and the parked tests pass.
5. Fingerprints for the same profile and events are identical to before (same ids, same tokens).

## STORY-FING-40: Smells and dead weight removed
**Points:** 3

**As** a maintainer,
**I want** the code that only existed for compatibility, or that nothing uses, deleted, and the
worst-graded functions simplified,
**so that** there is less to read and change.

### Acceptance Criteria
1. Gone: the `fingerling` re-export shims, the `fingerling fingerprint` alias, the
   `fingerprint-sampler` console-script alias, and every public name `vulture` reports unused.
2. `make quality` reports no function graded C or worse and no dead code in the package; any
   remaining extended-ruff finding is listed in the sprint record with the reason it stays.
3. `fingerprint merge` behaviour (output, exit codes, files written) is unchanged.

## STORY-FING-41: Smoke suite for the installed tool
**Points:** 3 · **Owner:** Trin (tests), Tank (target) · added mid-sprint at the owner's request

**As** the owner,
**I want** the checks agents were running by hand — install the wheel, run the commands, try the
README — to be a test suite behind one make target,
**so that** they are repeatable and nobody needs ad hoc commands to know the tool works.

### Acceptance Criteria
1. `make smoke` builds the wheel, installs it into a throwaway environment with no project
   checkout on the path, and runs the smoke tests there; it fails if any test fails.
2. The suite runs the installed `fingerprint` command: `--version` matches the package version;
   `check` passes every shipped example profile; an invalid profile gives exit 1 from `check`
   and exit 2 from `merge` with nothing written.
3. The README is executed: the Quickstart shell block runs and prints exactly the output block
   shown under it; every `python` block runs without error; every YAML block that is a whole
   profile passes `fingerprint check`.
4. The SDLC lists `make smoke` as a gate before handoff to Trin and at sprint close.

---

## Out of Scope
- Event-time timestamps, `fingerprint show`, new modifiers.
- Refactoring the parked `fingerling` modules beyond what the tokenizer move requires.
- Turning the lint report into a gate.

## Open Questions
None.

---

## Architecture (Morpheus)

### Domain model

```
Event        one JSON object from one JSONL line (plain dict; input is strictly JSONL)
Profile      fields: [Field]  +  aggregates: [Aggregate]          → profile_id
  Field      key, Path, Modifier          → token(event) -> str
  Aggregate  key, Path, [Aggregator]      → update(state, event) -> skipped
  Path       compiled JSONPath            → values(event) -> list
  Modifier   Default | IsPresent | IsNull | InRange | Any | Glob | Regex | RegSub
  Aggregator Sum | Min | Max | Avg | Last
FingerprintSet  profile_id, {id: Fingerprint}   ← Warehouse renamed
  Fingerprint   tokens, total_occurrences, first_seen, last_seen, aggregates  ← FingerprintRecord renamed
```

**D1 — `Rule`, the one validation mechanism.** `Modifier` and `Aggregator` subclass `Rule`.
A subclass declares `name` and its argument fields (a frozen dataclass), and registers itself
by `name` (`__init_subclass__`). `Rule.build(spec)` takes a bare name or mapping, validates it
against the schema definition for that family (`modifier` / `aggregator`), constructs the
subclass, then calls `check()` — the per-class hook for what a schema cannot express (regex
compiles, `low <= high`). Errors are `ValueError`s. No other construction path exists.

**D2 — Profile checking walks objects.** `check_profile`: schema over the whole document
(unchanged); then build each `Field` and `Aggregate`, collecting each `ValueError` with its
location; then duplicate keys. The per-section branching collapses into one loop over
`("fields", Field), ("aggregates", Aggregate)`.

**D3 — Behaviour on the objects, not in switch statements.** `Modifier.token(value)`,
`Aggregator.update(state, value)` and `Aggregator.wants_numbers` replace `_MODIFIERS`,
`_fold_number`, `parse_fn` and the `if name == …` chains. Set-file state stays keyed by
function name.

**D4 — Module layout.** `fingerprint_sampler/model.py` (Path, Rule, Modifier family, Field),
`aggregators.py` (Aggregator family, Aggregate), `profile.py`, `fingerprint_set.py`
(`warehouse.py` renamed), `schema.py`, `cli.py`. `tokenizer.py` moves to `fingerling/` as
`tokenize(record, fields)` and `parse_jsonl` over `fingerprint_sampler.Field`; `MaskEntry` is
replaced by `Field`.

**D5 — YAGNI cuts.** Delete: `fingerling/{aggregators,profile,cli}.py` shims and the
`fingerling fingerprint` command; `merge_main`, `default_prog` and the alias parser; the
`fingerprint-sampler` script; `apply_modifier`, `validate_modifier`, `tokenize_values`,
`PROFILE_VERSION`. `Warehouse.load(path, force)` becomes keyword-only `force`.

**D6 — Smell targets from the baseline** (radon): `_cmd_merge` D(21) → split into
load-profile / open-set / fold / report steps; `check_profile` C(15) → D2; `Warehouse.load`
C(14) → separate parsing from validation; `aggregators.update` C(11) → D3.

**D7 — Build environment.** Dev dependencies `vulture` and `radon` and target `make quality`
are a mechanism change: Tank, Phase 0. No runtime dependency changes.

**D8 — Smoke suite (FING-41).** `packages/fingerprint-sampler/smoke/test_smoke.py`, stdlib
`unittest` only, outside `tests/` so `make test` does not pick it up. `make smoke` depends on
`build` and runs `uv run --isolated --no-project --with dist/*.whl python -m unittest discover`
on it, so the code under test is the installed wheel, not the source tree. README blocks are
found by their fences under a heading; output comparison is exact. Mechanism change (target, SDLC
gate): Tank.
