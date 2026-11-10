$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open("C:\Users\User\OneDrive\桌面\期中報告\楊亞恩.docx")
    foreach ($b in $doc.Bookmarks) {
        $p = $b.Range.Information(3) # wdActiveEndPageNumber
        Write-Host "$($b.Name):$p"
    }
    $doc.Close()
} finally {
    $word.Quit()
}
