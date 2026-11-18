# Medium 每週一圖數據敘事專欄規範（Format B Genre 5: Medium Data Storytelling Column Spec）

> **單一職責定位（Single Responsibility）**：本檔專責 **Format B 文體 5：Medium 每週一圖數據敘事專欄（`<= 1,600` 繁體中文字 `.md`）**，**僅當第二層（[`advisors/layer2_advisor_b_report.md`](advisors/layer2_advisor_b_report.md)）選定文體 5 時才按需載入**。本檔已與 A4 PDF 深度報告（[`document_report_spec.md`](document_report_spec.md)）徹底解耦隔離，確保 AI 撰寫 Medium 專欄時 100% 遵守原生 Markdown 語法、免編譯 PDF 與字數分離計算鐵律，不受任何 HTML 卡片或表格規則幹擾。
> - **筆風 `Slot 3`, `Slot 4` & `Slot 8` 穿透**：破題句式、段落呼吸節奏、引言塊語氣與禁用詞受當前啟用筆風檔控制（詳見 [`visual_cognition_principles.md`](visual_cognition_principles.md)）。
> - **配圖色彩接力連動**：搭配產出之 1～2 張獨立單面板統計圖須遵守 [`quantitative_chart_spec.md`](quantitative_chart_spec.md) 第二節第 2 點「Medium 獨立單面板色彩接力規則」。

---

## 一、 Medium 100% 原生相容語法與免 PDF 編譯鐵律（Zero Custom HTML / Zero Tables）

1. **交付位置與免除 PDF 編譯**：
   - 存為 `reading_sessions/<YYYYMMDD_主題簡稱>/02_outputs/02_medium_article.md`（或 `02_report.md`）。
   - **嚴格免除呼叫 `scripts/pdf_report_engine.py` 編譯 A4 PDF**；僅對搭配產出的 1～2 張 `.png` 統計圖執行 `view_file` 視覺驗收。
2. **全面禁用 Medium 不支援語法**：
   - 為確保使用者可直接全文複製貼上至 `medium.com` 發布且版面 100% 正常，**全面禁用** `.card-grid-2`、`<div>` 卡片容器、`<figure>` / `<figcaption>` HTML 標籤，以及任何 **Markdown 或 HTML 表格（`|---|---|` 或 `<table>`）**！
3. **配圖張數與獨立單面板限制**：
   - 搭配 **1～2 張各自獨立的單面板 `300 DPI` `.png` 統計圖**（`01_chart_hook.png` 採色序 1 主色系破題；選配之 `02_chart_drilldown.png` 採色序 2 次色系深挖，**嚴禁使用 `ncols=2` 橫向並排雙子圖**）。

---

## 二、 Medium 最佳七步閱讀結構（Mobile & Web Scannability）

| 閱讀步驟 | 構成元素與篇幅建議 | 寫作與視覺整合規範 |
| :---: | :--- | :--- |
| **Step 1** | `# 新聞感數據主標題` ＋ `### 一句話破題副標題` | 直接點出純明細 `df_detail` 最反差的核心發現或反直覺比率（避免學術報告式呆板標題）。 |
| **Step 2** | **開場 Hook 短段落**（`15%`） | 以 1～2 個短段落拋出最抓眼球的黃金數字或具體個案，建立閱讀張力。 |
| **Step 3** | **`![圖 1 圖說文字](./01_chart_hook.png)`** | 插入主色系破題主圖，並於緊鄰下方展開現象拆解。 |
| **Step 4** | **現象解讀與結構拆解短段落**（`35%`） | 分為 2～3 個短段落，**每段嚴控 3～4 行以適配手機直向滑動閱讀**，重點統計數據以 `**粗體**` 加強；若第三層開啟模式 2/3，亦嚴守自然流暢的數據新聞口吻。 |
| **Step 5** | **`> 關鍵數據金句引言塊（Medium Pull Quote）`** | 提煉全篇最震撼的 1 句結構性反差或政策警語作為視覺呼吸錨點。 |
| **Step 6** | **`![圖 2 圖說文字](./02_chart_drilldown.png)`** ＋ **深層原因分析**（`35%`） | 若產出雙圖，於此穿插次色系深挖圖並剖析背後驅動機制或結構異質性。 |
| **Step 7** | **《資料說明書》第 6 章解讀邊界反思與結尾洞見**（`15%`） | 自然融入生態謬誤提醒、母體涵蓋限制、跨年名目金額或第 3 章前處理血統（Winsorization/Imputation）之誠實邊界，最後收斂洞見。 |

---

## 三、 文末「參考資料來源」分離計字鐵律 ＋ 自動化字數檢驗

```python
# === scripts/verify_visual_outputs.py Black-Box API ===
from verify_visual_outputs import (
    verify_medium_article_words, # (md_path_or_text, max_body_words=1600) -> dict
)
```

1. **水平分隔線 `---` 強制隔離**：在正文 Step 7 結尾後，必須加上水平分隔線 `---`，於下方附上 **「參考資料來源」** 附註區塊。
2. **來源精簡與正確性鐵律（每筆官方公開資料集僅附 2 項資訊）**：
   - 列出實際引用之**原始官方發布機關與資料集正式名稱**（**絕對禁止將使用者自己生成的「資料說明書」寫成資料來源！**）。
   - 每筆資料集下方**只要附加說明以下 2 項資訊即可**（直接從《資料說明書》第 1 章提取，免除冗長授權與統計母體段落）：
     1. **官方資料集網址**
     2. **資料涵蓋期間**
3. **分離計字規則（不計入正文 1,600 字額度內）**：
   - `---` 上方之**正文（含主副標題、內文段落、引言塊與圖片替代文字）嚴格控制在 `<= 1,600` 繁體中文字**；`---` 下方之參考資料來源不計入該額度。
   - 完稿後執行 `verify_medium_article_words("02_medium_article.md")`（或 CLI `python scripts/verify_visual_outputs.py --verify-medium 02_medium_article.md`）驗證無自訂 HTML／表格且字數合規，並於文稿最底部印出雙軌統計：
     > `📊 字數統計：正文共 XXX 字（不含文末參考資料來源，符合 <= 1,600 字規範；若含文末來源共 YYY 字）。`

---

## 四、 GitHub 單一檔案對話紀錄推送與課堂 Google Doc 繳交區塊

完成視覺驗收與分離計字驗證後，依 **[`../setup/git_sync_and_evolution_protocol.md`](../setup/git_sync_and_evolution_protocol.md)** 第三節規範，將完整思辨軌跡 `01_phase1_socratic_log.md` 與產出檔推送至公開倉庫（或依課程繳交連結規範分享），並在回覆結尾輸出符合課堂 Google Doc 格式的一鍵複製繳交區塊：

```text
{學號} {姓名}
{您的 medium.com 報導連結}
{您在 Gemini 網頁版製作資料說明書的分享連結 (AI 對話 1)}
https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis/blob/main/reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md
```
