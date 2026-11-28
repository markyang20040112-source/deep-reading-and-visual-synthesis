# 階段二主幹總路由與分枝隔離調度中心（Phase 2 Trunk Router）

> **職責**：Phase 2 樹狀主幹唯一入口：① 拍板格式分枝（`A/B/C/D/E`）與邊界排除；② 訂定全域預設三支柱（[`style_and_color_core.md`](./style_and_color_core.md)）並寫入藍圖 `## 0`（[`blueprint_template.md`](./blueprint_template.md)）；③ 僅開選定格式之 `01_plan.md`；④ 以 **Subagent 隔離**（優先）或 **單執行緒接力**（備援）完成生成與驗收。未選格式 **100% 零讀取**。

```text
Phase 1 / Fast-Track (00_source + 01_log + data/*.csv)
  └─▶ [主幹 Trunk] 格式選擇 (本檔) ＋ 全域風格/色票預設 (style_and_color_core.md) ➔ 寫藍圖 ## 0
        ├─▶ Format D: formats/format_d_charts/   (01_plan ➔ 02_build_core + families/ ➔ 03_qa)
        ├─▶ Format A: formats/format_a_diagram/  (01_plan ➔ 02_build ➔ 03_qa)
        ├─▶ Format B: formats/format_b_document/ (01_plan ➔ 02_build_pdf | 02_build_medium ➔ 03_qa)
        ├─▶ Format C: formats/format_c_slides/   (01_plan ➔ 02_build [Step 3/4A 關卡] ➔ 03_qa)
        └─▶ Format E: formats/format_e_dashboard/(01_plan ➔ 02_build ➔ 03_qa)
```

> [!IMPORTANT]
> **暫停確認與智慧直通**：除非使用者當次明指定或 `user_preferences.json` 設 `"auto_apply_default": true`，否則**主幹提案**與**各分枝 `01_plan.md`** 後皆須暫停待拍板。若使用者已明講格式（如「畫圖＋寫 Medium」即鎖 `D+B`），自動完成格式範圍寫入 `## 0` 並直入分枝規劃。

---

## 一、 主幹步驟 1：格式選擇與「自給自足邊界鐵律」

| 素材體裁與任務場景 | 核心特徵 | 建議格式分枝組合（A / B / C / D / E） |
| :--- | :--- | :--- |
| **A. 實證研究與多維數據集** | 樣本數 $N$、連續分布、跨期／跨區／多類 | **D ＋ B ＋ C**（可加選 **E** 或 **A**） |
| **B. 策略框架與商業管理** | 管理模型、轉型路線、因果對比或治理 | **A ＋ B ＋ C** |
| **C. 系統架構與工程方法** | 技術堆疊、雙腦管線、資料流向或防禦 | **A ＋ B ＋ C** |
| **D. 跨領域評論與長篇敘事** | 多學科視角、理論演化與思維重構 | **A ＋ B** |
| **E. Medium 每週一圖專欄** | CSV＋資料說明書，單故事 `<= 1,600` 字 | **僅 D（1～2 張獨立單面板圖）＋ B（Medium，免 PDF）** |
| **F. 分配與密度圖形導學** | CSV＋資料說明書，逐步學 10 大分配圖 | **僅 D（`step_by_step_tutor` 一次 1 張圖＋五步解說）** |

> [!IMPORTANT]
> **【無統計圖／僅需內嵌簡圖之自給自足邊界鐵律】**：
> 1. **不需統計圖時絕不選 Format D**；純論述／管理／工程文獻無須強掛 D。
> 2. **僅需在 PDF 或 PPT 內插簡單流程／概念圖時，絕不為此額外選 Format A 或 D**：
>    - **Format B 自給自足**：於 [`../formats/format_b_document/02_build_pdf.md`](../formats/format_b_document/02_build_pdf.md) 直接呼叫 `generate_mindmap.py` 之 A4 直向簡圖 API（`setup_a4_portrait_canvas`、`draw_a4_node_box`、`draw_a4_arrow`、`save_a4_portrait_figure`，`7.44"` / `189mm`，`300 DPI`）；嚴禁將高密度 Format A 塞入 A4 報告。
>    - **Format C 自給自足**：於 [`../formats/format_c_slides/02_build.md`](../formats/format_c_slides/02_build.md) 直接使用原生向量版型（`F3-A`、`F3-B`、`F4-A`）或模式 3 `Tier 3` `render_svg_to_png_300dpi` HTML+SVG 透明底層。
> 3. **僅當需獨立交付全景知識圖譜 `.png`（`23.8"×12.6"–15.4"`, T1～T5）時才選 Format A**。
> 4. **B＋C 雙軌分工**：細節留 B、高視距口報與認知轉移歸 C。
> 5. **A2 無損擴展 vs. Medium 輕量路由**：一般文獻分支 $>4$ 個以拆圖（A `01/02/03+`）、擴章（B）、加頁（C）無損展開；Medium 聚焦單一故事線（1～2 張獨立單面板圖＋`<=1,600` 字原生 Markdown，禁 `ncols=2` 與 PDF）。

---

## 二、 主幹步驟 2：全域預設 ＋ 分枝計畫（`01_plan.md`）

1. **全域預設（混合式定裝）**：開啟 [`style_and_color_core.md`](./style_and_color_core.md) 拍板全域預設三支柱（模式 1/2/3 × 筆風 × 分層配色），依 [`blueprint_template.md`](./blueprint_template.md) 建立 `02_phase2_generation_blueprint.md` 寫入 **`## 0. 主幹全域錨點`**。
2. **分枝細節規劃（未選者 0 讀取，各分枝可局部覆寫模式／筆風／配色）**：
   - D ➔ [`../formats/format_d_charts/01_plan.md`](../formats/format_d_charts/01_plan.md) ｜ A ➔ [`../formats/format_a_diagram/01_plan.md`](../formats/format_a_diagram/01_plan.md) ｜ B ➔ [`../formats/format_b_document/01_plan.md`](../formats/format_b_document/01_plan.md)
   - C ➔ [`../formats/format_c_slides/01_plan.md`](../formats/format_c_slides/01_plan.md) ｜ E ➔ [`../formats/format_e_dashboard/01_plan.md`](../formats/format_e_dashboard/01_plan.md)
3. **落盤藍圖**：各分枝確認後寫入 `02_phase2_generation_blueprint.md` 對應之 **`## Format X 分枝藍圖`**（嚴禁回寫 `01_phase1_socratic_log.md`，亦不在 `01` 或 Medium 繳交區附 `02` 連結）。

---

## 三、 分枝執行與驗收（Subagent 隔離優先 ＋ 單執行緒備援）

> **依賴順序與作用域**：跨格式預設佇列 **`D ➔ A ➔ B ➔ C ➔ E`**（含 D 時必先完成 D 以供應圖檔與 `02_color_registry.json`）。`batch_generation`／`step_by_step_tutor` **僅作用於 Format D 內部**，不覆蓋跨格式 `sequential_confirm` 紀律。

### 模式 A：分格式 Subagent 隔離（平台支援 Subagent 時優先）
- **主對話負責**：主幹決策、各格式 `01_plan.md` 確認、藍圖維護、交付確認，以及互動型關卡（Format C `Step 3` 文案凍結／`Step 4A` 配置對齊、Format D `step_by_step_tutor` 逐張導學、Format E 驗畢後之雲端部署確認）。
- **Subagent 隔離封包（最小必要集，保護注意力）**：將單格式 `02_build*.md` ＋ `03_qa.md` 派發獨立 Subagent，**僅傳入**：
  1. `00_source_article.md`（需讀資料時含 `data/<原檔名>.csv`）與 `01_phase1_socratic_log.md`
  2. 共享狀態與上游產物：`02_color_registry.json`（存在或屬 D/E）；選 C 必傳 `02c_slide_spec_lock.json`；B/C 嵌 D 圖時附 `02_outputs/*.png`（含 `*_slide.png`）清單
  3. 藍圖之 **`## 0. 主幹全域錨點` ＋ 該格式 `## Format X 分枝藍圖`**（不傳其他分枝）
  4. 該格式 `02_build*.md` ＋ `03_qa.md`（D 併傳選定 1～2 個 `families/*.md`；E 併傳 `formats/format_d_charts/02_build_core.md` 與選定 `families/*.md`）
  5. [`visual_cognition_core.md`](./visual_cognition_core.md) ＋ 該格式單一筆風檔 ＋（開模式 2/3 時）[`editorial_narrative_spec.md`](./editorial_narrative_spec.md) 或 [`creative_armory/INDEX.md`](./creative_armory/INDEX.md)
- Subagent 跑完生成與 `03_qa.md`（含 `--cleanup`）後回報路徑與 QA 結果 ➔ 主對話向使用者確認並勾選藍圖 `- [x]`，再啟下一格式（除非使用者核准無依賴分枝並行）。

### 模式 B：單執行緒循序接力備援（無 Subagent 環境）
- 嚴守 `default_delivery_cadence = "sequential_confirm"` 依 **`D ➔ A ➔ B ➔ C ➔ E`** 每輪**僅載入當前單一格式**之 `02_build*.md` ＋ `03_qa.md`（加讀共通底盤、單一筆風與按需模式 2/3 檔），直接黑盒呼叫 `scripts/` 引擎生成並完成 `03_qa.md` 驗收 ➔ **⏸️ 獲使用者確認**後再進下一格式。

### 統一結案與 Git 同步
- 全選定格式確認交付後，將藍圖標頭改為 **`已交付`**，再按需開啟 [`../setup/git_sync_and_evolution_protocol.md`](../setup/git_sync_and_evolution_protocol.md) 執行雙倉庫同步、Format E 部署、Medium 繳交或 Step E1～E3 靈感閉環。
