"""
pptx_engine/text_layout.py
Pillow Microsoft JhengHei real advance-width metrics, CJK Kinsoku wrapping, and geometry-first autofit.
Note: `pptx_slide_engine` is the public entry point.
"""

import math
import re
import unicodedata
from collections.abc import Sequence
from contextlib import suppress
from pathlib import Path

from .tokens import FONT_FAMILY, MIN_CONTENT_FONT_PT

WINDOWS_MSJH_REGULAR = Path(r"C:\Windows\Fonts\msjh.ttc")


WINDOWS_MSJH_BOLD = Path(r"C:\Windows\Fonts\msjhbd.ttc")


MSJH_LINE_HEIGHT_EM = 1.3333  # Natural (ascent+descent)/em of Microsoft JhengHei (384/288)


DEFAULT_TEXT_WIDTH_SAFETY = 1.01  # Empirically calibrated against Windows PowerPoint COM (39-case suite, 0 under-predictions)


KINSOKU_NO_START = frozenset("，。、；：！？）》」』】〉〕〗〞’”）％‰…—～·.,;:!?)]}%")


KINSOKU_HANGING_PUNCT = frozenset("，。、；：！？.,;:!?")


KINSOKU_NO_END = frozenset("（《「『【〈〔〖〝‘“([{¥$£€±")


ORPHAN_IGNORED_CHARS = frozenset("，。、；：！？）》」』】〉〕〗〞’”（）《「『【〈〔〖〝‘“.,;:!?()[]{}—…～·- \t\r\n")


_LATIN_TOKEN_RE = re.compile(r"(?:[+±](?=\d))?[A-Za-z0-9]+(?:['’][A-Za-z]+|,[0-9]+|[._:][A-Za-z0-9]+|[+%‰]+)*[-/]?")


def calc_pill_width(text: str, font_pt: float = 9.5, pad_in: float = 0.24) -> float:
    """
    Calculate exact text-hugging pill width in inches for Microsoft JhengHei using
    Pillow `msjhbd.ttc` (`index=0`) advance width via `measure_text_layout()`.
    """
    raw = str(text or "").strip()
    if not raw:
        return round(max(0.85, float(pad_in)), 3)
    m = measure_text_layout(raw, box_width_in=24.0, font_pt=float(font_pt), bold=True, line_spacing=1.15)
    w = float(m["max_line_width_in"]) + float(pad_in)
    return round(max(0.85, w), 3)


def _est_wrapped_lines(text: str, usable_w_in: float, font_pt: float, bold: bool = False) -> int:
    """Measure exact wrapped line count via Pillow + CJK Kinsoku `measure_text_layout()`."""
    clean = str(text or "").strip()
    if not clean:
        return 1
    m = measure_text_layout(clean, box_width_in=max(0.35, float(usable_w_in)), font_pt=max(6.0, float(font_pt)), bold=bold)
    return max(1, int(m["line_count"]))


def _load_msjh_font(size_px: int, bold: bool = False):
    """Load Windows Microsoft JhengHei (`msjh.ttc` / `msjhbd.ttc`, `index=0`) via Pillow with caching."""
    with suppress(ImportError, OSError, ValueError):
        from PIL import ImageFont  # type: ignore

        font_path = WINDOWS_MSJH_BOLD if bold else WINDOWS_MSJH_REGULAR
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size=int(size_px), index=0)
        alt_path = WINDOWS_MSJH_REGULAR if bold else WINDOWS_MSJH_BOLD
        if alt_path.exists():
            return ImageFont.truetype(str(alt_path), size=int(size_px), index=0)
    return None


def _parse_inline_bold_segments(text: str, default_bold: bool = False) -> list[tuple[str, bool]]:
    """Split text into `(segment_text, is_bold)` tuples honoring inline `**bold**` spans."""
    raw = str(text or "")
    if not raw:
        return []
    parts = re.split(r"(\*\*(?:(?!\*\*).)+\*\*)", raw)
    segments: list[tuple[str, bool]] = []
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) >= 5:
            segments.append((part[2:-2], True))
        else:
            segments.append((part, bool(default_bold)))
    return segments


def _tokenize_line_for_kinsoku(segments: list[tuple[str, bool]]) -> list[tuple[str, bool]]:
    """
    Tokenize a single hard paragraph into atomic wrapping units for Traditional Chinese + Latin mixed text.
    - NEVER splits Chinese by whitespace and NEVER inserts `-` hyphenation.
    - Keeps contiguous Latin words / numbers / percentages / codes as atomic tokens.
    - Splits CJK ideographs and punctuation into individual character tokens for Kinsoku processing.
    """
    tokens: list[tuple[str, bool]] = []
    for seg_text, is_bold in segments:
        idx = 0
        n = len(seg_text)
        while idx < n:
            ch = seg_text[idx]
            if ch in (" ", "\t"):
                j = idx + 1
                while j < n and seg_text[j] in (" ", "\t"):
                    j += 1
                tokens.append((" ", is_bold))
                idx = j
                continue
            m = _LATIN_TOKEN_RE.match(seg_text, idx)
            if m:
                tokens.append((m.group(0), is_bold))
                idx = m.end()
                continue
            tokens.append((ch, is_bold))
            idx += 1
    return tokens


def _measure_styled_tokens_width_in(
    tokens: Sequence[tuple[str, bool]],
    font_pt: float,
    safety: float,
    reg_font,
    bold_font,
    ref_dpi: float = 288.0,
) -> float:
    """Measure exact advance width in inches for a list of `(text, is_bold)` tokens."""
    if not tokens:
        return 0.0
    if reg_font is not None or bold_font is not None:
        # Merge adjacent same-weight runs to preserve authentic kerning & sub-pixel advances
        total_px = 0.0
        run_buf: list[str] = []
        run_bold = tokens[0][1]
        for tok_txt, tok_bold in tokens:
            if tok_bold == run_bold:
                run_buf.append(tok_txt)
            else:
                f_obj = (bold_font or reg_font) if run_bold else (reg_font or bold_font)
                total_px += float(f_obj.getlength("".join(run_buf)))
                run_buf = [tok_txt]
                run_bold = tok_bold
        if run_buf:
            f_obj = (bold_font or reg_font) if run_bold else (reg_font or bold_font)
            total_px += float(f_obj.getlength("".join(run_buf)))
        return (total_px / ref_dpi) * float(safety)

    # Geometric fallback when Pillow or Windows msjh.ttc is unavailable
    em_units = 0.0
    for tok_txt, tok_bold in tokens:
        w_mult = 1.03 if tok_bold else 1.0
        for ch in tok_txt:
            if unicodedata.east_asian_width(ch) in ("W", "F"):
                em_units += 1.00 * w_mult
            elif ch == " ":
                em_units += 0.28
            elif ch.isupper() or ch in "MW%&@":
                em_units += 0.66 * w_mult
            else:
                em_units += 0.50 * w_mult
    return ((float(font_pt) / 72.0) * em_units) * float(safety)


def _trim_line_edge_spaces(tokens: list[tuple[str, bool]]) -> list[tuple[str, bool]]:
    """Trim leading and trailing pure-space tokens from a wrapped line."""
    start = 0
    end = len(tokens)
    while start < end and tokens[start][0].strip() == "":
        start += 1
    while end > start and tokens[end - 1][0].strip() == "":
        end -= 1
    return tokens[start:end]


def _count_orphan_core_chars(line_text: str) -> int:
    """Count non-punctuation, non-whitespace core characters on a line for orphan detection."""
    return sum(1 for ch in line_text if ch not in ORPHAN_IGNORED_CHARS)


def _wrap_paragraph_kinsoku(
    tokens: list[tuple[str, bool]],
    eff_width_in: float,
    font_pt: float,
    safety: float,
    reg_font,
    bold_font,
    hanging_punct: bool = True,
    ref_dpi: float = 288.0,
) -> list[tuple[str, float]]:
    """
    Wrap a tokenized paragraph using Traditional Chinese Kinsoku rules:
    - Prohibits `KINSOKU_NO_START` at line start (using hanging punctuation when enabled or pulling previous token).
    - Prohibits `KINSOKU_NO_END` (opening brackets) at line end (pushing them to the next line).
    - Breaks overly wide atomic Latin tokens cleanly by character without inserting `-`.
    """
    if not tokens:
        return [("", 0.0)]

    em_in = float(font_pt) / 72.0
    hang_allowance_in = (0.72 * em_in) if hanging_punct else 0.0

    def _w(toks: Sequence[tuple[str, bool]]) -> float:
        return _measure_styled_tokens_width_in(toks, font_pt, safety, reg_font, bold_font, ref_dpi)

    lines_toks: list[list[tuple[str, bool]]] = []
    cur: list[tuple[str, bool]] = []
    idx = 0
    n = len(tokens)

    while idx < n:
        tok_txt, tok_bold = tokens[idx]
        if not cur and tok_txt.strip() == "":
            idx += 1
            continue

        candidate = cur + [(tok_txt, tok_bold)]
        cand_w = _w(candidate)

        if cand_w <= eff_width_in + 1e-6:
            cur = candidate
            idx += 1
            continue

        # Token overflows current line
        if not cur or all(len(t[0]) == 1 and t[0] in KINSOKU_NO_END for t in cur):
            # Single atomic token (or opener + wide atomic token) wider than box: break char-by-char (no '-')
            if len(tok_txt) > 1:
                split_pos = 1
                for k in range(2, len(tok_txt) + 1):
                    if _w(cur + [(tok_txt[:k], tok_bold)]) <= eff_width_in + 1e-6:
                        split_pos = k
                    else:
                        break
                lines_toks.append(cur + [(tok_txt[:split_pos], tok_bold)])
                cur = []
                tokens = tokens[:idx] + [(tok_txt[split_pos:], tok_bold)] + tokens[idx + 1:]
                n = len(tokens)
                continue
            lines_toks.append(cur + [(tok_txt, tok_bold)])
            cur = []
            idx += 1
            continue

        # Rule 1: No-start punctuation (`KINSOKU_NO_START`)
        if len(tok_txt) == 1 and tok_txt in KINSOKU_NO_START:
            if tok_txt in KINSOKU_HANGING_PUNCT and hanging_punct and cand_w <= eff_width_in + hang_allowance_in:
                # Allow single punctuation to hang at line end (matching PowerPoint hangingPunct="1")
                cur = candidate
                lines_toks.append(_trim_line_edge_spaces(cur))
                cur = []
                idx += 1
                continue
            # Otherwise pull preceding token(s) down with this punctuation (oi-dashi),
            # continuing past consecutive closing/no-start punctuation (e.g., `》，` or `）。`)
            cur_trimmed = _trim_line_edge_spaces(cur)
            if len(cur_trimmed) >= 2:
                carry = [(tok_txt, tok_bold)]
                while len(cur_trimmed) >= 2 and (
                    (len(carry[0][0]) == 1 and carry[0][0] in KINSOKU_NO_START)
                    or (len(cur_trimmed[-1][0]) == 1 and cur_trimmed[-1][0] in KINSOKU_NO_END)
                ):
                    carry.insert(0, cur_trimmed.pop())
                lines_toks.append(_trim_line_edge_spaces(cur_trimmed))
                cur = carry
                idx += 1
                continue

        # Rule 2: No-end opening brackets (`KINSOKU_NO_END`)
        cur_trimmed = _trim_line_edge_spaces(cur)
        carry_openers: list[tuple[str, bool]] = []
        while len(cur_trimmed) >= 2 and cur_trimmed[-1][0] in KINSOKU_NO_END:
            carry_openers.insert(0, cur_trimmed.pop())

        lines_toks.append(_trim_line_edge_spaces(cur_trimmed))
        if tok_txt.strip() == "":
            cur = carry_openers
            idx += 1
        else:
            cur = carry_openers
            # Re-evaluate current token on the new line in next iteration

    if cur:
        trimmed = _trim_line_edge_spaces(cur)
        if trimmed:
            lines_toks.append(trimmed)

    if not lines_toks:
        return [("", 0.0)]

    return [("".join(t[0] for t in lt), round(_w(lt), 4)) for lt in lines_toks]


def measure_text_layout(
    text: str,
    box_width_in: float,
    font_pt: float,
    bold: bool = False,
    line_spacing: float = 1.30,
    safety: float = DEFAULT_TEXT_WIDTH_SAFETY,
    space_after_pt: float = 0.0,
    margin_left_in: float = 0.0,
    margin_right_in: float = 0.0,
    margin_top_in: float = 0.0,
    margin_bottom_in: float = 0.0,
    hanging_punct: bool = True,
    font_family: str = FONT_FAMILY,
) -> dict[str, object]:
    """
    Measure exact wrapped lines, orphan status, and safe container height using
    Pillow + Windows `msjh.ttc` / `msjhbd.ttc` (`index=0`, Microsoft JhengHei) and
    Traditional Chinese Kinsoku rules (supporting inline `**bold**` segments).
    """
    _ = font_family  # Reserved for future custom font paths; Windows primary is msjh.ttc index=0
    raw_w = float(box_width_in)
    raw_pt = float(font_pt)
    raw_ls = float(line_spacing)
    raw_safety = float(safety)
    if not (math.isfinite(raw_w) and math.isfinite(raw_pt) and math.isfinite(raw_ls) and math.isfinite(raw_safety)):
        raise ValueError(
            f"box_width_in ({box_width_in}), font_pt ({font_pt}), line_spacing ({line_spacing}), "
            f"and safety ({safety}) must be finite numbers."
        )
    resolved_pt = max(6.0, raw_pt)
    resolved_ls = max(1.0, raw_ls)
    resolved_safety = max(0.85, raw_safety)
    usable_w = max(0.25, raw_w - float(margin_left_in) - float(margin_right_in))

    ref_dpi = 288.0
    size_px = max(12, int(round(resolved_pt * (ref_dpi / 72.0))))
    reg_font = _load_msjh_font(size_px, bold=False)
    bold_font = _load_msjh_font(size_px, bold=True)
    backend = "pillow_msjh" if (reg_font is not None or bold_font is not None) else "fallback_heuristic"

    raw_text = str(text or "")
    if not raw_text.strip():
        single_h = (resolved_pt * MSJH_LINE_HEIGHT_EM * resolved_ls) / 72.0
        safe_h = round(single_h + float(margin_top_in) + float(margin_bottom_in) + 0.04, 4)
        return {
            "line_count": 0,
            "lines": [],
            "line_widths_in": [],
            "max_line_width_in": 0.0,
            "usable_width_in": round(usable_w, 4),
            "last_line_text": "",
            "last_line_char_count": 0,
            "last_line_cjk_chars": 0,
            "orphan_flag": False,
            "orphan_paragraphs": [],
            "content_height_in": 0.0,
            "safe_height_in": safe_h,
            "font_backend": backend,
            "safety_factor": resolved_safety,
        }

    # Split into hard paragraphs while preserving inline **bold** state per line
    hard_paragraphs = raw_text.splitlines()
    all_lines: list[str] = []
    all_widths: list[float] = []
    orphan_paragraphs: list[int] = []

    for p_idx, para in enumerate(hard_paragraphs):
        if not para.strip():
            all_lines.append("")
            all_widths.append(0.0)
            continue
        segs = _parse_inline_bold_segments(para, default_bold=bold)
        toks = _tokenize_line_for_kinsoku(segs)
        wrapped = _wrap_paragraph_kinsoku(
            toks,
            usable_w,
            resolved_pt,
            resolved_safety,
            reg_font,
            bold_font,
            hanging_punct=hanging_punct,
            ref_dpi=ref_dpi,
        )
        p_lines = [w[0] for w in wrapped]
        p_widths = [w[1] for w in wrapped]
        all_lines.extend(p_lines)
        all_widths.extend(p_widths)

        if len(p_lines) >= 2:
            tail_core = _count_orphan_core_chars(p_lines[-1])
            if 0 < tail_core <= 2:
                orphan_paragraphs.append(p_idx)

    line_count = len(all_lines)
    last_line_text = all_lines[-1] if all_lines else ""
    last_core = _count_orphan_core_chars(last_line_text)
    last_cjk = sum(
        1 for ch in last_line_text
        if ch not in ORPHAN_IGNORED_CHARS and unicodedata.east_asian_width(ch) in ("W", "F")
    )

    # PowerPoint line advance: first (N-1) lines advance by font_pt * MSJH_LINE_HEIGHT_EM * line_spacing;
    # final line needs natural glyph box height (font_pt * MSJH_LINE_HEIGHT_EM).
    single_natural_in = (resolved_pt * MSJH_LINE_HEIGHT_EM) / 72.0
    step_in = single_natural_in * resolved_ls
    inter_para_in = (max(0, len(hard_paragraphs) - 1) * max(0.0, float(space_after_pt))) / 72.0
    content_h = ((max(0, line_count - 1) * step_in) + single_natural_in + inter_para_in) if line_count > 0 else 0.0
    safe_h = content_h + float(margin_top_in) + float(margin_bottom_in) + 0.04

    return {
        "line_count": line_count,
        "lines": all_lines,
        "line_widths_in": all_widths,
        "max_line_width_in": round(max(all_widths, default=0.0), 4),
        "usable_width_in": round(usable_w, 4),
        "last_line_text": last_line_text,
        "last_line_char_count": last_core,
        "last_line_cjk_chars": last_cjk,
        "orphan_flag": bool(orphan_paragraphs),
        "orphan_paragraphs": orphan_paragraphs,
        "content_height_in": round(content_h, 4),
        "safe_height_in": round(safe_h, 4),
        "font_backend": backend,
        "safety_factor": resolved_safety,
    }


# -------------------------------------------------------------------------
# Step 3 Core 3: Inverted Geometry-First Autofit (NEVER shrink font first)
# -------------------------------------------------------------------------

def _normalize_box_dict(box: object) -> dict[str, float]:
    """Normalize a `(left, top, width, height)` tuple or dict into a canonical box dict."""
    if isinstance(box, dict):
        return {
            "left": float(box.get("left", box.get("x", 0.5))),
            "top": float(box.get("top", box.get("y", 1.36))),
            "width": max(0.5, float(box.get("width", box.get("w", 4.0)))),
            "height": max(0.3, float(box.get("height", box.get("h", 2.0)))),
        }
    if isinstance(box, (list, tuple)) and len(box) >= 4:
        return {
            "left": float(box[0]),
            "top": float(box[1]),
            "width": max(0.5, float(box[2])),
            "height": max(0.3, float(box[3])),
        }
    raise TypeError(f"Unsupported box specification: {box!r}")


def _measure_single_text_spec(
    spec: object,
    box: dict[str, float],
    default_font_pt: float,
    default_line_spacing: float,
    default_bold: bool,
    safety: float,
) -> dict[str, object]:
    """Measure a single text spec (str, dict, or list of paragraphs) against a candidate box."""
    if isinstance(spec, dict):
        text = spec.get("text")
        if text is None and "paragraphs" in spec:
            text = "\n".join(str(p) for p in spec["paragraphs"])
        font_pt = max(default_font_pt, float(spec.get("font_pt", default_font_pt)))
        bold = bool(spec.get("bold", default_bold))
        ls = float(spec.get("line_spacing", default_line_spacing))
        sa = float(spec.get("space_after_pt", 0.0))
        ml = float(spec.get("margin_left_in", spec.get("margin_x_in", 0.0)))
        mr = float(spec.get("margin_right_in", spec.get("margin_x_in", 0.0)))
        mt = float(spec.get("margin_top_in", spec.get("margin_y_in", 0.0)))
        mb = float(spec.get("margin_bottom_in", spec.get("margin_y_in", 0.0)))
    elif isinstance(spec, (list, tuple)):
        text = "\n".join(str(p) for p in spec)
        font_pt, bold, ls, sa = default_font_pt, default_bold, default_line_spacing, 4.0
        ml = mr = mt = mb = 0.0
    else:
        text = str(spec or "")
        font_pt, bold, ls, sa = default_font_pt, default_bold, default_line_spacing, 0.0
        ml = mr = mt = mb = 0.0

    return measure_text_layout(
        str(text or ""),
        box_width_in=box["width"],
        font_pt=font_pt,
        bold=bold,
        line_spacing=ls,
        safety=safety,
        space_after_pt=sa,
        margin_left_in=ml,
        margin_right_in=mr,
        margin_top_in=mt,
        margin_bottom_in=mb,
    )


def autofit_box_geometry_first(
    text_spec: object,
    candidate_boxes: object,
    target_body_pt: float,
    min_font_pt: float = MIN_CONTENT_FONT_PT,
    line_spacing: float = 1.30,
    bold: bool = False,
    max_bottom_in: float = 7.25,
    max_right_in: float = 12.833,
    safety: float = DEFAULT_TEXT_WIDTH_SAFETY,
    allow_rebalance: bool = True,
    allow_height_grow: bool = True,
) -> dict[str, object]:
    """
    Inverted Geometry-First Autofit Engine (never shrinks font below `target_body_pt` or `min_font_pt`):
    - Phase 1 (Width Rebalance / Micro-Expand): If overflow or orphan last line (`<= 2` CJK chars) is
      detected, rebalances widths across adjacent columns (or gently widens a single box within bounds).
    - Phase 2 (Grow Height Downward): Expands box height downward up to `max_bottom_in`.
    - Phase 3 (Split Flag / Copy Consent): If geometry alone cannot resolve overflow, flags
      `needs_split_slide=True` (`fits=False`); if only an orphan remains, flags `needs_copy_consent=True`.
    - Hard Invariant: `resolved_font_pt >= max(min_font_pt, target_body_pt)` and `font_shrunk` is ALWAYS `False`.
    """
    raw_min = float(min_font_pt)
    raw_target = float(target_body_pt)
    if not (math.isfinite(raw_min) and math.isfinite(raw_target)):
        raise ValueError(
            f"min_font_pt ({min_font_pt}) and target_body_pt ({target_body_pt}) must be finite numbers."
        )
    resolved_min = max(MIN_CONTENT_FONT_PT, raw_min)
    effective_pt = max(resolved_min, raw_target)

    if isinstance(candidate_boxes, dict) or (
        isinstance(candidate_boxes, (list, tuple))
        and len(candidate_boxes) == 4
        and all(isinstance(v, (int, float)) for v in candidate_boxes)
    ):
        boxes = [_normalize_box_dict(candidate_boxes)]
    elif isinstance(candidate_boxes, (list, tuple)) and len(candidate_boxes) > 0:
        boxes = [_normalize_box_dict(b) for b in candidate_boxes]
    else:
        raise ValueError("candidate_boxes must be a box dict/4-tuple or a non-empty list of boxes.")

    n_boxes = len(boxes)
    if n_boxes == 1:
        specs = [text_spec]
    elif isinstance(text_spec, (list, tuple)) and len(text_spec) == n_boxes:
        specs = list(text_spec)
    else:
        raise ValueError(
            f"Mismatch between candidate_boxes count ({n_boxes}) and text_spec; "
            "pass a sequence of equal length for multi-box autofit."
        )

    def _measure_all(cur_boxes: list[dict[str, float]]) -> list[dict[str, object]]:
        return [
            _measure_single_text_spec(sp, bx, effective_pt, line_spacing, bold, safety)
            for sp, bx in zip(specs, cur_boxes)
        ]

    actions: list[str] = []
    measurements = _measure_all(boxes)

    # Phase 1: Rebalance adjacent columns or micro-expand single box width
    if allow_rebalance:
        if n_boxes == 1:
            m0 = measurements[0]
            b0 = boxes[0]
            needs_help = (float(m0["safe_height_in"]) > b0["height"]) or bool(m0["orphan_flag"])
            avail_w = max(0.0, float(max_right_in) - (b0["left"] + b0["width"]))
            if needs_help and avail_w > 0.05:
                step_max = min(avail_w, 0.50)
                best_w = b0["width"]
                best_m = m0
                fallback_w = b0["width"]
                fallback_m = m0
                for step_i in range(1, 11):
                    trial_w = round(b0["width"] + step_max * (step_i / 10.0), 3)
                    trial_box = dict(b0, width=trial_w)
                    trial_m = _measure_single_text_spec(specs[0], trial_box, effective_pt, line_spacing, bold, safety)
                    if float(trial_m["safe_height_in"]) < float(fallback_m["safe_height_in"]) - 1e-3:
                        fallback_w = trial_w
                        fallback_m = trial_m
                    improved_overflow = float(trial_m["safe_height_in"]) < float(best_m["safe_height_in"]) - 1e-3
                    fixed_orphan = bool(best_m["orphan_flag"]) and not bool(trial_m["orphan_flag"])
                    if fixed_orphan or (improved_overflow and not bool(trial_m["orphan_flag"])):
                        best_w = trial_w
                        best_m = trial_m
                        if float(best_m["safe_height_in"]) <= b0["height"] and not bool(best_m["orphan_flag"]):
                            break
                if best_w <= b0["width"] + 1e-4 and float(m0["safe_height_in"]) > b0["height"] and fallback_w > b0["width"] + 1e-4:
                    best_w = fallback_w
                if best_w > b0["width"] + 1e-4:
                    boxes[0]["width"] = best_w
                    measurements = _measure_all(boxes)
                    actions.append("expand_width")
        else:
            # Multi-column horizontal rebalance preserving outer edges, gaps, and caller input order
            order = sorted(range(n_boxes), key=lambda idx: (boxes[idx]["left"], boxes[idx]["top"]))
            same_row = all(abs(boxes[idx]["top"] - boxes[order[0]]["top"]) <= 0.35 for idx in order)
            gaps = [
                round(boxes[order[pos + 1]]["left"] - (boxes[order[pos]]["left"] + boxes[order[pos]]["width"]), 4)
                for pos in range(n_boxes - 1)
            ]
            is_horizontal_row = same_row and all(g >= -0.02 for g in gaps)
            if is_horizontal_row:
                min_col_w = 1.60
                rebalanced = False
                for _pass in range(3):
                    changed = False
                    for pos_i in range(n_boxes):
                        i = order[pos_i]
                        mi = measurements[i]
                        overflow_i = float(mi["safe_height_in"]) - boxes[i]["height"]
                        orphan_i = bool(mi["orphan_flag"])
                        if overflow_i <= 0.0 and not orphan_i:
                            continue
                        # Find donor column with greatest spare vertical capacity
                        best_donor = None
                        best_spare = 0.0
                        for pos_j in range(n_boxes):
                            j = order[pos_j]
                            if j == i:
                                continue
                            mj = measurements[j]
                            spare_j = boxes[j]["height"] - float(mj["safe_height_in"])
                            if spare_j > best_spare and boxes[j]["width"] > min_col_w + 0.25 and not bool(mj["orphan_flag"]):
                                best_spare = spare_j
                                best_donor = j
                        if best_donor is None:
                            continue
                        max_delta = min(boxes[best_donor]["width"] - min_col_w, boxes[i]["width"] * 0.25, 0.75)
                        if max_delta <= 0.05:
                            continue
                        base_boxes = [dict(b) for b in boxes]
                        best_trial_boxes: list[dict[str, float]] | None = None
                        best_trial_ms: list[dict[str, object]] | None = None
                        for step_i in range(1, 9):
                            delta = round(max_delta * (step_i / 8.0), 3)
                            trial_boxes = [dict(b) for b in base_boxes]
                            trial_boxes[i]["width"] = round(trial_boxes[i]["width"] + delta, 3)
                            trial_boxes[best_donor]["width"] = round(trial_boxes[best_donor]["width"] - delta, 3)
                            # Recompute left positions cleanly along sorted visual order preserving gaps
                            cur_x = trial_boxes[order[0]]["left"]
                            for pos_k, k in enumerate(order):
                                trial_boxes[k]["left"] = round(cur_x, 3)
                                cur_x += trial_boxes[k]["width"] + (gaps[pos_k] if pos_k < n_boxes - 1 else 0.0)
                            trial_ms = _measure_all(trial_boxes)
                            donor_ok = (
                                float(trial_ms[best_donor]["safe_height_in"]) <= trial_boxes[best_donor]["height"]
                                and not bool(trial_ms[best_donor]["orphan_flag"])
                            )
                            ref_mi = best_trial_ms[i] if best_trial_ms is not None else mi
                            ref_orphan = bool(ref_mi["orphan_flag"])
                            target_better = (
                                (float(trial_ms[i]["safe_height_in"]) < float(ref_mi["safe_height_in"]) - 1e-3 and not (not ref_orphan and bool(trial_ms[i]["orphan_flag"])))
                                or (ref_orphan and not bool(trial_ms[i]["orphan_flag"]) and float(trial_ms[i]["safe_height_in"]) <= float(ref_mi["safe_height_in"]) + 1e-3)
                            )
                            if donor_ok and target_better:
                                best_trial_boxes = trial_boxes
                                best_trial_ms = trial_ms
                                if float(trial_ms[i]["safe_height_in"]) <= trial_boxes[i]["height"] and not bool(trial_ms[i]["orphan_flag"]):
                                    break
                        if best_trial_boxes is not None and best_trial_ms is not None:
                            boxes = best_trial_boxes
                            measurements = best_trial_ms
                            changed = True
                            rebalanced = True
                    if not changed:
                        break
                if rebalanced:
                    actions.append("rebalance_widths")

    # Phase 2: Grow box height downward (within max_bottom_in and respecting vertically stacked neighbors)
    if allow_height_grow:
        grew_any = False
        for i in range(n_boxes):
            req_h = round(float(measurements[i]["safe_height_in"]) + 0.02, 3)
            if req_h > boxes[i]["height"]:
                bottom_limit = float(max_bottom_in)
                bi = boxes[i]
                for j in range(n_boxes):
                    if j == i:
                        continue
                    bj = boxes[j]
                    x_overlap = min(bi["left"] + bi["width"], bj["left"] + bj["width"]) - max(bi["left"], bj["left"])
                    if x_overlap > 0.02 and bj["top"] >= bi["top"] + bi["height"] - 0.02:
                        bottom_limit = min(bottom_limit, bj["top"] - 0.12)
                max_h = round(bottom_limit - bi["top"], 3)
                if max_h >= req_h:
                    boxes[i]["height"] = req_h
                    grew_any = True
                elif max_h > boxes[i]["height"]:
                    boxes[i]["height"] = max_h
                    grew_any = True
        if grew_any:
            actions.append("grow_height")

    # Phase 3: Evaluate final fit (NEVER shrink font)
    still_overflow = any(
        float(measurements[i]["safe_height_in"]) > boxes[i]["height"] + 1e-4
        for i in range(n_boxes)
    )
    orphan_unresolved = any(bool(m["orphan_flag"]) for m in measurements)
    if still_overflow:
        actions.append("split_slide_required")
    if not actions:
        actions.append("none")

    return {
        "fits": not still_overflow,
        "boxes": boxes,
        "measurements": measurements,
        "resolved_font_pt": effective_pt,
        "min_font_pt": resolved_min,
        "font_shrunk": False,
        "actions": actions,
        "needs_split_slide": still_overflow,
        "orphan_unresolved": orphan_unresolved,
        "needs_copy_consent": (not still_overflow) and orphan_unresolved,
    }
