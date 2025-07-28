from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>FoodXchange API</h1><p>Health Status: <a href="/health/simple">/health/simple</a></p>'

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "foodxchange"})

@app.route('/health/simple')
def health_simple():
    return jsonify({"status": "ok"})

@app.route('/health/detailed')
def health_detailed():
    return jsonify({
        "status": "healthy",
        "service": "foodxchange",
        "version": "1.0.0",
        "environment": "production"
    })

@app.route('/api/health')
def api_health():
    return jsonify({"status": "healthy", "api": "v1"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
