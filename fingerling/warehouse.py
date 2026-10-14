"""Telemetry-side helpers around the fingerprint set (which lives in `fingerprint_sampler`):
the aggregates the telemetry pipeline tracks and the N-gram baseline helper.
"""

from __future__ import annotations

from fingerling.tokenizer import tokenize
from fingerprint_sampler.aggregators import Aggregate
from fingerprint_sampler.fingerprint_set import FingerprintSet
from fingerprint_sampler.model import Field

TELEMETRY_AGGREGATES: tuple[Aggregate, ...] = (
    Aggregate("duration_ms", "$.duration_ms", ["MIN", "MAX"]),
    Aggregate("samples", "$", {"name": "LAST", "n": 3}),
)
"""What the pre-aggregator warehouse hardcoded: duration bounds and the last 3 raw events."""


def build_whitelist(
    records: list[dict],
    mask_profile: list[Field],
    n: int,
    warehouse: FingerprintSet | None = None,
) -> set[tuple[str, ...]]:
    """Observe a clean baseline telemetry stream and compile a whitelist of N-gram fingerprint trajectories."""
    if warehouse is None:
        warehouse = FingerprintSet()
    fingerprint_ids = []
    for r in records:
        tokens = tokenize(r, mask_profile)
        fid = warehouse.upsert(tokens, r)
        fingerprint_ids.append(fid)

    whitelist = set()
    for i in range(len(fingerprint_ids) - n + 1):
        whitelist.add(tuple(fingerprint_ids[i : i + n]))
    return whitelist
