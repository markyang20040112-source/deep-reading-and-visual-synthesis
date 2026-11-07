# Deep Reading & Visual Synthesis (深度閱讀引導與視覺化知識統整技能庫)

本倉庫包含 **「深度閱讀引導與視覺化知識統整（Deep Reading & Visual Synthesis）」** Agent 技能之完整模組化規範、科學渲染引擎，以及每次深度閱讀專案所生成的知識資產。

---

## 🗺️ 倉庫全景檔案地圖與單一職責分工 (Project File Map & Single Responsibility)

```text
deep-reading-and-visual-synthesis/
├── README.md                                                 # [總覽] 倉庫全景地圖、檔案分工矩陣與運作流程說明
├── .agents/skills/deep-reading-and-visual-synthesis/         # 【核心技能定義區 — 採按需載入 (Lazy Routing) 省流量架構】
│   ├── SKILL.md                                              # [總控台] 雙階段隔離鐵律、檔案路由地圖、歸檔規範與靈感生命週期唯一權威定義
│   ├── THEORY_ARCHIVE.md                                     # [文獻庫] 認知心理學、視覺感知與排版工學實證文獻封存庫 (日常執行嚴禁讀取)
│   ├── phase1_reading/
│   │   └── phase1_socratic_reading_guide.md                  # [階段一] 四大輸入模式路由、五步蘇格拉底式引導、CSV+資料說明書「讀取—分析—討論」漏斗敘事三迴路與收斂協定
│   ├── phase2_output/
│   │   ├── phase2_output_router.md                           # [階段二總路由] 輸出分流總控台、「動態三軸視覺決策引擎」、「A2 無損分流擴展」與「Medium 專欄輕量路由」
│   │   ├── visual_cognition_principles.md                    # [共通底層規範] 單畫布 4→2→3 vs 跨畫布擴展、由淺入深敘事、同步字級階梯總表與 HCL 色彩學
│   │   ├── visual_diagram_matplotlib_spec.md                 # [特化格式 A：知識圖譜] 28"×18.5" 畫布、01/02/03+ 拆圖擴展、五大拓撲與 generate_mindmap.py API 契約
│   │   ├── document_report_spec.md                           # [特化格式 B：深度報告與專欄] 五大體裁 (B1~B4 深度報告 + 文體5 Medium <=1,000字專欄) 與 pdf_report_engine.py API 契約
│   │   ├── presentation_slide_spec.md                        # [特化格式 C：高階簡報] 三區架構、八大版型、2欄/3-4欄分級字級底線與 pptx_slide_engine.py API 契約
│   │   ├── quantitative_chart_spec.md                        # [特化格式 D：量化圖表] 鎖定版 Gephi·pastel 配色 SSOT、三層分流 assert、單面板跨檔接力與 hcl_color_engine.py API 契約
│   │   └── data_dashboard_spec.md                            # [特化格式 E：數據儀表板] 動態圖表選型、自包含本地 CSS、gephi_palette.js API 契約與獨立 Git 網站發布規範
│   └── scripts/                                              # 【底層黑盒渲染與驗證引擎 — 日常執行直接 import 呼叫，免讀原始碼】
│       ├── hcl_color_engine.py                               # [Python 色彩引擎] CIELUV HCL 色彩空間、Gephi·pastel 色階、零透明度標籤底色與 CIELAB 插值
│       ├── gephi_palette.js                                  # [前端 JS 色彩引擎] 純 JS CIELAB 插值、類別色碼鎖定與 0-Alpha 標籤底色引擎 (UMD/Browser/Node)
│       ├── generate_mindmap.py                               # [Format A 圖譜引擎] 出版級繁體中文知識圖譜渲染、避頭尾保護與 T1~T5 高階拓撲組件
│       ├── pdf_report_engine.py                              # [Format B 報告引擎] A4 直向/橫向混合排版 CSS 生成器與 Playwright PDF 編譯引擎
│       ├── pptx_slide_engine.py                              # [Format C 簡報引擎] 16:9 原生向量投影片組件、欄數自適應字級與版型防撞驗證引擎
│       └── verify_visual_outputs.py                          # [視覺驗收與清理引擎] PDF/PPTX 自動轉 PNG 預覽檢驗與暫存中介檔一鍵清除工具
└── reading_sessions/                                         # 【閱讀專案與生成資產自動歸檔區】
    └── <YYYYMMDD_主題簡稱>/
        ├── data/<原檔名>.csv                                 # [原始數據層] 原始 CSV 檔案原封不動存檔（嚴守規範第 5 節絕對不改動原始檔）
        ├── 00_source_article.md                              # [輸入層] 原始文章全文或 Gemini 網頁版《資料說明書 (Data Codebook)》無損存檔
        ├── 01_phase1_socratic_log.md                         # [思辨層] 第一階段蘇格拉底思辨軌跡、CSV 三層分流驗算、候選切角選單與單一故事線/雙群組收斂紀錄
        └── 02_outputs/                                       # [產出層] 僅存放最終正式成果 (.png / .pdf / .md / .pptx / 正式 Git-Ready 儀表板網站專案) 與對應生成腳本 (.py)
```

---

## 📋 核心檔案職責邊界與按需載入順序 (Strict Role Boundaries & Loading Order)

為避免 AI 注意力分散與 Token 浪費，本技能嚴格執行**「單一事實來源（SSOT）」**、**「按階段按需載入」**與**「底層引擎黑盒呼叫鐵律」**：

| 執行階段 | 讀取檔案順序 | 檔案唯一職責（管什麼） | 嚴格邊界（不管什麼／禁止事項） |
| :--- | :--- | :--- | :--- |
| **0. 啟動入口** | `SKILL.md` | 判定進入階段一或階段二、管理 `reading_sessions/` 歸檔、定義黑盒引擎呼叫鐵律與 `_pending_skill_inspirations.md` 靈感生命週期。 | 不存放具體提問話術或視覺排版參數。 |
| **1. 第一階段**<br>*(深度閱讀思辨／數據探索)* | `phase1_socratic_reading_guide.md` | 依四大輸入模式執行 Step 0～Step 5 蘇格拉底式提問或「CSV＋資料說明書」讀取—分析—討論三迴路，即時更新 `01_phase1_socratic_log.md`。 | **嚴禁提前讀取 `phase2_output/` 任何檔案**；嚴禁直接將大型 CSV 讀入 LLM 上下文消耗 Token。 |
| **2. 第二階段 Step 1**<br>*(共通視覺基準)* | `phase2_output_router.md`<br>$\rightarrow$ `visual_cognition_principles.md` | 啟動三軸視覺決策引擎、無損分流擴展（拆圖、擴章、加頁）或 Medium 專欄輕量路由，載入五格式共通定律與同步字級階梯總表。 | 不載入使用者未要求的特化格式規範。 |
| **3. 第二階段 Step 2**<br>*(特化格式渲染)* | 依需求擇一或組合讀取：<br>• 格式 A：`visual_diagram_matplotlib_spec.md`<br>• 格式 B：`document_report_spec.md`<br>• 格式 C：`presentation_slide_spec.md`<br>• 格式 D：`quantitative_chart_spec.md`<br>• 格式 E：`data_dashboard_spec.md`（🔗與格式 D 連動） | 依各規格檔內建之黑盒 API 契約直接 `import` `scripts/` 引擎渲染成品，透過 `view_file` 逐頁視覺驗收並清除暫存檔；Medium 模式免編譯 PDF 並自動推送 GitHub 輸出繳交區塊；格式 E 完成後可綁定獨立 Git 儲存庫發布網站。 | **正常執行時嚴禁 `read_file` 讀取 `scripts/*.py` 原始碼**；`02_outputs/` 嚴禁殘留臨時預覽檔（`_preview_*.png`、暫存 `.html`）。格式 D 與格式 E 之共通配色規則若有改動須同步更新。 |
| **4. 技能演進 Step 4**<br>*(文獻查證與固化)* | `THEORY_ARCHIVE.md` | 僅於成果驗收完畢後（或使用者詢問學術依據時）開啟，將實證文獻與新規則固化至技能庫並刪除靈感暫存檔。 | **日常執行階段一與階段二時嚴禁主動讀取**，以節省注意力預算。 |

