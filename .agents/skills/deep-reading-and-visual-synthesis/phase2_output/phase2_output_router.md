# 階段二：視覺化綜合、生成前五維度確認關卡與多格式產出路由（Phase 2 Output Router）

> **單一職責定位（Single Responsibility）**：本檔負責 Phase 2 的**「生成前五維度動態確認關卡（Pre-Generation Confirmation Gate）」**、**標準五步執行流程（含一次批次生成 vs. 逐步導學互動模式）**與**動態三軸視覺決策引擎（決定要生成哪幾種格式與對應拓撲）**。底層視覺認知規範、筆風 8 大插槽綁定與分層顏色設定集請見 [`visual_cognition_principles.md`](visual_cognition_principles.md)；即時靈感捕獲與演進閉環請見 [`SKILL.md`](../SKILL.md) 第三節。

---

## 零、 生成前「五維度動態確認關卡（Pre-Generation Confirmation Gate）」

> [!IMPORTANT]
> **核心鐵律：除非使用者已在 [`../config/user_preferences.json`](../config/user_preferences.json) 的 `confirmation_gate` 中將該維度設為 `"auto_apply_default": true`（或已在當次提示詞中明確指定），否則無論是從 Phase 1 收斂進入 Phase 2，還是使用者要求「直接生成（Fast-Track）」，在動手撰寫或繪圖前，AI 必須先向使用者確認以下 5 大生成維度，絕對禁止擅自幫使用者代選！**

| 確認維度 | 當設定為「每次詢問（`ask_every_time` — 預設）」時的 AI 行為 | 當設有「複數設定檔」或 `"auto_apply_default": true` 時 |
| :--- | :--- | :--- |
| **1. 產出格式與檔案清單**<br>*(Output Formats & Files)* | 依內容特性與下方第二節決策引擎提出建議組合（如 Format A/B/C/D/E 哪幾種、Format B 哪種文體），請使用者確認本次要生成的具體檔案。 | 若已鎖定常用組合且設為免問，則直接套用。 |
| **2. 對應筆風設定檔**<br>*(Writing Style Profile)* | 呼叫 `check_user_identity_and_load_prefs()` 列出當前使用者自己擁有的筆風設定檔（擁有者 `markyang20040112-source` 顯示 [`../config/owner_styles/`](../config/owner_styles/) 下之 `plain_first_progressive`、`rigorous_empirical_stat`、`editorial_data_journalism`；外部使用者僅顯示 `config/user_styles/`），詢問本次要套用哪一種筆風（**支援不同輸出檔案交叉搭配不同筆風**，且筆風之 `Slot 1～8` **100% 穿透控制所有生成場景的每一個字詞與微文案**）。 | 若僅有 1 組且設為預設免問，自動套用；若有複數組則列出供挑選。 |
| **3. 對應顏色設定集**<br>*(Layered Color Sets)* | 若使用者擁有複數個圖表色票集（`chart_palettes`）或文件佈景主題（`document_themes`），詢問本次要套用哪一套配色（擁有者預設為 `gephi_pastel_locked` ＋ `modern_academic_slate`）。 | 若已鎖定預設某套色票且設為免問，自動套用。 |
| **4. 圖表模式與故事結構選型**<br>*(Chart Mode & Interaction)* | 當產出包含 Format D 或 E 時，根據數據或文章的故事張力，向使用者確認：<br>① **圖表模式**：**`editorial_storytelling`（編輯室敘事圖解模式）** vs. **`pure_dataviz`（純資料視覺化／10 大分配圖形模式）** vs. **`hybrid_custom`（自由混搭）**；<br>② **具體圖表結構方案**（以故事張力驅動，不強制最簡圖表）；<br>③ **推進節奏**：採用**「逐步導學／探索互動模式（`step_by_step_tutor`：一次呈現一張圖＋五步解說，討論後再畫下一張）」**或**「一次批次生成（`batch_generation`）」**。 | 即使預先設定偏好模式，涉及「具體用哪幾張圖表結構反映本次數據故事」仍須與使用者對齊確認。 |
| **5. 版面與輸出細節偏好**<br>*(Layout & Delivery Details)* | 詢問 PDF 字體排版模式（`modern_sans` 現代黑體 vs. `clreq_kaiti` 標楷體首行縮排）、是否需要完成後自動同步 Git 等細節。 | 依個人化設定或筆風檔 `linked_defaults` 決定是否免問。 |

---

## 一、 階段二標準執行步驟（5-Step Workflow）

1. **步驟 1：盤點核心洞見與數據結構**：回顧 `01_phase1_socratic_log.md` 或輸入資料集，梳理文章／數據的「全局論證架構」、「最值得深挖的核心機制」與「具體量化實證／多維度數據結構」。
2. **步驟 2：啟動「動態三軸視覺決策引擎」並通過「五維度動態確認關卡」**：依照上方第零節與下方第二節的決策框架，向使用者提出**五維度生成確認清單**（格式、筆風檔、顏色集、圖表模式與互動節奏、版面細節），待使用者拍板後鎖定本次執行契約。
3. **步驟 3：按需載入對應筆風檔、規格檔與黑盒呼叫共用引擎（Lazy-Loading Style Profiles, Specs & Black-Box Engines）**：
   - **【底層引擎黑盒呼叫鐵律（Black-Box Engine API Rule）】**：`scripts/*.py` 與 `scripts/*.js` 為已封裝完成之黑盒渲染引擎，其精簡函數簽名（10～20 行 API 契約）已直接記載於各對應 `phase2_output/*_spec.md` 規範檔中。**在正常執行流程中，AI 必須直接 `import` 並呼叫這些引擎，嚴禁對 `scripts/*.py` 原始碼執行 `read_file` / `view_file`（除非腳本執行拋出異常需要除錯）**，以極大化節省 Token 與注意力預算。
   - **必讀共用底層與選定之筆風檔**：讀取 [`phase2_output/visual_cognition_principles.md`](visual_cognition_principles.md) ＋ 本次選定之筆風設定檔（如 `config/owner_styles/<style_id>.md` 或 `config/user_styles/<style_id>.md`），將 `Slot 1～8` 規則注入所有生成步驟。
   - **Format A（知識圖譜 `.png`）**：讀取 [`phase2_output/visual_diagram_matplotlib_spec.md`](visual_diagram_matplotlib_spec.md) $\rightarrow$ 直接黑盒 `import` [`scripts/generate_mindmap.py`](../scripts/generate_mindmap.py)（圖內文字受筆風 `Slot 5` 控制）
   - **Format B（結構化深度報告 `.md` + `.pdf` ／ 文體 5：Medium 數據敘事專欄 `.md`）**：讀取 [`phase2_output/document_report_spec.md`](document_report_spec.md) $\rightarrow$ 若為文體 1～4 深度報告則直接黑盒 `import` [`scripts/pdf_report_engine.py`](../scripts/pdf_report_engine.py)；**若為「文體 5：Medium 每週一圖數據敘事專欄（`<= 1,600` 字）」，則僅產出原生相容 `.md` 文稿，免除呼叫 `pdf_report_engine.py` 編譯 A4 PDF**（行文受筆風 `Slot 3 & 4` 控制）
   - **Format C（高階主管簡報 `.pptx`）**：讀取 [`phase2_output/presentation_slide_spec.md`](presentation_slide_spec.md) $\rightarrow$ 直接黑盒 `import` [`scripts/pptx_slide_engine.py`](../scripts/pptx_slide_engine.py)（標題與講稿受筆風 `Slot 4 & 7` 控制）
   - **Format D（量化實證圖表 `.png`）**：讀取 [`phase2_output/quantitative_chart_spec.md`](quantitative_chart_spec.md)（若採 `pure_dataviz`、分配與密度圖形或背景基準分面，同步讀取 **[`phase2_output/distribution_and_density_chart_spec.md`](distribution_and_density_chart_spec.md)**）$\rightarrow$ 直接黑盒 `import` [`scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)（圖內微文案受筆風 `Slot 6` 控制）
   - **Format E（數據儀表板 Web `.html`/`.css`/`.js` + 靜態全景圖 `.png`）**：讀取 [`phase2_output/data_dashboard_spec.md`](data_dashboard_spec.md) + [`phase2_output/quantitative_chart_spec.md`](quantitative_chart_spec.md)（若含分配圖形視角加讀 [`phase2_output/distribution_and_density_chart_spec.md`](distribution_and_density_chart_spec.md)）$\rightarrow$ 直接載入 [`scripts/gephi_palette.js`](../scripts/gephi_palette.js) 與 [`scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)
4. **步驟 4：執行「一次批次生成」或「逐步導學互動推進」**：
   - 若使用者選擇 **「逐步導學互動模式（`step_by_step_tutor`）」**：嚴格遵守 [`distribution_and_density_chart_spec.md`](distribution_and_density_chart_spec.md) 第一節協定——**每次只生成並展示一張圖（或回答同一比較問題的一組分面圖）**，搭配 `Slot 2` 五步完整解說（分析問題、資料篩選與計算、座標與元素讀法、實際發現、適用時機與限制），**解說後立即停下來等待使用者回應**，再依使用者思考方向提出 1 個聚焦問題或推進下一張圖。
   - 若使用者選擇 **「一次批次生成（`batch_generation`）」**：依確認之檔案清單依序完成全部檔案渲染。
5. **步驟 5：逐張視覺驗證、清理交付、Git 單檔對話紀錄推送與獨立網站部署（Mandatory Visual Inspection, Clean Hygiene & Git Deployment）**：
   - 凡生成 `.png`、`.pdf`、`.pptx` 或互動式儀表板，**必須**透過 `view_file`（或瀏覽器預覽）檢視渲染成品：針對 `.pdf` 與 `.pptx`，直接黑盒呼叫 [`scripts/verify_visual_outputs.py`](../scripts/verify_visual_outputs.py) 之 `render_pdf_to_pngs()` / `render_pptx_to_pngs()` 轉出臨時預覽圖，逐頁核對：無文字重疊、無穿線、無溢界、無斷頭框線、字級飽滿易讀、同名類別跨圖表色碼鎖定一致、參考線具白框描邊、極端值底部具定位圓點。
   - **【Medium 每週一圖模式免編譯 PDF 特例】**：當執行「Medium 每週一圖／輕量數據敘事專欄模式」時，**免除呼叫 `scripts/pdf_report_engine.py` 編譯 A4 PDF**，僅針對產出的 1～2 張獨立單面板 `.png` 統計圖執行 `view_file` 視覺驗收，並於驗收後自動執行 `git add`、`git commit` 與 `git push origin main`，在回覆結尾輸出課堂 Google Doc 一鍵複製繳交區塊（含 `01_phase1_socratic_log.md` 之 GitHub `blob/main/...` 單檔完整網址）。
   - 檢驗通過後，立即呼叫 `cleanup_preview_artifacts(output_dir)`（或執行 `python scripts/verify_visual_outputs.py <02_outputs> --cleanup`）刪除 `02_outputs/` 內的暫存渲染中介檔（如 PDF 編譯暫存 `.html`、`_preview_page_*.png`、`_preview_slide_*.png`），確保交付資料夾 100% 乾淨。
   - **【Format E 數據儀表板專屬交付與 Git 網站綁定】**：若產出包含 Format E 互動式網頁儀表板，其正式網站專案檔（`index.html`、`css/`、`js/`、`data/`、`.nojekyll`、`.gitignore`、`README.md`）予以完整保留，並依 [`data_dashboard_spec.md`](data_dashboard_spec.md) 第四節主動詢問或執行**「獨立 Git 儲存庫綁定與 GitHub Pages 線上網站發布」**。

---

## 二、 動態三軸視覺決策引擎（Dynamic Tri-Axial Visual Decision Engine）

> **理論依據**：**認知適配理論（Cognitive Fit Theory, Vessey 1991）** 與 **任務導向圖表分類學（Task-by-Data-Type Taxonomy, Shneiderman 1996）**。當外在視覺表徵的空間拓撲與讀者的內在決策心智模型一致時，問題解決效率最高。

### 軸線一：文章／資料體裁與證據結構（Genre & Evidence Structure）

| 體裁與資料類型 | 核心特徵 | 必備主圖（圖 1：全局架構／破題） | 推薦深挖副圖／數據視覺化 | 推薦報告、簡報與儀表板組合 |
| :--- | :--- | :--- | :--- | :--- |
| **A. 實證研究與多維度數據集**<br>*(Empirical / Dataset)* | 含樣本數 $N$、連續變數分布、跨期／跨區域／多類別結構數據 | **全景三欄式研究拆解圖** 或 **核心四模組脊椎圖**（若為純數據導學則直接以 **直方圖＋KDE** 破題） | 1. **雙軌量化圖表（Format D）**：`editorial_storytelling`（斷崖／配對雙柱）或 `pure_dataviz`（**10 大分配圖形＋背景基準分面圖**）<br>2. **動態多視角數據儀表板**（Format E） | **Format B（文體 2：高階決策備忘錄 或 實證研究報告）** + **Format C（簡報）** + **Format E（數據儀表板）** |
| **B. 策略框架與商業管理**<br>*(Strategic / Management)* | 提出新管理模型、轉型路線或二元對立破局 | **雙軌對比匯流圖** 或 **4×2 階層組塊心智圖** | 1. **2×2 策略定位矩陣圖**<br>2. **多階段演進藍圖 / 閉環系統圖** | **Format B（文體 2：高階決策備忘錄）** + **Format C（簡報）** |
| **C. 系統架構與工程方法**<br>*(System / Architecture)* | 聚焦技術堆疊、資料流向、演算法或治理管線 | **多層次雙腦/管線架構圖** | 1. **時序資料流 / 狀態轉換圖**<br>2. **失效模式與工程對策平行解剖圖** | **Format B（文體 3：方法論實踐藍圖）** + **Format C（簡報）** |
| **D. 跨領域評論與長篇敘事**<br>*(Synthesis / Essay)* | 融合多學科視角、歷史演進與思維重構 | **核心脊椎 + 4 象限宏觀容器圖** | **跨領域類比結構映射對照圖** | **Format B（文體 1：深度綜合評論 或 文體 4：跨域知識卡片）** |
| **E. Medium 每週一圖／輕量數據敘事專欄**<br>*(Medium Data Storytelling Column)* | 傳入 CSV 原始檔 ＋《資料說明書（Data Codebook）》，撰寫 `<= 1,600` 字、含 1～2 張統計圖之公開數據專欄 | **Format D 獨立單面板統計圖 1（`01_chart_hook.png`）**：主色系（如暖杏蜜橘 `#ECA072`）呈現全局現象反差或偏態破題 | **Format D 獨立單面板統計圖 2（`02_chart_drilldown.png`，選配，總圖數限 1～2 張）**：次色系（如霧靄青藍 `#5DBACD`）呈現結構拆解或交叉深挖（**禁止 `ncols=2` 並排子圖**） | **僅產出 Format D（1～2 張獨立單面板 `.png`）＋ Format B 文體 5（`02_medium_article.md` 短專欄）**；不產出 Format A / C / E，且**免除編譯 A4 PDF** |
| **F. 分配與密度圖形逐步導學**<br>*(Step-by-Step Distribution Tutor)* | 傳入 CSV（如村里所得）＋《資料說明書》，學習或探索 10 大分配圖形讀法與限制 | **依序每次只出一張圖**：① 直方圖 $\rightarrow$ ② KDE $\rightarrow$ ③ ECDF $\rightarrow$ ④ Q-Q 圖 $\rightarrow$ ⑤ 箱形圖 $\rightarrow$ ⑥ 小提琴圖 $\rightarrow$ ⑦ 山脊圖 $\rightarrow$ ⑧ 2D 直方圖 $\rightarrow$ ⑨ 2D KDE 等高線 | **進階背景基準疊加分面比較（Context Overlay / Shadow Distribution）四大案例**（逐案獨立呈現，每案結束停下等待回應） | **Format D（`pure_dataviz` 模式逐圖生成）** ＋ 搭配 `rigorous_empirical_stat` 筆風之五步導學解說 |

### 軸線二：核心溝通任務對映表（Task-to-Topology Mapping）

| 溝通任務（Communication Task） | 最佳視覺拓撲（Optimal Visual Topology） | 負責規格檔與引擎 |
| :--- | :--- | :--- |
| **建立全篇宏觀地圖與邏輯脈絡** | **中央脊椎 + $4 \to 2 \to 3$ 階層組塊圖**（`generate_mindmap.py`：`draw_spine_hub_module`） | [`visual_diagram_matplotlib_spec.md`](visual_diagram_matplotlib_spec.md) |
| **拆解二元衝突、回饋迴路與整合破局** | **左右雙軌對抗 + 中央匯流引擎 / 雙迴路圖**（`draw_feedback_loop_pair` / `draw_3x3_pipeline_grid`） | [`visual_diagram_matplotlib_spec.md`](visual_diagram_matplotlib_spec.md) |
| **批判邊界、反例壓力測試與跨域遷移** | **2×2 策略象限矩陣 / 跨領域結構映射專題圖**（`draw_2x2_matrix_quadrants`） | [`visual_diagram_matplotlib_spec.md`](visual_diagram_matplotlib_spec.md) |
| **比較跨階段留存率遞減或同案雙指標反差（`editorial_storytelling`）** | **XY 軸空間重力折線＋直柱複合圖 / 共同基準線配對雙柱＋剪刀差標註圖**（`hcl_color_engine.py`） | [`quantitative_chart_spec.md`](quantitative_chart_spec.md) |
| **探索連續變數分布、偏態、多峰分化與跨組/跨期對照（`pure_dataviz`）** | **10 大分配與密度圖形（直方圖、非負截斷 KDE、ECDF、Q-Q、箱形、小提琴、山脊、2D 直方圖、2D 等高線、背景基準疊加分面圖 Context Overlay）** | [`distribution_and_density_chart_spec.md`](distribution_and_density_chart_spec.md) + [`quantitative_chart_spec.md`](quantitative_chart_spec.md) |
| **拆解多階段成熟度分佈與跨圖接力** | **5 階同質循序漸層 ＋ 雙圖跨面板色相區隔與視覺接力（1+1>2）** | [`quantitative_chart_spec.md`](quantitative_chart_spec.md) |
| **撰寫 Medium 每週一圖／輕量數據新聞專欄（`<= 1,600` 字 ＋ 1～2 張圖）** | **1～2 張獨立單面板 `300 DPI` 統計圖（圖 1 主色破題 $\rightarrow$ 圖 2 次色深挖，內嵌三層分流 `assert` 與精簡官方資料來源圖註［僅附：1.官方資料集網址、2.資料涵蓋期間］）＋ 文體 5 Medium 原生 Markdown 專欄（含文末參考資料來源分離計字）** | [`quantitative_chart_spec.md`](quantitative_chart_spec.md) + [`document_report_spec.md`](document_report_spec.md) |
| **探索多維度數據集（總覽、篩選、排行、增減發散與深鑽明細）** | **不寫死圖表格式之動態數據儀表板（KPI 卡 + 動態多視角互動圖表 + 明細表與 CSV 匯出，引用 `gephi_palette.js`）** | [`data_dashboard_spec.md`](data_dashboard_spec.md) ⇄ [`quantitative_chart_spec.md`](quantitative_chart_spec.md) |
| **提供高密度治理規範、審計清單與完整論述** | **A4 雙模態混合排版 PDF 報告**（`pdf_report_engine.py`：支援 A4 橫向滿版大圖跨頁與三線表） | [`document_report_spec.md`](document_report_spec.md) |
| **進行高階主管會議簡報與決策提案** | **16:9 斷言-證據式（Assertion-Evidence）原生向量投影片**（`pptx_slide_engine.py`） | [`presentation_slide_spec.md`](presentation_slide_spec.md) |

### 軸線三：無損分流擴展鐵律 vs. Medium 單一故事線輕量交付場景（Zero-Loss Expansion vs. Single-Hook Lightweight Delivery）

> **【A2 無損分流擴展鐵律（適用一般文獻／深度報告／簡報）：以「拆圖、擴章、加頁」取代「刪減內容」】**：
> 當第一階段 `01_phase1_socratic_log.md` 第五節收斂出 $> 4$ 個分支（含 `(a) 核心論證主幹分支` 與 `(b) 批判延伸與跨域遷移分支`）時，**嚴禁為了塞進單一畫布而刪減任何細節或批判延伸議題**！單張 2D 視覺畫布維持 3～4 個宏觀大區塊以守住 `12pt` 字級底線，並自動啟動以下跨畫布／跨章節無損擴展：
> - **Format A（知識圖譜拆圖擴展）**：`01` 繪製核心論證主幹（3～4 個核心模組）；`02` 繪製核心機制與架構深挖圖；**`03+` 自動加開「批判邊界、反例壓力測試與跨域類比遷移專題圖」**，完整承載所有延伸分支。
> - **Format B（深度報告動態擴章）**：章節編號依分支總數 $N$ 自然延展（`壹、貳、參、肆、伍、陸、柒...`），讓每個核心主幹與批判延伸分支皆擁有獨立章節、三線表或戰術卡片。
> - **Format C（高階簡報動態加頁）**：中段內容頁隨實質命題數 $N$ 動態加頁（如以 `S1` 雙欄對比呈現正反辯證、以 `S5` 象限呈現邊界條件），並附上完整演講備忘稿。
> - **Format D / E（量化圖表與儀表板擴展）**：自動增加子面板（Subplots）、背景基準分面網格或互動切換視角（Tabs）。

- **場景 1：若使用者於五維度確認中選擇「完整全套產出」**，則依序生成（並可依資料屬性加選或單獨指定 **Format E 數據儀表板**）：
  1. `01_article_master_structure_map.png`（Format A：全篇核心主幹總覽圖）
  2. `02_<specific_mechanism_diagram>.png`（Format A：核心機制/架構深挖圖）
  3. `03_<critical_synthesis_or_quantitative_charts>.png`（Format A 批判延伸與跨域遷移專題圖，及／或 Format D 量化實證圖表）
  4. `01_executive_strategy_report.md` & `.pdf`（Format B：結構化決策報告，嵌入上述高清圖表或 A4 橫向跨頁大圖）
  5. `02_executive_presentation.pptx`（Format C：16:9 原生向量高階主管簡報）
  6. `dashboard/` 或獨立專案目錄（Format E：Git-Ready 零後端互動式 Web 儀表板 `index.html` + `css/style.css` + `js/gephi_palette.js` + `js/dashboard.js` + `data/` + `.nojekyll` + `.gitignore` + `README.md` 及對應靜態全景圖 `.png`）
- **場景 2：若任務屬於「Medium 每週一圖／輕量數據敘事專欄模式」**，則啟動**單一故事線輕量路由（Single-Hook Lightweight Route）**，於 `02_outputs/` 僅生成：
  1. `01_chart_hook.png`（及選配之 `02_chart_drilldown.png`，嚴格限制 **1～2 張各自獨立的單面板 `300 DPI` `.png` 統計圖**與繪圖腳本 `generate_charts.py`，**禁止 `ncols=2` 並排雙子圖**）
  2. `02_medium_article.md`（Format B 文體 5：正文絕對 `<= 1,600` 字之 Medium 100% 原生相容專欄文稿，含 `---` 分隔之「參考資料來源（僅附：1.官方資料集網址、2.資料涵蓋期間）」及雙軌字數統計，**免除編譯 PDF**）
  3. 透過 `view_file` 驗收 1～2 張 `.png` 圖表無誤後，自動將整個 session（含 `data/<原檔名>.csv`、`00_source_article.md`、`01_phase1_socratic_log.md` 與 `02_outputs/`）執行 `git add -A && git commit -m "..." && git push origin main`，並在回覆結尾印出課堂 Google Doc 一鍵複製繳交區塊。
- **場景 3：若任務屬於「分配與密度圖形逐步導學互動模式（`step_by_step_tutor`）」**，則啟動 **[`distribution_and_density_chart_spec.md`](distribution_and_density_chart_spec.md)**：每次僅生成 1 張圖（如 `01_histogram.png`），配合 `Slot 2` 五步導學解說並更新 `01_phase1_socratic_log.md`，等待使用者回應後再推進下一張圖。
