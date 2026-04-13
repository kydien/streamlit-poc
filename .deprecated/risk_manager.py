from typing import Any, Dict, List, Optional

import pandas as pd
import yfinance as yf


def _download_market_data(tickers: List[str], period: str = "2y") -> Optional[pd.DataFrame]:
    """
    Lädt Marktdaten für die gegebenen Ticker herunter und bereitet sie auf.
    Gibt ein DataFrame mit den 'Close'-Preisen zurück oder None bei Fehlern.
    """
    try:
        # Batch-Download zur Vermeidung von Rate-Limits
        # period="2y" stellt sicher, dass wir genug Daten für den SMA 200 haben
        data = yf.download(tickers, period=period, progress=False, auto_adjust=True)

        if data is None or data.empty:
            return None

        # Sicherer Zugriff auf die 'Close' Spalte, falls ein MultiIndex vorhanden ist
        if isinstance(data.columns, pd.MultiIndex):
            close_data = data["Close"]
        else:
            close_data = data

        # Sicherstellen, dass close_data ein DataFrame ist, auch wenn nur ein Ticker angefragt wurde
        if isinstance(close_data, pd.Series):
            close_data = close_data.to_frame()

        # Validierung: Prüfen ob es ein DataFrame ist und Spalten hat
        if not isinstance(close_data, pd.DataFrame) or close_data.empty:
            return None

        return close_data

    except Exception as e:
        print(f"Fehler beim Herunterladen der Marktdaten: {e}")
        return None


def fetch_raw_risk_data() -> Optional[Dict[str, Any]]:
    """
    Sammelt alle notwendigen Marktdaten in einem einzigen Batch-Request und übergibt sie
    an die Verarbeitungsfunktion. Trennt Datenbeschaffung strikt von der UI.
    """
    tickers = ["^TNX", "^IRX", "HYG", "IEI", "^GSPC", "^VIX"]

    df_market_data = _download_market_data(tickers, period="2y")

    if df_market_data is None:
        return None

    try:
        # Fange potenzielle Fehler während der Metrikberechnung ab
        return _process_metrics(df_market_data)
    except Exception as e:
        print(f"Fehler bei der Metrikberechnung: {e}")
        return None


def _process_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Interne Hilfsfunktion zur Berechnung der mathematischen Kennzahlen.
    Arbeitet rein auf dem übergebenen DataFrame.
    """

    # Helferfunktion für sicheren Zugriff
    def get_last_value_or_nan(series: pd.Series):
        return float(series.iloc[-1]) if not series.empty else float("nan")

    def get_sma_or_nan(series: pd.Series, window: int):
        return (
            float(series.rolling(window=window).mean().iloc[-1])
            if len(series) >= window
            else float("nan")
        )

    # 1. Long-term: Yield Curve (10Y - 3M)
    yield_series = (df["^TNX"] - df["^IRX"]).dropna()
    yield_spread = get_last_value_or_nan(yield_series)

    # 2. Medium-term: Credit Spreads Proxy (HYG / IEI)
    credit_series = (df["HYG"] / df["IEI"]).dropna()
    # Sicherstellen, dass genügend Daten für 200-Tage SMA vorhanden sind
    if len(credit_series) < 200:
        # Hier könnte eine Warnung geloggt oder ein Fehler gemeldet werden
        credit_50_sma = float("nan")
        credit_200_sma = float("nan")
    else:
        credit_50_sma = float(credit_series.rolling(window=50).mean().iloc[-1])
        credit_200_sma = float(credit_series.rolling(window=200).mean().iloc[-1])

    # 3. Short-term: S&P 500 Trend & VIX
    sp500_series = df["^GSPC"].dropna()
    vix_series = df["^VIX"].dropna()

    # Berechnungen
    current_price = float(sp500_series.iloc[-1])
    # Sicherstellen, dass genügend Daten für SMA 200 vorhanden sind
    if len(sp500_series) < 200:
        sma200 = float("nan")
    else:
        sma200 = float(sp500_series.rolling(window=200).mean().iloc[-1])

    return {
        "long_term": {
            "yield_spread": float(yield_series.iloc[-1]),
            "is_inverted": yield_series.iloc[-1] < 0,
        },
        "medium_term": {
            "credit_proxy_value": float(credit_series.iloc[-1]),
            "credit_50_sma": credit_50_sma,
            "credit_200_sma": credit_200_sma,
        },
        "short_term": {
            "vix_current": float(vix_series.iloc[-1]),
            "sp500_price": current_price,
            "sma200": sma200,
            "is_bullish": current_price > sma200 if not pd.isna(sma200) else False,
        },
    }


def display_risk_metrics(metrics: Dict[str, Any]):
    """
    Gibt die berechneten Risikometriken formatiert im Terminal aus.
    """
    if not metrics:
        print("Keine Risikometriken zur Anzeige verfügbar.")
        return

    print("\n--- Risikometriken Zusammenfassung ---")

    # Long-term
    print("\n[1] Langfristig (Yield Curve):")
    yield_spread = metrics["long_term"]["yield_spread"]
    is_inverted = metrics["long_term"]["is_inverted"]
    print(f"  Renditedifferenz (10Y - 3M): {yield_spread:.2f} %")
    print(f"  Invertierte Zinskurve: {'Ja' if is_inverted else 'Nein'}")
    if is_inverted:
        print(
            "  Hinweis: Eine invertierte Zinskurve kann ein Indikator für eine bevorstehende Rezession sein."
        )

    # Medium-term
    print("\n[2] Mittelfristig (Credit Spreads Proxy):")
    credit_proxy_value = metrics["medium_term"]["credit_proxy_value"]
    credit_50_sma = metrics["medium_term"]["credit_50_sma"]
    credit_200_sma = metrics["medium_term"]["credit_200_sma"]
    print(f"  Kredit-Spread Proxy (HYG/IEI): {credit_proxy_value:.3f}")
    if not pd.isna(credit_50_sma):
        print(f"  50-Tage SMA Kredit-Proxy: {credit_50_sma:.3f}")
    if not pd.isna(credit_200_sma):
        print(f"  200-Tage SMA Kredit-Proxy: {credit_200_sma:.3f}")

    # Short-term
    print("\n[3] Kurzfristig (S&P 500 & VIX):")
    vix_current = metrics["short_term"]["vix_current"]
    sp500_price = metrics["short_term"]["sp500_price"]
    sma200 = metrics["short_term"]["sma200"]
    is_bullish = metrics["short_term"]["is_bullish"]
    print(f"  VIX (Volatilitätsindex): {vix_current:.2f}")
    print(f"  S&P 500 Aktueller Preis: {sp500_price:.2f}")
    if not pd.isna(sma200):
        print(f"  S&P 500 200-Tage SMA: {sma200:.2f}")
        print(f"  S&P 500 Bullisch (Preis > SMA200): {'Ja' if is_bullish else 'Nein'}")
    if vix_current > 20:  # Beispielwert für erhöhte Volatilität
        print("  Hinweis: Ein hoher VIX deutet auf erhöhte Marktunsicherheit hin.")
    if not is_bullish and not pd.isna(sma200):
        print(
            "  Hinweis: Der S&P 500 notiert unter dem 200-Tage gleitenden Durchschnitt."
        )

    print("\n--- Ende der Zusammenfassung ---")


def generate_action_recommendations(metrics: Dict[str, Any]) -> List[str]:
    """
    Generiert Handlungsempfehlungen basierend auf den Risikometriken.
    """
    recommendations = []

    if not metrics:
        recommendations.append(
            "Keine Risikometriken verfügbar, keine Empfehlungen möglich."
        )
        return recommendations

    # 1. Langfristig: Yield Curve (10Y - 3M Spread)
    yield_spread = metrics["long_term"]["yield_spread"]
    if yield_spread > 0.20:
        recommendations.append(
            "[LANGFRISTIG - GRÜN]: Zinskurve normal. Achte weiterhin auf fundamentale Stärke und langfristige Wachstumstrends."
        )
    elif -0.10 <= yield_spread <= 0.20:
        recommendations.append(
            "[LANGFRISTIG - GELB]: Fokus auf Qualität, reduziere gehebelte Positionen. Prüfe Cash-Reserven für eine potenzielle Durststrecke (2 Jahre)."
        )
    else:  # yield_spread < -0.10
        recommendations.append(
            "[LANGFRISTIG - ROT]: Defensive Umschichtung. Reduziere Übergewichtung in zyklischen Sektoren (Banken, Immobilien). Erhöhe den Anteil an liquiden Mitteln oder kurzlaufenden Staatsanleihen."
        )

    # 2. Mittelfristig: Credit Spreads (HYG/IEI Proxy)
    credit_proxy_value = metrics["medium_term"]["credit_proxy_value"]
    credit_50_sma = metrics["medium_term"]["credit_50_sma"]
    credit_200_sma = metrics["medium_term"]["credit_200_sma"]

    if pd.isna(credit_50_sma) or pd.isna(credit_200_sma):
        recommendations.append(
            "[MITTELFRISTIG]: Nicht genügend Daten für Credit Spread SMAs, keine präzise Empfehlung möglich."
        )
    elif credit_proxy_value > credit_50_sma:
        recommendations.append(
            "[MITTELFRISTIG - GRÜN]: Kreditmärkte stabil. Suche nach Opportunitäten in Unternehmen mit solider Bilanz und nachhaltigem Geschäftsmodell."
        )
    elif credit_200_sma < credit_proxy_value <= credit_50_sma:
        recommendations.append(
            "[MITTELFRISTIG - GELB]: Kaufsperre für spekulative Einzelaktien. 'Watchlist-Modus': Welche Titel zeigen relative Stärke zum Gesamtmarkt?"
        )
    else:  # credit_proxy_value <= credit_200_sma
        recommendations.append(
            "[MITTELFRISTIG - ROT]: Risikoreduktion. Verkauf von Werten mit hoher Verschuldung oder schwachem Cashflow. Kreditmärkte lügen selten; wenn sie drehen, folgt der Aktienmarkt meist mit Verzögerung."
        )

    # 3. Kurzfristig: Markttechnik & Volatilität (VIX & SMA200)
    vix_current = metrics["short_term"]["vix_current"]
    sp500_price = metrics["short_term"]["sp500_price"]
    sma200 = metrics["short_term"]["sma200"]

    if pd.isna(sma200):
        recommendations.append(
            "[KURZFRISTIG]: Nicht genügend Daten für S&P 500 SMA200, keine präzise Empfehlung möglich."
        )
    elif vix_current < 20 and sp500_price > sma200:
        recommendations.append(
            "[KURZFRISTIG - GRÜN]: Markttechnik und Volatilität unauffällig. Aktive Suche nach Einstiegspunkten bei bewährten Qualitätsaktien möglich."
        )
    elif (20 <= vix_current < 30) or (sp500_price < sma200 and vix_current < 30):
        recommendations.append(
            "[KURZFRISTIG - GELB]: Rebalancing: Bringe die Gewichtungen auf das Zielniveau zurück. Trailing Stops: Ziehe Stop-Loss-Marken eng an den aktuellen Preis heran. Kein neues Kapital: Warte auf eine Beruhigung (VIX sinkend)."
        )


if __name__ == "__main__":
    try:
        print("Starte Risikomanagement-Analyse...")
        risk_metrics = fetch_raw_risk_data()
        if risk_metrics:
            display_risk_metrics(risk_metrics)
            print("\n--- Handlungsempfehlungen ---")
            recommendations = generate_action_recommendations(risk_metrics)
            for i, rec in enumerate(recommendations):
                print(f"- {rec}")
            print("----------------------------")
        else:
            print("Fehler: Konnte keine Risikometriken abrufen.")
    except KeyboardInterrupt:
        print("\nAnalyse durch Benutzer abgebrochen.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
