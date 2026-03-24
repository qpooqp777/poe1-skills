#!/usr/bin/env python3
"""PoE1 Character Viewer — requires POESESSID or OAuth token."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse

BASE = "https://api.pathofexile.com"


def get_token():
    token = os.environ.get("POE_TOKEN") or os.environ.get("POE_SESSION")
    if not token:
        raise SystemExit("需要設定 POE_TOKEN 或 POESESSID 環境變數")
    return token


def headers():
    token = get_token()
    if token.startswith("Bearer "):
        return {"Authorization": token, "User-Agent": "OpenClaw-PoE1/1.0"}
    return {"Cookie": f"POESESSID={token}", "User-Agent": "OpenClaw-PoE1/1.0"}


def get(path, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(url, headers=headers())
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def fmt_character(c):
    status = "💀 死亡" if c.get("dead") else "✓ 存活"
    league = c.get("league", "?")
    return f"{c['name']:<20} {c['class']:<10} Lv{c['level']:<4} {league:<20} {status}"


def cmd_list(_args):
    data = get("/character")
    chars = data.get("characters", [])
    print(f"{'角色名':<20} {'職業':<10} {'等級'} {'聯盟':<20} 狀態")
    print("-" * 75)
    for c in chars:
        print(fmt_character(c))


def cmd_get(args):
    name_enc = urllib.parse.quote(args.name)
    data = get(f"/character/pc/{name_enc}")
    ch = data.get("character")
    if not ch:
        print("找不到角色或無權限查看")
        return
    print(json.dumps(ch, indent=2, ensure_ascii=False))


def cmd_gear(args):
    name_enc = urllib.parse.quote(args.name)
    data = get(f"/character/pc/{name_enc}")
    ch = data.get("character")
    if not ch:
        print("找不到角色或無權限查看")
        return
    equip = ch.get("equipment", []) or []
    slots = {}
    for item in equip:
        slot = item.get("slot", "unknown")
        slots.setdefault(slot, []).append(item)

    for slot, items in slots.items():
        print(f"\n[{slot}]")
        for item in items:
            icon = item.get("icon", "")[:60]
            print(f"  {item.get('name','')} {item.get('typeLine','')}")
            if icon:
                print(f"  圖示: {icon}")


def cmd_passives(args):
    name_enc = urllib.parse.quote(args.name)
    data = get(f"/character/pc/{name_enc}")
    ch = data.get("character")
    if not ch:
        print("找不到角色或無權限查看")
        return
    passive = ch.get("passives", {})
    print(f"被動技能樹 ID 總數: {passive.get('hashes', [])[:10]}... (共 {len(passive.get('hashes',[]))} 個)")
    if passive.get("mastery_effects"):
        print(f"天賦效果: {passive['mastery_effects']}")
    jewels = ch.get("jewels", []) or []
    print(f"珠寶: {len(jewels)} 個")
    for j in jewels[:5]:
        print(f"  - {j.get('name','')} {j.get('typeLine','')}")


def main():
    p = argparse.ArgumentParser(description="PoE1 Character Viewer")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("list")
    g = sub.add_parser("get")
    g.add_argument("name")
    g2 = sub.add_parser("gear")
    g2.add_argument("name")
    g3 = sub.add_parser("passives")
    g3.add_argument("name")

    args = p.parse_args()
    dispatch = {"list": cmd_list, "get": cmd_get, "gear": cmd_gear, "passives": cmd_passives}
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
