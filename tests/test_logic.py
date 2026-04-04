import os
import sys

import pandas as pd

from analysis_engine import calculate_rsi, evaluate_strategy

# Dieser Block erlaubt es dem Skript, die Dateien im Ordner darüber zu sehen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# JETZT kannst du die richtige Datei importieren
from analysis_engine import calculate_rsi, evaluate_strategy


def run_logic_test():
    print("Test der Logik-Engine läuft...")
    # Wir faken 3 Szenarien
    test_cases = [
        {
            "name": "Perfekter Treffer",
            "peg": 0.8,
            "prices": [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30],
        },
        {
            "name": "Zu teuer (PEG)",
            "peg": 2.5,
            "prices": [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30],
        },
        {
            "name": "Nicht überverkauft",
            "peg": 0.7,
            "prices": [
                100,
                101,
                102,
                103,
                104,
                105,
                106,
                107,
                108,
                109,
                110,
                111,
                112,
                113,
                114,
            ],
        },
        {"name": "Fehlende Daten", "peg": None, "prices": [50, 45, 40]},
    ]

    print(f"{'Testfall':<20} | {'RSI':<8} | {'Treffer?':<10}")
    print("-" * 45)

    for case in test_cases:
        # RSI berechnen (wir nutzen eine künstliche Serie)
        price_series = pd.Series(case["prices"])
        rsi_val = calculate_rsi(price_series, window=5)  # Kleines Fenster für Testdaten

        # Strategie prüfen
        is_hit = evaluate_strategy(case["peg"], rsi_val, max_peg=1.0, max_rsi=30)

        rsi_str = f"{rsi_val:.2f}" if rsi_val else "N/A"
        print(f"{case['name']:<20} | {rsi_str:<8} | {str(is_hit):<10}")


if __name__ == "__main__":
    run_logic_test()
