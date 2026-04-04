import pandas as pd


def calculate_rsi(price_data: pd.Series, window: int = 14) -> float | None:
    """Berechnet den RSI für eine Schlusskurs-Serie."""
    if len(price_data) < window + 1:
        return None
    rsi_series = price_data.ta.rsi(price_data, length=window)
    return rsi_series.iloc[-1] if not rsi_series.empty else None


def evaluate_strategy(
    peg: float | None, rsi: float | None, max_peg: float, max_rsi: float
) -> bool:
    """
    Kern der Strategie: PEG < max_peg UND RSI < max_rsi.
    Gibt True zurück, wenn beide Kriterien erfüllt sind.
    """
    if peg is None or rsi is None:
        return False
    return peg < max_peg and rsi < max_rsi
