import json
import tempfile
import unittest
from pathlib import Path

from src.data_loader import PreMarketDataLoader


class PreMarketDataLoaderTests(unittest.TestCase):
    def _write(self, path: Path, value: dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_loader_uses_canonical_manifest_and_source_snapshots(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "data"
            analysis_date = "2026-09-11"
            t0 = "2026-09-10"

            self._write(
                root / "premarket" / f"{analysis_date}.json",
                {
                    "manifest_version": "1.2.0",
                    "manifest_type": "pre-market",
                    "analysis_date": analysis_date,
                    "t0_trading_date": t0,
                    "sources": {
                        "TAIFEX": {"snapshot": "data/snapshots/2026-09-10/snapshot.json", "ready_for_analysis": True},
                        "TWSE": {"snapshot": "data/snapshots/2026-09-10/twse-snapshot.json", "ready_for_analysis": True},
                    },
                    "validation": {"successful_sources": ["TAIFEX", "TWSE"], "validation_errors": []},
                    "ready_for_analysis": True,
                    "published": True,
                },
            )
            self._write(
                root / "snapshots" / t0 / "snapshot.json",
                {"date": analysis_date, "source": "TAIFEX", "validation": {"ready_for_analysis": True}, "data": {}},
            )
            self._write(
                root / "snapshots" / t0 / "twse-snapshot.json",
                {"date": t0, "source": "TWSE", "validation": {"ready_for_analysis": True}, "data": {}},
            )

            result = PreMarketDataLoader(root).load(analysis_date)
            self.assertTrue(result["ready_for_analysis"])
            self.assertEqual(result["analysis_date"], analysis_date)
            self.assertEqual(result["t0_trading_date"], t0)
            self.assertEqual(result["taifex"]["source"], "TAIFEX")
            self.assertEqual(result["twse"]["source"], "TWSE")

    def test_loader_blocks_not_ready_canonical_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "data"
            analysis_date = "2026-09-11"
            self._write(
                root / "premarket" / f"{analysis_date}.json",
                {
                    "manifest_type": "pre-market",
                    "analysis_date": analysis_date,
                    "validation": {"successful_sources": [], "validation_errors": ["TAIFEX failed"]},
                    "ready_for_analysis": False,
                    "published": False,
                },
            )
            with self.assertRaises(RuntimeError):
                PreMarketDataLoader(root).load(analysis_date)


if __name__ == "__main__":
    unittest.main()
