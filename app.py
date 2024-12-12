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
    try:
        # Sprawdź, czy żądanie ma poprawny format JSON
        if request.method == 'POST':
            data = request.json
            print(f"Otrzymane dane: {data}")

            # Pobierz parametry z JSON
            action = data.get('action')  # "BUY" lub "SELL"
            instrument = data.get('instrument')  # np. "US Tech 100"
            amount = data.get('amount', 1)  # Domyślna wielkość transakcji
            sl_pips = data.get('sl_pips', 20)  # Stop Loss w punktach
            tp_pips = data.get('tp_pips', 100)  # Take Profit w punktach

            # Upewnij się, że wymagane dane istnieją
            if not action or not instrument:
                return jsonify({"error": "Missing required fields: action or instrument"}), 400

            # Wyślij zlecenie do Capital.com
            order_response = send_order_to_capital(action, instrument, amount, sl_pips, tp_pips)
            return jsonify({"status": "success", "response": order_response}), 200
        else:
            return jsonify({"error": "Method not allowed"}), 405
    except Exception as e:
        print(f"Błąd: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

# Funkcja pomocnicza do wysyłania zleceń do Capital.com
def send_order_to_capital(action, instrument, amount, sl_pips, tp_pips):
    API_KEY = "r37TqfQufR2ZvlTx"  # Twój klucz API
    BASE_URL = "https://demo-api-capital.com"  # Demo API; zmień na "https://api-capital.com" dla konta rzeczywistego

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Popraw nazwę instrumentu (zamiana spacji na podkreślenia)
    instrument_url = instrument.replace(" ", "_")  # Zamień spacje na podkreślenia

    # Pobierz aktualną cenę instrumentu
    market_info = requests.get(f"{BASE_URL}/market/{instrument_url}", headers=headers).json()
    current_price = float(market_info['bidPrice'] if action == "SELL" else market_info['offerPrice'])

    # Oblicz poziomy SL i TP
    # US Tech 100: SL i TP to liczba punktów od aktualnej ceny
    sl_price = current_price - sl_pips if action == "BUY" else current_price + sl_pips
    tp_price = current_price + tp_pips if action == "BUY" else current_price - tp_pips

    # Dane zlecenia
    order_data = {
        "market": instrument,
        "direction": action,
        "orderType": "MARKET",
        "quantity": amount,
        "stopLevel": round(sl_price, 2),  # 2 miejsca po przecinku dla indeksów
        "limitLevel": round(tp_price, 2)
    }

    # Wyślij zlecenie do Capital.com
    response = requests.post(f"{BASE_URL}/trading/positions", json=order_data, headers=headers)
    return response.json()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
