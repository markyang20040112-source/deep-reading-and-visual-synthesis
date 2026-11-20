# 第二層結構顧問（Format B）：深度報告體裁與 Medium 專欄選型大腦

> **單一職責定位（Single Responsibility）**：本檔為 Phase 2 **第二層（Layer 2）分類顧問檔**，**僅當第一層確定包含 Format B（文字報告或數據新聞專欄）時按需開啟**。專責診斷並協助使用者在「五大文體（文體 1～4 A4 PDF 深度報告 vs. 文體 5 Medium 專欄）」與章節結構骨架之間做出最佳選型，拍板後交由第三層定裝。

---

## 一、 第一步：五大報告與專欄體裁選型顧問表（5 Document Genres Diagnostic Matrix）

依據素材來源、目標讀者與發布媒介，查表診斷出**首選推薦文體 ＋ 推薦理由 ＋ 備選方案**：

| 文體類型 | 觸發情境與最佳適用素材（何時首選） | 核心結構與篇幅權重配比（`%`） | 產出形式與終端規格檔（Layer 3 後才開啟） |
| :--- | :--- | :--- | :--- |
| **文體 1：深度綜合評論**<br>*(Comprehensive Synthesis)* | 跨領域長文、多學科理論交鋒、歷史脈絡重構與批判反思 | ① 核心命題與金字塔結論 (`15%`) $\rightarrow$ ② 原文論證脈絡與實證拆解 (`35%`) $\rightarrow$ ③ 跨領域視角與結構映射 (`25%`) $\rightarrow$ ④ 反思盲點與延伸應用 (`25%`) | `.md` + A4 印刷級 `.pdf`<br>$\rightarrow$ [`../document_report_spec.md`](../document_report_spec.md) |
| **文體 2：高階決策備忘錄**<br>*(Executive Strategy Memo)* | 商業調查報告、產業研究、策略轉型或具量化實證的政策分析 | ① 執行摘要與 SCQA 破題 (`15%`) $\rightarrow$ ② 核心矛盾與實證數據診斷 (`25%`) $\rightarrow$ ③ 系統架構與失效機制解剖 (`30%`) $\rightarrow$ ④ 雙軌治理與分階段行動路線圖 (`30%`) | `.md` + A4 印刷級 `.pdf`<br>$\rightarrow$ [`../document_report_spec.md`](../document_report_spec.md) |
| **文體 3：方法論實踐藍圖**<br>*(Methodological Blueprint)* | 工程架構、演算法、資料治理管線、SOP 或技術操作指南 | ① 核心設計哲學與邊界 (`15%`) $\rightarrow$ ② 系統架構與運作機制 (`35%`) $\rightarrow$ ③ 落地步驟與檢核矩陣 (`30%`) $\rightarrow$ ④ 常見反模式與防禦對策 (`20%`) | `.md` + A4 印刷級 `.pdf`<br>$\rightarrow$ [`../document_report_spec.md`](../document_report_spec.md) |
| **文體 4：跨域知識卡片組**<br>*(Atomic Knowledge Cards)* | 概念密度極高之教材或經典，需拆解為可複用的個人知識原子卡片 | ① 全局概念索引地圖 (`15%`) $\rightarrow$ ② 原子概念卡（白話定義、運作機制、正反案例、跨域連結）(`65%`) $\rightarrow$ ③ 實踐自測清單 (`20%`) | `.md` + A4 印刷級 `.pdf`<br>$\rightarrow$ [`../document_report_spec.md`](../document_report_spec.md) |
| **文體 5：Medium 每週一圖數據敘事專欄**<br>*(Medium Data Storytelling Column)* | **CSV 原始檔＋《資料說明書》**、公開數據新聞、或課堂「每週一圖」作業（追求手機與網頁流暢快讀） | ① 新聞感標題與黃金數字 Hook (`15%`) $\rightarrow$ ② 圖 1 嵌入與結構拆解短段落 (`35%`) $\rightarrow$ ③ 數據金句引言塊與圖 2 深挖 (`35%`) $\rightarrow$ ④ 第 6 章解讀邊界反思 (`15%`) ＋ `---` 分離計字官方來源 | **僅產出 Medium 原生 `.md`**（正文 `<= 1,600` 字、**禁用 HTML/表格、免 PDF**）<br>$\rightarrow$ [`../medium_column_spec.md`](../medium_column_spec.md) |

---

## 二、 第二步：結構骨架與圖文配置規劃（Structure & Figure Integration）

1. **若推薦為文體 1～4（深度報告）**：
   - 依 Phase 1 收斂分支總數動態規劃一級章節（`壹、貳、參、肆、伍、陸、柒...`），確保每個核心論證與批判延伸分支擁有獨立章節，絕不強制壓縮總頁數。
   - 確認每個大章節採「敘事散文（波谷）$\rightarrow$ 三線表／卡片矩陣／公式盒（波峰）$\rightarrow$ 洞見收斂」交錯節律；同時掃描各章節抽象度，預先標註哪 1～2 個核心機制章節適合呼叫 `setup_a4_portrait_canvas()` 安插 **A4 直向原生輕量流程簡圖（`7.44"` / `189mm` 寬）**。**嚴禁將高密度 Format A 知識圖譜或 Format E 靜態全景圖塞入 PDF 報告（亦禁用 A4 橫向跨頁）**，全景大圖一律維持獨立檔案交付。
   - 確認 PDF 報告與 PPTX 簡報維持**預設獨立**（除非使用者特別要求於報告中列出簡報頁次配當）。
2. **若推薦為文體 5（Medium 專欄）**：
   - 鎖定 **單一故事線（Single Hook）** 與七步敘事大綱，明確分配 **圖 1（`01_chart_hook.png`）** 與選配之 **圖 2（`02_chart_drilldown.png`）** 在文章中的敘事分工（兩者須互補為 $1+1>2$，且為各自獨立單面板圖片）。

---

## 三、 第三步：第二層提案格式與進入第三層交接

向使用者提出 **Format B 第二層體裁與章節大綱提案**（列明：**首選文體＋推薦理由＋備選文體＋擬定章節大綱與配圖位置**）：
- 註：是否開啟經濟學人式「巨型數字衝擊盒／迷思與真相對撞台／方法論紅黃綠燈警示卡」、筆風設定檔（`Slot 1, 3, 4`）與 PDF 字體（現代黑體 `modern_sans` vs. 標楷體首行縮排 `clreq_kaiti`），將於**第三層**統一確認定裝。

**⏸️ 暫停關卡**：等待使用者確認 Format B（及同期選定的其他格式）第二層結構方案後，立即將文體、章節重點與討論取捨理由寫入 `02_phase2_generation_blueprint.md` 第 2 節，隨即讀取 **[`layer3_advisor_design_style_color.md`](layer3_advisor_design_style_color.md)** 進入第三層定裝。
