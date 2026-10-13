"""Telemetry-side helpers around the fingerprint set.

The fingerprint set itself (`Warehouse`, `FingerprintRecord`, `fingerprint_id`)
lives in the `fingerprint_sampler` package and is re-exported here. What stays
in this module is specific to the telemetry pipeline: the aggregates it tracks
and the N-gram baseline helper for the sequence-analysis stage.
"""

from __future__ import annotations

from fingerprint_sampler.aggregators import AggregateEntry, make_entry
from fingerprint_sampler.tokenizer import MaskEntry, tokenize
from fingerprint_sampler.warehouse import (  # noqa: F401
    SET_VERSION,
    FingerprintRecord,
    FingerprintSetError,
    ProfileMismatchError,
    Warehouse,
    fingerprint_id,
)

TELEMETRY_AGGREGATES: tuple[AggregateEntry, ...] = (
    make_entry("duration_ms", "$.duration_ms", ["MIN", "MAX"]),
    make_entry("samples", "$", "LAST(3)"),
)
"""What the pre-aggregator warehouse hardcoded: duration bounds and the last 3 raw events."""


def build_whitelist(
    records: list[dict],
    mask_profile: list[MaskEntry],
    n: int,
    warehouse: Warehouse | None = None,
) -> set[tuple[str, ...]]:
    """Observe a clean baseline telemetry stream and compile a whitelist of N-gram fingerprint trajectories."""
    if warehouse is None:
        warehouse = Warehouse()
    fingerprint_ids = []
    for r in records:
        tokens = tokenize(r, mask_profile)
        fid = warehouse.upsert(tokens, r)
        fingerprint_ids.append(fid)

    whitelist = set()
    for i in range(len(fingerprint_ids) - n + 1):
        whitelist.add(tuple(fingerprint_ids[i : i + n]))
    return whitelist
