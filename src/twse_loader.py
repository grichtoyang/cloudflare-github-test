import json
from urllib.request import urlopen


GITHUB_RAW_BASE = (
    "https://raw.githubusercontent.com/"
    "grichtoyang/cloudflare-github-test/main/data"
)


def load_json(url: str) -> dict:
    """Load JSON from a URL."""
    with urlopen(url, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def load_twse(date: str) -> dict:
    """Load and validate the immutable daily TWSE snapshot."""
    url = f"{GITHUB_RAW_BASE}/twse/{date}.json"
    wrapper = load_json(url)

    if not isinstance(wrapper, dict):
        raise ValueError("TWSE snapshot is not a JSON object")
    if wrapper.get("ok") is not True:
        raise ValueError("TWSE snapshot ok != true")
    if wrapper.get("source") != "TWSE":
        raise ValueError("Invalid TWSE source")
    if wrapper.get("date") != date:
        raise ValueError(f"TWSE snapshot date={wrapper.get('date')}, expected={date}")

    endpoints = wrapper.get("endpoints")
    if not isinstance(endpoints, dict):
        raise ValueError("TWSE endpoints are missing")
    for name in ("IND", "MS"):
        endpoint = endpoints.get(name)
        if not isinstance(endpoint, dict):
            raise ValueError(f"TWSE endpoint {name} is missing")
        if endpoint.get("status") != 200 or endpoint.get("fetch_ok") is not True:
            raise ValueError(f"TWSE endpoint {name} is not OK")

    data = wrapper.get("data")
    if not isinstance(data, dict):
        raise ValueError("TWSE data is missing")
    for key in ("taiex", "market_statistics", "advance_decline"):
        if key not in data:
            raise ValueError(f"TWSE data.{key} is missing")

    return wrapper


if __name__ == "__main__":
    TEST_DATE = "2026-09-09"
    data = load_twse(TEST_DATE)
    print("TWSE Loader V1.2: PASS")
    print(f"Date: {data['date']}")
    print(f"TAIEX close: {data['data']['taiex']['close']}")
