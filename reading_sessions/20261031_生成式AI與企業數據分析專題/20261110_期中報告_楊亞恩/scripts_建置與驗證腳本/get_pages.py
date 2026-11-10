import os
import subprocess
import base64

doc_path = r"C:\Users\User\OneDrive\桌面\期中報告\楊亞恩.docx"
os.environ["TARGET_DOCX"] = doc_path

ps_script = """
$p = [System.Environment]::GetEnvironmentVariable('TARGET_DOCX')
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($p)
    Write-Host "Total Pages: $($doc.ComputeStatistics(2))"
    foreach ($b in $doc.Bookmarks) {
        $pg = $b.Range.Information(3)
        Write-Host "$($b.Name):$pg"
    }
    $doc.Close()
} finally {
    $word.Quit()
}
"""

enc = base64.b64encode(ps_script.encode("utf-16le")).decode("ascii")
out = subprocess.check_output(["powershell", "-NoProfile", "-EncodedCommand", enc], text=True)
print(out)
