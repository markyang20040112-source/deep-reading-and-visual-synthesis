---
style_id: "<your_custom_style_id>"
style_name: "<筆風顯示名稱>"
owner_bound: null                       # 外部使用者自建筆風設為本機 Git 帳號或 null；嚴禁冒用原作者私人筆風
applicable_formats: ["A", "B", "C", "D", "E"]
linked_defaults:
  pdf_theme: "AI_ADAPTIVE"              # modern_sans | clreq_kaiti | AI_ADAPTIVE
  preferred_chart_mode: "AI_ADAPTIVE"   # editorial_storytelling | pure_dataviz | AI_ADAPTIVE
  allow_exclamation_mark: "AI_ADAPTIVE" # true | false | AI_ADAPTIVE
  terminology_format: "AI_ADAPTIVE"     # plain_first_bracket_term | term_first_bracket_en | direct_academic | AI_ADAPTIVE
---

# [筆風名稱] — 全生成場景文字與微文案控制契約（8 All-Scenario Control Slots Schema）

> **單一職責與 100% 全域穿透原則**：
> 本檔案為 `deep-reading-and-visual-synthesis` 的**公開空白筆風結構規範模板**。
> 筆風設定檔不只控制 Format B 報告正文，而是 **100% 穿透控制所有生成場景的每一個字詞與微文案**（含 Phase 1 對談導學、Format A 知識圖譜卡片與箭頭謂詞、Format B 報告散文與表格錨點、Format C 簡報斷言與講稿、Format D 統計圖表軸籤與標註氣泡、Format E 儀表板 UI 微文案與禁用詞護欄）。
>
> ### 三態參數機制（Tri-State Parameter Resolution）
> 每個插槽內的細項皆必須標記以下三種狀態之一：
> 1. **`[USER_LOCKED]`（使用者自訂鎖定）**：使用者已明確指定偏好（例如：「禁用驚嘆號」、「金額一律換算為億元」），AI 必須 100% 嚴格遵守，不得擅自更改。
> 2. **`[SCENARIO_PRESET]`（AI 情境預設）**：使用者初期僅指定大方向（如「學術報告」或「商業簡報」），由 AI 依該情境填入的推薦預設值。
> 3. **`[AI_ADAPTIVE]`（AI 動態適配／無想法時交由 AI 預設）**：當使用者對某個細項暫無想法、或希望保留彈性時，設為 `[AI_ADAPTIVE]`——AI 會在執行時根據本檔 **Slot 1 的核心主基調** 與 **當下文章／資料集的屬性** 自動推導最協調的寫法；且支援使用者在日常對話中隨時一句話局部熱修改並升級為 `[USER_LOCKED]`！

---

## Slot 1: `Core_Persona_And_Progression` (核心人設與認知推進邏輯)
- **寫作者人設與語氣冷熱度**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義寫作者身分定位、客觀中立度或敘事親和力>
- **三階資訊展開順序**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義從破題、推演到結論的展開順序，例如：現象直覺 → 機制情境 → 決策法則，或 研究問題 → 統計檢驗 → 實證發現與限制>

## Slot 2: `Interactive_Guidance_Tone` (Phase 1 蘇格拉底與逐步導學對談語氣)
- **提問與回饋口吻**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義 Phase 1 對話時的引導語氣、每次提問聚焦數量（如一次 1 題聚焦追問 vs. 雙維度詰問）與肯定回饋方式>
- **逐步導學解說結構**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義「一次一張圖逐步導學模式」下的標準解說骨架，例如：① 分析問題 → ② 資料篩選與計算方式 → ③ 座標軸與圖形元素讀法 → ④ 實際數據發現 → ⑤ 適用時機與解讀限制>

## Slot 3: `Prose_And_Narrative_Rhythm` (Format B 報告與專欄散文段落)
- **段落長度與長短句節奏**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義散文段落字數範圍、長短句交替節奏與手機/A4 閱讀呼吸感>
- **破題句式與轉折連接詞習慣**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義段落開頭習慣（如數據反差破題、問題意識破題或結論先行）與轉折詞偏好>
- **標點符號與粗體強調密度**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義是否允許驚嘆號、破折號與括號使用頻率，以及每段粗體重點句之密度上限>

## Slot 4: `Structured_Blocks_And_Captions` (表格、卡片、公式導讀與圖說)
- **條目開頭錨點格式 (`Anchor_Format`)**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義卡片與表格列點的開頭格式，例如：`● 【直覺白話動詞錨點】`、`● 【四字精確概念】`、或無括號直接陳述>
- **公式導讀與圖說 (`Caption`) 規範**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義數學/統計公式下方的導讀方式，以及 `<figure>` 圖說應包含的要素（如觀察重點、分析單位與限制）>

## Slot 5: `Knowledge_Diagram_Copy` (Format A 知識圖譜內部全部文字)
- **分區大標與卡片標題句型**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義宏觀容器（Macro Zone）與子卡片（Card）標題的句式與字數密度>
- **有向箭頭「謂詞膠囊 (`Predicate_Verbs`)」用詞風格**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義連接線膠囊內的動詞風格，如具象動作詞 vs. 嚴謹因果/統計關係詞>
- **底部 Takeaway 橫幅語氣**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義畫布底部全寬收斂橫幅的結語風格>

## Slot 6: `Chart_And_Dashboard_MicroCopy` (Format D & E 統計圖表與儀表板微文案)
- **圖表主、副標題句型公式**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義圖表頂部主標題（如結論斷言式 vs. 中立描述式＋指標口徑）與副標題（含樣本數 $n$、資料層級與單位）公式>
- **X/Y 座標軸籤與分類標籤用詞**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義座標軸標籤是否標明單位、是否採用雙層 `【四字定位】` 或原始分類名稱>
- **圖內標註氣泡 (`Callouts`)、基準線與網頁 Tooltip 解說語氣**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義圖內極值/中位數/平均數標註與網頁儀表板 KPI 卡、Tooltip 的文字口吻>

## Slot 7: `Slide_Headline_And_Speaker_Notes` (Format C 簡報標題與上台講稿)
- **Zone 1 斷言標題與 Zone 3 行動橫幅句型**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義投影片頂部 22～36 字斷言標題與底部 So-What 行動橫幅的語氣>
- **演講者備忘稿 (`Speaker_Notes`) 口語化口條**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義上台講稿的開場、轉場與口語說服節奏>

## Slot 8: `Notation_Terminology_And_Guardrails` (數值、單位、術語格式與禁用詞紅綠燈)
- **數值與單位換算規則**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義大額數值換算（如千元轉億元）、千分位逗號與小數點保留位數>
- **專有名詞與中英夾雜規則**：`[USER_LOCKED | SCENARIO_PRESET | AI_ADAPTIVE]` <定義首次出現專有名詞時的呈現格式>
- **🟢 偏好慣用詞白名單 (`Whitelist`)**：<列出鼓勵使用的精準動詞或過渡詞>
- **🔴 絕對禁用詞黑名單 (`Banned_Cliches`)**：<列出嚴禁出現的空洞套話、AI 罐頭詞或誇大超譯詞彙>
- **跨格式 Few-Shot 正反校準範例 (`❌ 違規 vs. ✅ 標準`)**：
  1. **【散文段落對照（Slot 3）】**：
     - ❌ 違規：`<填入不符合本筆風的寫法>`
     - ✅ 標準：`<填入符合本筆風的寫法>`
  2. **【卡片與表格條目對照（Slot 4 & 5）】**：
     - ❌ 違規：`<填入不符合本筆風的卡片條目>`
     - ✅ 標準：`<填入符合本筆風的卡片條目>`
  3. **【圖表標題與標註微文案對照（Slot 6）】**：
     - ❌ 違規：`<填入不符合本筆風的圖表標題或標註>`
     - ✅ 標準：`<填入符合本筆風的圖表標題或標註>`
