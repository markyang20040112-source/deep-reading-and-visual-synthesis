"""
chart_editorial.py
Editorial narrative chart components (badge vlines, footers, regime shading, inset leaderboard).
Note: `hcl_color_engine` is the public entry point.
"""

from typing import Dict, List, Optional, Sequence, Tuple

from chart_common import _ensure_cjk_font
from chart_data import _parse_numeric_or_na
from color_core import (
    GEPHI_LIGHT_BADGE_TINTS,
    GEPHI_QUALITATIVE_HEX,
    GEPHI_SEQUENTIAL_SCALES,
)

class _BadgeVLineResult(tuple):
    """
    Native tuple `(line, badge_annotation)` returned by `add_badge_vline` with attribute and dict-key access.
    """
    def __new__(cls, line: object, badge: object):
        obj = super().__new__(cls, (line, badge))
        obj.line = line
        obj.badge = badge
        obj.annotation = badge
        return obj

    def __getitem__(self, key):
        if key == "line":
            return self.line
        if key in ("badge", "annotation"):
            return self.badge
        return super().__getitem__(key)


def _estimate_badge_width_pts(text: str, fontsize: float, pad_pts: float = 18.0) -> float:
    """Estimate horizontal width in points of a multi-line CJK/ASCII pill badge."""
    lines = str(text or "").splitlines() or [""]
    max_w = 0.0
    for ln in lines:
        w = 0.0
        for ch in ln:
            w += (1.04 * fontsize) if ord(ch) > 127 else (0.60 * fontsize)
        max_w = max(max_w, w)
    return max_w + pad_pts


def _rebalance_badge_vlines_on_ax(ax: object) -> None:
    """
    Automatic horizontal collision avoidance when multiple `add_badge_vline` calls are made on the same `ax`.
    Shifts colliding top pill badges horizontally in offset points while keeping their leader lines anchored
    to the exact `(x, 1.0)` top of each vertical reference line.
    When an renderer is available, measures real rendered bbox widths for exact multi-badge de-collision.
    """
    registry = getattr(ax, "_badge_vlines_registry", None)
    if not registry or len(registry) < 2:
        return
    try:
        fig = ax.figure
        fig_w_pts = float(fig.get_figwidth()) * 72.0
        fig_h_pts = float(fig.get_figheight()) * 72.0
        pos = ax.get_position()
        ax_w_pts = max(100.0, fig_w_pts * float(pos.width))
        ax_h_pts = max(80.0, fig_h_pts * float(pos.height))
        x_min, x_max = ax.get_xlim()
        x_span = float(x_max - x_min)
        if abs(x_span) < 1e-9:
            return
    except Exception:
        return

    # Sort items by data x position
    ordered = sorted(registry, key=lambda item: float(item["x"]))
    n = len(ordered)
    x_centers_pts = [((float(item["x"]) - float(x_min)) / x_span) * ax_w_pts for item in ordered]

    # Try to measure real rendered pill widths in points if a canvas renderer exists
    widths_pts = [float(item["width_pts"]) for item in ordered]
    try:
        dpi = float(fig.dpi) if hasattr(fig, "dpi") and float(fig.dpi) > 0 else 72.0
        renderer = fig.canvas.get_renderer() if hasattr(fig.canvas, "get_renderer") else None
        if renderer is not None:
            for idx, item in enumerate(ordered):
                patch = item["ann"].get_bbox_patch()
                if patch is not None:
                    ext = patch.get_window_extent(renderer=renderer)
                    if ext.width > 1.0:
                        widths_pts[idx] = max(widths_pts[idx], float(ext.width) * 72.0 / dpi)
    except Exception:
        pass

    offsets = [float(item["user_x_offset_pts"]) for item in ordered]
    locked = [bool(item["user_locked"]) for item in ordered]

    min_gap_pts = 8.0
    for _pass in range(28):
        changed = False
        for i in range(n - 1):
            c_left = x_centers_pts[i] + offsets[i]
            c_right = x_centers_pts[i + 1] + offsets[i + 1]
            req_dist = 0.5 * (widths_pts[i] + widths_pts[i + 1]) + min_gap_pts
            actual_dist = c_right - c_left
            if actual_dist < req_dist - 0.05:
                overlap = req_dist - actual_dist
                if not locked[i] and not locked[i + 1]:
                    offsets[i] -= 0.51 * overlap
                    offsets[i + 1] += 0.51 * overlap
                    changed = True
                elif not locked[i]:
                    offsets[i] -= overlap
                    changed = True
                elif not locked[i + 1]:
                    offsets[i + 1] += overlap
                    changed = True
        if not changed:
            break

    for item, eff_offset in zip(ordered, offsets):
        item["effective_x_offset_pts"] = eff_offset
        ann = item["ann"]
        lift_pts = max(6.0, (float(item["badge_y_axes"]) - 1.0) * ax_h_pts)
        ann.set_position((eff_offset, lift_pts))


def add_badge_vline(
    ax: object,
    x: float,
    badge_text: str,
    color: Optional[str] = None,
    linestyle: str = "--",
    linewidth: float = 2.0,
    badge_y_axes: float = 1.03,
    x_offset_pts: float = 0.0,
    zorder: int = 6,
    **kwargs,
) -> _BadgeVLineResult:
    """
    Data 8 Editorial Dual/Multi Benchmark Reference Line + Top Rounded Callout Pill Badge.
    - Draws a white-halo vertical reference dashed line at `x`.
    - Places a white-background, colored-border rounded pill badge at the top of the plot area (`badge_y_axes`).
    - Automatically avoids horizontal pill collisions when multiple `add_badge_vline` calls share the same `ax`.
    """
    _ensure_cjk_font()
    import matplotlib.patheffects as patheffects

    existing_count = len(getattr(ax, "_badge_vlines_registry", []))
    if color is not None:
        resolved_color = str(color)
    else:
        palette_choices = [
            GEPHI_SEQUENTIAL_SCALES.get("blue", ["#EBF7F9", "#BCE2EB", "#5DBACD", "#2C8B9F", "#0E5B6B"])[3],
            GEPHI_SEQUENTIAL_SCALES.get("orange", ["#FFF3EA", "#FBD8C0", "#ECA072", "#CA6F35", "#97481B"])[3],
            GEPHI_SEQUENTIAL_SCALES.get("pink", ["#FFF0F5", "#F9CEE0", "#E89BB6", "#C46487", "#8D3658"])[3],
            GEPHI_SEQUENTIAL_SCALES.get("green", ["#F1F7EE", "#D0E5CC", "#8FBA88", "#5E8F56", "#396032"])[3],
        ]
        resolved_color = palette_choices[existing_count % len(palette_choices)]

    halo_color = str(kwargs.pop("halo_color", "#FFFFFF"))
    halo_width = float(kwargs.pop("halo_width", linewidth + 2.2))
    fontsize = float(kwargs.pop("fontsize", 9.5))
    fontweight = str(kwargs.pop("fontweight", "bold"))
    badge_bg = str(kwargs.pop("badge_bg", "#FFFFFF"))
    badge_text_color = str(kwargs.pop("badge_text_color", resolved_color))
    badge_border_lw = float(kwargs.pop("badge_border_lw", 1.5))
    ymax_line = float(kwargs.pop("ymax", 1.005))
    ymin_line = float(kwargs.pop("ymin", 0.0))
    line_zorder = float(kwargs.pop("line_zorder", 3.0))

    line = ax.axvline(
        x=float(x),
        ymin=ymin_line,
        ymax=ymax_line,
        color=resolved_color,
        linestyle=linestyle,
        linewidth=linewidth,
        zorder=line_zorder,
        clip_on=False,
        **{k: v for k, v in kwargs.items() if k in ("alpha", "label")},
    )
    line.set_path_effects([
        patheffects.Stroke(linewidth=halo_width, foreground=halo_color),
        patheffects.Normal(),
    ])

    try:
        fig = ax.figure
        ax_h_pts = max(80.0, float(fig.get_figheight()) * 72.0 * float(ax.get_position().height))
    except Exception:
        ax_h_pts = 280.0
    lift_pts = max(6.0, (float(badge_y_axes) - 1.0) * ax_h_pts)

    bbox_props = dict(
        boxstyle="round,pad=0.38,rounding_size=0.45",
        facecolor=badge_bg,
        edgecolor=resolved_color,
        linewidth=badge_border_lw,
    )
    if "bbox" in kwargs and isinstance(kwargs["bbox"], dict):
        bbox_props.update(kwargs["bbox"])

    ann = ax.annotate(
        str(badge_text),
        xy=(float(x), 1.0),
        xycoords=("data", "axes fraction"),
        xytext=(float(x_offset_pts), lift_pts),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=fontsize,
        fontweight=fontweight,
        color=badge_text_color,
        bbox=bbox_props,
        arrowprops=dict(
            arrowstyle="-",
            color=resolved_color,
            lw=1.3,
            shrinkA=0,
            shrinkB=1,
        ),
        zorder=zorder + 1,
        annotation_clip=False,
    )

    if not hasattr(ax, "_badge_vlines_registry"):
        ax._badge_vlines_registry = []
        try:
            ax.callbacks.connect("xlim_changed", lambda target_ax: _rebalance_badge_vlines_on_ax(target_ax))
        except Exception:
            pass

    ax._badge_vlines_registry.append({
        "x": float(x),
        "badge_text": str(badge_text),
        "ann": ann,
        "line": line,
        "badge_y_axes": float(badge_y_axes),
        "user_x_offset_pts": float(x_offset_pts),
        "effective_x_offset_pts": float(x_offset_pts),
        "user_locked": abs(float(x_offset_pts)) > 1e-6,
        "width_pts": _estimate_badge_width_pts(str(badge_text), fontsize=fontsize),
    })
    _rebalance_badge_vlines_on_ax(ax)

    return _BadgeVLineResult(line, ann)


def add_editorial_footer(
    fig: object,
    footer_lines: object,
    y_top: float = 0.088,
    line_spacing: float = 0.022,
    rule_color: str = "#CBD5E1",
    fontsize: float = 9.0,
    **kwargs,
) -> List[object]:
    """
    Data 8 Editorial 4-Tier Structured Footer (`資料補充 / 註 / 來源 / 提醒`).
    - Draws a crisp horizontal top separator rule across the figure bottom margin.
    - Renders structured multi-line editorial notes with bold lead tags (`#0F172A`) and slate body text (`#475569`).
    - Accepts `footer_lines` as a `List[str]`, `Dict[str, str]`, `List[Tuple[str, str]]`, or multi-line `str`.
    """
    _ensure_cjk_font()
    from matplotlib.lines import Line2D

    x_left = float(kwargs.pop("x_left", 0.04))
    x_right = float(kwargs.pop("x_right", 0.96))
    text_color = str(kwargs.pop("text_color", "#475569"))
    prefix_color = str(kwargs.pop("prefix_color", "#0F172A"))
    rule_linewidth = float(kwargs.pop("rule_linewidth", 0.9))
    rule_offset = float(kwargs.pop("rule_offset", 0.012))
    auto_adjust_bottom = bool(kwargs.pop("auto_adjust_bottom", True))

    normalized_lines: List[Tuple[Optional[str], str]] = []
    if isinstance(footer_lines, dict):
        for k, v in footer_lines.items():
            normalized_lines.append((str(k).strip(), str(v).strip()))
    elif isinstance(footer_lines, str):
        for raw_ln in footer_lines.splitlines():
            s = raw_ln.strip()
            if s:
                normalized_lines.append((None, s))
    elif isinstance(footer_lines, (list, tuple)):
        for item in footer_lines:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                normalized_lines.append((str(item[0]).strip(), str(item[1]).strip()))
            elif item is not None:
                normalized_lines.append((None, str(item).strip()))

    # Parse `Prefix：Body` when prefix wasn't passed as a tuple/dict
    parsed_entries: List[Tuple[Optional[str], str]] = []
    for pfx, body in normalized_lines:
        if pfx is not None:
            clean_pfx = pfx.rstrip(":：")
            parsed_entries.append((f"{clean_pfx}：", body))
        else:
            split_done = False
            for sep in ("：", ":"):
                if sep in body:
                    head, tail = body.split(sep, 1)
                    if 1 <= len(head.strip()) <= 10:
                        parsed_entries.append((f"{head.strip()}：", tail.strip()))
                        split_done = True
                        break
            if not split_done:
                parsed_entries.append((None, body))

    if auto_adjust_bottom:
        try:
            needed_bottom = float(y_top) + 0.088
            if hasattr(fig, "subplotpars") and float(fig.subplotpars.bottom) < needed_bottom:
                fig.subplots_adjust(bottom=min(0.32, needed_bottom))
        except Exception:
            pass

    artists: List[object] = []
    rule_y = float(y_top) + rule_offset
    rule_line = Line2D(
        [x_left, x_right],
        [rule_y, rule_y],
        transform=fig.transFigure,
        color=rule_color,
        linewidth=rule_linewidth,
        zorder=10,
    )
    fig.add_artist(rule_line)
    artists.append(rule_line)

    renderer = None
    try:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
    except Exception:
        renderer = None

    for idx, (pfx, body) in enumerate(parsed_entries):
        y_curr = float(y_top) - idx * float(line_spacing)
        if pfx:
            t_pfx = fig.text(
                x_left,
                y_curr,
                pfx,
                fontsize=fontsize,
                fontweight="bold",
                color=prefix_color,
                ha="left",
                va="top",
                **kwargs,
            )
            artists.append(t_pfx)
            if renderer is not None:
                try:
                    bbox_fig = t_pfx.get_window_extent(renderer=renderer).transformed(fig.transFigure.inverted())
                    x_body = float(bbox_fig.x1) + 0.002
                except Exception:
                    x_body = x_left + len(pfx) * (fontsize * 0.00145)
            else:
                x_body = x_left + len(pfx) * (fontsize * 0.00145)
            t_body = fig.text(
                x_body,
                y_curr,
                body,
                fontsize=fontsize,
                fontweight="normal",
                color=text_color,
                ha="left",
                va="top",
                **kwargs,
            )
            artists.append(t_body)
        else:
            t_full = fig.text(
                x_left,
                y_curr,
                body,
                fontsize=fontsize,
                fontweight="normal",
                color=text_color,
                ha="left",
                va="top",
                **kwargs,
            )
            artists.append(t_full)

    return artists


def add_regime_shading_and_events(
    ax: object,
    regimes: Optional[Sequence[object]] = None,
    events: Optional[Sequence[object]] = None,
    **kwargs,
) -> Dict[str, List[object]]:
    """
    Data 7《臺灣數據百閱》Time-Series Regime Background Shading Bands & Historical/Policy Event Callout Boxes.
    - `regimes`: list of dicts `{"start": x0, "end": x1, "label": "...", "color": "#F1F5F9", "alpha": 0.55}`
      or tuples `(x0, x1, label[, color])`.
    - `events`: list of dicts `{"x": x_val, "y": y_val (optional), "label": "...", "color": "#CA6F35"}`
      or tuples `(x_val, label)` / `(x_val, y_val, label[, color])`.
    """
    _ensure_cjk_font()
    regime_patches: List[object] = []
    regime_texts: List[object] = []
    event_annotations: List[object] = []
    event_lines: List[object] = []

    default_band_Palette = [
        GEPHI_LIGHT_BADGE_TINTS[1] if len(GEPHI_LIGHT_BADGE_TINTS) > 1 else "#EBF7F9",
        "#F1F5F9",
        GEPHI_LIGHT_BADGE_TINTS[0] if len(GEPHI_LIGHT_BADGE_TINTS) > 0 else "#FFF3EA",
        GEPHI_LIGHT_BADGE_TINTS[3] if len(GEPHI_LIGHT_BADGE_TINTS) > 3 else "#F1F7EE",
    ]
    fontsize = float(kwargs.pop("fontsize", 9.0))

    if regimes:
        for idx, reg in enumerate(regimes):
            if isinstance(reg, dict):
                x0 = reg.get("start", reg.get("x0", reg.get("xmin", reg.get("from"))))
                x1 = reg.get("end", reg.get("x1", reg.get("xmax", reg.get("to"))))
                label = str(reg.get("label", reg.get("title", reg.get("name", ""))))
                color = str(reg.get("color", default_band_Palette[idx % len(default_band_Palette)]))
                alpha = float(reg.get("alpha", 0.55))
                text_color = str(reg.get("text_color", "#334155"))
                label_y = float(reg.get("label_y", 0.965))
            elif isinstance(reg, (list, tuple)) and len(reg) >= 2:
                x0, x1 = reg[0], reg[1]
                label = str(reg[2]) if len(reg) >= 3 else ""
                color = str(reg[3]) if len(reg) >= 4 else default_band_Palette[idx % len(default_band_Palette)]
                alpha = 0.55
                text_color = "#334155"
                label_y = 0.965
            else:
                continue

            if x0 is None or x1 is None:
                continue
            span_patch = ax.axvspan(float(x0), float(x1), color=color, alpha=alpha, zorder=0, lw=0)
            regime_patches.append(span_patch)
            if label:
                mid_x = 0.5 * (float(x0) + float(x1))
                t_obj = ax.text(
                    mid_x,
                    label_y,
                    label,
                    transform=ax.get_xaxis_transform(),
                    ha="center",
                    va="top",
                    fontsize=fontsize,
                    fontweight="bold",
                    color=text_color,
                    bbox=dict(boxstyle="round,pad=0.22", facecolor="#FFFFFF", edgecolor="none", alpha=0.78),
                    zorder=2,
                )
                regime_texts.append(t_obj)

    if events:
        default_ev_color = GEPHI_SEQUENTIAL_SCALES.get("orange", ["#FFF3EA", "#FBD8C0", "#ECA072", "#CA6F35", "#97481B"])[3]
        stagger_levels = [0.84, 0.70, 0.56, 0.77]
        for idx, ev in enumerate(events):
            y_val = None
            color = default_ev_color
            dx_pts = 0.0
            dy_pts = 26.0
            y_axes = stagger_levels[idx % len(stagger_levels)]
            draw_vline = True

            if isinstance(ev, dict):
                x_val = ev.get("x")
                y_val = ev.get("y")
                label = str(ev.get("label", ev.get("text", ev.get("title", ""))))
                color = str(ev.get("color", default_ev_color))
                dx_pts = float(ev.get("dx_pts", ev.get("x_offset_pts", 0.0)))
                dy_pts = float(ev.get("dy_pts", ev.get("y_offset_pts", 26.0)))
                if "y_axes" in ev:
                    y_axes = float(ev["y_axes"])
                draw_vline = bool(ev.get("vline", y_val is None))
            elif isinstance(ev, (list, tuple)):
                if len(ev) == 2:
                    x_val, label = ev[0], str(ev[1])
                elif len(ev) >= 3:
                    if isinstance(ev[1], (int, float)) and not isinstance(ev[1], bool):
                        x_val, y_val, label = ev[0], float(ev[1]), str(ev[2])
                        draw_vline = False
                        if len(ev) >= 4:
                            color = str(ev[3])
                    else:
                        x_val, label, color = ev[0], str(ev[1]), str(ev[2])
                else:
                    continue
            else:
                continue

            if x_val is None:
                continue

            if draw_vline:
                vl = ax.axvline(float(x_val), color=color, linestyle=":", linewidth=1.4, alpha=0.85, zorder=3)
                event_lines.append(vl)

            bbox_ev = dict(
                boxstyle="round,pad=0.35,rounding_size=0.35",
                facecolor="#FFFFFF",
                edgecolor=color,
                linewidth=1.3,
            )
            if y_val is not None:
                ax.scatter(
                    [float(x_val)],
                    [float(y_val)],
                    s=58,
                    color=color,
                    edgecolors="#FFFFFF",
                    linewidths=1.5,
                    zorder=5,
                )
                ann = ax.annotate(
                    label,
                    xy=(float(x_val), float(y_val)),
                    xycoords="data",
                    xytext=(dx_pts, dy_pts),
                    textcoords="offset points",
                    ha="center",
                    va="bottom" if dy_pts >= 0 else "top",
                    fontsize=fontsize,
                    fontweight="bold",
                    color="#0F172A",
                    bbox=bbox_ev,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.3, shrinkA=2, shrinkB=4),
                    zorder=6,
                )
            else:
                ann = ax.annotate(
                    label,
                    xy=(float(x_val), y_axes),
                    xycoords=("data", "axes fraction"),
                    xytext=(dx_pts, 0.0),
                    textcoords="offset points",
                    ha="center",
                    va="center",
                    fontsize=fontsize,
                    fontweight="bold",
                    color="#0F172A",
                    bbox=bbox_ev,
                    zorder=6,
                )
            event_annotations.append(ann)

    return {
        "regime_patches": regime_patches,
        "regime_texts": regime_texts,
        "event_lines": event_lines,
        "event_annotations": event_annotations,
    }


def add_inset_leaderboard(
    ax: object,
    labels: Sequence[str],
    values: Sequence[float],
    bbox: Tuple[float, float, float, float] = (0.62, 0.08, 0.34, 0.32),
    title: str = "",
    color: Optional[str] = None,
    **kwargs,
) -> object:
    """
    Data 7 Bubble Tea Density Map Mode: Rounded white-card Inset Leaderboard in a corner of the main chart.
    Returns the created `inset_ax` Matplotlib Axes object.
    """
    _ensure_cjk_font()
    import numpy as np

    bg_color = str(kwargs.pop("bg_color", "#FFFFFF"))
    border_color = str(kwargs.pop("border_color", "#CBD5E1"))
    value_fmt = str(kwargs.pop("value_fmt", "{:.1f}"))
    max_items = int(kwargs.pop("max_items", 5))
    fontsize = float(kwargs.pop("fontsize", 8.5))
    sort_desc = bool(kwargs.pop("sort_desc", False))
    zorder = int(kwargs.pop("zorder", 8))

    resolved_color = color if color is not None else GEPHI_QUALITATIVE_HEX[0]
    top_color = GEPHI_SEQUENTIAL_SCALES.get("orange", ["#FFF3EA", "#FBD8C0", "#ECA072", "#CA6F35", "#97481B"])[3]

    pairs = [(str(lbl), float(val)) for lbl, val in zip(labels, values) if _parse_numeric_or_na(val) is not None]
    if sort_desc:
        pairs.sort(key=lambda item: item[1], reverse=True)
    pairs = pairs[:max(1, max_items)]

    inset_ax = ax.inset_axes(list(bbox), zorder=zorder)
    inset_ax.set_facecolor(bg_color)
    for side in ("top", "right", "bottom", "left"):
        if side in inset_ax.spines:
            inset_ax.spines[side].set_visible(True)
            inset_ax.spines[side].set_color(border_color)
            inset_ax.spines[side].set_linewidth(1.2)

    if not pairs:
        inset_ax.set_xticks([])
        inset_ax.set_yticks([])
        return inset_ax

    # Reverse so rank #1 is at top of horizontal bar chart
    display_pairs = list(reversed(pairs))
    y_pos = np.arange(len(display_pairs))
    disp_labels = [p[0] for p in display_pairs]
    disp_vals = [p[1] for p in display_pairs]
    v_max = max(max(disp_vals), 1e-6)

    bar_colors = [
        (top_color if color is None else resolved_color) if idx == len(display_pairs) - 1 else resolved_color
        for idx in range(len(display_pairs))
    ]
    inset_ax.barh(y_pos, [v_max * 1.05] * len(display_pairs), height=0.58, color="#F1F5F9", edgecolor="none", zorder=1)
    inset_ax.barh(y_pos, disp_vals, height=0.58, color=bar_colors, edgecolor="none", zorder=2)

    inset_ax.set_yticks(y_pos)
    inset_ax.set_yticklabels(disp_labels, fontsize=fontsize, fontweight="bold", color="#1E293B")
    inset_ax.tick_params(axis="y", length=0, pad=4)
    inset_ax.set_xticks([])
    inset_ax.set_xlim(0, v_max * 1.34)
    inset_ax.set_ylim(-0.65, len(display_pairs) - 0.30)

    for y_i, val in zip(y_pos, disp_vals):
        inset_ax.text(
            val + v_max * 0.04,
            y_i,
            value_fmt.format(val),
            va="center",
            ha="left",
            fontsize=fontsize,
            fontweight="bold",
            color="#0F172A",
            zorder=3,
        )

    if title:
        inset_ax.set_title(
            title,
            fontsize=fontsize + 0.8,
            fontweight="bold",
            color="#0F172A",
            loc="left",
            pad=5,
        )

    return inset_ax
