# 模式 2：編輯室權威敘事設計終端實作規範（Mode 2: Editorial Narrative Spec）

> **單一職責定位（Single Responsibility）**：本檔為 Phase 2 **模式 2（`editorial_narrative`，資料八／經濟學人／臺灣數據百閱編輯室敘事）專屬終端規格檔**，**僅當第三層（[`advisors/layer3_advisor_design_style_color.md`](advisors/layer3_advisor_design_style_color.md)）明確開啟模式 2 時才按需載入**（模式 1 完全不讀；純模式 3 具象／幾何隱喻可獨立執行而不強制載入本檔，除非使用者同時疊加編輯室標註或 PDF 社論組件）。
> - 若需開啟 **模式 3（`bespoke_metaphor` 開放式具象材質與幾何空間隱喻武器庫）**，請改讀 **[`creative_armory/INDEX.md`](creative_armory/INDEX.md)**。

---

## 一、 Format D ⇄ E 編輯室敘事圖表 5 大標竿技法與黑盒 API 契約

> **黑盒呼叫鐵律**：所有編輯室高階圖表元素皆已封裝於 [`../scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)，直接 `import` 呼叫並可於回傳之原生 Matplotlib 物件上自由微調（Zero Side-Effects）。

```python
# === scripts/hcl_color_engine.py Editorial Narrative Black-Box API Signatures ===
from hcl_color_engine import (
    apply_spotlight_colors,        # (values_or_labels, top_n=1, bottom_n=1, highlight_indices=None, highlight_color=None, context_color="#94A3B8", **kwargs) -> _SpotlightStyleResult
    add_badge_vline,               # (ax, x, badge_text, color=None, linestyle="--", linewidth=2.0, badge_y_axes=1.03, x_offset_pts=0.0, zorder=6, **kwargs) -> _BadgeVLineResult
    add_editorial_footer,          # (fig, footer_lines, y_top=0.088, line_spacing=0.022, rule_color="#CBD5E1", fontsize=9.0, **kwargs) -> List[Text]
    add_regime_shading_and_events, # (ax, regimes=None, events=None, **kwargs) -> Dict[str, List[Any]]
    add_inset_leaderboard,         # (ax, labels, values, bbox=(0.62, 0.08, 0.34, 0.32), title="", color=None, **kwargs) -> Axes
)
```

1. **技法 1：聚光燈階層著色（Spotlight vs. Context Hierarchy — 資料八標竿）**
   - **設計規範**：絕不將 20 個項目塗成無差別同色或彩虹雜色！使用 `apply_spotlight_colors(values, top_n=1, bottom_n=1)` 自動把「故事主角極值（如最高臺北市 117.0 萬、最低花蓮縣 59.2 萬）」或指定焦點索引設為深色聚光燈色（預設深海軍藍 `#0F3A68` 或主色極深階）、放大圓點（`highlight_size=110.0`）與粗體黑字（`#0F172A`, `bold`）；其餘中間配角退居柔和背景灰藍（`context_color="#94A3B8"`, `context_size=56.0`）與次要灰字（`#475569`, `normal`）。
2. **技法 2：多重統計基準虛線＋頂部帶框圓角膠囊徽章（Multi-Baseline Callout Badges — 資料八標竿）**
   - **設計規範**：當「未加權算術平均」與「官方加權整體值」或「中位數」存在顯著口徑落差（揭示右偏或大都會權重效應）時，**必須將兩條基準線同屏並立為視覺地標**！
   - **實作**：呼叫 `add_badge_vline(ax, x_val, "20 縣市未加權平均\n83.58 萬元", color="#0284C7")` 與第二條 `add_badge_vline(ax, x_val2, "臺灣整體（官方戶數加權）\n92.04 萬元", color="#CA6F35")`。函數內建 **白色描邊虛線防穿混** 與 **28 輪渲染器級水平碰撞鬆弛演算法**，自動將相鄰的頂部白底彩框圓角膠囊往左右推開，保證零重疊並保留斜角引線精準指向垂直虛線頂端。
   - *頂部留白提醒*：若啟用頂部膠囊徽章，主繪圖區 `subplots_adjust(top=...)` 建議調整至 `0.78~0.80`，為 `badge_y_axes=1.03` 預留充足上方空間以免撞及副標題。
3. **技法 3：時期背景色塊分區＋重大歷史／法規轉折引線方框（Regime Shading & Event Callouts — 資料七《臺灣數據百閱》）**
   - **設計規範**：長時序折線圖不可只畫一條孤立曲線，必須交代造成斜率劇變的制度背景或統計定義變更，防止讀者誤判趨勢。
   - **實作**：呼叫 `add_regime_shading_and_events(ax, regimes=[...], events=[...])`：
     - `regimes`：在時間軸背景鋪設淡色時期帶（如 `{"start": 2016, "end": 2019, "label": "擴張期"}`）；
     - `events`：在指定轉折點 `(x, y)` 標註圓點並拉出白底彩框引線方框說明歷史事件或口徑變更。
4. **技法 4：主圖＋角落微型排行榜副卡複合構圖（Primary Chart + Inset Leaderboard — 資料七《手搖飲密度》）**
   - **設計規範**：當地理密度圖或全局散布圖留有空白象限時，嵌入第二視角微型排行榜，一屏同時回答「分布在哪」與「誰占最多」。
   - **實作**：呼叫 `add_inset_leaderboard(ax, top_labels, top_values, bbox=(0.62, 0.08, 0.34, 0.32), title="規模前三名")`，於指定角落建立帶陰影邊框之乾淨白底子圖卡。
5. **技法 5：底部四層結構化資訊底註（4-Tier Editorial Footer — 資料八標竿）**
   - **設計規範**：於畫布底緣以 `#CBD5E1` 水平細線分隔，依序呈現四層高資訊密度圖註（粗體深色前導籤 `#0F172A`＋柔和灰說明文 `#475569`）：
     ```python
     add_editorial_footer(fig, [
         ("資料補充", "中位數 80.10 萬元；僅 4 縣市高於全臺加權整體值、16 縣市低於。"),
         ("註", "20 縣市未加權平均與官方臺灣地區整體加權值統計口徑不同。"),
         ("來源", "行政院主計總處《家庭收支調查報告》（有效樣本 16,528 戶）。"),
         ("提醒", "縣市估計值含抽樣誤差，不宜將細微排序差距視為具統計顯著性。"),
     ])
     ```
   - *(Medium 專欄相容規則)*：若屬於課堂 Medium 每週一圖作業模式且篇幅空間緊湊，圖表底註可改用精簡 2 項官方來源格式（1. 官方資料集網址、2. 資料涵蓋期間），將補充脈絡寫入專欄正文或維持四層圖註並擴大 `bottom` 至 `0.21`。

---

## 二、 Format B 深度報告（`.pdf`）編輯室社論排版組件與 Print-CSS 契約

[`../scripts/pdf_report_engine.py`](../scripts/pdf_report_engine.py) 已內建 4 組經 Chromium A4 印刷實測之無斷框編輯室組件，於報告 HTML 中可直接選用：

1. **`.editorial-masthead`（報刊頭條頂線開篇區）**：於報告首頁或大章節破題使用。
   ```html
   <div class="editorial-masthead">
     <div class="masthead-kicker">EMPIRICAL POLICY BRIEF · 2026</div>
     <h1>主標題斷言句</h1>
     <p class="masthead-deck">一句話導讀摘要...</p>
   </div>
   ```
2. **`.big-stat-callout`（巨型黃金數字衝擊盒）**：突顯單一最具反差感的關鍵統計量。
   ```html
   <div class="big-stat-callout">
     <div class="big-stat-number">1.98 倍</div>
     <div class="big-stat-label">最高縣市（臺北 117.0 萬）與最低縣市（花蓮 59.2 萬）每戶年消費差距</div>
   </div>
   ```
3. **`.myth-reality-split`（迷思 vs. 實證真相雙欄對撞解剖台）**：左紅右綠對照常見誤區與實證證據。
   ```html
   <div class="myth-reality-split">
     <div class="myth-box"><strong>常見直覺迷思</strong><p>...</p></div>
     <div class="reality-box"><strong>實證數據真相</strong><p>...</p></div>
   </div>
   ```
4. **`.methodology-traffic-light`（方法論紅黃綠燈證據紀律警示卡）**：對應《資料說明書》五種證據標籤與第 6 章推論限制。
   ```html
   <div class="methodology-traffic-light">
     <div class="traffic-tier"><span class="traffic-badge-green">綠燈已驗證</span><span>純明細 df_detail 統計口徑完全一致...</span></div>
     <div class="traffic-tier"><span class="traffic-badge-yellow">黃燈待查證</span><span>舊版欄位跨期定義轉換須留意...</span></div>
     <div class="traffic-tier"><span class="traffic-badge-red">紅燈禁推論</span><span>嚴禁將村里彙整資料推論為個人貧富差距（生態謬誤）</span></div>
   </div>
   ```

---

## 三、 Format A / C / E 編輯室敘事延伸規範

1. **Format A（知識圖譜 `.png`）**：在既有 T1～T5 網格下，維持全圖 **80/20 聚光燈階層**（僅將核心破局卡與關鍵痛點容器設為高彩度強調框，其餘鋪墊背景卡退為淡結構灰）；並在因果斷裂或瓶頸箭頭上加掛醒目紅色／橘色「瓶頸流失地標膠囊」。
2. **Format C（高階簡報 `.pptx`）**：啟用**「單一巨幅數據衝擊頁（Big Number Spotlight）」**（左側超大字級展示單一震撼比例＋脈絡副標，右側並置資料八聚光燈圖表）與「雙基準線落差對決卡」；同頁其餘對照卡片退居 `#CBD5E1` / `#64748B`。
3. **Format E（互動數據儀表板 Web）**：
   - 頂部 KPI 摘要卡內嵌「與基準線之正負差距膠囊（`Δ vs. 全國均值`）」；
   - 圖表工具列內建**「基準線切換器（切換未加權平均／官方加權整體值／中位數）」**與**「首尾極值聚光燈高亮開關」**。
