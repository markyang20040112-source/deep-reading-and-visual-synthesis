# Deep Reading & Visual Synthesis (深度閱讀引導與視覺化知識統整技能庫)

本倉庫包含 **「深度閱讀引導與視覺化知識統整（Deep Reading & Visual Synthesis）」** Agent 技能完整規範與每次深度閱讀專案所生成的知識資產。

---

## 📁 倉庫目錄結構

```text
deep-reading-and-visual-synthesis/
├── README.md                                                 # 倉庫總覽說明
├── .agents/skills/deep-reading-and-visual-synthesis/         # 【核心技能定義區】
│   ├── SKILL.md                                              # 極簡總路由指南、歸檔規範與靈感生命週期
│   ├── THEORY_ARCHIVE.md                                     # 29 篇認知心理學與設計科學實證文獻封存庫
│   ├── phase1_reading/
│   │   └── phase1_socratic_reading_guide.md                  # 第一階段：五步漸進式認知推進與蘇格拉底思辨協定
│   ├── phase2_output/
│   │   ├── phase2_output_router.md                           # 第二階段：模組化輸出分流總控台
│   │   ├── visual_cognition_principles.md                    # 共通核心：Cowan 4±1、瑞士網格、W3C CLREQ 與 4 大科學色板
│   │   ├── visual_diagram_matplotlib_spec.md                 # 特化格式 A：五大動態拓撲版型（T1~T5）與 Novak 關係膠囊
│   │   ├── document_report_spec.md                           # 特化格式 B：四大報告體裁篇幅配額與 Ehrenberg 科學表格
│   │   └── presentation_slide_spec.md                        # 特化格式 C：Alley 斷言—證據三區架構與 80/20 聚光燈規範
│   └── scripts/
│       └── generate_mindmap.py                               # 科學化知識圖譜 Python Matplotlib 向量渲染引擎
└── reading_sessions/                                         # 【閱讀專案與生成資產自動歸檔區】
    └── <YYYYMMDD_主題簡稱>/
        ├── 00_source_article.md                              # 原始文章全文存檔
        ├── 01_phase1_socratic_log.md                         # 第一階段蘇格拉底思辨紀錄檔
        └── 02_outputs/                                       # 第二階段生成之圖譜 (.jpg/.png)、腳本 (.py)、報告與簡報
```
