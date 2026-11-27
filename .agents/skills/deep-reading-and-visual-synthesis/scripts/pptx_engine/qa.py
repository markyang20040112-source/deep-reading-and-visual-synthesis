"""
pptx_engine/qa.py
Format C Option C 3-tier internal QA, PPTX-to-PNG preview rendering, contact sheets, and 2x2 QA grids.
Note: `verify_visual_outputs` is the public entry point.
"""

import io
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import suppress
from pathlib import Path

PREVIEW_PREFIX = "_preview_"


QA_CONTACT_PREFIX = "_qa_contact_"


QA_GRID_PREFIX = "_qa_grid_"

_DRAFT_PLACEHOLDER_RE = re.compile(r"(?<![A-Za-z])(?:TBD|TODO|FIXME)(?![A-Za-z])", re.IGNORECASE)


_SLIDE_NUM_RE = re.compile(r"(?:_s|slide[_-]?)(\d+)(?:\.[^.]+)?$", re.IGNORECASE)


def _load_slide_engine_module():
    """Import sibling `pptx_slide_engine` safely for Pillow measurement & spec-lock helpers."""
    scripts_dir = str(Path(__file__).resolve().parents[1])
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import pptx_slide_engine  # type: ignore

        return pptx_slide_engine
    except ImportError:
        return None


def _normalize_one_based_indices(
    indices: int | list[int] | tuple[int, ...] | set[int] | None,
    max_count: int | None = None,
    param_name: str = "slide_indices",
) -> list[int] | None:
    """Validate and normalize 1-based slide/page indices into a sorted unique list (or None)."""
    if indices is None:
        return None
    if isinstance(indices, bool):
        raise ValueError(f"{param_name} cannot be a boolean.")
    if isinstance(indices, int):
        raw_items = [indices]
    else:
        raw_items = list(indices)

    cleaned: list[int] = []
    seen: set[int] = set()
    for item in raw_items:
        if isinstance(item, bool) or not isinstance(item, int):
            raise ValueError(f"{param_name} must contain 1-based integers; got {item!r}.")
        if item < 1:
            raise ValueError(f"{param_name} entries must be >= 1; got {item}.")
        if max_count is not None and item > max_count:
            raise ValueError(f"{param_name} entry {item} exceeds total count ({max_count}).")
        if item not in seen:
            seen.add(item)
            cleaned.append(item)
    cleaned.sort()
    return cleaned


def render_pptx_to_pngs(
    pptx_path: str,
    out_dir: str | None = None,
    width_px: int = 1920,
    height_px: int = 1080,
    dpi: int | None = None,
    slide_indices: int | list[int] | tuple[int, ...] | set[int] | None = None,
) -> list[str]:
    """
    Render slides of a `.pptx` file into temporary PNG images (`_preview_<stem>_s01.png`, ...).
    Supports F4 3-strategy full-deck or targeted partial single-slide re-rendering via `slide_indices` (1-based):
    - Strategy A: Windows PowerShell PowerPoint COM (`$pres.Slides.Item($idx).Export(...)`, zero pywin32 dependency).
    - Strategy B: Python `win32com.client` PowerPoint COM (if `pywin32` is installed).
    - Strategy C: LibreOffice headless (`soffice --headless --convert-to pdf`) + PyMuPDF `fitz` / WinRT targeted pages.
    """
    src = Path(pptx_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"PPTX file not found: {src}")
    dest_dir = Path(out_dir).resolve() if out_dir else src.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    if dpi is not None:
        if float(dpi) <= 0:
            raise ValueError(f"dpi must be positive; got {dpi!r}.")
        if width_px == 1920 and height_px == 1080:
            width_px = round(13.333 * float(dpi))
            height_px = round(7.5 * float(dpi))
    if int(width_px) <= 0 or int(height_px) <= 0:
        raise ValueError(f"width_px and height_px must be positive; got ({width_px!r}, {height_px!r}).")

    # Pre-validate slide_indices against actual deck slide count when python-pptx is available
    deck_slide_count: int | None = None
    deck_w_in: float = 13.333
    with suppress(ImportError, OSError, ValueError):
        from pptx import Presentation  # type: ignore

        _prs_meta = Presentation(str(src))
        deck_slide_count = len(_prs_meta.slides)
        if _prs_meta.slide_width:
            deck_w_in = max(1.0, float(_prs_meta.slide_width) / 914400.0)

    target_indices = _normalize_one_based_indices(
        slide_indices,
        max_count=deck_slide_count,
        param_name="slide_indices",
    )
    if target_indices is not None and len(target_indices) == 0:
        return []
    if deck_slide_count == 0 and target_indices is None:
        return []

    expected_n: int | None = len(target_indices) if target_indices is not None else deck_slide_count
    generated: list[str] = []

    if os.name == "nt":
        # Strategy A: Built-in Windows PowerShell PowerPoint COM automation (no pywin32 needed)
        env = os.environ.copy()
        env["VERIFY_SRC_PATH"] = str(src)
        env["VERIFY_DEST_DIR"] = str(dest_dir)
        env["VERIFY_FILE_PREFIX"] = f"{PREVIEW_PREFIX}{src.stem}_s"
        env["VERIFY_SLIDE_INDICES"] = ",".join(str(i) for i in target_indices) if target_indices is not None else ""
        ps_ppt = f"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ppt = New-Object -ComObject PowerPoint.Application
$hadOpen = ($ppt.Presentations.Count -gt 0)
$pres = $null
try {{
    $pres = $ppt.Presentations.Open($env:VERIFY_SRC_PATH, $true, $false, $false)
    $total = [int]$pres.Slides.Count
    if ($total -le 0) {{
        return
    }}
    if ($env:VERIFY_SLIDE_INDICES) {{
        $indices = $env:VERIFY_SLIDE_INDICES.Split(',') | ForEach-Object {{ [int]$_.Trim() }}
    }} else {{
        $indices = 1..$total
    }}
    foreach ($idx in $indices) {{
        if ($idx -lt 1 -or $idx -gt $total) {{
            throw "Slide index $idx out of range (1..$total)"
        }}
        $slide = $pres.Slides.Item($idx)
        $sNum = $idx.ToString('00')
        $outPath = Join-Path $env:VERIFY_DEST_DIR ($env:VERIFY_FILE_PREFIX + $sNum + '.png')
        $slide.Export($outPath, 'PNG', {int(width_px)}, {int(height_px)})
        Write-Output $outPath
    }}
}} finally {{
    if ($null -ne $pres) {{
        $pres.Close()
    }}
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
            timeout=120,
            check=False,
        )
        if res.returncode == 0:
            for line in (res.stdout or "").splitlines():
                p = line.strip()
                if p and os.path.exists(p):
                    generated.append(p)
            if generated and (expected_n is None or len(generated) == expected_n):
                return generated
        generated = []

        # Strategy B: Python win32com.client fallback if installed
        com_err: tuple[type[BaseException], ...] = ()
        with suppress(ImportError):
            import pywintypes  # type: ignore

            com_err = (pywintypes.com_error,)
        with suppress(ImportError, OSError, AttributeError, RuntimeError, *com_err):
            import win32com.client  # type: ignore

            ppt_app = win32com.client.Dispatch("PowerPoint.Application")
            had_open = ppt_app.Presentations.Count > 0
            presentation = None
            try:
                presentation = ppt_app.Presentations.Open(str(src), WithWindow=False, ReadOnly=True)
                total = int(presentation.Slides.Count)
                if total <= 0:
                    return []
                indices_to_run = target_indices if target_indices is not None else list(range(1, total + 1))
                for idx in indices_to_run:
                    if idx < 1 or idx > total:
                        raise ValueError(f"slide_indices entry {idx} exceeds slide count ({total}).")
                    slide = presentation.Slides.Item(idx)
                    out_png = dest_dir / f"{PREVIEW_PREFIX}{src.stem}_s{idx:02d}.png"
                    slide.Export(str(out_png), "PNG", int(width_px), int(height_px))
                    generated.append(str(out_png))
            finally:
                if presentation is not None:
                    presentation.Close()
                if not had_open and ppt_app.Presentations.Count == 0:
                    ppt_app.Quit()
            if generated and (expected_n is None or len(generated) == expected_n):
                return generated
            generated = []

    # Strategy C: LibreOffice headless -> isolated temp dir PDF -> targeted render_pdf_to_pngs (fitz / WinRT)
    soffice_bin = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice_bin:
        with tempfile.TemporaryDirectory(prefix="pptx_lo_") as lo_tmp:
            lo_tmp_dir = Path(lo_tmp)
            subprocess.run(
                [soffice_bin, "--headless", "--convert-to", "pdf", "--outdir", str(lo_tmp_dir), str(src)],
                check=True,
                capture_output=True,
            )
            tmp_pdf = lo_tmp_dir / f"{src.stem}.pdf"
            if not tmp_pdf.exists():
                pdfs = list(lo_tmp_dir.glob("*.pdf"))
                if pdfs:
                    tmp_pdf = pdfs[0]
            if tmp_pdf.exists():
                eff_dpi = int(round(float(dpi))) if dpi is not None else max(144, round(float(width_px) / deck_w_in))
                from verify_visual_outputs import render_pdf_to_pngs

                raw_pngs = render_pdf_to_pngs(
                    str(tmp_pdf),
                    out_dir=str(lo_tmp_dir),
                    dpi=eff_dpi,
                    page_indices=target_indices,
                )
                if target_indices is not None and len(raw_pngs) != len(target_indices):
                    raise RuntimeError(
                        f"LibreOffice fallback rendered {len(raw_pngs)} page(s), expected {len(target_indices)}."
                    )
                renamed_pngs: list[str] = []
                for pos, p_str in enumerate(raw_pngs):
                    p_path = Path(p_str)
                    real_idx = target_indices[pos] if target_indices is not None else (pos + 1)
                    target_png = dest_dir / f"{PREVIEW_PREFIX}{src.stem}_s{real_idx:02d}.png"
                    if p_path.exists():
                        shutil.move(str(p_path), str(target_png))
                        renamed_pngs.append(str(target_png))
                if renamed_pngs and (expected_n is None or len(renamed_pngs) == expected_n):
                    return renamed_pngs

    raise RuntimeError(
        "Unable to export PPTX slides to PNG: neither Windows PowerPoint COM nor LibreOffice (`soffice`) was available."
    )


def _extract_slide_badge_label(png_path: Path, fallback_idx: int) -> str:
    """Derive a concise `S01` badge label from slide PNG filename or 1-based fallback index."""
    m = _SLIDE_NUM_RE.search(png_path.name)
    if m:
        return f"S{int(m.group(1)):02d}"
    return f"S{int(fallback_idx):02d}"


def _load_qa_badge_font(size_px: int):
    """Load a crisp bold sans-serif font for QA contact-sheet & grid corner badges."""
    from PIL import ImageFont  # type: ignore

    for candidate in (
        Path(r"C:\Windows\Fonts\msjhbd.ttc"),
        Path(r"C:\Windows\Fonts\msjh.ttc"),
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
    ):
        if candidate.exists():
            with suppress(OSError, ValueError):
                if candidate.suffix.lower() == ".ttc":
                    return ImageFont.truetype(str(candidate), size=int(size_px), index=0)
                return ImageFont.truetype(str(candidate), size=int(size_px))
    return ImageFont.load_default()


def _paste_slide_tile(
    canvas,
    draw,
    png_path: Path,
    x: int,
    y: int,
    tile_w: int,
    tile_h: int,
    label: str,
    badge_font,
    border_color: tuple[int, int, int] = (71, 85, 105),
) -> None:
    """Resize and paste a single slide PNG onto a Pillow canvas with crisp border & corner badge."""
    from PIL import Image  # type: ignore

    with Image.open(png_path) as raw_im:
        im = raw_im.convert("RGB")
        src_w, src_h = im.size
        if src_w == tile_w and src_h == tile_h:
            fitted = im
            ox, oy = 0, 0
        else:
            scale = min(tile_w / float(max(1, src_w)), tile_h / float(max(1, src_h)))
            new_w = max(1, int(round(src_w * scale)))
            new_h = max(1, int(round(src_h * scale)))
            resampler = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.BICUBIC)
            fitted = im.resize((new_w, new_h), resampler)
            ox = (tile_w - new_w) // 2
            oy = (tile_h - new_h) // 2
        canvas.paste(fitted, (x + ox, y + oy))

    draw.rectangle([x, y, x + tile_w - 1, y + tile_h - 1], outline=border_color, width=1)

    # Compact high-contrast slide number corner badge (bottom-right margin)
    bbox = draw.textbbox((0, 0), label, font=badge_font)
    txt_w = max(1, bbox[2] - bbox[0])
    txt_h = max(1, bbox[3] - bbox[1])
    pad_x, pad_y = 8, 4
    bw = txt_w + pad_x * 2
    bh = txt_h + pad_y * 2
    bx0 = max(x + 4, x + tile_w - bw - 6)
    by0 = max(y + 4, y + tile_h - bh - 6)
    draw.rounded_rectangle(
        [bx0, by0, bx0 + bw, by0 + bh],
        radius=4,
        fill=(15, 23, 42),
        outline=(56, 189, 248),
        width=1,
    )
    draw.text((bx0 + pad_x - bbox[0], by0 + pad_y - bbox[1]), label, fill=(248, 250, 252), font=badge_font)


def build_pptx_contact_sheet(
    png_paths: list[str] | tuple[str, ...],
    out_path: str,
    cols: int = 4,
    rows: int = 4,
    tile_width: int = 480,
    tile_height: int = 270,
    padding: int = 10,
    bg_color: tuple[int, int, int] = (15, 23, 42),
    trim_empty_rows: bool = True,
) -> str:
    """
    [Option C Tier 2] Assemble slide PNGs into a single pure-Pillow deck rhythm contact sheet
    (default `4×4`, auto-expanding rows if deck exceeds `cols*rows` so zero slides are dropped).
    Returns absolute path of the written PNG file.
    """
    from PIL import Image, ImageDraw  # type: ignore

    paths = [Path(p).resolve() for p in png_paths]
    if not paths:
        raise ValueError("png_paths cannot be empty for build_pptx_contact_sheet().")
    for p in paths:
        if not p.is_file():
            raise FileNotFoundError(f"Slide PNG not found: {p}")

    eff_cols = max(1, int(cols))
    needed_rows = max(1, math.ceil(len(paths) / float(eff_cols)))
    eff_rows = needed_rows if (needed_rows > int(rows) or trim_empty_rows) else max(1, int(rows))
    tw, th, pad = max(120, int(tile_width)), max(68, int(tile_height)), max(2, int(padding))
    header_h = 36

    canvas_w = pad + eff_cols * (tw + pad)
    canvas_h = header_h + pad + eff_rows * (th + pad)
    canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)
    draw = ImageDraw.Draw(canvas)
    hdr_font = _load_qa_badge_font(16)
    badge_font = _load_qa_badge_font(max(12, int(round(th * 0.062))))

    title_txt = f"PPTX Rhythm Contact Sheet  |  {len(paths)} Slides  ({eff_cols}x{eff_rows})"
    draw.text((pad + 2, 8), title_txt, fill=(226, 232, 240), font=hdr_font)
    draw.line([(0, header_h - 1), (canvas_w, header_h - 1)], fill=(51, 65, 85), width=1)

    for idx, p in enumerate(paths):
        r, c = divmod(idx, eff_cols)
        tx = pad + c * (tw + pad)
        ty = header_h + pad + r * (th + pad)
        label = _extract_slide_badge_label(p, idx + 1)
        _paste_slide_tile(canvas, draw, p, tx, ty, tw, th, label, badge_font)

    dest = Path(out_path).resolve()
    if dest.exists() and dest.is_dir():
        dest = dest / f"{QA_CONTACT_PREFIX}sheet.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(dest), format="PNG", optimize=True)
    return str(dest)


def build_pptx_qa_grids(
    png_paths: list[str] | tuple[str, ...],
    out_dir: str,
    cols: int = 2,
    rows: int = 2,
    width_px: int = 1920,
    height_px: int = 1080,
    prefix: str | None = None,
) -> list[str]:
    """
    [Option C Tier 2] Stitch all slide PNGs sequentially into `1920×1080` HD `2×2` four-up QA grids
    (`960×540` per tile with slide-number corner badges and crisp dividers) for 100% full-deck visual coverage.
    Output files follow `_qa_grid_<prefix>_g01.png`, `_qa_grid_<prefix>_g02.png`, ...
    Returns list of generated PNG paths.
    """
    from PIL import Image, ImageDraw  # type: ignore

    paths = [Path(p).resolve() for p in png_paths]
    if not paths:
        return []
    for p in paths:
        if not p.is_file():
            raise FileNotFoundError(f"Slide PNG not found: {p}")

    dest_dir = Path(out_dir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    eff_cols = max(1, int(cols))
    eff_rows = max(1, int(rows))
    per_grid = eff_cols * eff_rows
    cw, ch = max(320, int(width_px)), max(180, int(height_px))
    tile_w = cw // eff_cols
    tile_h = ch // eff_rows

    if prefix is None:
        stem = paths[0].stem
        if stem.startswith(PREVIEW_PREFIX):
            stem = stem[len(PREVIEW_PREFIX):]
        stem = re.sub(r"(?:_s|slide[_-]?)\d+$", "", stem, flags=re.IGNORECASE).strip("_- ")
        safe_prefix = stem or "deck"
    else:
        safe_prefix = str(prefix).strip("_- ") or "deck"

    badge_font = _load_qa_badge_font(max(14, int(round(tile_h * 0.040))))
    generated: list[str] = []

    for grid_idx, start in enumerate(range(0, len(paths), per_grid), start=1):
        chunk = paths[start : start + per_grid]
        canvas = Image.new("RGB", (cw, ch), (15, 23, 42))
        draw = ImageDraw.Draw(canvas)

        for local_idx, p in enumerate(chunk):
            r, c = divmod(local_idx, eff_cols)
            tx = c * tile_w
            ty = r * tile_h
            label = _extract_slide_badge_label(p, start + local_idx + 1)
            _paste_slide_tile(canvas, draw, p, tx, ty, tile_w, tile_h, label, badge_font)

        # Crisp grid divider lines separating tiles cleanly on white-background slides
        for c in range(1, eff_cols):
            lx = c * tile_w
            draw.line([(lx, 0), (lx, ch)], fill=(71, 85, 105), width=2)
        for r in range(1, eff_rows):
            ly = r * tile_h
            draw.line([(0, ly), (cw, ly)], fill=(71, 85, 105), width=2)

        out_file = dest_dir / f"{QA_GRID_PREFIX}{safe_prefix}_g{grid_idx:02d}.png"
        canvas.save(str(out_file), format="PNG", optimize=True)
        generated.append(str(out_file))

    return generated


def _shape_has_visible_border(shape) -> bool:
    """Read-only XML check for whether a python-pptx shape renders a visible border line."""
    with suppress(AttributeError, KeyError, TypeError, ValueError):
        sp_el = shape._element
        nv_pr = sp_el.find(".//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvSpPr")
        is_txbox = nv_pr is not None and nv_pr.get("txBox") in ("1", "true")
        ln_el = sp_el.find(
            "{http://schemas.openxmlformats.org/presentationml/2006/main}spPr/"
            "{http://schemas.openxmlformats.org/drawingml/2006/main}ln"
        )
        if ln_el is not None:
            no_fill = ln_el.find("{http://schemas.openxmlformats.org/drawingml/2006/main}noFill")
            if no_fill is not None:
                return False
            solid_fill = ln_el.find("{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill")
            if solid_fill is not None:
                return True
        if is_txbox:
            return False
        ln_ref = sp_el.find(
            "{http://schemas.openxmlformats.org/presentationml/2006/main}style/"
            "{http://schemas.openxmlformats.org/drawingml/2006/main}lnRef"
        )
        if ln_ref is not None and ln_ref.get("idx", "0") != "0":
            return True
    return False


def _iter_slide_shapes(
    shapes,
    parent_off_x: float = 0.0,
    parent_off_y: float = 0.0,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    ch_off_x: float = 0.0,
    ch_off_y: float = 0.0,
):
    """Yield `(shape, abs_left_emu, abs_top_emu, w_emu, h_emu)` recursively with exact GroupShape xfrm mapping."""
    ns_a = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    ns_p = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
    for shp in shapes:
        raw_x = float(shp.left or 0)
        raw_y = float(shp.top or 0)
        raw_w = float(shp.width or 0)
        raw_h = float(shp.height or 0)
        lx = parent_off_x + (raw_x - ch_off_x) * scale_x
        ty = parent_off_y + (raw_y - ch_off_y) * scale_y
        w = raw_w * scale_x
        h = raw_h * scale_y
        if hasattr(shp, "shapes"):
            g_ch_x, g_ch_y = 0.0, 0.0
            g_sx, g_sy = scale_x, scale_y
            with suppress(AttributeError, KeyError, TypeError, ValueError):
                xfrm = shp._element.find(f"{ns_p}grpSpPr/{ns_a}xfrm")
                if xfrm is not None:
                    ext_el = xfrm.find(f"{ns_a}ext")
                    ch_off_el = xfrm.find(f"{ns_a}chOff")
                    ch_ext_el = xfrm.find(f"{ns_a}chExt")
                    if ch_off_el is not None:
                        g_ch_x = float(ch_off_el.get("x", "0"))
                        g_ch_y = float(ch_off_el.get("y", "0"))
                    if ext_el is not None and ch_ext_el is not None:
                        cx = float(ext_el.get("cx", "0"))
                        cy = float(ext_el.get("cy", "0"))
                        ch_cx = float(ch_ext_el.get("cx", "0"))
                        ch_cy = float(ch_ext_el.get("cy", "0"))
                        if ch_cx > 0 and cx > 0:
                            g_sx = (w / ch_cx)
                        if ch_cy > 0 and cy > 0:
                            g_sy = (h / ch_cy)
            yield from _iter_slide_shapes(shp.shapes, lx, ty, g_sx, g_sy, g_ch_x, g_ch_y)
        else:
            yield (shp, round(lx), round(ty), round(w), round(h))


def _estimate_union_area_sq_in(rects: list[tuple[float, float, float, float]], grid_n: int = 80) -> float:
    """Estimate geometric union area of `(x, y, w, h)` rectangles via fine grid rasterization."""
    if not rects:
        return 0.0
    min_x = min(r[0] for r in rects)
    min_y = min(r[1] for r in rects)
    max_x = max(r[0] + r[2] for r in rects)
    max_y = max(r[1] + r[3] for r in rects)
    span_w = max_x - min_x
    span_h = max_y - min_y
    if span_w <= 0 or span_h <= 0:
        return 0.0
    dx = span_w / grid_n
    dy = span_h / grid_n
    covered = 0
    for gy in range(grid_n):
        cy = min_y + (gy + 0.5) * dy
        active_x = [r for r in rects if r[1] <= cy <= (r[1] + r[3])]
        if not active_x:
            continue
        for gx in range(grid_n):
            cx = min_x + (gx + 0.5) * dx
            if any(r[0] <= cx <= (r[0] + r[2]) for r in active_x):
                covered += 1
    return (covered / float(grid_n * grid_n)) * (span_w * span_h)


def _rgb_luminance(rgb) -> float:
    """Compute perceptual relative luminance (0..1) of a python-pptx RGBColor."""
    r = float(rgb[0]) / 255.0
    g = float(rgb[1]) / 255.0
    b = float(rgb[2]) / 255.0
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _slide_has_dark_background(slide, flat_shapes: list, canvas_w_in: float, canvas_h_in: float, emu_per_inch: float) -> bool:
    """Detect whether a slide uses a dark bookend/stage background (luminance < 0.22)."""
    from pptx.enum.dml import MSO_FILL  # type: ignore
    from pptx.enum.shapes import MSO_SHAPE_TYPE  # type: ignore

    with suppress(AttributeError, KeyError, TypeError, ValueError):
        bg_fill = slide.background.fill
        if bg_fill.type == MSO_FILL.SOLID and bg_fill.fore_color and bg_fill.fore_color.rgb:
            if _rgb_luminance(bg_fill.fore_color.rgb) < 0.22:
                return True

    for shp, _lx, _ty, w_emu, h_emu in flat_shapes:
        w_in = w_emu / emu_per_inch
        h_in = h_emu / emu_per_inch
        if w_in < canvas_w_in * 0.90 or h_in < canvas_h_in * 0.90:
            continue
        if getattr(shp, "shape_type", None) == MSO_SHAPE_TYPE.PICTURE:
            continue
        if shp.has_text_frame and (shp.text_frame.text or "").strip():
            continue
        with suppress(AttributeError, KeyError, TypeError, ValueError):
            if shp.fill.type == MSO_FILL.SOLID and shp.fill.fore_color and shp.fill.fore_color.rgb:
                if _rgb_luminance(shp.fill.fore_color.rgb) < 0.22:
                    return True
    return False


def _shape_has_omml(shape) -> bool:
    """Return True if a python-pptx shape contains native `<m:oMath>` OMML equation XML."""
    with suppress(AttributeError, TypeError, ValueError):
        return shape._element.find(".//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath") is not None
    return False


def _shape_is_rounded_rect(shape) -> bool:
    """Return True if a shape is a ROUNDED_RECTANGLE AutoShape (used for pills & badges)."""
    from pptx.enum.shapes import MSO_SHAPE  # type: ignore

    with suppress(AttributeError, TypeError, ValueError):
        return getattr(shape, "auto_shape_type", None) == MSO_SHAPE.ROUNDED_RECTANGLE
    return False


def _build_paragraph_measure_input(para) -> tuple[str, bool, float, float]:
    """
    Resolve `(measure_text, default_bold, max_pt, min_pt)` from a python-pptx paragraph.
    Preserves mixed bold/regular spans as inline `**...**` for `measure_text_layout()`
    (sanitizing any literal `**` out of the measurement string only; raw residual `**` is audited separately).
    """
    raw_p = para.text or ""
    p_def_pt = para.font.size.pt if (para.font and para.font.size) else None
    p_def_bold = bool(para.font.bold) if (para.font and para.font.bold is not None) else False
    ne_runs = [r for r in para.runs if (r.text or "").strip()]

    if ne_runs:
        resolved_pts = [
            r.font.size.pt if (r.font and r.font.size) else (p_def_pt if p_def_pt is not None else 18.0)
            for r in ne_runs
        ]
        max_pt = float(max(resolved_pts))
        min_pt = float(min(resolved_pts))
        run_bolds = [
            bool(r.font.bold) if (r.font and r.font.bold is not None) else p_def_bold
            for r in ne_runs
        ]
        if all(run_bolds):
            return raw_p.replace("**", ""), True, max_pt, min_pt
        if not any(run_bolds):
            return raw_p.replace("**", ""), False, max_pt, min_pt

        # Mixed bold/regular runs: encode bold non-empty spans per line with inline `**...**`
        parts: list[str] = []
        for r in para.runs:
            rt = (r.text or "").replace("\x0b", "\n").replace("**", "")
            if not rt:
                continue
            r_bold = bool(r.font.bold) if (r.font and r.font.bold is not None) else p_def_bold
            if r_bold and rt.strip():
                segs = rt.split("\n")
                wrapped_segs: list[str] = []
                for seg in segs:
                    if seg.strip():
                        lead_ws = seg[: len(seg) - len(seg.lstrip())]
                        trail_ws = seg[len(seg.rstrip()) :]
                        wrapped_segs.append(f"{lead_ws}**{seg.strip()}**{trail_ws}")
                    else:
                        wrapped_segs.append(seg)
                parts.append("\n".join(wrapped_segs))
            else:
                parts.append(rt)
        return "".join(parts), False, max_pt, min_pt

    eff_pt = float(p_def_pt) if p_def_pt is not None else 18.0
    return raw_p.replace("**", ""), p_def_bold, eff_pt, eff_pt


def _inspect_embedded_image_quality(shape, w_in: float, h_in: float) -> dict | None:
    """
    Audit an embedded Picture shape for raster blur (`effective_ppi < 150`) and
    high-DPI chart downscaling (`scale_ratio < 0.80` for >= 150 DPI native charts,
    signaling need for a dedicated 1:1 `*_slide.png`).
    """
    if w_in < 1.0 or h_in < 0.8:
        return None
    with suppress(ImportError, AttributeError, OSError, ValueError, TypeError):
        from PIL import Image  # type: ignore

        blob = shape.image.blob
        with Image.open(io.BytesIO(blob)) as im:
            px_w, px_h = im.size
            if px_w <= 0 or px_h <= 0:
                return None
            eff_ppi_x = float(px_w) / float(w_in)
            eff_ppi_y = float(px_h) / float(h_in)
            eff_ppi = min(eff_ppi_x, eff_ppi_y)

            dpi_info = im.info.get("dpi")
            scale_ratio: float | None = None
            native_in: tuple[float, float] | None = None
            if isinstance(dpi_info, (tuple, list)) and len(dpi_info) >= 2:
                dx, dy = float(dpi_info[0] or 0.0), float(dpi_info[1] or 0.0)
                if dx >= 150.0 and dy >= 150.0:
                    nat_w = float(px_w) / dx
                    nat_h = float(px_h) / dy
                    native_in = (round(nat_w, 2), round(nat_h, 2))
                    scale_ratio = min(w_in / nat_w, h_in / nat_h)

            low_ppi = eff_ppi < 150.0
            over_shrunk = scale_ratio is not None and scale_ratio < 0.80
            if low_ppi or over_shrunk:
                return {
                    "name": shape.name,
                    "pixel_size": (int(px_w), int(px_h)),
                    "placed_in": (round(w_in, 2), round(h_in, 2)),
                    "native_in": native_in,
                    "eff_ppi": round(eff_ppi, 1),
                    "scale_ratio": round(scale_ratio, 3) if scale_ratio is not None else None,
                    "low_ppi": low_ppi,
                    "over_shrunk": over_shrunk,
                }
    return None


def _parse_spec_lock_metadata(spec_lock_path, eng_mod) -> dict:
    """Load optional `02c_slide_spec_lock.json` (path or dict) for family, floor, and Mode 3 metadata."""
    meta: dict = {
        "loaded": False,
        "min_font_pt": None,
        "mode3_active": False,
        "slides": {},  # 1-based slide_num -> {"family_id", "family_group", "variant", "boxed", "is_mode3_visual"}
    }
    if spec_lock_path is None:
        return meta

    import json

    raw_spec = None
    if isinstance(spec_lock_path, dict):
        raw_spec = spec_lock_path
    else:
        p = Path(spec_lock_path).resolve()
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(f"spec_lock_path not found: {p}")
        raw_spec = json.loads(p.read_text(encoding="utf-8"))

    if not isinstance(raw_spec, dict):
        return meta

    meta["loaded"] = True
    deck_meta = raw_spec.get("deck_meta") if isinstance(raw_spec.get("deck_meta"), dict) else {}
    design_tokens = raw_spec.get("design_tokens") if isinstance(raw_spec.get("design_tokens"), dict) else {}

    for candidate in (design_tokens.get("min_font_pt"), deck_meta.get("min_font_pt")):
        if candidate is not None:
            with suppress(ValueError, TypeError):
                meta["min_font_pt"] = max(12.0, float(candidate))
                break

    design_mode = str(deck_meta.get("design_mode") or deck_meta.get("mode") or "").lower()
    if "3" in design_mode or "bespoke" in design_mode or "creative" in design_mode or deck_meta.get("mode3_tier"):
        meta["mode3_active"] = True

    slides_list = raw_spec.get("slides") if isinstance(raw_spec.get("slides"), list) else []
    norm_fn = getattr(eng_mod, "_normalize_layout_entry", None) if eng_mod is not None else None

    for idx, sl in enumerate(slides_list, start=1):
        if not isinstance(sl, dict):
            continue
        lay = sl.get("layout") if isinstance(sl.get("layout"), dict) else {}
        if norm_fn is not None and lay:
            info = norm_fn(lay)
            canon_id = str(info.get("canonical_id") or "")
            fam_group = str(info.get("family_group") or (canon_id.split("-")[0] if "-" in canon_id else ""))
            variant = str(info.get("variant") or "")
            boxed = bool(info.get("boxed", False))
        else:
            canon_id = str(lay.get("family_id") or lay.get("layout") or "").strip().upper()
            fam_group = canon_id.split("-")[0] if "-" in canon_id else ""
            variant = str(lay.get("variant") or "").strip().lower()
            boxed = variant in ("clean_card", "card_arrow", "boxed", "bento")

        has_mode3_layer = bool(
            lay.get("geometric_accent")
            or lay.get("motif_type")
            or lay.get("mode3_tier")
            or (meta["mode3_active"] and canon_id != "F5-A" and lay.get("visual_asset"))
        )
        meta["slides"][idx] = {
            "family_id": canon_id,
            "family_group": fam_group,
            "variant": variant,
            "boxed": boxed,
            "is_mode3_visual": has_mode3_layer,
        }
    return meta


def verify_pptx_structure(
    pptx_path: str,
    min_font_pt: float | None = None,
    profile: str = "reading",
    spec_lock_path: str | Path | dict | None = None,
    **kwargs,
) -> dict:
    """
    Two-Track Verification & Option C Tier-1 QA Engine for Format C `.pptx` presentations (Phase 2 Step 6):
    - Powered by Pillow real font metrics + Traditional Chinese Kinsoku wrapping (`measure_text_layout()`).
    - Zero arbitrary word-count caps (`不使用死板總字數判定議題數`).
    - 100% backward-compatible when `spec_lock_path=None`.
    - HARD ERRORS (`issues` & `errors` -> `passed = False`):
      1. Minimum Slide Count (< 2 bookend slides).
      2. Missing `Speaker_Notes` on any slide.
      3. Dynamic Canvas Out-of-Bounds (tolerance 0.08").
      4. Content Typography Floor Violation (`< min_font_pt`; exempts Zone 1 top pills & `F1-A` bookend pills >= 8.5pt,
         including dark closing `F1-A` slides followed by trailing `F4-B` Appendix slides).
      5. Physical Text Box Overflow (Pillow `measure_text_layout()` real heights, tolerance +0.12").
      6. Zone 2 vs. Zone 3 Vertical Overlap Collision (`zone_overlap_slides`, upgraded from Soft Warning to Hard Error).
      7. Arbitrary Non-Background Content-Box Collision (`shape_collisions`, `siril9`-inspired).
      8. Residual Markdown `**` or Draft Placeholders (`TBD` / `TODO` / `FIXME`).
      9. Optional `spec_lock_path` Copy & Key Numeric Fidelity Verification (`check_copy_fidelity()`).
    - SOFT WARNINGS (`warnings` -> diagnostic quality alerts, does NOT flip `passed` to `False`):
      1. Single-character / <= 2 CJK char orphan line wrapping (F5).
      2. Embedded image downscale `< 0.80×` (for >=150 DPI charts) or effective PPI `< 150` (`*_slide.png` alert).
      3. Left-right / top-bottom spatial imbalance (`imbalanced_slides`) & vertical top-heavy check (`vertical_top_heavy_slides`: middle content slides with Zone 2 top gap `< 0.30"` and bottom whitespace `> 1.80"`, excluding `F1-A`/`F1-B`).
      4. Boxed card slide ratio `> 40%` (`boxed_slide_ratio`, `slide_count >= 4`).
      5. Single layout family ratio `> 40%` (`family_distribution`, `slide_count >= 6`).
      6. Primary Visual + Stacked Boxed Cards (`visual_with_boxed_cards_slides`).
      7. Nested Box-in-Box Header (`nested_box_slides`).
      8. Local Box Crowding (`> 86%` fill) or Tall Box Sparsity (`< 28%` fill on `h >= 2.60"`).
      9. Excessive Bordered Containers (`>= 6` in Zone 2).
    - Automatically emits `high_risk_slides` (chart/table/formula/Mode-3/Warning/Error/>75%-fill slides) for Option C Tier 3.
    """
    _ = kwargs  # Reserved for forward-compatible optional flags
    import unicodedata

    from pptx import Presentation  # type: ignore
    from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE  # type: ignore

    src = Path(pptx_path).resolve()
    if not src.exists() or not src.is_file():
        raise FileNotFoundError(f"PPTX file not found: {src}")

    eng_mod = _load_slide_engine_module()
    measure_fn = getattr(eng_mod, "measure_text_layout", None) if eng_mod is not None else None
    msjh_line_em = float(getattr(eng_mod, "MSJH_LINE_HEIGHT_EM", 1.3333)) if eng_mod is not None else 1.3333
    spec_meta = _parse_spec_lock_metadata(spec_lock_path, eng_mod)

    mode = str(profile or "reading").strip().lower()
    if min_font_pt is not None:
        effective_min_pt = float(min_font_pt)
    elif spec_meta["min_font_pt"] is not None:
        effective_min_pt = float(spec_meta["min_font_pt"])
    else:
        effective_min_pt = 16.0 if mode == "live" else 12.0

    prs = Presentation(str(src))
    slide_count = len(prs.slides)
    emu_per_inch = 914400.0
    canvas_w_in = float(prs.slide_width or 12192000) / emu_per_inch
    canvas_h_in = float(prs.slide_height or 6858000) / emu_per_inch
    canvas_area = max(1.0, canvas_w_in * canvas_h_in)

    issues: list[str] = []
    warnings: list[str] = []
    missing_notes_slides: list[int] = []
    overflow_boxes: list[dict] = []
    out_of_bounds_shapes: list[dict] = []
    under_min_font_items: list[dict] = []
    zone_overlap_slides: list[int] = []
    shape_collisions: list[dict] = []
    residual_markdown_items: list[dict] = []
    draft_placeholder_items: list[dict] = []
    orphan_lines: list[dict] = []
    image_quality_warnings: list[dict] = []
    imbalanced_slides: list[dict] = []
    vertical_top_heavy_slides: list[dict] = []
    crowded_boxes: list[dict] = []
    sparse_boxes: list[dict] = []
    nested_box_slides: list[int] = []
    visual_with_boxed_cards_slides: list[int] = []
    excess_container_slides: list[int] = []
    boxed_slides: list[int] = []
    family_counts: dict[str, int] = {}
    high_risk_reasons: dict[int, list[str]] = {}
    slide_metrics: list[dict] = []

    def _mark_high_risk(s_idx: int, reason: str) -> None:
        bucket = high_risk_reasons.setdefault(s_idx, [])
        if reason not in bucket:
            bucket.append(reason)

    if slide_count < 2:
        issues.append(f"簡報僅有 {slide_count} 頁，不符合首尾定錨頁（至少封面＋結尾 2 頁）規範。")

    total_slide_chars = 0
    total_notes_chars = 0
    global_min_content_pt: float | None = None
    arrow_types = {
        MSO_SHAPE.RIGHT_ARROW,
        MSO_SHAPE.LEFT_ARROW,
        MSO_SHAPE.DOWN_ARROW,
        MSO_SHAPE.UP_ARROW,
    }

    # Pre-scan slide shapes and dark backgrounds across deck so whole-deck `dark_stage` themes
    # are distinguished cleanly from isolated dark `F1-A` bookend slides (even with trailing Appendix).
    all_slide_shapes: list[list] = [list(_iter_slide_shapes(sl.shapes)) for sl in prs.slides]
    slide_dark_flags: list[bool] = [
        _slide_has_dark_background(sl, fl, canvas_w_in, canvas_h_in, emu_per_inch)
        for sl, fl in zip(prs.slides, all_slide_shapes)
    ]
    is_whole_deck_dark = slide_count >= 4 and (sum(slide_dark_flags) > max(2, int(slide_count * 0.5)))

    for idx, (slide, flat_shapes, is_dark_bg) in enumerate(
        zip(prs.slides, all_slide_shapes, slide_dark_flags), start=1
    ):
        sl_spec_info = spec_meta["slides"].get(idx, {})
        spec_family_id = str(sl_spec_info.get("family_id") or "")
        spec_family_group = str(sl_spec_info.get("family_group") or "")

        notes_txt = ""
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None:
            notes_txt = (slide.notes_slide.notes_text_frame.text or "").strip()
        if not notes_txt:
            missing_notes_slides.append(idx)
            _mark_high_risk(idx, "missing_speaker_notes")
        else:
            for m_ph in _DRAFT_PLACEHOLDER_RE.finditer(notes_txt):
                draft_placeholder_items.append(
                    {"slide": idx, "location": "speaker_notes", "token": m_ph.group(0), "snippet": notes_txt[:22]}
                )
        notes_non_ws = sum(1 for c in notes_txt if not c.isspace())
        total_notes_chars += notes_non_ws

        # Pre-scan structural cues before main shape loop so `is_bookend_slide` is accurate
        # on dark_stage decks, light bookends, and trailing F4-B Appendix slides alike.
        pre_has_table = False
        pre_has_omml = False
        pre_has_primary_pic = False
        pre_has_z1_pill = False
        pre_has_z1_divider = False
        pre_has_bookend_badge = False
        pre_z1_wide_texts: list[tuple[float, float]] = []
        pre_z1_divider_bars: list[tuple[float, float]] = []
        for _shp, _lx, _ty, _w, _h in flat_shapes:
            _top = _ty / emu_per_inch
            _wi = _w / emu_per_inch
            _hi = _h / emu_per_inch
            if getattr(_shp, "has_table", False):
                pre_has_table = True
            if _shape_has_omml(_shp):
                pre_has_omml = True
            if getattr(_shp, "shape_type", None) == MSO_SHAPE_TYPE.PICTURE:
                if not (_wi >= canvas_w_in * 0.88 and _hi >= canvas_h_in * 0.88) and _wi >= 3.2 and _hi >= 1.6:
                    pre_has_primary_pic = True
            _has_t = bool(_shp.has_text_frame and (_shp.text_frame.text or "").strip())
            if _has_t:
                _txt = (_shp.text_frame.text or "").strip()
                if _top <= 0.45 and _hi <= 0.38:
                    pre_has_z1_pill = True
                if 0.42 <= _top <= 0.80 and _hi <= 0.42 and len(_txt) <= 48 and _shape_is_rounded_rect(_shp):
                    pre_has_bookend_badge = True
                if 0.18 <= _top <= 2.20 and _hi <= 1.35 and _wi >= canvas_w_in * 0.65:
                    pre_z1_wide_texts.append((_top, _top + _hi))
            elif (
                not getattr(_shp, "has_table", False)
                and getattr(_shp, "shape_type", None) != MSO_SHAPE_TYPE.PICTURE
                and _wi >= canvas_w_in * 0.75
                and _hi <= 0.04
                and 0.55 <= _top <= 2.35
            ):
                pre_z1_divider_bars.append((_top, _top + _hi))

        # Structurally chain Zone 1 headline -> tightly-adjacent subtitle (+0.03") -> tightly-adjacent divider (+0.06")
        # so multi-line headers with `show_divider=False` never lose their subtitle or misclassify Zone 2 top hairlines.
        pre_z1_wide_texts.sort(key=lambda pair: pair[0])
        z1_text_bottom: float | None = None
        for _wt_top, _wt_bot in pre_z1_wide_texts:
            if z1_text_bottom is None:
                if 0.18 <= _wt_top <= 0.72 and _wt_bot <= 1.90:
                    z1_text_bottom = _wt_bot
            elif (z1_text_bottom - 0.01) <= _wt_top <= (z1_text_bottom + 0.10) and (_wt_bot - _wt_top) <= 0.85:
                z1_text_bottom = max(z1_text_bottom, _wt_bot)

        z1_bottom_in: float | None = None
        if z1_text_bottom is not None:
            matched_divs = [
                (_dt, _db) for (_dt, _db) in pre_z1_divider_bars
                if (z1_text_bottom - 0.02) <= _dt <= (z1_text_bottom + 0.11)
            ]
            if matched_divs:
                pre_has_z1_divider = True
                z1_bottom_in = round(min(_db for _dt, _db in matched_divs), 3)
            elif pre_has_z1_pill:
                z1_bottom_in = round(z1_text_bottom, 3)
        elif pre_z1_divider_bars:
            fallback_divs = [(_dt, _db) for (_dt, _db) in pre_z1_divider_bars if 0.65 <= _dt <= 1.50]
            if fallback_divs:
                if any(_dt <= 1.35 for _dt, _db in fallback_divs):
                    pre_has_z1_divider = True
                z1_bottom_in = round(min(_db for _dt, _db in fallback_divs), 3)
        pre_has_z1_header = pre_has_z1_pill and (pre_has_z1_divider or z1_text_bottom is not None)

        if spec_family_id:
            is_bookend_slide = spec_family_id == "F1-A"
        else:
            is_obvious_content = (
                pre_has_table
                or pre_has_omml
                or pre_has_primary_pic
                or (pre_has_z1_header and not (is_dark_bg and not is_whole_deck_dark))
            )
            if is_obvious_content:
                is_bookend_slide = False
            elif idx == 1:
                is_bookend_slide = True
            elif is_dark_bg and not is_whole_deck_dark:
                is_bookend_slide = True
            elif pre_has_bookend_badge and not pre_has_z1_pill:
                is_bookend_slide = True
            elif idx == slide_count and not pre_has_z1_pill:
                is_bookend_slide = True
            else:
                is_bookend_slide = False

        slide_non_ws = 0
        slide_min_pt: float | None = None
        slide_max_font_pt: float = 0.0
        slide_max_fill_pct: float = 0.0
        slide_rects: list[tuple[float, float, float, float]] = []
        bordered_boxes: list[tuple[float, float, float, float, bool]] = []  # (x, y, w, h, has_text)
        picture_rects: list[tuple[float, float, float, float]] = []
        content_boxes: list[tuple[str, float, float, float, float, str]] = []  # (name, x, y, w, h, kind)
        formula_text_boxes: list[tuple[float, float, float, float]] = []
        z2_balance_boxes: list[tuple[float, float, float, float]] = []
        has_arrow_shape = False
        has_table_on_slide = False
        has_omml_on_slide = False
        has_full_bleed_pic = False
        has_h_axis_line = False
        has_v_axis_line = False
        large_kpi_boxes = 0
        has_wide_z2_quote = False

        for shape, lx_emu, ty_emu, w_emu, h_emu in flat_shapes:
            left_in = lx_emu / emu_per_inch
            top_in = ty_emu / emu_per_inch
            w_in = w_emu / emu_per_inch
            h_in = h_emu / emu_per_inch

            if (
                left_in < -0.08
                or top_in < -0.08
                or (left_in + w_in) > (canvas_w_in + 0.08)
                or (top_in + h_in) > (canvas_h_in + 0.08)
            ):
                out_of_bounds_shapes.append(
                    {
                        "slide": idx,
                        "name": shape.name,
                        "bounds": (round(left_in, 2), round(top_in, 2), round(w_in, 2), round(h_in, 2)),
                    }
                )

            has_txt = bool(shape.has_text_frame and (shape.text_frame.text or "").strip())
            has_tbl = bool(getattr(shape, "has_table", False))
            has_omml = _shape_has_omml(shape)
            is_pic = getattr(shape, "shape_type", None) == MSO_SHAPE_TYPE.PICTURE
            is_full_bleed_pic = is_pic and w_in >= canvas_w_in * 0.88 and h_in >= canvas_h_in * 0.88
            if is_full_bleed_pic:
                has_full_bleed_pic = True
            if has_tbl:
                has_table_on_slide = True
            if has_omml:
                has_omml_on_slide = True

            is_full_bleed_bg = (
                w_in >= canvas_w_in * 0.92
                and h_in >= canvas_h_in * 0.92
                and not has_txt
                and not has_tbl
                and not has_omml
                and not is_pic
            )

            # Detect crosshair axes (F4-A / S5 structural cue)
            if not has_txt and not has_tbl and not is_pic:
                if w_in >= canvas_w_in * 0.70 and h_in <= 0.05 and 2.5 <= top_in <= 5.5:
                    has_h_axis_line = True
                if h_in >= canvas_h_in * 0.45 and w_in <= 0.05 and 4.5 <= left_in <= 8.8:
                    has_v_axis_line = True

            # Track visible footprint for outer whitespace estimation (skip hairlines & full-bleed backgrounds)
            if w_in >= 0.15 and h_in >= 0.12 and not is_full_bleed_bg and not is_full_bleed_pic:
                cx0 = max(0.0, left_in)
                cy0 = max(0.0, top_in)
                cx1 = min(canvas_w_in, left_in + w_in)
                cy1 = min(canvas_h_in, top_in + h_in)
                if cx1 > cx0 and cy1 > cy0:
                    slide_rects.append((cx0, cy0, cx1 - cx0, cy1 - cy0))

            # Track content boxes for arbitrary collision linter (exclude full-bleed background images/rects)
            if has_txt or has_tbl or has_omml or (is_pic and not is_full_bleed_pic):
                c_kind = "table" if has_tbl else ("picture" if is_pic else ("omml" if has_omml else "text"))
                full_raw_c = (shape.text_frame.text or "").strip() if has_txt else ""
                c_label = full_raw_c.replace("\n", " ")[:18] if has_txt else (shape.name or c_kind)
                content_boxes.append((c_label, left_in, top_in, w_in, h_in, c_kind))
                if has_txt and any(sym in full_raw_c for sym in ("=", "∑", "√", "÷", "∝", "≈")):
                    formula_text_boxes.append((left_in, top_in, w_in, h_in))
                if top_in >= 1.15 and (top_in + h_in) <= (canvas_h_in - 0.55):
                    z2_balance_boxes.append((left_in, top_in, w_in, h_in))

            if is_pic:
                if not is_full_bleed_pic and w_in >= 3.2 and h_in >= 1.6:
                    picture_rects.append((left_in, top_in, w_in, h_in))
                img_warn = _inspect_embedded_image_quality(shape, w_in, h_in)
                if img_warn is not None:
                    img_warn["slide"] = idx
                    image_quality_warnings.append(img_warn)

            with suppress(AttributeError, ValueError, TypeError):
                auto_t = getattr(shape, "auto_shape_type", None)
                if auto_t in arrow_types or (
                    auto_t == MSO_SHAPE.ISOSCELES_TRIANGLE and w_in <= 0.45 and h_in <= 0.45
                ):
                    has_arrow_shape = True

            if _shape_has_visible_border(shape) and w_in >= 1.0 and h_in >= 0.36 and not is_full_bleed_bg:
                bordered_boxes.append((left_in, top_in, w_in, h_in, has_txt))

            # Inspect native Table cells if present (deduplicating spanned/merged cells)
            if has_tbl:
                seen_tcs: set[object] = set()
                for row in shape.table.rows:
                    for cell in row.cells:
                        if getattr(cell, "is_spanned", False):
                            continue
                        tc_obj = getattr(cell, "_tc", cell)
                        if tc_obj in seen_tcs:
                            continue
                        seen_tcs.add(tc_obj)
                        cell_txt = (cell.text or "").strip()
                        if not cell_txt:
                            continue
                        slide_non_ws += sum(1 for c in cell_txt if not c.isspace())
                        if "**" in cell_txt:
                            residual_markdown_items.append(
                                {"slide": idx, "location": "table", "snippet": cell_txt.replace("\n", " ")[:24]}
                            )
                        for m_ph in _DRAFT_PLACEHOLDER_RE.finditer(cell_txt):
                            draft_placeholder_items.append(
                                {
                                    "slide": idx,
                                    "location": "table",
                                    "token": m_ph.group(0),
                                    "snippet": cell_txt.replace("\n", " ")[:24],
                                }
                            )
                        for para in cell.text_frame.paragraphs:
                            if not (para.text or "").strip():
                                continue
                            p_def_pt = para.font.size.pt if (para.font and para.font.size) else None
                            ne_runs = [r for r in para.runs if (r.text or "").strip()]
                            if ne_runs:
                                pts_to_check = [
                                    r.font.size.pt
                                    if (r.font and r.font.size)
                                    else (p_def_pt if p_def_pt is not None else 18.0)
                                    for r in ne_runs
                                ]
                            elif p_def_pt is not None:
                                pts_to_check = [p_def_pt]
                            else:
                                pts_to_check = []
                            for pt_val in pts_to_check:
                                slide_max_font_pt = max(slide_max_font_pt, float(pt_val))
                                slide_min_pt = pt_val if slide_min_pt is None else min(slide_min_pt, pt_val)
                                global_min_content_pt = (
                                    pt_val if global_min_content_pt is None else min(global_min_content_pt, pt_val)
                                )
                                if pt_val < effective_min_pt - 1e-6:
                                    under_min_font_items.append(
                                        {
                                            "slide": idx,
                                            "font_pt": round(float(pt_val), 1),
                                            "snippet": (para.text or "").strip().replace("\n", " ")[:22],
                                        }
                                    )

            if has_txt:
                tf = shape.text_frame
                full_tf_txt = (tf.text or "").strip()
                slide_non_ws += sum(1 for c in full_tf_txt if not c.isspace())

                # Residual Markdown `**` and draft placeholders (`TBD` / `TODO` / `FIXME`) -> Hard Error
                if "**" in full_tf_txt:
                    residual_markdown_items.append(
                        {"slide": idx, "location": shape.name, "snippet": full_tf_txt.replace("\n", " ")[:24]}
                    )
                for m_ph in _DRAFT_PLACEHOLDER_RE.finditer(full_tf_txt):
                    draft_placeholder_items.append(
                        {
                            "slide": idx,
                            "location": shape.name,
                            "token": m_ph.group(0),
                            "snippet": full_tf_txt.replace("\n", " ")[:24],
                        }
                    )

                # Step 5 fix: recognize `F1-A` bookend 10.5pt pill even when trailing `F4-B` Appendix follows closing
                # (strictly gated on `is_bookend_slide` so trailing Appendix & dark_stage content slides are never exempted)
                is_bookend_pill_zone = (
                    is_bookend_slide
                    and top_in <= 0.80
                    and h_in <= 0.42
                    and len(full_tf_txt) <= 48
                    and (spec_family_id == "F1-A" or _shape_is_rounded_rect(shape))
                )
                is_nav_pill = (top_in <= 0.45 and h_in <= 0.38) or is_bookend_pill_zone

                ml_in = (tf.margin_left / emu_per_inch) if tf.margin_left is not None else 0.10
                mr_in = (tf.margin_right / emu_per_inch) if tf.margin_right is not None else 0.10
                mt_in = (tf.margin_top / emu_per_inch) if tf.margin_top is not None else 0.05
                mb_in = (tf.margin_bottom / emu_per_inch) if tf.margin_bottom is not None else 0.05
                usable_w = max(0.25, w_in - ml_in - mr_in)
                usable_h = max(0.15, h_in - mt_in - mb_in)

                non_empty_paras = [p for p in tf.paragraphs if (p.text or "").strip()]
                wrap_enabled = tf.word_wrap is not False
                req_h_in = 0.0
                total_est_lines = 0
                shape_max_pt = 0.0

                for p_idx, para in enumerate(non_empty_paras):
                    raw_p = para.text or ""
                    meas_text, def_bold, p_pt, min_run_pt = _build_paragraph_measure_input(para)
                    shape_max_pt = max(shape_max_pt, p_pt)
                    slide_max_font_pt = max(slide_max_font_pt, p_pt)

                    if is_nav_pill:
                        if min_run_pt < 8.5 - 1e-6:
                            under_min_font_items.append(
                                {
                                    "slide": idx,
                                    "font_pt": round(float(min_run_pt), 1),
                                    "snippet": raw_p.strip().replace("\n", " ")[:22],
                                }
                            )
                    else:
                        slide_min_pt = min_run_pt if slide_min_pt is None else min(slide_min_pt, min_run_pt)
                        global_min_content_pt = (
                            min_run_pt if global_min_content_pt is None else min(global_min_content_pt, min_run_pt)
                        )
                        if min_run_pt < effective_min_pt - 1e-6:
                            under_min_font_items.append(
                                {
                                    "slide": idx,
                                    "font_pt": round(float(min_run_pt), 1),
                                    "snippet": raw_p.strip().replace("\n", " ")[:22],
                                }
                            )

                    # Line spacing calculation (supports multiplier, exact Pt, or PowerPoint default 1.0x natural height)
                    # Multi-line leading follows font metrics (MSJH_LINE_HEIGHT_EM), while final/single pure-ASCII
                    # display tokens (e.g. '01', '70%', 'KPI') have ~1.05em visual cap+descender height.
                    has_cjk_in_para = any(unicodedata.east_asian_width(ch) in ("W", "F") for ch in raw_p)
                    final_em = msjh_line_em if has_cjk_in_para else 1.05
                    ls = para.line_spacing
                    if ls is None:
                        ls_mult = 1.0
                        single_h_in = (p_pt * final_em) / 72.0
                        step_in = (p_pt * msjh_line_em) / 72.0
                    elif hasattr(ls, "pt"):
                        step_in = float(ls.pt) / 72.0
                        single_h_in = min(step_in, (p_pt * final_em) / 72.0)
                        ls_mult = max(1.0, float(ls.pt) / max(1.0, p_pt * msjh_line_em))
                    else:
                        ls_mult = max(1.0, float(ls))
                        single_h_in = (p_pt * final_em) / 72.0
                        step_in = ((p_pt * msjh_line_em) / 72.0) * ls_mult

                    if para.space_before is not None and hasattr(para.space_before, "pt"):
                        req_h_in += float(para.space_before.pt) / 72.0

                    p_lines_count = 0
                    if measure_fn is not None:
                        m_res = measure_fn(
                            meas_text.replace("\x0b", "\n"),
                            box_width_in=(usable_w if wrap_enabled else 999.0),
                            font_pt=p_pt,
                            bold=def_bold,
                            line_spacing=ls_mult,
                        )
                        p_lines_count = max(1, int(m_res["line_count"]))
                        if wrap_enabled and not is_nav_pill and bool(m_res.get("orphan_flag")):
                            orphan_lines.append(
                                {
                                    "slide": idx,
                                    "box_w": round(w_in, 2),
                                    "last_line": str(m_res.get("last_line_text") or ""),
                                    "snippet": raw_p.strip().replace("\n", " ")[:22],
                                }
                            )
                    else:
                        chars_per_line = max(1.0, (usable_w * 72.0) / (p_pt * 1.02))
                        for sub_line in raw_p.replace("\x0b", "\n").splitlines():
                            if not sub_line.strip():
                                p_lines_count += 1
                                continue
                            if not wrap_enabled:
                                p_lines_count += 1
                            else:
                                eff_len = sum(
                                    1.0 if unicodedata.east_asian_width(c) in ("W", "F") else 0.54 for c in sub_line
                                )
                                p_lines_count += max(1, math.ceil(eff_len / chars_per_line))

                    total_est_lines += p_lines_count
                    if p_idx < len(non_empty_paras) - 1:
                        req_h_in += p_lines_count * step_in
                        if para.space_after is not None and hasattr(para.space_after, "pt"):
                            req_h_in += float(para.space_after.pt) / 72.0
                    else:
                        req_h_in += (max(0, p_lines_count - 1) * step_in) + single_h_in

                if shape_max_pt >= 28.0 and 1.2 <= top_in <= 3.1 and h_in <= 1.6 and len(full_tf_txt) <= 18:
                    large_kpi_boxes += 1
                if shape_max_pt >= 26.0 and top_in >= 1.40 and w_in >= 6.0 and len(full_tf_txt) >= 6:
                    has_wide_z2_quote = True

                fill_ratio = req_h_in / usable_h if usable_h > 0 else 0.0
                fill_pct = round(fill_ratio * 100.0, 1)
                if h_in >= 0.85 and total_est_lines >= 3:
                    slide_max_fill_pct = max(slide_max_fill_pct, fill_pct)

                if req_h_in > usable_h + 0.12:
                    overflow_boxes.append(
                        {
                            "slide": idx,
                            "box_w": round(w_in, 2),
                            "box_h": round(usable_h, 2),
                            "req_h": round(req_h_in, 2),
                            "snippet": full_tf_txt.replace("\n", " ")[:24],
                        }
                    )
                elif h_in >= 0.85 and total_est_lines >= 3 and fill_ratio > 0.86:
                    crowded_boxes.append(
                        {
                            "slide": idx,
                            "fill_pct": fill_pct,
                            "snippet": full_tf_txt.replace("\n", " ")[:20],
                        }
                    )
                elif (
                    h_in >= 2.60
                    and not is_bookend_slide
                    and spec_family_id not in ("F1-A", "F1-B", "F1-C")
                    and fill_pct < 28.0
                ):
                    sparse_boxes.append(
                        {
                            "slide": idx,
                            "box_h": round(h_in, 2),
                            "fill_pct": fill_pct,
                            "snippet": full_tf_txt.replace("\n", " ")[:20],
                        }
                    )

        # --- Anti-pattern & Collision Checks ---
        # 1. Nested Box-in-Box (Soft Warning)
        has_nested_hdr = False
        for i_a, (ax, ay, aw, ah, _) in enumerate(bordered_boxes):
            if ah < 1.35:
                continue
            for i_b, (bx, by, bw, bh, b_txt) in enumerate(bordered_boxes):
                if i_a == i_b or not b_txt:
                    continue
                if (
                    bx >= ax - 0.05
                    and (bx + bw) <= (ax + aw + 0.05)
                    and by >= ay - 0.05
                    and (by + bh) <= (ay + ah - 0.25)
                    and bw >= aw * 0.78
                ):
                    has_nested_hdr = True
                    break
            if has_nested_hdr:
                break
        if has_nested_hdr:
            nested_box_slides.append(idx)

        # 2. Detect S4 clean mechanism diagram mats
        s4_diagram_rects: list[tuple[float, float, float, float]] = []
        if has_arrow_shape:
            for i_m, (mx, my, mw, mh, m_txt) in enumerate(bordered_boxes):
                if m_txt or mw < 4.0 or mh < 2.2:
                    continue
                inner_nodes = sum(
                    1
                    for i_n, (nx, ny, nw, nh, _) in enumerate(bordered_boxes)
                    if i_n != i_m
                    and nx >= mx - 0.04
                    and (nx + nw) <= (mx + mw + 0.04)
                    and ny >= my - 0.04
                    and (ny + nh) <= (my + mh + 0.04)
                )
                if inner_nodes >= 3:
                    s4_diagram_rects.append((mx, my, mw, mh))

        primary_visual_rects = list(picture_rects) + s4_diagram_rects
        if primary_visual_rects:
            z2_cards = 0
            for bx, by, bw, bh, _ in bordered_boxes:
                if bw < 1.5 or by < 0.95 or by > (canvas_h_in - 1.05) or bh < 0.55:
                    continue
                encloses_vis = any(
                    vx >= bx - 0.10
                    and (vx + vw) <= (bx + bw + 0.10)
                    and vy >= by - 0.10
                    and (vy + vh) <= (by + bh + 0.10)
                    for (vx, vy, vw, vh) in primary_visual_rects
                )
                inside_vis = any(
                    bx >= vx - 0.08
                    and (bx + bw) <= (vx + vw + 0.08)
                    and by >= vy - 0.08
                    and (by + bh) <= (vy + vh + 0.08)
                    for (vx, vy, vw, vh) in primary_visual_rects
                )
                if not encloses_vis and not inside_vis:
                    z2_cards += 1
            if z2_cards >= 2:
                visual_with_boxed_cards_slides.append(idx)

        # 3. Zone 2 vs. Zone 3 Vertical Overlap Collision (UPGRADED TO HARD ERROR)
        footer_rects = [
            (rx, ry, rw, rh)
            for (rx, ry, rw, rh) in slide_rects
            if ry >= (canvas_h_in - 1.15) and rw >= canvas_w_in * 0.72 and rh <= 1.05
        ]
        if footer_rects:
            has_z_overlap = False
            for fx, fy, fw, _fh in footer_rects:
                for rx, ry, rw, rh in slide_rects:
                    if ry >= fy - 0.15 or ry < 1.0 or rh < 0.45:
                        continue
                    horiz_ov = min(fx + fw, rx + rw) - max(fx, rx)
                    if horiz_ov > 0.50 and (ry + rh) > (fy + 0.04):
                        has_z_overlap = True
                        break
                if has_z_overlap:
                    break
            if has_z_overlap:
                zone_overlap_slides.append(idx)

        # 4. Top-level Zone 2 bordered containers (excess container warning & boxed slide ratio)
        top_level_z2: list[tuple[float, float, float, float]] = []
        for i_a, (ax, ay, aw, ah, _) in enumerate(bordered_boxes):
            if aw < 1.5 or ay < 1.00 or ay > (canvas_h_in - 1.05):
                continue
            is_inside_another = any(
                i_a != i_b
                and ax >= bx - 0.04
                and (ax + aw) <= (bx + bw + 0.04)
                and ay >= by - 0.04
                and (ay + ah) <= (by + bh + 0.04)
                for i_b, (bx, by, bw, bh, _) in enumerate(bordered_boxes)
            )
            if not is_inside_another:
                top_level_z2.append((ax, ay, aw, ah))
        if len(top_level_z2) >= 6:
            excess_container_slides.append(idx)

        # 5. Arbitrary Non-Background Content-Box Collision Linter (HARD ERROR, siril9-inspired)
        for i_c in range(len(content_boxes)):
            lbl_a, x1, y1, w1, h1, kind_a = content_boxes[i_c]
            for j_c in range(i_c + 1, len(content_boxes)):
                lbl_b, x2, y2, w2, h2, kind_b = content_boxes[j_c]
                ox = min(x1 + w1, x2 + w2) - max(x1, x2)
                oy = min(y1 + h1, y2 + h2) - max(y1, y2)
                if ox > 0.08 and oy > 0.08 and (ox * oy) > 0.015:
                    shape_collisions.append(
                        {
                            "slide": idx,
                            "box_a": lbl_a,
                            "box_b": lbl_b,
                            "kinds": (kind_a, kind_b),
                            "overlap_in": (round(ox, 2), round(oy, 2)),
                        }
                    )
        # Also detect sibling non-nested Zone 2 bordered card containers colliding with each other
        for i_b in range(len(top_level_z2)):
            x1, y1, w1, h1 = top_level_z2[i_b]
            for j_b in range(i_b + 1, len(top_level_z2)):
                x2, y2, w2, h2 = top_level_z2[j_b]
                ox = min(x1 + w1, x2 + w2) - max(x1, x2)
                oy = min(y1 + h1, y2 + h2) - max(y1, y2)
                if ox > 0.08 and oy > 0.08 and (ox * oy) > 0.02:
                    shape_collisions.append(
                        {
                            "slide": idx,
                            "box_a": f"card#{i_b + 1}",
                            "box_b": f"card#{j_b + 1}",
                            "kinds": ("card_container", "card_container"),
                            "overlap_in": (round(ox, 2), round(oy, 2)),
                        }
                    )

        # 6. Boxed slide & single focal formula box classification (spec-backed when available, else structural)
        non_mat_z2 = [
            b for b in top_level_z2
            if b[3] >= 1.0 and not any(
                abs(b[0] - mx) <= 0.05 and abs(b[1] - my) <= 0.05 for (mx, my, _mw, _mh) in s4_diagram_rects
            )
        ]
        has_formula_focal_box = False
        if not is_bookend_slide and len(non_mat_z2) == 1 and not s4_diagram_rects:
            fx, fy, fw, fh = non_mat_z2[0]
            for cx, cy, cw, ch in formula_text_boxes:
                if (
                    cx >= fx - 0.08
                    and (cx + cw) <= (fx + fw + 0.08)
                    and cy >= fy - 0.08
                    and (cy + ch) <= (fy + fh + 0.08)
                ):
                    has_formula_focal_box = True
                    break

        if sl_spec_info:
            is_boxed_slide = bool(sl_spec_info.get("boxed", False))
        else:
            is_boxed_slide = (not is_bookend_slide) and (len(non_mat_z2) >= 2)
        if is_boxed_slide:
            boxed_slides.append(idx)

        # 7. Family group classification (for >40% single-family ratio warning)
        has_quote_manifesto = (
            not is_bookend_slide
            and not has_table_on_slide
            and not picture_rects
            and not has_arrow_shape
            and not has_omml_on_slide
            and not has_formula_focal_box
            and large_kpi_boxes < 3
            and len(non_mat_z2) == 0
            and len(z2_balance_boxes) <= 4
            and has_wide_z2_quote
        )
        if spec_family_group:
            eff_family_group = spec_family_group
        else:
            if is_bookend_slide or (slide_max_font_pt >= 40.0 and len(content_boxes) <= 5) or has_quote_manifesto:
                eff_family_group = "F1"
            elif has_table_on_slide or (has_h_axis_line and has_v_axis_line):
                eff_family_group = "F4"
            elif picture_rects or has_omml_on_slide or has_formula_focal_box or large_kpi_boxes >= 3:
                eff_family_group = "F5"
            elif has_arrow_shape or s4_diagram_rects:
                eff_family_group = "F3"
            else:
                eff_family_group = "F2"
        family_counts[eff_family_group] = family_counts.get(eff_family_group, 0) + 1

        # 8. Whitespace, Vertical Top-Heavy & Left-Right / Top-Bottom Visual Balance Check (Soft Warning)
        covered_sq_in = _estimate_union_area_sq_in(slide_rects)
        outer_ws_pct = round(max(0.0, 100.0 - (covered_sq_in / canvas_area) * 100.0), 1)

        # 8a. Vertical Top-Heavy Check (excludes F1-A/F1-B bookends/dividers and properly centered slides)
        z2_top_gap_in: float | None = None
        z2_bottom_gap_in: float | None = None
        is_vertical_top_heavy = False
        if (
            not is_bookend_slide
            and spec_family_id not in ("F1-A", "F1-B")
            and z1_bottom_in is not None
        ):
            z3_ceiling_y = min(fy for (_fx, fy, _fw, _fh) in footer_rects) if footer_rects else canvas_h_in
            z2_v_spans: list[tuple[float, float]] = []
            for _lbl, _bx, by, _bw, bh, _ck in content_boxes:
                if by >= (z1_bottom_in + 0.02) and (by + bh) <= (z3_ceiling_y + 0.03) and by < (z3_ceiling_y - 0.02):
                    z2_v_spans.append((by, by + bh))
            for _bx, by, _bw, bh, _ht in bordered_boxes:
                if by >= (z1_bottom_in + 0.02) and (by + bh) <= (z3_ceiling_y + 0.03) and by < (z3_ceiling_y - 0.02):
                    z2_v_spans.append((by, by + bh))
            if z2_v_spans:
                z2_min_y = min(sp_t for sp_t, _sp_b in z2_v_spans)
                z2_max_b = max(sp_b for _sp_t, sp_b in z2_v_spans)
                z2_top_gap_in = round(max(0.0, z2_min_y - z1_bottom_in), 2)
                z2_bottom_gap_in = round(max(0.0, z3_ceiling_y - z2_max_b), 2)
                if z2_top_gap_in < 0.30 and z2_bottom_gap_in > 1.80:
                    is_vertical_top_heavy = True
                    vertical_top_heavy_slides.append(
                        {
                            "slide": idx,
                            "z2_top_gap_in": z2_top_gap_in,
                            "z2_bottom_gap_in": z2_bottom_gap_in,
                            "has_zone3": bool(footer_rects),
                            "detail": (
                                f"Zone 2 上方留白 {z2_top_gap_in:.2f}\" < 0.30\" 且底部空白 {z2_bottom_gap_in:.2f}\" > 1.80\""
                                "（頭重腳輕，建議啟用兩段式舒展與光學置中）"
                            ),
                        }
                    )

        if (
            not is_bookend_slide
            and spec_family_id not in ("F1-A", "F1-B", "F1-C", "F4-B")
            and not has_table_on_slide
            and len(z2_balance_boxes) >= 2
        ):
            mid_x = canvas_w_in / 2.0
            z2_top, z2_bot = 1.30, max(2.0, canvas_h_in - 0.60)
            mid_y = (z2_top + z2_bot) / 2.0
            left_a = right_a = top_a = bot_a = 0.0
            for bx, by, bw, bh in z2_balance_boxes:
                lx0, lx1 = max(0.0, bx), min(mid_x, bx + bw)
                rx0, rx1 = max(mid_x, bx), min(canvas_w_in, bx + bw)
                if lx1 > lx0:
                    left_a += (lx1 - lx0) * bh
                if rx1 > rx0:
                    right_a += (rx1 - rx0) * bh
                ty0, ty1 = max(z2_top, by), min(mid_y, by + bh)
                by0, by1 = max(mid_y, by), min(z2_bot, by + bh)
                if ty1 > ty0:
                    top_a += (ty1 - ty0) * bw
                if by1 > by0:
                    bot_a += (by1 - by0) * bw

            tot_lr = left_a + right_a
            tot_tb = top_a + bot_a
            if tot_lr >= 4.0 and (min(left_a, right_a) / tot_lr) < 0.15:
                side = "左側" if left_a > right_a else "右側"
                imbalanced_slides.append(
                    {
                        "slide": idx,
                        "axis": "horizontal",
                        "detail": f"Zone 2 內容過度偏向{side}（左/右面積比 {round(left_a/tot_lr*100)}%:{round(right_a/tot_lr*100)}%）",
                    }
                )
            elif (
                not is_vertical_top_heavy
                and tot_tb >= 6.0
                and outer_ws_pct > 50.0
                and (min(top_a, bot_a) / tot_tb) < 0.10
            ):
                side = "上方" if top_a > bot_a else "下方"
                imbalanced_slides.append(
                    {
                        "slide": idx,
                        "axis": "vertical",
                        "detail": f"Zone 2 內容過度集中於{side}（上/下面積比 {round(top_a/tot_tb*100)}%:{round(bot_a/tot_tb*100)}%）",
                    }
                )

        # 9. Tag high-risk slides for Option C Tier 3 single-slide full-res inspection
        if picture_rects or spec_family_id == "F5-A":
            _mark_high_risk(idx, "chart_or_visual_F5A")
        if has_table_on_slide or spec_family_id == "F4-B":
            _mark_high_risk(idx, "table_F4B")
        if has_omml_on_slide or has_formula_focal_box or spec_family_id == "F5-C":
            _mark_high_risk(idx, "formula_F5C")
        if has_full_bleed_pic or bool(sl_spec_info.get("is_mode3_visual")):
            _mark_high_risk(idx, "mode3_visual")
        if slide_max_fill_pct > 75.0:
            _mark_high_risk(idx, f"high_fill_{slide_max_fill_pct}%")

        total_slide_chars += slide_non_ws
        slide_metrics.append(
            {
                "slide": idx,
                "family_id": spec_family_id or None,
                "family_group": eff_family_group,
                "is_boxed": is_boxed_slide,
                "slide_chars": slide_non_ws,
                "notes_chars": notes_non_ws,
                "min_font_pt": round(float(slide_min_pt), 1) if slide_min_pt is not None else None,
                "max_box_fill_pct": slide_max_fill_pct,
                "outer_whitespace_pct": outer_ws_pct,
                "z2_top_gap_in": z2_top_gap_in,
                "z2_bottom_gap_in": z2_bottom_gap_in,
            }
        )

    # --- Optional Step 5 Spec-Lock Copy & Numeric Fidelity Audit ---
    copy_fidelity_report: dict | None = None
    if spec_lock_path is not None and eng_mod is not None:
        check_fid_fn = getattr(eng_mod, "check_copy_fidelity", None)
        if check_fid_fn is not None:
            copy_fidelity_report = check_fid_fn(spec_lock_path, str(src))
            if not copy_fidelity_report.get("passed", False):
                fid_errs = copy_fidelity_report.get("errors", [])
                for fe in fid_errs:
                    s_no = int(fe.get("slide", 0) or 0)
                    if s_no > 0:
                        _mark_high_risk(s_no, "copy_fidelity_mismatch")
                detail = "; ".join(str(fe.get("detail") or fe) for fe in fid_errs[:6])
                issues.append(f"與鎖定規格 `02c_slide_spec_lock.json` 文案／關鍵數字保真失配：{detail}")

    # --- Assemble Hard Errors (`issues` & `errors` -> `passed = False`) ---
    if missing_notes_slides:
        pages_str = ", ".join(str(p) for p in missing_notes_slides)
        issues.append(f"第 {pages_str} 頁缺少演講者備忘稿 (Speaker Notes)。")
    if out_of_bounds_shapes:
        for item in out_of_bounds_shapes:
            _mark_high_risk(item["slide"], "out_of_bounds")
        detail = ", ".join(f"第{item['slide']}頁({item['name']})" for item in out_of_bounds_shapes[:8])
        issues.append(
            f"偵測到元件超出 {round(canvas_w_in, 3)}\"×{round(canvas_h_in, 3)}\" 投影片畫布邊界：{detail}。"
        )
    if under_min_font_items:
        by_slide: dict[int, tuple[float, str]] = {}
        for u in under_min_font_items:
            s_no = u["slide"]
            _mark_high_risk(s_no, "under_min_font")
            if s_no not in by_slide or u["font_pt"] < by_slide[s_no][0]:
                by_slide[s_no] = (u["font_pt"], u["snippet"])
        detail = "; ".join(f"第{s}頁({pt}pt「{snip}...」)" for s, (pt, snip) in sorted(by_slide.items()))
        issues.append(
            f"偵測到內容字級低於 {effective_min_pt:.1f}pt 硬底線（嚴禁縮字硬塞，請拆頁擴展）：{detail}。"
        )
    if overflow_boxes:
        for b in overflow_boxes:
            _mark_high_risk(b["slide"], "text_overflow")
        detail = "; ".join(
            f"第{b['slide']}頁「{b['snippet']}...」(可用框高{b['box_h']}\" < Pillow實測需求{b['req_h']}\")"
            for b in overflow_boxes[:8]
        )
        issues.append(
            f"偵測到文字物理穿框／溢位風險（請先調幾何擴展容器或拆頁，勿縮字低於底線）：{detail}。"
        )
    if zone_overlap_slides:
        for s_no in zone_overlap_slides:
            _mark_high_risk(s_no, "zone2_zone3_overlap")
        s_str = ", ".join(str(s) for s in zone_overlap_slides)
        issues.append(
            f"第 {s_str} 頁偵測到中央 Zone 2 與底部 Zone 3 橫幅發生垂直重疊碰撞（硬錯誤），請縮減 Zone 2 高度或省略 Zone 3。"
        )
    if shape_collisions:
        for col in shape_collisions:
            _mark_high_risk(col["slide"], "shape_collision")
        detail = "; ".join(
            f"第{c['slide']}頁「{c['box_a']}」×「{c['box_b']}」(重疊{c['overlap_in'][0]}\"×{c['overlap_in'][1]}\")"
            for c in shape_collisions[:8]
        )
        issues.append(f"偵測到非背景內容框邊界碰撞重疊（硬錯誤）：{detail}。")
    if residual_markdown_items:
        for rm in residual_markdown_items:
            _mark_high_risk(rm["slide"], "residual_markdown")
        detail = "; ".join(f"第{r['slide']}頁「{r['snippet']}...」" for r in residual_markdown_items[:6])
        issues.append(f"畫面殘留未轉譯之 Markdown 星號 `**`（硬錯誤）：{detail}。")
    if draft_placeholder_items:
        for dp in draft_placeholder_items:
            _mark_high_risk(dp["slide"], "draft_placeholder")
        detail = "; ".join(f"第{d['slide']}頁({d['token']} @ {d['location']})" for d in draft_placeholder_items[:6])
        issues.append(f"偵測到未填寫之草稿佔位字 `TBD`/`TODO`/`FIXME`（硬錯誤）：{detail}。")

    # --- Assemble Soft Warnings (`warnings`, do NOT flip `passed`) ---
    if orphan_lines:
        by_s_orph: dict[int, list[str]] = {}
        for o in orphan_lines:
            _mark_high_risk(o["slide"], "orphan_line")
            by_s_orph.setdefault(o["slide"], []).append(o["last_line"])
        detail = "; ".join(f"第{s}頁({', '.join(repr(x) for x in ls[:2])})" for s, ls in sorted(by_s_orph.items())[:8])
        warnings.append(
            f"偵測到單字／雙字孤兒換行（尾行 <= 2 漢字＋標點；建議優先微調框寬／欄寬幾何，無解時再徵求使用者微調文案）：{detail}。"
        )
    if image_quality_warnings:
        parts = []
        for iw in image_quality_warnings:
            _mark_high_risk(iw["slide"], "image_scale_or_ppi")
            reasons = []
            if iw["over_shrunk"]:
                reasons.append(f"縮放比 {iw['scale_ratio']}x < 0.80x")
            if iw["low_ppi"]:
                reasons.append(f"實效 {iw['eff_ppi']} PPI < 150")
            parts.append(f"第{iw['slide']}頁({', '.join(reasons)})")
        warnings.append(
            f"嵌入圖片解析度或縮放比警示（高密圖表被壓縮恐致小字模糊，建議由同繪圖腳本另存 1:1 專用 `*_slide.png`）：{'; '.join(parts[:8])}。"
        )
    if imbalanced_slides:
        for imb in imbalanced_slides:
            _mark_high_risk(imb["slide"], "spatial_imbalance")
        detail = "; ".join(f"第{i['slide']}頁({i['detail']})" for i in imbalanced_slides[:6])
        warnings.append(f"偵測到畫面左右／上下視覺分布失衡：{detail}。")
    if vertical_top_heavy_slides:
        for vth in vertical_top_heavy_slides:
            _mark_high_risk(vth["slide"], "vertical_top_heavy")
        detail = "; ".join(
            f"第{v['slide']}頁(上留白{v['z2_top_gap_in']:.2f}\"/底空白{v['z2_bottom_gap_in']:.2f}\")"
            for v in vertical_top_heavy_slides[:8]
        )
        warnings.append(
            f"偵測到上下垂直頭重腳輕（Vertical Top-Heavy：Zone 2 上方留白 < 0.30\" 且底部空白 > 1.80\"，建議啟用兩段式自然舒展與整體群組光學置中）：{detail}。"
        )

    boxed_slide_ratio = round(len(boxed_slides) / float(slide_count), 3) if slide_count > 0 else 0.0
    if slide_count >= 4 and boxed_slide_ratio > 0.40 + 1e-9:
        warnings.append(
            f"方塊卡片頁佔比達 {boxed_slide_ratio:.1%}（{len(boxed_slides)}/{slide_count} 頁，超過 <= 40% 去方塊節奏目標），"
            "建議將部分卡片轉為無框排版（minimal_column / borderless_centerline / F2-B / F3-A fine_track / F4-A 去框十字軸）。"
        )

    if slide_count >= 6:
        for fg, cnt in sorted(family_counts.items()):
            f_ratio = cnt / float(slide_count)
            if f_ratio > 0.40 + 1e-9:
                warnings.append(
                    f"單一版型家族 `{fg}` 佔比達 {f_ratio:.1%}（{cnt}/{slide_count} 頁，超過 <= 40% 多樣性上限），建議跨 F1–F5 分散版型節奏。"
                )

    if visual_with_boxed_cards_slides:
        for s_no in visual_with_boxed_cards_slides:
            _mark_high_risk(s_no, "visual_with_boxed_cards")
        s_str = ", ".join(str(s) for s in visual_with_boxed_cards_slides)
        warnings.append(
            f"第 {s_str} 頁含主視覺圖（統計圖表或機制架構圖）卻同時堆疊多個帶框卡片（違反『圖旁不疊卡』規範，建議改用旁側／上方／下方無框導讀列或僅留大標＋副標）。"
        )
    if nested_box_slides:
        for s_no in nested_box_slides:
            _mark_high_risk(s_no, "nested_box")
        s_str = ", ".join(str(s) for s in nested_box_slides)
        warnings.append(
            f"第 {s_str} 頁偵測到『雙層套盒（框中框表頭或列框）』線條雜訊，建議改用單層去套盒卡片。"
        )
    if crowded_boxes:
        crowd_by_slide: dict[int, float] = {}
        for c in crowded_boxes:
            s_no = c["slide"]
            _mark_high_risk(s_no, "crowded_box")
            crowd_by_slide[s_no] = max(crowd_by_slide.get(s_no, 0.0), float(c["fill_pct"]))
        detail = ", ".join(f"第{s}頁({pct}%)" for s, pct in list(sorted(crowd_by_slide.items()))[:8])
        warnings.append(
            f"部分文字框局部填滿率 > 86%（Tullis 框內呼吸空間偏緊，建議檢視是否需拆頁）：{detail}。"
        )
    if sparse_boxes:
        sparse_by_slide: dict[int, float] = {}
        for sb in sparse_boxes:
            s_no = sb["slide"]
            _mark_high_risk(s_no, "sparse_tall_box")
            sparse_by_slide[s_no] = min(sparse_by_slide.get(s_no, 100.0), float(sb["fill_pct"]))
        detail = ", ".join(f"第{s}頁({pct}%)" for s, pct in list(sorted(sparse_by_slide.items()))[:8])
        warnings.append(
            f"部分高容器（>= 2.6\"）局部填滿率 < 28%（容器過空，建議採 Content-Driven Height 收緊高度並將留白推出框外）：{detail}。"
        )
    if excess_container_slides:
        for s_no in excess_container_slides:
            _mark_high_risk(s_no, "excess_containers")
        s_str = ", ".join(str(s) for s in excess_container_slides)
        warnings.append(
            f"第 {s_str} 頁中央畫布出現 >= 6 個獨立帶框容器（超過簡報兩層組塊 2～4 主容器上限，請檢查是否同頁硬併了多個子議題）。"
        )

    high_risk_slides = sorted(high_risk_reasons.keys())
    avg_ws = (
        round(sum(m["outer_whitespace_pct"] for m in slide_metrics) / len(slide_metrics), 1)
        if slide_metrics
        else 0.0
    )
    s2n_ratio = round(total_slide_chars / float(total_notes_chars), 2) if total_notes_chars > 0 else None
    min_pt_str = f"{global_min_content_pt:.1f}pt" if global_min_content_pt is not None else "N/A"
    stats_line = (
        f"🎤 PPTX 雙軌體檢（{mode}，底線 >={effective_min_pt:.1f}pt）：共 {slide_count} 頁｜"
        f"最小內容字級 {min_pt_str}｜平均外圍留白 {avg_ws}%｜方塊頁 {round(boxed_slide_ratio * 100, 1)}%｜"
        f"螢幕/講稿字數 {total_slide_chars}/{total_notes_chars}"
        + (f" ({s2n_ratio}x)" if s2n_ratio is not None else "")
        + f"｜硬錯誤 {len(issues)} 項，軟提醒 {len(warnings)} 項，高風險精檢頁 {len(high_risk_slides)} 頁。"
    )
    return {
        "passed": len(issues) == 0,
        "profile": mode,
        "min_font_floor_pt": effective_min_pt,
        "min_content_font_pt": round(float(global_min_content_pt), 1) if global_min_content_pt is not None else None,
        "slide_count": slide_count,
        "total_slide_chars": total_slide_chars,
        "total_notes_chars": total_notes_chars,
        "slide_to_notes_ratio": s2n_ratio,
        "avg_outer_whitespace_pct": avg_ws,
        "boxed_slides": boxed_slides,
        "boxed_slide_ratio": boxed_slide_ratio,
        "family_distribution": family_counts,
        "missing_notes_slides": missing_notes_slides,
        "overflow_boxes": overflow_boxes,
        "out_of_bounds_shapes": out_of_bounds_shapes,
        "under_min_font_items": under_min_font_items,
        "zone_overlap_slides": zone_overlap_slides,
        "shape_collisions": shape_collisions,
        "residual_markdown_items": residual_markdown_items,
        "draft_placeholder_items": draft_placeholder_items,
        "orphan_lines": orphan_lines,
        "image_quality_warnings": image_quality_warnings,
        "imbalanced_slides": imbalanced_slides,
        "vertical_top_heavy_slides": vertical_top_heavy_slides,
        "crowded_boxes": crowded_boxes,
        "sparse_boxes": sparse_boxes,
        "nested_box_slides": nested_box_slides,
        "visual_with_boxed_cards_slides": visual_with_boxed_cards_slides,
        "excess_container_slides": excess_container_slides,
        "copy_fidelity": copy_fidelity_report,
        "high_risk_slides": high_risk_slides,
        "high_risk_reasons": high_risk_reasons,
        "warnings": warnings,
        "slide_metrics": slide_metrics,
        "issues": issues,
        "errors": list(issues),
        "stats_line": stats_line,
    }
