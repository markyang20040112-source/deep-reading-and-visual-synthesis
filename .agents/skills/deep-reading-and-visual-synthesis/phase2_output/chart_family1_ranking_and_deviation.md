# 圖表家族 1：比較、排名、跨距與目標偏差（Chart Family 1: Ranking, Span & Deviation Spec）

> **單一職責定位（Single Responsibility）**：本檔為 Format D ⇄ E **圖表家族 1 終端細分規範**，**僅當第二層選定比較排名、非零區間點陣、雙態跨距、兩期洗牌或目標偏差圖型時按需載入**（須搭配核心契約 [`quantitative_chart_spec.md`](quantitative_chart_spec.md) 使用；若第三層開啟模式 2 或 3，同步加載 [`editorial_and_metaphor_armory_spec.md`](editorial_and_metaphor_armory_spec.md)）。

```python
# === Family 1 Black-Box API Signatures (scripts/hcl_color_engine.py) ===
from hcl_color_engine import (
    plot_cleveland_dot,     # (ax, labels, values, top_n=1, bottom_n=1, highlight_indices=None, highlight_color=None, context_color="#94A3B8", stem_color="#CBD5E1", stem_linestyle="--", stem_linewidth=1.0, value_fmt="{:.1f}", value_offset_pts=7.0, sort_values=True, ascending=True, x_padding_ratio=0.14, **kwargs) -> Dict
    plot_dumbbell,          # (ax, labels, val_start, val_end, label_start="期初 / 基準", label_end="期末 / 現況", color_start=None, color_end=None, bar_color="#CBD5E1", bar_linewidth=3.2, dot_size=90.0, show_delta=True, delta_fmt="{:+.1f}", sort_by="end", **kwargs) -> Dict
    plot_slope_chart,       # (ax, labels, val_t1, val_t2, t1_label="期初 (T1)", t2_label="期末 (T2)", up_color=None, down_color=None, neutral_color="#94A3B8", value_fmt="{:.1f}", linewidth=2.4, dot_size=75.0, **kwargs) -> Dict
    plot_bullet,            # (ax, labels, actuals, targets, bands=None, band_colors=None, actual_color=None, target_color="#0F172A", bar_height=0.6, actual_height=0.28, value_fmt="{:.1f}", **kwargs) -> Dict
    add_badge_vline,        # (ax, x, badge_text, color=None, linestyle="--", linewidth=2.0, badge_y_axes=1.03, x_offset_pts=0.0, zorder=6, **kwargs) -> _BadgeVLineResult
    apply_spotlight_colors, # (values_or_labels, top_n=1, bottom_n=1, highlight_indices=None, highlight_color=None, context_color="#94A3B8", **kwargs) -> _SpotlightStyleResult
    add_editorial_footer,   # (fig, footer_lines, y_top=0.088, line_spacing=0.022, rule_color="#CBD5E1", fontsize=9.0, **kwargs) -> List[Text]
)
```

---

## 一、 編輯室克里夫蘭點陣圖（Editorial Cleveland Dot Plot — 資料八標竿規範）

1. **適用時機**：實體數 $N = 10 \sim 30$、且數值集中於**非零高檔狹窄區間**（如 20 縣市家庭消費支出介於 `59.2～117.0 萬元`），若從 `0` 畫實心長條會導致差距被擠扁、若截斷長條又違反零點鐵律——此時**點陣圖是唯一兼顧「科學誠實」與「視覺張力」的標準解法**！
2. **五大核心構圖守則**：
   - **(a) 水平引導虛線取代實心柱**：呼叫 `plot_cleveland_dot()` 自動在每個 Y 軸項目至圓點之間繪製 `#CBD5E1` 細虛線（`stem_linestyle="--"`），預設將橫軸聚焦於 `[v_min - 0.11*span, v_max + 0.16*span]`（若需強迫從 0 起算可傳 `force_zero=True`）。
   - **(b) 首尾極值聚光燈階層著色**：透過 `top_n=1, bottom_n=1`（或指定 `highlight_indices`）自動將最高與最低極值（如臺北市、花蓮縣）設為深色放大圓點（`s=110`）與粗體深色 Y 軸標籤；其餘中間縣市自動退居柔和灰藍（`#94A3B8`, `s=56`）。
   - **(c) 雙重統計基準線＋頂部帶框圓角膠囊**：呼叫 `add_badge_vline()` 同屏立起兩條統計基準（如未加權算術平均 vs. 官方戶數加權整體值），自動執行白色描邊與水平膠囊防撞避讓。
   - **(d) 點旁直接數值標註**：每個圓點右側 `7pt` 自動附帶具白色外框描邊（`patheffects.Stroke`）的直接數值標籤。
   - **(e) 四層結構化底註**：搭配 `add_editorial_footer()` 交代 `資料補充 / 註 / 來源 / 提醒`。
3. **標準實作骨架（`12.8" × 6.7"`, `300 DPI`）**：
   ```python
   fig, ax = plt.subplots(figsize=(12.8, 6.7), dpi=300)
   fig.subplots_adjust(left=0.145, right=0.965, top=0.775, bottom=0.185)
   plot_cleveland_dot(ax, labels, values, top_n=1, bottom_n=1,
                      highlight_color="#0F3A68", value_fmt="{:.1f} 萬")
   add_badge_vline(ax, unweighted_mean, f"20 縣市未加權平均\n{unweighted_mean:.2f} 萬元", color="#0284C7")
   add_badge_vline(ax, weighted_total, f"臺灣整體（官方加權）\n{weighted_total:.2f} 萬元", color="#CA6F35")
   fig.text(0.045, 0.962, title, fontsize=16.5, fontweight="bold", ha="left", va="top")
   fig.text(0.045, 0.912, subtitle, fontsize=11.2, ha="left", va="top")
   add_editorial_footer(fig, [("資料補充", "..."), ("註", "..."), ("來源", "..."), ("提醒", "...")])
   ```

---

## 二、 橫向排行長條圖與棒棒糖圖（Horizontal Ranking Bar & Lollipop Chart）

1. **嚴守零點基準鐵律**：實心長條圖（`ax.barh`）數值軸**必須固定從 `0` 開始**（`ax.set_xlim(0, max_val * 1.18)`），長條依數值由大到小降冪排列（最高置頂）。
2. **色彩與標註**：依純明細 `df_detail` 正規化位置 $p = (v - v_{\min}) / (v_{\max} - v_{\min})$ 呼叫 `get_sequential_color(v, v_min, v_max, scale="orange")`（次面板用 `"blue"`）；於長條末端直接標註粗體數值與佔比。若項目達 `10～25` 項且希望降低墨水視覺壓迫，可改用**棒棒糖圖（細實線長條幹 `lw=2.2` ＋ 末端圓點 `s=85`，同樣強制從 `0` 起算）**。

---

## 三、 啞鈴跨距圖（Dumbbell Span Plot — 資料七）

1. **適用時機**：展示同一組實體在「兩個時間點（如 2015 vs. 2025）」或「兩組條件（如男 vs. 女、預算 vs. 實支）」之間的**起訖差距跨度**。
2. **規範與呼叫**：呼叫 `plot_dumbbell(ax, labels, val_start, val_end, label_start=..., label_end=..., delta_fmt="{:+.1f}")`：
   - 嚴格綁定色序 2 次色（起點／基準）與色序 1 主色（終點／現況），中央以粗灰桿（`#CBD5E1`, `lw=3.2`）連接，右側自動加上正負方向色標註之差值 `Δ`。
   - 依現況或差值大小排序（`sort_by="end" | "start" | "delta"`），禁止散亂無序排列。

---

## 四、 坡度圖／斜坡圖（Slope Chart — 資料五、七）

1. **適用時機**：**嚴格限定僅比較前後兩個時間點（$T=2$）** 時多實體的排名洗牌、交叉超越與增減斜率（項目數建議 $4 \sim 12$ 個）。
2. **規範與呼叫**：呼叫 `plot_slope_chart(ax, labels, val_t1, val_t2, t1_label=..., t2_label=...)`：
   - 自動在 `x=0` 與 `x=1` 建立兩條垂直基準線，依方向將上升線標為主色橘、下降線標為次色藍、持平線退為結構灰 `#94A3B8`。
   - 內建一維垂直標籤碰撞鬆弛演算法（`_decollide_1d_positions`），確保左右兩側數值密集實體名稱絕不重疊。

---

## 五、 標靶圖／子彈圖（Stephen Few Bullet Graph — 資料五）

1. **適用時機**：評估各部門、指標或專案「實際達成值 vs. 目標值＋表現等級帶（劣／良／優）」，**全面取代低資訊密度的圓形速度計（Gauge）**！
2. **規範與呼叫**：呼叫 `plot_bullet(ax, labels, actuals, targets, bands=[[60, 85, 110], ...])`：
   - 底層為三階灰階背景區間帶（`#CBD5E1` $\rightarrow$ `#E2E8F0` $\rightarrow$ `#F1F5F9`），中央嵌入較細的實績深色長條（`actual_height=0.28`），目標位置以垂直深墨色粗短線（`#0F172A`, `lw=2.6`）橫切標記，右側自動標明 `實際 / 目標 (達成率%)`。

---

## 六、 雙向對稱蝴蝶金字塔圖（Butterfly Pyramid）與 80/20 柏拉圖（Pareto Chart）

1. **雙向對稱蝴蝶／人口金字塔圖（資料五、七）**：
   - 使用共中心點（或雙子圖緊貼中央共享 Y 軸類別標籤），左側群體往左延伸（以負座標繪製但將 X 軸刻度格式化為正數絕對值 `abs(x)`，綁定次色系藍）、右側群體往右延伸（綁定主色系橘），左右 X 軸上下限必須嚴格對稱（`[-M, +M]`）以防視覺傾斜詐欺。
2. **80/20 柏拉圖（Pareto Chart — 資料五）**：
   - 步驟：① 僅在純明細 `df_detail` 上按數值由大到小降冪排序繪製左 Y 軸長條（強制從 0 起算）；② 計算累積百分比 $C_k = \sum_{i=1}^k v_i / \sum v$，於右副軸（`ax2 = ax.twinx()`, `ylim(0, 105)`）繪製累積折線；③ 在 `80%` 處加上水平虛線與交叉垂直截斷虛線，醒目標示「前 $K$ 項貢獻 `80%` 核心總量」。
