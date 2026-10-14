"""eBPF-side tokenizing: turn telemetry records into tokens with fingerprint-sampler fields.

Moved out of fingerprint-sampler (STORY-FING-39), which reads JSONL itself and
tokenizes through `Profile.tokens`.
"""

from __future__ import annotations

import json
from typing import Any

from fingerprint_sampler.model import Field, tokens


def tokenize(record: Any, fields: list[Field]) -> dict[str, str]:
    """The tokens `fields` make of one telemetry record, by key."""
    return tokens(record, fields)


def parse_jsonl(jsonl_text: str) -> list[dict]:
    """Parse JSONL text into records, skipping blank lines (streamed probe output ends in one)."""
    return [json.loads(line) for line in jsonl_text.splitlines() if line.strip()]
