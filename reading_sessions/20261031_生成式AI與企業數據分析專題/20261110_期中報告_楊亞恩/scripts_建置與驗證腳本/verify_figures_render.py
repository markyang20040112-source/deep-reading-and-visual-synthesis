# -*- coding: utf-8 -*-
"""
verify_figures_render.py
Converts project 楊亞恩.docx to PDF via Word COM, and renders pages containing Figures 1 to 5 as PNGs.
"""

import os
import subprocess
import base64
import pymupdf

BASE_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩"
DOCX_PATH = os.path.join(BASE_DIR, "楊亞恩.docx")
PDF_PATH = os.path.join(BASE_DIR, "preview_step2.pdf")
PREVIEW_DIR = os.path.join(BASE_DIR, "preview_step2_pages")
os.makedirs(PREVIEW_DIR, exist_ok=True)

os.environ["VERIFY_DOCX"] = os.path.abspath(DOCX_PATH)
os.environ["VERIFY_PDF"] = os.path.abspath(PDF_PATH)

ps = """
$p = [System.Environment]::GetEnvironmentVariable('VERIFY_DOCX')
$out = [System.Environment]::GetEnvironmentVariable('VERIFY_PDF')
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($p)
    $doc.ExportAsFixedFormat($out, 17)
    $doc.Close([ref][Microsoft.Office.Interop.Word.WdSaveOptions]::wdDoNotSaveChanges)
} finally {
    $word.Quit()
}
"""

print("Exporting docx to PDF via Word COM...")
enc = base64.b64encode(ps.encode("utf-16le")).decode("ascii")
proc = subprocess.run(["powershell", "-NoProfile", "-EncodedCommand", enc], capture_output=True, text=True)

if not os.path.exists(PDF_PATH):
    print("Export failed! Output:", proc.stdout, "Error:", proc.stderr)
    exit(1)

print(f"Exported PDF successfully: {PDF_PATH} ({os.path.getsize(PDF_PATH)} bytes)")

pdf = pymupdf.open(PDF_PATH)
print(f"Total PDF pages: {len(pdf)}")

rendered_pages = []
for p_idx in range(len(pdf)):
    page = pdf[p_idx]
    text = page.get_text()
    page_num = p_idx + 1
    
    # Check if page has figure captions or figure content
    fig_matches = []
    for fig_k in ["圖一", "圖二", "圖三", "圖四", "圖五"]:
        if fig_k in text:
            fig_matches.append(fig_k)
            
    if fig_matches:
        pix = page.get_pixmap(dpi=150)
        out_img = os.path.join(PREVIEW_DIR, f"page_{page_num:02d}_{'_'.join(fig_matches)}.png")
        pix.save(out_img)
        print(f"Rendered Page {page_num} [{', '.join(fig_matches)}] -> {out_img}")
        rendered_pages.append((page_num, fig_matches, out_img))

print("\nAll figure pages rendered successfully:")
for p_num, figs, img_p in rendered_pages:
    print(f"  Page {p_num}: {figs} -> {img_p}")
