"""
pptx_engine/layouts_narrative.py
Narrative & flow layouts: F1-C, F2-A/B/C, and F3-A/B.
Note: `pptx_slide_engine` is the public entry point.
"""

import math
import re
from collections.abc import Sequence
from pathlib import Path

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from .tokens import (
    _add_flat_shape,
    _blend_hex,
    _populate_paragraph_runs,
    _resolve_engine_context,
    _round_half_pt,
    _theme_palette,
    hex_to_rgb_color,
)
from .text_layout import calc_pill_width, measure_text_layout
from .primitives import (
    _LEADING_INDEX_PREFIX_RE,
    _apply_zone2_optical_vertical_balance,
    _calc_zone2_expansion_factor,
    _estimate_horizontal_band_height,
    _estimate_vertical_callouts_height,
    _extract_lead_body_items,
    _first_non_empty_str,
    _measure_lead_body_item_height,
    _measure_three_tier_header,
    _normalize_callout_items,
    _render_compact_lead_body_stack,
    _render_lead_body_box,
    _render_three_tier_header,
    _render_unboxed_callouts_horizontal,
    _render_unboxed_callouts_vertical,
    _resolve_zone2_avail_bottom,
    _resolve_zone2_height,
    _shift_coords_y,
)
from .layouts_data import draw_visual_callout_slide

def draw_parallel_row_cards(
    slide,
    cards_spec: list[dict[str, object]],
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    gap: float = 0.26,
    spotlight_idx: int | None = None,
    body_font_pt: float | None = None,
    title_font_pt: float | None = None,
    width_ratios: list[float] | None = None,
    card_style: str = "clean_card",
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> list[tuple[float, float, float, float]]:
    """
    [F2-A / S1 + S2] Render 2, 3, or 4 parallel columns in Zone 2 (Module 1 & 2 Upgraded):
    - `card_style`:
      * `"clean_card"`: single-layer clean white card with de-noised spotlight (soft tint + single top bar + deep ink title).
      * `"minimal_column"`: borderless column with oversized soft numeral (`01`/`02`/`03`), short accent bar, and hairline gap dividers.
      * `"borderless_centerline"`: borderless contrast layout with crisp vertical centerline divider (ideal for 2-column S1).
    - Uses `measure_text_layout()`, `MSO_ANCHOR.TOP` natural flow stacking (abolishing `slot_h` equal splits),
      3-tier headers (`Kicker -> Title (+3pt) -> Subtitle`), independent 2-paragraph Lead/Body rows,
      Content-Driven Height, and eliminates the L789 unequal-row ghost separator bug.
    """
    n_cols = len(cards_spec)
    if n_cols == 0:
        return []

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.20)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    default_body = 13.5 if n_cols <= 2 else (12.5 if n_cols == 3 else 12.0)
    dt, min_floor, resolved_pt, typo, sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=default_body
    )
    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_primary = pal["primary_accent"]
    theme_border = pal["border_card"]
    theme_card_bg = pal["bg_card"]
    theme_canvas = pal["bg_canvas"]
    theme_ink_pri = pal["ink_primary"]
    theme_ink_body = pal["ink_body"]
    theme_ink_muted = pal["ink_muted"]
    div_subtle = pal["divider_subtle"]
    div_strong = pal["divider_strong"]
    muted_bar = pal["muted_bar"]
    muted_acc = pal["muted_accent"]

    style_norm = str(card_style or "clean_card").strip().lower()
    if style_norm not in ("clean_card", "minimal_column", "borderless_centerline"):
        style_norm = "clean_card"

    if title_font_pt is None:
        resolved_title_pt = float(typo["card_title"])
    else:
        resolved_title_pt = max(min_floor + 1.0, float(title_font_pt))
    kicker_pt = float(typo["kicker"])
    sub_pt = float(typo["subtitle"])
    lead_pt = float(typo["lead"])
    ls = float(sp.get("line_spacing", 1.30))
    base_item_gap = 0.22 if n_cols <= 2 else 0.18

    if style_norm in ("minimal_column", "borderless_centerline") and gap < 0.34:
        eff_gap = 0.42 if style_norm == "borderless_centerline" else 0.36
    else:
        eff_gap = float(gap)

    if width_ratios and len(width_ratios) == n_cols:
        tot_r = sum(float(r) for r in width_ratios) or float(n_cols)
        usable_w = total_width - eff_gap * (n_cols - 1)
        col_widths = [usable_w * (float(r) / tot_r) for r in width_ratios]
    else:
        w = (total_width - eff_gap * (n_cols - 1)) / n_cols
        col_widths = [w] * n_cols

    pad_x = 0.20 if style_norm == "clean_card" else 0.10
    num_band_h = 0.56 if style_norm == "minimal_column" else 0.0
    top_inset = (0.14 if style_norm == "clean_card" else 0.06) + num_band_h

    # Pre-measure 3-tier headers across all columns for aligned horizontal rhythm
    parsed_cols: list[dict[str, object]] = []
    max_hdr_h = 0.0
    for idx_c, card in enumerate(cards_spec):
        cw = col_widths[idx_c]
        inner_w = max(0.55, cw - 2.0 * pad_x)
        if style_norm == "minimal_column":
            kicker = _first_non_empty_str(card, "kicker", "badge", "step")
        else:
            kicker = _first_non_empty_str(card, "kicker", "badge", "step", "num")
        title = _first_non_empty_str(card, "title", "heading", "label", "name")
        subtitle = _first_non_empty_str(card, "subtitle", "sub")
        if kicker and not title:
            title, kicker = kicker, ""

        # Prevent duplicate leading numeral in minimal_column when title already begins with e.g. "01 "
        col_num_str = ""
        if style_norm == "minimal_column":
            has_explicit_num = isinstance(card, dict) and "num" in card and card.get("num") is not None
            if has_explicit_num:
                col_num_str = str(card.get("num") or "").strip()
            else:
                m_short_num = re.match(r"^\s*(0?\d{1,2})(?:[\.\)、:：\-—–\|｜\s]+)(.+)$", title)
                if m_short_num and _LEADING_INDEX_PREFIX_RE.match(title):
                    col_num_str = m_short_num.group(1).strip()
                    title = m_short_num.group(2).strip()
                elif _LEADING_INDEX_PREFIX_RE.match(title):
                    col_num_str = ""
                else:
                    col_num_str = f"{idx_c + 1:02d}"

        hdr_h_c = _measure_three_tier_header(kicker, title, subtitle, inner_w, kicker_pt, resolved_title_pt, sub_pt)
        max_hdr_h = max(max_hdr_h, hdr_h_c)

        card_lead = _first_non_empty_str(card, "lead")
        if card_lead == title:
            card_lead = ""
        raw_pairs = _extract_lead_body_items(card, extra_lead=card_lead)
        norm_rows: list[tuple[str, str, float]] = []
        for lead_s, body_s in raw_pairs:
            item_h = _measure_lead_body_item_height(lead_s, body_s, inner_w, lead_pt, resolved_pt, line_spacing=ls)
            norm_rows.append((lead_s, body_s, item_h))

        parsed_cols.append({
            "card": card,
            "cw": cw,
            "inner_w": inner_w,
            "num_str": col_num_str,
            "kicker": kicker,
            "title": title,
            "subtitle": subtitle,
            "rows": norm_rows,
        })

    header_h = round(min(resolved_h * 0.44, max(0.46, max_hdr_h)), 3)
    rule_gap = 0.08
    body_gap = 0.14
    nat_body_top = round(top + top_inset + header_h + rule_gap + body_gap, 3)

    # Measure natural Content-Driven Height first to check Direction 2 (natural expansion)
    nat_max_col_body_h = 0.0
    for col_info in parsed_cols:
        r_list: list[tuple[str, str, float]] = col_info["rows"]  # type: ignore[assignment]
        if r_list:
            stack_h = sum(r[2] for r in r_list) + base_item_gap * max(0, len(r_list) - 1)
            nat_max_col_body_h = max(nat_max_col_body_h, stack_h)

    nat_total_h = (nat_body_top - top) + nat_max_col_body_h + 0.24
    exp_factor = _calc_zone2_expansion_factor(avail_h, nat_total_h)
    if exp_factor > 1.0:
        rule_gap = round(rule_gap * exp_factor, 3)
        body_gap = round(body_gap * exp_factor, 3)
        base_item_gap = round(base_item_gap * exp_factor, 3)

    max_card_budget_h = max(resolved_h, avail_h) if exp_factor > 1.0 else resolved_h
    rule_y = round(top + top_inset + header_h + rule_gap, 3)
    body_top = round(rule_y + body_gap, 3)
    avail_body_h = max(0.90, round(top + max_card_budget_h - body_top - 0.16, 3))

    # Compute Content-Driven Height (pushes dead whitespace outside boxes!)
    max_col_body_h = 0.0
    for col_info in parsed_cols:
        r_list = col_info["rows"]  # type: ignore[assignment]
        if r_list:
            stack_h = sum(r[2] for r in r_list) + base_item_gap * max(0, len(r_list) - 1)
            max_col_body_h = max(max_col_body_h, stack_h)

    bot_pad = round(0.24 * exp_factor, 3) if exp_factor > 1.0 else 0.24
    needed_total_h = (body_top - top) + max_col_body_h + bot_pad
    actual_card_h = round(min(max_card_budget_h, max(min(max_card_budget_h, 2.30), needed_total_h)), 3)

    coords: list[tuple[float, float, float, float]] = []
    cur_x = left
    for idx, col_info in enumerate(parsed_cols):
        card: dict[str, object] = col_info["card"]  # type: ignore[assignment]
        cw = float(col_info["cw"])
        inner_w = float(col_info["inner_w"])
        is_spot = (spotlight_idx == idx) if spotlight_idx is not None else bool(card.get("is_spotlight", False))
        accent_hex = str(card.get("accent", theme_primary if is_spot else muted_acc))
        spot_wash = _blend_hex(accent_hex, theme_card_bg, 0.14 if is_dark_theme else 0.06)

        if style_norm == "clean_card":
            card_fill = str(card.get("bg", spot_wash if is_spot else theme_card_bg))
            card_border = _blend_hex(accent_hex, theme_border, 0.45 if is_dark_theme else 0.35) if is_spot else theme_border
            base_rect = _add_flat_shape(
                slide,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(cur_x), Inches(top), Inches(cw), Inches(actual_card_h),
            )
            base_rect.adjustments[0] = 0.03
            base_rect.fill.solid()
            base_rect.fill.fore_color.rgb = hex_to_rgb_color(card_fill)
            base_rect.line.color.rgb = hex_to_rgb_color(card_border)
            base_rect.line.width = Pt(1.25 if is_spot else 1.0)

            top_strip = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(cur_x + 0.14), Inches(top + 0.01), Inches(max(0.4, cw - 0.28)), Inches(0.06 if is_spot else 0.035),
            )
            top_strip.fill.solid()
            top_strip.fill.fore_color.rgb = hex_to_rgb_color(accent_hex if is_spot else muted_bar)
            top_strip.line.fill.background()

        elif style_norm == "minimal_column":
            num_str = str(col_info.get("num_str", "")).strip()
            num_color = _blend_hex(accent_hex, theme_canvas, 0.45) if is_spot else muted_bar
            if num_str:
                nb = slide.shapes.add_textbox(
                    Inches(cur_x + pad_x), Inches(top), Inches(inner_w), Inches(0.46)
                )
                tf_n = nb.text_frame
                tf_n.word_wrap = False
                tf_n.vertical_anchor = MSO_ANCHOR.TOP
                tf_n.margin_left = Inches(0.0)
                tf_n.margin_top = Inches(0.0)
                pn = tf_n.paragraphs[0]
                pn.alignment = PP_ALIGN.LEFT
                _populate_paragraph_runs(pn, num_str, 30.0, num_color, bold=True)

            short_bar = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(cur_x + pad_x), Inches(top + 0.48), Inches(0.68 if is_spot else 0.45), Inches(0.055 if is_spot else 0.035),
            )
            short_bar.fill.solid()
            short_bar.fill.fore_color.rgb = hex_to_rgb_color(accent_hex if is_spot else muted_acc)
            short_bar.line.fill.background()

            if idx > 0:
                div_x = cur_x - eff_gap / 2.0
                v_div = _add_flat_shape(
                    slide,
                    MSO_SHAPE.RECTANGLE,
                    Inches(div_x), Inches(top + 0.08), Inches(0.012), Inches(max(1.2, actual_card_h - 0.16)),
                )
                v_div.fill.solid()
                v_div.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
                v_div.line.fill.background()

        else:  # borderless_centerline
            if is_spot:
                wash = _add_flat_shape(
                    slide,
                    MSO_SHAPE.RECTANGLE,
                    Inches(cur_x), Inches(top), Inches(cw), Inches(actual_card_h),
                )
                wash.fill.solid()
                wash.fill.fore_color.rgb = hex_to_rgb_color(_blend_hex(accent_hex, theme_canvas, 0.14 if is_dark_theme else 0.055))
                wash.line.fill.background()

            top_bar = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(cur_x + pad_x), Inches(top + 0.01), Inches(1.20 if is_spot else 0.72), Inches(0.06 if is_spot else 0.04),
            )
            top_bar.fill.solid()
            top_bar.fill.fore_color.rgb = hex_to_rgb_color(accent_hex if is_spot else muted_acc)
            top_bar.line.fill.background()

            if idx > 0:
                div_x = cur_x - eff_gap / 2.0
                v_div = _add_flat_shape(
                    slide,
                    MSO_SHAPE.RECTANGLE,
                    Inches(div_x), Inches(top + 0.04), Inches(0.018), Inches(max(1.2, actual_card_h - 0.08)),
                )
                v_div.fill.solid()
                v_div.fill.fore_color.rgb = hex_to_rgb_color(div_strong)
                v_div.line.fill.background()

        # 3-tier header (TOP aligned; deep ink title even on spotlight to prevent 5x blue noise)
        _render_three_tier_header(
            slide,
            x=cur_x + pad_x,
            y=top + top_inset,
            w=inner_w,
            h=header_h + 0.04,
            kicker=str(col_info["kicker"]),
            title=str(col_info["title"]),
            subtitle=str(col_info["subtitle"]),
            kicker_pt=kicker_pt,
            title_pt=resolved_title_pt,
            sub_pt=sub_pt,
            kicker_hex=accent_hex if is_spot else theme_ink_muted,
            title_hex=theme_ink_pri,
            sub_hex=theme_ink_muted,
        )

        # Clean neutral hairline under header
        hdr_rule = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(cur_x + pad_x), Inches(rule_y), Inches(inner_w), Inches(0.012),
        )
        hdr_rule.fill.solid()
        hdr_rule.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
        hdr_rule.line.fill.background()

        # TOP-aligned natural flow stacking (ZERO slot_h equal split, ZERO ghost separators!)
        r_list = col_info["rows"]  # type: ignore[assignment]
        if r_list:
            raw_sum_h = sum(r[2] for r in r_list)
            if len(r_list) > 1:
                eff_item_gap = min(base_item_gap, max(0.08, (avail_body_h - raw_sum_h) / (len(r_list) - 1)))
            else:
                eff_item_gap = 0.0

            cur_y = body_top
            card_bot_limit = top + actual_card_h - 0.08
            for r_i, (lead_s, body_s, item_h) in enumerate(r_list):
                if cur_y >= card_bot_limit - 0.16:
                    break
                if r_i > 0:
                    sep_y = round(cur_y - eff_item_gap * 0.52, 3)
                    sep = _add_flat_shape(
                        slide,
                        MSO_SHAPE.RECTANGLE,
                        Inches(cur_x + pad_x), Inches(sep_y), Inches(inner_w), Inches(0.008),
                    )
                    sep.fill.solid()
                    sep.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
                    sep.line.fill.background()

                rem_h = max(0.20, card_bot_limit - cur_y)
                box_h = round(min(rem_h, item_h + 0.02), 3)
                _render_lead_body_box(
                    slide,
                    x=cur_x + pad_x,
                    y=cur_y,
                    w=inner_w,
                    h=box_h,
                    lead=lead_s,
                    body=body_s,
                    lead_pt=lead_pt,
                    body_pt=resolved_pt,
                    lead_hex=theme_ink_pri,
                    body_hex=theme_ink_body,
                    bold_color_hex=theme_ink_pri,
                    line_spacing=ls,
                )
                cur_y = round(cur_y + box_h + eff_item_gap, 3)

        coords.append((round(cur_x, 3), round(top, 3), round(cw, 3), round(actual_card_h, 3)))
        cur_x += cw + eff_gap

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y(coords, dy_in)


def draw_editorial_split_rows_s8(
    slide,
    rows_spec: Sequence[dict[str, object]],
    left_ratio: float = 0.28,
    spotlight_idx: int | None = None,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    body_font_pt: float | None = None,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> list[tuple[float, float, float, float]]:
    """
    [F2-B / S8] Render Swiss Editorial Grid "Left Label / Right Expand" Horizontal Rows (ZERO card boxes):
    - Crisp horizontal hairlines separate 2–4 rows.
    - Left column (`left_ratio`, default 28%): index numeral + bold category title + optional subtitle.
    - Right column (`1 - left_ratio`, default 72%): expanded narrative or Lead/Body points flowing TOP-aligned.
    - Spotlight row gets a single left accent bar + ultra-subtle borderless wash.
    """
    n_rows = len(rows_spec)
    if n_rows == 0:
        return []

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.26)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, _min_floor, resolved_pt, typo, sp = _resolve_engine_context(
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

    ratio = max(0.20, min(0.42, float(left_ratio)))
    gutter = 0.36
    left_w = round((total_width - gutter) * ratio, 3)
    right_w = round(total_width - gutter - left_w, 3)

    title_pt = _round_half_pt(resolved_pt + 2.5)
    lead_pt = float(typo["lead"])
    kicker_pt = float(typo["kicker"])
    sub_pt = float(typo["subtitle"])
    ls = float(sp.get("line_spacing", 1.30))

    # Measure natural Content-Driven height for each row
    row_plans: list[dict[str, object]] = []
    for idx, row in enumerate(rows_spec):
        label_s = _first_non_empty_str(row, "label")
        if label_s:
            title_s = label_s
            right_lead = _first_non_empty_str(row, "lead", "heading", "title")
        else:
            title_s = _first_non_empty_str(row, "title", "heading", "name", "category")
            right_lead = _first_non_empty_str(row, "lead", "heading")
            if right_lead == title_s:
                right_lead = ""

        has_explicit_num = isinstance(row, dict) and any(
            k in row and row.get(k) is not None for k in ("kicker", "num", "badge", "step", "index")
        )
        if has_explicit_num:
            num_s = _first_non_empty_str(row, "kicker", "num", "badge", "step", "index")
        else:
            num_s = "" if _LEADING_INDEX_PREFIX_RE.match(title_s) else f"{idx + 1:02d}"

        sub_s = _first_non_empty_str(row, "subtitle", "sub")
        left_h = _measure_three_tier_header(num_s, title_s, sub_s, left_w - 0.16, kicker_pt, title_pt, sub_pt)

        raw_pairs = _extract_lead_body_items(row, extra_lead=right_lead)
        parsed_pts: list[tuple[str, str, float]] = []
        for ld, bd in raw_pairs:
            ih = _measure_lead_body_item_height(ld, bd, right_w - 0.12, lead_pt, resolved_pt, line_spacing=ls)
            parsed_pts.append((ld, bd, ih))

        pt_gap = 0.14
        right_h = sum(p[2] for p in parsed_pts) + pt_gap * max(0, len(parsed_pts) - 1) if parsed_pts else 0.36
        content_h = max(left_h, right_h)
        row_plans.append({
            "row": row,
            "num": num_s,
            "title": title_s,
            "subtitle": sub_s,
            "points": parsed_pts,
            "pt_gap": pt_gap,
            "left_h": left_h,
            "content_h": content_h,
        })

    pad_y = 0.18
    raw_total_h = sum(float(p["content_h"]) + 2 * pad_y for p in row_plans)
    exp_factor = _calc_zone2_expansion_factor(avail_h, raw_total_h)
    if exp_factor > 1.0:
        pad_y = round(0.18 * exp_factor, 3)
        for p in row_plans:
            pts_p: list[tuple[str, str, float]] = p["points"]  # type: ignore[assignment]
            new_pt_gap = round(0.14 * exp_factor, 3)
            p["pt_gap"] = new_pt_gap
            r_h = sum(it[2] for it in pts_p) + new_pt_gap * max(0, len(pts_p) - 1) if pts_p else 0.36
            p["content_h"] = max(float(p["left_h"]), r_h)
        raw_total_h = sum(float(p["content_h"]) + 2 * pad_y for p in row_plans)

    budget_h = max(resolved_h, avail_h) if exp_factor > 1.0 else resolved_h
    if raw_total_h > budget_h:
        pad_y = max(0.06, (budget_h - sum(float(p["content_h"]) for p in row_plans)) / (2.0 * n_rows))
        raw_total_h = sum(float(p["content_h"]) + 2 * pad_y for p in row_plans)

    # Extra breathing room gently distributed up to a clean cap (never bloated); scale proportionally if taller than budget_h
    extra_cap = round(0.18 * exp_factor, 3) if exp_factor > 1.0 else 0.18
    extra_per_row = min(extra_cap, max(0.0, (budget_h - raw_total_h) / max(1, n_rows)))
    row_scale = (budget_h / raw_total_h) if raw_total_h > budget_h and raw_total_h > 0 else 1.0

    coords: list[tuple[float, float, float, float]] = []
    cur_y = top
    for idx, plan in enumerate(row_plans):
        row_dict: dict[str, object] = plan["row"]  # type: ignore[assignment]
        is_spot = (spotlight_idx == idx) if spotlight_idx is not None else bool(row_dict.get("is_spotlight", False))
        acc_hex = str(row_dict.get("accent", theme_pri if is_spot else muted_acc))

        target_rh = (float(plan["content_h"]) + 2 * pad_y) * row_scale + extra_per_row
        rem_total = max(0.40, (top + budget_h) - cur_y)
        rh = round(min(rem_total, max(0.45, target_rh)), 3)

        # Top hairline divider
        top_line = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(left), Inches(cur_y), Inches(total_width), Inches(0.015 if idx == 0 else 0.010),
        )
        top_line.fill.solid()
        top_line.fill.fore_color.rgb = hex_to_rgb_color(div_strong if idx == 0 else div_subtle)
        top_line.line.fill.background()

        if is_spot:
            wash = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(left), Inches(cur_y + 0.015), Inches(total_width), Inches(max(0.40, rh - 0.015)),
            )
            wash.fill.solid()
            wash.fill.fore_color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_canvas, 0.14 if is_dark_theme else 0.07))
            wash.line.fill.background()

            bar = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(left), Inches(cur_y + 0.08), Inches(0.06), Inches(max(0.35, rh - 0.16)),
            )
            bar.fill.solid()
            bar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex)
            bar.line.fill.background()

        inner_y = round(cur_y + pad_y, 3)
        inner_h = max(0.36, rh - 2 * pad_y)
        _render_three_tier_header(
            slide,
            x=left + (0.16 if is_spot else 0.04),
            y=inner_y,
            w=max(0.8, left_w - (0.16 if is_spot else 0.04)),
            h=inner_h,
            kicker=str(plan["num"]),
            title=str(plan["title"]),
            subtitle=str(plan["subtitle"]),
            kicker_pt=kicker_pt,
            title_pt=title_pt,
            sub_pt=sub_pt,
            kicker_hex=acc_hex if is_spot else ink_muted,
            title_hex=ink_pri,
            sub_hex=ink_muted,
        )

        # Right expanded block (TOP natural flow, with compact single-textbox packing when tight)
        pts_list: list[tuple[str, str, float]] = plan["points"]  # type: ignore[assignment]
        rx = left + left_w + gutter
        ry = inner_y
        pt_gap = float(plan["pt_gap"])
        if pts_list:
            inner_right_h = max(0.32, (cur_y + rh - 0.06) - ry)
            raw_pts_sum = sum(p[2] for p in pts_list)
            min_gap_tot = 0.05 * max(0, len(pts_list) - 1)
            if len(pts_list) > 1 and (raw_pts_sum + min_gap_tot) > inner_right_h:
                _render_compact_lead_body_stack(
                    slide,
                    x=rx,
                    y=ry,
                    w=right_w - 0.08,
                    h=inner_right_h,
                    items=[(ld, bd) for ld, bd, _ih in pts_list],
                    lead_pt=lead_pt,
                    body_pt=resolved_pt,
                    lead_hex=ink_pri,
                    body_hex=ink_body,
                    bold_color_hex=ink_pri,
                    line_spacing=min(ls, 1.16),
                    para_space_after_pt=2.0,
                )
            else:
                eff_pt_gap = (
                    min(pt_gap, max(0.05, (inner_right_h - raw_pts_sum) / max(1, len(pts_list) - 1)))
                    if len(pts_list) > 1
                    else 0.0
                )
                for ld, bd, ih in pts_list:
                    rem_h = max(0.26, (cur_y + rh - 0.06) - ry)
                    bh = round(rem_h if len(pts_list) == 1 else min(rem_h, ih + 0.02), 3)
                    _render_lead_body_box(
                        slide,
                        x=rx,
                        y=ry,
                        w=right_w - 0.08,
                        h=bh,
                        lead=ld,
                        body=bd,
                        lead_pt=lead_pt,
                        body_pt=resolved_pt,
                        lead_hex=ink_pri,
                        body_hex=ink_body,
                        bold_color_hex=ink_pri,
                        line_spacing=ls,
                    )
                    ry = round(ry + bh + eff_pt_gap, 3)

        coords.append((round(left, 3), round(cur_y, 3), round(total_width, 3), round(rh, 3)))
        cur_y = round(cur_y + rh, 3)

    # Closing bottom hairline
    bot_line = _add_flat_shape(
        slide,
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(min(top + budget_h, cur_y)), Inches(total_width), Inches(0.015),
    )
    bot_line.fill.solid()
    bot_line.fill.fore_color.rgb = hex_to_rgb_color(div_strong)
    bot_line.line.fill.background()

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y(coords, dy_in)


def _render_bento_tile(
    slide,
    block: dict[str, object],
    x: float,
    y: float,
    w: float,
    h: float,
    is_spot: bool,
    dt: dict[str, str],
    typo: dict[str, float],
    body_pt: float,
    ls: float,
    item_gap_scale: float = 1.0,
) -> tuple[float, float, float, float]:
    """Internal SSOT helper to render a single Bento Grid tile (`F2-C / S9`)."""
    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_pri = pal["primary_accent"]
    theme_border = pal["border_card"]
    theme_card_bg = pal["bg_card"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    ink_muted = pal["ink_muted"]
    is_dark = bool(block.get("dark", False))

    acc_hex = str(block.get("accent", dt.get("bookend_accent", "#38BDF8") if is_dark else theme_pri))
    if is_dark:
        fill_hex = str(block.get("bg", dt.get("bookend_dark_bg", "#0F172A")))
        border_hex = acc_hex
        title_hex = "#F8FAFC"
        kicker_hex = acc_hex
        sub_hex = "#CBD5E1"
        lead_hex = "#F8FAFC"
        body_hex = "#E2E8F0"
        bold_hex = "#FFFFFF"
    else:
        fill_hex = str(block.get("bg", _blend_hex(acc_hex, theme_card_bg, 0.14 if is_dark_theme else 0.065) if is_spot else theme_card_bg))
        border_hex = _blend_hex(acc_hex, theme_border, 0.45 if is_dark_theme else 0.35) if is_spot else theme_border
        title_hex = ink_pri
        kicker_hex = acc_hex if is_spot else ink_muted
        sub_hex = ink_muted
        lead_hex = ink_pri
        body_hex = ink_body
        bold_hex = ink_pri

    box = _add_flat_shape(
        slide,
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h),
    )
    box.adjustments[0] = 0.035
    box.fill.solid()
    box.fill.fore_color.rgb = hex_to_rgb_color(fill_hex)
    box.line.color.rgb = hex_to_rgb_color(border_hex)
    box.line.width = Pt(1.3 if (is_spot or is_dark) else 1.0)

    if is_spot or is_dark:
        bar = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(x + 0.16), Inches(y + 0.01), Inches(max(0.5, w - 0.32)), Inches(0.06),
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex)
        bar.line.fill.background()

    pad_x = 0.22
    inner_w = max(0.60, w - 2.0 * pad_x)
    cur_y = round(y + (0.18 if (is_spot or is_dark) else 0.14), 3)

    kicker = _first_non_empty_str(block, "kicker", "badge", "num", "step")
    title = _first_non_empty_str(block, "title", "heading", "label", "name")
    subtitle = _first_non_empty_str(block, "subtitle", "sub")
    kicker_pt = float(typo["kicker"])
    title_pt = float(typo["card_title"])
    sub_pt = float(typo["subtitle"])
    lead_pt = float(typo["lead"])

    stat_val = _first_non_empty_str(block, "stat", "value", "metric")
    block_lead = _first_non_empty_str(block, "lead")
    if block_lead == title:
        block_lead = ""
    raw_pairs = _extract_lead_body_items(block, extra_lead=block_lead)

    parsed_items: list[tuple[str, str, float]] = []
    for ld, bd in raw_pairs:
        ih = _measure_lead_body_item_height(ld, bd, inner_w, lead_pt, body_pt, line_spacing=ls)
        parsed_items.append((ld, bd, ih))

    if kicker or title or subtitle:
        hdr_h = _measure_three_tier_header(kicker, title, subtitle, inner_w, kicker_pt, title_pt, sub_pt)
        est_items_h = (
            sum(it[2] for it in parsed_items) + 0.05 * max(0, len(parsed_items) - 1)
            if parsed_items
            else 0.0
        )
        # Compact 3-tier header into 2 lines (`Kicker · Subtitle` + `Title`) when tile vertical budget is tight
        if kicker and title and subtitle and parsed_items and (cur_y + hdr_h + 0.06 + est_items_h) > (y + h - 0.06):
            kicker = f"{kicker} · {subtitle}"
            subtitle = ""
            hdr_h = _measure_three_tier_header(kicker, title, subtitle, inner_w, kicker_pt, title_pt, sub_pt)
        hdr_box_h = round(min(h * 0.58, hdr_h + 0.02), 3)
        hdr_gap = 0.06 if (parsed_items and (cur_y + hdr_box_h + 0.14 + est_items_h) > (y + h - 0.08)) else 0.14
        _render_three_tier_header(
            slide, x + pad_x, cur_y, inner_w, hdr_box_h,
            kicker, title, subtitle, kicker_pt, title_pt, sub_pt,
            kicker_hex, title_hex, sub_hex,
        )
        cur_y = round(cur_y + hdr_box_h + hdr_gap, 3)

    if stat_val:
        stat_pt = max(24.0, _round_half_pt(body_pt * 2.1))
        m_st = measure_text_layout(stat_val, inner_w, stat_pt, bold=True, line_spacing=1.12)
        st_h = round(max(0.42, float(m_st["safe_height_in"])), 3)
        st_tb = slide.shapes.add_textbox(Inches(x + pad_x), Inches(cur_y), Inches(inner_w), Inches(st_h))
        tf_st = st_tb.text_frame
        tf_st.word_wrap = True
        tf_st.vertical_anchor = MSO_ANCHOR.TOP
        tf_st.margin_left = Inches(0.02)
        tf_st.margin_top = Inches(0.0)
        p_st = tf_st.paragraphs[0]
        p_st.alignment = PP_ALIGN.LEFT
        _populate_paragraph_runs(p_st, stat_val, stat_pt, acc_hex, bold=True)
        cur_y = round(cur_y + st_h + 0.08, 3)

    if parsed_items:
        avail_h = max(0.32, (y + h - 0.06) - cur_y)
        raw_sum = sum(it[2] for it in parsed_items)
        min_gap_total = 0.05 * max(0, len(parsed_items) - 1)
        if len(parsed_items) > 1 and (raw_sum + min_gap_total) > avail_h:
            _render_compact_lead_body_stack(
                slide,
                x=x + pad_x,
                y=cur_y,
                w=inner_w,
                h=avail_h,
                items=[(ld, bd) for ld, bd, _ih in parsed_items],
                lead_pt=lead_pt,
                body_pt=body_pt,
                lead_hex=lead_hex,
                body_hex=body_hex,
                bold_color_hex=bold_hex,
                line_spacing=min(ls, 1.15),
                para_space_after_pt=2.0,
            )
        else:
            max_tile_gap = round(0.18 * max(1.0, float(item_gap_scale)), 3)
            item_gap = (
                min(max_tile_gap, max(0.05, (avail_h - raw_sum) / max(1, len(parsed_items) - 1)))
                if len(parsed_items) > 1
                else 0.0
            )
            for ld, bd, ih in parsed_items:
                rem_h = max(0.26, (y + h - 0.06) - cur_y)
                bh = round(min(rem_h, ih + 0.02), 3)
                _render_lead_body_box(
                    slide, x + pad_x, cur_y, inner_w, bh,
                    ld, bd, lead_pt, body_pt, lead_hex, body_hex, bold_hex, line_spacing=ls,
                )
                cur_y = round(cur_y + bh + item_gap, 3)

    return (round(x, 3), round(y, 3), round(w, 3), round(h, 3))


def draw_bento_grid_slide(
    slide,
    primary_block: dict[str, object],
    secondary_blocks: Sequence[dict[str, object]],
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
    [F2-C / S9] Render Asymmetric Bento Grid ("1 Primary Anchor + 2~3 Supporting Blocks"):
    - Left `45%` primary full-height block (`idx=0`) + Right `55%` stacked or 1+2 asymmetric secondary blocks.
    - At `target_body_pt >= 16.0pt`, automatically avoids narrow sub-columns (stacks secondary blocks wide) to prevent Pitfall 1.
    Returns list of bounding rects `[primary_rect, secondary_rect_1, ...]`.
    """
    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.60)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, _min_floor, resolved_pt, typo, sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.0
    )
    ls = float(sp.get("line_spacing", 1.30))
    exp_factor = _calc_zone2_expansion_factor(avail_h, resolved_h)
    gap = round(0.24 * exp_factor, 3) if exp_factor > 1.0 else 0.24
    grid_h = (
        round(min(avail_h, resolved_h * min(1.25, exp_factor)), 3)
        if (exp_factor > 1.0 and height is None)
        else resolved_h
    )
    sec_list = list(secondary_blocks or [])[:3]

    if not sec_list:
        coords = [
            _render_bento_tile(
                slide, primary_block, left, top, total_width, grid_h,
                spotlight_idx == 0, dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
            )
        ]
        dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
        return _shift_coords_y(coords, dy_in)

    pri_ratio = 0.50 if len(sec_list) == 1 else (0.45 if len(sec_list) == 2 else 0.42)
    pri_w = round((total_width - gap) * pri_ratio, 3)
    sec_x = round(left + pri_w + gap, 3)
    sec_w = round(total_width - pri_w - gap, 3)

    coords: list[tuple[float, float, float, float]] = []
    coords.append(
        _render_bento_tile(
            slide, primary_block, left, top, pri_w, grid_h,
            spotlight_idx == 0, dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
        )
    )

    n_sec = len(sec_list)
    if n_sec == 1:
        coords.append(
            _render_bento_tile(
                slide, sec_list[0], sec_x, top, sec_w, grid_h,
                spotlight_idx == 1, dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
            )
        )
    elif n_sec == 2:
        sh = round((grid_h - gap) / 2.0, 3)
        for s_i, blk in enumerate(sec_list):
            sy = round(top + s_i * (sh + gap), 3)
            coords.append(
                _render_bento_tile(
                    slide, blk, sec_x, sy, sec_w, sh,
                    spotlight_idx == (s_i + 1), dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
                )
            )
    else:  # n_sec == 3
        if resolved_pt >= 16.0:
            # High-distance Pitfall 1 protection: keep all 3 secondary tiles wide in a vertical stack
            sh = round((grid_h - 2.0 * gap) / 3.0, 3)
            for s_i, blk in enumerate(sec_list):
                sy = round(top + s_i * (sh + gap), 3)
                coords.append(
                    _render_bento_tile(
                        slide, blk, sec_x, sy, sec_w, sh,
                        spotlight_idx == (s_i + 1), dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
                    )
                )
        else:
            top_h = round((grid_h - gap) * 0.48, 3)
            bot_h = round(grid_h - gap - top_h, 3)
            bot_y = round(top + top_h + gap, 3)
            sub_w = round((sec_w - gap) / 2.0, 3)
            coords.append(
                _render_bento_tile(
                    slide, sec_list[0], sec_x, top, sec_w, top_h,
                    spotlight_idx == 1, dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
                )
            )
            coords.append(
                _render_bento_tile(
                    slide, sec_list[1], sec_x, bot_y, sub_w, bot_h,
                    spotlight_idx == 2, dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
                )
            )
            coords.append(
                _render_bento_tile(
                    slide, sec_list[2], round(sec_x + sub_w + gap, 3), bot_y, sub_w, bot_h,
                    spotlight_idx == 3, dt, typo, resolved_pt, ls, item_gap_scale=exp_factor,
                )
            )

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y(coords, dy_in)


# -------------------------------------------------------------------------
# Family 3 | Flow & Mechanism (`F3-A` S3+S12, `F3-B` S4)
# -------------------------------------------------------------------------

def draw_process_steps_s3(
    slide,
    steps_spec: Sequence[dict[str, object]],
    layout_style: str = "auto",
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    spotlight_idx: int | None = None,
    body_font_pt: float | None = None,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> list[tuple[float, float, float, float]]:
    """
    [F3-A / S3 + S12] Render Sequential Process Track or Staggered Timeline:
    - `layout_style`:
      * `"auto"` (default): selects `"staggered_timeline"` (`S12`) for 4–5 milestones, `"fine_track"` for <=3 steps.
      * `"fine_track"`: de-boxed horizontal hairline track (`01 ─── 02 ─── 03`) with TOP-aligned unboxed columns below.
      * `"staggered_timeline"` (`S12`): central horizontal spine with milestones alternating UP/DOWN for wide, Pitfall-1-safe blocks.
      * `"card_arrow"`: single-layer clean step cards connected by vector `RIGHT_ARROW` shapes (TOP natural flow + Content-Driven Height).
    """
    n_steps = len(steps_spec)
    if n_steps == 0:
        return []

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.20)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    default_body = 13.0 if n_steps <= 3 else 12.5
    dt, min_floor, resolved_pt, typo, sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=default_body
    )
    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_primary = pal["primary_accent"]
    theme_border = pal["border_card"]
    theme_card_bg = pal["bg_card"]
    theme_canvas = pal["bg_canvas"]
    theme_ink_pri = pal["ink_primary"]
    theme_ink_body = pal["ink_body"]
    theme_ink_muted = pal["ink_muted"]
    pill_fg = pal["pill_fg"]
    div_subtle = pal["divider_subtle"]
    div_strong = pal["divider_strong"]
    muted_bar = pal["muted_bar"]
    muted_acc = pal["muted_accent"]
    arrow_muted = pal["arrow_muted"]

    title_pt = float(typo["card_title"])
    lead_pt = float(typo["lead"])
    sub_pt = float(typo["subtitle"])
    kicker_pt = float(typo["kicker"])
    ls = float(sp.get("line_spacing", 1.30))

    if spotlight_idx is None:
        spotlight_idx = n_steps - 1

    eff_style = str(layout_style or "auto").strip().lower()
    if eff_style == "auto":
        eff_style = "staggered_timeline" if n_steps >= 4 else "fine_track"
    if eff_style not in ("fine_track", "staggered_timeline", "card_arrow"):
        eff_style = "fine_track"

    def _parse_step_spec(step: dict[str, object], default_label: str) -> tuple[str, str, str, list[tuple[str, str]]]:
        lbl = _first_non_empty_str(step, "step", "badge", "num", "phase", "date", "kicker", default=default_label)
        t_s = _first_non_empty_str(step, "title", "heading", "label", "name")
        s_s = _first_non_empty_str(step, "subtitle", "sub")
        ld_s = _first_non_empty_str(step, "lead")
        if ld_s == t_s:
            ld_s = ""
        pairs = _extract_lead_body_items(step, extra_lead=ld_s)
        return lbl, t_s, s_s, pairs

    # ---- Variant 1: S12 Staggered Alternating Timeline (4–5 milestones, wide Pitfall-1-safe blocks) ----
    if eff_style == "staggered_timeline":
        # Evenly spaced milestone X centers inside [left, left+total_width]
        edge_pad = total_width * (0.12 if n_steps <= 4 else 0.10)
        if n_steps == 1:
            centers = [left + total_width / 2.0]
        else:
            step_dx = (total_width - 2.0 * edge_pad) / (n_steps - 1)
            centers = [left + edge_pad + i * step_dx for i in range(n_steps)]

        upper_indices = [i for i in range(n_steps) if i % 2 == 0]
        lower_indices = [i for i in range(n_steps) if i % 2 == 1]

        def _compute_row_boxes(indices: list[int]) -> dict[int, tuple[float, float]]:
            if not indices:
                return {}
            min_gap = 0.28
            n_row = len(indices)
            max_slot_w = (total_width - min_gap * max(0, n_row - 1)) / n_row
            box_w = round(min(4.80, max_slot_w), 3)
            out: dict[int, tuple[float, float]] = {}
            for pos_i, idx_val in enumerate(indices):
                ideal_x = centers[idx_val] - box_w / 2.0
                min_x = left + pos_i * (box_w + min_gap)
                max_x = left + total_width - (n_row - pos_i) * box_w - (n_row - 1 - pos_i) * min_gap
                bx = round(max(min_x, min(max_x, ideal_x)), 3)
                out[idx_val] = (bx, box_w)
            return out

        row_x_map = {}
        row_x_map.update(_compute_row_boxes(upper_indices))
        row_x_map.update(_compute_row_boxes(lower_indices))

        # Pre-measure milestone blocks for Direction 2 expansion check
        st_title_pt = _round_half_pt(resolved_pt + 2.0)
        pre_st_data: list[tuple[str, str, str, float, list[tuple[str, str, float]], float]] = []
        max_upper_need = 0.0
        max_lower_need = 0.0
        for idx, step in enumerate(steps_spec):
            _bx, bw = row_x_map[idx]
            inner_w = max(0.80, bw - 0.18)
            step_lbl, step_title, step_sub, raw_pairs = _parse_step_spec(step, f"{idx + 1:02d}")
            hdr_h = _measure_three_tier_header(step_lbl, step_title, step_sub, inner_w, kicker_pt, st_title_pt, sub_pt)
            parsed_pts: list[tuple[str, str, float]] = [
                (ld, bd, _measure_lead_body_item_height(ld, bd, inner_w, lead_pt, resolved_pt, line_spacing=1.26))
                for ld, bd in raw_pairs
            ]
            pts_h = sum(p[2] for p in parsed_pts) + 0.08 * max(0, len(parsed_pts) - 1) if parsed_pts else 0.0
            need_h = max(0.65, hdr_h + (0.06 + pts_h if pts_h else 0.0) + 0.16)
            pre_st_data.append((step_lbl, step_title, step_sub, hdr_h, parsed_pts, need_h))
            if idx % 2 == 0:
                max_upper_need = max(max_upper_need, need_h)
            else:
                max_lower_need = max(max_lower_need, need_h)

        nat_tl_h = max_upper_need + max_lower_need + 2.0 * 0.24 + 0.24
        tl_exp = _calc_zone2_expansion_factor(avail_h, nat_tl_h)
        stem_len = round(0.24 * tl_exp, 3) if tl_exp > 1.0 else 0.24
        st_pt_gap = round(0.08 * tl_exp, 3) if tl_exp > 1.0 else 0.08
        tl_budget_h = max(resolved_h, avail_h) if tl_exp > 1.0 else resolved_h
        half_avail_h = max(1.10, round((tl_budget_h / 2.0) - stem_len - 0.16, 3))
        spine_y = round(top + min(half_avail_h, max_upper_need) + stem_len + 0.12, 3) if tl_exp > 1.0 else round(top + resolved_h * 0.50, 3)
        spine_y = max(round(top + 1.05, 3), min(round(top + tl_budget_h - 1.05, 3), spine_y))

        spine = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(left), Inches(spine_y - 0.015), Inches(total_width - 0.16), Inches(0.03),
        )
        spine.fill.solid()
        spine.fill.fore_color.rgb = hex_to_rgb_color(arrow_muted)
        spine.line.fill.background()

        cap_arr = _add_flat_shape(
            slide,
            MSO_SHAPE.ISOSCELES_TRIANGLE,
            Inches(left + total_width - 0.18), Inches(spine_y - 0.09), Inches(0.18), Inches(0.18),
        )
        cap_arr.rotation = 90.0
        cap_arr.fill.solid()
        cap_arr.fill.fore_color.rgb = hex_to_rgb_color(theme_primary)
        cap_arr.line.fill.background()

        coords: list[tuple[float, float, float, float]] = []

        for idx, step in enumerate(steps_spec):
            is_upper = (idx % 2 == 0)
            is_spot = (idx == spotlight_idx) or bool(step.get("is_spotlight", False))
            acc_hex = str(step.get("accent", theme_primary if is_spot else muted_acc))
            cx = centers[idx]
            bx, bw = row_x_map[idx]

            # Milestone marker node on central spine
            node_d = 0.24 if is_spot else 0.18
            node = _add_flat_shape(
                slide,
                MSO_SHAPE.OVAL,
                Inches(cx - node_d / 2.0), Inches(spine_y - node_d / 2.0), Inches(node_d), Inches(node_d),
            )
            node.fill.solid()
            node.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else theme_card_bg)
            node.line.color.rgb = hex_to_rgb_color(acc_hex if is_spot else muted_acc)
            node.line.width = Pt(2.0 if is_spot else 1.5)

            # Reuse pre-measured text content
            step_lbl, step_title, step_sub, hdr_h, parsed_pts, _need_h = pre_st_data[idx]
            inner_w = max(0.80, bw - 0.18)

            pts_h = sum(p[2] for p in parsed_pts) + st_pt_gap * max(0, len(parsed_pts) - 1) if parsed_pts else 0.0
            blk_h = round(min(half_avail_h, max(0.65, hdr_h + (0.06 + pts_h if pts_h else 0.0) + 0.16)), 3)
            by = round((spine_y - node_d / 2.0 - stem_len - blk_h) if is_upper else (spine_y + node_d / 2.0 + stem_len), 3)
            by = max(top, min(top + tl_budget_h - blk_h, by))

            # Vertical stem joining spine node cleanly to the block's spine-facing anchor rail
            actual_stem_top = (by + blk_h) if is_upper else (spine_y + node_d / 2.0)
            actual_stem_h = max(0.08, ((spine_y - node_d / 2.0) - actual_stem_top) if is_upper else (by - actual_stem_top))
            stem = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(cx - 0.012), Inches(actual_stem_top), Inches(0.024), Inches(actual_stem_h),
            )
            stem.fill.solid()
            stem.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else arrow_muted)
            stem.line.fill.background()

            if is_spot:
                wash = _add_flat_shape(
                    slide,
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    Inches(bx), Inches(by), Inches(bw), Inches(blk_h),
                )
                wash.adjustments[0] = 0.04
                wash.fill.solid()
                wash.fill.fore_color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_canvas, 0.14 if is_dark_theme else 0.07))
                wash.line.fill.background()

            # Horizontal spine-facing T-joint rail anchoring block directly to the stem
            rail_edge_y = (by + blk_h - 0.024) if is_upper else by
            edge_rail = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(bx), Inches(rail_edge_y), Inches(bw), Inches(0.030 if is_spot else 0.018),
            )
            edge_rail.fill.solid()
            edge_rail.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else muted_bar)
            edge_rail.line.fill.background()

            # Crisp left vertical hairline anchoring block text
            lbar = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(bx), Inches(by + 0.04), Inches(0.055 if is_spot else 0.032), Inches(max(0.36, blk_h - 0.08)),
            )
            lbar.fill.solid()
            lbar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else muted_bar)
            lbar.line.fill.background()

            hdr_box_h = round(min(blk_h * 0.62, hdr_h + 0.02), 3)
            _render_three_tier_header(
                slide,
                x=bx + 0.14, y=by + 0.04, w=inner_w, h=hdr_box_h,
                kicker=step_lbl, title=step_title, subtitle=step_sub,
                kicker_pt=kicker_pt, title_pt=st_title_pt, sub_pt=sub_pt,
                kicker_hex=acc_hex if is_spot else theme_ink_muted,
                title_hex=theme_ink_pri, sub_hex=theme_ink_muted,
            )

            cy_pt = round(by + 0.04 + hdr_box_h + 0.04, 3)
            if parsed_pts:
                avail_pt_h = max(0.28, (by + blk_h - 0.04) - cy_pt)
                raw_pts_h = sum(p[2] for p in parsed_pts)
                min_gap_h = 0.05 * max(0, len(parsed_pts) - 1)
                if len(parsed_pts) > 1 and (raw_pts_h + min_gap_h) > avail_pt_h:
                    _render_compact_lead_body_stack(
                        slide,
                        x=bx + 0.14,
                        y=cy_pt,
                        w=inner_w,
                        h=avail_pt_h,
                        items=[(ld, bd) for ld, bd, _ih in parsed_pts],
                        lead_pt=lead_pt,
                        body_pt=resolved_pt,
                        lead_hex=theme_ink_pri,
                        body_hex=theme_ink_body,
                        bold_color_hex=theme_ink_pri,
                        line_spacing=1.16,
                        para_space_after_pt=2.0,
                    )
                else:
                    eff_pt_g = (
                        min(st_pt_gap, max(0.04, (avail_pt_h - raw_pts_h) / max(1, len(parsed_pts) - 1)))
                        if len(parsed_pts) > 1
                        else 0.0
                    )
                    for ld, bd, ih in parsed_pts:
                        rem = max(0.24, (by + blk_h - 0.04) - cy_pt)
                        bh = round(min(rem, ih + 0.02), 3)
                        _render_lead_body_box(
                            slide, bx + 0.14, cy_pt, inner_w, bh,
                            ld, bd, lead_pt, resolved_pt, theme_ink_pri, theme_ink_body, theme_ink_pri, line_spacing=1.26,
                        )
                        cy_pt = round(cy_pt + bh + eff_pt_g, 3)

            coords.append((round(bx, 3), round(by, 3), round(bw, 3), round(blk_h, 3)))

        dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
        return _shift_coords_y(coords, dy_in)

    # ---- Variant 2: De-Boxed Horizontal Fine Track (`01 ─── 02 ─── 03`) ----
    if eff_style == "fine_track":
        col_gap = 0.36 if n_steps <= 3 else 0.24
        col_w = (total_width - col_gap * max(0, n_steps - 1)) / n_steps
        pill_h = max(0.36, round((kicker_pt * 1.35) / 72.0 + 0.14, 3))
        track_y = round(top + pill_h / 2.0, 3)

        # Continuous background horizontal track rail (terminates cleanly inside the last step pill)
        last_pill_x = left + (n_steps - 1) * (col_w + col_gap)
        rail_start_x = left + 0.10
        rail_end_x = last_pill_x + 0.30 if n_steps > 1 else (left + col_w * 0.50)
        rail = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(rail_start_x), Inches(track_y - 0.012), Inches(max(0.5, rail_end_x - rail_start_x)), Inches(0.024),
        )
        rail.fill.solid()
        rail.fill.fore_color.rgb = hex_to_rgb_color(div_strong)
        rail.line.fill.background()

        # Pre-measure headers and rows across all steps
        step_plans: list[dict[str, object]] = []
        max_hdr_h = 0.0
        for idx, step in enumerate(steps_spec):
            inner_w = max(0.55, col_w - 0.16)
            step_label, title_s, sub_s, raw_pairs = _parse_step_spec(step, f"STEP {idx + 1:02d}")
            hdr_h_s = _measure_three_tier_header("", title_s, sub_s, inner_w, kicker_pt, title_pt, sub_pt)
            max_hdr_h = max(max_hdr_h, hdr_h_s)
            parsed_rows: list[tuple[str, str, float]] = []
            for ld, bd in raw_pairs:
                parsed_rows.append((ld, bd, _measure_lead_body_item_height(ld, bd, inner_w, lead_pt, resolved_pt, line_spacing=ls)))
            step_plans.append({
                "step": step,
                "step_label": step_label,
                "title": title_s,
                "subtitle": sub_s,
                "rows": parsed_rows,
                "inner_w": inner_w,
            })

        nat_col_top = round(top + pill_h + 0.22, 3)
        nat_avail_col_h = max(1.2, round(top + resolved_h - nat_col_top, 3))
        hdr_h = round(min(nat_avail_col_h * 0.42, max(0.44, max_hdr_h)), 3)
        base_gap = 0.20
        nat_body_need = 0.0
        for sp_item in step_plans:
            r_l: list[tuple[str, str, float]] = sp_item["rows"]  # type: ignore[assignment]
            if r_l:
                nat_body_need = max(nat_body_need, sum(r[2] for r in r_l) + base_gap * max(0, len(r_l) - 1))
        nat_total_h = (pill_h + 0.22) + (hdr_h + 0.16) + nat_body_need + 0.22
        ft_exp = _calc_zone2_expansion_factor(avail_h, nat_total_h)

        pill_col_gap = round(0.22 * ft_exp, 3) if ft_exp > 1.0 else 0.22
        hdr_body_gap = round(0.16 * ft_exp, 3) if ft_exp > 1.0 else 0.16
        if ft_exp > 1.0:
            base_gap = round(base_gap * ft_exp, 3)
        col_bot_pad = round(0.22 * ft_exp, 3) if ft_exp > 1.0 else 0.22
        col_top = round(top + pill_h + pill_col_gap, 3)
        col_budget_bottom = avail_bottom if ft_exp > 1.0 else (top + resolved_h)
        avail_col_h = max(1.2, round(col_budget_bottom - col_top, 3))
        body_start_y = round(col_top + hdr_h + hdr_body_gap, 3)

        max_body_need = 0.0
        for sp_item in step_plans:
            r_l = sp_item["rows"]  # type: ignore[assignment]
            if r_l:
                max_body_need = max(max_body_need, sum(r[2] for r in r_l) + base_gap * max(0, len(r_l) - 1))
        actual_col_h = round(min(avail_col_h, max(min(avail_col_h, 1.85), (body_start_y - col_top) + max_body_need + col_bot_pad)), 3)

        coords = []
        cur_x = left
        for idx, sp_item in enumerate(step_plans):
            step = sp_item["step"]  # type: ignore[assignment]
            is_spot = (idx == spotlight_idx) or bool(step.get("is_spotlight", False))
            acc_hex = str(step.get("accent", theme_primary if is_spot else muted_acc))
            step_label = str(sp_item["step_label"])
            inner_w = float(sp_item["inner_w"])

            pill_w = min(col_w - 0.10, max(1.10, calc_pill_width(step_label, font_pt=kicker_pt, pad_in=0.28)))
            step_pill = _add_flat_shape(
                slide,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(cur_x), Inches(top), Inches(pill_w), Inches(pill_h),
            )
            step_pill.adjustments[0] = 0.48
            step_pill.fill.solid()
            step_pill.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else theme_card_bg)
            if not is_spot:
                step_pill.line.color.rgb = hex_to_rgb_color(arrow_muted)
                step_pill.line.width = Pt(1.1)
            else:
                step_pill.line.fill.background()
            tf_sp = step_pill.text_frame
            tf_sp.word_wrap = False
            tf_sp.vertical_anchor = MSO_ANCHOR.MIDDLE
            p_sp = tf_sp.paragraphs[0]
            p_sp.alignment = PP_ALIGN.CENTER
            _populate_paragraph_runs(p_sp, step_label, kicker_pt, pill_fg if is_spot else theme_ink_pri, bold=True)

            # Small clean directional chevron on the track between steps
            if idx < n_steps - 1:
                chev_x = cur_x + col_w + col_gap / 2.0 - 0.08
                chev = _add_flat_shape(
                    slide,
                    MSO_SHAPE.ISOSCELES_TRIANGLE,
                    Inches(chev_x), Inches(track_y - 0.08), Inches(0.15), Inches(0.16),
                )
                chev.rotation = 90.0
                chev.fill.solid()
                chev.fill.fore_color.rgb = hex_to_rgb_color(theme_primary if (idx + 1 == spotlight_idx) else arrow_muted)
                chev.line.fill.background()

            # Spotlight column gets a subtle borderless tint wash + single left bar; non-spotlight is 100% unboxed
            if is_spot:
                wash = _add_flat_shape(
                    slide,
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    Inches(cur_x), Inches(col_top), Inches(col_w), Inches(actual_col_h),
                )
                wash.adjustments[0] = 0.03
                wash.fill.solid()
                wash.fill.fore_color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_canvas, 0.14 if is_dark_theme else 0.065))
                wash.line.fill.background()

                lbar = _add_flat_shape(
                    slide,
                    MSO_SHAPE.RECTANGLE,
                    Inches(cur_x), Inches(col_top + 0.08), Inches(0.055), Inches(max(0.6, actual_col_h - 0.16)),
                )
                lbar.fill.solid()
                lbar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex)
                lbar.line.fill.background()

            txt_x = cur_x + (0.14 if is_spot else 0.04)
            _render_three_tier_header(
                slide,
                x=txt_x, y=col_top + 0.08, w=inner_w, h=hdr_h + 0.04,
                kicker="", title=str(sp_item["title"]), subtitle=str(sp_item["subtitle"]),
                kicker_pt=kicker_pt, title_pt=title_pt, sub_pt=sub_pt,
                kicker_hex=acc_hex, title_hex=theme_ink_pri, sub_hex=theme_ink_muted,
            )

            hrule = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(txt_x), Inches(col_top + hdr_h + 0.10), Inches(inner_w), Inches(0.012),
            )
            hrule.fill.solid()
            hrule.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
            hrule.line.fill.background()

            r_list: list[tuple[str, str, float]] = sp_item["rows"]  # type: ignore[assignment]
            if r_list:
                avail_b = max(0.5, (col_top + actual_col_h - 0.10) - body_start_y)
                raw_sum = sum(r[2] for r in r_list)
                eff_g = min(base_gap, max(0.08, (avail_b - raw_sum) / max(1, len(r_list) - 1))) if len(r_list) > 1 else 0.0
                cy_r = body_start_y
                for r_i, (ld, bd, ih) in enumerate(r_list):
                    if r_i > 0:
                        sep = _add_flat_shape(
                            slide,
                            MSO_SHAPE.RECTANGLE,
                            Inches(txt_x), Inches(round(cy_r - eff_g * 0.5, 3)), Inches(inner_w), Inches(0.008),
                        )
                        sep.fill.solid()
                        sep.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
                        sep.line.fill.background()
                    rem = max(0.30, (col_top + actual_col_h - 0.08) - cy_r)
                    bh = round(min(rem, ih + 0.02), 3)
                    _render_lead_body_box(
                        slide, txt_x, cy_r, inner_w, bh,
                        ld, bd, lead_pt, resolved_pt, theme_ink_pri, theme_ink_body, theme_ink_pri, line_spacing=ls,
                    )
                    cy_r = round(cy_r + bh + eff_g, 3)

            coords.append((round(cur_x, 3), round(col_top, 3), round(col_w, 3), round(actual_col_h, 3)))
            cur_x += col_w + col_gap

        dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
        return _shift_coords_y(coords, dy_in)

    # ---- Variant 3: Upgraded Single-Layer Arrow Step Cards (`card_arrow`) ----
    corridor_w = 0.40 if n_steps <= 3 else 0.30
    card_w = (total_width - corridor_w * max(0, n_steps - 1)) / n_steps
    pill_band_h = max(0.36, round((kicker_pt * 1.35) / 72.0 + 0.12, 3))
    nat_card_top = round(top + pill_band_h + 0.12, 3)
    nat_avail_card_h = max(1.5, round(top + resolved_h - nat_card_top, 3))

    inner_w = max(0.50, card_w - 0.32)
    step_plans = []
    max_hdr_h = 0.0
    for idx_s, step in enumerate(steps_spec):
        step_label, title_s, sub_s, raw_pairs = _parse_step_spec(step, f"STEP {idx_s + 1:02d}")
        hdr_h_s = _measure_three_tier_header("", title_s, sub_s, inner_w, kicker_pt, title_pt, sub_pt)
        max_hdr_h = max(max_hdr_h, hdr_h_s)
        parsed_rows = []
        for ld, bd in raw_pairs:
            parsed_rows.append((ld, bd, _measure_lead_body_item_height(ld, bd, inner_w, lead_pt, resolved_pt, line_spacing=ls)))
        step_plans.append({"step": step, "step_label": step_label, "title": title_s, "subtitle": sub_s, "rows": parsed_rows})

    hdr_h = round(min(nat_avail_card_h * 0.42, max(0.46, max_hdr_h)), 3)
    base_gap = 0.18
    nat_body_need = max(
        (sum(r[2] for r in sp_i["rows"]) + base_gap * max(0, len(sp_i["rows"]) - 1) for sp_i in step_plans if sp_i["rows"]),
        default=0.8,
    )
    nat_ca_total = (pill_band_h + 0.12) + (0.14 + hdr_h + 0.14) + nat_body_need + 0.22
    ca_exp = _calc_zone2_expansion_factor(avail_h, nat_ca_total)
    pill_card_gap = round(0.12 * ca_exp, 3) if ca_exp > 1.0 else 0.12
    hdr_rows_gap = round(0.14 * ca_exp, 3) if ca_exp > 1.0 else 0.14
    if ca_exp > 1.0:
        base_gap = round(base_gap * ca_exp, 3)
    card_bot_pad = round(0.22 * ca_exp, 3) if ca_exp > 1.0 else 0.22

    card_top = round(top + pill_band_h + pill_card_gap, 3)
    ca_budget_bottom = avail_bottom if ca_exp > 1.0 else (top + resolved_h)
    avail_card_h = max(1.5, round(ca_budget_bottom - card_top, 3))
    rows_top = round(card_top + 0.14 + hdr_h + hdr_rows_gap, 3)
    max_body_need = max(
        (sum(r[2] for r in sp_i["rows"]) + base_gap * max(0, len(sp_i["rows"]) - 1) for sp_i in step_plans if sp_i["rows"]),
        default=0.8,
    )
    actual_card_h = round(min(avail_card_h, max(min(avail_card_h, 2.10), (rows_top - card_top) + max_body_need + card_bot_pad)), 3)

    coords = []
    cur_x = left
    for idx, sp_item in enumerate(step_plans):
        step = sp_item["step"]  # type: ignore[assignment]
        is_spot = (idx == spotlight_idx) or bool(step.get("is_spotlight", False))
        acc_hex = str(step.get("accent", theme_primary if is_spot else muted_acc))
        step_label = str(sp_item["step_label"])

        pill_w = min(card_w, max(1.15, calc_pill_width(step_label, font_pt=kicker_pt, pad_in=0.26)))
        step_pill = _add_flat_shape(
            slide,
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(cur_x), Inches(top), Inches(pill_w), Inches(pill_band_h),
        )
        step_pill.adjustments[0] = 0.45
        step_pill.fill.solid()
        step_pill.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else (theme_card_bg if is_dark_theme else "#E2E8F0"))
        if is_dark_theme and not is_spot:
            step_pill.line.color.rgb = hex_to_rgb_color(theme_border)
            step_pill.line.width = Pt(1.0)
        else:
            step_pill.line.fill.background()
        tf_sp = step_pill.text_frame
        tf_sp.word_wrap = False
        tf_sp.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_sp = tf_sp.paragraphs[0]
        p_sp.alignment = PP_ALIGN.CENTER
        _populate_paragraph_runs(p_sp, step_label, kicker_pt, pill_fg if is_spot else theme_ink_pri, bold=True)

        card_fill = str(step.get("bg", _blend_hex(acc_hex, theme_card_bg, 0.14 if is_dark_theme else 0.06) if is_spot else theme_card_bg))
        card_box = _add_flat_shape(
            slide,
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(cur_x), Inches(card_top), Inches(card_w), Inches(actual_card_h),
        )
        card_box.adjustments[0] = 0.035
        card_box.fill.solid()
        card_box.fill.fore_color.rgb = hex_to_rgb_color(card_fill)
        card_box.line.color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_border, 0.45 if is_dark_theme else 0.35) if is_spot else theme_border)
        card_box.line.width = Pt(1.3 if is_spot else 1.0)

        top_strip = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(cur_x + 0.14), Inches(card_top + 0.01), Inches(max(0.4, card_w - 0.28)), Inches(0.06 if is_spot else 0.035),
        )
        top_strip.fill.solid()
        top_strip.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else muted_bar)
        top_strip.line.fill.background()

        _render_three_tier_header(
            slide, cur_x + 0.16, card_top + 0.12, inner_w, hdr_h + 0.04,
            "", str(sp_item["title"]), str(sp_item["subtitle"]),
            kicker_pt, title_pt, sub_pt, acc_hex, theme_ink_pri, theme_ink_muted,
        )

        rule = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(cur_x + 0.16), Inches(card_top + 0.14 + hdr_h + 0.04), Inches(inner_w), Inches(0.012),
        )
        rule.fill.solid()
        rule.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
        rule.line.fill.background()

        r_list = sp_item["rows"]  # type: ignore[assignment]
        if r_list:
            avail_b = max(0.5, (card_top + actual_card_h - 0.10) - rows_top)
            raw_sum = sum(r[2] for r in r_list)
            eff_g = min(base_gap, max(0.08, (avail_b - raw_sum) / max(1, len(r_list) - 1))) if len(r_list) > 1 else 0.0
            cy_r = rows_top
            for r_i, (ld, bd, ih) in enumerate(r_list):
                if r_i > 0:
                    sep = _add_flat_shape(
                        slide,
                        MSO_SHAPE.RECTANGLE,
                        Inches(cur_x + 0.16), Inches(round(cy_r - eff_g * 0.5, 3)), Inches(inner_w), Inches(0.008),
                    )
                    sep.fill.solid()
                    sep.fill.fore_color.rgb = hex_to_rgb_color(div_subtle)
                    sep.line.fill.background()
                rem = max(0.24, (card_top + actual_card_h - 0.08) - cy_r)
                bh = round(min(rem, ih + 0.02), 3)
                _render_lead_body_box(
                    slide, cur_x + 0.16, cy_r, inner_w, bh,
                    ld, bd, lead_pt, resolved_pt, theme_ink_pri, theme_ink_body, theme_ink_pri, line_spacing=ls,
                )
                cy_r = round(cy_r + bh + eff_g, 3)

        if idx < n_steps - 1:
            arr_w = min(0.28, corridor_w - 0.08)
            arr_h = 0.22
            arr_x = cur_x + card_w + (corridor_w - arr_w) / 2.0
            arr_y = card_top + actual_card_h / 2.0 - arr_h / 2.0
            arr = _add_flat_shape(
                slide,
                MSO_SHAPE.RIGHT_ARROW,
                Inches(arr_x), Inches(arr_y), Inches(max(0.16, arr_w)), Inches(arr_h),
            )
            arr.fill.solid()
            arr.fill.fore_color.rgb = hex_to_rgb_color(theme_primary if (idx + 1 == spotlight_idx) else arrow_muted)
            arr.line.fill.background()

        coords.append((round(cur_x, 3), round(card_top, 3), round(card_w, 3), round(actual_card_h, 3)))
        cur_x += card_w + corridor_w

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y(coords, dy_in)


def draw_clean_mechanism_s4(
    slide,
    nodes_spec: Sequence[dict[str, object]],
    edges_spec: Sequence[dict[str, object]] | None = None,
    topology: str = "horizontal_chain",
    callouts: Sequence[object] | None = None,
    callout_position: str = "right",
    callout_heading: str | None = None,
    visual_ratio: float = 0.64,
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    body_font_pt: float = 13.0,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> tuple[float, float, float, float]:
    """
    [F3-B / S4] Render Clean Native Vector Mechanism / Loop Diagram (strictly <= 5 concise nodes):
    - Module 1 Fixes (`L1473`): Removes heavy gray backing mat AND eliminates skinny skyscraper nodes.
    - When `horizontal_chain` has 4–5 nodes in a narrow visual area (`nw < 1.95"`), automatically uses a
      clean 2-row serpentine layout (`0 -> 1 -> down -> 2 -> left -> 3`) so nodes keep balanced landscape proportions.
    - Enforces `>= min_font_pt`, left-aligned multi-line node descriptions, and unboxed side callouts (`圖旁不疊卡`).
    """
    n_nodes = len(nodes_spec)
    if n_nodes > 5:
        raise ValueError(
            f"S4 clean mechanism diagram restricts node count to 3~5 (<= 5, got {n_nodes}). "
            "Never cram a full mindmap onto a slide; split into multiple slides instead."
        )

    start_shape_idx = len(slide.shapes)
    resolved_h = _resolve_zone2_height(slide, top, height, 5.26)
    avail_bottom = _resolve_zone2_avail_bottom(slide, top, height)
    avail_h = round(avail_bottom - float(top), 3)
    dt, min_floor, resolved_pt, _typo, _sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.0, caller_default_pt=13.0
    )

    # Pre-estimate callout + diagram height to decide Direction 2 expansion factor cohesively
    norm_callouts = _normalize_callout_items(callouts)
    pos_norm = str(callout_position or "right").strip().lower() if norm_callouts else "header_only"
    ratio_clamped = max(0.45, min(0.82, float(visual_ratio)))
    est_callout_h = 0.0
    if norm_callouts and pos_norm in ("right", "left"):
        est_cw = total_width - 0.36 - (total_width - 0.36) * ratio_clamped
        est_callout_h = _estimate_vertical_callouts_height(norm_callouts, est_cw, callout_heading, resolved_pt, gap_scale=1.0)
    elif norm_callouts and pos_norm in ("top", "bottom"):
        est_callout_h = min(resolved_h * 0.44, _estimate_horizontal_band_height(norm_callouts, total_width, resolved_pt))
    est_base_h = max(est_callout_h, min(resolved_h, 3.60)) if pos_norm in ("right", "left", "header_only") else min(resolved_h, 3.60 + est_callout_h)
    mech_exp = _calc_zone2_expansion_factor(avail_h, est_base_h)

    vx, vy, vw, vh = draw_visual_callout_slide(
        slide,
        image_path=None,
        callout_position=callout_position,
        callouts=callouts,
        visual_ratio=visual_ratio,
        callout_heading=callout_heading,
        body_font_pt=resolved_pt,
        left=left,
        top=top,
        total_width=total_width,
        height=resolved_h,
        tokens=tokens,
        doc_theme_id=doc_theme_id,
        _callout_gap_scale=mech_exp,
    )
    if n_nodes == 0:
        dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
        return _shift_coords_y((vx, vy, vw, vh), dy_in)

    # Measure actual rendered callout span so side-by-side diagram aligns rhythmically with callouts
    actual_callout_h = 0.0
    if norm_callouts and pos_norm in ("right", "left") and len(slide.shapes) > start_shape_idx:
        c_shapes = list(slide.shapes)[start_shape_idx:]
        c_max_b = max((float(shp.top or 0) + float(shp.height or 0)) / 914400.0 for shp in c_shapes)
        actual_callout_h = max(0.0, round(c_max_b - float(top), 3))

    pal = _theme_palette(dt)
    is_dark_theme = bool(pal["is_dark"])
    theme_pri = pal["primary_accent"]
    theme_border = pal["border_card"]
    theme_card_bg = pal["bg_card"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    muted_bar = pal["muted_bar"]
    muted_acc = pal["muted_accent"]
    arrow_muted = pal["arrow_muted"]
    node_pt = max(min_floor, _round_half_pt(resolved_pt - 0.5))
    node_title_pt = _round_half_pt(node_pt + 1.5)

    # Clean direct canvas placement (gray mat backing abolished per Module 1)
    pad_x, pad_y = 0.06, 0.14
    ix, iy = vx + pad_x, vy + pad_y
    iw, ih = max(1.0, vw - 2.0 * pad_x), max(1.0, vh - 2.0 * pad_y)

    def _resolve_node_content(nd: dict[str, object]) -> tuple[str, list[str]]:
        kicker_s = _first_non_empty_str(nd, "kicker", "badge", "num", "step")
        t_s = _first_non_empty_str(nd, "title", "heading", "label", "name")
        if kicker_s and t_s:
            if not t_s.lower().startswith(kicker_s.lower()):
                t_s = f"{kicker_s} {t_s}"
        elif kicker_s and not t_s:
            t_s = kicker_s
        sub_s = _first_non_empty_str(nd, "subtitle", "sub")
        nd_lead = _first_non_empty_str(nd, "lead")
        if nd_lead == t_s:
            nd_lead = ""
        pairs = _extract_lead_body_items(nd, extra_lead=nd_lead, include_subtitle_as_body=False)
        lines: list[str] = []
        if sub_s:
            lines.extend(seg.strip() for seg in sub_s.splitlines() if seg.strip())
        for ld, bd in pairs:
            text_line = f"**{ld}**：{bd}" if (ld and bd) else (ld or bd)
            for seg in text_line.splitlines():
                seg_c = seg.strip()
                if seg_c and seg_c not in lines:
                    lines.append(seg_c)
        return t_s, lines

    def _measure_max_node_h(cand_w: float) -> float:
        tw = max(0.60, cand_w - 0.30)
        mh = 0.0
        for nd in nodes_spec:
            t_s, d_lines = _resolve_node_content(nd)
            h_need = 0.28
            if t_s:
                h_need += float(measure_text_layout(t_s, tw, node_title_pt, bold=True, line_spacing=1.20)["safe_height_in"])
            if d_lines:
                if t_s:
                    h_need += 0.06
                for li, dl in enumerate(d_lines):
                    h_need += float(measure_text_layout(dl, tw, node_pt, bold=False, line_spacing=1.24)["safe_height_in"])
                    if li < len(d_lines) - 1:
                        h_need += 0.03
            mh = max(mh, h_need)
        return round(max(1.15, mh + 0.18), 3)

    node_boxes: list[tuple[float, float, float, float]] = []
    topo = str(topology or "horizontal_chain").strip().lower()
    use_serpentine = False
    gap_mult = mech_exp if mech_exp > 1.0 else 1.0

    def _align_diag_top(tot_diag_h: float) -> float:
        if actual_callout_h > 0.0 and pos_norm in ("right", "left"):
            band_h = min(ih, max(tot_diag_h, actual_callout_h - 0.14))
            return iy + max(0.0, (band_h - tot_diag_h) / 2.0)
        if pos_norm == "header_only":
            # Anchor at `iy` so Stage 2 optical centering places it at exact ~40%/60% (<= 0.90" top buffer)
            return iy
        return iy + max(0.0, (ih - tot_diag_h) / 2.0)

    if topo == "hub_spoke" and n_nodes >= 3:
        hub_w = iw * 0.34
        n_right = n_nodes - 1
        r_gap = round((0.22 if n_right <= 3 else 0.14) * gap_mult, 3)
        rx_start = ix + hub_w + iw * 0.14
        rw = iw - hub_w - iw * 0.14
        r_h = min((ih - r_gap * (n_right - 1)) / n_right, max(1.15, _measure_max_node_h(rw)))
        tot_r_h = n_right * r_h + r_gap * (n_right - 1)
        ry_start = _align_diag_top(tot_r_h)
        hub_h = min(tot_r_h, max(1.55, _measure_max_node_h(hub_w) + 0.20))
        node_boxes.append((ix, ry_start + (tot_r_h - hub_h) / 2.0, hub_w, hub_h))
        for r_i in range(n_right):
            node_boxes.append((rx_start, ry_start + r_i * (r_h + r_gap), rw, r_h))
    elif topo == "cycle_loop" and n_nodes in (3, 4, 5):
        if n_nodes == 3:
            nw = iw * 0.44
            nh = min(ih * 0.42, _measure_max_node_h(nw))
            max_v_gap = max(0.24, ih - 2.0 * nh)
            v_gap = round(min(max_v_gap, max(min(max_v_gap, 0.48 * gap_mult), min(0.76 * gap_mult, 0.90))), 3)
            y0 = _align_diag_top(2.0 * nh + v_gap)
            y1 = y0 + nh + v_gap
            node_boxes = [
                (ix + (iw - nw) / 2.0, y0, nw, nh),
                (ix + iw - nw, y1, nw, nh),
                (ix, y1, nw, nh),
            ]
        elif n_nodes == 4:
            nw = iw * 0.42
            nh = min(ih * 0.42, _measure_max_node_h(nw))
            max_v_gap = max(0.24, ih - 2.0 * nh)
            v_gap = round(min(max_v_gap, max(min(max_v_gap, 0.48 * gap_mult), min(0.76 * gap_mult, 0.90))), 3)
            y0 = _align_diag_top(2.0 * nh + v_gap)
            y1 = y0 + nh + v_gap
            node_boxes = [
                (ix, y0, nw, nh),
                (ix + iw - nw, y0, nw, nh),
                (ix + iw - nw, y1, nw, nh),
                (ix, y1, nw, nh),
            ]
        else:  # n_nodes == 5
            top_corr = 0.30
            top_nw = (iw - 2 * top_corr) / 3.0
            nh = min(ih * 0.42, _measure_max_node_h(top_nw))
            max_v_gap = max(0.24, ih - 2.0 * nh)
            v_gap = round(min(max_v_gap, max(min(max_v_gap, 0.48 * gap_mult), min(0.76 * gap_mult, 0.90))), 3)
            y0 = _align_diag_top(2.0 * nh + v_gap)
            y1 = y0 + nh + v_gap
            bot_nw = iw * 0.43
            node_boxes = [
                (ix, y0, top_nw, nh),
                (ix + top_nw + top_corr, y0, top_nw, nh),
                (ix + 2 * (top_nw + top_corr), y0, top_nw, nh),
                (ix + iw - bot_nw, y1, bot_nw, nh),
                (ix, y1, bot_nw, nh),
            ]
    elif topo == "custom":
        for nd in nodes_spec:
            rx = float(nd.get("rx", 0.05))  # type: ignore[arg-type]
            ry = float(nd.get("ry", 0.15))  # type: ignore[arg-type]
            rw = float(nd.get("rw", 0.28))  # type: ignore[arg-type]
            rh = float(nd.get("rh", 0.55))  # type: ignore[arg-type]
            node_boxes.append((ix + rx * iw, iy + ry * ih, rw * iw, rh * ih))
    else:  # horizontal_chain default (with anti-skyscraper 2-row serpentine auto-switch!)
        corridor = 0.34 if n_nodes <= 3 else 0.26
        cand_nw = (iw - corridor * max(0, n_nodes - 1)) / n_nodes
        if not edges_spec and n_nodes in (4, 5) and cand_nw < 2.05:
            use_serpentine = True
            v_gap = min(0.78, round(0.52 * gap_mult, 3))
            if n_nodes == 4:
                h_gap = 0.44
                nw = (iw - h_gap) / 2.0
                nh = min((ih - v_gap) / 2.0, max(1.45, _measure_max_node_h(nw)))
                tot_h = 2.0 * nh + v_gap
                sy0 = _align_diag_top(tot_h)
                sy1 = sy0 + nh + v_gap
                # Clockwise serpentine: 0 (top-left) -> 1 (top-right) -> 2 (bot-right) -> 3 (bot-left)
                node_boxes = [
                    (ix, sy0, nw, nh),
                    (ix + nw + h_gap, sy0, nw, nh),
                    (ix + nw + h_gap, sy1, nw, nh),
                    (ix, sy1, nw, nh),
                ]
            else:  # 5 nodes: 3 on top, 2 on bottom (0 -> 1 -> 2 -> down -> 3 -> left -> 4)
                h_gap = 0.34
                top_nw = (iw - 2.0 * h_gap) / 3.0
                bot_nw = (iw - h_gap) / 2.0
                nh = min((ih - v_gap) / 2.0, max(1.40, _measure_max_node_h(top_nw)))
                tot_h = 2.0 * nh + v_gap
                sy0 = _align_diag_top(tot_h)
                sy1 = sy0 + nh + v_gap
                node_boxes = [
                    (ix, sy0, top_nw, nh),
                    (ix + top_nw + h_gap, sy0, top_nw, nh),
                    (ix + 2.0 * (top_nw + h_gap), sy0, top_nw, nh),
                    (ix + bot_nw + h_gap, sy1, bot_nw, nh),
                    (ix, sy1, bot_nw, nh),
                ]
        else:
            nw = cand_nw
            nh = min(ih * 0.62, max(1.45, _measure_max_node_h(nw)))
            ny = _align_diag_top(nh)
            for i in range(n_nodes):
                node_boxes.append((ix + i * (nw + corridor), ny, nw, nh))

    for idx, (nd, (nx, ny, nw, nh)) in enumerate(zip(nodes_spec, node_boxes)):
        is_spot = bool(nd.get("is_spotlight", idx == n_nodes - 1))
        acc_hex = str(nd.get("accent", theme_pri if is_spot else muted_acc))
        node_fill = str(nd.get("bg", _blend_hex(acc_hex, theme_card_bg, 0.16 if is_dark_theme else 0.08) if is_spot else theme_card_bg))
        nshape = _add_flat_shape(
            slide,
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(nx), Inches(ny), Inches(nw), Inches(nh),
        )
        nshape.adjustments[0] = 0.05
        nshape.fill.solid()
        nshape.fill.fore_color.rgb = hex_to_rgb_color(node_fill)
        nshape.line.color.rgb = hex_to_rgb_color(_blend_hex(acc_hex, theme_border, 0.45 if is_dark_theme else 0.40) if is_spot else theme_border)
        nshape.line.width = Pt(1.4 if is_spot else 1.1)

        # Single top accent strip inside node (de-noised spotlight)
        nbar = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(nx + 0.14), Inches(ny + 0.01), Inches(max(0.4, nw - 0.28)), Inches(0.055 if is_spot else 0.03),
        )
        nbar.fill.solid()
        nbar.fill.fore_color.rgb = hex_to_rgb_color(acc_hex if is_spot else muted_bar)
        nbar.line.fill.background()

        tb = slide.shapes.add_textbox(
            Inches(nx + 0.14), Inches(ny + 0.12), Inches(max(0.45, nw - 0.28)), Inches(max(0.40, nh - 0.18))
        )
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.02)
        tf.margin_right = Inches(0.02)
        tf.margin_top = Inches(0.01)
        tf.margin_bottom = Inches(0.01)
        tf.vertical_anchor = MSO_ANCHOR.TOP
        nd_title, nd_lines = _resolve_node_content(nd)
        first_used = False
        if nd_title:
            p0 = tf.paragraphs[0]
            first_used = True
            p0.alignment = PP_ALIGN.LEFT
            p0.line_spacing = 1.20
            if nd_lines:
                p0.space_after = Pt(3.5)
            _populate_paragraph_runs(p0, nd_title, node_title_pt, acc_hex if is_spot else ink_pri, bold=True)

        for li, dl in enumerate(nd_lines):
            p_d = tf.add_paragraph() if first_used else tf.paragraphs[0]
            first_used = True
            p_d.alignment = PP_ALIGN.LEFT
            p_d.line_spacing = 1.24
            if li < len(nd_lines) - 1:
                p_d.space_after = Pt(2.0)
            _populate_paragraph_runs(p_d, dl, node_pt, ink_body, bold=False, bold_color_hex=ink_pri)

    def _add_arrow(shp_type, ax_in: float, ay_in: float, aw_in: float, ah_in: float, color_hex: str) -> None:
        arr = _add_flat_shape(slide, shp_type, Inches(ax_in), Inches(ay_in), Inches(aw_in), Inches(ah_in))
        arr.fill.solid()
        arr.fill.fore_color.rgb = hex_to_rgb_color(color_hex)
        arr.line.fill.background()

    # Draw arrows between nodes
    if edges_spec:
        for edge in edges_spec:
            u = int(edge.get("from", 0))  # type: ignore[arg-type]
            v = int(edge.get("to", 0))  # type: ignore[arg-type]
            if not (0 <= u < len(node_boxes) and 0 <= v < len(node_boxes)) or u == v:
                continue
            ux, uy, uw, uh = node_boxes[u]
            tx, ty, tw, th = node_boxes[v]
            ucx, ucy = ux + uw / 2.0, uy + uh / 2.0
            tcx, tcy = tx + tw / 2.0, ty + th / 2.0
            dx, dy = tcx - ucx, tcy - ucy
            e_col = str(edge.get("color", theme_pri))
            if abs(dx) >= abs(dy):
                ax_in = (ux + uw + 0.05) if dx > 0 else (tx + tw + 0.05)
                aw_in = max(0.16, abs(dx) - (uw + tw) / 2.0 - 0.10)
                ay_in = (ucy + tcy) / 2.0 - 0.12
                _add_arrow(MSO_SHAPE.RIGHT_ARROW if dx > 0 else MSO_SHAPE.LEFT_ARROW, ax_in, ay_in, aw_in, 0.24, e_col)
            else:
                ay_in = (uy + uh + 0.05) if dy > 0 else (ty + th + 0.05)
                ah_in = max(0.16, abs(dy) - (uh + th) / 2.0 - 0.10)
                ax_in = (ucx + tcx) / 2.0 - 0.12
                _add_arrow(MSO_SHAPE.DOWN_ARROW if dy > 0 else MSO_SHAPE.UP_ARROW, ax_in, ay_in, 0.24, ah_in, e_col)
    elif use_serpentine:
        for i in range(len(node_boxes) - 1):
            ux, uy, uw, uh = node_boxes[i]
            tx, ty, tw, th = node_boxes[i + 1]
            ucx, ucy = ux + uw / 2.0, uy + uh / 2.0
            tcx, tcy = tx + tw / 2.0, ty + th / 2.0
            dx, dy = tcx - ucx, tcy - ucy
            col = theme_pri if i == len(node_boxes) - 2 else arrow_muted
            if abs(dy) > 0.35:
                ay_in = uy + uh + 0.08
                ah_in = max(0.18, ty - (uy + uh) - 0.16)
                ax_in = min(ux + uw, tx + tw) - min(uw, tw) * 0.5 - 0.12
                _add_arrow(MSO_SHAPE.DOWN_ARROW, ax_in, ay_in, 0.24, ah_in, col)
            elif dx > 0:
                ax_in = ux + uw + 0.04
                aw_in = max(0.18, tx - (ux + uw) - 0.08)
                _add_arrow(MSO_SHAPE.RIGHT_ARROW, ax_in, ucy - 0.11, aw_in, 0.22, col)
            else:
                ax_in = tx + tw + 0.04
                aw_in = max(0.18, ux - (tx + tw) - 0.08)
                _add_arrow(MSO_SHAPE.LEFT_ARROW, ax_in, ucy - 0.11, aw_in, 0.22, col)
    elif topo == "hub_spoke" and n_nodes >= 3:
        # Clean orthogonal tree-bus connector: hub trunk -> vertical spine -> spoke arrows (never floating in mid-air!)
        hx, hy, hw, hh = node_boxes[0]
        spoke_boxes = node_boxes[1:]
        spoke_rx = spoke_boxes[0][0]
        corr_w = max(0.24, spoke_rx - (hx + hw))
        bus_x = hx + hw + corr_w * 0.36
        hub_cy = hy + hh / 2.0
        y_first = spoke_boxes[0][1] + spoke_boxes[0][3] / 2.0
        y_last = spoke_boxes[-1][1] + spoke_boxes[-1][3] / 2.0

        # Horizontal trunk from hub right edge to vertical bus
        trunk = _add_flat_shape(
            slide, MSO_SHAPE.RECTANGLE,
            Inches(hx + hw + 0.02), Inches(hub_cy - 0.015), Inches(max(0.08, bus_x - (hx + hw + 0.02))), Inches(0.03),
        )
        trunk.fill.solid()
        trunk.fill.fore_color.rgb = hex_to_rgb_color(theme_pri)
        trunk.line.fill.background()

        # Vertical spine spanning first spoke center to last spoke center
        v_bus = _add_flat_shape(
            slide, MSO_SHAPE.RECTANGLE,
            Inches(bus_x - 0.015), Inches(y_first - 0.015), Inches(0.03), Inches(max(0.06, y_last - y_first + 0.03)),
        )
        v_bus.fill.solid()
        v_bus.fill.fore_color.rgb = hex_to_rgb_color(theme_pri)
        v_bus.line.fill.background()

        # Horizontal branch arrows from vertical spine cleanly into each spoke
        for rx, ry, _rw, rh in spoke_boxes:
            arr_x = bus_x + 0.015
            arr_w = max(0.18, rx - arr_x - 0.06)
            arr_y = ry + rh / 2.0 - 0.10
            _add_arrow(MSO_SHAPE.RIGHT_ARROW, arr_x, arr_y, arr_w, 0.20, theme_pri)
    elif topo == "cycle_loop" and n_nodes == 3:
        top_b, br_b, bl_b = node_boxes[0], node_boxes[1], node_boxes[2]
        raw_vgap = br_b[1] - (top_b[1] + top_b[3])
        v_arr_h = min(0.46, max(0.20, raw_vgap - 0.16))
        v_arr_y = top_b[1] + top_b[3] + (raw_vgap - v_arr_h) / 2.0
        _add_arrow(MSO_SHAPE.DOWN_ARROW, br_b[0] + br_b[2] * 0.35 - 0.12, v_arr_y, 0.24, v_arr_h, theme_pri)
        _add_arrow(MSO_SHAPE.LEFT_ARROW, bl_b[0] + bl_b[2] + 0.06, bl_b[1] + bl_b[3] / 2.0 - 0.11, max(0.18, br_b[0] - (bl_b[0] + bl_b[2]) - 0.12), 0.22, theme_pri)
        _add_arrow(MSO_SHAPE.UP_ARROW, bl_b[0] + bl_b[2] * 0.65 - 0.12, v_arr_y, 0.24, v_arr_h, theme_pri)
    elif topo == "cycle_loop" and n_nodes == 4:
        for u, v in [(0, 1), (1, 2), (2, 3), (3, 0)]:
            ux, uy, uw, uh = node_boxes[u]
            tx, ty, tw, th = node_boxes[v]
            dx, dy = (tx - ux), (ty - uy)
            if abs(dx) >= abs(dy):
                ax_in = (ux + uw + 0.06) if dx > 0 else (tx + tw + 0.06)
                aw_in = max(0.18, abs(dx) - uw - 0.12)
                ay_in = uy + uh / 2.0 - 0.11
                _add_arrow(MSO_SHAPE.RIGHT_ARROW if dx > 0 else MSO_SHAPE.LEFT_ARROW, ax_in, ay_in, aw_in, 0.22, theme_pri)
            else:
                raw_vgap = abs(dy) - uh
                ah_in = min(0.46, max(0.20, raw_vgap - 0.16))
                top_edge = (uy + uh) if dy > 0 else (ty + th)
                ay_in = top_edge + (raw_vgap - ah_in) / 2.0
                ax_in = ux + uw / 2.0 - 0.12
                _add_arrow(MSO_SHAPE.DOWN_ARROW if dy > 0 else MSO_SHAPE.UP_ARROW, ax_in, ay_in, 0.24, ah_in, theme_pri)
    elif topo == "cycle_loop" and n_nodes == 5:
        for i_top in (0, 1):
            ux, uy, uw, uh = node_boxes[i_top]
            tx = node_boxes[i_top + 1][0]
            _add_arrow(MSO_SHAPE.RIGHT_ARROW, ux + uw + 0.04, uy + uh / 2.0 - 0.11, max(0.18, tx - (ux + uw) - 0.08), 0.22, theme_pri)
        raw_vgap = node_boxes[3][1] - (node_boxes[0][1] + node_boxes[0][3])
        v_arr_h = min(0.46, max(0.20, raw_vgap - 0.16))
        v_arr_y = node_boxes[0][1] + node_boxes[0][3] + (raw_vgap - v_arr_h) / 2.0
        _add_arrow(MSO_SHAPE.DOWN_ARROW, node_boxes[2][0] + node_boxes[2][2] / 2.0 - 0.12, v_arr_y, 0.24, v_arr_h, theme_pri)
        _add_arrow(MSO_SHAPE.LEFT_ARROW, node_boxes[4][0] + node_boxes[4][2] + 0.06, node_boxes[4][1] + node_boxes[4][3] / 2.0 - 0.11, max(0.18, node_boxes[3][0] - (node_boxes[4][0] + node_boxes[4][2]) - 0.12), 0.22, theme_pri)
        _add_arrow(MSO_SHAPE.UP_ARROW, node_boxes[0][0] + node_boxes[0][2] / 2.0 - 0.12, v_arr_y, 0.24, v_arr_h, theme_pri)
    else:
        for i in range(len(node_boxes) - 1):
            ux, uy, uw, uh = node_boxes[i]
            tx, ty, tw, th = node_boxes[i + 1]
            arr_x = ux + uw + 0.05
            arr_w = max(0.18, tx - (ux + uw) - 0.10)
            arr_y = uy + uh / 2.0 - 0.11
            _add_arrow(MSO_SHAPE.RIGHT_ARROW, arr_x, arr_y, arr_w, 0.22, theme_pri if i == len(node_boxes) - 2 else arrow_muted)

    dy_in = _apply_zone2_optical_vertical_balance(slide, start_shape_idx, top, avail_bottom)
    return _shift_coords_y((vx, vy, vw, vh), dy_in)


def draw_hero_stat_slide(
    slide,
    stat_value: str,
    stat_label: str,
    context_points: Sequence[object] = (),
    right_image_path: str | None = None,
    variant: str = "big_number",
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float | None = None,
    stat_pt: float = 54.0,
    body_font_pt: float = 13.5,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> tuple[float, float, float, float]:
    """
    [F1-C / Hero Stat + S14] Render Giant Focus Manifesto Slide (2 variants, ZERO card boxes):
    - `variant="big_number"` (default): Left giant hero KPI number + concise label paired with right image or unboxed callouts.
    - `variant="quote_manifesto"` (`S14`): Full-width high-whitespace typographic thesis / manifesto quote
      (left vertical accent rule, bold statement, attribution/sub-claim, and optional supporting bottom strip).
    """
    resolved_h = _resolve_zone2_height(slide, top, height, 5.26)
    dt, min_floor, resolved_pt, typo, _sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=body_font_pt, default_body_pt=13.5, caller_default_pt=13.5
    )
    pal = _theme_palette(dt)
    theme_pri = pal["primary_accent"]
    ink_pri = pal["ink_primary"]
    ink_muted = pal["ink_muted"]
    div_strong = pal["divider_strong"]
    var_norm = str(variant or "big_number").strip().lower()

    if var_norm == "quote_manifesto":
        items = _normalize_callout_items(context_points)
        quote_str = str(stat_value or "").strip()
        attr_str = str(stat_label or "").strip()

        custom_stat = abs(float(stat_pt) - 54.0) > 1e-6
        quote_pt = min(48.0 if custom_stat else 38.0, max(24.0, float(stat_pt) if custom_stat else _round_half_pt(resolved_pt * 2.15)))
        attr_pt = max(min_floor, _round_half_pt(resolved_pt + 2.0))

        band_h = 0.0
        if items:
            band_h = min(resolved_h * 0.40, _estimate_horizontal_band_height(items, total_width, resolved_pt) + 0.24)
        quote_zone_h = max(1.80, resolved_h - band_h)

        text_x = left + 0.36
        text_w = total_width - 0.56
        min_quote_pt = max(22.0, _round_half_pt(resolved_pt * 1.35))
        q_attr_gap = 0.18
        while True:
            m_q = measure_text_layout(quote_str, text_w, quote_pt, bold=True, line_spacing=1.24)
            q_h = round(max(0.60, float(m_q["safe_height_in"]) + 0.06), 3)
            a_h = 0.0
            if attr_str:
                m_a = measure_text_layout(attr_str, text_w, attr_pt, bold=False, line_spacing=1.24)
                a_h = round(max(0.30, float(m_a["safe_height_in"]) + 0.04), 3)
            tot_q_h = q_h + (q_attr_gap + a_h if attr_str else 0.0)
            if tot_q_h <= quote_zone_h - 0.22 or quote_pt <= min_quote_pt + 1e-6:
                break
            quote_pt = max(min_quote_pt, _round_half_pt(quote_pt - 1.5))

        if tot_q_h > quote_zone_h - 0.18:
            q_attr_gap = 0.10
            tot_q_h = q_h + (q_attr_gap + a_h if attr_str else 0.0)
            if items and tot_q_h > quote_zone_h - 0.16:
                # Rebalance divider slightly downward only if bottom band has spare room
                need_extra = (tot_q_h + 0.18) - quote_zone_h
                min_band = _estimate_horizontal_band_height(items, total_width, resolved_pt) + 0.14
                spare = max(0.0, band_h - min_band)
                shift = min(need_extra, spare)
                quote_zone_h += shift
                band_h -= shift

        q_top = round(top + max(0.06, min(0.14, (quote_zone_h - tot_q_h) * 0.44)) if tot_q_h >= quote_zone_h - 0.30 else top + (quote_zone_h - tot_q_h) * 0.44, 3)

        # Bold architectural left accent bar spanning the quote block
        lbar = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(left + 0.04), Inches(q_top + 0.04), Inches(0.09), Inches(max(0.75, min(quote_zone_h - 0.14, tot_q_h - 0.08))),
        )
        lbar.fill.solid()
        lbar.fill.fore_color.rgb = hex_to_rgb_color(theme_pri)
        lbar.line.fill.background()

        q_tb = slide.shapes.add_textbox(Inches(text_x), Inches(q_top), Inches(text_w), Inches(q_h))
        tf_q = q_tb.text_frame
        tf_q.word_wrap = True
        tf_q.vertical_anchor = MSO_ANCHOR.TOP
        tf_q.margin_left = Inches(0.0)
        tf_q.margin_right = Inches(0.0)
        pq = tf_q.paragraphs[0]
        pq.alignment = PP_ALIGN.LEFT
        pq.line_spacing = 1.24
        _populate_paragraph_runs(pq, quote_str, quote_pt, ink_pri, bold=True, bold_color_hex=theme_pri)

        if attr_str:
            a_top = round(q_top + q_h + q_attr_gap, 3)
            max_a_h = max(0.28, (top + quote_zone_h - 0.10) - a_top) if items else a_h
            a_tb = slide.shapes.add_textbox(Inches(text_x), Inches(a_top), Inches(text_w), Inches(min(a_h, max_a_h)))
            tf_a = a_tb.text_frame
            tf_a.word_wrap = True
            tf_a.vertical_anchor = MSO_ANCHOR.TOP
            tf_a.margin_left = Inches(0.0)
            tf_a.margin_right = Inches(0.0)
            pa = tf_a.paragraphs[0]
            pa.alignment = PP_ALIGN.LEFT
            pa.line_spacing = 1.24
            _populate_paragraph_runs(pa, attr_str, attr_pt, ink_muted, bold=False, bold_color_hex=theme_pri)

        if items:
            div_y = round(max(top + quote_zone_h - 0.06, (q_top + tot_q_h + 0.08) if not attr_str else (a_top + min(a_h, max_a_h) + 0.08)), 3)
            div_y = min(div_y, round(top + resolved_h - 0.85, 3))
            hdiv = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(left), Inches(div_y), Inches(total_width), Inches(0.014),
            )
            hdiv.fill.solid()
            hdiv.fill.fore_color.rgb = hex_to_rgb_color(div_strong)
            hdiv.line.fill.background()
            _render_unboxed_callouts_horizontal(
                slide, items, left, round(div_y + 0.16, 3), total_width, max(0.65, (top + resolved_h) - (div_y + 0.16)), resolved_pt, 0, dt
            )

        return (round(left, 3), round(top, 3), round(total_width, 3), round(resolved_h, 3))

    # Default variant="big_number"
    if isinstance(tokens, dict) and abs(float(stat_pt) - 54.0) < 1e-6:
        resolved_stat_pt = float(typo["hero_stat"])
    else:
        resolved_stat_pt = max(32.0, float(stat_pt))
    lbl_pt = max(min_floor + 2.0, _round_half_pt(resolved_pt + 2.0))

    items = _normalize_callout_items(context_points)
    has_both_img_and_items = (right_image_path is not None) and bool(items)
    has_right = (right_image_path is not None) or bool(items)
    gap = 0.44
    left_w = (total_width * 0.40) if has_right else (total_width * 0.82)
    right_x = left + left_w + gap
    right_w = total_width - left_w - gap

    band_h = 0.0
    if has_both_img_and_items:
        band_h = min(resolved_h * 0.38, _estimate_horizontal_band_height(items, total_width, resolved_pt) + 0.18)
    upper_h = max(1.80, round(resolved_h - (band_h + 0.16 if has_both_img_and_items else 0.0), 3))

    val_str = str(stat_value or "").strip()
    lbl_str = str(stat_label or "").strip()
    m_num = measure_text_layout(val_str, left_w - 0.06, resolved_stat_pt, bold=True, line_spacing=1.14)
    m_lbl = measure_text_layout(lbl_str, left_w - 0.06, lbl_pt, bold=True, line_spacing=1.28)
    req_hero_h = float(m_num["safe_height_in"]) + float(m_lbl["safe_height_in"]) + 0.46
    hero_block_h = min(upper_h, max(min(upper_h, 2.20), req_hero_h))
    # Harmonize vertical anchor: when paired with right unboxed callouts, start both cleanly at top+0.36"
    if has_both_img_and_items:
        hero_y = round(top + max(0.06, (upper_h - hero_block_h) * 0.36), 3)
    elif items and right_image_path is None:
        hero_y = round(top + 0.36, 3)
    else:
        hero_y = round(top + max(0.10, (upper_h - hero_block_h) * 0.40), 3)

    accent_rule = _add_flat_shape(
        slide,
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(hero_y), Inches(1.20), Inches(0.075),
    )
    accent_rule.fill.solid()
    accent_rule.fill.fore_color.rgb = hex_to_rgb_color(theme_pri)
    accent_rule.line.fill.background()

    hero_tb = slide.shapes.add_textbox(
        Inches(left), Inches(hero_y + 0.18), Inches(left_w), Inches(max(1.20, hero_block_h - 0.18))
    )
    tf = hero_tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p_num = tf.paragraphs[0]
    p_num.alignment = PP_ALIGN.LEFT
    p_num.line_spacing = 1.14
    p_num.space_after = Pt(10)
    _populate_paragraph_runs(p_num, val_str, resolved_stat_pt, theme_pri, bold=True)

    if lbl_str:
        p_lbl = tf.add_paragraph()
        p_lbl.alignment = PP_ALIGN.LEFT
        p_lbl.line_spacing = 1.28
        _populate_paragraph_runs(p_lbl, lbl_str, lbl_pt, ink_pri, bold=True)

    if right_image_path is not None:
        draw_visual_callout_slide(
            slide,
            image_path=right_image_path,
            callout_position="header_only",
            left=right_x,
            top=top,
            total_width=right_w,
            height=upper_h,
            tokens=tokens,
            doc_theme_id=doc_theme_id,
        )
        if items:
            div_y = round(top + upper_h + 0.04, 3)
            hdiv = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(left), Inches(div_y), Inches(total_width), Inches(0.014),
            )
            hdiv.fill.solid()
            hdiv.fill.fore_color.rgb = hex_to_rgb_color(div_strong)
            hdiv.line.fill.background()
            _render_unboxed_callouts_horizontal(
                slide,
                items,
                left,
                round(div_y + 0.14, 3),
                total_width,
                max(0.65, (top + resolved_h) - (div_y + 0.14)),
                resolved_pt,
                0,
                dt,
            )
    elif items:
        _render_unboxed_callouts_vertical(
            slide, items, right_x, hero_y, right_w, max(1.60, (top + resolved_h) - hero_y), None, resolved_pt, 0, dt
        )

    return (round(left, 3), round(top, 3), round(left_w, 3), round(resolved_h, 3))
