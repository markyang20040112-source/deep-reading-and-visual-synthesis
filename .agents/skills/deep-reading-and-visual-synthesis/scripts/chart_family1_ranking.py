"""
chart_family1_ranking.py
Chart Family 1: Cleveland dot, dumbbell / momentum vector arrow, slope, and bullet charts.
Note: `hcl_color_engine` is the public entry point.
"""

from typing import Dict, List, Optional, Sequence

from chart_common import (
    _decollide_1d_positions,
    _ensure_cjk_font,
    apply_spotlight_colors,
    despine_axes,
)
from chart_data import _parse_numeric_or_na
from color_core import (
    GEPHI_QUALITATIVE_HEX,
    GEPHI_SEQUENTIAL_SCALES,
    _resolve_lookup_color,
)

def plot_cleveland_dot(
    ax: object,
    labels: Sequence[str],
    values: Sequence[float],
    top_n: int = 1,
    bottom_n: int = 1,
    highlight_indices: Optional[Sequence[int]] = None,
    highlight_color: Optional[str] = None,
    context_color: str = "#94A3B8",
    stem_color: str = "#CBD5E1",
    stem_linestyle: str = "--",
    stem_linewidth: float = 1.0,
    value_fmt: str = "{:.1f}",
    value_offset_pts: float = 7.0,
    sort_values: bool = True,
    ascending: bool = True,
    x_padding_ratio: float = 0.14,
    category_color_map: Optional[Dict[str, str]] = None,
    **kwargs,
) -> Dict[str, object]:
    """
    Data 8 Editorial Cleveland Dot Plot:
    - Focuses X-axis on the true non-zero variation interval (unless `force_zero=True`).
    - Replaces heavy solid bars with horizontal dashed guide stems (`#CBD5E1`) + spotlight/context dots.
    - Applies `apply_spotlight_colors` to highlight top_n / bottom_n extremes in both dot color/size and Y-tick typography.
    - Places direct value labels immediately to the right of every dot.
    """
    _ensure_cjk_font()
    import numpy as np

    pairs = [
        (str(lbl), float(val))
        for lbl, val in zip(labels, values)
        if _parse_numeric_or_na(val) is not None
    ]
    if not pairs:
        return {"scatter": None, "stems": None, "annotations": [], "spotlight": None, "ax": ax}

    if sort_values:
        pairs.sort(key=lambda item: item[1], reverse=not ascending)

    sorted_labels = [p[0] for p in pairs]
    sorted_vals = [p[1] for p in pairs]
    n = len(pairs)
    y_pos = np.arange(n)

    spot = apply_spotlight_colors(
        sorted_vals,
        top_n=top_n,
        bottom_n=bottom_n,
        highlight_indices=highlight_indices,
        highlight_color=highlight_color,
        context_color=context_color,
        highlight_size=kwargs.pop("highlight_size", 110.0),
        context_size=kwargs.pop("context_size", 56.0),
    )
    if highlight_color is None:
        for i, is_hl in enumerate(spot["is_highlight"]):
            if is_hl:
                looked_up = _resolve_lookup_color(sorted_labels[i], category_color_map)
                if looked_up is not None:
                    spot["colors"][i] = looked_up

    v_min = min(sorted_vals)
    v_max = max(sorted_vals)
    span = max(1e-6, v_max - v_min)
    force_zero = bool(kwargs.pop("force_zero", False))
    custom_xlim = kwargs.pop("xlim", None)

    if custom_xlim is not None:
        x_left, x_right = float(custom_xlim[0]), float(custom_xlim[1])
    elif force_zero:
        x_left = 0.0
        x_right = v_max + span * max(0.16, float(x_padding_ratio))
    else:
        x_left = v_min - span * 0.11
        x_right = v_max + span * max(0.16, float(x_padding_ratio))

    ax.set_xlim(x_left, x_right)
    ax.set_ylim(-0.75, n - 0.25)

    stems = ax.hlines(
        y=y_pos,
        xmin=x_left,
        xmax=sorted_vals,
        color=stem_color,
        linestyle=stem_linestyle,
        linewidth=stem_linewidth,
        zorder=2,
    )

    sc = ax.scatter(
        sorted_vals,
        y_pos,
        s=spot["sizes"],
        c=spot["colors"],
        edgecolors="#FFFFFF",
        linewidths=1.5,
        zorder=4,
        **kwargs,
    )

    ax.set_yticks(y_pos)
    tick_labels = ax.set_yticklabels(sorted_labels, fontsize=10.5)
    for tick_lbl, t_color, t_weight in zip(tick_labels, spot["text_colors"], spot["fontweights"]):
        tick_lbl.set_color(t_color)
        tick_lbl.set_fontweight(t_weight)
    ax.tick_params(axis="y", length=0, pad=6)

    anns = []
    import matplotlib.patheffects as patheffects
    fontsize_val = float(kwargs.get("value_fontsize", 9.8))
    for i, (val, y_i) in enumerate(zip(sorted_vals, y_pos)):
        txt = value_fmt(val) if callable(value_fmt) else value_fmt.format(val)
        ann = ax.annotate(
            txt,
            xy=(val, float(y_i)),
            xytext=(float(value_offset_pts), 0.0),
            textcoords="offset points",
            va="center",
            ha="left",
            fontsize=fontsize_val,
            fontweight=spot["fontweights"][i],
            color=spot["text_colors"][i],
            zorder=7,
        )
        ann.set_path_effects([
            patheffects.Stroke(linewidth=2.8, foreground="#FFFFFF"),
            patheffects.Normal(),
        ])
        anns.append(ann)

    despine_axes(ax, grid_axis="x", grid_alpha=0.45)
    return {
        "scatter": sc,
        "stems": stems,
        "annotations": anns,
        "spotlight": spot,
        "labels": sorted_labels,
        "values": sorted_vals,
        "ax": ax,
    }


def plot_dumbbell(
    ax: object,
    labels: Sequence[str],
    val_start: Sequence[float],
    val_end: Sequence[float],
    label_start: str = "期初 / 基準",
    label_end: str = "期末 / 現況",
    color_start: Optional[str] = None,
    color_end: Optional[str] = None,
    bar_color: str = "#CBD5E1",
    bar_linewidth: float = 3.2,
    dot_size: float = 90.0,
    show_delta: bool = True,
    delta_fmt: str = "{:+.1f}",
    sort_by: Optional[str] = "end",
    directed: bool = False,
    category_color_map: Optional[Dict[str, str]] = None,
    **kwargs,
) -> Dict[str, object]:
    """
    Dumbbell Span Plot & Directional Momentum Vector Arrow Plot.

    - ``directed=False`` (default): Neutral dual-state dumbbell span plot
      (solid start/end dots connected by a neutral bar + inline delta label).
    - ``directed=True``: Directional origin-to-outcome momentum arrow plot
      (hollow circle origin -> solid directional arrowhead, direction-coded
      positive/negative colors, optional subtle row shading, and a cleanly
      right-aligned delta column; uses native Matplotlib vector arrowheads to
      avoid Microsoft JhengHei broken-glyph arrow concatenation).
    """
    _ensure_cjk_font()
    import matplotlib.patches as mpatches
    import matplotlib.patheffects as pe
    import numpy as np

    c_start = (
        color_start
        if color_start is not None
        else (_resolve_lookup_color(label_start, category_color_map) or GEPHI_QUALITATIVE_HEX[1])
    )
    c_end = (
        color_end
        if color_end is not None
        else (_resolve_lookup_color(label_end, category_color_map) or GEPHI_QUALITATIVE_HEX[0])
    )

    rows = []
    for lbl, vs, ve in zip(labels, val_start, val_end):
        ps, pe_val = _parse_numeric_or_na(vs), _parse_numeric_or_na(ve)
        if ps is not None and pe_val is not None:
            rows.append((str(lbl), float(ps), float(pe_val), float(pe_val - ps)))

    if not rows:
        return {
            "scatter_start": None,
            "scatter_end": None,
            "bars": None,
            "arrows": [],
            "annotations": [],
            "ax": ax,
        }

    if sort_by == "end":
        rows.sort(key=lambda r: r[2])
    elif sort_by == "start":
        rows.sort(key=lambda r: r[1])
    elif sort_by == "delta":
        rows.sort(key=lambda r: r[3])

    n = len(rows)
    y_pos = np.arange(n)
    r_labels = [r[0] for r in rows]
    r_start = [r[1] for r in rows]
    r_end = [r[2] for r in rows]
    r_delta = [r[3] for r in rows]

    all_vals = r_start + r_end
    v_min, v_max = min(all_vals), max(all_vals)
    raw_span = v_max - v_min
    span = raw_span if raw_span > 1e-6 else max(1.0, abs(v_max) * 0.25)

    default_orange = ["#FFF3EA", "#FBD8C0", "#ECA072", "#CA6F35", "#97481B"]
    default_blue = ["#EBF7F9", "#BCE2EB", "#5DBACD", "#2C8B9F", "#0E5B6B"]
    pos_ink = GEPHI_SEQUENTIAL_SCALES.get("orange", default_orange)[3]
    neg_ink = GEPHI_SEQUENTIAL_SCALES.get("blue", default_blue)[3]

    arrows = []
    anns = []

    if not directed:
        bars = ax.hlines(
            y=y_pos,
            xmin=[min(a, b) for a, b in zip(r_start, r_end)],
            xmax=[max(a, b) for a, b in zip(r_start, r_end)],
            color=bar_color,
            linewidth=bar_linewidth,
            zorder=2,
        )
        sc_start = ax.scatter(
            r_start,
            y_pos,
            s=dot_size,
            color=c_start,
            edgecolors="#FFFFFF",
            linewidths=1.5,
            label=label_start,
            zorder=4,
        )
        sc_end = ax.scatter(
            r_end,
            y_pos,
            s=dot_size,
            color=c_end,
            edgecolors="#FFFFFF",
            linewidths=1.5,
            label=label_end,
            zorder=5,
        )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(r_labels, fontsize=10.5, fontweight="bold", color="#1E293B")
        ax.tick_params(axis="y", length=0, pad=6)

        ax.set_xlim(v_min - span * 0.10, v_max + span * 0.16)
        ax.set_ylim(-0.65, n - 0.30)

        if show_delta:
            for y_i, vs, ve, d_val in zip(y_pos, r_start, r_end, r_delta):
                x_right_dot = max(vs, ve)
                d_txt = delta_fmt.format(d_val)
                d_col = pos_ink if d_val >= 0 else neg_ink
                ann = ax.annotate(
                    d_txt,
                    xy=(x_right_dot, float(y_i)),
                    xytext=(8.0, 0.0),
                    textcoords="offset points",
                    va="center",
                    ha="left",
                    fontsize=9.5,
                    fontweight="bold",
                    color=d_col,
                    zorder=6,
                )
                anns.append(ann)

        despine_axes(ax, grid_axis="x", grid_alpha=0.45)
        if kwargs.get("show_legend", True):
            ax.legend(frameon=False, loc="upper right", fontsize=9.5)

        return {
            "scatter_start": sc_start,
            "scatter_end": sc_end,
            "bars": bars,
            "arrows": arrows,
            "annotations": anns,
            "ax": ax,
        }

    # --- Directed Momentum Vector Arrow Mode (directed=True) ---
    pos_col = kwargs.get("pos_color") or (
        color_end if color_end is not None else pos_ink
    )
    neg_col = kwargs.get("neg_color") or (
        color_start if color_start is not None else neg_ink
    )
    zero_col = kwargs.get("zero_color", "#64748B")
    pos_shade = kwargs.get("pos_row_shade") or GEPHI_SEQUENTIAL_SCALES.get(
        "orange", default_orange
    )[0]
    neg_shade = kwargs.get("neg_row_shade", "#F8FAFC")
    row_shading = bool(kwargs.get("row_shading", True))
    arrow_lw = float(kwargs.get("arrow_linewidth", bar_linewidth))
    head_length = float(kwargs.get("head_length", 0.55))
    head_width = float(kwargs.get("head_width", 0.32))
    show_values = bool(kwargs.get("show_values", False))
    value_fmt = str(kwargs.get("value_fmt", "{:.1f}"))
    start_prefix = str(kwargs.get("start_prefix", ""))
    end_prefix = str(kwargs.get("end_prefix", ""))
    delta_header = kwargs.get("delta_header")
    force_zero = bool(kwargs.get("force_zero", False))
    stroke_halo = [pe.withStroke(linewidth=3.0, foreground="#FFFFFF")]

    row_colors = [
        pos_col if d > 0 else (neg_col if d < 0 else zero_col) for d in r_delta
    ]

    def _est_text_pts(text: str, fontsize: float) -> float:
        """Estimate horizontal display width in points for mixed CJK/ASCII text."""
        width_units = 0.0
        for ch in str(text):
            width_units += 1.02 if ord(ch) > 127 else 0.58
        return width_units * fontsize

    fig_obj = ax.figure
    ax_bbox_frac = ax.get_position()
    ax_width_pts = max(
        180.0, float(fig_obj.get_figwidth()) * float(ax_bbox_frac.width) * 72.0
    )

    # Pre-format strings so horizontal padding adapts dynamically to label widths
    start_texts = [f"{start_prefix}{value_fmt.format(vs)}" for vs in r_start]
    end_texts = [f"{end_prefix}{value_fmt.format(ve)}" for ve in r_end]
    delta_texts = [delta_fmt.format(d_val) for d_val in r_delta]

    delta_col_pts = 0.0
    if show_delta:
        delta_col_pts = max((_est_text_pts(t, 9.6) for t in delta_texts), default=0.0)
        if delta_header:
            delta_col_pts = max(delta_col_pts, _est_text_pts(str(delta_header), 9.4))
        delta_col_pts += 12.0  # right margin + column separation

    # Estimate dynamic left/right padding in data units (iterated to converge)
    x_pad_left_override = kwargs.get("x_pad_left_ratio")
    x_pad_right_override = kwargs.get("x_pad_right_ratio")
    base_left_ratio = (
        float(x_pad_left_override)
        if x_pad_left_override is not None
        else (0.16 if show_values else 0.10)
    )
    default_right_pad = (
        (0.38 if show_values else 0.28)
        if show_delta
        else (0.18 if show_values else 0.14)
    )
    base_right_ratio = (
        float(x_pad_right_override)
        if x_pad_right_override is not None
        else default_right_pad
    )

    x_lo = (min(0.0, v_min) if force_zero else v_min) - span * base_left_ratio
    if force_zero and v_min >= 0.0 and x_pad_left_override is None:
        # Start from 0.0 for non-negative data; expand left only if a label needs room
        x_lo = 0.0
    x_hi = v_max + span * base_right_ratio

    for _ in range(3):
        curr_data_span = max(1e-6, x_hi - x_lo)
        pts_to_data = curr_data_span / ax_width_pts

        if x_pad_left_override is None:
            needed_lo = (
                0.0 if (force_zero and v_min >= 0.0) else v_min - span * base_left_ratio
            )
            if show_values:
                for vs, ve, d_val, s_txt, e_txt in zip(
                    r_start, r_end, r_delta, start_texts, end_texts
                ):
                    if abs(d_val) <= 1e-9:
                        continue
                    left_val = vs if d_val > 0 else ve
                    left_txt = s_txt if d_val > 0 else e_txt
                    left_fs = 8.8 if d_val > 0 else 9.0
                    left_need_pts = _est_text_pts(left_txt, left_fs) + 14.0
                    needed_lo = min(needed_lo, left_val - left_need_pts * pts_to_data)
            else:
                needed_lo = min(needed_lo, v_min - 14.0 * pts_to_data)
            if force_zero and v_min >= 0.0:
                x_lo = min(0.0, needed_lo)
            else:
                x_lo = min(x_lo, needed_lo)

        if x_pad_right_override is None:
            needed_hi = v_max + span * base_right_ratio
            right_label_max_x = v_max + 12.0 * pts_to_data
            if show_values:
                for vs, ve, d_val, s_txt, e_txt in zip(
                    r_start, r_end, r_delta, start_texts, end_texts
                ):
                    if abs(d_val) <= 1e-9:
                        right_val, right_txt, right_fs = ve, e_txt, 8.8
                    elif d_val > 0:
                        right_val, right_txt, right_fs = ve, e_txt, 9.0
                    else:
                        right_val, right_txt, right_fs = vs, s_txt, 8.8
                    right_need_pts = _est_text_pts(right_txt, right_fs) + 14.0
                    right_label_max_x = max(
                        right_label_max_x, right_val + right_need_pts * pts_to_data
                    )
            if show_delta:
                # Keep clean separation between rightmost value label and delta column
                gap_pts = 14.0
                needed_hi = max(
                    needed_hi,
                    right_label_max_x + (gap_pts + delta_col_pts) * pts_to_data,
                )
            else:
                needed_hi = max(needed_hi, right_label_max_x + 6.0 * pts_to_data)
            x_hi = max(x_hi, needed_hi)

    total_x_span = max(1e-6, x_hi - x_lo)
    pts_per_data = ax_width_pts / total_x_span

    bars = []
    for y_i, vs, ve, d_val, col in zip(y_pos, r_start, r_end, r_delta, row_colors):
        if row_shading:
            span_patch = ax.axhspan(
                float(y_i) - 0.36,
                float(y_i) + 0.36,
                color=pos_shade if d_val > 0 else neg_shade,
                zorder=1,
            )
            bars.append(span_patch)

        if abs(d_val) > 1e-9:
            dx_pts = abs(d_val) * pts_per_data
            # Prevent FancyArrowPatch shrinkA > segment length from inverting arrows
            if dx_pts >= 9.0:
                eff_shrink_a = min(4.0, dx_pts * 0.30)
                eff_hl = min(head_length, max(0.32, dx_pts / 24.0))
                eff_hw = min(head_width, max(0.22, eff_hl * 0.60))
                arr = ax.annotate(
                    "",
                    xy=(ve, float(y_i)),
                    xytext=(vs, float(y_i)),
                    arrowprops=dict(
                        arrowstyle=(
                            f"-|>,head_length={eff_hl:.2f},head_width={eff_hw:.2f}"
                        ),
                        color=col,
                        lw=arrow_lw,
                        shrinkA=eff_shrink_a,
                        shrinkB=0,
                    ),
                    zorder=4,
                )
                arrows.append(arr)
            else:
                # Ultra-short delta: place solid directional triangle beside origin
                direction = 1.0 if d_val > 0 else -1.0
                tip_x = vs + direction * (max(dx_pts, 6.2) / pts_per_data)
                tri_marker = ">" if d_val > 0 else "<"
                tri_pts = ax.scatter(
                    [tip_x],
                    [float(y_i)],
                    marker=tri_marker,
                    s=max(32.0, dot_size * 0.42),
                    color=col,
                    edgecolors="none",
                    zorder=4,
                )
                arrows.append(tri_pts)

    sc_start = ax.scatter(
        r_start,
        y_pos,
        s=dot_size,
        facecolors="#FFFFFF",
        edgecolors=row_colors,
        linewidths=2.0,
        zorder=5,
    )
    sc_end = None

    ax.set_yticks(y_pos)
    ax.set_yticklabels(r_labels, fontsize=10.5, fontweight="bold", color="#1E293B")
    ax.tick_params(axis="y", length=0, pad=6)

    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(-0.65, (n - 0.05) if delta_header else (n - 0.30))

    # Keep x-ticks strictly inside valid data bounds (no negative ticks for non-negative
    # force_zero data, and no ticks extending under/past the right-hand delta column).
    x_delta_col = x_hi - max(6.0 / pts_per_data, span * 0.020)
    tick_lo_bound = 0.0 if (force_zero and v_min >= 0.0) else x_lo + 4.0 / pts_per_data
    if show_delta:
        delta_left_edge = x_delta_col - (delta_col_pts + 4.0) / pts_per_data
        tick_hi_bound = min(delta_left_edge, x_hi - 8.0 / pts_per_data)
        if tick_hi_bound < v_max:
            tick_hi_bound = min(v_max, x_delta_col - delta_col_pts / pts_per_data)
    else:
        tick_hi_bound = x_hi - 8.0 / pts_per_data

    raw_ticks = list(ax.get_xticks())
    valid_ticks = [
        t for t in raw_ticks if (tick_lo_bound - 1e-9) <= t <= (tick_hi_bound + 1e-9)
    ]
    if len(valid_ticks) >= 2:
        ax.set_xticks(valid_ticks)
    ax.set_xlim(x_lo, x_hi)

    if show_values:
        for y_i, vs, ve, d_val, col, s_txt, e_txt in zip(
            y_pos, r_start, r_end, r_delta, row_colors, start_texts, end_texts
        ):
            if abs(d_val) <= 1e-9:
                anns.append(
                    ax.annotate(
                        e_txt,
                        xy=(ve, float(y_i)),
                        xytext=(8.0, 0.0),
                        textcoords="offset points",
                        va="center",
                        ha="left",
                        fontsize=8.8,
                        fontweight="bold",
                        color=col,
                        path_effects=stroke_halo,
                        zorder=6,
                    )
                )
            elif d_val > 0:
                anns.append(
                    ax.annotate(
                        s_txt,
                        xy=(vs, float(y_i)),
                        xytext=(-8.0, 0.0),
                        textcoords="offset points",
                        va="center",
                        ha="right",
                        fontsize=8.8,
                        color="#475569",
                        path_effects=stroke_halo,
                        zorder=6,
                    )
                )
                anns.append(
                    ax.annotate(
                        e_txt,
                        xy=(ve, float(y_i)),
                        xytext=(8.0, 0.0),
                        textcoords="offset points",
                        va="center",
                        ha="left",
                        fontsize=9.0,
                        fontweight="bold",
                        color=col,
                        path_effects=stroke_halo,
                        zorder=6,
                    )
                )
            else:
                anns.append(
                    ax.annotate(
                        e_txt,
                        xy=(ve, float(y_i)),
                        xytext=(-8.0, 0.0),
                        textcoords="offset points",
                        va="center",
                        ha="right",
                        fontsize=9.0,
                        fontweight="bold",
                        color=col,
                        path_effects=stroke_halo,
                        zorder=6,
                    )
                )
                anns.append(
                    ax.annotate(
                        s_txt,
                        xy=(vs, float(y_i)),
                        xytext=(8.0, 0.0),
                        textcoords="offset points",
                        va="center",
                        ha="left",
                        fontsize=8.8,
                        color="#475569",
                        path_effects=stroke_halo,
                        zorder=6,
                    )
                )

    if show_delta:
        for y_i, d_txt, col in zip(y_pos, delta_texts, row_colors):
            ann = ax.text(
                x_delta_col,
                float(y_i),
                d_txt,
                va="center",
                ha="right",
                fontsize=9.4,
                fontweight="bold",
                color=col,
                zorder=6,
            )
            anns.append(ann)
        if delta_header:
            anns.append(
                ax.text(
                    x_delta_col,
                    n - 0.42,
                    str(delta_header),
                    va="bottom",
                    ha="right",
                    fontsize=9.2,
                    fontweight="bold",
                    color="#475569",
                    zorder=6,
                )
            )

    despine_axes(ax, grid_axis="x", grid_alpha=0.45)
    if kwargs.get("show_legend", True):
        pos_label = kwargs.get(
            "pos_label", f"正向推進（{label_end} > {label_start}）"
        )
        neg_label = kwargs.get(
            "neg_label", f"負向回縮（{label_end} < {label_start}）"
        )
        handles = [
            mpatches.Patch(facecolor=pos_col, label=pos_label),
            mpatches.Patch(facecolor=neg_col, label=neg_label),
        ]
        leg_kwargs = dict(
            loc="lower left",
            bbox_to_anchor=(-0.01, 1.015),
            ncol=2,
            frameon=False,
            fontsize=9.4,
        )
        if isinstance(kwargs.get("legend_kwargs"), dict):
            leg_kwargs.update(kwargs["legend_kwargs"])
        ax.legend(handles=handles, **leg_kwargs)

    return {
        "scatter_start": sc_start,
        "scatter_end": sc_end,
        "bars": bars,
        "arrows": arrows,
        "annotations": anns,
        "ax": ax,
    }


def plot_slope_chart(
    ax: object,
    labels: Sequence[str],
    val_t1: Sequence[float],
    val_t2: Sequence[float],
    t1_label: str = "期初 (T1)",
    t2_label: str = "期末 (T2)",
    up_color: Optional[str] = None,
    down_color: Optional[str] = None,
    neutral_color: str = "#94A3B8",
    value_fmt: str = "{:.1f}",
    linewidth: float = 2.4,
    dot_size: float = 75.0,
    **kwargs,
) -> Dict[str, object]:
    """
    Data 5 & Data 7 Two-Period Ranking & Trajectory Slope Chart with 1D vertical label collision avoidance.
    """
    _ensure_cjk_font()

    c_up = up_color if up_color is not None else GEPHI_QUALITATIVE_HEX[0]
    c_down = down_color if down_color is not None else GEPHI_QUALITATIVE_HEX[1]
    threshold = float(kwargs.pop("threshold", 1e-6))

    rows = []
    for lbl, v1, v2 in zip(labels, val_t1, val_t2):
        p1, p2 = _parse_numeric_or_na(v1), _parse_numeric_or_na(v2)
        if p1 is not None and p2 is not None:
            rows.append((str(lbl), float(p1), float(p2)))

    if not rows:
        return {"lines": [], "annotations": [], "ax": ax}

    v_all = [r[1] for r in rows] + [r[2] for r in rows]
    v_min, v_max = min(v_all), max(v_all)
    v_span = max(1e-6, v_max - v_min)

    ax.axvline(0.0, color="#CBD5E1", linestyle="--", linewidth=1.2, zorder=1)
    ax.axvline(1.0, color="#CBD5E1", linestyle="--", linewidth=1.2, zorder=1)

    y1_adj = _decollide_1d_positions([r[1] for r in rows], min_dist=v_span * 0.055)
    y2_adj = _decollide_1d_positions([r[2] for r in rows], min_dist=v_span * 0.055)

    lines = []
    anns = []
    for idx, (lbl, v1, v2) in enumerate(rows):
        diff = v2 - v1
        if diff > threshold:
            col = c_up
            fw = "bold"
            t_col = "#0F172A"
        elif diff < -threshold:
            col = c_down
            fw = "bold"
            t_col = "#0F172A"
        else:
            col = neutral_color
            fw = "normal"
            t_col = "#475569"

        ln = ax.plot([0.0, 1.0], [v1, v2], color=col, linewidth=linewidth, zorder=3)[0]
        ax.scatter([0.0, 1.0], [v1, v2], s=dot_size, color=col, edgecolors="#FFFFFF", linewidths=1.5, zorder=4)
        lines.append(ln)

        ann_left = ax.annotate(
            f"{lbl}  {value_fmt.format(v1)}",
            xy=(0.0, v1),
            xytext=(-0.05, y1_adj[idx]),
            textcoords="data",
            ha="right",
            va="center",
            fontsize=9.8,
            fontweight=fw,
            color=t_col,
            zorder=5,
        )
        ann_right = ax.annotate(
            f"{value_fmt.format(v2)}  {lbl}",
            xy=(1.0, v2),
            xytext=(1.05, y2_adj[idx]),
            textcoords="data",
            ha="left",
            va="center",
            fontsize=9.8,
            fontweight=fw,
            color=t_col,
            zorder=5,
        )
        anns.extend([ann_left, ann_right])

    ax.set_xlim(-0.42, 1.42)
    ax.set_ylim(v_min - v_span * 0.10, v_max + v_span * 0.12)
    ax.set_xticks([0.0, 1.0])
    ax.set_xticklabels([t1_label, t2_label], fontsize=11.0, fontweight="bold", color="#0F172A")
    ax.set_yticks([])
    for side in ("top", "right", "left", "bottom"):
        if side in ax.spines:
            ax.spines[side].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=8)

    return {"lines": lines, "annotations": anns, "ax": ax}


def plot_bullet(
    ax: object,
    labels: Sequence[str],
    actuals: Sequence[float],
    targets: Sequence[float],
    bands: Optional[Sequence[Sequence[float]]] = None,
    band_colors: Optional[Sequence[str]] = None,
    actual_color: Optional[str] = None,
    target_color: str = "#0F172A",
    bar_height: float = 0.60,
    actual_height: float = 0.28,
    value_fmt: str = "{:.1f}",
    **kwargs,
) -> Dict[str, object]:
    """
    Data 5 Stephen Few (2006) Bullet Graph:
    Encodes actual performance bar, target perpendicular reference marker, and 3-tier qualitative background ranges.
    """
    _ensure_cjk_font()
    import numpy as np

    n = min(len(labels), len(actuals), len(targets))
    if n == 0:
        return {"actual_bars": None, "target_lines": [], "band_bars": [], "ax": ax}

    c_actual = (
        actual_color
        if actual_color is not None
        else GEPHI_SEQUENTIAL_SCALES.get("blue", ["#EBF7F9", "#BCE2EB", "#5DBACD", "#2C8B9F", "#0E5B6B"])[3]
    )
    b_colors = list(band_colors) if band_colors is not None else ["#CBD5E1", "#E2E8F0", "#F1F5F9"]

    y_pos = np.arange(n)
    clean_labels = [str(labels[i]) for i in range(n)]
    clean_actuals = [float(actuals[i]) for i in range(n)]
    clean_targets = [float(targets[i]) for i in range(n)]

    resolved_bands: List[List[float]] = []
    if bands is not None and len(bands) > 0:
        if isinstance(bands[0], (int, float)):
            shared = sorted(float(x) for x in bands)
            resolved_bands = [list(shared) for _ in range(n)]
        else:
            for i in range(n):
                row_b = bands[i] if i < len(bands) else bands[-1]
                resolved_bands.append(sorted(float(x) for x in row_b))
    else:
        for act, tgt in zip(clean_actuals, clean_targets):
            ref = max(act, tgt, 1.0)
            resolved_bands.append([0.65 * ref, 0.95 * ref, 1.20 * ref])

    band_bars = []
    max_x = 0.0
    for i, y_i in enumerate(y_pos):
        tiers = resolved_bands[i]
        max_x = max(max_x, tiers[-1], clean_actuals[i], clean_targets[i])
        prev = 0.0
        for t_idx, tier_end in enumerate(tiers):
            w = max(0.0, tier_end - prev)
            col = b_colors[min(t_idx, len(b_colors) - 1)]
            b_patch = ax.barh(
                y_i,
                w,
                left=prev,
                height=bar_height,
                color=col,
                edgecolor="none",
                zorder=1,
            )
            band_bars.append(b_patch)
            prev = tier_end

    actual_bars = ax.barh(
        y_pos,
        clean_actuals,
        height=actual_height,
        color=c_actual,
        edgecolor="none",
        zorder=3,
        label=kwargs.get("actual_label", "實際值 (Actual)"),
    )

    target_lines = []
    for i, (y_i, tgt) in enumerate(zip(y_pos, clean_targets)):
        tl = ax.plot(
            [tgt, tgt],
            [y_i - bar_height * 0.44, y_i + bar_height * 0.44],
            color=target_color,
            linewidth=2.6,
            zorder=4,
            label=kwargs.get("target_label", "目標值 (Target)") if i == 0 else None,
        )[0]
        target_lines.append(tl)

    anns = []
    for y_i, act, tgt, tiers in zip(y_pos, clean_actuals, clean_targets, resolved_bands):
        right_edge = max(tiers[-1], act, tgt)
        pct = (act / tgt * 100.0) if abs(tgt) > 1e-9 else 0.0
        ann = ax.annotate(
            f"{value_fmt.format(act)} / 目標 {value_fmt.format(tgt)} ({pct:.0f}%)",
            xy=(right_edge, float(y_i)),
            xytext=(8.0, 0.0),
            textcoords="offset points",
            va="center",
            ha="left",
            fontsize=9.2,
            fontweight="bold",
            color="#0F172A",
            zorder=5,
        )
        anns.append(ann)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(clean_labels, fontsize=10.5, fontweight="bold", color="#0F172A")
    ax.tick_params(axis="y", length=0, pad=6)
    ax.set_xlim(0.0, max_x * 1.28)
    ax.set_ylim(-0.65, n - 0.30)
    despine_axes(ax, grid_axis="x", grid_alpha=0.40)

    return {
        "actual_bars": actual_bars,
        "target_lines": target_lines,
        "band_bars": band_bars,
        "annotations": anns,
        "ax": ax,
    }
