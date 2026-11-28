# 原子案例卡：Format A / C 空間與物理結構隱喻（Diagram & Slide Spatial Metaphors）

> **分類**：`03_spatial_and_thematic`（`0~100` 瑞士網格空間隱喻 ＆ 簡報向量物理隱喻）
> **父索引**：[`../../INDEX.md`](../../INDEX.md) ｜ **關聯規格**：[`../../../visual_diagram_matplotlib_spec.md`](../../../visual_diagram_matplotlib_spec.md) · [`../../../presentation_slide_spec.md`](../../../presentation_slide_spec.md)

---

## 一、 Format A（知識圖譜 `.png` — `0~100` 瑞士網格空間隱喻）

當第三層開啟模式 3 且文章核心論證高度契合特定空間物理關係時，於 `generate_mindmap.py` 的 `0~100` 瑞士網格畫布上實作以下三大空間隱喻（仍須 100% 遵守 $4 \to 2 \to 3$ 單畫布組塊、字級下限與零穿線鐵律）：

1. **冰山分層圖（Iceberg Anatomy — 表象 vs. 結構根因）**：
   - 繪製水平水面分界線（`Y = 56`）；
   - 水面上方（`Y: 58~88`）以清淺天藍 `draw_macro_zone` 承載「可見表象／表面症狀卡」；
   - 水面下方（`Y: 12~52`）以深海藍紫背景區承載「水面下結構根因／隱含機制卡」。
2. **階梯漏斗過濾器（Funnel Filter — 層層篩選與流失機制）**：
   - 由上而下配置寬度逐層收窄的 `draw_macro_zone`（`W = 90 -> 68 -> 46`）；
   - 兩側以斜向流失箭頭＋膠囊標註每一層的過濾淘汰因子與流失比例。
3. **雙向天平／力場對決（Force-Field Balance — 推進力 vs. 結構阻力）**：
   - 中央置入支點樞紐模組；
   - 左右兩區分別以推進力（右綠／藍）與阻力（左紅／橘）平行對應推演，確保跨區列槽水平對齊便於掃描。

---

## 二、 Format C（高階簡報 `.pptx` — 模式 3 `Tier 1 / 2 / 3` 操作細則與主題目標對齊規範）

動工前必須先於 [`../../../advisors/layer3_advisor_design_style_color.md`](../../../advisors/layer3_advisor_design_style_color.md) 完成使用者拍板之 **Topic Art Direction DNA 卡**（選定 `Tier 1 / Tier 2 / Tier 3` 與唯一核心視覺母題），嚴禁未經詢問預設硬套單一等級。

### 1. 三級漸進解鎖實作細則（`Tier 1` ➔ `Tier 2` ➔ `Tier 3`）
1. **`Tier 1`（100% 原生幾何原語 ＋ 動態主題色票）**：
   - 搭配 [`thematic_palette_frame.md`](thematic_palette_frame.md) 之 `derive_slide_theme_from_topic()` 推導主題色票，並於 `pptx_slide_engine.py` 調用 **`draw_theme_geometric_accent()` 主題幾何原語**（斜切色面 `diagonal_wedge`、極細刻度尺線 `ruler_ticks`、階段進度台階 `step_blocks`、向量天平 `vector_scale`）與巨型淡序號無框分欄打造專屬雜誌幾何誌感；
   - **全物件 100% 為 PowerPoint 原生向量與文字**，後續改字彈性最高、生成成本最低。
2. **`Tier 2`（`Tier 1` ＋ `image-generator` 無文字概念主視覺）**：
   - 在 `Tier 1` 基礎上，僅於 **封面（`F1-A`）、過場（`F1-B`）或至多 1 頁核心破題頁** 置入呼叫 `image-generator` 子代理產出（存於 `02_outputs/assets/<topic>_concept_<nn>.png`）之 **零任何文字與數字、預留乾淨負空間** 概念藝術底圖；
   - 中文斷言標題與細線一律以 PowerPoint 原生文字疊加於乾淨負空間上；**嚴禁使用無關裝飾圖或商務握手／發光大腦圖庫風格照**；中段 70%～80% 頁維持 100% 原生可編輯。
   - **`Tier 2` 彈性生圖提示詞最小骨架（保留最大主題自由度）**：呼叫 `image-generator` 子代理時僅需鎖定以下 6 項工程欄位，其餘構圖、藝術媒材與氛圍皆依每份報告主題 100% 自由發揮：
     ```text
     [Aspect] 16:9 widescreen background illustration
     [Core Motif] <取自 Topic Art Direction DNA 卡之唯一核心母題>
     [Palette HEX] <取自 Topic Art Direction DNA 卡之主題色票 HEX>
     [Negative Space] Leave clean, uncluttered negative space on the <left / right / top / bottom — 依 F1-A/F1-B/F1-C 標題與文字區所在側填寫> for overlaid typography
     [Shared Style] <同一份簡報之 1～3 張概念圖共用同一句媒材／風格描述以維持跨頁一致性>
     [Negative Constraint] Strictly NO text, NO numbers, NO letters, NO watermark or logo text
     ```
3. **`Tier 3`（`Tier 1/2` ＋ 1～2 頁核心機制頁 HTML+SVG `300 DPI` 透明視覺底層嵌入）**：
   - 僅針對原生 PowerPoint 幾何難以精準承載的 **1～2 頁最核心因果／系統隱喻**（如平滑貝茲訊號濾網漏斗、失衡天平、冰山分層切面），以 HTML/CSS+SVG 精繪透明視覺底層，並呼叫 `pptx_slide_engine.render_svg_to_png_300dpi(html_or_svg_path, out_png_path, width_px, height_px)`（優先 Playwright + Chromium `device_scale_factor=3, omit_background=True` 寫入 `300 DPI`；未安裝時自動退回本機 Chrome/Edge CLI）無損嵌入 Zone 2；
   - **原生可編輯紅線**：頁頂 Zone 1 斷言大標與旁側無框導讀／註解必須維持 PowerPoint 原生可編輯文字，且底層色票與幾何性格必須與全檔其餘原生頁一體成型。

### 2. 防花俏四條底線與品質驗證
1. **唯一核心母題**：全簡報嚴限 **`1` 個核心視覺母題**，貫穿主題 DNA，嚴禁每頁換一套不連貫的視覺隱喻。
2. **`20/80` 克制配比**：高創意表現頁（`Tier 2` 概念底圖或 `Tier 3` SVG 底層）控制在全簡報 **`<= 20%～30%`**，其餘 **`70%～80%`** 頁面採乾淨無框排版與極細線條承托，確保認知聚焦。
3. **零無關裝飾廢圖紅線**：嚴守 Bartsch & Cobern (2003) 實證底線，拒絕任何不承載結構資訊之純裝飾插圖、圓圈小徽章或發光外框。
4. **物理底線強制驗收**：所有模式 3 頁面仍須 100% 遵守 [`../../../presentation_slide_spec.md`](../../../presentation_slide_spec.md) 之 DISCAS `min_font_pt` 硬底線、拍板文案保真鐵律與方案 C 內部品管（自動列入 `high_risk_slides` 執行 `1920×1080` 滿版精檢）。
