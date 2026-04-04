import pandas as pd
import pandas_ta as ta


def calculate_rsi(price_data: pd.Series, window: int = 14) -> float | None:
    if price_data.empty or len(price_data) < window + 1:
        return None
    try:
        # Direkter Aufruf ohne .ta Accessor (Robuster!)
        rsi_series = ta.rsi(price_data, length=window)  # type:ignore
        if rsi_series is None or rsi_series.empty:
            return None
        return float(rsi_series.iloc[-1])
    except Exception:
        return None


def evaluate_strategy(peg, rsi, max_peg, max_rsi) -> bool:
    if peg is None or rsi is None:
        return False
    return peg < max_peg and rsi < max_rsi
