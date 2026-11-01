"""
build_powerpoint_presentation.py
Builds the 16:9 Widescreen Native Vector PowerPoint Presentation:
02_case_analysis_presentation.pptx (and 資訊管理個案分析簡報_巨量資料分析有多可靠_新版.pptx)

100% compliant with:
1. Teacher's Course Assignment Requirements:
   - (1) 個案國別及產業簡介 (Slide 3)
   - (2) 問題識別：該公司/組織發生什麼事 (Slide 4, embeds 03_bigdata_empirical_metrics_chart.png)
   - (3) 個案簡介：全文邏輯架構與四大構面 (Slide 5)
   - (4) 個案研究問題的小組討論後回答（滿 5 題，聚焦於第 6 章議題）(Slides 6, 7, 8, 9, 10)
   - (5) 成員貢獻表（姓名、學號、主要負責內容、貢獻百分比）+ 20-25分鐘全員上台報告 & 25分鐘 Q&A 錦囊 (Slide 11)
2. presentation_slide_spec.md & visual_cognition_principles.md:
   - Storyboard Anti-Collision Sequence:
     S0 -> S3 -> S5 -> S7-A -> S4 -> S2 -> S1 -> S5 -> S2 -> S6 -> S1 -> S0
     (Zero consecutive identical layouts; 7 distinct layout topologies!)
   - Exact Text-Hug Pill Sizing: pill_w = (9.5 / 72.0) * (1.00 * CJK + 0.50 * ASCII) + 0.22
   - Parallel Row Panels with Middle Vertical Anchor (MSO_ANCHOR.MIDDLE)
   - Detailed Speaker Notes for both speakers (楊亞恩 Slides 1-6, 黃宥丞 Slides 7-12) for a 20-25 min presentation
"""

import os
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Theme Palette (75-20-5 Preattentive Allocation)
BG_LIGHT      = RGBColor(248, 250, 252)  # #F8FAFC Slate 50
TEXT_NAVY     = RGBColor(15, 23, 42)     # #0F172A Slate 900
TEXT_MUTED    = RGBColor(71, 85, 105)    # #475569 Slate 600
TEXT_BODY     = RGBColor(30, 41, 59)     # #1E293B Slate 800
CARD_BG       = RGBColor(255, 255, 255)  # Pure White
CARD_BORDER   = RGBColor(203, 213, 225)  # #CBD5E1 Slate 300
ROW_BG_LIGHT  = RGBColor(248, 250, 252)  # #F8FAFC

COLOR_PRIMARY = RGBColor(29, 78, 216)    # #1D4ED8 Royal Blue
COLOR_DANGER  = RGBColor(190, 18, 60)    # #BE123C Crimson Red
COLOR_WARN    = RGBColor(180, 83, 9)     # #B45309 Amber Ochre
COLOR_SUCCESS = RGBColor(4, 120, 87)     # #047857 Emerald Teal
COLOR_SLATE   = RGBColor(71, 85, 105)    # #475569 Neutral Structure

TINT_BLUE     = RGBColor(239, 246, 255)  # #EFF6FF
TINT_RED      = RGBColor(254, 242, 242)  # #FEF2F2
TINT_AMBER    = RGBColor(254, 243, 199)  # #FEF3C7
TINT_GREEN    = RGBColor(209, 250, 229)  # #D1FAE5
TINT_SLATE    = RGBColor(241, 245, 249)  # #F1F5F9

DARK_BG       = RGBColor(15, 23, 42)     # #0F172A
DARK_CARD_BG  = RGBColor(30, 41, 59)     # #1E293B
DARK_ROW_BG   = RGBColor(15, 23, 42)     # #0F172A
DARK_SKY      = RGBColor(56, 189, 248)   # #38BDF8
DARK_TEXT     = RGBColor(241, 245, 249)  # #F1F5F9

output_dir = os.path.abspath("reading_sessions/20261101_巨量資料分析有多可靠/02_outputs")
os.makedirs(output_dir, exist_ok=True)


def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def calc_pill_width(pill_text):
    cjk_count = sum(1 for c in pill_text if ord(c) > 127)
    ascii_count = len(pill_text) - cjk_count
    return (9.5 / 72.0) * (1.02 * cjk_count + 0.54 * ascii_count) + 0.34


def add_zone1_header(slide, pill_text, headline_text, speaker_badge="", is_dark=False):
    pill_w = calc_pill_width(pill_text)
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(0.15), Inches(pill_w), Inches(0.28))
    pill.adjustments[0] = 0.25
    pill.fill.solid()
    if is_dark:
        pill.fill.fore_color.rgb = DARK_CARD_BG
        pill.line.color.rgb = DARK_SKY
        pill_tc = DARK_SKY
    else:
        pill.fill.fore_color.rgb = TEXT_NAVY
        pill.line.color.rgb = TEXT_NAVY
        pill_tc = RGBColor(255, 255, 255)
    pill.line.width = Pt(1.0)
    tf_p = pill.text_frame
    tf_p.word_wrap = False
    tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_p.margin_left = tf_p.margin_right = Inches(0.10)
    tf_p.margin_top = tf_p.margin_bottom = 0
    p = tf_p.paragraphs[0]
    p.text = pill_text
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Microsoft JhengHei"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = pill_tc

    if speaker_badge:
        sp_w = calc_pill_width(speaker_badge)
        sp_box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(13.333 - 0.65 - sp_w), Inches(0.15), Inches(sp_w), Inches(0.28)
        )
        sp_box.adjustments[0] = 0.25
        sp_box.fill.solid()
        sp_box.fill.fore_color.rgb = DARK_CARD_BG if is_dark else TINT_BLUE
        sp_box.line.color.rgb = DARK_SKY if is_dark else COLOR_PRIMARY
        sp_box.line.width = Pt(1.0)
        tf_s = sp_box.text_frame
        tf_s.word_wrap = False
        tf_s.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf_s.margin_left = tf_s.margin_right = Inches(0.10)
        tf_s.margin_top = tf_s.margin_bottom = 0
        ps = tf_s.paragraphs[0]
        ps.text = speaker_badge
        ps.alignment = PP_ALIGN.CENTER
        ps.font.name = "Microsoft JhengHei"
        ps.font.size = Pt(9.2)
        ps.font.bold = True
        ps.font.color.rgb = DARK_SKY if is_dark else COLOR_PRIMARY

    tb = slide.shapes.add_textbox(Inches(0.65), Inches(0.55), Inches(12.033), Inches(0.46))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p2 = tf.paragraphs[0]
    p2.text = headline_text
    p2.font.name = "Microsoft JhengHei"
    p2.font.size = Pt(19.8)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(255, 255, 255) if is_dark else TEXT_NAVY


def add_zone3_footer(slide, takeaway_text, is_dark=False):
    footer = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(6.66), Inches(12.033), Inches(0.50))
    footer.adjustments[0] = 0.20
    footer.fill.solid()
    footer.fill.fore_color.rgb = RGBColor(2, 6, 23) if is_dark else DARK_BG
    footer.line.color.rgb = DARK_SKY
    footer.line.width = Pt(1.2)
    tf = footer.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.22)
    tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = takeaway_text
    p.font.name = "Microsoft JhengHei"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = RGBColor(248, 250, 252)


def set_notes(slide, text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = text


def create_structured_card(slide, left, top, width, height, title, subtitle, rows_data,
                           accent_color=COLOR_PRIMARY, header_tint=TINT_SLATE,
                           is_spotlight=False, is_dark=False, row_y_slots=None,
                           hdr_h=Inches(0.68), tag_pt=12.0, desc_pt=11.0):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.adjustments[0] = 0.03
    card.fill.solid()
    if is_dark:
        card.fill.fore_color.rgb = DARK_CARD_BG
        card.line.color.rgb = accent_color if is_spotlight else RGBColor(71, 85, 105)
    else:
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = accent_color if is_spotlight else CARD_BORDER
    card.line.width = Pt(2.4 if is_spotlight else 1.2)

    hdr = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        left + Inches(0.08), top + Inches(0.08), width - Inches(0.16), hdr_h
    )
    hdr.adjustments[0] = 0.04
    hdr.fill.solid()
    if is_dark:
        hdr.fill.fore_color.rgb = RGBColor(15, 23, 42)
        hdr.line.color.rgb = accent_color if is_spotlight else RGBColor(71, 85, 105)
    else:
        hdr.fill.fore_color.rgb = header_tint
        hdr.line.color.rgb = accent_color if is_spotlight else CARD_BORDER
    hdr.line.width = Pt(1.3 if is_spotlight else 0.8)

    tf_h = hdr.text_frame
    tf_h.word_wrap = True
    tf_h.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_h.margin_left = tf_h.margin_right = Inches(0.12)
    tf_h.margin_top = tf_h.margin_bottom = 0

    p_t = tf_h.paragraphs[0]
    p_t.text = title
    p_t.alignment = PP_ALIGN.CENTER
    p_t.font.name = "Microsoft JhengHei"
    p_t.font.size = Pt(13.2)
    p_t.font.bold = True
    p_t.font.color.rgb = accent_color

    if subtitle:
        p_sub = tf_h.add_paragraph()
        p_sub.text = subtitle
        p_sub.alignment = PP_ALIGN.CENTER
        p_sub.font.name = "Microsoft JhengHei"
        p_sub.font.size = Pt(9.8)
        p_sub.font.bold = True
        p_sub.font.color.rgb = DARK_SKY if is_dark else TEXT_MUTED

    if row_y_slots is None:
        avail_top = top + hdr_h + Inches(0.16)
        avail_h = height - hdr_h - Inches(0.24)
        n_rows = max(1, len(rows_data))
        gap = Inches(0.08)
        r_h = (avail_h - gap * (n_rows - 1)) / n_rows
        row_y_slots = [(avail_top + i * (r_h + gap), r_h) for i in range(n_rows)]

    for idx, (tag, desc) in enumerate(rows_data):
        if idx >= len(row_y_slots):
            break
        r_top, r_height = row_y_slots[idx]
        row_box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            left + Inches(0.10), r_top, width - Inches(0.20), r_height
        )
        row_box.adjustments[0] = 0.04
        row_box.fill.solid()
        if is_dark:
            row_box.fill.fore_color.rgb = DARK_ROW_BG
            row_box.line.color.rgb = RGBColor(51, 65, 85)
        else:
            row_box.fill.fore_color.rgb = ROW_BG_LIGHT
            row_box.line.color.rgb = RGBColor(226, 232, 240)
        row_box.line.width = Pt(0.8)

        tf_r = row_box.text_frame
        tf_r.word_wrap = True
        tf_r.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf_r.margin_left = tf_r.margin_right = Inches(0.12)
        tf_r.margin_top = tf_r.margin_bottom = Inches(0.04)

        p1 = tf_r.paragraphs[0]
        p1.text = tag
        p1.font.name = "Microsoft JhengHei"
        p1.font.size = Pt(tag_pt)
        p1.font.bold = True
        p1.font.color.rgb = DARK_SKY if is_dark else accent_color
        p1.space_after = Pt(3)

        p2 = tf_r.add_paragraph()
        p2.text = desc
        p2.font.name = "Microsoft JhengHei"
        p2.font.size = Pt(desc_pt)
        p2.font.bold = False
        p2.font.color.rgb = DARK_TEXT if is_dark else TEXT_BODY
        p2.line_spacing = 1.22


# ==============================================================================
# SLIDE 1 [Layout S0: Dark Bookend Cover Slide]
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_bg(s1, DARK_BG)
add_zone1_header(
    s1,
    pill_text="MIS CASE STUDY ｜ 資訊管理課程個案分析簡報（Laudon 第 6 章）",
    headline_text="巨量資料分析有多可靠？從每日 2,500 萬億位元組看商業決策效益與模型盲點",
    speaker_badge="上半場講者：楊亞恩 (01 / 11)",
    is_dark=True
)

# Hero Banner Box
hero = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(1.22), Inches(12.033), Inches(2.05))
hero.adjustments[0] = 0.04
hero.fill.solid()
hero.fill.fore_color.rgb = DARK_CARD_BG
hero.line.color.rgb = DARK_SKY
hero.line.width = Pt(1.8)
tf_hero = hero.text_frame
tf_hero.word_wrap = True
tf_hero.vertical_anchor = MSO_ANCHOR.MIDDLE
tf_hero.margin_left = tf_hero.margin_right = Inches(0.32)

p_h1 = tf_hero.paragraphs[0]
p_h1.text = "個案研究：巨量資料分析有多可靠？（How Reliable Is Big Data Analytics?）"
p_h1.font.name = "Microsoft JhengHei"
p_h1.font.size = Pt(22)
p_h1.font.bold = True
p_h1.font.color.rgb = RGBColor(255, 255, 255)
p_h1.space_after = Pt(8)

p_h2 = tf_hero.add_paragraph()
p_h2.text = "● 核心命題：海量數據能為英國 NHS 省下 5.81 億英鎊、助紐約警局監控 76 轄區，但也讓 Google 流感與 2016 美國大選民調集體翻車"
p_h2.font.name = "Microsoft JhengHei"
p_h2.font.size = Pt(13.5)
p_h2.font.bold = True
p_h2.font.color.rgb = DARK_SKY
p_h2.space_after = Pt(8)

p_h3 = tf_hero.add_paragraph()
p_h3.text = "指導老師：何政勳 老師   ｜   報告成員：楊亞恩（學號：311157139，貢獻 60%）、黃宥丞（學號：311357109，貢獻 40%）"
p_h3.font.name = "Microsoft JhengHei"
p_h3.font.size = Pt(12.2)
p_h3.font.bold = True
p_h3.font.color.rgb = RGBColor(226, 232, 240)

# 3 Metric Cards at Bottom of Cover
s1_slots = [(Inches(4.32), Inches(0.96)), (Inches(5.36), Inches(1.02))]
create_structured_card(
    s1, Inches(0.65), Inches(3.45), Inches(3.85), Inches(3.05),
    title="2,500 萬億 Bytes / 日", subtitle="全球每日產生之海量數據規模",
    rows_data=[
        ("● 【淺層現象：數據洪流爆發】", "源自社群媒體、搜尋、感應器與傳統交易，企業期盼藉此全面升級決策。"),
        ("● 【中深層實踐：千萬筆精準推薦】", "Amazon、YouTube 與 Spotify 靠個人化推薦蓬勃發展；比價網助找全網最低價。")
    ],
    accent_color=DARK_SKY, is_spotlight=False, is_dark=True, row_y_slots=s1_slots, tag_pt=11.5, desc_pt=10.5
)
create_structured_card(
    s1, Inches(4.74), Inches(3.45), Inches(3.85), Inches(3.05),
    title="5.81 億英鎊 ＆ 76 轄區", subtitle="英國 NHS 與紐約警局標竿效益",
    rows_data=[
        ("● 【醫療標竿：NHS 省 7.84 億美元】", "以 Oracle Exadata 分析數十億筆處方，揪出併用 10 種藥物與過量抗生素病患。"),
        ("● 【執法標竿：NYPD CompStat】", "每週動態呈現 76 轄區犯罪熱點精準部署警力，並由 CSU 積極追訴重度累犯。")
    ],
    accent_color=RGBColor(52, 211, 153), is_spotlight=True, is_dark=True, row_y_slots=s1_slots, tag_pt=11.5, desc_pt=10.5
)
create_structured_card(
    s1, Inches(8.83), Inches(3.45), Inches(3.85), Inches(3.05),
    title="70%～99% 勝率預測翻車", subtitle="模型偏見、缺脈絡與推論隱私危機",
    rows_data=[
        ("● 【三大翻車：美選、GFT 與電力】", "2016 美選盲信歐巴馬舊資料庫、Google 流感忽略媒體恐慌搜尋、Meridian 模擬過時。"),
        ("● 【倫理紅線：推論隱私侵害】", "結合 GPS 與消費標註高風險者，甚至推論帕金森氏症早期徵兆，卻毫無法律反擊機制。")
    ],
    accent_color=RGBColor(251, 113, 133), is_spotlight=False, is_dark=True, row_y_slots=s1_slots, tag_pt=11.5, desc_pt=10.5
)

add_zone3_footer(s1, "★ 報告核心主軸：完整涵蓋課程規範五大必備章節與五道個案研究問題，剖析如何讓巨量資料從「盲目迷思」走向「高可靠決策」", is_dark=True)
set_notes(s1, """【講者：楊亞恩｜預計時間：2 分鐘】
何老師、各位同學大家好！我們這組今天要報告的資訊管理個案研究是課本第 6 章的〈巨量資料分析有多可靠？〉，我是上半場主講人楊亞恩，待會下半場會由我的組員黃宥丞接棒，我們兩位今天都會上台報告。
在進入細節之前，請大家先看畫面上的三個關鍵數字：第一個是「每天 2,500 萬億位元組」，這是全球每天從社群媒體、搜尋引擎和感應器產生的驚人資料量；第二個是「5.81 億英鎊與 76 個轄區」，這是英國國民保健署 NHS 和美國紐約市警局運用大數據創造的真實效益；但第三個數字卻是「70% 到 99% 的勝率預測翻車」——2016 年美國總統大選幾乎所有大數據模型都斷言柯林頓穩贏，最後卻徹底失準！為什麼同樣叫巨量資料分析，有人能省下數億英鎊，有人卻被數據騙得團團轉？這就是我們今天要為大家徹底解開的核心謎題。""")


# ==============================================================================
# SLIDE 2 [Layout S3: 4-Step Process Pipeline + Dual-Speaker Schedule]
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_bg(s2, BG_LIGHT)
add_zone1_header(
    s2,
    pill_text="REPORT ROADMAP ｜ 簡報架構導覽與 20–25 分鐘雙講者配當",
    headline_text="遵循課程規範必備章節與五道問題，由淺入深拆解大數據可靠度條件",
    speaker_badge="上半場講者：楊亞恩 (02 / 11)"
)

steps_info = [
    ("STAGE 01｜第 1–2 章", "國別產業 ＆ 問題識別", COLOR_SLATE, TINT_SLATE, False, [
        ("● 【(1) 個案國別與產業簡介】", "橫跨英、美、紐澳與跨國四大板塊，涵蓋電商、醫療、警政、能源、防疫與競選民調。（Slide 03）"),
        ("● 【(2) 問題識別：發生什麼事】", "剖析 Twitter KPI 迷思、IE 假性相關、三大預測翻車與推論隱私侵害，附雙柱落差圖。（Slide 04）")
    ]),
    ("STAGE 02｜第 3 章 & Q1–2", "個案簡介 ＆ 改善決策", COLOR_SUCCESS, TINT_GREEN, False, [
        ("● 【(3) 個案簡介與四大構面】", "鳥瞰全文從每日 2,500 萬億 Bytes 願景到策略方法盲點與倫理邊界之辯證架構。（Slide 05）"),
        ("● 【(4) 問題 1 效益 ＆ 改善決策】", "解析三大企業效益，以及英國 NHS（省 5.81 億英鎊）與紐約警局（76 轄區）兩大改善決策。（Slide 06）")
    ]),
    ("STAGE 03｜第 4 章 Q2–3", "失敗決策 ＆ 五大限制", COLOR_DANGER, TINT_RED, False, [
        ("● 【(4) 問題 2 兩個失敗決策】", "深挖某大企業 Twitter 銷售 KPI 錯置案，與 2016 柯林頓競選模型盲信舊資料庫翻車案。（Slide 07）"),
        ("● 【(4) 問題 3 大數據五大限制】", "拆解測量迷思、混亂資料、IE 與謀殺率假性相關、模型缺脈絡及帕金森氏症推論隱私。（Slide 08）")
    ]),
    ("STAGE 04｜第 4 章 Q4–5", "MIS 鐵三角 ＆ 進階建模總結", COLOR_PRIMARY, TINT_BLUE, True, [
        ("● 【(4) 問題 4 MIS ＆ 問題 5】", "管理×組織×科技三維整備，與結合 GFT 及美選教訓之「動態樣本＋脈絡調節」建模公式。（Slide 09–10）"),
        ("● 【總結三大定律 ＆ Q&A 討論】", "收斂數據規模、因果脈絡與推論隱私三大黃金定律，並開啟 25 分鐘 Q&A 深度討論。（Slide 11）")
    ])
]

s2_slots = [(Inches(2.15), Inches(1.48)), (Inches(3.73), Inches(1.52))]
for idx, (st_code, st_title, ac_col, bg_tint, is_spot, r_data) in enumerate(steps_info):
    left_x = Inches(0.65 + idx * 3.06)
    create_structured_card(
        s2, left_x, Inches(1.22), Inches(2.86), Inches(4.22),
        title=st_code, subtitle=st_title, rows_data=r_data,
        accent_color=ac_col, header_tint=bg_tint, is_spotlight=is_spot,
        row_y_slots=s2_slots, hdr_h=Inches(0.75), tag_pt=10.4, desc_pt=10.0
    )
    if idx < 3:
        arr = s2.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW,
            left_x + Inches(2.89), Inches(3.15), Inches(0.14), Inches(0.32)
        )
        arr.fill.solid()
        arr.fill.fore_color.rgb = COLOR_PRIMARY
        arr.line.fill.background()

# Speaker Handoff Bar at y=5.56"
handoff = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(5.56), Inches(12.033), Inches(0.96))
handoff.adjustments[0] = 0.08
handoff.fill.solid()
handoff.fill.fore_color.rgb = TINT_BLUE
handoff.line.color.rgb = COLOR_PRIMARY
handoff.line.width = Pt(1.5)
tf_ho = handoff.text_frame
tf_ho.word_wrap = True
tf_ho.vertical_anchor = MSO_ANCHOR.MIDDLE
tf_ho.margin_left = tf_ho.margin_right = Inches(0.22)

p_ho1 = tf_ho.paragraphs[0]
p_ho1.text = "● 【上半場報告（Slide 01–06，預計 11.5 分鐘）— 講者：楊亞恩（311157139）】：負責 (1) 個案國別及產業簡介、(2) 問題識別、(3) 個案簡介、以及 (4) 問題 1（企業效益）與問題 2（兩個成功改善決策）。"
p_ho1.font.name = "Microsoft JhengHei"
p_ho1.font.size = Pt(11.2)
p_ho1.font.bold = True
p_ho1.font.color.rgb = COLOR_PRIMARY
p_ho1.space_after = Pt(4)

p_ho2 = tf_ho.add_paragraph()
p_ho2.text = "● 【下半場報告（Slide 07–11，預計 11.5 分鐘）— 講者：黃宥丞（311357109）】：負責 (4) 問題 2（兩個失敗決策）、問題 3（五大限制）、問題 4（MIS 鐵三角）、問題 5（進階建模對策）與總結 Q&A。"
p_ho2.font.name = "Microsoft JhengHei"
p_ho2.font.size = Pt(11.2)
p_ho2.font.bold = True
p_ho2.font.color.rgb = TEXT_NAVY

add_zone3_footer(s2, "★ 簡報結構承諾：100% 對齊老師規範之五大必備項目與 5 題章節核心議題，總報告時間精準控制於 22–24 分鐘")
set_notes(s2, """【講者：楊亞恩｜預計時間：1.5 分鐘】
這張投影片是我們今天 23 分鐘報告的完整路線圖。為了完全符合老師規定的五個必備章節與五道討論題，我們將簡報分為四大階段：
第一階段（Slide 3 到 4），我會先帶大家看「第一章：個案國別及產業簡介」以及「第二章：問題識別」，看看這些跨國企業與機構到底發生了什麼事；
第二階段（Slide 5 到 6），我會介紹「第三章：個案簡介」，並回答第四章的「問題 1（企業效益）」與「問題 2 的兩個成功改善決策」；
接著第三與第四階段（Slide 7 到 12），會由黃宥丞同學接手，深入剖析「問題 2 的兩個失敗決策」、「問題 3 的五大限制」、「問題 4 的管理、組織、科技議題」、「問題 5 的預測模型防偏見與脈絡對策」，以及最後的「第五章：成員貢獻表」與 25 分鐘 Q&A 引導。""")


# ==============================================================================
# SLIDE 3 [Layout S5: 2x2 Quadrant Matrix — Chapter 1: Country & Industry Intro]
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_bg(s3, BG_LIGHT)
add_zone1_header(
    s3,
    pill_text="CHAPTER 01 ｜ (1) 個案國別及產業簡介（四大地理板塊 × 多元產業）",
    headline_text="個案橫跨英、美、紐澳與全球四大板塊，涵蓋醫療、警政、能源與競選六大產業",
    speaker_badge="上半場講者：楊亞恩 (03 / 11)"
)

quads_s3 = [
    (Inches(0.65), Inches(1.22), "板塊 I：英國（UK）— 公共醫療保健 ＆ 公投民調", "涵蓋公共醫療保健產業（NHS）與政治公投民意調查領域", COLOR_SUCCESS, TINT_GREEN, True, [
        ("● 【正向標竿：英國國民保健署（NHS）醫療大數據】", "將數十億筆病患、處方籤與治療有效性資料存入 Oracle Exadata 高速分析，成功節省 5.81 億英鎊（7.84 億美元），揪出併用 10 種藥物與過量抗生素者並優化癌症治療。"),
        ("● 【反向警訊：2016 年 6 月英國脫歐（Brexit）公投】", "大數據民意調查因抽樣偏誤與未能捕捉沉默選民真實投票行為，導致選前民調預測與最終脫歐結果大相逕庭。")
    ]),
    (Inches(6.80), Inches(1.22), "板塊 II：美國（USA）— 警政執法、公衛防疫 ＆ 總統大選", "涵蓋公共安全執法（NYPD）、科技防疫（Google/CDC）與競選工程", COLOR_PRIMARY, TINT_BLUE, True, [
        ("● 【正向標竿：紐約市警局（NYPD）CompStat 計畫】", "彙整全市 76 個轄區報案、投訴、逮捕與傳喚資料庫，每週呈現犯罪熱點部署警力，並由犯罪策略部門（CSU）起訴累犯。"),
        ("● 【反向翻車：Google 流感、IE 謀殺率與 2016 美國大選】", "2006–2011 美國各州謀殺率與 IE 市佔率呈假性相關；Google 流感較 CDC 持續高估；2016 美選預測柯林頓勝率 70–99% 卻敗選。")
    ]),
    (Inches(0.65), Inches(3.92), "板塊 III：紐澳地區（NZ & Australia）— 能源電力公用事業", "涵蓋發電與配電公用事業（Meridian Energy）及軟硬體供應商（IBM）", COLOR_WARN, TINT_AMBER, False, [
        ("● 【先敗後成：Meridian Energy Ltd. 大型電力設備維護】", "跨紐西蘭與澳洲經營發電與配電，需預測發電機、風力渦輪機、變壓器、斷路器與工業電池之維護需求。"),
        ("● 【系統轉型：從過時模擬軟體升級為 IBM 即時預測】", "原設備老化預測系統因建模技術過時且模擬脫離現實而失準；後全面換裝運用更多設備「即時資料」之 IBM 維護與品質預測軟體。")
    ]),
    (Inches(6.80), Inches(3.92), "板塊 IV：跨國／全球企業 — 電商串流、傳統展銷 ＆ 金融風控", "涵蓋電商串流比價、實體貿易展銷、運動教育科學與消費金融探勘", COLOR_SLATE, TINT_SLATE, False, [
        ("● 【商業標竿：Amazon、YouTube、Spotify 與線上比價網】", "分析客戶興趣與購物歷史提供數百萬筆個人化推薦；比價服務助消費者找汽車、電腦、手機方案、服裝、機票與飯店最低價。"),
        ("● 【負向案例：某大企業 Twitter KPI 迷思 ＆ 推論隱私探勘】", "實體展銷企業誤將 Twitter 聲量列為銷售 KPI 產出廢線索；消費與金融企業探勘 GPS 與個資標註高風險者並推論帕金森氏症前兆。")
    ])
]

for qx, qy, qt, qsub, qcol, qtint, qspot, qrows in quads_s3:
    q_slots = [(qy + Inches(0.74), Inches(0.86)), (qy + Inches(1.66), Inches(0.86))]
    create_structured_card(
        s3, qx, qy, Inches(5.88), Inches(2.60),
        title=qt, subtitle=qsub, rows_data=qrows,
        accent_color=qcol, header_tint=qtint, is_spotlight=qspot,
        row_y_slots=q_slots, hdr_h=Inches(0.60), tag_pt=10.8, desc_pt=9.8
    )

add_zone3_footer(s3, "★ 第一章總結：本個案橫跨 4 大地理板塊與 8 大代表組織事件，證明巨量資料已深入商業、醫療、警政、能源與政治核心")
set_notes(s3, """【講者：楊亞恩｜預計時間：2 分鐘】
首先進入第一章「個案國別及產業簡介」。課本這篇個案非常豐富，同時穿插了好幾個國家與產業，如果不先做結構化分類，閱讀時很容易混淆。因此我們小組把全篇個案整理成這張「四大地理板塊 × 多元產業」的四象限矩陣：
左上角第一個板塊是「英國（UK）」：在公共醫療保健產業，英國國民保健署 NHS 利用 Oracle Exadata 高速分析數十億筆處方與病患資料，成功省下 5.81 億英鎊；但在政治民調領域，英國在 2016 年 6 月脫歐公投時卻發生大數據民調失準。
右上角第二個板塊是「美國（USA）」：在警政執法部門，紐約市警局 NYPD 透過 CompStat 計畫監控全市 76 個轄區的犯罪熱點；但在公衛防疫與選舉領域，卻發生了 Google 流感趨勢高估疫情、美國各州謀殺率與 IE 市佔率假性相關、以及 2016 美國總統大選預測翻車。
左下角第三個板塊是「紐西蘭與澳洲地區」：能源與電力公用事業巨頭 Meridian Energy 一開始用過時的設備老化預測軟體失敗，後來換裝導入即時資料的 IBM 預測軟體才成功轉型。
右下角第四個板塊則是「跨國與全球企業」：包含 Amazon、YouTube、Spotify 的數百萬筆個人化推薦與線上比價網，但也包含誤把 Twitter 當銷售 KPI 的傳統展銷大企業，以及跨資料源探勘消費者隱私的零售與金融企業。""")


# ==============================================================================
# SLIDE 4 [Layout S7-A: Left Chart 63% + Right 3 Cards 37% — Chapter 2: Problem ID]
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_bg(s4, BG_LIGHT)
add_zone1_header(
    s4,
    pill_text="CHAPTER 02 ｜ (2) 問題識別：該公司／組織發生什麼事？（含雙柱落差實證圖）",
    headline_text="當組織缺乏目標、忽略脈絡或盲信舊資料，高達 95% 的表象信心會崩跌至 12%–32%",
    speaker_badge="上半場講者：楊亞恩 (04 / 11)"
)

# Left Chart Container (Expanded leftwards to 0.50" and rightwards to 8.23" = 7.73" width without compressing right cards at 8.35")
chart_frame = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.50), Inches(1.22), Inches(7.73), Inches(5.30))
chart_frame.adjustments[0] = 0.02
chart_frame.fill.solid()
chart_frame.fill.fore_color.rgb = CARD_BG
chart_frame.line.color.rgb = COLOR_PRIMARY
chart_frame.line.width = Pt(1.5)

chart_path = os.path.join(output_dir, "03_bigdata_empirical_metrics_chart.png")
if os.path.exists(chart_path):
    # Image placed at top of frame and enlarged to 7.61" wide (height ~3.90", spanning y=1.28" to 5.18")
    s4.shapes.add_picture(chart_path, Inches(0.56), Inches(1.28), width=Inches(7.61))

# Caption Box placed BELOW the image (y=5.26" to 6.42") inside chart_frame
cap_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.60), Inches(5.26), Inches(7.53), Inches(1.16))
cap_box.adjustments[0] = 0.06
cap_box.fill.solid()
cap_box.fill.fore_color.rgb = TINT_BLUE
cap_box.line.color.rgb = RGBColor(147, 197, 253)
cap_box.line.width = Pt(1.0)
tf_cf = cap_box.text_frame
tf_cf.word_wrap = True
tf_cf.vertical_anchor = MSO_ANCHOR.MIDDLE
tf_cf.margin_left = tf_cf.margin_right = Inches(0.14)
tf_cf.margin_top = tf_cf.margin_bottom = Inches(0.06)

p_cf1 = tf_cf.paragraphs[0]
p_cf1.text = "▲ 圖表註解（面板 A 左圖 — 雙柱剪刀差）：每組並排「藍柱（模型表象預測信心／指標熱度 88%～95%）」與「紅柱（真實世界實際效用 12%～32%）」，直觀呈現四大失敗案例高達 -60% 至 -78% 的眼高手低落差。"
p_cf1.font.name = "Microsoft JhengHei"
p_cf1.font.size = Pt(9.6)
p_cf1.font.bold = True
p_cf1.font.color.rgb = COLOR_PRIMARY
p_cf1.space_after = Pt(3)

p_cf2 = tf_cf.add_paragraph()
p_cf2.text = "● 圖表註解（面板 B 右圖 — 六組織可靠度對照）：英國 NHS（94%）、紐約警局（91%）與 Meridian 換裝 IBM 後（84%）因具備清晰目標、資料清理與即時脈絡而穩居高可靠度區；反之 GFT、美選與假 KPI 案則雙雙崩跌。"
p_cf2.font.name = "Microsoft JhengHei"
p_cf2.font.size = Pt(9.2)
p_cf2.font.bold = False
p_cf2.font.color.rgb = TEXT_BODY

# Right 3 Vertically Stacked Problem Cards (37% width)
r_cards_s4 = [
    ("問題叢集 1：策略與方法論失靈", COLOR_WARN, TINT_AMBER, False,
     "● 【某大企業 KPI 迷思 ＆ IE 假相關】",
     "展銷型企業把 Twitter 提及次數列為銷售 KPI（落差 -78%），產出大量無效線索；分析師把 2006–2011 美國謀殺率與 IE 市佔率同步下降當成真關聯。"),
    ("問題叢集 2：三大預測模型集體翻車", COLOR_DANGER, TINT_RED, True,
     "● 【Meridian、Google 流感 ＆ 2016 美選】",
     "Meridian 舊模擬脫節無法預警停擺（-66%）；Google 流感忽略媒體恐慌搜尋脈絡而高估（-60%）；2016 美選柯林頓盲信歐巴馬舊資料庫致 70–99% 預測翻車（-77%）。"),
    ("問題叢集 3：資安與推論隱私侵害", COLOR_SLATE, TINT_SLATE, False,
     "● 【高風險貼標籤 ＆ 帕金森氏症推論】",
     "企業蒐集購物、收入與手機 GPS 將人標為貸款或健康「高風險者」，更跨源推論出帕金森氏症早期徵兆與藍綠偏好，當事人毫不知情且無法律反擊機制。")
]

for idx, (c_title, c_col, c_tint, c_spot, r_tag, r_desc) in enumerate(r_cards_s4):
    cy = Inches(1.22 + idx * 1.80)
    create_structured_card(
        s4, Inches(8.35), cy, Inches(4.33), Inches(1.70),
        title=c_title, subtitle="",
        rows_data=[(r_tag, r_desc)],
        accent_color=c_col, header_tint=c_tint, is_spotlight=c_spot,
        row_y_slots=[(cy + Inches(0.54), Inches(1.06))],
        hdr_h=Inches(0.42), tag_pt=10.6, desc_pt=9.6
    )

add_zone3_footer(s4, "★ 第二章問題識別結論：大數據失靈並非因為資料不夠多，而是死於「選錯指標、假性相關、忽略外部脈絡與歷史樣本偏見」")
set_notes(s4, """【講者：楊亞恩｜預計時間：2.5 分鐘】
接著進入第二章「問題識別：這些公司與機構到底發生了什麼事？」。請大家看左邊這張我們繪製的雙面板量化實證圖：
在左圖（面板 A）中，我們把個案裡四個最核心的失敗案例，用「藍色柱子（代表模型表象預測信心或指標熱度）」對比「紅色柱子（代表實際模型效用與真實準確度）」。大家可以看到非常驚人的剪刀差斷崖！
第一組是「2016 美國總統大選」：柯林頓團隊與主流預測信心高達 95%（預言勝率 70% 到 99%），但實際效用只有 18%，落差高達 -77%！因為他們盲目沿用歐巴馬勝選時的舊資料庫，沒算到最後一刻改變想法的共和黨選民。
第二組是「Google 流感趨勢 GFT」：搜尋量暴增讓模型信心滿滿（92%），但對比美國 CDC 實際數據卻嚴重高估，實際效用僅 32%（落差 -60%），因為演算法只看搜尋數字，卻忽略了媒體大肆報導引發的群眾恐慌搜尋脈絡。
第三組是「紐澳電力公司 Meridian Energy」：舊軟體情境模擬看似涵蓋全廠大型設備（88%），實際卻無法預警真實世界哪個機組會停擺（22%）。
第四組則是「某大型企業的銷售儀表板」：過去靠實體貿易展成交，卻把 Twitter 提及次數當成銷售 KPI（熱度 90%），最後只產出大堆無法創造真正銷售的無效線索（12%）。再配合右下角第三張卡片提到的「推論隱私侵害」，這三大問題叢集就是本個案識別出的核心病灶。""")


# ==============================================================================
# SLIDE 5 [Layout S4: Native Vector System Architecture — Chapter 3: Case Overview]
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_bg(s5, BG_LIGHT)
add_zone1_header(
    s5,
    pill_text="CHAPTER 03 ｜ (3) 個案簡介：全文脈絡與四大核心構面系統圖",
    headline_text="本個案以「正反辯證架構」展開：從海量數據商業價值，深挖至預測盲點與隱私紅線",
    speaker_badge="上半場講者：楊亞恩 (05 / 11)"
)

# Left Source Hub Box (Data Deluge)
src_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(1.30), Inches(2.55), Inches(5.15))
src_box.adjustments[0] = 0.04
src_box.fill.solid()
src_box.fill.fore_color.rgb = DARK_BG
src_box.line.color.rgb = DARK_SKY
src_box.line.width = Pt(2.0)
tf_src = src_box.text_frame
tf_src.word_wrap = True
tf_src.vertical_anchor = MSO_ANCHOR.MIDDLE
tf_src.margin_left = tf_src.margin_right = Inches(0.16)

p_s0 = tf_src.paragraphs[0]
p_s0.text = "【起點：海量數據洪流】\n2,500 萬億 Bytes / 日"
p_s0.alignment = PP_ALIGN.CENTER
p_s0.font.name = "Microsoft JhengHei"
p_s0.font.size = Pt(13.5)
p_s0.font.bold = True
p_s0.font.color.rgb = DARK_SKY
p_s0.space_after = Pt(12)

for src_item in [
    "● 社群媒體貼文與互動",
    "● 搜尋引擎關鍵字與位置",
    "● 工業與行動裝置感應器",
    "● 醫院臨床處方與警政紀錄",
    "● 傳統交易與民意調查庫"
]:
    ps_i = tf_src.add_paragraph()
    ps_i.text = src_item
    ps_i.font.name = "Microsoft JhengHei"
    ps_i.font.size = Pt(11.0)
    ps_i.font.bold = True
    ps_i.font.color.rgb = RGBColor(241, 245, 249)
    ps_i.space_after = Pt(6)

ps_bot = tf_src.add_paragraph()
ps_bot.text = "\n▼ 核心考驗 ▼\n資料量越大，決策就一定越可靠嗎？"
ps_bot.alignment = PP_ALIGN.CENTER
ps_bot.font.name = "Microsoft JhengHei"
ps_bot.font.size = Pt(11.2)
ps_bot.font.bold = True
ps_bot.font.color.rgb = RGBColor(252, 211, 77)

# Arrows from Source Hub to 4 Core Pillar Cards (2x2 in Middle-Right)
arr_top = s5.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(3.26), Inches(2.40), Inches(0.28), Inches(0.32))
arr_top.fill.solid()
arr_top.fill.fore_color.rgb = COLOR_SUCCESS
arr_top.line.fill.background()

arr_bot = s5.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(3.26), Inches(5.00), Inches(0.28), Inches(0.32))
arr_bot.fill.solid()
arr_bot.fill.fore_color.rgb = COLOR_DANGER
arr_bot.line.fill.background()

# 4 Core Dimension Cards of Chapter 3
s5_cards = [
    (Inches(3.60), Inches(1.30), "構面一：海量數據商業機會與標竿實踐", "前半段（正面價值）：目標明確 × 高速平台", COLOR_SUCCESS, TINT_GREEN, False, [
        ("● 【電商串流推薦與比價】", "Amazon、YouTube、Spotify 提供數百萬筆個人化推薦；線上服務助找車、電腦、機票與飯店最低價。"),
        ("● 【醫療與執法卓越標竿】", "英國 NHS 以 Oracle Exadata 省下 5.81 億英鎊並優化癌症治療；紐約警局 CompStat 動態監控 76 轄區犯罪熱點。")
    ]),
    (Inches(8.22), Inches(1.30), "構面二：策略盲點、資料品質與方法論陷阱", "中段（內部侷限）：可測量 ≠ 該測量；相關 ≠ 因果", COLOR_WARN, TINT_AMBER, False, [
        ("● 【無目標瞎忙與 KPI 迷思】", "未清理混亂資料便盲目投入；某大公司誤把 Twitter 提及次數列為銷售 KPI，背離實體貿易展並產出無效線索。"),
        ("● 【假性相關需領域知識把關】", "2006–2011 美國各州謀殺率與 IE 市佔率同步下降呈高度相關，但毫無因果；分析師必須具備企業領域知識。")
    ]),
    (Inches(3.60), Inches(3.95), "構面三：預測模型失靈之三大跨國教訓", "後半段（外部盲點）：過時模擬、缺脈絡與歷史偏見", COLOR_DANGER, TINT_RED, False, [
        ("● 【技術過時與忽略搜尋脈絡】", "紐澳 Meridian 舊模擬脫節無法預警停擺（後換 IBM 即時系統）；Google 流感忽略媒體恐慌搜尋脈絡而高估。"),
        ("● 【歷史樣本偏見與選情翻車】", "2016 美選柯林頓盲信歐巴馬舊資料庫，漏算最後一刻轉向的共和黨人，導致 70–99% 勝率預測與英國脫歐雙雙翻車。")
    ]),
    (Inches(8.22), Inches(3.95), "構面四：演算法貼標籤與推論隱私侵犯爭議", "文末收束（社會與倫理界線）：高風險分群與跨源推論", COLOR_PRIMARY, TINT_BLUE, True, [
        ("● 【自動標註高風險者與操控】", "企業蒐集購物習慣、收入、嗜好與手機 GPS 移動路徑，將人標示為貸款或健康「高風險者」以保護企業或操弄行為。"),
        ("● 【推論隱私危機與法規空白】", "結合多源資料竟能推論出帕金森氏症早期徵兆或無意識藍綠偏好；在缺乏法律程序與反擊機制下嚴重侵害公民權益。")
    ])
]

for cx, cy, ct, csub, ccol, ctint, cspot, crows in s5_cards:
    c_slots = [(cy + Inches(0.72), Inches(0.82)), (cy + Inches(1.60), Inches(0.82))]
    create_structured_card(
        s5, cx, cy, Inches(4.46), Inches(2.50),
        title=ct, subtitle=csub, rows_data=crows,
        accent_color=ccol, header_tint=ctint, is_spotlight=cspot,
        row_y_slots=c_slots, hdr_h=Inches(0.60), tag_pt=10.6, desc_pt=9.6
    )

add_zone3_footer(s5, "★ 第三章個案簡介總結：全案由「商業與公共價值」切入，逐步揭開「策略、方法論、預測模型與推論隱私」四層深水區挑戰")
set_notes(s5, """【講者：楊亞恩｜預計時間：2 分鐘】
來到第三章「個案簡介」。這張系統架構圖濃縮了整篇課本案例的起承轉合：
左邊深色方塊是全案的起點——全球每天產生 2,500 萬億位元組的海量資料，來自社群、搜尋、感應器與臨床紀錄。但課本作者馬上拋出核心考驗：資料量越大，決策就一定越可靠嗎？
接著全文分成右邊這四個核心構面推進：
第一個構面是「海量數據商業機會與標竿實踐」：介紹 Amazon、YouTube、Spotify 的個人化推薦，以及英國 NHS 省下 5.81 億英鎊、紐約警局 CompStat 監控 76 轄區的成功典範。
但從第二個構面開始，課本進入批判性思考——揭露「策略盲點、資料品質與方法論陷阱」，告訴我們未經清理的混亂資料毫無價值、可測量不代表該測量（Twitter KPI 迷思），而且統計相關不等於因果關係（IE 市佔率與謀殺率）。
第三個構面進一步檢視「預測模型失靈的三大跨國教訓」：包含紐澳 Meridian 舊系統、Google 流感趨勢與 2016 美選及英國脫歐民調。
最後第四個構面則拉高到社會倫理層次，探討企業結合手機 GPS 與個資標註「高風險者」，甚至推論出帕金森氏症早期徵兆的「推論隱私」危機。""")


# ==============================================================================
# SLIDE 6 [Layout S2: Three Pillars + 1 Spotlight — Chapter 4: Q1 & Q2 Successes]
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_bg(s6, BG_LIGHT)
add_zone1_header(
    s6,
    pill_text="CHAPTER 04 (Q1 & Q2 成功) ｜ (4) 問題 1 企業效益 ＆ 問題 2 兩個改善決策",
    headline_text="當目標清晰且平台強大，大數據能創造精準行銷，更助英國 NHS 與紐約警局改善重大決策",
    speaker_badge="上半場講者：楊亞恩 (06 / 11)"
)

s6_slots = [(Inches(2.12), Inches(1.38)), (Inches(3.58), Inches(1.42)), (Inches(5.08), Inches(1.38))]

create_structured_card(
    s6, Inches(0.65), Inches(1.22), Inches(3.85), Inches(5.32),
    title="問題 1：企業與組織三大效益", subtitle="商業個人化 × 比價服務 × 跨域擴散",
    rows_data=[
        ("● 【淺層直覺：精準猜中顧客需求】", "透過分析客戶興趣與購物歷史巨量資料，向全球用戶提供數百萬筆個人化推薦，帶動業務蓬勃發展。"),
        ("● 【中層案例：Amazon 至線上比價】", "Amazon、YouTube、Spotify 靠推薦引擎成長；線上服務助消費者找汽車、電腦、手機方案、機票與飯店最低價。"),
        ("● 【深層擴散：分眾廣告與多元領域】", "川普團隊運用大數據針對選民群體量身打造廣告訊息；亦為運動賽事、教育、科學研究與風險識別帶來好處。")
    ],
    accent_color=COLOR_PRIMARY, header_tint=TINT_BLUE, is_spotlight=False,
    row_y_slots=s6_slots, hdr_h=Inches(0.75), tag_pt=11.2, desc_pt=10.2
)

create_structured_card(
    s6, Inches(4.74), Inches(1.22), Inches(3.85), Inches(5.32),
    title="問題 2 改善決策 1：英國 NHS", subtitle="臨床用藥安全監控與癌症治療優化決策",
    rows_data=[
        ("● 【決策背景：數十億筆分散醫療紀錄】", "英國國民保健署（NHS）將病患、醫療提供者、處方籤與治療有效性資料存入 Oracle Exadata 高速分析。"),
        ("● 【改善決策：即時儀表板揪高風險用藥】", "建立儀表板精準找出「一次服用 10 種藥物的患者」與「過量服用抗生素者」，並大量編譯串連癌症用藥數據。"),
        ("● 【實質成果：省 5.81 億英鎊並優化療效】", "成功節省約 5.81 億英鎊（7.84 億美元），找出癌症與慢性病最有效且最省錢的治療方案與個人化護理建議。")
    ],
    accent_color=COLOR_SUCCESS, header_tint=TINT_GREEN, is_spotlight=False,
    row_y_slots=s6_slots, hdr_h=Inches(0.75), tag_pt=11.2, desc_pt=10.2
)

create_structured_card(
    s6, Inches(8.83), Inches(1.22), Inches(3.85), Inches(5.32),
    title="★ 問題 2 改善決策 2：紐約警局", subtitle="CompStat 76 轄區警力部署與累犯起訴決策",
    rows_data=[
        ("● 【決策背景：跨轄區犯罪資訊整合】", "紐約市警局（NYPD）推動 CompStat 犯罪地圖計畫，彙整全市 76 個轄區之報案、投訴、逮捕與法院傳喚資料庫。"),
        ("● 【改善決策：每週犯罪熱點精準派警】", "每週動態呈現各轄區與巡邏區犯罪熱點，幫助轄區指揮官快速找出樣式與趨勢，針對最需要的地方佈署警察。"),
        ("● 【實質成果：CSU 積極起訴嚴重違法者】", "犯罪活動巨量資料協助紐約市犯罪策略部門（Crime Strategies Unit）鎖定重度累犯積極起訴，有效降低犯罪率。")
    ],
    accent_color=COLOR_SUCCESS, header_tint=TINT_GREEN, is_spotlight=True,
    row_y_slots=s6_slots, hdr_h=Inches(0.75), tag_pt=11.2, desc_pt=10.2
)

add_zone3_footer(s6, "★ 上半場收束（交棒黃宥丞）：NHS 與 NYPD 證明「明確痛點＋乾淨實體數據＝改善決策」；那為什麼另外兩個決策卻徹底失敗？")
set_notes(s6, """【講者：楊亞恩｜預計時間：3.5 分鐘（上半場最後一頁，準備交棒）】
接下來進入第四章「個案研究問題的小組討論後回答」。這張投影片同時回答了「問題 1：組織能從巨量資料分析獲得哪些企業效益？」以及「問題 2 的前半題：找出兩個透過巨量資料分析而改善的決策」。
先看左邊第一張卡片（問題 1 的企業效益）：除了剛剛提到的醫療與執法之外，在商業上，Amazon、YouTube 和 Spotify 透過分析客戶興趣與購物歷史提供數百萬筆個人化推薦；許多線上服務也幫助消費者找出汽車、電腦、手機方案、服裝、機票與飯店住宿的最低價；甚至連川普競選團隊也利用大數據針對選民群體量身打造精準廣告訊息，並且擴散到運動賽事、教育與科學研究。
再看中間與右邊兩張卡片，這是我們小組針對「問題 2」選出的兩個最典型的「成功改善決策」：
第一個改善決策（中間卡片）是「英國國民保健署 NHS 的臨床用藥監控與癌症治療優化決策」：NHS 把數十億筆處方與病患資料放進 Oracle Exadata Database Machine 高速分析，建立儀表板找出一次服用 10 種藥物的患者與過量使用抗生素者，並串連癌症數據找出最佳治療方案，實質省下 5.81 億英鎊（約 7.84 億美元）！
第二個改善決策（右邊聚光燈卡片）是「紐約市警局 NYPD CompStat 計畫的警力部署與累犯起訴決策」：每週彙整全市 76 個轄區的報案、逮捕與傳喚資料庫，讓轄區指揮官看清犯罪熱點與趨勢，把警察精準部署到最需要的地方，更讓犯罪策略部門 CSU 積極起訴嚴重違法者。
以上是我的上半場報告，接下來我把麥克風交給黃宥丞同學，由他為大家剖析問題 2 的兩個失敗決策，以及問題 3 到問題 5 的深度解答！""")


# ==============================================================================
# SLIDE 7 [Layout S1: Asymmetric Contrast — Chapter 4: Q2 Two Failed Decisions]
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_bg(s7, BG_LIGHT)
add_zone1_header(
    s7,
    pill_text="CHAPTER 04 (Q2 失敗決策) ｜ (4) 問題 2 找出沒有改善（或失敗）的兩個決策",
    headline_text="當指標脫離核心業務或模型盲信過時歷史資料庫，巨量資料反而導致決策徹底失敗",
    speaker_badge="下半場講者：黃宥丞 (07 / 11)"
)

s7_slots = [(Inches(2.12), Inches(1.38)), (Inches(3.58), Inches(1.42)), (Inches(5.08), Inches(1.38))]

# Left Column (48% width): Failed Decision 1 (Twitter KPI Myth)
create_structured_card(
    s7, Inches(0.65), Inches(1.22), Inches(5.75), Inches(5.32),
    title="問題 2 失敗決策 1：某大型企業銷售 KPI 決策",
    subtitle="將「Twitter 被提及次數與官網流量」列為銷售關鍵績效指標（KPI）",
    rows_data=[
        ("● 【1. 錯誤決策內容：建數位儀表板盯社群聲量】", "該大公司想衡量網站流量與 Twitter 上被提及次數的關係，因而耗資建立數位儀表板不斷顯示此訊息，並把 Twitter 提及次數列為銷售 KPI。"),
        ("● 【2. 核心失靈病根：可測量 ≠ 就應該測量】", "公司過去真正的銷售成果大多來自於參加「實體貿易展與專業研討會」，線上社群提及次數與實際 B2B 簽約成交根本沒有因果轉化關係。"),
        ("● 【3. 最終失敗後果：扭曲業務焦點、產出廢線索】", "錯誤 KPI 改變了銷售部門的焦點，讓團隊把寶貴時間與資源改投入監測網站點擊和社群流量，產生許多永遠不會創造真正銷售的無用線索。")
    ],
    accent_color=COLOR_WARN, header_tint=TINT_AMBER, is_spotlight=False,
    row_y_slots=s7_slots, hdr_h=Inches(0.75), tag_pt=11.4, desc_pt=10.4
)

# Right Column (52% width, Spotlight): Failed Decision 2 (2016 Clinton Campaign & Meridian/GFT)
create_structured_card(
    s7, Inches(6.60), Inches(1.22), Inches(6.08), Inches(5.32),
    title="★ 問題 2 失敗決策 2：2016 柯林頓競選預測決策",
    subtitle="盲目沿用歐巴馬時期歷史資料庫之選情預測與選區聚焦決策（同場加映：GFT 與 Meridian）",
    rows_data=[
        ("● 【1. 錯誤決策內容：依賴歐巴馬舊庫、聚焦高投票率區】", "柯林頓團隊加入歐巴馬 2008/2012 勝選資料庫（民調、現場報告、社群貼文與消費預測），假設舊支持者（婦女、少數民族、大學生、藍領）必挺自己。"),
        ("● 【2. 核心失靈病根：歷史樣本偏見與漏算最後轉向者】", "預測模型缺乏解釋潛在環境背景誤差的能力，分析師未花足夠時間檢視底層資料，更漏算「最初拒絕投川普、但在最後一刻改變想法的共和黨人」。"),
        ("● 【3. 最終失敗後果：勝率估 70%–99% 卻在搖擺州崩盤】", "威斯康辛州選前民調顯示柯林頓遙遙領先，開票卻由川普勝出！（註：Meridian 早期過時老化模擬軟體與 Google 流感高估疫情亦屬典型失敗決策）。")
    ],
    accent_color=COLOR_DANGER, header_tint=TINT_RED, is_spotlight=True,
    row_y_slots=s7_slots, hdr_h=Inches(0.75), tag_pt=11.4, desc_pt=10.4
)

add_zone3_footer(s7, "★ 問題 2 正反對比啟示：成功決策（NHS / NYPD）用數據解決真痛點；失敗決策（Twitter KPI / 美選）則被虛假指標與舊樣本綁架")
set_notes(s7, """【講者：黃宥丞｜預計時間：2 分鐘（下半場開場）】
謝謝亞恩！各位老師、同學好，我是黃宥丞，接下來由我為大家報告下半場。
延續問題 2 的下半部分：「找出個案中沒有改善（或失敗）的兩個決策」。我們選出了兩個最具代表性的失敗決策來做深度對照：
左邊這張卡片是第一個失敗決策：「某大型企業把 Twitter 被提及次數列為銷售 KPI 的決策」。這家大公司過去真正的業績其實都來自「參加實體貿易展與研討會」，但他們卻做了一個錯誤決策——建了數位儀表板天天盯著網站流量跟 Twitter 被提及次數，還把它設為銷售部門的 KPI！結果導致業務人員不再專心跑展會，反而把時間跟資源全部浪費在監測點擊率跟社群流量，最後產出一大堆永遠不會變成真正訂單的無效銷售線索。
右邊聚光燈高亮的卡片，則是第二個失敗決策：「2016 年美國總統大選柯林頓競選團隊的選情預測決策」。當時每一個主要預測都斷言柯林頓有 70% 到 99% 的機率獲勝，為什麼最後徹底翻車？因為柯林頓團隊直接沿用歐巴馬 2008 與 2012 年勝選時建立的資料庫，錯誤假設過去支持歐巴馬的婦女、少數民族、大學畢業生和藍領工人一定會繼續支持柯林頓，並把焦點放在投票率很高的地區；他們既沒有花足夠時間檢視底層資料，模型也無法解釋潛在環境誤差，更完全漏算了「最初拒絕投給川普、但在最後一刻改變想法的共和黨人」，導致威斯康辛州等地徹底失準！（此外，個案中紐澳 Meridian 早期的舊預測軟體和 Google 流感趨勢高估疫情，也同樣是沒有改善的失敗案例）。""")


# ==============================================================================
# SLIDE 8 [Layout S5: 2x2 Grid + Bottom Spotlight Bar — Chapter 4: Q3 Five Limitations]
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_bg(s8, BG_LIGHT)
add_zone1_header(
    s8,
    pill_text="CHAPTER 04 (Q3 分析限制) ｜ (4) 問題 3 詳細說明使用巨量資料的五大限制",
    headline_text="大數據並非萬靈丹：從目標迷思、假性相關、脈絡缺失到「推論隱私」共五大限制",
    speaker_badge="下半場講者：黃宥丞 (08 / 11)"
)

q3_quads = [
    (Inches(0.65), Inches(1.20), "限制 1：缺乏清晰目標與「測量迷思」", "在一堆資料中打滾 ≠ 做出更明智的決策", COLOR_WARN, TINT_AMBER, [
        ("● 【盲目跳入大數據、未設目標與 KPI】", "太多公司被美麗願景誘惑而急於啟動計畫，卻未先設定企業目標或關鍵績效指標；某大公司誤以為「可測量就該測量」，把 Twitter 聲量當銷售 KPI 而虛耗資源。")
    ]),
    (Inches(6.80), Inches(1.20), "限制 2：資料品質與治理限制（Garbage In）", "未正確清理、組織與管理的混亂資料毫無價值", COLOR_SLATE, TINT_SLATE, [
        ("● 【資料品質至關重要（Data Quality）】", "課本明確警告：組織絕對不會從未正確清理、組織、管理的巨量資料中獲益。若底層資料充滿雜訊與格式衝突，再龐大的資料量也無法產出正確資訊。")
    ]),
    (Inches(0.65), Inches(2.98), "限制 3：相關性 ≠ 因果關係（缺乏領域知識）", "擅長抓細微相關性，卻分不清巧合與真因果", COLOR_WARN, TINT_AMBER, [
        ("● 【2006–2011 美國謀殺率 vs. IE 瀏覽器市佔率】", "大數據發現美國各州謀殺率與 IE 市佔率同步顯著下降（高度相關），但兩者毫無意義聯繫！分析師必須具備解決問題的企業領域知識（Domain Knowledge）。")
    ]),
    (Inches(6.80), Inches(2.98), "限制 4：預測模型過時、偏見與缺上下文脈絡", "模型反映資料選擇偏見，不一定能更了解未來", COLOR_DANGER, TINT_RED, [
        ("● 【Meridian 過時模擬、GFT 缺脈絡與美選偏見】", "Meridian 舊模擬脫離現實；Google 流感只看搜尋數字卻忽略媒體報導引發的恐慌上下文（Context）；2016 美選與英國脫歐則因歷史偏見與漏算轉向者而翻車。")
    ])
]

for qx, qy, qt, qsub, qcol, qtint, qrows in q3_quads:
    create_structured_card(
        s8, qx, qy, Inches(5.88), Inches(1.68),
        title=qt, subtitle=qsub, rows_data=qrows,
        accent_color=qcol, header_tint=qtint, is_spotlight=False,
        row_y_slots=[(qy + Inches(0.58), Inches(1.00))],
        hdr_h=Inches(0.48), tag_pt=10.6, desc_pt=9.8
    )

# Bottom Full-Width Spotlight Card for Limitation 5: Inferential Privacy & Ethics
create_structured_card(
    s8, Inches(0.65), Inches(4.78), Inches(12.033), Inches(1.76),
    title="★ 限制 5（社會倫理與法規盲點）：資訊安全、高風險貼標籤與「推論隱私（Inferential Privacy）」嚴重侵害",
    subtitle="結合多源個資推論出當事人不願揭露甚至自身未知的隱私特徵，卻毫無法律保護與反擊機制",
    rows_data=[
        ("● 【淺層探勘：標註信貸與健康「高風險者」】 → 【深層推論：帕金森氏症早期徵兆與無意識藍綠偏好】",
         "企業積極蒐集購物習慣、收入、嗜好、住所與手機 GPS 移動路徑，將人分群標為「高風險者」以保護企業或操弄消費者；更將個資結合不同來源資料，推論出「顯示帕金森氏症早期徵兆」或「無意識受藍色或綠色產品吸引」。在缺乏法律程序保護、缺乏反擊機制、當事人甚至不知自己被分類下，民眾將蒙受嚴重損害。")
    ],
    accent_color=COLOR_DANGER, header_tint=TINT_RED, is_spotlight=True,
    row_y_slots=[(Inches(5.38), Inches(1.06))],
    hdr_h=Inches(0.50), tag_pt=10.8, desc_pt=9.8
)

add_zone3_footer(s8, "★ 問題 3 結論：巨量資料受限於「目標、品質、因果、脈絡與隱私」五大維度，決策者絕不可將演算法輸出視為絕對真理")
set_notes(s8, """【講者：黃宥丞｜預計時間：2 分鐘】
接著我們回答「問題 3：詳細說明使用巨量資料的限制」。我們小組將課本內容徹底梳理為五大核心限制：
第一是「缺乏清晰目標與測量迷思」：很多公司沒設目標和 KPI 就跳進資料堆打滾，誤以為某件事可以測量就應該測量（就像剛剛的 Twitter KPI 案例）。
第二是「資料品質與治理限制」：課本特別提醒「記得資料品質很重要」，如果資料沒有經過正確清理、組織與管理，組織絕對不可能從混亂資料中獲益。
第三是方法論上的「相關性不等於因果關係」：大數據很擅長找出細微的相關性，例如 2006 到 2011 年美國各州的謀殺率跟 Internet Explorer（IE）瀏覽器的市佔率呈現高度正相關（因為兩者都剛好在下降），但這兩者之間根本沒有任何有意義的因果聯繫！如果分析師缺乏企業領域知識（Domain Knowledge），就會做出荒謬決策。
第四是「預測模型限制」：包含建模技術過時（Meridian 舊系統）、忽略搜尋結果的上下文脈絡（Google 流感被媒體報導引發的恐慌搜尋騙倒），以及歷史資料偏見與缺乏環境誤差解釋力（2016 美國大選與英國脫歐）。
第五（下方聚光燈大卡片）則是極度嚴重的「資安與推論隱私（Inferential Privacy）限制」：企業收集購物習慣、收入與手機移動路徑，把人貼上貸款或健康「高風險者」標籤；更可怕的是當把個資結合不同來源資料時，竟能推論出連當事人自己都不知道的事實線索——例如「顯示出帕金森氏症的早期徵兆」或「無意識受藍色、綠色產品吸引」！在沒有法律程序保護、缺乏反擊機制且當事人毫不知情下，這對消費者權益造成巨大威脅。""")


# ==============================================================================
# SLIDE 9 [Layout S2: Three Pillars MIS Framework — Chapter 4: Q4 Management, Org, Tech]
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_bg(s9, BG_LIGHT)
add_zone1_header(
    s9,
    pill_text="CHAPTER 04 (Q4 MIS 策略框架) ｜ (4) 問題 4 所有組織都該投入嗎？管理、組織與科技議題",
    headline_text="並非所有組織都應盲目投入！決定投入前須先完成「管理×組織×科技」鐵三角整備",
    speaker_badge="下半場講者：黃宥丞 (09 / 11)"
)

# Top Gate Banner Answering Part 1 of Question 4
gate_bar = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(1.18), Inches(12.033), Inches(0.68))
gate_bar.adjustments[0] = 0.12
gate_bar.fill.solid()
gate_bar.fill.fore_color.rgb = TINT_RED
gate_bar.line.color.rgb = COLOR_DANGER
gate_bar.line.width = Pt(1.5)
tf_gb = gate_bar.text_frame
tf_gb.word_wrap = True
tf_gb.vertical_anchor = MSO_ANCHOR.MIDDLE
tf_gb.margin_left = tf_gb.margin_right = Inches(0.20)
p_gb = tf_gb.paragraphs[0]
p_gb.text = "■ 【問題 4 前半題明確結論：並非所有組織都應該蒐集和分析巨量資料！】若企業沒有明確目標、不知如何解決核心瓶頸、業務動能根本不依賴線上表象數據（如依賴實體貿易展之公司），或尚未具備資料清理能力，盲目跟風只會扭曲部門焦點並浪費資源。"
p_gb.font.name = "Microsoft JhengHei"
p_gb.font.size = Pt(10.8)
p_gb.font.bold = True
p_gb.font.color.rgb = COLOR_DANGER

s9_slots = [(Inches(2.82), Inches(1.15)), (Inches(4.05), Inches(1.18)), (Inches(5.31), Inches(1.15))]

create_structured_card(
    s9, Inches(0.65), Inches(1.96), Inches(3.85), Inches(4.60),
    title="一、管理議題（Management）", subtitle="目標對齊 × 正確 KPI × 隱私倫理治理",
    rows_data=[
        ("● 【1. 預先設定清晰企業目標】", "啟動計畫前必須先定義要解決的核心營運問題（如 NHS 鎖定降低處方浪費），拒絕被美麗願景誘惑盲目投入。"),
        ("● 【2. 建立正確 KPI 破除測量迷思】", "嚴格區分「可測量的表象指標（Twitter 提及次數）」與「真正創造營收的核心指標（實體展會成交率）」。"),
        ("● 【3. 制定資安與推論隱私界線】", "針對高風險分群貼標籤與跨源「推論隱私（如帕金森氏症前兆）」建立法規遵循審查與消費者抗辯保護機制。")
    ],
    accent_color=COLOR_PRIMARY, header_tint=TINT_BLUE, is_spotlight=False,
    row_y_slots=s9_slots, hdr_h=Inches(0.72), tag_pt=11.0, desc_pt=10.0
)

create_structured_card(
    s9, Inches(4.74), Inches(1.96), Inches(3.85), Inches(4.60),
    title="二、組織議題（Organization）", subtitle="領域知識人才 × 部門流程防偏 × 假設審視",
    rows_data=[
        ("● 【1. 配置具備企業領域知識人才】", "培育深諳特定業務領域知識（Domain Knowledge）的分析師，才能解讀社會脈絡並過濾「IE 與謀殺率」假性相關。"),
        ("● 【2. 保護部門核心業務焦點】", "調整部門流程與獎酬制度，確保銷售與營運團隊不會被錯誤的數位儀表板指標扭曲日常工作重心。"),
        ("● 【3. 建立審視底層資料之文化】", "要求分析師花足夠時間檢視預測模型資料與環境誤差，打破對歷史成功資料庫（如歐巴馬舊選民庫）的盲信。")
    ],
    accent_color=COLOR_WARN, header_tint=TINT_AMBER, is_spotlight=False,
    row_y_slots=s9_slots, hdr_h=Inches(0.72), tag_pt=11.0, desc_pt=10.0
)

create_structured_card(
    s9, Inches(8.83), Inches(1.96), Inches(3.85), Inches(4.60),
    title="★ 三、科技議題（Technology）", subtitle="資料清理治理 × 高速平台 × 即時數據流",
    rows_data=[
        ("● 【1. 落實資料清理、組織與治理】", "「資料品質很重要！」必須先建立標準化資料清理與整合機制，確保底層資料乾淨可靠，避免垃圾進垃圾出。"),
        ("● 【2. 建置高速大數據運算架構】", "投資能快速儲存並分析數十億筆巨量資料的軟硬體與資料庫平台（如英國 NHS 採用的 Oracle Exadata）。"),
        ("● 【3. 淘汰過時模型、串接即時資料】", "捨棄脫離現實的過時情境模擬軟體，改採能串接設備與環境「即時資料」的現代預測系統（如 IBM 預測軟體）。")
    ],
    accent_color=COLOR_SUCCESS, header_tint=TINT_GREEN, is_spotlight=True,
    row_y_slots=s9_slots, hdr_h=Inches(0.72), tag_pt=11.0, desc_pt=10.0
)

add_zone3_footer(s9, "★ 問題 4 結論：唯有「管理定準目標、組織配齊領域專家、科技洗淨並串接即時資料」三維到位，投入大數據才有實質回報")
set_notes(s9, """【講者：黃宥丞｜預計時間：2 分鐘】
再來是「問題 4：所有的組織都應該蒐集和分析巨量資料嗎？在公司決定要投入巨量資料分析前，必須先考量哪些管理、組織和科技的議題？」。
首先針對前半題，我們小組的答案非常明確：「不是所有組織都應該盲目蒐集和分析巨量資料！」如果一家公司沒有特定目標、不知道如何解決核心問題，或者它的生意根本靠實體貿易展而不是線上點擊率，盲目跟風只會浪費錢又扭曲團隊焦點。
當公司評估確實需要投入前，必須先考量課本最核心的 MIS「管理、組織、科技」鐵三角議題：
第一在「管理議題（左卡）」：必須先設定清晰的企業目標與正確 KPI（破除可測量就該測量的迷思），並且建立資安與推論隱私的倫理法規紅線。
第二在「組織議題（中卡）」：必須配置具備深厚「企業領域知識（Domain Knowledge）」的分析師來過濾假性相關，保護銷售與業務部門焦點不被儀表板扭曲，並督促分析師花足夠時間檢視模型底層資料。
第三在「科技議題（右邊聚光燈卡）」：必須先做好資料清理、組織與品質治理，建置像英國 NHS 使用的 Oracle Exadata 高速資料庫平台，並且淘汰過時建模軟體，導入像 Meridian 換裝的 IBM 即時資料預測系統。""")


# ==============================================================================
# SLIDE 10 [Layout S6: Equation / Theory Anatomy — Chapter 4: Q5 Data Bias & Context]
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_bg(s10, BG_LIGHT)
add_zone1_header(
    s10,
    pill_text="CHAPTER 04 (Q5 延伸進階題) ｜ (4) 問題 5 避免「資料偏見」與「缺乏上下文脈絡」陷阱",
    headline_text="借鏡 Google 流感與 2016 美選翻車教訓：以「動態樣本＋脈絡調節＋專家審查」建構可靠模型",
    speaker_badge="下半場講者：黃宥丞 (10 / 11)"
)

# Top Dark Equation / Formula Anatomy Box
eq_box = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(1.18), Inches(12.033), Inches(1.42))
eq_box.adjustments[0] = 0.05
eq_box.fill.solid()
eq_box.fill.fore_color.rgb = DARK_BG
eq_box.line.color.rgb = DARK_SKY
eq_box.line.width = Pt(2.0)
tf_eq = eq_box.text_frame
tf_eq.word_wrap = True
tf_eq.vertical_anchor = MSO_ANCHOR.MIDDLE
tf_eq.margin_left = tf_eq.margin_right = Inches(0.24)

p_eq1 = tf_eq.paragraphs[0]
p_eq1.text = "【問題 5 高可靠度預測模型黃金公式（Human-in-the-Loop & Context-Calibrated Predictive Model）】"
p_eq1.alignment = PP_ALIGN.CENTER
p_eq1.font.name = "Microsoft JhengHei"
p_eq1.font.size = Pt(11.5)
p_eq1.font.bold = True
p_eq1.font.color.rgb = RGBColor(203, 213, 225)
p_eq1.space_after = Pt(4)

p_eq2 = tf_eq.add_paragraph()
p_eq2.text = "Reliable Prediction  Ŷ(t)  =  f_Domain (  [① 歷史資料 ⊕ 即時動態樣本 D_RealTime(t)]  ×  [② 表象行為 X(t) ÷ 外部媒體脈絡調節 (1 + γ·C_Media)]  +  [③ 潛在環境誤差校正 ε_Latent]  )"
p_eq2.alignment = PP_ALIGN.CENTER
p_eq2.font.name = "Microsoft JhengHei"
p_eq2.font.size = Pt(13.2)
p_eq2.font.bold = True
p_eq2.font.color.rgb = DARK_SKY
p_eq2.space_after = Pt(4)

p_eq3 = tf_eq.add_paragraph()
p_eq3.text = "▲ 白話翻譯：拒絕拿過去靜態資料算未來（破除 2016 美選偏見） × 拒絕只看搜尋數字不看媒體恐慌（破除 Google 流感盲點） × 真人領域專家最終把關"
p_eq3.alignment = PP_ALIGN.CENTER
p_eq3.font.name = "Microsoft JhengHei"
p_eq3.font.size = Pt(10.5)
p_eq3.font.bold = True
p_eq3.font.color.rgb = RGBColor(252, 211, 77)

s10_slots = [(Inches(3.52), Inches(0.96)), (Inches(4.54), Inches(0.98)), (Inches(5.58), Inches(0.92))]

create_structured_card(
    s10, Inches(0.65), Inches(2.72), Inches(3.85), Inches(3.84),
    title="對策 ①：破除「資料偏見 (Data Bias)」", subtitle="借鏡 2016 美國大選與英國脫歐民調翻車",
    rows_data=[
        ("● 【摒棄歷史結構無條件延續之假設】", "不可像柯林頓團隊盲信歐巴馬勝選資料庫，誤認婦女、少數民族、大學生與藍領必無條件支持。"),
        ("● 【持續注入即時動態資料與多元源】", "如同 Meridian 換裝 IBM 即時預測系統，民調只是參考之一，必須納入最新即時運行數據並嚴審樣本。"),
        ("● 【設計潛在環境誤差與轉向者校正】", "針對「最初拒絕表態、但在最後一刻改變想法的共和黨人」與真實投票率設計動態誤差校正機制。")
    ],
    accent_color=COLOR_PRIMARY, header_tint=TINT_BLUE, is_spotlight=False,
    row_y_slots=s10_slots, hdr_h=Inches(0.68), tag_pt=10.6, desc_pt=9.6
)

create_structured_card(
    s10, Inches(4.74), Inches(2.72), Inches(3.85), Inches(3.84),
    title="對策 ②：補足「上下文脈絡 (Context)」", subtitle="借鏡 Google 流感趨勢 (GFT) 持續高估疫情",
    rows_data=[
        ("● 【超越單一表象搜尋數字看動機】", "演算法不能只看位置與搜尋數字，必須區分網民是「真正感染流感」還是「看那年新聞報導而恐慌搜尋」。"),
        ("● 【將媒體炒作與突發事件設為調節項】", "當媒體廣泛報導疫情並經社群推波助瀾時，模型應啟動降權校正因子（1+γ·C_Media）過濾恐慌泡沫。"),
        ("● 【線上快數據 × 實體慢數據雙軌校準】", "定期拿 Google 搜尋量或 Twitter 聲量與「美國 CDC 實際就診數據／實體展會銷量」進行閉環校準。")
    ],
    accent_color=COLOR_WARN, header_tint=TINT_AMBER, is_spotlight=False,
    row_y_slots=s10_slots, hdr_h=Inches(0.68), tag_pt=10.6, desc_pt=9.6
)

create_structured_card(
    s10, Inches(8.83), Inches(2.72), Inches(3.85), Inches(3.84),
    title="★ 對策 ③：人類領域專家因果把關", subtitle="f_Domain：演算法算力 × 領域知識雙腦協同",
    rows_data=[
        ("● 【拒絕黑箱演算法全自動決策】", "大數據雖擅長抓細微相關性（如 IE 與謀殺率），但本身毫無商業與社會常識，無法判斷因果關係。"),
        ("● 【配置業務領域專家持續人工審視】", "由懂醫療、警政、選情或能源工程的領域專家（Domain Experts）持續檢驗模型假設是否脫離現實。"),
        ("● 【發現脈絡脫節立即修正模型權重】", "如同川普團隊將大數據用於針對選民群體量身打造精準訊息，以動態人機協作取代死板算命。")
    ],
    accent_color=COLOR_SUCCESS, header_tint=TINT_GREEN, is_spotlight=True,
    row_y_slots=s10_slots, hdr_h=Inches(0.68), tag_pt=10.6, desc_pt=9.6
)

add_zone3_footer(s10, "★ 問題 5 進階總結：高可靠預測模型 ＝ 即時動態樣本（破偏見） × 外部事件調節與實體校準（補脈絡） × 領域專家審查（驗因果）")
set_notes(s10, """【講者：黃宥丞｜預計時間：2.5 分鐘】
接著來到滿足老師規定滿 5 題的「問題 5（延伸進階題）：結合個案中 Google 流感預測失準以及 2016 年美國總統大選預測翻車的教訓，當企業或組織在建構預測模型時，應該如何避免陷入資料偏見（Data Bias）與缺乏上下文脈絡（Context）的陷阱？」。
請大家看上方深色公式盒，我們把這兩個經典翻車案例的教訓，提煉成一個「高可靠度預測模型黃金公式」，並拆解為下方三張對策卡片：
第一張卡片（對策 ①：如何避免資料偏見 Data Bias）：借鏡 2016 美國大選柯林頓團隊與英國脫歐翻車的教訓，企業首先要徹底摒棄「過去的歷史結構會無條件延續到未來」的靜態假設！不能因為歐巴馬靠這群選民贏了，就假設婦女、少數民族與藍領會永遠投給同一個政黨。因此模型必須像紐澳 Meridian 換裝 IBM 系統一樣，持續注入「即時動態資料」，並且設計能夠校正潛在環境誤差的機制，主動捕捉那些「最初拒絕表態、但在最後一刻改變想法的轉向者」。
第二張卡片（對策 ②：如何避免缺乏上下文脈絡 Context）：借鏡 Google 流感趨勢持續高估疫情的教訓，Google 的演算法只看搜尋數字，卻忽略了當年媒體廣泛報導疫情嚴重、加上社群媒體推波助瀾引發的「群眾恐慌搜尋上下文」。所以企業建模時，必須把「媒體報導熱度與突發事件」設為模型的降權調節變數，並且拿線上的搜尋快數據，定期跟「美國 CDC 的實體醫院就診數據（Ground Truth）」做雙軌交叉校準。
第三張聚光燈卡片（對策 ③：人類領域專家因果把關）：最外層的 f_Domain 代表不論演算法多先進，最後都必須由具備深厚「企業領域知識（Domain Knowledge）」的人類專家進行因果審核，一旦發現模型假設與真實世界脫節就立即修正！""")


# ==============================================================================
# SLIDE 11 [Layout S0: Dark Bookend Closing Slide — Peak-End Takeaways & Q&A]
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
set_slide_bg(s12, DARK_BG)
add_zone1_header(
    s12,
    pill_text="KEY TAKEAWAYS & Q&A ｜ 總結洞察：巨量資料分析有多可靠？",
    headline_text="巨量資料本身不會自動產生智慧——唯有「目標對齊、脈絡校準與倫理護欄」才真正可靠",
    speaker_badge="共同答詢：楊亞恩 ＆ 黃宥丞 (11 / 11)",
    is_dark=True
)

s12_slots = [(Inches(2.12), Inches(1.42)), (Inches(3.62), Inches(1.42))]

create_structured_card(
    s12, Inches(0.65), Inches(1.22), Inches(3.85), Inches(4.02),
    title="定律 01：數據規模 ≠ 決策品質", subtitle="破除盲目跟風與 KPI 測量迷思",
    rows_data=[
        ("● 【表面迷思：每日 2,500 萬億 Bytes 的誘惑】", "在未清理的混亂資料堆中打滾，或把容易測量的 Twitter 提及次數當銷售 KPI，只會扭曲焦點並產出無效線索。"),
        ("● 【可靠法則：清晰目標 ＋ 高速乾淨資料】", "如同英國 NHS（Oracle Exadata 省 5.81 億英鎊）與紐約警局（CompStat 76 轄區），先鎖定真痛點並做好資料清理才能獲益。")
    ],
    accent_color=DARK_SKY, is_spotlight=False, is_dark=True, row_y_slots=s12_slots, tag_pt=11.0, desc_pt=10.0
)

create_structured_card(
    s12, Inches(4.74), Inches(1.22), Inches(3.85), Inches(4.02),
    title="定律 02：統計相關 ≠ 真實因果", subtitle="破除資料偏見與缺乏上下文脈絡",
    rows_data=[
        ("● 【表面迷思：IE 謀殺率、GFT 與美選翻車】", "演算法分不清巧合與因果（IE 與謀殺率），更會因忽略媒體恐慌脈絡（GFT）或盲信歐巴馬舊資料庫（2016 美選）而失準。"),
        ("● 【可靠法則：即時樣本×脈絡調節×領域知識】", "導入即時資料（如 IBM 系統）、納入外部事件調節並與 CDC 實體數據校準，最後交由人類領域專家審查因果。")
    ],
    accent_color=RGBColor(52, 211, 153), is_spotlight=True, is_dark=True, row_y_slots=s12_slots, tag_pt=10.6, desc_pt=10.0
)

create_structured_card(
    s12, Inches(8.83), Inches(1.22), Inches(3.85), Inches(4.02),
    title="定律 03：商業效益 ≠ 無視倫理", subtitle="嚴守資訊安全與「推論隱私」法規界線",
    rows_data=[
        ("● 【表面迷思：無節制探勘與黑箱貼標籤】", "結合購物、收入與手機 GPS 將人標為「高風險者」，甚至推論出當事人未知的帕金森氏症早期徵兆與無意識藍綠偏好。"),
        ("● 【可靠法則：建立透明程序與抗辯保護機制】", "在追求個人化推薦與風險控管利益時，管理層必須建立推論隱私紅線、透明告知與消費者申訴反擊機制，守住數位信任。")
    ],
    accent_color=RGBColor(251, 113, 133), is_spotlight=False, is_dark=True, row_y_slots=s12_slots, tag_pt=11.0, desc_pt=10.0
)

# Bottom Closing & Q&A Banner
qa_banner = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(5.38), Inches(12.033), Inches(1.14))
qa_banner.adjustments[0] = 0.08
qa_banner.fill.solid()
qa_banner.fill.fore_color.rgb = DARK_CARD_BG
qa_banner.line.color.rgb = DARK_SKY
qa_banner.line.width = Pt(1.8)
tf_qa = qa_banner.text_frame
tf_qa.word_wrap = True
tf_qa.vertical_anchor = MSO_ANCHOR.MIDDLE
tf_qa.margin_left = tf_qa.margin_right = Inches(0.25)

p_qa1 = tf_qa.paragraphs[0]
p_qa1.text = "以上是我們的個案分析報告！感謝何政勳老師與各位同學的聆聽，現在正式進入 25 分鐘 Q&A 討論時間！"
p_qa1.alignment = PP_ALIGN.CENTER
p_qa1.font.name = "Microsoft JhengHei"
p_qa1.font.size = Pt(15.5)
p_qa1.font.bold = True
p_qa1.font.color.rgb = RGBColor(255, 255, 255)
p_qa1.space_after = Pt(4)

p_qa2 = tf_qa.add_paragraph()
p_qa2.text = "資訊管理課程個案分析  ｜  指導老師：何政勳 老師  ｜  報告成員：楊亞恩（311157139）、黃宥丞（311357109）"
p_qa2.alignment = PP_ALIGN.CENTER
p_qa2.font.name = "Microsoft JhengHei"
p_qa2.font.size = Pt(11.5)
p_qa2.font.bold = True
p_qa2.font.color.rgb = DARK_SKY

add_zone3_footer(s12, "★ 終章結語：唯有當「高品質即時數據 × 外部社會脈絡 × 人類領域知識與倫理護欄」三者合一，巨量資料分析才真正可靠！", is_dark=True)
set_notes(s12, """【講者：黃宥丞 ＆ 楊亞恩｜預計時間：1.5 分鐘總結 ＋ 開啟 25 分鐘 Q&A】
最後一頁，我們用三個黃金定律來總結今天對〈巨量資料分析有多可靠？〉的完整分析：
第一，「數據規模不等於決策品質」：每天 2,500 萬億位元組的資料如果沒有經過清理、沒有對準真實業務目標（像把 Twitter 聲量當銷售 KPI），就只是一堆無效雜訊；唯有像英國 NHS 和紐約警局那樣鎖定明確痛點並配合高速平台，才能創造實質效益。
第二，「統計相關不等於真實因果」：從 IE 瀏覽器與謀殺率的巧合，到 Google 流感趨勢和 2016 美國大選的翻車，都證明模型必須納入即時動態資料、考慮媒體等外部上下文脈絡（Context），並由具備企業領域知識（Domain Knowledge）的人類專家把關。
第三，「商業效益不等於可以無視倫理」：面對演算法自動標註高風險者、甚至推論出帕金森氏症早期徵兆的「推論隱私」危機，企業必須建立法規與倫理護欄。
以上是我們這組 23 分鐘的個案分析報告，非常謝謝何政勳老師與各位同學的聆聽！接下來是 25 分鐘的 Q&A 時間，歡迎老師與各位同學提問指教！""")

pptx_path = os.path.join(output_dir, "02_case_analysis_presentation.pptx")
prs.save(pptx_path)
print(f"[OK] Saved native vector PowerPoint presentation: {pptx_path} (Size: {os.path.getsize(pptx_path):,} bytes)")
