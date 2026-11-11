# -*- coding: utf-8 -*-
import os
import subprocess
import fitz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX_PATH = os.path.abspath(os.path.join(BASE_DIR, "preview_links_and_sources.docx"))
PDF_PATH = os.path.abspath(os.path.join(BASE_DIR, "preview_links_and_sources.pdf"))

ps_content = f"""# Export preview_links_and_sources to PDF
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {{
    $doc = $word.Documents.Open('{DOCX_PATH}')
    $doc.ExportAsFixedFormat('{PDF_PATH}', 17)
    $doc.Close()
    Write-Host "SUCCESS: Exported PDF to {PDF_PATH}"
}} catch {{
    Write-Host "ERROR: " $_.Exception.Message
}} finally {{
    $word.Quit()
}}
"""

ps_path = os.path.join(BASE_DIR, "scripts_建置與驗證腳本", "export_links_preview.ps1")
with open(ps_path, "w", encoding="utf-8-sig") as f:
    f.write(ps_content)

print(f"Running PowerShell export on: {DOCX_PATH}")
subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_path], check=True)

if os.path.exists(PDF_PATH):
    print(f"PDF generated successfully: {PDF_PATH} ({os.path.getsize(PDF_PATH):,} bytes)")
    doc = fitz.open(PDF_PATH)
    print(f"Total pages: {len(doc)}")
    preview_dir = os.path.join(BASE_DIR, "preview_links_pages")
    os.makedirs(preview_dir, exist_ok=True)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        img_name = os.path.join(preview_dir, f"preview_links_page_{i+1}.png")
        pix.save(img_name)
        print(f"Rendered: {img_name}")
else:
    print("PDF generation failed.")
