"""
The instruments the simulated market trades, and how each broker names them.

Prices are kept in the exchange's native unit — VND for cash equities and covered
warrants, index points for futures — and each broker server converts on the way
out, exactly as the real brokers disagree (SSI "45.50" thousand VND as a string,
DNSE 24.35 thousand VND as a number, TCBS "24550" VND as a string).
"""

from __future__ import annotations

from dataclasses import dataclass

HOSE, HNX, UPCOM, DERIV = "HOSE", "HNX", "UPCOM", "DERIVATIVES"

# Daily price band (fraction of the reference price).
BAND = {HOSE: 0.07, HNX: 0.10, UPCOM: 0.15, DERIV: 0.07}

# DNSE marketId / productGrpId (docs/dnse/brief section 8).
DNSE_MARKET_ID = {HOSE: "STO", HNX: "STX", UPCOM: "UPX", DERIV: "DVX"}

# TCBS floor codes for `d|s|ro|...|<floors>` (docs/tcbs/brief section 9):
#   1 VN-INDEX(HOSE) 3 HNX 5 UPCOM 7 covered warrant 8 Derivative-VN30
TCBS_FLOOR = {"stock-" + HOSE: "1", "stock-" + HNX: "3", "stock-" + UPCOM: "5",
              "cw": "7", "future": "8"}
# Put-through floors for `d|s|pt|...`: 1 HOSE, 2 HNX, 3 UPCOM.
TCBS_PT_FLOOR = {HOSE: "1", HNX: "2", UPCOM: "3"}


@dataclass(frozen=True)
class Instrument:
    symbol: str
    exchange: str
    kind: str            # stock | cw | future
    ref_price: float     # VND (stock, cw) or index points (future)
    weight: float        # relative trading activity
    shares_out: int = 0  # for the foreign room
    isin: str = ""

    @property
    def tcbs_floor(self) -> str:
        if self.kind == "stock":
            return TCBS_FLOOR["stock-" + self.exchange]
        return TCBS_FLOOR[self.kind]

    def tick_size(self, price: float) -> float:
        if self.kind == "future":
            return 0.1
        if self.kind == "cw":
            return 10.0
        if self.exchange == HOSE:
            return 10.0 if price < 10_000 else 50.0 if price < 50_000 else 100.0
        return 100.0

    def lot(self) -> int:
        return 1 if self.kind == "future" else 100

    def band(self) -> tuple[float, float]:
        """(floor, ceiling), rounded onto the tick grid."""
        b = BAND[DERIV if self.kind == "future" else self.exchange]
        lo, hi = self.ref_price * (1 - b), self.ref_price * (1 + b)
        t = self.tick_size(self.ref_price)
        return (round(-(-lo // t) * t, 1), round((hi // t) * t, 1))


def _isin(sym: str) -> str:
    return ("VN000000" + sym + "0" * 4)[:12]


# VN30 (src/ingestion/symbols/vn30.txt) with plausible reference prices in VND.
_VN30 = {
    "ACB": 24_550, "BCM": 64_300, "BID": 38_900, "BVH": 49_200, "CTG": 36_100,
    "FPT": 118_500, "GAS": 66_800, "GVR": 30_250, "HDB": 25_400, "HPG": 24_350,
    "MBB": 23_150, "MSN": 73_600, "MWG": 61_900, "PLX": 37_800, "POW": 12_450,
    "SAB": 50_600, "SHB": 11_950, "SSB": 17_850, "SSI": 45_500, "STB": 38_200,
    "TCB": 24_550, "TPB": 15_900, "VCB": 61_200, "VHM": 41_850, "VIB": 18_400,
    "VIC": 44_300, "VJC": 101_200, "VNM": 61_500, "VPB": 19_250, "VRE": 24_800,
}
_HOSE_OTHER = {"DGC": 92_400, "DXG": 15_750, "KDH": 31_600, "PNJ": 79_300, "VND": 15_200,
               "VCI": 33_450, "REE": 66_000, "GEX": 21_500, "PDR": 18_900, "NVL": 10_350}
_HNX = {"SHS": 13_400, "PVS": 33_200, "CEO": 18_300, "IDC": 52_100, "MBS": 27_900,
        "NVB": 9_800, "TNG": 21_700, "VCS": 58_400, "PVI": 50_900, "HUT": 17_600}
_UPCOM = {"BSR": 19_850, "VEA": 41_300, "ACV": 96_500, "MCH": 128_000, "QNS": 47_900,
          "OIL": 11_200, "VGI": 77_400, "FOX": 64_100}
# Covered warrants (HOSE-listed); names follow the real Cxxx<yy><nn> scheme.
_CW = {"CFPT2518": 2_350, "CHPG2525": 1_120, "CMWG2524": 1_860, "CTCB2509": 980,
       "CVHM2601": 1_540, "CMSN2603": 2_010, "CACB2511": 770, "CSTB2512": 1_330}
# VN30 index futures, priced in index points (contract codes as in the audit).
_FUT = {"41I1G8000": 1_872.4, "41I1G9000": 1_869.9, "41I1GC000": 1_865.2}


def build_universe() -> list[Instrument]:
    out: list[Instrument] = []
    for sym, px in _VN30.items():
        out.append(Instrument(sym, HOSE, "stock", px, 6.0, 2_000_000_000, _isin(sym)))
    for sym, px in _HOSE_OTHER.items():
        out.append(Instrument(sym, HOSE, "stock", px, 2.0, 800_000_000, _isin(sym)))
    for sym, px in _HNX.items():
        out.append(Instrument(sym, HNX, "stock", px, 1.0, 400_000_000, _isin(sym)))
    for sym, px in _UPCOM.items():
        out.append(Instrument(sym, UPCOM, "stock", px, 0.6, 600_000_000, _isin(sym)))
    for sym, px in _CW.items():
        out.append(Instrument(sym, HOSE, "cw", px, 0.8, 10_000_000, _isin(sym)))
    # The front month dominates futures volume (>90% in the audit).
    for i, (sym, px) in enumerate(_FUT.items()):
        out.append(Instrument(sym, DERIV, "future", px, 20.0 if i == 0 else 1.0, 0,
                              "VN" + sym))
    return out


VN30 = tuple(_VN30)

# Indices the simulator publishes, with each broker's identifier for them.
#   name      constituents filter                   TCBS indexNumber  DNSE indexTypeCode
INDICES = {
    "VNINDEX": (lambda i: i.kind == "stock" and i.exchange == HOSE, 1, "001", 1_669.38),
    "VN30":    (lambda i: i.symbol in VN30,                         2, "101", 1_948.57),
    "HNX":     (lambda i: i.kind == "stock" and i.exchange == HNX,  3, "002", 228.41),
    "HNX30":   (lambda i: i.kind == "stock" and i.exchange == HNX,  4, "100", 497.10),
    "UPCOM":   (lambda i: i.kind == "stock" and i.exchange == UPCOM, 5, "301", 91.43),
}
