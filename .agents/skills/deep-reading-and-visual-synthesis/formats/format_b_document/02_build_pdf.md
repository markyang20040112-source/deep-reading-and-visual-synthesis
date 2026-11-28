# Format B 終端建構規格（文體 1～4：結構化深度報告與 A4 印刷 PDF 規範）

> **單一職責定位（Single Responsibility）**：本檔專責 **Format B 文體 1～4（結構化深度分析報告 `.md` + 高解析印刷級 `.pdf`）** 的文體選擇、注意力節律排版、內建 A4 直向輕量簡圖 API、Playwright/Chromium A4 印刷 CSS 規格與防斷框工程守則。
> - **文體 5（Medium 每週一圖數據敘事專欄 `.md`，`<= 1,600` 字）已獨立拆出**：請改讀 **[`02_build_medium.md`](./02_build_medium.md)**（與本檔 100% 隔離，互不干擾）。
> - **分枝規劃、驗收與設計武器庫連動**：前置體裁與字體規劃見 [`01_plan.md`](./01_plan.md)；驗收見 [`03_qa.md`](./03_qa.md)；正文散文、表格/卡片錨點、公式導讀與圖說受當前筆風 `Slot 1`、`Slot 3`、`Slot 4` & `Slot 8` 控制（[`../../shared/visual_cognition_core.md`](../../shared/visual_cognition_core.md)）；若主幹或本分枝開啟模式 2，同步載入 **[`../../shared/editorial_narrative_spec.md`](../../shared/editorial_narrative_spec.md)** 以使用編輯室社論組件（`.editorial-masthead`、`.big-stat-callout`、`.myth-reality-split`、`.methodology-traffic-light`）；若開啟模式 3 主題裝幀則按需加載 **[`../../shared/creative_armory/INDEX.md`](../../shared/creative_armory/INDEX.md)**。

---

## 一、 文體 1～4 結構配比與「動態擴章」法則（Document Genres 1–4 & Zero-Truncation）

- **理論依據**：**體裁分析理論（Genre Analysis, Swales 1990）** 與 **金字塔原理（Pyramid Principle, Minto 2009）**。
- **頁數無硬性上限與動態擴章原則（Zero-Truncation Dynamic Chapters）**：
  - 報告總頁數由內容深度、圖表數量與視覺留白自然決定，**嚴禁設定固定頁數上限（如強行壓縮至 6 頁）或為了湊頁數而灌水**。
  - 當 Phase 1 Step 5 收斂出 $> 4$ 個知識分支（含 `(a) 核心論證主幹分支` 與 `(b) 批判延伸與跨域遷移分支`）時，**嚴禁刪減或合併壓縮延伸議題**！必須**動態擴充一級大章節（`壹、貳、參、肆、伍、陸、柒...`）**，讓每一個批判延伸、假設邊界與跨域遷移分支皆享有獨立完整的「敘事段落 + 三線表/雙欄卡 + 洞見收斂」章節。

| 文體類型 | 適用場景 | 核心結構與篇幅權重配比（`%`） |
| :--- | :--- | :--- |
| **1. 深度綜合評論**<br>*(Comprehensive Synthesis)* | 跨領域長文、多視角理論交鋒 | ① 核心命題與金字塔結論 (`15%`) → ② 原文論證脈絡與實證拆解 (`35%`) → ③ 跨領域視角與結構映射 (`25%`) → ④ 反思盲點與延伸應用 (`25%`) |
| **2. 高階決策備忘錄**<br>*(Executive Strategy Memo)* | 商業調查報告、轉型策略、管理實證 | ① 執行摘要與 SCQA 破題 (`15%`) → ② 核心矛盾與實證數據診斷 (`25%`) → ③ 系統架構與失效機制解剖 (`30%`) → ④ 雙軌治理與分階段行動路線圖 (`30%`) |
| **3. 方法論實踐藍圖**<br>*(Methodological Blueprint)* | 工程架構、演算法、治理管線或操作指南 | ① 核心設計哲學與邊界 (`15%`) → ② 系統架構與運作機制 (`35%`) → ③ 落地步驟與檢核矩陣 (`30%`) → ④ 常見反模式（Anti-patterns）與防禦對策 (`20%`) |
| **4. 跨域知識卡片組**<br>*(Atomic Knowledge Cards)* | 高密度概念萃取、建立個人知識庫 | ① 全局概念索引地圖 (`15%`) → ② 原子概念卡（每卡含：白話定義、運作機制、正反案例、跨域連結）(`65%`) → ③ 實踐自測清單 (`20%`) |

*(註：若任務為 **文體 5：Medium 每週一圖數據敘事專欄**，請立即切換至獨立專檔 [`02_build_medium.md`](./02_build_medium.md)，免除編譯 PDF。)*

---

## 二、 注意力節律與雙模態混合排版法則（Attention Cadence & Dual-Modal Formatting — 適用文體 1～4）

### 1. 「注意力波峰與波谷」交錯節律（Attention Peak-and-Valley Cadence）
- **理論依據**：**雙碼理論（Dual-Coding Theory, Paivio 1986）** 與 **認知負荷理論（Sweller 2011）**。若整份報告全部堆滿卡片與表格，會引發嚴重的「視覺網格疲勞（Grid Fatigue）」；若全部皆為純文字長段落，則缺乏結構錨點。
- **強制交錯結構**：每一個大章節（Section）必須遵循 **「敘事波谷（Narrative Valley）$\rightarrow$ 結構波峰（Structural Peak）$\rightarrow$ 洞見收斂（Synthesis Takeaway）」** 的節律：
  1. **章節前導與過渡敘事段落（Narrative Exposition Paragraphs — 受筆風檔 `Slot 3` 控制）**：在進入高密度表格、架構圖或公式前，**必須撰寫未經壓縮的完整散文段落（每段約 180～280 漢字，段落節奏、破題句式與粗體密度嚴格遵循當前筆風檔 `Slot 3`）**，流暢交代背景脈絡、因果推演與核心問題意識，建立閱讀呼吸感與邏輯連貫性。
  2. **高密度結構化視覺組件（Tables / Parallel Anatomy Matrices / Cards — 受筆風檔 `Slot 1` & `Slot 4` 控制）**：將多維度對比、階段指標或正反案例收斂為對齊矩陣或雙欄卡片。卡片與表格內的條目開頭錨點格式（`Anchor_Format`）與三階資訊展開順序，**嚴格遵循當前啟用筆風設定檔之 `Slot 1` 與 `Slot 4` 規範**（例如在 `plain_first_progressive` 筆風下採用 `● 【白話核心錨點】` 由淺入深；在 `rigorous_empirical_stat` 筆風下採用精確統計維度或證據紀律標籤）。
  3. **獨立公式展示塊（Display Equation Box — 受筆風檔 `Slot 4` 控制）**：凡涉及數學、統計或邏輯關係式，一律抽離為獨立置中的展示區塊，並在下方緊接符合當前筆風檔 `Slot 4` 規範之公式導讀（逐項解釋每個符號的真實業務或統計意義與加權口徑）。

### 2. A4 直向原生輕量架構圖與格式解耦鐵律（Strict Format A Decoupling & A4-Portrait-Native Diagrams）
- **【嚴禁將高密度 Format A 知識圖譜嵌入 Format B PDF（亦禁用 A4 橫向 Format A 跨頁）】**：
  - Format A（`23.8" × 12.6"–15.4"` 全景知識圖譜 `.png`）與 Format B（A4 直向深度報告 `.pdf`）為**各自獨立交付**的載體。直接將高密度 Format A 塞入直向 `189mm` 欄位會導致字體微縮難以辨認；強制切換為 A4 橫向滿版跨頁又會打斷報告直向閱讀節律。
  - **標準處置規範（Format B 自給自足，免勾選 Format A）**：
    1. **概念／架構流程圖改採「A4 直向原生輕量簡圖（`189mm` / `7.44"` 寬，`300 DPI`）」**：當報告某章節需要視覺架構或機制流程圖時，直接呼叫 [`../../scripts/generate_mindmap.py`](../../scripts/generate_mindmap.py) 內建之 **`setup_a4_portrait_canvas()` / `draw_a4_node_box()` / `draw_a4_arrow()` / `save_a4_portrait_figure()`**（寬度鎖定 `7.44"`），僅呈現**精簡關鍵詞節點＋有向箭頭＋短標籤（真實字級 `8.5–10.8pt`）**，**絕對禁止將長篇條列散文硬塞進報告圖框**！
    2. **所有高密度論證與對比細節留在原生 HTML 散文與三線表**：圖形負責建立空間與因果直覺，完整論述、數據細節與制度比較統一以 Format B 原生 HTML 散文段落、三線表（`<table>`）與雙欄卡片呈現。
    3. **量化實證圖表（Format D 單面板 `12.0"×6.4"` / `12.8"×6.7"`）可原生直向嵌入**：以 `<figure>` 搭配完整圖說（`figcaption`）並於前後正文進行**圖文互文導讀**（嚴禁「只貼圖不解說」）。

---

## 三、 黑盒引擎 API 簽名、Playwright/Chromium A4 印刷規格與自適應分頁守則（Black-Box Engine API & Adaptive Pagination — 適用文體 1～4）

> [!IMPORTANT]
> **【底層引擎黑盒呼叫鐵律（Black-Box API Rule）】**：[`../../scripts/pdf_report_engine.py`](../../scripts/pdf_report_engine.py)、[`../../scripts/generate_mindmap.py`](../../scripts/generate_mindmap.py)（A4 簡圖 API）與 [`../../scripts/verify_visual_outputs.py`](../../scripts/verify_visual_outputs.py) 已封裝 A4 直向印刷 CSS、現代黑體與標楷體雙模主題、**通用 `<h2>` 殘餘空間自適應分頁**、**短／長表自動分流與輕量尾端保護**及自動轉圖驗收。撰寫生成腳本時，**請直接依下方 API 簽名 `import` 呼叫，日常執行嚴禁呼叫 `view_file` / `read_file` 讀取 `scripts/*.py` 原始碼**（除非發生執行報錯需除錯）！

```python
# === scripts/pdf_report_engine.py, generate_mindmap (A4) & verify_visual_outputs.py Black-Box API ===
from pdf_report_engine import (
    load_document_theme,         # (doc_theme_id=None) -> Dict[str, str]
    build_report_css,            # (theme="modern_sans" | "clreq_kaiti", body_pt=10.9, doc_theme_id=None) -> str
    apply_content_adaptive_rules,# (body_html, short_table_max_rows=5) -> str (Tags table-short/table-long & light-tail callout)
    wrap_report_html,            # (title, body_html, theme="modern_sans", body_pt=10.9, extra_css="", doc_theme_id=None, adaptive_layout=True) -> str
    compile_html_to_pdf,         # (html_content_or_path, output_pdf_path, cleanup_temp_html=True, wait_ms=400) -> str
    compile_adaptive_report_pdf, # (title, body_html, output_pdf_path, theme="modern_sans", body_pt=10.9, extra_css="", doc_theme_id=None, genre=None, min_remaining_ratio=None, skip_first_h2=True, return_diagnostics=False) -> str | dict
)
from generate_mindmap import (
    setup_a4_portrait_canvas,    # (height_in=2.30, dpi=300, theme="swiss_editorial") -> (fig, ax, theme_dict) [7.44" / 189mm]
    draw_a4_node_box,            # (ax, x, y, w, h, badge, title, lines=None, theme=None, accent_key="primary") -> (x, y, w, h)
    draw_a4_arrow,               # (ax, p0, p1, label=None, theme=None, accent_key="primary", rad=0.0, label_dy=8.5, font_pt=8.0) -> None
    save_a4_portrait_figure,     # (fig, output_path, theme=None, dpi=300) -> None
)
from verify_visual_outputs import (
    render_pdf_to_pngs,          # (pdf_path, out_dir=None, dpi=180) -> List[str] (Generates _preview_<stem>_p01.png, ...)
    cleanup_preview_artifacts,   # (target_dir) -> List[str] (Removes _preview_*.png, _tmp_*.html, test_*.png)
)
```

### 1. A4 邊距擴張與舒適字級規格（Expansive Print Margins & Comfortable Typography）
- **頁面尺寸、擴張印域與單行最佳行寬**：`@page { size: A4 portrait; margin: 11mm 10.5mm 12mm 10.5mm; }`（可列印寬度 **`189mm`**，正文單行最佳漢字寬度 **`38～44` 漢字**，透過頁邊距與段落間距維持視覺呼吸感）。
- **舒適字級與行高硬指標**：
  - 報告主標題（`h1`）：**`20pt ~ 24pt Bold`**；章節與區塊標題（`h2`, `h3`）：**`12.0pt ~ 14.5pt Bold`**。
  - 正文段落（`p`）：**`10.8pt ~ 11.2pt`**（引擎預設 `10.9pt`），**行高 `1.68 ~ 1.75`**（預設 `1.70`），段距 `margin-bottom: ~8px`（`orphans: 3; widows: 3;`）。
  - 表格、卡片與收斂框（`table`, `td`, `.card-body`, `.callout`）：**`9.6pt ~ 10.0pt`**（引擎預設 `9.8pt`），**行高 `1.50 ~ 1.55`**（預設 `1.52–1.54`），舒適內距（`th, td { padding: 6px 8px; }`、`.card-body { padding: 8px 10px; }`、`.callout { padding: 8px 12px; }`）。
  - 圖說（`figcaption`）：**`9.0pt`**（行高 `1.45`）；表標題（`caption`）：`9.6pt Bold`。
- **傳統中文學術／課程報告排版模式（`theme="clreq_kaiti"`：W3C CLReq `DFKai-SB` 標楷體 ＋ 段落首行空兩格）**：
  - 當使用者於 [`01_plan.md`](./01_plan.md) 指定或任務屬於台灣大專院校正式中文課程報告／傳統公文書格式時，傳入 `theme="clreq_kaiti"` 即可將全篇字型設為 **`font-family: "DFKai-SB", "標楷體", "BiauKai", "Times New Roman", serif;`**，並自動為正文散文段落設定 **`p { text-indent: 2em; }`**（表格 `td`、卡片 `.card-body p`、`.callout p` 與圖說維持不縮排）。
- **PDF 報告與 PPTX 簡報「預設獨立原則」與「特例連動檢查」**：
  - **預設完全獨立（Default Independence）**：一般情況下，Format B（深度報告 `.md`/`.pdf`）與 Format C（簡報 `.pptx`）彼此獨立，**嚴禁在 PDF 報告中自行生成「PPTX 簡報頁次配當表」或互相綁定頁數**，除非使用者或課程規範特別要求。
  - **特例跨格式連動檢查（Conditional Cross-Format Sync）**：唯有當使用者或課程規範明確要求於 PDF 報告中介紹或列出 PPTX 簡報頁次配當表時才予以生成；且一旦建立此連結，後續若修改 PPTX 簡報頁數或結構，**必須主動同步更新 PDF 與 Markdown 報告內所有提及之簡報總頁數與頁次數字**，確保兩者 100% 一致。

### 2. 「通用內容自適應分頁」與「短／長表分流 ＋ 輕量尾端保護」鐵律
- **通用 `<h2>` 殘餘空間自適應分頁（Generic Content-Adaptive Smart Pagination，取代每章強制換頁）**：
  - 嚴禁對所有章節一律寫死 `break-before: page`（會製造大量半頁空白），亦嚴禁在章節半途硬插 `.page-break` 切斷圖文呼應。
  - 直接呼叫 `pdf_report_engine.compile_adaptive_report_pdf()`（多輪分頁量測與定稿自動重用單一 Playwright Chromium 實例以加速編譯，外部簽名不變）：引擎自動掃描 HTML 內**任意格式之所有 `<h2>` 標題**（無須寫死 `壹、～柒、` 前綴，完整相容中英文 Markdown/HTML 標題），透過 Chromium 實測每個 `<h2>` 在實際 PDF 頁面下方的剩餘空間比例（`rem_ratio`）：
    - 剩餘空間 $\ge$ `min_remaining_ratio` 時自然接續流動；
    - 剩餘空間 $<$ `min_remaining_ratio` 時自動注入 `chapter-start` 換頁，確保新章節從頁頂乾淨展開。
  - **文體自適應門檻（`genre` 參數）**：結構化備忘錄／方法論藍圖（`genre="memo"` / `"blueprint"`）預設 **`0.34`（`~0.30–0.35`）**；連續敘事評論／知識卡片（`genre="synthesis"` / `"cards"`）預設 **`0.22`（`~0.20–0.25`）**。
- **內容自適應防斷頭／防孤尾與短／長表分流（取代僵化 `table + callout` 硬綁）**：
  1. **標題與段落連貫鎖定**：`h2, h3, h4, caption { break-after: avoid; }` ＋ `p { orphans: 3; widows: 3; }`，杜絕頁底孤行標題或表題與表格分離。
  2. **短表整張保護 vs. 長表跨頁重複表頭**：`apply_content_adaptive_rules()` 自動計算每張 `<table>` 之表身資料列數（`<tbody> tr`）：
     - **短表（`<= 5` 列）** 自動賦予 `table-short`（`break-inside: avoid`），整張表完整呈現不被拆頁；
     - **長表（`> 5` 列）** 自動賦予 `table-long`（`break-inside: auto`），允許在資料列之間乾淨跨頁（搭配 `tr { break-inside: avoid; }` 禁單列腰斬與 `thead { display: table-header-group; }` 於續頁頂端自動重複表頭）。
  3. **彈性輕量尾端保護（Flexible Light-Tail Protection）**：`.callout` 本身設定 `break-inside: avoid`；引擎僅在 2～3 行 `.callout` 緊接於**輕量級前導區塊**（短段落 `p <= 240` 字、`.equation-box`、精簡 `.card-grid` 或 `<= 3` 列小表）之後時自動附加 `keep-with-prev`（`break-before: avoid`），**絕不將大型 `<figure>` 或長表格硬綁進 `break-inside: avoid` 容器**，避免將整張大圖／長表拖往下一頁製造空白帶。
- **防溢位斷框（No Hardcoded Height & No Overflow Hidden）**：
  - 所有結構容器（`.card`, `.matrix-box`, `figure`, `.equation-box`, `tr`, `.callout`）均受 `break-inside: avoid` 保護；**嚴禁**在卡片或容器設定固定 `height` 或 `overflow: hidden`（會切斷底部框線），標題列圓角一律設於 `.card-header` 本身（`border-radius: 6px 6px 0 0;`）。

---

## 四、 編輯室社論組件（模式 2 Print-CSS Components）

當主幹或本分枝開啟 **模式 2 (`editorial_narrative`)**（或模式 3 併同選用編輯室社論排版）時，`scripts/pdf_report_engine.py` 內建以下 4 組經 Chromium A4 實測防斷框（`break-inside: avoid`、零固定高度）之編輯室社論組件可供呼叫（完整 HTML 範本見 [`../../shared/editorial_narrative_spec.md`](../../shared/editorial_narrative_spec.md) 第二節）：
- **`.editorial-masthead`**（搭配 `.masthead-kicker`、`<h1>`、`.masthead-deck`）：報刊頭條頂部粗橫線開篇區。
- **`.big-stat-callout`**（搭配 `.big-stat-number`、`.big-stat-label`）：巨型黃金數字衝擊盒。
- **`.myth-reality-split`**（搭配 `.myth-box` 左紅 vs. `.reality-box` 右綠）：常見直覺迷思 vs. 實證真相雙欄對撞解剖台。
- **`.methodology-traffic-light`**（搭配 `.traffic-tier` 及 `.traffic-badge-green` / `.traffic-badge-yellow` / `.traffic-badge-red`）：對應《資料說明書》證據紀律標籤之方法論紅黃綠燈警示卡。

*(編譯完成後立即依 **[`03_qa.md`](./03_qa.md)** 執行全頁轉圖實地驗收與暫存檔清理。)*
