# 視覺認知與設計規範（Visual Cognition & Design Principles）

> **單一職責定位（Single Responsibility）**：本檔為 Phase 2 **五大產出格式（Format A 知識圖譜、Format B 決策報告、Format C 簡報、Format D 量化圖表、Format E 數據儀表板）唯一共用的視覺認知底層規範**。凡屬跨格式通用的組塊階層、筆風設定檔 8 大插槽全域穿透綁定、分層式色彩配置與字體下限，統一於本檔定義；各專項規格檔（`*_spec.md`）僅規範該媒體專屬的幾何排版與渲染技術，不重複贅述本檔原則。

---

## 一、 單一畫布階層組塊、平行對齊與多畫布無損擴展法則（Per-Canvas $4 \to 2 \to 3$ Chunking & Zero-Loss Expansion）

- **理論依據**：**工作記憶容量極限（Working Memory Capacity $4 \pm 1$, Cowan 2001）**、**格式塔共同區域原則（Law of Common Region, Palmer 1992）** 與 **組塊理論（Chunking, Miller 1956）**。
- **跨格式設計標準**：
  1. **單一視覺畫面 $4 \to 2 \to 3$ 階層組塊結構**：任何**單一視覺畫面**（單張圖譜、單頁簡報、報告單一模組或儀表板頂欄）的頂層宏觀容器（Macro Zones / KPI 頂欄）嚴格控制在 **$3 \sim 4$ 個**（單張畫布絕不超過 4 個）；每個宏觀容器內收納 **$2 \sim 3$ 張子卡片（Cards）**；每張子卡片內收納 **$2 \sim 3$ 條核心論點（Bullets）**。
  2. **無損分流擴展鐵律 vs. Medium 單一故事線收斂特例**：
     - **一般文獻／深度報告／簡報模式（以「拆圖、擴章、加頁」取代刪減內容）**：Phase 1 Step 5 收斂出的「核心論證主幹分支」與「批判延伸／跨域遷移分支」不論總數多少（如 $5 \sim 8+$ 個分支），**嚴禁為了塞進單張 $4$ 區畫布而刪減任何細節或批判性議題**！當總分支數 $> 4$ 時，Phase 2 強制啟動多畫布／多章節擴展（Format A 自動拆分為 `01` 主幹圖、`02` 機制深挖圖、`03+` 批判延伸與跨域遷移專題圖；Format B 動態擴增章節 `壹～柒...`；Format C 動態加頁；Format D/E 增加面板或互動視角）。
     - **Medium 每週一圖／輕量數據敘事專欄模式（Single-Hook Convergence）**：針對公開數據新聞與課堂「每週一圖」作業，聚焦**單一核心數據故事主軸**，僅產出 **1～2 張各自獨立之單面板（Single-Panel）`300 DPI` `.png` 統計圖（禁止 `ncols=2` 橫向並排子圖）** ＋ **正文 `<= 1,600` 字之 Medium 原生 Markdown 專欄（免除編譯 A4 PDF）**。
  3. **同類維度水平平行對齊（Parallel Row Alignment）**：當呈現並列的維度、階段或方案時，各卡片內部的條目必須按相同屬性（依當前筆風設定檔 `Slot 1` 與 `Slot 4` 定義之三階資訊展開順序）嚴格水平對齊，支援視線橫向掃描比對。
  4. **留白呼吸比（Whitespace Ratio）**：資訊圖譜、量化圖表與數據儀表板留白 $\ge 25\%$，簡報投影片留白 $\ge 35\%$，PDF 報告透過頁邊距與段落間距維持視覺呼吸感。

---

## 二、 筆風設定檔解耦與 8 大插槽 100% 全域穿透綁定法則（Decoupled Writing Style Profiles & 100% Slot Penetration）

- **設計哲學與徹底解耦原則（Full Decoupling of Visual Geometry vs. Writing Style）**：
  - 底層視覺規範僅定義「空間幾何、字級、留白與色彩對比」，**絕對不寫死任何單一行文語氣或錨點格式**（原寫死之「白話直覺先行、由淺入深」已抽離為擁有者專屬筆風檔 [`../config/owner_styles/plain_first_progressive.md`](../config/owner_styles/plain_first_progressive.md)）。
  - 所有生成內容的語氣、資訊展開順序、標題句型、卡片錨點、圖譜箭頭謂詞、統計圖表微文案、簡報講稿與禁用詞，**100% 由當前啟用之「筆風設定檔（Writing Style Profile）」動態控制**（支援不同輸出格式交叉指定不同筆風檔）。
- **作者私人筆風庫 vs. 外部使用者隔離（Owner-Only Style Isolation）**：
  - 當本機 Git 身分驗證為擁有者 `markyang20040112-source` 時，直接讀取 [`../config/owner_styles/`](../config/owner_styles/) 下之專屬筆風庫（`plain_first_progressive.md`、`rigorous_empirical_stat.md`、`editorial_data_journalism.md`）。
  - 當外部新使用者執行時，系統嚴格隱藏並隔離 `config/owner_styles/`，僅依空白結構模板 [`../config/styles/_style_schema_template.md`](../config/styles/_style_schema_template.md) 讀取或生成存放於 `config/user_styles/` 的使用者自訂筆風檔。
- **8 大全生成場景控制插槽（Slots 1～8）跨格式強制映射表**：
  1. **`Slot 1: Core_Persona_And_Progression`**：控制全格式共通之寫作者人設、語氣冷熱度與三階資訊展開順序。
  2. **`Slot 2: Interactive_Guidance_Tone`**：控制 Phase 1 蘇格拉底提問口吻與 Phase 2「一次一張圖逐步導學互動模式」之五步解說骨架。
  3. **`Slot 3: Prose_And_Narrative_Rhythm`**：控制 Format B（深度報告與 Medium 專欄）之散文段落長度、破題句式、標點與粗體強調密度。
  4. **`Slot 4: Structured_Blocks_And_Captions`**：控制 Format B/C 表格與卡片條目開頭錨點格式（`Anchor_Format`）、公式導讀與 `<figure>` 圖說規範。
  5. **`Slot 5: Knowledge_Diagram_Copy`**：控制 Format A（知識圖譜 `.png`）之宏觀分區大標、子卡片標題、有向箭頭「謂詞膠囊（`Predicate_Verbs`）」動詞風格與底部 Takeaway 橫幅語氣。
  6. **`Slot 6: Chart_And_Dashboard_MicroCopy`**：控制 Format D（量化統計圖表 `.png`）與 Format E（數據儀表板 Web）之主副標題公式、X/Y 座標軸籤、圖內標註氣泡（`Callouts`）、基準線說明、KPI 卡與網頁 Tooltip 解說微文案。
  7. **`Slot 7: Slide_Headline_And_Speaker_Notes`**：控制 Format C（高階簡報 `.pptx`）之 Zone 1 斷言標題、Zone 3 行動橫幅與 `Speaker_Notes` 口語化講稿。
  8. **`Slot 8: Notation_Terminology_And_Guardrails`**：控制全格式之數值與單位換算、專有名詞中英呈現格式、偏好詞白名單（`Whitelist`）、絕對禁用詞黑名單（`Banned_Cliches`）與 Few-Shot 正反校準。
- **三態參數解析與即時熱修改（Tri-State Resolution & Hot-Reload）**：
  - 筆風檔內標記為 **`[USER_LOCKED]`** 者強制 100% 遵守；標記為 **`[SCENARIO_PRESET]`** 者依情境套用；標記為 **`[AI_ADAPTIVE]`** 者由 AI 依 `Slot 1` 主基調與當下資料特性自動推導最協調寫法。若使用者於對話中臨時要求調整語氣或用詞，立即局部熱修改並於該次生成生效。

---

## 三、 跨格式字級、行寬與漢字換行規範（Typography, Line Measure & CJK Wrapping）

- **理論依據**：**大字級與長行寬閱讀效率研究（Dyson 2004; Tinker 1963）** 與 **前注意特徵處理（Preattentive Processing, Ware 2020）**。過小的字級或過度壓縮的短行寬會強迫眼球頻繁折返（Saccadic Eye Movements），大幅拉高閱讀疲勞。
- **字體優先序**：統一使用無襯線正黑體（`Microsoft JhengHei`、`PingFang TC`、`Noto Sans CJK TC`；Format B 另支援大專院校傳統中文標楷體 `DFKai-SB` 模式，可由筆風檔 `linked_defaults.pdf_theme` 或生成前五維度確認指定），嚴格建立 **3 階字重對比**（標題 Bold $\ge 1.35\times$ 內文 Regular）。
- **五大產出格式字級與行寬權威基準表（與各 `*_spec.md` 100% 同步）**：

| 產出格式 | 畫布 / 頁面基準 | 主標題 / 斷言字級 | 區塊 / 卡片標題 | 內文 / 條目字級 | 膠囊標籤 / 橫幅 / 註腳 | 單行最佳漢字寬度 / 幾何配置 |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Format A：知識圖譜** | `28" × 18.5"` (`240 DPI`) | `23.5pt` | `14.6~15.0pt`<br>*(分區 `13.6pt`)* | **`11.8~12.5pt`** | **`10.2~10.8pt`**<br>*(底橫幅 `12.4~14.4pt`)* | **`32~36 漢字/行`**（每點 `60~66 字` 折 2 滿行，填滿卡片 `88%~92%`；文案受 `Slot 5` 控制） |
| **Format B：決策報告 & Medium 專欄** | `A4`（印域寬 `189mm`，支援橫向圖表專頁）或 **Medium 原生 `.md`** | `20~24pt`<br>*(Medium `#`)* | `12.0~15.0pt`<br>*(Medium `###`)* | **正文 `p`：`10.6~11.2pt`**<br>*(學術個案可微調 `9.2~10.5pt`)*<br>**表格/卡片 (`td`/`.card-body`)：`9.0~10.5pt`**<br>**文體 5 Medium：正文 `<=1,600` 字（免 PDF）** | **`8.8~9.8pt`**<br>*(Medium 文末 `---` 參考資料來源不計入 1,600 字)* | **`38~44 漢字`**（正文行高 `1.62~1.75`；文體 5 禁用自訂 HTML/表格，每段 3～4 行適配手機閱讀；文案受 `Slot 3 & 4` 控制） |
| **Format C：簡報投影片** | `16:9`（`13.333" × 7.5"`） | **Zone 1 斷言：`19.5~22pt`**<br>*(S0 首尾頁：`26~32pt`)* | `14.5~16.0pt` | **雙欄卡 (`S1`)：`13.0~14.5pt`**<br>**三/四欄卡 (`S2`/`S3`/`S7`)：`11.5~12.5pt`** | **左上章節膠囊：`9.5pt`**<br>**Zone 3 底部橫幅：`12.5~14.0pt`** | **雙欄：`22~26 漢字/行`**；**三/四欄：`16~19 漢字/行`**（每列槽 $\le 45$ 漢字，垂直置中；文案受 `Slot 4 & 7` 控制） |
| **Format D：量化圖表** | 單面板 `12.0" × 6.4"`（直柱／折線）／`12.8" × 6.7"`（橫向分位數），主繪圖區占畫布高 `~62%–65%`；多面板依面板數動態縮放 (`300 DPI`)<br>*(Medium 模式限 1～2 張獨立單面板，禁 `ncols=2`)* | `16~20pt` | `12.5~13.5pt`<br>*(副標題 `11.2~12.5pt`)* | **`10.5~12.0pt`** | **`9.0~10.5pt`**<br>*(雙行精簡官方來源圖註 `9.0~9.5pt`：1.官方資料集網址、2.資料涵蓋期間)* | 支援 `editorial_storytelling`（敘事圖解）與 `pure_dataviz`（純資料視覺化／10 大分配圖形）雙軌結構；微文案受 `Slot 6` 控制 |
| **Format E：數據儀表板** | 響應式 Web ／ 單面板靜態匯出依 Format D（`12.0" × 6.4"` / `12.8" × 6.7"`, `~62%–65%`） ／ 全景圖 `24"×14"` (`300 DPI`) | `20~24px` (`pt`) | `14~16px` (`pt`) | **`12~14px`** (`10~12pt`) | **`11~12px`** (`9.0~9.5pt`) | 頂欄 3～4 張 KPI 卡 + 動態多視角畫布 + 明細表（UI 微文案與 Tooltip 受 `Slot 6` 控制） |

- **漢字避頭尾標點保護（Kinsoku Shori）**：所有基於座標繪圖的渲染引擎（`matplotlib`）在強制折行後，必須先剝離續行前導全形/半形縮排（`\u3000 `），檢查次行首字是否為禁則標點（`，、。；：！？）》」】』％`）或前一行末字是否為開括號（`（《「【『`），將違規字元回推或下移後再重新掛回縮排。

---

## 四、 75-20-5 認知色彩分配與「分層式顏色設定集」動態連動法則（75-20-5 Cognitive Color & Layered Color Sets）

- **理論依據**：**數據墨水比（Data-Ink Ratio, Tufte 1983）**、**Brewer 色階分類理論（Sequential vs. Qualitative Palettes, Brewer 1994）**、**面積補償色度定律（CIELUV HCL Area-Chroma Scaling, Zeileis et al. 2009）** 與 **WCAG 2.1 AA 對比度標準（$\ge 4.5:1$）**。
- **75-20-5 畫面色彩預算**：
  - **75% 中性結構底色（Neutral Canvas & Ink）**：畫布底色（`#F8FAFC`）、卡片純白底（`#FFFFFF`）、內文深石板灰（`#0F172A` / `#1E293B`）與次要灰字（`#475569`），絕不使用刺眼純黑（`#000000`）。
  - **20% 語義家族色（Semantic Families）**：同一張圖譜或投影片最多動用 **2～3 種色相（Hue）**。大面積容器填充必須將色度壓低至 $C \le 12, L \ge 95$（極淡柔光底色），外框與標題則採用高飽和同色系（$C \in [48, 65], L \in [40, 50]$）。
  - **5% 焦點強調色（Focal Callout）**：高對比焦點強調色，**全圖僅限用於 1～2 個最關鍵的破局轉折或核心異常值**。
- **分層式顏色設定集架構（Two-Tier Layered Color Configuration in `config/user_preferences.json`）**：
  1. **第一層：`chart_palettes`（數據圖表色票集 — 控制 Format D 量化圖表 ⇄ Format E 數據儀表板）**：
     - 支援於 [`../config/user_preferences.json`](../config/user_preferences.json) 中儲存並切換多組色票設定集（擁有者 `markyang20040112-source` 預設啟用專屬 `gephi_pastel_locked` 色票；外部使用者透過 `hcl_color_engine.build_palette_from_primary_hexes(hex_list)` 從任意 2～4 個主色經由 CIELAB 插值自動推導全套色階）。
     - 每組 `chart_palette` 包含：**無序類別固定 4 色（`qualitative_4`）**、**零透明度 `0.00` 極淺徽章底色（`light_badge_tints_4`）**、**4 組 5 階 CIELAB 循序色階（`sequential_scales`）**、**9 階對稱發散色階（`diverging_9`，中心冷灰 `#F5F6F7`）** 與 **特殊語義中性色（`discrete_neutrals`：長尾/背景基準灰 `#CBD5E1`、缺失值 `#D9D9D9`）**。
     - Python 端透過 [`../scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)（`activate_chart_palette()`、`get_sequential_color()`、`get_diverging_color()`、`bind_qualitative_colors()`）動態取色，並可一鍵同步匯出至前端 [`../scripts/gephi_palette.js`](../scripts/gephi_palette.js)。
     - **嚴禁使用 Alpha 透明度（如 `rgba(...)` 或 `#RRGGBB20`）冒充深淺明度或徽章底色**！
  2. **第二層：`document_themes`（文件與簡報佈景主題 — 控制 Format A 知識圖譜、Format B PDF 報告、Format C PPTX 簡報）**：
     - 控制文件與簡報的主強調色（`primary_accent`）、柔光淺底色（`primary_tint`）、卡片邊框與首尾定錨深色背景（`bookend_dark_bg`），同時強制保留高對比文字（WCAG AA $\ge 4.5:1$）與紅／綠／琥珀語義警示色（`danger_accent`、`success_accent`、`warn_accent`）。
     - Python 端由 `pdf_report_engine.load_document_theme()`、`pptx_slide_engine.load_document_theme()` 與 `generate_mindmap.THEMES` 自動對齊套用。
  3. **雙向同步更新義務**：往後 Format D 與 Format E 在共通配色或圖表設計規則上有任何修改，必須同步更新 [`quantitative_chart_spec.md`](quantitative_chart_spec.md)、[`data_dashboard_spec.md`](data_dashboard_spec.md)、[`../scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py) 與 [`../scripts/gephi_palette.js`](../scripts/gephi_palette.js)。
