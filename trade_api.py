#!/usr/bin/env python3
"""PoE1 Trade Monitor — public stash stream & currency exchange.

USAGE:
  python3 trade_api.py --token=xxx public-stashes
  python3 trade_api.py --token=xxx exchange
  python3 trade_api.py --help

IMPORTANT API CHANGES (2024-2025):
- Public stash tabs: Requires OAuth (POETOKEN) - POESESSID is NOT sufficient
- Currency exchange: Requires OAuth (POETOKEN)

Many endpoints that were previously public now require OAuth authentication.
"""

import argparse
import json
import sys
import os
import urllib.request
import urllib.parse

BASE = "https://api.pathofexile.com"

# Global auth
_SESSION_ID = None
_OAUTH_TOKEN = None


def set_auth(session_id=None, oauth_token=None):
    global _SESSION_ID, _OAUTH_TOKEN
    if session_id:
        _SESSION_ID = session_id
    if oauth_token:
        _OAUTH_TOKEN = oauth_token


def get_headers(require_oauth=False):
    headers = {"User-Agent": "OpenClaw-PoE1-Skill/1.0"}
    
    token = _OAUTH_TOKEN or os.environ.get("POETOKEN") or os.environ.get("POE_TOKEN")
    if token:
        if not token.startswith("Bearer "):
            token = f"Bearer {token}"
        headers["Authorization"] = token
        return headers
    
    if require_oauth:
        print("錯誤: 此功能需要 OAuth 認證", file=sys.stderr)
        print("提示: 請設定 POETOKEN 環境變數或使用 --token 參數", file=sys.stderr)
        sys.exit(1)
    
    session = _SESSION_ID or os.environ.get("POESESSID") or os.environ.get("POE_SESSION")
    if session:
        headers["Cookie"] = f"POESESSID={session}"
    
    return headers


def get(path, params=None, require_oauth=False):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    
    headers = get_headers(require_oauth=require_oauth)
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        try:
            err_data = json.loads(body)
            message = err_data.get('message', err_data.get('error_description', 'Unknown error'))
        except:
            message = body[:200] if body else f"HTTP {e.code}"
        
        if e.code == 401:
            print(f"錯誤: 未授權 (401) - {message}", file=sys.stderr)
        elif e.code == 403:
            print(f"錯誤: 權限不足 (403) - {message}", file=sys.stderr)
            if require_oauth:
                print("提示: 此功能需要 OAuth 認證，請設定 POETOKEN", file=sys.stderr)
        else:
            print(f"錯誤: HTTP {e.code} - {message}", file=sys.stderr)
        sys.exit(1)


def fmt_item(item):
    rarity = item.get("rarity", "")
    name = item.get("name", "")
    t = item.get("typeLine", "")
    identified = "已鑑定" if item.get("identified") else "未鑑定"
    sockets = [sk.get("attr", "?") for sk in (item.get("sockets", []) or [])]
    sock_str = f" [{'-'.join(sockets)}]" if sockets else ""
    stack = item.get("stackSizeText", "")
    stack_str = f" ×{stack}" if stack else ""
    ilvl = item.get("ilvl", "")
    ilvl_str = f" | iLvl: {ilvl}" if ilvl else ""
    return f"  → {name} {t}{sock_str}{stack_str} | {rarity}{ilvl_str} | {identified}"


def cmd_public_stashes(args):
    """Monitor public stash tabs - REQUIRES OAuth."""
    params = {}
    if args.id:
        params["id"] = args.id
    data = get("/public-stash-tabs", params, require_oauth=True)
    stashes = data.get("stashes", [])
    next_id = data.get("next_change_id", "")

    if not stashes:
        print("無新資料（或已到流末端）")
        if next_id:
            print(f"下次查詢使用: --id {next_id}")
        return

    for s in stashes[: args.count]:
        acc = s.get("accountName", "?")
        stash_name = s.get("stash", "?")
        league = s.get("league", "?")
        items = s.get("items", []) or []
        action = "移除" if not s.get("public") else "上架"
        print(f"[{action}]  帳號: {acc}  |  標籤: 「{stash_name}」  |  聯盟: {league}  |  物品數: {len(items)}")
        for item in items[:10]:
            print(fmt_item(item))
        if len(items) > 10:
            print(f"  ... 還有 {len(items) - 10} 個物品")
        print()

    if next_id:
        print(f"next_change_id: {next_id}")
        print(f"（用 --id {next_id} 繼續）")


def cmd_find(args):
    """Find items in public stashes - REQUIRES OAuth."""
    next_id = None
    found = []
    league = args.league or "Settlers"
    query_name = args.name.lower()
    max_pages = args.pages

    print(f"搜尋「{args.name}」在 {league} 聯盟公開倉庫中...", file=sys.stderr)
    for _ in range(max_pages):
        params = {}
        if next_id:
            params["id"] = next_id
        data = get("/public-stash-tabs", params, require_oauth=True)
        stashes = data.get("stashes", [])
        next_id = data.get("next_change_id", "")

        if not stashes:
            break

        for s in stashes:
            if s.get("league", "").lower() != league.lower():
                continue
            if not s.get("public"):
                continue
            for item in s.get("items", []) or []:
                full_name = (item.get("name", "") + " " + item.get("typeLine", "")).lower()
                if query_name in full_name:
                    found.append((s, item))

        if not next_id:
            break

    if found:
        print(f"\n找到 {len(found)} 個結果：\n")
        seen = set()
        for stash, item in found:
            key = item.get("id", "")
            if key in seen:
                continue
            seen.add(key)
            print(f"帳號: {stash.get('accountName','?')}  |  標籤: 「{stash.get('stash','?')}」")
            print(fmt_item(item))
            print()
    else:
        print("找不到符合的物品")


def cmd_exchange(args):
    """Query currency exchange - REQUIRES OAuth."""
    params = {}
    if args.timestamp:
        params["id"] = args.timestamp
    data = get("/currency-exchange", params, require_oauth=True)
    markets = data.get("markets", [])
    next_ts = data.get("next_change_id", "")

    print(f"通貨交易所\n")
    
    # Find chaos/divine exchange rates
    divine_chaos = None
    
    for m in markets:
        market_id = m.get("market_id", "")
        if "chaos" in market_id and "divine" in market_id:
            volume = m.get("volume_traded", {})
            low_ratio = m.get("lowest_ratio", {})
            high_ratio = m.get("highest_ratio", {})
            
            chaos_vol = volume.get("chaos", 0)
            div_vol = volume.get("divine", 0)
            low_c = low_ratio.get("chaos", 0)
            high_c = high_ratio.get("chaos", 0)
            
            if "chaos|divine" in market_id:
                divine_chaos = {
                    "volume": chaos_vol,
                    "low": low_c,
                    "high": high_c
                }

    if divine_chaos:
        print(f"chaos ↔ divine")
        if divine_chaos["volume"]:
            print(f"  交易量: {int(divine_chaos['volume']):,} chaos")
        if divine_chaos["low"] and divine_chaos["high"]:
            print(f"  1 divine = {divine_chaos['low']}~{divine_chaos['high']} chaos")
    else:
        print("目前沒有 chaos/divine 交易數據")

    print(f"\n時間戳: {next_ts}")


def cmd_exchange_history(args):
    """Get historical exchange data - REQUIRES OAuth."""
    ts = int(args.timestamp)
    data = get("/currency-exchange", {"id": ts}, require_oauth=True)
    markets = data.get("markets", [])
    print(f"歷史數據 — 時間戳: {ts}")
    for m in markets[:10]:
        print(f"{m.get('market_id')}: vol={m.get('volume_traded')}")


def main():
    p = argparse.ArgumentParser(description="PoE1 Trade Monitor")
    p.add_argument("--session", help="POESESSID cookie value (may not work for all endpoints)")
    p.add_argument("--token", help="POETOKEN OAuth Bearer token (required for most endpoints)")
    
    sub = p.add_subparsers(dest="cmd")

    ps = sub.add_parser("public-stashes")
    ps.add_argument("--id")
    ps.add_argument("--count", type=int, default=10)

    f = sub.add_parser("find")
    f.add_argument("name")
    f.add_argument("--league", default="Settlers")
    f.add_argument("--rarity")
    f.add_argument("--pages", type=int, default=5)

    ex = sub.add_parser("exchange")
    ex.add_argument("--league", default="Settlers")
    ex.add_argument("--timestamp")

    exh = sub.add_parser("exchange-history")
    exh.add_argument("timestamp", help="Unix timestamp")

    args = p.parse_args()
    if args.session:
        set_auth(session_id=args.session)
    if args.token:
        set_auth(oauth_token=args.token)
    
    dispatch = {
        "public-stashes": cmd_public_stashes,
        "find": cmd_find,
        "exchange": cmd_exchange,
        "exchange-history": cmd_exchange_history,
    }
    if args.cmd in dispatch:
        try:
            dispatch[args.cmd](args)
        except Exception as e:
            print(f"錯誤: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
