"""Command-line interface (STORY-FING-26).

    python -m fingerling fingerprint --profile P --set S [EVENTS|-]

Folds a stream of JSONL events into a fingerprint set that grows across runs.
Knows nothing about where the events came from.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import IO, Iterable

from fingerling.profile import Profile, ProfileError, load_profile
from fingerling.tokenizer import tokenize
from fingerling.warehouse import FingerprintSetError, ProfileMismatchError, Warehouse

EXIT_OK = 0
EXIT_LINES_SKIPPED = 1
EXIT_NOT_WRITTEN = 2

_MAX_LINE_WARNINGS = 10

_FINGERPRINT_EPILOG = """\
example:
  # first run creates web.fingerprints.yaml; every later run merges into it
  python -m fingerling fingerprint -p examples/profiles/access_log.yaml \\
      -s web.fingerprints.yaml examples/data/access_log.jsonl

  # read events from a pipe
  tail -n 1000 app.jsonl | python -m fingerling fingerprint -p app.yaml -s app.fingerprints.yaml -

  # trial run: write the merged result elsewhere, leave the set untouched
  python -m fingerling fingerprint -p app.yaml -s app.fingerprints.yaml -o /tmp/preview.yaml new.jsonl

The SET file is updated in place (atomically) unless --output is given.

exit status:
  0  set written, every line was used
  1  set written, but some input lines were skipped (see stderr)
  2  nothing written (bad arguments, profile, set file, or profile mismatch)
"""


def _say(message: str) -> None:
    print(message, file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m fingerling",
        description="Fingerprint and sample JSONL event streams.",
    )
    commands = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)

    fp = commands.add_parser(
        "fingerprint",
        help="merge a JSONL event stream into a fingerprint set",
        description=(
            "Fingerprint every event in a JSONL stream using PROFILE and merge the results "
            "into the fingerprint set SET: counts add up, aggregates continue, new "
            "fingerprints are appended. SET is created if it does not exist."
        ),
        epilog=_FINGERPRINT_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    fp.add_argument(
        "-p",
        "--profile",
        required=True,
        metavar="PROFILE",
        help="YAML profile: which fields identify a fingerprint, what to aggregate",
    )
    fp.add_argument(
        "-s",
        "--set",
        required=True,
        metavar="SET",
        dest="set_path",
        help="fingerprint set file to merge into (created if missing, updated in place)",
    )
    fp.add_argument(
        "events",
        nargs="?",
        default="-",
        metavar="EVENTS",
        help="JSONL file of events, one JSON object per line; '-' or omitted reads stdin",
    )
    fp.add_argument(
        "-o",
        "--output",
        metavar="OUTPUT",
        help="write the merged set here instead, leaving SET unchanged",
    )
    fp.add_argument(
        "--force-profile",
        action="store_true",
        help="merge even if SET was built with a different profile "
        "(its existing fingerprints are kept as they are)",
    )
    fp.set_defaults(func=_cmd_fingerprint)
    return parser


def _fold_stream(lines: Iterable[str], profile: Profile, warehouse: Warehouse) -> dict:
    """Fingerprint each JSONL line into `warehouse`. Returns run statistics."""
    known_before = set(warehouse)
    seen: set[str] = set()
    events = skipped_lines = 0
    fields = list(profile.fields)

    def warn(lineno: int, reason: str) -> None:
        if skipped_lines <= _MAX_LINE_WARNINGS:
            _say(f"fingerling: line {lineno}: {reason} - skipped")
        elif skipped_lines == _MAX_LINE_WARNINGS + 1:
            _say("fingerling: further skipped lines are counted but not listed")

    for lineno, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            skipped_lines += 1
            warn(lineno, f"invalid JSON ({exc.msg} at column {exc.colno})")
            continue
        if not isinstance(event, dict):
            skipped_lines += 1
            warn(lineno, f"expected a JSON object, got {type(event).__name__}")
            continue
        seen.add(warehouse.upsert(tokenize(event, fields), event))
        events += 1

    return {
        "events": events,
        "skipped_lines": skipped_lines,
        "new": len(seen - known_before),
        "updated": len(seen & known_before),
    }


def _cmd_fingerprint(args: argparse.Namespace) -> int:
    try:
        profile = load_profile(args.profile)
    except ProfileError as exc:
        _say(f"fingerling: {exc}")
        return EXIT_NOT_WRITTEN

    from_stdin = args.events == "-"
    if from_stdin and sys.stdin.isatty():
        _say(
            "fingerling: no events to read. Name a JSONL file, or pipe events in:\n"
            f"  python -m fingerling fingerprint -p {args.profile} -s {args.set_path} events.jsonl\n"
            f"  some-command | python -m fingerling fingerprint -p {args.profile} -s {args.set_path} -"
        )
        return EXIT_NOT_WRITTEN

    warehouse = Warehouse(aggregates=profile.aggregates, profile_id=profile.profile_id)
    set_existed = os.path.exists(args.set_path)
    if set_existed:
        try:
            warehouse.load(args.set_path, force=args.force_profile)
        except ProfileMismatchError as exc:
            _say(
                f"fingerling: {exc}.\n"
                "  Fingerprints from different profiles are not comparable, so nothing was merged.\n"
                "  Use a separate --set file for this profile, or pass --force-profile to merge anyway."
            )
            return EXIT_NOT_WRITTEN
        except (FingerprintSetError, OSError) as exc:
            _say(f"fingerling: cannot use set file: {exc}")
            return EXIT_NOT_WRITTEN

    stream: IO[str]
    try:
        stream = sys.stdin if from_stdin else open(args.events, encoding="utf-8", errors="replace")
    except OSError as exc:
        _say(f"fingerling: cannot read events from {args.events}: {exc.strerror or exc}")
        return EXIT_NOT_WRITTEN

    destination = args.output or args.set_path
    try:
        stats = _fold_stream(stream, profile, warehouse)
    except KeyboardInterrupt:
        _say(f"fingerling: interrupted - {destination} was not modified")
        return 130
    finally:
        if not from_stdin:
            stream.close()

    try:
        warehouse.save(destination)
    except OSError as exc:
        _say(f"fingerling: cannot write {destination}: {exc.strerror or exc}")
        return EXIT_NOT_WRITTEN

    source = "stdin" if from_stdin else args.events
    _say(f"fingerling: {stats['events']} events read from {source}")
    _say(
        f"  fingerprints: {stats['new']} new, {stats['updated']} updated, "
        f"{len(warehouse)} total in set"
    )
    _say(
        f"  skipped: {stats['skipped_lines']} malformed lines, "
        f"{warehouse.skipped_values} aggregate values"
    )
    verb = "updated" if set_existed and not args.output else "wrote"
    _say(f"  {verb} {destination} (profile {profile.profile_id})")
    if args.output:
        _say(f"  {args.set_path} left unchanged")

    return EXIT_LINES_SKIPPED if stats["skipped_lines"] else EXIT_OK


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)
