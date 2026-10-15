# Sprint 17 User Stories: Duplicate Protection

*   **Total Points**: 5 (Tier 2)
*   **Branch**: `sprint-17`
*   **Source**: owner, 2026-10-14 in session: "duplicate protection to avoid situations where the tool is run more than once with the same source or from sources that overlap ... a sequenceNumber path ... capture max seq and drop events that are lower". Clarified in session: the path is declared in the profile; events are compared with the mark as it stood at the start of the run; an event with no usable sequence is an error.
*   **Status**: Approved (Smith Gates 1 and 2, 2026-10-14)

## Goal

A user who runs the tool twice over the same file, or over sources that overlap, does not count
the same events twice. A profile can name the field that numbers its events. The set remembers
the highest number merged so far, and later runs drop anything at or below it.

## Assumptions made for the owner

1. "Errs" means a line error, not an aborted run. An event without a usable sequence is reported
   on stderr with its line number, is not merged, counts as a skipped line, and the run exits 1.
   The rest of the run is merged. If you want the whole run to abort instead (nothing written,
   exit 2), say so.
2. An event *equal* to the mark is dropped too, because it is the last event already merged.
   A run over exactly the same source therefore drops everything.
3. Sequences compare as numbers. Numbers and numeric strings (GH Archive's `"id": "34541893465"`)
   are accepted; anything else is "no usable sequence". A path that selects more than one value
   is also an error, because it is ambiguous.
4. Duplicates *inside* one run are not detected, because events are compared with the mark from
   before the run. You chose this to tolerate events that arrive slightly out of order.
5. Dropped events are not an error: if nothing else went wrong, the exit status stays 0.

---

## STORY-FING-49: Declare a sequence in the profile
**Points:** 2

**As a** user writing a profile for a stream whose events carry a sequence number,
**I want** to name that field once in the profile,
**so that** every merge with this profile is protected without my remembering a flag.

### Acceptance Criteria
1. A profile may have a top-level `sequence: <JSONPath>`, for example `sequence: $.id`.
2. `fingerprint check` reports an invalid JSONPath under `sequence` as
   `<profile>: sequence: Invalid JSONPath ...` and exits 1.
3. Adding, removing or changing `sequence` does not change the profile id.
4. The GH Archive example profile declares `sequence: $.id`.

## STORY-FING-50: Drop events that were already merged
**Points:** 3

**As a** user who may run the tool again over the same or overlapping input,
**I want** events already merged to be dropped,
**so that** counts and aggregates are not inflated by duplicates.

### Acceptance Criteria
1. After a run with `sequence: $.id`, the set file has
   `sequence: {path: $.id, max: <highest sequence merged>}`.
2. In the next run, events whose sequence is ≤ the stored `max` are not merged into the set or
   the run file. Example: set max 5, events with ids 3, 5, 6, 8 merge only 6 and 8, and the new
   max is 8.
3. The summary adds `  dropped: <n> events already merged (sequence ≤ <max at start>)` whenever
   the profile has a sequence.
4. An event without a usable sequence prints
   `fingerprint: line <n>: no usable sequence at $.id - skipped`, counts as a malformed line, and
   makes the exit status 1.
5. Running `make gharchive` twice in a row: the second run reads 180,387 events, drops all of
   them, and leaves counts unchanged.
6. If the set's stored `sequence.path` differs from the profile's, the stored mark is ignored,
   stderr says
   `fingerprint: sequence path changed ($.old -> $.new); previous mark ignored`, and a new mark
   is recorded.
7. The run file's `run:` header gains `sequence: {min, max}` for the events this run merged
   (omitted when no event was merged or the profile has no sequence).
8. A profile without `sequence` behaves exactly as before, and a stored mark is left untouched.
9. README, USER_GUIDE and `merge --help` describe `sequence`, the drop rule and the summary line.

---

## Out of Scope
- Detecting duplicates without a sequence (for example by hashing whole events).
- Duplicates within a single run.
- A CLI flag for the sequence path.

## Open Questions
None. (Assumption 1 is the one to check.)

---

## Architecture (Morpheus)

Tier 2: stories and architecture in one document. There is no new dependency or make target,
so there is no Tank Phase 0.

**D1 — Profile.** The schema gains a top-level `"sequence": {"$ref": "#/$defs/text",
"description": ...}`. `Profile` gains `sequence: Path | None = None`, built in `check_profile` with
`Path`. A `ValueError` from it becomes the problem `"<source>: sequence: <reason>"`. `profile_id`
is unchanged because it hashes the fields only.

**D2 — The set's mark.** `FingerprintSet.sequence: dict | None` (`{"path", "max"}`) is saved
after `last_run` and loaded like `last_run`.

**D3 — Filtering in `_fold_stream`.** A small `_Sequencer(path, mark)` helper with a single
method, `check(event) -> int | None | DROP`. It returns the number for an event to keep, `DROP`
for one at or below the mark, and `None` for an event with no usable sequence: zero values,
several values, or a non-number (via `aggregators._as_number`; a bool or a non-finite number is
not usable). It tracks `dropped`, `min` and `max` over the kept events. `_cmd_merge` builds it
from the profile and the loaded set. When the stored path differs, it prints the notice and uses
`mark = None`. After the fold it sets
`fingerprints.sequence = {path, max(mark, run max)}` and the run header's `sequence`.

**D4 — Reporting.** `_report` adds the `dropped:` line when the profile has a sequence. Line
errors reuse the existing `warn()` path, so the cap of 10 listed lines still applies.

**Build environment:** no change.
