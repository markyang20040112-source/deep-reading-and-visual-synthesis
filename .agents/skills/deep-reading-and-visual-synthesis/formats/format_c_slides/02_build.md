# Format C 終端建構規格（16:9 視距自適應簡報設計與規格驅動渲染規範 — 路 B 升級版）

> **單一職責定位（Single Responsibility）**：本檔為 **Format C（16:9 視距自適應簡報 `.pptx` — 路 B 升級版單一自適應架構）** 的唯一終端建構規範。涵蓋 DISCAS 視距反推字級底線與封頂收斂階梯、五步內容優先流程（含 `Step 3` 文案凍結至 `02c_slide_spec_lock.json` 與 `Step 4A` 純文字配置對齊表）、**五大簡報版型家族（13 精煉版型：1 首尾定錨 ＋ 12 內容與衝擊版型）**、模組 1～3（`TOP` 自然流式堆疊、去方塊語彙、圖表 1:1 純粹性）、淨新增 Anti-AI-Slop 底線與黑盒引擎 API 契約。
> - **跨檔分工與零重複邊界**：Step 1 定位、單一議題章節與模式 3 `Tier 1/2/3` / Topic Art Direction DNA 卡見 [`01_plan.md`](./01_plan.md)；Step 5 方案 C 三階內部品管見 [`03_qa.md`](./03_qa.md)；跨格式共通底層定律（表達三支柱、零元語言、事實因果保真、正黑體與 75-20-5 雙層色票）見 [`../../shared/visual_cognition_core.md`](../../shared/visual_cognition_core.md)。若開啟模式 2 加讀 [`../../shared/editorial_narrative_spec.md`](../../shared/editorial_narrative_spec.md)；開啟模式 3 加讀 [`../../shared/creative_armory/INDEX.md`](../../shared/creative_armory/INDEX.md)（按需單開 [`diagram_spatial_metaphors.md`](../../shared/creative_armory/cases/03_spatial_and_thematic/diagram_spatial_metaphors.md) 或 [`thematic_palette_frame.md`](../../shared/creative_armory/cases/03_spatial_and_thematic/thematic_palette_frame.md)）。
> - **筆風語氣自然穿透（解除機械套路綁定）**：簡報文字自然遵循選定筆風檔之人設語氣、標題力度、講稿口條與禁用詞護欄（`Slot 1 / 7 / 8`），**全面廢除對 `Slot 1`「`淺→中→深` 三格機械展開」與 `Slot 4`「每條強制掛 `● 【粗體直覺白話錨點】`」的硬性綁定**。

---

## 一、 路 B 升級版：DISCAS 視距自適應字級與五步內容優先管線

### 1. DISCAS 繁中視距地板對照表與「地板 ≠ 起跳線」原則
依據 **ANSI/AVIXA V202.01（DISCAS）**，`16:9` 畫布（`13.333" × 7.5"` = `540pt` 高，繁中無襯線黑體實字高係數 `0.85× em`）由最遠觀眾視距 $D$（公尺）與畫面高度 $H$（公尺）反推全簡報不可跌破的最小正文字級硬底線：

$$\text{min\_font\_pt} = \max\left(12.0,\ \text{round}\left(3.18 \times \frac{D}{H}\right)\right)$$

| 觀看情境（或自訂 $D/H$） | $D/H$ | 硬底線 `min_font_pt` | 建議全檔目標基準 `target_body_pt` | 結構與寫作自適應連動（融合模式 2 精髓） |
| :--- | :---: | :---: | :---: | :--- |
| **① 筆電近看／留存預讀** | $\le 3.5$ | **`12.0pt`** | `13.0–13.5pt` | 閱讀自足：精煉完整短句，無框細線為主、單層輕卡點綴 |
| **② 小型會議室**（`4–6m`） | `~4.0–5.0` | **`14.0pt`** | `15.0–16.0pt` | 報告閱讀兩棲：微縮句長、輕量化框線，遠近皆清晰 |
| **③ 標準教室投影**（`8–10m`） | `~5.3–6.7` | **`16.0–18.0pt`** | `16.0–18.0pt`（建議 `18.0pt`） | 教室口報：自動禁 4 欄窄排改無框、視情境轉關鍵短語＋講稿＋尾段 `Appendix` |
| **④ 演講廳／Pitch**（`12m+`） | `>= 7.0` | **`20.0pt+`** | `20.0–24.0pt` | 大場衝擊：高比例採 `F1-C` 巨幅焦點宣言頁與 `F5-A` 全幅圖頁，觸發物理短語精簡 |
| **⑤ 自訂物理距離**（輸入 $D, H$） | 依實算 | **`max(12.0, round(3.18 * D / H))`** | 依地板上調訂定 | 依實算 `min_font_pt` 自動歸入對應級距 |

- **地板 ≠ 起跳線（全檔統一基準字級）**：`min_font_pt` 只是防遠距糊字的物理底線，**不是每頁都硬貼底線的起跳線**。進入 Step 4 時必先在地板之上訂定單一全簡報目標設計基準字級 **`target_body_pt >= min_font_pt`**（經統一 Token 工廠 `build_slide_design_tokens()` 貫穿全檔），避免相鄰頁字級忽大忽小。
- **封頂收斂字級階梯（`resolve_typography_scale(target_body_pt)` — 防止高字級大標失衡）**：
  - `13.0pt ➔ 斷言主標 21–22pt`（`~1.60×`）｜`15–16pt ➔ 24–25pt`（`~1.55×`）｜`18pt ➔ 26–27pt`（`~1.48×`）｜`20pt ➔ 27–28pt`（`~1.35–1.40×`），嚴守大標 Bold $\ge 1.35\times$ 正文同時保護斷言主標不超過 `2` 行。
- **高字級雙防線（坑 1 ＆ 坑 2 護欄）**：
  1. **防窄寬破碎（坑 1）**：當 `target_body_pt >= 16.0pt` 時，**禁用 4 欄並排卡片**（`F3-A` 水平流程限 3 步；4～5 里程碑自動切上下交錯時間軸），改採無框分欄（`minimal_column`）並優先調度 `F2-A` 雙欄、`F2-B`、`F2-C`、`F5-A/C`、`F1-C`。
  2. **防頁數失控與寫作顆粒度分流（坑 2）**：容量吃緊時**第一優先永遠採「增加頁數＋去框釋放空間＋自然流式堆疊」**；僅於「現場口說防演說抑制效應（Wecker 2012）」或「`>= 20.0pt` 大場物理門檻」時進一步精煉為關鍵短語錨點（完整推論寫入 `Speaker_Notes` 並視需要於主封底後附 `F4-B` `Appendix` 備查頁）。

### 2. 五步內容優先流程與 `02c_slide_spec_lock.json` 確定性管線

| 階段 | 階段名稱 | 核心動作與產出 | 強制停頓關卡與工程護欄 |
| :---: | :--- | :--- | :--- |
| **Step 1** | **定位與視距地板**（[`01_plan.md`](./01_plan.md)） | 確立北極星 AST、使用情境、DISCAS `min_font_pt` 與單一議題章節清單 | **不提前鎖版型**，亦不用死板總字數限縮議題 |
| **Step 2** | **筆風、模式與配色**（[`../../shared/style_and_color_core.md`](../../shared/style_and_color_core.md) ＋ [`01_plan.md`](./01_plan.md)） | 鎖定筆風檔、模式 1/2/3 與靜態／動態主題色票 | 模式 3 須由使用者拍板 `Tier 1/2/3` 並寫出 **Topic Art Direction DNA** |
| **Step 3** | **文案先行 ➔ 凍結鎖定** | 撰寫每頁標題、副標、Lead/Body 要點、資料來源與 `Speaker_Notes`，**以人眼好讀之 Markdown 逐頁呈現文案草案供使用者審核**（不讓使用者讀原始 JSON），拍板後凍結寫入工作階段根目錄之 **`02c_slide_spec_lock.json`（`copy` 區）** | **⏸️ 文案審核關卡**：使用者拍板後立即生效 **拍板文案保真鐵律**（Step 4 嚴禁未經同意壓縮／刪改文字致失真；極端微調須列前後對照徵求同意） |
| **Step 4A** | **渲染前純文字配置對齊** | 依兩段式語義自動配框架產出配置，調用 `export_step4a_alignment_preview()` 呈現**人眼好讀之純文字逐頁配置＋配圖對齊表**（頁次、家族與版型、定稿標題、文案骨架與 `★聚光燈`、掛載圖檔名與 `*_slide.png`/模式 3 標記、是否省略 Zone 3；**不讓使用者讀原始 JSON**） | **⏸️ 版面與配圖對齊關卡**：確認後鎖入 `02c_slide_spec_lock.json`（`layout` 區） |
| **Step 4B** | **確定性渲染與保真比對** | 呼叫 `render_deck_from_spec()` 嚴格唯讀讀取 `02c_slide_spec_lock.json` 產出 `.pptx`，並自動執行 `validate_layout_sequence()` 與 `check_copy_fidelity()` | 程式碼級鎖死唯讀 `copy` 區，核驗文字與百分比／金額／年份等關鍵數值 100% 原樣保真 |
| **Step 5** | **方案 C 三階內部品管與單頁重繪**（[`03_qa.md`](./03_qa.md)） | 執行 AI 內部三階品管；發現單頁瑕疵時以 `slide_indices=[k]` 局部重繪覆檢，全數通過後 `--cleanup` 清理暫存再交付 | 遇孤兒字或溢出**先調幾何、絕不先縮字**；唯幾何無解須微調文案時始問使用者 |

- **`02c_slide_spec_lock.json` 標準四區 Schema 契約**（存於 `reading_sessions/<專案>/02c_slide_spec_lock.json`）：
  1. `deck_meta`：專案標題、觀看情境、DISCAS `distance_m`/`screen_height_m`/`min_font_pt`、模式 1/2/3（及模式 3 `tier`＋DNA）、筆風檔 ID；
  2. `design_tokens`：全檔統一之 `target_body_pt`、`doc_theme_id` / `theme_overrides` 與 `resolve_typography_scale()` 計算結果；
  3. `slides[i].copy`（**Step 3 凍結唯讀區**）：`chapter_pill`、`headline`、`subtitle`、`items`（Lead/Body 結構化段落）、`zone3_takeaway`（選配）、`speaker_notes`、`key_numbers`（供保真校驗）；
  4. `slides[i].layout`（**Step 4A 鎖定幾何區**）：`family_id`（`F1-A`～`F5-C`）、`variant`（如 `minimal_column` / `staggered_timeline` / `header_only` / `quote_manifesto`）、`spotlight_idx`、`include_zone3`、`visual_asset`（含 `*_slide.png` 或模式 3 `Tier 2/3` 路徑）。

---

## 二、 五大簡報版型家族（13 精煉版型：1 首尾定錨 ＋ 12 內容與衝擊版型）與自動配框架

> **理論依據**：**相容性原則（Kosslyn 2007：版型幾何須與論點內在邏輯同構）** 與 **視覺習慣化防禦（Mackworth 1948：相鄰頁切換拓撲重心）**。引擎保留舊代號 `S0～S14` 與 `Hero Stat` 雙向正規化解析，100% 向下相容。

### 1. 五大簡報版型家族總表（1 首尾定錨 `F1-A` ＋ 12 內容與衝擊版型）

| 簡報版型家族 | 精煉版型代號與名稱（對照舊代號） | 語義觸發條件（何時首選） | 預設視覺語彙與對應黑盒 API |
| :--- | :--- | :--- | :--- |
| **家族 1｜破題與節奏**<br>*(Bookend & Impact)* | • **`F1-A` 封面／封底**（原 `S0` — **1 首尾定錨**）<br>• **`F1-B` 極簡章節過場頁**（原 `S13`，短簡報可省）<br>• **`F1-C` 巨幅焦點宣言頁**（合原 `Hero Stat`＋`S14`） | 開場與峰終收尾；長簡報跨幕換氣；單一極強震撼數字或核心金句主張定錨 | 極高留白純排版（無方塊）：<br>`add_bookend_slide_s0()`<br>`draw_section_divider_slide()`<br>`draw_hero_stat_slide()`（數字／金句雙變體） |
| **家族 2｜觀點並陳與結構展開**<br>*(Structured Narrative)* | • **`F2-A` 並列／對比欄**（合原 `S1`＋`S2`）<br>• **`F2-B` 瑞士網格「左標右展」橫列**（原 `S8`）<br>• **`F2-C` 不對稱便當盒網格 Bento**（原 `S9`） | 二元對決、3 支柱並列、3～4 類條列展開、「1 核心主軸＋2 輔助支柱」非對稱結構 | **無框＋細線為主**（輕卡／Bento 主塊點綴）：<br>`draw_parallel_row_cards()`（`minimal_column` 大序號／無框中線／`clean_card`）<br>`draw_editorial_split_rows_s8()`<br>`draw_bento_grid_slide()` |
| **家族 3｜時序、因果與機制**<br>*(Flow & Mechanism)* | • **`F3-A` 流程軌道／上下交錯時間軸**（合原 `S3`＋`S12`）<br>• **`F3-B` 精簡機制架構圖**（原 `S4`，嚴限 `3～5` 節點） | 3 步先後管線、4～5 階段歷史／路線里程碑、3～5 節點正負回饋閉環或因果協同機制 | 細線軌道與簡潔向量節點：<br>`draw_process_steps_s3()`（3 步水平軌道／4～5 節點自動轉上下交錯時間軸）<br>`draw_clean_mechanism_s4()` |
| **家族 4｜多維比較與分類**<br>*(Comparison & Matrix)* | • **`F4-A` 2×2 正交四象限**（原 `S5`）<br>• **`F4-B` 極簡三線比較表**（原 `S11`，亦適配 `Appendix` 備查） | 兩獨立評估維度（X × Y）交叉分類四種狀態；多方案 × 多維度橫向比較或尾段備查表 | 十字軸線／顧問無外框三線表：<br>`draw_quadrant_matrix_s5()`（預設去框十字軸，可選輕框）<br>`draw_comparison_table_slide()`（原生表格＋單欄淡底聚光） |
| **家族 5｜數據實證與公式解剖**<br>*(Evidence & Anatomy)* | • **`F5-A` 主圖＋四向無框導讀**（原 `S7`／`S7-A/B/C/D`）<br>• **`F5-B` 頂部指標橫帶＋下方洞察**（原 `S10`）<br>• **`F5-C` 焦點公式／指標解剖**（原 `S6`，含原生 OMML） | `300 DPI` 量化統計圖表佐證、3～4 個量化核心指標總覽／跨案例彙整、數學公式或定律拆解 | 圖數主導＋無框導讀：<br>`draw_visual_callout_slide()`（`right`/`left`/`top`/`bottom`/`header_only`）<br>`draw_kpi_strip_slide()`<br>`draw_focal_anatomy_s6()`（搭配 `insert_omml_equation()`） |

### 2. 兩段式語義自動配框架矩陣與全局防撞車護欄
1. **第一段（文案邏輯鎖家族 — `recommend_layout_family()`）**：依 Step 3 定稿文案之內在論點結構鎖定家族——開合／換氣／極強單點衝擊 $\rightarrow$ **`F1`**；對立／並列／清單／主輔展開 $\rightarrow$ **`F2`**；先後步驟／里程碑／3～5 節點機制 $\rightarrow$ **`F3`**；雙軸四類／多維對比表／備查 $\rightarrow$ **`F4`**；圖表／多指標橫帶／公式定律 $\rightarrow$ **`F5`**。
2. **第二段（物理條件與節奏鎖版型）**：
   - `target_body_pt >= 16.0pt` 自動避開過窄多欄，轉用無框雙欄、`F2-B` 橫列、`F2-C` Bento、`F5-A/C` 或 `F1-C`；
   - `4～5` 個時間里程碑自動採 **`F3-A` 上下交錯時間軸**；
   - 跨案例多組指標總覽獨立成 **`F5-B`**，嚴禁塞進統計圖表內。
3. **全簡報防撞車與去方塊節奏硬護欄（`validate_layout_sequence()` 自動檢核）**：
   - **首尾定錨**：第 1 頁封面與主結尾鎖定 **`F1-A`**（尾段 `Appendix` 備查頁可置於主封底後）；
   - **相鄰異構**：連續兩頁嚴禁重複同一版型代號（`Layout[i] != Layout[i+1]`）；
   - **帶方塊卡片頁佔比 `<= 30%～40%`**（超過 `40%` 觸發去框警示）；目標全檔節奏配比為 **無框純排版＋細線 `50%～60%` × 單層輕卡／焦點盒 `25%～30%` × 主圖／巨數衝擊 `15%～20%`**；
   - **單一版型家族佔比 `<= 40%`**；
   - **多樣性底線**：長簡報（`>= 6` 頁）至少涵蓋 **5 種以上不同版型**（`< 6` 頁之短簡報依頁數彈性降階，不誤攔合法短簡報）。

---

## 三、 模組 1～3 版面工程規範 ＋ 淨新增 Anti-AI-Slop 底線

### 1. 模組 1｜微排版、空間再分配與「2＋1 彈性三區結構」
1. **Zone 1 頁頂斷言區緊貼頂部自然計算（`TOP` 對齊）**：
   - 廢除寫死 `head_lines=max(2,...)` ＋ `MIDDLE` 造成單行大標懸浮空置之舊設計；頁頂區改為 **`MSO_ANCHOR.TOP` 緊貼頂部自然計算高度**，構成克制三段（每層至多 2～3 視覺變數）：
     - **頁頂章節膠囊**（`9.5pt`，由 `calc_pill_width()` 精準貼合字寬，右側選配講者／頁碼膠囊）；
     - **完整因果斷言主標**（建議 1～2 行，字級由 `resolve_typography_scale(target_body_pt)` 推算，Bold 深墨 `#0F172A`）；
     - **選配無框頁副標**（`#64748B`，補充資料口徑或 `F5-A` `header_only` 全幅純圖頁脈絡）。
2. **Zone 2 兩層組塊、`TOP` 自然流式堆疊、容器三層表頭與 Content-Driven Height**：
   - **簡報專屬兩層組塊上限**：單頁只承載 1 個獨立子議題，Zone 2 頂層容器限 **`2～4` 個** × 每容器 **`2～3` 點**（全頁總要點 `<= 6～8` 點）。
   - **垂直對齊規則化、容器內部 `TOP` 靠上 ＋ 整體 Zone 2 兩段式垂直均衡**：多欄、四象限與圖旁導讀之**單一容器／欄位內部**全面維持 **`MSO_ANCHOR.TOP` ＋ 固定間距由上往下自然流式堆疊**（廢除 `slot_h` 硬均分並杜絕幽靈空分隔線與導讀總標斷層；`MIDDLE` 僅保留給高度 `<= 0.55"` 之單行窄帶／膠囊／橫幅、封面主標、公式盒與巨幅數字），亦不改動全檔統一之 `target_body_pt`；同時於中段版型（`F2`～`F5`）底層執行**整體 Zone 2 兩段式均衡**（不加每頁標配頁底細字，維持極簡白底）：① **先自然舒展**——當 Zone 2 實高較可用高度多出 `> 1.2"` 時，將組塊間距、表列上下 padding 或要點間距適度舒展 `1.25×～1.45×`（不壓迫 Zone 3 或底緣）；② **再整體群組光學置中（`~40% / 60%`）**——舒展後若仍矮於可用高度超過 `0.50"`，將該頁整組 Zone 2 物件一體下移至光學重心（上方分攤 `~40%` 剩餘空白、下方留 `~60%`，**上方新增緩衝上限 `<= 0.90"`**，嚴守不碰撞 Zone 3 與底緣 `7.22"`）。
   - **Content-Driven Height 與 Tullis 雙層留白**：容器高度由實際文字高度驅動（把無用內部死白推出方塊外），維持外框邊界留白 `26%～32%`（高視距簡報可擴至 `35%～45%+`）與框內文字佔高 `<= 65%～70%`（行距 `1.28~1.35×`）；`F3-B`（`S4`）採緊湊比例節點並徹底移除細長摩天樓節點框與大灰底墊板；`F5-C`（`S6`）善用寬螢幕採 `left_right`（左 `38%` 焦點盒 ＋ 右 `62%` 無框拆解列）或 `top_bottom`（上方極薄焦點帶 ＋ 下方無框三欄，省略 Zone 3）。
   - **克制文字層級與聚光燈減噪**：
     - **容器／欄位表頭拆為三層**：**Kicker 眉標 $\rightarrow$ 主標（`target_body_pt + 3pt` Bold 深墨 `#0F172A`）$\rightarrow$ 副標（`#64748B`）**；
     - **要點拆為獨立兩段**：**Lead 小標（`+1.0～1.5pt Bold` 深墨 `#0F172A`）$\rightarrow$ Body 說明（`#334155` Regular）**；
     - **圖旁導讀區拉開明確階梯**：**導讀總標 `1.30×` / 小標 `1.15×` / 內文 `1.0×`**，且左側豎細線高度緊貼實際文字高度；
     - **聚光燈主角減噪**（全頁至多 `1` 個）：消除多重重複框線，改以 **極淡底色面＋單條左／頂色帶＋深墨標題** 呈現，次要對照退居 `#CBD5E1` / `#64748B`。
   - **Pillow 真實字寬量測、繁中 Kinsoku 斷行與反轉版幾何修框**：
     - 全面以 **`measure_text_layout()`**（讀取 Windows `msjh.ttc` / `msjhbd.ttc` `index=0` 實寬 ＋ 支援行內 `**粗體**` 權重 ＋ 配合 `<a:ea>`/`eaLnBrk="1"`/`hangingPunct="1"` 之自寫繁中禁行首標點與禁行尾開括號斷行器，**嚴禁英文空白 `split()` 與連字號 `-` 斷中文**）計算真實行數與偵測 **單字孤兒換行（尾行 `<= 2` 漢字＋標點）**；
     - 觸發溢出或孤兒換行時呼叫 **`autofit_box_geometry_first()`（反轉版先調幾何、絕不先縮字）**：優先微幅調整框高、欄寬比例或拆頁，**嚴禁未經授權把字級壓低於 `target_body_pt` 或跌破 `min_font_pt`**。
3. **Zone 3（按需選配 Optional）與 `Speaker_Notes` 雙通道**：
   - Zone 3 預設按需省略（`F5-A` 主圖、`F5-C` 公式或 Zone 1 已講明結論時不畫）；必要時可選 `"dark_banner"` 或輕量 `"subtle_line"`。
   - 每頁必備完整口語化 `Speaker_Notes`（自然銜接 AST 轉場，不將 AST 標語印入畫面），且支援行內 `**粗體詞組**` 自動解析並禁止以 `\n` 硬塞多條要點於單一段落。

### 2. 模組 2｜去方塊設計語彙擴充（單層去套盒 ＋ 6 大去方塊詞彙）
- **純文字卡片去雙層套盒**：凡使用卡片一律採單層乾淨白底卡（頂部極薄色帶＋無框標題＋細分隔線），徹底消滅框中框圓角表頭與逐列小方框。
- **6 大無方塊／輕量化詞彙**：① 升級 `minimal_column`（巨型淡序號 `01/02/03`＋短色條＋靠上堆疊＋極細垂直線）；② 去框十字軸 `F4-A`（3 象限無框排字、僅聚光燈象限極淡底色）；③ 水平細線節點軌道／交錯軸 `F3-A`；④ 瑞士網格左標右展 `F2-B`（左 `28%` 序號分類＋右 `72%` 展開＋極細橫線）；⑤ 無框中線對決 `F2-A`；⑥ 高留白巨幅宣言 `F1-C`（搭配 `F2-C` Bento 與 `F4-B` 極簡三線表）。

### 3. 模組 3｜圖表純粹性、1:1 實體吋數與跨 Format D ➔ C `*_slide.png`
- **主視覺圖四向無框導讀鐵律**：凡含主視覺圖（`F5-A` 量化統計圖或 `F3-B` 3～5 節點精簡機制圖），**嚴禁在圖旁或上下疊加帶框卡片**，亦嚴禁縮小貼入高密度 Format A 知識圖譜；一律依數據列數與圖幅比例選用 `right` / `left` / `top` / `bottom` / `header_only` 四向無框導讀（如 2 列扁平數據優先採寬扁 `bottom` 或 `F1-C` 巨幅數字頁），且圖說錨定於 Zone 2 下緣與右側底緣切齊。
- **圖表純粹性與 1:1 實體吋數**：嚴禁在統計圖內塞入跨案例文字事實小卡（獨立成 `F5-B` 或 `F1-C`）、重複繪製 Zone 1 斷言大標或雙重底註；繪圖須依目標貼圖框實體吋數 **1:1 設 `figsize`**。若掛載既有 Format D 原圖時符合「縮放比 `< 0.80×`、`min_font_pt >= 14.0pt`、或原圖含重標／事實小卡」，必須由同腳本另存無重標專用 **`*_slide.png`** 而不覆寫原圖（詳見 [`../format_d_charts/02_build_core.md`](../format_d_charts/02_build_core.md)）。

### 4. 淨新增 Anti-AI-Slop 三底線（與 `visual_cognition_core.md` 零重複）
1. **嚴禁多行正文置中對齊**：所有 2 行以上之說明段落與清單要點一律靠左對齊（僅封面主標、單行膠囊、巨幅數字與公式盒允許置中）。
2. **嚴禁純裝飾性無意義圓圈圖標徽章與發光陰影框**：關閉所有 PowerPoint 預設模糊陰影，不為了湊版面插入無結構語義之圓形裝飾小圖示或霓虹發光外框。
3. **嚴禁跨區重複文案與殘留草稿字元**：同一句結論不可同時出現在 Zone 1 大標、圖表內標題與 Zone 3 橫幅；完稿畫面絕不可殘留未替換之 `TBD` / `TODO` 或未轉譯之 Markdown 星號 `**`。

- *(註：簡報主色系與視覺引導預設屬設計與排版層，不與 `02_color_registry.json` 綁定；僅當簡報元素明確代表與統計圖表共用之特定資料實體（如「台北」KPI 摘要卡或圖例色標），且該版型支援強調色覆寫時，始透過 `get_active_registry().hex_for(name)` 精準對齊。)*
- *(註：若開啟 **模式 3 `bespoke_metaphor`**，請依 [`01_plan.md`](./01_plan.md) 拍板之 `Tier 1 / 2 / 3` 與 Topic Art Direction DNA 卡，按需參閱 [`../../shared/creative_armory/INDEX.md`](../../shared/creative_armory/INDEX.md) 執行主題幾何原語、無字概念主視覺或 1～2 頁 HTML+SVG `300 DPI` 透明底層，嚴守 `1` 核心母題與 `20/80` 克制比。)*

---

## 四、 黑盒引擎 API 契約（Black-Box Engine API Contract）

> [!IMPORTANT]
> **【底層引擎黑盒呼叫鐵律（Black-Box API Rule）】**：[`../../scripts/hcl_color_engine.py`](../../scripts/hcl_color_engine.py)、[`../../scripts/pptx_slide_engine.py`](../../scripts/pptx_slide_engine.py) 與 [`../../scripts/verify_visual_outputs.py`](../../scripts/verify_visual_outputs.py)（後兩者底層實作已模組化收斂於 `scripts/pptx_engine/`，原檔案保留為 100% 相容統一入口與 CLI 門面）封裝全套 DISCAS Token 工廠、Pillow 真實字寬量測、五大版型家族 13 精煉版型、確定性渲染層與方案 C 驗證網格。撰寫腳本時**直接依下方簽名 `import` 呼叫，日常執行嚴禁對 `scripts/*.py` 呼叫 `read_file`（除非報錯除錯）**！

```python
# === scripts/hcl_color_engine.py (Format C Mode 3 Dynamic Theme Bridge) ===
from hcl_color_engine import (
    derive_slide_theme_from_topic,  # (topic_or_hex, mode="light_classroom"|"dark_stage", **kwargs) -> Dict[str, str] (CIELAB + WCAG AA >= 4.5:1)
)

# === scripts/pptx_slide_engine.py Black-Box API Contract (Backward-Compatible) ===
from pptx_slide_engine import (
    # --- Core Canvas, DISCAS Tokens, Real Text Measurement, Autofit, SVG 300DPI & OMML ---
    create_widescreen_presentation, # () -> Presentation (13.333" x 7.5")
    load_document_theme,            # (doc_theme_id=None) -> Dict[str, str]
    hex_to_rgb_color,               # (hex_str) -> RGBColor
    set_slide_background,           # (slide, bg_hex=None, doc_theme_id=None) -> None
    calc_pill_width,                # (text, font_pt=9.5, pad_in=0.24) -> float (inches)
    calc_min_font_pt_from_distance, # (distance_m, screen_height_m) -> float (>= 12.0pt DISCAS floor)
    resolve_typography_scale,       # (target_body_pt) -> Dict[str, float] (capped converging scale: headline/card_title/lead/body/caption)
    build_slide_design_tokens,      # (min_font_pt=12.0, target_body_pt=None, doc_theme_id=None, theme_overrides=None) -> Dict
    measure_text_layout,            # (text, box_width_in, font_pt, bold=False, line_spacing=1.30, ...) -> Dict (Pillow msjh.ttc index=0 + CJK Kinsoku lines, orphan_flag, safe_height_in)
    autofit_box_geometry_first,     # (text_spec, candidate_boxes, target_body_pt, ...) -> Dict (grow height / rebalance widths / flag split; NEVER shrink below target_body_pt)
    render_svg_to_png_300dpi,       # (html_or_svg_path, out_png_path, width_px, height_px) -> str (Playwright+Chromium primary, Chrome/Edge CLI fallback, RGBA 300 DPI)
    insert_omml_equation,           # (text_frame, equation_str, font_pt=None, ...) -> None (native editable <m:oMath> XML + plain fallback)
    add_zone1_header,               # (slide, chapter_pill_text, assertion_headline, pill_bg_hex=None, pill_fg_hex="#FFFFFF", headline_hex=None, headline_pt=20.5, subtitle_text=None, subtitle_pt=13.0, subtitle_hex=None, right_badge_text=None, show_divider=True, tokens=None, doc_theme_id=None) -> float (TOP aligned, returns zone2_top_in)
    add_zone3_footer,               # [Optional] (slide, takeaway_text, bg_hex=None, border_hex=None, fg_hex="#F8FAFC", font_pt=13.0, style="dark_banner"|"subtle_line", tokens=None, doc_theme_id=None) -> None
    add_speaker_notes,              # (slide, notes_text) -> None
    # --- 5 Layout Families / 13 Refined Layouts (1 Bookend + 12 Content & Impact; all accept optional tokens=None) ---
    add_bookend_slide_s0,           # [F1-A / S0]  (prs, badge_text="EXECUTIVE BRIEFING", main_title="", subtitle_text="", kpi_cards=None, speaker_notes=None, bg_hex=None, accent_hex=None, title_pt=28.0, subtitle_pt=14.5, footer_text=None, tokens=None, doc_theme_id=None, **kwargs) -> Slide  [Note: first arg is prs, NOT slide]
    draw_section_divider_slide,     # [F1-B / S13] (slide, section_num, section_title, subtitle_text="", tokens=None, doc_theme_id=None) -> None
    draw_hero_stat_slide,           # [F1-C / Hero Stat + S14] (slide, stat_value, stat_label, context_points=(), right_image_path=None, variant="big_number"|"quote_manifesto", left=0.5, top=1.36, total_width=12.333, height=None, stat_pt=54.0, body_font_pt=13.5, tokens=None, doc_theme_id=None) -> Tuple
    draw_parallel_row_cards,        # [F2-A / S1 + S2] (slide, cards_spec, left=0.5, top=1.36, total_width=12.333, height=None, gap=0.26, spotlight_idx=None, body_font_pt=None, title_font_pt=None, width_ratios=None, card_style="clean_card"|"minimal_column"|"borderless_centerline", tokens=None, doc_theme_id=None) -> List[Tuple]
    draw_editorial_split_rows_s8,   # [F2-B / S8]  (slide, rows_spec, left_ratio=0.28, spotlight_idx=None, left=0.5, top=1.36, total_width=12.333, height=None, body_font_pt=None, tokens=None, doc_theme_id=None) -> List[Tuple]
    draw_bento_grid_slide,          # [F2-C / S9]  (slide, primary_block, secondary_blocks, spotlight_idx=0, left=0.5, top=1.36, total_width=12.333, height=None, body_font_pt=None, tokens=None, doc_theme_id=None) -> List[Tuple]
    draw_process_steps_s3,          # [F3-A / S3 + S12] (slide, steps_spec, layout_style="auto"|"fine_track"|"staggered_timeline"|"card_arrow", left=0.5, top=1.36, total_width=12.333, height=None, spotlight_idx=None, body_font_pt=None, tokens=None, doc_theme_id=None) -> List[Tuple]
    draw_clean_mechanism_s4,        # [F3-B / S4]  (slide, nodes_spec, edges_spec=None, topology="horizontal_chain"|"cycle_loop"|"hub_spoke"|"custom", callouts=None, callout_position="right", callout_heading=None, visual_ratio=0.64, left=0.5, top=1.36, total_width=12.333, height=None, body_font_pt=13.0, tokens=None, doc_theme_id=None) -> Tuple
    draw_quadrant_matrix_s5,        # [F4-A / S5]  (slide, quadrants_spec, x_axis_label="", y_axis_label="", spotlight_idx=1, borderless=True, left=0.5, top=1.36, total_width=12.333, height=None, body_font_pt=12.5, tokens=None, doc_theme_id=None) -> List[Tuple]
    draw_comparison_table_slide,    # [F4-B / S11] (slide, headers, rows, spotlight_col=None, col_widths=None, left=0.5, top=1.36, total_width=12.333, height=None, body_font_pt=None, tokens=None, doc_theme_id=None) -> Tuple
    draw_visual_callout_slide,      # [F5-A / S7]  (slide, image_path=None, callout_position="right"|"left"|"top"|"bottom"|"header_only", callouts=None, visual_ratio=0.65, visual_caption=None, callout_heading=None, body_font_pt=13.0, left=0.5, top=1.36, total_width=12.333, height=None, spotlight_idx=0, tokens=None, doc_theme_id=None) -> Tuple
    draw_kpi_strip_slide,           # [F5-B / S10] (slide, kpi_items, insight_blocks=(), spotlight_idx=0, left=0.5, top=1.36, total_width=12.333, height=None, body_font_pt=None, tokens=None, doc_theme_id=None) -> List[Tuple]
    draw_focal_anatomy_s6,          # [F5-C / S6]  (slide, focal_title, focal_formula, focal_note="", breakdown_items=(), mode="left_right"|"top_bottom", focal_ratio=0.38, use_omml=False, left=0.5, top=1.36, total_width=12.333, height=None, body_font_pt=13.0, tokens=None, doc_theme_id=None) -> Tuple
    draw_theme_geometric_accent,    # [Mode 3 Tier 1] (slide, motif_type="diagonal_wedge"|"ruler_ticks"|"step_blocks"|"vector_scale", tokens=None, doc_theme_id=None, **kwargs) -> None
    # --- Two-Stage Semantic Routing, Anti-Collision & Spec-Driven Deterministic Pipeline ---
    recommend_layout_family,        # (slide_copy_spec, target_body_pt=13.0, ...) -> Dict (family_id, variant, rationale)
    validate_layout_sequence,       # (layouts, require_bookends=True, min_distinct=5, max_boxed_ratio=0.40, max_family_ratio=0.40) -> bool (normalizes F1-A..F5-C & S0..S14; scales min_distinct for <6 slides)
    export_step4a_alignment_preview,# (spec_json_or_path) -> str (Human-readable Step 4A Markdown alignment table)
    render_deck_from_spec,          # (spec_json_or_path, output_pptx_path, ...) -> str (Read-only deterministic render from 02c_slide_spec_lock.json)
    check_copy_fidelity,            # (spec_json_or_path, pptx_path) -> Dict (Verifies 100% text & key numeric fidelity, zero TBD/**)
)
```

*(Step 4B 確定性渲染完成後，立即依 **[`03_qa.md`](./03_qa.md)** 執行方案 C 三階內部品管與暫存檔清理。)*
