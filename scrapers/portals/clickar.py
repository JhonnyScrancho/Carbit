from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scrapers.base import BaseScraper
import time
import streamlit as st

class ClickarScraper(BaseScraper):
    def __init__(self):
        """Inizializzazione dello scraper Clickar"""
        super().__init__()
        self.base_url = "https://www.clickar.biz/private"
        self.wait_time = 20
        
    def login(self, username: str, password: str) -> bool:
        """
        Gestisce il flusso di login su Clickar
        Args:
            username: Username per il login
            password: Password per il login
        Returns:
            bool: True se il login ha successo, False altrimenti
        """
        try:
            # 1. Navigazione alla pagina principale
            st.write("🌐 Navigazione alla homepage...")
            self.driver.get(self.base_url)
            time.sleep(5)  # Attesa caricamento iniziale
            
            # 2. Gestione iframe login
            st.write("🔄 Ricerca form di login...")
            
            # Verifica presenza iframe o form diretto
            if self.is_element_present(By.ID, "loginFrame"):
                iframe = self.wait.until(
                    EC.presence_of_element_located((By.ID, "loginFrame"))
                )
                self.driver.switch_to.frame(iframe)
                
            # 3. Compila form login
            st.write("📝 Compilazione credenziali...")
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "userNameInput"))
            )
            password_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "passwordInput"))
            )
            
            # Clear e input con retry
            for _ in range(3):  # 3 tentativi
                try:
                    username_field.clear()
                    username_field.send_keys(username)
                    password_field.clear()
                    password_field.send_keys(password)
                    break
                except:
                    time.sleep(1)
            
            # 4. Submit login
            st.write("🔐 Invio credenziali...")
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "submitButton"))
            )
            submit_button.click()
            time.sleep(3)  # Attesa post-click
            
            # 5. Torna al contesto principale
            if self.is_element_present(By.ID, "loginFrame"):
                self.driver.switch_to.default_content()
            
            # 6. Verifica login
            st.write("✅ Verifica login...")
            try:
                # Verifica multipla per conferma login
                success = any([
                    self.wait_for_element(By.CLASS_NAME, "carusedred", 10),
                    self.wait_for_element(By.CLASS_NAME, "user-menu", 5),
                    self.wait_for_element(By.CLASS_NAME, "logged-user", 5)
                ])
                
                if success:
                    st.success("Login completato con successo!")
                    return True
                else:
                    st.error("Login fallito - Menu non trovato")
                    return False
                    
            except TimeoutException:
                st.error("Login fallito - Timeout verifica")
                return False
                
        except Exception as e:
            st.error(f"Errore durante il login: {str(e)}")
            self.save_debug_screenshot("login_error")
            return False

    def navigate_to_introvabili(self) -> bool:
        """
        Naviga alla sezione INTROVABILI
        Returns:
            bool: True se la navigazione ha successo, False altrimenti
        """
        try:
            st.write("⌛ Attesa caricamento pagina...")
            time.sleep(5)
            
            st.write("🔍 Ricerca sezione INTROVABILI...")
            
            # Lista di possibili selettori per il link Introvabili
            selectors = [
                "//span[contains(text(), 'INTROVABILI')]",
                "//h4[contains(text(), 'LE INTROVABILI')]",
                "//a[contains(text(), 'INTROVABILI')]",
                "//div[contains(@class, 'menu')]//a[contains(text(), 'Introvabili')]"
            ]
            
            # Prova ogni selettore
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    element.click()
                    time.sleep(3)
                    
                    # Verifica che siamo nella pagina corretta
                    if any([
                        self.is_element_present(By.CLASS_NAME, "vehiclesTable"),
                        self.is_element_present(By.CLASS_NAME, "vehicleRow"),
                        self.is_element_present(By.ID, "vehiclesList")
                    ]):
                        st.success("Navigazione completata!")
                        return True
                except:
                    continue
            
            st.error("Sezione INTROVABILI non trovata")
            self.save_debug_screenshot("navigation_error")
            return False
                
        except Exception as e:
            st.error(f"Errore navigazione: {str(e)}")
            self.save_debug_screenshot("navigation_error")
            return False

    def extract_vehicle_data(self, row) -> dict:
        """
        Estrae i dati di un veicolo da una riga della tabella
        Args:
            row: Elemento selenium rappresentante la riga
        Returns:
            dict: Dati del veicolo o None se estrazione fallita
        """
        try:
            data = {}
            
            # Mappatura celle -> dati (adatta in base alla struttura reale)
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 6:
                    data = {
                        'plate': cells[0].text.strip(),
                        'brand': cells[1].text.strip(),
                        'model': cells[2].text.strip(),
                        'year': cells[3].text.strip(),
                        'km': cells[4].text.strip(),
                        'location': cells[5].text.strip(),
                        'base_price': cells[6].text.strip() if len(cells) > 6 else "N/D"
                    }
            except:
                # Tentativo alternativo con classi specifiche
                try:
                    data = {
                        'plate': row.find_element(By.CLASS_NAME, "plateCell").text.strip(),
                        'brand': row.find_element(By.CLASS_NAME, "brandCell").text.strip(),
                        'model': row.find_element(By.CLASS_NAME, "modelCell").text.strip(),
                        'year': row.find_element(By.CLASS_NAME, "yearCell").text.strip(),
                        'km': row.find_element(By.CLASS_NAME, "kmCell").text.strip(),
                        'location': row.find_element(By.CLASS_NAME, "locationCell").text.strip(),
                        'base_price': row.find_element(By.CLASS_NAME, "priceCell").text.strip()
                    }
                except:
                    return None
            
            # Formatta e standardizza i dati
            return {
                'plate': data.get('plate', 'N/D'),
                'brand_model': f"{data.get('brand', '')} {data.get('model', '')}".strip(),
                'year': data.get('year', 'N/D'),
                'km': data.get('km', 'N/D'),
                'location': data.get('location', 'N/D'),
                'base_price': data.get('base_price', 'N/D'),
                'status': 'active',
                'fonte': 'Clickar',
                'last_update': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            st.warning(f"Errore estrazione dati: {str(e)}")
            return None

    def get_all_vehicles(self) -> list:
        """
        Recupera tutti i veicoli da tutte le pagine
        Returns:
            list: Lista dei veicoli trovati
        """
        vehicles = []
        page = 1
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                st.write(f"📃 Elaborazione pagina {page}...")
                
                # Attesa caricamento tabella (prova diversi selettori)
                table_found = any([
                    self.wait_for_element(By.CLASS_NAME, "vehiclesTable", 10),
                    self.wait_for_element(By.CLASS_NAME, "vehiclesList", 5),
                    self.wait_for_element(By.CLASS_NAME, "rich-table", 5)
                ])
                
                if not table_found:
                    st.error("Tabella veicoli non trovata")
                    break
                
                time.sleep(3)  # Attesa aggiuntiva per caricamento dati
                
                # Ricerca righe veicoli con diversi selettori
                rows = []
                for selector in [
                    "vehicleRow",
                    "rich-table-row",
                    "vehicle-item"
                ]:
                    rows = self.driver.find_elements(By.CLASS_NAME, selector)
                    if rows:
                        break
                
                if not rows:
                    st.warning(f"Nessun veicolo trovato nella pagina {page}")
                    break
                
                # Estrazione dati veicoli
                page_vehicles = []
                for idx, row in enumerate(rows, 1):
                    try:
                        vehicle = self.extract_vehicle_data(row)
                        if vehicle and vehicle.get('plate'):
                            page_vehicles.append(vehicle)
                            st.write(f"✅ Veicolo {idx} estratto: {vehicle['plate']}")
                        else:
                            st.warning(f"⚠️ Dati incompleti per veicolo {idx}")
                    except Exception as e:
                        st.error(f"❌ Errore estrazione veicolo {idx}: {str(e)}")
                        continue
                
                vehicles.extend(page_vehicles)
                st.success(f"Trovati {len(page_vehicles)} veicoli nella pagina {page}")
                
                # Gestione paginazione
                next_page_found = False
                for selector in [
                    f"//a[contains(@class, 'pageNumber') and text()='{page + 1}']",
                    f"//a[contains(@class, 'page-item') and text()='{page + 1}']",
                    f"//span[contains(@class, 'pageNumber') and text()='{page + 1}']"
                ]:
                    try:
                        next_page = self.driver.find_element(By.XPATH, selector)
                        next_page.click()
                        next_page_found = True
                        time.sleep(3)
                        break
                    except:
                        continue
                
                if not next_page_found:
                    st.info("Nessuna pagina successiva trovata")
                    break
                
                page += 1
                retry_count = 0  # Reset retry count on successful page
                
            except Exception as e:
                retry_count += 1
                st.error(f"Errore nella pagina {page} (tentativo {retry_count}/{max_retries}): {str(e)}")
                self.save_debug_screenshot(f"page_{page}_error_{retry_count}")
                if retry_count >= max_retries:
                    st.error("Numero massimo di tentativi raggiunti")
                    break
                time.sleep(2)  # Attesa prima del retry
                
        st.success(f"✅ Trovati {len(vehicles)} veicoli totali")
        return vehicles

    def scrape(self, username: str = None, password: str = None) -> list:
        """
        Metodo principale di scraping
        Args:
            username: Username opzionale per il login
            password: Password opzionale per il login
        Returns:
            list: Lista dei veicoli trovati o None se errore
        """
        try:
            # Verifica credenziali
            if not username or not password:
                st.error("❌ Credenziali mancanti")
                return None
            
            # Setup iniziale se necessario
            if not self.driver:
                if not self.setup_driver():
                    st.error("❌ Setup driver fallito")
                    return None
            
            # Login
            st.write("🔐 Tentativo login...")
            if not self.login(username, password):
                st.error("❌ Login fallito")
                return None
            
            # Navigazione a Introvabili
            st.write("🔍 Navigazione a sezione Introvabili...")
            if not self.navigate_to_introvabili():
                st.error("❌ Navigazione fallita")
                return None
            
            # Recupero veicoli
            st.write("🚗 Recupero veicoli...")
            vehicles = self.get_all_vehicles()
            
            if not vehicles:
                st.warning("⚠️ Nessun veicolo trovato")
                return None
            
            return vehicles
            
        except Exception as e:
            st.error(f"❌ Errore durante lo scraping: {str(e)}")
            self.save_debug_screenshot("scrape_error")
            return None
        finally:
            try:
                self.cleanup()
                st.write("🧹 Pulizia browser completata")
            except Exception as e:
                st.warning(f"⚠️ Errore durante la pulizia: {str(e)}")

    # Implementazione metodi astratti richiesti da BaseScraper
    def get_auctions(self) -> list:
        """Non implementato per Clickar (struttura diversa)"""
        return []

    def get_vehicles(self, auction_id: str) -> list:
        """Non implementato per Clickar (struttura diversa)"""
        return []