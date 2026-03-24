# PoE1 Skills — Path of Exile 1 API Skills for OpenClaw

4 OpenClaw skill packages for Path of Exile 1, powered by the official GGG API.

## Skills

| Skill | File | Description |
|---|---|---|
| poe1-league-tracker | `poe1-league-tracker.skill` | League list, ladder rankings, PvP events |
| poe1-character-viewer | `poe1-character-viewer.skill` | Character list, equipment, passive tree |
| poe1-stash-manager | `poe1-stash-manager.skill` | Stash tabs, guild stashes |
| poe1-trade-monitor | `poe1-trade-monitor.skill` | Public stash stream, currency exchange |

## Installation

```bash
openclaw skills install poe1-league-tracker
openclaw skills install poe1-character-viewer
openclaw skills install poe1-stash-manager
openclaw skills install poe1-trade-monitor
```

## Authentication

### POESESSID (required for account endpoints)
1. Log in to [pathofexile.com](https://www.pathofexile.com)
2. F12 → Application → Cookies → `https://www.pathofexile.com`
3. Copy the `POESESSID` value

```bash
export POESESSID="your_session_id"
export POE_TOKEN="Bearer your_oauth_token"  # optional, more secure
```

### Free Endpoints (no auth needed)
- League list & details
- Public stash stream
- Currency exchange

### Auth Required
- Character equipment
- Stash tabs
- Item filters

## Quick Start

```bash
# List leagues
python3 poe_api.py leagues

# View character equipment
POESESSID=xxx python3 character_api.py gear "MyCharacter"

# Search public stashes
python3 trade_api.py find "Headhunter" --league "Mirage"

# Check currency exchange
python3 trade_api.py exchange --league "Mirage"
```

## License
MIT
