"""
pptx_slide_engine.py
Backward-compatible facade for the modularized Format C presentation engine.
Implementation lives in `scripts/pptx_engine/` (`tokens`, `text_layout`, `media_omml`,
`primitives`, `layouts_data`, `layouts_narrative`, `spec_pipeline`).
"""

from pptx_engine.tokens import *  # noqa: F401, F403
from pptx_engine.text_layout import *  # noqa: F401, F403
from pptx_engine.media_omml import *  # noqa: F401, F403
from pptx_engine.primitives import *  # noqa: F401, F403
from pptx_engine.layouts_data import *  # noqa: F401, F403
from pptx_engine.layouts_narrative import *  # noqa: F401, F403
from pptx_engine.spec_pipeline import *  # noqa: F401, F403

from pptx_engine.tokens import (  # noqa: F401
    _add_flat_shape,
    _populate_paragraph_runs,
    _read_image_pixel_size,
    _round_half_pt,
    _blend_hex,
    _is_dark_hex,
    _theme_palette,
    _resolve_engine_context,
    _get_slide_height_in,
)
from pptx_engine.text_layout import (  # noqa: F401
    _LATIN_TOKEN_RE,
    _est_wrapped_lines,
    _load_msjh_font,
    _parse_inline_bold_segments,
    _tokenize_line_for_kinsoku,
    _measure_styled_tokens_width_in,
    _trim_line_edge_spaces,
    _count_orphan_core_chars,
    _wrap_paragraph_kinsoku,
    _normalize_box_dict,
    _measure_single_text_spec,
)
from pptx_engine.media_omml import (  # noqa: F401
    _find_chromium_cli_binary,
    _finalize_png_300dpi,
    _render_with_playwright,
    _render_with_chrome_cli,
    _OMML_A_NS,
    _OMML_A14_NS,
    _OMML_M_NS,
    _OMML_MC_NS,
    _XML_SPACE_ATTR,
    _OMML_ACCENT_CHARS,
    _OMML_SYMBOLS,
    _OMML_UPRIGHT_FUNCS,
    _OMML_NARY_CHARS,
    _clean_omml_hex,
    _make_omml_run,
    _build_omml_math_element,
)
from pptx_engine.primitives import (  # noqa: F401
    _LEAD_BODY_SPLIT_RE,
    _LEADING_INDEX_PREFIX_RE,
    _first_non_empty_str,
    _coerce_items_list,
    _parse_lead_body_item,
    _extract_lead_body_items,
    _measure_lead_body_item_height,
    _render_compact_lead_body_stack,
    _render_lead_body_box,
    _measure_three_tier_header,
    _render_three_tier_header,
    _resolve_zone2_height,
    _resolve_zone2_avail_bottom,
    _calc_zone2_expansion_factor,
    _apply_zone2_optical_vertical_balance,
    _shift_coords_y,
    _normalize_callout_items,
    _estimate_vertical_callouts_height,
    _render_unboxed_callouts_vertical,
    _render_unboxed_callouts_horizontal,
    _estimate_horizontal_band_height,
)
from pptx_engine.layouts_data import (  # noqa: F401
    _set_table_cell_ooxml_style,
)
from pptx_engine.layouts_narrative import (  # noqa: F401
    _render_bento_tile,
)
from pptx_engine.spec_pipeline import (  # noqa: F401
    _CANONICAL_LAYOUT_MAP,
    _BOXED_VARIANT_TOKENS,
    _UNBOXED_VARIANT_TOKENS,
    _normalize_layout_entry,
    _DRAFT_PLACEHOLDER_RE,
    _FIDELITY_NUM_TOKEN_RE,
    _INLINE_BOLD_STRIP_RE,
    _SVG_HTML_EXTS,
    _load_spec_lock,
    _validate_spec_lock_structure,
    _resolve_spec_design_tokens,
    _should_render_zone3,
    _resolve_visual_asset_info,
    _materialize_visual_asset_png,
    _place_overlay_picture,
    _apply_tier1_geometric_accent,
    _strip_inline_bold,
    _escape_md_cell,
    _summarize_slide_copy_skeleton,
    _adapt_f1a_kpi_cards,
    _coerce_spec_block_dict,
    _coerce_kpi_item_dict,
    _render_single_spec_slide,
    _normalize_ws,
    _extract_numeric_tokens,
    _match_numeric_phrase_in_text,
    _extract_slide_rendered_texts,
    _collect_expected_copy_segments,
)
