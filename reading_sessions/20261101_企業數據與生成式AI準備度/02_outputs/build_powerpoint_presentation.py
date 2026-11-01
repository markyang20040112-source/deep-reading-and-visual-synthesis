"""
build_powerpoint_presentation.py
Builds the 16:9 widescreen PowerPoint deck (02_executive_presentation.pptx)
in 100% compliance with presentation_slide_spec.md & visual_cognition_principles.md:
- 3-Tier Anti-Fatigue Layout Sequence: S0 -> S1 -> S7 -> S2 -> S6 -> S4 -> S1 -> S3 -> S0 (Zero consecutive identical layouts!)
- Plain-First & Shallow-to-Deep (淺層現象/直覺 -> 中層情境/做法 -> 深層風險/價值) across all cards
- Parallel Row Alignment (Centered Row Panels) + Knaflic 80/20 Preattentive Spotlight
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Theme Colors
BG_LIGHT = RGBColor(248, 250, 252)       # Slate 50 (#F8FAFC)
TEXT_NAVY = RGBColor(15, 23, 42)         # Slate 900 (#0F172A)
TEXT_MUTED = RGBColor(100, 116, 139)     # Slate 500 (#64748B)
TEXT_BODY = RGBColor(51, 65, 85)         # Slate 700 (#334155)
CARD_BG = RGBColor(255, 255, 255)        # Pure White
CARD_BORDER = RGBColor(203, 213, 225)    # Slate 300 (#CBD5E1)

COLOR_PRIMARY = RGBColor(30, 64, 175)    # Royal Blue (#1E40AF)
COLOR_DANGER = RGBColor(190, 18, 60)     # Crimson Red (#BE123C)
COLOR_WARN = RGBColor(180, 83, 9)        # Amber Warm (#B45309)
COLOR_SUCCESS = RGBColor(4, 120, 87)     # Emerald Green (#047857)

# Soft Header Tints
TINT_BLUE = RGBColor(239, 246, 255)      # Blue 50
TINT_RED = RGBColor(254, 242, 242)       # Red 50
TINT_AMBER = RGBColor(254, 243, 199)     # Amber 100
TINT_GREEN = RGBColor(236, 253, 245)     # Emerald 50
TINT_SLATE = RGBColor(241, 245, 249)     # Slate 100

# Dark Slide Colors
DARK_HUB_BG = RGBColor(15, 23, 42)       # Slate 900
DARK_CARD_BG = RGBColor(30, 41, 59)      # Slate 800
DARK_ROW_BG = RGBColor(15, 23, 42)       # Slate 900 row
DARK_HUB_SUB = RGBColor(56, 189, 248)    # Sky blue (#38BDF8)
DARK_TEXT_BODY = RGBColor(226, 232, 240) # Slate 200 (#E2E8F0)


def calc_pill_width(pill_text):
    """Exact Text-Hug Sizing formula: pill_w = (9.5 / 72.0) * (1.00 * CJK + 0.50 * ASCII) + 0.22"""
    cjk_count = sum(1 for c in pill_text if ord(c) > 127)
    ascii_count = len(pill_text) - cjk_count
    return (9.5 / 72.0) * (1.00 * cjk_count + 0.50 * ascii_count) + 0.22


def add_zone1_header(slide, pill_text, headline_text, accent_color=COLOR_PRIMARY, is_dark_slide=False):
    pill_w = calc_pill_width(pill_text)
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.15), Inches(pill_w), Inches(0.28))
    pill.adjustments[0] = 0.25
    pill.fill.solid()

    if is_dark_slide:
        pill.fill.fore_color.rgb = DARK_CARD_BG
        pill.line.color.rgb = DARK_HUB_SUB
        pill_text_color = DARK_HUB_SUB
    else:
        pill.fill.fore_color.rgb = RGBColor(15, 23, 42)
        pill.line.color.rgb = RGBColor(15, 23, 42)
        pill_text_color = RGBColor(255, 255, 255)

    pill.line.width = Pt(1.0)
    tf_p = pill.text_frame
    tf_p.word_wrap = False
    tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_p.margin_left = tf_p.margin_right = Inches(0.11)
    tf_p.margin_top = tf_p.margin_bottom = 0
    p = tf_p.paragraphs[0]
    p.text = pill_text
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Microsoft JhengHei"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = pill_text_color

    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.58), Inches(11.733), Inches(0.44))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p2 = tf.paragraphs[0]
    p2.text = headline_text
    p2.font.name = "Microsoft JhengHei"
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(255, 255, 255) if is_dark_slide else TEXT_NAVY


def add_zone3_footer(slide, takeaway_text, is_dark_slide=False):
    footer = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.60), Inches(11.733), Inches(0.48))
    footer.adjustments[0] = 0.20
    footer.fill.solid()
    footer.fill.fore_color.rgb = RGBColor(2, 6, 23) if is_dark_slide else DARK_HUB_BG
    footer.line.color.rgb = DARK_HUB_SUB
    footer.line.width = Pt(1.2)

    tf = footer.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.25)
    tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = takeaway_text
    p.font.name = "Microsoft JhengHei"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(248, 250, 252)


def set_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text


def create_structured_card(slide, left, top, width, height, title, subtitle, rows_data,
                           accent_color=COLOR_PRIMARY, header_tint=TINT_SLATE,
                           is_spotlight=False, is_dark_slide=False, row_y_slots=None,
                           hdr_h=Inches(0.72), tag_pt=10.8, desc_pt=9.8):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.adjustments[0] = 0.035
    card.fill.solid()
    if is_dark_slide:
        card.fill.fore_color.rgb = DARK_CARD_BG
        card.line.color.rgb = accent_color if is_spotlight else RGBColor(71, 85, 105)
    else:
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = accent_color if is_spotlight else CARD_BORDER
    card.line.width = Pt(2.2 if is_spotlight else 1.1)

    hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.08), top + Inches(0.08), width - Inches(0.16), hdr_h)
    hdr.adjustments[0] = 0.04
    hdr.fill.solid()
    if is_dark_slide:
        hdr.fill.fore_color.rgb = RGBColor(15, 23, 42)
        hdr.line.color.rgb = accent_color if is_spotlight else RGBColor(71, 85, 105)
    else:
        hdr.fill.fore_color.rgb = header_tint
        hdr.line.color.rgb = accent_color if is_spotlight else CARD_BORDER
    hdr.line.width = Pt(1.2 if is_spotlight else 0.8)

    tf_h = hdr.text_frame
    tf_h.word_wrap = True
    tf_h.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_h.margin_left = tf_h.margin_right = Inches(0.14)
    tf_h.margin_top = tf_h.margin_bottom = 0

    p_t = tf_h.paragraphs[0]
    p_t.text = title
    p_t.alignment = PP_ALIGN.CENTER
    p_t.font.name = "Microsoft JhengHei"
    p_t.font.size = Pt(11.8)
    p_t.font.bold = True
    p_t.font.color.rgb = accent_color

    if subtitle:
        p_sub = tf_h.add_paragraph()
        p_sub.text = subtitle
        p_sub.alignment = PP_ALIGN.CENTER
        p_sub.font.name = "Microsoft JhengHei"
        p_sub.font.size = Pt(9.0)
        p_sub.font.bold = False
        p_sub.font.color.rgb = DARK_HUB_SUB if is_dark_slide else TEXT_MUTED

    for idx, (tag, desc) in enumerate(rows_data):
        if idx >= len(row_y_slots):
            break
        r_top, r_height = row_y_slots[idx]
        row_box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            left + Inches(0.12), r_top, width - Inches(0.24), r_height
        )
        row_box.adjustments[0] = 0.04
        row_box.fill.solid()
        if is_dark_slide:
            row_box.fill.fore_color.rgb = DARK_ROW_BG
            row_box.line.color.rgb = RGBColor(51, 65, 85)
        else:
            row_box.fill.fore_color.rgb = RGBColor(248, 250, 252)
            row_box.line.color.rgb = RGBColor(226, 232, 240)
        row_box.line.width = Pt(0.8)

        tf_r = row_box.text_frame
        tf_r.word_wrap = True
        tf_r.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf_r.margin_left = tf_r.margin_right = Inches(0.16)
        tf_r.margin_top = tf_r.margin_bottom = Inches(0.05)

        p1 = tf_r.paragraphs[0]
        p1.text = f"● 【{tag}】"
        p1.alignment = PP_ALIGN.CENTER
        p1.font.name = "Microsoft JhengHei"
        p1.font.size = Pt(tag_pt)
        p1.font.bold = True
        p1.font.color.rgb = accent_color
        p1.space_after = Pt(3)

        p2 = tf_r.add_paragraph()
        p2.text = desc
        p2.alignment = PP_ALIGN.CENTER
        p2.font.name = "Microsoft JhengHei"
        p2.font.size = Pt(desc_pt)
        p2.font.bold = False
        p2.font.color.rgb = DARK_TEXT_BODY if is_dark_slide else TEXT_BODY
        p2.line_spacing = 1.32

    return card


# ==============================================================================
# SLIDE 1 [Layout S0]: 序幕：高階決策封面頁 (Dark Bookend Cover Slide)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg1.fill.solid()
bg1.fill.fore_color.rgb = DARK_HUB_BG
bg1.line.fill.background()

bar = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(0.12), Inches(5.9))
bar.adjustments[0] = 0.5
bar.fill.solid()
bar.fill.fore_color.rgb = DARK_HUB_SUB
bar.line.fill.background()

pill1_w = calc_pill_width("企業生成式 AI 數據戰略白皮書")
pill1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(0.85), Inches(pill1_w), Inches(0.32))
pill1.adjustments[0] = 0.25
pill1.fill.solid()
pill1.fill.fore_color.rgb = DARK_CARD_BG
pill1.line.color.rgb = DARK_HUB_SUB
pill1.line.width = Pt(1.2)
tf_cp = pill1.text_frame
tf_cp.word_wrap = False
tf_cp.vertical_anchor = MSO_ANCHOR.MIDDLE
tf_cp.margin_left = tf_cp.margin_right = Inches(0.12)
p_cp = tf_cp.paragraphs[0]
p_cp.text = "企業生成式 AI 數據戰略白皮書"
p_cp.font.name = "Microsoft JhengHei"
p_cp.font.size = Pt(10)
p_cp.font.bold = True
p_cp.font.color.rgb = DARK_HUB_SUB

tb_title = s1.shapes.add_textbox(Inches(1.2), Inches(1.40), Inches(11.3), Inches(2.2))
tf_t = tb_title.text_frame
tf_t.word_wrap = True
tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0

p_m1 = tf_t.paragraphs[0]
p_m1.text = "從流沙到混凝土"
p_m1.font.name = "Microsoft JhengHei"
p_m1.font.size = Pt(36)
p_m1.font.bold = True
p_m1.font.color.rgb = RGBColor(255, 255, 255)
p_m1.space_after = Pt(8)

p_m2 = tf_t.add_paragraph()
p_m2.text = "生成式 AI 時代的企業數據治理與資產準備度戰略"
p_m2.font.name = "Microsoft JhengHei"
p_m2.font.size = Pt(21)
p_m2.font.bold = True
p_m2.font.color.rgb = DARK_HUB_SUB
p_m2.space_after = Pt(6)

p_m3 = tf_t.add_paragraph()
p_m3.text = "Enterprise Data Readiness & Governance Strategy for Generative AI: From Quicksand to Concrete"
p_m3.font.name = "Georgia"
p_m3.font.size = Pt(12)
p_m3.font.italic = True
p_m3.font.color.rgb = RGBColor(148, 163, 184)

thesis_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(3.85), Inches(11.3), Inches(1.80))
thesis_box.adjustments[0] = 0.04
thesis_box.fill.solid()
thesis_box.fill.fore_color.rgb = DARK_CARD_BG
thesis_box.line.color.rgb = RGBColor(16, 185, 129)
thesis_box.line.width = Pt(2.0)
tf_th = thesis_box.text_frame
tf_th.word_wrap = True
tf_th.vertical_anchor = MSO_ANCHOR.MIDDLE
tf_th.margin_left = tf_th.margin_right = Inches(0.35)

p_th1 = tf_th.paragraphs[0]
p_th1.text = "★ 全篇終極戰略定錨 (Core Strategic Thesis)"
p_th1.font.name = "Microsoft JhengHei"
p_th1.font.size = Pt(11)
p_th1.font.bold = True
p_th1.font.color.rgb = RGBColor(52, 211, 153)
p_th1.space_after = Pt(6)

p_th2 = tf_th.add_paragraph()
p_th2.text = "「生成式 AI 的企業壁壘不在買多貴的模型算力，而在內部私有數據的乾淨度與一致性——地基必須是混凝土，絕不能是流沙。」"
p_th2.font.name = "Microsoft JhengHei"
p_th2.font.size = Pt(15.5)
p_th2.font.bold = True
p_th2.font.color.rgb = RGBColor(255, 255, 255)
p_th2.line_spacing = 1.3

tb_meta = s1.shapes.add_textbox(Inches(1.2), Inches(5.95), Inches(11.3), Inches(0.5))
tf_meta = tb_meta.text_frame
p_meta = tf_meta.paragraphs[0]
p_meta.text = "實證依據：Thomas H. Davenport & Priyanka Tiwari (MIT Sloan / AWS, N=334)  ｜  版型引擎：S0–S7 防疲勞動態輪替架構  ｜  2026"
p_meta.font.name = "Microsoft JhengHei"
p_meta.font.size = Pt(10)
p_meta.font.color.rgb = RGBColor(148, 163, 184)

set_notes(s1, "各位董事會成員與技術主管，今天我們不談虛幻的模型參數，我們談最殘酷的商業現實。所有人都以為生成式 AI 只要採購 API 就能帶來生產力暴增，但最新麻省理工學院與 AWS 對全球 334 位數據長調查揭示：80% 企業躍躍欲試，但真正將生成式 AI 投入生產環境的只有 6%。今天我們拆解如何把這片流沙打造成混凝土。")


# ==============================================================================
# SLIDE 2 [Layout S1]: 序幕：戰略定錨 (Asymmetric Contrast: Myth vs Reality, 3 Shallow-to-Deep Rows)
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
bg2 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg2.fill.solid()
bg2.fill.fore_color.rgb = BG_LIGHT
bg2.line.fill.background()

add_zone1_header(s2, "戰略定錨｜版型 S1", "競爭壁壘不在買多貴的模型，而在內部數據是否乾淨且全公司口徑一致", COLOR_PRIMARY)

s_3rows_y = [
    (Inches(2.12), Inches(1.30)),
    (Inches(3.52), Inches(1.30)),
    (Inches(4.92), Inches(1.30)),
]

create_structured_card(
    s2, left=Inches(0.8), top=Inches(1.25), width=Inches(5.55), height=Inches(5.15),
    title="【流行技術迷思：流沙陷阱】",
    subtitle="誤以為模型夠聰明就能跳過底層數據大掃除",
    rows_data=[
        ("淺層直覺：買頂級模型就萬事大吉", "以為只要買最新 AI 介面就能自動變聰明，完全忽略自家底層資料還沒打通。"),
        ("中層情境：把矛盾舊檔直接倒進 AI", "將各部門互打嘴巴的舊合約與未審草稿直接餵給模型，如同在流沙上蓋高樓。"),
        ("深層後果：高速放大胡說八道風險", "垃圾進必然導致垃圾出（GIGO），錯誤報價與幻覺將直接引爆財務與法律危機。")
    ],
    accent_color=COLOR_DANGER, header_tint=TINT_RED, is_spotlight=False, row_y_slots=s_3rows_y
)

create_structured_card(
    s2, left=Inches(6.65), top=Inches(1.25), width=Inches(5.883), height=Inches(5.15),
    title="【物理現實真相：混凝土底座】★",
    subtitle="乾淨統一的內部私有數據才是對手抄不走的護城河",
    rows_data=[
        ("淺層直覺：模型是引擎，數據才是汽油", "外部大模型誰都能買到；唯有經過人工審核、乾淨無誤的私有知識庫才是真正壁壘。"),
        ("中層做法：用統一字典與名冊約束 AI", "先統一全公司業務名詞（Ontology）與客戶唯一名冊（MDM），不讓 AI 自由瞎猜。"),
        ("深層價值：先在安全區練兵再全面投產", "優先切入有真人把關的客服與寫程式場景，跑通治理閉環後再擴展至核心資產。")
    ],
    accent_color=COLOR_PRIMARY, header_tint=TINT_BLUE, is_spotlight=True, row_y_slots=s_3rows_y
)

add_zone3_footer(s2, "★ 核心行動結論：立即停止拿未清洗的髒資料微調模型，將戰略資源全面轉向底層數據整理與統一標準。")
set_notes(s2, "大家看這兩張卡片的對比：流行觀點認為模型愈大愈聰明，但真實物理世界中，如果沒有高品質的內部數據，大模型只是放大了垃圾。我們必須把戰略重心從買算力，轉向做數據大掃除。")


# ==============================================================================
# SLIDE 3 [Layout S7]: 第一幕：現狀診斷 (Left Wide Chart 65% + Right 3-Tier Stack 35%)
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
bg3 = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg3.fill.solid()
bg3.fill.fore_color.rgb = BG_LIGHT
bg3.line.fill.background()

add_zone1_header(s3, "現狀診斷｜版型 S7", "企業陷入「80% 投資熱潮 vs. 6% 實際投產」斷崖，數據策略嚴重脫節", COLOR_DANGER)

chart_img_path = "reading_sessions/20261101_企業數據與生成式AI準備度/02_outputs/03_cdo_survey_quantitative_charts.png"
if os.path.exists(chart_img_path):
    # Left 65% full-height zone: width=8.32", vertically centered at top=1.48" (height=4.25")
    s3.shapes.add_picture(chart_img_path, Inches(0.42), Inches(1.48), width=Inches(8.32))

# Right 35% vertical 3-card stack (Shallow -> Medium -> Deep)
b_left = Inches(8.88)
b_card_w = Inches(3.65)
b_height = Inches(1.58)
b_tops = [Inches(1.25), Inches(3.03), Inches(4.82)]

warnings = [
    ("淺層現象：雷聲大雨點小", "80% 高層看好 AI 重塑商業，但高達 73% 停留在零星試玩，僅 6% 真正進入核心生產。", COLOR_DANGER, TINT_RED, False),
    ("中層卡關：舊資料太髒太亂", "46% 數據長坦承「數據品質不良」是頭號死穴，16% 更因害怕機密外洩與出錯而全面禁用。", COLOR_DANGER, TINT_RED, False),
    ("深層病灶：策略原地踏步 ★", "高達 57% 企業至今未對數據策略做任何調整，僅 11% 強烈同意自家數據地基已準備到位。", COLOR_DANGER, TINT_RED, True)
]

for idx, (w_tag, w_desc, w_col, w_tint, is_spot) in enumerate(warnings):
    by = b_tops[idx]
    w_card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, b_left, by, b_card_w, b_height)
    w_card.adjustments[0] = 0.05
    w_card.fill.solid()
    w_card.fill.fore_color.rgb = CARD_BG
    w_card.line.color.rgb = w_col if is_spot else CARD_BORDER
    w_card.line.width = Pt(2.2 if is_spot else 1.0)

    tf_w = w_card.text_frame
    tf_w.word_wrap = True
    tf_w.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_w.margin_left = tf_w.margin_right = Inches(0.20)
    tf_w.margin_top = tf_w.margin_bottom = Inches(0.10)

    p1 = tf_w.paragraphs[0]
    p1.text = f"● 【{w_tag}】"
    p1.alignment = PP_ALIGN.CENTER
    p1.font.name = "Microsoft JhengHei"
    p1.font.size = Pt(11.5)
    p1.font.bold = True
    p1.font.color.rgb = w_col
    p1.space_after = Pt(5)

    p2 = tf_w.add_paragraph()
    p2.text = w_desc
    p2.alignment = PP_ALIGN.CENTER
    p2.font.name = "Microsoft JhengHei"
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_BODY
    p2.line_spacing = 1.35

add_zone3_footer(s3, "★ 戰略警示：局部試玩（POC）無法產生規模經濟價值，跳過數據大掃除是擋在 94% 企業門口的唯一高牆。")
set_notes(s3, "請看上方圖表：80% 的變革期望與 6% 的生產落地形成了刺眼的斷崖！下方三張卡片按照由淺入深總結了三大警訊：表層是雷聲大雨點小，中層是舊資料太髒，深層則是 57% 公司根本還沒調整數據策略。")


# ==============================================================================
# SLIDE 4 [Layout S2]: 第一幕：病因剖析 (Three Pillars + 1 Spotlight, 3 Shallow-to-Deep Rows)
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
bg4 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg4.fill.solid()
bg4.fill.fore_color.rgb = BG_LIGHT
bg4.line.fill.background()

add_zone1_header(s4, "病因剖析｜版型 S2", "46% 認證數據品質為頭號死穴：舊檔過期、暗數據暴增與跨部門名詞打架", COLOR_WARN)

s4_card_w = Inches(3.644)

create_structured_card(
    s4, left=Inches(0.8), top=Inches(1.25), width=s4_card_w, height=Inches(5.15),
    title="【痛點一：舊檔案過期沒人清】",
    subtitle="歷史資料夾塞滿失效法規與草稿",
    rows_data=[
        ("淺層現象：過期與正式版混雜", "公司歷年資料夾塞滿過期促銷、失效連結與未審核草稿，從未定期淘汰。"),
        ("中層情境：AI 新舊不分全盤照收", "AI 讀檔時無法分辨哪份才是今年最新規定，把十年前廢止條款當成聖旨。"),
        ("深層風險：46% 主管認定的頭號死穴", "高達 46% 數據長指認基礎品質不良為最大阻礙，髒資料直接癱瘓上線進度。")
    ],
    accent_color=COLOR_WARN, header_tint=TINT_AMBER, is_spotlight=False, row_y_slots=s_3rows_y
)

create_structured_card(
    s4, left=Inches(4.844), top=Inches(1.25), width=s4_card_w, height=Inches(5.15),
    title="【痛點二：文字影音暗數據暴增】",
    subtitle="80%~90% 非表格資料像無底洞累積",
    rows_data=[
        ("淺層現象：每天暴增海量會議與錄音", "企業 80% 以上資料不是整齊表格，而是客訴錄音、合約、郵件與會議紀錄。"),
        ("中層情境：人工整理像烏龜追高鐵", "非結構化資料每年以 50% 以上速度暴增，傳統人工貼標籤永遠追不上產生速度。"),
        ("深層風險：沉澱為拖垮轉型的數據債", "未整理的暗數據越積越多，不僅無法發揮高維語境價值，更成為資安與合規黑洞。")
    ],
    accent_color=COLOR_WARN, header_tint=TINT_AMBER, is_spotlight=False, row_y_slots=s_3rows_y
)

create_structured_card(
    s4, left=Inches(8.888), top=Inches(1.25), width=s4_card_w, height=Inches(5.15),
    title="【痛點三：各部門名詞打架】★",
    subtitle="大模型天生沒有分辨誰對誰錯的能力",
    rows_data=[
        ("淺層現象：同一客戶各部門叫法不同", "A 部門寫「台積電」、B 部門寫「TSMC」、C 部門寫「3 奈米專案」，信用額度還互異。"),
        ("中層情境：AI 遇到矛盾只能隨機瞎猜", "大語言模型本質是「文字接龍機」，看到兩份衝突報表時只會隨機拼湊或自己腦補。"),
        ("深層風險：缺乏單一權威名冊必崩盤", "若不在模型外部建立「單一真實來源（MDM）」，微小矛盾將被 AI 自動化放大。")
    ],
    accent_color=COLOR_PRIMARY, header_tint=TINT_BLUE, is_spotlight=True, row_y_slots=s_3rows_y
)

add_zone3_footer(s4, "★ 系統鐵律：大語言模型沒有分辨真假事實的裁判能力，企業必須在模型外部建立唯一權威名冊。")
set_notes(s4, "很多人問：大模型不是很聰明嗎？為什麼不能直接把所有內部文檔灌給它？答案在於第三張聚光燈卡片：當不同部門對同一個客戶或指標各寫各的，AI 根本不知道誰才是對的，只會隨機瞎猜。")


# ==============================================================================
# SLIDE 5 [Layout S6]: 第二幕：理論極限 (Equation Anatomy + 3 Downward Pointer Arrows + 3 Cards)
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
bg5 = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg5.fill.solid()
bg5.fill.fore_color.rgb = BG_LIGHT
bg5.line.fill.background()

add_zone1_header(s5, "理論極限｜版型 S6", "為什麼不能只靠寫提示詞（Prompt）解決？三大底層限制讓規則必然破功", COLOR_WARN)

eq_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.22), Inches(11.733), Inches(1.18))
eq_card.adjustments[0] = 0.04
eq_card.fill.solid()
eq_card.fill.fore_color.rgb = DARK_HUB_BG
eq_card.line.color.rgb = DARK_HUB_SUB
eq_card.line.width = Pt(1.5)
tf_eq = eq_card.text_frame
tf_eq.vertical_anchor = MSO_ANCHOR.MIDDLE
p_eq1 = tf_eq.paragraphs[0]
p_eq1.text = "【非結構化數據剪刀差與數據債累積定律（Formula Anatomy）】"
p_eq1.alignment = PP_ALIGN.CENTER
p_eq1.font.name = "Microsoft JhengHei"
p_eq1.font.size = Pt(10.5)
p_eq1.font.color.rgb = DARK_HUB_SUB
p_eq1.font.bold = True
p_eq2 = tf_eq.add_paragraph()
p_eq2.text = "數據債累積 Data Debt (t)  =  ∫ [  暗數據指數爆炸 α·exp(λτ)   −   ( 人工線性整理 β·M  +  AI 治理通量 γ·I_MDM )  ] dτ"
p_eq2.alignment = PP_ALIGN.CENTER
p_eq2.font.name = "Microsoft JhengHei"
p_eq2.font.size = Pt(13.5)
p_eq2.font.color.rgb = RGBColor(255, 255, 255)
p_eq2.font.bold = True

# 3 Native Vector Downward Pointer Arrows (Connecting Equation Box to the 3 Cards)
for idx, arrow_col in enumerate([COLOR_WARN, COLOR_WARN, COLOR_DANGER]):
    center_x = Inches(0.8 + idx * 4.044 + 1.822)
    arr = s5.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, center_x - Inches(0.18), Inches(2.43), Inches(0.36), Inches(0.28))
    arr.fill.solid()
    arr.fill.fore_color.rgb = arrow_col
    arr.line.fill.background()

s5_3rows_y = [
    (Inches(3.48), Inches(0.92)),
    (Inches(4.46), Inches(0.92)),
    (Inches(5.44), Inches(0.92)),
]

create_structured_card(
    s5, left=Inches(0.8), top=Inches(2.74), width=s4_card_w, height=Inches(3.72),
    title="【1. 資料爆炸 vs. 人工烏龜爬】",
    subtitle="對應公式左項：α·exp(λt) 遠大於 β·M",
    rows_data=[
        ("淺層現象：資料倍增、人力固定", "公司影音與文檔呈指數爆炸，但人工審核團隊永遠只能線性慢爬。"),
        ("中層情境：硬壓成表格反而失真", "若強行把客訴錄音壓成「退貨/負評」死板表格，會抹殺語氣急迫度與訴訟警訊。"),
        ("深層結論：必須靠 AI 協助貼標籤", "不能只靠人工，但 AI 貼標籤的前提是底層必須先有統一標準（I_MDM → 1）。")
    ],
    accent_color=COLOR_WARN, header_tint=TINT_AMBER, is_spotlight=False,
    row_y_slots=s5_3rows_y, hdr_h=Inches(0.64), tag_pt=10.2, desc_pt=9.2
)

create_structured_card(
    s5, left=Inches(4.844), top=Inches(2.74), width=s4_card_w, height=Inches(3.72),
    title="【2. 老師傅的潛規則寫不完】",
    subtitle="波蘭尼悖論：我們懂的比寫出來的多",
    rows_data=[
        ("淺層直覺：就像騎單車很難靠文字教", "老員工看一眼合約就知道哪裡有貓膩，但要他寫成死規則卻永遠寫不全。"),
        ("中層情境：提示詞寫越長越互相打架", "企圖在 Prompt 塞入上千條例外規則，只會讓指令前後矛盾、徹底失靈。"),
        ("深層結論：範例只能處理 80% 常態", "少樣本提示（Few-Shot）只能覆蓋常見案件，絕對無法取代外部知識庫。")
    ],
    accent_color=COLOR_WARN, header_tint=TINT_AMBER, is_spotlight=False,
    row_y_slots=s5_3rows_y, hdr_h=Inches(0.64), tag_pt=10.2, desc_pt=9.2
)

create_structured_card(
    s5, left=Inches(8.888), top=Inches(2.74), width=s4_card_w, height=Inches(3.72),
    title="【3. 遇到罕見特例會自信瞎掰】★",
    subtitle="長尾案例引發最危險的「偽陽性錯誤」",
    rows_data=[
        ("淺層現象：AI 不懂裝懂最可怕", "遇到沒見過的 20% 特殊合約條款，AI 不會舉手說不懂，而是硬套常規模板。"),
        ("中層情境：表面格式完美、內容全錯", "產出看似專業工整、實則把豁免條款完全寫反的致命報表，讓人失去戒心。"),
        ("深層結論：必須設「真人裁判安全網」", "一旦 AI 把握度低於 90% 或跨檔矛盾，必須強制攔截交由真人專家拍板！")
    ],
    accent_color=COLOR_DANGER, header_tint=TINT_RED, is_spotlight=True,
    row_y_slots=s5_3rows_y, hdr_h=Inches(0.64), tag_pt=10.2, desc_pt=9.2
)

add_zone3_footer(s5, "★ 工程結論：放棄「把所有規則塞進 Prompt」的幻想，唯有建立外部統一字典與真人攔截網才能根除瞎掰。")
set_notes(s5, "大家常想：既然 AI 會出錯，那我們把提示詞寫得無比詳細不就好了嗎？這頁上方的公式與下方的三支箭頭說明了為什麼這條路走不通：老師傅的默會經驗寫不進提示詞，而且遇到罕見特例時 AI 會自信滿滿地胡說八道。")


# ==============================================================================
# SLIDE 6 [Layout S4]: 第二幕：系統架構 (TRUE S4 Interactive System Loop / Bicameral Architecture)
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
bg6 = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg6.fill.solid()
bg6.fill.fore_color.rgb = BG_LIGHT
bg6.line.fill.background()

add_zone1_header(s6, "系統架構｜版型 S4", "打造「左腦管標準 ＋ 右腦讀語境 ＋ 中間安全網把關」三層雙腦協同系統", COLOR_SUCCESS)

# 1. TOP CENTRAL HUB: Prefrontal Human-in-the-Loop Gate (S4 System Hub)
hub_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.22), Inches(11.733), Inches(1.22))
hub_box.adjustments[0] = 0.04
hub_box.fill.solid()
hub_box.fill.fore_color.rgb = TINT_GREEN
hub_box.line.color.rgb = COLOR_SUCCESS
hub_box.line.width = Pt(2.2)

tf_hub = hub_box.text_frame
tf_hub.word_wrap = True
tf_hub.vertical_anchor = MSO_ANCHOR.TOP
tf_hub.margin_top = Inches(0.08)
tf_hub.margin_left = tf_hub.margin_right = Inches(0.20)
p_hb = tf_hub.paragraphs[0]
p_hb.text = "★【中間安全網：AI 自動對帳 ＋ 5% 真人專家把關迴路 (Human-in-the-Loop Gate)】"
p_hb.alignment = PP_ALIGN.CENTER
p_hb.font.name = "Microsoft JhengHei"
p_hb.font.size = Pt(12.0)
p_hb.font.bold = True
p_hb.font.color.rgb = COLOR_SUCCESS

# Two internal sub-pills inside Top Hub
for sub_idx, (sub_title, sub_desc) in enumerate([
    ("① 95% 常態案件：AI 自動對帳秒速放行", "右腦讀出的重點若與左腦字典完全吻合，系統自動入庫，兼顧萬篇級高效率。"),
    ("② < 5% 模糊與矛盾特例：攔截由真人專家拍板", "一旦發現跨檔案數字打架或把握度不足，強制轉交人類專家裁決並同步更新字典。")
]):
    sx = Inches(0.98 + sub_idx * 5.76)
    s_panel = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx, Inches(1.62), Inches(5.60), Inches(0.72))
    s_panel.adjustments[0] = 0.05
    s_panel.fill.solid()
    s_panel.fill.fore_color.rgb = CARD_BG
    s_panel.line.color.rgb = COLOR_SUCCESS
    s_panel.line.width = Pt(1.0)
    tf_sp = s_panel.text_frame
    tf_sp.word_wrap = True
    tf_sp.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_sp.margin_left = tf_sp.margin_right = Inches(0.14)
    p_s1 = tf_sp.paragraphs[0]
    p_s1.text = f"● {sub_title}"
    p_s1.font.name = "Microsoft JhengHei"
    p_s1.font.size = Pt(10.2)
    p_s1.font.bold = True
    p_s1.font.color.rgb = COLOR_SUCCESS
    p_s2 = tf_sp.add_paragraph()
    p_s2.text = sub_desc
    p_s2.font.name = "Microsoft JhengHei"
    p_s2.font.size = Pt(9.2)
    p_s2.font.color.rgb = TEXT_BODY

# 2. MIDDLE BIDIRECTIONAL SYSTEM CONNECTORS (y = 2.48" to 2.80")
for c_idx, (conn_text, conn_col, conn_tint) in enumerate([
    ("▼ 權威規則下發：左腦提供 100% 標準字典與唯一名冊", COLOR_PRIMARY, TINT_BLUE),
    ("▲ 異常攔截與反哺：右腦抽取衝突升級專家、越用越聰明", COLOR_WARN, TINT_AMBER)
]):
    cx = Inches(1.15 + c_idx * 6.05)
    c_pill = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, Inches(2.49), Inches(5.00), Inches(0.30))
    c_pill.adjustments[0] = 0.3
    c_pill.fill.solid()
    c_pill.fill.fore_color.rgb = conn_tint
    c_pill.line.color.rgb = conn_col
    c_pill.line.width = Pt(1.1)
    tf_cp2 = c_pill.text_frame
    tf_cp2.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_cp2 = tf_cp2.paragraphs[0]
    p_cp2.text = conn_text
    p_cp2.alignment = PP_ALIGN.CENTER
    p_cp2.font.name = "Microsoft JhengHei"
    p_cp2.font.size = Pt(9.5)
    p_cp2.font.bold = True
    p_cp2.font.color.rgb = conn_col

# 3. BOTTOM OPPOSING BICAMERAL MODULES + CENTER BRIDGE (y = 2.84" to 6.46")
s6_bot_rows_y = [
    (Inches(3.56), Inches(0.90)),
    (Inches(4.52), Inches(0.90)),
    (Inches(5.48), Inches(0.90)),
]

create_structured_card(
    s6, left=Inches(0.8), top=Inches(2.84), width=Inches(5.35), height=Inches(3.62),
    title="【剛性左腦：100% 確定性統一字典與名冊】",
    subtitle="扮演企業事實憲法，保證零幻覺與單一口徑",
    rows_data=[
        ("第 1 層（淺）：全公司統一字典 (Ontology)", "硬性規定「毛利率、活躍客戶」唯一算法，禁止各部門自創名詞。"),
        ("第 2 層（中）：單一權威名冊 (MDM)", "把「台積電 / TSMC」綁定同一客戶編號，鎖定全公司唯一最新事實版本。"),
        ("第 3 層（深）：檔案健康身分證 (Data Fabric)", "為每份檔案貼上有效期限与可信度分數，自動淘汰過期草稿。")
    ],
    accent_color=COLOR_PRIMARY, header_tint=TINT_BLUE, is_spotlight=False,
    row_y_slots=s6_bot_rows_y, hdr_h=Inches(0.62), tag_pt=10.2, desc_pt=9.2
)

# Center Horizontal Bridge Badge between Left & Right Brain
bridge = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.23), Inches(4.15), Inches(0.87), Inches(1.10))
bridge.adjustments[0] = 0.15
bridge.fill.solid()
bridge.fill.fore_color.rgb = DARK_HUB_BG
bridge.line.color.rgb = DARK_HUB_SUB
bridge.line.width = Pt(1.5)
tf_br = bridge.text_frame
tf_br.word_wrap = True
tf_br.vertical_anchor = MSO_ANCHOR.MIDDLE
tf_br.margin_left = tf_br.margin_right = Inches(0.05)
p_br = tf_br.paragraphs[0]
p_br.text = "雙向\n校驗\n◄═►\n實體\n對齊"
p_br.alignment = PP_ALIGN.CENTER
p_br.font.name = "Microsoft JhengHei"
p_br.font.size = Pt(9.5)
p_br.font.bold = True
p_br.font.color.rgb = DARK_HUB_SUB

create_structured_card(
    s6, left=Inches(7.18), top=Inches(2.84), width=Inches(5.35), height=Inches(3.62),
    title="【靈活右腦：AI 語義理解與重點雷達】",
    subtitle="負責讀懂海量長文語境，但受左腦字典嚴格約束",
    rows_data=[
        ("第 1 層（淺）：讀懂長篇合約與錄音情緒", "保留高維語義向量（Embeddings），直接聽出客訴錄音裡的焦急與訴訟警訊。"),
        ("第 2 層（中）：照著左腦字典自動貼標籤", "不准自己發明新欄位，只能乖乖按照左腦規定的標準格子抽取重點。"),
        ("第 3 層（深）：圖譜約束檢索 (GraphRAG)", "回答問題時強制鎖定左腦審核過的知識庫，徹底根除憑空捏造。")
    ],
    accent_color=COLOR_WARN, header_tint=TINT_AMBER, is_spotlight=False,
    row_y_slots=s6_bot_rows_y, hdr_h=Inches(0.62), tag_pt=10.2, desc_pt=9.2
)

add_zone3_footer(s6, "★ 架構守則：左腦立規矩保精準、右腦讀長文保效率、中間真人專家管 5% 特例，形成越用越聰明的治理飛輪。")
set_notes(s6, "為了避免跟第 4 頁的三欄卡視覺重複，這頁以版型 S4 完整呈現三層雙腦協同系統：上方是中間安全網（95% 自動放行、5% 真人專家把關），下方左右分別是剛性左腦與靈活右腦，中間透過雙向校驗橋樑即時對齊。")


# ==============================================================================
# SLIDE 7 [Layout S1]: 第三幕：標竿實證 (Asymmetric Contrast: Morgan Stanley vs Quicksand)
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
bg7 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg7.fill.solid()
bg7.fill.fore_color.rgb = BG_LIGHT
bg7.line.fill.background()

add_zone1_header(s7, "標竿實證｜版型 S1", "摩根士丹利靠「5 年人工策劃」打下混凝土地基，盲目微調髒資料必遭反噬", COLOR_SUCCESS)

create_structured_card(
    s7, left=Inches(0.8), top=Inches(1.25), width=Inches(5.85), height=Inches(5.15),
    title="【成功典範：摩根士丹利與默克藥廠】★",
    subtitle="先花數年整理乾淨知識庫，才讓 GPT-4 安全上線",
    rows_data=[
        ("淺層做法：專人逐篇審核打分數", "摩根士丹利在 AI 爆發前 5 年就組建專責團隊，為內部研究報告逐篇審核並標記品質分數。"),
        ("中層基建：打造混凝土地基 (Data Fabric)", "默克（Merck）與賽諾菲建立統一數據經緯，自動剔除過期政策並鎖定權威來源。"),
        ("深層成果：萬名顧問零事故投入生產", "成為全球少數成功將生成式 AI 部署至財富管理核心業務、且達成零重大合規事故的標竿。")
    ],
    accent_color=COLOR_SUCCESS, header_tint=TINT_GREEN, is_spotlight=True, row_y_slots=s_3rows_y
)

create_structured_card(
    s7, left=Inches(6.883), top=Inches(1.25), width=Inches(5.65), height=Inches(5.15),
    title="【反面警示：跳過清理、盲目微調流沙】",
    subtitle="把未整理的歷史髒資料直接拿去訓練模型",
    rows_data=[
        ("淺層誤區：迷信「丟進模型微調就會好」", "不願花時間做數據大掃除，直接把歷年混亂的對話紀錄與草稿灌入開源模型微調。"),
        ("中層災難：AI 學會過期報價與錯誤習慣", "模型把十年前的過期折扣當成常態，對客戶給出違規承諾並觸發法律賠償訴訟。"),
        ("深層崩潰：陷入「模型自噬」越訓越笨", "AI 產生的錯誤內容又流回資料庫再次訓練（Model Autophagy），導致系統智商雪崩退化。")
    ],
    accent_color=COLOR_DANGER, header_tint=TINT_RED, is_spotlight=False, row_y_slots=s_3rows_y
)

add_zone3_footer(s7, "★ 實證教訓：生成式 AI 的成敗不看演算法多新潮，而看數據長（CDO）與業務專家有沒有做好底層大掃除。")
set_notes(s7, "摩根士丹利能成為全球第一個把 GPT-4 成功放進財富管理生產環境的機構，不是因為他們比別人更懂寫提示詞，而是他們五年前就開始逐篇審核打分內部報告。默克集團數據長強調：地基必須是混凝土，不能是流沙。")


# ==============================================================================
# SLIDE 8 [Layout S3]: 第四幕：落地路線 (4-Step Horizontal Pipeline + Vector Progression Arrows)
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
bg8 = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg8.fill.solid()
bg8.fill.fore_color.rgb = BG_LIGHT
bg8.line.fill.background()

add_zone1_header(s8, "落地路線｜版型 S3", "破除 71% 觀望僵局：先從「客服與寫程式」安全試點，再分四步擴展全公司", COLOR_PRIMARY)

step_w = Inches(2.68)
step_gap = Inches(0.337)
s8_3rows_y = [
    (Inches(2.12), Inches(1.30)),
    (Inches(3.52), Inches(1.30)),
    (Inches(4.92), Inches(1.30)),
]

stages = [
    (
        "Stage 01 (1~3月)\n【盤點與止血】", "先鎖定高價值資料並統一詞彙",
        [
            ("淺層目標：摸清家底", "盤點公司最有價值的文本與錄音，淘汰失效連結（對標 18% 先行者）。"),
            ("具體動作：編第一本字典", "召集業務與 IT 編纂首部《統一業務名詞字典》，立即叫停髒資料微調。"),
            ("驗收價值：止住數據債", "終結各部門自創名詞亂象，為後續試點準備好乾淨的標準尺規。")
        ],
        TEXT_NAVY, TINT_SLATE, False
    ),
    (
        "Stage 02 (3~6月)\n【★ 安全區試點】", "先挑有安全網的客服與寫程式",
        [
            ("淺層目標：零風險見效", "避開高風險財務與醫療決策，先挑自帶安全網的兩大場景練兵。"),
            ("具體動作：客服＋寫程式", "客服由真人坐席看過才發送（天然把關）；寫程式有編譯器一秒抓錯。"),
            ("驗收價值：打消高層觀望", "90 天內安全縮短 30% 處理時間，用真實戰果打破 71% 組織觀望僵局。")
        ],
        COLOR_PRIMARY, TINT_BLUE, True
    ),
    (
        "Stage 03 (6~12月)\n【打通數據經緯】", "跨部門身分證與單一權威名冊",
        [
            ("淺層目標：跨系統連通", "將安全試點驗證成功的治理流程，擴展為跨部門共享的數據高速公路。"),
            ("具體動作：上線 MDM 與標籤", "全面推行檔案健康身分證（時效/可信度），打通 ERP 與向量資料庫。"),
            ("驗收價值：消滅資料孤島", "讓 AI 在全公司範圍內都能查到唯一權威事實，攔截率穩定控制在 <5%。")
        ],
        TEXT_NAVY, TINT_SLATE, False
    ),
    (
        "Stage 04 (12~18月)\n【核心全面投產】", "複製至研發與核心資產築起壁壘",
        [
            ("淺層目標：跨越 6% 鴻溝", "將成熟的「雙腦協同＋真人把關」架構正式推進高價值核心業務。"),
            ("具體動作：賦能研發與財管", "導入新產品研發、供應鏈預測與財富管理，實現規模化自動運轉。"),
            ("驗收價值：混凝土地基護城河", "把累積數十年的內部暗數據轉化為競爭對手無法複製的商業壁壘。")
        ],
        COLOR_SUCCESS, TINT_GREEN, False
    )
]

for idx, (st_title, st_sub, st_rows, st_col, st_tint, st_spot) in enumerate(stages):
    sx = Inches(0.80 + idx * (2.68 + 0.337))
    create_structured_card(
        s8, left=sx, top=Inches(1.25), width=step_w, height=Inches(5.15),
        title=st_title, subtitle=st_sub, rows_data=st_rows,
        accent_color=st_col, header_tint=st_tint, is_spotlight=st_spot,
        row_y_slots=s8_3rows_y, tag_pt=10.0, desc_pt=9.0
    )
    # Draw Native Vector Progression Arrow between stages
    if idx < 3:
        arr_x = sx + step_w + Inches(0.04)
        arr = s8.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, arr_x, Inches(3.65), Inches(0.257), Inches(0.32))
        arr.fill.solid()
        arr.fill.fore_color.rgb = COLOR_PRIMARY if idx in (0, 1) else TEXT_MUTED
        arr.line.fill.background()

add_zone3_footer(s8, "★ 破局秘訣：不要一開始就拿核心命脈冒險！先在「客服與寫程式」安全區跑通飛輪，再複製到全公司。")
set_notes(s8, "面對 71% 數據長觀望與權力爭奪，我們該怎麼破局？這頁 S3 四步階梯流程圖給出了最務實的路線：第 2 步先做客服輔助和寫程式！因為客服有真人坐席把關，寫程式有編譯器自動抓錯，跑通後再推進到第 3、第 4 步。")


# ==============================================================================
# SLIDE 9 [Layout S0]: 終幕：峰終收斂 (Dark Bookend Closing & Monday Action)
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
bg9 = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg9.fill.solid()
bg9.fill.fore_color.rgb = DARK_HUB_BG
bg9.line.fill.background()

add_zone1_header(s9, "終幕收斂｜版型 S0", "以混凝土地基贏得企業 AI 持久戰，星期一即刻啟動跨部門數據治理", DARK_HUB_SUB, is_dark_slide=True)

create_structured_card(
    s9, left=Inches(0.8), top=Inches(1.25), width=Inches(5.7), height=Inches(5.15),
    title="【董事會三大黃金決策鐵律】★",
    subtitle="終結流沙幻想，打牢企業長青之混凝土地基",
    rows_data=[
        ("鐵律一：數據大掃除不是事後補丁", "大模型只是引擎，乾淨、統一且標明有效期限的內部知識庫才是真正的燃料。"),
        ("鐵律二：左腦規矩與右腦理解缺一不可", "用左腦統一字典與名冊約束右腦大模型，並保留 5% 真人專家把關罕見特例。"),
        ("鐵律三：先從自帶安全網的場景試點", "從真人把關的客服與編譯器把關的寫程式切入，90 天跑通治理飛輪再擴展。")
    ],
    accent_color=DARK_HUB_SUB, is_spotlight=True, is_dark_slide=True, row_y_slots=s_3rows_y
)

create_structured_card(
    s9, left=Inches(6.833), top=Inches(1.25), width=Inches(5.7), height=Inches(5.15),
    title="【星期一立即行動清單 (Monday Action)】★",
    subtitle="將戰略共識轉化為可追蹤、可驗收的落地動作",
    rows_data=[
        ("行動一：成立跨部門數據治理小組", "召開數據長（CDO）、資訊長（CIO）與業務主管聯席會，終結多頭馬車內耗。"),
        ("行動二：立即叫停未清洗資料之微調", "全面凍結把未審核歷史檔案直接丟進模型微調的專案，防止錯誤規則寫死。"),
        ("行動三：啟動首部字典與 90 天試點", "指派業務專家於 60 天內編出首部統一詞庫，同步立項客服或寫程式試點。")
    ],
    accent_color=RGBColor(16, 185, 129), is_spotlight=True, is_dark_slide=True, row_y_slots=s_3rows_y
)

add_zone3_footer(s9, "★ 終極結語：大型企業把數據準備到位需耗時數年，而該起身行動的時刻，就是現在！", is_dark_slide=True)
set_notes(s9, "各位長官，生成式 AI 的競爭不是比誰買了更多算力，而是比誰的數據準備度更高。想讓大型企業的重要數據準備好，需要花費數年時間；而該起身動作的時刻，就是現在。謝謝大家！")


output_pptx = os.path.abspath("reading_sessions/20261101_企業數據與生成式AI準備度/02_outputs/02_executive_presentation.pptx")
prs.save(output_pptx)
print(f"[OK] Publication-grade PowerPoint saved to: {output_pptx}")
