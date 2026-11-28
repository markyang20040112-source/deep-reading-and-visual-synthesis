# 圖表家族 5：多維關聯、四象限矩陣、熱力表與空間複合（Chart Family 5: Multivariate & Spatial Spec）

> **單一職責定位（Single Responsibility）**：本檔為 Format D ⇄ E **圖表家族 5 終端細分規範**，**僅當 [`../01_plan.md`](../01_plan.md) 選定散佈／氣泡四象限矩陣、突出顯示熱力表、雷達圖或「主圖＋角落微型排行榜副卡」空間複合圖時按需載入**（須搭配核心契約 [`../02_build_core.md`](../02_build_core.md) 使用）。

```python
# === Family 5 Black-Box API Signatures (scripts/hcl_color_engine.py) ===
from hcl_color_engine import (
    setup_chart_canvas,      # (orientation="vertical", dpi=300, figsize=None, wide_left=False, slide_mode=False, grid_axis=None, **subplots_kwargs) -> (fig, ax)
    plot_quadrant_bubble,    # (ax, x_vals, y_vals, size_vals=None, labels=None, categories=None, x_ref=None, y_ref=None, quadrant_labels=None, annotate_indices=None, annotate_top_k=4, min_bubble_area=90.0, max_bubble_area=1400.0, show_size_legend=True, size_unit="", category_color_map=None, **kwargs) -> Dict
    add_halo_vline,          # (ax, x, color=None, linestyle="--", linewidth=2.2, halo_color="#FFFFFF", halo_width=4.8, label=None, zorder=5) -> Line2D
    add_inset_leaderboard,   # (ax, labels, values, bbox=(0.62, 0.08, 0.34, 0.32), title="", color=None, **kwargs) -> Axes
    get_sequential_color,    # (value, v_min, v_max, scale="orange", discrete_steps=False, scale_key=None) -> str
    get_diverging_color,     # (value, center=0.0, max_span=None, discrete_steps=False) -> str
    derive_thematic_palette, # (theme_preset_or_hex, sync_js_path=None, activate=False, **kwargs) -> Dict
    ink,                     # (bg_hex, dark_ink="#0F172A", light_ink="#FFFFFF") -> str
    despine_axes,            # (ax, grid_axis="y", grid_color="#CBD5E1", grid_linestyle="--", grid_alpha=0.65, spine_color="#CBD5E1") -> None
)
```

---

## 一、 波士頓四象限散點／氣泡矩陣圖（BCG / 4-Quadrant Bubble Matrix — 資料一、三、五、七、`T25`）

1. **適用場景與全樣本資料密度守衛（Full-Sample Density Preservation — `T25`）**：
   - 探索兩個連續變數 $(X, Y)$ 的相關性、以氣泡大小呈現第三維度母體規模，並透過中位數／平均數或業務門檻切出四大策略象限（如市場規模 × 成長率、平均房價 × 住用率 × 住用房晚數、投入成本 × 轉換效益）。
   - **絕不為具象造型犧牲全樣本密度**：當純明細 `df_detail` 包含數十個實體（如全臺 22 縣市 × 3 業別共 `n=63`）且故事重點為揭露「全體分布集群、地板與少數天價離群值」時，**必須完整保留全數明細點繪製四象限氣泡散點圖**，嚴禁改用僅能塞入少數代表縣市的具象建物／圖標造型而掩蓋整體真實分布！
2. **面積編碼平方根鐵律（Anti-Deception Law）**：
   - 在 Matplotlib `ax.scatter(x, y, s=sizes)` 中，`s` 參數本身即代表氣泡面積（$\text{pt}^2$）。因此必須將第三維度數值 `z` **線性正規化映射至面積 `s`**（使圓半徑嚴格正比於 $\sqrt{z}$）：
     ```python
     # z_vals strictly computed from df_detail (never square z_vals!)
     z_norm = (z_arr - z_min) / max(1e-9, z_max - z_min)
     bubble_areas = 90.0 + z_norm * 1350.0
     ```
   - 並在圖表空白角落補上 **2～3 個不同大小同心圓／並排圓之規模圖例（Size Legend）**，誠實交代氣泡面積對應的真實物理量級。
3. **四象限基準線、四角象限標籤與「類別深色實心箭頭指引線」標註規範**：
   - 以 `add_halo_vline(ax, x_ref, ...)` 與白色描邊水平線 `ax.axhline(y_ref, ...)` 切出十字座標（預設取 `df_detail` 中位數或政策目標門檻）。
   - 於四個角落（`ax.transAxes` 如 `(0.03, 0.96)`, `(0.97, 0.96)`, `(0.03, 0.04)`, `(0.97, 0.04)`）按需標註 `【象限名稱】`（或於中位線旁精簡標註門檻數值）。
   - **極值標註必配「對應類別深色實心箭頭指引線」**：密集氣泡區切忌僅靠鄰近空白浮字（極易看錯歸屬點位或發生重疊）；對關鍵離群／標竿氣泡應使用 `ax.annotate(..., arrowprops=dict(arrowstyle="-|>,head_length=0.40,head_width=0.22", color=cat_edge[cat], lw=1.25, shrinkA=3, shrinkB=4), path_effects=[pe.withStroke(linewidth=3.2, foreground="#FFFFFF")])`，以對應類別深色實心箭頭精準指向目標氣泡中心，確保零重疊且歸屬一目了然。

---

## 二、 突出顯示熱力表與相關性矩陣（Highlight Table & Annotated Heatmap — 資料二、五、七）

1. **核心優勢**：同時結合「表格的精確數字查閱」與「顏色深淺的前注意熱區掃描」，適合雙類別交叉表（如縣市 × 年度指標、產業 × 風險構面）與相關係數矩陣。
2. **四大繪圖工程鐵律**：
   - **CIELAB 等距色階填色**：同向數值矩陣一律依純明細 `df_detail` 正規化後呼叫 `get_sequential_color(val, v_min, v_max, scale="orange"|"blue")`；含正負偏差或相關係數（$r \in [-1, +1]$，中心 `0.0`）一律呼叫 9 階對稱發散 `get_diverging_color(val, center=0.0, max_span=...)`。缺失值（`NA`）統一填塗 **`#D9D9D9`** 並標記 `"NA"`。
   - **自動 WCAG AA 文字反白**：每個儲存格內的精確數字顏色**強制呼叫 `ink(cell_hex)` 自動切換深石板字 `#0F172A` 或純白字 `#FFFFFF`**，確保在極深色格內依然清晰銳利！
   - **白色網格隔離與清晰區間圖例**：格子之間以 `1.5pt` 純白框線隔離；右側或上方必須附有明確標註數值區間的 Colorbar（資料七熱力圖鐵律）。

---

## 三、 多維度綜合評估雷達圖（Multi-Metric Radar / Spider Chart — 資料一、二、三、七）

1. **嚴格使用邊界（Anti-Spaghetti Guardrail）**：
   - 比較對象**嚴格限制 $\le 3$ 組**（推薦 2 組對比，如「標竿企業 vs. 產業均值」）；超過 3 組線條交錯成蜘蛛網時，強制轉用「突出顯示熱力表」或「小倍圖（Small Multiples）並排雷達」。
   - 指標維度數建議 **$5 \sim 8$ 個**（過少如 3 個變成無意義三角形，過多標籤必撞車）。
2. **同質正規化繪圖規範**：
   - 所有輻射軸必須先正規化為**方向一致的正向分數（`0～100`，越往外圈代表表現越佳／強度越高）**，禁止某些軸往外是好、某些軸往外是壞。
   - 使用 `fig.add_subplot(111, polar=True)`，以 `theta` 閉合多邊形（`angles += angles[:1]`, `vals += vals[:1]`），線寬 `lw=2.2`，內部填色壓低為極淡柔光（`alpha=0.16`）並標註圓周刻度與重點頂點分數。

---

## 四、 空間分布與「主圖＋角落微型排行副卡」複合構圖（Spatial + Inset Composite — 資料七《手搖飲密度》）

1. **設計定位**：當繪製地理區域密度分布圖（Choropleth / Hexbin / 座標散點圖）或大型總覽圖時，常有一側或角落留白（如台灣地圖的東南或西北外海區域）。利用該留白置入互補的第二視角微型排行榜，可讓單張圖的敘事厚度倍增。
2. **標準實作組合**：
   - **主繪圖區（Primary Axes）**：繪製地理面量圖、空間密度點圖或主題精靈圖標散佈圖；若開啟主題語義微調（模式 3），先呼叫 `derive_thematic_palette("milk_tea" | "forest_eco" | "ocean_blue" | ...)` 讓地圖色階貼合議題語義（如奶茶焦糖色階表現飲料店密度）。
   - **角落微型排行榜副卡（Inset Leaderboard）**：直接呼叫黑盒函數：
     ```python
     add_inset_leaderboard(
         ax,
         labels=["清心福全", "50 嵐", "CoCo 都可"],
         values=[960, 610, 480],
         bbox=(0.64, 0.08, 0.32, 0.28),
         title="全臺門市數 Top 3 品牌",
         value_fmt="{:.0f} 家",
     )
     ```
   - 確保 `bbox` 位置精準落在地理主體外圍空白處，不遮擋任何縣市輪廓或數據圓點。
