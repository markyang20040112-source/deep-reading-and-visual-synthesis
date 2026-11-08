"""
render_knowledge_diagrams.py
Generates the publication-grade Visual Knowledge Diagrams (Format A):
1. 01_article_master_structure_map.png
2. 02_bicameral_data_architecture.png

Upgraded in full compliance with:
- visual_diagram_matplotlib_spec.md (Ausubel-Sweller Segmenting, Swiss Grid, 88%-92% Horizontal Fill, True Vertical Slot Centering)
- [INS-10] & [INS-12] Expansive Typography (font_pt=12.5pt, Titles=15pt), Rich 2-Line Analytical Bullets (no telegraph over-compression),
  Balanced Central Thesis Spine (no top/bottom central void), and Full 3x3 Topological Wiring.
"""

import sys
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Import unified visual engine
script_dir = os.path.abspath(".agents/skills/deep-reading-and-visual-synthesis/scripts")
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from generate_mindmap import (
    THEMES,
    configure_cjk_fonts,
    draw_macro_zone as draw_expansive_macro_zone,
    draw_modern_card,
    draw_labeled_bezier as draw_expansive_bezier,
    draw_hierarchical_trunk_fork,
    draw_canvas_header_and_footer as draw_expansive_header_and_footer,
    save_publication_figure,
)


def draw_expansive_card(ax, x, y, width, height, title, bullets, theme,
                        accent_key="primary", badge_text=None,
                        fig_width_in=28.0, font_pt=12.2, max_em_override=None):
    return draw_modern_card(
        ax, x, y, width, title, bullets, theme,
        accent_key=accent_key, badge_text=badge_text,
        max_em_width=max_em_override, fixed_height=height,
        fig_width_in=fig_width_in, font_pt=font_pt
    )

configure_cjk_fonts()

output_dir = os.path.abspath("reading_sessions/20261101_企業數據與生成式AI準備度/02_outputs")
os.makedirs(output_dir, exist_ok=True)


# ==============================================================================
# DIAGRAM 1: ARTICLE MASTER STRUCTURE MAP (全景主架構圖 — 由淺入深白話版 + 4主幹階層分塊)
# ==============================================================================
def render_master_structure_map():
    theme = THEMES["swiss_editorial"]
    fig, ax = plt.subplots(figsize=(28, 18.5), dpi=240)
    ax.set_facecolor(theme["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    draw_expansive_header_and_footer(
        ax,
        title="【全景主圖】企業數據資產面對生成式 AI 的準備度與治理策略",
        subtitle="Thomas H. Davenport & Priyanka Tiwari (MIT Sloan / AWS 全球 334 位數據長實證研究) ｜ 由淺入深四階全景結構圖",
        takeaway_title="★ 一句話讀懂核心結論：買了最聰明的 AI 模型，若餵給它雜亂矛盾的內部文件，只會產出更逼真的錯誤答案",
        takeaway_lines=[
            "● 【由淺入深看問題】多數企業砸大錢買 AI（80% 看好），卻只敢讓員工私下試玩、僅 6% 真正上線；因為公司內部高達 80%～90% 的合約與報告從未整理，只靠寫提示詞（Prompt）根本救不了爛資料。",
            "● 【由淺入深看解法】對內必須先幫公司資料建好「標準字典與唯一客戶名冊（左腦）」，再搭配「AI 語境閱讀（右腦）」與「少數難題由專家把關」；對外則先挑「客服草擬」與「寫程式」兩個最安全的部門試水溫。"
        ],
        theme=theme
    )

    # 1. Palmer Macro Zones (4 Macro Regions = Level 1 Chunking <= 4+-1)
    draw_expansive_macro_zone(ax, 3.5, 51.8, 30.8, 38.0, "壹、【表面現象】為什麼大家都在買 AI，真正上線卻只有 6%？", theme, "danger")
    draw_expansive_macro_zone(ax, 3.5, 11.8, 30.8, 38.2, "貳、【深層原因】為什麼只靠「寫提示詞（Prompt）」一定會失敗？", theme, "warn")
    draw_expansive_macro_zone(ax, 65.7, 51.8, 30.8, 38.0, "參、【系統解法】如何用「左右腦分工＋專家把關」管好海量文件？", theme, "success")
    draw_expansive_macro_zone(ax, 65.7, 11.8, 30.8, 38.2, "肆、【行動步驟】如何打破部門推諉，挑對最安全的試點先贏？", theme, "primary")

    # 2. Central Thesis Spine (X: 37.0, W: 26.0, Y: 14.5 ~ 86.5 -> 4 Core Modules = 4 Main Trunks)
    hub_x, hub_y, hub_w, hub_h = 37.0, 14.5, 26.0, 72.0
    hub_box = FancyBboxPatch(
        (hub_x, hub_y), hub_w, hub_h,
        boxstyle="round,pad=0.3,rounding_size=1.3",
        linewidth=2.4, edgecolor=theme["hub_border"], facecolor=theme["hub_bg"], zorder=3
    )
    ax.add_patch(hub_box)

    # Central Hub Header
    ax.text(hub_x + hub_w / 2.0, hub_y + hub_h - 2.3, "【核心主軸】從流沙地基到鋼筋混凝土",
            fontsize=17.2, fontweight="bold", color=theme["hub_text"], ha="center", va="center", zorder=4)
    ax.text(hub_x + hub_w / 2.0, hub_y + hub_h - 5.1, "由淺入深四步拆解：企業如何跨越 AI 落地的「資料準備度赤字」",
            fontsize=11.8, fontweight="bold", color=theme["hub_sub"], ha="center", va="center", zorder=4)
    ax.plot([hub_x + 1.2, hub_x + hub_w - 1.2], [hub_y + hub_h - 6.8, hub_y + hub_h - 6.8],
            color=theme["hub_border"], lw=1.2, alpha=0.8, zorder=3.5)

    # 4 Vertically Centered Core Thesis Modules inside the Central Spine (1-to-1 with 4 Macro Zones)
    spine_modules = [
        ("【第 1 步：看清表面落差】熱潮與現實的斷崖", "#FCA5A5", [
            "過去電腦只管 10% 的數字表格，現在生成式 AI 首度能讀懂",
            "公司裡 80%～90% 的文字報告與錄音；雖然 80% 高管極度看",
            "好並加碼預算，但高達 89% 企業仍卡在員工私下試用階段。"
        ]),
        ("【第 2 步：挖出背後病根】散亂文件無法靠提示詞硬救", "#FCD34D", [
            "公司內部未整理的文字檔每年暴增 50%，高達 46% 數據長坦",
            "言「資料品質太差」是頭號死穴；老師傅的潛規則寫不進提示",
            "詞，不同部門文件又各說各話，硬餵給 AI 只會讓它自信瞎掰。"
        ]),
        ("【第 3 步：建立雙腦分工】標準名冊約束＋專家把關", "#6EE7B7", [
            "把「死板規定」與「靈活閱讀」分開：先用「左腦（統一名詞",
            "字典與唯一客戶主檔）」鎖死事實邊界，再讓「右腦（AI 大模",
            "型）」閱讀長文，最後只把 <5% 有爭議的難題交給真人拍板。"
        ]),
        ("【第 4 步：挑對起點破局】終結部門搶權、從安全區先發", "#93C5FD", [
            "71% 數據長因舊報表還沒整理完而不敢動。企業必須先由高層",
            "拍板「誰對資料真偽負責」，立刻禁止拿髒資料直接訓練模型，",
            "並優先從「客服草擬」與「寫程式」兩個自帶安全網的場景落地。"
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
        # Sub-box inside Central Hub
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

    # 3. Eight Sub-Cards inside the 4 Macro Zones (Each Card: 淺 -> 中 -> 深 3-Step Progression!)
    # Zone 1: Left Top (Danger)
    draw_expansive_card(
        ax, 4.6, 70.5, 28.6, 16.4,
        title="表面熱絡：80% 看好，卻僅 6% 真正上線",
        bullets=[
            "● 【淺層現象：老闆搶著給錢】— 80% 數據長深信生成式 AI 會徹底洗牌產業競爭力，高達 62% 企業已準備加碼投資預算",
            "● 【中層現實：近九成原地踏步】— 高達 89% 公司仍停留在員工零星試玩（33%）、寫使用守則（21%）或小部門測試（19%）",
            "● 【深層警訊：核心業務不敢用】— 真正放進核心業務正式運行的僅有 6%，甚至有 16% 企業因為害怕機密外洩與出錯而全面禁用"
        ],
        theme=theme, accent_key="danger", badge_text="現象一"
    )
    draw_expansive_card(
        ax, 4.6, 52.8, 28.6, 16.4,
        title="頭號卡關：46% 點名「資料太亂」是最大死穴",
        bullets=[
            "● 【淺層現象：大家怪錯地方】— 許多人以為 AI 沒落地是因為模型不夠聰明，但 46% 數據長一致指出「內部資料品質太差」才是首因",
            "● 【中層現實：未整理文件暴增】— 公司裡高達 80%～90% 資料是散亂的文字、信件與錄音（暗數據），且每年以 50% 速度翻倍成長",
            "● 【深層警訊：管理制度沒跟上】— 高達 57% 企業至今沒修改資料管理策略，僅 11% 有把握自家的資料品質能支撐 AI 大規模運作"
        ],
        theme=theme, accent_key="danger", badge_text="現象二"
    )

    # Zone 2: Left Bottom (Warn)
    draw_expansive_card(
        ax, 4.6, 30.5, 28.6, 16.5,
        title="陷阱一：老師傅的潛規則，根本寫不進提示詞",
        bullets=[
            "● 【淺層直覺：有些事只可意會】— 就像騎單車一樣，「人類心裡懂的潛規則，遠比能用文字寫出來的多」（波蘭尼默會知識悖論）",
            "● 【中層情境：給範例只管八成】— 在提示詞（Prompt）裡塞幾份標準範例，只能應付 80% 日常文件，遇到歷史特例與部門默契就失靈",
            "● 【深層風險：不懂裝懂最致命】— 面對剩下 20% 罕見的特殊合約，大模型不會承認看不懂，反而會自信滿滿地硬套範本給出錯誤結論"
        ],
        theme=theme, accent_key="warn", badge_text="失敗根因一"
    )
    draw_expansive_card(
        ax, 4.6, 12.8, 28.6, 16.5,
        title="陷阱二：單篇讀得懂，合在一起卻各說各話",
        bullets=[
            "● 【淺層直覺：看單篇都很合理】— AI 讀單份合約抓重點可達 98% 準確，但它無法自己判斷全公司 10 萬份檔案裡誰說的才算數",
            "● 【中層情境：同名不同人亂成團】— A 部門寫「台積電」、B 部門寫「TSMC」、C 檔案寫舊信用額度，缺乏統一客戶主檔（MDM）就會算錯帳",
            "● 【深層風險：硬塞表格反失真】— 若為了省事把客訴錄音強行壓成「類別：退貨」兩格死板表格，反而抹殺了客戶語氣急迫度與訴訟前兆"
        ],
        theme=theme, accent_key="warn", badge_text="失敗根因二"
    )

    # Zone 3: Right Top (Success)
    draw_expansive_card(
        ax, 66.8, 70.5, 28.6, 16.4,
        title="左腦管規矩：先建「統一字典」與「可信度標籤」",
        bullets=[
            "● 【淺層做法：統一全公司稱呼】— 先編一本全公司共用的「標準業務字典（本體詞庫 Ontology）」，規定產品代碼與部門名詞不准亂叫",
            "● 【中層做法：鎖定唯一正確版本】— 建立「唯一真實名冊（主數據 MDM）」，當會議紀錄與正式合約金額衝突時，強制以正式合約為準",
            "● 【深層做法：幫每份文件貼身分證】— 效法默克與賽諾菲藥廠，為每份報告貼上「生效日期、作者權威度與誰能看」標籤（後設資料層）"
        ],
        theme=theme, accent_key="success", badge_text="解法一"
    )
    draw_expansive_card(
        ax, 66.8, 52.8, 28.6, 16.4,
        title="右腦讀語意＋專家把關：只審 5% 有爭議的難題",
        bullets=[
            "● 【淺層做法：保留原文豐富語氣】— 不把長文硬壓成死板表格，而是讓 AI 右腦保留整段文字的上下文脈絡（高維語義向量）來做智慧搜尋",
            "● 【中層做法：設一道 90 分安全門】— AI 有 90% 以上把握的常規文件（約佔 95%）自動放行；遇到沒見過的新名詞或矛盾才攔下來",
            "● 【深層做法：專家審核反哺字典】— 效法摩根士丹利花 5 年為報告打分；真人專家只需審核 <5% 難題，每判完一題就自動更新回左腦字典"
        ],
        theme=theme, accent_key="success", badge_text="解法二"
    )

    # Zone 4: Right Bottom (Primary)
    draw_expansive_card(
        ax, 66.8, 30.5, 28.6, 16.5,
        title="組織破局：別再觀望，先敲定「誰對資料負責」",
        bullets=[
            "● 【淺層痛點：七成主管不敢動】— 高達 71% 數據長坦言還在忙傳統數位轉型舊債，因為怕 AI 回答出錯惹上官司而不敢跨出第一步",
            "● 【中層做法：終結四頭馬車搶權】— 召集數據長（CDO）、資訊長與技術長簽立權責表（RACI），明定由數據長掌握「資料真偽最終審定權」",
            "● 【深層鐵律：立刻禁止拿髒資料微調】— 嚴禁各部門把還沒清理、沒標註日期的內部雜亂文件直接灌進大模型微調，避免把錯誤永久烤進腦子裡"
        ],
        theme=theme, accent_key="primary", badge_text="行動一"
    )
    draw_expansive_card(
        ax, 66.8, 12.8, 28.6, 16.5,
        title="安全試點：先挑「客服草擬」與「寫程式」開局",
        bullets=[
            "● 【淺層原則：別拿財務法務當白老鼠】— 第一仗絕對不要碰錯一個字就會賠大錢的財報或臨床數據，要挑「自帶安全防護網」的部門先做",
            "● 【首選戰場一：客服人員的草稿助手】— 讓 AI 先查資料寫好回覆草稿，由真人客服看過再按發送（真人就是天然防火牆），立省 30% 找資料時間",
            "● 【首選戰場二：軟體工程師寫程式】— 像環球音樂一樣讓 AI 輔助寫程式碼，因為電腦編譯器（Compiler）一跑就知道能不能動，一秒驗出對錯"
        ],
        theme=theme, accent_key="primary", badge_text="行動二"
    )

    # 4. Hierarchical 4-Trunk -> 2-Subcard Forks (Strictly obeying 4 -> 2 -> 3 Chunking!)
    # Trunk 1 (Module 1 -> Zone 1 Cards)
    draw_hierarchical_trunk_fork(ax, (hub_x, module_centers_y[0]), (33.2, 78.7), (33.2, 61.0), "壹、現況落差", theme=theme, accent_key="danger")
    # Trunk 2 (Module 2 -> Zone 2 Cards)
    draw_hierarchical_trunk_fork(ax, (hub_x, module_centers_y[1]), (33.2, 38.7), (33.2, 21.0), "貳、深層病因", theme=theme, accent_key="warn")
    # Trunk 3 (Module 3 -> Zone 3 Cards)
    draw_hierarchical_trunk_fork(ax, (hub_x + hub_w, module_centers_y[2]), (66.8, 78.7), (66.8, 61.0), "參、雙腦分工", theme=theme, accent_key="success")
    # Trunk 4 (Module 4 -> Zone 4 Cards)
    draw_hierarchical_trunk_fork(ax, (hub_x + hub_w, module_centers_y[3]), (66.8, 38.7), (66.8, 21.0), "肆、落地步驟", theme=theme, accent_key="primary")

    out_png = os.path.join(output_dir, "01_article_master_structure_map.png")
    save_publication_figure(fig, out_png, theme, dpi=240)
    print(f"[OK] Diagram 1 generated at {out_png}")


# ==============================================================================
# DIAGRAM 2: BICAMERAL DATA ARCHITECTURE & GOVERNANCE PIPELINE (專題拓撲圖 — 由淺入深白話版)
# ==============================================================================
def render_bicameral_architecture_map():
    theme = THEMES["mckinsey_executive"]
    fig, ax = plt.subplots(figsize=(28, 18.5), dpi=240)
    ax.set_facecolor(theme["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    draw_expansive_header_and_footer(
        ax,
        title="【專題圖譜】企業資料「左右腦分工」與安全落地三層流程圖",
        subtitle="Bicameral Cognitive Data Architecture & Governance Pipeline ｜ 由淺入深看懂：如何讓 AI 既能讀懂長文、又不會胡說八道",
        takeaway_title="★ 一句話讀懂這張架構圖：用「左腦的死規矩」管住「右腦的活聯想」，中間再放一位「真人裁判」專門處理少數難題",
        takeaway_lines=[
            "● 【橫向看三層怎麼配合】第 1 層「先對齊全公司名詞字典」× 第 2 層「抓出跨文件矛盾交給專家拍板」× 第 3 層「過濾掉過期與無權限檔案後，才讓 AI 回答問題或支援客服與寫程式」。",
            "● 【縱向看系統怎麼越用越聰明】左腦由上往下提供 100% 準確的名詞、客戶主檔與安全權限；中軸把 <5% 罕見難題交給專家裁決並回頭更新字典；右腦則在安全邊界內幫全公司快速讀懂海量報告。"
        ],
        theme=theme
    )

    # Three Macro Columns (Left X: 3.5~31.5, Mid X: 36.0~64.0, Right X: 68.5~96.5)
    draw_expansive_macro_zone(ax, 3.5, 11.8, 28.2, 78.0, "【剛性左腦】管規矩與唯一事實（100% 不准瞎掰）", theme, "primary")
    draw_expansive_macro_zone(ax, 35.9, 11.8, 28.2, 78.0, "【中間裁判】自動檢查哨＋真人專家把關（攔截 5% 難題）", theme, "warn")
    draw_expansive_macro_zone(ax, 68.3, 11.8, 28.2, 78.0, "【靈性右腦】讀懂長文語氣與智慧搜尋（高效率理解）", theme, "success")

    # Row Y coordinates: Row 1 (65.8, H=19.8), Row 2 (39.8, H=19.8), Row 3 (13.5, H=20.0)
    # --- LEFT BRAIN CARDS ---
    draw_expansive_card(
        ax, 4.5, 65.8, 26.2, 19.8,
        title="第 1 層左腦：全公司統一字典 (Ontology)",
        bullets=[
            "● 【淺層概念：先統一大家講的話】— 就像編一本公司專屬字典，把各部門各叫各的產品代號、職稱與業務縮寫全部對齊成標準名稱",
            "● 【中層做法：只准從字典裡選詞】— 規定 AI 在整理文件貼標籤時，只能從這本審核過的標準字典裡挑詞，不准它自己發明新名詞",
            "● 【深層價值：跨國跨部門不再雞同鴨講】— 全球分公司的在地文件都能自動對應到同一個標準概念（目前已有 18% 領先企業正積極編纂）"
        ],
        theme=theme, accent_key="primary", badge_text="標準字典", font_pt=11.8
    )
    draw_expansive_card(
        ax, 4.5, 39.8, 26.2, 19.8,
        title="第 2 層左腦：唯一真實客戶名冊 (MDM)",
        bullets=[
            "● 【淺層概念：認出誰跟誰是同一家】— 自動認出合約裡的「台積電」、信件裡的「TSMC」與報表裡的「3nm 專案組」其實是同一個客戶",
            "● 【中層做法：檔案打架時誰說了算】— 當業務會議紀錄寫的折扣跟法務正式合約不一致時，系統強制規定「以正式合約主檔為唯一準則」",
            "● 【深層價值：每筆資料都查得到源頭】— 完整記錄每個數字與結論是從哪個部門、哪一天、哪份檔案來的（資料血緣），隨時都能驗算查核"
        ],
        theme=theme, accent_key="primary", badge_text="唯一事實", font_pt=11.8
    )
    draw_expansive_card(
        ax, 4.5, 13.5, 26.2, 20.0,
        title="第 3 層左腦：文件的身分證與評分卡 (Metadata)",
        bullets=[
            "● 【淺層概念：幫每份文件打品質分數】— 效法摩根士丹利做法，由專家幫內部研究報告打上「可信度分數與完整度等級」，好壞一目了然",
            "● 【中層做法：過期作廢檔案自動下架】— 每份文件強制貼上「生效日與作廢日」，一旦舊法規或舊產品規格過期，立刻禁止 AI 拿出來引用",
            "● 【深層價值：沒權限的人絕對搜不到】— 在 AI 搜尋之前先檢查提問者的職級權限（RBAC），徹底解決 16% 企業怕機密被員工問出來的恐懼"
        ],
        theme=theme, accent_key="primary", badge_text="安全過濾", font_pt=11.8
    )

    # --- MIDDLE PREFRONTAL / PIPELINE CARDS ---
    draw_expansive_card(
        ax, 36.9, 65.8, 26.2, 19.8,
        title="第 1 層裁判：雙腦自動檢查哨 (Validation Gate)",
        bullets=[
            "● 【淺層概念：AI 讀完先對一下字典】— 右腦 AI 剛從長文抓出重點時，不能直接入庫，必須先拿到左腦的標準字典前面逐項核對",
            "● 【中層做法：90 分以上才准自動通關】— 設定 90% 把握度門檻：95% 清楚明白的日常文件自動放行入庫；只要信心低於 90% 立刻亮紅燈攔截",
            "● 【深層價值：鎖死輸出格式防偷渡】— 用嚴格的欄位格式（Schema）綁住 AI 的回答結構，防止它寫出看似通順、實則答非所問的模糊句子"
        ],
        theme=theme, accent_key="warn", badge_text="自動把關", font_pt=11.8
    )
    draw_expansive_card(
        ax, 36.9, 39.8, 26.2, 19.8,
        title="第 2 層裁判：真人專家拍板迴路 (HITL)",
        bullets=[
            "● 【淺層概念：好鋼用在刀刃上】— 資深業務與法務專家不必笨到去重讀 10 萬份舊檔案，只需專心審查被檢查哨攔下來的 <5% 罕見難題",
            "● 【中層做法：專家判一題、系統學一題】— 專家每次拍板決定「哪份合約才對」，系統就立刻把這條新規定寫回左腦字典，並當成右腦的新範例",
            "● 【深層價值：防止 AI 吃到自己掰的假話】— 嚴格禁止未經真人審核的 AI 生成內容直接流回知識庫（防範模型自噬），確保公司知識庫越用越純淨"
        ],
        theme=theme, accent_key="warn", badge_text="專家仲裁", font_pt=11.8
    )
    draw_expansive_card(
        ax, 36.9, 13.5, 26.2, 20.0,
        title="第 3 層裁判：自帶安全網的兩大試點 (Safe MVP)",
        bullets=[
            "● 【淺層概念：先在有防護網的地方練兵】— 系統建好後，先挑「就算 AI 寫錯一點點，也不會直接害公司賠錢」的兩個安全場景上線實測",
            "● 【試點一：幫真人客服先寫回覆草稿】— AI 查完資料先擬好答案，真人客服檢查無誤才按發送（真人就是最後防線），直接省下 30% 翻找時間",
            "● 【試點二：幫軟體工程師寫程式碼】— AI 寫完程式碼後，電腦編譯器與自動測試一秒就能驗出能不能跑，在 90 天內安全跑通整套管理流程"
        ],
        theme=theme, accent_key="warn", badge_text="安全試點", font_pt=11.8
    )

    # --- RIGHT BRAIN CARDS ---
    draw_expansive_card(
        ax, 69.3, 65.8, 26.2, 19.8,
        title="第 1 層右腦：讀懂整段話的弦外之音 (Embeddings)",
        bullets=[
            "● 【淺層概念：不把文章切碎塞進死格子】— 放棄把客訴錄音硬壓成「退貨」兩個字的舊做法，完整保留整段話的語氣急迫度與前因後果",
            "● 【中層做法：用意思相近來找資料】— 將文字轉成代表語意的數學座標（高維向量），就算客戶沒講出標準專有名詞，也能精準搜出相關解答",
            "● 【深層價值：再活潑的聯想都有掛牌】— 每一段語意座標都強制綁定左腦的「標準客戶代號」與「文件身分證」，既能靈活聯想又不會張冠李戴"
        ],
        theme=theme, accent_key="success", badge_text="語境保留", font_pt=11.8
    )
    draw_expansive_card(
        ax, 69.3, 39.8, 26.2, 19.8,
        title="第 2 層右腦：看幾個好範例就能大量閱讀 (ICL)",
        bullets=[
            "● 【淺層概念：不用從頭重訓練大模型】— 只要給 AI 看 3～5 份由專家挑選出來的「黃金標準範例（Few-Shot）」，它就能學會怎麼抓重點",
            "● 【中層做法：每天自動初篩上萬份文件】— 讓 AI 先當初級助理，每天自動掃描成千上萬份會議紀錄與報告，抓出初步重點送去中間檢查哨",
            "● 【深層價值：主動幫公司發現新業務名詞】— 當 AI 發現最近幾百封客訴裡頻繁出現某個字典裡沒有的新詞時，會主動打包提醒專家要不要收錄"
        ],
        theme=theme, accent_key="success", badge_text="大量初篩", font_pt=11.8
    )
    draw_expansive_card(
        ax, 69.3, 13.5, 26.2, 20.0,
        title="第 3 層右腦：有憑有據的企業智慧問答 (GraphRAG)",
        bullets=[
            "● 【淺層概念：規定 AI 只能看認證資料回答】— 員工提問時，AI 不准憑印象亂猜，必須同時翻開「左腦的標準關係圖」與「右腦的原文段落」來作答",
            "● 【中層做法：自動附上出處與日期備查】— 只把通過時效檢查、高評分且提問者有權限看的文件餵給 AI，且每句回答都附上原始合約頁碼供查證",
            "● 【深層價值：全公司員工都能安全問數據】— 真正實現默克（Merck）與賽諾菲藥廠的願景，讓第一線業務不用懂技術也能隨時獲得可靠決策支援"
        ],
        theme=theme, accent_key="success", badge_text="可靠問答", font_pt=11.8
    )

    # --- COMPLETE 3x3 TOPOLOGICAL CONNECTORS (Horizontal & Vertical Corridors) ---
    # Row 1 Horizontal: Left -> Mid <- Right
    draw_expansive_bezier(ax, (30.7, 75.7), (36.9, 75.7), "字典標準核對", theme=theme, accent_key="primary")
    draw_expansive_bezier(ax, (69.3, 75.7), (63.1, 75.7), "語意座標掛載", theme=theme, accent_key="success")

    # Row 2 Horizontal: Left <-> Mid <-> Right
    draw_expansive_bezier(ax, (30.7, 49.7), (36.9, 49.7), "拍板更新名冊", theme=theme, accent_key="primary")
    draw_expansive_bezier(ax, (69.3, 49.7), (63.1, 49.7), "初篩難題送審", theme=theme, accent_key="success")

    # Row 3 Horizontal: Left -> Mid -> Right
    draw_expansive_bezier(ax, (30.7, 23.5), (36.9, 23.5), "權限時效放行", theme=theme, accent_key="primary")
    draw_expansive_bezier(ax, (63.1, 23.5), (69.3, 23.5), "安全推廣全企", theme=theme, accent_key="warn")

    # Vertical Pipeline Connectors across Rows 1 -> 2 -> 3
    # Left Column Vertical
    draw_expansive_bezier(ax, (17.6, 65.8), (17.6, 59.6), "第1步：統一稱呼", theme=theme, accent_key="primary")
    draw_expansive_bezier(ax, (17.6, 39.8), (17.6, 33.5), "第2步：貼上標籤", theme=theme, accent_key="primary")
    # Middle Column Vertical
    draw_expansive_bezier(ax, (50.0, 65.8), (50.0, 59.6), "攔下 <5% 難題", theme=theme, accent_key="warn")
    draw_expansive_bezier(ax, (50.0, 39.8), (50.0, 33.5), "安全場景實測", theme=theme, accent_key="warn")
    # Right Column Vertical
    draw_expansive_bezier(ax, (82.4, 65.8), (82.4, 59.6), "保留語境初篩", theme=theme, accent_key="success")
    draw_expansive_bezier(ax, (82.4, 39.8), (82.4, 33.5), "有憑有據回答", theme=theme, accent_key="success")

    out_png = os.path.join(output_dir, "02_bicameral_data_architecture.png")
    save_publication_figure(fig, out_png, theme, dpi=240)
    print(f"[OK] Diagram 2 generated at {out_png}")


if __name__ == "__main__":
    render_master_structure_map()
    render_bicameral_architecture_map()
