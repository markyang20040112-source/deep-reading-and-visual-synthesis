# 量化實證圖表共通核心契約（Format D ⇄ E Common Chart Core Spec — SSOT）

> **單一職責定位（Single Responsibility）**：本檔為 **Format D（量化與敘事圖表 `.png`）⇄ Format E（數據儀表板 Web + `.png`）** 在終端執行層的**共通核心契約（SSOT）**，僅負責跨所有圖表家族通用的：**① 按需圖表家族路由索引**、**② 視覺編碼誠實三鐵律與圖表 8 大元件解剖檢核表**、**③ 圖表配色設定集唯一權威定義（`qualitative_4`、`sequential_scales`、`diverging_9`、`THEMATIC_PALETTE_PRESETS` 與 `df_other` 雙重消歧）**、**④ 三層互斥分流 `assert` 防呆、單面板 `300 DPI` 黃金比例畫布與全套黑盒 API 索引**。
> - **筆風 `Slot 6` & `Slot 8` 100% 穿透**：圖表主副標題、X/Y 軸籤、氣泡標註與數值單位，受當前啟用筆風檔控制（詳見 [`visual_cognition_principles.md`](visual_cognition_principles.md)）。
> - 🔗 **雙向同步義務**：與 [`data_dashboard_spec.md`](data_dashboard_spec.md)、[`../scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py) 及 [`../scripts/gephi_palette.js`](../scripts/gephi_palette.js) 強制同步，嚴禁單邊改動。

---

## 零、 按需載入圖表家族微規格檔 ＆ 設計武器庫索引表（On-Demand Family Loading）

由 [`advisors/layer2_advisor_de_chart.md`](advisors/layer2_advisor_de_chart.md) 完成選型診斷與 [`advisors/layer3_advisor_design_style_color.md`](advisors/layer3_advisor_design_style_color.md) 完成第三層定裝後，**除本核心契約外，僅按需開啟本次明確選定之 1～2 個家族子檔**（未選中之家族 0 讀取）：

| 圖表家族／武器庫專檔 | 涵蓋圖型與專屬規範 | 開啟時機 |
| :--- | :--- | :--- |
| **[`chart_family1_ranking_and_deviation.md`](chart_family1_ranking_and_deviation.md)** | **家族 1（比較、排名、跨距與偏差）**：**資料八編輯室克里夫蘭點陣圖**、棒棒糖、排行長條、**啞鈴圖**、**斜坡圖**、**子彈圖**、**蝴蝶金字塔圖**、**柏拉圖（80/20）** | 第二層選定此家族圖型時 |
| **[`chart_family2_trend_and_comparison.md`](chart_family2_trend_and_comparison.md)** | **家族 2（時序趨勢、斷崖與同案反差）**：**空間重力斷崖折線＋直柱複合圖**、**指標極性 100% 同質化**、底部雙層 `【四字定位】`、**時期色帶＋事件折線（數據百閱）**、**配對雙柱＋剪刀差**、面積圖、範圍／甘特圖 | 第二層選定此家族圖型時 |
| **[`chart_family3_composition_and_flow.md`](chart_family3_composition_and_flow.md)** | **家族 3（結構佔比、雙維馬賽克、瀑布與流向）**：`4+1` 堆疊與環形圖、**馬賽克雙維佔比圖（Marimekko）**、**增減瀑布圖（Waterfall）**、矩形樹圖、**巢狀環／旭日／圓堆圖**、**桑基流向與弦圖** | 第二層選定此家族圖型時 |
| **[`distribution_and_density_chart_spec.md`](distribution_and_density_chart_spec.md)** | **家族 4（10 大分配與密度圖形 ＋ 背景基準疊加分面）**：直方圖（`add_halo_vline`＋`annotate_floor_extreme`）、非負截斷 KDE、ECDF、Q-Q、箱形、小提琴、山脊、2D 直方、2D 等高線、**Context Overlay 8 大鐵律**與三層指標消歧 | 第二層選定分配圖形或逐步導學時 |
| **[`chart_family5_multivariate_and_spatial.md`](chart_family5_multivariate_and_spatial.md)** | **家族 5（多維關聯、矩陣與空間複合）**：**波士頓四象限散點／氣泡矩陣**、**突出顯示熱力表**、雷達圖（$\le 3$ 組）、**主圖＋角落微型排行副卡複合構圖** | 第二層選定此家族圖型時 |
| **[`editorial_and_metaphor_armory_spec.md`](editorial_and_metaphor_armory_spec.md)** | **跨格式設計武器庫專檔**：模式 2（資料八／數據百閱編輯室 5 大技法與報告 CSS）＆ 模式 3（RE:LAB 六大編碼具象材質與 IDE 跨工具合成管線） | **僅當第三層開啟模式 2 或模式 3 時加載** |

---

## 一、 視覺編碼誠實三鐵律與圖表 8 大元件解剖檢核表（Encoding Integrity & Chart Anatomy）

### 1. 視覺編碼防誤導三鐵律（Zero-Deception Encoding Laws — 資料一、五、七、八）
1. **【鐵律 1：實心長條／面積圖零點鐵律 vs. 非零狹窄區間點陣轉換】**：
   - 凡依賴「長度或面積比例感知」之實心長條／柱狀圖與面積圖，**數值軸強制從 `0` 開始**，嚴禁截斷非零起點誇大倍數差距。
   - **唯一合法解套**：當所有實體數值遠離 `0` 且集中於高檔狹窄區間（例如資料八臺灣 20 縣市消費支出 `59.2～117.0 萬元`），欲放大細微差距時，**強制改用依賴「位置感知」之克里夫蘭點陣圖（`plot_cleveland_dot`）或啞鈴圖（`plot_dumbbell`）**！
2. **【鐵律 2：面積編碼平方根鐵律（Area $\propto$ Value, Radius $\propto \sqrt{\text{Value}}$）】**：
   - 面積是長度的平方。繪製氣泡圖、圓堆圖或方塊面積圖時，**數值必須線性映射至「面積 Area」**（即圓半徑或正方形邊長必須與 $\sqrt{\text{Value}}$ 成正比；在 Matplotlib `ax.scatter(..., s=area)` 中，`s` 單位已是面積 $\text{pt}^2$，故直接將數值線性映射至 `s` 即可，嚴禁再平方或以半徑直接對齊數值導致 4 倍視覺膨脹詐欺）。
3. **【鐵律 3：角度與圓餅／環形圖切片上限鐵律（Max 5 Slices & Center KPI）】**：
   - 圓餅圖與單層環形圖類別**嚴格限制 $\le 5$ 項**（環形圖中心留白區須置入總數或核心關鍵指標）；類別超過 5 項時，強制啟動 `4+1` 長尾聚合或轉用橫向排行長條圖、矩形樹狀圖或馬賽克圖。

### 2. 出版級圖表 8 大元件完整度檢核表（Chart Anatomy Checklist — 資料四、八）
每次生成圖表後、驗收前，依序核對以下 8 項幾何與元件完備性：
1. **圖表外框與留白呼吸區**：整體留白 $\ge 25\%$，嚴禁過高畫布上下空洞。
2. **頂部斷言主副標題區**：主標題（`16~17.5pt Bold`）為完整數據結論句；副標題（`11.2~12.5pt`）交代樣本、單位、口徑與排序邏輯。
3. **頂部圖例或基準線膠囊區**：無框單列圖例（`frameon=False`）或資料八 `add_badge_vline` 頂部帶框圓角膠囊（確保不撞及副標題）。
4. **主繪圖核心區**：單面板佔畫布總高約 **`62%–65%`**。
5. **極簡去邊框座標軸與零旋轉標籤**：隱藏頂部與右側軸線（`despine_axes`），**中文標籤 100% 水平零旋轉（禁止斜放 45°/90°）**。
6. **背景極淡輔助基準格線**：`#CBD5E1` 細虛線（`alpha=0.45~0.65`），絕不搶奪主視覺。
7. **資料數列與直接數據標註**：主角極值聚光燈高亮，節點或長條末端直接標註數值並採白色外框避讓。
8. **底部官方來源與方法論圖註**：預設採雙行精簡官方來源（1. 官方資料集網址、2. 資料涵蓋期間）；若開啟編輯室模式則呼叫 `add_editorial_footer` 繪製四層結構化底註（`資料補充 / 註 / 來源 / 提醒`）。

---

## 二、 圖表配色設定集架構與跨圖色階連動規範（Color Specification — SSOT）

> **設定集動態載入來源**：由本機 `config/user_preferences.json` 之 `color_sets.chart_palettes` 動態載入（外部新使用者透過 `build_palette_from_primary_hexes()` 由 2～4 個主色於 CIELAB 空間推導均衡色階；若第三層開啟主題語義微調，則呼叫 `derive_thematic_palette()` / `deriveThematicPalette()` 衍生主題色票）。
> **單一事實來源（SSOT）**：Python 實作強制匯入 [`../scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)，Web 前端強制載入 [`../scripts/gephi_palette.js`](../scripts/gephi_palette.js)。

### 1. 無序類別固定色序與零 Alpha 徽章淺底色（Qualitative Fixed Order & Zero-Alpha Tints）
同名類別在跨圖表、跨面板或互動篩選切換時必須維持完全相同的色碼，絕不因資料順序變動而換色：

| 色序順位 | 角色定位 | 程式變數鍵值 | 零 Alpha 徽章淺底 (`0.00`) | 跨圖表／跨視角綁定規範 |
| :---: | :---: | :---: | :---: | :--- |
| **1** | **主色 (Primary)** | `GEPHI_QUALITATIVE_HEX[0]` | `GEPHI_LIGHT_BADGE_TINTS[0]` | 第一主類別、預設單指標主視覺 |
| **2** | **次色 (Secondary)** | `GEPHI_QUALITATIVE_HEX[1]` | `GEPHI_LIGHT_BADGE_TINTS[1]` | 第二類別、雙指標對比第二維度 |
| **3** | **第三色 (Tertiary)** | `GEPHI_QUALITATIVE_HEX[2]` | `GEPHI_LIGHT_BADGE_TINTS[2]` | 第三類別 |
| **4** | **第四色 (Quaternary)** | `GEPHI_QUALITATIVE_HEX[3]` | `GEPHI_LIGHT_BADGE_TINTS[3]` | 第四類別 |
| *(收斂/缺漏)* | **長尾聚合 / 缺失值** | **`#CBD5E1`** / **`#D9D9D9`** | **`#F1F5F9`** | 類別數 $>4$ 時採「**智慧 4+1 聚焦聚合**」將第 5 名後歸入 `#CBD5E1`（**嚴禁將 5 階循序色階拿去模除循環 `idx % 5` 塗抹 30 個無序類別**！）；缺失值統一為 `#D9D9D9`。 |

- **【原表 `df_other`（「其他」列）vs. `4+1` 長尾灰柱（`#CBD5E1`）之雙重語義消歧鐵律】**：
  - **嚴禁讓原表自帶的 `其他`／`未分類` 列（`df_other`）混入前四大彩色主色柱（`GEPHI_QUALITATIVE_HEX[0..3]`），也嚴禁同屏出現兩個都叫「其他」的柱子！**
  - 當純明細 `df_detail` 類別數 $>4$ 且原表存在 `df_other` 時，依第一、二階段拍板執行二擇一：
    1. **選項 1（純明細聚焦 ＋ 圖註揭露原表其他項）**：圖表僅繪製 `df_detail` Top 4（彩色）＋ 第五類「其餘明細項目合計（`#CBD5E1`）」，底註載明*「註：不含原表未細分之『其他』項（計 XX 筆 / 占 X%）」*。
    2. **選項 2（長尾透明整併）**：將「第 5 名後長尾明細」與「原表 `其他` 列」整併為單一 `#CBD5E1` 灰柱，並透過 `bind_qualitative_colors(..., other_label="其餘明細與原表其他項合計")` 明確命名。

### 2. 四組五階循序色階（Sequential 5-Node Scales：低值淺 `0.00` $\rightarrow$ 高值深 `1.00`）

| 循序色階系列 | 適用場景 | `0.00` | `0.25` | `0.50` | `0.75` | `1.00` |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **(1) 主色循序（`orange` / `primary`）** | **預設數值尺度**、主面板／圖 1 同質漸層 | `[0]` | `[1]` | `[2]` | `[3]` | `[4]` |
| **(2) 次色循序（`blue` / `secondary`）** | **對比雙指標**、雙圖右面板／圖 2 深鑽 | `[0]` | `[1]` | `[2]` | `[3]` | `[4]` |
| **(3) 第三色循序（`pink` / `tertiary`）** | 第三維度數值分布或專題序列 | `[0]` | `[1]` | `[2]` | `[3]` | `[4]` |
| **(4) 第四色循序（`green` / `quaternary`）** | 第四維度數值分布或專題序列 | `[0]` | `[1]` | `[2]` | `[3]` | `[4]` |

- **連續數值平滑插值與正規化公式**：嚴格依 **純明細 `df_detail` 之 $p = (v - v_{\min}) / (v_{\max} - v_{\min})$ 計算**（嚴禁混入 `df_subtotal` 極值，亦嚴禁簡化為 $v / v_{\max}$），並呼叫 `get_sequential_color()` 於 CIELAB 感知空間分段線性插值。**嚴禁使用 Alpha 透明度（如 `rgba(...)` 或 `#RRGGBB20`）冒充深淺明度或徽章底色**！
- **一般雙圖並排 vs.「Medium 模式獨立單面板鐵律」（$1 + 1 > 2$ 跨檔色彩接力）**：
  - 一般報告／簡報雙面板並排（`ncols=2`）：左圖採 `(1) 主色循序 (orange)`，右圖採 `(2) 次色循序 (blue)`。
  - **Medium 每週一圖模式**：禁止 `ncols=2` 橫向雙子圖！強制產出 **1～2 張各自獨立之單面板 `300 DPI` `.png` 圖檔**——圖 1（`01_chart_hook.png`）採主色系（`GEPHI_QUALITATIVE_HEX[0]` / `orange`）、圖 2（`02_chart_drilldown.png`）切換次色系（`GEPHI_QUALITATIVE_HEX[1]` / `blue` 或雙色配對），缺失值統一 `#D9D9D9`。

### 3. 九階對稱發散色階（9-Node Symmetric Diverging Scale：中心 `#F5F6F7`）

| 尺度位置 | `0.000` | `0.125` | `0.250` | `0.375` | **`0.500`** | `0.625` | `0.750` | `0.875` | `1.000` |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **語意映射** | 負向極值(次色極深) | 負向中深 | 負向中度 | 負向輕度 | **`#F5F6F7` 中立冷灰** | 正向輕度 | 正向中度 | 正向中深 | 正向極值(主色極深) |
| **陣列索引** | `diverging[0]` | `diverging[1]` | `diverging[2]` | `diverging[3]` | **`#F5F6F7`** | `diverging[5]` | `diverging[6]` | `diverging[7]` | `diverging[8]` |

### 4. 製圖前 6 大條件與 5 大執行鐵律
- **6 項自動從《資料說明書》與 `df_detail` 預填條件**：1. 實際變數與枚舉對照；2. 數值單位；3. **剔除 `df_subtotal` 後之純明細 `df_detail` `Min / Max`**；4. 發散色階中心基準；5. 缺失值 `NA`（`#D9D9D9`）筆數；6. 超界值與 Winsorization／Binning／Imputation 血統標明。
- **5 大執行鐵律**：1. 色碼同時套用於 `colour` 與 `fill`；2. 類別嚴格按固定色序跨圖鎖定；3. 數值預設主色循序、對比／圖 2 用次色循序；4. 發散以指定中心為軸對稱映射（嚴禁二元黑白化）；5. 絕不隨機補色。

---

## 三、 黑盒引擎 API 簽名、三層分流 `assert` 防呆與黃金比例畫布標準

> [!IMPORTANT]
> **【底層引擎黑盒呼叫鐵律（Black-Box API Rule）】**：所有 Python 繪圖腳本**必須直接 `import hcl_color_engine`**，**嚴禁對 `scripts/hcl_color_engine.py` 呼叫 `read_file`（除非執行報錯需除錯）**！

```python
# === scripts/hcl_color_engine.py Complete Black-Box API Signatures ===
from hcl_color_engine import (
    # --- Core Palettes, Identity & Data Hygiene ---
    GEPHI_QUALITATIVE_HEX,              # Active 4 qualitative hex colors
    GEPHI_LIGHT_BADGE_TINTS,            # Active 4 zero-alpha 0.00 badge tints
    GEPHI_SEQUENTIAL_SCALES,            # Dict["orange"|"blue"|"pink"|"green", List[5 hex nodes]]
    GEPHI_DIVERGING_SCALE,              # List[9 hex nodes: neg extreme .. #F5F6F7 .. pos extreme]
    GEPHI_DISCRETE_NEUTRALS,            # {"diverging_center": "#F5F6F7", "na_missing": "#D9D9D9", "other_aggregated": "#CBD5E1"}
    THEMATIC_PALETTE_PRESETS,           # Dict of built-in thematic presets ("milk_tea", "forest_eco", "ocean_blue", "coffee_roast", "pineapple_tropical", ...)
    check_user_identity_and_load_prefs, # (prefs_path=None, override_git_user=None, allow_workspace_fallback=True, override_local_user=None) -> Dict
    build_palette_from_primary_hexes,   # (hex_list, palette_id="custom_cielab_palette", palette_name="Custom CIELAB Palette", sync_js_path=None) -> Dict
    derive_thematic_palette,            # (theme_preset_or_hex, sync_js_path=None, activate=False, **kwargs) -> Dict
    activate_chart_palette,             # (palette_dict_or_id, prefs_path=None) -> Dict
    export_gephi_palette_js,            # (output_path, palette_dict=None) -> str
    load_and_split_csv,                 # (csv_path, numeric_cols=None, label_cols=None, subtotal_keywords=None, other_keywords=None, known_na_tokens=None) -> (df_raw, df_detail, df_other, df_subtotal, stats_report)
    ink,                                # (bg_hex, dark_ink="#0F172A", light_ink="#FFFFFF") -> str (WCAG AA ink contrast)
    get_sequential_color,               # (value, v_min, v_max, scale="orange", discrete_steps=False, scale_key=None) -> str
    get_diverging_color,                # (value, center=0.0, max_span=None, discrete_steps=False) -> str
    bind_qualitative_colors,            # (categories, allow_top4_aggregation=False, other_label="其他項目合計") -> Dict[str, str]
    get_category_badge_tint,            # (cat_or_key, category_color_map=None) -> str
    despine_axes,                       # (ax, grid_axis="y", grid_color="#CBD5E1", grid_linestyle="--", grid_alpha=0.65, spine_color="#CBD5E1") -> None
    # --- Chart Families & Distribution Helpers ---
    plot_cleveland_dot,                 # (ax, labels, values, top_n=1, bottom_n=1, highlight_indices=None, highlight_color=None, context_color="#94A3B8", stem_color="#CBD5E1", stem_linestyle="--", stem_linewidth=1.0, value_fmt="{:.1f}", value_offset_pts=7.0, sort_values=True, ascending=True, x_padding_ratio=0.14, **kwargs) -> Dict
    plot_dumbbell,                      # (ax, labels, val_start, val_end, label_start="期初 / 基準", label_end="期末 / 現況", color_start=None, color_end=None, bar_color="#CBD5E1", bar_linewidth=3.2, dot_size=90.0, show_delta=True, delta_fmt="{:+.1f}", sort_by="end", **kwargs) -> Dict
    plot_slope_chart,                   # (ax, labels, val_t1, val_t2, t1_label="期初 (T1)", t2_label="期末 (T2)", up_color=None, down_color=None, neutral_color="#94A3B8", value_fmt="{:.1f}", linewidth=2.4, dot_size=75.0, **kwargs) -> Dict
    plot_bullet,                        # (ax, labels, actuals, targets, bands=None, band_colors=None, actual_color=None, target_color="#0F172A", bar_height=0.6, actual_height=0.28, value_fmt="{:.1f}", **kwargs) -> Dict
    plot_marimekko,                     # (ax, categories, weights, sub_matrix_pct, sub_labels, colors=None, edgecolor="#FFFFFF", linewidth=1.6, show_cell_labels=True, min_pct_for_label=7.5, show_weight_header=True, weight_fmt="{:.0f}", **kwargs) -> Dict
    plot_waterfall,                     # (ax, step_labels, deltas, is_total_flags=None, pos_color=None, neg_color=None, total_color="#334155", connector_color="#94A3B8", connector_linestyle="--", bar_width=0.56, value_fmt="{:+.1f}", total_fmt="{:.1f}", **kwargs) -> Dict
    add_halo_vline,                     # (ax, x, color=None, linestyle="--", linewidth=2.2, halo_color="#FFFFFF", halo_width=4.8, label=None, zorder=5) -> Line2D
    annotate_floor_extreme,             # (ax, x, y_floor=0.0, label_text="", dot_color=None, dot_size=46.0, arrow_height_ratio=0.14, text_offset_x=0.0, fontsize=9.5, zorder=6, label=None, color=None) -> Annotation
    compute_clipped_kde,                # (data, x_min=0.0, x_max=None, bw_method="scott", grid_size=512) -> (x_grid, density_norm, h)
    plot_clipped_kde,                   # (ax, data, x_min=0.0, x_max=None, bw_method="scott", grid_size=512, color=None, fill_color=None, fill_alpha=0.28, linewidth=2.2, label=None, zorder=3) -> (x_grid, density_norm, h)
    setup_context_overlay_grid,         # (n_panels, ncols=4, figsize_per_panel=(4.2, 3.2), dpi=300, xlim=None, ylim=None, baseline_data=None, baseline_x_min=0.0, baseline_bw="scott", baseline_color="#CBD5E1", baseline_fill_alpha=0.35, baseline_label="全體基準分布 (Context)") -> (fig, axes, bg_info)
    # --- Layer 3 Armory (Editorial Narrative & RE:LAB Bespoke Metaphor) ---
    apply_spotlight_colors,             # (values_or_labels, top_n=1, bottom_n=1, highlight_indices=None, highlight_color=None, context_color="#94A3B8", **kwargs) -> _SpotlightStyleResult
    add_badge_vline,                    # (ax, x, badge_text, color=None, linestyle="--", linewidth=2.0, badge_y_axes=1.03, x_offset_pts=0.0, zorder=6, **kwargs) -> _BadgeVLineResult
    add_editorial_footer,               # (fig, footer_lines, y_top=0.088, line_spacing=0.022, rule_color="#CBD5E1", fontsize=9.0, **kwargs) -> List[Text]
    add_regime_shading_and_events,      # (ax, regimes=None, events=None, **kwargs) -> Dict[str, List[Any]]
    add_inset_leaderboard,              # (ax, labels, values, bbox=(0.62, 0.08, 0.34, 0.32), title="", color=None, **kwargs) -> Axes
    plot_liquid_container_bars,         # (ax, labels, values, max_capacity=None, container_style="glass_cup", liquid_color="#FFFFFF", canvas_bg="#5BC0EB", glass_edge_color="#E2F1F8", value_fmt="{:.0f} ml", subtitle_values=None, **kwargs) -> Dict
    plot_masked_texture_wedge,          # (ax, pct_value, texture_img_path=None, title="", subtitle="", base_disc_color="#E2E8F0", wedge_edge_color="#FFFFFF", start_angle=90.0, clockwise=True, value_fmt=None, **kwargs) -> Dict
    plot_sprite_scatter,                # (ax, x_vals, y_vals, sprite_img_path=None, labels=None, zoom=0.18, auto_remove_white_bg=True, white_threshold=242, **kwargs) -> Dict
)
from verify_visual_outputs import (
    check_matplotlib_text_collisions,   # (fig, shrink_pt=1.5, print_report=True) -> dict (Zero-token text-on-text & canvas bounds pre-check before view_file)
)
```

1. **強制三層互斥分流 `assert` 與兩段式安全轉型**：
   - 一律透過 `load_and_split_csv()`（探測 `utf-8-sig` $\rightarrow$ `utf-8` $\rightarrow$ `cp950` $\rightarrow$ `big5`，初始 `dtype=str` 防代碼前置零遺失，先映射已知合法缺漏為 `np.nan`，再剝離 `,` 執行嚴格數值轉型）拆分並執行：
     ```python
     assert len(df_detail) + len(df_other) + len(df_subtotal) == len(df_raw), "三層互斥分流筆數不守恆！"
     ```
     **所有統計量與繪圖嚴禁混入 `df_subtotal`（100% 杜絕 Double Counting）**。
2. **單面板 `300 DPI` 黃金比例畫布與垂直空間預算（反過高空白帶護欄）**：
   - **標準直立圖（Column / Line / Scatter / Histogram / KDE / ECDF / Q-Q / Marimekko / Waterfall / 2D）**：固定 **`figsize=(12.0, 6.4)`**、`dpi=300`。
   - **橫向分位數／多列對照圖（Dot Plot / Dumbbell / Bullet / Horizontal Bar / Box / Violin / Ridgeline）**：固定 **`figsize=(12.8, 6.7)`**、`dpi=300`（僅橫向列數 $>10$ 致標籤擁擠時按列數微增高；一般單面板嚴禁無故拉高至 `7.4"~7.6"` 以上）。
   - **黃金比例垂直配置**：主繪圖區占總高 **`~62%–65%`**（`top ≈ 0.800–0.812`［含頂部膠囊時取 `0.780–0.800`］, `bottom ≈ 0.155–0.190`；標準 `left ≈ 0.075–0.095`，寬左欄橫向圖 `left ≈ 0.16–0.18`，`right ≈ 0.960–0.980`）。
   - **標準版面骨架**：
     ```python
     fig, ax = plt.subplots(figsize=(12.0, 6.4), dpi=300)  # Horizontal/Dot/Bullet: (12.8, 6.7)
     fig.subplots_adjust(left=0.075, right=0.965, top=0.808, bottom=0.188)
     fig.text(0.055, 0.962, title, fontsize=16.5, fontweight="bold", ha="left", va="top")  # Wide-left: x=0.040
     fig.text(0.055, 0.912, subtitle, fontsize=11.2, ha="left", va="top")
     ax.legend(loc="lower left", bbox_to_anchor=(-0.01, 1.012), ncol=4, frameon=False)
     fig.text(0.055, 0.058, footnote_line1, fontsize=9.2, ha="left", va="top")  # Or add_editorial_footer()
     fig.text(0.055, 0.030, footnote_line2, fontsize=9.0, ha="left", va="top")
     ```
3. **零 Emoji 鐵律（Zero-Emoji Rule）與精簡官方資料來源**：
   - Windows `Microsoft JhengHei` 遇彩色 Emoji 必現缺字方框（`□`），圖表內一律禁止 Emoji，僅用原生幾何符號（`▲`、`●`、`■`、`★`）。
   - 底部資料來源**必須寫原始官方發布機關與資料集正式名稱**（嚴禁寫成「資料來源：資料說明書」），精簡版只需附 **1. 官方資料集網址、2. 資料涵蓋期間**。
