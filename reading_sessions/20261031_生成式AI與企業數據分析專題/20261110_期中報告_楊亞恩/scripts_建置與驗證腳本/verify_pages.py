import os, subprocess, fitz, base64

docx_path = os.path.abspath(r'reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\楊亞恩.docx')
pdf_path = os.path.abspath(r'reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\test_verify.pdf')

ps_script = """
$p = $env:DOCX_PATH
$out = $env:PDF_PATH
$w = New-Object -ComObject Word.Application
$w.Visible = $false
try {
    $doc = $w.Documents.Open($p)
    $doc.ExportAsFixedFormat($out, 17)
    $doc.Close([ref]0)
} finally {
    $w.Quit()
}
"""

os.environ["DOCX_PATH"] = docx_path
os.environ["PDF_PATH"] = pdf_path

enc = base64.b64encode(ps_script.encode('utf-16le')).decode('ascii')
res = subprocess.run(['powershell', '-NoProfile', '-EncodedCommand', enc], capture_output=True, text=True)

if os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)
    print(f"Total pages: {len(doc)}")
    
    # Render TOC page (page 2)
    pix_toc = doc[1].get_pixmap(dpi=150)
    out_toc = os.path.abspath(r'C:\Users\User\.gemini\antigravity\brain\1acca209-68d9-4ef2-a88e-a0aa523820c5\toc_verified.png')
    pix_toc.save(out_toc)
    print("Saved TOC image to:", out_toc)
    
    # Check page 2 text
    print("\n--- Page 2 (TOC) Preview ---")
    for b in doc[1].get_text("blocks")[:4]:
        print(" ", b[4].strip().replace('\n', ' / '))
        
    print("\n--- Page 3 (Body Start) Preview ---")
    for b in doc[2].get_text("blocks")[:4]:
        print(" ", b[4].strip().replace('\n', ' / '))
        
    doc.close()
    os.remove(pdf_path)
else:
    print("Failed to export PDF:", res.stderr)
