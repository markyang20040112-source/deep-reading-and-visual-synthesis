import os, subprocess, fitz, base64

docx_path = os.path.abspath(r'reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\楊亞恩.docx')
pdf_path = os.path.abspath(r'reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\test_cover.pdf')

ps_script = """
$p = $env:DOCX_PATH
$out = $env:PDF_PATH
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $doc = $w.Documents.Open($p, $false, $true) # ReadOnly = True
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
    page = doc[0]
    rect = page.rect
    print(f"Page rect: width={rect.width:.1f}, height={rect.height:.1f}")
    blocks = page.get_text("blocks")
    for b in blocks:
        text = b[4].strip().replace('\n', ' / ')
        if text:
            print(f"Text block: y0={b[1]:.1f}, y1={b[3]:.1f} ({b[1]/rect.height*100:.1f}% - {b[3]/rect.height*100:.1f}%): {text}")
    
    drawings = page.get_drawings()
    print(f"Number of drawings: {len(drawings)}")
    for d in drawings:
        r = d['rect']
        print(f"Drawing: y0={r.y0:.1f}, y1={r.y1:.1f} ({r.y0/rect.height*100:.1f}%), width={r.width:.1f}")
    
    pix = page.get_pixmap(dpi=150)
    out_img = os.path.abspath(r'C:\Users\User\.gemini\antigravity\brain\1acca209-68d9-4ef2-a88e-a0aa523820c5\current_cover.png')
    pix.save(out_img)
    print("Saved cover image to:", out_img)
    doc.close()
    os.remove(pdf_path)
else:
    print("PDF export failed! PS Stderr:", res.stderr)
