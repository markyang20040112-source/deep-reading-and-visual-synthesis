# -*- coding: utf-8 -*-
"""
apply_perfect_step2.py
Applies the 7.30" ultra-wide full-bleed layout and panoramic figures to 楊亞恩.docx:
1. Replaces images for Fig 1, Fig 2, Fig 3, Fig 4, Fig 5 with high-resolution 18-inch widescreen assets.
2. In image paragraphs, writes:
   <w:jc w:val="center"/>
   <w:ind w:left="-720" w:right="-720" w:firstLine="0" w:firstLineChars="0"/>
3. Explicitly sets image width to Inches(7.30) (approx 18.54 cm, leaving 0.48" symmetric safe margins).
4. Caption paragraphs formatted with w:firstLine="0" w:firstLineChars="0" and center alignment.
5. Absolute safety: ONLY modifies project docx, NEVER touches Desktop.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

BASE_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩"
DOCX_PATH = os.path.join(BASE_DIR, "楊亞恩.docx")
ASSETS_DIR = os.path.join(BASE_DIR, "assets_原始素材與圖表")

FIG1_PATH = os.path.join(ASSETS_DIR, "fig1_cdo_dual_panel.png")
FIG2_PATH = os.path.join(ASSETS_DIR, "fig2_brain_architecture.png")
FIG3_PATH = os.path.join(ASSETS_DIR, "fig3_price_sensitivity_confounding.png")
FIG4_PATH = os.path.join(ASSETS_DIR, "fig4_customer_value_gap.png")
FIG5_PATH = os.path.join(ASSETS_DIR, "fig5_ecosystem_mindmap.png")

# Verify all source images exist
for name, pth in [("Fig 1", FIG1_PATH), ("Fig 2", FIG2_PATH), ("Fig 3", FIG3_PATH), ("Fig 4", FIG4_PATH), ("Fig 5", FIG5_PATH)]:
    if not os.path.exists(pth):
        raise FileNotFoundError(f"Missing {name} at {pth}")
    print(f"Verified image: {name} -> {pth} ({os.path.getsize(pth):,} bytes)")


def configure_image_paragraph(p_img, img_path, width_in=7.30):
    """Sets image with exact 7.30" width and negative margin -720 dxa centering."""
    p_img.paragraph_format.line_spacing = 1.0
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(4)
    p_img.paragraph_format.keep_with_next = True

    # Clear existing runs
    for r in list(p_img.runs):
        p_img._p.remove(r._r)

    # Clean existing <w:ind> and <w:jc> elements to prevent invalid OOXML duplicates
    pPr = p_img._p.get_or_add_pPr()
    for child in list(pPr):
        if child.tag.endswith('ind') or child.tag.endswith('jc'):
            pPr.remove(child)

    # Append exact requested XML specifications
    pPr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>'))
    pPr.append(parse_xml(f'<w:ind {nsdecls("w")} w:left="-720" w:right="-720" w:firstLine="0" w:firstLineChars="0"/>'))

    # Add image run with explicit width
    r_img = p_img.add_run()
    r_img.add_picture(img_path, width=Inches(width_in))
    print(f"  Configured img (width={width_in}in, left=-720, right=-720, center)")


def configure_caption_paragraph(p_cap, caption_text):
    """Configures caption paragraph format and text."""
    p_cap.paragraph_format.line_spacing = 1.15
    p_cap.paragraph_format.space_before = Pt(3)
    p_cap.paragraph_format.space_after = Pt(12)

    # Clear existing runs
    for r in list(p_cap.runs):
        p_cap._p.remove(r._r)

    # Clean existing <w:ind> and <w:jc>
    pPr = p_cap._p.get_or_add_pPr()
    for child in list(pPr):
        if child.tag.endswith('ind') or child.tag.endswith('jc'):
            pPr.remove(child)

    pPr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>'))
    pPr.append(parse_xml(f'<w:ind {nsdecls("w")} w:left="0" w:right="0" w:firstLine="0" w:firstLineChars="0"/>'))

    r_cap = p_cap.add_run(caption_text)
    r_cap.font.name = '標楷體'
    r_cap.font.size = Pt(10.5)
    r_cap.font.bold = True
    r_cap.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
    r_cap._r.get_or_add_rPr().append(parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="標楷體" w:ascii="標楷體" w:hAnsi="標楷體"/>'))


def execute():
    print(f"\nOpening document: {DOCX_PATH}")
    doc = docx.Document(DOCX_PATH)

    # Figures configuration:
    # All 5 figures set to 7.30 inches full-bleed
    figures = [
        (56, 57, FIG1_PATH, 7.30, "圖一：2024 全球數據長（CDO）實證調查：企業 AI 商業預期（80%）與核心投產（6%）之準備度大斷崖暨成熟度結構"),
        (66, 67, FIG2_PATH, 7.30, "圖二：人機協同數據治理大腦架構圖（剛性數據辭典、靈活大模型、人類專家防線）"),
        (76, 77, FIG3_PATH, 7.30, "圖三：生成式 AI 市場研究之「價格敏感度混淆」實證實驗（真實消費者 vs. AI 模擬受訪者）"),
        (96, 97, FIG4_PATH, 7.30, "圖四：高管直覺客戶重視價值與現實落差（主觀重要性 vs. 客戶真實權重與營收轉換率）"),
        (111, 112, FIG5_PATH, 7.30, "圖五：顧客-企業-投資者關係生態心智圖（造血發動機 vs. 資本助燃劑健康循環）")
    ]

    for p_img_idx, p_cap_idx, img_path, w_in, cap_text in figures:
        p_img = doc.paragraphs[p_img_idx]
        p_cap = doc.paragraphs[p_cap_idx]
        print(f"Updating Fig at P{p_img_idx}/P{p_cap_idx}: {cap_text[:35]}...")
        configure_image_paragraph(p_img, img_path, width_in=w_in)
        configure_caption_paragraph(p_cap, cap_text)

    # Save ONLY to project docx
    doc.save(DOCX_PATH)
    print(f"\nSUCCESS: Updated {DOCX_PATH} with 7.30\" ultra-wide layout for all 5 figures.")


if __name__ == "__main__":
    execute()
