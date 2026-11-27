"""
verify_visual_outputs.py
Automated Visual Verification, Option C 3-Tier Internal QA & Hygiene Cleanup Engine for Phase 2 Step 4/5.
Renders .pdf pages and .pptx slides (full deck or single-slide `slide_indices` partial re-render)
into temporary high-DPI .png images, builds `4×4` deck rhythm contact sheets and `1920×1080` HD `2×2` QA grids,
verifies Medium articles (`--verify-medium`), PPTX two-track structure/typography/collision/fidelity (`--verify-pptx`),
Format E dashboard bundles (`--verify-dashboard`), and session color registries (`--verify-colors`),
and cleans up all temporary preview / QA grid artifacts so `02_outputs/` remains 100% clean.

Provides:
- render_pdf_to_pngs(pdf_path, out_dir=None, dpi=180, page_indices=None) -> List[str]
- render_pptx_to_pngs(pptx_path, out_dir=None, width_px=1920, height_px=1080, dpi=None, slide_indices=None) -> List[str]
- build_pptx_contact_sheet(png_paths, out_path, cols=4, rows=4, ...) -> str
- build_pptx_qa_grids(png_paths, out_dir, ...) -> List[str]
- cleanup_preview_artifacts(target_dir) -> List[str]
- verify_medium_article_words(md_path_or_text, max_body_words=1600) -> dict
- verify_pptx_structure(pptx_path, min_font_pt=None, profile="reading", spec_lock_path=None, ...) -> dict
- verify_dashboard_bundle(dashboard_dir) -> dict
- verify_color_registry(session_dir) -> dict
- check_matplotlib_text_collisions(fig, shrink_pt=1.5, print_report=True) -> dict
- CLI:
  python verify_visual_outputs.py --input <file.pdf|file.pptx> [--out-dir <dir>] [--slides 1,4] [--qa-grids]
  python verify_visual_outputs.py --verify-medium <02_medium_article.md>
  python verify_visual_outputs.py --verify-pptx <deck.pptx> [--min-font-pt 16.0] [--spec-lock <02c_slide_spec_lock.json>]
  python verify_visual_outputs.py --verify-dashboard <dashboard_dir>
  python verify_visual_outputs.py --cleanup <02_outputs_dir>
"""


import argparse
import os
import re
import shutil
import subprocess
import sys
from contextlib import suppress
from pathlib import Path

from pptx_engine.qa import (  # noqa: F401
    PREVIEW_PREFIX,
    QA_CONTACT_PREFIX,
    QA_GRID_PREFIX,
    render_pptx_to_pngs,
    build_pptx_contact_sheet,
    build_pptx_qa_grids,
    verify_pptx_structure,
    _DRAFT_PLACEHOLDER_RE,
    _SLIDE_NUM_RE,
    _load_slide_engine_module,
    _normalize_one_based_indices,
    _extract_slide_badge_label,
    _load_qa_badge_font,
    _paste_slide_tile,
    _shape_has_visible_border,
    _iter_slide_shapes,
    _estimate_union_area_sq_in,
    _rgb_luminance,
    _slide_has_dark_background,
    _shape_has_omml,
    _shape_is_rounded_rect,
    _build_paragraph_measure_input,
    _inspect_embedded_image_quality,
    _parse_spec_lock_metadata,
)

def render_pdf_to_pngs(
    pdf_path: str,
    out_dir: str | None = None,
    dpi: int = 180,
    page_indices: int | list[int] | tuple[int, ...] | set[int] | None = None,
) -> list[str]:
    """
    Render pages of a PDF file into temporary PNG images (`_preview_<stem>_p01.png`, ...)
    using PyMuPDF (`fitz`) or Windows native WinRT `Windows.Data.Pdf.PdfDocument` fallback.
    Supports optional 1-based `page_indices` subset rendering.
    """
    src = Path(pdf_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"PDF file not found: {src}")
    dest_dir = Path(out_dir).resolve() if out_dir else src.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    target_pages = _normalize_one_based_indices(page_indices, param_name="page_indices")
    if target_pages is not None and len(target_pages) == 0:
        return []

    generated: list[str] = []
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(src))
        try:
            page_count = len(doc)
            if target_pages is not None:
                _normalize_one_based_indices(target_pages, max_count=page_count, param_name="page_indices")
                pages_to_render = target_pages
            else:
                pages_to_render = list(range(1, page_count + 1))

            zoom = float(dpi) / 72.0
            mat = fitz.Matrix(zoom, zoom)
            for idx in pages_to_render:
                page = doc[idx - 1]
                pix = page.get_pixmap(matrix=mat, alpha=False)
                out_png = dest_dir / f"{PREVIEW_PREFIX}{src.stem}_p{idx:02d}.png"
                pix.save(str(out_png))
                generated.append(str(out_png))
        finally:
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
        env["VERIFY_PAGE_INDICES"] = ",".join(str(i) for i in target_pages) if target_pages is not None else ""
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
$count = [int]$pdf.PageCount
if ($env:VERIFY_PAGE_INDICES) {{
    $targetPages = $env:VERIFY_PAGE_INDICES.Split(',') | ForEach-Object {{ [int]$_.Trim() }}
}} else {{
    $targetPages = 1..$count
}}
foreach ($pNo in $targetPages) {{
    if ($pNo -lt 1 -or $pNo -gt $count) {{
        throw "Page index $pNo out of range (1..$count)"
    }}
    $page = $pdf.GetPage([uint32]($pNo - 1))
    $opts = New-Object Windows.Data.Pdf.PdfPageRenderOptions
    $opts.DestinationWidth = [uint32]([Math]::Round($page.Size.Width * {scale:.3f}))
    $opts.DestinationHeight = [uint32]([Math]::Round($page.Size.Height * {scale:.3f}))
    $pageNum = $pNo.ToString('00')
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
            timeout=120,
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


def cleanup_preview_artifacts(target_dir: str) -> list[str]:
    """
    Remove all temporary verification and compilation artifacts in `target_dir`:
    - `_preview_*.png`, `_preview_*.pdf`, `slide_*.png`, `page_*.png`, `test_*.png`
    - `_qa_contact_*.png`, `_qa_grid_*.png` (Option C contact sheets & 2x2 QA grids)
    - `_tmp_*.html`, `temp_*.html`, `*.tmp.html`
    - Duplicate `.jpg` / `.jpeg` files when a lossless `.png` exists
    Returns list of deleted file paths.
    """
    d = Path(target_dir).resolve()
    if not d.exists() or not d.is_dir():
        return []

    patterns = [
        f"{PREVIEW_PREFIX}*.png",
        f"{PREVIEW_PREFIX}*.pdf",
        f"{QA_CONTACT_PREFIX}*.png",
        f"{QA_GRID_PREFIX}*.png",
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


def check_matplotlib_text_collisions(
    fig,
    shrink_pt: float = 1.5,
    print_report: bool = True,
) -> dict:
    """
    Zero-visual-token pre-check for Matplotlib figures (Format A / D / E static PNGs) before `view_file`:
    - Checks ONLY visible text-on-text collisions (each text bbox shrunk by `shrink_pt` pt on all 4 sides)
      and text-vs-canvas out-of-bounds.
    - Ignores gridlines/patches, hidden axes (`ax.axis("off")`), and `Annotation` arrow tips
      by querying `Text.get_window_extent()` directly.
    Returns dict with `passed`, `text_count`, `overlaps`, `out_of_bounds`, `issues`, `stats_line`.
    """
    from matplotlib.text import Text  # type: ignore

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    fig_w, fig_h = fig.canvas.get_width_height()
    shrink_px = float(shrink_pt) * (float(fig.dpi) / 72.0)

    seen: set[int] = set()
    artists: list[tuple[str, Text]] = []

    def _add(t) -> None:
        if t is None or id(t) in seen:
            return
        seen.add(id(t))
        txt = (t.get_text() or "").strip()
        if not txt or not t.get_visible() or t.get_alpha() == 0:
            return
        artists.append((txt.replace("\n", " ")[:24], t))

    for t in fig.texts:
        _add(t)
    for ax in fig.axes:
        if not ax.get_visible():
            continue
        for t in ax.texts:
            _add(t)
        for t in (ax.title, getattr(ax, "_left_title", None), getattr(ax, "_right_title", None)):
            _add(t)
        leg = ax.get_legend()
        if leg is not None and leg.get_visible():
            for t in leg.get_texts():
                _add(t)
            _add(leg.get_title())
        if ax.axison:
            if ax.xaxis.get_visible():
                _add(ax.xaxis.label)
                for t in ax.get_xticklabels():
                    _add(t)
            if ax.yaxis.get_visible():
                _add(ax.yaxis.label)
                for t in ax.get_yticklabels():
                    _add(t)

    boxes = []
    for label, t in artists:
        bb = Text.get_window_extent(t, renderer=renderer)
        if bb.width <= 0 or bb.height <= 0:
            continue
        boxes.append((label, bb))

    overlaps: list[dict] = []
    out_of_bounds: list[dict] = []
    for i, (label, bb) in enumerate(boxes):
        if bb.x0 < -shrink_px or bb.y0 < -shrink_px or bb.x1 > fig_w + shrink_px or bb.y1 > fig_h + shrink_px:
            out_of_bounds.append(
                {
                    "text": label,
                    "bbox_px": (round(float(bb.x0)), round(float(bb.y0)), round(float(bb.x1)), round(float(bb.y1))),
                    "canvas_px": (int(fig_w), int(fig_h)),
                }
            )
        sx0, sy0, sx1, sy1 = bb.x0 + shrink_px, bb.y0 + shrink_px, bb.x1 - shrink_px, bb.y1 - shrink_px
        if sx0 >= sx1 or sy0 >= sy1:
            continue
        for j in range(i + 1, len(boxes)):
            label2, bb2 = boxes[j]
            tx0, ty0, tx1, ty1 = bb2.x0 + shrink_px, bb2.y0 + shrink_px, bb2.x1 - shrink_px, bb2.y1 - shrink_px
            if tx0 >= tx1 or ty0 >= ty1:
                continue
            ix = min(sx1, tx1) - max(sx0, tx0)
            iy = min(sy1, ty1) - max(sy0, ty0)
            if ix > 0 and iy > 0:
                overlaps.append(
                    {
                        "text_a": label,
                        "text_b": label2,
                        "overlap_px": (round(float(ix), 1), round(float(iy), 1)),
                    }
                )

    issues: list[str] = []
    if overlaps:
        detail = "; ".join(f"「{o['text_a']}」×「{o['text_b']}」({o['overlap_px'][0]}×{o['overlap_px'][1]}px)" for o in overlaps)
        issues.append(f"偵測到文字重疊：{detail}")
    if out_of_bounds:
        detail = ", ".join(f"「{o['text']}」" for o in out_of_bounds)
        issues.append(f"偵測到文字超出畫布邊界：{detail}")

    stats_line = (
        f"🔍 Matplotlib 文字快篩：檢查 {len(boxes)} 個文字元件，"
        f"重疊 {len(overlaps)} 處，出界 {len(out_of_bounds)} 處。"
    )
    if print_report and issues:
        print(stats_line)
        for iss in issues:
            print(f"[TEXT_WARN] {iss}")

    return {
        "passed": len(issues) == 0,
        "text_count": len(boxes),
        "overlaps": overlaps,
        "out_of_bounds": out_of_bounds,
        "issues": issues,
        "stats_line": stats_line,
    }


def verify_color_registry(session_dir: str) -> dict:
    """
    Verify session-level category color consistency across `<session_dir>/02_color_registry.json`
    and any embedded Format E `js/gephi_palette.js` files under `session_dir`.
    Returns dict with `passed`, `session_dir`, `issues`, `warnings`, `stats_line`.
    """
    import json
    import re
    from color_registry import REGISTRY_FILENAME, CategoryColorRegistry

    s_dir = Path(session_dir).resolve()
    issues: list[str] = []
    warnings: list[str] = []

    if not s_dir.is_dir():
        issues.append(f"Session directory does not exist: {s_dir}")
        return {
            "passed": False,
            "session_dir": str(s_dir),
            "issues": issues,
            "warnings": warnings,
            "stats_line": f"🎨 色彩登記表檢查（{s_dir.name}）：工作階段目錄不存在。",
        }

    reg_path = s_dir / REGISTRY_FILENAME
    if not reg_path.is_file():
        issues.append(f"缺少工作階段色彩登記表：{reg_path}")
        return {
            "passed": False,
            "session_dir": str(s_dir),
            "issues": issues,
            "warnings": warnings,
            "stats_line": f"🎨 色彩登記表檢查（{s_dir.name}）：缺少 {REGISTRY_FILENAME}。",
        }

    try:
        reg = CategoryColorRegistry(reg_path)
    except Exception as exc:
        issues.append(f"無法載入 {REGISTRY_FILENAME}：{exc}")
        return {
            "passed": False,
            "session_dir": str(s_dir),
            "issues": issues,
            "warnings": warnings,
            "stats_line": f"🎨 色彩登記表檢查（{s_dir.name}）：登記表格式錯誤。",
        }

    for msg in reg.audit():
        if msg.startswith("WARN:"):
            warnings.append(msg)
        else:
            issues.append(msg)

    expected_js_colors = {k: str(v).upper() for k, v in reg.to_js_entity_colors().items()}
    js_files = sorted(p for p in s_dir.rglob("gephi_palette.js") if p.parent.name == "js")
    for js_path in js_files:
        text = js_path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"entityColors\s*:\s*(\{.*?\})", text, re.DOTALL)
        if not match:
            issues.append(f"{js_path.relative_to(s_dir)} 缺少 `entityColors` 區塊。")
            continue
        try:
            parsed = json.loads(match.group(1))
        except Exception as exc:
            issues.append(f"{js_path.relative_to(s_dir)} 的 `entityColors` JSON 解析失敗：{exc}")
            continue
        actual_js_colors = {str(k): str(v).upper() for k, v in parsed.items()}
        if actual_js_colors != expected_js_colors:
            issues.append(
                f"{js_path.relative_to(s_dir)} 的 `entityColors` ({actual_js_colors}) "
                f"與登記表 ({expected_js_colors}) 不一致。"
            )

    passed = len(issues) == 0
    stats_line = (
        f"🎨 色彩登記表檢查（{s_dir.name}）："
        + ("全部一致通過！" if passed else f"發現 {len(issues)} 項不一致。")
        + (f"（另有 {len(warnings)} 項警示）" if warnings else "")
    )
    return {
        "passed": passed,
        "session_dir": str(s_dir),
        "issues": issues,
        "warnings": warnings,
        "stats_line": stats_line,
    }


if __name__ == "__main__":
    with suppress(AttributeError, OSError, ValueError):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Render PDF/PPTX to temporary PNG previews, build Option C QA grids, verify outputs, and clean up `02_outputs/`.")
    parser.add_argument("target", nargs="?", default=None, help="Optional positional path to .pdf/.pptx/.md file or directory to clean up.")
    parser.add_argument("--input", "-i", type=str, default=None, help="Path to .pdf or .pptx file to render into preview PNGs.")
    parser.add_argument("--slides", type=str, default=None, help="Optional comma-separated 1-based slide indices for partial PPTX re-render (e.g., 1,4).")
    parser.add_argument("--qa-grids", action="store_true", help="When rendering a .pptx, also build 4x4 contact sheet and 1920x1080 HD 2x2 QA grids.")
    parser.add_argument("--verify-medium", "-m", type=str, default=None, help="Path to 02_medium_article.md to verify separated word count and Medium syntax.")
    parser.add_argument("--verify-pptx", "-p", type=str, default=None, help="Path to .pptx file to verify two-track physical/typography/collision/fidelity rules & Speaker Notes.")
    parser.add_argument("--pptx-profile", type=str, default="reading", choices=["reading", "live"], help="PPTX verification profile (default: reading >=12.0pt; live >=16.0pt).")
    parser.add_argument("--min-font-pt", type=float, default=None, help="Optional override for minimum content font size floor in pt.")
    parser.add_argument("--spec-lock", type=str, default=None, help="Optional path to 02c_slide_spec_lock.json for copy/numeric fidelity & family checks.")
    parser.add_argument("--verify-dashboard", "-d", type=str, default=None, help="Path to Format E dashboard directory to verify bundle hygiene.")
    parser.add_argument("--verify-colors", type=str, default=None, help="Path to session directory to verify 02_color_registry.json and JS entityColors consistency.")
    parser.add_argument("--out-dir", "-o", type=str, default=None, help="Output directory for preview PNGs and QA grids.")
    parser.add_argument("--dpi", type=int, default=180, help="DPI for PDF rasterization (default: 180).")
    parser.add_argument("--cleanup", "-c", nargs="?", const="__USE_TARGET__", default=None, help="Clean up temporary preview & QA grid artifacts in target directory.")
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
        report = verify_pptx_structure(
            args.verify_pptx,
            min_font_pt=args.min_font_pt,
            profile=args.pptx_profile,
            spec_lock_path=args.spec_lock,
        )
        print(report["stats_line"])
        if report.get("high_risk_slides"):
            print(f"[HIGH_RISK] Slides {report['high_risk_slides']}")
        for w_msg in report.get("warnings", []):
            print(f"[WARN] {w_msg}")
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

    if args.verify_colors:
        import json as _json

        report = verify_color_registry(args.verify_colors)
        print(_json.dumps(report, ensure_ascii=False, indent=2))
        if not report["passed"]:
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
        parsed_slides = (
            [int(tok.strip()) for tok in args.slides.split(",") if tok.strip()]
            if args.slides
            else None
        )
        if ext == ".pdf":
            files = render_pdf_to_pngs(str(in_path), out_dir=args.out_dir, dpi=args.dpi, page_indices=parsed_slides)
        elif ext in (".pptx", ".ppt"):
            files = render_pptx_to_pngs(str(in_path), out_dir=args.out_dir, slide_indices=parsed_slides)
            if args.qa_grids and files:
                out_root = Path(args.out_dir).resolve() if args.out_dir else in_path.parent
                cs_path = build_pptx_contact_sheet(files, str(out_root / f"{QA_CONTACT_PREFIX}{in_path.stem}.png"))
                print(f"[CONTACT] {cs_path}")
                grid_paths = build_pptx_qa_grids(files, str(out_root), prefix=in_path.stem)
                for gp in grid_paths:
                    print(f"[QA_GRID] {gp}")
        else:
            raise ValueError(f"Unsupported file extension '{ext}'. Expected .pdf or .pptx.")
        for f in files:
            print(f"[PREVIEW] {f}")

    if cleanup_dir:
        deleted = cleanup_preview_artifacts(cleanup_dir)
        print(f"[CLEANUP] Removed {len(deleted)} temporary artifact(s) from {cleanup_dir}")
