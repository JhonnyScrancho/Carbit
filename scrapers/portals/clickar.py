from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scrapers.base import BaseScraper
import time
import streamlit as st
import base64
from io import BytesIO

class ClickarScraper(BaseScraper):
    def __init__(self, headless: bool = True):
        super().__init__(headless=headless)
        self.base_url = "https://www.clickar.biz/private"
        self.is_logged_in = False

    def save_screenshot_st(self, name: str):
        """Salva e mostra screenshot in Streamlit"""
        try:
            # Cattura screenshot
            img_binary = self.driver.get_screenshot_as_png()
            
            # Converti in base64 per mostrarlo
            img_b64 = base64.b64encode(img_binary).decode()
            
            # Mostra in Streamlit
            st.write(f"📸 Screenshot - {name}:")
            st.image(img_binary, caption=name)
            
            # Aggiungi bottone download
            st.download_button(
                label=f"📥 Scarica Screenshot {name}",
                data=img_binary,
                file_name=f"screenshot_{name}_{int(time.time())}.png",
                mime="image/png"
            )
            return True
        except Exception as e:
            st.error(f"❌ Errore salvataggio screenshot {name}: {str(e)}")
            return False

    def login(self, username: str, password: str) -> bool:
        """Gestisce il login su Clickar con form specifico"""
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False
            
            st.write("🌐 Navigazione alla homepage...")
            self.driver.get(self.base_url)
            time.sleep(5)  # Attesa caricamento iniziale
            
            # Screenshot pre-login
            self.save_screenshot_st("pre_login")
            
            st.write("🔄 Gestione iframe...")
            # Trova l'iframe corretto
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            st.write(f"Trovati {len(iframes)} iframe")
            
            login_frame = None
            for frame in iframes:
                try:
                    frame_id = frame.get_attribute('id')
                    frame_src = frame.get_attribute('src')
                    st.write(f"Frame trovato - ID: {frame_id}, SRC: {frame_src}")
                    if 'sts.fiatgroup' in frame_src or 'login' in frame_src.lower():
                        login_frame = frame
                        st.write("✅ Frame login trovato!")
                        break
                except:
                    continue
            
            if not login_frame:
                st.error("❌ Frame login non trovato")
                self.save_screenshot_st("no_frame_error")
                return False
            
            st.write("🔄 Switch al frame login...")
            self.driver.switch_to.frame(login_frame)
            time.sleep(2)
            self.save_screenshot_st("inside_frame")
            
            # Verifica presenza form
            try:
                form_area = self.wait.until(
                    EC.presence_of_element_located((By.ID, "formsAuthenticationArea"))
                )
                st.write("✅ Form di autenticazione trovato")
            except:
                st.error("❌ Form di autenticazione non trovato")
                self.save_screenshot_st("no_form_error")
                return False
            
            # Compila username usando multiple strategie
            st.write("📝 Compilazione username...")
            try:
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='email'][@id='userNameInput']"))
                )
                # Pulisci campo
                username_field.clear()
                # Invia con Actions
                actions = ActionChains(self.driver)
                actions.move_to_element(username_field)
                actions.click()
                actions.send_keys(username)
                actions.perform()
                time.sleep(1)
                
                # Verifica inserimento
                if username_field.get_attribute('value') != username:
                    # Prova metodo alternativo
                    username_field.send_keys(Keys.CONTROL + "a")  # Seleziona tutto
                    username_field.send_keys(Keys.DELETE)  # Cancella
                    username_field.send_keys(username)  # Reinserisci
                    
                st.write("✅ Username inserito")
            except:
                st.error("❌ Errore inserimento username")
                self.save_screenshot_st("username_error")
                return False
            
            # Compila password
            st.write("📝 Compilazione password...")
            try:
                password_field = self.driver.find_element(
                    By.XPATH, 
                    "//input[@type='password'][@id='passwordInput']"
                )
                # Pulisci campo
                password_field.clear()
                # Invia con Actions
                actions = ActionChains(self.driver)
                actions.move_to_element(password_field)
                actions.click()
                actions.send_keys(password)
                actions.perform()
                time.sleep(1)
                
                st.write("✅ Password inserita")
            except:
                st.error("❌ Errore inserimento password")
                self.save_screenshot_st("password_error")
                return False
            
            # Screenshot pre-submit
            self.save_screenshot_st("pre_submit")
            
            # Click sul bottone submit usando JavaScript
            st.write("🔐 Click sul bottone login...")
            try:
                submit_button = self.wait.until(
                    EC.presence_of_element_located((By.ID, "submitButton"))
                )
                
                # Prova prima click normale
                try:
                    submit_button.click()
                except:
                    # Se fallisce, usa JavaScript
                    self.driver.execute_script("arguments[0].click();", submit_button)
                    # Se anche JavaScript fallisce, prova la funzione di login diretta
                    self.driver.execute_script("Login.submitLoginRequest();")
                
                time.sleep(5)  # Attesa post-click
                
            except:
                st.error("❌ Errore click submit")
                self.save_screenshot_st("submit_error")
                return False
            
            # Torna al contesto principale
            self.driver.switch_to.default_content()
            time.sleep(5)  # Attesa post-login
            
            # Screenshot post-login
            self.save_screenshot_st("post_login")
            
            # Verifica login
            st.write("✅ Verifica login...")
            success_selectors = [
                (By.CLASS_NAME, "carusedred"),
                (By.CLASS_NAME, "user-menu"),
                (By.CLASS_NAME, "logged-user"),
                (By.XPATH, "//span[contains(text(), 'INTROVABILI')]"),
                (By.XPATH, "//a[contains(text(), 'INTROVABILI')]")
            ]
            
            for selector_type, selector_value in success_selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    st.success(f"✅ Login verificato! Elemento trovato: {selector_value}")
                    self.is_logged_in = True
                    return True
                except:
                    continue
            
            st.error("❌ Login fallito - Nessun elemento di verifica trovato")
            self.save_screenshot_st("verification_failed")
            return False
            
        except Exception as e:
            st.error(f"❌ Errore durante il login: {str(e)}")
            self.save_screenshot_st("error")
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