# PoE1 API 類型定義

## League
```json
{
  "id": "string",
  "realm": "pc | xbox | sony",
  "name": "string",
  "description": "string?",
  "category": { "id": "string", "current": true },
  "rules": [{ "id": "string", "name": "string", "description": "string?" }],
  "registerAt": "ISO8601",
  "startAt": "ISO8601",
  "endAt": "ISO8601",
  "event": true,
  "timedEvent": true,
  "scoreEvent": true,
  "delveEvent": true
}
```

## LadderEntry
```json
{
  "rank": 1,
  "dead": true,
  "retired": true,
  "character": {
    "id": "64位十六進制",
    "name": "string",
    "level": 100,
    "class": "Witch | Ranger | ..." ,
    "time": 3600,
    "score": 10,
    "experience": 4250334444,
    "depth": { "default": 200, "solo": 180 }
  },
  "account": {
    "name": "string",
    "realm": "string",
    "guild": { "id": 1, "name": "string", "tag": "[TAG]" },
    "challenges": { "set": "set_id", "completed": 40, "max": 40 },
    "twitch": { "name": "string", "stream": { "name": "string", "image": "url", "status": "string" } }
  }
}
```

## Character
```json
{
  "name": "string",
  "league": "string",
  "class": "string",
  "level": 100,
  "level": 100,
  "experience": 4250334444,
  "dead": false,
  "equipment": [Item],
  "inventory": [Item],
  "passives": {
    "hashes": [int],
    "mastery_effects": []
  },
  "jewels": [Item]
}
```

## Item
```json
{
  "id": "64位十六進制",
  "name": "string",
  "typeLine": "string",
  "baseType": "string",
  "rarity": "Normal | Magic | Rare | Unique",
  "identified": true,
  "ilvl": 84,
  "verified": true,
  "w": 1,
  "h": 1,
  "icon": "https://web.poecdn.com/...",
  "league": "string",
  "stackSize": 10,
  "maxStackSize": 20,
  "stackSizeText": "10 / 20",
  "sockets": [{ "attr": "S|R|G|B|W|D", "sColour": "R" }],
  "socketedItems": [Item],
  "note": "string",
  "influences": { "elder": true, "shaper": false },
  "fractured": true,
  "synthesised": true,
  "delve": true,
  "abyssJewel": true,
  "builtInSupport": "Level 1 Melee Splash"
}
```

## StashTab
```json
{
  "id": "string (public id)",
  "parent": "string?",
  "label": "string",
  "type": "Normal | Quad | DivinationCard | Currency | Map | ..." ,
  "public": true,
  "children": [StashTab],
  "items": [Item]
}
```
