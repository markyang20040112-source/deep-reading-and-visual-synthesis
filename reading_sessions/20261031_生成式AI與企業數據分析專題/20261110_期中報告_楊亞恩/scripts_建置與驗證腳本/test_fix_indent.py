# -*- coding: utf-8 -*-
import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import subprocess, base64, os, pymupdf

BASE = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩"
src_docx = os.path.join(BASE, "楊亞恩.docx")
test_docx = os.path.join(BASE, "test_fix_indent.docx")
test_pdf = os.path.join(BASE, "test_fix_indent.pdf")

doc = docx.Document(src_docx)
for idx in [56, 66, 76, 96, 111]:
    p = doc.paragraphs[idx]
    pPr = p._p.get_or_add_pPr()
    for child in list(pPr):
        if child.tag.endswith('ind'):
            pPr.remove(child)
    # Add with firstLineChars='0'
    pPr.append(parse_xml(f'<w:ind {nsdecls("w")} w:left="-400" w:right="-400" w:firstLine="0" w:firstLineChars="0"/>'))

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
    for pno in [4, 5, 6, 9, 11]:
        page = pdf[pno]
        for img in page.get_images():
            for r in page.get_image_rects(img[0]):
                print(f"Page {pno+1} img: x0={r.x0:.2f}, x1={r.x1:.2f}, w={r.width:.2f}, L_space={r.x0:.2f}, R_space={page.rect.width - r.x1:.2f}, diff={r.x0 - (page.rect.width - r.x1):.2f}")
else:
    print("Failed to export test_fix_indent.pdf")
