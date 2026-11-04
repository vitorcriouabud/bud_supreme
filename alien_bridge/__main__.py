"""Uso: python -m alien_bridge examples/alien_xauusd_snapshot.json"""
import argparse
import json
import sys

from .observer import SnapshotError, analyze_snapshot, load_snapshot


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Observador offline Bud–ALIEN; não envia ordens."
    )
    parser.add_argument("snapshot", help="Caminho do JSON local (máximo 1 MB)")
    args = parser.parse_args(argv)
    try:
        report = analyze_snapshot(load_snapshot(args.snapshot))
    except SnapshotError as exc:
        # Não exibir o conteúdo de arquivos nem credenciais.
        print(json.dumps({
            "status": "error", "mode": "offline_read_only",
            "error": str(exc), "trading_enabled": False,
            "orders_sent": 0,
        }, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
