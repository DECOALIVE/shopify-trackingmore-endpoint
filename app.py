from flask import Flask, request
import os
import json

app = Flask(__name__)

@app.route("/trackingmore/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("✅ Webhook recibido:")
        print(json.dumps(data, indent=2))  # Esto mostrará el JSON bonito en los logs
        return "Webhook recibido", 200
    except Exception as e:
        print("❌ Error al procesar el webhook:", str(e))
        return "Error", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
