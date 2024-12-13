from flask import Flask, request, jsonify
import requests
import threading
import time

app = Flask(__name__)

# Capital.com API konfiguracja
CAPITAL_API_URL = "https://demo-api-capital.backend-capital.com/api/v1"
CAPITAL_API_KEY = "r37TqfQufR2ZvlTx"  # Wstaw swój klucz API
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {CAPITAL_API_KEY}"
}

# Funkcja do wysyłania zleceń do Capital.com
def send_order(action, ticker, quantity):
    direction = "BUY" if action.upper() == "BUY" else "SELL"
    order_data = {
        "marketId": ticker,
        "direction": direction,
        "orderType": "MARKET",
        "size": quantity,
        "timeInForce": "FILL_OR_KILL",
        "guaranteedStop": False
    }
    response = requests.post(f"{CAPITAL_API_URL}/positions", headers=HEADERS, json=order_data)
    if response.status_code == 200:
        return {"status": "success", "data": response.json()}
    else:
        return {"status": "error", "message": response.text}

# Funkcja do zamykania pozycji na podstawie TP i SL
def close_position(market_id):
    response = requests.delete(f"{CAPITAL_API_URL}/positions/{market_id}", headers=HEADERS)
    if response.status_code == 200:
        print(f"Position {market_id} closed successfully.")
    else:
        print(f"Failed to close position {market_id}: {response.text}")

# Monitorowanie pozycji w tle (TP i SL)
def monitor_positions():
    while True:
        try:
            response = requests.get(f"{CAPITAL_API_URL}/positions", headers=HEADERS)
            if response.status_code == 200:
                positions = response.json().get("positions", [])
                for position in positions:
                    market_id = position["marketId"]
                    direction = position["direction"]
                    entry_price = position["price"]
                    current_price = float(position["market"]["bid"])

                    # Definicja TP i SL
                    if direction == "BUY":
                        take_profit = entry_price * 1.03  # 3% TP
                        stop_loss = entry_price * 0.97  # 3% SL
                    else:  # SELL
                        take_profit = entry_price * 0.97  # 3% TP
                        stop_loss = entry_price * 1.03  # 3% SL

                    # Zamykanie pozycji na TP/SL
                    if (direction == "BUY" and current_price >= take_profit) or \
                       (direction == "BUY" and current_price <= stop_loss) or \
                       (direction == "SELL" and current_price <= take_profit) or \
                       (direction == "SELL" and current_price >= stop_loss):
                        close_position(market_id)
        except Exception as e:
            print(f"Error monitoring positions: {e}")
        time.sleep(10)  # Sprawdzaj co 10 sekund

# Funkcja pingująca Render, aby utrzymać serwis aktywny
def ping():
    url = "https://tv-capital-webhook.onrender.com/"
    while True:
        try:
            response = requests.get(url)
            print(f"Ping sent to {url}, status code: {response.status_code}")
        except Exception as e:
            print(f"Error pinging {url}: {e}")
        time.sleep(30)  # Ping co 30 sekund

# Endpoint webhooka do odbierania sygnałów z TradingView
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
    return "Service v2 is running and ready to receive signals!", 200

# Uruchomienie funkcji w tle
ping_thread = threading.Thread(target=ping)
ping_thread.daemon = True
ping_thread.start()

monitor_thread = threading.Thread(target=monitor_positions)
monitor_thread.daemon = True
monitor_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
