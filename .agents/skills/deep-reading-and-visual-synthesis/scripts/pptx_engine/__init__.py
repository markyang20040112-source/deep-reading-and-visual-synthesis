"""
pptx_engine
Modularized Format C 16:9 presentation engine and Option C QA package.
Note: `pptx_slide_engine` and `verify_visual_outputs` remain the public entry points.
"""

from .tokens import *  # noqa: F401, F403
from .text_layout import *  # noqa: F401, F403
from .media_omml import *  # noqa: F401, F403
from .primitives import *  # noqa: F401, F403
from .layouts_data import *  # noqa: F401, F403
from .layouts_narrative import *  # noqa: F401, F403
from .spec_pipeline import *  # noqa: F401, F403
