# 公私雙倉庫 Git 同步、獨立儀表板發布與技能優化靈感進化協定（Git Sync, Web Deployment & Evolution Protocol）

> **單一職責定位（Single Responsibility）**：本檔由 [`../SKILL.md`](../SKILL.md) 按需拆出，專責處理 **① 作者公私雙倉庫自動同步與跨電腦一鍵還原**、**② Format E 數據儀表板獨立 Git 儲存庫綁定（含防嵌套 `.git` 子模組衝突）**、**③ Medium 每週一圖單檔連結推送與課堂繳交區塊**，以及 **④ 技能優化靈感之 Step E1～E3 查證、GitHub Issues 三通道自動回報與暫存檔歸零閉環**。**日常閱讀與畫圖階段不開啟本檔，唯有準備執行 Git 同步／網站發布／Step E1～E3 技能進化時才按需讀取**！

---

## 一、 公私雙倉庫架構與跨電腦無損同步指令（Owner Dual-Repo Sync）

1. **雙倉庫徹底隔離架構**：
   - **外層公開倉庫（Public）**：`https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis.git`。透過根目錄 `.gitignore` 嚴格排除 `reading_sessions/`、`config/owner_styles/` 與 `config/user_preferences.json`，僅包含核心技能規範、渲染引擎與空白範本。
   - **內層私人資產倉庫（Private）**：`reading_sessions/` 內綁定 `https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis-Private-.git`，同步所有 `reading_sessions/` 專案與 `reading_sessions/_owner_private_config/`（`user_preferences.json` 與 `owner_styles/*.md`）。
2. **一鍵還原與雙向同步 CLI 指令**：
   - **另一台電腦一鍵還原私人設定與紀錄**：
     ```bash
     python .agents/skills/deep-reading-and-visual-synthesis/scripts/hcl_color_engine.py --restore-private
     ```
   - **階段完成／隨時跨裝置檢查點同步（Checkpoint Sync）**：
     當 `git_sync_mode == "auto_push_main"` 且完成第二階段產出，或作者要求「先同步到 Git／我要換裝置」時，先將最新進度寫入 `01_phase1_socratic_log.md`（Phase 1）或 `02_phase2_generation_blueprint.md`（Phase 2），再執行：
     ```bash
     python .agents/skills/deep-reading-and-visual-synthesis/scripts/hcl_color_engine.py --sync-private -m "wip(session): checkpoint sync for device handoff"
     ```
     *(註：唯有改動 `.agents/skills/` 核心技能檔（Step E3）時，才於工作區根目錄同步推送公開倉庫；外部使用者若設 `git_sync_mode == "none"` 則僅存本機。)*

---

## 二、 Format E（數據儀表板）獨立 Git 儲存庫綁定與網站發布規範

每當生成 Format E 互動式數據儀表板時，依 **[`../phase2_output/data_dashboard_spec.md`](../phase2_output/data_dashboard_spec.md)** 第四節執行：
1. 確保已封裝完整 Git-Ready 靜態結構（純 `./` 相對路徑、`css/style.css`、`js/gephi_palette.js`、`js/dashboard.js`、`data/<dataset>_data.js` & `.json`、`.nojekyll`、`.gitignore`、`README.md`）。
2. 驗收完畢後，主動詢問使用者是否立即綁定獨立遠端儲存庫或透過 `gh` CLI 自動建立公開倉庫並啟用 GitHub Pages。
3. **【防嵌套 `.git` 子模組衝突鐵律（Nested Gitlink Prevention）】**：當儀表板目錄位於 `reading_sessions/` 內時，若於子目錄執行 `git init` 完成獨立推送後，**必須立即移除子目錄內的 `.git` 資料夾**（PowerShell：`Remove-Item -Recurse -Force .git`；Bash：`rm -rf .git`），或改採主倉庫 `git subtree split --prefix="..." -b dashboard-deploy` 推送，嚴防外層私人倉庫將該儀表板目錄誤判為空 `gitlink` 子模組！

---

## 三、 Medium 每週一圖專欄之 GitHub 單一檔案推送與課堂繳交區塊

執行 **[`../phase2_output/medium_column_spec.md`](../phase2_output/medium_column_spec.md)** 工作流時：
1. 將 Phase 1 完整討論與收斂軌跡詳實寫入 `reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md`；Phase 2 三層決策與取捨理由則依時機 A 記錄於同目錄 `02_phase2_generation_blueprint.md`（無需於 `01_phase1_socratic_log.md` 或下方課堂繳交區塊額外附掛 `02` 連結）。
2. 依使用者倉庫設定同步（注意：作者私人倉庫預設不對外公開；若課堂繳交需公開檢視連結，請另以 Secret Gist 或獨立公開倉庫頁分享該單一檔案）。
3. 在回覆結尾輸出符合課堂 Google Doc（[每週一圖：作業範例](https://docs.google.com/document/d/1ZQUB9kwHqW162xjAFyPbVNEs-kJQteMvxohhGVhCad0/edit?usp=sharing)）格式的一鍵複製繳交區塊：
   ```text
   {學號} {姓名}
   {您的 medium.com 報導連結}
   {您在 Gemini 網頁版製作資料說明書的分享連結 (AI 對話 1)}
   https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis/blob/main/reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md
   ```

---

## 四、 技能優化靈感之「紀錄、運用、GitHub Issues 回報與刪除」三步閉環（Step E1 ～ Step E3）

1. **觸發與暫存規則**：對話進行中察覺可優化處時，僅寫入 `reading_sessions/_pending_skill_inspirations.md`（格式：`[編號] | [來源] | [類別] | [目標檔案] | [觀察痛點與具體改良構想]`）並附註一句提示，**嚴禁中途離題或私自改檔**。
2. **最終成果驗收後之三步進化閉環（Step E1 ～ Step E3）**：
   - **Step E1（提議本機升級 ＋ 一鍵回報原作者 GitHub Issues）**：
     列出暫存靈感，詢問使用者：(1) 是否同意檢索文獻評估升級本機技能庫？(2) 是否呼叫 [`../scripts/report_skill_feedback.py`](../scripts/report_skill_feedback.py) 以固定代號格式（`[FR-FLOW]` / `[FR-VIS]` / `[FR-STYLE]` / `[FR-CODE]` / `[FR-DOC]` / `[FR-BUG]`）回報至原作者公開倉庫（**`https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis/issues`**）？（支援通道 A `gh issue create`、通道 B Google Apps Script Webhook、通道 C 預填網址）。
   - **Step E2（查證文獻與修改方案確認）**：檢索實證研究或工程標準，回報「(1) 實證依據、(2) 預計修改檔案與具體條文」待使用者拍板。
   - **Step E3（無損寫入 ＋ 跨檔連動同步 ＋ 模式 3 成功創意案例回饋入庫閉環）**：將理論補入 [`../THEORY_ARCHIVE.md`](../THEORY_ARCHIVE.md)，將精煉規則寫入對應單一職責檔。
     - **【格式 D ⇄ 格式 E ⇄ 分配圖形 ⇄ 顧問大腦強制連動條款】**：若更新涉及圖表配色、編碼鐵律或選型邏輯，必須同步更新 `quantitative_chart_spec.md`、`data_dashboard_spec.md`、`advisors/layer2_advisor_de_chart.md`、對應之 `chart_family*.md`、`scripts/hcl_color_engine.py` 與 `scripts/gephi_palette.js`！
     - **【模式 3 成功創意案例回饋入庫閉環（Creative Armory Case Feedback-to-Library Loop）】**：當某次 **模式 3 (`bespoke_metaphor`)** 專案原創出全新的具象材質、純幾何物理結構（Form-as-Metaphor）或空間隱喻視覺方案，並經使用者實戰驗收勝出後，於 Step E3 依下列兩步沉澱入庫：
       1. **建立單一原子案例卡**：將去專案化之適用時機、防誤導邊界、核心 API／原生實作骨架寫成 1 份獨立 `.md` 檔案，放入 [`../phase2_output/creative_armory/cases/`](../phase2_output/creative_armory/cases/) 下對應之視覺編碼分類目錄（`01_texture_and_container/`、`02_structural_geometry/` 或 `03_spatial_and_thematic/`）。
       2. **僅追加 1 行單行索引**：於 [`../phase2_output/creative_armory/INDEX.md`](../phase2_output/creative_armory/INDEX.md) 索引表追加**恰好 1 行摘要與連結**，嚴禁將長篇實作細節複製進 `INDEX.md`、`SKILL.md` 或 `layer3_advisor_design_style_color.md`，確保案例庫隨實戰持續擴充時仍維持 $O(1)$ 注意力與極低 Token 負擔。
3. **🗑️ 暫存檔清理與歸零刪除時機**：於 Step E1/E2 遭使用者否決或於 Step E3 寫入完成後，**當下立即從 `reading_sessions/_pending_skill_inspirations.md` 移除該筆已完成／已否決之靈感**；若清單中僅剩 `[LOCKED / DEFERRED]` 封存靈感則保留檔案供日後解鎖，若已無任何剩餘條目則**當下立即刪除 `reading_sessions/_pending_skill_inspirations.md`** 確保暫存區歸零！
