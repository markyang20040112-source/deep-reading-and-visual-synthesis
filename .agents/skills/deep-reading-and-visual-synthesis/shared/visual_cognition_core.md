# 視覺認知與設計規範（Visual Cognition & Design Core）

> **單一職責定位（Single Responsibility）**：本檔為 Phase 2 **五大產出格式（Format A 知識圖譜、Format B 決策報告／專欄、Format C 簡報、Format D 量化圖表、Format E 數據儀表板）唯一共用的跨格式底層認知與表達原則**。
> - **徹底解耦原則**：本檔僅規範五大格式真正共通的無損擴展哲學、表達三支柱架構、對外行文與事實保真底線、正黑體與漢字避頭尾標點保護、以及 75-20-5 雙層色票架構。凡因畫布面積與閱讀距離不同而不互通之**組塊階層公式、留白計算方式、物理字級下限與行寬幾何參數**，全數歸還各格式分枝規格檔（`formats/format_*/02_build*.md`）獨立定義，嚴禁跨格式硬套。

---

## 一、 工作記憶容量保護與多畫布無損擴展法則（Working Memory Protection & Zero-Loss Expansion）

- **理論依據**：**工作記憶容量極限（Working Memory Capacity $4 \pm 1$, Cowan 2001）**、**組塊理論（Chunking, Miller 1956）** 與 **格式塔共同區域原則（Law of Common Region, Palmer 1992）**。
- **跨格式共通標準**：
  1. **單一畫面焦點組塊受載體物理面積約束（各格式組塊上限見對應 `formats/format_*/02_build*.md`）**：人類單次視覺掃描能同時處理的頂層獨立組塊有限，嚴禁在單一畫布堆砌過多同級容器引發注意力分散。惟全景知識圖譜、A4 深度報告、`16:9` 簡報投影片與單面板圖表之物理面積與觀看距離差異極大，其具體組塊層數、容器上限與留白呼吸規範一律依各格式 `02_build*.md` 執行。
  2. **無損分流擴展鐵律 vs. Medium 單一故事線收斂特例**：
     - **一般文獻／深度報告／簡報模式（以「拆圖、擴章、加頁」取代刪減內容）**：Phase 1 Step 5 收斂出的「核心論證主幹分支」與「批判延伸／跨域遷移分支」不論總數多少（如 $5 \sim 8+$ 個分支），**嚴禁為了塞進單一畫面而刪減任何細節、縮字硬塞或壓縮批判性議題**！當單一畫面容量不足時，Phase 2 強制啟動多畫布／多章節／多頁擴展（Format A 自動拆分為 `01` 主幹圖、`02` 機制深挖圖、`03+` 批判延伸與跨域遷移專題圖；Format B 動態擴增章節 `壹～柒...`；Format C 按單頁單一議題動態加頁；Format D/E 增加獨立面板或互動視角）。
     - **Medium 每週一圖／輕量數據敘事專欄模式（Single-Hook Convergence）**：針對公開數據新聞與課堂「每週一圖」作業，聚焦**單一核心數據故事主軸**，僅產出 **1～2 張各自獨立之單面板（Single-Panel）`300 DPI` `.png` 統計圖（禁止 `ncols=2` 橫向並排子圖）** ＋ **正文 `<= 1,600` 字之 Medium 原生 Markdown 專欄（免除編譯 A4 PDF）**。
  3. **並列維度結構對稱與視覺對齊（Structural Parallelism）**：當同一畫面並列比較多個維度、階段或方案時，各區塊內部資訊應維持一致的屬性顆粒度與對齊基準，支援視線低阻力比對（各格式之具體對齊結構與是否使用開頭錨點，依各格式 `02_build*.md` 規範；其中 Format C 簡報免除機械式括號錨點與固定三階套路）。

---

## 二、 表達三支柱統御原則：設計光譜武器庫 × 筆風插槽 × 分層配色（Three Pillars of Expression）

- **設計哲學與徹底解耦原則（Full Decoupling of Visual Geometry vs. Writing Style vs. Design Spectrum）**：
  - 底層視覺規範僅定義「空間幾何、字級對比與色彩結構」，**絕對不寫死任何單一行文語氣或單一裝飾風格**。
  - 在 Phase 2 主幹定裝（[`style_and_color_core.md`](./style_and_color_core.md)）與各分枝 `01_plan.md` 局部覆寫中，透過「表達三支柱」統御所有選定之產出格式（Format A / B / C / D / E）：
    1. **支柱 1：設計光譜與轉譯武器庫開／關**：依任務特性於 `standard_rigorous`（模式 1：標準嚴謹）、`editorial_narrative`（模式 2：資料八／經濟學人編輯室敘事，見 [`editorial_narrative_spec.md`](./editorial_narrative_spec.md)）與 `bespoke_metaphor`（模式 3：開放式創意材質與幾何空間隱喻武器庫，見 [`creative_armory/INDEX.md`](./creative_armory/INDEX.md)）間切換，可全域統一或分枝局部覆寫。
    2. **支柱 2：筆風設定檔（`Slot 1～8` 語氣與護欄全域穿透）**：控制所有生成內容的人設語氣、敘事節奏、標題句型、圖譜謂詞、統計圖表微文案、簡報講稿與禁用詞護欄。
    3. **支柱 3：分層顏色設定集（`chart_palettes` ＋ `document_themes` ＋ `derive_thematic_palette`）**：統籌數值色彩科學與文件視覺佈景主題。
- **作者私人筆風庫 vs. 外部使用者隔離（Owner-Only Style Isolation）**：
  - 當本機 Git 身分驗證為擁有者 `markyang20040112-source` 時，直接讀取 `config/owner_styles/` 下之專屬筆風庫（`plain_first_progressive.md`、`rigorous_empirical_stat.md`、`editorial_data_journalism.md`、`personalized_essay_style.md`）。
  - 當外部新使用者執行時，系統嚴格隱藏並隔離 `config/owner_styles/`，僅依空白結構模板 [`../config/styles/_style_schema_template.md`](../config/styles/_style_schema_template.md) 讀取或生成存放於 `config/user_styles/` 的使用者自訂筆風檔。
- **跨格式寫作共通鐵律（適用所有筆風檔與 Format A～E 對外交付物）**：
  - **零工作流元語言洩漏（Zero Meta-Workflow Leakage）**：讀者並不知道作者背後如何與 AI 進行閱讀理解與多輪對話；所有對外輸出之正文、標題、圖說與圖譜副標**嚴禁出現任何閱讀系統內部流程詞彙**（如 `第一階段`、`Phase 1/2`、`蘇格拉底思辨／詰問／收斂`、`直覺探針`、`Step 1～5`、`零刪減分流`、`系統基模 A/B` 等未面向讀者定義的內部代號）。
  - **高張力修辭同篇去重複（Anti-Repetition Guardrail）**：任何鮮明比喻、口語形容詞或標誌性轉折片語，在同一篇成品中至多出現 `1` 次，避免複製貼上造成閱讀疲勞。
  - **事實與因果保真底線（Factual & Causal Fidelity — 不干擾行文、不硬塞背景）**：本原則**不要求**在純論述、跨域延伸或已有圖表說明的頁面額外補充數據背景或專有名詞（一切篇幅與表達仍 100% 依循筆風檔節奏與去冗餘原則）。唯獨**當內容確實引用原文數據或因果關係時**，須遵守兩條負面底線：① **不憑空捏造原文未載之統計數字、百分比或具體數據案例**；② **不擅自升級因果強度**（原文若為相關、伴隨或局部現象，不改寫為絕對決定或全體必然）。
- **8 大全生成場景控制插槽（Slots 1～8）跨格式映射表**：
  1. **`Slot 1: Core_Persona_And_Progression`**：控制全格式共通之寫作者人設與語氣冷熱度；其三階資訊展開順序適用於長文論述與深度圖譜（註：Format C 簡報卡片不硬綁三格機械展開，改依頁面論點自然分段）。
  2. **`Slot 2: Interactive_Guidance_Tone`**：控制 Phase 1 蘇格拉底提問口吻與 Phase 2「一次一張圖逐步導學互動模式」之五步解說骨架。
  3. **`Slot 3: Prose_And_Narrative_Rhythm`**：控制 Format B（深度報告與 Medium 專欄）之散文段落長度、破題句式、標點與粗體強調密度。
  4. **`Slot 4: Structured_Blocks_And_Captions`**：控制 Format B 報告表格／卡片條目開頭錨點格式（`Anchor_Format`）、公式導讀與 `<figure>` 圖說規範（註：Format C 簡報解除機械錨點綁定，不強制每條掛 `● 【...】` 括號前綴，僅自然符合筆風語氣）。
  5. **`Slot 5: Knowledge_Diagram_Copy`**：控制 Format A（知識圖譜 `.png`）之宏觀分區大標、子卡片標題、有向箭頭「謂詞膠囊（`Predicate_Verbs`）」動詞風格與底部 Takeaway 橫幅語氣。
  6. **`Slot 6: Chart_And_Dashboard_MicroCopy`**：控制 Format D（量化統計圖表 `.png`）與 Format E（數據儀表板 Web）之主副標題公式、X/Y 座標軸籤、圖內標註氣泡（`Callouts`）、基準線說明、KPI 卡與網頁 Tooltip 解說微文案。
  7. **`Slot 7: Slide_Headline_And_Speaker_Notes`**：控制 Format C（簡報 `.pptx`）之 Zone 1 斷言標題、選配 Zone 3 行動橫幅、畫面精煉自然語氣與 `Speaker_Notes` 口語化講稿。
  8. **`Slot 8: Notation_Terminology_And_Guardrails`**：控制全格式之數值與單位換算、專有名詞中英呈現格式、偏好詞白名單（`Whitelist`）、絕對禁用詞黑名單（`Banned_Cliches`）與 Few-Shot 正反校準。
- **三態參數解析與即時熱修改（Tri-State Resolution & Hot-Reload）**：
  - 筆風檔內標記為 **`[USER_LOCKED]`** 者強制 100% 遵守；標記為 **`[SCENARIO_PRESET]`** 者依情境套用；標記為 **`[AI_ADAPTIVE]`** 者由 AI 依 `Slot 1` 主基調與當下資料特性自動推導最協調寫法。若使用者於對話中臨時要求調整語氣或用詞，立即局部熱修改並於該次生成生效。

---

## 三、 跨格式字型家族、字重階層與漢字避頭尾規範（Font Stack, Hierarchy & CJK Kinsoku Shori）

- **理論依據**：**字級與閱讀跳視效率研究（Dyson 2004; Tinker 1963）** 與 **前注意特徵處理（Preattentive Processing, Ware 2020）**。
- **字體優先序**：統一使用無襯線正黑體（`Microsoft JhengHei`、`PingFang TC`、`Noto Sans CJK TC`；Format B 另支援大專院校傳統中文標楷體 `DFKai-SB` 模式，可由筆風檔 `linked_defaults.pdf_theme` 或 Format B `01_plan.md` 指定），並建立明確的 **3 階字重與尺度對比**（主標題 Bold $\ge 1.35\times$ 正文 Regular）。*(各格式專屬之畫布尺寸、物理字級下限與行寬標準，均以各自 `formats/format_*/02_build*.md` 為唯一權威依據。)*
- **漢字避頭尾標點保護（Kinsoku Shori）**：所有基於座標繪圖的渲染引擎（`matplotlib`）在強制折行後，必須先剝離續行前導全形/半形縮排（`\u3000 `），檢查次行首字是否為禁則標點（`，、。；：！？）》」】』％`）或前一行末字是否為開括號（`（《「【『`），將違規字元回推或下移後再重新掛回縮排；且在靜態圖與簡報中避免使用彩色 Emoji 以防微軟正黑體產生缺字方框（`□`）。

---

## 四、 75-20-5 認知色彩分配與「分層式顏色設定集」動態連動法則（75-20-5 Cognitive Color & Layered Color Sets）

- **理論依據**：**數據墨水比（Data-Ink Ratio, Tufte 1983）**、**Brewer 色階分類理論（Sequential vs. Qualitative Palettes, Brewer 1994）**、**面積補償色度定律（CIELUV HCL Area-Chroma Scaling, Zeileis et al. 2009）** 與 **WCAG 2.1 AA 對比度標準（$\ge 4.5:1$）**。
- **75-20-5 畫面色彩預算**：
  - **75% 中性結構底色（Neutral Canvas & Ink）**：畫布底色（`#F8FAFC`）、卡片純白底（`#FFFFFF`）、內文深石板灰（`#0F172A` / `#1E293B`）與次要灰字（`#475569`），絕不使用刺眼純黑（`#000000`）。
  - **20% 語義家族色（Semantic Families）**：同一張圖譜或投影片最多動用 **2～3 種色相（Hue）**。大面積容器填充必須將色度壓低至 $C \le 12, L \ge 95$（極淡柔光底色），外框與標題則採用高飽和同色系（$C \in [48, 65], L \in [40, 50]$）。
  - **5% 焦點強調色（Focal Callout）**：高對比焦點強調色，**全圖僅限用於 1～2 個最關鍵的破局轉折或核心異常值**。
- **分層式顏色設定集架構（Two-Tier Layered Color Configuration in `config/user_preferences.json`）**：
  1. **第一層：`chart_palettes`（數據圖表色票集 — 控制 Format D 量化圖表 ⇄ Format E 數據儀表板）**：
     - 支援於本機 `config/user_preferences.json`（範本見 [`../config/user_preferences.template.json`](../config/user_preferences.template.json)）中儲存並切換多組色票設定集（擁有者 `markyang20040112-source` 預設啟用專屬 `gephi_pastel_locked` 色票；外部使用者透過 `hcl_color_engine.build_palette_from_primary_hexes(hex_list)` 從任意 2～4 個主色經由 CIELAB 插值自動推導全套色階）。
     - 每組 `chart_palette` 包含：**無序類別固定 4 色（`qualitative_4`）**、**零透明度 `0.00` 極淺徽章底色（`light_badge_tints_4`）**、**4 組 5 階 CIELAB 循序色階（`sequential_scales`）**、**9 階對稱發散色階（`diverging_9`，中心冷灰 `#F5F6F7`）** 與 **特殊語義中性色（`discrete_neutrals`：長尾/背景基準灰 `#CBD5E1`、缺失值 `#D9D9D9`）**。
     - Python 端透過 [`../scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)（`activate_chart_palette()`、`get_sequential_color()`、`get_diverging_color()`、`bind_qualitative_colors()`、`use_session_registry()` 寫入 `02_color_registry.json` 跨圖鎖定同實體色彩）動態取色，並可一鍵同步匯出至前端 [`../scripts/gephi_palette.js`](../scripts/gephi_palette.js)。
     - **嚴禁使用 Alpha 透明度（如 `rgba(...)` 或 `#RRGGBB20`）冒充深淺明度或徽章底色**！
  2. **第二層：`document_themes`（文件與簡報佈景主題 — 控制 Format A 知識圖譜、Format B PDF 報告、Format C PPTX 簡報）**：
     - 控制文件與簡報的主強調色（`primary_accent`）、柔光淺底色（`primary_tint`）、卡片邊框與首尾定錨深色背景（`bookend_dark_bg`），同時強制保留高對比文字（WCAG AA $\ge 4.5:1$）與紅／綠／琥珀語義警示色（`danger_accent`、`success_accent`、`warn_accent`）。
     - Python 端由 `pdf_report_engine.load_document_theme()`、`pptx_slide_engine.load_document_theme()` 與 `generate_mindmap.THEMES` 自動對齊套用。
  3. **雙向同步更新義務**：往後 Format D 與 Format E 在共通配色或圖表設計規則上有任何修改，必須同步更新 [`../formats/format_d_charts/02_build_core.md`](../formats/format_d_charts/02_build_core.md)、[`../formats/format_e_dashboard/02_build.md`](../formats/format_e_dashboard/02_build.md)、[`../scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py) 與 [`../scripts/gephi_palette.js`](../scripts/gephi_palette.js)。
