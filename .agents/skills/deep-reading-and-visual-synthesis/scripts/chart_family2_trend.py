"""
chart_family2_trend.py
Chart Family 2: Shared-baseline scissors line + gap fill and paired dual-bar contrast charts.
Note: `hcl_color_engine` is the public entry point.
"""

from typing import Dict, List, Optional, Sequence

from chart_common import _decollide_1d_positions, _ensure_cjk_font, despine_axes
from chart_data import _parse_numeric_or_na
from color_core import (
    GEPHI_QUALITATIVE_HEX,
    GEPHI_SEQUENTIAL_SCALES,
    _resolve_lookup_color,
)


def _est_text_pts(text: str, fontsize: float) -> float:
    width_units = 0.0
    for ch in str(text):
        width_units += 1.02 if ord(ch) > 127 else 0.58
    return width_units * fontsize


def plot_scissors_line(
    ax: object,
    x_vals: Sequence[object],
    y_series_a: Sequence[object],
    y_series_b: Sequence[object],
    label_a: str = "序列 A",
    label_b: str = "序列 B",
    color_a: Optional[str] = None,
    color_b: Optional[str] = None,
    fill_gap: bool = True,
    gap_color: Optional[str] = None,
    gap_alpha: float = 0.55,
    value_fmt: str = "{:.1f}",
    show_end_labels: bool = True,
    right_pad_ratio: float = 0.22,
    linewidth: float = 2.6,
    marker: str = "o",
    markersize: float = 6.0,
    category_color_map: Optional[Dict[str, str]] = None,
    **kwargs,
) -> Dict[str, object]:
    """
    Chart Family 2: Shared-Baseline Scissors Line Chart with Gap Area Band.
    - Uses true numeric `x_vals` (preserves irregular spacing; breaks cleanly on NaN/None).
    - Places both series on a shared baseline (`Y >= 0` by default for non-negative data).
    - Resolves `label_a` / `label_b` via read-only registry lookup unless explicit colors are given.
    - Expands right X padding and decollides end-of-line direct labels.
    """
    _ensure_cjk_font()
    import matplotlib.patheffects as pe
    import numpy as np

    xs: List[float] = []
    ya_list: List[float] = []
    yb_list: List[float] = []
    for xv, av, bv in zip(x_vals, y_series_a, y_series_b):
        px = _parse_numeric_or_na(xv)
        if px is None:
            continue
        pa = _parse_numeric_or_na(av)
        pb = _parse_numeric_or_na(bv)
        xs.append(float(px))
        ya_list.append(float(pa) if pa is not None else float("nan"))
        yb_list.append(float(pb) if pb is not None else float("nan"))

    if not xs:
        return {"line_a": None, "line_b": None, "fill": None, "annotations": [], "ax": ax}

    order = sorted(range(len(xs)), key=lambda i: xs[i])
    x_arr = np.asarray([xs[i] for i in order], dtype="float64")
    ya = np.asarray([ya_list[i] for i in order], dtype="float64")
    yb = np.asarray([yb_list[i] for i in order], dtype="float64")

    c_a = (
        color_a
        if color_a is not None
        else (_resolve_lookup_color(label_a, category_color_map) or GEPHI_QUALITATIVE_HEX[0])
    )
    c_b = (
        color_b
        if color_b is not None
        else (_resolve_lookup_color(label_b, category_color_map) or GEPHI_QUALITATIVE_HEX[1])
    )
    c_gap = gap_color if gap_color is not None else GEPHI_SEQUENTIAL_SCALES["orange"][0]

    fill_obj = None
    if fill_gap:
        valid_both = np.isfinite(ya) & np.isfinite(yb)
        if np.any(valid_both):
            fill_obj = ax.fill_between(
                x_arr,
                ya,
                yb,
                where=valid_both,
                interpolate=True,
                color=c_gap,
                alpha=float(gap_alpha),
                zorder=1.5,
            )

    line_a = ax.plot(
        x_arr,
        ya,
        color=c_a,
        linewidth=linewidth,
        marker=marker,
        markersize=markersize,
        markeredgecolor="#FFFFFF",
        markeredgewidth=1.2,
        label=label_a,
        zorder=3,
    )[0]
    line_b = ax.plot(
        x_arr,
        yb,
        color=c_b,
        linewidth=linewidth,
        marker=marker,
        markersize=markersize,
        markeredgecolor="#FFFFFF",
        markeredgewidth=1.2,
        label=label_b,
        zorder=3.2,
    )[0]

    finite_vals = np.concatenate([ya[np.isfinite(ya)], yb[np.isfinite(yb)]])
    if finite_vals.size > 0:
        v_min = float(np.min(finite_vals))
        v_max = float(np.max(finite_vals))
        y_span = max(1e-6, v_max - v_min)
        force_zero = bool(kwargs.get("force_zero", True))
        if force_zero and v_min >= 0.0:
            y_lo = 0.0
            y_hi = max(1e-6, v_max) * 1.16
        else:
            y_lo = v_min - y_span * 0.14
            y_hi = v_max + y_span * 0.16
        ax.set_ylim(y_lo, y_hi)
    else:
        y_lo, y_hi = 0.0, 1.0

    x_min, x_max = float(x_arr[0]), float(x_arr[-1])
    x_span = max(1e-6, x_max - x_min)
    eff_y_span = max(1e-6, y_hi - y_lo)

    anns: List[object] = []
    if show_end_labels:
        end_items = []
        for arr, lbl, col in ((ya, label_a, c_a), (yb, label_b, c_b)):
            fin_idx = np.where(np.isfinite(arr))[0]
            if fin_idx.size > 0:
                idx = int(fin_idx[-1])
                end_items.append((float(x_arr[idx]), float(arr[idx]), lbl, col))

        # Ensure right X headroom fits the longest direct end label cleanly
        fig_obj = ax.figure
        ax_width_pts = max(180.0, float(fig_obj.get_figwidth()) * float(ax.get_position().width) * 72.0)
        label_texts = [f"{lbl} {value_fmt.format(yv)}" for _, yv, lbl, _ in end_items]
        max_lbl_pts = max((_est_text_pts(t, 9.8) for t in label_texts), default=40.0) + 18.0
        needed_frac = max_lbl_pts / max(60.0, ax_width_pts - max_lbl_pts)
        eff_right_pad = max(float(right_pad_ratio), min(0.45, needed_frac + 0.03))
        ax.set_xlim(x_min - x_span * 0.05, x_max + x_span * eff_right_pad)
        # Keep x-ticks strictly inside actual data domain so ticks never sit under right-hand labels
        x_lo_now, x_hi_now = ax.get_xlim()
        valid_ticks = [t for t in ax.get_xticks() if (x_min - 1e-9) <= t <= (x_max + 1e-9)]
        if len(valid_ticks) >= 2:
            ax.set_xticks(valid_ticks)
            ax.set_xlim(x_lo_now, x_hi_now)

        if end_items:
            raw_ys = [item[1] for item in end_items]
            adj_ys = _decollide_1d_positions(raw_ys, min_dist=eff_y_span * 0.09)
            # Clamp decollided labels inside [y_lo + 4%, y_hi - 4%]
            adj_ys = [max(y_lo + eff_y_span * 0.05, min(y_hi - eff_y_span * 0.05, yv)) for yv in adj_ys]
            stroke_halo = [pe.withStroke(linewidth=3.0, foreground="#FFFFFF")]
            x_text = x_max + x_span * 0.025
            for (xl, _yl, _lbl, col), txt, y_adj in zip(end_items, label_texts, adj_ys):
                ann = ax.annotate(
                    txt,
                    xy=(xl, y_adj),
                    xytext=(x_text, y_adj),
                    ha="left",
                    va="center",
                    fontsize=9.6,
                    fontweight="bold",
                    color=col,
                    path_effects=stroke_halo,
                    zorder=6,
                )
                anns.append(ann)
    else:
        ax.set_xlim(x_min - x_span * 0.05, x_max + x_span * 0.05)

    despine_axes(ax, grid_axis="y", grid_alpha=0.45)
    if kwargs.get("show_legend", True):
        ax.legend(frameon=False, loc="upper left", ncol=2, fontsize=9.5)

    return {
        "line_a": line_a,
        "line_b": line_b,
        "fill": fill_obj,
        "annotations": anns,
        "ax": ax,
    }


def plot_paired_dual_bar(
    ax: object,
    labels: Sequence[str],
    vals_a: Sequence[float],
    vals_b: Sequence[float],
    label_a: str = "基準 / 預期",
    label_b: str = "實際 / 對照",
    color_a: Optional[str] = None,
    color_b: Optional[str] = None,
    bar_width: float = 0.34,
    show_delta: bool = True,
    delta_fmt: str = "{:+.1f}",
    value_fmt: str = "{:.1f}",
    category_color_map: Optional[Dict[str, str]] = None,
    **kwargs,
) -> Dict[str, object]:
    """
    Chart Family 2: Paired Dual-Bar Chart with Explicit Gap/Delta Callout.
    - Enforces a zero baseline (`Y=0`) and horizontal zero-tilt category labels.
    - Resolves `label_a` / `label_b` via read-only registry lookup unless explicit colors are given.
    - Draws dashed comparison guides, vertical gap indicator, and `Δ` pill without overlapping bar labels.
    """
    _ensure_cjk_font()
    import matplotlib.patheffects as pe
    import numpy as np

    rows = []
    for lbl, av, bv in zip(labels, vals_a, vals_b):
        pa = _parse_numeric_or_na(av)
        pb = _parse_numeric_or_na(bv)
        if pa is not None and pb is not None:
            rows.append((str(lbl), float(pa), float(pb)))

    if not rows:
        return {"bars_a": None, "bars_b": None, "annotations": [], "ax": ax}

    c_a = (
        color_a
        if color_a is not None
        else (_resolve_lookup_color(label_a, category_color_map) or GEPHI_QUALITATIVE_HEX[0])
    )
    c_b = (
        color_b
        if color_b is not None
        else (_resolve_lookup_color(label_b, category_color_map) or GEPHI_QUALITATIVE_HEX[1])
    )

    n = len(rows)
    x_pos = np.arange(n, dtype="float64")
    r_labels = [r[0] for r in rows]
    r_a = [r[1] for r in rows]
    r_b = [r[2] for r in rows]

    bars_a = ax.bar(
        x_pos - bar_width / 2.0,
        r_a,
        width=bar_width,
        color=c_a,
        edgecolor="#FFFFFF",
        linewidth=1.0,
        label=label_a,
        zorder=3,
    )
    bars_b = ax.bar(
        x_pos + bar_width / 2.0,
        r_b,
        width=bar_width,
        color=c_b,
        edgecolor="#FFFFFF",
        linewidth=1.0,
        label=label_b,
        zorder=3,
    )

    all_v = r_a + r_b
    v_min = min(0.0, min(all_v))
    v_max = max(0.0, max(all_v))
    v_span = max(1e-6, v_max - v_min)
    top_mult = 1.32 if show_delta else 1.16
    ax.set_ylim(v_min * 1.12 if v_min < 0 else 0.0, v_max * top_mult if v_max > 0 else 1.0)
    ax.set_xlim(-0.65, n - 0.35)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(r_labels, fontsize=10.2, fontweight="bold", color="#1E293B", rotation=0)
    ax.tick_params(axis="x", length=0, pad=6)

    pos_ink = GEPHI_SEQUENTIAL_SCALES["orange"][3]
    neg_ink = GEPHI_SEQUENTIAL_SCALES["blue"][3]
    stroke_halo = [pe.withStroke(linewidth=2.8, foreground="#FFFFFF")]
    anns: List[object] = []

    for xi, va, vb in zip(x_pos, r_a, r_b):
        for bar_x, val in ((xi - bar_width / 2.0, va), (xi + bar_width / 2.0, vb)):
            va_align = "bottom" if val >= 0 else "top"
            y_off = 3.0 if val >= 0 else -4.0
            anns.append(
                ax.annotate(
                    value_fmt.format(val),
                    xy=(float(bar_x), float(val)),
                    xytext=(0.0, y_off),
                    textcoords="offset points",
                    ha="center",
                    va=va_align,
                    fontsize=9.0,
                    fontweight="bold",
                    color="#1E293B",
                    path_effects=stroke_halo,
                    zorder=5,
                )
            )

        if show_delta:
            delta = vb - va
            y_top = max(va, vb)
            y_bot = min(va, vb)
            if y_top - y_bot > v_span * 0.03:
                x_left_c = float(xi - bar_width / 2.0)
                x_right_c = float(xi + bar_width / 2.0)
                if va >= vb:
                    ax.plot(
                        [x_left_c, x_right_c],
                        [va, va],
                        linestyle="--",
                        linewidth=1.0,
                        color="#94A3B8",
                        zorder=4,
                    )
                    arr_x = x_right_c + bar_width * 0.25
                else:
                    ax.plot(
                        [x_left_c, x_right_c],
                        [vb, vb],
                        linestyle="--",
                        linewidth=1.0,
                        color="#94A3B8",
                        zorder=4,
                    )
                    arr_x = x_left_c - bar_width * 0.25
                arr_x = max(-0.55, min(n - 0.45, float(xi)))
                if y_top - y_bot > v_span * 0.14:
                    anns.append(
                        ax.annotate(
                            "",
                            xy=(arr_x, y_top),
                            xytext=(arr_x, y_bot),
                            arrowprops=dict(arrowstyle="<->", color="#64748B", lw=1.2, shrinkA=1, shrinkB=1),
                            zorder=4.5,
                        )
                    )

            d_col = pos_ink if delta >= 0 else neg_ink
            badge_y = y_top + v_span * 0.145
            anns.append(
                ax.text(
                    float(xi),
                    badge_y,
                    f"Δ {delta_fmt.format(delta)}",
                    ha="center",
                    va="center",
                    fontsize=8.8,
                    fontweight="bold",
                    color=d_col,
                    bbox=dict(
                        boxstyle="round,pad=0.22,rounding_size=0.35",
                        facecolor="#F8FAFC",
                        edgecolor=d_col,
                        lw=1.0,
                    ),
                    zorder=6,
                )
            )

    despine_axes(ax, grid_axis="y", grid_alpha=0.45)
    if kwargs.get("show_legend", True):
        ax.legend(frameon=False, loc="upper right", ncol=2, fontsize=9.5)

    return {
        "bars_a": bars_a,
        "bars_b": bars_b,
        "annotations": anns,
        "ax": ax,
    }
