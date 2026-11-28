# 原子案例卡：高清無文字圓盤材質 ＋ Python `Wedge` 精準扇形遮罩小倍圖（Masked Texture Wedges）

> **分類**：`01_texture_and_container`（角度與比例編碼具象轉譯 — RE:LAB《台灣鳳梨外銷中國比率》4×4 矩陣模式）
> **父索引**：[`../../INDEX.md`](../../INDEX.md) ｜ **所屬核心契約**：[`../../../../formats/format_d_charts/02_build_core.md`](../../../../formats/format_d_charts/02_build_core.md)

---

## 一、 適用時機與防誤導邊界

- **最佳適用場景**：呈現**單一核心佔比（$0\% \sim 100\%$）**隨時間或跨群組的消長軌跡，特別適合 2×4、3×4 或 4×4 小倍圖（Small Multiples）矩陣，透過直覺的實物剖面材質（如鳳梨剖面、年輪、農產品）大幅拉高視覺記憶點。
- **數學誠實與跨工具邊界**：
  - 嚴禁直接請生圖模型畫出特定百分比切片或附帶中文數字！
  - `image-generator` 僅負責產出完整 100% 正圓無文字材質；圓心角嚴格等於 $360^\circ \times p$ 的遮罩裁切與中文字排版 100% 由 Python `matplotlib.patches.Wedge` 執行。

---

## 二、 兩步標準作業程序（IDE Cross-Tool SOP）與黑盒 API

```python
from hcl_color_engine import plot_masked_texture_wedge
# Signature:
# plot_masked_texture_wedge(
#     ax, pct_value,
#     texture_img_path=None,
#     title="", subtitle="",
#     base_disc_color="#E2E8F0",
#     wedge_edge_color="#FFFFFF",
#     start_angle=90.0,
#     clockwise=True,
#     value_fmt=None,
#     **kwargs,
# ) -> Dict[str, Any]
```

1. **Step 1（呼叫 `image-generator` 生成無文字高清圓盤材質，存於 `02_outputs/assets/<topic>_texture.png`）**：
   - **標準 Prompt 範本**：
     > *"Top-down flat orthographic macro view of a single circular [TOPIC OBJECT, e.g. fresh golden pineapple cross-section slice], centered symmetrically and filling a square frame, rich natural organic fiber texture and vibrant realistic lighting, clean edge-to-edge pattern, strictly NO text, NO numbers, NO labels, NO watermark, high resolution studio photo/illustration."*
   - *(離線備援：若離線或僅需快速原型，`texture_img_path=None` 亦內建高解析程序化鳳梨剖面材質生成器。)*
2. **Step 2（由 Python 執行精準扇形遮罩與小倍圖排版）**：
   - 迴圈呼叫 `plot_masked_texture_wedge(ax, pct_value, texture_img_path="assets/<topic>_texture.png", title="2020", subtitle="外銷中國占比")`。
   - 引擎自動將材質中心裁切為 `512×512` RGBA，於底層繪製淡灰 `100%` 基準圓盤（`#E2E8F0`），再以 `matplotlib.patches.Wedge`（圓心角嚴格等於 $360^\circ \times p$）套用 `set_clip_path()` 精準裁切，完全確保 **100% 數學無誤差＋繁體中文零亂碼**。
