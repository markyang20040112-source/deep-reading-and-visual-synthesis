# 斷言-證據式簡報設計與原生向量排版規範（Format C: Presentation Slide Spec）

> **單一職責定位（Single Responsibility）**：本檔專責 **Format C（16:9 高階主管簡報 `.pptx`）** 的斷言-證據（Assertion-Evidence）三區架構、首尾定錨與中段雙因子動態配頁、**防審美疲勞之八大版型指派與防撞車仲裁引擎（`S0`～`S7`）** 與 `python-pptx` 原生向量繪製規範。跨格式共用的組塊階層、白話由淺入深原則與基礎色票請見 [`visual_cognition_principles.md`](visual_cognition_principles.md)。

---

## 一、 單頁投影片「三區黃金結構」與斷言-證據核心法則（3-Zone Architecture）

- **理論依據**：**斷言-證據簡報架構（Assertion-Evidence Approach, Alley & Neeley 2005）**、**前注意聚光燈法則（Knaflic 2015）** 與 **冗餘效應消除（Mayer 2009）**。全面禁止傳統純文字項目符號頁（Zero Raw Bullet-Point Slides），每頁 `16:9`（`13.333" × 7.5"`）嚴格切分為三區：

1. **【Zone 1：頂部斷言區（Top 15% Height, `y = 0.0"` to `1.18"`）】**
   - **頂部章節導航膠囊「剛剛好貼合字寬（Exact Text-Hug Sizing）」**：左上角深藍色章節膠囊既不可比文字短（穿框），也不可比文字長出一大截。必須使用微軟正黑體 `9.5pt` 精確字寬公式：
     $$\text{pill\_w} = \frac{9.5}{72.0} \times (1.00 \times \text{CJK\_Chars} + 0.50 \times \text{ASCII\_Chars}) + 0.22\text{"}$$
     搭配文字水平置中（`PP_ALIGN.CENTER`）與左右對稱微內距，讓膠囊完美貼合字體長度。
   - **Zone 1 垂直三段等距呼吸配置**：
     1. 頂部留白 `0.15"` $\rightarrow$ 章節膠囊（`top = 0.15"`, `height = 0.28"`, 底邊 `0.43"`）。
     2. 中段呼吸間距 `0.15"`（嚴禁將大標題緊貼膠囊底邊）。
     3. **完整句子結論斷言標題（Sentence Assertion Headline）**：配置於 `top = 0.58"`, `height = 0.44"`，強制設定 `vertical_anchor = MSO_ANCHOR.MIDDLE`，底部留白 `0.16"`。字數嚴格控制在 **1～2 行、22～36 漢字**（`19.5pt ~ 22pt Bold`），直接陳述該頁「主詞 + 動詞 + 因果/數據結論」。
2. **【Zone 2：中央視覺證據畫布（Middle 75% Height, `y = 1.32"` to `6.55"`）】**
   - **禁止塞入縮小版心智圖圖片**：嚴禁將高密度心智圖直接縮小貼入投影片（會導致字體過小看不清）。所有畫面必須使用 `python-pptx` 原生向量幾何圖形與大字級卡片，或嵌入專為簡報比例裁切的高解析度單面板量化圖表（`300 DPI`）。
   - **依欄數物理幾何分級之內文字級下限（Column-Count Calibrated Typography）**：
     - **雙欄並排卡片（`S1` 不對稱雙欄，單卡寬度 $\approx 5.4"\sim 6.6"$）**：內文字級鎖定 **`13.0pt ~ 14.5pt`**（每行容納 `22～26` 漢字）。
     - **三欄或四欄並排卡片（`S2` 三支柱、`S3` 四步管線、`S7-A/B` 圖卡複合，單卡寬度 $\approx 2.85"\sim 4.65"$）**：內文字級鎖定 **`11.5pt ~ 12.5pt`**（每行容納 `16～19` 漢字，**每個水平列槽嚴格控制在 $\le 45$ 漢字／2～3 行以內**，杜絕文字溢位穿框）。
   - **並排卡片內部「水平平行對齊列槽（Parallel Row Panels）」**：當畫面有 2 欄、3 欄或 4 欄卡片並排時，嚴禁將所有列點塞進單一文字框任其高低錯位；必須調用 `draw_parallel_row_cards()` 將每張卡片內部切分為**相同 $Y$ 座標與等高之獨立列槽（Row 1: 淺層現象、Row 2: 中層情境、Row 3: 深層對策）**，並在每個列槽內垂直置中（`MSO_ANCHOR.MIDDLE`），確保跨卡橫向 100% 平行對齊。
   - **Knaflic 80/20 聚光燈配額（Preattentive Spotlight）**：同頁的 2～4 個視覺區塊中，**最多僅允許 1 個核心破局區塊使用高彩度強調色邊框/頂帶**，其餘背景與對照區塊一律退居低飽和結構灰藍（`#64748B` / `#CBD5E1`），避免滿頁五顏六色造成視覺疲勞，確保聽眾於 $200\text{ms}$ 內鎖定焦點。
3. **【Zone 3：底部行動啟示橫幅（Bottom 10% Height, `y = 6.68"` to `7.22"`）】**
   - 全寬單行高對比橫幅（**`12.5pt ~ 14.0pt Bold`**），一句話點出本頁證據對決策者的具體行動意義（*So-What Takeaway*）。
   - **講者備忘稿（Speaker Notes）雙通道分離**：單頁畫面總字數控制在 **110～160 漢字以內**；完整口語推演、白話比喻與轉場台詞一律寫入 `slide.notes_slide.notes_text_frame`（`add_speaker_notes()`）。

---

## 二、 防審美疲勞核心：三階版型指派與防撞車仲裁引擎（3-Tier Layout Dispatch Engine）

- **理論依據**：**相容性原則（Compatibility Principle, Kosslyn 2007：版型幾何必須與論點內在邏輯同構）** 與 **視覺習慣化防禦（Visual Habituation Defense, Mackworth 1948：相鄰頁變換空間拓撲以維持前注意警覺度）**。
- **AI 決定每一頁使用何種排版的「三階段控制流程」**：

### 階段 1：首尾位置鎖定（Position Lock）
- **第 1 頁（封面頁）** 與 **最後 1 頁（峰終結尾頁）** $\rightarrow$ 無條件鎖定為 **`S0`（深色首尾定錨型）**。

### 階段 2：論點語義與證據型態對映（Semantic-to-Layout Dispatch Table）
中段每一頁依其**「核心論點邏輯」與「證據型態」**，查表指派**首選版型（Primary Fit）**；若與前一頁撞版，則自動啟用右欄的**防撞車備選版型（Fallback Fit）**：

| 版型代號與名稱 | 觸發條件（當該頁論點具備以下特徵時選用） | 空間幾何配置與 80/20 聚光燈設計（`13.333" × 7.5"`） | 防撞車備選轉換版型（若前一頁已用此版型時） |
| :--- | :--- | :--- | :--- |
| **S0：深色首尾定錨型**<br>*(Dark Bookend)* | **僅限第 1 頁封面 & 最後 1 頁結尾總結** | 深石板藍底（`#0F172A`）+ 頂部亮色分類膠囊 + `26~32pt` 巨幅主標題 + 底部 3 張關鍵指標或決策鐵律亮框卡。 | *(固定於首尾，中段禁用)* |
| **S1：不對稱雙欄對照型**<br>*(Asymmetric Contrast)* | **2 個二元對立觀點**（迷思 vs. 真相、舊模式 vs. 新典範、失敗案例 vs. 成功標竿） | 左欄（`45%` 寬，中性灰或警示色條）呈現「舊盲點／反例」$\leftrightarrow$ 右欄（`55%` 寬，**聚光燈強調色條**）呈現「新破局／正例」。 | 轉為 **`S4`**（畫出兩者互動/轉換機制）或 **`S5`**（加入第 2 維度展開為 2×2 象限） |
| **S2：三支柱聚焦卡片型**<br>*(Three Pillars + 1 Spotlight)* | **3 個並列同質維度**（三大痛點、三大陷阱、三個分析層面） | 水平等寬並列 3 張圓角卡片（內部切為 3 個水平平行對齊列槽）。前 2 張為穩重結構色，**第 3 張套用聚光燈高亮邊框**。 | 若 3 點具先後關係則轉為 **`S3`（水平階梯流）**；若具交互作用則轉為 **`S4`（三層系統架構）** |
| **S3：水平階梯演進流程型**<br>*(4-Step Process Pipeline)* | **3～4 個具時序或因果依賴的步驟**（落地路線圖、MVP 四部曲、轉換管線） | 由左至右排列 3～4 個帶編號（`Step 01` $\rightarrow$ `Step 04`）之垂直流程卡，卡片間以原生向量箭頭標註轉換條件，於核心破局步驟高亮。 | 轉為 **`S5`**（依「實行難度 × 商業價值」或「短期 × 長期」排入 2×2 矩陣） |
| **S4：核心系統迴路／雙腦架構型**<br>*(System Loop / Architecture)* | **多組件雙向協同、正負反饋閉環或雙腦架構**（如左腦規則 × 中間裁判 × 右腦檢索） | 左側或中央繪製原生向量雙軌/三層系統迴路圖（標註雙向互動箭頭與仲裁核心），旁側或下方配置關鍵機制洞察卡。 | 轉為 **`S1`**（左右雙腦對比 + 中央橋接橫幅）或 **`S2`**（三層平行協同矩陣） |
| **S5：2×2 策略象限矩陣型**<br>*(2×2 Quadrant Matrix)* | **4 個分類項目或雙軸評估**（四大機會領域、風險 × 報酬矩陣、四象限治理） | 正交雙軸四象限網格，將三個次要象限設為淺灰背景，僅將**目標破局象限**高亮放大並標註行動方針。 | 若 4 項具演進順序則轉為 **`S3`（四步階梯管線）** |
| **S6：核心公式／理論解剖型**<br>*(Equation / Theory Anatomy)* | **含數學公式、不等式、剪刀差模型或核心理論定律** | 上方置中呈現醒目的深色或高對比「核心公式／定律展示盒」，下方水平並列 3 張指向拆解卡，逐一對應公式變數的白話意義。 | 轉為 **`S1`**（左側公式與理論推導 + 右側商業實證對照） |
| **S7：量化圖表＋洞見卡複合型**<br>*(Chart + Cards Dual-Mode: `S7-A` 左圖右卡 / `S7-B` 上圖下卡)* | **含高解析度量化實證圖表與 3 張數據洞見卡**（依**圖片內容長寬比**與**文字結構**動態二選一，嚴禁寫死單一放法！） | • **`S7-A`（左圖最大化 `W=7.35"~7.45"` + 圖表正下方緊鄰註解框 + 右垂直三卡 `W=4.65"`）**：當圖片接近 `16:9` 或雙圖並列（`1.3 ≤ AR ≤ 2.1`、具垂直高度斷崖）且文字為 3 段精煉垂直遞進洞見時選用。**強制規範**：左側圖表寬度最大化至 `7.35"~7.45"`（`Left = 0.50"`），「圖表導讀註解框」必須緊貼配置於**圖表正下方**（符合 Mayer 空間鄰近原則），且右側三張卡片維持原寬 `W = 4.65"`（`Left = 8.18"`）絕不壓縮！<br>• **`S7-B`（上全寬圖 + 下水平三卡）**：當圖片為極寬扁橫幅（`AR > 2.1`，如超長跨期時間軸或寬幅矩陣）或文字卡需直接對應圖表左、中、右三區段時選用。 | 若與前後頁版型重心重複，可在 **`S7-A`（左右重心）** 與 **`S7-B`（上下重心）** 之間自動切換以打破視覺疲勞！ |

### 階段 3：全局序列防撞車檢核（Storyboard Anti-Collision Check）
在動手寫 `python-pptx` 腳本前，AI 必須先列出全簡報的 **「分頁版型序列（Layout Sequence）」** 並調用 `validate_layout_sequence(layouts)` 執行兩項硬性檢查：
1. **相鄰異構檢核（`Layout[i] != Layout[i+1]`）**：檢查是否有任何連續兩頁使用相同版型代號。若有，強制將第 $i+1$ 頁依上表右欄轉為備選版型。
2. **視覺重心交替檢核（Visual Center-of-Gravity Alternation）**：確保全簡報在「左右分欄（`S1`）」、「上下分層（`S6`/`S7`）」、「三欄/四欄並列（`S2`/`S3`）」與「網格/系統圖（`S4`/`S5`）」之間交錯切換，整份簡報至少涵蓋 **5 種以上不同版型**。

---

## 三、 首尾錨定與中段「雙因子動態擴展・零刪減加頁」法則（Bookends & Zero-Truncation Dynamic Budgeting）

1. **強制保留首尾定錨頁（Mandatory Bookends）**：
   - **第 1 頁（封面頁 Cover Slide）** 與 **最後 1 頁（峰終定律結尾總結頁 Closing Slide, Kahneman 1993）** 必須固定保留為獨立單頁（套用版型 `S0`），嚴禁講完最後一頁內容就突兀結束。
2. **中段四幕敘事弧與「零刪減動態加頁」法則**：
   - 中段依序展開 **Act I（現狀診斷與痛點）→ Act II（核心矛盾與理論模型）→ Act III（系統架構、反例邊界與跨域實證）→ Act IV（落地行動路線圖）**。
   - **不設硬性總頁數上限，嚴禁刪減批判延伸分支**：當 Phase 1 Step 5 收斂出 $> 4$ 個分支（含 `(b) 批判延伸與跨域遷移分支`）時，**必須動態加開獨立投影片**（如以 `S1` 呈現正反案例對撞、以 `S5` 呈現假設失效邊界象限、以 `S4` 呈現跨領域同構系統）並附上完整講者備忘稿，確保所有思辨成果 100% 呈現：
     - **功能性聚合（何時合於一頁）**：當多個觀點屬於「正反二元對比（`S1`）」、「三大平行維度比較（`S2`）」、「四步管線/四象限（`S3`/`S5`）」或「系統因果閉環（`S4`）」時，聚合於同一頁方便聽眾同屏橫向比對。
     - **空間呼吸與序列推進（何時拆頁擴展）**：當塞入同頁會導致組塊 $> 4$、三欄內文字級被迫低於 `11.5pt`（雙欄低於 `13.0pt`）、或留白低於 `35%` 時，**必須拆分為連續多頁並依階段 2 & 3 切換不同版型（`S1`～`S7`）**。

---

## 四、 黑盒引擎 API 簽名、`python-pptx` 防溢位與強制視覺檢查鐵律（Black-Box Engine API & QA Gate）

> [!IMPORTANT]
> **【底層引擎黑盒呼叫鐵律（Black-Box API Rule）】**：[`scripts/pptx_slide_engine.py`](../scripts/pptx_slide_engine.py) 與 [`scripts/verify_visual_outputs.py`](../scripts/verify_visual_outputs.py) 已封裝 `13.333" × 7.5"` 原生向量三區結構、微軟正黑體膠囊精確字寬計算、欄數自適應平行列槽卡片與版型防撞車驗證器。撰寫簡報生成腳本時，**請直接依下方 API 簽名 `import` 呼叫，日常執行嚴禁呼叫 `view_file` / `read_file` 讀取 `scripts/*.py` 原始碼**（除非發生執行報錯需除錯）！

```python
# === scripts/pptx_slide_engine.py & verify_visual_outputs.py Black-Box API Signatures ===
from pptx_slide_engine import (
    create_widescreen_presentation, # () -> Presentation (13.333" x 7.5")
    calc_pill_width,                # (text, font_pt=9.5, pad_in=0.22) -> float (inches, exact CJK/ASCII width)
    add_zone1_header,               # (slide, chapter_pill_text, assertion_headline, pill_bg_hex="#0284C7", headline_pt=20.5) -> None
    add_zone3_footer,               # (slide, takeaway_text, bg_hex="#0F172A", border_hex="#0284C7", font_pt=13.0) -> None
    add_bookend_slide_s0,           # (prs, badge_text, main_title, subtitle_text, kpi_cards=None, speaker_notes=None) -> slide
    draw_parallel_row_cards,        # (slide, cards_spec, left=0.50, top=1.36, total_width=12.333, height=5.12, spotlight_idx=None, body_font_pt=None, width_ratios=None) -> List[box]
    add_speaker_notes,              # (slide, notes_text) -> None
    validate_layout_sequence,       # (layouts, require_bookends=True, min_distinct=5) -> bool (Raises ValueError on collision)
)
from verify_visual_outputs import (
    render_pptx_to_pngs,            # (pptx_path, out_dir=None, width_px=1920, height_px=1080) -> List[str]
    cleanup_preview_artifacts,      # (target_dir) -> List[str] (Removes _preview_*.png, slide_*.png)
)
```

1. **獨立段落保護（No `\n` Soft Breaks）**：嚴禁以 `p.text = "...\n●..."` 塞入多行文字；必須使用 `draw_parallel_row_cards()` 或 `tf.add_paragraph()` 逐條建立獨立段落，並明確設定 `tf.word_wrap = True`、行距 `line_spacing = 1.25~1.35` 與段距 `space_after = Pt(4~6)`。
2. **轉圖強制視覺檢查（Visual Inspection Gate）**：生成 `.pptx` 後，必須調用 `render_pptx_to_pngs(pptx_path)` 轉出每頁預覽圖並呼叫 `view_file` 逐頁檢視，確認 **(1) 零文字重疊或穿框、(2) 相鄰頁版型無重複單調感、(3) 80/20 聚光燈焦點鮮明**，檢驗通過後立即調用 `cleanup_preview_artifacts(out_dir)` 清除暫存圖片檔。

