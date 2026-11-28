"""
chart_common.py
Shared Matplotlib chart helpers (CJK font setup, despine, spotlight styling, 1D decollision).
Note: `hcl_color_engine` is the public entry point.
"""

from typing import List, Optional, Sequence, Tuple

from chart_data import _parse_numeric_or_na
from color_core import GEPHI_SEQUENTIAL_SCALES

CJK_FONT_FALLBACKS: Tuple[str, ...] = (
    "Microsoft JhengHei",
    "PingFang TC",
    "Noto Sans CJK TC",
    "Source Han Sans TC",
    "Heiti TC",
    "WenQuanYi Micro Hei",
    "SimHei",
    "Arial Unicode MS",
    "sans-serif",
)

def despine_axes(
    ax: object,
    grid_axis: Optional[str] = "y",
    grid_color: str = "#CBD5E1",
    grid_linestyle: str = "--",
    grid_alpha: float = 0.65,
    spine_color: str = "#CBD5E1",
) -> None:
    """
    Apply publication-grade despined axis formatting to a Matplotlib Axes object:
    - Hides top and right spines.
    - Colors bottom and left spines with `spine_color`.
    - Enables subtle dashed reference grid on `grid_axis` ('x', 'y', 'both', or None).
    """
    if hasattr(ax, "spines"):
        if "top" in ax.spines:
            ax.spines["top"].set_visible(False)
        if "right" in ax.spines:
            ax.spines["right"].set_visible(False)
        for side in ("bottom", "left"):
            if side in ax.spines:
                ax.spines[side].set_color(spine_color)
                ax.spines[side].set_linewidth(1.0)
    if grid_axis in ("x", "y", "both") and hasattr(ax, "grid"):
        ax.grid(False)
        ax.grid(axis=grid_axis, linestyle=grid_linestyle, color=grid_color, alpha=grid_alpha, zorder=0)


def _ensure_cjk_font() -> None:
    """Ensure Matplotlib has CJK-capable sans-serif fonts registered and unicode_minus disabled."""
    try:
        import matplotlib.pyplot as plt
        current = list(plt.rcParams.get("font.sans-serif", []))
        cjk_candidates = list(CJK_FONT_FALLBACKS)
        missing = [c for c in cjk_candidates if c not in current]
        if missing:
            plt.rcParams["font.sans-serif"] = cjk_candidates + [c for c in current if c not in cjk_candidates]
        plt.rcParams["axes.unicode_minus"] = False
    except Exception:
        pass


def setup_chart_canvas(
    orientation: str = "vertical",
    dpi: int = 300,
    figsize: Optional[Tuple[float, float]] = None,
    wide_left: bool = False,
    slide_mode: bool = False,
    grid_axis: Optional[str] = None,
    facecolor: str = "#FFFFFF",
    **subplots_kwargs,
) -> Tuple[object, object]:
    """
    Create a standardized 300 DPI Matplotlib canvas following `formats/format_d_charts/02_build_core.md`:
    - orientation='vertical'   -> (12.0, 6.4) default; (9.6, 5.2) when slide_mode=True
    - orientation='horizontal' -> (12.8, 6.7) default; (10.0, 5.4) when slide_mode=True
    Applies CJK fonts, golden-ratio `subplots_adjust`, and `despine_axes()`.
    Returns `(fig, ax)`.
    """
    orient = str(orientation or "vertical").strip().lower()
    if orient not in ("vertical", "horizontal"):
        raise ValueError(f"Unsupported orientation '{orientation}'. Expected 'vertical' or 'horizontal'.")

    _ensure_cjk_font()
    import matplotlib.pyplot as plt

    if figsize is not None:
        resolved_figsize = (float(figsize[0]), float(figsize[1]))
    elif slide_mode:
        resolved_figsize = (10.0, 5.4) if orient == "horizontal" else (9.6, 5.2)
    else:
        resolved_figsize = (12.8, 6.7) if orient == "horizontal" else (12.0, 6.4)

    fig, ax = plt.subplots(figsize=resolved_figsize, dpi=int(dpi), facecolor=facecolor, **subplots_kwargs)
    ax.set_facecolor(facecolor)

    if slide_mode:
        left = 0.14 if (wide_left or orient == "horizontal") else 0.08
        fig.subplots_adjust(left=left, right=0.96, top=0.92, bottom=0.12)
    else:
        left = 0.165 if (wide_left or orient == "horizontal") else 0.082
        fig.subplots_adjust(left=left, right=0.965, top=0.808, bottom=0.188)

    resolved_grid = grid_axis if grid_axis is not None else ("x" if orient == "horizontal" else "y")
    despine_axes(ax, grid_axis=resolved_grid)
    return fig, ax


class _SpotlightStyleResult(dict):
    """
    Dictionary-compatible container returned by `apply_spotlight_colors`.
    Supports:
    - Dict key access: `res["colors"]`, `res["point_colors"]`, `res["text_colors"]`,
      `res["fontweights"]`, `res["sizes"]`, `res["is_highlight"]`, `res["highlight_indices"]`
    - Attribute access: `res.colors`, `res.text_colors`, `res.fontweights`, `res.sizes`
    - 3-tuple unpacking: `colors, text_colors, fontweights = apply_spotlight_colors(...)`
    """
    def __getattr__(self, name: str) -> object:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __iter__(self):
        return iter((self["colors"], self["text_colors"], self["fontweights"]))


def apply_spotlight_colors(
    values_or_labels: Sequence[object],
    top_n: int = 1,
    bottom_n: int = 1,
    highlight_indices: Optional[Sequence[int]] = None,
    highlight_color: Optional[str] = None,
    context_color: str = "#94A3B8",
    **kwargs,
) -> _SpotlightStyleResult:
    """
    Data 8 Editorial Spotlight vs. Context Hierarchy Styling.
    Highlights top_n, bottom_n, and/or explicit `highlight_indices` (or `highlight_labels` via kwargs)
    with deep accent color (`highlight_color`), bold `#0F172A` text, and enlarged dot sizes,
    while pushing remaining context items to muted slate (`context_color="#94A3B8"`) and `#475569` regular text.
    """
    items = list(values_or_labels) if values_or_labels is not None else []
    n = len(items)
    resolved_hl_color = (
        highlight_color
        if highlight_color is not None
        else GEPHI_SEQUENTIAL_SCALES.get("blue", ["#EBF7F9", "#BCE2EB", "#5DBACD", "#2C8B9F", "#0E5B6B"])[4]
    )
    hl_text_color = str(kwargs.get("highlight_text_color", "#0F172A"))
    ctx_text_color = str(kwargs.get("context_text_color", "#475569"))
    hl_weight = str(kwargs.get("highlight_fontweight", "bold"))
    ctx_weight = str(kwargs.get("context_fontweight", "normal"))
    hl_size = float(kwargs.get("highlight_size", 105.0))
    ctx_size = float(kwargs.get("context_size", 54.0))

    if n == 0:
        return _SpotlightStyleResult({
            "colors": [],
            "point_colors": [],
            "dot_colors": [],
            "text_colors": [],
            "label_colors": [],
            "fontweights": [],
            "weights": [],
            "sizes": [],
            "dot_sizes": [],
            "is_highlight": [],
            "highlight_indices": [],
        })

    hl_set = set()
    if highlight_indices is not None:
        for idx in highlight_indices:
            try:
                i_val = int(idx)
                if i_val < 0:
                    i_val = n + i_val
                if 0 <= i_val < n:
                    hl_set.add(i_val)
            except (TypeError, ValueError):
                continue

    highlight_labels = kwargs.get("highlight_labels")
    if highlight_labels:
        hl_label_strs = {str(lbl).strip() for lbl in highlight_labels}
        for i, item in enumerate(items):
            if str(item).strip() in hl_label_strs:
                hl_set.add(i)

    parsed_nums: List[Tuple[float, int]] = []
    for i, item in enumerate(items):
        v = _parse_numeric_or_na(item)
        if v is not None:
            parsed_nums.append((v, i))

    t_n = max(0, int(top_n))
    b_n = max(0, int(bottom_n))
    if t_n > 0 or b_n > 0:
        if len(parsed_nums) > 0:
            sorted_asc = sorted(parsed_nums, key=lambda pair: (pair[0], pair[1]))
            for _, i_low in sorted_asc[:b_n]:
                hl_set.add(i_low)
            for _, i_high in sorted_asc[max(0, len(sorted_asc) - t_n):]:
                hl_set.add(i_high)
        else:
            for i_top in range(min(n, t_n)):
                hl_set.add(i_top)
            for i_bot in range(max(0, n - b_n), n):
                hl_set.add(i_bot)

    is_hl = [i in hl_set for i in range(n)]
    colors = [resolved_hl_color if flag else context_color for flag in is_hl]
    text_colors = [hl_text_color if flag else ctx_text_color for flag in is_hl]
    fontweights = [hl_weight if flag else ctx_weight for flag in is_hl]
    sizes = [hl_size if flag else ctx_size for flag in is_hl]

    return _SpotlightStyleResult({
        "colors": colors,
        "point_colors": colors,
        "dot_colors": colors,
        "text_colors": text_colors,
        "label_colors": text_colors,
        "fontweights": fontweights,
        "weights": fontweights,
        "sizes": sizes,
        "dot_sizes": sizes,
        "is_highlight": is_hl,
        "highlight_indices": sorted(hl_set),
    })


def _decollide_1d_positions(positions: List[float], min_dist: float) -> List[float]:
    """Relax 1D vertical label coordinates so adjacent labels maintain at least `min_dist` separation."""
    if len(positions) <= 1 or min_dist <= 0:
        return list(positions)
    indexed = sorted(enumerate(positions), key=lambda pair: pair[1])
    adjusted = [p for _, p in indexed]
    for _ in range(12):
        moved = False
        for i in range(len(adjusted) - 1):
            gap = adjusted[i + 1] - adjusted[i]
            if gap < min_dist:
                push = 0.5 * (min_dist - gap)
                adjusted[i] -= push
                adjusted[i + 1] += push
                moved = True
        if not moved:
            break
    out = [0.0] * len(positions)
    for (orig_idx, _), adj_val in zip(indexed, adjusted):
        out[orig_idx] = adj_val
    return out
