import json
from pathlib import Path
from datetime import date


class TAIFEXDataLoader:
    """TAIFEX 每日 JSON 資料載入器"""

    def __init__(self, data_dir="data/taifex"):
        self.data_dir = Path(data_dir)

    def load(self, target_date=None):
        """
        載入指定日期的 TAIFEX JSON。

        target_date:
            None -> 使用今天日期
            str  -> YYYY-MM-DD
        """

        if target_date is None:
            target_date = date.today().isoformat()

        file_path = self.data_dir / f"{target_date}.json"

        if not file_path.exists():
            raise FileNotFoundError(
                f"找不到 TAIFEX 資料檔案: {file_path}"
            )

        with file_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        self._validate(raw, target_date)

        # Cloudflare Proxy → GitHub JSON
        proxy_data = raw.get("data", {})

        # TAIFEX modules
        taifex_data = proxy_data.get("data", {})

        return {
            "date": target_date,
            "source": raw.get("source"),
            "proxy": raw.get("proxy"),
            "file": str(file_path),

            "futures_price": self._extract(
                taifex_data,
                "futures_price"
            ),

            "futures_institutional": self._extract(
                taifex_data,
                "futures_institutional"
            ),

            "futures_institutional_oi": self._extract(
                taifex_data,
                "futures_institutional_oi"
            ),
        }

    @staticmethod
    def _extract(data, key):
        """取得 TAIFEX module 的 data 陣列"""

        module = data.get(key, {})

        if not isinstance(module, dict):
            raise ValueError(
                f"TAIFEX module 格式錯誤: {key}"
            )

        rows = module.get("data", [])

        if not isinstance(rows, list):
            raise ValueError(
                f"TAIFEX module data 必須是 list: {key}"
            )

        return rows

    @staticmethod
    def _validate(raw, target_date):
        """基本資料完整性驗證"""

        if not isinstance(raw, dict):
            raise ValueError(
                "TAIFEX JSON 根節點必須是 object"
            )

        if raw.get("date") != target_date:
            raise ValueError(
                f"日期不一致: "
                f"JSON={raw.get('date')} "
                f"要求={target_date}"
            )

        if "data" not in raw:
            raise ValueError(
                "TAIFEX JSON 缺少 data"
            )


def load_taifex(target_date=None):
    """簡易介面"""

    loader = TAIFEXDataLoader()
    return loader.load(target_date)


if __name__ == "__main__":
    data = load_taifex()

    print("=" * 60)
    print("TAIFEX Data Loader V1.0")
    print("=" * 60)

    print(f"Date   : {data['date']}")
    print(f"Source : {data['source']}")
    print(f"Proxy  : {data['proxy']}")
    print(f"File   : {data['file']}")

    print()
    print("-" * 60)
    print("TAIFEX Data Modules")
    print("-" * 60)

    print(
        f"futures_price           : "
        f"{len(data['futures_price'])} 筆"
    )

    print(
        f"futures_institutional   : "
        f"{len(data['futures_institutional'])} 筆"
    )

    print(
        f"futures_institutional_oi: "
        f"{len(data['futures_institutional_oi'])} 筆"
    )

    print()
    print("=" * 60)
    print("TAIFEX Data Loader 成功")
    print("=" * 60)
