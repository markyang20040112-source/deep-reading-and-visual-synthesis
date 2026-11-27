"""
pptx_engine/media_omml.py
Playwright/Chromium 300 DPI SVG/HTML rasterizer and native editable OOXML `<m:oMath>` equation builder.
Note: `pptx_slide_engine` is the public entry point.
"""

import math
import os
import re
import shutil
import subprocess
import tempfile
from contextlib import suppress
from pathlib import Path

from pptx.enum.text import PP_ALIGN
from pptx.util import Pt

from .tokens import FONT_FAMILY, MIN_CONTENT_FONT_PT, _populate_paragraph_runs

MAX_CHROME_CLI_DIM_PX = 8192


def _find_chromium_cli_binary() -> str | None:
    """Locate local Chrome or Edge binary for headless CLI fallback."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    for name in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    return None


def _finalize_png_300dpi(
    png_path: Path,
    dpi: int = 300,
    transparent: bool = True,
    expected_size: tuple[int, int] | None = None,
) -> None:
    """Stamp exact `(dpi, dpi)` PNG metadata and preserve RGBA alpha via Pillow."""
    from PIL import Image  # type: ignore

    with Image.open(png_path) as im:
        out_im = im.convert("RGBA") if transparent else im.convert("RGB")
        if expected_size is not None and out_im.size != expected_size:
            # Trim minor Chrome CLI viewport padding or upscale cleanly if clamped for oversized canvas
            ew, eh = expected_size
            cw, ch = out_im.size
            if cw >= ew and ch >= eh and (cw - ew) <= 24 and (ch - eh) <= 24:
                out_im = out_im.crop((0, 0, ew, eh))
        out_im.save(png_path, format="PNG", dpi=(float(dpi), float(dpi)))


def _render_with_playwright(
    target_html_uri: str,
    out_png: Path,
    width_px: int,
    height_px: int,
    scale_factor: float,
    transparent: bool,
    timeout_sec: int,
) -> None:
    """Primary Tier 3 renderer using Playwright + Chromium."""
    from playwright.sync_api import sync_playwright  # type: ignore

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                viewport={"width": int(width_px), "height": int(height_px)},
                device_scale_factor=float(scale_factor),
            )
            page = context.new_page()
            page.goto(target_html_uri, wait_until="networkidle", timeout=int(timeout_sec * 1000))
            with suppress(Exception):
                page.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
            page.screenshot(
                path=str(out_png),
                omit_background=bool(transparent),
                full_page=False,
                timeout=int(timeout_sec * 1000),
            )
        finally:
            browser.close()


def _render_with_chrome_cli(
    target_html_uri: str,
    out_png: Path,
    width_px: int,
    height_px: int,
    scale_factor: float,
    transparent: bool,
    timeout_sec: int,
) -> None:
    """Fallback Tier 3 renderer using local Chrome / Edge headless CLI with oversized-canvas guard."""
    browser_bin = _find_chromium_cli_binary()
    if not browser_bin:
        raise RuntimeError(
            "Neither Playwright Chromium nor local Chrome/Edge CLI binary is available for 300 DPI rendering."
        )

    # Oversized canvas guard: cap physical render bitmap to MAX_CHROME_CLI_DIM_PX to prevent headless OOM/clipping
    eff_scale = float(scale_factor)
    max_dim = max(int(width_px), int(height_px))
    if max_dim * eff_scale > MAX_CHROME_CLI_DIM_PX:
        eff_scale = max(1.0, MAX_CHROME_CLI_DIM_PX / float(max_dim))

    tmp_profile = Path(tempfile.mkdtemp(prefix="pptx_chrome_cli_"))
    try:
        cmd = [
            browser_bin,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--hide-scrollbars",
            f"--user-data-dir={tmp_profile}",
            f"--window-size={int(width_px)},{int(height_px)}",
            f"--force-device-scale-factor={eff_scale:.3f}",
            f"--screenshot={out_png}",
        ]
        if transparent:
            cmd.append("--default-background-color=00000000")
        cmd.append(target_html_uri)

        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=int(timeout_sec),
            check=False,
        )
        if not out_png.exists() or out_png.stat().st_size == 0:
            raise RuntimeError(
                f"Chrome/Edge CLI failed to produce PNG (code={res.returncode}): {(res.stderr or res.stdout).strip()[:300]}"
            )
    finally:
        shutil.rmtree(tmp_profile, ignore_errors=True)


def render_svg_to_png_300dpi(
    html_or_svg_path: str | Path,
    out_png_path: str | Path,
    width_px: int = 1200,
    height_px: int = 800,
    engine: str = "auto",
    scale_factor: float = 3.0,
    dpi: int = 300,
    transparent: bool = True,
    timeout_sec: int = 45,
) -> str:
    """
    Mode 3 Tier 3 Dual-Engine 300 DPI Transparent Renderer:
    - Accepts an `.html` or `.svg` file (wrapping raw `.svg` in a transparent zero-margin HTML shell).
    - Primary engine (`engine="auto"` or `"playwright"`): Playwright + Chromium with
      `device_scale_factor=scale_factor` & `omit_background=transparent`.
    - Fallback engine (`engine="chrome_cli"`, or automatic fallback when Playwright is unavailable):
      Local Chrome / Edge `--headless=new --default-background-color=00000000` with oversized-canvas guard.
    - Post-processes with Pillow to guarantee RGBA output and exact `dpi=(300.0, 300.0)` PNG metadata.
    Returns absolute resolved path string of `out_png_path`.
    """
    src = Path(html_or_svg_path).resolve()
    if not src.exists() or not src.is_file():
        raise FileNotFoundError(f"HTML/SVG source not found: {src}")

    w_px = max(16, int(width_px))
    h_px = max(16, int(height_px))
    raw_scale = float(scale_factor)
    if not math.isfinite(raw_scale):
        raise ValueError(f"scale_factor must be a finite number; got {scale_factor!r}.")
    eff_scale = max(1.0, raw_scale)
    eff_dpi = max(72, int(dpi))
    out_png = Path(out_png_path).resolve()
    out_png.parent.mkdir(parents=True, exist_ok=True)

    eng = str(engine or "auto").strip().lower()
    if eng not in ("auto", "playwright", "chrome_cli"):
        raise ValueError(f"Unsupported engine '{engine}'. Use 'auto', 'playwright', or 'chrome_cli'.")

    tmp_html: Path | None = None
    try:
        if src.suffix.lower() == ".svg":
            svg_raw = src.read_text(encoding="utf-8-sig").strip()
            bg_css = "transparent" if transparent else "#FFFFFF"
            html_doc = (
                "<!DOCTYPE html><html><head><meta charset='utf-8'>"
                f"<style>html,body{{margin:0;padding:0;width:{w_px}px;height:{h_px}px;"
                f"overflow:hidden;background:{bg_css};}}svg{{display:block;width:100%;height:100%;}}</style>"
                f"</head><body>{svg_raw}</body></html>"
            )
            fd, tmp_name = tempfile.mkstemp(prefix="_pptx_svg_wrap_", suffix=".html", dir=str(out_png.parent))
            os.close(fd)
            tmp_html = Path(tmp_name)
            tmp_html.write_text(html_doc, encoding="utf-8")
            target_uri = tmp_html.as_uri()
        else:
            target_uri = src.as_uri()

        if eng == "playwright":
            _render_with_playwright(target_uri, out_png, w_px, h_px, eff_scale, transparent, timeout_sec)
        elif eng == "chrome_cli":
            _render_with_chrome_cli(target_uri, out_png, w_px, h_px, eff_scale, transparent, timeout_sec)
        else:
            try:
                _render_with_playwright(target_uri, out_png, w_px, h_px, eff_scale, transparent, timeout_sec)
            except Exception:
                _render_with_chrome_cli(target_uri, out_png, w_px, h_px, eff_scale, transparent, timeout_sec)

        expected = (int(round(w_px * eff_scale)), int(round(h_px * eff_scale)))
        _finalize_png_300dpi(out_png, dpi=eff_dpi, transparent=bool(transparent), expected_size=expected)
        return str(out_png)
    finally:
        if tmp_html is not None:
            with suppress(OSError):
                tmp_html.unlink(missing_ok=True)


# -------------------------------------------------------------------------
# Step 3 Core 5: Native Editable <m:oMath> OMML Equation Injector
# -------------------------------------------------------------------------

_OMML_A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


_OMML_A14_NS = "http://schemas.microsoft.com/office/drawing/2010/main"


_OMML_M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


_OMML_MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"


_XML_SPACE_ATTR = "{http://www.w3.org/XML/1998/namespace}space"

_OMML_ACCENT_CHARS: dict[str, str] = {
    "hat": "\u0302",
    "widehat": "\u0302",
    "bar": "\u0304",
    "tilde": "\u0303",
    "widetilde": "\u0303",
    "vec": "\u20d7",
    "dot": "\u0307",
    "ddot": "\u0308",
}

_OMML_SYMBOLS: dict[str, str] = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "varepsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ", "iota": "ι",
    "kappa": "κ", "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ",
    "pi": "π", "rho": "ρ", "sigma": "σ", "tau": "τ", "upsilon": "υ",
    "phi": "φ", "varphi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
    "times": "×", "cdot": "·", "div": "÷", "pm": "±", "mp": "∓",
    "approx": "≈", "neq": "≠", "ne": "≠", "le": "≤", "leq": "≤",
    "ge": "≥", "geq": "≥", "equiv": "≡", "sim": "∼", "simeq": "≃", "cong": "≅", "propto": "∝",
    "ll": "≪", "gg": "≫", "mid": "∣", "vert": "|", "parallel": "∥", "perp": "⊥",
    "ast": "∗", "star": "⋆", "circ": "∘", "bullet": "•", "therefore": "∴", "because": "∵", "angle": "∠",
    "infty": "∞", "to": "→", "rightarrow": "→", "leftarrow": "←",
    "Rightarrow": "⇒", "Leftarrow": "⇐", "leftrightarrow": "↔", "Leftrightarrow": "⇔",
    "partial": "∂", "nabla": "∇", "forall": "∀", "exists": "∃",
    "in": "∈", "notin": "∉", "subset": "⊂", "subseteq": "⊆",
    "cup": "∪", "cap": "∩", "emptyset": "∅", "dots": "…", "ldots": "…", "cdots": "⋯",
    "quad": "  ", "qquad": "    ", ",": " ", ";": " ", " ": " ", "%": "%", "_": "_",
}

_OMML_UPRIGHT_FUNCS: frozenset[str] = frozenset({
    "max", "min", "log", "ln", "exp", "sin", "cos", "tan", "lim", "arg", "sup", "inf", "round", "Var", "Cov", "Pr",
})

_OMML_NARY_CHARS: dict[str, tuple[str, str]] = {
    "sum": ("∑", "undOvr"),
    "prod": ("∏", "undOvr"),
    "int": ("∫", "subSup"),
}


def _clean_omml_hex(color_hex: str | None) -> str | None:
    """Validate and normalize color_hex into uppercase 6-digit RRGGBB for OOXML `<a:srgbClr>`, else None."""
    if not color_hex:
        return None
    clean_hex = str(color_hex).strip().lstrip("#").upper()
    if len(clean_hex) == 3:
        clean_hex = "".join(c * 2 for c in clean_hex)
    if len(clean_hex) == 6 and re.fullmatch(r"[0-9A-F]{6}", clean_hex):
        return clean_hex
    return None


def _make_omml_run(
    text: str,
    font_pt: float,
    color_hex: str | None,
    font_family: str,
    plain: bool = True,
    style: str | None = None,
):
    """Create a DrawingML-valid `<m:r>` math run with `<a:rPr>` sizing, color, and EA font."""
    from lxml import etree  # type: ignore

    r_el = etree.Element(f"{{{_OMML_M_NS}}}r")
    resolved_sty = style if style is not None else ("p" if plain else None)
    if resolved_sty:
        mrpr = etree.SubElement(r_el, f"{{{_OMML_M_NS}}}rPr")
        sty = etree.SubElement(mrpr, f"{{{_OMML_M_NS}}}sty")
        sty.set(f"{{{_OMML_M_NS}}}val", resolved_sty)

    arpr = etree.SubElement(r_el, f"{{{_OMML_A_NS}}}rPr")
    arpr.set("lang", "en-US")
    arpr.set("sz", str(int(round(float(font_pt) * 100.0))))
    arpr.set("dirty", "0")
    clean_hex = _clean_omml_hex(color_hex)
    if clean_hex:
        sfill = etree.SubElement(arpr, f"{{{_OMML_A_NS}}}solidFill")
        srgb = etree.SubElement(sfill, f"{{{_OMML_A_NS}}}srgbClr")
        srgb.set("val", clean_hex)
    latin = etree.SubElement(arpr, f"{{{_OMML_A_NS}}}latin")
    latin.set("typeface", font_family)
    ea = etree.SubElement(arpr, f"{{{_OMML_A_NS}}}ea")
    ea.set("typeface", FONT_FAMILY)

    t_el = etree.SubElement(r_el, f"{{{_OMML_M_NS}}}t")
    t_el.set(_XML_SPACE_ATTR, "preserve")
    t_el.text = text
    return r_el


def _build_omml_math_element(
    equation_str: str,
    font_pt: float,
    color_hex: str | None,
    font_family: str,
):
    """
    Parse LaTeX-like / Unicode math expression into a native `<m:oMath>` lxml element.
    Supports `\\frac{}{}`, `\\sqrt[n]{}`, `^`, `_`, `\\sum`/`\\prod`/`\\int`,
    `\\left(...\\right)`, `\\text{}`/`\\mathrm{}`/`\\operatorname{}`, Greek letters, and math operators.
    """
    from lxml import etree  # type: ignore

    src = str(equation_str or "").strip()
    if src.startswith("$$") and src.endswith("$$") and len(src) >= 4:
        src = src[2:-2].strip()
    elif src.startswith("$") and src.endswith("$") and len(src) >= 2:
        src = src[1:-1].strip()

    def _parse_slice(s: str) -> list:
        nodes: list = []
        i = 0
        slen = len(s)

        def _s_skip_ws(p: int) -> int:
            while p < slen and s[p] in (" ", "\t", "\r", "\n"):
                p += 1
            return p

        def _s_read_braced(p: int) -> tuple[str, int]:
            p = _s_skip_ws(p)
            if p >= slen:
                return "", p
            if s[p] != "{":
                if s[p] == "\\":
                    j = p + 1
                    while j < slen and s[j].isalpha():
                        j += 1
                    if j == p + 1 and j < slen:
                        j += 1
                    return s[p:j], j
                return s[p], p + 1
            depth = 0
            start = p + 1
            j = p
            while j < slen:
                if s[j] == "\\" and j + 1 < slen:
                    j += 2
                    continue
                if s[j] == "{":
                    depth += 1
                elif s[j] == "}":
                    depth -= 1
                    if depth == 0:
                        return s[start:j], j + 1
                j += 1
            return s[start:], slen

        def _s_read_bracketed(p: int) -> tuple[str | None, int]:
            p = _s_skip_ws(p)
            if p >= slen or s[p] != "[":
                return None, p
            depth = 0
            start = p + 1
            j = p
            while j < slen:
                if s[j] == "[":
                    depth += 1
                elif s[j] == "]":
                    depth -= 1
                    if depth == 0:
                        return s[start:j], j + 1
                j += 1
            return s[start:], slen

        def _s_read_delim(p: int) -> tuple[str, int]:
            p = _s_skip_ws(p)
            if p >= slen:
                return "", p
            if s[p] == "\\":
                if p + 1 < slen and s[p + 1] in ("{", "}", "|"):
                    return s[p + 1], p + 2
                j = p + 1
                while j < slen and s[j].isalpha():
                    j += 1
                cmd = s[p + 1:j]
                return _OMML_SYMBOLS.get(cmd, cmd), j
            ch = s[p]
            return ("" if ch == "." else ch), p + 1

        def _parse_atom(p: int) -> tuple[object | None, int]:
            p = _s_skip_ws(p)
            if p >= slen:
                return None, p

            ch = s[p]
            if ch == "{":
                inner, p_next = _s_read_braced(p)
                box = _parse_slice(inner)
                if len(box) == 1:
                    return box[0], p_next
                # Wrap multi-node group in an invisible delimiter or list marker
                return ("__GROUP__", box), p_next

            if ch == "\\":
                j = p + 1
                while j < slen and s[j].isalpha():
                    j += 1
                if j == p + 1 and j < slen:
                    cmd = s[j]
                    j += 1
                else:
                    cmd = s[p + 1:j]

                if cmd == "frac":
                    num_s, j = _s_read_braced(j)
                    den_s, j = _s_read_braced(j)
                    f_el = etree.Element(f"{{{_OMML_M_NS}}}f")
                    num_el = etree.SubElement(f_el, f"{{{_OMML_M_NS}}}num")
                    for child in _parse_slice(num_s):
                        num_el.append(child)
                    den_el = etree.SubElement(f_el, f"{{{_OMML_M_NS}}}den")
                    for child in _parse_slice(den_s):
                        den_el.append(child)
                    return f_el, j

                if cmd == "sqrt":
                    deg_s, j = _s_read_bracketed(j)
                    rad_s, j = _s_read_braced(j)
                    rad_el = etree.Element(f"{{{_OMML_M_NS}}}rad")
                    rad_pr = etree.SubElement(rad_el, f"{{{_OMML_M_NS}}}radPr")
                    deg_hide = etree.SubElement(rad_pr, f"{{{_OMML_M_NS}}}degHide")
                    deg_hide.set(f"{{{_OMML_M_NS}}}val", "0" if deg_s else "1")
                    deg_el = etree.SubElement(rad_el, f"{{{_OMML_M_NS}}}deg")
                    if deg_s:
                        for child in _parse_slice(deg_s):
                            deg_el.append(child)
                    e_el = etree.SubElement(rad_el, f"{{{_OMML_M_NS}}}e")
                    for child in _parse_slice(rad_s):
                        e_el.append(child)
                    return rad_el, j

                if cmd in ("text", "mathrm", "operatorname", "mathbf"):
                    txt_s, j = _s_read_braced(j)
                    txt_clean = (
                        txt_s.replace(r"\_", "_")
                        .replace(r"\%", "%")
                        .replace(r"\,", " ")
                        .replace(r"\ ", " ")
                    )
                    run_sty = "b" if cmd == "mathbf" else "p"
                    return _make_omml_run(txt_clean, font_pt, color_hex, font_family, plain=True, style=run_sty), j

                if cmd in _OMML_ACCENT_CHARS:
                    acc_s, j = _s_read_braced(j)
                    acc_el = etree.Element(f"{{{_OMML_M_NS}}}acc")
                    acc_pr = etree.SubElement(acc_el, f"{{{_OMML_M_NS}}}accPr")
                    chr_el = etree.SubElement(acc_pr, f"{{{_OMML_M_NS}}}chr")
                    chr_el.set(f"{{{_OMML_M_NS}}}val", _OMML_ACCENT_CHARS[cmd])
                    e_el = etree.SubElement(acc_el, f"{{{_OMML_M_NS}}}e")
                    for child in _parse_slice(acc_s):
                        e_el.append(child)
                    return acc_el, j

                if cmd in ("overline", "underline"):
                    bar_s, j = _s_read_braced(j)
                    bar_el = etree.Element(f"{{{_OMML_M_NS}}}bar")
                    bar_pr = etree.SubElement(bar_el, f"{{{_OMML_M_NS}}}barPr")
                    pos_el = etree.SubElement(bar_pr, f"{{{_OMML_M_NS}}}pos")
                    pos_el.set(f"{{{_OMML_M_NS}}}val", "top" if cmd == "overline" else "bot")
                    e_el = etree.SubElement(bar_el, f"{{{_OMML_M_NS}}}e")
                    for child in _parse_slice(bar_s):
                        e_el.append(child)
                    return bar_el, j

                if cmd == "right":
                    end_chr, j = _s_read_delim(j)
                    return _make_omml_run(end_chr or ")", font_pt, color_hex, font_family, plain=True), j

                if cmd == "left":
                    beg_chr, j = _s_read_delim(j)
                    # Find matching \right at nesting depth 0
                    depth = 1
                    body_start = j
                    k = j
                    end_chr = ""
                    while k < slen:
                        if s.startswith(r"\left", k) and (k + 5 >= slen or not s[k + 5].isalpha()):
                            depth += 1
                            k += 5
                            continue
                        if s.startswith(r"\right", k) and (k + 6 >= slen or not s[k + 6].isalpha()):
                            depth -= 1
                            if depth == 0:
                                body_str = s[body_start:k]
                                end_chr, k = _s_read_delim(k + 6)
                                d_el = etree.Element(f"{{{_OMML_M_NS}}}d")
                                d_pr = etree.SubElement(d_el, f"{{{_OMML_M_NS}}}dPr")
                                beg_el = etree.SubElement(d_pr, f"{{{_OMML_M_NS}}}begChr")
                                beg_el.set(f"{{{_OMML_M_NS}}}val", beg_chr)
                                end_el = etree.SubElement(d_pr, f"{{{_OMML_M_NS}}}endChr")
                                end_el.set(f"{{{_OMML_M_NS}}}val", end_chr)
                                e_el = etree.SubElement(d_el, f"{{{_OMML_M_NS}}}e")
                                for child in _parse_slice(body_str):
                                    e_el.append(child)
                                return d_el, k
                            k += 6
                            continue
                        k += 1
                    # Unmatched \left fallback
                    return _make_omml_run(beg_chr or "(", font_pt, color_hex, font_family, plain=True), j

                if cmd in _OMML_NARY_CHARS:
                    sym_chr, lim_loc = _OMML_NARY_CHARS[cmd]
                    sub_s: str | None = None
                    sup_s: str | None = None
                    while True:
                        j = _s_skip_ws(j)
                        if j < slen and s[j] == "_" and sub_s is None:
                            sub_s, j = _s_read_braced(j + 1)
                        elif j < slen and s[j] == "^" and sup_s is None:
                            sup_s, j = _s_read_braced(j + 1)
                        else:
                            break
                    nary_el = etree.Element(f"{{{_OMML_M_NS}}}nary")
                    nary_pr = etree.SubElement(nary_el, f"{{{_OMML_M_NS}}}naryPr")
                    c_el = etree.SubElement(nary_pr, f"{{{_OMML_M_NS}}}chr")
                    c_el.set(f"{{{_OMML_M_NS}}}val", sym_chr)
                    ll_el = etree.SubElement(nary_pr, f"{{{_OMML_M_NS}}}limLoc")
                    ll_el.set(f"{{{_OMML_M_NS}}}val", lim_loc)
                    sub_h = etree.SubElement(nary_pr, f"{{{_OMML_M_NS}}}subHide")
                    sub_h.set(f"{{{_OMML_M_NS}}}val", "0" if sub_s is not None else "1")
                    sup_h = etree.SubElement(nary_pr, f"{{{_OMML_M_NS}}}supHide")
                    sup_h.set(f"{{{_OMML_M_NS}}}val", "0" if sup_s is not None else "1")
                    sub_el = etree.SubElement(nary_el, f"{{{_OMML_M_NS}}}sub")
                    if sub_s:
                        for child in _parse_slice(sub_s):
                            sub_el.append(child)
                    sup_el = etree.SubElement(nary_el, f"{{{_OMML_M_NS}}}sup")
                    if sup_s:
                        for child in _parse_slice(sup_s):
                            sup_el.append(child)
                    e_el = etree.SubElement(nary_el, f"{{{_OMML_M_NS}}}e")
                    # Attach the following atom (including any attached _ / ^ scripts!) as n-ary operand
                    op_nodes, j_after = _parse_atom_with_scripts(j)
                    if op_nodes:
                        j = j_after
                        for child in op_nodes:
                            e_el.append(child)
                    return nary_el, j

                if cmd in _OMML_UPRIGHT_FUNCS:
                    return _make_omml_run(cmd, font_pt, color_hex, font_family, plain=True), j

                if cmd in _OMML_SYMBOLS:
                    sym = _OMML_SYMBOLS[cmd]
                    is_greek_lower = len(sym) == 1 and ("\u03b1" <= sym <= "\u03c9")
                    return _make_omml_run(sym, font_pt, color_hex, font_family, plain=not is_greek_lower), j

                return _make_omml_run(cmd, font_pt, color_hex, font_family, plain=True), j

            # Numbers (keep contiguous digits/decimal together)
            if ch.isdigit():
                j = p + 1
                while j < slen and (s[j].isdigit() or (s[j] == "." and j + 1 < slen and s[j + 1].isdigit())):
                    j += 1
                return _make_omml_run(s[p:j], font_pt, color_hex, font_family, plain=True), j

            # Single Latin variable (italic math style)
            if ch.isalpha() and ord(ch) < 128:
                return _make_omml_run(ch, font_pt, color_hex, font_family, plain=False), p + 1

            # CJK or operators/punctuation (upright plain style; PowerPoint OMML handles math operator spacing natively)
            return _make_omml_run(ch, font_pt, color_hex, font_family, plain=True), p + 1

        def _parse_atom_with_scripts(p: int) -> tuple[list, int]:
            p = _s_skip_ws(p)
            if p >= slen:
                return [], p
            atom, p = _parse_atom(p)
            if atom is None:
                return [], p

            # Look ahead for `_` / `^` scripts attached to this atom
            sub_str: str | None = None
            sup_str: str | None = None
            while True:
                p_look = _s_skip_ws(p)
                if p_look < slen and s[p_look] == "_" and sub_str is None:
                    sub_str, p = _s_read_braced(p_look + 1)
                elif p_look < slen and s[p_look] == "^" and sup_str is None:
                    sup_str, p = _s_read_braced(p_look + 1)
                else:
                    break

            def _append_atom_children(parent_el, a_obj) -> None:
                if isinstance(a_obj, tuple) and a_obj[0] == "__GROUP__":
                    for ch_el in a_obj[1]:
                        parent_el.append(ch_el)
                else:
                    parent_el.append(a_obj)

            if sub_str is not None and sup_str is not None:
                ss_el = etree.Element(f"{{{_OMML_M_NS}}}sSubSup")
                e_el = etree.SubElement(ss_el, f"{{{_OMML_M_NS}}}e")
                _append_atom_children(e_el, atom)
                sub_el = etree.SubElement(ss_el, f"{{{_OMML_M_NS}}}sub")
                for child in _parse_slice(sub_str):
                    sub_el.append(child)
                sup_el = etree.SubElement(ss_el, f"{{{_OMML_M_NS}}}sup")
                for child in _parse_slice(sup_str):
                    sup_el.append(child)
                return [ss_el], p
            if sub_str is not None:
                sb_el = etree.Element(f"{{{_OMML_M_NS}}}sSub")
                e_el = etree.SubElement(sb_el, f"{{{_OMML_M_NS}}}e")
                _append_atom_children(e_el, atom)
                sub_el = etree.SubElement(sb_el, f"{{{_OMML_M_NS}}}sub")
                for child in _parse_slice(sub_str):
                    sub_el.append(child)
                return [sb_el], p
            if sup_str is not None:
                sp_el = etree.Element(f"{{{_OMML_M_NS}}}sSup")
                e_el = etree.SubElement(sp_el, f"{{{_OMML_M_NS}}}e")
                _append_atom_children(e_el, atom)
                sup_el = etree.SubElement(sp_el, f"{{{_OMML_M_NS}}}sup")
                for child in _parse_slice(sup_str):
                    sup_el.append(child)
                return [sp_el], p
            if isinstance(atom, tuple) and atom[0] == "__GROUP__":
                return list(atom[1]), p
            return [atom], p

        while i < slen:
            i = _s_skip_ws(i)
            if i >= slen:
                break
            parsed_nodes, next_i = _parse_atom_with_scripts(i)
            if not parsed_nodes and next_i == i:
                break
            nodes.extend(parsed_nodes)
            i = next_i

        return nodes

    omath = etree.Element(f"{{{_OMML_M_NS}}}oMath")
    for child in _parse_slice(src):
        omath.append(child)
    return omath


def insert_omml_equation(
    text_frame,
    equation_str: str,
    font_pt: float | None = None,
    color_hex: str | None = None,
    align: str = "center",
    font_family: str = "Cambria Math",
    append_paragraph: bool | None = None,
) -> None:
    """
    Inject a native editable PowerPoint OMML equation wrapped in OOXML-compliant
    `<mc:AlternateContent><mc:Choice Requires="a14"><a14:m><m:oMathPara><m:oMath>...`
    with an `<mc:Fallback><a:r>` plain-text run for non-a14 viewers (LibreOffice / legacy Office)
    and automatic plain-text fallback on failure.
    """
    raw = str(equation_str or "").strip()
    if not raw:
        return

    if font_pt is not None:
        raw_pt = float(font_pt)
        if not math.isfinite(raw_pt):
            raise ValueError(f"font_pt must be a finite number; got {font_pt!r}.")
        resolved_pt = max(MIN_CONTENT_FONT_PT, raw_pt)
    else:
        resolved_pt = 18.0
    resolved_color = color_hex or "#0F172A"
    clean_hex = _clean_omml_hex(resolved_color) or "0F172A"
    align_norm = str(align or "center").strip().lower()
    pp_align_map = {
        "left": PP_ALIGN.LEFT,
        "center": PP_ALIGN.CENTER,
        "right": PP_ALIGN.RIGHT,
    }
    jc_map = {"left": "left", "center": "center", "right": "right"}

    first_p = text_frame.paragraphs[0]
    first_has_content = (
        bool(first_p.text.strip())
        or (first_p._p.find(f".//{{{_OMML_A14_NS}}}m") is not None)
    )
    if append_paragraph is True or (append_paragraph is None and first_has_content):
        paragraph = text_frame.add_paragraph()
    else:
        paragraph = first_p
        paragraph.text = ""

    paragraph.alignment = pp_align_map.get(align_norm, PP_ALIGN.CENTER)

    try:
        from lxml import etree  # type: ignore

        omath_el = _build_omml_math_element(raw, resolved_pt, clean_hex, font_family)
        alt_content = etree.Element(
            f"{{{_OMML_MC_NS}}}AlternateContent",
            nsmap={"mc": _OMML_MC_NS},
        )
        choice = etree.SubElement(
            alt_content,
            f"{{{_OMML_MC_NS}}}Choice",
            nsmap={"a14": _OMML_A14_NS},
        )
        choice.set("Requires", "a14")
        a14_m = etree.SubElement(
            choice,
            f"{{{_OMML_A14_NS}}}m",
            nsmap={"a14": _OMML_A14_NS, "m": _OMML_M_NS},
        )
        omath_para = etree.SubElement(a14_m, f"{{{_OMML_M_NS}}}oMathPara")
        omath_para_pr = etree.SubElement(omath_para, f"{{{_OMML_M_NS}}}oMathParaPr")
        jc_el = etree.SubElement(omath_para_pr, f"{{{_OMML_M_NS}}}jc")
        jc_el.set(f"{{{_OMML_M_NS}}}val", jc_map.get(align_norm, "center"))
        omath_para.append(omath_el)

        # Standard OOXML <mc:Fallback> plain-text run for LibreOffice / Office 2007 compatibility
        fallback_el = etree.SubElement(alt_content, f"{{{_OMML_MC_NS}}}Fallback")
        fb_r = etree.SubElement(fallback_el, f"{{{_OMML_A_NS}}}r")
        fb_rpr = etree.SubElement(fb_r, f"{{{_OMML_A_NS}}}rPr")
        fb_rpr.set("lang", "en-US")
        fb_rpr.set("sz", str(int(round(resolved_pt * 100.0))))
        fb_rpr.set("dirty", "0")
        fb_sfill = etree.SubElement(fb_rpr, f"{{{_OMML_A_NS}}}solidFill")
        fb_srgb = etree.SubElement(fb_sfill, f"{{{_OMML_A_NS}}}srgbClr")
        fb_srgb.set("val", clean_hex)
        fb_latin = etree.SubElement(fb_rpr, f"{{{_OMML_A_NS}}}latin")
        fb_latin.set("typeface", font_family)
        fb_ea = etree.SubElement(fb_rpr, f"{{{_OMML_A_NS}}}ea")
        fb_ea.set("typeface", FONT_FAMILY)
        fb_t = etree.SubElement(fb_r, f"{{{_OMML_A_NS}}}t")
        fb_t.text = raw.replace("$$", "").replace("$", "")

        p_el = paragraph._p
        end_rpr = p_el.find(f"{{{_OMML_A_NS}}}endParaRPr")
        if end_rpr is not None:
            p_el.insert(list(p_el).index(end_rpr), alt_content)
        else:
            p_el.append(alt_content)
    except Exception:
        # Plain-text graceful fallback: never break slide generation
        fallback = raw.replace("$$", "").replace("$", "")
        _populate_paragraph_runs(paragraph, fallback, resolved_pt, f"#{clean_hex}", bold=True)
