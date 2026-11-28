# Deep Reading & Visual Synthesis (深度閱讀引導與視覺化知識統整技能庫)

本倉庫包含 **「深度閱讀引導與視覺化知識統整（Deep Reading & Visual Synthesis）」** Agent 技能之完整樹狀模組化規範、科學渲染引擎，以及公私雙倉庫隔離範本架構。

---

## 🏗️ 全系統架構總覽圖與完整介紹（System Architecture Overview）

![Deep Reading & Visual Synthesis 核心架構圖](技能說明與架構圖/skill_architecture_overview.png)

> 📖 **想由淺入深了解這個技能怎麼用、有哪些設計巧思，以及各 `.md` / `.py` 檔案的詳細分工？**
> 請閱讀 👉 **[技能介紹與架構指南（白話功能解說 ＋ 完整架構流程與模組職責）](技能說明與架構圖/技能介紹與架構指南.md)**

---

## 🗺️ 倉庫全景檔案地圖與單一職責分工 (Project File Map & Single Responsibility)

本技能庫採 **「樹狀主幹分枝（Thin Trunk + 5 Independent Format Branches）＋ 分格式 Subagent 隔離（單執行緒備援）＋ 混合式表達三支柱 ＋ 底層黑盒引擎」** 設計，確保 AI 在極低注意力負荷下維持高穩定度的知識萃取與出版級視覺渲染：

```text
deep-reading-and-visual-synthesis/
├── README.md                                                 # [人類導覽] 倉庫總覽、樹狀檔案地圖與執行階段邊界說明
├── 技能說明與架構圖/                                           # [給使用者看的白話介紹與架構圖]
│   ├── skill_architecture_overview.png                       # [架構圖] 清爽白話版核心架構總覽圖（10 秒看懂技能功用）
│   ├── 技能介紹與架構指南.md                                   # [完整介紹] 壹、白話功能與流程解說 ＋ 貳、詳細架構流程與各 .md/.py 定位
│   ├── generate_architecture_diagram.py                      # [生圖腳本] 生成核心架構圖的 Python 腳本（含防撞檢查）
│   └── architecture_diagram_spec.md                          # [規格提示詞] 架構圖構圖規格、色票與日後交給 AI 修改重繪之提示詞
└── .agents/skills/deep-reading-and-visual-synthesis/         # 【核心技能定義區 — 採樹狀分枝與 O(1) 按需載入】
    ├── SKILL.md                                              # [總控台 <=8KB] Gate 0 身分驗證門神、五大運作鐵律、樹狀地圖與歸檔規範
    ├── THEORY_ARCHIVE.md                                     # [文獻庫] 認知心理學、視覺感知、投影光學與排版工學實證文獻封存庫 (T01~T26)
    ├── config/                                               # [設定範本] 公開範本與 8 插槽筆風契約（私人色票/筆風由 .gitignore 隔離）
    │   ├── user_preferences.template.json                    # 個人化設定公開範本（含確認關卡、分層色票、筆風映射與 Git 同步設定）
    │   ├── styles/_style_schema_template.md                  # 8 大全場景筆風控制契約（Slots 1～8）標準範本
    │   └── user_styles/.gitkeep                              # 外部使用者自訂筆風存放目錄
    ├── setup/                                                # [初始化與同步協定]
    │   ├── onboarding_wizard.md                              # 外部新使用者首次啟動強制初始化精靈
    │   └── git_sync_and_evolution_protocol.md                # 公私雙倉庫同步、Format E 防嵌套開站、Medium 繳交與 Step E1~E3 進化閉環
    ├── phase1_reading/                                       # [階段一：深度閱讀與數據探索]
    │   ├── phase1_socratic_reading_guide.md                  # Stage 0 素材嗅探正規化 ＋ 四大輸入模式路由與 01_phase1_socratic_log.md 持久化
    │   ├── mode1_article_socratic_protocol.md                # 模式 1/3/4：Step 0～5 蘇格拉底鷹架、圖爾敏論證與跨域類比
    │   └── mode2_dataset_codebook_protocol.md                # 模式 2：CSV＋《資料說明書》「讀取—分析—討論」三迴路與 Track A/B/C 導學
    ├── shared/                                               # [階段二主幹與共用元件 — 極簡主幹，未選格式零讀取]
    │   ├── router.md                                         # [主幹總路由 <=8KB] 格式分枝選擇、自給自足邊界鐵律、Subagent 隔離封包與單執行緒備援
    │   ├── blueprint_template.md                             # [樹狀藍圖範本 <=6KB] 02_phase2_generation_blueprint.md 主幹 (## 0) ＋ 分枝切片範本
    │   ├── style_and_color_core.md                           # [混合式定裝核心 <=8KB] 全域預設三支柱（模式 1/2/3 × 筆風 × 分層色票）＋ 分枝局部覆寫
    │   ├── visual_cognition_core.md                          # [跨格式底盤] 無損擴展哲學、表達三支柱、事實與因果保真底線、避頭尾保護與 75-20-5
    │   ├── editorial_narrative_spec.md                       # [模式 2 專檔] 資料八編輯室 5 大技法、Format B 社論組件與 A/C/E 敘事延伸（徹底解耦）
    │   └── creative_armory/                                  # [模式 3 開放式創意隱喻武器庫 — O(1) 單行索引＋按需原子案例卡]
    │       ├── INDEX.md                                      # 模式 3 唯一輕量入口：開放式 Form-as-Metaphor 五大底線 ＋ 單行案例索引表
    │       └── cases/                                        # 依視覺編碼分類之原子案例卡（按需單開，成功案例可持續回饋入庫）
    │           ├── 01_texture_and_container/                 # glass_liquid_bars.md、masked_texture_wedges.md、sprite_coord_scatter.md
    │           ├── 02_structural_geometry/                   # 純向量幾何結構隱喻開放成長目錄（Form-as-Metaphor 預留庫）
    │           └── 03_spatial_and_thematic/                  # thematic_palette_frame.md、diagram_spatial_metaphors.md
    ├── formats/                                              # [階段二五大獨立格式分枝 — 每枝內聚 01_plan ➔ 02_build* ➔ 03_qa]
    │   ├── format_a_diagram/                                 # [Format A 知識圖譜]
    │   │   ├── 01_plan.md                                    # 無損分圖 (01/02/03+)、T1~T5 拓撲診斷與分枝覆寫
    │   │   ├── 02_build.md                                   # 23.8"×12.6"–15.4" 瑞士網格圖譜 (T1~T5) ＋ Format B 7.44" 直向簡圖 API
    │   │   └── 03_qa.md                                      # 零文字碰撞預檢、零穿線／真弧頂置中／避頭尾／清暫存驗收清單
    │   ├── format_b_document/                                # [Format B 報告與專欄]
    │   │   ├── 01_plan.md                                    # 文體 1~4 PDF（含字體 modern_sans / clreq_kaiti 與內建 A4 簡圖）vs. 文體 5 Medium
    │   │   ├── 02_build_pdf.md                               # 文體 1~4：A4 自適應分頁印刷 PDF、注意力波峰波谷與內建 7.44" 直向簡圖
    │   │   ├── 02_build_medium.md                            # 文體 5：<=1,600 字純淨原生 Markdown 專欄（禁 HTML/表格、免 PDF）
    │   │   └── 03_qa.md                                      # 雙軌驗收：PDF 全頁轉圖檢查 vs. --verify-medium 分離計字與來源驗證
    │   ├── format_c_slides/                                  # [Format C 16:9 視距自適應簡報]
    │   │   ├── 01_plan.md                                    # Step 1 北極星 AST、DISCAS 視距地板、單一議題清單 ＋ 模式 3 Tier 1~3 / DNA 卡
    │   │   ├── 02_build.md                                   # 五步管線、02c_slide_spec_lock.json、五大家族 13 版型 (F1-A~F5-C)、去方塊與 API
    │   │   └── 03_qa.md                                      # 方案 C 三階內部品管（verify_pptx_structure＋4×4 接觸表＋2×2 四宮格＋高風險滿版精檢）
    │   ├── format_d_charts/                                  # [Format D 量化統計圖表 — 5 大家族 30+ 圖型]
    │   │   ├── 01_plan.md                                    # 4D 資料快篩 × 8 溝通意圖 × 30+ 圖表決策樹、T25 選型與 D➔C `*_slide.png` 銜接
    │   │   ├── 02_build_core.md                              # Format D⇄E SSOT：編碼誠實三鐵律、8 元件檢核、配色 SSOT、02_color_registry.json 與 API
    │   │   ├── 03_qa.md                                      # 三層分流 assert、文字碰撞預檢、--verify-colors 鎖色與 8 元件實地驗收
    │   │   └── families/                                     # 按需單開 1～2 個圖表家族微檔（未選家族 0 讀取）
    │   │       ├── family1_ranking_and_deviation.md          # 克里夫蘭點陣、棒棒糖、啞鈴＆雙向動量向量箭頭、斜坡、子彈、蝴蝶金字塔、柏拉圖
    │   │       ├── family2_trend_and_comparison.md           # 共用基線剪刀差折線＋面積帶、空間重力斷崖、時期色帶折線、配對雙柱、面積、甘特
    │   │       ├── family3_composition_and_flow.md           # 4+1 堆疊、中心 KPI 環形、馬賽克雙維圖、瀑布、樹圖、旭日、桑基/弦圖
    │   │       ├── family4_distribution_and_density.md       # 10 大分配與密度圖形 ＋ 背景基準分面 (Context Overlay) 8 鐵律與逐步導學
    │   │       └── family5_multivariate_and_spatial.md       # 全樣本波士頓四象限氣泡矩陣（類別深色箭頭指引線）、熱力表、雷達、主圖＋角落副卡
    │   └── format_e_dashboard/                               # [Format E 互動數據儀表板]
    │       ├── 01_plan.md                                    # 呈現模式 A/B/C 動態選型、內部圖表連動、模式 2/3 前端組件與部署目標規劃
    │       ├── 02_build.md                                   # 零後端自包含前端、CSS `:root` + `gephi_palette.js`、24"×14" 全景圖與雲端直推部署
    │       └── 03_qa.md                                      # --verify-dashboard 封裝體檢、--verify-colors 鎖色、互動／CSV BOM 與靜態圖驗收
    ├── scripts/                                              # 【底層黑盒擷取、渲染、色彩、圖表、驗收與進化引擎 — 免讀原始碼直接呼叫】
    │   ├── ingest_source_material.py                         # Stage 0 四合一素材黑盒擷取引擎（網頁 URL / YouTube 字幕 / PDF / DOCX → 00_source_article.md）
    │   ├── hcl_color_engine.py                               # 統一相容入口門面（轉接 color_core / color_registry / owner_sync / chart_* 各模組）
    │   ├── color_core.py                                     # CIELAB/HCL 色彩科學、全域色票契約、主題衍生與前端 JS 匯出核心
    │   ├── color_registry.py                                 # 跨圖工作階段類別色彩登記表（02_color_registry.json 持久化鎖色）
    │   ├── owner_sync.py                                     # 使用者身分識別與公私雙倉庫同步 CLI
    │   ├── chart_data.py                                     # 輕量 DataFrame、數值/NA 解析與三層 CSV 分流引擎
    │   ├── chart_common.py                                   # CJK 字型設定、黃金畫布工廠 setup_chart_canvas、despine_axes、聚光燈配色與 1D 防撞共用工具
    │   ├── chart_editorial.py                                # 資料八編輯室敘事組件（膠囊基準線、時期色帶、角落排行卡、四層底註）
    │   ├── chart_family1_ranking.py                          # 圖表家族 1 引擎（克里夫蘭點陣圖、啞鈴/雙向動量箭頭圖、斜坡圖、子彈圖）
    │   ├── chart_family2_trend.py                            # 圖表家族 2 引擎（共用基線剪刀差折線＋面積帶、配對雙柱＋差距標註）
    │   ├── chart_family3_composition.py                      # 圖表家族 3 引擎（Marimekko 雙維佔比圖、瀑布圖）
    │   ├── chart_family4_distribution.py                     # 圖表家族 4 引擎（裁切 KDE、背景基準分面與分布輔助函式）
    │   ├── chart_family5_multivariate.py                     # 圖表家族 5 引擎（全樣本波士頓四象限氣泡矩陣＋指引線）
    │   ├── chart_creative_armory.py                          # 模式 3 創意隱喻圖（液體容器柱、遮罩紋理扇形、圖示散佈）
    │   ├── gephi_palette.js                                  # 前端 JS 色彩 SSOT、CIELAB 插值、entityColors 查詢與 deriveThematicPalette (UMD/Browser/Node)
    │   ├── generate_mindmap.py                               # Format A 出版級繁體中文知識圖譜引擎 ＋ Format B 7.44" A4 直向簡圖 API
    │   ├── pdf_report_engine.py                              # Format B A4 自適應分頁 CSS 生成器與 Playwright PDF 編譯引擎
    │   ├── pptx_slide_engine.py                              # Format C 16:9 統一相容入口門面（底層模組位於 pptx_engine/）
    │   ├── verify_visual_outputs.py                          # PDF/PPTX 轉圖、Medium/網站/色彩登記表驗收與清理門面（Format C QA 位於 pptx_engine/qa.py）
    │   ├── pptx_engine/                                      # Format C 16:9 五大家族 13 版型與方案 C QA 套件
    │   │   ├── tokens.py                                     # 主題載入、DISCAS 字級階梯、Design Tokens 與 OOXML 底層
    │   │   ├── text_layout.py                                # Pillow 微軟正黑體實寬量測、Kinsoku 避頭尾與幾何優先縮放
    │   │   ├── media_omml.py                                 # Playwright/Chrome 300 DPI SVG 轉圖與原生 <m:oMath> 公式
    │   │   ├── primitives.py                                 # Zone 1/3、全域光學垂直平衡、三層表頭與封面/過場
    │   │   ├── layouts_data.py                               # F4-A/B、F5-A/B/C 與 Mode 3 Tier 1 幾何原語
    │   │   ├── layouts_narrative.py                          # F1-C、F2-A/B/C 與 F3-A/B
    │   │   ├── spec_pipeline.py                              # 版型推薦、序列驗證、Step 4A 預覽、確定性渲染與保真檢查
    │   │   └── qa.py                                         # 方案 C 接觸表/2×2 四宮格、單頁重繪與結構/碰撞體檢
    │   ├── report_skill_feedback.py                          # 技能優化靈感三通道自動化 GitHub Issues 回報工具
    │   └── check_skill_updates.py                            # 30 天節流之無損技能更新檢查工具
    └── tests/
        ├── run_all.py                                        # 一鍵執行全部 7 套安全網測試之總入口
        ├── test_color_registry.py                            # 跨圖類別色彩登記表與繪圖模組回歸測試套件
        ├── test_charts_regression.py                         # 全圖表渲染、零文字碰撞與家族 2/5 鎖色回歸測試
        ├── test_pdf_pipeline.py                              # Format B PDF 自適應分頁與單瀏覽器重用測試
        ├── test_mindmap_and_ingest.py                        # Format A 延遲載入出圖與素材擷取離線測試
        ├── test_pptx_pipeline.py                             # Format C 五大家族 13 版型端到端渲染與方案 C QA 測試
        ├── test_dashboard_bundle.py                          # Format E Deploy-Ready 封裝與防嵌套 .git 測試
        └── test_md_architecture.py                           # 樹狀 .md 架構完整性、零斷鏈、零舊路徑與體積紅線測試
```

---

## 📋 核心執行階段與嚴格邊界 (Execution Phases & Strict Boundaries)

| 執行階段 | 讀取檔案順序 | 核心職責（管什麼） | 嚴格邊界（不管什麼／禁止事項） |
| :--- | :--- | :--- | :--- |
| **0. Gate 0 啟動門神** | `SKILL.md` | 身分驗證與公私雙倉庫隔離（作者還原私人設定／新用戶導向 `onboarding_wizard.md`）、30 天更新節流與靈感暫存規則。 | 不存放具體提問話術或視覺排版參數；私人設定與 `reading_sessions/` 嚴格受 `.gitignore` 隔離。 |
| **1. 第一階段 (Phase 1)**<br>*(深度閱讀／數據探索)* | `phase1_socratic_reading_guide.md`<br>$\rightarrow$ `mode1_*` 或 `mode2_*` | 先執行 **Stage 0 垂直工序**（調用 `ingest_source_material.py` 自動將 URL / YouTube 字幕 / PDF / DOCX 轉為 `00_source_article.md`），再二擇一載入子協定執行 5 步蘇格拉底思辨或 CSV 三迴路分析，即時寫入 `01_phase1_socratic_log.md`。 | **嚴禁提前讀取 `shared/` 或 `formats/` 任何檔案**（僅模式 2 軌道 C 按需連動 `family4`）；嚴禁將大型 CSV 直接讀入 LLM 上下文消耗 Token。 |
| **2. 第二階段主幹 (Trunk)**<br>*(格式選擇＋全域預設)* | `shared/router.md`<br>+ `shared/style_and_color_core.md`<br>+ `shared/blueprint_template.md` | 拍板 Format A～E 產出範圍（落實「無統計圖不選 D、僅需內嵌簡圖不選 A/D」自給自足邊界）與全域預設三支柱，建立樹狀單檔藍圖 `02_phase2_generation_blueprint.md` 之 `## 0. 主幹全域錨點`。 | 預設分步停下來確認，不擅自代選；`01` 與 `02` 紀錄檔互不跨鏈附掛。 |
| **3. 分枝規劃 (Branch Plan)**<br>*(各格式內容細節決定)* | 僅開選定格式之<br>`formats/format_*/01_plan.md` | 依選定分枝規劃拓撲、文體與 PDF 字體（B）、DISCAS 視距與模式 3 Tier/DNA（C）、30+ 圖表選型（D）、儀表板模式（E）及分枝局部覆寫，拍板後寫入藍圖對應之 `## Format X 分枝藍圖`。 | **未選中之格式分枝 100% 零讀取**；Format C 此階段嚴禁提前鎖死版型代號。 |
| **4. 隔離建構與驗收**<br>*(Build & QA — Subagent 優先)* | 僅開當前格式之<br>`02_build*.md` + `03_qa.md`<br>+ `shared/visual_cognition_core.md`<br>+ 單一筆風檔（＋按需模式 2/3） | **優先採分格式 Subagent 隔離**（僅傳 `00`、`01`、`02_color_registry.json`、選 C 傳 `02c_slide_spec_lock.json`、含 D 傳上游圖檔清單、藍圖 `## 0`＋該格式分枝與該格式資料夾；E 併傳 D 共通 SSOT 與選定 `families/`）或 **單執行緒 `D➔A➔B➔C➔E` 接力備援**；黑盒呼叫 `scripts/` 引擎生成並執行對應 `03_qa.md` 與 `read_file` 實地檢查（Format C 採 `02c_slide_spec_lock.json` ➔ `Step 4A` ➔ 方案 C 三階品管）。 | **日常執行嚴禁讀取 `scripts/*.py` 原始碼**；驗收後立即 `--cleanup` 清除暫存檔；格式 D/E 配色或編碼規則變動須同步更新對應 SSOT。 |
| **5. 結案進化閉環**<br>*(Step E1～E3 & Sync)* | `git_sync_and_evolution_protocol.md`<br>+ `THEORY_ARCHIVE.md` | 查證實證文獻（T01~T26）、一鍵透過 `report_skill_feedback.py` 回報 GitHub Issues、將模式 3 勝出創意沉澱入 `shared/creative_armory/cases/`（單行寫入 `INDEX.md`）、清理已結案靈感。 | **日常閱讀與製圖階段不開啟**，僅於 Git 同步、開站或 Step E1~E3 結案進化時按需載入。 |
