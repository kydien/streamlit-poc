import pandas as pd
import streamlit as st

from analysis_engine import calculate_rsi, evaluate_strategy
from data_provider import DataProvider

st.set_page_config(page_title="Stock Intelligence", layout="wide")

# Sidebar für API-Key und Filter
st.sidebar.header("Konfiguration")
api_key = st.sidebar.text_input("FMP API Key", type="password")
m_peg = st.sidebar.slider("Maximales PEG", 0.1, 2.0, 1.0)
m_rsi = st.sidebar.slider("Maximaler RSI", 10, 60, 35)

if not api_key:
    st.info("Bitte gib deinen FMP API Key in der Sidebar ein.")
    st.stop()

provider = DataProvider(api_key)

if st.button("🚀 Profi-Scan starten"):
    # 1. Symbole laden
    with st.spinner("Lade S&P 500..."):
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX"]
        # symbols = provider.get_sp500_symbols()

    if not symbols:
        st.error("API Fehler: Konnte Symbole nicht laden. Key korrekt?")
        st.stop()

    # 2. Fundamentaldaten-Filter (Batch)
    # Wir laden erst die Kennzahlen für die ersten 100 (Free Tier Limit oft 100)
    with st.spinner("Prüfe PEG-Ratios..."):
        fundamentals = provider.get_ratios_batch(symbols[:100])

    if fundamentals.empty:
        st.warning("Keine PEG-Daten gefunden. Prüfe deinen API-Key-Status.")
        st.stop()

    # Wir filtern sofort im Speicher (superschnell)
    # FMP nutzt 'pegRatioTTM'
    candidates = fundamentals[fundamentals["pegRatioTTM"] < m_peg]
    st.write(f"Gefiltert: {len(candidates)} von 100 Aktien haben ein PEG < {m_peg}")

    hits = []
    progress = st.progress(0)

    # 3. RSI Check für Kandidaten
    for i, (_, row) in enumerate(candidates.iterrows()):
        symbol = row["symbol"]
        progress.progress((i + 1) / len(candidates))

        prices = provider.get_historical_prices(symbol)
        rsi_val = calculate_rsi(prices)

        print(f"[SCAN] {symbol} | PEG: {row['pegRatioTTM']:.2f} | RSI: {rsi_val}")

        if rsi_val and rsi_val < m_rsi:
            hits.append(
                {
                    "Symbol": symbol,
                    "PEG": round(row["pegRatioTTM"], 2),
                    "RSI": round(rsi_val, 2),
                }
            )

    # 4. Resultate
    if hits:
        st.balloons()
        st.table(pd.DataFrame(hits))
    else:
        st.info("Aktuell keine Treffer für diese Kombination.")
