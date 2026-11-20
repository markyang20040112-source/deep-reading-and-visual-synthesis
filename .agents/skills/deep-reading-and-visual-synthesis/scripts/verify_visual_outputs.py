"""
verify_visual_outputs.py
Automated Visual Verification & Hygiene Cleanup Engine for Phase 2 Step 4.
Renders .pdf pages and .pptx slides into temporary high-DPI .png images for visual inspection,
verifies Medium articles (`--verify-medium`), PPTX physical box capacity / bounds / speaker notes (`--verify-pptx`),
and Format E dashboard bundles (`--verify-dashboard`),
and cleans up all temporary preview images / intermediate artifacts so `02_outputs/` remains 100% clean.

Provides:
- render_pdf_to_pngs(pdf_path, out_dir=None, dpi=180) -> List[str]
- render_pptx_to_pngs(pptx_path, out_dir=None, width_px=1920, height_px=1080) -> List[str]
- cleanup_preview_artifacts(target_dir) -> List[str]
- verify_medium_article_words(md_path_or_text, max_body_words=1600) -> dict
- verify_pptx_structure(pptx_path) -> dict
- verify_dashboard_bundle(dashboard_dir) -> dict
- CLI:
  python verify_visual_outputs.py --input <file.pdf|file.pptx> [--out-dir <dir>]
  python verify_visual_outputs.py --verify-medium <02_medium_article.md>
  python verify_visual_outputs.py --verify-pptx <deck.pptx>
  python verify_visual_outputs.py --verify-dashboard <dashboard_dir>
  python verify_visual_outputs.py --cleanup <02_outputs_dir>
"""

import argparse
import os
import shutil
import subprocess
from contextlib import suppress
from pathlib import Path

PREVIEW_PREFIX = "_preview_"


def render_pdf_to_pngs(
    pdf_path: str,
    out_dir: str | None = None,
    dpi: int = 180,
) -> list[str]:
    """
    Render every page of a PDF file into temporary PNG images (`_preview_<stem>_p01.png`, ...)
    using PyMuPDF (`fitz`) or Windows native WinRT `Windows.Data.Pdf.PdfDocument` fallback.
    """
    src = Path(pdf_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"PDF file not found: {src}")
    dest_dir = Path(out_dir).resolve() if out_dir else src.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    generated: list[str] = []
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(src))
        zoom = float(dpi) / 72.0
        mat = fitz.Matrix(zoom, zoom)
        for idx, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=mat, alpha=False)
            out_png = dest_dir / f"{PREVIEW_PREFIX}{src.stem}_p{idx:02d}.png"
            pix.save(str(out_png))
            generated.append(str(out_png))
        doc.close()
        return generated
    except ImportError:
        pass

    # Fallback on Windows: Built-in WinRT Windows.Data.Pdf.PdfDocument via PowerShell
    if os.name == "nt":
        scale = max(1.0, float(dpi) / 72.0)
        env = os.environ.copy()
        env["VERIFY_SRC_PATH"] = str(src)
        env["VERIFY_DEST_DIR"] = str(dest_dir)
        env["VERIFY_FILE_PREFIX"] = f"{PREVIEW_PREFIX}{src.stem}_p"
        ps_script = f"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime]
$null = [Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType=WindowsRuntime]
$null = [Windows.Data.Pdf.PdfPageRenderOptions, Windows.Data.Pdf, ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime]

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
}})[0]

function Await($WinRtTask, $ResultType) {{
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    return $netTask.Result
}}

function AwaitAction($WinRtAction) {{
    $asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{
        $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction'
    }})[0]
    $netTask = $asTask.Invoke($null, @($WinRtAction))
    $netTask.Wait(-1) | Out-Null
}}

$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($env:VERIFY_SRC_PATH)) ([Windows.Storage.StorageFile])
$pdf = Await ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)) ([Windows.Data.Pdf.PdfDocument])
$count = $pdf.PageCount
for ($i = 0; $i -lt $count; $i++) {{
    $page = $pdf.GetPage($i)
    $opts = New-Object Windows.Data.Pdf.PdfPageRenderOptions
    $opts.DestinationWidth = [uint32]([Math]::Round($page.Size.Width * {scale:.3f}))
    $opts.DestinationHeight = [uint32]([Math]::Round($page.Size.Height * {scale:.3f}))
    $pageNum = ($i + 1).ToString('00')
    $outPath = Join-Path $env:VERIFY_DEST_DIR ($env:VERIFY_FILE_PREFIX + $pageNum + '.png')
    $stream = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
    AwaitAction ($page.RenderToStreamAsync($stream, $opts))
    $reader = New-Object Windows.Storage.Streams.DataReader($stream.GetInputStreamAt(0))
    $len = [uint32]$stream.Size
    $null = Await ($reader.LoadAsync($len)) ([uint32])
    $bytes = New-Object byte[] $len
    $reader.ReadBytes($bytes)
    [System.IO.File]::WriteAllBytes($outPath, $bytes)
    $reader.Dispose()
    $stream.Dispose()
    $page.Dispose()
    Write-Output $outPath
}}
"""
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=90,
            check=False,
        )
        for line in (res.stdout or "").splitlines():
            p = line.strip()
            if p and os.path.exists(p):
                generated.append(p)
        if generated:
            return generated

    raise RuntimeError(
        "Unable to rasterize PDF pages to PNG (neither PyMuPDF `fitz` nor Windows WinRT PdfDocument succeeded)."
    )


def render_pptx_to_pngs(
    pptx_path: str,
    out_dir: str | None = None,
    width_px: int = 1920,
    height_px: int = 1080,
    dpi: int | None = None,
) -> list[str]:
    """
    Render every slide of a .pptx file into temporary PNG images (`_preview_<stem>_s01.png`, ...)
    via Windows PowerPoint COM (`win32com.client` or PowerShell COM) or LibreOffice (`soffice --headless --convert-to pdf`).
    """
    src = Path(pptx_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"PPTX file not found: {src}")
    dest_dir = Path(out_dir).resolve() if out_dir else src.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    if dpi is not None and width_px == 1920 and height_px == 1080:
        width_px = round(13.333 * float(dpi))
        height_px = round(7.5 * float(dpi))

    generated: list[str] = []

    # Strategy 1A: Python win32com.client if installed
    if os.name == "nt":
        com_err: tuple[type[BaseException], ...] = ()
        with suppress(ImportError):
            import pywintypes  # type: ignore

            com_err = (pywintypes.com_error,)
        with suppress(ImportError, OSError, AttributeError, RuntimeError, *com_err):
            import win32com.client  # type: ignore

            ppt_app = win32com.client.Dispatch("PowerPoint.Application")
            had_open = ppt_app.Presentations.Count > 0
            presentation = ppt_app.Presentations.Open(str(src), WithWindow=False, ReadOnly=True)
            try:
                for idx, slide in enumerate(presentation.Slides, start=1):
                    out_png = dest_dir / f"{PREVIEW_PREFIX}{src.stem}_s{idx:02d}.png"
                    slide.Export(str(out_png), "PNG", int(width_px), int(height_px))
                    generated.append(str(out_png))
            finally:
                presentation.Close()
                if not had_open and ppt_app.Presentations.Count == 0:
                    ppt_app.Quit()
            if generated:
                return generated

        # Strategy 1B: Built-in Windows PowerShell PowerPoint COM automation (no pywin32 needed)
        env = os.environ.copy()
        env["VERIFY_SRC_PATH"] = str(src)
        env["VERIFY_DEST_DIR"] = str(dest_dir)
        env["VERIFY_FILE_PREFIX"] = f"{PREVIEW_PREFIX}{src.stem}_s"
        ps_ppt = f"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ppt = New-Object -ComObject PowerPoint.Application
$hadOpen = ($ppt.Presentations.Count -gt 0)
$pres = $ppt.Presentations.Open($env:VERIFY_SRC_PATH, $true, $false, $false)
try {{
    $idx = 1
    foreach ($slide in $pres.Slides) {{
        $sNum = $idx.ToString('00')
        $outPath = Join-Path $env:VERIFY_DEST_DIR ($env:VERIFY_FILE_PREFIX + $sNum + '.png')
        $slide.Export($outPath, 'PNG', {int(width_px)}, {int(height_px)})
        Write-Output $outPath
        $idx++
    }}
}} finally {{
    $pres.Close()
    if (-not $hadOpen -and $ppt.Presentations.Count -eq 0) {{
        $ppt.Quit()
    }}
}}
"""
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_ppt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=90,
            check=False,
        )
        for line in (res.stdout or "").splitlines():
            p = line.strip()
            if p and os.path.exists(p):
                generated.append(p)
        if generated:
            return generated

    # Strategy 2: LibreOffice headless -> temp PDF -> render_pdf_to_pngs
    soffice_bin = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice_bin:
        tmp_pdf = dest_dir / f"{PREVIEW_PREFIX}{src.stem}_temp.pdf"
        subprocess.run(
            [soffice_bin, "--headless", "--convert-to", "pdf", "--outdir", str(dest_dir), str(src)],
            check=True,
            capture_output=True,
        )
        default_pdf = dest_dir / f"{src.stem}.pdf"
        if default_pdf.exists() and default_pdf != tmp_pdf:
            default_pdf.replace(tmp_pdf)
        if tmp_pdf.exists():
            try:
                raw_pngs = render_pdf_to_pngs(str(tmp_pdf), out_dir=str(dest_dir), dpi=dpi or 180)
                renamed_pngs: list[str] = []
                for idx, p_str in enumerate(raw_pngs, start=1):
                    p_path = Path(p_str)
                    target_png = dest_dir / f"{PREVIEW_PREFIX}{src.stem}_s{idx:02d}.png"
                    if p_path.exists():
                        p_path.replace(target_png)
                        renamed_pngs.append(str(target_png))
                return renamed_pngs
            finally:
                tmp_pdf.unlink(missing_ok=True)

    raise RuntimeError(
        "Unable to export PPTX slides to PNG: neither Windows PowerPoint COM nor LibreOffice (`soffice`) was available."
    )


def cleanup_preview_artifacts(target_dir: str) -> list[str]:
    """
    Remove all temporary verification and compilation artifacts in `target_dir`:
    - `_preview_*.png`, `_preview_*.pdf`, `slide_*.png`, `page_*.png`, `test_*.png`
    - `_tmp_*.html`, `temp_*.html`
    - Duplicate `.jpg` / `.jpeg` files when a lossless `.png` exists
    Returns list of deleted file paths.
    """
    d = Path(target_dir).resolve()
    if not d.exists() or not d.is_dir():
        return []

    patterns = [
        f"{PREVIEW_PREFIX}*.png",
        f"{PREVIEW_PREFIX}*.pdf",
        "slide_*.png",
        "page_*.png",
        "test_*.png",
        "_tmp_*.html",
        "temp_*.html",
        "*.tmp.html",
    ]
    removed: list[str] = []
    for pat in patterns:
        for fpath in d.glob(pat):
            if fpath.is_file():
                try:
                    fpath.unlink()
                    removed.append(str(fpath))
                except OSError:
                    pass

    # Also remove duplicate .jpg/.jpeg when matching .png is present
    for jpg_file in list(d.glob("*.jpg")) + list(d.glob("*.jpeg")):
        matching_png = jpg_file.with_suffix(".png")
        if matching_png.exists():
            try:
                jpg_file.unlink()
                removed.append(str(jpg_file))
            except OSError:
                pass

    return removed


def _count_cjk_and_words(markdown_segment: str) -> int:
    """
    Count words in a Traditional Chinese + English Markdown segment (matching Google Docs / MS Word convention):
    - Replaces `![alt](url)` with `alt` (preserving image captions while stripping file paths).
    - Replaces `[text](url)` with `text` (preserving link text while stripping raw URLs).
    - Counts each CJK character (and CJK punctuation) + each contiguous ASCII alphanumeric/number token.
    """
    import re
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", markdown_segment)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    # Strip markdown structural markers (#, >, *, `, ~, -, |)
    text = re.sub(r"(?m)^\s*[#>*-]+\s*", "", text)
    text = re.sub(r"[*_`~]", "", text)
    cjk_chars = re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef]", text)
    ascii_words = re.findall(r"[A-Za-z0-9]+(?:[.\-%/][A-Za-z0-9]+)*", text)
    return len(cjk_chars) + len(ascii_words)


def verify_medium_article_words(
    md_path_or_text: str,
    max_body_words: int = 1600,
) -> dict:
    """
    Verify a Format B Genre 5 Medium Data Storytelling Column (`02_medium_article.md`):
    1. Splits body text from the trailing `---` official reference source block.
    2. Computes `body_words` (excluding the `---` source block) and `total_words` (including it).
    3. Verifies `body_words <= max_body_words` (<= 1,600 words).
    4. Verifies 100% Medium-native syntax (zero `<div`, `.card-grid-2`, `<table`, `<figure`, or Markdown tables).
    5. Verifies chart count is 1 or 2 (`![...](...)`).
    6. Verifies the source declaration does NOT falsely cite `資料說明書` as the official data source.
    Returns a dict with `passed`, `body_words`, `footer_words`, `total_words`, `chart_count`, `issues`, and `stats_line`.
    """
    import re
    p = Path(md_path_or_text)
    if p.exists() and p.is_file():
        raw_text = p.read_text(encoding="utf-8")
    else:
        raw_text = str(md_path_or_text)

    # Remove existing word-count summary line so re-runs are idempotent
    cleaned_text = re.sub(r"(?m)^>?\s*📊\s*字數統計：.*$", "", raw_text).strip()

    # Split at the horizontal rule `---` separating body from official source block
    hr_parts = re.split(r"(?m)^\s*---\s*$", cleaned_text)
    if len(hr_parts) >= 2:
        body_md = "\n---\n".join(hr_parts[:-1]).strip()
        footer_md = hr_parts[-1].strip()
        has_hr_footer = True
    else:
        body_md = cleaned_text
        footer_md = ""
        has_hr_footer = False

    body_words = _count_cjk_and_words(body_md)
    footer_words = _count_cjk_and_words(footer_md)
    total_words = body_words + footer_words

    issues: list[str] = []
    if not has_hr_footer:
        issues.append("缺少文末 `---` 水平分隔線與「參考資料來源」附註區塊。")
    if body_words > max_body_words:
        issues.append(f"正文字數 ({body_words} 字) 超過 Medium 專欄上限 ({max_body_words} 字)！")
    if re.search(r"<(div|table|figure)\b|\.card-grid-2", cleaned_text, re.IGNORECASE):
        issues.append("偵測到 Medium 不支援之自訂 HTML 標籤 (`<div>` / `<table>` / `<figure>` / `.card-grid-2`)。")
    if re.search(r"(?m)^\s*\|.*\|.*\n\s*\|\s*[-:]+", body_md):
        issues.append("偵測到 Medium 不支援之 Markdown 表格 (`|---|`)。")

    charts = re.findall(r"!\[[^\]]*\]\([^)]+\)", body_md)
    chart_count = len(charts)
    if chart_count < 1 or chart_count > 2:
        issues.append(f"圖表數量 ({chart_count} 張) 不符合『至少 1 張、至多 2 張』規定。")

    if footer_md and re.search(r"(資料來源|數據來源|取自)\s*[：:]\s*[^\n]*資料說明書", footer_md):
        issues.append("嚴禁將使用者自己生成的『資料說明書』寫成官方資料來源！必須填寫原始公開資料集之發布機關與名稱。")

    status_str = f"符合 <= {max_body_words:,} 字規範" if body_words <= max_body_words else f"超過 <= {max_body_words:,} 字規範"
    stats_line = (
        f"📊 字數統計：正文共 {body_words} 字（不含文末參考資料來源，{status_str}；"
        f"若含文末來源共 {total_words} 字）。"
    )
    return {
        "passed": len(issues) == 0,
        "body_words": body_words,
        "footer_words": footer_words,
        "total_words": total_words,
        "chart_count": chart_count,
        "issues": issues,
        "stats_line": stats_line,
    }


def verify_pptx_structure(
    pptx_path: str,
) -> dict:
    """
    Verify a Format C Assertion-Evidence `.pptx` presentation using pure physical & structural invariants
    (zero arbitrary per-slide word count, paragraph count, or box count caps):
    1. Box Physical Capacity Check: Estimates wrapped line height per paragraph using actual font pt & box width;
       flags only when wrapped text physically overflows the box height (`req_h_in > box_h + 0.30"`).
    2. Canvas Boundary Check: Flags shapes extending outside the 13.333" x 7.5" widescreen canvas.
    3. Speaker Notes Presence Check: Ensures every slide contains non-empty `Speaker_Notes`.
    4. Bookend Minimum Slide Count Check: Ensures at least 2 slides exist (cover + closing).
    Returns dict with `passed`, `slide_count`, `missing_notes_slides`, `overflow_boxes`, `out_of_bounds_shapes`, `issues`, `stats_line`.
    """
    import math
    import unicodedata

    from pptx import Presentation  # type: ignore

    src = Path(pptx_path).resolve()
    if not src.exists() or not src.is_file():
        raise FileNotFoundError(f"PPTX file not found: {src}")

    prs = Presentation(str(src))
    slide_count = len(prs.slides)
    issues: list[str] = []
    missing_notes_slides: list[int] = []
    overflow_boxes: list[dict] = []
    out_of_bounds_shapes: list[dict] = []

    if slide_count < 2:
        issues.append(f"簡報僅有 {slide_count} 頁，不符合首尾定錨頁（至少封面＋結尾 2 頁）規範。")

    emu_per_inch = 914400.0
    for idx, slide in enumerate(prs.slides, start=1):
        notes_txt = ""
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None:
            notes_txt = (slide.notes_slide.notes_text_frame.text or "").strip()
        if not notes_txt:
            missing_notes_slides.append(idx)

        for shape in slide.shapes:
            left_in = shape.left / emu_per_inch
            top_in = shape.top / emu_per_inch
            w_in = shape.width / emu_per_inch
            h_in = shape.height / emu_per_inch
            if left_in < -0.10 or top_in < -0.10 or (left_in + w_in) > 13.45 or (top_in + h_in) > 7.60:
                out_of_bounds_shapes.append(
                    {
                        "slide": idx,
                        "name": shape.name,
                        "bounds": (round(left_in, 2), round(top_in, 2), round(w_in, 2), round(h_in, 2)),
                    }
                )

            if shape.has_text_frame and (shape.text_frame.text or "").strip():
                tf = shape.text_frame
                usable_w = max(0.30, w_in - 0.12)
                req_h_in = 0.0
                for para in tf.paragraphs:
                    raw_p = para.text or ""
                    if not raw_p.strip():
                        continue
                    r_pts = [r.font.size.pt for r in para.runs if r.font and r.font.size]
                    p_pt = max(r_pts) if r_pts else (para.font.size.pt if para.font and para.font.size else 12.0)
                    chars_per_line = max(1.0, (usable_w * 72.0) / p_pt)
                    for sub_line in raw_p.replace("\x0b", "\n").splitlines():
                        if not sub_line.strip():
                            req_h_in += (p_pt * 0.65) / 72.0
                            continue
                        eff_len = sum(1.0 if unicodedata.east_asian_width(c) in ("W", "F") else 0.55 for c in sub_line)
                        lines = max(1, math.ceil(eff_len / chars_per_line))
                        req_h_in += lines * ((p_pt * 1.28) / 72.0)

                if req_h_in > h_in + 0.30:
                    overflow_boxes.append(
                        {
                            "slide": idx,
                            "box_w": round(w_in, 2),
                            "box_h": round(h_in, 2),
                            "req_h": round(req_h_in, 2),
                            "snippet": tf.text.strip().replace("\n", " ")[:24],
                        }
                    )

    if missing_notes_slides:
        pages_str = ", ".join(str(p) for p in missing_notes_slides)
        issues.append(f"第 {pages_str} 頁缺少演講者備忘稿 (Speaker Notes)。")
    if out_of_bounds_shapes:
        detail = ", ".join(f"第{item['slide']}頁({item['name']})" for item in out_of_bounds_shapes)
        issues.append(f"偵測到元件超出 13.333\"×7.5\" 投影片畫布邊界：{detail}。")
    if overflow_boxes:
        detail = "; ".join(
            f"第{b['slide']}頁「{b['snippet']}...」(框高{b['box_h']}\" < 預估需求{b['req_h']}\")"
            for b in overflow_boxes
        )
        issues.append(
            f"偵測到文字物理穿框／溢位風險（請拉高卡片框、微調字級或拆頁，勿刪減核心論點）：{detail}。"
        )

    stats_line = (
        f"🎤 PPTX 物理與講稿體檢：共 {slide_count} 頁，"
        f"缺講稿 {len(missing_notes_slides)} 頁，物理穿框風險 {len(overflow_boxes)} 處，畫布越界 {len(out_of_bounds_shapes)} 處。"
    )
    return {
        "passed": len(issues) == 0,
        "slide_count": slide_count,
        "missing_notes_slides": missing_notes_slides,
        "overflow_boxes": overflow_boxes,
        "out_of_bounds_shapes": out_of_bounds_shapes,
        "issues": issues,
        "stats_line": stats_line,
    }


def verify_dashboard_bundle(dashboard_dir: str) -> dict:
    """
    Verify a Format E zero-backend interactive web dashboard directory:
    1. Required files exist: `index.html`, `css/style.css`, `js/gephi_palette.js`, `js/dashboard.js`,
       `.nojekyll`, `.gitignore`, `README.md`.
    2. `index.html` does NOT load `cdn.tailwindcss.com` and uses strict `./` relative local paths
       (no root-absolute `/css/...` or `/js/...` paths).
    3. `data/` contains BOTH `*_data.js` and `*_data.json` (offline `file://` dual-loading).
    4. `css/style.css` includes `:root` CSS variables and `tabular-nums`.
    5. No nested `.git` directory remains inside `dashboard_dir`.
    Returns dict with `passed`, `dashboard_dir`, `issues`, `stats_line`.
    """
    import re

    d = Path(dashboard_dir).resolve()
    if not d.exists() or not d.is_dir():
        raise FileNotFoundError(f"Dashboard directory not found: {d}")

    issues: list[str] = []
    required_files = [
        "index.html",
        "css/style.css",
        "js/gephi_palette.js",
        "js/dashboard.js",
        ".nojekyll",
        ".gitignore",
        "README.md",
    ]
    missing = [rel for rel in required_files if not (d / rel).is_file()]
    if missing:
        issues.append(f"缺少必要網站專案檔案：{', '.join(missing)}")

    index_path = d / "index.html"
    if index_path.is_file():
        html_text = index_path.read_text(encoding="utf-8", errors="replace")
        if "cdn.tailwindcss.com" in html_text:
            issues.append("偵測到禁用之執行期 `cdn.tailwindcss.com`（須將樣式完整寫入 `./css/style.css`）。")
        abs_paths = re.findall(r"""(?:src|href)\s*=\s*["'](/(?!/)[^"']*)["']""", html_text, re.IGNORECASE)
        if abs_paths:
            issues.append(f"index.html 偵測到以 `/` 開頭的根目錄絕對路徑（必須改用 `./` 相對路徑）：{', '.join(abs_paths[:5])}")

    data_dir = d / "data"
    if not data_dir.is_dir():
        issues.append("缺少 `data/` 目錄。")
    else:
        js_files = list(data_dir.glob("*_data.js"))
        json_files = list(data_dir.glob("*_data.json"))
        if not js_files:
            issues.append("`data/` 缺少離線防 CORS 用 `*_data.js` 檔（須與 `.json` 雙檔並存）。")
        if not json_files:
            issues.append("`data/` 缺少標準 `*_data.json` 檔。")

    css_path = d / "css/style.css"
    if css_path.is_file():
        css_text = css_path.read_text(encoding="utf-8", errors="replace")
        if ":root" not in css_text:
            issues.append("`css/style.css` 缺少 `:root` 色彩變數定義區塊。")
        if "tabular-nums" not in css_text:
            issues.append("`css/style.css` 缺少 `font-variant-numeric: tabular-nums` 等寬數字對齊設定。")

    if (d / ".git").exists():
        issues.append("偵測到殘留之嵌套 `.git` 目錄！推送獨立網站倉庫後請務必清除內層 `.git`，避免外層倉庫產生 gitlink 衝突。")

    stats_line = (
        f"🌐 Format E 網站結構檢查（{d.name}）："
        + ("全部規範通過！" if not issues else f"發現 {len(issues)} 項待修問題。")
    )
    return {
        "passed": len(issues) == 0,
        "dashboard_dir": str(d),
        "issues": issues,
        "stats_line": stats_line,
    }


if __name__ == "__main__":
    import sys

    with suppress(AttributeError, OSError, ValueError):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Render PDF/PPTX to temporary PNG previews, verify outputs, and clean up `02_outputs/`.")
    parser.add_argument("target", nargs="?", default=None, help="Optional positional path to .pdf/.pptx/.md file or directory to clean up.")
    parser.add_argument("--input", "-i", type=str, default=None, help="Path to .pdf or .pptx file to render into preview PNGs.")
    parser.add_argument("--verify-medium", "-m", type=str, default=None, help="Path to 02_medium_article.md to verify separated word count and Medium syntax.")
    parser.add_argument("--verify-pptx", "-p", type=str, default=None, help="Path to .pptx file to verify physical box capacity, canvas bounds, and Speaker Notes.")
    parser.add_argument("--verify-dashboard", "-d", type=str, default=None, help="Path to Format E dashboard directory to verify bundle hygiene.")
    parser.add_argument("--out-dir", "-o", type=str, default=None, help="Output directory for preview PNGs.")
    parser.add_argument("--dpi", type=int, default=180, help="DPI for PDF rasterization (default: 180).")
    parser.add_argument("--cleanup", "-c", nargs="?", const="__USE_TARGET__", default=None, help="Clean up temporary preview artifacts in target directory.")
    args = parser.parse_args()

    input_file = args.input
    cleanup_dir = None

    if args.verify_medium:
        report = verify_medium_article_words(args.verify_medium)
        print(report["stats_line"])
        if not report["passed"]:
            for iss in report["issues"]:
                print(f"[ISSUE] {iss}")
            sys.exit(1)
        sys.exit(0)

    if args.verify_pptx:
        report = verify_pptx_structure(args.verify_pptx)
        print(report["stats_line"])
        if not report["passed"]:
            for iss in report["issues"]:
                print(f"[ISSUE] {iss}")
            sys.exit(1)
        sys.exit(0)

    if args.verify_dashboard:
        report = verify_dashboard_bundle(args.verify_dashboard)
        print(report["stats_line"])
        if not report["passed"]:
            for iss in report["issues"]:
                print(f"[ISSUE] {iss}")
            sys.exit(1)
        sys.exit(0)

    if args.cleanup is not None:
        cleanup_dir = args.target if args.cleanup == "__USE_TARGET__" else args.cleanup
        if not cleanup_dir:
            cleanup_dir = "."
    elif args.target:
        t_path = Path(args.target).resolve()
        if t_path.is_dir():
            cleanup_dir = str(t_path)
        elif t_path.suffix.lower() == ".md":
            report = verify_medium_article_words(str(t_path))
            print(report["stats_line"])
            if not report["passed"]:
                for iss in report["issues"]:
                    print(f"[ISSUE] {iss}")
                sys.exit(1)
        else:
            input_file = str(t_path)

    if input_file:
        in_path = Path(input_file).resolve()
        ext = in_path.suffix.lower()
        if ext == ".pdf":
            files = render_pdf_to_pngs(str(in_path), out_dir=args.out_dir, dpi=args.dpi)
        elif ext in (".pptx", ".ppt"):
            files = render_pptx_to_pngs(str(in_path), out_dir=args.out_dir)
        else:
            raise ValueError(f"Unsupported file extension '{ext}'. Expected .pdf or .pptx.")
        for f in files:
            print(f"[PREVIEW] {f}")

    if cleanup_dir:
        deleted = cleanup_preview_artifacts(cleanup_dir)
        print(f"[CLEANUP] Removed {len(deleted)} temporary artifact(s) from {cleanup_dir}")


