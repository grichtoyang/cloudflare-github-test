import json

from taifex_loader import load_taifex
from twse_loader import load_twse


TEST_DATE = "2026-09-09"


def test_taifex():
    print("=" * 60)
    print("TEST 1 — TAIFEX")
    print("=" * 60)

    data = load_taifex(TEST_DATE)

    proxy_data = data["data"]

    print(f"Date   : {TEST_DATE}")
    print(f"Source : {data.get('source')}")
    print(f"Status : {proxy_data.get('ok')}")

    assert proxy_data.get("ok") is True
    assert data.get("source") == "TAIFEX"

    print("TAIFEX: PASS")
    print()


def test_twse():
    print("=" * 60)
    print("TEST 2 — TWSE")
    print("=" * 60)

    data = load_twse(TEST_DATE)

    proxy_data = data["data"]

    print(f"Date   : {TEST_DATE}")
    print(f"Source : {data.get('source')}")
    print(f"Status : {proxy_data.get('ok')}")

    assert proxy_data.get("ok") is True
    assert data.get("source") == "TWSE"

    print("TWSE: PASS")
    print()


def test_combined():
    print("=" * 60)
    print("TEST 3 — COMBINED MARKET DATA")
    print("=" * 60)

    taifex = load_taifex(TEST_DATE)
    twse = load_twse(TEST_DATE)

    market_data = {
        "date": TEST_DATE,
        "taifex": taifex,
        "twse": twse,
    }

    assert market_data["date"] == TEST_DATE
    assert market_data["taifex"]["data"]["ok"] is True
    assert market_data["twse"]["data"]["ok"] is True

    print("Date   :", market_data["date"])
    print("TAIFEX : PASS")
    print("TWSE   : PASS")
    print("Combined Market Data: PASS")
    print()

    print("Combined structure:")
    print(
        json.dumps(
            {
                "date": market_data["date"],
                "taifex": {
                    "ok": market_data["taifex"]["data"].get("ok"),
                    "source": market_data["taifex"].get("source"),
                },
                "twse": {
                    "ok": market_data["twse"]["data"].get("ok"),
                    "source": market_data["twse"].get("source"),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    test_taifex()
    test_twse()
    test_combined()

    print()
    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
