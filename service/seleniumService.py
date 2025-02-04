from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth
import traceback

from service.dropBoxService import upload_screenshot_result

class SeleniumService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._init_driver()
        return cls._instance

    def _init_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")

            self.service = Service('/app/.chrome-for-testing/chromedriver-linux64/chromedriver')

            self.driver = webdriver.Chrome(service=self.service, options=chrome_options)

            stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="MacIntel",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
            
        except Exception as e:
            print(f"_init_driver | Errore durante l'inizializzazione del driver Selenium: {e}")
            self.driver = None

    def validification(self, url):
        if not self.driver:
            raise RuntimeError("Il driver Selenium non è stato inizializzato correttamente.")
        try:
            self.driver.get(url)

            wait = WebDriverWait(self.driver, 15)
            self.driver.save_screenshot('screenshot.png')
            upload_screenshot_result()
            img = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.is-front")))
            if img:
                tabella = self.driver.find_element(By.CSS_SELECTOR, ".table.article-table.table-striped")
                listaPrezzi = tabella.find_elements(By.CSS_SELECTOR, 
                                                    "div.price-container.d-none.d-md-flex.justify-content-end span.color-primary.small.text-end.text-nowrap.fw-bold")
            
            if listaPrezzi:
                return float(listaPrezzi[0].text.replace("€", "").replace(",", ".").strip())
            else:
                print("al momento non sono state torvate inserizioni per la carta cercata")
                return None
        except Exception as e:
            print(f"validification | Errore durante la validazione dell'URL: {str(e)}")
            traceback.print_exc()
            return None
        
    def get_prize(self, url):
        if not self.driver:
            raise RuntimeError("Il driver Selenium non è stato inizializzato correttamente.")
        try:
            self.driver.get(url)
            if self.driver.find_element(By.CSS_SELECTOR, "img.is-front") is not None:
                tabella = self.driver.find_element(By.CSS_SELECTOR, ".table.article-table.table-striped")

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 
                        "div.price-container.d-none.d-md-flex.justify-content-end span.color-primary.small.text-end.text-nowrap.fw-bold"))
                )

                listaPrezzi = tabella.find_elements(By.CSS_SELECTOR, 
                    "div.price-container.d-none.d-md-flex.justify-content-end span.color-primary.small.text-end.text-nowrap.fw-bold")
                return float(listaPrezzi[0].text.replace("€", "").replace(",", ".").strip())
        except NoSuchElementException:
            print("Elemento richiesto non trovato sulla pagina.")
            return None
        except Exception as e:
            print(f"get_prize | Errore durante il recupero del prezzo: {e}")
            return None
        
    def update_prize(self, url):
        print("all'interno di selenium con update prize")
        try:
            self.driver.get(url)
            lista_dati = self.driver.find_elements(By.CSS_SELECTOR, "div.info-list-container dl.labeled dd")
            if len(lista_dati) >= 6 and len(lista_dati) <= 10:
                prezzo_corrente = float(lista_dati[6].text.replace("€", "").replace(",", "."))
            else:
                prezzo_corrente = float(lista_dati[7].text.replace("€", "").replace(",", "."))

            tabella = self.driver.find_element(By.CSS_SELECTOR, ".table.article-table.table-striped")
            listaPrezzi = tabella.find_elements(By.CSS_SELECTOR, 
                "div.price-container.d-none.d-md-flex.justify-content-end span.color-primary.small.text-end.text-nowrap.fw-bold")
            prezzo_attuale =  float(listaPrezzi[0].text.replace("€", "").replace(",", ".").strip())
            print(f"prezzo trovato= {prezzo_attuale}")
            self.driver.save_screenshot('screenshot.png')
            upload_screenshot_result()
            return {
                "prezzo_di_tendenza": prezzo_corrente,
                "prezzo_attuale" : prezzo_attuale
            }
        except NoSuchElementException:
            print("Elemento richiesto non trovato sulla pagina.")
            return None
        except Exception as e:
            print(f"update_prize | Errore durante il recupero del prezzo: {e}")
            return None

    def quit(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            SeleniumService._instance = None