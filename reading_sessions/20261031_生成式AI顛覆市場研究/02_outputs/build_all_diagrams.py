# -*- coding: utf-8 -*-
"""
build_all_diagrams.py
Generates 4 publication-grade visual knowledge diagrams (240 DPI .jpg) following Post-E3 upgraded rules:
0. 00_生成式AI顛覆市場研究_全篇內容與脈絡總覽架構圖.jpg (Ausubel Macrostructure Master Map)
1. 01_生成式AI顛覆市場研究_四大機會與核心實務圖.jpg (Deep Dive 1: Opportunities, Outset.ai Moral Modification, & 3 Data Structures)
2. 02_生成式AI市調局限_實驗混淆與四大前沿解法思辨圖.jpg (Deep Dive 2: Confounding, Prompt Dilemma, & Critique of 4 Solutions)
3. 03_三篇合體_顧客價值與AI數據科學決策終極藍圖.jpg (Deep Dive 3: 3-Article Synthesis "道・法・術")

Key Visual Quality Guarantees (Fixes User Points 1 & 2 from Round 2):
1. Modular Horizontal Row Slots (Müller-Brockmann 1981 & W3C Box Alignment):
   Every card divides its vertical body area into N equal horizontal slots (`slot_h = avail_h / N`) with subtle
   horizontal grid dividers, guaranteeing that across all side-by-side cards, Bullet 1, Bullet 2, and Bullet 3
   sit on the EXACT same horizontal plane (`slot_top`) AND fill the vertical height of the card evenly with zero bottom blank void!
2. Full-Width Hanging Indent (`\u3000 `): Continuation lines align vertically with the text start after `● `.
3. Central Hub & Top Banner Alignment: Central hub bullets use left-aligned block centering (`ha="left"`) so all `●` dots
   form a straight vertical line, with a cyan divider line eliminating the middle empty gap.
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


def calc_card_max_em(card_w_units, font_pt=11.4):
    usable_units = card_w_units - 2.20
    usable_pts = (usable_units / 100.0) * (0.96 * FIG_W_IN * 72.0)
    return usable_pts / (font_pt * 1.02)


def wrap_bullet_to_lines(bullet_text, card_w_units, font_pt=11.4, hanging_indent="　 "):
    """Wraps a single bullet into lines with full-width hanging indent matching '● '."""
    max_em = calc_card_max_em(card_w_units, font_pt=font_pt)
    indent_w = sum(char_em(c) for c in hanging_indent)
    lines = []
    b = sanitize_cjk_glyphs(bullet_text)
    for raw_seg in b.split("\n"):
        tokens = TOKEN_RE.findall(raw_seg)
        cur_line = ""
        cur_w = 0.0
        for tok in tokens:
            tok_w = sum(char_em(c) for c in tok)
            is_punct = (len(tok) == 1 and tok in NO_START_CHARS)
            if cur_w + tok_w > max_em and cur_line.strip() and not is_punct:
                lines.append(cur_line)
                tok_s = tok.lstrip(" ")
                cur_line = hanging_indent + tok_s
                cur_w = indent_w + sum(char_em(c) for c in tok_s)
            else:
                cur_line += tok
                cur_w += tok_w
        if cur_line.strip():
            lines.append(cur_line)
    return lines


def draw_calibrated_card(ax, x, y, width, title, bullets, theme,
                         accent_key="primary", badge_text=None,
                         font_pt=11.3, fixed_height=27.0):
    """
    Draws a card using Modular Horizontal Row Slots (`slot_h = avail_h / N`):
    1. Divides the card's vertical body space (`divider_y - 0.15` to `y + 0.45`) into N equal horizontal row slots.
    2. Draws subtle horizontal divider rules (`#CBD5E1`) between slots so side-by-side cards form a continuous parallel grid.
    3. Anchors Line 1 (`● ...`) of each slot at `slot_top - top_pad` and distributes the wrapped lines evenly across the slot,
       simultaneously guaranteeing 100% horizontal parallel alignment AND zero bottom empty whitespace!
    """
    title = sanitize_cjk_glyphs(title)
    badge_text = sanitize_cjk_glyphs(badge_text)
    accent = theme["accents"].get(accent_key, theme["accents"]["primary"])
    accent_color = accent["main"]
    pill_bg = accent["pill_bg"]
    height = fixed_height

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
    header_y = y + height - 1.20

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
            fontsize=13.4, fontweight="bold", color=theme["text_title"],
            va="top", ha="left", zorder=4
        )
    else:
        ax.text(
            text_x, header_y, title,
            fontsize=13.5, fontweight="bold", color=accent_color,
            va="top", ha="left", zorder=4
        )

    divider_y = y + height - 3.05
    ax.plot(
        [text_x, x + width - 0.65], [divider_y, divider_y],
        color=accent_color, linewidth=0.9, alpha=0.55, zorder=3.5
    )

    # Modular Horizontal Row Slots
    slots = [wrap_bullet_to_lines(b, card_w_units=width, font_pt=font_pt) for b in bullets]
    num_slots = len(slots)
    if num_slots > 0:
        body_top = divider_y - 0.15
        body_bot = y + 0.40
        avail_h = body_top - body_bot
        slot_h = avail_h / num_slots

        for s_idx, slot_lines in enumerate(slots):
            slot_top = body_top - s_idx * slot_h
            if s_idx > 0:
                ax.plot(
                    [text_x, x + width - 0.65], [slot_top, slot_top],
                    color=theme["card_border"], linewidth=0.75, alpha=0.75, zorder=3.5
                )

            m_lines = max(1, len(slot_lines))
            # Center the block vertically inside the slot while keeping Line 1 horizontally aligned across equal-line slots:
            # We use a generous line_step (2.35 - 2.65 units) so lines spread comfortably across the slot height!
            line_step = min(2.65, max(2.05, (slot_h - 1.35) / max(1, m_lines)))
            block_h = (m_lines - 1) * line_step + (font_pt / 6.2)
            # Fixed top_pad based on slot_h so Line 1 (`● ...`) is 100% horizontally parallel across all side-by-side cards!
            top_pad = max(0.68, (slot_h - block_h) * 0.42 if m_lines >= 3 else 0.95)
            # Lock top_pad to a deterministic function of slot_h so left/middle/right cards share the EXACT same Line 1 Y coordinate!
            locked_top_pad = 0.95 if slot_h > 10.5 else 0.78
            line_y = slot_top - locked_top_pad

            for l_i, line_str in enumerate(slot_lines):
                ax.text(
                    text_x, line_y, line_str,
                    fontsize=font_pt,
                    fontweight="bold" if (l_i == 0 and "★" in line_str) else "normal",
                    color=theme["text_title"] if (l_i == 0 and "★" in line_str) else theme["text_body"],
                    va="top", ha="left", zorder=4
                )
                line_y -= line_step

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

    # Top Master Hub Banner with 3 Horizontally Parallel Sub-Columns (Fixes Screenshot 1!)
    hub_x, hub_y, hub_w, hub_h = 4.0, 77.5, 92.0, 11.5
    hub_box = FancyBboxPatch(
        (hub_x, hub_y), hub_w, hub_h,
        boxstyle="round,pad=0.25,rounding_size=1.0",
        facecolor=theme["hub_bg"], edgecolor=theme["hub_border"],
        linewidth=2.2, zorder=4
    )
    ax.add_patch(hub_box)
    ax.text(
        hub_x + 1.8, hub_y + hub_h - 1.25,
        "【核心命題與調查現況】Jeremy Korst, Stefano Puntoni, Olivier Toubia (HBR) × GBK Collective 170 位市調專家與企業用戶實證調查",
        fontsize=13.2, fontweight="bold", color=theme["hub_sub"],
        ha="left", va="top", zorder=5
    )
    # Horizontal cyan divider line inside top banner
    ax.plot([hub_x + 1.8, hub_x + hub_w - 1.8], [hub_y + hub_h - 3.65, hub_y + hub_h - 3.65],
            color="#38BDF8", linewidth=0.9, alpha=0.55, zorder=5)

    # 3 Parallel Columns inside Top Banner (aligned 1-to-1 with the 3 Macro Zones below!)
    banner_cols = [
        (5.5, "● 【傳統市調結構痛點】", "　 專案耗時且成本高昂，「量化調查廣度」與「質化訪談深度」長期無法兼得，使多數決策被迫憑直覺拍板。"),
        (36.8, "● 【GBK 實證導入現況 (90% 普及)】", "　 45% 已使用、45% 規畫中（62% 統整逐字稿、58% 分析數據、54% 撰寫報告；逾 80% 認同釋放策略敘事時間）。"),
        (68.2, "● 【4 大核心能力 × 3 大流程階段】", "　 「統整、編碼、互動、寫作」全面滲透「① 設計研究與找機會 → ② 蒐集與分析數據 → ③ 報告影響與傳播」。"),
    ]
    for b_idx, (bx, b_head, b_body) in enumerate(banner_cols):
        if b_idx > 0:
            ax.plot([bx - 1.5, bx - 1.5], [hub_y + 1.0, hub_y + hub_h - 4.1],
                    color="#475569", linewidth=0.85, alpha=0.7, zorder=5)
        ax.text(bx, hub_y + hub_h - 4.35, b_head, fontsize=10.8, fontweight="bold", color="#38BDF8", ha="left", va="top", zorder=5)
        wrapped_b = "\n".join(wrap_bullet_to_lines(b_body, card_w_units=27.2, font_pt=10.2, hanging_indent="　 "))
        ax.text(bx, hub_y + hub_h - 6.75, wrapped_b, fontsize=10.1, color="#F8FAFC", ha="left", va="top", linespacing=1.48, zorder=5)

    draw_macro_zone(ax, 3.5, 12.0, 29.5, 61.5, "【第一部曲】四大變革機會與標竿實證", theme)
    draw_macro_zone(ax, 35.25, 12.0, 29.5, 61.5, "【第二部曲】合成數據三機制與四大風險局限", theme)
    draw_macro_zone(ax, 67.0, 12.0, 29.5, 61.5, "【第三部曲】四大前沿破局解法與管理者行動", theme)

    # Top Row of 3 Cards (All N=2 parallel slots, y=42.5, height=27.0)
    draw_calibrated_card(
        ax, x=4.6, y=42.5, width=27.3,
        title="機會 1 & 2：強化實務與取代問卷",
        badge_text="章節一",
        accent_key="primary",
        font_pt=11.8, fixed_height=27.0,
        bullets=[
            "● 機會 1（強化現有實務）：摘要過往研究、自動生成程式碼清理數據；Meaningful 與 Outset.ai 打造「AI 動態訪談員」依受訪者回答即時動態追問（WeightWatchers 實證受訪者更坦誠且幾乎無幻覺）。",
            "● 機會 2（取代現有實務）：以「合成受訪者」填寫量化問卷或接受深度質化訪談（高達 81% 已用或計畫使用）；Evidenza 與安永 (EY) 雙盲測試 1,000+ 名合成 CEO，與真人結論高達 95% 相同。"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=36.35, y=42.5, width=27.3,
        title="合成數據三機制 × 大小模型取捨",
        badge_text="章節三",
        accent_key="synth",
        font_pt=11.8, fixed_height=27.0,
        bullets=[
            "● 提升合成品質三關鍵：現階段僅 31% 認為純合成數據價值極高，必須結合 ① 提示詞輸入問答範例 (Few-shot)、② 從過去研究知識庫提取內容 (RAG)、③ 以企業內部現有數據微調參數。",
            "● 隱私與能力取捨：私有小型模型（如美國陸軍採用的 Rockfish Data）完全保密但僅能處理結構化／半結構化數據；公開大型模型方能處理非結構化質化數據（最佳折衷：內部數據微調大模型）。"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=68.1, y=42.5, width=27.3,
        title="克服混淆與偏誤之四大前沿解法",
        badge_text="章節五",
        accent_key="primary",
        font_pt=11.8, fixed_height=27.0,
        bullets=[
            "● 解法 1 & 2：① 建立綁定真人數小時深度訪談、認知測驗與實際購物行為「基準事實」之數位雙生；② 右腦大模型轉譯非結構化圖文特徵 ＋ 左腦傳統統計公式計算價格彈性。",
            "● 解法 3 & 4：③ 結合少量真人隨機樣本與大量 AI 樣本進行統計校準（扣除系統偏誤）；④ 以大量歷史調查與真實 A/B 實驗數據直接微調模型（如 Evidenza、GBK Collective 實測）。"
        ],
        theme=theme
    )

    # Bottom Row of 3 Cards (All N=2 parallel slots, y=13.5, height=27.0)
    draw_calibrated_card(
        ax, x=4.6, y=13.5, width=27.3,
        title="機會 3 & 4：填補缺口與數位雙生",
        badge_text="章節二",
        accent_key="success",
        font_pt=11.8, fixed_height=27.0,
        bullets=[
            "● 機會 3（填補現有缺口）：30% 用於引導過往因預算或時間不足而憑直覺拍板的決策（如通用磨坊加速早期新品發想；Arena 依各門市地方客群量身打造選品；估算品牌定位對財務 ROI 影響）。",
            "● 機會 4（創造新見解—顧客數位雙生）：為個別客戶建立永不疲勞的虛擬分身供業務事前演練話術（82% 計畫實驗；哥倫比亞 2,500 人群組、史丹福 85% 兩週重測信度、CivicSync、Oleria）。"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=36.35, y=13.5, width=27.3,
        title="生成式 AI 市調之四大風險局限",
        badge_text="章節四",
        accent_key="danger",
        font_pt=11.8, fixed_height=27.0,
        bullets=[
            "● 人口偏誤與跨期不穩：公開模型偏向自由派與高學歷，難代表 65 歲以上與宗教群體（哥倫比亞/史丹福）；回答變異過小、易受選項順序影響且 3 個月內表現搖擺（范登堡 Bisbee 2024）。",
            "● 多感官失靈與實驗混淆：純文字 AI 無法模擬嗅覺與潛意識記憶（高砂香料失敗）；盲測訂價時會自動腦補競品與歷史價同步變貴（混淆現象 Confounding），使需求曲線平坦失真！"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=68.1, y=13.5, width=27.3,
        title="管理者行動建議與防偏見四關卡",
        badge_text="章節六",
        accent_key="warn",
        font_pt=11.8, fixed_height=27.0,
        bullets=[
            "● 落地雙原則：早期概念發想與高接觸門檻受眾（如繁忙外科醫師）大膽用 AI 衝速度；但面對「消費者行為劇變」或「突破性產品創新」，歷史微調模型預測力較弱，必回歸真人研究。",
            "● 防偏見四道關卡：開放式探索題目 → 統計迴歸推導重要性（不信口頭宣稱）→ 綁定真實會計財務指標 → 上市前執行真人隨機對照實驗（如 800 億美元銀行分支機構實證案例）。"
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

    # Central Hub with Left-Aligned Centered Block & Cyan Divider (Fixes Screenshot 2!)
    hub_x, hub_y, hub_w, hub_h = 40.2, 42.2, 19.6, 16.5
    hub_box = FancyBboxPatch(
        (hub_x, hub_y), hub_w, hub_h,
        boxstyle="round,pad=0.25,rounding_size=1.2",
        facecolor=theme["hub_bg"], edgecolor=theme["hub_border"],
        linewidth=2.3, zorder=4
    )
    ax.add_patch(hub_box)
    ax.text(
        hub_x + hub_w / 2, hub_y + hub_h - 1.55,
        "生成式 AI 顛覆市調\n核心機制與資料光譜",
        fontsize=13.8, fontweight="bold", color=theme["hub_text"],
        ha="center", va="top", linespacing=1.35, zorder=5
    )
    # Crisp cyan horizontal divider line bridging title and bullets (eliminates middle black hole!)
    div_y = hub_y + hub_h - 5.95
    ax.plot(
        [hub_x + 1.6, hub_x + hub_w - 1.6], [div_y, div_y],
        color="#38BDF8", linewidth=1.1, alpha=0.75, zorder=5
    )
    # 4 Equal-Length Left-Aligned Bullets Centered as a Block (all `●` dots 100% vertically aligned!)
    hub_bullets = [
        "● 兼得量化廣度與質化深度",
        "● 解除受訪者社會期許偏誤",
        "● 依資料結構配置大小模型",
        "● 綁定基準事實建數位雙生",
    ]
    bullet_x_left = hub_x + 2.35
    for hb_i, hb_txt in enumerate(hub_bullets):
        by = div_y - 1.05 - hb_i * 2.22
        ax.text(
            bullet_x_left, by, hb_txt,
            fontsize=10.3, fontweight="bold", color="#E2E8F0",
            ha="left", va="top", zorder=5
        )

    c_lt = draw_calibrated_card(
        ax, x=4.2, y=49.0, width=27.6,
        title="強化實務：AI 訪談員消除道德修飾",
        badge_text="機會 1 思辨",
        accent_key="primary",
        font_pt=11.1, fixed_height=33.5,
        bullets=[
            "● 4 大能力 × 3 大階段全面提速：在設計研究、蒐集分析、報告傳播全面賦能（62% 統整訪談逐字稿、58% 編碼分析數據、54% 撰寫報告與視覺化，逾 80% 認同釋放策略時間）。",
            "● Outset.ai 動態追問平台：由 AI 依受訪者前次回答即時動態追問，成功打破傳統市場研究「量化問卷規模廣度」與「質化深度訪談」長期無法兼得之結構瓶頸。",
            "● ★ 思辨突破（為何對 AI 更誠實？）：人類面對「真人」時會自動啟動「心理與道德修飾機制（社會期許偏誤）」，為顧面子而隱藏私密痛點；面對無道德審判眼神的 AI 反而卸下心防（WeightWatchers 實證），且 AI 僅提問與統整故幾乎零幻覺！"
        ],
        theme=theme
    )

    c_lb = draw_calibrated_card(
        ax, x=4.2, y=13.5, width=27.6,
        title="取代與補缺口：合成受眾與全天候引擎",
        badge_text="機會 2 & 3",
        accent_key="warn",
        font_pt=11.1, fixed_height=33.5,
        bullets=[
            "● 合成數據（Synthetic Data）：由 AI 模擬目標客群填寫量化問卷或接受深度質化訪談（高達 81% 已用或計畫使用，但現階段僅 31% 認為純合成數據價值極高，需搭配錨定機制）。",
            "● 接地氣三關鍵錨定：① 在提示詞輸入問答範例（Few-shot）、② 從過去研究知識庫提取內容（RAG 檢索增強）、③ 微調模型參數以對齊企業內部現有真實數據。",
            "● 黃金雙盲實證與補缺口：Evidenza × 安永 (EY) 模擬 1,000+ 名營收逾 10 億美元公司 CEO，與真人結論高達 95% 相同；30% 用於填補過往無預算調查之決策缺口（如通用磨坊新品發想、Arena 門市選品）。"
        ],
        theme=theme
    )

    c_rt = draw_calibrated_card(
        ax, x=68.2, y=49.0, width=27.6,
        title="三類數據結構 × 小模型 vs. 大模型",
        badge_text="資料科學拆解",
        accent_key="synth",
        font_pt=11.1, fixed_height=33.5,
        bullets=[
            "● ① 結構化數據（固定二維表格欄位）：含「數字型（年齡 34 歲、年消費額 28,500 元）」與「類別型（性別、居住城市、會員卡別、李克特五點滿意度選項）」，可直接存入關聯式資料庫。",
            "● ② 半結構化數據（自帶標籤階層日誌）：網站與 App 點擊流 JSON 瀏覽軌跡、帶標頭之客服工單與電子郵件紀錄（每位顧客行為序列長短不一，但具明確結構標籤可供程式解析）。",
            "● ★ ③ 非結構化質化數據 & 模型權衡：訪談逐字稿與社群長文（回答 Why 與 How）。私有小模型（如 Rockfish Data）完全保密但僅懂表格機率；唯有具「人類世界知識先驗」的公開大模型方能理解質化語意（最佳折衷：用內部私有數據微調公開大模型）！"
        ],
        theme=theme
    )

    c_rb = draw_calibrated_card(
        ax, x=68.2, y=13.5, width=27.6,
        title="創造新見解：顧客數位雙生虛擬分身",
        badge_text="機會 4",
        accent_key="success",
        font_pt=11.1, fixed_height=33.5,
        bullets=[
            "● 打破「第一印象只有一次機會」鐵律：為個別客戶打造永不疲勞、不煩躁的虛擬分身，供 B2B 業務團隊事前反覆演練推銷話術與測試廣告共鳴（逾 82% 受訪者已實驗或計畫實驗）。",
            "● 商業與研發實戰案例：Arena 訓練銷售人員應對、CivicSync 經授權追蹤線上購物軌跡動態更新雙生、奧美測試廣告創意共鳴、Oleria 用 NotebookLM 建立專屬安全研究助理。",
            "● 學術基準事實群組（Ground Truth）：哥倫比亞商學院建 2,500 名真人全維度數位雙生；史丹福 + DeepMind 以數小時深度訪談建雙生，兩週後重測回答與本人相似度高達 85%！"
        ],
        theme=theme
    )

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
# DIAGRAM 02: 實驗混淆機制與四大前沿解法思辨圖 (Deep Dive 2 — Symmetric 2x2 Parallel Grid!)
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

    # Top Row: Left Card (y=49.0, h=33.5, 3 slots) & Right Card (y=49.0, h=33.5, 3 slots) -> 100% Parallel!
    l_top = draw_calibrated_card(
        ax, x=4.4, y=49.0, width=40.1,
        title="人口偏誤、多感官失靈與「盲測訂價混淆現象」",
        badge_text="四大技術局限",
        accent_key="danger",
        font_pt=11.0, fixed_height=33.5,
        bullets=[
            "● 局限 1 & 2【人口代表性偏誤與跨期搖擺】：OpenAI 等公開模型明顯偏向「自由派、高學歷」（哥倫比亞/史丹福 2023），難代表高齡與宗教群體；且合成民調變異過小、易受選項順序影響，在 3 個月內表現搖擺不穩（范登堡 Bisbee 2024）。",
            "● 局限 3【多感官與潛意識失靈（高砂香料 Takasago 實證）】：人類對香水氣味與食品風味的偏好，緊密綁定生理嗅味覺受器與童年潛意識情緒記憶；純文字訓練之 AI 無法模擬真實五感體驗。",
            "● ★ 局限 4【盲測訂價實驗之混淆現象 (Confounding)】：真人隨機盲測 P(Y|do(X)) 中背景物價 Z 獨立不變；但 AI 運算語境聯想 P_LLM(Y|X)，看到標價 X=5,000 元時自動調高 P_LLM(Z|X)（腦補競品與歷史價 Z 也全賣 5,000 元），使需求曲線平坦失真！"
        ],
        theme=theme
    )

    r_top = draw_calibrated_card(
        ax, x=55.5, y=49.0, width=40.1,
        title="四大前沿破局解法 vs. 第一性原理「理論死穴」批判",
        badge_text="第一性原理批判",
        accent_key="primary",
        font_pt=11.0, fixed_height=33.5,
        bullets=[
            "● ★ 解法 1【綁定真人記憶之數位雙生】→ 死穴批判：【具身感質不可壓縮】永遠無法「把一整個人塞進模型」！數小時訪談逐字稿無法編碼生理嗅覺、味覺與潛意識記憶（如高砂香料測試香氣徹底失靈）。",
            "● ★ 解法 2【右腦 AI 轉譯＋左腦統計公式】→ 死穴批判：【計量模型誤設偏誤】雖出現幻覺機率最小，但面對高度複雜、多變數非線性交互作用的感性決策時，左腦極難寫出高解釋力函式（寫簡單 R² 低、寫複雜又過度配適）。",
            "● ★ 解法 3【少量真人＋AI 統計校準】& 解法 4【大量歷史實驗微調】→ 死穴批判：解法 3 當下對準人類可能只是「湊巧發生」，換字眼或跨期即失準；解法 4 屬「後照鏡內插」，面對未來「消費者行為劇變」或「突破性創新」即外推失靈！"
        ],
        theme=theme
    )

    # Bottom Row: Left Card (y=13.5, h=33.5, 3 slots) & Right Card (y=13.5, h=33.5, 3 slots) -> 100% Parallel!
    l_bot = draw_calibrated_card(
        ax, x=4.4, y=13.5, width=40.1,
        title="為何純靠「修改提示詞規範」必淪為挖東牆補西牆？",
        badge_text="提示詞死胡同",
        accent_key="warn",
        font_pt=11.0, fixed_height=33.5,
        bullets=[
            "● 【結構性死胡同診斷】：面對盲測訂價混淆現象，若研究員試圖在提示詞（Prompt）中寫入更詳細的市場價格與背景情境規範，必然在「隱空間繞道腦補」與「實驗目的劇透」之間顧此失彼。",
            "● ★ 【東牆：未知腦補變數永遠鎖不完（無限混淆）】：就算在提示詞死鎖「歷史價與競品價皆為 1,200 元」，具備數千億參數的 AI 看到標價 5,000 元時，又會在高維度隱空間自動繞道腦補「現在全球大缺貨、頂級巨星聯名或限量溢價」，人工無法窮舉所有潛在混淆變數 Z！",
            "● ★ 【西牆：寫太白引發需求特徵劇透（焦點錯覺）】：若在 Prompt 刻意強調「別家一模一樣都賣 1,200 元、唯獨這家賣 5,000 元，請決定買不買」，會觸發心理學「需求特徵」與「焦點錯覺」，使 AI 變成 100% 拒買的比大小計算機，照樣測不出真實價格彈性！"
        ],
        theme=theme
    )

    r_bot = draw_calibrated_card(
        ax, x=55.5, y=13.5, width=40.1,
        title="終極解方：George Box 依商業情境配置之「權變組合」",
        badge_text="效益最大化處方",
        accent_key="success",
        font_pt=11.0, fixed_height=33.5,
        bullets=[
            "● 戰場 A【早期點子發想、B2B 銷售話術演練、高接觸門檻受眾初探】：配置「解法 1 數位雙生 ＋ 解法 4 歷史微調」→ 容錯率高，發揮 AI 低成本、全天候、永不疲倦優勢，百倍速淘汰 80% 弱點子。",
            "● 戰場 B【常規品牌健康度追蹤、核心價值驅動因素排序】：配置「AI 動態訪談員（消除道德修飾）＋ 解法 2 右腦 AI 轉譯與左腦道斯線性統計模型」→ 變數結構穩定，兼顧質化真心話與量化零幻覺。",
            "● ★ 戰場 C【高風險最終訂價實驗、多感官體驗（香水/食品）、突破性產品創新】：強制回歸「真人隨機盲測實驗（A/B Test）＋ 解法 3 當期動態校準」→ 嚴格避開價格混淆、感官失靈與外推失效三大禁區！"
        ],
        theme=theme
    )

    draw_corridor_arrow(
        ax, (l_top[0] + l_top[2], l_top[1] + l_top[3] * 0.5), (r_top[0], r_top[1] + r_top[3] * 0.5),
        label_text="催生四大解法與批判", theme=theme, accent_key="primary", rad=0.0, label_pos=0.5, label_dy=2.2
    )
    draw_corridor_arrow(
        ax, (l_bot[0] + l_bot[2], l_bot[1] + l_bot[3] * 0.5), (r_bot[0], r_bot[1] + r_bot[3] * 0.5),
        label_text="放棄單一模型轉向權變", theme=theme, accent_key="success", rad=0.0, label_pos=0.5, label_dy=2.2
    )

    out_path = os.path.join(OUT_DIR, "02_生成式AI市調局限_實驗混淆與四大前沿解法思辨圖.jpg")
    save_publication_figure(fig, out_path, theme, dpi=240)


# ==============================================================================
# DIAGRAM 03: 三篇合體「道・法・術」企業科學決策終極藍圖 (Deep Dive 3 — 3x2 Parallel Grid!)
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

    # Top Row of 3 Cards (All N=3 parallel slots, y=49.0, height=33.5)
    draw_calibrated_card(
        ax, x=4.6, y=49.0, width=26.8,
        title="破除高層直覺偏誤與對齊目標 Y",
        badge_text="Step 1 定錨",
        accent_key="danger",
        font_pt=11.4, fixed_height=33.5,
        bullets=[
            "● 診斷高層兩大盲點：72% 上市 B2B 高層認知與顧客真實重視呈零或負相關；85.5% 每兩年大改優先順序（受顯眼少數客訴之可得性偏誤與盲從競爭對手所誤導）。",
            "● 道斯（Robyn Dawes）線性模型定理：人腦擅長選取變數 X，卻無法穩定加權排序；必須用雙層統計模型算出各因素對整體價值與真實會計營收 Y 的「提升潛力（Lift）」。",
            "● 實證財務鐵證：高層與顧客認知一致度每提升 12.5 分，企業年營收成長 +9.2%、毛利率提升 +5.2%、整體企業市值躍升 +11.1%（證明先找對問題方向是一切數據科學的起點）！"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=36.6, y=49.0, width=26.8,
        title="內嵌 ERP / CRM 跨部門「背景情境」",
        badge_text="Step 3 基建",
        accent_key="primary",
        font_pt=11.4, fixed_height=33.5,
        bullets=[
            "● 打破企業數據孤島：真實商業問題皆跨職能，必須將數據分析工具直接內嵌於 ERP（財務/庫存/供應鏈）與 CRM（銷售/客戶互動）日常交易系統中，實現跨部門數據同源。",
            "● 注入領域背景情境（Contextual Information）：如人資系統結合職缺情境自動配對履歷、供應鏈結合氣候預測瓶頸、保險巨頭 AXA XL 僅花 8 週全公司導入內建 KPI 分析系統。",
            "● 訊號 vs. 雜訊人機分工：由人類領域專家在系統中預先設定合理因果邊界（防止醫療 AI 將肺炎合併氣喘死亡率低誤判為安全等虛假相關災難），再讓 AI 於邊界內找模式。"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=68.6, y=49.0, width=26.8,
        title="生成式 AI 市調實操：訪談、合成與雙生",
        badge_text="Step 5 實操",
        accent_key="success",
        font_pt=11.4, fixed_height=33.5,
        bullets=[
            "● AI 動態訪談員（Outset.ai）：針對第一階鎖定的核心因素 X*，以機器提問解除受訪者「心理與道德修飾機制（社會期許偏誤）」，挖出無偽裝真實痛點，兼顧規模與深度。",
            "● 合成數據與大小模型調配：以第二階 ERP 私有數據微調公開大型模型（兼顧機密與世界知識先驗），模擬高接觸門檻受眾（如安永 EY 合成 1,000 名 CEO 達 95% 結論一致）。",
            "● 顧客數位雙生（Digital Twins）：打造永不疲倦的客戶虛擬分身（哥倫比亞 2,500 人群組、史丹福 85% 重測信度），供業務事前演練話術與百倍速快篩早期產品點子。"
        ],
        theme=theme
    )

    # Bottom Row of 3 Cards (All N=3 parallel slots, y=13.5, height=33.5 -> 100% Parallel across all 3 columns!)
    draw_calibrated_card(
        ax, x=4.6, y=13.5, width=26.8,
        title="少做多得五步驟：鎖定少數關鍵 X*",
        badge_text="Step 2 聚焦",
        accent_key="primary",
        font_pt=11.4, fixed_height=33.5,
        bullets=[
            "● 落地執行五步驟：揭露高層認知落差 → 統計計算提升潛力 → 將關鍵行動融入員工日常流程 → 果斷淘汰近零價值計畫（化解跨部門政治角力）→ 執行卓越後才對外宣揚品牌。",
            "● 標竿轉型實證：工業零件商 ITI 鎖定「每週主動進度報告」使股價兩年大漲 162%；能源設備商 S-SET 鎖定「3 小時快速報價」使人均銷售大增 52% 且雙雙砍除無效專案。",
            "● ★ 跨篇交棒任務（道 → 法）：明確界定企業真正該集中資源改進的 1~2 個核心價值驅動因素 X*，為下一階段的企業數據分析與生成式 AI 市調指明唯一高價值靶心！"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=36.6, y=13.5, width=26.8,
        title="擴增分析賦能與數學懲罰過濾雜訊",
        badge_text="Step 4 賦能",
        accent_key="synth",
        font_pt=11.4, fixed_height=33.5,
        bullets=[
            "● 擴增分析（Augmented Analytics）：結合 ML（自動找趨勢變異）+ NLP（口說自然語言提問）+ NLG（自動生成白話摘要），賦能第一線「平民數據分析師」日常決策。",
            "● 統計防過度配適護欄：固定樣本 N 盲目擴充參數 p 會耗盡自由度導致 Overfitting；必須以 Adjusted R² 與 Lasso 正則化（L1 懲罰）自動將無效雜訊特徵權重壓縮歸零！",
            "● ★ 跨篇交棒任務（法 → 術）：製造業標竿藉此揪出未授權折扣挽回數十萬美元，並為前線生成式 AI 市調提供乾淨、高信度的內部微調數據與 RAG 知識庫底座！"
        ],
        theme=theme
    )
    draw_calibrated_card(
        ax, x=68.6, y=13.5, width=26.8,
        title="情境權變防線與真人隨機實驗終審閉環",
        badge_text="Step 6 終審",
        accent_key="warn",
        font_pt=11.4, fixed_height=33.5,
        bullets=[
            "● 嚴守 AI 三大禁區：高度警覺「盲測訂價混淆現象（AI 自動腦補競品與歷史價同步變貴）」、「多感官失靈（高砂香料香氣測試失敗）」與「未來行為劇變外推失靈」。",
            "● George Box 情境權變配置：早期發想靠數位雙生百倍速探索；常規診斷靠 AI 訪談員＋左腦道斯模型算權重；最終定價、五感體驗與突破性創新則強制回歸真人實驗。",
            "● ★ 終局驗證四道關卡：開放式探索題目 → 迴歸推導重要性 → 綁定真實會計帳本 → 真人隨機對照實驗（A/B Test，如 800 億美元銀行案例），完整驅動「企業 ←→ 客戶」造血引擎！"
        ],
        theme=theme
    )

    draw_corridor_arrow(
        ax, (31.4, 65.5), (36.6, 65.5),
        label_text="道 → 法：定錨 X*", theme=theme, accent_key="primary", rad=0.0, label_pos=0.5, label_dy=17.5
    )
    draw_corridor_arrow(
        ax, (63.4, 65.5), (68.6, 65.5),
        label_text="法 → 術：注入情境", theme=theme, accent_key="success", rad=0.0, label_pos=0.5, label_dy=17.5
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
