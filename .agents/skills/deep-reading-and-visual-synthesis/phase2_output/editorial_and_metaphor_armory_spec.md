# 全格式「編輯室敘事設計 ＆ RE:LAB 具象隱喻武器庫」終端實作規範（All-Format Editorial & Metaphor Armory Spec）

> **單一職責定位（Single Responsibility）**：本檔為 Phase 2 **終端執行層專檔**，**僅當第三層（Layer 3）確定開啟 `editorial_narrative`（模式 2）或 `bespoke_metaphor`（模式 3）時才按需載入**（若為 `standard_rigorous` 模式 1 則完全不開啟）。本檔統一定義資料八、資料七 RE:LAB 視覺與敘事設計哲學如何跨 **Format A / B / C / D / E 五大格式** 安全落地，包含經驗證的 **Python / JS / Print-CSS 黑盒 API 契約** 與 **IDE 跨工具協同渲染管線（SOP）**。

---

## 第一部：模式 2 `editorial_narrative`（資料八 & 數據百閱：編輯室權威敘事設計全格式規範）

### 1.1 Format D ⇄ E 編輯室敘事圖表 5 大標竿技法與黑盒 API 契約

> **黑盒呼叫鐵律**：所有編輯室高階圖表元素皆已封裝於 [`../scripts/hcl_color_engine.py`](../scripts/hcl_color_engine.py)，直接 `import` 呼叫並可於回傳之原生 Matplotlib 物件上自由微調（Zero Side-Effects）。

```python
# === scripts/hcl_color_engine.py Editorial Armory Black-Box API Signatures ===
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

### 1.2 Format B 深度報告（`.pdf`）編輯室社論排版組件與 Print-CSS 契約

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

### 1.3 Format A / C / E 編輯室敘事延伸規範

1. **Format A（知識圖譜 `.png`）**：在既有 T1～T5 網格下，維持全圖 **80/20 聚光燈階層**（僅將核心破局卡與關鍵痛點容器設為高彩度強調框，其餘鋪墊背景卡退為淡結構灰）；並在因果斷裂或瓶頸箭頭上加掛醒目紅色／橘色「瓶頸流失地標膠囊」。
2. **Format C（高階簡報 `.pptx`）**：啟用**「單一巨幅數據衝擊頁（Big Number Spotlight）」**（左側超大字級展示單一震撼比例＋脈絡副標，右側並置資料八聚光燈圖表）與「雙基準線落差對決卡」；同頁其餘對照卡片退居 `#CBD5E1` / `#64748B`。
3. **Format E（互動數據儀表板 Web）**：
   - 頂部 KPI 摘要卡內嵌「與基準線之正負差距膠囊（`Δ vs. 全國均值`）」；
   - 圖表工具列內建**「基準線切換器（切換未加權平均／官方加權整體值／中位數）」**與**「首尾極值聚光燈高亮開關」**。

---

## 第二部：模式 3 `bespoke_metaphor`（資料七 RE:LAB：六大編碼具象材質與空間隱喻武器庫 ＆ IDE 跨工具協同渲染管線）

### 2.1 跨工具協同分工鐵律與防破圖底線（Anti-Chartjunk & Cross-Tool Division of Labor）

> [!CAUTION]
> **【鐵律 1：生圖模型 (`image-generator`) 與 Python 渲染引擎之絕對邊界】**
> - **絕對禁止**呼叫 `image-generator` 直接生成含中文標題、數字標籤、百分比或座標軸的完整圖表（必生亂碼文字且比例失真）！
> - `image-generator` 在本管線中的**唯一職責**，是產出 **「純白底 `#FFFFFF`（或正對稱圓盤）、零任何文字與數字、高解析度材質紋理（Texture）或單一主題精靈圖標（Sprite）」**。
> - 所有數學比例裁切（`clip_path` / `Wedge`）、$(X, Y)$ 座標錨定（`AnnotationBbox`）與繁體中文 `Microsoft JhengHei` 排版，**100% 由 Python `hcl_color_engine.py` 精確執行**！
>
> **【鐵律 2：幾何比例 100% 數學誠實】**
> 任何具象設計皆不可犧牲數據精準度：容器液面高度線性對應數值、材質扇形圓心角嚴格等於 $360^\circ \times p$、面積大小圖塊之半徑／邊長正比於 $\sqrt{\text{Value}}$。

---

### 2.2 四大 IDE 跨工具具象轉譯管線標準作業程序（SOP）與黑盒 API 契約

```python
# === scripts/hcl_color_engine.py Bespoke Metaphor & Thematic Palette Black-Box API ===
from hcl_color_engine import (
    plot_liquid_container_bars, # (ax, labels, values, max_capacity=None, container_style="glass_cup", liquid_color="#FFFFFF", canvas_bg="#5BC0EB", glass_edge_color="#E2F1F8", value_fmt="{:.0f} ml", subtitle_values=None, **kwargs) -> Dict[str, Any]
    plot_masked_texture_wedge,  # (ax, pct_value, texture_img_path=None, title="", subtitle="", base_disc_color="#E2E8F0", wedge_edge_color="#FFFFFF", start_angle=90.0, clockwise=True, value_fmt=None, **kwargs) -> Dict[str, Any]
    plot_sprite_scatter,        # (ax, x_vals, y_vals, sprite_img_path=None, labels=None, zoom=0.18, auto_remove_white_bg=True, white_threshold=242, **kwargs) -> Dict[str, Any]
    derive_thematic_palette,    # (theme_preset_or_hex, sync_js_path=None, activate=False, **kwargs) -> Dict[str, Any]
)
```

#### 管線 A：【長度編碼具象轉譯】多層向量光影 ＋ `clip_path` 液面容器圖（RE:LAB《100元買多少鮮乳》模式）
- **適用時機**：呈現與「容量、購買力、電量、蓄水量、達成滿額度」高度相關的單序列長度比較（如各國鮮奶購買力、水庫蓄水率、電池續航）。
- **實作規範**：直接呼叫 `plot_liquid_container_bars(ax, labels, values, container_style="glass_cup" | "battery" | "beaker", ...)`：
  - 引擎自動繪製：等寬透明容器外框、底部加厚玻璃底座、內腔 `clip_path` 精確裁切液面高度、3D 液面頂部微橢圓半月面（Meniscus）、左右兩道半透明垂直玻璃反光高光帶（Specular Highlight Strips），並於上方自動標註實測數值與相對基準倍數 `subtitle_values`（如 `["約 1.99 倍", ..., "基準 1.00 倍"]`）。
  - **高對比底色設定**：若液體為純白鮮奶（`liquid_color="#FFFFFF"`），`canvas_bg` 選用清透天藍（如 `#3A8EAB` / `#5BC0EB`），函數會自動依 `relative_luminance(canvas_bg)` 切換高對比白字或深石板字體。

#### 管線 B：【角度與比例編碼具象轉譯】`image-generator` 無文字高清材質 ＋ Python `Wedge` 精準扇形遮罩小倍圖（RE:LAB《台灣鳳梨外銷中國比率》4×4 矩陣模式）
- **適用時機**：呈現單一核心佔比隨時間或跨群組的消長（特別適合 4×4 小倍圖 Small Multiples 矩陣）。
- **兩步標準 SOP**：
  1. **Step 1（呼叫 `image-generator` 生成無文字高清圓盤材質，存於 `02_outputs/assets/<topic>_texture.png`）**：
     - **標準 Prompt 範本**：
       > *"Top-down flat orthographic macro view of a single circular [TOPIC OBJECT, e.g. fresh golden pineapple cross-section slice], centered symmetrically and filling a square frame, rich natural organic fiber texture and vibrant realistic lighting, clean edge-to-edge pattern, strictly NO text, NO numbers, NO labels, NO watermark, high resolution studio photo/illustration."*
     - *(註：若離線或僅需快速原型，`texture_img_path=None` 亦內建高解析程序化鳳梨剖面材質生成器。)*
  2. **Step 2（由 Python 執行精準扇形遮罩與排版）**：
     - 迴圈呼叫 `plot_masked_texture_wedge(ax, pct_value, texture_img_path="assets/<topic>_texture.png", title="2020", subtitle="外銷中國占比")`。函數會將材質中心裁切為 `512×512` RGBA，於底層繪製淡灰 `100%` 基準圓盤（`#E2E8F0`），再以 `matplotlib.patches.Wedge`（圓心角嚴格等於 $360^\circ \times p$）套用 `set_clip_path()` 精準裁切，完全確保 **100% 數學無誤差＋繁體中文零亂碼**！

#### 管線 C：【點位與陣列編碼具象轉譯】`image-generator` 單體精靈圖標 ＋ PIL 白底自動去背 ＋ Python `AnnotationBbox` 座標散佈圖（RE:LAB《咖啡廳數據散佈圖》模式）
- **適用時機**：X-Y 雙變數散佈圖或 $10 \times 10$ 象形陣列圖，當每個資料點都代表極具生活辨識度的實體（咖啡廳、飛機、住宅、貨櫃、太陽能板）。
- **兩步標準 SOP**：
  1. **Step 1（呼叫 `image-generator` 生成單體精靈圖標，存於 `02_outputs/assets/<topic>_sprite.png`）**：
     - **標準 Prompt 範本**：
       > *"Single isolated top-down studio photograph of one [TOPIC ICON, e.g. roasted coffee bean], centered on a pure solid #FFFFFF white background with crisp clean edges and zero drop shadow outside the object, strictly NO text, NO labels, NO watermark."*
  2. **Step 2（由 Python 自動去背並精準錨定座標）**：
     - 呼叫 `plot_sprite_scatter(ax, x_vals, y_vals, sprite_img_path="assets/<topic>_sprite.png", labels=city_names, zoom=0.16, auto_remove_white_bg=True)`。引擎自動將純白背景轉為透明 Alpha 通道，再透過 `OffsetImage` ＋ `AnnotationBbox` 將圖標**精確釘在每個縣市真實的 `(x, y)` 數值座標上**並附帶防衝突引線標註。

#### 管線 D：【色彩深淺與主題語義轉譯】CIELAB 主題語義色階推導 ＋ 看板外框與角落排行副卡（RE:LAB《台灣飲料店密度》模式）
- **實作規範**：調用 `derive_thematic_palette(theme_preset_or_hex, activate=True)`（前端 JS 同步提供 `window.GephiPalette.deriveThematicPalette(presetOrHex, { activate: true })`）。
- **內建 6 大主題語義色階預設鍵值（皆經 CIELAB 感知空間等明度校正）**：
  - `"milk_tea"` / `"bubble_tea"`（奶茶焦糖棕 `#C87D55` ＋ 茶綠 `#5C8D89`）
  - `"forest_eco"` / `"matcha_forest"`（森林生態綠 `#3A7D44` ＋ 溪流藍 `#2C6E8F`）
  - `"ocean_blue"` / `"ocean_hydro"`（海洋深藍 `#0284C7` ＋ 潟湖綠 `#0D9488`）
  - `"coffee_roast"`（深焙咖啡棕 `#7F4F24` ＋ 抹茶綠 `#4A7C59`）
  - `"pineapple_tropical"` / `"agri_gold"`（熱帶金黃 `#D97706` ＋ 農產綠 `#15803D`）
  - 或傳入**任意單一主題代表 HEX**（如 `"#E11D48"`），由引擎透過 CIELAB 正交旋轉自動衍生 4 組均衡主色、5 階循序色階與 9 階發散色階，並搭配 `add_inset_leaderboard()` 呈現角落 Top N 排行小卡。

---

### 2.3 Format A / B / C / E 空間與物理結構隱喻延伸規範

1. **Format A（知識圖譜 `.png` — `0~100` 瑞士網格空間隱喻）**：
   - 當開啟模式 3 且文章核心適合空間隱喻時，於 `generate_mindmap.py` 的 `0~100` 畫布上實作：
     - **冰山分層圖（Iceberg Anatomy）**：繪製水平水面分界線（`Y = 56`），上方（`Y: 58~88`）以清淺天藍 `draw_macro_zone` 承載「可見表象／表面症狀卡」，下方（`Y: 12~52`）以深海藍紫背景區承載「水面下結構根因／隱含機制卡」。
     - **階梯漏斗過濾器（Funnel Filter）**：由上而下配置寬度逐層收窄的 `draw_macro_zone`（`W = 90 -> 68 -> 46`），兩側以斜向流失箭頭＋膠囊標註每一層的過濾淘汰因子。
     - **雙向天平／力場對決（Force-Field Balance）**：中央置入支點樞紐，左右兩區分別以推進力（右綠/藍）與阻力（左紅/橘）平行對應推演。
2. **Format B / C / E（報告、簡報與儀表板主題沉浸式裝幀）**：
   - **Format B（PDF）**：將 `derive_thematic_palette()` 衍生色注入報刊頭條頂線 `.editorial-masthead`、`.big-stat-callout` 與標題強調色，同時維持白底高對比（WCAG AA $\ge 4.5:1$）。
   - **Format C（簡報）**：於階段或對比頁運用階梯進度、容器液面填充向量塊或天平雙軌對比，搭配 `image-generator` 生成之透明主題小圖標點綴章節視覺記憶點。
   - **Format E（儀表板 Web）**：於前端直接呼叫 `window.GephiPalette.deriveThematicPalette(preset, { activate: true })` 動態覆寫 CSS `:root` 變數，並可選配水平/垂直玻璃容器進度條與 $10 \times 10$ 象形陣列佔比卡。
