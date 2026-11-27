"""
hcl_color_engine.py
Backward-compatible facade for Deep Reading & Visual Synthesis color & chart engines.
The implementation has been modularized into `color_core`, `owner_sync`, `chart_data`,
`chart_common`, `chart_editorial`, `chart_family1_ranking`, `chart_family3_composition`,
`chart_family4_distribution`, `chart_creative_armory`, and `color_registry`.
"""

from color_core import *  # noqa: F401, F403
from owner_sync import *  # noqa: F401, F403
from chart_data import *  # noqa: F401, F403
from chart_common import *  # noqa: F401, F403
from chart_editorial import *  # noqa: F401, F403
from chart_family1_ranking import *  # noqa: F401, F403
from chart_family3_composition import *  # noqa: F401, F403
from chart_family4_distribution import *  # noqa: F401, F403
from chart_creative_armory import *  # noqa: F401, F403
from color_registry import (  # noqa: F401
    CategoryColorRegistry,
    RegistryFullError,
    clear_active_registry,
    get_active_registry,
    use_session_registry,
)

# Re-export underscore-prefixed helpers that may be imported explicitly by tests/tools
from color_core import (  # noqa: F401
    _ensure_wcag_contrast_in_lab,
    _expand_single_hex_to_four,
    _hcl_to_linear_rgb,
    _is_in_srgb_gamut,
    _lab_to_xyz,
    _linear_to_srgb,
    _normalize_hex,
    _resolve_lookup_color,
    _resolve_slide_topic_seed,
    _rgb_to_xyz,
    _xyz_to_lab,
    _xyz_to_rgb_clamped,
)
from owner_sync import (  # noqa: F401
    _detect_local_git_user,
    _detect_local_os_user,
    _is_gh_owner_authenticated,
)
from chart_data import _parse_numeric_or_na  # noqa: F401
from chart_common import _decollide_1d_positions, _ensure_cjk_font  # noqa: F401
from chart_creative_armory import (  # noqa: F401
    _build_tapered_cup_path,
    _generate_procedural_coffee_bean_sprite,
    _generate_procedural_pineapple_texture,
)

if __name__ == "__main__":
    from owner_sync import main

    main()
