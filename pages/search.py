import streamlit as st
from scrapers.portals.clickar import ClickarScraper
from scrapers.portals.ayvens import AyvensScraper
import pandas as pd
from datetime import datetime

def main():
    st.title("🚗 Ricerca Aste Auto")
    
    # Verifica inizializzazione Firebase
    if not st.session_state.get('firebase_initialized', False):
        st.error("⚠️ Firebase non inizializzato")
        return
    
    firebase_mgr = st.session_state.get('firebase_mgr')
    if not firebase_mgr:
        st.error("⚠️ Firebase Manager non disponibile")
        return
    
    # Sidebar per i controlli
    with st.sidebar:
        st.header("Portali")
        clickar_enabled = st.checkbox("Clickar", value=True)
        ayvens_enabled = st.checkbox("Ayvens", value=True)
        
        if st.button("Avvia Ricerca", type="primary"):
            with st.spinner("Recupero aste in corso..."):
                all_vehicles = []
                
                # Scraping Clickar
                if clickar_enabled:
                    with st.spinner("Scraping Clickar..."):
                        try:
                            scraper = ClickarScraper()
                            credentials = st.secrets.credentials.clickar
                            vehicles = scraper.scrape(
                                credentials.username,
                                credentials.password
                            )
                            if vehicles:
                                for v in vehicles:
                                    v['fonte'] = 'Clickar'
                                all_vehicles.extend(vehicles)
                                
                                results = firebase_mgr.save_auction_batch(vehicles)
                                st.sidebar.info(f"Salvati {results['success']} veicoli su Firebase")
                                st.sidebar.success(f"✅ Clickar: {len(vehicles)} veicoli trovati")
                            else:
                                st.sidebar.error("❌ Clickar: Errore nel recupero dei dati")
                        except Exception as e:
                            st.sidebar.error(f"❌ Clickar: {str(e)}")
                
                # Scraping Ayvens
                if ayvens_enabled:
                    with st.spinner("Scraping Ayvens..."):
                        try:
                            scraper = AyvensScraper()
                            credentials = st.secrets.credentials.ayvens
                            vehicles = scraper.scrape(
                                credentials.username,
                                credentials.password
                            )
                            if vehicles:
                                for v in vehicles:
                                    v['fonte'] = 'Ayvens'
                                all_vehicles.extend(vehicles)
                                
                                results = firebase_mgr.save_auction_batch(vehicles)
                                st.sidebar.info(f"Salvati {results['success']} veicoli su Firebase")
                                st.sidebar.success(f"✅ Ayvens: {len(vehicles)} veicoli trovati")
                            else:
                                st.sidebar.error("❌ Ayvens: Errore nel recupero dei dati")
                        except Exception as e:
                            st.sidebar.error(f"❌ Ayvens: {str(e)}")
                
                # Converti in DataFrame
                if all_vehicles:
                    df = pd.DataFrame(all_vehicles)
                    st.session_state['vehicles_data'] = df
                    st.sidebar.success(f"Totale veicoli trovati: {len(df)}")
                else:
                    st.sidebar.error("Nessun veicolo trovato")
    
    # Area principale - Visualizzazione risultati
    if 'vehicles_data' in st.session_state:
        df = st.session_state['vehicles_data']
        
        # Filtri
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
        if st.download_button(
            label="📥 Scarica risultati",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name=f'auto_arbitrage_export_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
            mime='text/csv'
        ):
            st.success("Download completato!")
    
    else:
        st.info("👈 Utilizza i controlli nella sidebar per avviare una ricerca")

if __name__ == "__main__":
    main()