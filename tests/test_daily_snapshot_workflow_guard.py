from pathlib import Path


WORKFLOW = Path(".github/workflows/daily-snapshot.yml").read_text(encoding="utf-8")


def test_production_twse_proxy_is_canonical():
    assert 'TWSE_PROXY_BASE_URL: https://twse-proxy.grichtoyang.workers.dev' in WORKFLOW
    assert 'DEFAULT_BASE = "https://twse-proxy.grichtoyang.workers.dev"' in WORKFLOW


def test_legacy_guard_checks_active_default_only():
    assert 'DEFAULT_BASE = "https://taiex-proxy.grichtoyang.workers.dev"' in WORKFLOW
    assert 'legacy TWSE proxy URL is configured as the active collector DEFAULT_BASE' in WORKFLOW
    assert "if grep -F 'taiex-proxy.grichtoyang.workers.dev' scripts/twse_snapshot.py" not in WORKFLOW
