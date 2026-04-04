import streamlit as st

st.title("Hello World")
st.write("Dies ist ein Proof of Concept, erstellt am iPhone.")

if st.button("Klick mich"):
    st.balloons()
    st.success("Es funktioniert!")
