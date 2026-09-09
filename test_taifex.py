import json
from pathlib import Path


FILE_PATH = Path("data/taifex/2026-09-09.json")


def main():
    print("=" * 60)
    print("TAIFEX GitHub → Python 測試")
    print("=" * 60)

    # 檢查檔案
    if not FILE_PATH.exists():
        raise FileNotFoundError(
            f"找不到資料檔案: {FILE_PATH}"
        )

    # 讀取 JSON
    with FILE_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"資料檔案: {FILE_PATH}")
    print(f"日期: {data.get('date')}")
    print(f"來源: {data.get('source')}")
    print(f"Proxy: {data.get('proxy')}")

    # 取得 TAIFEX data
    taifex = data.get("data", {})

    print()
    print("-" * 60)
    print("TAIFEX 資料模組")
    print("-" * 60)

    # futures_price
    futures_price = taifex.get("futures_price", [])
    print(
        f"futures_price       : "
        f"{len(futures_price)} 筆"
    )

    # futures_institutional
    futures_institutional = taifex.get(
        "futures_institutional", []
    )
    print(
        f"futures_institutional: "
        f"{len(futures_institutional)} 筆"
    )

    # futures_institutional_oi
    futures_institutional_oi = taifex.get(
        "futures_institutional_oi", []
    )
    print(
        f"futures_institutional_oi: "
        f"{len(futures_institutional_oi)} 筆"
    )

    print()
    print("=" * 60)
    print("Python 讀取 TAIFEX JSON 成功")
    print("=" * 60)


if __name__ == "__main__":
    main()
