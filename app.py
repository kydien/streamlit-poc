import pandas as pd
import streamlit as st

from analysis_engine import calculate_rsi, evaluate_strategy

# Import der neuen Module (Struktur-Check: Dateien müssen im selben Ordner liegen)
from data_provider import DataProvider

# --- UI SETUP ---
st.set_page_config(page_title="Aktien-Scanner", layout="wide")
st.title("🎯 Multi-Dimensionaler Aktien-Scanner")

# Sidebar für Parameter (Benutzereingaben)
st.sidebar.header("Filter-Einstellungen")
target_index = st.sidebar.selectbox("Index wählen", ["S&P 500", "DAX"])
max_peg = st.sidebar.slider("Maximales PEG (Value)", 0.1, 2.0, 1.0)
max_rsi = st.sidebar.slider("Maximaler RSI (Oversold)", 10, 50, 30)

# Initialisierung des Daten-Providers (Infrastruktur-Klasse)
provider = DataProvider()


def run_main_scan():
    """Hauptlogik der App: Orchestrierung von Import und Analyse."""

    # 1. Symbole holen über den DataProvider
    with st.spinner(f"Lade Symbole für {target_index}..."):
        if target_index == "S&P 500":
            symbols = provider.get_sp500_symbols()
        else:
            # Annahme: Du hast get_dax_symbols() im Provider implementiert
            symbols = provider.get_dax_symbols()

    if not symbols:
        st.error("Keine Symbole gefunden. Bitte Internetverbindung/API prüfen.")
        return

    hits = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    # 2. Iteration über alle Aktien
    for i, symbol in enumerate(symbols):
        # UI Update
        progress_bar.progress((i + 1) / len(symbols))
        status_text.text(f"Analysiere {symbol} ({i + 1}/{len(symbols)})...")

        try:
            # Daten abrufen
            info, history = provider.get_stock_data(symbol)

            # Analyse-Logik delegieren
            current_rsi = calculate_rsi(history)
            current_peg = info.get("pegRatio")

            # Strategie-Check (Saubere Trennung von der UI)
            if evaluate_strategy(current_peg, current_rsi, max_peg, max_rsi):
                hits.append(
                    {
                        "Symbol": symbol,
                        "Name": info.get("shortName", "N/A"),
                        "PEG": current_peg,
                        "RSI": round(current_rsi, 2) if current_rsi else "N/A",
                        "Preis": info.get("currentPrice", "N/A"),
                    }
                )
        except Exception:
            # Einzelausfälle (z.B. Delisted Stocks) ignorieren
            continue

    # 3. Ergebnisanzeige
    status_text.empty()
    if hits:
        st.success(f"{len(hits)} Treffer gefunden!")
        st.table(pd.DataFrame(hits))
    else:
        st.info(
            "Der Scan war erfolgreich, aber keine Aktie erfüllt derzeit alle Kriterien."
        )


# Start-Button
if st.button(f"Scan {target_index} jetzt starten"):
    run_main_scan()
