# 階段二：視覺化綜合與多格式產出路由（Phase 2 Output Router）

> **單一職責定位（Single Responsibility）**：本檔負責 Phase 2 的**標準四步執行流程**與**動態三軸視覺決策引擎（决定要生成哪幾種格式與對應拓撲）**。底層視覺認知規範請見 `visual_cognition_principles.md`；即時靈感捕獲與演進閉環請見 `SKILL.md` 第三節。

---

## 一、 階段二標準執行步驟（4-Step Workflow）

1. **步驟 1：盤點核心洞見與數據結構**：回顧 `01_notes/reading_notes.md`，梳理文章的「全局論證架構」、「最值得深挖的核心機制」與「具體量化實證數據」。
2. **步驟 2：啟動「動態三軸視覺決策引擎」**：依照下方第二節的決策框架，向使用者提出**客製化視覺產出組合建議**（亦可由使用者直接指定單一或全部 4 種格式）。
3. **步驟 3：按需載入對應規格檔（Lazy-Loading Specs）**：
   - **必讀共用底層**：`phase2_output/visual_cognition_principles.md`
   - **Format A（知識圖譜 PNG）**：`phase2_output/visual_diagram_matplotlib_spec.md` + `scripts/generate_mindmap.py`
   - **Format B（結構化深度報告 MD + PDF）**：`phase2_output/document_report_spec.md`
   - **Format C（高階主管簡報 PPTX）**：`phase2_output/presentation_slide_spec.md`
   - **Format D（量化實證圖表 PNG）**：`phase2_output/quantitative_chart_spec.md`
4. **步驟 4：逐張視覺驗證與清理交付（Mandatory Visual Inspection & Clean Hygiene）**：
   - 凡生成 `.png`、`.pdf` 或 `.pptx`，**必須**轉出或直接透過 `read_file` 檢視渲染成品，逐一核對：無文字重疊、無穿線、無溢界、無斷頭框線、字級飽滿易讀。
   - 檢驗通過後，立即刪除 `02_outputs/` 內的暫存渲染檔（`.html`、`slide_*.png`），確保交付資料夾乾淨。

---

## 二、 動態三軸視覺決策引擎（Dynamic Tri-Axial Visual Decision Engine）

> **理論依據**：**認知適配理論（Cognitive Fit Theory, Vessey 1991）** 與 **任務導向圖表分類學（Task- by-Data-Type Taxonomy, Shneiderman 1996）**。當外在視覺表徵的空間拓撲與讀者的內在決策心智模型一致時，問題解決效率最高。

### 軸線一：文章體裁與證據結構（Genre & Evidence Structure）

| 文章體裁類型 | 核心特徵 | 必備主圖（圖 1：全局架構） | 推薦深挖副圖（圖 2～圖 3） | 推薦報告與簡報組合 |
| :--- | :--- | :--- | :--- | :--- |
| **A. 實證研究與數據調查**<br>*(Empirical / Survey)* | 含樣本數 $N$、百分比落差、迴歸或因果對照 | **全景三欄式研究拆解圖** 或 **核心四模組脊椎圖** | 1. **理論機制 / 雙軌架構對照圖**（Format A）<br>2. **多面板量化實證圖表**（Format D） | **Format B（文體 2：高階決策備忘錄）** + **Format C（簡報）** |
| **B. 策略框架與商業管理**<br>*(Strategic / Management)* | 提出新管理模型、轉型路線或二元對立破局 | **雙軌對比匯流圖** 或 **4×2 階層組塊心智圖** | 1. **2×2 策略定位矩陣圖**<br>2. **多階段演進藍圖 / 閉環系統圖** | **Format B（文體 2：高階決策備忘錄）** + **Format C（簡報）** |
| **C. 系統架構與工程方法**<br>*(System / Architecture)* | 聚焦技術堆疊、資料流向、演算法或治理管線 | **多層次雙腦/管線架構圖** | 1. **時序資料流 / 狀態轉換圖**<br>2. **失效模式與工程對策平行解剖圖** | **Format B（文體 3：方法論實踐藍圖）** + **Format C（簡報）** |
| **D. 跨領域評論與長篇敘事**<br>*(Synthesis / Essay)* | 融合多學科視角、歷史演進與思維重構 | **核心脊椎 + 4 象限宏觀容器圖** | **跨領域類比結構映射對照圖** | **Format B（文體 1：深度綜合評論 或 文體 4：跨域知識卡片）** |

### 軸線二：核心溝通任務對映表（Task-to-Topology Mapping）

| 溝通任務（Communication Task） | 最佳視覺拓撲（Optimal Visual Topology） | 負責規格檔 |
| :--- | :--- | :--- |
| **建立全篇宏觀地圖與邏輯脈絡** | **中央脊椎 + $4 \to 2 \to 3$ 階層組塊圖**（`generate_mindmap.py`） | `visual_diagram_matplotlib_spec.md` |
| **拆解二元衝突與整合式破局** | **左右雙軌對抗 + 中央匯流引擎架構圖** | `visual_diagram_matplotlib_spec.md` |
| **比較跨階段留存率遞減或預期與現實斷崖** | **XY 軸空間重力折線＋直柱複合圖（左至右階段推演 × 0~100% 垂直高度）** | `quantitative_chart_spec.md` |
| **拆解多階段成熟度分佈與跨圖接力** | **同質單色相漸層柱線圖 ＋ 雙圖跨面板色相區隔與視覺接力（1+1>2）** | `quantitative_chart_spec.md` |
| **提供高密度治理規範、審計清單與完整論述** | **A4 雙模態混合排版 PDF 報告**（敘事段落 + 平行解剖矩陣 + 戰術卡片） | `document_report_spec.md` |
| **進行高階主管會議簡報與決策提案** | **16:9 斷言-證據式（Assertion-Evidence）原生向量投影片** | `presentation_slide_spec.md` |

### 軸線三：使用者交付場景（Delivery Scenario）
- 若使用者要求**「完整全套產出」**，則依序生成：
  1. `01_article_master_structure_map.png`（Format A：全篇結構總覽圖）
  2. `02_<specific_mechanism_diagram>.png`（Format A：核心機制/架構深挖圖）
  3. `03_<quantitative_charts>.png`（Format D：量化實證圖表，若原文含量化數據）
  4. `01_executive_strategy_report.md` & `.pdf`（Format B：結構化決策報告，嵌入上述高清圖表）
  5. `02_executive_presentation.pptx`（Format C：16:9 原生向量高階主管簡報）
