# Sprint 14 User Stories: Weighted Aggregates

*   **Total Points**: 2 (Tier 2)
*   **Branch**: `sprint-14`
*   **Source**: owner, 2026-10-14 in session: "weighted aggregates something like SUM(SIZE(payload)) for quantitative assessment of the fingerprint set". The design (an `op` on the aggregate, not a parameter of `SUM`) was agreed in the same conversation.
*   **Status**: Approved (Smith Gates 1 and 2, 2026-10-14)

## Goal

Someone assessing a fingerprint set can weigh each fingerprint by the volume of data it carries,
not only by how often it occurs, for example the total, average and largest payload size in
bytes. One aggregate entry gives every function the measured value, so `SUM`, `AVG` and `MAX` of
the size come from one line of profile.

## Assumptions made for the owner

1. A string's size is its UTF-8 byte length. Any other value (object, array, number, boolean,
   null) is measured as the UTF-8 byte length of its compact JSON (`null` is 4). If you want
   another measure, such as element count, it becomes a separate op (`LEN`) later.
2. `op` and `type` cannot be used together on the same aggregate. Measuring a date has no meaning,
   so the combination is rejected rather than given a silent order. If a future op needs both,
   this rule is revisited then.

---

## STORY-FING-45: Aggregate the size of a value
**Points:** 2

**As a** user assessing a fingerprint set,
**I want** to aggregate the size in bytes of what a path selects,
**so that** I can see which fingerprints carry the most data, not just the most events.

### Acceptance Criteria
1. The aggregate `{key: payload_bytes, path: $.payload, op: SIZE, fn: [SUM, AVG, MAX]}` over the
   events `{"payload": "héllo"}` and `{"payload": {"a": 1}}` stores `SUM: 13`, `MAX: 7` and an
   `AVG` of `6.5`. `"héllo"` is 6 bytes in UTF-8, and `{"a":1}` is 7.
2. `op: SIZE` works with every aggregate function. For example, `fn: {name: LAST, n: 2}` keeps the
   last two sizes.
3. An event where the path selects nothing adds nothing and is not counted as skipped. A null
   value measures 4.
4. `fingerprint check` on `op: BOGUS` reports
   `<profile>: aggregates[0] (key 'x') → op: 'BOGUS' is not one of ['SIZE']` and exits 1.
5. `fingerprint check` on an aggregate with both `op` and `type` reports a problem located at
   that aggregate and exits 1. `merge` with such a profile writes nothing.
6. Adding, removing or changing `op` does not change the profile id, so an existing set keeps
   merging, as with every other aggregate change.
7. The README and USER_GUIDE document `op: SIZE`, and the GH Archive example profile tracks
   payload bytes per fingerprint.

---

## Out of Scope
- Other ops (`LEN`, `ABS`, ...) and ops on fields.
- A weighted total across the whole set, and `show` columns for aggregates. The per-fingerprint
  `SUM` is stored in the set file.

## Open Questions
None.

---

## Architecture (Morpheus)

Tier 2: stories and architecture in one document. There is no new dependency or make target,
so there is no Tank Phase 0.

**D1 — `Op` is a new Rule family.** `Op(Rule)` has `family = "op"` and the method
`apply(value) -> Any`. It lives in `aggregators.py`, next to `Aggregator`, because only aggregates
use it. `Size(Op)` has `name = "SIZE"`: for `str` it returns `len(value.encode("utf-8"))`;
otherwise it returns the byte length of
`json.dumps(value, separators=(",", ":"), ensure_ascii=False)`. Set data comes from JSON, so
every value can be serialised.

**D2 — Schema.** A new `$defs.op` is defined as `{"enum": ["SIZE"]}`, with a description. Like
`valuetype`, it takes bare names only; if an op ever takes arguments, it moves to the
mapping form that `modifier` uses. `aggregate.properties.op` refers to it. The rule that forbids
`op` and `type` together is a `"not": {"required": ["op", "type"]}` on `aggregate`, with a
description saying why. Phase 1's needs-arguments message is unaffected, because the enum here
is not under `then`.

**D3 — `Aggregate.op`.** The field is `op: Op | None = None`, built in `__post_init__` with
`Op.build`, the same way `type` is. In `update`, the selected values pass through
`op.apply` when `op` is set, and through `typed_values` otherwise; the schema makes the two
exclusive. The rest of `update` is unchanged, so skip counting, state layout and
merge-continuation behave as before.

**D4 — Docs and example.** The README "Profiles" aggregate section and the USER_GUIDE gain one
`op` paragraph and an example. `examples/gharchive.yaml` gains
`{key: payload_bytes, path: $.payload, op: SIZE, fn: [SUM, AVG, MAX]}`. The existing test
that every example passes the schema covers it.

**Build environment:** no change.
