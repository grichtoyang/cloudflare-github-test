import json
from datetime import date
from pathlib import Path
from urllib.request import urlopen


GITHUB_RAW_BASE = (
    "https://raw.githubusercontent.com/"
    "grichtoyang/cloudflare-github-test/main/data"
)


class PreMarketDataLoader:
    """Load the canonical, manifest-gated daily pre-market package."""

    def __init__(self, data_root="data"):
        self.data_root = Path(data_root)

    def load(self, analysis_date=None):
        if analysis_date is None:
            analysis_date = date.today().isoformat()

        manifest_path = self.data_root / "premarket" / f"{analysis_date}.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"找不到 pre-market manifest: {manifest_path}")

        manifest = self._read_json(manifest_path)
        self._validate_manifest(manifest, analysis_date, manifest_path)

        sources = manifest.get("sources")
        if not isinstance(sources, dict):
            raise ValueError("pre-market manifest 缺少 sources")

        loaded_sources = {}
        for source in ("TAIFEX", "TWSE"):
            source_meta = sources.get(source)
            if not isinstance(source_meta, dict):
                raise ValueError(f"pre-market manifest 缺少 source: {source}")
            snapshot_ref = source_meta.get("snapshot")
            if not snapshot_ref:
                raise ValueError(f"pre-market manifest 缺少 {source} snapshot")
            snapshot_path = self._resolve_snapshot(snapshot_ref)
            if not snapshot_path.exists():
                raise FileNotFoundError(f"找不到已發布 {source} snapshot: {snapshot_path}")
            snapshot = self._read_json(snapshot_path)
            self._validate_snapshot(snapshot, source, manifest.get("t0_trading_date"), analysis_date)
            loaded_sources[source] = snapshot

        return {
            "date": analysis_date,
            "analysis_date": analysis_date,
            "t0_trading_date": manifest.get("t0_trading_date"),
            "manifest": str(manifest_path),
            "manifest_version": manifest.get("manifest_version"),
            "ready_for_analysis": True,
            "premarket": manifest,
            "taifex": loaded_sources["TAIFEX"],
            "twse": loaded_sources["TWSE"],
        }

    @staticmethod
    def _read_json(path):
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
        if not isinstance(value, dict):
            raise ValueError(f"{path} 根節點必須是 object")
        return value

    def _resolve_snapshot(self, reference):
        path = Path(reference)
        if path.is_absolute():
            return path
        return self.data_root.parent / path if path.parts and path.parts[0] == self.data_root.name else self.data_root / path

    @staticmethod
    def _validate_manifest(manifest, analysis_date, manifest_path):
        if manifest.get("manifest_type") != "pre-market":
            raise ValueError(f"不是 pre-market manifest: {manifest_path}")
        if manifest.get("analysis_date") != analysis_date:
            raise ValueError(
                f"manifest 日期不一致: JSON={manifest.get('analysis_date')} 要求={analysis_date}"
            )
        if manifest.get("ready_for_analysis") is not True:
            raise RuntimeError(f"READY_FOR_ANALYSIS=false，禁止分析: {manifest_path}")
        if manifest.get("published") is not True:
            raise RuntimeError(f"manifest 尚未標記 published: {manifest_path}")
        if manifest.get("validation", {}).get("validation_errors"):
            raise RuntimeError(f"manifest 存在 validation_errors: {manifest_path}")
        if set(manifest.get("validation", {}).get("successful_sources", [])) != {"TAIFEX", "TWSE"}:
            raise RuntimeError(f"pre-market sources 尚未全部成功: {manifest_path}")

    @staticmethod
    def _validate_snapshot(snapshot, source, t0_date, analysis_date):
        if snapshot.get("source") != source:
            raise ValueError(f"{source} snapshot source 不一致")
        if snapshot.get("validation", {}).get("ready_for_analysis") is not True:
            raise RuntimeError(f"{source} snapshot READY_FOR_ANALYSIS=false")
        expected_date = analysis_date if source == "TAIFEX" else t0_date
        if snapshot.get("date") != expected_date:
            raise ValueError(
                f"{source} snapshot 日期不一致: JSON={snapshot.get('date')} 要求={expected_date}"
            )


def load_premarket(analysis_date=None):
    return PreMarketDataLoader().load(analysis_date)


def load_json(url: str) -> dict:
    """從 GitHub Raw URL 讀取 JSON；保留作為底層相容函式。"""
    with urlopen(url, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def load_taifex(date: str) -> dict:
    """讀取指定日期 TAIFEX 原始 JSON；相容舊程式。"""
    return load_json(f"{GITHUB_RAW_BASE}/taifex/{date}.json")


def load_twse(date: str) -> dict:
    """讀取指定日期 TWSE 原始 JSON；相容舊程式。"""
    return load_json(f"{GITHUB_RAW_BASE}/twse/{date}.json")


def load_market_data(date: str = None) -> dict:
    """分析入口：一律透過 canonical pre-market manifest 載入。"""
    return load_premarket(date)


if __name__ == "__main__":
    TEST_DATE = date.today().isoformat()
    market_data = load_premarket(TEST_DATE)
    print("=" * 60)
    print("每日盤前分析 V1.1")
    print("=" * 60)
    print(f"Analysis Date: {market_data['analysis_date']}")
    print(f"T0: {market_data['t0_trading_date']}")
    print(f"Ready: {market_data['ready_for_analysis']}")
    print(f"Manifest: {market_data['manifest']}")
    print("=" * 60)
