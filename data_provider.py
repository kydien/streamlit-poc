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
            st.error(f"S&P 500 Fehler: {e}")
            return []

    @st.cache_data(ttl=86400)
    def get_dax_symbols(_self) -> list:
        url = "https://de.wikipedia.org/wiki/DAX"
        try:
            response = requests.get(url, headers=_self.headers, timeout=10)
            tables = pd.read_html(io.StringIO(response.text), flavor="bs4")
            # Suche die Tabelle mit den DAX-Werten
            for table in tables:
                if "Symbol" in table.columns:
                    symbols = [str(s).strip() + ".DE" for s in table["Symbol"].tolist()]
                    print(f"[SUCCESS] {len(symbols)} DAX Symbole geladen.")
                    return symbols
            return []
        except Exception as e:
            st.error(f"DAX Fehler: {e}")
            return []

    def get_stock_data(self, symbol: str) -> tuple[dict, pd.Series]:
        ticker = yf.Ticker(symbol)
        # 3 Monate Historie für einen stabilen RSI(14)
        hist = ticker.history(period="3mo")
        return ticker.info, hist["Close"]
