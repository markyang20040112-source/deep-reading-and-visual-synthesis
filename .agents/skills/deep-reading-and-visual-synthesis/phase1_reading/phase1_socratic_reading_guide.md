# 第一階段：蘇格拉底式深度閱讀與漏斗式數據敘事總路由 (Phase 1 Master Router)

> [!CAUTION]
> **階段鐵律**：
> 1. 只要使用者未明確要求「跳過第一階段／直接生成」，**絕對禁止**在使用者表達個人初步觀點前輸出全文罐頭摘要、重點條列或最終批次圖表！
> 2. **按需載入（Zero-Waste Lazy Loading）**：本檔為 Phase 1 輕量總路由。收到輸入後，**僅依下方分流表按需讀取對應之單一子協定檔**（文獻讀 [`mode1_article_socratic_protocol.md`](./mode1_article_socratic_protocol.md)；CSV＋資料說明書讀 [`mode2_dataset_codebook_protocol.md`](./mode2_dataset_codebook_protocol.md)），**嚴禁同時載入無關模式的子檔或提前讀取 `../phase2_output/`**（唯獨模式 2 軌道 C「分配圖形逐步導學」可按需連動讀取 [`../phase2_output/distribution_and_density_chart_spec.md`](../phase2_output/distribution_and_density_chart_spec.md)）。
> 3. 若使用者**明確下令跳過引導直接生成（Fast-Track）**，先將原文存入 `00_source_article.md`（若含原始 CSV 則原封不動存入 `data/<原檔名>.csv`），直接切換讀取 [`../phase2_output/phase2_output_router.md`](../phase2_output/phase2_output_router.md) 並依**「三層漸進式決策漏斗（Layer 1 $\rightarrow$ Layer 2 $\rightarrow$ Layer 3）」**推進確認，同步逐層寫入 `02_phase2_generation_blueprint.md`。
> 4. **靈感暫存守則**：互動中若產生任何技能優化靈感，嚴格遵循 [`../SKILL.md`](../SKILL.md) 第三節規定，僅寫入 `reading_sessions/_pending_skill_inspirations.md` 暫存，嚴禁中斷閱讀流程或私自改檔。

---

## 零、 第一道垂直工序：輸入媒介嗅探與黑盒正規化閘門 (Stage 0: Input Modality Sniffing & Black-Box Normalization)

收到任何外部素材或連結時，必須嚴格執行**兩段式垂直工序**，確保不浪費 LLM Token 人工讀檔，且先完成物理正規化再決定思辨協定：

1. **工序 1（物理媒介正規化 — 先判斷素材型態再決定讀入／轉檔方式）**：
   - **網頁 URL / YouTube 連結 / 本機 `.pdf` / 本機 `.docx`**：立即呼叫黑盒腳本 [`../scripts/ingest_source_material.py`](../scripts/ingest_source_material.py)（CLI 或 `ingest_to_source_markdown()`）於背景自動清洗並轉存為 `reading_sessions/<YYYYMMDD_主題簡稱>/00_source_article.md`（日常執行嚴禁讀取該 `.py` 原始碼）。若網頁遇 Cloudflare／登入牆回傳 `BLOCKED_OR_TOO_SHORT`，則禮貌告知原因並請使用者直接貼上正文。
   - **`.csv` / 資料表 ＋《資料說明書》**：原始 CSV **原封不動**存入 `data/<原檔名>.csv`；《資料說明書》存入 `00_source_article.md`。
   - **對話框直接貼上之文章／逐字稿純文字**：直接原封不動寫入 `00_source_article.md`。
2. **工序 2（思辨協定路由 — 僅開啟唯一對應子協定檔）**：待 `00_source_article.md`（與 `data/*.csv`）正規化就緒後，始依下方「四大輸入模式自動分流表」按需載入唯一對應子協定檔。

```python
# === scripts/ingest_source_material.py Black-Box API Signatures ===
from ingest_source_material import (
    detect_input_modality,           # (source_input: str) -> "youtube" | "web_url" | "pdf_file" | "docx_file" | "csv_dataset" | "text_or_md"
    ingest_url_to_markdown,          # (url, output_md_path=None, timeout=20, title_override=None) -> dict
    ingest_youtube_transcript,       # (url_or_id, output_md_path=None, preferred_langs=(...), title_override=None) -> dict
    ingest_local_document_to_markdown, # (file_path, output_md_path=None, title_override=None) -> dict (.pdf/.docx/.md/.txt)
    ingest_to_source_markdown,       # (source_input, output_md_path, title_override=None) -> dict (Unified Stage 0 Dispatcher)
)
# CLI: python .agents/skills/deep-reading-and-visual-synthesis/scripts/ingest_source_material.py --input "<URL或檔案>" --output "<00_source_article.md>"
```

---

## 一、 四大輸入模式自動分流與按需載入表 (4 Input Modes & Lazy-Loading Dispatch Table)

收到使用者輸入時，先依輸入型態執行對應之歸檔，並**僅開啟對應之子協定檔**：

| 輸入模式 | 觸發特徵 | 原始檔案歸檔方式 | 按需載入之唯一子協定檔與核心任務 |
| :--- | :--- | :--- | :--- |
| **模式 1：單篇文獻／報告／逐字稿**<br>*(Single Article / Paper)* | 單篇商業評論、學術論文、個案或演講稿 | 完整存入 `00_source_article.md` | 👉 **開啟 [`./mode1_article_socratic_protocol.md`](./mode1_article_socratic_protocol.md)**<br>執行標準 **Step 0 ～ Step 5 蘇格拉底五步思辨**（初始探針 1 題 $\rightarrow$ 雙維詰問每輪 2 題 $\rightarrow$ 跨域類比 $\rightarrow$ 零刪減雙群組收斂）。 |
| **模式 2：純結構化數據集／CSV ＋《資料說明書》數據敘事＆分配圖形導學**<br>*(Structured Dataset / Data Codebook, Medium Column & Distribution Tutor)* | 傳入 `.csv`（常搭配依據 HackMD 規範生成的《資料說明書 Data Codebook》及使用者提示詞）、`.json`、資料表或開放數據指標 | **原始 CSV 原封不動存入 `data/<原檔名>.csv`（嚴禁改動）**；《資料說明書》存入 `00_source_article.md` | 👉 **開啟 [`./mode2_dataset_codebook_protocol.md`](./mode2_dataset_codebook_protocol.md)**<br>啟動 **「讀取（Read）— 分析（Analyze）— 討論（Discuss）漏斗式數據敘事三迴路」**：背景 Python `load_and_split_csv()` 零 Token 浪費掃描、兩段式安全轉型、標準化三層互斥分流（`df_detail`/`df_other`/`df_subtotal`）、8/5 欄字典直通車與純明細極值重算、五種證據標籤與前處理血統過濾、三軌 Track A/B/C 探索（含 10 大分配圖形逐步導學）、製圖 6 條件全預填確認表（含 `df_other` 雙重消歧）、第 6 章外推邊界護欄與單一故事線收斂。 |
| **模式 3：多檔案專案／課程診斷包**<br>*(Multi-File Diagnostic Package)* | 傳入多個簡報、報告、草稿與課程／專案評分規範 | 原始檔案歸入 `00_drive_source_files/`，建立 `00_source_article.md` 總索引 | 👉 **開啟 [`./mode1_article_socratic_protocol.md`](./mode1_article_socratic_protocol.md)**<br>建立**「評分標準／需求矩陣對齊表（Rubric & Requirement Alignment Matrix）」**，逐項診斷結構斷層與視覺痛點並執行五步思辨收斂。 |
| **模式 4：多篇跨文獻綜合統整**<br>*(Multi-Article Synthesis)* | 要求跨多篇已讀文章或多個 `reading_sessions/` 進行融會貫通 | 於 `00_source_article.md` 列出跨篇來源清單與核心命題索引 | 👉 **開啟 [`./mode1_article_socratic_protocol.md`](./mode1_article_socratic_protocol.md)**<br>以**「道（底層統計與認知哲學）・法（系統治理與雙腦架構）・術（非對稱試點與工具落地）」**三層框架進行跨文獻結構映射與五步收斂。 |

---

## 二、 每輪對話後即時持久化與跨裝置中繼同步 (`01_phase1_socratic_log.md`)

- 在每輪互動後，同步更新 `reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md`（純粹記錄 Phase 1 本文思辨、數據故事探索或分配圖形逐步導學軌跡；**嚴禁混雜系統靈感，亦無需寫入 Phase 2 生成規格或附掛 `02_phase2_generation_blueprint.md` 連結**）。
- 若為「Medium 每週一圖／輕量數據敘事專欄」任務，該 `01_phase1_socratic_log.md` 將作為獨立自洽的 Phase 1 思辨紀錄供課堂作業 `{AI 對話 2}` 單檔連結檢視，因此**必須完整、詳實記錄從「三層分流驗算 $\rightarrow$ 廣角候選切角選單（或 Track A/C 驗證）$\rightarrow$ 互動問答推演 $\rightarrow$ 製圖 6 條件預填與消歧拍板 $\rightarrow$ 單一故事線收斂」的全過程**（Phase 2 三層生成藍圖則獨立存於同目錄 `02_phase2_generation_blueprint.md`，無需於 `01` 內附連結）。
- 若使用者要求「先同步到 Git／我要換裝置」，更新 `01_phase1_socratic_log.md` 後立即執行 `git add -A && git commit -m "wip(phase1): checkpoint at Step X" && git push origin main`。

```markdown
# 【第一階段思辨與數據探索紀錄】<文章或數據專案主題名稱>
- **建立時間**：YYYY-MM-DD | **原文／資料說明書路徑**：`./00_source_article.md` | **原始數據路徑**：`./data/<原檔名>.csv`（若適用） | **狀態**：進行中 / 已完成
- **輸入模式**：模式 1 (單篇文獻) / 模式 2 (CSV＋資料說明書數據敘事＆分配導學) / 模式 3 (多檔案診斷包) / 模式 4 (跨篇統整)
- **前序 Gemini 網頁版《資料說明書》對話分享連結（AI 對話 1，若適用）**：`https://g.co/gemini/share/...`

## 1. 問題意識錨點 / 數據三層互斥分流與純明細統計基準 (Step 0 / Read & Analyze Loop)
- **核心挑戰之傳統認知（模式 1）或 三層互斥分流驗算（模式 2：`df_detail` + `df_other` + `df_subtotal` == `df_raw`）**：...
- **純明細 `df_detail` 真實極值（Min/Max）、中位數與偏態亮點、證據標籤（🟢官方已說明/檔案觀察 vs. 🟡推論待確認/前處理血統預警）**：...

## 2. 使用者先備直覺 / 漏斗式數據敘事起手式 (Step 1 & 2 / Discuss Loop - Track A, B or C)
- **使用者初始切角（Track A）、AI 廣角數據雷達候選切角選單（Track B）或 10 大分配圖形逐步導學進度（Track C）**：...
- **使用者挑選之切角與觀點 / 理論與數據結構對齊**：...

## 3. 蘇格拉底式雙維度詰問 / 數據故事深挖與製圖 6 條件全預填確認表 (Step 3 / Pre-Chart Gate)
- **第一輪 & 第二輪互動推演軌跡（因果深挖 × 說明書第 6 章生態謬誤、三層指標消歧與外推邊界把關）**：...
- **製圖前 6 大條件全預填確認表（含發散中心 `#F5F6F7` 與原表 `df_other` vs. `4+1` `#CBD5E1` 長尾消歧決策）**：...

## 4. 跨領域類比編碼與抽象系統基模 (Step 4 — Medium 每週一圖模式與純分配導學模式豁免此步)
- **抽離之底層抽象基模 / 公式與跨領域正反案例**：...

## 5. 最終確認之知識架構或單一數據故事線收斂 (Step 5 Exit Consensus)
- **【文獻／深度報告模式 — 零刪減雙群組架構】**：(a) 核心論證主幹分支（3~4 個） + (b) 批判延伸與跨域遷移分支（1~4+ 個，零刪減）。
- **【Medium 每週一圖模式 — 單一故事線漏斗收斂（Single-Hook Convergence）】**：
  1. **核心數據故事主軸（Single Hook）**：...
  2. **1～2 張獨立單面板統計圖敘事分工**：圖 1（主色破題）`01_chart_hook.png` + 圖 2（次色深挖，選配）`02_chart_drilldown.png`。
  3. **`<= 1,600` 字專欄報導大綱（含第 6 章 1 項核心外推邊界反思，以及官方參考資料來源確認［僅附：1.官方資料集網址、2.資料涵蓋期間］）**：...
```
