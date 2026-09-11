import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import build_premarket_manifest


class PreMarketManifestDateTests(unittest.TestCase):
    def _write_source(self, root: Path, name: str, manifest: dict, snapshot_name: str) -> None:
        manifest_path = root / "data" / "manifests" / name
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path = root / "data" / "snapshots" / snapshot_name
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_text("{}\n", encoding="utf-8")
        manifest["published_snapshot"] = str(snapshot_path)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    def test_analysis_date_is_separate_from_t0(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_source(
                root,
                "2026-09-10.json",
                {
                    "analysis_date": "2026-09-11",
                    "source": "TAIFEX",
                    "ready_for_analysis": True,
                    "published": True,
                },
                "2026-09-10/taifex.json",
            )
            self._write_source(
                root,
                "2026-09-10.twse.json",
                {
                    "analysis_date": "2026-09-10",
                    "source": "TWSE",
                    "ready_for_analysis": True,
                    "published": True,
                },
                "2026-09-10/twse.json",
            )

            with patch("sys.argv", ["build_premarket_manifest.py", "--date", "2026-09-10", "--analysis-date", "2026-09-11", "--output-root", str(root / "data")]):
                rc = build_premarket_manifest.main()

            self.assertEqual(rc, 0)
            output = root / "data" / "premarket" / "2026-09-11.json"
            self.assertTrue(output.exists())
            manifest = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(manifest["analysis_date"], "2026-09-11")
            self.assertEqual(manifest["t0_trading_date"], "2026-09-10")
            self.assertTrue(manifest["ready_for_analysis"])
            self.assertTrue(manifest["published"])

    def test_taifex_must_match_analysis_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_source(
                root,
                "2026-09-10.json",
                {
                    "analysis_date": "2026-09-10",
                    "source": "TAIFEX",
                    "ready_for_analysis": True,
                    "published": True,
                },
                "2026-09-10/taifex.json",
            )
            self._write_source(
                root,
                "2026-09-10.twse.json",
                {
                    "analysis_date": "2026-09-10",
                    "source": "TWSE",
                    "ready_for_analysis": True,
                    "published": True,
                },
                "2026-09-10/twse.json",
            )

            with patch("sys.argv", ["build_premarket_manifest.py", "--date", "2026-09-10", "--analysis-date", "2026-09-11", "--output-root", str(root / "data")]):
                rc = build_premarket_manifest.main()

            self.assertEqual(rc, 1)
            output = root / "data" / "premarket" / "2026-09-11.json"
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
