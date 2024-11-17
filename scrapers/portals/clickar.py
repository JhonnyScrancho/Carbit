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
        
    def login(self, username, password):
        """Handle the dynamic redirect login flow for Clickar"""
        try:
            self.driver.get(self.base_url)
            # Wait for redirect to login page
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "userNameInput"))
            )
            
            # Input credentials
            username_field = self.driver.find_element(By.ID, "userNameInput")
            password_field = self.driver.find_element(By.ID, "passwordInput")
            submit_button = self.driver.find_element(By.ID, "submitButton")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            submit_button.click()
            
            # Wait for successful login and redirect
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "carusedred"))
            )
            return True
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
            
    def navigate_to_introvabili(self):
        """Navigate to 'LE INTROVABILI' section"""
        try:
            # Find and click the INTROVABILI section
            introvabili = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//h4[contains(text(), 'LE INTROVABILI')]"))
            )
            introvabili.click()
            return True
        except Exception as e:
            print(f"Navigation to INTROVABILI failed: {str(e)}")
            return False
            
    def extract_vehicle_data(self, row):
        """Extract data from a vehicle row"""
        try:
            data = {
                'brand_model': row.find_element(By.XPATH, ".//td[4]").text,
                'plate': row.find_element(By.XPATH, ".//td[5]").text,
                'vin': row.find_element(By.XPATH, ".//td[6]").text,
                'year': row.find_element(By.XPATH, ".//td[7]").text,
                'lot': row.find_element(By.XPATH, ".//td[8]").text,
                'location': row.find_element(By.XPATH, ".//td[9]").text,
                'base_price': row.find_element(By.XPATH, ".//td[10]").text,
                'auction_type': row.find_element(By.XPATH, ".//td[11]").text,
                'km': row.find_element(By.XPATH, ".//td[12]").text,
                'damages': row.find_element(By.XPATH, ".//td[13]").text,
                'status': row.find_element(By.XPATH, ".//td[14]").text
            }
            
            # Get image URL if available
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
                # Wait for vehicle table to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "rich-table-row"))
                )
                
                # Extract current page vehicles
                rows = self.driver.find_elements(By.CLASS_NAME, "rich-table-row")
                for row in rows:
                    vehicle_data = self.extract_vehicle_data(row)
                    if vehicle_data:
                        all_vehicles.append(vehicle_data)
                
                # Check for next page
                next_page = self.driver.find_elements(By.XPATH, f"//li[@class='page-item']/a[text()='{page + 1}']")
                if not next_page:
                    break
                    
                next_page[0].click()
                page += 1
                time.sleep(2)  # Wait for page load
                
            except Exception as e:
                print(f"Error processing page {page}: {str(e)}")
                break
                
        return all_vehicles
        
    def scrape(self, username, password):
        """Main scraping method"""
        try:
            if not self.login(username, password):
                return None
                
            if not self.navigate_to_introvabili():
                return None
                
            vehicles = self.get_all_vehicles()
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