"""`fingerling` command: kept as an alias for the stand-alone `fingerprint` tool."""

from __future__ import annotations

import sys

from fingerprint_sampler.cli import merge_main

_USAGE = """\
usage: fingerling fingerprint -p PROFILE -s SET [EVENTS|-] [-o OUTPUT] [--force-profile]

`fingerling fingerprint` is an alias for `fingerprint merge`, the command installed by the
fingerprint-sampler package. Run `fingerprint --help` for everything it can do.
"""


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["fingerprint"]:
        return merge_main(argv[1:], prog="fingerling fingerprint")
    if argv and argv[0] in ("-h", "--help"):
        print(_USAGE, end="")
        return 0
    print(_USAGE, end="", file=sys.stderr)
    return 2
