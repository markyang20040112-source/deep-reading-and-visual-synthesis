# 原子案例卡：單體精靈圖標 ＋ PIL 自動去背 ＋ Python `AnnotationBbox` 座標散佈圖（Sprite Coordinate Scatter）

> **分類**：`01_texture_and_container`（點位與陣列編碼具象轉譯 — RE:LAB《咖啡廳數據散佈圖》模式）
> **父索引**：[`../../INDEX.md`](../../INDEX.md) ｜ **所屬核心契約**：[`../../../../formats/format_d_charts/02_build_core.md`](../../../../formats/format_d_charts/02_build_core.md)

---

## 一、 適用時機與防誤導邊界

- **最佳適用場景**：X-Y 雙變數散佈圖或 $10 \times 10$ 象形陣列圖，當每個資料點皆代表極具生活辨識度的實體（如咖啡廳、飛機、住宅、貨櫃、太陽能板），且點位總數適中（建議 $N \le 30$）不致因圖標尺寸過度堆疊遮蔽座標。
- **資料密度與防遮蔽邊界（參考 `T25`）**：
  - 若樣本數龐大（如全臺數十個縣市×多業別 $N \ge 50$）且核心任務為呈現「全樣本結構分布與氣泡規模」，**請回歸標準四象限氣泡散點圖**（見 [`../../../../formats/format_d_charts/families/family5_multivariate_and_spatial.md`](../../../../formats/format_d_charts/families/family5_multivariate_and_spatial.md)），切勿為了塞進圖標而刪減樣本點！
  - 所有精靈圖標的幾何中心必須精確錨定於真實 $(x, y)$ 座標，嚴禁手動挪移位置。

---

## 二、 兩步標準作業程序（IDE Cross-Tool SOP）與黑盒 API

```python
from hcl_color_engine import plot_sprite_scatter
# Signature:
# plot_sprite_scatter(
#     ax, x_vals, y_vals,
#     sprite_img_path=None,
#     labels=None,
#     zoom=0.18,
#     auto_remove_white_bg=True,
#     white_threshold=242,
#     **kwargs,
# ) -> Dict[str, Any]
```

1. **Step 1（呼叫 `image-generator` 生成單體精靈圖標，存於 `02_outputs/assets/<topic>_sprite.png`）**：
   - **標準 Prompt 範本**：
     > *"Single isolated top-down studio photograph of one [TOPIC ICON, e.g. roasted coffee bean], centered on a pure solid #FFFFFF white background with crisp clean edges and zero drop shadow outside the object, strictly NO text, NO labels, NO watermark."*
2. **Step 2（由 Python 自動去背並精準錨定座標）**：
   - 呼叫 `plot_sprite_scatter(ax, x_vals, y_vals, sprite_img_path="assets/<topic>_sprite.png", labels=city_names, zoom=0.16, auto_remove_white_bg=True)`。
   - 引擎自動將純白背景（`>= white_threshold`）轉為透明 Alpha 通道，再透過 `OffsetImage` ＋ `AnnotationBbox` 將圖標**精確釘在每個實體真實的 `(x, y)` 數值座標上**並附帶防衝突引線標註。
