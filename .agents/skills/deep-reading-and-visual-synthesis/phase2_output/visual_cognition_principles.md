# 視覺認知與設計規範（Visual Cognition & Design Principles）

> **單一職責定位（Single Responsibility）**：本檔為 Phase 2 **五大產出格式（Format A 知識圖譜、Format B 決策報告、Format C 簡報、Format D 量化圖表、Format E 數據儀表板）唯一共用的視覺認知底層規範**。凡屬跨格式通用的組塊階層、白話由淺入深表達、色彩配置與字體下限，統一於本檔定義；各專項規格檔（`*_spec.md`）僅規範該媒體專屬的幾何排版與渲染技術，不重複贅述本檔原則。

---

## 一、 單一畫布階層組塊、平行對齊與多畫布無損擴展法則（Per-Canvas $4 \to 2 \to 3$ Chunking & Zero-Loss Expansion）

- **理論依據**：**工作記憶容量極限（Working Memory Capacity $4 \pm 1$, Cowan 2001）**、**格式塔共同區域原則（Law of Common Region, Palmer 1992）** 與 **組塊理論（Chunking, Miller 1956）**。
- **跨格式設計標準**：
  1. **單一視覺畫面 $4 \to 2 \to 3$ 階層組塊結構**：任何**單一視覺畫面**（單張圖譜、單頁簡報、報告單一模組或儀表板頂欄）的頂層宏觀容器（Macro Zones / KPI 頂欄）嚴格控制在 **$3 \sim 4$ 個**（單張畫布絕不超過 4 個）；每個宏觀容器內收納 **$2 \sim 3$ 張子卡片（Cards）**；每張子卡片內收納 **$2 \sim 3$ 條核心論點（Bullets）**。
  2. **無損分流擴展鐵律 vs. Medium 單一故事線收斂特例**：
     - **一般文獻／深度報告／簡報模式（以「拆圖、擴章、加頁」取代刪減內容）**：Phase 1 Step 5 收斂出的「核心論證主幹分支」與「批判延伸／跨域遷移分支」不論總數多少（如 $5 \sim 8+$ 個分支），**嚴禁為了塞進單張 $4$ 區畫布而刪減任何細節或批判性議題**！當總分支數 $> 4$ 時，Phase 2 強制啟動多畫布／多章節擴展（Format A 自動拆分為 `01` 主幹圖、`02` 機制深挖圖、`03+` 批判延伸與跨域遷移專題圖；Format B 動態擴增章節 `壹～柒...`；Format C 動態加頁；Format D/E 增加面板或互動視角）。
     - **Medium 每週一圖／輕量數據敘事專欄模式（Single-Hook Convergence）**：針對公開數據新聞與課堂「每週一圖」作業，聚焦**單一核心數據故事主軸**，僅產出 **1～2 張各自獨立之單面板（Single-Panel）`300 DPI` `.png` 統計圖（禁止 `ncols=2` 橫向並排子圖）** ＋ **正文 `<= 1,600` 字之 Medium 原生 Markdown 專欄（免除編譯 A4 PDF）**。
  3. **同類維度水平平行對齊（Parallel Row Alignment）**：當呈現並列的維度、階段或方案時，各卡片內部的條目必須按相同屬性（如：`第 1 列：淺層直覺/現象`、`第 2 列：中層案例/機制`、`第 3 列：深層價值/行動`）嚴格水平對齊，支援視線橫向掃描比對。
  4. **留白呼吸比（Whitespace Ratio）**：資訊圖譜、量化圖表與數據儀表板留白 $\ge 25\%$，簡報投影片留白 $\ge 35\%$，PDF 報告透過頁邊距與段落間距維持視覺呼吸感。

---

## 二、 「白話直覺先行、由淺入深」漸進式揭露法則（Plain-First & Shallow-to-Deep Progression）

- **理論依據**：**具象漸退理論（Concreteness Fading, Goldstone & Sloutsky 2005; Fyfe et al. 2014）** 與 **多媒體個人化原則（Personalization Principle, Mayer 2009）**。生硬的學術或工程黑話會瞬間耗盡外在認知負荷，必須先建立日常直覺錨點，再引入專有名詞。
- **跨格式三階漸進結構（`淺 → 中 → 深`）**：
  1. **第一階（淺層：白話直覺與痛點現象）**：條目開頭的 `● 【粗體視覺錨點】` 必須使用直覺白話或生活化動詞（例如：`● 【各部門字典打架】`、`● 【整理完就過期】`），禁止直接堆砌未解釋的複合術語。
  2. **第二階（中層：具體情境與機制拆解）**：用一句具體的業務場景說明運作方式（例如：「業務與財務對同一指標各算各的，AI 抓到兩份報表只能瞎猜」），再以括號附註精準專有名詞（如 `Ontology / MDM`），讓術語自然退居輔助定位。
  3. **第三階（深層：決策價值與落地法則）**：底層條目或卡片總結收斂出可執行的工程/管理決策與長期商業護城河。

---

## 三、 跨格式字級、行寬與漢字換行規範（Typography, Line Measure & CJK Wrapping）

- **理論依據**：**大字級與長行寬閱讀效率研究（Dyson 2004; Tinker 1963）** 與 **前注意特徵處理（Preattentive Processing, Ware 2020）**。過小的字級或過度壓縮的短行寬會強迫眼球頻繁折返（Saccadic Eye Movements），大幅拉高閱讀疲勞。
- **字體優先序**：統一使用無襯線正黑體（`Microsoft JhengHei`、`PingFang TC`、`Noto Sans CJK TC`；Format B 另支援大專院校傳統中文標楷體 `DFKai-SB` 模式），嚴格建立 **3 階字重對比**（標題 Bold $\ge 1.35\times$ 內文 Regular）。
- **五大產出格式字級與行寬權威基準表（與各 `*_spec.md` 100% 同步）**：

| 產出格式 | 畫布 / 頁面基準 | 主標題 / 斷言字級 | 區塊 / 卡片標題 | 內文 / 條目字級 | 膠囊標籤 / 橫幅 / 註腳 | 單行最佳漢字寬度 / 幾何配置 |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Format A：知識圖譜** | `28" × 18.5"` (`240 DPI`) | `23.5pt` | `14.6~15.0pt`<br>*(分區 `13.6pt`)* | **`11.8~12.5pt`** | **`10.2~10.8pt`**<br>*(底橫幅 `12.4~14.4pt`)* | **`32~36 漢字/行`**（每點 `60~66 字` 折 2 滿行，填滿卡片 `88%~92%`） |
| **Format B：決策報告 & Medium 專欄** | `A4`（印域寬 `189mm`，支援橫向圖表專頁）或 **Medium 原生 `.md`** | `20~24pt`<br>*(Medium `#`)* | `12.0~15.0pt`<br>*(Medium `###`)* | **正文 `p`：`10.6~11.2pt`**<br>*(學術個案可微調 `9.2~10.5pt`)*<br>**表格/卡片 (`td`/`.card-body`)：`9.0~10.5pt`**<br>**文體 5 Medium：正文 `<=1,600` 字（免 PDF）** | **`8.8~9.8pt`**<br>*(Medium 文末 `---` 參考資料來源不計入 1,600 字)* | **`38~44 漢字`**（正文行高 `1.62~1.75`；文體 5 禁用自訂 HTML/表格，每段 3～4 行適配手機閱讀） |
| **Format C：簡報投影片** | `16:9`（`13.333" × 7.5"`） | **Zone 1 斷言：`19.5~22pt`**<br>*(S0 首尾頁：`26~32pt`)* | `14.5~16.0pt` | **雙欄卡 (`S1`)：`13.0~14.5pt`**<br>**三/四欄卡 (`S2`/`S3`/`S7`)：`11.5~12.5pt`** | **左上章節膠囊：`9.5pt`**<br>**Zone 3 底部橫幅：`12.5~14.0pt`** | **雙欄：`22~26 漢字/行`**；**三/四欄：`16~19 漢字/行`**（每列槽 $\le 45$ 漢字，垂直置中） |
| **Format D：量化圖表** | 依面板數動態縮放 (`300 DPI`)<br>*(Medium 模式限 1～2 張獨立單面板，禁 `ncols=2`)* | `16~20pt` | `12.5~13.5pt` | **`10.5~12.0pt`** | **`9.5~10.5pt`**<br>*(含精簡官方來源圖註：1.官方資料集網址、2.資料涵蓋期間)* | 數據標籤直接標註於幾何圖形末端，X 軸雙層 `0°` 水平定位籤；Medium 雙圖採橘破題 $\rightarrow$ 藍深挖跨檔接力 |
| **Format E：數據儀表板** | 響應式 Web / `24"×14"` (`300 DPI`) 靜態圖 | `20~24px` (`pt`) | `14~16px` (`pt`) | **`12~14px`** (`10~12pt`) | **`11~12px`** (`9.5pt`) | 頂欄 3～4 張 KPI 卡 + 動態多視角畫布 + 明細表 |

- **漢字避頭尾標點保護（Kinsoku Shori）**：所有基於座標繪圖的渲染引擎（`matplotlib`）在強制折行後，必須先剝離續行前導全形/半形縮排（`\u3000 `），檢查次行首字是否為禁則標點（`，、。；：！？）》」】』％`）或前一行末字是否為開括號（`（《「【『`），將違規字元回推或下移後再重新掛回縮排。

---

## 四、 75-20-5 認知色彩分配與鎖定版圖表色票連動法則（Cognitive Color & Locked Chart Palette）

- **理論依據**：**數據墨水比（Data-Ink Ratio, Tufte 1983）**、**Brewer 色階分類理論（Sequential vs. Qualitative Palettes, Brewer 1994）**、**面積補償色度定律（CIELUV HCL Area-Chroma Scaling, Zeileis et al. 2009）** 與 **WCAG 2.1 AA 對比度標準（$\ge 4.5:1$）**。
- **75-20-5 畫面色彩預算**：
  - **75% 中性結構底色（Neutral Canvas & Ink）**：畫布底色（`#F8FAFC`）、卡片純白底（`#FFFFFF`）、內文深石板灰（`#0F172A` / `#1E293B`）與次要灰字（`#475569`），絕不使用刺眼純黑（`#000000`）。
  - **20% 語義家族色（Semantic Families）**：同一張圖譜或投影片最多動用 **2～3 種色相（Hue）**。大面積容器填充必須將色度壓低至 $C \le 12, L \ge 95$（極淡柔光底色），外框與標題則採用高飽和同色系（$C \in [48, 65], L \in [40, 50]$）。
  - **5% 焦點強調色（Focal Callout）**：高飽和琥珀橘或珊瑚紅，**全圖僅限用於 1～2 個最關鍵的破局轉折或核心異常值**。
- **量化圖表（Format D）與數據儀表板（Format E）之「鎖定版配色設定集」雙向連動鐵律**：
  - 凡繪製 **Format D（[`quantitative_chart_spec.md`](quantitative_chart_spec.md)）** 與 **Format E（[`data_dashboard_spec.md`](data_dashboard_spec.md)）** 之統計圖表，**嚴格鎖定採用[個人圖表配色規範檔（`ggsci` `Gephi · pastel` CIELAB/HCL $L^* \approx 72$ 均衡版）](https://docs.google.com/document/d/1puNpLGR7hYcyvZL1DZMdUpmP9fXM-TQcxu1N6QyGb1E/edit?usp=sharing)**（權威完整色階表單一收納於 [`quantitative_chart_spec.md`](quantitative_chart_spec.md) 第三節；Python 端直接調用 [`scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)，Web JS 端直接調用 [`scripts/gephi_palette.js`](../scripts/gephi_palette.js)）：
    1. **無序類別固定四色序與零 Alpha 徽章淺底色**：`1. 暖杏蜜橘 #ECA072`（淺底 `#FFF3EA`）$\rightarrow$ `2. 霧靄青藍 #5DBACD`（淺底 `#EBF7F9`）$\rightarrow$ `3. 落櫻粉黛 #E89BB6`（淺底 `#FFF0F5`）$\rightarrow$ `4. 鼠尾草綠 #8FBA88`（淺底 `#F1F7EE`）；跨圖表與跨視角同名類別嚴格綁定同色；超過 4 類時向使用者確認擴充方式或採 `4+1` 聚焦收斂至 `#CBD5E1`；缺失值標記為 `#D9D9D9`。
    2. **同質連續五階循序色階**：預設採用**主色暖杏橘系循序（`#FFF3EA` $\rightarrow$ `#97481B`）**，對比雙指標或次視角採用**次色霧靄藍系循序（`#EBF7F9` $\rightarrow$ `#0E5B6B`）**，於 CIELAB 空間依 $p = (v - v_{\min}) / (v_{\max} - v_{\min})$ 分段線性插值，**嚴禁使用 Alpha 透明度（如 `rgba(...)` 或 `#RRGGBB20`）冒充深淺明度或徽章底色**。
    3. **九階對稱發散色階**：以業務中立基準（`0%` 或 `100%`）對應中心冷灰 **`#F5F6F7`**，負向端延伸至深墨青 **`#0E5B6B`**，正向端延伸至深栗橘 **`#884725`**。
    4. **雙向同步更新義務**：往後 Format D 與 Format E 在共通配色或圖表設計規則上有任何修改，必須同步更新 [`quantitative_chart_spec.md`](quantitative_chart_spec.md)、[`data_dashboard_spec.md`](data_dashboard_spec.md)、[`scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py) 與 [`scripts/gephi_palette.js`](../scripts/gephi_palette.js)。


