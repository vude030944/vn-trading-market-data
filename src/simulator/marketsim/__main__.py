"""
python -m marketsim — one process, one market, three broker servers.

    :8001  SSI   REST /api/v3/auth/*      WS /ws/v3 (and /)
    :8002  DNSE                           WS /v1/stream
    :8003  TCBS  REST /gaia/v1/oauth2/... WS /ws/thesis/v1/stream/{normal,derivative}
                                             /ws/ouranos/v1/stream
    :8080  GET /stats   delivered frames per (source, feed, wire_code)
           GET /healthz
           POST /control/pause | /control/resume | /control/revoke-tokens
"""

from __future__ import annotations

import asyncio
import logging
import random
import signal

from aiohttp import web

from .config import SimConfig
from .dnse import DnseServer
from .hub import Registry, Stats
from .market import MarketEngine
from .ssi import SsiServer
from .tcbs import TcbsServer

log = logging.getLogger("marketsim")


def build(cfg: SimConfig) -> tuple[MarketEngine, Stats, Registry, dict[int, web.Application]]:
    market, stats, reg = MarketEngine(cfg), Stats(), Registry()
    ssi, tcbs = SsiServer(cfg, market, stats, reg), TcbsServer(cfg, market, stats, reg)
    apps = {
        cfg.ssi_port: ssi.app(),
        cfg.dnse_port: DnseServer(cfg, market, stats, reg).app(),
        cfg.tcbs_port: tcbs.app(),
    }

    async def stats_view(_: web.Request) -> web.Response:
        return web.json_response(stats.as_dict(reg.clients))

    async def health(_: web.Request) -> web.Response:
        return web.json_response({"ok": True, "phase": market.phase[0], "paused": market.paused})

    async def control(req: web.Request) -> web.Response:
        action = req.match_info["action"]
        if action == "revoke-tokens":
            # Every SSI/TCBS token issued so far becomes INVALID (as after a key
            # rotation): clients must notice and obtain a new one.
            ssi.tokens.revoke_all()
            ssi.refresh.revoke_all()
            tcbs.tokens.revoke_all()
            log.info("all SSI/TCBS tokens revoked")
            return web.json_response({"revoked": True})
        market.paused = action == "pause"
        log.info("market %s", "paused" if market.paused else "resumed")
        return web.json_response({"paused": market.paused})

    ops = web.Application()
    ops.router.add_get("/stats", stats_view)
    ops.router.add_get("/healthz", health)
    ops.router.add_post("/control/{action:pause|resume|revoke-tokens}", control)
    apps[cfg.stats_port] = ops
    return market, stats, reg, apps


async def serve(cfg: SimConfig, stop: asyncio.Event) -> None:
    market, _, reg, apps = build(cfg)
    runners = []
    for port, app in apps.items():
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        await web.TCPSite(runner, cfg.host, port).start()
        runners.append(runner)
    log.info("listening: ssi=%d dnse=%d tcbs=%d stats=%d",
             cfg.ssi_port, cfg.dnse_port, cfg.tcbs_port, cfg.stats_port)
    tasks = [asyncio.create_task(market.run())]
    if cfg.chaos_drop_every_s > 0:
        tasks.append(asyncio.create_task(reg.chaos(cfg.chaos_drop_every_s, random.Random(cfg.seed))))
    await stop.wait()
    for t in tasks:
        t.cancel()
    for r in runners:
        await r.cleanup()


def main() -> None:
    cfg = SimConfig()
    logging.basicConfig(level=cfg.log_level,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    loop = asyncio.new_event_loop()
    stop = asyncio.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:          # Windows
            pass
    try:
        loop.run_until_complete(serve(cfg, stop))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
