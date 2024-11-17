# scrapers/base.py
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
import streamlit as st
import platform
import os

class BaseScraper(ABC):
    def __init__(self):
        self.driver = None
        self.wait_time = 20
        self.wait = None
        self.debug = True

    def setup_driver(self) -> bool:
        """Setup del webdriver ottimizzato per Streamlit Cloud"""
        try:
            st.write("🔧 Setup Chrome Driver:")
            
            # Info sistema
            st.write(f"Sistema Operativo: {platform.system()} {platform.release()}")
            st.write(f"Python Version: {platform.python_version()}")
            
            # Configurazione opzioni Chrome
            chrome_options = Options()
            
            # Opzioni necessarie per Streamlit Cloud
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            # Opzioni aggiuntive per evitare rilevamento
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # User agent realistico
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Configurazioni aggiuntive
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            st.write("Installazione ChromeDriver...")
            # Usa webdriver_manager per gestire l'installazione
            service = Service(ChromeDriverManager().install())
            
            # Inizializza il driver
            st.write("Inizializzazione Chrome...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_time)
            
            # Test base di navigazione
            st.write("Test di navigazione base...")
            self.driver.get("https://www.google.com")
            st.success("✅ Driver inizializzato correttamente")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Errore setup driver: {type(e).__name__}")
            st.error(str(e))
            return False
            
    def cleanup(self):
        """Pulizia risorse del driver"""
        if self.driver:
            try:
                self.driver.quit()
                st.write("✅ Driver chiuso correttamente")
            except Exception as e:
                st.error(f"❌ Errore chiusura driver: {str(e)}")

    def is_element_present(self, by: By, value: str) -> bool:
        """Verifica presenza elemento"""
        try:
            self.driver.find_element(by, value)
            return True
        except:
            return False

    def wait_for_element(self, by: By, value: str, timeout: int = None) -> bool:
        """Attende presenza elemento"""
        try:
            wait = WebDriverWait(self.driver, timeout or self.wait_time)
            wait.until(EC.presence_of_element_located((by, value)))
            return True
        except:
            return False

    @abstractmethod
    def login(self, username: str, password: str) -> bool:
        pass

    @abstractmethod
    def get_auctions(self) -> list:
        pass

    @abstractmethod
    def get_vehicles(self, auction_id: str) -> list:
        pass