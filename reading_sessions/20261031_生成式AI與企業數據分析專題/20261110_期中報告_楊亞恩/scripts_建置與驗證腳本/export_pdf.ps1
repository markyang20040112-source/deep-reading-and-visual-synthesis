# Export 楊亞恩.docx to 楊亞恩.pdf via Word COM
$baseDir = "C:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩"
$docxPath = Join-Path $baseDir "楊亞恩.docx"
$pdfPath = Join-Path $baseDir "楊亞恩.pdf"

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    Write-Host "Opening $docxPath..."
    $doc = $word.Documents.Open($docxPath, $false, $true) # ReadOnly
    Write-Host "Exporting to $pdfPath (OptimizeForOnScreen)..."
    # ExportAsFixedFormat(OutputFileName, ExportFormat=17, OpenAfterExport=False, OptimizeFor=1 (OnScreen), Range=0 (All))
    $doc.ExportAsFixedFormat($pdfPath, 17, $false, 1, 0)
    $doc.Close(0)
    Write-Host "SUCCESS: Exported PDF to $pdfPath ($(Get-Item $pdfPath).Length bytes)"
} catch {
    Write-Host "ERROR: $($_.Exception.Message)"
} finally {
    $word.Quit()
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
