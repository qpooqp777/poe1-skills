---
name: poe1-trade-monitor
description: Path of Exile 1 交易監控工具。追蹤公開倉庫流（所有公開標籤的即時更新）、查詢通貨交易所行情（chaos/divine 兌換比率）。適用於：拍賣行行情、監控特定物品上架、通貨比率查詢。**需要 OAuth token**。
---

# PoE1 Trade Monitor

Base URL: `https://api.pathofexile.com`

## 認證設定

### 方法 1: 命令行參數（推薦）
```bash
python3 scripts/trade_api.py --token=<POETOKEN> <command>
```

### 方法 2: 環境變數
```bash
export POETOKEN="<your_oauth_token>"
```

## 重要說明

⚠️ **所有功能都需要 OAuth 認證**
POESESSID (Cookie) 無法用於交易監控功能，請使用 OAuth token。

### 獲取 OAuth Token（Client Credentials 流程）

本工具使用 **Client Credentials Grant**，適用於服務類 API（公開倉庫、通貨交易所）。

#### 步驟 1：註冊 OAuth 應用
1. 訪問 https://www.pathofexile.com/developer/docs/applications
2. 登入你的 Path of Exile 帳號
3. 創建新的 OAuth 應用：
   - **Name**: 自訂名稱（如 "My Trade Monitor"）
   - **Redirect URI**: 填寫任意 HTTPS URL（Client Credentials 不需要實際跳轉）
     - 例如：`https://localhost/callback`
4. 記下你的 **Client ID** 和 **Client Secret**

#### 步驟 2：使用 Client Credentials 獲取 Token
```bash
curl -X POST https://www.pathofexile.com/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=<YOUR_CLIENT_ID>" \
  -d "client_secret=<YOUR_CLIENT_SECRET>" \
  -d "grant_type=client_credentials" \
  -d "scope=service:psapi service:cxapi"
```

#### 步驟 3：從回應中提取 Token
```json
{
  "access_token": "cded8a4638ae9bc5fe6cd897890e25e41f0f4e21",
  "expires_in": null,
  "token_type": "bearer",
  "scope": "service:psapi service:cxapi"
}
```

`access_token` 就是你需要的 OAuth token。

### 所需 Scopes
- `service:psapi` — 公開倉庫 API（Public Stash API）
- `service:cxapi` — 通貨交易所 API（Currency Exchange API）

### Token 特性
- **不會過期**（`expires_in: null`）
- 可隨時在 https://www.pathofexile.com/my-account/applications 撤銷

## Workflows

### 1. 監控公開倉庫流
```bash
python3 scripts/trade_api.py --token=<POETOKEN> public-stashes [--id <next_change_id>] [--count 5]
```
- 預設只取第一批（約 40 個倉庫變更）
- `next_change_id`：用於分頁，接上次結果的 `next_change_id` 繼續
- 持續輪詢可追蹤新上架物品

### 2. 找特定物品
```bash
python3 scripts/trade_api.py --token=<POETOKEN> find "<item_name>" [--league <league>] [--rarity unique|rare] [--pages 5]
```
從公開倉庫流中搜尋包含指定名稱的物品。

### 3. 查詢通貨交易所
```bash
python3 scripts/trade_api.py --token=<POETOKEN> exchange [--league <league>]
```
回傳：chaos↔divine 比率、交易量、最低/最高庫存

### 4. 查詢交易所歷史（指定小時）
```bash
python3 scripts/trade_api.py --token=<POETOKEN> exchange-history "<unix_timestamp>"
```

## Output Format

公開倉庫變更範例：
```
[新增] 帳號: xyz  |  標籤: "My Maps"  |  聯盟: Settlers  |  物品數: 24
  → Storm's Edge | Unique | iLvl: 84 | 未鑑定
  → Vaal Regret  ×10
```

通貨交易所範例：
```
通貨交易所

chaos ↔ divine
  交易量: 124,521 chaos
  1 divine = 140~155 chaos
```

## Notes
- 公開倉庫 API 有 5 分鐘延遲
- 使用 `next_change_id` 持續輪詢以追蹤倉庫變化
- **必須使用 OAuth token 才能運作**
- 詳細 Item 結構見 `references/item-types.md`

## References
- OAuth 2.1 完整授權流程：`references/oauth-authorization.md`
- API 類型定義：`references/api-types.md`
- PoE 官方文檔：https://www.pathofexile.com/developer/docs/authorization
