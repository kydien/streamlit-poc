import yfinance as yf
import pandas as pd

def get_risk_metrics():
    # Long-term: Yield Curve (10Y - 2Y)
    # Tickers: ^TNX (10Y), ^IRX (3M) oder custom 2Y
    yield_data = yf.download(["^TNX", "^IRX"], period="1y")['Close']
    yield_spread = yield_data["^TNX"] - yield_data["^IRX"]

    # Medium-term: Credit Spreads (BofA High Yield Index vs Treasury)
    # Ersatz-Proxy: HYG (High Yield ETF) vs IEI (Interm. Treasury ETF)
    credit_data = yf.download(["HYG", "IEI"], period="1y")['Close']
    credit_spread = credit_data["HYG"] / credit_data["IEI"] # Ratio als Proxy

    # Short-term: VIX & Trend (SMA 200)
    market = yf.download("^GSPC", period="2y")['Close']
    vix = yf.download("^VIX", period="5d")['Close'].iloc[-1]
    
    current_price = market.iloc[-1]
    sma200 = market.rolling(window=200).mean().iloc[-1]
    trend_signal = "Bullish" if current_price > sma200 else "Bearish"

    return {
        "yield_spread": yield_spread.iloc[-1],
        "credit_proxy": credit_spread.iloc[-1],
        "vix": vix,
        "trend": trend_signal
    }
