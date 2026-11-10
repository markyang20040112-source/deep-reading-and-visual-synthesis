# -*- coding: utf-8 -*-
import os
import sys
import base64
import subprocess

TARGET_DOCX = os.path.abspath(r"C:\Users\User\OneDrive\桌面\期中報告\楊亞恩.docx")
os.environ["TARGET_DOCX"] = TARGET_DOCX

ps_script = """
$p = [System.Environment]::GetEnvironmentVariable('TARGET_DOCX')
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($p)
    Write-Host "Total paragraphs: $($doc.Paragraphs.Count)"
    Write-Host "Total pages: $($doc.ComputeStatistics(2))"
    for ($i = 1; $i -le 10; $i++) {
        $par = $doc.Paragraphs.Item($i)
        $txt = $par.Range.Text.Trim()
        $lines = $par.Range.ComputeStatistics(1)
        Write-Host "P $i [lines=$lines]: $txt"
    }
    $doc.Close()
} finally {
    $word.Quit()
}
"""

enc = base64.b64encode(ps_script.encode("utf-16le")).decode("ascii")
out = subprocess.check_output(["powershell", "-NoProfile", "-EncodedCommand", enc], text=True)
print(out)
