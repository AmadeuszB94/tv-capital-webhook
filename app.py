from flask import Flask, request, jsonify
import requests
import threading
import time

app = Flask(__name__)

# Capital.com API konfiguracja
CAPITAL_API_URL = "https://demo-api-capital.backend-capital.com/api/v1"
CAPITAL_API_KEY = "YOUR_CAPITAL_API_KEY"  # Wstaw swój klucz API
ACCOUNT_ID = "YOUR_ACCOUNT_ID"  # Wstaw swój ID konta

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {CAPITAL_API_KEY}"
}

# Funkcja do wysyłania zleceń do Capital.com
def send_order(action, ticker, quantity):
    if action == "BUY":
        direction = "BUY"
    elif action == "SELL":
        direction = "SELL"
    else:
        return {"status": "error", "message": "Invalid action"}

    order_data = {
        "marketId": ticker,
        "direction": direction,
        "orderType": "MARKET",
        "size": quantity,
        "timeInForce": "FILL_OR_KILL",
        "guaranteedStop": False
    }

    response = requests.post(
        f"{CAPITAL_API_URL}/positions",
        headers=HEADERS,
        json=order_data
    )

    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {"status": "error", "message": response.text}

# Endpoint do odbierania sygnałów z TradingView
@app.route('/api/v1/orders', methods=['POST'])
def handle_order():
    data = request.json
    action = data.get("action")
    ticker = data.get("ticker")
    quantity = data.get("quantity")

    if not action or not ticker or not quantity:
        return jsonify({"status": "error", "message": "Invalid payload"}), 400

    result = send_order(action, ticker, quantity)
    return jsonify(result)

# Endpoint testowy
@app.route("/", methods=["GET"])
def home():
    return "Service is running and ready to receive signals!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
