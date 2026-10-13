"""`python -m fingerling` entry point."""

from __future__ import annotations

import sys

_DEPENDENCIES = ("fingerprint_sampler", "jsonpath", "yaml")


def main() -> None:
    try:
        from fingerling.cli import main as cli_main
    except ModuleNotFoundError as exc:
        if exc.name not in _DEPENDENCIES:
            raise
        print(
            f"fingerling: the {exc.name!r} module is not installed for this Python.\n"
            '  Run `make install` once, then use `make fingerprint ARGS="..."`\n'
            "  or `.venv/bin/fingerprint merge ...`.",
            file=sys.stderr,
        )
        sys.exit(2)
    sys.exit(cli_main())


if __name__ == "__main__":
    main()
