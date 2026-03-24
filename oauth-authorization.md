# PoE OAuth 2.1 授權說明

> 來源：https://www.pathofexile.com/developer/docs/authorization

## 概述

Path of Exile 的開發者 API 使用 OAuth 2.1 框架進行授權。幾乎所有 API 都需要授權才能使用。

---

## ⚠️ 重要：OAuth 應用申請流程

**註冊 OAuth 應用需要向 GGG 申請，無法自助註冊！**

### 申請方式

發送郵件至 **[oauth@grindinggear.com](mailto:oauth@grindinggear.com?subject=OAuth%20Application)**

### 申請郵件模板

```
Subject: OAuth Application

Hi GGG Team,

I would like to request OAuth access for my application.

Account Name: <你的 PoE 帳號名稱（含四位數字）>
Application Name: <應用名稱>

Client Type: Confidential Client
Grant Types: client_credentials
Scopes Required:
- service:psapi (Public Stash API) - 用於監控公開倉庫
- service:cxapi (Currency Exchange API) - 用於查詢通貨交易所

Redirect URI: https://localhost/callback

Purpose: 
<簡短說明你的應用用途>

Thank you.
```

### 申請注意事項

⚠️ **低質量或 LLM 生成的申請會被直接拒絕！**

- 必須已閱讀並理解官方文檔
- 必須清楚說明每個 scope 的用途
- 回覆時間可能較長（特別是聯盟開始時）
- 這是低優先級請求

### 申請所需資訊

| 項目 | 說明 |
|------|------|
| PoE 帳號名稱 | 包含四位數字識別碼 |
| 應用名稱 | 你的應用/工具名稱 |
| 客戶端類型 | Confidential 或 Public |
| Grant Types | authorization_code / client_credentials |
| Scopes | 需要的權限範圍及原因 |
| Redirect URI | HTTPS URL（Confidential）或 localhost（Public） |

---

## API 政策與第三方要求

> 來源：https://www.pathofexile.com/developer/docs/index#policy

### 應用類型規範

| 類型 | 規範 |
|------|------|
| **網站/Web Apps** | ✅ 推薦 — 對用戶風險最低，憑證安全 |
| **獨立執行檔** | ⚠️ 允許但需使用 Public OAuth Client |
| **與遊戲互動的程式** | ❌ 嚴格禁止 — 違反 ToS，帳號會被終止 |

### 必須遵守的規則

#### 1. OAuth 憑證安全
- ❌ 不要分享你的憑證給任何人
- ❌ 不要在代碼中包含應用密鑰
- ❌ 不要在分發的二進制文件中嵌入密鑰
- ✅ 每個產品註冊一個應用

#### 2. User Agent 格式
```
User-Agent: OAuth {$clientId}/{$version} (contact: {$contact}) ...
```

範例：
```
User-Agent: OAuth mypoeapp/1.0.0 (contact: mypoeapp@gmail.com)
```

#### 3. 第三方聲明
所有公開應用必須在顯眼位置顯示：
```
This product isn't affiliated with or endorsed by Grinding Gear Games in any way.
```

#### 4. 速率限制
- 遵守 Response Headers 中的速率限制
- 頻繁超過限制會導致應用權限被撤銷
- 查看 `X-Rate-Limit-*` Headers 了解當前狀態

### 違規後果

- 應用訪問權限被撤銷
- 帳號被終止（嚴重違規）

---

## OAuth 伺服器端點

| 端點 | 用途 |
|------|------|
| `/oauth/authorize` | 授權頁面，獲取用戶同意 |
| `/oauth/token` | 創建 Token |
| `/oauth/token/revoke` | 撤銷 Token（需要 `oauth:revoke` scope） |
| `/oauth/token/introspect` | 檢查 Token（需要 `oauth:introspect` scope） |

## 客戶端類型

### Confidential Clients（機密客戶端）

由應用開發者控制的後端伺服器支持的客戶端。

**特性：**
- 可使用所有可用的 Grant Types
- Redirect URI 必須是 HTTPS（不接受 IP 地址或 localhost）
- Access Token 有效期：28 天
- Refresh Token 有效期：90 天
- 每個客戶端有獨立的速率限制

### Public Clients（公開客戶端）

無法安全存儲憑證的客戶端，例如桌面應用。

**特性：**
- 必須使用 Authorization Code (with PKCE) Grant
- 必須使用本地 Redirect URI（如 `http://127.0.0.1:8080/callback`）
- 無法使用 `service:*` scopes
- Access Token 有效期：10 小時
- Refresh Token 有效期：7 天
- 與所有其他公開客戶端共享速率限制
- 授權時會顯示警告訊息

## 可用 Scopes

### 帳號相關

| Scope | 說明 |
|-------|------|
| `account:profile` | 帳號基本資料 |
| `account:leagues` | 查看帳號可用的聯盟（包含私人聯盟） |
| `account:stashes` | 查看帳號的倉庫和物品 |
| `account:characters` | 查看帳號的角色和物品欄 |
| `account:league_accounts` | 查看帳號分配的 Altas 被動技能 |
| `account:item_filter` | 管理帳號的物品過濾器 |

### 服務相關

⚠️ **需要 Confidential Client + client_credentials Grant**

| Scope | 說明 |
|-------|------|
| `service:leagues` | 獲取聯盟資訊 |
| `service:leagues:ladder` | 獲取聯盟天梯 |
| `service:pvp_matches` | 獲取 PvP 比賽 |
| `service:pvp_matches:ladder` | 獲取 PvP 比賽天梯 |
| `service:psapi` | 公開倉庫 API（Public Stash API） |
| `service:cxapi` | 通貨交易所 API（Currency Exchange API） |

## Grant Types

### 1. Authorization Code (with PKCE)

用於應用需要代表用戶操作的情況。

**流程：**

1. **生成 PKCE 參數**
```python
import secrets
import base64
import hashlib

# 生成 code_verifier（至少 32 bytes）
secret = secrets.token_bytes(32)
code_verifier = base64.urlsafe_b64encode(secret).rstrip(b'=').decode()

# 生成 code_challenge
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).rstrip(b'=').decode()
```

2. **構建授權 URL**
```
https://www.pathofexile.com/oauth/authorize
  ?client_id=<YOUR_CLIENT_ID>
  &response_type=code
  &scope=account:profile
  &state=<RANDOM_STATE>
  &redirect_uri=https://example.com/callback
  &code_challenge=<CODE_CHALLENGE>
  &code_challenge_method=S256
```

3. **交換 Authorization Code 為 Token**
```bash
POST https://www.pathofexile.com/oauth/token
Content-Type: application/x-www-form-urlencoded

client_id=<CLIENT_ID>
&client_secret=<CLIENT_SECRET>
&grant_type=authorization_code
&code=<AUTHORIZATION_CODE>
&redirect_uri=https://example.com/callback
&scope=account:profile
&code_verifier=<CODE_VERIFIER>
```

**回應：**
```json
{
  "access_token": "486132c90fedb152360bc0e1aa54eea155768eb9",
  "expires_in": 2592000,
  "token_type": "bearer",
  "scope": "account:profile",
  "username": "Novynn",
  "sub": "c5b9c286-8d05-47af-be41-67ab10a8c53e",
  "refresh_token": "17abaa74e599192f7650a4b89b6e9dfef2ff68cd"
}
```

⚠️ Authorization Code 只在 30 秒內有效！

---

### 2. Client Credentials Grant

用於應用訪問與特定帳號無關的服務 API。

**本技能包使用此方法獲取 Token。**

**流程：**

```bash
POST https://www.pathofexile.com/oauth/token
Content-Type: application/x-www-form-urlencoded

client_id=<YOUR_CLIENT_ID>
&client_secret=<YOUR_CLIENT_SECRET>
&grant_type=client_credentials
&scope=service:psapi service:cxapi
```

**回應：**
```json
{
  "access_token": "cded8a4638ae9bc5fe6cd897890e25e41f0f4e21",
  "expires_in": null,
  "token_type": "bearer",
  "username": "Novynn",
  "sub": "c5b9c286-8d05-47af-be41-67ab10a8c53e",
  "scope": "service:psapi service:cxapi"
}
```

**特點：**
- Token 不會過期（`expires_in: null`）
- Token 身份設置為應用的註冊所有者
- 可在 https://www.pathofexile.com/my-account/applications 撤銷

---

### 3. Refresh Token Grant

使用 Refresh Token 獲取新的 Access Token。

```bash
POST https://www.pathofexile.com/oauth/token
Content-Type: application/x-www-form-urlencoded

client_id=<CLIENT_ID>
&client_secret=<CLIENT_SECRET>
&grant_type=refresh_token
&refresh_token=<REFRESH_TOKEN>
```

**回應：**
```json
{
  "access_token": "41bcefbc2f0d6ea0fa1cce10c435310d3c475e5b",
  "expires_in": 2592000,
  "token_type": "bearer",
  "scope": "account:profile",
  "username": "Novynn",
  "sub": "c5b9c286-8d05-47af-be41-67ab10a8c53e",
  "refresh_token": "4e9dbe97e038430bd943d35f8d5f8bef99699396"
}
```

**注意：**
- 新的 Refresh Token 會繼承舊 Token 的過期時間
- 無法延長 Refresh Token 的過期時間
- 舊的 Refresh Token 會立即失效

## 使用 Token 發送請求

在請求的 `Authorization` Header 中包含 Token：

```
Authorization: Bearer <ACCESS_TOKEN>
```

**錯誤碼：**
- `401 Unauthorized` — Token 已過期或已撤銷
- `403 Forbidden` — Token 沒有正確的 Scope

## Token 管理

- Access Token 允許訪問用戶的個人資訊，必須謹慎存儲
- 不要與任何人共享 Access Token
- 可通過 HTTPS 安全地將 Token 存儲在瀏覽器的 Cookie 或 Local Storage
- Refresh Token 必須在伺服器端安全存儲
- 用戶可隨時在 https://www.pathofexile.com/my-account/applications 查看和撤銷 Token

## 快速設置指南（本技能包）

### 步驟 1：註冊應用

1. 訪問 https://www.pathofexile.com/developer/docs/applications
2. 登入你的 Path of Exile 帳號
3. 創建新的 OAuth 應用：
   - **Name**: 自訂名稱（如 "My Trade Monitor"）
   - **Redirect URI**: 任意 HTTPS URL（Client Credentials 不需要實際跳轉）
     - 例如：`https://localhost/callback`
4. 記下 **Client ID** 和 **Client Secret**

### 步驟 2：獲取 Token

```bash
curl -X POST https://www.pathofexile.com/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=<YOUR_CLIENT_ID>" \
  -d "client_secret=<YOUR_CLIENT_SECRET>" \
  -d "grant_type=client_credentials" \
  -d "scope=service:psapi service:cxapi"
```

### 步驟 3：配置環境變數

```bash
export POETOKEN="<YOUR_ACCESS_TOKEN>"
```

或直接使用：

```bash
python3 scripts/trade_api.py --token=<YOUR_ACCESS_TOKEN> public-stashes
```

## 參考資料

- [OAuth 2.1 Authorization Framework (Draft RFC)](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13)
- [RFC 7636 - PKCE](https://tools.ietf.org/html/rfc7636)
- [RFC 6749 - OAuth 2.0](https://tools.ietf.org/html/rfc6749)
