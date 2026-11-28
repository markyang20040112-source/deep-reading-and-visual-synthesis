# Format A 內容細節規劃（視覺化知識圖譜與拓撲選型大腦）

> **單一職責定位（Single Responsibility）**：本檔為 **Format A（獨立全景視覺化知識圖譜 `.png`）** 分枝的內容細節決策大腦，**僅當主幹 [`../../shared/router.md`](../../shared/router.md) 確定勾選 Format A 時按需開啟**。專責協助使用者規劃「零刪減多圖分流配置」、「T1～T5 網格拓撲結構選型」與「本分枝局部覆寫（設計模式／筆風／主題色票）」，拍板後寫入 `02_phase2_generation_blueprint.md` 的 **`## Format A 分枝藍圖`**，交由 [`02_build.md`](./02_build.md) ＋ [`03_qa.md`](./03_qa.md) 執行（Subagent 隔離或單執行緒備援）。
> - **邊界提醒**：若專案僅需於 PDF 報告中嵌入輕量流程簡圖，無須選擇 Format A（Format B 內建 `7.44"` A4 直向簡圖 API 自給自足）。

---

## 一、 第一步：無損分圖擴展診斷（Zero-Loss Multi-Canvas Diagnosis）

開啟本檔後，先盤點 `01_phase1_socratic_log.md` 第五節收斂出的所有分支總數，嚴守 **單張畫布 $4 \to 2 \to 3$ 組塊上限（3～4 個宏觀容器、卡片內文 `16.0~16.5pt`）** 與 **A2 零刪減鐵律**：
- **若總分支 $\le 4$ 個**：規劃 1 張全域主幹圖（`01_article_master_structure_map.png`），或視機制複雜度加開 1 張機制深挖圖。
- **若總分支 $> 4$ 個（含 `(a) 核心論證主幹` ＋ `(b) 批判延伸與跨域遷移`）**：強制啟動無損多圖分流：
  1. **`01` 全篇內容架構主圖**：100% 承載核心論證主幹（背景痛點 $\rightarrow$ 核心診斷 $\rightarrow$ 關鍵支柱 $\rightarrow$ 治理結論）。
  2. **`02` 核心機制／系統架構深挖圖**：聚焦文中最高價值的單一工程機制、雙腦協同或轉型路線進行結構解剖。
  3. **`03+` 批判邊界與跨域遷移專題圖**：獨立完整承載 Phase 1 Step 3（隱含假設失效邊界、反例壓力測試、組織阻力）與 Step 4（跨領域同構類比遷移），**絕不刪減或壓縮任何延伸思辨**。

---

## 二、 第二步：五大瑞士網格拓撲選型診斷矩陣（T1～T5 Diagnostic Advisor）

依每張圖預計承載的**「知識內在邏輯結構」**，查表診斷出**首選拓撲 ＋ 推薦理由 ＋ 備選拓撲**：

| 拓撲代號與名稱 | 觸發之知識邏輯特徵（何時首選） | 推薦理由與認知適配優勢 | 備選轉換拓撲 | 對應黑盒組件（`generate_mindmap.py`） |
| :--- | :--- | :--- | :--- | :--- |
| **T1：焦點問題層級概念圖**<br>*(Top-Down Concept Map)* | 單一核心理論／第一性原理向下推導出 3～4 條實證或處方支柱 | 由上而下形成明確演繹階梯，頂層樞紐鎖定焦點問題、中層機制、底層處方與跨分支虛線關聯一目了然 | 若演繹具嚴格時序步驟 $\rightarrow$ 轉 **T2**；若需強調兩極張力 $\rightarrow$ 轉 **T5** | `draw_spine_hub_module` ＋ `draw_modern_card` ＋ `draw_labeled_bezier` |
| **T2：三欄雙腦／演進管線圖**<br>*(3-Column Pipeline / 3×3 Wiring)* | 明確的「輸入 $\rightarrow$ 處理/機制 $\rightarrow$ 產出」三階段管線，或三層並行協同系統 | 以 Palmer 共同區域框起三欄 3×3 矩陣，橫向呈現轉化流向、縱向呈現分層組件，最適合工程與治理流程 | 若步驟間有強烈正負增強反饋 $\rightarrow$ 轉 **T3** | `draw_3x3_pipeline_grid` |
| **T3：系統動力學雙迴路圖**<br>*(System Dynamics Loop)* | 存在自我強化（`+ 增強`）或制衡調節（`- 調節`）的正負回饋閉環與多方生態互動 | 中央雙向弧形迴路直接揭示「為什麼系統會自我加速或陷入死結」，兩側容器承載外部輸入與治理槓桿 | 若因果主要是單向對立而非循環 $\rightarrow$ 轉 **T4** | `draw_feedback_loop_pair` ＋ `draw_macro_zone` |
| **T4：對照矩陣與雙欄架構**<br>*(Comparative / 2×2 Matrix)* | 二元典範轉移（舊迷思 vs. 新破局）、雙維評估象限（風險 × 報酬）或反例邊界測試 | 左警示／右破局雙欄並立，或正交十字四象限鎖定目標象限，最能創造強烈對比與批判張力 | 若需整合為全篇四段式總覽 $\rightarrow$ 轉 **T5** | `draw_2x2_matrix_quadrants` ＋ `draw_labeled_arrow` |
| **T5：瑞士網格全高主軸分叉圖**<br>*(Swiss Full-Spine & 4-Trunk Fork)* | 完整長文或實證報告之全域總覽（現象 $\rightarrow$ 病因 $\rightarrow$ 解法 $\rightarrow$ 行動四段並進） | 中央垂直脊椎從上貫穿至下，拉出 4 條主幹並 $1 \to 2$ 分叉連向 8 張細節卡，兼具骨架順序與細節飽滿度 | 若分支偏向純階層演繹 $\rightarrow$ 轉 **T1** | `draw_spine_hub_module` ＋ `draw_hierarchical_trunk_fork` |

---

## 三、 第三步：本分枝混合式局部覆寫與提案確認

向使用者提出 **Format A 分枝骨架提案**，並同時確認是否針對本格式覆寫主幹預設（見 [`../../shared/style_and_color_core.md`](../../shared/style_and_color_core.md)）：
- **設計模式覆寫（可選）**：承襲主幹，或單獨為知識圖譜開啟 **模式 2 編輯室 80/20 聚光燈＋瓶頸膠囊**（[`../../shared/editorial_narrative_spec.md`](../../shared/editorial_narrative_spec.md)），或 **模式 3 冰山／階梯漏斗／雙向天平空間隱喻**（[`../../shared/creative_armory/INDEX.md`](../../shared/creative_armory/INDEX.md)）。
- **筆風與主題色票覆寫（可選）**：承襲主幹，或為 Format A 單獨指定筆風檔（`Slot 1, 4, 5, 8`）與 `generate_mindmap.THEMES` 佈景主題（如 `swiss_editorial` / `modern_academic_slate` / `warm_editorial_ivory`）。

> **📌 Format A 分枝提案標準輸出結構**：
> - **圖 1（`01_...png`）**：承載分支 `[...]` $\rightarrow$ **首選推薦拓撲 `[T?]`**（理由：...）／**備選：`[T?]`**
> - **圖 2+（`02_...png`）**：承載分支 `[...]` $\rightarrow$ **首選推薦拓撲 `[T?]`**（理由：...）／**備選：`[T?]`**
> - **分枝覆寫建議**：`承襲主幹` 或 `<具體模式／筆風／主題覆寫建議>`

**⏸️ 暫停關卡**：等待使用者確認 Format A 分枝規劃後，立即寫入 `02_phase2_generation_blueprint.md` 之 **`## Format A 分枝藍圖`**；輪到 Format A 執行時，依 [`02_build.md`](./02_build.md) 生成並依 [`03_qa.md`](./03_qa.md) 驗收。
