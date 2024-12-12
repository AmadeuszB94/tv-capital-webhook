from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 1. Endpoint do sprawdzenia działania serwera
@app.route('/')
def home():
    return "Hello, Render! Your service is live."

# 2. Endpoint do obsługi webhooka
@app.route('/webhook', methods=['POST'])
def webhook():
    # Sprawdź, czy żądanie jest typu POST
    if request.method == 'POST':
        data = request.json  # Pobierz dane JSON z żądania
        print(f"Otrzymane dane z webhooka: {data}")
        return jsonify({"status": "success", "data": data}), 200
    else:
        return jsonify({"error": "Method not allowed"}), 405

        # Pobierz dane z JSON
        action = data.get('action')  # "BUY" lub "SELL"
        instrument = data.get('instrument')  # np. "EUR/USD"
        amount = data.get('amount', 1)  # Wielkość transakcji
        sl_pips = data.get('sl_pips', 10)  # Stop Loss w pipsach
        tp_pips = data.get('tp_pips', 50)  # Take Profit w pipsach

        # Wyślij zlecenie do Capital.com
        order_response = send_order_to_capital(action, instrument, amount, sl_pips, tp_pips)
        return jsonify({"status": "success", "response": order_response}), 200
    else:
        return jsonify({"error": "Method not allowed"}), 405

# 3. Funkcja pomocnicza do wysyłania zleceń do Capital.com
def send_order_to_capital(action, instrument, amount, sl_pips, tp_pips):
    # === MIEJSCE DO ZMIANY ===
    API_KEY = r37TqfQufR2ZvlTx  # Wstaw swój klucz API z Capital.com
    BASE_URL = "https://demo-api-capital.com"  # Zmieniaj na "https://api-capital.com" dla konta rzeczywistego

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Pobierz aktualną cenę instrumentu
    market_info = requests.get(f"{BASE_URL}/market/{instrument}", headers=headers).json()
    current_price = float(market_info['bidPrice'] if action == "SELL" else market_info['offerPrice'])

    # Oblicz poziomy SL i TP
    pip_value = 0.0001  # Standardowy pip dla par walutowych
    if "JPY" in instrument:  # Dla par z JPY pip wynosi 0.01
        pip_value = 0.01

    sl_price = current_price - sl_pips * pip_value if action == "BUY" else current_price + sl_pips * pip_value
    tp_price = current_price + tp_pips * pip_value if action == "BUY" else current_price - tp_pips * pip_value

    # Dane zlecenia
    order_data = {
        "market": instrument,
        "direction": action,
        "orderType": "MARKET",
        "quantity": amount,
        "stopLevel": round(sl_price, 5),
        "limitLevel": round(tp_price, 5)
    }

    # Wyślij zlecenie do Capital.com
    response = requests.post(f"{BASE_URL}/trading/positions", json=order_data, headers=headers)
    return response.json()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
