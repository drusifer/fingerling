"""Telemetry-side helpers around the sketch (from the sketch-tastic package, `sketchtastic`):
the aggregates the telemetry pipeline tracks and the N-gram baseline helper.
"""

from __future__ import annotations

from sketchtastic.aggregators import Aggregate
from sketchtastic.model import Field
from sketchtastic.sketch import Sketch

from fingerling.tokenizer import tokenize

TELEMETRY_AGGREGATES: tuple[Aggregate, ...] = (
    Aggregate("duration_ms", "$.duration_ms", ["MIN", "MAX"]),
)
"""Duration bounds; every fingerprint also keeps its first and last events as built-in samples."""


def build_whitelist(
    records: list[dict],
    mask_profile: list[Field],
    n: int,
    warehouse: Sketch | None = None,
) -> set[tuple[str, ...]]:
    """Observe a clean baseline telemetry stream and compile a whitelist of N-gram fingerprint trajectories."""
    if warehouse is None:
        warehouse = Sketch()
    fingerprint_ids = []
    for r in records:
        tokens = tokenize(r, mask_profile)
        fid = warehouse.upsert(tokens, r)
        fingerprint_ids.append(fid)

    whitelist = set()
    for i in range(len(fingerprint_ids) - n + 1):
        whitelist.add(tuple(fingerprint_ids[i : i + n]))
    return whitelist
