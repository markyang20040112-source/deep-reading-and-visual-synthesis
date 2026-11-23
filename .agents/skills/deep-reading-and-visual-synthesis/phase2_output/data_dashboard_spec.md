# 數據儀表板設計與互動／靜態雙模態實作規範（Format E: Data Dashboard Spec）

> **單一職責定位（Single Responsibility）**：本檔專責 **Format E（數據儀表板：互動式 Web 數據儀表板 `.html`/`.css`/`.js` ＋ 出版級靜態全景儀表板圖 `.png`）** 的**動態呈現架構選型（工作台 / Bento 網格 / 雙模態交付，嚴禁寫死圖表類型與呈現格式）**、**前端 CSS `:root` 變數與 `scripts/gephi_palette.js` 色彩工程實作**、第三層設計武器庫前端延伸，以及**零後端自包含前端工程、獨立 Git 儲存庫綁定與網站發布驗收守則**。
> - **圖表選型、色彩 SSOT 與家族規格連動**：本檔已去除與 Format D 重複之選型長表與靜態圖細則！內部圖表動態選型請見 **[`advisors/layer2_advisor_de_chart.md`](advisors/layer2_advisor_de_chart.md)**；配色設定集與編碼誠實三鐵律請見 **[`quantitative_chart_spec.md`](quantitative_chart_spec.md)**；各家族繪圖細則依需求按需開啟 **[`chart_family1_ranking_and_deviation.md`](chart_family1_ranking_and_deviation.md)**、**[`chart_family2_trend_and_comparison.md`](chart_family2_trend_and_comparison.md)**、**[`chart_family3_composition_and_flow.md`](chart_family3_composition_and_flow.md)**、**[`distribution_and_density_chart_spec.md`](distribution_and_density_chart_spec.md)** 或 **[`chart_family5_multivariate_and_spatial.md`](chart_family5_multivariate_and_spatial.md)**；若第三層開啟模式 2 則加讀 **[`editorial_narrative_spec.md`](editorial_narrative_spec.md)**，若開啟模式 3 則加讀 **[`creative_armory/INDEX.md`](creative_armory/INDEX.md)**。
> - **筆風設定檔 100% 穿透綁定**：儀表板標題、KPI 卡、頁籤、座標軸籤與 Tooltip 解說微文案受 **`Slot 6`** 與 **`Slot 8`** 控制（[`visual_cognition_principles.md`](visual_cognition_principles.md)）。

---

## 一、 動態數據維度與呈現拓撲：嚴禁寫死圖表類型與呈現方式（Zero Hardcoded Layouts）

> [!IMPORTANT]
> **動態生成核心鐵律**：**絕對禁止寫死數據儀表板的圖表類型、頁籤數量或呈現方式**（嚴禁不論遇到何種資料都機械套用固定四圖或固定版型）！
> 內部要生成哪些圖表，必須完全依據 **[`advisors/layer2_advisor_de_chart.md`](advisors/layer2_advisor_de_chart.md)** 之「資料結構四維快篩 × 8 大溝通意圖決策樹」動態選配；其單圖繪製與編碼防詐欺守則完全遵循 [`quantitative_chart_spec.md`](quantitative_chart_spec.md) 及對應之 `chart_family1~5` 規格檔。

### 1. 動態呈現方式與版面拓撲（Adaptive Presentation & Layout Topologies）
遵循 **Shneiderman (1996) 視覺資訊尋求箴言（*"Overview first, zoom and filter, then details-on-demand"*）** 與 [`visual_cognition_principles.md`](visual_cognition_principles.md) 之 **$4 \to 2 \to 3$ 階層組塊原則**，依資料規模與使用者需求動態選擇呈現架構：

1. **【呈現模式 A：多視角切換互動工作台（Multi-Perspective Interactive Workbench）】**
   - **適用情境**：資料具備多個觀察切面（如同時含結構組成、跨實體排行、期比增減、分配密度或多指標切換）。
   - **動態組件**：頂部全局維度控制列（時間／分群／口徑切換／排序）$\rightarrow$ 頂層 3～4 張關鍵 KPI 摘要卡 $\rightarrow$ 動態生成之 $N$ 個互動視角頁籤（Tabs）$\rightarrow$ 底部支援即時搜尋、排序與一鍵匯出 CSV（含 `\uFEFF` UTF-8 BOM）之明細資料表。
2. **【呈現模式 B：多面板全景聯動網格（Synchronized Multi-Panel Bento Grid）】**
   - **適用情境**：需要在單一畫面同時比對「全局結構 × 關鍵排行 × 變化趨勢／落差診斷」以進行高階主管決策。
   - **動態組件**：採用不對稱 Bento 網格（如左側主視覺面板佔 `55%~60%` 寬度呈現核心結構或跨階段軌跡，右側上下堆疊 2 個互補副面板呈現常態化排行與正負偏差），各面板間遵守**跨面板色相區隔與固定類別色碼綁定**。
3. **【呈現模式 C：雙模態協同交付（Self-Contained Web Dashboard + High-Res Static Overview PNG）】**
   - **互動網頁端**：產出零後端依賴、雙擊 `index.html` 即可離線秒開、且可直接綁定獨立 Git 儲存庫發布為線上網站的互動式 Web 專案（使用 `ECharts` / `Chart.js` / `Plotly` / 原生 Canvas 等）。
   - **靜態出版端**：同步以 Python `matplotlib` (`GridSpec`) 渲染一張遵循完全相同配色與黃金比例垂直空間規範（`24" × 14"`, `dpi=300`）的出版級靜態全景儀表板圖（`.png`）。

### 2. 第三層設計武器庫連動（模式 2 編輯室工作台 & 模式 3 主題沉浸式策展網頁）
- 若第三層開啟 **模式 2 (`editorial_narrative`)**：頂部 KPI 卡增設「與基準線正負差距膠囊」，圖表區提供「統計基準線切換開關（未加權平均／官方加權／中位數）」與「首尾極值聚光燈高亮」控制項。
- 若第三層開啟 **模式 3 (`bespoke_metaphor`)**：直接調用 `window.GephiPalette.deriveThematicPalette(presetOrHex, { activate: true })` 將主題語義色階動態注入 CSS `:root`，並可於卡片中嵌入容器式液面進度條或 $10 \times 10$ 象形陣列佔比卡（詳見 [`creative_armory/INDEX.md`](creative_armory/INDEX.md) 與 [`creative_armory/cases/03_spatial_and_thematic/thematic_palette_frame.md`](creative_armory/cases/03_spatial_and_thematic/thematic_palette_frame.md)）。

---

## 二、 鎖定版圖表配色前端實作與黑盒引擎 API（Frontend Color Implementation & Black-Box API — 雙向連動 SSOT）

> **單一事實來源（SSOT）**：完整之 **無序類別 4 色表、4 組 5 階循序色階表、9 階對稱發散色階表，以及製圖前 6 項確認條件與 5 大執行鐵律**，權威收納於 **[`quantitative_chart_spec.md`](quantitative_chart_spec.md) 第三節**（由本機 `config/user_preferences.json` 動態驅動，公開倉庫僅附中性預設與 CIELAB 自動推導引擎）。本節僅定義前端 CSS/JS 變數映射與黑盒 API 呼叫規範，避免跨檔重複。

### 1. 黑盒色彩引擎 API 簽名（`scripts/gephi_palette.js` ⇄ `scripts/hcl_color_engine.py`）
> [!IMPORTANT]
> **【底層引擎黑盒呼叫鐵律（Black-Box API Rule）】**：建構 Format E 互動網頁與靜態全景圖時，Python 端直接調用 `hcl_color_engine.export_gephi_palette_js("./js/gephi_palette.js")` 匯出前端色彩引擎，並於 `index.html` 引入 `<script src="./js/gephi_palette.js"></script>`。**日常執行嚴禁呼叫 `view_file` / `read_file` 讀取 `scripts/*.py` 或 `scripts/*.js` 原始碼**（除非除錯需要）！

```javascript
// === scripts/gephi_palette.js (window.GephiPalette) Black-Box API Signatures ===
const {
  PALETTE,                        // { categories, badgeTints, other: '#CBD5E1', na: '#D9D9D9', divergingCenter: '#F5F6F7', seqOrange, seqBlue, seqPink, seqGreen, divergingHex }
  THEMATIC_PRESETS,               // Built-in CIELAB thematic presets (milk_tea, forest_eco, ocean_blue, coffee_roast, pineapple_tropical, ...)
  labInterpolate,                 // (hexList, t) -> '#RRGGBB' (True CIELAB piecewise linear interpolation)
  getSequentialColor,             // (val, min, max, scale='orange', discreteSteps=false) -> '#RRGGBB' (Enforces (val - min)/(max - min) normalization)
  getDivergingColor,              // (val, center=0, maxSpan=1, discreteSteps=false) -> '#RRGGBB' (Symmetric 9-node mapping around #F5F6F7)
  bindQualitativeColors,          // (categories, allowTop4Aggregation=true, otherLabel='其他項目合計') -> { colorMap, badgeTintMap, top4Categories, otherCategories }
  getCategoryBadgeTint,           // (catOrKey, badgeTintMap) -> active PALETTE.badgeTints[0..3] | '#F1F5F9'
  buildPaletteFromPrimaryHexes,   // (hexList) -> customPaletteObj (CIELAB auto-derivation from 2~4 primary hex colors)
  deriveThematicPalette,          // (themePresetOrHex, options={ activate: false }) -> customPaletteObj (CIELAB thematic derivation)
  setActivePalette,               // (customPaletteObj) -> PALETTE (Switches active frontend palette in-place)
} = window.GephiPalette;
```
```python
# === scripts/verify_visual_outputs.py Black-Box API Signature ===
from verify_visual_outputs import verify_dashboard_bundle # (dashboard_dir) -> dict (CLI: --verify-dashboard)
```

### 2. 前端 `css/style.css` 標準 `:root` 變數與四大色彩工程鐵律
1. **CSS `:root` 集中變數映射**（數值須與當前啟用 `PALETTE.categories` 與 `PALETTE.badgeTints` 100% 同步）：
   ```css
   :root {
     --color-cat-1: <PALETTE.categories[0]>; --tint-cat-1: <PALETTE.badgeTints[0]>; /* 1. 主色（色序 1）& 0.00 極淺底色 */
     --color-cat-2: <PALETTE.categories[1]>; --tint-cat-2: <PALETTE.badgeTints[1]>; /* 2. 次色（色序 2）& 0.00 極淺底色 */
     --color-cat-3: <PALETTE.categories[2]>; --tint-cat-3: <PALETTE.badgeTints[2]>; /* 3. 第三色（色序 3）& 0.00 極淺底色 */
     --color-cat-4: <PALETTE.categories[3]>; --tint-cat-4: <PALETTE.badgeTints[3]>; /* 4. 第四色（色序 4）& 0.00 極淺底色 */
     --color-other: #CBD5E1; --color-na:   #D9D9D9; --div-zero: #F5F6F7;
   }
   ```
2. **跨視角同名類別色彩鎖定（Global `categoryColorMap` Lock）**：
   - 初始化時必須針對全資料集呼叫 `bindQualitativeColors(sortedCats, true)` 建立全域固定 `categoryColorMap` 與 `badgeTintMap`。當使用者切換地區分組、排序或頁籤時，必須從 `categoryColorMap[cat]` 取色，**嚴禁依當前畫面陣列 `idx` 重新計算 Top 4 或換色**。
3. **零 Alpha 透明度鐵律與 `0.00` 淺底色徽章（Zero-Alpha Badge Tints）**：
   - **嚴禁使用 Alpha 透明度（如 `rgba(...)` 或 `${hex}20`）冒充數值明度或表格膠囊底色**！明細表或 UI 內的類別標籤底色，必須一律使用對應循序色階的 `0.00` 極淺節點（直接調用 `getCategoryBadgeTint(cat, badgeTintMap)`）。
4. **正確數值正規化公式、`>4` 類別展開防呆與原表 `df_other` 雙重語義消歧**：
   - **純明細 `df_detail` 正規化公式**：連續循序圖表必須先剔除合計／小計列（`df_subtotal`），傳入純明細 `df_detail` 之真實 `vMin` 與 `vMax` 調用 `getSequentialColor(val, vMin, vMax, scale)`（依 $(v - v_{\min}) / (v_{\max} - v_{\min})$ 正規化，**嚴禁簡化為 $v / v_{\max}$ 或混入合計列極值**）。
   - **超過 4 個無序類別之展開規範與原表 `df_other` 消歧**：預設啟用「**智慧 4+1 聚焦視角**」（前四大綁定四色，其餘聚合為 `#CBD5E1`）。**嚴禁讓原表自帶的 `其他` 列（`df_other`）混入前四大彩色主色柱，亦嚴禁同屏出現兩個「其他」**！若原表存在 `df_other`，須依與使用者拍板之策略選用：**選項 1（純明細聚焦＋註腳揭露原表其他項）** 或 **選項 2（長尾透明整併，傳入 `otherLabel: '其餘明細與原表其他項合計'`）**。若提供「展開全部細項」切換開關，展開時**必須維持前四大為固定四色、其餘細項採用典雅結構灰階（`#CBD5E1` / `#94A3B8`）搭配滑鼠懸停高亮（`emphasis: { focus: 'series' }`），或自動切換為單一循序色階之橫向排行圖，絕對禁止將 5 階循序色階拿去模除循環（`seqOrange[idx % 5]`）塗抹 30 個無序類別**！

### 3. 前端排版三要素與標準 CSS 基準骨架（Baseline Typography & 3-Tier Surface CSS Template）
撰寫本地 `./css/style.css` 時，必須同時落實以下三項排版工程紀律，並直接以基準 CSS 骨架為出發點（色彩由 `gephi_palette.js` 與 `:root` 動態驅動，嚴禁過度花俏之深重陰影）：
1. **等寬數值對齊（`tabular-nums`）**：所有 KPI 大數字（`.kpi-value`）、基準線差距膠囊（`.delta-pill`）與明細表數值欄（`td.num`, `th.num`）強制設定 `font-variant-numeric: tabular-nums; font-feature-settings: "tnum";`，確保跨列數字小數點與千分位垂直 100% 對齊。
2. **三層表面高度與留白階梯（3-Tier Surface Hierarchy）**：
   - **Tier 1 全局控制列（`.control-bar` & `.segmented-control`）**：低對比 `#F1F5F9` 膠囊槽、無陰影，視覺退居幕後，避免按鈕縮放亂跳。
   - **Tier 2 主角卡片（`.kpi-card` & `.chart-panel`）**：純白 `#FFFFFF` 底、`1px solid #E2E8F0` 細框、克制微陰影 `0 1px 3px rgba(15, 23, 42, 0.04)`，主圖表區保持寬裕內距 `24px 28px`。
   - **Tier 3 明細資料表（`.data-table-wrap` & `.data-table`）**：黏性表頭（`position: sticky; top: 0;`）、緊湊行高、數值右對齊。
3. **開箱即用標準 CSS 基準範本（複製進 `./css/style.css` 並補齊 `:root` 變數）**：
   ```css
   body { background: #F8FAFC; color: #0F172A; font-family: "Microsoft JhengHei", "Noto Sans TC", system-ui, -apple-system, sans-serif; line-height: 1.55; }
   .control-bar { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 14px; background: #F1F5F9; border-radius: 10px; border: 1px solid #E2E8F0; }
   .segmented-control { display: inline-flex; flex-wrap: wrap; gap: 4px; background: #E2E8F0; padding: 3px; border-radius: 8px; }
   .segmented-control button { border: 0; background: transparent; color: #475569; padding: 6px 12px; border-radius: 6px; font-size: 0.875rem; font-weight: 600; cursor: pointer; }
   .segmented-control button.active { background: #FFFFFF; color: #0F172A; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06); }
   .kpi-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px 20px; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04); }
   .kpi-label { font-size: 0.8125rem; font-weight: 600; color: #64748B; letter-spacing: 0.02em; margin-bottom: 6px; }
   .kpi-value { font-size: 1.875rem; font-weight: 700; color: #0F172A; line-height: 1.2; font-variant-numeric: tabular-nums; font-feature-settings: "tnum"; }
   .delta-pill { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; font-variant-numeric: tabular-nums; font-feature-settings: "tnum"; }
   .chart-panel { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 24px 28px; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04); }
   .data-table-wrap { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; overflow: auto; }
   .data-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
   .data-table th { position: sticky; top: 0; background: #F8FAFC; color: #475569; font-weight: 600; text-align: left; padding: 10px 14px; border-bottom: 1px solid #E2E8F0; }
   .data-table td { padding: 9px 14px; border-bottom: 1px solid #F1F5F9; color: #1E293B; }
   .data-table th.num, .data-table td.num { text-align: right; font-variant-numeric: tabular-nums; font-feature-settings: "tnum"; }
   ```

---

## 三、 Format E 專屬互動回饋、75-20-5 與全景靜態圖佈局守則（Format E Interactive Polish & Static Overview）

所有共通之三層互斥分流（`df_detail`/`df_other`/`df_subtotal` `assert`）、極性同質化、零旋轉中文標籤、編碼誠實三鐵律與單面板黃金比例畫布，**一律直接引用 [`quantitative_chart_spec.md`](quantitative_chart_spec.md) 及對應之 `chart_family1~5` 規格檔（免跨檔重複抄寫）**；Format E 額外執行以下互動與全景圖專屬守則：
1. **高可讀性自訂 Tooltip 與直接數據回饋**：互動式圖表必須配置含色塊圖示、等寬對齊精確數值、單位與佔比提示之自訂 `tooltip`；單序列排行／發散圖於末端直接顯示數值標籤；隱藏不必要的外框線（靜態端調用 `despine_axes(ax)`），僅留極淡 `#F1F5F9` / `#CBD5E1` 輔助網格線。
2. **75-20-5 畫布呼吸與微軟正黑體零 Emoji 防護**：整體頁面採 75% 中性結構底色（畫布 `#F8FAFC`、卡片 `#FFFFFF`、邊框 `#E2E8F0`、主字 `#0F172A` / `#1E293B`、次字 `#475569` / `#64748B`），頁尾標註原始官方發布機關與資料集（1. 官方資料集網址、2. 資料涵蓋期間）；靜態輸出圖嚴禁 Emoji（僅用 `▲`、`●`、`■`、`★`）。
3. **多面板靜態全景儀表板匯出圖（`GridSpec` Overview PNG，預設 `24" × 14"`, `dpi=300`）**：維持寬景比例（`1.71:1`），明確切分頂部主副標題、共用圖例／KPI 摘要條、主多面板視覺化區（占總高約 `62%–72%`，`GridSpec` 邊界建議 `top ≈ 0.80–0.84`、`bottom ≈ 0.08–0.12`）與底部官方來源圖註，各層間維持均衡垂直間距（單面板靜態匯出直接套用 [`quantitative_chart_spec.md`](quantitative_chart_spec.md) `12.0" × 6.4"` / `12.8" × 6.7"` 黃金比例標準）。

---

## 四、 零後端自包含前端架構、獨立 Git 綁定與網站部署規範（Self-Contained Engineering, Git Binding & Web Deployment）

### 1. 雙擊即開且相容子路徑部署之 Git-Ready 檔案結構（Zero-Backend & Git-Ready Package Structure）
每個生成的互動式 Web 數據儀表板，預設皆視為**「準備綁定獨立 Git 儲存庫並發布為線上網站（如 GitHub Pages / GitLab Pages / Vercel / Netlify）」**的標準靜態網站專案，必須一次生成以下完整模組化結構：
- `index.html`：響應式語義化佈局（頂部標題與資料來源聲明、動態維度控制列、KPI 摘要卡片區、主視覺化圖表區、底部搜尋明細表與 CSV 匯出按鈕）。
  - **【純相對路徑鐵律（Strict `./` Relative Paths）】**：`index.html`、`css/style.css` 與 `js/dashboard.js` 內部引用任何本地資源時，**必須一律使用明確的 `./` 相對路徑**（如 `./css/style.css`、`./js/gephi_palette.js`、`./js/dashboard.js`、`./data/<dataset>_data.js`、`fetch('./data/<dataset>_data.json')`），**嚴禁使用以 `/` 開頭的根目錄絕對路徑**（如 `/css/style.css`），確保同時 100% 相容於：(1) 檔案總管 `file://` 直接雙擊開啟、(2) 獨立網域根目錄，以及 (3) GitHub Pages 子路徑網站（`https://<username>.github.io/<repo-name>/`）而絕不發生 404 破圖或腳本載入失敗！
  - **【禁用執行期 `cdn.tailwindcss.com` 鐵律（Zero Runtime Tailwind CDN）】**：**嚴禁依賴 `<script src="https://cdn.tailwindcss.com"></script>`**（不僅產生 Console 生產環境警告，更會導致離線環境版面崩潰）！所有網格、卡片、按鈕、表格與響應式排版樣式必須完整編寫於本地 `./css/style.css` 中。
- `css/style.css`：於 `:root` 集中定義當前啟用配色設定集之所有 CSS 變數（`--color-cat-1`、`--tint-cat-1` 等，與 `js/gephi_palette.js` 同步）與完整自包含 UI 樣式，確保零外部 CSS 框架依賴。
- `js/gephi_palette.js` ＋ `js/dashboard.js`：由 `hcl_color_engine.export_gephi_palette_js("./js/gephi_palette.js")` 匯出權威 CIELAB 色彩引擎，`dashboard.js` 直接調用 `window.GephiPalette` 完成全域固定類別色碼映射、`(v - min)/(max - min)` 循序插值與 9 階對稱發散取色，並監聽 `window.addEventListener('resize', ...)` 自動自適應縮放。
- `data/<dataset>_data.js` ＋ `data/<dataset>_data.json`：**【離線雙載入防 CORS 鐵律】** 為了讓使用者在檔案總管直接雙擊 `index.html`（`file://` 協定）時不會因瀏覽器阻擋 `fetch('*.json')` 而白屏，必須同時將結構化資料輸出為 `data/<dataset>_data.js`（內含 `window.DASHBOARD_DATA = ...` 並於 `index.html` 以 `<script src="./data/<dataset>_data.js">` 引入）與標準 `.json` 檔！
- `.nojekyll`：於儀表板專案根目錄建立空白 `.nojekyll` 檔，防止 GitHub Pages 啟動 Jekyll 編譯器而忽略底線開頭檔案或拖慢部署速度。
- `.gitignore`：預先建立標準忽略清單（排除 `.DS_Store`、`Thumbs.db`、`*.log`、`.vscode/`、`.idea/`、`__pycache__/`、`node_modules/` 等），讓該目錄隨時可直接執行 `git init` 獨立版控。
- `README.md`：**【網站專案與 Git 部署指南】** 每個儀表板必須自動生成專屬 `README.md`，內容須包含：(1) 儀表板核心特色與視角說明、(2) 專案檔案結構樹（含 `.nojekyll` 與 `.gitignore`）、(3) 本機雙擊與 HTTP Server 預覽方式、(4) **一鍵綁定獨立 Git 儲存庫並發布至 GitHub Pages（含 `gh` CLI 自動建庫、`main` 或 `gh-pages` 分支推送、防外層倉庫嵌套 `.git` 清理指令與 `git subtree` 方案）**、(5) 鎖定版 CIELAB 配色速查表與資料來源聲明。


### 2. 強制視覺與結構驗收（Mandatory Visual & Bundle Inspection Gate）
- 若包含靜態全景儀表板圖（`.png`），生成後必須透過 `view_file` 實際檢視渲染成品，確認無文字重疊、無穿線、無溢界、圖例與標題對齊完美。
- 若為互動式 Web 儀表板，必須執行 `python .agents/skills/deep-reading-and-visual-synthesis/scripts/verify_visual_outputs.py --verify-dashboard "<儀表板目錄>"`（或呼叫 `verify_dashboard_bundle()`）確認基礎檔案齊備、零 Tailwind CDN、純 `./` 相對路徑、`data/*_data.js` + `.json` 雙檔齊全、`css/style.css` 含 `:root` 與 `tabular-nums` 且無殘留嵌套 `.git`；同時確認所有篩選控制項、視角切換、Tooltip 單位顯示與 CSV 匯出（含 `\uFEFF` UTF-8 BOM 防 Excel 中文亂碼）運作正常，並清除任何臨時測試腳本或廢棄預覽檔。

### 3. 獨立 Git 儲存庫綁定與網站發布標準流程（Git Repository Binding & Live Website Deployment Workflow）
由於每個數據儀表板生成完成後，皆預期綁定一個獨立 Git 儲存庫並架設為網站，AI 於完成儀表板渲染與驗收後，**必須執行以下「Git 網站綁定與部署閉環」**：

1. **步驟 A：主動回報部署就緒狀態並詢問遠端綁定方式（Proactive Deployment Prompt）**
   - 交付成果時，除了告知本機雙擊 `index.html` 預覽路徑外，主動詢問使用者是否要**立即綁定獨立 Git 儲存庫並發布為線上網站**：
     - **方式 1（提供遠端 Git URL 直接綁定推送）**：請使用者提供新建之空白 GitHub / GitLab 儲存庫網址（例如 `https://github.com/<username>/<repo-name>.git`），由 AI 自動完成初始化、綁定推送（`main` 或 `gh-pages` 分支）與內層 `.git` 無損清理。
     - **方式 2（透過 GitHub CLI `gh` 全自動建庫＋開通 GitHub Pages）**：若使用者環境已登入 `gh` CLI，只需指定儲存庫名稱（如 `<repo-name>`），即可由 AI 自動建立公開儲存庫、推送程式碼並啟用 GitHub Pages。
     - **方式 3（保留 Git-Ready 封裝供後續手動推送）**：若當下暫不綁定，專案目錄內已備妥 `.gitignore`、`.nojekyll` 與寫好專案路徑的 `README.md` 部署指令，使用者後續隨時可複製指令一鍵上線。

2. **步驟 B：執行獨立 Git 綁定、推送與 GitHub Pages 自動開站（Standard Binding & Publishing Commands）**
   - **標準獨立倉庫初始化與推送指令（支援推送至 `main` 或 `gh-pages` 分支，自動繼承外層倉庫 Git 身分並內建推送後清理內層 `.git` 防護）**：
     ```bash
     # 1. 先從外層主倉庫讀取 Git 身分（防止本機未設定 --global .gitconfig 導致 Author identity unknown 報錯）
     GIT_USER_NAME=$(git config user.name || echo "dashboard-bot")
     GIT_USER_EMAIL=$(git config user.email || echo "dashboard-bot@users.noreply.github.com")

     cd "<儀表板專案目錄>"
     git init
     git config user.name "$GIT_USER_NAME"
     git config user.email "$GIT_USER_EMAIL"
     git add -A
     git commit -m "feat(dashboard): initial release of interactive data dashboard"
     git branch -M main
     git remote add origin https://github.com/<username>/<repo-name>.git
     # 推送至 main 分支（若欲直接以 gh-pages 分支開站，可改為 git push -u origin main:gh-pages --force）
     git push -u origin main
     # 【關鍵防護】若此目錄位於外層主倉庫 (reading_sessions/...) 內，推送完畢立即移除內層 .git 避免外層產生 gitlink 空指標：
     # PowerShell: Remove-Item -Recurse -Force .git
     # Bash:       rm -rf .git
     ```
   - **GitHub CLI 一鍵建庫與開啟 GitHub Pages 網站（若 `gh auth status` 可用；參數加引號確保 PowerShell 與 Bash 雙相容）**：
     ```bash
     GIT_USER_NAME=$(git config user.name || echo "dashboard-bot")
     GIT_USER_EMAIL=$(git config user.email || echo "dashboard-bot@users.noreply.github.com")

     cd "<儀表板專案目錄>"
     git init
     git config user.name "$GIT_USER_NAME"
     git config user.email "$GIT_USER_EMAIL"
     git add -A
     git commit -m "feat(dashboard): initial release of interactive data dashboard"
     git branch -M main
     gh repo create <repo-name> --public --source=. --remote=origin --push
     gh api repos/{owner}/{repo}/pages -X POST -F build_type=legacy -F "source[branch]=main" -F "source[path]=/"
     # 【關鍵防護】若位於外層主倉庫內，發布後立即移除內層 .git 以確保外層主倉庫完整備份所有前端原始碼：
     # PowerShell: Remove-Item -Recurse -Force .git
     # Bash:       rm -rf .git
     ```
     部署完成後，立即向使用者回報正式網站網址：`https://<username>.github.io/<repo-name>/`（亦可直接匯入 Vercel / Netlify 零設定部署）。

3. **步驟 C：【雙倉庫無損同步護欄 — 嚴防外層主倉庫嵌套 `.git` 子模組衝突（Nested Gitlink Prevention）】**
   - **核心風險**：當儀表板目錄位於本技能主倉庫（`deep-reading-and-visual-synthesis/reading_sessions/...`）內部時，若在子目錄內執行 `git init` 後保留子目錄的 `.git/` 資料夾，外層主倉庫在執行階段完成自動同步（`git add -A`）時，會將該儀表板目錄誤判為未配置的 **Git 子模組（gitlink，mode `160000`）**，導致外層主倉庫只記錄一筆空指標而**無法追蹤並備份儀表板內部的 `index.html`、`css/`、`js/`、`data/` 原始碼**！
   - **強制防衝突處置原則（二擇一）**：
     - **方案 1（獨立推送後清理內層 `.git` 或使用 `--git-dir` 隔離法 — 預設推薦）**：如上方步驟 B 所示，在子目錄內完成向獨立網站 Git 儲存庫的 `git push` 後，於執行外層主倉庫 `git add -A` 前，**必須先移除子目錄內的 `.git` 資料夾**（PowerShell：`Remove-Item -Recurse -Force .git`；Bash：`rm -rf .git`），或從頭使用外部臨時 Git 目錄（`git --git-dir="$env:TEMP/dashboard_git" --work-tree="." ...`）執行推送。如此既能讓**獨立網站 Git 儲存庫成功發布 GitHub Pages**，又能讓**主知識庫完整備份每一支前端檔案**！
     - **方案 2（`git subtree split/push` 子樹直推法 — 零內層 `.git`）**：先將儀表板所有檔案正常 commit 至外層主倉庫，再於主倉庫根目錄執行：
       ```bash
       git subtree split --prefix="reading_sessions/<YYYYMMDD_主題簡稱>/<儀表板子路徑>" -b dashboard-deploy
       # 可直接推送至目標獨立倉庫之 main 或 gh-pages 分支：
       git push https://github.com/<username>/<repo-name>.git dashboard-deploy:main --force
       git branch -D dashboard-deploy
       ```
       即可在不產生任何嵌套 `.git` 的情況下，將該儀表板目錄做為乾淨的根目錄獨立推送到目標網站 Git 儲存庫！

