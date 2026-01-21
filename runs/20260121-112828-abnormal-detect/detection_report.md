# 智能異常檢測報告

**生成時間:** 2026-01-21 11:30:03
**檢測範圍:** Sales + Inventory 數據

---

## 📊 檢測概覽

- **總異常數:** 12
- **檢測類別:** 4 種
- **嚴重程度:** 4 級

## ⚡ 嚴重程度分佈

| 嚴重程度 | 數量 | 百分比 |
|---------|------|--------|
| CRITICAL | 5 | 41.7% |
| HIGH | 3 | 25.0% |
| MEDIUM | 3 | 25.0% |
| LOW | 1 | 8.3% |

## 📈 異常類別分佈

| 異常類別 | 數量 | 說明 |
|---------|------|------|
| DATA_QUALITY | 4 | 數據質量問題（缺失值等） |
| LOGIC_ERROR | 3 | 邏輯錯誤（負值等） |
| OUTLIER | 3 | 統計異常值 |
| BUSINESS_LOGIC | 2 | 業務邏輯錯誤 |

## 📦 Sales 數據統計

- **總記錄數:** 50
- **時間範圍:** 2026-01-01 09:15:30 ~ 2026-01-10 16:30:35
- **總營收:** $107,161.35
- **平均售價:** $2232.53
- **產品種類:** 7
- **商店數量:** 3
- **數據質量問題:** 缺失數量 1, 缺失價格 1
- **邏輯錯誤:** 負數量 1, 負價格 1

## 📊 Inventory 數據統計

- **總記錄數:** 30
- **總庫存量:** 1406.0
- **總預留量:** 410.0
- **產品種類:** 7
- **商店數量:** 3
- **數據質量問題:** 缺失庫存 1, 缺失預留 1
- **業務邏輯錯誤:** 2 筆

## 🚨 CRITICAL 級別異常

### ORD-032

- **表:** `sales.sale_price`
- **類別:** LOGIC_ERROR
- **問題:** Negative price - data corruption
- **異常值:** `-999.99`
- **預期:** `> 0`

### ORD-004

- **表:** `sales.quantity`
- **類別:** OUTLIER
- **問題:** Extreme quantity outlier
- **異常值:** `9999.0`
- **預期:** `[-7.0, 14.0]`

### ORD-046

- **表:** `sales.quantity`
- **類別:** OUTLIER
- **問題:** Extreme quantity outlier
- **異常值:** `8888.0`
- **預期:** `[-7.0, 14.0]`

### ORD-047

- **表:** `sales.sale_price`
- **類別:** OUTLIER
- **問題:** Extreme price outlier
- **異常值:** `99999.99`
- **預期:** `[-254.5, 540.9]`

### ST-02|PRD-E509

- **表:** `inventory.on_hand`
- **類別:** LOGIC_ERROR
- **問題:** Negative inventory - critical issue
- **異常值:** `-20.0`
- **預期:** `>= 0`


## ⚠️ HIGH 級別異常

### ORD-030

- **表:** `sales.quantity`
- **類別:** LOGIC_ERROR
- **問題:** Negative quantity
- **異常值:** `-5.0`

### ST-01|PRD-E509

- **表:** `inventory.reserved`
- **類別:** BUSINESS_LOGIC
- **問題:** Reserved exceeds available stock
- **異常值:** `reserved=50.0, on_hand=15.0`

### ST-02|PRD-E509

- **表:** `inventory.reserved`
- **類別:** BUSINESS_LOGIC
- **問題:** Reserved exceeds available stock
- **異常值:** `reserved=8.0, on_hand=-20.0`


## 💡 建議行動

### 🔴 緊急處理

1. 立即調查所有 CRITICAL 級別異常
2. 檢查數據管道是否有損壞
3. 驗證資料來源系統的正確性

### 🟡 優先處理

1. 審查 HIGH 級別異常的業務合理性
2. 確認異常值是否為真實業務場景
3. 若為錯誤，回溯修正數據

### 🔵 持續改善

1. 建立自動化數據質量監控
2. 在數據輸入端加強驗證規則
3. 定期執行異常檢測報告

---

**報告結束**
