# Copilot 開發任務：Data Fetch Agent Skill（MVP）

## 目標
把「撈取 mock data」做成 `.github/skills` 的 Agent Skill。  
輸入：task text（使用者指令文字）  
輸出：JSON profile（供後續異常彙整使用）  
> Trace 已完成，不在本任務範圍內（可自行在關鍵步驟呼叫既有 trace logger）。

---

## 交付物（必做）
建立/新增以下檔案與資料夾：

```txt
.github/
  skills/
    data-fetch/
      SKILL.md
      scripts/
        fetch.py
mock_data/
  sales.csv
  inventory.csv   # 可選（建議做）
```

---

## 規格（MVP）

### Dataset registry（常數 mapping）
- `sales` -> `mock_data/sales.csv`
- `inventory` -> `mock_data/inventory.csv`
- `default` -> `mock_data/sales.csv`

### Task parser（最簡單 keyword）
- task text 含 `inventory` -> dataset_key = inventory
- 含 `sales` -> dataset_key = sales
- 否則 -> dataset_key = default

### Loader
- 只支援 CSV（pandas read_csv）
- 只能讀 repo 內 `mock_data/`（不得下載外部資料）
- dataset 不存在要回清楚錯誤（非靜默失敗）

### JSON 輸出 schema（stdout 必須符合）
- `dataset_key`: `sales|inventory|default`
- `path`: string（實際讀取路徑）
- `rows`: int
- `cols`: int
- `dtypes`: `{col: dtype_str}`
- `null_counts`: `{col: int}`
- `sample_head`: `[ {col: value, ...}, ... ]`（前 5 列）
- 若存在 `ts` 欄位且可 parse：加上 `min_ts`, `max_ts`（string）

---

## 任務清單（照順序做）

### Task A — 準備 mock data
1. 建立 `mock_data/sales.csv`（至少 50 筆）
   - 欄位建議：`order_id, store_id, ts, product_id, quantity, sale_price`
2. （建議）建立 `mock_data/inventory.csv`（至少 30 筆）
   - 欄位建議：`store_id, ts, product_id, on_hand, reserved`

驗收：
- `python -c "import pandas as pd; print(pd.read_csv('mock_data/sales.csv').head())"` 可成功
- 若有 inventory：同上也可成功

---

### Task B — 建立 Skill 說明文件
新增 `.github/skills/data-fetch/SKILL.md`，需包含：
- YAML frontmatter：
  - `name: data-fetch`
  - `description: Load mock CSV datasets from mock_data/ based on task text and output a JSON profile for downstream analysis.`
- What this skill does / When to use / Steps
- 執行指令：
  ```bash
  python .github/skills/data-fetch/scripts/fetch.py --task "<task text>"
  ```
- Output JSON schema（貼上本文件的 schema）

驗收：
- SKILL.md 存在且 frontmatter 正確
- 指令與輸出格式描述清楚

---

### Task C — 實作 fetch 腳本
新增 `.github/skills/data-fetch/scripts/fetch.py`，需包含：
- CLI 參數：
  - `--task`（必填）
  - `--save`（可選，預設 `data_fetch_profile.json`；若為空字串則不存檔）
- 功能：
  1. `parse_dataset_key(task_text)`：依「規格（MVP）」判斷 dataset_key
  2. registry mapping：依 dataset_key 取得 path
  3. `pandas.read_csv(path)` 讀取成 df
  4. `profile_df(df)` 產出 schema 欄位
     - `rows, cols, dtypes, null_counts, sample_head`
     - 若有 `ts`：best-effort `to_datetime(errors='coerce')`，輸出 `min_ts/max_ts`（若可用）
  5. stdout 印 JSON（確保可 JSON 序列化，`ensure_ascii=False`）
  6. （可選）寫入 `--save` 指定檔名

驗收：
- `python .github/skills/data-fetch/scripts/fetch.py --task "撈 sales 資料"` 可成功輸出 JSON
- 缺檔時（例如 inventory.csv 不存在但 task 指向 inventory）會明確報錯

---

### Task D — 最小測試（3 cases）
1. `--task "撈 sales 資料"`
2. `--task "讀 inventory 看看"`（若 inventory.csv 有做）
3. `--task "先把資料抓出來"`（default -> sales）

驗收：
- Case 1 path 指向 `mock_data/sales.csv`
- Case 2 path 指向 `mock_data/inventory.csv`（若存在）
- Case 3 path 指向 default（sales）
- JSON schema 完整且可被後續異常彙整直接使用
