# scrapers/portals/ayvens.py
from typing import Dict, List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from ..base import BaseScraper
import requests
import PyPDF2
import io
import re
import time
from urllib.parse import urljoin

class AyvensScraper(BaseScraper):
    """Scraper specifico per il portale Ayvens/ALD/Leaseplan"""
    
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.base_url = "https://carmarket.ayvens.com"
        self.is_logged_in = False

    def login(self, username: str = "justcars", password: str = "Sandaliecalzini11!") -> bool:
        """
        Esegue il login sul portale Ayvens
        Returns:
            bool: True se login riuscito, False altrimenti
        """
        try:
            if not self.driver:
                self.setup_driver()
            
            # Naviga alla homepage
            self.driver.get(self.base_url)
            
            # Click sul bottone login
            login_btn = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary text-uppercase text-bold dropdown-toggle"))
            )
            login_btn.click()
            
            # Compila form login
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, "Username")))
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "Password")))
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # Submit login
            submit_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
            )
            submit_btn.click()
            
            # Verifica login successo
            try:
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "user-menu")))
                self.is_logged_in = True
                print("Login effettuato con successo")
                return True
            except TimeoutException:
                print("Login fallito - Menu utente non trovato")
                return False
                
        except Exception as e:
            print(f"Errore durante il login: {str(e)}")
            return False

    def get_italian_auctions(self) -> List[Dict]:
        """
        Recupera tutte le aste italiane disponibili
        Returns:
            List[Dict]: Lista di aste italiane con relativi dettagli
        """
        if not self.is_logged_in:
            print("Login necessario prima di recuperare le aste")
            return []

        auctions = []
        try:
            # Trova tutte le aste con icona italiana
            italian_auctions = self.driver.find_elements(
                By.XPATH, 
                "//use[@xlink:href='#icon-round-ITA']/ancestor::div[contains(@class, 'auction-item')]"
            )

            for auction in italian_auctions:
                try:
                    # Estrai ID asta dal bottone "MOSTRA DI PIÙ"
                    more_btn = auction.find_element(
                        By.XPATH,
                        ".//a[@data-show-button-sale-code]"
                    )
                    auction_id = more_btn.get_attribute('data-show-button-saleeventid')
                    
                    auction_data = {
                        'id': auction_id,
                        'url': f"/it-it/sales/{auction_id}/",
                        'title': auction.find_element(By.CLASS_NAME, 'auction-title').text,
                        'end_date': auction.find_element(By.CLASS_NAME, 'auction-end-date').text,
                        'vehicle_count': auction.find_element(By.CLASS_NAME, 'vehicle-count').text
                    }
                    auctions.append(auction_data)
                    
                except Exception as e:
                    print(f"Errore nell'estrazione dati asta: {str(e)}")
                    continue

            return auctions
            
        except Exception as e:
            print(f"Errore nel recupero aste italiane: {str(e)}")
            return []

    def get_auction_vehicles(self, auction_url: str) -> List[Dict]:
        """
        Recupera tutti i veicoli di una specifica asta
        Args:
            auction_url: URL dell'asta
        Returns:
            List[Dict]: Lista di veicoli con relativi dettagli
        """
        if not self.is_logged_in:
            print("Login necessario prima di recuperare i veicoli")
            return []

        vehicles = []
        try:
            full_url = urljoin(self.base_url, auction_url)
            self.driver.get(full_url)
            
            # Attendi caricamento veicoli
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "vehicle-item")))
            
            vehicle_elements = self.driver.find_elements(By.CLASS_NAME, "vehicle-item")
            
            for vehicle in vehicle_elements:
                try:
                    # Estrai dati base veicolo
                    vehicle_data = {
                        'id': vehicle.get_attribute('id'),
                        'brand_model': vehicle.find_element(By.CLASS_NAME, 'vehicle-title').text,
                        'image_url': vehicle.find_element(By.TAG_NAME, 'img').get_attribute('src'),
                        'details': vehicle.find_element(By.CLASS_NAME, 'vehicle-details').text,
                        'documents': self._get_vehicle_documents(vehicle)
                    }
                    vehicles.append(vehicle_data)
                    
                except Exception as e:
                    print(f"Errore nell'estrazione dati veicolo: {str(e)}")
                    continue

            return vehicles
            
        except Exception as e:
            print(f"Errore nel recupero veicoli dell'asta: {str(e)}")
            return []

    def _get_vehicle_documents(self, vehicle_element) -> Dict:
        """
        Estrae i link alle perizie di un veicolo
        Args:
            vehicle_element: Elemento selenium del veicolo
        Returns:
            Dict: URLs delle perizie
        """
        try:
            documents = {
                'damage_report': None,
                'maintenance': None
            }
            
            # Trova sezione documenti
            doc_section = vehicle_element.find_element(By.CLASS_NAME, 'details-documents')
            doc_links = doc_section.find_elements(By.TAG_NAME, 'a')
            
            for link in doc_links:
                href = link.get_attribute('href')
                if 'perizia1' in href.lower():
                    documents['damage_report'] = href
                elif 'perizia2' in href.lower():
                    documents['maintenance'] = href
                    
            return documents
            
        except Exception as e:
            print(f"Errore nell'estrazione documenti: {str(e)}")
            return {'damage_report': None, 'maintenance': None}

    def scrape(self, username: str, password: str) -> List[Dict]:
        """
        Metodo principale di scraping
        Args:
            username: Username per il login
            password: Password per il login
        Returns:
            List[Dict]: Lista di tutti i veicoli trovati
        """
        try:
            # Login
            if not self.login(username, password):
                return []

            # Recupera aste italiane
            auctions = self.get_italian_auctions()
            
            # Recupera veicoli da ogni asta
            all_vehicles = []
            for auction in auctions:
                vehicles = self.get_auction_vehicles(auction['url'])
                all_vehicles.extend(vehicles)

            return all_vehicles
        except Exception as e:
            print(f"Errore nello scraping: {str(e)}")
            return []
        finally:
            self.cleanup()

    # Implementazione metodi astratti
    def get_auctions(self) -> List[Dict]:
        return self.get_italian_auctions()

    def get_vehicles(self, auction_id: str) -> List[Dict]:
        return self.get_auction_vehicles(f"/it-it/sales/{auction_id}/")