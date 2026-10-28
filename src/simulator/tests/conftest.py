"""
Make both the simulator and the REAL ingestion package importable, so the tests
drive the production client code against the simulator — no Kafka, no docker.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest
from aiohttp import web

ROOT = Path(__file__).resolve().parents[2]          # src/
sys.path.insert(0, str(ROOT / "simulator"))
sys.path.insert(0, str(ROOT))

from marketsim.__main__ import build  # noqa: E402
from marketsim.config import SimConfig  # noqa: E402


class Sim:
    def __init__(self, cfg: SimConfig) -> None:
        self.cfg = cfg
        self.market, self.stats, self.reg, self._apps = build(cfg)
        self.ports: dict[str, int] = {}
        self._runners: list[web.AppRunner] = []

    async def start(self) -> "Sim":
        names = {self.cfg.ssi_port: "ssi", self.cfg.dnse_port: "dnse",
                 self.cfg.tcbs_port: "tcbs", self.cfg.stats_port: "stats"}
        for port, app in self._apps.items():
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "127.0.0.1", 0)
            await site.start()
            self.ports[names[port]] = site._server.sockets[0].getsockname()[1]
            self._runners.append(runner)
        return self

    async def stop(self) -> None:
        for r in self._runners:
            await r.cleanup()


@pytest.fixture
def sim_config() -> SimConfig:
    # Busy and fast: lots of trades, indices every 200 ms, supply/demand every 1 s.
    return replace(SimConfig(), trades_per_sec=300, index_interval_s=0.2,
                   sd_short_s=1, sd_long_s=2, tcbs_ouranos_server_ping_s=0.3,
                   tcbs_thesis_timeout_s=5)


@pytest.fixture
async def sim(sim_config):
    import asyncio

    s = await Sim(sim_config).start()
    task = asyncio.create_task(s.market.run())
    yield s
    task.cancel()
    await s.stop()
