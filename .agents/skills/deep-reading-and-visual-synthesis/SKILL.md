---
name: deep-reading-and-visual-synthesis
description: >-
  Theory-grounded 5-step Socratic reading and 3-loop Data Codebook storytelling/10-distribution-chart tutor (Phase 1),
  followed by a tree-structured Phase 2 workflow: thin trunk (format selection, self-sufficient embedded-diagram boundaries, hybrid global style/color defaults, trunk+branch blueprint) branching into 5 independent format folders (A diagrams, B PDF/Medium, C DISCAS slides, D 5-family 30+ charts, E zero-backend dashboards), each running `01_plan -> 02_build -> 03_qa` with per-format Subagent isolation or sequential fallback, plus empirical skill evolution & GitHub Issues feedback.
  Activate when a user uploads or discusses an article, business case, research paper, report, dataset + Data Codebook (資料說明書), or video transcript for deep reading, critical analysis, statistical distribution tutoring, data journalism, or visual synthesis.
---

# 深度閱讀引導與視覺化知識統整 — 樹狀總控台 (Master Router)

> [!IMPORTANT]
> **【第零關：公私雙倉庫隔離、身分驗證、雙機還原、外部初始化與 30 天更新】**
> 本技能採 **Public（規範／引擎／範本）＋ Private（私人資產與 `reading_sessions/`，`.gitignore` 隔離）** 雙倉庫架構。啟動時檢核 `config/user_preferences.json`（範本 [`user_preferences.template.json`](./config/user_preferences.template.json)，呼叫 `hcl_color_engine.check_user_identity_and_load_prefs()`）：
> 1. **作者（`markyang20040112-source`）**：未還原時自動從 Private 還原 `config/user_preferences.json` 與 `config/owner_styles/`，`"onboarding_completed"` 鎖 `true`，**日常嚴禁讀 [`onboarding_wizard.md`](./setup/onboarding_wizard.md)**！
> 2. **外部新用戶**：無個人設定時**強制開 [`onboarding_wizard.md`](./setup/onboarding_wizard.md)** 建專屬色票與 `config/user_styles/` 筆風。
> 3. **30 天無損更新檢查**：依 `update_check.interval_days: 30` 呼叫 `check_skill_updates.py`，保護 `config/` 與 `reading_sessions/*`。

> [!IMPORTANT]
> **五大核心運作鐵律（Core Operational Laws）**：
> 1. **雙階段隔離與按需載入**：Phase 1 先讀 [`phase1_socratic_reading_guide.md`](./phase1_reading/phase1_socratic_reading_guide.md)，再二擇一開 [`mode1`](./phase1_reading/mode1_article_socratic_protocol.md) 或 [`mode2`](./phase1_reading/mode2_dataset_codebook_protocol.md)（僅模式 2 軌道 C 連動 [`family4`](./formats/format_d_charts/families/family4_distribution_and_density.md)）；Phase 1 嚴禁預讀其他 `shared/` 或 `formats/`。
> 2. **Phase 2 樹狀主幹分枝 ＋ Subagent 隔離（單執行緒備援）**：進 Phase 2（Fast-Track 先存 `00_source_article.md` 與原始 `data/<原檔名>.csv`）先開 **[`shared/router.md`](./shared/router.md)** 拍板格式（A～E）與全域預設（[`style_and_color_core.md`](./shared/style_and_color_core.md)）➔ 僅開選定格式 `formats/format_*/01_plan.md` 寫樹狀藍圖 ➔ 各格式 `02_build*` ＋ `03_qa` 優先採 **Subagent 隔離**，或 **`D ➔ A ➔ B ➔ C ➔ E` 單執行緒逐項確認**（備援），未選格式 0 讀取！
> 3. **混合式表達三支柱 100% 穿透**：主幹訂定「設計光譜（模式 1/2/3）× 筆風（`Slot 1～8`）× 分層配色」全域預設，各分枝 `01_plan.md` 可局部覆寫並 100% 穿透產出。
> 4. **底層引擎黑盒鐵律**：`scripts/*.py` 與 `scripts/*.js` API 契約載於各 `02_build*.md`，**日常直接 `import` 呼叫，嚴禁對 `scripts/` 讀原始碼（除錯除外）**！
> 5. **靈感生命週期**：優化靈感僅暫存 `reading_sessions/_pending_skill_inspirations.md` 並附一句提示，**嚴禁中斷主流程或私自改檔**；驗畢再按需開 [`git_sync_and_evolution_protocol.md`](./setup/git_sync_and_evolution_protocol.md) 跑 Step E1～E3。

---

## 一、 樹狀檔案地圖（Tree File Map）

| 模組路徑 | 唯一職責 | 開啟時機 |
| :--- | :--- | :--- |
| **[`SKILL.md`](./SKILL.md)** | 總控台：Gate 0、五大鐵律、樹狀地圖與歸檔規則。 | 啟動預設載入。 |
| `config/` ([範本](./config/user_preferences.template.json) · [筆風契約](./config/styles/_style_schema_template.md)) | 個人化範本與 8 插槽筆風契約（私人資產隔離於 `owner_styles/`、`user_styles/`）。 | 驗身與定裝讀單一筆風檔。 |
| `setup/` ([初始化](./setup/onboarding_wizard.md) · [同步進化](./setup/git_sync_and_evolution_protocol.md)) | 外部初始化；雙倉庫同步、Format E 部署、Medium 繳交與 Step E1～E3。 | 外部首次／結案進化按需。 |
| `phase1_reading/` ([總路由](./phase1_reading/phase1_socratic_reading_guide.md) · [Mode 1](./phase1_reading/mode1_article_socratic_protocol.md) · [Mode 2](./phase1_reading/mode2_dataset_codebook_protocol.md)) | **Phase 1**：Stage 0 素材擷取、四大分流、`01` 落盤、五步思辨、CSV 三迴路。 | 先總路由，再二擇一。 |
| `shared/` (**[router](./shared/router.md)** · [blueprint](./shared/blueprint_template.md) · [style/color](./shared/style_and_color_core.md) · [cognition](./shared/visual_cognition_core.md) · [模式 2](./shared/editorial_narrative_spec.md) · [模式 3](./shared/creative_armory/INDEX.md)) | **Phase 2 主幹與共用核心**：格式路由與自給自足邊界、樹狀藍圖、混合式風格色票預設、跨格式認知底盤、解耦模式 2/3。 | 進 Phase 2 開 `router.md`；執行讀 `cognition`，開模式 2/3 才讀專檔。 |
| `formats/` (**[A](./formats/format_a_diagram/01_plan.md)** · **[B](./formats/format_b_document/01_plan.md)** · **[C](./formats/format_c_slides/01_plan.md)** · **[D](./formats/format_d_charts/01_plan.md)** · **[E](./formats/format_e_dashboard/01_plan.md)**) | **五大獨立格式分枝**：各含 `01_plan ➔ 02_build* ➔ 03_qa`（A 圖譜；B PDF 含內建 A4 簡圖／Medium 互斥；C DISCAS＋Step 3/4A＋方案 C QA；D 5 家族 30+ 圖；E 零後端儀表板＋直推部署）。 | **僅開選定格式分枝**（未選 0 讀取）。 |
| [`scripts/`](./scripts/hcl_color_engine.py) | **黑盒引擎**：`ingest_source_material`、`hcl_color_engine`、`gephi_palette.js`、`generate_mindmap`、`pdf_report_engine`、`pptx_slide_engine`、`verify_visual_outputs`、`report_skill_feedback`、`check_skill_updates`。 | 擷取、繪圖、編譯、驗收或同步直接呼叫。 |
| **[`THEORY_ARCHIVE.md`](./THEORY_ARCHIVE.md)** | 實證科學理論封存庫（T01～T26）。 | 查理論出處或 Step E3。 |

---

## 二、 專案歸檔與結案規則（`reading_sessions/`）

1. **嚴禁存入 `.agents/skills/`**，專案統一歸於 `reading_sessions/<YYYYMMDD_主題簡稱>/`：
   - `data/<原檔名>.csv`：**原始 CSV 原封不動存入，嚴禁改動**。
   - `00_source_article.md`（或 `00_drive_source_files/`）：收到原文或《資料說明書》立即存檔。
   - `01_phase1_socratic_log.md`：Phase 1 獨立紀錄（不回寫 Phase 2，不附 `02` 連結）。
   - `02_phase2_generation_blueprint.md`：樹狀單檔藍圖（`## 0` ＋ 選定之 `## Format X 分枝藍圖`）；選 C 另存 `02c_slide_spec_lock.json`，選 D/E 另存 `02_color_registry.json`。
   - `02_outputs/`：僅存正式交付物與正式腳本；驗畢立刻執行 `verify_visual_outputs.py --cleanup` 清除暫存檔。
   - `reading_sessions/_pending_skill_inspirations.md`：`[編號] | [來源] | [類別] | [目標檔案] | [觀察痛點與具體改良構想]`。
2. **雙倉庫同步、網站發布與 Step E1～E3**：全格式確認後，按需開 [`setup/git_sync_and_evolution_protocol.md`](./setup/git_sync_and_evolution_protocol.md)。
