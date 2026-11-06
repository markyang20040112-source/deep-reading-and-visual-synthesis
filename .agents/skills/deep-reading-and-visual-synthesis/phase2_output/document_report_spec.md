# 結構化深度報告與雙模態排版規範（Format B: Document Report Spec）

> **單一職責定位（Single Responsibility）**：本檔專責 **Format B（結構化深度分析報告 `.md` 與高解析印刷級 `.pdf`）** 的文體選擇、注意力節律排版、Playwright A4 印刷 CSS 規格與防斷框工程守則。跨格式共用的組塊階層、白話由淺入深原則與基礎色票請見 `visual_cognition_principles.md`。

---

## 一、 四大報告文體、結構配比與「動態擴章零刪減」法則（4 Document Genres & Dynamic Chapter Expansion）

- **理論依據**：**體裁分析理論（Genre Analysis, Swales 1990）** 與 **金字塔原理（Pyramid Principle, Minto 2009）**。
- **頁數無硬性上限與動態擴章原則（Zero-Truncation Dynamic Chapters）**：
  - 報告總頁數由內容深度、圖表數量與視覺留白自然決定，**嚴禁設定固定頁數上限（如強行壓縮至 6 頁）或為了湊頁數而灌水**。
  - 當 Phase 1 Step 5 收斂出 $> 4$ 個知識分支（含 `(a) 核心論證主幹分支` 與 `(b) 批判延伸與跨域遷移分支`）時，**嚴禁刪減或合併壓縮延伸議題**！必須**動態擴充一級大章節（`壹、貳、參、肆、伍、陸、柒...`）**，讓每一個批判延伸、假設邊界與跨域遷移分支皆享有獨立完整的「敘事段落 + 三線表/雙欄卡 + 洞見收斂」章節。以下百分比（`%`）代表**全篇篇幅與認知權重的相對配比**：

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

### 2. 原創精煉圖表嵌入與「寬幅圖譜 A4 橫向滿版專頁」法則（Seamless Visual Integration & Landscape Figure Page）
- 報告必須直接嵌入 Phase 2 生成的高解析度資訊圖譜（Format A）與量化實證圖表（Format D，或數據儀表板靜態全景圖 Format E），使用 `<figure>` 搭配完整圖說（Caption），並於前後正文進行**圖文互文導讀**（嚴禁「只貼圖不解說」）。
- **寬幅高密度圖表防微縮鐵律（A4 Landscape Figure Page or Native HTML Anatomy Table）**：
  - Format A 全景知識圖譜（`28" × 18.5"`）與 Format E 靜態全景儀表板圖（`24" × 14"`）若直接縮小塞入直向（Portrait `189mm`）欄位，圖內 `12pt` 文字會被壓縮至 `< 5pt` 導致難以辨識。
  - **標準處置方案（二擇一或並用）**：
    1. **專用 A4 橫向滿版圖表頁（`@page landscape-fig` + `<div class="landscape-page">`）**：直接套用 [`scripts/pdf_report_engine.py`](../scripts/pdf_report_engine.py) 內建之 `.landscape-page` 容器，使該張寬幅圖譜自動獨佔一頁 **A4 橫向（Landscape `297mm × 210mm`）滿版頁面**，讓圖內文字放大逾 $1.55\times$、清晰銳利！
    2. **搭配原生 HTML 平行解剖三線表／卡片矩陣**：在直向正文中以原生 HTML 表格或雙欄卡片完整展開圖譜內的文字細節，使讀者既能於圖譜綜觀全局拓撲，又能以原生向量文字精讀細節。

---

## 三、 黑盒引擎 API 簽名、Playwright A4 印刷規格與防斷框守則（Black-Box Engine API & Print PDF Engineering）

> [!IMPORTANT]
> **【底層引擎黑盒呼叫鐵律（Black-Box API Rule）】**：[`scripts/pdf_report_engine.py`](../scripts/pdf_report_engine.py) 與 [`scripts/verify_visual_outputs.py`](../scripts/verify_visual_outputs.py) 已封裝 A4 直向／橫向印刷 CSS、現代黑體與標楷體雙模主題、Playwright PDF 編譯及自動轉圖驗收。撰寫生成腳本時，**請直接依下方 API 簽名 `import` 呼叫，日常執行嚴禁呼叫 `view_file` / `read_file` 讀取 `scripts/*.py` 原始碼**（除非發生執行報錯需除錯）！

```python
# === scripts/pdf_report_engine.py & verify_visual_outputs.py Black-Box API Signatures ===
from pdf_report_engine import (
    build_report_css,       # (theme="modern_sans" | "clreq_kaiti", body_pt=10.8) -> str (Includes @page 189mm, @page landscape-fig, .card-grid-2/3, Ehrenberg table)
    wrap_report_html,       # (title, body_html, theme="modern_sans" | "clreq_kaiti", body_pt=10.8, extra_css="") -> str
    compile_html_to_pdf,    # (html_content_or_path, output_pdf_path, cleanup_temp_html=True) -> str (Auto-removes temp .html)
)
from verify_visual_outputs import (
    render_pdf_to_pngs,        # (pdf_path, out_dir=None, dpi=180) -> List[str] (Generates _preview_<stem>_p01.png, ...)
    cleanup_preview_artifacts, # (target_dir) -> List[str] (Removes _preview_*.png, _tmp_*.html, test_*.png)
)
```

### 1. A4 邊距擴張與字級舒適度（Expansive Print Margins & Typography）
- **頁面尺寸與擴張印域**：`@page { size: A4 portrait; margin: 11mm 10.5mm 12mm 10.5mm; }`（可列印寬度 **`189mm`**）；寬幅圖表專頁 `@page landscape-fig { size: A4 landscape; margin: 8mm 10mm 8mm 10mm; }`（搭配 `<div class="landscape-page"><figure>...</figure></div>`）。
- **字級與行高硬指標**：
  - 正文段落（`p`）：**`10.6pt ~ 11.2pt`**（若為高密度大專院校個案報告可微調至 `9.2pt ~ 10.5pt`），行高 `1.62 ~ 1.75`，段距 `6px ~ 10px`。
  - 表格與卡片內文（`td`, `.card-body`）：**`9.0pt ~ 10.5pt`**，行高 `1.45 ~ 1.62`。
  - 膠囊標籤與圖說（`.badge`, `figcaption`）：**`8.8pt ~ 9.8pt`**。
- **傳統中文學術／課程報告排版模式（`theme="clreq_kaiti"`：W3C CLReq `DFKai-SB` 標楷體 ＋ 段落首行空兩格）**：
  - 當使用者指定或任務屬於台灣大專院校正式中文課程報告／傳統公文書格式時，傳入 `theme="clreq_kaiti"` 即可將全篇字型設為 **`font-family: "DFKai-SB", "標楷體", "BiauKai", "Times New Roman", serif;`**，並自動為正文散文段落設定 **`p { text-indent: 2em; }`**（表格 `td`、卡片 `.card-body p` 與圖說維持不縮排）。
- **PDF 報告與 PPTX 簡報「預設獨立原則」與「特例連動檢查」**：
  - **預設完全獨立（Default Independence）**：一般情況下，Format B（深度報告 `.md`/`.pdf`）與 Format C（簡報 `.pptx`）彼此獨立，**嚴禁在 PDF 報告中自行生成「PPTX 簡報頁次配當表」或互相綁定頁數**，除非使用者或課程規範特別要求。
  - **特例跨格式連動檢查（Conditional Cross-Format Sync）**：唯有當使用者或課程規範明確要求於 PDF 報告中介紹或列出 PPTX 簡報頁次配當表時才予以生成；且一旦建立此連結，後續若修改 PPTX 簡報頁數或結構，**必須主動同步更新 PDF 與 Markdown 報告內所有提及之簡報總頁數與頁次數字**，確保兩者 100% 一致。

### 2. 「大章節起始換頁」與「防跨頁裁切／防溢位斷框」三重鐵律
- **大章節起始強制換頁（Chapter-Boundary Page-Break Rule）**：
  - **換頁點必須設於一級大章節（`<h2 class="chapter-start">`：貳、參、肆、伍、陸、柒...）起始處**，確保每個核心大章節皆從新頁面頂部乾淨展開！
  - **嚴禁在章節半途插換頁符**：絕對禁止將 `.page-break` 插在同一個章節的「導讀文字／表格」與「對應配圖／矩陣」正中間，導致前一個章節的尾巴掛在下一頁頂部、而新章節標題卻被迫卡在頁面半途！
- **防跨頁腰斬與防溢位斷框（No Hardcoded Height & No Overflow Hidden）**：
  - 所有視覺容器（`.card`, `.matrix-box`, `figure`, `.equation-box`, `tr`, `.callout`）皆已由 `pdf_report_engine.py` 強制設定 `break-inside: avoid; page-break-inside: avoid;`。
  - **嚴禁**在任何卡片、表格容器或雙欄區塊設定固定高度（`height: ...`）或 `overflow: hidden`（會切斷卡片底部框線）。頂部標題列圓角一律設於 `.card-header` 本身（`border-radius: 6px 6px 0 0;`）。

### 3. 視覺預覽驗證與正式檔單一交付流程
- 調用 `compile_html_to_pdf()` 生成 PDF 後，使用 `render_pdf_to_pngs(pdf_path)` 轉出預覽圖並透過 `view_file` 檢視每一頁，確認**所有卡片四邊框線完整閉合、無孤行標題（Orphan Headings）、無圖片爆版或微縮失真**，驗證完畢後立即呼叫 `cleanup_preview_artifacts(out_dir)` 清除所有 `_preview_*.png` 與暫存檔。

