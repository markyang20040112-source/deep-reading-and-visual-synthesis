# 特化格式 D：統計數據視覺化與量化科學圖表規範 (Quantitative Chart Spec)

在第二階段若文本觸發【量化數據、實驗對照、數值分佈或相關關係】之情境，必須依據 **Mackinlay (1986) 表達力與有效性準則**、**Cleveland & McGill (1984) 圖形知覺階層**、**Few (2012) 數據關係分類** 與 **Knaflic (2015) 數據敘事聚光燈原則**，生成高資料墨水比之出版級科學圖表。

---

## 一、 Mackinlay 表達力與有效性鐵律 (Expressiveness & Effectiveness)

1. **表達力準則（Expressiveness Filter）`[Mackinlay 1986]`**：
   - **Encode all facts and ONLY the facts**：圖表必須精確表達資料本身，**嚴禁暗示不存在的數學關係**。
   - *違規禁令 1*：絕對禁止使用折線圖連接「無自然連續順序之離散類別」（折線會誤導讀者以為中間存在連續插值）。
   - *違規禁令 2*：絕對禁止使用 3D 立體圖（3D 角度會扭曲二維長度與面積比例）。
   - *違規禁令 3*：絕對禁止在長條圖截斷 Y 軸起點（Y 軸起點非零會誇大真實差距）。
   - *違規禁令 4（Tufte 謊言因子與統一尺度鐵律 `[Tufte 1983]`）*：**嚴禁在並排多子圖（Subplots）中各自縮放相同單位的座標軸**！若兩子圖皆為百分比（%），其座標軸上限與刻度步長必須強制完全相等（如皆為 `xlim(0, 100)`），確保視覺長度比完全等於數據比（$0.95 \le \text{Lie Factor} \le 1.05$），100% 杜絕「實體長度相同但數值懸殊」的視覺欺騙。
2. **有效性排序（Effectiveness Ranking）`[Cleveland & McGill 1984]`**：
   - 人眼解碼精確度最高者為**「共同基準線上的位置與長度」**；最低者為角度、面積與彩度。
   - 類別數值比較一律優先採用**水平長條圖（Horizontal Bar Chart）**，而非圓餅圖。

---

## 二、 Zelazny, Few & Knaflic 六大數據敘事圖表選型 (6 Core Quantitative Visual Forms)

| 數據關係類型 | 適用情境與文章特徵 | 唯一推薦圖表類型 | 繪圖幾何與直接標註 (Direct Labeling) 規範 |
| :--- | :--- | :--- | :--- |
| **1. 項目比較與排名 (Item Ranking)** | 各項驅動因素之提升潛力（Lift）、各 AI 工具滲透率（%） | **水平排序長條圖 (Horizontal Bar Chart)** | 由大到小降序排列；數值與類別名稱直接標註於長條右側（消除獨立圖例）。 |
| **2. 預期 vs. 現實斷崖 (Expectation vs. Reality Cascade) `[Knaflic 2015]`** | 80% 熱潮期望 $\rightarrow$ 6% 生產落地、漏斗流失、計畫 vs. 實際 | **階梯漏斗對比圖 (Funnel / Slope Cascade)** | 單一基準線水平串聯「期望 $\rightarrow$ 瓶頸 $\rightarrow$ 現實」因果鏈，色彩聚光燈直擊斷崖落差。 |
| **3. 實驗組 vs. 對照組函數曲線 (Diverging Response Curves)** | 隨機盲測 vs. AI 語境混淆之需求曲線、敏感度分析 | **雙曲線座標對比圖 (Paired Coordinate Curves)** | 包含清晰座標軸標籤、真人向下傾斜曲線 vs. AI 平坦曲線，末端直接標註文字標籤。 |
| **3. 構成與份額拆解 (Part-to-Whole / Flow)** | 預算配置、從毛利到淨利的階段性貢獻與流失 | **瀑布圖 (Waterfall Chart) 或堆疊長條圖** | 起點與終點為實色基準柱，中間增減項採雙極色（綠增/紅減），底部保留微弱連結線。 |
| **4. 雙變數相關與迴歸 (Correlation & Scatter)** | 滿意度 × 權重、測試價格 $X$ × 購買意願 $Y$ | **散布圖 ＋ 線性迴歸擬合線 (Scatter & Trendline)** | 數據點使用高透明度散點防重疊（Alpha=0.6），加繪統計迴歸線與信賴區間帶。 |
| **5. 頻率與分布變異 (Distribution & Variance)** | AI 生成回答變異過小、評分分布偏態 | **箱形圖 (Box Plot) 或核密度曲線 (KDE)** | 標註中位數、四分位距（IQR）與極端離群值點。 |

---

## 三、 Tufte 高資料墨水比與美學細節 (Tufte Data-Ink & Decluttering)

1. **消除一切圖表雜訊（Zero Chartjunk `[Tufte 1983]`）**：
   - 移除外圍邊框矩形（`ax.spines['top'].set_visible(False)`, `ax.spines['right'].set_visible(False)`）。
   - 座標軸刻度線維持細灰線（`#CBD5E1`, `lw=0.8`），僅保留單一方向的微弱水平參考虛線（`alpha=0.4`）。
2. **直接標註原則（Direct Labeling `[Knaflic 2015]`）**：
   - **全面消滅獨立圖例（Legend Box）**！數值、百分比與類別名稱必須就近標記在長條或折線末端，杜絕眼動來回搜尋。
3. **文字工學與字級硬性限制**：
   - 圖表標題（Action Headline）：`12.5pt ~ 14pt Bold`。
   - 座標軸與數據標籤：`9.5pt ~ 11pt Regular`（保證簡報免放大鏡即可清晰辨識）。
   - 字體統一使用 `Microsoft JhengHei`（Windows）或系統標準無襯線中文字體。

---

## 四、 跨媒介嵌合工學 (Cross-Media Embed Geometry)

### A. 在簡報 PPT (16:9 橫向) 中的嵌合規範：
- **版型適配**：
  1. **左圖右文（45%:55% 分割）**：左側放置長寬比 $1.33:1 \sim 1.5:1$ 之圖表（寬 `5.5"`，高 `4.8"`），右側放置 2~3 張平行對齊之論點卡片。
  2. **上公式下圖表（因果對照）**：上方配置因果公式盒，下方並排呈現雙對照曲線圖（如盲測對照）。
- **底色融合**：圖表輸出時背景色必須嚴格與 PPT 畫布底色一致（`#F8FAFC`），或輸出為帶 Alpha 的透明底 PNG，確保無白底補丁感。

### B. 在報告 PDF (A4 直向) 中的嵌合規範：
- **欄寬對齊**：單欄展示時寬度鎖定 `100%`（長寬比約 $1.8:1 \sim 2.2:1$ 扁平型）；雙欄並排時寬度鎖定 `48%`。
- **圖文包覆與三層解剖**：圖表上方必備「圖表編號與動作標題」，下方必備「資料來源與統計意義註釋（Context Footnote）」，與段落維持 $8\text{pt}$ 呼吸留白。
