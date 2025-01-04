from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
                EC.presence_of_element_located((By.CSS_SELECTOR, "img.is-front"))
            )  # Attendere che l'immagine con classe 'is-front' sia presente
            print("Pagina caricata correttamente.")
            
            tabella = self.driver.find_element(By.CSS_SELECTOR, ".table.article-table.table-striped")
            listaPrezzi = tabella.find_elements(By.CSS_SELECTOR, 
                "div.price-container.d-none.d-md-flex.justify-content-end span.color-primary.small.text-end.text-nowrap.fw-bold")
            
            if listaPrezzi:
                return float(listaPrezzi[0].text.replace("€", "").replace(",", ".").strip())
            else:
                print("Nessun prezzo trovato.")
                return None
        except TimeoutException:
            print("Tempo di attesa scaduto per caricare l'elemento.")
            return None
        except NoSuchElementException as e:
            print(f"Elemento richiesto non trovato sulla pagina: {e}")
            return None
        except Exception as e:
            print(f"Errore durante la validazione dell'URL: {e}")
            return None

    def quit(self):
        """Chiude il driver e rilascia le risorse."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            SeleniumService._instance = None