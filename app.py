from flask import Flask, request
import os
import json
import requests

app = Flask(__name__)

# Mapeo de estados TrackingMore a Amazon
STATUS_MAP = {
    'inforeceived': 'InfoReceived',
    'transit': 'InTransit',
    'pickup': 'OutForDelivery',
    'delivered': 'Delivered',
    'exception': 'Exception',
    'pending': 'ReadyForPickup'
}

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

        # Traducir a estado Amazon
        amazon_status = STATUS_MAP.get(delivery_status.lower(), "InTransit")

        # Crear payload para Amazon Vendor
        amazon_payload = {
            "shipmentStatusUpdates": [
                {
                    "trackingNumber": tracking_number,
                    "eventCode": amazon_status,
                    "eventTime": event_time or "2025-01-01T00:00:00Z",  # Valor por defecto
                    "location": {
                        "countryCode": "ES"
                    }
                }
            ]
        }

        print("📦 Payload preparado para Amazon Vendor:")
        print(json.dumps(amazon_payload, indent=2))

        # 🔒 COMENTADO hasta tener credenciales Amazon
        # response = requests.post(
        #     "https://sellingpartnerapi-eu.amazon.com/vendor/directFulfillment/shipping/v1/shipmentStatusUpdates",
        #     headers={
        #         "Authorization": "Bearer <ACCESS_TOKEN>",
        #         "x-amz-access-token": "<REFRESHED_ACCESS_TOKEN>",
        #         "Content-Type": "application/json"
        #     },
        #     json=amazon_payload
        # )
        # print("🛰️ Respuesta de Amazon:", response.status_code, response.text)

        return "Webhook recibido y procesado", 200

    except Exception as e:
        print("❌ Error al procesar el webhook:", str(e))
        return "Error", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
