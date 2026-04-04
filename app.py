import io

import pandas as pd
import pandas_ta as ta
import requests  # WICHTIG: Füge dies oben bei deinen Imports hinzu
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Aktien-Screener", layout="wide")
st.title("🎯 Multi-Dimensionaler Aktien-Scanner")

# --- FUNKTIONEN ---


@st.cache_data(ttl=86400)
def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)

    # Sicherstellen, dass die Antwort nicht leer ist
    if response.status_code != 200:
        st.error(f"Fehler beim Laden von Wikipedia: {response.status_code}")
        return []

    # WICHTIG: response.text in StringIO einpacken
    table = pd.read_html(io.StringIO(response.text), flavor="bs4")
    df = table[0]
    return df["Symbol"].tolist()


@st.cache_data(ttl=86400)
def get_dax_tickers():
    url = "https://de.wikipedia.org/wiki/DAX"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    # tables = pd.read_html(response.text)
    tables = pd.read_html(response.text, flavor="bs4")

    for table in tables:
        if "Symbol" in table.columns and len(table) > 35:
            return [str(s).replace(" ", "") + ".DE" for s in table["Symbol"].tolist()]
    return []


def screen_stocks(ticker_list, peg_max, rsi_max):
    results = []
    progress_bar = st.progress(0)

    for i, symbol in enumerate(ticker_list):
        try:
            # Fortschrittsanzeige
            progress_bar.progress((i + 1) / len(ticker_list))

            ticker = yf.Ticker(symbol)
            info = ticker.info

            # 1. PEG Filter (Fundamentale Bewertung)
            peg = info.get("pegRatio")
            if peg is None or peg >= peg_max:
                continue

            # 2. RSI Filter (Technische Überverkauftheit)
            hist = ticker.history(period="1mo")
            if len(hist) < 15:
                continue
            rsi = ta.rsi(hist["Close"], length=14).iloc[-1]

            if rsi < rsi_max:
                results.append(
                    {
                        "Symbol": symbol,
                        "Name": info.get("shortName", "N/A"),
                        "PEG": peg,
                        "RSI": round(rsi, 2),
                        "Preis": info.get("currentPrice"),
                    }
                )
        except:
            continue
    return results


# --- DASHBOARD BEDIENUNG ---

st.sidebar.header("Filter-Einstellungen")
target_index = st.sidebar.selectbox("Index wählen", ["S&P 500", "DAX"])
peg_input = st.sidebar.slider("Maximales PEG (Value)", 0.1, 2.0, 1.0)
rsi_input = st.sidebar.slider("Maximaler RSI (Oversold)", 10, 40, 25)

# VIX Check für das Marktumfeld
vix_data = yf.Ticker("^VIX").history(period="1d")
current_vix = vix_data["Close"].iloc[-1]
st.metric(
    "VIX Index (Marktangst)",
    f"{current_vix:.2f}",
    delta="Hohe Volatilität" if current_vix > 25 else "Ruhiger Markt",
    delta_color="inverse",
)

if st.button(f"Scan {target_index} starten"):
    tickers = get_sp500_tickers() if target_index == "S&P 500" else get_dax_tickers()
    st.info(f"Scanne {len(tickers)} Aktien. Bitte warten...")

    hits = screen_stocks(tickers, peg_input, rsi_input)

    if hits:
        st.success(f"{len(hits)} Treffer gefunden!")
        st.table(pd.DataFrame(hits))
    else:
        st.warning("Keine Aktie erfüllt aktuell alle Kriterien.")
