from flask import Flask, request
import os
import json
import requests

app = Flask(__name__)

# Mapeo de estados TrackingMore a Amazon Vendor
STATUS_MAP = {
    'inforeceived': 'InfoReceived',
    'transit': 'InTransit',
    'pickup': 'OutForDelivery',
    'delivered': 'Delivered',
    'exception': 'Exception',
    'pending': 'ReadyForPickup'
}

# 🔐 Función para refrescar el token de acceso de Amazon
def refresh_amazon_token():
    client_id = "<TU_CLIENT_ID>"
    client_secret = "<TU_CLIENT_SECRET>"
    refresh_token = "<TU_REFRESH_TOKEN>"
    lwa_endpoint = "https://api.amazon.com/auth/o2/token"

    try:
        response = requests.post(
            lwa_endpoint,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret
            }
        )
        response.raise_for_status()
        access_token = response.json().get("access_token")
        print("🔑 Token de acceso actualizado.")
        return access_token
    except Exception as e:
        print("❌ Error al refrescar el token de Amazon:", str(e))
        return None

# 🎯 Webhook de TrackingMore
@app.route("/trackingmore/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("✅ Webhook recibido:")
        print(json.dumps(data, indent=2))

        # Extraer datos clave
        tracking = data.get("data", {})
        tracking_number = tracking.get("tracking_number")
        delivery_status = tracking.get("delivery_status")
        event_time = tracking.get("latest_checkpoint_time")

        # Traducir estado a Amazon Vendor
        amazon_status = STATUS_MAP.get(delivery_status.lower(), "InTransit")

        # Crear payload para Amazon
        amazon_payload = {
            "shipmentStatusUpdates": [
                {
                    "trackingNumber": tracking_number,
                    "eventCode": amazon_status,
                    "eventTime": event_time or "2025-01-01T00:00:00Z",
                    "location": {
                        "countryCode": "ES"
                    }
                }
            ]
        }

        print("📦 Payload preparado para Amazon Vendor:")
        print(json.dumps(amazon_payload, indent=2))

        # 🚀 Enviar a Amazon (descomenta cuando tengas las credenciales)
        # access_token = refresh_amazon_token()
        # if access_token:
        #     response = requests.post(
        #         "https://sellingpartnerapi-eu.amazon.com/vendor/directFulfillment/shipping/v1/shipmentStatusUpdates",
        #         headers={
        #             "Authorization": f"Bearer {access_token}",
        #             "x-amz-access-token": access_token,
        #             "Content-Type": "application/json"
        #         },
        #         json=amazon_payload
        #     )
        #     print("🛰️ Respuesta de Amazon:", response.status_code, response.text)
        # else:
        #     print("⚠️ No se pudo enviar a Amazon por falta de token.")

        return "Webhook recibido y procesado", 200

    except Exception as e:
        print("❌ Error al procesar el webhook:", str(e))
        return "Error", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
