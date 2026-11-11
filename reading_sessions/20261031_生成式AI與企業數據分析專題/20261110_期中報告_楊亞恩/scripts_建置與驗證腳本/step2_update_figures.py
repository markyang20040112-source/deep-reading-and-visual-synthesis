# -*- coding: utf-8 -*-
"""
step2_update_figures.py
Executes Step 2: Optimizes, validates, and inserts Figures 1 to 5 into 楊亞恩.docx.
Strictly does NOT modify desktop files, and strictly does NOT touch Tables (Step 3) or Links (Step 4).
"""

import os
import shutil
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

BASE_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩"
DOCX_PATH = os.path.join(BASE_DIR, "楊亞恩.docx")
ASSETS_DIR = os.path.join(BASE_DIR, "assets_原始素材與圖表")

# Target image paths
FIG1_PATH = os.path.join(ASSETS_DIR, "fig1_cdo_dual_panel.png")
FIG2_PATH = os.path.join(ASSETS_DIR, "fig2_brain_architecture.png")
FIG3_PATH = os.path.join(ASSETS_DIR, "fig3_price_sensitivity_confounding.png")
FIG4_PATH = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261031_顧客需求與統計模型\02_outputs\03_quantitative_empirical_charts.png"
FIG5_PATH = os.path.join(ASSETS_DIR, "04_顧客-企業-投資者關係心智圖_橫版.png")

def format_image_paragraph(p, img_path, width_in=6.9):
    """Configures paragraph to centered full-bleed image presentation with negative margins."""
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    
    pPr = p._p.get_or_add_pPr()
    # Add negative indent -400 dxa (-0.28 in) on both sides
    ind_xml = f'<w:ind {nsdecls("w")} w:left="-400" w:right="-400" w:firstLine="0"/>'
    pPr.append(parse_xml(ind_xml))
    
    r = p.add_run()
    r.add_picture(img_path, width=Inches(width_in))
    return p

def run_step2():
    print(f"Loading document: {DOCX_PATH}")
    doc = docx.Document(DOCX_PATH)
    
    # -------------------------------------------------------------------------
    # 1. Figure 1: CDO Dual-panel Chart
    # Located at paragraph with text starting with "這時人們就發現"
    # -------------------------------------------------------------------------
    p_fig1_text = None
    idx_fig1 = None
    for i, p in enumerate(doc.paragraphs):
        if "這時人們就發現" in p.text and any('graphic' in r._element.xml for r in p.runs):
            p_fig1_text = p
            idx_fig1 = i
            break
            
    if p_fig1_text is not None:
        print(f"Found Figure 1 at paragraph {idx_fig1}")
        # Remove graphic run from the text paragraph
        for r in list(p_fig1_text.runs):
            if 'graphic' in r._element.xml:
                p_fig1_text._p.remove(r._r)
                print("  Removed inline graphic from Fig 1 text paragraph.")
                
        # Remove the subsequent empty spacing paragraphs until "這張圖是整理自"
        curr_p = p_fig1_text._p.getnext()
        removed_count = 0
        while curr_p is not None:
            text_val = curr_p.text
            if "這張圖是整理自" in text_val:
                break
            next_p = curr_p.getnext()
            if len(text_val.strip()) == 0:
                curr_p.getparent().remove(curr_p)
                removed_count += 1
            curr_p = next_p
        print(f"  Removed {removed_count} redundant empty paragraphs after Fig 1.")
        
        # Insert dedicated image paragraph right after p_fig1_text
        new_p_fig1 = doc.add_paragraph()
        p_fig1_text._p.addnext(new_p_fig1._p)
        format_image_paragraph(new_p_fig1, FIG1_PATH, width_in=6.9)
        print("  Inserted Figure 1 in dedicated centered paragraph (width=6.9 in).")
    else:
        print("WARNING: Figure 1 paragraph not found!")

    # -------------------------------------------------------------------------
    # 2. Figure 2: Brain Architecture Diagram
    # Located after "最後是前額葉" paragraph
    # -------------------------------------------------------------------------
    p_fig2 = None
    idx_fig2 = None
    for i, p in enumerate(doc.paragraphs):
        if any('graphic' in r._element.xml for r in p.runs) and i > (idx_fig1 or 0):
            # Check if previous paragraph mentions 前額葉
            prev_text = doc.paragraphs[i-1].text if i > 0 else ""
            if "前額葉" in prev_text or len(p.text.strip()) == 0:
                p_fig2 = p
                idx_fig2 = i
                break

    if p_fig2 is not None:
        print(f"Found Figure 2 at paragraph {idx_fig2}")
        # Clear existing runs in p_fig2
        for r in list(p_fig2.runs):
            p_fig2._p.remove(r._r)
            
        # Remove empty trailing paragraphs until "這套系統利用了"
        curr_p = p_fig2._p.getnext()
        removed_count = 0
        while curr_p is not None:
            text_val = curr_p.text
            if "這套系統利用了" in text_val:
                break
            next_p = curr_p.getnext()
            if len(text_val.strip()) == 0:
                curr_p.getparent().remove(curr_p)
                removed_count += 1
            curr_p = next_p
        print(f"  Removed {removed_count} redundant empty paragraphs after Fig 2.")
        
        format_image_paragraph(p_fig2, FIG2_PATH, width_in=6.9)
        print("  Updated Figure 2 in dedicated centered paragraph (width=6.9 in).")
    else:
        print("WARNING: Figure 2 paragraph not found!")

    # -------------------------------------------------------------------------
    # 3. Figure 3: Pricing Demand Curve Confounding
    # Located at paragraph with "在這裡我想分享文章中提到的兩個"
    # -------------------------------------------------------------------------
    p_fig3_text = None
    idx_fig3 = None
    for i, p in enumerate(doc.paragraphs):
        if "在這裡我想分享文章中提到的兩個" in p.text and any('graphic' in r._element.xml for r in p.runs):
            p_fig3_text = p
            idx_fig3 = i
            break

    if p_fig3_text is not None:
        print(f"Found Figure 3 at paragraph {idx_fig3}")
        for r in list(p_fig3_text.runs):
            if 'graphic' in r._element.xml:
                p_fig3_text._p.remove(r._r)
                print("  Removed inline graphic from Fig 3 text paragraph.")
                
        # Insert dedicated image paragraph right after p_fig3_text
        new_p_fig3 = doc.add_paragraph()
        p_fig3_text._p.addnext(new_p_fig3._p)
        format_image_paragraph(new_p_fig3, FIG3_PATH, width_in=6.9)
        print("  Inserted Figure 3 in dedicated centered paragraph (width=6.9 in).")
    else:
        print("WARNING: Figure 3 paragraph not found!")

    # -------------------------------------------------------------------------
    # 4. Figure 4: Customer Value Empirical Chart
    # Located at paragraph with "這篇文章主要在說，研究顯示高層認為重要"
    # -------------------------------------------------------------------------
    p_fig4_text = None
    idx_fig4 = None
    for i, p in enumerate(doc.paragraphs):
        if "高層認為重要的價值驅動因素與顧客真實重視的事物" in p.text and any('graphic' in r._element.xml for r in p.runs):
            p_fig4_text = p
            idx_fig4 = i
            break

    if p_fig4_text is not None:
        print(f"Found Figure 4 at paragraph {idx_fig4}")
        for r in list(p_fig4_text.runs):
            if 'graphic' in r._element.xml:
                p_fig4_text._p.remove(r._r)
                print("  Removed inline graphic from Fig 4 text paragraph.")
                
        # Insert dedicated image paragraph right after p_fig4_text
        new_p_fig4 = doc.add_paragraph()
        p_fig4_text._p.addnext(new_p_fig4._p)
        format_image_paragraph(new_p_fig4, FIG4_PATH, width_in=6.9)
        print("  Inserted Figure 4 in dedicated centered paragraph (width=6.9 in).")
    else:
        print("WARNING: Figure 4 paragraph not found!")

    # -------------------------------------------------------------------------
    # 5. Figure 5: Ecosystem Mindmap
    # Located at paragraph with "在大部分的情況下企業與客戶才是主要在製造經濟循環的關係"
    # -------------------------------------------------------------------------
    p_fig5_text = None
    idx_fig5 = None
    for i, p in enumerate(doc.paragraphs):
        if "在大部分的情況下企業與客戶才是主要在製造經濟循環的關係" in p.text and any('graphic' in r._element.xml for r in p.runs):
            p_fig5_text = p
            idx_fig5 = i
            break

    if p_fig5_text is not None:
        print(f"Found Figure 5 at paragraph {idx_fig5}")
        for r in list(p_fig5_text.runs):
            if 'graphic' in r._element.xml:
                p_fig5_text._p.remove(r._r)
                print("  Removed inline graphic from Fig 5 text paragraph.")
                
        # Insert dedicated image paragraph right after p_fig5_text
        new_p_fig5 = doc.add_paragraph()
        p_fig5_text._p.addnext(new_p_fig5._p)
        format_image_paragraph(new_p_fig5, FIG5_PATH, width_in=6.9)
        print("  Inserted Figure 5 in dedicated centered paragraph (width=6.9 in).")
    else:
        print("WARNING: Figure 5 paragraph not found!")

    # Save to project docx ONLY
    doc.save(DOCX_PATH)
    print(f"SUCCESS: Step 2 Figures integrated and saved to: {DOCX_PATH}")

if __name__ == "__main__":
    run_step2()
