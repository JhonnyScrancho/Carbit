import streamlit as st
from scrapers.portals.clickar import ClickarScraper
from scrapers.portals.ayvens import AyvensScraper
import pandas as pd
from datetime import datetime

def main():
    st.title("🚗 Ricerca Aste Auto")
    
    # Crea due colonne principali
    main_col, log_col = st.columns([3, 1])
    
    with log_col:
        st.header("📋 Log")
        log_container = st.empty()
        # Inizializza log se non esiste
        if 'log_messages' not in st.session_state:
            st.session_state.log_messages = []
            
        # Funzione per aggiungere log
        def add_log(message, type="info"):
            timestamp = datetime.now().strftime("%H:%M:%S")
            icon = "ℹ️" if type == "info" else "✅" if type == "success" else "❌" if type == "error" else "⚠️"
            st.session_state.log_messages.append(f"{icon} {timestamp} - {message}")
            # Aggiorna visualizzazione log
            with log_container:
                for msg in st.session_state.log_messages:
                    st.text(msg)
    
    with main_col:
        # Controlli
        st.header("🔍 Controlli Ricerca")
        col1, col2 = st.columns(2)
        
        with col1:
            clickar_enabled = st.checkbox("👥 Clickar", value=True)
            headless = st.checkbox("🔒 Modalità Headless", value=False, 
                                help="Se disattivato, vedrai il browser durante lo scraping")
            
        with col2:
            ayvens_enabled = st.checkbox("🚗 Ayvens", value=True)
            debug_mode = st.checkbox("🐛 Debug Mode", value=True,
                                  help="Mostra informazioni aggiuntive durante lo scraping")
        
        # Bottone di ricerca
        if st.button("🚀 Avvia Ricerca", type="primary", use_container_width=True):
            if not st.session_state.get('firebase_mgr'):
                st.error("🔥 Firebase non inizializzato correttamente")
                add_log("Firebase non inizializzato", "error")
                return
            
            add_log("Avvio della ricerca...")
            if not headless:
                st.warning("⚠️ Si aprirà una finestra del browser. Non chiuderla durante lo scraping!")
            
            with st.spinner("⏳ Recupero aste in corso..."):
                all_vehicles = []
                
                # Clickar scraping
                if clickar_enabled:
                    try:
                        add_log("Avvio scraping Clickar...")
                        scraper = ClickarScraper()
                        if debug_mode:
                            st.info("🔄 Connessione a Clickar...")
                        
                        credentials = st.secrets.credentials.clickar
                        vehicles = scraper.scrape(
                            credentials.username,
                            credentials.password
                        )
                        
                        if vehicles:
                            for v in vehicles:
                                v['fonte'] = 'Clickar'
                            all_vehicles.extend(vehicles)
                            add_log(f"Clickar: trovati {len(vehicles)} veicoli", "success")
                            if debug_mode:
                                st.success(f"✅ Clickar: {len(vehicles)} veicoli trovati")
                        else:
                            add_log("Clickar: nessun veicolo trovato", "error")
                            if debug_mode:
                                st.error("❌ Clickar: Nessun veicolo trovato")
                    except Exception as e:
                        error_msg = str(e)
                        add_log(f"Errore Clickar: {error_msg}", "error")
                        if debug_mode:
                            st.error(f"❌ Clickar: {error_msg}")
                
                # Ayvens scraping
                if ayvens_enabled:
                    try:
                        add_log("Avvio scraping Ayvens...")
                        scraper = AyvensScraper()
                        if debug_mode:
                            st.info("🔄 Connessione a Ayvens...")
                            
                        credentials = st.secrets.credentials.ayvens
                        vehicles = scraper.scrape(
                            credentials.username,
                            credentials.password
                        )
                        
                        if vehicles:
                            for v in vehicles:
                                v['fonte'] = 'Ayvens'
                            all_vehicles.extend(vehicles)
                            
                            # Salva su Firebase
                            results = st.session_state.firebase_mgr.save_auction_batch(vehicles)
                            add_log(f"Ayvens: salvati {results['success']} veicoli su Firebase", "success")
                            if debug_mode:
                                st.success(f"✅ Ayvens: {len(vehicles)} veicoli trovati")
                        else:
                            add_log("Ayvens: nessun veicolo trovato", "error")
                            if debug_mode:
                                st.error("❌ Ayvens: Nessun veicolo trovato")
                    except Exception as e:
                        error_msg = str(e)
                        add_log(f"Errore Ayvens: {error_msg}", "error")
                        if debug_mode:
                            st.error(f"❌ Ayvens: {error_msg}")
                
                # Gestione risultati
                if all_vehicles:
                    df = pd.DataFrame(all_vehicles)
                    st.session_state['vehicles_data'] = df
                    add_log(f"Totale veicoli trovati: {len(df)}", "success")
                    if debug_mode:
                        st.success(f"✅ Totale veicoli trovati: {len(df)}")
                else:
                    add_log("Nessun veicolo trovato", "error")
                    if debug_mode:
                        st.error("❌ Nessun veicolo trovato")
        
        # Visualizzazione risultati
        if 'vehicles_data' in st.session_state:
            st.header("📊 Risultati")
            df = st.session_state['vehicles_data']
            
            # Filtri
            with st.expander("🔍 Filtri", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    brand_filter = st.multiselect(
                        "Marca",
                        options=sorted(df['brand_model'].str.split().str[0].unique())
                    )
                with col2:
                    location_filter = st.multiselect(
                        "Ubicazione",
                        options=sorted(df['location'].unique()) if 'location' in df.columns else []
                    )
                with col3:
                    status_filter = st.multiselect(
                        "Stato",
                        options=sorted(df['status'].unique()) if 'status' in df.columns else []
                    )
            
            # Applica filtri
            filtered_df = df.copy()
            if brand_filter:
                filtered_df = filtered_df[filtered_df['brand_model'].str.split().str[0].isin(brand_filter)]
            if location_filter and 'location' in df.columns:
                filtered_df = filtered_df[filtered_df['location'].isin(location_filter)]
            if status_filter and 'status' in df.columns:
                filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
            
            # Visualizzazione risultati
            st.dataframe(
                filtered_df,
                column_config={
                    "image_url": st.column_config.ImageColumn("Immagine"),
                    "brand_model": "Marca e Modello",
                    "plate": "Targa",
                    "vin": "Telaio",
                    "year": "Anno",
                    "location": "Ubicazione",
                    "base_price": st.column_config.NumberColumn(
                        "Prezzo Base",
                        format="€%.2f"
                    ),
                    "km": "Kilometraggio",
                    "damages": "Danni",
                    "status": "Stato",
                    "fonte": "Fonte"
                },
                hide_index=True
            )
            
            # Download CSV
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.download_button(
                    label="📥 Scarica CSV",
                    data=filtered_df.to_csv(index=False).encode('utf-8'),
                    file_name=f'auto_arbitrage_export_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                    mime='text/csv',
                    use_container_width=True
                ):
                    st.success("✅ Download completato!")
                    add_log("CSV scaricato", "success")
        else:
            st.info("👆 Utilizza i controlli sopra per avviare una ricerca")

if __name__ == "__main__":
    main()