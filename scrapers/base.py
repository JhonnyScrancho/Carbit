# scrapers/base.py
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import logging
from typing import List, Dict

class BaseScraper(ABC):
    """Base scraper con funzionalità comuni a tutti i portali"""
    
    def __init__(self, headless: bool = True):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.driver = None
        self.headless = headless
        self.wait_time = 10
        
    def setup_driver(self):
        """Setup base del webdriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, self.wait_time)
        
    def cleanup(self):
        """Pulizia risorse"""
        if self.driver:
            self.driver.quit()

    @abstractmethod
    def login(self) -> bool:
        """Metodo astratto per login"""
        pass

    @abstractmethod
    def get_auctions(self) -> List[Dict]:
        """Metodo astratto per recupero aste"""
        pass

    @abstractmethod
    def get_vehicles(self, auction_id: str) -> List[Dict]:
        """Metodo astratto per recupero veicoli"""
        pass