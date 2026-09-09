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


def load_taifex(date: str) -> dict:
    """
    讀取指定日期的 TAIFEX 原始 JSON。
    """

    url = f"{GITHUB_RAW_BASE}/taifex/{date}.json"

    wrapper = load_json(url)

    # ----------------------------------------
    # 第一層：GitHub 儲存的資料封裝
    # ----------------------------------------
    if not isinstance(wrapper, dict):
        raise ValueError("TAIFEX data is not a JSON object")

    if wrapper.get("source") != "TAIFEX":
        raise ValueError("Invalid TAIFEX source")

    # ----------------------------------------
    # 第二層：Proxy 回傳結果
    # ----------------------------------------
    proxy_data = wrapper.get("data")

    if not isinstance(proxy_data, dict):
        raise ValueError("TAIFEX proxy data is missing")

    if proxy_data.get("ok") is not True:
        raise ValueError("TAIFEX proxy status is not OK")

    # ----------------------------------------
    # 第三層：TAIFEX datasets
    # ----------------------------------------
    datasets = proxy_data.get("data")

    if not isinstance(datasets, dict):
        raise ValueError("TAIFEX datasets are missing")

    # 至少確認三個核心資料集存在
    required_datasets = [
        "futures_price",
        "futures_institutional",
        "futures_institutional_oi",
    ]

    for name in required_datasets:
        if name not in datasets:
            raise ValueError(
                f"TAIFEX dataset missing: {name}"
            )

    return wrapper


if __name__ == "__main__":

    TEST_DATE = "2026-09-09"

    print("=" * 60)
    print("TAIFEX Loader V1.1")
    print("=" * 60)

    data = load_taifex(TEST_DATE)

    proxy_data = data["data"]
    datasets = proxy_data["data"]

    print(f"Date: {TEST_DATE}")
    print("Source: TAIFEX")
    print("Proxy status: OK")
    print()

    print("TAIFEX datasets:")

    for name, dataset in datasets.items():

        if isinstance(dataset, dict):
            rows = dataset.get("data", [])

            if isinstance(rows, list):
                print(f"  {name}: {len(rows)} rows")
            else:
                print(f"  {name}: OK")
        else:
            print(f"  {name}: OK")

    print()
    print("TAIFEX Loader: PASS")
