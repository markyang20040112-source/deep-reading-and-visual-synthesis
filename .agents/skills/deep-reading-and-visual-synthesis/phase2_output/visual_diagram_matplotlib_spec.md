# 視覺化知識圖譜與概念架構圖規範（Format A: Visual Knowledge Diagram Spec）

> **單一職責定位（Single Responsibility）**：本檔專責 **Format A（視覺化知識圖譜 `.png`）** 的多圖拆分策略、五大瑞士網格拓撲（T1～T5）、主幹分叉連線與 `matplotlib`（搭配 [`generate_mindmap.py`](../scripts/generate_mindmap.py) 引擎）座標級渲染工程守則。跨格式共用的組塊階層、白話由淺入深原則與基礎色票請見 [`visual_cognition_principles.md`](visual_cognition_principles.md)。

> [!CAUTION]
> **核心鐵律**：嚴禁使用擴散生圖模型（Imagen / DALL-E）繪製中文字圖表！所有繁體中文知識圖譜必須 100% 由 Python `matplotlib` 精確渲染。

---

## 一、 認知負荷自動分圖與「零刪減多圖無損展開」鐵律

- **理論依據**：**前導組織體與宏觀結構理論（Ausubel 1968）** 與 **分段原則（Segmenting Principle, Sweller 2019）**。
- **分圖與無損展開規範（Zero-Loss Multi-Canvas Expansion）**：
  1. **單張畫布維持 3～4 個宏觀容器，嚴禁刪減分支內容**：為確保 `28" × 18.5"` 畫布上 `11.8~12.5pt` 的高可讀性，**單張圖譜**的頂層宏觀容器（Macro Zones）嚴格維持 3～4 個。當 Phase 1 Step 5 收斂出 $> 4$ 個分支（包含 `(a) 核心論證主幹分支` 與 `(b) 批判延伸與跨域遷移分支`）時，**絕對禁止為了塞入單張圖而刪減或壓縮任何延伸議題**，必須自動啟動多圖無損分流：
  2. **編號 `01` 強制為「本篇文章整體內容架構主圖（Article Master Structure Map）」**：承載 Phase 1 收斂之 **`(a) 核心論證主幹分支（3～4 個核心支柱）`**，100% 聚焦於原文從「背景痛點 $\rightarrow$ 核心診斷 $\rightarrow$ 關鍵機會/支柱 $\rightarrow$ 治理與結論」的完整脈絡，先為讀者建立單篇全域心智地圖。
  3. **編號 `02` 為「核心機制／雙軌架構深挖圖（Core Mechanism Deep-Dive Map）」**：針對文中最高價值的單一工程機制、雙腦協同管線或決策框架進行 3×3 矩陣或雙軌匯流解剖。
  4. **編號 `03+` 為「批判延伸、失效邊界與跨域遷移專題圖（Critical Boundaries, Counter-Examples & Cross-Domain Synthesis Map）」**：專門承載 Phase 1 Step 3（隱含假設失效邊界、反方對立案例、組織阻力）與 Step 4（跨領域同構基模與進階追問）所產生的 **`(b) 批判延伸與跨域遷移分支`**，確保所有延伸思辨結晶獲得獨立、飽滿的視覺化呈現！

---

## 二、 五大動態拓撲版型與主幹分叉路由（5 Topologies & Hierarchical Trunk-Fork）

繪圖前必須根據知識結構，從以下 5 種 `0～100` 瑞士網格拓撲中挑選最匹配的一種，並落實 [`visual_cognition_principles.md`](visual_cognition_principles.md) 的 **$4 \to 2 \to 3$ 階層組塊** 與 **由淺入深（淺層現象 $\rightarrow$ 中層情境 $\rightarrow$ 深層價值）白話敘事**：

| 拓撲代號與名稱 | 適用知識結構 | `0～100` 瑞士網格空間配置與連線規範 |
| :--- | :--- | :--- |
| **T1：焦點問題層級概念圖**<br>*(Top-Down Concept Map)* | 理論推導、學術論文、第一性原理拆解 | • **頂層（`Y: 76~86`）**：置中「焦點問題與核心定理樞紐」（`draw_spine_hub_module`）。<br>• **中層（`Y: 44~68`）**：並排 3～4 張「核心機制卡」，由頂層以帶謂詞膠囊之有向箭頭向下連接。<br>• **底層（`Y: 14~38`）**：對應之「實證與處方卡」，並以水平虛線標示跨分支連結。 |
| **T2：三欄雙腦／演進管線圖**<br>*(3-Column Pipeline / 3×3 Wiring)* | 雙腦協同架構、方法論步驟、痛點至處方鏈條 | • **水平 3 個垂直欄位（Columns）**：可直接調用 `draw_3x3_pipeline_grid()`，由左至右各外包一個 **Palmer 共同區域底色框（Macro Zone）**，每欄內含 3 張垂直堆疊子卡。<br>• **完整 3×3 拓撲連線**：第 1、2、3 層皆具備完整的橫向與縱向有向關係膠囊連線，清楚呈現跨層協同機制。 |
| **T3：系統動力學雙迴路圖**<br>*(System Dynamics Loop)* | 商業生態、增強／調節反饋循環、跨篇統整 | • **中央迴路區（`X: 34~66`）**：配置兩個核心實體，調用 `draw_feedback_loop_pair()` 以弧形有向箭頭連接並標註 `+ 增強 / - 調節` 謂詞膠囊。<br>• **兩側模組區（左 `X: 4~30`，右 `X: 70~96`）**：左右各配置共同區域容器連入中央。 |
| **T4：對照矩陣與雙欄架構**<br>*(Comparative / 2×2 Matrix)* | 典範轉移（舊 vs. 新）、人機分工、2×2 象限策略、批判反例邊界 | • **左右雙大區（左 `X: 4~48` vs. 右 `X: 52~96`）** 或 **中央十字四象限（`draw_2x2_matrix_quadrants()`）**。<br>• 左區採用 `danger` 警示色條，右區採用 `primary`/`success` 破局色條；中央以雙向對照膠囊橋樑逐層比較。 |
| **T5：瑞士網格全高主軸分叉圖**<br>*(Swiss Full-Spine & 4-Trunk Fork)* | 全篇全景結構總覽（現象、病因、解法、行動） | • **中央核心主軸（`X: 37~63, Y: 14.5~86.5`，`H=72.0` 全高無上下空洞）**：內嵌與 4 大分區一一對應的 **4 個核心步驟模組（`draw_spine_hub_module`）**。<br>• **4 主幹 $1 \to 2$ 分叉連線（`draw_hierarchical_trunk_fork`）**：嚴禁從中央直接拉出 8 條散亂細線；必須從中央 4 模組拉出 **4 條主幹**（於大區入口配置主幹關係膠囊），再**一分為二（$1 \to 2$ Fork）**連向區內的 2 張子卡片。<br>• **底部全寬收斂橫幅（`X: 3.5~96.5, Y: 2.0~10.2`）**。 |

---

## 三、 黑盒引擎 API 簽名與程式級渲染守則（Black-Box Engine API & Rendering Rules）

> [!IMPORTANT]
> **【底層引擎黑盒呼叫鐵律（Black-Box API Rule）】**：[`scripts/generate_mindmap.py`](../scripts/generate_mindmap.py) 已封裝所有 CJK 避頭尾折行、列槽幾何真置中與 T1～T5 拓撲組件（並自動連結 `hcl_color_engine.GLOBAL_COLOR_CONTRACT`）。撰寫繪圖腳本時，**請直接依下方 API 簽名 `import` 呼叫，日常執行嚴禁呼叫 `view_file` / `read_file` 讀取 `scripts/generate_mindmap.py` 原始碼**（除非發生執行報錯需除錯），以極大化節省 Token！

```python
# === scripts/generate_mindmap.py Black-Box API Signatures ===
from generate_mindmap import (
    THEMES,                        # Dict: "swiss_editorial" (default), "hcl_scientific", "mckinsey_executive", "nature_academic", "warm_humanist"
    configure_cjk_fonts,           # () -> None  (Sets Microsoft JhengHei / Noto Sans CJK TC)
    setup_publication_canvas,      # (figsize=(28.0, 18.5), dpi=240, theme="swiss_editorial") -> (fig, ax, theme_dict)
    draw_macro_zone,               # (ax, x, y, width, height, zone_title, theme, accent_key="primary", is_dashed=False) -> None
    draw_modern_card,              # (ax, x, y, width, title, bullets, theme, accent_key="primary", badge_text=None, fixed_height=None, font_pt=12.0) -> (x, y, w, h)
    draw_spine_hub_module,         # (ax, x, y, width, height, step_badge, title, subtitle_lines, theme=None, accent_key="primary") -> (x, y, w, h) [T1/T5]
    draw_hierarchical_trunk_fork,  # (ax, p_start, p_card1, p_card2, trunk_label, theme=None, accent_key="primary", lw=2.5) -> None [T5 1->2 Fork]
    draw_3x3_pipeline_grid,        # (ax, columns_spec, theme=None, horizontal_links=None, vertical_links=None, font_pt=12.0) -> grid_boxes[3][3] [T2]
    draw_feedback_loop_pair,       # (ax, left_box, right_box, top_loop_label, bottom_loop_label, theme=None, top_accent="primary", bottom_accent="success") -> None [T3]
    draw_2x2_matrix_quadrants,     # (ax, x_axis_label, y_axis_label, quadrants_spec, theme=None, font_pt=12.0) -> List[box] [T4]
    draw_labeled_bezier,           # (ax, p0, p3, label_text=None, theme=None, accent_key=None, width=2.3) -> None
    draw_labeled_arrow,            # (ax, p0, p1, label_text=None, theme=None, accent_key="primary", rad=0.0) -> None
    draw_canvas_header_and_footer, # (ax, title, subtitle, takeaway_title, takeaway_body, theme=None) -> None
    save_publication_figure,       # (fig, output_path, theme=None, dpi=240) -> None (Lossless PNG)
)
```

1. **畫布與大字級雙行滿版配適**：
   - 畫布固定為 `figsize=(28, 18.5)`、`dpi=240`（`ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")`，僅輸出單一高畫質無損 `.png`）。
   - **字級硬指標**：主標題 `23.5pt`、卡片內文 **`11.8pt ~ 12.5pt`**、卡片標題 `14.6pt ~ 15.0pt`、分類徽章 `10.2pt ~ 10.8pt`、分區大標題 `13.6pt`、底部橫幅標題 `14.4pt`／內文 `12.4pt`。
   - **雙行飽滿敘事（60～66 漢字／列點）**：每行約容納 34～36 個漢字；每條列點應撰寫 **60～66 字的完整白話敘事**，使其自然折為勻稱的 **2 滿行**，填滿卡片橫向寬度的 **`88%～92%`**。
2. **字型安全與全形縮排避頭尾保護**：
   - 引擎內建 `sanitize_cjk_glyphs()` 自動將微軟正黑體缺字（`➔`, `↔`, `⇄`）替換為安全字元（`→`, `×`），並以 `apply_kinsoku_shori()` 執行全形縮排避頭尾保護。
3. **Tufte 四層 Z-Order 深度分離與走廊膠囊定位**：
   - `zorder = 1`：`draw_macro_zone()`；`zorder = 2`：連線；`zorder = 3~4`：`draw_modern_card()`（內部自動以 `va="center"` 達成水平列槽幾何真置中）；`zorder = 5`：關係謂詞膠囊**必須精確落於兩張卡片之間的空白走廊中央，嚴禁壓在卡片邊框線上**。

