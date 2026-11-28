# 原子案例卡：CIELAB 主題語義色階推導 ＋ 看板外框與跨格式沉浸裝幀（Thematic Palette & Frame）

> **分類**：`03_spatial_and_thematic`（色彩深淺與主題語義轉譯 — RE:LAB《台灣飲料店密度》模式 ＋ Format B/C/E 主題裝幀）
> **父索引**：[`../../INDEX.md`](../../INDEX.md) ｜ **所屬核心契約**：[`../../../../formats/format_d_charts/02_build_core.md`](../../../../formats/format_d_charts/02_build_core.md) · [`../../../../formats/format_c_slides/02_build.md`](../../../../formats/format_c_slides/02_build.md)

---

## 一、 適用時機與色彩科學邊界

- **最佳適用場景**：大眾傳播專題、生活消費／農業／茶飲／能源／環境／海洋等具備強烈自然物質或產業色調聯想的專題，希望從圖表、PDF 報告、簡報到互動儀表板全面貫穿統一的主題語義色彩識別。
- **CIELAB 感知均勻與對比度底線**：
  - 嚴禁手工挑選高飽和度霓虹色或以 Alpha 透明度冒充明度！所有主題色階皆須由 `derive_thematic_palette()` 於 CIELAB 感知空間等明度校正推導，並維持白底 WCAG 2.1 AA（$\ge 4.5:1$）文字對比度。

---

## 二、 跨端黑盒 API 與內建 5 大主題語義色階（9 組鍵值別名）

```python
# === Python (scripts/hcl_color_engine.py) ===
from hcl_color_engine import (
    derive_thematic_palette,        # (theme_preset_or_hex, sync_js_path=None, activate=False, **kwargs) -> Dict[str, Any]
    derive_slide_theme_from_topic,  # (topic_or_hex, mode="light_classroom"|"dark_stage", **kwargs) -> Dict[str, str] (CIELAB PPT document_theme + WCAG AA >= 4.5:1)
    add_inset_leaderboard,          # (ax, labels, values, bbox=(0.62, 0.08, 0.34, 0.32), title="", color=None, **kwargs) -> Axes
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
   - **Format C（簡報動態主題色票契約 — `derive_slide_theme_from_topic()`）**：
     - Format C 開啟模式 3 或需主題化色票時，**禁止生硬套用千篇一律的商務藍或手工亂挑暗底配暗字**；一律呼叫 **`derive_slide_theme_from_topic(topic_or_hex, mode=...)`**，依內建 5 大主題語義鍵（9 組別名）或任意單一代表 HEX 在 CIELAB 空間衍生完整相容 `pptx_slide_engine.py`（及 `build_slide_design_tokens()`）的 `document_theme` 鍵值字典。
     - **雙場景模式與對比度硬底線**：預設採 **「開燈教室淺底安全組（`mode="light_classroom"`）」**，僅於高張力暗場演講／Pitch 啟用 **「可控深場模式（`mode="dark_stage"`）」**；所有前景文字與背景色組強制通過 **`wcag_contrast() >= 4.5:1`** 檢核，並配合 [`diagram_spatial_metaphors.md`](diagram_spatial_metaphors.md) 之 `Tier 1 / 2 / 3`、唯一核心母題與 `20/80` 克制紅線。
   - **Format E（互動儀表板 Web）**：於前端直接呼叫 `window.GephiPalette.deriveThematicPalette(preset, { activate: true })` 動態覆寫 CSS `:root` 變數，並可選配水平／垂直玻璃容器進度條與 $10 \times 10$ 象形陣列佔比卡。
