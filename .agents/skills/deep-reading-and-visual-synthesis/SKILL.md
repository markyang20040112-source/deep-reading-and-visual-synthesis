---
name: deep-reading-and-visual-synthesis
description: >-
  Facilitates deep reading comprehension via a theory-grounded 5-step Socratic scaffolding and analogical encoding protocol or a 3-loop Data Codebook funnel storytelling & 10-distribution-chart step-by-step tutor workflow (Phase 1),
  followed by a 5-dimension pre-generation confirmation gate, 8-slot all-scenario writing style penetration, layered CIELAB color palettes, and scientifically designed multi-format outputs including multi-topology Python matplotlib knowledge diagrams, 5-genre structured reports (including <=1,600-word Medium data storytelling columns), Assertion-Evidence presentation slides, dual-track quantitative scientific & distribution charts, and dynamic data dashboards (Phase 2),
  with a post-session empirical skill evolution & GitHub Issues feedback mechanism.
  Activate when a user uploads or discusses an article, business case, research paper, report, dataset + Data Codebook (資料說明書), or video transcript for deep reading, critical analysis, statistical distribution tutoring, data journalism, or visual synthesis.
---

# 深度閱讀引導與視覺化知識統整 — 總路由指南與檔案地圖 (Master Router & File Map)

> [!IMPORTANT]
> **【第零關：公私雙倉庫架構、身分驗證、作者雙電腦自動還原、外部新使用者強制初始化與每月無損檢查更新門神】**
> 本技能採**「公開範本倉庫（Public）＋ 作者私人資產倉庫（Private）」雙倉庫徹底隔離架構**：公開倉庫僅包含核心技能規範、渲染引擎與空白範本（[`config/user_preferences.template.json`](./config/user_preferences.template.json)、[`config/styles/_style_schema_template.md`](./config/styles/_style_schema_template.md)），**不包含**任何作者私人色票、私人筆風檔（`config/owner_styles/`）與 `reading_sessions/` 紀錄（皆已由根目錄 `.gitignore` 隔離）。
> 啟動本技能時，首先檢查 [`config/user_preferences.json`](./config/user_preferences.json)（或由 Python 黑盒呼叫 `hcl_color_engine.check_user_identity_and_load_prefs()`）：
> 1. **作者本人雙電腦 100% 無縫還原與直通車（Owner Seamless Sync & Pass-Through）**：只要本機 Git 身分驗證為擁有者 **`markyang20040112-source`**（或通過 `gh` CLI／家目錄標記 `~/.deep_reading_owner_verified` 驗證）：
>    - 若本機尚未還原私人設定（例如在第二台電腦剛 `git clone` 公開倉庫），`check_user_identity_and_load_prefs()` 會自動呼叫 `ensure_owner_private_assets(pull_remote=True)`，從私人倉庫 `https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis-Private-.git` 拉取 `reading_sessions/` 並將 `reading_sessions/_owner_private_config/` 還原至 `config/user_preferences.json` 與 `config/owner_styles/`（亦可手動執行 `python .agents/skills/deep-reading-and-visual-synthesis/scripts/hcl_color_engine.py --restore-private`）。
>    - 系統隨即啟用擁有者全套私人色票與私人筆風庫（`config/owner_styles/`），且 `"onboarding_completed"` 永遠鎖定為 `true`——**日常執行絕對禁止讀取 [`setup/onboarding_wizard.md`](./setup/onboarding_wizard.md)，確保零額外 Token 消耗與零誤觸**！
> 2. **外部新使用者強制攔截與範本初始化（External User Mandatory Onboarding）**：當本機身分**非** `markyang20040112-source` 且本機尚無個人化的 `config/user_preferences.json` 時，系統一律從空白範本 [`config/user_preferences.template.json`](./config/user_preferences.template.json) 啟動，並**強制攔截、唯一開啟 [`setup/onboarding_wizard.md`](./setup/onboarding_wizard.md)** 引導新使用者完成環境健檢並自建專屬色票與筆風（存於 `config/user_styles/`）後才放行進入主流程！
> 3. **每月一次官方技能無損檢查更新（Monthly Non-Destructive Upstream Check）**：對外部使用者（依 `update_check.interval_days: 30` 節流，未滿 30 天零網路請求、零延遲），可呼叫 `check_skill_updates.check_for_skill_updates()` 檢查官方倉庫是否有新版本。若有更新，先向使用者展示本次更新內容摘要（Changelog）並徵詢是否更新；確認後呼叫 `apply_non_destructive_update()`，**嚴格保護且絕不覆蓋**使用者的 `config/user_preferences.json`、`config/user_styles/*`、`config/owner_styles/*`、專屬色票（含 `gephi_palette.js`）與 `reading_sessions/*`！

> [!IMPORTANT]
> **五大核心運作鐵律**：
> 1. **雙階段隔離與按需拆檔載入（Default Mode & Lazy Loading）**：傳入文章、資料集（含 CSV＋《資料說明書》）或課程專案包時預設**只讀 [`phase1_reading/phase1_socratic_reading_guide.md`](./phase1_reading/phase1_socratic_reading_guide.md)**，再依輸入模式**僅開啟單一對應子協定檔**（文獻讀 [`mode1_article_socratic_protocol.md`](./phase1_reading/mode1_article_socratic_protocol.md)；CSV＋資料說明書讀 [`mode2_dataset_codebook_protocol.md`](./phase1_reading/mode2_dataset_codebook_protocol.md)）；第一階段進行中**嚴禁提前讀取 `phase2_output/`**（唯模式 2 軌道 C「分配圖形逐步導學」可按需連動讀取 [`phase2_output/distribution_and_density_chart_spec.md`](./phase2_output/distribution_and_density_chart_spec.md)）。
> 2. **生成前「五維度動態確認關卡」與顯式跳關特例（Pre-Generation 5-Dimension Gate & Fast-Track Override）**：無論從 Phase 1 收斂進入 Phase 2，或使用者明確要求跳過引導直接生成（先將原始素材存入 `reading_sessions/<YYYYMMDD_主題簡稱>/00_source_article.md`、原始 CSV 原封不動存入 `data/<原檔名>.csv`），讀取 [`phase2_output/phase2_output_router.md`](./phase2_output/phase2_output_router.md) 後，**除非該維度已在 `config/user_preferences.json` 設為 `"auto_apply_default": true`，否則動工前必須先向使用者確認：1. 產出格式與檔案清單、2. 筆風設定檔（支援多檔交叉搭配）、3. 顏色設定集、4. 圖表模式（`editorial_storytelling` vs. `pure_dataviz`）與故事結構／互動節奏（`batch_generation` 一次批次 vs. `step_by_step_tutor` 一次一張圖逐步導學）、5. 版面與輸出細節**，絕不擅自代選！
> 3. **筆風設定檔 8 大插槽 100% 全域穿透鐵律（100% Style Penetration）**：底層視覺規範與行文語氣徹底解耦。選定之筆風設定檔（`Slot 1～Slot 8`）**100% 穿透控制所有生成場景**——包含 Phase 1 對談導學、Format B 報告散文與表格錨點、Format A 知識圖譜卡片與箭頭謂詞、Format C 簡報斷言與講稿、以及 Format D & E 圖表主副標題、座標軸籤、圖內標註氣泡與網頁 Tooltip 微文案！
> 4. **底層引擎黑盒呼叫鐵律（Black-Box Engine API Rule）**：`scripts/*.py` 與 `scripts/*.js` 為已封裝之黑盒渲染與驗證引擎，其精簡函數簽名（10～20 行 API 契約）已直接寫入對應的 `phase2_output/*_spec.md` 中。**正常執行時必須直接 `import` 並呼叫引擎函數，嚴禁對 `scripts/*.py` 原始碼呼叫 `read_file` / `view_file`（除非執行報錯需除錯）**，以杜絕無謂的 Token 消耗。
> 5. **靈感生命週期鐵律（Capture $\rightarrow$ Apply / Report $\rightarrow$ Delete，嚴禁私自改檔）**：過程中產生之技能優化靈感，必須嚴格遵守本檔第三節之「紀錄、運用、GitHub Issues 自動回報與刪除規則」，**絕對禁止中斷主流程或私自在背後偷改技能檔**！

---

## 🗺️ 一、 全專案檔案地圖與單一職責分工表 (File Architecture & Single Responsibility Map)

本技能庫採**「單一事實來源（SSOT）＋按需載入（Lazy Loading）」**設計，每個檔案僅負責單一明確維度，**嚴禁跨檔重複抄寫規則或一次讀取全部檔案**：

| 檔案路徑 | 唯一職責說明（Single Responsibility） | 開啟時機（When to Read） |
| :--- | :--- | :--- |
| **[`SKILL.md`](./SKILL.md)**<br>*(本檔案 — 總控台)* | 身分驗證門神、雙階段路由判定、五維度確認鐵律、黑盒引擎呼叫鐵律、`reading_sessions/` 歸檔結構、Git 同步規範、靈感生命週期與 GitHub Issues 回報唯一權威定義。 | 技能啟動時預設載入。 |
| **[`config/user_preferences.template.json`](./config/user_preferences.template.json)**<br>*(本機執行態：`config/user_preferences.json`，由 `.gitignore` 隔離)* | 個人化總設定檔與公開空白範本：公開倉庫僅附空白範本 `user_preferences.template.json`；本機執行時依身分自動還原作者私人設定（自私人倉庫）或由外部使用者初始化生成 `user_preferences.json`（含五維度確認關卡、分層顏色設定集、筆風映射與 Git 回報設定）。 | 啟動及進入 Phase 2 五維度確認關卡時讀取。 |
| **[`config/styles/_style_schema_template.md`](./config/styles/_style_schema_template.md)**<br>**`config/user_styles/*.md`**<br>*(作者本機另含由 `.gitignore` 隔離之 `config/owner_styles/*.md`)* | **8 大全生成場景筆風控制契約（Slots 1～8 ＋ 三態參數 `[USER_LOCKED]` / `[SCENARIO_PRESET]` / `[AI_ADAPTIVE]`）**：<br>• 公開倉庫僅提供 `_style_schema_template.md` 空白結構契約與 `config/user_styles/` 供使用者自建專屬筆風。<br>• 作者個人私人筆風庫存於私人倉庫 `_owner_private_config/owner_styles/`，僅於作者雙電腦自動還原至 `config/owner_styles/` 供本機載入。 | 依使用者選定之筆風按需讀取對應單一筆風檔。 |
| **[`setup/onboarding_wizard.md`](./setup/onboarding_wizard.md)** | **外部新使用者首次啟動強制初始化精靈**：引導非作者之外部新使用者自建專屬 CIELAB 色票与專屬 8 插槽筆風檔（嚴禁提供作者私人資產）。 | **僅限外部未初始化新使用者首次啟動時開啟**（作者本人日常 100% 不讀取）。 |
| **[`phase1_reading/phase1_socratic_reading_guide.md`](./phase1_reading/phase1_socratic_reading_guide.md)**<br>**[`phase1_reading/mode1_article_socratic_protocol.md`](./phase1_reading/mode1_article_socratic_protocol.md)**<br>**[`phase1_reading/mode2_dataset_codebook_protocol.md`](./phase1_reading/mode2_dataset_codebook_protocol.md)** | **第一階段輕量總路由與按需子協定（零刪減拆檔瘦身）**：<br>• `phase1_socratic_reading_guide.md`：四大輸入模式分流表與 `01_phase1_socratic_log.md` 即時持久化模板。<br>• `mode1_article_socratic_protocol.md`：模式 1/3/4 文獻蘇格拉底五步推進（Step 0～5 零刪減雙群組收斂）。<br>• `mode2_dataset_codebook_protocol.md`：模式 2「CSV＋《資料說明書》」之讀取（兩段式安全轉型、三層互斥分流 `df_detail`/`df_other`/`df_subtotal`）— 分析（純明細極值重算、五種證據標籤與血統過濾）— 討論（Track A/B/C 漏斗故事探索與分配導學、製圖 6 條件預填表、`df_other` 雙重消歧、第 6 章護欄與單一故事線收斂）三迴路協定。 | **狀態 1**：進入第一階段時先讀 `phase1_socratic_reading_guide.md`，再**二擇一**讀取對應之 `mode1` 或 `mode2` 子檔。 |
| **[`phase2_output/phase2_output_router.md`](./phase2_output/phase2_output_router.md)** | **第二階段總控台**：**「生成前五維度動態確認關卡」**、5 步標準輸出流程（含一次批次生成 vs. 逐步導學互動模式）、跨格式「動態三軸視覺決策引擎」、「A2 無損分流擴展鐵律」與「Medium 每週一圖輕量路由」。 | **狀態 2**：第一階段收斂完成或要求直接生成時首先開啟。 |
| **[`phase2_output/visual_cognition_principles.md`](./phase2_output/visual_cognition_principles.md)** | **五格式共通底層定律**：① 單畫布 $4 \to 2 \to 3$ 視覺上限 vs. 跨畫布無損擴展；② **筆風設定檔解耦與 8 大插槽（Slots 1～8）100% 全域穿透綁定法則**；③ 跨格式字級階梯總表；④ **75-20-5 色彩配額與分層式顏色設定集（`chart_palettes` + `document_themes`）動態連動法則**。 | 進入第二階段必讀（提供跨格式共通標準）。 |
| **[`phase2_output/visual_diagram_matplotlib_spec.md`](./phase2_output/visual_diagram_matplotlib_spec.md)** | **特化格式 A（知識圖譜 `.png`）**：`23.8"×15.4"` 標準畫布（依 2/3 列密度自適應 `12.6"–15.4"`、`240 DPI`）、`16.0–16.5pt` 高可讀大字級與放大雙重小方框（`13.4–14.0pt`）、多畫布無損分流（`01` 主幹圖、`02` 機制圖、`03+` 批判延伸與跨域遷移專題圖）、五大拓撲（T1～T5）、`measure_card_height`／`top_y` 幾何防護、A4 直向原生輕量簡圖 API（`7.44"`）、筆風 `Slot 5` 綁定，以及 **`scripts/generate_mindmap.py` 黑盒 API 契約**。 | 第二階段需生成【格式 A：知識圖譜】或 Format B 內嵌輕量簡圖時開啟。 |
| **[`phase2_output/document_report_spec.md`](./phase2_output/document_report_spec.md)** | **特化格式 B（深度報告 `.md`/`.pdf` 與 Medium 數據敘事專欄 `.md`）**：**五大體裁**——含 B1～B4 深度報告（嚴格解耦 Format A，**禁嵌高密度圖譜與 A4 橫向跨頁**；改採 A4 直向原生 `189mm` 輕量流程圖、舒適字級 `10.8–11.2pt`、通用 `<h2>` 殘餘空間自適應分頁、`<=5`／`>5` 列短長表分流護欄、筆風 `Slot 3 & 4` 綁定與 `scripts/pdf_report_engine.py` 黑盒 API 契約），以及 **文體 5：Medium 每週一圖數據敘事專欄（`<= 1,600` 字、禁用自訂 HTML/表格、文末「參考資料來源（僅附：1.官方資料集網址、2.資料涵蓋期間）」分離計字規則與課堂繳交區塊）**。 | 第二階段需生成【格式 B：深度報告／白皮書／Medium 數據專欄】時開啟。 |
| **[`phase2_output/presentation_slide_spec.md`](./phase2_output/presentation_slide_spec.md)** | **特化格式 C（高階簡報 `.pptx`）**：三區架構、八大版型動態調度（`S0`～`S7`）、依欄數分級字級底線、首尾定錨＋中段無損加頁、筆風 `Slot 4 & 7` 綁定，以及 **`scripts/pptx_slide_engine.py` 黑盒 API 契約**。 | 第二階段需生成【格式 C：高階簡報】時開啟。 |
| **[`phase2_output/quantitative_chart_spec.md`](./phase2_output/quantitative_chart_spec.md)** | **特化格式 D（量化科學圖表 `.png`）**：**結構級雙軌制（`editorial_storytelling` 敘事圖解 vs. `pure_dataviz` 純資料視覺化）**、圖表配色設定集唯一權威定義（SSOT）、Medium 模式 1～2 張獨立單面板跨檔色彩接力、腳本內嵌三層分流 `assert`、筆風 `Slot 6` 綁定、精簡官方資料來源圖註，以及 **`scripts/hcl_color_engine.py` 黑盒 API 契約**。<br>🔗 **與格式 E 及分配圖形指南雙向連動**。 | 第二階段需生成【格式 D：量化統計圖表】或【格式 E：數據儀表板】時開啟。 |
| **[`phase2_output/distribution_and_density_chart_spec.md`](./phase2_output/distribution_and_density_chart_spec.md)** | **特化模組（10 大分配與密度圖形完整指南 & 逐步導學規範）**：直方圖（含參考線白框描邊 `add_halo_vline`、右尾貼地極端值定位圓點 `annotate_floor_extreme`）、非負截斷 KDE（`plot_clipped_kde`，嚴禁樣條插值次數多邊圖冒充）、ECDF、常態 Q-Q 圖、箱形圖、小提琴圖、山脊圖、2D 直方圖、2D KDE 等高線、**背景基準疊加分面比較（Context Overlay / Shadow Distribution）8 大防詐欺鐵律与四大實證案例**、以及**三層指標消歧與資料血統護欄**。 | 當執行 `pure_dataviz` 分配圖形、背景基準分面比較或「逐步導學互動模式（`step_by_step_tutor`）」時開啟。 |
| **[`phase2_output/data_dashboard_spec.md`](./phase2_output/data_dashboard_spec.md)** | **特化格式 E（數據儀表板 Web `.html`/`.css`/`.js` ＋ 靜態全景圖 `.png`）**：動態圖表選型、前端 CSS `:root` 色票與 `scripts/gephi_palette.js` 黑盒 API 契約、自包含本地 `css/style.css`（禁用 `cdn.tailwindcss.com`）、零後端雙擊即開、筆風 `Slot 6` 綁定、CSV 匯出與獨立 Git 網站發布規範。<br>🔗 **與格式 D 及分配圖形指南雙向連動**。 | 第二階段需生成【格式 E：數據儀表板】時開啟。 |
| **[`scripts/hcl_color_engine.py`](./scripts/hcl_color_engine.py)**<br>**[`scripts/gephi_palette.js`](./scripts/gephi_palette.js)**<br>**[`scripts/generate_mindmap.py`](./scripts/generate_mindmap.py)**<br>**[`scripts/pdf_report_engine.py`](./scripts/pdf_report_engine.py)**<br>**[`scripts/pptx_slide_engine.py`](./scripts/pptx_slide_engine.py)**<br>**[`scripts/verify_visual_outputs.py`](./scripts/verify_visual_outputs.py)**<br>**[`scripts/report_skill_feedback.py`](./scripts/report_skill_feedback.py)**<br>**[`scripts/check_skill_updates.py`](./scripts/check_skill_updates.py)** | **八大底層黑盒渲染、色彩、驗證、回報與更新引擎（日常執行直接 `import` 或 CLI 呼叫，免讀原始碼）**：<br>• `hcl_color_engine.py` / `gephi_palette.js`：身分驗證與設定載入（`check_user_identity_and_load_prefs`）、多色票切換与 CIELAB 主色自動推導（`build_palette_from_primary_hexes`）、分配圖形與背景基準分面繪圖 API（`add_halo_vline`、`annotate_floor_extreme`、`plot_clipped_kde`、`setup_context_overlay_grid`）及 CSV 三層互斥分流（`load_and_split_csv`）。<br>• `generate_mindmap.py`：Format A 緊湊高可讀知識圖譜引擎（含 Format B 專用 A4 直向原生輕量簡圖 API）。<br>• `pdf_report_engine.py`：Format B A4 直向雙模排版、通用 `<h2>` 殘餘空間自適應分頁（`compile_adaptive_report_pdf`）、短／長表與輕量尾端保護及 PDF 編譯引擎。<br>• `pptx_slide_engine.py`：Format C 16:9 原生向量簡報與版型防撞引擎。<br>• `verify_visual_outputs.py`：PDF/PPTX 轉 PNG 視覺預覽、Medium 專欄分離計字檢驗與暫存檔清除工具。<br>• `report_skill_feedback.py`：跨使用者靈感三通道自動回報 GitHub Issues 工具。<br>• `check_skill_updates.py`：每月一次官方技能檢查更新與無損更新引擎（嚴格保護使用者筆風、色票與設定不被覆蓋）。 | 撰寫或執行第一／第二階段腳本、視覺驗收、每月檢查更新與 Step E1 靈感回報時直接 `import` 或 CLI 呼叫（**免讀原始碼**）。 |
| **[`THEORY_ARCHIVE.md`](./THEORY_ARCHIVE.md)** | 本技能背後之核心認知心理學、教育心理學、視覺感知、統計分配圖形（Tukey, Silverman, Hintze & Nelson, Wilke）、數據新聞敘事與排版工學實證文獻封存庫（T01～T21）。 | **狀態 3**：僅於詢問理論出處或執行 Step E3 技能進化時開啟（**日常嚴禁讀取以省流量**）。 |

---

## 🗂️ 二、 閱讀專案自動歸檔與目錄整潔規範 (`reading_sessions/`)

每次處理新文章或數據集時，於工作區根目錄建立以下結構（嚴禁存入 `.agents/skills/` 內）：
- `reading_sessions/<YYYYMMDD_主題簡稱>/data/<原檔名>.csv`：**【原始 CSV 零改動鐵律】** 凡傳入 CSV 數據集，原始 CSV 檔案必須**原封不動存入 `data/<原檔名>.csv`**（嚴格遵守 HackMD《資料集說明文件與品質稽核規範》第 5 節「保留原始 CSV 檔案絕對不改動」）。
- `reading_sessions/<YYYYMMDD_主題簡稱>/00_source_article.md`（或多檔目錄 `00_drive_source_files/`）：一收到文章素材或使用者於 Gemini 網頁版生成的《資料說明書（Data Codebook）》立即原封不動存檔。
- `reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md`：即時同步更新該專案之思辨軌跡，或「CSV＋資料說明書」之三層互斥分流驗算、廣角候選切角選單、逐步導學互動討論、6 條件預填表、單一故事線收斂與五維度確認完整過程紀錄。
- `reading_sessions/<YYYYMMDD_主題簡稱>/02_outputs/`：**僅存放最終正式交付成果（`.png`、`.pdf`、`.md`、`.pptx`、正式生成腳本 `.py`，以及格式 E 互動式數據儀表板之 Git-Ready 網站專案檔案 `index.html`、`css/`、`js/`、`data/`、`.nojekyll`、`.gitignore`、`README.md`）**。任何臨時編譯中介檔（如 PDF 轉換過程產生之臨時 `.html`、`_preview_page_*.png`、`_preview_slide_*.png`）於驗證完畢後必須立即呼叫 `verify_visual_outputs.py --cleanup` 自動清除，保持交付目錄 100% 乾淨！
- `reading_sessions/_pending_skill_inspirations.md`：**【跨階段靈感暫存檔】**（僅在過程中出現優化靈感時動態建立，於 Step E3 寫入技能庫後**立即刪除**）。
- **公私雙倉庫 Git 同步、跨電腦自動還原、獨立儀表板網站綁定與課堂作業繳交規則**（依 `config/user_preferences.json` 之 `git_sync_mode` 執行）：
  0. **公私雙倉庫隔離與同步指令（Owner Dual-Repo Architecture）**：
     - **外層公開倉庫（`https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis.git`）**：透過根目錄 `.gitignore` 嚴格排除 `reading_sessions/`、`config/owner_styles/` 與 `config/user_preferences.json`，僅推送核心技能規範、腳本與公開範本。
     - **內層私人資產倉庫（`reading_sessions/` 內綁定 `https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis-Private-.git`）**：同步所有 `reading_sessions/` 專案及 `reading_sessions/_owner_private_config/`（`user_preferences.json` 與 `owner_styles/*.md`）。
     - **另一台電腦一鍵還原／雙向同步**：`python .agents/skills/deep-reading-and-visual-synthesis/scripts/hcl_color_engine.py --restore-private`（拉取並還原至 `config/`）；`python .agents/skills/deep-reading-and-visual-synthesis/scripts/hcl_color_engine.py --sync-private`（將最新閱讀紀錄與修改後的筆風/設定備份並推送至私人倉庫）。
  1. **階段完成自動同步**：當 `git_sync_mode == "auto_push_main"` 時，每當完成第二階段成果產出，作者帳號自動呼叫 `hcl_color_engine.ensure_owner_private_assets(pull_remote=False, push_remote=True)` 將 `reading_sessions/` 與私人設定推送至私人倉庫；若涉及核心技能檔更新（Step E3），才於根目錄同步推送公開倉庫（外部使用者若將 `git_sync_mode` 設為 `"none"` 則僅存本機）。
  2. **跨裝置隨時同步（On-Demand Checkpoint Sync）**：在任何時刻，只要作者要求「先同步到 Git／我要換裝置」，AI 立即將當前進度寫入 `01_phase1_socratic_log.md`，並執行 `python .agents/skills/deep-reading-and-visual-synthesis/scripts/hcl_color_engine.py --sync-private -m "wip(session): checkpoint sync for device handoff"` 推送至私人倉庫（若有核心技能改動亦一併推送公開倉庫）。
  3. **格式 E（數據儀表板）獨立 Git 儲存庫綁定與網站發布**：每當生成格式 E 數據儀表板時，預設封裝為可獨立上線之靜態網站結構（含純相對路徑、自包含 `css/style.css`、`js/gephi_palette.js`、`.nojekyll`、`.gitignore` 與專屬部署 `README.md`），並於驗收後主動詢問或協助使用者將該儀表板綁定至**獨立 Git 儲存庫**發布為線上網站（如 GitHub Pages / Vercel）；同時嚴格遵守 [`phase2_output/data_dashboard_spec.md`](./phase2_output/data_dashboard_spec.md) 第四節之**「防嵌套 `.git` 子模組衝突（Nested Gitlink Prevention）」**規範，確保獨立網站發布與外層 `reading_sessions/` 版控雙贏無衝突。
  4. **Medium 每週一圖專欄之 GitHub 單一檔案對話連結與課堂繳交區塊**：當執行「Medium 每週一圖／輕量數據敘事專欄」工作流時，將 Phase 1 完整討論過程寫入 `reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md` 並完成 Phase 2 產出後，依使用者設定同步至對應倉庫（注意：作者私人倉庫預設不對外公開，若課堂繳交需要公開連結，請另行以 Secret Gist 或獨立公開頁分享該檔案），並於回覆結尾輸出符合課堂 Google Doc 格式的繳交摘要區塊（詳見 [`phase2_output/document_report_spec.md`](./phase2_output/document_report_spec.md) 第四節）。

---

## 🔄 三、 技能優化靈感之「紀錄、運用、GitHub Issues 自動回報與刪除」完整生命週期規範（唯一權威定義）

### 1. 📝 紀錄規則（Recording Rules — 何時記、記哪裡、怎麼記）
- **全方位靈感範疇**：凡與本技能相關的一切構想皆可納入，包含：(1) 功能與引導流程、(2) 視覺與排版設計、(3) 筆風與配色設定、(4) 技能 `.md` 檔案本身的寫法、結構去重、檔案分工或 Python 腳本優化。
- **觸發與不中斷原則**：在第一階段或第二階段進行中，當使用者主動提出或 AI 察覺可優化之處時，統一寫入 `reading_sessions/_pending_skill_inspirations.md`（格式：`[編號] | [來源] | [類別] | [目標檔案] | [觀察痛點與具體改良構想]`），僅附註一句*「（💡 已記錄至靈感暫存檔，待成果交付完畢後再一併查證與升級）」*，**嚴禁中途離題查資料或私自改檔**（若正在逐項檢查格式，則待全部格式檢查完畢後統一處理）。

### 2. 🚀 運用與跨使用者回報時機（Application & Upstream GitHub Issues Reporting — 三步閉環）
當最終成果已交付並驗收完畢（或使用者主動下令處理靈感）時，若 `_pending_skill_inspirations.md` 存在，依序執行：
1. **Step E1（提議、徵詢本機升級同意 ＋ 詢問是否一鍵回報原作者 GitHub Issues）**：
   - 列出暫存靈感，詢問使用者：
     1. 是否同意檢索學術研究與實證標準以評估升級本機技能庫？
     2. **【跨使用者靈感三通道自動回報（GitHub Issues）】**：是否要同時呼叫 [`scripts/report_skill_feedback.py`](./scripts/report_skill_feedback.py) 將本次靈感以固定代號格式（`[FR-FLOW]` / `[FR-VIS]` / `[FR-STYLE]` / `[FR-CODE]` / `[FR-DOC]` / `[FR-BUG]`）一鍵回報至原作者公開倉庫（**唯一鎖定：`https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis/issues`**）？（支援 **通道 A**：已登入 `gh` CLI 時直接 `gh issue create`；**通道 B**：無 GitHub 帳號／未登入 `gh` 時，透過匿名 Google Apps Script Webhook 背景自動建 Issue 並私密通知原作者；**通道 C**：離線環境退回預填 GitHub Issue 網址）。
2. **Step E2（查證文獻與修改方案確認）**：檢索權威論文或技術標準，回報「(1) 實證依據、(2) 預計修改之技能檔案與具體條文」，請使用者確認。
3. **Step E3（無損寫入技能庫 ＋ 格式 D/E 與分配圖形指南雙向連動同步）**：獲確認後，將文獻補入 `THEORY_ARCHIVE.md`，將精煉規則更新至對應之單一職責規範檔（避免跨檔重複與舊規矛盾）。**【格式 D ⇄ 格式 E ⇄ 分配圖形指南強制連動條款】**：若更新內容涉及「圖表配色設定集」、「分配與密度圖形規則」或「統計圖表共通設計與視覺編碼規則」，**必須同時檢查並同步更新 [`phase2_output/quantitative_chart_spec.md`](./phase2_output/quantitative_chart_spec.md)、[`phase2_output/distribution_and_density_chart_spec.md`](./phase2_output/distribution_and_density_chart_spec.md)、[`phase2_output/data_dashboard_spec.md`](./phase2_output/data_dashboard_spec.md)、[`scripts/hcl_color_engine.py`](./scripts/hcl_color_engine.py) 與 [`scripts/gephi_palette.js`](./scripts/gephi_palette.js)**，確保量化圖表與數據儀表板永遠保持 100% 同步！

### 3. 🗑️ 刪除時機（Deletion Timing — 處理完畢即刻歸零）
- **刪除時機 A（使用者否決時）**：於 Step E1/E2 使用者表示不採用時，當下立即將該條靈感從暫存檔移除。
- **刪除時機 B（完成技能更新時）**：於 Step E3 將新規則寫入技能庫後，**當下立即刪除 `reading_sessions/_pending_skill_inspirations.md` 檔案**，確保暫存區 100% 歸零！
