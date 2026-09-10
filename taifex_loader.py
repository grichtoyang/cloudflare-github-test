import json
from datetime import date
from pathlib import Path


class TAIFEXDataLoader:
    """Load the immutable, manifest-gated daily TAIFEX snapshot."""

    def __init__(self, data_root="data"):
        self.data_root = Path(data_root)
        self.manifest_dir = self.data_root / "manifests"
        self.snapshot_dir = self.data_root / "snapshots"

    def load(self, target_date=None):
        if target_date is None:
            target_date = date.today().isoformat()

        manifest_path = self.manifest_dir / f"{target_date}.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"找不到 TAIFEX manifest: {manifest_path}")

        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)

        self._validate_manifest(manifest, target_date, manifest_path)

        snapshot_path = Path(
            manifest.get("published_snapshot")
            or self.snapshot_dir / target_date / "snapshot.json"
        )
        if not snapshot_path.is_absolute():
            snapshot_path = Path(snapshot_path)

        if not snapshot_path.exists():
            raise FileNotFoundError(f"找不到已發布 TAIFEX snapshot: {snapshot_path}")

        with snapshot_path.open("r", encoding="utf-8") as f:
            snapshot = json.load(f)

        self._validate_snapshot(snapshot, target_date, snapshot_path)
        endpoint_data = snapshot["data"]

        return {
            "date": target_date,
            "source": snapshot.get("source"),
            "proxy": snapshot.get("proxy"),
            "file": str(snapshot_path),
            "manifest": str(manifest_path),
            "manifest_version": manifest.get("manifest_version"),
            "ready_for_analysis": True,
            "endpoints": endpoint_data,
            # Compatibility aliases for existing analysis code.
            "futures_price": self._endpoint_rows(endpoint_data, "futures-price"),
            "futures_institutional": self._endpoint_rows(endpoint_data, "futures-institutional"),
            "futures_institutional_oi": self._endpoint_rows(endpoint_data, "futures-institutional-oi"),
        }

    @staticmethod
    def _endpoint_rows(data, endpoint):
        payload = data.get(endpoint)
        if not isinstance(payload, dict):
            raise ValueError(f"TAIFEX endpoint 缺失或格式錯誤: {endpoint}")
        rows = payload.get("data")
        if not isinstance(rows, list):
            raise ValueError(f"TAIFEX endpoint data 必須是 list: {endpoint}")
        return rows

    @staticmethod
    def _validate_manifest(manifest, target_date, manifest_path):
        if not isinstance(manifest, dict):
            raise ValueError("TAIFEX manifest 根節點必須是 object")
        if manifest.get("analysis_date") != target_date:
            raise ValueError(
                f"manifest 日期不一致: JSON={manifest.get('analysis_date')} 要求={target_date}"
            )
        if manifest.get("ready_for_analysis") is not True:
            raise RuntimeError(
                f"READY_FOR_ANALYSIS=false，禁止分析: {manifest_path}"
            )
        if manifest.get("published") is not True:
            raise RuntimeError(f"manifest 尚未標記 published: {manifest_path}")
        if manifest.get("validation", {}).get("validation_errors"):
            raise RuntimeError(f"manifest 存在 validation_errors: {manifest_path}")

    @staticmethod
    def _validate_snapshot(snapshot, target_date, snapshot_path):
        if not isinstance(snapshot, dict):
            raise ValueError("TAIFEX snapshot 根節點必須是 object")
        if snapshot.get("date") != target_date:
            raise ValueError(
                f"snapshot 日期不一致: JSON={snapshot.get('date')} 要求={target_date}"
            )
        if snapshot.get("validation", {}).get("ready_for_analysis") is not True:
            raise RuntimeError(f"snapshot READY_FOR_ANALYSIS=false: {snapshot_path}")
        data = snapshot.get("data")
        if not isinstance(data, dict):
            raise ValueError("TAIFEX snapshot 缺少 data object")


def load_taifex(target_date=None):
    return TAIFEXDataLoader().load(target_date)


if __name__ == "__main__":
    data = load_taifex()

    print("=" * 60)
    print("TAIFEX Immutable Snapshot Loader V1.1")
    print("=" * 60)
    print(f"Date   : {data['date']}")
    print(f"Source : {data['source']}")
    print(f"Proxy  : {data['proxy']}")
    print(f"File   : {data['file']}")
    print(f"Manifest: {data['manifest']}")
    print(f"Ready  : {data['ready_for_analysis']}")
    print(f"Endpoints: {len(data['endpoints'])}")
    print("=" * 60)
