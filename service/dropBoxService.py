import dropbox
import os
import json
from dotenv import load_dotenv

load_dotenv()
DROPBOX_ACCESS_TOKEN = os.getenv("DROP_BOX_TOKEN")

# Inizializza il client Dropbox (singleton per evitare di reinizializzarlo ogni volta)
DBX = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

def download_user_json_file():
    local_path = os.path.join("user.json")
    dropbox_path = "/card-hunt-telegrambot/user.json"

    try:
        metdata, res = DBX.files_download(path=dropbox_path)
        with open(local_path,"wb") as f:
            f.write(res.content)
        print("file user.json scaricato correttamente da dropbox")
    except dropbox.exceptions.ApiError as e:
        print(f"Errore durante il download: {e}")

def upload_user_json_file():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    local_path = os.path.join(base_dir, "user.json")
    dropbox_path = "/card-hunt-telegrambot/user.json"

    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Il file '{local_path}' non esiste.")
    try:
        with open(local_path, "rb") as f:
            data = f.read()
            DBX.files_upload(data, dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
        print("File user.json caricato correttamente su Dropbox.")
    except Exception as e:
        print(f"Errore durante l'upload del file: {e}")

def download_brand_json_file():
    local_path = os.path.join("brand.json")
    dropbox_path = "/card-hunt-telegrambot/brand.json"

    try:
        metdata, res = DBX.files_download(path=dropbox_path)
        with open(local_path,"wb") as f:
            f.write(res.content)
        print("file brand.json scaricato correttamente da dropbox")
    except dropbox.exceptions.ApiError as e:
        print(f"Errore durante il download: {e}")

def upload_brand_json_file():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    local_path = os.path.join(base_dir, "brand.json")
    dropbox_path = "/card-hunt-telegrambot/brand.json"

    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Il file '{local_path}' non esiste.")
    try:
        with open(local_path, "rb") as f:
            data = f.read()
            DBX.files_upload(data, dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
        print("File brand.json caricato correttamente su Dropbox.")
    except Exception as e:
        print(f"Errore durante l'upload del file: {e}")

def downloads_wishlist_user():
    with open("user.json", "r") as f:
        user_data = json.load(f)
        print(f"recupero lista utenti: {user_data}")

    local_path = os.path.join("wishlistUtenti/")
    dropbox_path = "/card-hunt-telegrambot/wishlistUtenti/"

    for user_id, user_info in user_data.items():  # user_data.items() restituisce (ID, dati dell'utente)
        local_path_relative = os.path.join(local_path, user_info["wishlist"])  # Usa user_info per accedere al dizionario
        dropbox_path_relative = os.path.join(dropbox_path, user_info["wishlist"])

        try:
            metadata, res = DBX.files_download(path=dropbox_path_relative)
            with open(local_path_relative, "wb") as f:
                f.write(res.content)
            print(f"file {user_info['wishlist']} scaricato correttamente da Dropbox")
        except dropbox.exceptions.ApiError as e:
            print(f"Errore durante il download: {e}")

def upload_wishlist_user_single(name_file):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    local_path = os.path.join(base_dir, f"{name_file}")
    dropbox_path = f"/card-hunt-telegrambot/{name_file}"

    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Il file '{local_path}' non esiste.")
    try:
        with open(local_path, "rb") as f:
            data = f.read()
            DBX.files_upload(data, dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
        print(f"File {name_file} caricato correttamente su Dropbox.")
    except Exception as e:
        print(f"Errore durante l'upload del file: {e}")