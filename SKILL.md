---
name: poe1-trade-monitor
description: Path of Exile 1 交易監控工具。追蹤公開倉庫流（所有公開標籤的即時更新）、查詢通貨交易所行情（chaos/divine 兌換比率）。適用於：拍賣行行情、監控特定物品上架、通貨比率查詢。**不需要認證**（公開數據）。
---

# PoE1 Trade Monitor

Base URL: `https://api.pathofexile.com`  
**不需要認證**：所有端點均為公開數據

## Workflows

### 1. 監控公開倉庫流
```bash
python3 scripts/trade_api.py public-stashes [--id <next_change_id>] [--count 5]
```
- 預設只取第一批（約 40 個倉庫變更）
- `next_change_id`：用於分頁，接上次結果的 `next_change_id` 繼續
- 持續輪詢可追蹤新上架物品

### 2. 找特定物品
```bash
python3 scripts/trade_api.py find "<item_name>" [--league <league>] [--rarity unique|rare]
```
從公開倉庫流中搜尋包含指定名稱的物品。

### 3. 查詢通貨交易所
```bash
python3 scripts/trade_api.py exchange [--league <league>]
```
回傳：chaos↔divine 比率、交易量、最低/最高庫存

### 4. 查詢交易所歷史（指定小時）
```bash
python3 scripts/trade_api.py exchange-history "<unix_timestamp>"
```

## Output Format

公開倉庫變更範例：
```
[新增] 帳號: xyz  |  標籤: "My Maps"  |  聯盟: Affliction  |  物品數: 24
  → Storm's Edge | Unique | iLvl: 84 | 未鑑定
  → Vaal Regret  ×10
```

通貨交易所範例：
```
chaos|divine  交易量: 124,521 chaos | 比率: 1 div = 140~155 chaos
```

## Notes
- 公開倉庫 API 有 5 分鐘延遲
- 使用 `next_change_id` 持續輪詢以追蹤倉庫變化
- 詳細 Item 結構見 `references/item-types.md`
