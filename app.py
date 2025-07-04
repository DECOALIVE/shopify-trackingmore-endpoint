from flask import Flask, request
import os
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()  # Esto es útil para entorno local con .env

app = Flask(__name__)

# Mapeo de estados TrackingMore → Amazon SP‑API
STATUS_MAP = {
    'inforeceived': 'InfoReceived',
    'transit': 'InTransit',
    'pickup': 'OutForDelivery',
    'delivered': 'Delivered',
    'exception': 'Exception',
    'pending': 'ReadyForPickup'
}

# Función para refrescar token de Amazon
def refresh_amazon_token():
    client_id = os.getenv("AMAZON_CLIENT_ID")
    client_secret = os.getenv("AMAZON_CLIENT_SECRET")
    refresh_token = os.getenv("AMAZON_REFRESH_TOKEN")
    lwa_endpoint = "https://api.amazon.com/auth/o2/token"

    try:
        resp = requests.post(
            lwa_endpoint,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret
            }
        )
        resp.raise_for_status()
        token = resp.json().get("access_token")
        print("🔑 Token de acceso de Amazon renovado.")
        return token
    except Exception as ex:
        print("❌ Error refrescando token de Amazon:", str(ex))
        return None

# Simulación de llamada real a SP‑API
def send_to_amazon(payload):
    print("📤 Simulación de envío a Amazon:")
    print(json.dumps(payload, indent=2))

    # Sólo descomentar cuando tengas los tokens y permisos
    # access_token = refresh_amazon_token()
    # if access_token:
    #     response = requests.post(
    #         "https://sellingpartnerapi-eu.amazon.com/vendor/directFulfillment/shipping/v1/shipmentStatusUpdates",
    #         headers={
    #             "Authorization": f"Bearer {access_token}",
    #             "x-amz-access-token": access_token,
    #             "Content-Type": "application/json"
    #         },
    #         json={"shipmentStatusUpdates": [payload]}
    #     )
    #     print("🛰️ Respuesta API Amazon:", response.status_code, response.text)
    # else:
    #     print("⚠️ No se envió a Amazon por falta de token.")

# Crea payload según formato SP‑API
def crear_payload_amazon(tracking_data):
    status_raw = tracking_data.get("delivery_status", "").lower()
    status = STATUS_MAP.get(status_raw, "InTransit")
timestamp = tracking_data.get("latest_checkpoint_time") or datetime.now(timezone.utc).isoformat()

    return {
        "trackingNumber": tracking_data.get("tracking_number"),
        "eventCode": status,
        "eventTime": timestamp,
        "location": {"countryCode": "ES"}
    }

# Webhook de TrackingMore
@app.route("/trackingmore/webhook", methods=["POST"])
def trackingmore_webhook():
    data = request.get_json(force=True)
    print("🔔 Evento recibido del webhook:")
    print(json.dumps(data, indent=2))

    if data and "data" in data:
        tracking_data = data["data"]
        amazon_payload = crear_payload_amazon(tracking_data)
        send_to_amazon(amazon_payload)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
