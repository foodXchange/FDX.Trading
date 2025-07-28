from flask import Flask, jsonify, Response, request
from datetime import datetime
import os

app = Flask(__name__)

# Basic health endpoint that handles both GET and HEAD
@app.route('/health', methods=['GET', 'HEAD'])
def health():
    if request.method == 'HEAD':
        return Response(status=200)
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# Root endpoint
@app.route('/', methods=['GET', 'HEAD'])
def root():
    if request.method == 'HEAD':
        return Response(status=200)
    return jsonify({
        'message': 'FoodXchange API',
        'version': '1.0.0',
        'status': 'operational',
        'timestamp': datetime.now().isoformat()
    })

# Alternative health endpoints Azure might check
@app.route('/health/simple', methods=['GET', 'HEAD'])
def health_simple():
    if request.method == 'HEAD':
        return Response(status=200)
    return jsonify({'status': 'ok'})

@app.route('/health/detailed', methods=['GET', 'HEAD'])
def health_detailed():
    if request.method == 'HEAD':
        return Response(status=200)
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'foodxchange',
        'version': '1.0.0'
    })

# Azure health probe endpoint
@app.route('/robots933456.txt', methods=['GET', 'HEAD'])
def robots():
    if request.method == 'HEAD':
        return Response(status=200)
    return Response('', status=200)

# Standard favicon endpoint
@app.route('/favicon.ico')
def favicon():
    return Response('', status=204)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)