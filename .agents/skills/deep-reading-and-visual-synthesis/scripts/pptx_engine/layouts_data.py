"""
pptx_engine/layouts_data.py
Evidence, comparison & geometry layouts: F4-A/B, F5-A/B/C, and Mode 3 Tier 1 geometric accents.
Note: `pptx_slide_engine` is the public entry point.
"""

import math
from collections.abc import Sequence
from contextlib import suppress
from pathlib import Path

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from .tokens import (
    _add_flat_shape,
    _blend_hex,
    _populate_paragraph_runs,
    _read_image_pixel_size,
    _resolve_engine_context,
    _round_half_pt,
    _theme_palette,
    hex_to_rgb_color,
)
from .text_layout import MSJH_LINE_HEIGHT_EM, calc_pill_width, measure_text_layout
from .media_omml import _OMML_A_NS, _clean_omml_hex, insert_omml_equation
from .primitives import (
    _apply_zone2_optical_vertical_balance,
    _calc_zone2_expansion_factor,
    _coerce_items_list,
    _estimate_horizontal_band_height,
    _estimate_vertical_callouts_height,
    _extract_lead_body_items,
    _first_non_empty_str,
    _measure_lead_body_item_height,
    _measure_three_tier_header,
    _normalize_callout_items,
    _parse_lead_body_item,
    _render_compact_lead_body_stack,
    _render_lead_body_box,
    _render_three_tier_header,
    _render_unboxed_callouts_horizontal,
    _render_unboxed_callouts_vertical,
    _resolve_zone2_avail_bottom,
    _resolve_zone2_height,
    _shift_coords_y,
)

def draw_visual_callout_slide(
    slide,
    image_path: str | None = None,
    callout_position: str = "right",
    callouts: Sequence[object] | None = None,
    visual_ratio: float = 0.65,
    visual_caption: str | None = None,
    callout_heading: str | None = None,
    body_font_pt: float = 13.0,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    spotlight_idx: int | None = 0,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
    *,
    _callout_gap_scale: float | None = None,
) -> tuple[float, float, float, float]:
    """
    [F5-A / S7] Render Primary Visual Slide obeying the Unboxed Callout Iron Law (`圖旁不疊卡`):
    Supports 5 flexible unboxed layouts via `callout_position`:
      1. "right" (S7-A): Left maximized visual + Right unboxed TOP-aligned callouts (`1.30x / 1.15x / 1.0x`).
      2. "left"  (S7-A alt): Left unboxed callouts + Right maximized visual.
      3. "bottom"(S7-B): Top maximized visual + Bottom horizontal unboxed callouts.
      4. "top"   (S7-C): Top horizontal unboxed callout band + Bottom maximized visual.
      5. "header_only" (S7-D, or when `callouts` is empty): Full-width maximized visual.
    Anchors `visual_caption` cleanly to the bottom edge of Zone 2 (left-aligned, `>= min_font_pt`).
    Returns `visual_rect = (vx, vy, vw, vh)` in inches.
    """
    pos = str(callout_position or "right").strip().lower()
    valid_positions = {"right", "left", "top", "bottom", "header_only"}
    if pos not in valid_positions:
        raise ValueError(f"Unsupported callout_position '{callout_position}'. Expected one of {sorted(valid_positions)}.")

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.66)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, min_floor, resolved_pt, typo, _sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.0, caller_default_pt=13.0
    )
    items = _normalize_callout_items(callouts)
    if not items:
        pos = "header_only"

    gap = 0.36
    ratio = max(0.45, min(0.82, float(visual_ratio)))
    band_gap = 0.18
    if image_path is not None and pos in ("bottom", "top"):
        vis_exp = _calc_zone2_expansion_factor(avail_h, resolved_h)
        if vis_exp > 1.0:
            band_gap = round(0.18 * vis_exp, 3)

    if pos == "header_only":
        vx, vy, vw, vh = left, top, total_width, resolved_h
    elif pos == "right":
        vw = (total_width - gap) * ratio
        cw = total_width - gap - vw
        vx, vy, vh = left, top, resolved_h
        c_scale = _callout_gap_scale
        if c_scale is None:
            est_c_h = _estimate_vertical_callouts_height(items, cw, callout_heading, resolved_pt, gap_scale=1.0)
            c_scale = _calc_zone2_expansion_factor(avail_h, est_c_h)
        callout_budget_h = max(resolved_h, avail_h) if c_scale > 1.0 else resolved_h
        _render_unboxed_callouts_vertical(
            slide, items, left + vw + gap, top, cw, callout_budget_h, callout_heading, resolved_pt, spotlight_idx, dt,
            gap_scale=c_scale,
        )
    elif pos == "left":
        vw = (total_width - gap) * ratio
        cw = total_width - gap - vw
        vx, vy, vh = left + cw + gap, top, resolved_h
        c_scale = _callout_gap_scale
        if c_scale is None:
            est_c_h = _estimate_vertical_callouts_height(items, cw, callout_heading, resolved_pt, gap_scale=1.0)
            c_scale = _calc_zone2_expansion_factor(avail_h, est_c_h)
        callout_budget_h = max(resolved_h, avail_h) if c_scale > 1.0 else resolved_h
        _render_unboxed_callouts_vertical(
            slide, items, left, top, cw, callout_budget_h, callout_heading, resolved_pt, spotlight_idx, dt,
            gap_scale=c_scale,
        )
    elif pos == "bottom":
        band_h = min(resolved_h * 0.44, _estimate_horizontal_band_height(items, total_width, resolved_pt))
        vh = max(1.2, resolved_h - band_h - band_gap)
        vx, vy, vw = left, top, total_width
        _render_unboxed_callouts_horizontal(
            slide, items, left, top + vh + band_gap, total_width, band_h, resolved_pt, spotlight_idx, dt
        )
    else:  # pos == "top"
        band_h = min(resolved_h * 0.44, _estimate_horizontal_band_height(items, total_width, resolved_pt))
        vx, vy, vw = left, top + band_h + band_gap, total_width
        vh = max(1.2, resolved_h - band_h - band_gap)
        _render_unboxed_callouts_horizontal(
            slide, items, left, top, total_width, band_h, resolved_pt, spotlight_idx, dt
        )

    if image_path is not None:
        img_file = Path(image_path).resolve()
        if not img_file.exists():
            raise FileNotFoundError(f"Slide visual image not found: {img_file}")

        cap_str = str(visual_caption or "").strip()
        cap_pt = max(min_floor, float(typo["caption"]))
        px_w, px_h = _read_image_pixel_size(img_file)
        img_ar = float(px_w) / max(1.0, float(px_h))

        def _fit_image(avail_h: float) -> tuple[float, float, float, float]:
            box_ar = vw / avail_h
            if img_ar >= box_ar:
                pw = vw
                ph = vw / img_ar
            else:
                ph = avail_h
                pw = avail_h * img_ar
            px = vx + (vw - pw) / 2.0
            py = vy + (avail_h - ph) / 2.0
            return px, py, pw, ph

        actual_side_callout_h = 0.0
        if pos in ("right", "left") and len(slide.shapes) > start_shape_idx:
            c_shapes = list(slide.shapes)[start_shape_idx:]
            c_max_b = max((float(s.top or 0) + float(s.height or 0)) / 914400.0 for s in c_shapes)
            actual_side_callout_h = max(0.0, round(c_max_b - float(top), 3))

        if cap_str:
            m_cap = measure_text_layout(cap_str, max(2.2, vw - 0.04), cap_pt, bold=False, line_spacing=1.22)
            cap_h = round(max(0.28, float(m_cap["safe_height_in"]) + 0.04), 3)
        else:
            cap_h = 0.0
        cap_block_h = (cap_h + 0.12) if cap_str else 0.0
        avail_img_h = max(0.80, vh - cap_block_h)
        pic_x, pic_y, pic_w, pic_h = _fit_image(avail_img_h)

        cap_x = vx
        cap_w = vw
        if cap_str and pos in ("bottom", "top", "header_only") and pic_x > vx + 0.40:
            cap_x = pic_x
            cap_w = min(vx + vw - cap_x, max(pic_w, min(vw, 5.50)))
            m_cap_narrow = measure_text_layout(cap_str, max(2.2, cap_w - 0.04), cap_pt, bold=False, line_spacing=1.22)
            new_cap_h = round(max(0.28, float(m_cap_narrow["safe_height_in"]) + 0.04), 3)
            if new_cap_h > cap_h:
                cap_h = new_cap_h
                cap_block_h = cap_h + 0.12
                avail_img_h = max(0.80, vh - cap_block_h)
                pic_x, pic_y, pic_w, pic_h = _fit_image(avail_img_h)
                cap_x = pic_x if pic_x > vx + 0.40 else vx
                cap_w = min(vx + vw - cap_x, max(pic_w, min(vw, 5.50))) if cap_x > vx else vw

        # Cohesive vertical rhythm before whole-group optical centering:
        # - In side-by-side (`right`/`left`), align picture with the side callout band rather than pre-centering
        #   in empty full `vh`, preventing wide/short charts from detaching below short side callouts.
        # - In `header_only`, anchor at `vy` so Stage 2 optical centering places it at exact 40%/60% (<= 0.90").
        resolved_cap_y = round(vy + vh - cap_h, 3)
        if pos in ("right", "left") and actual_side_callout_h > 0.0:
            band_h = min(vh, max(pic_h + cap_block_h, actual_side_callout_h))
            pic_slot_h = max(pic_h, band_h - cap_block_h)
            pic_y = vy + max(0.0, (pic_slot_h - pic_h) / 2.0)
            if cap_str:
                resolved_cap_y = round(vy + band_h - cap_h, 3)
        elif pos == "header_only":
            pic_y = vy
            if cap_str:
                resolved_cap_y = round(pic_y + pic_h + 0.12, 3)

        slide.shapes.add_picture(
            str(img_file),
            Inches(pic_x),
            Inches(pic_y),
            width=Inches(pic_w),
            height=Inches(pic_h),
        )

        if cap_str:
            # Anchor caption flush with bottom edge of Zone 2 visual area (left-aligned to chart in wide horizontal modes)
            cap_y = resolved_cap_y
            cap_tb = slide.shapes.add_textbox(
                Inches(cap_x), Inches(cap_y), Inches(cap_w), Inches(cap_h)
            )
            tf_cap = cap_tb.text_frame
            tf_cap.word_wrap = True
            tf_cap.margin_left = Inches(0.02)
            tf_cap.margin_right = Inches(0.02)
            tf_cap.margin_top = Inches(0.01)
            tf_cap.margin_bottom = Inches(0.01)
            tf_cap.vertical_anchor = MSO_ANCHOR.TOP
            p_cap = tf_cap.paragraphs[0]
            p_cap.alignment = PP_ALIGN.LEFT
            p_cap.line_spacing = 1.22
            _populate_paragraph_runs(
                p_cap,
                cap_str,
                cap_pt,
                dt.get("ink_muted", "#64748B"),
                bold=False,
                bold_color_hex=dt.get("ink_primary", "#0F172A"),
            )

    vis_rect = (round(vx, 3), round(vy, 3), round(vw, 3), round(vh, 3))
    if image_path is not None:
        dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
        return _shift_coords_y(vis_rect, dy_in)
    return vis_rect


def draw_quadrant_matrix_s5(
    slide,
    quadrants_spec: Sequence[dict[str, object]],
    x_axis_label: str = "",
    y_axis_label: str = "",
    spotlight_idx: int | None = 1,
    borderless: bool = True,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    body_font_pt: float = 12.5,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> list[tuple[float, float, float, float]]:
    """
    [F4-A / S5] Render 2x2 Orthogonal Strategy Quadrant Matrix (Module 1 & 2 Upgraded):
    - `borderless=True` (default): crisp orthogonal crosshair axes, 3 unboxed quadrants, soft tint wash on spotlight quadrant only.
    - `borderless=False`: optional single-layer light cards.
    - Strict `MSO_ANCHOR.TOP` natural flow Lead/Body stacking inside every quadrant, `>= min_font_pt` axis labels.
    `quadrants_spec` order: [Top-Left (Q2), Top-Right (Q1), Bottom-Left (Q3), Bottom-Right (Q4)].
    """
    if not quadrants_spec:
        return []

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.82)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    q_exp = _calc_zone2_expansion_factor(avail_h, resolved_h)
    dt, min_floor, resolved_pt, typo, sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=12.5, caller_default_pt=12.5
    )
    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_pri = pal["primary_accent"]
    theme_border = pal["border_card"]
    theme_card_bg = pal["bg_card"]
    theme_canvas = pal["bg_canvas"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    ink_muted = pal["ink_muted"]
    arrow_muted = pal["arrow_muted"]
    muted_acc = pal["muted_accent"]
    ls = float(sp.get("line_spacing", 1.28))

    axis_pt = max(min_floor, float(typo["caption"]))
    q_title_pt = _round_half_pt(resolved_pt + 2.0)
    kicker_pt = float(typo["kicker"])
    sub_pt = float(typo["subtitle"])
    lead_pt = float(typo["lead"])

    axis_top_reserve = max(0.36, round((axis_pt * 1.45) / 72.0 + 0.10, 3)) if y_axis_label else 0.0
    axis_bot_reserve = max(0.36, round((axis_pt * 1.45) / 72.0 + 0.10, 3)) if x_axis_label else 0.0
    grid_top = round(top + axis_top_reserve, 3)
    grid_h = max(2.2, round(resolved_h - axis_top_reserve - axis_bot_reserve, 3))
    cross_gap = round(0.30 * q_exp, 3) if q_exp > 1.0 else 0.30
    qw = (total_width - cross_gap) / 2.0
    qh = (grid_h - cross_gap) / 2.0

    # Orthogonal crosshair lines with subtle directional end arrows
    cx_mid = left + qw + cross_gap / 2.0
    cy_mid = grid_top + qh + cross_gap / 2.0

    v_line = _add_flat_shape(slide, MSO_SHAPE.RECTANGLE, Inches(cx_mid - 0.012), Inches(grid_top + 0.10), Inches(0.024), Inches(max(0.5, grid_h - 0.10)))
    v_line.fill.solid()
    v_line.fill.fore_color.rgb = hex_to_rgb_color(arrow_muted)
    v_line.line.fill.background()

    v_tip = _add_flat_shape(slide, MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(cx_mid - 0.07), Inches(grid_top), Inches(0.14), Inches(0.14))
    v_tip.fill.solid()
    v_tip.fill.fore_color.rgb = hex_to_rgb_color(muted_acc)
    v_tip.line.fill.background()

    h_line = _add_flat_shape(slide, MSO_SHAPE.RECTANGLE, Inches(left), Inches(cy_mid - 0.012), Inches(max(0.5, total_width - 0.10)), Inches(0.024))
    h_line.fill.solid()
    h_line.fill.fore_color.rgb = hex_to_rgb_color(arrow_muted)
    h_line.line.fill.background()

    h_tip = _add_flat_shape(slide, MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(left + total_width - 0.14), Inches(cy_mid - 0.07), Inches(0.14), Inches(0.14))
    h_tip.rotation = 90.0
    h_tip.fill.solid()
    h_tip.fill.fore_color.rgb = hex_to_rgb_color(muted_acc)
    h_tip.line.fill.background()

    if y_axis_label and str(y_axis_label).strip():
        y_str = f"▲ {str(y_axis_label).strip()}"
        yb_w = min(total_width, max(5.6, calc_pill_width(y_str, font_pt=axis_pt, pad_in=0.30)))
        yb_x = max(left, min(left + total_width - yb_w, cx_mid - yb_w / 2.0))
        yb = slide.shapes.add_textbox(Inches(yb_x), Inches(top), Inches(yb_w), Inches(axis_top_reserve - 0.02))
        tf_y = yb.text_frame
        tf_y.word_wrap = True
        tf_y.vertical_anchor = MSO_ANCHOR.MIDDLE
        py = tf_y.paragraphs[0]
        py.alignment = PP_ALIGN.CENTER
        _populate_paragraph_runs(py, y_str, axis_pt, ink_muted, bold=True)

    if x_axis_label and str(x_axis_label).strip():
        x_str = f"{str(x_axis_label).strip()} ▶"
        xb_w = min(total_width, max(5.6, calc_pill_width(x_str, font_pt=axis_pt, pad_in=0.30)))
        xb = slide.shapes.add_textbox(
            Inches(left + total_width - xb_w), Inches(grid_top + grid_h + 0.04), Inches(xb_w), Inches(axis_bot_reserve - 0.04)
        )
        tf_x = xb.text_frame
        tf_x.word_wrap = True
        tf_x.vertical_anchor = MSO_ANCHOR.MIDDLE
        px = tf_x.paragraphs[0]
        px.alignment = PP_ALIGN.RIGHT
        _populate_paragraph_runs(px, x_str, axis_pt, ink_muted, bold=True)

    positions = [
        (left, grid_top),
        (left + qw + cross_gap, grid_top),
        (left, grid_top + qh + cross_gap),
        (left + qw + cross_gap, grid_top + qh + cross_gap),
    ]

    coords: list[tuple[float, float, float, float]] = []
    for idx in range(min(4, len(quadrants_spec))):
        q = quadrants_spec[idx]
        qx, qy = positions[idx]
        is_spot = (spotlight_idx == idx) if spotlight_idx is not None else bool(q.get("is_spotlight", False))
        acc_hex = str(q.get("accent", theme_pri if is_spot else muted_acc))

        if borderless:
            if is_spot:
                wash = _add_flat_shape(
                    slide,
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    Inches(qx), Inches(qy), Inches(qw), Inches(qh),
                )
                wash.adjustments[0] = 0.035
                wash.fill.solid()
                wash.fill.fore_color.rgb = hex_to_rgb_color(str(q.get("bg", _blend_hex(acc_hex, theme_canvas, 0.14 if is_dark_theme else 0.085))))
                wash.line.fill.background()

                bar = _add_flat_shape(
                    slide,
                    MSO_SHAPE.RECTANGLE,
                    Inches(qx), Inches(qy + 0.08), Inches(0.06), Inches(max(0.50, qh - 0.16)),
                )
                bar.fill.solid()
                bar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex)
                bar.line.fill.background()
        else:
            qbox = _add_flat_shape(
                slide,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(qx), Inches(qy), Inches(qw), Inches(qh),
            )
            qbox.adjustments[0] = 0.035
            qbox.fill.solid()
            qbox.fill.fore_color.rgb = hex_to_rgb_color(str(q.get("bg", _blend_hex(acc_hex, theme_card_bg, 0.14 if is_dark_theme else 0.07) if is_spot else theme_card_bg)))
            qbox.line.color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_border, 0.45 if is_dark_theme else 0.35) if is_spot else theme_border)
            qbox.line.width = Pt(1.3 if is_spot else 1.0)
            if is_spot:
                tbar = _add_flat_shape(
                    slide,
                    MSO_SHAPE.RECTANGLE,
                    Inches(qx + 0.14), Inches(qy + 0.01), Inches(max(0.4, qw - 0.28)), Inches(0.055),
                )
                tbar.fill.solid()
                tbar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex)
                tbar.line.fill.background()

        pad_l = 0.18 if (is_spot or not borderless) else 0.08
        inner_w = max(0.70, qw - pad_l - 0.14)
        cur_y = round(qy + 0.10, 3)

        q_kicker = _first_non_empty_str(q, "kicker", "badge", "num", "step")
        q_title = _first_non_empty_str(q, "title", "heading", "label", "name")
        q_sub = _first_non_empty_str(q, "subtitle", "sub")
        q_lead = _first_non_empty_str(q, "lead")
        if q_lead == q_title:
            q_lead = ""
        raw_pairs = _extract_lead_body_items(q, extra_lead=q_lead)
        parsed_pts: list[tuple[str, str, float]] = []
        for ld, bd in raw_pairs:
            parsed_pts.append((ld, bd, _measure_lead_body_item_height(ld, bd, inner_w, lead_pt, resolved_pt, line_spacing=ls)))

        est_pts_h = sum(p[2] for p in parsed_pts) + 0.05 * max(0, len(parsed_pts) - 1) if parsed_pts else 0.0
        if q_kicker or q_sub:
            qt_h = _measure_three_tier_header(q_kicker, q_title, q_sub, inner_w, kicker_pt, q_title_pt, sub_pt)
            if q_kicker and q_title and q_sub and parsed_pts and (cur_y + qt_h + 0.06 + est_pts_h) > (qy + qh - 0.06):
                q_kicker = f"{q_kicker} · {q_sub}"
                q_sub = ""
                qt_h = _measure_three_tier_header(q_kicker, q_title, q_sub, inner_w, kicker_pt, q_title_pt, sub_pt)
            hdr_box_h = round(min(qh * 0.54, qt_h + 0.02), 3)
            _render_three_tier_header(
                slide, qx + pad_l, cur_y, inner_w, hdr_box_h,
                q_kicker, q_title, q_sub, kicker_pt, q_title_pt, sub_pt,
                acc_hex if is_spot else ink_muted, acc_hex if is_spot else ink_pri, ink_muted,
            )
            cur_y = round(cur_y + hdr_box_h + 0.04, 3)
        elif q_title:
            m_qt = measure_text_layout(q_title, inner_w, q_title_pt, bold=True, line_spacing=1.18)
            qt_h = round(max(0.30, float(m_qt["safe_height_in"])), 3)
            qt_tb = slide.shapes.add_textbox(Inches(qx + pad_l), Inches(cur_y), Inches(inner_w), Inches(qt_h))
            tf_qt = qt_tb.text_frame
            tf_qt.word_wrap = True
            tf_qt.vertical_anchor = MSO_ANCHOR.TOP
            tf_qt.margin_left = Inches(0.02)
            tf_qt.margin_top = Inches(0.01)
            p_qt = tf_qt.paragraphs[0]
            p_qt.alignment = PP_ALIGN.LEFT
            p_qt.line_spacing = 1.18
            _populate_paragraph_runs(p_qt, q_title, q_title_pt, acc_hex if is_spot else ink_pri, bold=True)
            cur_y = round(cur_y + qt_h + 0.06, 3)

        if parsed_pts:
            avail_q = max(0.34, (qy + qh - 0.06) - cur_y)
            raw_sum = sum(p[2] for p in parsed_pts)
            min_q_gap = 0.05 * max(0, len(parsed_pts) - 1)
            if len(parsed_pts) > 1 and (raw_sum + min_q_gap) > avail_q:
                _render_compact_lead_body_stack(
                    slide,
                    x=qx + pad_l,
                    y=cur_y,
                    w=inner_w,
                    h=avail_q,
                    items=[(ld, bd) for ld, bd, _ih in parsed_pts],
                    lead_pt=lead_pt,
                    body_pt=resolved_pt,
                    lead_hex=ink_pri,
                    body_hex=ink_body,
                    bold_color_hex=ink_pri,
                    line_spacing=min(ls, 1.15),
                    para_space_after_pt=2.0,
                )
            else:
                q_gap_cap = round(0.14 * q_exp, 3) if q_exp > 1.0 else 0.14
                q_gap = min(q_gap_cap, max(0.05, (avail_q - raw_sum) / max(1, len(parsed_pts) - 1))) if len(parsed_pts) > 1 else 0.0
                for ld, bd, ih in parsed_pts:
                    rem = max(0.26, (qy + qh - 0.06) - cur_y)
                    bh = round(min(rem, ih + 0.02), 3)
                    _render_lead_body_box(
                        slide, qx + pad_l, cur_y, inner_w, bh,
                        ld, bd, lead_pt, resolved_pt, ink_pri, ink_body, ink_pri, line_spacing=ls,
                    )
                    cur_y = round(cur_y + bh + q_gap, 3)

        coords.append((round(qx, 3), round(qy, 3), round(qw, 3), round(qh, 3)))

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y(coords, dy_in)


def _set_table_cell_ooxml_style(
    cell,
    fill_hex: str | None = None,
    top_border: tuple[float, str] | None = None,
    bottom_border: tuple[float, str] | None = None,
    margin_l_in: float = 0.12,
    margin_r_in: float = 0.12,
    margin_t_in: float = 0.08,
    margin_b_in: float = 0.08,
    anchor=MSO_ANCHOR.TOP,
) -> None:
    """
    Style a native PowerPoint table cell cleanly as an academic Three-Line Table (`極簡三線表`):
    - Removes all vertical gridlines (`lnL` / `lnR` = `<a:noFill/>`).
    - Sets explicit OOXML `<a:lnT>` / `<a:lnB>` and `<a:solidFill>` in strict ECMA-376 `<a:tcPr>` element order.
    """
    from lxml import etree  # type: ignore

    a_ns = _OMML_A_NS
    cell.margin_left = Inches(margin_l_in)
    cell.margin_right = Inches(margin_r_in)
    cell.margin_top = Inches(margin_t_in)
    cell.margin_bottom = Inches(margin_b_in)
    cell.vertical_anchor = anchor

    tc_pr = cell._tc.get_or_add_tcPr()
    for tag in ("lnL", "lnR", "lnT", "lnB", "solidFill", "noFill"):
        for old in list(tc_pr.findall(f"{{{a_ns}}}{tag}")):
            tc_pr.remove(old)

    def _make_ln(tag_name: str, spec: tuple[float, str] | None):
        ln = etree.Element(f"{{{a_ns}}}{tag_name}")
        if spec is None:
            ln.set("w", "0")
            etree.SubElement(ln, f"{{{a_ns}}}noFill")
        else:
            pt_w, hex_c = spec
            ln.set("w", str(int(round(float(pt_w) * 12700))))
            ln.set("cap", "flat")
            ln.set("cmpd", "sng")
            sf = etree.SubElement(ln, f"{{{a_ns}}}solidFill")
            sc = etree.SubElement(sf, f"{{{a_ns}}}srgbClr")
            sc.set("val", _clean_omml_hex(hex_c) or "0F172A")
        return ln

    # Strict ECMA-376 CT_TableCellProperties child order: lnL, lnR, lnT, lnB, ..., fill
    insert_els = [
        _make_ln("lnL", None),
        _make_ln("lnR", None),
        _make_ln("lnT", top_border),
        _make_ln("lnB", bottom_border),
    ]
    for idx_i, el in enumerate(insert_els):
        tc_pr.insert(idx_i, el)

    if fill_hex:
        sf = etree.Element(f"{{{a_ns}}}solidFill")
        sc = etree.SubElement(sf, f"{{{a_ns}}}srgbClr")
        sc.set("val", _clean_omml_hex(fill_hex) or "FFFFFF")
        tc_pr.insert(4, sf)
    else:
        tc_pr.insert(4, etree.Element(f"{{{a_ns}}}noFill"))


def draw_comparison_table_slide(
    slide,
    headers: Sequence[str],
    rows: Sequence[Sequence[object]],
    spotlight_col: int | None = None,
    col_widths: Sequence[float] | None = None,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    body_font_pt: float | None = None,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> tuple[float, float, float, float]:
    """
    [F4-B / S11] Render Minimal Consulting / Academic Three-Line Comparison Table (native PowerPoint Table):
    - Zero vertical borders, strong top/header/bottom rules (`1.5pt #0F172A`), ultra-light row hairlines (`0.75pt #E2E8F0`).
    - Optional single-column soft spotlight (`spotlight_col`) with tinted fill and accent header text.
    - Content-Driven row heights measured via `measure_text_layout()`; all cell fonts `>= min_font_pt`.
    Returns `(left, top, total_width, actual_table_h)`.
    """
    hdr_list = [str(h or "").strip() for h in (headers or [])]
    n_cols = len(hdr_list)
    if n_cols == 0:
        return (round(left, 3), round(top, 3), round(total_width, 3), 0.0)

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.20)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, _min_floor, resolved_pt, _typo, sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.0
    )
    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_pri = pal["primary_accent"]
    theme_canvas = pal["bg_canvas"]
    theme_card_bg = pal["bg_card"]
    theme_border = pal["border_card"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    div_subtle = pal["divider_subtle"]
    spot_bg = _blend_hex(theme_pri, theme_card_bg, 0.16 if is_dark_theme else 0.09)
    hdr_bg = _blend_hex(theme_card_bg, theme_border, 0.30) if is_dark_theme else _blend_hex(theme_canvas, "#E2E8F0", 0.25)
    alt_row_bg = _blend_hex(theme_canvas, theme_card_bg, 0.45)
    ls = float(sp.get("line_spacing", 1.24))

    hdr_pt = _round_half_pt(resolved_pt + 0.5)
    row_list = [list(r) for r in (rows or [])]
    n_rows = 1 + len(row_list)

    if col_widths and len(col_widths) == n_cols:
        tot_w = sum(float(c) for c in col_widths) or float(n_cols)
        resolved_col_ws = [total_width * (float(c) / tot_w) for c in col_widths]
    else:
        if n_cols >= 3:
            first_w = round(total_width * 0.22, 3)
            rem_w = (total_width - first_w) / (n_cols - 1)
            resolved_col_ws = [first_w] + [rem_w] * (n_cols - 1)
        else:
            resolved_col_ws = [total_width / n_cols] * n_cols

    # Measure exact Content-Driven row heights
    row_heights: list[float] = []
    hdr_h = 0.42
    for c_i, h_txt in enumerate(hdr_list):
        m = measure_text_layout(h_txt, max(0.50, resolved_col_ws[c_i] - 0.24), hdr_pt, bold=True, line_spacing=1.18)
        hdr_h = max(hdr_h, float(m["safe_height_in"]) + 0.18)
    row_heights.append(round(hdr_h, 3))

    for r_vals in row_list:
        rh = 0.44
        for c_i in range(n_cols):
            val_s = str(r_vals[c_i] if c_i < len(r_vals) else "").strip()
            m = measure_text_layout(val_s, max(0.50, resolved_col_ws[c_i] - 0.24), resolved_pt, bold=(c_i == 0), line_spacing=ls)
            rh = max(rh, float(m["safe_height_in"]) + 0.18)
        row_heights.append(round(rh, 3))

    sum_h = sum(row_heights)
    tbl_exp = _calc_zone2_expansion_factor(avail_h, sum_h)
    cell_pad_y = round(min(0.16, 0.08 * tbl_exp), 3) if tbl_exp > 1.0 else 0.08
    if tbl_exp > 1.0 and sum_h > 0:
        target_tbl_h = min(max(sum_h, avail_h - 0.50), sum_h * (1.0 + (tbl_exp - 1.0) * 0.72))
        if target_tbl_h > sum_h + 0.04:
            grow_ratio = target_tbl_h / sum_h
            row_heights = [round(rh * grow_ratio, 3) for rh in row_heights]
            sum_h = sum(row_heights)

    tbl_budget_h = max(resolved_h, avail_h) if tbl_exp > 1.0 else resolved_h
    if sum_h > tbl_budget_h and sum_h > 0:
        scale_f = tbl_budget_h / sum_h
        row_heights = [max(0.34, round(rh * scale_f, 3)) for rh in row_heights]
    actual_tbl_h = round(min(tbl_budget_h, sum(row_heights)), 3)

    tbl_shape = slide.shapes.add_table(
        n_rows, n_cols, Inches(left), Inches(top), Inches(total_width), Inches(actual_tbl_h)
    )
    table = tbl_shape.table

    # Disable PowerPoint built-in blue theme table banding
    with suppress(AttributeError, TypeError):
        tbl_pr = table._tbl.tblPr
        if tbl_pr is not None:
            for attr in ("firstRow", "bandRow", "bandCol", "firstCol", "lastCol", "lastRow"):
                tbl_pr.set(attr, "0")
            for style_id in list(tbl_pr.findall(f"{{{_OMML_A_NS}}}tableStyleId")):
                tbl_pr.remove(style_id)

    for c_i, cw in enumerate(resolved_col_ws):
        table.columns[c_i].width = Inches(cw)

    # Render Header Row (Three-Line top & bottom strong rules)
    table.rows[0].height = Inches(row_heights[0])
    for c_i, h_txt in enumerate(hdr_list):
        cell = table.cell(0, c_i)
        is_spot = spotlight_col is not None and c_i == spotlight_col
        _set_table_cell_ooxml_style(
            cell,
            fill_hex=spot_bg if is_spot else hdr_bg,
            top_border=(1.5, theme_pri if is_spot else ink_pri),
            bottom_border=(1.5, theme_pri if is_spot else ink_pri),
            margin_l_in=0.12,
            margin_r_in=0.12,
            margin_t_in=cell_pad_y,
            margin_b_in=cell_pad_y,
            anchor=MSO_ANCHOR.MIDDLE,
        )
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        p.line_spacing = 1.18
        _populate_paragraph_runs(p, h_txt, hdr_pt, theme_pri if is_spot else ink_pri, bold=True)

    # Render Data Rows
    for r_i, r_vals in enumerate(row_list, start=1):
        table.rows[r_i].height = Inches(row_heights[r_i])
        is_last = r_i == len(row_list)
        for c_i in range(n_cols):
            cell = table.cell(r_i, c_i)
            val_s = str(r_vals[c_i] if c_i < len(r_vals) else "").strip()
            is_spot = spotlight_col is not None and c_i == spotlight_col
            cell_bg = spot_bg if is_spot else (theme_card_bg if r_i % 2 == 1 else alt_row_bg)
            _set_table_cell_ooxml_style(
                cell,
                fill_hex=cell_bg,
                top_border=None,
                bottom_border=(1.5, ink_pri) if is_last else (0.75, div_subtle),
                margin_l_in=0.12,
                margin_r_in=0.12,
                margin_t_in=cell_pad_y,
                margin_b_in=cell_pad_y,
                anchor=MSO_ANCHOR.TOP,
            )
            tf = cell.text_frame
            tf.word_wrap = True
            lines = val_s.splitlines() or [val_s]
            for l_i, seg in enumerate(lines):
                p = tf.paragraphs[0] if l_i == 0 else tf.add_paragraph()
                p.alignment = PP_ALIGN.LEFT
                p.line_spacing = ls
                _populate_paragraph_runs(
                    p,
                    seg,
                    resolved_pt,
                    ink_pri if c_i == 0 else ink_body,
                    bold=(c_i == 0),
                    bold_color_hex=theme_pri if is_spot else ink_pri,
                )

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y((round(left, 3), round(top, 3), round(total_width, 3), actual_tbl_h), dy_in)


def draw_kpi_strip_slide(
    slide,
    kpi_items: Sequence[dict[str, object]],
    insight_blocks: Sequence[object] = (),
    spotlight_idx: int | None = 0,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    body_font_pt: float | None = None,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> list[tuple[float, float, float, float]]:
    """
    [F5-B / S10] Render Top Quantitative KPI Metric Strip (2–4 KPIs) + Lower Unboxed Insight Zone:
    - Ideal for cross-case quantitative summaries (never crammed inside Matplotlib charts!).
    - Top strip is clean & unboxed with vertical hairlines (spotlight KPI gets top accent bar + soft wash).
    - Lower insight blocks flow TOP-aligned below a crisp horizontal divider.
    Returns `[kpi_strip_rect, *insight_rects]`.
    """
    k_list = list(kpi_items or [])[:4]
    if not k_list:
        return []

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.66)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, min_floor, resolved_pt, typo, sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.5
    )
    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_pri = pal["primary_accent"]
    theme_canvas = pal["bg_canvas"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    ink_muted = pal["ink_muted"]
    div_strong = pal["divider_strong"]
    div_subtle = pal["divider_subtle"]
    muted_acc = pal["muted_accent"]
    ls = float(sp.get("line_spacing", 1.30))

    n_kpi = len(k_list)
    k_gap = 0.24
    k_col_w = (total_width - k_gap * (n_kpi - 1)) / n_kpi
    val_pt_base = 34.0 if n_kpi <= 3 else 28.0
    lbl_pt = max(min_floor, _round_half_pt(resolved_pt + 0.5))
    note_pt = max(min_floor, float(typo["caption"]))
    lead_pt = float(typo["lead"])

    def _resolve_kpi_fields(item: dict[str, object]) -> tuple[str, str, str]:
        v_s = _first_non_empty_str(item, "value", "stat", "metric", "number", "kpi", "num")
        l_s = _first_non_empty_str(item, "label", "title", "heading", "name")
        lead_s = _first_non_empty_str(item, "lead")
        if not l_s and lead_s:
            l_s, lead_s = lead_s, ""
        elif lead_s == l_s:
            lead_s = ""
        delta_s = _first_non_empty_str(item, "delta")
        extra_n = _first_non_empty_str(item, "note", "detail", "desc", "body", "subtitle", "sub", "text", "caption")

        note_lines: list[str] = []
        if lead_s and delta_s and delta_s != lead_s:
            note_lines.append(f"{lead_s}｜{delta_s}" if (len(lead_s) + len(delta_s) <= 22) else f"{lead_s}\n{delta_s}")
        elif lead_s:
            note_lines.append(lead_s)
        elif delta_s:
            note_lines.append(delta_s)

        if extra_n and extra_n not in (lead_s, delta_s):
            if note_lines and "\n" not in note_lines[-1] and (len(note_lines[-1]) + len(extra_n) <= 22):
                note_lines[-1] = f"{note_lines[-1]}｜{extra_n}"
            else:
                note_lines.append(extra_n)

        for ck in ("items", "rows", "points", "bullets"):
            sub_raw = _coerce_items_list(item.get(ck)) if isinstance(item, dict) else []
            if sub_raw:
                for sub_it in sub_raw:
                    s_ld, s_bd = _parse_lead_body_item(sub_it)
                    line = f"**{s_ld}**：{s_bd}" if (s_ld and s_bd) else (s_ld or s_bd)
                    if line and line not in note_lines:
                        note_lines.append(line)
                break

        n_s = "\n".join(note_lines).strip()
        return v_s, l_s, n_s

    # Compute Content-Driven KPI strip height
    max_kpi_h = 1.30
    kpi_parsed: list[tuple[str, str, str, float]] = []
    for k_item in k_list:
        val_s, lbl_s, note_s = _resolve_kpi_fields(k_item)
        inner_kw = max(0.80, k_col_w - 0.24)

        # Pick largest clean single-line value font size (never shrinking below 22pt)
        chosen_vpt = val_pt_base
        while chosen_vpt > 22.0 and val_s:
            mv = measure_text_layout(val_s, inner_kw, chosen_vpt, bold=True, line_spacing=1.10)
            if int(mv["line_count"]) <= 1:
                break
            chosen_vpt -= 2.0
        kpi_parsed.append((val_s, lbl_s, note_s, chosen_vpt))

        h_need = 0.0
        if val_s:
            m_v = measure_text_layout(val_s, inner_kw, chosen_vpt, bold=True, line_spacing=1.12)
            v_lines = max(1, int(m_v["line_count"]))
            if lbl_s or note_s:
                h_need += v_lines * ((chosen_vpt * MSJH_LINE_HEIGHT_EM) / 72.0) * 1.12 + (4.0 / 72.0)
            else:
                h_need += float(m_v["content_height_in"])
        if lbl_s:
            m_l = measure_text_layout(lbl_s, inner_kw, lbl_pt, bold=True, line_spacing=1.20)
            l_lines = max(1, int(m_l["line_count"]))
            if note_s:
                h_need += l_lines * ((lbl_pt * MSJH_LINE_HEIGHT_EM) / 72.0) * 1.20 + (2.0 / 72.0)
            else:
                h_need += float(m_l["content_height_in"])
        if note_s:
            n_segs = note_s.splitlines() or [note_s]
            for ni, n_seg in enumerate(n_segs):
                m_n = measure_text_layout(n_seg, inner_kw, note_pt, bold=False, line_spacing=1.20)
                n_lines = max(1, int(m_n["line_count"]))
                if ni < len(n_segs) - 1:
                    h_need += n_lines * ((note_pt * MSJH_LINE_HEIGHT_EM) / 72.0) * 1.20 + (2.0 / 72.0)
                else:
                    h_need += float(m_n["content_height_in"])
        # Textbox sits at top+0.14 with height strip_h-0.20 (usable ~ strip_h-0.26); add >=20% breathing room
        max_kpi_h = max(max_kpi_h, h_need * 1.22 + 0.30)

    has_insights = bool(insight_blocks)
    strip_h = round(min(resolved_h * (0.50 if has_insights else 0.72), max(1.38, max_kpi_h)), 3)
    kpi_note_ls = 1.14 if max_kpi_h > strip_h else 1.20

    # Pre-measure natural insight blocks height to drive Direction 2 expansion before drawing
    ins_list = list(insight_blocks) if has_insights else []
    n_ins = len(ins_list)
    ins_gap = 0.34
    ins_w = (total_width - ins_gap * max(0, n_ins - 1)) / max(1, n_ins)
    max_nat_ins_h = 0.0
    if has_insights:
        inner_iw_est = max(0.70, ins_w - 0.16)
        ht_pt_est = _round_half_pt(resolved_pt + 2.0)
        k_pt_est = float(typo["kicker"])
        s_pt_est = float(typo["subtitle"])
        for blk in ins_list:
            bk_k = ""
            bk_s = ""
            if isinstance(blk, dict):
                has_col = any(bool(_coerce_items_list(blk.get(ck))) for ck in ("rows", "items", "points", "bullets"))
                bk_k = _first_non_empty_str(blk, "kicker", "badge", "num", "step")
                b_t = _first_non_empty_str(blk, "title", "heading", "label", "name")
                bk_s = _first_non_empty_str(blk, "subtitle", "sub")
                b_l = _first_non_empty_str(blk, "lead")
                if bk_k or bk_s or has_col or (b_t and b_l and b_l != b_t):
                    bk_h = b_t
                    ex_ld = b_l if b_l != b_t else ""
                    s_its = _extract_lead_body_items(blk, extra_lead=ex_ld, include_subtitle_as_body=False)
                else:
                    bk_h = ""
                    s_its = _extract_lead_body_items(blk, extra_lead=(b_t or b_l), include_subtitle_as_body=True)
            else:
                bk_h = ""
                ld_e, bd_e = _parse_lead_body_item(blk)
                s_its = [(ld_e, bd_e)] if (ld_e or bd_e) else []
            est_h = 0.0
            if bk_k or bk_h or bk_s:
                est_h += _measure_three_tier_header(bk_k, bk_h, bk_s, inner_iw_est, k_pt_est, ht_pt_est, s_pt_est) + 0.10
            if s_its:
                m_sh = [_measure_lead_body_item_height(ld_e, bd_e, inner_iw_est, lead_pt, resolved_pt, line_spacing=ls) for ld_e, bd_e in s_its]
                est_h += sum(m_sh) + 0.14 * max(0, len(m_sh) - 1) + 0.02
            max_nat_ins_h = max(max_nat_ins_h, max(0.45, est_h))

    nat_kpi_total_h = strip_h + ((0.20 + 0.22 + max_nat_ins_h) if has_insights else 0.0)
    kpi_exp = _calc_zone2_expansion_factor(avail_h, nat_kpi_total_h)
    if kpi_exp > 1.0:
        strip_extra = min(0.24, (kpi_exp - 1.0) * 0.55)
        expanded_strip = min(2.50, min(avail_h * (0.44 if has_insights else 0.72), strip_h + strip_extra))
        strip_h = round(max(strip_h, expanded_strip), 3)
    div_gap = round(0.20 * kpi_exp, 3) if kpi_exp > 1.0 else 0.20
    ins_top_gap = round(0.22 * kpi_exp, 3) if kpi_exp > 1.0 else 0.22
    ins_hdr_gap = round(0.08 * kpi_exp, 3) if kpi_exp > 1.0 else 0.08
    ins_item_gap_cap = round(0.14 * kpi_exp, 3) if kpi_exp > 1.0 else 0.14
    kpi_budget_bottom = avail_bottom if kpi_exp > 1.0 else (top + resolved_h)

    coords: list[tuple[float, float, float, float]] = [(round(left, 3), round(top, 3), round(total_width, 3), strip_h)]
    cur_x = left
    for idx, (k_item, (val_s, lbl_s, note_s, vpt)) in enumerate(zip(k_list, kpi_parsed)):
        is_spot = (spotlight_idx == idx) if spotlight_idx is not None else bool(k_item.get("is_spotlight", False))
        acc_hex = str(k_item.get("accent", theme_pri if is_spot else muted_acc))

        if is_spot:
            wash = _add_flat_shape(
                slide,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(cur_x), Inches(top), Inches(k_col_w), Inches(strip_h),
            )
            wash.adjustments[0] = 0.04
            wash.fill.solid()
            wash.fill.fore_color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_canvas, 0.14 if is_dark_theme else 0.08))
            wash.line.fill.background()

        tbar = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(cur_x + 0.12), Inches(top + 0.01), Inches(max(0.5, k_col_w - 0.24)), Inches(0.06 if is_spot else 0.03),
        )
        tbar.fill.solid()
        tbar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else div_strong)
        tbar.line.fill.background()

        if idx > 0:
            vdiv = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(cur_x - k_gap / 2.0), Inches(top + 0.14), Inches(0.012), Inches(max(0.5, strip_h - 0.28)),
            )
            vdiv.fill.solid()
            vdiv.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
            vdiv.line.fill.background()

        tb = slide.shapes.add_textbox(
            Inches(cur_x + 0.12), Inches(top + 0.14), Inches(max(0.6, k_col_w - 0.24)), Inches(max(0.6, strip_h - 0.20))
        )
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = Inches(0.02)
        tf.margin_top = Inches(0.01)

        first_used = False
        if val_s:
            p0 = tf.paragraphs[0]
            first_used = True
            p0.alignment = PP_ALIGN.LEFT
            p0.line_spacing = 1.12
            if lbl_s or note_s:
                p0.space_after = Pt(4)
            _populate_paragraph_runs(p0, val_s, vpt, acc_hex if is_spot else ink_pri, bold=True)

        if lbl_s:
            p1 = tf.add_paragraph() if first_used else tf.paragraphs[0]
            first_used = True
            p1.alignment = PP_ALIGN.LEFT
            p1.line_spacing = 1.20
            if note_s:
                p1.space_after = Pt(2)
            _populate_paragraph_runs(p1, lbl_s, lbl_pt, ink_pri, bold=True)

        if note_s:
            n_lines = note_s.splitlines() or [note_s]
            for ni, n_seg in enumerate(n_lines):
                p2 = tf.add_paragraph() if first_used else tf.paragraphs[0]
                first_used = True
                p2.alignment = PP_ALIGN.LEFT
                p2.line_spacing = kpi_note_ls
                if ni < len(n_lines) - 1:
                    p2.space_after = Pt(2)
                _populate_paragraph_runs(p2, n_seg, note_pt, ink_muted, bold=False, bold_color_hex=ink_pri)

        cur_x += k_col_w + k_gap

    # Divider & Lower Insight Blocks
    if has_insights:
        div_y = round(top + strip_h + div_gap, 3)
        hdiv = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(left), Inches(div_y), Inches(total_width), Inches(0.015),
        )
        hdiv.fill.solid()
        hdiv.fill.fore_color.rgb = hex_to_rgb_color(div_strong)
        hdiv.line.fill.background()

        ins_top = round(div_y + ins_top_gap, 3)
        ins_h = max(1.0, round(kpi_budget_bottom - ins_top, 3))
        has_explicit_ins_spot = any(isinstance(b, dict) and b.get("is_spotlight") is not None for b in ins_list)

        ix = left
        for i_idx, blk in enumerate(ins_list):
            blk_kicker = ""
            blk_sub = ""
            if isinstance(blk, dict):
                has_collection = any(bool(_coerce_items_list(blk.get(ck))) for ck in ("rows", "items", "points", "bullets"))
                blk_kicker = _first_non_empty_str(blk, "kicker", "badge", "num", "step")
                b_title = _first_non_empty_str(blk, "title", "heading", "label", "name")
                blk_sub = _first_non_empty_str(blk, "subtitle", "sub")
                b_lead = _first_non_empty_str(blk, "lead")
                if blk_kicker or blk_sub or has_collection or (b_title and b_lead and b_lead != b_title):
                    blk_heading = b_title
                    extra_ld = b_lead if b_lead != b_title else ""
                    sub_items = _extract_lead_body_items(blk, extra_lead=extra_ld, include_subtitle_as_body=False)
                else:
                    blk_heading = ""
                    sub_items = _extract_lead_body_items(blk, extra_lead=(b_title or b_lead), include_subtitle_as_body=True)
            else:
                blk_heading = ""
                ld, bd = _parse_lead_body_item(blk)
                sub_items = [(ld, bd)] if (ld or bd) else []

            is_spot_ins = bool(blk.get("is_spotlight", False)) if (has_explicit_ins_spot and isinstance(blk, dict)) else (i_idx == 0)
            bar_hex = theme_pri if is_spot_ins else div_strong
            cur_iy = ins_top
            inner_iw = max(0.70, ins_w - 0.16)

            measured_subs: list[tuple[str, str, float]] = [
                (ld, bd, _measure_lead_body_item_height(ld, bd, inner_iw, lead_pt, resolved_pt, line_spacing=ls))
                for ld, bd in sub_items
            ]
            est_sub_h = sum(s[2] for s in measured_subs) + 0.06 * max(0, len(measured_subs) - 1) if measured_subs else 0.0

            if blk_kicker or blk_heading or blk_sub:
                ht_pt = _round_half_pt(resolved_pt + 2.0)
                k_pt = float(typo["kicker"])
                s_pt = float(typo["subtitle"])
                hh = _measure_three_tier_header(blk_kicker, blk_heading, blk_sub, inner_iw, k_pt, ht_pt, s_pt)
                if blk_kicker and blk_heading and blk_sub and measured_subs and (hh + 0.08 + est_sub_h) > ins_h:
                    blk_kicker = f"{blk_kicker} · {blk_sub}"
                    blk_sub = ""
                    hh = _measure_three_tier_header(blk_kicker, blk_heading, blk_sub, inner_iw, k_pt, ht_pt, s_pt)
                hdr_box_h = round(min(ins_h * 0.54, hh + 0.02), 3)
                _render_three_tier_header(
                    slide,
                    x=ix + 0.14,
                    y=cur_iy,
                    w=inner_iw,
                    h=hdr_box_h,
                    kicker=blk_kicker,
                    title=blk_heading,
                    subtitle=blk_sub,
                    kicker_pt=k_pt,
                    title_pt=ht_pt,
                    sub_pt=s_pt,
                    kicker_hex=theme_pri if is_spot_ins else ink_muted,
                    title_hex=theme_pri if is_spot_ins else ink_pri,
                    sub_hex=ink_muted,
                )
                cur_iy = round(cur_iy + hdr_box_h + ins_hdr_gap, 3)

            if measured_subs:
                avail_sub_h = max(0.32, (ins_top + ins_h) - cur_iy)
                raw_sub_sum = sum(s[2] for s in measured_subs)
                min_sub_gap = 0.05 * max(0, len(measured_subs) - 1)
                ins_lead_hex = theme_pri if (is_spot_ins and not (blk_kicker or blk_heading or blk_sub)) else ink_pri
                if len(measured_subs) > 1 and (raw_sub_sum + min_sub_gap) > avail_sub_h:
                    _render_compact_lead_body_stack(
                        slide,
                        x=ix + 0.14,
                        y=cur_iy,
                        w=inner_iw,
                        h=avail_sub_h,
                        items=[(ld, bd) for ld, bd, _ih in measured_subs],
                        lead_pt=lead_pt,
                        body_pt=resolved_pt,
                        lead_hex=ins_lead_hex,
                        body_hex=ink_body,
                        bold_color_hex=ink_pri,
                        line_spacing=min(ls, 1.16),
                        para_space_after_pt=2.0,
                    )
                    cur_iy = round(cur_iy + avail_sub_h, 3)
                else:
                    eff_ig = (
                        min(ins_item_gap_cap, max(0.05, (avail_sub_h - raw_sub_sum) / max(1, len(measured_subs) - 1)))
                        if len(measured_subs) > 1
                        else 0.0
                    )
                    for ld, bd, ih in measured_subs:
                        rem = max(0.28, (ins_top + ins_h) - cur_iy)
                        bh = round(min(rem, ih + 0.02), 3)
                        _render_lead_body_box(
                            slide, ix + 0.14, cur_iy, inner_iw, bh,
                            ld, bd, lead_pt, resolved_pt, ins_lead_hex,
                            ink_body, ink_pri, line_spacing=ls,
                        )
                        cur_iy = round(cur_iy + bh + eff_ig, 3)

            used_h = max(0.45, min(ins_h, cur_iy - ins_top - 0.06))
            lbar = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(ix), Inches(ins_top + 0.03), Inches(0.055 if is_spot_ins else 0.035), Inches(max(0.32, used_h - 0.06)),
            )
            lbar.fill.solid()
            lbar.fill.fore_color.rgb = hex_to_rgb_color(bar_hex)
            lbar.line.fill.background()

            coords.append((round(ix, 3), round(ins_top, 3), round(ins_w, 3), round(used_h, 3)))
            ix += ins_w + ins_gap

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y(coords, dy_in)


def draw_focal_anatomy_s6(
    slide,
    focal_title: str,
    focal_formula: str,
    focal_note: str = "",
    breakdown_items: Sequence[object] = (),
    mode: str = "left_right",
    focal_ratio: float = 0.38,
    use_omml: bool = False,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    body_font_pt: float = 13.0,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> tuple[float, float, float, float]:
    """
    [F5-C / S6] Render Focal Equation / Core Principle Anatomy Slide optimized for 16:9 widescreen:
    - `mode="left_right"` (default): Left `38%` dark focal box + Right `62%` unboxed TOP-aligned breakdown rows.
    - `mode="top_bottom"`: Compact top focal banner + Bottom horizontal unboxed breakdown columns.
    - `use_omml=True`: injects native editable `<m:oMath>` equation via `insert_omml_equation()`.
    - All text enforces `>= min_font_pt`.
    """
    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.26)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, min_floor, resolved_pt, _typo, _sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.0, caller_default_pt=13.0
    )
    dark_bg = dt.get("bookend_dark_bg", "#0F172A")
    dark_acc = dt.get("bookend_accent", "#38BDF8")
    items = _normalize_callout_items(breakdown_items)

    layout_mode = str(mode or "left_right").strip().lower()
    gap = 0.38
    ratio = max(0.30, min(0.55, float(focal_ratio)))

    ft_pt = max(min_floor, _round_half_pt(resolved_pt))
    formula_pt = max(18.0, _round_half_pt(resolved_pt + 4.0))
    note_pt = max(min_floor, _round_half_pt(resolved_pt - 0.5 if resolved_pt >= 13.5 else resolved_pt))

    def _measure_focal_min_h(box_w: float) -> float:
        tw = max(0.8, box_w - 0.56)
        need = 0.56
        t_s = str(focal_title or "").strip()
        if t_s:
            need += float(measure_text_layout(t_s, tw, ft_pt, bold=True, line_spacing=1.20)["safe_height_in"]) + 0.14
        f_s = str(focal_formula or "").strip()
        if f_s:
            need += float(measure_text_layout(f_s, tw, formula_pt, bold=True, line_spacing=1.28)["safe_height_in"]) + 0.16
        n_s = str(focal_note or "").strip()
        if n_s:
            need += float(measure_text_layout(n_s, tw, note_pt, bold=False, line_spacing=1.28)["safe_height_in"])
        return round(max(2.10, need + 0.24), 3)

    if layout_mode == "top_bottom":
        fh = min(1.95, max(1.35, resolved_h * 0.34)) if items else resolved_h * 0.55
        fx, fy, fw = left, top, total_width
        if items:
            horz_h = _estimate_horizontal_band_height(items, total_width, resolved_pt)
            nat_tb_h = fh + 0.24 + horz_h
            tb_exp = _calc_zone2_expansion_factor(avail_h, nat_tb_h)
            tb_gap = round(0.24 * tb_exp, 3) if tb_exp > 1.0 else 0.24
            tb_budget_h = max(resolved_h, avail_h) if tb_exp > 1.0 else resolved_h
            _render_unboxed_callouts_horizontal(
                slide, items, left, top + fh + tb_gap, total_width, max(0.8, tb_budget_h - fh - tb_gap), resolved_pt, 0, dt
            )
    else:
        fw = (total_width - gap) * ratio if items else total_width
        fx, fy = left, top
        focal_min_h = _measure_focal_min_h(fw)
        if items:
            rx = left + fw + gap
            rw = total_width - fw - gap
            right_nat_h = _estimate_vertical_callouts_height(items, rw, None, resolved_pt, gap_scale=1.0)
            nat_lr_h = max(focal_min_h, right_nat_h)
            lr_exp = _calc_zone2_expansion_factor(avail_h, nat_lr_h)
            lr_budget_h = max(resolved_h, avail_h) if lr_exp > 1.0 else resolved_h
            before_r = len(slide.shapes)
            _render_unboxed_callouts_vertical(
                slide, items, rx, top, rw, lr_budget_h, None, resolved_pt, 0, dt, gap_scale=lr_exp
            )
            right_shapes = list(slide.shapes)[before_r:]
            right_actual_h = (
                max((float(s.top or 0) + float(s.height or 0)) / 914400.0 for s in right_shapes) - float(top)
                if right_shapes
                else right_nat_h
            )
            fh = round(min(lr_budget_h, max(focal_min_h, right_actual_h)), 3)
        else:
            fh = round(min(resolved_h, max(focal_min_h, resolved_h * 0.68)), 3)

    fbox = _add_flat_shape(
        slide,
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(fx), Inches(fy), Inches(fw), Inches(fh),
    )
    fbox.adjustments[0] = 0.04
    fbox.fill.solid()
    fbox.fill.fore_color.rgb = hex_to_rgb_color(dark_bg)
    fbox.line.color.rgb = hex_to_rgb_color(dark_acc)
    fbox.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(
        Inches(fx + 0.26), Inches(fy + 0.18), Inches(max(0.8, fw - 0.52)), Inches(max(0.6, fh - 0.36))
    )
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    is_centered = layout_mode == "top_bottom"

    p0 = tf.paragraphs[0]
    p0.alignment = PP_ALIGN.CENTER if is_centered else PP_ALIGN.LEFT
    p0.space_after = Pt(10)
    _populate_paragraph_runs(p0, str(focal_title).strip(), ft_pt, "#CBD5E1", bold=True)

    formula_str = str(focal_formula or "").strip()
    if use_omml and formula_str:
        insert_omml_equation(
            tf,
            formula_str,
            font_pt=formula_pt,
            color_hex=dark_acc,
            align="center" if is_centered else "left",
            append_paragraph=True,
        )
        if focal_note and str(focal_note).strip():
            tf.paragraphs[-1].space_after = Pt(10)
    else:
        for f_i, f_line in enumerate(formula_str.splitlines() or [formula_str]):
            p_f = tf.add_paragraph()
            p_f.alignment = PP_ALIGN.CENTER if is_centered else PP_ALIGN.LEFT
            p_f.line_spacing = 1.28
            if f_i == len(formula_str.splitlines() or [formula_str]) - 1 and focal_note:
                p_f.space_after = Pt(10)
            _populate_paragraph_runs(p_f, f_line, formula_pt, dark_acc, bold=True, bold_color_hex="#FFFFFF")

    if focal_note and str(focal_note).strip():
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER if is_centered else PP_ALIGN.LEFT
        p2.line_spacing = 1.28
        _populate_paragraph_runs(p2, str(focal_note).strip(), note_pt, "#FDE68A", bold=False, bold_color_hex="#FFFFFF")

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y((round(fx, 3), round(fy, 3), round(fw, 3), round(fh, 3)), dy_in)


def draw_theme_geometric_accent(
    slide,
    motif_type: str = "diagonal_wedge",
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
    **kwargs,
) -> None:
    """
    [Mode 3 Tier 1] Add a restrained, 100% native PowerPoint editable thematic geometric motif
    strictly within peripheral margin space (20/80 restraint, zero drop shadow, zero text collision).
    Supported `motif_type`:
      - `"diagonal_wedge"`: architectural right-edge diagonal wedge + crisp accent edge strip.
      - `"ruler_ticks"`: precision analytical ruler tick strip along far-left or bottom margin.
      - `"step_blocks"`: ascending 4-step editorial stair silhouette in bottom-right corner.
      - `"vector_scale"`: minimalist geometric balance scale motif in bottom-right / top-right corner.
    """
    dt, _min_floor, _body_pt, _typo, _sp = _resolve_engine_context(tokens, doc_theme_id)
    primary = str(kwargs.get("accent_hex") or dt.get("primary_accent", "#0284C7"))
    bg_canvas = dt.get("bg_canvas", "#F8FAFC")
    tint = str(kwargs.get("tint_hex") or _blend_hex(primary, bg_canvas, 0.18))
    muted = str(kwargs.get("muted_hex") or dt.get("border_card", "#CBD5E1"))
    m_type = str(motif_type or "diagonal_wedge").strip().lower()

    if m_type == "diagonal_wedge":
        # Crisp peripheral top-right diagonal architectural accent (stays strictly outside Zone 1/2 content)
        w1 = _add_flat_shape(
            slide,
            MSO_SHAPE.RIGHT_TRIANGLE,
            Inches(12.55), Inches(0.0), Inches(0.783), Inches(0.88),
        )
        w1.rotation = 180.0
        w1.fill.solid()
        w1.fill.fore_color.rgb = hex_to_rgb_color(tint)
        w1.line.fill.background()

        strip = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(13.253), Inches(0.0), Inches(0.08), Inches(7.5),
        )
        strip.fill.solid()
        strip.fill.fore_color.rgb = hex_to_rgb_color(primary)
        strip.line.fill.background()
        return

    if m_type == "ruler_ticks":
        # Precision analytical scale ticks tucked cleanly along the far-left margin (x <= 0.28")
        spine = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(0.14), Inches(1.40), Inches(0.015), Inches(5.40),
        )
        spine.fill.solid()
        spine.fill.fore_color.rgb = hex_to_rgb_color(muted)
        spine.line.fill.background()

        n_ticks = int(kwargs.get("num_ticks", 13))
        n_ticks = max(5, min(25, n_ticks))
        step_y = 5.40 / (n_ticks - 1)
        highlight_idx = int(kwargs.get("highlight_idx", n_ticks // 2))
        for i in range(n_ticks):
            ty = 1.40 + i * step_y
            is_major = (i % 4 == 0)
            is_hl = (i == highlight_idx)
            tw = 0.16 if is_hl else (0.12 if is_major else 0.07)
            th = 0.032 if is_hl else (0.018 if is_major else 0.012)
            tk = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(0.14), Inches(ty - th / 2.0), Inches(tw), Inches(th),
            )
            tk.fill.solid()
            tk.fill.fore_color.rgb = hex_to_rgb_color(primary if is_hl else (muted if not is_major else "#94A3B8"))
            tk.line.fill.background()
        return

    if m_type == "step_blocks":
        # Ascending geometric stair motif tucked cleanly in bottom-right margin (y >= 7.12" or right edge)
        base_x = float(kwargs.get("left", 11.75))
        base_y = float(kwargs.get("bottom", 7.42))
        n_bars = 4
        bar_w = 0.24
        bar_gap = 0.06
        heights = [0.10, 0.16, 0.22, 0.30]
        weights = [0.22, 0.42, 0.68, 1.00]
        for i in range(n_bars):
            bh = heights[i]
            bx = base_x + i * (bar_w + bar_gap)
            by = base_y - bh
            blk = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(bx), Inches(by), Inches(bar_w), Inches(bh),
            )
            blk.fill.solid()
            blk.fill.fore_color.rgb = hex_to_rgb_color(_blend_hex(primary, bg_canvas, weights[i]))
            blk.line.fill.background()
        return

    if m_type == "vector_scale":
        # Minimalist geometric balance scale motif tucked cleanly in bottom-right corner
        cx = float(kwargs.get("center_x", 12.52))
        base_y = float(kwargs.get("bottom", 7.40))
        tilt_deg = float(kwargs.get("tilt_deg", -6.0))

        # Fulcrum triangle
        tri = _add_flat_shape(
            slide,
            MSO_SHAPE.ISOSCELES_TRIANGLE,
            Inches(cx - 0.11), Inches(base_y - 0.18), Inches(0.22), Inches(0.18),
        )
        tri.fill.solid()
        tri.fill.fore_color.rgb = hex_to_rgb_color("#94A3B8")
        tri.line.fill.background()

        # Balance beam
        beam = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(cx - 0.48), Inches(base_y - 0.21), Inches(0.96), Inches(0.032),
        )
        beam.rotation = tilt_deg
        beam.fill.solid()
        beam.fill.fore_color.rgb = hex_to_rgb_color(primary)
        beam.line.fill.background()

        # Two minimal geometric weight markers at beam ends
        pan_l = _add_flat_shape(
            slide,
            MSO_SHAPE.OVAL,
            Inches(cx - 0.46), Inches(base_y - 0.28), Inches(0.11), Inches(0.11),
        )
        pan_l.fill.solid()
        pan_l.fill.fore_color.rgb = hex_to_rgb_color(tint)
        pan_l.line.fill.background()

        pan_r = _add_flat_shape(
            slide,
            MSO_SHAPE.OVAL,
            Inches(cx + 0.35), Inches(base_y - 0.32), Inches(0.13), Inches(0.13),
        )
        pan_r.fill.solid()
        pan_r.fill.fore_color.rgb = hex_to_rgb_color(primary)
        pan_r.line.fill.background()
        return

    raise ValueError(
        f"Unsupported motif_type '{motif_type}'. Expected one of: "
        "'diagonal_wedge', 'ruler_ticks', 'step_blocks', 'vector_scale'."
    )
