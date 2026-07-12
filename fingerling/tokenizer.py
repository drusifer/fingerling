"""JSONPath extraction and plug-and-play modifier engine (STORY-FING-01).

Collapses high-cardinality eBPF telemetry fields (PIDs, timestamps, raw byte
counts) into stable, low-cardinality string tokens before hashing.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable

_MISSING = object()
"""Sentinel returned by resolve_path when a path segment can't be found."""

_SEGMENT_RE = re.compile(r"^(\w+)((?:\[\d+\])*)$")
_INDEX_RE = re.compile(r"\[(\d+)\]")


@dataclass(frozen=True)
class MaskEntry:
    """One extraction rule: pull `path` out of a record, tag it `key`, tokenize with `modifier`."""

    key: str
    path: str
    modifier: str


def resolve_path(record: dict, path: str) -> Any:
    """Resolve a dot/bracket-index path (e.g. "$.a.b[0].c") against `record`.

    Returns the `_MISSING` sentinel instead of raising if any segment is
    absent, so callers never need to catch KeyError/IndexError.
    """
    if path.startswith("$."):
        path = path[2:]
    elif path.startswith("$"):
        path = path[1:]

    current: Any = record
    for segment in path.split("."):
        match = _SEGMENT_RE.match(segment)
        if not match:
            return _MISSING
        name, indices = match.group(1), match.group(2)
        if not isinstance(current, dict) or name not in current:
            return _MISSING
        current = current[name]
        for idx_str in _INDEX_RE.findall(indices):
            idx = int(idx_str)
            if not isinstance(current, list) or idx >= len(current):
                return _MISSING
            current = current[idx]
    return current


def _mod_default(value: Any) -> str:
    return "NULL" if value is _MISSING or value is None else str(value)


def _mod_is_present(value: Any) -> str:
    return "FALSE" if value is _MISSING or value is None else "TRUE"


def _mod_is_null(value: Any) -> str:
    return "TRUE" if value is _MISSING or value is None else "FALSE"


def _mod_in_range(value: Any, low: str, high: str) -> str:
    if value is _MISSING or value is None:
        return "FALSE"
    try:
        num = float(value)
    except (TypeError, ValueError):
        return "FALSE"
    return "TRUE" if float(low) <= num <= float(high) else "FALSE"


def _mod_any(value: Any, *options: str) -> str:
    if value is _MISSING or value is None:
        return "FALSE"
    return "TRUE" if str(value) in {str(o) for o in options} else "FALSE"


_MODIFIERS: dict[str, Callable[..., str]] = {
    "DEFAULT": _mod_default,
    "IS_PRESENT": _mod_is_present,
    "IS_NULL": _mod_is_null,
    "IN_RANGE": _mod_in_range,
    "ANY": _mod_any,
}


def apply_modifier(value: Any, modifier: str) -> str:
    """Apply a modifier expression (e.g. "IN_RANGE(-999, 0)") to `value`."""
    name, _, rest = modifier.partition("(")
    name = name.strip()
    if name not in _MODIFIERS:
        raise ValueError(f"Unknown modifier: {name!r}")

    args: list[str] = []
    if rest:
        args_str = rest.rstrip(")").strip()
        if args_str:
            args = [a.strip() for a in args_str.split(",")]

    fn = _MODIFIERS[name]
    if name in ("DEFAULT", "IS_PRESENT", "IS_NULL"):
        return fn(value)
    return fn(value, *args)


def tokenize(record: dict, mask_profile: list[MaskEntry]) -> dict[str, str]:
    """Extract + tokenize every `MaskEntry` in `mask_profile` against `record`."""
    return {
        entry.key: apply_modifier(resolve_path(record, entry.path), entry.modifier)
        for entry in mask_profile
    }


def parse_jsonl(jsonl_text: str) -> list[dict]:
    """Parse a JSONL (newline-delimited JSON) string into a list of records.

    Blank lines are skipped so trailing newlines in a streamed eBPF probe
    output don't produce spurious entries.
    """
    return [json.loads(line) for line in jsonl_text.splitlines() if line.strip()]
