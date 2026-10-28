# marketsim — SSI / DNSE / TCBS broker simulator

One Docker service that impersonates all three brokers closely enough for the
**real** ingestion service to authenticate, subscribe, stay alive and receive
every channel — so the whole pipeline can be tested at any hour, without
credentials.

```
:8001  SSI   POST /api/v3/auth/token|refresh      WS /ws/v3  (and /)
:8002  DNSE                                        WS /v1/stream?encoding=json|msgpack
:8003  TCBS  POST /gaia/v1/oauth2/openapi/token    WS /ws/thesis/v1/stream/{normal,derivative}
                                                      /ws/ouranos/v1/stream
:8080  GET /stats  GET /healthz  POST /control/{pause,resume}
```

## One market, three dialects

A single engine (`market.py`) owns the truth: a random walk per instrument on the
real tick-size grid, clamped to each exchange's daily band (HOSE ±7%, HNX ±10%,
UPCOM ±15%), a 10-level book, foreign room, minute bars, aggressor-side
supply/demand and five indices. Each broker server re-encodes the **same** events
in its own way, so the same HPG trade arrives as:

| | price | qty | time |
|---|---|---|---|
| SSI `trade_tick` | `"24.35"` (thousand VND, string) | `"500"` | `"2026/10/28 10:15:32"` |
| DNSE `tick_extra` | `24.35` (thousand VND, number) | `500` | `{"Seconds":…, "Nanos":…}` |
| TCBS `s|6` | `"24350"` (VND, string) | `"500"` | none |

Universe: VN30 + 10 other HOSE names, 10 HNX, 8 UPCOM, 8 covered warrants and
3 VN30 futures (`universe.py`).

## Protocol fidelity

Every behaviour is taken from `docs/<broker>/brief/DOCUMENT.md`, or — for TCBS —
from the audit of 6.1M production messages in `examples/`, which wins where the
two disagree. Where both are silent the behaviour is **invented, configurable,
and marked INVENTED** in the module docstring.

| | Enforced |
|---|---|
| **SSI** | REST token + refresh, `expiresAt` in ms or s; token via query / header / first frame (doc 10.3 leaves it open → `SIM_SSI_AUTH_MODE`); topic grammar with `*`, `SYM-SYM`, `vn30`, `hose` scopes and `@tick/1m/5m`; server `PING` → client must `PONG`; both `market` shapes |
| **DNSE** | welcome → HMAC auth **recomputed by the server**, ±5 min window, nonce replay rejected for 10 min, `AUTH_TIMEOUT` after 30 s; `rate_limit` in `auth_success`; ping every 3 min / pong within 60 s; 8-hour `connection_expired` + 1008; slow consumer → 1013; json **and** msgpack; every documented timestamp inconsistency; `T` absent like every doc sample (`SIM_DNSE_SEND_T=1` to add it) |
| **TCBS** | REST apiKey+OTP token; `d|a|||b64` → `d|33|N` + `d|0|…`; subscribe before auth → closed; `tk/ro/si/pt` subscriptions, `d|u`, `d|r` → `s|38`, `tmh` backfill → `s|22`; `d|34|1` acks; heartbeat timeout → close 1000; **RFC 6455 ping → close 1002**; cash = strings, futures = numbers; covered warrants `s|18/28/29/30/32`, futures foreign `s|25`, `s|42` only with `dtn`; **futures family on both sockets, byte-identical, normal ~1 ms first**; ouranos `d|33|30` and server `d|pi` every 10 s |

## Configuration

All `SIM_*` variables are in `marketsim/config.py`. The useful ones:

| Variable | Default | |
|---|---|---|
| `SIM_TRADES_PER_SEC` | 40 | matched trades per second (total frames are ~10–20×) |
| `SIM_MARKET_HOURS` | 0 | 1 = only trade inside real HOSE sessions (to test "silent but healthy") |
| `SIM_CHAOS_DROP_EVERY_S` | 0 | drop one random connection per broker every N s (reconnect test) |
| `SIM_SSI_AUTH_MODE` | any | any / query / header / frame |
| `SIM_DNSE_MAX_CONN_S` | 28800 | shorten to watch the 8-hour renewal happen |
| `SIM_TCBS_FUTURES_ON_BOTH` | 1 | reproduce the cross-socket duplicate |

## Tests

`tests/` drive the production ingestion code (`src/ingestion`) against the
simulator in-process — no Kafka, no Docker:

```bash
pip install aiohttp msgpack pytest pytest-asyncio websockets httpx aiokafka cramjam \
    python-dotenv opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
cd src/simulator && pytest -q
```

They check every auth mode and encoding, that each frame ingestion received was
counted as delivered by the simulator, and the failure paths (wrong secret,
reused nonce, RFC ping, subscribe before auth, heartbeat silence).

The full pipeline test is in [`environment/e2e/`](../../environment/e2e/).
