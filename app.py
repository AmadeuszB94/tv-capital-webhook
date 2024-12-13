from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Dane API Capital.com
API_KEY = "r37TqfQufR2ZvlTx"
CST = "2V0KV2TXXlA77IAeg5OnexJo"
SECURITY_TOKEN = "Gmadg8XUfXSS6pHzgW8lohxlbLP5GqF"

# Endpoint do wysyłania żądań do Capital.com
CAPITAL_API_URL = "https://demo-api-capital.backend-capital.com/api/v1/positions"

@app.route('/api/v1/orders', methods=['POST'])
def handle_order():
    """
    Odbiera dane z TradingView i przesyła je do Capital.com.
    """
    try:
        # Pobranie danych z webhooka TradingView
        data = request.json
        print("Otrzymane dane z TradingView:", data)

        # Przygotowanie danych do API Capital.com
        payload = {
            "direction": data.get("action"),  # BUY lub SELL
            "epic": data.get("ticker"),      # np. AAPL
            "size": data.get("quantity")     # np. 1
        }

        # Walidacja danych wejściowych
        if not payload["direction"] or not payload["epic"] or not payload["size"]:
            return jsonify({"status": "error", "message": "Nieprawidłowe dane wejściowe"}), 400

        # Przygotowanie nagłówków do żądania
        headers = {
            "X-CAP-API-KEY": API_KEY,
            "CST": CST,
            "X-SECURITY-TOKEN": SECURITY_TOKEN,
            "Content-Type": "application/json"
        }

        # Wysłanie żądania do API Capital.com
        response = requests.post(CAPITAL_API_URL, json=payload, headers=headers)

        # Logowanie odpowiedzi
        print("Odpowiedź z Capital.com:", response.status_code, response.text)

        # Zwrócenie odpowiedzi
        if response.status_code == 200:
            return jsonify({"status": "success", "capital_response": response.json()}), 200
        else:
            return jsonify({"status": "error", "capital_error": response.text}), response.status_code

    except Exception as e:
        print("Błąd:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
