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


@dataclass(frozen=True)
class MaskEntry:
    """One extraction rule: pull `path` out of a record, tag it `key`, tokenize with `modifier`."""

    key: str
    path: str
    modifier: str


def resolve_segments(data: Any, segments: list[str]) -> list[Any]:
    """Recursively resolve JSONPath segments (supporting fixed indices, wildcards, and descent)."""
    if data is _MISSING:
        return []

    if not segments:
        return [data]

    if data is None:
        return []

    seg = segments[0]
    remaining = segments[1:]

    if seg == "":
        # Recursive descent ".."
        results = []
        results.extend(resolve_segments(data, remaining))
        if isinstance(data, dict):
            for val in data.values():
                results.extend(resolve_segments(val, segments))
        elif isinstance(data, list):
            for val in data:
                results.extend(resolve_segments(val, segments))
        return results

    # Parse brackets (e.g. "args[*]", "[0]", "args")
    brackets = re.findall(r"\[([^\]]+)\]", seg)
    name = re.sub(r"\[[^\]]+\]", "", seg)

    curr_level: list[Any] = []
    if name:
        if isinstance(data, dict) and name in data:
            curr_level = [data[name]]
        else:
            return []
    else:
        curr_level = [data]

    for br in brackets:
        next_level: list[Any] = []
        for item in curr_level:
            if br == "*":
                if isinstance(item, list):
                    next_level.extend(item)
            else:
                try:
                    idx = int(br)
                    if isinstance(item, list) and 0 <= idx < len(item):
                        next_level.append(item[idx])
                except ValueError:
                    pass
        curr_level = next_level
        if not curr_level:
            break

    final_results: list[Any] = []
    for item in curr_level:
        final_results.extend(resolve_segments(item, remaining))
    return final_results


def resolve_path(record: dict, path: str) -> Any:
    """Resolve a dot/bracket-index path (supporting wildcards [*] and recursive descent ..) against `record`."""
    if path == "$":
        return record
    if path.startswith("$."):
        path = path[2:]
    elif path.startswith("$"):
        path = path[1:]

    segments = path.split(".")
    results = resolve_segments(record, segments)

    has_wildcard = "*" in path or ".." in path
    if has_wildcard:
        return results
    else:
        if not results:
            return _MISSING
        return results[0]


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


def apply_modifier(value: Any, modifier: str, has_wildcard: bool = False) -> str:
    """Apply a modifier expression (e.g. "IN_RANGE(-999, 0)") to `value`."""
    if has_wildcard and isinstance(value, list):
        if not value:
            value = _MISSING
        else:
            tokens = [apply_modifier(item, modifier, has_wildcard=False) for item in value]
            return ",".join(sorted(list(set(tokens))))

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
    result = {}
    for entry in mask_profile:
        has_wildcard = "*" in entry.path or ".." in entry.path
        val = resolve_path(record, entry.path)
        result[entry.key] = apply_modifier(val, entry.modifier, has_wildcard)
    return result


def parse_jsonl(jsonl_text: str) -> list[dict]:
    """Parse a JSONL (newline-delimited JSON) string into a list of records.

    Blank lines are skipped so trailing newlines in a streamed eBPF probe
    output don't produce spurious entries.
    """
    return [json.loads(line) for line in jsonl_text.splitlines() if line.strip()]
