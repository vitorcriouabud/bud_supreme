"""Testes sem MT5 e sem rede para o observador de dados."""
from copy import deepcopy
import json
import math
from pathlib import Path
import tempfile
import unittest

from alien_bridge import SnapshotError, analyze_snapshot, load_snapshot
from alien_bridge.__main__ import main


SAMPLE = {
    "schema_version": "alien-market-v1",
    "source": "synthetic",
    "symbol": "XAUUSD",
    "timeframe": "M1",
    "captured_at": "2026-11-04T12:04:40+00:00",
    "spread": 0.1,
    "bars": [
        {"time": "2026-11-04T12:03:00Z", "open": 2700, "high": 2702,
         "low": 2699, "close": 2701, "volume": 123},
        {"time": "2026-11-04T12:04:00Z", "open": 2701, "high": 2703,
         "low": 2700, "close": 2702, "volume": 125},
    ],
}


class AlienObserverTests(unittest.TestCase):
    def changed(self):
        return deepcopy(SAMPLE)

    def test_valid_snapshot_has_no_trading_execution(self):
        report = analyze_snapshot(self.changed())
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["bar_count"], 2)
        self.assertEqual(report["gaps_detected"], 0)
        self.assertFalse(report["trading_enabled"])
        self.assertEqual(report["orders_sent"], 0)
        self.assertEqual(report["mode"], "offline_read_only")

    def test_example_file(self):
        sample = load_snapshot(Path("examples/alien_xauusd_snapshot.json"))
        self.assertEqual(analyze_snapshot(sample)["symbol"], "XAUUSD")

    def test_valid_utc_conversion(self):
        sample = self.changed()
        sample["captured_at"] = "2026-11-04T09:04:40-03:00"
        self.assertEqual(analyze_snapshot(sample)["last_bar_age_seconds"], 40)

    def test_timestamps_must_have_timezone(self):
        sample = self.changed()
        sample["captured_at"] = "2026-11-04T12:04:40"
        with self.assertRaises(SnapshotError):
            analyze_snapshot(sample)

    def test_duplicate_candles_fails(self):
        sample = self.changed()
        sample["bars"][1]["time"] = sample["bars"][0]["time"]
        with self.assertRaises(SnapshotError):
            analyze_snapshot(sample)

    def test_future_candle_fails(self):
        sample = self.changed()
        sample["bars"][-1]["time"] = "2026-11-04T12:05:00Z"
        with self.assertRaises(SnapshotError):
            analyze_snapshot(sample)

    def test_gaps_are_reported(self):
        sample = self.changed()
        sample["bars"][0]["time"] = "2026-11-04T12:01:00Z"
        report = analyze_snapshot(sample)
        self.assertEqual(report["gaps_detected"], 1)
        self.assertEqual(report["status"], "warning")

    def test_staleness_is_reported(self):
        sample = self.changed()
        sample["captured_at"] = "2026-11-04T12:15:00Z"
        report = analyze_snapshot(sample)
        self.assertTrue(report["stale"])
        self.assertEqual(report["status"], "warning")

    def test_high_spread_relative_to_bars(self):
        sample = self.changed()
        sample["spread"] = 2.0
        self.assertTrue(analyze_snapshot(sample)["high_relative_spread"])

    def test_invalid_price_or_volume_rejected(self):
        for invalid in [math.nan, math.inf, -1, True, "1"]:
            with self.subTest(value=repr(invalid)):
                sample = self.changed()
                sample["bars"][0]["volume"] = invalid
                with self.assertRaises(SnapshotError):
                    analyze_snapshot(sample)

    def test_invalid_ohlc_rejected(self):
        sample = self.changed()
        sample["bars"][0]["low"] = 2701.5
        with self.assertRaises(SnapshotError):
            analyze_snapshot(sample)

    def test_secrets_and_unknown_keys_rejected(self):
        for key in ["password", "token", "account", "order"]:
            with self.subTest(key=key):
                sample = self.changed()
                sample[key] = "sensitive-value"
                with self.assertRaises(SnapshotError):
                    analyze_snapshot(sample)

    def test_bad_source_rejected(self):
        sample = self.changed()
        sample["source"] = "live"
        with self.assertRaises(SnapshotError):
            analyze_snapshot(sample)

    def test_max_bars_enforced(self):
        sample = self.changed()
        sample["bars"] = sample["bars"] * 1001
        with self.assertRaises(SnapshotError):
            analyze_snapshot(sample)

    def test_max_file_size_enforced(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "oversized.json"
            p.write_bytes(b" " * (1024 * 1024 + 1))
            with self.assertRaises(SnapshotError):
                load_snapshot(p)

    def test_cli_outputs_diagnostic(self):
        import contextlib
        import io
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(["examples/alien_xauusd_snapshot.json"])
        self.assertEqual(result, 0)
        report = json.loads(output.getvalue())
        self.assertFalse(report["trading_enabled"])

    def test_cli_missing_file_fails_without_false_success(self):
        import contextlib
        import io
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            status = main(["examples/no-such-file.json"])
        self.assertEqual(status, 2)
        self.assertEqual(json.loads(output.getvalue())["status"], "error")


if __name__ == "__main__":
    unittest.main()
