from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from scrapers.base import BaseScraper
import time
import streamlit as st

class ClickarScraper(BaseScraper):
    def __init__(self):
        super().__init__(headless=False)  # Disabilitato headless per debug
        self.base_url = "https://www.clickar.biz/private"
        self.login_url = "https://sts.fiatgroup.com"
        self.setup_driver()
    
    def login(self, username, password):
        """Handle the login flow for Clickar"""
        try:
            self.log("Navigazione alla pagina di login...")
            self.driver.get(self.base_url)
            time.sleep(5)
            
            self.log("Attesa campo username...")
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "userNameInput"))
            )
            
            self.log("Compilazione credenziali...")
            password_field = self.driver.find_element(By.ID, "passwordInput")
            submit_button = self.driver.find_element(By.ID, "submitButton")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            self.log("Click sul bottone login...")
            submit_button.click()
            
            self.log("Attesa completamento login...")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "carusedred"))
            )
            
            self.log("Login completato con successo")
            return True
            
        except Exception as e:
            self.log(f"Login fallito: {str(e)}", "error")
            # Salva screenshot per debug
            try:
                screenshot_path = "login_error.png"
                self.driver.save_screenshot(screenshot_path)
                self.log(f"Screenshot salvato in {screenshot_path}")
            except:
                self.log("Impossibile salvare screenshot", "error")
            return False
            
    def navigate_to_introvabili(self):
        try:
            self.log("Attesa caricamento pagina principale...")
            time.sleep(5)
            
            self.log("Ricerca sezione INTROVABILI...")
            try:
                introvabili = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//h4[contains(text(), 'LE INTROVABILI')]"))
                )
                self.log("Sezione INTROVABILI trovata (h4)")
                introvabili.click()
                return True
            except TimeoutException:
                self.log("Tentativo alternativo di ricerca INTROVABILI...", "warning")
                introvabili_links = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'INTROVABILI')]")
                if introvabili_links:
                    self.log("Sezione INTROVABILI trovata (link)")
                    introvabili_links[0].click()
                    time.sleep(5)
                    return True
                else:
                    self.log("Sezione INTROVABILI non trovata", "error")
                    return False
                    
        except Exception as e:
            self.log(f"Errore navigazione INTROVABILI: {str(e)}", "error")
            return False

    def get_all_vehicles(self):
        """Get all vehicles from all pages"""
        all_vehicles = []
        page = 1
        
        while True:
            try:
                self.log(f"Elaborazione pagina {page}...")
                
                # Attendi caricamento tabella
                self.log("Attesa caricamento tabella veicoli...")
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "rich-table-row"))
                )
                time.sleep(3)
                
                # Trova tutte le righe
                rows = self.driver.find_elements(By.CLASS_NAME, "rich-table-row")
                self.log(f"Trovate {len(rows)} righe nella pagina {page}")
                
                for idx, row in enumerate(rows, 1):
                    self.log(f"Elaborazione veicolo {idx}/{len(rows)} della pagina {page}")
                    vehicle_data = self.extract_vehicle_data(row)
                    if vehicle_data and vehicle_data.get('plate'):
                        all_vehicles.append(vehicle_data)
                
                self.log(f"Veicoli totali trovati finora: {len(all_vehicles)}")
                
                # Gestione paginazione
                next_page = self.driver.find_elements(
                    By.XPATH, 
                    f"//a[contains(@class, 'page-item') and text()='{page + 1}']"
                )
                
                if not next_page:
                    self.log("Nessuna pagina successiva trovata")
                    break
                    
                self.log(f"Passaggio alla pagina {page + 1}")
                next_page[0].click()
                page += 1
                time.sleep(5)
                
            except Exception as e:
                self.log(f"Errore nella pagina {page}: {str(e)}", "error")
                break
                
        return all_vehicles
        
    def scrape(self, username, password):
        """Main scraping method"""
        try:
            if not self.login(username, password):
                print("Login failed")
                return None
                
            if not self.navigate_to_introvabili():
                print("Navigation to INTROVABILI failed")
                return None
                
            vehicles = self.get_all_vehicles()
            
            if not vehicles:
                print("No vehicles found")
                return None
                
            return vehicles
            
        except Exception as e:
            print(f"Scraping failed: {str(e)}")
            return None
        finally:
            self.cleanup()

    # Implementazione dei metodi astratti della classe base
    def get_auctions(self):
        """Non implementato per Clickar perché usa una struttura diversa"""
        return []

    def get_vehicles(self, auction_id: str):
        """Non implementato per Clickar perché usa una struttura diversa"""
        return []