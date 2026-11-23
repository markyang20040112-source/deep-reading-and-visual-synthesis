# 原子案例卡：CIELAB 主題語義色階推導 ＋ 看板外框與跨格式沉浸裝幀（Thematic Palette & Frame）

> **分類**：`03_spatial_and_thematic`（色彩深淺與主題語義轉譯 — RE:LAB《台灣飲料店密度》模式 ＋ Format B/C/E 主題裝幀）
> **父索引**：[`../../INDEX.md`](../../INDEX.md) ｜ **所屬核心契約**：[`../../../quantitative_chart_spec.md`](../../../quantitative_chart_spec.md)

---

## 一、 適用時機與色彩科學邊界

- **最佳適用場景**：大眾傳播專題、生活消費／農業／茶飲／能源／環境／海洋等具備強烈自然物質或產業色調聯想的專題，希望從圖表、PDF 報告、簡報到互動儀表板全面貫穿統一的主題語義色彩識別。
- **CIELAB 感知均勻與對比度底線**：
  - 嚴禁手工挑選高飽和度霓虹色或以 Alpha 透明度冒充明度！所有主題色階皆須由 `derive_thematic_palette()` 於 CIELAB 感知空間等明度校正推導，並維持白底 WCAG 2.1 AA（$\ge 4.5:1$）文字對比度。

---

## 二、 跨端黑盒 API 與內建 6 大主題色階鍵值

```python
# === Python (scripts/hcl_color_engine.py) ===
from hcl_color_engine import (
    derive_thematic_palette,  # (theme_preset_or_hex, sync_js_path=None, activate=False, **kwargs) -> Dict[str, Any]
    add_inset_leaderboard,    # (ax, labels, values, bbox=(0.62, 0.08, 0.34, 0.32), title="", color=None, **kwargs) -> Axes
)
```
```javascript
// === Web Frontend (scripts/gephi_palette.js) ===
window.GephiPalette.deriveThematicPalette(presetOrHex, { activate: true });
```

1. **內建主題語義色階預設鍵值（皆經 CIELAB 感知空間等明度校正）**：
   - `"milk_tea"` / `"bubble_tea"`（奶茶焦糖棕 `#C87D55` ＋ 茶綠 `#5C8D89`）
   - `"forest_eco"` / `"matcha_forest"`（森林生態綠 `#3A7D44` ＋ 溪流藍 `#2C6E8F`）
   - `"ocean_blue"` / `"ocean_hydro"`（海洋深藍 `#0284C7` ＋ 潟湖綠 `#0D9488`）
   - `"coffee_roast"`（深焙咖啡棕 `#7F4F24` ＋ 抹茶綠 `#4A7C59`）
   - `"pineapple_tropical"` / `"agri_gold"`（熱帶金黃 `#D97706` ＋ 農產綠 `#15803D`）
   - **任意單一代表 HEX 自動推導**：傳入任意單一 HEX（如 `"#E11D48"`），由引擎透過 CIELAB 正交旋轉自動衍生 4 組均衡主色、5 階循序色階與 9 階發散色階，並可搭配 `add_inset_leaderboard()` 呈現角落 Top N 排行小卡。
2. **Format B / C / E 跨格式主題沉浸式裝幀**：
   - **Format B（PDF 報告）**：將 `derive_thematic_palette()` 衍生色注入報刊頭條頂線 `.editorial-masthead`、`.big-stat-callout` 與標題強調色，同時維持白底高對比（WCAG AA $\ge 4.5:1$）。
   - **Format C（簡報）**：將衍生主色套用於章節膠囊與核心視覺容器，搭配 `image-generator` 生成之透明主題小圖標點綴章節記憶點。
   - **Format E（互動儀表板 Web）**：於前端直接呼叫 `window.GephiPalette.deriveThematicPalette(preset, { activate: true })` 動態覆寫 CSS `:root` 變數，並可選配水平／垂直玻璃容器進度條與 $10 \times 10$ 象形陣列佔比卡。
