"""
pptx_engine/spec_pipeline.py
Two-stage layout routing, anti-collision sequence validator, Step 4A preview, deterministic spec renderer, and fidelity checker.
Note: `pptx_slide_engine` is the public entry point.
"""

import copy
import json
import os
import re
import tempfile
from collections import Counter
from collections.abc import Sequence
from contextlib import suppress
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches

from .tokens import (
    MIN_CONTENT_FONT_PT,
    _read_image_pixel_size,
    add_speaker_notes,
    build_slide_design_tokens,
    create_widescreen_presentation,
    set_slide_background,
)
from .media_omml import (
    _OMML_A_NS,
    _OMML_MC_NS,
    _OMML_M_NS,
    render_svg_to_png_300dpi,
)
from .primitives import (
    _LEADING_INDEX_PREFIX_RE,
    _LEAD_BODY_SPLIT_RE,
    _extract_lead_body_items,
    _first_non_empty_str,
    _parse_lead_body_item,
    add_bookend_slide_s0,
    add_zone1_header,
    add_zone3_footer,
    draw_section_divider_slide,
)
from .layouts_data import (
    draw_comparison_table_slide,
    draw_focal_anatomy_s6,
    draw_kpi_strip_slide,
    draw_quadrant_matrix_s5,
    draw_theme_geometric_accent,
    draw_visual_callout_slide,
)
from .layouts_narrative import (
    draw_bento_grid_slide,
    draw_clean_mechanism_s4,
    draw_editorial_split_rows_s8,
    draw_hero_stat_slide,
    draw_parallel_row_cards,
    draw_process_steps_s3,
)

_CANONICAL_LAYOUT_MAP: dict[str, tuple[str, str, bool, str]] = {
    # code -> (canonical_id, family_group, default_boxed, legacy_adj_key)
    "F1-A": ("F1-A", "F1", False, "F1-A"),
    "S0": ("F1-A", "F1", False, "F1-A"),
    "F1-B": ("F1-B", "F1", False, "F1-B"),
    "S13": ("F1-B", "F1", False, "F1-B"),
    "F1-C": ("F1-C", "F1", False, "F1-C"),
    "HERO_STAT": ("F1-C", "F1", False, "F1-C:HERO"),
    "HERO STAT": ("F1-C", "F1", False, "F1-C:HERO"),
    "HERO": ("F1-C", "F1", False, "F1-C:HERO"),
    "S14": ("F1-C", "F1", False, "F1-C:S14"),
    "F2-A": ("F2-A", "F2", False, "F2-A"),
    "S1": ("F2-A", "F2", False, "F2-A:S1"),
    "S2": ("F2-A", "F2", False, "F2-A:S2"),
    "F2-B": ("F2-B", "F2", False, "F2-B"),
    "S8": ("F2-B", "F2", False, "F2-B"),
    "F2-C": ("F2-C", "F2", True, "F2-C"),
    "S9": ("F2-C", "F2", True, "F2-C"),
    "F3-A": ("F3-A", "F3", False, "F3-A"),
    "S3": ("F3-A", "F3", False, "F3-A:S3"),
    "S12": ("F3-A", "F3", False, "F3-A:S12"),
    "F3-B": ("F3-B", "F3", True, "F3-B"),
    "S4": ("F3-B", "F3", True, "F3-B"),
    "F4-A": ("F4-A", "F4", False, "F4-A"),
    "S5": ("F4-A", "F4", False, "F4-A"),
    "F4-B": ("F4-B", "F4", False, "F4-B"),
    "S11": ("F4-B", "F4", False, "F4-B"),
    "APPENDIX": ("F4-B", "F4", False, "F4-B"),
    "F5-A": ("F5-A", "F5", False, "F5-A"),
    "S7": ("F5-A", "F5", False, "F5-A"),
    "S7-A": ("F5-A", "F5", False, "F5-A"),
    "S7-B": ("F5-A", "F5", False, "F5-A"),
    "S7-C": ("F5-A", "F5", False, "F5-A"),
    "S7-D": ("F5-A", "F5", False, "F5-A"),
    "F5-B": ("F5-B", "F5", False, "F5-B"),
    "S10": ("F5-B", "F5", False, "F5-B"),
    "F5-C": ("F5-C", "F5", True, "F5-C"),
    "S6": ("F5-C", "F5", True, "F5-C"),
}

_BOXED_VARIANT_TOKENS = frozenset({"clean_card", "card", "card_arrow", "boxed", "bento", "bento_grid"})


_UNBOXED_VARIANT_TOKENS = frozenset({"minimal_column", "borderless_centerline", "borderless", "fine_track", "staggered_timeline"})


def _normalize_layout_entry(entry: object) -> dict[str, object]:
    """Normalize a layout code string or layout dict into canonical `(canonical_id, family_group, boxed, adj_key)`."""
    explicit_boxed: bool | None = None
    variant = ""
    if isinstance(entry, dict):
        raw_code = str(entry.get("family_id", entry.get("layout", entry.get("code", "")))).strip()
        variant = str(entry.get("variant", entry.get("card_style", entry.get("layout_style", "")))).strip().lower()
        if "boxed" in entry and entry["boxed"] is not None:
            explicit_boxed = bool(entry["boxed"])
        elif "borderless" in entry and entry["borderless"] is not None:
            explicit_boxed = not bool(entry["borderless"])
    else:
        raw_str = str(entry or "").strip()
        if ":" in raw_str:
            raw_code, variant = [p.strip() for p in raw_str.split(":", 1)]
            variant = variant.lower()
        else:
            raw_code = raw_str

    code_upper = raw_code.upper().replace("_", "-")
    if code_upper not in _CANONICAL_LAYOUT_MAP:
        alt_upper = raw_code.upper()
        info = _CANONICAL_LAYOUT_MAP.get(alt_upper)
    else:
        info = _CANONICAL_LAYOUT_MAP[code_upper]

    if info is None:
        canonical_id = code_upper
        family_group = code_upper.split("-")[0] if "-" in code_upper else code_upper
        default_boxed = False
        adj_key = code_upper
    else:
        canonical_id, family_group, default_boxed, adj_key = info

    if explicit_boxed is not None:
        is_boxed = explicit_boxed
    elif variant in _BOXED_VARIANT_TOKENS:
        is_boxed = True
    elif variant in _UNBOXED_VARIANT_TOKENS:
        is_boxed = False
    else:
        is_boxed = default_boxed

    return {
        "raw": str(entry),
        "canonical_id": canonical_id,
        "family_group": family_group,
        "boxed": is_boxed,
        "adj_key": adj_key,
        "variant": variant,
    }


def recommend_layout_family(
    slide_copy_spec: dict[str, object],
    target_body_pt: float = 13.0,
    prev_layout: str | None = None,
    recent_families: Sequence[str] | None = None,
    boxed_ratio_so_far: float = 0.0,
) -> dict[str, object]:
    """
    Two-Stage Semantic-to-Layout Router (`兩段式語義自動配框架`):
    - Stage 1 (Copy Logic -> Layout Family): inspects semantic intent and copy structure in `slide_copy_spec`.
    - Stage 2 (Physical Constraints & Rhythm): applies DISCAS high-font guardrails (`target_body_pt >= 16.0pt`),
      4–5 milestone staggered timeline routing, boxed-ratio steering (`<= 0.40`), and adjacent anti-collision.
    Returns `{"family_id", "family_group", "variant", "is_boxed", "rationale"}`.
    """
    spec = slide_copy_spec if isinstance(slide_copy_spec, dict) else {}
    role = str(spec.get("role", spec.get("intent", spec.get("semantic_type", "")))).strip().lower()
    body_pt = max(MIN_CONTENT_FONT_PT, float(target_body_pt))
    high_font = body_pt >= 16.0
    avoid_boxed = float(boxed_ratio_so_far) >= 0.34

    prev_canon = _normalize_layout_entry(prev_layout)["canonical_id"] if prev_layout else None
    recent_fams = [str(f).upper() for f in (recent_families or [])]

    # Stage 1: Determine primary semantic layout
    family_id = "F2-A"
    variant = "minimal_column"
    is_boxed = False
    rationale = "Parallel narrative points mapped to structured columns."

    if role in ("cover", "closing", "bookend", "title") or spec.get("is_bookend"):
        family_id, variant, is_boxed = "F1-A", "bookend", False
        rationale = "Opening or peak-end closing slide locked to F1-A bookend."
    elif role in ("section", "divider", "section_divider", "transition") or spec.get("section_num") is not None:
        family_id, variant, is_boxed = "F1-B", "section_divider", False
        rationale = "Act/chapter breathing divider mapped to F1-B minimal section divider."
    elif role in ("quote", "manifesto", "thesis") or spec.get("quote"):
        family_id, variant, is_boxed = "F1-C", "quote_manifesto", False
        rationale = "Single high-impact thesis statement mapped to F1-C quote manifesto."
    elif role in ("hero_stat", "big_number", "spotlight_stat") or spec.get("stat_value"):
        family_id, variant, is_boxed = "F1-C", "big_number", False
        rationale = "Single decisive quantitative stat mapped to F1-C big number spotlight."
    elif spec.get("image_path") or spec.get("has_image") or role in ("chart", "visual", "evidence_chart"):
        family_id, variant, is_boxed = "F5-A", str(spec.get("callout_position", "right")), False
        rationale = "Primary chart/visual evidence paired with unboxed F5-A callouts."
    elif spec.get("formula") or spec.get("has_formula") or role in ("formula", "equation", "law", "anatomy"):
        family_id, variant, is_boxed = "F5-C", "left_right", True
        rationale = "Mathematical formula or governing law mapped to F5-C widescreen anatomy."
    elif spec.get("kpi_items") or role in ("kpi_strip", "kpi_overview", "metrics_summary"):
        family_id, variant, is_boxed = "F5-B", "kpi_strip", False
        rationale = "3–4 quantitative indicators with insights mapped to F5-B top KPI strip."
    elif spec.get("headers") or spec.get("has_table") or role in ("table", "comparison_table", "appendix"):
        family_id, variant, is_boxed = "F4-B", "three_line_table", False
        rationale = "Multi-criterion comparison or appendix reference mapped to F4-B three-line table."
    elif spec.get("quadrants") or role in ("quadrant", "2x2", "matrix"):
        family_id, variant, is_boxed = "F4-A", "borderless", False
        rationale = "Two orthogonal evaluation dimensions mapped to F4-A de-boxed 2x2 matrix."
    elif spec.get("nodes") or role in ("mechanism", "loop", "causal_loop", "architecture"):
        family_id, variant, is_boxed = "F3-B", str(spec.get("topology", "horizontal_chain")), True
        rationale = "3–5 node causal mechanism or feedback loop mapped to F3-B diagram."
    elif spec.get("steps") or role in ("process", "steps", "timeline", "roadmap", "milestones"):
        steps = spec.get("steps") or spec.get("items") or []
        n_steps = len(steps) if isinstance(steps, (list, tuple)) else 3
        family_id = "F3-A"
        if n_steps >= 4:
            variant, is_boxed = "staggered_timeline", False
            rationale = f"{n_steps} sequential milestones routed to F3-A staggered timeline (S12) for wide readable blocks."
        else:
            variant, is_boxed = "fine_track", False
            rationale = f"{n_steps}-step sequential flow routed to F3-A de-boxed horizontal fine track."
    elif spec.get("primary_block") or role in ("bento", "asymmetric", "anchor_and_support"):
        family_id, variant, is_boxed = "F2-C", "bento_grid", True
        rationale = "1 primary anchor + supporting blocks mapped to F2-C asymmetric Bento grid."
    elif role in ("split_rows", "swiss", "categories", "list_expand"):
        family_id, variant, is_boxed = "F2-B", "editorial_split_rows", False
        rationale = "Multi-category horizontal expansion mapped to F2-B Swiss split rows."
    else:
        items = spec.get("items") or spec.get("cards") or []
        n_items = len(items) if isinstance(items, (list, tuple)) else 2
        if n_items >= 4:
            family_id, variant, is_boxed = "F2-B", "editorial_split_rows", False
            rationale = f"{n_items} items routed to F2-B horizontal split rows to avoid narrow columns (Pitfall 1)."
        elif n_items == 2 or role in ("compare", "contrast", "vs", "binary"):
            family_id, variant, is_boxed = "F2-A", "borderless_centerline", False
            rationale = "Binary contrast routed to F2-A borderless centerline columns."
        else:
            family_id, variant, is_boxed = "F2-A", "minimal_column", False
            rationale = "Three-pillar structure routed to F2-A de-boxed minimal columns with oversized numerals."

    # Stage 2: Physical guardrails, boxed-ratio steering & adjacent anti-collision
    if avoid_boxed and is_boxed and family_id == "F2-C":
        family_id, variant, is_boxed = "F2-B", "editorial_split_rows", False
        rationale += " Steered from Bento (F2-C) to unboxed F2-B to stay under <=40% boxed ratio."

    if prev_canon and family_id == prev_canon and family_id != "F1-A":
        fallbacks: dict[str, tuple[str, str, bool]] = {
            "F1-C": ("F5-B", "kpi_strip", False),
            "F2-A": ("F2-B", "editorial_split_rows", False),
            "F2-B": ("F2-A", "minimal_column" if high_font else "borderless_centerline", False),
            "F2-C": ("F2-B", "editorial_split_rows", False),
            "F3-A": ("F2-B", "editorial_split_rows", False),
            "F3-B": ("F3-A", "fine_track", False),
            "F4-A": ("F4-B", "three_line_table", False),
            "F4-B": ("F2-B", "editorial_split_rows", False),
            "F5-A": ("F5-B", "kpi_strip", False),
            "F5-B": ("F2-B", "editorial_split_rows", False),
            "F5-C": ("F2-B", "editorial_split_rows", False),
        }
        if family_id in fallbacks:
            fb_id, fb_var, fb_box = fallbacks[family_id]
            rationale += f" Switched from {family_id} to {fb_id} to avoid adjacent collision with previous slide."
            family_id, variant, is_boxed = fb_id, fb_var, fb_box

    family_group = family_id.split("-")[0]
    if len(recent_fams) >= 2 and recent_fams[-1] == family_group and recent_fams[-2] == family_group:
        rationale += f" Note: family {family_group} used in 2 preceding slides; verify deck-level <=40% family balance."

    return {
        "family_id": family_id,
        "family_group": family_group,
        "variant": variant,
        "is_boxed": is_boxed,
        "rationale": rationale,
    }


def validate_layout_sequence(
    layouts: Sequence[object],
    require_bookends: bool = True,
    min_distinct: int = 5,
    max_boxed_ratio: float = 0.40,
    max_family_ratio: float = 0.40,
) -> bool:
    """
    Enforce Phase 2 Format C Storyboard Anti-Collision & Rhythm Guardrails:
    - Bidirectionally normalizes both new family codes (`F1-A`..`F5-C`) and legacy codes (`S0`..`S14`, `Hero Stat`).
    1. Bookend Rule (`require_bookends=True`, `len >= 3`): Slide 1 and main closing slide must be `F1-A` (`S0`);
       optional trailing `F4-B`/`S11`/`Appendix` reference slides are allowed after the main closing `F1-A`.
    2. Adjacent Non-Repetition: consecutive slides must not repeat the same layout (preserving legacy `S1` vs `S2` distinction).
    3. Diversity Floor (`min_distinct=5`): scales cleanly for short decks (`< 6` slides).
    4. Boxed Ratio Guardrail (`max_boxed_ratio=0.40`): prevents box-heavy decks (`>= 4` slides).
    5. Single Family Cap (`max_family_ratio=0.40`): prevents over-reliance on any one family (`>= 6` slides).
    Raises `ValueError` on violation; returns `True` when valid.
    """
    parsed = [_normalize_layout_entry(x) for x in layouts]
    n_slides = len(parsed)
    if n_slides == 0:
        raise ValueError("Layout sequence cannot be empty.")

    if require_bookends and n_slides >= 3:
        if parsed[0]["canonical_id"] != "F1-A":
            raise ValueError(
                f"Mandatory Bookend Rule violated: Slide 1 ({parsed[0]['raw']}) must be 'F1-A' / 'S0'."
            )
        # Allow optional trailing Appendix (`F4-B` / `S11`) slides placed after the main closing bookend
        closing_idx = n_slides - 1
        while closing_idx > 1 and parsed[closing_idx]["canonical_id"] == "F4-B":
            closing_idx -= 1
        if parsed[closing_idx]["canonical_id"] != "F1-A":
            raise ValueError(
                f"Mandatory Bookend Rule violated: Main closing slide #{closing_idx + 1} ({parsed[closing_idx]['raw']}) "
                "must be 'F1-A' / 'S0' (trailing F4-B/S11 Appendix slides are allowed after closing)."
            )
        for mid_idx in range(1, closing_idx):
            if parsed[mid_idx]["canonical_id"] == "F1-A":
                raise ValueError(
                    f"Slide {mid_idx + 1} uses '{parsed[mid_idx]['raw']}' (F1-A/S0), which is reserved exclusively for Cover and Closing bookends."
                )

    for i in range(n_slides - 1):
        a = parsed[i]
        b = parsed[i + 1]
        # Collide if exact adjacency key matches OR if either uses the generic canonical code (e.g., F2-A -> S1 or F2-A -> F2-A)
        same_canon = a["canonical_id"] == b["canonical_id"]
        same_adj = a["adj_key"] == b["adj_key"]
        either_generic = (a["adj_key"] == a["canonical_id"]) or (b["adj_key"] == b["canonical_id"])
        if same_adj or (same_canon and either_generic):
            raise ValueError(
                f"Adjacent Layout Collision at Slide {i + 1} -> Slide {i + 2}: "
                f"'{a['raw']}' ({a['canonical_id']}) followed by '{b['raw']}' ({b['canonical_id']}). "
                f"Switch Slide {i + 2} to a distinct layout via `recommend_layout_family()`."
            )

    distinct_canons = {str(p["canonical_id"]) for p in parsed}
    distinct_count = len(distinct_canons)
    max_possible = max(1, (n_slides - 1) if (require_bookends and n_slides >= 3) else n_slides)
    required_distinct = min(int(min_distinct), max_possible)
    if distinct_count < required_distinct:
        raise ValueError(
            f"Insufficient layout diversity: found {distinct_count} distinct layouts ({sorted(distinct_canons)}) "
            f"across {n_slides} slides, but at least {required_distinct} are required to prevent visual habituation."
        )

    if max_boxed_ratio is not None and n_slides >= 4:
        boxed_count = sum(1 for p in parsed if bool(p["boxed"]))
        boxed_ratio = boxed_count / float(n_slides)
        if boxed_ratio > float(max_boxed_ratio) + 1e-9:
            raise ValueError(
                f"Boxed slide ratio {boxed_ratio:.1%} ({boxed_count}/{n_slides}) exceeds max_boxed_ratio "
                f"{float(max_boxed_ratio):.0%}. Convert excess boxed cards to unboxed layouts "
                "(minimal_column / borderless_centerline / F2-B / F3-A fine_track / F4-A borderless)."
            )

    if max_family_ratio is not None and n_slides >= 6:
        fam_counts: dict[str, int] = {}
        for p in parsed:
            fg = str(p["family_group"])
            fam_counts[fg] = fam_counts.get(fg, 0) + 1
        for fg, cnt in fam_counts.items():
            ratio = cnt / float(n_slides)
            if ratio > float(max_family_ratio) + 1e-9:
                raise ValueError(
                    f"Single family '{fg}' occupies {ratio:.1%} ({cnt}/{n_slides}) of slides, "
                    f"exceeding max_family_ratio {float(max_family_ratio):.0%}. Diversify across F1–F5."
                )

    return True


# -------------------------------------------------------------------------
# Step 5: F4 Spec-Driven Deterministic Rendering Layer (`02c_slide_spec_lock.json`)
#   - Standard 4-Zone Schema (`deck_meta`, `design_tokens`, `slides[i].copy`, `slides[i].layout`)
#   - `export_step4a_alignment_preview(spec_json_or_path) -> str`
#   - `render_deck_from_spec(spec_json_or_path, output_pptx_path, ...) -> str`
#   - `check_copy_fidelity(spec_json_or_path, pptx_path) -> dict[str, object]`
# -------------------------------------------------------------------------

SLIDE_SPEC_LOCK_SCHEMA_VERSION = "1.0"

SLIDE_SPEC_LOCK_SCHEMA: dict[str, object] = {
    "schema_version": SLIDE_SPEC_LOCK_SCHEMA_VERSION,
    "description": (
        "Standard 4-zone Format C deterministic slide specification (`02c_slide_spec_lock.json`). "
        "Separates Step 3 frozen human-approved copy (`slides[i].copy`, STRICTLY READ-ONLY in Step 4B) "
        "from Step 4A locked geometry (`slides[i].layout`)."
    ),
    "zones": {
        "deck_meta": {
            "required": False,
            "fields": [
                "title",
                "viewing_context",
                "distance_m",
                "screen_height_m",
                "min_font_pt",
                "design_mode",
                "mode3_tier",
                "art_direction_dna",
                "writing_style_id",
            ],
        },
        "design_tokens": {
            "required": False,
            "fields": [
                "min_font_pt",
                "target_body_pt",
                "doc_theme_id",
                "topic_or_hex",
                "theme_mode",
                "theme_overrides",
                "typography",
            ],
        },
        "slides[i].copy": {
            "required": True,
            "read_only": True,
            "fields": [
                "chapter_pill",
                "right_badge",
                "headline",
                "subtitle",
                "items",
                "zone3_takeaway",
                "speaker_notes",
                "key_numbers",
            ],
            "layout_extensions": [
                "badge_text",
                "footer_text",
                "kpi_cards",
                "section_num",
                "section_title",
                "stat_value",
                "stat_label",
                "context_points",
                "quote",
                "attribution",
                "cards",
                "rows",
                "primary_block",
                "secondary_blocks",
                "steps",
                "nodes",
                "edges",
                "callouts",
                "callout_heading",
                "quadrants",
                "x_axis_label",
                "y_axis_label",
                "headers",
                "table",
                "visual_caption",
                "kpi_items",
                "insight_blocks",
                "focal_title",
                "focal_formula",
                "focal_note",
                "breakdown_items",
            ],
        },
        "slides[i].layout": {
            "required": True,
            "fields": [
                "family_id",
                "variant",
                "spotlight_idx",
                "spotlight_col",
                "include_zone3",
                "zone3_style",
                "visual_asset",
                "geometric_accent",
                "use_omml",
                "borderless",
                "left_ratio",
                "visual_ratio",
                "focal_ratio",
                "callout_position",
                "topology",
                "width_ratios",
                "col_widths",
                "body_font_pt",
                "show_divider",
            ],
        },
    },
}

LAYOUT_FAMILY_LABELS: dict[str, tuple[str, str]] = {
    "F1-A": ("家族 1｜破題與節奏", "封面／封底"),
    "F1-B": ("家族 1｜破題與節奏", "極簡章節過場頁"),
    "F1-C": ("家族 1｜破題與節奏", "巨幅焦點宣言頁"),
    "F2-A": ("家族 2｜觀點並陳", "並列／對比欄"),
    "F2-B": ("家族 2｜觀點並陳", "瑞士網格左標右展"),
    "F2-C": ("家族 2｜觀點並陳", "不對稱便當盒 Bento"),
    "F3-A": ("家族 3｜時序與機制", "流程軌道／交錯時間軸"),
    "F3-B": ("家族 3｜時序與機制", "精簡機制架構圖"),
    "F4-A": ("家族 4｜比較與分類", "2×2 正交四象限"),
    "F4-B": ("家族 4｜比較與分類", "極簡三線比較表"),
    "F5-A": ("家族 5｜實證與解剖", "主圖＋無框導讀"),
    "F5-B": ("家族 5｜實證與解剖", "頂部指標橫帶＋洞察"),
    "F5-C": ("家族 5｜實證與解剖", "焦點公式／指標解剖"),
}

_DRAFT_PLACEHOLDER_RE = re.compile(r"(?<![A-Za-z])(?:TBD|TODO|FIXME)(?![A-Za-z])", re.IGNORECASE)


_FIDELITY_NUM_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9.])(?:[$£€¥])?[+-]?\d+(?:,\d{3})*(?:\.\d+)?(?:%|％|‰)?"
)


_INLINE_BOLD_STRIP_RE = re.compile(r"\*\*((?:(?!\*\*).)+)\*\*")


_SVG_HTML_EXTS = frozenset({".svg", ".html", ".htm"})


def _load_spec_lock(spec_json_or_path: dict[str, object] | str | Path) -> tuple[dict[str, object], Path | None]:
    """
    Load `02c_slide_spec_lock.json` from a file path or deep-copy an in-memory dict so caller data
    (especially frozen `slides[i].copy`) is guaranteed 100% read-only and never mutated.
    """
    if isinstance(spec_json_or_path, dict):
        return copy.deepcopy(spec_json_or_path), None
    if isinstance(spec_json_or_path, (str, Path)):
        p = Path(spec_json_or_path).resolve()
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(f"Slide spec lock file not found: {p}")
        raw = json.loads(p.read_text(encoding="utf-8-sig"))
        if not isinstance(raw, dict):
            raise ValueError(f"Slide spec lock root must be a JSON object; got {type(raw).__name__}.")
        return raw, p.parent
    raise TypeError(
        f"spec_json_or_path must be a dict or path (str/Path); got {type(spec_json_or_path).__name__}."
    )


def _validate_spec_lock_structure(spec: dict[str, object], *, require_layout: bool = True) -> list[dict[str, object]]:
    """Validate the 4-zone structure of `02c_slide_spec_lock.json` and return its slides list."""
    if not isinstance(spec, dict):
        raise ValueError("Slide spec must be a JSON object (dict).")
    for zone_key in ("deck_meta", "design_tokens"):
        if zone_key in spec and spec[zone_key] is not None and not isinstance(spec[zone_key], dict):
            raise ValueError(f"Spec zone '{zone_key}' must be an object (dict) when provided.")
    slides = spec.get("slides")
    if not isinstance(slides, list) or len(slides) == 0:
        raise ValueError("Spec must contain a non-empty 'slides' array.")
    for idx, sl in enumerate(slides, start=1):
        if not isinstance(sl, dict):
            raise ValueError(f"Slide #{idx} entry must be a dict.")
        if not isinstance(sl.get("copy"), dict):
            raise ValueError(f"Slide #{idx} is missing required read-only 'copy' dict zone.")
        if require_layout:
            lay = sl.get("layout")
            if not isinstance(lay, dict) or not str(lay.get("family_id", lay.get("layout", lay.get("code", "")))).strip():
                raise ValueError(f"Slide #{idx} is missing required 'layout.family_id' specification.")
        elif "layout" in sl and sl["layout"] is not None and not isinstance(sl["layout"], dict):
            raise ValueError(f"Slide #{idx} 'layout' must be a dict when provided.")
    return slides


def _resolve_spec_design_tokens(spec: dict[str, object]) -> dict[str, object]:
    """Build unified design tokens from `deck_meta` + `design_tokens` (including Mode 3 CIELAB dynamic themes)."""
    deck_meta = spec.get("deck_meta") if isinstance(spec.get("deck_meta"), dict) else {}
    dt_cfg = spec.get("design_tokens") if isinstance(spec.get("design_tokens"), dict) else {}
    dna = deck_meta.get("art_direction_dna") or deck_meta.get("topic_art_direction_dna") or {}
    if not isinstance(dna, dict):
        dna = {}

    min_font_raw = dt_cfg.get("min_font_pt", deck_meta.get("min_font_pt", MIN_CONTENT_FONT_PT))
    min_font_pt = float(min_font_raw) if min_font_raw is not None else MIN_CONTENT_FONT_PT

    dist_raw = dt_cfg.get("distance_m", deck_meta.get("distance_m"))
    screen_raw = dt_cfg.get("screen_height_m", deck_meta.get("screen_height_m"))
    distance_m = float(dist_raw) if dist_raw is not None else None
    screen_height_m = float(screen_raw) if screen_raw is not None else None
    if (distance_m is None) != (screen_height_m is None):
        distance_m = None
        screen_height_m = None

    target_body_raw = dt_cfg.get("target_body_pt", deck_meta.get("target_body_pt"))
    target_body_pt = float(target_body_raw) if target_body_raw is not None else None

    doc_theme_id = dt_cfg.get("doc_theme_id") or deck_meta.get("doc_theme_id")
    topic_or_hex = (
        dt_cfg.get("topic_or_hex")
        or dt_cfg.get("dynamic_topic")
        or dna.get("topic_or_hex")
        or dna.get("seed_hex")
        or deck_meta.get("topic_or_hex")
    )
    theme_mode = str(
        dt_cfg.get("theme_mode")
        or dna.get("theme_mode")
        or deck_meta.get("theme_mode")
        or "light_classroom"
    ).strip()

    theme_overrides: dict[str, str] = {}
    if isinstance(dt_cfg.get("theme"), dict):
        for k, v in dt_cfg["theme"].items():  # type: ignore[union-attr]
            if v is not None:
                theme_overrides[str(k)] = str(v)
    if isinstance(dt_cfg.get("theme_overrides"), dict):
        for k, v in dt_cfg["theme_overrides"].items():  # type: ignore[union-attr]
            if v is not None:
                theme_overrides[str(k)] = str(v)

    return build_slide_design_tokens(
        min_font_pt=min_font_pt,
        target_body_pt=target_body_pt,
        doc_theme_id=str(doc_theme_id) if doc_theme_id else None,
        theme_overrides=theme_overrides or None,
        distance_m=distance_m,
        screen_height_m=screen_height_m,
        topic_or_hex=topic_or_hex,
        theme_mode=theme_mode,
    )


def _should_render_zone3(copy_zone: dict[str, object], layout_zone: dict[str, object], canonical_id: str) -> bool:
    """SSOT decision on whether `zone3_takeaway` (or `footer_text` on F1-A) should be rendered & fidelity-checked."""
    inc = layout_zone.get("include_zone3")
    takeaway = _first_non_empty_str(copy_zone, "zone3_takeaway")
    if canonical_id == "F1-A":
        footer = _first_non_empty_str(copy_zone, "footer_text")
        if footer:
            return True
        return bool(takeaway) and (inc is not False)
    if canonical_id == "F1-B":
        return (inc is True) and bool(takeaway)
    if inc is False:
        return False
    return bool(takeaway)


def _resolve_visual_asset_info(
    layout_zone: dict[str, object],
    copy_zone: dict[str, object],
    base_dir: Path | None = None,
) -> dict[str, object]:
    """Parse `layout.visual_asset` (string or dict) without mutating input spec."""
    raw = layout_zone.get("visual_asset")
    if raw is None and copy_zone.get("image_path"):
        raw = copy_zone.get("image_path")

    info: dict[str, object] = {
        "raw_path": "",
        "resolved_path": None,
        "kind": "",
        "mode3_tier": None,
        "is_slide_variant": False,
        "is_svg_or_html": False,
        "placement": "visual_zone",
        "width_px": 1200,
        "height_px": 800,
        "scale_factor": 3.0,
        "dpi": 300,
        "transparent": True,
        "engine": "auto",
        "out_png_path": None,
        "rect_in": None,
    }
    if not raw:
        return info

    if isinstance(raw, (str, Path)):
        raw_path = str(raw).strip()
    elif isinstance(raw, dict):
        raw_path = _first_non_empty_str(raw, "path", "image_path", "src", "file")
        info["kind"] = _first_non_empty_str(raw, "kind", "type")
        if raw.get("mode3_tier") is not None:
            info["mode3_tier"] = raw.get("mode3_tier")
        elif raw.get("tier") is not None:
            info["mode3_tier"] = raw.get("tier")
        if raw.get("is_slide_variant") is not None:
            info["is_slide_variant"] = bool(raw.get("is_slide_variant"))
        if raw.get("placement") or raw.get("position"):
            info["placement"] = str(raw.get("placement") or raw.get("position")).strip().lower()
        for num_k in ("width_px", "height_px", "dpi"):
            if raw.get(num_k) is not None:
                info[num_k] = int(raw[num_k])  # type: ignore[arg-type]
        if raw.get("scale_factor") is not None:
            info["scale_factor"] = float(raw["scale_factor"])  # type: ignore[arg-type]
        if raw.get("transparent") is not None:
            info["transparent"] = bool(raw["transparent"])
        if raw.get("engine"):
            info["engine"] = str(raw["engine"])
        if raw.get("out_png_path"):
            info["out_png_path"] = str(raw["out_png_path"])
        if all(raw.get(rk) is not None for rk in ("left_in", "top_in", "width_in", "height_in")):
            info["rect_in"] = (
                float(raw["left_in"]),  # type: ignore[arg-type]
                float(raw["top_in"]),  # type: ignore[arg-type]
                float(raw["width_in"]),  # type: ignore[arg-type]
                float(raw["height_in"]),  # type: ignore[arg-type]
            )
    else:
        return info

    info["raw_path"] = raw_path
    if not raw_path:
        return info

    p_obj = Path(raw_path)
    low_name = p_obj.name.lower()
    if low_name.endswith("_slide.png") or "_slide." in low_name:
        info["is_slide_variant"] = True
    if p_obj.suffix.lower() in _SVG_HTML_EXTS:
        info["is_svg_or_html"] = True
        if info["mode3_tier"] is None:
            info["mode3_tier"] = 3

    resolved: Path | None = None
    if p_obj.is_absolute():
        resolved = p_obj
    else:
        candidates = []
        if base_dir is not None:
            candidates.append((base_dir / p_obj).resolve())
        candidates.append((Path.cwd() / p_obj).resolve())
        for cand in candidates:
            if cand.exists():
                resolved = cand
                break
        if resolved is None:
            resolved = candidates[0]
    info["resolved_path"] = resolved
    return info


def _materialize_visual_asset_png(
    asset_info: dict[str, object],
    temp_files: list[Path],
    base_dir: Path | None = None,
) -> str | None:
    """Resolve a PNG path for embedding, rendering `.svg`/`.html` via `render_svg_to_png_300dpi()` for Tier 3."""
    resolved = asset_info.get("resolved_path")
    if not isinstance(resolved, Path):
        return None
    if not resolved.exists():
        raise FileNotFoundError(f"Spec visual_asset not found: {resolved}")

    if bool(asset_info.get("is_svg_or_html")):
        out_raw = asset_info.get("out_png_path")
        if out_raw:
            out_p = Path(str(out_raw))
            if not out_p.is_absolute() and base_dir is not None:
                out_p = (base_dir / out_p).resolve()
            else:
                out_p = out_p.resolve()
        else:
            fd, tmp_name = tempfile.mkstemp(prefix="_pptx_tier3_", suffix=".png")
            os.close(fd)
            out_p = Path(tmp_name)
            temp_files.append(out_p)
        return render_svg_to_png_300dpi(
            resolved,
            out_p,
            width_px=int(asset_info.get("width_px", 1200)),  # type: ignore[arg-type]
            height_px=int(asset_info.get("height_px", 800)),  # type: ignore[arg-type]
            engine=str(asset_info.get("engine", "auto")),
            scale_factor=float(asset_info.get("scale_factor", 3.0)),  # type: ignore[arg-type]
            dpi=int(asset_info.get("dpi", 300)),  # type: ignore[arg-type]
            transparent=bool(asset_info.get("transparent", True)),
        )

    return str(resolved)


def _place_overlay_picture(slide, png_path: str, asset_info: dict[str, object], *, default_behind: bool = True) -> None:
    """Embed a Mode 3 Tier 2/3 visual asset on bookend/divider/custom slides without colliding with text."""
    rect_in = asset_info.get("rect_in")
    placement = str(asset_info.get("placement") or "").strip().lower()
    behind = (placement == "background") or (default_behind and rect_in is None and placement not in ("right", "left"))

    if isinstance(rect_in, tuple) and len(rect_in) == 4:
        vx, vy, vw, vh = rect_in
    elif placement == "right":
        vx, vy, vw, vh = 8.40, 0.90, 4.43, 5.70
    elif placement == "left":
        vx, vy, vw, vh = 0.50, 0.90, 4.43, 5.70
    else:
        vx, vy, vw, vh = 0.0, 0.0, 13.333, 7.50

    px_w, px_h = _read_image_pixel_size(Path(png_path))
    img_ar = float(px_w) / max(1.0, float(px_h))
    box_ar = vw / max(0.1, vh)
    if img_ar >= box_ar:
        pw = vw
        ph = vw / img_ar
    else:
        ph = vh
        pw = vh * img_ar
    px = vx + (vw - pw) / 2.0
    py = vy + (vh - ph) / 2.0

    pic = slide.shapes.add_picture(png_path, Inches(px), Inches(py), width=Inches(pw), height=Inches(ph))
    if behind:
        with suppress(AttributeError, ValueError, TypeError):
            sp_tree = slide.shapes._spTree
            sp_tree.remove(pic._element)
            # Insert immediately after nvGrpSpPr + grpSpPr so the image renders behind all text shapes
            sp_tree.insert(2, pic._element)


def _apply_tier1_geometric_accent(slide, layout_zone: dict[str, object], tokens: dict[str, object]) -> None:
    """Apply optional Mode 3 Tier 1 native geometric accent motif specified on a slide."""
    accent_spec = layout_zone.get("geometric_accent")
    if accent_spec is None:
        accent_spec = layout_zone.get("tier1_motif")
    if not accent_spec:
        return
    if isinstance(accent_spec, str):
        draw_theme_geometric_accent(slide, motif_type=accent_spec, tokens=tokens)
    elif isinstance(accent_spec, dict):
        motif_type = _first_non_empty_str(accent_spec, "motif_type", "type", "motif", default="diagonal_wedge")
        extra_kw = {k: v for k, v in accent_spec.items() if k not in ("motif_type", "type", "motif")}
        draw_theme_geometric_accent(slide, motif_type=motif_type, tokens=tokens, **extra_kw)


def _strip_inline_bold(text: str) -> str:
    """Strip valid `**bold**` markers the same way `_populate_paragraph_runs()` renders them."""
    return _INLINE_BOLD_STRIP_RE.sub(r"\1", str(text or ""))


def _escape_md_cell(text: str, max_len: int | None = None) -> str:
    """Escape a string cleanly for single-row GitHub-flavored Markdown tables."""
    clean = re.sub(r"\s+", " ", _strip_inline_bold(str(text or "")).strip())
    if max_len is not None and len(clean) > max_len:
        clean = clean[: max(1, max_len - 1)].rstrip() + "…"
    return clean.replace("|", "\\|")


def _summarize_slide_copy_skeleton(
    copy_zone: dict[str, object],
    layout_zone: dict[str, object],
    canonical_id: str,
) -> str:
    """Build a concise human-readable skeleton of slide copy items with `★` spotlight indicator for Step 4A."""
    spot_idx = layout_zone.get("spotlight_idx")
    spot_col = layout_zone.get("spotlight_col")

    def _fmt_entry(idx: int, raw: object, is_spot: bool) -> str:
        prefix = "★" if is_spot else "•"
        if isinstance(raw, dict):
            val = _first_non_empty_str(raw, "value", "stat", "metric", "kpi")
            title = _first_non_empty_str(raw, "title", "heading", "label", "name", "lead")
            sub = _first_non_empty_str(raw, "body", "desc", "detail", "note", "text", "subtitle")
            parts = [p for p in (val, title) if p]
            head = " ".join(parts) if parts else sub
            if not head:
                sub_items = _extract_lead_body_items(raw)
                head = sub_items[0][0] or sub_items[0][1] if sub_items else f"項目 {idx + 1}"
            return f"{prefix} {_escape_md_cell(head, 34)}"
        ld, bd = _parse_lead_body_item(raw)
        txt = ld or bd or f"項目 {idx + 1}"
        return f"{prefix} {_escape_md_cell(txt, 34)}"

    lines: list[str] = []
    if canonical_id == "F1-A":
        kpis = copy_zone.get("kpi_cards") or copy_zone.get("items") or []
        if isinstance(kpis, list) and kpis:
            for i, it in enumerate(kpis[:3]):
                lines.append(_fmt_entry(i, it, is_spot=(spot_idx == i) or (isinstance(it, dict) and bool(it.get("is_spotlight")))))
        elif copy_zone.get("subtitle"):
            lines.append(f"副標：{_escape_md_cell(str(copy_zone['subtitle']), 46)}")
        else:
            lines.append("封面／峰終主視覺定錨")
    elif canonical_id == "F1-B":
        sec_num = _first_non_empty_str(copy_zone, "section_num", "chapter_pill")
        sub = _first_non_empty_str(copy_zone, "subtitle")
        if sec_num:
            sec_disp = f"{int(sec_num):02d}" if sec_num.isdigit() else sec_num
            lines.append(f"章節序號：`{sec_disp}`")
        if sub:
            lines.append(f"引導語：{_escape_md_cell(sub, 44)}")
        if not lines:
            lines.append("高留白章節過場換氣")
    elif canonical_id == "F1-C":
        val = _first_non_empty_str(copy_zone, "stat_value", "quote", "manifesto")
        lbl = _first_non_empty_str(copy_zone, "stat_label", "attribution")
        if val:
            lines.append(f"★ 焦點：{_escape_md_cell(val, 38)}")
        if lbl:
            lines.append(f"說明：{_escape_md_cell(lbl, 38)}")
        pts = copy_zone.get("context_points") or copy_zone.get("items") or []
        if isinstance(pts, list):
            for i, it in enumerate(pts[:3]):
                lines.append(_fmt_entry(i, it, is_spot=(spot_idx == i)))
    elif canonical_id == "F2-C":
        pri = copy_zone.get("primary_block")
        secs = copy_zone.get("secondary_blocks")
        if pri is None and isinstance(copy_zone.get("items"), list) and copy_zone["items"]:
            pri = copy_zone["items"][0]
            secs = copy_zone["items"][1:]
        if pri is not None:
            eff_spot = 0 if spot_idx is None else spot_idx
            lines.append(_fmt_entry(0, pri, is_spot=(eff_spot == 0)))
        if isinstance(secs, list):
            eff_spot = 0 if spot_idx is None else spot_idx
            for i, sb in enumerate(secs[:3], start=1):
                lines.append(_fmt_entry(i, sb, is_spot=(eff_spot == i)))
    elif canonical_id == "F4-B":
        tbl = copy_zone.get("table") if isinstance(copy_zone.get("table"), dict) else {}
        hdrs = copy_zone.get("headers") or tbl.get("headers") or []
        rows = copy_zone.get("rows") or tbl.get("rows") or []
        eff_col = spot_col if spot_col is not None else spot_idx
        if isinstance(hdrs, list) and hdrs:
            fmt_hdrs = [
                f"★{_escape_md_cell(str(h), 16)}" if (eff_col == c_i) else _escape_md_cell(str(h), 16)
                for c_i, h in enumerate(hdrs)
            ]
            lines.append("欄：" + " / ".join(fmt_hdrs))
        if isinstance(rows, list):
            lines.append(f"共 {len(rows)} 列對比資料")
    elif canonical_id == "F5-B":
        kpis = copy_zone.get("kpi_items") or copy_zone.get("kpis") or []
        ins = copy_zone.get("insight_blocks") or copy_zone.get("insights") or (copy_zone.get("items") if kpis else [])
        eff_spot = 0 if spot_idx is None else spot_idx
        if isinstance(kpis, list):
            for i, k in enumerate(kpis[:4]):
                lines.append(_fmt_entry(i, k, is_spot=(eff_spot == i)))
        if isinstance(ins, list) and ins:
            lines.append(f"下方洞察：{len(ins)} 欄")
    elif canonical_id == "F5-C":
        ft = _first_non_empty_str(copy_zone, "focal_title")
        ff = _first_non_empty_str(copy_zone, "focal_formula", "formula")
        if ft or ff:
            lines.append(f"★ 焦點：{_escape_md_cell(ft or ff, 40)}")
        bds = copy_zone.get("breakdown_items") or copy_zone.get("items") or []
        if isinstance(bds, list):
            for i, b in enumerate(bds[:4]):
                lines.append(_fmt_entry(i, b, is_spot=(i == 0)))
    elif canonical_id == "F5-A":
        raw_c_upper = _first_non_empty_str(layout_zone, "family_id", "layout", "code").upper().replace("_", "-")
        c_pos = _first_non_empty_str(layout_zone, "callout_position").lower()
        var_low = str(_normalize_layout_entry(layout_zone).get("variant") or "").strip().lower()
        is_hdr_only = (c_pos == "header_only") or (not c_pos and (var_low == "header_only" or raw_c_upper == "S7-D"))
        c_head = _first_non_empty_str(copy_zone, "callout_heading")
        cs = copy_zone.get("callouts") or copy_zone.get("items") or []
        if is_hdr_only:
            lines.append("全幅純圖（`header_only`）")
            if isinstance(cs, list) and cs:
                lines.append(f"⚠️ `header_only` 將省略 {len(cs)} 項凍結導讀文案")
        else:
            if c_head:
                lines.append(f"導讀題：{_escape_md_cell(c_head, 32)}")
            eff_spot = 0 if spot_idx is None else spot_idx
            if isinstance(cs, list) and cs:
                for i, c in enumerate(cs[:4]):
                    lines.append(_fmt_entry(i, c, is_spot=(eff_spot == i)))
            else:
                lines.append("全幅純圖（`header_only`）")
    else:
        # F2-A, F2-B, F3-A, F3-B, F4-A
        coll = (
            copy_zone.get("cards")
            or copy_zone.get("rows")
            or copy_zone.get("steps")
            or copy_zone.get("nodes")
            or copy_zone.get("quadrants")
            or copy_zone.get("items")
            or []
        )
        if isinstance(coll, list):
            for i, it in enumerate(coll[:5]):
                is_sp = (spot_idx == i) if spot_idx is not None else (isinstance(it, dict) and bool(it.get("is_spotlight")))
                lines.append(_fmt_entry(i, it, is_spot=is_sp))
        if canonical_id == "F3-B" and isinstance(copy_zone.get("callouts"), list) and copy_zone["callouts"]:
            lines.append(f"旁側導讀：{len(copy_zone['callouts'])} 點")

    return "<br>".join(lines) if lines else "—"


def export_step4a_alignment_preview(spec_json_or_path: dict[str, object] | str | Path) -> str:
    """
    [Step 4A] Export a clean, human-readable Markdown slide-by-slide layout & visual asset alignment table
    from `02c_slide_spec_lock.json` (never exposing raw JSON to the user).
    Strictly read-only: never mutates the input spec.
    """
    spec, base_dir = _load_spec_lock(spec_json_or_path)
    slides = _validate_spec_lock_structure(spec, require_layout=False)
    deck_meta = spec.get("deck_meta") if isinstance(spec.get("deck_meta"), dict) else {}
    tokens = _resolve_spec_design_tokens(spec)
    typo = tokens["typography"]  # type: ignore[index]

    dt_cfg = spec.get("design_tokens") if isinstance(spec.get("design_tokens"), dict) else {}
    dna_raw = deck_meta.get("art_direction_dna") or deck_meta.get("topic_art_direction_dna") or {}
    dna = dna_raw if isinstance(dna_raw, dict) else {}

    title = _first_non_empty_str(deck_meta, "title", "project_title", default="Format C 簡報配置對齊表")
    viewing_ctx = _first_non_empty_str(deck_meta, "viewing_context", "context", "scenario", default="自適應簡報")
    dist_m = dt_cfg.get("distance_m", deck_meta.get("distance_m"))
    screen_h = dt_cfg.get("screen_height_m", deck_meta.get("screen_height_m"))
    discas_str = (
        f"D={dist_m}m / H={screen_h}m → 地板 `{tokens['min_font_pt']}pt`"
        if (dist_m is not None and screen_h is not None)
        else f"地板 `{tokens['min_font_pt']}pt`"
    )
    design_mode = deck_meta.get("design_mode", "Mode 1 (rigorous)")
    mode3_tier = deck_meta.get("mode3_tier", deck_meta.get("tier"))
    mode_str = f"{design_mode}" + (f" / Tier {mode3_tier}" if mode3_tier is not None else "")
    topic_seed = (
        dt_cfg.get("topic_or_hex")
        or dt_cfg.get("dynamic_topic")
        or dna.get("topic_or_hex")
        or dna.get("seed_hex")
        or deck_meta.get("topic_or_hex")
    )
    theme_label = (
        f"動態 CIELAB (`{topic_seed}`)"
        if topic_seed
        else f"靜態主題 (`{tokens.get('doc_theme_id') or 'default'}`)"
    )
    style_id = _first_non_empty_str(deck_meta, "writing_style_id", "style_id", default="預設筆風")

    out: list[str] = [
        f"## Step 4A 渲染前逐頁配置與配圖對齊表 — {title}",
        "",
        f"- **觀看情境與 DISCAS**：{viewing_ctx}（{discas_str}；全檔統一基準 `target_body_pt = {tokens['target_body_pt']}pt`，斷言主標 `{typo['headline']}pt`）",
        f"- **總頁數／模式／主題／筆風**：共 `{len(slides)}` 頁｜設計光譜：`{mode_str}`｜配色：{theme_label}｜筆風：`{style_id}`",
    ]
    if dna:
        metaphor = _first_non_empty_str(dna, "core_metaphor", "visual_metaphor", "motif")
        if metaphor:
            out.append(f"- **Topic Art Direction DNA**：{metaphor}")

    out.extend([
        "",
        "| 頁次 | 家族與版型 | 定稿標題 | 文案骨架與 ★聚光燈 | 配圖／模式 3 標記 | Zone 3 |",
        "| :---: | :--- | :--- | :--- | :--- | :--- |",
    ])

    layout_entries: list[dict[str, object]] = []
    total_key_nums = 0
    draft_flags: list[str] = []

    for idx, sl in enumerate(slides, start=1):
        copy_z: dict[str, object] = sl["copy"]  # type: ignore[assignment]
        lay_z: dict[str, object] = sl.get("layout") if isinstance(sl.get("layout"), dict) else {}  # type: ignore[assignment]
        layout_entries.append(lay_z)

        raw_code = _first_non_empty_str(lay_z, "family_id", "layout", "code")
        norm = _normalize_layout_entry(lay_z) if raw_code else {"canonical_id": "待定", "variant": "", "boxed": False, "family_group": "?"}
        canon_id = str(norm["canonical_id"])
        variant = str(norm.get("variant") or "")
        fam_label = LAYOUT_FAMILY_LABELS.get(canon_id, ("未分類", canon_id))[1]
        layout_cell = f"**`{canon_id}`** {fam_label}" + (f"<br>`{variant}`" if variant else "")

        pill = _first_non_empty_str(copy_z, "chapter_pill", "badge_text", "section_num")
        if canon_id == "F1-B" and pill.isdigit():
            pill = f"{int(pill):02d}"
        headline = _first_non_empty_str(copy_z, "headline", "main_title", "section_title", default="(無標題)")
        title_cell = (f"`{_escape_md_cell(pill, 22)}`<br>" if pill else "") + f"**{_escape_md_cell(headline, 44)}**"

        skeleton_cell = _summarize_slide_copy_skeleton(copy_z, lay_z, canon_id)

        # Visual asset & Mode 3 markers
        asset_tags: list[str] = []
        asset_info = _resolve_visual_asset_info(lay_z, copy_z, base_dir=base_dir)
        if asset_info["raw_path"]:
            fname = Path(str(asset_info["raw_path"])).name
            if asset_info["is_svg_or_html"]:
                asset_tags.append(f"`{fname}` [Mode 3 Tier 3 SVG/HTML 300DPI]")
            elif asset_info["is_slide_variant"]:
                asset_tags.append(f"`{fname}` [專用 `*_slide.png`]")
            elif asset_info["mode3_tier"] == 2 or str(asset_info["kind"]).lower() == "tier2_concept":
                asset_tags.append(f"`{fname}` [Mode 3 Tier 2 概念視覺]")
            else:
                asset_tags.append(f"`{fname}`")
        geo_acc = lay_z.get("geometric_accent") or lay_z.get("tier1_motif")
        if geo_acc:
            m_name = geo_acc.get("motif_type", "motif") if isinstance(geo_acc, dict) else str(geo_acc)
            asset_tags.append(f"[Mode 3 Tier 1: `{m_name}`]")
        if bool(lay_z.get("use_omml")) or bool(copy_z.get("use_omml")):
            asset_tags.append("[原生 OMML 公式]")
        asset_cell = "<br>".join(asset_tags) if asset_tags else "— 純原生排版"

        # Zone 3 column
        if _should_render_zone3(copy_z, lay_z, canon_id):
            z3_txt = _first_non_empty_str(copy_z, "footer_text", "zone3_takeaway")
            z3_style = _first_non_empty_str(lay_z, "zone3_style", default="dark_banner" if canon_id != "F1-A" else "footer")
            z3_cell = f"保留 (`{z3_style}`)<br>{_escape_md_cell(z3_txt, 26)}"
        else:
            z3_cell = "省略"

        out.append(f"| S{idx:02d} | {layout_cell} | {title_cell} | {skeleton_cell} | {asset_cell} | {z3_cell} |")

        k_nums = copy_z.get("key_numbers")
        if isinstance(k_nums, list):
            total_key_nums += len([k for k in k_nums if str(k or "").strip()])
        raw_copy_blob = json.dumps(copy_z, ensure_ascii=False)
        if _DRAFT_PLACEHOLDER_RE.search(raw_copy_blob):
            draft_flags.append(f"S{idx:02d}")

    # Pre-render diagnostic footer (non-throwing so user sees exact rhythm status before locking)
    out.append("")
    out.append("### 渲染前節奏與保真預檢摘要")
    has_all_layouts = all(bool(_first_non_empty_str(le, "family_id", "layout", "code")) for le in layout_entries)
    if has_all_layouts:
        parsed_ls = [_normalize_layout_entry(le) for le in layout_entries]
        n_tot = len(parsed_ls)
        boxed_cnt = sum(1 for p in parsed_ls if bool(p["boxed"]))
        distinct_ids = sorted({str(p["canonical_id"]) for p in parsed_ls})
        fam_cnts = Counter(str(p["family_group"]) for p in parsed_ls)
        fam_summary = "、".join(f"`{fg}` {cnt}/{n_tot} ({cnt / n_tot:.0%})" for fg, cnt in sorted(fam_cnts.items()))
        try:
            validate_layout_sequence(layout_entries)
            seq_status = "✅ 通過防撞車、帶框比與家族均衡護欄"
        except ValueError as exc:
            seq_status = f"⚠️ 需調整：{exc}"
        out.append(f"- **版型序列檢核**：{seq_status}")
        out.append(f"- **版型多樣性與去方塊比**：共 `{len(distinct_ids)}` 種版型（`{', '.join(distinct_ids)}`）｜帶框頁 `{boxed_cnt}/{n_tot}`（`{boxed_cnt / n_tot:.0%}`，上限 `<=40%`）")
        out.append(f"- **五大簡報家族分布**：{fam_summary}（單家族上限 `<=40%`）")
    else:
        out.append("- **版型序列檢核**：尚有頁面未鎖定 `layout.family_id`。")

    draft_note = "無殘留 `TBD`/`TODO`" if not draft_flags else f"⚠️ 偵測到草稿佔位字於 {', '.join(draft_flags)}"
    out.append(f"- **拍板文案凍結預檢**：已標記關鍵數字 `{total_key_nums}` 項｜{draft_note}")

    return "\n".join(out)


def _adapt_f1a_kpi_cards(raw_items: object) -> list[dict[str, str]] | None:
    """Adapt F1-A `kpi_cards` or Lead/Body `items` cleanly without mutating the source spec."""
    if not isinstance(raw_items, list) or not raw_items:
        return None
    adapted: list[dict[str, str]] = []
    for it in raw_items:
        if isinstance(it, dict):
            card: dict[str, str] = {}
            kicker = _first_non_empty_str(it, "kicker", "badge")
            title = _first_non_empty_str(it, "title", "heading", "label", "lead", "name")
            if kicker and title and kicker != title:
                title = f"{kicker}｜{title}"
            elif kicker and not title:
                title = kicker
            value = _first_non_empty_str(it, "value", "stat", "metric", "kpi")
            sub = _first_non_empty_str(it, "subtitle", "sub")
            desc_body = _first_non_empty_str(it, "desc", "body", "detail", "note", "text")
            if sub and desc_body and sub != desc_body:
                desc = f"{sub}｜{desc_body}"
            else:
                desc = desc_body or sub
            if title:
                card["title"] = title
            if value:
                card["value"] = value
            if desc:
                card["desc"] = desc
            if it.get("accent"):
                card["accent"] = str(it["accent"])
            if it.get("is_spotlight") is not None:
                card["is_spotlight"] = bool(it["is_spotlight"])  # type: ignore[assignment]
            adapted.append(card)
        else:
            ld, bd = _parse_lead_body_item(it)
            adapted.append({"title": ld or bd, "desc": bd if ld else ""})
    return adapted


def _coerce_spec_block_dict(raw: object) -> dict[str, object]:
    """Coerce a Step 3 Lead/Body string or tuple into a standard block dict without mutating caller data."""
    if isinstance(raw, dict):
        return dict(raw)
    ld, bd = _parse_lead_body_item(raw)
    if ld and bd:
        return {"title": ld, "body": bd}
    return {"title": ld or bd, "body": ""}


def _coerce_kpi_item_dict(raw: object) -> dict[str, object]:
    """Coerce a Step 3 KPI item (dict or `'value：label'` string) into a dict for `draw_kpi_strip_slide()`."""
    if isinstance(raw, dict):
        return dict(raw)
    ld, bd = _parse_lead_body_item(raw)
    if ld and bd:
        return {"value": ld, "label": bd}
    return {"value": ld or bd, "label": ""}


def _render_single_spec_slide(
    prs: Presentation,
    slide_spec: dict[str, object],
    slide_idx: int,
    tokens: dict[str, object],
    base_dir: Path | None,
    temp_files: list[Path],
) -> None:
    """Deterministically render one slide from its read-only `copy` + locked `layout` zones."""
    copy_z: dict[str, object] = slide_spec["copy"]  # type: ignore[assignment]
    lay_z: dict[str, object] = slide_spec["layout"]  # type: ignore[assignment]

    norm = _normalize_layout_entry(lay_z)
    canon_id = str(norm["canonical_id"])
    raw_code_upper = _first_non_empty_str(lay_z, "family_id", "layout", "code").upper().replace("_", "-")
    variant = str(norm.get("variant") or "").strip().lower()

    asset_info = _resolve_visual_asset_info(lay_z, copy_z, base_dir=base_dir)
    mat_png = _materialize_visual_asset_png(asset_info, temp_files, base_dir=base_dir)

    resolved_body_pt = (
        float(lay_z["body_font_pt"])
        if lay_z.get("body_font_pt") is not None
        else float(tokens["target_body_pt"])  # type: ignore[arg-type]
    )
    speaker_notes = _first_non_empty_str(copy_z, "speaker_notes")
    use_zone3 = _should_render_zone3(copy_z, lay_z, canon_id)
    z3_text = _first_non_empty_str(copy_z, "zone3_takeaway")
    z3_style = _first_non_empty_str(lay_z, "zone3_style", default="dark_banner")
    spot_idx = lay_z.get("spotlight_idx")
    if spot_idx is not None:
        spot_idx = int(spot_idx)  # type: ignore[arg-type]

    # --- Family 1-A: Cover / Closing Bookend (first arg is `prs`) ---
    if canon_id == "F1-A":
        badge_txt = _first_non_empty_str(copy_z, "badge_text", "chapter_pill")
        main_title = _first_non_empty_str(copy_z, "headline", "main_title", "title")
        subtitle = _first_non_empty_str(copy_z, "subtitle")
        kpi_cards = _adapt_f1a_kpi_cards(copy_z.get("kpi_cards") or copy_z.get("items"))
        footer_txt = _first_non_empty_str(copy_z, "footer_text") or (z3_text if use_zone3 else None)
        bg_hex = str(lay_z["bg_hex"]) if lay_z.get("bg_hex") else None
        accent_hex = str(lay_z["accent_hex"]) if lay_z.get("accent_hex") else None
        slide = add_bookend_slide_s0(
            prs,
            badge_text=badge_txt,
            main_title=main_title,
            subtitle_text=subtitle,
            kpi_cards=kpi_cards,
            speaker_notes=speaker_notes or None,
            bg_hex=bg_hex,
            accent_hex=accent_hex,
            footer_text=footer_txt,
            tokens=tokens,
        )
        if mat_png:
            _place_overlay_picture(slide, mat_png, asset_info, default_behind=True)
        _apply_tier1_geometric_accent(slide, lay_z, tokens)
        return

    # All other 12 layouts operate on a blank slide
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg_override = str(lay_z["bg_hex"]) if lay_z.get("bg_hex") else None
    set_slide_background(slide, bg_hex=bg_override, tokens=tokens)

    # --- Family 1-B: Ultra-Minimal Section Divider ---
    if canon_id == "F1-B":
        sec_num = _first_non_empty_str(copy_z, "section_num", "chapter_pill", default=f"{slide_idx:02d}")
        sec_title = _first_non_empty_str(copy_z, "section_title", "headline", "title")
        sec_sub = _first_non_empty_str(copy_z, "subtitle")
        draw_section_divider_slide(
            slide,
            section_num=sec_num,
            section_title=sec_title,
            subtitle_text=sec_sub,
            tokens=tokens,
        )
        if use_zone3 and z3_text:
            add_zone3_footer(slide, z3_text, style=z3_style, tokens=tokens)
        if mat_png:
            _place_overlay_picture(slide, mat_png, asset_info, default_behind=True)
        _apply_tier1_geometric_accent(slide, lay_z, tokens)
        if speaker_notes:
            add_speaker_notes(slide, speaker_notes)
        return

    # --- Standard Content & Impact Slides (F1-C .. F5-C): Zone 1 -> Optional Zone 3 -> Zone 2 ---
    pill_txt = _first_non_empty_str(copy_z, "chapter_pill", "badge_text")
    headline_txt = _first_non_empty_str(copy_z, "headline", "title")
    subtitle_txt = _first_non_empty_str(copy_z, "subtitle") or None
    right_badge_txt = _first_non_empty_str(copy_z, "right_badge") or None
    show_divider = bool(lay_z.get("show_divider", True))

    if pill_txt or headline_txt or subtitle_txt or right_badge_txt:
        z2_top = add_zone1_header(
            slide,
            chapter_pill_text=pill_txt,
            assertion_headline=headline_txt,
            subtitle_text=subtitle_txt,
            right_badge_text=right_badge_txt,
            show_divider=show_divider,
            tokens=tokens,
        )
    else:
        z2_top = 0.56

    # Render optional Zone 3 BEFORE Zone 2 so Zone 2 reserves exact non-overlapping height
    z2_height: float | None = None
    if use_zone3 and z3_text:
        before_cnt = len(slide.shapes)
        add_zone3_footer(slide, z3_text, style=z3_style, tokens=tokens)
        z3_tops = [
            float(shp.top or 0) / 914400.0
            for shp in list(slide.shapes)[before_cnt:]
        ]
        if z3_tops:
            min_z3_top = min(z3_tops)
            z2_height = round(max(1.60, min_z3_top - 0.14 - z2_top), 3)

    # Dispatch across the remaining 11 refined layouts
    if canon_id == "F1-C":
        if not variant:
            variant = "quote_manifesto" if raw_code_upper == "S14" else ("quote_manifesto" if copy_z.get("quote") or copy_z.get("manifesto") else "big_number")
        stat_val = _first_non_empty_str(copy_z, "stat_value", "quote", "manifesto")
        stat_lbl = _first_non_empty_str(copy_z, "stat_label", "attribution")
        ctx_pts = copy_z.get("context_points")
        if ctx_pts is None:
            ctx_pts = copy_z.get("items") or ()
        if not stat_val and isinstance(ctx_pts, list) and ctx_pts:
            first_it = ctx_pts[0]
            rest_pts = list(ctx_pts[1:])
            if isinstance(first_it, dict):
                stat_val = _first_non_empty_str(first_it, "value", "stat", "quote", "lead", "title")
                used_lbl_key = None
                if not stat_lbl:
                    for lk in ("label", "subtitle", "body", "desc"):
                        cand_l = _first_non_empty_str(first_it, lk)
                        if cand_l:
                            stat_lbl = cand_l
                            used_lbl_key = lk
                            break
                # Preserve any remaining body/desc/detail so zero frozen copy is ever silently dropped
                rem_body = _first_non_empty_str(first_it, "body", "desc", "detail", "note", "text")
                if rem_body and rem_body != stat_val and rem_body != stat_lbl and used_lbl_key not in ("body", "desc"):
                    rest_pts.insert(0, {"lead": "", "body": rem_body})
            else:
                ld, bd = _parse_lead_body_item(first_it)
                stat_val = ld or bd
                if not stat_lbl and ld and bd:
                    stat_lbl = bd
                elif stat_lbl and ld and bd and bd != stat_lbl:
                    rest_pts.insert(0, {"lead": "", "body": bd})
            ctx_pts = rest_pts
        stat_pt = float(lay_z["stat_pt"]) if lay_z.get("stat_pt") is not None else 54.0
        draw_hero_stat_slide(
            slide,
            stat_value=stat_val,
            stat_label=stat_lbl,
            context_points=ctx_pts if isinstance(ctx_pts, (list, tuple)) else (),
            right_image_path=mat_png if variant != "quote_manifesto" else None,
            variant=variant,
            top=z2_top,
            height=z2_height,
            stat_pt=stat_pt,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )
        if mat_png and variant == "quote_manifesto":
            _place_overlay_picture(slide, mat_png, asset_info, default_behind=True)

    elif canon_id == "F2-A":
        cards = copy_z.get("cards") if isinstance(copy_z.get("cards"), list) else copy_z.get("items")
        cards_list = [_coerce_spec_block_dict(c) for c in cards] if isinstance(cards, list) else []
        card_style = variant or _first_non_empty_str(lay_z, "card_style")
        if not card_style:
            card_style = "borderless_centerline" if len(cards_list) == 2 else "minimal_column"
        width_ratios = lay_z.get("width_ratios") if isinstance(lay_z.get("width_ratios"), list) else None
        title_pt = float(lay_z["title_font_pt"]) if lay_z.get("title_font_pt") is not None else None
        draw_parallel_row_cards(
            slide,
            cards_spec=cards_list,
            top=z2_top,
            height=z2_height,
            spotlight_idx=spot_idx,
            body_font_pt=resolved_body_pt,
            title_font_pt=title_pt,
            width_ratios=width_ratios,
            card_style=card_style,
            tokens=tokens,
        )

    elif canon_id == "F2-B":
        rows = copy_z.get("rows") if isinstance(copy_z.get("rows"), list) else copy_z.get("items")
        rows_list = [_coerce_spec_block_dict(r) for r in rows] if isinstance(rows, list) else []
        left_ratio = float(lay_z.get("left_ratio", 0.28))  # type: ignore[arg-type]
        draw_editorial_split_rows_s8(
            slide,
            rows_spec=rows_list,
            left_ratio=left_ratio,
            spotlight_idx=spot_idx,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F2-C":
        pri = copy_z.get("primary_block")
        secs = copy_z.get("secondary_blocks")
        if pri is None and isinstance(copy_z.get("items"), list) and copy_z["items"]:
            pri = copy_z["items"][0]
            secs = copy_z["items"][1:]
        pri_dict = _coerce_spec_block_dict(pri)
        sec_list = [_coerce_spec_block_dict(sb) for sb in (secs if isinstance(secs, list) else [])]
        eff_spot = 0 if ("spotlight_idx" not in lay_z) else spot_idx
        draw_bento_grid_slide(
            slide,
            primary_block=pri_dict,
            secondary_blocks=sec_list,
            spotlight_idx=eff_spot,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F3-A":
        steps = copy_z.get("steps") if isinstance(copy_z.get("steps"), list) else copy_z.get("items")
        steps_list = [_coerce_spec_block_dict(st) for st in steps] if isinstance(steps, list) else []
        lay_style = variant or _first_non_empty_str(lay_z, "layout_style")
        if not lay_style:
            lay_style = "staggered_timeline" if raw_code_upper == "S12" else "auto"
        draw_process_steps_s3(
            slide,
            steps_spec=steps_list,
            layout_style=lay_style,
            top=z2_top,
            height=z2_height,
            spotlight_idx=spot_idx,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F3-B":
        nodes = copy_z.get("nodes") if isinstance(copy_z.get("nodes"), list) else copy_z.get("items")
        nodes_list = [_coerce_spec_block_dict(nd) for nd in nodes] if isinstance(nodes, list) else []
        edges = copy_z.get("edges") if isinstance(copy_z.get("edges"), list) else lay_z.get("edges")
        valid_topos = {"horizontal_chain", "cycle_loop", "hub_spoke", "custom"}
        topo = _first_non_empty_str(lay_z, "topology") or (variant if variant in valid_topos else "horizontal_chain")
        c_pos = _first_non_empty_str(lay_z, "callout_position", default="right")
        v_ratio = float(lay_z.get("visual_ratio", 0.64))  # type: ignore[arg-type]
        draw_clean_mechanism_s4(
            slide,
            nodes_spec=nodes_list,
            edges_spec=edges if isinstance(edges, list) else None,
            topology=topo,
            callouts=copy_z.get("callouts") if isinstance(copy_z.get("callouts"), list) else None,
            callout_position=c_pos,
            callout_heading=_first_non_empty_str(copy_z, "callout_heading") or None,
            visual_ratio=v_ratio,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F4-A":
        quads = copy_z.get("quadrants") if isinstance(copy_z.get("quadrants"), list) else copy_z.get("items")
        quads_list = [_coerce_spec_block_dict(q) for q in quads] if isinstance(quads, list) else []
        if lay_z.get("borderless") is not None:
            borderless = bool(lay_z["borderless"])
        else:
            borderless = variant not in ("boxed", "clean_card")
        eff_spot = 1 if ("spotlight_idx" not in lay_z) else spot_idx
        draw_quadrant_matrix_s5(
            slide,
            quadrants_spec=quads_list,
            x_axis_label=_first_non_empty_str(copy_z, "x_axis_label"),
            y_axis_label=_first_non_empty_str(copy_z, "y_axis_label"),
            spotlight_idx=eff_spot,
            borderless=borderless,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F4-B":
        tbl = copy_z.get("table") if isinstance(copy_z.get("table"), dict) else {}
        hdrs = copy_z.get("headers") or tbl.get("headers")
        rows = copy_z.get("rows") or tbl.get("rows")
        if hdrs is None and isinstance(copy_z.get("items"), list) and copy_z["items"]:
            first_row = copy_z["items"][0]
            if isinstance(first_row, dict):
                hdrs = list(first_row.keys())
                rows = [[r.get(k, "") if isinstance(r, dict) else "" for k in hdrs] for r in copy_z["items"]]
        spot_col = lay_z.get("spotlight_col")
        if spot_col is not None:
            spot_col = int(spot_col)  # type: ignore[arg-type]
        elif spot_idx is not None:
            spot_col = spot_idx
        col_widths = lay_z.get("col_widths") if isinstance(lay_z.get("col_widths"), list) else None
        draw_comparison_table_slide(
            slide,
            headers=list(hdrs) if isinstance(hdrs, list) else [],
            rows=list(rows) if isinstance(rows, list) else [],
            spotlight_col=spot_col,
            col_widths=col_widths,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F5-A":
        valid_pos = {"right", "left", "top", "bottom", "header_only"}
        legacy_pos_map = {"S7-A": "right", "S7-B": "bottom", "S7-C": "top", "S7-D": "header_only"}
        c_pos = _first_non_empty_str(lay_z, "callout_position").lower()
        if c_pos not in valid_pos:
            if variant in valid_pos:
                c_pos = variant
            else:
                c_pos = legacy_pos_map.get(raw_code_upper, "right")
        callouts = copy_z.get("callouts") if isinstance(copy_z.get("callouts"), list) else copy_z.get("items")
        v_ratio = float(lay_z.get("visual_ratio", 0.65))  # type: ignore[arg-type]
        v_cap = _first_non_empty_str(copy_z, "visual_caption", "caption", "source") or None
        c_head = _first_non_empty_str(copy_z, "callout_heading") or None
        eff_spot = 0 if ("spotlight_idx" not in lay_z) else spot_idx
        draw_visual_callout_slide(
            slide,
            image_path=mat_png,
            callout_position=c_pos,
            callouts=callouts if isinstance(callouts, list) else None,
            visual_ratio=v_ratio,
            visual_caption=v_cap,
            callout_heading=c_head,
            body_font_pt=resolved_body_pt,
            top=z2_top,
            height=z2_height,
            spotlight_idx=eff_spot,
            tokens=tokens,
        )

    elif canon_id == "F5-B":
        kpis = copy_z.get("kpi_items") or copy_z.get("kpis")
        insights = copy_z.get("insight_blocks") or copy_z.get("insights")
        if kpis is None and isinstance(copy_z.get("items"), dict):
            kpis = copy_z["items"].get("kpi_items") or copy_z["items"].get("kpis")  # type: ignore[union-attr]
            insights = insights or copy_z["items"].get("insight_blocks") or copy_z["items"].get("insights")  # type: ignore[union-attr]
        elif kpis is not None and insights is None and isinstance(copy_z.get("items"), list):
            insights = copy_z["items"]
        elif kpis is None and isinstance(copy_z.get("items"), list):
            kpis = copy_z["items"]
        eff_spot = 0 if ("spotlight_idx" not in lay_z) else spot_idx
        draw_kpi_strip_slide(
            slide,
            kpi_items=[_coerce_kpi_item_dict(k) for k in kpis] if isinstance(kpis, list) else [],
            insight_blocks=list(insights) if isinstance(insights, list) else (),
            spotlight_idx=eff_spot,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    elif canon_id == "F5-C":
        f_title = _first_non_empty_str(copy_z, "focal_title")
        f_formula = _first_non_empty_str(copy_z, "focal_formula", "formula")
        f_note = _first_non_empty_str(copy_z, "focal_note")
        b_items = copy_z.get("breakdown_items") if isinstance(copy_z.get("breakdown_items"), list) else copy_z.get("items")
        f_mode = _first_non_empty_str(lay_z, "mode").lower()
        if f_mode not in ("left_right", "top_bottom"):
            f_mode = variant if variant in ("left_right", "top_bottom") else "left_right"
        f_ratio = float(lay_z.get("focal_ratio", 0.38))  # type: ignore[arg-type]
        use_omml = bool(lay_z.get("use_omml")) if ("use_omml" in lay_z) else bool(copy_z.get("use_omml", False))
        draw_focal_anatomy_s6(
            slide,
            focal_title=f_title,
            focal_formula=f_formula,
            focal_note=f_note,
            breakdown_items=list(b_items) if isinstance(b_items, list) else (),
            mode=f_mode,
            focal_ratio=f_ratio,
            use_omml=use_omml,
            top=z2_top,
            height=z2_height,
            body_font_pt=resolved_body_pt,
            tokens=tokens,
        )

    else:
        raise ValueError(
            f"Unsupported layout family_id '{raw_code_upper}' (canonical='{canon_id}') on Slide #{slide_idx}. "
            "Expected one of F1-A..F5-C (or legacy S0..S14 / Hero Stat)."
        )

    # Optional Mode 3 Tier 2/3 overlay on non-image slides when explicitly supplied
    if mat_png and canon_id not in ("F1-A", "F1-B", "F1-C", "F5-A"):
        _place_overlay_picture(slide, mat_png, asset_info, default_behind=False)

    _apply_tier1_geometric_accent(slide, lay_z, tokens)
    if speaker_notes:
        add_speaker_notes(slide, speaker_notes)


def render_deck_from_spec(
    spec_json_or_path: dict[str, object] | str | Path,
    output_pptx_path: str | Path,
    *,
    validate_sequence: bool = True,
    require_bookends: bool = True,
    min_distinct: int = 5,
    max_boxed_ratio: float = 0.40,
    max_family_ratio: float = 0.40,
    asset_base_dir: str | Path | None = None,
    strict_fidelity: bool = False,
) -> str:
    """
    [Step 4B] Deterministically render a `.pptx` deck from a locked `02c_slide_spec_lock.json`:
    - Strictly READ-ONLY on `slides[i].copy` (deep-copied at entry + canonical JSON fingerprint asserted post-render).
    - Resolves unified DISCAS / dynamic CIELAB tokens via `build_slide_design_tokens()`.
    - Automatically runs `validate_layout_sequence()` when `validate_sequence=True`.
    - Dispatches all 5 layout families / 13 refined layouts (`F1-A`..`F5-C`) plus Mode 3 `Tier 1/2/3` and OMML.
    - Cleans up any ephemeral Tier 3 SVG/HTML PNG temp files automatically.
    Returns absolute resolved path string of `output_pptx_path`.
    """
    spec, spec_parent = _load_spec_lock(spec_json_or_path)
    slides = _validate_spec_lock_structure(spec, require_layout=True)

    # Code-level Read-Only Copy Guardrail: freeze canonical JSON snapshot of every slide's copy zone
    copy_snapshot_before = json.dumps([s["copy"] for s in slides], ensure_ascii=False, sort_keys=True)

    if validate_sequence:
        layout_seq = [s["layout"] for s in slides]
        validate_layout_sequence(
            layout_seq,
            require_bookends=require_bookends,
            min_distinct=min_distinct,
            max_boxed_ratio=max_boxed_ratio,
            max_family_ratio=max_family_ratio,
        )

    tokens = _resolve_spec_design_tokens(spec)
    base_dir = Path(asset_base_dir).resolve() if asset_base_dir is not None else spec_parent

    prs = create_widescreen_presentation()
    temp_files: list[Path] = []
    out_path = Path(output_pptx_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        for idx, sl in enumerate(slides, start=1):
            _render_single_spec_slide(prs, sl, idx, tokens, base_dir, temp_files)

        # Runtime assertion proving `slides[i].copy` was never modified during deterministic rendering
        copy_snapshot_after = json.dumps([s["copy"] for s in slides], ensure_ascii=False, sort_keys=True)
        if copy_snapshot_after != copy_snapshot_before:
            raise RuntimeError("Read-Only Copy Fidelity Guardrail violated: slides[i].copy mutated during render.")

        prs.save(str(out_path))
    finally:
        for tmp_p in temp_files:
            with suppress(OSError):
                tmp_p.unlink(missing_ok=True)

    if strict_fidelity:
        report = check_copy_fidelity(spec, out_path)
        if not report["passed"]:
            raise ValueError(f"Copy fidelity verification failed: {report['summary']}")

    return str(out_path)


def _normalize_ws(text: str) -> str:
    """Collapse internal whitespace cleanly for robust line-wrap-invariant comparison."""
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _extract_numeric_tokens(text: str) -> list[str]:
    """Extract normalized key numeric tokens (percentages, currencies, years, decimals, integers) from text."""
    clean = _strip_inline_bold(str(text or ""))
    tokens: list[str] = []
    for m in _FIDELITY_NUM_TOKEN_RE.finditer(clean):
        tok = m.group(0).replace("％", "%").strip()
        if tok:
            tokens.append(tok)
    return tokens


def _match_numeric_phrase_in_text(phrase: str, haystack: str) -> bool:
    """
    Check whether a key numeric phrase (e.g. `'70%'`, `'5.81 億英鎊'`, `'2026'`, `'$1,200'`) appears
    intact in `haystack` with strict numeric digit, comma-group, and unary-sign boundaries so:
    - `'20%'` never matches `'120%'`
    - `'100'` never matches `'1,100'` or `'100,000'` (while still matching `'100, 200'`)
    - `'15%'` never matches `'-15%'` or `'+15%'` (while `'2026'` still matches `'2020-2026'`)
    """
    clean_p = _normalize_ws(phrase).replace("％", "%")
    clean_h = _normalize_ws(haystack).replace("％", "%")
    if not clean_p:
        return True
    parts = clean_p.split(" ")
    pat = r"\s*".join(re.escape(pt) for pt in parts)
    if clean_p[0].isdigit():
        pat = r"(?<!\d,)(?<![0-9.])(?<!(?<![0-9])[+-])" + pat
    if clean_p[-1].isdigit():
        pat = pat + r"(?![0-9.]|,\d{3})"
    return re.search(pat, clean_h) is not None


def _extract_slide_rendered_texts(slide) -> dict[str, object]:
    """
    Extract all rendered text from a PowerPoint slide:
    - standard text frames (including recursive GroupShapes)
    - native Table cells (`F4-B`)
    - native OMML `<m:oMath>` `<m:t>` math runs AND `<mc:Fallback>` `<a:t>` runs (`F5-C`)
    - speaker notes text
    """
    visible_chunks: list[str] = []
    omml_math_chunks: list[str] = []
    omml_fallback_chunks: list[str] = []

    a_ns = _OMML_A_NS
    m_ns = _OMML_M_NS
    mc_ns = _OMML_MC_NS

    def _collect_text_frame(tf) -> None:
        for para in tf.paragraphs:
            p_el = para._p
            # Standard direct <a:r><a:t> runs (excludes <mc:AlternateContent>)
            direct_runs: list[str] = []
            for child in p_el:
                if child.tag == f"{{{a_ns}}}r":
                    t_el = child.find(f"{{{a_ns}}}t")
                    if t_el is not None and t_el.text:
                        direct_runs.append(t_el.text)
                elif child.tag == f"{{{a_ns}}}fld":
                    t_el = child.find(f"{{{a_ns}}}t")
                    if t_el is not None and t_el.text:
                        direct_runs.append(t_el.text)
                elif child.tag == f"{{{mc_ns}}}AlternateContent":
                    # Extract both native OMML <m:t> and <mc:Fallback> <a:t>
                    math_ts = [el.text for el in child.findall(f".//{{{m_ns}}}t") if el.text]
                    if math_ts:
                        omml_math_chunks.append("".join(math_ts))
                    fb_el = child.find(f"{{{mc_ns}}}Fallback")
                    if fb_el is not None:
                        fb_ts = [el.text for el in fb_el.findall(f".//{{{a_ns}}}t") if el.text]
                        if fb_ts:
                            omml_fallback_chunks.append("".join(fb_ts))
            line_txt = "".join(direct_runs)
            if line_txt.strip():
                visible_chunks.append(line_txt)

    def _walk_shapes(shapes) -> None:
        for shp in shapes:
            if getattr(shp, "has_text_frame", False):
                _collect_text_frame(shp.text_frame)
            if getattr(shp, "has_table", False):
                for row in shp.table.rows:
                    for cell in row.cells:
                        _collect_text_frame(cell.text_frame)
            if hasattr(shp, "shapes"):
                with suppress(Exception):
                    _walk_shapes(shp.shapes)

    _walk_shapes(slide.shapes)

    notes_text = ""
    with suppress(Exception):
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None:
            notes_text = str(slide.notes_slide.notes_text_frame.text or "")

    visible_joined = "\n".join(visible_chunks)
    # `primary_chunks` avoids double-counting OMML `<m:t>` + `<mc:Fallback>` `<a:t>` for multiset numeric verification
    primary_chunks = visible_chunks + (omml_math_chunks if omml_math_chunks else omml_fallback_chunks)
    combined_for_match = "\n".join(visible_chunks + omml_math_chunks + omml_fallback_chunks)
    return {
        "visible_text": visible_joined,
        "omml_math_text": "\n".join(omml_math_chunks),
        "omml_fallback_text": "\n".join(omml_fallback_chunks),
        "primary_text": "\n".join(primary_chunks),
        "combined_text": combined_for_match,
        "notes_text": notes_text,
    }


def _collect_expected_copy_segments(
    copy_zone: dict[str, object],
    layout_zone: dict[str, object],
    canonical_id: str,
) -> tuple[list[str], str | None]:
    """
    Collect all frozen visible text segments expected on the rendered slide (plus optional `omml_formula`
    for dual math-run numeric verification) from `slides[i].copy`, respecting `layout.include_zone3`.
    """
    segments: list[str] = []
    omml_formula: str | None = None
    variant = str(_normalize_layout_entry(layout_zone).get("variant") or "").strip().lower()
    use_zone3 = _should_render_zone3(copy_zone, layout_zone, canonical_id)

    def _add_str(raw: object, *, split_lead_body: bool = False) -> None:
        if raw is None or isinstance(raw, bool):
            return
        s = str(raw).strip()
        if not s:
            return
        for hard_line in s.splitlines():
            hl = hard_line.strip()
            if not hl:
                continue
            if split_lead_body:
                m = _LEAD_BODY_SPLIT_RE.match(hl)
                if m:
                    segments.append(_strip_inline_bold(m.group(1).strip()))
                    segments.append(_strip_inline_bold(m.group(2).strip()))
                    continue
            segments.append(_strip_inline_bold(hl))

    def _add_item_obj(obj: object, *, is_minimal_col_card: bool = False) -> None:
        if obj is None or isinstance(obj, bool):
            return
        if isinstance(obj, str):
            if is_minimal_col_card:
                ld, bd = _parse_lead_body_item(obj)
                title_part = ld or bd
                body_part = bd if ld else ""
                if title_part:
                    m_sn = re.match(r"^\s*(0?\d{1,2})(?:[\.\)、:：\-—–\|｜\s]+)(.+)$", title_part)
                    if m_sn and _LEADING_INDEX_PREFIX_RE.match(title_part):
                        _add_str(m_sn.group(1))
                        _add_str(m_sn.group(2))
                    else:
                        _add_str(title_part)
                    if body_part:
                        _add_str(body_part, split_lead_body=True)
                    return
            _add_str(obj, split_lead_body=True)
            return
        if isinstance(obj, (list, tuple)):
            for sub in obj:
                _add_item_obj(sub)
            return
        if isinstance(obj, dict):
            # Text keys only (explicitly skips styling/geometry keys like accent/bg/dark/is_spotlight/rx/ry/rw/rh)
            scalar_keys = (
                "kicker", "badge", "step", "num", "phase", "date", "index",
                "title", "heading", "label", "name", "category",
                "subtitle", "sub", "value", "stat", "metric", "number", "kpi", "delta",
                "lead", "body", "detail", "desc", "text", "content", "note", "caption",
            )
            for k in scalar_keys:
                val = obj.get(k)
                if val is None or isinstance(val, (bool, list, tuple, dict)):
                    continue
                s = str(val).strip()
                if not s:
                    continue
                # Handle F2-A minimal_column leading numeral extraction ("01. Title" -> "01" + "Title")
                if is_minimal_col_card and k in ("title", "heading", "label", "name"):
                    m_sn = re.match(r"^\s*(0?\d{1,2})(?:[\.\)、:：\-—–\|｜\s]+)(.+)$", s)
                    if m_sn and _LEADING_INDEX_PREFIX_RE.match(s):
                        _add_str(m_sn.group(1))
                        _add_str(m_sn.group(2))
                        continue
                _add_str(s, split_lead_body=(k in ("body", "detail", "desc", "text", "content", "note")))
            for ck in ("rows", "items", "points", "bullets"):
                sub_coll = obj.get(ck)
                if isinstance(sub_coll, (list, tuple)):
                    for entry in sub_coll:
                        _add_item_obj(entry)

    # Top-level fields by family
    if canonical_id == "F1-A":
        _add_str(_first_non_empty_str(copy_zone, "badge_text", "chapter_pill"))
        _add_str(_first_non_empty_str(copy_zone, "headline", "main_title", "title"))
        _add_str(_first_non_empty_str(copy_zone, "subtitle"))
        for card in (copy_zone.get("kpi_cards") or copy_zone.get("items") or []):
            _add_item_obj(card)
        if use_zone3:
            _add_str(_first_non_empty_str(copy_zone, "footer_text", "zone3_takeaway"))
        return segments, None

    if canonical_id == "F1-B":
        sec_num = _first_non_empty_str(copy_zone, "section_num", "chapter_pill")
        if sec_num:
            _add_str(f"{int(sec_num):02d}" if sec_num.isdigit() else sec_num)
        _add_str(_first_non_empty_str(copy_zone, "section_title", "headline", "title"))
        _add_str(_first_non_empty_str(copy_zone, "subtitle"))
        if use_zone3:
            _add_str(_first_non_empty_str(copy_zone, "zone3_takeaway"))
        return segments, None

    # Zone 1 shared fields for F1-C .. F5-C
    _add_str(_first_non_empty_str(copy_zone, "chapter_pill", "badge_text"))
    _add_str(_first_non_empty_str(copy_zone, "right_badge"))
    _add_str(_first_non_empty_str(copy_zone, "headline", "title"))
    _add_str(_first_non_empty_str(copy_zone, "subtitle"))

    # Family-specific Zone 2 copy fields
    if canonical_id == "F1-C":
        _add_str(_first_non_empty_str(copy_zone, "stat_value", "quote", "manifesto"))
        _add_str(_first_non_empty_str(copy_zone, "stat_label", "attribution"))
        pts = copy_zone.get("context_points") if copy_zone.get("context_points") is not None else copy_zone.get("items")
        if isinstance(pts, list):
            for it in pts:
                _add_item_obj(it)
    elif canonical_id == "F2-A":
        cards = copy_zone.get("cards") if isinstance(copy_zone.get("cards"), list) else copy_z_items(copy_zone)
        is_min_col = (variant == "minimal_column") or (not variant and len(cards) != 2)
        for c in cards:
            _add_item_obj(c, is_minimal_col_card=is_min_col)
    elif canonical_id == "F2-B":
        for r in (copy_zone.get("rows") if isinstance(copy_zone.get("rows"), list) else copy_z_items(copy_zone)):
            _add_item_obj(r)
    elif canonical_id == "F2-C":
        if copy_zone.get("primary_block") is not None:
            _add_item_obj(copy_zone.get("primary_block"))
            for sb in (copy_zone.get("secondary_blocks") or []):
                _add_item_obj(sb)
        else:
            for it in copy_z_items(copy_zone):
                _add_item_obj(it)
    elif canonical_id == "F3-A":
        for st in (copy_zone.get("steps") if isinstance(copy_zone.get("steps"), list) else copy_z_items(copy_zone)):
            _add_item_obj(st)
    elif canonical_id == "F3-B":
        for nd in (copy_zone.get("nodes") if isinstance(copy_zone.get("nodes"), list) else copy_z_items(copy_zone)):
            _add_item_obj(nd)
        _add_str(_first_non_empty_str(copy_zone, "callout_heading"))
        for co in (copy_zone.get("callouts") or []):
            _add_item_obj(co)
    elif canonical_id == "F4-A":
        _add_str(_first_non_empty_str(copy_zone, "x_axis_label"))
        _add_str(_first_non_empty_str(copy_zone, "y_axis_label"))
        for q in (copy_zone.get("quadrants") if isinstance(copy_zone.get("quadrants"), list) else copy_z_items(copy_zone)):
            _add_item_obj(q)
    elif canonical_id == "F4-B":
        tbl = copy_zone.get("table") if isinstance(copy_zone.get("table"), dict) else {}
        hdrs = copy_zone.get("headers") or tbl.get("headers")
        rows = copy_zone.get("rows") or tbl.get("rows")
        if hdrs is None and isinstance(copy_zone.get("items"), list) and copy_zone["items"] and isinstance(copy_zone["items"][0], dict):
            hdrs = list(copy_zone["items"][0].keys())
            rows = [[r.get(k, "") if isinstance(r, dict) else "" for k in hdrs] for r in copy_zone["items"]]
        for h in (hdrs or []):
            _add_str(h)
        for r in (rows or []):
            if isinstance(r, (list, tuple)):
                for cell_val in r:
                    _add_str(cell_val)
            else:
                _add_str(r)
    elif canonical_id == "F5-A":
        _add_str(_first_non_empty_str(copy_zone, "callout_heading"))
        for co in (copy_zone.get("callouts") if isinstance(copy_zone.get("callouts"), list) else copy_z_items(copy_zone)):
            _add_item_obj(co)
        _add_str(_first_non_empty_str(copy_zone, "visual_caption", "caption", "source"))
    elif canonical_id == "F5-B":
        kpis = copy_zone.get("kpi_items") or copy_zone.get("kpis")
        insights = copy_zone.get("insight_blocks") or copy_zone.get("insights")
        if kpis is None and isinstance(copy_zone.get("items"), dict):
            kpis = copy_zone["items"].get("kpi_items") or copy_zone["items"].get("kpis")  # type: ignore[union-attr]
            insights = insights or copy_zone["items"].get("insight_blocks") or copy_zone["items"].get("insights")  # type: ignore[union-attr]
        elif kpis is not None and insights is None and isinstance(copy_zone.get("items"), list):
            insights = copy_zone["items"]
        elif kpis is None and isinstance(copy_zone.get("items"), list):
            kpis = copy_zone["items"]
        for k in (kpis or []):
            _add_item_obj(k)
        for ins in (insights or []):
            _add_item_obj(ins)
    elif canonical_id == "F5-C":
        _add_str(_first_non_empty_str(copy_zone, "focal_title"))
        raw_formula = _first_non_empty_str(copy_zone, "focal_formula", "formula")
        use_omml = bool(layout_zone.get("use_omml")) if ("use_omml" in layout_zone) else bool(copy_zone.get("use_omml", False))
        if raw_formula:
            clean_formula = raw_formula.replace("$$", "").replace("$", "").strip()
            _add_str(clean_formula)
            if use_omml:
                omml_formula = clean_formula
        _add_str(_first_non_empty_str(copy_zone, "focal_note"))
        for bd in (copy_zone.get("breakdown_items") if isinstance(copy_zone.get("breakdown_items"), list) else copy_z_items(copy_zone)):
            _add_item_obj(bd)
    else:
        # Layout-agnostic fallback (e.g., Step 3 spec prior to Step 4A layout locking): never silently skip frozen copy
        for fk in ("stat_value", "quote", "manifesto", "stat_label", "attribution", "callout_heading", "visual_caption", "caption", "source", "x_axis_label", "y_axis_label", "focal_title", "focal_formula", "formula", "focal_note"):
            _add_str(_first_non_empty_str(copy_zone, fk))
        if copy_zone.get("primary_block") is not None:
            _add_item_obj(copy_zone.get("primary_block"))
        for ck in ("items", "cards", "rows", "steps", "nodes", "quadrants", "callouts", "kpi_items", "kpis", "insight_blocks", "insights", "breakdown_items", "context_points", "secondary_blocks", "kpi_cards"):
            coll = copy_zone.get(ck)
            if isinstance(coll, list):
                for entry in coll:
                    _add_item_obj(entry)

    if use_zone3:
        _add_str(_first_non_empty_str(copy_zone, "zone3_takeaway"))

    return segments, omml_formula


def copy_z_items(copy_zone: dict[str, object]) -> list[object]:
    """Return `copy_zone['items']` as a list when present, else an empty list."""
    raw = copy_zone.get("items")
    return list(raw) if isinstance(raw, list) else []


def check_copy_fidelity(
    spec_json_or_path: dict[str, object] | str | Path,
    pptx_path: str | Path,
) -> dict[str, object]:
    """
    [Step 4B] Cross-check rendered `.pptx` text (shapes, GroupShapes, native tables, OMML math,
    and speaker notes) against the frozen `slides[i].copy` zone of `02c_slide_spec_lock.json`:
    - Verifies slide count match.
    - Guarantees 100% presence of every frozen `copy` text segment (no silent deletion or truncation).
    - Guarantees zero unparsed Markdown `**` and zero draft placeholders (`TBD` / `TODO` / `FIXME`).
    - Guarantees 100% verbatim numeric fidelity for both explicit `copy.key_numbers` and all
      auto-extracted percentages / currencies / years / values across every slide.
    - Verifies `copy.speaker_notes` preservation.
    Returns structured report dict with `passed: bool`, `errors`, `warnings`, `slides`, and `summary`.
    """
    spec, _base_dir = _load_spec_lock(spec_json_or_path)
    slides_spec = _validate_spec_lock_structure(spec, require_layout=False)

    pptx_file = Path(pptx_path).resolve()
    if not pptx_file.exists() or not pptx_file.is_file():
        raise FileNotFoundError(f"PPTX file not found for copy fidelity check: {pptx_file}")

    prs = Presentation(str(pptx_file))
    spec_n = len(slides_spec)
    pptx_n = len(prs.slides)

    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    per_slide_reports: list[dict[str, object]] = []
    total_expected_segments = 0
    total_expected_numbers = 0

    if spec_n != pptx_n:
        errors.append({
            "slide": 0,
            "type": "slide_count_mismatch",
            "detail": f"Spec defines {spec_n} slides, but PPTX contains {pptx_n} slides.",
        })

    n_check = min(spec_n, pptx_n)
    for idx in range(n_check):
        slide_num = idx + 1
        sl_spec = slides_spec[idx]
        copy_z: dict[str, object] = sl_spec["copy"]  # type: ignore[assignment]
        lay_z: dict[str, object] = sl_spec.get("layout") if isinstance(sl_spec.get("layout"), dict) else {}  # type: ignore[assignment]
        canon_id = str(_normalize_layout_entry(lay_z)["canonical_id"]) if lay_z else ""

        extracted = _extract_slide_rendered_texts(prs.slides[idx])
        vis_raw = str(extracted["visible_text"])
        omml_math_raw = str(extracted["omml_math_text"])
        primary_raw = str(extracted["primary_text"])
        combined_raw = str(extracted["combined_text"])
        notes_raw = str(extracted["notes_text"])

        combined_norm = _normalize_ws(combined_raw)
        combined_nospace = re.sub(r"\s+", "", combined_norm)

        slide_errors: list[dict[str, object]] = []
        missing_segments: list[str] = []
        missing_key_numbers: list[str] = []
        missing_numeric_tokens: list[str] = []
        residual_markdown: list[str] = []
        draft_placeholders: list[str] = []

        # 1. Zero residual Markdown `**` on rendered slide surface
        if "**" in vis_raw or "**" in omml_math_raw:
            residual_markdown.append("**")
            slide_errors.append({
                "slide": slide_num,
                "type": "residual_markdown",
                "detail": f"Slide {slide_num} contains unparsed Markdown '**' on screen.",
            })

        # 2. Zero draft placeholders (`TBD` / `TODO` / `FIXME`) on screen or speaker notes
        for m in _DRAFT_PLACEHOLDER_RE.finditer(combined_raw + "\n" + notes_raw):
            tok = m.group(0)
            if tok not in draft_placeholders:
                draft_placeholders.append(tok)
        if draft_placeholders:
            slide_errors.append({
                "slide": slide_num,
                "type": "draft_placeholder",
                "detail": f"Slide {slide_num} contains draft placeholder(s): {draft_placeholders}.",
                "tokens": draft_placeholders,
            })

        # 3. Verify every frozen visible copy segment is present verbatim (whitespace-normalized)
        expected_segments, omml_formula = _collect_expected_copy_segments(copy_z, lay_z, canon_id)
        total_expected_segments += len(expected_segments)

        for seg in expected_segments:
            seg_norm = _normalize_ws(seg)
            if not seg_norm:
                continue
            seg_nospace = re.sub(r"\s+", "", seg_norm)
            if (seg_norm not in combined_norm) and (seg_nospace not in combined_nospace):
                missing_segments.append(seg_norm)

        if missing_segments:
            slide_errors.append({
                "slide": slide_num,
                "type": "missing_copy_segment",
                "detail": f"Slide {slide_num} missing {len(missing_segments)} frozen copy segment(s): {missing_segments[:5]}",
                "missing": missing_segments,
            })

        # 4. Verify explicit `copy.key_numbers` with strict numeric digit boundaries
        raw_key_nums = copy_z.get("key_numbers")
        if isinstance(raw_key_nums, list):
            for kn in raw_key_nums:
                kn_s = str(kn or "").strip()
                if not kn_s:
                    continue
                total_expected_numbers += 1
                if not _match_numeric_phrase_in_text(kn_s, combined_raw):
                    missing_key_numbers.append(kn_s)
        if missing_key_numbers:
            slide_errors.append({
                "slide": slide_num,
                "type": "missing_key_number",
                "detail": f"Slide {slide_num} missing frozen key_numbers: {missing_key_numbers}.",
                "missing": missing_key_numbers,
            })

        # 5. Verify multiset fidelity of ALL auto-extracted numeric tokens across frozen copy
        # Uses `primary_raw` (visible + OMML `<m:t>` only, excluding duplicate `<mc:Fallback>`) so OMML
        # numbers are counted once and can never mask a deleted duplicate elsewhere on the slide.
        expected_num_counter: Counter[str] = Counter()
        for seg in expected_segments:
            expected_num_counter.update(_extract_numeric_tokens(seg))
        actual_num_counter: Counter[str] = Counter(_extract_numeric_tokens(primary_raw))
        total_expected_numbers += sum(expected_num_counter.values())

        for num_tok, exp_cnt in expected_num_counter.items():
            act_cnt = actual_num_counter.get(num_tok, 0)
            if act_cnt < exp_cnt:
                missing_numeric_tokens.append(f"{num_tok} (expected {exp_cnt}, found {act_cnt})")

        # Extra check for OMML `<m:oMath>` math runs so tampering or stripping `<m:oMath>` cannot hide behind `<mc:Fallback>`
        if omml_formula:
            if not omml_math_raw.strip():
                slide_errors.append({
                    "slide": slide_num,
                    "type": "missing_omml_math",
                    "detail": f"Slide {slide_num} expects native OMML equation ('{omml_formula}') but no <m:oMath> runs were found.",
                })
            else:
                exp_math_nums = Counter(_extract_numeric_tokens(omml_formula))
                act_math_nums = Counter(_extract_numeric_tokens(omml_math_raw))
                for num_tok, exp_cnt in exp_math_nums.items():
                    act_cnt = act_math_nums.get(num_tok, 0)
                    if act_cnt < exp_cnt:
                        missing_numeric_tokens.append(f"OMML:{num_tok} (expected {exp_cnt}, found {act_cnt})")

        if missing_numeric_tokens:
            slide_errors.append({
                "slide": slide_num,
                "type": "missing_numeric_token",
                "detail": f"Slide {slide_num} numeric fidelity mismatch: {missing_numeric_tokens}.",
                "missing": missing_numeric_tokens,
            })

        # 6. Verify `copy.speaker_notes` fidelity when defined in frozen copy
        expected_notes = _first_non_empty_str(copy_z, "speaker_notes")
        speaker_notes_ok = True
        if expected_notes:
            exp_notes_norm = _normalize_ws(expected_notes)
            act_notes_norm = _normalize_ws(notes_raw)
            if exp_notes_norm not in act_notes_norm:
                speaker_notes_ok = False
                slide_errors.append({
                    "slide": slide_num,
                    "type": "speaker_notes_mismatch",
                    "detail": f"Slide {slide_num} speaker notes missing or altered relative to frozen copy.",
                })

        errors.extend(slide_errors)
        per_slide_reports.append({
            "slide": slide_num,
            "family_id": canon_id,
            "passed": len(slide_errors) == 0,
            "expected_segments": len(expected_segments),
            "missing_segments": missing_segments,
            "missing_key_numbers": missing_key_numbers,
            "missing_numeric_tokens": missing_numeric_tokens,
            "residual_markdown": residual_markdown,
            "draft_placeholders": draft_placeholders,
            "speaker_notes_ok": speaker_notes_ok,
        })

    passed = len(errors) == 0
    summary = (
        f"PASSED: {n_check}/{spec_n} slides verified (100% copy & numeric fidelity, 0 errors)."
        if passed
        else f"FAILED: {len(errors)} copy/numeric fidelity error(s) detected across {n_check}/{spec_n} slides."
    )

    return {
        "passed": passed,
        "spec_slide_count": spec_n,
        "pptx_slide_count": pptx_n,
        "checked_slides": n_check,
        "total_expected_segments": total_expected_segments,
        "total_expected_numbers": total_expected_numbers,
        "errors": errors,
        "warnings": warnings,
        "slides": per_slide_reports,
        "summary": summary,
    }
