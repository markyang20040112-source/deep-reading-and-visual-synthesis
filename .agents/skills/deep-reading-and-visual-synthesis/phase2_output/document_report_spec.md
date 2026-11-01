# 結構化深度報告與雙模態排版規範（Format B: Document Report Spec）

> **單一職責定位（Single Responsibility）**：本檔專責 **Format B（結構化深度分析報告 `.md` 與高解析印刷級 `.pdf`）** 的文體選擇、注意力節律排版、Playwright A4 印刷 CSS 規格與防斷框工程守則。跨格式共用的組塊階層、白話由淺入深原則與基礎色票請見 `visual_cognition_principles.md`。

---

## 一、 四大報告文體與結構配比（4 Document Genres & Structural Proportions）

- **理論依據**：**體裁分析理論（Genre Analysis, Swales 1990）** 與 **金字塔原理（Pyramid Principle, Minto 2009）**。
- **頁數無硬性上限原則**：報告總頁數由內容深度、圖表數量與視覺留白自然決定，**嚴禁設定固定頁數上限（如強行壓縮至 6 頁）或為了湊頁數而灌水**。以下百分比（`%`）代表**全篇篇幅與認知權重的相對配比**：

| 文體類型 | 適用場景 | 核心結構與篇幅權重配比（`%`） |
| :--- | :--- | :--- |
| **1. 深度綜合評論**<br>*(Comprehensive Synthesis)* | 跨領域長文、多視角理論交鋒 | ① 核心命題與金字塔結論 (`15%`) → ② 原文論證脈絡與實證拆解 (`35%`) → ③ 跨領域視角與結構映射 (`25%`) → ④ 反思盲點與延伸應用 (`25%`) |
| **2. 高階決策備忘錄**<br>*(Executive Strategy Memo)* | 商業調查報告、轉型策略、管理實證 | ① 執行摘要與 SCQA 破題 (`15%`) → ② 核心矛盾與實證數據診斷 (`25%`) → ③ 系統架構與失效機制解剖 (`30%`) → ④ 雙軌治理與分階段行動路線圖 (`30%`) |
| **3. 方法論實踐藍圖**<br>*(Methodological Blueprint)* | 工程架構、演算法、治理管線或操作指南 | ① 核心設計哲學與邊界 (`15%`) → ② 系統架構與運作機制 (`35%`) → ③ 落地步驟與檢核矩陣 (`30%`) → ④ 常見反模式（Anti-patterns）與防禦對策 (`20%`) |
| **4. 跨域知識卡片組**<br>*(Atomic Knowledge Cards)* | 高密度概念萃取、建立個人知識庫 | ① 全局概念索引地圖 (`15%`) → ② 原子概念卡（每卡含：白話定義、運作機制、正反案例、跨域連結）(`65%`) → ③ 實踐自測清單 (`20%`) |

---

## 二、 注意力節律與雙模態混合排版法則（Attention Cadence & Dual-Modal Formatting）

### 1. 「注意力波峰與波谷」交錯節律（Attention Peak-and-Valley Cadence）
- **理論依據**：**雙碼理論（Dual-Coding Theory, Paivio 1986）** 與 **認知負荷理論（Sweller 2011）**。若整份報告全部堆滿卡片與表格，會引發嚴重的「視覺網格疲勞（Grid Fatigue）」；若全部皆為純文字長段落，則缺乏結構錨點。
- **強制交錯結構**：每一個大章節（Section）必須遵循 **「敘事波谷（Narrative Valley）$\rightarrow$ 結構波峰（Structural Peak）$\rightarrow$ 洞見收斂（Synthesis Takeaway）」** 的節律：
  1. **章節前導與過渡敘事段落（Narrative Exposition Paragraphs）**：在進入高密度表格、架構圖或公式前，**必須撰寫未經壓縮的完整散文段落（每段約 180～280 漢字）**，流暢交代背景脈絡、因果推演與「為什麼這件事對決策者至關重要」，建立閱讀呼吸感與邏輯連貫性。
  2. **高密度結構化視覺組件（Tables / Parallel Anatomy Matrices / Cards）**：將多維度對比、階段指標或正反案例收斂為對齊矩陣或雙欄卡片。卡片與表格內的條目一律採用 `● 【白話核心錨點】` 開頭並落實「由淺入深（淺層現象 $\rightarrow$ 中層情境 $\rightarrow$ 深層對策）」。
  3. **獨立公式展示塊（Display Equation Box）**：凡涉及數學、統計或邏輯關係式，一律抽離為獨立置中的展示區塊，並在下方緊接「白話直覺翻譯（Plain-Language Walkthrough）」，逐項解釋每個符號的真實業務意義。

### 2. 原創精煉圖表嵌入與零孤立原則（Seamless Visual Integration）
- 報告必須直接嵌入 Phase 2 生成的高解析度資訊圖譜（Format A）與量化實證圖表（Format D），使用 `<figure>` 搭配完整圖說（Caption）。
- **圖文互文導讀**：每張圖表前後的正文必須明確引導讀者觀察圖中的關鍵落差或轉折，嚴禁「只貼圖不解說」。

---

## 三、 Playwright A4 印刷級 PDF 轉換與防斷框工程規範（Print PDF Engineering）

### 1. A4 邊距擴張與字級舒適度（Expansive Print Margins & Typography）
- **頁面尺寸與擴張印域**：`@page { size: A4 portrait; margin: 11mm 10.5mm 12mm 10.5mm; }`，將實際可列印寬度擴張至 **`189mm`**（較傳統 `16mm` 邊距增加 `11mm` 橫向空間），徹底舒緩多欄比較表與雙欄卡片的垂直折行壓力。
- **字級與行高硬指標**：
  - 正文段落（`p`）：**`10.6pt ~ 11.2pt`**，行高 `1.68 ~ 1.75`，段距 `8px ~ 10px`。
  - 表格與卡片內文（`td`, `.card-body`）：**`9.8pt ~ 10.5pt`**，行高 `1.55 ~ 1.62`。
  - 膠囊標籤與圖說（`.badge`, `figcaption`）：**`9.2pt ~ 9.8pt`**。

### 2. 「大章節起始換頁」與「防跨頁裁切／防溢位斷框」三重鐵律
- **大章節起始強制換頁（Chapter-Boundary Page-Break Rule）**：
  - **換頁點必須設於一級大章節（`<h2>`：貳、參、肆、伍、陸）起始處**（使用 `<div class="page-break"></div>` 置於 `<h2>` 之前，或設定 `h2.chapter-start { break-before: page; page-break-before: always; }`），確保每個核心大章節皆從新頁面頂部乾淨展開！
  - **嚴禁在章節半途插換頁符**：絕對禁止將 `.page-break` 插在同一個章節的「導讀文字／表格」與「對應配圖／矩陣」正中間，導致前一個章節的尾巴掛在下一頁頂部、而新章節標題卻被迫卡在頁面半途！同一章節的論述文字、三線表與視覺圖譜必須聚合於同一章節頁面內完整收束。
- **防跨頁腰斬**：所有視覺容器（`.card`, `.matrix-box`, `figure`, `.equation-box`, `tr`, `.callout`）必須強制加上 CSS：
  ```css
  break-inside: avoid;
  page-break-inside: avoid;
  ```
- **防渲染高度溢位斷框（No Hardcoded Height & No Overflow Hidden）**：
  - **嚴禁**在任何卡片、表格容器或雙欄區塊設定固定高度（`height: ...`）或 `overflow: hidden`。當字級放大或文字折行增加時，`overflow: hidden` 會直接切斷卡片底部框線（Bottom Border Missing）。
  - 雙欄或多欄並列容器必須使用 `display: flex; align-items: stretch;` 或 CSS Grid，外框統一設為整數像素 `border: 1.5px solid <color>; border-radius: 8px; background: #FFFFFF;`。
  - 若卡片帶有頂部色塊標題列（`.card-header`），則將圓角 `border-radius: 6px 6px 0 0;` 設於標題列本身，避免依賴父容器 `overflow: hidden` 裁切圓角。

### 3. 視覺預覽驗證與正式檔單一交付流程
- 渲染腳本統一使用 Python `playwright`（Chromium Headless `page.pdf(print_background=True, prefer_css_page_size=True)`）。
- 生成 PDF 後必須實際檢視每一頁，確認**所有卡片四邊框線完整閉合、無孤行標題（Orphan Headings）、無圖片爆版**，驗證完畢後立即刪除暫存 `.html` 檔。
