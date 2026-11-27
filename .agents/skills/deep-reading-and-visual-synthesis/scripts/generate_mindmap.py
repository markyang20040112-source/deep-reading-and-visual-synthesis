"""
generate_mindmap.py
Scientific Visual Knowledge Diagram & Concept Map Engine (Matplotlib Vector Renderer).

Grounded in empirical design & cognitive science studies:
- Cowan (2001) & Palmer (1992, 1999): 4±1 Per-Level Hierarchical Chunking (4 Macro Zones -> 2-3 Cards -> 2-3 Bullets)
- Goldstone & Son (2005), Clark & Haviland (1977), Mayer (2009): Concreteness Fading & Plain-Language Progressive Disclosure
- Reber, Schwarz, & Winkielman (2004): Processing Fluency Theory of Aesthetic Pleasure
- Müller-Brockmann (1981) & W3C Box Alignment: Swiss Grid, Modular Row Slots, & True Vertical Centering (va='center')
- Bringhurst (2012) & W3C CLREQ: High-Legibility CJK Typographic Scale (16.0pt-16.5pt body, 13.4pt-14.0pt pills on 23.8"x12.6"-15.4" canvas) & Fullwidth-Indent-Aware Kinsoku Shori
- Crameri et al. (2020), Okabe & Ito (2008), Knaflic (2015): 75-20-5 Preattentive Color Science
- Novak & Cañas (2008): Concept Maps with Relational Linking Phrase Pills & 1-to-2 Hierarchical Trunk Forks
- Purchase (1997) & Tufte (1990): Zero Edge Crossings & Z-order Stratification
"""

import argparse
import os
import re
import sys
import unicodedata
from pathlib import Path

_MPL_CACHE = None


def _get_mpl():
    """Lazy-load heavy Matplotlib modules only when drawing/configuring figures."""
    global _MPL_CACHE
    if _MPL_CACHE is None:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
        from matplotlib.path import Path as MplPath

        _MPL_CACHE = (plt, patches, FancyBboxPatch, FancyArrowPatch, MplPath)
    return _MPL_CACHE

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
from hcl_color_engine import GLOBAL_COLOR_CONTRACT

NO_START_CHARS = set("），。、；：！？）」』】〉》%),.;:?!)]}")
NO_END_CHARS = set("（「『【〈《([")
TOKEN_RE = re.compile(r"\d+(?:,\d+)+\+?|[A-Za-z0-9_.\-+%/]+|.")


def sanitize_cjk_glyphs(text):
    """Replaces glyphs and emojis missing in Windows Microsoft JhengHei with safe geometric equivalents."""
    if not text:
        return text
    return (
        text.replace("➔", "→")
            .replace("➜", "→")
            .replace("↔", "←→")
            .replace("⇄", "←→")
            .replace("⚠️", "▲")
            .replace("⚠", "▲")
            .replace("🟢", "●")
            .replace("🔴", "●")
            .replace("🔵", "●")
            .replace("🟡", "●")
            .replace("✅", "■")
            .replace("❌", "×")
            .replace("⭐", "★")
    )


# ==============================================================================
# 1. CURATED SCIENTIFIC THEME PALETTES (75-20-5 Preattentive Allocation + HCL Contract)
# ==============================================================================
_HCL_ACCENTS = {
    role: {"main": hcl_obj.accent_dark, "pill_bg": hcl_obj.surface_tint, "badge_fill": hcl_obj.badge_fill}
    for role, hcl_obj in GLOBAL_COLOR_CONTRACT.mapping.items()
}

THEMES = {
    "swiss_editorial": {
        "name": "Swiss Editorial (Default, HCL Calibrated)",
        "canvas_bg": GLOBAL_COLOR_CONTRACT.neutral_surface,
        "zone_bg": "#F1F5F9",
        "zone_border": "#CBD5E1",
        "card_bg": "#FFFFFF",
        "card_border": "#CBD5E1",
        "shadow": GLOBAL_COLOR_CONTRACT.neutral_dark,
        "text_title": GLOBAL_COLOR_CONTRACT.neutral_dark,
        "text_body": "#1E293B",
        "muted_ink": "#64748B",
        "edge_line": "#94A3B8",
        "hub_bg": GLOBAL_COLOR_CONTRACT.neutral_dark,
        "hub_border": "#38BDF8",
        "hub_text": "#F8FAFC",
        "hub_sub": "#38BDF8",
        "accents": {
            "primary": {"main": "#0284C7", "pill_bg": "#E0F2FE", "hcl_main": _HCL_ACCENTS["primary"]["main"]},
            "danger":  {"main": "#DC2626", "pill_bg": "#FEE2E2", "hcl_main": _HCL_ACCENTS["danger"]["main"]},
            "success": {"main": "#059669", "pill_bg": "#D1FAE5", "hcl_main": _HCL_ACCENTS["success"]["main"]},
            "warn":    {"main": "#D97706", "pill_bg": "#FEF3C7", "hcl_main": _HCL_ACCENTS["warn"]["main"]},
            "synth":   {"main": "#4F46E5", "pill_bg": "#E0E7FF", "hcl_main": _HCL_ACCENTS["synth"]["main"]},
        },
        "hcl_contract": _HCL_ACCENTS,
    },
    "hcl_scientific": {
        "name": "CIELUV HCL Equal-Chroma Scientific",
        "canvas_bg": GLOBAL_COLOR_CONTRACT.neutral_surface,
        "zone_bg": "#F1F5F9",
        "zone_border": GLOBAL_COLOR_CONTRACT.neutral_border,
        "card_bg": "#FFFFFF",
        "card_border": GLOBAL_COLOR_CONTRACT.neutral_border,
        "shadow": GLOBAL_COLOR_CONTRACT.neutral_dark,
        "text_title": GLOBAL_COLOR_CONTRACT.neutral_dark,
        "text_body": "#1E293B",
        "muted_ink": GLOBAL_COLOR_CONTRACT.neutral_muted,
        "edge_line": "#94A3B8",
        "hub_bg": GLOBAL_COLOR_CONTRACT.neutral_dark,
        "hub_border": _HCL_ACCENTS["primary"]["badge_fill"],
        "hub_text": "#F8FAFC",
        "hub_sub": "#7DD3FC",
        "accents": {
            role: {"main": val["main"], "pill_bg": val["pill_bg"]}
            for role, val in _HCL_ACCENTS.items()
        },
        "hcl_contract": _HCL_ACCENTS,
    },
    "mckinsey_executive": {
        "name": "McKinsey Executive",
        "canvas_bg": "#F4F6F9",
        "zone_bg": "#EAEFF5",
        "zone_border": "#C5D1E0",
        "card_bg": "#FFFFFF",
        "card_border": "#D0D9E6",
        "shadow": "#0A192F",
        "text_title": "#0A192F",
        "text_body": "#1E293B",
        "muted_ink": "#5A6A85",
        "edge_line": "#8FA0B5",
        "hub_bg": "#0A2540",
        "hub_border": "#00A3E0",
        "hub_text": "#FFFFFF",
        "hub_sub": "#7CE0FF",
        "accents": {
            "primary": {"main": "#005EB8", "pill_bg": "#E6F0FA"},
            "danger":  {"main": "#B91C1C", "pill_bg": "#FEE2E2"},
            "success": {"main": "#0F766E", "pill_bg": "#CCFBF1"},
            "warn":    {"main": "#B45309", "pill_bg": "#FEF3C7"},
            "synth":   {"main": "#1D4ED8", "pill_bg": "#DBEAFE"},
        },
        "hcl_contract": _HCL_ACCENTS,
    },
    "nature_academic": {
        "name": "Nature Academic (Okabe-Ito CVD Safe)",
        "canvas_bg": "#F9FAFB",
        "zone_bg": "#F3F4F6",
        "zone_border": "#D1D5DB",
        "card_bg": "#FFFFFF",
        "card_border": "#D1D5DB",
        "shadow": "#111827",
        "text_title": "#111827",
        "text_body": "#374151",
        "muted_ink": "#6B7280",
        "edge_line": "#9CA3AF",
        "hub_bg": "#111827",
        "hub_border": "#56B4E9",
        "hub_text": "#FFFFFF",
        "hub_sub": "#56B4E9",
        "accents": {
            "primary": {"main": "#0072B2", "pill_bg": "#EBF5FB"},
            "danger":  {"main": "#D55E00", "pill_bg": "#FEF3EB"},
            "success": {"main": "#009E73", "pill_bg": "#E8F8F5"},
            "warn":    {"main": "#E69F00", "pill_bg": "#FEF9E7"},
            "synth":   {"main": "#CC79A7", "pill_bg": "#FDEDEC"},
        },
        "hcl_contract": _HCL_ACCENTS,
    },
    "warm_humanist": {
        "name": "Warm Humanist",
        "canvas_bg": "#FAF7F2",
        "zone_bg": "#F3EFE6",
        "zone_border": "#DED8CE",
        "card_bg": "#FFFDF9",
        "card_border": "#DED8CE",
        "shadow": "#2C2523",
        "text_title": "#2C2523",
        "text_body": "#4A423E",
        "muted_ink": "#7D726D",
        "edge_line": "#ACA29A",
        "hub_bg": "#2C2523",
        "hub_border": "#D4A373",
        "hub_text": "#FAF7F2",
        "hub_sub": "#E9EDC9",
        "accents": {
            "primary": {"main": "#2B4C7E", "pill_bg": "#EDF2F8"},
            "danger":  {"main": "#A8382B", "pill_bg": "#FDF2F0"},
            "success": {"main": "#3B6E5C", "pill_bg": "#EFF6F3"},
            "warn":    {"main": "#B06D27", "pill_bg": "#FDF8F0"},
            "synth":   {"main": "#6B4C7A", "pill_bg": "#F5F0F7"},
        },
        "hcl_contract": _HCL_ACCENTS,
    },
    "modern_academic_slate": {
        "name": "Modern Academic Slate (Document Theme)",
        "canvas_bg": "#F8FAFC",
        "zone_bg": "#F1F5F9",
        "zone_border": "#CBD5E1",
        "card_bg": "#FFFFFF",
        "card_border": "#CBD5E1",
        "shadow": "#0F172A",
        "text_title": "#0F172A",
        "text_body": "#1E293B",
        "muted_ink": "#475569",
        "edge_line": "#94A3B8",
        "hub_bg": "#0F172A",
        "hub_border": "#38BDF8",
        "hub_text": "#F8FAFC",
        "hub_sub": "#38BDF8",
        "accents": {
            "primary": {"main": "#0284C7", "pill_bg": "#E0F2FE"},
            "danger":  {"main": "#E11D48", "pill_bg": "#FFE4E6"},
            "success": {"main": "#0D9488", "pill_bg": "#CCFBF1"},
            "warn":    {"main": "#D97706", "pill_bg": "#FEF3C7"},
            "synth":   {"main": "#4F46E5", "pill_bg": "#E0E7FF"},
        },
        "hcl_contract": _HCL_ACCENTS,
    },
    "warm_editorial_ivory": {
        "name": "Warm Editorial Ivory (Document Theme)",
        "canvas_bg": "#FAF8F5",
        "zone_bg": "#F3EFE6",
        "zone_border": "#E5E0D8",
        "card_bg": "#FFFFFF",
        "card_border": "#E5E0D8",
        "shadow": "#1C1917",
        "text_title": "#1C1917",
        "text_body": "#292524",
        "muted_ink": "#57534E",
        "edge_line": "#A8A29E",
        "hub_bg": "#1C1917",
        "hub_border": "#D97706",
        "hub_text": "#FAF8F5",
        "hub_sub": "#D97706",
        "accents": {
            "primary": {"main": "#9A3412", "pill_bg": "#FFEDD5"},
            "danger":  {"main": "#BE123C", "pill_bg": "#FFE4E6"},
            "success": {"main": "#15803D", "pill_bg": "#DCFCE7"},
            "warn":    {"main": "#B45309", "pill_bg": "#FEF3C7"},
            "synth":   {"main": "#6B4C7A", "pill_bg": "#F5F0F7"},
        },
        "hcl_contract": _HCL_ACCENTS,
    },
}


def resolve_diagram_theme(theme="swiss_editorial"):
    """Resolve diagram theme dict by name, including dynamic document_themes in config/user_preferences.json."""
    if isinstance(theme, dict):
        return theme
    theme_id = str(theme or "swiss_editorial").strip()
    if theme_id in THEMES:
        base = dict(THEMES[theme_id])
    else:
        base = dict(THEMES["swiss_editorial"])
    try:
        import json
        prefs_file = Path(__file__).resolve().parents[1] / "config" / "user_preferences.json"
        if prefs_file.exists():
            prefs = json.loads(prefs_file.read_text(encoding="utf-8"))
            doc_themes = prefs.get("color_sets", {}).get("document_themes", {})
            if theme_id in doc_themes:
                dt = doc_themes[theme_id]
                base = dict(THEMES.get(theme_id, THEMES["swiss_editorial"]))
                base["name"] = dt.get("theme_name", dt.get("name", base["name"]))
                base["canvas_bg"] = dt.get("bg_canvas", base["canvas_bg"])
                base["card_bg"] = dt.get("bg_card", base["card_bg"])
                base["card_border"] = dt.get("border_card", base["card_border"])
                base["zone_border"] = dt.get("border_card", base["zone_border"])
                base["text_title"] = dt.get("ink_primary", base["text_title"])
                base["shadow"] = dt.get("ink_primary", base["shadow"])
                base["text_body"] = dt.get("ink_secondary", base["text_body"])
                base["muted_ink"] = dt.get("ink_muted", base["muted_ink"])
                base["hub_bg"] = dt.get("bookend_dark_bg", dt.get("dark_bookend_bg", base["hub_bg"]))
                base["hub_border"] = dt.get("bookend_accent", dt.get("dark_bookend_accent", base["hub_border"]))
                base["hub_sub"] = dt.get("bookend_accent", dt.get("dark_bookend_accent", base["hub_sub"]))
                accents = dict(base.get("accents", {}))
                accents["primary"] = {"main": dt.get("primary_accent", "#0284C7"), "pill_bg": dt.get("primary_tint", "#E0F2FE")}
                accents["danger"] = {"main": dt.get("danger_accent", "#E11D48"), "pill_bg": dt.get("danger_tint", "#FFE4E6")}
                accents["success"] = {"main": dt.get("success_accent", "#0D9488"), "pill_bg": dt.get("success_tint", "#CCFBF1")}
                accents["warn"] = {"main": dt.get("warn_accent", "#D97706"), "pill_bg": dt.get("warn_tint", "#FEF3C7")}
                base["accents"] = accents
    except Exception:
        pass
    return base



# ==============================================================================
# 2. CJK FONT, COMPACT HIGH-LEGIBILITY CALIBRATION & AUTO-WRAPPING ENGINE
# ==============================================================================
DEFAULT_FIG_W = 23.8
DEFAULT_FIG_H = 15.4
A4_PORTRAIT_WIDTH_IN = 7.44  # 189mm printable A4 portrait width

REF_PT_PER_X = (DEFAULT_FIG_W * 0.98 * 72.0) / 100.0   # ~16.793 pt per X-unit
REF_PT_PER_Y = (DEFAULT_FIG_H * 0.96 * 72.0) / 100.0   # ~10.644 pt per Y-unit


def get_canvas_metrics(ax=None, fig_width_in=None, fig_height_in=None):
    """
    Returns (fig_w, fig_h, pt_per_x, pt_per_y, scale_x, scale_y) calibrated to the
    active figure dimensions (using left=0.01..0.99 -> 0.98W, bottom=0.02..0.98 -> 0.96H).
    """
    if fig_width_in is None or fig_height_in is None:
        if ax is not None and getattr(ax, "figure", None) is not None:
            w_in, h_in = ax.figure.get_size_inches()
            if fig_width_in is None:
                fig_width_in = float(w_in)
            if fig_height_in is None:
                fig_height_in = float(h_in)
        else:
            if fig_width_in is None:
                fig_width_in = DEFAULT_FIG_W
            if fig_height_in is None:
                fig_height_in = DEFAULT_FIG_H
    fig_width_in = float(fig_width_in)
    fig_height_in = float(fig_height_in)
    pt_per_x = (fig_width_in * 0.98 * 72.0) / 100.0
    pt_per_y = (fig_height_in * 0.96 * 72.0) / 100.0
    scale_x = REF_PT_PER_X / pt_per_x
    scale_y = REF_PT_PER_Y / pt_per_y
    return fig_width_in, fig_height_in, pt_per_x, pt_per_y, scale_x, scale_y


def configure_cjk_fonts():
    """Configures cross-platform Traditional Chinese (CJK) font fallbacks."""
    plt, _, _, _, _ = _get_mpl()
    try:
        from chart_common import CJK_FONT_FALLBACKS

        cjk_fonts = list(CJK_FONT_FALLBACKS)
    except ImportError:
        cjk_fonts = [
            "Microsoft JhengHei",
            "PingFang TC",
            "Noto Sans CJK TC",
            "Source Han Sans TC",
            "Heiti TC",
            "WenQuanYi Micro Hei",
            "SimHei",
            "Arial Unicode MS",
            "sans-serif",
        ]
    plt.rcParams["font.sans-serif"] = cjk_fonts
    plt.rcParams["axes.unicode_minus"] = False


def char_visual_width(ch):
    """Returns approximate visual width in CJK em-units (Hanzi=1.0, ASCII=0.53)."""
    eaw = unicodedata.east_asian_width(ch)
    return 1.0 if eaw in ("W", "F") else 0.53


def token_visual_width(tok):
    return sum(char_visual_width(c) for c in tok)


def _text_width_x(text, font_pt, pt_per_x=REF_PT_PER_X):
    em = sum(char_visual_width(c) for c in (text or ""))
    return (em * font_pt) / pt_per_x


def compute_dynamic_max_em(card_width, fig_width_in=DEFAULT_FIG_W, font_pt=16.2, pad_units=2.04):
    """
    Dynamically computes max_em_width from the card's actual physical width on the figure
    so wrapped text fills 88%–92% of the card width with zero right-side empty gap.
    """
    usable_width_units = max(6.0, card_width - pad_units)
    usable_points = (usable_width_units / 100.0) * (fig_width_in * 0.98) * 72.0
    return usable_points / (font_pt * 1.02)


def apply_kinsoku_shori(lines):
    """
    Enforces W3C CLREQ Kinsoku Shori (避頭尾標點規則) while preserving fullwidth hanging indent ('\\u3000 ').
    Ensures no wrapped line starts with a closing bracket/comma/period or ends with an opening bracket.
    """
    lines = list(lines)
    for i in range(len(lines) - 1):
        next_body = lines[i + 1].lstrip(" \u3000\t")
        indent_prefix = lines[i + 1][:len(lines[i + 1]) - len(next_body)]
        while len(next_body) > 0 and next_body[0] in NO_START_CHARS and len(lines[i]) > 2:
            next_body = lines[i][-1] + next_body
            lines[i] = lines[i][:-1]
        while len(lines[i]) > 1 and lines[i][-1] in NO_END_CHARS:
            next_body = lines[i][-1] + next_body
            lines[i] = lines[i][:-1]
        lines[i + 1] = indent_prefix + next_body
    return lines


def wrap_cjk_text(text, max_em_width=None, hanging_indent="　 ", card_width=30.0,
                  fig_width_in=DEFAULT_FIG_W, font_pt=16.2):
    """
    Wraps a single bullet string according to W3C CLREQ visual measure limits,
    keeping English words/numbers intact, using full-width hanging indent ('\\u3000 ')
    to match the exact width of '● ', and enforcing fullwidth-indent-aware Kinsoku Shori.
    """
    text = sanitize_cjk_glyphs(text)
    if max_em_width is None:
        max_em_width = compute_dynamic_max_em(card_width, fig_width_in=fig_width_in, font_pt=font_pt)

    indent_w = token_visual_width(hanging_indent)
    lines = []
    for raw_seg in text.split("\n"):
        tokens = TOKEN_RE.findall(raw_seg)
        current_line = ""
        current_w = 0.0
        for tok in tokens:
            w = token_visual_width(tok)
            if current_w + w > max_em_width and current_line.strip():
                if tok in NO_START_CHARS:
                    current_line += tok
                    lines.append(current_line)
                    current_line = hanging_indent
                    current_w = indent_w
                else:
                    lines.append(current_line)
                    tok_clean = tok.lstrip(" ")
                    current_line = hanging_indent + tok_clean
                    current_w = indent_w + token_visual_width(tok_clean)
            else:
                current_line += tok
                current_w += w
        if current_line.strip():
            lines.append(current_line)
    return apply_kinsoku_shori(lines)


def prepare_card_slots(bullets, max_em_width=None, card_width=30.0,
                       fig_width_in=DEFAULT_FIG_W, font_pt=16.2):
    """Expands each bullet string into its own list of Kinsoku-protected wrapped lines (1 slot per bullet)."""
    slots = []
    for b in bullets:
        wrapped = wrap_cjk_text(b, max_em_width=max_em_width, card_width=card_width,
                                fig_width_in=fig_width_in, font_pt=font_pt)
        slots.append(apply_kinsoku_shori(wrapped))
    return slots


def prepare_card_lines(bullets, max_em_width=None, card_width=30.0,
                       fig_width_in=DEFAULT_FIG_W, font_pt=16.2):
    """Expands a list of bullet strings into wrapped visual lines."""
    all_lines = []
    for slot in prepare_card_slots(bullets, max_em_width=max_em_width, card_width=card_width,
                                   fig_width_in=fig_width_in, font_pt=font_pt):
        all_lines.extend(slot)
    return all_lines


def measure_card_height(
    width, title, bullets, badge_text=None,
    font_pt=16.2, title_pt=17.4, badge_pt=13.6,
    line_spacing=1.50, slot_pad=0.88, fixed_height=None,
    fig_width_in=None, fig_height_in=None, ax=None, max_em_width=None
):
    """
    Accurately measures natural card height in 0-100 Y-coordinates calibrated to canvas dimensions,
    including automatic stacked-header detection when badge + title exceed single-line width.
    """
    fig_w, fig_h, pt_per_x, pt_per_y, _sx, scale_y = get_canvas_metrics(
        ax=ax, fig_width_in=fig_width_in, fig_height_in=fig_height_in
    )
    _, _, FancyBboxPatch, _, _ = _get_mpl()
    title = sanitize_cjk_glyphs(title)
    badge_text = sanitize_cjk_glyphs(badge_text)
    strip_w = 0.60
    left_pad = strip_w + 0.72
    right_pad = 0.72
    usable_w_x = max(6.0, width - left_pad - right_pad)
    eff_max_em = max_em_width if max_em_width is not None else (usable_w_x * pt_per_x) / (font_pt * 1.02)

    slots = [
        apply_kinsoku_shori(wrap_cjk_text(b, max_em_width=eff_max_em, hanging_indent="　 "))
        for b in bullets
    ]

    stack_header = False
    if badge_text:
        badge_w_x = _text_width_x(f" {badge_text} ", badge_pt, pt_per_x=pt_per_x) + 0.72
        title_w_x = _text_width_x(title, title_pt, pt_per_x=pt_per_x)
        if badge_w_x + 0.75 + title_w_x > usable_w_x:
            if badge_w_x + 0.65 + _text_width_x(title, max(12.0, title_pt - 1.2), pt_per_x=pt_per_x) > usable_w_x:
                stack_header = True

    header_h = (6.05 if stack_header else 3.95) * scale_y
    line_step = (font_pt * line_spacing) / pt_per_y
    body_h = sum(max(1, len(s)) * line_step + slot_pad * scale_y for s in slots) + 0.35 * scale_y
    calc_h = header_h + body_h
    return max(fixed_height, calc_h) if fixed_height else calc_h


def compute_card_height(bullets, max_em_width=None, line_Step=None, header_pad=None, bottom_pad=None,
                        card_width=30.0, fig_width_in=DEFAULT_FIG_W, font_pt=16.2,
                        fig_height_in=DEFAULT_FIG_H, line_spacing=1.50, slot_pad=0.88):
    """Mathematically computes the exact card height and wrapped lines in 0-100 canvas coordinates."""
    wrapped_lines = prepare_card_lines(
        bullets, max_em_width=max_em_width, card_width=card_width,
        fig_width_in=fig_width_in, font_pt=font_pt
    )
    if line_Step is not None or header_pad is not None or bottom_pad is not None:
        ls = 1.78 if line_Step is None else line_Step
        hp = 4.2 if header_pad is None else header_pad
        bp = 1.5 if bottom_pad is None else bottom_pad
        return hp + len(wrapped_lines) * ls + bp, wrapped_lines
    h = measure_card_height(
        card_width, "", bullets, font_pt=font_pt, line_spacing=line_spacing,
        slot_pad=slot_pad, fig_width_in=fig_width_in, fig_height_in=fig_height_in,
        max_em_width=max_em_width
    )
    return h, wrapped_lines


def fit_stacked_cards_to_zone(
    card_specs, zone_y, zone_h, gap=2.1,
    top_offset=3.45, bot_margin=1.00, target_fill=0.91,
    fig_width_in=None, fig_height_in=None, ax=None
):
    """
    Computes natural heights for stacked cards inside a Macro Zone and expands proportionally
    only when `target_fill` is specified (e.g. 0.91 for 2-row cards).
    Pass `target_fill=None` for 3-row dense cards to keep natural heights without artificial stretching.
    Returns (top_y_start, heights_list).
    """
    fig_w, fig_h, _px, _py, _sx, scale_y = get_canvas_metrics(
        ax=ax, fig_width_in=fig_width_in, fig_height_in=fig_height_in
    )
    usable_top = zone_y + zone_h - top_offset * scale_y
    usable_bot = zone_y + bot_margin * scale_y
    usable_h = usable_top - usable_bot

    nat_hs = [
        measure_card_height(
            s["width"], s["title"], s["bullets"],
            badge_text=s.get("badge_text", s.get("badge")),
            font_pt=s.get("font_pt", 16.2),
            title_pt=s.get("title_pt", 17.4),
            badge_pt=s.get("badge_pt", 13.6),
            line_spacing=s.get("line_spacing", 1.50),
            slot_pad=s.get("slot_pad", 0.88),
            fig_width_in=fig_w, fig_height_in=fig_h,
        )
        for s in card_specs
    ]
    n = len(nat_hs)
    total_gaps = max(0, n - 1) * gap
    nat_cards_sum = sum(nat_hs)
    if target_fill is not None and nat_cards_sum > 0:
        target_cards_sum = usable_h * target_fill - total_gaps
        if target_cards_sum > nat_cards_sum:
            extra = target_cards_sum - nat_cards_sum
            final_hs = [h + extra * (h / nat_cards_sum) for h in nat_hs]
        else:
            final_hs = nat_hs
    else:
        final_hs = nat_hs
    return usable_top, final_hs


def box_edge_point(box, side, pad=0.20, frac=0.5, ax=None):
    """
    Returns FancyBboxPatch pad-compensated (x, y) anchor point on the requested edge
    ('left', 'right', 'top', 'bottom') of a (x, y, width, height) box.
    """
    _, _, _, _, scale_x, scale_y = get_canvas_metrics(ax=ax)
    bx, by, bw, bh = box
    px_pad = pad * scale_x
    py_pad = pad * scale_y
    s = str(side).lower()
    if s == "left":
        return (bx - px_pad, by + bh * frac)
    if s == "right":
        return (bx + bw + px_pad, by + bh * frac)
    if s == "top":
        return (bx + bw * frac, by + bh + py_pad)
    if s == "bottom":
        return (bx + bw * frac, by - py_pad)
    raise ValueError(f"Unsupported side '{side}'. Expected 'left', 'right', 'top', or 'bottom'.")


# ==============================================================================
# 3. LAYERED GRAPHICAL PRIMITIVES (Palmer, Tufte, Novak, Purchase)
# ==============================================================================
def draw_macro_zone(ax, x, y, width, height, zone_title, theme, accent_key=None, is_dashed=False, font_pt=16.0):
    """
    Z-Order 1: Draws a Palmer (1992) 'Common Region' macro container box
    to group related sub-cards and keep top-level chunks within Cowan's 4±1 limit.
    """
    _, _, FancyBboxPatch, _, _ = _get_mpl()
    _, _, _, pt_per_y, _, _ = get_canvas_metrics(ax=ax)
    title_color = theme["accents"][accent_key]["main"] if (accent_key and accent_key in theme["accents"]) else theme["muted_ink"]
    zone_box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.25,rounding_size=1.1",
        linewidth=1.7 if not is_dashed else 1.8,
        edgecolor=theme["zone_border"],
        facecolor=theme["zone_bg"],
        linestyle="--" if is_dashed else "-",
        alpha=0.92,
        zorder=1
    )
    ax.add_patch(zone_box)
    if zone_title:
        ax.text(
            x + 0.95, y + height - 14.902 / pt_per_y, sanitize_cjk_glyphs(zone_title),
            fontsize=font_pt, fontweight="bold",
            color=title_color, va="center", ha="left", zorder=2
        )


def draw_modern_card(ax, x, y, width, title, bullets, theme,
                     accent_key="primary", badge_text=None,
                     max_em_width=None, is_dashed=False, fixed_height=None,
                     fig_width_in=None, font_pt=16.2,
                     title_pt=17.4, badge_pt=13.6, line_spacing=1.50, slot_pad=0.88,
                     top_y=None, fig_height_in=None, force_height=False):
    """
    Z-Order 3-4: Draws a Tufte-layered, Swiss-grid aligned card with:
    - Compact high-legibility typography (Title=17.4pt, Badge=13.6pt, Body=16.2pt)
    - Dynamic width-calibrated CJK wrapping & automatic stacked-header fallback on narrow cards
    - Optional `top_y` anchoring (extends downward from `top_y` for exact collision-free stacking)
    - Weighted modular row slots with true mathematical vertical centering (va='center')
    Returns (x, y, width, height) for exact connector anchoring.
    """
    fig_w, fig_h, pt_per_x, pt_per_y, _sx, scale_y = get_canvas_metrics(
        ax=ax, fig_width_in=fig_width_in, fig_height_in=fig_height_in
    )
    _, _, FancyBboxPatch, _, _ = _get_mpl()
    title = sanitize_cjk_glyphs(title)
    badge_text = sanitize_cjk_glyphs(badge_text)
    accent = theme["accents"].get(accent_key, theme["accents"]["primary"])
    accent_color = accent["main"]
    pill_bg = accent["pill_bg"]

    strip_w = 0.60
    left_pad = strip_w + 0.72
    right_pad = 0.72
    usable_w_x = max(6.0, width - left_pad - right_pad)
    eff_max_em = max_em_width if max_em_width is not None else (usable_w_x * pt_per_x) / (font_pt * 1.02)

    slots = [
        apply_kinsoku_shori(wrap_cjk_text(b, max_em_width=eff_max_em, hanging_indent="　 "))
        for b in bullets
    ]

    stack_header = False
    eff_title_pt = title_pt
    if badge_text:
        badge_w_x = _text_width_x(f" {badge_text} ", badge_pt, pt_per_x=pt_per_x) + 0.72
        title_w_x = _text_width_x(title, eff_title_pt, pt_per_x=pt_per_x)
        if badge_w_x + 0.75 + title_w_x > usable_w_x:
            if badge_w_x + 0.65 + _text_width_x(title, max(12.0, title_pt - 1.2), pt_per_x=pt_per_x) <= usable_w_x:
                eff_title_pt = max(12.0, title_pt - 1.2)
            else:
                stack_header = True
                eff_title_pt = min(title_pt, 16.6)

    header_h = (6.05 if stack_header else 3.95) * scale_y
    line_step = (font_pt * line_spacing) / pt_per_y
    body_h = sum(max(1, len(s)) * line_step + slot_pad * scale_y for s in slots) + 0.35 * scale_y
    calc_h = header_h + body_h
    if fixed_height and force_height:
        height = float(fixed_height)
    else:
        height = max(fixed_height, calc_h) if fixed_height else calc_h

    if top_y is not None:
        y = top_y - height

    # 1. Subtle Elevation Shadow (zorder=2.5)
    ax.add_patch(FancyBboxPatch(
        (x + 0.18, y - 0.24 * scale_y), width, height,
        boxstyle="round,pad=0.18,rounding_size=0.8",
        linewidth=0, facecolor=theme["shadow"], alpha=0.055, zorder=2.5
    ))

    # 2. Clean Neutral Card Surface (zorder=3)
    ax.add_patch(FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.18,rounding_size=0.8",
        linewidth=1.55 if not is_dashed else 1.8,
        edgecolor=theme["card_border"] if not is_dashed else accent_color,
        facecolor=theme["card_bg"],
        linestyle="--" if is_dashed else "-",
        zorder=3
    ))

    # 3. Left Preattentive Semantic Accent Strip (zorder=3.5)
    ax.add_patch(FancyBboxPatch(
        (x, y + 0.30 * scale_y), strip_w, max(0.5 * scale_y, height - 0.60 * scale_y),
        boxstyle="round,pad=0.04,rounding_size=0.25",
        linewidth=0, facecolor=accent_color, zorder=3.5
    ))

    # 4. Header Badge Pill & Card Title
    text_x = x + left_pad
    divider_y = y + height - header_h

    if badge_text and not stack_header:
        badge_w_x = _text_width_x(f" {badge_text} ", badge_pt, pt_per_x=pt_per_x) + 0.72
        header_mid_y = y + height - header_h / 2.0
        ax.text(
            text_x, header_mid_y, f" {badge_text} ",
            fontsize=badge_pt, fontweight="bold", color=accent_color,
            va="center", ha="left", zorder=4,
            bbox=dict(
                boxstyle="round,pad=0.22,rounding_size=0.4",
                facecolor=pill_bg, edgecolor=accent_color, lw=1.05
            )
        )
        ax.text(
            text_x + badge_w_x + 0.55, header_mid_y, title,
            fontsize=eff_title_pt, fontweight="bold", color=theme["text_title"],
            va="center", ha="left", zorder=4
        )
    elif badge_text and stack_header:
        ax.text(
            text_x, y + height - 1.65 * scale_y, f" {badge_text} ",
            fontsize=badge_pt, fontweight="bold", color=accent_color,
            va="center", ha="left", zorder=4,
            bbox=dict(
                boxstyle="round,pad=0.22,rounding_size=0.38",
                facecolor=pill_bg, edgecolor=accent_color, lw=1.05
            )
        )
        ax.text(
            text_x, y + height - 4.35 * scale_y, title,
            fontsize=eff_title_pt, fontweight="bold", color=theme["text_title"],
            va="center", ha="left", zorder=4
        )
    else:
        ax.text(
            text_x, y + height - header_h / 2.0, title,
            fontsize=eff_title_pt, fontweight="bold", color=accent_color,
            va="center", ha="left", zorder=4
        )

    ax.plot(
        [text_x, x + width - right_pad], [divider_y, divider_y],
        color=theme["card_border"], linewidth=1.0, alpha=0.9, zorder=3.5
    )

    # 5. Weighted Modular Horizontal Row Slots with True Vertical Centering (va="center")
    num_slots = len(slots)
    if num_slots > 0:
        body_top = divider_y - 0.14 * scale_y
        body_bot = y + 0.04 * scale_y
        avail_h = max(1.5 * scale_y, body_top - body_bot)
        weights = [max(1, len(s)) * line_step + slot_pad * scale_y for s in slots]
        total_w = sum(weights)
        curr_top = body_top
        for s_idx, (slot_lines, w) in enumerate(zip(slots, weights)):
            slot_h = avail_h * (w / total_w)
            slot_center_y = curr_top - slot_h / 2.0
            if s_idx > 0:
                ax.plot(
                    [text_x, x + width - right_pad], [curr_top, curr_top],
                    color=theme["card_border"], linewidth=0.8, alpha=0.75, zorder=3.5
                )
            m_lines = len(slot_lines)
            eff_step = min(line_step, (slot_h * 0.84) / max(1, m_lines))
            start_y = slot_center_y + ((m_lines - 1) * eff_step) / 2.0
            for l_i, line in enumerate(slot_lines):
                ax.text(
                    text_x, start_y - l_i * eff_step, line,
                    fontsize=font_pt, color=theme["text_body"],
                    va="center", ha="left", zorder=4
                )
            curr_top -= slot_h

    return (x, y, width, height)


def draw_zone_stacked_cards(
    ax, x, width, zone_y, zone_h, cards_data, theme,
    gap=2.1, target_fill=0.91, distribute_gap_if_unfilled=False
):
    """
    Convenience helper that measures, optionally expands (`target_fill`), and stacks a list of
    card dicts inside a Macro Zone using `top_y` anchoring.
    Returns (boxes_list, fill_ratio).
    """
    fig_w, fig_h, _px, _py, _sx, scale_y = get_canvas_metrics(ax=ax)
    specs = [
        {
            "width": width,
            "title": d["title"],
            "bullets": d["bullets"],
            "badge_text": d.get("badge_text", d.get("badge")),
            "font_pt": d.get("font_pt", 16.2),
            "title_pt": d.get("title_pt", 17.4),
            "badge_pt": d.get("badge_pt", 13.6),
            "line_spacing": d.get("line_spacing", 1.50),
            "slot_pad": d.get("slot_pad", 0.88),
        }
        for d in cards_data
    ]
    top_y, heights = fit_stacked_cards_to_zone(
        specs, zone_y=zone_y, zone_h=zone_h, gap=gap,
        top_offset=3.45, bot_margin=1.00, target_fill=target_fill, ax=ax
    )
    usable_h = (zone_y + zone_h - 3.45 * scale_y) - (zone_y + 1.00 * scale_y)
    if distribute_gap_if_unfilled and len(heights) > 1:
        eff_gap = max(gap, (usable_h - sum(heights)) / (len(heights) - 1))
    else:
        eff_gap = gap

    boxes = []
    curr_top = top_y
    for d, h in zip(cards_data, heights):
        box = draw_modern_card(
            ax, x, 0, width, d["title"], d["bullets"], theme,
            accent_key=d.get("accent_key", "primary"),
            badge_text=d.get("badge_text", d.get("badge")),
            font_pt=d.get("font_pt", 16.2), title_pt=d.get("title_pt", 17.4),
            badge_pt=d.get("badge_pt", 13.6),
            line_spacing=d.get("line_spacing", 1.50), slot_pad=d.get("slot_pad", 0.88),
            fixed_height=h, top_y=curr_top, fig_width_in=fig_w, fig_height_in=fig_h
        )
        boxes.append(box)
        curr_top = box[1] - eff_gap
    span = (top_y - boxes[-1][1]) if boxes else 0.0
    return boxes, (span / usable_h if usable_h > 0 else 0.0)


def draw_hierarchical_trunk_fork(ax, p_start, p_card1, p_card2, trunk_label,
                                 theme=None, accent_key="primary", lw=2.4, font_pt=13.8):
    """
    Draws a true Hierarchical Chunking connector (1 Main Trunk -> 2 Sub-Card Branches),
    strictly enforcing Cowan's 4±1 branching limit at the macro hub level (4 trunks total)
    and bifurcating symmetrically at the midpoint of the corridor.
    """
    if theme is None:
        theme = THEMES["swiss_editorial"]
    _, patches, _, _, MplPath = _get_mpl()
    accent = theme["accents"].get(accent_key, theme["accents"]["primary"])
    line_color = accent["main"]
    pill_bg = accent["pill_bg"]

    x0, y0 = p_start
    x1, y1 = p_card1
    x2, y2 = p_card2
    split_x = (x0 + x1) / 2.0
    split_y = (y1 + y2) / 2.0

    dx_trunk = split_x - x0
    t_verts = [
        (x0, y0),
        (x0 + dx_trunk * 0.50, y0),
        (split_x - dx_trunk * 0.50, split_y),
        (split_x, split_y)
    ]
    t_codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4]
    trunk_patch = patches.PathPatch(
        MplPath(t_verts, t_codes), facecolor="none", edgecolor=line_color,
        linewidth=lw + 0.5, alpha=0.92, zorder=2
    )
    ax.add_patch(trunk_patch)

    for (tx, ty) in [(x1, y1), (x2, y2)]:
        dx = tx - split_x
        p1 = (split_x + dx * 0.48, split_y)
        p2 = (tx - dx * 0.48, ty)
        verts = [(split_x, split_y), p1, p2, (tx, ty)]
        codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4]
        patch = patches.PathPatch(
            MplPath(verts, codes), facecolor="none", edgecolor=line_color,
            linewidth=lw, alpha=0.88, zorder=2
        )
        ax.add_patch(patch)
        ax.scatter([tx], [ty], s=36, color=line_color, zorder=4)

    ax.text(
        split_x, split_y, f" {sanitize_cjk_glyphs(trunk_label)} ",
        fontsize=font_pt, fontweight="bold", color=line_color,
        ha="center", va="center", zorder=5,
        bbox=dict(
            boxstyle="round,pad=0.22,rounding_size=0.45",
            facecolor=pill_bg, edgecolor=line_color, lw=1.3, alpha=0.99
        )
    )


def draw_labeled_bezier(ax, p0, p3, label_text=None, theme=None,
                        accent_key=None, width=2.2, alpha=0.88, font_pt=13.6):
    """
    Z-Order 2 (curve) & Z-Order 5 (Novak Relational Pill Label):
    Draws a smooth zero-crossing cubic Bezier connector with an optional
    Novak & Cañas (2008) relational linking phrase pill at its midpoint.
    """
    if theme is None:
        theme = THEMES["swiss_editorial"]
    _, patches, _, _, MplPath = _get_mpl()

    if accent_key and accent_key in theme["accents"]:
        line_color = theme["accents"][accent_key]["main"]
        pill_bg = theme["accents"][accent_key]["pill_bg"]
    else:
        line_color = theme["edge_line"]
        pill_bg = "#FFFFFF"

    x0, y0 = p0
    x3, y3 = p3
    dx = x3 - x0
    p1 = (x0 + dx * 0.48, y0)
    p2 = (x3 - dx * 0.48, y3)

    verts = [p0, p1, p2, p3]
    codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4]
    path = MplPath(verts, codes)
    patch = patches.PathPatch(
        path, facecolor="none", edgecolor=line_color,
        linewidth=width, alpha=alpha, zorder=2
    )
    ax.add_patch(patch)

    if label_text:
        mx = 0.125 * x0 + 0.375 * p1[0] + 0.375 * p2[0] + 0.125 * x3
        my = 0.125 * y0 + 0.375 * p1[1] + 0.375 * p2[1] + 0.125 * y3
        ax.text(
            mx, my, f" {sanitize_cjk_glyphs(label_text)} ",
            fontsize=font_pt, fontweight="bold",
            color=line_color if accent_key else theme["text_body"],
            ha="center", va="center", zorder=5,
            bbox=dict(
                boxstyle="round,pad=0.20,rounding_size=0.45",
                facecolor=pill_bg, edgecolor=line_color, lw=1.2, alpha=0.98
            )
        )


def draw_labeled_arrow(ax, p0, p1, label_text=None, theme=None,
                       accent_key="primary", rad=0.0, font_pt=13.6):
    """
    Draws a directed causal arrow with a Novak relational pill label.
    When `rad != 0`, centers the pill on the true quadratic Bezier apex of `arc3,rad=...`.
    """
    if theme is None:
        theme = THEMES["swiss_editorial"]
    _, _, _, FancyArrowPatch, _ = _get_mpl()
    accent = theme["accents"].get(accent_key, theme["accents"]["primary"])
    color = accent["main"]

    arrow = FancyArrowPatch(
        p0, p1,
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="simple,head_length=7,head_width=7,tail_width=2.2",
        color=color, alpha=0.88, zorder=4
    )
    ax.add_patch(arrow)

    if label_text:
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        mx = (p0[0] + p1[0]) / 2.0 + 0.5 * rad * dy
        my = (p0[1] + p1[1]) / 2.0 - 0.5 * rad * dx
        ax.text(
            mx, my, f" {sanitize_cjk_glyphs(label_text)} ",
            fontsize=font_pt, fontweight="bold", color=color,
            ha="center", va="center", zorder=5,
            bbox=dict(
                boxstyle="round,pad=0.22,rounding_size=0.45",
                facecolor="#FFFFFF", edgecolor=color, lw=1.2
            )
        )


# ==============================================================================
# 4. HIGH-LEVEL TOPOLOGY LAYOUT HELPERS (T1 - T5)
# ==============================================================================
def draw_spine_hub_module(
    ax, x, y, width, height, step_badge, title, subtitle_lines,
    theme=None, accent_key="primary",
    title_pt=16.6, badge_pt=13.8, subtitle_pt=14.0
):
    """
    T1 / T5 Helper: Draws a high-contrast central spine module or top-level focus problem hub.
    Returns (x, y, width, height) for trunk-fork or downward arrow anchoring.
    """
    if theme is None:
        theme = THEMES["swiss_editorial"]
    _, _, FancyBboxPatch, _, _ = _get_mpl()
    _, _, _, pt_per_y, _, scale_y = get_canvas_metrics(ax=ax)
    accent = theme["accents"].get(accent_key, theme["accents"]["primary"])
    border_col = accent["main"]

    hub_box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.22,rounding_size=0.9",
        facecolor=theme["hub_bg"], edgecolor=border_col,
        linewidth=2.1, zorder=3
    )
    ax.add_patch(hub_box)

    top_y = y + height - 2.35 * scale_y
    if step_badge:
        ax.text(
            x + width / 2.0, top_y, f" {sanitize_cjk_glyphs(step_badge)} ",
            fontsize=badge_pt, fontweight="bold", color=theme["hub_bg"],
            ha="center", va="center", zorder=4,
            bbox=dict(boxstyle="round,pad=0.22,rounding_size=0.4", facecolor=theme["hub_sub"], edgecolor="none")
        )
        title_y = top_y - 3.30 * scale_y
    else:
        title_y = y + height - 2.60 * scale_y

    ax.text(
        x + width / 2.0, title_y, sanitize_cjk_glyphs(title),
        fontsize=title_pt, fontweight="bold", color=theme["hub_text"],
        ha="center", va="center", zorder=4
    )

    lines = subtitle_lines if isinstance(subtitle_lines, (list, tuple)) else str(subtitle_lines).split("\n")
    start_sub_y = title_y - 3.05 * scale_y
    line_step = (subtitle_pt * 1.94) / pt_per_y
    for idx, line in enumerate(lines):
        ax.text(
            x + width / 2.0, start_sub_y - idx * line_step, sanitize_cjk_glyphs(line),
            fontsize=subtitle_pt, color=theme["hub_sub"],
            ha="center", va="center", zorder=4
        )
    return (x, y, width, height)


def draw_3x3_pipeline_grid(
    ax, columns_spec, theme=None, horizontal_links=None, vertical_links=None,
    fig_width_in=None, font_pt=16.0, title_pt=16.8, badge_pt=13.4, pill_pt=13.4
):
    """
    T2 Helper: Draws a 3-Column Pipeline / 3x3 Wiring Grid with widened pill corridors (>= 6.6-8.0 X-units),
    high-legibility typography, `measure_card_height` + `top_y` stacking, and pad-compensated link endpoints.
    Dynamically adapts zone vertical bounds to any figure height (12.6"-15.4") and guarantees zero card overflow.
    Returns a 3x3 matrix of card bounding boxes `grid_boxes[col_idx][row_idx]`.
    """
    if theme is None:
        theme = THEMES["swiss_editorial"]
    fig_w, fig_h, _px, pt_per_y, _sx, scale_y = get_canvas_metrics(ax=ax, fig_width_in=fig_width_in)

    # Widened corridors between zones (X gaps: 36.6 - 28.0 = 8.6; 72.0 - 63.4 = 8.6 X-units)
    col_x = [1.2, 36.6, 72.0]
    col_w = 26.8
    zone_bot = (11.709 + 88.349 + 14.902) / pt_per_y
    zone_top = 100.0 - (98.994 + 13.840) / pt_per_y
    zone_y = zone_bot
    zone_h = max(20.0, zone_top - zone_bot)
    card_w = col_w - 1.4
    usable_top = zone_y + zone_h - 3.45 * scale_y
    usable_bot = zone_y + 1.00 * scale_y
    usable_h = max(12.0, usable_top - usable_bot)

    grid_boxes = [[None for _ in range(3)] for _ in range(3)]

    def _measure_rows(eff_ls, eff_pad, eff_fpt):
        rhs = [0.0, 0.0, 0.0]
        for col in columns_spec[:3]:
            for r_i, card in enumerate(col.get("cards", [])[:3]):
                nh = measure_card_height(
                    card_w, card.get("title", ""), card.get("bullets", []),
                    badge_text=card.get("badge", card.get("badge_text")),
                    font_pt=card.get("font_pt", eff_fpt),
                    title_pt=card.get("title_pt", title_pt),
                    badge_pt=card.get("badge_pt", badge_pt),
                    line_spacing=card.get("line_spacing", eff_ls),
                    slot_pad=card.get("slot_pad", eff_pad),
                    fig_width_in=fig_w, fig_height_in=fig_h,
                )
                rhs[r_i] = max(rhs[r_i], nh)
        return rhs

    eff_line_spacing = 1.50
    eff_slot_pad = 0.88
    eff_font_pt = font_pt
    min_gap = (2.4 if vertical_links else 1.8) * scale_y
    max_cards_h = max(9.0, usable_h - 2.0 * min_gap)

    row_heights = _measure_rows(eff_line_spacing, eff_slot_pad, eff_font_pt)
    if sum(row_heights) > max_cards_h:
        eff_line_spacing, eff_slot_pad = 1.38, 0.52
        row_heights = _measure_rows(eff_line_spacing, eff_slot_pad, eff_font_pt)
    if sum(row_heights) > max_cards_h:
        eff_font_pt = max(13.5, font_pt - 1.4)
        row_heights = _measure_rows(eff_line_spacing, eff_slot_pad, eff_font_pt)

    force_shrink = False
    total_cards_h = sum(row_heights)
    if total_cards_h > max_cards_h and total_cards_h > 0:
        shrink = max_cards_h / total_cards_h
        row_heights = [h * shrink for h in row_heights]
        force_shrink = True

    row_gap = max(0.8 * scale_y, (usable_h - sum(row_heights)) / 2.0)

    row_tops = [
        usable_top,
        usable_top - row_heights[0] - row_gap,
        usable_top - row_heights[0] - row_gap - row_heights[1] - row_gap,
    ]

    for c_i, col in enumerate(columns_spec[:3]):
        zx = col_x[c_i]
        accent_key = col.get("accent_key", "primary")
        draw_macro_zone(ax, zx, zone_y, col_w, zone_h, col.get("zone_title", ""), theme, accent_key=accent_key)
        cards = col.get("cards", [])
        for r_i, card in enumerate(cards[:3]):
            cx = zx + 0.7
            box = draw_modern_card(
                ax, cx, 0, card_w,
                title=card.get("title", ""),
                bullets=card.get("bullets", []),
                theme=theme,
                accent_key=card.get("accent_key", accent_key),
                badge_text=card.get("badge", card.get("badge_text")),
                fixed_height=row_heights[r_i],
                top_y=row_tops[r_i],
                fig_width_in=fig_w, fig_height_in=fig_h,
                font_pt=card.get("font_pt", eff_font_pt),
                title_pt=card.get("title_pt", title_pt),
                badge_pt=card.get("badge_pt", badge_pt),
                line_spacing=card.get("line_spacing", eff_line_spacing),
                slot_pad=card.get("slot_pad", eff_slot_pad),
                force_height=force_shrink,
            )
            grid_boxes[c_i][r_i] = box

    if horizontal_links:
        for (c1, r1), (c2, r2), lbl, acc in horizontal_links:
            b1, b2 = grid_boxes[c1][r1], grid_boxes[c2][r2]
            if b1 and b2:
                p0 = box_edge_point(b1, "right", pad=0.22, frac=0.5, ax=ax)
                p1 = box_edge_point(b2, "left", pad=0.22, frac=0.5, ax=ax)
                draw_labeled_arrow(ax, p0, p1, label_text=lbl, theme=theme,
                                   accent_key=acc or "primary", rad=0.0, font_pt=pill_pt)

    if vertical_links:
        for c_i, r1, r2, lbl, acc in vertical_links:
            b1, b2 = grid_boxes[c_i][r1], grid_boxes[c_i][r2]
            if b1 and b2:
                p0 = box_edge_point(b1, "bottom", pad=0.22, frac=0.5, ax=ax)
                p1 = box_edge_point(b2, "top", pad=0.22, frac=0.5, ax=ax)
                draw_labeled_arrow(ax, p0, p1, label_text=lbl, theme=theme,
                                   accent_key=acc or "primary", rad=0.0, font_pt=pill_pt)

    return grid_boxes


def draw_feedback_loop_pair(
    ax, left_box, right_box, top_loop_label, bottom_loop_label,
    theme=None, top_accent="primary", bottom_accent="success",
    rad=-0.34, font_pt=13.4, box_pad=0.22
):
    """
    T3 Helper: Connects two central system boxes with a symmetric upper & lower feedback loop
    using FancyBboxPatch pad-compensated anchors and true quadratic Bezier apex pill centering.
    Returns (top_apex_y, bot_apex_y).
    """
    if theme is None:
        theme = THEMES["swiss_editorial"]
    _, _, _, _, _, scale_y = get_canvas_metrics(ax=ax)
    lx, ly, lw, lh = left_box
    rx, ry, rw, rh = right_box

    p_top_start = (lx + lw * 0.72, ly + lh + box_pad * scale_y)
    p_top_end = (rx + rw * 0.28, ry + rh + box_pad * scale_y)
    top_apex_y = p_top_start[1] - 0.5 * rad * (p_top_end[0] - p_top_start[0])
    draw_labeled_arrow(
        ax, p_top_start, p_top_end, label_text=top_loop_label,
        theme=theme, accent_key=top_accent, rad=rad, font_pt=font_pt
    )

    p_bot_start = (rx + rw * 0.28, ry - box_pad * scale_y)
    p_bot_end = (lx + lw * 0.72, ly - box_pad * scale_y)
    bot_apex_y = p_bot_start[1] - 0.5 * rad * (p_bot_end[0] - p_bot_start[0])
    draw_labeled_arrow(
        ax, p_bot_start, p_bot_end, label_text=bottom_loop_label,
        theme=theme, accent_key=bottom_accent, rad=rad, font_pt=font_pt
    )
    return top_apex_y, bot_apex_y


def draw_2x2_matrix_quadrants(
    ax, x_axis_label, y_axis_label, quadrants_spec,
    theme=None, fig_width_in=None, font_pt=16.2, title_pt=17.2, badge_pt=13.6
):
    """
    T4 Helper: Draws an orthogonal 2x2 strategic quadrant matrix on the 0-100 canvas
    with a widened center corridor (>= 6.4 X-units) and high-legibility typography.
    Returns list of 4 drawn card bounding boxes.
    """
    if theme is None:
        theme = THEMES["swiss_editorial"]
    fig_w, fig_h, _px, pt_per_y, _sx, scale_y = get_canvas_metrics(ax=ax, fig_width_in=fig_width_in)
    zone_bot = (11.709 + 88.349 + 14.902) / pt_per_y
    zone_top = 100.0 - (98.994 + 13.840) / pt_per_y
    cx = 50.0
    cy = (zone_bot + zone_top) / 2.0
    v_gap = 2.6 * scale_y
    q_h = max(12.0, (zone_top - zone_bot - v_gap) / 2.0)
    top_qy = zone_bot + q_h + v_gap

    ax.annotate(
        "", xy=(97.5, cy), xytext=(2.5, cy),
        arrowprops=dict(arrowstyle="->,head_width=0.5,head_length=0.7", lw=2.2, color=theme["muted_ink"]),
        zorder=2
    )
    ax.annotate(
        "", xy=(cx, zone_top + 0.2 * scale_y), xytext=(cx, zone_bot - 0.2 * scale_y),
        arrowprops=dict(arrowstyle="->,head_width=0.5,head_length=0.7", lw=2.2, color=theme["muted_ink"]),
        zorder=2
    )
    ax.text(
        97.2, cy + 1.1 * scale_y, sanitize_cjk_glyphs(x_axis_label),
        fontsize=13.6, fontweight="bold", color=theme["text_title"], ha="right", va="bottom", zorder=5,
        bbox=dict(boxstyle="round,pad=0.22,rounding_size=0.4", facecolor="#FFFFFF", edgecolor=theme["card_border"])
    )
    ax.text(
        cx + 0.9, zone_top - 0.1 * scale_y, sanitize_cjk_glyphs(y_axis_label),
        fontsize=13.6, fontweight="bold", color=theme["text_title"], ha="left", va="top", zorder=5,
        bbox=dict(boxstyle="round,pad=0.22,rounding_size=0.4", facecolor="#FFFFFF", edgecolor=theme["card_border"])
    )

    q_coords = [
        (0.9, top_qy, 45.8, q_h),   # Top-Left (corridor 46.7..53.3 = 6.6 X-units)
        (53.3, top_qy, 45.8, q_h),  # Top-Right
        (0.9, zone_bot, 45.8, q_h), # Bottom-Left
        (53.3, zone_bot, 45.8, q_h),# Bottom-Right
    ]
    drawn_boxes = []
    for idx, q in enumerate(quadrants_spec[:4]):
        qx, qy, qw, qh = q_coords[idx]
        acc = q.get("accent_key", "primary")
        draw_macro_zone(ax, qx, qy, qw, qh, q.get("zone_title", ""), theme,
                        accent_key=acc, is_dashed=q.get("is_dashed", False))
        card = q.get("card", {})
        c_top = qy + qh - 3.45 * scale_y
        c_h = qh - 4.45 * scale_y
        c_box = draw_modern_card(
            ax, qx + 0.8, 0, qw - 1.6,
            title=card.get("title", ""),
            bullets=card.get("bullets", []),
            theme=theme,
            accent_key=card.get("accent_key", acc),
            badge_text=card.get("badge", card.get("badge_text")),
            fixed_height=c_h,
            top_y=c_top,
            fig_width_in=fig_w, fig_height_in=fig_h,
            font_pt=card.get("font_pt", font_pt),
            title_pt=card.get("title_pt", title_pt),
            badge_pt=card.get("badge_pt", badge_pt),
        )
        drawn_boxes.append(c_box)
    return drawn_boxes


def draw_canvas_header_and_footer(
    ax, title, subtitle, takeaway_title, takeaway_body=None, theme=None, takeaway_lines=None,
    title_pt=25.5, subtitle_pt=14.8, banner_title_pt=16.0, banner_body_pt=14.6
):
    """
    Draws the standardized Swiss-grid header and full-width bottom synthesis banner,
    calibrated to exact figure physical points so spacing remains crisp across adaptive heights.
    """
    if theme is None:
        theme = THEMES["swiss_editorial"]
    _, _, FancyBboxPatch, _, _ = _get_mpl()
    if takeaway_body is None and takeaway_lines is not None:
        takeaway_body = takeaway_lines

    _, _, pt_per_x, pt_per_y, _, _ = get_canvas_metrics(ax=ax)

    title_y = 100.0 - 25.547 / pt_per_y
    subtitle_y = 100.0 - 72.382 / pt_per_y
    div_top_y = 100.0 - 98.994 / pt_per_y

    ax.text(
        2.0, title_y, sanitize_cjk_glyphs(title),
        fontsize=title_pt, fontweight="bold", color=theme["text_title"],
        ha="left", va="top", zorder=4
    )
    ax.text(
        2.0, subtitle_y, sanitize_cjk_glyphs(subtitle),
        fontsize=subtitle_pt, fontweight="bold", color=theme["muted_ink"],
        ha="left", va="top", zorder=4
    )
    ax.plot([2.0, 98.0], [div_top_y, div_top_y], color=theme["card_border"], lw=1.4, zorder=2)

    banner_y = 11.709 / pt_per_y
    banner_h = 88.349 / pt_per_y
    banner = FancyBboxPatch(
        (2.0, banner_y), 96.0, banner_h,
        boxstyle="round,pad=0.28,rounding_size=0.9",
        facecolor=theme["hub_bg"], edgecolor=theme["hub_border"],
        linewidth=2.0, zorder=3
    )
    ax.add_patch(banner)
    ax.text(
        3.6, banner_y + banner_h - 15.967 / pt_per_y, sanitize_cjk_glyphs(takeaway_title),
        fontsize=banner_title_pt, fontweight="bold", color=theme["hub_sub"],
        ha="left", va="center", zorder=4
    )
    div_y = banner_y + banner_h - 31.401 / pt_per_y
    ax.plot([3.6, 96.4], [div_y, div_y], color=theme["hub_border"], lw=0.9, alpha=0.5, zorder=3.5)

    if isinstance(takeaway_body, (list, tuple)):
        wrapped = [sanitize_cjk_glyphs(str(line)) for line in takeaway_body]
    else:
        max_em = (92.8 * pt_per_x) / (banner_body_pt * 1.03)
        wrapped = wrap_cjk_text(str(takeaway_body or ""), max_em_width=max_em, hanging_indent="")

    body_mid = (banner_y + div_y) / 2.0
    step_y = (banner_body_pt * 1.42) / pt_per_y
    start_y = body_mid + ((len(wrapped) - 1) * step_y) / 2.0
    for idx, line in enumerate(wrapped):
        ax.text(
            3.6, start_y - idx * step_y, line,
            fontsize=banner_body_pt, color=theme["hub_text"],
            ha="left", va="center", zorder=4
        )


def setup_publication_canvas(figsize=(DEFAULT_FIG_W, DEFAULT_FIG_H), dpi=240, theme="swiss_editorial"):
    """
    Creates a standardized 0-100 coordinate publication canvas with configured CJK fonts.
    Default is compact high-legibility 23.8" x 15.4" (supports adaptive height 12.6"-15.4").
    Returns (fig, ax, theme_dict).
    """
    plt, _, _, _, _ = _get_mpl()
    configure_cjk_fonts()
    theme_dict = resolve_diagram_theme(theme)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.patch.set_facecolor(theme_dict["canvas_bg"])
    ax.set_facecolor(theme_dict["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax, theme_dict


def save_publication_figure(fig, output_path, theme=None, dpi=240):
    """Saves high-DPI lossless PNG figure for razor-sharp CJK text."""
    plt, _, _, _, _ = _get_mpl()
    theme_dict = resolve_diagram_theme(theme) if theme is not None else THEMES["swiss_editorial"]
    plt.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02)
    fig.savefig(
        output_path,
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=0.3,
        facecolor=theme_dict["canvas_bg"]
    )
    plt.close(fig)
    print(f"[OK] Saved publication-grade diagram: {output_path} (Theme: {theme_dict['name']}, DPI: {dpi})")


# ==============================================================================
# 5. A4-PORTRAIT-NATIVE LIGHTWEIGHT DIAGRAM HELPERS (For Format B PDF Reports)
# ==============================================================================
def setup_a4_portrait_canvas(height_in=2.30, dpi=300, theme="swiss_editorial"):
    """
    Creates an A4-portrait-native lightweight diagram canvas (7.44" = 189mm printable width)
    at 300 DPI so embedded Format B architecture/flow diagrams render at true 8.5-10.8pt
    with zero micro-shrinking and zero landscape page disruption.
    Returns (fig, ax, theme_dict).
    """
    plt, _, _, _, _ = _get_mpl()
    configure_cjk_fonts()
    theme_dict = resolve_diagram_theme(theme)
    fig, ax = plt.subplots(figsize=(A4_PORTRAIT_WIDTH_IN, float(height_in)), dpi=dpi)
    fig.patch.set_facecolor(theme_dict["canvas_bg"])
    ax.set_facecolor(theme_dict["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax, theme_dict


def draw_a4_node_box(
    ax, x, y, w, h, badge, title, lines=None, theme=None, accent_key="primary",
    badge_pt=8.8, title_pt=10.2, line_pt=8.4
):
    """
    Draws a lightweight keyword node box sized natively for A4 portrait (7.44" width).
    Header band height adapts proportionally to box height `h` and canvas height.
    Returns (x, y, w, h).
    """
    _, _, FancyBboxPatch, _, _ = _get_mpl()
    if theme is None:
        theme = THEMES["swiss_editorial"]
    _, _, _, pt_per_y, _, _ = get_canvas_metrics(ax=ax)
    acc = theme["accents"].get(accent_key, theme["accents"]["primary"])
    col = acc["main"]
    tint = acc["pill_bg"]

    band_h = min(h * 0.36, max(11.0, 15.5 / max(1.0, pt_per_y)))
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.35,rounding_size=1.4",
        facecolor=theme["card_bg"], edgecolor="none", zorder=3
    ))
    if badge:
        ax.add_patch(FancyBboxPatch(
            (x + 0.15, y + h - band_h), w - 0.30, band_h - 0.15,
            boxstyle="round,pad=0.20,rounding_size=1.1",
            facecolor=tint, edgecolor="none", zorder=3.1
        ))
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.35,rounding_size=1.4",
        facecolor="none", edgecolor=col, linewidth=1.55, zorder=3.4
    ))
    if badge:
        ax.text(
            x + w / 2.0, y + h - band_h * 0.48, sanitize_cjk_glyphs(badge),
            fontsize=badge_pt, fontweight="bold", color=col,
            ha="center", va="center", zorder=4
        )
    title_y = y + (h - band_h) * 0.65 if lines else y + (h - band_h) * 0.50
    if not badge:
        title_y = y + h * 0.68 if lines else y + h * 0.50
    ax.text(
        x + w / 2.0, title_y, sanitize_cjk_glyphs(title),
        fontsize=title_pt, fontweight="bold", color=theme["text_title"],
        ha="center", va="center", zorder=4
    )
    if lines:
        line_list = lines if isinstance(lines, (list, tuple)) else [str(lines)]
        body_span = (title_y - y) * 0.72
        step = min(13.0, body_span / max(1, len(line_list))) if len(line_list) > 1 else 0.0
        sub_y0 = y + body_span * 0.58 + ((len(line_list) - 1) * step) / 2.0
        for i, line in enumerate(line_list):
            ax.text(
                x + w / 2.0, sub_y0 - i * step, sanitize_cjk_glyphs(line),
                fontsize=line_pt, color=theme["text_body"],
                ha="center", va="center", zorder=4
            )
    return (x, y, w, h)


def draw_a4_arrow(
    ax, p0, p1, label=None, theme=None, accent_key="primary",
    rad=0.0, label_dy=8.5, font_pt=8.0
):
    """
    Draws a crisp directional flow arrow + concise pill label on an A4-portrait-native canvas.
    """
    _, _, _, FancyArrowPatch, _ = _get_mpl()
    if theme is None:
        theme = THEMES["swiss_editorial"]
    col = theme["accents"].get(accent_key, theme["accents"]["primary"])["main"]
    ax.add_patch(FancyArrowPatch(
        p0, p1,
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="simple,head_length=5.5,head_width=5.5,tail_width=1.8",
        color=col, alpha=0.9, zorder=4
    ))
    if label:
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        mx = (p0[0] + p1[0]) / 2.0 + 0.5 * rad * dy
        my = (p0[1] + p1[1]) / 2.0 - 0.5 * rad * dx + (label_dy if rad == 0.0 else 0.0)
        ax.text(
            mx, my, sanitize_cjk_glyphs(label),
            fontsize=font_pt, fontweight="bold", color=col,
            ha="center", va="center", zorder=5,
            bbox=dict(boxstyle="round,pad=0.18,rounding_size=0.4", facecolor="#FFFFFF", edgecolor=col, lw=0.9)
        )


def save_a4_portrait_figure(fig, output_path, theme=None, dpi=300):
    """Saves an A4-portrait-native (7.44") lightweight diagram at 300 DPI."""
    plt, _, _, _, _ = _get_mpl()
    theme_dict = resolve_diagram_theme(theme) if theme is not None else THEMES["swiss_editorial"]
    plt.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02)
    fig.savefig(
        output_path,
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=0.08,
        facecolor=theme_dict["canvas_bg"]
    )
    plt.close(fig)
    print(f"[OK] Saved A4-portrait diagram: {output_path} (Theme: {theme_dict['name']}, DPI: {dpi})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scientific Visual Knowledge Diagram Engine")
    parser.add_argument("--theme", choices=list(THEMES.keys()), default="swiss_editorial",
                        help="Scientific color theme palette")
    parser.add_argument("--dpi", type=int, default=240, help="Output DPI (220-300)")
    args = parser.parse_args()
    configure_cjk_fonts()
    print(f"Visual Diagram Engine Ready. Default Canvas: {DEFAULT_FIG_W}\"x{DEFAULT_FIG_H}\". Available Themes: {list(THEMES.keys())}")

