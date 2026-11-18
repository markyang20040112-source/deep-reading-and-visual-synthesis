# 首次啟用強制個人化初始化精靈（First-Time Onboarding Wizard — 外部新使用者專用）

> [!IMPORTANT]
> **【單一職責與永久退場機制（One-Time Gatekeeper & Zero Daily Token Overhead）】**
> 1. **作者雙電腦 100% 免觸發保護**：當本機 Git 身分驗證為技能作者本人（`"markyang20040112-source"`）或 `check_user_identity_and_load_prefs()` 判定 `is_owner == True` 時，`onboarding_completed` 永遠為 `true`，**日常執行嚴禁讀取本檔案，實現零額外 Token 消耗**！
> 2. **外部新使用者強制攔截與私人資產隔離（Strict Owner Asset Isolation）**：當外部使用者從 GitHub Clone 本技能首次執行時，因本機 Git 身分非 `markyang20040112-source`，系統**嚴格隱藏並隔離作者本人的私人色票（`Gephi · pastel`）與私人筆風庫（`config/owner_styles/*`）**，絕不提供給外部使用者直接選用，並強制進入本精靈完成專屬設定！
> 3. **一次設定、永久生效**：一旦新使用者完成以下 4 步初始化並寫入 [`../config/user_preferences.json`](../config/user_preferences.json)（將 `"onboarding_completed"` 設為 `true` 且綁定其本機 `"bound_git_user"`），往後每次啟動皆直接放行，不再載入本檔。

---

## 🛡️ 零、 若新使用者要求「跳過初始化／直接開始」之強制風險警告（Skip Warning Gate）

若外部新使用者在首次啟動時表示「不想設定、直接跳過」，AI **絕對不可靜默跳過或偷塞原作者私人色票／筆風**，必須先彈出以下具體副作用警告並請使用者二選一確認：

> ⚠️ **【跳過個人化初始化之具體副作用提醒】**
> 由於原作者的私人色票與私人筆風受擁有者隔離鎖保護，若您現在跳過初始化：
> 1. **圖表配色（Format D & E）**：將無專屬色票可用，只能臨時由 AI 以基礎中性藍灰生成，可能缺乏跨圖表一致的品牌／個人視覺辨識度。
> 2. **行文與微文案筆風（Slots 1～8）**：所有報告、圖譜卡片、簡報講稿與圖表標註將全部退回 `[AI_ADAPTIVE]` 通用預設，可能不符合您的個人寫作習慣或課程／工作規範。
> 3. **Git 自動同步**：預設將關閉（`"git_sync_mode": "none"`），不會自動幫您備份對話紀錄。
>
> 👉 請問您要：
> - **選項 A（推薦，僅需 1 分鐘）**：現在快速回答下方 4 個問題（沒想法的項目可直接選「交給 AI 動態預設 `[AI_ADAPTIVE]`」），立即生成專屬於您的色票與筆風檔！
> - **選項 B（請 AI 一鍵幫我隨機／依場景自動生成全套預設並完成初始化）**：只需告訴我您的主要用途（如：`學術研究`、`商業簡報` 或 `數據新聞專欄`），我立刻為您生成一套專屬色票與筆風並直接開始任務！

---

## 🧭 一、 五步互動式個人化初始化流程（Pre-Flight Check + 4-Step Onboarding Protocol）

當外部新使用者首次啟動本技能時，請先暫停主任務（但先將使用者已上傳之文章或 CSV 安全歸檔至 `reading_sessions/`），親切引導完成以下環境健檢與個人化設定：

### Step 0：分級環境健檢（Pre-Flight Environment Check）
啟動精靈時，AI 先在背景靜默執行一筆 Python 探針檢查環境套件（`python -c "import matplotlib, numpy, pandas"` 等）與 CLI 工具，並依以下**三級分類**向使用者簡潔回報缺少項目（**嚴禁未經同意就強制下載龐大套件**）：

| 工具分級 | 包含項目 | 什麼時候需要？ | 引導處置方式 |
| :--- | :--- | :--- | :--- |
| **1. 核心必備** | `Python 3.10+`、`matplotlib`、`numpy`、`pandas` | 幾乎所有模式都會用到（畫知識圖譜、統計圖表、CSV 三層分流） | 若有缺少，主動詢問：**「是否幫您一鍵執行 `pip install` 安裝這幾個核心套件？」** |
| **2. 格式選配** | • `python-pptx`（Format C 簡報 `.pptx`）<br>• `playwright` ＋ Chromium（Format B `.pdf` 編譯與預覽轉圖） | **僅於輸出 `.pptx` 或 `.pdf` 時需要**（例如僅寫 Medium 專欄或只看 PNG 圖表者免裝 Chromium） | 告知用途與缺少項目，由使用者決定**「現在一併安裝」**或**「先跳過，有需要該格式時再裝」** |
| **3. 雲端協作（選用）** | `git`、`gh` (GitHub CLI) | 僅用於「跨電腦同步」或「Format E 發布線上網站」 | **明確告知「完全沒有 Git 或 GitHub 帳號也能 100% 正常使用本技能（本機存檔＋匿名 Webhook 自動回報靈感）」**，不強迫安裝 |

---

### Step 1：建立專屬「分層顏色設定集（Chart Palette & Document Theme）」
> 🚫 **嚴格隔離鐵律**：公開倉庫僅提供中性預設基底與空白範本，**絕對禁止**將原作者私人色票列為選項給外部使用者挑選！一律引導新使用者透過下方方式自建專屬 CIELAB 色票！

請向新使用者提供以下 **3 種建立專屬色票的方式**（三選一）：
1. **方式 A（自選 2～4 個喜愛的主色 HEX 或顏色描述）**：
   - 請使用者輸入 2～4 個喜歡的色碼（或描述喜愛的色系，如「深海藍＋暖琥珀橘」、「森林綠＋大地棕」）。
   - AI 立即呼叫 `hcl_color_engine.build_palette_from_primary_hexes(hex_list, sync_js_path=".agents/skills/deep-reading-and-visual-synthesis/scripts/gephi_palette.js")`，透過 CIELAB 感知空間插值自動衍生出：4 個無序類別主色、4 個 `0.00` 零透明度極淺徽章底色、4 組 5 階循序色階、以及 9 階對稱發散色階，並同步更新 `gephi_palette.js`！
2. **方式 B（由 AI 依使用場景現場動態設計一套專屬色票）**：
   - 若使用者對配色沒概念，請告知主要場景（如：① 科技與商務決策、② 社會科學與公共政策、③ 自然科學與醫療實證、④ 溫暖人文專欄），由 AI 當場挑選 4 個互補均衡色相並呼叫 `build_palette_from_primary_hexes()` 生成專屬色票。
3. **方式 C（同時確認第二層 `document_theme` 文件與簡報佈景主題）**：
   - 詢問文件／簡報（Format A/B/C）偏好「現代深石板藍（`modern_academic_slate`）」或「人文暖白（`warm_editorial_ivory`）」，或依其主色自訂。

---

### Step 2：建立專屬「8 大全生成場景筆風設定檔（`config/user_styles/<style_id>.md`）」
> 🚫 **嚴格隔離鐵律**：**絕對禁止**讀取或複製 `config/owner_styles/` 下的作者私人筆風檔給外部使用者！一律讀取公開空白結構規範模板 **[`../config/styles/_style_schema_template.md`](../config/styles/_style_schema_template.md)** 為新使用者建立存放於 `config/user_styles/` 的專屬筆風檔。

請向新使用者提供以下 **3 種建立筆風的方式**（三選一，且支援建立多組筆風檔）：
1. **方式 A（貼上自己的歷史文章／報告段落，由 AI 逆向萃取專屬筆風）**：
   - 使用者貼上 1～3 段自己過去寫過最滿意的報告、專欄或簡報文字，AI 自動分析其人設語氣、段落節奏、開頭錨點習慣、標點偏好與常用詞，填入 `_style_schema_template.md` 的 **Slot 1 ～ Slot 8**（明確特徵標記為 `[USER_LOCKED]`，未涵蓋細項標記為 `[AI_ADAPTIVE]`）。
2. **方式 B（口述偏好規則，沒想法的細項設為 `[AI_ADAPTIVE]`）**：
   - 詢問使用者對以下關鍵維度有無特別偏好（沒想法可直接說「交給 AI 預設」）：
     - ① 整體語氣與展開順序（`Slot 1`：如結論先行、白話直覺先行、或嚴謹實證推進）
     - ② 卡片與表格條目開頭格式（`Slot 4`：如 `● 【四字錨點】`、動詞短語或直接敘述）
     - ③ 圖表模式偏好（`Slot 6`：`editorial_storytelling` 敘事圖解 vs. `pure_dataviz` 純資料視覺化 vs. `AI_ADAPTIVE`）
     - ④ 排版與禁用詞（`Slot 8`：PDF 偏好現代黑體 `modern_sans` 或標楷體首行縮排 `clreq_kaiti`、是否禁用驚嘆號、有無特定禁用詞）
3. **方式 C（完全無想法 —— 由 AI 現場生成全套 `[SCENARIO_PRESET]` + `[AI_ADAPTIVE]` 基礎筆風檔）**：
   - AI 依使用者的領域現場生成一份完整的 8 插槽筆風檔存入 `config/user_styles/default_user_style.md`，並提醒使用者：**「日後在任何對話中，您隨時可以用一句話（例如：『以後圖表標題不要用冒號』）局部熱修改這份筆風檔！」**

---

### Step 3：設定「Phase 2 三層決策確認關卡」之詢問偏好（`confirmation_gate`）
詢問使用者在每次進入 Phase 2 生成成果前，針對 **確認關卡各設定維度（1. 產出格式範圍、2. 筆風檔、3. 顏色集、4. 圖表設計光譜／逐步導學互動節奏、5. 版面細節）**：
- **預設推薦（`"ask_every_time"`）**：每次生成前由 AI 列出建議清單向您確認後再動工（最靈活、零誤判）。
- **鎖定預設免問（`"auto_apply_default": true`）**：若某幾個維度（例如顏色集或筆風檔）固定不變，可設為自動套用免問以加快速度。

---

### Step 4：設定本機／Git 同步與跨使用者靈感回報偏好（`git_and_feedback`）
1. **無 Git 帳號支援與同步模式（`git_sync_mode`）**：
   - 若新使用者**沒有 Git / GitHub 帳號**，或不需要將閱讀紀錄推送到遠端，直接設為 **`"none"`**（僅保存在本機 `reading_sessions/`），並以本機系統帳號（`bound_local_user`）或自訂暱稱作為個人設定識別碼，確保下次開啟免重複初始化。
   - 若新使用者有自己的個人 Git 倉庫，可設為 `"auto_push_main"` 並協助將 `git remote set-url origin` 指向其個人倉庫。
2. **跨使用者靈感自動回報（`upstream_feedback_repo` & `feedback_webhook_url`）**：
   - 保持指向原作者公開倉庫 `"markyang20040112-source/deep-reading-and-visual-synthesis"` 與匿名 Apps Script Webhook，當使用者在日常使用中累積技能優化靈感時，**即使沒有 GitHub 帳號**，亦可於 Step E1 透過 `scripts/report_skill_feedback.py` 一鍵背景自動回報（自動加上 `[FR-*]` 固定分類代號）協助技能演進。

---

## ✅ 二、 完成寫入與無縫接回主任務

完成上述設定後：
1. 將新使用者的專屬色票、筆風路徑、Phase 2 決策確認偏好、本機識別（有 Git 者寫入 `"bound_git_user"`；無 Git 者寫入 `"bound_local_user"` 與 `"bound_git_user": null`）與 **`"onboarding_completed": true`** 完整寫入 [`../config/user_preferences.json`](../config/user_preferences.json)（並確保移除任何 `owner_only: true` 條目）。
2. 立即關閉本精靈，無縫接回使用者原本上傳的文章或資料集任務（依 [`../SKILL.md`](../SKILL.md) 進入 Phase 1 或 Phase 2）！
