#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

def num(v):
    if v is None: return None
    s = str(v).replace(',', '').replace('%', '').replace('－', '-').replace('—', '-').strip()
    if s in ('', '--', '---', 'N/A', 'null', 'None', '除息', '-'): return None
    m = re.search(r'-?\d+(?:\.\d+)?', s)
    return float(m.group()) if m else None

def load_raw(root, name, date):
    p = root / 'raw' / f'{name}_{date}.json'
    if not p.exists(): return None
    try:
        x = json.loads(p.read_text(encoding='utf-8'))
        return x.get('payload') if isinstance(x, dict) else x
    except Exception:
        return None

def load_twse(root, date):
    p = root / 'twse' / f'{date}.json'
    if not p.exists(): return {}
    try:
        x = json.loads(p.read_text(encoding='utf-8'))
        return x.get('data', {}) if isinstance(x, dict) else {}
    except Exception:
        return {}

def rows(x):
    if isinstance(x, list): return x
    if isinstance(x, dict):
        fields = x.get('fields') or x.get('columns') or []
        data = x.get('data') or x.get('records') or x.get('aaData') or []
        if fields and data:
            return [{str(fields[i]): v for i, v in enumerate(r) if i < len(fields)} if isinstance(r, list) else r for r in data]
        return data if isinstance(data, list) else []
    return []

def field(r, *names):
    if not isinstance(r, dict): return None
    for n in names:
        if n in r: return num(r[n])
    for k, v in r.items():
        nk = re.sub(r'[^a-z0-9一-龥]', '', str(k).lower())
        if any(re.sub(r'[^a-z0-9一-龥]', '', str(n).lower()) == nk for n in names): return num(v)
    return None

def first(x, pred=lambda r: True):
    return next((r for r in rows(x) if isinstance(r, dict) and pred(r)), {})

def total(x, *names):
    vals = [field(r, *names) for r in rows(x)]
    vals = [v for v in vals if v is not None]
    return sum(vals) if vals else None

def add(a, b):
    return a + b if a is not None and b is not None else (a if b is None else b)

def table_value(table, label, column):
    if not isinstance(table, dict): return None
    fields, data = table.get('fields', []), table.get('data', [])
    try: i = fields.index(column)
    except ValueError: return None
    for r in data:
        if r and str(r[0]).strip() == label: return num(r[i]) if len(r) > i else None
    return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--date', required=True); ap.add_argument('--output-root', default='data'); a = ap.parse_args()
    d, root = a.date, Path(a.output_root)
    tw = load_twse(root, d)
    ta = tw.get('taiex', {}); stats = tw.get('market_statistics', {}); br = tw.get('advance_decline', {})
    mi = load_raw(root, 'twse_mi_index', d); breadth = load_raw(root, 'twse_listed_breadth', d)
    t86 = load_raw(root, 'twse_t86', d); margin = load_raw(root, 'twse_margin', d); sbl = load_raw(root, 'twse_sbl', d); turn = load_raw(root, 'twse_turnover', d)
    om = load_raw(root, 'tpex_margin', d); os = load_raw(root, 'tpex_sbl', d); oh = load_raw(root, 'tpex_highlight', d)
    idx = first(mi, lambda r: r.get('指數') == '發行量加權股價指數'); listed = first(breadth, lambda r: r.get('類型') == '股票'); tr = first(turn)
    close = num(ta.get('close')) if ta else field(idx, '收盤指數')
    change = num(ta.get('change')) if ta else field(idx, '漲跌點數')
    change_pct = num(ta.get('change_percent')) if ta else field(idx, '漲跌百分比')
    listed_up = table_value(br, '上漲(漲停)', '股票') if br else field(listed, '上漲')
    listed_down = table_value(br, '下跌(跌停)', '股票') if br else field(listed, '下跌')
    listed_flat = table_value(br, '持平', '股票') if br else field(listed, '持平')
    listed_turn = table_value(stats, '總計(1~15)', '成交金額(元)') or field(tr, 'TradeValue')
    otc = first(oh); otc_turn = field(otc, 'DailyTradingValue'); otc_turn = otc_turn * 1000000 if otc_turn is not None else None
    tw_fin = total(margin, '融資今日餘額'); tp_fin = total(om, 'MarginPurchaseBalance')
    tw_fin_ch = add(total(margin, '融資買進'), -total(margin, '融資賣出')) if total(margin, '融資買進') is not None and total(margin, '融資賣出') is not None else None
    data = {'taiex': {'close': close, 'open': None, 'high': None, 'low': None, 'change_points': change, 'change_percent': change_pct, 'turnover_value': listed_turn}, 'listed_breadth': {'up': listed_up, 'down': listed_down, 'unchanged': listed_flat, 'limit_up': None, 'limit_down': None}, 'otc_breadth': {'up': field(otc, 'PriceRiseCompanyNumbers'), 'down': field(otc, 'PriceDeclineCompanyNumbers'), 'unchanged': field(otc, 'PriceFlatCompanyNumbers'), 'limit_up': field(otc, 'LimitUpCompanyNumbers'), 'limit_down': field(otc, 'LimitDownCompanyNumbers')}, 'institutional': {'unit': 'shares', 'foreign': total(t86, '外陸資買賣超股數(不含外資自營商)'), 'investment_trust': total(t86, '投信買賣超股數'), 'dealer': total(t86, '自營商買賣超股數'), 'total': total(t86, '三大法人買賣超股數')}, 'margin': {'financing_balance': add(tw_fin, tp_fin), 'financing_change': add(tw_fin_ch, total(om, 'MarginPurchase')), 'short_balance': add(total(margin, '融券今日餘額'), total(om, 'ShortSaleBalance')), 'short_change': add(add(total(margin, '融券賣出'), -total(margin, '融券買進')) if total(margin, '融券賣出') is not None and total(margin, '融券買進') is not None else None, total(om, 'ShortSale')), 'maintenance_ratio': None}, 'sbl': {'balance': total(os, 'SecuritiesBorrowingBalanceOfTheMarketDay'), 'short_sale_balance': None, 'short_sale_change': None}, 'turnover': {'listed': listed_turn, 'otc': otc_turn, 'total': add(listed_turn, otc_turn)}}
    optional = {'taiex.open', 'taiex.high', 'taiex.low', 'listed_breadth.limit_up', 'listed_breadth.limit_down', 'margin.maintenance_ratio', 'sbl.balance', 'sbl.short_sale_balance', 'sbl.short_sale_change'}
    unavailable = [f'{g}.{k}' for g, obj in data.items() for k, v in obj.items() if v is None and f'{g}.{k}' not in optional and k != 'unit']
    out = {'ok': not unavailable, 'source': 'SPOT', 'date': d, 'retrieved_at': datetime.now(timezone.utc).isoformat(), 'timezone': 'UTC', 'data': data, 'missing_required': [], 'unavailable_fields': unavailable, 'integrity_errors': []}
    for p in (root / 'snapshots' / d / 'spot-snapshot.json', root / 'spot' / f'{d}.json'):
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'date': d, 'ok': out['ok'], 'unavailable_fields': unavailable, 'integrity_errors': []}, ensure_ascii=False)); return 0 if out['ok'] else 1

if __name__ == '__main__': sys.exit(main())
