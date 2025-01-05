import json
import os
from dataclasses import dataclass, field
from entity.wishlist import WishList

from service.dropBoxService import upload_user_json_file

@dataclass
class Utente:
    id_utente: int
    nome_utente: str
    chat_id: int
    wishlist: WishList = field(init=False)

    def __post_init__(self):
        self.wishlist = WishList(self.id_utente)
        self.aggiungi_utente_json()

    def aggiungi_utente_json(self):

        utente = {
            "id_utente": self.id_utente,
            "chat_id": self.chat_id,
            "nome_utente": self.nome_utente,
            "wishlist": f"wishlist_{self.id_utente}.json"
        }

        if self.controllo_utente_presente():
            print("Utente già presente.")
        else:
            utenti_data = self.dammi_utenti()

            utenti_data[str(self.id_utente)] = utente

            with open("user.json", "w") as f:
                json.dump(utenti_data, f, indent=4)
                print("Utente salvato correttamente!")

        upload_user_json_file()


    def controllo_utente_presente(self):
        utenti_data = self.dammi_utenti()

        return str(self.id_utente) in utenti_data

    def dammi_utenti(self):
        try:
            with open("user.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def aggiungi_carta(self, carta):
        self.wishlist.add_carta(carta)

    def rimuovi_carta(self, id_carta):
        self.wishlist.remove_carta(id_carta)

    def aggiorna_carta_prezzo(self, id_carta, prezzo_attuale):
        self.wishlist.update_prezzo_carta_by_id(id_carta,prezzo_attuale)

    def get_carta(self, id_carta):
        wishlist = self.get_wishList()['carte']
        return next((carta for carta in wishlist if carta['id_carta'] == id_carta), None)

    def get_wishList(self):
        return self.wishlist._load_wishlist()

    @staticmethod
    def from_json(data: dict) -> 'Utente':
        return Utente(id_utente=data["id_utente"], nome_utente=data["nome_utente"], chat_id=data["chat_id"])

def carica_utente(id_utente: int) -> Utente:
    try:
        with open("user.json", "r") as f:
            utenti_data = json.load(f)

        if str(id_utente) in utenti_data:
            utente_data = utenti_data[str(id_utente)]
            return Utente.from_json(utente_data)
        else:
            print(f"Utente con ID {id_utente} non trovato.")
            return None
    except FileNotFoundError:
        print("Il file user.json non esiste.")
        return None
