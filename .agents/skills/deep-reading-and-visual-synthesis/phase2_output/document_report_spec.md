# 結構化深度報告、雙模態排版與 Medium 數據敘事專欄規範（Format B: Document Report & Medium Column Spec）

> **單一職責定位（Single Responsibility）**：本檔專責 **Format B（結構化深度分析報告 `.md` + 高解析印刷級 `.pdf` 體裁 1～4，以及文體 5：Medium 每週一圖數據敘事專欄 `.md`）** 的文體選擇、注意力節律排版、Playwright A4 印刷 CSS 規格、防斷框工程守則，以及 Medium 專欄 `<= 1,600` 字原生語法與「參考資料來源（僅附：1.官方資料集網址、2.資料涵蓋期間）」分離計字規範。跨格式共用的組塊階層、**筆風設定檔 8 大插槽綁定（Format B 正文散文、表格/卡片錨點、公式導讀、圖說與禁用詞受 `Slot 1`、`Slot 3`、`Slot 4` 與 `Slot 8` 100% 控制）**與分層顏色設定集請見 [`visual_cognition_principles.md`](visual_cognition_principles.md)。

---

## 一、 五大報告與專欄文體、結構配比與「動態擴章 vs. 單一故事線收斂」法則（5 Document Genres & Expansion / Convergence Rules）

- **理論依據**：**體裁分析理論（Genre Analysis, Swales 1990）**、**金字塔原理（Pyramid Principle, Minto 2009）** 與 **馬丁尼杯數據敘事結構（Martini Glass Narrative Structure, Segel & Heer 2010）**。
- **文體 1～4（深度報告）之頁數無硬性上限與動態擴章原則（Zero-Truncation Dynamic Chapters）**：
  - 報告總頁數由內容深度、圖表數量與視覺留白自然決定，**嚴禁設定固定頁數上限（如強行壓縮至 6 頁）或為了湊頁數而灌水**。
  - 當 Phase 1 Step 5 收斂出 $> 4$ 個知識分支（含 `(a) 核心論證主幹分支` 與 `(b) 批判延伸與跨域遷移分支`）時，**嚴禁刪減或合併壓縮延伸議題**！必須**動態擴充一級大章節（`壹、貳、參、肆、伍、陸、柒...`）**，讓每一個批判延伸、假設邊界與跨域遷移分支皆享有獨立完整的「敘事段落 + 三線表/雙欄卡 + 洞見收斂」章節。
- **文體 5（Medium 每週一圖數據敘事專欄）之單一故事線漏斗收斂與 `<= 1,600` 字鐵律**：
  - 針對公開數據新聞與課堂「每週一圖」作業，採用**單一故事線收斂（Single-Hook Convergence）**，正文嚴格控制在 **`<= 1,600` 繁體中文字（不含文末 `---` 下方之參考資料來源附註）**，搭配 1～2 張獨立單面板統計圖（`.png`），**免除編譯 PDF**。

| 文體類型 | 適用場景 | 核心結構與篇幅權重配比（`%`） |
| :--- | :--- | :--- |
| **1. 深度綜合評論**<br>*(Comprehensive Synthesis)* | 跨領域長文、多視角理論交鋒 | ① 核心命題與金字塔結論 (`15%`) → ② 原文論證脈絡與實證拆解 (`35%`) → ③ 跨領域視角與結構映射 (`25%`) → ④ 反思盲點與延伸應用 (`25%`) |
| **2. 高階決策備忘錄**<br>*(Executive Strategy Memo)* | 商業調查報告、轉型策略、管理實證 | ① 執行摘要與 SCQA 破題 (`15%`) → ② 核心矛盾與實證數據診斷 (`25%`) → ③ 系統架構與失效機制解剖 (`30%`) → ④ 雙軌治理與分階段行動路線圖 (`30%`) |
| **3. 方法論實踐藍圖**<br>*(Methodological Blueprint)* | 工程架構、演算法、治理管線或操作指南 | ① 核心設計哲學與邊界 (`15%`) → ② 系統架構與運作機制 (`35%`) → ③ 落地步驟與檢核矩陣 (`30%`) → ④ 常見反模式（Anti-patterns）與防禦對策 (`20%`) |
| **4. 跨域知識卡片組**<br>*(Atomic Knowledge Cards)* | 高密度概念萃取、建立個人知識庫 | ① 全局概念索引地圖 (`15%`) → ② 原子概念卡（每卡含：白話定義、運作機制、正反案例、跨域連結）(`65%`) → ③ 實踐自測清單 (`20%`) |
| **5. Medium 每週一圖數據敘事專欄**<br>*(Medium Data Storytelling Column, `<= 1,600` 字)* | 搭配 CSV 原始檔與《資料說明書》之公開數據新聞、課堂「每週一圖」作業（免編譯 PDF） | ① 新聞感主副標題與反直覺黃金數字 Hook 開場 (`15%`) → ② 圖 1（`01_chart_hook.png`）嵌入與現象結構拆解短段落 (`35%`) → ③ 關鍵數據金句引言塊（Pull Quote）與圖 2（`02_chart_drilldown.png`，選配）深層原因分析 (`35%`) → ④《資料說明書》第 6 章解讀邊界反思與結尾洞見 (`15%`) ＋ `---` 文末參考資料來源（僅附：1.官方資料集網址、2.資料涵蓋期間，**不計入正文 1,600 字額度**） |

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
  - **標準處置規範**：
    1. **概念／架構流程圖改採「A4 直向原生輕量簡圖（`189mm` / `7.44"` 寬，`300 DPI`）」**：當報告某章節需要視覺架構或機制流程圖時，直接呼叫 [`generate_mindmap.py`](../scripts/generate_mindmap.py) 內建之 **`setup_a4_portrait_canvas()` / `draw_a4_node_box()` / `draw_a4_arrow()` / `save_a4_portrait_figure()`**（寬度鎖定 `7.44"`），僅呈現**精簡關鍵詞節點＋有向箭頭＋短標籤（真實字級 `8.5–10.8pt`）**，**絕對禁止將長篇條列散文硬塞進報告圖框**！
    2. **所有高密度論證與對比細節留在原生 HTML 散文與三線表**：圖形負責建立空間與因果直覺，完整論述、數據細節與制度比較統一以 Format B 原生 HTML 散文段落、三線表（`<table>`）與雙欄卡片呈現。
    3. **量化實證圖表（Format D 單面板 `12.0"×6.4"` / `12.8"×6.7"`）可原生直向嵌入**：以 `<figure>` 搭配完整圖說（`figcaption`）並於前後正文進行**圖文互文導讀**（嚴禁「只貼圖不解說」）。

---

## 三、 黑盒引擎 API 簽名、Playwright/Chromium A4 印刷規格與自適應分頁守則（Black-Box Engine API & Adaptive Pagination — 適用文體 1～4）

> [!IMPORTANT]
> **【底層引擎黑盒呼叫鐵律（Black-Box API Rule）】**：[`scripts/pdf_report_engine.py`](../scripts/pdf_report_engine.py)、[`scripts/generate_mindmap.py`](../scripts/generate_mindmap.py)（A4 簡圖 API）與 [`scripts/verify_visual_outputs.py`](../scripts/verify_visual_outputs.py) 已封裝 A4 直向印刷 CSS、現代黑體與標楷體雙模主題、**通用 `<h2>` 殘餘空間自適應分頁**、**短／長表自動分流與輕量尾端保護**及自動轉圖驗收。撰寫生成腳本時，**請直接依下方 API 簽名 `import` 呼叫，日常執行嚴禁呼叫 `view_file` / `read_file` 讀取 `scripts/*.py` 原始碼**（除非發生執行報錯需除錯）！

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
    verify_medium_article_words, # (md_path_or_text, max_body_words=1600) -> dict (Separates body vs. `---` footer, checks <=1,600 words & Medium syntax)
)
```

### 1. A4 邊距擴張與舒適字級規格（Expansive Print Margins & Comfortable Typography）
- **頁面尺寸與擴張印域**：`@page { size: A4 portrait; margin: 11mm 10.5mm 12mm 10.5mm; }`（可列印寬度 **`189mm`**）。
- **舒適字級與行高硬指標**：
  - 正文段落（`p`）：**`10.8pt ~ 11.2pt`**（引擎預設 `10.9pt`），**行高 `1.68 ~ 1.75`**（預設 `1.70`），段距 `margin-bottom: ~8px`（`orphans: 3; widows: 3;`）。
  - 表格、卡片與收斂框（`table`, `td`, `.card-body`, `.callout`）：**`9.6pt ~ 10.0pt`**（引擎預設 `9.8pt`），**行高 `1.50 ~ 1.55`**（預設 `1.52–1.54`），舒適內距（`th, td { padding: 6px 8px; }`、`.card-body { padding: 8px 10px; }`、`.callout { padding: 8px 12px; }`）。
  - 圖說（`figcaption`）：**`9.0pt`**（行高 `1.45`）；表標題（`caption`）：`9.6pt Bold`。
- **傳統中文學術／課程報告排版模式（`theme="clreq_kaiti"`：W3C CLReq `DFKai-SB` 標楷體 ＋ 段落首行空兩格）**：
  - 當使用者指定或任務屬於台灣大專院校正式中文課程報告／傳統公文書格式時，傳入 `theme="clreq_kaiti"` 即可將全篇字型設為 **`font-family: "DFKai-SB", "標楷體", "BiauKai", "Times New Roman", serif;`**，並自動為正文散文段落設定 **`p { text-indent: 2em; }`**（表格 `td`、卡片 `.card-body p`、`.callout p` 與圖說維持不縮排）。
- **PDF 報告與 PPTX 簡報「預設獨立原則」與「特例連動檢查」**：
  - **預設完全獨立（Default Independence）**：一般情況下，Format B（深度報告 `.md`/`.pdf`）與 Format C（簡報 `.pptx`）彼此獨立，**嚴禁在 PDF 報告中自行生成「PPTX 簡報頁次配當表」或互相綁定頁數**，除非使用者或課程規範特別要求。
  - **特例跨格式連動檢查（Conditional Cross-Format Sync）**：唯有當使用者或課程規範明確要求於 PDF 報告中介紹或列出 PPTX 簡報頁次配當表時才予以生成；且一旦建立此連結，後續若修改 PPTX 簡報頁數或結構，**必須主動同步更新 PDF 與 Markdown 報告內所有提及之簡報總頁數與頁次數字**，確保兩者 100% 一致。

### 2. 「通用內容自適應分頁」與「短／長表分流 ＋ 輕量尾端保護」鐵律
- **通用 `<h2>` 殘餘空間自適應分頁（Generic Content-Adaptive Smart Pagination，取代每章強制換頁）**：
  - 嚴禁對所有章節一律寫死 `break-before: page`（會製造大量半頁空白），亦嚴禁在章節半途硬插 `.page-break` 切斷圖文呼應。
  - 直接呼叫 `pdf_report_engine.compile_adaptive_report_pdf()`：引擎自動掃描 HTML 內**任意格式之所有 `<h2>` 標題**（無須寫死 `壹、～柒、` 前綴，完整相容中英文 Markdown/HTML 標題），透過 Chromium 實測每個 `<h2>` 在實際 PDF 頁面下方的剩餘空間比例（`rem_ratio`）：
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

### 3. 視覺預覽驗證與正式檔單一交付流程
- 調用 `compile_html_to_pdf()` 生成 PDF 後，使用 `render_pdf_to_pngs(pdf_path)` 轉出預覽圖並透過 `view_file` 檢視每一頁，確認**所有卡片四邊框線完整閉合、無孤行標題（Orphan Headings）、無圖片爆版或微縮失真**，驗證完畢後立即呼叫 `cleanup_preview_artifacts(out_dir)` 清除所有 `_preview_*.png` 與暫存檔。

---

## 四、 文體 5 專屬規範：Medium 每週一圖數據敘事專欄（`<= 1,600` 字）、參考資料來源分離計字規則與課堂繳交協定（Genre 5: Medium Data Storytelling Column Spec）

### 1. Medium 100% 原生相容語法與七步閱讀結構（Zero Custom HTML / Zero Tables）
- **交付位置與免 PDF 編譯鐵律**：存為 `reading_sessions/<YYYYMMDD_主題簡稱>/02_outputs/02_medium_article.md`（或 `02_report.md`），**免除呼叫 `pdf_report_engine.py` 編譯 A4 PDF**。
- **全面禁用不支援語法**：為確保使用者可直接複製貼上至 `medium.com` 發布，**全面禁用** Medium 不支援的 HTML `.card-grid-2` `<div>` 卡片容器、`<figure>` 標籤，以及任何 **Markdown/HTML 表格（`|---|---|` 或 `<table>`）**！
- **Medium 最佳七步閱讀結構**：
  1. `# 新聞感數據主標題` ＋ `### 一句話破題副標題`（點出核心反差與關鍵發現）
  2. **開場 Hook 短段落**（直接拋出純明細 `df_detail` 最反直覺的核心黃金數字抓眼球）
  3. **`![圖 1 圖說文字](./01_chart_hook.png)`**（主色系 `GEPHI_QUALITATIVE_HEX[0]` / `orange` 破題圖）
  4. **現象解讀與結構拆解**（2～3 個短段落，每段嚴控 3～4 行，最佳化網頁與手機直向閱讀節奏，重點數據以 `**粗體**` 加強）
  5. **`> 關鍵數據金句引言塊（Medium Pull Quote）`**
  6. **`![圖 2 圖說文字](./02_chart_drilldown.png)`（若為雙圖時穿插，次色系 `GEPHI_QUALITATIVE_HEX[1]` / `blue` 深挖圖）＋ 深層原因分析**
  7. **數據背後的解讀邊界與結尾洞見**（自然融入《資料說明書》第 6 章的核心外推邊界，如生態謬誤、抽樣涵蓋偏差或第 3 章前處理反思）

### 2. 文末「參考資料來源」精簡規格鐵律 ＋ 字數分離計算規則（關鍵強制規範）
- **水平分隔線隔離**：在文章正文第 7 步結尾後，必須以水平分隔線 `---` 隔開，附上精簡的 **「參考資料來源」** 附註區塊。
- **內容精簡與正確性鐵律（每筆官方公開資料集僅需附加說明 2 項資訊）**：
  - 列出所引用的**原始官方發布機關與資料集正式名稱**，且每一筆資料集下方**只要附加說明以下 2 項資訊即可**（直接從《資料說明書》第 1 章提取，免除冗長的三重時間戳記、統計母體樣本說明與授權條款段落）：
    1. **官方資料集網址**
    2. **資料涵蓋期間**
  - **絕對禁止將使用者自己生成的「資料說明書」寫成資料來源！**
- **字數分離計算規則（不列入正文 1,600 字計算內）**：
  - 此 `---` 下方的「參考資料來源」附註區塊，**不計入正文 1,600 字額度內**。
  - `---` 上方的**正文（含主副標題、內文段落、引言塊與圖說）嚴格控制在 `<= 1,600` 繁體中文字**。
  - 完稿後可調用 `verify_visual_outputs.verify_medium_article_words("02_medium_article.md")`（或執行 `python scripts/verify_visual_outputs.py --verify-medium 02_medium_article.md`）自動檢驗，並在文稿最底部自動輸出**雙軌字數統計**：
    > `📊 字數統計：正文共 XXX 字（不含文末參考資料來源，符合 <= 1,600 字規範；若含文末來源共 YYY 字）。`

### 3. GitHub 單一檔案協作紀錄自動推送與課堂 Google Doc 繳交懶人區塊
- 將 Phase 1 從「廣角候選切角選單 $\rightarrow$ 互動延伸討論 $\rightarrow$ 漏斗收束定案」的完整討論過程詳實寫入 `reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md`。
- 自動執行 `git add`、`git commit` 與 `git push` 上傳至公開 GitHub 倉庫（依 `git remote get-url origin` 實際綁定之公開倉庫網址，預設為 `https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis`），並在回覆結尾直接印出符合課堂 Google Doc（[每週一圖：作業範例](https://docs.google.com/document/d/1ZQUB9kwHqW162xjAFyPbVNEs-kJQteMvxohhGVhCad0/edit?usp=sharing)）格式的一鍵複製繳交區塊（含該次 `01_phase1_socratic_log.md` 的 **GitHub 單一檔案 `blob/main/...` 完整網址**）：
  ```text
  {學號} {姓名}
  {您的 medium.com 報導連結}
  {您在 Gemini 網頁版製作資料說明書的分享連結 (AI 對話 1)}
  https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis/blob/main/reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md
  ```



