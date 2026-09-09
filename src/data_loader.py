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
    """讀取指定日期 TAIFEX 資料。"""

    url = f"{GITHUB_RAW_BASE}/taifex/{date}.json"

    return load_json(url)


def load_twse(date: str) -> dict:
    """讀取指定日期 TWSE 資料。"""

    url = f"{GITHUB_RAW_BASE}/twse/{date}.json"

    return load_json(url)


def load_market_data(date: str) -> dict:
    """
    同時讀取 TAIFEX + TWSE。
    """

    taifex = load_taifex(date)
    twse = load_twse(date)

    return {
        "date": date,
        "taifex": taifex,
        "twse": twse,
    }


if __name__ == "__main__":

    TEST_DATE = "2026-09-09"

    market_data = load_market_data(TEST_DATE)

    print("=" * 60)
    print("每日盤前分析 V1.0")
    print("=" * 60)

    print(f"Date: {market_data['date']}")

    print("\nTAIFEX:")
    print(
        json.dumps(
            market_data["taifex"],
            ensure_ascii=False,
            indent=2
        )
    )

    print("\nTWSE:")
    print(
        json.dumps(
            market_data["twse"],
            ensure_ascii=False,
            indent=2
        )
    )
