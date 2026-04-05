# import requests
# import streamlit as st
from data_provider import DataProvider

# WICHTIG: Erst die Standard-Bibliotheken, dann deine eigenen
# try:
#     from data_provider import DataProvider
# except ImportError:
#     st.error("Datei 'data_provider.py' nicht im Hauptverzeichnis gefunden!")
#     st.stop()

# st.title("🛠️ FMP API Connection Check")

# # Key-Eingabe
# api_key = st.sidebar.text_input(
#     "FMP API Key",
#     type="password",
#     help="Kopiere den Key direkt aus deinem FMP Dashboard",
# )

# if st.button("🔌 Verbindung testen"):
#     if not api_key:
#         st.warning("Bitte gib einen API-Key ein.")
#     else:
#         provider = DataProvider(api_key)
#         with st.spinner("Prüfe Verbindung zu FMP..."):
#             res = provider.test_connection()

#             if res["data"]:
#                 st.success(f"✅ Verbindung steht! Aktie: {res['data'].get('name')}")
#                 st.metric("Kurs (AAPL)", f"{res['data'].get('price')} USD")
#             else:
#                 st.error(f"❌ {res['error']}")
#                 st.info("Hinweis: Keys werden oft erst nach E-Mail-Bestätigung aktiv.")




if __name__ == "__main__":
    api_key = "3PDjTgOXt0PVNmFl1buyOIyujOgtCNia"
    provider = DataProvider(api_key)
    provider.test_connection()
