import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import twse_snapshot


class TwseSnapshotTests(unittest.TestCase):
    TARGET_DATE = "2026-09-11"

    def payload(self, date=TARGET_DATE, ok=True):
        return {
            "ok": ok,
            "source": "TWSE",
            "proxy": "twse-proxy",
            "version": "1.0.0",
            "date": date,
            "endpoints": {
                "IND": {"status": 200, "fetch_ok": True},
                "MS": {"status": 200, "fetch_ok": True},
            },
            "data": {
                "taiex": {"date": date, "close": 25000},
                "market_statistics": {"total_volume": 1},
                "advance_decline": {"advance": 1000, "decline": 500},
            },
        }

    def run_in_temp(self, root, payload):
        old = os.getcwd()
        try:
            os.chdir(root)
            with patch.object(twse_snapshot, "fetch_json", return_value=(payload, 200, 1)):
                return twse_snapshot.main(["--date", self.TARGET_DATE])
        finally:
            os.chdir(old)

    def test_success_publishes_stable_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status = self.run_in_temp(root, self.payload())
            self.assertEqual(status, 0)
            self.assertTrue((root / "data/twse/2026-09-11.json").exists())
            self.assertTrue((root / "data/snapshots/2026-09-11/twse-snapshot.json").exists())
            manifest = json.loads((root / "data/manifests/2026-09-11.twse.json").read_text())
            self.assertTrue(manifest["ready_for_analysis"])
            self.assertTrue(manifest["published"])

    def test_invalid_payload_does_not_publish_stable_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = self.payload()
            bad["endpoints"]["MS"]["fetch_ok"] = False
            status = self.run_in_temp(root, bad)
            self.assertNotEqual(status, 0)
            self.assertFalse((root / "data/twse/2026-09-11.json").exists())
            self.assertFalse((root / "data/snapshots/2026-09-11/twse-snapshot.json").exists())

    def test_second_run_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.run_in_temp(root, self.payload()), 0)
            self.assertEqual(self.run_in_temp(root, self.payload()), 3)


if __name__ == "__main__":
    unittest.main()
