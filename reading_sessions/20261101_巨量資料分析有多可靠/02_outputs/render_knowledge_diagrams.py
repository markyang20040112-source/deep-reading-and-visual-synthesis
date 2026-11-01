"""
render_knowledge_diagrams.py
Generates publication-grade Visual Knowledge Diagrams (Format A) for the MIS Case Study:
"How Reliable Is Big Data Analytics? (巨量資料分析有多可靠？)"
1. 01_article_master_structure_map.png (T5: Swiss Full-Spine & 4-Trunk Fork)
2. 02_predictive_reliability_architecture.png (T2: 3-Column 3x3 Pipeline & Governance Architecture)

Strictly follows visual_diagram_matplotlib_spec.md & visual_cognition_principles.md:
- 4 -> 2 -> 3 Hierarchical Chunking
- Plain-First & Shallow-to-Deep (淺層現象 -> 中層案例 -> 深層對策)
- 60~66 Hanzi 2-line balanced bullets, True Vertical Slot Centering (va="center")
"""

import sys
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

script_dir = os.path.abspath(".agents/skills/deep-reading-and-visual-synthesis/scripts")
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from generate_mindmap import (
    THEMES,
    configure_cjk_fonts,
    draw_macro_zone,
    draw_modern_card,
    draw_labeled_bezier,
    draw_labeled_arrow,
    draw_hierarchical_trunk_fork,
    draw_canvas_header_and_footer,
    save_publication_figure,
)

configure_cjk_fonts()

output_dir = os.path.abspath("reading_sessions/20261101_巨量資料分析有多可靠/02_outputs")
os.makedirs(output_dir, exist_ok=True)


def draw_expansive_card(ax, x, y, width, height, title, bullets, theme,
                        accent_key="primary", badge_text=None,
                        fig_width_in=28.0, font_pt=12.0, max_em_override=None):
    return draw_modern_card(
        ax, x, y, width, title, bullets, theme,
        accent_key=accent_key, badge_text=badge_text,
        max_em_width=max_em_override, fixed_height=height,
        fig_width_in=fig_width_in, font_pt=font_pt
    )


# ==============================================================================
# DIAGRAM 1: ARTICLE MASTER STRUCTURE MAP (T5 瑞士網格全高主軸分叉圖)
# ==============================================================================
def render_master_structure_map():
    theme = THEMES["swiss_editorial"]
    fig, ax = plt.subplots(figsize=(28, 18.5), dpi=240)
    ax.set_facecolor(theme["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    draw_canvas_header_and_footer(
        ax,
        title="【全景主圖】巨量資料分析有多可靠？商業效益、方法論盲點與預測失靈全景拆解",
        subtitle="Laudon《管理資訊系統》第 6 章個案研究 ｜ 橫跨英、美、紐澳與全球企業之大數據決策可靠度診斷",
        takeaway_title="★ 一句話讀懂核心結論：資料量再大也不會自動變成好決策——沒有清晰目標、即時脈絡與領域知識把關，大數據只會放大偏見",
        takeaway_lines=[
            "● 【由淺入深看問題】全球每日產生 2,500 萬億 Bytes 資料，但盲目跟風者常把 Twitter 聲量當銷售 KPI、把「IE 市佔與謀殺率」當因果，或因忽略社會脈絡與歷史偏見而預測翻車。",
            "● 【由淺入深看解法】標竿組織（英國 NHS 省 5.81 億英鎊、紐約警局監控 76 轄區）皆落實「管理目標 × 組織領域專家 × 科技即時清理」三維協同，讓演算法成為受監督的精準助手。"
        ],
        theme=theme
    )

    # 1. Four Macro Zones (Cowan 4+-1 Top-Level Chunking)
    draw_macro_zone(ax, 3.5, 51.8, 30.2, 38.0, "壹、【標竿價值】海量資料爆發與三大成功實踐", theme, "success")
    draw_macro_zone(ax, 3.5, 11.8, 30.2, 38.2, "貳、【策略與方法盲點】KPI 測量迷思與假性相關", theme, "warn")
    draw_macro_zone(ax, 66.3, 51.8, 30.2, 38.0, "參、【模型翻車與倫理】三大失準教訓與推論隱私", theme, "danger")
    draw_macro_zone(ax, 66.3, 11.8, 30.2, 38.2, "肆、【MIS 破局解方】管理×組織×科技與建模防線", theme, "primary")

    # 2. Central Full-Height Thesis Spine (X: 38.4, W: 23.2, Y: 14.5 ~ 86.5)
    hub_x, hub_y, hub_w, hub_h = 38.4, 14.5, 23.2, 72.0
    hub_box = FancyBboxPatch(
        (hub_x, hub_y), hub_w, hub_h,
        boxstyle="round,pad=0.3,rounding_size=1.3",
        linewidth=2.4, edgecolor=theme["hub_border"], facecolor=theme["hub_bg"], zorder=3
    )
    ax.add_patch(hub_box)

    ax.text(hub_x + hub_w / 2.0, hub_y + hub_h - 2.3, "【核心主軸】數據規模 ≠ 決策可靠度",
            fontsize=17.2, fontweight="bold", color=theme["hub_text"], ha="center", va="center", zorder=4)
    ax.text(hub_x + hub_w / 2.0, hub_y + hub_h - 5.1, "由淺入深四階剖析：從大數據美麗願景到高可靠決策防線",
            fontsize=11.8, fontweight="bold", color=theme["hub_sub"], ha="center", va="center", zorder=4)
    ax.plot([hub_x + 1.2, hub_x + hub_w - 1.2], [hub_y + hub_h - 6.8, hub_y + hub_h - 6.8],
            color=theme["hub_border"], lw=1.2, alpha=0.8, zorder=3.5)

    spine_modules = [
        ("【第 1 階：商業價值】精準推薦與公部門降本", "#6EE7B7", [
            "每日產生 2,500 萬億 Bytes 資料；目標清晰",
            "時，Amazon 精準推薦、英國 NHS 省 5.81 億",
            "英鎊，紐約警局即時鎖定 76 轄區犯罪熱點。"
        ]),
        ("【第 2 階：策略盲點】可測量不代表該測量", "#FCD34D", [
            "沒定目標就跳進資料堆，誤把 Twitter 聲量",
            "當銷售 KPI 耗盡精力；更常把「IE 市佔與謀",
            "殺率同步下降」當因果，缺領域知識易誤判。"
        ]),
        ("【第 3 階：預測翻車】過時模型與忽略脈絡", "#FCA5A5", [
            "Meridian 舊軟體脫節、Google 流感被恐慌搜",
            "尋騙倒、2016 美選盲信歐巴馬舊選民庫翻車；",
            "跨源探勘帕金森氏症前兆更引爆推論隱私危機。"
        ]),
        ("【第 4 階：MIS 防線】人機協同與脈絡校準", "#93C5FD", [
            "投入前須先對齊「管理目標、組織領域人才、",
            "科技即時清理」，並以「動態樣本＋外部脈絡",
            "調節＋專家因果檢驗」打造高可靠決策系統。"
        ])
    ]

    mod_top = hub_y + hub_h - 8.2
    mod_bot = hub_y + 1.4
    mod_avail = mod_top - mod_bot
    mod_h = mod_avail / len(spine_modules)
    module_centers_y = []

    for m_idx, (m_title, m_color, m_lines) in enumerate(spine_modules):
        my_top = mod_top - m_idx * mod_h
        box_y = my_top - mod_h + 0.7
        box_h = mod_h - 1.1
        module_centers_y.append(box_y + box_h / 2.0)
        sub_box = FancyBboxPatch(
            (hub_x + 1.1, box_y), hub_w - 2.2, box_h,
            boxstyle="round,pad=0.15,rounding_size=0.7",
            linewidth=1.2, edgecolor=m_color, facecolor="#1E293B", zorder=3.5
        )
        ax.add_patch(sub_box)
        header_line_y = box_y + box_h - 3.6
        ax.plot([hub_x + 1.8, hub_x + hub_w - 1.8], [header_line_y, header_line_y],
                color="#334155", lw=0.8, zorder=3.8)
        ax.text(hub_x + 1.9, box_y + box_h - 1.85, m_title,
                fontsize=12.6, fontweight="bold", color=m_color, ha="left", va="center", zorder=4)
        body_mid_y = box_y + (box_h - 3.6) / 2.0
        for l_i, line_str in enumerate(m_lines):
            ly = body_mid_y + (1 - l_i) * 2.55
            ax.text(hub_x + 1.9, ly, line_str,
                    fontsize=11.4, color="#F8FAFC", ha="left", va="center", zorder=4)

    # 3. Eight Sub-Cards (2 per Macro Zone, 3 bullets per card: 淺 -> 中 -> 深)
    # Zone 1: Left Top (Success)
    draw_expansive_card(
        ax, 4.4, 70.5, 28.4, 16.4,
        title="商業價值：個人化精準推薦與全網最低價比價",
        bullets=[
            "● 【淺層直覺：猜中你喜歡什麼】— 全球每天產生 2,500 萬億位元組資料，企業得以從海量行為軌跡中讀懂每位顧客的偏好",
            "● 【中層案例：串流與比價平台】— Amazon、YouTube 與 Spotify 提供數百萬筆個人化推薦；比價網助消費者找車與機票最低價",
            "● 【深層效益：跨產業全面擴散】— 除了帶動電商與數位平台蓬勃成長，更延伸至運動賽事、教育、科學研究等多元決策場景"
        ],
        theme=theme, accent_key="success", badge_text="效益一"
    )
    draw_expansive_card(
        ax, 4.4, 52.8, 28.4, 16.4,
        title="公部門標竿：英國 NHS 醫療省錢與紐約警局緝兇",
        bullets=[
            "● 【淺層直覺：救命與抓賊更快】— 公部門將分散在醫院與警局的數十億筆紀錄集中高速分析，把有限預算與人力派到刀口上",
            "● 【中層案例：Exadata 與犯罪地圖】— 英國 NHS 揪出併用 10 種藥物與過量抗生素病患省 5.81 億英鎊；紐約警局彙整 76 轄區熱點",
            "● 【深層效益：制度化精準治理】— NHS 串連癌症數據優化治療方案，紐約犯罪策略部門（CSU）則鎖定重度累犯積極追訴降犯罪"
        ],
        theme=theme, accent_key="success", badge_text="效益二"
    )

    # Zone 2: Left Bottom (Warn)
    draw_expansive_card(
        ax, 4.4, 30.5, 28.4, 16.5,
        title="策略陷阱：沒定目標瞎忙與「可測量就該測量」迷思",
        bullets=[
            "● 【淺層直覺：看錯指標白忙一場】— 在資料堆裡打滾不代表決策更聰明，若資料未清理或指標選錯，只會把團隊帶往錯誤方向",
            "● 【中層案例：誤把社群聲量當業績】— 某大公司原本靠實體貿易展成交，卻建儀表板把官網流量與 Twitter 提及次數列為銷售 KPI",
            "● 【深層代價：虛耗資源產出廢線索】— 銷售部門被迫花大把時間盯社群點擊率，最終只產出大堆永遠無法轉化為實際營收的無效線索"
        ],
        theme=theme, accent_key="warn", badge_text="盲點一"
    )
    draw_expansive_card(
        ax, 4.4, 12.6, 28.4, 16.5,
        title="方法論陷阱：統計相關性 ≠ 真實世界的因果關係",
        bullets=[
            "● 【淺層直覺：一起發生不代表誰害誰】— 大數據極擅長挖出微小資料集漏掉的細微關聯，但演算法分不清那是巧合還是真因果",
            "● 【中層案例：IE 瀏覽器與謀殺率】— 2006 至 2011 年美國各州謀殺率與 IE 瀏覽器市佔率同步顯著下降，呈現極高度正相關",
            "● 【深層防線：仰賴領域知識把關】— 兩者毫無實質因果聯繫；分析師若缺乏特定業務領域知識（Domain Knowledge），必遭假相關誤導"
        ],
        theme=theme, accent_key="warn", badge_text="盲點二"
    )

    # Zone 3: Right Top (Danger)
    draw_expansive_card(
        ax, 67.2, 70.5, 28.4, 16.4,
        title="模型失靈：過時模擬、忽略媒體脈絡與歷史樣本偏見",
        bullets=[
            "● 【淺層直覺：拿過去死規則算未來】— 當預測模型脫離真實環境、只看表面搜尋數字或盲信舊時代樣本，遇到突發變化就會集體翻車",
            "● 【中層案例：三大經典預測翻車案】— 紐澳 Meridian 舊軟體失準、Google 流感被媒體恐慌搜尋騙倒、2016 美選預測柯林頓勝率 70-99% 卻敗選",
            "● 【深層病根：缺乏脈絡與誤差校正】— 柯林頓盲信歐巴馬時期支持族群（婦女、少數族裔、藍領）不變，忽略最後一刻轉向者與英國脫歐式錯愕"
        ],
        theme=theme, accent_key="danger", badge_text="危機一"
    )
    draw_expansive_card(
        ax, 67.2, 52.8, 28.4, 16.4,
        title="倫理與資安危機：高風險貼標籤與「推論隱私」侵害",
        bullets=[
            "● 【淺層直覺：比你自己還懂你的秘密】— 企業收集購物習慣、收入、嗜好與手機 GPS 移動路徑，在當事人不知情下暗中分類貼標籤",
            "● 【中層案例：帕金森氏症與無意識偏好】— 跨資料源結合後，竟能推論出個人信貸健康高風險、早期帕金森氏症前兆或對藍綠商品無意識偏好",
            "● 【深層風險：缺乏法律程序與反擊權】— 在毫無法律保護與申訴機制下，民眾不知道自己已被標記為「高風險者」，更淪為演算法操控對象"
        ],
        theme=theme, accent_key="danger", badge_text="危機二"
    )

    # Zone 4: Right Bottom (Primary)
    draw_expansive_card(
        ax, 67.2, 30.5, 28.4, 16.5,
        title="MIS 鐵三角評估：管理、組織與科技三維整備",
        bullets=[
            "● 【管理維度：先立目標再談數據】— 破除可測量就該測量的迷思，先確立能解決核心瓶頸的 KPI，並劃定顧客推論隱私與法規紅線",
            "● 【組織維度：培育領域知識人才】— 確保業務部門重心不被錯誤儀表板扭曲，配置懂業務邏輯的分析師解讀脈絡並過濾假性相關",
            "● 【科技維度：清理資料與即時運算】— 先落實資料清理與治理，建置如 Oracle Exadata 高速架構，並導入串接即時數據的 IBM 預測系統"
        ],
        theme=theme, accent_key="primary", badge_text="解方一"
    )
    draw_expansive_card(
        ax, 67.2, 12.6, 28.4, 16.5,
        title="高可靠預測建模：動態樣本更新 × 外部脈絡 × 專家審核",
        bullets=[
            "● 【破除資料偏見：摒棄靜態歷史假設】— 不盲信過往成功資料庫，持續更新動態即時樣本並加入環境誤差校正，捕捉最後一刻轉向者",
            "● 【補足外部脈絡：設媒體異常調節項】— 將媒體炒作與突發事件設為模型降權因子，並拿線上搜尋量與 CDC 實體就診數據交叉校準",
            "● 【人機協同防線：領域專家最終把關】— 拒絕將決策權完全交給黑箱演算法，由人類專家持續檢驗因果邏輯，一發現脫節立即修正權重"
        ],
        theme=theme, accent_key="primary", badge_text="解方二"
    )

    # 4. Hierarchical 1-to-2 Trunk Forks (4 Main Trunks from Central Spine to 4 Macro Zones)
    draw_hierarchical_trunk_fork(
        ax,
        p_start=(hub_x, module_centers_y[0]),
        p_card1=(32.8, 78.7),
        p_card2=(32.8, 61.0),
        trunk_label="創造效益",
        theme=theme, accent_key="success"
    )
    draw_hierarchical_trunk_fork(
        ax,
        p_start=(hub_x, module_centers_y[1]),
        p_card1=(32.8, 38.7),
        p_card2=(32.8, 20.8),
        trunk_label="揭露盲點",
        theme=theme, accent_key="warn"
    )
    draw_hierarchical_trunk_fork(
        ax,
        p_start=(hub_x + hub_w, module_centers_y[2]),
        p_card1=(67.2, 78.7),
        p_card2=(67.2, 61.0),
        trunk_label="診斷失靈",
        theme=theme, accent_key="danger"
    )
    draw_hierarchical_trunk_fork(
        ax,
        p_start=(hub_x + hub_w, module_centers_y[3]),
        p_card1=(67.2, 38.7),
        p_card2=(67.2, 20.8),
        trunk_label="治理防線",
        theme=theme, accent_key="primary"
    )

    out_path = os.path.join(output_dir, "01_article_master_structure_map.png")
    save_publication_figure(fig, out_path, theme, dpi=240)


# ==============================================================================
# DIAGRAM 2: PREDICTIVE RELIABILITY & MIS GOVERNANCE ARCHITECTURE (T2 三欄 3x3 管線圖)
# ==============================================================================
def render_predictive_reliability_architecture():
    theme = THEMES["swiss_editorial"]
    fig, ax = plt.subplots(figsize=(28, 18.5), dpi=240)
    ax.set_facecolor(theme["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    draw_canvas_header_and_footer(
        ax,
        title="【核心機制圖】從「失靈黑箱預測」到「高可靠人機協同決策」之 3×3 治理架構",
        subtitle="整合問題 3（五大限制）、問題 4（MIS 管理-組織-科技鐵三角）與問題 5（破除資料偏見與脈絡缺失）之系統工程藍圖",
        takeaway_title="★ 系統治理黃金定律：可靠決策 ＝ 高品質即時資料（科技） × 外部脈絡動態校正（管理） × 人類領域知識因果把關（組織）",
        takeaway_lines=[
            "● 【橫向轉換邏輯（左 → 中 → 右）】左欄揭露企業最常踩中的「三大失靈黑箱陷阱」；中欄透過 MIS 鐵三角與雙軌校正機制進行「過濾、校準與審查」；右欄最終產出「商業降本、精準預警與隱私合規」三大可靠成果。",
            "● 【縱向協同邏輯（上 → 中 → 下）】上層處理「資料源頭與歷史偏見（Data Bias）」、中層處理「模型演算法與外部脈絡（Context）」、下層處理「組織領域知識（Domain Knowledge）與推論隱私邊界」，三層環環相扣缺一不可。"
        ],
        theme=theme
    )

    # 3 Columns Macro Zones (Left: Danger Trap, Middle: Primary Governance Engine, Right: Success Outcome)
    col1_x, col2_x, col3_x = 3.5, 36.2, 68.9
    col_w = 27.6
    zone_y, zone_h = 11.8, 78.0

    draw_macro_zone(ax, col1_x, zone_y, col_w, zone_h, "壹、【左欄：失靈黑箱陷阱】三大預測翻車病根", theme, "danger")
    draw_macro_zone(ax, col2_x, zone_y, col_w, zone_h, "貳、【中欄：MIS 校正引擎】管理×組織×科技防線", theme, "primary")
    draw_macro_zone(ax, col3_x, zone_y, col_w, zone_h, "參、【右欄：高可靠決策】標竿效益與倫理合規", theme, "success")

    row_y = [65.2, 39.2, 13.2]
    card_h = 21.2
    card_w = 25.4
    c1_cx = col1_x + 1.1
    c2_cx = col2_x + 1.1
    c3_cx = col3_x + 1.1

    # --- ROW 1: DATA BIAS & REAL-TIME INFRASTRUCTURE (科技維度 × 破除資料偏見) ---
    draw_expansive_card(
        ax, c1_cx, row_y[0], card_w, card_h,
        title="源頭陷阱：歷史樣本僵化與過時模擬",
        bullets=[
            "● 【淺層現象：拿舊地圖找新路】— 盲目相信過去成功的歷史資料庫與老舊模擬公式，以為世界永遠不會變",
            "● 【中層案例：美選翻車與電力失準】— 柯林頓沿用歐巴馬舊選民庫（預測勝率 70-99% 卻落敗）；Meridian 舊軟體無法預警停擺",
            "● 【深層病根：忽略動態轉向誤差】— 靜態模型無法捕捉沉默選民與最後一刻改變想法的共和黨人，也缺乏設備即時運行狀態"
        ],
        theme=theme, accent_key="danger", badge_text="陷阱 L1"
    )
    draw_expansive_card(
        ax, c2_cx, row_y[0], card_w, card_h,
        title="科技防線：資料清理治理與即時數據流",
        bullets=[
            "● 【淺層做法：先洗淨資料再接即時流】— 徹底淘汰未清理的混亂資料與靜態舊模型，改用高速資料庫與感應器即時數據",
            "● 【中層機制：Exadata 與 IBM 系統】— 導入如英國 NHS 之 Oracle Exadata 高速平台，以及 Meridian 換裝之 IBM 即時預測系統",
            "● 【深層價值：動態抽樣誤差校正】— 持續更新底層樣本結構，加入潛在環境誤差校正機制，即時捕捉群體行為轉向訊號"
        ],
        theme=theme, accent_key="primary", badge_text="科技 M1"
    )
    draw_expansive_card(
        ax, c3_cx, row_y[0], card_w, card_h,
        title="可靠產出：醫療降本與機組零意外停擺",
        bullets=[
            "● 【淺層成果：省下巨額預算與停機費】— 乾淨且即時的數據流讓公部門與能源廠能在問題惡化前精準出手干預",
            "● 【中層實證：NHS 省 5.81 億英鎊】— 英國 NHS 即時揪出併用 10 種藥物與過量抗生素病患；Meridian 精準預警發電機組維護",
            "● 【深層護城河：從事後補救轉事前預防】— 串連癌症用藥與慢性病臨床數據，為病患量身打造最省錢且最有效的個人化治療方案"
        ],
        theme=theme, accent_key="success", badge_text="成果 R1"
    )

    # --- ROW 2: CONTEXT DEFICIT & KPI ALIGNMENT (管理維度 × 補足上下文脈絡) ---
    draw_expansive_card(
        ax, c1_cx, row_y[1], card_w, card_h,
        title="脈絡陷阱：忽略外部事件與 KPI 測量迷思",
        bullets=[
            "● 【淺層現象：只看表面熱度被騙倒】— 以為「可測量就該測量」，讓演算法只盯著表面搜尋量或社群點擊率就自動下結論",
            "● 【中層案例：Google 流感與 Twitter】— Google 忽略媒體炒作引發恐慌搜尋而高估疫情；某大企業把 Twitter 提及次數當銷售 KPI",
            "● 【深層病根：表象數字脫離真實業務】— 搜尋量暴增不等於真的生病，社群點擊率也不等於實體展會成交，盲目追蹤只會產出廢線索"
        ],
        theme=theme, accent_key="danger", badge_text="陷阱 L2"
    )
    draw_expansive_card(
        ax, c2_cx, row_y[1], card_w, card_h,
        title="管理防線：目標對齊與外部脈絡調節變數",
        bullets=[
            "● 【淺層做法：鎖定真痛點並校正炒作】— 啟動大數據前先確立商業目標與真 KPI，並把媒體報導等外部事件放進模型當調節開關",
            "● 【中層機制：線上與實體雙軌交叉校準】— 當媒體大幅炒作疫情時自動降權搜尋指標，並拿 CDC 實際就診通報與實體展會業績做對照",
            "● 【深層價值：終結部門資源錯置虛耗】— 確保每一項儀表板指標都直接掛鉤核心營收與真實成效，不再被虛假的社群流量帶偏節奏"
        ],
        theme=theme, accent_key="primary", badge_text="管理 M2"
    )
    draw_expansive_card(
        ax, c3_cx, row_y[1], card_w, card_h,
        title="可靠產出：警力熱點精準部署與高轉化推薦",
        bullets=[
            "● 【淺層成果：每一分資源都打在熱點上】— 結合真實地理脈絡與歷史成交紀錄，讓推薦系統與公共安全部署發揮最大實質效益",
            "● 【中層實證：NYPD 76 轄區與電商推薦】— 紐約警局 CompStat 每週呈現 76 轄區熱點並起訴累犯；Amazon 與 Spotify 提供數百萬筆推薦",
            "● 【深層護城河：精準分眾與雙向共贏】— 川普團隊亦運用大數據針對選民群體量身打造精準廣告訊息，線上比價網更幫消費者找到最低價"
        ],
        theme=theme, accent_key="success", badge_text="成果 R2"
    )

    # --- ROW 3: SPURIOUS CORRELATION & INFERENTIAL PRIVACY (組織與倫理維度 × 領域專家把關) ---
    draw_expansive_card(
        ax, c1_cx, row_y[2], card_w, card_h,
        title="認知與倫理陷阱：假性相關與推論隱私侵害",
        bullets=[
            "● 【淺層現象：巧合當因果、探勘踩紅線】— 演算法把毫無關聯的數字湊成一對，更在用戶不知情下跨資料源拼湊出最私密的個人弱點",
            "● 【中層案例：IE 謀殺率與帕金森氏症】— 2006-2011 美國謀殺率與 IE 市佔率同步下降；企業結合 GPS 與消費推論帕金森氏症早期徵兆",
            "● 【深層病根：黑箱貼標籤且無反擊機制】— 將人自動標記為信貸或健康「高風險者」並操控無意識藍綠偏好，當事人毫無法律程序可自保"
        ],
        theme=theme, accent_key="danger", badge_text="陷阱 L3"
    )
    draw_expansive_card(
        ax, c2_cx, row_y[2], card_w, card_h,
        title="組織防線：領域知識把關與推論隱私界線",
        bullets=[
            "● 【淺層做法：真人專家審因果、設紅線】— 培育具備深厚業務領域知識（Domain Knowledge）的分析團隊，並建立隱私合規審查制度",
            "● 【中層機制：因果檢驗與透明申訴程序】— 由領域專家人工檢驗統計關聯背後的商業與科學機理，嚴禁黑箱演算法直接對個人貼高風險標籤",
            "● 【深層價值：保護核心焦點與公民權益】— 讓組織具備辨識「IE 與謀殺率」假相關的免疫力，同時賦予消費者知情權與演算法抗辯機制"
        ],
        theme=theme, accent_key="primary", badge_text="組織 M3"
    )
    draw_expansive_card(
        ax, c3_cx, row_y[2], card_w, card_h,
        title="可靠產出：可解釋因果決策與永續數位信任",
        bullets=[
            "● 【淺層成果：決策站得住腳且不傷商譽】— 每項大數據建議都經過因果邏輯驗證，同時守住客戶隱私底線，避免引爆法律與公關危機",
            "● 【中層實證：人機協同雙重防禦閉環】— 演算法負責在海量資料中快速篩出細微訊號，人類領域專家負責判斷上下文脈絡與倫理合規性",
            "● 【深層護城河：兼具精準與信任的組織】— 徹底回答「巨量資料有多可靠」：唯有在 MIS 三維治理與倫理護欄下，大數據才真正可靠"
        ],
        theme=theme, accent_key="success", badge_text="成果 R3"
    )

    # --- 3x3 Topological Wiring (Horizontal & Vertical Relational Pills in Corridors) ---
    row_mid_y = [ry + card_h / 2.0 for ry in row_y]
    left_edge_1 = c1_cx + card_w
    right_edge_2 = c2_cx
    left_edge_2 = c2_cx + card_w
    right_edge_3 = c3_cx

    horiz_labels_12 = ["淘汰靜態樣本", "注入外部脈絡", "專家因果審查"]
    horiz_labels_23 = ["驅動即時預警", "精準資源配置", "確立合規信任"]

    for r_i in range(3):
        my = row_mid_y[r_i]
        draw_labeled_arrow(ax, (left_edge_1, my), (right_edge_2, my),
                           label_text=horiz_labels_12[r_i], theme=theme, accent_key="warn")
        draw_labeled_arrow(ax, (left_edge_2, my), (right_edge_3, my),
                           label_text=horiz_labels_23[r_i], theme=theme, accent_key="success")

    # Vertical connectors between rows in each column
    col_mid_x = [c1_cx + card_w / 2.0, c2_cx + card_w / 2.0, c3_cx + card_w / 2.0]
    vert_labels = [
        ["偏見疊加盲點", "失準擴大侵權"],
        ["科技支撐管理", "管理對齊組織"],
        ["基建賦能業務", "效益兼顧倫理"]
    ]
    col_accents = ["danger", "primary", "success"]

    for c_i in range(3):
        mx = col_mid_x[c_i]
        # Row 1 bottom to Row 2 top
        draw_labeled_arrow(ax, (mx, row_y[0]), (mx, row_y[1] + card_h),
                           label_text=vert_labels[c_i][0], theme=theme, accent_key=col_accents[c_i])
        # Row 2 bottom to Row 3 top
        draw_labeled_arrow(ax, (mx, row_y[1]), (mx, row_y[2] + card_h),
                           label_text=vert_labels[c_i][1], theme=theme, accent_key=col_accents[c_i])

    out_path = os.path.join(output_dir, "02_predictive_reliability_architecture.png")
    save_publication_figure(fig, out_path, theme, dpi=240)


if __name__ == "__main__":
    render_master_structure_map()
    render_predictive_reliability_architecture()
