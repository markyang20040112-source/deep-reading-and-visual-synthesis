# 第三層顧問（最後決策層）：全格式設計武器庫 × 筆風 × 分層配色全域定裝大腦

> **單一職責定位（Single Responsibility）**：本檔為 Phase 2 **第三層（Layer 3 — 最後決策層）專用顧問檔**，僅於第一層（A/B/C/D/E 範圍）與第二層（具體圖型、文體、拓撲與簡報定位／單一議題章節清單）皆已拍板定案後開啟。負責協助使用者為所有確定生成的檔案統一或混搭配置 **「表達三支柱（設計光譜與轉譯武器庫開關 × 筆風設定檔 × 顏色設定集與版面細節）」**，完成後即鎖定終端最小葉節點規格檔清單，依 `D ➔ A ➔ B ➔ C ➔ E` 逐格式接力動工！

---

## 一、 支柱 1：全格式「設計光譜與轉譯武器庫開／關（套用至所有選定的 A / B / C / D / E）」

看著第二層拍板的具體圖表與文件清單，協助使用者選擇最適合的設計外衣（支援全套統一，或依不同檔案個別指定混搭）：

| 模式代號 | 設計光譜定位與武器庫狀態 | 適用情境診斷建議 | 跨五大格式（A / B / C / D / E）的具體視覺效果 | 終端按需載入之專檔（徹底解耦） |
| :--- | :--- | :--- | :--- | :--- |
| **🔘 模式 1**<br>`standard_rigorous` | **標準嚴謹模式**<br>*(設計武器庫關閉)* | 嚴肅實證統計研究、10 大分配圖形逐步導學（`pure_dataviz`）、**需嚴守共用基線之雙序列剪刀差或高密度全樣本多維散點圖**、對立蝴蝶金字塔與雙向動量箭頭圖（已內建常駐家族 1）、高密度法規／技術文件 | • **A/B/C**：標準瑞士網格知識卡、標準三線表、五大簡報版型家族（`F1～F5`，13 精煉版型：1 首尾定錨 ＋ 12 內容與衝擊版型，無框細線為主、單層輕卡點綴）標準斷言簡報<br>• **D/E**：純資料視覺化（零多餘浮動框）、統計基準線與誤差帶、共用基線剪刀差、全樣本氣泡矩陣、對稱蝴蝶金字塔、雙向動量向量箭頭與標準互動 BI 儀表板 | **否**（0 額外載入） |
| **🔘 模式 2**<br>`editorial_narrative` | **編輯室權威敘事設計**<br>*(資料八／經濟學人／數據百閱模式開啟)* | 數據新聞專欄（Medium）、商業策略備忘錄、縣市／產業差距排行、跨期政策轉折分析、高階決策簡報 | • **A**：80/20 聚光燈高亮核心卡＋因果斷裂瓶頸膠囊地標<br>• **B**：報刊頂部粗橫線（`.editorial-masthead`）、巨型黃金數字衝擊盒（`.big-stat-callout`）、迷思與真相對撞台（`.myth-reality-split`）、方法論紅黃綠燈卡（`.methodology-traffic-light`）<br>• **C**：`F1-C` 巨幅焦點宣言頁（巨幅數字／金句雙變體）、`F5-B` 頂部指標橫帶與 80/20 單頁聚光燈反差<br>• **D/E**：**資料八五大標竿技法**（首尾極值聚光燈著色、雙基準虛線＋頂部帶框膠囊徽章、時期背景色帶＋歷史事件引線框、主圖＋角落排行榜副卡、四層結構化底註） | **是**：僅開啟 [`../editorial_narrative_spec.md`](../editorial_narrative_spec.md) |
| **🔘 模式 3**<br>`bespoke_metaphor` | **開放式創意隱喻武器庫**<br>*(RE:LAB 具象材質 ＋ 純幾何 Form-as-Metaphor 開放式轉譯)* | 大眾傳播、主題專欄破題、生活消費／農業／茶飲／能源／環境等具強烈物質或空間隱喻的視覺故事（**可獨立運作且不強制附加模式 2 浮動框**；不限縮於既有固定模板，鼓勵依議題原創合法幾何／材質隱喻） | • **A**：將網格轉譯為**冰山分層圖（水面上下）**、**階梯漏斗過濾器**或**雙向天平力場圖**<br>• **B/E**：注入經 CIELAB 校正之**議題語義色階**、主題裝幀與容器進度組件<br>• **C**：**三級分層解鎖（`Tier 1 / Tier 2 / Tier 3`）**＋ `derive_slide_theme_from_topic()` 動態主題色票＋唯一核心母題與 `20/80` 克制紅線（見下方一之一節）<br>• **D**：依開放創意底線（100% 數學誠實、不損及共用基線與全樣本密度）自由發想純幾何物理結構，或按需取用武器庫原子案例（液面容器、無文字材質＋`Wedge` 扇形遮罩、精靈圖標座標散佈、CIELAB 主題色階看板） | **是**：先僅開啟 [`../creative_armory/INDEX.md`](../creative_armory/INDEX.md)（單行索引），再按需點開 1 份對應原子案例卡；**唯有同時要求模式 2 編輯室組件時才併讀 `editorial_narrative_spec.md`** |

> **【模式 1 vs. 模式 3 實證選型邊界提醒（`T25`）】**：在第三層混搭各圖表設計模式時，**直接依數據結構與讀取任務精準分派模式 1 或模式 3**（不設額外 A/B 雙軌重複生成模式）：
> - 凡屬「**雙序列淨差距比較**（需共用基線）」或「**多維全樣本高密度分布**（不可為造型刪減樣本）」，強制建議守住 **模式 1**（或搭配模式 2 精煉標註）；
> - 凡屬「**對立序數輪廓反轉**（蝴蝶金字塔）」或「**具起迄方向之轉化動量**（`plot_dumbbell(directed=True)`）」，已在**模式 1 家族 1** 原生常駐，無須啟動材質管線即可獲得高故事穿透力；
> - 唯有「**項目精簡且具備強烈物質／容量／比例／空間實體隱喻**」，才啟動 **模式 3** 開放創意武器庫。

### 一之一、 Format C 開啟模式 3（`bespoke_metaphor`）專屬機制：主動推薦 `Tier`、差異揭露與 Topic Art Direction DNA 卡

當本次包含 Format C 簡報且評估／開啟模式 3 時，**AI 嚴禁預設硬套單一等級**，必須先依本次「主題屬性」與「簡報用途」向使用者進行以下三項揭露，再由使用者最終拍板等級：
1. **主動給出推薦等級與理由**（例如建議 `Tier 1` 或 `Tier 2`）；
2. **具體描述 `Tier 1 / Tier 2 / Tier 3` 在本主題下的實際視覺隱喻與設計長相**；
3. **透明比較三等級在 PowerPoint 改字彈性與生成成本上的差異**：

| 模式 3 等級 | 技術構成與視覺表現 | PowerPoint 後續改字彈性 | 生成成本與依賴 |
| :---: | :--- | :--- | :--- |
| **`Tier 1`** | **100% 原生幾何原語**（斜切色面、刻度尺線、階段台階、向量天平、巨型序號）＋ **`derive_slide_theme_from_topic()` 動態主題色票** | **最高（全頁 100% 原生可改字與調幾何）** | 最低（純 `python-pptx` 原生向量） |
| **`Tier 2`** | `Tier 1` ＋ 封面／過場／至多 1 頁破題頁加入 **呼叫 `image-generator` 子代理生成之無文字概念主視覺**（存於 `02_outputs/assets/`，預留乾淨負空間，中文原生標題疊加其上；中段 70%～80% 頁維持全原生） | **高（全文字 100% 原生可改；僅概念底圖重繪需重跑生圖）** | 中（增 1～3 張無字概念圖） |
| **`Tier 3`** | `Tier 1/2` ＋ **1～2 頁最核心機制頁 HTML+SVG `300 DPI` 透明底層嵌入**（平滑貝茲濾網漏斗、失衡天平、冰山分層；**頁頂標題與旁側導讀維持 PowerPoint 原生可編輯**） | **中高（標題與導讀皆原生可改；該 1～2 頁 SVG 視覺底層須改 HTML/SVG 重渲）** | 較高（調用 `render_svg_to_png_300dpi`，Playwright+Chromium 優先、退回 Chrome/Edge CLI） |

- **三大創意元素與主題目標強對齊規範**：
  1. **動態主題色票（`derive_slide_theme_from_topic()`）**：依主題語義與場域（開燈教室淺底安全組優先 vs. 可控深場發表）於 CIELAB 推導色票並強制通過 WCAG AA（$\ge 4.5:1$），杜絕千篇一律商務藍；
  2. **`image-generator` 無文字概念主視覺（存於 `02_outputs/assets/`）**：緊扣唯一核心隱喻且預留乾淨負空間，嚴禁商務握手／發光大腦圖庫照與無關裝飾圖（Bartsch & Cobern 2003）；
  3. **HTML+SVG `300 DPI` 透明視覺底層**：僅服務 1～2 頁核心系統／因果隱喻，視覺語彙與色票須與原生頁一體成型，標題與註解維持原生可編輯。
- **Topic Art Direction DNA 卡（標準格式 — 使用者拍板後寫入 `02_phase2_generation_blueprint.md` 第 3 節）**：
  ```markdown
  - **Topic Art Direction DNA 卡（Format C 模式 3）**：
    - **拍板等級與理由**：`Tier 1` / `Tier 2` / `Tier 3` — <選型依據>
    - **唯一核心視覺母題（限 1 個）**：<例：訊號雜訊濾網 / 階梯天平 / 深度切面>
    - **動態主題色票性格**：<主題語義鍵或代表 HEX ➔ `derive_slide_theme_from_topic(mode="light_classroom"|"dark_stage")`>
    - **創意頁面配額（嚴守 `20/80` 克制紅線）**：<明確列出哪 1～3 頁使用概念圖／SVG 底層，其餘 70%～80% 頁採乾淨無框細線承托>
  ```

---

## 二、 支柱 2：筆風設定檔選配（Writing Style Profile — `Slot 1～8` 100% 全域穿透）

先呼叫 `hcl_color_engine.check_user_identity_and_load_prefs()` 取得當前使用者身分可用的筆風清單（擁有者 `markyang20040112-source` 顯示 `config/owner_styles/*.md`；外部使用者僅顯示 `config/user_styles/*.md`），並依本次任務特性提供搭配建議（**支援不同產出檔案交叉指定不同筆風**）：

| 任務與設計模式組合（若為擁有者） | 首選推薦筆風設定檔 | 核心筆風特徵與 `Slot 1～8` 穿透效果 |
| :--- | :--- | :--- |
| **模式 2 / 3 ＋ Medium 數據專欄 ／ 編輯室圖表** | `editorial_data_journalism.md` | 反差鉤子先行、新聞感精煉短句、微觀個案佐證，完美驅動圖表主副標題、膠囊與專欄敘事 |
| **模式 1 ＋ 10 大分配圖形導學 ／ 實證研究報告** | `rigorous_empirical_stat.md` | 統計指標與研究口徑先行、五步導學嚴謹解說、生態謬誤與推論邊界自動把關 |
| **長文深度剖析 ＋ Format A 知識圖譜 ／ 策略備忘錄** | `plain_first_progressive.md` 或 `personalized_essay_style.md` | 白話直覺先行、類比橋接由淺入深，確保複雜架構卡片與簡報講稿一眼秒懂 |

---

## 三、 支柱 3：分層顏色設定集、主題語義色階與版面細節

1. **圖表與儀表板配色設定集（`chart_palettes`）**：
   - **預設選項 A（個人鎖定色票）**：套用 `config/user_preferences.json` 當前啟用之預設色票（擁有者預設 `gephi_pastel_locked`）。
   - **進階選項 B（CIELAB 主題語義微調色階 — 推薦搭配模式 2 或 3）**：調用 `derive_thematic_palette()`（或 JS `deriveThematicPalette()`），依文章／數據議題選擇對應色階（或提供單一代表 HEX 自動推導 4 色＋5 階循序＋9 階發散）：
     - `"milk_tea"` / `"bubble_tea"`（奶茶焦糖棕與茶綠）
     - `"forest_eco"` / `"matcha_forest"`（森林生態與抹茶綠）
     - `"ocean_blue"` / `"ocean_hydro"`（深海與水文藍）
     - `"coffee_roast"`（烘焙咖啡棕）
     - `"pineapple_tropical"` / `"agri_gold"`（鳳梨金黃與農產綠）
2. **文件與簡報佈景主題（`document_themes`）與版面／交付細節**：
   - 靜態佈景主題（如 `modern_academic_slate`、`swiss_editorial`、`warm_editorial_ivory`）；若 Format C 開啟模式 3 或需主題動態色票，改以 **`derive_slide_theme_from_topic()`** 推導 CIELAB 動態主題並通過 WCAG AA（$\ge 4.5:1$）檢核。
   - 若含 **Format B 文體 1～4（A4 PDF）**：確認字體模式為 **`modern_sans`（現代無襯線黑體）** 或 **`clreq_kaiti`（台灣大專院校標楷體 `DFKai-SB` ＋ 正文首行空兩格）**。
   - 確認跨格式接力交付節奏（預設 `default_delivery_cadence = "sequential_confirm"`，按 **`D ➔ A ➔ B ➔ C ➔ E`** 逐格式確認後再推進）、Format C 內部品管模式（預設 `option_c_2x2_and_high_risk`），以及全部確認完成後是否統一執行私人倉庫／公開倉庫 Git 同步。

---

## 四、 第三層定裝提案確認與終端最小葉節點檔案清單鎖定

向使用者提出簡明清晰的第三層定裝建議表（並一併確認任何客製細節或例外覆寫需求）後 **⏸️ 暫停等待使用者最後拍板**。
使用者拍板後，立即將第 3 節（表達三支柱定裝與取捨理由）、第 4 節（使用者客製細節覆寫）與第 5 節（終端最小葉節點、跨格式接力佇列與交付清單）寫入 `02_phase2_generation_blueprint.md` 定稿（**嚴禁回寫入 `01_phase1_socratic_log.md`**），隨後依 **`default_delivery_cadence = "sequential_confirm"`（預設佇列 `D ➔ A ➔ B ➔ C ➔ E`）每輪僅按需開啟當前單一格式對應之最小葉節點規格檔**，完成生成、視覺驗收並獲使用者確認後，始開啟下一個格式的規格檔：
- 必讀底盤：[`../visual_cognition_principles.md`](../visual_cognition_principles.md) ＋ 選定之筆風檔
- 若開啟模式 2 (`editorial_narrative`) $\rightarrow$ [`../editorial_narrative_spec.md`](../editorial_narrative_spec.md)
- 若開啟模式 3 (`bespoke_metaphor`) $\rightarrow$ 先開啟 [`../creative_armory/INDEX.md`](../creative_armory/INDEX.md)，再依需求按需單開 `creative_armory/cases/` 下對應之原子案例卡（若同時疊加模式 2 編輯室組件再併開 `../editorial_narrative_spec.md`）
- 若含圖表（Format D/E）$\rightarrow$ [`../quantitative_chart_spec.md`](../quantitative_chart_spec.md) ＋ 第二層被點名的 1～2 個家族檔（`chart_family1` / `chart_family2` / `chart_family3` / `distribution_and_density_chart_spec` / `chart_family5`）
- 依選定格式（未選者 0 讀取）$\rightarrow$ Format A [`../visual_diagram_matplotlib_spec.md`](../visual_diagram_matplotlib_spec.md) ／ Format B PDF [`../document_report_spec.md`](../document_report_spec.md) ／ Format B Medium [`../medium_column_spec.md`](../medium_column_spec.md) ／ Format C [`../presentation_slide_spec.md`](../presentation_slide_spec.md) ／ Format E [`../data_dashboard_spec.md`](../data_dashboard_spec.md)
