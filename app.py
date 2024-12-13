from flask import Flask, request, jsonify
import threading
import time
import requests

app = Flask(__name__)

# Funkcja pingująca Render, aby utrzymać usługę aktywną
def ping():
    url = "https://tv-capital-webhook.onrender.com/"  # Upewnij się, że URL kończy się '/'
    while True:
        try:
            response = requests.get(url)
            print(f"Ping sent to {url}, status code: {response.status_code}")
        except Exception as e:
            print(f"Error pinging {url}: {e}")
        time.sleep(30)  # Ping co 30 sekund

# Uruchomienie funkcji ping w tle
thread = threading.Thread(target=ping)
thread.daemon = True  # Wątek zakończy się automatycznie, gdy aplikacja się zamknie
thread.start()

# Endpoint do obsługi zamówień z TradingView
@app.route('/api/v1/orders', methods=['POST'])
def handle_order():
    data = request.json
    print("Otrzymane dane z TradingView:", data)
    return jsonify({"status": "success", "received_data": data}), 200

# Endpoint do obsługi pingowania
@app.route("/", methods=["GET"])
def home():
    return "Service is running!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
