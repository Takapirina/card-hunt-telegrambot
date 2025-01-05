import os
import json
from datetime import datetime

from service.dropBoxService import upload_wishlist_user_single

class WishList:
    def __init__(self, id_utente):
        self.id_utente = id_utente
        self.file_path = os.path.join("wishlistUtenti", f"wishlist_{id_utente}.json")
        self._ensure_file_exists()
        self.contatore_id = self._load_wishlist().get("contatore_id", 1)

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w") as file:
                json.dump({"id_utente": self.id_utente, "carte": [], "contatore_id": 1}, file, indent=4)

            upload_wishlist_user_single(self.file_path)

    def add_carta(self, carta):
        data = self._load_wishlist()
        carta.id_carta = data["contatore_id"] 
        data["contatore_id"] += 1
        data["carte"].append(carta.to_dict())
        self._save_wishlist(data)
        upload_wishlist_user_single(self.file_path)

    def remove_carta(self, id_carta):
        data = self._load_wishlist()
        data["carte"] = [carta for carta in data["carte"] if carta["id_carta"] != id_carta]
        self._save_wishlist(data)

    def update_prezzo_carta_by_id(self, id_carta, nuovo_prezzo):
        data = self._load_wishlist()
        carta_trovata = False
        data_cur = datetime.fromisoformat(datetime.now().isoformat())

        for carta in data["carte"]:
            if carta["id_carta"] == id_carta:
                    carta["prezzo_attuale"] = nuovo_prezzo
                    carta_trovata = True

                    data_inserimento = datetime.fromisoformat(carta["data_inserimento"])
                    dif = data_cur - data_inserimento

                    if dif.days % 7 == 0:
                        carta["prezzo_settimanale"] = nuovo_prezzo

                    if dif.days % 30 == 0:
                        carta["prezzi_mensili"].append(nuovo_prezzo)
        
        if carta_trovata:
            self._save_wishlist(data)
        else:
            print(f"Carta con Id {id_carta} non trovata.")

    def visualizza_lista(self):
        data = self._load_wishlist()
        carte = data.get("carte", [])
        if not carte:
            print("La wishlist è vuota.")
        for carta in carte:
            print(f"Id: {carta['id']}, Carta: {carta['nome_carta']}, "
                  f"Brand: {carta['brand_carta']}, Espansione: {carta['espansione_carta']}, "
                  f"URL: {carta['url_carta']}")

    def _load_wishlist(self):
        """Carica i dati della wishlist dal file JSON."""
        if not os.path.exists(self.file_path):
            return {"id_utente": self.id_utente, "carte": [], "contatore_id": 1}
        try:
            with open(self.file_path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"_load_wishlist | Errore nella lettura del file JSON corrotto: {self.file_path}")
        return {"id_utente": self.id_utente, "carte": [], "contatore_id": 1}

    def _save_wishlist(self, data):
        """Salva i dati della wishlist nel file JSON."""
        try:
            with open(self.file_path, "w") as file:
                json.dump(data, file, indent=4)

            upload_wishlist_user_single(self.file_path)
        except Exception as e:
            print(f"_save_wishlist | Errore durante il salvataggio del file: {e}")