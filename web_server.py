import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    if not code:
        return "Code not provided", 400
    return f"Received code: {code}", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)