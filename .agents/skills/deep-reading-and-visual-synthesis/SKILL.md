---
name: deep-reading-and-visual-synthesis
description: >-
  Facilitates deep reading comprehension via a theory-grounded 5-step Socratic scaffolding and analogical encoding protocol or a 3-loop Data Codebook funnel storytelling & 10-distribution-chart step-by-step tutor workflow (Phase 1),
  followed by a 3-layer progressive diagnostic decision funnel (Layer 1 formats A-E -> Layer 2 classified structure & 30+ chart taxonomy advisors -> Layer 3 all-format Design Spectrum & Bespoke Metaphor Armory, 8-slot writing style penetration, and layered CIELAB color palettes) and on-demand micro-spec execution across knowledge diagrams, PDF reports, Medium columns, Assertion-Evidence slides, 5 chart families (including Data 8 editorial dot plots and RE:LAB IDE cross-tool bespoke metaphor rendering), and dynamic web dashboards (Phase 2),
  with post-session empirical skill evolution & GitHub Issues feedback mechanism.
  Activate when a user uploads or discusses an article, business case, research paper, report, dataset + Data Codebook (資料說明書), or video transcript for deep reading, critical analysis, statistical distribution tutoring, data journalism, or visual synthesis.
---

# 深度閱讀引導與視覺化知識統整 — 總路由指南與檔案地圖 (Master Router & File Map)

> [!IMPORTANT]
> **【第零關：公私雙倉庫架構、身分驗證、雙電腦自動還原、外部初始化與每月無損檢查更新】**
> 本技能採**「公開範本倉庫（Public）＋ 作者私人資產倉庫（Private）」雙倉庫徹底隔離架構**：公開倉庫僅含核心規範、引擎與空白範本（[`config/user_preferences.template.json`](./config/user_preferences.template.json)、[`config/styles/_style_schema_template.md`](./config/styles/_style_schema_template.md)），不含任何作者私人色票、私人筆風（`config/owner_styles/`）與 `reading_sessions/`（皆由 `.gitignore` 隔離）。
> 啟動時檢查 [`config/user_preferences.json`](./config/user_preferences.json)（或呼叫 `hcl_color_engine.check_user_identity_and_load_prefs()`）：
> 1. **作者本人（`markyang20040112-source`）無縫還原與直通**：若本機尚未還原私人資產，自動從 `deep-reading-and-visual-synthesis-Private-` 還原至 `config/user_preferences.json` 與 `config/owner_styles/`，`"onboarding_completed"` 鎖定 `true`，**日常嚴禁讀取 [`setup/onboarding_wizard.md`](./setup/onboarding_wizard.md)**！
> 2. **外部新使用者強制初始化**：非擁有者且無個人化 `user_preferences.json` 時，從空白範本啟動並**強制開啟 [`setup/onboarding_wizard.md`](./setup/onboarding_wizard.md)** 引導建置專屬色票與筆風（存於 `config/user_styles/`）。
> 3. **每月一次官方技能無損檢查更新**：依 `update_check.interval_days: 30` 節流，呼叫 `check_skill_updates.py` 檢查更新並保護個人 `config/` 與 `reading_sessions/*` 絕不被覆蓋。

> [!IMPORTANT]
> **五大核心運作鐵律（Core Operational Laws）**：
> 1. **雙階段隔離與按需微模組載入（Lazy Loading）**：傳入素材進入 Phase 1 時預設**只讀 [`phase1_reading/phase1_socratic_reading_guide.md`](./phase1_reading/phase1_socratic_reading_guide.md)**，再依模式**二擇一**讀取 [`mode1_article_socratic_protocol.md`](./phase1_reading/mode1_article_socratic_protocol.md) 或 [`mode2_dataset_codebook_protocol.md`](./phase1_reading/mode2_dataset_codebook_protocol.md)（唯模式 2 軌道 C「分配圖形逐步導學」連動讀取 [`phase2_output/distribution_and_density_chart_spec.md`](./phase2_output/distribution_and_density_chart_spec.md)）。Phase 1 進行中嚴禁提前讀取其他 `phase2_output/` 檔案。
> 2. **Phase 2 三層漸進式討論決策（方案甲）與最小葉節點載入**：進入 Phase 2（含明確要求直接生成 Fast-Track 時，先將原文存 `00_source_article.md`、原始 CSV 原封不動存 `data/<原檔名>.csv`）先僅讀取 **[`phase2_output/phase2_output_router.md`](./phase2_output/phase2_output_router.md)**，依序分步推進：**Layer 1（決定 A/B/C/D/E 範圍）$\rightarrow$ Layer 2（僅開選定格式之 `advisors/layer2_*.md` 顧問決定具體圖型／文體／拓撲／分鏡）$\rightarrow$ Layer 3（開 `advisors/layer3_advisor_design_style_color.md` 全格式統一或混搭定裝：設計武器庫模式 1/2/3 × 筆風 × 配色）$\rightarrow$ 終端僅開啟最終拍板之最小葉節點規格檔**，絕不擅自代選或一次全讀！
> 3. **表達三支柱 100% 全域穿透鐵律**：選定之筆風設定檔（`Slot 1～8`）、分層顏色設定集與第三層設計武器庫（`standard_rigorous` / `editorial_narrative` / `bespoke_metaphor`）**100% 穿透控制所有選定之 A/B/C/D/E 產出格式**。
> 4. **底層引擎黑盒呼叫鐵律（Black-Box Engine API Rule）**：`scripts/*.py` 與 `scripts/*.js` 之 API 契約已記載於對應 `*_spec.md` 中。**正常執行直接 `import` 呼叫，嚴禁對 `scripts/` 原始碼呼叫 `read_file`（除非報錯除錯）**！
> 5. **靈感生命週期鐵律（Capture $\rightarrow$ Apply / Report $\rightarrow$ Delete）**：過程中出現優化靈感時，僅暫存寫入 `reading_sessions/_pending_skill_inspirations.md` 並附註一句提示，**嚴禁中斷主流程或私自改檔**；待成果驗收後再按需開啟 [`setup/git_sync_and_evolution_protocol.md`](./setup/git_sync_and_evolution_protocol.md) 執行 Step E1～E3。

---

## 一、 全專案檔案地圖與單一職責分工表 (File Architecture & Single Responsibility Map)

本技能庫採 **「三層漏斗決策 ＋ 單一事實來源（SSOT）＋ 最小葉節點按需載入」** 架構，確保無論未來擴充多少新圖表或新格式，AI 單次任務負荷恆定維持極小值：

| 檔案路徑 | 唯一職責說明（Single Responsibility） | 精準開啟時機（When to Read） |
| :--- | :--- | :--- |
| **[`SKILL.md`](./SKILL.md)** *(本檔案)* | 總控台：第零關身分驗證門神、五大核心運作鐵律、全專案地圖與 `reading_sessions/` 基礎歸檔路徑。 | 技能啟動時預設載入。 |
| **[`config/user_preferences.template.json`](./config/user_preferences.template.json)**<br>*(本機：`config/user_preferences.json`)* | 個人化總設定檔與公開範本（含 `confirmation_gate`、分層 `chart_palettes` / `document_themes`、筆風映射與 `git_sync_mode`）。 | 啟動身分檢查與 Layer 3 定裝時。 |
| **[`config/styles/_style_schema_template.md`](./config/styles/_style_schema_template.md)**<br>**`config/user_styles/*.md`** / **`config/owner_styles/*.md`** | **8 大全場景筆風控制契約（Slots 1～8）**：控制所有生成格式之語氣、錨點格式、圖譜謂詞、圖表微文案、講稿與禁用詞。 | 終端執行層僅讀取本次選定之單一筆風檔。 |
| **[`setup/onboarding_wizard.md`](./setup/onboarding_wizard.md)** | 外部新使用者首次啟動強制初始化精靈（自建 CIELAB 色票與筆風）。 | **僅限外部未初始化新使用者首次啟動**（作者 100% 不讀）。 |
| **[`setup/git_sync_and_evolution_protocol.md`](./setup/git_sync_and_evolution_protocol.md)** | 公私雙倉庫 Git 同步、跨裝置還原、Format E 防嵌套 `.git` 獨立開站、Medium 課堂繳交區塊與 Step E1～E3 靈感進化回報細節。 | **僅於結案準備同步 Git / 發布網站 / 執行 Step E1～E3 時開啟**。 |
| **[`phase1_reading/phase1_socratic_reading_guide.md`](./phase1_reading/phase1_socratic_reading_guide.md)**<br>[`mode1_article_socratic_protocol.md`](./phase1_reading/mode1_article_socratic_protocol.md)<br>[`mode2_dataset_codebook_protocol.md`](./phase1_reading/mode2_dataset_codebook_protocol.md) | **Phase 1 輕量總路由與雙子協定**：Stage 0 四合一素材嗅探正規化（URL / YouTube / PDF / DOCX）、四大輸入分流、`01_phase1_socratic_log.md` 即時持久化、文獻 5 步蘇格拉底（Mode 1），以及 CSV＋《資料說明書》「讀取—分析—討論」三迴路（Mode 2）。 | **Phase 1**：先讀導覽頁，再依模式**二擇一**開啟子協定。 |
| **[`phase2_output/phase2_output_router.md`](./phase2_output/phase2_output_router.md)** | **Phase 2 Layer 1 總路由**：決定本次生成格式範圍（A / B / C / D / E）、A2 無損擴展 vs. Medium 輕量分流，並規範 `02_phase2_generation_blueprint.md` 時機 A 漸進持久化與標準範本。 | 進入 Phase 2 時首先開啟。 |
| **[`phase2_output/advisors/layer2_advisor_a_diagram.md`](./phase2_output/advisors/layer2_advisor_a_diagram.md)**<br>[`layer2_advisor_b_report.md`](./phase2_output/advisors/layer2_advisor_b_report.md)<br>[`layer2_advisor_c_slide.md`](./phase2_output/advisors/layer2_advisor_c_slide.md)<br>[`layer2_advisor_de_chart.md`](./phase2_output/advisors/layer2_advisor_de_chart.md) | **Phase 2 Layer 2 分類結構顧問大腦**：依第一層選定格式按需開啟——診斷 A（分圖與 T1～T5 拓撲）、B（文體 1～4 PDF＋直向簡圖切點 vs. 文體 5 Medium）、C（全簡報北極星主線、四幕劇、AST 認知轉折與 S0～S7 分鏡）、**D/E（4D 資料快篩 × 8 大溝通意圖 30+ 圖表決策樹與推進節奏）**。 | **Layer 2**：僅開第一層有勾選的格式顧問檔（未選者 0 讀取）。 |
| **[`phase2_output/advisors/layer3_advisor_design_style_color.md`](./phase2_output/advisors/layer3_advisor_design_style_color.md)** | **Phase 2 Layer 3（最後決策層）定裝顧問**：在第二層結構拍板後，為所有選定檔案決定「表達三支柱」（設計武器庫模式 1/2/3 開關 × 筆風 × 配色／主題色階）。 | **Layer 3**：第二層骨架拍板後開啟。 |
| **[`phase2_output/visual_cognition_principles.md`](./phase2_output/visual_cognition_principles.md)** | **五格式共通底層定律**：$4 \to 2 \to 3$ 組塊與無損擴展、表達三支柱穿透法則、事實與因果保真底線、字級階梯總表與 75-20-5 色彩分配。 | 終端執行層必讀共通底盤。 |
| **[`phase2_output/editorial_and_metaphor_armory_spec.md`](./phase2_output/editorial_and_metaphor_armory_spec.md)** | **全格式設計武器庫專檔（模式 2 & 3）**：資料八編輯室 5 大技法（聚光燈、雙基準膠囊、時期色帶、角落排行卡、四層底註）與報告 CSS；資料七 RE:LAB **IDE 四大跨工具具象管線（玻璃杯、`image-generator` 材質扇形遮罩、圖標散佈、主題色階）**及 A/B/C/E 空間隱喻。 | **僅當第三層開啟模式 2 或模式 3 時開啟**（模式 1 不讀）。 |
| **[`phase2_output/quantitative_chart_spec.md`](./phase2_output/quantitative_chart_spec.md)** | **Format D ⇄ E 圖表共通核心契約（SSOT）**：視覺編碼誠實三鐵律、圖表 8 大元件檢核、配色 SSOT、三層分流 `assert`、`300 DPI` 黃金畫布與黑盒 API 總表。 | 執行 Format D 或 E 時必讀。 |
| **[`phase2_output/chart_family1_ranking_and_deviation.md`](./phase2_output/chart_family1_ranking_and_deviation.md)**<br>[`chart_family2_trend_and_comparison.md`](./phase2_output/chart_family2_trend_and_comparison.md)<br>[`chart_family3_composition_and_flow.md`](./phase2_output/chart_family3_composition_and_flow.md)<br>[`distribution_and_density_chart_spec.md`](./phase2_output/distribution_and_density_chart_spec.md)<br>[`chart_family5_multivariate_and_spatial.md`](./phase2_output/chart_family5_multivariate_and_spatial.md) | **五大圖表家族葉節點微規格檔**：<br>• 家族 1：克里夫蘭點陣圖（資料八）、棒棒糖、啞鈴、斜坡、子彈、蝴蝶金字塔、柏拉圖<br>• 家族 2：空間重力斷崖複合、極性同質化、時期事件折線、配對雙柱剪刀差、面積、範圍甘特<br>• 家族 3：`4+1` 堆疊與環形、馬賽克雙維佔比（Marimekko）、瀑布圖、樹圖、巢狀環/旭日、桑基/弦圖<br>• 家族 4：10 大分配與密度圖形 ＋ 背景基準分面（Context Overlay）8 大鐵律<br>• 家族 5：波士頓四象限氣泡矩陣、突出顯示熱力表、雷達圖、主圖＋排行副卡 | 依 Layer 2 拍板結果**按需只開對應的 1～2 個家族檔**。 |
| **[`phase2_output/visual_diagram_matplotlib_spec.md`](./phase2_output/visual_diagram_matplotlib_spec.md)**<br>[`document_report_spec.md`](./phase2_output/document_report_spec.md)<br>[`medium_column_spec.md`](./phase2_output/medium_column_spec.md)<br>[`presentation_slide_spec.md`](./phase2_output/presentation_slide_spec.md)<br>[`data_dashboard_spec.md`](./phase2_output/data_dashboard_spec.md) | **Format A / B / C / E 終端規格檔**：<br>• `visual_diagram_matplotlib_spec.md`：Format A 知識圖譜（`23.8"×15.4"` T1～T5 ＋ Format B `7.44"` 直向簡圖）<br>• `document_report_spec.md`：Format B 文體 1～4 A4 自適應分頁印刷 PDF 報告<br>• `medium_column_spec.md`：Format B 文體 5 Medium `<=1,600` 字原生專欄（禁 HTML/表格，免 PDF）<br>• `presentation_slide_spec.md`：Format C 16:9 三區簡報、AST 講稿轉場與 S0～S7 防撞引擎<br>• `data_dashboard_spec.md`：Format E 零後端互動工作台／標準 CSS 骨架／Bento／Git 發布 | 終端執行層**僅開啟有選定之格式檔**（文體 1～4 與文體 5 互斥單開）。 |
| [`scripts/ingest_source_material.py`](./scripts/ingest_source_material.py)、[`hcl_color_engine.py`](./scripts/hcl_color_engine.py)、[`gephi_palette.js`](./scripts/gephi_palette.js)、[`generate_mindmap.py`](./scripts/generate_mindmap.py)、[`pdf_report_engine.py`](./scripts/pdf_report_engine.py)、[`pptx_slide_engine.py`](./scripts/pptx_slide_engine.py)、[`verify_visual_outputs.py`](./scripts/verify_visual_outputs.py)、[`report_skill_feedback.py`](./scripts/report_skill_feedback.py)、[`check_skill_updates.py`](./scripts/check_skill_updates.py) | **九大底層黑盒擷取、渲染、色彩、驗證、回報與更新引擎**：直接 `import` 或 CLI 呼叫，**日常免讀原始碼**。 | 執行各階段素材擷取、腳本生成、視覺驗收、更新或回報時調用。 |
| **[`THEORY_ARCHIVE.md`](./THEORY_ARCHIVE.md)** | 實證科學理論封存庫（T01～T24）。 | 僅於詢問理論出處或 Step E3 進化時開啟。 |

---

## 二、 閱讀專案歸檔與靈感收斂規則（`reading_sessions/` & Evolution）

1. **專案歸檔結構（嚴禁存入 `.agents/skills/` 內）**：
   - `reading_sessions/<YYYYMMDD_主題簡稱>/data/<原檔名>.csv`：**【原始 CSV 零改動鐵律】** 原始檔原封不動存入，嚴禁覆寫。
   - `reading_sessions/<YYYYMMDD_主題簡稱>/00_source_article.md`（或多檔目錄 `00_drive_source_files/`）：一收到原文或《資料說明書》立即原封不動存檔。
   - `reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md`：即時記錄 Phase 1 深度閱讀思辨或數據探索軌跡（維持獨立自洽，不回寫 Phase 2 規格，亦不附掛 `02` 連結）。
   - `reading_sessions/<YYYYMMDD_主題簡稱>/02_phase2_generation_blueprint.md`：進入 Phase 2 後依**時機 A（Layer 1 $\rightarrow$ Layer 2 $\rightarrow$ Layer 3）**漸進持久化生成選項、討論取捨理由、使用者客製細節覆寫與終端最小葉節點／交付清單。
   - `reading_sessions/<YYYYMMDD_主題簡稱>/02_outputs/`：僅存放正式交付成果（`.png`、`.pdf`、`.md`、`.pptx`、正式生成腳本 `.py` 或獨立網站結構）；驗收完畢立即調用 `verify_visual_outputs.py --cleanup` 清除臨時預覽檔。
   - `reading_sessions/_pending_skill_inspirations.md`：過程中若產生任何技能優化靈感（功能、視覺、筆風、文件去重或腳本改良），按格式 `[編號] | [來源] | [類別] | [目標檔案] | [觀察痛點與具體改良構想]` 暫存於此，絕不中斷主流程。
2. **Git 同步、網站發布與 Step E1～E3 技能升級閉環**：
   - 凡涉及 **作者公私雙倉庫同步（`--restore-private` / `--sync-private`）、Format E 獨立網站綁定（防嵌套 `.git` 衝突）、Medium 課堂作業繳交區塊**，或 **成果交付後執行 Step E1～E3 靈感查證、GitHub Issues 三通道回報與暫存檔刪除歸零**，請立即開啟 **[`setup/git_sync_and_evolution_protocol.md`](./setup/git_sync_and_evolution_protocol.md)** 依章執行！
