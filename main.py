# main.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Configurazione della pagina principale
st.set_page_config(
    page_title="Auto Arbitrage",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inizializzazione Firebase con Streamlit secrets
if 'firebase_initialized' not in st.session_state:
    try:
        # Usa direttamente i secrets di Streamlit
        cred = credentials.Certificate(st.secrets["firebase"])
        firebase_admin.initialize_app(cred)
        st.session_state.db = firebase_admin.firestore.client()
        st.session_state.firebase_initialized = True
        st.success("✅ Firebase inizializzato correttamente!")
    except Exception as e:
        st.error(f"❌ Errore nell'inizializzazione di Firebase: {str(e)}")

def main():
    st.title("🚗 Auto Arbitrage")
    st.write("Sistema di monitoraggio e analisi delle aste auto")
    
    # Menu principale nella sidebar
    st.sidebar.title("Menu")
    menu = st.sidebar.radio(
        "Seleziona sezione:",
        ["Dashboard", "Ricerca", "Analisi", "Watchlist"]
    )
    
    # Contenuto in base alla selezione
    if menu == "Dashboard":
        show_dashboard()
    elif menu == "Ricerca":
        show_search()
    elif menu == "Analisi":
        show_analysis()
    elif menu == "Watchlist":
        show_watchlist()

def show_dashboard():
    st.header("Dashboard")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Aste Attive", value="12")
    with col2:
        st.metric(label="Veicoli Monitorati", value="156")
    with col3:
        st.metric(label="Opportunità", value="8")

def show_search():
    try:
        from pages.search import main as search_main
        search_main()
    except Exception as e:
        st.error(f"Errore nel caricamento della pagina di ricerca: {str(e)}")

def show_analysis():
    st.header("Analisi Veicoli")
    st.info("Sezione in sviluppo")

def show_watchlist():
    st.header("Watchlist")
    st.info("Sezione in sviluppo")

if __name__ == "__main__":
    main()