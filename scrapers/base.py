from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import chromedriver_autoinstaller
import streamlit as st
import platform
import os
import subprocess
import time
import wget
import shutil

class BaseScraper(ABC):
    def __init__(self):
        self.driver = None
        self.wait_time = 20
        self.wait = None
        self.debug = True

    def install_chrome(self):
        """Installa Chrome automaticamente in ambiente Linux"""
        try:
            st.write("🔄 Installazione automatica Chrome...")
            
            # Installa dipendenze
            os.system('apt-get update')
            os.system('apt-get install -y wget unzip libnss3 libgconf-2-4')
            
            # Scarica e installa Chrome
            chrome_deb = wget.download(
                "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb",
                "chrome.deb"
            )
            
            os.system('dpkg -i chrome.deb || apt-get install -f -y')
            os.system('apt-get install -f -y')  # Fix dipendenze
            
            # Pulisci file temporanei
            if os.path.exists("chrome.deb"):
                os.remove("chrome.deb")
                
            st.success("✅ Chrome installato correttamente")
            return True
        except Exception as e:
            st.error(f"❌ Errore installazione Chrome: {str(e)}")
            return False

    def check_chrome_installation(self):
        """Verifica e installa Chrome se necessario"""
        try:
            subprocess.run(['google-chrome', '--version'], 
                         capture_output=True, 
                         check=True)
            st.write("✅ Google Chrome trovato")
            return True
        except:
            st.warning("⚠️ Chrome non trovato, tentativo di installazione automatica...")
            return self.install_chrome()

    def setup_driver(self) -> bool:
        """Setup dettagliato del webdriver con gestione errori"""
        try:
            st.write("🔧 Setup Chrome Driver:")
            
            # Info sistema
            st.write(f"Sistema Operativo: {platform.system()} {platform.release()}")
            st.write(f"Python Version: {platform.python_version()}")
            
            # Verifica/Installa Chrome
            if not self.check_chrome_installation():
                return False
            
            # Installa/aggiorna chromedriver
            st.write("Installing/updating chromedriver...")
            chromedriver_path = chromedriver_autoinstaller.install()
            st.write(f"Chromedriver path: {chromedriver_path}")
            
            # Opzioni Chrome per ambiente cloud/container
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Opzioni aggiuntive per stabilità
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Test dell'user agent
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Inizializza driver
            st.write("Inizializzazione Chrome...")
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_time)
            
            # Verifica inizializzazione
            if self.driver:
                st.write("✅ Driver inizializzato correttamente")
                # Test di navigazione base
                self.driver.get("https://www.google.com")
                st.write("✅ Test di navigazione base completato")
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