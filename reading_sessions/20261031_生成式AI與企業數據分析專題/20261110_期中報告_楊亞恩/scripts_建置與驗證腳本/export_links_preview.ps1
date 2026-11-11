# Export preview_links_and_sources to PDF
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open('C:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\preview_links_and_sources.docx')
    $doc.ExportAsFixedFormat('C:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\preview_links_and_sources.pdf', 17)
    $doc.Close()
    Write-Host "SUCCESS: Exported PDF to C:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\preview_links_and_sources.pdf"
} catch {
    Write-Host "ERROR: " $_.Exception.Message
} finally {
    $word.Quit()
}
