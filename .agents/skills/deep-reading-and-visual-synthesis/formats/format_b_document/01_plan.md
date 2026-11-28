# Format B 內容細節規劃（深度報告體裁、PDF 字體與 Medium 專欄選型大腦）

> **單一職責定位（Single Responsibility）**：本檔為 **Format B（深度分析報告 `.md`/`.pdf` 或 Medium 數據專欄 `.md`）** 分枝的內容細節決策大腦，**僅當主幹 [`../../shared/router.md`](../../shared/router.md) 確定勾選 Format B 時按需開啟**。專責診斷「五大文體（文體 1～4 A4 PDF 深度報告 vs. 文體 5 Medium 專欄）」、章節與配圖分工、**Format B 專屬 PDF 字體（`modern_sans` vs. `clreq_kaiti`）** 以及本分枝局部覆寫，拍板後寫入 `02_phase2_generation_blueprint.md` 之 **`## Format B 分枝藍圖`**，再互斥單開 [`02_build_pdf.md`](./02_build_pdf.md) 或 [`02_build_medium.md`](./02_build_medium.md) 搭配 [`03_qa.md`](./03_qa.md) 執行。

---

## 一、 第一步：五大報告與專欄體裁選型顧問表（5 Document Genres Diagnostic Matrix）

依據素材來源、目標讀者與發布媒介，查表診斷出**首選推薦文體 ＋ 推薦理由 ＋ 備選方案**：

| 文體類型 | 觸發情境與最佳適用素材（何時首選） | 核心結構與篇幅權重配比（`%`） | 產出形式與互斥終端規格檔 |
| :--- | :--- | :--- | :--- |
| **文體 1：深度綜合評論**<br>*(Comprehensive Synthesis)* | 跨領域長文、多學科理論交鋒、歷史脈絡重構與批判反思 | ① 核心命題與金字塔結論 (`15%`) $\rightarrow$ ② 原文論證脈絡與實證拆解 (`35%`) $\rightarrow$ ③ 跨領域視角與結構映射 (`25%`) $\rightarrow$ ④ 反思盲點與延伸應用 (`25%`) | `.md` + A4 印刷級 `.pdf`<br>$\rightarrow$ [`02_build_pdf.md`](./02_build_pdf.md) |
| **文體 2：高階決策備忘錄**<br>*(Executive Strategy Memo)* | 商業調查報告、產業研究、策略轉型或具量化實證的政策分析 | ① 執行摘要與 SCQA 破題 (`15%`) $\rightarrow$ ② 核心矛盾與實證數據診斷 (`25%`) $\rightarrow$ ③ 系統架構與失效機制解剖 (`30%`) $\rightarrow$ ④ 雙軌治理與分階段行動路線圖 (`30%`) | `.md` + A4 印刷級 `.pdf`<br>$\rightarrow$ [`02_build_pdf.md`](./02_build_pdf.md) |
| **文體 3：方法論實踐藍圖**<br>*(Methodological Blueprint)* | 工程架構、演算法、資料治理管線、SOP 或技術操作指南 | ① 核心設計哲學與邊界 (`15%`) $\rightarrow$ ② 系統架構與運作機制 (`35%`) $\rightarrow$ ③ 落地步驟與檢核矩陣 (`30%`) $\rightarrow$ ④ 常見反模式與防禦對策 (`20%`) | `.md` + A4 印刷級 `.pdf`<br>$\rightarrow$ [`02_build_pdf.md`](./02_build_pdf.md) |
| **文體 4：跨域知識卡片組**<br>*(Atomic Knowledge Cards)* | 概念密度極高之教材或經典，需拆解為可複用的個人知識原子卡片 | ① 全局概念索引地圖 (`15%`) $\rightarrow$ ② 原子概念卡（白話定義、運作機制、正反案例、跨域連結）(`65%`) $\rightarrow$ ③ 實踐自測清單 (`20%`) | `.md` + A4 印刷級 `.pdf`<br>$\rightarrow$ [`02_build_pdf.md`](./02_build_pdf.md) |
| **文體 5：Medium 每週一圖數據敘事專欄**<br>*(Medium Data Storytelling Column)* | **CSV 原始檔＋《資料說明書》**、公開數據新聞、或課堂「每週一圖」作業（追求手機與網頁流暢快讀） | ① 新聞感標題與黃金數字 Hook (`15%`) $\rightarrow$ ② 圖 1 嵌入與結構拆解短段落 (`35%`) $\rightarrow$ ③ 數據金句引言塊與圖 2 深挖 (`35%`) $\rightarrow$ ④ 第 6 章解讀邊界反思 (`15%`) ＋ `---` 分離計字官方來源 | **僅產出 Medium 原生 `.md`**（正文 `<= 1,600` 字、**禁用 HTML/表格、免 PDF**）<br>$\rightarrow$ [`02_build_medium.md`](./02_build_medium.md) |

---

## 二、 第二步：結構骨架、圖文配置與 Format B 專屬字體設定

1. **若推薦為文體 1～4（A4 PDF 深度報告）**：
   - **動態擴章無損承載**：依 Phase 1 收斂分支總數動態規劃一級章節（`壹、貳、參、肆、伍、陸、柒...`），確保每個核心論證與批判延伸分支擁有獨立章節，絕不強制壓縮總頁數。
   - **自給自足 A4 直向簡圖切點（免勾選 Format A）**：確認每個大章節採「敘事散文（波谷）$\rightarrow$ 三線表／卡片矩陣／公式盒（波峰）$\rightarrow$ 洞見收斂」交錯節律；同時掃描各章節抽象度，預先標註哪 1～2 個核心機制章節直接呼叫 `generate_mindmap.py` 之 **`setup_a4_portrait_canvas()`** 安插 **A4 直向原生輕量流程簡圖（`7.44"` / `189mm` 寬，`300 DPI`）**。**嚴禁將高密度 Format A 知識圖譜或 Format E 靜態全景圖塞入 PDF 報告（亦禁用 A4 橫向跨頁）**，全景大圖一律維持獨立檔案交付。
   - **Format B 專屬 PDF 字體確認（Format B 專屬設定）**：
     - **`modern_sans`（預設）**：現代無襯線正黑體（`Microsoft JhengHei` / `PingFang TC` / `Noto Sans CJK TC`），適用商業策略備忘錄、技術藍圖與現代評論。
     - **`clreq_kaiti`**：台灣大專院校正式中文課程報告／傳統公文書模式（W3C CLReq `DFKai-SB` 標楷體 ＋ 正文散文段落首行空兩格 `text-indent: 2em`；表格、卡片、收斂框與圖說維持不縮排）。
   - **與 Format C 預設獨立**：確認 PDF 報告與 PPTX 簡報維持**預設獨立**（除非使用者特別要求於報告中列出簡報頁次配當）。
2. **若推薦為文體 5（Medium 專欄）**：
   - 鎖定 **單一故事線（Single Hook）** 與七步敘事大綱，明確分配 **圖 1（`01_chart_hook.png`）** 與選配之 **圖 2（`02_chart_drilldown.png`）** 在文章中的敘事分工（兩者須互補為 $1+1>2$，且為各自獨立單面板圖片；免編譯 PDF，免選 PDF 字體）。

---

## 三、 第三步：本分枝混合式局部覆寫與提案確認

向使用者提出 **Format B 分枝體裁與章節大綱提案**，同時確認是否覆寫主幹預設（見 [`../../shared/style_and_color_core.md`](../../shared/style_and_color_core.md)）：
- **設計模式覆寫（可選）**：承襲主幹，或針對文體 1～4 PDF 開啟 **模式 2 編輯室社論組件**（`.editorial-masthead`、`.big-stat-callout`、`.myth-reality-split`、`.methodology-traffic-light`，見 [`../../shared/editorial_narrative_spec.md`](../../shared/editorial_narrative_spec.md)）或 **模式 3 主題裝幀**。
- **筆風與佈景主題覆寫（可選）**：承襲主幹，或單獨為 Format B 指定筆風檔（`Slot 1, 3, 4, 8`）與 `document_theme`。
- **PDF 字體（僅文體 1～4）**：確認 `modern_sans` 或 `clreq_kaiti`。

**⏸️ 暫停關卡**：等待使用者確認 Format B 體裁、大綱、配圖位置、PDF 字體（若文體 1～4）與分枝覆寫後，立即寫入 `02_phase2_generation_blueprint.md` 之 **`## Format B 分枝藍圖`**；輪到 Format B 執行時，依體裁互斥載入 [`02_build_pdf.md`](./02_build_pdf.md) 或 [`02_build_medium.md`](./02_build_medium.md) 並執行 [`03_qa.md`](./03_qa.md) 驗收。
