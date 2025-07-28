from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>FoodXchange</h1><p>Health: <a href="/health/simple">/health/simple</a></p>'

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/health/simple')
def health_simple():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
