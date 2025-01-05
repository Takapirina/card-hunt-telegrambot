from flask import Flask, request

app = Flask(__name__)

@app.route("/callback", methods=["GET"])
def handle_callback():
    code = request.args.get("code")
    if code:
        print(f"Codice ricevuto: {code}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)