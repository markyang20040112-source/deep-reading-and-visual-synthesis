# 第二階段：科學化視覺統整與模組化輸出總控台 (Phase 2 Router)

> [!CAUTION]
> **全方位靈感暫存與防私改鐵律**：在生成與微調成果期間，若使用者或 AI 產生**任何有關本技能的優化靈感（不限於功能或視覺設計，亦包含技能 `.md` 檔案本身的寫法、格式編排、目錄結構或 Token 讀取效率等一切層面）**，**當下僅寫入獨立暫存檔 `reading_sessions/_pending_skill_inspirations.md`**，等下方 Step 3 成果正式交付完畢後，才於 Step 4 啟動「技能實證進化與清理流程」，**絕對禁止私自在背後偷改技能檔案**！

---

## 一、 啟動條件與輸入準備
1. **標準交接模式**：第一階段已完成 Step 5 收斂，直接讀取 `reading_sessions/<YYYYMMDD_主題簡稱>/01_phase1_socratic_log.md`，**並優先檢視頂部「使用者輸出格式偏好與排除項」**（凡使用者曾表示不需生成某格式，嚴禁擅自生成）。
2. **顯式跳關快速通道（Fast-Track Override）**：當使用者**明確要求跳過引導直接生成**時，先將原文存入 `00_source_article.md`，由 AI 自行提煉 3～5 個核心知識分支簡要寫入 `01_phase1_socratic_log.md`，隨即依下方流程產出檔案。

---

## 二、 按需載入與閉環進化四步驟（嚴禁一次載入所有格式規範）

1. **Step 1（必讀共通規範）**：先讀取 **[visual_cognition_principles.md](./visual_cognition_principles.md)**，依文章屬性選擇 4 套科學主題色板之一（`Swiss Editorial` / `McKinsey Executive` / `Nature Academic` / `Warm Humanist`）。
2. **Step 2（擇一讀取指定格式規範，嚴守跨媒介圖表分流鐵律 `[ISO 9241 & Shneiderman 1996]`）**：

| 使用者指定格式 | 唯一應開啟之特化規範檔 | 核心產出動作 |
| :--- | :--- | :--- |
| **格式 A：知識圖譜 / 概念圖**<br>*(.jpg / .png)* | **[visual_diagram_matplotlib_spec.md](./visual_diagram_matplotlib_spec.md)**<br>＋ 參考 [generate_mindmap.py](../scripts/generate_mindmap.py) | • **Ausubel-Sweller 分圖鐵律**：若內容涵蓋原文脈絡、深度方法論思辨與跨篇整合，強制拆分為多張獨立圖譜，且**第 1 張必為「本篇文章整體內容架構主圖（Article Master Structure Map）」**。<br>• 以 `matplotlib` 動態換算卡片像素行寬（填滿 `88%~92%` 寬度，零右側留白），生成後用 `read_file` 驗收。 |
| **格式 B：深度報告 / 讀書筆記**<br>*(.md / .docx / .pdf)* | **[document_report_spec.md](./document_report_spec.md)** | • 選配 `B1`～`B4` 體裁，執行 W3C CSS 章節連續性鎖定（防止標題孤立頁尾與異常空白）與峰終定律收束頁。<br>• **禁止將格式 A 的高密度小字心智圖 `.jpg` 縮小塞入 PDF**！報告內嵌圖表一律採用「免放大即可清晰閱讀的 HTML/SVG 原生大字級結構圖（字級 $\ge 10\text{pt}$）」或格式 D 之量化科學圖表。 |
| **格式 C：高階簡報 / 投影片**<br>*(.pptx / 簡報稿)* | **[presentation_slide_spec.md](./presentation_slide_spec.md)** | • 執行 Alley 斷言—證據三區架構、頂部導航防溢框、並排卡片「水平平行對齊網格（Parallel Row Alignment）」、舒適行距（`1.35x`）與峰終定律結束頁（Closing Slide）。<br>• **禁止在 PPT 內塞入字極小的心智圖 `.jpg`**，一律以原生大字向量圖表（$\ge 13.5\text{pt}$）或格式 D 量化圖表呈現。 |
| **格式 D：統計數據與量化科學圖表**<br>*(.png / 內嵌圖表)* | **[quantitative_chart_spec.md](./quantitative_chart_spec.md)** | • 依據 Mackinlay (1986) 表達力準則、Cleveland (1984) 圖形知覺階層與 Knaflic (2015) 數據敘事聚光燈原則，輸出高資料墨水比之水平長條圖、因果曲線對照圖、瀑布圖、散布圖等，嵌合至 PPT 或 PDF 中。 |

### 🧠 跨格式共用：動態三維視覺決策引擎 (Dynamic Tri-Axial Visual Decision Engine `[I-21]~[I-23]`)
在產出簡報與報告時，**嚴禁採用死板配額硬塞圖片，亦嚴禁偷懶全用純文字卡片**！系統必須依據以下三維向量動態決定是否繪圖與繪製何種圖表：
$$\text{Visual Layout} = f(\text{Data Structure}, \text{Storytelling Intent [聯動 HCL 色彩]}, \text{Context Pairing})$$
1. **維度一（資料形式）**：自動判斷數據特徵（連續函數曲線 vs. 離散類別大小 vs. 正交分類 vs. 系統迴路）。
2. **維度二（敘事目的與 HCL 色尺聯動）**：
   - 突出懸殊差距 $\implies$ 水平長條圖 ＋ Knaflic 80/20 灰藍底襯托單一焦點主色；
   - 機制對立/兩難 $\implies$ 發散雙極對稱曲線（冷藍 vs. 暖紅棕）；
   - 策略邊界/防線 $\implies$ 2×2 象限色塊圖（藍綠衝刺區 vs. 玫瑰紅禁區）；
   - 階段進程 $\implies$ Sequential 單調明度階梯；
   - 無圖表需求（純哲學/質化分析）$\implies$ 嚴守零冗餘原則，維持純淨文字，絕不硬塞圖片！
3. **維度三（情境搭配）**：
   - 搭配公式 $\implies$ 上公式、下圖表緊湊對稱；
   - 搭配論點 $\implies$ 45%:55% 左右分欄（左圖視覺證據，右側深度論證）；
   - PPT 橫向長寬比 $1.33:1 \sim 1.5:1$（字級 $\ge 11\text{pt}$）；PDF 直向精確對齊單欄/雙欄欄寬。

3. **Step 3（統一輸出、交付與 Git 同步）**：所有生成之圖片、Python 繪圖腳本、報告或簡報，一律儲存於 **`reading_sessions/<YYYYMMDD_主題簡稱>/02_outputs/`** 並向使用者交付；交付同時執行 `git add -A && git commit -m "docs(session): add reading session and outputs for <主題>" && git push origin main` 同步至 GitHub。
4. **Step 4（整套流程結束後：靈感運用與刪除閉環）**：
   - 成果交付完畢後，檢查 `reading_sessions/_pending_skill_inspirations.md` 是否存在（或 AI 自身對本次流程是否有反思靈感）。若有待處理靈感，依序執行：
     - **Step E1（提議與徵求同意）**：列出暫存靈感，詢問使用者是否同意檢索相關學術研究來升級技能（若使用者選擇不採用，**當下立即刪除該條靈感或暫存檔**）。
     - **Step E2（查證文獻與修改方案確認）**：獲同意後檢索權威文獻論證，向使用者回報「查證依據 ＋ 預計修改之檔案與具體規則」，請使用者確認。
     - **Step E3（寫入技能庫、刪除暫存檔並 Git 同步）**：獲使用者確認後，將文獻補入 `../THEORY_ARCHIVE.md`，將精煉規則更新至對應規範檔，**隨即立即刪除 `reading_sessions/_pending_skill_inspirations.md` 暫存檔**，並執行 `git add -A && git commit -m "feat(skill): <進化更新摘要>" && git push origin main` 推送至遠端倉庫！
