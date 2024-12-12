from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Endpoint do sprawdzenia działania serwera
@app.route('/')
def home():
    return "Hello, Render! Your service is live."

# Endpoint do obsługi webhooka
@app.route('/webhook', methods=['POST'])
def webhook():
    # Pobierz dane JSON z żądania
    data = request.json
    print(f"Otrzymane dane: {data}")

    # Odczytaj dane z webhooka
    action = data.get('action')  # "BUY" lub "SELL"
    instrument = data.get('instrument')  # np. "EUR/USD"
    amount = data.get('amount', 1)  # Domyślna wielkość transakcji
    sl_pips = data.get('sl_pips', 10)  # Domyślny Stop Loss: 10 pipsów
    tp_pips = data.get('tp_pips', 50)  # Domyślny Take Profit: 50 pipsów

    # Wyślij zlecenie do Capital.com
    order_response = send_order_to_capital(action, instrument, amount, sl_pips, tp_pips)
    return jsonify({"status": "success", "response": order_response}), 200

# Funkcja pomocnicza do wysyłania zleceń do Capital.com
def send_order_to_capital(action, instrument, amount, sl_pips, tp_pips):
    API_KEY = r37TqfQufR2ZvlTx  # Wprowadź swój klucz API z Capital.com
    BASE_URL = "https://demo-api-capital.com"  # Zmieniaj na "https://api-capital.com" dla konta rzeczywistego

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Pobierz aktualną cenę instrumentu
    market_info = requests.get(f"{BASE_URL}/market/{instrument}", headers=headers).json()
    current_price = float(market_info['bidPrice'] if action == "SELL" else market_info['offerPrice'])

    # Oblicz wartości SL i TP w zależności od ceny
    pip_value = 0.0001  # Standardowy pip dla większości par walutowych
    if "JPY" in instrument:  # Dla par z JPY pip wynosi 0.01
        pip_value = 0.01

    sl_price = current_price - sl_pips * pip_value if action == "BUY" else current_price + sl_pips * pip_value
    tp_price = current_price + tp_pips * pip_value if action == "BUY" else current_price - tp_pips * pip_value

    # Zbuduj dane zlecenia
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
