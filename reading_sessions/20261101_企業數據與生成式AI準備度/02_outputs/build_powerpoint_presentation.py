"""
build_powerpoint_presentation.py
Builds the 16:9 widescreen PowerPoint deck (02_executive_presentation.pptx)
following Alley & Neeley (2005) Assertion-Evidence Architecture,
Kosslyn (2007) layouts, and Knaflic (2015) 80/20 preattentive spotlight.
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
BG_WHITE = RGBColor(248, 250, 252)       # #F8FAFC
TEXT_NAVY = RGBColor(15, 23, 42)         # #0F172A
TEXT_MUTED = RGBColor(100, 116, 139)     # #64748B
TEXT_BODY = RGBColor(51, 65, 85)         # #334155
CARD_BG = RGBColor(255, 255, 255)        # Pure White
CARD_BORDER = RGBColor(203, 213, 225)    # #CBD5E1

COLOR_PRIMARY = RGBColor(30, 64, 175)    # Royal Blue
COLOR_DANGER = RGBColor(190, 18, 60)     # Crimson Red
COLOR_WARN = RGBColor(180, 83, 9)        # Amber Warm
COLOR_SUCCESS = RGBColor(4, 120, 87)     # Emerald Green
PILL_BG = RGBColor(238, 242, 255)        # Soft Blue tint

DARK_HUB_BG = RGBColor(15, 23, 42)       # #0F172A
DARK_HUB_SUB = RGBColor(56, 189, 248)    # Sky blue

def add_zone1_header(slide, pill_text, headline_text, accent_color=COLOR_PRIMARY):
    """Draws Zone 1: Chapter navigation pill & sentence assertion headline."""
    # Pill box
    pill_w = Inches(len(pill_text) * 0.17 + 0.35)
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.28), pill_w, Inches(0.32))
    pill.fill.solid()
    pill.fill.fore_color.rgb = PILL_BG
    pill.line.color.rgb = accent_color
    pill.line.width = Pt(1.2)
    tf_p = pill.text_frame
    tf_p.word_wrap = False
    tf_p.margin_left = tf_p.margin_right = tf_p.margin_top = tf_p.margin_bottom = 0
    p = tf_p.paragraphs[0]
    p.text = pill_text
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Microsoft JhengHei"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = accent_color

    # Headline Box
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.733), Inches(0.55))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p2 = tf.paragraphs[0]
    p2.text = headline_text
    p2.font.name = "Microsoft JhengHei"
    p2.font.size = Pt(17.5)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_NAVY

def add_zone3_footer(slide, takeaway_text):
    """Draws Zone 3: Bottom action takeaway banner."""
    footer = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.72), Inches(11.733), Inches(0.52))
    footer.fill.solid()
    footer.fill.fore_color.rgb = DARK_HUB_BG
    footer.line.color.rgb = DARK_HUB_SUB
    footer.line.width = Pt(1.2)
    tf = footer.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = takeaway_text
    p.font.name = "Microsoft JhengHei"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = RGBColor(248, 250, 252)

def set_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text


# ------------------------------------------------------------------------------
# SLIDE 1: COVER / CORE THESIS
# ------------------------------------------------------------------------------
s1 = prs.slides.add_slide(blank_layout)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg1.fill.solid()
bg1.fill.fore_color.rgb = BG_WHITE
bg1.line.fill.background()

add_zone1_header(s1, "戰略定錨", "生成式 AI 的企業壁壘並非模型算力，而是內部私有數據資產的治理深度與一致性", COLOR_PRIMARY)

# Main Card Left (Myth)
c_left = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(5.6), Inches(4.85))
c_left.fill.solid()
c_left.fill.fore_color.rgb = CARD_BG
c_left.line.color.rgb = CARD_BORDER
c_left.line.width = Pt(1.5)
tf_l = c_left.text_frame
tf_l.margin_left = tf_l.margin_right = Inches(0.35)
tf_l.margin_top = Inches(0.4)
p = tf_l.paragraphs[0]
p.text = "【流行技術迷思】"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_DANGER
p2 = tf_l.add_paragraph()
p2.text = "\n● 以為只要採購最新大語言模型 API 或開源模型微調，企業就能自動完成智慧升級。\n\n● 以為資料量愈多愈好，將未經清洗、互相矛盾的內部歷史文檔一股腦餵給 AI。\n\n● 結果：模型充斥幻覺與自相矛盾，引發嚴重的合規與業務決策危機。"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(11.5)
p2.font.color.rgb = TEXT_BODY

# Main Card Right (Reality / Spotlight)
c_right = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.55), Inches(5.733), Inches(4.85))
c_right.fill.solid()
c_right.fill.fore_color.rgb = CARD_BG
c_right.line.color.rgb = COLOR_PRIMARY
c_right.line.width = Pt(2.5)
tf_r = c_right.text_frame
tf_r.margin_left = tf_r.margin_right = Inches(0.35)
tf_r.margin_top = Inches(0.4)
p = tf_r.paragraphs[0]
p.text = "【真實物理現實】★ 破局關鍵"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY
p2 = tf_r.add_paragraph()
p2.text = "\n● 大模型只是燃油，經過治理的高品質數據資產才是引擎（地基必須是混凝土，而非流沙）。\n\n● 必須建立「雙腦分層架構」：剛性左腦（主數據管理 MDM 與受控本體庫）約束靈性右腦（LLM）。\n\n● 採行非對稱 MVP 策略：優先切入客服與程式碼生成，在低敏感安全區跑通人機協同。"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(11.5)
p2.font.color.rgb = TEXT_BODY

add_zone3_footer(s1, "★ 核心行動結論：停止盲目微調未清洗之歷史數據，將戰略重心轉向底層數據準備度與主數據治理。")
set_notes(s1, "各位董事與技術主管，今天我們不談虛幻的模型參數，我們談最殘酷的商業現實。所有人都以為生成式 AI 只要買 API 就能帶來生產力暴增，但最新 MIT Sloan 調查揭示：80% 企業躍躍欲試，但真正進入生產環境的只有 6%。今天我們拆解如何把這片流沙打造成混凝土。")


# ------------------------------------------------------------------------------
# SLIDE 2: 80% HYPE VS 6% PRODUCTION GAP
# ------------------------------------------------------------------------------
s2 = prs.slides.add_slide(blank_layout)
bg2 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg2.fill.solid()
bg2.fill.fore_color.rgb = BG_WHITE
bg2.line.fill.background()

add_zone1_header(s2, "現狀診斷", "企業陷入「80% 投資熱潮 vs. 6% 生產落地」的巨大斷崖，57% 數據策略處於完全真空", COLOR_DANGER)

# Card 1 Left (Hype)
c1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(5.4), Inches(4.85))
c1.fill.solid()
c1.fill.fore_color.rgb = CARD_BG
c1.line.color.rgb = CARD_BORDER
c1.line.width = Pt(1.5)
tf = c1.text_frame
tf.margin_left = tf.margin_right = Inches(0.3)
tf.margin_top = Inches(0.35)
p = tf.paragraphs[0]
p.text = "【80% 熱潮表象 (Hype)】"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY
p2 = tf.add_paragraph()
p2.text = "\n● 高達 80% 數據長 (CDO) 認為生成式 AI 將徹底顛覆產業格局。\n\n● 62% 企業計畫實質增加生成式 AI 的專案與算力預算。\n\n● 高層管理團隊與董事會熱情推動各類概念驗證 (POC)。"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(11.5)
p2.font.color.rgb = TEXT_BODY

# Card 2 Right (Reality Spotlight)
c2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.6), Inches(1.55), Inches(5.933), Inches(4.85))
c2.fill.solid()
c2.fill.fore_color.rgb = CARD_BG
c2.line.color.rgb = COLOR_DANGER
c2.line.width = Pt(2.5)
tf2 = c2.text_frame
tf2.margin_left = tf2.margin_right = Inches(0.3)
tf2.margin_top = Inches(0.35)
p = tf2.paragraphs[0]
p.text = "【6% 生產落地殘局 (Reality)】★ 核心瓶頸"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_DANGER
p2 = tf2.add_paragraph()
p2.text = "\n● 僅 6% 企業真正將生成式 AI 部署至核心業務生產環境。\n\n● 16% 企業甚至下達員工全面禁用令（防範數據洩漏與法規風險）。\n\n● 57% 企業至今「未對數據策略做出任何修改」，僅 11% 強烈同意數據基礎已就緒。"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(11.5)
p2.font.color.rgb = TEXT_BODY

add_zone3_footer(s2, "★ 戰略警示：概念驗證（POC）無法產生實質經濟價值，數據赤字是阻止跨越生產鴻溝的唯一障礙。")
set_notes(s2, "請大家看右側這組數據：6%、16%、57%。當市場在歡呼 AI 革命時，真實世界裡能把 AI 放進核心業務產生真金白銀的企業只有 6%。甚至有 16% 的公司因為數據外洩與幻覺風險下達禁令。更令人震驚的是，57% 的企業根本還沒開始動手修改他們的數據策略。這說明絕大多數企業缺乏真正的戰略底座。")


# ------------------------------------------------------------------------------
# SLIDE 3: 3 PILLARS OF BOTTLENECK
# ------------------------------------------------------------------------------
s3 = prs.slides.add_slide(blank_layout)
bg3 = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg3.fill.solid()
bg3.fill.fore_color.rgb = BG_WHITE
bg3.line.fill.background()

add_zone1_header(s3, "病因剖析", "46% 數據長認證數據品質不良為首要瓶頸，大模型天生無法自動消歧數據來源衝突", COLOR_WARN)

card_w = Inches(3.644)
# Pillar 1
p1 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), card_w, Inches(4.85))
p1.fill.solid()
p1.fill.fore_color.rgb = CARD_BG
p1.line.color.rgb = CARD_BORDER
p1.line.width = Pt(1.5)
tf = p1.text_frame
tf.margin_left = tf.margin_right = Inches(0.25)
tf.margin_top = Inches(0.3)
p = tf.paragraphs[0]
p.text = "【病因一：數據品質不良】"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_WARN
p2 = tf.add_paragraph()
p2.text = "\n● 46% CDO 直指數據品質不良是最大挑戰。\n\n● 內部文檔充滿過期政策、未審核草稿與死連結。\n\n● 缺乏權威過濾，垃圾進必然垃圾出。"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(10.5)
p2.font.color.rgb = TEXT_BODY

# Pillar 2
p2_s = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.844), Inches(1.55), card_w, Inches(4.85))
p2_s.fill.solid()
p2_s.fill.fore_color.rgb = CARD_BG
p2_s.line.color.rgb = CARD_BORDER
p2_s.line.width = Pt(1.5)
tf = p2_s.text_frame
tf.margin_left = tf.margin_right = Inches(0.25)
tf.margin_top = Inches(0.3)
p = tf.paragraphs[0]
p.text = "【病因二：暗數據沼澤】"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_WARN
p2 = tf.add_paragraph()
p2.text = "\n● 80%~90% 數據為非結構化文字與錄音。\n\n● 傳統 ETL 速度遠不及數據產生速度。\n\n● 形成龐大無人敢用的技術數據債務。"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(10.5)
p2.font.color.rgb = TEXT_BODY

# Pillar 3 (Spotlight)
p3 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.888), Inches(1.55), card_w, Inches(4.85))
p3.fill.solid()
p3.fill.fore_color.rgb = CARD_BG
p3.line.color.rgb = COLOR_PRIMARY
p3.line.width = Pt(2.5)
tf = p3.text_frame
tf.margin_left = tf.margin_right = Inches(0.25)
tf.margin_top = Inches(0.3)
p = tf.paragraphs[0]
p.text = "【病因三：多源事實衝突】★ 致命死穴"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY
p2 = tf.add_paragraph()
p2.text = "\n● 大模型天生無法自動消歧數據來源矛盾。\n\n● 跨部門指標定義互斥時引發隨機腦補。\n\n● 缺乏主數據管理 (MDM)，錯誤自動化放大。"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(10.5)
p2.font.color.rgb = TEXT_BODY

add_zone3_footer(s3, "★ 系統鐵律：大語言模型不具備真理裁決力，企業必須在模型之外建立單一真實來源（SSOT）。")
set_notes(s3, "很多人問：大模型不是很聰明嗎？為什麼不能直接把所有內部文檔灌給它？答案在於第三張卡片：大語言模型天生是機率文本生成器，它完全不具備判斷跨系統衝突事實的能力。如果銷售文檔寫折扣 5%，財務系統寫折扣 8%，大模型只會隨機猜測。如果不先做主數據管理，餵給 AI 的資料愈多，決策就愈危險。")


# ------------------------------------------------------------------------------
# SLIDE 4: POLANYI'S PARADOX & THE CURSE OF RULES
# ------------------------------------------------------------------------------
s4 = prs.slides.add_slide(blank_layout)
bg4 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg4.fill.solid()
bg4.fill.fore_color.rgb = BG_WHITE
bg4.line.fill.background()

add_zone1_header(s4, "理論極限", "波蘭尼悖論證明規則無法靠 Prompt 窮盡，長尾未知情境將誘發自信的「結構性偽陽性」", COLOR_WARN)

# Equation card
eq_card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(11.733), Inches(1.6))
eq_card.fill.solid()
eq_card.fill.fore_color.rgb = DARK_HUB_BG
eq_card.line.color.rgb = DARK_HUB_SUB
eq_card.line.width = Pt(1.5)
tf = eq_card.text_frame
tf.margin_top = Inches(0.2)
p = tf.paragraphs[0]
p.text = "【非結構化數據剪刀差與債務積累模型】"
p.alignment = PP_ALIGN.CENTER
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(11)
p.font.color.rgb = DARK_HUB_SUB
p.font.bold = True
p2 = tf.add_paragraph()
p2.text = "Data Debt (t) = ∫ [ α · exp(λτ)  -  β · M(τ) ] dτ"
p2.alignment = PP_ALIGN.CENTER
p2.font.name = "Georgia"
p2.font.size = Pt(17)
p2.font.color.rgb = RGBColor(255, 255, 255)
p2.font.bold = True

# 3 Pointer cards below
pt_w = Inches(3.644)
p_titles = [
    "【1. 指數生成 vs 線性處理】",
    "【2. 波蘭尼默會知識悖論】",
    "【3. 長尾案例自信偽陽性】★"
]
p_texts = [
    "非結構化數據以幾何級數 α·exp(λt) 爆炸，而人類手寫 Prompt 與審核產能 β·M 僅為線性，剪刀差發散導致數據沼澤。",
    "「人類知道的遠比能說出來的多」。歷史文檔背後隱含大量默會情境，企圖窮盡規則只會導致規則衝突與注意力稀釋。",
    "遇到未見過的邊緣極端案例時，模型不會承認不懂，而是極度自信硬套最相近範本，產出表面工整實則顛倒的偽陽性。"
]
colors = [TEXT_NAVY, TEXT_NAVY, COLOR_DANGER]

for i in range(3):
    bx = Inches(0.8 + i * 4.044)
    c = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, Inches(3.35), pt_w, Inches(3.05))
    c.fill.solid()
    c.fill.fore_color.rgb = CARD_BG
    c.line.color.rgb = COLOR_DANGER if i == 2 else CARD_BORDER
    c.line.width = Pt(2.2 if i == 2 else 1.2)
    tf = c.text_frame
    tf.margin_left = tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = p_titles[i]
    p.font.name = "Microsoft JhengHei"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = colors[i]
    p2 = tf.add_paragraph()
    p2.text = f"\n● {p_texts[i]}"
    p2.font.name = "Microsoft JhengHei"
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = TEXT_BODY

add_zone3_footer(s4, "★ 工程結論：終結在 Prompt 裡寫長篇大論小作文的幻想，轉向建立外部受控詞表與圖譜約束。")
set_notes(s4, "大家常有一種工程直覺：既然有幻覺，那我們給模型更多範例、把規則寫得無比詳細不就行了嗎？哲學家波蘭尼早在半個世紀前就證明了這不可能。人類在寫文檔時依賴無數默會背景。當你在 Prompt 寫 1,000 條規則時，規則會自相矛盾，而模型遇到未見過的長尾案例時，它不會承認不懂，而是自信地套用最相近範本，產生最隱蔽致命的偽陽性。")


# ------------------------------------------------------------------------------
# SLIDE 5: BICAMERAL COGNITIVE HIERARCHY
# ------------------------------------------------------------------------------
s5 = prs.slides.add_slide(blank_layout)
bg5 = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg5.fill.solid()
bg5.fill.fore_color.rgb = BG_WHITE
bg5.line.fill.background()

add_zone1_header(s5, "系統架構", "建構「剛性左腦約束 ＋ 靈性右腦抽取 ＋ 前額葉專家仲裁」的現代雙腦數據架構", COLOR_SUCCESS)

# Left Column (Left-Brain)
col_w = Inches(3.644)
c_l = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), col_w, Inches(4.85))
c_l.fill.solid()
c_l.fill.fore_color.rgb = CARD_BG
c_l.line.color.rgb = COLOR_PRIMARY
c_l.line.width = Pt(2.0)
tf = c_l.text_frame
tf.margin_left = tf.margin_right = Inches(0.25)
tf.margin_top = Inches(0.3)
p = tf.paragraphs[0]
p.text = "【剛性左腦：確定性基底】"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY
p2 = tf.add_paragraph()
p2.text = "\n● 受控本體庫 (Ontology)：定義封閉業務字典，杜絕術語自由腦補。\n\n● 主數據管理 (MDM)：跨文檔實體消歧，鎖定唯一真理 (SSOT)。\n\n● 數據經緯 (Data Fabric)：端到端目錄、血緣追蹤與後設資料層。\n\n★ 特性：100% 零幻覺"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(10.5)
p2.font.color.rgb = TEXT_BODY

# Middle Column (Prefrontal / HITL Spotlight)
c_m = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.844), Inches(1.55), col_w, Inches(4.85))
c_m.fill.solid()
c_m.fill.fore_color.rgb = CARD_BG
c_m.line.color.rgb = COLOR_SUCCESS
c_m.line.width = Pt(2.5)
tf = c_m.text_frame
tf.margin_left = tf.margin_right = Inches(0.25)
tf.margin_top = Inches(0.3)
p = tf.paragraphs[0]
p.text = "【前額葉：人機協同 HITL】★"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_SUCCESS
p2 = tf.add_paragraph()
p2.text = "\n● 雙腦動態校驗：右腦抽取之 JSON 與左腦字典即時對齊。\n\n● 專家長尾仲裁：僅 < 5% 左右腦衝突案例由領域業務專家審查。\n\n● 主動學習反饋：修正結果自動沉澱為本體庫新增規則，消除模型自噬。\n\n★ 特性：最高價值安全網"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(10.5)
p2.font.color.rgb = TEXT_BODY

# Right Column (Right-Brain)
c_r = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.888), Inches(1.55), col_w, Inches(4.85))
c_r.fill.solid()
c_r.fill.fore_color.rgb = CARD_BG
c_r.line.color.rgb = COLOR_WARN
c_r.line.width = Pt(1.5)
tf = c_r.text_frame
tf.margin_left = tf.margin_right = Inches(0.25)
tf.margin_top = Inches(0.3)
p = tf.paragraphs[0]
p.text = "【靈性右腦：高維語義大模型】"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_WARN
p2 = tf.add_paragraph()
p2.text = "\n● 向量嵌入 (Embeddings)：保留完整情緒與語氣，拒絕表格壓平損耗。\n\n● 弱監督抽取：Few-Shot 快速生成候選標籤與密集段落摘要。\n\n● GraphRAG 檢索：錨定左腦知識圖譜，避免憑空捏造事實。\n\n★ 特性：高泛化模糊理解"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(10.5)
p2.font.color.rgb = TEXT_BODY

add_zone3_footer(s5, "★ 架構守則：左腦提供零幻覺硬約束，右腦提供泛化語義理解，前額葉專家把關長尾安全。")
set_notes(s5, "這就是我們為企業設計的破局架構：雙腦分層系統。左腦是確定性的知識圖譜與主數據管理，保證 100% 零幻覺；右腦是大語言模型，負責快速理解長篇大論的非結構化語義與模糊抽取。當右腦抽取的內容與左腦的字典衝突時，系統自動將這 5% 的長尾案例升級給人類領域專家仲裁。這樣既釋放了 95% 的人工作業，又守住了真實底線。")


# ------------------------------------------------------------------------------
# SLIDE 6: CASE STUDY MORGAN STANLEY VS BLIND FINE-TUNING
# ------------------------------------------------------------------------------
s6 = prs.slides.add_slide(blank_layout)
bg6 = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg6.fill.solid()
bg6.fill.fore_color.rgb = BG_WHITE
bg6.line.fill.background()

add_zone1_header(s6, "標竿案例", "摩根士丹利以 5 年人工策劃奠定混凝土底座，印證無治理的盲目微調必遭反噬", COLOR_SUCCESS)

# Left Column (Morgan Stanley Spotlight)
c_ms = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(5.7), Inches(4.85))
c_ms.fill.solid()
c_ms.fill.fore_color.rgb = CARD_BG
c_ms.line.color.rgb = COLOR_SUCCESS
c_ms.line.width = Pt(2.5)
tf = c_ms.text_frame
tf.margin_left = tf.margin_right = Inches(0.3)
tf.margin_top = Inches(0.35)
p = tf.paragraphs[0]
p.text = "【成功典範：摩根士丹利 (Morgan Stanley)】★"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_SUCCESS
p2 = tf.add_paragraph()
p2.text = "\n● 5 年知識策劃 (Knowledge Curation)：在生成式 AI 問世前即組建專責團隊逐篇審核內部所有研究報告。\n\n● 嚴格打分機制：為每份文檔訂出品質分數，過濾失效連結、過期政策並提供摘要。\n\n● 全球金融標竿：成為首批成功將 GPT-4 部署至數萬名理財顧問生產環境的金融機構，達成零重大法規事故。"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(11.5)
p2.font.color.rgb = TEXT_BODY

# Right Column (Quicksand Failure)
c_fail = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.55), Inches(5.733), Inches(4.85))
c_fail.fill.solid()
c_fail.fill.fore_color.rgb = CARD_BG
c_fail.line.color.rgb = CARD_BORDER
c_fail.line.width = Pt(1.5)
tf = c_fail.text_frame
tf.margin_left = tf.margin_right = Inches(0.3)
tf.margin_top = Inches(0.35)
p = tf.paragraphs[0]
p.text = "【反面警示：盲目微調之流沙災難】"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_DANGER
p2 = tf.add_paragraph()
p2.text = "\n● 輕信微調萬能：將未清洗、術語互相衝突的歷史客服紀錄與舊合約直接微調開源模型。\n\n● 吸收陳舊過期政策：模型學會了過期的折扣政策，自動化給出違規報價承諾，引發巨大法規訴訟風險。\n\n● 模型自噬 (MAD)：受污染的生成內容反覆進入訓練集，導致整體智能退化與幻覺失控。"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(11.5)
p2.font.color.rgb = TEXT_BODY

add_zone3_footer(s6, "★ 實證教訓：AI 能否成功不看算法多先進，而看數據長與知識策劃人（Curator）的基本功。")
set_notes(s6, "摩根士丹利能成為全球第一個把 GPT-4 成功放進財富管理生產環境的機構，不是因為他們比別人更懂 Prompt，而是他們的數據長在五年前就做對了一件事：組織專業團隊逐篇審核打分內部報告。這就是為什麼默克集團的數據長強調：地基必須是混凝土，而不能是流沙。任何試圖跳過數據治理、直接把未清洗數據拿去微調模型的公司，最後都自食惡果。")


# ------------------------------------------------------------------------------
# SLIDE 7: ASYMMETRIC MVP IMPLEMENTATION ROADMAP
# ------------------------------------------------------------------------------
s7 = prs.slides.add_slide(blank_layout)
bg7 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg7.fill.solid()
bg7.fill.fore_color.rgb = BG_WHITE
bg7.line.fill.background()

add_zone1_header(s7, "落地路線", "採行非對稱 MVP 策略：優先切入客服與程式碼生成，以短反饋累積組織治理經驗", COLOR_PRIMARY)

step_w = Inches(2.658)
steps = [
    ("Stage 01 (1~3月)", "基礎盤點與本體庫", "非結構化資產盤點\n建立核心業務受控詞表\n凍結盲目微調預算", CARD_BORDER, TEXT_NAVY),
    ("Stage 02 (3~6月)", "★ 非對稱 MVP 試點", "客服坐席輔助 (真人把關)\n程式碼生成 (編譯器抓錯)\n磨合提示範本與流程", COLOR_PRIMARY, COLOR_PRIMARY),
    ("Stage 03 (6~12月)", "數據經緯全面部署", "部署 Data Fabric\n主數據消歧 (MDM)\n打通 ERP/CRM 向量庫", CARD_BORDER, TEXT_NAVY),
    ("Stage 04 (12~18月)", "核心高價值全面賦能", "雙腦架構無損遷移\n賦能核心財務與研發\n建立全組織 AI 護城河", CARD_BORDER, TEXT_NAVY)
]

for i, (stage, title, body, border_col, title_col) in enumerate(steps):
    bx = Inches(0.8 + i * 3.025)
    c = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, Inches(1.55), step_w, Inches(4.85))
    c.fill.solid()
    c.fill.fore_color.rgb = CARD_BG
    c.line.color.rgb = border_col
    c.line.width = Pt(2.5 if i == 1 else 1.2)
    tf = c.text_frame
    tf.margin_left = tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.3)
    p = tf.paragraphs[0]
    p.text = stage
    p.font.name = "Microsoft JhengHei"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEXT_MUTED
    p2 = tf.add_paragraph()
    p2.text = f"\n{title}\n"
    p2.font.name = "Microsoft JhengHei"
    p2.font.size = Pt(12.5)
    p2.font.bold = True
    p2.font.color.rgb = title_col
    p3 = tf.add_paragraph()
    p3.text = f"\n● " + "\n\n● ".join(body.split("\n"))
    p3.font.name = "Microsoft JhengHei"
    p3.font.size = Pt(10)
    p3.font.color.rgb = TEXT_BODY

add_zone3_footer(s7, "★ 破局秘訣：以高容錯、短反饋場景打消 71% 觀望疑慮，讓組織飛輪在安全區轉動。")
set_notes(s7, "面對 71% 數據長觀望與權力爭奪，我們該怎麼破局？答案是非對稱試點。絕對不要一上來就碰財務決策或核心研發數據，那樣容錯率太低。先做客服輔助和程式碼生成！因為客服有真人坐席把關，程式碼有編譯器自動抓錯。在這兩個場景裡磨合提示詞範本、人機分工與數據血緣機制，成功後再將經驗無損複製到核心資產。")


# ------------------------------------------------------------------------------
# SLIDE 8: CLOSING TAKEAWAY & MONDAY ACTION
# ------------------------------------------------------------------------------
s8 = prs.slides.add_slide(blank_layout)
bg8 = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg8.fill.solid()
bg8.fill.fore_color.rgb = DARK_HUB_BG
bg8.line.fill.background()

# Zone 1 Dark
tb = s8.shapes.add_textbox(Inches(0.8), Inches(0.55), Inches(11.733), Inches(0.7))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "【終幕：峰終收斂】以混凝土基底贏得下一個十年的企業認知戰"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = RGBColor(255, 255, 255)

# Left Column (3 Golden Rules)
c_left = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(5.7), Inches(4.85))
c_left.fill.solid()
c_left.fill.fore_color.rgb = RGBColor(30, 41, 59)
c_left.line.color.rgb = DARK_HUB_SUB
c_left.line.width = Pt(1.5)
tf = c_left.text_frame
tf.margin_left = tf.margin_right = Inches(0.3)
tf.margin_top = Inches(0.35)
p = tf.paragraphs[0]
p.text = "【董事會三大黃金決策鐵律】"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = DARK_HUB_SUB
p2 = tf.add_paragraph()
p2.text = "\n1. 數據治理非事後補丁：沒有主數據管理的知識資產，只會產出規模化的幻覺與錯誤。\n\n2. 堅持雙腦分層架構：以左腦剛性知識圖譜約束右腦語義大模型，前額葉專家守護長尾。\n\n3. 非對稱試點破局：在客服與代碼的高容錯場景跑通人機迴路，以實證效益打破觀望。"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(11)
p2.font.color.rgb = RGBColor(241, 245, 249)

# Right Column (Monday Action Checklist)
c_right = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.55), Inches(5.733), Inches(4.85))
c_right.fill.solid()
c_right.fill.fore_color.rgb = RGBColor(30, 41, 59)
c_right.line.color.rgb = COLOR_SUCCESS
c_right.line.width = Pt(2.0)
tf = c_right.text_frame
tf.margin_left = tf.margin_right = Inches(0.3)
tf.margin_top = Inches(0.35)
p = tf.paragraphs[0]
p.text = "【星期一立即啟動清單 (Monday Action)】"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = RGBColor(52, 211, 153)
p2 = tf.add_paragraph()
p2.text = "\n[ ] 召開 CDO-CIO-BU 聯席會議：成立跨職能專案組，終結技術主導權爭奪。\n\n[ ] 凍結未清洗內部文檔的盲目微調預算。\n\n[ ] 啟動首個「業務受控詞表 (Ontology)」編纂專案。\n\n[ ] 立項 90 天內實現的客服/代碼生成非對稱 MVP 試點。"
p2.font.name = "Microsoft JhengHei"
p2.font.size = Pt(11)
p2.font.color.rgb = RGBColor(241, 245, 249)

# Bottom bar
b_bot = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.72), Inches(11.733), Inches(0.52))
b_bot.fill.solid()
b_bot.fill.fore_color.rgb = RGBColor(2, 6, 23)
b_bot.line.color.rgb = DARK_HUB_SUB
b_bot.line.width = Pt(1.0)
tf = b_bot.text_frame
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
tf.margin_left = Inches(0.2)
p = tf.paragraphs[0]
p.text = "★ 終極結語：起身的時刻，就是現在！想讓企業數據配合 AI 需花費數年，唯有即刻行動方能致勝。"
p.font.name = "Microsoft JhengHei"
p.font.size = Pt(10.5)
p.font.bold = True
p.font.color.rgb = RGBColor(255, 255, 255)

set_notes(s8, "各位長官，生成式 AI 的競爭不是比誰買了更多 GPU，而是比誰的數據準備度更高。想讓大型企業的重要數據準備好，需要花費數年時間；而該起身動作的時刻，就是現在。星期一開始，讓我們終結觀望與爭議，打好這片混凝土的地基。謝謝大家！")

output_pptx = os.path.abspath("reading_sessions/20261101_企業數據與生成式AI準備度/02_outputs/02_executive_presentation.pptx")
prs.save(output_pptx)
print(f"[OK] PowerPoint saved successfully to: {output_pptx}")
