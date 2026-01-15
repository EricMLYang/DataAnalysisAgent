可以再更極簡，而且做到你要的「**我在對話框說：請記錄** → 之後每動一步都要記下來」。

先講清楚一件事：**Copilot 不會因為你在 Chat 視窗打一句話就自動幫你寫檔**（它沒有那種“系統級自動錄影”）。但你可以用一個很可靠的方法達到同樣效果：

> **把「請記錄」變成 repo 的硬規則 + 提供一個 1 行就能寫 log 的小工具**
> 只要你在對話框跟 Copilot 說「請記錄」，它就會照規則用那個工具一直寫下去。

下面是最小化版本（資料夾/程式都最少）。

---

## 最小 Repo 長相（2 個資料夾 + 1 個檔案）

```
your-repo/
  agent_trace.py        # 唯一的程式：負責 append trace.ndjson
  runs/                 # 放執行紀錄（建議 gitignore）
```

`.gitignore`（建議）：

```
runs/**
!runs/.gitkeep
```

---

## 你要的「請記錄」行為怎麼做（最小工作流）

你每次在 Copilot Chat 下指令時，用這個開頭：

> **請記錄：ON**
> run_name: `<你自己取名>`
> 任務：……（你要它做的事）

**規則**（你要 Copilot 遵守）：

1. 看到「請記錄：ON」就建立一個新的 run 檔：
   `runs/<YYYYMMDD-HHMMSS>-<run_name>/trace.ndjson`
2. 從那一刻起，它每做一個動作（計劃、找工具、用工具、找 prompt、準備步驟、執行步驟、錯誤、摘要）都要 append 一行 JSON 到 `trace.ndjson`
3. 任務結束要寫 `summary` 事件

你會得到你想要的「計劃→嘗試→失敗→改策略」的外顯紀錄，而且能一直累積，之後搬 Databricks 也能沿用這種 trace。

---

## 最小事件清單（你要求的那些）

我建議先固定這幾種（越少越好，先能用）：

* `plan`：它打算怎麼做（列 3–8 步）
* `tool_search`：它在找什麼工具/指令
* `tool_use`：用了什麼工具（命令、檔案、function）
* `tool_result`：工具回傳/結果（成功/失敗/關鍵輸出）
* `prompt_search`：它去翻哪個 prompt / instruction（檔名/段落）
* `step_prepare`：準備跑某一步（輸入、假設、預期輸出）
* `step_execute`：開始/結束某步（可用 data 記 status）
* `strategy_shift`：找不到/失敗所以改方案（from/to + 原因）
* `error`
* `summary`

---

## 你要 Copilot「怎麼知道要記錄」：一段超短規則（直接貼給它）

你每次只要在 Copilot Chat 多貼這段一次，它就會照做（或你把它存成 repo 的 `README` / `docs` 給它參考）：

```text
當我訊息中包含「請記錄：ON」：
1) 在 runs/ 下建立新的資料夾 runs/<timestamp>-<run_name>/ ，並建立 trace.ndjson
2) 從現在開始，你每做一個動作都要呼叫 agent_trace.py 追加一行事件到 trace.ndjson
3) 事件至少包含：ts, type, message, data
4) 任務結束必須寫 summary 事件
如果沒有 trace.ndjson 或缺少 plan+summary，視為任務未完成。
```

---

## 最小計劃（Coding Agent 照著做就能完成）

1. 建立 `runs/` 資料夾（加 `.gitkeep`）
2. 新增 `agent_trace.py`：提供兩個最小功能

   * `init(run_name) -> run_dir`（建立 run folder + trace.ndjson）
   * `log(run_dir, type, message, data_json)`（append ndjson）
3. 你下次在 Copilot Chat 用「請記錄：ON + run_name + 任務」
4. Copilot 在每個動作前/後都呼叫 `agent_trace.py log ...` 寫事件

---

## 你說的「我在對話框提到，請記錄，就會記錄下去」怎麼落地？

就是上面這個模式：
**“請記錄：ON” 是觸發詞**，但需要 Copilot “遵守規則” 才會真的寫檔。

要提高遵守率，我建議你固定用這個開頭格式（Copilot 最容易照做）：

```text
請記錄：ON
run_name: <任務名>
要求：你接下來每一個動作都要寫 trace（plan/tool_search/tool_use/tool_result/prompt_search/step_prepare/step_execute/strategy_shift/error/summary）
任務：<你的指令>
```

---

如果你願意，我下一則就直接把 **最小的 `agent_trace.py` 完整內容**貼給你（不到 80 行、零依賴），你複製進 repo 後就能立刻用。
