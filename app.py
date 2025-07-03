from flask import Flask, request

app = Flask(__name__)

@app.route("/trackingmore/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Evento recibido de TrackingMore:")
    print(data)
    return "OK", 200
