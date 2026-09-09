import json
from urllib.request import urlopen


GITHUB_RAW_BASE = (
    "https://raw.githubusercontent.com/"
    "grichtoyang/cloudflare-github-test/main/data"
)


def load_json(url: str) -> dict:
    """從 GitHub Raw URL 讀取 JSON。"""

    with urlopen(url, timeout=15) as response:
        data = response.read().decode("utf-8")

    return json.loads(data)


def load_twse(date: str) -> dict:
    """
    讀取指定日期的 TWSE 原始 JSON。
    """

    url = f"{GITHUB_RAW_BASE}/twse/{date}.json"

    wrapper = load_json(url)

    # ----------------------------------------
    # 第一層：GitHub 儲存的資料封裝
    # ----------------------------------------
    if not isinstance(wrapper, dict):
        raise ValueError("TWSE data is not a JSON object")

    if wrapper.get("source") != "TWSE":
        raise ValueError("Invalid TWSE source")

    # ----------------------------------------
    # 第二層：TWSE Proxy 回傳結果
    # ----------------------------------------
    proxy_data = wrapper.get("data")

    if not isinstance(proxy_data, dict):
        raise ValueError("TWSE proxy data is missing")

    if proxy_data.get("ok") is not True:
        raise ValueError("TWSE proxy status is not OK")

    return wrapper


if __name__ == "__main__":

    TEST_DATE = "2026-09-09"

    print("=" * 60)
    print("TWSE Loader V1.1")
    print("=" * 60)

    data = load_twse(TEST_DATE)

    proxy_data = data["data"]

    print(f"Date: {TEST_DATE}")
    print("Source: TWSE")
    print("Proxy status: OK")

    # 顯示 TWSE tables 數量
    tables = proxy_data.get("data", {}).get("tables", [])

    if isinstance(tables, list):
        print(f"TWSE tables: {len(tables)}")

    print()
    print("TWSE Loader: PASS")
