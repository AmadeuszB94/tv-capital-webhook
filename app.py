from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    data = request.json  # Odczytaj dane z TradingView
    print("Otrzymano dane:", data)

    if "action" not in data or "ticker" not in data or "quantity" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    action = "buy" if data["action"] == "BUY" else "sell"
    api_data = {
        "market": data["ticker"],
        "direction": action,
        "size": data["quantity"],
        "orderType": "MARKET"
    }

    headers = {
        "X-CAP-API-KEY": "r37TqfQufR2ZvlTx",
        "CST": "TWÓJ_CST",
        "X-SECURITY-TOKEN": "TWÓJ_SECURITY_TOKEN",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://demo-api-capital.backend-capital.com/api/v1/orders",
        json=api_data,
        headers=headers
    )

    if response.status_code == 201:
        return jsonify({"status": "Order placed successfully!"})
    else:
        return jsonify({"error": response.json()}), response.status_code

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
