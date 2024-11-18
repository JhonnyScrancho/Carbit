from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
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
                    EC.presence_of_element_located((By.ID, "userNameInput"))
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
                    By.ID, "passwordInput"
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
                (By.XPATH, "//span[contains(text(), 'INTROVABILI')]")
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
            self.save_screenshot_st("navigation_error")
            return False
                
        except Exception as e:
            st.error(f"Errore navigazione: {str(e)}")
            self.save_screenshot_st("navigation_error")
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
