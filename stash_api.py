#!/usr/bin/env python3
"""Poe1 Stash Manager — list and view stash tabs. Requires POESESSID."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse

BASE = "https://api.pathofexile.com"


def get_session():
    sid = os.environ.get("POESESSID")
    if not sid:
        raise SystemExit("需要設定 POESESSID 環境變數")
    return sid


def headers():
    return {"Cookie": f"POESESSID={get_session()}", "User-Agent": "OpenClaw-PoE1/1.0"}


def get(path, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(url, headers=headers())
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


STASH_TYPE_LABELS = {
    "Normal": "普通",
    "Quad": "四格",
    "DivinationCard": "命運卡",
    "UniqueFragment": "碎片",
    " essences": "精華",
    "Flask": "藥劑",
    "Currency": "通貨",
    "Map": "地圖",
    "Premium": "Premium",
}


def fmt_stash(stash, depth=0):
    prefix = "  " * depth
    stype = stash.get("type", "")
    label = STASH_TYPE_LABELS.get(stype, stype)
    parent = stash.get("parent", "")
    parent_str = f" (← {parent})" if parent else ""
    public = "🔓 公開" if stash.get("public") else "🔒 私人"
    return f"{prefix}[{label}] 「{stash.get('label','')}」 ID: {stash.get('id','')} {public}{parent_str}"


def print_stashes(stashes, depth=0):
    for s in stashes:
        print(fmt_stash(s, depth))
        for child in s.get("children", []):
            print_stashes([child], depth + 1)


def cmd_list(args):
    data = get(f"/stash/pc/{urllib.parse.quote(args.league)}")
    stashes = data.get("stashes", [])
    if not stashes:
        print("找不到倉庫或無權限")
        return
    for s in stashes:
        print(fmt_stash(s))
        for child in s.get("children", []):
            print_stashes([child], depth=1)


def cmd_get(args):
    league_enc = urllib.parse.quote(args.league)
    stash_enc = urllib.parse.quote(args.stash_id)
    path = f"/stash/pc/{league_enc}/{stash_enc}"
    if args.substash_id:
        path += f"/{urllib.parse.quote(args.substash_id)}"
    data = get(path)
    stash = data.get("stash", {})
    if not stash:
        print("找不到倉庫或無權限")
        return
    print(f"標籤: {stash.get('label','')} | 聯盟: {stash.get('league','')}")
    items = stash.get("items", []) or []
    print(f"物品數量: {len(items)}")
    for item in items:
        rarity = item.get("rarity", "")
        name = item.get("name", "")
        typeline = item.get("typeLine", "")
        identified = "已鑑定" if item.get("identified") else "未鑑定"
        sockets = []
        for sk in item.get("sockets", []) or []:
            sockets.append(sk.get("attr", "?"))
        sock_str = f" [{'-'.join(sockets)}]" if sockets else ""
        stack = item.get("stackSizeText", "")
        stack_str = f" ×{stack}" if stack else ""
        print(f"  [{rarity}] {name} {typeline}{sock_str}{stack_str} {identified}")


def cmd_guild(args):
    data = get(f"/guild/pc/stash/{urllib.parse.quote(args.league)}")
    stashes = data.get("stashes", [])
    if not stashes:
        print("找不到幫派倉庫或無權限")
        return
    for s in stashes:
        print(fmt_stash(s))


def cmd_guild_stash(args):
    path = f"/guild/pc/stash/{urllib.parse.quote(args.league)}/{urllib.parse.quote(args.stash_id)}"
    if args.substash_id:
        path += f"/{urllib.parse.quote(args.substash_id)}"
    data = get(path)
    stash = data.get("stash", {})
    if not stash:
        print("找不到倉庫或無權限")
        return
    items = stash.get("items", []) or []
    print(f"幫派倉庫: {stash.get('label','')} | 物品數量: {len(items)}")
    for item in items:
        print(f"  [{item.get('rarity','')}] {item.get('name','')} {item.get('typeLine','')}")


def main():
    p = argparse.ArgumentParser(description="PoE1 Stash Manager")
    sub = p.add_subparsers(dest="cmd")

    lst = sub.add_parser("list")
    lst.add_argument("league")
    g = sub.add_parser("get")
    g.add_argument("league")
    g.add_argument("stash_id")
    g.add_argument("substash_id", nargs="?")
    sub.add_parser("guild").add_argument("league")
    gs = sub.add_parser("guild-stash")
    gs.add_argument("league")
    gs.add_argument("stash_id")
    gs.add_argument("substash_id", nargs="?")

    args = p.parse_args()
    dispatch = {
        "list": cmd_list,
        "get": cmd_get,
        "guild": cmd_guild,
        "guild-stash": cmd_guild_stash,
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
