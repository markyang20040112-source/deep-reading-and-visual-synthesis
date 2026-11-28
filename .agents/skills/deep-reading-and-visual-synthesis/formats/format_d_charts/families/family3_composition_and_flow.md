# 圖表家族 3：結構佔比、雙維馬賽克、增減瀑布、階層與流向（Chart Family 3: Composition, Waterfall & Flow Spec）

> **單一職責定位（Single Responsibility）**：本檔為 Format D ⇄ E **圖表家族 3 終端細分規範**，**僅當 [`../01_plan.md`](../01_plan.md) 選定結構佔比、雙維規模×結構（馬賽克圖）、增減瀑布圖、多層階層（樹狀圖/巢狀環/旭日/圓堆）或流量移轉（桑基/弦圖）時按需載入**（須搭配核心契約 [`../02_build_core.md`](../02_build_core.md) 使用）。

```python
# === Family 3 Black-Box API Signatures (scripts/hcl_color_engine.py) ===
from hcl_color_engine import (
    plot_marimekko,          # (ax, categories, weights, sub_matrix_pct, sub_labels, colors=None, edgecolor="#FFFFFF", linewidth=1.6, show_cell_labels=True, min_pct_for_label=7.5, show_weight_header=True, weight_fmt="{:.0f}", category_color_map=None, **kwargs) -> Dict
    plot_waterfall,          # (ax, step_labels, deltas, is_total_flags=None, pos_color=None, neg_color=None, total_color="#334155", connector_color="#94A3B8", connector_linestyle="--", bar_width=0.56, value_fmt="{:+.1f}", total_fmt="{:.1f}", **kwargs) -> Dict
    bind_qualitative_colors, # (categories, allow_top4_aggregation=False, other_label="其他項目合計", registry=None) -> Dict[str, str]
    get_category_badge_tint, # (cat_or_key, category_color_map=None) -> str
    ink,                     # (bg_hex, dark_ink="#0F172A", light_ink="#FFFFFF") -> str
)
```

---

## 一、 `4+1` 聚焦堆疊長條／100% 堆疊圖與環形圖（Stacked Bar, Donut & `df_other` 消歧）

1. **單層環形圖（Donut Chart — 資料一、六、七）**：
   - **切片數量上限**：嚴格限制 **$\le 5$ 項**，由 12 點鐘方向順時針按佔比由大到小排列（`startangle=90, counterclock=False`），各扇區間以白色描邊隔離（`wedgeprops=dict(width=0.38, edgecolor="#FFFFFF", linewidth=2.0)`）。
   - **中心留白資訊利用**：必須利用環形圖中央圓孔（`ax.text(0, 0, ...)`）標註母體總規模或最核心的一句話總結數字，切勿空白浪費。
   - **超過 5 項禁令**：凡類別 $>5$ 項（或相近占比難以辨識角度差距），強制轉為 `4+1` 堆疊橫條、橫向排行圖或矩形樹狀圖。
2. **`4+1` 聚焦堆疊長條／100% 堆疊圖與 `df_other` 消歧**：
   - 當類別 $>4$ 項且原表存在 `df_other`（「其他」列）時，必須呼叫 `bind_qualitative_colors(categories, allow_top4_aggregation=True, other_label=...)` 嚴格執行 [`../02_build_core.md`](../02_build_core.md) 第二節第 1 項之雙重消歧選項（選項 1 純明細聚焦＋底註揭露原表其他 vs. 選項 2 整併命名為「其餘明細與原表其他項合計」），長尾灰固定使用 `#CBD5E1`。

---

## 二、 馬賽克雙維度佔比圖（2D Marimekko / Mekko Chart — 資料七核心亮點）

1. **解決的核心痛點**：一般 100% 堆疊長條圖把「總量 480 萬」的都會區和「總量 90 萬」的離島畫成完全一樣寬的柱子，容易誤導決策者忽略母體規模差異！馬賽克圖在單一矩形陣列中同時編碼兩個維度：
   - **X 軸柱寬**：嚴格正比於各實體的母體規模權重（$w_i = \text{Weight}_i / \sum \text{Weight} \times 100\%$）。
   - **Y 軸高度**：各實體內部的 `0% ~ 100%` 子類別結構佔比。
   - 每個小矩形塊的**面積**正好代表該子類在全局中的真實絕對體積貢獻！
2. **實作規範與黑盒呼叫**：
   ```python
   fig, ax = plt.subplots(figsize=(12.0, 6.4), dpi=300)
   fig.subplots_adjust(left=0.075, right=0.965, top=0.790, bottom=0.175)
   plot_marimekko(
       ax,
       categories=["北部都會區", "中部生活圈", "南部核心區", "東部與離島"],
       weights=[480, 290, 340, 90],
       sub_matrix_pct=[[42, 28, 18, 12], [38, 34, 18, 10], [32, 40, 20, 8], [35, 33, 24, 8]],
       sub_labels=["醇香鮮奶茶", "原葉純茶", "鮮果茶飲", "芝士奶蓋"],
       weight_fmt="{:.0f}萬杯",
   )
   ```
   - 引擎自動處理：各欄寬比例運算、每格內部自動依據 `ink(cell_hex)` 切換白字或深石板字、窄欄位自動精簡標籤（`min_pct_for_label=7.5`）、頂部顯示各區母體權重總量、以及多列圖例自動墊高子圖標題防撞間距。

---

## 三、 增減橋樑瀑布圖（Bridge Waterfall Chart — 資料二、三、七）

1. **適用場景**：清楚交代「期初數值（或整體總量）如何透過一連串正向增加因素與負向扣減因素，一步步加減收斂為期末結果（或淨值）」。
2. **實作規範與黑盒呼叫**：
   ```python
   plot_waterfall(
       ax,
       step_labels=["上期營收", "新客擴張", "客單價提升", "舊客流失", "匯率折損", "本期淨額"],
       deltas=[100.0, 28.5, 12.0, -18.5, -6.0, 116.0],
       is_total_flags=[True, False, False, False, False, True],
       value_fmt="{:+.1f}億", total_fmt="{:.1f}億",
   )
   ```
   - **色彩與連線契約**：期初／期末／小計總量柱（落地於 `Y=0`）統一採深結構灰藍（`#334155`）；正向浮動柱綁定色序 1 主色（橘）、負向浮動柱綁定色序 2 次色（藍）；相鄰柱間自動以 `#94A3B8` 水平虛線串連階梯高度，正負數值自動分別標註於柱頂與柱底。

---

## 四、 多層階層佔比圖：矩形樹狀圖、巢狀環形圖、旭日圖與圓堆圖（Hierarchy Charts）

1. **巢狀環形圖（Nested Donut — 資料六）與旭日圖（Sunburst — 資料七）**：
   - **適用情境**：主類別較少（**$\le 4$ 大主類**），且每個主類下又拆分為 2～4 個明確次級細分項的兩層從屬結構。
   - **視覺編碼與色彩同系守則**：
     - **內環**（`radius=0.66, wedgeprops=dict(width=0.30, edgecolor="#FFFFFF", lw=2.2)`）代表主類別，依固定色序綁定 `GEPHI_QUALITATIVE_HEX[0..3]`。
     - **外環**（`radius=1.00, wedgeprops=dict(width=0.32, edgecolor="#FFFFFF", lw=1.5)`）代表對應的次級細分，**嚴禁外環重新亂配不相干的彩虹色！必須從所屬主類別對應的 5 階循序色階 `GEPHI_SEQUENTIAL_SCALES["orange"|"blue"|"pink"|"green"]` 取漸層色**，使讀者一眼看出「同家族的深淺細分」！
2. **矩形樹狀圖（Treemap）與圓堆圖（Circle Packing — 資料一、二、三、五、七）**：
   - 當階層分支多達 10～40 個項目（不適合圓形角度切片）時採用。
   - **強制面積誠實守則**：無論採 Squarified Treemap 矩形分割演算法或 Circle Packing 相切圓配置，**每個區塊的面積必須嚴格正比於實際數值**（圓堆圖圓半徑 $r_i \propto \sqrt{\text{Value}_i}$），主群組間保留清晰白色隔邊（`lw=2.0`），並依 `ink(fill_hex)` 自動切換框內文字對比色，小區塊僅顯示名稱或省略移至圖註說明。

---

## 五、 動態流量與節點移轉圖：桑基流向圖與弦圖（Sankey & Chord Diagrams — 資料二、五、七）

1. **桑基流向圖（Sankey Flow Diagram）**：
   - **適用場景**：呈現多階段之間的流量分流、來源去向分配（如國中會考落點流向高中職、能源供應至部門消耗、預算來源至支出項目）。
   - **幾何繪製守則**：
     - 每一階段節點採垂直堆疊的純淨矩形柱（節點高度嚴格正比於總流量），相鄰兩階段之間以平滑三次貝茲流帶（`matplotlib.path.Path` + `Path.CURVE4` 控制點設於兩欄水平中點 `(x_mid, y0)` 與 `(x_mid, y1)`）連接。
     - 同一來源流出的各分支流帶總高度必須嚴格等於來源節點柱高（流量守恆），流帶色彩繼承來源（或主要目標）主類別色並設適度柔化明度，確保交叉流帶與直接標註數值清晰可辨。
2. **弦圖（Chord Diagram）**：僅適用於「雙向對稱互流矩陣（如縣市間通勤人口互遷、貿易雙邊進出口）」，外環弧長對應各節點總流量，內部貝茲弦帶連接起始與目標弧段，並強烈建議配合節點數 $\le 8$ 以防中央變成不可讀的毛線團。
