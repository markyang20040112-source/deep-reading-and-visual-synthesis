"""
pptx_engine/tokens.py
Theme loading, DISCAS typography scale, design token factory, and low-level OOXML shape helpers.
Note: `pptx_slide_engine` is the public entry point.
"""

import functools
import json
import math
import re
import struct
from contextlib import suppress
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

FONT_FAMILY = "Microsoft JhengHei"


MIN_CONTENT_FONT_PT = 12.0


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
        prefs_file = Path(__file__).resolve().parents[2] / "config" / "user_preferences.json"
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

    # Piecewise linear anchor points (body_pt, headline_pt) matching formats/format_c_slides/02_build.md
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
        scripts_dir = str(Path(__file__).resolve().parents[1])
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


def _get_slide_height_in(slide, default_h: float = 7.50) -> float:
    """Safely read actual slide canvas height in inches (supports non-16:9 custom slide dimensions)."""
    emu_per_in = 914400.0
    with suppress(AttributeError, TypeError, ValueError):
        sh_emu = slide.part.package.presentation_part.presentation.slide_height
        if sh_emu and float(sh_emu) > 0:
            return round(float(sh_emu) / emu_per_in, 3)
    return float(default_h)


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
