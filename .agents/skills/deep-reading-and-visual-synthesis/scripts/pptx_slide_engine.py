"""
pptx_slide_engine.py
Native Vector 16:9 Presentation Slide Engine for Format C (.pptx — Path B Upgraded Viewing-Distance Adaptive Engine).
Grounded in ANSI/AVIXA V202.01 (DISCAS), Alley & Neeley (2005) Assertion-Evidence Headlines,
Tullis (1983, 1997) Local Density & Breathing Room, Knaflic (2015) 80/20 Preattentive Spotlight,
Kosslyn (2007) Compatibility Principle, Mackworth (1948) Anti-Habituation Alternation,
and Kahneman (1993) Peak-End Bookends.

Core Engineering Guarantees (Phase 2 Step 3, Step 4 & Step 5):
1. DISCAS Viewing-Distance Floor & Unified Token Factory (F3): Enforces `target_body_pt >= min_font_pt >= 12.0pt`
   with capped converging typography scale (`resolve_typography_scale`) across all layouts.
2. Pillow Real Text Width + CJK Kinsoku Line Wrapper (F5): Uses `msjh.ttc`/`msjhbd.ttc` (`index=0`) advance width
   measurements, inverted geometry-first autofit (`autofit_box_geometry_first`), and Content-Driven TOP-aligned flow.
3. De-Boxed Typography & Five Layout Families (13 Refined Layouts: 1 Bookend + 12 Content & Impact):
   - F1 Bookend & Impact: `F1-A` (`add_bookend_slide_s0`), `F1-B` (`draw_section_divider_slide`), `F1-C` (`draw_hero_stat_slide`)
   - F2 Structured Narrative: `F2-A` (`draw_parallel_row_cards`), `F2-B` (`draw_editorial_split_rows_s8`), `F2-C` (`draw_bento_grid_slide`)
   - F3 Flow & Mechanism: `F3-A` (`draw_process_steps_s3`), `F3-B` (`draw_clean_mechanism_s4`)
   - F4 Comparison & Matrix: `F4-A` (`draw_quadrant_matrix_s5`), `F4-B` (`draw_comparison_table_slide`)
   - F5 Evidence & Anatomy: `F5-A` (`draw_visual_callout_slide`), `F5-B` (`draw_kpi_strip_slide`), `F5-C` (`draw_focal_anatomy_s6` + OMML)
4. Mode 3 Tier 1 Native Geometric Accents (`draw_theme_geometric_accent`) & Tier 3 300 DPI Renderer (`render_svg_to_png_300dpi`).
5. Two-Stage Semantic Routing (`recommend_layout_family`) & Anti-Collision Validator (`validate_layout_sequence`) with 100% legacy compatibility.
6. Spec-Driven Deterministic Pipeline (F4): Standard 4-zone `02c_slide_spec_lock.json` schema, human-readable Step 4A preview
   (`export_step4a_alignment_preview`), strict read-only `copy` deterministic renderer (`render_deck_from_spec`),
   and bidirectional text + key numeric fidelity checker (`check_copy_fidelity`).
"""

import copy
import functools
import json
import math
import os
import re
import shutil
import struct
import subprocess
import tempfile
import unicodedata
from collections import Counter
from collections.abc import Sequence
from contextlib import suppress
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

FONT_FAMILY = "Microsoft JhengHei"
MIN_CONTENT_FONT_PT = 12.0
WINDOWS_MSJH_REGULAR = Path(r"C:\Windows\Fonts\msjh.ttc")
WINDOWS_MSJH_BOLD = Path(r"C:\Windows\Fonts\msjhbd.ttc")
MSJH_LINE_HEIGHT_EM = 1.3333  # Natural (ascent+descent)/em of Microsoft JhengHei (384/288)
DEFAULT_TEXT_WIDTH_SAFETY = 1.01  # Empirically calibrated against Windows PowerPoint COM (39-case suite, 0 under-predictions)
KINSOKU_NO_START = frozenset("，。、；：！？）》」』】〉〕〗〞’”）％‰…—～·.,;:!?)]}%")
KINSOKU_HANGING_PUNCT = frozenset("，。、；：！？.,;:!?")
KINSOKU_NO_END = frozenset("（《「『【〈〔〖〝‘“([{¥$£€±")
ORPHAN_IGNORED_CHARS = frozenset("，。、；：！？）》」』】〉〕〗〞’”（）《「『【〈〔〖〝‘“.,;:!?()[]{}—…～·- \t\r\n")
_LATIN_TOKEN_RE = re.compile(r"(?:[+±](?=\d))?[A-Za-z0-9]+(?:['’][A-Za-z]+|,[0-9]+|[._:][A-Za-z0-9]+|[+%‰]+)*[-/]?")
MAX_CHROME_CLI_DIM_PX = 8192


def load_document_theme(doc_theme_id: str | None = None) -> dict[str, str]:
    """Load the active document_theme from config/user_preferences.json (with safe defaults)."""
    default_theme = {
        "bg_canvas": "#F8FAFC",
        "bg_card": "#FFFFFF",
        "border_card": "#CBD5E1",
        "ink_primary": "#0F172A",
        "ink_secondary": "#1E293B",
        "ink_muted": "#475569",
        "primary_accent": "#0284C7",
        "primary_tint": "#E0F2FE",
        "warn_accent": "#D97706",
        "warn_tint": "#FEF3C7",
        "success_accent": "#0D9488",
        "success_tint": "#CCFBF1",
        "danger_accent": "#E11D48",
        "danger_tint": "#FFE4E6",
        "synth_accent": "#7C3AED",
        "synth_tint": "#EDE9FE",
        "bookend_dark_bg": "#0F172A",
        "bookend_accent": "#38BDF8",
    }
    with suppress(OSError, ValueError, KeyError, TypeError):
        prefs_file = Path(__file__).resolve().parents[1] / "config" / "user_preferences.json"
        if prefs_file.exists():
            prefs = json.loads(prefs_file.read_text(encoding="utf-8"))
            color_sets = prefs.get("color_sets", {})
            themes = color_sets.get("document_themes", {})
            chosen_id = doc_theme_id or color_sets.get("active_document_theme_id") or "modern_academic_slate"
            if chosen_id in themes:
                merged = dict(default_theme)
                merged.update(themes[chosen_id])
                return merged
    return default_theme


def hex_to_rgb_color(hex_str: str) -> RGBColor:
    """Convert '#RRGGBB' hex string to python-pptx RGBColor."""
    clean = str(hex_str or "#0F172A").strip().lstrip("#")
    if len(clean) == 3:
        clean = "".join(c * 2 for c in clean)
    if len(clean) != 6:
        clean = "0F172A"
    return RGBColor(int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16))


def _add_flat_shape(slide, shape_type, left, top, width, height):
    """Add an AutoShape with PowerPoint's default master drop-shadow disabled for crisp vector rendering."""
    shp = slide.shapes.add_shape(shape_type, left, top, width, height)
    with suppress(AttributeError, TypeError, ValueError):
        shp.shadow.inherit = False
    return shp


def _populate_paragraph_runs(
    paragraph,
    text: str,
    font_pt: float,
    color_hex: str,
    bold: bool = False,
    bold_color_hex: str | None = None,
    font_family: str = FONT_FAMILY,
) -> None:
    """
    Populate a python-pptx paragraph supporting inline `**bold**` segments cleanly
    (never leaving raw `**` asterisks on screen), activating PowerPoint East Asian Kinsoku Shori
    (`eaLnBrk="1"`, `hangingPunct="1"` so `。` / `，` never orphan onto a new line),
    and explicitly stamping font_family and font_pt on every run.
    """
    raw = str(text or "").strip()
    paragraph.text = ""
    if not raw:
        return

    from pptx.oxml.ns import qn

    def _stamp_ea_font_and_lang(r_obj) -> None:
        with suppress(AttributeError, TypeError, ValueError):
            r_pr = r_obj._r.get_or_add_rPr()
            r_pr.set("lang", "zh-TW")
            r_pr.set("altLang", "en-US")
            ea_el = r_pr.find(qn("a:ea"))
            if ea_el is None:
                ea_el = r_pr.makeelement(qn("a:ea"), {})
                r_pr.append(ea_el)
            ea_el.set("typeface", font_family)

    base_rgb = hex_to_rgb_color(color_hex)
    emph_rgb = hex_to_rgb_color(bold_color_hex) if bold_color_hex else base_rgb
    tokens = re.split(r"(\*\*(?:(?!\*\*).)+\*\*)", raw)
    wrote_any = False
    for tok in tokens:
        if not tok:
            continue
        is_emph = tok.startswith("**") and tok.endswith("**") and len(tok) >= 5
        clean_tok = tok[2:-2] if is_emph else tok
        if not clean_tok:
            continue
        run = paragraph.add_run()
        run.text = clean_tok
        run.font.name = font_family
        run.font.size = Pt(float(font_pt))
        run.font.bold = True if is_emph else bool(bold)
        run.font.color.rgb = emph_rgb if is_emph else base_rgb
        _stamp_ea_font_and_lang(run)
        wrote_any = True

    if not wrote_any:
        run = paragraph.add_run()
        run.text = raw
        run.font.name = font_family
        run.font.size = Pt(float(font_pt))
        run.font.bold = bool(bold)
        run.font.color.rgb = base_rgb
        _stamp_ea_font_and_lang(run)

    with suppress(AttributeError, TypeError, ValueError):
        p_pr = paragraph._p.get_or_add_pPr()
        p_pr.set("eaLnBrk", "1")
        p_pr.set("hangingPunct", "1")
        p_pr.set("latinLnBrk", "0")


def _read_image_pixel_size(image_path: Path) -> tuple[int, int]:
    """Read image (width_px, height_px) via Pillow or lightweight PNG/JPEG header fallback."""
    with suppress(ImportError, OSError, ValueError, TypeError):
        from PIL import Image  # type: ignore

        with Image.open(image_path) as im:
            w, h = im.size
            if w > 0 and h > 0:
                return int(w), int(h)

    with suppress(OSError, struct.error, ValueError), image_path.open("rb") as f:
        head = f.read(32)
        if len(head) >= 24 and head[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", head[16:24])
            if w > 0 and h > 0:
                return int(w), int(h)

    return (1920, 1080)


def calc_pill_width(text: str, font_pt: float = 9.5, pad_in: float = 0.24) -> float:
    """
    Calculate exact text-hugging pill width in inches for Microsoft JhengHei using
    Pillow `msjhbd.ttc` (`index=0`) advance width via `measure_text_layout()`.
    """
    raw = str(text or "").strip()
    if not raw:
        return round(max(0.85, float(pad_in)), 3)
    m = measure_text_layout(raw, box_width_in=24.0, font_pt=float(font_pt), bold=True, line_spacing=1.15)
    w = float(m["max_line_width_in"]) + float(pad_in)
    return round(max(0.85, w), 3)


def _est_wrapped_lines(text: str, usable_w_in: float, font_pt: float, bold: bool = False) -> int:
    """Measure exact wrapped line count via Pillow + CJK Kinsoku `measure_text_layout()`."""
    clean = str(text or "").strip()
    if not clean:
        return 1
    m = measure_text_layout(clean, box_width_in=max(0.35, float(usable_w_in)), font_pt=max(6.0, float(font_pt)), bold=bold)
    return max(1, int(m["line_count"]))


# -------------------------------------------------------------------------
# Step 3 Core 1: DISCAS Viewing-Distance Floor & Unified Token Factory (F3)
# -------------------------------------------------------------------------

def _round_half_pt(val: float) -> float:
    """Round a point size cleanly to the nearest 0.5 pt."""
    return round(float(val) * 2.0) / 2.0


def calc_min_font_pt_from_distance(distance_m: float, screen_height_m: float) -> float:
    """
    ANSI/AVIXA V202.01 (DISCAS) viewing-distance minimum body font floor for 16:9 CJK slides:
        min_font_pt = max(12.0, round(3.18 * (distance_m / screen_height_m)))
    Raises ValueError if `distance_m <= 0` or `screen_height_m <= 0`.
    """
    d = float(distance_m)
    h = float(screen_height_m)
    if not math.isfinite(d) or not math.isfinite(h) or d <= 0.0 or h <= 0.0:
        raise ValueError(
            f"distance_m ({distance_m}) and screen_height_m ({screen_height_m}) must be positive finite numbers."
        )
    raw_pt = round(3.18 * (d / h))
    return float(max(MIN_CONTENT_FONT_PT, float(raw_pt)))


def resolve_typography_scale(target_body_pt: float) -> dict[str, float]:
    """
    Capped converging typography scale derived from `target_body_pt`:
    - Protects Zone 1 assertion headlines from exceeding 2 lines at high body sizes while
      strictly preserving Bold headline >= 1.35x body across the full spectrum:
        * 12.0pt -> headline 20.0pt (1.67x)
        * 13.0pt -> headline 21.0pt (1.62x)
        * 15.0pt -> headline 24.0pt (1.60x)
        * 16.0pt -> headline 25.0pt (1.56x)
        * 18.0pt -> headline 26.5pt (1.47x)
        * 20.0pt -> headline 27.5pt (1.38x)
        * >20pt  -> max(27.5pt, ceil_half(body * 1.35))
    - Aligns container title (`+3.0pt`), lead (`+1.5pt`), and callout hierarchy (`1.30x / 1.15x / 1.0x`).
    """
    raw_body = float(target_body_pt)
    if not math.isfinite(raw_body):
        raise ValueError(f"target_body_pt must be a finite number; got {target_body_pt!r}.")
    body = _round_half_pt(max(MIN_CONTENT_FONT_PT, raw_body))

    # Piecewise linear anchor points (body_pt, headline_pt) matching presentation_slide_spec.md
    anchors: list[tuple[float, float]] = [
        (12.0, 20.0),
        (13.0, 21.0),
        (14.0, 22.5),
        (15.0, 24.0),
        (16.0, 25.0),
        (18.0, 26.5),
        (20.0, 27.5),
    ]
    if body <= anchors[0][0]:
        head_raw = anchors[0][1]
    elif body > anchors[-1][0]:
        head_raw = max(anchors[-1][1], body * 1.35)
    else:
        head_raw = anchors[-1][1]
        for (b0, h0), (b1, h1) in zip(anchors, anchors[1:]):
            if b0 <= body <= b1:
                t = (body - b0) / (b1 - b0)
                head_raw = h0 + t * (h1 - h0)
                break

    min_headline_pt = math.ceil((body * 1.35) * 2.0 - 1e-9) / 2.0
    headline = max(min_headline_pt, _round_half_pt(head_raw))
    card_title = _round_half_pt(body + 3.0)
    lead = _round_half_pt(body + 1.5)
    subtitle = _round_half_pt(max(MIN_CONTENT_FONT_PT, body - 0.5 if body >= 13.5 else body))
    caption = _round_half_pt(max(MIN_CONTENT_FONT_PT, body - 1.0))
    kicker = _round_half_pt(max(10.0, min(16.0, body * 0.78)))
    callout_heading = _round_half_pt(body * 1.30)
    callout_lead = _round_half_pt(body * 1.15)
    hero_stat = _round_half_pt(min(76.0, max(44.0, body * 3.6)))
    bookend_title = _round_half_pt(max(28.0, headline * 1.32))

    return {
        "headline": headline,
        "subtitle": subtitle,
        "card_title": card_title,
        "lead": lead,
        "body": body,
        "caption": caption,
        "kicker": kicker,
        "callout_heading": callout_heading,
        "callout_lead": callout_lead,
        "hero_stat": hero_stat,
        "bookend_title": bookend_title,
        "pill": 9.5,
        "headline_ratio": round(headline / body, 3),
    }


def build_slide_design_tokens(
    min_font_pt: float = MIN_CONTENT_FONT_PT,
    target_body_pt: float | None = None,
    doc_theme_id: str | None = None,
    theme_overrides: dict[str, str] | None = None,
    distance_m: float | None = None,
    screen_height_m: float | None = None,
    topic_or_hex: object = None,
    theme_mode: str = "light_classroom",
) -> dict[str, object]:
    """
    Unified Format C Slide Design Token Factory (F3):
    - Enforces 'Floor != Baseline' (`target_body_pt >= min_font_pt >= 12.0pt`).
    - Optionally computes DISCAS `min_font_pt` from `(distance_m, screen_height_m)`.
    - Resolves active `document_theme` (static preset or CIELAB `derive_slide_theme_from_topic()`
      when `topic_or_hex` is supplied) plus any `theme_overrides`.
    - Centralizes capped typography scale, spacing constants, and high-font guardrails.
    """
    raw_min = float(min_font_pt)
    if not math.isfinite(raw_min):
        raise ValueError(f"min_font_pt must be a finite number; got {min_font_pt!r}.")
    resolved_min = max(MIN_CONTENT_FONT_PT, raw_min)
    if (distance_m is None) != (screen_height_m is None):
        raise ValueError("Both distance_m and screen_height_m must be provided together.")
    if distance_m is not None and screen_height_m is not None:
        resolved_min = max(resolved_min, calc_min_font_pt_from_distance(distance_m, screen_height_m))

    if target_body_pt is None:
        if resolved_min <= 12.0:
            resolved_body = 13.0
        elif resolved_min <= 14.0:
            resolved_body = max(resolved_min, 15.0)
        elif resolved_min <= 16.0:
            resolved_body = max(resolved_min, 16.0)
        elif resolved_min <= 18.0:
            resolved_body = max(resolved_min, 18.0)
        else:
            resolved_body = resolved_min
    else:
        raw_target = float(target_body_pt)
        if not math.isfinite(raw_target):
            raise ValueError(f"target_body_pt must be a finite number; got {target_body_pt!r}.")
        resolved_body = max(resolved_min, raw_target)

    # Ensure half-point quantized body never rounds below resolved_min
    if _round_half_pt(resolved_body) < resolved_min - 1e-9:
        resolved_body = math.ceil(resolved_min * 2.0 - 1e-9) / 2.0

    typography = resolve_typography_scale(resolved_body)
    resolved_body = typography["body"]
    typography["subtitle"] = max(resolved_min, typography["subtitle"])
    typography["caption"] = max(resolved_min, typography["caption"])

    if topic_or_hex:
        import sys
        scripts_dir = str(Path(__file__).resolve().parent)
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from hcl_color_engine import derive_slide_theme_from_topic  # type: ignore

        theme = dict(derive_slide_theme_from_topic(topic_or_hex, mode=theme_mode))
    else:
        theme = dict(load_document_theme(doc_theme_id))

    if theme_overrides:
        for k, v in theme_overrides.items():
            if v is not None:
                theme[str(k)] = str(v)

    if resolved_body <= 13.5:
        discas_tier = "reading"
    elif resolved_body <= 15.5:
        discas_tier = "meeting"
    elif resolved_body <= 18.5:
        discas_tier = "classroom"
    else:
        discas_tier = "auditorium"

    return {
        "min_font_pt": resolved_min,
        "target_body_pt": resolved_body,
        "doc_theme_id": doc_theme_id,
        "typography": typography,
        "theme": theme,
        "spacing": {
            "canvas_w_in": 13.333,
            "canvas_h_in": 7.5,
            "margin_x_in": 0.50,
            "zone1_top_in": 0.15,
            "item_gap_in": 0.26,
            "col_gap_in": 0.28,
            "card_pad_x_in": 0.20,
            "card_pad_y_in": 0.16,
            "line_spacing": 1.30,
            "headline_line_spacing": 1.18,
        },
        "constraints": {
            "discas_tier": discas_tier,
            "forbid_4_col_cards": resolved_body >= 16.0,
            "prefer_borderless": resolved_body >= 15.0,
            "max_boxed_ratio": 0.40,
            "max_family_ratio": 0.40,
            "max_orphan_cjk_chars": 2,
        },
    }


# -------------------------------------------------------------------------
# Step 3 Core 2: Pillow Real Text Width + CJK Kinsoku Line Wrapper (F5)
# -------------------------------------------------------------------------

@functools.lru_cache(maxsize=64)
def _load_msjh_font(size_px: int, bold: bool = False):
    """Load Windows Microsoft JhengHei (`msjh.ttc` / `msjhbd.ttc`, `index=0`) via Pillow with caching."""
    with suppress(ImportError, OSError, ValueError):
        from PIL import ImageFont  # type: ignore

        font_path = WINDOWS_MSJH_BOLD if bold else WINDOWS_MSJH_REGULAR
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size=int(size_px), index=0)
        alt_path = WINDOWS_MSJH_REGULAR if bold else WINDOWS_MSJH_BOLD
        if alt_path.exists():
            return ImageFont.truetype(str(alt_path), size=int(size_px), index=0)
    return None


def _parse_inline_bold_segments(text: str, default_bold: bool = False) -> list[tuple[str, bool]]:
    """Split text into `(segment_text, is_bold)` tuples honoring inline `**bold**` spans."""
    raw = str(text or "")
    if not raw:
        return []
    parts = re.split(r"(\*\*(?:(?!\*\*).)+\*\*)", raw)
    segments: list[tuple[str, bool]] = []
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) >= 5:
            segments.append((part[2:-2], True))
        else:
            segments.append((part, bool(default_bold)))
    return segments


def _tokenize_line_for_kinsoku(segments: list[tuple[str, bool]]) -> list[tuple[str, bool]]:
    """
    Tokenize a single hard paragraph into atomic wrapping units for Traditional Chinese + Latin mixed text.
    - NEVER splits Chinese by whitespace and NEVER inserts `-` hyphenation.
    - Keeps contiguous Latin words / numbers / percentages / codes as atomic tokens.
    - Splits CJK ideographs and punctuation into individual character tokens for Kinsoku processing.
    """
    tokens: list[tuple[str, bool]] = []
    for seg_text, is_bold in segments:
        idx = 0
        n = len(seg_text)
        while idx < n:
            ch = seg_text[idx]
            if ch in (" ", "\t"):
                j = idx + 1
                while j < n and seg_text[j] in (" ", "\t"):
                    j += 1
                tokens.append((" ", is_bold))
                idx = j
                continue
            m = _LATIN_TOKEN_RE.match(seg_text, idx)
            if m:
                tokens.append((m.group(0), is_bold))
                idx = m.end()
                continue
            tokens.append((ch, is_bold))
            idx += 1
    return tokens


def _measure_styled_tokens_width_in(
    tokens: Sequence[tuple[str, bool]],
    font_pt: float,
    safety: float,
    reg_font,
    bold_font,
    ref_dpi: float = 288.0,
) -> float:
    """Measure exact advance width in inches for a list of `(text, is_bold)` tokens."""
    if not tokens:
        return 0.0
    if reg_font is not None or bold_font is not None:
        # Merge adjacent same-weight runs to preserve authentic kerning & sub-pixel advances
        total_px = 0.0
        run_buf: list[str] = []
        run_bold = tokens[0][1]
        for tok_txt, tok_bold in tokens:
            if tok_bold == run_bold:
                run_buf.append(tok_txt)
            else:
                f_obj = (bold_font or reg_font) if run_bold else (reg_font or bold_font)
                total_px += float(f_obj.getlength("".join(run_buf)))
                run_buf = [tok_txt]
                run_bold = tok_bold
        if run_buf:
            f_obj = (bold_font or reg_font) if run_bold else (reg_font or bold_font)
            total_px += float(f_obj.getlength("".join(run_buf)))
        return (total_px / ref_dpi) * float(safety)

    # Geometric fallback when Pillow or Windows msjh.ttc is unavailable
    em_units = 0.0
    for tok_txt, tok_bold in tokens:
        w_mult = 1.03 if tok_bold else 1.0
        for ch in tok_txt:
            if unicodedata.east_asian_width(ch) in ("W", "F"):
                em_units += 1.00 * w_mult
            elif ch == " ":
                em_units += 0.28
            elif ch.isupper() or ch in "MW%&@":
                em_units += 0.66 * w_mult
            else:
                em_units += 0.50 * w_mult
    return ((float(font_pt) / 72.0) * em_units) * float(safety)


def _trim_line_edge_spaces(tokens: list[tuple[str, bool]]) -> list[tuple[str, bool]]:
    """Trim leading and trailing pure-space tokens from a wrapped line."""
    start = 0
    end = len(tokens)
    while start < end and tokens[start][0].strip() == "":
        start += 1
    while end > start and tokens[end - 1][0].strip() == "":
        end -= 1
    return tokens[start:end]


def _count_orphan_core_chars(line_text: str) -> int:
    """Count non-punctuation, non-whitespace core characters on a line for orphan detection."""
    return sum(1 for ch in line_text if ch not in ORPHAN_IGNORED_CHARS)


def _wrap_paragraph_kinsoku(
    tokens: list[tuple[str, bool]],
    eff_width_in: float,
    font_pt: float,
    safety: float,
    reg_font,
    bold_font,
    hanging_punct: bool = True,
    ref_dpi: float = 288.0,
) -> list[tuple[str, float]]:
    """
    Wrap a tokenized paragraph using Traditional Chinese Kinsoku rules:
    - Prohibits `KINSOKU_NO_START` at line start (using hanging punctuation when enabled or pulling previous token).
    - Prohibits `KINSOKU_NO_END` (opening brackets) at line end (pushing them to the next line).
    - Breaks overly wide atomic Latin tokens cleanly by character without inserting `-`.
    """
    if not tokens:
        return [("", 0.0)]

    em_in = float(font_pt) / 72.0
    hang_allowance_in = (0.72 * em_in) if hanging_punct else 0.0

    def _w(toks: Sequence[tuple[str, bool]]) -> float:
        return _measure_styled_tokens_width_in(toks, font_pt, safety, reg_font, bold_font, ref_dpi)

    lines_toks: list[list[tuple[str, bool]]] = []
    cur: list[tuple[str, bool]] = []
    idx = 0
    n = len(tokens)

    while idx < n:
        tok_txt, tok_bold = tokens[idx]
        if not cur and tok_txt.strip() == "":
            idx += 1
            continue

        candidate = cur + [(tok_txt, tok_bold)]
        cand_w = _w(candidate)

        if cand_w <= eff_width_in + 1e-6:
            cur = candidate
            idx += 1
            continue

        # Token overflows current line
        if not cur or all(len(t[0]) == 1 and t[0] in KINSOKU_NO_END for t in cur):
            # Single atomic token (or opener + wide atomic token) wider than box: break char-by-char (no '-')
            if len(tok_txt) > 1:
                split_pos = 1
                for k in range(2, len(tok_txt) + 1):
                    if _w(cur + [(tok_txt[:k], tok_bold)]) <= eff_width_in + 1e-6:
                        split_pos = k
                    else:
                        break
                lines_toks.append(cur + [(tok_txt[:split_pos], tok_bold)])
                cur = []
                tokens = tokens[:idx] + [(tok_txt[split_pos:], tok_bold)] + tokens[idx + 1:]
                n = len(tokens)
                continue
            lines_toks.append(cur + [(tok_txt, tok_bold)])
            cur = []
            idx += 1
            continue

        # Rule 1: No-start punctuation (`KINSOKU_NO_START`)
        if len(tok_txt) == 1 and tok_txt in KINSOKU_NO_START:
            if tok_txt in KINSOKU_HANGING_PUNCT and hanging_punct and cand_w <= eff_width_in + hang_allowance_in:
                # Allow single punctuation to hang at line end (matching PowerPoint hangingPunct="1")
                cur = candidate
                lines_toks.append(_trim_line_edge_spaces(cur))
                cur = []
                idx += 1
                continue
            # Otherwise pull preceding token(s) down with this punctuation (oi-dashi),
            # continuing past consecutive closing/no-start punctuation (e.g., `》，` or `）。`)
            cur_trimmed = _trim_line_edge_spaces(cur)
            if len(cur_trimmed) >= 2:
                carry = [(tok_txt, tok_bold)]
                while len(cur_trimmed) >= 2 and (
                    (len(carry[0][0]) == 1 and carry[0][0] in KINSOKU_NO_START)
                    or (len(cur_trimmed[-1][0]) == 1 and cur_trimmed[-1][0] in KINSOKU_NO_END)
                ):
                    carry.insert(0, cur_trimmed.pop())
                lines_toks.append(_trim_line_edge_spaces(cur_trimmed))
                cur = carry
                idx += 1
                continue

        # Rule 2: No-end opening brackets (`KINSOKU_NO_END`)
        cur_trimmed = _trim_line_edge_spaces(cur)
        carry_openers: list[tuple[str, bool]] = []
        while len(cur_trimmed) >= 2 and cur_trimmed[-1][0] in KINSOKU_NO_END:
            carry_openers.insert(0, cur_trimmed.pop())

        lines_toks.append(_trim_line_edge_spaces(cur_trimmed))
        if tok_txt.strip() == "":
            cur = carry_openers
            idx += 1
        else:
            cur = carry_openers
            # Re-evaluate current token on the new line in next iteration

    if cur:
        trimmed = _trim_line_edge_spaces(cur)
        if trimmed:
            lines_toks.append(trimmed)

    if not lines_toks:
        return [("", 0.0)]

    return [("".join(t[0] for t in lt), round(_w(lt), 4)) for lt in lines_toks]


def measure_text_layout(
    text: str,
    box_width_in: float,
    font_pt: float,
    bold: bool = False,
    line_spacing: float = 1.30,
    safety: float = DEFAULT_TEXT_WIDTH_SAFETY,
    space_after_pt: float = 0.0,
    margin_left_in: float = 0.0,
    margin_right_in: float = 0.0,
    margin_top_in: float = 0.0,
    margin_bottom_in: float = 0.0,
    hanging_punct: bool = True,
    font_family: str = FONT_FAMILY,
) -> dict[str, object]:
    """
    Measure exact wrapped lines, orphan status, and safe container height using
    Pillow + Windows `msjh.ttc` / `msjhbd.ttc` (`index=0`, Microsoft JhengHei) and
    Traditional Chinese Kinsoku rules (supporting inline `**bold**` segments).
    """
    _ = font_family  # Reserved for future custom font paths; Windows primary is msjh.ttc index=0
    raw_w = float(box_width_in)
    raw_pt = float(font_pt)
    raw_ls = float(line_spacing)
    raw_safety = float(safety)
    if not (math.isfinite(raw_w) and math.isfinite(raw_pt) and math.isfinite(raw_ls) and math.isfinite(raw_safety)):
        raise ValueError(
            f"box_width_in ({box_width_in}), font_pt ({font_pt}), line_spacing ({line_spacing}), "
            f"and safety ({safety}) must be finite numbers."
        )
    resolved_pt = max(6.0, raw_pt)
    resolved_ls = max(1.0, raw_ls)
    resolved_safety = max(0.85, raw_safety)
    usable_w = max(0.25, raw_w - float(margin_left_in) - float(margin_right_in))

    ref_dpi = 288.0
    size_px = max(12, int(round(resolved_pt * (ref_dpi / 72.0))))
    reg_font = _load_msjh_font(size_px, bold=False)
    bold_font = _load_msjh_font(size_px, bold=True)
    backend = "pillow_msjh" if (reg_font is not None or bold_font is not None) else "fallback_heuristic"

    raw_text = str(text or "")
    if not raw_text.strip():
        single_h = (resolved_pt * MSJH_LINE_HEIGHT_EM * resolved_ls) / 72.0
        safe_h = round(single_h + float(margin_top_in) + float(margin_bottom_in) + 0.04, 4)
        return {
            "line_count": 0,
            "lines": [],
            "line_widths_in": [],
            "max_line_width_in": 0.0,
            "usable_width_in": round(usable_w, 4),
            "last_line_text": "",
            "last_line_char_count": 0,
            "last_line_cjk_chars": 0,
            "orphan_flag": False,
            "orphan_paragraphs": [],
            "content_height_in": 0.0,
            "safe_height_in": safe_h,
            "font_backend": backend,
            "safety_factor": resolved_safety,
        }

    # Split into hard paragraphs while preserving inline **bold** state per line
    hard_paragraphs = raw_text.splitlines()
    all_lines: list[str] = []
    all_widths: list[float] = []
    orphan_paragraphs: list[int] = []

    for p_idx, para in enumerate(hard_paragraphs):
        if not para.strip():
            all_lines.append("")
            all_widths.append(0.0)
            continue
        segs = _parse_inline_bold_segments(para, default_bold=bold)
        toks = _tokenize_line_for_kinsoku(segs)
        wrapped = _wrap_paragraph_kinsoku(
            toks,
            usable_w,
            resolved_pt,
            resolved_safety,
            reg_font,
            bold_font,
            hanging_punct=hanging_punct,
            ref_dpi=ref_dpi,
        )
        p_lines = [w[0] for w in wrapped]
        p_widths = [w[1] for w in wrapped]
        all_lines.extend(p_lines)
        all_widths.extend(p_widths)

        if len(p_lines) >= 2:
            tail_core = _count_orphan_core_chars(p_lines[-1])
            if 0 < tail_core <= 2:
                orphan_paragraphs.append(p_idx)

    line_count = len(all_lines)
    last_line_text = all_lines[-1] if all_lines else ""
    last_core = _count_orphan_core_chars(last_line_text)
    last_cjk = sum(
        1 for ch in last_line_text
        if ch not in ORPHAN_IGNORED_CHARS and unicodedata.east_asian_width(ch) in ("W", "F")
    )

    # PowerPoint line advance: first (N-1) lines advance by font_pt * MSJH_LINE_HEIGHT_EM * line_spacing;
    # final line needs natural glyph box height (font_pt * MSJH_LINE_HEIGHT_EM).
    single_natural_in = (resolved_pt * MSJH_LINE_HEIGHT_EM) / 72.0
    step_in = single_natural_in * resolved_ls
    inter_para_in = (max(0, len(hard_paragraphs) - 1) * max(0.0, float(space_after_pt))) / 72.0
    content_h = ((max(0, line_count - 1) * step_in) + single_natural_in + inter_para_in) if line_count > 0 else 0.0
    safe_h = content_h + float(margin_top_in) + float(margin_bottom_in) + 0.04

    return {
        "line_count": line_count,
        "lines": all_lines,
        "line_widths_in": all_widths,
        "max_line_width_in": round(max(all_widths, default=0.0), 4),
        "usable_width_in": round(usable_w, 4),
        "last_line_text": last_line_text,
        "last_line_char_count": last_core,
        "last_line_cjk_chars": last_cjk,
        "orphan_flag": bool(orphan_paragraphs),
        "orphan_paragraphs": orphan_paragraphs,
        "content_height_in": round(content_h, 4),
        "safe_height_in": round(safe_h, 4),
        "font_backend": backend,
        "safety_factor": resolved_safety,
    }


# -------------------------------------------------------------------------
# Step 3 Core 3: Inverted Geometry-First Autofit (NEVER shrink font first)
# -------------------------------------------------------------------------

def _normalize_box_dict(box: object) -> dict[str, float]:
    """Normalize a `(left, top, width, height)` tuple or dict into a canonical box dict."""
    if isinstance(box, dict):
        return {
            "left": float(box.get("left", box.get("x", 0.5))),
            "top": float(box.get("top", box.get("y", 1.36))),
            "width": max(0.5, float(box.get("width", box.get("w", 4.0)))),
            "height": max(0.3, float(box.get("height", box.get("h", 2.0)))),
        }
    if isinstance(box, (list, tuple)) and len(box) >= 4:
        return {
            "left": float(box[0]),
            "top": float(box[1]),
            "width": max(0.5, float(box[2])),
            "height": max(0.3, float(box[3])),
        }
    raise TypeError(f"Unsupported box specification: {box!r}")


def _measure_single_text_spec(
    spec: object,
    box: dict[str, float],
    default_font_pt: float,
    default_line_spacing: float,
    default_bold: bool,
    safety: float,
) -> dict[str, object]:
    """Measure a single text spec (str, dict, or list of paragraphs) against a candidate box."""
    if isinstance(spec, dict):
        text = spec.get("text")
        if text is None and "paragraphs" in spec:
            text = "\n".join(str(p) for p in spec["paragraphs"])
        font_pt = max(default_font_pt, float(spec.get("font_pt", default_font_pt)))
        bold = bool(spec.get("bold", default_bold))
        ls = float(spec.get("line_spacing", default_line_spacing))
        sa = float(spec.get("space_after_pt", 0.0))
        ml = float(spec.get("margin_left_in", spec.get("margin_x_in", 0.0)))
        mr = float(spec.get("margin_right_in", spec.get("margin_x_in", 0.0)))
        mt = float(spec.get("margin_top_in", spec.get("margin_y_in", 0.0)))
        mb = float(spec.get("margin_bottom_in", spec.get("margin_y_in", 0.0)))
    elif isinstance(spec, (list, tuple)):
        text = "\n".join(str(p) for p in spec)
        font_pt, bold, ls, sa = default_font_pt, default_bold, default_line_spacing, 4.0
        ml = mr = mt = mb = 0.0
    else:
        text = str(spec or "")
        font_pt, bold, ls, sa = default_font_pt, default_bold, default_line_spacing, 0.0
        ml = mr = mt = mb = 0.0

    return measure_text_layout(
        str(text or ""),
        box_width_in=box["width"],
        font_pt=font_pt,
        bold=bold,
        line_spacing=ls,
        safety=safety,
        space_after_pt=sa,
        margin_left_in=ml,
        margin_right_in=mr,
        margin_top_in=mt,
        margin_bottom_in=mb,
    )


def autofit_box_geometry_first(
    text_spec: object,
    candidate_boxes: object,
    target_body_pt: float,
    min_font_pt: float = MIN_CONTENT_FONT_PT,
    line_spacing: float = 1.30,
    bold: bool = False,
    max_bottom_in: float = 7.25,
    max_right_in: float = 12.833,
    safety: float = DEFAULT_TEXT_WIDTH_SAFETY,
    allow_rebalance: bool = True,
    allow_height_grow: bool = True,
) -> dict[str, object]:
    """
    Inverted Geometry-First Autofit Engine (never shrinks font below `target_body_pt` or `min_font_pt`):
    - Phase 1 (Width Rebalance / Micro-Expand): If overflow or orphan last line (`<= 2` CJK chars) is
      detected, rebalances widths across adjacent columns (or gently widens a single box within bounds).
    - Phase 2 (Grow Height Downward): Expands box height downward up to `max_bottom_in`.
    - Phase 3 (Split Flag / Copy Consent): If geometry alone cannot resolve overflow, flags
      `needs_split_slide=True` (`fits=False`); if only an orphan remains, flags `needs_copy_consent=True`.
    - Hard Invariant: `resolved_font_pt >= max(min_font_pt, target_body_pt)` and `font_shrunk` is ALWAYS `False`.
    """
    raw_min = float(min_font_pt)
    raw_target = float(target_body_pt)
    if not (math.isfinite(raw_min) and math.isfinite(raw_target)):
        raise ValueError(
            f"min_font_pt ({min_font_pt}) and target_body_pt ({target_body_pt}) must be finite numbers."
        )
    resolved_min = max(MIN_CONTENT_FONT_PT, raw_min)
    effective_pt = max(resolved_min, raw_target)

    if isinstance(candidate_boxes, dict) or (
        isinstance(candidate_boxes, (list, tuple))
        and len(candidate_boxes) == 4
        and all(isinstance(v, (int, float)) for v in candidate_boxes)
    ):
        boxes = [_normalize_box_dict(candidate_boxes)]
    elif isinstance(candidate_boxes, (list, tuple)) and len(candidate_boxes) > 0:
        boxes = [_normalize_box_dict(b) for b in candidate_boxes]
    else:
        raise ValueError("candidate_boxes must be a box dict/4-tuple or a non-empty list of boxes.")

    n_boxes = len(boxes)
    if n_boxes == 1:
        specs = [text_spec]
    elif isinstance(text_spec, (list, tuple)) and len(text_spec) == n_boxes:
        specs = list(text_spec)
    else:
        raise ValueError(
            f"Mismatch between candidate_boxes count ({n_boxes}) and text_spec; "
            "pass a sequence of equal length for multi-box autofit."
        )

    def _measure_all(cur_boxes: list[dict[str, float]]) -> list[dict[str, object]]:
        return [
            _measure_single_text_spec(sp, bx, effective_pt, line_spacing, bold, safety)
            for sp, bx in zip(specs, cur_boxes)
        ]

    actions: list[str] = []
    measurements = _measure_all(boxes)

    # Phase 1: Rebalance adjacent columns or micro-expand single box width
    if allow_rebalance:
        if n_boxes == 1:
            m0 = measurements[0]
            b0 = boxes[0]
            needs_help = (float(m0["safe_height_in"]) > b0["height"]) or bool(m0["orphan_flag"])
            avail_w = max(0.0, float(max_right_in) - (b0["left"] + b0["width"]))
            if needs_help and avail_w > 0.05:
                step_max = min(avail_w, 0.50)
                best_w = b0["width"]
                best_m = m0
                fallback_w = b0["width"]
                fallback_m = m0
                for step_i in range(1, 11):
                    trial_w = round(b0["width"] + step_max * (step_i / 10.0), 3)
                    trial_box = dict(b0, width=trial_w)
                    trial_m = _measure_single_text_spec(specs[0], trial_box, effective_pt, line_spacing, bold, safety)
                    if float(trial_m["safe_height_in"]) < float(fallback_m["safe_height_in"]) - 1e-3:
                        fallback_w = trial_w
                        fallback_m = trial_m
                    improved_overflow = float(trial_m["safe_height_in"]) < float(best_m["safe_height_in"]) - 1e-3
                    fixed_orphan = bool(best_m["orphan_flag"]) and not bool(trial_m["orphan_flag"])
                    if fixed_orphan or (improved_overflow and not bool(trial_m["orphan_flag"])):
                        best_w = trial_w
                        best_m = trial_m
                        if float(best_m["safe_height_in"]) <= b0["height"] and not bool(best_m["orphan_flag"]):
                            break
                if best_w <= b0["width"] + 1e-4 and float(m0["safe_height_in"]) > b0["height"] and fallback_w > b0["width"] + 1e-4:
                    best_w = fallback_w
                if best_w > b0["width"] + 1e-4:
                    boxes[0]["width"] = best_w
                    measurements = _measure_all(boxes)
                    actions.append("expand_width")
        else:
            # Multi-column horizontal rebalance preserving outer edges, gaps, and caller input order
            order = sorted(range(n_boxes), key=lambda idx: (boxes[idx]["left"], boxes[idx]["top"]))
            same_row = all(abs(boxes[idx]["top"] - boxes[order[0]]["top"]) <= 0.35 for idx in order)
            gaps = [
                round(boxes[order[pos + 1]]["left"] - (boxes[order[pos]]["left"] + boxes[order[pos]]["width"]), 4)
                for pos in range(n_boxes - 1)
            ]
            is_horizontal_row = same_row and all(g >= -0.02 for g in gaps)
            if is_horizontal_row:
                min_col_w = 1.60
                rebalanced = False
                for _pass in range(3):
                    changed = False
                    for pos_i in range(n_boxes):
                        i = order[pos_i]
                        mi = measurements[i]
                        overflow_i = float(mi["safe_height_in"]) - boxes[i]["height"]
                        orphan_i = bool(mi["orphan_flag"])
                        if overflow_i <= 0.0 and not orphan_i:
                            continue
                        # Find donor column with greatest spare vertical capacity
                        best_donor = None
                        best_spare = 0.0
                        for pos_j in range(n_boxes):
                            j = order[pos_j]
                            if j == i:
                                continue
                            mj = measurements[j]
                            spare_j = boxes[j]["height"] - float(mj["safe_height_in"])
                            if spare_j > best_spare and boxes[j]["width"] > min_col_w + 0.25 and not bool(mj["orphan_flag"]):
                                best_spare = spare_j
                                best_donor = j
                        if best_donor is None:
                            continue
                        max_delta = min(boxes[best_donor]["width"] - min_col_w, boxes[i]["width"] * 0.25, 0.75)
                        if max_delta <= 0.05:
                            continue
                        base_boxes = [dict(b) for b in boxes]
                        best_trial_boxes: list[dict[str, float]] | None = None
                        best_trial_ms: list[dict[str, object]] | None = None
                        for step_i in range(1, 9):
                            delta = round(max_delta * (step_i / 8.0), 3)
                            trial_boxes = [dict(b) for b in base_boxes]
                            trial_boxes[i]["width"] = round(trial_boxes[i]["width"] + delta, 3)
                            trial_boxes[best_donor]["width"] = round(trial_boxes[best_donor]["width"] - delta, 3)
                            # Recompute left positions cleanly along sorted visual order preserving gaps
                            cur_x = trial_boxes[order[0]]["left"]
                            for pos_k, k in enumerate(order):
                                trial_boxes[k]["left"] = round(cur_x, 3)
                                cur_x += trial_boxes[k]["width"] + (gaps[pos_k] if pos_k < n_boxes - 1 else 0.0)
                            trial_ms = _measure_all(trial_boxes)
                            donor_ok = (
                                float(trial_ms[best_donor]["safe_height_in"]) <= trial_boxes[best_donor]["height"]
                                and not bool(trial_ms[best_donor]["orphan_flag"])
                            )
                            ref_mi = best_trial_ms[i] if best_trial_ms is not None else mi
                            ref_orphan = bool(ref_mi["orphan_flag"])
                            target_better = (
                                (float(trial_ms[i]["safe_height_in"]) < float(ref_mi["safe_height_in"]) - 1e-3 and not (not ref_orphan and bool(trial_ms[i]["orphan_flag"])))
                                or (ref_orphan and not bool(trial_ms[i]["orphan_flag"]) and float(trial_ms[i]["safe_height_in"]) <= float(ref_mi["safe_height_in"]) + 1e-3)
                            )
                            if donor_ok and target_better:
                                best_trial_boxes = trial_boxes
                                best_trial_ms = trial_ms
                                if float(trial_ms[i]["safe_height_in"]) <= trial_boxes[i]["height"] and not bool(trial_ms[i]["orphan_flag"]):
                                    break
                        if best_trial_boxes is not None and best_trial_ms is not None:
                            boxes = best_trial_boxes
                            measurements = best_trial_ms
                            changed = True
                            rebalanced = True
                    if not changed:
                        break
                if rebalanced:
                    actions.append("rebalance_widths")

    # Phase 2: Grow box height downward (within max_bottom_in and respecting vertically stacked neighbors)
    if allow_height_grow:
        grew_any = False
        for i in range(n_boxes):
            req_h = round(float(measurements[i]["safe_height_in"]) + 0.02, 3)
            if req_h > boxes[i]["height"]:
                bottom_limit = float(max_bottom_in)
                bi = boxes[i]
                for j in range(n_boxes):
                    if j == i:
                        continue
                    bj = boxes[j]
                    x_overlap = min(bi["left"] + bi["width"], bj["left"] + bj["width"]) - max(bi["left"], bj["left"])
                    if x_overlap > 0.02 and bj["top"] >= bi["top"] + bi["height"] - 0.02:
                        bottom_limit = min(bottom_limit, bj["top"] - 0.12)
                max_h = round(bottom_limit - bi["top"], 3)
                if max_h >= req_h:
                    boxes[i]["height"] = req_h
                    grew_any = True
                elif max_h > boxes[i]["height"]:
                    boxes[i]["height"] = max_h
                    grew_any = True
        if grew_any:
            actions.append("grow_height")

    # Phase 3: Evaluate final fit (NEVER shrink font)
    still_overflow = any(
        float(measurements[i]["safe_height_in"]) > boxes[i]["height"] + 1e-4
        for i in range(n_boxes)
    )
    orphan_unresolved = any(bool(m["orphan_flag"]) for m in measurements)
    if still_overflow:
        actions.append("split_slide_required")
    if not actions:
        actions.append("none")

    return {
        "fits": not still_overflow,
        "boxes": boxes,
        "measurements": measurements,
        "resolved_font_pt": effective_pt,
        "min_font_pt": resolved_min,
        "font_shrunk": False,
        "actions": actions,
        "needs_split_slide": still_overflow,
        "orphan_unresolved": orphan_unresolved,
        "needs_copy_consent": (not still_overflow) and orphan_unresolved,
    }


# -------------------------------------------------------------------------
# Step 3 Core 4: Mode 3 Tier 3 Dual-Engine 300 DPI Transparent Renderer
# -------------------------------------------------------------------------

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


# -------------------------------------------------------------------------
# Step 4 Shared Module 1–2 Helpers (SSOT Typography, Spotlight & Flow)
# -------------------------------------------------------------------------

_LEAD_BODY_SPLIT_RE = re.compile(r"^\*\*([^*]{1,38})\*\*\s*[：:—–-]\s*(.+)$", re.DOTALL)


def _blend_hex(hex_a: str, hex_b: str, weight_a: float = 0.14) -> str:
    """Blend two '#RRGGBB' colors linearly (`weight_a` in [0, 1]) for high-contrast subtle spotlight washes."""
    def _parse(h: str) -> tuple[int, int, int]:
        c = str(h or "#FFFFFF").strip().lstrip("#")
        if len(c) == 3:
            c = "".join(ch * 2 for ch in c)
        if len(c) != 6:
            return (255, 255, 255)
        return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))

    wa = max(0.0, min(1.0, float(weight_a)))
    wb = 1.0 - wa
    ra, ga, ba = _parse(hex_a)
    rb, gb, bb = _parse(hex_b)
    r = int(round(ra * wa + rb * wb))
    g = int(round(ga * wa + gb * wb))
    b = int(round(ba * wa + bb * wb))
    return f"#{r:02X}{g:02X}{b:02X}"


def _is_dark_hex(hex_str: str) -> bool:
    """Return True if `#RRGGBB` has relative luminance < 0.25 (dark stage / dark surface)."""
    c = str(hex_str or "#FFFFFF").strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    if len(c) != 6:
        return False
    r, g, b = int(c[0:2], 16) / 255.0, int(c[2:4], 16) / 255.0, int(c[4:6], 16) / 255.0
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return lum < 0.25


def _theme_palette(dt: dict[str, str]) -> dict[str, str]:
    """
    SSOT theme-adaptive palette resolver supporting both `light_classroom` and `dark_stage` themes
    without hardcoded light-only fills (`#FFFFFF`) or dark-only body ink (`#334155`).
    """
    bg_canvas = dt.get("bg_canvas", "#F8FAFC")
    is_dark = _is_dark_hex(bg_canvas)
    bg_card = dt.get("bg_card", "#1E293B" if is_dark else "#FFFFFF")
    border_card = dt.get("border_card", "#475569" if is_dark else "#CBD5E1")
    ink_primary = dt.get("ink_primary", "#F8FAFC" if is_dark else "#0F172A")
    ink_muted = dt.get("ink_muted", "#94A3B8" if is_dark else "#64748B")
    ink_body = dt.get("ink_secondary", "#E2E8F0") if is_dark else "#334155"
    primary_accent = dt.get("primary_accent", "#38BDF8" if is_dark else "#0284C7")
    pill_fg = dt.get("pill_fg", "#0F172A" if is_dark else "#FFFFFF")
    divider_subtle = _blend_hex(border_card, bg_canvas, 0.55) if is_dark else "#E2E8F0"
    divider_strong = border_card if is_dark else "#CBD5E1"
    muted_bar = _blend_hex(border_card, ink_muted, 0.35) if is_dark else "#CBD5E1"
    muted_accent = ink_muted if is_dark else "#64748B"
    arrow_muted = ink_muted if is_dark else "#94A3B8"
    return {
        "is_dark": "1" if is_dark else "",
        "bg_canvas": bg_canvas,
        "bg_card": bg_card,
        "border_card": border_card,
        "ink_primary": ink_primary,
        "ink_body": ink_body,
        "ink_muted": ink_muted,
        "primary_accent": primary_accent,
        "pill_fg": pill_fg,
        "divider_subtle": divider_subtle,
        "divider_strong": divider_strong,
        "muted_bar": muted_bar,
        "muted_accent": muted_accent,
        "arrow_muted": arrow_muted,
    }


def _resolve_engine_context(
    tokens: dict[str, object] | None,
    doc_theme_id: str | None,
    body_font_pt: float | None = None,
    default_body_pt: float = 13.0,
    caller_default_pt: float | None = None,
) -> tuple[dict[str, str], float, float, dict[str, float], dict[str, float]]:
    """
    Central SSOT context resolver for all Step 4 layout functions:
    Returns `(theme_dict, min_floor_pt, resolved_body_pt, typography_scale, spacing_dict)`.
    - Preserves 100% backward compatibility when `tokens is None`.
    - When `tokens` is supplied, adopts `tokens['theme']`, `tokens['min_font_pt']`, and
      `tokens['target_body_pt']` (unless caller explicitly passed a non-default `body_font_pt`).
    - Guarantees every Zone 2 text tier (`kicker`, `subtitle`, `caption`) stays `>= min_floor_pt`.
    """
    if isinstance(tokens, dict) and isinstance(tokens.get("theme"), dict):
        dt = {str(k): str(v) for k, v in tokens["theme"].items()}  # type: ignore[union-attr]
    else:
        dt = load_document_theme(doc_theme_id)

    min_floor = MIN_CONTENT_FONT_PT
    if isinstance(tokens, dict) and tokens.get("min_font_pt") is not None:
        min_floor = max(MIN_CONTENT_FONT_PT, float(tokens["min_font_pt"]))  # type: ignore[arg-type]

    if body_font_pt is None:
        if isinstance(tokens, dict) and tokens.get("target_body_pt") is not None:
            raw_body = float(tokens["target_body_pt"])  # type: ignore[arg-type]
        else:
            raw_body = float(default_body_pt)
    else:
        raw_body = float(body_font_pt)
        if (
            isinstance(tokens, dict)
            and tokens.get("target_body_pt") is not None
            and caller_default_pt is not None
            and abs(raw_body - float(caller_default_pt)) < 1e-6
        ):
            raw_body = float(tokens["target_body_pt"])  # type: ignore[arg-type]

    resolved_body = max(min_floor, raw_body)
    typo = resolve_typography_scale(resolved_body)
    typo["body"] = resolved_body
    typo["subtitle"] = max(min_floor, float(typo["subtitle"]))
    typo["caption"] = max(min_floor, float(typo["caption"]))
    typo["kicker"] = max(min_floor, _round_half_pt(resolved_body * 0.85))
    typo["lead"] = _round_half_pt(resolved_body + 1.5)
    typo["card_title"] = _round_half_pt(resolved_body + 3.0)

    default_spacing = {
        "canvas_w_in": 13.333,
        "canvas_h_in": 7.5,
        "margin_x_in": 0.50,
        "zone1_top_in": 0.15,
        "item_gap_in": 0.24,
        "col_gap_in": 0.28,
        "card_pad_x_in": 0.20,
        "card_pad_y_in": 0.16,
        "line_spacing": 1.30,
        "headline_line_spacing": 1.18,
    }
    if isinstance(tokens, dict) and isinstance(tokens.get("spacing"), dict):
        merged_sp = dict(default_spacing)
        for k, v in tokens["spacing"].items():  # type: ignore[union-attr]
            merged_sp[str(k)] = float(v)
        spacing = merged_sp
    else:
        spacing = default_spacing

    return dt, min_floor, resolved_body, typo, spacing


_LEADING_INDEX_PREFIX_RE = re.compile(
    r"^\s*(?:"
    r"(?:#|No\.?\s*)\d{1,2}(?:[\.\)、:：\-—–\|｜\s]|$)"
    r"|0\d(?:[\.\)、:：\-—–\|｜\s]|$|(?=[\u4e00-\u9fff]))"
    r"|[1-9]\d?(?:[\.\)、:：\-—–\|｜]|$)"
    r"|[1-9]\d?\s+(?!(?:年|月|日|週|周|天|小時|分鐘|秒|倍|成|折|%|％|個|大|種|款|類|套|萬|億|千|百|元|美元|台幣|人|位|家|間|筆|次|季|歲|pp\b|[xX]\b|[KMB]\b))"
    r"|[\(\（]\d{1,2}[\)\）]"
    r"|(?:Phase|Step|Stage|Part|Tier|Layer|Pillar|Track|Level|Module|Act|Case)\s*(?:\d{1,2}|[IVX]{1,4})(?=$|[\.\)、:：\-—–\|｜\s\u4e00-\u9fff])"
    r"|Q[1-4](?=$|[\.\)、:：\-—–\|｜\s\u4e00-\u9fff])"
    r"|(?:階段|步驟)\s*[\d一二三四五六七八九十]+(?=$|[\.\)、:：\-—–\|｜\s\u4e00-\u9fff])"
    r"|第[一二三四五六七八九十\d]+(?:[步層階段項條部分章節篇點]|[\.\)、:：\-—–\s])"
    r"|[一二三四五六七八九十]+[\.\、]"
    r")",
    re.IGNORECASE,
)


def _first_non_empty_str(mapping: object, *keys: str, default: str = "") -> str:
    """Return the first non-empty scalar string found under `keys` in `mapping`, ignoring None/collections."""
    if not isinstance(mapping, dict):
        return default
    for k in keys:
        if k not in mapping:
            continue
        val = mapping.get(k)
        if val is None or isinstance(val, (bool, list, tuple, dict, set)):
            continue
        s = str(val).strip()
        if s:
            return s
    return default


def _coerce_items_list(val: object) -> list[object]:
    """Coerce a scalar string, dict, or sequence into a clean non-empty list of raw item entries."""
    if val is None or isinstance(val, bool):
        return []
    if isinstance(val, str):
        s = val.strip()
        return [s] if s else []
    if isinstance(val, dict):
        return [val] if val else []
    if isinstance(val, (list, tuple)):
        out: list[object] = []
        for entry in val:
            if entry is None or isinstance(entry, bool):
                continue
            if isinstance(entry, str):
                s = entry.strip()
                if s:
                    out.append(s)
            else:
                out.append(entry)
        return out
    s = str(val).strip()
    return [s] if s else []


def _parse_lead_body_item(item: object) -> tuple[str, str]:
    """
    Parse any structured or legacy row item into `(lead, body)` for independent two-paragraph rendering:
    - dict: `{lead/heading/title/label/name, body/detail/desc/text/content/subtitle/sub, rows/items/points/bullets}`
    - 2-tuple/list: `(lead, body)` (safely flattening nested lists/dicts in `body`)
    - string matching `**Lead**：Body` or `**Lead** — Body`: splits into `(Lead, Body)`
    - plain string: `("", text)`
    """
    if isinstance(item, dict):
        lead = _first_non_empty_str(item, "lead", "heading", "title", "label", "name")
        body_parts: list[str] = []
        body_scalar = _first_non_empty_str(item, "body", "detail", "desc", "text", "content", "subtitle", "sub")
        if body_scalar:
            body_parts.append(body_scalar)
        for list_k in ("rows", "items", "points", "bullets"):
            sub_raw = _coerce_items_list(item.get(list_k))
            if sub_raw:
                for sub_it in sub_raw:
                    s_ld, s_bd = _parse_lead_body_item(sub_it)
                    line = f"**{s_ld}**：{s_bd}" if (s_ld and s_bd) else (s_ld or s_bd)
                    if line and line not in body_parts:
                        body_parts.append(line)
                break
        return (lead, "\n".join(body_parts).strip())
    if isinstance(item, (list, tuple)):
        raw_segs = [seg for seg in item if seg is not None and not isinstance(seg, bool)]
        if len(raw_segs) >= 2:
            head_raw = raw_segs[0]
            head_s = str(head_raw).strip() if not isinstance(head_raw, (list, tuple, dict)) else ""
            tail_lines: list[str] = []
            for seg in raw_segs[1:]:
                if isinstance(seg, (list, tuple)):
                    for sub_it in _coerce_items_list(seg):
                        s_ld, s_bd = _parse_lead_body_item(sub_it)
                        line = f"**{s_ld}**：{s_bd}" if (s_ld and s_bd) else (s_ld or s_bd)
                        if line:
                            tail_lines.append(line)
                elif isinstance(seg, dict):
                    s_ld, s_bd = _parse_lead_body_item(seg)
                    line = f"**{s_ld}**：{s_bd}" if (s_ld and s_bd) else (s_ld or s_bd)
                    if line:
                        tail_lines.append(line)
                else:
                    s_txt = str(seg).strip()
                    if s_txt:
                        tail_lines.append(s_txt)
            if head_s or tail_lines:
                return (head_s, "\n".join(tail_lines))
        elif len(raw_segs) == 1:
            return _parse_lead_body_item(raw_segs[0])
        return ("", "")
    raw = str(item or "").strip()
    if not raw:
        return ("", "")
    m = _LEAD_BODY_SPLIT_RE.match(raw)
    if m:
        return (m.group(1).strip(), m.group(2).strip())
    return ("", raw)


def _extract_lead_body_items(
    mapping: object,
    *,
    extra_lead: str = "",
    include_subtitle_as_body: bool = False,
) -> list[tuple[str, str]]:
    """
    SSOT black-box content extractor for slide spec dicts (`F2-A/B/C`, `F3-A`, `F4-A`, `F5-B`).
    Accepts any intuitive collection key (`rows`/`items`/`points`/`bullets`) and/or narrative key
    (`body`/`desc`/`detail`/`text`/`content`) without silently dropping text, and integrates an
    optional `extra_lead` (Bold +1~1.5pt) cleanly ahead of body items.
    """
    if not isinstance(mapping, dict):
        ld, bd = _parse_lead_body_item(mapping)
        return [(ld, bd)] if (ld or bd) else []

    collection_raw: list[object] = []
    for ck in ("rows", "items", "points", "bullets"):
        if ck in mapping:
            cand = _coerce_items_list(mapping.get(ck))
            if cand:
                collection_raw = cand
                break

    body_raw: list[object] = []
    for bk in ("body", "desc", "detail", "text", "content"):
        if bk in mapping:
            cand = _coerce_items_list(mapping.get(bk))
            if cand:
                body_raw = cand
                break

    if not collection_raw and not body_raw and include_subtitle_as_body:
        for sk in ("subtitle", "sub"):
            if sk in mapping:
                cand = _coerce_items_list(mapping.get(sk))
                if cand:
                    body_raw = cand
                    break

    combined_raw: list[object] = []
    if body_raw and collection_raw:
        combined_raw.extend(body_raw)
        for entry in collection_raw:
            if entry not in combined_raw:
                combined_raw.append(entry)
    elif collection_raw:
        combined_raw = collection_raw
    else:
        combined_raw = body_raw

    parsed: list[tuple[str, str]] = []
    for entry in combined_raw:
        ld, bd = _parse_lead_body_item(entry)
        if ld or bd:
            parsed.append((ld, bd))

    lead_clean = str(extra_lead or "").strip()
    if lead_clean:
        if not parsed:
            parsed = [(lead_clean, "")]
        elif all(not p[0] for p in parsed):
            if len(parsed) == 1:
                parsed = [(lead_clean, parsed[0][1])]
            else:
                parsed = [(lead_clean, "\n".join(p[1] for p in parsed if p[1]))]
        elif not parsed[0][0]:
            parsed[0] = (lead_clean, parsed[0][1])
        elif parsed[0][0] != lead_clean:
            parsed.insert(0, (lead_clean, ""))

    return parsed


def _measure_lead_body_item_height(
    lead: str,
    body: str,
    width_in: float,
    lead_pt: float,
    body_pt: float,
    line_spacing: float = 1.30,
) -> float:
    """Measure exact safe vertical height (inches) for an independent two-paragraph Lead -> Body block."""
    w = max(0.45, float(width_in) - 0.04)
    total_h = 0.0
    if lead:
        m_lead = measure_text_layout(lead, w, lead_pt, bold=True, line_spacing=1.22)
        total_h += float(m_lead["content_height_in"])
    if body:
        m_body = measure_text_layout(body, w, body_pt, bold=False, line_spacing=line_spacing, space_after_pt=3.0)
        body_h = float(m_body["content_height_in"])
        # Borderline wrap guard: reserve extra vertical breathing room only when longest line is within 0.65" (or >86% on narrow cols)
        if float(m_body["max_line_width_in"]) >= max(w * 0.86, w - 0.65):
            body_h += (float(body_pt) * MSJH_LINE_HEIGHT_EM * line_spacing) / 72.0 * 0.65
        total_h += body_h
    if lead and body:
        total_h += 0.05  # Pt(2.5) space_after + safety cushion between Lead and Body
    return round(max(0.28, total_h + 0.08), 4)


def _render_compact_lead_body_stack(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    items: Sequence[tuple[str, str]],
    lead_pt: float,
    body_pt: float,
    lead_hex: str,
    body_hex: str,
    bold_color_hex: str,
    line_spacing: float = 1.16,
    para_space_after_pt: float = 2.0,
) -> None:
    """
    Render multiple `(lead, body)` items inside a single TOP-aligned textbox to avoid per-box margin
    overhead when vertical space in a tile/row/quadrant/milestone is tight.
    """
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(max(0.45, w)), Inches(max(0.24, h)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.01)
    tf.margin_bottom = Inches(0.01)

    compact_ls = min(float(line_spacing), 1.18)
    first_para = True
    n_items = len(items)
    for it_idx, (ld, bd) in enumerate(items):
        if ld:
            p_l = tf.paragraphs[0] if first_para else tf.add_paragraph()
            first_para = False
            p_l.alignment = PP_ALIGN.LEFT
            p_l.line_spacing = min(compact_ls, 1.15)
            if bd or it_idx < n_items - 1:
                p_l.space_after = Pt(min(para_space_after_pt, 2.0))
            _populate_paragraph_runs(p_l, ld, lead_pt, lead_hex, bold=True, bold_color_hex=lead_hex)
        if bd:
            bd_lines = bd.splitlines() or [bd]
            for li, seg in enumerate(bd_lines):
                p_b = tf.paragraphs[0] if first_para else tf.add_paragraph()
                first_para = False
                p_b.alignment = PP_ALIGN.LEFT
                p_b.line_spacing = compact_ls
                if li < len(bd_lines) - 1 or it_idx < n_items - 1:
                    p_b.space_after = Pt(para_space_after_pt)
                _populate_paragraph_runs(p_b, seg, body_pt, body_hex, bold=False, bold_color_hex=bold_color_hex)


def _render_lead_body_box(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    lead: str,
    body: str,
    lead_pt: float,
    body_pt: float,
    lead_hex: str,
    body_hex: str,
    bold_color_hex: str,
    line_spacing: float = 1.30,
) -> None:
    """Render an independent two-paragraph Lead (+1.0~1.5pt Bold #0F172A) -> Body (#334155) block with TOP alignment."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(max(0.45, w)), Inches(max(0.24, h)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.01)
    tf.margin_bottom = Inches(0.01)

    if lead and body:
        p0 = tf.paragraphs[0]
        p0.alignment = PP_ALIGN.LEFT
        p0.line_spacing = 1.22
        p0.space_after = Pt(2.5)
        _populate_paragraph_runs(p0, lead, lead_pt, lead_hex, bold=True, bold_color_hex=lead_hex)
        for seg_i, seg in enumerate(body.splitlines() or [body]):
            p_b = tf.add_paragraph()
            p_b.alignment = PP_ALIGN.LEFT
            p_b.line_spacing = line_spacing
            if seg_i < len(body.splitlines()) - 1:
                p_b.space_after = Pt(3.0)
            _populate_paragraph_runs(p_b, seg, body_pt, body_hex, bold=False, bold_color_hex=bold_color_hex)
    elif lead:
        p0 = tf.paragraphs[0]
        p0.alignment = PP_ALIGN.LEFT
        p0.line_spacing = 1.24
        _populate_paragraph_runs(p0, lead, lead_pt, lead_hex, bold=True, bold_color_hex=lead_hex)
    elif body:
        lines = body.splitlines() or [body]
        for seg_i, seg in enumerate(lines):
            p = tf.paragraphs[0] if seg_i == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.LEFT
            p.line_spacing = line_spacing
            if seg_i < len(lines) - 1:
                p.space_after = Pt(3.0)
            _populate_paragraph_runs(p, seg, body_pt, body_hex, bold=False, bold_color_hex=bold_color_hex)


def _measure_three_tier_header(
    kicker: str,
    title: str,
    subtitle: str,
    width_in: float,
    kicker_pt: float,
    title_pt: float,
    sub_pt: float,
) -> float:
    """Measure exact safe height (inches) for a single-textbox 3-tier header (`Kicker -> Title (+3pt) -> Subtitle`)."""
    w = max(0.45, float(width_in) - 0.04)
    tier_specs: list[tuple[str, float, bool, float, float]] = []
    if kicker:
        tier_specs.append((kicker, kicker_pt, True, 1.18, 2.5))
    if title:
        tier_specs.append((title, title_pt, True, 1.18, 3.0))
    if subtitle:
        tier_specs.append((subtitle, sub_pt, False, 1.22, 0.0))

    total_h = 0.0
    n_tiers = len(tier_specs)
    for t_i, (txt_t, pt_t, bold_t, ls_t, sp_after_t) in enumerate(tier_specs):
        m_t = measure_text_layout(txt_t, w, pt_t, bold=bold_t, line_spacing=ls_t)
        n_lines = max(1, int(m_t["line_count"]))
        step_in = ((pt_t * MSJH_LINE_HEIGHT_EM) / 72.0) * ls_t
        if t_i < n_tiers - 1:
            total_h += n_lines * step_in + (sp_after_t / 72.0)
        else:
            total_h += float(m_t["content_height_in"])
    # Include top/bottom margins (0.02") + >=18% vertical breathing room so Tullis fill stays <= 85%
    return round(max(0.36, total_h * 1.18 + 0.06), 4)


def _render_three_tier_header(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    kicker: str,
    title: str,
    subtitle: str,
    kicker_pt: float,
    title_pt: float,
    sub_pt: float,
    kicker_hex: str,
    title_hex: str,
    sub_hex: str,
) -> None:
    """Render crisp TOP-aligned 3-tier header (`Kicker -> Title (+3pt Bold #0F172A) -> Subtitle (#64748B)`)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(max(0.45, w)), Inches(max(0.30, h)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.01)
    tf.margin_bottom = Inches(0.01)

    first_used = False
    if kicker:
        pk = tf.paragraphs[0]
        first_used = True
        pk.alignment = PP_ALIGN.LEFT
        pk.line_spacing = 1.18
        if title or subtitle:
            pk.space_after = Pt(2.5)
        _populate_paragraph_runs(pk, kicker, kicker_pt, kicker_hex, bold=True, bold_color_hex=kicker_hex)

    if title:
        pt = tf.add_paragraph() if first_used else tf.paragraphs[0]
        first_used = True
        pt.alignment = PP_ALIGN.LEFT
        pt.line_spacing = 1.18
        if subtitle:
            pt.space_after = Pt(3.0)
        _populate_paragraph_runs(pt, title, title_pt, title_hex, bold=True, bold_color_hex=title_hex)

    if subtitle:
        ps = tf.add_paragraph() if first_used else tf.paragraphs[0]
        ps.alignment = PP_ALIGN.LEFT
        ps.line_spacing = 1.22
        _populate_paragraph_runs(ps, subtitle, sub_pt, sub_hex, bold=False, bold_color_hex=title_hex)


def _get_slide_height_in(slide, default_h: float = 7.50) -> float:
    """Safely read actual slide canvas height in inches (supports non-16:9 custom slide dimensions)."""
    emu_per_in = 914400.0
    with suppress(AttributeError, TypeError, ValueError):
        sh_emu = slide.part.package.presentation_part.presentation.slide_height
        if sh_emu and float(sh_emu) > 0:
            return round(float(sh_emu) / emu_per_in, 3)
    return float(default_h)


def _resolve_zone2_height(slide, top: float, height: float | None, default_h: float) -> float:
    """
    Resolve Zone 2 container height safely:
    - When `height` is None, preserves the standard bottom anchor (`1.36 + default_h`, capped at `slide_h - 0.38"` / `7.12"` on 16:9)
      so larger Zone 1 headers shrink Zone 2 proportionally instead of colliding with Zone 3 or the canvas bottom.
    - Also respects any pre-existing Zone 3 footer shape on `slide`.
    """
    emu_per_in = 914400.0
    slide_h_in = _get_slide_height_in(slide, 7.50)
    z3_y_thresh = round(slide_h_in - 1.30, 3)
    max_bottom = min(round(slide_h_in - 0.38, 3), 1.36 + float(default_h))
    with suppress(AttributeError, TypeError, ValueError):
        for shp in slide.shapes:
            sy = float(shp.top or 0) / emu_per_in
            sw = float(shp.width or 0) / emu_per_in
            if sy >= z3_y_thresh and sw >= 8.0:
                max_bottom = min(max_bottom, sy - 0.14)
    if height is not None:
        return round(min(float(height), max(1.60, max_bottom - float(top) + 0.10)), 3)
    return round(max(1.60, min(float(default_h), max_bottom - float(top))), 3)


def _resolve_zone2_avail_bottom(
    slide,
    top: float,
    height: float | None = None,
    safe_bottom: float | None = None,
) -> float:
    """
    Compute the safe bottom boundary (inches) available for Zone 2 two-stage vertical balancing:
    - Respects any pre-existing Zone 3 footer shape (`sy >= slide_h - 1.30` and `sw >= 8.0`) with >= 0.16" clearance.
    - Without Zone 3, defaults to `slide_h - 0.28"` (`7.22"` on a standard 16:9 `7.50"` canvas).
    - When an explicit `height` is supplied by the caller, never exceeds `top + height` so legacy
      callers that draw Zone 3 *after* Zone 2 remain 100% collision-free.
    """
    emu_per_in = 914400.0
    slide_h_in = _get_slide_height_in(slide, 7.50)
    z3_y_thresh = round(slide_h_in - 1.30, 3)
    canvas_safe = round(slide_h_in - 0.28, 3)
    avail_bottom = min(float(safe_bottom), canvas_safe) if safe_bottom is not None else canvas_safe
    with suppress(AttributeError, TypeError, ValueError):
        for shp in slide.shapes:
            sy = float(shp.top or 0) / emu_per_in
            sw = float(shp.width or 0) / emu_per_in
            if sy >= z3_y_thresh and sw >= 8.0:
                avail_bottom = min(avail_bottom, sy - 0.16)
    if height is not None:
        avail_bottom = min(avail_bottom, float(top) + float(height))
    return round(max(float(top) + 1.20, avail_bottom), 3)


def _calc_zone2_expansion_factor(
    avail_h: float,
    natural_h: float,
    *,
    trigger_spare_in: float = 1.20,
    min_scale: float = 1.25,
    max_scale: float = 1.45,
) -> float:
    """
    Two-Stage Global Vertical Balance — Stage 1 / Direction 2 (Natural Expansion First):
    When Zone 2 has > `trigger_spare_in` (default 1.20") of unused vertical space relative to
    `avail_h`, returns a smooth spacing/padding expansion factor in `[min_scale, max_scale]`
    (`1.25x`..`1.45x`); otherwise returns `1.0` (no expansion).
    """
    spare = float(avail_h) - float(natural_h)
    if spare <= float(trigger_spare_in) + 1e-6:
        return 1.0
    t = min(1.0, max(0.0, (spare - float(trigger_spare_in)) / 1.20))
    return round(float(min_scale) + t * (float(max_scale) - float(min_scale)), 3)


def _apply_zone2_optical_vertical_balance(
    slide,
    start_shape_idx: int,
    avail_top: float,
    avail_bottom: float,
    *,
    trigger_spare_in: float = 0.50,
    optical_top_ratio: float = 0.40,
    max_top_buffer_in: float = 0.90,
) -> float:
    """
    Two-Stage Global Vertical Balance — Stage 2 / Direction 1 (Whole-Group Optical Centering ~40% / 60%):
    Inspects the entire group of Zone 2 shapes drawn by the current layout call (`slide.shapes[start_shape_idx:]`).
    If actual group height is shorter than `avail_bottom - avail_top` by > `trigger_spare_in` (0.50"),
    shifts the entire group downward as one unit to the optical center of gravity (~40% spare space above,
    ~60% below), capped at `<= max_top_buffer_in` (0.90") above `avail_top` and strictly clamped so
    `group_bottom + dy <= avail_bottom` (zero collision with Zone 3 or the 7.22" bottom margin).
    Preserves internal TOP-aligned natural flow inside every container.
    Returns the applied downward shift `dy_in` in inches (>= 0.0).
    """
    new_shapes = list(slide.shapes)[int(start_shape_idx):]
    if not new_shapes:
        return 0.0
    emu_per_in = 914400.0
    min_y = min(float(shp.top or 0) / emu_per_in for shp in new_shapes)
    max_b = max((float(shp.top or 0) + float(shp.height or 0)) / emu_per_in for shp in new_shapes)
    actual_h = max(0.0, max_b - min_y)
    avail_h = max(0.0, float(avail_bottom) - float(avail_top))
    spare_h = avail_h - actual_h
    if spare_h <= float(trigger_spare_in) + 1e-6:
        return 0.0

    desired_top_buf = min(float(max_top_buffer_in), spare_h * float(optical_top_ratio))
    target_top = float(avail_top) + desired_top_buf
    raw_dy = min(float(max_top_buffer_in), target_top - min_y)
    max_safe_dy = float(avail_bottom) - max_b
    dy_in = min(raw_dy, max_safe_dy)
    if dy_in <= 0.02:
        return 0.0

    dy_emu = int(round(dy_in * emu_per_in))
    for shp in new_shapes:
        shp.top = int(round(float(shp.top or 0))) + dy_emu
    return round(dy_in, 3)


def _shift_coords_y(coords, dy_in: float):
    """Shift a `(x, y, w, h)` rect tuple or list of rect tuples vertically by `dy_in` inches."""
    if not dy_in:
        return coords
    if isinstance(coords, tuple) and len(coords) == 4:
        return (coords[0], round(float(coords[1]) + float(dy_in), 3), coords[2], coords[3])
    if isinstance(coords, list):
        return [
            (r[0], round(float(r[1]) + float(dy_in), 3), r[2], r[3]) if (isinstance(r, tuple) and len(r) == 4) else r
            for r in coords
        ]
    return coords


def create_widescreen_presentation() -> Presentation:
    """Create a 16:9 widescreen Presentation (13.333" x 7.5")."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def set_slide_background(
    slide,
    bg_hex: str | None = None,
    doc_theme_id: str | None = None,
    tokens: dict[str, object] | None = None,
) -> None:
    """Set solid background color for a slide (defaults to active theme['bg_canvas'])."""
    if bg_hex is not None:
        resolved_bg = bg_hex
    elif isinstance(tokens, dict) and isinstance(tokens.get("theme"), dict):
        resolved_bg = str(tokens["theme"].get("bg_canvas", "#F8FAFC"))  # type: ignore[union-attr]
    else:
        resolved_bg = load_document_theme(doc_theme_id).get("bg_canvas", "#F8FAFC")
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb_color(resolved_bg)


def add_speaker_notes(slide, notes_text: str) -> None:
    """Write oral narrative and AST transition script into slide speaker notes."""
    if not notes_text:
        return
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = str(notes_text).strip()


def add_zone1_header(
    slide,
    chapter_pill_text: str,
    assertion_headline: str,
    pill_bg_hex: str | None = None,
    pill_fg_hex: str = "#FFFFFF",
    headline_hex: str | None = None,
    headline_pt: float = 20.5,
    subtitle_text: str | None = None,
    subtitle_pt: float = 13.0,
    subtitle_hex: str | None = None,
    right_badge_text: str | None = None,
    show_divider: bool = True,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> float:
    """
    Render Zone 1 Top Assertion Header (Module 1 Refactored — TOP-aligned natural height):
    - Eliminates old `head_lines=max(2,...)` + `MIDDLE` floating single-line gap bug (`L333`).
    - Top margin 0.15" -> Chapter pill (exact Pillow width, 9.5pt Bold) + optional right badge pill.
    - Assertion Headline (`TOP` aligned, exact height via `measure_text_layout()`).
    - Optional unboxed `subtitle_text` (`TOP` aligned, `#64748B`, `>= min_font_pt`).
    - Supports optional `tokens=None` from `build_slide_design_tokens()`.
    Returns `zone2_top_in` (recommended starting Y coordinate in inches for Zone 2).
    """
    dt, min_floor, _body_pt, typo, _sp = _resolve_engine_context(tokens, doc_theme_id)
    pal = _theme_palette(dt)
    resolved_pill_bg = pill_bg_hex if pill_bg_hex is not None else pal["primary_accent"]
    resolved_pill_fg = pal["pill_fg"] if (pill_fg_hex == "#FFFFFF" and pill_bg_hex is None and dt.get("pill_fg")) else pill_fg_hex
    resolved_headline = headline_hex if headline_hex is not None else pal["ink_primary"]
    resolved_subtitle = subtitle_hex if subtitle_hex is not None else pal["ink_muted"]
    resolved_divider = pal["divider_strong"]

    has_top_pills = False
    if chapter_pill_text and str(chapter_pill_text).strip():
        has_top_pills = True
        pill_w = calc_pill_width(chapter_pill_text, font_pt=9.5, pad_in=0.22)
        pill = _add_flat_shape(
            slide,
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.50), Inches(0.15), Inches(pill_w), Inches(0.28),
        )
        pill.adjustments[0] = 0.5
        pill.fill.solid()
        pill.fill.fore_color.rgb = hex_to_rgb_color(resolved_pill_bg)
        pill.line.fill.background()

        tf_pill = pill.text_frame
        tf_pill.word_wrap = False
        tf_pill.margin_left = Inches(0.06)
        tf_pill.margin_right = Inches(0.06)
        tf_pill.margin_top = Inches(0.02)
        tf_pill.margin_bottom = Inches(0.02)
        tf_pill.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_pill = tf_pill.paragraphs[0]
        p_pill.alignment = PP_ALIGN.CENTER
        _populate_paragraph_runs(p_pill, str(chapter_pill_text).strip(), 9.5, resolved_pill_fg, bold=True)

    if right_badge_text and str(right_badge_text).strip():
        has_top_pills = True
        rb_w = calc_pill_width(right_badge_text, font_pt=9.5, pad_in=0.22)
        rb = _add_flat_shape(
            slide,
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(max(0.50, 12.833 - rb_w)), Inches(0.15), Inches(rb_w), Inches(0.28),
        )
        rb.adjustments[0] = 0.5
        rb.fill.solid()
        rb.fill.fore_color.rgb = hex_to_rgb_color(dt.get("primary_tint", "#E0F2FE"))
        rb.line.color.rgb = hex_to_rgb_color(resolved_pill_bg)
        rb.line.width = Pt(1.0)
        tf_rb = rb.text_frame
        tf_rb.word_wrap = False
        tf_rb.margin_left = Inches(0.06)
        tf_rb.margin_right = Inches(0.06)
        tf_rb.margin_top = Inches(0.02)
        tf_rb.margin_bottom = Inches(0.02)
        tf_rb.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_rb = tf_rb.paragraphs[0]
        p_rb.alignment = PP_ALIGN.CENTER
        _populate_paragraph_runs(p_rb, str(right_badge_text).strip(), 9.5, resolved_pill_bg, bold=True)

    if isinstance(tokens, dict) and abs(float(headline_pt) - 20.5) < 1e-6:
        resolved_head_pt = float(typo["headline"])
    else:
        resolved_head_pt = max(18.0, float(headline_pt))

    head_str = str(assertion_headline or "").strip()
    m_head = measure_text_layout(head_str, box_width_in=12.333, font_pt=resolved_head_pt, bold=True, line_spacing=1.18)
    head_top = 0.50 if has_top_pills else 0.22
    head_h = round(max(0.36, float(m_head["safe_height_in"])), 3)

    headline_box = slide.shapes.add_textbox(
        Inches(0.50), Inches(head_top), Inches(12.333), Inches(head_h)
    )
    tf_head = headline_box.text_frame
    tf_head.word_wrap = True
    tf_head.margin_left = Inches(0.0)
    tf_head.margin_right = Inches(0.0)
    tf_head.margin_top = Inches(0.0)
    tf_head.margin_bottom = Inches(0.0)
    tf_head.vertical_anchor = MSO_ANCHOR.TOP
    p_head = tf_head.paragraphs[0]
    p_head.alignment = PP_ALIGN.LEFT
    p_head.line_spacing = 1.18
    _populate_paragraph_runs(p_head, head_str, resolved_head_pt, resolved_headline, bold=True)

    cursor_y = head_top + head_h

    if subtitle_text and str(subtitle_text).strip():
        if isinstance(tokens, dict) and abs(float(subtitle_pt) - 13.0) < 1e-6:
            resolved_sub_pt = float(typo["subtitle"])
        else:
            resolved_sub_pt = max(min_floor, float(subtitle_pt))
        sub_str = str(subtitle_text).strip()
        m_sub = measure_text_layout(sub_str, box_width_in=12.333, font_pt=resolved_sub_pt, bold=False, line_spacing=1.22)
        sub_top = round(cursor_y + 0.03, 3)
        sub_h = round(max(0.24, float(m_sub["safe_height_in"])), 3)
        sub_box = slide.shapes.add_textbox(
            Inches(0.50), Inches(sub_top), Inches(12.333), Inches(sub_h)
        )
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = Inches(0.0)
        tf_sub.margin_right = Inches(0.0)
        tf_sub.margin_top = Inches(0.0)
        tf_sub.margin_bottom = Inches(0.0)
        tf_sub.vertical_anchor = MSO_ANCHOR.TOP
        p_sub = tf_sub.paragraphs[0]
        p_sub.alignment = PP_ALIGN.LEFT
        p_sub.line_spacing = 1.22
        _populate_paragraph_runs(
            p_sub,
            sub_str,
            resolved_sub_pt,
            resolved_subtitle,
            bold=False,
            bold_color_hex=resolved_headline,
        )
        cursor_y = sub_top + sub_h

    divider_y = round(cursor_y + 0.06, 3)
    if show_divider:
        divider = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(0.50), Inches(divider_y), Inches(12.333), Inches(0.015),
        )
        divider.fill.solid()
        divider.fill.fore_color.rgb = hex_to_rgb_color(resolved_divider)
        divider.line.fill.background()
        return round(divider_y + 0.145, 3)

    return round(cursor_y + 0.14, 3)


def add_zone3_footer(
    slide,
    takeaway_text: str | None,
    bg_hex: str | None = None,
    border_hex: str | None = None,
    fg_hex: str = "#F8FAFC",
    font_pt: float = 13.0,
    style: str = "dark_banner",
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> None:
    """
    Render OPTIONAL Zone 3 Bottom Action Takeaway (floor >= min_font_pt, ceiling UNLOCKED).
    If `takeaway_text` is empty/None, renders nothing (preserving clean bottom breathing room).
    `style`:
      - "dark_banner" (default): high-contrast dark slate takeaway bar.
      - "subtle_line": lightweight left-accented takeaway strip without heavy dark rectangle.
    """
    if not takeaway_text or not str(takeaway_text).strip():
        return

    dt, _min_floor, resolved_pt, _typo, _sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=font_pt, default_body_pt=13.0, caller_default_pt=13.0
    )
    tk_str = str(takeaway_text).strip()
    usable_w = 12.093 if style == "subtle_line" else 11.933
    m_tk = measure_text_layout(tk_str, box_width_in=usable_w, font_pt=resolved_pt, bold=True, line_spacing=1.22)
    banner_h = round(max(0.46, float(m_tk["safe_height_in"]) + 0.14), 3)
    banner_top = max(5.95, round(7.28 - banner_h, 3))
    resolved_border = border_hex if border_hex is not None else dt.get("primary_accent", "#0284C7")

    if style == "subtle_line":
        bar = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(0.50), Inches(banner_top + 0.05), Inches(0.06), Inches(max(0.28, banner_h - 0.10)),
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = hex_to_rgb_color(resolved_border)
        bar.line.fill.background()

        tb = slide.shapes.add_textbox(
            Inches(0.66), Inches(banner_top), Inches(12.173), Inches(banner_h)
        )
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.04)
        tf.margin_right = Inches(0.04)
        tf.margin_top = Inches(0.02)
        tf.margin_bottom = Inches(0.02)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE if int(m_tk["line_count"]) <= 1 else MSO_ANCHOR.TOP
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        p.line_spacing = 1.22
        ink_hex = dt.get("ink_primary", "#0F172A") if fg_hex == "#F8FAFC" else fg_hex
        _populate_paragraph_runs(p, tk_str, resolved_pt, ink_hex, bold=True, bold_color_hex=resolved_border)
        return

    resolved_bg = bg_hex if bg_hex is not None else dt.get("bookend_dark_bg", dt.get("ink_primary", "#0F172A"))
    banner = _add_flat_shape(
        slide,
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.50), Inches(banner_top), Inches(12.333), Inches(banner_h),
    )
    banner.adjustments[0] = 0.14
    banner.fill.solid()
    banner.fill.fore_color.rgb = hex_to_rgb_color(resolved_bg)
    banner.line.color.rgb = hex_to_rgb_color(resolved_border)
    banner.line.width = Pt(1.2)

    tf = banner.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.20)
    tf.margin_right = Inches(0.20)
    tf.margin_top = Inches(0.05)
    tf.margin_bottom = Inches(0.05)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE if int(m_tk["line_count"]) <= 1 else MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.line_spacing = 1.22
    _populate_paragraph_runs(p, tk_str, resolved_pt, fg_hex, bold=True)


# -------------------------------------------------------------------------
# Family 1 | Bookend & Impact (`F1-A` S0, `F1-B` S13, `F1-C` Hero / S14)
# -------------------------------------------------------------------------

def add_bookend_slide_s0(
    prs: Presentation,
    badge_text: str = "EXECUTIVE BRIEFING",
    main_title: str = "",
    subtitle_text: str = "",
    kpi_cards: list[dict[str, str]] | None = None,
    speaker_notes: str | None = None,
    bg_hex: str | None = None,
    accent_hex: str | None = None,
    title_pt: float = 28.0,
    subtitle_pt: float = 14.5,
    footer_text: str | None = None,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
    **kwargs,
):
    """
    [F1-A / S0] Add a Dark Bookend Slide (Slide 1 Cover or Final Slide Peak-End Summary).
    Note: First argument is `prs` (Presentation), NOT `slide`. Returns newly created `slide`.
    All content text enforces `>= min_font_pt` with Content-Driven TOP-aligned KPI cards.
    """
    dt, min_floor, body_pt, typo, _sp = _resolve_engine_context(tokens, doc_theme_id)
    resolved_bg = bg_hex if bg_hex is not None else dt.get("bookend_dark_bg", "#0F172A")
    resolved_accent = accent_hex if accent_hex is not None else dt.get("bookend_accent", "#38BDF8")

    if not main_title and "title" in kwargs:
        main_title = str(kwargs["title"])
    if not subtitle_text and "subtitle" in kwargs:
        subtitle_text = str(kwargs["subtitle"])
    if kpi_cards is None and "kpi_callouts" in kwargs:
        raw_kpis = kwargs["kpi_callouts"]
        if isinstance(raw_kpis, list):
            kpi_cards = [
                c
                if isinstance(c, dict)
                else {"title": str(c[0]), "value": str(c[1]), "desc": str(c[2]) if len(c) > 2 else ""}
                for c in raw_kpis
            ]

    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide, resolved_bg)

    if badge_text and str(badge_text).strip():
        pill_w = calc_pill_width(badge_text, font_pt=10.5, pad_in=0.28)
        pill = _add_flat_shape(
            slide,
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.65), Inches(0.55), Inches(pill_w), Inches(0.34),
        )
        pill.adjustments[0] = 0.5
        pill.fill.solid()
        pill.fill.fore_color.rgb = hex_to_rgb_color("#1E293B")
        pill.line.color.rgb = hex_to_rgb_color(resolved_accent)
        pill.line.width = Pt(1.2)
        tf_p = pill.text_frame
        tf_p.word_wrap = False
        tf_p.margin_left = Inches(0.08)
        tf_p.margin_right = Inches(0.08)
        tf_p.margin_top = Inches(0.02)
        tf_p.margin_bottom = Inches(0.02)
        tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
        p0 = tf_p.paragraphs[0]
        p0.alignment = PP_ALIGN.CENTER
        _populate_paragraph_runs(p0, str(badge_text).strip(), 10.5, resolved_accent, bold=True)

    if isinstance(tokens, dict) and abs(float(title_pt) - 28.0) < 1e-6:
        resolved_title_pt = float(typo["bookend_title"])
    else:
        resolved_title_pt = max(22.0, float(title_pt))

    if isinstance(tokens, dict) and abs(float(subtitle_pt) - 14.5) < 1e-6:
        resolved_sub_pt = max(min_floor, _round_half_pt(body_pt + 1.0))
    else:
        resolved_sub_pt = max(min_floor, float(subtitle_pt))

    has_cards = bool(kpi_cards)
    title_str = str(main_title or "").strip()
    m_title = measure_text_layout(title_str, box_width_in=12.033, font_pt=resolved_title_pt, bold=True, line_spacing=1.20)
    title_top = 1.08 if has_cards else 1.85
    title_h = round(min(2.10 if has_cards else 2.40, max(0.72, float(m_title["safe_height_in"]) + 0.08)), 3)

    t_box = slide.shapes.add_textbox(Inches(0.65), Inches(title_top), Inches(12.033), Inches(title_h))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = Inches(0.0)
    tf_t.margin_right = Inches(0.0)
    tf_t.vertical_anchor = MSO_ANCHOR.TOP if has_cards else MSO_ANCHOR.MIDDLE
    pt = tf_t.paragraphs[0]
    pt.alignment = PP_ALIGN.LEFT
    pt.line_spacing = 1.20
    _populate_paragraph_runs(pt, title_str, resolved_title_pt, "#F8FAFC", bold=True)

    cursor_y = title_top + title_h
    if subtitle_text and str(subtitle_text).strip():
        sub_str = str(subtitle_text).strip()
        m_sub = measure_text_layout(sub_str, box_width_in=12.033, font_pt=resolved_sub_pt, bold=False, line_spacing=1.30)
        sub_top = round(cursor_y + 0.14, 3)
        sub_h = round(min(1.25 if has_cards else 1.50, max(0.40, float(m_sub["safe_height_in"]) + 0.06)), 3)
        s_box = slide.shapes.add_textbox(Inches(0.65), Inches(sub_top), Inches(12.033), Inches(sub_h))
        tf_s = s_box.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = Inches(0.0)
        tf_s.margin_right = Inches(0.0)
        tf_s.vertical_anchor = MSO_ANCHOR.TOP
        ps = tf_s.paragraphs[0]
        ps.alignment = PP_ALIGN.LEFT
        ps.line_spacing = 1.30
        _populate_paragraph_runs(ps, sub_str, resolved_sub_pt, "#CBD5E1", bold=False, bold_color_hex="#FFFFFF")
        cursor_y = sub_top + sub_h

    footer_pt = max(min_floor, _round_half_pt(body_pt - 0.5))
    footer_y = 6.76
    if footer_text and str(footer_text).strip():
        m_f = measure_text_layout(str(footer_text).strip(), 12.033, footer_pt, bold=False, line_spacing=1.20)
        f_h = round(max(0.36, float(m_f["safe_height_in"]) + 0.04), 3)
        footer_y = round(7.24 - f_h, 3)
        f_box = slide.shapes.add_textbox(Inches(0.65), Inches(footer_y), Inches(12.033), Inches(f_h))
        tf_f = f_box.text_frame
        tf_f.word_wrap = True
        tf_f.margin_left = Inches(0.0)
        tf_f.margin_right = Inches(0.0)
        tf_f.vertical_anchor = MSO_ANCHOR.MIDDLE if int(m_f["line_count"]) <= 1 else MSO_ANCHOR.TOP
        pf = tf_f.paragraphs[0]
        pf.alignment = PP_ALIGN.LEFT
        _populate_paragraph_runs(pf, str(footer_text).strip(), footer_pt, "#94A3B8", bold=False, bold_color_hex=resolved_accent)

    if kpi_cards:
        n = min(3, len(kpi_cards))
        total_w = 12.033
        gap = 0.28
        card_w = (total_w - gap * (n - 1)) / n
        cy = round(max(3.15, cursor_y + 0.28), 3)
        max_avail_ch = max(1.20, round((footer_y - 0.20 if footer_text else 7.05) - cy, 3))
        card_title_pt = max(min_floor, _round_half_pt(body_pt))
        card_val_pt = max(19.0, _round_half_pt(body_pt + 5.5))
        card_desc_pt = max(min_floor, _round_half_pt(body_pt - 0.5 if body_pt >= 13.5 else body_pt))

        norm_cards: list[dict[str, object]] = []
        req_card_h = 0.0
        for raw_card in kpi_cards[:n]:
            if isinstance(raw_card, dict):
                card = raw_card
            elif isinstance(raw_card, (list, tuple)) and len(raw_card) >= 2:
                card = (
                    {"title": raw_card[0], "desc": raw_card[1]}
                    if len(raw_card) == 2
                    else {"title": raw_card[0], "value": raw_card[1], "desc": raw_card[2]}
                )
            else:
                card = {"title": str(raw_card), "desc": ""}
            norm_cards.append(card)
            inner_w = max(0.8, card_w - 0.44)
            ch_need = 0.36
            if card.get("title"):
                ch_need += float(measure_text_layout(str(card["title"]), inner_w, card_title_pt, bold=True, line_spacing=1.20)["content_height_in"]) + 0.08
            if card.get("value"):
                ch_need += float(measure_text_layout(str(card["value"]), inner_w, card_val_pt, bold=True, line_spacing=1.18)["content_height_in"]) + 0.10
            if card.get("desc"):
                ch_need += float(measure_text_layout(str(card["desc"]), inner_w, card_desc_pt, bold=False, line_spacing=1.30)["content_height_in"]) + 0.08
            req_card_h = max(req_card_h, ch_need)

        ch = round(min(max_avail_ch, max(min(max_avail_ch, 2.05), req_card_h + 0.24)), 3)
        for idx, card in enumerate(norm_cards):
            cx = 0.65 + idx * (card_w + gap)
            c_acc = str(card.get("accent", resolved_accent))
            is_spot = bool(card.get("is_spotlight", idx == 0 and n > 1))

            box = _add_flat_shape(
                slide,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(cx), Inches(cy), Inches(card_w), Inches(ch),
            )
            box.adjustments[0] = 0.05
            box.fill.solid()
            box.fill.fore_color.rgb = hex_to_rgb_color("#1E293B")
            box.line.color.rgb = hex_to_rgb_color(c_acc if is_spot else "#334155")
            box.line.width = Pt(1.6 if is_spot else 1.0)

            strip = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(cx + 0.18), Inches(cy + 0.01), Inches(card_w - 0.36), Inches(0.055 if is_spot else 0.035),
            )
            strip.fill.solid()
            strip.fill.fore_color.rgb = hex_to_rgb_color(c_acc if is_spot else "#475569")
            strip.line.fill.background()

            tb = slide.shapes.add_textbox(
                Inches(cx + 0.22), Inches(cy + 0.18), Inches(card_w - 0.44), Inches(max(0.8, ch - 0.28))
            )
            tf_c = tb.text_frame
            tf_c.word_wrap = True
            tf_c.vertical_anchor = MSO_ANCHOR.TOP
            tf_c.margin_left = Inches(0.02)
            tf_c.margin_right = Inches(0.02)
            tf_c.margin_top = Inches(0.02)
            tf_c.margin_bottom = Inches(0.02)

            p_title = tf_c.paragraphs[0]
            p_title.alignment = PP_ALIGN.LEFT
            p_title.space_after = Pt(6)
            _populate_paragraph_runs(p_title, str(card.get("title", "")).strip(), card_title_pt, c_acc if is_spot else "#94A3B8", bold=True)

            if card.get("value"):
                p_val = tf_c.add_paragraph()
                p_val.alignment = PP_ALIGN.LEFT
                p_val.space_after = Pt(7)
                _populate_paragraph_runs(p_val, str(card.get("value", "")).strip(), card_val_pt, "#FFFFFF", bold=True)

            if card.get("desc"):
                p_desc = tf_c.add_paragraph()
                p_desc.alignment = PP_ALIGN.LEFT
                p_desc.line_spacing = 1.30
                _populate_paragraph_runs(p_desc, str(card.get("desc", "")).strip(), card_desc_pt, "#E2E8F0", bold=False, bold_color_hex="#FFFFFF")

    if speaker_notes:
        add_speaker_notes(slide, speaker_notes)
    return slide


def draw_section_divider_slide(
    slide,
    section_num: str | int,
    section_title: str,
    subtitle_text: str = "",
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> None:
    """
    [F1-B / S13] Render an Ultra-Minimal Editorial Section Divider Slide (ZERO card boxes, high breathing whitespace).
    Features oversized typographic section numeral, crisp accent rule, large bold section title, and optional subtitle.
    """
    dt, min_floor, body_pt, typo, _sp = _resolve_engine_context(tokens, doc_theme_id)
    primary_acc = dt.get("primary_accent", "#0284C7")
    ink_pri = dt.get("ink_primary", "#0F172A")
    ink_muted = dt.get("ink_muted", "#64748B")
    soft_num_hex = _blend_hex(primary_acc, dt.get("bg_canvas", "#F8FAFC"), 0.22)

    raw_num = str(section_num).strip()
    if raw_num.isdigit():
        num_str = f"{int(raw_num):02d}"
    else:
        num_str = raw_num or "01"

    title_str = str(section_title or "").strip()
    sub_str = str(subtitle_text or "").strip()

    num_pt = 68.0
    title_pt = max(32.0, _round_half_pt(float(typo["bookend_title"]) + 4.0))
    sub_pt = max(min_floor, _round_half_pt(body_pt + 2.0))

    content_x = 1.15
    content_w = 10.80
    m_num = measure_text_layout(num_str, content_w, num_pt, bold=True, line_spacing=1.08)
    m_title = measure_text_layout(title_str, content_w, title_pt, bold=True, line_spacing=1.18)
    m_sub = measure_text_layout(sub_str, content_w, sub_pt, bold=False, line_spacing=1.30) if sub_str else None

    num_h = round(max(0.95, float(m_num["safe_height_in"])), 3)
    title_h = round(max(0.60, float(m_title["safe_height_in"]) + 0.04), 3)
    sub_h = round(float(m_sub["safe_height_in"]) + 0.04, 3) if m_sub else 0.0

    total_block_h = num_h + 0.22 + title_h + (0.20 + sub_h if sub_str else 0.0)
    start_y = round(max(1.15, (7.5 - total_block_h) * 0.46), 3)

    # Left vertical architectural hairline anchored to the title block
    v_accent = _add_flat_shape(
        slide,
        MSO_SHAPE.RECTANGLE,
        Inches(0.68), Inches(start_y + num_h + 0.08), Inches(0.065), Inches(max(0.80, title_h + (0.20 + sub_h if sub_str else 0.0) + 0.14)),
    )
    v_accent.fill.solid()
    v_accent.fill.fore_color.rgb = hex_to_rgb_color(primary_acc)
    v_accent.line.fill.background()

    # Oversized section numeral
    nb = slide.shapes.add_textbox(Inches(content_x), Inches(start_y), Inches(content_w), Inches(num_h))
    tf_n = nb.text_frame
    tf_n.word_wrap = True
    tf_n.vertical_anchor = MSO_ANCHOR.TOP
    tf_n.margin_left = Inches(0.0)
    tf_n.margin_right = Inches(0.0)
    pn = tf_n.paragraphs[0]
    pn.alignment = PP_ALIGN.LEFT
    _populate_paragraph_runs(pn, num_str, num_pt, soft_num_hex, bold=True)

    # Crisp short horizontal accent bar
    rule_y = round(start_y + num_h + 0.04, 3)
    h_rule = _add_flat_shape(
        slide,
        MSO_SHAPE.RECTANGLE,
        Inches(content_x), Inches(rule_y), Inches(1.25), Inches(0.06),
    )
    h_rule.fill.solid()
    h_rule.fill.fore_color.rgb = hex_to_rgb_color(primary_acc)
    h_rule.line.fill.background()

    # Large bold section title
    title_y = round(rule_y + 0.22, 3)
    tb = slide.shapes.add_textbox(Inches(content_x), Inches(title_y), Inches(content_w), Inches(title_h))
    tf_t = tb.text_frame
    tf_t.word_wrap = True
    tf_t.vertical_anchor = MSO_ANCHOR.TOP
    tf_t.margin_left = Inches(0.0)
    tf_t.margin_right = Inches(0.0)
    pt_p = tf_t.paragraphs[0]
    pt_p.alignment = PP_ALIGN.LEFT
    pt_p.line_spacing = 1.18
    _populate_paragraph_runs(pt_p, title_str, title_pt, ink_pri, bold=True)

    if sub_str:
        sub_y = round(title_y + title_h + 0.18, 3)
        sb = slide.shapes.add_textbox(Inches(content_x), Inches(sub_y), Inches(content_w), Inches(sub_h))
        tf_s = sb.text_frame
        tf_s.word_wrap = True
        tf_s.vertical_anchor = MSO_ANCHOR.TOP
        tf_s.margin_left = Inches(0.0)
        tf_s.margin_right = Inches(0.0)
        ps = tf_s.paragraphs[0]
        ps.alignment = PP_ALIGN.LEFT
        ps.line_spacing = 1.30
        _populate_paragraph_runs(ps, sub_str, sub_pt, ink_muted, bold=False, bold_color_hex=ink_pri)


# -------------------------------------------------------------------------
# Family 2 | Structured Narrative (`F2-A` S1+S2, `F2-B` S8, `F2-C` S9)
# -------------------------------------------------------------------------

def draw_parallel_row_cards(
    slide,
    cards_spec: list[dict[str, object]],
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    gap: float = 0.26,
    spotlight_idx: int | None = None,
    body_font_pt: float | None = None,
    title_font_pt: float | None = None,
    width_ratios: list[float] | None = None,
    card_style: str = "clean_card",
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> list[tuple[float, float, float, float]]:
    """
    [F2-A / S1 + S2] Render 2, 3, or 4 parallel columns in Zone 2 (Module 1 & 2 Upgraded):
    - `card_style`:
      * `"clean_card"`: single-layer clean white card with de-noised spotlight (soft tint + single top bar + deep ink title).
      * `"minimal_column"`: borderless column with oversized soft numeral (`01`/`02`/`03`), short accent bar, and hairline gap dividers.
      * `"borderless_centerline"`: borderless contrast layout with crisp vertical centerline divider (ideal for 2-column S1).
    - Uses `measure_text_layout()`, `MSO_ANCHOR.TOP` natural flow stacking (abolishing `slot_h` equal splits),
      3-tier headers (`Kicker -> Title (+3pt) -> Subtitle`), independent 2-paragraph Lead/Body rows,
      Content-Driven Height, and eliminates the L789 unequal-row ghost separator bug.
    """
    n_cols = len(cards_spec)
    if n_cols == 0:
        return []

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.20)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    default_body = 13.5 if n_cols <= 2 else (12.5 if n_cols == 3 else 12.0)
    dt, min_floor, resolved_pt, typo, sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=default_body
    )
    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_primary = pal["primary_accent"]
    theme_border = pal["border_card"]
    theme_card_bg = pal["bg_card"]
    theme_canvas = pal["bg_canvas"]
    theme_ink_pri = pal["ink_primary"]
    theme_ink_body = pal["ink_body"]
    theme_ink_muted = pal["ink_muted"]
    div_subtle = pal["divider_subtle"]
    div_strong = pal["divider_strong"]
    muted_bar = pal["muted_bar"]
    muted_acc = pal["muted_accent"]

    style_norm = str(card_style or "clean_card").strip().lower()
    if style_norm not in ("clean_card", "minimal_column", "borderless_centerline"):
        style_norm = "clean_card"

    if title_font_pt is None:
        resolved_title_pt = float(typo["card_title"])
    else:
        resolved_title_pt = max(min_floor + 1.0, float(title_font_pt))
    kicker_pt = float(typo["kicker"])
    sub_pt = float(typo["subtitle"])
    lead_pt = float(typo["lead"])
    ls = float(sp.get("line_spacing", 1.30))
    base_item_gap = 0.22 if n_cols <= 2 else 0.18

    if style_norm in ("minimal_column", "borderless_centerline") and gap < 0.34:
        eff_gap = 0.42 if style_norm == "borderless_centerline" else 0.36
    else:
        eff_gap = float(gap)

    if width_ratios and len(width_ratios) == n_cols:
        tot_r = sum(float(r) for r in width_ratios) or float(n_cols)
        usable_w = total_width - eff_gap * (n_cols - 1)
        col_widths = [usable_w * (float(r) / tot_r) for r in width_ratios]
    else:
        w = (total_width - eff_gap * (n_cols - 1)) / n_cols
        col_widths = [w] * n_cols

    pad_x = 0.20 if style_norm == "clean_card" else 0.10
    num_band_h = 0.56 if style_norm == "minimal_column" else 0.0
    top_inset = (0.14 if style_norm == "clean_card" else 0.06) + num_band_h

    # Pre-measure 3-tier headers across all columns for aligned horizontal rhythm
    parsed_cols: list[dict[str, object]] = []
    max_hdr_h = 0.0
    for idx_c, card in enumerate(cards_spec):
        cw = col_widths[idx_c]
        inner_w = max(0.55, cw - 2.0 * pad_x)
        if style_norm == "minimal_column":
            kicker = _first_non_empty_str(card, "kicker", "badge", "step")
        else:
            kicker = _first_non_empty_str(card, "kicker", "badge", "step", "num")
        title = _first_non_empty_str(card, "title", "heading", "label", "name")
        subtitle = _first_non_empty_str(card, "subtitle", "sub")
        if kicker and not title:
            title, kicker = kicker, ""

        # Prevent duplicate leading numeral in minimal_column when title already begins with e.g. "01 "
        col_num_str = ""
        if style_norm == "minimal_column":
            has_explicit_num = isinstance(card, dict) and "num" in card and card.get("num") is not None
            if has_explicit_num:
                col_num_str = str(card.get("num") or "").strip()
            else:
                m_short_num = re.match(r"^\s*(0?\d{1,2})(?:[\.\)、:：\-—–\|｜\s]+)(.+)$", title)
                if m_short_num and _LEADING_INDEX_PREFIX_RE.match(title):
                    col_num_str = m_short_num.group(1).strip()
                    title = m_short_num.group(2).strip()
                elif _LEADING_INDEX_PREFIX_RE.match(title):
                    col_num_str = ""
                else:
                    col_num_str = f"{idx_c + 1:02d}"

        hdr_h_c = _measure_three_tier_header(kicker, title, subtitle, inner_w, kicker_pt, resolved_title_pt, sub_pt)
        max_hdr_h = max(max_hdr_h, hdr_h_c)

        card_lead = _first_non_empty_str(card, "lead")
        if card_lead == title:
            card_lead = ""
        raw_pairs = _extract_lead_body_items(card, extra_lead=card_lead)
        norm_rows: list[tuple[str, str, float]] = []
        for lead_s, body_s in raw_pairs:
            item_h = _measure_lead_body_item_height(lead_s, body_s, inner_w, lead_pt, resolved_pt, line_spacing=ls)
            norm_rows.append((lead_s, body_s, item_h))

        parsed_cols.append({
            "card": card,
            "cw": cw,
            "inner_w": inner_w,
            "num_str": col_num_str,
            "kicker": kicker,
            "title": title,
            "subtitle": subtitle,
            "rows": norm_rows,
        })

    header_h = round(min(resolved_h * 0.44, max(0.46, max_hdr_h)), 3)
    rule_gap = 0.08
    body_gap = 0.14
    nat_body_top = round(top + top_inset + header_h + rule_gap + body_gap, 3)

    # Measure natural Content-Driven Height first to check Direction 2 (natural expansion)
    nat_max_col_body_h = 0.0
    for col_info in parsed_cols:
        r_list: list[tuple[str, str, float]] = col_info["rows"]  # type: ignore[assignment]
        if r_list:
            stack_h = sum(r[2] for r in r_list) + base_item_gap * max(0, len(r_list) - 1)
            nat_max_col_body_h = max(nat_max_col_body_h, stack_h)

    nat_total_h = (nat_body_top - top) + nat_max_col_body_h + 0.24
    exp_factor = _calc_zone2_expansion_factor(avail_h, nat_total_h)
    if exp_factor > 1.0:
        rule_gap = round(rule_gap * exp_factor, 3)
        body_gap = round(body_gap * exp_factor, 3)
        base_item_gap = round(base_item_gap * exp_factor, 3)

    max_card_budget_h = max(resolved_h, avail_h) if exp_factor > 1.0 else resolved_h
    rule_y = round(top + top_inset + header_h + rule_gap, 3)
    body_top = round(rule_y + body_gap, 3)
    avail_body_h = max(0.90, round(top + max_card_budget_h - body_top - 0.16, 3))

    # Compute Content-Driven Height (pushes dead whitespace outside boxes!)
    max_col_body_h = 0.0
    for col_info in parsed_cols:
        r_list = col_info["rows"]  # type: ignore[assignment]
        if r_list:
            stack_h = sum(r[2] for r in r_list) + base_item_gap * max(0, len(r_list) - 1)
            max_col_body_h = max(max_col_body_h, stack_h)

    bot_pad = round(0.24 * exp_factor, 3) if exp_factor > 1.0 else 0.24
    needed_total_h = (body_top - top) + max_col_body_h + bot_pad
    actual_card_h = round(min(max_card_budget_h, max(min(max_card_budget_h, 2.30), needed_total_h)), 3)

    coords: list[tuple[float, float, float, float]] = []
    cur_x = left
    for idx, col_info in enumerate(parsed_cols):
        card: dict[str, object] = col_info["card"]  # type: ignore[assignment]
        cw = float(col_info["cw"])
        inner_w = float(col_info["inner_w"])
        is_spot = (spotlight_idx == idx) if spotlight_idx is not None else bool(card.get("is_spotlight", False))
        accent_hex = str(card.get("accent", theme_primary if is_spot else muted_acc))
        spot_wash = _blend_hex(accent_hex, theme_card_bg, 0.14 if is_dark_theme else 0.06)

        if style_norm == "clean_card":
            card_fill = str(card.get("bg", spot_wash if is_spot else theme_card_bg))
            card_border = _blend_hex(accent_hex, theme_border, 0.45 if is_dark_theme else 0.35) if is_spot else theme_border
            base_rect = _add_flat_shape(
                slide,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(cur_x), Inches(top), Inches(cw), Inches(actual_card_h),
            )
            base_rect.adjustments[0] = 0.03
            base_rect.fill.solid()
            base_rect.fill.fore_color.rgb = hex_to_rgb_color(card_fill)
            base_rect.line.color.rgb = hex_to_rgb_color(card_border)
            base_rect.line.width = Pt(1.25 if is_spot else 1.0)

            top_strip = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(cur_x + 0.14), Inches(top + 0.01), Inches(max(0.4, cw - 0.28)), Inches(0.06 if is_spot else 0.035),
            )
            top_strip.fill.solid()
            top_strip.fill.fore_color.rgb = hex_to_rgb_color(accent_hex if is_spot else muted_bar)
            top_strip.line.fill.background()

        elif style_norm == "minimal_column":
            num_str = str(col_info.get("num_str", "")).strip()
            num_color = _blend_hex(accent_hex, theme_canvas, 0.45) if is_spot else muted_bar
            if num_str:
                nb = slide.shapes.add_textbox(
                    Inches(cur_x + pad_x), Inches(top), Inches(inner_w), Inches(0.46)
                )
                tf_n = nb.text_frame
                tf_n.word_wrap = False
                tf_n.vertical_anchor = MSO_ANCHOR.TOP
                tf_n.margin_left = Inches(0.0)
                tf_n.margin_top = Inches(0.0)
                pn = tf_n.paragraphs[0]
                pn.alignment = PP_ALIGN.LEFT
                _populate_paragraph_runs(pn, num_str, 30.0, num_color, bold=True)

            short_bar = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(cur_x + pad_x), Inches(top + 0.48), Inches(0.68 if is_spot else 0.45), Inches(0.055 if is_spot else 0.035),
            )
            short_bar.fill.solid()
            short_bar.fill.fore_color.rgb = hex_to_rgb_color(accent_hex if is_spot else muted_acc)
            short_bar.line.fill.background()

            if idx > 0:
                div_x = cur_x - eff_gap / 2.0
                v_div = _add_flat_shape(
                    slide,
                    MSO_SHAPE.RECTANGLE,
                    Inches(div_x), Inches(top + 0.08), Inches(0.012), Inches(max(1.2, actual_card_h - 0.16)),
                )
                v_div.fill.solid()
                v_div.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
                v_div.line.fill.background()

        else:  # borderless_centerline
            if is_spot:
                wash = _add_flat_shape(
                    slide,
                    MSO_SHAPE.RECTANGLE,
                    Inches(cur_x), Inches(top), Inches(cw), Inches(actual_card_h),
                )
                wash.fill.solid()
                wash.fill.fore_color.rgb = hex_to_rgb_color(_blend_hex(accent_hex, theme_canvas, 0.14 if is_dark_theme else 0.055))
                wash.line.fill.background()

            top_bar = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(cur_x + pad_x), Inches(top + 0.01), Inches(1.20 if is_spot else 0.72), Inches(0.06 if is_spot else 0.04),
            )
            top_bar.fill.solid()
            top_bar.fill.fore_color.rgb = hex_to_rgb_color(accent_hex if is_spot else muted_acc)
            top_bar.line.fill.background()

            if idx > 0:
                div_x = cur_x - eff_gap / 2.0
                v_div = _add_flat_shape(
                    slide,
                    MSO_SHAPE.RECTANGLE,
                    Inches(div_x), Inches(top + 0.04), Inches(0.018), Inches(max(1.2, actual_card_h - 0.08)),
                )
                v_div.fill.solid()
                v_div.fill.fore_color.rgb = hex_to_rgb_color(div_strong)
                v_div.line.fill.background()

        # 3-tier header (TOP aligned; deep ink title even on spotlight to prevent 5x blue noise)
        _render_three_tier_header(
            slide,
            x=cur_x + pad_x,
            y=top + top_inset,
            w=inner_w,
            h=header_h + 0.04,
            kicker=str(col_info["kicker"]),
            title=str(col_info["title"]),
            subtitle=str(col_info["subtitle"]),
            kicker_pt=kicker_pt,
            title_pt=resolved_title_pt,
            sub_pt=sub_pt,
            kicker_hex=accent_hex if is_spot else theme_ink_muted,
            title_hex=theme_ink_pri,
            sub_hex=theme_ink_muted,
        )

        # Clean neutral hairline under header
        hdr_rule = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(cur_x + pad_x), Inches(rule_y), Inches(inner_w), Inches(0.012),
        )
        hdr_rule.fill.solid()
        hdr_rule.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
        hdr_rule.line.fill.background()

        # TOP-aligned natural flow stacking (ZERO slot_h equal split, ZERO ghost separators!)
        r_list = col_info["rows"]  # type: ignore[assignment]
        if r_list:
            raw_sum_h = sum(r[2] for r in r_list)
            if len(r_list) > 1:
                eff_item_gap = min(base_item_gap, max(0.08, (avail_body_h - raw_sum_h) / (len(r_list) - 1)))
            else:
                eff_item_gap = 0.0

            cur_y = body_top
            card_bot_limit = top + actual_card_h - 0.08
            for r_i, (lead_s, body_s, item_h) in enumerate(r_list):
                if cur_y >= card_bot_limit - 0.16:
                    break
                if r_i > 0:
                    sep_y = round(cur_y - eff_item_gap * 0.52, 3)
                    sep = _add_flat_shape(
                        slide,
                        MSO_SHAPE.RECTANGLE,
                        Inches(cur_x + pad_x), Inches(sep_y), Inches(inner_w), Inches(0.008),
                    )
                    sep.fill.solid()
                    sep.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
                    sep.line.fill.background()

                rem_h = max(0.20, card_bot_limit - cur_y)
                box_h = round(min(rem_h, item_h + 0.02), 3)
                _render_lead_body_box(
                    slide,
                    x=cur_x + pad_x,
                    y=cur_y,
                    w=inner_w,
                    h=box_h,
                    lead=lead_s,
                    body=body_s,
                    lead_pt=lead_pt,
                    body_pt=resolved_pt,
                    lead_hex=theme_ink_pri,
                    body_hex=theme_ink_body,
                    bold_color_hex=theme_ink_pri,
                    line_spacing=ls,
                )
                cur_y = round(cur_y + box_h + eff_item_gap, 3)

        coords.append((round(cur_x, 3), round(top, 3), round(cw, 3), round(actual_card_h, 3)))
        cur_x += cw + eff_gap

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y(coords, dy_in)


def draw_editorial_split_rows_s8(
    slide,
    rows_spec: Sequence[dict[str, object]],
    left_ratio: float = 0.28,
    spotlight_idx: int | None = None,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    body_font_pt: float | None = None,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> list[tuple[float, float, float, float]]:
    """
    [F2-B / S8] Render Swiss Editorial Grid "Left Label / Right Expand" Horizontal Rows (ZERO card boxes):
    - Crisp horizontal hairlines separate 2–4 rows.
    - Left column (`left_ratio`, default 28%): index numeral + bold category title + optional subtitle.
    - Right column (`1 - left_ratio`, default 72%): expanded narrative or Lead/Body points flowing TOP-aligned.
    - Spotlight row gets a single left accent bar + ultra-subtle borderless wash.
    """
    n_rows = len(rows_spec)
    if n_rows == 0:
        return []

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.26)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, _min_floor, resolved_pt, typo, sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.5
    )
    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_pri = pal["primary_accent"]
    theme_canvas = pal["bg_canvas"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    ink_muted = pal["ink_muted"]
    div_strong = pal["divider_strong"]
    div_subtle = pal["divider_subtle"]
    muted_acc = pal["muted_accent"]

    ratio = max(0.20, min(0.42, float(left_ratio)))
    gutter = 0.36
    left_w = round((total_width - gutter) * ratio, 3)
    right_w = round(total_width - gutter - left_w, 3)

    title_pt = _round_half_pt(resolved_pt + 2.5)
    lead_pt = float(typo["lead"])
    kicker_pt = float(typo["kicker"])
    sub_pt = float(typo["subtitle"])
    ls = float(sp.get("line_spacing", 1.30))

    # Measure natural Content-Driven height for each row
    row_plans: list[dict[str, object]] = []
    for idx, row in enumerate(rows_spec):
        label_s = _first_non_empty_str(row, "label")
        if label_s:
            title_s = label_s
            right_lead = _first_non_empty_str(row, "lead", "heading", "title")
        else:
            title_s = _first_non_empty_str(row, "title", "heading", "name", "category")
            right_lead = _first_non_empty_str(row, "lead", "heading")
            if right_lead == title_s:
                right_lead = ""

        has_explicit_num = isinstance(row, dict) and any(
            k in row and row.get(k) is not None for k in ("kicker", "num", "badge", "step", "index")
        )
        if has_explicit_num:
            num_s = _first_non_empty_str(row, "kicker", "num", "badge", "step", "index")
        else:
            num_s = "" if _LEADING_INDEX_PREFIX_RE.match(title_s) else f"{idx + 1:02d}"

        sub_s = _first_non_empty_str(row, "subtitle", "sub")
        left_h = _measure_three_tier_header(num_s, title_s, sub_s, left_w - 0.16, kicker_pt, title_pt, sub_pt)

        raw_pairs = _extract_lead_body_items(row, extra_lead=right_lead)
        parsed_pts: list[tuple[str, str, float]] = []
        for ld, bd in raw_pairs:
            ih = _measure_lead_body_item_height(ld, bd, right_w - 0.12, lead_pt, resolved_pt, line_spacing=ls)
            parsed_pts.append((ld, bd, ih))

        pt_gap = 0.14
        right_h = sum(p[2] for p in parsed_pts) + pt_gap * max(0, len(parsed_pts) - 1) if parsed_pts else 0.36
        content_h = max(left_h, right_h)
        row_plans.append({
            "row": row,
            "num": num_s,
            "title": title_s,
            "subtitle": sub_s,
            "points": parsed_pts,
            "pt_gap": pt_gap,
            "left_h": left_h,
            "content_h": content_h,
        })

    pad_y = 0.18
    raw_total_h = sum(float(p["content_h"]) + 2 * pad_y for p in row_plans)
    exp_factor = _calc_zone2_expansion_factor(avail_h, raw_total_h)
    if exp_factor > 1.0:
        pad_y = round(0.18 * exp_factor, 3)
        for p in row_plans:
            pts_p: list[tuple[str, str, float]] = p["points"]  # type: ignore[assignment]
            new_pt_gap = round(0.14 * exp_factor, 3)
            p["pt_gap"] = new_pt_gap
            r_h = sum(it[2] for it in pts_p) + new_pt_gap * max(0, len(pts_p) - 1) if pts_p else 0.36
            p["content_h"] = max(float(p["left_h"]), r_h)
        raw_total_h = sum(float(p["content_h"]) + 2 * pad_y for p in row_plans)

    budget_h = max(resolved_h, avail_h) if exp_factor > 1.0 else resolved_h
    if raw_total_h > budget_h:
        pad_y = max(0.06, (budget_h - sum(float(p["content_h"]) for p in row_plans)) / (2.0 * n_rows))
        raw_total_h = sum(float(p["content_h"]) + 2 * pad_y for p in row_plans)

    # Extra breathing room gently distributed up to a clean cap (never bloated); scale proportionally if taller than budget_h
    extra_cap = round(0.18 * exp_factor, 3) if exp_factor > 1.0 else 0.18
    extra_per_row = min(extra_cap, max(0.0, (budget_h - raw_total_h) / max(1, n_rows)))
    row_scale = (budget_h / raw_total_h) if raw_total_h > budget_h and raw_total_h > 0 else 1.0

    coords: list[tuple[float, float, float, float]] = []
    cur_y = top
    for idx, plan in enumerate(row_plans):
        row_dict: dict[str, object] = plan["row"]  # type: ignore[assignment]
        is_spot = (spotlight_idx == idx) if spotlight_idx is not None else bool(row_dict.get("is_spotlight", False))
        acc_hex = str(row_dict.get("accent", theme_pri if is_spot else muted_acc))

        target_rh = (float(plan["content_h"]) + 2 * pad_y) * row_scale + extra_per_row
        rem_total = max(0.40, (top + budget_h) - cur_y)
        rh = round(min(rem_total, max(0.45, target_rh)), 3)

        # Top hairline divider
        top_line = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(left), Inches(cur_y), Inches(total_width), Inches(0.015 if idx == 0 else 0.010),
        )
        top_line.fill.solid()
        top_line.fill.fore_color.rgb = hex_to_rgb_color(div_strong if idx == 0 else div_subtle)
        top_line.line.fill.background()

        if is_spot:
            wash = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(left), Inches(cur_y + 0.015), Inches(total_width), Inches(max(0.40, rh - 0.015)),
            )
            wash.fill.solid()
            wash.fill.fore_color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_canvas, 0.14 if is_dark_theme else 0.07))
            wash.line.fill.background()

            bar = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(left), Inches(cur_y + 0.08), Inches(0.06), Inches(max(0.35, rh - 0.16)),
            )
            bar.fill.solid()
            bar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex)
            bar.line.fill.background()

        inner_y = round(cur_y + pad_y, 3)
        inner_h = max(0.36, rh - 2 * pad_y)
        _render_three_tier_header(
            slide,
            x=left + (0.16 if is_spot else 0.04),
            y=inner_y,
            w=max(0.8, left_w - (0.16 if is_spot else 0.04)),
            h=inner_h,
            kicker=str(plan["num"]),
            title=str(plan["title"]),
            subtitle=str(plan["subtitle"]),
            kicker_pt=kicker_pt,
            title_pt=title_pt,
            sub_pt=sub_pt,
            kicker_hex=acc_hex if is_spot else ink_muted,
            title_hex=ink_pri,
            sub_hex=ink_muted,
        )

        # Right expanded block (TOP natural flow, with compact single-textbox packing when tight)
        pts_list: list[tuple[str, str, float]] = plan["points"]  # type: ignore[assignment]
        rx = left + left_w + gutter
        ry = inner_y
        pt_gap = float(plan["pt_gap"])
        if pts_list:
            inner_right_h = max(0.32, (cur_y + rh - 0.06) - ry)
            raw_pts_sum = sum(p[2] for p in pts_list)
            min_gap_tot = 0.05 * max(0, len(pts_list) - 1)
            if len(pts_list) > 1 and (raw_pts_sum + min_gap_tot) > inner_right_h:
                _render_compact_lead_body_stack(
                    slide,
                    x=rx,
                    y=ry,
                    w=right_w - 0.08,
                    h=inner_right_h,
                    items=[(ld, bd) for ld, bd, _ih in pts_list],
                    lead_pt=lead_pt,
                    body_pt=resolved_pt,
                    lead_hex=ink_pri,
                    body_hex=ink_body,
                    bold_color_hex=ink_pri,
                    line_spacing=min(ls, 1.16),
                    para_space_after_pt=2.0,
                )
            else:
                eff_pt_gap = (
                    min(pt_gap, max(0.05, (inner_right_h - raw_pts_sum) / max(1, len(pts_list) - 1)))
                    if len(pts_list) > 1
                    else 0.0
                )
                for ld, bd, ih in pts_list:
                    rem_h = max(0.26, (cur_y + rh - 0.06) - ry)
                    bh = round(rem_h if len(pts_list) == 1 else min(rem_h, ih + 0.02), 3)
                    _render_lead_body_box(
                        slide,
                        x=rx,
                        y=ry,
                        w=right_w - 0.08,
                        h=bh,
                        lead=ld,
                        body=bd,
                        lead_pt=lead_pt,
                        body_pt=resolved_pt,
                        lead_hex=ink_pri,
                        body_hex=ink_body,
                        bold_color_hex=ink_pri,
                        line_spacing=ls,
                    )
                    ry = round(ry + bh + eff_pt_gap, 3)

        coords.append((round(left, 3), round(cur_y, 3), round(total_width, 3), round(rh, 3)))
        cur_y = round(cur_y + rh, 3)

    # Closing bottom hairline
    bot_line = _add_flat_shape(
        slide,
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(min(top + budget_h, cur_y)), Inches(total_width), Inches(0.015),
    )
    bot_line.fill.solid()
    bot_line.fill.fore_color.rgb = hex_to_rgb_color(div_strong)
    bot_line.line.fill.background()

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y(coords, dy_in)


def _render_bento_tile(
    slide,
    block: dict[str, object],
    x: float,
    y: float,
    w: float,
    h: float,
    is_spot: bool,
    dt: dict[str, str],
    typo: dict[str, float],
    body_pt: float,
    ls: float,
    item_gap_scale: float = 1.0,
) -> tuple[float, float, float, float]:
    """Internal SSOT helper to render a single Bento Grid tile (`F2-C / S9`)."""
    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_pri = pal["primary_accent"]
    theme_border = pal["border_card"]
    theme_card_bg = pal["bg_card"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    ink_muted = pal["ink_muted"]
    is_dark = bool(block.get("dark", False))

    acc_hex = str(block.get("accent", dt.get("bookend_accent", "#38BDF8") if is_dark else theme_pri))
    if is_dark:
        fill_hex = str(block.get("bg", dt.get("bookend_dark_bg", "#0F172A")))
        border_hex = acc_hex
        title_hex = "#F8FAFC"
        kicker_hex = acc_hex
        sub_hex = "#CBD5E1"
        lead_hex = "#F8FAFC"
        body_hex = "#E2E8F0"
        bold_hex = "#FFFFFF"
    else:
        fill_hex = str(block.get("bg", _blend_hex(acc_hex, theme_card_bg, 0.14 if is_dark_theme else 0.065) if is_spot else theme_card_bg))
        border_hex = _blend_hex(acc_hex, theme_border, 0.45 if is_dark_theme else 0.35) if is_spot else theme_border
        title_hex = ink_pri
        kicker_hex = acc_hex if is_spot else ink_muted
        sub_hex = ink_muted
        lead_hex = ink_pri
        body_hex = ink_body
        bold_hex = ink_pri

    box = _add_flat_shape(
        slide,
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h),
    )
    box.adjustments[0] = 0.035
    box.fill.solid()
    box.fill.fore_color.rgb = hex_to_rgb_color(fill_hex)
    box.line.color.rgb = hex_to_rgb_color(border_hex)
    box.line.width = Pt(1.3 if (is_spot or is_dark) else 1.0)

    if is_spot or is_dark:
        bar = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(x + 0.16), Inches(y + 0.01), Inches(max(0.5, w - 0.32)), Inches(0.06),
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex)
        bar.line.fill.background()

    pad_x = 0.22
    inner_w = max(0.60, w - 2.0 * pad_x)
    cur_y = round(y + (0.18 if (is_spot or is_dark) else 0.14), 3)

    kicker = _first_non_empty_str(block, "kicker", "badge", "num", "step")
    title = _first_non_empty_str(block, "title", "heading", "label", "name")
    subtitle = _first_non_empty_str(block, "subtitle", "sub")
    kicker_pt = float(typo["kicker"])
    title_pt = float(typo["card_title"])
    sub_pt = float(typo["subtitle"])
    lead_pt = float(typo["lead"])

    stat_val = _first_non_empty_str(block, "stat", "value", "metric")
    block_lead = _first_non_empty_str(block, "lead")
    if block_lead == title:
        block_lead = ""
    raw_pairs = _extract_lead_body_items(block, extra_lead=block_lead)

    parsed_items: list[tuple[str, str, float]] = []
    for ld, bd in raw_pairs:
        ih = _measure_lead_body_item_height(ld, bd, inner_w, lead_pt, body_pt, line_spacing=ls)
        parsed_items.append((ld, bd, ih))

    if kicker or title or subtitle:
        hdr_h = _measure_three_tier_header(kicker, title, subtitle, inner_w, kicker_pt, title_pt, sub_pt)
        est_items_h = (
            sum(it[2] for it in parsed_items) + 0.05 * max(0, len(parsed_items) - 1)
            if parsed_items
            else 0.0
        )
        # Compact 3-tier header into 2 lines (`Kicker · Subtitle` + `Title`) when tile vertical budget is tight
        if kicker and title and subtitle and parsed_items and (cur_y + hdr_h + 0.06 + est_items_h) > (y + h - 0.06):
            kicker = f"{kicker} · {subtitle}"
            subtitle = ""
            hdr_h = _measure_three_tier_header(kicker, title, subtitle, inner_w, kicker_pt, title_pt, sub_pt)
        hdr_box_h = round(min(h * 0.58, hdr_h + 0.02), 3)
        hdr_gap = 0.06 if (parsed_items and (cur_y + hdr_box_h + 0.14 + est_items_h) > (y + h - 0.08)) else 0.14
        _render_three_tier_header(
            slide, x + pad_x, cur_y, inner_w, hdr_box_h,
            kicker, title, subtitle, kicker_pt, title_pt, sub_pt,
            kicker_hex, title_hex, sub_hex,
        )
        cur_y = round(cur_y + hdr_box_h + hdr_gap, 3)

    if stat_val:
        stat_pt = max(24.0, _round_half_pt(body_pt * 2.1))
        m_st = measure_text_layout(stat_val, inner_w, stat_pt, bold=True, line_spacing=1.12)
        st_h = round(max(0.42, float(m_st["safe_height_in"])), 3)
        st_tb = slide.shapes.add_textbox(Inches(x + pad_x), Inches(cur_y), Inches(inner_w), Inches(st_h))
        tf_st = st_tb.text_frame
        tf_st.word_wrap = True
        tf_st.vertical_anchor = MSO_ANCHOR.TOP
        tf_st.margin_left = Inches(0.02)
        tf_st.margin_top = Inches(0.0)
        p_st = tf_st.paragraphs[0]
        p_st.alignment = PP_ALIGN.LEFT
        _populate_paragraph_runs(p_st, stat_val, stat_pt, acc_hex, bold=True)
        cur_y = round(cur_y + st_h + 0.08, 3)

    if parsed_items:
        avail_h = max(0.32, (y + h - 0.06) - cur_y)
        raw_sum = sum(it[2] for it in parsed_items)
        min_gap_total = 0.05 * max(0, len(parsed_items) - 1)
        if len(parsed_items) > 1 and (raw_sum + min_gap_total) > avail_h:
            _render_compact_lead_body_stack(
                slide,
                x=x + pad_x,
                y=cur_y,
                w=inner_w,
                h=avail_h,
                items=[(ld, bd) for ld, bd, _ih in parsed_items],
                lead_pt=lead_pt,
                body_pt=body_pt,
                lead_hex=lead_hex,
                body_hex=body_hex,
                bold_color_hex=bold_hex,
                line_spacing=min(ls, 1.15),
                para_space_after_pt=2.0,
            )
        else:
            max_tile_gap = round(0.18 * max(1.0, float(item_gap_scale)), 3)
            item_gap = (
                min(max_tile_gap, max(0.05, (avail_h - raw_sum) / max(1, len(parsed_items) - 1)))
                if len(parsed_items) > 1
                else 0.0
            )
            for ld, bd, ih in parsed_items:
                rem_h = max(0.26, (y + h - 0.06) - cur_y)
                bh = round(min(rem_h, ih + 0.02), 3)
                _render_lead_body_box(
                    slide, x + pad_x, cur_y, inner_w, bh,
                    ld, bd, lead_pt, body_pt, lead_hex, body_hex, bold_hex, line_spacing=ls,
                )
                cur_y = round(cur_y + bh + item_gap, 3)

    return (round(x, 3), round(y, 3), round(w, 3), round(h, 3))


def draw_bento_grid_slide(
    slide,
    primary_block: dict[str, object],
    secondary_blocks: Sequence[dict[str, object]],
    spotlight_idx: int | None = 0,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    body_font_pt: float | None = None,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> list[tuple[float, float, float, float]]:
    """
    [F2-C / S9] Render Asymmetric Bento Grid ("1 Primary Anchor + 2~3 Supporting Blocks"):
    - Left `45%` primary full-height block (`idx=0`) + Right `55%` stacked or 1+2 asymmetric secondary blocks.
    - At `target_body_pt >= 16.0pt`, automatically avoids narrow sub-columns (stacks secondary blocks wide) to prevent Pitfall 1.
    Returns list of bounding rects `[primary_rect, secondary_rect_1, ...]`.
    """
    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.60)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, _min_floor, resolved_pt, typo, sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.0
    )
    ls = float(sp.get("line_spacing", 1.30))
    exp_factor = _calc_zone2_expansion_factor(avail_h, resolved_h)
    gap = round(0.24 * exp_factor, 3) if exp_factor > 1.0 else 0.24
    grid_h = (
        round(min(avail_h, resolved_h * min(1.25, exp_factor)), 3)
        if (exp_factor > 1.0 and height is None)
        else resolved_h
    )
    sec_list = list(secondary_blocks or [])[:3]

    if not sec_list:
        coords = [
            _render_bento_tile(
                slide, primary_block, left, top, total_width, grid_h,
                spotlight_idx == 0, dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
            )
        ]
        dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
        return _shift_coords_y(coords, dy_in)

    pri_ratio = 0.50 if len(sec_list) == 1 else (0.45 if len(sec_list) == 2 else 0.42)
    pri_w = round((total_width - gap) * pri_ratio, 3)
    sec_x = round(left + pri_w + gap, 3)
    sec_w = round(total_width - pri_w - gap, 3)

    coords: list[tuple[float, float, float, float]] = []
    coords.append(
        _render_bento_tile(
            slide, primary_block, left, top, pri_w, grid_h,
            spotlight_idx == 0, dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
        )
    )

    n_sec = len(sec_list)
    if n_sec == 1:
        coords.append(
            _render_bento_tile(
                slide, sec_list[0], sec_x, top, sec_w, grid_h,
                spotlight_idx == 1, dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
            )
        )
    elif n_sec == 2:
        sh = round((grid_h - gap) / 2.0, 3)
        for s_i, blk in enumerate(sec_list):
            sy = round(top + s_i * (sh + gap), 3)
            coords.append(
                _render_bento_tile(
                    slide, blk, sec_x, sy, sec_w, sh,
                    spotlight_idx == (s_i + 1), dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
                )
            )
    else:  # n_sec == 3
        if resolved_pt >= 16.0:
            # High-distance Pitfall 1 protection: keep all 3 secondary tiles wide in a vertical stack
            sh = round((grid_h - 2.0 * gap) / 3.0, 3)
            for s_i, blk in enumerate(sec_list):
                sy = round(top + s_i * (sh + gap), 3)
                coords.append(
                    _render_bento_tile(
                        slide, blk, sec_x, sy, sec_w, sh,
                        spotlight_idx == (s_i + 1), dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
                    )
                )
        else:
            top_h = round((grid_h - gap) * 0.48, 3)
            bot_h = round(grid_h - gap - top_h, 3)
            bot_y = round(top + top_h + gap, 3)
            sub_w = round((sec_w - gap) / 2.0, 3)
            coords.append(
                _render_bento_tile(
                    slide, sec_list[0], sec_x, top, sec_w, top_h,
                    spotlight_idx == 1, dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
                )
            )
            coords.append(
                _render_bento_tile(
                    slide, sec_list[1], sec_x, bot_y, sub_w, bot_h,
                    spotlight_idx == 2, dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
                )
            )
            coords.append(
                _render_bento_tile(
                    slide, sec_list[2], round(sec_x + sub_w + gap, 3), bot_y, sub_w, bot_h,
                    spotlight_idx == 3, dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
                )
            )

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y(coords, dy_in)


# -------------------------------------------------------------------------
# Family 3 | Flow & Mechanism (`F3-A` S3+S12, `F3-B` S4)
# -------------------------------------------------------------------------

def draw_process_steps_s3(
    slide,
    steps_spec: Sequence[dict[str, object]],
    layout_style: str = "auto",
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    spotlight_idx: int | None = None,
    body_font_pt: float | None = None,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> list[tuple[float, float, float, float]]:
    """
    [F3-A / S3 + S12] Render Sequential Process Track or Staggered Timeline:
    - `layout_style`:
      * `"auto"` (default): selects `"staggered_timeline"` (`S12`) for 4–5 milestones, `"fine_track"` for <=3 steps.
      * `"fine_track"`: de-boxed horizontal hairline track (`01 ─── 02 ─── 03`) with TOP-aligned unboxed columns below.
      * `"staggered_timeline"` (`S12`): central horizontal spine with milestones alternating UP/DOWN for wide, Pitfall-1-safe blocks.
      * `"card_arrow"`: single-layer clean step cards connected by vector `RIGHT_ARROW` shapes (TOP natural flow + Content-Driven Height).
    """
    n_steps = len(steps_spec)
    if n_steps == 0:
        return []

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.20)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    default_body = 13.0 if n_steps <= 3 else 12.5
    dt, min_floor, resolved_pt, typo, sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=default_body
    )
    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_primary = pal["primary_accent"]
    theme_border = pal["border_card"]
    theme_card_bg = pal["bg_card"]
    theme_canvas = pal["bg_canvas"]
    theme_ink_pri = pal["ink_primary"]
    theme_ink_body = pal["ink_body"]
    theme_ink_muted = pal["ink_muted"]
    pill_fg = pal["pill_fg"]
    div_subtle = pal["divider_subtle"]
    div_strong = pal["divider_strong"]
    muted_bar = pal["muted_bar"]
    muted_acc = pal["muted_accent"]
    arrow_muted = pal["arrow_muted"]

    title_pt = float(typo["card_title"])
    lead_pt = float(typo["lead"])
    sub_pt = float(typo["subtitle"])
    kicker_pt = float(typo["kicker"])
    ls = float(sp.get("line_spacing", 1.30))

    if spotlight_idx is None:
        spotlight_idx = n_steps - 1

    eff_style = str(layout_style or "auto").strip().lower()
    if eff_style == "auto":
        eff_style = "staggered_timeline" if n_steps >= 4 else "fine_track"
    if eff_style not in ("fine_track", "staggered_timeline", "card_arrow"):
        eff_style = "fine_track"

    def _parse_step_spec(step: dict[str, object], default_label: str) -> tuple[str, str, str, list[tuple[str, str]]]:
        lbl = _first_non_empty_str(step, "step", "badge", "num", "phase", "date", "kicker", default=default_label)
        t_s = _first_non_empty_str(step, "title", "heading", "label", "name")
        s_s = _first_non_empty_str(step, "subtitle", "sub")
        ld_s = _first_non_empty_str(step, "lead")
        if ld_s == t_s:
            ld_s = ""
        pairs = _extract_lead_body_items(step, extra_lead=ld_s)
        return lbl, t_s, s_s, pairs

    # ---- Variant 1: S12 Staggered Alternating Timeline (4–5 milestones, wide Pitfall-1-safe blocks) ----
    if eff_style == "staggered_timeline":
        # Evenly spaced milestone X centers inside [left, left+total_width]
        edge_pad = total_width * (0.12 if n_steps <= 4 else 0.10)
        if n_steps == 1:
            centers = [left + total_width / 2.0]
        else:
            step_dx = (total_width - 2.0 * edge_pad) / (n_steps - 1)
            centers = [left + edge_pad + i * step_dx for i in range(n_steps)]

        upper_indices = [i for i in range(n_steps) if i % 2 == 0]
        lower_indices = [i for i in range(n_steps) if i % 2 == 1]

        def _compute_row_boxes(indices: list[int]) -> dict[int, tuple[float, float]]:
            if not indices:
                return {}
            min_gap = 0.28
            n_row = len(indices)
            max_slot_w = (total_width - min_gap * max(0, n_row - 1)) / n_row
            box_w = round(min(4.80, max_slot_w), 3)
            out: dict[int, tuple[float, float]] = {}
            for pos_i, idx_val in enumerate(indices):
                ideal_x = centers[idx_val] - box_w / 2.0
                min_x = left + pos_i * (box_w + min_gap)
                max_x = left + total_width - (n_row - pos_i) * box_w - (n_row - 1 - pos_i) * min_gap
                bx = round(max(min_x, min(max_x, ideal_x)), 3)
                out[idx_val] = (bx, box_w)
            return out

        row_x_map = {}
        row_x_map.update(_compute_row_boxes(upper_indices))
        row_x_map.update(_compute_row_boxes(lower_indices))

        # Pre-measure milestone blocks for Direction 2 expansion check
        st_title_pt = _round_half_pt(resolved_pt + 2.0)
        pre_st_data: list[tuple[str, str, str, float, list[tuple[str, str, float]], float]] = []
        max_upper_need = 0.0
        max_lower_need = 0.0
        for idx, step in enumerate(steps_spec):
            _bx, bw = row_x_map[idx]
            inner_w = max(0.80, bw - 0.18)
            step_lbl, step_title, step_sub, raw_pairs = _parse_step_spec(step, f"{idx + 1:02d}")
            hdr_h = _measure_three_tier_header(step_lbl, step_title, step_sub, inner_w, kicker_pt, st_title_pt, sub_pt)
            parsed_pts: list[tuple[str, str, float]] = [
                (ld, bd, _measure_lead_body_item_height(ld, bd, inner_w, lead_pt, resolved_pt, line_spacing=1.26))
                for ld, bd in raw_pairs
            ]
            pts_h = sum(p[2] for p in parsed_pts) + 0.08 * max(0, len(parsed_pts) - 1) if parsed_pts else 0.0
            need_h = max(0.65, hdr_h + (0.06 + pts_h if pts_h else 0.0) + 0.16)
            pre_st_data.append((step_lbl, step_title, step_sub, hdr_h, parsed_pts, need_h))
            if idx % 2 == 0:
                max_upper_need = max(max_upper_need, need_h)
            else:
                max_lower_need = max(max_lower_need, need_h)

        nat_tl_h = max_upper_need + max_lower_need + 2.0 * 0.24 + 0.24
        tl_exp = _calc_zone2_expansion_factor(avail_h, nat_tl_h)
        stem_len = round(0.24 * tl_exp, 3) if tl_exp > 1.0 else 0.24
        st_pt_gap = round(0.08 * tl_exp, 3) if tl_exp > 1.0 else 0.08
        tl_budget_h = max(resolved_h, avail_h) if tl_exp > 1.0 else resolved_h
        half_avail_h = max(1.10, round((tl_budget_h / 2.0) - stem_len - 0.16, 3))
        spine_y = round(top + min(half_avail_h, max_upper_need) + stem_len + 0.12, 3) if tl_exp > 1.0 else round(top + resolved_h * 0.50, 3)
        spine_y = max(round(top + 1.05, 3), min(round(top + tl_budget_h - 1.05, 3), spine_y))

        spine = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(left), Inches(spine_y - 0.015), Inches(total_width - 0.16), Inches(0.03),
        )
        spine.fill.solid()
        spine.fill.fore_color.rgb = hex_to_rgb_color(arrow_muted)
        spine.line.fill.background()

        cap_arr = _add_flat_shape(
            slide,
            MSO_SHAPE.ISOSCELES_TRIANGLE,
            Inches(left + total_width - 0.18), Inches(spine_y - 0.09), Inches(0.18), Inches(0.18),
        )
        cap_arr.rotation = 90.0
        cap_arr.fill.solid()
        cap_arr.fill.fore_color.rgb = hex_to_rgb_color(theme_primary)
        cap_arr.line.fill.background()

        coords: list[tuple[float, float, float, float]] = []

        for idx, step in enumerate(steps_spec):
            is_upper = (idx % 2 == 0)
            is_spot = (idx == spotlight_idx) or bool(step.get("is_spotlight", False))
            acc_hex = str(step.get("accent", theme_primary if is_spot else muted_acc))
            cx = centers[idx]
            bx, bw = row_x_map[idx]

            # Milestone marker node on central spine
            node_d = 0.24 if is_spot else 0.18
            node = _add_flat_shape(
                slide,
                MSO_SHAPE.OVAL,
                Inches(cx - node_d / 2.0), Inches(spine_y - node_d / 2.0), Inches(node_d), Inches(node_d),
            )
            node.fill.solid()
            node.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else theme_card_bg)
            node.line.color.rgb = hex_to_rgb_color(acc_hex if is_spot else muted_acc)
            node.line.width = Pt(2.0 if is_spot else 1.5)

            # Reuse pre-measured text content
            step_lbl, step_title, step_sub, hdr_h, parsed_pts, _need_h = pre_st_data[idx]
            inner_w = max(0.80, bw - 0.18)

            pts_h = sum(p[2] for p in parsed_pts) + st_pt_gap * max(0, len(parsed_pts) - 1) if parsed_pts else 0.0
            blk_h = round(min(half_avail_h, max(0.65, hdr_h + (0.06 + pts_h if pts_h else 0.0) + 0.16)), 3)
            by = round((spine_y - node_d / 2.0 - stem_len - blk_h) if is_upper else (spine_y + node_d / 2.0 + stem_len), 3)
            by = max(top, min(top + tl_budget_h - blk_h, by))

            # Vertical stem joining spine node cleanly to the block's spine-facing anchor rail
            actual_stem_top = (by + blk_h) if is_upper else (spine_y + node_d / 2.0)
            actual_stem_h = max(0.08, ((spine_y - node_d / 2.0) - actual_stem_top) if is_upper else (by - actual_stem_top))
            stem = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(cx - 0.012), Inches(actual_stem_top), Inches(0.024), Inches(actual_stem_h),
            )
            stem.fill.solid()
            stem.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else arrow_muted)
            stem.line.fill.background()

            if is_spot:
                wash = _add_flat_shape(
                    slide,
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    Inches(bx), Inches(by), Inches(bw), Inches(blk_h),
                )
                wash.adjustments[0] = 0.04
                wash.fill.solid()
                wash.fill.fore_color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_canvas, 0.14 if is_dark_theme else 0.07))
                wash.line.fill.background()

            # Horizontal spine-facing T-joint rail anchoring block directly to the stem
            rail_edge_y = (by + blk_h - 0.024) if is_upper else by
            edge_rail = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(bx), Inches(rail_edge_y), Inches(bw), Inches(0.030 if is_spot else 0.018),
            )
            edge_rail.fill.solid()
            edge_rail.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else muted_bar)
            edge_rail.line.fill.background()

            # Crisp left vertical hairline anchoring block text
            lbar = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(bx), Inches(by + 0.04), Inches(0.055 if is_spot else 0.032), Inches(max(0.36, blk_h - 0.08)),
            )
            lbar.fill.solid()
            lbar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else muted_bar)
            lbar.line.fill.background()

            hdr_box_h = round(min(blk_h * 0.62, hdr_h + 0.02), 3)
            _render_three_tier_header(
                slide,
                x=bx + 0.14, y=by + 0.04, w=inner_w, h=hdr_box_h,
                kicker=step_lbl, title=step_title, subtitle=step_sub,
                kicker_pt=kicker_pt, title_pt=st_title_pt, sub_pt=sub_pt,
                kicker_hex=acc_hex if is_spot else theme_ink_muted,
                title_hex=theme_ink_pri, sub_hex=theme_ink_muted,
            )

            cy_pt = round(by + 0.04 + hdr_box_h + 0.04, 3)
            if parsed_pts:
                avail_pt_h = max(0.28, (by + blk_h - 0.04) - cy_pt)
                raw_pts_h = sum(p[2] for p in parsed_pts)
                min_gap_h = 0.05 * max(0, len(parsed_pts) - 1)
                if len(parsed_pts) > 1 and (raw_pts_h + min_gap_h) > avail_pt_h:
                    _render_compact_lead_body_stack(
                        slide,
                        x=bx + 0.14,
                        y=cy_pt,
                        w=inner_w,
                        h=avail_pt_h,
                        items=[(ld, bd) for ld, bd, _ih in parsed_pts],
                        lead_pt=lead_pt,
                        body_pt=resolved_pt,
                        lead_hex=theme_ink_pri,
                        body_hex=theme_ink_body,
                        bold_color_hex=theme_ink_pri,
                        line_spacing=1.16,
                        para_space_after_pt=2.0,
                    )
                else:
                    eff_pt_g = (
                        min(st_pt_gap, max(0.04, (avail_pt_h - raw_pts_h) / max(1, len(parsed_pts) - 1)))
                        if len(parsed_pts) > 1
                        else 0.0
                    )
                    for ld, bd, ih in parsed_pts:
                        rem = max(0.24, (by + blk_h - 0.04) - cy_pt)
                        bh = round(min(rem, ih + 0.02), 3)
                        _render_lead_body_box(
                            slide, bx + 0.14, cy_pt, inner_w, bh,
                            ld, bd, lead_pt, resolved_pt, theme_ink_pri, theme_ink_body, theme_ink_pri, line_spacing=1.26,
                        )
                        cy_pt = round(cy_pt + bh + eff_pt_g, 3)

            coords.append((round(bx, 3), round(by, 3), round(bw, 3), round(blk_h, 3)))

        dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
        return _shift_coords_y(coords, dy_in)

    # ---- Variant 2: De-Boxed Horizontal Fine Track (`01 ─── 02 ─── 03`) ----
    if eff_style == "fine_track":
        col_gap = 0.36 if n_steps <= 3 else 0.24
        col_w = (total_width - col_gap * max(0, n_steps - 1)) / n_steps
        pill_h = max(0.36, round((kicker_pt * 1.35) / 72.0 + 0.14, 3))
        track_y = round(top + pill_h / 2.0, 3)

        # Continuous background horizontal track rail (terminates cleanly inside the last step pill)
        last_pill_x = left + (n_steps - 1) * (col_w + col_gap)
        rail_start_x = left + 0.10
        rail_end_x = last_pill_x + 0.30 if n_steps > 1 else (left + col_w * 0.50)
        rail = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(rail_start_x), Inches(track_y - 0.012), Inches(max(0.5, rail_end_x - rail_start_x)), Inches(0.024),
        )
        rail.fill.solid()
        rail.fill.fore_color.rgb = hex_to_rgb_color(div_strong)
        rail.line.fill.background()

        # Pre-measure headers and rows across all steps
        step_plans: list[dict[str, object]] = []
        max_hdr_h = 0.0
        for idx, step in enumerate(steps_spec):
            inner_w = max(0.55, col_w - 0.16)
            step_label, title_s, sub_s, raw_pairs = _parse_step_spec(step, f"STEP {idx + 1:02d}")
            hdr_h_s = _measure_three_tier_header("", title_s, sub_s, inner_w, kicker_pt, title_pt, sub_pt)
            max_hdr_h = max(max_hdr_h, hdr_h_s)
            parsed_rows: list[tuple[str, str, float]] = []
            for ld, bd in raw_pairs:
                parsed_rows.append((ld, bd, _measure_lead_body_item_height(ld, bd, inner_w, lead_pt, resolved_pt, line_spacing=ls)))
            step_plans.append({
                "step": step,
                "step_label": step_label,
                "title": title_s,
                "subtitle": sub_s,
                "rows": parsed_rows,
                "inner_w": inner_w,
            })

        nat_col_top = round(top + pill_h + 0.22, 3)
        nat_avail_col_h = max(1.2, round(top + resolved_h - nat_col_top, 3))
        hdr_h = round(min(nat_avail_col_h * 0.42, max(0.44, max_hdr_h)), 3)
        base_gap = 0.20
        nat_body_need = 0.0
        for sp_item in step_plans:
            r_l: list[tuple[str, str, float]] = sp_item["rows"]  # type: ignore[assignment]
            if r_l:
                nat_body_need = max(nat_body_need, sum(r[2] for r in r_l) + base_gap * max(0, len(r_l) - 1))
        nat_total_h = (pill_h + 0.22) + (hdr_h + 0.16) + nat_body_need + 0.22
        ft_exp = _calc_zone2_expansion_factor(avail_h, nat_total_h)

        pill_col_gap = round(0.22 * ft_exp, 3) if ft_exp > 1.0 else 0.22
        hdr_body_gap = round(0.16 * ft_exp, 3) if ft_exp > 1.0 else 0.16
        if ft_exp > 1.0:
            base_gap = round(base_gap * ft_exp, 3)
        col_bot_pad = round(0.22 * ft_exp, 3) if ft_exp > 1.0 else 0.22
        col_top = round(top + pill_h + pill_col_gap, 3)
        col_budget_bottom = avail_bottom if ft_exp > 1.0 else (top + resolved_h)
        avail_col_h = max(1.2, round(col_budget_bottom - col_top, 3))
        body_start_y = round(col_top + hdr_h + hdr_body_gap, 3)

        max_body_need = 0.0
        for sp_item in step_plans:
            r_l = sp_item["rows"]  # type: ignore[assignment]
            if r_l:
                max_body_need = max(max_body_need, sum(r[2] for r in r_l) + base_gap * max(0, len(r_l) - 1))
        actual_col_h = round(min(avail_col_h, max(min(avail_col_h, 1.85), (body_start_y - col_top) + max_body_need + col_bot_pad)), 3)

        coords = []
        cur_x = left
        for idx, sp_item in enumerate(step_plans):
            step = sp_item["step"]  # type: ignore[assignment]
            is_spot = (idx == spotlight_idx) or bool(step.get("is_spotlight", False))
            acc_hex = str(step.get("accent", theme_primary if is_spot else muted_acc))
            step_label = str(sp_item["step_label"])
            inner_w = float(sp_item["inner_w"])

            pill_w = min(col_w - 0.10, max(1.10, calc_pill_width(step_label, font_pt=kicker_pt, pad_in=0.28)))
            step_pill = _add_flat_shape(
                slide,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(cur_x), Inches(top), Inches(pill_w), Inches(pill_h),
            )
            step_pill.adjustments[0] = 0.48
            step_pill.fill.solid()
            step_pill.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else theme_card_bg)
            if not is_spot:
                step_pill.line.color.rgb = hex_to_rgb_color(arrow_muted)
                step_pill.line.width = Pt(1.1)
            else:
                step_pill.line.fill.background()
            tf_sp = step_pill.text_frame
            tf_sp.word_wrap = False
            tf_sp.vertical_anchor = MSO_ANCHOR.MIDDLE
            p_sp = tf_sp.paragraphs[0]
            p_sp.alignment = PP_ALIGN.CENTER
            _populate_paragraph_runs(p_sp, step_label, kicker_pt, pill_fg if is_spot else theme_ink_pri, bold=True)

            # Small clean directional chevron on the track between steps
            if idx < n_steps - 1:
                chev_x = cur_x + col_w + col_gap / 2.0 - 0.08
                chev = _add_flat_shape(
                    slide,
                    MSO_SHAPE.ISOSCELES_TRIANGLE,
                    Inches(chev_x), Inches(track_y - 0.08), Inches(0.15), Inches(0.16),
                )
                chev.rotation = 90.0
                chev.fill.solid()
                chev.fill.fore_color.rgb = hex_to_rgb_color(theme_primary if (idx + 1 == spotlight_idx) else arrow_muted)
                chev.line.fill.background()

            # Spotlight column gets a subtle borderless tint wash + single left bar; non-spotlight is 100% unboxed
            if is_spot:
                wash = _add_flat_shape(
                    slide,
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    Inches(cur_x), Inches(col_top), Inches(col_w), Inches(actual_col_h),
                )
                wash.adjustments[0] = 0.03
                wash.fill.solid()
                wash.fill.fore_color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_canvas, 0.14 if is_dark_theme else 0.065))
                wash.line.fill.background()

                lbar = _add_flat_shape(
                    slide,
                    MSO_SHAPE.RECTANGLE,
                    Inches(cur_x), Inches(col_top + 0.08), Inches(0.055), Inches(max(0.6, actual_col_h - 0.16)),
                )
                lbar.fill.solid()
                lbar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex)
                lbar.line.fill.background()

            txt_x = cur_x + (0.14 if is_spot else 0.04)
            _render_three_tier_header(
                slide,
                x=txt_x, y=col_top + 0.08, w=inner_w, h=hdr_h + 0.04,
                kicker="", title=str(sp_item["title"]), subtitle=str(sp_item["subtitle"]),
                kicker_pt=kicker_pt, title_pt=title_pt, sub_pt=sub_pt,
                kicker_hex=acc_hex, title_hex=theme_ink_pri, sub_hex=theme_ink_muted,
            )

            hrule = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(txt_x), Inches(col_top + hdr_h + 0.10), Inches(inner_w), Inches(0.012),
            )
            hrule.fill.solid()
            hrule.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
            hrule.line.fill.background()

            r_list: list[tuple[str, str, float]] = sp_item["rows"]  # type: ignore[assignment]
            if r_list:
                avail_b = max(0.5, (col_top + actual_col_h - 0.10) - body_start_y)
                raw_sum = sum(r[2] for r in r_list)
                eff_g = min(base_gap, max(0.08, (avail_b - raw_sum) / max(1, len(r_list) - 1))) if len(r_list) > 1 else 0.0
                cy_r = body_start_y
                for r_i, (ld, bd, ih) in enumerate(r_list):
                    if r_i > 0:
                        sep = _add_flat_shape(
                            slide,
                            MSO_SHAPE.RECTANGLE,
                            Inches(txt_x), Inches(round(cy_r - eff_g * 0.5, 3)), Inches(inner_w), Inches(0.008),
                        )
                        sep.fill.solid()
                        sep.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
                        sep.line.fill.background()
                    rem = max(0.30, (col_top + actual_col_h - 0.08) - cy_r)
                    bh = round(min(rem, ih + 0.02), 3)
                    _render_lead_body_box(
                        slide, txt_x, cy_r, inner_w, bh,
                        ld, bd, lead_pt, resolved_pt, theme_ink_pri, theme_ink_body, theme_ink_pri, line_spacing=ls,
                    )
                    cy_r = round(cy_r + bh + eff_g, 3)

            coords.append((round(cur_x, 3), round(col_top, 3), round(col_w, 3), round(actual_col_h, 3)))
            cur_x += col_w + col_gap

        dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
        return _shift_coords_y(coords, dy_in)

    # ---- Variant 3: Upgraded Single-Layer Arrow Step Cards (`card_arrow`) ----
    corridor_w = 0.40 if n_steps <= 3 else 0.30
    card_w = (total_width - corridor_w * max(0, n_steps - 1)) / n_steps
    pill_band_h = max(0.36, round((kicker_pt * 1.35) / 72.0 + 0.12, 3))
    nat_card_top = round(top + pill_band_h + 0.12, 3)
    nat_avail_card_h = max(1.5, round(top + resolved_h - nat_card_top, 3))

    inner_w = max(0.50, card_w - 0.32)
    step_plans = []
    max_hdr_h = 0.0
    for idx_s, step in enumerate(steps_spec):
        step_label, title_s, sub_s, raw_pairs = _parse_step_spec(step, f"STEP {idx_s + 1:02d}")
        hdr_h_s = _measure_three_tier_header("", title_s, sub_s, inner_w, kicker_pt, title_pt, sub_pt)
        max_hdr_h = max(max_hdr_h, hdr_h_s)
        parsed_rows = []
        for ld, bd in raw_pairs:
            parsed_rows.append((ld, bd, _measure_lead_body_item_height(ld, bd, inner_w, lead_pt, resolved_pt, line_spacing=ls)))
        step_plans.append({"step": step, "step_label": step_label, "title": title_s, "subtitle": sub_s, "rows": parsed_rows})

    hdr_h = round(min(nat_avail_card_h * 0.42, max(0.46, max_hdr_h)), 3)
    base_gap = 0.18
    nat_body_need = max(
        (sum(r[2] for r in sp_i["rows"]) + base_gap * max(0, len(sp_i["rows"]) - 1) for sp_i in step_plans if sp_i["rows"]),
        default=0.8,
    )
    nat_ca_total = (pill_band_h + 0.12) + (0.14 + hdr_h + 0.14) + nat_body_need + 0.22
    ca_exp = _calc_zone2_expansion_factor(avail_h, nat_ca_total)
    pill_card_gap = round(0.12 * ca_exp, 3) if ca_exp > 1.0 else 0.12
    hdr_rows_gap = round(0.14 * ca_exp, 3) if ca_exp > 1.0 else 0.14
    if ca_exp > 1.0:
        base_gap = round(base_gap * ca_exp, 3)
    card_bot_pad = round(0.22 * ca_exp, 3) if ca_exp > 1.0 else 0.22

    card_top = round(top + pill_band_h + pill_card_gap, 3)
    ca_budget_bottom = avail_bottom if ca_exp > 1.0 else (top + resolved_h)
    avail_card_h = max(1.5, round(ca_budget_bottom - card_top, 3))
    rows_top = round(card_top + 0.14 + hdr_h + hdr_rows_gap, 3)
    max_body_need = max(
        (sum(r[2] for r in sp_i["rows"]) + base_gap * max(0, len(sp_i["rows"]) - 1) for sp_i in step_plans if sp_i["rows"]),
        default=0.8,
    )
    actual_card_h = round(min(avail_card_h, max(min(avail_card_h, 2.10), (rows_top - card_top) + max_body_need + card_bot_pad)), 3)

    coords = []
    cur_x = left
    for idx, sp_item in enumerate(step_plans):
        step = sp_item["step"]  # type: ignore[assignment]
        is_spot = (idx == spotlight_idx) or bool(step.get("is_spotlight", False))
        acc_hex = str(step.get("accent", theme_primary if is_spot else muted_acc))
        step_label = str(sp_item["step_label"])

        pill_w = min(card_w, max(1.15, calc_pill_width(step_label, font_pt=kicker_pt, pad_in=0.26)))
        step_pill = _add_flat_shape(
            slide,
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(cur_x), Inches(top), Inches(pill_w), Inches(pill_band_h),
        )
        step_pill.adjustments[0] = 0.45
        step_pill.fill.solid()
        step_pill.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else (theme_card_bg if is_dark_theme else "#E2E8F0"))
        if is_dark_theme and not is_spot:
            step_pill.line.color.rgb = hex_to_rgb_color(theme_border)
            step_pill.line.width = Pt(1.0)
        else:
            step_pill.line.fill.background()
        tf_sp = step_pill.text_frame
        tf_sp.word_wrap = False
        tf_sp.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_sp = tf_sp.paragraphs[0]
        p_sp.alignment = PP_ALIGN.CENTER
        _populate_paragraph_runs(p_sp, step_label, kicker_pt, pill_fg if is_spot else theme_ink_pri, bold=True)

        card_fill = str(step.get("bg", _blend_hex(acc_hex, theme_card_bg, 0.14 if is_dark_theme else 0.06) if is_spot else theme_card_bg))
        card_box = _add_flat_shape(
            slide,
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(cur_x), Inches(card_top), Inches(card_w), Inches(actual_card_h),
        )
        card_box.adjustments[0] = 0.035
        card_box.fill.solid()
        card_box.fill.fore_color.rgb = hex_to_rgb_color(card_fill)
        card_box.line.color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_border, 0.45 if is_dark_theme else 0.35) if is_spot else theme_border)
        card_box.line.width = Pt(1.3 if is_spot else 1.0)

        top_strip = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(cur_x + 0.14), Inches(card_top + 0.01), Inches(max(0.4, card_w - 0.28)), Inches(0.06 if is_spot else 0.035),
        )
        top_strip.fill.solid()
        top_strip.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else muted_bar)
        top_strip.line.fill.background()

        _render_three_tier_header(
            slide, cur_x + 0.16, card_top + 0.12, inner_w, hdr_h + 0.04,
            "", str(sp_item["title"]), str(sp_item["subtitle"]),
            kicker_pt, title_pt, sub_pt, acc_hex, theme_ink_pri, theme_ink_muted,
        )

        rule = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(cur_x + 0.16), Inches(card_top + 0.14 + hdr_h + 0.04), Inches(inner_w), Inches(0.012),
        )
        rule.fill.solid()
        rule.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
        rule.line.fill.background()

        r_list = sp_item["rows"]  # type: ignore[assignment]
        if r_list:
            avail_b = max(0.5, (card_top + actual_card_h - 0.10) - rows_top)
            raw_sum = sum(r[2] for r in r_list)
            eff_g = min(base_gap, max(0.08, (avail_b - raw_sum) / max(1, len(r_list) - 1))) if len(r_list) > 1 else 0.0
            cy_r = rows_top
            for r_i, (ld, bd, ih) in enumerate(r_list):
                if r_i > 0:
                    sep = _add_flat_shape(
                        slide,
                        MSO_SHAPE.RECTANGLE,
                        Inches(cur_x + 0.16), Inches(round(cy_r - eff_g * 0.5, 3)), Inches(inner_w), Inches(0.008),
                    )
                    sep.fill.solid()
                    sep.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
                    sep.line.fill.background()
                rem = max(0.24, (card_top + actual_card_h - 0.08) - cy_r)
                bh = round(min(rem, ih + 0.02), 3)
                _render_lead_body_box(
                    slide, cur_x + 0.16, cy_r, inner_w, bh,
                    ld, bd, lead_pt, resolved_pt, theme_ink_pri, theme_ink_body, theme_ink_pri, line_spacing=ls,
                )
                cy_r = round(cy_r + bh + eff_g, 3)

        if idx < n_steps - 1:
            arr_w = min(0.28, corridor_w - 0.08)
            arr_h = 0.22
            arr_x = cur_x + card_w + (corridor_w - arr_w) / 2.0
            arr_y = card_top + actual_card_h / 2.0 - arr_h / 2.0
            arr = _add_flat_shape(
                slide,
                MSO_SHAPE.RIGHT_ARROW,
                Inches(arr_x), Inches(arr_y), Inches(max(0.16, arr_w)), Inches(arr_h),
            )
            arr.fill.solid()
            arr.fill.fore_color.rgb = hex_to_rgb_color(theme_primary if (idx + 1 == spotlight_idx) else arrow_muted)
            arr.line.fill.background()

        coords.append((round(cur_x, 3), round(card_top, 3), round(card_w, 3), round(actual_card_h, 3)))
        cur_x += card_w + corridor_w

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y(coords, dy_in)


def _normalize_callout_items(callouts: Sequence[object] | None) -> list[tuple[str, str]]:
    """Normalize callout items into [(lead_heading, body), ...] pairs using SSOT `_parse_lead_body_item()`."""
    if not callouts:
        return []
    normalized: list[tuple[str, str]] = []
    for item in callouts:
        h, b = _parse_lead_body_item(item)
        if h or b:
            normalized.append((h, b))
    return normalized


def _estimate_vertical_callouts_height(
    items: list[tuple[str, str]],
    w: float,
    heading: str | None,
    body_pt: float,
    gap_scale: float = 1.0,
) -> float:
    """Measure exact natural vertical height (inches) of `_render_unboxed_callouts_vertical()`."""
    heading_pt = _round_half_pt(body_pt * 1.30)
    lead_pt = _round_half_pt(body_pt * 1.15)
    total_h = 0.0
    if heading and heading.strip():
        m_h = measure_text_layout(heading.strip(), box_width_in=max(0.6, w - 0.04), font_pt=heading_pt, bold=True, line_spacing=1.20)
        total_h += max(0.32, float(m_h["safe_height_in"])) + 0.06 + 0.18
    if not items:
        return round(total_h, 3)
    txt_w = max(0.55, w - 0.18)
    base_gap = (0.26 if len(items) <= 2 else 0.22) * max(1.0, float(gap_scale))
    for idx, (c_title, c_body) in enumerate(items):
        item_h = _measure_lead_body_item_height(c_title, c_body, txt_w, lead_pt, body_pt, line_spacing=1.30)
        box_h = item_h + 0.02
        vis_h = 0.0
        if c_title:
            vis_h += float(measure_text_layout(c_title, max(0.45, txt_w - 0.04), lead_pt, bold=True, line_spacing=1.22)["content_height_in"])
        if c_body:
            vis_h += float(measure_text_layout(c_body, max(0.45, txt_w - 0.04), body_pt, bold=False, line_spacing=1.30)["content_height_in"])
        if c_title and c_body:
            vis_h += 0.04
        bar_h = min(max(0.28, box_h - 0.04), max(0.28, vis_h + 0.04))
        if idx < len(items) - 1:
            total_h += max(bar_h + 0.06, min(box_h, vis_h + 0.10)) + base_gap
        else:
            total_h += box_h
    return round(total_h, 3)


def _render_unboxed_callouts_vertical(
    slide,
    items: list[tuple[str, str]],
    x: float,
    y: float,
    w: float,
    h: float,
    heading: str | None,
    body_pt: float,
    spotlight_idx: int | None,
    dt: dict[str, str],
    gap_scale: float = 1.0,
) -> None:
    """
    Render side unboxed callouts (Module 1 Upgraded — fixes L1083 1.25" heading gap):
    - Strict `MSO_ANCHOR.TOP` natural top-down flow (abolishes vertical centering gap & `slot_h` equal split).
    - Clear typography scale: Heading `1.30x` Bold -> Lead `1.15x` Bold -> Body `1.0x` Regular (`#334155`).
    - Left vertical accent hairline strictly hugs each item's exact rendered text height via `measure_text_layout()`.
    """
    pal = _theme_palette(dt)
    theme_pri = pal["primary_accent"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    muted_bar = pal["muted_bar"]

    heading_pt = _round_half_pt(body_pt * 1.30)
    lead_pt = _round_half_pt(body_pt * 1.15)
    cur_y = float(y)

    if heading and heading.strip():
        h_str = heading.strip()
        m_h = measure_text_layout(h_str, box_width_in=max(0.6, w - 0.04), font_pt=heading_pt, bold=True, line_spacing=1.20)
        h_box_h = round(max(0.32, float(m_h["safe_height_in"])), 3)
        hb = slide.shapes.add_textbox(Inches(x), Inches(cur_y), Inches(w), Inches(h_box_h))
        tf_h = hb.text_frame
        tf_h.word_wrap = True
        tf_h.margin_left = Inches(0.0)
        tf_h.margin_right = Inches(0.0)
        tf_h.margin_top = Inches(0.0)
        tf_h.margin_bottom = Inches(0.0)
        tf_h.vertical_anchor = MSO_ANCHOR.TOP
        ph = tf_h.paragraphs[0]
        ph.alignment = PP_ALIGN.LEFT
        ph.line_spacing = 1.20
        _populate_paragraph_runs(ph, h_str, heading_pt, ink_pri, bold=True)

        rule_y = round(cur_y + h_box_h + 0.06, 3)
        h_rule = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(x), Inches(rule_y), Inches(min(w, 1.40)), Inches(0.03),
        )
        h_rule.fill.solid()
        h_rule.fill.fore_color.rgb = hex_to_rgb_color(theme_pri)
        h_rule.line.fill.background()
        cur_y = round(rule_y + 0.18, 3)

    if not items:
        return

    txt_w = max(0.55, w - 0.18)
    item_heights = [
        _measure_lead_body_item_height(c_title, c_body, txt_w, lead_pt, body_pt, line_spacing=1.30)
        for c_title, c_body in items
    ]
    avail_h = max(0.80, (y + h) - cur_y)
    base_gap = round((0.26 if len(items) <= 2 else 0.22) * max(1.0, float(gap_scale)), 3)
    raw_sum = sum(item_heights)
    if len(items) > 1:
        eff_gap = min(base_gap, max(0.08, (avail_h - raw_sum) / (len(items) - 1)))
    else:
        eff_gap = 0.0

    for idx, ((c_title, c_body), item_h) in enumerate(zip(items, item_heights)):
        is_spot = spotlight_idx is not None and idx == spotlight_idx
        bar_hex = theme_pri if is_spot else muted_bar
        rem_h = max(0.32, (y + h) - cur_y)
        box_h = round(min(rem_h, item_h + 0.02), 3)

        # Left hairline strictly hugs exact visual text height (without overflow-guard padding)
        vis_h = 0.0
        if c_title:
            vis_h += float(measure_text_layout(c_title, max(0.45, txt_w - 0.04), lead_pt, bold=True, line_spacing=1.22)["content_height_in"])
        if c_body:
            vis_h += float(measure_text_layout(c_body, max(0.45, txt_w - 0.04), body_pt, bold=False, line_spacing=1.30)["content_height_in"])
        if c_title and c_body:
            vis_h += 0.04
        bar_h = round(min(max(0.28, box_h - 0.04), max(0.28, vis_h + 0.04)), 3)
        bar = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(x), Inches(cur_y + 0.02), Inches(0.055 if is_spot else 0.035), Inches(bar_h),
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = hex_to_rgb_color(bar_hex)
        bar.line.fill.background()

        _render_lead_body_box(
            slide,
            x=x + 0.16,
            y=cur_y,
            w=txt_w,
            h=box_h,
            lead=c_title,
            body=c_body,
            lead_pt=lead_pt,
            body_pt=body_pt,
            lead_hex=theme_pri if is_spot else ink_pri,
            body_hex=ink_body,
            bold_color_hex=ink_pri,
            line_spacing=1.30,
        )
        cur_y = round(cur_y + max(bar_h + 0.06, min(box_h, vis_h + 0.10)) + eff_gap, 3)


def _render_unboxed_callouts_horizontal(
    slide,
    items: list[tuple[str, str]],
    x: float,
    y: float,
    w: float,
    h: float,
    body_pt: float,
    spotlight_idx: int | None,
    dt: dict[str, str],
) -> None:
    """Render top or bottom horizontal unboxed callouts (`TOP` aligned, `1.15x / 1.0x` hierarchy, text-hugging left bars)."""
    n = max(1, len(items))
    gap = 0.34
    col_w = (w - gap * (n - 1)) / n
    pal = _theme_palette(dt)
    theme_pri = pal["primary_accent"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    muted_bar = pal["muted_bar"]
    lead_pt = _round_half_pt(body_pt * 1.15)

    for idx, (c_title, c_body) in enumerate(items):
        cx = x + idx * (col_w + gap)
        is_spot = spotlight_idx is not None and idx == spotlight_idx
        rule_hex = theme_pri if is_spot else muted_bar
        txt_w = max(0.60, col_w - 0.16)
        item_h = _measure_lead_body_item_height(c_title, c_body, txt_w, lead_pt, body_pt, line_spacing=1.28)
        box_h = round(min(max(0.36, h), item_h + 0.04), 3)

        vis_h = 0.0
        if c_title:
            vis_h += float(measure_text_layout(c_title, max(0.45, txt_w - 0.04), lead_pt, bold=True, line_spacing=1.22)["content_height_in"])
        if c_body:
            vis_h += float(measure_text_layout(c_body, max(0.45, txt_w - 0.04), body_pt, bold=False, line_spacing=1.28)["content_height_in"])
        if c_title and c_body:
            vis_h += 0.04
        bar_h = round(min(max(0.28, box_h - 0.04), max(0.28, vis_h + 0.04)), 3)

        rule = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(cx), Inches(y + 0.02), Inches(0.055 if is_spot else 0.035), Inches(bar_h),
        )
        rule.fill.solid()
        rule.fill.fore_color.rgb = hex_to_rgb_color(rule_hex)
        rule.line.fill.background()

        _render_lead_body_box(
            slide,
            x=cx + 0.14,
            y=y,
            w=txt_w,
            h=box_h,
            lead=c_title,
            body=c_body,
            lead_pt=lead_pt,
            body_pt=body_pt,
            lead_hex=theme_pri if is_spot else ink_pri,
            body_hex=ink_body,
            bold_color_hex=ink_pri,
            line_spacing=1.28,
        )


def _estimate_horizontal_band_height(items: list[tuple[str, str]], total_w: float, body_pt: float) -> float:
    """Measure exact horizontal unboxed callout band height in inches via Pillow `measure_text_layout()`."""
    n = max(1, len(items))
    col_w = max(1.2, (total_w - 0.34 * (n - 1)) / n)
    usable_col_w = max(0.65, col_w - 0.16)
    lead_pt = _round_half_pt(body_pt * 1.15)
    max_item_h = 0.0
    for c_title, c_body in items:
        req = _measure_lead_body_item_height(c_title, c_body, usable_col_w, lead_pt, body_pt, line_spacing=1.28)
        max_item_h = max(max_item_h, req)
    return round(max(0.76, max_item_h + 0.10), 3)


# -------------------------------------------------------------------------
# Family 5 | Evidence & Anatomy (`F5-A` S7, `F5-B` S10, `F5-C` S6)
# -------------------------------------------------------------------------

def draw_visual_callout_slide(
    slide,
    image_path: str | None = None,
    callout_position: str = "right",
    callouts: Sequence[object] | None = None,
    visual_ratio: float = 0.65,
    visual_caption: str | None = None,
    callout_heading: str | None = None,
    body_font_pt: float = 13.0,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    spotlight_idx: int | None = 0,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
    *,
    _callout_gap_scale: float | None = None,
) -> tuple[float, float, float, float]:
    """
    [F5-A / S7] Render Primary Visual Slide obeying the Unboxed Callout Iron Law (`圖旁不疊卡`):
    Supports 5 flexible unboxed layouts via `callout_position`:
      1. "right" (S7-A): Left maximized visual + Right unboxed TOP-aligned callouts (`1.30x / 1.15x / 1.0x`).
      2. "left"  (S7-A alt): Left unboxed callouts + Right maximized visual.
      3. "bottom"(S7-B): Top maximized visual + Bottom horizontal unboxed callouts.
      4. "top"   (S7-C): Top horizontal unboxed callout band + Bottom maximized visual.
      5. "header_only" (S7-D, or when `callouts` is empty): Full-width maximized visual.
    Anchors `visual_caption` cleanly to the bottom edge of Zone 2 (left-aligned, `>= min_font_pt`).
    Returns `visual_rect = (vx, vy, vw, vh)` in inches.
    """
    pos = str(callout_position or "right").strip().lower()
    valid_positions = {"right", "left", "top", "bottom", "header_only"}
    if pos not in valid_positions:
        raise ValueError(f"Unsupported callout_position '{callout_position}'. Expected one of {sorted(valid_positions)}.")

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.66)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, min_floor, resolved_pt, typo, _sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.0, caller_default_pt=13.0
    )
    items = _normalize_callout_items(callouts)
    if not items:
        pos = "header_only"

    gap = 0.36
    ratio = max(0.45, min(0.82, float(visual_ratio)))
    band_gap = 0.18
    if image_path is not None and pos in ("bottom", "top"):
        vis_exp = _calc_zone2_expansion_factor(avail_h, resolved_h)
        if vis_exp > 1.0:
            band_gap = round(0.18 * vis_exp, 3)

    if pos == "header_only":
        vx, vy, vw, vh = left, top, total_width, resolved_h
    elif pos == "right":
        vw = (total_width - gap) * ratio
        cw = total_width - gap - vw
        vx, vy, vh = left, top, resolved_h
        c_scale = _callout_gap_scale
        if c_scale is None:
            est_c_h = _estimate_vertical_callouts_height(items, cw, callout_heading, resolved_pt, gap_scale=1.0)
            c_scale = _calc_zone2_expansion_factor(avail_h, est_c_h)
        callout_budget_h = max(resolved_h, avail_h) if c_scale > 1.0 else resolved_h
        _render_unboxed_callouts_vertical(
            slide, items, left + vw + gap, top, cw, callout_budget_h, callout_heading, resolved_pt, spotlight_idx, dt,
            gap_scale=c_scale,
        )
    elif pos == "left":
        vw = (total_width - gap) * ratio
        cw = total_width - gap - vw
        vx, vy, vh = left + cw + gap, top, resolved_h
        c_scale = _callout_gap_scale
        if c_scale is None:
            est_c_h = _estimate_vertical_callouts_height(items, cw, callout_heading, resolved_pt, gap_scale=1.0)
            c_scale = _calc_zone2_expansion_factor(avail_h, est_c_h)
        callout_budget_h = max(resolved_h, avail_h) if c_scale > 1.0 else resolved_h
        _render_unboxed_callouts_vertical(
            slide, items, left, top, cw, callout_budget_h, callout_heading, resolved_pt, spotlight_idx, dt,
            gap_scale=c_scale,
        )
    elif pos == "bottom":
        band_h = min(resolved_h * 0.44, _estimate_horizontal_band_height(items, total_width, resolved_pt))
        vh = max(1.2, resolved_h - band_h - band_gap)
        vx, vy, vw = left, top, total_width
        _render_unboxed_callouts_horizontal(
            slide, items, left, top + vh + band_gap, total_width, band_h, resolved_pt, spotlight_idx, dt
        )
    else:  # pos == "top"
        band_h = min(resolved_h * 0.44, _estimate_horizontal_band_height(items, total_width, resolved_pt))
        vx, vy, vw = left, top + band_h + band_gap, total_width
        vh = max(1.2, resolved_h - band_h - band_gap)
        _render_unboxed_callouts_horizontal(
            slide, items, left, top, total_width, band_h, resolved_pt, spotlight_idx, dt
        )

    if image_path is not None:
        img_file = Path(image_path).resolve()
        if not img_file.exists():
            raise FileNotFoundError(f"Slide visual image not found: {img_file}")

        cap_str = str(visual_caption or "").strip()
        cap_pt = max(min_floor, float(typo["caption"]))
        px_w, px_h = _read_image_pixel_size(img_file)
        img_ar = float(px_w) / max(1.0, float(px_h))

        def _fit_image(avail_h: float) -> tuple[float, float, float, float]:
            box_ar = vw / avail_h
            if img_ar >= box_ar:
                pw = vw
                ph = vw / img_ar
            else:
                ph = avail_h
                pw = avail_h * img_ar
            px = vx + (vw - pw) / 2.0
            py = vy + (avail_h - ph) / 2.0
            return px, py, pw, ph

        actual_side_callout_h = 0.0
        if pos in ("right", "left") and len(slide.shapes) > start_shape_idx:
            c_shapes = list(slide.shapes)[start_shape_idx:]
            c_max_b = max((float(s.top or 0) + float(s.height or 0)) / 914400.0 for s in c_shapes)
            actual_side_callout_h = max(0.0, round(c_max_b - float(top), 3))

        if cap_str:
            m_cap = measure_text_layout(cap_str, max(2.2, vw - 0.04), cap_pt, bold=False, line_spacing=1.22)
            cap_h = round(max(0.28, float(m_cap["safe_height_in"]) + 0.04), 3)
        else:
            cap_h = 0.0
        cap_block_h = (cap_h + 0.12) if cap_str else 0.0
        avail_img_h = max(0.80, vh - cap_block_h)
        pic_x, pic_y, pic_w, pic_h = _fit_image(avail_img_h)

        cap_x = vx
        cap_w = vw
        if cap_str and pos in ("bottom", "top", "header_only") and pic_x > vx + 0.40:
            cap_x = pic_x
            cap_w = min(vx + vw - cap_x, max(pic_w, min(vw, 5.50)))
            m_cap_narrow = measure_text_layout(cap_str, max(2.2, cap_w - 0.04), cap_pt, bold=False, line_spacing=1.22)
            new_cap_h = round(max(0.28, float(m_cap_narrow["safe_height_in"]) + 0.04), 3)
            if new_cap_h > cap_h:
                cap_h = new_cap_h
                cap_block_h = cap_h + 0.12
                avail_img_h = max(0.80, vh - cap_block_h)
                pic_x, pic_y, pic_w, pic_h = _fit_image(avail_img_h)
                cap_x = pic_x if pic_x > vx + 0.40 else vx
                cap_w = min(vx + vw - cap_x, max(pic_w, min(vw, 5.50))) if cap_x > vx else vw

        # Cohesive vertical rhythm before whole-group optical centering:
        # - In side-by-side (`right`/`left`), align picture with the side callout band rather than pre-centering
        #   in empty full `vh`, preventing wide/short charts from detaching below short side callouts.
        # - In `header_only`, anchor at `vy` so Stage 2 optical centering places it at exact 40%/60% (<= 0.90").
        resolved_cap_y = round(vy + vh - cap_h, 3)
        if pos in ("right", "left") and actual_side_callout_h > 0.0:
            band_h = min(vh, max(pic_h + cap_block_h, actual_side_callout_h))
            pic_slot_h = max(pic_h, band_h - cap_block_h)
            pic_y = vy + max(0.0, (pic_slot_h - pic_h) / 2.0)
            if cap_str:
                resolved_cap_y = round(vy + band_h - cap_h, 3)
        elif pos == "header_only":
            pic_y = vy
            if cap_str:
                resolved_cap_y = round(pic_y + pic_h + 0.12, 3)

        slide.shapes.add_picture(
            str(img_file),
            Inches(pic_x),
            Inches(pic_y),
            width=Inches(pic_w),
            height=Inches(pic_h),
        )

        if cap_str:
            # Anchor caption flush with bottom edge of Zone 2 visual area (left-aligned to chart in wide horizontal modes)
            cap_y = resolved_cap_y
            cap_tb = slide.shapes.add_textbox(
                Inches(cap_x), Inches(cap_y), Inches(cap_w), Inches(cap_h)
            )
            tf_cap = cap_tb.text_frame
            tf_cap.word_wrap = True
            tf_cap.margin_left = Inches(0.02)
            tf_cap.margin_right = Inches(0.02)
            tf_cap.margin_top = Inches(0.01)
            tf_cap.margin_bottom = Inches(0.01)
            tf_cap.vertical_anchor = MSO_ANCHOR.TOP
            p_cap = tf_cap.paragraphs[0]
            p_cap.alignment = PP_ALIGN.LEFT
            p_cap.line_spacing = 1.22
            _populate_paragraph_runs(
                p_cap,
                cap_str,
                cap_pt,
                dt.get("ink_muted", "#64748B"),
                bold=False,
                bold_color_hex=dt.get("ink_primary", "#0F172A"),
            )

    vis_rect = (round(vx, 3), round(vy, 3), round(vw, 3), round(vh, 3))
    if image_path is not None:
        dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
        return _shift_coords_y(vis_rect, dy_in)
    return vis_rect


def draw_clean_mechanism_s4(
    slide,
    nodes_spec: Sequence[dict[str, object]],
    edges_spec: Sequence[dict[str, object]] | None = None,
    topology: str = "horizontal_chain",
    callouts: Sequence[object] | None = None,
    callout_position: str = "right",
    callout_heading: str | None = None,
    visual_ratio: float = 0.64,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    body_font_pt: float = 13.0,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> tuple[float, float, float, float]:
    """
    [F3-B / S4] Render Clean Native Vector Mechanism / Loop Diagram (strictly <= 5 concise nodes):
    - Module 1 Fixes (`L1473`): Removes heavy gray backing mat AND eliminates skinny skyscraper nodes.
    - When `horizontal_chain` has 4–5 nodes in a narrow visual area (`nw < 1.95"`), automatically uses a
      clean 2-row serpentine layout (`0 -> 1 -> down -> 2 -> left -> 3`) so nodes keep balanced landscape proportions.
    - Enforces `>= min_font_pt`, left-aligned multi-line node descriptions, and unboxed side callouts (`圖旁不疊卡`).
    """
    n_nodes = len(nodes_spec)
    if n_nodes > 5:
        raise ValueError(
            f"S4 clean mechanism diagram restricts node count to 3~5 (<= 5, got {n_nodes}). "
            "Never cram a full mindmap onto a slide; split into multiple slides instead."
        )

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.26)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, min_floor, resolved_pt, _typo, _sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.0, caller_default_pt=13.0
    )

    # Pre-estimate callout + diagram height to decide Direction 2 expansion factor cohesively
    norm_callouts = _normalize_callout_items(callouts)
    pos_norm = str(callout_position or "right").strip().lower() if norm_callouts else "header_only"
    ratio_clamped = max(0.45, min(0.82, float(visual_ratio)))
    est_callout_h = 0.0
    if norm_callouts and pos_norm in ("right", "left"):
        est_cw = total_width - 0.36 - (total_width - 0.36) * ratio_clamped
        est_callout_h = _estimate_vertical_callouts_height(norm_callouts, est_cw, callout_heading, resolved_pt, gap_scale=1.0)
    elif norm_callouts and pos_norm in ("top", "bottom"):
        est_callout_h = min(resolved_h * 0.44, _estimate_horizontal_band_height(norm_callouts, total_width, resolved_pt))
    est_base_h = max(est_callout_h, min(resolved_h, 3.60)) if pos_norm in ("right", "left", "header_only") else min(resolved_h, 3.60 + est_callout_h)
    mech_exp = _calc_zone2_expansion_factor(avail_h, est_base_h)

    vx, vy, vw, vh = draw_visual_callout_slide(
        slide,
        image_path=None,
        callout_position=callout_position,
        callouts=callouts,
        visual_ratio=visual_ratio,
        callout_heading=callout_heading,
        body_font_pt=resolved_pt,
        left=left,
        top=top,
        total_width=total_width,
        height=resolved_h,
        tokens=tokens,
        doc_theme_id=doc_theme_id,
        _callout_gap_scale=mech_exp,
    )
    if n_nodes == 0:
        dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
        return _shift_coords_y((vx, vy, vw, vh), dy_in)

    # Measure actual rendered callout span so side-by-side diagram aligns rhythmically with callouts
    actual_callout_h = 0.0
    if norm_callouts and pos_norm in ("right", "left") and len(slide.shapes) > start_shape_idx:
        c_shapes = list(slide.shapes)[start_shape_idx:]
        c_max_b = max((float(shp.top or 0) + float(shp.height or 0)) / 914400.0 for shp in c_shapes)
        actual_callout_h = max(0.0, round(c_max_b - float(top), 3))

    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_pri = pal["primary_accent"]
    theme_border = pal["border_card"]
    theme_card_bg = pal["bg_card"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    muted_bar = pal["muted_bar"]
    muted_acc = pal["muted_accent"]
    arrow_muted = pal["arrow_muted"]
    node_pt = max(min_floor, _round_half_pt(resolved_pt - 0.5))
    node_title_pt = _round_half_pt(node_pt + 1.5)

    # Clean direct canvas placement (gray mat backing abolished per Module 1)
    pad_x, pad_y = 0.06, 0.14
    ix, iy = vx + pad_x, vy + pad_y
    iw, ih = max(1.0, vw - 2.0 * pad_x), max(1.0, vh - 2.0 * pad_y)

    def _resolve_node_content(nd: dict[str, object]) -> tuple[str, list[str]]:
        kicker_s = _first_non_empty_str(nd, "kicker", "badge", "num", "step")
        t_s = _first_non_empty_str(nd, "title", "heading", "label", "name")
        if kicker_s and t_s:
            if not t_s.lower().startswith(kicker_s.lower()):
                t_s = f"{kicker_s} {t_s}"
        elif kicker_s and not t_s:
            t_s = kicker_s
        sub_s = _first_non_empty_str(nd, "subtitle", "sub")
        nd_lead = _first_non_empty_str(nd, "lead")
        if nd_lead == t_s:
            nd_lead = ""
        pairs = _extract_lead_body_items(nd, extra_lead=nd_lead, include_subtitle_as_body=False)
        lines: list[str] = []
        if sub_s:
            lines.extend(seg.strip() for seg in sub_s.splitlines() if seg.strip())
        for ld, bd in pairs:
            text_line = f"**{ld}**：{bd}" if (ld and bd) else (ld or bd)
            for seg in text_line.splitlines():
                seg_c = seg.strip()
                if seg_c and seg_c not in lines:
                    lines.append(seg_c)
        return t_s, lines

    def _measure_max_node_h(cand_w: float) -> float:
        tw = max(0.60, cand_w - 0.30)
        mh = 0.0
        for nd in nodes_spec:
            t_s, d_lines = _resolve_node_content(nd)
            h_need = 0.28
            if t_s:
                h_need += float(measure_text_layout(t_s, tw, node_title_pt, bold=True, line_spacing=1.20)["safe_height_in"])
            if d_lines:
                if t_s:
                    h_need += 0.06
                for li, dl in enumerate(d_lines):
                    h_need += float(measure_text_layout(dl, tw, node_pt, bold=False, line_spacing=1.24)["safe_height_in"])
                    if li < len(d_lines) - 1:
                        h_need += 0.03
            mh = max(mh, h_need)
        return round(max(1.15, mh + 0.18), 3)

    node_boxes: list[tuple[float, float, float, float]] = []
    topo = str(topology or "horizontal_chain").strip().lower()
    use_serpentine = False
    gap_mult = mech_exp if mech_exp > 1.0 else 1.0

    def _align_diag_top(tot_diag_h: float) -> float:
        if actual_callout_h > 0.0 and pos_norm in ("right", "left"):
            band_h = min(ih, max(tot_diag_h, actual_callout_h - 0.14))
            return iy + max(0.0, (band_h - tot_diag_h) / 2.0)
        if pos_norm == "header_only":
            # Anchor at `iy` so Stage 2 optical centering places it at exact ~40%/60% (<= 0.90" top buffer)
            return iy
        return iy + max(0.0, (ih - tot_diag_h) / 2.0)

    if topo == "hub_spoke" and n_nodes >= 3:
        hub_w = iw * 0.34
        n_right = n_nodes - 1
        r_gap = round((0.22 if n_right <= 3 else 0.14) * gap_mult, 3)
        rx_start = ix + hub_w + iw * 0.14
        rw = iw - hub_w - iw * 0.14
        r_h = min((ih - r_gap * (n_right - 1)) / n_right, max(1.15, _measure_max_node_h(rw)))
        tot_r_h = n_right * r_h + r_gap * (n_right - 1)
        ry_start = _align_diag_top(tot_r_h)
        hub_h = min(tot_r_h, max(1.55, _measure_max_node_h(hub_w) + 0.20))
        node_boxes.append((ix, ry_start + (tot_r_h - hub_h) / 2.0, hub_w, hub_h))
        for r_i in range(n_right):
            node_boxes.append((rx_start, ry_start + r_i * (r_h + r_gap), rw, r_h))
    elif topo == "cycle_loop" and n_nodes in (3, 4, 5):
        if n_nodes == 3:
            nw = iw * 0.44
            nh = min(ih * 0.42, _measure_max_node_h(nw))
            max_v_gap = max(0.24, ih - 2.0 * nh)
            v_gap = round(min(max_v_gap, max(min(max_v_gap, 0.48 * gap_mult), min(0.76 * gap_mult, 0.90))), 3)
            y0 = _align_diag_top(2.0 * nh + v_gap)
            y1 = y0 + nh + v_gap
            node_boxes = [
                (ix + (iw - nw) / 2.0, y0, nw, nh),
                (ix + iw - nw, y1, nw, nh),
                (ix, y1, nw, nh),
            ]
        elif n_nodes == 4:
            nw = iw * 0.42
            nh = min(ih * 0.42, _measure_max_node_h(nw))
            max_v_gap = max(0.24, ih - 2.0 * nh)
            v_gap = round(min(max_v_gap, max(min(max_v_gap, 0.48 * gap_mult), min(0.76 * gap_mult, 0.90))), 3)
            y0 = _align_diag_top(2.0 * nh + v_gap)
            y1 = y0 + nh + v_gap
            node_boxes = [
                (ix, y0, nw, nh),
                (ix + iw - nw, y0, nw, nh),
                (ix + iw - nw, y1, nw, nh),
                (ix, y1, nw, nh),
            ]
        else:  # n_nodes == 5
            top_corr = 0.30
            top_nw = (iw - 2 * top_corr) / 3.0
            nh = min(ih * 0.42, _measure_max_node_h(top_nw))
            max_v_gap = max(0.24, ih - 2.0 * nh)
            v_gap = round(min(max_v_gap, max(min(max_v_gap, 0.48 * gap_mult), min(0.76 * gap_mult, 0.90))), 3)
            y0 = _align_diag_top(2.0 * nh + v_gap)
            y1 = y0 + nh + v_gap
            bot_nw = iw * 0.43
            node_boxes = [
                (ix, y0, top_nw, nh),
                (ix + top_nw + top_corr, y0, top_nw, nh),
                (ix + 2 * (top_nw + top_corr), y0, top_nw, nh),
                (ix + iw - bot_nw, y1, bot_nw, nh),
                (ix, y1, bot_nw, nh),
            ]
    elif topo == "custom":
        for nd in nodes_spec:
            rx = float(nd.get("rx", 0.05))  # type: ignore[arg-type]
            ry = float(nd.get("ry", 0.15))  # type: ignore[arg-type]
            rw = float(nd.get("rw", 0.28))  # type: ignore[arg-type]
            rh = float(nd.get("rh", 0.55))  # type: ignore[arg-type]
            node_boxes.append((ix + rx * iw, iy + ry * ih, rw * iw, rh * ih))
    else:  # horizontal_chain default (with anti-skyscraper 2-row serpentine auto-switch!)
        corridor = 0.34 if n_nodes <= 3 else 0.26
        cand_nw = (iw - corridor * max(0, n_nodes - 1)) / n_nodes
        if not edges_spec and n_nodes in (4, 5) and cand_nw < 2.05:
            use_serpentine = True
            v_gap = min(0.78, round(0.52 * gap_mult, 3))
            if n_nodes == 4:
                h_gap = 0.44
                nw = (iw - h_gap) / 2.0
                nh = min((ih - v_gap) / 2.0, max(1.45, _measure_max_node_h(nw)))
                tot_h = 2.0 * nh + v_gap
                sy0 = _align_diag_top(tot_h)
                sy1 = sy0 + nh + v_gap
                # Clockwise serpentine: 0 (top-left) -> 1 (top-right) -> 2 (bot-right) -> 3 (bot-left)
                node_boxes = [
                    (ix, sy0, nw, nh),
                    (ix + nw + h_gap, sy0, nw, nh),
                    (ix + nw + h_gap, sy1, nw, nh),
                    (ix, sy1, nw, nh),
                ]
            else:  # 5 nodes: 3 on top, 2 on bottom (0 -> 1 -> 2 -> down -> 3 -> left -> 4)
                h_gap = 0.34
                top_nw = (iw - 2.0 * h_gap) / 3.0
                bot_nw = (iw - h_gap) / 2.0
                nh = min((ih - v_gap) / 2.0, max(1.40, _measure_max_node_h(top_nw)))
                tot_h = 2.0 * nh + v_gap
                sy0 = _align_diag_top(tot_h)
                sy1 = sy0 + nh + v_gap
                node_boxes = [
                    (ix, sy0, top_nw, nh),
                    (ix + top_nw + h_gap, sy0, top_nw, nh),
                    (ix + 2.0 * (top_nw + h_gap), sy0, top_nw, nh),
                    (ix + bot_nw + h_gap, sy1, bot_nw, nh),
                    (ix, sy1, bot_nw, nh),
                ]
        else:
            nw = cand_nw
            nh = min(ih * 0.62, max(1.45, _measure_max_node_h(nw)))
            ny = _align_diag_top(nh)
            for i in range(n_nodes):
                node_boxes.append((ix + i * (nw + corridor), ny, nw, nh))

    for idx, (nd, (nx, ny, nw, nh)) in enumerate(zip(nodes_spec, node_boxes)):
        is_spot = bool(nd.get("is_spotlight", idx == n_nodes - 1))
        acc_hex = str(nd.get("accent", theme_pri if is_spot else muted_acc))
        node_fill = str(nd.get("bg", _blend_hex(acc_hex, theme_card_bg, 0.16 if is_dark_theme else 0.08) if is_spot else theme_card_bg))
        nshape = _add_flat_shape(
            slide,
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(nx), Inches(ny), Inches(nw), Inches(nh),
        )
        nshape.adjustments[0] = 0.05
        nshape.fill.solid()
        nshape.fill.fore_color.rgb = hex_to_rgb_color(node_fill)
        nshape.line.color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_border, 0.45 if is_dark_theme else 0.40) if is_spot else theme_border)
        nshape.line.width = Pt(1.4 if is_spot else 1.1)

        # Single top accent strip inside node (de-noised spotlight)
        nbar = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(nx + 0.14), Inches(ny + 0.01), Inches(max(0.4, nw - 0.28)), Inches(0.055 if is_spot else 0.03),
        )
        nbar.fill.solid()
        nbar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else muted_bar)
        nbar.line.fill.background()

        tb = slide.shapes.add_textbox(
            Inches(nx + 0.14), Inches(ny + 0.12), Inches(max(0.45, nw - 0.28)), Inches(max(0.40, nh - 0.18))
        )
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.02)
        tf.margin_right = Inches(0.02)
        tf.margin_top = Inches(0.01)
        tf.margin_bottom = Inches(0.01)
        tf.vertical_anchor = MSO_ANCHOR.TOP
        nd_title, nd_lines = _resolve_node_content(nd)
        first_used = False
        if nd_title:
            p0 = tf.paragraphs[0]
            first_used = True
            p0.alignment = PP_ALIGN.LEFT
            p0.line_spacing = 1.20
            if nd_lines:
                p0.space_after = Pt(3.5)
            _populate_paragraph_runs(p0, nd_title, node_title_pt, acc_hex if is_spot else ink_pri, bold=True)

        for li, dl in enumerate(nd_lines):
            p_d = tf.add_paragraph() if first_used else tf.paragraphs[0]
            first_used = True
            p_d.alignment = PP_ALIGN.LEFT
            p_d.line_spacing = 1.24
            if li < len(nd_lines) - 1:
                p_d.space_after = Pt(2.0)
            _populate_paragraph_runs(p_d, dl, node_pt, ink_body, bold=False, bold_color_hex=ink_pri)

    def _add_arrow(shp_type, ax_in: float, ay_in: float, aw_in: float, ah_in: float, color_hex: str) -> None:
        arr = _add_flat_shape(slide, shp_type, Inches(ax_in), Inches(ay_in), Inches(aw_in), Inches(ah_in))
        arr.fill.solid()
        arr.fill.fore_color.rgb = hex_to_rgb_color(color_hex)
        arr.line.fill.background()

    # Draw arrows between nodes
    if edges_spec:
        for edge in edges_spec:
            u = int(edge.get("from", 0))  # type: ignore[arg-type]
            v = int(edge.get("to", 0))  # type: ignore[arg-type]
            if not (0 <= u < len(node_boxes) and 0 <= v < len(node_boxes)) or u == v:
                continue
            ux, uy, uw, uh = node_boxes[u]
            tx, ty, tw, th = node_boxes[v]
            ucx, ucy = ux + uw / 2.0, uy + uh / 2.0
            tcx, tcy = tx + tw / 2.0, ty + th / 2.0
            dx, dy = tcx - ucx, tcy - ucy
            e_col = str(edge.get("color", theme_pri))
            if abs(dx) >= abs(dy):
                ax_in = (ux + uw + 0.05) if dx > 0 else (tx + tw + 0.05)
                aw_in = max(0.16, abs(dx) - (uw + tw) / 2.0 - 0.10)
                ay_in = (ucy + tcy) / 2.0 - 0.12
                _add_arrow(MSO_SHAPE.RIGHT_ARROW if dx > 0 else MSO_SHAPE.LEFT_ARROW, ax_in, ay_in, aw_in, 0.24, e_col)
            else:
                ay_in = (uy + uh + 0.05) if dy > 0 else (ty + th + 0.05)
                ah_in = max(0.16, abs(dy) - (uh + th) / 2.0 - 0.10)
                ax_in = (ucx + tcx) / 2.0 - 0.12
                _add_arrow(MSO_SHAPE.DOWN_ARROW if dy > 0 else MSO_SHAPE.UP_ARROW, ax_in, ay_in, 0.24, ah_in, e_col)
    elif use_serpentine:
        for i in range(len(node_boxes) - 1):
            ux, uy, uw, uh = node_boxes[i]
            tx, ty, tw, th = node_boxes[i + 1]
            ucx, ucy = ux + uw / 2.0, uy + uh / 2.0
            tcx, tcy = tx + tw / 2.0, ty + th / 2.0
            dx, dy = tcx - ucx, tcy - ucy
            col = theme_pri if i == len(node_boxes) - 2 else arrow_muted
            if abs(dy) > 0.35:
                ay_in = uy + uh + 0.08
                ah_in = max(0.18, ty - (uy + uh) - 0.16)
                ax_in = min(ux + uw, tx + tw) - min(uw, tw) * 0.5 - 0.12
                _add_arrow(MSO_SHAPE.DOWN_ARROW, ax_in, ay_in, 0.24, ah_in, col)
            elif dx > 0:
                ax_in = ux + uw + 0.04
                aw_in = max(0.18, tx - (ux + uw) - 0.08)
                _add_arrow(MSO_SHAPE.RIGHT_ARROW, ax_in, ucy - 0.11, aw_in, 0.22, col)
            else:
                ax_in = tx + tw + 0.04
                aw_in = max(0.18, ux - (tx + tw) - 0.08)
                _add_arrow(MSO_SHAPE.LEFT_ARROW, ax_in, ucy - 0.11, aw_in, 0.22, col)
    elif topo == "hub_spoke" and n_nodes >= 3:
        # Clean orthogonal tree-bus connector: hub trunk -> vertical spine -> spoke arrows (never floating in mid-air!)
        hx, hy, hw, hh = node_boxes[0]
        spoke_boxes = node_boxes[1:]
        spoke_rx = spoke_boxes[0][0]
        corr_w = max(0.24, spoke_rx - (hx + hw))
        bus_x = hx + hw + corr_w * 0.36
        hub_cy = hy + hh / 2.0
        y_first = spoke_boxes[0][1] + spoke_boxes[0][3] / 2.0
        y_last = spoke_boxes[-1][1] + spoke_boxes[-1][3] / 2.0

        # Horizontal trunk from hub right edge to vertical bus
        trunk = _add_flat_shape(
            slide, MSO_SHAPE.RECTANGLE,
            Inches(hx + hw + 0.02), Inches(hub_cy - 0.015), Inches(max(0.08, bus_x - (hx + hw + 0.02))), Inches(0.03),
        )
        trunk.fill.solid()
        trunk.fill.fore_color.rgb = hex_to_rgb_color(theme_pri)
        trunk.line.fill.background()

        # Vertical spine spanning first spoke center to last spoke center
        v_bus = _add_flat_shape(
            slide, MSO_SHAPE.RECTANGLE,
            Inches(bus_x - 0.015), Inches(y_first - 0.015), Inches(0.03), Inches(max(0.06, y_last - y_first + 0.03)),
        )
        v_bus.fill.solid()
        v_bus.fill.fore_color.rgb = hex_to_rgb_color(theme_pri)
        v_bus.line.fill.background()

        # Horizontal branch arrows from vertical spine cleanly into each spoke
        for rx, ry, _rw, rh in spoke_boxes:
            arr_x = bus_x + 0.015
            arr_w = max(0.18, rx - arr_x - 0.06)
            arr_y = ry + rh / 2.0 - 0.10
            _add_arrow(MSO_SHAPE.RIGHT_ARROW, arr_x, arr_y, arr_w, 0.20, theme_pri)
    elif topo == "cycle_loop" and n_nodes == 3:
        top_b, br_b, bl_b = node_boxes[0], node_boxes[1], node_boxes[2]
        raw_vgap = br_b[1] - (top_b[1] + top_b[3])
        v_arr_h = min(0.46, max(0.20, raw_vgap - 0.16))
        v_arr_y = top_b[1] + top_b[3] + (raw_vgap - v_arr_h) / 2.0
        _add_arrow(MSO_SHAPE.DOWN_ARROW, br_b[0] + br_b[2] * 0.35 - 0.12, v_arr_y, 0.24, v_arr_h, theme_pri)
        _add_arrow(MSO_SHAPE.LEFT_ARROW, bl_b[0] + bl_b[2] + 0.06, bl_b[1] + bl_b[3] / 2.0 - 0.11, max(0.18, br_b[0] - (bl_b[0] + bl_b[2]) - 0.12), 0.22, theme_pri)
        _add_arrow(MSO_SHAPE.UP_ARROW, bl_b[0] + bl_b[2] * 0.65 - 0.12, v_arr_y, 0.24, v_arr_h, theme_pri)
    elif topo == "cycle_loop" and n_nodes == 4:
        for u, v in [(0, 1), (1, 2), (2, 3), (3, 0)]:
            ux, uy, uw, uh = node_boxes[u]
            tx, ty, tw, th = node_boxes[v]
            dx, dy = (tx - ux), (ty - uy)
            if abs(dx) >= abs(dy):
                ax_in = (ux + uw + 0.06) if dx > 0 else (tx + tw + 0.06)
                aw_in = max(0.18, abs(dx) - uw - 0.12)
                ay_in = uy + uh / 2.0 - 0.11
                _add_arrow(MSO_SHAPE.RIGHT_ARROW if dx > 0 else MSO_SHAPE.LEFT_ARROW, ax_in, ay_in, aw_in, 0.22, theme_pri)
            else:
                raw_vgap = abs(dy) - uh
                ah_in = min(0.46, max(0.20, raw_vgap - 0.16))
                top_edge = (uy + uh) if dy > 0 else (ty + th)
                ay_in = top_edge + (raw_vgap - ah_in) / 2.0
                ax_in = ux + uw / 2.0 - 0.12
                _add_arrow(MSO_SHAPE.DOWN_ARROW if dy > 0 else MSO_SHAPE.UP_ARROW, ax_in, ay_in, 0.24, ah_in, theme_pri)
    elif topo == "cycle_loop" and n_nodes == 5:
        for i_top in (0, 1):
            ux, uy, uw, uh = node_boxes[i_top]
            tx = node_boxes[i_top + 1][0]
            _add_arrow(MSO_SHAPE.RIGHT_ARROW, ux + uw + 0.04, uy + uh / 2.0 - 0.11, max(0.18, tx - (ux + uw) - 0.08), 0.22, theme_pri)
        raw_vgap = node_boxes[3][1] - (node_boxes[0][1] + node_boxes[0][3])
        v_arr_h = min(0.46, max(0.20, raw_vgap - 0.16))
        v_arr_y = node_boxes[0][1] + node_boxes[0][3] + (raw_vgap - v_arr_h) / 2.0
        _add_arrow(MSO_SHAPE.DOWN_ARROW, node_boxes[2][0] + node_boxes[2][2] / 2.0 - 0.12, v_arr_y, 0.24, v_arr_h, theme_pri)
        _add_arrow(MSO_SHAPE.LEFT_ARROW, node_boxes[4][0] + node_boxes[4][2] + 0.06, node_boxes[4][1] + node_boxes[4][3] / 2.0 - 0.11, max(0.18, node_boxes[3][0] - (node_boxes[4][0] + node_boxes[4][2]) - 0.12), 0.22, theme_pri)
        _add_arrow(MSO_SHAPE.UP_ARROW, node_boxes[0][0] + node_boxes[0][2] / 2.0 - 0.12, v_arr_y, 0.24, v_arr_h, theme_pri)
    else:
        for i in range(len(node_boxes) - 1):
            ux, uy, uw, uh = node_boxes[i]
            tx, ty, tw, th = node_boxes[i + 1]
            arr_x = ux + uw + 0.05
            arr_w = max(0.18, tx - (ux + uw) - 0.10)
            arr_y = uy + uh / 2.0 - 0.11
            _add_arrow(MSO_SHAPE.RIGHT_ARROW, arr_x, arr_y, arr_w, 0.22, theme_pri if i == len(node_boxes) - 2 else arrow_muted)

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y((vx, vy, vw, vh), dy_in)


# -------------------------------------------------------------------------
# Family 4 | Comparison & Matrix (`F4-A` S5, `F4-B` S11)
# -------------------------------------------------------------------------

def draw_quadrant_matrix_s5(
    slide,
    quadrants_spec: Sequence[dict[str, object]],
    x_axis_label: str = "",
    y_axis_label: str = "",
    spotlight_idx: int | None = 1,
    borderless: bool = True,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    body_font_pt: float = 12.5,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> list[tuple[float, float, float, float]]:
    """
    [F4-A / S5] Render 2x2 Orthogonal Strategy Quadrant Matrix (Module 1 & 2 Upgraded):
    - `borderless=True` (default): crisp orthogonal crosshair axes, 3 unboxed quadrants, soft tint wash on spotlight quadrant only.
    - `borderless=False`: optional single-layer light cards.
    - Strict `MSO_ANCHOR.TOP` natural flow Lead/Body stacking inside every quadrant, `>= min_font_pt` axis labels.
    `quadrants_spec` order: [Top-Left (Q2), Top-Right (Q1), Bottom-Left (Q3), Bottom-Right (Q4)].
    """
    if not quadrants_spec:
        return []

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.82)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    q_exp = _calc_zone2_expansion_factor(avail_h, resolved_h)
    dt, min_floor, resolved_pt, typo, sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=12.5, caller_default_pt=12.5
    )
    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_pri = pal["primary_accent"]
    theme_border = pal["border_card"]
    theme_card_bg = pal["bg_card"]
    theme_canvas = pal["bg_canvas"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    ink_muted = pal["ink_muted"]
    arrow_muted = pal["arrow_muted"]
    muted_acc = pal["muted_accent"]
    ls = float(sp.get("line_spacing", 1.28))

    axis_pt = max(min_floor, float(typo["caption"]))
    q_title_pt = _round_half_pt(resolved_pt + 2.0)
    kicker_pt = float(typo["kicker"])
    sub_pt = float(typo["subtitle"])
    lead_pt = float(typo["lead"])

    axis_top_reserve = max(0.36, round((axis_pt * 1.45) / 72.0 + 0.10, 3)) if y_axis_label else 0.0
    axis_bot_reserve = max(0.36, round((axis_pt * 1.45) / 72.0 + 0.10, 3)) if x_axis_label else 0.0
    grid_top = round(top + axis_top_reserve, 3)
    grid_h = max(2.2, round(resolved_h - axis_top_reserve - axis_bot_reserve, 3))
    cross_gap = round(0.30 * q_exp, 3) if q_exp > 1.0 else 0.30
    qw = (total_width - cross_gap) / 2.0
    qh = (grid_h - cross_gap) / 2.0

    # Orthogonal crosshair lines with subtle directional end arrows
    cx_mid = left + qw + cross_gap / 2.0
    cy_mid = grid_top + qh + cross_gap / 2.0

    v_line = _add_flat_shape(slide, MSO_SHAPE.RECTANGLE, Inches(cx_mid - 0.012), Inches(grid_top + 0.10), Inches(0.024), Inches(max(0.5, grid_h - 0.10)))
    v_line.fill.solid()
    v_line.fill.fore_color.rgb = hex_to_rgb_color(arrow_muted)
    v_line.line.fill.background()

    v_tip = _add_flat_shape(slide, MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(cx_mid - 0.07), Inches(grid_top), Inches(0.14), Inches(0.14))
    v_tip.fill.solid()
    v_tip.fill.fore_color.rgb = hex_to_rgb_color(muted_acc)
    v_tip.line.fill.background()

    h_line = _add_flat_shape(slide, MSO_SHAPE.RECTANGLE, Inches(left), Inches(cy_mid - 0.012), Inches(max(0.5, total_width - 0.10)), Inches(0.024))
    h_line.fill.solid()
    h_line.fill.fore_color.rgb = hex_to_rgb_color(arrow_muted)
    h_line.line.fill.background()

    h_tip = _add_flat_shape(slide, MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(left + total_width - 0.14), Inches(cy_mid - 0.07), Inches(0.14), Inches(0.14))
    h_tip.rotation = 90.0
    h_tip.fill.solid()
    h_tip.fill.fore_color.rgb = hex_to_rgb_color(muted_acc)
    h_tip.line.fill.background()

    if y_axis_label and str(y_axis_label).strip():
        y_str = f"▲ {str(y_axis_label).strip()}"
        yb_w = min(total_width, max(5.6, calc_pill_width(y_str, font_pt=axis_pt, pad_in=0.30)))
        yb_x = max(left, min(left + total_width - yb_w, cx_mid - yb_w / 2.0))
        yb = slide.shapes.add_textbox(Inches(yb_x), Inches(top), Inches(yb_w), Inches(axis_top_reserve - 0.02))
        tf_y = yb.text_frame
        tf_y.word_wrap = True
        tf_y.vertical_anchor = MSO_ANCHOR.MIDDLE
        py = tf_y.paragraphs[0]
        py.alignment = PP_ALIGN.CENTER
        _populate_paragraph_runs(py, y_str, axis_pt, ink_muted, bold=True)

    if x_axis_label and str(x_axis_label).strip():
        x_str = f"{str(x_axis_label).strip()} ▶"
        xb_w = min(total_width, max(5.6, calc_pill_width(x_str, font_pt=axis_pt, pad_in=0.30)))
        xb = slide.shapes.add_textbox(
            Inches(left + total_width - xb_w), Inches(grid_top + grid_h + 0.04), Inches(xb_w), Inches(axis_bot_reserve - 0.04)
        )
        tf_x = xb.text_frame
        tf_x.word_wrap = True
        tf_x.vertical_anchor = MSO_ANCHOR.MIDDLE
        px = tf_x.paragraphs[0]
        px.alignment = PP_ALIGN.RIGHT
        _populate_paragraph_runs(px, x_str, axis_pt, ink_muted, bold=True)

    positions = [
        (left, grid_top),
        (left + qw + cross_gap, grid_top),
        (left, grid_top + qh + cross_gap),
        (left + qw + cross_gap, grid_top + qh + cross_gap),
    ]

    coords: list[tuple[float, float, float, float]] = []
    for idx in range(min(4, len(quadrants_spec))):
        q = quadrants_spec[idx]
        qx, qy = positions[idx]
        is_spot = (spotlight_idx == idx) if spotlight_idx is not None else bool(q.get("is_spotlight", False))
        acc_hex = str(q.get("accent", theme_pri if is_spot else muted_acc))

        if borderless:
            if is_spot:
                wash = _add_flat_shape(
                    slide,
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    Inches(qx), Inches(qy), Inches(qw), Inches(qh),
                )
                wash.adjustments[0] = 0.035
                wash.fill.solid()
                wash.fill.fore_color.rgb = hex_to_rgb_color(str(q.get("bg", _blend_hex(acc_hex, theme_canvas, 0.14 if is_dark_theme else 0.085))))
                wash.line.fill.background()

                bar = _add_flat_shape(
                    slide,
                    MSO_SHAPE.RECTANGLE,
                    Inches(qx), Inches(qy + 0.08), Inches(0.06), Inches(max(0.50, qh - 0.16)),
                )
                bar.fill.solid()
                bar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex)
                bar.line.fill.background()
        else:
            qbox = _add_flat_shape(
                slide,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(qx), Inches(qy), Inches(qw), Inches(qh),
            )
            qbox.adjustments[0] = 0.035
            qbox.fill.solid()
            qbox.fill.fore_color.rgb = hex_to_rgb_color(str(q.get("bg", _blend_hex(acc_hex, theme_card_bg, 0.14 if is_dark_theme else 0.07) if is_spot else theme_card_bg)))
            qbox.line.color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_border, 0.45 if is_dark_theme else 0.35) if is_spot else theme_border)
            qbox.line.width = Pt(1.3 if is_spot else 1.0)
            if is_spot:
                tbar = _add_flat_shape(
                    slide,
                    MSO_SHAPE.RECTANGLE,
                    Inches(qx + 0.14), Inches(qy + 0.01), Inches(max(0.4, qw - 0.28)), Inches(0.055),
                )
                tbar.fill.solid()
                tbar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex)
                tbar.line.fill.background()

        pad_l = 0.18 if (is_spot or not borderless) else 0.08
        inner_w = max(0.70, qw - pad_l - 0.14)
        cur_y = round(qy + 0.10, 3)

        q_kicker = _first_non_empty_str(q, "kicker", "badge", "num", "step")
        q_title = _first_non_empty_str(q, "title", "heading", "label", "name")
        q_sub = _first_non_empty_str(q, "subtitle", "sub")
        q_lead = _first_non_empty_str(q, "lead")
        if q_lead == q_title:
            q_lead = ""
        raw_pairs = _extract_lead_body_items(q, extra_lead=q_lead)
        parsed_pts: list[tuple[str, str, float]] = []
        for ld, bd in raw_pairs:
            parsed_pts.append((ld, bd, _measure_lead_body_item_height(ld, bd, inner_w, lead_pt, resolved_pt, line_spacing=ls)))

        est_pts_h = sum(p[2] for p in parsed_pts) + 0.05 * max(0, len(parsed_pts) - 1) if parsed_pts else 0.0
        if q_kicker or q_sub:
            qt_h = _measure_three_tier_header(q_kicker, q_title, q_sub, inner_w, kicker_pt, q_title_pt, sub_pt)
            if q_kicker and q_title and q_sub and parsed_pts and (cur_y + qt_h + 0.06 + est_pts_h) > (qy + qh - 0.06):
                q_kicker = f"{q_kicker} · {q_sub}"
                q_sub = ""
                qt_h = _measure_three_tier_header(q_kicker, q_title, q_sub, inner_w, kicker_pt, q_title_pt, sub_pt)
            hdr_box_h = round(min(qh * 0.54, qt_h + 0.02), 3)
            _render_three_tier_header(
                slide, qx + pad_l, cur_y, inner_w, hdr_box_h,
                q_kicker, q_title, q_sub, kicker_pt, q_title_pt, sub_pt,
                acc_hex if is_spot else ink_muted, acc_hex if is_spot else ink_pri, ink_muted,
            )
            cur_y = round(cur_y + hdr_box_h + 0.04, 3)
        elif q_title:
            m_qt = measure_text_layout(q_title, inner_w, q_title_pt, bold=True, line_spacing=1.18)
            qt_h = round(max(0.30, float(m_qt["safe_height_in"])), 3)
            qt_tb = slide.shapes.add_textbox(Inches(qx + pad_l), Inches(cur_y), Inches(inner_w), Inches(qt_h))
            tf_qt = qt_tb.text_frame
            tf_qt.word_wrap = True
            tf_qt.vertical_anchor = MSO_ANCHOR.TOP
            tf_qt.margin_left = Inches(0.02)
            tf_qt.margin_top = Inches(0.01)
            p_qt = tf_qt.paragraphs[0]
            p_qt.alignment = PP_ALIGN.LEFT
            p_qt.line_spacing = 1.18
            _populate_paragraph_runs(p_qt, q_title, q_title_pt, acc_hex if is_spot else ink_pri, bold=True)
            cur_y = round(cur_y + qt_h + 0.06, 3)

        if parsed_pts:
            avail_q = max(0.34, (qy + qh - 0.06) - cur_y)
            raw_sum = sum(p[2] for p in parsed_pts)
            min_q_gap = 0.05 * max(0, len(parsed_pts) - 1)
            if len(parsed_pts) > 1 and (raw_sum + min_q_gap) > avail_q:
                _render_compact_lead_body_stack(
                    slide,
                    x=qx + pad_l,
                    y=cur_y,
                    w=inner_w,
                    h=avail_q,
                    items=[(ld, bd) for ld, bd, _ih in parsed_pts],
                    lead_pt=lead_pt,
                    body_pt=resolved_pt,
                    lead_hex=ink_pri,
                    body_hex=ink_body,
                    bold_color_hex=ink_pri,
                    line_spacing=min(ls, 1.15),
                    para_space_after_pt=2.0,
                )
            else:
                q_gap_cap = round(0.14 * q_exp, 3) if q_exp > 1.0 else 0.14
                q_gap = min(q_gap_cap, max(0.05, (avail_q - raw_sum) / max(1, len(parsed_pts) - 1))) if len(parsed_pts) > 1 else 0.0
                for ld, bd, ih in parsed_pts:
                    rem = max(0.26, (qy + qh - 0.06) - cur_y)
                    bh = round(min(rem, ih + 0.02), 3)
                    _render_lead_body_box(
                        slide, qx + pad_l, cur_y, inner_w, bh,
                        ld, bd, lead_pt, resolved_pt, ink_pri, ink_body, ink_pri, line_spacing=ls,
                    )
                    cur_y = round(cur_y + bh + q_gap, 3)

        coords.append((round(qx, 3), round(qy, 3), round(qw, 3), round(qh, 3)))

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y(coords, dy_in)


def _set_table_cell_ooxml_style(
    cell,
    fill_hex: str | None = None,
    top_border: tuple[float, str] | None = None,
    bottom_border: tuple[float, str] | None = None,
    margin_l_in: float = 0.12,
    margin_r_in: float = 0.12,
    margin_t_in: float = 0.08,
    margin_b_in: float = 0.08,
    anchor=MSO_ANCHOR.TOP,
) -> None:
    """
    Style a native PowerPoint table cell cleanly as an academic Three-Line Table (`極簡三線表`):
    - Removes all vertical gridlines (`lnL` / `lnR` = `<a:noFill/>`).
    - Sets explicit OOXML `<a:lnT>` / `<a:lnB>` and `<a:solidFill>` in strict ECMA-376 `<a:tcPr>` element order.
    """
    from lxml import etree  # type: ignore

    a_ns = _OMML_A_NS
    cell.margin_left = Inches(margin_l_in)
    cell.margin_right = Inches(margin_r_in)
    cell.margin_top = Inches(margin_t_in)
    cell.margin_bottom = Inches(margin_b_in)
    cell.vertical_anchor = anchor

    tc_pr = cell._tc.get_or_add_tcPr()
    for tag in ("lnL", "lnR", "lnT", "lnB", "solidFill", "noFill"):
        for old in list(tc_pr.findall(f"{{{a_ns}}}{tag}")):
            tc_pr.remove(old)

    def _make_ln(tag_name: str, spec: tuple[float, str] | None):
        ln = etree.Element(f"{{{a_ns}}}{tag_name}")
        if spec is None:
            ln.set("w", "0")
            etree.SubElement(ln, f"{{{a_ns}}}noFill")
        else:
            pt_w, hex_c = spec
            ln.set("w", str(int(round(float(pt_w) * 12700))))
            ln.set("cap", "flat")
            ln.set("cmpd", "sng")
            sf = etree.SubElement(ln, f"{{{a_ns}}}solidFill")
            sc = etree.SubElement(sf, f"{{{a_ns}}}srgbClr")
            sc.set("val", _clean_omml_hex(hex_c) or "0F172A")
        return ln

    # Strict ECMA-376 CT_TableCellProperties child order: lnL, lnR, lnT, lnB, ..., fill
    insert_els = [
        _make_ln("lnL", None),
        _make_ln("lnR", None),
        _make_ln("lnT", top_border),
        _make_ln("lnB", bottom_border),
    ]
    for idx_i, el in enumerate(insert_els):
        tc_pr.insert(idx_i, el)

    if fill_hex:
        sf = etree.Element(f"{{{a_ns}}}solidFill")
        sc = etree.SubElement(sf, f"{{{a_ns}}}srgbClr")
        sc.set("val", _clean_omml_hex(fill_hex) or "FFFFFF")
        tc_pr.insert(4, sf)
    else:
        tc_pr.insert(4, etree.Element(f"{{{a_ns}}}noFill"))


def draw_comparison_table_slide(
    slide,
    headers: Sequence[str],
    rows: Sequence[Sequence[object]],
    spotlight_col: int | None = None,
    col_widths: Sequence[float] | None = None,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    body_font_pt: float | None = None,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> tuple[float, float, float, float]:
    """
    [F4-B / S11] Render Minimal Consulting / Academic Three-Line Comparison Table (native PowerPoint Table):
    - Zero vertical borders, strong top/header/bottom rules (`1.5pt #0F172A`), ultra-light row hairlines (`0.75pt #E2E8F0`).
    - Optional single-column soft spotlight (`spotlight_col`) with tinted fill and accent header text.
    - Content-Driven row heights measured via `measure_text_layout()`; all cell fonts `>= min_font_pt`.
    Returns `(left, top, total_width, actual_table_h)`.
    """
    hdr_list = [str(h or "").strip() for h in (headers or [])]
    n_cols = len(hdr_list)
    if n_cols == 0:
        return (round(left, 3), round(top, 3), round(total_width, 3), 0.0)

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.20)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, _min_floor, resolved_pt, _typo, sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.0
    )
    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_pri = pal["primary_accent"]
    theme_canvas = pal["bg_canvas"]
    theme_card_bg = pal["bg_card"]
    theme_border = pal["border_card"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    div_subtle = pal["divider_subtle"]
    spot_bg = _blend_hex(theme_pri, theme_card_bg, 0.16 if is_dark_theme else 0.09)
    hdr_bg = _blend_hex(theme_card_bg, theme_border, 0.30) if is_dark_theme else _blend_hex(theme_canvas, "#E2E8F0", 0.25)
    alt_row_bg = _blend_hex(theme_canvas, theme_card_bg, 0.45)
    ls = float(sp.get("line_spacing", 1.24))

    hdr_pt = _round_half_pt(resolved_pt + 0.5)
    row_list = [list(r) for r in (rows or [])]
    n_rows = 1 + len(row_list)

    if col_widths and len(col_widths) == n_cols:
        tot_w = sum(float(c) for c in col_widths) or float(n_cols)
        resolved_col_ws = [total_width * (float(c) / tot_w) for c in col_widths]
    else:
        if n_cols >= 3:
            first_w = round(total_width * 0.22, 3)
            rem_w = (total_width - first_w) / (n_cols - 1)
            resolved_col_ws = [first_w] + [rem_w] * (n_cols - 1)
        else:
            resolved_col_ws = [total_width / n_cols] * n_cols

    # Measure exact Content-Driven row heights
    row_heights: list[float] = []
    hdr_h = 0.42
    for c_i, h_txt in enumerate(hdr_list):
        m = measure_text_layout(h_txt, max(0.50, resolved_col_ws[c_i] - 0.24), hdr_pt, bold=True, line_spacing=1.18)
        hdr_h = max(hdr_h, float(m["safe_height_in"]) + 0.18)
    row_heights.append(round(hdr_h, 3))

    for r_vals in row_list:
        rh = 0.44
        for c_i in range(n_cols):
            val_s = str(r_vals[c_i] if c_i < len(r_vals) else "").strip()
            m = measure_text_layout(val_s, max(0.50, resolved_col_ws[c_i] - 0.24), resolved_pt, bold=(c_i == 0), line_spacing=ls)
            rh = max(rh, float(m["safe_height_in"]) + 0.18)
        row_heights.append(round(rh, 3))

    sum_h = sum(row_heights)
    tbl_exp = _calc_zone2_expansion_factor(avail_h, sum_h)
    cell_pad_y = round(min(0.16, 0.08 * tbl_exp), 3) if tbl_exp > 1.0 else 0.08
    if tbl_exp > 1.0 and sum_h > 0:
        target_tbl_h = min(max(sum_h, avail_h - 0.50), sum_h * (1.0 + (tbl_exp - 1.0) * 0.72))
        if target_tbl_h > sum_h + 0.04:
            grow_ratio = target_tbl_h / sum_h
            row_heights = [round(rh * grow_ratio, 3) for rh in row_heights]
            sum_h = sum(row_heights)

    tbl_budget_h = max(resolved_h, avail_h) if tbl_exp > 1.0 else resolved_h
    if sum_h > tbl_budget_h and sum_h > 0:
        scale_f = tbl_budget_h / sum_h
        row_heights = [max(0.34, round(rh * scale_f, 3)) for rh in row_heights]
    actual_tbl_h = round(min(tbl_budget_h, sum(row_heights)), 3)

    tbl_shape = slide.shapes.add_table(
        n_rows, n_cols, Inches(left), Inches(top), Inches(total_width), Inches(actual_tbl_h)
    )
    table = tbl_shape.table

    # Disable PowerPoint built-in blue theme table banding
    with suppress(AttributeError, TypeError):
        tbl_pr = table._tbl.tblPr
        if tbl_pr is not None:
            for attr in ("firstRow", "bandRow", "bandCol", "firstCol", "lastCol", "lastRow"):
                tbl_pr.set(attr, "0")
            for style_id in list(tbl_pr.findall(f"{{{_OMML_A_NS}}}tableStyleId")):
                tbl_pr.remove(style_id)

    for c_i, cw in enumerate(resolved_col_ws):
        table.columns[c_i].width = Inches(cw)

    # Render Header Row (Three-Line top & bottom strong rules)
    table.rows[0].height = Inches(row_heights[0])
    for c_i, h_txt in enumerate(hdr_list):
        cell = table.cell(0, c_i)
        is_spot = spotlight_col is not None and c_i == spotlight_col
        _set_table_cell_ooxml_style(
            cell,
            fill_hex=spot_bg if is_spot else hdr_bg,
            top_border=(1.5, theme_pri if is_spot else ink_pri),
            bottom_border=(1.5, theme_pri if is_spot else ink_pri),
            margin_l_in=0.12,
            margin_r_in=0.12,
            margin_t_in=cell_pad_y,
            margin_b_in=cell_pad_y,
            anchor=MSO_ANCHOR.MIDDLE,
        )
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        p.line_spacing = 1.18
        _populate_paragraph_runs(p, h_txt, hdr_pt, theme_pri if is_spot else ink_pri, bold=True)

    # Render Data Rows
    for r_i, r_vals in enumerate(row_list, start=1):
        table.rows[r_i].height = Inches(row_heights[r_i])
        is_last = r_i == len(row_list)
        for c_i in range(n_cols):
            cell = table.cell(r_i, c_i)
            val_s = str(r_vals[c_i] if c_i < len(r_vals) else "").strip()
            is_spot = spotlight_col is not None and c_i == spotlight_col
            cell_bg = spot_bg if is_spot else (theme_card_bg if r_i % 2 == 1 else alt_row_bg)
            _set_table_cell_ooxml_style(
                cell,
                fill_hex=cell_bg,
                top_border=None,
                bottom_border=(1.5, ink_pri) if is_last else (0.75, div_subtle),
                margin_l_in=0.12,
                margin_r_in=0.12,
                margin_t_in=cell_pad_y,
                margin_b_in=cell_pad_y,
                anchor=MSO_ANCHOR.TOP,
            )
            tf = cell.text_frame
            tf.word_wrap = True
            lines = val_s.splitlines() or [val_s]
            for l_i, seg in enumerate(lines):
                p = tf.paragraphs[0] if l_i == 0 else tf.add_paragraph()
                p.alignment = PP_ALIGN.LEFT
                p.line_spacing = ls
                _populate_paragraph_runs(
                    p,
                    seg,
                    resolved_pt,
                    ink_pri if c_i == 0 else ink_body,
                    bold=(c_i == 0),
                    bold_color_hex=theme_pri if is_spot else ink_pri,
                )

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y((round(left, 3), round(top, 3), round(total_width, 3), actual_tbl_h), dy_in)


def draw_kpi_strip_slide(
    slide,
    kpi_items: Sequence[dict[str, object]],
    insight_blocks: Sequence[object] = (),
    spotlight_idx: int | None = 0,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    body_font_pt: float | None = None,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> list[tuple[float, float, float, float]]:
    """
    [F5-B / S10] Render Top Quantitative KPI Metric Strip (2–4 KPIs) + Lower Unboxed Insight Zone:
    - Ideal for cross-case quantitative summaries (never crammed inside Matplotlib charts!).
    - Top strip is clean & unboxed with vertical hairlines (spotlight KPI gets top accent bar + soft wash).
    - Lower insight blocks flow TOP-aligned below a crisp horizontal divider.
    Returns `[kpi_strip_rect, *insight_rects]`.
    """
    k_list = list(kpi_items or [])[:4]
    if not k_list:
        return []

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.66)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, min_floor, resolved_pt, typo, sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.5
    )
    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_pri = pal["primary_accent"]
    theme_canvas = pal["bg_canvas"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    ink_muted = pal["ink_muted"]
    div_strong = pal["divider_strong"]
    div_subtle = pal["divider_subtle"]
    muted_acc = pal["muted_accent"]
    ls = float(sp.get("line_spacing", 1.30))

    n_kpi = len(k_list)
    k_gap = 0.24
    k_col_w = (total_width - k_gap * (n_kpi - 1)) / n_kpi
    val_pt_base = 34.0 if n_kpi <= 3 else 28.0
    lbl_pt = max(min_floor, _round_half_pt(resolved_pt + 0.5))
    note_pt = max(min_floor, float(typo["caption"]))
    lead_pt = float(typo["lead"])

    def _resolve_kpi_fields(item: dict[str, object]) -> tuple[str, str, str]:
        v_s = _first_non_empty_str(item, "value", "stat", "metric", "number", "kpi", "num")
        l_s = _first_non_empty_str(item, "label", "title", "heading", "name")
        lead_s = _first_non_empty_str(item, "lead")
        if not l_s and lead_s:
            l_s, lead_s = lead_s, ""
        elif lead_s == l_s:
            lead_s = ""
        delta_s = _first_non_empty_str(item, "delta")
        extra_n = _first_non_empty_str(item, "note", "detail", "desc", "body", "subtitle", "sub", "text", "caption")

        note_lines: list[str] = []
        if lead_s and delta_s and delta_s != lead_s:
            note_lines.append(f"{lead_s}｜{delta_s}" if (len(lead_s) + len(delta_s) <= 22) else f"{lead_s}\n{delta_s}")
        elif lead_s:
            note_lines.append(lead_s)
        elif delta_s:
            note_lines.append(delta_s)

        if extra_n and extra_n not in (lead_s, delta_s):
            if note_lines and "\n" not in note_lines[-1] and (len(note_lines[-1]) + len(extra_n) <= 22):
                note_lines[-1] = f"{note_lines[-1]}｜{extra_n}"
            else:
                note_lines.append(extra_n)

        for ck in ("items", "rows", "points", "bullets"):
            sub_raw = _coerce_items_list(item.get(ck)) if isinstance(item, dict) else []
            if sub_raw:
                for sub_it in sub_raw:
                    s_ld, s_bd = _parse_lead_body_item(sub_it)
                    line = f"**{s_ld}**：{s_bd}" if (s_ld and s_bd) else (s_ld or s_bd)
                    if line and line not in note_lines:
                        note_lines.append(line)
                break

        n_s = "\n".join(note_lines).strip()
        return v_s, l_s, n_s

    # Compute Content-Driven KPI strip height
    max_kpi_h = 1.30
    kpi_parsed: list[tuple[str, str, str, float]] = []
    for k_item in k_list:
        val_s, lbl_s, note_s = _resolve_kpi_fields(k_item)
        inner_kw = max(0.80, k_col_w - 0.24)

        # Pick largest clean single-line value font size (never shrinking below 22pt)
        chosen_vpt = val_pt_base
        while chosen_vpt > 22.0 and val_s:
            mv = measure_text_layout(val_s, inner_kw, chosen_vpt, bold=True, line_spacing=1.10)
            if int(mv["line_count"]) <= 1:
                break
            chosen_vpt -= 2.0
        kpi_parsed.append((val_s, lbl_s, note_s, chosen_vpt))

        h_need = 0.0
        if val_s:
            m_v = measure_text_layout(val_s, inner_kw, chosen_vpt, bold=True, line_spacing=1.12)
            v_lines = max(1, int(m_v["line_count"]))
            if lbl_s or note_s:
                h_need += v_lines * ((chosen_vpt * MSJH_LINE_HEIGHT_EM) / 72.0) * 1.12 + (4.0 / 72.0)
            else:
                h_need += float(m_v["content_height_in"])
        if lbl_s:
            m_l = measure_text_layout(lbl_s, inner_kw, lbl_pt, bold=True, line_spacing=1.20)
            l_lines = max(1, int(m_l["line_count"]))
            if note_s:
                h_need += l_lines * ((lbl_pt * MSJH_LINE_HEIGHT_EM) / 72.0) * 1.20 + (2.0 / 72.0)
            else:
                h_need += float(m_l["content_height_in"])
        if note_s:
            n_segs = note_s.splitlines() or [note_s]
            for ni, n_seg in enumerate(n_segs):
                m_n = measure_text_layout(n_seg, inner_kw, note_pt, bold=False, line_spacing=1.20)
                n_lines = max(1, int(m_n["line_count"]))
                if ni < len(n_segs) - 1:
                    h_need += n_lines * ((note_pt * MSJH_LINE_HEIGHT_EM) / 72.0) * 1.20 + (2.0 / 72.0)
                else:
                    h_need += float(m_n["content_height_in"])
        # Textbox sits at top+0.14 with height strip_h-0.20 (usable ~ strip_h-0.26); add >=20% breathing room
        max_kpi_h = max(max_kpi_h, h_need * 1.22 + 0.30)

    has_insights = bool(insight_blocks)
    strip_h = round(min(resolved_h * (0.50 if has_insights else 0.72), max(1.38, max_kpi_h)), 3)
    kpi_note_ls = 1.14 if max_kpi_h > strip_h else 1.20

    # Pre-measure natural insight blocks height to drive Direction 2 expansion before drawing
    ins_list = list(insight_blocks) if has_insights else []
    n_ins = len(ins_list)
    ins_gap = 0.34
    ins_w = (total_width - ins_gap * max(0, n_ins - 1)) / max(1, n_ins)
    max_nat_ins_h = 0.0
    if has_insights:
        inner_iw_est = max(0.70, ins_w - 0.16)
        ht_pt_est = _round_half_pt(resolved_pt + 2.0)
        k_pt_est = float(typo["kicker"])
        s_pt_est = float(typo["subtitle"])
        for blk in ins_list:
            bk_k = ""
            bk_s = ""
            if isinstance(blk, dict):
                has_col = any(bool(_coerce_items_list(blk.get(ck))) for ck in ("rows", "items", "points", "bullets"))
                bk_k = _first_non_empty_str(blk, "kicker", "badge", "num", "step")
                b_t = _first_non_empty_str(blk, "title", "heading", "label", "name")
                bk_s = _first_non_empty_str(blk, "subtitle", "sub")
                b_l = _first_non_empty_str(blk, "lead")
                if bk_k or bk_s or has_col or (b_t and b_l and b_l != b_t):
                    bk_h = b_t
                    ex_ld = b_l if b_l != b_t else ""
                    s_its = _extract_lead_body_items(blk, extra_lead=ex_ld, include_subtitle_as_body=False)
                else:
                    bk_h = ""
                    s_its = _extract_lead_body_items(blk, extra_lead=(b_t or b_l), include_subtitle_as_body=True)
            else:
                bk_h = ""
                ld_e, bd_e = _parse_lead_body_item(blk)
                s_its = [(ld_e, bd_e)] if (ld_e or bd_e) else []
            est_h = 0.0
            if bk_k or bk_h or bk_s:
                est_h += _measure_three_tier_header(bk_k, bk_h, bk_s, inner_iw_est, k_pt_est, ht_pt_est, s_pt_est) + 0.10
            if s_its:
                m_sh = [_measure_lead_body_item_height(ld_e, bd_e, inner_iw_est, lead_pt, resolved_pt, line_spacing=ls) for ld_e, bd_e in s_its]
                est_h += sum(m_sh) + 0.14 * max(0, len(m_sh) - 1) + 0.02
            max_nat_ins_h = max(max_nat_ins_h, max(0.45, est_h))

    nat_kpi_total_h = strip_h + ((0.20 + 0.22 + max_nat_ins_h) if has_insights else 0.0)
    kpi_exp = _calc_zone2_expansion_factor(avail_h, nat_kpi_total_h)
    if kpi_exp > 1.0:
        strip_extra = min(0.24, (kpi_exp - 1.0) * 0.55)
        expanded_strip = min(2.50, min(avail_h * (0.44 if has_insights else 0.72), strip_h + strip_extra))
        strip_h = round(max(strip_h, expanded_strip), 3)
    div_gap = round(0.20 * kpi_exp, 3) if kpi_exp > 1.0 else 0.20
    ins_top_gap = round(0.22 * kpi_exp, 3) if kpi_exp > 1.0 else 0.22
    ins_hdr_gap = round(0.08 * kpi_exp, 3) if kpi_exp > 1.0 else 0.08
    ins_item_gap_cap = round(0.14 * kpi_exp, 3) if kpi_exp > 1.0 else 0.14
    kpi_budget_bottom = avail_bottom if kpi_exp > 1.0 else (top + resolved_h)

    coords: list[tuple[float, float, float, float]] = [(round(left, 3), round(top, 3), round(total_width, 3), strip_h)]
    cur_x = left
    for idx, (k_item, (val_s, lbl_s, note_s, vpt)) in enumerate(zip(k_list, kpi_parsed)):
        is_spot = (spotlight_idx == idx) if spotlight_idx is not None else bool(k_item.get("is_spotlight", False))
        acc_hex = str(k_item.get("accent", theme_pri if is_spot else muted_acc))

        if is_spot:
            wash = _add_flat_shape(
                slide,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(cur_x), Inches(top), Inches(k_col_w), Inches(strip_h),
            )
            wash.adjustments[0] = 0.04
            wash.fill.solid()
            wash.fill.fore_color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_canvas, 0.14 if is_dark_theme else 0.08))
            wash.line.fill.background()

        tbar = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(cur_x + 0.12), Inches(top + 0.01), Inches(max(0.5, k_col_w - 0.24)), Inches(0.06 if is_spot else 0.03),
        )
        tbar.fill.solid()
        tbar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else div_strong)
        tbar.line.fill.background()

        if idx > 0:
            vdiv = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(cur_x - k_gap / 2.0), Inches(top + 0.14), Inches(0.012), Inches(max(0.5, strip_h - 0.28)),
            )
            vdiv.fill.solid()
            vdiv.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
            vdiv.line.fill.background()

        tb = slide.shapes.add_textbox(
            Inches(cur_x + 0.12), Inches(top + 0.14), Inches(max(0.6, k_col_w - 0.24)), Inches(max(0.6, strip_h - 0.20))
        )
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = Inches(0.02)
        tf.margin_top = Inches(0.01)

        first_used = False
        if val_s:
            p0 = tf.paragraphs[0]
            first_used = True
            p0.alignment = PP_ALIGN.LEFT
            p0.line_spacing = 1.12
            if lbl_s or note_s:
                p0.space_after = Pt(4)
            _populate_paragraph_runs(p0, val_s, vpt, acc_hex if is_spot else ink_pri, bold=True)

        if lbl_s:
            p1 = tf.add_paragraph() if first_used else tf.paragraphs[0]
            first_used = True
            p1.alignment = PP_ALIGN.LEFT
            p1.line_spacing = 1.20
            if note_s:
                p1.space_after = Pt(2)
            _populate_paragraph_runs(p1, lbl_s, lbl_pt, ink_pri, bold=True)

        if note_s:
            n_lines = note_s.splitlines() or [note_s]
            for ni, n_seg in enumerate(n_lines):
                p2 = tf.add_paragraph() if first_used else tf.paragraphs[0]
                first_used = True
                p2.alignment = PP_ALIGN.LEFT
                p2.line_spacing = kpi_note_ls
                if ni < len(n_lines) - 1:
                    p2.space_after = Pt(2)
                _populate_paragraph_runs(p2, n_seg, note_pt, ink_muted, bold=False, bold_color_hex=ink_pri)

        cur_x += k_col_w + k_gap

    # Divider & Lower Insight Blocks
    if has_insights:
        div_y = round(top + strip_h + div_gap, 3)
        hdiv = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(left), Inches(div_y), Inches(total_width), Inches(0.015),
        )
        hdiv.fill.solid()
        hdiv.fill.fore_color.rgb = hex_to_rgb_color(div_strong)
        hdiv.line.fill.background()

        ins_top = round(div_y + ins_top_gap, 3)
        ins_h = max(1.0, round(kpi_budget_bottom - ins_top, 3))
        has_explicit_ins_spot = any(isinstance(b, dict) and b.get("is_spotlight") is not None for b in ins_list)

        ix = left
        for i_idx, blk in enumerate(ins_list):
            blk_kicker = ""
            blk_sub = ""
            if isinstance(blk, dict):
                has_collection = any(bool(_coerce_items_list(blk.get(ck))) for ck in ("rows", "items", "points", "bullets"))
                blk_kicker = _first_non_empty_str(blk, "kicker", "badge", "num", "step")
                b_title = _first_non_empty_str(blk, "title", "heading", "label", "name")
                blk_sub = _first_non_empty_str(blk, "subtitle", "sub")
                b_lead = _first_non_empty_str(blk, "lead")
                if blk_kicker or blk_sub or has_collection or (b_title and b_lead and b_lead != b_title):
                    blk_heading = b_title
                    extra_ld = b_lead if b_lead != b_title else ""
                    sub_items = _extract_lead_body_items(blk, extra_lead=extra_ld, include_subtitle_as_body=False)
                else:
                    blk_heading = ""
                    sub_items = _extract_lead_body_items(blk, extra_lead=(b_title or b_lead), include_subtitle_as_body=True)
            else:
                blk_heading = ""
                ld, bd = _parse_lead_body_item(blk)
                sub_items = [(ld, bd)] if (ld or bd) else []

            is_spot_ins = bool(blk.get("is_spotlight", False)) if (has_explicit_ins_spot and isinstance(blk, dict)) else (i_idx == 0)
            bar_hex = theme_pri if is_spot_ins else div_strong
            cur_iy = ins_top
            inner_iw = max(0.70, ins_w - 0.16)

            measured_subs: list[tuple[str, str, float]] = [
                (ld, bd, _measure_lead_body_item_height(ld, bd, inner_iw, lead_pt, resolved_pt, line_spacing=ls))
                for ld, bd in sub_items
            ]
            est_sub_h = sum(s[2] for s in measured_subs) + 0.06 * max(0, len(measured_subs) - 1) if measured_subs else 0.0

            if blk_kicker or blk_heading or blk_sub:
                ht_pt = _round_half_pt(resolved_pt + 2.0)
                k_pt = float(typo["kicker"])
                s_pt = float(typo["subtitle"])
                hh = _measure_three_tier_header(blk_kicker, blk_heading, blk_sub, inner_iw, k_pt, ht_pt, s_pt)
                if blk_kicker and blk_heading and blk_sub and measured_subs and (hh + 0.08 + est_sub_h) > ins_h:
                    blk_kicker = f"{blk_kicker} · {blk_sub}"
                    blk_sub = ""
                    hh = _measure_three_tier_header(blk_kicker, blk_heading, blk_sub, inner_iw, k_pt, ht_pt, s_pt)
                hdr_box_h = round(min(ins_h * 0.54, hh + 0.02), 3)
                _render_three_tier_header(
                    slide,
                    x=ix + 0.14,
                    y=cur_iy,
                    w=inner_iw,
                    h=hdr_box_h,
                    kicker=blk_kicker,
                    title=blk_heading,
                    subtitle=blk_sub,
                    kicker_pt=k_pt,
                    title_pt=ht_pt,
                    sub_pt=s_pt,
                    kicker_hex=theme_pri if is_spot_ins else ink_muted,
                    title_hex=theme_pri if is_spot_ins else ink_pri,
                    sub_hex=ink_muted,
                )
                cur_iy = round(cur_iy + hdr_box_h + ins_hdr_gap, 3)

            if measured_subs:
                avail_sub_h = max(0.32, (ins_top + ins_h) - cur_iy)
                raw_sub_sum = sum(s[2] for s in measured_subs)
                min_sub_gap = 0.05 * max(0, len(measured_subs) - 1)
                ins_lead_hex = theme_pri if (is_spot_ins and not (blk_kicker or blk_heading or blk_sub)) else ink_pri
                if len(measured_subs) > 1 and (raw_sub_sum + min_sub_gap) > avail_sub_h:
                    _render_compact_lead_body_stack(
                        slide,
                        x=ix + 0.14,
                        y=cur_iy,
                        w=inner_iw,
                        h=avail_sub_h,
                        items=[(ld, bd) for ld, bd, _ih in measured_subs],
                        lead_pt=lead_pt,
                        body_pt=resolved_pt,
                        lead_hex=ins_lead_hex,
                        body_hex=ink_body,
                        bold_color_hex=ink_pri,
                        line_spacing=min(ls, 1.16),
                        para_space_after_pt=2.0,
                    )
                    cur_iy = round(cur_iy + avail_sub_h, 3)
                else:
                    eff_ig = (
                        min(ins_item_gap_cap, max(0.05, (avail_sub_h - raw_sub_sum) / max(1, len(measured_subs) - 1)))
                        if len(measured_subs) > 1
                        else 0.0
                    )
                    for ld, bd, ih in measured_subs:
                        rem = max(0.28, (ins_top + ins_h) - cur_iy)
                        bh = round(min(rem, ih + 0.02), 3)
                        _render_lead_body_box(
                            slide, ix + 0.14, cur_iy, inner_iw, bh,
                            ld, bd, lead_pt, resolved_pt, ins_lead_hex,
                            ink_body, ink_pri, line_spacing=ls,
                        )
                        cur_iy = round(cur_iy + bh + eff_ig, 3)

            used_h = max(0.45, min(ins_h, cur_iy - ins_top - 0.06))
            lbar = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(ix), Inches(ins_top + 0.03), Inches(0.055 if is_spot_ins else 0.035), Inches(max(0.32, used_h - 0.06)),
            )
            lbar.fill.solid()
            lbar.fill.fore_color.rgb = hex_to_rgb_color(bar_hex)
            lbar.line.fill.background()

            coords.append((round(ix, 3), round(ins_top, 3), round(ins_w, 3), round(used_h, 3)))
            ix += ins_w + ins_gap

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y(coords, dy_in)


def draw_focal_anatomy_s6(
    slide,
    focal_title: str,
    focal_formula: str,
    focal_note: str = "",
    breakdown_items: Sequence[object] = (),
    mode: str = "left_right",
    focal_ratio: float = 0.38,
    use_omml: bool = False,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    body_font_pt: float = 13.0,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> tuple[float, float, float, float]:
    """
    [F5-C / S6] Render Focal Equation / Core Principle Anatomy Slide optimized for 16:9 widescreen:
    - `mode="left_right"` (default): Left `38%` dark focal box + Right `62%` unboxed TOP-aligned breakdown rows.
    - `mode="top_bottom"`: Compact top focal banner + Bottom horizontal unboxed breakdown columns.
    - `use_omml=True`: injects native editable `<m:oMath>` equation via `insert_omml_equation()`.
    - All text enforces `>= min_font_pt`.
    """
    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.26)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, min_floor, resolved_pt, _typo, _sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.0, caller_default_pt=13.0
    )
    dark_bg = dt.get("bookend_dark_bg", "#0F172A")
    dark_acc = dt.get("bookend_accent", "#38BDF8")
    items = _normalize_callout_items(breakdown_items)

    layout_mode = str(mode or "left_right").strip().lower()
    gap = 0.38
    ratio = max(0.30, min(0.55, float(focal_ratio)))

    ft_pt = max(min_floor, _round_half_pt(resolved_pt))
    formula_pt = max(18.0, _round_half_pt(resolved_pt + 4.0))
    note_pt = max(min_floor, _round_half_pt(resolved_pt - 0.5 if resolved_pt >= 13.5 else resolved_pt))

    def _measure_focal_min_h(box_w: float) -> float:
        tw = max(0.8, box_w - 0.56)
        need = 0.56
        t_s = str(focal_title or "").strip()
        if t_s:
            need += float(measure_text_layout(t_s, tw, ft_pt, bold=True, line_spacing=1.20)["safe_height_in"]) + 0.14
        f_s = str(focal_formula or "").strip()
        if f_s:
            need += float(measure_text_layout(f_s, tw, formula_pt, bold=True, line_spacing=1.28)["safe_height_in"]) + 0.16
        n_s = str(focal_note or "").strip()
        if n_s:
            need += float(measure_text_layout(n_s, tw, note_pt, bold=False, line_spacing=1.28)["safe_height_in"])
        return round(max(2.10, need + 0.24), 3)

    if layout_mode == "top_bottom":
        fh = min(1.95, max(1.35, resolved_h * 0.34)) if items else resolved_h * 0.55
        fx, fy, fw = left, top, total_width
        if items:
            horz_h = _estimate_horizontal_band_height(items, total_width, resolved_pt)
            nat_tb_h = fh + 0.24 + horz_h
            tb_exp = _calc_zone2_expansion_factor(avail_h, nat_tb_h)
            tb_gap = round(0.24 * tb_exp, 3) if tb_exp > 1.0 else 0.24
            tb_budget_h = max(resolved_h, avail_h) if tb_exp > 1.0 else resolved_h
            _render_unboxed_callouts_horizontal(
                slide, items, left, top + fh + tb_gap, total_width, max(0.8, tb_budget_h - fh - tb_gap), resolved_pt, 0, dt
            )
    else:
        fw = (total_width - gap) * ratio if items else total_width
        fx, fy = left, top
        focal_min_h = _measure_focal_min_h(fw)
        if items:
            rx = left + fw + gap
            rw = total_width - fw - gap
            right_nat_h = _estimate_vertical_callouts_height(items, rw, None, resolved_pt, gap_scale=1.0)
            nat_lr_h = max(focal_min_h, right_nat_h)
            lr_exp = _calc_zone2_expansion_factor(avail_h, nat_lr_h)
            lr_budget_h = max(resolved_h, avail_h) if lr_exp > 1.0 else resolved_h
            before_r = len(slide.shapes)
            _render_unboxed_callouts_vertical(
                slide, items, rx, top, rw, lr_budget_h, None, resolved_pt, 0, dt, gap_scale=lr_exp
            )
            right_shapes = list(slide.shapes)[before_r:]
            right_actual_h = (
                max((float(s.top or 0) + float(s.height or 0)) / 914400.0 for s in right_shapes) - float(top)
                if right_shapes
                else right_nat_h
            )
            fh = round(min(lr_budget_h, max(focal_min_h, right_actual_h)), 3)
        else:
            fh = round(min(resolved_h, max(focal_min_h, resolved_h * 0.68)), 3)

    fbox = _add_flat_shape(
        slide,
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(fx), Inches(fy), Inches(fw), Inches(fh),
    )
    fbox.adjustments[0] = 0.04
    fbox.fill.solid()
    fbox.fill.fore_color.rgb = hex_to_rgb_color(dark_bg)
    fbox.line.color.rgb = hex_to_rgb_color(dark_acc)
    fbox.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(
        Inches(fx + 0.26), Inches(fy + 0.18), Inches(max(0.8, fw - 0.52)), Inches(max(0.6, fh - 0.36))
    )
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    is_centered = layout_mode == "top_bottom"

    p0 = tf.paragraphs[0]
    p0.alignment = PP_ALIGN.CENTER if is_centered else PP_ALIGN.LEFT
    p0.space_after = Pt(10)
    _populate_paragraph_runs(p0, str(focal_title).strip(), ft_pt, "#CBD5E1", bold=True)

    formula_str = str(focal_formula or "").strip()
    if use_omml and formula_str:
        insert_omml_equation(
            tf,
            formula_str,
            font_pt=formula_pt,
            color_hex=dark_acc,
            align="center" if is_centered else "left",
            append_paragraph=True,
        )
        if focal_note and str(focal_note).strip():
            tf.paragraphs[-1].space_after = Pt(10)
    else:
        for f_i, f_line in enumerate(formula_str.splitlines() or [formula_str]):
            p_f = tf.add_paragraph()
            p_f.alignment = PP_ALIGN.CENTER if is_centered else PP_ALIGN.LEFT
            p_f.line_spacing = 1.28
            if f_i == len(formula_str.splitlines() or [formula_str]) - 1 and focal_note:
                p_f.space_after = Pt(10)
            _populate_paragraph_runs(p_f, f_line, formula_pt, dark_acc, bold=True, bold_color_hex="#FFFFFF")

    if focal_note and str(focal_note).strip():
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER if is_centered else PP_ALIGN.LEFT
        p2.line_spacing = 1.28
        _populate_paragraph_runs(p2, str(focal_note).strip(), note_pt, "#FDE68A", bold=False, bold_color_hex="#FFFFFF")

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y((round(fx, 3), round(fy, 3), round(fw, 3), round(fh, 3)), dy_in)


def draw_hero_stat_slide(
    slide,
    stat_value: str,
    stat_label: str,
    context_points: Sequence[object] = (),
    right_image_path: str | None = None,
    variant: str = "big_number",
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    stat_pt: float = 54.0,
    body_font_pt: float = 13.5,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> tuple[float, float, float, float]:
    """
    [F1-C / Hero Stat + S14] Render Giant Focus Manifesto Slide (2 variants, ZERO card boxes):
    - `variant="big_number"` (default): Left giant hero KPI number + concise label paired with right image or unboxed callouts.
    - `variant="quote_manifesto"` (`S14`): Full-width high-whitespace typographic thesis / manifesto quote
      (left vertical accent rule, bold statement, attribution/sub-claim, and optional supporting bottom strip).
    """
    resolved_h = _resolve_zone2_height(slide, top, height, 5.26)
    dt, min_floor, resolved_pt, typo, _sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.5, caller_default_pt=13.5
    )
    pal = _theme_palette(dt)
    theme_pri = pal["primary_accent"]
    ink_pri = pal["ink_primary"]
    ink_muted = pal["ink_muted"]
    div_strong = pal["divider_strong"]
    var_norm = str(variant or "big_number").strip().lower()

    if var_norm == "quote_manifesto":
        items = _normalize_callout_items(context_points)
        quote_str = str(stat_value or "").strip()
        attr_str = str(stat_label or "").strip()

        custom_stat = abs(float(stat_pt) - 54.0) > 1e-6
        quote_pt = min(48.0 if custom_stat else 38.0, max(24.0, float(stat_pt) if custom_stat else _round_half_pt(resolved_pt * 2.15)))
        attr_pt = max(min_floor, _round_half_pt(resolved_pt + 2.0))

        band_h = 0.0
        if items:
            band_h = min(resolved_h * 0.40, _estimate_horizontal_band_height(items, total_width, resolved_pt) + 0.24)
        quote_zone_h = max(1.80, resolved_h - band_h)

        text_x = left + 0.36
        text_w = total_width - 0.56
        min_quote_pt = max(22.0, _round_half_pt(resolved_pt * 1.35))
        q_attr_gap = 0.18
        while True:
            m_q = measure_text_layout(quote_str, text_w, quote_pt, bold=True, line_spacing=1.24)
            q_h = round(max(0.60, float(m_q["safe_height_in"]) + 0.06), 3)
            a_h = 0.0
            if attr_str:
                m_a = measure_text_layout(attr_str, text_w, attr_pt, bold=False, line_spacing=1.24)
                a_h = round(max(0.30, float(m_a["safe_height_in"]) + 0.04), 3)
            tot_q_h = q_h + (q_attr_gap + a_h if attr_str else 0.0)
            if tot_q_h <= quote_zone_h - 0.22 or quote_pt <= min_quote_pt + 1e-6:
                break
            quote_pt = max(min_quote_pt, _round_half_pt(quote_pt - 1.5))

        if tot_q_h > quote_zone_h - 0.18:
            q_attr_gap = 0.10
            tot_q_h = q_h + (q_attr_gap + a_h if attr_str else 0.0)
            if items and tot_q_h > quote_zone_h - 0.16:
                # Rebalance divider slightly downward only if bottom band has spare room
                need_extra = (tot_q_h + 0.18) - quote_zone_h
                min_band = _estimate_horizontal_band_height(items, total_width, resolved_pt) + 0.14
                spare = max(0.0, band_h - min_band)
                shift = min(need_extra, spare)
                quote_zone_h += shift
                band_h -= shift

        q_top = round(top + max(0.06, min(0.14, (quote_zone_h - tot_q_h) * 0.44)) if tot_q_h >= quote_zone_h - 0.30 else top + (quote_zone_h - tot_q_h) * 0.44, 3)

        # Bold architectural left accent bar spanning the quote block
        lbar = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(left + 0.04), Inches(q_top + 0.04), Inches(0.09), Inches(max(0.75, min(quote_zone_h - 0.14, tot_q_h - 0.08))),
        )
        lbar.fill.solid()
        lbar.fill.fore_color.rgb = hex_to_rgb_color(theme_pri)
        lbar.line.fill.background()

        q_tb = slide.shapes.add_textbox(Inches(text_x), Inches(q_top), Inches(text_w), Inches(q_h))
        tf_q = q_tb.text_frame
        tf_q.word_wrap = True
        tf_q.vertical_anchor = MSO_ANCHOR.TOP
        tf_q.margin_left = Inches(0.0)
        tf_q.margin_right = Inches(0.0)
        pq = tf_q.paragraphs[0]
        pq.alignment = PP_ALIGN.LEFT
        pq.line_spacing = 1.24
        _populate_paragraph_runs(pq, quote_str, quote_pt, ink_pri, bold=True, bold_color_hex=theme_pri)

        if attr_str:
            a_top = round(q_top + q_h + q_attr_gap, 3)
            max_a_h = max(0.28, (top + quote_zone_h - 0.10) - a_top) if items else a_h
            a_tb = slide.shapes.add_textbox(Inches(text_x), Inches(a_top), Inches(text_w), Inches(min(a_h, max_a_h)))
            tf_a = a_tb.text_frame
            tf_a.word_wrap = True
            tf_a.vertical_anchor = MSO_ANCHOR.TOP
            tf_a.margin_left = Inches(0.0)
            tf_a.margin_right = Inches(0.0)
            pa = tf_a.paragraphs[0]
            pa.alignment = PP_ALIGN.LEFT
            pa.line_spacing = 1.24
            _populate_paragraph_runs(pa, attr_str, attr_pt, ink_muted, bold=False, bold_color_hex=theme_pri)

        if items:
            div_y = round(max(top + quote_zone_h - 0.06, (q_top + tot_q_h + 0.08) if not attr_str else (a_top + min(a_h, max_a_h) + 0.08)), 3)
            div_y = min(div_y, round(top + resolved_h - 0.85, 3))
            hdiv = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(left), Inches(div_y), Inches(total_width), Inches(0.014),
            )
            hdiv.fill.solid()
            hdiv.fill.fore_color.rgb = hex_to_rgb_color(div_strong)
            hdiv.line.fill.background()
            _render_unboxed_callouts_horizontal(
                slide, items, left, round(div_y + 0.16, 3), total_width, max(0.65, (top + resolved_h) - (div_y + 0.16)), resolved_pt, 0, dt
            )

        return (round(left, 3), round(top, 3), round(total_width, 3), round(resolved_h, 3))

    # Default variant="big_number"
    if isinstance(tokens, dict) and abs(float(stat_pt) - 54.0) < 1e-6:
        resolved_stat_pt = float(typo["hero_stat"])
    else:
        resolved_stat_pt = max(32.0, float(stat_pt))
    lbl_pt = max(min_floor + 2.0, _round_half_pt(resolved_pt + 2.0))

    items = _normalize_callout_items(context_points)
    has_both_img_and_items = (right_image_path is not None) and bool(items)
    has_right = (right_image_path is not None) or bool(items)
    gap = 0.44
    left_w = (total_width * 0.40) if has_right else (total_width * 0.82)
    right_x = left + left_w + gap
    right_w = total_width - left_w - gap

    band_h = 0.0
    if has_both_img_and_items:
        band_h = min(resolved_h * 0.38, _estimate_horizontal_band_height(items, total_width, resolved_pt) + 0.18)
    upper_h = max(1.80, round(resolved_h - (band_h + 0.16 if has_both_img_and_items else 0.0), 3))

    val_str = str(stat_value or "").strip()
    lbl_str = str(stat_label or "").strip()
    m_num = measure_text_layout(val_str, left_w - 0.06, resolved_stat_pt, bold=True, line_spacing=1.14)
    m_lbl = measure_text_layout(lbl_str, left_w - 0.06, lbl_pt, bold=True, line_spacing=1.28)
    req_hero_h = float(m_num["safe_height_in"]) + float(m_lbl["safe_height_in"]) + 0.46
    hero_block_h = min(upper_h, max(min(upper_h, 2.20), req_hero_h))
    # Harmonize vertical anchor: when paired with right unboxed callouts, start both cleanly at top+0.36"
    if has_both_img_and_items:
        hero_y = round(top + max(0.06, (upper_h - hero_block_h) * 0.36), 3)
    elif items and right_image_path is None:
        hero_y = round(top + 0.36, 3)
    else:
        hero_y = round(top + max(0.10, (upper_h - hero_block_h) * 0.40), 3)

    accent_rule = _add_flat_shape(
        slide,
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(hero_y), Inches(1.20), Inches(0.075),
    )
    accent_rule.fill.solid()
    accent_rule.fill.fore_color.rgb = hex_to_rgb_color(theme_pri)
    accent_rule.line.fill.background()

    hero_tb = slide.shapes.add_textbox(
        Inches(left), Inches(hero_y + 0.18), Inches(left_w), Inches(max(1.20, hero_block_h - 0.18))
    )
    tf = hero_tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p_num = tf.paragraphs[0]
    p_num.alignment = PP_ALIGN.LEFT
    p_num.line_spacing = 1.14
    p_num.space_after = Pt(10)
    _populate_paragraph_runs(p_num, val_str, resolved_stat_pt, theme_pri, bold=True)

    if lbl_str:
        p_lbl = tf.add_paragraph()
        p_lbl.alignment = PP_ALIGN.LEFT
        p_lbl.line_spacing = 1.28
        _populate_paragraph_runs(p_lbl, lbl_str, lbl_pt, ink_pri, bold=True)

    if right_image_path is not None:
        draw_visual_callout_slide(
            slide,
            image_path=right_image_path,
            callout_position="header_only",
            left=right_x,
            top=top,
            total_width=right_w,
            height=upper_h,
            tokens=tokens,
            doc_theme_id=doc_theme_id,
        )
        if items:
            div_y = round(top + upper_h + 0.04, 3)
            hdiv = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(left), Inches(div_y), Inches(total_width), Inches(0.014),
            )
            hdiv.fill.solid()
            hdiv.fill.fore_color.rgb = hex_to_rgb_color(div_strong)
            hdiv.line.fill.background()
            _render_unboxed_callouts_horizontal(
                slide,
                items,
                left,
                round(div_y + 0.14, 3),
                total_width,
                max(0.65, (top + resolved_h) - (div_y + 0.14)),
                resolved_pt,
                0,
                dt,
            )
    elif items:
        _render_unboxed_callouts_vertical(
            slide, items, right_x, hero_y, right_w, max(1.60, (top + resolved_h) - hero_y), None, resolved_pt, 0, dt
        )

    return (round(left, 3), round(top, 3), round(left_w, 3), round(resolved_h, 3))


# -------------------------------------------------------------------------
# Mode 3 Tier 1 | Native Editable Theme Geometric Accent Primitives
# -------------------------------------------------------------------------

def draw_theme_geometric_accent(
    slide,
    motif_type: str = "diagonal_wedge",
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
    **kwargs,
) -> None:
    """
    [Mode 3 Tier 1] Add a restrained, 100% native PowerPoint editable thematic geometric motif
    strictly within peripheral margin space (20/80 restraint, zero drop shadow, zero text collision).
    Supported `motif_type`:
      - `"diagonal_wedge"`: architectural right-edge diagonal wedge + crisp accent edge strip.
      - `"ruler_ticks"`: precision analytical ruler tick strip along far-left or bottom margin.
      - `"step_blocks"`: ascending 4-step editorial stair silhouette in bottom-right corner.
      - `"vector_scale"`: minimalist geometric balance scale motif in bottom-right / top-right corner.
    """
    dt, _min_floor, _body_pt, _typo, _sp = _resolve_engine_context(tokens, doc_theme_id)
    primary = str(kwargs.get("accent_hex") or dt.get("primary_accent", "#0284C7"))
    bg_canvas = dt.get("bg_canvas", "#F8FAFC")
    tint = str(kwargs.get("tint_hex") or _blend_hex(primary, bg_canvas, 0.18))
    muted = str(kwargs.get("muted_hex") or dt.get("border_card", "#CBD5E1"))
    m_type = str(motif_type or "diagonal_wedge").strip().lower()

    if m_type == "diagonal_wedge":
        # Crisp peripheral top-right diagonal architectural accent (stays strictly outside Zone 1/2 content)
        w1 = _add_flat_shape(
            slide,
            MSO_SHAPE.RIGHT_TRIANGLE,
            Inches(12.55), Inches(0.0), Inches(0.783), Inches(0.88),
        )
        w1.rotation = 180.0
        w1.fill.solid()
        w1.fill.fore_color.rgb = hex_to_rgb_color(tint)
        w1.line.fill.background()

        strip = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(13.253), Inches(0.0), Inches(0.08), Inches(7.5),
        )
        strip.fill.solid()
        strip.fill.fore_color.rgb = hex_to_rgb_color(primary)
        strip.line.fill.background()
        return

    if m_type == "ruler_ticks":
        # Precision analytical scale ticks tucked cleanly along the far-left margin (x <= 0.28")
        spine = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(0.14), Inches(1.40), Inches(0.015), Inches(5.40),
        )
        spine.fill.solid()
        spine.fill.fore_color.rgb = hex_to_rgb_color(muted)
        spine.line.fill.background()

        n_ticks = int(kwargs.get("num_ticks", 13))
        n_ticks = max(5, min(25, n_ticks))
        step_y = 5.40 / (n_ticks - 1)
        highlight_idx = int(kwargs.get("highlight_idx", n_ticks // 2))
        for i in range(n_ticks):
            ty = 1.40 + i * step_y
            is_major = (i % 4 == 0)
            is_hl = (i == highlight_idx)
            tw = 0.16 if is_hl else (0.12 if is_major else 0.07)
            th = 0.032 if is_hl else (0.018 if is_major else 0.012)
            tk = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(0.14), Inches(ty - th / 2.0), Inches(tw), Inches(th),
            )
            tk.fill.solid()
            tk.fill.fore_color.rgb = hex_to_rgb_color(primary if is_hl else (muted if not is_major else "#94A3B8"))
            tk.line.fill.background()
        return

    if m_type == "step_blocks":
        # Ascending geometric stair motif tucked cleanly in bottom-right margin (y >= 7.12" or right edge)
        base_x = float(kwargs.get("left", 11.75))
        base_y = float(kwargs.get("bottom", 7.42))
        n_bars = 4
        bar_w = 0.24
        bar_gap = 0.06
        heights = [0.10, 0.16, 0.22, 0.30]
        weights = [0.22, 0.42, 0.68, 1.00]
        for i in range(n_bars):
            bh = heights[i]
            bx = base_x + i * (bar_w + bar_gap)
            by = base_y - bh
            blk = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(bx), Inches(by), Inches(bar_w), Inches(bh),
            )
            blk.fill.solid()
            blk.fill.fore_color.rgb = hex_to_rgb_color(_blend_hex(primary, bg_canvas, weights[i]))
            blk.line.fill.background()
        return

    if m_type == "vector_scale":
        # Minimalist geometric balance scale motif tucked cleanly in bottom-right corner
        cx = float(kwargs.get("center_x", 12.52))
        base_y = float(kwargs.get("bottom", 7.40))
        tilt_deg = float(kwargs.get("tilt_deg", -6.0))

        # Fulcrum triangle
        tri = _add_flat_shape(
            slide,
            MSO_SHAPE.ISOSCELES_TRIANGLE,
            Inches(cx - 0.11), Inches(base_y - 0.18), Inches(0.22), Inches(0.18),
        )
        tri.fill.solid()
        tri.fill.fore_color.rgb = hex_to_rgb_color("#94A3B8")
        tri.line.fill.background()

        # Balance beam
        beam = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(cx - 0.48), Inches(base_y - 0.21), Inches(0.96), Inches(0.032),
        )
        beam.rotation = tilt_deg
        beam.fill.solid()
        beam.fill.fore_color.rgb = hex_to_rgb_color(primary)
        beam.line.fill.background()

        # Two minimal geometric weight markers at beam ends
        pan_l = _add_flat_shape(
            slide,
            MSO_SHAPE.OVAL,
            Inches(cx - 0.46), Inches(base_y - 0.28), Inches(0.11), Inches(0.11),
        )
        pan_l.fill.solid()
        pan_l.fill.fore_color.rgb = hex_to_rgb_color(tint)
        pan_l.line.fill.background()

        pan_r = _add_flat_shape(
            slide,
            MSO_SHAPE.OVAL,
            Inches(cx + 0.35), Inches(base_y - 0.32), Inches(0.13), Inches(0.13),
        )
        pan_r.fill.solid()
        pan_r.fill.fore_color.rgb = hex_to_rgb_color(primary)
        pan_r.line.fill.background()
        return

    raise ValueError(
        f"Unsupported motif_type '{motif_type}'. Expected one of: "
        "'diagonal_wedge', 'ruler_ticks', 'step_blocks', 'vector_scale'."
    )


# -------------------------------------------------------------------------
# Two-Stage Semantic Layout Router & Anti-Collision Validator (F1..F5)
# -------------------------------------------------------------------------

_CANONICAL_LAYOUT_MAP: dict[str, tuple[str, str, bool, str]] = {
    # code -> (canonical_id, family_group, default_boxed, legacy_adj_key)
    "F1-A": ("F1-A", "F1", False, "F1-A"),
    "S0": ("F1-A", "F1", False, "F1-A"),
    "F1-B": ("F1-B", "F1", False, "F1-B"),
    "S13": ("F1-B", "F1", False, "F1-B"),
    "F1-C": ("F1-C", "F1", False, "F1-C"),
    "HERO_STAT": ("F1-C", "F1", False, "F1-C:HERO"),
    "HERO STAT": ("F1-C", "F1", False, "F1-C:HERO"),
    "HERO": ("F1-C", "F1", False, "F1-C:HERO"),
    "S14": ("F1-C", "F1", False, "F1-C:S14"),
    "F2-A": ("F2-A", "F2", False, "F2-A"),
    "S1": ("F2-A", "F2", False, "F2-A:S1"),
    "S2": ("F2-A", "F2", False, "F2-A:S2"),
    "F2-B": ("F2-B", "F2", False, "F2-B"),
    "S8": ("F2-B", "F2", False, "F2-B"),
    "F2-C": ("F2-C", "F2", True, "F2-C"),
    "S9": ("F2-C", "F2", True, "F2-C"),
    "F3-A": ("F3-A", "F3", False, "F3-A"),
    "S3": ("F3-A", "F3", False, "F3-A:S3"),
    "S12": ("F3-A", "F3", False, "F3-A:S12"),
    "F3-B": ("F3-B", "F3", True, "F3-B"),
    "S4": ("F3-B", "F3", True, "F3-B"),
    "F4-A": ("F4-A", "F4", False, "F4-A"),
    "S5": ("F4-A", "F4", False, "F4-A"),
    "F4-B": ("F4-B", "F4", False, "F4-B"),
    "S11": ("F4-B", "F4", False, "F4-B"),
    "APPENDIX": ("F4-B", "F4", False, "F4-B"),
    "F5-A": ("F5-A", "F5", False, "F5-A"),
    "S7": ("F5-A", "F5", False, "F5-A"),
    "S7-A": ("F5-A", "F5", False, "F5-A"),
    "S7-B": ("F5-A", "F5", False, "F5-A"),
    "S7-C": ("F5-A", "F5", False, "F5-A"),
    "S7-D": ("F5-A", "F5", False, "F5-A"),
    "F5-B": ("F5-B", "F5", False, "F5-B"),
    "S10": ("F5-B", "F5", False, "F5-B"),
    "F5-C": ("F5-C", "F5", True, "F5-C"),
    "S6": ("F5-C", "F5", True, "F5-C"),
}

_BOXED_VARIANT_TOKENS = frozenset({"clean_card", "card", "card_arrow", "boxed", "bento", "bento_grid"})
_UNBOXED_VARIANT_TOKENS = frozenset({"minimal_column", "borderless_centerline", "borderless", "fine_track", "staggered_timeline"})


def _normalize_layout_entry(entry: object) -> dict[str, object]:
    """Normalize a layout code string or layout dict into canonical `(canonical_id, family_group, boxed, adj_key)`."""
    explicit_boxed: bool | None = None
    variant = ""
    if isinstance(entry, dict):
        raw_code = str(entry.get("family_id", entry.get("layout", entry.get("code", "")))).strip()
        variant = str(entry.get("variant", entry.get("card_style", entry.get("layout_style", "")))).strip().lower()
        if "boxed" in entry and entry["boxed"] is not None:
            explicit_boxed = bool(entry["boxed"])
        elif "borderless" in entry and entry["borderless"] is not None:
            explicit_boxed = not bool(entry["borderless"])
    else:
        raw_str = str(entry or "").strip()
        if ":" in raw_str:
            raw_code, variant = [p.strip() for p in raw_str.split(":", 1)]
            variant = variant.lower()
        else:
            raw_code = raw_str

    code_upper = raw_code.upper().replace("_", "-")
    if code_upper not in _CANONICAL_LAYOUT_MAP:
        alt_upper = raw_code.upper()
        info = _CANONICAL_LAYOUT_MAP.get(alt_upper)
    else:
        info = _CANONICAL_LAYOUT_MAP[code_upper]

    if info is None:
        canonical_id = code_upper
        family_group = code_upper.split("-")[0] if "-" in code_upper else code_upper
        default_boxed = False
        adj_key = code_upper
    else:
        canonical_id, family_group, default_boxed, adj_key = info

    if explicit_boxed is not None:
        is_boxed = explicit_boxed
    elif variant in _BOXED_VARIANT_TOKENS:
        is_boxed = True
    elif variant in _UNBOXED_VARIANT_TOKENS:
        is_boxed = False
    else:
        is_boxed = default_boxed

    return {
        "raw": str(entry),
        "canonical_id": canonical_id,
        "family_group": family_group,
        "boxed": is_boxed,
        "adj_key": adj_key,
        "variant": variant,
    }


def recommend_layout_family(
    slide_copy_spec: dict[str, object],
    target_body_pt: float = 13.0,
    prev_layout: str | None = None,
    recent_families: Sequence[str] | None = None,
    boxed_ratio_so_far: float = 0.0,
) -> dict[str, object]:
    """
    Two-Stage Semantic-to-Layout Router (`兩段式語義自動配框架`):
    - Stage 1 (Copy Logic -> Layout Family): inspects semantic intent and copy structure in `slide_copy_spec`.
    - Stage 2 (Physical Constraints & Rhythm): applies DISCAS high-font guardrails (`target_body_pt >= 16.0pt`),
      4–5 milestone staggered timeline routing, boxed-ratio steering (`<= 0.40`), and adjacent anti-collision.
    Returns `{"family_id", "family_group", "variant", "is_boxed", "rationale"}`.
    """
    spec = slide_copy_spec if isinstance(slide_copy_spec, dict) else {}
    role = str(spec.get("role", spec.get("intent", spec.get("semantic_type", "")))).strip().lower()
    body_pt = max(MIN_CONTENT_FONT_PT, float(target_body_pt))
    high_font = body_pt >= 16.0
    avoid_boxed = float(boxed_ratio_so_far) >= 0.34

    prev_canon = _normalize_layout_entry(prev_layout)["canonical_id"] if prev_layout else None
    recent_fams = [str(f).upper() for f in (recent_families or [])]

    # Stage 1: Determine primary semantic layout
    family_id = "F2-A"
    variant = "minimal_column"
    is_boxed = False
    rationale = "Parallel narrative points mapped to structured columns."

    if role in ("cover", "closing", "bookend", "title") or spec.get("is_bookend"):
        family_id, variant, is_boxed = "F1-A", "bookend", False
        rationale = "Opening or peak-end closing slide locked to F1-A bookend."
    elif role in ("section", "divider", "section_divider", "transition") or spec.get("section_num") is not None:
        family_id, variant, is_boxed = "F1-B", "section_divider", False
        rationale = "Act/chapter breathing divider mapped to F1-B minimal section divider."
    elif role in ("quote", "manifesto", "thesis") or spec.get("quote"):
        family_id, variant, is_boxed = "F1-C", "quote_manifesto", False
        rationale = "Single high-impact thesis statement mapped to F1-C quote manifesto."
    elif role in ("hero_stat", "big_number", "spotlight_stat") or spec.get("stat_value"):
        family_id, variant, is_boxed = "F1-C", "big_number", False
        rationale = "Single decisive quantitative stat mapped to F1-C big number spotlight."
    elif spec.get("image_path") or spec.get("has_image") or role in ("chart", "visual", "evidence_chart"):
        family_id, variant, is_boxed = "F5-A", str(spec.get("callout_position", "right")), False
        rationale = "Primary chart/visual evidence paired with unboxed F5-A callouts."
    elif spec.get("formula") or spec.get("has_formula") or role in ("formula", "equation", "law", "anatomy"):
        family_id, variant, is_boxed = "F5-C", "left_right", True
        rationale = "Mathematical formula or governing law mapped to F5-C widescreen anatomy."
    elif spec.get("kpi_items") or role in ("kpi_strip", "kpi_overview", "metrics_summary"):
        family_id, variant, is_boxed = "F5-B", "kpi_strip", False
        rationale = "3–4 quantitative indicators with insights mapped to F5-B top KPI strip."
    elif spec.get("headers") or spec.get("has_table") or role in ("table", "comparison_table", "appendix"):
        family_id, variant, is_boxed = "F4-B", "three_line_table", False
        rationale = "Multi-criterion comparison or appendix reference mapped to F4-B three-line table."
    elif spec.get("quadrants") or role in ("quadrant", "2x2", "matrix"):
        family_id, variant, is_boxed = "F4-A", "borderless", False
        rationale = "Two orthogonal evaluation dimensions mapped to F4-A de-boxed 2x2 matrix."
    elif spec.get("nodes") or role in ("mechanism", "loop", "causal_loop", "architecture"):
        family_id, variant, is_boxed = "F3-B", str(spec.get("topology", "horizontal_chain")), True
        rationale = "3–5 node causal mechanism or feedback loop mapped to F3-B diagram."
    elif spec.get("steps") or role in ("process", "steps", "timeline", "roadmap", "milestones"):
        steps = spec.get("steps") or spec.get("items") or []
        n_steps = len(steps) if isinstance(steps, (list, tuple)) else 3
        family_id = "F3-A"
        if n_steps >= 4:
            variant, is_boxed = "staggered_timeline", False
            rationale = f"{n_steps} sequential milestones routed to F3-A staggered timeline (S12) for wide readable blocks."
        else:
            variant, is_boxed = "fine_track", False
            rationale = f"{n_steps}-step sequential flow routed to F3-A de-boxed horizontal fine track."
    elif spec.get("primary_block") or role in ("bento", "asymmetric", "anchor_and_support"):
        family_id, variant, is_boxed = "F2-C", "bento_grid", True
        rationale = "1 primary anchor + supporting blocks mapped to F2-C asymmetric Bento grid."
    elif role in ("split_rows", "swiss", "categories", "list_expand"):
        family_id, variant, is_boxed = "F2-B", "editorial_split_rows", False
        rationale = "Multi-category horizontal expansion mapped to F2-B Swiss split rows."
    else:
        items = spec.get("items") or spec.get("cards") or []
        n_items = len(items) if isinstance(items, (list, tuple)) else 2
        if n_items >= 4:
            family_id, variant, is_boxed = "F2-B", "editorial_split_rows", False
            rationale = f"{n_items} items routed to F2-B horizontal split rows to avoid narrow columns (Pitfall 1)."
        elif n_items == 2 or role in ("compare", "contrast", "vs", "binary"):
            family_id, variant, is_boxed = "F2-A", "borderless_centerline", False
            rationale = "Binary contrast routed to F2-A borderless centerline columns."
        else:
            family_id, variant, is_boxed = "F2-A", "minimal_column", False
            rationale = "Three-pillar structure routed to F2-A de-boxed minimal columns with oversized numerals."

    # Stage 2: Physical guardrails, boxed-ratio steering & adjacent anti-collision
    if avoid_boxed and is_boxed and family_id == "F2-C":
        family_id, variant, is_boxed = "F2-B", "editorial_split_rows", False
        rationale += " Steered from Bento (F2-C) to unboxed F2-B to stay under <=40% boxed ratio."

    if prev_canon and family_id == prev_canon and family_id != "F1-A":
        fallbacks: dict[str, tuple[str, str, bool]] = {
            "F1-C": ("F5-B", "kpi_strip", False),
            "F2-A": ("F2-B", "editorial_split_rows", False),
            "F2-B": ("F2-A", "minimal_column" if high_font else "borderless_centerline", False),
            "F2-C": ("F2-B", "editorial_split_rows", False),
            "F3-A": ("F2-B", "editorial_split_rows", False),
            "F3-B": ("F3-A", "fine_track", False),
            "F4-A": ("F4-B", "three_line_table", False),
            "F4-B": ("F2-B", "editorial_split_rows", False),
            "F5-A": ("F5-B", "kpi_strip", False),
            "F5-B": ("F2-B", "editorial_split_rows", False),
            "F5-C": ("F2-B", "editorial_split_rows", False),
        }
        if family_id in fallbacks:
            fb_id, fb_var, fb_box = fallbacks[family_id]
            rationale += f" Switched from {family_id} to {fb_id} to avoid adjacent collision with previous slide."
            family_id, variant, is_boxed = fb_id, fb_var, fb_box

    family_group = family_id.split("-")[0]
    if len(recent_fams) >= 2 and recent_fams[-1] == family_group and recent_fams[-2] == family_group:
        rationale += f" Note: family {family_group} used in 2 preceding slides; verify deck-level <=40% family balance."

    return {
        "family_id": family_id,
        "family_group": family_group,
        "variant": variant,
        "is_boxed": is_boxed,
        "rationale": rationale,
    }


def validate_layout_sequence(
    layouts: Sequence[object],
    require_bookends: bool = True,
    min_distinct: int = 5,
    max_boxed_ratio: float = 0.40,
    max_family_ratio: float = 0.40,
) -> bool:
    """
    Enforce Phase 2 Format C Storyboard Anti-Collision & Rhythm Guardrails:
    - Bidirectionally normalizes both new family codes (`F1-A`..`F5-C`) and legacy codes (`S0`..`S14`, `Hero Stat`).
    1. Bookend Rule (`require_bookends=True`, `len >= 3`): Slide 1 and main closing slide must be `F1-A` (`S0`);
       optional trailing `F4-B`/`S11`/`Appendix` reference slides are allowed after the main closing `F1-A`.
    2. Adjacent Non-Repetition: consecutive slides must not repeat the same layout (preserving legacy `S1` vs `S2` distinction).
    3. Diversity Floor (`min_distinct=5`): scales cleanly for short decks (`< 6` slides).
    4. Boxed Ratio Guardrail (`max_boxed_ratio=0.40`): prevents box-heavy decks (`>= 4` slides).
    5. Single Family Cap (`max_family_ratio=0.40`): prevents over-reliance on any one family (`>= 6` slides).
    Raises `ValueError` on violation; returns `True` when valid.
    """
    parsed = [_normalize_layout_entry(x) for x in layouts]
    n_slides = len(parsed)
    if n_slides == 0:
        raise ValueError("Layout sequence cannot be empty.")

    if require_bookends and n_slides >= 3:
        if parsed[0]["canonical_id"] != "F1-A":
            raise ValueError(
                f"Mandatory Bookend Rule violated: Slide 1 ({parsed[0]['raw']}) must be 'F1-A' / 'S0'."
            )
        # Allow optional trailing Appendix (`F4-B` / `S11`) slides placed after the main closing bookend
        closing_idx = n_slides - 1
        while closing_idx > 1 and parsed[closing_idx]["canonical_id"] == "F4-B":
            closing_idx -= 1
        if parsed[closing_idx]["canonical_id"] != "F1-A":
            raise ValueError(
                f"Mandatory Bookend Rule violated: Main closing slide #{closing_idx + 1} ({parsed[closing_idx]['raw']}) "
                "must be 'F1-A' / 'S0' (trailing F4-B/S11 Appendix slides are allowed after closing)."
            )
        for mid_idx in range(1, closing_idx):
            if parsed[mid_idx]["canonical_id"] == "F1-A":
                raise ValueError(
                    f"Slide {mid_idx + 1} uses '{parsed[mid_idx]['raw']}' (F1-A/S0), which is reserved exclusively for Cover and Closing bookends."
                )

    for i in range(n_slides - 1):
        a = parsed[i]
        b = parsed[i + 1]
        # Collide if exact adjacency key matches OR if either uses the generic canonical code (e.g., F2-A -> S1 or F2-A -> F2-A)
        same_canon = a["canonical_id"] == b["canonical_id"]
        same_adj = a["adj_key"] == b["adj_key"]
        either_generic = (a["adj_key"] == a["canonical_id"]) or (b["adj_key"] == b["canonical_id"])
        if same_adj or (same_canon and either_generic):
            raise ValueError(
                f"Adjacent Layout Collision at Slide {i + 1} -> Slide {i + 2}: "
                f"'{a['raw']}' ({a['canonical_id']}) followed by '{b['raw']}' ({b['canonical_id']}). "
                f"Switch Slide {i + 2} to a distinct layout via `recommend_layout_family()`."
            )

    distinct_canons = {str(p["canonical_id"]) for p in parsed}
    distinct_count = len(distinct_canons)
    max_possible = max(1, (n_slides - 1) if (require_bookends and n_slides >= 3) else n_slides)
    required_distinct = min(int(min_distinct), max_possible)
    if distinct_count < required_distinct:
        raise ValueError(
            f"Insufficient layout diversity: found {distinct_count} distinct layouts ({sorted(distinct_canons)}) "
            f"across {n_slides} slides, but at least {required_distinct} are required to prevent visual habituation."
        )

    if max_boxed_ratio is not None and n_slides >= 4:
        boxed_count = sum(1 for p in parsed if bool(p["boxed"]))
        boxed_ratio = boxed_count / float(n_slides)
        if boxed_ratio > float(max_boxed_ratio) + 1e-9:
            raise ValueError(
                f"Boxed slide ratio {boxed_ratio:.1%} ({boxed_count}/{n_slides}) exceeds max_boxed_ratio "
                f"{float(max_boxed_ratio):.0%}. Convert excess boxed cards to unboxed layouts "
                "(minimal_column / borderless_centerline / F2-B / F3-A fine_track / F4-A borderless)."
            )

    if max_family_ratio is not None and n_slides >= 6:
        fam_counts: dict[str, int] = {}
        for p in parsed:
            fg = str(p["family_group"])
            fam_counts[fg] = fam_counts.get(fg, 0) + 1
        for fg, cnt in fam_counts.items():
            ratio = cnt / float(n_slides)
            if ratio > float(max_family_ratio) + 1e-9:
                raise ValueError(
                    f"Single family '{fg}' occupies {ratio:.1%} ({cnt}/{n_slides}) of slides, "
                    f"exceeding max_family_ratio {float(max_family_ratio):.0%}. Diversify across F1–F5."
                )

    return True


# -------------------------------------------------------------------------
# Step 5: F4 Spec-Driven Deterministic Rendering Layer (`02c_slide_spec_lock.json`)
#   - Standard 4-Zone Schema (`deck_meta`, `design_tokens`, `slides[i].copy`, `slides[i].layout`)
#   - `export_step4a_alignment_preview(spec_json_or_path) -> str`
#   - `render_deck_from_spec(spec_json_or_path, output_pptx_path, ...) -> str`
#   - `check_copy_fidelity(spec_json_or_path, pptx_path) -> dict[str, object]`
# -------------------------------------------------------------------------

SLIDE_SPEC_LOCK_SCHEMA_VERSION = "1.0"

SLIDE_SPEC_LOCK_SCHEMA: dict[str, object] = {
    "schema_version": SLIDE_SPEC_LOCK_SCHEMA_VERSION,
    "description": (
        "Standard 4-zone Format C deterministic slide specification (`02c_slide_spec_lock.json`). "
        "Separates Step 3 frozen human-approved copy (`slides[i].copy`, STRICTLY READ-ONLY in Step 4B) "
        "from Step 4A locked geometry (`slides[i].layout`)."
    ),
    "zones": {
        "deck_meta": {
            "required": False,
            "fields": [
                "title",
                "viewing_context",
                "distance_m",
                "screen_height_m",
                "min_font_pt",
                "design_mode",
                "mode3_tier",
                "art_direction_dna",
                "writing_style_id",
            ],
        },
        "design_tokens": {
            "required": False,
            "fields": [
                "min_font_pt",
                "target_body_pt",
                "doc_theme_id",
                "topic_or_hex",
                "theme_mode",
                "theme_overrides",
                "typography",
            ],
        },
        "slides[i].copy": {
            "required": True,
            "read_only": True,
            "fields": [
                "chapter_pill",
                "right_badge",
                "headline",
                "subtitle",
                "items",
                "zone3_takeaway",
                "speaker_notes",
                "key_numbers",
            ],
            "layout_extensions": [
                "badge_text",
                "footer_text",
                "kpi_cards",
                "section_num",
                "section_title",
                "stat_value",
                "stat_label",
                "context_points",
                "quote",
                "attribution",
                "cards",
                "rows",
                "primary_block",
                "secondary_blocks",
                "steps",
                "nodes",
                "edges",
                "callouts",
                "callout_heading",
                "quadrants",
                "x_axis_label",
                "y_axis_label",
                "headers",
                "table",
                "visual_caption",
                "kpi_items",
                "insight_blocks",
                "focal_title",
                "focal_formula",
                "focal_note",
                "breakdown_items",
            ],
        },
        "slides[i].layout": {
            "required": True,
            "fields": [
                "family_id",
                "variant",
                "spotlight_idx",
                "spotlight_col",
                "include_zone3",
                "zone3_style",
                "visual_asset",
                "geometric_accent",
                "use_omml",
                "borderless",
                "left_ratio",
                "visual_ratio",
                "focal_ratio",
                "callout_position",
                "topology",
                "width_ratios",
                "col_widths",
                "body_font_pt",
                "show_divider",
            ],
        },
    },
}

LAYOUT_FAMILY_LABELS: dict[str, tuple[str, str]] = {
    "F1-A": ("家族 1｜破題與節奏", "封面／封底"),
    "F1-B": ("家族 1｜破題與節奏", "極簡章節過場頁"),
    "F1-C": ("家族 1｜破題與節奏", "巨幅焦點宣言頁"),
    "F2-A": ("家族 2｜觀點並陳", "並列／對比欄"),
    "F2-B": ("家族 2｜觀點並陳", "瑞士網格左標右展"),
    "F2-C": ("家族 2｜觀點並陳", "不對稱便當盒 Bento"),
    "F3-A": ("家族 3｜時序與機制", "流程軌道／交錯時間軸"),
    "F3-B": ("家族 3｜時序與機制", "精簡機制架構圖"),
    "F4-A": ("家族 4｜比較與分類", "2×2 正交四象限"),
    "F4-B": ("家族 4｜比較與分類", "極簡三線比較表"),
    "F5-A": ("家族 5｜實證與解剖", "主圖＋無框導讀"),
    "F5-B": ("家族 5｜實證與解剖", "頂部指標橫帶＋洞察"),
    "F5-C": ("家族 5｜實證與解剖", "焦點公式／指標解剖"),
}

_DRAFT_PLACEHOLDER_RE = re.compile(r"(?<![A-Za-z])(?:TBD|TODO|FIXME)(?![A-Za-z])", re.IGNORECASE)
_FIDELITY_NUM_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9.])(?:[$£€¥])?[+-]?\d+(?:,\d{3})*(?:\.\d+)?(?:%|％|‰)?"
)
_INLINE_BOLD_STRIP_RE = re.compile(r"\*\*((?:(?!\*\*).)+)\*\*")
_SVG_HTML_EXTS = frozenset({".svg", ".html", ".htm"})


def _load_spec_lock(spec_json_or_path: dict[str, object] | str | Path) -> tuple[dict[str, object], Path | None]:
    """
    Load `02c_slide_spec_lock.json` from a file path or deep-copy an in-memory dict so caller data
    (especially frozen `slides[i].copy`) is guaranteed 100% read-only and never mutated.
    """
    if isinstance(spec_json_or_path, dict):
        return copy.deepcopy(spec_json_or_path), None
    if isinstance(spec_json_or_path, (str, Path)):
        p = Path(spec_json_or_path).resolve()
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(f"Slide spec lock file not found: {p}")
        raw = json.loads(p.read_text(encoding="utf-8-sig"))
        if not isinstance(raw, dict):
            raise ValueError(f"Slide spec lock root must be a JSON object; got {type(raw).__name__}.")
        return raw, p.parent
    raise TypeError(
        f"spec_json_or_path must be a dict or path (str/Path); got {type(spec_json_or_path).__name__}."
    )


def _validate_spec_lock_structure(spec: dict[str, object], *, require_layout: bool = True) -> list[dict[str, object]]:
    """Validate the 4-zone structure of `02c_slide_spec_lock.json` and return its slides list."""
    if not isinstance(spec, dict):
        raise ValueError("Slide spec must be a JSON object (dict).")
    for zone_key in ("deck_meta", "design_tokens"):
        if zone_key in spec and spec[zone_key] is not None and not isinstance(spec[zone_key], dict):
            raise ValueError(f"Spec zone '{zone_key}' must be an object (dict) when provided.")
    slides = spec.get("slides")
    if not isinstance(slides, list) or len(slides) == 0:
        raise ValueError("Spec must contain a non-empty 'slides' array.")
    for idx, sl in enumerate(slides, start=1):
        if not isinstance(sl, dict):
            raise ValueError(f"Slide #{idx} entry must be a dict.")
        if not isinstance(sl.get("copy"), dict):
            raise ValueError(f"Slide #{idx} is missing required read-only 'copy' dict zone.")
        if require_layout:
            lay = sl.get("layout")
            if not isinstance(lay, dict) or not str(lay.get("family_id", lay.get("layout", lay.get("code", "")))).strip():
                raise ValueError(f"Slide #{idx} is missing required 'layout.family_id' specification.")
        elif "layout" in sl and sl["layout"] is not None and not isinstance(sl["layout"], dict):
            raise ValueError(f"Slide #{idx} 'layout' must be a dict when provided.")
    return slides


def _resolve_spec_design_tokens(spec: dict[str, object]) -> dict[str, object]:
    """Build unified design tokens from `deck_meta` + `design_tokens` (including Mode 3 CIELAB dynamic themes)."""
    deck_meta = spec.get("deck_meta") if isinstance(spec.get("deck_meta"), dict) else {}
    dt_cfg = spec.get("design_tokens") if isinstance(spec.get("design_tokens"), dict) else {}
    dna = deck_meta.get("art_direction_dna") or deck_meta.get("topic_art_direction_dna") or {}
    if not isinstance(dna, dict):
        dna = {}

    min_font_raw = dt_cfg.get("min_font_pt", deck_meta.get("min_font_pt", MIN_CONTENT_FONT_PT))
    min_font_pt = float(min_font_raw) if min_font_raw is not None else MIN_CONTENT_FONT_PT

    dist_raw = dt_cfg.get("distance_m", deck_meta.get("distance_m"))
    screen_raw = dt_cfg.get("screen_height_m", deck_meta.get("screen_height_m"))
    distance_m = float(dist_raw) if dist_raw is not None else None
    screen_height_m = float(screen_raw) if screen_raw is not None else None
    if (distance_m is None) != (screen_height_m is None):
        distance_m = None
        screen_height_m = None

    target_body_raw = dt_cfg.get("target_body_pt", deck_meta.get("target_body_pt"))
    target_body_pt = float(target_body_raw) if target_body_raw is not None else None

    doc_theme_id = dt_cfg.get("doc_theme_id") or deck_meta.get("doc_theme_id")
    topic_or_hex = (
        dt_cfg.get("topic_or_hex")
        or dt_cfg.get("dynamic_topic")
        or dna.get("topic_or_hex")
        or dna.get("seed_hex")
        or deck_meta.get("topic_or_hex")
    )
    theme_mode = str(
        dt_cfg.get("theme_mode")
        or dna.get("theme_mode")
        or deck_meta.get("theme_mode")
        or "light_classroom"
    ).strip()

    theme_overrides: dict[str, str] = {}
    if isinstance(dt_cfg.get("theme"), dict):
        for k, v in dt_cfg["theme"].items():  # type: ignore[union-attr]
            if v is not None:
                theme_overrides[str(k)] = str(v)
    if isinstance(dt_cfg.get("theme_overrides"), dict):
        for k, v in dt_cfg["theme_overrides"].items():  # type: ignore[union-attr]
            if v is not None:
                theme_overrides[str(k)] = str(v)

    return build_slide_design_tokens(
        min_font_pt=min_font_pt,
        target_body_pt=target_body_pt,
        doc_theme_id=str(doc_theme_id) if doc_theme_id else None,
        theme_overrides=theme_overrides or None,
        distance_m=distance_m,
        screen_height_m=screen_height_m,
        topic_or_hex=topic_or_hex,
        theme_mode=theme_mode,
    )


def _should_render_zone3(copy_zone: dict[str, object], layout_zone: dict[str, object], canonical_id: str) -> bool:
    """SSOT decision on whether `zone3_takeaway` (or `footer_text` on F1-A) should be rendered & fidelity-checked."""
    inc = layout_zone.get("include_zone3")
    takeaway = _first_non_empty_str(copy_zone, "zone3_takeaway")
    if canonical_id == "F1-A":
        footer = _first_non_empty_str(copy_zone, "footer_text")
        if footer:
            return True
        return bool(takeaway) and (inc is not False)
    if canonical_id == "F1-B":
        return (inc is True) and bool(takeaway)
    if inc is False:
        return False
    return bool(takeaway)


def _resolve_visual_asset_info(
    layout_zone: dict[str, object],
    copy_zone: dict[str, object],
    base_dir: Path | None = None,
) -> dict[str, object]:
    """Parse `layout.visual_asset` (string or dict) without mutating input spec."""
    raw = layout_zone.get("visual_asset")
    if raw is None and copy_zone.get("image_path"):
        raw = copy_zone.get("image_path")

    info: dict[str, object] = {
        "raw_path": "",
        "resolved_path": None,
        "kind": "",
        "mode3_tier": None,
        "is_slide_variant": False,
        "is_svg_or_html": False,
        "placement": "visual_zone",
        "width_px": 1200,
        "height_px": 800,
        "scale_factor": 3.0,
        "dpi": 300,
        "transparent": True,
        "engine": "auto",
        "out_png_path": None,
        "rect_in": None,
    }
    if not raw:
        return info

    if isinstance(raw, (str, Path)):
        raw_path = str(raw).strip()
    elif isinstance(raw, dict):
        raw_path = _first_non_empty_str(raw, "path", "image_path", "src", "file")
        info["kind"] = _first_non_empty_str(raw, "kind", "type")
        if raw.get("mode3_tier") is not None:
            info["mode3_tier"] = raw.get("mode3_tier")
        elif raw.get("tier") is not None:
            info["mode3_tier"] = raw.get("tier")
        if raw.get("is_slide_variant") is not None:
            info["is_slide_variant"] = bool(raw.get("is_slide_variant"))
        if raw.get("placement") or raw.get("position"):
            info["placement"] = str(raw.get("placement") or raw.get("position")).strip().lower()
        for num_k in ("width_px", "height_px", "dpi"):
            if raw.get(num_k) is not None:
                info[num_k] = int(raw[num_k])  # type: ignore[arg-type]
        if raw.get("scale_factor") is not None:
            info["scale_factor"] = float(raw["scale_factor"])  # type: ignore[arg-type]
        if raw.get("transparent") is not None:
            info["transparent"] = bool(raw["transparent"])
        if raw.get("engine"):
            info["engine"] = str(raw["engine"])
        if raw.get("out_png_path"):
            info["out_png_path"] = str(raw["out_png_path"])
        if all(raw.get(rk) is not None for rk in ("left_in", "top_in", "width_in", "height_in")):
            info["rect_in"] = (
                float(raw["left_in"]),  # type: ignore[arg-type]
                float(raw["top_in"]),  # type: ignore[arg-type]
                float(raw["width_in"]),  # type: ignore[arg-type]
                float(raw["height_in"]),  # type: ignore[arg-type]
            )
    else:
        return info

    info["raw_path"] = raw_path
    if not raw_path:
        return info

    p_obj = Path(raw_path)
    low_name = p_obj.name.lower()
    if low_name.endswith("_slide.png") or "_slide." in low_name:
        info["is_slide_variant"] = True
    if p_obj.suffix.lower() in _SVG_HTML_EXTS:
        info["is_svg_or_html"] = True
        if info["mode3_tier"] is None:
            info["mode3_tier"] = 3

    resolved: Path | None = None
    if p_obj.is_absolute():
        resolved = p_obj
    else:
        candidates = []
        if base_dir is not None:
            candidates.append((base_dir / p_obj).resolve())
        candidates.append((Path.cwd() / p_obj).resolve())
        for cand in candidates:
            if cand.exists():
                resolved = cand
                break
        if resolved is None:
            resolved = candidates[0]
    info["resolved_path"] = resolved
    return info


def _materialize_visual_asset_png(
    asset_info: dict[str, object],
    temp_files: list[Path],
    base_dir: Path | None = None,
) -> str | None:
    """Resolve a PNG path for embedding, rendering `.svg`/`.html` via `render_svg_to_png_300dpi()` for Tier 3."""
    resolved = asset_info.get("resolved_path")
    if not isinstance(resolved, Path):
        return None
    if not resolved.exists():
        raise FileNotFoundError(f"Spec visual_asset not found: {resolved}")

    if bool(asset_info.get("is_svg_or_html")):
        out_raw = asset_info.get("out_png_path")
        if out_raw:
            out_p = Path(str(out_raw))
            if not out_p.is_absolute() and base_dir is not None:
                out_p = (base_dir / out_p).resolve()
            else:
                out_p = out_p.resolve()
        else:
            fd, tmp_name = tempfile.mkstemp(prefix="_pptx_tier3_", suffix=".png")
            os.close(fd)
            out_p = Path(tmp_name)
            temp_files.append(out_p)
        return render_svg_to_png_300dpi(
            resolved,
            out_p,
            width_px=int(asset_info.get("width_px", 1200)),  # type: ignore[arg-type]
            height_px=int(asset_info.get("height_px", 800)),  # type: ignore[arg-type]
            engine=str(asset_info.get("engine", "auto")),
            scale_factor=float(asset_info.get("scale_factor", 3.0)),  # type: ignore[arg-type]
            dpi=int(asset_info.get("dpi", 300)),  # type: ignore[arg-type]
            transparent=bool(asset_info.get("transparent", True)),
        )

    return str(resolved)


def _place_overlay_picture(slide, png_path: str, asset_info: dict[str, object], *, default_behind: bool = True) -> None:
    """Embed a Mode 3 Tier 2/3 visual asset on bookend/divider/custom slides without colliding with text."""
    rect_in = asset_info.get("rect_in")
    placement = str(asset_info.get("placement") or "").strip().lower()
    behind = (placement == "background") or (default_behind and rect_in is None and placement not in ("right", "left"))

    if isinstance(rect_in, tuple) and len(rect_in) == 4:
        vx, vy, vw, vh = rect_in
    elif placement == "right":
        vx, vy, vw, vh = 8.40, 0.90, 4.43, 5.70
    elif placement == "left":
        vx, vy, vw, vh = 0.50, 0.90, 4.43, 5.70
    else:
        vx, vy, vw, vh = 0.0, 0.0, 13.333, 7.50

    px_w, px_h = _read_image_pixel_size(Path(png_path))
    img_ar = float(px_w) / max(1.0, float(px_h))
    box_ar = vw / max(0.1, vh)
    if img_ar >= box_ar:
        pw = vw
        ph = vw / img_ar
    else:
        ph = vh
        pw = vh * img_ar
    px = vx + (vw - pw) / 2.0
    py = vy + (vh - ph) / 2.0

    pic = slide.shapes.add_picture(png_path, Inches(px), Inches(py), width=Inches(pw), height=Inches(ph))
    if behind:
        with suppress(AttributeError, ValueError, TypeError):
            sp_tree = slide.shapes._spTree
            sp_tree.remove(pic._element)
            # Insert immediately after nvGrpSpPr + grpSpPr so the image renders behind all text shapes
            sp_tree.insert(2, pic._element)


def _apply_tier1_geometric_accent(slide, layout_zone: dict[str, object], tokens: dict[str, object]) -> None:
    """Apply optional Mode 3 Tier 1 native geometric accent motif specified on a slide."""
    accent_spec = layout_zone.get("geometric_accent")
    if accent_spec is None:
        accent_spec = layout_zone.get("tier1_motif")
    if not accent_spec:
        return
    if isinstance(accent_spec, str):
        draw_theme_geometric_accent(slide, motif_type=accent_spec, tokens=tokens)
    elif isinstance(accent_spec, dict):
        motif_type = _first_non_empty_str(accent_spec, "motif_type", "type", "motif", default="diagonal_wedge")
        extra_kw = {k: v for k, v in accent_spec.items() if k not in ("motif_type", "type", "motif")}
        draw_theme_geometric_accent(slide, motif_type=motif_type, tokens=tokens, **extra_kw)


def _strip_inline_bold(text: str) -> str:
    """Strip valid `**bold**` markers the same way `_populate_paragraph_runs()` renders them."""
    return _INLINE_BOLD_STRIP_RE.sub(r"\1", str(text or ""))


def _escape_md_cell(text: str, max_len: int | None = None) -> str:
    """Escape a string cleanly for single-row GitHub-flavored Markdown tables."""
    clean = re.sub(r"\s+", " ", _strip_inline_bold(str(text or "")).strip())
    if max_len is not None and len(clean) > max_len:
        clean = clean[: max(1, max_len - 1)].rstrip() + "…"
    return clean.replace("|", "\\|")


def _summarize_slide_copy_skeleton(
    copy_zone: dict[str, object],
    layout_zone: dict[str, object],
    canonical_id: str,
) -> str:
    """Build a concise human-readable skeleton of slide copy items with `★` spotlight indicator for Step 4A."""
    spot_idx = layout_zone.get("spotlight_idx")
    spot_col = layout_zone.get("spotlight_col")

    def _fmt_entry(idx: int, raw: object, is_spot: bool) -> str:
        prefix = "★" if is_spot else "•"
        if isinstance(raw, dict):
            val = _first_non_empty_str(raw, "value", "stat", "metric", "kpi")
            title = _first_non_empty_str(raw, "title", "heading", "label", "name", "lead")
            sub = _first_non_empty_str(raw, "body", "desc", "detail", "note", "text", "subtitle")
            parts = [p for p in (val, title) if p]
            head = " ".join(parts) if parts else sub
            if not head:
                sub_items = _extract_lead_body_items(raw)
                head = sub_items[0][0] or sub_items[0][1] if sub_items else f"項目 {idx + 1}"
            return f"{prefix} {_escape_md_cell(head, 34)}"
        ld, bd = _parse_lead_body_item(raw)
        txt = ld or bd or f"項目 {idx + 1}"
        return f"{prefix} {_escape_md_cell(txt, 34)}"

    lines: list[str] = []
    if canonical_id == "F1-A":
        kpis = copy_zone.get("kpi_cards") or copy_zone.get("items") or []
        if isinstance(kpis, list) and kpis:
            for i, it in enumerate(kpis[:3]):
                lines.append(_fmt_entry(i, it, is_spot=(spot_idx == i) or (isinstance(it, dict) and bool(it.get("is_spotlight")))))
        elif copy_zone.get("subtitle"):
            lines.append(f"副標：{_escape_md_cell(str(copy_zone['subtitle']), 46)}")
        else:
            lines.append("封面／峰終主視覺定錨")
    elif canonical_id == "F1-B":
        sec_num = _first_non_empty_str(copy_zone, "section_num", "chapter_pill")
        sub = _first_non_empty_str(copy_zone, "subtitle")
        if sec_num:
            sec_disp = f"{int(sec_num):02d}" if sec_num.isdigit() else sec_num
            lines.append(f"章節序號：`{sec_disp}`")
        if sub:
            lines.append(f"引導語：{_escape_md_cell(sub, 44)}")
        if not lines:
            lines.append("高留白章節過場換氣")
    elif canonical_id == "F1-C":
        val = _first_non_empty_str(copy_zone, "stat_value", "quote", "manifesto")
        lbl = _first_non_empty_str(copy_zone, "stat_label", "attribution")
        if val:
            lines.append(f"★ 焦點：{_escape_md_cell(val, 38)}")
        if lbl:
            lines.append(f"說明：{_escape_md_cell(lbl, 38)}")
        pts = copy_zone.get("context_points") or copy_zone.get("items") or []
        if isinstance(pts, list):
            for i, it in enumerate(pts[:3]):
                lines.append(_fmt_entry(i, it, is_spot=(spot_idx == i)))
    elif canonical_id == "F2-C":
        pri = copy_zone.get("primary_block")
        secs = copy_zone.get("secondary_blocks")
        if pri is None and isinstance(copy_zone.get("items"), list) and copy_zone["items"]:
            pri = copy_zone["items"][0]
            secs = copy_zone["items"][1:]
        if pri is not None:
            eff_spot = 0 if spot_idx is None else spot_idx
            lines.append(_fmt_entry(0, pri, is_spot=(eff_spot == 0)))
        if isinstance(secs, list):
            eff_spot = 0 if spot_idx is None else spot_idx
            for i, sb in enumerate(secs[:3], start=1):
                lines.append(_fmt_entry(i, sb, is_spot=(eff_spot == i)))
    elif canonical_id == "F4-B":
        tbl = copy_zone.get("table") if isinstance(copy_zone.get("table"), dict) else {}
        hdrs = copy_zone.get("headers") or tbl.get("headers") or []
        rows = copy_zone.get("rows") or tbl.get("rows") or []
        eff_col = spot_col if spot_col is not None else spot_idx
        if isinstance(hdrs, list) and hdrs:
            fmt_hdrs = [
                f"★{_escape_md_cell(str(h), 16)}" if (eff_col == c_i) else _escape_md_cell(str(h), 16)
                for c_i, h in enumerate(hdrs)
            ]
            lines.append("欄：" + " / ".join(fmt_hdrs))
        if isinstance(rows, list):
            lines.append(f"共 {len(rows)} 列對比資料")
    elif canonical_id == "F5-B":
        kpis = copy_zone.get("kpi_items") or copy_zone.get("kpis") or []
        ins = copy_zone.get("insight_blocks") or copy_zone.get("insights") or (copy_zone.get("items") if kpis else [])
        eff_spot = 0 if spot_idx is None else spot_idx
        if isinstance(kpis, list):
            for i, k in enumerate(kpis[:4]):
                lines.append(_fmt_entry(i, k, is_spot=(eff_spot == i)))
        if isinstance(ins, list) and ins:
            lines.append(f"下方洞察：{len(ins)} 欄")
    elif canonical_id == "F5-C":
        ft = _first_non_empty_str(copy_zone, "focal_title")
        ff = _first_non_empty_str(copy_zone, "focal_formula", "formula")
        if ft or ff:
            lines.append(f"★ 焦點：{_escape_md_cell(ft or ff, 40)}")
        bds = copy_zone.get("breakdown_items") or copy_zone.get("items") or []
        if isinstance(bds, list):
            for i, b in enumerate(bds[:4]):
                lines.append(_fmt_entry(i, b, is_spot=(i == 0)))
    elif canonical_id == "F5-A":
        raw_c_upper = _first_non_empty_str(layout_zone, "family_id", "layout", "code").upper().replace("_", "-")
        c_pos = _first_non_empty_str(layout_zone, "callout_position").lower()
        var_low = str(_normalize_layout_entry(layout_zone).get("variant") or "").strip().lower()
        is_hdr_only = (c_pos == "header_only") or (not c_pos and (var_low == "header_only" or raw_c_upper == "S7-D"))
        c_head = _first_non_empty_str(copy_zone, "callout_heading")
        cs = copy_zone.get("callouts") or copy_zone.get("items") or []
        if is_hdr_only:
            lines.append("全幅純圖（`header_only`）")
            if isinstance(cs, list) and cs:
                lines.append(f"⚠️ `header_only` 將省略 {len(cs)} 項凍結導讀文案")
        else:
            if c_head:
                lines.append(f"導讀題：{_escape_md_cell(c_head, 32)}")
            eff_spot = 0 if spot_idx is None else spot_idx
            if isinstance(cs, list) and cs:
                for i, c in enumerate(cs[:4]):
                    lines.append(_fmt_entry(i, c, is_spot=(eff_spot == i)))
            else:
                lines.append("全幅純圖（`header_only`）")
    else:
        # F2-A, F2-B, F3-A, F3-B, F4-A
        coll = (
            copy_zone.get("cards")
            or copy_zone.get("rows")
            or copy_zone.get("steps")
            or copy_zone.get("nodes")
            or copy_zone.get("quadrants")
            or copy_zone.get("items")
            or []
        )
        if isinstance(coll, list):
            for i, it in enumerate(coll[:5]):
                is_sp = (spot_idx == i) if spot_idx is not None else (isinstance(it, dict) and bool(it.get("is_spotlight")))
                lines.append(_fmt_entry(i, it, is_spot=is_sp))
        if canonical_id == "F3-B" and isinstance(copy_zone.get("callouts"), list) and copy_zone["callouts"]:
            lines.append(f"旁側導讀：{len(copy_zone['callouts'])} 點")

    return "<br>".join(lines) if lines else "—"


def export_step4a_alignment_preview(spec_json_or_path: dict[str, object] | str | Path) -> str:
    """
    [Step 4A] Export a clean, human-readable Markdown slide-by-slide layout & visual asset alignment table
    from `02c_slide_spec_lock.json` (never exposing raw JSON to the user).
    Strictly read-only: never mutates the input spec.
    """
    spec, base_dir = _load_spec_lock(spec_json_or_path)
    slides = _validate_spec_lock_structure(spec, require_layout=False)
    deck_meta = spec.get("deck_meta") if isinstance(spec.get("deck_meta"), dict) else {}
    tokens = _resolve_spec_design_tokens(spec)
    typo = tokens["typography"]  # type: ignore[index]

    dt_cfg = spec.get("design_tokens") if isinstance(spec.get("design_tokens"), dict) else {}
    dna_raw = deck_meta.get("art_direction_dna") or deck_meta.get("topic_art_direction_dna") or {}
    dna = dna_raw if isinstance(dna_raw, dict) else {}

    title = _first_non_empty_str(deck_meta, "title", "project_title", default="Format C 簡報配置對齊表")
    viewing_ctx = _first_non_empty_str(deck_meta, "viewing_context", "context", "scenario", default="自適應簡報")
    dist_m = dt_cfg.get("distance_m", deck_meta.get("distance_m"))
    screen_h = dt_cfg.get("screen_height_m", deck_meta.get("screen_height_m"))
    discas_str = (
        f"D={dist_m}m / H={screen_h}m → 地板 `{tokens['min_font_pt']}pt`"
        if (dist_m is not None and screen_h is not None)
        else f"地板 `{tokens['min_font_pt']}pt`"
    )
    design_mode = deck_meta.get("design_mode", "Mode 1 (rigorous)")
    mode3_tier = deck_meta.get("mode3_tier", deck_meta.get("tier"))
    mode_str = f"{design_mode}" + (f" / Tier {mode3_tier}" if mode3_tier is not None else "")
    topic_seed = (
        dt_cfg.get("topic_or_hex")
        or dt_cfg.get("dynamic_topic")
        or dna.get("topic_or_hex")
        or dna.get("seed_hex")
        or deck_meta.get("topic_or_hex")
    )
    theme_label = (
        f"動態 CIELAB (`{topic_seed}`)"
        if topic_seed
        else f"靜態主題 (`{tokens.get('doc_theme_id') or 'default'}`)"
    )
    style_id = _first_non_empty_str(deck_meta, "writing_style_id", "style_id", default="預設筆風")

    out: list[str] = [
        f"## Step 4A 渲染前逐頁配置與配圖對齊表 — {title}",
        "",
        f"- **觀看情境與 DISCAS**：{viewing_ctx}（{discas_str}；全檔統一基準 `target_body_pt = {tokens['target_body_pt']}pt`，斷言主標 `{typo['headline']}pt`）",
        f"- **總頁數／模式／主題／筆風**：共 `{len(slides)}` 頁｜設計光譜：`{mode_str}`｜配色：{theme_label}｜筆風：`{style_id}`",
    ]
    if dna:
        metaphor = _first_non_empty_str(dna, "core_metaphor", "visual_metaphor", "motif")
        if metaphor:
            out.append(f"- **Topic Art Direction DNA**：{metaphor}")

    out.extend([
        "",
        "| 頁次 | 家族與版型 | 定稿標題 | 文案骨架與 ★聚光燈 | 配圖／模式 3 標記 | Zone 3 |",
        "| :---: | :--- | :--- | :--- | :--- | :--- |",
    ])

    layout_entries: list[dict[str, object]] = []
    total_key_nums = 0
    draft_flags: list[str] = []

    for idx, sl in enumerate(slides, start=1):
        copy_z: dict[str, object] = sl["copy"]  # type: ignore[assignment]
        lay_z: dict[str, object] = sl.get("layout") if isinstance(sl.get("layout"), dict) else {}  # type: ignore[assignment]
        layout_entries.append(lay_z)

        raw_code = _first_non_empty_str(lay_z, "family_id", "layout", "code")
        norm = _normalize_layout_entry(lay_z) if raw_code else {"canonical_id": "待定", "variant": "", "boxed": False, "family_group": "?"}
        canon_id = str(norm["canonical_id"])
        variant = str(norm.get("variant") or "")
        fam_label = LAYOUT_FAMILY_LABELS.get(canon_id, ("未分類", canon_id))[1]
        layout_cell = f"**`{canon_id}`** {fam_label}" + (f"<br>`{variant}`" if variant else "")

        pill = _first_non_empty_str(copy_z, "chapter_pill", "badge_text", "section_num")
        if canon_id == "F1-B" and pill.isdigit():
            pill = f"{int(pill):02d}"
        headline = _first_non_empty_str(copy_z, "headline", "main_title", "section_title", default="(無標題)")
        title_cell = (f"`{_escape_md_cell(pill, 22)}`<br>" if pill else "") + f"**{_escape_md_cell(headline, 44)}**"

        skeleton_cell = _summarize_slide_copy_skeleton(copy_z, lay_z, canon_id)

        # Visual asset & Mode 3 markers
        asset_tags: list[str] = []
        asset_info = _resolve_visual_asset_info(lay_z, copy_z, base_dir=base_dir)
        if asset_info["raw_path"]:
            fname = Path(str(asset_info["raw_path"])).name
            if asset_info["is_svg_or_html"]:
                asset_tags.append(f"`{fname}` [Mode 3 Tier 3 SVG/HTML 300DPI]")
            elif asset_info["is_slide_variant"]:
                asset_tags.append(f"`{fname}` [專用 `*_slide.png`]")
            elif asset_info["mode3_tier"] == 2 or str(asset_info["kind"]).lower() == "tier2_concept":
                asset_tags.append(f"`{fname}` [Mode 3 Tier 2 概念視覺]")
            else:
                asset_tags.append(f"`{fname}`")
        geo_acc = lay_z.get("geometric_accent") or lay_z.get("tier1_motif")
        if geo_acc:
            m_name = geo_acc.get("motif_type", "motif") if isinstance(geo_acc, dict) else str(geo_acc)
            asset_tags.append(f"[Mode 3 Tier 1: `{m_name}`]")
        if bool(lay_z.get("use_omml")) or bool(copy_z.get("use_omml")):
            asset_tags.append("[原生 OMML 公式]")
        asset_cell = "<br>".join(asset_tags) if asset_tags else "— 純原生排版"

        # Zone 3 column
        if _should_render_zone3(copy_z, lay_z, canon_id):
            z3_txt = _first_non_empty_str(copy_z, "footer_text", "zone3_takeaway")
            z3_style = _first_non_empty_str(lay_z, "zone3_style", default="dark_banner" if canon_id != "F1-A" else "footer")
            z3_cell = f"保留 (`{z3_style}`)<br>{_escape_md_cell(z3_txt, 26)}"
        else:
            z3_cell = "省略"

        out.append(f"| S{idx:02d} | {layout_cell} | {title_cell} | {skeleton_cell} | {asset_cell} | {z3_cell} |")

        k_nums = copy_z.get("key_numbers")
        if isinstance(k_nums, list):
            total_key_nums += len([k for k in k_nums if str(k or "").strip()])
        raw_copy_blob = json.dumps(copy_z, ensure_ascii=False)
        if _DRAFT_PLACEHOLDER_RE.search(raw_copy_blob):
            draft_flags.append(f"S{idx:02d}")

    # Pre-render diagnostic footer (non-throwing so user sees exact rhythm status before locking)
    out.append("")
    out.append("### 渲染前節奏與保真預檢摘要")
    has_all_layouts = all(bool(_first_non_empty_str(le, "family_id", "layout", "code")) for le in layout_entries)
    if has_all_layouts:
        parsed_ls = [_normalize_layout_entry(le) for le in layout_entries]
        n_tot = len(parsed_ls)
        boxed_cnt = sum(1 for p in parsed_ls if bool(p["boxed"]))
        distinct_ids = sorted({str(p["canonical_id"]) for p in parsed_ls})
        fam_cnts = Counter(str(p["family_group"]) for p in parsed_ls)
        fam_summary = "、".join(f"`{fg}` {cnt}/{n_tot} ({cnt / n_tot:.0%})" for fg, cnt in sorted(fam_cnts.items()))
        try:
            validate_layout_sequence(layout_entries)
            seq_status = "✅ 通過防撞車、帶框比與家族均衡護欄"
        except ValueError as exc:
            seq_status = f"⚠️ 需調整：{exc}"
        out.append(f"- **版型序列檢核**：{seq_status}")
        out.append(f"- **版型多樣性與去方塊比**：共 `{len(distinct_ids)}` 種版型（`{', '.join(distinct_ids)}`）｜帶框頁 `{boxed_cnt}/{n_tot}`（`{boxed_cnt / n_tot:.0%}`，上限 `<=40%`）")
        out.append(f"- **五大簡報家族分布**：{fam_summary}（單家族上限 `<=40%`）")
    else:
        out.append("- **版型序列檢核**：尚有頁面未鎖定 `layout.family_id`。")

    draft_note = "無殘留 `TBD`/`TODO`" if not draft_flags else f"⚠️ 偵測到草稿佔位字於 {', '.join(draft_flags)}"
    out.append(f"- **拍板文案凍結預檢**：已標記關鍵數字 `{total_key_nums}` 項｜{draft_note}")

    return "\n".join(out)


def _adapt_f1a_kpi_cards(raw_items: object) -> list[dict[str, str]] | None:
    """Adapt F1-A `kpi_cards` or Lead/Body `items` cleanly without mutating the source spec."""
    if not isinstance(raw_items, list) or not raw_items:
        return None
    adapted: list[dict[str, str]] = []
    for it in raw_items:
        if isinstance(it, dict):
            card: dict[str, str] = {}
            kicker = _first_non_empty_str(it, "kicker", "badge")
            title = _first_non_empty_str(it, "title", "heading", "label", "lead", "name")
            if kicker and title and kicker != title:
                title = f"{kicker}｜{title}"
            elif kicker and not title:
                title = kicker
            value = _first_non_empty_str(it, "value", "stat", "metric", "kpi")
            sub = _first_non_empty_str(it, "subtitle", "sub")
            desc_body = _first_non_empty_str(it, "desc", "body", "detail", "note", "text")
            if sub and desc_body and sub != desc_body:
                desc = f"{sub}｜{desc_body}"
            else:
                desc = desc_body or sub
            if title:
                card["title"] = title
            if value:
                card["value"] = value
            if desc:
                card["desc"] = desc
            if it.get("accent"):
                card["accent"] = str(it["accent"])
            if it.get("is_spotlight") is not None:
                card["is_spotlight"] = bool(it["is_spotlight"])  # type: ignore[assignment]
            adapted.append(card)
        else:
            ld, bd = _parse_lead_body_item(it)
            adapted.append({"title": ld or bd, "desc": bd if ld else ""})
    return adapted


def _coerce_spec_block_dict(raw: object) -> dict[str, object]:
    """Coerce a Step 3 Lead/Body string or tuple into a standard block dict without mutating caller data."""
    if isinstance(raw, dict):
        return dict(raw)
    ld, bd = _parse_lead_body_item(raw)
    if ld and bd:
        return {"title": ld, "body": bd}
    return {"title": ld or bd, "body": ""}


def _coerce_kpi_item_dict(raw: object) -> dict[str, object]:
    """Coerce a Step 3 KPI item (dict or `'value：label'` string) into a dict for `draw_kpi_strip_slide()`."""
    if isinstance(raw, dict):
        return dict(raw)
    ld, bd = _parse_lead_body_item(raw)
    if ld and bd:
        return {"value": ld, "label": bd}
    return {"value": ld or bd, "label": ""}


def _render_single_spec_slide(
    prs: Presentation,
    slide_spec: dict[str, object],
    slide_idx: int,
    tokens: dict[str, object],
    base_dir: Path | None,
    temp_files: list[Path],
) -> None:
    """Deterministically render one slide from its read-only `copy` + locked `layout` zones."""
    copy_z: dict[str, object] = slide_spec["copy"]  # type: ignore[assignment]
    lay_z: dict[str, object] = slide_spec["layout"]  # type: ignore[assignment]

    norm = _normalize_layout_entry(lay_z)
    canon_id = str(norm["canonical_id"])
    raw_code_upper = _first_non_empty_str(lay_z, "family_id", "layout", "code").upper().replace("_", "-")
    variant = str(norm.get("variant") or "").strip().lower()

    asset_info = _resolve_visual_asset_info(lay_z, copy_z, base_dir=base_dir)
    mat_png = _materialize_visual_asset_png(asset_info, temp_files, base_dir=base_dir)

    resolved_body_pt = (
        float(lay_z["body_font_pt"])
        if lay_z.get("body_font_pt") is not None
        else float(tokens["target_body_pt"])  # type: ignore[arg-type]
    )
    speaker_notes = _first_non_empty_str(copy_z, "speaker_notes")
    use_zone3 = _should_render_zone3(copy_z, lay_z, canon_id)
    z3_text = _first_non_empty_str(copy_z, "zone3_takeaway")
    z3_style = _first_non_empty_str(lay_z, "zone3_style", default="dark_banner")
    spot_idx = lay_z.get("spotlight_idx")
    if spot_idx is not None:
        spot_idx = int(spot_idx)  # type: ignore[arg-type]

    # --- Family 1-A: Cover / Closing Bookend (first arg is `prs`) ---
    if canon_id == "F1-A":
        badge_txt = _first_non_empty_str(copy_z, "badge_text", "chapter_pill")
        main_title = _first_non_empty_str(copy_z, "headline", "main_title", "title")
        subtitle = _first_non_empty_str(copy_z, "subtitle")
        kpi_cards = _adapt_f1a_kpi_cards(copy_z.get("kpi_cards") or copy_z.get("items"))
        footer_txt = _first_non_empty_str(copy_z, "footer_text") or (z3_text if use_zone3 else None)
        bg_hex = str(lay_z["bg_hex"]) if lay_z.get("bg_hex") else None
        accent_hex = str(lay_z["accent_hex"]) if lay_z.get("accent_hex") else None
        slide = add_bookend_slide_s0(
            prs,
            badge_text=badge_txt,
            main_title=main_title,
            subtitle_text=subtitle,
            kpi_cards=kpi_cards,
            speaker_notes=speaker_notes or None,
            bg_hex=bg_hex,
            accent_hex=accent_hex,
            footer_text=footer_txt,
            tokens=tokens,
        )
        if mat_png:
            _place_overlay_picture(slide, mat_png, asset_info, default_behind=True)
        _apply_tier1_geometric_accent(slide, lay_z, tokens)
        return

    # All other 12 layouts operate on a blank slide
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg_override = str(lay_z["bg_hex"]) if lay_z.get("bg_hex") else None
    set_slide_background(slide, bg_hex=bg_override, tokens=tokens)

    # --- Family 1-B: Ultra-Minimal Section Divider ---
    if canon_id == "F1-B":
        sec_num = _first_non_empty_str(copy_z, "section_num", "chapter_pill", default=f"{slide_idx:02d}")
        sec_title = _first_non_empty_str(copy_z, "section_title", "headline", "title")
        sec_sub = _first_non_empty_str(copy_z, "subtitle")
        draw_section_divider_slide(
            slide,
            section_num=sec_num,
            section_title=sec_title,
            subtitle_text=sec_sub,
            tokens=tokens,
        )
        if use_zone3 and z3_text:
            add_zone3_footer(slide, z3_text, style=z3_style, tokens=tokens)
        if mat_png:
            _place_overlay_picture(slide, mat_png, asset_info, default_behind=True)
        _apply_tier1_geometric_accent(slide, lay_z, tokens)
        if speaker_notes:
            add_speaker_notes(slide, speaker_notes)
        return

    # --- Standard Content & Impact Slides (F1-C .. F5-C): Zone 1 -> Optional Zone 3 -> Zone 2 ---
    pill_txt = _first_non_empty_str(copy_z, "chapter_pill", "badge_text")
    headline_txt = _first_non_empty_str(copy_z, "headline", "title")
    subtitle_txt = _first_non_empty_str(copy_z, "subtitle") or None
    right_badge_txt = _first_non_empty_str(copy_z, "right_badge") or None
    show_divider = bool(lay_z.get("show_divider", True))

    if pill_txt or headline_txt or subtitle_txt or right_badge_txt:
        z2_top = add_zone1_header(
            slide,
            chapter_pill_text=pill_txt,
            assertion_headline=headline_txt,
            subtitle_text=subtitle_txt,
            right_badge_text=right_badge_txt,
            show_divider=show_divider,
            tokens=tokens,
        )
    else:
        z2_top = 0.56

    # Render optional Zone 3 BEFORE Zone 2 so Zone 2 reserves exact non-overlapping height
    z2_height: float | None = None
    if use_zone3 and z3_text:
        before_cnt = len(slide.shapes)
        add_zone3_footer(slide, z3_text, style=z3_style, tokens=tokens)
        z3_tops = [
            float(shp.top or 0) / 914400.0
            for shp in list(slide.shapes)[before_cnt:]
        ]
        if z3_tops:
            min_z3_top = min(z3_tops)
            z2_height = round(max(1.60, min_z3_top - 0.14 - z2_top), 3)

    # Dispatch across the remaining 11 refined layouts
    if canon_id == "F1-C":
        if not variant:
            variant = "quote_manifesto" if raw_code_upper == "S14" else ("quote_manifesto" if copy_z.get("quote") or copy_z.get("manifesto") else "big_number")
        stat_val = _first_non_empty_str(copy_z, "stat_value", "quote", "manifesto")
        stat_lbl = _first_non_empty_str(copy_z, "stat_label", "attribution")
        ctx_pts = copy_z.get("context_points")
        if ctx_pts is None:
            ctx_pts = copy_z.get("items") or ()
        if not stat_val and isinstance(ctx_pts, list) and ctx_pts:
            first_it = ctx_pts[0]
            rest_pts = list(ctx_pts[1:])
            if isinstance(first_it, dict):
                stat_val = _first_non_empty_str(first_it, "value", "stat", "quote", "lead", "title")
                used_lbl_key = None
                if not stat_lbl:
                    for lk in ("label", "subtitle", "body", "desc"):
                        cand_l = _first_non_empty_str(first_it, lk)
                        if cand_l:
                            stat_lbl = cand_l
                            used_lbl_key = lk
                            break
                # Preserve any remaining body/desc/detail so zero frozen copy is ever silently dropped
                rem_body = _first_non_empty_str(first_it, "body", "desc", "detail", "note", "text")
                if rem_body and rem_body != stat_val and rem_body != stat_lbl and used_lbl_key not in ("body", "desc"):
                    rest_pts.insert(0, {"lead": "", "body": rem_body})
            else:
                ld, bd = _parse_lead_body_item(first_it)
                stat_val = ld or bd
                if not stat_lbl and ld and bd:
                    stat_lbl = bd
                elif stat_lbl and ld and bd and bd != stat_lbl:
                    rest_pts.insert(0, {"lead": "", "body": bd})
            ctx_pts = rest_pts
        stat_pt = float(lay_z["stat_pt"]) if lay_z.get("stat_pt") is not None else 54.0
        draw_hero_stat_slide(
            slide,
            stat_value=stat_val,
            stat_label=stat_lbl,
            context_points=ctx_pts if isinstance(ctx_pts, (list, tuple)) else (),
            right_image_path=mat_png if variant != "quote_manifesto" else None,
            variant=variant,
            top=z2_top,
            height=z2_height,
            stat_pt=stat_pt,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )
        if mat_png and variant == "quote_manifesto":
            _place_overlay_picture(slide, mat_png, asset_info, default_behind=True)

    elif canon_id == "F2-A":
        cards = copy_z.get("cards") if isinstance(copy_z.get("cards"), list) else copy_z.get("items")
        cards_list = [_coerce_spec_block_dict(c) for c in cards] if isinstance(cards, list) else []
        card_style = variant or _first_non_empty_str(lay_z, "card_style")
        if not card_style:
            card_style = "borderless_centerline" if len(cards_list) == 2 else "minimal_column"
        width_ratios = lay_z.get("width_ratios") if isinstance(lay_z.get("width_ratios"), list) else None
        title_pt = float(lay_z["title_font_pt"]) if lay_z.get("title_font_pt") is not None else None
        draw_parallel_row_cards(
            slide,
            cards_spec=cards_list,
            top=z2_top,
            height=z2_height,
            spotlight_idx=spot_idx,
            body_font_pt=resolved_body_pt,
            title_font_pt=title_pt,
            width_ratios=width_ratios,
            card_style=card_style,
            tokens=tokens,
        )

    elif canon_id == "F2-B":
        rows = copy_z.get("rows") if isinstance(copy_z.get("rows"), list) else copy_z.get("items")
        rows_list = [_coerce_spec_block_dict(r) for r in rows] if isinstance(rows, list) else []
        left_ratio = float(lay_z.get("left_ratio", 0.28))  # type: ignore[arg-type]
        draw_editorial_split_rows_s8(
            slide,
            rows_spec=rows_list,
            left_ratio=left_ratio,
            spotlight_idx=spot_idx,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F2-C":
        pri = copy_z.get("primary_block")
        secs = copy_z.get("secondary_blocks")
        if pri is None and isinstance(copy_z.get("items"), list) and copy_z["items"]:
            pri = copy_z["items"][0]
            secs = copy_z["items"][1:]
        pri_dict = _coerce_spec_block_dict(pri)
        sec_list = [_coerce_spec_block_dict(sb) for sb in (secs if isinstance(secs, list) else [])]
        eff_spot = 0 if ("spotlight_idx" not in lay_z) else spot_idx
        draw_bento_grid_slide(
            slide,
            primary_block=pri_dict,
            secondary_blocks=sec_list,
            spotlight_idx=eff_spot,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F3-A":
        steps = copy_z.get("steps") if isinstance(copy_z.get("steps"), list) else copy_z.get("items")
        steps_list = [_coerce_spec_block_dict(st) for st in steps] if isinstance(steps, list) else []
        lay_style = variant or _first_non_empty_str(lay_z, "layout_style")
        if not lay_style:
            lay_style = "staggered_timeline" if raw_code_upper == "S12" else "auto"
        draw_process_steps_s3(
            slide,
            steps_spec=steps_list,
            layout_style=lay_style,
            top=z2_top,
            height=z2_height,
            spotlight_idx=spot_idx,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F3-B":
        nodes = copy_z.get("nodes") if isinstance(copy_z.get("nodes"), list) else copy_z.get("items")
        nodes_list = [_coerce_spec_block_dict(nd) for nd in nodes] if isinstance(nodes, list) else []
        edges = copy_z.get("edges") if isinstance(copy_z.get("edges"), list) else lay_z.get("edges")
        valid_topos = {"horizontal_chain", "cycle_loop", "hub_spoke", "custom"}
        topo = _first_non_empty_str(lay_z, "topology") or (variant if variant in valid_topos else "horizontal_chain")
        c_pos = _first_non_empty_str(lay_z, "callout_position", default="right")
        v_ratio = float(lay_z.get("visual_ratio", 0.64))  # type: ignore[arg-type]
        draw_clean_mechanism_s4(
            slide,
            nodes_spec=nodes_list,
            edges_spec=edges if isinstance(edges, list) else None,
            topology=topo,
            callouts=copy_z.get("callouts") if isinstance(copy_z.get("callouts"), list) else None,
            callout_position=c_pos,
            callout_heading=_first_non_empty_str(copy_z, "callout_heading") or None,
            visual_ratio=v_ratio,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F4-A":
        quads = copy_z.get("quadrants") if isinstance(copy_z.get("quadrants"), list) else copy_z.get("items")
        quads_list = [_coerce_spec_block_dict(q) for q in quads] if isinstance(quads, list) else []
        if lay_z.get("borderless") is not None:
            borderless = bool(lay_z["borderless"])
        else:
            borderless = variant not in ("boxed", "clean_card")
        eff_spot = 1 if ("spotlight_idx" not in lay_z) else spot_idx
        draw_quadrant_matrix_s5(
            slide,
            quadrants_spec=quads_list,
            x_axis_label=_first_non_empty_str(copy_z, "x_axis_label"),
            y_axis_label=_first_non_empty_str(copy_z, "y_axis_label"),
            spotlight_idx=eff_spot,
            borderless=borderless,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F4-B":
        tbl = copy_z.get("table") if isinstance(copy_z.get("table"), dict) else {}
        hdrs = copy_z.get("headers") or tbl.get("headers")
        rows = copy_z.get("rows") or tbl.get("rows")
        if hdrs is None and isinstance(copy_z.get("items"), list) and copy_z["items"]:
            first_row = copy_z["items"][0]
            if isinstance(first_row, dict):
                hdrs = list(first_row.keys())
                rows = [[r.get(k, "") if isinstance(r, dict) else "" for k in hdrs] for r in copy_z["items"]]
        spot_col = lay_z.get("spotlight_col")
        if spot_col is not None:
            spot_col = int(spot_col)  # type: ignore[arg-type]
        elif spot_idx is not None:
            spot_col = spot_idx
        col_widths = lay_z.get("col_widths") if isinstance(lay_z.get("col_widths"), list) else None
        draw_comparison_table_slide(
            slide,
            headers=list(hdrs) if isinstance(hdrs, list) else [],
            rows=list(rows) if isinstance(rows, list) else [],
            spotlight_col=spot_col,
            col_widths=col_widths,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F5-A":
        valid_pos = {"right", "left", "top", "bottom", "header_only"}
        legacy_pos_map = {"S7-A": "right", "S7-B": "bottom", "S7-C": "top", "S7-D": "header_only"}
        c_pos = _first_non_empty_str(lay_z, "callout_position").lower()
        if c_pos not in valid_pos:
            if variant in valid_pos:
                c_pos = variant
            else:
                c_pos = legacy_pos_map.get(raw_code_upper, "right")
        callouts = copy_z.get("callouts") if isinstance(copy_z.get("callouts"), list) else copy_z.get("items")
        v_ratio = float(lay_z.get("visual_ratio", 0.65))  # type: ignore[arg-type]
        v_cap = _first_non_empty_str(copy_z, "visual_caption", "caption", "source") or None
        c_head = _first_non_empty_str(copy_z, "callout_heading") or None
        eff_spot = 0 if ("spotlight_idx" not in lay_z) else spot_idx
        draw_visual_callout_slide(
            slide,
            image_path=mat_png,
            callout_position=c_pos,
            callouts=callouts if isinstance(callouts, list) else None,
            visual_ratio=v_ratio,
            visual_caption=v_cap,
            callout_heading=c_head,
            body_font_pt=resolved_body_pt,
            top=z2_top,
            height=z2_height,
            spotlight_idx=eff_spot,
            tokens=tokens,
        )

    elif canon_id == "F5-B":
        kpis = copy_z.get("kpi_items") or copy_z.get("kpis")
        insights = copy_z.get("insight_blocks") or copy_z.get("insights")
        if kpis is None and isinstance(copy_z.get("items"), dict):
            kpis = copy_z["items"].get("kpi_items") or copy_z["items"].get("kpis")  # type: ignore[union-attr]
            insights = insights or copy_z["items"].get("insight_blocks") or copy_z["items"].get("insights")  # type: ignore[union-attr]
        elif kpis is not None and insights is None and isinstance(copy_z.get("items"), list):
            insights = copy_z["items"]
        elif kpis is None and isinstance(copy_z.get("items"), list):
            kpis = copy_z["items"]
        eff_spot = 0 if ("spotlight_idx" not in lay_z) else spot_idx
        draw_kpi_strip_slide(
            slide,
            kpi_items=[_coerce_kpi_item_dict(k) for k in kpis] if isinstance(kpis, list) else [],
            insight_blocks=list(insights) if isinstance(insights, list) else (),
            spotlight_idx=eff_spot,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F5-C":
        f_title = _first_non_empty_str(copy_z, "focal_title")
        f_formula = _first_non_empty_str(copy_z, "focal_formula", "formula")
        f_note = _first_non_empty_str(copy_z, "focal_note")
        b_items = copy_z.get("breakdown_items") if isinstance(copy_z.get("breakdown_items"), list) else copy_z.get("items")
        f_mode = _first_non_empty_str(lay_z, "mode").lower()
        if f_mode not in ("left_right", "top_bottom"):
            f_mode = variant if variant in ("left_right", "top_bottom") else "left_right"
        f_ratio = float(lay_z.get("focal_ratio", 0.38))  # type: ignore[arg-type]
        use_omml = bool(lay_z.get("use_omml")) if ("use_omml" in lay_z) else bool(copy_z.get("use_omml", False))
        draw_focal_anatomy_s6(
            slide,
            focal_title=f_title,
            focal_formula=f_formula,
            focal_note=f_note,
            breakdown_items=list(b_items) if isinstance(b_items, list) else (),
            mode=f_mode,
            focal_ratio=f_ratio,
            use_omml=use_omml,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    else:
        raise ValueError(
            f"Unsupported layout family_id '{raw_code_upper}' (canonical='{canon_id}') on Slide #{slide_idx}. "
            "Expected one of F1-A..F5-C (or legacy S0..S14 / Hero Stat)."
        )

    # Optional Mode 3 Tier 2/3 overlay on non-image slides when explicitly supplied
    if mat_png and canon_id not in ("F1-A", "F1-B", "F1-C", "F5-A"):
        _place_overlay_picture(slide, mat_png, asset_info, default_behind=False)

    _apply_tier1_geometric_accent(slide, lay_z, tokens)
    if speaker_notes:
        add_speaker_notes(slide, speaker_notes)


def render_deck_from_spec(
    spec_json_or_path: dict[str, object] | str | Path,
    output_pptx_path: str | Path,
    *,
    validate_sequence: bool = True,
    require_bookends: bool = True,
    min_distinct: int = 5,
    max_boxed_ratio: float = 0.40,
    max_family_ratio: float = 0.40,
    asset_base_dir: str | Path | None = None,
    strict_fidelity: bool = False,
) -> str:
    """
    [Step 4B] Deterministically render a `.pptx` deck from a locked `02c_slide_spec_lock.json`:
    - Strictly READ-ONLY on `slides[i].copy` (deep-copied at entry + canonical JSON fingerprint asserted post-render).
    - Resolves unified DISCAS / dynamic CIELAB tokens via `build_slide_design_tokens()`.
    - Automatically runs `validate_layout_sequence()` when `validate_sequence=True`.
    - Dispatches all 5 layout families / 13 refined layouts (`F1-A`..`F5-C`) plus Mode 3 `Tier 1/2/3` and OMML.
    - Cleans up any ephemeral Tier 3 SVG/HTML PNG temp files automatically.
    Returns absolute resolved path string of `output_pptx_path`.
    """
    spec, spec_parent = _load_spec_lock(spec_json_or_path)
    slides = _validate_spec_lock_structure(spec, require_layout=True)

    # Code-level Read-Only Copy Guardrail: freeze canonical JSON snapshot of every slide's copy zone
    copy_snapshot_before = json.dumps([s["copy"] for s in slides], ensure_ascii=False, sort_keys=True)

    if validate_sequence:
        layout_seq = [s["layout"] for s in slides]
        validate_layout_sequence(
            layout_seq,
            require_bookends=require_bookends,
            min_distinct=min_distinct,
            max_boxed_ratio=max_boxed_ratio,
            max_family_ratio=max_family_ratio,
        )

    tokens = _resolve_spec_design_tokens(spec)
    base_dir = Path(asset_base_dir).resolve() if asset_base_dir is not None else spec_parent

    prs = create_widescreen_presentation()
    temp_files: list[Path] = []
    out_path = Path(output_pptx_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        for idx, sl in enumerate(slides, start=1):
            _render_single_spec_slide(prs, sl, idx, tokens, base_dir, temp_files)

        # Runtime assertion proving `slides[i].copy` was never modified during deterministic rendering
        copy_snapshot_after = json.dumps([s["copy"] for s in slides], ensure_ascii=False, sort_keys=True)
        if copy_snapshot_after != copy_snapshot_before:
            raise RuntimeError("Read-Only Copy Fidelity Guardrail violated: slides[i].copy mutated during render.")

        prs.save(str(out_path))
    finally:
        for tmp_p in temp_files:
            with suppress(OSError):
                tmp_p.unlink(missing_ok=True)

    if strict_fidelity:
        report = check_copy_fidelity(spec, out_path)
        if not report["passed"]:
            raise ValueError(f"Copy fidelity verification failed: {report['summary']}")

    return str(out_path)


def _normalize_ws(text: str) -> str:
    """Collapse internal whitespace cleanly for robust line-wrap-invariant comparison."""
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _extract_numeric_tokens(text: str) -> list[str]:
    """Extract normalized key numeric tokens (percentages, currencies, years, decimals, integers) from text."""
    clean = _strip_inline_bold(str(text or ""))
    tokens: list[str] = []
    for m in _FIDELITY_NUM_TOKEN_RE.finditer(clean):
        tok = m.group(0).replace("％", "%").strip()
        if tok:
            tokens.append(tok)
    return tokens


def _match_numeric_phrase_in_text(phrase: str, haystack: str) -> bool:
    """
    Check whether a key numeric phrase (e.g. `'70%'`, `'5.81 億英鎊'`, `'2026'`, `'$1,200'`) appears
    intact in `haystack` with strict numeric digit, comma-group, and unary-sign boundaries so:
    - `'20%'` never matches `'120%'`
    - `'100'` never matches `'1,100'` or `'100,000'` (while still matching `'100, 200'`)
    - `'15%'` never matches `'-15%'` or `'+15%'` (while `'2026'` still matches `'2020-2026'`)
    """
    clean_p = _normalize_ws(phrase).replace("％", "%")
    clean_h = _normalize_ws(haystack).replace("％", "%")
    if not clean_p:
        return True
    parts = clean_p.split(" ")
    pat = r"\s*".join(re.escape(pt) for pt in parts)
    if clean_p[0].isdigit():
        pat = r"(?<!\d,)(?<![0-9.])(?<!(?<![0-9])[+-])" + pat
    if clean_p[-1].isdigit():
        pat = pat + r"(?![0-9.]|,\d{3})"
    return re.search(pat, clean_h) is not None


def _extract_slide_rendered_texts(slide) -> dict[str, object]:
    """
    Extract all rendered text from a PowerPoint slide:
    - standard text frames (including recursive GroupShapes)
    - native Table cells (`F4-B`)
    - native OMML `<m:oMath>` `<m:t>` math runs AND `<mc:Fallback>` `<a:t>` runs (`F5-C`)
    - speaker notes text
    """
    visible_chunks: list[str] = []
    omml_math_chunks: list[str] = []
    omml_fallback_chunks: list[str] = []

    a_ns = _OMML_A_NS
    m_ns = _OMML_M_NS
    mc_ns = _OMML_MC_NS

    def _collect_text_frame(tf) -> None:
        for para in tf.paragraphs:
            p_el = para._p
            # Standard direct <a:r><a:t> runs (excludes <mc:AlternateContent>)
            direct_runs: list[str] = []
            for child in p_el:
                if child.tag == f"{{{a_ns}}}r":
                    t_el = child.find(f"{{{a_ns}}}t")
                    if t_el is not None and t_el.text:
                        direct_runs.append(t_el.text)
                elif child.tag == f"{{{a_ns}}}fld":
                    t_el = child.find(f"{{{a_ns}}}t")
                    if t_el is not None and t_el.text:
                        direct_runs.append(t_el.text)
                elif child.tag == f"{{{mc_ns}}}AlternateContent":
                    # Extract both native OMML <m:t> and <mc:Fallback> <a:t>
                    math_ts = [el.text for el in child.findall(f".//{{{m_ns}}}t") if el.text]
                    if math_ts:
                        omml_math_chunks.append("".join(math_ts))
                    fb_el = child.find(f"{{{mc_ns}}}Fallback")
                    if fb_el is not None:
                        fb_ts = [el.text for el in fb_el.findall(f".//{{{a_ns}}}t") if el.text]
                        if fb_ts:
                            omml_fallback_chunks.append("".join(fb_ts))
            line_txt = "".join(direct_runs)
            if line_txt.strip():
                visible_chunks.append(line_txt)

    def _walk_shapes(shapes) -> None:
        for shp in shapes:
            if getattr(shp, "has_text_frame", False):
                _collect_text_frame(shp.text_frame)
            if getattr(shp, "has_table", False):
                for row in shp.table.rows:
                    for cell in row.cells:
                        _collect_text_frame(cell.text_frame)
            if hasattr(shp, "shapes"):
                with suppress(Exception):
                    _walk_shapes(shp.shapes)

    _walk_shapes(slide.shapes)

    notes_text = ""
    with suppress(Exception):
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None:
            notes_text = str(slide.notes_slide.notes_text_frame.text or "")

    visible_joined = "\n".join(visible_chunks)
    # `primary_chunks` avoids double-counting OMML `<m:t>` + `<mc:Fallback>` `<a:t>` for multiset numeric verification
    primary_chunks = visible_chunks + (omml_math_chunks if omml_math_chunks else omml_fallback_chunks)
    combined_for_match = "\n".join(visible_chunks + omml_math_chunks + omml_fallback_chunks)
    return {
        "visible_text": visible_joined,
        "omml_math_text": "\n".join(omml_math_chunks),
        "omml_fallback_text": "\n".join(omml_fallback_chunks),
        "primary_text": "\n".join(primary_chunks),
        "combined_text": combined_for_match,
        "notes_text": notes_text,
    }


def _collect_expected_copy_segments(
    copy_zone: dict[str, object],
    layout_zone: dict[str, object],
    canonical_id: str,
) -> tuple[list[str], str | None]:
    """
    Collect all frozen visible text segments expected on the rendered slide (plus optional `omml_formula`
    for dual math-run numeric verification) from `slides[i].copy`, respecting `layout.include_zone3`.
    """
    segments: list[str] = []
    omml_formula: str | None = None
    variant = str(_normalize_layout_entry(layout_zone).get("variant") or "").strip().lower()
    use_zone3 = _should_render_zone3(copy_zone, layout_zone, canonical_id)

    def _add_str(raw: object, *, split_lead_body: bool = False) -> None:
        if raw is None or isinstance(raw, bool):
            return
        s = str(raw).strip()
        if not s:
            return
        for hard_line in s.splitlines():
            hl = hard_line.strip()
            if not hl:
                continue
            if split_lead_body:
                m = _LEAD_BODY_SPLIT_RE.match(hl)
                if m:
                    segments.append(_strip_inline_bold(m.group(1).strip()))
                    segments.append(_strip_inline_bold(m.group(2).strip()))
                    continue
            segments.append(_strip_inline_bold(hl))

    def _add_item_obj(obj: object, *, is_minimal_col_card: bool = False) -> None:
        if obj is None or isinstance(obj, bool):
            return
        if isinstance(obj, str):
            if is_minimal_col_card:
                ld, bd = _parse_lead_body_item(obj)
                title_part = ld or bd
                body_part = bd if ld else ""
                if title_part:
                    m_sn = re.match(r"^\s*(0?\d{1,2})(?:[\.\)、:：\-—–\|｜\s]+)(.+)$", title_part)
                    if m_sn and _LEADING_INDEX_PREFIX_RE.match(title_part):
                        _add_str(m_sn.group(1))
                        _add_str(m_sn.group(2))
                    else:
                        _add_str(title_part)
                    if body_part:
                        _add_str(body_part, split_lead_body=True)
                    return
            _add_str(obj, split_lead_body=True)
            return
        if isinstance(obj, (list, tuple)):
            for sub in obj:
                _add_item_obj(sub)
            return
        if isinstance(obj, dict):
            # Text keys only (explicitly skips styling/geometry keys like accent/bg/dark/is_spotlight/rx/ry/rw/rh)
            scalar_keys = (
                "kicker", "badge", "step", "num", "phase", "date", "index",
                "title", "heading", "label", "name", "category",
                "subtitle", "sub", "value", "stat", "metric", "number", "kpi", "delta",
                "lead", "body", "detail", "desc", "text", "content", "note", "caption",
            )
            for k in scalar_keys:
                val = obj.get(k)
                if val is None or isinstance(val, (bool, list, tuple, dict)):
                    continue
                s = str(val).strip()
                if not s:
                    continue
                # Handle F2-A minimal_column leading numeral extraction ("01. Title" -> "01" + "Title")
                if is_minimal_col_card and k in ("title", "heading", "label", "name"):
                    m_sn = re.match(r"^\s*(0?\d{1,2})(?:[\.\)、:：\-—–\|｜\s]+)(.+)$", s)
                    if m_sn and _LEADING_INDEX_PREFIX_RE.match(s):
                        _add_str(m_sn.group(1))
                        _add_str(m_sn.group(2))
                        continue
                _add_str(s, split_lead_body=(k in ("body", "detail", "desc", "text", "content", "note")))
            for ck in ("rows", "items", "points", "bullets"):
                sub_coll = obj.get(ck)
                if isinstance(sub_coll, (list, tuple)):
                    for entry in sub_coll:
                        _add_item_obj(entry)

    # Top-level fields by family
    if canonical_id == "F1-A":
        _add_str(_first_non_empty_str(copy_zone, "badge_text", "chapter_pill"))
        _add_str(_first_non_empty_str(copy_zone, "headline", "main_title", "title"))
        _add_str(_first_non_empty_str(copy_zone, "subtitle"))
        for card in (copy_zone.get("kpi_cards") or copy_zone.get("items") or []):
            _add_item_obj(card)
        if use_zone3:
            _add_str(_first_non_empty_str(copy_zone, "footer_text", "zone3_takeaway"))
        return segments, None

    if canonical_id == "F1-B":
        sec_num = _first_non_empty_str(copy_zone, "section_num", "chapter_pill")
        if sec_num:
            _add_str(f"{int(sec_num):02d}" if sec_num.isdigit() else sec_num)
        _add_str(_first_non_empty_str(copy_zone, "section_title", "headline", "title"))
        _add_str(_first_non_empty_str(copy_zone, "subtitle"))
        if use_zone3:
            _add_str(_first_non_empty_str(copy_zone, "zone3_takeaway"))
        return segments, None

    # Zone 1 shared fields for F1-C .. F5-C
    _add_str(_first_non_empty_str(copy_zone, "chapter_pill", "badge_text"))
    _add_str(_first_non_empty_str(copy_zone, "right_badge"))
    _add_str(_first_non_empty_str(copy_zone, "headline", "title"))
    _add_str(_first_non_empty_str(copy_zone, "subtitle"))

    # Family-specific Zone 2 copy fields
    if canonical_id == "F1-C":
        _add_str(_first_non_empty_str(copy_zone, "stat_value", "quote", "manifesto"))
        _add_str(_first_non_empty_str(copy_zone, "stat_label", "attribution"))
        pts = copy_zone.get("context_points") if copy_zone.get("context_points") is not None else copy_zone.get("items")
        if isinstance(pts, list):
            for it in pts:
                _add_item_obj(it)
    elif canonical_id == "F2-A":
        cards = copy_zone.get("cards") if isinstance(copy_zone.get("cards"), list) else copy_z_items(copy_zone)
        is_min_col = (variant == "minimal_column") or (not variant and len(cards) != 2)
        for c in cards:
            _add_item_obj(c, is_minimal_col_card=is_min_col)
    elif canonical_id == "F2-B":
        for r in (copy_zone.get("rows") if isinstance(copy_zone.get("rows"), list) else copy_z_items(copy_zone)):
            _add_item_obj(r)
    elif canonical_id == "F2-C":
        if copy_zone.get("primary_block") is not None:
            _add_item_obj(copy_zone.get("primary_block"))
            for sb in (copy_zone.get("secondary_blocks") or []):
                _add_item_obj(sb)
        else:
            for it in copy_z_items(copy_zone):
                _add_item_obj(it)
    elif canonical_id == "F3-A":
        for st in (copy_zone.get("steps") if isinstance(copy_zone.get("steps"), list) else copy_z_items(copy_zone)):
            _add_item_obj(st)
    elif canonical_id == "F3-B":
        for nd in (copy_zone.get("nodes") if isinstance(copy_zone.get("nodes"), list) else copy_z_items(copy_zone)):
            _add_item_obj(nd)
        _add_str(_first_non_empty_str(copy_zone, "callout_heading"))
        for co in (copy_zone.get("callouts") or []):
            _add_item_obj(co)
    elif canonical_id == "F4-A":
        _add_str(_first_non_empty_str(copy_zone, "x_axis_label"))
        _add_str(_first_non_empty_str(copy_zone, "y_axis_label"))
        for q in (copy_zone.get("quadrants") if isinstance(copy_zone.get("quadrants"), list) else copy_z_items(copy_zone)):
            _add_item_obj(q)
    elif canonical_id == "F4-B":
        tbl = copy_zone.get("table") if isinstance(copy_zone.get("table"), dict) else {}
        hdrs = copy_zone.get("headers") or tbl.get("headers")
        rows = copy_zone.get("rows") or tbl.get("rows")
        if hdrs is None and isinstance(copy_zone.get("items"), list) and copy_zone["items"] and isinstance(copy_zone["items"][0], dict):
            hdrs = list(copy_zone["items"][0].keys())
            rows = [[r.get(k, "") if isinstance(r, dict) else "" for k in hdrs] for r in copy_zone["items"]]
        for h in (hdrs or []):
            _add_str(h)
        for r in (rows or []):
            if isinstance(r, (list, tuple)):
                for cell_val in r:
                    _add_str(cell_val)
            else:
                _add_str(r)
    elif canonical_id == "F5-A":
        _add_str(_first_non_empty_str(copy_zone, "callout_heading"))
        for co in (copy_zone.get("callouts") if isinstance(copy_zone.get("callouts"), list) else copy_z_items(copy_zone)):
            _add_item_obj(co)
        _add_str(_first_non_empty_str(copy_zone, "visual_caption", "caption", "source"))
    elif canonical_id == "F5-B":
        kpis = copy_zone.get("kpi_items") or copy_zone.get("kpis")
        insights = copy_zone.get("insight_blocks") or copy_zone.get("insights")
        if kpis is None and isinstance(copy_zone.get("items"), dict):
            kpis = copy_zone["items"].get("kpi_items") or copy_zone["items"].get("kpis")  # type: ignore[union-attr]
            insights = insights or copy_zone["items"].get("insight_blocks") or copy_zone["items"].get("insights")  # type: ignore[union-attr]
        elif kpis is not None and insights is None and isinstance(copy_zone.get("items"), list):
            insights = copy_zone["items"]
        elif kpis is None and isinstance(copy_zone.get("items"), list):
            kpis = copy_zone["items"]
        for k in (kpis or []):
            _add_item_obj(k)
        for ins in (insights or []):
            _add_item_obj(ins)
    elif canonical_id == "F5-C":
        _add_str(_first_non_empty_str(copy_zone, "focal_title"))
        raw_formula = _first_non_empty_str(copy_zone, "focal_formula", "formula")
        use_omml = bool(layout_zone.get("use_omml")) if ("use_omml" in layout_zone) else bool(copy_zone.get("use_omml", False))
        if raw_formula:
            clean_formula = raw_formula.replace("$$", "").replace("$", "").strip()
            _add_str(clean_formula)
            if use_omml:
                omml_formula = clean_formula
        _add_str(_first_non_empty_str(copy_zone, "focal_note"))
        for bd in (copy_zone.get("breakdown_items") if isinstance(copy_zone.get("breakdown_items"), list) else copy_z_items(copy_zone)):
            _add_item_obj(bd)
    else:
        # Layout-agnostic fallback (e.g., Step 3 spec prior to Step 4A layout locking): never silently skip frozen copy
        for fk in ("stat_value", "quote", "manifesto", "stat_label", "attribution", "callout_heading", "visual_caption", "caption", "source", "x_axis_label", "y_axis_label", "focal_title", "focal_formula", "formula", "focal_note"):
            _add_str(_first_non_empty_str(copy_zone, fk))
        if copy_zone.get("primary_block") is not None:
            _add_item_obj(copy_zone.get("primary_block"))
        for ck in ("items", "cards", "rows", "steps", "nodes", "quadrants", "callouts", "kpi_items", "kpis", "insight_blocks", "insights", "breakdown_items", "context_points", "secondary_blocks", "kpi_cards"):
            coll = copy_zone.get(ck)
            if isinstance(coll, list):
                for entry in coll:
                    _add_item_obj(entry)

    if use_zone3:
        _add_str(_first_non_empty_str(copy_zone, "zone3_takeaway"))

    return segments, omml_formula


def copy_z_items(copy_zone: dict[str, object]) -> list[object]:
    """Return `copy_zone['items']` as a list when present, else an empty list."""
    raw = copy_zone.get("items")
    return list(raw) if isinstance(raw, list) else []


def check_copy_fidelity(
    spec_json_or_path: dict[str, object] | str | Path,
    pptx_path: str | Path,
) -> dict[str, object]:
    """
    [Step 4B] Cross-check rendered `.pptx` text (shapes, GroupShapes, native tables, OMML math,
    and speaker notes) against the frozen `slides[i].copy` zone of `02c_slide_spec_lock.json`:
    - Verifies slide count match.
    - Guarantees 100% presence of every frozen `copy` text segment (no silent deletion or truncation).
    - Guarantees zero unparsed Markdown `**` and zero draft placeholders (`TBD` / `TODO` / `FIXME`).
    - Guarantees 100% verbatim numeric fidelity for both explicit `copy.key_numbers` and all
      auto-extracted percentages / currencies / years / values across every slide.
    - Verifies `copy.speaker_notes` preservation.
    Returns structured report dict with `passed: bool`, `errors`, `warnings`, `slides`, and `summary`.
    """
    spec, _base_dir = _load_spec_lock(spec_json_or_path)
    slides_spec = _validate_spec_lock_structure(spec, require_layout=False)

    pptx_file = Path(pptx_path).resolve()
    if not pptx_file.exists() or not pptx_file.is_file():
        raise FileNotFoundError(f"PPTX file not found for copy fidelity check: {pptx_file}")

    prs = Presentation(str(pptx_file))
    spec_n = len(slides_spec)
    pptx_n = len(prs.slides)

    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    per_slide_reports: list[dict[str, object]] = []
    total_expected_segments = 0
    total_expected_numbers = 0

    if spec_n != pptx_n:
        errors.append({
            "slide": 0,
            "type": "slide_count_mismatch",
            "detail": f"Spec defines {spec_n} slides, but PPTX contains {pptx_n} slides.",
        })

    n_check = min(spec_n, pptx_n)
    for idx in range(n_check):
        slide_num = idx + 1
        sl_spec = slides_spec[idx]
        copy_z: dict[str, object] = sl_spec["copy"]  # type: ignore[assignment]
        lay_z: dict[str, object] = sl_spec.get("layout") if isinstance(sl_spec.get("layout"), dict) else {}  # type: ignore[assignment]
        canon_id = str(_normalize_layout_entry(lay_z)["canonical_id"]) if lay_z else ""

        extracted = _extract_slide_rendered_texts(prs.slides[idx])
        vis_raw = str(extracted["visible_text"])
        omml_math_raw = str(extracted["omml_math_text"])
        primary_raw = str(extracted["primary_text"])
        combined_raw = str(extracted["combined_text"])
        notes_raw = str(extracted["notes_text"])

        combined_norm = _normalize_ws(combined_raw)
        combined_nospace = re.sub(r"\s+", "", combined_norm)

        slide_errors: list[dict[str, object]] = []
        missing_segments: list[str] = []
        missing_key_numbers: list[str] = []
        missing_numeric_tokens: list[str] = []
        residual_markdown: list[str] = []
        draft_placeholders: list[str] = []

        # 1. Zero residual Markdown `**` on rendered slide surface
        if "**" in vis_raw or "**" in omml_math_raw:
            residual_markdown.append("**")
            slide_errors.append({
                "slide": slide_num,
                "type": "residual_markdown",
                "detail": f"Slide {slide_num} contains unparsed Markdown '**' on screen.",
            })

        # 2. Zero draft placeholders (`TBD` / `TODO` / `FIXME`) on screen or speaker notes
        for m in _DRAFT_PLACEHOLDER_RE.finditer(combined_raw + "\n" + notes_raw):
            tok = m.group(0)
            if tok not in draft_placeholders:
                draft_placeholders.append(tok)
        if draft_placeholders:
            slide_errors.append({
                "slide": slide_num,
                "type": "draft_placeholder",
                "detail": f"Slide {slide_num} contains draft placeholder(s): {draft_placeholders}.",
                "tokens": draft_placeholders,
            })

        # 3. Verify every frozen visible copy segment is present verbatim (whitespace-normalized)
        expected_segments, omml_formula = _collect_expected_copy_segments(copy_z, lay_z, canon_id)
        total_expected_segments += len(expected_segments)

        for seg in expected_segments:
            seg_norm = _normalize_ws(seg)
            if not seg_norm:
                continue
            seg_nospace = re.sub(r"\s+", "", seg_norm)
            if (seg_norm not in combined_norm) and (seg_nospace not in combined_nospace):
                missing_segments.append(seg_norm)

        if missing_segments:
            slide_errors.append({
                "slide": slide_num,
                "type": "missing_copy_segment",
                "detail": f"Slide {slide_num} missing {len(missing_segments)} frozen copy segment(s): {missing_segments[:5]}",
                "missing": missing_segments,
            })

        # 4. Verify explicit `copy.key_numbers` with strict numeric digit boundaries
        raw_key_nums = copy_z.get("key_numbers")
        if isinstance(raw_key_nums, list):
            for kn in raw_key_nums:
                kn_s = str(kn or "").strip()
                if not kn_s:
                    continue
                total_expected_numbers += 1
                if not _match_numeric_phrase_in_text(kn_s, combined_raw):
                    missing_key_numbers.append(kn_s)
        if missing_key_numbers:
            slide_errors.append({
                "slide": slide_num,
                "type": "missing_key_number",
                "detail": f"Slide {slide_num} missing frozen key_numbers: {missing_key_numbers}.",
                "missing": missing_key_numbers,
            })

        # 5. Verify multiset fidelity of ALL auto-extracted numeric tokens across frozen copy
        # Uses `primary_raw` (visible + OMML `<m:t>` only, excluding duplicate `<mc:Fallback>`) so OMML
        # numbers are counted once and can never mask a deleted duplicate elsewhere on the slide.
        expected_num_counter: Counter[str] = Counter()
        for seg in expected_segments:
            expected_num_counter.update(_extract_numeric_tokens(seg))
        actual_num_counter: Counter[str] = Counter(_extract_numeric_tokens(primary_raw))
        total_expected_numbers += sum(expected_num_counter.values())

        for num_tok, exp_cnt in expected_num_counter.items():
            act_cnt = actual_num_counter.get(num_tok, 0)
            if act_cnt < exp_cnt:
                missing_numeric_tokens.append(f"{num_tok} (expected {exp_cnt}, found {act_cnt})")

        # Extra check for OMML `<m:oMath>` math runs so tampering or stripping `<m:oMath>` cannot hide behind `<mc:Fallback>`
        if omml_formula:
            if not omml_math_raw.strip():
                slide_errors.append({
                    "slide": slide_num,
                    "type": "missing_omml_math",
                    "detail": f"Slide {slide_num} expects native OMML equation ('{omml_formula}') but no <m:oMath> runs were found.",
                })
            else:
                exp_math_nums = Counter(_extract_numeric_tokens(omml_formula))
                act_math_nums = Counter(_extract_numeric_tokens(omml_math_raw))
                for num_tok, exp_cnt in exp_math_nums.items():
                    act_cnt = act_math_nums.get(num_tok, 0)
                    if act_cnt < exp_cnt:
                        missing_numeric_tokens.append(f"OMML:{num_tok} (expected {exp_cnt}, found {act_cnt})")

        if missing_numeric_tokens:
            slide_errors.append({
                "slide": slide_num,
                "type": "missing_numeric_token",
                "detail": f"Slide {slide_num} numeric fidelity mismatch: {missing_numeric_tokens}.",
                "missing": missing_numeric_tokens,
            })

        # 6. Verify `copy.speaker_notes` fidelity when defined in frozen copy
        expected_notes = _first_non_empty_str(copy_z, "speaker_notes")
        speaker_notes_ok = True
        if expected_notes:
            exp_notes_norm = _normalize_ws(expected_notes)
            act_notes_norm = _normalize_ws(notes_raw)
            if exp_notes_norm not in act_notes_norm:
                speaker_notes_ok = False
                slide_errors.append({
                    "slide": slide_num,
                    "type": "speaker_notes_mismatch",
                    "detail": f"Slide {slide_num} speaker notes missing or altered relative to frozen copy.",
                })

        errors.extend(slide_errors)
        per_slide_reports.append({
            "slide": slide_num,
            "family_id": canon_id,
            "passed": len(slide_errors) == 0,
            "expected_segments": len(expected_segments),
            "missing_segments": missing_segments,
            "missing_key_numbers": missing_key_numbers,
            "missing_numeric_tokens": missing_numeric_tokens,
            "residual_markdown": residual_markdown,
            "draft_placeholders": draft_placeholders,
            "speaker_notes_ok": speaker_notes_ok,
        })

    passed = len(errors) == 0
    summary = (
        f"PASSED: {n_check}/{spec_n} slides verified (100% copy & numeric fidelity, 0 errors)."
        if passed
        else f"FAILED: {len(errors)} copy/numeric fidelity error(s) detected across {n_check}/{spec_n} slides."
    )

    return {
        "passed": passed,
        "spec_slide_count": spec_n,
        "pptx_slide_count": pptx_n,
        "checked_slides": n_check,
        "total_expected_segments": total_expected_segments,
        "total_expected_numbers": total_expected_numbers,
        "errors": errors,
        "warnings": warnings,
        "slides": per_slide_reports,
        "summary": summary,
    }
