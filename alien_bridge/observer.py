"""Bud–ALIEN Observer v1: análise offline SOMENTE LEITURA.

Nenhum import de MT5, conexão de rede, login, ordem, saque ou autoedição.
Dados externos só entram por JSON local, sujeitos a validação explícita.
"""
from datetime import datetime, timezone
import json
import math
from pathlib import Path


class SnapshotError(ValueError):
    """Snapshot inválido: processamento interrompido sem executar ações."""


SCHEMA_VERSION = "alien-market-v1"
ALLOWED_TOP = frozenset({
    "schema_version", "source", "symbol", "timeframe",
    "captured_at", "spread", "bars",
})
ALLOWED_BAR = frozenset({"time", "open", "high", "low", "close", "volume"})
TIMEFRAMES = {"M1": 60, "M5": 300, "M15": 900, "H1": 3600}
SOURCES = frozenset({"synthetic", "historical", "demo"})
MAX_BYTES = 1024 * 1024
MAX_BARS = 2000


def _finite_number(value, label, *, minimum=0, strict=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SnapshotError("{} deve ser número".format(label))
    try:
        number = float(value)
    except (ValueError, OverflowError):
        raise SnapshotError("{} fora dos limites numéricos".format(label)) from None
    if not math.isfinite(number):
        raise SnapshotError("{} não pode ser NaN ou infinito".format(label))
    if (strict and number <= minimum) or (not strict and number < minimum):
        raise SnapshotError("{} fora da faixa permitida".format(label))
    return number


def _utc(value, label):
    if not isinstance(value, str):
        raise SnapshotError("{} deve ser string ISO-8601 com fuso".format(label))
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        raise SnapshotError("{} não é um timestamp válido".format(label)) from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SnapshotError("{} deve incluir fuso ou Z".format(label))
    return parsed.astimezone(timezone.utc)


def _strict_object(obj, keys, label):
    if not isinstance(obj, dict):
        raise SnapshotError("{} deve ser um objeto JSON".format(label))
    unexpected = set(obj) - keys
    if unexpected:
        # Não refletir valores: podem incluir credenciais ou dados privados.
        raise SnapshotError("{} contém campos não permitidos".format(label))


def load_snapshot(path):
    """Carrega um JSON pequeno; não faz solicitações HTTP nem importa MT5."""
    file_path = Path(path)
    try:
        if not file_path.is_file() or file_path.stat().st_size > MAX_BYTES:
            raise SnapshotError("Arquivo inexistente ou maior que 1 MB")
        with file_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data
    except SnapshotError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SnapshotError("Não foi possível abrir um JSON válido") from exc


def analyze_snapshot(data):
    """Retorna diagnóstico objetivo, nunca sinais de compra/venda."""
    _strict_object(data, ALLOWED_TOP, "Snapshot")
    if set(data) != ALLOWED_TOP:
        raise SnapshotError("Campos obrigatórios ausentes no snapshot")
    if data["schema_version"] != SCHEMA_VERSION:
        raise SnapshotError("Versão do contrato não suportada")
    if data["source"] not in SOURCES:
        raise SnapshotError("Somente origem synthetic/historical/demo é aceita")
    symbol = data["symbol"]
    if not isinstance(symbol, str) or not 1 <= len(symbol) <= 25 or not symbol.isascii():
        raise SnapshotError("Símbolo inválido")
    if not all(c.isalnum() or c in "._-" for c in symbol):
        raise SnapshotError("Símbolo contém caracteres não permitidos")
    timeframe = data["timeframe"]
    if timeframe not in TIMEFRAMES:
        raise SnapshotError("Timeframe não suportado")
    interval = TIMEFRAMES[timeframe]
    captured = _utc(data["captured_at"], "captured_at")
    spread = _finite_number(data["spread"], "spread")
    bars = data["bars"]
    if not isinstance(bars, list) or not 1 <= len(bars) <= MAX_BARS:
        raise SnapshotError("bars deve conter de 1 a 2000 candles")

    observed = []
    ranges = []
    gaps = 0
    previous = None
    for index, bar in enumerate(bars):
        _strict_object(bar, ALLOWED_BAR, "Candle")
        if set(bar) != ALLOWED_BAR:
            raise SnapshotError("Candle com campos obrigatórios ausentes")
        when = _utc(bar["time"], "bars.time")
        if when > captured:
            raise SnapshotError("Candle posterior à captura")
        if previous is not None:
            elapsed = (when - previous).total_seconds()
            if elapsed <= 0:
                raise SnapshotError("Candles duplicados ou fora de ordem")
            if elapsed < interval:
                raise SnapshotError("Intervalo entre candles menor que o timeframe")
            if elapsed > interval:
                gaps += 1
        previous = when
        op = _finite_number(bar["open"], "open", strict=True)
        hi = _finite_number(bar["high"], "high", strict=True)
        lo = _finite_number(bar["low"], "low", strict=True)
        cl = _finite_number(bar["close"], "close", strict=True)
        _finite_number(bar["volume"], "volume")
        if lo > min(op, cl) or hi < max(op, cl) or hi < lo:
            raise SnapshotError("OHLC inconsistente")
        ranges.append(hi - lo)
        observed.append(when)

    avg_range = sum(ranges) / len(ranges)
    age = (captured - observed[-1]).total_seconds()
    stale = age > (2 * interval)
    relative_spread = (spread / avg_range) if avg_range > 0 else None
    large_spread = relative_spread is not None and relative_spread > 0.25
    warnings = []
    if gaps:
        warnings.append("Há lacunas na sequência de candles")
    if stale:
        warnings.append("Último candle antigo em relação à captura")
    if large_spread:
        warnings.append("Spread alto em relação à amplitude média da amostra")
    if relative_spread is None:
        warnings.append("Sem amplitude para comparação de spread")
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "offline_read_only",
        "status": "warning" if warnings else "ok",
        "source": data["source"],
        "symbol": symbol,
        "timeframe": timeframe,
        "captured_at_utc": captured.isoformat(),
        "bar_count": len(bars),
        "last_bar_time_utc": observed[-1].isoformat(),
        "last_bar_age_seconds": round(age, 3),
        "stale": stale,
        "gaps_detected": gaps,
        "spread_price": spread,
        "average_bar_range_price": round(avg_range, 6),
        "spread_to_average_range": round(relative_spread, 6) if relative_spread is not None else None,
        "high_relative_spread": large_spread,
        "warnings": warnings,
        "trading_enabled": False,
        "orders_sent": 0,
        "advice": "Nenhum sinal de negociação; diagnóstico de qualidade de dados.",
    }
