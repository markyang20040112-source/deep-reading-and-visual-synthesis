"""
pdf_report_engine.py
A4 Dual-Modal Print CSS & Playwright PDF Compiler Engine for Format B (.md / .pdf).
Grounded in Paivio (1986) Dual-Coding Cadence, Sweller (2011) Cognitive Load, Tufte (2006) Ehrenberg Three-Line Tables,
W3C CSS Fragmentation Level 3, and W3C CLReq Traditional Chinese Layout Requirements.

Provides reusable building blocks:
- build_report_css(theme="modern_sans", body_pt=10.8) -> str
- wrap_report_html(title, body_html, theme="modern_sans", body_pt=10.8, extra_css="") -> str
- compile_html_to_pdf(html_content_or_path, output_pdf_path, cleanup_temp_html=True) -> str
"""

import os
import tempfile
from pathlib import Path
from typing import Optional


def build_report_css(theme: str = "modern_sans", body_pt: float = 10.8) -> str:
    """
    Generate publication-grade A4 print CSS with:
    - 189mm expansive printable width (@page margin: 11mm 10.5mm 12mm 10.5mm)
    - Dedicated A4 Landscape page rule (@page landscape-fig + .landscape-page) for 28"x18.5" or 24"x14" wide figures
    - Theme support:
      * "modern_sans": Microsoft JhengHei / PingFang TC / Noto Sans CJK TC, clean unindented paragraphs
      * "clreq_kaiti": DFKai-SB (標楷體) + Times New Roman, with `p { text-indent: 2em; }` for narrative paragraphs
    - Chapter-boundary page breaks (`h2.chapter-start`, `.page-break`)
    - Anti-clipping & border-safe flex/grid cards (`break-inside: avoid`, no fixed height, no `overflow: hidden`)
    - Ehrenberg three-line tables & formula sandwich boxes (`.equation-box`)
    """
    is_kaiti = str(theme).strip().lower() in {"clreq_kaiti", "kaiti", "dfkai", "academic_kaiti"}
    if is_kaiti:
        font_stack = '"DFKai-SB", "標楷體", "BiauKai", "Times New Roman", serif'
        p_indent_rule = "text-indent: 2em;"
    else:
        font_stack = '"Microsoft JhengHei", "PingFang TC", "Noto Sans CJK TC", -apple-system, sans-serif'
        p_indent_rule = "text-indent: 0;"

    pt_val = max(9.2, min(11.5, float(body_pt)))

    return f"""
@page {{
  size: A4 portrait;
  margin: 11mm 10.5mm 12mm 10.5mm;
}}

@page landscape-fig {{
  size: A4 landscape;
  margin: 8mm 10mm 8mm 10mm;
}}

* {{
  box-sizing: border-box;
  -webkit-print-color-adjust: exact !important;
  print-color-adjust: exact !important;
}}

html, body {{
  margin: 0;
  padding: 0;
  font-family: {font_stack};
  font-size: {pt_val}pt;
  line-height: 1.68;
  color: #1E293B;
  background-color: #FFFFFF;
}}

h1 {{
  font-size: 21pt;
  font-weight: 800;
  color: #0F172A;
  line-height: 1.3;
  margin: 0 0 8px 0;
}}

h2 {{
  font-size: 14.5pt;
  font-weight: 700;
  color: #0F172A;
  border-bottom: 2px solid #0284C7;
  padding-bottom: 4px;
  margin: 16px 0 10px 0;
  break-after: avoid;
  page-break-after: avoid;
}}

h2.chapter-start, .page-break {{
  break-before: page;
  page-break-before: always;
}}

h3 {{
  font-size: 12pt;
  font-weight: 700;
  color: #0F172A;
  margin: 12px 0 6px 0;
  break-after: avoid;
  page-break-after: avoid;
}}

p {{
  margin: 0 0 8px 0;
  text-align: justify;
  {p_indent_rule}
}}

/* Unindented paragraphs inside structured containers */
td p, th p, .card p, .card-body p, .callout p, .equation-box p, figcaption, .no-indent {{
  text-indent: 0 !important;
}}

.nowrap {{
  white-space: nowrap;
}}

/* Border-Safe Flex / Grid Cards (Zero fixed height, zero overflow:hidden) */
.card-grid-2 {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin: 10px 0;
  align-items: stretch;
}}

.card-grid-3 {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 9px;
  margin: 10px 0;
  align-items: stretch;
}}

.card, .matrix-box, .callout, .equation-box, figure, tr {{
  break-inside: avoid;
  page-break-inside: avoid;
}}

.card {{
  border: 1.5px solid #CBD5E1;
  border-radius: 8px;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
}}

.card-header {{
  padding: 6px 10px;
  font-size: 10.5pt;
  font-weight: 700;
  color: #0F172A;
  background: #F1F5F9;
  border-bottom: 1px solid #CBD5E1;
  border-radius: 6px 6px 0 0;
}}

.card-body {{
  padding: 8px 10px;
  font-size: 9.8pt;
  line-height: 1.54;
  color: #1E293B;
}}

.badge {{
  display: inline-block;
  padding: 1px 7px;
  font-size: 9pt;
  font-weight: 700;
  border-radius: 999px;
  background: #E0F2FE;
  color: #0284C7;
  white-space: nowrap;
}}

/* Ehrenberg Three-Line Table */
table {{
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0 12px 0;
  font-size: 9.6pt;
  line-height: 1.5;
}}

thead tr {{
  border-top: 2px solid #0F172A;
  border-bottom: 1.5px solid #0F172A;
  background: #F8FAFC;
}}

tbody tr {{
  border-bottom: 1px solid #E2E8F0;
}}

tbody tr:last-child {{
  border-bottom: 2px solid #0F172A;
}}

th, td {{
  padding: 6px 8px;
  text-align: left;
  vertical-align: top;
}}

th {{
  font-weight: 700;
  color: #0F172A;
}}

/* Display Equation Box (Formula Sandwich) */
.equation-box {{
  margin: 10px 0;
  padding: 9px 14px;
  background: #F8FAFC;
  border-left: 4px solid #0284C7;
  border-top: 1px solid #E2E8F0;
  border-right: 1px solid #E2E8F0;
  border-bottom: 1px solid #E2E8F0;
  border-radius: 0 6px 6px 0;
}}

.equation-formula {{
  text-align: center;
  font-weight: 700;
  font-size: 11pt;
  color: #0F172A;
  margin-bottom: 5px;
}}

/* Figures & Dedicated A4 Landscape Page for Wide Diagrams */
figure {{
  margin: 10px 0 12px 0;
  text-align: center;
}}

figure img {{
  max-width: 100%;
  height: auto;
  border: 1px solid #E2E8F0;
  border-radius: 6px;
}}

figcaption {{
  margin-top: 5px;
  font-size: 9.2pt;
  color: #475569;
  line-height: 1.45;
  text-align: left;
}}

.landscape-page {{
  page: landscape-fig;
  break-before: page;
  page-break-before: always;
  break-after: page;
  page-break-after: always;
  width: 100%;
}}

.landscape-page figure img {{
  max-height: 162mm;
  width: auto;
  max-width: 100%;
}}
""".strip()


def wrap_report_html(
    title: str,
    body_html: str,
    theme: str = "modern_sans",
    body_pt: float = 10.8,
    extra_css: str = "",
) -> str:
    """Wrap report HTML body with standardized DOCTYPE, UTF-8 meta, and A4 print CSS."""
    base_css = build_report_css(theme=theme, body_pt=body_pt)
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
{base_css}
{extra_css}
  </style>
</head>
<body>
{body_html}
</body>
</html>
"""


def _find_chromium_binary() -> Optional[str]:
    """Locate a local Chrome or Edge binary for headless PDF printing."""
    import shutil

    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("msedge"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def compile_html_to_pdf(
    html_content_or_path: str,
    output_pdf_path: str,
    cleanup_temp_html: bool = True,
    wait_ms: int = 400,
) -> str:
    """
    Compile an HTML string or existing .html file path to an A4 print-grade PDF via Playwright Chromium
    or local headless Chrome/Edge CLI.
    Automatically removes temporary .html files when `cleanup_temp_html=True` so `02_outputs/` stays clean.
    """
    import shutil
    import subprocess

    out_pdf = Path(output_pdf_path).resolve()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    potential_path = Path(html_content_or_path) if "\n" not in html_content_or_path and len(html_content_or_path) < 260 else None
    created_temp = False

    if potential_path is not None and potential_path.exists() and potential_path.is_file():
        html_file = potential_path.resolve()
    else:
        fd, temp_name = tempfile.mkstemp(suffix=".html", prefix="_tmp_report_", dir=str(out_pdf.parent))
        os.close(fd)
        html_file = Path(temp_name).resolve()
        html_file.write_text(html_content_or_path, encoding="utf-8")
        created_temp = True

    try:
        compiled = False
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(html_file.as_uri(), wait_until="networkidle")
                if wait_ms > 0:
                    page.wait_for_timeout(wait_ms)
                page.pdf(
                    path=str(out_pdf),
                    print_background=True,
                    prefer_css_page_size=True,
                )
                browser.close()
                compiled = out_pdf.exists() and out_pdf.stat().st_size > 500
        except Exception:
            compiled = False

        if not compiled:
            browser_bin = _find_chromium_binary()
            if not browser_bin:
                raise RuntimeError(
                    "Neither Playwright nor a local Chrome/Edge binary was found to compile HTML to PDF."
                )
            temp_profile = tempfile.mkdtemp(prefix="chrome_pdf_")
            temp_pdf = os.path.join(temp_profile, "output.pdf")
            try:
                args = [
                    browser_bin,
                    "--headless=new",
                    "--disable-gpu",
                    f"--user-data-dir={temp_profile}",
                    f"--print-to-pdf={temp_pdf}",
                    "--no-pdf-header-footer",
                    str(html_file),
                ]
                subprocess.run(
                    args,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=60,
                    check=False,
                )
                if not (os.path.exists(temp_pdf) and os.path.getsize(temp_pdf) > 500) and os.name == "nt":
                    env = os.environ.copy()
                    env["PDF_BROWSER_BIN"] = str(browser_bin)
                    env["PDF_TEMP_PROFILE"] = str(temp_profile)
                    env["PDF_TEMP_OUT"] = str(temp_pdf)
                    env["PDF_HTML_FILE"] = str(html_file)
                    ps_cmd = [
                        "powershell",
                        "-NoProfile",
                        "-Command",
                        (
                            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
                            '$argList = @("--headless=new", "--disable-gpu", '
                            '"--user-data-dir=$env:PDF_TEMP_PROFILE", '
                            '"--print-to-pdf=$env:PDF_TEMP_OUT", '
                            '"--no-pdf-header-footer", "$env:PDF_HTML_FILE"); '
                            'Start-Process -FilePath $env:PDF_BROWSER_BIN -ArgumentList $argList -Wait'
                        ),
                    ]
                    subprocess.run(
                        ps_cmd,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        env=env,
                        timeout=60,
                        check=False,
                    )

                if os.path.exists(temp_pdf) and os.path.getsize(temp_pdf) > 500:
                    shutil.copyfile(temp_pdf, str(out_pdf))
                else:
                    raise RuntimeError(f"Headless browser failed to produce PDF from {html_file}")
            finally:
                shutil.rmtree(temp_profile, ignore_errors=True)
    finally:
        fname_lower = html_file.name.lower()
        is_temp_file = (
            created_temp
            or fname_lower.startswith(("_tmp_", "temp_", "tmp_"))
            or fname_lower.endswith(".tmp.html")
        )
        if cleanup_temp_html and is_temp_file and html_file.exists():
            try:
                html_file.unlink(missing_ok=True)
            except OSError:
                pass

    return str(out_pdf)


