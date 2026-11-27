"""
pptx_engine/primitives.py
Zone 1/3 headers & footers, Zone 2 optical vertical balance, 3-tier headers, and bookend/divider builders.
Note: `pptx_slide_engine` is the public entry point.
"""

import re
from collections.abc import Sequence
from contextlib import suppress

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from .tokens import (
    _add_flat_shape,
    _blend_hex,
    _get_slide_height_in,
    _populate_paragraph_runs,
    _resolve_engine_context,
    _round_half_pt,
    _theme_palette,
    add_speaker_notes,
    hex_to_rgb_color,
    set_slide_background,
)
from .text_layout import MSJH_LINE_HEIGHT_EM, calc_pill_width, measure_text_layout

_LEAD_BODY_SPLIT_RE = re.compile(r"^\*\*([^*]{1,38})\*\*\s*[：:—–-]\s*(.+)$", re.DOTALL)


_LEADING_INDEX_PREFIX_RE = re.compile(
    r"^\s*(?:"
    r"(?:#|No\.?\s*)\d{1,2}(?:[\.\)、:：\-—–\|｜\s]|$)"
    r"|0\d(?:[\.\)、:：\-—–\|｜\s]|$|(?=[\u4e00-\u9fff]))"
    r"|[1-9]\d?(?:[\.\)、:：\-—–\|｜]|$)"
    r"|[1-9]\d?\s+(?!(?:年|月|日|週|周|天|小時|分鐘|秒|倍|成|折|%|％|個|大|種|款|類|套|萬|億|千|百|元|美元|台幣|人|位|家|間|筆|次|季|歲|pp\b|[xX]\b|[KMB]\b))"
    r"|[\(\（]\d{1,2}[\)\）]"
    r"|(?:Phase|Step|Stage|Part|Tier|Layer|Pillar|Track|Level|Module|Act|Case)\s*(?:\d{1,2}|[IVX]{1,4})(?=$|[\.\)、:：\-—–\|｜\s\u4e00-\u9fff])"
    r"|Q[1-4](?=$|[\.\)、:：\-—–\|｜\s\u4e00-\u9fff])"
    r"|(?:階段|步驟)\s*[\d一二三四五六七八九十]+(?=$|[\.\)、:：\-—–\|｜\s\u4e00-\u9fff])"
    r"|第[一二三四五六七八九十\d]+(?:[步層階段項條部分章節篇點]|[\.\)、:：\-—–\s])"
    r"|[一二三四五六七八九十]+[\.\、]"
    r")",
    re.IGNORECASE,
)


def _first_non_empty_str(mapping: object, *keys: str, default: str = "") -> str:
    """Return the first non-empty scalar string found under `keys` in `mapping`, ignoring None/collections."""
    if not isinstance(mapping, dict):
        return default
    for k in keys:
        if k not in mapping:
            continue
        val = mapping.get(k)
        if val is None or isinstance(val, (bool, list, tuple, dict, set)):
            continue
        s = str(val).strip()
        if s:
            return s
    return default


def _coerce_items_list(val: object) -> list[object]:
    """Coerce a scalar string, dict, or sequence into a clean non-empty list of raw item entries."""
    if val is None or isinstance(val, bool):
        return []
    if isinstance(val, str):
        s = val.strip()
        return [s] if s else []
    if isinstance(val, dict):
        return [val] if val else []
    if isinstance(val, (list, tuple)):
        out: list[object] = []
        for entry in val:
            if entry is None or isinstance(entry, bool):
                continue
            if isinstance(entry, str):
                s = entry.strip()
                if s:
                    out.append(s)
            else:
                out.append(entry)
        return out
    s = str(val).strip()
    return [s] if s else []


def _parse_lead_body_item(item: object) -> tuple[str, str]:
    """
    Parse any structured or legacy row item into `(lead, body)` for independent two-paragraph rendering:
    - dict: `{lead/heading/title/label/name, body/detail/desc/text/content/subtitle/sub, rows/items/points/bullets}`
    - 2-tuple/list: `(lead, body)` (safely flattening nested lists/dicts in `body`)
    - string matching `**Lead**：Body` or `**Lead** — Body`: splits into `(Lead, Body)`
    - plain string: `("", text)`
    """
    if isinstance(item, dict):
        lead = _first_non_empty_str(item, "lead", "heading", "title", "label", "name")
        body_parts: list[str] = []
        body_scalar = _first_non_empty_str(item, "body", "detail", "desc", "text", "content", "subtitle", "sub")
        if body_scalar:
            body_parts.append(body_scalar)
        for list_k in ("rows", "items", "points", "bullets"):
            sub_raw = _coerce_items_list(item.get(list_k))
            if sub_raw:
                for sub_it in sub_raw:
                    s_ld, s_bd = _parse_lead_body_item(sub_it)
                    line = f"**{s_ld}**：{s_bd}" if (s_ld and s_bd) else (s_ld or s_bd)
                    if line and line not in body_parts:
                        body_parts.append(line)
                break
        return (lead, "\n".join(body_parts).strip())
    if isinstance(item, (list, tuple)):
        raw_segs = [seg for seg in item if seg is not None and not isinstance(seg, bool)]
        if len(raw_segs) >= 2:
            head_raw = raw_segs[0]
            head_s = str(head_raw).strip() if not isinstance(head_raw, (list, tuple, dict)) else ""
            tail_lines: list[str] = []
            for seg in raw_segs[1:]:
                if isinstance(seg, (list, tuple)):
                    for sub_it in _coerce_items_list(seg):
                        s_ld, s_bd = _parse_lead_body_item(sub_it)
                        line = f"**{s_ld}**：{s_bd}" if (s_ld and s_bd) else (s_ld or s_bd)
                        if line:
                            tail_lines.append(line)
                elif isinstance(seg, dict):
                    s_ld, s_bd = _parse_lead_body_item(seg)
                    line = f"**{s_ld}**：{s_bd}" if (s_ld and s_bd) else (s_ld or s_bd)
                    if line:
                        tail_lines.append(line)
                else:
                    s_txt = str(seg).strip()
                    if s_txt:
                        tail_lines.append(s_txt)
            if head_s or tail_lines:
                return (head_s, "\n".join(tail_lines))
        elif len(raw_segs) == 1:
            return _parse_lead_body_item(raw_segs[0])
        return ("", "")
    raw = str(item or "").strip()
    if not raw:
        return ("", "")
    m = _LEAD_BODY_SPLIT_RE.match(raw)
    if m:
        return (m.group(1).strip(), m.group(2).strip())
    return ("", raw)


def _extract_lead_body_items(
    mapping: object,
    *,
    extra_lead: str = "",
    include_subtitle_as_body: bool = False,
) -> list[tuple[str, str]]:
    """
    SSOT black-box content extractor for slide spec dicts (`F2-A/B/C`, `F3-A`, `F4-A`, `F5-B`).
    Accepts any intuitive collection key (`rows`/`items`/`points`/`bullets`) and/or narrative key
    (`body`/`desc`/`detail`/`text`/`content`) without silently dropping text, and integrates an
    optional `extra_lead` (Bold +1~1.5pt) cleanly ahead of body items.
    """
    if not isinstance(mapping, dict):
        ld, bd = _parse_lead_body_item(mapping)
        return [(ld, bd)] if (ld or bd) else []

    collection_raw: list[object] = []
    for ck in ("rows", "items", "points", "bullets"):
        if ck in mapping:
            cand = _coerce_items_list(mapping.get(ck))
            if cand:
                collection_raw = cand
                break

    body_raw: list[object] = []
    for bk in ("body", "desc", "detail", "text", "content"):
        if bk in mapping:
            cand = _coerce_items_list(mapping.get(bk))
            if cand:
                body_raw = cand
                break

    if not collection_raw and not body_raw and include_subtitle_as_body:
        for sk in ("subtitle", "sub"):
            if sk in mapping:
                cand = _coerce_items_list(mapping.get(sk))
                if cand:
                    body_raw = cand
                    break

    combined_raw: list[object] = []
    if body_raw and collection_raw:
        combined_raw.extend(body_raw)
        for entry in collection_raw:
            if entry not in combined_raw:
                combined_raw.append(entry)
    elif collection_raw:
        combined_raw = collection_raw
    else:
        combined_raw = body_raw

    parsed: list[tuple[str, str]] = []
    for entry in combined_raw:
        ld, bd = _parse_lead_body_item(entry)
        if ld or bd:
            parsed.append((ld, bd))

    lead_clean = str(extra_lead or "").strip()
    if lead_clean:
        if not parsed:
            parsed = [(lead_clean, "")]
        elif all(not p[0] for p in parsed):
            if len(parsed) == 1:
                parsed = [(lead_clean, parsed[0][1])]
            else:
                parsed = [(lead_clean, "\n".join(p[1] for p in parsed if p[1]))]
        elif not parsed[0][0]:
            parsed[0] = (lead_clean, parsed[0][1])
        elif parsed[0][0] != lead_clean:
            parsed.insert(0, (lead_clean, ""))

    return parsed


def _measure_lead_body_item_height(
    lead: str,
    body: str,
    width_in: float,
    lead_pt: float,
    body_pt: float,
    line_spacing: float = 1.30,
) -> float:
    """Measure exact safe vertical height (inches) for an independent two-paragraph Lead -> Body block."""
    w = max(0.45, float(width_in) - 0.04)
    total_h = 0.0
    if lead:
        m_lead = measure_text_layout(lead, w, lead_pt, bold=True, line_spacing=1.22)
        total_h += float(m_lead["content_height_in"])
    if body:
        m_body = measure_text_layout(body, w, body_pt, bold=False, line_spacing=line_spacing, space_after_pt=3.0)
        body_h = float(m_body["content_height_in"])
        # Borderline wrap guard: reserve extra vertical breathing room only when longest line is within 0.65" (or >86% on narrow cols)
        if float(m_body["max_line_width_in"]) >= max(w * 0.86, w - 0.65):
            body_h += (float(body_pt) * MSJH_LINE_HEIGHT_EM * line_spacing) / 72.0 * 0.65
        total_h += body_h
    if lead and body:
        total_h += 0.05  # Pt(2.5) space_after + safety cushion between Lead and Body
    return round(max(0.28, total_h + 0.08), 4)


def _render_compact_lead_body_stack(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    items: Sequence[tuple[str, str]],
    lead_pt: float,
    body_pt: float,
    lead_hex: str,
    body_hex: str,
    bold_color_hex: str,
    line_spacing: float = 1.16,
    para_space_after_pt: float = 2.0,
) -> None:
    """
    Render multiple `(lead, body)` items inside a single TOP-aligned textbox to avoid per-box margin
    overhead when vertical space in a tile/row/quadrant/milestone is tight.
    """
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(max(0.45, w)), Inches(max(0.24, h)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.01)
    tf.margin_bottom = Inches(0.01)

    compact_ls = min(float(line_spacing), 1.18)
    first_para = True
    n_items = len(items)
    for it_idx, (ld, bd) in enumerate(items):
        if ld:
            p_l = tf.paragraphs[0] if first_para else tf.add_paragraph()
            first_para = False
            p_l.alignment = PP_ALIGN.LEFT
            p_l.line_spacing = min(compact_ls, 1.15)
            if bd or it_idx < n_items - 1:
                p_l.space_after = Pt(min(para_space_after_pt, 2.0))
            _populate_paragraph_runs(p_l, ld, lead_pt, lead_hex, bold=True, bold_color_hex=lead_hex)
        if bd:
            bd_lines = bd.splitlines() or [bd]
            for li, seg in enumerate(bd_lines):
                p_b = tf.paragraphs[0] if first_para else tf.add_paragraph()
                first_para = False
                p_b.alignment = PP_ALIGN.LEFT
                p_b.line_spacing = compact_ls
                if li < len(bd_lines) - 1 or it_idx < n_items - 1:
                    p_b.space_after = Pt(para_space_after_pt)
                _populate_paragraph_runs(p_b, seg, body_pt, body_hex, bold=False, bold_color_hex=bold_color_hex)


def _render_lead_body_box(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    lead: str,
    body: str,
    lead_pt: float,
    body_pt: float,
    lead_hex: str,
    body_hex: str,
    bold_color_hex: str,
    line_spacing: float = 1.30,
) -> None:
    """Render an independent two-paragraph Lead (+1.0~1.5pt Bold #0F172A) -> Body (#334155) block with TOP alignment."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(max(0.45, w)), Inches(max(0.24, h)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.01)
    tf.margin_bottom = Inches(0.01)

    if lead and body:
        p0 = tf.paragraphs[0]
        p0.alignment = PP_ALIGN.LEFT
        p0.line_spacing = 1.22
        p0.space_after = Pt(2.5)
        _populate_paragraph_runs(p0, lead, lead_pt, lead_hex, bold=True, bold_color_hex=lead_hex)
        for seg_i, seg in enumerate(body.splitlines() or [body]):
            p_b = tf.add_paragraph()
            p_b.alignment = PP_ALIGN.LEFT
            p_b.line_spacing = line_spacing
            if seg_i < len(body.splitlines()) - 1:
                p_b.space_after = Pt(3.0)
            _populate_paragraph_runs(p_b, seg, body_pt, body_hex, bold=False, bold_color_hex=bold_color_hex)
    elif lead:
        p0 = tf.paragraphs[0]
        p0.alignment = PP_ALIGN.LEFT
        p0.line_spacing = 1.24
        _populate_paragraph_runs(p0, lead, lead_pt, lead_hex, bold=True, bold_color_hex=lead_hex)
    elif body:
        lines = body.splitlines() or [body]
        for seg_i, seg in enumerate(lines):
            p = tf.paragraphs[0] if seg_i == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.LEFT
            p.line_spacing = line_spacing
            if seg_i < len(lines) - 1:
                p.space_after = Pt(3.0)
            _populate_paragraph_runs(p, seg, body_pt, body_hex, bold=False, bold_color_hex=bold_color_hex)


def _measure_three_tier_header(
    kicker: str,
    title: str,
    subtitle: str,
    width_in: float,
    kicker_pt: float,
    title_pt: float,
    sub_pt: float,
) -> float:
    """Measure exact safe height (inches) for a single-textbox 3-tier header (`Kicker -> Title (+3pt) -> Subtitle`)."""
    w = max(0.45, float(width_in) - 0.04)
    tier_specs: list[tuple[str, float, bool, float, float]] = []
    if kicker:
        tier_specs.append((kicker, kicker_pt, True, 1.18, 2.5))
    if title:
        tier_specs.append((title, title_pt, True, 1.18, 3.0))
    if subtitle:
        tier_specs.append((subtitle, sub_pt, False, 1.22, 0.0))

    total_h = 0.0
    n_tiers = len(tier_specs)
    for t_i, (txt_t, pt_t, bold_t, ls_t, sp_after_t) in enumerate(tier_specs):
        m_t = measure_text_layout(txt_t, w, pt_t, bold=bold_t, line_spacing=ls_t)
        n_lines = max(1, int(m_t["line_count"]))
        step_in = ((pt_t * MSJH_LINE_HEIGHT_EM) / 72.0) * ls_t
        if t_i < n_tiers - 1:
            total_h += n_lines * step_in + (sp_after_t / 72.0)
        else:
            total_h += float(m_t["content_height_in"])
    # Include top/bottom margins (0.02") + >=18% vertical breathing room so Tullis fill stays <= 85%
    return round(max(0.36, total_h * 1.18 + 0.06), 4)


def _render_three_tier_header(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    kicker: str,
    title: str,
    subtitle: str,
    kicker_pt: float,
    title_pt: float,
    sub_pt: float,
    kicker_hex: str,
    title_hex: str,
    sub_hex: str,
) -> None:
    """Render crisp TOP-aligned 3-tier header (`Kicker -> Title (+3pt Bold #0F172A) -> Subtitle (#64748B)`)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(max(0.45, w)), Inches(max(0.30, h)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.01)
    tf.margin_bottom = Inches(0.01)

    first_used = False
    if kicker:
        pk = tf.paragraphs[0]
        first_used = True
        pk.alignment = PP_ALIGN.LEFT
        pk.line_spacing = 1.18
        if title or subtitle:
            pk.space_after = Pt(2.5)
        _populate_paragraph_runs(pk, kicker, kicker_pt, kicker_hex, bold=True, bold_color_hex=kicker_hex)

    if title:
        pt = tf.add_paragraph() if first_used else tf.paragraphs[0]
        first_used = True
        pt.alignment = PP_ALIGN.LEFT
        pt.line_spacing = 1.18
        if subtitle:
            pt.space_after = Pt(3.0)
        _populate_paragraph_runs(pt, title, title_pt, title_hex, bold=True, bold_color_hex=title_hex)

    if subtitle:
        ps = tf.add_paragraph() if first_used else tf.paragraphs[0]
        ps.alignment = PP_ALIGN.LEFT
        ps.line_spacing = 1.22
        _populate_paragraph_runs(ps, subtitle, sub_pt, sub_hex, bold=False, bold_color_hex=title_hex)


def _resolve_zone2_height(slide, top: float, height: float | None, default_h: float) -> float:
    """
    Resolve Zone 2 container height safely:
    - When `height` is None, preserves the standard bottom anchor (`1.36 + default_h`, capped at `slide_h - 0.38"` / `7.12"` on 16:9)
      so larger Zone 1 headers shrink Zone 2 proportionally instead of colliding with Zone 3 or the canvas bottom.
    - Also respects any pre-existing Zone 3 footer shape on `slide`.
    """
    emu_per_in = 914400.0
    slide_h_in = _get_slide_height_in(slide, 7.50)
    z3_y_thresh = round(slide_h_in - 1.30, 3)
    max_bottom = min(round(slide_h_in - 0.38, 3), 1.36 + float(default_h))
    with suppress(AttributeError, TypeError, ValueError):
        for shp in slide.shapes:
            sy = float(shp.top or 0) / emu_per_in
            sw = float(shp.width or 0) / emu_per_in
            if sy >= z3_y_thresh and sw >= 8.0:
                max_bottom = min(max_bottom, sy - 0.14)
    if height is not None:
        return round(min(float(height), max(1.60, max_bottom - float(top) + 0.10)), 3)
    return round(max(1.60, min(float(default_h), max_bottom - float(top))), 3)


def _resolve_zone2_avail_bottom(
    slide,
    top: float,
    height: float | None = None,
    safe_bottom: float | None = None,
) -> float:
    """
    Compute the safe bottom boundary (inches) available for Zone 2 two-stage vertical balancing:
    - Respects any pre-existing Zone 3 footer shape (`sy >= slide_h - 1.30` and `sw >= 8.0`) with >= 0.16" clearance.
    - Without Zone 3, defaults to `slide_h - 0.28"` (`7.22"` on a standard 16:9 `7.50"` canvas).
    - When an explicit `height` is supplied by the caller, never exceeds `top + height` so legacy
      callers that draw Zone 3 *after* Zone 2 remain 100% collision-free.
    """
    emu_per_in = 914400.0
    slide_h_in = _get_slide_height_in(slide, 7.50)
    z3_y_thresh = round(slide_h_in - 1.30, 3)
    canvas_safe = round(slide_h_in - 0.28, 3)
    avail_bottom = min(float(safe_bottom), canvas_safe) if safe_bottom is not None else canvas_safe
    with suppress(AttributeError, TypeError, ValueError):
        for shp in slide.shapes:
            sy = float(shp.top or 0) / emu_per_in
            sw = float(shp.width or 0) / emu_per_in
            if sy >= z3_y_thresh and sw >= 8.0:
                avail_bottom = min(avail_bottom, sy - 0.16)
    if height is not None:
        avail_bottom = min(avail_bottom, float(top) + float(height))
    return round(max(float(top) + 1.20, avail_bottom), 3)


def _calc_zone2_expansion_factor(
    avail_h: float,
    natural_h: float,
    *,
    trigger_spare_in: float = 1.20,
    min_scale: float = 1.25,
    max_scale: float = 1.45,
) -> float:
    """
    Two-Stage Global Vertical Balance — Stage 1 / Direction 2 (Natural Expansion First):
    When Zone 2 has > `trigger_spare_in` (default 1.20") of unused vertical space relative to
    `avail_h`, returns a smooth spacing/padding expansion factor in `[min_scale, max_scale]`
    (`1.25x`..`1.45x`); otherwise returns `1.0` (no expansion).
    """
    spare = float(avail_h) - float(natural_h)
    if spare <= float(trigger_spare_in) + 1e-6:
        return 1.0
    t = min(1.0, max(0.0, (spare - float(trigger_spare_in)) / 1.20))
    return round(float(min_scale) + t * (float(max_scale) - float(min_scale)), 3)


def _apply_zone2_optical_vertical_balance(
    slide,
    start_shape_idx: int,
    avail_top: float,
    avail_bottom: float,
    *,
    trigger_spare_in: float = 0.50,
    optical_top_ratio: float = 0.40,
    max_top_buffer_in: float = 0.90,
) -> float:
    """
    Two-Stage Global Vertical Balance — Stage 2 / Direction 1 (Whole-Group Optical Centering ~40% / 60%):
    Inspects the entire group of Zone 2 shapes drawn by the current layout call (`slide.shapes[start_shape_idx:]`).
    If actual group height is shorter than `avail_bottom - avail_top` by > `trigger_spare_in` (0.50"),
    shifts the entire group downward as one unit to the optical center of gravity (~40% spare space above,
    ~60% below), capped at `<= max_top_buffer_in` (0.90") above `avail_top` and strictly clamped so
    `group_bottom + dy <= avail_bottom` (zero collision with Zone 3 or the 7.22" bottom margin).
    Preserves internal TOP-aligned natural flow inside every container.
    Returns the applied downward shift `dy_in` in inches (>= 0.0).
    """
    new_shapes = list(slide.shapes)[int(start_shape_idx):]
    if not new_shapes:
        return 0.0
    emu_per_in = 914400.0
    min_y = min(float(shp.top or 0) / emu_per_in for shp in new_shapes)
    max_b = max((float(shp.top or 0) + float(shp.height or 0)) / emu_per_in for shp in new_shapes)
    actual_h = max(0.0, max_b - min_y)
    avail_h = max(0.0, float(avail_bottom) - float(avail_top))
    spare_h = avail_h - actual_h
    if spare_h <= float(trigger_spare_in) + 1e-6:
        return 0.0

    desired_top_buf = min(float(max_top_buffer_in), spare_h * float(optical_top_ratio))
    target_top = float(avail_top) + desired_top_buf
    raw_dy = min(float(max_top_buffer_in), target_top - min_y)
    max_safe_dy = float(avail_bottom) - max_b
    dy_in = min(raw_dy, max_safe_dy)
    if dy_in <= 0.02:
        return 0.0

    dy_emu = int(round(dy_in * emu_per_in))
    for shp in new_shapes:
        shp.top = int(round(float(shp.top or 0))) + dy_emu
    return round(dy_in, 3)


def _shift_coords_y(coords, dy_in: float):
    """Shift a `(x, y, w, h)` rect tuple or list of rect tuples vertically by `dy_in` inches."""
    if not dy_in:
        return coords
    if isinstance(coords, tuple) and len(coords) == 4:
        return (coords[0], round(float(coords[1]) + float(dy_in), 3), coords[2], coords[3])
    if isinstance(coords, list):
        return [
            (r[0], round(float(r[1]) + float(dy_in), 3), r[2], r[3]) if (isinstance(r, tuple) and len(r) == 4) else r
            for r in coords
        ]
    return coords


def add_zone1_header(
    slide,
    chapter_pill_text: str,
    assertion_headline: str,
    pill_bg_hex: str | None = None,
    pill_fg_hex: str = "#FFFFFF",
    headline_hex: str | None = None,
    headline_pt: float = 20.5,
    subtitle_text: str | None = None,
    subtitle_pt: float = 13.0,
    subtitle_hex: str | None = None,
    right_badge_text: str | None = None,
    show_divider: bool = True,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> float:
    """
    Render Zone 1 Top Assertion Header (Module 1 Refactored — TOP-aligned natural height):
    - Eliminates old `head_lines=max(2,...)` + `MIDDLE` floating single-line gap bug (`L333`).
    - Top margin 0.15" -> Chapter pill (exact Pillow width, 9.5pt Bold) + optional right badge pill.
    - Assertion Headline (`TOP` aligned, exact height via `measure_text_layout()`).
    - Optional unboxed `subtitle_text` (`TOP` aligned, `#64748B`, `>= min_font_pt`).
    - Supports optional `tokens=None` from `build_slide_design_tokens()`.
    Returns `zone2_top_in` (recommended starting Y coordinate in inches for Zone 2).
    """
    dt, min_floor, _body_pt, typo, _sp = _resolve_engine_context(tokens, doc_theme_id)
    pal = _theme_palette(dt)
    resolved_pill_bg = pill_bg_hex if pill_bg_hex is not None else pal["primary_accent"]
    resolved_pill_fg = pal["pill_fg"] if (pill_fg_hex == "#FFFFFF" and pill_bg_hex is None and dt.get("pill_fg")) else pill_fg_hex
    resolved_headline = headline_hex if headline_hex is not None else pal["ink_primary"]
    resolved_subtitle = subtitle_hex if subtitle_hex is not None else pal["ink_muted"]
    resolved_divider = pal["divider_strong"]

    has_top_pills = False
    if chapter_pill_text and str(chapter_pill_text).strip():
        has_top_pills = True
        pill_w = calc_pill_width(chapter_pill_text, font_pt=9.5, pad_in=0.22)
        pill = _add_flat_shape(
            slide,
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.50), Inches(0.15), Inches(pill_w), Inches(0.28),
        )
        pill.adjustments[0] = 0.5
        pill.fill.solid()
        pill.fill.fore_color.rgb = hex_to_rgb_color(resolved_pill_bg)
        pill.line.fill.background()

        tf_pill = pill.text_frame
        tf_pill.word_wrap = False
        tf_pill.margin_left = Inches(0.06)
        tf_pill.margin_right = Inches(0.06)
        tf_pill.margin_top = Inches(0.02)
        tf_pill.margin_bottom = Inches(0.02)
        tf_pill.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_pill = tf_pill.paragraphs[0]
        p_pill.alignment = PP_ALIGN.CENTER
        _populate_paragraph_runs(p_pill, str(chapter_pill_text).strip(), 9.5, resolved_pill_fg, bold=True)

    if right_badge_text and str(right_badge_text).strip():
        has_top_pills = True
        rb_w = calc_pill_width(right_badge_text, font_pt=9.5, pad_in=0.22)
        rb = _add_flat_shape(
            slide,
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(max(0.50, 12.833 - rb_w)), Inches(0.15), Inches(rb_w), Inches(0.28),
        )
        rb.adjustments[0] = 0.5
        rb.fill.solid()
        rb.fill.fore_color.rgb = hex_to_rgb_color(dt.get("primary_tint", "#E0F2FE"))
        rb.line.color.rgb = hex_to_rgb_color(resolved_pill_bg)
        rb.line.width = Pt(1.0)
        tf_rb = rb.text_frame
        tf_rb.word_wrap = False
        tf_rb.margin_left = Inches(0.06)
        tf_rb.margin_right = Inches(0.06)
        tf_rb.margin_top = Inches(0.02)
        tf_rb.margin_bottom = Inches(0.02)
        tf_rb.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_rb = tf_rb.paragraphs[0]
        p_rb.alignment = PP_ALIGN.CENTER
        _populate_paragraph_runs(p_rb, str(right_badge_text).strip(), 9.5, resolved_pill_bg, bold=True)

    if isinstance(tokens, dict) and abs(float(headline_pt) - 20.5) < 1e-6:
        resolved_head_pt = float(typo["headline"])
    else:
        resolved_head_pt = max(18.0, float(headline_pt))

    head_str = str(assertion_headline or "").strip()
    m_head = measure_text_layout(head_str, box_width_in=12.333, font_pt=resolved_head_pt, bold=True, line_spacing=1.18)
    head_top = 0.50 if has_top_pills else 0.22
    head_h = round(max(0.36, float(m_head["safe_height_in"])), 3)

    headline_box = slide.shapes.add_textbox(
        Inches(0.50), Inches(head_top), Inches(12.333), Inches(head_h)
    )
    tf_head = headline_box.text_frame
    tf_head.word_wrap = True
    tf_head.margin_left = Inches(0.0)
    tf_head.margin_right = Inches(0.0)
    tf_head.margin_top = Inches(0.0)
    tf_head.margin_bottom = Inches(0.0)
    tf_head.vertical_anchor = MSO_ANCHOR.TOP
    p_head = tf_head.paragraphs[0]
    p_head.alignment = PP_ALIGN.LEFT
    p_head.line_spacing = 1.18
    _populate_paragraph_runs(p_head, head_str, resolved_head_pt, resolved_headline, bold=True)

    cursor_y = head_top + head_h

    if subtitle_text and str(subtitle_text).strip():
        if isinstance(tokens, dict) and abs(float(subtitle_pt) - 13.0) < 1e-6:
            resolved_sub_pt = float(typo["subtitle"])
        else:
            resolved_sub_pt = max(min_floor, float(subtitle_pt))
        sub_str = str(subtitle_text).strip()
        m_sub = measure_text_layout(sub_str, box_width_in=12.333, font_pt=resolved_sub_pt, bold=False, line_spacing=1.22)
        sub_top = round(cursor_y + 0.03, 3)
        sub_h = round(max(0.24, float(m_sub["safe_height_in"])), 3)
        sub_box = slide.shapes.add_textbox(
            Inches(0.50), Inches(sub_top), Inches(12.333), Inches(sub_h)
        )
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = Inches(0.0)
        tf_sub.margin_right = Inches(0.0)
        tf_sub.margin_top = Inches(0.0)
        tf_sub.margin_bottom = Inches(0.0)
        tf_sub.vertical_anchor = MSO_ANCHOR.TOP
        p_sub = tf_sub.paragraphs[0]
        p_sub.alignment = PP_ALIGN.LEFT
        p_sub.line_spacing = 1.22
        _populate_paragraph_runs(
            p_sub,
            sub_str,
            resolved_sub_pt,
            resolved_subtitle,
            bold=False,
            bold_color_hex=resolved_headline,
        )
        cursor_y = sub_top + sub_h

    divider_y = round(cursor_y + 0.06, 3)
    if show_divider:
        divider = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(0.50), Inches(divider_y), Inches(12.333), Inches(0.015),
        )
        divider.fill.solid()
        divider.fill.fore_color.rgb = hex_to_rgb_color(resolved_divider)
        divider.line.fill.background()
        return round(divider_y + 0.145, 3)

    return round(cursor_y + 0.14, 3)


def add_zone3_footer(
    slide,
    takeaway_text: str | None,
    bg_hex: str | None = None,
    border_hex: str | None = None,
    fg_hex: str = "#F8FAFC",
    font_pt: float = 13.0,
    style: str = "dark_banner",
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> None:
    """
    Render OPTIONAL Zone 3 Bottom Action Takeaway (floor >= min_font_pt, ceiling UNLOCKED).
    If `takeaway_text` is empty/None, renders nothing (preserving clean bottom breathing room).
    `style`:
      - "dark_banner" (default): high-contrast dark slate takeaway bar.
      - "subtle_line": lightweight left-accented takeaway strip without heavy dark rectangle.
    """
    if not takeaway_text or not str(takeaway_text).strip():
        return

    dt, _min_floor, resolved_pt, _typo, _sp = _resolve_engine_context(
        tokens, doc_theme_id, body_font_pt=font_pt, default_body_pt=13.0, caller_default_pt=13.0
    )
    tk_str = str(takeaway_text).strip()
    usable_w = 12.093 if style == "subtle_line" else 11.933
    m_tk = measure_text_layout(tk_str, box_width_in=usable_w, font_pt=resolved_pt, bold=True, line_spacing=1.22)
    banner_h = round(max(0.46, float(m_tk["safe_height_in"]) + 0.14), 3)
    banner_top = max(5.95, round(7.28 - banner_h, 3))
    resolved_border = border_hex if border_hex is not None else dt.get("primary_accent", "#0284C7")

    if style == "subtle_line":
        bar = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(0.50), Inches(banner_top + 0.05), Inches(0.06), Inches(max(0.28, banner_h - 0.10)),
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = hex_to_rgb_color(resolved_border)
        bar.line.fill.background()

        tb = slide.shapes.add_textbox(
            Inches(0.66), Inches(banner_top), Inches(12.173), Inches(banner_h)
        )
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.04)
        tf.margin_right = Inches(0.04)
        tf.margin_top = Inches(0.02)
        tf.margin_bottom = Inches(0.02)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE if int(m_tk["line_count"]) <= 1 else MSO_ANCHOR.TOP
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        p.line_spacing = 1.22
        ink_hex = dt.get("ink_primary", "#0F172A") if fg_hex == "#F8FAFC" else fg_hex
        _populate_paragraph_runs(p, tk_str, resolved_pt, ink_hex, bold=True, bold_color_hex=resolved_border)
        return

    resolved_bg = bg_hex if bg_hex is not None else dt.get("bookend_dark_bg", dt.get("ink_primary", "#0F172A"))
    banner = _add_flat_shape(
        slide,
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.50), Inches(banner_top), Inches(12.333), Inches(banner_h),
    )
    banner.adjustments[0] = 0.14
    banner.fill.solid()
    banner.fill.fore_color.rgb = hex_to_rgb_color(resolved_bg)
    banner.line.color.rgb = hex_to_rgb_color(resolved_border)
    banner.line.width = Pt(1.2)

    tf = banner.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.20)
    tf.margin_right = Inches(0.20)
    tf.margin_top = Inches(0.05)
    tf.margin_bottom = Inches(0.05)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE if int(m_tk["line_count"]) <= 1 else MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.line_spacing = 1.22
    _populate_paragraph_runs(p, tk_str, resolved_pt, fg_hex, bold=True)


# -------------------------------------------------------------------------
# Family 1 | Bookend & Impact (`F1-A` S0, `F1-B` S13, `F1-C` Hero / S14)
# -------------------------------------------------------------------------

def add_bookend_slide_s0(
    prs: Presentation,
    badge_text: str = "EXECUTIVE BRIEFING",
    main_title: str = "",
    subtitle_text: str = "",
    kpi_cards: list[dict[str, str]] | None = None,
    speaker_notes: str | None = None,
    bg_hex: str | None = None,
    accent_hex: str | None = None,
    title_pt: float = 28.0,
    subtitle_pt: float = 14.5,
    footer_text: str | None = None,
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
    **kwargs,
):
    """
    [F1-A / S0] Add a Dark Bookend Slide (Slide 1 Cover or Final Slide Peak-End Summary).
    Note: First argument is `prs` (Presentation), NOT `slide`. Returns newly created `slide`.
    All content text enforces `>= min_font_pt` with Content-Driven TOP-aligned KPI cards.
    """
    dt, min_floor, body_pt, typo, _sp = _resolve_engine_context(tokens, doc_theme_id)
    resolved_bg = bg_hex if bg_hex is not None else dt.get("bookend_dark_bg", "#0F172A")
    resolved_accent = accent_hex if accent_hex is not None else dt.get("bookend_accent", "#38BDF8")

    if not main_title and "title" in kwargs:
        main_title = str(kwargs["title"])
    if not subtitle_text and "subtitle" in kwargs:
        subtitle_text = str(kwargs["subtitle"])
    if kpi_cards is None and "kpi_callouts" in kwargs:
        raw_kpis = kwargs["kpi_callouts"]
        if isinstance(raw_kpis, list):
            kpi_cards = [
                c
                if isinstance(c, dict)
                else {"title": str(c[0]), "value": str(c[1]), "desc": str(c[2]) if len(c) > 2 else ""}
                for c in raw_kpis
            ]

    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide, resolved_bg)

    if badge_text and str(badge_text).strip():
        pill_w = calc_pill_width(badge_text, font_pt=10.5, pad_in=0.28)
        pill = _add_flat_shape(
            slide,
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.65), Inches(0.55), Inches(pill_w), Inches(0.34),
        )
        pill.adjustments[0] = 0.5
        pill.fill.solid()
        pill.fill.fore_color.rgb = hex_to_rgb_color("#1E293B")
        pill.line.color.rgb = hex_to_rgb_color(resolved_accent)
        pill.line.width = Pt(1.2)
        tf_p = pill.text_frame
        tf_p.word_wrap = False
        tf_p.margin_left = Inches(0.08)
        tf_p.margin_right = Inches(0.08)
        tf_p.margin_top = Inches(0.02)
        tf_p.margin_bottom = Inches(0.02)
        tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
        p0 = tf_p.paragraphs[0]
        p0.alignment = PP_ALIGN.CENTER
        _populate_paragraph_runs(p0, str(badge_text).strip(), 10.5, resolved_accent, bold=True)

    if isinstance(tokens, dict) and abs(float(title_pt) - 28.0) < 1e-6:
        resolved_title_pt = float(typo["bookend_title"])
    else:
        resolved_title_pt = max(22.0, float(title_pt))

    if isinstance(tokens, dict) and abs(float(subtitle_pt) - 14.5) < 1e-6:
        resolved_sub_pt = max(min_floor, _round_half_pt(body_pt + 1.0))
    else:
        resolved_sub_pt = max(min_floor, float(subtitle_pt))

    has_cards = bool(kpi_cards)
    title_str = str(main_title or "").strip()
    m_title = measure_text_layout(title_str, box_width_in=12.033, font_pt=resolved_title_pt, bold=True, line_spacing=1.20)
    title_top = 1.08 if has_cards else 1.85
    title_h = round(min(2.10 if has_cards else 2.40, max(0.72, float(m_title["safe_height_in"]) + 0.08)), 3)

    t_box = slide.shapes.add_textbox(Inches(0.65), Inches(title_top), Inches(12.033), Inches(title_h))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = Inches(0.0)
    tf_t.margin_right = Inches(0.0)
    tf_t.vertical_anchor = MSO_ANCHOR.TOP if has_cards else MSO_ANCHOR.MIDDLE
    pt = tf_t.paragraphs[0]
    pt.alignment = PP_ALIGN.LEFT
    pt.line_spacing = 1.20
    _populate_paragraph_runs(pt, title_str, resolved_title_pt, "#F8FAFC", bold=True)

    cursor_y = title_top + title_h
    if subtitle_text and str(subtitle_text).strip():
        sub_str = str(subtitle_text).strip()
        m_sub = measure_text_layout(sub_str, box_width_in=12.033, font_pt=resolved_sub_pt, bold=False, line_spacing=1.30)
        sub_top = round(cursor_y + 0.14, 3)
        sub_h = round(min(1.25 if has_cards else 1.50, max(0.40, float(m_sub["safe_height_in"]) + 0.06)), 3)
        s_box = slide.shapes.add_textbox(Inches(0.65), Inches(sub_top), Inches(12.033), Inches(sub_h))
        tf_s = s_box.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = Inches(0.0)
        tf_s.margin_right = Inches(0.0)
        tf_s.vertical_anchor = MSO_ANCHOR.TOP
        ps = tf_s.paragraphs[0]
        ps.alignment = PP_ALIGN.LEFT
        ps.line_spacing = 1.30
        _populate_paragraph_runs(ps, sub_str, resolved_sub_pt, "#CBD5E1", bold=False, bold_color_hex="#FFFFFF")
        cursor_y = sub_top + sub_h

    footer_pt = max(min_floor, _round_half_pt(body_pt - 0.5))
    footer_y = 6.76
    if footer_text and str(footer_text).strip():
        m_f = measure_text_layout(str(footer_text).strip(), 12.033, footer_pt, bold=False, line_spacing=1.20)
        f_h = round(max(0.36, float(m_f["safe_height_in"]) + 0.04), 3)
        footer_y = round(7.24 - f_h, 3)
        f_box = slide.shapes.add_textbox(Inches(0.65), Inches(footer_y), Inches(12.033), Inches(f_h))
        tf_f = f_box.text_frame
        tf_f.word_wrap = True
        tf_f.margin_left = Inches(0.0)
        tf_f.margin_right = Inches(0.0)
        tf_f.vertical_anchor = MSO_ANCHOR.MIDDLE if int(m_f["line_count"]) <= 1 else MSO_ANCHOR.TOP
        pf = tf_f.paragraphs[0]
        pf.alignment = PP_ALIGN.LEFT
        _populate_paragraph_runs(pf, str(footer_text).strip(), footer_pt, "#94A3B8", bold=False, bold_color_hex=resolved_accent)

    if kpi_cards:
        n = min(3, len(kpi_cards))
        total_w = 12.033
        gap = 0.28
        card_w = (total_w - gap * (n - 1)) / n
        cy = round(max(3.15, cursor_y + 0.28), 3)
        max_avail_ch = max(1.20, round((footer_y - 0.20 if footer_text else 7.05) - cy, 3))
        card_title_pt = max(min_floor, _round_half_pt(body_pt))
        card_val_pt = max(19.0, _round_half_pt(body_pt + 5.5))
        card_desc_pt = max(min_floor, _round_half_pt(body_pt - 0.5 if body_pt >= 13.5 else body_pt))

        norm_cards: list[dict[str, object]] = []
        req_card_h = 0.0
        for raw_card in kpi_cards[:n]:
            if isinstance(raw_card, dict):
                card = raw_card
            elif isinstance(raw_card, (list, tuple)) and len(raw_card) >= 2:
                card = (
                    {"title": raw_card[0], "desc": raw_card[1]}
                    if len(raw_card) == 2
                    else {"title": raw_card[0], "value": raw_card[1], "desc": raw_card[2]}
                )
            else:
                card = {"title": str(raw_card), "desc": ""}
            norm_cards.append(card)
            inner_w = max(0.8, card_w - 0.44)
            ch_need = 0.36
            if card.get("title"):
                ch_need += float(measure_text_layout(str(card["title"]), inner_w, card_title_pt, bold=True, line_spacing=1.20)["content_height_in"]) + 0.08
            if card.get("value"):
                ch_need += float(measure_text_layout(str(card["value"]), inner_w, card_val_pt, bold=True, line_spacing=1.18)["content_height_in"]) + 0.10
            if card.get("desc"):
                ch_need += float(measure_text_layout(str(card["desc"]), inner_w, card_desc_pt, bold=False, line_spacing=1.30)["content_height_in"]) + 0.08
            req_card_h = max(req_card_h, ch_need)

        ch = round(min(max_avail_ch, max(min(max_avail_ch, 2.05), req_card_h + 0.24)), 3)
        for idx, card in enumerate(norm_cards):
            cx = 0.65 + idx * (card_w + gap)
            c_acc = str(card.get("accent", resolved_accent))
            is_spot = bool(card.get("is_spotlight", idx == 0 and n > 1))

            box = _add_flat_shape(
                slide,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(cx), Inches(cy), Inches(card_w), Inches(ch),
            )
            box.adjustments[0] = 0.05
            box.fill.solid()
            box.fill.fore_color.rgb = hex_to_rgb_color("#1E293B")
            box.line.color.rgb = hex_to_rgb_color(c_acc if is_spot else "#334155")
            box.line.width = Pt(1.6 if is_spot else 1.0)

            strip = _add_flat_shape(
                slide,
                MSO_SHAPE.RECTANGLE,
                Inches(cx + 0.18), Inches(cy + 0.01), Inches(card_w - 0.36), Inches(0.055 if is_spot else 0.035),
            )
            strip.fill.solid()
            strip.fill.fore_color.rgb = hex_to_rgb_color(c_acc if is_spot else "#475569")
            strip.line.fill.background()

            tb = slide.shapes.add_textbox(
                Inches(cx + 0.22), Inches(cy + 0.18), Inches(card_w - 0.44), Inches(max(0.8, ch - 0.28))
            )
            tf_c = tb.text_frame
            tf_c.word_wrap = True
            tf_c.vertical_anchor = MSO_ANCHOR.TOP
            tf_c.margin_left = Inches(0.02)
            tf_c.margin_right = Inches(0.02)
            tf_c.margin_top = Inches(0.02)
            tf_c.margin_bottom = Inches(0.02)

            p_title = tf_c.paragraphs[0]
            p_title.alignment = PP_ALIGN.LEFT
            p_title.space_after = Pt(6)
            _populate_paragraph_runs(p_title, str(card.get("title", "")).strip(), card_title_pt, c_acc if is_spot else "#94A3B8", bold=True)

            if card.get("value"):
                p_val = tf_c.add_paragraph()
                p_val.alignment = PP_ALIGN.LEFT
                p_val.space_after = Pt(7)
                _populate_paragraph_runs(p_val, str(card.get("value", "")).strip(), card_val_pt, "#FFFFFF", bold=True)

            if card.get("desc"):
                p_desc = tf_c.add_paragraph()
                p_desc.alignment = PP_ALIGN.LEFT
                p_desc.line_spacing = 1.30
                _populate_paragraph_runs(p_desc, str(card.get("desc", "")).strip(), card_desc_pt, "#E2E8F0", bold=False, bold_color_hex="#FFFFFF")

    if speaker_notes:
        add_speaker_notes(slide, speaker_notes)
    return slide


def draw_section_divider_slide(
    slide,
    section_num: str | int,
    section_title: str,
    subtitle_text: str = "",
    tokens: dict[str, object] | None = None,
    doc_theme_id: str | None = None,
) -> None:
    """
    [F1-B / S13] Render an Ultra-Minimal Editorial Section Divider Slide (ZERO card boxes, high breathing whitespace).
    Features oversized typographic section numeral, crisp accent rule, large bold section title, and optional subtitle.
    """
    dt, min_floor, body_pt, typo, _sp = _resolve_engine_context(tokens, doc_theme_id)
    primary_acc = dt.get("primary_accent", "#0284C7")
    ink_pri = dt.get("ink_primary", "#0F172A")
    ink_muted = dt.get("ink_muted", "#64748B")
    soft_num_hex = _blend_hex(primary_acc, dt.get("bg_canvas", "#F8FAFC"), 0.22)

    raw_num = str(section_num).strip()
    if raw_num.isdigit():
        num_str = f"{int(raw_num):02d}"
    else:
        num_str = raw_num or "01"

    title_str = str(section_title or "").strip()
    sub_str = str(subtitle_text or "").strip()

    num_pt = 68.0
    title_pt = max(32.0, _round_half_pt(float(typo["bookend_title"]) + 4.0))
    sub_pt = max(min_floor, _round_half_pt(body_pt + 2.0))

    content_x = 1.15
    content_w = 10.80
    m_num = measure_text_layout(num_str, content_w, num_pt, bold=True, line_spacing=1.08)
    m_title = measure_text_layout(title_str, content_w, title_pt, bold=True, line_spacing=1.18)
    m_sub = measure_text_layout(sub_str, content_w, sub_pt, bold=False, line_spacing=1.30) if sub_str else None

    num_h = round(max(0.95, float(m_num["safe_height_in"])), 3)
    title_h = round(max(0.60, float(m_title["safe_height_in"]) + 0.04), 3)
    sub_h = round(float(m_sub["safe_height_in"]) + 0.04, 3) if m_sub else 0.0

    total_block_h = num_h + 0.22 + title_h + (0.20 + sub_h if sub_str else 0.0)
    start_y = round(max(1.15, (7.5 - total_block_h) * 0.46), 3)

    # Left vertical architectural hairline anchored to the title block
    v_accent = _add_flat_shape(
        slide,
        MSO_SHAPE.RECTANGLE,
        Inches(0.68), Inches(start_y + num_h + 0.08), Inches(0.065), Inches(max(0.80, title_h + (0.20 + sub_h if sub_str else 0.0) + 0.14)),
    )
    v_accent.fill.solid()
    v_accent.fill.fore_color.rgb = hex_to_rgb_color(primary_acc)
    v_accent.line.fill.background()

    # Oversized section numeral
    nb = slide.shapes.add_textbox(Inches(content_x), Inches(start_y), Inches(content_w), Inches(num_h))
    tf_n = nb.text_frame
    tf_n.word_wrap = True
    tf_n.vertical_anchor = MSO_ANCHOR.TOP
    tf_n.margin_left = Inches(0.0)
    tf_n.margin_right = Inches(0.0)
    pn = tf_n.paragraphs[0]
    pn.alignment = PP_ALIGN.LEFT
    _populate_paragraph_runs(pn, num_str, num_pt, soft_num_hex, bold=True)

    # Crisp short horizontal accent bar
    rule_y = round(start_y + num_h + 0.04, 3)
    h_rule = _add_flat_shape(
        slide,
        MSO_SHAPE.RECTANGLE,
        Inches(content_x), Inches(rule_y), Inches(1.25), Inches(0.06),
    )
    h_rule.fill.solid()
    h_rule.fill.fore_color.rgb = hex_to_rgb_color(primary_acc)
    h_rule.line.fill.background()

    # Large bold section title
    title_y = round(rule_y + 0.22, 3)
    tb = slide.shapes.add_textbox(Inches(content_x), Inches(title_y), Inches(content_w), Inches(title_h))
    tf_t = tb.text_frame
    tf_t.word_wrap = True
    tf_t.vertical_anchor = MSO_ANCHOR.TOP
    tf_t.margin_left = Inches(0.0)
    tf_t.margin_right = Inches(0.0)
    pt_p = tf_t.paragraphs[0]
    pt_p.alignment = PP_ALIGN.LEFT
    pt_p.line_spacing = 1.18
    _populate_paragraph_runs(pt_p, title_str, title_pt, ink_pri, bold=True)

    if sub_str:
        sub_y = round(title_y + title_h + 0.18, 3)
        sb = slide.shapes.add_textbox(Inches(content_x), Inches(sub_y), Inches(content_w), Inches(sub_h))
        tf_s = sb.text_frame
        tf_s.word_wrap = True
        tf_s.vertical_anchor = MSO_ANCHOR.TOP
        tf_s.margin_left = Inches(0.0)
        tf_s.margin_right = Inches(0.0)
        ps = tf_s.paragraphs[0]
        ps.alignment = PP_ALIGN.LEFT
        ps.line_spacing = 1.30
        _populate_paragraph_runs(ps, sub_str, sub_pt, ink_muted, bold=False, bold_color_hex=ink_pri)


def _normalize_callout_items(callouts: Sequence[object] | None) -> list[tuple[str, str]]:
    """Normalize callout items into [(lead_heading, body), ...] pairs using SSOT `_parse_lead_body_item()`."""
    if not callouts:
        return []
    normalized: list[tuple[str, str]] = []
    for item in callouts:
        h, b = _parse_lead_body_item(item)
        if h or b:
            normalized.append((h, b))
    return normalized


def _estimate_vertical_callouts_height(
    items: list[tuple[str, str]],
    w: float,
    heading: str | None,
    body_pt: float,
    gap_scale: float = 1.0,
) -> float:
    """Measure exact natural vertical height (inches) of `_render_unboxed_callouts_vertical()`."""
    heading_pt = _round_half_pt(body_pt * 1.30)
    lead_pt = _round_half_pt(body_pt * 1.15)
    total_h = 0.0
    if heading and heading.strip():
        m_h = measure_text_layout(heading.strip(), box_width_in=max(0.6, w - 0.04), font_pt=heading_pt, bold=True, line_spacing=1.20)
        total_h += max(0.32, float(m_h["safe_height_in"])) + 0.06 + 0.18
    if not items:
        return round(total_h, 3)
    txt_w = max(0.55, w - 0.18)
    base_gap = (0.26 if len(items) <= 2 else 0.22) * max(1.0, float(gap_scale))
    for idx, (c_title, c_body) in enumerate(items):
        item_h = _measure_lead_body_item_height(c_title, c_body, txt_w, lead_pt, body_pt, line_spacing=1.30)
        box_h = item_h + 0.02
        vis_h = 0.0
        if c_title:
            vis_h += float(measure_text_layout(c_title, max(0.45, txt_w - 0.04), lead_pt, bold=True, line_spacing=1.22)["content_height_in"])
        if c_body:
            vis_h += float(measure_text_layout(c_body, max(0.45, txt_w - 0.04), body_pt, bold=False, line_spacing=1.30)["content_height_in"])
        if c_title and c_body:
            vis_h += 0.04
        bar_h = min(max(0.28, box_h - 0.04), max(0.28, vis_h + 0.04))
        if idx < len(items) - 1:
            total_h += max(bar_h + 0.06, min(box_h, vis_h + 0.10)) + base_gap
        else:
            total_h += box_h
    return round(total_h, 3)


def _render_unboxed_callouts_vertical(
    slide,
    items: list[tuple[str, str]],
    x: float,
    y: float,
    w: float,
    h: float,
    heading: str | None,
    body_pt: float,
    spotlight_idx: int | None,
    dt: dict[str, str],
    gap_scale: float = 1.0,
) -> None:
    """
    Render side unboxed callouts (Module 1 Upgraded — fixes L1083 1.25" heading gap):
    - Strict `MSO_ANCHOR.TOP` natural top-down flow (abolishes vertical centering gap & `slot_h` equal split).
    - Clear typography scale: Heading `1.30x` Bold -> Lead `1.15x` Bold -> Body `1.0x` Regular (`#334155`).
    - Left vertical accent hairline strictly hugs each item's exact rendered text height via `measure_text_layout()`.
    """
    pal = _theme_palette(dt)
    theme_pri = pal["primary_accent"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    muted_bar = pal["muted_bar"]

    heading_pt = _round_half_pt(body_pt * 1.30)
    lead_pt = _round_half_pt(body_pt * 1.15)
    cur_y = float(y)

    if heading and heading.strip():
        h_str = heading.strip()
        m_h = measure_text_layout(h_str, box_width_in=max(0.6, w - 0.04), font_pt=heading_pt, bold=True, line_spacing=1.20)
        h_box_h = round(max(0.32, float(m_h["safe_height_in"])), 3)
        hb = slide.shapes.add_textbox(Inches(x), Inches(cur_y), Inches(w), Inches(h_box_h))
        tf_h = hb.text_frame
        tf_h.word_wrap = True
        tf_h.margin_left = Inches(0.0)
        tf_h.margin_right = Inches(0.0)
        tf_h.margin_top = Inches(0.0)
        tf_h.margin_bottom = Inches(0.0)
        tf_h.vertical_anchor = MSO_ANCHOR.TOP
        ph = tf_h.paragraphs[0]
        ph.alignment = PP_ALIGN.LEFT
        ph.line_spacing = 1.20
        _populate_paragraph_runs(ph, h_str, heading_pt, ink_pri, bold=True)

        rule_y = round(cur_y + h_box_h + 0.06, 3)
        h_rule = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(x), Inches(rule_y), Inches(min(w, 1.40)), Inches(0.03),
        )
        h_rule.fill.solid()
        h_rule.fill.fore_color.rgb = hex_to_rgb_color(theme_pri)
        h_rule.line.fill.background()
        cur_y = round(rule_y + 0.18, 3)

    if not items:
        return

    txt_w = max(0.55, w - 0.18)
    item_heights = [
        _measure_lead_body_item_height(c_title, c_body, txt_w, lead_pt, body_pt, line_spacing=1.30)
        for c_title, c_body in items
    ]
    avail_h = max(0.80, (y + h) - cur_y)
    base_gap = round((0.26 if len(items) <= 2 else 0.22) * max(1.0, float(gap_scale)), 3)
    raw_sum = sum(item_heights)
    if len(items) > 1:
        eff_gap = min(base_gap, max(0.08, (avail_h - raw_sum) / (len(items) - 1)))
    else:
        eff_gap = 0.0

    for idx, ((c_title, c_body), item_h) in enumerate(zip(items, item_heights)):
        is_spot = spotlight_idx is not None and idx == spotlight_idx
        bar_hex = theme_pri if is_spot else muted_bar
        rem_h = max(0.32, (y + h) - cur_y)
        box_h = round(min(rem_h, item_h + 0.02), 3)

        # Left hairline strictly hugs exact visual text height (without overflow-guard padding)
        vis_h = 0.0
        if c_title:
            vis_h += float(measure_text_layout(c_title, max(0.45, txt_w - 0.04), lead_pt, bold=True, line_spacing=1.22)["content_height_in"])
        if c_body:
            vis_h += float(measure_text_layout(c_body, max(0.45, txt_w - 0.04), body_pt, bold=False, line_spacing=1.30)["content_height_in"])
        if c_title and c_body:
            vis_h += 0.04
        bar_h = round(min(max(0.28, box_h - 0.04), max(0.28, vis_h + 0.04)), 3)
        bar = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(x), Inches(cur_y + 0.02), Inches(0.055 if is_spot else 0.035), Inches(bar_h),
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = hex_to_rgb_color(bar_hex)
        bar.line.fill.background()

        _render_lead_body_box(
            slide,
            x=x + 0.16,
            y=cur_y,
            w=txt_w,
            h=box_h,
            lead=c_title,
            body=c_body,
            lead_pt=lead_pt,
            body_pt=body_pt,
            lead_hex=theme_pri if is_spot else ink_pri,
            body_hex=ink_body,
            bold_color_hex=ink_pri,
            line_spacing=1.30,
        )
        cur_y = round(cur_y + max(bar_h + 0.06, min(box_h, vis_h + 0.10)) + eff_gap, 3)


def _render_unboxed_callouts_horizontal(
    slide,
    items: list[tuple[str, str]],
    x: float,
    y: float,
    w: float,
    h: float,
    body_pt: float,
    spotlight_idx: int | None,
    dt: dict[str, str],
) -> None:
    """Render top or bottom horizontal unboxed callouts (`TOP` aligned, `1.15x / 1.0x` hierarchy, text-hugging left bars)."""
    n = max(1, len(items))
    gap = 0.34
    col_w = (w - gap * (n - 1)) / n
    pal = _theme_palette(dt)
    theme_pri = pal["primary_accent"]
    ink_pri = pal["ink_primary"]
    ink_body = pal["ink_body"]
    muted_bar = pal["muted_bar"]
    lead_pt = _round_half_pt(body_pt * 1.15)

    for idx, (c_title, c_body) in enumerate(items):
        cx = x + idx * (col_w + gap)
        is_spot = spotlight_idx is not None and idx == spotlight_idx
        rule_hex = theme_pri if is_spot else muted_bar
        txt_w = max(0.60, col_w - 0.16)
        item_h = _measure_lead_body_item_height(c_title, c_body, txt_w, lead_pt, body_pt, line_spacing=1.28)
        box_h = round(min(max(0.36, h), item_h + 0.04), 3)

        vis_h = 0.0
        if c_title:
            vis_h += float(measure_text_layout(c_title, max(0.45, txt_w - 0.04), lead_pt, bold=True, line_spacing=1.22)["content_height_in"])
        if c_body:
            vis_h += float(measure_text_layout(c_body, max(0.45, txt_w - 0.04), body_pt, bold=False, line_spacing=1.28)["content_height_in"])
        if c_title and c_body:
            vis_h += 0.04
        bar_h = round(min(max(0.28, box_h - 0.04), max(0.28, vis_h + 0.04)), 3)

        rule = _add_flat_shape(
            slide,
            MSO_SHAPE.RECTANGLE,
            Inches(cx), Inches(y + 0.02), Inches(0.055 if is_spot else 0.035), Inches(bar_h),
        )
        rule.fill.solid()
        rule.fill.fore_color.rgb = hex_to_rgb_color(rule_hex)
        rule.line.fill.background()

        _render_lead_body_box(
            slide,
            x=cx + 0.14,
            y=y,
            w=txt_w,
            h=box_h,
            lead=c_title,
            body=c_body,
            lead_pt=lead_pt,
            body_pt=body_pt,
            lead_hex=theme_pri if is_spot else ink_pri,
            body_hex=ink_body,
            bold_color_hex=ink_pri,
            line_spacing=1.28,
        )


def _estimate_horizontal_band_height(items: list[tuple[str, str]], total_w: float, body_pt: float) -> float:
    """Measure exact horizontal unboxed callout band height in inches via Pillow `measure_text_layout()`."""
    n = max(1, len(items))
    col_w = max(1.2, (total_w - 0.34 * (n - 1)) / n)
    usable_col_w = max(0.65, col_w - 0.16)
    lead_pt = _round_half_pt(body_pt * 1.15)
    max_item_h = 0.0
    for c_title, c_body in items:
        req = _measure_lead_body_item_height(c_title, c_body, usable_col_w, lead_pt, body_pt, line_spacing=1.28)
        max_item_h = max(max_item_h, req)
    return round(max(0.76, max_item_h + 0.10), 3)
