# 第二層結構顧問（Format D & E）：30+ 圖表智慧診斷選型與儀表板架構大腦

> **單一職責定位（Single Responsibility）**：本檔為 Phase 2 **第二層（Layer 2）圖表與儀表板選型顧問大腦**，**僅當第一層確定包含 Format D（統計圖表）或 Format E（數據儀表板）時按需開啟**。融合 Google AI Mode、FineReport、FineBI、Tableau、Quire、RE:LAB 8 大指南與資料八實戰經驗，協助使用者從 **5 大圖表家族、30+ 種出版級圖型** 中診斷出最貼合數據結構與故事張力的圖表組合與推進節奏，拍板後再進入第三層（設計光譜武器庫／筆風／配色）定裝。

---

## 一、 資料結構四維快篩診斷（4D Data Profiling before Chart Selection）

向使用者推薦任何圖表前，先根據 Phase 1 分析結果（或 `load_and_split_csv()` 對純明細 `df_detail` 的掃描結果）完成以下四維診斷：
1. **實體／類別規模 $N$ 與母體分流**：是否已剔除合計列 `df_subtotal` 與妥善消歧原表 `df_other`？實體數落在 $N \le 5$、$6 \sim 15$、$16 \sim 30+$，還是大樣本連續觀測點 $N > 500$？
2. **數值尺度與基準落差**：數值是否從 `0` 起算？還是集中於**非零高檔狹窄區間**（如消費支出介於 `59.2～117.0 萬`）？是否存在「未加權平均 vs. 官方加權平均」或「平均數 vs. 中位數」顯著偏態差距？
3. **時間維度 $T$**：橫斷面單期（$T=1$）、前後兩點排名／數值變化（$T=2$）、多期連續軌跡（$T \ge 3$），或起訖時間區間（Duration / Range）？
4. **分組數 $G$ 與雙維規模權重**：對比群組數為何（$G=1$、$2$、$3\sim8$、$8\sim30+$）？檢視內部結構百分比時，各實體之間的**母體總規模差距**是否同樣重要？

---

## 二、 「8 大溝通意圖 × 資料維度結構」雙層選圖決策樹（30+ 圖庫）

> **顧問原則（形式追隨功能，Form Follows Function）**：絕不套用「最簡圖表萬能論」！針對每項擬呈現的數據命題，從下表診斷出 **「首選推薦圖表 ＋ 為什麼最適合 ＋ 備選對照圖表 ＋ 選圖禁忌提醒」**，並記下對應的**終端圖表家族檔案**（於第三層拍板後才按需開啟）。

| 溝通意圖與細分資料條件 | 首選推薦圖表（對應黑盒函數） | 顧問診斷理由（為何此圖最適合） | 備選對照圖表與防誤導禁忌提醒 | 終端圖表家族規格檔 |
| :--- | :--- | :--- | :--- | :--- |
| **1. 比較高低與排名**<br>*(Comparison & Ranking)*<br>• 單純比大小（從 `0` 起算，$N \le 12$）<br>• **非零高檔狹窄區間**（如 `59~117萬`, $N=10\sim30$）<br>• 雙群體對稱結構（男/女、城/鄉年齡層）<br>• 80/20 關鍵少數貢獻集中度 | • **直立柱狀／橫向排行長條圖**<br>• **編輯室克里夫蘭點陣圖**（`plot_cleveland_dot` + `add_badge_vline`）<br>• **雙向對稱蝴蝶金字塔圖**<br>• **柏拉圖（Pareto Chart）** | • 實心長條長度忠實反映 `0` 起算倍數關係<br>• 點陣圖靠「位置」而非長度編碼，可合法聚焦非零真實變異區間，並同屏釘上多重統計基準膠囊<br>• 柏拉圖結合降冪柱與累積線，一圖找出 80% 關鍵少數 | • **備選**：棒棒糖排行圖（Lollipop）<br>• **【禁忌】**：實心長條／柱狀圖之數值軸**絕對禁止截斷非零起點**！非零區間請改用克里夫蘭點陣圖 | [`chart_family1_ranking_and_deviation.md`](../chart_family1_ranking_and_deviation.md) |
| **2. 目標偏差與雙態跨距**<br>*(Deviation & Span)*<br>• 實際表現 vs. 目標線＋表現等級帶<br>• 前後兩期或兩群體間之跨距變化<br>• 相對中心基準之正負增減偏離 | • **標靶圖／子彈圖（Bullet Chart）**（`plot_bullet`）<br>• **啞鈴跨距圖（Dumbbell Plot）**（`plot_dumbbell`）<br>• **雙向正負發散長條圖（Diverging Bar）** | • 子彈圖在單一橫條內高密度編碼「實績＋目標線＋好/中/差背景帶」，完勝低效圓形儀表盤（Gauge）<br>• 啞鈴圖極度清晰地對比同一實體的起點、終點與淨差距 $\Delta$ | • **備選**：範圍條形圖（Range Bar）<br>• **【禁忌】**：發散圖嚴禁簡化為非黑即白雙色，必須對稱映射至 9 階發散色階中心 `#F5F6F7` | [`chart_family1_ranking_and_deviation.md`](../chart_family1_ranking_and_deviation.md) |
| **3. 時序趨勢、斷崖與洗牌**<br>*(Trend, Cliff & Trajectory)*<br>• 跨階段留存遞減／漏斗崩跌<br>• 多期長時序＋歷史事件／口徑變更<br>• **僅前後 2 期（$T=2$）**排名洗牌與斜率<br>• 同案內雙對立指標反差（預期 vs. 實際）<br>• 累積趨勢或時間排程區間 | • **空間重力斷崖折線＋直柱複合圖**<br>• **時期色帶＋事件標註折線圖**（`add_regime_shading_and_events`）<br>• **坡度圖／斜坡圖（Slope Chart）**（`plot_slope_chart`）<br>• **配對雙柱＋剪刀差標註圖**<br>• **堆疊面積圖 / 甘特圖（Gantt）** | • 將推進階段置於 X 軸、百分比置於 Y 軸，製造直覺物理斷崖感<br>• 時期色帶＋引線方框可解釋轉折點背後法規或統計定義變更，防止誤判趨勢<br>• 兩期對比用斜坡圖可一眼看清交叉洗牌與上升/下降斜率 | • **【禁忌 1】**：跨階段複合圖強制執行「指標極性 100% 同質化（`100% - 反向率`）」<br>• **【禁忌 2】**：同案雙維反差嚴禁用單一折線<br>• **【禁忌 3】**：折線圖 X 軸時間間隔必須保持一致 | [`chart_family2_trend_and_comparison.md`](../chart_family2_trend_and_comparison.md)<br>*(斜坡圖見 `chart_family1`)* |
| **4. 整體組成、雙維佔比與瀑布**<br>*(Part-to-Whole & Waterfall)*<br>• 單時點佔比（類別 **$\le 5$ 項**）<br>• **各組母體規模 × 內部結構佔比**<br>• 期初 $\rightarrow$ 各項正負增減 $\rightarrow$ 期末 | • **環形圖（Donut）**（中心置總數）或 **`4+1` 堆疊長條**<br>• **馬賽克雙維度佔比圖（Marimekko）**（`plot_marimekko`）<br>• **增減橋樑瀑布圖（Waterfall）**（`plot_waterfall`） | • 馬賽克圖以 X 軸寬度編碼總規模、Y 軸編碼 0–100% 結構，破解一般 100% 堆疊圖「大小市場等寬」的失真盲點<br>• 瀑布圖精準追蹤每一項正負增減對最終總額的貢獻 | • **【禁忌 1】**：圓餅／環形圖超過 5 類強制轉用 `4+1` 長條或樹狀圖<br>• **【禁忌 2】**：多於 4 類且原表含「其他」列時，強制執行 `df_other` 雙重語義消歧 | [`chart_family3_composition_and_flow.md`](../chart_family3_composition_and_flow.md) |
| **5. 多層階層佔比關係**<br>*(Hierarchy)*<br>• 多類別、多層級之面積佔比<br>• 主類少（$\le 4$）且含二階／多階細分 | • **矩形樹狀圖（Treemap）**<br>• **巢狀環形圖（Nested Donut）** 或 **旭日圖（Sunburst）** | • 樹狀圖善用矩形空間呈現數十個階層節點的相對規模<br>• 巢狀環／旭日圖清晰展現內環主類與外環次類之從屬關係 | • **備選**：圓堆圖（Circle Packing）<br>• **【禁忌】**：面積是長度的平方，嚴禁用半徑或邊長線性對應數值 | [`chart_family3_composition_and_flow.md`](../chart_family3_composition_and_flow.md) |
| **6. 動態流量與路徑移轉**<br>*(Movement & Flow)* | • **桑基流向圖（Sankey Diagram）** | • 直觀追蹤資源、預算、人口或流量從起點節點分流至各終點的粗細與損耗 | • **備選**：弦圖（Chord Diagram，適合雙向對稱互流矩陣） | [`chart_family3_composition_and_flow.md`](../chart_family3_composition_and_flow.md) |
| **7. 連續分布、多峰與跨組密度**<br>*(Distribution & Density)*<br>• 單變數計數與門檻 ($G=1$)<br>• 連續密度／分位／常態診斷 ($G=1\sim6$)<br>• 多群組比較 ($G=3\sim8$ vs. $8\sim30+$)<br>• 雙連續大樣本 ($N>500$)<br>• 跨組／跨期／跨成分防欺騙對照 | • **直方圖**（`add_halo_vline`＋`annotate_floor_extreme`）<br>• **非負截斷 KDE**（`plot_clipped_kde`）<br>• **ECDF** ／ **常態 Q-Q 圖**<br>• **小提琴圖** ($G=3\sim8$) ／ **山脊圖** ($G=8\sim20$) ／ **箱形圖** ($G \ge 8$)<br>• **2D 直方圖 ／ 2D KDE 等高線**<br>• **背景基準疊加分面圖（Context Overlay）**（`setup_context_overlay_grid`） | • 直方圖守住非負與小樣本誠實度；截斷 KDE 消除分箱偏誤並守住面積 $=1$<br>• 小提琴／山脊圖揭露箱形圖看不見的雙峰結構<br>• Context Overlay 以淡灰固定基準背景＋鎖死全面板座標軸破解跨組比較視覺錯覺 | • **【禁忌 1】**：嚴禁以連直方圖頂端之樣條平滑線（次數多邊圖）冒充 KDE<br>• **【禁忌 2】**：非負變數強制 `x_min=0` 截斷；嚴禁將村里總額當成個人貧富差距（生態謬誤） | [`../distribution_and_density_chart_spec.md`](../distribution_and_density_chart_spec.md) |
| **8. 多維關聯、熱區與空間複合**<br>*(Multivariate & Spatial)*<br>• 雙變數＋規模＋四象限策略<br>• 雙維交叉精確數值＋色階熱區<br>• 多項指標綜合輪廓（$\le 3$ 組）<br>• 地理／區域＋補充排行視角 | • **波士頓四象限散點／氣泡矩陣**<br>• **突出顯示熱力表（Highlight Table）**<br>• **雷達圖（Radar Chart）**<br>• **主圖＋角落微型排行副卡**（`add_inset_leaderboard`） | • 四象限氣泡同步呈現相關性、第三維度規模與象限歸屬<br>• 熱力表同時保留精確數字閱讀與視覺熱區掃描<br>• 主圖＋角落副卡一屏回答「分布在哪」與「誰排前三」 | • **【禁忌 1】**：氣泡**半徑必須正比於 $\sqrt{\text{Value}}$**（即散點面積參數 `s` 線性對應數值）<br>• **【禁忌 2】**：雷達圖禁止超過 3 組重疊，否則變蜘蛛網亂麻 | [`../chart_family5_multivariate_and_spatial.md`](../chart_family5_multivariate_and_spatial.md) |

---

## 三、 若含 Format E（數據儀表板）：動態呈現架構診斷

若第一層有勾選 **Format E**，除上述內部圖表選型外，須同時決定儀表板整體骨架（**嚴禁寫死固定四圖頁籤**）：
1. **呈現模式 A：多視角切換互動工作台（Multi-Perspective Workbench）** $\rightarrow$ 頂部維度篩選列 ＋ 3～4 張 KPI 摘要卡 ＋ 動態分頁視角 ＋ 可搜尋與匯出 CSV 之明細表。
2. **呈現模式 B：多面板全景聯動網格（Synchronized Bento Grid）** $\rightarrow$ 不對稱寬主圖（55～60%）＋ 右側互補副面板，同屏比對全局結構與局部排行。
3. **呈現模式 C：雙模態協同交付** $\rightarrow$ 零後端獨立 Git-Ready 網頁儀表板 ＋ 一張 `300 DPI` 靜態全景儀表板圖（`.png`）。

---

## 四、 第二層顧問提案標準輸出與暫停關卡

向使用者提出 **Format D / E 第二層選型提案** 時，必須完整列出：
1. **【製圖前 6 大條件預填摘要表】**（直接由《資料說明書》與 `df_detail` 自動帶入：實際欄位與枚舉映射、單位、純明細 `df_detail` 真實 `Min/Max` vs. 全檔 `Min/Max`、極性同質性、合法缺失值 `NA` `#D9D9D9` 筆數、前處理血統／`df_other` 消歧方案）。
2. **【每張圖表之診斷提案】**：
   - 清楚寫出：**「圖 X（檔名）：首選推薦圖型 ＋ 基於本次資料特徵（$N, T, G$）的診斷理由 ＋ 備選方案 ＋ 可搭配之第三層設計方向預告（如適合開啟資料八雙基準膠囊點陣，或適合開啟 RE:LAB 高光液面容器等）」**。
3. **【推進節奏確認】**：**一次批次生成（`batch_generation`）** vs. **逐步導學互動模式（`step_by_step_tutor`：一次一張圖＋五步解說）**。

**⏸️ 暫停關卡**：等待使用者確認 Format D / E（及同期選定的其他格式）第二層圖表組合、製圖條件與推進節奏後，立即將圖表選型、討論取捨理由與 `df_other` 消歧決策寫入 `02_phase2_generation_blueprint.md` 第 2 節，隨即讀取 **[`layer3_advisor_design_style_color.md`](layer3_advisor_design_style_color.md)** 進入最後一層（第三層）全域定裝！
