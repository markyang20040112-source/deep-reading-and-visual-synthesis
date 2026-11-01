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
│   │   └── phase1_socratic_reading_guide.md                  # [階段一] 五步蘇格拉底式閱讀引導、Kintsch 認知診斷與跨領域類比編碼協定
│   ├── phase2_output/
│   │   ├── phase2_output_router.md                           # [階段二總路由] 輸出分流總控台與「動態三維視覺決策引擎」
│   │   ├── visual_cognition_principles.md                    # [共通底層規範] 4→2→3 階層分塊、由淺入深敘事、放大字級階梯與 HCL 色彩學
│   │   ├── visual_diagram_matplotlib_spec.md                 # [特化格式 A：知識圖譜] 五大拓撲、4 主幹分叉、雙行飽滿配適與列槽真垂直置中
│   │   ├── document_report_spec.md                           # [特化格式 B：深度報告] 四大體裁、無上限自然分頁、189mm 擴張版心、注意力波峰波谷與防孤字/防掉框線
│   │   ├── presentation_slide_spec.md                        # [特化格式 C：高階簡報] 三區架構、四大黃金原型動態路由、首尾定錨與「功能聚合 vs. 空間舒展」動態分頁
│   │   └── quantitative_chart_spec.md                        # [特化格式 D：量化圖表] 差距型橫向柱線複合圖/啞鈴圖、Brewer 同質單色相漸層、雙圖視覺漏斗連通與對齊座標軸
│   └── scripts/
│       ├── hcl_color_engine.py                               # [色彩引擎] CIELUV 極座標 HCL 感知均勻色彩空間、三階面積衍生與 WCAG 自動墨水決策
│       └── generate_mindmap.py                               # [圖譜引擎] 出版級繁體中文知識圖譜 Matplotlib 向量渲染與全形縮排避頭尾引擎
└── reading_sessions/                                         # 【閱讀專案與生成資產自動歸檔區】
    └── <YYYYMMDD_主題簡稱>/
        ├── 00_source_article.md                              # [輸入層] 原始文章全文無損存檔
        ├── 01_phase1_socratic_log.md                         # [思辨層] 第一階段蘇格拉底思辨軌跡、使用者直覺與收斂架構紀錄
        └── 02_outputs/                                       # [產出層] 僅存放最終正式成果 (.png / .pdf / .md / .pptx) 與對應生成腳本 (.py)
```

---

## 📋 核心檔案職責邊界與按需載入順序 (Strict Role Boundaries & Loading Order)

為避免 AI 注意力分散與 Token 浪費，本技能嚴格執行**「單一事實來源（SSOT）」**與**「按階段按需載入」**：

| 執行階段 | 讀取檔案順序 | 檔案唯一職責（管什麼） | 嚴格邊界（不管什麼／禁止事項） |
| :--- | :--- | :--- | :--- |
| **0. 啟動入口** | `SKILL.md` | 判定進入階段一或階段二、管理 `reading_sessions/` 歸檔、定義 `_pending_skill_inspirations.md` 靈感生命週期。 | 不存放具體提問話術或視覺排版參數。 |
| **1. 第一階段**<br>*(深度閱讀思辨)* | `phase1_socratic_reading_guide.md` | 執行 Step 0～Step 5 蘇格拉底式提問、Kintsch 三層診斷、類比編碼，並即時更新 `01_phase1_socratic_log.md`。 | **嚴禁提前讀取 `phase2_output/` 任何檔案**；嚴禁未經思辨直接給出罐頭摘要。 |
| **2. 第二階段 Step 1**<br>*(共通視覺基準)* | `phase2_output_router.md`<br>$\rightarrow$ `visual_cognition_principles.md` | 啟動三維視覺決策引擎，載入四格式共通定律（$4 \to 2 \to 3$ 階層分塊、白話先行由淺入深、跨格式放大字級階梯、HCL 色彩配額）。 | 不載入使用者未要求的特化格式規範。 |
| **3. 第二階段 Step 2**<br>*(特化格式渲染)* | 依需求擇一或組合讀取：<br>• 格式 A：`visual_diagram_matplotlib_spec.md`<br>• 格式 B：`document_report_spec.md`<br>• 格式 C：`presentation_slide_spec.md`<br>• 格式 D：`quantitative_chart_spec.md` | 執行各格式專屬之幾何構圖、版面配置、CSS/Matplotlib/PPTX 工程防護規則，呼叫 `scripts/` 渲染並透過 `read_file` 視覺驗收。 | `02_outputs/` 嚴禁殘留臨時測試檔（如 `.html`、`test_*.png`、重複之 `.jpg`）。 |
| **4. 技能演進 Step 4**<br>*(文獻查證與固化)* | `THEORY_ARCHIVE.md` | 僅於成果驗收完畢後（或使用者詢問學術依據時）開啟，將實證文獻與新規則固化至技能庫並刪除靈感暫存檔。 | **日常執行階段一與階段二時嚴禁主動讀取**，以節省注意力預算。 |
