import os
import json
import logging
from typing import Dict, Optional, Any, List

logger = logging.getLogger("finpilot.symbol_mapper")

# Core Indian symbols and aliases
KNOWN_SYMBOLS: Dict[str, Dict[str, Any]] = {
    "NIFTY 50": {
        "symbol": "NIFTY 50",
        "name": "Nifty 50 Index",
        "exchange": "NSE",
        "kite_symbol": "NSE:NIFTY 50",
        "instrument_token": 256265,
        "alpha_symbol": "^NSEI",
        "sector": "Index",
        "is_index": True
    },
    "SENSEX": {
        "symbol": "SENSEX",
        "name": "BSE Sensex Index",
        "exchange": "BSE",
        "kite_symbol": "BSE:SENSEX",
        "instrument_token": 265,
        "alpha_symbol": "^BSESN",
        "sector": "Index",
        "is_index": True
    },
    "BANK NIFTY": {
        "symbol": "BANK NIFTY",
        "name": "Nifty Bank Index",
        "exchange": "NSE",
        "kite_symbol": "NSE:NIFTY BANK",
        "instrument_token": 260105,
        "alpha_symbol": "^NSEBANK",
        "sector": "Banking Index",
        "is_index": True
    },
    "RELIANCE": {
        "symbol": "RELIANCE",
        "name": "Reliance Industries Ltd",
        "exchange": "NSE",
        "kite_symbol": "NSE:RELIANCE",
        "instrument_token": 738561,
        "bse_code": "500325",
        "alpha_symbol": "RELIANCE.BSE",
        "sector": "Energy & Telecom"
    },
    "TCS": {
        "symbol": "TCS",
        "name": "Tata Consultancy Services Ltd",
        "exchange": "NSE",
        "kite_symbol": "NSE:TCS",
        "instrument_token": 2953217,
        "bse_code": "532540",
        "alpha_symbol": "TCS.BSE",
        "sector": "Information Technology"
    },
    "INFY": {
        "symbol": "INFY",
        "name": "Infosys Ltd",
        "exchange": "NSE",
        "kite_symbol": "NSE:INFY",
        "instrument_token": 408065,
        "bse_code": "500209",
        "alpha_symbol": "INFY", # Listed on NYSE as INFY
        "sector": "Information Technology"
    },
    "HDFCBANK": {
        "symbol": "HDFCBANK",
        "name": "HDFC Bank Ltd",
        "exchange": "NSE",
        "kite_symbol": "NSE:HDFCBANK",
        "instrument_token": 341249,
        "bse_code": "500180",
        "alpha_symbol": "HDB", # Listed on NYSE as HDB
        "sector": "Banking & Finance"
    },
    "ICICIBANK": {
        "symbol": "ICICIBANK",
        "name": "ICICI Bank Ltd",
        "exchange": "NSE",
        "kite_symbol": "NSE:ICICIBANK",
        "instrument_token": 1270529,
        "bse_code": "532174",
        "alpha_symbol": "IBN", # Listed on NYSE as IBN
        "sector": "Banking & Finance"
    },
    "SBIN": {
        "symbol": "SBIN",
        "name": "State Bank of India",
        "exchange": "NSE",
        "kite_symbol": "NSE:SBIN",
        "instrument_token": 779521,
        "bse_code": "500112",
        "alpha_symbol": "SBIN.BSE",
        "sector": "Banking & Finance"
    },
    "BHARTIARTL": {
        "symbol": "BHARTIARTL",
        "name": "Bharti Airtel Ltd",
        "exchange": "NSE",
        "kite_symbol": "NSE:BHARTIARTL",
        "instrument_token": 2714625,
        "bse_code": "532454",
        "alpha_symbol": "BHARTIARTL.BSE",
        "sector": "Telecommunications"
    },
    "ITC": {
        "symbol": "ITC",
        "name": "ITC Ltd",
        "exchange": "NSE",
        "kite_symbol": "NSE:ITC",
        "instrument_token": 424961,
        "bse_code": "500875",
        "alpha_symbol": "ITC.BSE",
        "sector": "FMCG"
    },
    "KOTAKBANK": {
        "symbol": "KOTAKBANK",
        "name": "Kotak Mahindra Bank Ltd",
        "exchange": "NSE",
        "kite_symbol": "NSE:KOTAKBANK",
        "instrument_token": 492033,
        "bse_code": "500247",
        "alpha_symbol": "KOTAKBANK.BSE",
        "sector": "Banking & Finance"
    },
    "LT": {
        "symbol": "LT",
        "name": "Larsen & Toubro Ltd",
        "exchange": "NSE",
        "kite_symbol": "NSE:LT",
        "instrument_token": 2939649,
        "bse_code": "500510",
        "alpha_symbol": "LT.BSE",
        "sector": "Engineering & Infra"
    }
}


class SymbolMapper:
    """Centralized symbol normalization and instrument token resolution."""

    def __init__(self):
        self._symbols = dict(KNOWN_SYMBOLS)
        self._token_map: Dict[int, str] = {
            v["instrument_token"]: k for k, v in KNOWN_SYMBOLS.items() if "instrument_token" in v
        }

    def normalize(self, raw_symbol: str) -> str:
        """Strip exchange prefixes and whitespace, e.g. NSE:RELIANCE -> RELIANCE."""
        s = raw_symbol.strip().upper()
        if s.startswith("NSE:"):
            s = s[4:]
        elif s.startswith("BSE:"):
            s = s[4:]
        return s

    def get_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        norm = self.normalize(symbol)
        return self._symbols.get(norm)

    def get_kite_symbol(self, symbol: str) -> str:
        norm = self.normalize(symbol)
        info = self._symbols.get(norm)
        if info and "kite_symbol" in info:
            return info["kite_symbol"]
        return f"NSE:{norm}"

    def get_alpha_symbol(self, symbol: str) -> str:
        norm = self.normalize(symbol)
        info = self._symbols.get(norm)
        if info and "alpha_symbol" in info:
            return info["alpha_symbol"]
        return f"{norm}.BSE"

    def get_token(self, symbol: str) -> Optional[int]:
        norm = self.normalize(symbol)
        info = self._symbols.get(norm)
        if info:
            return info.get("instrument_token")
        return None

    def get_symbol_by_token(self, token: int) -> Optional[str]:
        return self._token_map.get(token)

    def list_symbols(self) -> List[str]:
        return list(self._symbols.keys())

    def update_from_instruments(self, instruments: List[Dict[str, Any]]) -> None:
        """Dynamically populate symbol map from downloaded Kite instruments."""
        for inst in instruments:
            trading_sym = inst.get("tradingsymbol", "")
            exchange = inst.get("exchange", "NSE")
            token = inst.get("instrument_token")
            if not trading_sym or not token:
                continue
            if trading_sym not in self._symbols:
                self._symbols[trading_sym] = {
                    "symbol": trading_sym,
                    "name": inst.get("name") or trading_sym,
                    "exchange": exchange,
                    "kite_symbol": f"{exchange}:{trading_sym}",
                    "instrument_token": int(token),
                    "sector": "Equity"
                }
            if token:
                self._token_map[int(token)] = trading_sym


symbol_mapper = SymbolMapper()
