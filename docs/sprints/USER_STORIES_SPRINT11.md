# Sprint 11 User Stories: Structured Modifiers and Profile Checking

*   **Total Points**: 8 (Tier 2 — fast-track: stories and architecture in one document)
*   **Branch**: `sprint-11`
*   **Source**: Owner, 2026-10-13, in session after the GLOB/REGEX/REGSUB change ("lets simplify…
    leverage yaml for arg parsing", "no to keeping the string form", "use latest python",
    "include a yamlschema validator … don't roll your own", "make it so"). Logged in `agents/CHAT.md`.
*   **Status**: Gate 1 approved (Smith, 2026-10-13)

## Goal

A profile author writes modifier arguments as ordinary YAML instead of a mini-language inside a
string, so patterns need no special quoting rules. A mistake anywhere in a profile is reported
by a standard schema validator, with every problem and its location listed at once, through a
command the author can run before feeding any events. The tool targets current Python only.

## Assumptions made for the owner

1. **Python floor is 3.14; 3.14 and 3.15 are tested.** "Latest" is 3.15.0, about two weeks old;
   a 3.15 floor would also be fine if every dependency installs on it. Wrong → raise the floor
   in Phase 0, a one-line change.
2. **Modifiers without arguments keep the bare name** (`modifier: IS_PRESENT`); every modifier
   with arguments, including `IN_RANGE` and `ANY`, is mapping-only. Recommended on 2026-10-13
   and accepted with "make it so".
3. **Breaking the profile format is free now**: nothing has been published (`v0.1.0` was never
   pushed). Release is `0.2.0`.
4. **Aggregate functions keep their current form** (`fn: [MIN, MAX]`, `fn: "LAST(3)"`); the
   request was about modifiers. The schema still checks them.

---

## STORY-FING-35: Current Python only
**Points:** 2 · **Owner:** Tank

**As** the project owner,
**I want** the project to require and test only current Python,
**so that** the code can use current language and `re` features without compatibility work.

### Acceptance Criteria
1. Both manifests declare `requires-python = ">=3.14"`; the published package's classifiers
   list 3.14 and 3.15 only.
2. `make test-all` and the CI matrix run on 3.14 and 3.15, and pass.
3. `make install` from clean builds the environment on 3.14 (`.python-version`).
4. Installing on an older Python is refused by the installer with its normal
   "requires a different Python" message (nothing project-specific to build).
5. `docs/SDLC.md` sections 1, 3 and 8 say the same, with the change recorded in
   `docs/DECISIONS.md`.

## STORY-FING-36: Modifier arguments as YAML
**Points:** 3

**As** a profile author,
**I want** to give a modifier its arguments as named YAML keys,
**so that** a regular expression or a list of values is written exactly as it is, with no
second layer of quoting.

### Acceptance Criteria
1. A field's `modifier` is either the bare name of a modifier without arguments (`DEFAULT`,
   `IS_PRESENT`, `IS_NULL`) or a mapping with `name` plus that modifier's arguments:
   `IN_RANGE` `low`, `high` · `ANY` `values` (a non-empty list) · `GLOB` `pattern` ·
   `REGEX` `pattern`, optional `flags` · `REGSUB` `pattern`, `replace`, optional `flags`.
2. `flags` is any combination of the letters `i m s x` (ignore case, multi-line, dot matches
   newline, verbose). `{name: REGEX, pattern: '^hello', flags: i}` gives `TRUE` for `"HELLO world"`.
3. Tokens are the same as before for the same arguments: e.g. `{name: REGSUB, pattern: '\d+',
   replace: N}` turns `/items/17` into `/items/N`; `{name: IN_RANGE, low: 200, high: 399}` on 404
   gives `FALSE`.
4. A string with arguments (`"IN_RANGE(200, 399)"`) is refused at load time with a message that
   shows the mapping form to use instead.
5. The example profiles, both READMEs and the user guide use only the new form.
6. A profile whose fields use only bare-name modifiers has the same profile id as before.

## STORY-FING-37: Check a profile before using it
**Points:** 3

**As** a profile author,
**I want** `fingerprint check PROFILE` to list every problem in my profile with where it is,
**so that** I can fix them all in one pass, before any events are read.

### Acceptance Criteria
1. `fingerprint check good.yaml` prints `good.yaml: OK` and exits 0.
2. For an invalid profile it prints one line per problem — file, location (e.g.
   `fields[2] (key 'route') → modifier`) and what is wrong — and exits 1. Two separate
   mistakes give two lines.
3. Structure is checked by a published JSON Schema through a standard validator library,
   not hand-written checks. What a schema cannot express — a regex or JSONPath that does not
   compile, `low` above `high`, a duplicate key — is reported in the same format.
4. `fingerprint merge` runs the same check first; an invalid profile writes nothing and exits 2,
   listing the same problems.
5. A YAML syntax error is reported with its line and column, exit 1.
6. The README shows how to point an editor at the schema
   (`# yaml-language-server: $schema=…`) for checking while typing; the example profiles carry
   that line.

---

## Out of Scope
- A string shorthand for modifiers with arguments (rejected by the owner).
- Changing how aggregate functions are written.
- Migrating fingerprint sets built with an old profile (none exist outside this repository).
- Publishing the schema to SchemaStore.

## Open Questions
1. Floor 3.14 vs 3.15 — owner; 3.14 assumed (see Assumptions 1).

---

## Architecture (Morpheus)

**D1 — Python.** `requires-python = ">=3.14"` in both manifests; `.python-version` 3.14;
`PYTHONS := 3.14 3.15`; CI matrix `["3.14", "3.15"]`; ruff `target-version = "py314"`.
Mechanism-class change: Tank, approved by the owner on 2026-10-13.

**D2 — Validator.** Runtime dependency `jsonschema` (Draft 2020-12). Chosen over
`fastjsonschema` for its error messages and paths, which are the point of AC 37.2. Brings
`attrs`, `referencing`, `rpds-py`; Phase 0 confirms they install on 3.14 and 3.15.

**D3 — Schema.** `fingerprint_sampler/profile.schema.json`, shipped in the wheel, loaded with
`importlib.resources`. A modifier is `if string then enum[DEFAULT, IS_PRESENT, IS_NULL] else
mapping`; the mapping selects its argument rules with one `if {name: const X} then {…}` per
modifier, each with `required` and `additionalProperties: false`. No `oneOf`/`anyOf` on
modifiers: they produce "not valid under any of the given schemas" instead of the real reason.
A string containing `(` gets its own rule whose message shows the mapping form (AC 36.4).

**D4 — Two-layer check, one report.** `profile.check_profile(data, source) -> list[str]`:
schema errors first (all of them, sorted by location); only if the structure is valid, the
semantic checks the schema cannot express — JSONPath compiles, Python regex compiles with its
flags, REGSUB replacement is valid, `low <= high`, duplicate keys, aggregate functions. Each
message is `source: location: problem`. `parse_profile` raises `ProfileError` carrying the
list; the hand-written structural checks in `profile.py` are deleted.

**D5 — Modifier object.** `tokenizer.Modifier` (frozen, hashable): `name` + sorted `params`;
callable on a value; `spec` is the canonical text used by `profile_id` — the bare name for
argument-free modifiers (keeps AC 36.6), otherwise compact sorted JSON. `MaskEntry.modifier`
accepts a string or mapping and is normalised to a `Modifier` in `__post_init__`. The string
argument parser (`_parse_modifier`, `_split_args`) is deleted.

**D6 — CLI.** New subcommand `check PROFILE [PROFILE…]`: exit 0 all valid, 1 any invalid.
Problems go to stdout (they are the command's output), `OK` lines too. `merge` keeps exit 2 and
stderr.

**D7 — Editor hint.** Example profiles start with
`# yaml-language-server: $schema=<raw GitHub URL of the schema on main>`; README documents it.
Works once the owner pushes `main`.
