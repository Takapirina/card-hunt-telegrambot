from abc import ABC, abstractmethod

from enum import Enum
from datetime import datetime

from service.seleniumService import SeleniumService

#vale in quasi tutti i casi tranne alcuni girda teracrystal festival ex
class Versione(Enum):
    REGULAR = "V1"
    ARTRARE = "V2"
    FULLART = "V2"
    ALTART = "V3"
    GOLD = "V4"
    PROMO = "None"
    NESSUNA = "None"

class LinguaOccidentale(Enum):
    INGLESE = 1
    FRANCESE = 2
    TEDESCO = 3
    SPAGNOLO = 4
    ITALIANO = 5
    PORTOGHESE = 8

class LinguaOrientale(Enum):
    CINESE = 6
    GIAPPONESE = 7
    COREANO = 10
    TAIWANESE = 11

class Condizione(Enum):
    MINT = 1
    NEAR_MINT = 2
    EXCELLENT = 3
    GOOD = 4
    LIGHT_PLAYED = 5
    PLAYED = 6
    POOR = "None"


class TipoVenditore(Enum):
    PRIVATO = 0
    PROFESSIONALE = 1
    POWERSELLER = 2
    INDIFFERENTE = "None"

class ICard(ABC):
    def __init__(self, nome_personalizzato):
        self.nome_personalizzato = nome_personalizzato
        self.id_carta = None

        self.data_inserimento = datetime.now()
        self.prezzo_iniziale = None #prezzo che viene assegnato qaundo viene fatto il primo scraping
        self.prezzo_attuale = None #prezzo corrente o ultimo scraping fatto
        self.prezzo_settimanale = None
        self.prezzi_mensili = [] #prezzo salvato dell'ultimo mese

    @abstractmethod
    def genera_url(self):
        pass

    @abstractmethod
    def to_dict(self):
        pass

class CardPokemon(ICard):
    def __init__(self, nome_personalizzato, nome_carta,
                 espansione_nome, codice_espansione, 
                 versione_card, numero_carta,
                 isAsiatica, lingua_carta,
                 condizione_carta, tipo_venditore):
        super().__init__(nome_personalizzato)
        self.nome_carta = nome_carta
        self.espansione_nome = espansione_nome
        self.codice_espansione = codice_espansione
        self.versione_card = versione_card
        self.numero_carta = numero_carta

        self.lingua_carta = lingua_carta
        self.isAsiatica = isAsiatica #per determinare la lingua con la quale si sta cercando se asia o occidente
        self.condizione_carta = condizione_carta
        self.tipo_venditore = tipo_venditore

        self.url_card = self.genera_url()

    def genera_url(self):

        url = f"https://www.cardmarket.com/it/Pokemon/Products/Singles/{self.espansione_nome}/{self.nome_carta}-"
        if self.versione_card!= "None" : url += f"{self.versione_card}-"
        url += f"{self.codice_espansione}{self.numero_carta}"

        params = []
        if self.lingua_carta != "None":
            params.append(f"language={self.lingua_carta}")
        if self.condizione_carta != "None":
            params.append(f"minCondition={self.condizione_carta}")
        if self.tipo_venditore != "None":
            params.append(f"sellerType={self.tipo_venditore}")
        if params:
            url += '?' + '&'.join(params)

        try:
            selenium = SeleniumService()
            print(f"card entity | nel blocco try prima di validification url card da verificare: {url}")
            valid_url = selenium.validification(url)
            if valid_url is not None:
                self.prezzo_iniziale = valid_url
                self.prezzo_attuale = self.prezzo_iniziale
                self.prezzo_settimanale = self.prezzo_iniziale
                self.prezzi_mensili.append(self.prezzo_iniziale)
                return url
            else:
                return None
        finally:
            selenium.quit()
    
    def to_dict(self):
        return {
            "id_carta" : self.id_carta,
            "nome_personalizzato" : self.nome_personalizzato,
            "nome_carta": self.nome_carta,
            "espansione_nome": self.espansione_nome,
            "codice_espansione": self.codice_espansione,
            "versione_card": self.versione_card,
            "numero_carta": self.numero_carta,
            "lingua_carta": self.lingua_carta if self.lingua_carta else None,
            "isAsiatica": self.isAsiatica,
            "condizione_carta": self.condizione_carta if self.condizione_carta else None,
            "tipo_venditore": self.tipo_venditore if self.tipo_venditore else None,
            "url_card": self.url_card,
            "data_inserimento": self.data_inserimento.isoformat(),
            "prezzo_iniziale": self.prezzo_iniziale,
            "prezzo_attuale" : self.prezzo_attuale,
            "prezzo_settimanale" : self.prezzo_settimanale,
            "prezzi_mensili" : self.prezzi_mensili
        }