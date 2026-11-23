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

## 二、 Format C（高階簡報 `.pptx` — 向量物理結構隱喻）

- 於階段進展或雙力對比投影片（Zone 2）中，使用 `python-pptx` 原生向量幾何繪製**階梯進度台階**、**容器液面填充向量塊**或**天平雙軌對比圖**；
- 必要時可於章節破題處點綴經 `image-generator` 產出並已去背的無文字主題小精靈圖標，強化受眾長期記憶留存（`T24`），同時嚴守 Zone 1～3 斷言架構與零文字穿框底線。
