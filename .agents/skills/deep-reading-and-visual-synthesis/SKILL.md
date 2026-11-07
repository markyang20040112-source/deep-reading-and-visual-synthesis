---
name: deep-reading-and-visual-synthesis
description: >-
  Facilitates deep reading comprehension via a theory-grounded 5-step Socratic scaffolding and analogical encoding protocol or a 3-loop Data Codebook funnel storytelling workflow (Phase 1),
  followed by scientifically designed, high-cognitive-absorption multi-format outputs including multi-topology Python matplotlib knowledge diagrams, 5-genre structured reports (including <=1,600-word Medium data storytelling columns), Assertion-Evidence presentation slides, quantitative scientific charts, and dynamic data dashboards (Phase 2),
  with a post-session empirical skill evolution mechanism.
  Activate when a user uploads or discusses an article, business case, research paper, report, dataset + Data Codebook (資料說明書), or video transcript for deep reading, critical analysis, data journalism, or visual synthesis.
---

# 深度閱讀引導與視覺化知識統整 — 總路由指南與檔案地圖 (Master Router & File Map)

> [!IMPORTANT]
> **四大核心運作鐵律**：
> 1. **雙階段隔離（Default Mode）**：傳入文章、資料集（含 CSV＋《資料說明書》）或課程專案包時預設**只讀 [`phase1_reading/phase1_socratic_reading_guide.md`](./phase1_reading/phase1_socratic_reading_guide.md)**；第一階段進行中**嚴禁讀取 `phase2_output/`**。
> 2. **顯式跳關特例（Fast-Track Override）**：**唯有使用者明確要求跳過引導、直接生成成果**時，先將原始素材存入 `reading_sessions/<YYYYMMDD_主題簡稱>/00_source_article.md`（若含原始 CSV 則原封不動存入 `data/<原檔名>.csv`；多檔則存入 `00_drive_source_files/`），直接讀取 [`phase2_output/phase2_output_router.md`](./phase2_output/phase2_output_router.md) 產出檔案。
> 3. **底層引擎黑盒呼叫鐵律（Black-Box Engine API Rule）**：`scripts/*.py` 與 `scripts/*.js` 為已封裝之黑盒渲染與驗證引擎，其精簡函數簽名（10～15 行 API 契約）已直接寫入對應的 `phase2_output/*_spec.md` 中。**正常執行時必須直接 `import` 並呼叫引擎函數，嚴禁對 `scripts/*.py` 原始碼呼叫 `read_file` / `view_file`（除非執行報錯需除錯）**，以杜絕無謂的 Token 消耗。
> 4. **靈感生命週期鐵律（Capture $\rightarrow$ Apply $\rightarrow$ Delete，嚴禁私自改檔）**：過程中產生之技能優化靈感，必須嚴格遵守本檔第三節之「紀錄、運用與刪除規則」，**絕對禁止中斷主流程或私自在背後偷改技能檔**！

---

## 🗺️ 一、 全專案檔案地圖與單一職責分工表 (File Architecture & Single Responsibility Map)

本技能庫採**「單一事實來源（SSOT）＋按需載入（Lazy Loading）」**設計，每個檔案僅負責單一明確維度，**嚴禁跨檔重複抄寫規則或一次讀取全部檔案**：

| 檔案路徑 | 唯一職責說明（Single Responsibility） | 開啟時機（When to Read） |
| :--- | :--- | :--- |
| **[`SKILL.md`](./SKILL.md)**<br>*(本檔案 — 總控台)* | 雙階段路由判定、黑盒引擎呼叫鐵律、`reading_sessions/` 歸檔結構、Git 同步規範、靈感生命週期（`_pending_skill_inspirations.md`）唯一權威定義。 | 技能啟動時預設載入。 |
| **[`phase1_reading/phase1_socratic_reading_guide.md`](./phase1_reading/phase1_socratic_reading_guide.md)** | 第一階段四大輸入模式路由：含文獻蘇格拉底五步推進（Step 0～5 零刪減收斂），以及**模式 2「CSV 原始檔 ＋《資料說明書（Data Codebook）》」之讀取（零 CSV Token 浪費、兩段式安全轉型、標準化三層互斥分流 `df_detail`/`df_other`/`df_subtotal`）— 分析（8/5 欄雙模直通車、`df_detail` 極值重算、五種證據標籤與前處理血統過濾）— 討論（雙軌 Track A/B 漏斗故事探索、製圖條件全預填表、原表 `其他` 列雙重消歧、第 6 章外推邊界護欄與單一故事線收斂）三迴路協定**。 | **狀態 1**：進入第一階段閱讀與資料盤點時唯一開啟之檔案。 |
| **[`phase2_output/phase2_output_router.md`](./phase2_output/phase2_output_router.md)** | 第二階段 4 步輸出流程總控台、跨格式「動態三軸視覺決策引擎」、**「A2 無損分流擴展鐵律」**，以及**「Medium 每週一圖／輕量數據敘事專欄模式」專屬輕量路由（僅產出 1～2 張單面板 `.png` ＋ 文體 5 `.md`，免除 PDF 編譯）**。 | **狀態 2**：第一階段收斂完成或使用者要求直接生成時首先開啟。 |
| **[`phase2_output/visual_cognition_principles.md`](./phase2_output/visual_cognition_principles.md)** | **五格式共通底層定律**：① 單畫布 $4 \to 2 \to 3$ 視覺上限 vs. 跨畫布無損擴展；②「白話直覺先行、由淺入深」敘事鐵律；③ 跨格式字級階梯總表（與各規格檔 100% 同步）；④ 75-20-5 色彩配額、零透明度（0-Alpha）標籤底色與鎖定版圖表配色原則。 | 進入第二階段 Step 1 必讀（提供跨格式共通標準）。 |
| **[`phase2_output/visual_diagram_matplotlib_spec.md`](./phase2_output/visual_diagram_matplotlib_spec.md)** | **特化格式 A（知識圖譜 `.png`）**：`28"×18.5" (240 DPI)` 畫布、多畫布無損分流（`01` 主幹圖、`02` 機制圖、`03+` 批判延伸與跨域遷移專題圖）、五大拓撲（T1～T5）、雙行飽滿配適、列槽真置中，以及 **`scripts/generate_mindmap.py` 黑盒 API 契約**。 | 第二階段需生成【格式 A：知識圖譜】時開啟。 |
| **[`phase2_output/document_report_spec.md`](./phase2_output/document_report_spec.md)** | **特化格式 B（深度報告 `.md`/`.pdf` 與 Medium 數據敘事專欄 `.md`）**：**五大體裁**——含 B1～B4 深度報告（章節隨分支數 $N$ 動態擴展、A4 橫向滿版大圖跨頁與 `scripts/pdf_report_engine.py` 黑盒 API 契約），以及 **文體 5：Medium 每週一圖數據敘事專欄（`<= 1,600` 字、禁用自訂 HTML/表格、文末「參考資料來源（僅附：1.官方資料集網址、2.資料涵蓋期間）」分離計字規則與課堂繳交區塊）**。 | 第二階段需生成【格式 B：深度報告／白皮書／Medium 數據專欄】時開啟。 |
| **[`phase2_output/presentation_slide_spec.md`](./phase2_output/presentation_slide_spec.md)** | **特化格式 C（高階簡報 `.pptx`）**：三區架構、八大版型動態調度（`S0`～`S7`）、**依欄數分級字級底線（2 欄 `13.0~14.5pt`、3/4 欄 `11.5~12.5pt`）**、首尾定錨＋中段無損加頁，以及 **`scripts/pptx_slide_engine.py` 黑盒 API 契約**。 | 第二階段需生成【格式 C：高階簡報】時開啟。 |
| **[`phase2_output/quantitative_chart_spec.md`](./phase2_output/quantitative_chart_spec.md)** | **特化格式 D（量化科學圖表 `.png`）**：目的驅動差距表現、**鎖定版個人圖表配色設定集唯一權威定義（SSOT：`Gephi · pastel` 四色、零透明度標籤底色、5 階循序、9 階發散、出圖前 6 條件與原表 `df_other` vs. `4+1` `#CBD5E1` 雙重消歧）**、**Medium 模式 1～2 張獨立單面板跨檔色彩接力（橘破題 $\rightarrow$ 藍深挖）、腳本內嵌三層分流 `assert` 與精簡官方資料來源圖註（僅附：1.官方資料集網址、2.資料涵蓋期間）**，以及 **`scripts/hcl_color_engine.py` 黑盒 API 契約**。<br>🔗 **與格式 E 雙向連動**：凡共通配色或圖表設計規則改動，須與 [`data_dashboard_spec.md`](./phase2_output/data_dashboard_spec.md) 同步更新。 | 第二階段需生成【格式 D：量化統計圖表】或【格式 E：數據儀表板】時開啟。 |
| **[`phase2_output/data_dashboard_spec.md`](./phase2_output/data_dashboard_spec.md)** | **特化格式 E（數據儀表板 Web `.html`/`.css`/`.js` ＋ 靜態全景圖 `.png`）**：動態圖表選型、**前端 CSS `:root` 色票與 `scripts/gephi_palette.js` 黑盒 API 契約**、**自包含本地 `css/style.css`（禁用 `cdn.tailwindcss.com`）**、零後端雙擊即開、CSV 匯出與獨立 Git 網站發布規範。<br>🔗 **與格式 D 雙向連動**：引用 [`quantitative_chart_spec.md`](./phase2_output/quantitative_chart_spec.md) 第三節 SSOT 色階定義，任一方改動時另一方必須同步更新。 | 第二階段需生成【格式 E：數據儀表板】時開啟（並連動參照 [`quantitative_chart_spec.md`](./phase2_output/quantitative_chart_spec.md)）。 |
| **[`scripts/hcl_color_engine.py`](./scripts/hcl_color_engine.py)**<br>**[`scripts/gephi_palette.js`](./scripts/gephi_palette.js)**<br>**[`scripts/generate_mindmap.py`](./scripts/generate_mindmap.py)**<br>**[`scripts/pdf_report_engine.py`](./scripts/pdf_report_engine.py)**<br>**[`scripts/pptx_slide_engine.py`](./scripts/pptx_slide_engine.py)**<br>**[`scripts/verify_visual_outputs.py`](./scripts/verify_visual_outputs.py)** | **六大底層黑盒渲染與驗證引擎（日常執行直接 `import` 呼叫，免讀原始碼）**：<br>• `hcl_color_engine.py` / `gephi_palette.js`：Python 與純 JS 雙端 CIELAB 插值、`Gephi · pastel` 配色（含 `df_other` 自動防混入主色）與 CSV 防呆三層互斥分流引擎（`load_and_split_csv`）。<br>• `generate_mindmap.py`：Format A 知識圖譜卡片與 T1～T5 拓撲組件引擎。<br>• `pdf_report_engine.py`：Format B A4 直向／橫向混合排版與 Playwright PDF 編譯引擎。<br>• `pptx_slide_engine.py`：Format C 16:9 原生向量簡報與版型防撞引擎。<br>• `verify_visual_outputs.py`：PDF/PPTX 轉 PNG 視覺驗收預覽、Medium 專欄分離計字檢驗（`verify_medium_article_words`）與暫存檔一鍵清除工具。 | 撰寫或執行第一／第二階段腳本與視覺驗收時直接 `import` 或 CLI 呼叫（**免讀原始碼**）。 |
| **[`THEORY_ARCHIVE.md`](./THEORY_ARCHIVE.md)** | 本技能背後之核心認知心理學、教育心理學、視覺感知、數據新聞敘事與排版工學實證文獻封存庫。 | **狀態 3**：僅於詢問理論出處或執行 Step E3 技能進化時開啟（**日常嚴禁讀取以省流量**）。 |

---

## 🗂️ 二、 閱讀專案自動歸檔與目錄整潔規範 (`reading_sessions/`)

每次處理新文章或數據集時，於工作區根目錄建立以下結構（嚴禁存入 `.agents/skills/` 內）：
- `reading_sessions/<YYYYMMDD_主題簡稱>/data/<原檔名>.csv`：**【原始 CSV 零改動鐵律】** 凡傳入 CSV 數據集，原始 CSV 檔案必須**原封不動存入 `data/<原檔名>.csv`**（嚴格遵守 HackMD《資料集說明文件與品質稽核規範》第 5 節「保留原始 CSV 檔案絕對不改動」）。
- `reading_sessions/<YYYYMMDD_主題簡稱>/00_source_article.md`（或多檔目錄 `00_drive_source_files/`）：一收到文章素材或使用者於 Gemini 網頁版生成的《資料說明書（Data Codebook）》立即原封不動存檔。
- `reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md`：即時同步更新該專案之思辨軌跡，或「CSV＋資料說明書」之三層互斥分流驗算、廣角候選切角選單、互動討論、6 條件預填表與單一故事線收斂完整過程紀錄。
- `reading_sessions/<YYYYMMDD_主題簡稱>/02_outputs/`：**僅存放最終正式交付成果（`.png`、`.pdf`、`.md`、`.pptx`、正式生成腳本 `.py`，以及格式 E 互動式數據儀表板之 Git-Ready 網站專案檔案 `index.html`、`css/`、`js/`、`data/`、`.nojekyll`、`.gitignore`、`README.md`）**。任何臨時編譯中介檔（如 PDF 轉換過程產生之臨時 `.html`、`_preview_page_*.png`、`_preview_slide_*.png`）於驗證完畢後必須立即呼叫 `verify_visual_outputs.py --cleanup` 自動清除，保持交付目錄 100% 乾淨！
- `reading_sessions/_pending_skill_inspirations.md`：**【跨階段靈感暫存檔】**（僅在過程中出現優化靈感時動態建立，於 Step E3 寫入技能庫後**立即刪除**）。
- **Git 雙模同步、跨裝置接續、獨立儀表板網站綁定與課堂作業繳交規則**：
  1. **階段完成自動同步（主知識庫倉庫）**：每當完成第二階段成果產出，或完成技能進化更新（Step E3）後，自動於工作區根目錄執行 `git add -A && git commit -m "..." && git push origin main`。
  2. **跨裝置隨時同步（On-Demand Checkpoint Sync）**：在任何時刻，只要使用者要求「先同步到 Git／我要換裝置」，AI 立即將當前進度寫入 `01_phase1_socratic_log.md`，並執行 `git add -A && git commit -m "wip(session): checkpoint sync for device handoff" && git push origin main`。
  3. **格式 E（數據儀表板）獨立 Git 儲存庫綁定與網站發布**：每當生成格式 E 數據儀表板時，預設封裝為可獨立上線之靜態網站結構（含純相對路徑、自包含 `css/style.css`、`js/gephi_palette.js`、`.nojekyll`、`.gitignore` 與專屬部署 `README.md`），並於驗收後主動詢問或協助使用者將該儀表板綁定至**獨立 Git 儲存庫**發布為線上網站（如 GitHub Pages / Vercel）；同時嚴格遵守 [`phase2_output/data_dashboard_spec.md`](./phase2_output/data_dashboard_spec.md) 第四節之**「防嵌套 `.git` 子模組衝突（Nested Gitlink Prevention）」**規範，確保獨立網站發布與主知識庫版控雙贏無衝突。
  4. **Medium 每週一圖專欄之 GitHub 單一檔案對話連結自動推送與課堂繳交區塊**：當執行「Medium 每週一圖／輕量數據敘事專欄」工作流時，將 Phase 1 完整討論過程寫入 `reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md` 並完成 Phase 2 產出後，自動執行 `git add -A ; git commit -m "..." ; git push origin main` 推送至公開 GitHub 倉庫（依 `git remote get-url origin` 動態確認遠端網址，如 `https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis` 或 `https://github.com/s12161144/deep-reading-and-visual-synthesis`），並於回覆結尾直接印出符合課堂 Google Doc 格式的一鍵複製繳交區塊（含該次 `01_phase1_socratic_log.md` 的 **GitHub 單一檔案 `blob/main/...` 完整網址**，詳見 [`phase2_output/document_report_spec.md`](./phase2_output/document_report_spec.md) 第四節）。

---

## 🔄 三、 技能優化靈感之「紀錄、運用與刪除」完整生命週期規範（唯一權威定義）

### 1. 📝 紀錄規則（Recording Rules — 何時記、記哪裡、怎麼記）
- **全方位靈感範疇**：凡與本技能相關的一切構想皆可納入，包含：(1) 功能與引導流程、(2) 視覺與排版設計、(3) 技能 `.md` 檔案本身的寫法、結構去重、檔案分工或 Python 腳本優化。
- **觸發與不中斷原則**：在第一階段或第二階段進行中，當使用者主動提出或 AI 察覺可優化之處時，統一寫入 `reading_sessions/_pending_skill_inspirations.md`（格式：`[編號] | [來源] | [類別] | [目標檔案] | [觀察痛點與具體改良構想]`），僅附註一句*「（💡 已記錄至靈感暫存檔，待成果交付完畢後再一併查證與升級）」*，**嚴禁中途離題查資料或私自改檔**（若正在逐項檢查格式，則待全部格式檢查完畢後統一處理）。

### 2. 🚀 運用時機（Application Timing — 三步閉環）
當最終成果已交付並驗收完畢（或使用者主動下令處理靈感）時，若 `_pending_skill_inspirations.md` 存在，依序執行：
1. **Step E1（提議與徵詢同意）**：列出暫存靈感，詢問使用者是否同意檢索學術研究與實證標準以評估升級。
2. **Step E2（查證文獻與修改方案確認）**：檢索權威論文或技術標準，回報「(1) 實證依據、(2) 預計修改之技能檔案與具體條文」，請使用者確認。
3. **Step E3（無損寫入技能庫 ＋ 格式 D/E 雙向連動同步）**：獲確認後，將文獻補入 `THEORY_ARCHIVE.md`，將精煉規則更新至對應之單一職責規範檔（避免跨檔重複與舊規矛盾）。**【格式 D ⇄ 格式 E 強制連動條款】**：若更新內容涉及「圖表配色設定集」或「統計圖表共通設計與視覺編碼規則」，**必須同時更新 [`phase2_output/quantitative_chart_spec.md`](./phase2_output/quantitative_chart_spec.md)、[`phase2_output/data_dashboard_spec.md`](./phase2_output/data_dashboard_spec.md)、[`scripts/hcl_color_engine.py`](./scripts/hcl_color_engine.py) 與 [`scripts/gephi_palette.js`](./scripts/gephi_palette.js)**，確保量化圖表與數據儀表板永遠保持 100% 同步！

### 3. 🗑️ 刪除時機（Deletion Timing — 處理完畢即刻歸零）
- **刪除時機 A（使用者否決時）**：於 Step E1/E2 使用者表示不採用時，當下立即將該條靈感從暫存檔移除。
- **刪除時機 B（完成技能更新時）**：於 Step E3 將新規則寫入技能庫後，**當下立即刪除 `reading_sessions/_pending_skill_inspirations.md` 檔案**，確保暫存區 100% 歸零！

