# -*- coding: utf-8 -*-
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import subprocess, base64, os, pymupdf

BASE = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩"
test_docx = os.path.join(BASE, "test_indent.docx")
test_pdf = os.path.join(BASE, "test_indent.pdf")
asset_img = os.path.join(BASE, "assets_原始素材與圖表", "fig3_price_sensitivity_confounding.png")

doc = docx.Document()
# Normal style check
sec = doc.sections[0]
sec.page_width = Inches(8.267) # A4
sec.left_margin = Inches(1.0)
sec.right_margin = Inches(1.0)
content_w_in = 8.267 - 2.0 # 6.267 inches

# Test 1: exact margin width 6.26 in, center, ind 0
p1 = doc.add_paragraph("Test 1: width 6.26 in, ind 0")
p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
p1_pPr = p1._p.get_or_add_pPr()
p1_pPr.append(parse_xml(f'<w:ind {nsdecls("w")} w:left="0" w:right="0" w:firstLine="0" w:firstLineChars="0"/>'))
r1 = p1.add_run()
r1.add_picture(asset_img, width=Inches(6.26))

# Test 2: width 6.6 in, negative ind left=-240, right=-240
doc.add_page_break()
p2 = doc.add_paragraph("Test 2: width 6.6 in, ind left=-240 right=-240")
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
p2_pPr = p2._p.get_or_add_pPr()
p2_pPr.append(parse_xml(f'<w:ind {nsdecls("w")} w:left="-240" w:right="-240" w:firstLine="0" w:firstLineChars="0"/>'))
r2 = p2.add_run()
r2.add_picture(asset_img, width=Inches(6.6))

# Test 3: width 6.9 in, negative ind left=-450, right=-450
doc.add_page_break()
p3 = doc.add_paragraph("Test 3: width 6.9 in, ind left=-450 right=-450")
p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
p3_pPr = p3._p.get_or_add_pPr()
p3_pPr.append(parse_xml(f'<w:ind {nsdecls("w")} w:left="-450" w:right="-450" w:firstLine="0" w:firstLineChars="0"/>'))
r3 = p3.add_run()
r3.add_picture(asset_img, width=Inches(6.9))

doc.save(test_docx)

ps = f"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {{
    $doc = $word.Documents.Open('{test_docx}')
    $doc.ExportAsFixedFormat('{test_pdf}', 17)
    $doc.Close([ref][Microsoft.Office.Interop.Word.WdSaveOptions]::wdDoNotSaveChanges)
}} finally {{
    $word.Quit()
}}
"""
enc = base64.b64encode(ps.encode('utf-16le')).decode('ascii')
subprocess.run(['powershell', '-NoProfile', '-EncodedCommand', enc], capture_output=True)

if os.path.exists(test_pdf):
    pdf = pymupdf.open(test_pdf)
    print("PDF pages:", len(pdf))
    for pno in range(len(pdf)):
        page = pdf[pno]
        for img in page.get_images():
            for r in page.get_image_rects(img[0]):
                print(f"Page {pno+1} img: x0={r.x0:.2f}, x1={r.x1:.2f}, w={r.width:.2f}, L_space={r.x0:.2f}, R_space={page.rect.width - r.x1:.2f}, diff={r.x0 - (page.rect.width - r.x1):.2f}")
else:
    print("test_pdf not found!")
