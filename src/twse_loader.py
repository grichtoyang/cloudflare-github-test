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

    data = load_json(url)

    # 基本資料驗證
    if not isinstance(data, dict):
        raise ValueError("TWSE data is not a JSON object")

    if not data.get("ok"):
        raise ValueError("TWSE data status is not OK")

    if data.get("source") != "TWSE":
        raise ValueError("Invalid TWSE source")

    return data


if __name__ == "__main__":

    TEST_DATE = "2026-09-09"

    print("=" * 60)
    print("TWSE Loader V1.0")
    print("=" * 60)

    data = load_twse(TEST_DATE)

    print(f"Date: {TEST_DATE}")
    print("TWSE data loaded successfully.")
    print()

    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )
    )
