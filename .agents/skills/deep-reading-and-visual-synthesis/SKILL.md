---
name: deep-reading-and-visual-synthesis
description: >-
  Facilitates deep reading comprehension via a theory-grounded 5-step Socratic scaffolding and analogical encoding protocol (Phase 1),
  followed by scientifically designed, high-cognitive-absorption multi-format outputs including multi-topology Python matplotlib knowledge diagrams, 4-genre structured reports, and Assertion-Evidence presentation slides (Phase 2),
  with a post-session empirical skill evolution mechanism.
  Activate when a user uploads or discusses an article, business case, research paper, report, or video transcript for deep reading, critical analysis, or visual synthesis.
---

# 深度閱讀引導與視覺化知識統整 — 總路由指南 (Master Router)

> [!IMPORTANT]
> **三大核心運作鐵律**：
> 1. **雙階段隔離（Default Mode）**：傳入文章時預設**只讀 `phase1_reading/phase1_socratic_reading_guide.md`**；第一階段進行中**嚴禁讀取 `phase2_output/`**。
> 2. **顯式跳關特例（Fast-Track Override）**：**唯有使用者明確要求跳過引導、直接生成成果**時，先將原文存入 `reading_sessions/<YYYYMMDD_主題簡稱>/00_source_article.md`，直接讀取 `phase2_output/phase2_output_router.md` 產出檔案。
> 3. **靈感生命週期鐵律（Capture $\rightarrow$ Apply $\rightarrow$ Delete，嚴禁私自改檔）**：過程中產生之技能優化靈感，必須嚴格遵守下方「紀錄規則、運用時機與刪除時機」，**絕對禁止中斷主流程或私自在背後偷改技能檔**！

---

## 🗂️ 閱讀專案自動歸檔結構 (`reading_sessions/`)

每次處理新文章時，於工作區根目錄建立以下結構（嚴禁存入 `.agents/skills/` 內）：
- `reading_sessions/<YYYYMMDD_主題簡稱>/00_source_article.md`：一收到文章立即原封不動存檔。
- `reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md`：即時同步更新該篇文章之思辨紀錄。
- `reading_sessions/<YYYYMMDD_主題簡稱>/02_outputs/`：存放第二階段生成之圖譜、腳本、報告或簡報。
- `reading_sessions/_pending_skill_inspirations.md`：**【跨階段靈感暫存檔】**（僅在過程中出現優化靈感時動態建立，處理完畢後**立即刪除**，不污染文章知識庫）。
- **Git 自動同步規則（Git Auto-Sync）**：每當完成一篇閱讀專案之第二階段資料生成（`reading_sessions/<YYYYMMDD_主題簡稱>/`），或完成技能檔案之進化更新（Step E3）後，AI 必須自動於工作區根目錄執行 `git add -A`、`git commit -m "<清晰的更新摘要>"` 與 `git push origin main`，將最新生成的閱讀資產與技能改動同步推送至遠端 GitHub 倉庫（`https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis.git`）。

---

## 🗺️ 按需載入路由表 (When to Open What)

| 當前狀態 | 唯一應開啟之檔案 | 職責說明 |
| :--- | :--- | :--- |
| **狀態 1：進入第一階段**<br>*(預設閱讀與思辨互動)* | **[phase1_socratic_reading_guide.md](./phase1_reading/phase1_socratic_reading_guide.md)** | 建立 `00` 原文檔與 `01` 紀錄檔，執行五步漸進式認知推進流程（Step 0 ~ Step 5）。 |
| **狀態 2：進入第二階段**<br>*(Step 5 完成 或 顯式要求直接生成)* | **[phase2_output_router.md](./phase2_output/phase2_output_router.md)** | 讀取共通視覺科學規範與單一指定格式規範（圖譜 / 報告 / 簡報），輸出至 `02_outputs/`。 |
| **狀態 3：詢問學術依據 或 執行技能進化**<br>*(僅查詢理論出處 或 Step E3 更新文獻)* | **[THEORY_ARCHIVE.md](./THEORY_ARCHIVE.md)** | 查閱或擴充本技能背後之認知心理學與設計科學實證文獻庫（日常執行嚴禁讀取以省流量）。 |

---

## 🔄 技能優化靈感之「紀錄、運用與刪除」完整生命週期規範

### 1. 📝 紀錄規則（Recording Rules — 何時記、記哪裡、怎麼記）
- **全方位靈感範疇（All-Encompassing Scope）**：靈感**不限於功能或理論改動**，凡是與本技能相關的一切構想皆可納入，包含：
  1. **功能與引導流程**：閱讀提問策略、跨領域思辨方法、新輸出格式或 Python 腳本功能。
  2. **視覺與排版設計**：色彩配置、字體工學、圖譜拓撲、報告或簡報版面細節。
  3. **技能檔案本身的寫法與架構編排（Meta-Skill Architecture）**：`.md` 規範檔的提示詞寫法（Prompting）、格式編排、檔案拆分與路由邏輯、Token 流量壓縮或提升 AI 讀取效率之工程優化。
- **觸發時機**：在第一階段或第二階段進行中，當**(A) 使用者主動提出**想法，或 **(B) AI 自己察覺**上述任何維度有可優化之處時。
- **獨立暫存位置**：統一寫入 `reading_sessions/_pending_skill_inspirations.md`（與單篇文章的 `01` 思辨筆記分離，避免污染文章紀錄）。
- **標準紀錄格式**：每條靈感簡明記錄：`[編號] | [來源：使用者 / AI] | [靈感類別：功能流程 / 視覺設計 / 技能檔寫法與編排] | [目標檔案] | [觀察痛點與具體改良構想]`。
- **不中斷原則**：寫入暫存檔後，僅以括號附註一句：*「（💡 已將此技能優化靈感記錄至暫存檔，待本次閱讀與產出全部完成後再與您討論）」*，隨即繼續執行當前步驟，**嚴禁中途離題查資料或改檔**。

### 2. 🚀 運用時機（Application Timing — 何時喚醒與三步執行）
- **唯一喚醒時機**：當【第二階段】最終成果已存入 `02_outputs/` 並交付使用者、**整套閱讀與生成流程正式結束時**（或使用者主動下令現在處理靈感時），AI 檢查 `reading_sessions/_pending_skill_inspirations.md` 是否存在。若存在，立即啟動以下三步（每步皆須使用者確認）：
  1. **Step E1（提議與徵詢同意）**：列出暫存檔中的靈感（若為 AI 靈感須說明理由），詢問使用者：*「請問您是否同意我針對這項靈感去檢索相關學術研究與實證資料，來評估如何升級技能？（或選擇不採用並直接刪除）」*
  2. **Step E2（查證文獻與修改方案確認）**：獲同意後，檢索有憑有據之權威論文或設計標準，向使用者回報**「(1) 查證依據、(2) 預計修改之技能檔案與具體規則條文」**，請使用者確認。
  3. **Step E3（無損瘦身寫入技能庫）**：獲確認後，將完整文獻出處補入 `THEORY_ARCHIVE.md`，並將高密度執行指令更新至對應之 `phase1` 或 `phase2` 規範檔。

### 3. 🗑️ 刪除時機（Deletion Timing — 何時清理歸零）
為防止過期靈感殘留、重複詢問或浪費讀取流量，必須嚴格執行**「處理完畢即刻銷毀」**原則：
- **刪除時機 A（使用者否決/放棄時）**：於 Step E1 或 Step E2 使用者表示「不採用／不需要修改」時，**當下立即將該條靈感從 `_pending_skill_inspirations.md` 移除**。
- **刪除時機 B（完成技能更新時）**：於 Step E3 將新規則正式寫入技能規範檔與 `THEORY_ARCHIVE.md` 後，該靈感已固化為永久技能，**當下立即刪除 `reading_sessions/_pending_skill_inspirations.md` 檔案**，確保暫存區 100% 歸零！
