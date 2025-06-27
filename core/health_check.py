from flask import Flask, jsonify
import os
import threading
import time

app = Flask(__name__)

@app.route('/health')
def health_check():
    """
    Endpoint de health check para Railway.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'sorte-ai',
        'timestamp': time.time(),
        'components': {
            'interpreter': 'active',
            'telegram_bot': 'active',
            'local_llm': 'active'
        }
    })

@app.route('/')
def root():
    """
    Endpoint raiz.
    """
    return jsonify({
        'message': 'Sorte AI - Sistema Autônomo de Trading',
        'status': 'operational',
        'version': '1.0.0'
    })

def start_health_server():
    """
    Inicia servidor de health check em thread separada.
    """
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    start_health_server()

