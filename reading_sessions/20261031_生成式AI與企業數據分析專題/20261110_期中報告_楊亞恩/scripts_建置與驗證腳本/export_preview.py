# -*- coding: utf-8 -*-
import os
import subprocess
import base64
import fitz

TARGET_DOCX = os.path.abspath(r"C:\Users\User\OneDrive\桌面\期中報告\楊亞恩.docx")
TARGET_PDF = os.path.abspath(r"C:\Users\User\OneDrive\桌面\期中報告\preview.pdf")

os.environ["TARGET_DOCX"] = TARGET_DOCX
os.environ["TARGET_PDF"] = TARGET_PDF

ps = """
$p = [System.Environment]::GetEnvironmentVariable('TARGET_DOCX')
$out = [System.Environment]::GetEnvironmentVariable('TARGET_PDF')
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($p)
    $doc.ExportAsFixedFormat($out, 17)
    $doc.Close()
} finally {
    $word.Quit()
}
"""

enc = base64.b64encode(ps.encode("utf-16le")).decode("ascii")
proc = subprocess.run(["powershell", "-NoProfile", "-EncodedCommand", enc], capture_output=True)

if os.path.exists(TARGET_PDF):
    print("PDF size:", os.path.getsize(TARGET_PDF))
    doc = fitz.open(TARGET_PDF)
    print("PDF pages:", len(doc))
    for p_num in [1, 5, 6, 7]:
        pix = doc[p_num - 1].get_pixmap(dpi=150)
        out_name = f"preview_page_{p_num}.png"
        pix.save(out_name)
        print(f"Saved {out_name}")
else:
    print("PDF not found! PS Stderr:", proc.stderr)
