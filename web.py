from flask import Flask, request, redirect, jsonify
import requests
import os

app = Flask(__name__)

CLIENT_ID = os.getenv("APP_KEY")
CLIENT_SECRET = os.getenv("APP_KEY_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URL")

@app.route("/dropbox/login")
def dropbox_login():
    auth_url = (
        "https://www.dropbox.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(auth_url)

@app.route("/callback")
def dropbox_auth():
    auth_code = request.args.get("code")
    if not auth_code:
        return "Errore: Nessun codice di autorizzazione ricevuto.", 400

    token_url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        "code": auth_code,
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
    }
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()  # Controlla eventuali errori
        tokens = response.json()

        return jsonify(tokens)
    except requests.exceptions.RequestException as e:
        return f"Errore nella richiesta dei token: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)