from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/trackingmore/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Evento recibido de TrackingMore:")
    print(data)
    return "OK", 200

# Este bloque garantiza que Flask escuche correctamente en Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
