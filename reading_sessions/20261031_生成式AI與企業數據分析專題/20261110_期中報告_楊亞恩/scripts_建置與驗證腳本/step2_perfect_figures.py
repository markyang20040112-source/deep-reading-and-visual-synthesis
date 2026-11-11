# -*- coding: utf-8 -*-
"""
step2_perfect_figures.py
Executes Step 2: Optimizes, validates, and inserts Figures 1 to 5 into 楊亞恩.docx.
- Preserves Normal style formatting and all body text 100%.
- Centers all 5 figures at width 6.9 inches with negative margins (-400 dxa).
- Adds professional 10.5pt bold captions matching university submission quality.
- Strictly does NOT modify desktop files, and strictly leaves Tables (Step 3) and Links (Step 4) untouched.
"""

import os
import shutil
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

BASE_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩"
DOCX_PATH = os.path.join(BASE_DIR, "楊亞恩.docx")
ASSETS_DIR = os.path.join(BASE_DIR, "assets_原始素材與圖表")

# Target high-resolution images
FIG1_PATH = os.path.join(ASSETS_DIR, "fig1_cdo_dual_panel.png")
FIG2_PATH = os.path.join(ASSETS_DIR, "fig2_brain_architecture.png")
FIG3_PATH = os.path.join(ASSETS_DIR, "fig3_price_sensitivity_confounding.png")
FIG4_PATH = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261031_顧客需求與統計模型\02_outputs\03_quantitative_empirical_charts.png"
FIG5_PATH = os.path.join(ASSETS_DIR, "04_顧客-企業-投資者關係心智圖_橫版.png")

# Verify all source images exist
for name, pth in [("Fig 1", FIG1_PATH), ("Fig 2", FIG2_PATH), ("Fig 3", FIG3_PATH), ("Fig 4", FIG4_PATH), ("Fig 5", FIG5_PATH)]:
    if not os.path.exists(pth):
        raise FileNotFoundError(f"Missing {name} at {pth}")
    print(f"Verified image: {name} -> {pth} ({os.path.getsize(pth)} bytes)")


def insert_figure_with_caption(doc, ref_p, img_path, caption_text, width_in=6.9):
    """Inserts a full-bleed centered figure (6.9 in) and caption directly after ref_p."""
    # 1. Image paragraph
    p_img = doc.add_paragraph()
    ref_p._p.addnext(p_img._p)
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.first_line_indent = Pt(0)
    p_img.paragraph_format.line_spacing = 1.0
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(4)
    p_img.paragraph_format.keep_with_next = True

    pPr = p_img._p.get_or_add_pPr()
    ind_xml = f'<w:ind {nsdecls("w")} w:left="-400" w:right="-400" w:firstLine="0"/>'
    pPr.append(parse_xml(ind_xml))

    r_img = p_img.add_run()
    r_img.add_picture(img_path, width=Inches(width_in))

    # 2. Caption paragraph
    p_cap = doc.add_paragraph()
    p_img._p.addnext(p_cap._p)
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.first_line_indent = Pt(0)
    p_cap.paragraph_format.line_spacing = 1.15
    p_cap.paragraph_format.space_before = Pt(3)
    p_cap.paragraph_format.space_after = Pt(12)

    r_cap = p_cap.add_run(caption_text)
    r_cap.font.name = '標楷體'
    r_cap.font.size = Pt(10.5)
    r_cap.font.bold = True
    r_cap.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
    r_cap._r.get_or_add_rPr().append(parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="標楷體" w:ascii="標楷體" w:hAnsi="標楷體"/>'))

    return p_img, p_cap


def execute():
    print(f"Opening document: {DOCX_PATH}")
    doc = docx.Document(DOCX_PATH)

    # 1. Identify all 5 target paragraphs
    targets = {}
    for i, p in enumerate(doc.paragraphs):
        has_g = any('graphic' in r._element.xml for r in p.runs)
        if has_g:
            if "這時人們就發現" in p.text:
                targets['fig1'] = i
            elif len(p.text.strip()) == 0 and 60 < i < 85:
                targets['fig2'] = i
            elif "在這裡我想分享文章中提到的兩個" in p.text:
                targets['fig3'] = i
            elif "高層認為重要的價值驅動因素與顧客真實重視的事物" in p.text:
                targets['fig4'] = i
            elif "在大部分的情況下企業與客戶才是主要在製造經濟循環的關係" in p.text:
                targets['fig5'] = i

    print("Target paragraph indices identified:", targets)
    assert len(targets) == 5, f"Expected 5 targets, found: {targets}"

    # -------------------------------------------------------------------------
    # Process from bottom to top (highest index to lowest index)
    # -------------------------------------------------------------------------

    # --- FIGURE 5 (Target: P127) ---
    p5 = doc.paragraphs[targets['fig5']]
    print(f"\nProcessing Fig 5 at P{targets['fig5']}: {repr(p5.text[:35])}")
    for r in list(p5.runs):
        if 'graphic' in r._element.xml:
            p5._p.remove(r._r)
            print("  Removed inline graphic from Fig 5 text paragraph.")
    insert_figure_with_caption(
        doc, p5, FIG5_PATH,
        "圖五：顧客-企業-投資者關係生態心智圖（造血發動機 vs. 資本助燃劑健康循環）",
        width_in=6.9
    )
    print("  Inserted Fig 5 with negative margin -400 dxa and caption.")

    # --- FIGURE 4 (Target: P114) ---
    p4 = doc.paragraphs[targets['fig4']]
    print(f"\nProcessing Fig 4 at P{targets['fig4']}: {repr(p4.text[:35])}")
    for r in list(p4.runs):
        if 'graphic' in r._element.xml:
            p4._p.remove(r._r)
            print("  Removed inline graphic from Fig 4 text paragraph.")
    insert_figure_with_caption(
        doc, p4, FIG4_PATH,
        "圖四：高管直覺客戶重視價值與現實落差（主觀重要性 vs. 客戶真實權重與營收轉換率）",
        width_in=6.9
    )
    print("  Inserted Fig 4 with negative margin -400 dxa and caption.")

    # --- FIGURE 3 (Target: P96) ---
    p3 = doc.paragraphs[targets['fig3']]
    print(f"\nProcessing Fig 3 at P{targets['fig3']}: {repr(p3.text[:35])}")
    for r in list(p3.runs):
        if 'graphic' in r._element.xml:
            p3._p.remove(r._r)
            print("  Removed inline graphic from Fig 3 text paragraph.")
    insert_figure_with_caption(
        doc, p3, FIG3_PATH,
        "圖三：生成式 AI 市場研究之「價格敏感度混淆」實證實驗（真實消費者 vs. AI 模擬受訪者）",
        width_in=6.9
    )
    print("  Inserted Fig 3 with negative margin -400 dxa and caption.")

    # --- FIGURE 2 (Target: P76) ---
    p2 = doc.paragraphs[targets['fig2']]
    print(f"\nProcessing Fig 2 at P{targets['fig2']}")
    # Clean trailing empty paragraphs between p2 and "這套系統利用了"
    curr = p2._p.getnext()
    removed_p2_blanks = 0
    while curr is not None:
        t_val = curr.text
        if "這套系統利用了" in t_val:
            break
        nxt = curr.getnext()
        if len(t_val.strip()) == 0:
            curr.getparent().remove(curr)
            removed_p2_blanks += 1
        curr = nxt
    print(f"  Removed {removed_p2_blanks} blank paragraphs after Fig 2.")

    # Now clear runs in p2 and configure it as the Fig 2 image paragraph
    for r in list(p2.runs):
        p2._p.remove(r._r)

    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.first_line_indent = Pt(0)
    p2.paragraph_format.line_spacing = 1.0
    p2.paragraph_format.space_before = Pt(8)
    p2.paragraph_format.space_after = Pt(4)
    p2.paragraph_format.keep_with_next = True
    pPr2 = p2._p.get_or_add_pPr()
    ind2_xml = f'<w:ind {nsdecls("w")} w:left="-400" w:right="-400" w:firstLine="0"/>'
    pPr2.append(parse_xml(ind2_xml))
    r_img2 = p2.add_run()
    r_img2.add_picture(FIG2_PATH, width=Inches(6.9))

    # Caption for Fig 2
    p2_cap = doc.add_paragraph()
    p2._p.addnext(p2_cap._p)
    p2_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2_cap.paragraph_format.first_line_indent = Pt(0)
    p2_cap.paragraph_format.line_spacing = 1.15
    p2_cap.paragraph_format.space_before = Pt(3)
    p2_cap.paragraph_format.space_after = Pt(12)
    r2_cap = p2_cap.add_run("圖二：人機協同數據治理大腦架構圖（剛性數據辭典、靈活大模型、人類專家防線）")
    r2_cap.font.name = '標楷體'
    r2_cap.font.size = Pt(10.5)
    r2_cap.font.bold = True
    r2_cap.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
    r2_cap._r.get_or_add_rPr().append(parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="標楷體" w:ascii="標楷體" w:hAnsi="標楷體"/>'))
    print("  Updated Fig 2 with negative margin -400 dxa and caption.")

    # --- FIGURE 1 (Target: P55) ---
    p1 = doc.paragraphs[targets['fig1']]
    print(f"\nProcessing Fig 1 at P{targets['fig1']}: {repr(p1.text[:35])}")
    for r in list(p1.runs):
        if 'graphic' in r._element.xml:
            p1._p.remove(r._r)
            print("  Removed inline graphic from Fig 1 text paragraph.")

    # Clean trailing empty paragraphs between p1 and "這張圖是整理自"
    curr = p1._p.getnext()
    removed_p1_blanks = 0
    while curr is not None:
        t_val = curr.text
        if "這張圖是整理自" in t_val:
            break
        nxt = curr.getnext()
        if len(t_val.strip()) == 0:
            curr.getparent().remove(curr)
            removed_p1_blanks += 1
        curr = nxt
    print(f"  Removed {removed_p1_blanks} blank paragraphs after Fig 1.")

    insert_figure_with_caption(
        doc, p1, FIG1_PATH,
        "圖一：2024 全球數據長（CDO）實證調查：企業 AI 商業預期（80%）與核心投產（6%）之準備度大斷崖暨成熟度結構",
        width_in=6.9
    )
    print("  Inserted Fig 1 with negative margin -400 dxa and caption.")

    # Save to project docx ONLY
    doc.save(DOCX_PATH)
    print(f"\nSUCCESS: All 5 figures successfully optimized and saved to:\n  {DOCX_PATH}")


if __name__ == "__main__":
    execute()
