# scrapers/base.py
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import streamlit as st
import platform
import os
import time

class BaseScraper(ABC):
    def __init__(self):
        """Inizializzazione base dello scraper"""
        self.driver = None
        self.wait_time = 20
        self.wait = None
        self.debug = True
        
    def setup_driver(self) -> bool:
        """
        Setup dettagliato del webdriver con gestione errori
        Returns:
            bool: True se setup completato con successo, False altrimenti
        """
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
                
            # Opzioni aggiuntive per stabilità
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-extensions")
            
            # Inizializza driver
            st.write("Inizializzazione Chrome...")
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
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
            return False
            
    def save_debug_screenshot(self, prefix: str):
        """Utility per salvare screenshot di debug"""
        try:
            filename = f"debug_{prefix}_{int(time.time())}.png"
            self.driver.save_screenshot(filename)
            st.write(f"📸 Screenshot salvato: {filename}")
        except Exception as e:
            st.error(f"❌ Errore salvataggio screenshot: {str(e)}")
        
    def cleanup(self):
        """Pulizia risorse del driver"""
        if self.driver:
            try:
                self.driver.quit()
                st.write("✅ Driver chiuso correttamente")
            except Exception as e:
                st.error(f"❌ Errore chiusura driver: {str(e)}")
                
    def wait_for_element(self, by: By, value: str, timeout: int = None) -> bool:
        """
        Attende la presenza di un elemento con timeout
        Args:
            by: Tipo di selettore (By.ID, By.CLASS_NAME, etc)
            value: Valore del selettore
            timeout: Timeout in secondi (opzionale)
        Returns:
            bool: True se elemento trovato, False se timeout
        """
        try:
            wait = WebDriverWait(self.driver, timeout or self.wait_time)
            wait.until(EC.presence_of_element_located((by, value)))
            return True
        except:
            return False

    def is_element_present(self, by: By, value: str) -> bool:
        """
        Verifica se un elemento è presente nella pagina
        Args:
            by: Tipo di selettore
            value: Valore del selettore
        Returns:
            bool: True se presente, False altrimenti
        """
        try:
            self.driver.find_element(by, value)
            return True
        except:
            return False

    @abstractmethod
    def login(self, username: str, password: str) -> bool:
        """
        Metodo astratto per il login
        Args:
            username: Username per il login
            password: Password per il login
        Returns:
            bool: True se login riuscito, False altrimenti
        """
        pass

    @abstractmethod
    def get_auctions(self) -> list:
        """
        Metodo astratto per recuperare le aste
        Returns:
            list: Lista delle aste trovate
        """
        pass

    @abstractmethod
    def get_vehicles(self, auction_id: str) -> list:
        """
        Metodo astratto per recuperare i veicoli di un'asta
        Args:
            auction_id: ID dell'asta
        Returns:
            list: Lista dei veicoli trovati
        """
        pass

    @abstractmethod
    def scrape(self, username: str = None, password: str = None) -> list:
        """
        Metodo astratto principale di scraping
        Args:
            username: Username opzionale
            password: Password opzionale
        Returns:
            list: Lista dei dati recuperati
        """
        pass