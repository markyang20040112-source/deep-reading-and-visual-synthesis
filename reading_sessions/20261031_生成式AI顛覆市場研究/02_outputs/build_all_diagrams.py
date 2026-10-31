# -*- coding: utf-8 -*-
"""
build_all_diagrams.py
Generates 3 publication-grade visual knowledge diagrams for the session:
1. 01_生成式AI顛覆市場研究_四大機會與核心實務圖.jpg (T5: Swiss Hub-and-Spoke, swiss_editorial)
2. 02_生成式AI市調局限_實驗混淆與四大前沿解法思辨圖.jpg (T4: Comparative Dual-Zone Matrix, nature_academic)
3. 03_三篇合體_顧客價值與AI數據科學決策終極藍圖.jpg (T2: 3-Stage Left-to-Right Pipeline, mckinsey_executive)
"""

import os
import re
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Add skill scripts directory to path
SCRIPT_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\.agents\skills\deep-reading-and-visual-synthesis\scripts"
sys.path.insert(0, SCRIPT_DIR)

import generate_mindmap as gm
from generate_mindmap import (
    THEMES,
    configure_cjk_fonts,
    char_visual_width,
    draw_macro_zone,
    draw_modern_card,
    draw_labeled_bezier,
    draw_labeled_arrow,
    draw_canvas_header_and_footer,
    save_publication_figure,
)

# Enhance local text wrapping in session memory (without touching skill files)
# so English words are never split mid-word and CJK closing punctuation never starts a line.
NO_START_CHARS = set("，。、；：？！）」』】》〉—…,.!?;:)]}%‰")


def smart_wrap_cjk_text(text, max_em_width=24.0, hanging_indent="   "):
    # Tokenize numbers with commas (e.g. 1,000+), English words/numbers, or single CJK characters
    tokens = re.findall(r"\d+(?:,\d+)+\+?|[A-Za-z0-9_.\-+%/]+|.", text)
    lines = []
    current_line = ""
    current_w = 0.0

    for tok in tokens:
        if tok == "\n":
            lines.append(current_line)
            current_line = hanging_indent
            current_w = sum(char_visual_width(c) for c in hanging_indent)
            continue

        tok_w = sum(char_visual_width(c) for c in tok)
        # Allow closing punctuation to stay on the current line even if slightly over max_em_width
        is_closing_punct = (len(tok) == 1 and tok in NO_START_CHARS)

        if current_w + tok_w > max_em_width and current_line.strip() and not is_closing_punct:
            lines.append(current_line)
            current_line = hanging_indent + tok.lstrip()
            current_w = sum(char_visual_width(c) for c in current_line)
        else:
            current_line += tok
            current_w += tok_w

    if current_line.strip():
        lines.append(current_line)
    return lines


gm.wrap_cjk_text = smart_wrap_cjk_text

OUT_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI顛覆市場研究\02_outputs"
os.makedirs(OUT_DIR, exist_ok=True)


def build_diagram_1():
    """
    Diagram 1: Core Article Overview (T5: Swiss Hub-and-Spoke, Theme: swiss_editorial)
    """
    configure_cjk_fonts()
    theme = THEMES["swiss_editorial"]
    fig, ax = plt.subplots(figsize=(28, 18.5))
    fig.patch.set_facecolor(theme["canvas_bg"])
    ax.set_facecolor(theme["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    draw_canvas_header_and_footer(
        ax,
        title="《生成式 AI 正在顛覆市場研究》核心實務與數據結構心智圖 (篇一)",
        subtitle="4 大核心能力 × 3 大市調階段 × AI 訪談員消除心理道德修飾 × 三類數據結構與大小模型權衡 × 顧客數位雙生",
        takeaway_title="★ 核心洞見：生成式 AI 讓市場研究同時兼顧「量化調查的廣度」與「質化訪談的深度」，將市調從少數專案變成全天候智慧引擎",
        takeaway_body="透過動態追問消除人類受訪者的「心理與道德修飾偏誤」，並藉由「內部私有數據微調大型公開模型」兼顧企業機密與非結構化質化語意理解。",
        theme=theme,
    )

    # Central Hub (X: 37.5~62.5, Y: 43.5~59.0)
    hub_x, hub_y, hub_w, hub_h = 37.5, 43.5, 25.0, 15.5
    hub_box = FancyBboxPatch(
        (hub_x, hub_y), hub_w, hub_h,
        boxstyle="round,pad=0.3,rounding_size=1.3",
        facecolor=theme["hub_bg"], edgecolor=theme["hub_border"],
        linewidth=2.4, zorder=4
    )
    ax.add_patch(hub_box)
    ax.text(
        hub_x + hub_w / 2, hub_y + hub_h - 2.6,
        "生成式 AI 顛覆市場研究",
        fontsize=16.5, fontweight="bold", color=theme["hub_text"],
        ha="center", va="top", zorder=5
    )
    ax.text(
        hub_x + hub_w / 2, hub_y + hub_h - 6.0,
        "How Gen AI Is Transforming\nMarket Research (Korst et al.)",
        fontsize=10.2, fontweight="bold", color=theme["hub_sub"],
        ha="center", va="top", zorder=5
    )
    ax.text(
        hub_x + hub_w / 2, hub_y + 2.2,
        "● 4 大核心能力：統整 / 編碼 / 互動 / 寫作\n● 4 大機會：強化 / 取代 / 填補缺口 / 創新見解\n● GBK 調查：45% 已採用、45% 規畫中",
        fontsize=9.4, color="#E2E8F0",
        ha="center", va="bottom", zorder=5
    )

    # Macro Zones (Left & Right)
    draw_macro_zone(ax, 3.5, 13.0, 30.5, 76.0, "【左翼】強化現有實務與合成數據取代實務", theme)
    draw_macro_zone(ax, 66.0, 13.0, 30.5, 76.0, "【右翼】三類數據結構拆解與數位雙生新見解", theme)

    # Left Top Card: 機會① 強化現有實務 & AI 訪談員
    c_lt = draw_modern_card(
        ax, x=4.8, y=54.0, width=27.9,
        title="強化現有實務與 AI 動態訪談員",
        badge_text="機會 1",
        accent_key="primary",
        max_em_width=28.5,
        bullets=[
            "● 4大能力×3大階段：在「設計研究、蒐集分析、撰寫報告」全面加速（62%統整逐字稿、58%分析、54%寫報告）",
            "● Outset.ai 動態訪談平台：依受訪者前次回答動態追問，結合「量化問卷規模」與「質化訪談深度」（兩者兼得）",
            "● 消除「心理與道德修飾機制」（WeightWatchers 實證）：真人面對真人訪談員會啟動道德與面子修飾（社會期許偏誤）；面對無道德批判的 AI 反而更坦誠，且 AI 僅負責提問故幾乎無幻覺"
        ],
        theme=theme
    )

    # Left Bottom Card: 機會② 取代現有實務 & 機會③ 填補缺口
    c_lb = draw_modern_card(
        ax, x=4.8, y=15.5, width=27.9,
        title="合成數據 (Synthetic Data) 取代與補缺口",
        badge_text="機會 2 & 3",
        accent_key="warn",
        max_em_width=28.5,
        bullets=[
            "● 合成數據定義：由 AI 模擬真人行為與偏好（81% 受訪者已用或計畫使用，但僅 31% 認為現階段價值極高）",
            "● 提升品質三關鍵：① 提示詞輸入問答範例（Few-shot）、② 從過去研究知識庫提取內容（RAG）、③ 微調參數對齊現有數據",
            "● 黃金雙盲實證（Evidenza × 安永 EY）：模擬 1,000+ 名「營收逾 10 億美元公司 CEO」填問卷，與真人執行長結論高達 95% 相同",
            "● 填補決策缺口：通用磨坊（General Mills）加速新產品發想；Arena 協助零售商依各門市客群量身打造商品"
        ],
        theme=theme
    )

    # Right Top Card: 關鍵概念拆解：三類數據結構 × 大小模型權衡
    c_rt = draw_modern_card(
        ax, x=67.3, y=52.0, width=27.9,
        title="三類數據結構 × 私有小模型 vs. 公開大模型",
        badge_text="核心概念拆解",
        accent_key="synth",
        max_em_width=28.5,
        bullets=[
            "● 結構化數據（表格欄列）：含「數字型（年齡/消費額）」與「類別型（性別/會員等級/滿意度選項）」",
            "● 半結構化數據（自帶標籤階層）：如網站點擊流 JSON 日誌、客服工單紀錄（長短不一但具欄位標籤）",
            "● 非結構化／質化數據：訪談逐字稿、社群長文、語氣與情緒脈絡（回答 Why 與 How，如威斯康辛商學院與 Synthetic Users 合成訪談）",
            "● 模型權衡：小型私有模型（如 Rockfish Data，美國陸軍採用）完全保密但僅懂結構化/半結構化機率；公開大模型具人類世界知識先驗，方能處理質化數據（最佳折衷：用內部數據微調大模型）"
        ],
        theme=theme
    )

    # Right Bottom Card: 機會④ 創造新型態見解：顧客數位雙生
    c_rb = draw_modern_card(
        ax, x=67.3, y=15.5, width=27.9,
        title="顧客數位雙生 (Digital Twins) 虛擬分身",
        badge_text="機會 4",
        accent_key="success",
        max_em_width=28.5,
        bullets=[
            "● 打破「第一印象只有一次機會」鐵律：為個別客戶打造永不疲勞、不煩躁的虛擬分身，事前演練銷售話術與測試行銷素材（逾 82% 已實驗或計畫實驗）",
            "● 商業實戰：Arena 訓練 B2B 業務、CivicSync 經授權追蹤線上行為建雙生、奧美測試廣告共鳴、NotebookLM 打造個人化研究助理（Oleria 案例）",
            "● 學術基準事實群組（Ground Truth）：哥倫比亞商學院建 2,500 名真人全維度數位雙生；史丹福 + DeepMind 以數小時訪談建雙生，兩週後重測相似度達 85%（與真人自身重測相當）"
        ],
        theme=theme
    )

    # Bezier Connectors with Novak Relational Pills
    draw_labeled_bezier(
        ax,
        (hub_x, hub_y + hub_h * 0.72),
        (c_lt[0] + c_lt[2], c_lt[1] + c_lt[3] * 0.5),
        label_text="動態追問 × 卸下道德心防",
        theme=theme, accent_key="primary", width=2.2
    )
    draw_labeled_bezier(
        ax,
        (hub_x, hub_y + hub_h * 0.28),
        (c_lb[0] + c_lb[2], c_lb[1] + c_lb[3] * 0.5),
        label_text="合成受眾 × 95% 雙盲驗證",
        theme=theme, accent_key="warn", width=2.2
    )
    draw_labeled_bezier(
        ax,
        (hub_x + hub_w, hub_y + hub_h * 0.72),
        (c_rt[0], c_rt[1] + c_rt[3] * 0.5),
        label_text="資料結構 × 隱私與語意權衡",
        theme=theme, accent_key="synth", width=2.2
    )
    draw_labeled_bezier(
        ax,
        (hub_x + hub_w, hub_y + hub_h * 0.28),
        (c_rb[0], c_rb[1] + c_rb[3] * 0.5),
        label_text="個體虛擬分身 × 事前演練",
        theme=theme, accent_key="success", width=2.2
    )

    out_path = os.path.join(OUT_DIR, "01_生成式AI顛覆市場研究_四大機會與核心實務圖.jpg")
    save_publication_figure(fig, out_path, theme, dpi=240)


def build_diagram_2():
    """
    Diagram 2: Deep Methodological Critique (T4: Comparative Dual-Zone Matrix, Theme: nature_academic)
    """
    configure_cjk_fonts()
    theme = THEMES["nature_academic"]
    fig, ax = plt.subplots(figsize=(28, 18.5))
    fig.patch.set_facecolor(theme["canvas_bg"])
    ax.set_facecolor(theme["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    draw_canvas_header_and_footer(
        ax,
        title="《生成式 AI 正在顛覆市場研究》實驗混淆機制與四大前沿解法批判圖 (篇二)",
        subtitle="盲測訂價「混淆現象 (Confounding)」拆解 × 提示詞「挖東牆補西牆」困境 × 四大根本解法之理論死穴 × 情境權變配置",
        takeaway_title="★ 方法論總結：所有模型皆有缺陷（All Models Are Wrong, But Some Are Useful）—— 放棄尋找萬能單一模型，建立「情境權變組合」",
        takeaway_body="早期發想用「數位雙生＋歷史微調」衝速度；常規追蹤用「右腦 AI 轉譯＋左腦統計模型」防幻覺；高風險定價、多感官體驗與突破性創新則強制回歸「真人隨機盲測」！",
        theme=theme,
    )

    # Left Macro Zone: 三大局限與結構性困境
    draw_macro_zone(
        ax, 3.5, 12.5, 43.5, 76.5,
        "【左區：AI 市調三大結構局限】為何盲測與感官實驗在 AI 身上會失靈？",
        theme
    )
    # Right Macro Zone: 四大前沿解法 vs. 四大死穴批判與權變配置
    draw_macro_zone(
        ax, 53.0, 12.5, 43.5, 76.5,
        "【右區：破局與批判】四大前沿解法之「理論死穴」與情境權變組合",
        theme
    )

    # Left Card 1: 局限① 人口偏誤與時間飄移 + 局限③ 多感官失靈
    l1 = draw_modern_card(
        ax, x=5.0, y=64.0, width=40.5,
        title="人口樣本偏誤、時間不穩定與「多感官失靈」",
        badge_text="局限 1 & 3",
        accent_key="danger",
        max_em_width=41.5,
        bullets=[
            "● 人口代表性偏誤（哥倫比亞/史丹福 2023）：OpenAI 等公開模型觀點明顯偏向「自由派、高學歷人士」，難以代表 65 歲以上或虔誠宗教群體（源自訓練數據與人類對齊微調偏誤）",
            "● 提示脆弱與時間不穩定（范登堡 Bisbee 2024）：合成民調回答變異過小，極易受選擇題「選項順序與用字遣詞」影響，且在 3 個月期間內表現搖擺不穩定",
            "● 多感官與情緒反應失靈（高砂香料 Takasago 實證）：香氣嗅覺偏好緊密綁定人類個體生理經歷與潛意識情緒，純文字訓練之 AI 無法模擬真實感官反應"
        ],
        theme=theme
    )

    # Left Card 2: 局限② 盲測訂價實驗之「混淆現象 (Confounding)」深度拆解
    l2 = draw_modern_card(
        ax, x=5.0, y=38.0, width=40.5,
        title="盲測訂價實驗之「混淆現象 (Confounding)」機制",
        badge_text="局限 2 核心拆解",
        accent_key="warn",
        max_em_width=41.5,
        bullets=[
            "● 真人隨機盲測（其他條件不變 X 獨立於 Z）：只調高測試商品價格 X（如 1,000 → 5,000 元），真人心中對外界物價與競品價格 Z 認知不變 → 畫出正常向下傾斜之需求曲線",
            "● AI 語境腦補引發「混淆（Confounding）」：AI 學習的是上下文條件機率 P(Y|X)，無法將高價 X 視為隨機抽樣！看到標價 5,000 元時，AI 在隱空間自動同步調高混淆變數 Z（「腦補歷史價格與店內其他競品也全都賣 5,000 元」）",
            "● 災難後果：混淆變數 Z 同時連動自變數 X（價格）與應變數 Y（購買意願），抵銷了漲價痛感，導致無論定價高低 AI 都回答「合理會買」，需求曲線完全平坦失真！"
        ],
        theme=theme
    )

    # Left Card 3: 為何純靠「寫更詳細的提示詞」會淪為「挖東牆補西牆」？
    l3 = draw_modern_card(
        ax, x=5.0, y=14.5, width=40.5,
        title="為何純靠「詳細提示詞規範」會淪為挖東牆補西牆？",
        badge_text="結構性死胡同",
        accent_key="danger",
        max_em_width=41.5,
        bullets=[
            "● 東牆（未知腦補變數永遠鎖不完）：鎖死「歷史價與競品價」後，AI 又會偷偷腦補「大缺貨、巨星代言或限量溢價」，數千億參數的隱性聯想無法靠人工事前窮舉",
            "● 西牆（寫太白引發「需求特徵劇透」與「焦點錯覺」）：若在 Prompt 刻意強調「別家都賣 1,200、只有這家賣 5,000」，等於明示 AI 拒買，使 AI 從「過度遲鈍」跳到「過度理性的比大小計算機」，依然測不出真實人類的價格彈性"
        ],
        theme=theme
    )

    # Right Card 1: 四大根本解法 vs. 使用者一針見血之「四大理論死穴」批判
    r1 = draw_modern_card(
        ax, x=54.5, y=54.5, width=40.5,
        title="四大前沿破局解法 vs. 您的「四大理論死穴」批判",
        badge_text="方法論交鋒",
        accent_key="primary",
        max_em_width=41.5,
        bullets=[
            "● 解法① 綁定真人記憶之數位雙生 → 【死穴批判：具身認知不可壓縮】無法「真的把一整個人塞進模型」！文字訪談錄無法編碼生理嗅覺、味覺與潛意識記憶（如高砂香料困境）",
            "● 解法② 右腦 AI 轉譯＋左腦統計公式 → 【死穴批判：模型誤設偏誤】雖最能防幻覺，但遇高度複雜非線性問題時，左腦極難寫出高解釋力函式（寫簡單 R² 低、寫複雜又過度配適）",
            "● 解法③ 少量真人＋大量 AI 統計校準 (PPI) → 【死穴批判：分布偏移與湊巧對齊】極不穩定！當下對準人類可能只是湊巧，一旦問題換字眼或跨時間（如 Bisbee 3 個月研究）又再發幻覺",
            "● 解法④ 大量歷史數據微調訓練 → 【死穴批判：後照鏡外推失靈】對過去內插極準，但面對未來「消費者行為劇變」或「突破性產品創新」時預測力驟降"
        ],
        theme=theme
    )

    # Right Card 2: 終極解方：依情境需求匹配武器的「權變投資組合 (Contingency Portfolio)」
    r2 = draw_modern_card(
        ax, x=54.5, y=14.5, width=40.5,
        title="終極解方：依商業情境配置工具之「權變組合矩陣」",
        badge_text="效益最大化處方",
        accent_key="success",
        max_em_width=41.5,
        bullets=[
            "● 情境 A【早期點子發想、B2B 銷售話術演練、高接觸門檻受眾初探】：採用「解法① 數位雙生 ＋ 解法④ 歷史微調」→ 容錯率高，發揮 AI 低成本、全天候、不疲倦優勢，快速淘汰 80% 弱點子",
            "● 情境 B【常規品牌健康度追蹤、核心價值驅動因素排序】：採用「AI 動態訪談員（消除道德修飾）＋ 解法② 右腦 AI 轉譯與左腦道斯線性模型」→ 變數結構穩定，兼顧質化深度與量化零幻覺",
            "● 情境 C【高風險最終訂價實驗、多感官體驗（香水/食品）、突破性創新】：強制回歸「真人隨機盲測實驗（A/B Test）＋ 解法③ 局部校準」→ 避開價格混淆、無感官與外推失靈三大禁區！"
        ],
        theme=theme
    )

    # Central Bridge Arrows connecting Left Problems to Right Solutions
    draw_labeled_arrow(
        ax,
        (l2[0] + l2[2], l2[1] + l2[3] * 0.55),
        (r1[0], r1[1] + r1[3] * 0.45),
        label_text="跳出純 Prompt 催生四大解法",
        theme=theme, accent_key="primary", rad=0.08
    )
    draw_labeled_arrow(
        ax,
        (l3[0] + l3[2], l3[1] + l3[3] * 0.5),
        (r2[0], r2[1] + r2[3] * 0.5),
        label_text="放棄萬能模型 → 轉向情境權變",
        theme=theme, accent_key="success", rad=-0.06
    )
    draw_labeled_arrow(
        ax,
        (r1[0] + r1[2] * 0.5, r1[1]),
        (r2[0] + r2[2] * 0.5, r2[1] + r2[3]),
        label_text="看清各自死穴後依戰場派兵",
        theme=theme, accent_key="synth", rad=0.0
    )

    out_path = os.path.join(OUT_DIR, "02_生成式AI市調局限_實驗混淆與四大前沿解法思辨圖.jpg")
    save_publication_figure(fig, out_path, theme, dpi=240)


def build_diagram_3():
    """
    Diagram 3: Grand 3-Article Synthesis Blueprint (T2: Left-to-Right Pipeline, Theme: mckinsey_executive)
    """
    configure_cjk_fonts()
    theme = THEMES["mckinsey_executive"]
    fig, ax = plt.subplots(figsize=(28, 18.5))
    fig.patch.set_facecolor(theme["canvas_bg"])
    ax.set_facecolor(theme["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    draw_canvas_header_and_footer(
        ax,
        title="【三篇合體終極藍圖】企業數據科學與生成式 AI 決策之「道・法・術」三階架構 (篇三)",
        subtitle="第一階《顧客需求不靠猜》界定問題方向 → 第二階《AI 強化數據分析》打通情境底座 → 第三階《生成式 AI 顛覆市場研究》前線實操與權變驗證",
        takeaway_title="★ 三篇貫通核心閉環：以「統計模型」定錨真實客戶價值 X*，以「ERP/CRM 情境」約束 AI 邊界，再以「生成式 AI 市調＋真人盲測」高頻迭代",
        takeaway_body="徹底擺脫「高層憑直覺瞎猜」與「AI 黑盒子亂腦補」雙重陷阱，讓企業資源 100% 聚焦於驅動「企業與客戶雙向價值創造」的核心造血引擎。",
        theme=theme,
    )

    # Three Columns (T2 Pipeline):
    draw_macro_zone(ax, 3.5, 12.5, 28.0, 76.5, "【第一階：道】界定問題與改進方向\n《顧客需求不靠猜！統計模型找正解》", theme)
    draw_macro_zone(ax, 36.0, 12.5, 28.0, 76.5, "【第二階：法】盤點能力與情境底座\n《AI 能強化你的數據分析能力》", theme)
    draw_macro_zone(ax, 68.5, 12.5, 28.0, 76.5, "【第三階：術】前線市調實操與權變\n《生成式 AI 正在顛覆市場研究》", theme)

    # Col 1 Cards
    c1_top = draw_modern_card(
        ax, x=4.7, y=51.5, width=25.6,
        title="破除高層直覺偏誤與對齊目標 Y",
        badge_text="Step 1 定錨",
        accent_key="danger",
        max_em_width=26.2,
        bullets=[
            "● 診斷高層兩大錯誤：72% 高層認知與顧客真實重視呈零/負相關；85.5% 每兩年大改優先順序（受顯眼客訴與盲從對手誤導）",
            "● 道斯（Robyn Dawes）線性模型定理：人腦懂變數 X 卻無法穩定加權排序；用雙層統計模型算出各因素對整體價值與真實會計營收 Y 的「提升潛力（Lift）」",
            "● 財務鐵證：認知一致度每升 12.5 分，營收 +9.2%、毛利率 +5.2%、市值 +11.1%"
        ],
        theme=theme
    )

    c1_bot = draw_modern_card(
        ax, x=4.7, y=15.0, width=25.6,
        title="少做多得五步驟：鎖定少數關鍵 X*",
        badge_text="Step 2 聚焦",
        accent_key="primary",
        max_em_width=26.2,
        bullets=[
            "● 揭露落差 → 算提升潛力 → 融入員工日常 → 淘汰近零價值計畫（化解政治角力）→ 執行卓越後才對外宣揚",
            "● 標竿實證：ITI 鎖定「每週主動進度報告」（股價漲 162%）；S-SET 鎖定「3 小時快速報價」（人均銷售 +52%）",
            "● 交棒下一階：明確界定公司真正該改進的 1~2 個核心價值驅動因素 X*，防止 AI 無目標亂算"
        ],
        theme=theme
    )

    # Col 2 Cards
    c2_top = draw_modern_card(
        ax, x=37.2, y=51.5, width=25.6,
        title="內嵌 ERP / CRM 跨部門「背景情境」",
        badge_text="Step 3 基建",
        accent_key="primary",
        max_em_width=26.2,
        bullets=[
            "● 打破數據孤島：真實商業問題皆跨職能，將分析直接嵌入 ERP（財務/庫存/供應鏈）與 CRM（銷售/客戶互動）交易系統",
            "● 領域情境封裝（Domain Context）：如人資系統自動配對履歷、供應鏈預測瓶頸、AXA XL 僅 8 週全公司導入內建 KPI 系統",
            "● 訊號 vs. 雜訊分工：由人類領域情境預先設定合理因果邊界（避免醫療 AI 肺炎氣喘悖論等虛假相關），再讓 AI 在邊界內找模式"
        ],
        theme=theme
    )

    c2_bot = draw_modern_card(
        ax, x=37.2, y=15.0, width=25.6,
        title="AI 擴增分析賦能與數學懲罰過濾雜訊",
        badge_text="Step 4 賦能",
        accent_key="synth",
        max_em_width=26.2,
        bullets=[
            "● 擴增分析（Augmented Analytics）：結合 ML（找趨勢變異）+ NLP（口說提問）+ NLG（自動生成摘要），賦能「平民數據分析師」並解放專家（如製造商揪出未授權折扣挽回數十萬美元）",
            "● 統計防過度配適機制：固定樣本 N 盲目擴充參數 p 會耗盡自由度導致 Overfitting；以 Adjusted R² 與 Lasso 正則化（L1 懲罰）自動將雜訊權重壓為 0"
        ],
        theme=theme
    )

    # Col 3 Cards
    c3_top = draw_modern_card(
        ax, x=69.7, y=51.5, width=25.6,
        title="生成式 AI 市調實操：訪談、合成與雙生",
        badge_text="Step 5 實操",
        accent_key="success",
        max_em_width=26.2,
        bullets=[
            "● AI 動態訪談員（Outset.ai）：對機器不觸發人類「心理與道德修飾機制」，挖出無偽裝真實痛點，兼顧規模與深度",
            "● 合成數據與大小模型調配：以內部結構化數據微調公開大模型，模擬高接觸門檻受眾（如安永 EY 合成 CEO 達 95% 一致）",
            "● 顧客數位雙生（Digital Twins）：打造永不疲倦的客戶虛擬分身（哥倫比亞 2,500 人群組、史丹福 85% 重測穩定度），供業務事前演練話術與測試早期點子"
        ],
        theme=theme
    )

    c3_bot = draw_modern_card(
        ax, x=69.7, y=15.0, width=25.6,
        title="情境權變防線與真人隨機實驗終審閉環",
        badge_text="Step 6 終審",
        accent_key="warn",
        max_em_width=26.2,
        bullets=[
            "● 嚴守 AI 三大禁區：警覺「盲測訂價混淆現象（AI 腦補競品與歷史價同步變貴）」、「多感官失靈（高砂香料）」與「未來劇變外推失靈」",
            "● 實務防偏見四關卡：開放式探索題目 → 迴歸推導重要性 → 綁定真實會計帳本 → 真人隨機對照實驗（A/B Test，如 800 億美元銀行案例）完成價值創造閉環！"
        ],
        theme=theme
    )

    # Pipeline Arrows across columns
    draw_labeled_arrow(
        ax,
        (c1_top[0] + c1_top[2], c1_top[1] + c1_top[3] * 0.5),
        (c2_top[0], c2_top[1] + c2_top[3] * 0.5),
        label_text="鎖定核心目標 X* 與 Y",
        theme=theme, accent_key="primary", rad=0.05
    )
    draw_labeled_arrow(
        ax,
        (c1_bot[0] + c1_bot[2], c1_bot[1] + c1_bot[3] * 0.5),
        (c2_bot[0], c2_bot[1] + c2_bot[3] * 0.5),
        label_text="提供正則化篩選紀律",
        theme=theme, accent_key="synth", rad=-0.05
    )
    draw_labeled_arrow(
        ax,
        (c2_top[0] + c2_top[2], c2_top[1] + c2_top[3] * 0.5),
        (c3_top[0], c3_top[1] + c3_top[3] * 0.5),
        label_text="注入 ERP/CRM 真實情境",
        theme=theme, accent_key="success", rad=0.05
    )
    draw_labeled_arrow(
        ax,
        (c2_bot[0] + c2_bot[2], c2_bot[1] + c2_bot[3] * 0.5),
        (c3_bot[0], c3_bot[1] + c3_bot[3] * 0.5),
        label_text="人機分工過濾虛假相關",
        theme=theme, accent_key="warn", rad=-0.05
    )

    out_path = os.path.join(OUT_DIR, "03_三篇合體_顧客價值與AI數據科學決策終極藍圖.jpg")
    save_publication_figure(fig, out_path, theme, dpi=240)


if __name__ == "__main__":
    build_diagram_1()
    build_diagram_2()
    build_diagram_3()
