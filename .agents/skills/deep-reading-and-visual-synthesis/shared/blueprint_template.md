# `02_phase2_generation_blueprint.md` 樹狀主幹＋分枝範本

> **單一職責**：定義工作階段 `02_phase2_generation_blueprint.md` 標準結構，採 **「`## 0. 主幹全域錨點` ＋ 各選定格式之 `## Format X 分枝藍圖`」**。
> - **時機 A 漸進落盤**：主幹拍板 ➔ 寫 `## 0`；各選定格式 `01_plan.md` 拍板 ➔ 寫對應 `## Format X 分枝藍圖`（未選格式整節省略）；單格式交付確認 ➔ 勾 `- [x]`；全確認 ➔ 標頭改 `已交付`。
> - **Subagent 切片傳遞**：派發單格式 Subagent 時，**僅傳 `## 0. 主幹全域錨點` ＋ 該格式專屬 `## Format X 分枝藍圖`**。
> - **獨立自洽**：嚴禁貼入 Phase 1 長文或規格條文；不回寫 `01_phase1_socratic_log.md`，亦不在 `01` 或 Medium 繳交區附本檔連結。

```markdown
# 【第二階段生成藍圖與決策紀錄】<文章或數據專案主題名稱>
- **建立時間**：YYYY-MM-DD | **Phase 1 依據**：`./01_phase1_socratic_log.md`（Fast-Track 填 `./00_source_article.md`） | **狀態**：主幹確認 / 分枝規劃完成 / 執行中 / 已交付

## 0. 主幹全域錨點（Trunk Global Anchor — 派發所有 Subagent 必傳）
- **任務體裁與路由**：<實證數據 / 策略商業 / 系統架構 / 跨領域評論 / Medium 每週一圖 / 10 大分配導學>（預設分步 / 智慧直通 / Fast-Track）
- **選定格式分枝**：`[ ] D` / `[ ] A` / `[ ] B` / `[ ] C` / `[ ] E`
- **範圍取捨與排除理由**：<選定理由與邊界排除（如僅需內嵌簡圖不選 A/D；A2 無損擴展 vs. Medium 輕量路由）>
- **全域預設三支柱（各分枝可局部覆寫）**：
  - **設計光譜**：`standard_rigorous` (模式 1) / `editorial_narrative` (模式 2) / `bespoke_metaphor` (模式 3)
  - **預設筆風（`Slot 1～8`）**：`<style_id>.md`
  - **分層配色**：`chart_palette`（鎖定色票 vs. `derive_thematic_palette`）＋ `document_theme`
  - **定裝取捨理由**：<簡述為何採此配置>
- **執行與交付控制**：執行模式（Subagent 隔離 / 單執行緒備援）｜佇列 `sequential_confirm` 按 `D ➔ A ➔ B ➔ C ➔ E` 推進｜全確認後 Git 同步：`<偏好>`
- **全域客製覆寫（Global Overrides）**：內容／敘事要求：`<無或詳述>`｜視覺／排版要求：`<依標準或詳述>`

---
<!-- 以下僅保留本次勾選之 Format 分枝節 -->

## Format D 分枝藍圖（量化統計圖表）
- **分枝覆寫**：<承襲主幹 或 指定模式／筆風／色票>
- **D 內部節奏**：`batch_generation` / `step_by_step_tutor`（僅作用於 D 內部）
- **資料口徑與消歧**：`df_detail` 真實 `Min/Max`、`df_other` 選項 1/2、合法 `NA` 與前處理血統提醒
- **圖表選型與取捨**：<逐圖 `檔名 -> 圖型` ＋ 選型與捨棄備選理由 ＋ 是否另存 `*_slide.png` 供 C>
- **按需家族規格**：<僅列選定之 `formats/format_d_charts/families/family*.md`>
- **交付（`./02_outputs/` ＋ 根目錄 `02_color_registry.json`）**：
  - [ ] `<01_chart_xxx.png>` — <定位>

## Format A 分枝藍圖（視覺化知識圖譜）
- **分枝覆寫**：<承襲主幹 或 指定模式／筆風／主題>
- **分圖與 T1～T5 拓撲**：<分圖數 `01/02/03+`、各圖分支、首選拓撲與取捨理由>
- **交付（`./02_outputs/`）**：
  - [ ] `<01_article_master_structure_map.png>` — <定位>

## Format B 分枝藍圖（深度報告 ／ Medium 專欄）
- **分枝覆寫**：<承襲主幹 或 指定模式／筆風／主題>
- **體裁與路徑**：文體 1～4（A4 PDF ➔ `02_build_pdf.md`） / 文體 5（Medium `<=1,600` 字 ➔ `02_build_medium.md`，免 PDF）
- **PDF 字體（文體 1～4）**：`modern_sans` / `clreq_kaiti`（標楷體＋首行空兩格）
- **大綱與配圖分工**：<章節／七步大綱、內建 `7.44"` A4 簡圖切點或 D 配圖位置、體裁理由>
- **交付（`./02_outputs/`）**：
  - [ ] `<02_report.md / .pdf 或 02_medium_article.md>` — <定位>

## Format C 分枝藍圖（16:9 視距自適應簡報）
- **分枝覆寫**：<承襲主幹 或 指定模式／筆風／靜態或動態主題>
- **Step 1 定位與視距地板**：北極星 AST、使用情境（獨立閱覽／兩棲／口報）、$D/H$ 與 DISCAS `min_font_pt`（`>=12.0pt`）、寫作顆粒度
- **單一議題章節清單**：<逐頁單一議題與 D `*_slide.png` 連動；**不早鎖版型**，待 Step 3/4A 鎖入 `02c_slide_spec_lock.json`>
- **模式 3 Topic Art Direction DNA（僅開啟模式 3 填寫）**：`Tier 1/2/3` 與理由、唯一核心母題、動態色票模式（`light_classroom`/`dark_stage`）、`20/80` 頁面配額
- **品管偏好**：`option_c_2x2_and_high_risk`
- **交付（`./02_outputs/` ＋ 根目錄 `02c_slide_spec_lock.json`）**：
  - [ ] `<03_slides.pptx>` — <定位>

## Format E 分枝藍圖（數據儀表板）
- **分枝覆寫**：<承襲主幹 或 指定模式／筆風／色票>
- **呈現架構與圖表**：模式 A（工作台）/ B（Bento）/ C（Web+全景圖）；內部圖表與 `df_other` 消歧；模式 2/3 前端組件
- **雲端部署紀錄（部署後補齊）**：`provider`｜站點／專案名｜正式網址｜部署日期
- **交付（`./02_outputs/<dashboard_dir>/`）**：
  - [ ] `index.html`（Deploy-Ready 專案）＋（選配）靜態全景圖 `.png`
```
