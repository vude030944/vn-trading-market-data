"""
Entry point for the ingestion service.

    python -m ingestion --broker tcbs

ONE image, three services — differing by a single argument. That way no code
path runs for one broker while going untested for the others.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from .config.base import RuntimeSettings
from .core import json_logging
from .core.runner import Runner
from .feeds import BROKERS, load

log = logging.getLogger("ingestion")


def _load_dotenv() -> None:
    """Convenience for running locally; in Docker the environment is passed directly."""
    try:
        from pathlib import Path

        from dotenv import load_dotenv

        load_dotenv(Path(__file__).resolve().parent / ".env")
    except ImportError:
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ingestion", description="VN market data ingestion")
    parser.add_argument("--broker", required=True, choices=BROKERS)
    args = parser.parse_args(argv)

    _load_dotenv()
    runtime = RuntimeSettings()
    logging_runtime = json_logging.configure(
        f"{runtime.service_name}-{args.broker}", runtime.environment, runtime.log_level
    )

    try:
        cfg, specs, topics = load(args.broker)
    except ValueError as exc:
        log.error("Invalid configuration: %s", exc)
        logging_runtime.shutdown()
        return 1

    log.info("Starting ingestion", extra={"broker": args.broker, "config": str(cfg),
                                         "feeds": [s.name for s in specs]})

    runner = Runner(
        specs,
        cfg.infra,                       # type: ignore[attr-defined]
        backoff=cfg.backoff,             # type: ignore[attr-defined]
        connect_timeout_s=cfg.connect_timeout_s,   # type: ignore[attr-defined]
        topics=topics,
    )

    try:
        try:
            import uvloop

            uvloop.run(runner.run())
        except ImportError:
            asyncio.run(runner.run())
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt — exiting")
    except Exception:
        log.exception("Unhandled error in main")
        return 1
    finally:
        logging_runtime.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
