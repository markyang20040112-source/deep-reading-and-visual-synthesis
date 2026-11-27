"""
chart_creative_armory.py
Mode 3 Creative Armory charts (liquid container bars, masked texture wedge, sprite scatter).
Note: `hcl_color_engine` is the public entry point.
"""

import math
from typing import Dict, Optional, Sequence

from chart_common import _ensure_cjk_font, despine_axes
from chart_data import _parse_numeric_or_na
from color_core import relative_luminance

def _build_tapered_cup_path(
    x_center: float,
    y_bottom: float,
    y_top: float,
    w_bottom: float,
    w_top: float,
    corner_r_x: float = 0.06,
    corner_r_y_ratio: float = 0.06,
):
    """Build a smooth Matplotlib Path for a tapered glass tumbler with a rounded bottom."""
    from matplotlib.path import Path

    h = max(1e-6, y_top - y_bottom)
    ry = h * corner_r_y_ratio
    rx = min(corner_r_x, w_bottom * 0.35)

    x_tl = x_center - 0.5 * w_top
    x_tr = x_center + 0.5 * w_top
    x_bl = x_center - 0.5 * w_bottom
    x_br = x_center + 0.5 * w_bottom

    verts = [
        (x_tl, y_top),
        (x_bl, y_bottom + ry),
        (x_bl, y_bottom),
        (x_bl + rx, y_bottom),
        (x_br - rx, y_bottom),
        (x_br, y_bottom),
        (x_br, y_bottom + ry),
        (x_tr, y_top),
        (x_tl, y_top),
    ]
    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.CURVE3,
        Path.CURVE3,
        Path.LINETO,
        Path.CURVE3,
        Path.CURVE3,
        Path.LINETO,
        Path.CLOSEPOLY,
    ]
    return Path(verts, codes)


def plot_liquid_container_bars(
    ax: object,
    labels: Sequence[str],
    values: Sequence[float],
    max_capacity: Optional[float] = None,
    container_style: str = "glass_cup",
    liquid_color: str = "#FFFFFF",
    canvas_bg: str = "#5BC0EB",
    glass_edge_color: str = "#E2F1F8",
    value_fmt: str = "{:.0f} ml",
    subtitle_values: Optional[Sequence[str]] = None,
    **kwargs,
) -> Dict[str, object]:
    """
    Data 7 RE:LAB NT$100 Milk Purchasing Power High-Gloss Container Chart:
    - Renders multi-layered vector glass cups (or battery/test-tube containers) with rim thickness,
      heavy curved glass base cushion, left/right specular reflection strips, and an exact `clip_path`
      liquid fill + 3D meniscus surface ellipse.
    """
    _ensure_cjk_font()
    from matplotlib.patches import Ellipse, FancyBboxPatch, PathPatch, Polygon, Rectangle

    clean_pairs = [
        (str(lbl), float(val))
        for lbl, val in zip(labels, values)
        if _parse_numeric_or_na(val) is not None
    ]
    n = len(clean_pairs)
    if n == 0:
        return {"containers": [], "liquids": [], "highlights": [], "annotations": [], "ax": ax}

    c_labels = [p[0] for p in clean_pairs]
    c_vals = [p[1] for p in clean_pairs]
    v_max = max(c_vals)
    cap = float(max_capacity) if (max_capacity is not None and float(max_capacity) >= v_max) else (v_max * 1.12)
    cap = max(cap, 1.0)

    set_fig_bg = bool(kwargs.pop("set_fig_bg", True))
    ax.set_facecolor(canvas_bg)
    if set_fig_bg and hasattr(ax, "figure") and ax.figure is not None:
        ax.figure.patch.set_facecolor(canvas_bg)

    bg_lum = relative_luminance(canvas_bg)
    primary_ink = str(kwargs.pop("text_color", "#FFFFFF" if bg_lum < 0.42 else "#0F172A"))
    secondary_ink = str(kwargs.pop("subtitle_color", "#E0F2FE" if primary_ink == "#FFFFFF" else "#334155"))

    containers = []
    liquids = []
    highlights = []
    anns = []

    style_key = str(container_style or "glass_cup").strip().lower()
    w_top = float(kwargs.pop("cup_top_width", 0.62))
    w_bot = float(kwargs.pop("cup_bottom_width", 0.46 if style_key == "glass_cup" else 0.58))
    wall_dx = 0.038
    base_thick = cap * 0.055

    for idx, (lbl, val) in enumerate(zip(c_labels, c_vals)):
        xc = float(idx)
        fill_h = max(0.0, min(cap, val))

        # 1. Outer Glass Silhouette + Heavy Glass Base Cushion
        outer_path = _build_tapered_cup_path(
            xc,
            y_bottom=-base_thick,
            y_top=cap * 1.02,
            w_bottom=w_bot + 2.0 * wall_dx,
            w_top=w_top + 2.0 * wall_dx,
        )
        outer_patch = PathPatch(
            outer_path,
            facecolor="#FFFFFF",
            alpha=0.22,
            edgecolor=glass_edge_color,
            linewidth=2.0,
            zorder=2,
        )
        ax.add_patch(outer_patch)
        containers.append(outer_patch)

        # Heavy bottom glass base refraction cushion
        base_path = _build_tapered_cup_path(
            xc,
            y_bottom=-base_thick,
            y_top=0.0,
            w_bottom=w_bot + 1.6 * wall_dx,
            w_top=w_bot + 1.8 * wall_dx,
            corner_r_y_ratio=0.35,
        )
        base_patch = PathPatch(
            base_path,
            facecolor="#FFFFFF",
            alpha=0.36,
            edgecolor="none",
            zorder=2.5,
        )
        ax.add_patch(base_patch)

        # 2. Inner Cavity Clip Path & Exact Liquid Level Fill
        inner_path = _build_tapered_cup_path(
            xc,
            y_bottom=0.0,
            y_top=cap,
            w_bottom=w_bot,
            w_top=w_top,
            corner_r_y_ratio=0.04,
        )
        inner_clip_patch = PathPatch(
            inner_path,
            facecolor="#FFFFFF",
            alpha=0.08,
            edgecolor="#FFFFFF",
            linewidth=0.8,
            zorder=3,
        )
        ax.add_patch(inner_clip_patch)

        if fill_h > 0:
            liq_rect = Rectangle(
                (xc - 0.6 * w_top, -base_thick * 0.2),
                1.2 * w_top,
                fill_h + base_thick * 0.2,
                facecolor=liquid_color,
                alpha=0.95,
                edgecolor="none",
                zorder=3.5,
            )
            ax.add_patch(liq_rect)
            liq_rect.set_clip_path(inner_clip_patch)
            liquids.append(liq_rect)

            # 3D liquid meniscus ellipse at height fill_h
            ratio_h = fill_h / cap
            w_at_fill = w_bot + ratio_h * (w_top - w_bot)
            meniscus = Ellipse(
                (xc, fill_h),
                width=w_at_fill * 0.98,
                height=cap * 0.032,
                facecolor=liquid_color,
                edgecolor="#E2E8F0",
                linewidth=1.1,
                alpha=0.98,
                zorder=4,
            )
            ax.add_patch(meniscus)
            liquids.append(meniscus)

        # 3. High-Gloss Vertical Glass Specular Reflection Strips & Top Rim
        # Left primary reflection band (tapered matching the cup wall)
        y_r0, y_r1 = cap * 0.06, cap * 0.94
        w_at_r0 = w_bot + 0.06 * (w_top - w_bot)
        w_at_r1 = w_bot + 0.94 * (w_top - w_bot)
        left_strip = Polygon(
            [
                (xc - 0.41 * w_at_r0, y_r0),
                (xc - 0.31 * w_at_r0, y_r0),
                (xc - 0.31 * w_at_r1, y_r1),
                (xc - 0.41 * w_at_r1, y_r1),
            ],
            closed=True,
            facecolor="#FFFFFF",
            alpha=0.38,
            edgecolor="none",
            zorder=5,
        )
        ax.add_patch(left_strip)
        highlights.append(left_strip)

        # Right subtle rim reflection strip
        right_strip = Polygon(
            [
                (xc + 0.33 * w_at_r0, cap * 0.10),
                (xc + 0.39 * w_at_r0, cap * 0.10),
                (xc + 0.39 * w_at_r1, cap * 0.90),
                (xc + 0.33 * w_at_r1, cap * 0.90),
            ],
            closed=True,
            facecolor="#FFFFFF",
            alpha=0.22,
            edgecolor="none",
            zorder=5,
        )
        ax.add_patch(right_strip)
        highlights.append(right_strip)

        # Top glass rim ellipse ring
        top_rim = Ellipse(
            (xc, cap * 1.02),
            width=w_top + 2.0 * wall_dx,
            height=cap * 0.038,
            facecolor="none",
            edgecolor=glass_edge_color,
            linewidth=1.8,
            alpha=0.88,
            zorder=6,
        )
        ax.add_patch(top_rim)
        highlights.append(top_rim)

        if style_key == "battery":
            term = FancyBboxPatch(
                (xc - 0.12 * w_top, cap * 1.02),
                0.24 * w_top,
                cap * 0.045,
                boxstyle="round,pad=0.01",
                facecolor=glass_edge_color,
                edgecolor="none",
                zorder=6,
            )
            ax.add_patch(term)

        # 4. Direct Value Label & Country/Category Footer Label
        val_str = value_fmt(val) if callable(value_fmt) else value_fmt.format(val)
        has_sub = bool(subtitle_values and idx < len(subtitle_values) and subtitle_values[idx])
        val_y = cap * 1.135 if has_sub else cap * 1.075
        t_val = ax.text(
            xc,
            val_y,
            val_str,
            ha="center",
            va="bottom",
            fontsize=13.5,
            fontweight="bold",
            color=primary_ink,
            zorder=7,
        )
        anns.append(t_val)

        if has_sub:
            t_sub = ax.text(
                xc,
                cap * 1.062,
                str(subtitle_values[idx]),
                ha="center",
                va="bottom",
                fontsize=9.5,
                fontweight="bold",
                color=secondary_ink,
                zorder=7,
            )
            anns.append(t_sub)

        t_lbl = ax.text(
            xc,
            -base_thick - cap * 0.06,
            lbl,
            ha="center",
            va="top",
            fontsize=12.5,
            fontweight="bold",
            color=primary_ink,
            zorder=7,
        )
        anns.append(t_lbl)

    ax.set_xlim(-0.70, (n - 1) + 0.70)
    ax.set_ylim(-base_thick - cap * 0.22, cap * 1.28)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right", "bottom", "left"):
        if side in ax.spines:
            ax.spines[side].set_visible(False)

    return {
        "containers": containers,
        "liquids": liquids,
        "highlights": highlights,
        "annotations": anns,
        "max_capacity": cap,
        "ax": ax,
    }


def _generate_procedural_pineapple_texture(size: int = 512):
    """
    Generate a rich, high-resolution procedural organic pineapple cross-section texture (`size x size x 4` RGBA uint8)
    used when `texture_img_path` is not provided or as a fallback.
    """
    import numpy as np

    yy, xx = np.mgrid[-1.0:1.0:complex(0, size), -1.0:1.0:complex(0, size)]
    rr = np.sqrt(xx ** 2 + yy ** 2)
    theta = np.arctan2(yy, xx)

    rgba = np.zeros((size, size, 4), dtype=np.uint8)
    inside = rr <= 1.0

    # Base golden yellow flesh gradient
    radial_wave = 0.5 + 0.5 * np.cos(16.0 * theta)
    fibrous_ripples = 0.5 + 0.5 * np.sin(38.0 * rr - 16.0 * theta)

    r_ch = np.clip(248.0 - 22.0 * rr + 10.0 * radial_wave, 0, 255)
    g_ch = np.clip(208.0 - 38.0 * (rr ** 1.4) + 14.0 * radial_wave + 8.0 * fibrous_ripples, 0, 255)
    b_ch = np.clip(46.0 + 25.0 * (1.0 - rr) + 12.0 * fibrous_ripples, 0, 255)

    # Central lighter core (r < 0.23)
    core_mask = rr < 0.23
    r_ch = np.where(core_mask, 254.0, r_ch)
    g_ch = np.where(core_mask, 240.0 - 25.0 * (rr / 0.23), g_ch)
    b_ch = np.where(core_mask, 138.0 - 30.0 * (rr / 0.23), b_ch)

    # Radial carpel septum lines (16 segments between r=0.23 and r=0.88)
    septum = (rr >= 0.23) & (rr <= 0.88) & (np.abs(np.sin(8.0 * theta)) < 0.045)
    r_ch = np.where(septum, r_ch * 0.90, r_ch)
    g_ch = np.where(septum, g_ch * 0.84, g_ch)
    b_ch = np.where(septum, b_ch * 0.70, b_ch)

    # Ring of 16 seed pockets around r = 0.74
    for k in range(16):
        ang = (2.0 * math.pi * k) / 16.0 + (math.pi / 16.0)
        sx, sy = 0.74 * math.cos(ang), 0.74 * math.sin(ang)
        d_seed = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2)
        seed_dot = d_seed < 0.042
        r_ch = np.where(seed_dot, 180.0, r_ch)
        g_ch = np.where(seed_dot, 83.0, g_ch)
        b_ch = np.where(seed_dot, 9.0, b_ch)

    # Scalloped golden-brown rind outer ring (0.90 <= r <= 1.05, clipped by vector Wedge r=1.0)
    rind_boundary = 0.905 + 0.022 * np.cos(24.0 * theta)
    rind_mask = rr >= rind_boundary
    r_ch = np.where(rind_mask, 194.0, r_ch)
    g_ch = np.where(rind_mask, 106.0, g_ch)
    b_ch = np.where(rind_mask, 18.0, b_ch)

    rgba[..., 0] = r_ch.astype(np.uint8)
    rgba[..., 1] = g_ch.astype(np.uint8)
    rgba[..., 2] = b_ch.astype(np.uint8)
    rgba[..., 3] = 255
    return rgba


def plot_masked_texture_wedge(
    ax: object,
    pct_value: float,
    texture_img_path: Optional[str] = None,
    title: str = "",
    subtitle: str = "",
    base_disc_color: str = "#E2E8F0",
    wedge_edge_color: str = "#FFFFFF",
    start_angle: float = 90.0,
    clockwise: bool = True,
    value_fmt: Optional[str] = None,
    **kwargs,
) -> Dict[str, object]:
    """
    Data 7 RE:LAB Pineapple Export Wedge / Small-Multiples Texture Mask Chart:
    - Draws a muted 100% full reference disc (`base_disc_color`).
    - Loads a text-free texture image (from `image-generator` or procedural pineapple cross-section fallback)
      and clips it with a mathematically exact `matplotlib.patches.Wedge` of angle `360 * pct`.
    """
    _ensure_cjk_font()
    import os
    from matplotlib.patches import Circle, Wedge
    import numpy as np

    raw_v = float(pct_value)
    p_norm = (raw_v / 100.0) if raw_v > 1.0 else raw_v
    p_clamped = max(0.0, min(1.0, p_norm))
    pct_display = p_clamped * 100.0

    img_arr = None
    if texture_img_path and os.path.exists(str(texture_img_path)):
        try:
            from PIL import Image
            pil_img = Image.open(str(texture_img_path)).convert("RGBA")
            w, h = pil_img.size
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            pil_sq = pil_img.crop((left, top, left + side, top + side)).resize((512, 512))
            img_arr = np.asarray(pil_sq)
        except Exception:
            img_arr = None

    if img_arr is None:
        img_arr = _generate_procedural_pineapple_texture(size=512)

    base_disc = Circle(
        (0.0, 0.0),
        radius=1.0,
        facecolor=base_disc_color,
        edgecolor="#CBD5E1",
        linewidth=1.4,
        zorder=1,
    )
    ax.add_patch(base_disc)

    angle_span = 360.0 * p_clamped
    if p_clamped >= 0.9999:
        theta1, theta2 = 0.0, 360.0
    elif clockwise:
        theta1 = float(start_angle) - angle_span
        theta2 = float(start_angle)
    else:
        theta1 = float(start_angle)
        theta2 = float(start_angle) + angle_span

    im = ax.imshow(
        img_arr,
        extent=[-1.0, 1.0, -1.0, 1.0],
        origin="upper",
        zorder=2,
    )

    wedge_patch = Wedge(
        (0.0, 0.0),
        r=1.0,
        theta1=theta1,
        theta2=theta2,
        facecolor="none",
        edgecolor=wedge_edge_color,
        linewidth=2.4,
        zorder=3,
    )
    ax.add_patch(wedge_patch)
    im.set_clip_path(wedge_patch)

    # Redraw wedge border on top so slice boundary is razor sharp
    border_wedge = Wedge(
        (0.0, 0.0),
        r=1.0,
        theta1=theta1,
        theta2=theta2,
        facecolor="none",
        edgecolor=wedge_edge_color,
        linewidth=2.2,
        zorder=4,
    )
    ax.add_patch(border_wedge)

    val_text = value_fmt.format(pct_display) if value_fmt else f"{pct_display:.1f}%"
    badge_color = kwargs.pop("badge_color", "#B45309")
    t_pct = ax.text(
        0.0,
        -1.18,
        val_text,
        ha="center",
        va="top",
        fontsize=15.0,
        fontweight="bold",
        color=badge_color,
        zorder=5,
    )

    t_title = None
    if title:
        t_title = ax.text(
            0.0,
            1.14,
            str(title),
            ha="center",
            va="bottom",
            fontsize=12.5,
            fontweight="bold",
            color="#0F172A",
            zorder=5,
        )

    t_sub = None
    if subtitle:
        t_sub = ax.text(
            0.0,
            -1.38,
            str(subtitle),
            ha="center",
            va="top",
            fontsize=9.5,
            color="#475569",
            zorder=5,
        )

    ax.set_xlim(-1.22, 1.22)
    ax.set_ylim(-1.52 if subtitle else -1.35, 1.32 if title else 1.15)
    ax.set_aspect("equal")
    ax.axis("off")

    return {
        "image": im,
        "wedge": wedge_patch,
        "border_wedge": border_wedge,
        "base_disc": base_disc,
        "pct_text": t_pct,
        "title_text": t_title,
        "subtitle_text": t_sub,
        "ax": ax,
    }


def _generate_procedural_coffee_bean_sprite(size: int = 128):
    """Generate a crisp 128x128 RGBA roasted coffee bean icon with 3D shading and central S-crease."""
    import numpy as np

    yy, xx = np.mgrid[-1.0:1.0:complex(0, size), -1.0:1.0:complex(0, size)]
    # Tilted oval bean (rotated by 28 degrees)
    ang = math.radians(28.0)
    xr = xx * math.cos(ang) + yy * math.sin(ang)
    yr = -xx * math.sin(ang) + yy * math.cos(ang)

    ellipse_d = (xr / 0.62) ** 2 + (yr / 0.84) ** 2
    bean_mask = ellipse_d <= 1.0

    # S-curve central crease along yr
    crease_center_x = 0.09 * np.sin(2.6 * yr)
    crease_dist = np.abs(xr - crease_center_x)
    crease_mask = (crease_dist < 0.055) & (ellipse_d <= 0.88)

    # 3D Lambertian highlight on upper-left
    light = np.clip(1.0 - 0.55 * ((xr + 0.22) ** 2 + (yr + 0.25) ** 2), 0.35, 1.08)

    rgba = np.zeros((size, size, 4), dtype=np.uint8)
    r_ch = np.where(crease_mask, 42.0, np.clip(122.0 * light, 35, 168))
    g_ch = np.where(crease_mask, 22.0, np.clip(74.0 * light, 18, 108))
    b_ch = np.where(crease_mask, 12.0, np.clip(38.0 * light, 10, 62))

    # Crisp rim outline
    rim_mask = (ellipse_d > 0.86) & bean_mask
    r_ch = np.where(rim_mask, 58.0, r_ch)
    g_ch = np.where(rim_mask, 32.0, g_ch)
    b_ch = np.where(rim_mask, 16.0, b_ch)

    rgba[..., 0] = r_ch.astype(np.uint8)
    rgba[..., 1] = g_ch.astype(np.uint8)
    rgba[..., 2] = b_ch.astype(np.uint8)
    rgba[..., 3] = np.where(bean_mask, 255, 0).astype(np.uint8)
    return rgba


def plot_sprite_scatter(
    ax: object,
    x_vals: Sequence[float],
    y_vals: Sequence[float],
    sprite_img_path: Optional[str] = None,
    labels: Optional[Sequence[str]] = None,
    zoom: float = 0.18,
    auto_remove_white_bg: bool = True,
    white_threshold: int = 242,
    **kwargs,
) -> Dict[str, object]:
    """
    Data 7 RE:LAB Coffee Bean Sprite Scatter Plot:
    - Loads a sprite icon (or procedural roasted coffee bean fallback), automatically strips solid white
      backgrounds via PIL when `auto_remove_white_bg=True`, and anchors sprites at exact `(x, y)` coordinates
      using `OffsetImage` & `AnnotationBbox` with leader-line callouts.
    """
    _ensure_cjk_font()
    import os
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage
    import numpy as np

    pts = []
    for idx, (xv, yv) in enumerate(zip(x_vals, y_vals)):
        px, py = _parse_numeric_or_na(xv), _parse_numeric_or_na(yv)
        if px is not None and py is not None:
            lbl = str(labels[idx]) if (labels is not None and idx < len(labels) and labels[idx] is not None) else ""
            pts.append((float(px), float(py), lbl))

    if not pts:
        return {"artists": [], "annotations": [], "ax": ax}

    sprite_rgba = None
    if sprite_img_path and os.path.exists(str(sprite_img_path)):
        try:
            from PIL import Image
            pil_img = Image.open(str(sprite_img_path)).convert("RGBA")
            arr = np.asarray(pil_img).copy()
            if auto_remove_white_bg:
                white_mask = (
                    (arr[..., 0] >= white_threshold)
                    & (arr[..., 1] >= white_threshold)
                    & (arr[..., 2] >= white_threshold)
                )
                arr[white_mask, 3] = 0
            sprite_rgba = arr
        except Exception:
            sprite_rgba = None

    if sprite_rgba is None:
        sprite_rgba = _generate_procedural_coffee_bean_sprite(size=128)

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.scatter(xs, ys, s=10, alpha=0.0, zorder=1)

    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_span = max(1e-6, x_max - x_min)
    y_span = max(1e-6, y_max - y_min)
    ax.set_xlim(x_min - x_span * 0.12, x_max + x_span * 0.16)
    ax.set_ylim(y_min - y_span * 0.14, y_max + y_span * 0.16)

    artists = []
    anns = []
    offsets_cycle = [(14, 14), (14, -16), (-14, 14), (-14, -16), (18, 0), (-18, 0)]

    for idx, (px, py, lbl) in enumerate(pts):
        oi = OffsetImage(sprite_rgba, zoom=float(zoom))
        ab = AnnotationBbox(oi, (px, py), frameon=False, zorder=4)
        ax.add_artist(ab)
        artists.append(ab)

        if lbl:
            dx, dy = offsets_cycle[idx % len(offsets_cycle)]
            ha_align = "left" if dx >= 0 else "right"
            ann = ax.annotate(
                lbl,
                xy=(px, py),
                xytext=(float(dx), float(dy)),
                textcoords="offset points",
                ha=ha_align,
                va="center",
                fontsize=9.2,
                fontweight="bold",
                color="#0F172A",
                arrowprops=dict(arrowstyle="-", color="#64748B", lw=1.0, shrinkA=0, shrinkB=6),
                zorder=5,
            )
            anns.append(ann)

    despine_axes(ax, grid_axis="both", grid_alpha=0.45)
    return {"artists": artists, "annotations": anns, "ax": ax}
