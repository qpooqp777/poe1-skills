# PoE1 Trade Monitor

Path of Exile 1 交易監控工具 — OpenClaw Skill

追蹤公開倉庫流（所有公開標籤的即時更新）、查詢通貨交易所行情（chaos/divine 兌換比率）。

## 功能

- **公開倉庫流監控** — 即時追蹤所有公開倉庫標籤的變更
- **物品搜尋** — 在公開倉庫中搜尋特定物品
- **通貨交易所** — 查詢 chaos/divine 兌換比率
- **歷史數據** — 獲取交易所歷史記錄

## 安裝

將整個 `poe1-trade-monitor` 目錄放入你的 OpenClaw skills 目錄：

```
~/.qclaw/skills/poe1-trade-monitor/
```

或

```
~/.openclaw/workspace/skills/poe1-trade-monitor/
```

## OAuth 認證設置

⚠️ **所有功能都需要 OAuth 認證**  
POESESSID (Cookie) 無法用於交易監控功能。

### 快速設置

1. **註冊 OAuth 應用**
   - 訪問 https://www.pathofexile.com/developer/docs/applications
   - 創建新的 OAuth 應用（Redirect URI 可填任意 HTTPS URL）
   - 記下 Client ID 和 Client Secret

2. **獲取 Access Token**
   ```bash
   curl -X POST https://www.pathofexile.com/oauth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "client_id=<YOUR_CLIENT_ID>" \
     -d "client_secret=<YOUR_CLIENT_SECRET>" \
     -d "grant_type=client_credentials" \
     -d "scope=service:psapi service:cxapi"
   ```

3. **配置環境變數**
   ```bash
   export POETOKEN="<your_access_token>"
   ```

### 所需 Scopes

| Scope | 說明 |
|-------|------|
| `service:psapi` | 公開倉庫 API |
| `service:cxapi` | 通貨交易所 API |

### Token 特性

- **不會過期**（`expires_in: null`）
- 可隨時在 https://www.pathofexile.com/my-account/applications 撤銷

## 使用方式

### 方法 1：環境變數

```bash
export POETOKEN="<your_oauth_token>"
python3 scripts/trade_api.py public-stashes
```

### 方法 2：命令行參數

```bash
python3 scripts/trade_api.py --token=<POETOKEN> public-stashes
```

## 命令範例

### 監控公開倉庫流

```bash
python3 scripts/trade_api.py --token=<TOKEN> public-stashes
```

輸出範例：
```
[上架]  帳號: xyz  |  標籤: 「My Maps」  |  聯盟: Settlers  |  物品數: 24
  → Storm's Edge | Unique | iLvl: 84 | 未鑑定
  → Vaal Regret  ×10

next_change_id: abc123
（用 --id abc123 繼續）
```

### 搜尋特定物品

```bash
python3 scripts/trade_api.py --token=<TOKEN> find "Headhunter" --league Settlers --pages 5
```

### 查詢通貨交易所

```bash
python3 scripts/trade_api.py --token=<TOKEN> exchange
```

輸出範例：
```
通貨交易所

chaos ↔ divine
  交易量: 124,521 chaos
  1 divine = 140~155 chaos
```

### 查詢歷史數據

```bash
python3 scripts/trade_api.py --token=<TOKEN> exchange-history 1709817600
```

## API 文檔

- **OAuth 2.1 授權** — `references/oauth-authorization.md`
- **API 類型定義** — `references/api-types.md`
- **官方文檔** — https://www.pathofexile.com/developer/docs/authorization

## 注意事項

- 公開倉庫 API 有 5 分鐘延遲
- 使用 `next_change_id` 持續輪詢以追蹤倉庫變化
- **必須使用 OAuth token 才能運作**

## 系統需求

- Python 3.6+
- 無額外依賴（使用標準庫）

## License

MIT License

## 作者

OpenClaw Community
