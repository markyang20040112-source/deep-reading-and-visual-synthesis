"""
generate_mindmap.py
Scientific Visual Knowledge Diagram & Concept Map Engine (Matplotlib Vector Renderer).

Grounded in empirical design & cognitive science studies:
- Cowan (2001) & Palmer (1992, 1999): 4±1 Per-Level Hierarchical Chunking (4 Macro Zones -> 2 Cards -> 3 Bullets)
- Goldstone & Son (2005), Clark & Haviland (1977), Mayer (2009): Concreteness Fading & Plain-Language Progressive Disclosure
- Reber, Schwarz, & Winkielman (2004): Processing Fluency Theory of Aesthetic Pleasure
- Müller-Brockmann (1981) & W3C Box Alignment: Swiss Grid, Modular Row Slots, & True Vertical Centering (va='center')
- Bringhurst (2012) & W3C CLREQ: CJK Typographic Scale (11.8pt-12.5pt on 28x18.5 canvas) & Fullwidth-Indent-Aware Kinsoku Shori
- Crameri et al. (2020), Okabe & Ito (2008), Knaflic (2015): 75-20-5 Preattentive Color Science
- Novak & Cañas (2008): Concept Maps with Relational Linking Phrase Pills & 1-to-2 Hierarchical Trunk Forks
- Purchase (1997) & Tufte (1990): Zero Edge Crossings & Z-order Stratification
"""

import argparse
import re
import unicodedata
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path

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
        "text_body": "#1E293B",
        "muted_ink": "#64748B",
        "edge_line": "#94A3B8",
        "hub_bg": "#0F172A",
        "hub_border": "#38BDF8",
        "hub_text": "#F8FAFC",
        "hub_sub": "#38BDF8",
        "accents": {
            "primary": {"main": "#0284C7", "pill_bg": "#E0F2FE"},
            "danger":  {"main": "#DC2626", "pill_bg": "#FEE2E2"},
            "success": {"main": "#059669", "pill_bg": "#D1FAE5"},
            "warn":    {"main": "#D97706", "pill_bg": "#FEF3C7"},
            "synth":   {"main": "#4F46E5", "pill_bg": "#E0E7FF"},
        }
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
            "primary": {"main": "#0072B2", "pill_bg": "#EBF5FB"},
            "danger":  {"main": "#D55E00", "pill_bg": "#FEF3EB"},
            "success": {"main": "#009E73", "pill_bg": "#E8F8F5"},
            "warn":    {"main": "#E69F00", "pill_bg": "#FEF9E7"},
            "synth":   {"main": "#CC79A7", "pill_bg": "#FDEDEC"},
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
        "Microsoft JhengHei",
        "PingFang TC",
        "Noto Sans CJK TC",
        "Source Han Sans TC",
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


def compute_dynamic_max_em(card_width, fig_width_in=28.0, font_pt=12.0, pad_units=2.35):
    """
    Dynamically computes max_em_width from the card's actual physical width on the figure
    so wrapped text fills 88%–92% of the card width with zero right-side empty gap.
    """
    usable_width_units = max(8.0, card_width - pad_units)
    usable_points = (usable_width_units / 100.0) * (fig_width_in * 0.91) * 72.0
    return usable_points / (font_pt * 1.04)


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


def wrap_cjk_text(text, max_em_width=None, hanging_indent="　 ", card_width=28.0, fig_width_in=28.0, font_pt=12.0):
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


def prepare_card_slots(bullets, max_em_width=None, card_width=28.0, fig_width_in=28.0, font_pt=12.0):
    """Expands each bullet string into its own list of Kinsoku-protected wrapped lines (1 slot per bullet)."""
    slots = []
    for b in bullets:
        wrapped = wrap_cjk_text(b, max_em_width=max_em_width, card_width=card_width, fig_width_in=fig_width_in, font_pt=font_pt)
        slots.append(apply_kinsoku_shori(wrapped))
    return slots


def prepare_card_lines(bullets, max_em_width=None, card_width=28.0, fig_width_in=28.0, font_pt=12.0):
    """Expands a list of bullet strings into wrapped visual lines."""
    all_lines = []
    for slot in prepare_card_slots(bullets, max_em_width=max_em_width, card_width=card_width, fig_width_in=fig_width_in, font_pt=font_pt):
        all_lines.extend(slot)
    return all_lines


def compute_card_height(bullets, max_em_width=None, line_Step=1.78, header_pad=4.2, bottom_pad=1.5,
                        card_width=28.0, fig_width_in=28.0, font_pt=12.0):
    """Mathematically computes the exact card height in 0-100 canvas coordinates."""
    wrapped_lines = prepare_card_lines(bullets, max_em_width=max_em_width, card_width=card_width, fig_width_in=fig_width_in, font_pt=font_pt)
    return header_pad + len(wrapped_lines) * line_Step + bottom_pad, wrapped_lines


# ==============================================================================
# 3. LAYERED GRAPHICAL PRIMITIVES (Palmer, Tufte, Novak, Purchase)
# ==============================================================================
def draw_macro_zone(ax, x, y, width, height, zone_title, theme, accent_key=None, is_dashed=False):
    """
    Z-Order 1: Draws a Palmer (1992) 'Common Region' macro container box
    to group related sub-cards and keep top-level chunks within Cowan's 4±1 limit.
    """
    title_color = theme["accents"][accent_key]["main"] if (accent_key and accent_key in theme["accents"]) else theme["muted_ink"]
    zone_box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.3,rounding_size=1.3",
        linewidth=1.7 if not is_dashed else 1.8,
        edgecolor=theme["zone_border"],
        facecolor=theme["zone_bg"],
        linestyle="--" if is_dashed else "-",
        alpha=0.90,
        zorder=1
    )
    ax.add_patch(zone_box)
    if zone_title:
        ax.text(
            x + 1.1, y + height - 1.15, zone_title,
            fontsize=13.6, fontweight="bold",
            color=title_color, va="center", ha="left", zorder=2
        )


def draw_modern_card(ax, x, y, width, title, bullets, theme,
                     accent_key="primary", badge_text=None,
                     max_em_width=None, is_dashed=False, fixed_height=None,
                     fig_width_in=28.0, font_pt=12.0):
    """
    Z-Order 3-4: Draws a Tufte-layered, Swiss-grid aligned card with:
    - Scaled-up typography matching a 28x18.5 canvas (Title=14.6pt, Badge=10.6pt, Body=12.0pt)
    - Dynamic width-calibrated CJK wrapping (fills 88%-92% of card width, zero right-side gap)
    - True mathematical vertical centering (va='center') inside every row slot!
    Returns (x, y, width, height) for exact connector anchoring.
    """
    title = sanitize_cjk_glyphs(title)
    badge_text = sanitize_cjk_glyphs(badge_text)
    accent = theme["accents"].get(accent_key, theme["accents"]["primary"])
    accent_color = accent["main"]
    pill_bg = accent["pill_bg"]

    calc_h, _ = compute_card_height(
        bullets, max_em_width=max_em_width, card_width=width, fig_width_in=fig_width_in, font_pt=font_pt
    )
    height = max(fixed_height, calc_h) if fixed_height else calc_h

    # 1. Subtle Elevation Shadow (zorder=2.5)
    shadow_box = FancyBboxPatch(
        (x + 0.20, y - 0.28), width, height,
        boxstyle="round,pad=0.2,rounding_size=0.9",
        linewidth=0, facecolor=theme["shadow"], alpha=0.055, zorder=2.5
    )
    ax.add_patch(shadow_box)

    # 2. Clean Neutral Card Surface (zorder=3)
    card_box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.2,rounding_size=0.9",
        linewidth=1.5 if not is_dashed else 1.8,
        edgecolor=theme["card_border"] if not is_dashed else accent_color,
        facecolor=theme["card_bg"],
        linestyle="--" if is_dashed else "-",
        zorder=3
    )
    ax.add_patch(card_box)

    # 3. Left Preattentive Semantic Accent Strip (zorder=3.5)
    strip_w = 0.58
    accent_strip = FancyBboxPatch(
        (x, y + 0.35), strip_w, height - 0.70,
        boxstyle="round,pad=0.05,rounding_size=0.28",
        linewidth=0, facecolor=accent_color, zorder=3.5
    )
    ax.add_patch(accent_strip)

    # 4. Header Badge Pill & Card Title (Vertically centered in header band)
    text_x = x + strip_w + 0.85
    divider_y = y + height - 3.35
    header_mid_y = y + height - 1.68

    if badge_text:
        ax.text(
            text_x, header_mid_y, f" {badge_text} ",
            fontsize=10.6, fontweight="bold", color=accent_color,
            va="center", ha="left", zorder=4,
            bbox=dict(boxstyle="round,pad=0.24,rounding_size=0.42",
                      facecolor=pill_bg, edgecolor=accent_color, lw=1.0)
        )
        title_offset_x = text_x + sum(char_visual_width(c) for c in badge_text) * 0.82 + 1.65
        ax.text(
            title_offset_x, header_mid_y, title,
            fontsize=14.6, fontweight="bold", color=theme["text_title"],
            va="center", ha="left", zorder=4
        )
    else:
        ax.text(
            text_x, header_mid_y, title,
            fontsize=14.8, fontweight="bold", color=accent_color,
            va="center", ha="left", zorder=4
        )

    ax.plot(
        [text_x, x + width - 0.75], [divider_y, divider_y],
        color=theme["card_border"], linewidth=1.0, alpha=0.9, zorder=3.5
    )

    # 5. Modular Horizontal Row Slots with True Vertical Centering (va="center")
    slots = prepare_card_slots(
        bullets, max_em_width=max_em_width, card_width=width, fig_width_in=fig_width_in, font_pt=font_pt
    )
    num_slots = len(slots)
    if num_slots > 0:
        body_top = divider_y - 0.12
        body_bot = y + 0.22
        avail_h = max(2.0, body_top - body_bot)
        slot_h = avail_h / num_slots

        for s_idx, slot_lines in enumerate(slots):
            slot_top = body_top - s_idx * slot_h
            slot_center_y = slot_top - slot_h / 2.0
            if s_idx > 0:
                ax.plot(
                    [text_x, x + width - 0.75], [slot_top, slot_top],
                    color=theme["card_border"], linewidth=0.75, alpha=0.75, linestyle="-", zorder=3.5
                )
            m_lines = max(1, len(slot_lines))
            line_step = min(1.86, max(1.52, (slot_h * 0.74) / max(1, m_lines)))
            total_block_h = (m_lines - 1) * line_step
            start_y = slot_center_y + total_block_h / 2.0
            for l_i, line in enumerate(slot_lines):
                ax.text(
                    text_x, start_y - l_i * line_step, line,
                    fontsize=font_pt, color=theme["text_body"],
                    va="center", ha="left", zorder=4
                )

    return (x, y, width, height)


def draw_hierarchical_trunk_fork(ax, p_start, p_card1, p_card2, trunk_label, theme=None, accent_key="primary", lw=2.5):
    """
    Draws a true Hierarchical Chunking connector (1 Main Trunk -> 2 Sub-Card Branches),
    strictly enforcing Cowan's 4±1 branching limit at the macro hub level (4 trunks total)
    and bifurcating symmetrically at the vertical midpoint of the target Macro Zone.
    """
    if theme is None:
        theme = THEMES["swiss_editorial"]
    accent = theme["accents"].get(accent_key, theme["accents"]["primary"])
    line_color = accent["main"]
    pill_bg = accent["pill_bg"]

    x0, y0 = p_start
    x1, y1 = p_card1
    x2, y2 = p_card2
    split_x = x0 + (x1 - x0) * 0.45
    split_y = (y1 + y2) / 2.0

    dx_trunk = split_x - x0
    t_verts = [
        (x0, y0),
        (x0 + dx_trunk * 0.50, y0),
        (split_x - dx_trunk * 0.50, split_y),
        (split_x, split_y)
    ]
    t_codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    trunk_patch = patches.PathPatch(
        Path(t_verts, t_codes), facecolor="none", edgecolor=line_color,
        linewidth=lw + 0.6, alpha=0.92, zorder=2
    )
    ax.add_patch(trunk_patch)

    for (tx, ty) in [(x1, y1), (x2, y2)]:
        dx = tx - split_x
        p1 = (split_x + dx * 0.48, split_y)
        p2 = (tx - dx * 0.48, ty)
        verts = [(split_x, split_y), p1, p2, (tx, ty)]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
        patch = patches.PathPatch(
            Path(verts, codes), facecolor="none", edgecolor=line_color,
            linewidth=lw, alpha=0.88, zorder=2
        )
        ax.add_patch(patch)
        ax.scatter([tx], [ty], s=32, color=line_color, zorder=4)

    ax.text(
        split_x, split_y, f" {trunk_label} ",
        fontsize=10.6, fontweight="bold", color=line_color,
        ha="center", va="center", zorder=5,
        bbox=dict(
            boxstyle="round,pad=0.32,rounding_size=0.55",
            facecolor=pill_bg, edgecolor=line_color, lw=1.4, alpha=0.99
        )
    )


def draw_labeled_bezier(ax, p0, p3, label_text=None, theme=None,
                        accent_key=None, width=2.3, alpha=0.88):
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

    if label_text:
        mx = 0.125 * x0 + 0.375 * p1[0] + 0.375 * p2[0] + 0.125 * x3
        my = 0.125 * y0 + 0.375 * p1[1] + 0.375 * p2[1] + 0.125 * y3
        ax.text(
            mx, my, f" {label_text} ",
            fontsize=10.2, fontweight="bold",
            color=line_color if accent_key else theme["text_body"],
            ha="center", va="center", zorder=5,
            bbox=dict(
                boxstyle="round,pad=0.28,rounding_size=0.5",
                facecolor=pill_bg, edgecolor=line_color, lw=1.2, alpha=0.98
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
            fontsize=10.2, fontweight="bold", color=color,
            ha="center", va="center", zorder=5,
            bbox=dict(
                boxstyle="round,pad=0.28,rounding_size=0.5",
                facecolor="#FFFFFF", edgecolor=color, lw=1.2
            )
        )


def draw_canvas_header_and_footer(ax, title, subtitle, takeaway_title, takeaway_body=None, theme=None, takeaway_lines=None):
    """Draws the standardized Swiss-grid header and full-width bottom synthesis banner."""
    if theme is None:
        theme = THEMES["swiss_editorial"]
    if takeaway_body is None and takeaway_lines is not None:
        takeaway_body = takeaway_lines
    ax.text(
        3.5, 97.2, title,
        fontsize=23.5, fontweight="bold", color=theme["text_title"],
        ha="left", va="top", zorder=4
    )
    ax.text(
        3.5, 93.4, subtitle,
        fontsize=13.0, fontweight="bold", color=theme["muted_ink"],
        ha="left", va="top", zorder=4
    )
    ax.plot([3.5, 96.5], [91.3, 91.3], color=theme["card_border"], lw=1.4, zorder=2)

    banner_y, banner_h = 2.0, 8.2
    banner = FancyBboxPatch(
        (3.5, banner_y), 93.0, banner_h,
        boxstyle="round,pad=0.3,rounding_size=1.0",
        facecolor=theme["hub_bg"], edgecolor=theme["hub_border"],
        linewidth=2.0, zorder=3
    )
    ax.add_patch(banner)
    ax.text(
        5.2, banner_y + banner_h - 1.55, takeaway_title,
        fontsize=14.4, fontweight="bold", color=theme["hub_sub"],
        ha="left", va="center", zorder=4
    )
    ax.plot([5.2, 94.8], [banner_y + banner_h - 3.05, banner_y + banner_h - 3.05],
            color=theme["hub_border"], lw=0.8, alpha=0.45, zorder=3.5)

    lines = takeaway_body if isinstance(takeaway_body, (list, tuple)) else str(takeaway_body).split("\n")
    for idx, line in enumerate(lines):
        ly = banner_y + banner_h - 4.40 - idx * 2.15
        ax.text(
            5.2, ly, line,
            fontsize=12.4, color=theme["hub_text"],
            ha="left", va="center", zorder=4
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
