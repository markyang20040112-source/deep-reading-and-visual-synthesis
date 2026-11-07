# 量化實證圖表設計與出版級繪製規範（Format D: Quantitative Chart Spec）

> **單一職責定位（Single Responsibility）**：本檔專責 **Format D（量化實證數據圖表 `.png`）** 的空間座標映射、折線／柱線複合差距表現、**鎖定版個人圖表配色規範（`Gephi · pastel` CIELAB / HCL 均衡色系）**、同質單色相漸層與跨面板色相區隔、指標語意同質化轉化，以及 `matplotlib` 出版級精準繪製規範。跨格式共用的組塊階層與白話由淺入深原則請見 [`visual_cognition_principles.md`](visual_cognition_principles.md)。
>
> 🔗 **【Format D（量化圖表）⇄ Format E（數據儀表板）雙向連動與同步更新鐵律】**：
> 本檔（[`quantitative_chart_spec.md`](quantitative_chart_spec.md)）與 **[`data_dashboard_spec.md`](data_dashboard_spec.md)（Format E：數據儀表板規範）** 及 **[`scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)** 共用完全相同的「鎖定配色設定集」與「圖表視覺設計規則（座標映射、極性同質化、色階分流、去框座標軸、標籤對齊與製圖前確認條件）」。**往後凡涉及圖表配色或共通設計規則之任何新增、修改或技能進化（Step E3），必須強制同步更新本檔、`data_dashboard_spec.md` 與 `scripts/hcl_color_engine.py`，嚴禁單邊改動導致規則脫節！**

---

## 一、 空間重力座標映射與折線差距表現法則（Spatial Gravity XY-Mapping & Trajectory Line Chart）

### 1. XY 軸空間重力對調法則（Horizontal Progression on X-Axis + Vertical Magnitude on Y-Axis）
- **理論依據**：**空間重力與閱讀動線隱喻（Spatial Gravity & Reading Trajectory Metaphor, Tversky 2011）** 與 **圖形感知精準度階層（Cleveland & McGill 1984）**。人類大腦天生將「高低起伏（強／弱、高昂／崩跌）」映射於**垂直高度（Y 軸）**，並將「階段推進、漏斗篩選或成熟度演進」映射於**由左至右的水平動線（X 軸）**。
- **強制對調規範**：
  - 當數據旨在展現**「跨階段留存率遞減、預期與現實的斷崖崩跌（Cliff Drop）、或由淺入深的成熟度結構分佈」**時，**嚴禁使用水平長條圖（`barh`）將階段上下堆疊於 Y 軸**！
  - 必須將 **X 軸設為由左至右的推進階段**，並將 **Y 軸設為 `0% ~ 100%` 的垂直高度**，使左上角的高預期（如 `80%`）一路向右下角的低投產（如 `6%`）俯衝，創造直覺且震撼的**物理斷崖崩跌感（Physical Cliff Drop）**。

### 2. 跨階段遞減 vs. 同案雙維反差之圖表選型分流（Trajectory Line vs. Paired Dual-Bar with Gap Callout）
依數據的核心比較任務（Cleveland & McGill 1984），嚴格區分以下兩種差距表現型態：

- **【型態 A：跨階段單序列遞減】折線軌跡為主、直柱與落差帶為輔之複合圖（Combo Column + Drop Line Trajectory）**：
  - **適用場景**：衡量單一指標跨多個階段的留存遞減或漏斗流失（如 `80% → 62% → 54% → ... → 6%`）。
  - **核心結構**：
    1. **主視覺折線（Primary Drop Trajectory Line）**：以粗實線（`linewidth=3.2`）搭配醒目實心圓點（`marker='o'`, `markersize=9~11`, 白邊環繞）串聯各階段數據頂點，直接刻劃出陡峭的滑落斜率。
    2. **輔助漸層直柱（Supporting Vertical Bars）**：於折線下方繪製寬度適中（`width=0.52`）的垂直長條，填滿由頂點至 `Y=0` 的基準高度，強化實體量感。
    3. **斷崖落差標註帶（Explicit Cliff / Gap Callout Zone）**：在起點高峰與終點低谷之間，繪製水平基準虛線與垂直雙向箭頭／陰影區間，直接標註總落差（如 `Δ = -74% 預期與投產巨大斷崖`）及關鍵轉折流失率。

- **【型態 B：同案例雙維反差】配對雙柱＋剪刀差落差標註圖（Paired Dual-Bar & Explicit Gap Callout Chart）**：
  - **適用場景**：當數據旨在對比**每一個獨立案例內部的兩個對立指標**（例如同一組織之「表象預測信心 88%～95% vs. 實際模型效用 12%～32%」或「事前預期 vs. 事後真實表現」）時，**嚴禁使用單一序列折線圖**（單一折線無法呈現同案內的高低雙維落差）。
  - **核心結構**：
    1. **共同基準線並排雙柱（Common-Baseline Paired Bars）**：於每個 X 軸案例位置並排繪製左柱（`x - width/2`，代表第一指標／基準預期，採鎖定色序 1 **主色暖杏蜜橘 `#ECA072`** 或其深階 `#CA6F35`）與右柱（`x + width/2`，代表第二對比指標／實際結果，採鎖定色序 2 **次色霧靄青藍 `#5DBACD`** 或其深階 `#2C8B9F`），讓同一案例的高低反差同屏立見。
    2. **顯式剪刀差垂直雙向箭頭與落差膠囊（Explicit Delta Callout）**：於左柱頂端延伸水平虛線至右柱上方，並在右柱頂端與左柱頂端高度之間繪製**垂直雙向箭頭（`<->`）與醒目差值膠囊（`Δ = -XX%`）**，將讀者的「視覺心算減法負荷」轉化為零阻力的直接讀取。

---

## 二、 指標語意同質化轉化與底部雙層零旋轉標籤（Homogeneous Polarity & Two-Tier 0° X-Axis Labels）

### 1. 指標極性 100% 同質化轉化（Homogeneous Metric Polarity Conversion）
- **核心痛點防範**：調查報告常同時混雜「正向準備度指標（如 `80% 看好`、`62% 增資`、`37% 具基礎`、`6% 投產`）」與「反向阻礙指標（如 `46% 視數據品質不良為死穴`、`57% 至今未修改數據策略`）」。若未經轉化直接畫在同一張圖上，會導致「高數值有時代表好、有時代表壞」的嚴重認知錯亂！
- **強制同質化轉換公式**：
  - 繪製同一條折線或同一組 X 軸序列前，必須將所有數據點統一轉化為 **100% 同質的正向留存／過關率**（或全部統一為反向障礙率）：
    $$\text{正向過關／行動率} = 100\% - \text{反向卡關／未行動率}$$
  - **實務範例**：將「`46%` 視數據品質不良為死穴」轉化為 **`54%`【品質過關】（未受困於基礎品質死穴）**；將「`57%` 未修改數據策略」轉化為 **`43%`【策略行動】（已實質翻修數據策略）**。如此一來，X 軸由左至右形成 **`80% → 62% → 54% → 43% → 37% → 11% → 6%`** 邏輯完全同質、單調遞減的留存斷崖！同時於折線轉折處以醒目膠囊標註反向流失原因（如 `▲ 46% 卡於品質不良`、`▲ 57% 策略原地踏步`），兼顧原意與同質性。

### 2. 底部 X 軸雙層水平對齊標籤（Two-Tier Zero-Tilt Aligned Label Blocks）
- **零旋轉鐵律**：X 軸中文標籤**絕對禁止傾斜 45° 或 90°**，亦禁止長短不一的散亂句子。
- **雙層對齊結構（Two-Tier Centered Structure）**：
  - **第一層（Tier 1 — 四字粗體定位籤）**：統一採用 `【四字定位】` 格式（如 `【商業預期】`、`【預算投入】`、`【品質過關】`、`【策略行動】`、`【基礎信心】`、`【高度完備】`、`【核心投產】`），字級 `10.5~11pt Bold`，**所有定位籤必須 100% 水平對齊於同一 Y 座標基準線**。
  - **第二層（Tier 2 — 雙行平行短句說明）**：緊接於定位籤正下方，以兩行工整對稱的短句（每行嚴控 `6～7 個漢字`，字級 `9~9.5pt`）說明該指標之具體同質定義，讓讀者在極低眼動負擔下瞬間掃視比較。

---

## 三、 鎖定版圖表配色設定集與跨圖色階連動規範（Locked Color Specification — Format D & Format E 唯一權威 SSOT）

> **權威設定集來源**：[我的圖表配色設定（Google Doc 權威規範檔）](https://docs.google.com/document/d/1puNpLGR7hYcyvZL1DZMdUpmP9fXM-TQcxu1N6QyGb1E/edit?usp=sharing)
> **理論與衍生說明**：源自 `ggsci` 之 `Gephi · pastel`（[scale_gephi](https://nanx.me/ggsci/reference/scale_gephi.html)），以原色盤四個基礎類別色系為靈感，在色彩感知空間（CIELAB / HCL）中進行明度（Lightness $L^* \approx 72$）與彩度（Chroma）均衡校正，提升白底圖表清晰度；循序色階採物理感知等差階梯計算生成，發散色階保持雙向視覺重量對稱。
> **單一事實來源（SSOT）**：本節為 Format D 與 Format E **唯一完整色票表格定義處**；Python 實作強制匯入 [`scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)，Web 前端 JS 強制載入 [`scripts/gephi_palette.js`](../scripts/gephi_palette.js)。

### 1. 無序類別固定色序與零 Alpha 徽章淺底色（Qualitative Fixed Color Order & Zero-Alpha Badge Tints）
當資料為無序類別（Qualitative）時，依下列固定順序綁定類別（對應 `GEPHI_QUALITATIVE_HEX`、`GEPHI_LIGHT_BADGE_TINTS` 與 `bind_qualitative_colors()`），**同名類別在跨圖表、跨面板或互動篩選／排序切換時必須保持完全相同的色碼，絕不得隨機指派或因資料順序變動而換色**：

| 色序順位 | 角色定位 | 顏色描述 | 鎖定 HEX 色碼 | 零 Alpha 徽章/表格淺底色 (`0.00` 節點) | 跨圖表／跨視角綁定規範 |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **主色** | 暖杏蜜橘 | **`#ECA072`** | **`#FFF3EA`** | 第一主類別、預設單指標主視覺 |
| **2** | **次色** | 霧靄青藍 | **`#5DBACD`** | **`#EBF7F9`** | 第二類別、雙指標對比之第二維度 |
| **3** | **第三色** | 落櫻粉黛 | **`#E89BB6`** | **`#FFF0F5`** | 第三類別 |
| **4** | **第四色** | 鼠尾草綠 | **`#8FBA88`** | **`#F1F7EE`** | 第四類別 |
| *(擴充/收斂)* | **長尾聚合 / 缺失值** | 典雅淺灰 / 中性灰 | **`#CBD5E1`** / **`#D9D9D9`** | **`#F1F5F9`** | 絕不自行發明新色或隨機補色；若類別數 $> 4$，必先向使用者確認擴充方式（如切換為單一循序色階之橫向排行圖），或採「**智慧 4+1 聚焦聚合**」將前四大綁定四色、長尾歸入 `#CBD5E1`（**嚴禁將 5 階循序色階拿去模除循環 `idx % 5` 塗抹 30 個無序類別**！）；缺失值（NA/Null）統一標記為 `#D9D9D9`。 |

- **【原表 `df_other`（「其他」列）vs. `Gephi · pastel` `4+1` 長尾灰柱（`#CBD5E1`）之雙重語義消歧鐵律】**：
  - **嚴禁讓原表自帶的 `其他`／`未分類` 列（`df_other`）混入前四大彩色主色柱（`#ECA072`, `#5DBACD`, `#E89BB6`, `#8FBA88`），也嚴禁在同一張圖上產生兩個都叫「其他」的柱子！**
  - 當純明細 `df_detail` 類別數 $>4$ 且原表存在 `df_other` 時，必須依第一階段與使用者拍板之選項執行二擇一：
    1. **選項 1（純明細聚焦 ＋ 圖註揭露原表其他項）**：圖表僅繪製 `df_detail` 的 Top 4（彩色）＋ 第五類「其餘明細項目合計（`#CBD5E1`）」，並於圖表底註載明*「註：不含原表未細分之『其他』項（計 XX 筆 / 占 X%）」*。
    2. **選項 2（長尾透明整併）**：將「第 5 名後之長尾明細」與「原表 `其他` 列」整併為單一 `#CBD5E1` 灰柱，並透過 `bind_qualitative_colors(..., other_label="其餘明細與原表其他項合計")` 將標籤明確命名為 **`「其餘明細與原表其他項合計」`**。

### 2. 四組五階循序色階（Sequential 5-Node Scales：低值淺 `0.00` $\rightarrow$ 高值深 `1.00`）
用於有序等級（如五級量表、成熟度階段）或同質連續數值圖表（對應 `GEPHI_SEQUENTIAL_SCALES` 與 `get_sequential_color()`）：

| 循序色階系列 | 適用場景 | `0.00` (極淺) | `0.25` (淺) | `0.50` (中/基準) | `0.75` (深) | `1.00` (極深) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **(1) 主色循序（暖杏橘系）** | **預設數值尺度**、主面板／圖 1 同質連續漸層 | `#FFF3EA` | `#FBD8C0` | `#ECA072` | `#CA6F35` | `#97481B` |
| **(2) 次色循序（霧靄藍系）** | **對比雙指標**、雙圖右面板／圖 2 深鑽區隔 | `#EBF7F9` | `#BCE2EB` | `#5DBACD` | `#2C8B9F` | `#0E5B6B` |
| **(3) 第三色循序（落櫻粉系）** | 第三維度數值分布或專題序列 | `#FFF0F5` | `#F9CEE0` | `#E89BB6` | `#C46487` | `#8D3658` |
| **(4) 第四色循序（鼠尾草綠系）** | 第四維度數值分布或專題序列 | `#F1F7EE` | `#D0E5CC` | `#8FBA88` | `#5E8F56` | `#396032` |

- **連續數值平滑插值規則與正規化公式**：
  - 連續變數**必須嚴格依**純明細 `df_detail`** 之正規化位置 $p = (v - v_{\min}) / (v_{\max} - v_{\min})$ 計算**（嚴禁混入合計列 `df_subtotal` 之極值，亦嚴禁直接用 $v / v_{\max}$ 導致最低值無法對應淺端點），並依據上述 5 個等距節點在 **CIELAB / HCL 感知空間中進行分段線性插值（調用 `get_sequential_color()` 或 `lab_interpolate()`）**。
  - **嚴格禁止使用透明度（Alpha channel，如 `rgba(...)` 或 `#ECA07220`）冒充深淺明度或表格膠囊底色**！
- **單圖同質漸層 vs. 雙圖色相區隔與「Medium 模式獨立單面板鐵律」（$1 + 1 > 2$ 敘事接力）**：
  - **單一圖表內部**：衡量同質連續維度時，嚴禁混用多色相彩虹色，預設採用 **(1) 主色循序（暖杏橘系 `#FFF3EA` $\leftrightarrow$ `#97481B`）** 隨數值高低調整明度與彩度。
  - **一般報告／簡報之雙圖橫向並排（`ncols=2`）**：左圖使用 **(1) 主色循序（暖杏橘系）** 呈現宏觀留存斷崖，右圖換用 **(2) 次色循序（霧靄藍系 `#EBF7F9` $\leftrightarrow$ `#0E5B6B`）** 拆解子階段分佈，共用相同 Y 軸比例尺並以跨面板引導標註連通。
  - **【Medium 每週一圖模式專屬：禁止 `ncols=2`，強制拆為 1～2 張獨立單面板（Single-Panel）`.png` 跨檔色彩接力】**：
    - **張數與單面板護欄**：嚴格限制產出 **1 或 2 張** `300 DPI` `.png` 統計圖（如 `01_chart_hook.png`、`02_chart_drilldown.png`）。為適配 Medium 窄欄與手機直向閱讀、並嚴守作業「至少 1 個圖、至多 2 個圖」規定，**在 Medium 模式下禁止使用 `ncols=2` 橫向並排雙子圖**，強制拆為 **1～2 張各自獨立的單面板（Single-Panel）`.png` 圖檔**。
    - **雙圖跨檔色彩敘事接力**：若產出 2 張獨立圖檔，**圖 1（`01_chart_hook.png` 全局現象破題）** 主色調採用 **暖杏蜜橘系（`#ECA072` / `orange` 色階）**；**圖 2（`02_chart_drilldown.png` 結構拆解或交叉深挖）** 主色調切換為 **霧靄青藍系（`#5DBACD` / `blue` 色階，或橘藍配對雙柱）**；缺失值統一標記為 **`#D9D9D9`（`NA / 無資料`）**。

### 3. 九階對稱發散色階（9-Node Symmetric Diverging Scale：中心位置 `0.500`）
適用於具備明確中心基準（如目標達標率 `100%`、年度預算增減偏差 `0%`、全國純明細中位數或滿意度中立點）之資料（對應 `GEPHI_DIVERGING_SCALE` 與 `get_diverging_color()`）。負向端（低於基準／未達標）往霧靄藍系延伸，正向端（高於基準／超標）往暖杏橘系延伸：

| 尺度位置 | `0.000` | `0.125` | `0.250` | `0.375` | **`0.500`** | `0.625` | `0.750` | `0.875` | `1.000` |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **偏離程度** | `-100%` 極端 | `-75%` 中深 | `-50%` 中度 | `-25%` 輕度 | **`0%` 基準中心** | `+25%` 輕度 | `+50%` 中度 | `+75%` 中深 | `+100%` 極端 |
| **語意說明** | 負向極值(深墨青) | 負向中深 | 負向中度 | 負向輕度 | **中立冷灰** | 正向輕度 | 正向中度 | 正向中深 | 正向極值(深栗橘) |
| **HEX 色碼** | **`#0E5B6B`** | **`#257F92`** | **`#5DBACD`** | **`#B2DFE9`** | **`#F5F6F7`** | **`#FBD9C2`** | **`#ECA072`** | **`#B4693A`** | **`#884725`** |

### 4. 製圖前強制確認之 6 大條件（含《資料說明書》全預填直通車）與 5 大套用鐵律
- **製圖時自動從《資料說明書》與 `df_detail` 預填並向使用者確認之 6 項條件**：
  1. **實際變數與類別欄位名稱**（含官方枚舉值對照映射，如 `0=凍結, 1=正常`，禁止重複詢問說明書已載明之定義）。
  2. **數值單位**（如 `mm`, `%`, `億元`, `元/人`, `人` 等）。
  3. **數值尺度之上下限範圍（`Min / Max`）**：**強制使用剔除 `df_subtotal` 後之純明細 `df_detail` 重算真實 `Min / Max`**（並與說明書第 4 章全檔 `Min / Max` 對照展示）。
  4. **發散色階之中心數值**（對應 `#F5F6F7`，預設尋求業務基準值，如 `0`、`100%` 或 `df_detail` 中位數）。
  5. **缺失值（`NA / Null`）**：經兩段式安全轉型識別之合法缺漏筆數，預設統一以中性淺灰 **`#D9D9D9`** 標記。
  6. **超界值與前處理血統狀態**：Clamp 至端點色（`#0E5B6B` / `#884725` 或循序端點）或保留警示標註（若《資料說明書》第 3 章記載該欄位經過離群值截斷 Winsorization、粗粒度分箱 Binning 或遺漏值插補 Imputation，必須於圖註或旁白顯式標明）。
- **五大套用執行鐵律**：
  1. 無論使用 `matplotlib`、`ggplot2`、`ECharts` 或其他繪圖套件，本規範色碼一律同時適用於 `colour`（線條/邊框）與 `fill`（填充）。
  2. 類別資料嚴格按照「固定色序」依序分配，同名類別跨圖表保持完全相同色碼，絕不隨機指派或因排序變動而換色。
  3. 數值圖表預設採用主色循序尺度（暖杏橘系，低值淺、高值深）；若為對比雙指標、次面板或 Medium 圖 2，則使用次色循序（霧靄藍系）。
  4. 發散圖表嚴格以指定中立基準為中心（對應 `#F5F6F7`），兩側採對稱數值跨度映射至藍端與橘端（嚴禁簡化為非黑即白的雙色二元判斷）。
  5. 絕不自行發明新色或隨機補色；若類別數超過 4 個，必須先向使用者確認擴充方式（或啟用 4+1 聚焦聚合與 `df_other` 雙重消歧）。

---

## 四、 黑盒引擎 API 簽名、三層分流防呆內嵌與出版級排版細節（Black-Box Engine API, 3-Way Split Guardrails & Publication Polish）

> [!IMPORTANT]
> **【底層引擎黑盒呼叫鐵律（Black-Box API Rule）】**：所有 Format D 與 Format E 的 Python 繪圖腳本**必須直接 `import hcl_color_engine`** 調用鎖定色票、CIELAB 插值與座標軸去框函數，**嚴禁在腳本中手動硬編碼簡化版二元色或呼叫 `view_file` / `read_file` 讀取 `scripts/hcl_color_engine.py` 原始碼**（除非除錯需要）！

```python
# === scripts/hcl_color_engine.py Black-Box API Signatures ===
from hcl_color_engine import (
    GEPHI_QUALITATIVE_HEX,      # ["#ECA072", "#5DBACD", "#E89BB6", "#8FBA88"]
    GEPHI_LIGHT_BADGE_TINTS,    # ["#FFF3EA", "#EBF7F9", "#FFF0F5", "#F1F7EE"] (Zero-alpha 0.00 nodes)
    GEPHI_SEQUENTIAL_SCALES,    # Dict["orange"|"blue"|"pink"|"green", List[5 hex nodes]]
    GEPHI_DIVERGING_SCALE,      # List[9 hex nodes: #0E5B6B .. #F5F6F7 .. #884725]
    GEPHI_DISCRETE_NEUTRALS,    # {"diverging_center": "#F5F6F7", "na_missing": "#D9D9D9", "other_aggregated": "#CBD5E1"}
    get_sequential_color,       # (value, v_min, v_max, scale="orange", discrete_steps=False) -> str (True CIELAB interpolation)
    get_diverging_color,        # (value, center=0.0, max_span=None, discrete_steps=False) -> str (Symmetric 9-node mapping)
    bind_qualitative_colors,    # (categories, allow_top4_aggregation=False, other_label="其他項目合計") -> Dict[str, str] (Auto-maps '其他' to #CBD5E1)
    get_category_badge_tint,    # (cat_or_key, category_color_map=None) -> str (Returns #FFF3EA / #EBF7F9 / #FFF0F5 / #F1F7EE)
    despine_axes,               # (ax, grid_axis="y", grid_color="#CBD5E1", grid_linestyle="--", grid_alpha=0.65) -> None
    export_gephi_palette_js,    # (output_path) -> str (Copies standalone gephi_palette.js into a Format E web project)
    load_and_split_csv,         # (csv_path, numeric_cols=None, label_cols=None, subtotal_keywords=None, other_keywords=None, known_na_tokens=None) -> (df_raw, df_detail, df_other, df_subtotal, stats_report)
)
```

1. **繪圖腳本防呆前處理、兩段式安全轉型與「標準化三層互斥分流」內嵌 `assert` 鐵律（Mandatory 3-Way Split & Safe Casting in Chart Scripts）**：
   - 凡讀取 CSV 繪圖之 Python 腳本，開頭強制實作以下防呆工序（可直接調用黑盒函數 `load_and_split_csv()` 或顯式內嵌）：
     1. **編碼與字串保護載入**：依序探測 `utf-8-sig` $\rightarrow$ `utf-8` $\rightarrow$ `cp950` $\rightarrow$ `big5`，初始以 `dtype=str` 讀取（保護行政區／機構代碼前置零），並清理欄名首尾空白與內嵌 `\ufeff` BOM。
     2. **兩段式安全轉型（Two-Stage Safe Casting）**：第一段先將《資料說明書》第 4 章記載之已知合法缺漏符號（如 `''`, `'-'`, `'—'`, `'...'`, `'N/A'`, `'NA'`, `'＊'`, `'*'`）顯式映射為 `np.nan`（統計 `NA` 筆數並於圖表標記為 `#D9D9D9`）；第二段對扣除已知缺漏後之數值字串（先清除千分位 `,`）執行嚴格數值轉型檢驗（若仍有未知非數值字元則報錯中止）。
     3. **三層互斥分流與 `assert` 檢核**：解析說明書第 2 章與第 4 節盤點之彙整列標籤，將 `df_raw` 強制拆解為三個互斥 DataFrame 並內嵌斷言：
        ```python
        # df_detail: 純一般明細列（剔除所有維度上的 總計/合計/小計/計 與原表 其他 列）
        # df_other:  原表自帶之 其他 / 未分類 彙整列
        # df_subtotal: 各層級之 合計 / 總計 / 小計 列（含交叉表次級小計）
        assert len(df_detail) + len(df_other) + len(df_subtotal) == len(df_raw), "三層互斥分流筆數不守恆！"
        ```
        所有後續之極值計算（`v_min, v_max`）、中位數、排行與視覺化繪製，**強制在 `df_detail`（或依選項 2 顯式整併 `df_other` 後之長尾）上進行，100% 杜絕合計列混入排行（Double Counting）**！
2. **極簡座標軸與水平基準網格**：調用 `despine_axes(ax, grid_axis="y")`（橫向長條圖則傳入 `grid_axis="x"`）隱藏頂部與右側邊框並設定極淡輔助虛線，輸出解析度統一為 **`dpi=300`**。
3. **節點上方直接數據標註與陡降折線右偏避讓（Direct Node Callouts & Steep-Slope Offset）**：每個折線圓點或長條末端直接標註粗體數值／百分比（`10~13pt Bold`），並預留軸線安全空間（如 `ax.set_ylim(0, 108)` 或 `ax.set_xlim(0, max_val * 1.18)`）。若為大斜率陡降折線，中間下降節點的標籤必須設定為**向右上微偏（`x + 0.14, y + 2.5, ha='left'`）**，嚴防左上至右下的折線直接穿過數字中央。
4. **零 Emoji 鐵律（Zero-Emoji Rule for FreeType / Microsoft JhengHei）**：Windows `Microsoft JhengHei`（微軟正黑體）不支援彩色 Emoji（如 `⚠️`、`🟢`、`🔴`、`✅`），在 `matplotlib` 渲染時必產生缺字方框（Tofu Box `□`）。圖表內所有文字、圖例與標註膠囊**絕對禁止使用任何 Emoji**，一律改用微軟正黑體原生內建之幾何符號（`▲`、`●`、`■`、`★`）。
5. **頂部斷言主標題與底部「精簡官方資料來源圖註」（Official Source Footnote）**：
   - **頂部**：配置 `16~20pt Bold` 完整核心斷言主標題（Assertion，優先採用說明書標註為 `【官方已說明】` 或 `【檔案觀察】` 之欄位發現）與 `11.5~12.5pt` 導讀副標題。
   - **底部精簡官方圖註（Footnote）**：列出所引用之**原始官方發布機關與資料集正式名稱**（**絕對禁止寫成「資料來源：資料說明書」或使用者自己的說明檔！**），且每項資料集**只要附加說明以下 2 項資訊即可**（免除冗長的三重時間戳記、樣本數與前處理說明，釋放畫布空間以放大圖表主體）：
     1. **官方資料集網址**
     2. **資料涵蓋期間**
