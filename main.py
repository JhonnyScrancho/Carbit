# main.py
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.firebase_config import FirebaseConfig
from utils.firebase_manager import FirebaseManager

# Configurazione della pagina principale
st.set_page_config(
    page_title="Auto Arbitrage",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Auto Arbitrage - Sistema di monitoraggio aste auto",
        'Get Help': 'https://github.com/tuouser/auto-arbitrage',
        'Report a bug': "https://github.com/tuouser/auto-arbitrage/issues"
    }
)

# Inizializzazione Firebase e stato globale
if 'firebase_initialized' not in st.session_state:
    st.session_state.firebase_initialized = FirebaseConfig.initialize_firebase()

if st.session_state.get('firebase_initialized') and 'firebase_mgr' not in st.session_state:
    st.session_state.firebase_mgr = FirebaseManager()

def show_dashboard():
    st.header("📊 Dashboard")
    
    # Metriche principali
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Aste Attive",
            value="12",
            delta="2",
            delta_color="normal",
            help="Numero di aste attualmente attive"
        )
    with col2:
        st.metric(
            label="Veicoli Monitorati",
            value="156",
            delta="15",
            delta_color="normal",
            help="Totale veicoli sotto monitoraggio"
        )
    with col3:
        st.metric(
            label="Opportunità",
            value="8",
            delta="-2",
            delta_color="inverse",
            help="Opportunità con margine >20%"
        )
    with col4:
        st.metric(
            label="Margine Medio",
            value="18.5%",
            delta="2.1%",
            delta_color="normal",
            help="Margine medio delle opportunità"
        )
    
    # Grafici e tabelle
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Trend Opportunità")
        st.info("Grafico in sviluppo")
        
    with col2:
        st.subheader("🎯 Top Opportunità")
        if st.session_state.get('firebase_initialized'):
            st.dataframe(
                pd.DataFrame({
                    'Veicolo': ['Audi A3', 'BMW X1', 'Mercedes C220'],
                    'Prezzo': ['€15.000', '€22.000', '€25.000'],
                    'Margine': ['25%', '22%', '20%']
                })
            )
        else:
            st.info("Dati non disponibili - Firebase non inizializzato")

def show_search():
    st.header("🔍 Ricerca")
    try:
        from pages.search import main as search_main
        search_main()
    except Exception as e:
        st.error(f"Errore nel caricamento della pagina di ricerca: {str(e)}")

def show_analysis():
    st.header("📊 Analisi Veicoli")
    
    # Tabs per diverse analisi
    tab1, tab2, tab3 = st.tabs(["Trend Prezzi", "Analisi Margini", "Statistiche"])
    
    with tab1:
        st.subheader("📈 Trend Prezzi")
        st.info("Sezione in sviluppo")
        
    with tab2:
        st.subheader("💰 Analisi Margini")
        st.info("Sezione in sviluppo")
        
    with tab3:
        st.subheader("📊 Statistiche")
        st.info("Sezione in sviluppo")

def show_watchlist():
    st.header("👀 Watchlist")
    
    if st.session_state.get('firebase_initialized'):
        st.info("Watchlist in sviluppo")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🚗 Veicoli Monitorati")
        with col2:
            st.subheader("🔔 Alert Attivi")
    else:
        st.warning("Watchlist non disponibile - Firebase non inizializzato")

def main():
    # Header principale
    st.title("🚗 Auto Arbitrage")
    st.write("Sistema di monitoraggio e analisi delle aste auto")
    
    if not st.session_state.get('firebase_initialized'):
        st.warning("⚠️ Firebase non inizializzato. Alcune funzionalità potrebbero non essere disponibili.")
    
    # Menu principale nella sidebar
    with st.sidebar:
        st.title("Menu")
        
        # Sezione utente
        if st.session_state.get('firebase_initialized'):
            st.write("👤 Utente connesso")
        
        # Menu principale
        menu = st.radio(
            "Seleziona sezione:",
            ["Dashboard", "Ricerca", "Analisi", "Watchlist"]
        )
        
        # Info aggiuntive
        st.divider()
        st.caption("Ultimo aggiornamento dati:")
        st.caption(datetime.now().strftime("%d/%m/%Y %H:%M"))
    
    # Contenuto principale in base alla selezione
    if menu == "Dashboard":
        show_dashboard()
    elif menu == "Ricerca":
        show_search()
    elif menu == "Analisi":
        show_analysis()
    elif menu == "Watchlist":
        show_watchlist()

if __name__ == "__main__":
    main()