# 階段二：視覺化綜合與多格式產出路由（Phase 2 Output Router）

> **單一職責定位（Single Responsibility）**：本檔負責 Phase 2 的**標準四步執行流程**與**動態三軸視覺決策引擎（決定要生成哪幾種格式與對應拓撲）**。底層視覺認知規範請見 [`visual_cognition_principles.md`](visual_cognition_principles.md)；即時靈感捕獲與演進閉環請見 [`SKILL.md`](../SKILL.md) 第三節。

---

## 一、 階段二標準執行步驟（4-Step Workflow）

1. **步驟 1：盤點核心洞見與數據結構**：回顧 `01_phase1_socratic_log.md` 或輸入資料集，梳理文章／數據的「全局論證架構」、「最值得深挖的核心機制」與「具體量化實證／多維度數據結構」。
2. **步驟 2：啟動「動態三軸視覺決策引擎」**：依照下方第二節的決策框架，向使用者提出**客製化視覺產出組合建議**（亦可由使用者直接指定單一或任意組合之 5 種特化格式 A～E）。
3. **步驟 3：按需載入對應規格檔（Lazy-Loading Specs）**：
   - **必讀共用底層**：[`phase2_output/visual_cognition_principles.md`](visual_cognition_principles.md)
   - **Format A（知識圖譜 `.png`）**：[`phase2_output/visual_diagram_matplotlib_spec.md`](visual_diagram_matplotlib_spec.md) + [`scripts/generate_mindmap.py`](../scripts/generate_mindmap.py)
   - **Format B（結構化深度報告 `.md` + `.pdf`）**：[`phase2_output/document_report_spec.md`](document_report_spec.md)
   - **Format C（高階主管簡報 `.pptx`）**：[`phase2_output/presentation_slide_spec.md`](presentation_slide_spec.md)
   - **Format D（量化實證圖表 `.png`）**：[`phase2_output/quantitative_chart_spec.md`](quantitative_chart_spec.md) + [`scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)
   - **Format E（數據儀表板 Web `.html`/`.css`/`.js` + 靜態全景圖 `.png`）**：[`phase2_output/data_dashboard_spec.md`](data_dashboard_spec.md) + [`phase2_output/quantitative_chart_spec.md`](quantitative_chart_spec.md)（🔗 **雙向連動**：與 Format D 共用鎖定版 `Gephi · pastel` 配色設定集與圖表設計規則，兩者共通部分若有改動須同步更新）
4. **步驟 4：逐張視覺驗證、清理交付與獨立網站部署（Mandatory Visual Inspection, Clean Hygiene & Git Web Deployment）**：
   - 凡生成 `.png`、`.pdf`、`.pptx` 或互動式儀表板，**必須**透過 `view_file`（或瀏覽器預覽）檢視渲染成品，逐一核對：無文字重疊、無穿線、無溢界、無斷頭框線、字級飽滿易讀、同名類別跨圖表色碼鎖定一致。
   - 檢驗通過後，立即刪除 `02_outputs/` 內的暫存渲染中介檔（如 PDF 編譯暫存 `.html`、`slide_*.png`），確保交付資料夾乾淨。
   - **【Format E 數據儀表板專屬交付與 Git 網站綁定】**：若產出包含 Format E 互動式網頁儀表板，其正式網站專案檔（`index.html`、`css/`、`js/`、`data/`、`.nojekyll`、`.gitignore`、`README.md`）予以完整保留，並依 [`data_dashboard_spec.md`](data_dashboard_spec.md) 第四節主動詢問或執行**「獨立 Git 儲存庫綁定與 GitHub Pages 線上網站發布」**。

---

## 二、 動態三軸視覺決策引擎（Dynamic Tri-Axial Visual Decision Engine）

> **理論依據**：**認知適配理論（Cognitive Fit Theory, Vessey 1991）** 與 **任務導向圖表分類學（Task-by-Data-Type Taxonomy, Shneiderman 1996）**。當外在視覺表徵的空間拓撲與讀者的內在決策心智模型一致時，問題解決效率最高。

### 軸線一：文章／資料體裁與證據結構（Genre & Evidence Structure）

| 體裁與資料類型 | 核心特徵 | 必備主圖（圖 1：全局架構） | 推薦深挖副圖／數據視覺化 | 推薦報告、簡報與儀表板組合 |
| :--- | :--- | :--- | :--- | :--- |
| **A. 實證研究與多維度數據集**<br>*(Empirical / Dataset)* | 含樣本數 $N$、百分比落差、跨期／跨區域／多類別結構數據 | **全景三欄式研究拆解圖** 或 **核心四模組脊椎圖** | 1. **多面板量化實證圖表**（Format D）<br>2. **動態多視角數據儀表板**（Format E，不寫死圖表類型，依資料維度動態配置） | **Format B（文體 2：高階決策備忘錄）** + **Format C（簡報）** + **Format E（數據儀表板）** |
| **B. 策略框架與商業管理**<br>*(Strategic / Management)* | 提出新管理模型、轉型路線或二元對立破局 | **雙軌對比匯流圖** 或 **4×2 階層組塊心智圖** | 1. **2×2 策略定位矩陣圖**<br>2. **多階段演進藍圖 / 閉環系統圖** | **Format B（文體 2：高階決策備忘錄）** + **Format C（簡報）** |
| **C. 系統架構與工程方法**<br>*(System / Architecture)* | 聚焦技術堆疊、資料流向、演算法或治理管線 | **多層次雙腦/管線架構圖** | 1. **時序資料流 / 狀態轉換圖**<br>2. **失效模式與工程對策平行解剖圖** | **Format B（文體 3：方法論實踐藍圖）** + **Format C（簡報）** |
| **D. 跨領域評論與長篇敘事**<br>*(Synthesis / Essay)* | 融合多學科視角、歷史演進與思維重構 | **核心脊椎 + 4 象限宏觀容器圖** | **跨領域類比結構映射對照圖** | **Format B（文體 1：深度綜合評論 或 文體 4：跨域知識卡片）** |

### 軸線二：核心溝通任務對映表（Task-to-Topology Mapping）

| 溝通任務（Communication Task） | 最佳視覺拓撲（Optimal Visual Topology） | 負責規格檔 |
| :--- | :--- | :--- |
| **建立全篇宏觀地圖與邏輯脈絡** | **中央脊椎 + $4 \to 2 \to 3$ 階層組塊圖**（`generate_mindmap.py`） | [`visual_diagram_matplotlib_spec.md`](visual_diagram_matplotlib_spec.md) |
| **拆解二元衝突與整合式破局** | **左右雙軌對抗 + 中央匯流引擎架構圖** | [`visual_diagram_matplotlib_spec.md`](visual_diagram_matplotlib_spec.md) |
| **比較跨階段留存率遞減或同案雙指標反差** | **XY 軸空間重力折線＋直柱複合圖 / 共同基準線配對雙柱＋剪刀差標註圖** | [`quantitative_chart_spec.md`](quantitative_chart_spec.md) |
| **拆解多階段成熟度分佈與跨圖接力** | **鎖定版 `Gephi · pastel` 5 階同質循序漸層 ＋ 雙圖跨面板色相區隔與視覺接力（1+1>2）** | [`quantitative_chart_spec.md`](quantitative_chart_spec.md) |
| **探索多維度數據集（總覽、篩選、排行、增減發散與深鑽明細）** | **不寫死圖表格式之動態數據儀表板（KPI 卡 + 動態多視角互動圖表 / Bento 網格 + 明細表與 CSV 匯出，鎖定 `Gephi · pastel` 配色設定集，支援一鍵綁定獨立 Git 發布網站）** | [`data_dashboard_spec.md`](data_dashboard_spec.md) ⇄ [`quantitative_chart_spec.md`](quantitative_chart_spec.md) |
| **提供高密度治理規範、審計清單與完整論述** | **A4 雙模態混合排版 PDF 報告**（敘事段落 + 平行解剖矩陣 + 戰術卡片） | [`document_report_spec.md`](document_report_spec.md) |
| **進行高階主管會議簡報與決策提案** | **16:9 斷言-證據式（Assertion-Evidence）原生向量投影片** | [`presentation_slide_spec.md`](presentation_slide_spec.md) |

### 軸線三：使用者交付場景（Delivery Scenario）
- 若使用者要求**「完整全套產出」**，則依序生成（並可依資料屬性加選或單獨指定 **Format E 數據儀表板**）：
  1. `01_article_master_structure_map.png`（Format A：全篇結構總覽圖）
  2. `02_<specific_mechanism_diagram>.png`（Format A：核心機制/架構深挖圖）
  3. `03_<quantitative_charts>.png`（Format D：量化實證圖表，若原文含量化數據）
  4. `01_executive_strategy_report.md` & `.pdf`（Format B：結構化決策報告，嵌入上述高清圖表）
  5. `02_executive_presentation.pptx`（Format C：16:9 原生向量高階主管簡報）
  6. `dashboard/` 或獨立專案目錄（Format E：當任務涉及多維度數據探索或使用者指定生成數據儀表板時，產出 Git-Ready 零後端互動式 Web 儀表板 `index.html` + `css/` + `js/` + `data/` + `.nojekyll` + `.gitignore` + `README.md` 及對應靜態全景圖 `.png`，並執行獨立 Git 儲存庫綁定與 GitHub Pages 網站部署流程）

