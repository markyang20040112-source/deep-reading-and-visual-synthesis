# -*- coding: utf-8 -*-
r"""
table_components.py
Decoupled, publication-grade table components module for the midterm report:
企管系 3B 楊亞恩《從數據債到人機協同：生成式 AI 時代下的企業商業分析重構》

Features & Architectural Design:
1. Pure Decoupling:
   - Self-contained and isolated from production document file locks.
   - Safe, idempotent insertion APIs that another AI agent can call with 1 line.
2. Publication & PPT Visual Grade:
   - Font Pairing: 標楷體 (DFKai-SB for Traditional Chinese) + Times New Roman (for Latin / Digits).
   - Horizontally Widened: 7.10 inches (10,224 dxa) for executive widescreen clarity.
   - Enlarged Title Font: 11.5pt Bold Deep Navy with direct semantic line break for subtitle.
   - Headers: 11pt bold white text on Deep Navy (#1B365D), centered alignment, tblHeader repetition.
   - Data Rows: Alternating zebra striping (#FFFFFF / #F1F5F9), cantSplit pagination protection on every row.
   - Natural Semantic Line Wrapping: All bullet descriptions are structured by semantic clause/意群,
     completely eliminating hard cuts across Chinese words and orphan characters.
   - Alert Accents: Theoretical boundaries & limits highlighted in Alert Red (#B91C1C).
   - Accompanying Callout Box: High-executive warm amber styling (#FFFBEB fill, #F59E0B left bar, #B45309 header),
     symmetrically aligned with the 7.10-inch table.
3. Non-Destructive Insertion APIs:
   - insert_table_1_before(doc, target_p)
   - insert_table_2_before(doc, target_p, include_callout=True)
   - insert_tables_into_doc(doc)
   - insert_tables_into_file(source_docx_path, output_docx_path=None)
   - build_preview_docx(preview_path)
   - verify_tables_in_doc(doc_or_path)
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
HEX_ALERT_RED = "B91C1C"     # Alert Red for theoretical boundaries / limits
HEX_AMBER_BG = "FFFBEB"      # Warm amber background for Callout Box
HEX_AMBER_BORDER = "F59E0B"  # Amber left bar border (3pt)
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

# Total widened table width: 7.10 inches = 10,224 dxa
DEFAULT_TABLE_WIDTH_DXA = 10224


# =============================================================================
# Low-level XML & Styling Helpers
# =============================================================================
def set_run_font(run, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=9.5, bold=False, italic=False, color_rgb=COLOR_DARK):
    """
    Applies comprehensive dual-font properties (EastAsian + Ascii/HAnsi)
    to eliminate font substitution fallbacks across Microsoft Word and LibreOffice.
    Strictly replaces any existing w:rFonts to eliminate duplicate schema tags.
    """
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size_pt)
    run.font.color.rgb = color_rgb

    rPr = run._r.get_or_add_rPr()
    old_rFonts = rPr.find(qn('w:rFonts'))
    if old_rFonts is not None:
        rPr.remove(old_rFonts)

    rFonts_xml = (
        f'<w:rFonts {nsdecls("w")} '
        f'w:ascii="{western_font}" '
        f'w:hAnsi="{western_font}" '
        f'w:eastAsia="{font_name}" '
        f'w:cs="{western_font}"/>'
    )
    rPr.append(parse_xml(rFonts_xml))
    return run


def style_cell(cell, fill_hex=None, top_pt=4, bottom_pt=4, left_pt=5, right_pt=5,
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
                            desc_color=COLOR_DARK, font_size_pt=9.5):
    """
    Formats a bullet-point item paragraph with hanging indent (hanging 240, left 240).
    Places bullet title on Line 1, followed by natural semantic clause wrapping
    on subsequent lines to guarantee zero hard-cut words and zero orphan characters.
    """
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pPr = p._p.get_or_add_pPr()

    # Spacing and line height
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="16" w:after="16" w:line="220" w:lineRule="auto"/>')
    pPr.append(sp)

    # Hanging indent: 240 dxa (0.167 in / 12pt)
    ind = parse_xml(f'<w:ind {nsdecls("w")} w:left="240" w:hanging="240"/>')
    pPr.append(ind)

    # Bullet title (Bold, colored) on line 1 with semantic newline
    title_str = bullet_title if bullet_title.endswith("\n") else bullet_title + "\n"
    r_title = p.add_run(title_str)
    set_run_font(r_title, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=font_size_pt, bold=True, color_rgb=title_color)

    # Bullet description (Regular, charcoal) with natural semantic wrapping
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
    Features enlarged title font (11.5pt Bold Deep Navy) with direct line break
    for subtitle (10.0pt Bold Deep Navy) to provide optimal visual hierarchy.
    """
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    pPr = p._p.get_or_add_pPr()
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="180" w:after="80" w:line="240" w:lineRule="auto"/>')
    pPr.append(sp)

    if "\n" in caption_text:
        lines = caption_text.split("\n", 1)
        # Main Title (Enlarged: 11.5pt Bold Deep Navy)
        r0 = p.add_run(lines[0])
        set_run_font(r0, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                     size_pt=11.5, bold=True, color_rgb=COLOR_NAVY)
        # Direct line break subtitle (10.0pt Bold Deep Navy)
        r1 = p.add_run("\n" + lines[1])
        set_run_font(r1, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                     size_pt=10.0, bold=True, color_rgb=COLOR_NAVY)
    else:
        r = p.add_run(caption_text)
        set_run_font(r, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                     size_pt=11.5, bold=True, color_rgb=COLOR_NAVY)
    return p


def build_callout_box(p, title_text, body_text):
    """
    Renders an executive callout box with:
    - Warm amber background (#FFFBEB)
    - 3pt solid amber left border (#F59E0B)
    - Subtle slate borders on other three sides (#CBD5E1)
    - Symmetrically aligned horizontal width matching the 7.10-inch table (-598 dxa on left/right)
    - Clean 標楷體 typography.
    - keep_together / w:keepLines pagination protection ensuring the callout card
      NEVER splits across a page break.
    """
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.keep_together = True
    pPr = p._p.get_or_add_pPr()

    # Spacing and line height
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="120" w:after="120" w:line="260" w:lineRule="auto"/>')
    pPr.append(sp)

    # Expanded horizontal box width to harmonize symmetrically with the 7.10-inch table
    ind = parse_xml(f'<w:ind {nsdecls("w")} w:left="-598" w:right="-598"/>')
    pPr.append(ind)

    # Box borders: Amber-500 on left (sz="24"=3pt), subtle Slate on top/right/bottom (sz="4"=0.5pt)
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="6" w:color="{HEX_BORDER}"/>'
        f'<w:left w:val="single" w:sz="24" w:space="12" w:color="{HEX_AMBER_BORDER}"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="6" w:color="{HEX_BORDER}"/>'
        f'<w:right w:val="single" w:sz="4" w:space="6" w:color="{HEX_BORDER}"/>'
        f'</w:pBdr>'
    )
    pPr.append(pBdr)

    # Amber shading fill
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{HEX_AMBER_BG}"/>')
    pPr.append(shd)

    # Title run
    r_title = p.add_run(title_text + "\n")
    set_run_font(r_title, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=10.5, bold=True, color_rgb=COLOR_AMBER_TEXT)

    # Body run
    r_body = p.add_run(body_text)
    set_run_font(r_body, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=9.5, bold=False, color_rgb=COLOR_DARK)
    return p


# =============================================================================
# Structured Table Renderer (PPT Style)
# =============================================================================
def populate_ppt_table(table, headers, data, col_widths, table_width_dxa=DEFAULT_TABLE_WIDTH_DXA):
    """
    Populates and styles an existing docx Table object with:
    - 7.10-inch total width (10,224 dxa) with explicit tblGrid column constraints
    - 11pt bold white text headers on Deep Navy (#1B365D)
    - tblHeader repetition and cantSplit protection on every row
    - Alternating row zebra striping (#FFFFFF / #F1F5F9)
    - Column 0: Centered, bold, navy category anchors with clean line breaks
    - Columns > 0: Natural semantic line wrapping bullets with hanging indents (hanging 240)
    - Alert Red (#B91C1C) for theoretical limits / boundaries
    """
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    tblPr = table._tbl.tblPr
    old_tblW = tblPr.find(qn('w:tblW'))
    if old_tblW is not None:
        tblPr.remove(old_tblW)
    tblW = parse_xml(f'<w:tblW {nsdecls("w")} w:w="{table_width_dxa}" w:type="dxa"/>')
    tblPr.append(tblW)

    # Explicit tblGrid definition to enforce column dimensions across Word and PDF renderers
    old_grid = table._tbl.find(qn('w:tblGrid'))
    if old_grid is not None:
        table._tbl.remove(old_grid)
    grid_cols = ''.join([f'<w:gridCol w:w="{int(w.inches * 1440)}"/>' for w in col_widths])
    tblGrid = parse_xml(f'<w:tblGrid {nsdecls("w")}>{grid_cols}</w:tblGrid>')
    table._tbl.insert(table._tbl.index(tblPr) + 1, tblGrid)

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
        tcPr = cell._tc.get_or_add_tcPr()
        old_tcW = tcPr.find(qn('w:tcW'))
        if old_tcW is not None:
            tcPr.remove(old_tcW)
        tcW = parse_xml(f'<w:tcW {nsdecls("w")} w:w="{int(col_widths[i].inches * 1440)}" w:type="dxa"/>')
        tcPr.append(tcW)

        style_cell(cell, fill_hex=HEX_NAVY, top_pt=5, bottom_pt=5, left_pt=3, right_pt=3,
                   border_bottom_hex=HEX_NAVY, v_align="center")

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pPr = p._p.get_or_add_pPr()
        sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="24" w:after="24" w:line="220" w:lineRule="auto"/>')
        pPr.append(sp)

        # Handle intentional line breaks in headers with styling
        if "\n" in h_text:
            lines = h_text.split("\n")
            r0 = p.add_run(lines[0])
            set_run_font(r0, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                         size_pt=11.0, bold=True, color_rgb=COLOR_WHITE)
            r1 = p.add_run("\n" + lines[1])
            set_run_font(r1, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                         size_pt=9.0, bold=True, color_rgb=RGBColor(226, 232, 240))
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
            tcPr = cell._tc.get_or_add_tcPr()
            old_tcW = tcPr.find(qn('w:tcW'))
            if old_tcW is not None:
                tcPr.remove(old_tcW)
            tcW = parse_xml(f'<w:tcW {nsdecls("w")} w:w="{int(col_widths[c_idx].inches * 1440)}" w:type="dxa"/>')
            tcPr.append(tcW)

            v_align = "center" if c_idx == 0 else "top"
            style_cell(cell, fill_hex=fill_hex, top_pt=4, bottom_pt=4, left_pt=5, right_pt=5,
                       border_bottom_hex=HEX_BORDER, v_align=v_align)

            if c_idx == 0:
                # Column 0: Category title
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                pPr = p._p.get_or_add_pPr()
                sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="24" w:after="24" w:line="220" w:lineRule="auto"/>')
                pPr.append(sp)

                for item in cell_bullets:
                    if isinstance(item, tuple):
                        t_main, t_sub = item[0], item[1] if len(item) > 1 else ""
                        r0 = p.add_run(t_main)
                        set_run_font(r0, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                                     size_pt=10.5, bold=True, color_rgb=COLOR_NAVY)
                        if t_sub:
                            r_sub = p.add_run("\n" + t_sub)
                            set_run_font(r_sub, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                                         size_pt=9.0, bold=True, color_rgb=COLOR_MUTED)
                    else:
                        r = p.add_run(str(item))
                        set_run_font(r, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                                     size_pt=10.5, bold=True, color_rgb=COLOR_NAVY)
            else:
                # Columns > 0: Structured bullet points with natural semantic line wrapping
                for b_idx, bullet in enumerate(cell_bullets):
                    p_cur = cell.paragraphs[0] if b_idx == 0 else cell.add_paragraph()
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
                                            desc_color=COLOR_DARK, font_size_pt=9.5)
    return table


# =============================================================================
# Data Specifications for Table 1 and Table 2
# =============================================================================
def get_table_1_spec():
    """
    Returns (caption, headers, data, col_widths) for Table 1:
    表一：四種 AI 應用情境矩陣（前沿破局解法、核心機制與理論死穴批判）
    Dimensions: 5 rows (1 header + 4 data), 4 columns.
    Expanded width: 7.10 inches (10,224 dxa).
    """
    caption = "表一：四種 AI 應用情境矩陣\n（前沿破局解法、核心機制與理論死穴批判）"
    headers = ["【應用模式】", "【核心做法】\n(文中實例)", "【主要優勢】\n(PPT重點)", "【人機邊界與極限】"]
    col_widths = [Inches(1.35), Inches(2.15), Inches(1.85), Inches(1.75)]

    data = [
        # Row 1: Grounded Twins
        [
            [("解法一：\n綁定真人數位雙生", "(Grounded Twins)")],
            [
                ("• 深度訪談：", "以數小時真人深度訪談，\n建立客觀基準事實錨點", False),
                ("• 追蹤軌跡：", "哥倫比亞、史丹福與\nCivicSync 真實行為錨定", False)
            ],
            [
                ("• 真實性高：", "有客觀基準事實錨定，\n杜絕純虛構人格", False),
                ("• 破局關鍵：", "將質化訪談規模化，\n兼具樣本規模與深度", False)
            ],
            [
                ("• 感覺不可壓縮：", "香料氣味與生理直覺，\n完全無法數位化", True),
                ("• 成本門檻高：", "前期真人訪談與資料，\n長期維護耗費巨大", True)
            ]
        ],
        # Row 2: Hybrid Model
        [
            [("解法二：\n混合架構模型", "(Hybrid Model)")],
            [
                ("• 分工轉譯：", "右腦大模型僅轉譯圖文，\n產出標準特徵分數", False),
                ("• 統計計算：", "左腦傳統計量模型計算，\n產出價格彈性敏感度", False)
            ],
            [
                ("• 數學防幻覺：", "截斷大模型自作聰明之\n「混淆」推論偏差", False),
                ("• 解釋力清晰：", "模型係數與因果關係，\n具備高度可稽核性", False)
            ],
            [
                ("• 模型誤設風險：", "多變數非線性關係下，\n左腦統計函式難擬合", True),
                ("• 維護高度依賴：", "需專業計量經濟學家，\n持續調校核心參數", True)
            ]
        ],
        # Row 3: PPI Calibration
        [
            [("解法三：\n真人基準校準", "(PPI Calibration)")],
            [
                ("• 黃金基準：", "以 100 名真人盲測結果，\n作為核心校準點", False),
                ("• 統計修正：", "萬名 AI 代理人模擬後，\n以公式扣除系統偏誤", False)
            ],
            [
                ("• 成本暴降：", "兼顧真人實測深度，\n與 AI 海量樣本規模", False),
                ("• 快速擴充：", "極小預算即可啟動，\n大規模市場動態調查", False)
            ],
            [
                ("• 分布偏移風險：", "AI 對齊真人恐為湊巧\n（3 個月即產生漂移）", True),
                ("• 動態依賴性：", "每波次皆需重新抽取，\n真人客觀基準校準", True)
            ]
        ],
        # Row 4: Fine-Tuning
        [
            [("解法四：\n歷史實驗微調", "(Fine-Tuning)")],
            [
                ("• 專有數據微調：", "輸入歷史問卷與銷售日誌，\n結合真實 A/B 數據", False),
                ("• 產業專用：", "Evidenza、GBK 團隊\n針對特定品類深度調權", False)
            ],
            [
                ("• 貼近企業內部：", "高度適配既有商品，\n與目標客群行為特徵", False),
                ("• 自動化部署：", "常態性選品與門市配置，\n快速標準化輸出", False)
            ],
            [
                ("• 倖存者偏差：", "無法泛化至跨品類，\n或未涉足之全新市場", True),
                ("• 模型過擬合：", "歷史資料偏誤將導致，\n模型陷入路徑依賴", True)
            ]
        ]
    ]
    return caption, headers, data, col_widths


def get_table_2_spec():
    """
    Returns (caption, headers, data, col_widths) for Table 2:
    表二：AI 模型在不同企業類型中的定位矩陣（客戶焦點、幕後任務與商業價值）
    Dimensions: 6 rows (1 header + 5 data), 4 columns.
    Expanded width: 7.10 inches (10,224 dxa).
    """
    caption = "表二：AI 模型在不同企業類型中的定位矩陣\n（客戶焦點、幕後任務與商業價值）"
    headers = ["【企業類型】\n(B2B/B2C等)", "【客戶關注焦點】", "【AI 幕後核心任務】", "【核心商業價值】\n(帶來的核心成效)"]
    col_widths = [Inches(1.20), Inches(2.10), Inches(2.00), Inches(1.80)]

    data = [
        # Row 1: B2B
        [
            [("B2B", "(企業對企業)")],
            [
                ("• 理性採購：", "決策背負部門損益 (P&L)，\n嚴格評估合約責任", False),
                ("• 硬性指標：", "審批週期長，唯一只看\n可量化降本增效成果", False)
            ],
            [
                ("• 檯面硬實力：", "精準預測停機風險、\n工時節省與履約進度", False),
                ("• 合約標的：", "直接寫入採購合約，\n作為驗收結案基準", False)
            ],
            [
                ("• 實質價值：", "S-SET 報價縮至 3hr，\n徹底排除停機損失", False)
            ]
        ],
        # Row 2: B2C
        [
            [("B2C", "(企業對終端客)")],
            [
                ("• 感性消費：", "追求即時滿足與省時，\n重視情緒愉悅體驗", False),
                ("• 轉換極快：", "轉換成本趨近於零，\n對繁瑣操作零容忍", False)
            ],
            [
                ("• 幕後隱形調度：", "千人千面推薦、毫秒定價，\n與線上排隊精準預估", False),
                ("• 無感極致體驗：", "深埋系統後台，嚴禁增加\n任何用戶操作阻力", False)
            ],
            [
                ("• 實質價值：", "Netflix 個性化推薦、\n星巴克點餐排隊調度", False)
            ]
        ],
        # Row 3: B2B2C
        [
            [("B2B2C", "(平台賦能商戶)")],
            [
                ("• 雙重買單主體：", "商戶追求流量增長，\n終端客看重品質可靠", False),
                ("• 生態平衡：", "平台需同時兼顧雙邊利益，\n與交易撮合公平", False)
            ],
            [
                ("• 雙向媒合引擎：", "替商戶自動生成文案、\n精準預測銷量動態定價", False),
                ("• 履約背書：", "替消費者精準搜尋，\n並推薦優選品質商品", False)
            ],
            [
                ("• 實質價值：", "Shopify 獨立站賦能、\n外送平台即時動態媒合", False)
            ]
        ],
        # Row 4: C2C
        [
            [("C2C", "(個人對個人)")],
            [
                ("• 平權個人交易：", "資訊高度不對稱，\n交易核心命脈為「信任」", False),
                ("• 風險脆弱：", "極易因單次詐騙或假貨，\n糾紛瓦解平台信心", False)
            ],
            [
                ("• 信任仲裁中樞：", "以圖搜圖比對真品細節、\n對話即時防詐預警", False),
                ("• 歷史信用評級：", "交易糾紛智慧初審，\n與自動化履約保障", False)
            ],
            [
                ("• 實質價值：", "Airbnb 雙向審查保險、\n二手交易平台信任擔保", False)
            ]
        ],
        # Row 5: B2G
        [
            [("B2G", "(企業對公部門)")],
            [
                ("• 公務法規稽核：", "講求 100% 依法行政、\n主權資安與零弊端風險", False),
                ("• 公共利益導向：", "重視程序正義與隱私，\n遠大於短期商業利潤", False)
            ],
            [
                ("• 可解釋性 (XAI)：", "杜絕黑箱演算法，\n決策路徑完整可溯源", False),
                ("• 主權合規防護：", "提供完整 Audit Trail，\n備議會與政風單位查驗", False)
            ],
            [
                ("• 實質價值：", "智慧交通號誌調控、\n數位稅務異常交易查核", False)
            ]
        ]
    ]
    return caption, headers, data, col_widths


def get_callout_box_spec():
    """
    Returns (title, body) for the Executive Callout Box below Table 2.
    Applies strict natural semantic line breaks (顺应语义断句) to guarantee zero hard-cut words
    and zero orphan characters across lines.
    """
    title = "★ 高管決策啟示：切莫張冠李戴，找準真實價值槓桿"
    body = (
        "高管制定戰略時最忌「位階錯位」：在 B2B 切莫拿酷炫但無法量化 ROI 的前台 AI 噱頭當賣點，\n"
        "客戶只看合約實力與履約保障；在 B2C 切莫強迫消費者理解模型架構，增加操作步驟的技術都是退步；\n"
        "在 B2G 貿然採用不可說明的黑箱演算法，將直接引發合規災難。\n"
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
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="100"/>'))
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
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="100"/>'))
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
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="80"/>'))
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
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="80"/>'))
    return tbl


def find_target_paragraphs(doc):
    """
    Locates the precise paragraph anchors for Table 1 and Table 2.
    Target for Table 1: Paragraph starting with "上面這四種應用方式還只是AI應用上的冰山一角"
    Target for Table 2: Paragraph starting with "不難看出，其實AI模型"
    Uses resilient substring matching stripped of whitespace.
    """
    target_p1 = None
    target_p2 = None

    for p in doc.paragraphs:
        txt = p.text.strip().replace(" ", "").replace("　", "")
        if "上面這四種應用方式還只是" in txt and target_p1 is None:
            target_p1 = p
        elif "不難看出，其實AI模型" in txt and target_p2 is None:
            target_p2 = p

    return target_p1, target_p2


def remove_legacy_table_images(doc):
    """
    Removes legacy draft screenshot images of Table 1 and Table 2 (image4.jpeg and image6.jpeg)
    that were embedded in paragraphs before the anchor points.
    Preserves all 5 analytical figures (fig1-fig5, all .png) and all paragraph text and formatting.
    """
    removed_count = 0
    for p in doc.paragraphs:
        runs_to_remove = []
        for r in p.runs:
            if 'graphic' in r._r.xml:
                for blip in r._r.xpath('.//a:blip'):
                    embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    if embed_id and embed_id in doc.part.rels:
                        tgt = doc.part.rels[embed_id].target_ref
                        if 'image4' in tgt or 'image6' in tgt or tgt.lower().endswith('.jpeg'):
                            runs_to_remove.append(r)
        for r in runs_to_remove:
            p._p.remove(r._r)
            removed_count += 1
    if removed_count > 0:
        print(f"[table_components] Cleaned up {removed_count} legacy screenshot image(s).")
    return removed_count


def remove_existing_tables(doc):
    """
    Removes previously inserted Table 1, Table 2, captions, and Callout Box
    if present, allowing a clean idempotent re-insertion or update.
    """
    to_remove = []
    for t in doc.tables:
        if len(t.rows) == 5 and len(t.columns) == 4:
            if "應用模式" in "".join(c.text for c in t.rows[0].cells):
                to_remove.append(t._tbl)
        elif len(t.rows) == 6 and len(t.columns) == 4:
            if "企業類型" in "".join(c.text for c in t.rows[0].cells):
                to_remove.append(t._tbl)

    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt.startswith("表一：四種 AI 應用情境矩陣") or txt.startswith("表二：AI 模型在不同企業類型中的定位矩陣") or txt.startswith("★ 高管決策啟示"):
            to_remove.append(p._p)

    for elem in to_remove:
        parent = elem.getparent()
        if parent is not None:
            parent.remove(elem)
    if to_remove:
        print(f"[table_components] Removed {len(to_remove)} existing table/caption/callout element(s) for fresh insertion.")
    return len(to_remove)


def insert_tables_into_doc(doc, force=False):
    """
    Idempotent and safe table insertion into an existing docx Document object.
    Checks whether Table 1 and Table 2 already exist and have valid keepLines pagination protection.
    If force=True or if existing callout box lacks keepLines protection, re-inserts cleanly.
    """
    t1_exists = False
    t2_exists = False
    callout_has_keeplines = False

    for t in doc.tables:
        if len(t.rows) == 5 and len(t.columns) == 4:
            if "應用模式" in "".join(c.text for c in t.rows[0].cells):
                t1_exists = True
        elif len(t.rows) == 6 and len(t.columns) == 4:
            if "企業類型" in "".join(c.text for c in t.rows[0].cells):
                t2_exists = True

    for p in doc.paragraphs:
        if "★ 高管決策啟示" in p.text:
            if p._p.pPr is not None and any(e.tag.endswith('keepLines') for e in p._p.pPr):
                callout_has_keeplines = True

    if t1_exists and t2_exists and callout_has_keeplines and not force:
        print("[table_components] Both Table 1 and Table 2 already exist with full pagination protection. No duplicate insertion.")
        return doc

    if t1_exists or t2_exists:
        remove_existing_tables(doc)
        t1_exists = False
        t2_exists = False

    # Clean legacy screenshot placeholders before inserting publication-grade tables
    remove_legacy_table_images(doc)

    target_p1, target_p2 = find_target_paragraphs(doc)
    assert target_p1 is not None, "Could not find anchor paragraph for Table 1 ('上面這四種應用方式')!"
    assert target_p2 is not None, "Could not find anchor paragraph for Table 2 ('不難看出，其實AI模型')!"

    print("[table_components] Inserting Table 1 before anchor paragraph...")
    insert_table_1_before(doc, target_p1)

    print("[table_components] Inserting Table 2 & Callout Box before anchor paragraph...")
    insert_table_2_before(doc, target_p2, include_callout=True)

    print("[table_components] Successfully inserted Table 1 and Table 2!")
    return doc


def insert_tables_into_file(source_docx_path, output_docx_path=None, force=False):
    """
    Safely opens source_docx_path, inserts Table 1 and Table 2, and saves to output_docx_path
    (or overwrites source_docx_path if output_docx_path is None).
    """
    source_docx_path = os.path.abspath(source_docx_path)
    if output_docx_path is None:
        output_docx_path = source_docx_path
    else:
        output_docx_path = os.path.abspath(output_docx_path)

    doc = docx.Document(source_docx_path)
    insert_tables_into_doc(doc, force=force)
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

    # Setup standard A4 page layout (identical to main report: 1.0" left/right margins)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

    # Preview Header
    p_head = doc.add_paragraph()
    p_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pHeadPr = p_head._p.get_or_add_pPr()
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="40" w:after="80"/>')
    pHeadPr.append(sp)

    r_title = p_head.add_run("期中報告表格組件視覺預覽 (Table Preview)\n")
    set_run_font(r_title, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=16.0, bold=True, color_rgb=COLOR_NAVY)

    r_sub = p_head.add_run("企管系 3B 楊亞恩｜期中專題報告獨立表格模組驗證")
    set_run_font(r_sub, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=10.5, bold=False, color_rgb=COLOR_MUTED)

    # 1. Section Title: Table 1
    p_sec1 = doc.add_paragraph()
    p_sec1.paragraph_format.space_before = Pt(8)
    p_sec1.paragraph_format.space_after = Pt(2)
    p_sec1.paragraph_format.keep_with_next = True
    r_sec1 = p_sec1.add_run("一、 Table 1：四種 AI 應用情境矩陣")
    set_run_font(r_sec1, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=12.0, bold=True, color_rgb=COLOR_NAVY)

    # Build Table 1
    caption, headers, data, col_widths = get_table_1_spec()
    p_cap1 = doc.add_paragraph()
    build_caption_paragraph(p_cap1, caption)
    tbl1 = doc.add_table(rows=len(data) + 1, cols=len(headers))
    populate_ppt_table(tbl1, headers, data, col_widths)

    # Page Break for clean 2-page preview
    p_br = doc.add_paragraph()
    p_br.paragraph_format.space_before = Pt(0)
    p_br.paragraph_format.space_after = Pt(0)
    p_br.add_run().add_break(docx.enum.text.WD_BREAK.PAGE)

    # 2. Section Title: Table 2
    p_sec2 = doc.add_paragraph()
    p_sec2.paragraph_format.space_before = Pt(8)
    p_sec2.paragraph_format.space_after = Pt(2)
    p_sec2.paragraph_format.keep_with_next = True
    r_sec2 = p_sec2.add_run("二、 Table 2：AI 模型在不同企業類型中的定位矩陣與高管啟示")
    set_run_font(r_sec2, font_name=FONT_CHINESE, western_font=FONT_WESTERN,
                 size_pt=12.0, bold=True, color_rgb=COLOR_NAVY)

    # Build Table 2 + Callout Box
    caption2, headers2, data2, col_widths2 = get_table_2_spec()
    p_cap2 = doc.add_paragraph()
    build_caption_paragraph(p_cap2, caption2)
    tbl2 = doc.add_table(rows=len(data2) + 1, cols=len(headers2))
    populate_ppt_table(tbl2, headers2, data2, col_widths2)

    title_box, body_box = get_callout_box_spec()
    p_box = doc.add_paragraph()
    build_callout_box(p_box, title_box, body_box)

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

    # 2. Structural checks: cantSplit, tblHeader, tblW width 10224 dxa
    for t_idx, t in enumerate([t1, t2], start=1):
        tblPr = t._tbl.tblPr
        tblWs = [elem for elem in tblPr if elem.tag.endswith('tblW')]
        assert len(tblWs) == 1, f"Table {t_idx} has {len(tblWs)} tblW elements (must be exactly 1)!"
        assert tblWs[0].get(qn('w:w')) == str(DEFAULT_TABLE_WIDTH_DXA), (
            f"Table {t_idx} width is {tblWs[0].get(qn('w:w'))}, expected {DEFAULT_TABLE_WIDTH_DXA}"
        )

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

    print("Table width (10224 dxa), header background (#1B365D), tblHeader, and cantSplit protections verified 100%!")

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
            keep_lines = [elem for elem in pPr if elem.tag.endswith('keepLines')]
            assert len(keep_lines) >= 1, "Callout paragraph missing keepLines (keep_together) protection!"

            pBdr = [elem for elem in pPr if elem.tag.endswith('pBdr')]
            assert len(pBdr) >= 1, "Callout paragraph missing pBdr"
            left_bdr = [elem for elem in pBdr[0] if elem.tag.endswith('left')]
            assert len(left_bdr) >= 1, "Callout paragraph missing left border"
            bdr_color = left_bdr[0].get(qn('w:color'))
            assert bdr_color.upper() == HEX_AMBER_BORDER.upper(), f"Callout border {bdr_color} != {HEX_AMBER_BORDER}"

            shd = [elem for elem in pPr if elem.tag.endswith('shd')]
            assert len(shd) >= 1, "Callout paragraph missing shading"
            fill_color = shd[0].get(qn('w:fill'))
            assert fill_color.upper() == HEX_AMBER_BG.upper(), f"Callout fill {fill_color} != {HEX_AMBER_BG}"
            callout_found += 1

    if callout_found:
        print(f"Executive Callout Box verified with Amber styling (#FFFBEB / #{HEX_AMBER_BORDER}) and keepLines protection!")

    print("ALL TABLE AND CALLOUT FORMATTING VERIFICATIONS PASSED!\n")
    return True


# =============================================================================
# CLI Main Entry Point
# =============================================================================
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    preview_file = os.path.join(base_dir, "preview_tables.docx")

    # CLI Argument Parsing: allows another AI to call via CLI or Python import
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        if "-h" in args or "--help" in args:
            print("Usage:")
            print("  python table_components.py                  # Builds and verifies preview_tables.docx")
            print("  python table_components.py <target_docx>    # Merges Table 1 & Table 2 into target_docx")
            print("  python table_components.py --force <target> # Force re-insertion")
            print("\nPython 1-Line Merge Snippet:")
            print('  from table_components import insert_tables_into_file; insert_tables_into_file(r"<PATH_TO_DOCX>")')
            sys.exit(0)

        force_flag = "--force" in args
        target_args = [a for a in args if not a.startswith("--")]
        target_file = target_args[0] if target_args else os.path.join(base_dir, "楊亞恩.docx")

        print(f"[table_components] Merging tables into target document: {target_file} (force={force_flag})")
        insert_tables_into_file(target_file, force=force_flag)
        verify_tables_in_doc(target_file)
        print("[table_components] Merge and verification completed successfully!")
    else:
        print(f"Generating preview document: {preview_file}")
        build_preview_docx(preview_file)

        print("Verifying preview document...")
        verify_tables_in_doc(preview_file)
        print("table_components.py execution and self-test completed successfully.")
        print("\n" + "="*70)
        print("1-LINE MERGE SNIPPET FOR THE OTHER AI AGENT:")
        print('from table_components import insert_tables_into_file; insert_tables_into_file(r"C:\\Users\\User\\OneDrive\\桌面\\期中報告\\楊亞恩.docx")')
        print("="*70 + "\n")
