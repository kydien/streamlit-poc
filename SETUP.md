# 🚀 Streamlit PoC: Mobile-First Setup (Desktop & iPhone)

Dieses Repository dient als Proof of Concept (PoC) für ein Streamlit-Dashboard, das vollständig über das Smartphone (iPhone) oder den Desktop entwickelt und gewartet werden kann.

---

## 🏗 Infrastruktur & Tools

* **Hosting:** [Streamlit Cloud](https://share.streamlit.io) (Auto-Deployment bei jedem Push).
* **Source Control:** [GitHub](https://github.com).
* **IDE (Desktop/iPhone):** [github.dev](https://github.dev) (Web-basiertes VS Code).
* **Mobile Access:** Safari -> `github.dev` -> "Zum Home-Bildschirm hinzufügen".

---

## 📂 Projekt-Struktur

Für ein skalierbares Dashboard wird folgende Struktur empfohlen:

```text
streamlit-poc/
├── .vscode/
│   └── settings.json      # Editor-Optimierung (iPhone/Desktop)
├── data/
│   └── mock_data.csv      # Testdaten (optional)
├── modules/
│   └── charts.py          # Ausgelagerte Visualisierungs-Logik
├── app.py                 # Hauptanwendung (Entrypoint)
├── requirements.txt       # Abhängigkeiten (Bibliotheken)
└── SETUP.md               # Diese Anleitung

Essenzielle Extensions
Installiere diese im VS Code (Web/Desktop), um professionell zu arbeiten:

Python (Microsoft): Die Kern-Logik für Pylance und Type-Checking.

Ruff: (Wichtig!) Ersetzt Black/Flake8. Formatiert und säubert den Code blitzschnell.

Error Lens: Zeigt Fehler direkt in der Zeile an (unverzichtbar am iPhone).

Indent Rainbow: Visualisiert Einrückungen farblich (verhindert Python-Indentation-Errors).

Streamlit Snippets: Shortcuts für UI-Komponenten (z.B. stcol, stsidebar).