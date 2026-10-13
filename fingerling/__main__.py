"""`python -m fingerling` entry point."""

from __future__ import annotations

import sys

_DEPENDENCIES = {"jsonpath": "python-jsonpath", "yaml": "PyYAML"}


def main() -> None:
    try:
        from fingerling.cli import main as cli_main
    except ModuleNotFoundError as exc:
        if exc.name not in _DEPENDENCIES:
            raise
        print(
            f"fingerling: the {_DEPENDENCIES[exc.name]} package is not installed for this Python.\n"
            "  Run `make install` once, then use `make fingerprint ARGS=\"...\"`\n"
            "  or `.venv/bin/python -m fingerling ...`.",
            file=sys.stderr,
        )
        sys.exit(2)
    sys.exit(cli_main())


if __name__ == "__main__":
    main()
