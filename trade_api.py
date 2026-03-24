#!/usr/bin/env python3
"""PoE1 Trade Monitor — public stash stream & currency exchange. No auth needed."""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import time

BASE = "https://api.pathofexile.com"
HEADERS = {"User-Agent": "OpenClaw-PoE1-Skill/1.0"}


def get(path, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def fmt_item(item):
    rarity = item.get("rarity", "")
    name = item.get("name", "")
    t = item.get("typeLine", "")
    identified = "已鑑定" if item.get("identified") else "未鑑定"
    sockets = [sk.get("attr", "?") for sk in (item.get("sockets") or [])]
    sock_str = f" [{'-'.join(sockets)}]" if sockets else ""
    stack = item.get("stackSizeText", "")
    stack_str = f" ×{stack}" if stack else ""
    ilvl = item.get("ilvl", "")
    ilvl_str = f" | iLvl: {ilvl}" if ilvl else ""
    return f"  → {name} {t}{sock_str}{stack_str} | {rarity}{ilvl_str} | {identified}"


def cmd_public_stashes(args):
    params = {}
    if args.id:
        params["id"] = args.id
    data = get("/public-stash-tabs", params)
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
        stype = s.get("stashType", "?")
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
    # Fetch multiple pages to find the item
    next_id = None
    found = []
    league = args.league or "Affliction"
    query_name = args.name.lower()
    max_pages = args.pages

    print(f"搜尋「{args.name}」在 {league} 聯盟公開倉庫中...", file=sys.stderr)
    for _ in range(max_pages):
        params = {}
        if next_id:
            params["id"] = next_id
        data = get("/public-stash-tabs", params)
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
    league = args.league or "Affliction"
    params = {}
    if args.timestamp:
        params["id"] = args.timestamp
    data = get("/currency-exchange/pc", params)
    markets = data.get("markets", [])
    next_ts = data.get("next_change_id", "")

    # Filter for relevant pairs
    relevant = [m for m in markets if m.get("league") == league]
    if not relevant:
        relevant = markets

    print(f"通貨交易所 — 聯盟: {league} | 查詢時間戳: {next_ts}\n")
    for m in relevant:
        mid = m.get("market_id", "")
        vol = m.get("volume_traded", {})
        low_ratio = m.get("lowest_ratio", {})
        high_ratio = m.get("highest_ratio", {})

        # Find chaos<->divine details
        chaos_vol = vol.get("chaos", "")
        div_vol = vol.get("divine", "")
        low_c = low_ratio.get("chaos", "")
        high_c = high_ratio.get("chaos", "")
        low_d = low_ratio.get("divine", "")
        high_d = high_ratio.get("divine", "")

        if "chaos" in mid and "divine" in mid:
            print(f"chaos ↔ divine")
            if chaos_vol:
                print(f"  交易量: {int(chaos_vol):,} chaos")
            if low_c and high_c:
                print(f"  1 divine = {low_c}~{high_c} chaos")
            if low_d and high_d:
                print(f"  1 chaos = {low_d}~{high_d} divine")
        else:
            print(f"{mid}: 交易量 chaos={int(chaos_vol):,}" if chaos_vol else f"{mid}")

    print(f"\nnext_change_id: {next_ts}")


def cmd_exchange_history(args):
    ts = int(args.timestamp)
    data = get("/currency-exchange/pc", {"id": ts})
    markets = data.get("markets", [])
    print(f"歷史數據 — 時間戳: {ts}")
    for m in markets[:10]:
        print(f"{m.get('market_id')}: vol={m.get('volume_traded')}")


def main():
    p = argparse.ArgumentParser(description="PoE1 Trade Monitor")
    sub = p.add_subparsers(dest="cmd")

    ps = sub.add_parser("public-stashes")
    ps.add_argument("--id")
    ps.add_argument("--count", type=int, default=10)

    f = sub.add_parser("find")
    f.add_argument("name")
    f.add_argument("--league", default="Affliction")
    f.add_argument("--rarity")
    f.add_argument("--pages", type=int, default=5)

    ex = sub.add_parser("exchange")
    ex.add_argument("--league", default="Affliction")
    ex.add_argument("--timestamp")

    exh = sub.add_parser("exchange-history")
    exh.add_argument("timestamp", help="Unix timestamp")

    args = p.parse_args()
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
