#!/usr/bin/env python3
"""PoE1 League Tracker CLI — wraps api.pathofexile.com public endpoints."""

import argparse
import json
import sys
import urllib.request
import urllib.parse

BASE = "https://api.pathofexile.com"
HEADERS = {"User-Agent": "OpenClaw-PoE1-Skill/1.0"}


def get(path, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def fmt_league(lg):
    rules = ", ".join(r["id"] for r in (lg.get("rules") or []))
    end = lg.get("endAt", "無期限")
    return f"[{lg['id']}] {lg.get('name', '')} | 結束: {end} | 規則: {rules or '標準'}"


def fmt_entry(i, e):
    ch = e["character"]
    acc = (e.get("account") or {}).get("name", "?")
    guild = ((e.get("account") or {}).get("guild") or {}).get("tag", "")
    guild_str = f" [{guild}]" if guild else ""
    exp = ch.get("experience", "")
    exp_str = f" | EXP: {exp:,}" if exp else ""
    depth = (ch.get("depth") or {}).get("default", "")
    depth_str = f" | Delve: {depth}" if depth else ""
    dead = " 💀" if e.get("dead") else ""
    return f"#{i+1:>4}  {ch['name']}{dead} ({ch['class']}, Lv{ch['level']}) — 帳號: {acc}{guild_str}{exp_str}{depth_str}"


def cmd_leagues(args):
    params = {"realm": "pc", "type": args.type, "limit": args.limit}
    if args.season:
        params["season"] = args.season
    data = get("/league", params)
    for lg in data.get("leagues", []):
        print(fmt_league(lg))


def cmd_league(args):
    data = get(f"/league/{urllib.parse.quote(args.name)}", {"realm": "pc"})
    lg = data.get("league")
    if not lg:
        print("找不到聯盟")
        return
    print(fmt_league(lg))
    if lg.get("description"):
        print(f"說明: {lg['description']}")
    if lg.get("url"):
        print(f"論壇: {lg['url']}")


def cmd_ladder(args):
    params = {"realm": "pc", "limit": args.limit, "offset": args.offset}
    if args.sort:
        params["sort"] = args.sort
    if args.cls:
        params["sort"] = "class"
        params["class"] = args.cls
    data = get(f"/league/{urllib.parse.quote(args.name)}/ladder", params)
    ladder = data.get("ladder", {})
    total = ladder.get("total", "?")
    cached = ladder.get("cached_since", "")
    print(f"聯盟: {args.name} | 總計: {total} 名 | 快取: {cached}")
    for i, e in enumerate(ladder.get("entries", [])):
        print(fmt_entry(args.offset + i, e))


def cmd_event_ladder(args):
    params = {"realm": "pc", "limit": args.limit, "offset": args.offset}
    data = get(f"/league/{urllib.parse.quote(args.name)}/event-ladder", params)
    ladder = data.get("ladder", {})
    print(f"活動排行榜: {args.name} | 總計: {ladder.get('total', '?')}")
    for i, e in enumerate(ladder.get("entries", [])):
        pl = e.get("private_league", {})
        print(f"#{args.offset+i+1:>4}  {pl.get('name','?')} | 時間: {e.get('time','?')}s")


def cmd_pvp_matches(args):
    params = {"realm": "pc", "type": args.type}
    if args.season:
        params["season"] = args.season
    if args.league:
        params["league"] = args.league
    data = get("/pvp-match", params)
    for m in data.get("matches", []):
        status = "進行中" if m.get("inProgress") else ("即將開始" if m.get("upcoming") else "已結束")
        print(f"[{m['id']}] {m['style']} | {status} | 開始: {m.get('startAt','?')} | 結束: {m.get('endAt','?')}")


def cmd_pvp_match(args):
    data = get(f"/pvp-match/{urllib.parse.quote(args.name)}", {"realm": "pc"})
    m = data.get("match")
    if not m:
        print("找不到賽事")
        return
    print(json.dumps(m, indent=2, ensure_ascii=False))


def cmd_pvp_ladder(args):
    params = {"realm": "pc", "limit": args.limit, "offset": args.offset}
    data = get(f"/pvp-match/{urllib.parse.quote(args.name)}/ladder", params)
    ladder = data.get("ladder", {})
    print(f"PvP 排行榜: {args.name} | 總計: {ladder.get('total','?')}")
    for i, e in enumerate(ladder.get("entries", [])):
        members = ", ".join(
            f"{m['character']['name']}({m['character']['class']})"
            for m in e.get("members", [])
        )
        print(f"#{args.offset+i+1:>4}  積分: {e.get('points','?')} | 成員: {members}")


def main():
    p = argparse.ArgumentParser(description="PoE1 League Tracker")
    sub = p.add_subparsers(dest="cmd")

    # leagues
    pl = sub.add_parser("leagues")
    pl.add_argument("--type", default="main", choices=["main", "event", "season"])
    pl.add_argument("--limit", type=int, default=50)
    pl.add_argument("--season")

    # league
    pg = sub.add_parser("league")
    pg.add_argument("name")

    # ladder
    pla = sub.add_parser("ladder")
    pla.add_argument("name")
    pla.add_argument("--sort", choices=["xp", "depth", "depthsolo", "ancestor", "time", "score"])
    pla.add_argument("--class", dest="cls")
    pla.add_argument("--limit", type=int, default=20)
    pla.add_argument("--offset", type=int, default=0)

    # event-ladder
    pel = sub.add_parser("event-ladder")
    pel.add_argument("name")
    pel.add_argument("--limit", type=int, default=20)
    pel.add_argument("--offset", type=int, default=0)

    # pvp-matches
    ppm = sub.add_parser("pvp-matches")
    ppm.add_argument("--type", default="upcoming", choices=["upcoming", "season", "league"])
    ppm.add_argument("--season")
    ppm.add_argument("--league")

    # pvp-match
    ppmg = sub.add_parser("pvp-match")
    ppmg.add_argument("name")

    # pvp-ladder
    ppml = sub.add_parser("pvp-ladder")
    ppml.add_argument("name")
    ppml.add_argument("--limit", type=int, default=20)
    ppml.add_argument("--offset", type=int, default=0)

    args = p.parse_args()
    dispatch = {
        "leagues": cmd_leagues,
        "league": cmd_league,
        "ladder": cmd_ladder,
        "event-ladder": cmd_event_ladder,
        "pvp-matches": cmd_pvp_matches,
        "pvp-match": cmd_pvp_match,
        "pvp-ladder": cmd_pvp_ladder,
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
