import json
import tempfile
import unittest
from pathlib import Path

from taifex_loader import TAIFEXDataLoader


class TAIFEXLoaderTests(unittest.TestCase):
    def test_loader_accepts_ready_manifest_and_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            date = "2026-09-11"
            snapshot_path = root / "snapshots" / date / "snapshot.json"
            manifest_path = root / "manifests" / f"{date}.json"
            snapshot_path.parent.mkdir(parents=True)
            manifest_path.parent.mkdir(parents=True)

            endpoint = {
                "ok": True,
                "source": "TAIFEX",
                "dataset": "futures-price",
                "data": [{"contract_month": "202609"}],
            }
            snapshot = {
                "date": date,
                "source": "TAIFEX",
                "proxy": "https://taifex.grichtoyang.workers.dev",
                "validation": {"ready_for_analysis": True},
                "data": {
                    "futures-price": endpoint,
                    "futures-institutional": {"data": []},
                    "futures-institutional-oi": {"data": []},
                },
            }
            snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")
            manifest = {
                "manifest_version": "1.1.0",
                "analysis_date": date,
                "published": True,
                "published_snapshot": str(snapshot_path),
                "validation": {"validation_errors": []},
                "ready_for_analysis": True,
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            data = TAIFEXDataLoader(root).load(date)
            self.assertTrue(data["ready_for_analysis"])
            self.assertEqual(data["futures_price"][0]["contract_month"], "202609")

    def test_loader_blocks_not_ready_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            date = "2026-09-11"
            manifest_path = root / "manifests" / f"{date}.json"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "analysis_date": date,
                        "published": True,
                        "validation": {"validation_errors": ["endpoint failed"]},
                        "ready_for_analysis": False,
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(RuntimeError):
                TAIFEXDataLoader(root).load(date)


if __name__ == "__main__":
    unittest.main()
