from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/v1/orders', methods=['POST'])
def handle_order():
    data = request.json
    print("Otrzymane dane z TradingView:", data)
    return jsonify({"status": "success", "received_data": data}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
