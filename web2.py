import os
import uuid
import requests
import time
from flask import Flask, redirect, request, jsonify
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

CLIENT_ID = os.getenv("APP_KEY")
CLIENT_SECRET = os.getenv("APP_KEY_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URL")

def get_authorization_url(client_id, redirect_uri, state):
    url = f"https://www.dropbox.com/oauth2/authorize?client_id={client_id}&response_type=code&token_access_type=offline&state={state}&redirect_uri={redirect_uri}"
    return url

def get_tokens(auth_code, client_id, client_secret, redirect_uri):
    response = requests.post(
        "https://api.dropbox.com/oauth2/token",
        data={
            "code": auth_code,
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        }
    )
    if response.status_code == 200:
        tokens = response.json()
        return tokens['access_token'], tokens['refresh_token']
    else:
        print(f"Error getting tokens: {response.text}")
        return None, None

def refresh_access_token(refresh_token, client_id, client_secret):
    response = requests.post(
        "https://api.dropbox.com/oauth2/token",
        data={
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    )
    print("Request payload:", {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret[:4] + "****"
    })
    print("Response status:", response.status_code)
    print("Response body:", response.text)

    if response.status_code == 200:
        tokens = response.json()
        return tokens['access_token']
    else:
        print(f"Error refreshing token: {response.text}")
        return None


def update_access_token(access_token):
    HEROKU_API_KEY = os.getenv("HEROKU_API_KEY")
    APP_NAME = os.getenv("APP_NAME")
    headers = {
        "Authorization": f"Bearer {HEROKU_API_KEY}",
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    data = {
        "DROP_BOX_TOKEN": access_token
    }
    heroku_url = f"https://api.heroku.com/apps/{APP_NAME}/config-vars"
    put_response = requests.patch(heroku_url, json=data, headers=headers)
    if put_response.status_code == 200:
        print("Token aggiornato su Heroku!")
    else:
        print("Errore nell'aggiornamento del token su Heroku")


@app.route('/')
def home():
    state = str(uuid.uuid4()) 
    auth_url = get_authorization_url(CLIENT_ID, REDIRECT_URI, state)
    return f'<a href="{auth_url}">Autorizza l\'app</a>'

@app.route('/callback')
def callback():
    auth_code = request.args.get('code')
    state = request.args.get('state')
    
    if not auth_code:
        return "Errore: nessun codice di autorizzazione ricevuto", 400
    
    access_token, refresh_token = get_tokens(auth_code, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    
    if access_token and refresh_token:
        os.environ["DROP_BOX_TOKEN"] = access_token
        os.environ["DROP_BOX_REFRESH_TOKEN"] = refresh_token
        return f"Accesso completato! Access Token: {access_token}<br>Refresh Token: {refresh_token}"
    else:
        return "Errore nell'ottenere i token", 400

# Funzione per l'aggiornamento periodico dei token
def periodic_update():
    refresh_token = os.getenv("DROP_BOX_REFRESH_TOKEN")
    if refresh_token:
        new_access_token = refresh_access_token(refresh_token, CLIENT_ID, CLIENT_SECRET)
        if new_access_token:
            update_access_token(new_access_token)
        else:
            print("Errore nel rinnovare l'access token.")
    else:
        print("Errore: non è stato trovato un refresh token.")

# Configura e avvia il task scheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(periodic_update, 'interval', hours=3)  # Ogni 3 ore
    scheduler.start()

if __name__ == "__main__":
    start_scheduler()  # Avvia il task scheduler
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)