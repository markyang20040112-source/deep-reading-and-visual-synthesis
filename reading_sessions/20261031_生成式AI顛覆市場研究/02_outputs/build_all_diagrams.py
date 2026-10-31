# -*- coding: utf-8 -*-
"""
build_all_diagrams.py
Generates 4 publication-grade visual knowledge diagrams (240 DPI .jpg) following upgraded skill rules:
0. 00_生成式AI顛覆市場研究_全篇內容與脈絡總覽架構圖.jpg (Ausubel Macrostructure Master Map)
1. 01_生成式AI顛覆市場研究_四大機會與核心實務圖.jpg (Deep Dive 1: Opportunities, Outset.ai Moral Modification, & 3 Data Structures)
2. 02_生成式AI市調局限_實驗混淆與四大前沿解法思辨圖.jpg (Deep Dive 2: Confounding, Prompt Dilemma, & Critique of 4 Solutions)
3. 03_三篇合體_顧客價值與AI數據科學決策終極藍圖.jpg (Deep Dive 3: 3-Article Synthesis "道・法・術")

Key Visual Quality Guarantees:
- Dynamic pixel-to-em line measure at 11.6pt-12.0pt body font: text fills ~90% of BOTH horizontal width AND vertical height of every card!
- Token-aware wrapping & Kinsoku Shori: English words/numbers never split mid-word; punctuation never starts a line; zero missing glyphs.
- Connector pills placed cleanly in wide open corridors with zero card-border overlap.
"""

import os
import re
import sys
import unicodedata
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

SCRIPT_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\.agents\skills\deep-reading-and-visual-synthesis\scripts"
sys.path.insert(0, SCRIPT_DIR)

from generate_mindmap import (
    THEMES,
    configure_cjk_fonts,
    sanitize_cjk_glyphs,
    draw_macro_zone,
    draw_canvas_header_and_footer,
    save_publication_figure,
)

OUT_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI顛覆市場研究\02_outputs"
os.makedirs(OUT_DIR, exist_ok=True)

NO_START_CHARS = set("，。、；：？！）」』】》〉—…,.!?;:)]}%‰")
TOKEN_RE = re.compile(r"\d+(?:,\d+)+\+?|[A-Za-z0-9_.\-+%/]+|.")

FIG_W_IN = 24.0
FIG_H_IN = 15.6


def char_em(ch):
    eaw = unicodedata.east_asian_width(ch)
    return 1.0 if eaw in ("W", "F") else 0.54


def calc_card_max_em(card_w_units, font_pt=11.6):
    usable_units = card_w_units - 2.25
    usable_pts = (usable_units / 100.0) * (0.96 * FIG_W_IN * 72.0)
    return usable_pts / (font_pt * 1.02)


def wrap_card_bullets(bullets, card_w_units, font_pt=11.6, hanging_indent="   "):
    max_em = calc_card_max_em(card_w_units, font_pt=font_pt)
    indent_w = sum(char_em(c) for c in hanging_indent)
    all_lines = []

    for idx, b in enumerate(bullets):
        b = sanitize_cjk_glyphs(b)
        for raw_seg in b.split("\n"):
            tokens = TOKEN_RE.findall(raw_seg)
            cur_line = ""
            cur_w = 0.0
            for tok in tokens:
                tok_w = sum(char_em(c) for c in tok)
                is_punct = (len(tok) == 1 and tok in NO_START_CHARS)
                if cur_w + tok_w > max_em and cur_line.strip() and not is_punct:
                    all_lines.append((cur_line, False))
                    tok_s = tok.lstrip(" ")
                    cur_line = hanging_indent + tok_s
                    cur_w = indent_w + sum(char_em(c) for c in tok_s)
                else:
                    cur_line += tok
                    cur_w += tok_w
            if cur_line.strip():
                # Mark the last line of each bullet (except the final bullet) for extra paragraph spacing
                is_last_of_bullet = (idx < len(bullets) - 1)
                all_lines.append((cur_line, is_last_of_bullet))
    return all_lines


def draw_calibrated_card(ax, x, y, width, title, bullets, theme,
                         accent_key="primary", badge_text=None,
                         font_pt=11.5, line_step=2.22, bullet_gap=0.55, fixed_height=None):
    """
    Draws a card where body lines automatically fill ~90% of card width AND have comfortable
    inter-bullet breathing space (`bullet_gap`), eliminating both right-side and bottom empty space!
    """
    title = sanitize_cjk_glyphs(title)
    badge_text = sanitize_cjk_glyphs(badge_text)
    accent = theme["accents"].get(accent_key, theme["accents"]["primary"])
    accent_color = accent["main"]
    pill_bg = accent["pill_bg"]

    wrapped_items = wrap_card_bullets(bullets, card_w_units=width, font_pt=font_pt)
    num_bullet_gaps = sum(1 for _, is_end in wrapped_items if is_end)
    calc_h = 4.6 + len(wrapped_items) * line_step + num_bullet_gaps * bullet_gap + 1.4
    height = max(fixed_height, calc_h) if fixed_height else calc_h

    # Shadow
    shadow_box = FancyBboxPatch(
        (x + 0.20, y - 0.28), width, height,
        boxstyle="round,pad=0.18,rounding_size=0.9",
        linewidth=0, facecolor=theme["shadow"], alpha=0.045, zorder=2.5
    )
    ax.add_patch(shadow_box)

    # Card Surface
    card_box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.18,rounding_size=0.9",
        linewidth=1.35, edgecolor=theme["card_border"],
        facecolor=theme["card_bg"], zorder=3
    )
    ax.add_patch(card_box)

    # Left Accent Strip
    strip_w = 0.50
    accent_strip = FancyBboxPatch(
        (x, y + 0.35), strip_w, height - 0.7,
        boxstyle="round,pad=0.04,rounding_size=0.25",
        linewidth=0, facecolor=accent_color, zorder=3.5
    )
    ax.add_patch(accent_strip)

    text_x = x + strip_w + 0.78
    header_y = y + height - 1.25

    if badge_text:
        ax.text(
            text_x, header_y, f" {badge_text} ",
            fontsize=9.6, fontweight="bold", color=accent_color,
            va="top", ha="left", zorder=4,
            bbox=dict(boxstyle="round,pad=0.20,rounding_size=0.38",
                      facecolor=pill_bg, edgecolor=accent_color, lw=0.9)
        )
        title_offset_x = text_x + sum(char_em(c) for c in badge_text) * 0.80 + 1.45
        ax.text(
            title_offset_x, header_y - 0.02, title,
            fontsize=13.5, fontweight="bold", color=theme["text_title"],
            va="top", ha="left", zorder=4
        )
    else:
        ax.text(
            text_x, header_y, title,
            fontsize=13.6, fontweight="bold", color=accent_color,
            va="top", ha="left", zorder=4
        )

    divider_y = y + height - 3.15
    ax.plot(
        [text_x, x + width - 0.65], [divider_y, divider_y],
        color=theme["card_border"], linewidth=0.8, alpha=0.8, zorder=3.5
    )

    line_y = y + height - 3.90
    for line_str, is_end_of_bullet in wrapped_items:
        ax.text(
            text_x, line_y, line_str,
            fontsize=font_pt, color=theme["text_body"],
            va="top", ha="left", zorder=4
        )
        line_y -= line_step
        if is_end_of_bullet:
            line_y -= bullet_gap

    return (x, y, width, height)


def draw_corridor_arrow(ax, p0, p1, label_text=None, theme=None,
                        accent_key="primary", rad=0.0, label_pos=0.5, label_dy=0.0):
    if theme is None:
        theme = THEMES["swiss_editorial"]
    accent = theme["accents"].get(accent_key, theme["accents"]["primary"])
    color = accent["main"]

    arrow = FancyArrowPatch(
        p0, p1,
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="simple,head_length=6.5,head_width=6.5,tail_width=2.0",
        color=color, alpha=0.85, zorder=3.8
    )
    ax.add_patch(arrow)

    if label_text:
        mx = p0[0] + (p1[0] - p0[0]) * label_pos
        my = p0[1] + (p1[1] - p0[1]) * label_pos + label_dy
        ax.text(
            mx, my, f" {sanitize_cjk_glyphs(label_text)} ",
            fontsize=8.8, fontweight="bold", color=color,
            ha="center", va="center", zorder=5,
            bbox=dict(
                boxstyle="round,pad=0.22,rounding_size=0.45",
                facecolor="#FFFFFF", edgecolor=color, lw=1.05, alpha=0.98
            )
        )


# ==============================================================================
# DIAGRAM 00: 全篇內容與脈絡總覽架構主圖 (Ausubel Macrostructure Master Map)
# ==============================================================================
def build_diagram_0():
    configure_cjk_fonts()
    theme = THEMES["swiss_editorial"]
    fig, ax = plt.subplots(figsize=(FIG_W_IN, FIG_H_IN))
    fig.patch.set_facecolor(theme["canvas_bg"])
    ax.set_facecolor(theme["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    draw_canvas_header_and_footer(
        ax,
        title="《生成式 AI 正在顛覆市場研究》全篇內容與脈絡總覽架構主圖 (篇零：文章主幹)",
        subtitle="Ausubel 宏觀內容結構圖：前言與 GBK 調查現況 → 4 大能力 × 3 大階段 → 4 大變革機會 → 合成數據 3 大機制 → 4 大風險局限 → 4 大破局解法",
        takeaway_title="★ 文章核心主旨：生成式 AI 正將市場研究從「昂貴少數的專案」轉型為「全天候運作的組織智慧引擎」",
        takeaway_body="企業應在早期產品發想與話術演練中大膽發揮 AI 的百倍速與低成本優勢；但在高風險定價與突破性創新上，必須清楚認識其語境混淆與感官局限，並結合真人實驗。",
        theme=theme,
    )

    hub_x, hub_y, hub_w, hub_h = 4.0, 77.5, 92.0, 11.5
    hub_box = FancyBboxPatch(
        (hub_x, hub_y), hub_w, hub_h,
        boxstyle="round,pad=0.25,rounding_size=1.0",
        facecolor=theme["hub_bg"], edgecolor=theme["hub_border"],
        linewidth=2.2, zorder=4
    )
    ax.add_patch(hub_box)
    ax.text(
        hub_x + 2.0, hub_y + hub_h - 1.7,
        "【核心命題與調查現況】Jeremy Korst, Stefano Puntoni, Olivier Toubia (HBR) × GBK Collective 170 位市調專家與企業調查",
        fontsize=13.8, fontweight="bold", color=theme["hub_sub"],
        ha="left", va="top", zorder=5
    )
    ax.text(
        hub_x + 2.0, hub_y + hub_h - 5.1,
        "● 傳統痛點：耗時昂貴、量化廣度與質化深度難以兼得  ｜  ● 採用現況：45% 已使用生成式 AI、45% 規畫中（62% 統整逐字稿、58% 分析數據、54% 撰寫報告；80%+ 認同釋放策略敘事時間）\n"
        "● 核心矩陣：生成式 AI 的「4 大核心能力（統整、編寫程式碼、人機互動、寫作）」全面滲透市場研究的「3 大流程階段（① 設計研究與找機會 → ② 蒐集與分析數據 → ③ 報告影響與傳播）」",
        fontsize=10.5, color="#F8FAFC",
        ha="left", va="top", zorder=5
    )

    draw_macro_zone(ax, 3.5, 12.0, 29.5, 61.5, "【第一部曲】四大變革機會與標竿實證", theme)
    draw_macro_zone(ax, 35.25, 12.0, 29.5, 61.5, "【第二部曲】合成數據三機制與四大風險局限", theme)
    draw_macro_zone(ax, 67.0, 12.0, 29.5, 61.5, "【第三部曲】四大前沿破局解法與管理者行動", theme)

    draw_calibrated_card(
        ax, x=4.6, y=42.5, width=27.3,
        title="機會 1 & 2：強化實務與取代問卷",
        badge_text="章節一",
        accent_key="primary",
        font_pt=11.3, line_step=2.18, bullet_gap=0.6, fixed_height=27.0,
        bullets=[
            "● 機會 1（強化現有實務）：摘要過往研究、自動生成程式碼清理數據；Meaningful 與 Outset.ai 打造「AI 動態訪談員」依回答即時追問（WeightWatchers 實證受訪者更坦誠且幾乎無幻覺）。",
            "● 機會 2（取代現有實務）：以「合成受訪者」填問卷或接受質化訪談（81% 已用或計畫使用）；Evidenza 與安永 (EY) 雙盲測試 1,000+ 名合成 CEO，與真人結論高達 95% 相同。"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=4.6, y=13.5, width=27.3,
        title="機會 3 & 4：填補缺口與數位雙生",
        badge_text="章節二",
        accent_key="success",
        font_pt=11.3, line_step=2.18, bullet_gap=0.6, fixed_height=27.0,
        bullets=[
            "● 機會 3（填補現有缺口）：30% 用於引導過往因預算/時間不足而憑直覺拍板的決策（通用磨坊加速早期新品發想；Arena 依各門市客群量身打造選品；估算品牌對財務 ROI 影響）。",
            "● 機會 4（創造新見解—顧客數位雙生）：為客戶建立永不疲勞的虛擬分身供業務演練話術（82% 計畫實驗；哥倫比亞 2,500 人群組、史丹福 85% 兩週重測信度、CivicSync、Oleria）。"
        ],
        theme=theme
    )

    draw_calibrated_card(
        ax, x=36.35, y=42.5, width=27.3,
        title="合成數據三機制 × 大小模型取捨",
        badge_text="章節三",
        accent_key="synth",
        font_pt=11.3, line_step=2.18, bullet_gap=0.6, fixed_height=27.0,
        bullets=[
            "● 提升合成品質三關鍵：現階段僅 31% 認為純合成數據價值極高，須結合 ① 提示詞輸入問答範例 (Few-shot)、② 從研究知識庫提取內容 (RAG)、③ 以內部數據微調參數。",
            "● 隱私與能力取捨：私有小型模型（如美國陸軍採用的 Rockfish Data）完全保密但僅能處理結構化／半結構化數據；公開大型模型方能處理非結構化質化數據（折衷：內部數據微調大模型）。"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=36.35, y=13.5, width=27.3,
        title="生成式 AI 市調之四大風險局限",
        badge_text="章節四",
        accent_key="danger",
        font_pt=11.3, line_step=2.18, bullet_gap=0.6, fixed_height=27.0,
        bullets=[
            "● 人口偏誤與跨期不穩：公開模型偏向自由派與高學歷，難代表 65 歲以上與宗教群體（哥倫比亞/史丹福）；回答變異過小、易受選項順序影響且 3 個月內表現搖擺（范登堡 Bisbee 2024）。",
            "● 多感官失靈與實驗混淆：純文字 AI 無法模擬嗅覺與潛意識記憶（高砂香料失敗）；盲測訂價時會自動腦補競品與歷史價同步變貴（混淆現象 Confounding），使需求曲線平坦失真！"
        ],
        theme=theme
    )

    draw_calibrated_card(
        ax, x=68.1, y=42.5, width=27.3,
        title="克服混淆與偏誤之四大前沿解法",
        badge_text="章節五",
        accent_key="primary",
        font_pt=11.3, line_step=2.18, bullet_gap=0.6, fixed_height=27.0,
        bullets=[
            "● 解法 1 & 2：① 建立綁定真人數小時訪談、認知測驗與實際購物行為「基準事實」之數位雙生；② 右腦大模型轉譯非結構化圖文特徵 ＋ 左腦傳統統計公式計算價格彈性。",
            "● 解法 3 & 4：③ 結合少量真人隨機樣本與大量 AI 樣本進行統計校準（扣除系統偏誤）；④ 以大量歷史調查與真實 A/B 實驗數據直接微調模型（如 Evidenza、GBK 實測）。"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=68.1, y=13.5, width=27.3,
        title="管理者行動建議與防偏見四關卡",
        badge_text="章節六",
        accent_key="warn",
        font_pt=11.3, line_step=2.18, bullet_gap=0.6, fixed_height=27.0,
        bullets=[
            "● 落地雙原則：早期概念發想與高接觸門檻受眾（如繁忙外科醫師）大膽用 AI 衝速度；但面對「消費者行為劇變」或「突破性產品創新」，歷史微調模型預測力弱，必回歸真人研究。",
            "● 防偏見四道關卡：開放式探索題目 → 迴歸推導重要性（不信口頭宣稱）→ 綁定真實會計指標 → 上市前執行真人隨機對照實驗（如 800 億美元銀行案例）。"
        ],
        theme=theme
    )

    draw_corridor_arrow(ax, (18.2, 77.5), (18.2, 73.5), label_text="展開四大機會", theme=theme, accent_key="primary")
    draw_corridor_arrow(ax, (50.0, 77.5), (50.0, 73.5), label_text="審視機制與風險", theme=theme, accent_key="danger")
    draw_corridor_arrow(ax, (81.7, 77.5), (81.7, 73.5), label_text="導入解法與防線", theme=theme, accent_key="success")

    out_path = os.path.join(OUT_DIR, "00_生成式AI顛覆市場研究_全篇內容與脈絡總覽架構圖.jpg")
    save_publication_figure(fig, out_path, theme, dpi=240)


# ==============================================================================
# DIAGRAM 01: 四大機會、消除道德修飾機制與三類數據結構拆解圖 (Deep Dive 1)
# ==============================================================================
def build_diagram_1():
    configure_cjk_fonts()
    theme = THEMES["swiss_editorial"]
    fig, ax = plt.subplots(figsize=(FIG_W_IN, FIG_H_IN))
    fig.patch.set_facecolor(theme["canvas_bg"])
    ax.set_facecolor(theme["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    draw_canvas_header_and_footer(
        ax,
        title="《生成式 AI 正在顛覆市場研究》四大機會與三類數據結構深度拆解圖 (篇一)",
        subtitle="AI 動態訪談員消除「心理與道德修飾機制」 × 合成數據雙盲實證 × 結構化（數字/類別）、半結構化、非結構化質化數據與大小模型分工",
        takeaway_title="★ 核心思辨洞見：人類面對真人訪談會啟動「心理與道德修飾機制」，面對無道德審判的 AI 訪談員反而吐露最真實痛點",
        takeaway_body="同時，小型私有模型雖具絕對隱私但僅能學習結構化與半結構化機率；唯有具備人類世界知識先驗的公開大型模型，方能解析非結構化質化語意（最佳折衷：內部數據微調大模型）。",
        theme=theme,
    )

    draw_macro_zone(ax, 3.2, 12.0, 29.8, 76.5, "【左翼】AI 動態訪談破除道德偽裝 × 合成數據規模化", theme)
    draw_macro_zone(ax, 67.0, 12.0, 29.8, 76.5, "【右翼】三類數據結構光譜 × 大小模型取捨 × 數位雙生", theme)

    hub_x, hub_y, hub_w, hub_h = 40.5, 42.0, 19.0, 17.5
    hub_box = FancyBboxPatch(
        (hub_x, hub_y), hub_w, hub_h,
        boxstyle="round,pad=0.25,rounding_size=1.2",
        facecolor=theme["hub_bg"], edgecolor=theme["hub_border"],
        linewidth=2.3, zorder=4
    )
    ax.add_patch(hub_box)
    ax.text(
        hub_x + hub_w / 2, hub_y + hub_h - 2.3,
        "生成式 AI 顛覆市調\n核心機制與資料光譜",
        fontsize=13.8, fontweight="bold", color=theme["hub_text"],
        ha="center", va="top", zorder=5
    )
    ax.text(
        hub_x + hub_w / 2, hub_y + 2.0,
        "● 兼得量化廣度與質化深度\n● 解除受訪者社會期許偏誤\n● 依資料結構配置大小模型\n● 建立基準事實顧客雙生",
        fontsize=9.6, color="#E2E8F0",
        ha="center", va="bottom", zorder=5
    )

    c_lt = draw_calibrated_card(
        ax, x=4.2, y=49.5, width=27.6,
        title="強化實務：AI 訪談員消除道德修飾",
        badge_text="機會 1 思辨",
        accent_key="primary",
        font_pt=11.1, line_step=2.12, bullet_gap=0.55, fixed_height=33.5,
        bullets=[
            "● 4 大能力 × 3 大階段全面提速：在設計研究、蒐集分析、報告傳播全面賦能（62% 統整逐字稿、58% 分析數據、54% 撰寫報告）。",
            "● Outset.ai 動態追問平台：依受訪者前次回答即時動態追問，打破傳統市調「量化問卷規模」與「質化訪談深度」不可兼得之瓶頸。",
            "● ★ 思辨突破（為何對 AI 更誠實？）：人類與「真人」互動時會自動啟動「心理與道德修飾機制（社會期許偏誤）」，為顧面子而隱藏私密想法；面對無道德審判眼神的 AI 反而卸下心防（WeightWatchers 實證），且 AI 僅提問與統整故幾乎零幻覺！"
        ],
        theme=theme
    )

    c_lb = draw_calibrated_card(
        ax, x=4.2, y=13.5, width=27.6,
        title="取代與補缺口：合成受眾與全天候引擎",
        badge_text="機會 2 & 3",
        accent_key="warn",
        font_pt=11.1, line_step=2.12, bullet_gap=0.55, fixed_height=33.5,
        bullets=[
            "● 合成數據（Synthetic Data）：由 AI 模擬目標客群填問卷或接受深度訪談（81% 已用或計畫使用，但僅 31% 認為純合成數據價值極高）。",
            "● 接地氣三關鍵：① 提示詞輸入問答範例（Few-shot）、② 從過去研究知識庫提取內容（RAG）、③ 微調模型參數以對齊內部現有數據。",
            "● 黃金雙盲實證與補缺口：Evidenza × 安永 (EY) 模擬 1,000+ 名營收逾 10 億美元公司 CEO，與真人結論高達 95% 相同；30% 用於填補過往無預算調查之決策缺口（如通用磨坊新品發想、Arena 門市選品）。"
        ],
        theme=theme
    )

    c_rt = draw_calibrated_card(
        ax, x=68.2, y=49.5, width=27.6,
        title="三類數據結構 × 小模型 vs. 大模型",
        badge_text="資料科學拆解",
        accent_key="synth",
        font_pt=11.1, line_step=2.12, bullet_gap=0.55, fixed_height=33.5,
        bullets=[
            "● ① 結構化數據（表格欄位）：含「數字型（年齡 34 歲、消費額 28,500 元）」與「類別型（性別、城市、會員卡別、五點滿意度選項）」。",
            "● ② 半結構化數據（自帶標籤階層）：網站與 App 點擊流 JSON 日誌、客服工單與郵件紀錄（每位顧客行為序列長短不一，但具明確標籤）。",
            "● ③ 非結構化質化數據 & 模型權衡：訪談逐字稿與社群長文（回答 Why 與 How）。私有小模型（如 Rockfish Data）完全保密但僅懂表格機率；唯有具「人類世界知識先驗」的公開大模型方能理解質化語意（最佳解：用內部私有數據微調公開大模型）！"
        ],
        theme=theme
    )

    c_rb = draw_calibrated_card(
        ax, x=68.2, y=13.5, width=27.6,
        title="創造新見解：顧客數位雙生虛擬分身",
        badge_text="機會 4",
        accent_key="success",
        font_pt=11.1, line_step=2.12, bullet_gap=0.55, fixed_height=33.5,
        bullets=[
            "● 打破「第一印象只有一次機會」鐵律：為個別客戶打造永不疲勞、不煩躁的虛擬分身，供 B2B 業務事前演練推銷話術與測試廣告共鳴（逾 82% 已實驗或計畫實驗）。",
            "● 商業與研發實戰：Arena 訓練銷售人員、CivicSync 經授權追蹤線上購物軌跡建雙生、奧美測試創意、Oleria 用 NotebookLM 建研究助理。",
            "● 學術基準事實群組（Ground Truth）：哥倫比亞商學院建 2,500 名真人全維度數位雙生；史丹福 + DeepMind 以數小時訪談建雙生，兩週後重測回答相似度高達 85%！"
        ],
        theme=theme
    )

    # Wide corridor between x=31.8 and x=40.5 (8.7 units!) and x=59.5 to x=68.2 (8.7 units!)
    draw_corridor_arrow(
        ax, (hub_x, hub_y + hub_h * 0.78), (c_lt[0] + c_lt[2], c_lt[1] + c_lt[3] * 0.5),
        label_text="卸下道德心防", theme=theme, accent_key="primary", rad=-0.08, label_pos=0.52, label_dy=3.2
    )
    draw_corridor_arrow(
        ax, (hub_x, hub_y + hub_h * 0.22), (c_lb[0] + c_lb[2], c_lb[1] + c_lb[3] * 0.5),
        label_text="95% 雙盲吻合", theme=theme, accent_key="warn", rad=0.08, label_pos=0.52, label_dy=-3.2
    )
    draw_corridor_arrow(
        ax, (hub_x + hub_w, hub_y + hub_h * 0.78), (c_rt[0], c_rt[1] + c_rt[3] * 0.5),
        label_text="三階資料光譜", theme=theme, accent_key="synth", rad=0.08, label_pos=0.48, label_dy=3.2
    )
    draw_corridor_arrow(
        ax, (hub_x + hub_w, hub_y + hub_h * 0.22), (c_rb[0], c_rb[1] + c_rb[3] * 0.5),
        label_text="85% 重測信度", theme=theme, accent_key="success", rad=-0.08, label_pos=0.48, label_dy=-3.2
    )

    out_path = os.path.join(OUT_DIR, "01_生成式AI顛覆市場研究_四大機會與核心實務圖.jpg")
    save_publication_figure(fig, out_path, theme, dpi=240)


# ==============================================================================
# DIAGRAM 02: 實驗混淆機制與四大前沿解法思辨圖 (Deep Dive 2)
# ==============================================================================
def build_diagram_2():
    configure_cjk_fonts()
    theme = THEMES["nature_academic"]
    fig, ax = plt.subplots(figsize=(FIG_W_IN, FIG_H_IN))
    fig.patch.set_facecolor(theme["canvas_bg"])
    ax.set_facecolor(theme["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    draw_canvas_header_and_footer(
        ax,
        title="《生成式 AI 正在顛覆市場研究》實驗混淆機制與四大前沿解法批判圖 (篇二)",
        subtitle="盲測訂價「混淆現象 (Confounding)」因果公式 × 提示詞「挖東牆補西牆」困境 × 四大前沿解法之理論死穴批判 × George Box 情境權變組合",
        takeaway_title="★ 方法論總結：所有模型皆有缺陷（All Models Are Wrong, But Some Are Useful）—— 放棄尋找萬能單一模型，建立「情境權變組合」",
        takeaway_body="早期發想用「數位雙生＋歷史微調」衝百倍速度；常規追蹤用「AI 訪談員＋左腦統計模型」防幻覺；高風險定價、多感官體驗與突破性創新則強制回歸「真人隨機盲測」！",
        theme=theme,
    )

    draw_macro_zone(ax, 3.2, 12.0, 42.5, 76.5, "【左區：AI 市調結構局限】為何盲測訂價與感官實驗在 AI 身上會失靈？", theme)
    draw_macro_zone(ax, 54.3, 12.0, 42.5, 76.5, "【右區：方法論思辨與破局】四大前沿解法之「理論死穴」與情境權變組合", theme)

    l1 = draw_calibrated_card(
        ax, x=4.4, y=62.5, width=40.1,
        title="人口樣本偏誤、跨期搖擺與「多感官失靈」",
        badge_text="局限 1 & 3",
        accent_key="danger",
        font_pt=11.0, line_step=2.05, bullet_gap=0.45, fixed_height=21.5,
        bullets=[
            "● 人口代表性偏誤（哥倫比亞/史丹福 2023）：OpenAI 等公開模型觀點明顯偏向「自由派、高學歷人士」，難以代表 65 歲以上或虔誠宗教群體（源自訓練語料與人類對齊微調偏誤）。",
            "● 提示脆弱與跨時間不穩（范登堡 Bisbee 2024）：合成民調回答變異過小，極易受選擇題「選項順序與細微措辭」影響，且在 3 個月期間內表現搖擺不穩。",
            "● 多感官與潛意識失靈（高砂香料 Takasago 實證）：香氣嗅覺偏好緊密綁定人類個體生理經歷與潛意識情緒記憶，純文字訓練之 AI 無法模擬真實五感反應。"
        ],
        theme=theme
    )

    l2 = draw_calibrated_card(
        ax, x=4.4, y=36.5, width=40.1,
        title="盲測訂價實驗之「混淆現象 (Confounding)」機制",
        badge_text="局限 2 因果拆解",
        accent_key="warn",
        font_pt=11.0, line_step=2.05, bullet_gap=0.45, fixed_height=23.8,
        bullets=[
            "● 真人隨機盲測 P(Y | do(X))：只調高測試商品價格 X（1,000 → 5,000 元），真人受試者心中對外界物價與競品價格 Z（1,200 元）認知不變 → 測出正常向右下傾斜之需求曲線。",
            "● AI 語境腦補引發混淆 P_LLM(Y | X)：AI 運算的是上下文條件聯想，無法將高價 X 視為隨機抽樣！看到標價 5,000 元時，自動調高 P_LLM(Z|X)，在隱空間「腦補歷史價格與店內其他競品 Z 也全都賣 5,000 元」！",
            "● 災難後果：混淆變數 Z 同時連動自變數 X（測試價格）與應變數 Y（購買意願），抵銷了漲價痛感，導致無論定價多高 AI 都回答「合理會買」，需求曲線完全平坦失真！"
        ],
        theme=theme
    )

    l3 = draw_calibrated_card(
        ax, x=4.4, y=13.5, width=40.1,
        title="為何純靠「詳細提示詞規範」必淪為挖東牆補西牆？",
        badge_text="提示詞死胡同",
        accent_key="danger",
        font_pt=11.0, line_step=2.05, bullet_gap=0.45, fixed_height=21.0,
        bullets=[
            "● 【東牆：未知腦補變數永遠鎖不完】：就算在提示詞鎖死「歷史價與競品價皆 1,200 元」，具備數千億參數的 AI 看到 5,000 元又會自動繞道腦補「現在大缺貨、巨星代言或限量溢價」，人工無法事前窮舉所有潛在混淆變數 Z！",
            "● 【西牆：寫太白引發需求特徵劇透與焦點錯覺】：若在 Prompt 刻意強調「別家都賣 1,200、唯獨這家賣 5,000」，等於明示 AI 拒買，使 AI 從「過度遲鈍」跳到「過度理性的比大小計算機」，依然測不出真實人類的價格彈性。"
        ],
        theme=theme
    )

    r1 = draw_calibrated_card(
        ax, x=55.5, y=49.2, width=40.1,
        title="四大前沿破局解法 vs. 您的「四大理論死穴」批判",
        badge_text="第一性原理批判",
        accent_key="primary",
        font_pt=11.0, line_step=2.06, bullet_gap=0.5, fixed_height=34.8,
        bullets=[
            "● 解法 1【綁定真人記憶之數位雙生】→ 死穴批判：【具身感質不可壓縮】無法「真的把一整個人塞進模型」！文字逐字稿無法編碼生理嗅覺、味覺與潛意識記憶（如高砂香料測試香氣徹底失靈）。",
            "● 解法 2【右腦 AI 轉譯＋左腦統計公式】→ 死穴批判：【計量模型誤設偏誤】雖出現幻覺機率最小，但面對高度複雜、多變數非線性交互作用的感性問題時，左腦極難寫出高解釋力函式（寫簡單 R² 低、寫複雜又過度配適）。",
            "● 解法 3【少量真人＋大量 AI 統計校準 (PPI)】→ 死穴批判：【分布偏移與湊巧對齊】極不穩定！當下 AI 對準人類可能只是「湊巧發生」，一旦問題換字眼或跨時間（如 Bisbee 3 個月研究）校準即失效並再發幻覺。",
            "● 解法 4【大量歷史調查與實驗微調】→ 死穴批判：【後照鏡外推失靈】拿過去數據訓練屬於「分布內插值」，面對未來「消費者行為劇變」或「突破性產品創新」時預測力驟降！"
        ],
        theme=theme
    )

    r2 = draw_calibrated_card(
        ax, x=55.5, y=13.5, width=40.1,
        title="終極解方：George Box 依商業情境配置之「權變組合矩陣」",
        badge_text="效益最大化處方",
        accent_key="success",
        font_pt=11.0, line_step=2.08, bullet_gap=0.55, fixed_height=33.0,
        bullets=[
            "● 戰場 A【早期點子發想、B2B 銷售話術演練、高接觸門檻受眾初探】：配置「解法 1 數位雙生 ＋ 解法 4 歷史微調」→ 容錯率高，發揮 AI 低成本、全天候、永不疲倦優勢，百倍速淘汰 80% 弱點子。",
            "● 戰場 B【常規品牌健康度追蹤、核心價值驅動因素排序】：配置「AI 動態訪談員（消除道德修飾）＋ 解法 2 右腦 AI 轉譯與左腦道斯線性統計模型」→ 變數結構穩定，兼顧質化真心話與量化零幻覺。",
            "● 戰場 C【高風險最終訂價實驗、多感官體驗（香水/食品）、突破性產品創新】：強制回歸「真人隨機盲測實驗（A/B Test）＋ 解法 3 當期動態校準」→ 嚴格避開價格混淆、感官失靈與外推失效三大禁區！"
        ],
        theme=theme
    )

    # Corridor is 44.5 to 55.5 (11.0 units wide!)
    draw_corridor_arrow(
        ax, (l2[0] + l2[2], l2[1] + l2[3] * 0.65), (r1[0], r1[1] + r1[3] * 0.35),
        label_text="催生四大解法", theme=theme, accent_key="primary", rad=0.08, label_pos=0.5, label_dy=2.2
    )
    draw_corridor_arrow(
        ax, (l3[0] + l3[2], l3[1] + l3[3] * 0.5), (r2[0], r2[1] + r2[3] * 0.5),
        label_text="轉向情境權變", theme=theme, accent_key="success", rad=-0.08, label_pos=0.5, label_dy=-2.2
    )

    out_path = os.path.join(OUT_DIR, "02_生成式AI市調局限_實驗混淆與四大前沿解法思辨圖.jpg")
    save_publication_figure(fig, out_path, theme, dpi=240)


# ==============================================================================
# DIAGRAM 03: 三篇合體「道・法・術」企業科學決策終極藍圖 (Deep Dive 3)
# ==============================================================================
def build_diagram_3():
    configure_cjk_fonts()
    theme = THEMES["mckinsey_executive"]
    fig, ax = plt.subplots(figsize=(FIG_W_IN, FIG_H_IN))
    fig.patch.set_facecolor(theme["canvas_bg"])
    ax.set_facecolor(theme["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    draw_canvas_header_and_footer(
        ax,
        title="【三篇合體終極藍圖】企業數據科學與生成式 AI 決策之「道・法・術」三階架構 (篇三)",
        subtitle="第一階《顧客需求不靠猜》界定問題方向（道） → 第二階《AI 強化數據分析》打通情境底座（法） → 第三階《生成式 AI 顛覆市場研究》前線實操與權變終審（術）",
        takeaway_title="★ 三篇貫通核心閉環：以「統計模型」定錨真實客戶價值 X*，以「ERP/CRM 情境」約束 AI 邊界，再以「生成式 AI 市調＋真人盲測」高頻迭代",
        takeaway_body="徹底擺脫「高層憑直覺瞎猜」與「AI 黑盒子亂腦補」雙重陷阱，讓企業資源 100% 聚焦於驅動「企業與客戶雙向價值創造」的核心造血引擎。",
        theme=theme,
    )

    draw_macro_zone(ax, 3.5, 12.0, 29.0, 76.5, "【第一階：道】界定問題與改進方向\n《顧客需求不靠猜！統計模型找正解》", theme)
    draw_macro_zone(ax, 35.5, 12.0, 29.0, 76.5, "【第二階：法】盤點能力與情境底座\n《AI 能強化你的數據分析能力》", theme)
    draw_macro_zone(ax, 67.5, 12.0, 29.0, 76.5, "【第三階：術】前線市調實操與權變\n《生成式 AI 正在顛覆市場研究》", theme)

    draw_calibrated_card(
        ax, x=4.6, y=48.5, width=26.8,
        title="破除高層直覺偏誤與對齊目標 Y",
        badge_text="Step 1 定錨",
        accent_key="danger",
        font_pt=11.2, line_step=2.15, bullet_gap=0.55, fixed_height=33.5,
        bullets=[
            "● 診斷高層兩大盲點：72% 上市 B2B 高層認知與顧客真實重視呈零或負相關；85.5% 每兩年大改優先順序（受顯眼客訴可得性偏誤與盲從對手誤導）。",
            "● 道斯（Robyn Dawes）線性模型定理：人腦擅長選取變數 X，卻無法穩定加權排序；必須用雙層統計模型算出各因素對整體價值與真實會計營收 Y 的「提升潛力（Lift）」。",
            "● 財務鐵證：高層與顧客認知一致度每提升 12.5 分，年營收 +9.2%、毛利率 +5.2%、企業市值 +11.1%！"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=4.6, y=13.5, width=26.8,
        title="少做多得五步驟：鎖定少數關鍵 X*",
        badge_text="Step 2 聚焦",
        accent_key="primary",
        font_pt=11.2, line_step=2.15, bullet_gap=0.55, fixed_height=32.5,
        bullets=[
            "● 落地五步驟：揭露認知落差 → 計算提升潛力 → 融入員工日常流程 → 果斷淘汰近零價值計畫（化解跨部門政治角力）→ 執行卓越後才對外宣揚。",
            "● 標竿實證：ITI 鎖定「每週主動進度報告」使股價大漲 162%；S-SET 鎖定「3 小時快速報價」使人均銷售大增 52%。",
            "● 交棒下一階：明確界定企業真正該改進的 1~2 個核心價值驅動因素 X*，防止後續 AI 陷入無目標盲算！"
        ],
        theme=theme
    )

    draw_calibrated_card(
        ax, x=36.6, y=48.5, width=26.8,
        title="內嵌 ERP / CRM 跨部門「背景情境」",
        badge_text="Step 3 基建",
        accent_key="primary",
        font_pt=11.2, line_step=2.15, bullet_gap=0.55, fixed_height=33.5,
        bullets=[
            "● 打破數據孤島：真實商業問題皆跨職能，必須將數據分析直接內嵌於 ERP（財務/庫存/供應鏈）與 CRM（銷售/客戶互動）交易系統。",
            "● 領域背景情境（Contextual Information）：如人資系統自動配對履歷、供應鏈預測瓶頸、AXA XL 僅 8 週全公司導入內建 KPI 系統。",
            "● 訊號 vs. 雜訊分工：由人類領域專家在系統中預先設定合理因果邊界（防止醫療 AI 肺炎合併氣喘死亡率低等虛假相關災難），再讓 AI 於邊界內找模式。"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=36.6, y=13.5, width=26.8,
        title="擴增分析賦能與數學懲罰過濾雜訊",
        badge_text="Step 4 賦能",
        accent_key="synth",
        font_pt=11.2, line_step=2.15, bullet_gap=0.55, fixed_height=32.5,
        bullets=[
            "● 擴增分析（Augmented Analytics）：結合 ML（找趨勢變異）+ NLP（口說自然語言提問）+ NLG（自動生成摘要），賦能前線「平民數據分析師」（如製造商揪出未授權折扣挽回數十萬美元）。",
            "● 統計防過度配適護欄：固定樣本 N 盲目擴充參數 p 會耗盡自由度導致 Overfitting；必須以 Adjusted R² 與 Lasso 正則化（L1 懲罰）自動將無效雜訊特徵權重壓縮歸零！"
        ],
        theme=theme
    )

    draw_calibrated_card(
        ax, x=68.6, y=48.5, width=26.8,
        title="生成式 AI 市調實操：訪談、合成與雙生",
        badge_text="Step 5 實操",
        accent_key="success",
        font_pt=11.2, line_step=2.15, bullet_gap=0.55, fixed_height=33.5,
        bullets=[
            "● AI 動態訪談員（Outset.ai）：針對第一階鎖定的 X*，以機器提問解除受訪者「心理與道德修飾機制」，挖出無偽裝真實痛點，兼顧規模與深度。",
            "● 合成數據與大小模型調配：以第二階 ERP 私有數據微調公開大模型，模擬高接觸門檻受眾（如安永 EY 合成 1,000 名 CEO 達 95% 結論一致）。",
            "● 顧客數位雙生（Digital Twins）：打造永不疲倦的客戶虛擬分身（哥倫比亞 2,500 人群組、史丹福 85% 重測信度），供業務事前演練話術與百倍速快篩早期點子。"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=68.6, y=13.5, width=26.8,
        title="情境權變防線與真人隨機實驗終審閉環",
        badge_text="Step 6 終審",
        accent_key="warn",
        font_pt=11.2, line_step=2.15, bullet_gap=0.55, fixed_height=32.5,
        bullets=[
            "● 嚴守 AI 三大禁區：高度警覺「盲測訂價混淆現象（AI 自動腦補競品與歷史價同步變貴）」、「多感官失靈（高砂香料）」與「未來劇變外推失靈」。",
            "● 終局驗證四道關卡：開放式探索題目 → 迴歸推導重要性 → 綁定真實會計帳本 → 真人隨機對照實驗（A/B Test，如 800 億美元銀行案例），完整驅動「企業 ←→ 客戶」價值造血引擎！"
        ],
        theme=theme
    )

    draw_corridor_arrow(
        ax, (31.4, 65.0), (36.6, 65.0),
        label_text="道 → 法：定錨 X*", theme=theme, accent_key="primary", rad=0.0, label_pos=0.5, label_dy=17.8
    )
    draw_corridor_arrow(
        ax, (63.4, 65.0), (68.6, 65.0),
        label_text="法 → 術：注入情境", theme=theme, accent_key="success", rad=0.0, label_pos=0.5, label_dy=17.8
    )
    draw_corridor_arrow(
        ax, (31.4, 30.0), (36.6, 30.0),
        label_text="L1 懲罰篩選紀律", theme=theme, accent_key="synth", rad=0.0, label_pos=0.5, label_dy=17.2
    )
    draw_corridor_arrow(
        ax, (63.4, 30.0), (68.6, 30.0),
        label_text="人機權變終審閉環", theme=theme, accent_key="warn", rad=0.0, label_pos=0.5, label_dy=17.2
    )

    out_path = os.path.join(OUT_DIR, "03_三篇合體_顧客價值與AI數據科學決策終極藍圖.jpg")
    save_publication_figure(fig, out_path, theme, dpi=240)


if __name__ == "__main__":
    build_diagram_0()
    build_diagram_1()
    build_diagram_2()
    build_diagram_3()
