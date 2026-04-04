import io

import pandas as pd
import requests
import streamlit as st
import yfinance as yf


class DataProvider:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    @st.cache_data(ttl=86400)
    def get_sp500_symbols(_self) -> list:
        print("\n[INFO] Lade S&P 500 Liste von Wikipedia...")
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        try:
            response = requests.get(url, headers=_self.headers, timeout=10)
            tables = pd.read_html(io.StringIO(response.text), flavor="bs4")
            symbols = tables[0]["Symbol"].tolist()
            print(f"[SUCCESS] {len(symbols)} Symbole geladen.")
            return symbols
        except Exception as e:
            print(f"[ERROR] Wikipedia S&P 500 fehlgeschlagen: {e}")
            return []

    @st.cache_data(ttl=86400)
    def get_dax_symbols(_self) -> list:
        print("\n[INFO] Lade DAX Liste von Wikipedia...")
        url = "https://de.wikipedia.org/wiki/DAX"
        try:
            response = requests.get(url, headers=_self.headers, timeout=10)
            tables = pd.read_html(io.StringIO(response.text), flavor="bs4")
            for table in tables:
                if "Symbol" in table.columns:
                    symbols = [str(s).strip() + ".DE" for s in table["Symbol"].tolist()]
                    print(f"[SUCCESS] {len(symbols)} DAX Symbole geladen.")
                    return symbols
            return []
        except Exception as e:
            print(f"[ERROR] Wikipedia DAX fehlgeschlagen: {e}")
            return []

    def get_stock_data(self, symbol: str) -> tuple[dict, pd.Series]:
        """Holt Daten und gibt Status im Terminal aus."""
        print(
            f"[SCAN] Analysiere: {symbol: <6}", end="\r"
        )  # \r überschreibt die Zeile für Sauberkeit

        try:
            ticker = yf.Ticker(symbol)

            # 1. Fundamentaldaten
            info = ticker.info
            peg = info.get("pegRatio")

            # 2. Historie
            hist = ticker.history(period="3mo")

            # Terminal Detail-Log (optional, falls du jede Zeile einzeln willst)
            # print(f"[DATA] {symbol} - PEG: {peg} - Hist: {len(hist)} Tage")

            if hist.empty:
                print(f"[WARN] {symbol}: Keine Historie gefunden.")
                return info, pd.Series()

            return info, hist["Close"]

        except Exception as e:
            print(f"\n[ERROR] {symbol}: Datenabruf fehlgeschlagen: {e}")
            return {}, pd.Series()
