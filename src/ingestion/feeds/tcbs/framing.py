"""
TCBS wire protocol — PURE functions, no network imports.

That keeps all frame-splitting testable without websockets or Kafka, and keeps
the hot path from paying for a full json.loads of every payload.

Grammar (docs/tcbs/brief/DOCUMENT.md sections 3.3, 4, 7.2):
    control       d|<code>|<payload>       e.g. d|0|{...}  d|33|15  d|34|1
    thesis data   s|<wire>|{json}          e.g. s|6|{"symbol":"TCB",...}
    ouranos data  <CODE>|<SYMBOL>|{json}   e.g. C001|TCB|{...}
"""

from __future__ import annotations

import re
from typing import NamedTuple

# --- control ---------------------------------------------------------------
AUTH_FRAME = "d|a|||{b64_token}"
AUTH_RESPONSE_PREFIX = "d|0|"
CONFIG_PREFIX = "d|33|"          # d|33|N  -> heartbeat timeout in seconds
SUBSCRIBE_ACK_PREFIX = "d|34|"   # d|34|1  -> subscription acknowledged

# --- thesis ---------------------------------------------------------------
THESIS_PING = "d|p|||"
DATA_PREFIX = "s|"

# --- ouranos --------------------------------------------------------------
# `d|po` is the heartbeat the CLIENT sends. The server also emits its own `d|pi`
# roughly every 10 seconds — this is NOT in the documentation and was only found
# by live probing in examples/. Without handling it, every 10s produces an
# "unrecognised message" warning.
OURANOS_PING = "d|po"
OURANOS_SERVER_PING = "d|pi"

# A single message MAY carry several concatenated frames. An audit of 3M messages
# found it is always 1 frame per message in practice, but that is an observation
# rather than a TCBS guarantee -> keep the splitter as defence in depth. DOTALL
# because TCBS pretty-prints its JSON.
_FRAME_RE = re.compile(r"[sd]\|[^|]*\|.*?(?=(?:[sd]\|)|$)", re.DOTALL)

_SYMBOL_RE = re.compile(r'"symbol"\s*:\s*"([^"]*)"')
_INDEX_ID_RE = re.compile(r'"indexId"\s*:\s*"([^"]*)"')
# s|8 carries only indexNumber as a NUMBER (no indexId). examples/ lacked this
# branch, so the Kafka key of every index frame was NULL — losing per-index ordering.
_INDEX_NUMBER_RE = re.compile(r'"indexNumber"\s*:\s*(\d+)')


class ThesisFrame(NamedTuple):
    wire_code: str
    json_body: str


class OuranosFrame(NamedTuple):
    code: str        # C001 | C002S60 | C002S900
    symbol: str
    json_body: str


def split_frames(text: str) -> list[str]:
    return [m.group(0) for m in _FRAME_RE.finditer(text)]


def parse_thesis_frame(frame: str) -> ThesisFrame | None:
    """`s|6|{json}` -> ('6', '{json}'). None when malformed."""
    if not frame.startswith(DATA_PREFIX):
        return None
    sep1 = frame.find("|")
    sep2 = frame.find("|", sep1 + 1)
    if sep1 < 0 or sep2 < 0:
        return None
    return ThesisFrame(frame[sep1 + 1 : sep2], frame[sep2 + 1 :])


def parse_ouranos_frame(raw: str) -> OuranosFrame | None:
    """`C001|TCB|{json}` -> ('C001', 'TCB', '{json}'). Control frames -> None."""
    if raw.startswith("d|"):
        return None
    sep1 = raw.find("|")
    sep2 = raw.find("|", sep1 + 1)
    if sep1 <= 0 or sep2 < 0:
        return None
    body = raw[sep2 + 1 :]
    if not body.lstrip().startswith("{"):
        return None
    return OuranosFrame(raw[:sep1], raw[sep1 + 1 : sep2], body)


def extract_key(json_body: str) -> str | None:
    """
    Partition key: symbol -> indexId -> indexNumber.

    Regex instead of json.loads: the payload is forwarded verbatim, so these are
    the only fields we need and a full object parse is not worth it on the hot path.
    """
    m = _SYMBOL_RE.search(json_body)
    if m and m.group(1):
        return m.group(1)
    m = _INDEX_ID_RE.search(json_body)
    if m and m.group(1):
        return m.group(1)
    m = _INDEX_NUMBER_RE.search(json_body)
    if m:
        return m.group(1)
    return None


def parse_config_timeout(raw: str) -> float | None:
    """`d|33|15` -> 15.0. This value OVERRIDES config — the server is authoritative."""
    if not raw.startswith(CONFIG_PREFIX):
        return None
    try:
        return float(raw[len(CONFIG_PREFIX) :].strip())
    except ValueError:
        return None
