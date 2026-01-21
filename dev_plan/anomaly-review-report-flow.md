## 🎯 簡易版規劃（可行性驗證）

### 核心目標
模擬 Databricks 異常檢測→原因分析→生成報告的完整流程

### 最小可行流程（3 階段）

#### 階段 1：資料準備 (mock_data/)
```
mock_data/
├── sales.csv          # 現有
├── inventory.csv      # 現有  
└── anomaly_log.csv    # 新增（模擬異常紀錄表）
```
- **異常情境模擬**：刻意在資料中埋入 2-3 種異常（如：異常峰值、缺失值、邏輯錯誤）

#### 階段 2：技能開發 (.github/skills/)
```
先用現有的看看有沒有合適的，暫不開發
```


#### 階段 3：整合測試
```
/full-pipeline
run_name: anomaly-review-test
任務：檢測 mock_data 中所有 CSV 的異常並生成報告
```

### 預期輸出
```
runs/
└── <timestamp>-anomaly-review-test/
    ├── trace.ndjson                    # 執行記錄
    ├── detected_anomalies.json         # 檢測結果
    └── anomaly_report.csv              # 最終報告

specs/
└── anomaly-review-test.flow_spec.yaml  # 流程定義

flows/
└── anomaly-review-test/
    ├── graph.py                        # LangGraph 實作
    └── run.py                          # 執行入口
```

### 可行性關鍵驗證點
✅ **驗證 1**：Agent 能否正確調用兩個技能（detector → reporter）  
✅ **驗證 2**：trace.ndjson 是否完整記錄技能調用順序  
✅ **驗證 3**：生成的 Flow Spec 是否反映實際執行邏輯  
✅ **驗證 4**：最終報告格式是否符合 Databricks Table Schema

### 未來擴展方向（本階段不做）
- 🔮 接入真實 Databricks SQL Warehouse
- 🔮 加入 ML 模型進行根因分析
- 🔮 自動化異常通知機制

---

## 🚀 執行步驟（簡易版）

1. **準備測試資料**（5 分鐘）
   ```bash
   # 在現有 sales.csv 中人工加入異常值
   ```

2. **開發 anomaly-detector 技能**（15 分鐘）
   - 實作基礎統計檢測邏輯

3. **開發 anomaly-reporter 技能**（10 分鐘）
   - 實作簡單的格式化輸出

4. **執行一鍵測試**（2 分鐘）
   ```
   /full-pipeline
   run_name: anomaly-review-test
   任務：分析 mock_data/sales.csv，找出異常值並生成報告
   ```

5. **檢視結果**（3 分鐘）
   - 確認報告格式正確
   - 驗證 trace → spec → flow 轉換成功

**總耗時預估：~35 分鐘**