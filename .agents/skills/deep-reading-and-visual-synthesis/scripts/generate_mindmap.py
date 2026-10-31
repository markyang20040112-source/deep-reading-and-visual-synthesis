"""
generate_mindmap.py
Scientific Visual Knowledge Diagram & Concept Map Engine (Matplotlib Vector Renderer).

Grounded in 15+ empirical design & cognitive science studies:
- Cowan (2001): 4±1 Working Memory Chunking Limit
- Palmer (1992, 1999): Modern Gestalt Common Region & Element Connectedness
- Reber, Schwarz, & Winkielman (2004): Processing Fluency Theory of Aesthetic Pleasure
- Müller-Brockmann (1981): 12-Column Swiss Grid & Active Negative Space (>=35%)
- Bringhurst (2012) & W3C CLREQ: CJK Typographic Measure (18-22 Hanzi) & Leading (1.65x)
- Crameri et al. (2020), Okabe & Ito (2008), Knaflic (2015): 75-20-5 Preattentive Color Science
- Novak & Cañas (2008): Concept Maps with Relational Linking Phrase Pills
- Purchase (1997): Zero Edge Crossings & Orthogonal Symmetry
- Tufte (1990): Layering and Separation (Z-order stratification)
"""

import argparse
import re
import unicodedata
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path

NO_START_CHARS = set("），。、；：！？）」』】〉》. , ; : ! ? ) ] }")
TOKEN_RE = re.compile(r"\d+(?:,\d+)+\+?|[A-Za-z0-9_.\-+%/]+|.")


def sanitize_cjk_glyphs(text):
    """Replaces glyphs missing in Windows Microsoft JhengHei (e.g. U+2794, U+2194, U+21C4) with safe equivalents."""
    if not text:
        return text
    return (
        text.replace("➔", "→")
            .replace("➜", "→")
            .replace("↔", "←→")
            .replace("⇄", "←→")
    )


# ==============================================================================
# 1. CURATED SCIENTIFIC THEME PALETTES (75-20-5 Preattentive Allocation)
# ==============================================================================
THEMES = {
    "swiss_editorial": {
        "name": "Swiss Editorial (Default)",
        "canvas_bg": "#F8FAFC",
        "zone_bg": "#F1F5F9",
        "zone_border": "#CBD5E1",
        "card_bg": "#FFFFFF",
        "card_border": "#CBD5E1",
        "shadow": "#0F172A",
        "text_title": "#0F172A",
        "text_body": "#334155",
        "muted_ink": "#64748B",
        "edge_line": "#94A3B8",
        "hub_bg": "#0F172A",
        "hub_border": "#38BDF8",
        "hub_text": "#FFFFFF",
        "hub_sub": "#38BDF8",
        "accents": {
            "primary": {"main": "#1E40AF", "pill_bg": "#EFF6FF"},   # Core Theory
            "danger":  {"main": "#BE123C", "pill_bg": "#FFF1F2"},   # Pain / Risk
            "success": {"main": "#047857", "pill_bg": "#ECFDF5"},   # Solution / Action
            "warn":    {"main": "#B45309", "pill_bg": "#FFFBEB"},   # Catalyst / Assumption
            "synth":   {"main": "#5B21B6", "pill_bg": "#F5F3FF"},   # Deep Synthesis / Schema
        }
    },
    "mckinsey_executive": {
        "name": "McKinsey Executive",
        "canvas_bg": "#F4F6F9",
        "zone_bg": "#EBF0F5",
        "zone_border": "#C5D1E0",
        "card_bg": "#FFFFFF",
        "card_border": "#D1D9E6",
        "shadow": "#0A192F",
        "text_title": "#0A192F",
        "text_body": "#2D3748",
        "muted_ink": "#5A6A85",
        "edge_line": "#8C9BAE",
        "hub_bg": "#002244",
        "hub_border": "#0077B6",
        "hub_text": "#FFFFFF",
        "hub_sub": "#90E0EF",
        "accents": {
            "primary": {"main": "#003366", "pill_bg": "#E6F0FA"},
            "danger":  {"main": "#B91C1C", "pill_bg": "#FEF2F2"},
            "success": {"main": "#0D9488", "pill_bg": "#F0FDFA"},
            "warn":    {"main": "#C58B00", "pill_bg": "#FEFCE8"},
            "synth":   {"main": "#4338CA", "pill_bg": "#EEF2FF"},
        }
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
            "primary": {"main": "#0072B2", "pill_bg": "#EBF5FB"},   # Okabe Blue
            "danger":  {"main": "#D55E00", "pill_bg": "#FEF3EB"},   # Okabe Vermilion
            "success": {"main": "#009E73", "pill_bg": "#E8F8F5"},   # Okabe Bluish Green
            "warn":    {"main": "#E69F00", "pill_bg": "#FEF9E7"},   # Okabe Orange
            "synth":   {"main": "#CC79A7", "pill_bg": "#FDEDEC"},   # Okabe Reddish Purple
        }
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
        }
    }
}


# ==============================================================================
# 2. CJK FONT & AUTO-WRAPPING ERGONOMICS ENGINE (W3C CLREQ & Bringhurst)
# ==============================================================================
def configure_cjk_fonts():
    """Configures cross-platform Traditional Chinese (CJK) font fallbacks."""
    cjk_fonts = [
        "Microsoft JhengHei",      # Windows Traditional Chinese
        "PingFang TC",             # macOS Traditional Chinese
        "Noto Sans CJK TC",        # Linux / Google Noto CJK
        "Source Han Sans TC",      # Adobe Source Han Sans
        "Heiti TC",
        "WenQuanYi Micro Hei",
        "Arial Unicode MS",
        "sans-serif"
    ]
    plt.rcParams["font.sans-serif"] = cjk_fonts
    plt.rcParams["axes.unicode_minus"] = False


def char_visual_width(ch):
    """Returns approximate visual width in CJK em-units (Hanzi=1.0, ASCII=0.53)."""
    eaw = unicodedata.east_asian_width(ch)
    return 1.0 if eaw in ("W", "F") else 0.53


def token_visual_width(tok):
    return sum(char_visual_width(c) for c in tok)


def compute_dynamic_max_em(card_width, fig_width_in=28.0, font_pt=9.6, pad_units=2.1):
    """
    Dynamically computes max_em_width from the card's actual physical width on the figure
    so wrapped text fills 88%–92% of the card width with zero right-side empty gap.
    """
    usable_width_units = max(8.0, card_width - pad_units)
    usable_points = (usable_width_units / 100.0) * fig_width_in * 72.0
    return usable_points / (font_pt * 1.03)


def wrap_cjk_text(text, max_em_width=None, hanging_indent="   ", card_width=28.0, fig_width_in=28.0, font_pt=9.6):
    """
    Wraps a single bullet string according to W3C CLREQ visual measure limits,
    keeping English words/numbers intact and enforcing Kinsoku Shori (no closing punctuation at line start).
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
    return lines


def prepare_card_lines(bullets, max_em_width=None, card_width=28.0, fig_width_in=28.0, font_pt=9.6):
    """Expands a list of bullet strings into wrapped visual lines."""
    all_lines = []
    for b in bullets:
        wrapped = wrap_cjk_text(b, max_em_width=max_em_width, card_width=card_width, fig_width_in=fig_width_in, font_pt=font_pt)
        all_lines.extend(wrapped)
    return all_lines


def compute_card_height(bullets, max_em_width=None, line_Step=1.72, header_pad=4.2, bottom_pad=1.5,
                        card_width=28.0, fig_width_in=28.0, font_pt=9.6):
    """
    Mathematically computes the exact card height in 0-100 canvas coordinates
    so text NEVER overflows or leaves awkward right-side whitespace.
    """
    wrapped_lines = prepare_card_lines(bullets, max_em_width=max_em_width, card_width=card_width, fig_width_in=fig_width_in, font_pt=font_pt)
    return header_pad + len(wrapped_lines) * line_Step + bottom_pad, wrapped_lines


# ==============================================================================
# 3. LAYERED GRAPHICAL PRIMITIVES (Palmer, Tufte, Novak, Purchase)
# ==============================================================================
def draw_macro_zone(ax, x, y, width, height, zone_title, theme, is_dashed=False):
    """
    Z-Order 1: Draws a Palmer (1992) 'Common Region' macro container box
    to group related sub-cards and keep top-level chunks within Cowan's 4±1 limit.
    """
    zone_box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.3,rounding_size=1.4",
        linewidth=1.5 if not is_dashed else 1.8,
        edgecolor=theme["zone_border"],
        facecolor=theme["zone_bg"],
        linestyle="--" if is_dashed else "-",
        alpha=0.85,
        zorder=1
    )
    ax.add_patch(zone_box)
    if zone_title:
        ax.text(
            x + 1.2, y + height - 1.1, zone_title,
            fontsize=11.5, fontweight="bold",
            color=theme["muted_ink"], va="top", ha="left", zorder=2
        )


def draw_modern_card(ax, x, y, width, title, bullets, theme,
                     accent_key="primary", badge_text=None,
                     max_em_width=None, is_dashed=False, fixed_height=None,
                     fig_width_in=28.0, font_pt=9.6):
    """
    Z-Order 3-4: Draws a Tufte-layered, Swiss-grid aligned card with:
    - Subtle drop shadow (figure-ground separation)
    - Pure neutral card surface (75% receding base)
    - 4pt Left Semantic Accent Strip & optional Badge Pill (5% preattentive focal cue)
    - Dynamic width-calibrated CJK typography (fills 88%-92% of card width, zero right-side gap)
    Returns (x, y, width, height) for exact connector anchoring.
    """
    title = sanitize_cjk_glyphs(title)
    badge_text = sanitize_cjk_glyphs(badge_text)
    accent = theme["accents"].get(accent_key, theme["accents"]["primary"])
    accent_color = accent["main"]
    pill_bg = accent["pill_bg"]

    calc_h, wrapped_lines = compute_card_height(
        bullets, max_em_width=max_em_width, card_width=width, fig_width_in=fig_width_in, font_pt=font_pt
    )
    height = max(fixed_height, calc_h) if fixed_height else calc_h

    # 1. Subtle Elevation Shadow (zorder=2.5)
    shadow_box = FancyBboxPatch(
        (x + 0.22, y - 0.32), width, height,
        boxstyle="round,pad=0.2,rounding_size=1.0",
        linewidth=0, facecolor=theme["shadow"], alpha=0.045, zorder=2.5
    )
    ax.add_patch(shadow_box)

    # 2. Clean Neutral Card Surface (zorder=3)
    card_box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.2,rounding_size=1.0",
        linewidth=1.3 if not is_dashed else 1.8,
        edgecolor=theme["card_border"] if not is_dashed else accent_color,
        facecolor=theme["card_bg"],
        linestyle="--" if is_dashed else "-",
        zorder=3
    )
    ax.add_patch(card_box)

    # 3. Left Preattentive Semantic Accent Strip (zorder=3.5)
    strip_w = 0.52
    accent_strip = FancyBboxPatch(
        (x, y + 0.4), strip_w, height - 0.8,
        boxstyle="round,pad=0.05,rounding_size=0.3",
        linewidth=0, facecolor=accent_color, zorder=3.5
    )
    ax.add_patch(accent_strip)

    # 4. Header Badge Pill & Card Title (zorder=4)
    text_x = x + strip_w + 0.85
    header_y = y + height - 1.35

    if badge_text:
        ax.text(
            text_x, header_y, f" {badge_text} ",
            fontsize=8.8, fontweight="bold", color=accent_color,
            va="top", ha="left", zorder=4,
            bbox=dict(boxstyle="round,pad=0.22,rounding_size=0.4",
                      facecolor=pill_bg, edgecolor=accent_color, lw=0.8)
        )
        title_offset_x = text_x + sum(char_visual_width(c) for c in badge_text) * 0.68 + 1.4
        ax.text(
            title_offset_x, header_y - 0.05, title,
            fontsize=12.5, fontweight="bold", color=theme["text_title"],
            va="top", ha="left", zorder=4
        )
    else:
        ax.text(
            text_x, header_y, title,
            fontsize=12.8, fontweight="bold", color=accent_color,
            va="top", ha="left", zorder=4
        )

    # Subtle header divider rule
    divider_y = y + height - 3.1
    ax.plot(
        [text_x, x + width - 0.8], [divider_y, divider_y],
        color=theme["card_border"], linewidth=0.7, alpha=0.7, zorder=3.5
    )

    # 5. Wrapped Body Lines (W3C CLREQ Leading)
    line_y = y + height - 3.85
    for line in wrapped_lines:
        ax.text(
            text_x, line_y, line,
            fontsize=9.6, color=theme["text_body"],
            va="top", ha="left", zorder=4
        )
        line_y -= 1.72

    return (x, y, width, height)


def draw_labeled_bezier(ax, p0, p3, label_text=None, theme=None,
                        accent_key=None, width=1.9, alpha=0.82):
    """
    Z-Order 2 (curve) & Z-Order 5 (Novak Relational Pill Label):
    Draws a smooth zero-crossing cubic Bezier connector with an optional
    Novak & Cañas (2008) relational linking phrase pill at its midpoint.
    """
    if theme is None:
        theme = THEMES["swiss_editorial"]

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
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    path = Path(verts, codes)
    patch = patches.PathPatch(
        path, facecolor="none", edgecolor=line_color,
        linewidth=width, alpha=alpha, zorder=2
    )
    ax.add_patch(patch)

    # Midpoint of cubic Bezier at t=0.5: B(0.5) = 0.125*P0 + 0.375*P1 + 0.375*P2 + 0.125*P3
    if label_text:
        mx = 0.125 * x0 + 0.375 * p1[0] + 0.375 * p2[0] + 0.125 * x3
        my = 0.125 * y0 + 0.375 * p1[1] + 0.375 * p2[1] + 0.125 * y3
        ax.text(
            mx, my, f" {label_text} ",
            fontsize=8.5, fontweight="bold",
            color=line_color if accent_key else theme["text_body"],
            ha="center", va="center", zorder=5,
            bbox=dict(
                boxstyle="round,pad=0.25,rounding_size=0.5",
                facecolor=pill_bg, edgecolor=line_color, lw=1.0, alpha=0.96
            )
        )


def draw_labeled_arrow(ax, p0, p1, label_text=None, theme=None,
                       accent_key="primary", rad=0.0):
    """Draws a directed causal arrow with a Novak relational pill label."""
    if theme is None:
        theme = THEMES["swiss_editorial"]
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
        mx = (p0[0] + p1[0]) / 2.0
        my = (p0[1] + p1[1]) / 2.0
        ax.text(
            mx, my, f" {label_text} ",
            fontsize=8.6, fontweight="bold", color=color,
            ha="center", va="center", zorder=5,
            bbox=dict(
                boxstyle="round,pad=0.25,rounding_size=0.5",
                facecolor="#FFFFFF", edgecolor=color, lw=1.1
            )
        )


def draw_canvas_header_and_footer(ax, title, subtitle, takeaway_title, takeaway_body, theme):
    """Draws the standardized Swiss-grid header and bottom synthesis banner."""
    # Top Header
    ax.text(
        4.0, 96.8, title,
        fontsize=22, fontweight="bold", color=theme["text_title"],
        ha="left", va="top", zorder=4
    )
    ax.text(
        4.0, 93.2, subtitle,
        fontsize=11.5, color=theme["muted_ink"],
        ha="left", va="top", zorder=4
    )
    ax.plot([4.0, 96.0], [91.2, 91.2], color=theme["card_border"], lw=1.2, zorder=2)

    # Bottom Takeaway Banner
    banner = FancyBboxPatch(
        (4.0, 2.5), 92.0, 7.8,
        boxstyle="round,pad=0.3,rounding_size=1.0",
        facecolor=theme["hub_bg"], edgecolor=theme["hub_border"],
        linewidth=1.6, zorder=3
    )
    ax.add_patch(banner)
    ax.text(
        6.0, 8.8, takeaway_title,
        fontsize=12.5, fontweight="bold", color=theme["hub_sub"],
        ha="left", va="top", zorder=4
    )
    ax.text(
        6.0, 5.8, takeaway_body,
        fontsize=9.8, color=theme["hub_text"],
        ha="left", va="top", zorder=4
    )


def save_publication_figure(fig, output_path, theme, dpi=240):
    """Saves high-DPI figure with zero chroma subsampling for razor-sharp CJK text."""
    plt.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02)
    fig.savefig(
        output_path,
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=0.3,
        facecolor=theme["canvas_bg"],
        pil_kwargs={"quality": 98, "subsampling": 0}
    )
    plt.close(fig)
    print(f"[OK] Saved publication-grade diagram: {output_path} (Theme: {theme['name']}, DPI: {dpi})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scientific Visual Knowledge Diagram Engine")
    parser.add_argument("--theme", choices=list(THEMES.keys()), default="swiss_editorial",
                        help="Scientific color theme palette")
    parser.add_argument("--dpi", type=int, default=240, help="Output DPI (220-300)")
    args = parser.parse_args()
    configure_cjk_fonts()
    print(f"Visual Diagram Engine Ready. Available Themes: {list(THEMES.keys())}")
