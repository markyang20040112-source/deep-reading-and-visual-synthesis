$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open('C:\Users\User\OneDrive\桌面\期中報告\楊亞恩.docx')
    for ($i = 1; $i -le 8; $i++) {
        $p = $doc.Paragraphs.Item($i)
        $t = $p.Range.Text.Trim()
        $lines = $p.Range.ComputeStatistics(1)
        Write-Host "P $i [$lines lines]: $t"
    }
    $doc.Close()
} finally {
    $word.Quit()
}
