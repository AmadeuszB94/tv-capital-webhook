@app.route('/')
def home():
    return "Hello, Render! Your service is live."

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Nowy endpoint dla strony głównej
@app.route('/')
def home():
    return "Hello, Render! Your service is live."

# Oryginalny endpoint webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Otrzymane dane: {data}")

    # Dane do zlecenia
    action = data.get('action')  # "BUY" lub "SELL"
    instrument = data.get('instrument')  # np. "EUR/USD"
    amount = data.get('amount', 1)  # Domyślna wielkość transakcji
    sl_pips = data.get('sl_pips', 10)  # Stop Loss: domyślnie 10 pipsów
    tp_pips = data.get('tp_pips', 50)  # Take Profit: domyślnie 50 pipsów

    # Złóż zlecenie (funkcja pomocnicza)
    order_response = send_order_to_capital(action, instrument, amount, sl_pips, tp_pips)
    return jsonify({"status": "success", "response": order_response}), 200

# Funkcja pomocnicza do wysyłania zleceń do Capital.com
def send_order_to_capital(action, instrument, amount, sl_pips, tp_pips):
    headers = {
        "Authorization": f"Bearer TWOJ_CAPITAL_API_KEY",  # Wstaw swój klucz API z Capital.com
        "Content-Type": "application/json"
    }

    # Oblicz poziomy SL i TP
    market_info = requests.get(f"https://demo-api-capital.com/market/{instrument}", headers=headers).json()
    current_price = float(market_info['bidPrice'] if action == "SELL" else market_info['offerPrice'])

    pip_value = 0.0001  # Standardowy pip dla par walutowych
    if "JPY" in instrument:  # Dla par z JPY pip to 0.01
        pip_value = 0.01

    sl_price = current_price - sl_pips * pip_value if action == "BUY" else current_price + sl_pips * pip_value
    tp_price = current_price + tp_pips * pip_value if action == "BUY" else current_price - tp_pips * pip_value

    # Tworzenie zlecenia
    order_data = {
        "market": instrument,
        "direction": action,
        "orderType": "MARKET",
        "quantity": amount,
        "stopLevel": round(sl_price, 5),
        "limitLevel": round(tp_price, 5)
    }

    response = requests.post("https://demo-api-capital.com/trading/positions", json=order_data, headers=headers)
    return response.json()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
