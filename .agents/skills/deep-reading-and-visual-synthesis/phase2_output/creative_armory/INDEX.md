# 模式 3：開放式創意隱喻武器庫總索引（Mode 3: Open-Ended Creative Armory Index）

> **單一職責定位（Single Responsibility）**：本檔為 Phase 2 **模式 3（`bespoke_metaphor` 議題具象材質、純幾何物理隱喻與空間轉譯）之唯一輕量入口**，**僅當第三層（[`../advisors/layer3_advisor_design_style_color.md`](../advisors/layer3_advisor_design_style_color.md)）明確開啟模式 3 時才按需載入**。
> - **與模式 2 徹底解耦**：本武器庫可獨立運作（零圖內多餘浮動說明框），無須強制載入 [`../editorial_narrative_spec.md`](../editorial_narrative_spec.md)；唯有當使用者同時開啟模式 2 編輯室標註或 PDF 社論組件時，才併同載入該檔。
> - **O(1) 注意力零浪費設計**：下方案例庫僅保留「單行索引表」，**禁止一次讀完所有案例卡**！唯有鎖定某項技法參考時，才點開對應之單一原子案例卡（`cases/<category>/<case>.md`）。

---

## 一、 開放式創意原則（Open-Ended "Form-as-Metaphor" Philosophy — 絕不限縮為封閉模板庫）

模式 3 的本質不是「從既有的 3～4 個固定模板中硬套一個」，而是**依據該次數據的真實領域語義，為讀者打造「形式即故事（Form-as-Metaphor）」的專屬視覺編碼**。AI 可自由發明全新的純幾何結構隱喻或跨工具材質轉譯，但**所有創意皆必須嚴守以下五大科學與工程底線**：

> [!CAUTION]
> **【底線 1：100% 數學誠實與零失真比例（Zero Lie Factor）】**
> 任何具象容器、材質遮罩或幾何結構皆不得犧牲讀取精準度：液面高度嚴格線性對應數值、材質扇形圓心角嚴格等於 $360^\circ \times p$、二維面積之半徑／邊長嚴格正比於 $\sqrt{\text{Value}}$。
>
> **【底線 2：實證選型紅線 — 不為造型犧牲共用基線與全樣本密度（參考 `T25`）】**
> 動工前先依 [`../advisors/layer2_advisor_de_chart.md`](../advisors/layer2_advisor_de_chart.md) 檢驗：(1) 若核心命題是「兩條序列的淨差距」，不可為追求鏡像造型而拆散共用基線；(2) 若核心命題是「多維全樣本結構分布（如數十個縣市／業別）」，不可為了畫具象造型而砍掉多數樣本只剩少數代表點。唯有**創意形式本身能放大數據反差或記憶點、且不損及核心讀取任務**時，才啟用模式 3。
>
> **【底線 3：生圖模型（`image-generator` 子代理）與 Python 渲染引擎之絕對邊界】**
> - **絕對禁止**呼叫生圖模型直接生成含中文標題、數字標籤、百分比或座標軸的完整圖表或整頁投影片（必生亂碼文字且比例失真）！
> - 生圖模型的**合法邊界**僅限兩類「零文字與零數字」視覺素材：① **Format D 統計圖表**僅產出「純白底 `#FFFFFF`（或正對稱圓盤）之高解析度材質紋理（Texture）或單一主題精靈圖標（Sprite）」，所有數學比例裁切（`clip_path` / `Wedge`）、$(X, Y)$ 座標錨定（`AnnotationBbox`）與繁中排版 100% 由 `hcl_color_engine.py` 精確執行；② **Format C 模式 3 `Tier 2` 簡報**僅於封面／過場／至多 1 頁破題頁產出「預留乾淨負空間、零任何文字與數字」之概念主視覺底圖，標題與細線 100% 由 `pptx_slide_engine.py` 原生文字疊加。所有生圖素材一律存於 `reading_sessions/<YYYYMMDD_主題簡稱>/02_outputs/assets/`。
>
> **【底線 4：優先讓幾何結構本身說話，不硬塞浮動說明框】**
> 模式 3 支援極簡無浮動文字框的「純幾何隱喻（Pure Form-as-Metaphor）」，無須為了營造設計感而堆砌多餘裝飾方框或圖內長段旁白。
>
> **【底線 5：Format C 簡報模式 3 三級解鎖與防花俏紅線（`Tier 1 / 2 / 3`）】**
> Format C 開啟模式 3 時須先於 [`../advisors/layer3_advisor_design_style_color.md`](../advisors/layer3_advisor_design_style_color.md) 由使用者拍板 **`Tier 1`（原生幾何原語＋動態主題色票）／`Tier 2`（加無文字概念主視覺）／`Tier 3`（加 1～2 頁 HTML+SVG `300 DPI` 透明底層）** 並寫入 **Topic Art Direction DNA 卡**；全簡報嚴限 **`1` 個核心視覺母題**、嚴守 **`20/80` 克制比**（70%～80% 頁採乾淨無框與細線承托）、禁無關裝飾廢圖（Bartsch & Cobern 2003），且全頁仍強制通過 `verify_pptx_structure(min_font_pt=...)`。

---

## 二、 依視覺編碼分類之原子案例單行索引表（Atomic Case Library — Single-Line Index）

> **按需載入守則**：先看下表單行摘要決定方向——若現有原子案例符合需求，**僅讀取對應的 1 份案例卡**；若本次數據適合全新的領域隱喻，直接依上述五大底線原創設計即可！

| 視覺編碼分類目錄 | 原子案例卡（按需單開） | 核心隱喻機制與適用情境（單行摘要） | 黑盒 API / 跨工具依賴 |
| :--- | :--- | :--- | :--- |
| **`01_texture_and_container/`**<br>*(材質、容器與精靈圖標)* | [`cases/01_texture_and_container/glass_liquid_bars.md`](cases/01_texture_and_container/glass_liquid_bars.md) | **長度編碼 → 透明容器液面柱**（玻璃杯／電池／燒杯高光與半月面；適用容量、購買力、蓄水率、續航） | `plot_liquid_container_bars` |
| **`01_texture_and_container/`**<br>*(材質、容器與精靈圖標)* | [`cases/01_texture_and_container/masked_texture_wedges.md`](cases/01_texture_and_container/masked_texture_wedges.md) | **角度／佔比編碼 → 高清材質扇形遮罩小倍圖**（無文字圓盤材質＋`Wedge` 精準 $360^\circ \times p$ 裁切；適用跨期單一佔比消長） | `image-generator` + `plot_masked_texture_wedge` |
| **`01_texture_and_container/`**<br>*(材質、容器與精靈圖標)* | [`cases/01_texture_and_container/sprite_coord_scatter.md`](cases/01_texture_and_container/sprite_coord_scatter.md) | **點位／陣列編碼 → 單體精靈圖標座標散佈**（白底自動去背＋`AnnotationBbox` 精準釘座標；適用高辨識度實體散佈） | `image-generator` + `plot_sprite_scatter` |
| **`02_structural_geometry/`**<br>*(純幾何物理結構隱喻)* | *(開放式成長目錄：[`cases/02_structural_geometry/.gitkeep`](cases/02_structural_geometry/.gitkeep))* | **純向量幾何 Form-as-Metaphor 預留庫**（零材質、零浮動框、且不損及讀取精度與樣本密度之未來原創純向量幾何隱喻；凡經使用者實戰驗收勝出者自動沉澱為單行原子卡；註：蝴蝶金字塔與雙向向量箭頭已升格常駐 [`../chart_family1_ranking_and_deviation.md`](../chart_family1_ranking_and_deviation.md)） | 原生 Matplotlib 向量幾何 |
| **`03_spatial_and_thematic/`**<br>*(空間拓撲與主題色階裝幀)* | [`cases/03_spatial_and_thematic/thematic_palette_frame.md`](cases/03_spatial_and_thematic/thematic_palette_frame.md) | **色彩語義與跨格式裝幀 → CIELAB 主題色階＋Format C 動態主題色票**（5 大內建色階（9 別名）或單一 HEX 推導；Format C 支援開燈教室淺底安全組／可控深場＋WCAG AA $\ge 4.5:1$） | `derive_thematic_palette` / `derive_slide_theme_from_topic` / `deriveThematicPalette` + `add_inset_leaderboard` |
| **`03_spatial_and_thematic/`**<br>*(空間拓撲與主題色階裝幀)* | [`cases/03_spatial_and_thematic/diagram_spatial_metaphors.md`](cases/03_spatial_and_thematic/diagram_spatial_metaphors.md) | **Format A / C 空間拓撲隱喻與 `Tier 1 / 2 / 3` 操作細則**（Format A 冰山／漏斗／天平；Format C 原生幾何原語、`image-generator` 無字概念主視覺、HTML+SVG `300 DPI` 透明底層、1 母題與 `20/80` 紅線） | `generate_mindmap.py` / `pptx_slide_engine.py` (`draw_theme_geometric_accent`, `render_svg_to_png_300dpi`) + `image-generator` |

---

## 三、 成功創意案例回饋入庫閉環（Case Feedback-to-Library Rule）

當某次模式 3 專案發想出**不在上表中的全新創意圖型或空間隱喻**，且經使用者實際驗收勝出時，於結案 Step E1～E3 進化閉環（詳見 [`../../setup/git_sync_and_evolution_protocol.md`](../../setup/git_sync_and_evolution_protocol.md)）中執行：
1. 將去專案化之通用設計法則、適用與不適用邊界（防誤導條件）及核心實作骨架寫成 1 份獨立原子案例卡，存入對應分類目錄 `cases/<category>/<case_name>.md`。
2. 僅於本檔第二節索引表**追加 1 行單行索引**，確保案例庫即使成長至數十個案例，日常載入 `INDEX.md` 仍維持極低 Token 負擔。
