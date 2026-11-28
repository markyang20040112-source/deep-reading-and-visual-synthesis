# Format E 內容細節規劃（數據儀表板呈現架構、內部圖表與部署選型大腦）

> **單一職責定位（Single Responsibility）**：本檔為 **Format E（零後端互動式 Web 數據儀表板 ＋ 選配靜態全景圖 `.png`）** 分枝的內容細節決策大腦，**僅當主幹 [`../../shared/router.md`](../../shared/router.md) 確定勾選 Format E 時按需開啟**。專責診斷「呈現模式 A / B / C（嚴禁寫死固定四圖頁籤）」、「內部圖表選型與 `02_color_registry.json` 連動」、「模式 2 / 3 前端組件與本分枝局部覆寫」及「雲端部署偏好」，拍板後寫入 `02_phase2_generation_blueprint.md` 之 **`## Format E 分枝藍圖`**，交由 [`02_build.md`](./02_build.md) ＋ [`03_qa.md`](./03_qa.md) 執行。

---

## 一、 第一步：動態呈現架構診斷（Zero Hardcoded Layouts — Modes A / B / C）

遵循 **Shneiderman (1996) 視覺資訊尋求箴言（*"Overview first, zoom and filter, then details-on-demand"*）**，依資料維度與決策任務選擇最適呈現拓撲（**嚴禁機械套用固定四圖或固定版型**）：

| 呈現模式 | 適用情境 | 核心組件配置 |
| :--- | :--- | :--- |
| **模式 A：多視角切換互動工作台**<br>*(Multi-Perspective Workbench)* | 資料含多個觀察切面（結構組成、跨實體排行、期比增減、分配密度或多指標切換） | 頂部全局維度篩選列 $\rightarrow$ 3～4 張 KPI 摘要卡 $\rightarrow$ 動態生成之 $N$ 個互動視角頁籤 $\rightarrow$ 可搜尋、排序並匯出 CSV（含 `\uFEFF` BOM）之明細表 |
| **模式 B：多面板全景聯動網格**<br>*(Synchronized Bento Grid)* | 需於單一畫面同屏比對「全局結構 × 關鍵排行 × 變化趨勢／落差診斷」供主管決策 | 不對稱 Bento 網格（寬主視覺面板 `55%～60%` ＋ 右側上下堆疊互補副面板），跨面板嚴格鎖定同實體色彩 |
| **模式 C：雙模態協同交付**<br>*(Web Dashboard + Static Overview PNG)* | 同時需要可離線雙擊／雲端部署的互動網頁，以及可印刷／附檔分享之全景高解析圖 | 完整零後端 Deploy-Ready 互動網頁專案 ＋ 1 張 `24" × 14"`, `300 DPI` `GridSpec` 出版級靜態全景儀表板圖（`.png`） |

---

## 二、 第二步：內部圖表選型、資料消歧與色彩鎖定連動

1. **內部圖表動態選型**：直接依 **[`../format_d_charts/01_plan.md`](../format_d_charts/01_plan.md)** 之「4D 資料快篩 × 8 大溝通意圖 30+ 圖表決策樹」與 `T25` 實證準則選配儀表板內部圖表，並對照 [`../format_d_charts/02_build_core.md`](../format_d_charts/02_build_core.md) 及對應 1～2 個 `families/*.md`。
2. **純明細與 `df_other` 消歧**：確認純明細 `df_detail` 真實 `Min/Max`、合法缺失值 `#D9D9D9`、以及「4+1 智慧聚焦 vs. 原表 `df_other`」消歧選項（選項 1 純明細聚焦＋註腳揭露 vs. 選項 2 長尾透明整併）。
3. **跨圖鎖色連動**：若同專案亦含 Format D，確認先完成 Format D 並沿用工作階段根目錄之 `02_color_registry.json`，於建構 Format E 時透過 `export_gephi_palette_js()` 將 `entityColors` 與 `entityAliases` 同步匯出至前端 `js/gephi_palette.js`。

---

## 三、 第三步：本分枝混合式局部覆寫與雲端部署規劃

向使用者提出 **Format E 分枝提案** 時，同步確認以下三項：
1. **分枝風格覆寫（承襲主幹或局部調整，見 [`../../shared/style_and_color_core.md`](../../shared/style_and_color_core.md)）**：
   - 若開啟 **模式 2 (`editorial_narrative`)**：頂部 KPI 卡內嵌「與基準線正負差距膠囊（`Δ vs. 全國均值`）」，圖表工具列配置「基準線切換器（未加權平均／官方加權／中位數）」與「首尾極值聚光燈開關」。
   - 若開啟 **模式 3 (`bespoke_metaphor`)**：透過 `window.GephiPalette.deriveThematicPalette(..., { activate: true })` 注入主題語義色階，並選配容器液面進度條或 $10 \times 10$ 象形陣列卡。
   - 筆風檔（`Slot 6 & 8`）與 `chart_palette`（預設承襲主幹，可單獨指定）。
2. **雲端直推部署目標預告（`config/user_preferences.json` 之 `web_deploy.provider`）**：
   - 確認驗收完畢後要部署至單一平台（`netlify` / `cloudflare_pages` / `github_pages_fallback`）或先保留本機 Deploy-Ready 封裝（`none`）；若含機密或未公開數據，提前標記公開網址資料曝光風險。

**⏸️ 暫停關卡**：等待使用者確認 Format E 呈現模式（A / B / C）、內部圖表組合、`df_other` 消歧、分枝覆寫與部署偏好後，立即寫入 `02_phase2_generation_blueprint.md` 之 **`## Format E 分枝藍圖`**；輪到 Format E 執行時，依 [`02_build.md`](./02_build.md) 建構並依 [`03_qa.md`](./03_qa.md) 驗收！
