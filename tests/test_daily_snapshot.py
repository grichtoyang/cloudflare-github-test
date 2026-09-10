import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.daily_snapshot as daily_snapshot


class DailySnapshotTests(unittest.TestCase):
    def fake_fetch(self, url, retries, timeout):
        if url.endswith("/health"):
            return {"ok": True}, 200, 1

        endpoint = url.rstrip("/").split("/")[-1].split("?")[0]
        payload = {"ok": True, "source": "TAIFEX", "dataset": endpoint, "data": {}}
        if "?date=" in url:
            payload["date"] = url.split("?date=", 1)[1]
        return payload, 200, 1

    def test_success_publishes_stable_artifacts_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(daily_snapshot, "fetch_json", side_effect=self.fake_fetch):
                with patch("sys.argv", ["daily_snapshot.py", "--date", "2026-09-11", "--output-root", tmp]):
                    rc = daily_snapshot.main()

            self.assertEqual(rc, 0)
            root = Path(tmp)
            snapshot = root / "snapshots" / "2026-09-11" / "snapshot.json"
            manifest = root / "manifests" / "2026-09-11.json"
            legacy = root / "taifex" / "2026-09-11.json"
            self.assertTrue(snapshot.exists())
            self.assertTrue(manifest.exists())
            self.assertTrue(legacy.exists())

            data = json.loads(snapshot.read_text(encoding="utf-8"))
            meta = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertTrue(data["validation"]["ready_for_analysis"])
            self.assertTrue(meta["ready_for_analysis"])
            self.assertEqual(meta["required_endpoint_count"], 15)
            self.assertEqual(meta["successful_endpoint_count"], 15)

    def test_second_run_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            argv = ["daily_snapshot.py", "--date", "2026-09-11", "--output-root", tmp]
            with patch.object(daily_snapshot, "fetch_json", side_effect=self.fake_fetch):
                with patch("sys.argv", argv):
                    self.assertEqual(daily_snapshot.main(), 0)

                with patch("sys.argv", argv):
                    self.assertEqual(daily_snapshot.main(), 3)

    def test_failed_attempt_does_not_publish_ready_artifacts(self):
        def failed_fetch(url, retries, timeout):
            if url.endswith("/health"):
                return {"ok": True}, 200, 1
            raise RuntimeError("upstream unavailable")

        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(daily_snapshot, "fetch_json", side_effect=failed_fetch):
                with patch("sys.argv", ["daily_snapshot.py", "--date", "2026-09-11", "--output-root", tmp]):
                    self.assertEqual(daily_snapshot.main(), 1)

            root = Path(tmp)
            self.assertFalse((root / "taifex" / "2026-09-11.json").exists())
            self.assertFalse((root / "manifests" / "2026-09-11.json").exists())
            attempts = list((root / "snapshots" / "2026-09-11").glob("attempt-*/manifest.json"))
            self.assertEqual(len(attempts), 1)
            attempt = json.loads(attempts[0].read_text(encoding="utf-8"))
            self.assertFalse(attempt["ready_for_analysis"])


if __name__ == "__main__":
    unittest.main()
