# Sprint 13 User Stories: Fingerprint UX

*   **Total Points**: 5 (Tier 2)
*   **Branch**: `sprint-13`
*   **Source**: owner chose "Fingerprint UX" from the backlog on 2026-10-14 (`/sprint resume`); items from `task.md` Backlog and Smith's Sprint 8 and 11 findings
*   **Status**: Approved (Smith Gates 1 and 2, 2026-10-14)

## Goal

Someone who has built a fingerprint set can read it without opening the YAML file, can trust the
"skipped" count in the merge summary, and gets a clear error when they write a modifier that
needs arguments as a bare name. These are the three rough edges seen most often when the tool is
run on real data such as GH Archive.

## Assumptions made for the owner

1. `fingerprint show` prints a plain-text table to stdout and has no options in this sprint. If you
   want sorting, filtering or JSON output, they become backlog items.
2. A path that selects nothing in an event is normal, because not every event carries every
   field, so it no longer counts as skipped. Only a value that is present but cannot be used is
   counted. If you want absent paths reported, they go on a separate line.
3. Long token values in the table are not truncated. You can pipe the output to `less -S`.

---

## STORY-FING-42: See what is in a fingerprint set
**Points:** 3

**As a** user who has merged events into a set,
**I want** to print a table of its fingerprints,
**so that** I can see what was found, and how often, without reading the YAML.

### Acceptance Criteria
1. `fingerprint show web.fingerprints.yaml` prints one header row and then one row per
   fingerprint, with the columns `ID` (the first 8 characters of the fingerprint ID), `COUNT`,
   `FIRST SEEN`, `LAST SEEN`, then one column per token key in alphabetical order.
2. Rows are sorted by `COUNT`, highest first. Ties keep the order of the file.
3. Times are shown as `YYYY-MM-DD HH:MM:SS` in UTC.
4. Columns are aligned with spaces, and the exit status is 0.
5. A set with no fingerprints prints `<SET>: no fingerprints` and exits 0.
6. A missing file, or a file that is not a fingerprint set, prints
   `fingerprint: cannot use set file: <reason>` to stderr, prints nothing to stdout, and exits 2.
   The file is not modified.
7. `fingerprint show --help` describes the command and shows an example. `fingerprint --help`
   lists `show`.

## STORY-FING-43: A "skipped" count that means something
**Points:** 1

**As a** user reading the merge summary,
**I want** the skipped count to include only values that could not be used,
**so that** a non-zero number points to a real problem in my data or profile.

### Acceptance Criteria
1. An event where an aggregate's path selects nothing adds 0 to the count. For example, merging
   `{"size": 5}` and `{}` with `{key: size, path: $.size, fn: SUM}` reports
   `0 unusable aggregate values`.
2. A present value that a function cannot use still counts. For example, `{"size": "big"}` with
   `SUM` reports `1 unusable aggregate values`.
3. A value that does not convert to the declared `type` still counts.
4. The summary line reads `  skipped: <n> malformed lines, <m> unusable aggregate values`.
5. The README and USER_GUIDE examples show the new wording.

## STORY-FING-44: Clear error for a modifier written without its arguments
**Points:** 1

**As a** user writing a profile,
**I want** `modifier: GLOB` (or `REGEX`, `REGSUB`, `IN_RANGE`, `ANY`, `TRUNC`, or `fn: FIRST`
or `fn: LAST`) to be reported as needing arguments,
**so that** I know how to fix it instead of being told it is not one of three other names.

### Acceptance Criteria
1. `fingerprint check` on a field with `modifier: GLOB` prints
   `<profile>: fields[0] (key 'x') → modifier: GLOB needs arguments (pattern); write it as {name: GLOB, pattern: ...}`
   and exits 1.
2. The same holds for every rule that needs arguments, and names all its required arguments.
   For example, `IN_RANGE` names `low, high`, and `fn: LAST` names `n`.
3. An unknown bare name such as `modifier: GLOBB` is reported as it is today: it is not one of
   the allowed names.
4. `fingerprint merge` with such a profile writes nothing and shows the same message, as it does
   for every other profile problem.

---

## Out of Scope
- Options for `show`: sorting, filtering, aggregate columns, JSON or CSV output, a detail view of
  one fingerprint.
- A JSON Schema for set files.
- Event-time timestamps and merging one set into another.

## Open Questions
None.

---

## Architecture (Morpheus)

Tier 2, so stories and architecture are in one document. No new dependency, language or make
target, so there is no Tank Phase 0.

**D1 — `show` lives in `cli.py`.** It adds a `show` subparser with one positional `SET` and a
`_cmd_show` that loads the set with `FingerprintSet().load(path)`. With no `profile_id`, the
mismatch check does not apply, so no profile is needed. `FingerprintSetError` and `OSError` map to
`fingerprint: cannot use set file: <reason>` and exit 2, the same text `merge` uses. The table
is built by one small helper, `_table(rows) -> str`, which pads each column to its widest cell.
No library is used.

**D2 — Reading the built-in metadata.** `COUNT`, `FIRST SEEN` and `LAST SEEN` come from
`Fingerprint.meta` (`count`, `first_seen`, `last_seen`). A set loaded from YAML may hold these as
`datetime` objects or as ISO strings, so one helper normalises both to UTC
`YYYY-MM-DD HH:MM:SS`. A missing value shows as `-`. Token columns are the sorted union of token
keys across the set, and a fingerprint without a key shows `-`.

**D3 — The skipped count.** In `Aggregate.update`, a path that selects nothing returns `0`
instead of `1`. Nothing else changes: the type-conversion and `accept`-SKIP counts stay. The
`_report` wording becomes `unusable aggregate values`. Message wording is not a format, so this is
not a breaking change.

**D4 — Rules that need arguments.** `schema.schema_errors` stays the single source of schema
messages. When an `enum` error's instance is a string that the same definition's mapping form
accepts as `name`, the message is replaced by
`<NAME> needs arguments (<required>); write it as {name: <NAME>, <first required>: ...}`. The
required list is read from the schema's `if name == X then required` entry, so new rules get the
message without code changes. This covers both `modifier` and `aggregator`, and it reaches both
`check_profile`, which validates the whole profile, and `Rule.build`.

**Build environment:** no change.
