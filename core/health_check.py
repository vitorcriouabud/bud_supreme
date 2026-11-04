"""Saúde HTTP: não confundir processo ativo com IA/trading validados."""
from flask import Flask, jsonify
import os
import time

app = Flask(__name__)


@app.route("/health")
def health_check():
    return jsonify({
        "status": "alive", "service": "bud-supreme",
        "timestamp": time.time(),
        "checks": {"http": "alive", "llm": "not_checked",
                   "telegram": "not_checked", "mt5_trading": "disabled"},
    })


@app.route("/")
def root():
    return jsonify({
        "service": "bud-supreme", "status": "alive",
        "trading_real": "disabled", "code_apply_mode": "review_only",
    })


def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    start_health_server()
