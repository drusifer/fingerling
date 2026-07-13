"""Intentionally vulnerable local demo target for `examples/demo_live_exploit.py`.

A single diagnostics endpoint that shells out to `ping` with unsanitized user
input -- classic OS command injection (CWE-78 / OWASP A03). Loopback-only,
non-destructive, and torn down by the caller when the demo finishes. This is
a deliberately vulnerable toy for a controlled, local security demo -- do not
expose it beyond 127.0.0.1.
"""

from __future__ import annotations

import os

from flask import Flask, request

app = Flask(__name__)


@app.route("/health")
def health() -> str:
    """Readiness probe that does not fork anything -- keeps startup checks out of the capture."""
    return "ok\n"


@app.route("/diagnostics")
def diagnostics() -> str:
    host = request.args.get("host", "127.0.0.1")
    os.system(f"ping -c 1 -W1 {host}")  # CWE-78: unsanitized shell interpolation, by design.
    return "diagnostic sent\n"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
