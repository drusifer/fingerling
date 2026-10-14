# Sprint 16 User Stories: Run History

*   **Total Points**: 3 (Tier 2)
*   **Branch**: `sprint-16`
*   **Source**: owner, 2026-10-14, `/sprint time to add history - keep this light weight`. Clarified in session: files go in `<set>.history/` beside the set; history is always on; `-o` stays for now, may be revisited, and writes no history.
*   **Status**: Approved (Smith Gates 1 and 2, 2026-10-14; Gate 1 after one revision)

## Goal

Every merge leaves behind a small file holding just that run's fingerprints, next to the primary
set, which keeps growing as before. You can then look back at what a single run saw (for example,
what was new or heavy in one hour of events) without any new tooling: a run file is a fingerprint
set, so `fingerprint show` reads it.

## Assumptions made for the owner

1. Each run file starts with a short `run:` header: when the run started and finished (UTC), where
   the events came from, how many events were read and lines skipped, and which set the run was
   merged into. Without it, the only run information is the timestamp in the file name.
2. Run files are never pruned or rotated in this sprint. If they pile up, retention is a later
   story.
3. A run that writes nothing (exit 2, or interrupted) leaves no run file, because the primary set
   did not change either.
4. If the set is written but its run file cannot be, the run is reported with a new exit status 3
   and a message, rather than failing silently. The set is not rolled back.
5. Shares in a run file are relative to that run alone.

---

## STORY-FING-48: A file per run beside the set
**Points:** 3

**As a** user who merges events into a set over time,
**I want** each run's own fingerprints kept in a separate file,
**so that** I can see what any single run contributed after it has been folded into the set.

### Acceptance Criteria
1. `fingerprint merge -p app.yaml -s data/app.fingerprints.yaml events.jsonl` updates
   `data/app.fingerprints.yaml` as before, and also writes
   `data/app.fingerprints.history/<UTC start time>.yaml`, named like `2026-10-14T193005Z.yaml`.
   The directory is created if it is missing. If the set file has no extension, the directory is
   `<set>.history/`.
2. The run file is a fingerprint set (`version: 0`, same `profile_id`) that contains only the
   fingerprints seen in this run, with counts, aggregates, metadata and shares computed from this
   run's events only. `fingerprint show` reads it.
3. The run file has a `run:` header after `profile_id`:
   `{started, finished, source, events, skipped_lines, set}`. `source` is the events file, or
   `stdin`.
4. Two runs that start in the same second do not overwrite each other: the second file is named
   `...Z_2.yaml`, the next `...Z_3.yaml`, and so on, so names still list in run order (`_` sorts
   after `.yaml`; `-` would sort before it — found in UAT, revised from `-2`).
5. The summary on stderr adds the line `  history: <path of the run file>`.
6. With `-o`, no run file is written. A run that exits 2 or is interrupted writes no run file.
7. A run where no event was read (for example, an empty input) still writes a run file with no
   fingerprints. Such a run still happened.
8. If the run file cannot be written (for example, the history path is a regular file), the set
   is still updated, stderr says `fingerprint: <set> updated, but history not written: <reason>`,
   and the exit status is 3. Status 3 takes precedence over 1 (lines skipped), because a missing
   run file is the bigger surprise.
9. The README, USER_GUIDE and `merge --help` describe the history directory, the run header and
   exit status 3.

---

## Out of Scope
- Pruning or rotating history, and switching it off. History is always on.
- Comparing two runs, or merging run files back into a set (set-to-set merge is on the backlog).
- Any change to `-o` (it may be revisited later).

## Open Questions
None.

---

## Architecture (Morpheus)

Tier 2: stories and architecture in one document. There is no new dependency or make target,
so there is no Tank Phase 0.

**D1 — The run is a second `FingerprintSet`.** `_cmd_merge` creates
`run = FingerprintSet(profile.aggregates, profile.profile_id)` alongside the primary set.
`_fold_stream` upserts every event into both, with one timestamp per event
(`datetime.now(UTC).isoformat()`, computed once and passed to both), so `meta` times agree. The
memory cost is at most one more copy of the fingerprints this run touched.

**D2 — The run header is a set attribute.** `FingerprintSet` gains `run: dict | None = None`.
`save` writes it between `profile_id` and `fingerprints` when it is set. `load` ignores the key,
so `show` and `merge` read run files like any set. The set format stays `version: 0`.

**D3 — Paths and naming live in `cli.py`.** `_history_path(set_path, started)` returns
`<set without its last extension>.history/<YYYY-MM-DDTHHMMSSZ>.yaml`, adding `_2`, `_3`, ... while
the name is taken. It creates the directory with `os.makedirs(exist_ok=True)`. The file is
written with `FingerprintSet.save`, which is already atomic.

**D4 — Order and failure.** The primary set is saved first; only then is the run file written.
An `OSError` from the history step is caught: `_cmd_merge` prints the message from AC8, still
prints the summary, and returns the new `EXIT_HISTORY_NOT_WRITTEN = 3`. The new exit status is
documented in the epilog.

**D5 — `-o` and failures.** With `args.output` set, the history step is skipped. A
`_NotWritten` or `KeyboardInterrupt` returns before the history step, as today.

**Build environment:** no change.
