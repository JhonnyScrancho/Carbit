import streamlit as st
import pandas as pd
from datetime import datetime
from utils.firebase_config import FirebaseConfig
from utils.firebase_manager import FirebaseManager
import time
import traceback

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

def show_debug_info():
    """Mostra informazioni di debug nella sidebar"""
    with st.sidebar:
        st.divider()
        st.subheader("ℹ️ Debug Info")
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Firebase:")
            st.caption("✅ OK" if st.session_state.get('firebase_initialized') else "❌ ERROR")
        with col2:
            st.caption("Ultimo update:")
            st.caption(datetime.now().strftime("%H:%M:%S"))

def show_dashboard():
    st.header("📊 Dashboard")
    
    # Metriche principali in cards con sfondo
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='padding: 1rem; background: #f0f2f6; border-radius: 10px; text-align: center;'>
            <h3 style='margin:0'>🚗 Aste Attive</h3>
            <h2 style='margin:0; color: #0066cc;'>12</h2>
            <p style='margin:0; color: green;'>↑ +2</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='padding: 1rem; background: #f0f2f6; border-radius: 10px; text-align: center;'>
            <h3 style='margin:0'>🔍 Veicoli Monitorati</h3>
            <h2 style='margin:0; color: #0066cc;'>156</h2>
            <p style='margin:0; color: green;'>↑ +15</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='padding: 1rem; background: #f0f2f6; border-radius: 10px; text-align: center;'>
            <h3 style='margin:0'>💰 Opportunità</h3>
            <h2 style='margin:0; color: #0066cc;'>8</h2>
            <p style='margin:0; color: red;'>↓ -2</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div style='padding: 1rem; background: #f0f2f6; border-radius: 10px; text-align: center;'>
            <h3 style='margin:0'>📈 Margine Medio</h3>
            <h2 style='margin:0; color: #0066cc;'>18.5%</h2>
            <p style='margin:0; color: green;'>↑ +2.1%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Grafici e tabelle
    st.divider()
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
                }),
                hide_index=True
            )
        else:
            st.warning("⚠️ Firebase non inizializzato")

def show_search():
    st.header("🔍 Ricerca Aste", divider="blue")
    
    # Area Controlli in un box
    with st.container():
        st.markdown("""
        <div style='padding: 1rem; background: #f0f2f6; border-radius: 10px;'>
            <h3 style='margin:0'>🎮 Controlli Ricerca</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            clickar = st.checkbox("🔄 Clickar", value=True, 
                                help="Abilita ricerca su Clickar")
            debug_mode = st.checkbox("🐛 Debug Mode", value=True,
                                   help="Mostra log dettagliati")
            
        with col2:
            ayvens = st.checkbox("🔄 Ayvens", value=True,
                               help="Abilita ricerca su Ayvens")
            headless = st.checkbox("🤖 Headless", value=False,
                                 help="Esegui senza interfaccia browser")
            
        with col3:
            with st.expander("⚙️ Opzioni Avanzate"):
                retry_count = st.number_input("Max tentativi", 1, 5, 3)
                wait_time = st.number_input("Timeout (sec)", 10, 60, 20)

        # Progress bar placeholder
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Log area
        log_container = st.container()
        with log_container:
            st.markdown("""
            <div style='padding: 1rem; background: #f0f2f6; border-radius: 10px;'>
                <h3 style='margin:0'>📋 Log Operazioni</h3>
            </div>
            """, unsafe_allow_html=True)
            log_area = st.empty()

        # Bottone avvio ricerca
        if st.button("🚀 Avvia Ricerca", type="primary", use_container_width=True):
            try:
                # Check Firebase
                if not st.session_state.get('firebase_mgr'):
                    st.error("❌ Firebase non inizializzato")
                    return
                
                all_vehicles = []
                sources = []
                
                if clickar:
                    sources.append(("Clickar", st.secrets.credentials.clickar))
                if ayvens:
                    sources.append(("Ayvens", st.secrets.credentials.ayvens))
                
                total_steps = len(sources) * 4  # Login, Navigate, Scrape, Save
                current_step = 0
                
                for source_name, credentials in sources:
                    try:
                        status_text.text(f"Elaborazione {source_name}...")
                        
                        # Importa scraper dinamicamente
                        if source_name == "Clickar":
                            from scrapers.portals.clickar import ClickarScraper
                            scraper = ClickarScraper()
                        else:
                            from scrapers.portals.ayvens import AyvensScraper
                            scraper = AyvensScraper()
                        
                        # Setup e debug mode
                        if debug_mode:
                            log_area.text(f"🔧 Inizializzazione {source_name}...")
                        
                        # Esegui scraping
                        vehicles = scraper.scrape(
                            credentials.username,
                            credentials.password
                        )
                        
                        if vehicles:
                            # Aggiunge fonte
                            for v in vehicles:
                                v['fonte'] = source_name
                            all_vehicles.extend(vehicles)
                            
                            if debug_mode:
                                log_area.text(f"✅ {source_name}: {len(vehicles)} veicoli trovati")
                        else:
                            if debug_mode:
                                log_area.text(f"⚠️ {source_name}: Nessun veicolo trovato")
                        
                        current_step += 1
                        progress_bar.progress(current_step / total_steps)
                        
                    except Exception as e:
                        st.error(f"❌ Errore in {source_name}: {str(e)}")
                        if debug_mode:
                            st.code(traceback.format_exc())
                        continue
                        
                # Mostra risultati
                if all_vehicles:
                    st.session_state['vehicles_data'] = pd.DataFrame(all_vehicles)
                    status_text.text(f"✅ Trovati {len(all_vehicles)} veicoli totali")
                else:
                    status_text.text("⚠️ Nessun veicolo trovato")
                    
            except Exception as e:
                st.error(f"❌ Errore generale: {str(e)}")
                if debug_mode:
                    st.code(traceback.format_exc())
            finally:
                progress_bar.progress(100)
        
        # Mostra risultati se presenti
        if 'vehicles_data' in st.session_state:
            show_search_results(st.session_state['vehicles_data'])

def show_search_results(df):
    """Mostra i risultati della ricerca"""
    st.divider()
    st.subheader("📊 Risultati Ricerca", divider="blue")
    
    # Filtri in expander
    with st.expander("🔍 Filtri", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            brands = sorted(df['brand_model'].str.split().str[0].unique()) if 'brand_model' in df.columns else []
            brand_filter = st.multiselect("🚗 Marca", options=brands)
        
        with col2:
            locations = sorted(df['location'].unique()) if 'location' in df.columns else []
            location_filter = st.multiselect("📍 Ubicazione", options=locations)
        
        with col3:
            sources = sorted(df['fonte'].unique()) if 'fonte' in df.columns else []
            source_filter = st.multiselect("🔄 Fonte", options=sources)
    
    # Applica filtri
    filtered_df = df.copy()
    if brand_filter:
        filtered_df = filtered_df[filtered_df['brand_model'].str.split().str[0].isin(brand_filter)]
    if location_filter:
        filtered_df = filtered_df[filtered_df['location'].isin(location_filter)]
    if source_filter:
        filtered_df = filtered_df[filtered_df['fonte'].isin(source_filter)]
    
    # Mostra risultati
    st.dataframe(
        filtered_df,
        column_config={
            "image_url": st.column_config.ImageColumn("🖼️ Immagine"),
            "brand_model": "🚗 Marca e Modello",
            "plate": "🔢 Targa",
            "vin": "🔑 Telaio",
            "year": "📅 Anno",
            "location": "📍 Ubicazione",
            "base_price": st.column_config.NumberColumn("💰 Prezzo Base", format="€%.2f"),
            "km": "🛣️ Kilometraggio",
            "damages": "🔧 Danni",
            "status": "📊 Stato",
            "fonte": "🔄 Fonte"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Download CSV
    if st.button("📥 Scarica CSV", use_container_width=True):
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        filename = f'auto_export_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        st.download_button(
            "Conferma Download",
            csv,
            filename,
            "text/csv",
            key='download-csv'
        )

def show_analysis():
    st.header("📊 Analisi", divider="blue")
    
    # Tabs per diverse analisi
    tab1, tab2, tab3 = st.tabs(["📈 Trend Prezzi", "💰 Analisi Margini", "📊 Statistiche"])
    
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
    st.header("👀 Watchlist", divider="blue")
    
    if st.session_state.get('firebase_initialized'):
        # Cards per statistiche watchlist
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='padding: 1rem; background: #f0f2f6; border-radius: 10px; text-align: center;'>
                <h3 style='margin:0'>🚗 Veicoli Monitorati</h3>
                <h2 style='margin:0; color: #0066cc;'>24</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div style='padding: 1rem; background: #f0f2f6; border-radius: 10px; text-align: center;'>
                <h3 style='margin:0'>🔔 Alert Attivi</h3>
                <h2 style='margin:0; color: #0066cc;'>12</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown("""
            <div style='padding: 1rem; background: #f0f2f6; border-radius: 10px; text-align: center;'>
                <h3 style='margin:0'>📊 Variazione Media</h3>
                <h2 style='margin:0; color: #0066cc;'>-2.3%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Tabelle watchlist
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚗 Veicoli Monitorati")
            # Esempio di dati watchlist
            watchlist_df = pd.DataFrame({
                'Veicolo': ['Audi A3', 'BMW X1', 'Mercedes C220'],
                'Prezzo Iniziale': ['€15.000', '€22.000', '€25.000'],
                'Prezzo Attuale': ['€14.500', '€21.000', '€24.000'],
                'Variazione': ['-3.3%', '-4.5%', '-4.0%']
            })
            st.dataframe(watchlist_df, hide_index=True, use_container_width=True)
            
        with col2:
            st.subheader("🔔 Alert Configurati")
            # Esempio di dati alert
            alert_df = pd.DataFrame({
                'Veicolo': ['Audi A3', 'BMW X1'],
                'Tipo Alert': ['Prezzo < €14.000', 'Variazione > 5%'],
                'Stato': ['Attivo', 'Attivo']
            })
            st.dataframe(alert_df, hide_index=True, use_container_width=True)
            
    else:
        st.warning("⚠️ Watchlist non disponibile - Firebase non inizializzato")

def main():
    # Header principale con stile
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(90deg, #f0f2f6, #e0e2e6); border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: #0066cc;'>🚗 Auto Arbitrage</h1>
        <p style='font-size: 1.2rem;'>Sistema di monitoraggio e analisi delle aste auto</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Warning Firebase se non inizializzato
    if not st.session_state.get('firebase_initialized'):
        st.warning("⚠️ Firebase non inizializzato. Alcune funzionalità potrebbero essere limitate.", icon="⚠️")
    
    # Menu principale nella sidebar con stile
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: #f0f2f6; border-radius: 10px; margin-bottom: 1rem;'>
            <h2 style='margin:0; color: #0066cc;'>Menu</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Sezione utente
        if st.session_state.get('firebase_initialized'):
            st.markdown("""
            <div style='text-align: center; padding: 0.5rem; background: #e0e2e6; border-radius: 10px; margin-bottom: 1rem;'>
                <p style='margin:0;'>👤 Utente connesso</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Menu principale
        menu = st.radio(
            "Seleziona sezione:",
            ["Dashboard", "Ricerca", "Analisi", "Watchlist"],
            key="menu_selection"
        )
        
        show_debug_info()
    
    # Contenuto principale in base alla selezione
    if menu == "Dashboard":
        show_dashboard()
    elif menu == "Ricerca":
        show_search()
    elif menu == "Analisi":
        show_analysis()
    elif menu == "Watchlist":
        show_watchlist()

def init_session_state():
    """Inizializza variabili di sessione"""
    if 'debug_messages' not in st.session_state:
        st.session_state.debug_messages = []
    if 'current_operation' not in st.session_state:
        st.session_state.current_operation = None
    if 'operation_progress' not in st.session_state:
        st.session_state.operation_progress = 0
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None

if __name__ == "__main__":
    try:
        init_session_state()
        main()
    except Exception as e:
        st.error(f"❌ Errore applicazione: {str(e)}")
        if st.checkbox("Mostra dettagli errore"):
            st.code(traceback.format_exc())