# scrapers/base.py
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import logging
import streamlit as st
from datetime import datetime

class BaseScraper(ABC):
    """Base scraper con funzionalità comuni a tutti i portali"""
    
    def __init__(self, headless: bool = False):  # Default a False per debug
        self.setup_logging()
        self.driver = None
        self.headless = headless
        self.wait_time = 20  # Aumentato timeout
        
    def setup_logging(self):
        """Setup del logger"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Log sia su file che su Streamlit
        def streamlit_log_handler(message):
            timestamp = datetime.now().strftime("%H:%M:%S")
            with st.sidebar:
                st.text(f"{timestamp} - {message}")
        
        self.st_log = streamlit_log_handler
        
    def log(self, message, level="info"):
        """Unified logging to both file and Streamlit"""
        if level == "info":
            self.logger.info(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)
            
        # Log to Streamlit
        self.st_log(message)
        
    def setup_driver(self):
        """Setup base del webdriver"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
                
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_time)
            self.log("Driver inizializzato correttamente")
            
        except Exception as e:
            self.log(f"Errore nell'inizializzazione del driver: {str(e)}", "error")
            raise
        
    def cleanup(self):
        """Pulizia risorse"""
        if self.driver:
            self.driver.quit()
            self.log("Driver chiuso correttamente")

    @abstractmethod
    def login(self) -> bool:
        """Metodo astratto per login"""
        pass

    @abstractmethod
    def get_auctions(self):
        """Metodo astratto per recupero aste"""
        pass

    @abstractmethod
    def get_vehicles(self, auction_id: str):
        """Metodo astratto per recupero veicoli"""
        pass