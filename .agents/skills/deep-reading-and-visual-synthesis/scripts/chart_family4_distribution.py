"""
chart_family4_distribution.py
Chart Family 4: Clipped KDE, context overlay grids, and distribution guardrail helpers.
Note: `hcl_color_engine` is the public entry point.
"""

import math
from typing import Dict, Optional, Sequence, Tuple

from chart_common import despine_axes
from chart_data import _parse_numeric_or_na
from color_core import (
    GEPHI_LIGHT_BADGE_TINTS,
    GEPHI_QUALITATIVE_HEX,
    GEPHI_SEQUENTIAL_SCALES,
)

def add_halo_vline(
    ax: object,
    x: float,
    color: Optional[str] = None,
    linestyle: str = "--",
    linewidth: float = 2.2,
    halo_color: str = "#FFFFFF",
    halo_width: float = 4.8,
    label: Optional[str] = None,
    zorder: int = 5,
):
    """
    Draw a vertical reference line (e.g. Mean / Median on a Histogram or KDE plot) with a mandatory
    white outer stroke/halo so it never visually merges with dark bars or bin boundaries.
    """
    import matplotlib.patheffects as patheffects

    resolved_color = color if color is not None else GEPHI_QUALITATIVE_HEX[0]
    line = ax.axvline(
        x=float(x),
        color=resolved_color,
        linestyle=linestyle,
        linewidth=linewidth,
        label=label,
        zorder=zorder,
    )
    line.set_path_effects([
        patheffects.Stroke(linewidth=halo_width, foreground=halo_color),
        patheffects.Normal(),
    ])
    return line


def annotate_floor_extreme(
    ax: object,
    x: float,
    y_floor: float = 0.0,
    label_text: str = "",
    dot_color: Optional[str] = None,
    dot_size: float = 46.0,
    arrow_height_ratio: float = 0.14,
    text_offset_x: float = 0.0,
    fontsize: float = 9.5,
    zorder: int = 6,
    label: Optional[str] = None,
    color: Optional[str] = None,
):
    """
    Safely annotate a right-tail extreme value whose histogram bar height is tiny (e.g. n=1, ~0.3% of Y-axis)
    and sits nearly flat on the horizontal axis:
    - Places a high-contrast anchor dot directly on the bottom axis at `(x, y_floor)` (with white halo).
    - Uses a short vertical arrow pointing straight down to the anchor dot instead of a long diagonal
      arrow pointing at empty air.
    """
    if label is not None and not label_text:
        label_text = label
    if color is not None:
        dot_color = color
    resolved_dot_color = dot_color if dot_color is not None else GEPHI_SEQUENTIAL_SCALES["orange"][4]
    y_min, y_max = ax.get_ylim()
    y_span = max(1e-6, y_max - y_min)
    text_y = float(y_floor) + y_span * float(arrow_height_ratio)

    ax.scatter(
        [float(x)],
        [float(y_floor)],
        s=dot_size,
        color=resolved_dot_color,
        edgecolors="#FFFFFF",
        linewidths=1.5,
        zorder=zorder + 1,
        clip_on=False,
    )
    ann = ax.annotate(
        str(label_text),
        xy=(float(x), float(y_floor)),
        xytext=(float(x) + float(text_offset_x), text_y),
        ha="center",
        va="bottom",
        fontsize=fontsize,
        fontweight="bold",
        color="#0F172A",
        bbox=dict(boxstyle="round,pad=0.3", facecolor=GEPHI_LIGHT_BADGE_TINTS[0], edgecolor=resolved_dot_color, linewidth=1.1),
        arrowprops=dict(arrowstyle="-|>", color=resolved_dot_color, lw=1.6, shrinkA=2, shrinkB=4),
        zorder=zorder + 2,
    )
    return ann


def compute_clipped_kde(
    data: Sequence[float],
    x_min: Optional[float] = 0.0,
    x_max: Optional[float] = None,
    bw_method: object = "scott",
    grid_size: int = 512,
) -> Tuple[object, object, float]:
    """
    Compute a 1D Gaussian Kernel Density Estimate with strict boundary clipping (e.g. `x >= 0` for non-negative
    variables like income/revenue) and area renormalization so `integral(density, x_min..x_max) == 1.0`.
    Returns `(x_grid, density_normalized, bandwidth_h)`.
    """
    import numpy as np

    arr = np.asarray([float(v) for v in data if _parse_numeric_or_na(v) is not None], dtype="float64")
    if arr.size == 0:
        raise ValueError("compute_clipped_kde received empty numeric data.")

    low_bound = float(x_min) if x_min is not None else float(arr.min())
    high_bound = float(x_max) if x_max is not None else float(arr.max())
    if high_bound <= low_bound:
        high_bound = low_bound + 1.0

    n = arr.size
    std_val = float(np.std(arr, ddof=1)) if n > 1 else 1.0
    iqr_val = float(np.percentile(arr, 75) - np.percentile(arr, 25)) if n > 1 else std_val
    sigma = min(std_val, iqr_val / 1.34) if (iqr_val > 0 and std_val > 0) else max(std_val, 1e-6)

    if isinstance(bw_method, (int, float)):
        h = float(bw_method)
    elif str(bw_method).lower() == "silverman":
        h = 0.9 * sigma * (n ** (-0.2))
    else:
        # Scott's rule default
        h = 1.06 * std_val * (n ** (-0.2))
    h = max(h, (high_bound - low_bound) * 1e-3)

    x_grid = np.linspace(low_bound, high_bound, int(max(64, grid_size)))
    diffs = (x_grid[:, None] - arr[None, :]) / h
    raw_density = np.mean(np.exp(-0.5 * (diffs ** 2)), axis=1) / (h * math.sqrt(2.0 * math.pi))

    trapz_fn = getattr(np, "trapezoid", None) or getattr(np, "trapz")
    area = float(trapz_fn(raw_density, x_grid))
    if area > 1e-12:
        density_norm = raw_density / area
    else:
        density_norm = raw_density

    return x_grid, density_norm, float(h)


def plot_clipped_kde(
    ax: object,
    data: Sequence[float],
    x_min: Optional[float] = 0.0,
    x_max: Optional[float] = None,
    bw_method: object = "scott",
    grid_size: int = 512,
    color: Optional[str] = None,
    fill_color: Optional[str] = None,
    fill_alpha: float = 0.28,
    linewidth: float = 2.2,
    label: Optional[str] = None,
    zorder: int = 3,
) -> Tuple[object, object, float]:
    """
    Plot a boundary-clipped, unit-area-renormalized (`Area = 1.0`) KDE curve on `ax`.
    Prevents Gaussian kernel spillover into impossible negative regions (`x < 0`).
    """
    resolved_color = color if color is not None else GEPHI_QUALITATIVE_HEX[0]
    x_grid, density_norm, h = compute_clipped_kde(
        data, x_min=x_min, x_max=x_max, bw_method=bw_method, grid_size=grid_size
    )
    ax.plot(x_grid, density_norm, color=resolved_color, linewidth=linewidth, label=label, zorder=zorder)
    if fill_color is not None or fill_alpha > 0:
        fc = fill_color if fill_color is not None else resolved_color
        ax.fill_between(x_grid, 0.0, density_norm, color=fc, alpha=fill_alpha, zorder=max(1, zorder - 1))
    return x_grid, density_norm, h


def setup_context_overlay_grid(
    n_panels: int,
    ncols: int = 4,
    figsize_per_panel: Tuple[float, float] = (4.2, 3.2),
    dpi: int = 300,
    xlim: Optional[Tuple[float, float]] = None,
    ylim: Optional[Tuple[float, float]] = None,
    baseline_data: Optional[Sequence[float]] = None,
    baseline_x_min: float = 0.0,
    baseline_bw: object = "scott",
    baseline_color: str = "#CBD5E1",
    baseline_fill_alpha: float = 0.35,
    baseline_label: str = "全體基準分布 (Context)",
):
    """
    Create a small-multiples facet grid enforcing the 8 Iron Laws of Context Overlay / Shadow Distribution:
    1. Plots the identical light-gray (`#CBD5E1`) full-population / baseline-year normalized density curve
       in the background of every active subplot (`zorder=1`).
    2. Locks identical X and Y axis limits across all panels (`sharex=True, sharey=True`), preventing deceptive
       per-panel auto-scaling.
    3. Returns `(fig, active_axes, baseline_info)` where `baseline_info` contains `{"x_grid", "density", "h"}`.
    """
    import matplotlib.pyplot as plt

    n_panels = max(1, int(n_panels))
    ncols = max(1, min(int(ncols), n_panels))
    nrows = int(math.ceil(n_panels / float(ncols)))

    fig_w = figsize_per_panel[0] * ncols
    fig_h = figsize_per_panel[1] * nrows
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(fig_w, fig_h),
        dpi=dpi,
        sharex=True,
        sharey=True,
        squeeze=False,
    )
    axes_flat = [ax for row in axes for ax in row]

    baseline_info = None
    if baseline_data is not None and len(baseline_data) > 0:
        x_max_bound = xlim[1] if xlim is not None else None
        x_min_bound = xlim[0] if xlim is not None else baseline_x_min
        bg_x, bg_y, bg_h = compute_clipped_kde(
            baseline_data, x_min=x_min_bound, x_max=x_max_bound, bw_method=baseline_bw
        )
        baseline_info = {"x_grid": bg_x, "density": bg_y, "h": bg_h}

    active_axes = []
    for idx, ax in enumerate(axes_flat):
        if idx >= n_panels:
            ax.set_visible(False)
            continue
        despine_axes(ax, grid_axis="y")
        if baseline_info is not None:
            ax.plot(
                baseline_info["x_grid"],
                baseline_info["density"],
                color="#94A3B8",
                linewidth=1.3,
                linestyle="-",
                label=baseline_label if idx == 0 else None,
                zorder=1,
            )
            ax.fill_between(
                baseline_info["x_grid"],
                0.0,
                baseline_info["density"],
                color=baseline_color,
                alpha=baseline_fill_alpha,
                zorder=1,
            )
        if xlim is not None:
            ax.set_xlim(xlim[0], xlim[1])
        if ylim is not None:
            ax.set_ylim(ylim[0], ylim[1])
        active_axes.append(ax)

    return fig, active_axes, baseline_info
