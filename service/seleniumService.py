from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class SeleniumService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._init_driver()
        return cls._instance

    def _init_driver(self):
        """Inizializza il driver Selenium."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox') 
            chrome_options.add_argument('--disable-dev-shm-usage')

            self.service = Service('/app/.chrome-for-testing/chromedriver-linux64/chromedriver')
            self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        except Exception as e:
            print(f"Errore durante l'inizializzazione del driver Selenium: {e}")
            self.driver = None

    def validification(self, url):
        """Verifica la validità di un URL e restituisce il prezzo o None."""
        if not self.driver:
            raise RuntimeError("Il driver Selenium non è stato inizializzato correttamente.")
        try:
            self.driver.get(url)

            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "img.is-front"))
            )

            tabella = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".table.article-table.table-striped"))
            )
            listaPrezzi = tabella.find_elements(By.CSS_SELECTOR, 
                "div.price-container.d-none.d-md-flex.justify-content-end span.color-primary.small.text-end.text-nowrap.fw-bold")
            return float(listaPrezzi[0].text.replace("€", "").replace(",", ".").strip())
        except NoSuchElementException:
            print("Elemento richiesto non trovato sulla pagina.")
            return None
        except Exception as e:
            print(f"Errore durante la validazione dell'URL: {e}")
            return None

    def get_prize(self, url):
        """Ottiene il prezzo dalla pagina data."""
        if not self.driver:
            raise RuntimeError("Il driver Selenium non è stato inizializzato correttamente.")
        try:
            self.driver.get(url)

            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "img.is-front"))
            )

            tabella = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".table.article-table.table-striped"))
            )
            listaPrezzi = tabella.find_elements(By.CSS_SELECTOR, 
                "div.price-container.d-none.d-md-flex.justify-content-end span.color-primary.small.text-end.text-nowrap.fw-bold")
            return float(listaPrezzi[0].text.replace("€", "").replace(",", ".").strip())
        except NoSuchElementException:
            print("Elemento richiesto non trovato sulla pagina.")
            return None
        except Exception as e:
            print(f"Errore durante il recupero del prezzo: {e}")
            return None
        
    def update_prize(self, url):
        """Aggiorna il prezzo sulla pagina."""
        try:
            self.driver.get(url)

            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.info-list-container dl.labeled dd"))
            )
            lista_dati = self.driver.find_elements(By.CSS_SELECTOR, "div.info-list-container dl.labeled dd")
            if len(lista_dati) >= 6 and len(lista_dati) <= 10:
                prezzo_corrente = float(lista_dati[6].text.replace("€","").replace(",","."))
            else:
                prezzo_corrente = float(lista_dati[7].text.replace("€","").replace(",","."))

            tabella = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".table.article-table.table-striped"))
            )
            listaPrezzi = tabella.find_elements(By.CSS_SELECTOR, 
                "div.price-container.d-none.d-md-flex.justify-content-end span.color-primary.small.text-end.text-nowrap.fw-bold")
            prezzo_attuale =  float(listaPrezzi[0].text.replace("€", "").replace(",", ".").strip())
            return {
                "prezzo_di_tendenza": prezzo_corrente,
                "prezzo_attuale" : prezzo_attuale
            }
        except NoSuchElementException:
            print("Elemento richiesto non trovato sulla pagina.")
            return None
        except Exception as e:
            print(f"Errore durante il recupero del prezzo: {e}")
            return None

    def quit(self):
        """Chiude il driver e rilascia le risorse."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            SeleniumService._instance = None