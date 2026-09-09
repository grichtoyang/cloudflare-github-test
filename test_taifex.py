import json
from pathlib import Path


FILE_PATH = Path("data/taifex/2026-09-09.json")


def main():
    print("=" * 60)
    print("TAIFEX GitHub → Python 測試")
    print("=" * 60)

    if not FILE_PATH.exists():
        raise FileNotFoundError(
            f"找不到資料檔案: {FILE_PATH}"
        )

    with FILE_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"資料檔案: {FILE_PATH}")
    print(f"日期: {data.get('date')}")
    print(f"來源: {data.get('source')}")
    print(f"Proxy: {data.get('proxy')}")

    # ==========================================
    # 取得 Cloudflare Proxy 回傳的資料
    # ==========================================

    proxy_data = data.get("data", {})

    # 真正的 TAIFEX modules 在第二層 data
    taifex = proxy_data.get("data", {})

    print()
    print("-" * 60)
    print("TAIFEX 資料模組")
    print("-" * 60)

    futures_price = taifex.get("futures_price", {})
    futures_price_data = futures_price.get("data", [])

    print(
        f"futures_price          : "
        f"{len(futures_price_data)} 筆"
    )

    futures_institutional = taifex.get(
        "futures_institutional", {}
    )
    futures_institutional_data = futures_institutional.get(
        "data", []
    )

    print(
        f"futures_institutional   : "
        f"{len(futures_institutional_data)} 筆"
    )

    futures_institutional_oi = taifex.get(
        "futures_institutional_oi", {}
    )
    futures_institutional_oi_data = (
        futures_institutional_oi.get("data", [])
    )

    print(
        f"futures_institutional_oi: "
        f"{len(futures_institutional_oi_data)} 筆"
    )

    # ==========================================
    # 顯示台指期近月資料
    # ==========================================

    if futures_price_data:
        near = futures_price_data[0]

        print()
        print("-" * 60)
        print("台指期近月")
        print("-" * 60)

        print(f"Contract : {near.get('contract_month')}")
        print(f"Open     : {near.get('open')}")
        print(f"High     : {near.get('high')}")
        print(f"Low      : {near.get('low')}")
        print(f"Close    : {near.get('close')}")
        print(f"Change   : {near.get('change')}")
        print(f"Volume   : {near.get('total_volume')}")
        print(f"OI       : {near.get('open_interest')}")

    # ==========================================
    # 顯示三大法人期貨
    # ==========================================

    if futures_institutional_data:
        print()
        print("-" * 60)
        print("三大法人期貨")
        print("-" * 60)

        for item in futures_institutional_data:
            print(
                f"{item.get('institution'):20}"
                f"net_volume = "
                f"{item.get('net_volume')}"
            )

    # ==========================================
    # 顯示三大法人未平倉
    # ==========================================

    if futures_institutional_oi_data:
        print()
        print("-" * 60)
        print("三大法人未平倉")
        print("-" * 60)

        for item in futures_institutional_oi_data:
            print(
                f"{item.get('institution'):20}"
                f"net_oi = "
                f"{item.get('net_oi')}"
            )

    print()
    print("=" * 60)
    print("Python 讀取 TAIFEX JSON 成功")
    print("=" * 60)


if __name__ == "__main__":
    main()
