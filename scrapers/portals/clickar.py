# scrapers/portals/clickar.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapers.base import BaseScraper
import time

class ClickarScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.clickar.biz/private"
        self.login_url = "https://sts.fiatgroup.com"
        self.setup_driver()  # Inizializza subito il driver
    
    def login(self, username, password):
        """Handle the login flow for Clickar"""
        try:
            self.driver.get(self.base_url)
            time.sleep(5)  # Attendi il redirect
            
            # Attendi e compila le credenziali
            username_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "userNameInput"))
            )
            password_field = self.driver.find_element(By.ID, "passwordInput")
            submit_button = self.driver.find_element(By.ID, "submitButton")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            submit_button.click()
            
            # Attendi il redirect dopo il login
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "carusedred"))
            )
            return True
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
            
    def navigate_to_introvabili(self):
        """Navigate to 'LE INTROVABILI' section"""
        try:
            time.sleep(5)  # Attendi caricamento pagina
            # Cerca il link INTROVABILI
            introvabili_links = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'INTROVABILI')]")
            if introvabili_links:
                introvabili_links[0].click()
                time.sleep(5)  # Attendi caricamento sezione
                return True
                
            # Alternativa: cerca per h4
            introvabili = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//h4[contains(text(), 'LE INTROVABILI')]"))
            )
            introvabili.click()
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"Navigation to INTROVABILI failed: {str(e)}")
            return False
            
    def extract_vehicle_data(self, row):
        """Extract data from a vehicle row"""
        try:
            data = {}
            # Usa try/except per ogni campo per evitare errori se manca qualcosa
            try:
                data['brand_model'] = row.find_element(By.XPATH, ".//td[4]").text.strip()
            except: data['brand_model'] = ''
            
            try:
                data['plate'] = row.find_element(By.XPATH, ".//td[5]").text.strip()
            except: data['plate'] = ''
            
            try:
                data['vin'] = row.find_element(By.XPATH, ".//td[6]").text.strip()
            except: data['vin'] = ''
            
            try:
                data['year'] = row.find_element(By.XPATH, ".//td[7]").text.strip()
            except: data['year'] = ''
            
            try:
                data['lot'] = row.find_element(By.XPATH, ".//td[8]").text.strip()
            except: data['lot'] = ''
            
            try:
                data['location'] = row.find_element(By.XPATH, ".//td[9]").text.strip()
            except: data['location'] = ''
            
            try:
                price_text = row.find_element(By.XPATH, ".//td[10]").text.strip()
                # Converte il prezzo in numero
                data['base_price'] = float(price_text.replace('€', '').replace('.', '').replace(',', '.').strip())
            except:
                data['base_price'] = 0
            
            try:
                data['auction_type'] = row.find_element(By.XPATH, ".//td[11]").text.strip()
            except: data['auction_type'] = ''
            
            try:
                data['km'] = row.find_element(By.XPATH, ".//td[12]").text.strip()
            except: data['km'] = ''
            
            try:
                data['damages'] = row.find_element(By.XPATH, ".//td[13]").text.strip()
            except: data['damages'] = ''
            
            try:
                data['status'] = row.find_element(By.XPATH, ".//td[14]").text.strip()
            except: data['status'] = ''
            
            # Get image URL
            try:
                img_element = row.find_element(By.XPATH, ".//img[contains(@src, 'ticonet')]")
                data['image_url'] = img_element.get_attribute('src')
            except:
                data['image_url'] = None
                
            return data
            
        except Exception as e:
            print(f"Error extracting vehicle data: {str(e)}")
            return None
            
    def get_all_vehicles(self):
        """Get all vehicles from all pages"""
        all_vehicles = []
        page = 1
        
        while True:
            try:
                # Attendi caricamento tabella
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "rich-table-row"))
                )
                time.sleep(3)  # Attendi caricamento completo
                
                # Trova tutte le righe della tabella
                rows = self.driver.find_elements(By.CLASS_NAME, "rich-table-row")
                print(f"Found {len(rows)} rows on page {page}")
                
                for row in rows:
                    vehicle_data = self.extract_vehicle_data(row)
                    if vehicle_data and vehicle_data.get('plate'):  # Verifica dati minimi
                        all_vehicles.append(vehicle_data)
                
                # Cerca paginazione
                next_page = self.driver.find_elements(By.XPATH, f"//a[contains(@class, 'page-item') and text()='{page + 1}']")
                if not next_page:
                    break
                    
                next_page[0].click()
                page += 1
                time.sleep(5)  # Attendi caricamento pagina
                
            except Exception as e:
                print(f"Error processing page {page}: {str(e)}")
                break
                
        print(f"Total vehicles found: {len(all_vehicles)}")
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