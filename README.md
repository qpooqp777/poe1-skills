# PoE1 Trade Monitor

Path of Exile 1 Trade Monitoring Tool — OpenClaw Skill

Monitor public stash tabs in real-time (all public tab updates), query currency exchange rates (chaos/divine conversion).

## Features

- **Public Stash Tab Monitoring** — Real-time tracking of all public stash tab changes
- **Item Search** — Search for specific items in public stashes
- **Currency Exchange** — Query chaos/divine exchange rates
- **Historical Data** — Retrieve exchange history records

## Installation

Place the entire `poe1-trade-monitor` directory into your OpenClaw skills directory:

```
~/.qclaw/skills/poe1-trade-monitor/
```

or

```
~/.openclaw/workspace/skills/poe1-trade-monitor/
```

## ⚠️ Important: OAuth Application Must Be Requested First

**Self-registration is not available!** Before using this tool, you must request an OAuth application from Grinding Gear Games.

### Application Process

1. **Send email to** [oauth@grindinggear.com](mailto:oauth@grindinggear.com?subject=OAuth%20Application)

2. **Email Template:**
   ```
   Subject: OAuth Application
   
   Account Name: <Your PoE account name (with 4-digit discriminator)>
   Application Name: <Application name>
   Client Type: Confidential Client
   Grant Types: client_credentials
   Scopes: service:psapi, service:cxapi
   Redirect URI: https://localhost/callback
   Purpose: Monitor public stashes and query currency exchange
   ```

3. **Wait for Review** — GGG will review your application (may take several weeks)

⚠️ **Note:** Low-effort or LLM-generated applications will be rejected immediately. Please read the official documentation before applying.

---

## OAuth Authentication Setup

⚠️ **All features require OAuth authentication**  
POESESSID (Cookie) cannot be used for trade monitoring features.

### Prerequisites

- ✅ OAuth application has been requested and approved by GGG
- ✅ You have received Client ID and Client Secret

### Quick Setup

1. **Get Access Token**
   ```bash
   curl -X POST https://www.pathofexile.com/oauth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "client_id=<YOUR_CLIENT_ID>" \
     -d "client_secret=<YOUR_CLIENT_SECRET>" \
     -d "grant_type=client_credentials" \
     -d "scope=service:psapi service:cxapi"
   ```

2. **Set Environment Variable**
   ```bash
   export POETOKEN="<your_access_token>"
   ```

### Required Scopes

| Scope | Description |
|-------|-------------|
| `service:psapi` | Public Stash API |
| `service:cxapi` | Currency Exchange API |

### Token Characteristics

- **Does not expire** (`expires_in: null`)
- Can be revoked anytime at https://www.pathofexile.com/my-account/applications

## Usage

### Method 1: Environment Variable

```bash
export POETOKEN="<your_oauth_token>"
python3 scripts/trade_api.py public-stashes
```

### Method 2: Command Line Parameter

```bash
python3 scripts/trade_api.py --token=<POETOKEN> public-stashes
```

## Command Examples

### Monitor Public Stash Stream

```bash
python3 scripts/trade_api.py --token=<TOKEN> public-stashes
```

Output example:
```
[上架]  Account: xyz  |  Tab: 「My Maps」  |  League: Settlers  |  Items: 24
  → Storm's Edge | Unique | iLvl: 84 | Unidentified
  → Vaal Regret  ×10

next_change_id: abc123
(Use --id abc123 to continue)
```

### Search for Specific Items

```bash
python3 scripts/trade_api.py --token=<TOKEN> find "Headhunter" --league Settlers --pages 5
```

### Query Currency Exchange

```bash
python3 scripts/trade_api.py --token=<TOKEN> exchange
```

Output example:
```
Currency Exchange

chaos ↔ divine
  Volume: 124,521 chaos
  1 divine = 140~155 chaos
```

### Query Historical Data

```bash
python3 scripts/trade_api.py --token=<TOKEN> exchange-history 1709817600
```

## API Documentation

| Document | Description |
|----------|-------------|
| `references/oauth-authorization.md` | Complete OAuth 2.1 authorization guide (includes application process, policy requirements) |
| `references/api-types.md` | API type definitions |
| [Official Docs](https://www.pathofexile.com/developer/docs/authorization) | PoE Developer Docs |

## Notes

- Public stash API has 5-minute delay
- Use `next_change_id` to continuously poll for stash changes
- **OAuth token is required to operate**

## System Requirements

- Python 3.6+
- No additional dependencies (uses standard library)

## License

MIT License

## Author

OpenClaw Community

---

**Available in other languages:**
- [繁體中文 (Traditional Chinese)](README.zh-TW.md)
