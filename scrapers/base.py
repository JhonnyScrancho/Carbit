# scrapers/base.py
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import chromedriver_autoinstaller
import streamlit as st
import platform
import os

class BaseScraper(ABC):
    def __init__(self):
        self.driver = None
        self.wait_time = 20
        
    def setup_driver(self):
        """Setup dettagliato del webdriver con info di debug"""
        try:
            st.write("🔧 Setup Chrome Driver:")
            
            # Info sistema
            st.write(f"Sistema Operativo: {platform.system()} {platform.release()}")
            st.write(f"Python Version: {platform.python_version()}")
            
            # Installa/aggiorna chromedriver
            st.write("Installing/updating chromedriver...")
            chromedriver_path = chromedriver_autoinstaller.install()
            st.write(f"Chromedriver path: {chromedriver_path}")
            
            # Opzioni Chrome
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Verifica ambiente
            if os.getenv('STREAMLIT_SERVER_PORT'):
                st.write("⚠️ Ambiente Streamlit Cloud rilevato")
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--disable-gpu")
            else:
                st.write("💻 Ambiente locale rilevato")
            
            # Inizializza driver
            st.write("Inizializzazione Chrome...")
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_time)
            
            # Verifica inizializzazione
            if self.driver:
                st.write("✅ Driver inizializzato correttamente")
                return True
            else:
                st.error("❌ Driver non inizializzato")
                return False
                
        except Exception as e:
            st.error(f"❌ Errore setup driver: {type(e).__name__}")
            st.error(str(e))
            raise
        
    def cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
                st.write("✅ Driver chiuso correttamente")
            except Exception as e:
                st.error(f"❌ Errore chiusura driver: {str(e)}")

    @abstractmethod
    def login(self) -> bool:
        pass

    @abstractmethod
    def get_auctions(self):
        pass

    @abstractmethod
    def get_vehicles(self, auction_id: str):
        pass