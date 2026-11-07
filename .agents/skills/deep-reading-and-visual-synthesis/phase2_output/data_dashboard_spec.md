# 數據儀表板設計與互動／靜態雙模態實作規範（Format E: Data Dashboard Spec）

> **單一職責定位（Single Responsibility）**：本檔專責 **Format E（數據儀表板：互動式 Web 數據儀表板 `.html`/`.css`/`.js` ＋ 出版級靜態全景儀表板圖 `.png`）** 的**動態圖表選型與版面配適架構（嚴禁寫死圖表類型與呈現格式）**、**鎖定版個人圖表配色規範（`Gephi · pastel` CIELAB / HCL 均衡色系）**、跨視角固定色序綁定，以及**零後端自包含（Self-Contained）前端工程、獨立 Git 儲存庫綁定與靜態網站發布（GitHub Pages 等）驗收守則**。跨格式共用的組塊階層（$4 \to 2 \to 3$）與白話由淺入深原則請見 [`visual_cognition_principles.md`](visual_cognition_principles.md)。
>
> 🔗 **【Format E（數據儀表板）⇄ Format D（量化圖表）雙向連動與同步更新鐵律】**：
> 本檔（[`data_dashboard_spec.md`](data_dashboard_spec.md)）與 **[`quantitative_chart_spec.md`](quantitative_chart_spec.md)（Format D：量化實證圖表規範）** 及 **[`scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)** 屬於**雙向連動共生規範**，共用完全相同的「鎖定配色設定集」與「圖表視覺設計規則（座標映射、極性同質化、色階分流、去框座標軸、標籤對齊與製圖前 6 項確認條件）」。**往後凡涉及圖表配色或共通設計規則之任何新增、修改或技能進化（Step E3），必須強制同步更新本檔、`quantitative_chart_spec.md` 與 `scripts/hcl_color_engine.py`，嚴禁單邊改動導致規則脫節！**

---

## 一、 動態數據維度與任務驅動架構：嚴禁寫死圖表類型與呈現方式（Zero Hardcoded Chart Types or Layouts）

> [!IMPORTANT]
> **動態生成核心鐵律**：
> **絕對禁止寫死數據儀表板的圖表類型、頁籤數量或呈現方式**（例如：嚴禁不論遇到何種資料都機械式套用固定的「結構堆疊＋排行榜＋增減發散＋單項深鑽」四種圖表或固定版型）！
> 儀表板內部要生成哪幾種圖表、採用何種互動控制項與空間佈局，必須完全根據**「輸入數據的真實維度結構（Data Dimensionality & Schema）」**與**「核心分析決策任務（Analytical Tasks）」**動態推導組合。

### 1. 任務導向之動態圖表選型引擎（Task-Driven Dynamic Chart Selection — 與 [`quantitative_chart_spec.md`](quantitative_chart_spec.md) 連動）
在規劃儀表板前，先盤點數據包含哪些維度（時間序列、無序類別、有序成熟度、地理/組織實體、正負增減偏差、雙指標落差或多變數關聯），依下列任務動態選配最合適的圖表型態：

| 核心數據特徵與分析任務 | 動態選配之最佳圖表類型（依資料特性自由組合，不限單一形式） | 連動設計與配色規則（詳見第二、三節及 [`quantitative_chart_spec.md`](quantitative_chart_spec.md)） |
| :--- | :--- | :--- |
| **1. 跨階段留存遞減／漏斗流失／時序軌跡演進**<br>*(Stage Progression / Funnel / Time-Series Trajectory)* | • **XY 軸空間重力折線＋直柱複合圖（Combo Column + Drop Line Trajectory）**<br>• **多序列趨勢折線圖／面積軌跡圖（Multi-Series Line / Area Chart）** | • **強制空間重力映射**：X 軸為由左至右階段／時間推進，Y 軸為垂直高度（嚴禁將遞減階段塞入水平長條圖 Y 軸）。<br>• 單一指標採用**主色循序（暖杏橘系）**；多類別軌跡依**固定四色序**綁定，並標註關鍵斷崖落差 $\Delta$。 |
| **2. 同實體內部雙指標反差／預期 vs. 實際落差**<br>*(Paired Dual-Metric Contrast / Target vs. Actual)* | • **共同基準線並排配對雙柱＋剪刀差標註圖（Paired Dual-Bar + Explicit Gap Callout）**<br>• **啞鈴跨距圖（Dumbbell Plot）或子彈圖（Bullet Chart）** | • 嚴禁使用單一折線表達同案雙維落差。<br>• 第一指標（基準／預期）綁定**主色暖杏蜜橘 `#ECA072`**，第二指標（對比／實際）綁定**次色霧靄青藍 `#5DBACD`**，並直接標註差值膠囊（`Δ = ±XX%`）。 |
| **3. 多維度結構組成與核心支柱拆解**<br>*(Part-to-Whole / Structural Composition)* | • **堆疊長條／直柱圖（Stacked Bar / Column，支援總額與 `100%` 佔比切換）**<br>• **群組並排比較圖（Grouped Bar）、矩形樹圖（Treemap）或旭日圖（Sunburst）** | • 類別數 $\le 4$ 時依序綁定**固定類別四色**。<br>• 若原始細項超過 4 個（如數十個細目），向使用者確認擴充方式，或啟用**「智慧 4+1 聚焦視角」**：自動萃取前四大核心支柱綁定四色，長尾細項聚合為第五項**典雅灰 `#CBD5E1`**（並可提供切換開關）。 |
| **4. 多實體規模排行／常態化強度對比**<br>*(Entity Ranking / Normalized Per-Capita Magnitude)* | • **橫向排行長條圖（Horizontal Ranking Leaderboard）**<br>• **棒棒糖排行圖（Lollipop Chart）或點陣分佈圖（Dot Plot）** | • 依數值正規化位置 $p \in [0, 1]$ 映射至 **5 階循序色階**（主視角預設用**暖杏橘系循序**；若為單一類別深鑽或次面板對照則用**霧靄藍系循序**），低值淺、高值深。 |
| **5. 基準正負偏差／期比增減／達標率檢視**<br>*(Deviation from Reference / YoY Growth / Variance)* | • **雙向發散長條圖（Diverging Bar / Butterfly Chart）**<br>• **正負偏差熱力矩陣（Diverging Heatmap）或瀑布圖（Waterfall Chart）** | • 嚴格鎖定 **9 階對稱發散色階**：以指定業務基準（如偏差 `0%` 或達標率 `100%`）為中心 `#F5F6F7`，負向／未達標往**霧靄藍系（極值 `#0E5B6B`）**延伸，正向／超標往**暖杏橘系（極值 `#884725`）**延伸。 |
| **6. 多變數關聯、交叉分佈與單項深鑽探索**<br>*(Multi-Variate Correlation / Distribution / Deep-Dive)* | • **雙軸散佈／氣泡圖（Scatter / Bubble Plot，含象限基準線）**<br>• **交叉維度熱力圖（Matrix Heatmap）、箱形圖（Boxplot）或單維度深鑽器（Deep-Dive Selector）** | • 氣泡或分群類別綁定固定四色序；熱力強度使用 CIELAB 5 階循序或 9 階發散插值，嚴禁使用 Alpha 透明度冒充明度深淺。 |

### 2. 動態呈現方式與版面拓撲（Adaptive Presentation & Layout Topologies）
遵循 **Shneiderman (1996) 視覺資訊尋求箴言（*"Overview first, zoom and filter, then details-on-demand"*）** 與 [`visual_cognition_principles.md`](visual_cognition_principles.md) 之 **$4 \to 2 \to 3$ 階層組塊原則**，依資料規模與使用者需求動態選擇呈現架構（不寫死單一面板結構）：

1. **【呈現模式 A：多視角切換互動工作台（Multi-Perspective Interactive Workbench）】**
   - **適用情境**：資料具備多個觀察切面（如同時含結構組成、跨實體排行、期比增減、細項深鑽或多指標切換）。
   - **動態組件**：頂部全局維度控制列（時間／分群／口徑切換／排序）$\rightarrow$ 頂層 3～4 張關鍵 KPI 摘要卡（含基準比較或極值亮點）$\rightarrow$ 依資料特性動態生成的 $N$ 個互動視角頁籤（Tabs）或視圖切換器 $\rightarrow$ 底部支援即時搜尋、排序與一鍵匯出 CSV 之明細資料表。
2. **【呈現模式 B：多面板全景聯動網格（Synchronized Multi-Panel Bento Grid）】**
   - **適用情境**：需要在單一畫面同時比對「全局結構 × 關鍵排行 × 變化趨勢／落差診斷」以進行高階主管決策。
   - **動態組件**：採用不對稱 Bento 網格（如左側主視覺面板佔 `55%~60%` 寬度呈現核心結構或跨階段軌跡，右側上下堆疊 2 個互補副面板呈現常態化排行與正負偏差），各面板間遵守**跨面板色相區隔與固定類別色碼綁定**。
3. **【呈現模式 C：雙模態協同交付（Self-Contained Web Dashboard + High-Res Static Overview PNG）】**
   - **互動網頁端**：產出零後端依賴、雙擊 `index.html` 即可離線秒開、且可直接綁定獨立 Git 儲存庫發布為線上網站的互動式 Web 專案（使用 `ECharts` / `Chart.js` / `Plotly` / 原生 Canvas 等）。
   - **靜態出版端**：當需要將儀表板精華嵌入報告（Format B）、簡報（Format C）或提供靜態高畫質預覽時，同步以 Python `matplotlib` (`GridSpec`) 渲染一張遵循完全相同配色與設計規則的出版級靜態全景儀表板圖（`.png`）。

---

## 二、 鎖定版圖表配色前端實作與黑盒引擎 API（Frontend Color Implementation & Black-Box API — 雙向連動 SSOT）

> **單一事實來源（SSOT）**：完整之 **無序類別 4 色表、4 組 5 階循序色階表、9 階對稱發散色階表，以及製圖前 6 項確認條件與 5 大執行鐵律**，權威收納於 **[`quantitative_chart_spec.md`](quantitative_chart_spec.md) 第三節**（源自 [個人圖表配色設定 Google Doc](https://docs.google.com/document/d/1puNpLGR7hYcyvZL1DZMdUpmP9fXM-TQcxu1N6QyGb1E/edit?usp=sharing)，`ggsci` `Gephi · pastel` $L^* \approx 72$ 均衡版）。本節僅定義前端 CSS/JS 變數映射與黑盒 API 呼叫規範，避免跨檔重複。

### 1. 黑盒色彩引擎 API 簽名（`scripts/gephi_palette.js` ⇄ `scripts/hcl_color_engine.py`）
> [!IMPORTANT]
> **【底層引擎黑盒呼叫鐵律（Black-Box API Rule）】**：建構 Format E 互動網頁與靜態全景圖時，Python 端直接調用 `hcl_color_engine.export_gephi_palette_js("./js/gephi_palette.js")` 匯出前端色彩引擎，並於 `index.html` 引入 `<script src="./js/gephi_palette.js"></script>`。**日常執行嚴禁呼叫 `view_file` / `read_file` 讀取 `scripts/*.py` 或 `scripts/*.js` 原始碼**（除非除錯需要）！

```javascript
// === scripts/gephi_palette.js (window.GephiPalette) Black-Box API Signatures ===
const {
  PALETTE,               // { categories: ['#ECA072','#5DBACD','#E89BB6','#8FBA88'], badgeTints: ['#FFF3EA','#EBF7F9','#FFF0F5','#F1F7EE'], other: '#CBD5E1', na: '#D9D9D9', divergingCenter: '#F5F6F7', seqOrange, seqBlue, seqPink, seqGreen, divergingHex }
  labInterpolate,        // (hexList, t) -> '#RRGGBB' (True CIELAB piecewise linear interpolation)
  getSequentialColor,    // (val, min, max, scale='orange', discreteSteps=false) -> '#RRGGBB' (Enforces (val - min)/(max - min) normalization)
  getDivergingColor,     // (val, center=0, maxSpan=1, discreteSteps=false) -> '#RRGGBB' (Symmetric 9-node mapping around #F5F6F7)
  bindQualitativeColors, // (categories, allowTop4Aggregation=true, otherLabel='其他項目合計') -> { colorMap, badgeTintMap, top4Categories, otherCategories }
  getCategoryBadgeTint,  // (catOrKey, badgeTintMap) -> '#FFF3EA' | '#EBF7F9' | '#FFF0F5' | '#F1F7EE' | '#F1F5F9'
} = window.GephiPalette;
```

### 2. 前端 `css/style.css` 標準 `:root` 變數與四大色彩工程鐵律
1. **CSS `:root` 集中變數映射**：
   ```css
   :root {
     --color-cat-1: #ECA072; --tint-cat-1: #FFF3EA; /* 1. 主色暖杏蜜橘 & 0.00 極淺底色 */
     --color-cat-2: #5DBACD; --tint-cat-2: #EBF7F9; /* 2. 次色霧靄青藍 & 0.00 極淺底色 */
     --color-cat-3: #E89BB6; --tint-cat-3: #FFF0F5; /* 3. 第三色落櫻粉黛 & 0.00 極淺底色 */
     --color-cat-4: #8FBA88; --tint-cat-4: #F1F7EE; /* 4. 第四色鼠尾草綠 & 0.00 極淺底色 */
     --color-other: #CBD5E1; --color-na:   #D9D9D9; --div-zero: #F5F6F7;
   }
   ```
2. **跨視角同名類別色彩鎖定（Global `categoryColorMap` Lock）**：
   - 初始化時必須針對全資料集呼叫 `bindQualitativeColors(sortedCats, true)` 建立全域固定 `categoryColorMap` 與 `badgeTintMap`。當使用者切換地區分組、排序或頁籤時，必須從 `categoryColorMap[cat]` 取色，**嚴禁依當前畫面陣列 `idx` 重新計算 Top 4 或換色**。
3. **零 Alpha 透明度鐵律與 `0.00` 淺底色徽章（Zero-Alpha Badge Tints）**：
   - **嚴禁使用 Alpha 透明度（如 `rgba(...)` 或 `${hex}20`）冒充數值明度或表格膠囊底色**！明細表或 UI 內的類別標籤底色，必須一律使用對應循序色階的 `0.00` 極淺節點（`#FFF3EA`、`#EBF7F9`、`#FFF0F5`、`#F1F7EE`，直接調用 `getCategoryBadgeTint(cat, badgeTintMap)`）。
4. **正確數值正規化公式、`>4` 類別展開防呆與原表 `df_other` 雙重語義消歧**：
   - **純明細 `df_detail` 正規化公式**：連續循序圖表必須先剔除合計／小計列（`df_subtotal`），傳入純明細 `df_detail` 之真實 `vMin` 與 `vMax` 調用 `getSequentialColor(val, vMin, vMax, scale)`（依 $(v - v_{\min}) / (v_{\max} - v_{\min})$ 正規化，**嚴禁簡化為 $v / v_{\max}$ 或混入合計列極值**）。
   - **超過 4 個無序類別之展開規範與原表 `df_other` 消歧**：預設啟用「**智慧 4+1 聚焦視角**」（前四大綁定四色，其餘聚合為 `#CBD5E1`）。**嚴禁讓原表自帶的 `其他` 列（`df_other`）混入前四大彩色主色柱，亦嚴禁同屏出現兩個「其他」**！若原表存在 `df_other`，須依與使用者拍板之策略選用：**選項 1（純明細聚焦＋註腳揭露原表其他項）** 或 **選項 2（長尾透明整併，傳入 `otherLabel: '其餘明細與原表其他項合計'`）**。若提供「展開全部細項」切換開關，展開時**必須維持前四大為固定四色、其餘細項採用典雅結構灰階（`#CBD5E1` / `#94A3B8`）搭配滑鼠懸停高亮（`emphasis: { focus: 'series' }`），或自動切換為單一循序色階之橫向排行圖，絕對禁止將 5 階循序色階拿去模除循環（`seqOrange[idx % 5]`）塗抹 30 個無序類別**！

---

## 三、 與 Format D（[`quantitative_chart_spec.md`](quantitative_chart_spec.md)）共通連動之圖表視覺設計守則

凡於數據儀表板內繪製任何統計圖表（無論是前端互動 Canvas/SVG 或 Python 靜態全景圖），皆須與 [`quantitative_chart_spec.md`](quantitative_chart_spec.md) 保持 100% 規則同步：

1. **三層互斥分流（`df_detail` / `df_other` / `df_subtotal`）與兩段式安全轉型防呆**：
   - 資料前處理腳本必須先將已知合法缺漏符號（如 `''`, `'-'`, `'...'`, `'N/A'`, `'＊'`）顯式映射為 `null` / `np.nan`（統一標記為 `#D9D9D9`），並將資料強制分流為 `df_detail`（純一般明細列）、`df_other`（原表其他列）與 `df_subtotal`（合計／總計／小計列），執行 `assert len(df_detail) + len(df_other) + len(df_subtotal) == len(df_raw)`，100% 杜絕合計列混入排行榜或 KPI 重複加總（Double Counting）。
2. **指標極性同質化轉化（Homogeneous Metric Polarity）**：
   - 當同一個視覺序列或排行榜同時包含正向指標（如「完成率」）與反向阻礙指標（如「卡關率」）時，必須先依 `正向率 = 100% - 反向率` 轉化為同質極性，並在 Tooltip 或標註膠囊中補充原始反向原因，避免高低方向語義錯亂。
3. **零旋轉清晰標籤與雙層/左對齊結構（Zero-Tilt Readable Labels）**：
   - 座標軸之中文類別或階段標籤**嚴禁傾斜 45° 或 90°**。若 X 軸項目較多或名稱較長，應採用雙層水平對齊短籤（`【四字定位】` + 短句說明），或自動轉為橫向排行圖（`yAxis: { type: 'category', inverse: true }`）讓中文標籤水平左對齊/右對齊清晰呈現。
4. **去邊框極簡座標軸與直接數據回饋（Despined Axes & Direct Data Feedback）**：
   - 隱藏不必要的外框線（Python 端直接調用 `hcl_color_engine.despine_axes(ax)` 移除頂部與右側軸線，並以 `dpi=300` 輸出），背景網格線設為極淡虛線或細線（`#F1F5F9` 或 `#CBD5E1`）。
   - 互動式圖表必須配置高可讀性之自訂 `tooltip`（色塊圖示、等寬字體對齊之精確數值與單位、自動加總或佔比提示）；單序列排行或發散圖應直接於長條末端顯示數值標籤。
5. **75-20-5 畫布呼吸、微軟正黑體零 Emoji 防護與精簡官方資料來源聲明**：
   - 儀表板整體背景採 75% 中性結構底色（畫布 `#F8FAFC`、卡片純白 `#FFFFFF`、邊框 `#E2E8F0`、主文字 `#0F172A` / `#1E293B`、次要文字 `#475569` / `#64748B`），將色彩聚光燈留給數據圖形本身；頁首／頁尾標註原始官方發布機關與資料集名稱，並附加說明 **1. 官方資料集網址、2. 資料涵蓋期間**（嚴禁將《資料說明書》寫成資料來源）。
   - 若同步生成 `matplotlib` 靜態儀表板圖（`.png`），嚴格執行**零 Emoji 鐵律**（僅用 `▲`、`●`、`■`、`★`），杜絕缺字方框（Tofu Box `□`）。


---

## 四、 零後端自包含前端架構、獨立 Git 綁定與網站部署規範（Self-Contained Engineering, Git Binding & Web Deployment）

### 1. 雙擊即開且相容子路徑部署之 Git-Ready 檔案結構（Zero-Backend & Git-Ready Package Structure）
每個生成的互動式 Web 數據儀表板，預設皆視為**「準備綁定獨立 Git 儲存庫並發布為線上網站（如 GitHub Pages / GitLab Pages / Vercel / Netlify）」**的標準靜態網站專案，必須一次生成以下完整模組化結構：
- `index.html`：響應式語義化佈局（頂部標題與資料來源聲明、動態維度控制列、KPI 摘要卡片區、主視覺化圖表區、底部搜尋明細表與 CSV 匯出按鈕）。
  - **【純相對路徑鐵律（Strict `./` Relative Paths）】**：`index.html`、`css/style.css` 與 `js/dashboard.js` 內部引用任何本地資源時，**必須一律使用明確的 `./` 相對路徑**（如 `./css/style.css`、`./js/gephi_palette.js`、`./js/dashboard.js`、`./data/<dataset>_data.js`、`fetch('./data/<dataset>_data.json')`），**嚴禁使用以 `/` 開頭的根目錄絕對路徑**（如 `/css/style.css`），確保同時 100% 相容於：(1) 檔案總管 `file://` 直接雙擊開啟、(2) 獨立網域根目錄，以及 (3) GitHub Pages 子路徑網站（`https://<username>.github.io/<repo-name>/`）而絕不發生 404 破圖或腳本載入失敗！
  - **【禁用執行期 `cdn.tailwindcss.com` 鐵律（Zero Runtime Tailwind CDN）】**：**嚴禁依賴 `<script src="https://cdn.tailwindcss.com"></script>`**（不僅產生 Console 生產環境警告，更會導致離線環境版面崩潰）！所有網格、卡片、按鈕、表格與響應式排版樣式必須完整編寫於本地 `./css/style.css` 中。
- `css/style.css`：於 `:root` 集中定義鎖定版配色設定集之所有 CSS 變數（`--color-cat-1: #ECA072`、`--tint-cat-1: #FFF3EA` 等）與完整自包含 UI 樣式，確保零外部 CSS 框架依賴。
- `js/gephi_palette.js` ＋ `js/dashboard.js`：由 `hcl_color_engine.export_gephi_palette_js("./js/gephi_palette.js")` 匯出權威 CIELAB 色彩引擎，`dashboard.js` 直接調用 `window.GephiPalette` 完成全域固定類別色碼映射、`(v - min)/(max - min)` 循序插值與 9 階對稱發散取色，並監聽 `window.addEventListener('resize', ...)` 自動自適應縮放。
- `data/<dataset>_data.js` ＋ `data/<dataset>_data.json`：**【離線雙載入防 CORS 鐵律】** 為了讓使用者在檔案總管直接雙擊 `index.html`（`file://` 協定）時不會因瀏覽器阻擋 `fetch('*.json')` 而白屏，必須同時將結構化資料輸出為 `data/<dataset>_data.js`（內含 `window.DASHBOARD_DATA = ...` 並於 `index.html` 以 `<script src="./data/<dataset>_data.js">` 引入）與標準 `.json` 檔！
- `.nojekyll`：於儀表板專案根目錄建立空白 `.nojekyll` 檔，防止 GitHub Pages 啟動 Jekyll 編譯器而忽略底線開頭檔案或拖慢部署速度。
- `.gitignore`：預先建立標準忽略清單（排除 `.DS_Store`、`Thumbs.db`、`*.log`、`.vscode/`、`.idea/`、`__pycache__/`、`node_modules/` 等），讓該目錄隨時可直接執行 `git init` 獨立版控。
- `README.md`：**【網站專案與 Git 部署指南】** 每個儀表板必須自動生成專屬 `README.md`，內容須包含：(1) 儀表板核心特色與視角說明、(2) 專案檔案結構樹（含 `.nojekyll` 與 `.gitignore`）、(3) 本機雙擊與 HTTP Server 預覽方式、(4) **一鍵綁定獨立 Git 儲存庫並發布至 GitHub Pages（含 `gh` CLI 自動建庫、`main` 或 `gh-pages` 分支推送、防外層倉庫嵌套 `.git` 清理指令與 `git subtree` 方案）**、(5) 鎖定版 CIELAB 配色速查表與資料來源聲明。


### 2. 強制視覺驗收與交付清理（Mandatory Visual Inspection Gate）
- 若包含靜態全景儀表板圖（`.png`），生成後必須透過 `view_file` 實際檢視渲染成品，確認無文字重疊、無穿線、無溢界、圖例與標題對齊完美。
- 若為互動式 Web 儀表板，必須確認所有篩選控制項、視角切換、Tooltip 單位顯示與 CSV 匯出（含 `\uFEFF` UTF-8 BOM 防 Excel 中文亂碼）運作正常，並清除任何臨時測試腳本或廢棄預覽檔。

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

