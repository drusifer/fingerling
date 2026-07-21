"""Stateful append-only upsert data warehouse (STORY-FING-02).

Serializes tokenized fingerprints into a stable MD5 ID and continuously
reconciles occurrences against a bounded-size historical record, so
multi-day production traces don't bloat the tracking manifest.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

import yaml

_SAMPLE_RING_CAP = 3


def fingerprint_id(tokens: dict[str, str]) -> str:
    """Alphabetically sort tokens by key, flatten, and MD5-fold into a stable ID."""
    flattened = "|".join(f"{key}:{tokens[key]}" for key in sorted(tokens))
    return hashlib.md5(flattened.encode("utf-8")).hexdigest()


@dataclass
class FingerprintRecord:
    total_occurrences: int
    first_seen: str
    last_seen: str
    min_duration_ms: float
    max_duration_ms: float
    samples: list = field(default_factory=list)


class Warehouse:
    """In-memory fingerprint inventory with YAML load/save."""

    def __init__(self) -> None:
        self._records: dict[str, FingerprintRecord] = {}

    def upsert(
        self,
        tokens: dict[str, str],
        duration_ms: float,
        raw_record: dict,
        timestamp: str | None = None,
    ) -> str:
        """Upsert one telemetry observation. Returns the fingerprint_id.

        Match: increments total_occurrences, updates last_seen and the
        min/max duration bounds — no new record block.
        Drift: creates a new record block seeded from this observation.
        Both states append `raw_record` to the fixed-capacity sample ring.
        """
        fid = fingerprint_id(tokens)
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        existing = self._records.get(fid)

        if existing is None:
            self._records[fid] = FingerprintRecord(
                total_occurrences=1,
                first_seen=ts,
                last_seen=ts,
                min_duration_ms=duration_ms,
                max_duration_ms=duration_ms,
                samples=[raw_record],
            )
        else:
            existing.total_occurrences += 1
            existing.last_seen = ts
            existing.min_duration_ms = min(existing.min_duration_ms, duration_ms)
            existing.max_duration_ms = max(existing.max_duration_ms, duration_ms)
            existing.samples = (existing.samples + [raw_record])[-_SAMPLE_RING_CAP:]

        return fid

    def get(self, fingerprint_id_: str) -> FingerprintRecord | None:
        return self._records.get(fingerprint_id_)

    def __len__(self) -> int:
        return len(self._records)

    def save(self, path: str) -> None:
        data = {fid: asdict(rec) for fid, rec in self._records.items()}
        with open(path, "w") as f:
            yaml.safe_dump(data, f, sort_keys=True)

    def load(self, path: str) -> None:
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        self._records = {fid: FingerprintRecord(**rec) for fid, rec in data.items()}


def build_whitelist(
    records: list[dict],
    mask_profile: list[MaskEntry],
    n: int,
    warehouse: Warehouse | None = None,
) -> set[tuple[str, ...]]:
    """Observe a clean baseline telemetry stream and compile a whitelist of N-gram fingerprint trajectories."""
    from fingerling.tokenizer import tokenize

    if warehouse is None:
        warehouse = Warehouse()
    fingerprint_ids = []
    for r in records:
        tokens = tokenize(r, mask_profile)
        fid = warehouse.upsert(tokens, duration_ms=0.0, raw_record=r)
        fingerprint_ids.append(fid)

    whitelist = set()
    for i in range(len(fingerprint_ids) - n + 1):
        whitelist.add(tuple(fingerprint_ids[i : i + n]))
    return whitelist


