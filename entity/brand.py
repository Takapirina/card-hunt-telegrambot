from abc import ABC, abstractmethod
from enum import Enum

import json
import uuid

from service.dropBoxService import upload_brand_json_file

class Brand(Enum):
    POKEMON = "Pokemon"
    ONEPIECE = "OnePiece"

class GenerazionePokemon(Enum):
    PrimaGen = "Rosso & Verde"
    SecondaGen = "Oro & Argento"
    TerzaGen = "Rubino & Zaffiro"
    QuartaGen = "Diamante & Perla"
    QuintaGen = "Bianco & Nero"
    SestaGen = "X & Y"
    SettimanGen = "Sole & Luna"
    OttavaGen = "Spada & Scudo"
    NonaGen = "Scarlatto & Violetto"


class IBrand(ABC):
    def __init__(self, brand_nome):
        self.brand_nome = brand_nome

    @abstractmethod
    def add_espansione(self):
        pass

    @abstractmethod
    def remove_espansione(self):
        pass

    def get_brand_json(self):
        with open("brand.json", "r") as f:
            return json.load(f)
    


class BrandPokemon(IBrand):
    def __init__(self):
        super().__init__(Brand.POKEMON)

    def add_espansione(self,  generazione , nome_espansione, codice_espansione, isAsiatica):
        if self.controlla_espansione_esistente(nome_espansione, codice_espansione, isAsiatica):
            print(f"espansione esistente")
        else:
            self.id_espansione = uuid.uuid1()
            espansione = {
                "id_espansione": str(self.id_espansione),
                "nome_espansione": nome_espansione,
                "codice_espansione": codice_espansione
            }

            sezione = "Orientale" if isAsiatica else "occidentale"

            brand_data = self.get_brand_json()

            brand_key = self.brand_nome.value
            generazione_key = generazione

            if brand_key not in brand_data:
                brand_data[brand_key] = {}

            if generazione_key not in brand_data[brand_key]:
                brand_data[brand_key][generazione_key] = {"Orientale": [], "occidentale": []}

            brand_data[brand_key][generazione_key][sezione].append(espansione)

            with open("brand.json", "w") as f:
                json.dump(brand_data, f, indent=4)
            
            upload_brand_json_file()

    def remove_espansione(self, id_espansione, generazione, isAsiatica):
        try:
            brand_data = self.get_brand_json()
            sezione = "Orientale" if isAsiatica else "occidentale"

            if (self.brand_nome.value not in brand_data or
                generazione not in brand_data[self.brand_nome.value] or
                sezione not in brand_data[self.brand_nome.value][generazione]):
                return False

            espansioni = brand_data[self.brand_nome.value][generazione][sezione]
            espansione_da_rimuovere = next((e for e in espansioni if e["id_espansione"] == id_espansione), None)

            if espansione_da_rimuovere:
                espansioni.remove(espansione_da_rimuovere)
                print(f"Espansione con ID {id_espansione} rimossa.")
            else:
                print(f"Nessuna espansione trovata con ID {id_espansione}.")
                return False

            with open("brand.json", "w") as f:
                json.dump(brand_data, f, indent=4)

            upload_brand_json_file()
            
            return True

        except Exception as e:
            print(f"remove_espansione | Errore durante la rimozione dell'espansione: {e}")
            return False
        
    def controlla_espansione_esistente(self, nome_espansione, codice_espansione, isAsiatica):
        sezione = "Orientale" if isAsiatica else "occidentale"
        brand_data = self.get_brand_json()
        brand_key = self.brand_nome.value

        if brand_key not in brand_data:
            return False

        for generazione in brand_data[brand_key]:
            if sezione in brand_data[brand_key][generazione]:
                for espansione in brand_data[brand_key][generazione][sezione]:
                    if (espansione["nome_espansione"] == nome_espansione and
                            espansione["codice_espansione"] == codice_espansione):
                        return True