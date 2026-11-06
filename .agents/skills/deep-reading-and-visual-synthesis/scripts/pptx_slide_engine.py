"""
pptx_slide_engine.py
Native Vector 16:9 Presentation Slide Engine for Format C (.pptx).
Grounded in Alley & Neeley (2005) Assertion-Evidence Architecture, Knaflic (2015) 80/20 Preattentive Spotlight,
Kosslyn (2007) Compatibility Principle, Mackworth (1948) Anti-Habituation Alternation, and Kahneman (1993) Peak-End Bookends.

Provides reusable building blocks:
- create_widescreen_presentation() -> Presentation (13.333" x 7.5")
- calc_pill_width(text, font_pt=9.5, pad_in=0.22) -> float (inches)
- add_zone1_header(slide, chapter_pill_text, assertion_headline, ...)
- add_zone3_footer(slide, takeaway_text, ...)
- add_speaker_notes(slide, notes_text)
- add_bookend_slide_s0(prs, badge_text, main_title, subtitle_text, kpi_cards=None, speaker_notes=None)
- draw_parallel_row_cards(slide, cards_spec, left=0.50, top=1.36, total_width=12.333, height=5.12, ...)
- validate_layout_sequence(layouts, require_bookends=True, min_distinct=5) -> bool
"""

import unicodedata
from typing import List, Dict, Optional, Sequence, Tuple
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

FONT_FAMILY = "Microsoft JhengHei"


def hex_to_rgb_color(hex_str: str) -> RGBColor:
    """Convert '#RRGGBB' hex string to python-pptx RGBColor."""
    clean = hex_str.strip().lstrip("#")
    if len(clean) == 3:
        clean = "".join(c * 2 for c in clean)
    return RGBColor(int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16))


def calc_pill_width(text: str, font_pt: float = 9.5, pad_in: float = 0.22) -> float:
    """
    Calculate exact text-hugging pill width in inches for Microsoft JhengHei:
    pill_w = (font_pt / 72.0) * (1.00 * CJK_Chars + 0.50 * ASCII_Chars) + pad_in
    """
    cjk_count = 0
    ascii_count = 0
    for ch in str(text or ""):
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            cjk_count += 1
        else:
            ascii_count += 1
    w = (float(font_pt) / 72.0) * (1.00 * cjk_count + 0.50 * ascii_count) + float(pad_in)
    return round(max(0.85, w), 3)


def create_widescreen_presentation() -> Presentation:
    """Create a 16:9 widescreen Presentation (13.333" x 7.5")."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def set_slide_background(slide, bg_hex: str = "#F8FAFC") -> None:
    """Set solid background color for a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb_color(bg_hex)


def add_speaker_notes(slide, notes_text: str) -> None:
    """Write oral narrative and transition script into slide speaker notes."""
    if not notes_text:
        return
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = str(notes_text).strip()


def add_zone1_header(
    slide,
    chapter_pill_text: str,
    assertion_headline: str,
    pill_bg_hex: str = "#0284C7",
    pill_fg_hex: str = "#FFFFFF",
    headline_hex: str = "#0F172A",
    headline_pt: float = 20.5,
) -> None:
    """
    Render Zone 1 (Top 15% height, y = 0.0" to 1.18"):
    - Top margin 0.15" -> Chapter pill (top=0.15", height=0.28", exact text-hug width, 9.5pt Bold).
    - Breathing gap 0.15" -> Assertion headline (top=0.58", height=0.44", 19.5~22pt Bold, MSO_ANCHOR.MIDDLE).
    """
    pill_w = calc_pill_width(chapter_pill_text, font_pt=9.5, pad_in=0.22)
    pill = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.50), Inches(0.15), Inches(pill_w), Inches(0.28)
    )
    pill.adjustments[0] = 0.5
    pill.fill.solid()
    pill.fill.fore_color.rgb = hex_to_rgb_color(pill_bg_hex)
    pill.line.fill.background()

    tf_pill = pill.text_frame
    tf_pill.word_wrap = False
    tf_pill.margin_left = Inches(0.06)
    tf_pill.margin_right = Inches(0.06)
    tf_pill.margin_top = Inches(0.02)
    tf_pill.margin_bottom = Inches(0.02)
    tf_pill.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_pill = tf_pill.paragraphs[0]
    p_pill.text = str(chapter_pill_text).strip()
    p_pill.alignment = PP_ALIGN.CENTER
    p_pill.font.name = FONT_FAMILY
    p_pill.font.size = Pt(9.5)
    p_pill.font.bold = True
    p_pill.font.color.rgb = hex_to_rgb_color(pill_fg_hex)

    headline_box = slide.shapes.add_textbox(
        Inches(0.50), Inches(0.58), Inches(12.333), Inches(0.44)
    )
    tf_head = headline_box.text_frame
    tf_head.word_wrap = True
    tf_head.margin_left = Inches(0.0)
    tf_head.margin_right = Inches(0.0)
    tf_head.margin_top = Inches(0.0)
    tf_head.margin_bottom = Inches(0.0)
    tf_head.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_head = tf_head.paragraphs[0]
    p_head.text = str(assertion_headline).strip()
    p_head.font.name = FONT_FAMILY
    p_head.font.size = Pt(max(19.5, min(22.0, float(headline_pt))))
    p_head.font.bold = True
    p_head.font.color.rgb = hex_to_rgb_color(headline_hex)

    divider = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0.50), Inches(1.14), Inches(12.333), Inches(0.015)
    )
    divider.fill.solid()
    divider.fill.fore_color.rgb = hex_to_rgb_color("#CBD5E1")
    divider.line.fill.background()


def add_zone3_footer(
    slide,
    takeaway_text: str,
    bg_hex: str = "#0F172A",
    border_hex: str = "#0284C7",
    fg_hex: str = "#F8FAFC",
    font_pt: float = 13.0,
) -> None:
    """
    Render Zone 3 (Bottom 10% height, y = 6.68" to 7.22"):
    Full-width high-contrast action takeaway banner (12.5~14.0pt).
    """
    banner = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.50), Inches(6.68), Inches(12.333), Inches(0.54)
    )
    banner.adjustments[0] = 0.18
    banner.fill.solid()
    banner.fill.fore_color.rgb = hex_to_rgb_color(bg_hex)
    banner.line.color.rgb = hex_to_rgb_color(border_hex)
    banner.line.width = Pt(1.5)

    tf = banner.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.20)
    tf.margin_right = Inches(0.20)
    tf.margin_top = Inches(0.04)
    tf.margin_bottom = Inches(0.04)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = str(takeaway_text).strip()
    p.font.name = FONT_FAMILY
    p.font.size = Pt(max(12.5, min(14.0, float(font_pt))))
    p.font.bold = True
    p.font.color.rgb = hex_to_rgb_color(fg_hex)


def add_bookend_slide_s0(
    prs: Presentation,
    badge_text: str = "EXECUTIVE BRIEFING",
    main_title: str = "",
    subtitle_text: str = "",
    kpi_cards: Optional[List[Dict[str, str]]] = None,
    speaker_notes: Optional[str] = None,
    bg_hex: str = "#0F172A",
    accent_hex: str = "#38BDF8",
    **kwargs,
):
    """
    Add an S0 Dark Bookend Slide (for Slide 1 Cover or Final Slide Peak-End Summary).
    `kpi_cards`: list of up to 3 dicts: [{"title": str, "value": str, "desc": str, "accent": "#38BDF8"}, ...]
    """
    if not main_title and "title" in kwargs:
        main_title = str(kwargs["title"])
    if not subtitle_text and "subtitle" in kwargs:
        subtitle_text = str(kwargs["subtitle"])
    if kpi_cards is None and "kpi_callouts" in kwargs:
        raw_kpis = kwargs["kpi_callouts"]
        if isinstance(raw_kpis, list):
            kpi_cards = [
                c if isinstance(c, dict) else {"title": str(c[0]), "value": str(c[1]), "desc": str(c[2]) if len(c) > 2 else ""}
                for c in raw_kpis
            ]
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide, bg_hex)

    pill_w = calc_pill_width(badge_text, font_pt=10.5, pad_in=0.28)
    pill = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.65), Inches(0.65), Inches(pill_w), Inches(0.34)
    )
    pill.adjustments[0] = 0.5
    pill.fill.solid()
    pill.fill.fore_color.rgb = hex_to_rgb_color("#1E293B")
    pill.line.color.rgb = hex_to_rgb_color(accent_hex)
    pill.line.width = Pt(1.2)
    tf_p = pill.text_frame
    tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
    p0 = tf_p.paragraphs[0]
    p0.text = str(badge_text).strip()
    p0.alignment = PP_ALIGN.CENTER
    p0.font.name = FONT_FAMILY
    p0.font.size = Pt(10.5)
    p0.font.bold = True
    p0.font.color.rgb = hex_to_rgb_color(accent_hex)

    t_box = slide.shapes.add_textbox(Inches(0.65), Inches(1.25), Inches(12.0), Inches(1.45))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.vertical_anchor = MSO_ANCHOR.MIDDLE
    pt = tf_t.paragraphs[0]
    pt.text = str(main_title).strip()
    pt.font.name = FONT_FAMILY
    pt.font.size = Pt(28.0)
    pt.font.bold = True
    pt.font.color.rgb = hex_to_rgb_color("#F8FAFC")

    s_box = slide.shapes.add_textbox(Inches(0.65), Inches(2.78), Inches(12.0), Inches(0.75))
    tf_s = s_box.text_frame
    tf_s.word_wrap = True
    ps = tf_s.paragraphs[0]
    ps.text = str(subtitle_text).strip()
    ps.font.name = FONT_FAMILY
    ps.font.size = Pt(14.5)
    ps.font.color.rgb = hex_to_rgb_color("#94A3B8")

    if kpi_cards:
        n = min(3, len(kpi_cards))
        total_w = 12.033
        gap = 0.28
        card_w = (total_w - gap * (n - 1)) / n
        for idx, card in enumerate(kpi_cards[:n]):
            cx = 0.65 + idx * (card_w + gap)
            cy = 3.85
            ch = 2.95
            c_acc = card.get("accent", accent_hex)
            box = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(cx), Inches(cy), Inches(card_w), Inches(ch)
            )
            box.adjustments[0] = 0.06
            box.fill.solid()
            box.fill.fore_color.rgb = hex_to_rgb_color("#1E293B")
            box.line.color.rgb = hex_to_rgb_color(c_acc)
            box.line.width = Pt(1.75)

            tb = slide.shapes.add_textbox(Inches(cx + 0.22), Inches(cy + 0.18), Inches(card_w - 0.44), Inches(ch - 0.36))
            tf_c = tb.text_frame
            tf_c.word_wrap = True
            p_title = tf_c.paragraphs[0]
            p_title.text = str(card.get("title", "")).strip()
            p_title.font.name = FONT_FAMILY
            p_title.font.size = Pt(12.0)
            p_title.font.bold = True
            p_title.font.color.rgb = hex_to_rgb_color(c_acc)
            p_title.space_after = Pt(6)

            if card.get("value"):
                p_val = tf_c.add_paragraph()
                p_val.text = str(card.get("value", "")).strip()
                p_val.font.name = FONT_FAMILY
                p_val.font.size = Pt(18.0)
                p_val.font.bold = True
                p_val.font.color.rgb = hex_to_rgb_color("#FFFFFF")
                p_val.space_after = Pt(8)

            if card.get("desc"):
                p_desc = tf_c.add_paragraph()
                p_desc.text = str(card.get("desc", "")).strip()
                p_desc.font.name = FONT_FAMILY
                p_desc.font.size = Pt(12.0)
                p_desc.font.color.rgb = hex_to_rgb_color("#CBD5E1")
                p_desc.line_spacing = 1.3

    if speaker_notes:
        add_speaker_notes(slide, speaker_notes)
    return slide


def draw_parallel_row_cards(
    slide,
    cards_spec: List[Dict[str, object]],
    left: float = 0.50,
    top: float = 1.36,
    total_width: float = 12.333,
    height: float = 5.12,
    gap: float = 0.24,
    spotlight_idx: Optional[int] = None,
    body_font_pt: Optional[float] = None,
    width_ratios: Optional[List[float]] = None,
) -> List[Tuple[float, float, float, float]]:
    """
    Render 2, 3, or 4 parallel column cards in Zone 2 with horizontal row-slot alignment:
    - Enforces column-count typography floors:
      * 2-column cards (S1): 13.0~14.5pt (default 13.5pt)
      * 3-column or 4-column cards (S2, S3, S7): 11.5~12.5pt (default 12.0pt)
    - Enforces Knaflic 80/20 spotlight rule: only `spotlight_idx` uses high-chroma border/strip;
      other cards use calm structural slate (#CBD5E1 border, #475569 header).
    - Divides each card body into equal-height horizontal row slots (MSO_ANCHOR.MIDDLE) so
      Row 1 (Shallow), Row 2 (Middle), Row 3 (Deep) align 100% horizontally across all cards.
    """
    n_cols = len(cards_spec)
    if n_cols == 0:
        return []

    if body_font_pt is None:
        resolved_pt = 13.5 if n_cols <= 2 else 12.0
    else:
        floor_pt = 13.0 if n_cols <= 2 else 11.5
        ceil_pt = 14.5 if n_cols <= 2 else 12.5
        resolved_pt = max(floor_pt, min(ceil_pt, float(body_font_pt)))

    title_pt = 16.0 if n_cols <= 2 else 14.5

    if width_ratios and len(width_ratios) == n_cols:
        tot_r = sum(width_ratios)
        usable_w = total_width - gap * (n_cols - 1)
        col_widths = [usable_w * (r / tot_r) for r in width_ratios]
    else:
        w = (total_width - gap * (n_cols - 1)) / n_cols
        col_widths = [w] * n_cols

    max_rows = max(len(c.get("rows", [])) for c in cards_spec)
    max_rows = max(1, max_rows)

    header_h = 0.62
    body_top = top + header_h + 0.06
    body_h = height - header_h - 0.12
    slot_h = body_h / max_rows

    coords = []
    cur_x = left
    for idx, card in enumerate(cards_spec):
        cw = col_widths[idx]
        is_spot = (spotlight_idx == idx) if spotlight_idx is not None else bool(card.get("is_spotlight", False))
        accent_hex = str(card.get("accent", "#0284C7" if is_spot else "#64748B"))
        border_hex = accent_hex if is_spot else "#CBD5E1"
        card_bg_hex = str(card.get("bg", "#FFFFFF"))
        header_bg_hex = accent_hex if is_spot else "#F1F5F9"
        header_fg_hex = "#FFFFFF" if is_spot else "#0F172A"

        base_rect = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(cur_x), Inches(top), Inches(cw), Inches(height)
        )
        base_rect.adjustments[0] = 0.04
        base_rect.fill.solid()
        base_rect.fill.fore_color.rgb = hex_to_rgb_color(card_bg_hex)
        base_rect.line.color.rgb = hex_to_rgb_color(border_hex)
        base_rect.line.width = Pt(2.2 if is_spot else 1.2)

        hdr_rect = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(cur_x), Inches(top), Inches(cw), Inches(header_h)
        )
        hdr_rect.adjustments[0] = 0.04
        hdr_rect.fill.solid()
        hdr_rect.fill.fore_color.rgb = hex_to_rgb_color(header_bg_hex)
        hdr_rect.line.color.rgb = hex_to_rgb_color(border_hex)
        hdr_rect.line.width = Pt(1.5 if is_spot else 1.0)

        tf_h = hdr_rect.text_frame
        tf_h.word_wrap = True
        tf_h.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf_h.margin_left = Inches(0.16)
        tf_h.margin_right = Inches(0.16)
        ph = tf_h.paragraphs[0]
        badge_str = f"【{card['badge']}】" if card.get("badge") else ""
        ph.text = f"{badge_str}{card.get('title', '')}".strip()
        ph.font.name = FONT_FAMILY
        ph.font.size = Pt(title_pt)
        ph.font.bold = True
        ph.font.color.rgb = hex_to_rgb_color(header_fg_hex)

        rows = list(card.get("rows", []))
        for r_i in range(max_rows):
            sy = body_top + r_i * slot_h
            if r_i > 0:
                sep = slide.shapes.add_shape(
                    MSO_SHAPE.RECTANGLE,
                    Inches(cur_x + 0.14), Inches(sy), Inches(cw - 0.28), Inches(0.01)
                )
                sep.fill.solid()
                sep.fill.fore_color.rgb = hex_to_rgb_color("#E2E8F0")
                sep.line.fill.background()

            if r_i < len(rows):
                row_text = rows[r_i]
                tb = slide.shapes.add_textbox(
                    Inches(cur_x + 0.14), Inches(sy + 0.04), Inches(cw - 0.28), Inches(slot_h - 0.08)
                )
                tf_r = tb.text_frame
                tf_r.word_wrap = True
                tf_r.vertical_anchor = MSO_ANCHOR.MIDDLE
                tf_r.margin_left = Inches(0.04)
                tf_r.margin_right = Inches(0.04)
                tf_r.margin_top = Inches(0.02)
                tf_r.margin_bottom = Inches(0.02)

                paragraphs = row_text if isinstance(row_text, (list, tuple)) else [str(row_text)]
                for p_i, seg in enumerate(paragraphs):
                    p = tf_r.paragraphs[0] if p_i == 0 else tf_r.add_paragraph()
                    p.text = str(seg).strip()
                    p.font.name = FONT_FAMILY
                    p.font.size = Pt(resolved_pt)
                    p.font.color.rgb = hex_to_rgb_color("#1E293B")
                    p.line_spacing = 1.28
                    p.space_after = Pt(4)

        coords.append((cur_x, top, cw, height))
        cur_x += cw + gap

    return coords


def validate_layout_sequence(
    layouts: Sequence[str],
    require_bookends: bool = True,
    min_distinct: int = 5,
) -> bool:
    """
    Enforce Phase 2 Format C Storyboard Anti-Collision Rules:
    1. First and last slides must be 'S0' when `require_bookends=True` and len(layouts) >= 3.
    2. Adjacent slides must never repeat the same layout code (`layouts[i] != layouts[i+1]`).
    3. Full deck (>= 6 slides) must use at least `min_distinct` distinct layout codes.
    Raises ValueError on violation; returns True when valid.
    """
    seq = [str(x).strip().upper() for x in layouts]
    if not seq:
        raise ValueError("Layout sequence cannot be empty.")

    if require_bookends and len(seq) >= 3:
        if seq[0] != "S0" or seq[-1] != "S0":
            raise ValueError(
                f"Mandatory Bookend Rule violated: Slide 1 ({seq[0]}) and Final Slide ({seq[-1]}) must both be 'S0'."
            )
        for mid_idx, code in enumerate(seq[1:-1], start=2):
            if code == "S0":
                raise ValueError(f"Slide {mid_idx} uses 'S0', which is reserved exclusively for Cover and Closing bookends.")

    for i in range(len(seq) - 1):
        if seq[i] == seq[i + 1]:
            raise ValueError(
                f"Adjacent Layout Collision at Slide {i + 1} -> Slide {i + 2}: both use '{seq[i]}'. "
                f"Switch Slide {i + 2} to its fallback layout per the Semantic-to-Layout Dispatch Table."
            )

    distinct_count = len(set(seq))
    max_possible = max(1, (len(seq) - 1) if (require_bookends and len(seq) >= 3) else len(seq))
    required_distinct = min(int(min_distinct), max_possible)
    if distinct_count < required_distinct:
        raise ValueError(
            f"Insufficient layout diversity: found {distinct_count} distinct layouts ({sorted(set(seq))}) across {len(seq)} slides, "
            f"but at least {required_distinct} are required to prevent visual habituation."
        )

    return True
