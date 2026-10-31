# -*- coding: utf-8 -*-
"""
build_pptx_slides.py
Generates Format C (16:9 Widescreen Presentation Slides .pptx + Dual-Channel Markdown Script .md)
Strictly adheres to upgraded presentation_slide_spec.md (Post-E3 Standards):
1. Dynamic Pill Width & Left-Aligned Padding: Top-left header pill dynamically sizes to text length so text NEVER overflows the pill borders.
2. Zero Shrunk Mindmap Images (ISO 9241-303): Never embeds full-canvas .jpg mindmaps into slides; uses Native Large-Font PPTX Vector Diagrams (>= 12.5pt-14pt).
3. Horizontal Parallel Row Alignment (Müller-Brockmann Grid): Side-by-side cards align Bullet Row 1, Row 2, Row 3 at identical Y coordinates across columns, with 1.35x line spacing.
4. Peak-End Closing Slide (Kahneman Peak-End Rule): Includes a dedicated Final Closing & Action Summary Slide at the end of the presentation.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

OUT_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI顛覆市場研究\02_outputs"
PPTX_PATH = os.path.join(OUT_DIR, "生成式AI顛覆市場研究_深度思辨與三篇合體簡報.pptx")
MD_SCRIPT_PATH = os.path.join(OUT_DIR, "生成式AI顛覆市場研究_斷言證據簡報腳本.md")

# Color Palette (McKinsey Executive + Knaflic 80/20 Preattentive Spotlight)
C_NAVY_DARK  = RGBColor(15, 23, 42)      # #0F172A Deep Slate Navy
C_NAVY_MED   = RGBColor(30, 58, 138)     # #1E3A8A Executive Blue
C_SLATE_TXT  = RGBColor(30, 41, 59)      # #1E293B Body Ink
C_MUTED_TXT  = RGBColor(71, 85, 105)     # #475569 Context Text
C_BG_CANVAS  = RGBColor(248, 250, 252)   # #F8FAFC Warm Alabaster
C_CARD_BG    = RGBColor(255, 255, 255)   # #FFFFFF Pure Card Surface
C_ROW_ALT    = RGBColor(248, 250, 252)   # #F8FAFC Subtle Row Fill
C_BORDER_MUT = RGBColor(203, 213, 225)   # #CBD5E1 Neutral Context Border

# Spotlight Accent Colors (10% Preattentive Quota)
C_SPOT_BLUE   = RGBColor(30, 64, 175)    # #1E40AF Spotlight Primary
C_SPOT_BG     = RGBColor(239, 246, 255)  # #EFF6FF Spotlight Soft Blue Fill
C_SPOT_RED    = RGBColor(190, 18, 60)    # #BE123C Spotlight Alert / Critique
C_SPOT_REDBG  = RGBColor(255, 241, 242)  # #FFF1F2 Spotlight Soft Rose Fill
C_SPOT_GOLD   = RGBColor(180, 83, 9)     # #B45309 Spotlight Amber / Math
C_SPOT_GOLDBG = RGBColor(255, 251, 235)  # #FFFBEB Spotlight Soft Amber Fill
C_SPOT_TEAL   = RGBColor(4, 120, 87)     # #047857 Spotlight Emerald
C_SPOT_TEALBG = RGBColor(236, 253, 245)  # #ECFDF5 Spotlight Soft Emerald Fill
C_SKY_LIGHT   = RGBColor(56, 189, 248)   # #38BDF8 Cover Accent
C_WHITE       = RGBColor(255, 255, 255)

FONT_CJK = "Microsoft JhengHei"


def calc_pill_width(text_str, font_pt=9.5, pad_in=0.42):
    """Calculates dynamic width in inches so text never overflows a rounded pill."""
    cjk_count = sum(1 for ch in text_str if ord(ch) > 127)
    ascii_count = len(text_str) - cjk_count
    char_in = (font_pt / 72.0) * (cjk_count * 1.08 + ascii_count * 0.60)
    return max(2.2, min(11.8, char_in + pad_in))


def set_slide_bg(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_speaker_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text


def add_zone1_header(slide, slide_num_str, act_tag, assertion_headline):
    """
    Zone 1: Top 15% Height (0.0" to 1.18") - Sentence Assertion Headline
    Fixes User Point 7: Dynamically sizes the top-left pill width to fit the full string
    with comfortable left/right padding so text NEVER spills outside the badge!
    """
    header_bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.18)
    )
    header_bg.fill.solid()
    header_bg.fill.fore_color.rgb = C_WHITE
    header_bg.line.color.rgb = C_BORDER_MUT
    header_bg.line.width = Pt(1)

    accent = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.12), Inches(1.18)
    )
    accent.fill.solid()
    accent.fill.fore_color.rgb = C_NAVY_MED
    accent.line.fill.background()

    full_tag_str = f"{slide_num_str}  |  {act_tag}"
    pill_w = calc_pill_width(full_tag_str, font_pt=9.5, pad_in=0.48)
    pill = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.35), Inches(0.11), Inches(pill_w), Inches(0.30)
    )
    pill.adjustments[0] = 0.5
    pill.fill.solid()
    pill.fill.fore_color.rgb = C_NAVY_DARK
    pill.line.fill.background()
    tf_p = pill.text_frame
    tf_p.word_wrap = False
    tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_p.margin_left = Inches(0.18)
    tf_p.margin_right = Inches(0.18)
    tf_p.margin_top = tf_p.margin_bottom = 0
    p = tf_p.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = full_tag_str
    run.font.name = FONT_CJK
    run.font.size = Pt(9.5)
    run.font.bold = True
    run.font.color.rgb = C_SKY_LIGHT

    tb = slide.shapes.add_textbox(Inches(0.35), Inches(0.45), Inches(12.6), Inches(0.68))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = assertion_headline
    run.font.name = FONT_CJK
    run.font.size = Pt(19.5)
    run.font.bold = True
    run.font.color.rgb = C_NAVY_DARK


def add_zone3_footer(slide, takeaway_text):
    """Zone 3: Bottom 10% Height (6.82" to 7.50") - Action Takeaway Banner"""
    banner = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(6.82), Inches(13.333), Inches(0.68)
    )
    banner.fill.solid()
    banner.fill.fore_color.rgb = C_NAVY_DARK
    banner.line.fill.background()

    strip = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(6.82), Inches(13.333), Inches(0.05)
    )
    strip.fill.solid()
    strip.fill.fore_color.rgb = C_SKY_LIGHT
    strip.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(0.40), Inches(6.92), Inches(12.5), Inches(0.48))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = f"★ 決策行動啟示 (So-What)：{takeaway_text}"
    run.font.name = FONT_CJK
    run.font.size = Pt(12.5)
    run.font.bold = True
    run.font.color.rgb = C_WHITE


def add_parallel_cards(slide, cards_spec, top=1.40, height=5.20, row_heights=None):
    """
    Fixes User Point 9 (Müller-Brockmann Horizontal Parallel Row Alignment & 1.35x Line Spacing):
    Draws multiple side-by-side cards where each bullet item (head, body) is placed in its own
    horizontally aligned row slot across all cards, ensuring Bullet 1, Bullet 2, Bullet 3
    start at the EXACT same vertical Y coordinate across columns!
    cards_spec: list of dicts:
      {
        "left": float, "width": float,
        "tag": str, "title": str,
        "rows": [(bullet_head_str, bullet_body_str), ...],
        "is_spotlight": bool, "spot_color": RGBColor, "spot_bg": RGBColor
      }
    """
    header_zone_h = 1.12
    num_rows = max(len(c["rows"]) for c in cards_spec)
    avail_rows_h = height - header_zone_h - 0.12
    if row_heights is None:
        row_heights = [avail_rows_h / num_rows] * num_rows

    for c in cards_spec:
        left = c["left"]
        width = c["width"]
        is_spot = c.get("is_spotlight", False)
        spot_color = c.get("spot_color", C_SPOT_BLUE)
        spot_bg = c.get("spot_bg", C_SPOT_BG)

        # Card outer container
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
        )
        card.adjustments[0] = 0.025
        card.fill.solid()
        card.fill.fore_color.rgb = spot_bg if is_spot else C_CARD_BG
        card.line.color.rgb = spot_color if is_spot else C_BORDER_MUT
        card.line.width = Pt(2.4 if is_spot else 1.2)

        # Top color bar
        bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.09)
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = spot_color if is_spot else RGBColor(100, 116, 139)
        bar.line.fill.background()

        # Dynamic Tag Pill inside card
        tag_text = c["tag"]
        pill_w = min(width - 0.36, calc_pill_width(tag_text, font_pt=9.5, pad_in=0.36))
        pill = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left + 0.18), Inches(top + 0.18), Inches(pill_w), Inches(0.28)
        )
        pill.adjustments[0] = 0.45
        pill.fill.solid()
        pill.fill.fore_color.rgb = spot_color if is_spot else RGBColor(226, 232, 240)
        pill.line.fill.background()
        tf_p = pill.text_frame
        tf_p.word_wrap = False
        tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf_p.margin_left = Inches(0.12)
        tf_p.margin_right = Inches(0.12)
        tf_p.margin_top = tf_p.margin_bottom = 0
        p = tf_p.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = tag_text
        r.font.name = FONT_CJK
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = C_WHITE if is_spot else C_SLATE_TXT

        # Card Title
        tb_t = slide.shapes.add_textbox(Inches(left + 0.18), Inches(top + 0.52), Inches(width - 0.36), Inches(0.50))
        tf_t = tb_t.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        r_t = p_t.add_run()
        r_t.text = c["title"]
        r_t.font.name = FONT_CJK
        r_t.font.size = Pt(14)
        r_t.font.bold = True
        r_t.font.color.rgb = spot_color if is_spot else C_NAVY_DARK

        # Header divider line
        div = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(left + 0.18), Inches(top + 1.04), Inches(width - 0.36), Inches(0.018)
        )
        div.fill.solid()
        div.fill.fore_color.rgb = spot_color if is_spot else C_BORDER_MUT
        div.line.fill.background()

        # Parallel Bullet Rows (each row starts at exact same Y across all cards!)
        curr_y = top + header_zone_h
        for r_idx, (b_head, b_body) in enumerate(c["rows"]):
            r_h = row_heights[r_idx]
            if r_idx > 0:
                # Subtle horizontal row alignment divider
                r_div = slide.shapes.add_shape(
                    MSO_SHAPE.RECTANGLE, Inches(left + 0.18), Inches(curr_y - 0.04), Inches(width - 0.36), Inches(0.01)
                )
                r_div.fill.solid()
                r_div.fill.fore_color.rgb = RGBColor(203, 213, 225)
                r_div.line.fill.background()

            tb_r = slide.shapes.add_textbox(
                Inches(left + 0.18), Inches(curr_y), Inches(width - 0.36), Inches(r_h - 0.06)
            )
            tf_r = tb_r.text_frame
            tf_r.word_wrap = True
            tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = 0

            # Paragraph 1: Bold Bullet Header
            p_h = tf_r.paragraphs[0]
            p_h.line_spacing = 1.30
            p_h.space_after = Pt(3)
            rh = p_h.add_run()
            rh.text = b_head
            rh.font.name = FONT_CJK
            rh.font.size = Pt(12)
            rh.font.bold = True
            rh.font.color.rgb = spot_color if is_spot else C_NAVY_DARK

            # Paragraph 2: Comfortable 1.35x Line-Spaced Body
            p_b = tf_r.add_paragraph()
            p_b.line_spacing = 1.35
            rb = p_b.add_run()
            rb.text = b_body
            rb.font.name = FONT_CJK
            rb.font.size = Pt(11.2)
            rb.font.bold = False
            rb.font.color.rgb = C_SLATE_TXT

            curr_y += r_h


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

slides_md_records = []

# ==============================================================================
# SLIDE 01: 序幕 (Cover & Core Thesis)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_bg(s1, C_NAVY_DARK)

top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.14))
top_bar.fill.solid()
top_bar.fill.fore_color.rgb = C_SKY_LIGHT
top_bar.line.fill.background()

cover_tag = "HBR 深度閱讀與視覺化綜合產出  |  斷言—證據高階簡報 (Assertion-Evidence Deck)"
pill0_w = calc_pill_width(cover_tag, font_pt=11, pad_in=0.55)
pill0 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(0.60), Inches(pill0_w), Inches(0.38))
pill0.adjustments[0] = 0.5
pill0.fill.solid()
pill0.fill.fore_color.rgb = C_NAVY_MED
pill0.line.color.rgb = C_SKY_LIGHT
pill0.line.width = Pt(1.2)
tf0 = pill0.text_frame
tf0.word_wrap = False
tf0.vertical_anchor = MSO_ANCHOR.MIDDLE
tf0.margin_left = Inches(0.20)
p0 = tf0.paragraphs[0]
p0.alignment = PP_ALIGN.LEFT
r0 = p0.add_run()
r0.text = cover_tag
r0.font.name = FONT_CJK
r0.font.size = Pt(11)
r0.font.bold = True
r0.font.color.rgb = C_SKY_LIGHT

tb_title = s1.shapes.add_textbox(Inches(0.7), Inches(1.18), Inches(11.9), Inches(1.55))
tf_title = tb_title.text_frame
tf_title.word_wrap = True
p_t1 = tf_title.paragraphs[0]
p_t1.line_spacing = 1.25
r_t1 = p_t1.add_run()
r_t1.text = "《生成式 AI 正在顛覆市場研究》\n深度思辨與「道・法・術」三篇合體科學決策藍圖"
r_t1.font.name = FONT_CJK
r_t1.font.size = Pt(30)
r_t1.font.bold = True
r_t1.font.color.rgb = C_WHITE

thesis_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(2.95), Inches(11.9), Inches(1.55))
thesis_box.adjustments[0] = 0.04
thesis_box.fill.solid()
thesis_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
thesis_box.line.color.rgb = C_SKY_LIGHT
thesis_box.line.width = Pt(2)
tf_th = thesis_box.text_frame
tf_th.word_wrap = True
tf_th.margin_left = tf_th.margin_right = Inches(0.25)
tf_th.margin_top = Inches(0.16)
p_th = tf_th.paragraphs[0]
p_th.line_spacing = 1.35
r_th = p_th.add_run()
r_th.text = (
    "★ 全篇終極核心主張 (Core Thesis)：\n"
    "生成式 AI 能以「動態訪談員」卸下人類心理與道德偽裝、以「合成數據與數位雙生」百倍速擴張早期探索；"
    "但因天生運算「語境條件聯想」而非「獨立因果干預」，在盲測訂價與多感官領域必生混淆失靈。企業須以《顧客需求不靠猜》定錨問題（道）、以《AI 強化數據分析》打通 ERP 情境（法），再執行人機權變市調閉環（術）。"
)
r_th.font.name = FONT_CJK
r_th.font.size = Pt(13)
r_th.font.bold = True
r_th.font.color.rgb = C_WHITE

kpis = [
    ("90%", "市調機構導入與規畫率", "45% 已使用、45% 規畫中\n80%+ 認同釋放策略敘事時間"),
    ("95%", "安永雙盲測試結論一致率", "Evidenza 合成 1,000 名 CEO\n與真人調查結論高度吻合"),
    ("85%", "史丹福數位雙生重測信度", "綁定真人深度訪談與測驗\n兩週後回答相似度達 85%"),
    ("道・法・術", "三篇 HBR 合體決策閉環", "統計模型找 X* → ERP 情境底座\n→ 生成式市調與真人 A/B 終審"),
]
for idx, (big_num, k_title, k_sub) in enumerate(kpis):
    kx = 0.7 + idx * 3.04
    kcard = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(kx), Inches(4.80), Inches(2.82), Inches(2.05))
    kcard.adjustments[0] = 0.05
    kcard.fill.solid()
    kcard.fill.fore_color.rgb = RGBColor(23, 37, 84) if idx < 3 else RGBColor(6, 78, 59)
    kcard.line.color.rgb = C_SKY_LIGHT if idx < 3 else RGBColor(52, 211, 153)
    kcard.line.width = Pt(1.5)
    tf_k = kcard.text_frame
    tf_k.word_wrap = True
    tf_k.margin_left = tf_k.margin_right = Inches(0.18)
    tf_k.margin_top = Inches(0.16)
    pk1 = tf_k.paragraphs[0]
    rk1 = pk1.add_run()
    rk1.text = big_num
    rk1.font.name = FONT_CJK
    rk1.font.size = Pt(24)
    rk1.font.bold = True
    rk1.font.color.rgb = C_SKY_LIGHT if idx < 3 else RGBColor(110, 231, 183)

    pk2 = tf_k.add_paragraph()
    pk2.space_before = Pt(6)
    rk2 = pk2.add_run()
    rk2.text = k_title
    rk2.font.name = FONT_CJK
    rk2.font.size = Pt(12.5)
    rk2.font.bold = True
    rk2.font.color.rgb = C_WHITE

    pk3 = tf_k.add_paragraph()
    pk3.space_before = Pt(6)
    pk3.line_spacing = 1.30
    rk3 = pk3.add_run()
    rk3.text = k_sub
    rk3.font.name = FONT_CJK
    rk3.font.size = Pt(10.5)
    rk3.font.color.rgb = RGBColor(203, 213, 225)

notes_s1 = (
    "【講者備忘稿 Slide 01】各位決策夥伴大家好。今天這份簡報不僅深度拆解 HBR 最新力作《生成式 AI 正在顛覆市場研究》，"
    "更將我們前兩次研讀的《顧客需求不靠猜》與《AI 能強化你的數據分析能力》融會貫通，建立一套「道、法、術」三階企業科學決策藍圖。"
)
add_speaker_notes(s1, notes_s1)
slides_md_records.append(("Slide 01：【序幕：核心命題封面】", "生成式 AI 顛覆市場研究之機會邊界與「道・法・術」三篇合體決策藍圖", notes_s1))


# ==============================================================================
# SLIDE 02: 第一幕 — 全篇內容架構總覽 (原生大字版 PPTX 結構圖，取代縮小圖檔！)
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_bg(s2, C_BG_CANVAS)
add_zone1_header(
    s2, "Slide 02", "第一幕：全篇內容與脈絡總覽架構 (Ausubel 宏觀前導結構圖)",
    "生成式 AI 以四大核心能力滲透市調三階段，開啟四大變革機會並伴隨四大方法論挑戰"
)
add_parallel_cards(
    s2,
    [
        {
            "left": 0.40, "width": 3.95,
            "tag": "脈絡一：核心能力 × 三大階段",
            "title": "全天候智慧引擎重塑市調價值鏈",
            "rows": [
                ("● 【四大生成式 AI 核心能力】", "統整冗長逐字稿 (62%)、數據清理與編碼分析 (58%)、自然語言人機互動追問、自動撰寫報告與視覺化 (54%)。"),
                ("● 【三大市調流程階段滲透】", "① 設計研究與尋找機會（摘要文獻、發想假設） → ② 蒐集與分析數據（AI 訪談、合成問卷） → ③ 撰寫報告與發揮影響。"),
                ("● 【研究員角色升級】", "高達 90% 機構已用或規畫導入；逾 80% 認同省下資料整理苦工，將時間轉投高價值「策略說故事」。"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 4.68, "width": 3.95,
            "tag": "脈絡二：四大機會 × 三大錨定",
            "title": "由強化實務邁向顧客數位雙生",
            "rows": [
                ("● 【機會 1 & 2：強化與取代】", "Outset.ai 動態訪談員兼顧廣度與深度；安永以 Evidenza 生成 1,000 名合成 CEO，雙盲測試結論與真人 95% 一致。"),
                ("● 【機會 3 & 4：補缺口與數位雙生】", "30% 用於填補過往因預算放棄之決策（通用磨坊）；哥倫比亞 2,500 人與史丹福數位雙生兩週重測達 85% 信度。"),
                ("● 【接地氣三大錨定機制】", "純合成數據僅 31% 認同高價值！必須結合：少樣本提示 (Few-shot) ＋ 檢索增強 (RAG) ＋ 內部私有數據微調。"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 8.96, "width": 3.97,
            "tag": "★ 脈絡三：四大局限 × 四大解法",
            "title": "方法論交鋒與人機權變邊界",
            "rows": [
                ("● ★ 【四大技術風險與局限】", "① 人口偏誤（偏自由派高學歷）、② 跨期搖擺（Bisbee 3 個月飄移）、③ 感官失靈（高砂香料）、④ 盲測訂價混淆。"),
                ("● ★ 【四大前沿破局解法】", "① 綁定真人記憶數位雙生、② 右腦 AI 轉譯＋左腦統計、③ 少量真人＋大量 AI 校準 (PPI)、④ 大量歷史實驗微調。"),
                ("● ★ 【終局人機權變鐵律】", "四大解法各有理論死穴；早期發想靠 AI 百倍速探索，最終訂價、五感體驗與突破性創新強制回歸真人盲測！"),
            ],
            "is_spotlight": True, "spot_color": C_SPOT_BLUE, "spot_bg": C_SPOT_BG,
        },
    ],
    top=1.40, height=5.20, row_heights=[1.28, 1.34, 1.34]
)
add_zone3_footer(
    s2, "先掌握全篇「能力→階段→機會→局限→解法」五維宏觀架構，切勿在未設錨定與驗證防線下盲目導入合成數據。"
)
notes_s2 = (
    "【講者備忘稿 Slide 02】這頁原生大字架構圖為各位建立全篇論文的宏觀導覽（Ausubel 前導組織體）。"
    "整篇文章由左至右分為三大板塊：左欄是生成式 AI 的四大能力如何滲透市調三階段；中欄是由淺入深的四大變革機會與三大錨定機制；"
    "右欄則是本文最精華的方法論反思——四大技術局限與四大前沿解法。請注意三欄的每一列都採水平平行對齊，方便各位橫向對照。"
)
add_speaker_notes(s2, notes_s2)
slides_md_records.append(("Slide 02：【第一幕：全篇內容與脈絡總覽架構】原生大字結構圖", "生成式 AI 以四大核心能力滲透市調三階段，開啟四大變革機會並伴隨四大方法論挑戰", notes_s2))


# ==============================================================================
# SLIDE 03: 第一幕 — 四大機會與 AI 訪談員破除道德修飾 (平行對齊三支柱)
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_bg(s3, C_BG_CANVAS)
add_zone1_header(
    s3, "Slide 03", "第一幕：現狀診斷與機會深探 (S2 水平平行對齊三支柱型)",
    "AI 動態訪談員因不觸發人類心理與道德修飾機制，反而能比真人挖出更坦誠之深層痛點"
)
add_parallel_cards(
    s3,
    [
        {
            "left": 0.40, "width": 3.95,
            "tag": "支柱一：規模化合成受眾",
            "title": "取代現有問卷與填補預算缺口",
            "rows": [
                ("● 【雙盲實證 95% 高吻合度】", "安永 (EY) 與 Evidenza 合作測試 1,000 名合成 CEO，結論與真人調查高達 95% 相同，成本與時間呈指數級下降。"),
                ("● 【填補 30% 無數據決策缺口】", "通用磨坊與 Arena 運用 AI 引導過去因時間或預算不足、只能憑高層直覺拍板的跨門市選品與財務 ROI 估算。"),
                ("● 【百倍速早期概念快篩】", "在投入昂貴真人調查前，先以合成受訪者模擬市場反應，快速淘汰 80% 低潛力構想。"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 4.68, "width": 3.95,
            "tag": "支柱二：顧客數位雙生",
            "title": "綁定真人基準事實之模擬分身",
            "rows": [
                ("● 【跨期重測達 85% 穩定信度】", "史丹福與哥倫比亞大學（2,500 人群組）實證，綁定深度訪談之數位雙生與本人在兩週後重測相似度達 85%。"),
                ("● 【永不疲勞的 B2B 演練靶子】", "打破「第一印象只有一次機會」鐵律！B2B 業務可與大客戶數位雙生事前反覆演練推銷話術（82% 企業已實驗或計畫導入）。"),
                ("● 【動態綁定真實購物軌跡】", "CivicSync 結合心理認知測驗與線上購物行為，持續更新分身記憶，避免靜態角色過時。"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 8.96, "width": 3.97,
            "tag": "★ 聚光燈：AI 動態訪談員",
            "title": "解除人類「心理與道德修飾機制」",
            "rows": [
                ("● ★ 【思辨核心：道德修飾機制】", "人類面對「真人訪談員」時會自動啟動「心理與道德修飾機制（社會期許偏誤）」，為顧及面子或道德正確而隱藏真心話！"),
                ("● ★ 【機器無道德審判眼神】", "WeightWatchers 與 Outset.ai 實證發現，受訪者對 AI 訪談員反而更坦誠吐露私密痛點（呼應第一篇 ESG 口頭宣稱 100% 卻零購買力）。"),
                ("● ★ 【兼得量化廣度與質化深度】", "AI 能根據受訪者前次回答即時動態追問，且僅負責提問與統整逐字稿，幾乎完全不產生幻覺！"),
            ],
            "is_spotlight": True, "spot_color": C_SPOT_BLUE, "spot_bg": C_SPOT_BG,
        },
    ],
    top=1.40, height=5.20, row_heights=[1.30, 1.36, 1.30]
)
add_zone3_footer(
    s3, "將傳統「死板量化問卷」升級為「AI 動態追問訪談」，在羞於啟齒或高道德敏感議題上直接採集無偽裝之顧客真心話。"
)
notes_s3 = (
    "【講者備忘稿 Slide 03】為什麼 WeightWatchers 用 Outset.ai 進行訪談時，受訪者反而比面對真人更誠實？"
    "因為人類在面對另一個『人』時，會本能啟動『心理與道德修飾機制』（社會期許偏誤）；但面對沒有道德批判眼神的機器時，這層心理防禦就卸下了！"
)
add_speaker_notes(s3, notes_s3)
slides_md_records.append(("Slide 03：【第一幕：現狀診斷與機會深探】版型 S2", "AI 動態訪談員因不觸發人類心理與道德修飾機制，反而能比真人挖出更坦誠之深層痛點", notes_s3))


# ==============================================================================
# SLIDE 04: 第二幕 — 三類資料結構與大小模型取捨 (平行對齊三支柱)
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_bg(s4, C_BG_CANVAS)
add_zone1_header(
    s4, "Slide 04", "第二幕：資料結構與大小模型分工 (S2 水平平行對齊三支柱型)",
    "私有小型模型僅能學習表格統計機率，唯有公開大型模型具備解析質化語意之人類世界知識"
)
add_parallel_cards(
    s4,
    [
        {
            "left": 0.40, "width": 3.95,
            "tag": "結構一：結構化數據",
            "title": "數字型 (Numerical) ＋ 類別型 (Categorical)",
            "rows": [
                ("● 【資料定義與統計尺度】", "具嚴格固定二維表格欄位，含 ① 數字型（年齡 34 歲、年消費額 28,500 元）與 ② 類別型（性別、城市、五點滿意度標籤）。"),
                ("● 【模型運作機制】", "僅需計算欄位間之條件聯合機率分布 P(X₁, X₂, ..., Xₚ)，不涉及自然語言隱喻或心理推論。"),
                ("● 【最佳適配模型】", "企業私有小型模型（如 Rockfish Data）即可精準建模生成合成表格，保障機密 100% 不外洩。"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 4.68, "width": 3.95,
            "tag": "結構二：半結構化數據",
            "title": "自帶標籤之巢狀日誌 (JSON / XML)",
            "rows": [
                ("● 【資料定義與統計尺度】", "每位顧客行為序列長短不一、無法塞入死板二維表格，但內部自帶明確結構標籤（Tags / Key-Value）。"),
                ("● 【典型市場研究實例】", "網站與 App 點擊流瀏覽軌跡（Clickstream）、帶固定標頭之電子郵件與客服工單系統日誌。"),
                ("● 【最佳適配模型】", "小型私有模型同樣能有效捕捉事件序列轉移機率（如美國陸軍與國土安全部採用之模擬系統）。"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 8.96, "width": 3.97,
            "tag": "★ 聚光燈：非結構化質化數據",
            "title": "自然語言脈絡 × 大模型世界知識先驗",
            "rows": [
                ("● ★ 【資料定義與深層動機】", "深度訪談逐字稿、焦點團體錄影、社群抱怨長文，完全無預先定義格式，專門回答 Why 與 How 的情緒與動機。"),
                ("● ★ 【為何私有小模型無能為力？】", "小型私有模型只看過內部表格，從未讀過全人類書籍與對話，缺乏「世界知識先驗（World Knowledge Prior）」，不懂言外之意！"),
                ("● ★ 【黃金折衷處方】", "以「企業內部獨有數據微調（Fine-tune）公開大型模型」＋ RAG 知識庫，兼顧商業機密與質化深度。"),
            ],
            "is_spotlight": True, "spot_color": C_SPOT_TEAL, "spot_bg": C_SPOT_TEALBG,
        },
    ],
    top=1.40, height=5.20, row_heights=[1.32, 1.32, 1.32]
)
add_zone3_footer(
    s4, "依資料結構選配模型：純表格與點擊流交給「私有小模型」保機密；深度質化訪談則必須採用「內部數據微調之公開大模型」。"
)
notes_s4 = (
    "【講者備忘稿 Slide 04】這頁三支柱卡片清楚拆解了文中第 10 頁的三類資料結構。"
    "三欄的三個列點（資料定義、運作機制/實例、適配模型）完全水平平行對齊，讓決策者一眼看懂為何質化數據非用公開大模型不可。"
)
add_speaker_notes(s4, notes_s4)
slides_md_records.append(("Slide 04：【第二幕：資料結構與大小模型分工】版型 S2", "私有小型模型僅能學習表格統計機率，唯有公開大型模型具備解析質化語意之人類世界知識", notes_s4))


# ==============================================================================
# SLIDE 05: 第二幕 — 盲測訂價失靈之因果公式拆解 (S6 核心公式與平行三卡片)
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_bg(s5, C_BG_CANVAS)
add_zone1_header(
    s5, "Slide 05", "第二幕：盲測訂價失靈之因果公式拆解 (S6 核心公式與直覺拆解型)",
    "生成式 AI 在盲測訂價中會自動腦補競品與歷史價同步變貴，導致需求曲線平坦失真"
)

eq_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.40), Inches(1.36), Inches(12.53), Inches(1.75))
eq_box.adjustments[0] = 0.04
eq_box.fill.solid()
eq_box.fill.fore_color.rgb = C_SPOT_GOLDBG
eq_box.line.color.rgb = C_SPOT_GOLD
eq_box.line.width = Pt(2.2)

tf_eq = eq_box.text_frame
tf_eq.word_wrap = True
tf_eq.margin_left = tf_eq.margin_right = Inches(0.25)
tf_eq.margin_top = Inches(0.12)

pe1 = tf_eq.paragraphs[0]
pe1.alignment = PP_ALIGN.CENTER
re1 = pe1.add_run()
re1.text = "【真人隨機盲測：獨立因果干預】 P(Y | do(X = x)) = ∑z P(Y | X = x, Z = z) · P(Z = z)"
re1.font.name = FONT_CJK
re1.font.size = Pt(15)
re1.font.bold = True
re1.font.color.rgb = C_NAVY_DARK

pe2 = tf_eq.add_paragraph()
pe2.alignment = PP_ALIGN.CENTER
pe2.space_before = Pt(5)
re2 = pe2.add_run()
re2.text = "≠   【生成式 AI 盲測：語境條件聯想混淆】 P_LLM(Y | X = x) = ∑z P(Y | X = x, Z = z) · P_LLM(Z = z | X = x)"
re2.font.name = FONT_CJK
re2.font.size = Pt(15)
re2.font.bold = True
re2.font.color.rgb = C_SPOT_RED

pe3 = tf_eq.add_paragraph()
pe3.alignment = PP_ALIGN.CENTER
pe3.space_before = Pt(5)
re3 = pe3.add_run()
re3.text = "▲ 關鍵差異項：真人盲測中 P(Z | X) = P(Z) 恆定不變；但 AI 的 P_LLM(Z = z | X = x) 會隨測試價格 X 升高而同步調高背景價格 Z！"
re3.font.name = FONT_CJK
re3.font.size = Pt(11.5)
re3.font.bold = True
re3.font.color.rgb = C_SPOT_GOLD

add_parallel_cards(
    s5,
    [
        {
            "left": 0.40, "width": 3.95,
            "tag": "公式項拆解 (1)：X 與 Y",
            "title": "測試價格 (X) → 購買意願 (Y)",
            "rows": [
                ("● 【盲測實驗設計目的】", "將受試者隨機分組（A 組看 1,000 元、B 組看 5,000 元），測量單純調高價格 X 對購買率 Y 的獨立因果斜率。"),
                ("● 【真實人類反應】", "看到 5,000 元時，依據日常物價基準果斷拒買，需求曲線正常向右下傾斜。"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 4.68, "width": 3.95,
            "tag": "公式項拆解 (2)：混淆變數 Z",
            "title": "歷史價格與店內競品價格 (Z)",
            "rows": [
                ("● 【隱藏的背景物價錨點 Z】", "顧客心中的參考價格錨點（過往買過的歷史價格、貨架旁競爭對手的售價 1,200 元）。"),
                ("● 【隨機分派獨立性 P(Z|X)=P(Z)】", "在真人實驗中，研究員改動標價 X，不會改變受試者腦中對競品價格 Z 的既有記憶。"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 8.96, "width": 3.97,
            "tag": "★ 聚光燈拆解 (3)：P_LLM(Z | X)",
            "title": "AI 自動腦補語境共現 (Confounding)",
            "rows": [
                ("● ★ 【語境條件聯想本能】", "LLM 本質是根據上下文猜測合理語境，無法將測試價格 X 視為獨立的「隨機抽樣」。"),
                ("● ★ 【致命腦補效應】", "看到 X=5,000 元時自動調高 P_LLM(Z|X)，腦補「店內競品與歷史價 Z 也全是 5,000 元」，誤判高價合理而照買不誤！"),
            ],
            "is_spotlight": True, "spot_color": C_SPOT_RED, "spot_bg": C_SPOT_REDBG,
        },
    ],
    top=3.26, height=3.38, row_heights=[1.08, 1.08]
)
add_zone3_footer(
    s5, "絕對禁止直接拿未經統計校準的生成式 AI 進行「單一變數盲測訂價實驗」，否則將嚴重低估顧客對漲價的抗拒度！"
)
notes_s5 = (
    "【講者備忘稿 Slide 05】這頁公式三明治揭開了盲測訂價失靈的數學本質：真人盲測是獨立因果干預 do(X)，而 LLM 是語境條件機率 P(Z|X)。"
)
add_speaker_notes(s5, notes_s5)
slides_md_records.append(("Slide 05：【第二幕：盲測訂價失靈之因果公式拆解】版型 S6", "生成式 AI 在盲測訂價中會自動腦補競品與歷史價同步變貴，導致需求曲線平坦失真", notes_s5))


# ==============================================================================
# SLIDE 06: 第二幕 — 純改提示詞「挖東牆補西牆」 vs. 四大前沿解法死穴批判
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_bg(s6, C_BG_CANVAS)
add_zone1_header(
    s6, "Slide 06", "第二幕：方法論深度思辨與第一性原理批判 (S1 雙欄平行對照型)",
    "純改提示詞必淪為挖東牆補西牆，四大前沿修補解法亦各自存在無法根除之理論死穴"
)

# Left Column: Prompt Engineering Dilemma (Formatted with clean 1.35x spacing & separate row boxes)
add_parallel_cards(
    s6,
    [
        {
            "left": 0.40, "width": 4.75,
            "tag": "舊思維盲點：純改提示詞 (Prompt)",
            "title": "為何寫更細的規範是「挖東牆補西牆」？",
            "rows": [
                (
                    "● 【東牆：未知腦補變數永遠鎖不完】",
                    "就算在提示詞死鎖「歷史價與競品價皆為 1,200 元」，具備數千億參數的 AI 看到 5,000 元仍會自動繞道腦補「現在大缺貨、巨星聯名或限量溢價」，人類無法事前窮舉所有潛在混淆變數 Z！"
                ),
                (
                    "● 【西牆：寫太白引發需求特徵劇透】",
                    "若刻意強調「別家都賣 1,200、唯獨這家賣 5,000」，等於向 AI 劇透實驗目的並觸發焦點錯覺，使 AI 變成呆板比大小的計算機（100% 拒買），照樣測不出真實人類的價格彈性曲線。"
                ),
            ],
            "is_spotlight": False,
        }
    ],
    top=1.40, height=5.20, row_heights=[1.98, 1.98]
)

# Right Column: Spotlight Table of 4 Frontier Solutions & User's Critique
right_panel = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.32), Inches(1.40), Inches(7.61), Inches(5.20))
right_panel.adjustments[0] = 0.02
right_panel.fill.solid()
right_panel.fill.fore_color.rgb = C_WHITE
right_panel.line.color.rgb = C_SPOT_BLUE
right_panel.line.width = Pt(2.2)

tb_rp = s6.shapes.add_textbox(Inches(5.50), Inches(1.50), Inches(7.25), Inches(0.42))
tf_rp = tb_rp.text_frame
p_rp = tf_rp.paragraphs[0]
r_rp = p_rp.add_run()
r_rp.text = "★ 聚光燈焦點：四大前沿破局解法 vs. 第一性原理「四大理論死穴」批判"
r_rp.font.name = FONT_CJK
r_rp.font.size = Pt(13.5)
r_rp.font.bold = True
r_rp.font.color.rgb = C_SPOT_BLUE

rows, cols = 5, 3
tbl_shape = s6.shapes.add_table(rows, cols, Inches(5.48), Inches(1.98), Inches(7.30), Inches(4.45))
tbl = tbl_shape.table
tbl.columns[0].width = Inches(1.78)
tbl.columns[1].width = Inches(2.42)
tbl.columns[2].width = Inches(3.10)

headers_s6 = ["前沿破局解法", "核心運作機制", "★ 第一性原理「理論死穴」批判"]
table_data_s6 = [
    ["1. 綁定真人數位雙生\n(Grounded Twins)", "以真人數小時訪談、認知測驗與購物軌跡錨定分身", "【具身感質不可壓縮】：無法把一整個人塞進模型！文字無法編碼生理嗅覺與潛意識（高砂香料失敗）"],
    ["2. 右腦 AI＋左腦統計\n(Hybrid Model)", "大模型僅將圖文轉為特徵分數，交左腦統計公式算彈性", "【計量模型誤設偏誤】：幻覺最少，但面對多變數非線性複雜感性交互作用時，極難寫出高解釋力函式"],
    ["3. 少量真人＋AI 校準\n(PPI Calibration)", "以 100 名真人盲測為基準，用統計公式扣除 AI 系統偏誤", "【跨時間分布偏移】：當下對準人類可能只是「湊巧發生」，換字眼或跨 3 個月（Bisbee 2024）即失準"],
    ["4. 大量歷史數據微調\n(Fine-Tuning)", "以過往累積之大量真實調查與歷史實驗微調模型權重", "【後照鏡外推失靈】：過去數據屬分布內插值，面對未來「消費者行為劇變」或「突破性創新」即失靈"],
]

for c_idx, h_text in enumerate(headers_s6):
    cell = tbl.cell(0, c_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = C_NAVY_DARK if c_idx < 2 else C_SPOT_RED
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = cell.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = h_text
    r.font.name = FONT_CJK
    r.font.size = Pt(10.5)
    r.font.bold = True
    r.font.color.rgb = C_WHITE

for r_idx, row_vals in enumerate(table_data_s6):
    for c_idx, val in enumerate(row_vals):
        cell = tbl.cell(r_idx + 1, c_idx)
        cell.fill.solid()
        if c_idx == 2:
            cell.fill.fore_color.rgb = C_SPOT_REDBG
        else:
            cell.fill.fore_color.rgb = C_WHITE if r_idx % 2 == 0 else C_BG_CANVAS
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.line_spacing = 1.25
        r = p.add_run()
        r.text = val
        r.font.name = FONT_CJK
        r.font.size = Pt(10)
        r.font.bold = (c_idx == 0 or c_idx == 2)
        r.font.color.rgb = C_SPOT_RED if c_idx == 2 else C_SLATE_TXT

add_zone3_footer(
    s6, "徹底放棄尋找「單一萬能 AI 市調模型」的幻想；承認四大解法各有死穴，改採「依商業情境動態配置工具組合」。"
)
notes_s6 = (
    "【講者備忘稿 Slide 06】左欄將『東牆』與『西牆』拆分為獨立高行距區塊，清楚展示為何純改提示詞會陷入死胡同；"
    "右欄表格則完整呈現我們對四大前沿解法的第一性原理批判。"
)
add_speaker_notes(s6, notes_s6)
slides_md_records.append(("Slide 06：【第二幕：方法論深度思辨與第一性原理批判】版型 S1", "純改提示詞必淪為挖東牆補西牆，四大前沿修補解法亦各自存在無法根除之理論死穴", notes_s6))


# ==============================================================================
# SLIDE 07: 第三幕 — George Box 情境權變投資組合 (原生大字結構圖，取代縮小圖檔！)
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_bg(s7, C_BG_CANVAS)
add_zone1_header(
    s7, "Slide 07", "第三幕：George Box 情境權變配置矩陣 (原生大字決策結構圖)",
    "所有模型皆有盲區，企業須依「容錯率、感官涉入度、創新劇變度」分階段配置人機組合"
)
add_parallel_cards(
    s7,
    [
        {
            "left": 0.40, "width": 3.95,
            "tag": "戰場一：早期百倍速發想與演練",
            "title": "高容錯率 × 理性認知 × 常規品類",
            "rows": [
                ("● 【核心決策目標】", "在投入高昂研發與真人市調前，以極低成本從 100 個早期產品概念中淘汰 80% 弱點子，或訓練 B2B 業務話術。"),
                ("● 【最佳工具組合（解法一＋四）】", "結合「綁定真人記憶之數位雙生」＋「企業歷史數據微調大模型」＋ RAG 知識庫錨定，百倍速模擬市場反應。"),
                ("● 【風險護欄與案例】", "安永 1,000 名合成 CEO（95% 一致）、哥倫比亞 2,500 人數位雙生；嚴禁在此階段直接拍板最終售價！"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 4.68, "width": 3.95,
            "tag": "戰場二：常規品牌診斷與驅動排序",
            "title": "中容錯率 × 挖掘痛點 × 量化權重",
            "rows": [
                ("● 【核心決策目標】", "找出顧客不願對真人明說的深層痛點，並精準計算各項品質／服務因素對真實營收的「提升潛力（Lift）」。"),
                ("● 【最佳工具組合（AI 訪談＋解法二）】", "先派「AI 動態訪談員（Outset.ai）」卸下受訪者道德修飾，再以「右腦 AI 轉譯特徵＋左腦道斯線性統計模型」算權重。"),
                ("● 【風險護欄與案例】", "WeightWatchers 坦誠訪談 ＋ ITI / S-SET 線性迴歸鎖定 1~2 個關鍵因素 X*，幻覺機率最小且具高度可解釋性。"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 8.96, "width": 3.97,
            "tag": "★ 戰場三：終局定價與五感／突破創新",
            "title": "零容錯率 × 生理感官 × 行為劇變",
            "rows": [
                ("● ★ 【三大 AI 絕對禁區】", "① 最終盲測訂價（防語境混淆）、② 香水／食品五感體驗（防感質失靈）、③ 突破性創新與環境劇變（防後照鏡外推失靈）。"),
                ("● ★ 【強制回歸真人盲測＋解法三】", "上市前最後一哩路強制執行「真人隨機對照實驗（A/B Test）」，或以每波次抽取真人小樣本進行 PPI 動態統計校準。"),
                ("● ★ 【風險護欄與案例】", "高砂香料（Takasago）香氣測試與 800 億美元銀行真人分支機構對照實驗，守住真實財務毛利底線！"),
            ],
            "is_spotlight": True, "spot_color": C_SPOT_GOLD, "spot_bg": C_SPOT_GOLDBG,
        },
    ],
    top=1.40, height=5.20, row_heights=[1.30, 1.36, 1.30]
)
add_zone3_footer(
    s7, "統計大師 George Box：「所有模型都是錯的，但有些很有用。」將市調預算按「80% AI 早期快篩 ＋ 20% 真人終局盲測」重新配置！"
)
notes_s7 = (
    "【講者備忘稿 Slide 07】我們將原本縮小的圖譜改造成這頁原生大字版『George Box 情境權變配置矩陣』。"
    "三欄分別對應早期百倍速發想、常規品牌診斷、以及終局定價與感官創新三大戰場，每一列（目標、工具組合、護欄案例）完全水平對齊。"
)
add_speaker_notes(s7, notes_s7)
slides_md_records.append(("Slide 07：【第三幕：George Box 情境權變配置矩陣】原生大字結構圖", "所有模型皆有盲區，企業須依「容錯率、感官涉入度、創新劇變度」分階段配置人機組合", notes_s7))


# ==============================================================================
# SLIDE 08: 第三幕 — 正反實證與人機邊界 2x2 矩陣 (S5 2x2 策略象限矩陣型)
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_bg(s8, C_BG_CANVAS)
add_zone1_header(
    s8, "Slide 08", "第三幕：正反實證與人機邊界矩陣 (S5 2×2 策略象限矩陣型)",
    "高感官涉入與突破性創新構成生成式 AI 禁區，最終定價與五感測試必須回歸真人盲測"
)

axis_y = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.35), Inches(1.42), Inches(0.55), Inches(5.15))
axis_y.fill.solid()
axis_y.fill.fore_color.rgb = C_NAVY_DARK
axis_y.line.fill.background()
tf_ay = axis_y.text_frame
tf_ay.vertical_anchor = MSO_ANCHOR.MIDDLE
p_ay = tf_ay.paragraphs[0]
p_ay.alignment = PP_ALIGN.CENTER
r_ay = p_ay.add_run()
r_ay.text = "縱\n軸\n：\n感\n官\n與\n因\n果\n敏\n感\n度"
r_ay.font.name = FONT_CJK
r_ay.font.size = Pt(11)
r_ay.font.bold = True
r_ay.font.color.rgb = C_SKY_LIGHT

# Top Row of 2x2 Matrix (Parallel aligned)
add_parallel_cards(
    s8,
    [
        {
            "left": 1.05, "width": 5.82,
            "tag": "象限 II：高生理五感 × 既有品類改版",
            "title": "【AI 禁區一】多感官與潛意識失靈（高砂香料案例）",
            "rows": [
                ("● 【實證敗北與處方】", "高砂香料（Takasago）嘗試以合成受訪者評估新款香水，但 AI 完全沒鼻子，無法連結氣味分子與童年潛意識記憶；香水與食品必須強制採用「真人實體感官盲測」。"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 7.05, "width": 5.88,
            "tag": "★ 象限 I（聚光燈核心禁區）：突破性創新 × 盲測訂價",
            "title": "【AI 禁區二 & 三】歷史外推失靈 ＋ 價格混淆現象",
            "rows": [
                ("● ★ 【雙重失靈風險與終局鐵律】", "面對「消費者行為劇變／突破性新產品」時歷史微調外推失效；進行「盲測訂價」時 AI 自動腦補競品同價。上市前最終定價與突破性創新，必須執行「真人隨機對照實驗（A/B Test）」！"),
            ],
            "is_spotlight": True, "spot_color": C_SPOT_RED, "spot_bg": C_SPOT_REDBG,
        },
    ],
    top=1.42, height=2.48, row_heights=[1.22]
)

# Bottom Row of 2x2 Matrix (Parallel aligned)
add_parallel_cards(
    s8,
    [
        {
            "left": 1.05, "width": 5.82,
            "tag": "象限 III（AI 主力戰場）：理性認知 × 常規品類診斷",
            "title": "【AI 最佳適配】AI 動態訪談員 ＋ 右腦轉譯／左腦統計",
            "rows": [
                ("● 【實證成功與處方】", "WeightWatchers 透過 Outset.ai 消除受訪者道德修飾；安永 1,000 名合成 CEO 雙盲測試達 95% 一致率。以 AI 訪談員收集無偽裝痛點，交由左腦統計模型計算提升潛力（Lift）。"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 7.05, "width": 5.88,
            "tag": "象限 IV（AI 加速戰場）：早期百倍速探索 × 話術演練",
            "title": "【AI 最佳適配】顧客數位雙生 ＋ 內部數據微調大模型",
            "rows": [
                ("● 【實證成功與處方】", "哥倫比亞 2,500 人數位雙生群組、史丹福 85% 重測信度、通用磨坊填補無外部數據決策缺口。用綁定真人記憶之數位雙生進行 B2B 業務話術演練與百倍速早期產品概念篩選。"),
            ],
            "is_spotlight": False,
        },
    ],
    top=4.08, height=2.48, row_heights=[1.22]
)

add_zone3_footer(
    s8, "用 2×2 矩陣把關市調專案：下方兩個象限放手讓生成式 AI 百倍速衝刺，上方兩個象限嚴格保留真人實驗預算！"
)
notes_s8 = (
    "【講者備忘稿 Slide 08】這張 2×2 策略象限矩陣讓前線團隊一秒判斷何時放手用 AI（下方兩象限）、何時強制回歸真人盲測（上方兩象限）。"
)
add_speaker_notes(s8, notes_s8)
slides_md_records.append(("Slide 08：【第三幕：正反實證與人機邊界矩陣】版型 S5", "高感官涉入與突破性創新構成生成式 AI 禁區，最終定價與五感測試必須回歸真人盲測", notes_s8))


# ==============================================================================
# SLIDE 09: 第四幕 — 三篇 HBR 合體「道・法・術」終極決策閉環 (原生大字平行矩陣)
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_bg(s9, C_BG_CANVAS)
add_zone1_header(
    s9, "Slide 09", "第四幕：三篇 HBR 合體終極藍圖 (S3 水平平行對齊流程型)",
    "串聯「統計定錨問題（道）→ 嵌入 ERP 情境（法）→ 生成式市調與真人終審（術）」閉環"
)
add_parallel_cards(
    s9,
    [
        {
            "left": 0.40, "width": 3.95,
            "tag": "第一階【道：界定問題與方向】",
            "title": "《顧客需求不靠猜！統計模型找正解》",
            "rows": [
                ("● 【破除高層直覺偏誤】", "72% 上市 B2B 高層認知與顧客真實重視呈零或負相關，85.5% 每兩年大改優先順序（受顯眼客訴與盲從對手誤導）。"),
                ("● 【道斯線性模型鎖定 X*】", "量化各因素對真實財報毛利 Y 之「提升潛力（Lift）」，嚴格鎖定 1~2 個關鍵因素 X*（ITI 股價漲 162%、S-SET 銷售增 52%）。"),
                ("● 【跨篇交棒任務（道 → 法）】", "砍除零價值口號（如表面重視卻零購買力的 ESG），為後續 AI 分析與市調指明唯一高價值靶心 X*！"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 4.68, "width": 3.95,
            "tag": "第二階【法：能力與情境底座】",
            "title": "《AI 能強化你的數據分析能力》",
            "rows": [
                ("● 【打破數據孤島與虛假相關】", "將分析工具直接內嵌於 ERP 與 CRM 日常交易系統，由人類專家預先設定「背景情境（Contextual Information）」因果護欄。"),
                ("● 【擴增分析與 L1 正則化過濾】", "以 ML + NLP 口說提問 + NLG 自動摘要賦能第一線平民分析師（挽回數十萬美元折扣），並用 Adjusted R² 與 Lasso 砍除雜訊。"),
                ("● 【跨篇交棒任務（法 → 術）】", "提供乾淨、結構化與半結構化的企業內部歷史交易底座，作為生成式 AI 微調與 RAG 檢索的基準事實錨點！"),
            ],
            "is_spotlight": False,
        },
        {
            "left": 8.96, "width": 3.97,
            "tag": "★ 第三階【術：前線市調與權變】",
            "title": "《生成式 AI 正在顛覆市場研究》",
            "rows": [
                ("● ★ 【突破廣度與深度兩難】", "針對第一階鎖定的 X*，派出 AI 動態訪談員（Outset.ai）解除受訪者道德修飾，並以第二階 ERP 數據微調顧客數位雙生。"),
                ("● ★ 【百倍速快篩 ＋ 統計模型分工】", "用數位雙生進行百倍速早期概念快篩與業務演練；用「右腦大模型轉譯＋左腦道斯模型」計算精準權重。"),
                ("● ★ 【四道關卡真人盲測終審】", "嚴守價格混淆、多感官與突破性創新三大禁區，上市前強制執行「真人隨機對照實驗（A/B Test）」完成科學閉環！"),
            ],
            "is_spotlight": True, "spot_color": C_SPOT_TEAL, "spot_bg": C_SPOT_TEALBG,
        },
    ],
    top=1.40, height=5.20, row_heights=[1.30, 1.34, 1.32]
)
add_zone3_footer(
    s9, "三篇合體黃金閉環：① 開放探索 → ② 道斯迴歸抓高 Lift 因素 X* → ③ 嵌入 ERP/CRM 與數位雙生快篩 → ④ 真人 A/B Test 終審！"
)
notes_s9 = (
    "【講者備忘稿 Slide 09】這頁是我們三次深度閱讀的最高潮：將三篇 HBR 經典文獻按照『道、法、術』串聯成平行對齊的三階科學決策閉環。"
)
add_speaker_notes(s9, notes_s9)
slides_md_records.append(("Slide 09：【第四幕：三篇 HBR 合體終極藍圖】版型 S3", "串聯「統計定錨問題（道）→ 嵌入 ERP 情境（法）→ 生成式市調與真人終審（術）」閉環", notes_s9))


# ==============================================================================
# SLIDE 10: 終幕 — 最後結束頁面：三大黃金決策鐵律與立即行動檢核 (Fixes User Point 10!)
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_bg(s10, C_NAVY_DARK)

# Top decorative cyan strip
end_top = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.14))
end_top.fill.solid()
end_top.fill.fore_color.rgb = C_SKY_LIGHT
end_top.line.fill.background()

# End Badge Pill
end_tag = "Slide 10  |  終幕：決策收束與立即行動檢核 (Executive Closing & Next Steps)"
end_pill_w = calc_pill_width(end_tag, font_pt=10.5, pad_in=0.50)
end_pill = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.60), Inches(0.42), Inches(end_pill_w), Inches(0.36))
end_pill.adjustments[0] = 0.5
end_pill.fill.solid()
end_pill.fill.fore_color.rgb = C_NAVY_MED
end_pill.line.color.rgb = C_SKY_LIGHT
end_pill.line.width = Pt(1.2)
tf_ep = end_pill.text_frame
tf_ep.word_wrap = False
tf_ep.vertical_anchor = MSO_ANCHOR.MIDDLE
tf_ep.margin_left = Inches(0.18)
p_ep = tf_ep.paragraphs[0]
p_ep.alignment = PP_ALIGN.LEFT
r_ep = p_ep.add_run()
r_ep.text = end_tag
r_ep.font.name = FONT_CJK
r_ep.font.size = Pt(10.5)
r_ep.font.bold = True
r_ep.font.color.rgb = C_SKY_LIGHT

# Closing Headline
tb_end_t = s10.shapes.add_textbox(Inches(0.60), Inches(0.90), Inches(12.1), Inches(0.95))
tf_et = tb_end_t.text_frame
tf_et.word_wrap = True
p_et = tf_et.paragraphs[0]
r_et = p_et.add_run()
r_et.text = "以科學因果為舵、以生成式 AI 為帆：企業導入 AI 市場研究之三步落地行動守則"
r_et.font.name = FONT_CJK
r_et.font.size = Pt(23)
r_et.font.bold = True
r_et.font.color.rgb = C_WHITE

# 3 Parallel Closing Action Pillars on Dark Background
closing_steps = [
    (
        "Step 01 ｜ 檢核問題靶心（道）",
        "啟動 AI 前先算提升潛力 (Lift)",
        [
            ("● 【拒絕直覺拍板】", "不依賴顯眼少數客訴、不盲從競爭對手，先將客戶調查綁定真實財報毛利 Y。"),
            ("● 【鎖定 1~2 個 X*】", "用道斯線性統計模型找出最高 Lift 的核心因素 X*，果斷砍除零價值表面計畫。"),
        ],
        C_SKY_LIGHT, RGBColor(23, 37, 84)
    ),
    (
        "Step 02 ｜ 配置資料與模型（法）",
        "依資料結構分工大小模型與 ERP",
        [
            ("● 【結構化／半結構化】", "表格（數字／類別）與點擊流日誌交由「企業私有小模型」建模，確保機密零外洩。"),
            ("● 【非結構化質化訪談】", "採用「內部 ERP/CRM 數據微調公開大模型」＋ RAG 知識庫，兼顧世界知識與隱私。"),
        ],
        RGBColor(251, 191, 36), RGBColor(30, 41, 59)
    ),
    (
        "Step 03 ｜ 執行人機權變閉環（術）",
        "AI 百倍速廣度探索 ＋ 真人盲測終審",
        [
            ("● 【AI 訪談員＋數位雙生】", "用 Outset.ai 解除受訪者道德修飾，用綁定真人記憶之數位雙生百倍速快篩早期概念。"),
            ("● 【三大禁區真人終審】", "最終盲測訂價、五感體驗與突破性創新，強制回歸「真人隨機 A/B Test」拍板！"),
        ],
        RGBColor(52, 211, 153), RGBColor(6, 78, 59)
    ),
]

for idx, (st_tag, st_title, st_rows, border_col, fill_col) in enumerate(closing_steps):
    cx = 0.60 + idx * 4.12
    cw = 3.88
    ctop = 1.85
    ch = 3.85

    scard = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(cx), Inches(ctop), Inches(cw), Inches(ch))
    scard.adjustments[0] = 0.04
    scard.fill.solid()
    scard.fill.fore_color.rgb = fill_col
    scard.line.color.rgb = border_col
    scard.line.width = Pt(2.0)

    # Step Tag
    tb_st = s10.shapes.add_textbox(Inches(cx + 0.20), Inches(ctop + 0.18), Inches(cw - 0.40), Inches(0.35))
    p_st = tb_st.text_frame.paragraphs[0]
    r_st = p_st.add_run()
    r_st.text = st_tag
    r_st.font.name = FONT_CJK
    r_st.font.size = Pt(11)
    r_st.font.bold = True
    r_st.font.color.rgb = border_col

    # Step Title
    tb_stt = s10.shapes.add_textbox(Inches(cx + 0.20), Inches(ctop + 0.52), Inches(cw - 0.40), Inches(0.45))
    p_stt = tb_stt.text_frame.paragraphs[0]
    r_stt = p_stt.add_run()
    r_stt.text = st_title
    r_stt.font.name = FONT_CJK
    r_stt.font.size = Pt(14.5)
    r_stt.font.bold = True
    r_stt.font.color.rgb = C_WHITE

    # Divider
    sdiv = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx + 0.20), Inches(ctop + 1.02), Inches(cw - 0.40), Inches(0.015))
    sdiv.fill.solid()
    sdiv.fill.fore_color.rgb = border_col
    sdiv.line.fill.background()

    # Parallel Rows inside Closing Card
    for r_i, (rh_txt, rb_txt) in enumerate(st_rows):
        ry = ctop + 1.15 + r_i * 1.30
        if r_i > 0:
            rdiv = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx + 0.20), Inches(ry - 0.08), Inches(cw - 0.40), Inches(0.01))
            rdiv.fill.solid()
            rdiv.fill.fore_color.rgb = RGBColor(71, 85, 105)
            rdiv.line.fill.background()

        tb_sr = s10.shapes.add_textbox(Inches(cx + 0.20), Inches(ry), Inches(cw - 0.40), Inches(1.20))
        tf_sr = tb_sr.text_frame
        tf_sr.word_wrap = True
        tf_sr.margin_left = tf_sr.margin_right = tf_sr.margin_top = tf_sr.margin_bottom = 0

        p1 = tf_sr.paragraphs[0]
        p1.line_spacing = 1.30
        p1.space_after = Pt(3)
        r1 = p1.add_run()
        r1.text = rh_txt
        r1.font.name = FONT_CJK
        r1.font.size = Pt(12)
        r1.font.bold = True
        r1.font.color.rgb = border_col

        p2 = tf_sr.add_paragraph()
        p2.line_spacing = 1.35
        r2 = p2.add_run()
        r2.text = rb_txt
        r2.font.name = FONT_CJK
        r2.font.size = Pt(11.2)
        r2.font.color.rgb = RGBColor(226, 232, 240)

# Bottom Grand Closing & Thank You Banner
close_box = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.60), Inches(5.95), Inches(12.13), Inches(1.10))
close_box.adjustments[0] = 0.06
close_box.fill.solid()
close_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
close_box.line.color.rgb = C_SKY_LIGHT
close_box.line.width = Pt(1.8)
tf_cb = close_box.text_frame
tf_cb.word_wrap = True
tf_cb.vertical_anchor = MSO_ANCHOR.MIDDLE
tf_cb.margin_left = tf_cb.margin_right = Inches(0.30)

p_cb1 = tf_cb.paragraphs[0]
p_cb1.alignment = PP_ALIGN.CENTER
r_cb1 = p_cb1.add_run()
r_cb1.text = "★ 終章核心金句：「讓 AI 訪談員聽見無道德偽裝的真心話，讓數位雙生百倍速跑完早期試錯，把最終因果裁決權留給真人實驗。」"
r_cb1.font.name = FONT_CJK
r_cb1.font.size = Pt(13.5)
r_cb1.font.bold = True
r_cb1.font.color.rgb = C_WHITE

p_cb2 = tf_cb.add_paragraph()
p_cb2.alignment = PP_ALIGN.CENTER
p_cb2.space_before = Pt(6)
r_cb2 = p_cb2.add_run()
r_cb2.text = "THANK YOU  ｜  Q&A 策略研討與落地交流  ｜  HBR 三篇合體深度閱讀專案圓滿完成"
r_cb2.font.name = FONT_CJK
r_cb2.font.size = Pt(11.5)
r_cb2.font.bold = True
r_cb2.font.color.rgb = C_SKY_LIGHT

notes_s10 = (
    "【講者備忘稿 Slide 10（最後結束頁）】在簡報的最後一頁，我們依據峰終定律（Peak-End Rule）將全篇濃縮為立刻可執行的三步落地守則："
    "第一步以道斯模型鎖定高 Lift 靶心 X*（道）；第二步依資料結構分工私有小模型與微調大模型（法）；"
    "第三步以 AI 訪談員與數位雙生百倍速探索，並在最終定價與五感創新關頭強制執行真人隨機盲測（術）。感謝各位的聆聽，現在開放 Q&A 策略交流！"
)
add_speaker_notes(s10, notes_s10)
slides_md_records.append(("Slide 10：【終幕：全篇三大黃金決策鐵律與結束頁】Peak-End Closing", "以科學因果為舵、以生成式 AI 為帆：企業導入 AI 市場研究之三步落地行動守則", notes_s10))


prs.save(PPTX_PATH)
print(f"[OK] Saved PPTX to: {PPTX_PATH} ({os.path.getsize(PPTX_PATH)} bytes)")

# Save Dual-Channel Markdown Script
with open(MD_SCRIPT_PATH, "w", encoding="utf-8") as f:
    f.write("# 《生成式 AI 正在顛覆市場研究》深度思辨與「道・法・術」三篇合體簡報腳本 (Assertion-Evidence Deck)\n\n")
    f.write("- **簡報實體檔案**：`生成式AI顛覆市場研究_深度思辨與三篇合體簡報.pptx` (10 頁 16:9 寬螢幕原生視覺圖表簡報)\n")
    f.write("- **設計規範**：嚴格遵循 Alley & Neeley (2005) 三區斷言證據架構、動態標籤寬度防溢位、零縮小圖片嵌入（全原生大字結構圖）、Müller-Brockmann 水平平行對齊列點（1.35x 行距）與 Kahneman 峰終定律結束頁。\n\n---\n\n")
    for title, headline, notes in slides_md_records:
        f.write(f"## {title}\n")
        f.write(f"- **Zone 1 斷言標題**：**{headline}**\n")
        f.write(f"- **講者逐字備忘稿 (Speaker Notes)**：\n  > {notes}\n\n---\n\n")

print(f"[OK] Saved Markdown Script to: {MD_SCRIPT_PATH}")
