import os, subprocess, fitz

docx_path = os.path.abspath(r'reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\楊亞恩.docx')
pdf_path = os.path.abspath(r'reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\cover_check.pdf')

ps_script = f"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {{
    $doc = $word.Documents.Open('{docx_path}')
    $doc.ExportAsFixedFormat('{pdf_path}', 17)
    $doc.Close(0)
}} finally {{
    $word.Quit()
}}
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
print("PS Exit:", res.returncode)
if os.path.exists(pdf_path):
    print("PDF generated successfully! Size:", os.path.getsize(pdf_path))
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(dpi=150)
    out_img = os.path.abspath(r'C:\Users\User\.gemini\antigravity\brain\1acca209-68d9-4ef2-a88e-a0aa523820c5\cover_clean_preview.png')
    pix.save(out_img)
    print("Saved preview to:", out_img)
    
    # check blocks
    for b in page.get_text('blocks'):
        t = b[4].strip().replace('\n', ' ')
        if t:
            print(f"y0={b[1]:.1f}, y1={b[3]:.1f}: {t}")
    doc.close()
    os.remove(pdf_path)
else:
    print("Failed. Stderr:", res.stderr)
