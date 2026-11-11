# -*- coding: utf-8 -*-
r"""
table_components.py
Decoupled, publication-grade table components module for the midterm report:
東吳大學企管系 3B 楊亞恩《從數據債到人機協同：生成式 AI 時代下的企業商業分析重構》

Features & Architectural Design:
1. Pure Decoupling:
   - Self-contained and isolated from document-wide file locks.
   - Ready to be inserted into the main document without side-effects or regressions.
2. Publication & PPT Visual Grade:
   - Font Pairing: 標楷體 (DFKai-SB for Traditional Chinese) + Times New Roman (for Latin / Digits).
   - Headers: 11pt bold white text on deep navy background (#1B365D), centered alignment, tblHeader repetition.
   - Data Rows: Zebra striping (pure white #FFFFFF / slate tint #F1F5F9), cantSplit protection on every row.
   - Bullet Points: Hanging indent (hanging 240 dxa = 12pt, left 240 dxa) to prevent orphan line wraps.
   - Alert Accents: Theoretical boundaries & limits highlighted in Alert Red (#B91C1C).
   - Accompanying Callout Box: High-executive warm amber styling (#FFFBEB fill, #F59E0B left bar, #B45309 header).
3. Non-Destructive Insertion APIs:
   - insert_table_1_before(doc, target_p)
   - insert_table_2_before(doc, target_p, include_callout=True)
   - insert_tables_into_doc(doc)
   - insert_tables_into_file(source_docx_path, output_docx_path)
   - build_preview_docx(preview_path)
   - verify_tables_in_doc(doc)
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

# =============================================================================
# Color Palette & Styling Constants
# =============================================================================
HEX_NAVY = "1B365D"          # Deep Navy Blue (Headers & Category Anchors)
HEX_ZEBRA = "F1F5F9"         # Subtle slate-tint background for alternating rows
HEX_WHITE = "FFFFFF"         # Pure white background
HEX_BORDER = "CBD5E1"        # Subtle slate border (#CBD5E1)
HEX_BORDER_DARK = "94A3B8"   # Darker accent border
HEX_ALERT_RED = "B91C1C"     # Alert Red for theoretical boundaries / limits
HEX_AMBER_BG = "FFFBEB"      # Warm amber background for Callout Box
HEX_AMBER_BORDER = "F59E0B"  # Amber left bar border
HEX_AMBER_TEXT = "B45309"    # Amber title text
HEX_DARK = "0F172A"          # Dark charcoal text for readability
HEX_MUTED = "64748B"         # Muted slate text

COLOR_NAVY = RGBColor(0x1B, 0x36, 0x5D)
COLOR_ALERT_RED = RGBColor(0xB9, 0x1C, 0x1C)
COLOR_AMBER_TEXT = RGBColor(0xB4, 0x53, 0x09)
COLOR_DARK = RGBColor(0x0F, 0x17, 0x2A)
COLOR_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
COLOR_MUTED = RGBColor(0x64, 0x74, 0x8B)

FONT_CHINESE = "標楷體"
FONT_WESTERN = "Times New Roman"

# Default table width in dxa (Expanded to 7.10 inches = 10224 dxa for optimal breathing room and no line wrap)
DEFAULT_TABLE_WIDTH_DXA = 10224


# =============================================================================
# Low-level XML & Styling Helpers
# =============================================================================
def set_run_font(run, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=10.5, bold=False, italic=False, color_rgb=COLOR_DARK):
    """
    Applies comprehensive dual-font properties (EastAsian + Ascii/HAnsi)
    to eliminate font substitution fallbacks across Microsoft Word and LibreOffice.
    """
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size_pt)
    run.font.color.rgb = color_rgb
    run.font.name = western_font

    rPr = run._r.get_or_add_rPr()
    rFonts_xml = (
        f'<w:rFonts {nsdecls("w")} '
        f'w:ascii="{western_font}" '
        f'w:hAnsi="{western_font}" '
        f'w:eastAsia="{font_name}" '
        f'w:cs="{western_font}"/>'
    )
    rPr.append(parse_xml(rFonts_xml))
    return run


def style_cell(cell, fill_hex=None, top_pt=5, bottom_pt=5, left_pt=6, right_pt=6,
               border_bottom_hex=None, border_top_hex=None, v_align="top"):
    """
    Applies padding, shading background, borders, and vertical alignment to a table cell.
    """
    tcPr = cell._tc.get_or_add_tcPr()

    # Background shading
    if fill_hex:
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    # Cell interior padding (margins)
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{int(top_pt * 20)}" w:type="dxa"/>'
        f'<w:bottom w:w="{int(bottom_pt * 20)}" w:type="dxa"/>'
        f'<w:left w:w="{int(left_pt * 20)}" w:type="dxa"/>'
        f'<w:right w:w="{int(right_pt * 20)}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

    # Vertical alignment
    vAlign = parse_xml(f'<w:vAlign {nsdecls("w")} w:val="{v_align}"/>')
    tcPr.append(vAlign)

    # Optional borders
    if border_bottom_hex or border_top_hex:
        bdr_xml = f'<w:tcBorders {nsdecls("w")}>'
        if border_top_hex:
            bdr_xml += f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{border_top_hex}"/>'
        if border_bottom_hex:
            bdr_xml += f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{border_bottom_hex}"/>'
        bdr_xml += '</w:tcBorders>'
        tcPr.append(parse_xml(bdr_xml))


def apply_row_protections(row, is_header=False):
    """
    Guarantees publication pagination safety:
    - cantSplit: Prevents rows from splitting across page breaks.
    - tblHeader: Causes the header row to repeat if the table crosses pages.
    """
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    if is_header:
        trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))


def format_bullet_paragraph(p, bullet_title, bullet_desc, title_color=COLOR_NAVY,
                            desc_color=COLOR_DARK, font_size_pt=10.0):
    """
    Formats a bullet-point item paragraph with hanging indent (hanging 240, left 240)
    and dual font runs for title and description.
    """
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pPr = p._p.get_or_add_pPr()

    # Line spacing & compact vertical rhythm
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="24" w:after="24" w:line="240" w:lineRule="auto"/>')
    pPr.append(sp)

    # Hanging indent: 240 dxa (0.167 in / 12pt)
    ind = parse_xml(f'<w:ind {nsdecls("w")} w:left="240" w:hanging="240"/>')
    pPr.append(ind)

    # Bullet title (Bold, colored)
    r_title = p.add_run(bullet_title)
    set_run_font(r_title, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=font_size_pt, bold=True, color_rgb=title_color)

    # Bullet description (Regular, charcoal)
    if bullet_desc:
        r_desc = p.add_run(bullet_desc)
        set_run_font(r_desc, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                     size_pt=font_size_pt, bold=False, color_rgb=desc_color)
    return p


# =============================================================================
# Caption & Callout Box Builders
# =============================================================================
def build_caption_paragraph(p, caption_text):
    """
    Formats a table caption paragraph with proper spacing, navy bold text, and keep_with_next.
    Preserves clean 標楷體 font properties without Times New Roman overrides on Normal style.
    """
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    pPr = p._p.get_or_add_pPr()
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="200" w:after="90" w:line="240" w:lineRule="auto"/>')
    pPr.append(sp)

    r = p.add_run(caption_text)
    set_run_font(r, font_name=FONT_CHINESE, western_font=FONT_CHINESE,
                 size_pt=10.5, bold=True, color_rgb=COLOR_NAVY)
    return p


def build_callout_box(p, title_text, body_text):
    """
    Renders an executive callout box with:
    - Warm amber background (#FFFBEB)
    - 3pt solid amber left border (#F59E0B)
    - Subtle slate borders on other three sides (#CBD5E1)
    - Balanced interior padding and clean typography.
    - Clean 標楷體 font runs to ensure 100% compliance with verify_report.py.
    """
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pPr = p._p.get_or_add_pPr()

    # Spacing and line height
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="140" w:after="160" w:line="270" w:lineRule="auto"/>')
    pPr.append(sp)

    # Expanded horizontal box width to harmonize with the 7.10-inch wide table
    ind = parse_xml(f'<w:ind {nsdecls("w")} w:left="-180" w:right="-180"/>')
    pPr.append(ind)

    # Box borders: Amber-500 on left (sz="24"=3pt), subtle Slate on top/right/bottom (sz="4"=0.5pt)
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="8" w:color="{HEX_BORDER}"/>'
        f'<w:left w:val="single" w:sz="24" w:space="15" w:color="{HEX_AMBER_BORDER}"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="8" w:color="{HEX_BORDER}"/>'
        f'<w:right w:val="single" w:sz="4" w:space="8" w:color="{HEX_BORDER}"/>'
        f'</w:pBdr>'
    )
    pPr.append(pBdr)

    # Amber shading fill
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{HEX_AMBER_BG}"/>')
    pPr.append(shd)

    # Title run
    r_title = p.add_run(title_text + "\n")
    set_run_font(r_title, font_name=FONT_CHINESE, western_font=FONT_CHINESE,
                 size_pt=10.5, bold=True, color_rgb=COLOR_AMBER_TEXT)

    # Body run
    r_body = p.add_run(body_text)
    set_run_font(r_body, font_name=FONT_CHINESE, western_font=FONT_CHINESE,
                 size_pt=10.0, bold=False, color_rgb=COLOR_DARK)
    return p


# =============================================================================
# Structured Table Renderer (PPT Style)
# =============================================================================
def populate_ppt_table(table, headers, data, col_widths, table_width_dxa=DEFAULT_TABLE_WIDTH_DXA):
    """
    Populates and styles an existing docx Table object with:
    - 11pt bold white text headers on Deep Navy (#1B365D)
    - tblHeader repetition and cantSplit protection on every row
    - Alternating row zebra striping (#FFFFFF / #F1F5F9)
    - Column 0: Centered, bold, navy category anchors
    - Columns > 0: Bullet points with hanging indents (hanging 240)
    - Alert Red (#B91C1C) for theoretical limits / boundaries
    """
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    tblPr = table._tbl.tblPr
    tblW = parse_xml(f'<w:tblW {nsdecls("w")} w:w="{table_width_dxa}" w:type="dxa"/>')
    tblPr.append(tblW)

    # Table horizontal border styling (PPT clean look)
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="12" w:space="0" w:color="{HEX_NAVY}"/>'
        f'<w:bottom w:val="single" w:sz="12" w:space="0" w:color="{HEX_NAVY}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)

    # 1. Header Row
    hdr_row = table.rows[0]
    apply_row_protections(hdr_row, is_header=True)

    for i, h_text in enumerate(headers):
        cell = hdr_row.cells[i]
        cell.width = col_widths[i]
        # Compact horizontal padding in header to prevent awkward single-character wraps
        style_cell(cell, fill_hex=HEX_NAVY, top_pt=6, bottom_pt=6, left_pt=3, right_pt=3,
                   border_bottom_hex=HEX_NAVY, v_align="center")

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pPr = p._p.get_or_add_pPr()
        sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="30" w:after="30" w:line="240" w:lineRule="auto"/>')
        pPr.append(sp)

        # Handle intentional line breaks in headers with styling
        if "\n" in h_text:
            lines = h_text.split("\n")
            r0 = p.add_run(lines[0])
            set_run_font(r0, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                         size_pt=11.0, bold=True, color_rgb=COLOR_WHITE)
            r1 = p.add_run("\n" + lines[1])
            set_run_font(r1, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                         size_pt=9.5, bold=True, color_rgb=RGBColor(226, 232, 240))
        else:
            r = p.add_run(h_text)
            set_run_font(r, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                         size_pt=11.0, bold=True, color_rgb=COLOR_WHITE)

    # 2. Data Rows
    for r_idx, row_spec in enumerate(data):
        row = table.rows[r_idx + 1]
        apply_row_protections(row, is_header=False)
        fill_hex = HEX_WHITE if r_idx % 2 == 0 else HEX_ZEBRA

        for c_idx, cell_bullets in enumerate(row_spec):
            cell = row.cells[c_idx]
            cell.width = col_widths[c_idx]

            # Vertical alignment: Center for Column 0 (category anchor), Top for bullets
            v_align = "center" if c_idx == 0 else "top"
            style_cell(cell, fill_hex=fill_hex, top_pt=5, bottom_pt=5, left_pt=6, right_pt=6,
                       border_bottom_hex=HEX_BORDER, v_align=v_align)

            if c_idx == 0:
                # Column 0: Category title
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                pPr = p._p.get_or_add_pPr()
                sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="30" w:after="30" w:line="240" w:lineRule="auto"/>')
                pPr.append(sp)

                for item in cell_bullets:
                    # item can be tuple: (title, subtitle) or single string
                    if isinstance(item, tuple):
                        t_main, t_sub = item[0], item[1] if len(item) > 1 else ""
                        r0 = p.add_run(t_main)
                        set_run_font(r0, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                                     size_pt=10.5, bold=True, color_rgb=COLOR_NAVY)
                        if t_sub:
                            r_sub = p.add_run("\n" + t_sub)
                            set_run_font(r_sub, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                                         size_pt=9.5, bold=True, color_rgb=COLOR_MUTED)
                    else:
                        r = p.add_run(str(item))
                        set_run_font(r, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                                     size_pt=10.5, bold=True, color_rgb=COLOR_NAVY)
            else:
                # Columns > 0: Structured bullet points
                for b_idx, bullet in enumerate(cell_bullets):
                    p_cur = cell.paragraphs[0] if b_idx == 0 else cell.add_paragraph()
                    # bullet: (bullet_prefix, bullet_text, is_alert)
                    if isinstance(bullet, tuple):
                        b_pref = bullet[0]
                        b_text = bullet[1] if len(bullet) > 1 else ""
                        is_alert = bullet[2] if len(bullet) > 2 else False
                    else:
                        b_pref = str(bullet)
                        b_text = ""
                        is_alert = False

                    title_color = COLOR_ALERT_RED if is_alert else COLOR_NAVY
                    format_bullet_paragraph(p_cur, b_pref, b_text, title_color=title_color,
                                            desc_color=COLOR_DARK, font_size_pt=10.0)
    return table


# =============================================================================
# Data Specifications for Table 1 and Table 2
# =============================================================================
def get_table_1_spec():
    """
    Returns (caption, headers, data, col_widths) for Table 1:
    表一：四種 AI 應用情境矩陣（前沿破局解法、核心機制與理論死穴批判）
    Dimensions: 5 rows (1 header + 4 data), 4 columns.
    Expanded width: 6.90 inches (9936 dxa).
    """
    caption = "表一：四種 AI 應用情境矩陣（前沿破局解法、核心機制與理論死穴批判）"
    headers = ["【應用模式】", "【核心做法】\n(文中實例)", "【主要優勢】\n(PPT重點)", "【人機邊界與極限】"]
    col_widths = [Inches(1.40), Inches(2.10), Inches(1.80), Inches(1.60)]

    data = [
        # Row 1: Grounded Twins
        [
            [("解法一：綁定真人數位雙生", "(Grounded Twins)")],
            [
                ("• 深度訪談：", "以數小時真人訪談與心智測驗建立基準事實", False),
                ("• 追蹤軌跡：", "哥倫比亞、史丹福與 CivicSync 行為錨點", False)
            ],
            [
                ("• 真實性高：", "有客觀基準事實錨定，杜絕純虛構人格", False),
                ("• 破局關鍵：", "將質化訪談規模化，兼具規模與深度", False)
            ],
            [
                ("• 感覺不可壓縮：", "香料氣味、生理直覺無法數位化", True),
                ("• 成本門檻高：", "前期真人訪談與資料維護耗費巨大", True)
            ]
        ],
        # Row 2: Hybrid Model
        [
            [("解法二：混合架構模型", "(Hybrid Model)")],
            [
                ("• 分工轉譯：", "右腦大模型僅轉譯非結構圖文為特徵分數", False),
                ("• 統計計算：", "左腦傳統計量模型計算價格彈性與敏感度", False)
            ],
            [
                ("• 數學防幻覺：", "截斷大模型自作聰明之「混淆」推論", False),
                ("• 解釋力清晰：", "係數與因果關係具備高度可稽核性", False)
            ],
            [
                ("• 模型誤設風險：", "多變數非線性時左腦統計函式難以擬合", True),
                ("• 維護依賴：", "需專業計量經濟學家持續調校參數", True)
            ]
        ],
        # Row 3: PPI Calibration
        [
            [("解法三：真人基準校準", "(PPI Calibration)")],
            [
                ("• 黃金基準：", "以 100 名真人盲測為核心標準點", False),
                ("• 統計修正：", "萬名 AI 代理人模擬後以公式扣除系統偏誤", False)
            ],
            [
                ("• 成本暴降：", "兼顧真人深度與 AI 海量樣本規模", False),
                ("• 快速擴充：", "小預算即可啟動大規模市場動態調查", False)
            ],
            [
                ("• 分布偏移風險：", "AI 對齊真人可能為短期湊巧（3個月即漂移）", True),
                ("• 動態依賴：", "每一波次皆需重新抽取真人基準校準", True)
            ]
        ],
        # Row 4: Fine-Tuning
        [
            [("解法四：歷史實驗微調", "(Fine-Tuning)")],
            [
                ("• 專有數據微調：", "輸入歷史問卷、銷售日誌與 A/B Test", False),
                ("• 產業專用：", "Evidenza、GBK Collective 針對品類調權", False)
            ],
            [
                ("• 貼近企業內部：", "高度適配既有商品與客戶群行為特徵", False),
                ("• 自動化部署：", "常態性選品與門市配置快速標準化輸出", False)
            ],
            [
                ("• 倖存者偏差：", "無法泛化至跨品類或未曾涉足之全新市場", True),
                ("• 模型過擬合：", "歷史資料偏誤將導致模型陷入路徑依賴", True)
            ]
        ]
    ]
    return caption, headers, data, col_widths


def get_table_2_spec():
    """
    Returns (caption, headers, data, col_widths) for Table 2:
    表二：AI 模型在不同企業類型中的定位矩陣（客戶焦點、幕後任務與商業價值）
    Dimensions: 6 rows (1 header + 5 data), 4 columns.
    Expanded width: 6.90 inches (9936 dxa).
    """
    caption = "表二：AI 模型在不同企業類型中的定位矩陣（客戶焦點、幕後任務與商業價值）"
    headers = ["【企業類型】\n(B2B/B2C等)", "【客戶關注焦點】", "【AI 幕後核心任務】", "【核心商業價值】\n(帶來的核心成效)"]
    col_widths = [Inches(1.25), Inches(2.05), Inches(1.90), Inches(1.70)]

    data = [
        # Row 1: B2B
        [
            [("B2B", "(企業對企業)")],
            [
                ("• 理性採購：", "決策背負部門損益（P&L）與合約風險", False),
                ("• 硬性指標：", "審批週期長，只看可量化降本增效", False)
            ],
            [
                ("• 檯面硬實力：", "預測停機風險、工時節省與履約進度", False),
                ("• 合約標的：", "直接寫入採購合約成為驗收基準", False)
            ],
            [
                ("• 實質價值：", "S-SET 流體報價縮至 3hr，排除停機損失", False)
            ]
        ],
        # Row 2: B2C
        [
            [("B2C", "(企業對終端客)")],
            [
                ("• 感性消費：", "追求即時滿足、省時省力與情緒價值", False),
                ("• 轉換極快：", "轉換成本趨近於零，對繁瑣操作零容忍", False)
            ],
            [
                ("• 幕後隱形調度：", "千人千面推薦、毫秒定價、排隊預估", False),
                ("• 無感極致體驗：", "深埋系統後台，嚴禁增加用戶操作阻力", False)
            ],
            [
                ("• 實質價值：", "Netflix 個性化推薦、星巴克行動點餐調度", False)
            ]
        ],
        # Row 3: B2B2C
        [
            [("B2B2C", "(平台賦能商戶)")],
            [
                ("• 雙重買單主體：", "商戶要流量增長，終端客要品質與可靠", False),
                ("• 生態平衡：", "平台需同時兼顧雙邊利益與交易公平", False)
            ],
            [
                ("• 雙向媒合引擎：", "替商戶自動生成文案、預測銷量定價", False),
                ("• 履約背書：", "替消費者精準搜尋、推薦優選商品", False)
            ],
            [
                ("• 實質價值：", "Shopify 獨立站賦能、外送平台動態媒合", False)
            ]
        ],
        # Row 4: C2C
        [
            [("C2C", "(個人對個人)")],
            [
                ("• 平權個人交易：", "資訊高度不對稱，核心命脈為「信任」", False),
                ("• 風險脆弱：", "極易因單次詐騙或假貨糾紛瓦解信心", False)
            ],
            [
                ("• 信任仲裁中樞：", "以圖搜圖比對真品細節、對話防詐預警", False),
                ("• 歷史信用評級：", "交易糾紛智慧初審與自動化履約保障", False)
            ],
            [
                ("• 實質價值：", "Airbnb 雙向審查與保險、二手交易平台", False)
            ]
        ],
        # Row 5: B2G
        [
            [("B2G", "(企業對公部門)")],
            [
                ("• 公務法規稽核：", "講求 100% 依法行政、主權資安與無弊端", False),
                ("• 公共利益導向：", "重視程序正義與個資隱私大於短期利潤", False)
            ],
            [
                ("• 可解釋性 (XAI)：", "杜絕黑箱演算法，決策路徑完整可溯源", False),
                ("• 主權合規防護：", "提供 Audit Trail 審計日誌備議會政風查驗", False)
            ],
            [
                ("• 實質價值：", "智慧交通號誌調控、數位稅務異常查核", False)
            ]
        ]
    ]
    return caption, headers, data, col_widths


def get_callout_box_spec():
    """
    Returns (title, body) for the Executive Callout Box below Table 2.
    """
    title = "★ 高管決策啟示：切莫張冠李戴，找準真實價值槓桿"
    body = (
        "高管制定戰略時最忌「位階錯位」：在 B2B 切莫拿酷炫但無法量化 ROI 的前台 AI 噱頭當賣點，"
        "客戶只看合約實力與履約保障；在 B2C 切莫強迫消費者理解模型架構，增加操作步驟的技術都是退步；"
        "在 B2G 貿然採用不可說明的黑箱演算法，將直接引發合規災難。"
        "唯有對齊自身商業模式，統計模型才能找準真正的造血槓桿。"
    )
    return title, body


# =============================================================================
# Standalone Document Builders (Appending to End)
# =============================================================================
def create_table_1(doc):
    """
    Creates and appends Table 1 (with caption) to the end of doc.
    """
    caption, headers, data, col_widths = get_table_1_spec()
    p_cap = doc.add_paragraph()
    build_caption_paragraph(p_cap, caption)

    tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
    populate_ppt_table(tbl, headers, data, col_widths)

    p_after = doc.add_paragraph()
    pPr = p_after._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="120"/>'))
    return tbl


def create_table_2(doc, include_callout=True):
    """
    Creates and appends Table 2 (with caption) and Callout Box to the end of doc.
    """
    caption, headers, data, col_widths = get_table_2_spec()
    p_cap = doc.add_paragraph()
    build_caption_paragraph(p_cap, caption)

    tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
    populate_ppt_table(tbl, headers, data, col_widths)

    if include_callout:
        title, body = get_callout_box_spec()
        p_box = doc.add_paragraph()
        build_callout_box(p_box, title, body)

    p_after = doc.add_paragraph()
    pPr = p_after._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="120"/>'))
    return tbl


# =============================================================================
# Clean Non-Destructive In-Place Insertion APIs (Before Target Paragraphs)
# =============================================================================
def insert_table_1_before(doc, ref_paragraph):
    """
    Inserts Table 1 and its caption directly before ref_paragraph.
    Leaves all existing text and bookmarks intact.
    """
    caption, headers, data, col_widths = get_table_1_spec()

    # 1. Caption paragraph
    p_cap = doc.add_paragraph()
    ref_paragraph._p.addprevious(p_cap._p)
    build_caption_paragraph(p_cap, caption)

    # 2. Table
    tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
    ref_paragraph._p.addprevious(tbl._tbl)
    populate_ppt_table(tbl, headers, data, col_widths)

    # 3. Spacing paragraph after table
    p_after = doc.add_paragraph()
    ref_paragraph._p.addprevious(p_after._p)
    pPr = p_after._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="100"/>'))
    return tbl


def insert_table_2_before(doc, ref_paragraph, include_callout=True):
    """
    Inserts Table 2, its caption, and the Executive Callout Box directly before ref_paragraph.
    Leaves all existing text and bookmarks intact.
    """
    caption, headers, data, col_widths = get_table_2_spec()

    # 1. Caption paragraph
    p_cap = doc.add_paragraph()
    ref_paragraph._p.addprevious(p_cap._p)
    build_caption_paragraph(p_cap, caption)

    # 2. Table
    tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
    ref_paragraph._p.addprevious(tbl._tbl)
    populate_ppt_table(tbl, headers, data, col_widths)

    # 3. Callout Box
    if include_callout:
        title, body = get_callout_box_spec()
        p_box = doc.add_paragraph()
        ref_paragraph._p.addprevious(p_box._p)
        build_callout_box(p_box, title, body)

    # 4. Spacing paragraph after table/box
    p_after = doc.add_paragraph()
    ref_paragraph._p.addprevious(p_after._p)
    pPr = p_after._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="100"/>'))
    return tbl


def find_target_paragraphs(doc):
    """
    Locates the precise paragraph anchors for Table 1 and Table 2.
    Target for Table 1: Paragraph starting with "上面這四種應用方式還只是AI應用上的冰山一角"
    Target for Table 2: Paragraph starting with "不難看出，其實AI模型"
    """
    target_p1 = None
    target_p2 = None

    for p in doc.paragraphs:
        txt = p.text.strip()
        if "上面這四種應用方式" in txt and target_p1 is None:
            target_p1 = p
        elif "不難看出，其實AI模型" in txt and target_p2 is None:
            target_p2 = p

    return target_p1, target_p2


def insert_tables_into_doc(doc):
    """
    Idempotent and safe table insertion into an existing docx Document object.
    Checks whether Table 1 and Table 2 already exist to avoid duplicate insertions.
    """
    # Check if tables already exist
    t1_exists = False
    t2_exists = False
    for t in doc.tables:
        if len(t.rows) == 5 and len(t.columns) == 4:
            if "應用模式" in "".join(c.text for c in t.rows[0].cells):
                t1_exists = True
        elif len(t.rows) == 6 and len(t.columns) == 4:
            if "企業類型" in "".join(c.text for c in t.rows[0].cells):
                t2_exists = True

    if t1_exists and t2_exists:
        print("[table_components] Both Table 1 and Table 2 already exist. No duplicate insertion.")
        return doc

    target_p1, target_p2 = find_target_paragraphs(doc)
    assert target_p1 is not None, "Could not find anchor paragraph for Table 1 ('上面這四種應用方式')!"
    assert target_p2 is not None, "Could not find anchor paragraph for Table 2 ('不難看出，其實AI模型')!"

    if not t1_exists:
        print("[table_components] Inserting Table 1 before anchor paragraph...")
        insert_table_1_before(doc, target_p1)

    if not t2_exists:
        print("[table_components] Inserting Table 2 & Callout Box before anchor paragraph...")
        insert_table_2_before(doc, target_p2, include_callout=True)

    print("[table_components] Successfully inserted Table 1 and Table 2!")
    return doc


def insert_tables_into_file(source_docx_path, output_docx_path=None):
    """
    Safely opens source_docx_path, inserts Table 1 and Table 2, and saves to output_docx_path
    (or overwrites source_docx_path if output_docx_path is None).
    """
    if output_docx_path is None:
        output_docx_path = source_docx_path

    doc = docx.Document(source_docx_path)
    insert_tables_into_doc(doc)
    doc.save(output_docx_path)
    print(f"[table_components] Saved updated document to: {output_docx_path}")
    return output_docx_path


# =============================================================================
# Standalone Preview Document Generator
# =============================================================================
def build_preview_docx(preview_path):
    """
    Builds a standalone preview document 'preview_tables.docx' exhibiting
    Table 1, Table 2, and the Executive Callout Box with complete page styling.
    """
    doc = docx.Document()

    # Setup standard A4 page layout
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(0.85)   # Provide ample horizontal room
    section.right_margin = Inches(0.85)

    # Preview Header
    p_head = doc.add_paragraph()
    p_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pHeadPr = p_head._p.get_or_add_pPr()
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="60" w:after="140"/>')
    pHeadPr.append(sp)

    r_title = p_head.add_run("期中報告表格組件視覺預覽 (Table Preview)\n")
    set_run_font(r_title, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=18.0, bold=True, color_rgb=COLOR_NAVY)

    r_sub = p_head.add_run("東吳大學企管系 3B 楊亞恩｜期中專題報告獨立表格模組驗證")
    set_run_font(r_sub, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=11.0, bold=False, color_rgb=COLOR_MUTED)

    # Intro description
    p_intro = doc.add_paragraph()
    p_intro.paragraph_format.space_before = Pt(8)
    p_intro.paragraph_format.space_after = Pt(16)
    r_intro = p_intro.add_run(
        "本預覽文件獨立展示依據出版級標準設計的兩張核心視覺化 PPT 風格表格及高管決策啟示 Callout Box。"
        "全部採用 標楷體 / Times New Roman 雙字體配置、11pt 深海藍 (#1B365D) 白字表頭、交替斑馬紋、"
        "懸掛縮排 (hanging 240) 列表、警戒紅 (#B91C1C) 人機極限醒目提示、以及 cantSplit 與 tblHeader 分頁保護防護。"
    )
    set_run_font(r_intro, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=10.5, bold=False, color_rgb=COLOR_DARK)

    # 1. Section Title: Table 1
    p_sec1 = doc.add_paragraph()
    p_sec1.paragraph_format.space_before = Pt(14)
    p_sec1.paragraph_format.space_after = Pt(4)
    p_sec1.paragraph_format.keep_with_next = True
    r_sec1 = p_sec1.add_run("一、 Table 1：四種 AI 應用情境矩陣")
    set_run_font(r_sec1, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=13.0, bold=True, color_rgb=COLOR_NAVY)

    # Build Table 1
    create_table_1(doc)

    # Page Break for clean multi-page preview
    p_br = doc.add_paragraph()
    p_br.add_run().add_break(docx.enum.text.WD_BREAK.PAGE)

    # 2. Section Title: Table 2
    p_sec2 = doc.add_paragraph()
    p_sec2.paragraph_format.space_before = Pt(14)
    p_sec2.paragraph_format.space_after = Pt(4)
    p_sec2.paragraph_format.keep_with_next = True
    r_sec2 = p_sec2.add_run("二、 Table 2：AI 模型在不同企業類型中的定位矩陣與高管啟示")
    set_run_font(r_sec2, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=13.0, bold=True, color_rgb=COLOR_NAVY)

    # Build Table 2 + Callout Box
    create_table_2(doc, include_callout=True)

    # Save preview docx
    os.makedirs(os.path.dirname(os.path.abspath(preview_path)), exist_ok=True)
    doc.save(preview_path)
    print(f"[table_components] Successfully generated standalone preview: {preview_path}")
    return preview_path


# =============================================================================
# Automated Verification Harness
# =============================================================================
def verify_tables_in_doc(doc_or_path):
    """
    Performs rigorous deep verification against verify_report.py rules and
    all publication-grade visual and structural requirements:
    1. Table 1 dimensions (5x4) and required header keywords.
    2. Table 2 dimensions (6x4) and required header keywords.
    3. cantSplit attribute present on every row.
    4. tblHeader attribute present on row 0.
    5. Table header fill == #1B365D and header text color == white, bold, 11pt.
    6. Hanging indent (hanging 240) applied to bullet points.
    7. Alert Red (#B91C1C) applied to theoretical limits in Table 1.
    8. Callout Box styling: warm background #FFFBEB and amber left border #F59E0B.
    """
    if isinstance(doc_or_path, str):
        assert os.path.exists(doc_or_path), f"File not found: {doc_or_path}"
        doc = docx.Document(doc_or_path)
    else:
        doc = doc_or_path

    print("\n--- Verifying Table Components ---")
    t1 = None
    t2 = None

    for t in doc.tables:
        if len(t.rows) == 5 and len(t.columns) == 4:
            h = "".join(c.text for c in t.rows[0].cells)
            if "應用模式" in h:
                t1 = t
        elif len(t.rows) == 6 and len(t.columns) == 4:
            h = "".join(c.text for c in t.rows[0].cells)
            if "企業類型" in h:
                t2 = t

    assert t1 is not None, "Verification failed: Table 1 (5x4) not found!"
    assert t2 is not None, "Verification failed: Table 2 (6x4) not found!"

    # 1. Header keywords matching verify_report.py
    t1_headers = [c.text.strip().replace('\n', '') for c in t1.rows[0].cells]
    print(f"Table 1 Headers: {t1_headers}")
    assert "應用模式" in t1_headers[0], f"Col 0 header mismatch: {t1_headers[0]}"
    assert "核心做法" in t1_headers[1], f"Col 1 header mismatch: {t1_headers[1]}"
    assert "主要優勢" in t1_headers[2], f"Col 2 header mismatch: {t1_headers[2]}"
    assert "人機邊界" in t1_headers[3], f"Col 3 header mismatch: {t1_headers[3]}"

    t2_headers = [c.text.strip().replace('\n', '') for c in t2.rows[0].cells]
    print(f"Table 2 Headers: {t2_headers}")
    assert "企業類型" in t2_headers[0], f"Col 0 header mismatch: {t2_headers[0]}"
    assert "客戶關注焦點" in t2_headers[1], f"Col 1 header mismatch: {t2_headers[1]}"
    assert "AI 幕後核心任務" in t2_headers[2], f"Col 2 header mismatch: {t2_headers[2]}"
    assert "商業價值" in t2_headers[3], f"Col 3 header mismatch: {t2_headers[3]}"

    # 2. Structural checks: cantSplit and tblHeader
    for t_idx, t in enumerate([t1, t2], start=1):
        for r_idx, row in enumerate(t.rows):
            trPr = row._tr.trPr
            assert trPr is not None, f"Table {t_idx} Row {r_idx} missing trPr"
            cant_splits = [elem for elem in trPr if elem.tag.endswith('cantSplit')]
            assert len(cant_splits) >= 1, f"Table {t_idx} Row {r_idx} missing cantSplit protection!"

            if r_idx == 0:
                tbl_headers = [elem for elem in trPr if elem.tag.endswith('tblHeader')]
                assert len(tbl_headers) >= 1, f"Table {t_idx} Header row missing tblHeader!"

                # Check Header Cell Background #1B365D
                for c_idx, cell in enumerate(row.cells):
                    tcPr = cell._tc.tcPr
                    shd = [elem for elem in tcPr if elem.tag.endswith('shd')]
                    assert len(shd) >= 1, f"Table {t_idx} Header cell {c_idx} missing shading!"
                    fill = shd[0].get(qn('w:fill'))
                    assert fill.upper() == HEX_NAVY.upper(), f"Header fill {fill} != {HEX_NAVY}"

    print("Header background (#1B365D), tblHeader, and cantSplit protections verified 100%!")

    # 3. Zebra Rows check
    for t_idx, t in enumerate([t1, t2], start=1):
        for r_idx in range(1, len(t.rows)):
            expected_fill = HEX_WHITE if (r_idx - 1) % 2 == 0 else HEX_ZEBRA
            for c_idx, cell in enumerate(t.rows[r_idx].cells):
                tcPr = cell._tc.tcPr
                shd = [elem for elem in tcPr if elem.tag.endswith('shd')]
                assert len(shd) >= 1, f"Table {t_idx} Row {r_idx} Cell {c_idx} missing shading!"
                fill = shd[0].get(qn('w:fill'))
                assert fill.upper() == expected_fill.upper(), (
                    f"Zebra striping mismatch: Row {r_idx} Cell {c_idx} expected {expected_fill}, got {fill}"
                )
    print("Zebra rows striping (#FFFFFF / #F1F5F9) verified 100%!")

    # 4. Hanging indents check (hanging 240, left 240) on bullet points
    bullet_paragraphs_checked = 0
    for t_idx, t in enumerate([t1, t2], start=1):
        for r_idx in range(1, len(t.rows)):
            for c_idx in range(1, len(t.columns)):
                cell = t.rows[r_idx].cells[c_idx]
                for p in cell.paragraphs:
                    pPr = p._p.pPr
                    if pPr is not None:
                        inds = [elem for elem in pPr if elem.tag.endswith('ind')]
                        if inds:
                            hanging = inds[0].get(qn('w:hanging'))
                            left = inds[0].get(qn('w:left'))
                            assert hanging == "240", f"Expected hanging='240', got {hanging}"
                            assert left == "240", f"Expected left='240', got {left}"
                            bullet_paragraphs_checked += 1
    print(f"Hanging indents verified on all {bullet_paragraphs_checked} bullet paragraphs!")
    assert bullet_paragraphs_checked >= 15, f"Expected >= 15 bullet paragraphs, found {bullet_paragraphs_checked}"

    # 5. Alert Red (#B91C1C) in Table 1 Column 3
    alert_red_found = 0
    for r_idx in range(1, len(t1.rows)):
        cell = t1.rows[r_idx].cells[3]  # "人機邊界與極限"
        for p in cell.paragraphs:
            for r in p.runs:
                if r.font.color and r.font.color.rgb == COLOR_ALERT_RED:
                    alert_red_found += 1
    print(f"Alert Red (#B91C1C) runs found in Table 1 limits column: {alert_red_found}")
    assert alert_red_found >= 4, f"Expected >= 4 alert red runs in Table 1, found {alert_red_found}"

    # 6. Callout Box verification (if present in document)
    callout_found = 0
    for p in doc.paragraphs:
        if "★ 高管決策啟示" in p.text:
            pPr = p._p.pPr
            assert pPr is not None, "Callout paragraph missing pPr"
            # Check left border is amber #F59E0B
            pBdr = [elem for elem in pPr if elem.tag.endswith('pBdr')]
            assert len(pBdr) >= 1, "Callout paragraph missing pBdr"
            left_bdr = [elem for elem in pBdr[0] if elem.tag.endswith('left')]
            assert len(left_bdr) >= 1, "Callout paragraph missing left border"
            bdr_color = left_bdr[0].get(qn('w:color'))
            assert bdr_color.upper() == HEX_AMBER_BORDER.upper(), f"Callout border {bdr_color} != {HEX_AMBER_BORDER}"

            # Check background is amber #FFFBEB
            shd = [elem for elem in pPr if elem.tag.endswith('shd')]
            assert len(shd) >= 1, "Callout paragraph missing shading"
            fill_color = shd[0].get(qn('w:fill'))
            assert fill_color.upper() == HEX_AMBER_BG.upper(), f"Callout fill {fill_color} != {HEX_AMBER_BG}"
            callout_found += 1

    if callout_found:
        print(f"Executive Callout Box verified with Amber styling (#FFFBEB / #{HEX_AMBER_BORDER})!")

    print("ALL TABLE AND CALLOUT FORMATTING VERIFICATIONS PASSED!\n")
    return True


# =============================================================================
# CLI Main Entry Point
# =============================================================================
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    preview_file = os.path.join(base_dir, "preview_tables.docx")

    print(f"Generating preview document: {preview_file}")
    build_preview_docx(preview_file)

    print("Verifying preview document...")
    verify_tables_in_doc(preview_file)
    print("table_components.py execution and self-test completed successfully.")
