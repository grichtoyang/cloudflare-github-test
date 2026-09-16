#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-15"

p = subprocess.run(
    [sys.executable, "scripts/spot_snapshot.py", "--date", DATE],
    cwd=ROOT,
    text=True,
    capture_output=True,
)
if p.returncode not in (0, 3):
    raise SystemExit(f"spot_snapshot failed unexpectedly: {p.returncode}\n{p.stderr}")

payload = json.loads((ROOT / "data" / "spot" / f"{DATE}.json").read_text(encoding="utf-8"))
assert payload["source"] == "SPOT"
assert payload["data"]["taiex"]["close"] is not None
assert payload["data"]["taiex"]["change_points"] is not None
assert payload["data"]["taiex"]["change_percent"] is not None
assert payload["data"]["turnover"]["total"] is not None
assert payload["data"]["listed_breadth"]["up"] is not None
assert payload["data"]["listed_breadth"]["down"] is not None
assert payload["data"]["listed_breadth"]["unchanged"] is not None
assert payload["data"]["listed_breadth"]["limit_up"] is not None
assert payload["data"]["listed_breadth"]["limit_down"] is not None
print("SPOT contract checks passed")
