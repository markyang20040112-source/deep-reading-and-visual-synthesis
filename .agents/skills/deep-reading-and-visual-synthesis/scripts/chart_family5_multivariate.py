"""
chart_family5_multivariate.py
Chart Family 5: Full-sample 4-quadrant bubble matrix with size legend and arrow callouts.
Note: `hcl_color_engine` is the public entry point.
"""

from typing import Dict, List, Optional, Sequence, Tuple

from chart_common import _decollide_1d_positions, _ensure_cjk_font, despine_axes
from chart_data import _parse_numeric_or_na
from chart_family4_distribution import add_halo_vline
from color_core import (
    GEPHI_DISCRETE_NEUTRALS,
    GEPHI_QUALITATIVE_HEX,
    _resolve_lookup_color,
)


def _resolve_category_colors_readonly(
    categories: Sequence[object],
    category_color_map: Optional[Dict[str, str]] = None,
) -> Tuple[List[str], Dict[str, str]]:
    """Resolve per-point hex colors using read-only registry lookup + unused slot fallback."""
    cat_strs = [str(c).strip() if c is not None else "NA" for c in categories]
    unique_cats: List[str] = []
    for c in cat_strs:
        if c not in unique_cats:
            unique_cats.append(c)

    resolved_map: Dict[str, str] = {}
    used_upper = set()
    for c in unique_cats:
        hx = _resolve_lookup_color(c, category_color_map)
        if hx is not None:
            resolved_map[c] = hx
            used_upper.add(str(hx).upper())

    pool = [hx for hx in GEPHI_QUALITATIVE_HEX if str(hx).upper() not in used_upper]
    pool_iter = iter(pool)
    other_hex = GEPHI_DISCRETE_NEUTRALS["other_aggregated"]
    for c in unique_cats:
        if c not in resolved_map:
            resolved_map[c] = next(pool_iter, other_hex)

    return [resolved_map[c] for c in cat_strs], resolved_map


def plot_quadrant_bubble(
    ax: object,
    x_vals: Sequence[float],
    y_vals: Sequence[float],
    size_vals: Optional[Sequence[float]] = None,
    labels: Optional[Sequence[str]] = None,
    categories: Optional[Sequence[str]] = None,
    x_ref: Optional[float] = None,
    y_ref: Optional[float] = None,
    quadrant_labels: Optional[object] = None,
    annotate_indices: Optional[Sequence[int]] = None,
    annotate_top_k: int = 4,
    min_bubble_area: float = 90.0,
    max_bubble_area: float = 1400.0,
    show_size_legend: bool = True,
    size_unit: str = "",
    category_color_map: Optional[Dict[str, str]] = None,
    **kwargs,
) -> Dict[str, object]:
    """
    Chart Family 5: Full-Sample Boston 4-Quadrant Bubble Matrix.
    - Preserves all valid sample points (never drops detail points).
    - Linearly maps `size_vals` to bubble area `s` (radius proportional to sqrt(z)).
    - Draws white-halo crosshair reference lines (default: medians of X and Y).
    - Uses read-only entity lookup for category colors and decollided solid-arrow callouts.
    """
    _ensure_cjk_font()
    import matplotlib.lines as mlines
    import matplotlib.patheffects as pe
    import numpy as np

    pts: List[Tuple[float, float, float, str, str]] = []
    n_raw = min(len(x_vals), len(y_vals))
    for i in range(n_raw):
        px = _parse_numeric_or_na(x_vals[i])
        py = _parse_numeric_or_na(y_vals[i])
        if px is None or py is None:
            continue
        if size_vals is not None and i < len(size_vals):
            pz = _parse_numeric_or_na(size_vals[i])
            if pz is None:
                continue
            z_val = max(0.0, float(pz))
        else:
            z_val = 1.0
        lbl = str(labels[i]) if (labels is not None and i < len(labels)) else ""
        cat = str(categories[i]) if (categories is not None and i < len(categories)) else "樣本"
        pts.append((float(px), float(py), z_val, lbl, cat))

    if not pts:
        return {"scatter": None, "annotations": [], "x_ref": None, "y_ref": None, "ax": ax}

    xs = np.asarray([p[0] for p in pts], dtype="float64")
    ys = np.asarray([p[1] for p in pts], dtype="float64")
    zs = np.asarray([p[2] for p in pts], dtype="float64")
    p_labels = [p[3] for p in pts]
    p_cats = [p[4] for p in pts]

    if size_vals is not None:
        z_min, z_max = float(np.min(zs)), float(np.max(zs))
        if z_max > z_min:
            z_norm = (zs - z_min) / (z_max - z_min)
            areas = float(min_bubble_area) + z_norm * (float(max_bubble_area) - float(min_bubble_area))
        else:
            areas = np.full(len(pts), 0.5 * (float(min_bubble_area) + float(max_bubble_area)))
    else:
        areas = np.full(len(pts), 220.0)

    if categories is not None:
        point_colors, cat_color_map = _resolve_category_colors_readonly(p_cats, category_color_map)
    else:
        default_col = GEPHI_QUALITATIVE_HEX[0]
        point_colors = [default_col] * len(pts)
        cat_color_map = {}

    rx = float(x_ref) if x_ref is not None else float(np.median(xs))
    ry = float(y_ref) if y_ref is not None else float(np.median(ys))

    x_min, x_max = float(np.min(xs)), float(np.max(xs))
    y_min, y_max = float(np.min(ys)), float(np.max(ys))
    x_span = max(1e-6, x_max - x_min)
    y_span = max(1e-6, y_max - y_min)

    x_lo = x_min - x_span * 0.16
    x_hi = x_max + x_span * 0.18
    y_lo = y_min - y_span * 0.18
    y_hi = y_max + y_span * 0.18
    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(y_lo, y_hi)

    add_halo_vline(ax, rx, color="#64748B", linestyle="--", linewidth=1.6, halo_width=4.0, zorder=2)
    hline = ax.axhline(ry, color="#64748B", linestyle="--", linewidth=1.6, zorder=2)
    hline.set_path_effects([
        pe.Stroke(linewidth=4.0, foreground="#FFFFFF"),
        pe.Normal(),
    ])

    sc = ax.scatter(
        xs,
        ys,
        s=areas,
        c=point_colors,
        alpha=float(kwargs.get("bubble_alpha", 0.82)),
        edgecolors="#FFFFFF",
        linewidths=1.4,
        zorder=3.5,
    )

    anns: List[object] = []
    if quadrant_labels:
        if isinstance(quadrant_labels, dict):
            q_specs = [
                ("top_left", 0.03, 0.96, "left", "top"),
                ("top_right", 0.97, 0.96, "right", "top"),
                ("bottom_left", 0.03, 0.04, "left", "bottom"),
                ("bottom_right", 0.97, 0.04, "right", "bottom"),
            ]
            q_texts = [(quadrant_labels.get(k), qx, qy, ha, va) for k, qx, qy, ha, va in q_specs]
        else:
            q_list = list(quadrant_labels)
            coords = [
                (0.03, 0.96, "left", "top"),
                (0.97, 0.96, "right", "top"),
                (0.03, 0.04, "left", "bottom"),
                (0.97, 0.04, "right", "bottom"),
            ]
            q_texts = [(q_list[i] if i < len(q_list) else None, *coords[i]) for i in range(4)]

        for q_txt, qx, qy, ha, va in q_texts:
            if q_txt:
                anns.append(
                    ax.text(
                        qx,
                        qy,
                        str(q_txt),
                        transform=ax.transAxes,
                        ha=ha,
                        va=va,
                        fontsize=9.2,
                        fontweight="bold",
                        color="#475569",
                        bbox=dict(
                            boxstyle="round,pad=0.24,rounding_size=0.35",
                            facecolor="#F8FAFC",
                            edgecolor="#CBD5E1",
                            lw=0.9,
                        ),
                        zorder=5,
                    )
                )

    # Select indices to annotate
    chosen_indices: List[int] = []
    if annotate_indices is not None:
        for idx in annotate_indices:
            if 0 <= int(idx) < len(pts) and p_labels[int(idx)]:
                chosen_indices.append(int(idx))
    elif labels is not None and annotate_top_k > 0:
        scores = []
        for i in range(len(pts)):
            if not p_labels[i]:
                continue
            dist = ((xs[i] - rx) / x_span) ** 2 + ((ys[i] - ry) / y_span) ** 2
            scores.append((dist, i))
        scores.sort(reverse=True)
        chosen_indices = [idx for _, idx in scores[: int(annotate_top_k)]]

    if chosen_indices:
        eff_x_span = max(1e-6, x_hi - x_lo)
        eff_y_span = max(1e-6, y_hi - y_lo)
        stroke_halo = [pe.withStroke(linewidth=3.2, foreground="#FFFFFF")]
        left_group = []
        right_group = []
        for idx in chosen_indices:
            px, py = float(xs[idx]), float(ys[idx])
            on_right = px >= rx
            tx = px + (0.09 if on_right else -0.09) * eff_x_span
            tx = max(x_lo + 0.08 * eff_x_span, min(x_hi - 0.08 * eff_x_span, tx))
            ty = py + (0.08 if py >= ry else -0.08) * eff_y_span
            ty = max(y_lo + 0.10 * eff_y_span, min(y_hi - 0.10 * eff_y_span, ty))
            rec = (idx, px, py, tx, ty, "left" if on_right else "right")
            if on_right:
                right_group.append(rec)
            else:
                left_group.append(rec)

        for grp in (left_group, right_group):
            if not grp:
                continue
            adj_tys = _decollide_1d_positions([r[4] for r in grp], min_dist=0.11 * eff_y_span)
            adj_tys = [max(y_lo + 0.09 * eff_y_span, min(y_hi - 0.09 * eff_y_span, v)) for v in adj_tys]
            for (idx, px, py, tx, _ty, ha), final_ty in zip(grp, adj_tys):
                col = point_colors[idx]
                anns.append(
                    ax.annotate(
                        p_labels[idx],
                        xy=(px, py),
                        xytext=(tx, final_ty),
                        ha=ha,
                        va="center",
                        fontsize=9.2,
                        fontweight="bold",
                        color="#0F172A",
                        path_effects=stroke_halo,
                        arrowprops=dict(
                            arrowstyle="-|>,head_length=0.40,head_width=0.22",
                            color=col,
                            lw=1.25,
                            shrinkA=3,
                            shrinkB=5,
                        ),
                        zorder=6,
                    )
                )

    despine_axes(ax, grid_axis="both", grid_alpha=0.35)

    handles = []
    if categories is not None and kwargs.get("show_legend", True) and cat_color_map:
        for cat_name, cat_hex in cat_color_map.items():
            handles.append(
                mlines.Line2D(
                    [], [],
                    color="none",
                    marker="o",
                    markersize=8,
                    markerfacecolor=cat_hex,
                    markeredgecolor="#FFFFFF",
                    label=cat_name,
                )
            )
    if show_size_legend and size_vals is not None and float(np.max(zs)) > float(np.min(zs)):
        z_mid = 0.5 * (float(np.min(zs)) + float(np.max(zs)))
        z_hi = float(np.max(zs))
        unit_sfx = f" {size_unit}".rstrip() if size_unit else ""
        for z_sample, mk_size in ((z_mid, 8.5), (z_hi, 13.0)):
            handles.append(
                mlines.Line2D(
                    [], [],
                    color="none",
                    marker="o",
                    markersize=mk_size,
                    markerfacecolor="#CBD5E1",
                    markeredgecolor="#64748B",
                    label=f"規模 {z_sample:.0f}{unit_sfx}",
                )
            )
    if handles:
        ax.legend(
            handles=handles,
            frameon=False,
            loc="lower left",
            bbox_to_anchor=(-0.01, 1.01),
            ncol=min(6, len(handles)),
            fontsize=9.0,
        )

    return {
        "scatter": sc,
        "annotations": anns,
        "x_ref": rx,
        "y_ref": ry,
        "category_colors": cat_color_map,
        "ax": ax,
    }
