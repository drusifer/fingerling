# Sprint 15 User Stories: Shares of the Set

*   **Total Points**: 5 (Tier 2)
*   **Branch**: `sprint-15`
*   **Source**: owner, 2026-10-14, `/sprint add '%'s for all agg values`. Clarified in session: the shares are stored in the set file and also shown by `fingerprint show`, for `SUM` and `COUNT` values (including the built-in count), each as a share of the set total.
*   **Status**: Approved (Smith Gates 1 and 2, 2026-10-14)

## Goal

Someone assessing a fingerprint set can see what share of the whole each fingerprint accounts
for: what percentage of all events it covers, and what percentage of every summed or counted
quantity, for example payload bytes. The shares are in the set file, so any tool can read them,
and in `fingerprint show`, so a person can read them at a glance.

## Assumptions made for the owner

1. A share is `100 × value ÷ total of that value over every fingerprint in the set`, rounded to
   2 decimal places in the file and shown with 1 decimal place in `show`. If you want a different
   precision, this is a one-line change.
2. Only `SUM` and `COUNT` get shares. `AVG`, `MIN`, `MAX`, `FIRST` and `LAST` do not add up across
   fingerprints, so a share of them would mean nothing (your answer, 2026-10-14).
3. When a value's total is 0, no share is stored, and `show` prints `-`, because there is nothing
   to divide by.
4. A set file written before this sprint has no shares until its next merge, and `show` prints
   `-` for them. There is no backwards compatibility before 1.0.

---

## STORY-FING-46: Shares stored in the set file
**Points:** 3

**As a** user or tool reading a fingerprint set,
**I want** each fingerprint to record its share of every `SUM` and `COUNT` total,
**so that** I can tell which fingerprints dominate without adding up the whole file myself.

### Acceptance Criteria
1. After a merge, each fingerprint has a `share` section with the same layout as the values it
   describes. `share.meta.count` is its percentage of all events in the set. Under
   `share.aggregates`, a single-function aggregate stores its share directly
   (`requests: 25.0`); a multi-function aggregate stores a map of its `SUM` and `COUNT` shares
   (`payload_bytes: {SUM: 31.25}`).
2. Example: three events with sizes 10 and 30 (kind `a`) and 60 (kind `b`), under
   `{key: size, path: $.size, fn: [SUM, MAX]}`, give `a` the shares `meta.count: 66.67` and
   `aggregates.size: {SUM: 40.0}`, and give `b` the shares `33.33` and `{SUM: 60.0}`. `MAX` has
   no share.
3. Shares are recomputed on every write, so they always describe the whole set as written,
   including after a merge into an existing set and with `-o`.
4. An aggregate whose total is 0, or which no fingerprint has a value for, has no share entry.
5. Loading and re-merging a set never treats the stored shares as input. Shares do not change the
   counts or the aggregates.
6. The README section on the fingerprint set describes `share`.

## STORY-FING-47: Shares in `fingerprint show`
**Points:** 2

**As a** user reading a set,
**I want** `show` to print each fingerprint's shares next to its values,
**so that** I can see at a glance which fingerprints carry most of the events and the data.

### Acceptance Criteria
1. `show` prints `COUNT %` right after `COUNT`. After `LAST SEEN`, it prints one value column and
   one `%` column for every shared value in the set, in profile order: `size.SUM`, `size.SUM %`
   for a multi-function aggregate, and `requests`, `requests %` for a single-function one. Token
   columns come last.
2. Percentages are printed with 1 decimal place (`66.7`). A missing value or share is printed as
   `-`.
3. Rows are still sorted by `COUNT`, highest first.
4. A set written before this sprint, with no shares, shows `-` in every `%` column and no
   aggregate columns. It does not fail.
5. `show --help` and the README describe the new columns.

---

## Out of Scope
- `show --sort KEY` and `--top N` (backlog).
- Shares of `AVG`, `MIN`, `MAX`, `FIRST` and `LAST`.
- Shares across several set files.

## Open Questions
None.

---

## Architecture (Morpheus)

Tier 2: stories and architecture in one document. There is no new dependency or make target,
so there is no Tank Phase 0.

**D1 — The `share` field on `Fingerprint`.** Add
`share: dict[str, Any] = field(default_factory=dict)` as the last field, so a record serialises as
`tokens`, `aggregates`, `meta`, `share`. It is derived data: `load` accepts it, the way it accepts
the other fields, and `save` overwrites it.

**D2 — Computed in `FingerprintSet.save`.** Before dumping, `_compute_shares()` walks
`(section, aggregates)` over `("meta", builtin_aggregates())` and
`("aggregates", self._aggregates)`. For each aggregate and each of its functions named `SUM` or
`COUNT`, it reads the value with the same layout rule as `Aggregate` (direct when the aggregate
has one function, `[fn.name]` otherwise), sums the numeric values across records, and writes
`round(100 * value / total, 2)` into `record.share[section]`, at the same position. A total of 0
writes nothing. A small accessor `Aggregate.value(states, function)` is extracted from the
existing `_state` logic so the layout rule lives in one place. It returns `None` when the value
is absent.

**D3 — Where the profile's aggregates come from.** `merge` builds the set with the profile's
aggregates, so its shares are complete. A set constructed with no aggregates (as `show` does)
never writes, so it cannot erase the stored shares.

**D4 — `show` reads stored shares and recomputes nothing.** The columns come from the union of
share paths across records, `meta.count` first and then `share.aggregates` keys in the order
they first appear (profile order, because records are written in that order). Each column's
value is read from the same path under `meta`/`aggregates`. The header is `<key>` for a direct
value and `<key>.<FN>` for a mapped one, followed by `<header> %`. `COUNT %` sits right after
`COUNT`. Percentages are formatted with `f"{share:.1f}"`; anything missing is printed as `-`.

**D5 — Format.** The set format changes (it gains a field) but stays `version: 0`, per the
owner's rule. A line in `docs/DECISIONS.md` records the change.

**Build environment:** no change.
