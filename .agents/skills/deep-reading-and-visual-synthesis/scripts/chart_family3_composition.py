"""
chart_family3_composition.py
Chart Family 3: Marimekko and waterfall composition charts.
Note: `hcl_color_engine` is the public entry point.
"""

from typing import Dict, List, Optional, Sequence

from chart_common import _ensure_cjk_font, despine_axes
from color_core import (
    GEPHI_DISCRETE_NEUTRALS,
    GEPHI_QUALITATIVE_HEX,
    _resolve_lookup_color,
    ink,
)

def plot_marimekko(
    ax: object,
    categories: Sequence[str],
    weights: Sequence[float],
    sub_matrix_pct: Sequence[Sequence[float]],
    sub_labels: Sequence[str],
    colors: Optional[Sequence[str]] = None,
    edgecolor: str = "#FFFFFF",
    linewidth: float = 1.6,
    show_cell_labels: bool = True,
    min_pct_for_label: float = 7.5,
    show_weight_header: bool = True,
    weight_fmt: str = "{:.0f}",
    category_color_map: Optional[Dict[str, str]] = None,
    **kwargs,
) -> Dict[str, object]:
    """
    Data 7 2D Marimekko / Mekko Chart:
    - Column X-width is proportional to each entity's scale/weight (`weights`), normalized to 0..100%.
    - Column Y-height is a 0..100% stacked composition across `sub_labels`.
    - Automatically checks WCAG contrast via `ink()` for direct in-cell labels.
    """
    _ensure_cjk_font()
    from matplotlib.patches import Rectangle
    import numpy as np

    n_cats = len(categories)
    n_subs = len(sub_labels)
    if n_cats == 0 or n_subs == 0:
        return {"patches": [], "annotations": [], "x_edges": [], "ax": ax}

    w_arr = np.asarray([max(0.0, float(w)) for w in weights[:n_cats]], dtype="float64")
    total_w = float(w_arr.sum())
    if total_w <= 0:
        w_shares = np.full(n_cats, 100.0 / n_cats)
    else:
        w_shares = (w_arr / total_w) * 100.0

    mat = np.asarray(sub_matrix_pct, dtype="float64")
    if mat.shape == (n_cats, n_subs):
        cat_sub_mat = mat.copy()
    elif mat.shape == (n_subs, n_cats):
        cat_sub_mat = mat.T.copy()
    else:
        raise ValueError(
            f"sub_matrix_pct shape {mat.shape} does not match categories ({n_cats}) x sub_labels ({n_subs})."
        )

    # Normalize each category column to sum to 100%
    for i in range(n_cats):
        col_sum = float(cat_sub_mat[i].sum())
        if col_sum > 0:
            cat_sub_mat[i] = (cat_sub_mat[i] / col_sum) * 100.0

    if colors is not None:
        sub_colors = list(colors)
    else:
        looked_up = [_resolve_lookup_color(lbl, category_color_map) for lbl in sub_labels[:n_subs]]
        if any(c is not None for c in looked_up):
            used_upper = {str(c).upper() for c in looked_up if c is not None}
            pool = [c for c in GEPHI_QUALITATIVE_HEX if str(c).upper() not in used_upper]
            pool.append(GEPHI_DISCRETE_NEUTRALS["other_aggregated"])
            pool_iter = iter(pool)
            sub_colors = []
            for c in looked_up:
                if c is not None:
                    sub_colors.append(c)
                else:
                    sub_colors.append(next(pool_iter, "#94A3B8"))
        else:
            base_cols = list(GEPHI_QUALITATIVE_HEX)
            if n_subs > 4:
                base_cols.append(GEPHI_DISCRETE_NEUTRALS["other_aggregated"])
                while len(base_cols) < n_subs:
                    base_cols.append("#94A3B8")
            sub_colors = base_cols[:n_subs]

    x_edges = [0.0]
    for w_s in w_shares:
        x_edges.append(x_edges[-1] + float(w_s))

    patches = []
    anns = []
    legend_handles = []

    for j in range(n_subs):
        col_hex = sub_colors[j % len(sub_colors)]
        proxy = Rectangle((0, 0), 1, 1, facecolor=col_hex, edgecolor=edgecolor, linewidth=linewidth, label=str(sub_labels[j]))
        legend_handles.append(proxy)

    for i in range(n_cats):
        x0 = x_edges[i]
        w = w_shares[i]
        y_bot = 0.0
        for j in range(n_subs):
            h_pct = float(cat_sub_mat[i, j])
            col_hex = sub_colors[j % len(sub_colors)]
            rect = Rectangle(
                (x0, y_bot),
                w,
                h_pct,
                facecolor=col_hex,
                edgecolor=edgecolor,
                linewidth=linewidth,
                zorder=2,
            )
            ax.add_patch(rect)
            patches.append(rect)

            if show_cell_labels and h_pct >= min_pct_for_label and w >= 7.5:
                cell_ink = ink(col_hex)
                label_str = f"{sub_labels[j]}\n{h_pct:.1f}%" if (h_pct >= 13.5 and w >= 12.0) else f"{h_pct:.1f}%"
                ann = ax.text(
                    x0 + 0.5 * w,
                    y_bot + 0.5 * h_pct,
                    label_str,
                    ha="center",
                    va="center",
                    fontsize=8.8 if w >= 12.0 else 8.0,
                    fontweight="bold",
                    color=cell_ink,
                    zorder=4,
                )
                anns.append(ann)
            y_bot += h_pct

        if show_weight_header:
            w_txt = weight_fmt.format(w_arr[i])
            hdr = ax.text(
                x0 + 0.5 * w,
                101.5,
                w_txt,
                ha="center",
                va="bottom",
                fontsize=8.8,
                fontweight="bold",
                color="#334155",
                zorder=4,
            )
            anns.append(hdr)

    x_mids = [0.5 * (x_edges[i] + x_edges[i + 1]) for i in range(n_cats)]
    x_tick_labels = [f"{categories[i]}\n({w_shares[i]:.1f}%)" for i in range(n_cats)]
    ax.set_xticks(x_mids)
    ax.set_xticklabels(x_tick_labels, fontsize=9.8, fontweight="bold", color="#0F172A")
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_xlim(0.0, 100.0)
    ax.set_ylim(0.0, 108.0 if show_weight_header else 101.0)
    ax.set_ylabel("結構佔比 (%)", fontsize=10.5, fontweight="bold", color="#0F172A")
    despine_axes(ax, grid_axis=None)
    if hasattr(ax, "spines") and "left" in ax.spines:
        ax.spines["left"].set_bounds(0.0, 100.0)

    title_str = kwargs.get("title")
    show_leg = bool(kwargs.get("show_legend", True))
    legend_ncol = int(kwargs.get("legend_ncol", min(n_subs, 5)))
    legend_rows = max(1, (n_subs + max(1, legend_ncol) - 1) // max(1, legend_ncol)) if show_leg else 0
    default_title_pad = (28.0 + 18.0 * (legend_rows - 1)) if show_leg else 14.0
    title_pad = float(kwargs.get("title_pad", default_title_pad))

    if show_leg and hasattr(ax, "set_title"):
        _orig_set_title = getattr(ax, "_marimekko_orig_set_title", ax.set_title)
        ax._marimekko_orig_set_title = _orig_set_title
        ax._marimekko_min_title_pad = title_pad

        def _safe_set_title(label, fontdict=None, loc=None, pad=None, **st_kwargs):
            min_pad = getattr(ax, "_marimekko_min_title_pad", title_pad)
            eff_pad = max(float(pad), min_pad) if pad is not None else min_pad
            return _orig_set_title(label, fontdict=fontdict, loc=loc, pad=eff_pad, **st_kwargs)

        ax.set_title = _safe_set_title

    if title_str:
        ax.set_title(
            str(title_str),
            loc=str(kwargs.get("title_loc", "left")),
            fontsize=float(kwargs.get("title_fontsize", 12.5)),
            fontweight="bold",
            color="#0F172A",
            pad=title_pad,
        )
    elif show_leg and hasattr(ax, "get_title"):
        for _loc, _attr in (("left", "_left_title"), ("center", "title"), ("right", "_right_title")):
            existing_t = ax.get_title(loc=_loc)
            if existing_t:
                t_obj = getattr(ax, _attr, None)
                saved_fs = t_obj.get_fontsize() if t_obj is not None else None
                saved_fw = t_obj.get_fontweight() if t_obj is not None else None
                saved_col = t_obj.get_color() if t_obj is not None else None
                st_kw = {"loc": _loc, "pad": title_pad}
                if saved_fs is not None:
                    st_kw["fontsize"] = saved_fs
                if saved_fw is not None:
                    st_kw["fontweight"] = saved_fw
                if saved_col is not None:
                    st_kw["color"] = saved_col
                ax.set_title(existing_t, **st_kw)

    if show_leg:
        legend_loc = str(kwargs.get("legend_loc", "lower left"))
        default_anchor = (0.0, 1.005 if show_weight_header else 1.01)
        legend_anchor = kwargs.get("legend_bbox_to_anchor", default_anchor)
        ax.legend(
            handles=legend_handles,
            loc=legend_loc,
            bbox_to_anchor=legend_anchor,
            ncol=max(1, legend_ncol),
            frameon=False,
            fontsize=8.8,
            columnspacing=1.2,
            handletextpad=0.45,
            borderaxespad=0.0,
        )

    return {
        "patches": patches,
        "annotations": anns,
        "x_edges": x_edges,
        "width_shares": w_shares.tolist(),
        "ax": ax,
    }


def plot_waterfall(
    ax: object,
    step_labels: Sequence[str],
    deltas: Sequence[float],
    is_total_flags: Optional[Sequence[bool]] = None,
    pos_color: Optional[str] = None,
    neg_color: Optional[str] = None,
    total_color: str = "#334155",
    connector_color: str = "#94A3B8",
    connector_linestyle: str = "--",
    bar_width: float = 0.56,
    value_fmt: str = "{:+.1f}",
    total_fmt: str = "{:.1f}",
    **kwargs,
) -> Dict[str, object]:
    """
    Data 2, 3 & 7 Bridge Waterfall Chart with floating positive/negative bars and horizontal dashed step connectors.
    """
    _ensure_cjk_font()
    import numpy as np

    n = min(len(step_labels), len(deltas))
    if n == 0:
        return {"bars": None, "connectors": [], "annotations": [], "ax": ax}

    c_pos = pos_color if pos_color is not None else GEPHI_QUALITATIVE_HEX[0]
    c_neg = neg_color if neg_color is not None else GEPHI_QUALITATIVE_HEX[1]

    clean_labels = [str(step_labels[i]) for i in range(n)]
    clean_vals = [float(deltas[i]) for i in range(n)]

    if is_total_flags is not None:
        totals_mask = [bool(f) for f in is_total_flags[:n]]
    else:
        totals_mask = [False] * n
        totals_mask[0] = True
        if n >= 3 and abs(sum(clean_vals[:-1]) - clean_vals[-1]) <= max(1e-4, abs(clean_vals[-1]) * 1e-3):
            totals_mask[-1] = True
        elif any(any(k in clean_labels[-1].lower() for k in ("期末", "總計", "合計", "total", "net")) for _ in (0,)):
            totals_mask[-1] = True

    bottoms: List[float] = []
    heights: List[float] = []
    end_levels: List[float] = []
    bar_colors: List[str] = []

    running = 0.0
    for i, (val, is_tot) in enumerate(zip(clean_vals, totals_mask)):
        if is_tot:
            # If user passed 0 or match for final total, use running sum if val == 0 and i > 0
            eff_tot = running if (i > 0 and abs(val) < 1e-12) else val
            bottoms.append(0.0)
            heights.append(eff_tot)
            running = eff_tot
            end_levels.append(running)
            bar_colors.append(total_color)
        else:
            bottoms.append(running)
            heights.append(val)
            running += val
            end_levels.append(running)
            bar_colors.append(c_pos if val >= 0 else c_neg)

    x_pos = np.arange(n)
    bars = ax.bar(
        x_pos,
        heights,
        bottom=bottoms,
        width=bar_width,
        color=bar_colors,
        edgecolor="#FFFFFF",
        linewidth=1.3,
        zorder=3,
    )

    connectors = []
    for i in range(n - 1):
        y_conn = end_levels[i]
        ln = ax.plot(
            [x_pos[i] + bar_width * 0.5, x_pos[i + 1] - bar_width * 0.5],
            [y_conn, y_conn],
            color=connector_color,
            linestyle=connector_linestyle,
            linewidth=1.2,
            zorder=2,
        )[0]
        connectors.append(ln)

    ax.axhline(0.0, color="#CBD5E1", linewidth=1.0, zorder=1)

    all_y = [0.0] + bottoms + end_levels
    y_min, y_max = min(all_y), max(all_y)
    y_span = max(1e-6, y_max - y_min)
    ax.set_ylim(y_min - y_span * 0.14 if y_min < 0 else 0.0, y_max + y_span * 0.16)

    anns = []
    for i, (x_i, bot, h_val, end_v, is_tot) in enumerate(zip(x_pos, bottoms, heights, end_levels, totals_mask)):
        if is_tot:
            txt = total_fmt.format(h_val)
            y_anchor = max(0.0, h_val)
            va_align = "bottom"
            dy = 5.0
        else:
            txt = value_fmt.format(h_val)
            if h_val >= 0:
                y_anchor = bot + h_val
                va_align = "bottom"
                dy = 5.0
            else:
                y_anchor = bot + h_val
                va_align = "top"
                dy = -5.0
        ann = ax.annotate(
            txt,
            xy=(float(x_i), y_anchor),
            xytext=(0.0, dy),
            textcoords="offset points",
            ha="center",
            va=va_align,
            fontsize=9.5,
            fontweight="bold",
            color="#0F172A" if is_tot else bar_colors[i],
            zorder=5,
        )
        anns.append(ann)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(clean_labels, fontsize=10.0, fontweight="bold", color="#0F172A")
    despine_axes(ax, grid_axis="y", grid_alpha=0.45)

    return {
        "bars": bars,
        "connectors": connectors,
        "annotations": anns,
        "end_levels": end_levels,
        "ax": ax,
    }
