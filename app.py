from flask import Flask, request, jsonify
import threading
import time
import requests
import datetime

app = Flask(__name__)

# Zapisujemy czas startu serwera
start_time = datetime.datetime.now()

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

# Endpoint główny - pokazuje czas działania serwera
@app.route("/", methods=["GET"])
def home():
    current_time = datetime.datetime.now()
    uptime = current_time - start_time
    return f"""
    <h1>Service is running!</h1>
    <p>Server started at: {start_time}</p>
    <p>Uptime: {uptime}</p>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
