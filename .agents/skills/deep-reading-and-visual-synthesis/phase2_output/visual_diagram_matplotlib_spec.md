# 視覺化知識圖譜與概念架構圖規範（Format A: Visual Knowledge Diagram Spec）

> **單一職責定位（Single Responsibility）**：本檔專責 **Format A（視覺化知識圖譜 `.png`）** 的多圖拆分策略、五大瑞士網格拓撲（T1～T5）、主幹分叉連線與 `matplotlib`（搭配 [`generate_mindmap.py`](../scripts/generate_mindmap.py) 引擎）座標級渲染工程守則，並收錄供 Format B 調用之 **A4 直向原生（`7.44"` / `189mm`）輕量流程簡圖輔助 API**。
> - **前置選型與第三層設計武器庫連動**：第二層多圖分拆與拓撲診斷由 [`advisors/layer2_advisor_a_diagram.md`](advisors/layer2_advisor_a_diagram.md) 執行；若第三層（[`advisors/layer3_advisor_design_style_color.md`](advisors/layer3_advisor_design_style_color.md)）開啟模式 2（`editorial_narrative`：80/20 聚光燈高亮與瓶頸膠囊地標）請加載 **[`editorial_narrative_spec.md`](editorial_narrative_spec.md)**；若開啟模式 3（`bespoke_metaphor`：`0~100` 畫布冰山分層／階梯漏斗／雙向天平空間隱喻）請加載 **[`creative_armory/INDEX.md`](creative_armory/INDEX.md)**。
> - **筆風與色彩底線**：全圖文字受 `Slot 1`、`Slot 4`、`Slot 5` 與 `Slot 8` 控制，分層色彩與組塊階層請見 [`visual_cognition_principles.md`](visual_cognition_principles.md)。

> [!CAUTION]
> **核心鐵律**：嚴禁使用擴散生圖模型（Imagen / DALL-E）繪製中文字圖表！所有繁體中文知識圖譜必須 100% 由 Python `matplotlib` 精確渲染。此外，**嚴禁將高密度 Format A 知識圖譜（或 A4 橫向跨頁大圖）直接嵌入 Format B PDF 報告**——Format A 與 Format B 徹底解耦（Format B 內需架構流程圖時，一律改用 A4 直向原生輕量簡圖 API）。

---

## 一、 認知負荷自動分圖與「零刪減多圖無損展開」鐵律

- **理論依據**：**前導組織體與宏觀結構理論（Ausubel 1968）** 與 **分段原則（Segmenting Principle, Sweller 2019）**。
- **分圖與無損展開規範（Zero-Loss Multi-Canvas Expansion）**：
  1. **單張畫布維持 3～4 個宏觀容器，嚴禁刪減分支內容**：為確保緊湊高可讀畫布（`23.8" × 12.6"–15.4"`）上 `16.0~16.5pt` 內文與 `13.4~14.0pt` 膠囊標籤的高可讀性，**單張圖譜**的頂層宏觀容器（Macro Zones）嚴格維持 3～4 個。當 Phase 1 Step 5 收斂出 $> 4$ 個分支（包含 `(a) 核心論證主幹分支` 與 `(b) 批判延伸與跨域遷移分支`）時，**絕對禁止為了塞入單張圖而刪減或壓縮任何延伸議題**，必須自動啟動多圖無損分流：
  2. **編號 `01` 強制為「本篇文章整體內容架構主圖（Article Master Structure Map）」**：承載 Phase 1 收斂之 **`(a) 核心論證主幹分支（3～4 個核心支柱）`**，100% 聚焦於原文從「背景痛點 $\rightarrow$ 核心診斷 $\rightarrow$ 關鍵機會/支柱 $\rightarrow$ 治理與結論」的完整脈絡，先為讀者建立單篇全域心智地圖。
  3. **編號 `02` 為「核心機制／雙軌架構深挖圖（Core Mechanism Deep-Dive Map）」**：針對文中最高價值的單一工程機制、雙腦協同管線或決策框架進行 3×3 矩陣或雙軌匯流解剖。
  4. **編號 `03+` 為「批判延伸、失效邊界與跨域遷移專題圖（Critical Boundaries, Counter-Examples & Cross-Domain Synthesis Map）」**：專門承載 Phase 1 Step 3（隱含假設失效邊界、反方對立案例、組織阻力）與 Step 4（跨領域同構基模與進階追問）所產生的 **`(b) 批判延伸與跨域遷移分支`**，確保所有延伸思辨結晶獲得獨立、飽滿的視覺化呈現！

---

## 二、 五大動態拓撲版型與主幹分叉路由（5 Topologies & Hierarchical Trunk-Fork）

繪圖前必須根據知識結構，從以下 5 種 `0～100` 瑞士網格拓撲中挑選最匹配的一種，並落實 [`visual_cognition_principles.md`](visual_cognition_principles.md) 的 **$4 \to 2 \to 3$ 階層組塊** 與 **當前啟用筆風設定檔（`Slot 1` 認知推進順序、`Slot 4` 條目開頭錨點格式、`Slot 5` 分區大標／卡片標題／有向箭頭謂詞膠囊 `Predicate_Verbs`／底部 Takeaway 橫幅語氣、以及 `Slot 8` 術語與禁用詞護欄）**：

| 拓撲代號與名稱 | 適用知識結構 | `0～100` 瑞士網格空間配置與連線規範 |
| :--- | :--- | :--- |
| **T1：焦點問題層級概念圖**<br>*(Top-Down Concept Map)* | 理論推導、學術論文、第一性原理拆解 | • **頂層（`Y: 76~86`）**：置中「焦點問題與核心定理樞紐」（`draw_spine_hub_module`）。<br>• **中層（`Y: 44~68`）**：並排 3～4 張「核心機制卡」，由頂層以帶謂詞膠囊（`13.4~14.0pt`）之有向箭頭向下連接。<br>• **底層（`Y: 14~38`）**：對應之「實證與處方卡」，並以水平虛線標示跨分支連結。 |
| **T2：三欄雙腦／演進管線圖**<br>*(3-Column Pipeline / 3×3 Wiring)* | 雙腦協同架構、方法論步驟、痛點至處方鏈條 | • **水平 3 個垂直欄位（Columns）**：直接調用 `draw_3x3_pipeline_grid()`（採 `8.6` X-unit 加寬膠囊走廊，確保 `13.4pt+` 謂詞膠囊不壓線），由左至右各外包 **Macro Zone**，每欄內含 3 張垂直堆疊子卡。<br>• **緊湊自適應高度**：3 列堆疊建議搭配 `figsize=(23.8, 12.6~13.8)` 與自然卡片高度（`target_fill=None`），杜絕卡片內部出現無謂大塊空白拉伸。 |
| **T3：系統動力學雙迴路圖**<br>*(System Dynamics Loop)* | 商業生態、增強／調節反饋循環、跨篇統整 | • **中央迴路區（`X: 34~66`）**：配置兩個核心實體，調用 `draw_feedback_loop_pair()`（內建 `FancyBboxPatch` pad 補償起訖點與 **真二次貝茲曲線頂點（Quadratic Bezier Apex）膠囊置中**）以弧形有向箭頭連接並標註 `+ 增強 / - 調節` 謂詞膠囊。<br>• **兩側模組區（如左 `X: 0.7~27.2`，右 `X: 72.8~99.3`）**：預留 `>= 6.2~7.5` X-unit 走廊連入中央。 |
| **T4：對照矩陣與雙欄架構**<br>*(Comparative / 2×2 Matrix)* | 典範轉移（舊 vs. 新）、人機分工、2×2 象限策略、批判反例邊界 | • **左右雙大區** 或 **中央十字四象限（`draw_2x2_matrix_quadrants()`）**：中央走廊強制保留 `>= 6.2~7.4` X-units，讓雙向對照謂詞膠囊（`13.4~14.0pt`）寬裕居中不碰框。<br>• 左區／負面區採用 `danger` 警示色條，右區／正面區採用 `primary`/`success` 破局色條。 |
| **T5：瑞士網格全高主軸分叉圖**<br>*(Swiss Full-Spine & 4-Trunk Fork)* | 全篇全景結構總覽（現象、病因、解法、行動） | • **中央核心主軸（`X: 40~60, Y: 10.8~89.4`）**：內嵌與 4 大分區一一對應的 **4 個核心步驟模組（`draw_spine_hub_module`）**，與兩側大區之間維持 `>= 6.8~7.7` X-unit 膠囊走廊。<br>• **4 主幹 $1 \to 2$ 分叉連線（`draw_hierarchical_trunk_fork`）**：嚴禁從中央直接拉出 8 條散亂細線；必須從中央 4 模組拉出 **4 條主幹**（於走廊中央配置 `13.4~14.0pt` 主幹關係膠囊），再**一分為二（$1 \to 2$ Fork）**連向區內的 2 張子卡片。<br>• **底部全寬收斂橫幅（`X: 2.0~98.0`）**：`draw_canvas_header_and_footer()` 自動依實體點數校準高度與 CJK 折行。 |

---

## 三、 黑盒引擎 API 簽名與程式級渲染守則（Black-Box Engine API & Rendering Rules）

> [!IMPORTANT]
> **【底層引擎黑盒呼叫鐵律（Black-Box API Rule）】**：[`scripts/generate_mindmap.py`](../scripts/generate_mindmap.py) 已封裝緊湊高可讀比例校準（`get_canvas_metrics`）、`measure_card_height`、`top_y` 精準堆疊、CJK 避頭尾折行、真二次貝茲弧頂置中、`FancyBboxPatch` pad 補償與 T1～T5 拓撲組件（並連結 `hcl_color_engine.GLOBAL_COLOR_CONTRACT`），同時提供 Format B 專用之 **A4 直向原生輕量簡圖 API**。撰寫繪圖腳本時，**請直接依下方 API 簽名 `import` 呼叫，日常執行嚴禁呼叫 `view_file` / `read_file` 讀取 `scripts/generate_mindmap.py` 原始碼**（除非發生執行報錯需除錯）！

```python
# === scripts/generate_mindmap.py Black-Box API Signatures ===
from generate_mindmap import (
    THEMES,                        # Dict: "swiss_editorial", "modern_academic_slate", "warm_editorial_ivory", "hcl_scientific", "mckinsey_executive", "nature_academic", "warm_humanist"
    DEFAULT_FIG_W, DEFAULT_FIG_H,  # 23.8, 15.4 (Compact high-legibility default; adaptive height 12.6"-15.4")
    A4_PORTRAIT_WIDTH_IN,          # 7.44 inches (= 189mm Format B printable width)
    resolve_diagram_theme,         # (theme="swiss_editorial") -> theme_dict (supports dynamic document_themes from user_preferences.json)
    configure_cjk_fonts,           # () -> None  (Sets Microsoft JhengHei / Noto Sans CJK TC)
    get_canvas_metrics,            # (ax=None, fig_width_in=None, fig_height_in=None) -> (fig_w, fig_h, pt_per_x, pt_per_y, scale_x, scale_y)
    setup_publication_canvas,      # (figsize=(23.8, 15.4), dpi=240, theme="swiss_editorial") -> (fig, ax, theme_dict)
    measure_card_height,           # (width, title, bullets, badge_text=None, font_pt=16.2, title_pt=17.4, badge_pt=13.6, line_spacing=1.50, slot_pad=0.88, fixed_height=None, ax=None) -> float
    fit_stacked_cards_to_zone,     # (card_specs, zone_y, zone_h, gap=2.1, top_offset=3.45, bot_margin=1.00, target_fill=0.91, ax=None) -> (top_y_start, heights_list)
    draw_zone_stacked_cards,       # (ax, x, width, zone_y, zone_h, cards_data, theme, gap=2.1, target_fill=0.91, distribute_gap_if_unfilled=False) -> (boxes, fill_ratio)
    box_edge_point,                # (box, side, pad=0.20, frac=0.5, ax=None) -> (px, py) [FancyBboxPatch pad-compensated anchor]
    draw_macro_zone,               # (ax, x, y, width, height, zone_title, theme, accent_key=None, is_dashed=False, font_pt=16.0) -> None
    draw_modern_card,              # (ax, x, y, width, title, bullets, theme, accent_key="primary", badge_text=None, fixed_height=None, font_pt=16.2, title_pt=17.4, badge_pt=13.6, line_spacing=1.50, slot_pad=0.88, top_y=None) -> (x, y, w, h)
    draw_spine_hub_module,         # (ax, x, y, width, height, step_badge, title, subtitle_lines, theme=None, accent_key="primary", title_pt=16.6, badge_pt=13.8, subtitle_pt=14.0) -> (x, y, w, h) [T1/T5]
    draw_hierarchical_trunk_fork,  # (ax, p_start, p_card1, p_card2, trunk_label, theme=None, accent_key="primary", lw=2.4, font_pt=13.8) -> None [T5 1->2 Fork]
    draw_3x3_pipeline_grid,        # (ax, columns_spec, theme=None, horizontal_links=None, vertical_links=None, font_pt=16.0, title_pt=16.8, badge_pt=13.4, pill_pt=13.4) -> grid_boxes[3][3] [T2]
    draw_feedback_loop_pair,       # (ax, left_box, right_box, top_loop_label, bottom_loop_label, theme=None, top_accent="primary", bottom_accent="success", rad=-0.34, font_pt=13.4, box_pad=0.22) -> (top_apex_y, bot_apex_y) [T3]
    draw_2x2_matrix_quadrants,     # (ax, x_axis_label, y_axis_label, quadrants_spec, theme=None, font_pt=16.2, title_pt=17.2, badge_pt=13.6) -> List[box] [T4]
    draw_labeled_bezier,           # (ax, p0, p3, label_text=None, theme=None, accent_key=None, width=2.2, alpha=0.88, font_pt=13.6) -> None
    draw_labeled_arrow,            # (ax, p0, p1, label_text=None, theme=None, accent_key="primary", rad=0.0, font_pt=13.6) -> None
    draw_canvas_header_and_footer, # (ax, title, subtitle, takeaway_title, takeaway_body=None, theme=None, title_pt=25.5, subtitle_pt=14.8, banner_title_pt=16.0, banner_body_pt=14.6) -> None
    save_publication_figure,       # (fig, output_path, theme=None, dpi=240) -> None (Lossless PNG)
    # --- A4-Portrait-Native Lightweight Diagram Helpers (For Format B Reports, 7.44" / 189mm, 300 DPI) ---
    setup_a4_portrait_canvas,      # (height_in=2.30, dpi=300, theme="swiss_editorial") -> (fig, ax, theme_dict)
    draw_a4_node_box,              # (ax, x, y, w, h, badge, title, lines=None, theme=None, accent_key="primary", badge_pt=8.8, title_pt=10.2, line_pt=8.4) -> (x, y, w, h)
    draw_a4_arrow,                 # (ax, p0, p1, label=None, theme=None, accent_key="primary", rad=0.0, label_dy=8.5, font_pt=8.0) -> None
    save_a4_portrait_figure,       # (fig, output_path, theme=None, dpi=300) -> None
)
from verify_visual_outputs import (
    check_matplotlib_text_collisions, # (fig, shrink_pt=1.5, print_report=True) -> dict (Zero-token text-on-text & canvas bounds pre-check before view_file)
)
```

1. **緊湊高可讀畫布與自適應高度（Compact High-Legibility Canvas & Snug Zone Wrapping）**：
   - 標準畫布採 `figsize=(23.8, 15.4)`（`dpi=240`，`ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")`，僅輸出單一高畫質無損 `.png`）。
   - **依密度動態微調畫布高度（`12.6"–15.4"`）**：2 列卡片結構採 `14.8"–15.4"`（搭配 `fit_stacked_cards_to_zone(..., target_fill=0.91)` 讓 Macro Zone 填滿 `89%–92%`）；3 列較緊湊結構或機制圖可下調畫布高度至 **`12.6"–13.8"`** 並傳入 `target_fill=None` 保持卡片自然高度，讓 Macro Zone 緊密包覆內容，徹底消除死板灰白／米色空白帶與卡片內部空白拉伸。
   - **高可讀字級硬指標**：主標題 `25.0~26.0pt Bold`、副標題 `14.5~15.5pt Bold`、Macro Zone 分區標題 `15.5~16.5pt Bold`、卡片標題 **`16.6~17.5pt Bold`**、卡片內文 **`16.0~16.5pt`**（行距 **`1.48~1.52×`**）、底部橫幅標題 `16.0~16.2pt Bold`／內文 `14.5~15.0pt`。
   - **放大雙重圓角小方框（Enlarged Badge & Predicate Pills）**：**無論是卡片分類徽章（`badge_text`）或箭頭／連線關係謂詞膠囊（`trunk_label`、`label_text`），字級全面放大至 `13.4~14.0pt Bold`**（預設 `13.6~13.8pt`），確保縮圖或螢幕預覽時所有關係動詞與標籤依然一清二楚。
   - **資訊量無損雙行敘事（~60–66 漢字／列點）**：不得以刪減關鍵資訊來遷就大字級！透過緊湊畫布比例與寬裕卡片寬度，每條列點依筆風檔（`Slot 1` 認知推進順序與 `Slot 4` 開頭錨點格式）維持 **~52–66 漢字的完整資訊密度**（雙欄寬卡 60～66 字、三欄緊湊卡 50～56 字），自然折為勻稱的 **2 滿行**（填滿卡片橫向寬度的 `88%–92%`）。
2. **幾何防撞與精準錨定工程守則**：
   - **`top_y` 堆疊＋窄卡自動疊層標題**：使用 `draw_zone_stacked_cards()` 或 `measure_card_height()` + `draw_modern_card(..., top_y=...)` 由上而下精準定位；當窄卡徽章與標題無法同列時，引擎會自動切換雙層標題並校正卡片總高，絕不發生徽章壓字。
   - **加寬膠囊走廊（`>= 6.2–7.4` X-units）**：所有承載 `13.4~14.0pt` 關係謂詞膠囊的垂直或水平走廊，淨寬至少保留 `6.2–7.4` X-units（建議 `7.4–8.6` X-units）。
   - **Pad 補償與真弧頂置中**：使用 `box_edge_point(box, side, pad=0.20)` 補償 `FancyBboxPatch` 外擴邊距，且 `draw_labeled_arrow()` / `draw_feedback_loop_pair()` 會自動將謂詞膠囊精確置中於二次貝茲曲線真實頂點（Apex），杜絕膠囊懸空漂移或壓線。
3. **字型安全、全形縮排避頭尾與 Z-Order 分層**：
   - 引擎內建 `sanitize_cjk_glyphs()`（替換微軟正黑體缺字並杜絕彩色 Emoji）與 `apply_kinsoku_shori()`（全形縮排避頭尾保護）；Z-order 嚴格分層為 `zorder=1`（Macro Zone）、`2`（連線）、`3~4`（卡片與槽位數學置中）、`5`（關係謂詞膠囊）。
4. **Format B 專用 A4 直向原生輕量簡圖規範（`7.44"` / `189mm`）**：
   - 僅供 Format B PDF 報告嵌入流程或概念架構時調用 `setup_a4_portrait_canvas()`、`draw_a4_node_box()`、`draw_a4_arrow()`、`save_a4_portrait_figure()`：畫布寬度鎖定 `7.44"`（`300 DPI`），節點僅放精簡關鍵詞與短標籤（真實字級 **`8.5–10.8pt`**），**嚴禁塞入長篇條列散文**（所有完整敘事與對比矩陣一律留在 Format B 原生 HTML 散文與三線表中）。
