# Deep Reading & Visual Synthesis (深度閱讀引導與視覺化知識統整技能庫)

本倉庫包含 **「深度閱讀引導與視覺化知識統整（Deep Reading & Visual Synthesis）」** Agent 技能之完整模組化規範、科學渲染引擎，以及公私雙倉庫隔離範本架構。

---

## 🏗️ 全系統架構全景圖（System Architecture Overview）

![Deep Reading & Visual Synthesis 全系統架構全景圖](assets/skill_architecture_overview.png)

---

## 🗺️ 倉庫全景檔案地圖與單一職責分工 (Project File Map & Single Responsibility)

本技能庫採 **「三層漸進決策漏斗（O(1) 按需載入）＋ 表達三支柱全域穿透 ＋ 底層黑盒引擎」** 設計，確保 AI 在極低注意力負荷下維持高穩定度的知識萃取與出版級視覺渲染：

```text
deep-reading-and-visual-synthesis/
├── README.md                                                 # [人類導覽] 倉庫全景架構圖、檔案分工矩陣與運作流程說明
├── assets/
│   └── skill_architecture_overview.png                       # [架構圖] 全系統架構全景圖（給人類閱覽之 PNG 導覽）
└── .agents/skills/deep-reading-and-visual-synthesis/         # 【核心技能定義區 — 採 O(1) 按需載入 (Lazy Routing)】
    ├── SKILL.md                                              # [總控台] Gate 0 身分驗證門神、五大運作鐵律、檔案路由地圖與歸檔規範
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
    ├── phase2_output/                                        # [階段二：三層漸進決策漏斗 ＋ 最小葉節點規格庫]
    │   ├── phase2_output_router.md                           # [Layer 1 總路由] 決定 Format A~E 範圍、02_phase2_generation_blueprint.md 與 D➔A➔B➔C➔E 逐格式接力確認規則
    │   ├── advisors/                                         # [Layer 2 & Layer 3 顧問大腦 — 未選格式零讀取]
    │   │   ├── layer2_advisor_a_diagram.md                   # Format A 顧問：無損分圖 (01/02/03+) 與 T1~T5 拓撲推薦
    │   │   ├── layer2_advisor_b_report.md                    # Format B 顧問：文體 1~4 (A4 PDF ＋ 直向簡圖切點) vs. 文體 5 (Medium 專欄)
    │   │   ├── layer2_advisor_c_slide.md                     # Format C 顧問：DISCAS 視距反推字級地板、單一議題章節與 Step 3/4A 文案保真關卡
    │   │   ├── layer2_advisor_de_chart.md                    # Format D/E 顧問：4D 資料快篩 × 8 溝通意圖 × 30+ 圖表決策樹、T25 選型與 Format D➔C `*_slide.png` 銜接
    │   │   └── layer3_advisor_design_style_color.md          # [Layer 3 定裝] 解耦式設計光譜 (模式 1 / 模式 2 編輯室 / 模式 3 Tier 1~3 主動推薦＋DNA) × 筆風 × 分層色票全域定裝
    │   ├── visual_cognition_principles.md                    # [共通底盤] 無損擴展哲學、表達三支柱、事實與因果保真底線、避頭尾保護與 75-20-5 雙層色票
    │   ├── editorial_narrative_spec.md                       # [模式 2 專檔] 資料八編輯室 5 大技法、Format B 社論組件與 A/C/E 敘事延伸（與模式 3 徹底解耦）
    │   ├── creative_armory/                                  # [模式 3 開放式創意隱喻武器庫 — O(1) 單行索引＋按需原子案例卡]
    │   │   ├── INDEX.md                                      # 模式 3 唯一輕量入口：開放式 Form-as-Metaphor 四大底線 ＋ 單行案例索引表
    │   │   └── cases/                                        # 依視覺編碼分類之原子案例卡（按需單開，成功案例可持續回饋入庫）
    │   │       ├── 01_texture_and_container/                 # 材質、容器與精靈圖標：glass_liquid_bars.md、masked_texture_wedges.md、sprite_coord_scatter.md
    │   │       ├── 02_structural_geometry/                   # 純向量幾何結構隱喻開放成長目錄（Form-as-Metaphor 預留庫）
    │   │       └── 03_spatial_and_thematic/                  # 空間與主題裝幀：thematic_palette_frame.md、diagram_spatial_metaphors.md
    │   ├── quantitative_chart_spec.md                        # [Format D⇄E SSOT] 編碼誠實三鐵律、圖表 8 元件檢核、配色 SSOT、零斷裂箭頭與三層 CSV 分流
    │   ├── chart_family1_ranking_and_deviation.md            # [家族 1] 克里夫蘭點陣圖、棒棒糖、啞鈴＆雙向動量向量箭頭 (directed=True)、斜坡、子彈、垂直對稱蝴蝶金字塔、柏拉圖
    │   ├── chart_family2_trend_and_comparison.md             # [家族 2] 共用基線剪刀差折線＋面積帶、空間重力斷崖複合、時期色帶折線、配對雙柱剪刀差、面積、範圍甘特
    │   ├── chart_family3_composition_and_flow.md             # [家族 3] 4+1 堆疊、中心 KPI 環形、馬賽克雙維圖、瀑布、樹圖、旭日、桑基/弦圖
    │   ├── distribution_and_density_chart_spec.md            # [家族 4] 10 大分配與密度圖形 ＋ 背景基準分面 (Context Overlay) 8 鐵律
    │   ├── chart_family5_multivariate_and_spatial.md         # [家族 5] 全樣本波士頓四象限氣泡矩陣（類別深色實心箭頭指引線）、突出顯示熱力表、雷達圖、主圖＋角落排行副卡
    │   ├── visual_diagram_matplotlib_spec.md                 # [Format A] 23.8"×15.4" 知識圖譜 (T1~T5) ＋ Format B 7.44" 直向簡圖 API
    │   ├── document_report_spec.md                           # [Format B1~4] A4 自適應分頁印刷 PDF 報告與現代黑體 / 標楷體雙字體主題
    │   ├── medium_column_spec.md                             # [Format B5] <=1,600 字純淨原生 Markdown 專欄（免編譯 PDF）
    │   ├── presentation_slide_spec.md                        # [Format C] 16:9 視距自適應簡報（DISCAS 地板、五大家族 13 精煉版型 F1-A~F5-C、去方塊 <=40%、Step 4A 規格鎖與方案 C 三階品管）
    │   └── data_dashboard_spec.md                            # [Format E] 零後端互動式數據儀表板、標準 CSS 骨架與獨立 Git 網站發布規範
    ├── scripts/                                              # 【底層黑盒擷取、渲染、色彩、圖表、驗收與進化引擎 — 免讀原始碼直接呼叫】
    │   ├── ingest_source_material.py                         # Stage 0 四合一素材黑盒擷取引擎（網頁 URL / YouTube 字幕 / PDF / DOCX → 00_source_article.md）
    │   ├── hcl_color_engine.py                               # 統一相容入口門面（轉接 color_core / color_registry / owner_sync / chart_* 各模組）
    │   ├── color_core.py                                     # CIELAB/HCL 色彩科學、全域色票契約、主題衍生與前端 JS 匯出核心
    │   ├── color_registry.py                                 # 跨圖工作階段類別色彩登記表（02_color_registry.json 持久化鎖色）
    │   ├── owner_sync.py                                     # 使用者身分識別與公私雙倉庫同步 CLI
    │   ├── chart_data.py                                     # 輕量 DataFrame、數值/NA 解析與三層 CSV 分流引擎
    │   ├── chart_common.py                                   # CJK 字型設定、despine_axes、聚光燈配色與 1D 防撞共用工具
    │   ├── chart_editorial.py                                # 資料八編輯室敘事組件（膠囊基準線、時期色帶、角落排行卡、四層底註）
    │   ├── chart_family1_ranking.py                          # 圖表家族 1 引擎（克里夫蘭點陣圖、啞鈴/雙向動量箭頭圖、斜坡圖、子彈圖）
    │   ├── chart_family3_composition.py                      # 圖表家族 3 引擎（Marimekko 雙維佔比圖、瀑布圖）
    │   ├── chart_family4_distribution.py                     # 圖表家族 4 引擎（裁切 KDE、背景基準分面與分布輔助函式）
    │   ├── chart_creative_armory.py                          # 模式 3 創意隱喻圖（液體容器柱、遮罩紋理扇形、圖示散佈）
    │   ├── gephi_palette.js                                  # 前端 JS 色彩 SSOT、CIELAB 插值、entityColors 查詢與 deriveThematicPalette (UMD/Browser/Node)
    │   ├── generate_mindmap.py                               # Format A 出版級繁體中文知識圖譜引擎（避頭尾保護與 T1~T5 拓撲組件）
    │   ├── pdf_report_engine.py                              # Format B A4 自適應分頁 CSS 生成器與 Playwright PDF 編譯引擎
    │   ├── pptx_slide_engine.py                              # Format C 16:9 五大家族 13 版型原生引擎（Pillow 繁中字寬、DISCAS Token、OMML 公式、Playwright 300 DPI 與規格驅動確定性渲染）
    │   ├── verify_visual_outputs.py                          # PDF/PPTX 轉圖（含 slide_indices 單頁重繪）、方案 C 接觸表/2×2 四宮格、碰撞/孤兒/保真體檢、色彩登記表與自動清理工具
    │   ├── report_skill_feedback.py                          # 技能優化靈感三通道自動化 GitHub Issues 回報工具
    │   └── check_skill_updates.py                            # 30 天節流之無損技能更新檢查工具
    └── tests/
        └── test_color_registry.py                            # 跨圖類別色彩登記表與繪圖模組回歸測試套件
```

---

## 📋 核心執行階段與嚴格邊界 (Execution Phases & Strict Boundaries)

| 執行階段 | 讀取檔案順序 | 核心職責（管什麼） | 嚴格邊界（不管什麼／禁止事項） |
| :--- | :--- | :--- | :--- |
| **0. Gate 0 啟動門神** | `SKILL.md` | 身分驗證與公私雙倉庫隔離（作者還原私人設定／新用戶導向 `onboarding_wizard.md`）、30 天更新節流與靈感暫存規則。 | 不存放具體提問話術或視覺排版參數；私人設定與 `reading_sessions/` 嚴格受 `.gitignore` 隔離。 |
| **1. 第一階段 (Phase 1)**<br>*(深度閱讀／數據探索)* | `phase1_socratic_reading_guide.md`<br>$\rightarrow$ `mode1_*` 或 `mode2_*` | 先執行 **Stage 0 垂直工序**（調用 `ingest_source_material.py` 自動將 URL / YouTube 字幕 / PDF / DOCX 轉為 `00_source_article.md`），再二擇一載入子協定執行 5 步蘇格拉底思辨或 CSV 三迴路分析，即時寫入 `01_phase1_socratic_log.md`。 | **嚴禁提前讀取 `phase2_output/` 任何檔案**；嚴禁將大型 CSV 直接讀入 LLM 上下文消耗 Token。 |
| **2. 第二階段 (Phase 2)**<br>*(三層漸進決策漏斗)* | **L1**: `phase2_output_router.md`<br>**L2**: `advisors/layer2_*.md`<br>**L3**: `advisors/layer3_*.md` | 逐層討論拍板：**L1** 決定 Format A~E 範圍 $\rightarrow$ **L2** 僅開選定格式顧問定骨架 $\rightarrow$ **L3** 統一或混搭定裝「設計武器庫 × 筆風 × 配色」，並依時機 A 逐層寫入 `02_phase2_generation_blueprint.md`（含取捨理由與客製細節）。 | 未選中之格式與顧問檔 **100% 零讀取**；預設分步停下來確認，不擅自代選；`01` 與 `02` 紀錄檔互不跨鏈附掛。 |
| **3. 終端執行與驗收**<br>*(Terminal Execution & QA)* | `visual_cognition_principles.md`<br>+ 選定之單一筆風檔<br>+ 按需之最小葉節點 `*_spec.md` | 依 `D➔A➔B➔C➔E` 逐格式接力生成與確認：僅載入拍板之最小葉節點規格檔，直接 `import` `scripts/` 底層黑盒引擎渲染（Format C 採 `02c_slide_spec_lock.json` ➔ `Step 4A` ➔ `render_deck_from_spec()`），並強制執行 `verify_visual_outputs.py`（含 Format C 方案 C 三階內部品管：`verify_pptx_structure`＋`4×4` 接觸表＋`2×2` 四宮格＋高風險頁滿版精檢與 `slide_indices` 單頁重繪）與 `read_file` 實地檢查。 | **日常執行嚴禁讀取 `scripts/*.py` 原始碼**；驗收後立即 `--cleanup` 清除所有暫存預覽與網格圖；格式 D/E 配色或編碼規則變動須同步更新對應 SSOT。 |
| **4. 結案進化閉環**<br>*(Step E1～E3 & Sync)* | `git_sync_and_evolution_protocol.md`<br>+ `THEORY_ARCHIVE.md` | 查證實證文獻（T01~T26）、一鍵透過 `report_skill_feedback.py` 回報 GitHub Issues、將模式 3 勝出創意沉澱入 `creative_armory/cases/`（單行寫入 `INDEX.md`）、清理已結案靈感。 | **日常閱讀與製圖階段不開啟**，僅於 Git 同步、開站或 Step E1~E3 結案進化時按需載入。 |
