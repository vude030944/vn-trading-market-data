"""
Container health.

Health is deliberately NOT "is data flowing": outside trading hours every feed
goes silent while remaining perfectly healthy (all three brokers document this).
The correct criterion is:

    the process is still updating the file AND every feed has completed its handshake

Written to a file rather than exposed over HTTP so a service whose entire job is
reading a socket does not need a web framework.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

DEFAULT_PATH = Path(os.getenv("HEALTH_FILE", "/tmp/health/ingestion.json"))
# Considered dead if the file has not been refreshed within this window.
STALE_AFTER_S = 30.0


def write(path: Path, broker: str, feeds: dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "ts": time.time(),
        "broker": broker,
        "healthy": all(f["connected"] for f in feeds.values()) if feeds else False,
        "feeds": feeds,
    }
    # Write to a temp file then rename, so a health check never reads a half-written file.
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc), encoding="utf-8")
    tmp.replace(path)


def check(path: Path = DEFAULT_PATH) -> tuple[bool, str]:
    """Return (healthy, reason). Used by `python -m ingestion.core.health`."""
    if not path.exists():
        return False, f"missing file {path}"
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"corrupt health file: {exc}"

    age = time.time() - doc.get("ts", 0)
    if age > STALE_AFTER_S:
        return False, f"health file is {age:.0f}s stale — the process may be stuck"

    down = [n for n, f in doc.get("feeds", {}).items() if not f.get("connected")]
    if down:
        return False, "feeds disconnected: " + ", ".join(down)
    return True, "ok"


if __name__ == "__main__":
    import sys

    ok, reason = check()
    print(reason)
    sys.exit(0 if ok else 1)
