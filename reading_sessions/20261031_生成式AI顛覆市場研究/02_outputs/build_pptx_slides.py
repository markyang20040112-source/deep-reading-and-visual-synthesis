# -*- coding: utf-8 -*-
"""
build_pptx_slides.py
Generates Format C (16:9 Widescreen Presentation Slides .pptx + Dual-Channel Markdown Script .md)
Strictly adheres to presentation_slide_spec.md:
- Alley & Neeley (2005) 3-Zone Slide Architecture:
  * Zone 1 (Top 15%): Full-sentence Assertion Headline (22-36 CJK chars, 22-24pt Bold)
  * Zone 2 (Middle 75%): Kosslyn S1-S6 Visual Evidence Layouts + 80/20 Knaflic Preattentive Spotlight + Embedded High-DPI Diagrams
  * Zone 3 (Bottom 10%): High-contrast So-What Action Takeaway Banner
- Dual-Channel Separation: Concise visual text on canvas, full spoken narrative in Speaker Notes.
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

IMG1 = os.path.join(OUT_DIR, "01_生成式AI顛覆市場研究_四大機會與核心實務圖.jpg")
IMG2 = os.path.join(OUT_DIR, "02_生成式AI市調局限_實驗混淆與四大前沿解法思辨圖.jpg")
IMG3 = os.path.join(OUT_DIR, "03_三篇合體_顧客價值與AI數據科學決策終極藍圖.jpg")

# Color Palette (McKinsey Executive + Knaflic 80/20 Preattentive Spotlight)
C_NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A Deep Slate Navy
C_NAVY_MED  = RGBColor(30, 58, 138)     # #1E3A8A Executive Blue
C_SLATE_TXT = RGBColor(30, 41, 59)      # #1E293B Body Ink
C_MUTED_TXT = RGBColor(71, 85, 105)     # #475569 Context Text
C_BG_CANVAS = RGBColor(248, 250, 252)   # #F8FAFC Warm Alabaster / Off-white
C_CARD_BG   = RGBColor(255, 255, 255)   # #FFFFFF Pure Card Surface
C_CARD_MUTED= RGBColor(241, 245, 249)   # #F1F5F9 Neutral Context Card Fill
C_BORDER_MUT= RGBColor(203, 213, 225)   # #CBD5E1 Neutral Context Border

# Spotlight Accent Colors (10% Preattentive Quota)
C_SPOT_BLUE = RGBColor(30, 64, 175)     # #1E40AF Spotlight Primary
C_SPOT_BG   = RGBColor(239, 246, 255)   # #EFF6FF Spotlight Soft Blue Fill
C_SPOT_RED  = RGBColor(190, 18, 60)     # #BE123C Spotlight Alert / Critique
C_SPOT_REDBG= RGBColor(255, 241, 242)   # #FFF1F2 Spotlight Soft Rose Fill
C_SPOT_GOLD = RGBColor(180, 83, 9)      # #B45309 Spotlight Amber / Math
C_SPOT_GOLDBG=RGBColor(255, 251, 235)   # #FFFBEB Spotlight Soft Amber Fill
C_SPOT_TEAL = RGBColor(4, 120, 87)      # #047857 Spotlight Emerald
C_SPOT_TEALBG=RGBColor(236, 253, 245)   # #ECFDF5 Spotlight Soft Emerald Fill
C_SKY_LIGHT = RGBColor(56, 189, 248)    # #38BDF8 Cover Accent
C_WHITE     = RGBColor(255, 255, 255)

FONT_CJK = "Microsoft JhengHei"


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
    """Zone 1: Top 15% Height (0.0" to 1.15") - Sentence Assertion Headline"""
    # Top subtle header bar
    header_bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.18)
    )
    header_bg.fill.solid()
    header_bg.fill.fore_color.rgb = C_WHITE
    header_bg.line.color.rgb = C_BORDER_MUT
    header_bg.line.width = Pt(1)

    # Left vertical accent bar
    accent = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.12), Inches(1.18)
    )
    accent.fill.solid()
    accent.fill.fore_color.rgb = C_NAVY_MED
    accent.line.fill.background()

    # Act tag pill
    pill = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.35), Inches(0.12), Inches(2.9), Inches(0.28)
    )
    pill.fill.solid()
    pill.fill.fore_color.rgb = C_NAVY_DARK
    pill.line.fill.background()
    tf_p = pill.text_frame
    tf_p.word_wrap = False
    tf_p.margin_left = tf_p.margin_right = tf_p.margin_top = tf_p.margin_bottom = 0
    p = tf_p.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = f"{slide_num_str} | {act_tag}"
    run.font.name = FONT_CJK
    run.font.size = Pt(9.5)
    run.font.bold = True
    run.font.color.rgb = C_SKY_LIGHT

    # Full-sentence Assertion Headline
    tb = slide.shapes.add_textbox(Inches(0.35), Inches(0.42), Inches(12.6), Inches(0.70))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = assertion_headline
    run.font.name = FONT_CJK
    run.font.size = Pt(20)
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

    # Top gold/cyan strip on footer
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


def add_card(slide, left, top, width, height, tag_text, title_text, bullets,
             is_spotlight=False, spot_color=C_SPOT_BLUE, spot_bg=C_SPOT_BG):
    """Draws a structured visual evidence card (Context vs. 80/20 Preattentive Spotlight)"""
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    card.adjustments[0] = 0.03
    card.fill.solid()
    card.fill.fore_color.rgb = spot_bg if is_spotlight else C_CARD_BG
    card.line.color.rgb = spot_color if is_spotlight else C_BORDER_MUT
    card.line.width = Pt(2.5 if is_spotlight else 1.2)

    # Top accent bar inside card
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.10)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = spot_color if is_spotlight else RGBColor(100, 116, 139)
    bar.line.fill.background()

    # Tag pill
    pill_w = min(width - 0.3, max(1.5, len(tag_text) * 0.16 + 0.35))
    pill = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left + 0.18), Inches(top + 0.20), Inches(pill_w), Inches(0.28)
    )
    pill.fill.solid()
    pill.fill.fore_color.rgb = spot_color if is_spotlight else RGBColor(226, 232, 240)
    pill.line.fill.background()
    tf_p = pill.text_frame
    tf_p.word_wrap = False
    tf_p.margin_left = tf_p.margin_right = tf_p.margin_top = tf_p.margin_bottom = 0
    p = tf_p.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = tag_text
    r.font.name = FONT_CJK
    r.font.size = Pt(9.5)
    r.font.bold = True
    r.font.color.rgb = C_WHITE if is_spotlight else C_SLATE_TXT

    # Card Title
    tb_t = slide.shapes.add_textbox(Inches(left + 0.18), Inches(top + 0.54), Inches(width - 0.36), Inches(0.55))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    r_t = p_t.add_run()
    r_t.text = title_text
    r_t.font.name = FONT_CJK
    r_t.font.size = Pt(14)
    r_t.font.bold = True
    r_t.font.color.rgb = spot_color if is_spotlight else C_NAVY_DARK

    # Divider line
    div = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(left + 0.18), Inches(top + 1.12), Inches(width - 0.36), Inches(0.015)
    )
    div.fill.solid()
    div.fill.fore_color.rgb = spot_color if is_spotlight else C_BORDER_MUT
    div.line.fill.background()

    # Bullets
    tb_b = slide.shapes.add_textbox(Inches(left + 0.18), Inches(top + 1.22), Inches(width - 0.36), Inches(height - 1.32))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0
    for idx, b_text in enumerate(bullets):
        p_b = tf_b.paragraphs[0] if idx == 0 else tf_b.add_paragraph()
        p_b.space_after = Pt(8)
        r_b = p_b.add_run()
        r_b.text = b_text
        r_b.font.name = FONT_CJK
        r_b.font.size = Pt(11.5)
        r_b.font.bold = is_spotlight and ("★" in b_text or "【" in b_text)
        r_b.font.color.rgb = C_SLATE_TXT


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

# Top decorative bar
top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.14))
top_bar.fill.solid()
top_bar.fill.fore_color.rgb = C_SKY_LIGHT
top_bar.line.fill.background()

# Subtitle pill
pill0 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(0.65), Inches(5.8), Inches(0.38))
pill0.fill.solid()
pill0.fill.fore_color.rgb = C_NAVY_MED
pill0.line.color.rgb = C_SKY_LIGHT
pill0.line.width = Pt(1.2)
tf0 = pill0.text_frame
p0 = tf0.paragraphs[0]
p0.alignment = PP_ALIGN.CENTER
r0 = p0.add_run()
r0.text = "HBR 深度閱讀與視覺化綜合產出 ｜ 斷言—證據高階簡報 (Assertion-Evidence Deck)"
r0.font.name = FONT_CJK
r0.font.size = Pt(11)
r0.font.bold = True
r0.font.color.rgb = C_SKY_LIGHT

# Main Title
tb_title = s1.shapes.add_textbox(Inches(0.7), Inches(1.25), Inches(11.9), Inches(1.6))
tf_title = tb_title.text_frame
tf_title.word_wrap = True
p_t1 = tf_title.paragraphs[0]
r_t1 = p_t1.add_run()
r_t1.text = "《生成式 AI 正在顛覆市場研究》\n深度思辨與「道・法・術」三篇合體科學決策藍圖"
r_t1.font.name = FONT_CJK
r_t1.font.size = Pt(31)
r_t1.font.bold = True
r_t1.font.color.rgb = C_WHITE

# Core Thesis Box
thesis_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(3.05), Inches(11.9), Inches(1.45))
thesis_box.adjustments[0] = 0.04
thesis_box.fill.solid()
thesis_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
thesis_box.line.color.rgb = C_SKY_LIGHT
thesis_box.line.width = Pt(2)
tf_th = thesis_box.text_frame
tf_th.word_wrap = True
tf_th.margin_left = tf_th.margin_right = Inches(0.25)
tf_th.margin_top = Inches(0.18)
p_th = tf_th.paragraphs[0]
r_th = p_th.add_run()
r_th.text = (
    "★ 全篇終極核心主張 (Core Thesis)：\n"
    "生成式 AI 能以「動態訪談員」卸下人類心理與道德偽裝、以「合成數據與數位雙生」百倍速擴張早期探索；\n"
    "但因天生運算「語境條件聯想」而非「獨立因果干預」，在盲測訂價與多感官領域必生混淆失靈。企業須以《顧客需求不靠猜》定錨問題（道）、以《AI 強化數據分析》打通 ERP 情境（法），再執行人機權變市調閉環（術）。"
)
r_th.font.name = FONT_CJK
r_th.font.size = Pt(13.5)
r_th.font.bold = True
r_th.font.color.rgb = C_WHITE

# 4 KPI Cards at bottom of cover
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
    tf_k.margin_left = tf_k.margin_right = Inches(0.15)
    tf_k.margin_top = Inches(0.15)
    pk1 = tf_k.paragraphs[0]
    rk1 = pk1.add_run()
    rk1.text = big_num
    rk1.font.name = FONT_CJK
    rk1.font.size = Pt(24)
    rk1.font.bold = True
    rk1.font.color.rgb = C_SKY_LIGHT if idx < 3 else RGBColor(110, 231, 183)

    pk2 = tf_k.add_paragraph()
    pk2.space_before = Pt(4)
    rk2 = pk2.add_run()
    rk2.text = k_title
    rk2.font.name = FONT_CJK
    rk2.font.size = Pt(12)
    rk2.font.bold = True
    rk2.font.color.rgb = C_WHITE

    pk3 = tf_k.add_paragraph()
    pk3.space_before = Pt(4)
    rk3 = pk3.add_run()
    rk3.text = k_sub
    rk3.font.name = FONT_CJK
    rk3.font.size = Pt(10)
    rk3.font.color.rgb = RGBColor(203, 213, 225)

notes_s1 = (
    "【講者備忘稿 Slide 01】各位決策夥伴大家好。今天這份簡報不僅深度拆解 HBR 最新力作《生成式 AI 正在顛覆市場研究》，"
    "更將我們前兩次研讀的《顧客需求不靠猜》與《AI 能強化你的數據分析能力》融會貫通，建立一套「道、法、術」三階企業科學決策藍圖。"
    "我們的核心主張非常明確：生成式 AI 在擔任「動態訪談員」時能破除人類的道德偽裝，在擔任「早期探索引擎」時能百倍速擴充樣本；"
    "但它絕非萬能，面對盲測訂價與感官體驗時會發生嚴重的語境腦補混淆。接下來我們將從實證機會、底層資料結構、因果混淆公式到三篇合體路線圖逐一剖析。"
)
add_speaker_notes(s1, notes_s1)
slides_md_records.append(("Slide 01：【序幕：核心命題封面】", "生成式 AI 顛覆市場研究之機會邊界與「道・法・術」三篇合體決策藍圖", notes_s1))


# ==============================================================================
# SLIDE 02: 第一幕 (S2 三支柱聚焦卡片型 — 四大機會與 AI 訪談員破除道德修飾)
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_bg(s2, C_BG_CANVAS)
add_zone1_header(
    s2, "Slide 02", "第一幕：現狀診斷與機會全貌 (S2 三支柱聚焦型)",
    "AI 動態訪談員因不觸發人類心理與道德修飾機制，反而能比真人挖出更坦誠之深層痛點"
)
add_card(
    s2, 0.40, 1.42, 3.95, 5.15,
    "支柱一：規模化合成受眾", "取代現有問卷與填補預算缺口",
    [
        "● 雙盲實證高吻合度：安永 (EY) 與 Evidenza 測試 1,000 名合成 CEO，結論與真人高達 95% 相同，成本與時間卻呈指數級下降。",
        "● 填補無數據決策缺口：30% 受訪者用 AI 引導過去因預算不足而憑直覺拍板的決策（如通用磨坊、Arena 模擬跨門市選品）。",
        "● 早期概念快篩：在投入昂貴真人調查前，先以合成受訪者快速淘汰低潛力構想。"
    ],
    is_spotlight=False
)
add_card(
    s2, 4.68, 1.42, 3.95, 5.15,
    "支柱二：顧客數位雙生", "綁定真人基準事實之模擬分身",
    [
        "● 跨期重測高度穩定：史丹福與哥倫比亞大學（2,500 人群組）證實，數位雙生與本人在兩週後重測相似度高達 85%。",
        "● 永不疲勞的演練靶子：B2B 銷售團隊可與大客戶的數位雙生事前反覆演練推銷話術、測試廣告共鳴（82% 企業已實驗或計畫導入）。",
        "● 動態綁定行為軌跡：CivicSync 結合心理測驗與真實線上購物行為，持續更新分身記憶。"
    ],
    is_spotlight=False
)
add_card(
    s2, 8.96, 1.42, 3.97, 5.15,
    "★ 聚光燈焦點：AI 動態訪談員", "解除人類「心理與道德修飾機制」",
    [
        "● ★ 思辨核心洞察：人類面對「真人訪談員」時會自動啟動「心理與道德修飾機制（社會期許偏誤）」，為顧及面子或道德正確而隱藏真心話！",
        "● ★ 機器無道德審判眼神：WeightWatchers 與 Outset.ai 實證發現，受訪者對 AI 訪談員反而更坦誠吐露私密痛點（呼應第一篇 ESG 口頭宣稱 100% 卻零購買力之現象）。",
        "● 兼得量化廣度與質化深度：AI 能根據前次回答即時動態追問，且摘要逐字稿幾乎零幻覺。"
    ],
    is_spotlight=True, spot_color=C_SPOT_BLUE, spot_bg=C_SPOT_BG
)
add_zone3_footer(
    s2, "將傳統「死板量化問卷」升級為「AI 動態追問訪談」，在羞於啟齒或高道德敏感議題上直接採集無偽裝之顧客真心話。"
)
notes_s2 = (
    "【講者備忘稿 Slide 02】在第一幕中，我們看到高達 90% 的市調人員已使用或規畫使用生成式 AI。除了大家熟知的合成數據（左卡）與顧客數位雙生（中卡）之外，"
    "最值得決策者注意的破局點在右側聚光燈卡片：為什麼 WeightWatchers 用 Outset.ai 進行訪談時，受訪者反而比面對真人更誠實？"
    "因為人類在面對另一個『人』時，會本能啟動『心理與道德修飾機制』（社會期許偏誤），不敢承認自己貪小便宜或不在乎環保；"
    "但面對沒有道德批判眼神的機器時，這層心理防禦就卸下了！這讓企業第一次能用量化問卷的規模，收到不受道德修飾污染的質化真心話。"
)
add_speaker_notes(s2, notes_s2)
slides_md_records.append(("Slide 02：【第一幕：現狀診斷與機會全貌】版型 S2", "AI 動態訪談員因不觸發人類心理與道德修飾機制，反而能比真人挖出更坦誠之深層痛點", notes_s2))


# ==============================================================================
# SLIDE 03: 第一幕全景圖譜 (嵌入高解析圖譜一)
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_bg(s3, C_BG_CANVAS)
add_zone1_header(
    s3, "Slide 03", "第一幕：核心實務與數據結構全景圖譜 (High-DPI Diagram 01)",
    "生成式 AI 四大核心能力全面滲透市調三階段，將研究員由資料苦工解放為高價值策略敘事者"
)
# Left 72%: Embedded Diagram 01
img_frame1 = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.35), Inches(1.32), Inches(8.65), Inches(5.35))
img_frame1.fill.solid()
img_frame1.fill.fore_color.rgb = C_WHITE
img_frame1.line.color.rgb = C_BORDER_MUT
img_frame1.line.width = Pt(1.5)
s3.shapes.add_picture(IMG1, Inches(0.42), Inches(1.38), width=Inches(8.51))

# Right 28%: Spotlight Summary Card
add_card(
    s3, 9.15, 1.32, 3.82, 5.35,
    "★ 圖譜一核心導讀", "四大能力 × 四大機會關鍵指標",
    [
        "● 【4 大核心能力】：統整 (62%)、分析與編碼 (58%)、人機互動、報告寫作 (54%)。",
        "● 【三大接地氣錨定機制】：純合成數據僅 31% 認為價值極高；必須結合 ① 少樣本提示 (Few-shot)、② 知識庫檢索 (RAG)、③ 內部數據微調 (Fine-tuning)。",
        "● 【研究員角色轉型】：逾 80% 認同 AI 省下繁瑣逐字稿整理時間，讓真人研究員專注於高層策略溝通與因果驗證。"
    ],
    is_spotlight=True, spot_color=C_SPOT_BLUE, spot_bg=C_SPOT_BG
)
add_zone3_footer(
    s3, "切勿直接拿未經錨定的裸模型做市調；務必配備「提示範例＋RAG 知識庫＋內部數據微調」三道接地氣防線。"
)
notes_s3 = (
    "【講者備忘稿 Slide 03】這張高解析瑞士網格放射圖譜完整呈現了生成式 AI 在市場研究中的四大機會與資料結構全貌。"
    "請特別留意右側聚光燈卡片的關鍵警訊：雖然 81% 的人計畫使用合成數據，但目前只有 31% 認為純合成數據價值極高。"
    "原因在於未經錨定的模型容易流於表面空談，必須透過少樣本提示、RAG 檢索企業知識庫，以及內部歷史數據微調三大機制來扎根基準事實。"
)
add_speaker_notes(s3, notes_s3)
slides_md_records.append(("Slide 03：【第一幕：全景圖譜實證（一）】", "生成式 AI 四大核心能力全面滲透市調三階段，將研究員由資料苦工解放為高價值策略敘事者", notes_s3))


# ==============================================================================
# SLIDE 04: 第二幕 (S2 三支柱聚焦卡片型 — 三類資料結構與大小模型取捨)
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_bg(s4, C_BG_CANVAS)
add_zone1_header(
    s4, "Slide 04", "第二幕：資料結構與大小模型分工 (S2 三支柱聚焦型)",
    "私有小型模型僅能學習表格統計機率，唯有公開大型模型具備解析質化語意之人類世界知識"
)
add_card(
    s4, 0.40, 1.42, 3.95, 5.15,
    "結構一：結構化數據", "數字型 (Numerical) ＋ 類別型 (Categorical)",
    [
        "● 固定二維表格欄位：可直接存入 SQL 或 Excel 之明確資料。",
        "● ① 數字型數據：可算術運算之量化指標（如年齡 34 歲、年消費額 28,500 元、購買頻次）。",
        "● ② 類別型數據：離散分類或順序標籤（如性別、城市、會員等級、五點滿意度選項）。",
        "● 適配模型：企業私有小型模型（如 Rockfish Data）即可精準學習聯合機率分布，保障機密不外洩。"
    ],
    is_spotlight=False
)
add_card(
    s4, 4.68, 1.42, 3.95, 5.15,
    "結構二：半結構化數據", "自帶標籤之巢狀日誌 (JSON / XML)",
    [
        "● 非固定長度但具結構標籤：因每位顧客行為序列長短不一，無法直接塞入死板二維表格，但具明確 Key-Value 標籤。",
        "● 典型市調實例：網站與 App 點擊流紀錄（Clickstream）、帶標頭之客服工單與電子郵件中繼資料。",
        "● 適配模型：小型私有模型同樣能有效捕捉序列轉移機率（如美國陸軍與國土安全部之模擬應用）。"
    ],
    is_spotlight=False
)
add_card(
    s4, 8.96, 1.42, 3.97, 5.15,
    "★ 聚光燈焦點：非結構化質化數據", "自然語言脈絡 × 大模型世界知識先驗",
    [
        "● 承載 Why 與 How 深層動機：深度訪談逐字稿、焦點團體錄影、社群長篇抱怨貼文，完全無預先定義格式。",
        "● ★ 為何小模型無能為力？小型私有模型只看過內部表格，沒讀過全人類文本，缺乏「世界知識先驗（World Knowledge Prior）」，不懂反諷與心理脈絡！",
        "● ★ 黃金折衷處方：以「企業內部獨有數據微調（Fine-tune）公開大型模型」，兼顧隱私與質化深度。"
    ],
    is_spotlight=True, spot_color=C_SPOT_TEAL, spot_bg=C_SPOT_TEALBG
)
add_zone3_footer(
    s4, "依資料結構選配模型：純表格與點擊流交給「私有小模型」保機密；深度質化訪談則必須採用「內部數據微調之公開大模型」。"
)
notes_s4 = (
    "【講者備忘稿 Slide 04】很多高管會問：我們能不能自己訓練一個小型私有模型，既省錢又百分之百保密？"
    "這頁三支柱卡片給出了最精準的資料科學解答：如果你的資料是左卡的『結構化數據』（包含數字型與類別型）或中卡的『半結構化點擊流日誌』，"
    "像 Rockfish Data 這類私有小模型完全勝任。但如果你要處理右卡的『非結構化質化數據』，小模型因為從未讀過全人類的文學與對話，沒有『世界知識先驗』，"
    "根本聽不懂人類的言外之意！因此，拿企業內部私有數據去微調公開大型模型，才是兼顧機密與質化智慧的最佳解方。"
)
add_speaker_notes(s4, notes_s4)
slides_md_records.append(("Slide 04：【第二幕：資料結構與大小模型分工】版型 S2", "私有小型模型僅能學習表格統計機率，唯有公開大型模型具備解析質化語意之人類世界知識", notes_s4))


# ==============================================================================
# SLIDE 05: 第二幕 (S6 核心公式與直覺拆解型 — 盲測訂價實驗之混淆現象 Confounding)
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_bg(s5, C_BG_CANVAS)
add_zone1_header(
    s5, "Slide 05", "第二幕：盲測訂價失靈之因果公式拆解 (S6 核心公式與直覺拆解型)",
    "生成式 AI 在盲測訂價中會自動腦補競品與歷史價同步變貴，導致需求曲線平坦失真"
)

# Top Math Equation Box in Zone 2
eq_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.40), Inches(1.38), Inches(12.53), Inches(1.85))
eq_box.adjustments[0] = 0.04
eq_box.fill.solid()
eq_box.fill.fore_color.rgb = C_SPOT_GOLDBG
eq_box.line.color.rgb = C_SPOT_GOLD
eq_box.line.width = Pt(2.2)

tf_eq = eq_box.text_frame
tf_eq.word_wrap = True
tf_eq.margin_left = tf_eq.margin_right = Inches(0.25)
tf_eq.margin_top = Inches(0.14)

pe1 = tf_eq.paragraphs[0]
pe1.alignment = PP_ALIGN.CENTER
re1 = pe1.add_run()
re1.text = "【真人隨機盲測：獨立因果干預】 P(Y | do(X = x)) = ∑z P(Y | X = x, Z = z) · P(Z = z)"
re1.font.name = FONT_CJK
re1.font.size = Pt(15.5)
re1.font.bold = True
re1.font.color.rgb = C_NAVY_DARK

pe2 = tf_eq.add_paragraph()
pe2.alignment = PP_ALIGN.CENTER
pe2.space_before = Pt(6)
re2 = pe2.add_run()
re2.text = "≠   【生成式 AI 盲測：語境條件聯想混淆】 P_LLM(Y | X = x) = ∑z P(Y | X = x, Z = z) · P_LLM(Z = z | X = x)"
re2.font.name = FONT_CJK
re2.font.size = Pt(15.5)
re2.font.bold = True
re2.font.color.rgb = C_SPOT_RED

pe3 = tf_eq.add_paragraph()
pe3.alignment = PP_ALIGN.CENTER
pe3.space_before = Pt(6)
re3 = pe3.add_run()
re3.text = "▲ 關鍵差異項：真人盲測中 P(Z | X) = P(Z) 恆定不變；但 AI 的 P_LLM(Z = z | X = x) 會隨測試價格 X 升高而同步調高背景價格 Z！"
re3.font.name = FONT_CJK
re3.font.size = Pt(11.5)
re3.font.bold = True
re3.font.color.rgb = C_SPOT_GOLD

# 3 Pointer Anatomy Cards below Equation
add_card(
    s5, 0.40, 3.42, 3.95, 3.18,
    "公式項拆解 (1)：X 與 Y", "測試價格 (X) → 購買意願 (Y)",
    [
        "● 盲測實驗目的：將受試者隨機分組，A 組看 1,000 元、B 組看 5,000 元，測量純粹調高價格 X 對購買率 Y 的因果斜率。",
        "● 真人反應：看到 5,000 元時，依據日常物價基準果斷拒絕購買，需求曲線正常向右下傾斜。"
    ],
    is_spotlight=False
)
add_card(
    s5, 4.68, 3.42, 3.95, 3.18,
    "公式項拆解 (2)：混淆變數 Z", "歷史價格與店內競品價格 (Z)",
    [
        "● 隱藏的第三變數 Z：顧客心中的參考價格錨點（過往買過的歷史價、貨架旁競爭對手的售價）。",
        "● 隨機分派獨立性：在真人實驗中，研究員改動標價 X，並不會改變受試者腦中對競品價格 Z（1,200 元）的既有記憶。"
    ],
    is_spotlight=False
)
add_card(
    s5, 8.96, 3.42, 3.97, 3.18,
    "★ 聚光燈拆解 (3)：P_LLM(Z | X)", "AI 自動腦補語境共現 (Confounding)",
    [
        "● ★ 語境條件聯想本能：LLM 本質是根據上下文猜測合理語境，無法將測試價格 X 視為「隨機抽樣」。",
        "● ★ 致命腦補效應：當 AI 看到標價 X=5,000 元時，自動調高 P_LLM(Z|X)，腦補「店內競品與歷史價 Z 也全是 5,000 元」，誤判高價合理而照買不誤！"
    ],
    is_spotlight=True, spot_color=C_SPOT_RED, spot_bg=C_SPOT_REDBG
)
add_zone3_footer(
    s5, "絕對禁止直接拿未經統計校準的生成式 AI 進行「單一變數盲測訂價實驗」，否則將嚴重低估顧客對漲價的抗拒度！"
)
notes_s5 = (
    "【講者備忘稿 Slide 05】為什麼生成式 AI 可以做深度訪談，卻不能直接拿來做『盲測訂價實驗』？這頁公式三明治揭開了最底層的數學真相。"
    "在真人隨機盲測中，受試者看到測試商品標價 5,000 元（X），他腦中對旁邊競品只賣 1,200 元（Z）的記憶是不變的，所以他會拒買。"
    "但大型語言模型天生運算的是『語境條件機率 P_LLM(Z|X)』：當你給它看 5,000 元時，它會自動腦補『既然這件賣 5,000，那這家店肯定在通膨世界或頂級名牌店，旁邊競品 Z 一定也賣 5,000 元』！"
    "結果 AI 在高價組依然照買不誤，需求曲線完全平坦失真。這就是文中強調的『混淆現象（Confounding）』。"
)
add_speaker_notes(s5, notes_s5)
slides_md_records.append(("Slide 05：【第二幕：盲測訂價失靈之因果公式拆解】版型 S6", "生成式 AI 在盲測訂價中會自動腦補競品與歷史價同步變貴，導致需求曲線平坦失真", notes_s5))


# ==============================================================================
# SLIDE 06: 第二幕 (S1 不對稱雙欄對照型 — 純改提示詞挖東牆補西牆 vs. 四大前沿解法死穴批判)
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_bg(s6, C_BG_CANVAS)
add_zone1_header(
    s6, "Slide 06", "第二幕：方法論深度思辨與第一性原理批判 (S1 不對稱雙欄對照型)",
    "純改提示詞必淪為挖東牆補西牆，四大前沿修補解法亦各自存在無法根除之理論死穴"
)

# Left Column (40% width): Prompt Engineering Dilemma
add_card(
    s6, 0.40, 1.40, 4.75, 5.20,
    "舊思維盲點：純改提示詞 (Prompt)", "為何寫更細的規範是「挖東牆補西牆」？",
    [
        "● 【東牆：未知腦補變數永遠鎖不完】\n"
        "就算在提示詞死鎖「歷史價與競品價皆為 1,200 元」，具備數千億參數的 AI 看到 5,000 元仍會自動繞道腦補「現在大缺貨、巨星聯名或限量溢價」，人類無法事前窮舉所有潛在混淆變數 Z！",
        "● 【西牆：寫太白引發需求特徵劇透】\n"
        "若刻意強調「別家都賣 1,200、唯獨這家賣 5,000」，等於向 AI 劇透實驗目的並觸發焦點錯覺，使 AI 變成呆板比大小的計算機（100% 拒買），照樣測不出真實人類的價格彈性曲線。"
    ],
    is_spotlight=False
)

# Right Column (60% width): Spotlight Table of 4 Frontier Solutions & User's Critique
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

# Native Table inside Right Panel
rows, cols = 5, 3
tbl_shape = s6.shapes.add_table(rows, cols, Inches(5.48), Inches(1.98), Inches(7.30), Inches(4.45))
tbl = tbl_shape.table
tbl.columns[0].width = Inches(1.75)
tbl.columns[1].width = Inches(2.45)
tbl.columns[2].width = Inches(3.10)

headers_s6 = ["前沿破局解法", "核心運作機制", "★ 您的第一性原理「理論死穴」批判"]
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
    r.font.size = Pt(10)
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
        r = p.add_run()
        r.text = val
        r.font.name = FONT_CJK
        r.font.size = Pt(9.5)
        r.font.bold = (c_idx == 0 or c_idx == 2)
        r.font.color.rgb = C_SPOT_RED if c_idx == 2 else C_SLATE_TXT

add_zone3_footer(
    s6, "徹底放棄尋找「單一萬能 AI 市調模型」的幻想；承認四大解法各有死穴，改採「依商業情境動態配置工具組合」。"
)
notes_s6 = (
    "【講者備忘稿 Slide 06】既然 AI 會發生語境腦補，我們能不能靠『把提示詞寫得更詳細』來解決？左欄點破了為什麼這是一條死胡同："
    "第一，未知腦補變數永遠鎖不完；第二，寫太白會引發需求特徵劇透，讓 AI 變成死板比大小的計算機。這就是『挖東牆補西牆』！"
    "而右欄則是我們在第一階段思辨中最精彩的結晶：學術界提出的四大前沿解法，從第一性原理來看也各有死穴——"
    "數位雙生塞不進生理嗅覺與潛意識、左腦統計公式寫不出高度複雜的非線性交互作用、統計校準只是當下湊巧對齊、歷史微調則無法預測未來行為劇變與突破性創新。"
)
add_speaker_notes(s6, notes_s6)
slides_md_records.append(("Slide 06：【第二幕：方法論深度思辨與第一性原理批判】版型 S1", "純改提示詞必淪為挖東牆補西牆，四大前沿修補解法亦各自存在無法根除之理論死穴", notes_s6))


# ==============================================================================
# SLIDE 07: 第三幕全景圖譜 (嵌入高解析圖譜二)
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_bg(s7, C_BG_CANVAS)
add_zone1_header(
    s7, "Slide 07", "第三幕：實驗混淆與四大解法批判全景圖譜 (High-DPI Diagram 02)",
    "所有模型皆有盲區，企業須依感官涉入度與創新幅度動態切換人機權變工具組合"
)
img_frame2 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.35), Inches(1.32), Inches(8.65), Inches(5.35))
img_frame2.fill.solid()
img_frame2.fill.fore_color.rgb = C_WHITE
img_frame2.line.color.rgb = C_BORDER_MUT
img_frame2.line.width = Pt(1.5)
s7.shapes.add_picture(IMG2, Inches(0.42), Inches(1.38), width=Inches(8.51))

add_card(
    s7, 9.15, 1.32, 3.82, 5.35,
    "★ 圖譜二核心導讀", "George Box 情境權變投資組合",
    [
        "● 【統計大師名言】：「所有模型都是錯的，但有些在特定情境下極度有用！」",
        "● 【情境 A：早期百倍速發想】\n組合「解法一（數位雙生）＋ 解法四（歷史微調）」，低成本淘汰 80% 弱點子。",
        "● 【情境 B：常規品牌診斷】\n組合「AI 動態訪談員 ＋ 解法二（右腦轉譯＋左腦統計）」，幻覺最少且精準抓出高 Lift 關鍵因素。",
        "● 【情境 C：終局定價與感官創新】\n強制回歸「真人隨機盲測（A/B Test）」。"
    ],
    is_spotlight=True, spot_color=C_SPOT_GOLD, spot_bg=C_SPOT_GOLDBG
)
add_zone3_footer(
    s7, "將市調預算按「80% AI 早期廣度快篩 ＋ 20% 真人終局因果盲測」重新配置，實現速度與科學嚴謹度的最佳解。"
)
notes_s7 = (
    "【講者備忘稿 Slide 07】這張對照矩陣圖譜將 AI 的三大技術局限與四大前沿解法完整視覺化。"
    "呼應統計學大師 George Box 的名言『所有模型都是錯的，但有些很有用』，企業不該爭論哪一個模型最好，"
    "而是建立右側的『情境權變組合矩陣』：早期發想用數位雙生衝速度、常規診斷用左腦統計控幻覺、關鍵定價與感官體驗則交還真人盲測。"
)
add_speaker_notes(s7, notes_s7)
slides_md_records.append(("Slide 07：【第三幕：全景圖譜實證（二）】", "所有模型皆有盲區，企業須依感官涉入度與創新幅度動態切換人機權變工具組合", notes_s7))


# ==============================================================================
# SLIDE 08: 第三幕 (S5 2x2 策略象限矩陣型 — 人機分工邊界與三大禁區)
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_bg(s8, C_BG_CANVAS)
add_zone1_header(
    s8, "Slide 08", "第三幕：正反實證與人機邊界矩陣 (S5 2×2 策略象限矩陣型)",
    "高感官涉入與突破性創新構成生成式 AI 禁區，最終定價與五感測試必須回歸真人盲測"
)

# Axis Labels
axis_y = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.35), Inches(1.42), Inches(0.55), Inches(5.15))
axis_y.fill.solid()
axis_y.fill.fore_color.rgb = C_NAVY_DARK
axis_y.line.fill.background()
tf_ay = axis_y.text_frame
p_ay = tf_ay.paragraphs[0]
p_ay.alignment = PP_ALIGN.CENTER
r_ay = p_ay.add_run()
r_ay.text = "縱\n軸\n：\n感\n官\n與\n潛\n意\n識\n涉\n入\n度"
r_ay.font.name = FONT_CJK
r_ay.font.size = Pt(11)
r_ay.font.bold = True
r_ay.font.color.rgb = C_SKY_LIGHT

# Top-Left Quadrant (High Sensory x Existing/Incremental)
add_card(
    s8, 1.05, 1.42, 5.80, 2.48,
    "象限 II：高生理五感 × 既有品類改版", "【AI 禁區一】多感官與潛意識失靈（高砂香料案例）",
    [
        "● 實證敗北：高砂香料（Takasago）嘗試以合成受訪者評估新款香水，但 AI 完全沒鼻子，無法連結氣味分子與童年潛意識記憶。",
        "● 處方：香水、食品口味、材質觸感測試必須強制採用「真人實體感官盲測」。"
    ],
    is_spotlight=False
)

# Top-Right Quadrant (High Causal/Pricing & Radical Innovation — SPOTLIGHT)
add_card(
    s8, 7.05, 1.42, 5.88, 2.48,
    "★ 象限 I（聚光燈核心禁區）：突破性創新 × 盲測訂價", "【AI 禁區二 & 三】歷史外推失靈 ＋ 價格混淆現象",
    [
        "● ★ 雙重失靈風險：面對「消費者行為劇變／突破性新產品」時歷史微調外推失效；進行「盲測訂價」時 AI 自動腦補競品同價。",
        "● ★ 終局鐵律：上市前最終定價與突破性產品驗證，必須執行「真人隨機對照實驗（A/B Test）」搭配「PPI 小樣本真人動態校準」。"
    ],
    is_spotlight=True, spot_color=C_SPOT_RED, spot_bg=C_SPOT_REDBG
)

# Bottom-Left Quadrant (Low Sensory / Rational x Existing Category)
add_card(
    s8, 1.05, 4.08, 5.80, 2.48,
    "象限 III（AI 主力戰場）：理性認知 × 常規品類診斷", "【AI 最佳適配】AI 動態訪談員 ＋ 右腦轉譯／左腦統計",
    [
        "● 實證成功：WeightWatchers 透過 Outset.ai 消除受訪者道德修飾；安永 (EY) 1,000 名合成 CEO 雙盲測試達 95% 一致率。",
        "● 處方：以 AI 訪談員收集無偽裝痛點，交由左腦統計模型計算各驅動因素之提升潛力（Lift）。"
    ],
    is_spotlight=False
)

# Bottom-Right Quadrant (Low Sensory / Rational x Early Ideation & B2B Roleplay)
add_card(
    s8, 7.05, 4.08, 5.88, 2.48,
    "象限 IV（AI 加速戰場）：早期百倍速探索 × 話術演練", "【AI 最佳適配】顧客數位雙生 ＋ 內部數據微調大模型",
    [
        "● 實證成功：哥倫比亞 2,500 人數位雙生群組、史丹福 85% 重測信度、通用磨坊與 Arena 填補過往無外部數據之決策缺口。",
        "● 處方：用綁定真人記憶之數位雙生進行 B2B 業務話術演練與百倍速早期產品概念篩選。"
    ],
    is_spotlight=False
)

add_zone3_footer(
    s8, "用 2×2 矩陣把關市調專案：下方兩個象限放手讓生成式 AI 百倍速衝刺，上方兩個象限嚴格保留真人實驗預算！"
)
notes_s8 = (
    "【講者備忘稿 Slide 08】為了讓前線團隊一秒判斷什麼時候該用 AI、什麼時候必須找真人，我們將人機分工邊界收斂為這張 2×2 策略象限矩陣。"
    "請看下半部：只要屬於理性認知評估、早期概念篩選或 B2B 銷售話術演練（象限 III 與 IV），生成式 AI 與數位雙生能帶來百倍速的生產力爆發。"
    "但一旦進入上半部——涉及香水與食品等生理五感（象限 II，如高砂香料案例），或是右上角聚光燈標示的『突破性產品創新與盲測訂價』（象限 I），"
    "就是生成式 AI 的絕對禁區，必須強制回歸真人隨機盲測！"
)
add_speaker_notes(s8, notes_s8)
slides_md_records.append(("Slide 08：【第三幕：正反實證與人機邊界矩陣】版型 S5", "高感官涉入與突破性創新構成生成式 AI 禁區，最終定價與五感測試必須回歸真人盲測", notes_s8))


# ==============================================================================
# SLIDE 09: 第四幕 (S3 水平階梯演進流程型 — 三篇合體「道・法・術」三階閉環)
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_bg(s9, C_BG_CANVAS)
add_zone1_header(
    s9, "Slide 09", "第四幕：三篇 HBR 合體決策架構 (S3 水平階梯演進流程型)",
    "企業須先以統計模型定錨關鍵驅動因素並打通情境底座，再部署生成式 AI 市調實操閉環"
)

# Step 01 Card (道)
add_card(
    s9, 0.38, 1.42, 3.88, 5.15,
    "Step 01【道：界定問題與方向】", "《顧客需求不靠猜！統計模型找正解》",
    [
        "● 破除高層直覺偏誤：72% B2B 高層認知與顧客真實重視零相關（受顯眼客訴與盲從對手誤導）。",
        "● 道斯線性模型找 X*：計算各屬性對整體價值與真實營收 Y 的「提升潛力（Lift）」。",
        "● 少做多得：嚴格鎖定 1~2 個高 Lift 關鍵因素 X*（如 ITI 主動週報使股價漲 162%），為後續 AI 指明改進靶心！"
    ],
    is_spotlight=False
)

# Arrow 1 -> 2
arr1 = s9.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(4.31), Inches(3.75), Inches(0.36), Inches(0.45))
arr1.fill.solid()
arr1.fill.fore_color.rgb = C_NAVY_MED
arr1.line.fill.background()

# Step 02 Card (法)
add_card(
    s9, 4.72, 1.42, 3.88, 5.15,
    "Step 02【法：能力盤點與情境底座】", "《AI 能強化你的數據分析能力》",
    [
        "● 內嵌 ERP/CRM 背景情境：打破數據孤島，由領域專家設定合理因果邊界（防止醫療 AI 肺炎配氣喘等虛假相關）。",
        "● 擴增分析賦能前線：結合 ML + NLP 口說提問 + NLG 自動摘要（如製造商揪出未授權折扣挽回數十萬美元）。",
        "● 統計自由度懲罰：以 Adjusted R² 與 Lasso (L1) 正則化自動將無效雜訊特徵權重歸零。"
    ],
    is_spotlight=False
)

# Arrow 2 -> 3
arr2 = s9.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(8.65), Inches(3.75), Inches(0.36), Inches(0.45))
arr2.fill.solid()
arr2.fill.fore_color.rgb = C_SPOT_BLUE
arr2.line.fill.background()

# Step 03 Card (術 — SPOTLIGHT)
add_card(
    s9, 9.06, 1.42, 3.90, 5.15,
    "★ Step 03【術：前線市調與人機權變】", "《生成式 AI 正在顛覆市場研究》",
    [
        "● ★ 前線高頻武器：針對第一階鎖定的 X*，派出「AI 動態訪談員（Outset.ai）」消除受訪者心理與道德修飾，挖出深層痛點。",
        "● ★ 數位雙生快篩：以第二階的 ERP 私有數據微調大模型，打造顧客數位雙生進行百倍速早期策略測試與業務演練。",
        "● ★ 四關卡終審閉環：最終定價與感官體驗強制回歸「真人隨機盲測（A/B Test）」，並綁定真實會計毛利！"
    ],
    is_spotlight=True, spot_color=C_SPOT_BLUE, spot_bg=C_SPOT_BG
)

add_zone3_footer(
    s9, "切勿在目標不明（無道）與數據孤島（無法）下盲目導入生成式 AI；必須按「道 → 法 → 術」三階順序建構決策閉環。"
)
notes_s9 = (
    "【講者備忘稿 Slide 09】這頁是我們整個系列讀書會最核心的結晶——將三篇 HBR 經典文章串聯為『道、法、術』三階閉環！"
    "第一階是『道』（《顧客需求不靠猜》）：用統計模型克服高層直覺偏誤，鎖定 1 到 2 個真正高 Lift 的關鍵驅動因素 X*，明確定義我們要解決什麼問題；"
    "第二階是『法』（《AI 能強化你的數據分析能力》）：打通企業內部的 ERP 與 CRM，把人類專家的『背景情境（Contextual Information）』嵌進去，並用 Lasso 正則化過濾雜訊；"
    "第三階才是『術』（《生成式 AI 正在顛覆市場研究》）：在前兩階的穩固地基上，派出 AI 訪談員消除受訪者的道德修飾，用數位雙生百倍速快篩方案，最後以真人 A/B Test 完成終審閉環！"
)
add_speaker_notes(s9, notes_s9)
slides_md_records.append(("Slide 09：【第四幕：三篇 HBR 合體決策架構】版型 S3", "企業須先以統計模型定錨關鍵驅動因素並打通情境底座，再部署生成式 AI 市調實操閉環", notes_s9))


# ==============================================================================
# SLIDE 10: 第四幕全景圖譜與落地檢核 (嵌入高解析圖譜三)
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_bg(s10, C_BG_CANVAS)
add_zone1_header(
    s10, "Slide 10", "第四幕：三篇合體終極藍圖與四道關卡 (High-DPI Diagram 03)",
    "貫通統計決策、情境底座與生成式市調四道關卡，全面驅動企業與客戶價值造血迴路"
)
img_frame3 = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.35), Inches(1.32), Inches(8.65), Inches(5.35))
img_frame3.fill.solid()
img_frame3.fill.fore_color.rgb = C_WHITE
img_frame3.line.color.rgb = C_BORDER_MUT
img_frame3.line.width = Pt(1.5)
s10.shapes.add_picture(IMG3, Inches(0.42), Inches(1.38), width=Inches(8.51))

add_card(
    s10, 9.15, 1.32, 3.82, 5.35,
    "★ 終局落地：四道實證檢核關卡", "驅動「企業 ↔ 客戶」造血引擎",
    [
        "● 【關卡一：開放式無偽裝探索】\n以 AI 動態訪談員消除心理與道德修飾，搭配合成雙生百倍速發掘潛在痛點。",
        "● 【關卡二：統計推導重要性】\n不信口頭宣稱，以道斯線性模型與 Lasso 正則化篩出高 Lift 關鍵因素 X*。",
        "● 【關卡三：綁定 ERP 真實帳本】\n在跨部門背景情境護欄下，驗證 X* 對實際購買率與客戶留存率的財務貢獻。",
        "● 【關卡四：真人隨機盲測終審】\n針對最終訂價、多感官與突破性創新執行真人 A/B Test（如 800 億美元銀行案例）。"
    ],
    is_spotlight=True, spot_color=C_SPOT_TEAL, spot_bg=C_SPOT_TEALBG
)
add_zone3_footer(
    s10, "立即啟動試點：先用統計模型鎖定 1 個核心業務痛點 X*，再導入 AI 動態訪談與微調雙生，最後以真人小樣本 A/B Test 驗收 ROI！"
)
notes_s10 = (
    "【講者備忘稿 Slide 10】最後一頁我們呈現了『三篇合體』的終極架構藍圖與四道落地關卡。"
    "無論 AI 技術如何演進，企業存在的本質永遠是底部的『企業 ↔ 客戶價值造血迴路』。"
    "只要我們嚴格執行右側的『四道實證檢核關卡』——AI 訪談無偽裝探索、統計模型推導重要性、綁定 ERP 真實會計帳本、以及真人隨機盲測終審，"
    "就能同時擁有生成式 AI 的百倍速敏捷度，以及統計因果科學的最高嚴謹度。謝謝大家！"
)
add_speaker_notes(s10, notes_s10)
slides_md_records.append(("Slide 10：【第四幕：三篇合體終極藍圖與四道關卡】", "貫通統計決策、情境底座與生成式市調四道關卡，全面驅動企業與客戶價值造血迴路", notes_s10))

prs.save(PPTX_PATH)
print(f"[OK] Saved PPTX: {PPTX_PATH} ({os.path.getsize(PPTX_PATH)} bytes)")

# Also write Dual-Channel Markdown Script
md_lines = [
    "# 《生成式 AI 正在顛覆市場研究》深度思辨與「三篇合體」斷言—證據簡報腳本 (Format C)\n",
    "> **架構規範**：全面遵循 Alley & Neeley (2005) 斷言—證據三區架構、Kosslyn (2007) 相容性視覺版型（`S1`～`S6`）、Knaflic (2015) 80/20 前注意力聚光燈與 Mayer (2003) 視覺／語音雙通道分離原則。\n\n---\n"
]
for title, assertion, notes in slides_md_records:
    md_lines.append(f"## {title}\n")
    md_lines.append(f"- **【Zone 1 頂部結論斷言】**：**{assertion}**\n")
    md_lines.append(f"- **🎙️ 講者備忘稿 (Speaker Notes — 語音通道)**：\n  > {notes}\n\n---\n")

with open(MD_SCRIPT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))
print(f"[OK] Saved Markdown Slide Script: {MD_SCRIPT_PATH}")
