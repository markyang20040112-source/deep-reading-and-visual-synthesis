# 主幹風格與色彩定裝核心（Trunk Style & Color Core — 混合式全域預設）

> **單一職責定位（Single Responsibility）**：本檔負責於 Phase 2 **主幹階段**建立輕量級 **「全域預設三支柱（設計光譜模式 1/2/3 × 筆風檔 `Slot 1～8` × 分層配色/主題）」**，寫入藍圖 `## 0. 主幹全域錨點`。採 **混合式定裝架構（Hybrid Styling Model）**：各選定格式在進入各自 `01_plan.md` 時可**無痛承襲全域預設，或針對單一格式進行局部覆寫**（例如 Format D 用模式 2 編輯室筆風，Format B 改用模式 1 嚴謹統計＋標楷體）。
> - **格式專屬定裝已下放各分枝**：Format B PDF 字體（`modern_sans` vs. `clreq_kaiti`）歸屬 [`../formats/format_b_document/01_plan.md`](../formats/format_b_document/01_plan.md)；Format C 模式 3 `Tier 1/2/3` 推薦、差異揭露與 Topic Art Direction DNA 卡歸屬 [`../formats/format_c_slides/01_plan.md`](../formats/format_c_slides/01_plan.md)。

---

## 一、 支柱 1：全格式「設計光譜與轉譯武器庫」全域預設

| 模式代號 | 設計光譜定位與武器庫狀態 | 適用情境診斷建議 | 跨格式（A / B / C / D / E）核心視覺效果 | 終端按需載入之專檔（徹底解耦） |
| :--- | :--- | :--- | :--- | :--- |
| **🔘 模式 1**<br>`standard_rigorous` | **標準嚴謹模式**<br>*(設計武器庫關閉)* | 嚴肅實證研究、10 大分配圖形導學（`pure_dataviz`）、**共用基線雙序列剪刀差／全樣本高密度散點圖**、蝴蝶金字塔與雙向動量箭頭圖（已內建家族 1）、高密度技術／法規文件 | • **A/B/C**：標準瑞士網格、三線表、五大簡報家族（`F1～F5` 13 版型，無框細線為主）<br>• **D/E**：純資料視覺化（零浮動框）、共用基線剪刀差、全樣本氣泡矩陣、蝴蝶金字塔、雙向動量箭頭、標準 BI 儀表板 | **否**（0 額外載入） |
| **🔘 模式 2**<br>`editorial_narrative` | **編輯室權威敘事設計**<br>*(資料八／經濟學人／數據百閱)* | 數據新聞專欄（Medium）、商業策略備忘錄、縣市／產業差距排行、跨期政策轉折、高階決策簡報 | • **A**：80/20 聚光燈高亮卡＋瓶頸膠囊地標<br>• **B**：`.editorial-masthead`、`.big-stat-callout`、`.myth-reality-split`、`.methodology-traffic-light`<br>• **C**：`F1-C` 巨幅焦點宣言、`F5-B` 頂部指標橫帶、80/20 聚光燈<br>• **D/E**：資料八 5 大技法（聚光燈著色、雙基準膠囊、時期色帶、角落排行卡、四層底註） | **是**：僅開啟 [`editorial_narrative_spec.md`](./editorial_narrative_spec.md) |
| **🔘 模式 3**<br>`bespoke_metaphor` | **開放式創意隱喻武器庫**<br>*(RE:LAB 材質 ＋ Form-as-Metaphor 純幾何)* | 大眾傳播、主題專欄破題、茶飲／農業／能源／環境等具強烈物質或空間隱喻的視覺故事（**可獨立運作，不強制附模式 2 浮動框**；不限縮固定模板） | • **A**：冰山分層、階梯漏斗、雙向天平空間隱喻<br>• **B/E**：CIELAB 議題語義色階、主題裝幀與容器進度條<br>• **C**：`Tier 1/2/3` 分層解鎖＋動態主題色票＋唯一核心母題與 `20/80` 紅線（細節於 `formats/format_c_slides/01_plan.md` 拍板）<br>• **D**：100% 數學誠實之純幾何隱喻或武器庫原子案例（液面容器、材質遮罩扇形、精靈散佈） | **是**：先僅開啟 [`creative_armory/INDEX.md`](./creative_armory/INDEX.md) 單行索引，再按需單開 1 份案例卡（唯有疊加模式 2 才併讀 `editorial_narrative_spec.md`） |

> **【模式 1 vs. 模式 3 實證選型邊界（`T25`）】**：直接依數據結構與讀取任務分派模式，不設重複雙軌製圖：
> - **雙序列淨差距（需共用基線）**或**多維全樣本高密度分布（不可刪樣本）** ➔ 強制守住 **模式 1**（可搭模式 2 精煉標註）；
> - **正倒金字塔對立（蝴蝶金字塔）**與**起迄轉化動量（`plot_dumbbell(directed=True)`）** ➔ 已常駐 **模式 1 家族 1**，免啟動材質管線；
> - 唯有**項目精簡且具強烈物質／容量／比例／空間實體隱喻**時，才啟用 **模式 3**。

---

## 二、 支柱 2：筆風設定檔全域預設（Writing Style — `Slot 1～8` 穿透）

先呼叫 `hcl_color_engine.check_user_identity_and_load_prefs()` 取得當前身分可用筆風（擁有者 `markyang20040112-source` 讀 `config/owner_styles/*.md`；外部使用者僅讀 `config/user_styles/*.md`），並給出預設搭配建議（各分枝可於 `01_plan.md` 局部指定不同筆風）：

| 任務與設計模式組合（若為擁有者） | 首選推薦筆風檔 | 核心筆風特徵與 `Slot 1～8` 穿透效果 |
| :--- | :--- | :--- |
| **模式 2 / 3 ＋ Medium 數據專欄 ／ 編輯室圖表** | `editorial_data_journalism.md` | 反差鉤子先行、新聞感精煉短句、微觀個案佐證，驅動圖表主副標、膠囊與專欄敘事 |
| **模式 1 ＋ 10 大分配導學 ／ 實證研究報告** | `rigorous_empirical_stat.md` | 統計指標與口徑先行、五步導學嚴謹解說、生態謬誤與推論邊界自動把關 |
| **長文剖析 ＋ Format A 圖譜 ／ 策略備忘錄** | `plain_first_progressive.md` 或 `personalized_essay_style.md` | 白話直覺先行、類比橋接由淺入深，確保複雜架構卡片與簡報講稿一眼秒懂 |

---

## 三、 支柱 3：分層顏色設定集全域預設（Layered Color Sets）

1. **第一層：`chart_palettes`（控制 Format D ⇄ Format E）**：
   - **預設 A（個人鎖定色票）**：套用 `config/user_preferences.json` 現行色票（擁有者預設 `gephi_pastel_locked`；外部使用者為自建 CIELAB 色票）。
   - **進階 B（CIELAB 主題語義微調色階 — 推薦搭模式 2/3）**：呼叫 `derive_thematic_palette()` / JS `deriveThematicPalette()` 選用內建 5 大色階（或傳入單一代表 HEX 自動推導 4 色＋5 階循序＋9 階發散）：
     - `"milk_tea"` / `"bubble_tea"`（奶茶焦糖棕＋茶綠）
     - `"forest_eco"` / `"matcha_forest"`（森林生態＋抹茶綠）
     - `"ocean_blue"` / `"ocean_hydro"`（深海＋水文藍）
     - `"coffee_roast"`（烘焙咖啡棕）
     - `"pineapple_tropical"` / `"agri_gold"`（鳳梨金黃＋農產綠）
2. **第二層：`document_themes`（控制 Format A / B / C）**：
   - 靜態佈景主題：`modern_academic_slate`、`swiss_editorial`、`warm_editorial_ivory`（各分枝皆可覆寫；Format C 模式 3 動態色票 `derive_slide_theme_from_topic()` 由 `formats/format_c_slides/01_plan.md` 決定）。
3. **全域交付偏好**：預設 `default_delivery_cadence = "sequential_confirm"`（佇列 `D ➔ A ➔ B ➔ C ➔ E`）、`default_slide_qa_mode = "option_c_2x2_and_high_risk"`，並於全格式確認後統一執行 Git 同步。

---

## 四、 混合式分枝覆寫規則與主幹交接

主幹確認全域預設三支柱（與任何全域客製細節）後，寫入 `02_phase2_generation_blueprint.md` 的 **`## 0. 主幹全域錨點`**，隨即按 [`router.md`](./router.md) 進入各選定格式的 `01_plan.md`。任何格式若需不同模式、筆風、色票或專屬參數（如 B 的 PDF 字體、C 的模式 3 Tier/DNA），直接記錄於該格式的 **`## Format X 分枝藍圖`「分枝覆寫」** 欄位，**覆寫僅作用於該格式分枝，不污染其他格式**。
