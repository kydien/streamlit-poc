import pandas as pd
import requests
import streamlit as st


class DataProvider:
    def __init__(self, api_key: str):
        # Entferne eventuelle Leerzeichen, die beim Kopieren mitgerutscht sind
        self.api_key = api_key.strip()
        self.base_url = "https://financialmodelingprep.com/stable"

    def get_sp500_symbols(self) -> list:
        """Holt die S&P 500 Liste über den stabilen Financial-Statement-Endpunkt."""
        # Wir nutzen den 'constituents' Endpunkt, der oft zuverlässiger ist
        url = f"{self.base_url}/index-list?apikey={self.api_key}"
        print(f"API {self.api_key}")
        print(f"URL:{url} ")
        try:
            response = requests.get(url, timeout=10)

            # DEBUG-PRINT im Terminal: Was sagt der Server wirklich?
            print(f"[DEBUG] Status Code: {response.status_code}")
            if response.status_code == 403:
                print(
                    "[ERROR] 403: Dein API-Key ist ungültig oder für diesen Endpunkt gesperrt."
                )
                return []

            if response.status_code == 200:
                data = response.json()
                symbols = [item["symbol"] for item in data]
                print(f"[SUCCESS] {len(symbols)} Symbole gefunden.")
                return symbols

            return []
        except Exception as e:
            print(f"[ERROR] Netzwerkfehler: {e}")
        return []

    def get_ratios_batch(self, symbols: list) -> pd.DataFrame:
        """Holt PEG-Ratios für eine Liste von Symbolen (Batch)."""
        # FMP erlaubt Komma-getrennte Listen
        sym_str = ",".join(symbols)
        url = f"{self.base_url}/ratios-ttm/{sym_str}?apikey={self.api_key}"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                return pd.DataFrame(response.json())
            return pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    def get_historical_prices(self, symbol: str) -> pd.Series:
        """Holt die letzten 60 Tage Schlusskurse."""
        url = f"{self.base_url}/historical-price-full/{symbol}?timeseries=60&apikey={self.api_key}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json().get("historical", [])
                df = pd.DataFrame(data)
                # FMP liefert neueste Daten zuerst -> umkehren für RSI
                return df["close"].iloc[::-1]
            return pd.Series()
        except Exception:
            return pd.Series()

    def test_connection(self) -> dict | None:
        """Nutzt den stabilsten Endpunkt für den Key-Check."""
        # /quote/ ist im Free-Tier fast immer offen
        # url = f"{self.base_url}/quote/AAPL?apikey={self.api_key}"
        url = f"{self.base_url}/sp500-constituent?apikey={self.api_key}"
        print(f"API {self.api_key}")
        print(f"URL:{url} ")

        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                print(f"\n[ERFOLG] {len(data)} Unternehmen im S&P 500 gefunden.\n")
                print("-" * 50)
                print(f"{'Symbol':<10} | {'Name':<30}")
                print("-" * 50)

                # Die ersten 20 Symbole ausgeben
                for entry in data[:20]:
                    symbol = entry.get("symbol")
                    name = entry.get("name")
                    print(f"{symbol:<10} | {name:<30}")

                print("-" * 50)
                print(f"... und {len(data) - 20} weitere.")

            else:
                print(f"[FEHLER] Status Code: {response.status_code}")
                print(f"Antwort: {response.text}")

        except Exception as e:
            print(f"[CRITICAL] Fehler bei der Anfrage: {e}")
