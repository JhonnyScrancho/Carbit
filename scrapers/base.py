from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        try:
            st.write("🔧 Setup Chrome Driver:")
            
            # Info sistema
            st.write(f"Sistema Operativo: {platform.system()} {platform.release()}")
            st.write(f"Python Version: {platform.python_version()}")
            
            # Opzioni Chrome
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Configurazioni specifiche per Chromium su Debian
            chrome_options.binary_location = "/usr/bin/chromium"
            
            # Setup del service con chromedriver per Chromium
            st.write("Installazione ChromeDriver per Chromium...")
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            
            # Inizializzazione driver
            st.write("Inizializzazione Chromium...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_time)
            
            # Test di navigazione
            st.write("Test di navigazione...")
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