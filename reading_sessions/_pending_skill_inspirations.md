# 跨階段技能優化靈感暫存檔 (_pending_skill_inspirations.md)

| 編號 | 來源 | 類別 | 目標檔案 | 觀察痛點與具體改良構想 |
| :--- | :--- | :--- | :--- | :--- |
| INS-01 | 使用者回饋 + AI 診斷 | 視覺與排版設計 / Python 腳本優化 | `phase2_output/quantitative_chart_spec.md`, `scripts/generate_mindmap.py` | Windows `Microsoft JhengHei`（微軟正黑體）不支援彩色 Emoji 字元（如 `⚠️` U+26A0、`🟢` U+1F7E2、`🔴` U+1F534），在 `matplotlib` 繪製 Format D 量化圖表時會渲染為方框亂碼（Tofu Box `□`）。應在 `quantitative_chart_spec.md` 明確禁止於 `matplotlib` 圖表中使用 Emoji，統一規定改用微軟正黑體原生支援之幾何符號（`▲`、`●`、`■`、`★`），並擴充 `sanitize_cjk_glyphs()` 自動攔截替換常見 Emoji，同時規定陡峭折線下降節點的數值標籤應向右微偏（`x + 0.14, ha="left"`）以防折線穿過數字。 |
| INS-02 | 使用者回饋 | 視覺與排版設計 | `phase2_output/quantitative_chart_spec.md` | 當圖表旨在呈現「模型表象信心很高、但實際模型效用稀爛」的預期與現實反差時，單一序列折線圖無法直觀呈現同一案例內的「高信心 vs. 低效用」對比。應於 `quantitative_chart_spec.md` 新增「配對雙柱＋剪刀差落差帶（Paired Dual-Bar & Gap Callout Chart）」規範：每個案例同時並排繪製「表象信心柱（左）」與「實際效用柱（右）」，並於兩柱間標註垂直雙向落差箭頭（`Δ = -XX%`），一目了然凸顯差距。 |
