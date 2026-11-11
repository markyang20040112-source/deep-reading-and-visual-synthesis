# -*- coding: utf-8 -*-
import os
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX_PATH = os.path.join(BASE_DIR, "楊亞恩.docx")
PDF_PATH = os.path.join(BASE_DIR, "楊亞恩.pdf")

ps = f"""
$docx = '{DOCX_PATH}'
$pdf = '{PDF_PATH}'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {{
    $doc = $word.Documents.Open($docx, $false, $true)
    $pages = $doc.ComputeStatistics(2)
    Write-Host "Total Pages: $pages"
    # Export range from page 1 to $pages
    $doc.ExportAsFixedFormat($pdf, 17, $false, 1, 3, 1, $pages)
    $doc.Close(0)
    Write-Host "SUCCESS: Exported PDF to $pdf ($(Get-Item $pdf).Length bytes)"
}} catch {{
    Write-Host "ERROR: $($_.Exception.Message)"
}} finally {{
    $word.Quit()
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}}
"""

print(f"Exporting {DOCX_PATH} -> {PDF_PATH}...")
start = time.time()
res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print("Stderr:", res.stderr)
print(f"Elapsed time: {time.time() - start:.2f} seconds")

if os.path.exists(PDF_PATH):
    print(f"PDF verified exists: {PDF_PATH} ({os.path.getsize(PDF_PATH):,} bytes)")
else:
    print("FAILED: PDF not found!")
