# PoE1 Skills — Path of Exile 1 API Skills for OpenClaw

OpenClaw skill packages for Path of Exile 1, powered by the official GGG API (`api.pathofexile.com`).

## 📦 Skills

| Skill | Description | Auth |
|---|---|---|
| **poe1-league-tracker** | League list, ladder rankings, PvP events | Free |
| **poe1-character-viewer** | Character equipment, passive tree | POESESSID |
| **poe1-stash-manager** | Stash tabs, guild stashes | POESESSID |
| **poe1-trade-monitor** | Public stash stream, currency exchange | Free |

## 🔧 Installation

Download the `.skill` files and install to your OpenClaw skills directory:

```bash
# Or install via openclaw skills CLI
openclaw skills install poe1-league-tracker
openclaw skills install poe1-character-viewer
openclaw skills install poe1-stash-manager
openclaw skills install poe1-trade-monitor
```

## 🔑 Authentication

### Get POESESSID
1. Log in to [pathofexile.com](https://www.pathofexile.com)
2. Press **F12** → **Application** → **Cookies** → `https://www.pathofexile.com`
3. Copy the `POESESSID` value

```bash
export POESESSID="your_session_id"
export POE_TOKEN="Bearer your_oauth_token"  # optional, more secure
```

## 📁 File Structure

```
poe1-league-tracker/   ← League + Ladder API
poe1-character-viewer/ ← Character equipment + passives
poe1-stash-manager/    ← Stash tabs management
poe1-trade-monitor/    ← Public stash stream + currency
```

## 📄 License
MIT
