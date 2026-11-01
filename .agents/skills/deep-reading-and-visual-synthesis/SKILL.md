---
name: deep-reading-and-visual-synthesis
description: >-
  Facilitates deep reading comprehension via a theory-grounded 5-step Socratic scaffolding and analogical encoding protocol (Phase 1),
  followed by scientifically designed, high-cognitive-absorption multi-format outputs including multi-topology Python matplotlib knowledge diagrams, 4-genre structured reports, Assertion-Evidence presentation slides, and quantitative scientific charts (Phase 2),
  with a post-session empirical skill evolution mechanism.
  Activate when a user uploads or discusses an article, business case, research paper, report, or video transcript for deep reading, critical analysis, or visual synthesis.
---

# 深度閱讀引導與視覺化知識統整 — 總路由指南与檔案地圖 (Master Router & File Map)

> [!IMPORTANT]
> **三大核心運作鐵律**：
> 1. **雙階段隔離（Default Mode）**：傳入文章時預設**只讀 [`phase1_reading/phase1_socratic_reading_guide.md`](./phase1_reading/phase1_socratic_reading_guide.md)**；第一階段進行中**嚴禁讀取 `phase2_output/`**。
> 2. **顯式跳關特例（Fast-Track Override）**：**唯有使用者明確要求跳過引導、直接生成成果**時，先將原文存入 `reading_sessions/<YYYYMMDD_主題簡稱>/00_source_article.md`，直接讀取 [`phase2_output/phase2_output_router.md`](./phase2_output/phase2_output_router.md) 產出檔案。
> 3. **靈感生命週期鐵律（Capture $\rightarrow$ Apply $\rightarrow$ Delete，嚴禁私自改檔）**：過程中產生之技能優化靈感，必須嚴格遵守本檔第四節之「紀錄、運用與刪除規則」，**絕對禁止中斷主流程或私自在背後偷改技能檔**！

---

## 🗺️ 一、 全專案檔案地圖與單一職責分工表 (File Architecture & Single Responsibility Map)

本技能庫採**「單一事實來源（SSOT）＋按需載入（Lazy Loading）」**設計，每個檔案僅負責單一明確維度，**嚴禁跨檔重複抄寫規則或一次讀取全部檔案**：

| 檔案路徑 | 唯一職責說明（Single Responsibility） | 開啟時機（When to Read） |
| :--- | :--- | :--- |
| **[`SKILL.md`](./SKILL.md)**<br>*(本檔案 — 總控台)* | 雙階段路由判定、`reading_sessions/` 歸檔結構、Git 同步規範、靈感生命週期（`_pending_skill_inspirations.md`）唯一權威定義。 | 技能啟動時預設載入。 |
| **[`phase1_reading/phase1_socratic_reading_guide.md`](./phase1_reading/phase1_socratic_reading_guide.md)** | 第一階段五步漸進式認知推進（Step 0 護欄 $\rightarrow$ Step 1 直覺提取与 Kintsch 診斷 $\rightarrow$ Step 2 理論對齊 $\rightarrow$ Step 3 雙維詰問 $\rightarrow$ Step 4 類比編碼 $\rightarrow$ Step 5 架構收斂）。 | **狀態 1**：進入第一階段閱讀互動時唯一開啟之檔案。 |
| **[`phase2_output/phase2_output_router.md`](./phase2_output/phase2_output_router.md)** | 第二階段 4 步輸出流程總控台、跨格式「動態三維視覺決策引擎（資料形式 × 敘事目的 × 長寬比配適）」。 | **狀態 2**：第一階段 Step 5 完成或使用者要求直接生成時首先開啟。 |
| **[`phase2_output/visual_cognition_principles.md`](./phase2_output/visual_cognition_principles.md)** | **四格式共通底層定律**：① $4 \to 2 \to 3$ 階層式分塊與平行列對齊；②「白話直覺先行、由淺入深（淺 $\rightarrow$ 中 $\rightarrow$ 深）」敘事鐵律；③ 跨格式適度放大字級階梯；④ 75-20-5 色彩配額與 CIELUV HCL 規則。 | 進入第二階段 Step 1 必讀（提供跨格式共通標準）。 |
| **[`phase2_output/visual_diagram_matplotlib_spec.md`](./phase2_output/visual_diagram_matplotlib_spec.md)** | **特化格式 A（知識圖譜 `.png`）**：Ausubel 宏觀主圖優先、五大拓撲（T1～T5）、4 主幹分叉連線、雙行 60～66 字飽滿配適、列槽幾何真置中（`va="center"`）、全形縮排避頭尾保護。 | 第二階段需生成【格式 A：知識圖譜】時開啟。 |
| **[`phase2_output/document_report_spec.md`](./phase2_output/document_report_spec.md)** | **特化格式 B（深度報告 `.md`/`.pdf`）**：四大體裁（B1～B4，總頁數無上限）、人類注意力起伏節奏（波谷長段敘事 $\leftrightarrow$ 波峰三線表／公式三明治）、`189mm` 擴張版心、`.nowrap` 防孤字鎖定、Chromium 四邊實線防掉框。 | 第二階段需生成【格式 B：深度報告／白皮書】時開啟。 |
| **[`phase2_output/presentation_slide_spec.md`](./phase2_output/presentation_slide_spec.md)** | **特化格式 C（高階簡報 `.pptx`）**：三區架構、八大版型動態調度（`S0`～`S7`，含依圖片長寬比與文字結構動態切換之 `S7-A` 左圖右卡／`S7-B` 上圖下卡）、首尾定錨＋中段雙因子動態分頁。 | 第二階段需生成【格式 C：高階簡報】時開啟。 |
| **[`phase2_output/quantitative_chart_spec.md`](./phase2_output/quantitative_chart_spec.md)** | **特化格式 D（量化科學圖表 `.png`）**：目的驅動差距表現（橫向推演柱線複合圖／啞鈴跨距圖）、Brewer 同質單色相明度漸層 vs. 異質色相、雙圖 1+1>2 視覺漏斗連通、零旋轉雙層 X 軸與左對齊雙欄 Y 軸。 | 第二階段需生成【格式 D：量化統計圖表】時開啟。 |
| **[`scripts/hcl_color_engine.py`](./scripts/hcl_color_engine.py)**<br>**[`scripts/generate_mindmap.py`](./scripts/generate_mindmap.py)** | 底層 Python 科學渲染引擎：`hcl_color_engine.py` 負責 CIELUV HCL 色尺與 WCAG 對比度計算；`generate_mindmap.py` 負責知識圖譜卡片、列槽置中、避頭尾斷行與主幹分叉繪製。 | 撰寫或執行第二階段 Python 繪圖腳本時引用。 |
| **[`THEORY_ARCHIVE.md`](./THEORY_ARCHIVE.md)** | 本技能背後之 35 條核心認知心理學、教育心理學、視覺感知與排版工學實證文獻封存庫。 | **狀態 3**：僅於詢問理論出處或執行 Step E3 技能進化時開啟（**日常嚴禁讀取以省流量**）。 |

---

## 🗂️ 二、 閱讀專案自動歸檔與目錄整潔規範 (`reading_sessions/`)

每次處理新文章時，於工作區根目錄建立以下結構（嚴禁存入 `.agents/skills/` 內）：
- `reading_sessions/<YYYYMMDD_主題簡稱>/00_source_article.md`：一收到文章立即原封不動存檔。
- `reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md`：即時同步更新該篇文章之思辨紀錄。
- `reading_sessions/<YYYYMMDD_主題簡稱>/02_outputs/`：**僅存放最終正式交付成果（`.png`、`.pdf`、`.md`、`.pptx`）與對應之正式生成腳本（`.py`）**。任何臨時編譯中介檔（如 `.html`、`test_*.png`、重複之 `.jpg` 或預覽圖）於驗證完畢後必須立即自動清除，保持 `02_outputs/` 100% 乾淨！
- `reading_sessions/_pending_skill_inspirations.md`：**【跨階段靈感暫存檔】**（僅在過程中出現優化靈感時動態建立，於 Step E3 寫入技能庫後**立即刪除**）。
- **Git 雙模同步與跨裝置接續規則**：
  1. **階段完成自動同步**：每當完成第二階段成果產出，或完成技能進化更新（Step E3）後，自動執行 `git add -A && git commit -m "..." && git push origin main`。
  2. **跨裝置隨時同步（On-Demand Checkpoint Sync）**：在任何時刻，只要使用者要求「先同步到 Git／我要換裝置」，AI 立即將當前進度寫入 `01_phase1_socratic_log.md`，並執行 `git add -A && git commit -m "wip(session): checkpoint sync for device handoff" && git push origin main`。

---

## 🔄 三、 技能優化靈感之「紀錄、運用與刪除」完整生命週期規範（唯一權威定義）

### 1. 📝 紀錄規則（Recording Rules — 何時記、記哪裡、怎麼記）
- **全方位靈感範疇**：凡與本技能相關的一切構想皆可納入，包含：(1) 功能與引導流程、(2) 視覺與排版設計、(3) 技能 `.md` 檔案本身的寫法、結構去重、檔案分工或 Python 腳本優化。
- **觸發與不中斷原則**：在第一階段或第二階段進行中，當使用者主動提出或 AI 察覺可優化之處時，統一寫入 `reading_sessions/_pending_skill_inspirations.md`（格式：`[編號] | [來源] | [類別] | [目標檔案] | [觀察痛點與具體改良構想]`），僅附註一句*「（💡 已記錄至靈感暫存檔，待成果交付完畢後再一併查證與升級）」*，**嚴禁中途離題查資料或私自改檔**（若正在逐項檢查格式，則待全部格式檢查完畢後統一處理）。

### 2. 🚀 運用時機（Application Timing — 三步閉環）
當最終成果已交付並驗收完畢（或使用者主動下令處理靈感）時，若 `_pending_skill_inspirations.md` 存在，依序執行：
1. **Step E1（提議與徵詢同意）**：列出暫存靈感，詢問使用者是否同意檢索學術研究與實證標準以評估升級。
2. **Step E2（查證文獻與修改方案確認）**：檢索權威論文或技術標準，回報「(1) 實證依據、(2) 預計修改之技能檔案與具體條文」，請使用者確認。
3. **Step E3（無損寫入技能庫）**：獲確認後，將文獻補入 `THEORY_ARCHIVE.md`，將精煉規則更新至對應之單一職責規範檔（避免跨檔重複與舊規矛盾）。

### 3. 🗑️ 刪除時機（Deletion Timing — 處理完畢即刻歸零）
- **刪除時機 A（使用者否決時）**：於 Step E1/E2 使用者表示不採用時，當下立即將該條靈感從暫存檔移除。
- **刪除時機 B（完成技能更新時）**：於 Step E3 將新規則寫入技能庫後，**當下立即刪除 `reading_sessions/_pending_skill_inspirations.md` 檔案**，確保暫存區 100% 歸零！
