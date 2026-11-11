import os, subprocess, base64

ps_script = """
$p = "C:\\Users\\User\\.gemini\\antigravity\\scratch\\deep-reading-and-visual-synthesis\\reading_sessions\\20261031_生成式AI與企業數據分析專題\\20261110_期中報告_楊亞恩\\楊亞恩.docx"

try {
    $word = [System.Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application')
    foreach ($d in $word.Documents) {
        if ($d.FullName -eq $p) {
            Write-Host "Closing open doc in Word: " $d.FullName
            $d.Close([ref]0) # 0 = wdDoNotSaveChanges
        }
    }
} catch {
    Write-Host "Could not get active Word object: " $_.Exception.Message
}
"""

enc = base64.b64encode(ps_script.encode('utf-16le')).decode('ascii')
res = subprocess.run(['powershell', '-NoProfile', '-EncodedCommand', enc], capture_output=True, text=True)
print("Return code:", res.returncode)
print("Output:", res.stdout)
if res.stderr:
    print("Stderr:", res.stderr)
