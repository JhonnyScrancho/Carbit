from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import logging
import streamlit as st
from datetime import datetime
import chromedriver_autoinstaller

class BaseScraper(ABC):
    """Base scraper con funzionalità comuni a tutti i portali"""
    
    def __init__(self):
        self.setup_logging()
        self.driver = None
        self.wait_time = 20
        
    def setup_logging(self):
        """Setup del logger"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Log su Streamlit
        def st_log(msg):
            with st.sidebar:
                st.write(f"🔄 {datetime.now().strftime('%H:%M:%S')} - {msg}")
        
        self.st_log = st_log
        
    def setup_driver(self):
        """Setup del webdriver in modalità visibile"""
        try:
            # Installa/aggiorna chromedriver
            chromedriver_autoinstaller.install()
            
            # Configurazione Chrome
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")  # Massimizza finestra
            chrome_options.add_argument("--disable-gpu")  # Riduce problemi grafici
            chrome_options.add_argument("--no-sandbox")  # Necessario per alcuni ambienti
            
            # Rimuovi argomento headless per vedere il browser
            # chrome_options.add_argument('--headless')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_time)
            self.st_log("✅ Driver Chrome inizializzato correttamente")
            
        except Exception as e:
            self.st_log(f"❌ Errore nell'inizializzazione del driver: {str(e)}")
            raise
        
    def cleanup(self):
        """Pulizia risorse"""
        if self.driver:
            try:
                self.driver.quit()
                self.st_log("✅ Browser chiuso correttamente")
            except Exception as e:
                self.st_log(f"❌ Errore nella chiusura del browser: {str(e)}")

    @abstractmethod
    def login(self) -> bool:
        pass

    @abstractmethod
    def get_auctions(self):
        pass

    @abstractmethod
    def get_vehicles(self, auction_id: str):
        pass