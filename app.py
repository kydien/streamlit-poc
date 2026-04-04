import streamlit as st

from data_provider import DataProvider

st.title("🛠️ FMP API Connection Check")

api_key = st.sidebar.text_input("FMP API Key eingeben", type="password")

if st.button("🔌 Verbindung testen"):
    if not api_key:
        st.warning("Bitte erst einen Key eingeben!")
    else:
        provider = DataProvider(api_key)
        with st.spinner("Prüfe Verbindung..."):
            res = provider.test_connection()

            if res["data"]:
                st.success("✅ Verbindung erfolgreich!")
                # Zeige ein paar Basis-Daten zur Bestätigung
                col1, col2 = st.columns(2)
                col1.metric("Unternehmen", res["data"].get("companyName"))
                col2.metric("Währung", res["data"].get("currency"))
                st.json(res["data"])  # Zeigt das volle Profil zur Inspektion
            else:
                st.error(f"❌ Verbindung fehlgeschlagen: {res['error']}")
                st.info("Schau ins Terminal für den genauen Status-Code.")
