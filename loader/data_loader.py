import yfinance as yf
import pandas as pd
from typing import List, Optional

class Data_Loader:
    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialisiert den Data_Loader. Für yfinance sind api_key und base_url
        oft nicht direkt erforderlich, werden aber zur Kompatibilität mit
        der Architekturdefinition beibehalten.
        """
        self.api_key = api_key
        self.base_url = base_url

    def download_yfinance_market_data(self, tickers: List[str], period: str = "2y") -> Optional[pd.DataFrame]:
        """
        Lädt historische Marktdaten von Yahoo Finance für eine Liste von Ticker-Symbolen.

        Args:
            tickers (List[str]): Eine Liste von Ticker-Symbolen (z.B. ["AAPL", "MSFT"]).
            period (str): Der Zeitraum der Daten (z.B. "1d", "1mo", "1y", "5y", "max").

        Returns:
            Optional[pd.DataFrame]: Ein DataFrame mit den historischen Daten oder None bei einem Fehler.
        """
        if not tickers:
            print("Fehler: Keine Ticker-Symbole zum Herunterladen angegeben.")
            return None

        try:
            # yfinance download kann für mehrere Ticker ein MultiIndex DataFrame zurückgeben
            # Wir holen 'Close'-Preise, können aber auch andere Daten auswählen
            data = yf.download(tickers, period=period)
            if data.empty:
                print(f"Keine Daten für Ticker {tickers} im Zeitraum {period} gefunden.")
                return None

            # Wenn nur ein Ticker angefragt wurde, ist das Ergebnis oft kein MultiIndex
            # Wir stellen sicher, dass wir immer einen konsistenten DataFrame-Typ zurückgeben
            if len(tickers) == 1:
                return data
            else:
                # Für mehrere Ticker geben wir den gesamten DataFrame zurück
                # Der Data_Transformer ist für die Bereinigung zuständig
                return data

        except Exception as e:
            print(f"Fehler beim Herunterladen der yfinance-Daten: {e}")
            return None
