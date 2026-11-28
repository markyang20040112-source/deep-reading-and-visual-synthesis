# 原子案例卡：多層向量光影 ＋ `clip_path` 液面容器圖（Liquid Container Bars）

> **分類**：`01_texture_and_container`（長度編碼具象轉譯 — RE:LAB《100元買多少鮮乳》模式）
> **父索引**：[`../../INDEX.md`](../../INDEX.md) ｜ **所屬核心契約**：[`../../../../formats/format_d_charts/02_build_core.md`](../../../../formats/format_d_charts/02_build_core.md)

---

## 一、 適用時機與防誤導邊界

- **最佳適用場景**：呈現與「容量、購買力、電量、蓄水量、達成滿額度」高度相關之單序列長度比較（如各國鮮奶購買力、水庫蓄水率、電池續航力），項目數建議 $N = 3 \sim 8$。
- **數學誠實邊界**：
  - 容器內腔液面高度必須嚴格從 `0` 起算並與數值呈 100% 線性比例；
  - 所有對比容器必須採用**完全相同之等寬外框與最大容量刻度（`max_capacity`）**，嚴禁以不等寬杯身造成體積面積誤導。

---

## 二、 黑盒 API 簽名與實作規範

```python
from hcl_color_engine import plot_liquid_container_bars
# Signature:
# plot_liquid_container_bars(
#     ax, labels, values,
#     max_capacity=None,
#     container_style="glass_cup",  # "glass_cup" | "battery" | "beaker"
#     liquid_color="#FFFFFF",
#     canvas_bg="#5BC0EB",
#     glass_edge_color="#E2F1F8",
#     value_fmt="{:.0f} ml",
#     subtitle_values=None,         # e.g. ["約 1.99 倍", ..., "基準 1.00 倍"]
#     **kwargs,
# ) -> Dict[str, Any]
```

1. **自動化向量物理光影**：引擎自動繪製等寬透明容器外框、底部加厚玻璃底座、內腔 `clip_path` 精確裁切液面高度、3D 液面頂部微橢圓半月面（Meniscus）、左右兩道半透明垂直玻璃反光高光帶（Specular Highlight Strips），並於上方自動標註實測數值與相對基準倍數 `subtitle_values`。
2. **高對比底色自適應**：若液體為純白鮮奶（`liquid_color="#FFFFFF"`），`canvas_bg` 選用清透天藍（如 `#3A8EAB` / `#5BC0EB`），函數會自動依 `relative_luminance(canvas_bg)` 切換高對比純白字或深石板字體，確保符合 WCAG AA 讀性。
