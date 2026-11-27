# 階段二第一層總路由與三層漸進式決策導航中心（Phase 2 Layer 1 Router）

> **單一職責定位（Single Responsibility）**：本檔為 Phase 2 的**第一層極簡總路由（~4 KB）**，負責在極低認知負荷下協助使用者完成 **「第一層決策：決定本次要生成 A / B / C / D / E 哪幾類產出與任務走向」**，並嚴格引導 AI 依 **「三層漸進式討論決策（方案甲：分步緩衝）$\rightarrow$ 終端最小葉節點規格檔按需載入」** 推進。第二層（結構骨架）與第三層（設計武器庫／筆風／配色定裝）由 [`advisors/`](./advisors/) 各獨立顧問檔負責，未選中的格式**100% 零讀取**。

---

## 零、 Phase 2「三層漸進式討論決策關卡（3-Layer Progressive Decision Funnel — 方案甲）」

> [!IMPORTANT]
> **核心鐵律（Progressive Lazy-Loading & Pause Gate）**：
> 為避免大量規格文字同時湧入稀釋 AI 注意力（$O(1)$ 讀取複雜度），並賦予使用者充足的討論緩衝空間，Phase 2 嚴格依下列 **三層決策順序** 逐層收斂，**除非使用者已在當次提示詞明確指定或於 `config/user_preferences.json` 設為 `"auto_apply_default": true`，否則每層提案後必須停下來等待使用者確認，絕不擅自代選或提前載入未選中之規範檔！**

### 【第一層決策（Layer 1 — 本檔案負責）：決定生成大類範圍（A / B / C / D / E）】

進入 Phase 2 時，先盤點 Phase 1（`01_phase1_socratic_log.md`）或輸入資料集（`data/<原檔名>.csv` ＋ `00_source_article.md`）之素材特性，依下表提出第一層宏觀格式建議：

| 素材體裁與任務場景 | 核心特徵 | 建議生成大類組合（請使用者拍板 A / B / C / D / E） |
| :--- | :--- | :--- |
| **A. 實證研究與多維度數據集**<br>*(Empirical / CSV + Data Codebook)* | 含樣本數 $N$、連續變數分布、跨期／跨區域／多類別結構 | **Format D（量化統計圖表）＋ Format B（深度報告）＋ Format C（簡報）**，可加選 **Format E（互動數據儀表板）** 或 **Format A（知識圖譜）** |
| **B. 策略框架與商業管理**<br>*(Strategic / Management)* | 提出管理模型、轉型路線、因果對比或四象限治理 | **Format A（知識圖譜）＋ Format B（深度報告）＋ Format C（簡報）** |
| **C. 系統架構與工程方法**<br>*(System / Architecture)* | 聚焦技術堆疊、雙腦管線、資料流向或失效防禦 | **Format A（知識圖譜）＋ Format B（深度報告）＋ Format C（簡報）** |
| **D. 跨領域評論與長篇敘事**<br>*(Synthesis / Essay)* | 融合多學科視角、理論演化與思維重構 | **Format A（知識圖譜）＋ Format B（深度報告）** |
| **E. Medium 每週一圖／輕量數據專欄**<br>*(Medium Data Storytelling Column)* | CSV＋《資料說明書》，聚焦單一數據故事寫 `<= 1,600` 字公開專欄 | **僅 Format D（1～2 張獨立單面板統計圖）＋ Format B（Medium 專欄）**；不產出 A / C / E，免編譯 PDF |
| **F. 分配與密度圖形逐步導學**<br>*(Step-by-Step Distribution Tutor)* | CSV＋《資料說明書》，逐步學習 10 大分配圖形讀法與限制 | **Format D（逐步導學模式：一次只畫 1 張圖＋五步解說）** |

- **分步緩衝與智慧直通規則（Pause Rule & Smart Fast-Forward）**：
  1. **預設分步確認（方案甲）**：向使用者簡明列出本次建議生成的格式組合（Format A～E）與推薦理由（若同時建議或勾選 **Format B 深度報告 ＋ Format C 簡報**，附註提醒採雙軌分工：完整細節留存於 Format B，Format C 進入 Layer 2 再依觀看視距與口說／閱覽需求決定字級地板），**立即停下來等待使用者確認第一層範圍**（此時嚴禁提前開啟第二層顧問檔或任何終端 `*_spec.md`）。使用者確認後，立即建立 `reading_sessions/<YYYYMMDD_主題簡稱>/02_phase2_generation_blueprint.md` 並寫入 **第 1 節（Layer 1 產出範圍與路由決策）**。
  2. **智慧直通特例（Smart Fast-Forward）**：若使用者於提示詞中已明確指明產出格式（例如：「幫我畫圖並寫 Medium 專欄」即已鎖定 `Format D + B`；或「只做統計圖表」即鎖定 `Format D`），則自動完成第一層判定，**直接建立 `02_phase2_generation_blueprint.md` 寫入第 1 節並跳轉第二層**，不再重複詢問第一層！

---

### 【第二層決策（Layer 2 — 按需分類載入）：決定各選定格式的「具體骨架與型態」】

第一層範圍拍板後，**僅讀取第一層有勾選之格式對應的第二層結構顧問檔**（未勾選之格式 100% 零讀取）：
- 若選 **Format A（知識圖譜 `.png`）** $\rightarrow$ 讀取 [`advisors/layer2_advisor_a_diagram.md`](advisors/layer2_advisor_a_diagram.md)（診斷 T1～T5 網格拓撲與無損分圖規劃）
- 若選 **Format B（報告／專欄）** $\rightarrow$ 讀取 [`advisors/layer2_advisor_b_report.md`](advisors/layer2_advisor_b_report.md)（診斷文體 1～4 A4 PDF vs. 文體 5 Medium 專欄與章節大綱）
- 若選 **Format C（高階簡報 `.pptx`）** $\rightarrow$ 讀取 [`advisors/layer2_advisor_c_slide.md`](advisors/layer2_advisor_c_slide.md)（Format C Step 1 定位顧問：確立北極星認知轉移、獨立閱覽／兩棲 vs. 現場口說情境、由觀看視距 $D/H$ 依 DISCAS 公式反推 `min_font_pt` 硬底線，並規劃單一議題章節清單；**此階段不提前鎖死版型代號**）
- 若選 **Format D（統計圖表）或 Format E（數據儀表板）** $\rightarrow$ 讀取 [`advisors/layer2_advisor_de_chart.md`](advisors/layer2_advisor_de_chart.md)（執行資料結構四維快篩與「8 大溝通意圖 × 30+ 圖表決策樹」，推薦首選／備選圖型、對應圖表家族，以及 **Format D 內部**批次／導學出圖節奏）

向使用者提出第二層具體結構與圖表選型建議，**停下來等待使用者確認第二層骨架**；拍板後立即將選型結果、討論取捨理由與資料消歧決策寫入 `02_phase2_generation_blueprint.md` **第 2 節**。

---

### 【第三層決策（Layer 3 — 最後決策層）：全格式「設計武器庫開關 × 筆風 × 配色」全域定裝】

第二層具體結構與圖表清單拍板後，讀取 **[`advisors/layer3_advisor_design_style_color.md`](advisors/layer3_advisor_design_style_color.md)**，針對所有確定產出的檔案統一或混搭確認「表達三支柱」：
1. **全格式設計光譜與轉譯武器庫開／關（套用至所有選定的 A/B/C/D/E）**：
   - 🔘 **模式 1：`standard_rigorous`**（標準嚴謹模式 — 武器庫關閉）
   - 🔘 **模式 2：`editorial_narrative`**（資料八／經濟學人／數據百閱：編輯室權威敘事設計開啟）
   - 🔘 **模式 3：`bespoke_metaphor`**（開放式創意隱喻武器庫開啟：不限縮固定模板之純幾何 Form-as-Metaphor ＆ RE:LAB IDE 跨工具材質管線，按需單開 `creative_armory/INDEX.md`；**若含 Format C 開啟模式 3，須主動推薦 `Tier 1 / Tier 2 / Tier 3` 並揭露設計長相、改字彈性與生成成本差異，由使用者拍板等級並產出 Topic Art Direction DNA 卡**）
2. **筆風設定檔（Writing Style Profile）**：`Slot 1～8` 100% 全域穿透控制（支援跨檔混搭）。
3. **分層顏色設定集與版面／交付細節（Layered Color Sets, Layout & Delivery Details）**：鎖定色票 vs. CIELAB 主題語義微調色階（`derive_thematic_palette`／Format C 動態主題色票）、PDF 字體（`modern_sans` vs. `clreq_kaiti`）、跨格式接力確認節奏與佇列（`default_delivery_cadence = "sequential_confirm"`、`default_delivery_queue = ["D", "A", "B", "C", "E"]`），以及 Format C 方案 C 內部品管偏好（`default_slide_qa_mode = "option_c_2x2_and_high_risk"`）。

**停下來等待使用者拍板第三層定裝**，隨即於 `02_phase2_generation_blueprint.md` 補齊 **第 3～5 節（表達三支柱定裝、使用者客製細節覆寫、跨格式接力佇列與終端最小葉節點／交付清單）** 後再進入終端執行層（**嚴禁將 Phase 2 生成細節回寫塞入 `01_phase1_socratic_log.md`，亦不在 `01` 或 Medium 繳交區塊附掛 `02` 連結**）。

---

### 【時機 A 漸進持久化：`02_phase2_generation_blueprint.md` 標準範本（約 40～80 行精簡工作錨點）】

> [!IMPORTANT]
> **實時漸進寫入與零漂移鐵律（Timing A Progressive Persistence）**：
> - **分段落盤**：**Layer 1 拍板 $\rightarrow$ 寫第 1 節**；**Layer 2 拍板 $\rightarrow$ 寫第 2 節**；**Layer 3 拍板 $\rightarrow$ 補齊第 3～5 節**，隨後始得進入終端生成；過程中若有熱修改或例外調整，同步更新第 4 節或對應決策項。
> - **精簡分工與跨檔不互連**：本檔篇幅控制在 **~40～80 行** 精簡決策錨點，**嚴禁複製 Phase 1 思辨內容或貼入冗長 `*_spec.md` 條文**；同時維持 `01_phase1_socratic_log.md` 獨立自洽，**不在 `01` 或 Medium 課堂繳交區塊加入本檔網址或交叉連結**。

```markdown
# 【第二階段生成藍圖與決策紀錄】<文章或數據專案主題名稱>
- **建立時間**：YYYY-MM-DD | **Phase 1 依據**：`./01_phase1_socratic_log.md`（若 Fast-Track 則為 `./00_source_article.md`） | **狀態**：Layer 1 確認 / Layer 2 確認 / Layer 3 定裝完成 / 已交付

## 1. Layer 1：產出格式範圍與路由決策（Layer 1 拍板後寫入）
- **任務體裁與路由模式**：<實證數據 / 策略商業 / 系統架構 / 跨領域評論 / Medium 每週一圖 / 10 大分配導學>（預設分步 / 智慧直通 / Fast-Track）
- **選定產出大類**：`[ ] Format A` / `[ ] Format B` / `[ ] Format C` / `[ ] Format D` / `[ ] Format E`
- **範圍取捨與排除理由**：<簡述為何選定此組合、為何排除其他格式，或 A2 無損擴展 vs. Medium 輕量路由判定>

## 2. Layer 2：各格式結構骨架、圖表選型與討論取捨（Layer 2 拍板後寫入）
- **Format A（知識圖譜）**：<分圖數 `01/02/03+`、各圖承載分支與 T1～T5 拓撲選擇及取捨理由；未選填「無」>
- **Format B（報告／專欄）**：<文體 1～4 PDF 或文體 5 Medium、章節／七步大綱重點、配圖分工與體裁取捨理由；未選填「無」>
- **Format C（簡報）**：<北極星認知轉移、使用情境（獨立閱覽／兩棲 vs. 現場口說）、觀看視距 $D/H$ 與 DISCAS 反推 `min_font_pt` 地板（`>=12.0pt`）、單一議題章節清單；**此階段不提前鎖死版型代號**，待 Step 3 文案凍結與 Step 4A 純文字配置對齊後再鎖入 `02c_slide_spec_lock.json`；未選填「無」>
- **Format D / E（圖表／儀表板）**：
  - **Format D 內部推進節奏與 E 架構**：`batch_generation` / `step_by_step_tutor`（**僅作用域為 Format D 統計圖表內部**之出圖與導學節奏，不影響跨格式接力確認；若含 E：呈現模式 A / B / C）
  - **圖表選型與討論取捨**：<逐圖列出 `檔名 -> 選定圖型` ＋ **為何選此圖／為何捨棄備選圖的討論理由**>
  - **資料口徑與消歧拍板**：<`df_detail` 口徑、原表 `df_other` 消歧選項 1/2、缺失值與前處理血統提醒（若適用）>

## 3. Layer 3：表達三支柱全域定裝（Layer 3 拍板後寫入）
- **支柱 1（設計光譜武器庫）**：`standard_rigorous` (模式 1) / `editorial_narrative` (模式 2) / `bespoke_metaphor` (模式 3)（若含 Format C 開啟模式 3，註明使用者拍板之 **`Tier 1 / Tier 2 / Tier 3`** 與 **Topic Art Direction DNA** 核心視覺母題、色票性格與版面節制紅線；若混搭請註明各檔對應模式）
- **支柱 2（筆風設定檔 `Slot 1～8`）**：`<style_id>.md`（若有跨檔混搭或臨時熱修改請註明）
- **支柱 3（分層配色、版面與交付細節）**：`chart_palette`（鎖定色票 vs. `derive_thematic_palette` 主題色階）＋ `document_theme` ＋ PDF 字體（`modern_sans` / `clreq_kaiti`）＋ 跨格式交付節奏與佇列（預設 `sequential_confirm`，佇列 `D ➔ A ➔ B ➔ C ➔ E`）＋ Format C 品管模式（預設 `option_c_2x2_and_high_risk`）＋ Git 同步偏好
- **定裝取捨理由**：<簡述為何採此設計模式／筆風／色票配置，或為何捨棄其他選項>

## 4. 使用者客製細節與例外覆寫（User Special Overrides）
- **內容／敘事特別要求**：<例如：必須點名某案例、特定比較對象、禁用某類用語或保留特定專有名詞；無則填「無」>
- **視覺／排版細節微調**：<例如：指定聚光燈強調對象、基準線標籤、Format C 目標基準字級 `target_body_pt` 或特定配色微調；無則填「依標準規格執行」>

## 5. 終端最小葉節點規格、跨格式接力佇列與交付清單（Terminal Spec & Output Manifest）
- **跨格式接力交付佇列**：`default_delivery_cadence = "sequential_confirm"` ➔ 按 **`D ➔ A ➔ B ➔ C ➔ E`** 順序執行本次選定子集（每完成單一格式並獲使用者確認後，始開啟下一格式規格檔動工；全部確認完成後再統一執行 Git 同步）
- **按需載入規格檔**：<僅列出本次實際開啟之 `*_spec.md` 與 `chart_family*.md` 清單，確保零多餘載入>
- **預計交付檔案（`./02_outputs/`，Format C 另於根目錄存 `02c_slide_spec_lock.json`）**：
  - [ ] `<01_xxx.png>` — <一句話用途定位>
  - [ ] `<02_xxx.md / .pdf / .pptx>` — <一句話用途定位>
```

---

## 一、 終端執行層：三層拍板後之跨格式逐項接力交付流程（Sequential Per-Format Delivery）

> [!IMPORTANT]
> **【三層全局拍板 ➔ `D ➔ A ➔ B ➔ C ➔ E` 逐格式接力確認鐵律】**：
> 1. **全域決策先行，逐格式接力動工**：三層決策全部拍板並完整寫入 `02_phase2_generation_blueprint.md`（第 1～5 節）後，依 `config/user_preferences.json` 之 **`default_delivery_cadence = "sequential_confirm"`**，按預設佇列 **`default_delivery_queue = ["D", "A", "B", "C", "E"]`** 依序執行本次選定的格式子集。
> 2. **單一格式完成＋驗收＋使用者確認 ➔ 始得進入下一個格式**：每輪**僅開啟當前單一格式**對應之最小葉節點規格檔進行生成與視覺品管驗收，並**向使用者交付確認**；獲明確確認後始開啟佇列下一個格式的規格檔並動工（嚴禁一口氣未經確認連跑全部格式）。
> 3. **作用域嚴格區分**：`batch_generation` 與 `step_by_step_tutor` **僅作用域為 Format D 統計圖表內部**（決定多張統計圖是一次畫完或逐張導學），**不影響**跨格式 `D ➔ A ➔ B ➔ C ➔ E` 的逐項接力確認紀律。
> 4. **全部格式確認完再統一 Git 同步**：待本次選定之全部格式皆完成交付並獲使用者確認後，再統一執行藍圖結案勾稽與 Git 同步。

每個格式輪次嚴格依 **步驟 1～4** 推進，待佇列中全部選定格式皆交付並獲使用者確認後，再統一執行 **步驟 5（結案與 Git 同步）**：

1. **步驟 1（每輪）：錨定藍圖客製條款並載入跨格式底線與當前格式筆風契約**：
   - 對照 `02_phase2_generation_blueprint.md` 第 4 節（使用者客製細節覆寫）與第 5 節（跨格式接力佇列與按需載入規格檔清單），讀取 [`visual_cognition_principles.md`](visual_cognition_principles.md) ＋ 當前格式選定之單一筆風設定檔（`config/owner_styles/<style>.md` 或 `config/user_styles/<style>.md`）。
2. **步驟 2（每輪）：僅按需載入當前輪次單一格式之最小葉節點規格檔（Leaf Micro-Specs）**：
   - **若當前格式於第三層開啟「模式 2 (`editorial_narrative`)」** $\rightarrow$ 加讀 **[`editorial_narrative_spec.md`](editorial_narrative_spec.md)**；**若開啟「模式 3 (`bespoke_metaphor`)」** $\rightarrow$ 先讀 **[`creative_armory/INDEX.md`](creative_armory/INDEX.md)** 並按需單開對應之原子案例卡（模式 1 則兩者皆略過不讀）。
   - **輪到 Format D（或 Format E 含圖表）** $\rightarrow$ 讀取 [`quantitative_chart_spec.md`](quantitative_chart_spec.md)（圖表共通核心契約 SSOT）＋ **僅開啟第二層選定之對應圖表家族微檔（5 選 1～2）**：
     - 家族 1（排行、跨距與目標偏差：克里夫蘭點陣圖、棒棒糖、啞鈴、斜坡、子彈、蝴蝶金字塔、柏拉圖）$\rightarrow$ [`chart_family1_ranking_and_deviation.md`](chart_family1_ranking_and_deviation.md)
     - 家族 2（時序趨勢、斷崖與同案反差：斷崖複合、時期色帶＋事件折線、配對雙柱剪刀差、面積、範圍甘特）$\rightarrow$ [`chart_family2_trend_and_comparison.md`](chart_family2_trend_and_comparison.md)
     - 家族 3（結構佔比、雙維馬賽克、瀑布與流向：`4+1` 堆疊、馬賽克、瀑布圖、矩形樹圖、巢狀環／旭日／圓堆、桑基與弦圖）$\rightarrow$ [`chart_family3_composition_and_flow.md`](chart_family3_composition_and_flow.md)
     - 家族 4（10 大分配與密度圖形＋背景基準分面）$\rightarrow$ [`distribution_and_density_chart_spec.md`](distribution_and_density_chart_spec.md)
     - 家族 5（多維象限、熱力矩陣與空間複合：波士頓四象限氣泡、突出顯示熱力表、雷達圖、主圖＋排行副卡）$\rightarrow$ [`chart_family5_multivariate_and_spatial.md`](chart_family5_multivariate_and_spatial.md)
   - **輪到 Format A** $\rightarrow$ 讀取 [`visual_diagram_matplotlib_spec.md`](visual_diagram_matplotlib_spec.md)
   - **輪到 Format B 文體 1～4（深度報告 `.md`/`.pdf`）** $\rightarrow$ 讀取 [`document_report_spec.md`](document_report_spec.md)
   - **輪到 Format B 文體 5（Medium 專欄 `.md`，免 PDF）** $\rightarrow$ 讀取 [`medium_column_spec.md`](medium_column_spec.md)
   - **輪到 Format C（簡報 `.pptx`）** $\rightarrow$ 讀取 [`presentation_slide_spec.md`](presentation_slide_spec.md)（依五步內容優先流程推進：`Step 3` 撰寫每頁文案並 **⏸️ 停頓審核凍結**至 `02c_slide_spec_lock.json` ➔ `Step 4A` 輸出純文字逐頁配置＋配圖對齊表並 **⏸️ 停頓對齊** ➔ `Step 4B` 確定性渲染 `.pptx`；若需掛載先前 Format D 圖表且縮放 `<0.80×`、高視距 `min_font_pt >= 14.0pt` 或原圖含重標／事實小卡，從同腳本另存專用 `*_slide.png` 而不覆寫原圖）
   - **輪到 Format E（數據儀表板 Web ＋ 全景圖）** $\rightarrow$ 讀取 [`data_dashboard_spec.md`](data_dashboard_spec.md)
3. **步驟 3（每輪）：底層引擎黑盒呼叫鐵律（Black-Box Engine API Rule）**：
   - 直接 `import` [`../scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)、[`../scripts/generate_mindmap.py`](../scripts/generate_mindmap.py)、[`../scripts/pdf_report_engine.py`](../scripts/pdf_report_engine.py)、[`../scripts/pptx_slide_engine.py`](../scripts/pptx_slide_engine.py) 或前端 [`../scripts/gephi_palette.js`](../scripts/gephi_palette.js)。**日常執行嚴禁對 `scripts/*.py` 與 `scripts/*.js` 原始碼呼叫 `read_file`（除非除錯）**。
4. **步驟 4（每輪）：單一格式生成、內部品管驗收與 ⏸️ 接力確認關卡**：
   - 產出當前格式檔案（若為 **Format D**，依藍圖選定於 Format D 內部執行 `batch_generation` 或 `step_by_step_tutor`）。
   - 凡生成 `.png`、`.pdf`、`.pptx` 或儀表板，必須呼叫 [`../scripts/verify_visual_outputs.py`](../scripts/verify_visual_outputs.py) 轉圖並實地視覺檢查（Format C `Step 5` 依 `default_slide_qa_mode = "option_c_2x2_and_high_risk"` 執行方案 C 三階內部品管：`4×4` 接觸表 ＋ `2×2` 高清四宮格 ＋ `high_risk_slides` 滿版精檢，必要時以單頁重繪覆檢），驗畢執行 `--cleanup` 清理暫存預覽圖。
   - **⏸️ 單格式接力確認**：向使用者交付當前格式成果並勾選藍圖第 5 節對應檔案 `- [x]`，**待使用者確認無誤後，始進入佇列下一個格式**。
5. **步驟 5（全佇列確認完畢後僅執行一次）：全格式結案、藍圖更新與統一 Git 同步**：
   - 待佇列中所有選定格式皆交付並獲使用者確認後，將 `02_phase2_generation_blueprint.md` 標頭狀態更新為 **`已交付`**；最後統一按需開啟 [`../setup/git_sync_and_evolution_protocol.md`](../setup/git_sync_and_evolution_protocol.md) 執行公私雙倉庫 Git 同步、獨立儀表板網站 GitHub Pages 發布、Medium 課堂繳交連結推送或 Step E1～E3 靈感進化流程。

---

## 二、 A2 無損分流擴展鐵律 vs. Medium 單一故事線輕量路由

> **【A2 無損分流擴展鐵律（適用一般文獻／深度報告／簡報）】**：
> 當 Phase 1 收斂出 $> 4$ 個分支（含 `(a) 核心論證主幹` 與 `(b) 批判延伸與跨域遷移`）時，**嚴禁為了塞進單一畫布而刪減任何細節或批判延伸議題**！單張畫布維持 3～4 個宏觀容器以守住字級底線，並自動以 **拆圖（Format A `01`/`02`/`03+`）、擴章（Format B `壹～柒...`）、動態加頁（Format C）、多子圖／分頁（Format D/E）** 無損承載。
>
> **【Medium 每週一圖單一故事線輕量路由】**：
> 僅產出 **1～2 張各自獨立的單面板 `300 DPI` `.png` 圖表**（禁止 `ncols=2` 並排雙子圖）＋ **正文 `<= 1,600` 字原生 Markdown 專欄**（含 `---` 分離計字之官方資料來源與課堂繳交區塊），**免除編譯 A4 PDF**。
