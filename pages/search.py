# pages/search.py
import streamlit as st
from scrapers.portals.clickar import ClickarScraper
from scrapers.portals.ayvens import AyvensScraper
import pandas as pd
from datetime import datetime
import sys
import traceback

def debug_scraper(portal_name, username, password, log_container):
    """Funzione di debug per testare singoli step dello scraping"""
    try:
        with log_container:
            st.write(f"🔍 DEBUG {portal_name}")
            st.write("1️⃣ Inizializzazione scraper...")
            scraper = ClickarScraper() if portal_name == "Clickar" else AyvensScraper()
            st.success("✅ Scraper inizializzato")
            
            st.write("2️⃣ Setup driver...")
            scraper.setup_driver()
            st.success("✅ Driver inizializzato")
            
            st.write("3️⃣ Tentativo login...")
            login_success = scraper.login(username, password)
            if not login_success:
                st.error("❌ Login fallito")
                return None
            st.success("✅ Login riuscito")
            
            st.write("4️⃣ Recupero veicoli...")
            vehicles = []
            if portal_name == "Clickar":
                if not scraper.navigate_to_introvabili():
                    st.error("❌ Navigazione a introvabili fallita")
                    return None
                st.success("✅ Navigazione a introvabili riuscita")
                vehicles = scraper.get_all_vehicles()
            else:
                auctions = scraper.get_auctions()
                if auctions:
                    st.success(f"✅ Trovate {len(auctions)} aste")
                    for auction in auctions:
                        auction_vehicles = scraper.get_vehicles(auction['id'])
                        if auction_vehicles:
                            vehicles.extend(auction_vehicles)
                else:
                    st.error("❌ Nessuna asta trovata")
                    return None
            
            return vehicles

    except Exception as e:
        with log_container:
            st.error("❌ ERRORE CRITICO")
            st.error(f"Tipo errore: {type(e).__name__}")
            st.error(f"Messaggio: {str(e)}")
            st.error("Traceback completo:")
            st.code(traceback.format_exc())
        return None
    finally:
        try:
            scraper.cleanup()
            with log_container:
                st.write("🧹 Cleanup eseguito")
        except:
            with log_container:
                st.warning("⚠️ Errore durante il cleanup")

def main():
    st.title("🚗 Ricerca Aste Auto")
    
    # Setup delle colonne principali
    main_col, debug_col = st.columns([3, 1])
    
    # Colonna di debug/log
    with debug_col:
        st.header("📋 Debug Log")
        log_container = st.empty()
        if 'debug_messages' not in st.session_state:
            st.session_state.debug_messages = []
    
    # Colonna principale
    with main_col:
        # Area Controlli
        st.header("🎮 Controlli")
        control_col1, control_col2 = st.columns(2)
        
        with control_col1:
            clickar_enabled = st.checkbox("Clickar", value=True)
            debug_mode = st.checkbox("Modalità Debug", value=True, 
                                   help="Mostra informazioni dettagliate durante l'esecuzione")
        
        with control_col2:
            ayvens_enabled = st.checkbox("Ayvens", value=True)
            headless = st.checkbox("Headless Mode", value=False,
                                 help="Esegui senza mostrare il browser")
        
        # Bottone di avvio
        if st.button("🚀 Avvia Ricerca", type="primary", use_container_width=True):
            if not st.session_state.get('firebase_mgr'):
                st.error("Firebase non inizializzato")
                return
            
            all_vehicles = []
            
            # Test di connessione e debug
            if debug_mode:
                st.info("🔧 Modalità debug attiva")
                if clickar_enabled:
                    vehicles = debug_scraper("Clickar", 
                                          st.secrets.credentials.clickar.username,
                                          st.secrets.credentials.clickar.password,
                                          log_container)
                    if vehicles:
                        for v in vehicles:
                            v['fonte'] = 'Clickar'
                        all_vehicles.extend(vehicles)
                
                if ayvens_enabled:
                    vehicles = debug_scraper("Ayvens",
                                          st.secrets.credentials.ayvens.username,
                                          st.secrets.credentials.ayvens.password,
                                          log_container)
                    if vehicles:
                        for v in vehicles:
                            v['fonte'] = 'Ayvens'
                        all_vehicles.extend(vehicles)
            
            # Se abbiamo trovato veicoli, mostriamoli
            if all_vehicles:
                st.session_state['vehicles_data'] = pd.DataFrame(all_vehicles)
                st.success(f"✅ Trovati {len(all_vehicles)} veicoli")
            else:
                st.error("❌ Nessun veicolo trovato")
        
        # Area Risultati
        if 'vehicles_data' in st.session_state:
            st.header("📊 Risultati")
            df = st.session_state['vehicles_data']
            
            # Filtri
            with st.expander("🔍 Filtri", expanded=True):
                filter_col1, filter_col2, filter_col3 = st.columns(3)
                
                with filter_col1:
                    brands = sorted(df['brand_model'].str.split().str[0].unique()) if 'brand_model' in df.columns else []
                    brand_filter = st.multiselect("Marca", options=brands)
                
                with filter_col2:
                    locations = sorted(df['location'].unique()) if 'location' in df.columns else []
                    location_filter = st.multiselect("Ubicazione", options=locations)
                
                with filter_col3:
                    statuses = sorted(df['status'].unique()) if 'status' in df.columns else []
                    status_filter = st.multiselect("Stato", options=statuses)
            
            # Applica filtri
            filtered_df = df.copy()
            if brand_filter:
                filtered_df = filtered_df[filtered_df['brand_model'].str.split().str[0].isin(brand_filter)]
            if location_filter:
                filtered_df = filtered_df[filtered_df['location'].isin(location_filter)]
            if status_filter:
                filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
            
            # Mostra risultati
            st.dataframe(
                filtered_df,
                column_config={
                    "image_url": st.column_config.ImageColumn("Immagine"),
                    "brand_model": "Marca e Modello",
                    "plate": "Targa",
                    "vin": "Telaio",
                    "year": "Anno",
                    "location": "Ubicazione",
                    "base_price": st.column_config.NumberColumn("Prezzo Base", format="€%.2f"),
                    "km": "Kilometraggio",
                    "damages": "Danni",
                    "status": "Stato",
                    "fonte": "Fonte"
                },
                hide_index=True
            )
            
            # Download
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

if __name__ == "__main__":
    main()