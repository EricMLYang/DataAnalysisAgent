# 異常數據分析報告

**生成時間:** 2026-01-21 11:23:02

---

## 📊 總體概覽

- **總異常數:** 11
- **檢測時間範圍:** 2026-01-15 10:30:00 ~ 2026-01-15 10:36:15

## 📈 異常類型分佈

| 異常類型 | 數量 |
|---------|------|
| MISSING_VALUE | 4 |
| LOGIC_ERROR | 4 |
| OUTLIER | 3 |

## ⚡ 嚴重程度分佈

| 嚴重程度 | 數量 |
|---------|------|
| HIGH | 4 |
| MEDIUM | 3 |
| CRITICAL | 3 |
| LOW | 1 |

## 🗂️ 受影響的資料表

| 資料表 | 異常數 |
|-------|--------|
| sales | 7 |
| inventory | 4 |

## 🚨 CRITICAL 級別異常

### ORD-032

- **表名:** `sales.sale_price`
- **異常類型:** LOGIC_ERROR
- **異常值:** `-999.99`
- **預期範圍:** `> 0`
- **建議行動:** Critical: Check for data corruption

### ORD-047

- **表名:** `sales.sale_price`
- **異常類型:** OUTLIER
- **異常值:** `99999.99`
- **預期範圍:** `[10, 500]`
- **建議行動:** Critical pricing anomaly detected

### ST-02|PRD-E509

- **表名:** `inventory.on_hand`
- **異常類型:** LOGIC_ERROR
- **異常值:** `-20`
- **預期範圍:** `>= 0`
- **建議行動:** Negative inventory - immediate investigation required

## ⚠️ HIGH 級別異常

### ORD-004

- **表名:** `sales.quantity`
- **異常類型:** OUTLIER
- **異常值:** `9999`
- **建議行動:** Verify if bulk order is legitimate

### ORD-030

- **表名:** `sales.quantity`
- **異常類型:** LOGIC_ERROR
- **異常值:** `-5`
- **建議行動:** Investigate data pipeline error

### ORD-046

- **表名:** `sales.quantity`
- **異常類型:** OUTLIER
- **異常值:** `8888`
- **建議行動:** Verify bulk order authenticity

### ST-01|PRD-E509

- **表名:** `inventory.reserved`
- **異常類型:** LOGIC_ERROR
- **異常值:** `50 > 15`
- **建議行動:** Reserved exceeds available stock

---

**報告結束**
