# 階段二：視覺化綜合與多格式產出路由（Phase 2 Output Router）

> **單一職責定位（Single Responsibility）**：本檔負責 Phase 2 的**標準四步執行流程**與**動態三軸視覺決策引擎（決定要生成哪幾種格式與對應拓撲）**。底層視覺認知規範請見 [`visual_cognition_principles.md`](visual_cognition_principles.md)；即時靈感捕獲與演進閉環請見 [`SKILL.md`](../SKILL.md) 第三節。

---

## 一、 階段二標準執行步驟（4-Step Workflow）

1. **步驟 1：盤點核心洞見與數據結構**：回顧 `01_phase1_socratic_log.md` 或輸入資料集，梳理文章／數據的「全局論證架構」、「最值得深挖的核心機制」與「具體量化實證／多維度數據結構」。
2. **步驟 2：啟動「動態三軸視覺決策引擎」**：依照下方第二節的決策框架，向使用者提出**客製化視覺產出組合建議**（亦可由使用者直接指定單一或任意組合之 5 種特化格式 A～E）。
3. **步驟 3：按需載入對應規格檔與黑盒呼叫共用引擎（Lazy-Loading Specs & Black-Box Engine Invocation）**：
   - **【底層引擎黑盒呼叫鐵律（Black-Box Engine API Rule）】**：`scripts/*.py` 與 `scripts/*.js` 為已封裝完成之黑盒渲染引擎，其精簡函數簽名（10～15 行 API 契約）已直接記載於各對應 `phase2_output/*_spec.md` 規範檔中。**在正常執行流程中，AI 必須直接 `import` 並呼叫這些引擎，嚴禁對 `scripts/*.py` 原始碼執行 `read_file` / `view_file`（除非腳本執行拋出異常需要除錯）**，以極大化節省 Token 與注意力預算。
   - **必讀共用底層**：[`phase2_output/visual_cognition_principles.md`](visual_cognition_principles.md)
   - **Format A（知識圖譜 `.png`）**：讀取 [`phase2_output/visual_diagram_matplotlib_spec.md`](visual_diagram_matplotlib_spec.md) $\rightarrow$ 直接黑盒 `import` [`scripts/generate_mindmap.py`](../scripts/generate_mindmap.py)
   - **Format B（結構化深度報告 `.md` + `.pdf` ／ 文體 5：Medium 數據敘事專欄 `.md`）**：讀取 [`phase2_output/document_report_spec.md`](document_report_spec.md) $\rightarrow$ 若為文體 1～4 深度報告則直接黑盒 `import` [`scripts/pdf_report_engine.py`](../scripts/pdf_report_engine.py)；**若為「文體 5：Medium 每週一圖數據敘事專欄（`<= 1,000` 字）」，則僅產出原生相容 `.md` 文稿，免除呼叫 `pdf_report_engine.py` 編譯 A4 PDF**
   - **Format C（高階主管簡報 `.pptx`）**：讀取 [`phase2_output/presentation_slide_spec.md`](presentation_slide_spec.md) $\rightarrow$ 直接黑盒 `import` [`scripts/pptx_slide_engine.py`](../scripts/pptx_slide_engine.py)
   - **Format D（量化實證圖表 `.png`）**：讀取 [`phase2_output/quantitative_chart_spec.md`](quantitative_chart_spec.md) $\rightarrow$ 直接黑盒 `import` [`scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)
   - **Format E（數據儀表板 Web `.html`/`.css`/`.js` + 靜態全景圖 `.png`）**：讀取 [`phase2_output/data_dashboard_spec.md`](data_dashboard_spec.md) + [`phase2_output/quantitative_chart_spec.md`](quantitative_chart_spec.md) $\rightarrow$ 直接載入 [`scripts/gephi_palette.js`](../scripts/gephi_palette.js) 與 [`scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)（🔗 **雙向連動**：與 Format D 共用鎖定版 `Gephi · pastel` 配色設定集 SSOT，兩者共通部分若有改動須同步更新）
4. **步驟 4：逐張視覺驗證、清理交付、Git 單檔對話紀錄推送與獨立網站部署（Mandatory Visual Inspection, Clean Hygiene & Git Deployment）**：
   - 凡生成 `.png`、`.pdf`、`.pptx` 或互動式儀表板，**必須**透過 `view_file`（或瀏覽器預覽）檢視渲染成品：針對 `.pdf` 與 `.pptx`，直接黑盒呼叫 [`scripts/verify_visual_outputs.py`](../scripts/verify_visual_outputs.py) 之 `render_pdf_to_pngs()` / `render_pptx_to_pngs()` 轉出臨時預覽圖，逐頁核對：無文字重疊、無穿線、無溢界、無斷頭框線、字級飽滿易讀、同名類別跨圖表色碼鎖定一致。
   - **【Medium 每週一圖模式免編譯 PDF 特例】**：當執行「Medium 每週一圖／輕量數據敘事專欄模式」時，**免除呼叫 `scripts/pdf_report_engine.py` 編譯 A4 PDF**，僅針對產出的 1～2 張獨立單面板 `.png` 統計圖執行 `view_file` 視覺驗收，並於驗收後自動執行 `git add`、`git commit` 與 `git push origin main`，在回覆結尾輸出課堂 Google Doc 一鍵複製繳交區塊（含 `01_phase1_socratic_log.md` 之 GitHub `blob/main/...` 單檔完整網址）。
   - 檢驗通過後，立即呼叫 `cleanup_preview_artifacts(output_dir)`（或執行 `python scripts/verify_visual_outputs.py <02_outputs> --cleanup`）刪除 `02_outputs/` 內的暫存渲染中介檔（如 PDF 編譯暫存 `.html`、`_preview_page_*.png`、`_preview_slide_*.png`），確保交付資料夾 100% 乾淨。
   - **【Format E 數據儀表板專屬交付與 Git 網站綁定】**：若產出包含 Format E 互動式網頁儀表板，其正式網站專案檔（`index.html`、`css/`、`js/`、`data/`、`.nojekyll`、`.gitignore`、`README.md`）予以完整保留，並依 [`data_dashboard_spec.md`](data_dashboard_spec.md) 第四節主動詢問或執行**「獨立 Git 儲存庫綁定與 GitHub Pages 線上網站發布」**。

---

## 二、 動態三軸視覺決策引擎（Dynamic Tri-Axial Visual Decision Engine）

> **理論依據**：**認知適配理論（Cognitive Fit Theory, Vessey 1991）** 與 **任務導向圖表分類學（Task-by-Data-Type Taxonomy, Shneiderman 1996）**。當外在視覺表徵的空間拓撲與讀者的內在決策心智模型一致時，問題解決效率最高。

### 軸線一：文章／資料體裁與證據結構（Genre & Evidence Structure）

| 體裁與資料類型 | 核心特徵 | 必備主圖（圖 1：全局架構／破題） | 推薦深挖副圖／數據視覺化 | 推薦報告、簡報與儀表板組合 |
| :--- | :--- | :--- | :--- | :--- |
| **A. 實證研究與多維度數據集**<br>*(Empirical / Dataset)* | 含樣本數 $N$、百分比落差、跨期／跨區域／多類別結構數據 | **全景三欄式研究拆解圖** 或 **核心四模組脊椎圖** | 1. **多面板量化實證圖表**（Format D）<br>2. **動態多視角數據儀表板**（Format E，不寫死圖表類型，依資料維度動態配置） | **Format B（文體 2：高階決策備忘錄）** + **Format C（簡報）** + **Format E（數據儀表板）** |
| **B. 策略框架與商業管理**<br>*(Strategic / Management)* | 提出新管理模型、轉型路線或二元對立破局 | **雙軌對比匯流圖** 或 **4×2 階層組塊心智圖** | 1. **2×2 策略定位矩陣圖**<br>2. **多階段演進藍圖 / 閉環系統圖** | **Format B（文體 2：高階決策備忘錄）** + **Format C（簡報）** |
| **C. 系統架構與工程方法**<br>*(System / Architecture)* | 聚焦技術堆疊、資料流向、演算法或治理管線 | **多層次雙腦/管線架構圖** | 1. **時序資料流 / 狀態轉換圖**<br>2. **失效模式與工程對策平行解剖圖** | **Format B（文體 3：方法論實踐藍圖）** + **Format C（簡報）** |
| **D. 跨領域評論與長篇敘事**<br>*(Synthesis / Essay)* | 融合多學科視角、歷史演進與思維重構 | **核心脊椎 + 4 象限宏觀容器圖** | **跨領域類比結構映射對照圖** | **Format B（文體 1：深度綜合評論 或 文體 4：跨域知識卡片）** |
| **E. Medium 每週一圖／輕量數據敘事專欄**<br>*(Medium Data Storytelling Column)* | 傳入 CSV 原始檔 ＋《資料說明書（Data Codebook）》，撰寫 `<= 1,000` 字、含 1～2 張統計圖之公開數據專欄 | **Format D 獨立單面板統計圖 1（`01_chart_hook.png`）**：暖杏蜜橘系（`#ECA072` / `orange`）呈現全局現象反差或偏態破題 | **Format D 獨立單面板統計圖 2（`02_chart_drilldown.png`，選配，總圖數限 1～2 張）**：霧靄青藍系（`#5DBACD` / `blue`）呈現結構拆解或交叉深挖（**禁止 `ncols=2` 並排子圖**） | **僅產出 Format D（1～2 張獨立單面板 `.png`）＋ Format B 文體 5（`02_medium_article.md` 短專欄）**；不產出 Format A / C / E，且**免除編譯 A4 PDF** |

### 軸線二：核心溝通任務對映表（Task-to-Topology Mapping）

| 溝通任務（Communication Task） | 最佳視覺拓撲（Optimal Visual Topology） | 負責規格檔與引擎 |
| :--- | :--- | :--- |
| **建立全篇宏觀地圖與邏輯脈絡** | **中央脊椎 + $4 \to 2 \to 3$ 階層組塊圖**（`generate_mindmap.py`：`draw_spine_hub_module`） | [`visual_diagram_matplotlib_spec.md`](visual_diagram_matplotlib_spec.md) |
| **拆解二元衝突、回饋迴路與整合破局** | **左右雙軌對抗 + 中央匯流引擎 / 雙迴路圖**（`draw_feedback_loop_pair` / `draw_3x3_pipeline_grid`） | [`visual_diagram_matplotlib_spec.md`](visual_diagram_matplotlib_spec.md) |
| **批判邊界、反例壓力測試與跨域遷移** | **2×2 策略象限矩陣 / 跨領域結構映射專題圖**（`draw_2x2_matrix_quadrants`） | [`visual_diagram_matplotlib_spec.md`](visual_diagram_matplotlib_spec.md) |
| **比較跨階段留存率遞減或同案雙指標反差** | **XY 軸空間重力折線＋直柱複合圖 / 共同基準線配對雙柱＋剪刀差標註圖**（`hcl_color_engine.py`） | [`quantitative_chart_spec.md`](quantitative_chart_spec.md) |
| **拆解多階段成熟度分佈與跨圖接力** | **鎖定版 `Gephi · pastel` 5 階同質循序漸層 ＋ 雙圖跨面板色相區隔與視覺接力（1+1>2）** | [`quantitative_chart_spec.md`](quantitative_chart_spec.md) |
| **撰寫 Medium 每週一圖／輕量數據新聞專欄（`<= 1,000` 字 ＋ 1～2 張圖）** | **1～2 張獨立單面板 `300 DPI` 統計圖（圖 1 橘色破題 $\rightarrow$ 圖 2 藍色深挖，內嵌三層分流 `assert` 與三重時間戳記官方圖註）＋ 文體 5 Medium 原生 Markdown 專欄（含官方來源授權分離計字）** | [`quantitative_chart_spec.md`](quantitative_chart_spec.md) + [`document_report_spec.md`](document_report_spec.md) |
| **探索多維度數據集（總覽、篩選、排行、增減發散與深鑽明細）** | **不寫死圖表格式之動態數據儀表板（KPI 卡 + 動態多視角互動圖表 + 明細表與 CSV 匯出，引用 `gephi_palette.js`）** | [`data_dashboard_spec.md`](data_dashboard_spec.md) ⇄ [`quantitative_chart_spec.md`](quantitative_chart_spec.md) |
| **提供高密度治理規範、審計清單與完整論述** | **A4 雙模態混合排版 PDF 報告**（`pdf_report_engine.py`：支援 A4 橫向滿版大圖跨頁與三線表） | [`document_report_spec.md`](document_report_spec.md) |
| **進行高階主管會議簡報與決策提案** | **16:9 斷言-證據式（Assertion-Evidence）原生向量投影片**（`pptx_slide_engine.py`） | [`presentation_slide_spec.md`](presentation_slide_spec.md) |

### 軸線三：無損分流擴展鐵律 vs. Medium 單一故事線輕量交付場景（Zero-Loss Expansion vs. Single-Hook Lightweight Delivery）

> **【A2 無損分流擴展鐵律（適用一般文獻／深度報告／簡報）：以「拆圖、擴章、加頁」取代「刪減內容」】**：
> 當第一階段 `01_phase1_socratic_log.md` 第五節收斂出 $> 4$ 個分支（含 `(a) 核心論證主幹分支` 與 `(b) 批判延伸與跨域遷移分支`）時，**嚴禁為了塞進單一畫布而刪減任何細節或批判延伸議題**！單張 2D 視覺畫布維持 3～4 個宏觀大區塊以守住 `12pt` 字級底線，並自動啟動以下跨畫布／跨章節無損擴展：
> - **Format A（知識圖譜拆圖擴展）**：`01` 繪製核心論證主幹（3～4 個核心模組）；`02` 繪製核心機制與架構深挖圖；**`03+` 自動加開「批判邊界、反例壓力測試與跨域類比遷移專題圖」**，完整承載所有延伸分支。
> - **Format B（深度報告動態擴章）**：章節編號依分支總數 $N$ 自然延展（`壹、貳、參、肆、伍、陸、柒...`），讓每個核心主幹與批判延伸分支皆擁有獨立章節、三線表或戰術卡片。
> - **Format C（高階簡報動態加頁）**：中段內容頁隨實質命題數 $N$ 動態加頁（如以 `S1` 雙欄對比呈現正反辯證、以 `S5` 象限呈現邊界條件），並附上完整演講備忘稿。
> - **Format D / E（量化圖表與儀表板擴展）**：自動增加子面板（Subplots）或互動切換視角（Tabs）。

- **場景 1：若使用者要求「完整全套產出」**，則依序生成（並可依資料屬性加選或單獨指定 **Format E 數據儀表板**）：
  1. `01_article_master_structure_map.png`（Format A：全篇核心主幹總覽圖）
  2. `02_<specific_mechanism_diagram>.png`（Format A：核心機制/架構深挖圖）
  3. `03_<critical_synthesis_or_quantitative_charts>.png`（Format A 批判延伸與跨域遷移專題圖，及／或 Format D 量化實證圖表）
  4. `01_executive_strategy_report.md` & `.pdf`（Format B：結構化決策報告，嵌入上述高清圖表或 A4 橫向跨頁大圖）
  5. `02_executive_presentation.pptx`（Format C：16:9 原生向量高階主管簡報）
  6. `dashboard/` 或獨立專案目錄（Format E：Git-Ready 零後端互動式 Web 儀表板 `index.html` + `css/style.css` + `js/gephi_palette.js` + `js/dashboard.js` + `data/` + `.nojekyll` + `.gitignore` + `README.md` 及對應靜態全景圖 `.png`）
- **場景 2：若任務屬於「Medium 每週一圖／輕量數據敘事專欄模式」**，則啟動**單一故事線輕量路由（Single-Hook Lightweight Route）**，於 `02_outputs/` 僅生成：
  1. `01_chart_hook.png`（及選配之 `02_chart_drilldown.png`，嚴格限制 **1～2 張各自獨立的單面板 `300 DPI` `.png` 統計圖**與繪圖腳本 `generate_charts.py`，**禁止 `ncols=2` 並排雙子圖**）
  2. `02_medium_article.md`（Format B 文體 5：正文 `650～900` 字、絕對 `<= 1,000` 字之 Medium 100% 原生相容專欄文稿，含 `---` 分隔之「原始官方資料來源與授權聲明」及雙軌字數統計，**免除編譯 PDF**）
  3. 透過 `view_file` 驗收 1～2 張 `.png` 圖表無誤後，自動將整個 session（含 `data/<原檔名>.csv`、`00_source_article.md`、`01_phase1_socratic_log.md` 與 `02_outputs/`）執行 `git add -A && git commit -m "..." && git push origin main`，並在回覆結尾印出課堂 Google Doc 一鍵複製繳交區塊。



