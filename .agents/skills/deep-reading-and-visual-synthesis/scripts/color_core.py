"""
color_core.py
CIELAB/HCL color science, palette contracts, theme derivation, and Gephi palette JS export.
Note: `hcl_color_engine` is the public entry point.
"""

import math
from typing import List, Tuple, Dict, Optional, Sequence

# D65 standard illuminant white point constants
XN = 0.95047


YN = 1.00000


ZN = 1.08883

UN_PRIME = (4.0 * XN) / (XN + 15.0 * YN + 3.0 * ZN)


VN_PRIME = (9.0 * YN) / (XN + 15.0 * YN + 3.0 * ZN)


def _hcl_to_linear_rgb(h_deg: float, c: float, l: float) -> Tuple[float, float, float]:
    """Convert H (0..360), C (>=0), L (0..100) to linear sRGB (before gamma companding)."""
    if l <= 0.0:
        return 0.0, 0.0, 0.0
    if l >= 100.0 and c <= 0.001:
        return 1.0, 1.0, 1.0

    h_rad = math.radians(h_deg % 360.0)
    u = c * math.cos(h_rad)
    v = c * math.sin(h_rad)

    u_prime = u / (13.0 * l) + UN_PRIME
    v_prime = v / (13.0 * l) + VN_PRIME

    if l > 8.0:
        y = YN * math.pow((l + 16.0) / 116.0, 3.0)
    else:
        y = YN * l * math.pow(3.0 / 29.0, 3.0)

    if abs(v_prime) < 1e-9:
        v_prime = 1e-9 if v_prime >= 0 else -1e-9

    x = y * (9.0 * u_prime) / (4.0 * v_prime)
    z = y * (12.0 - 3.0 * u_prime - 20.0 * v_prime) / (4.0 * v_prime)

    r_lin =  3.2404542 * x - 1.5371385 * y - 0.4985314 * z
    g_lin = -0.9692660 * x + 1.8760108 * y + 0.0415560 * z
    b_lin =  0.0556434 * x - 0.2040259 * y + 1.0572252 * z

    return r_lin, g_lin, b_lin


def _linear_to_srgb(v_lin: float) -> float:
    """Compand linear sRGB channel to standard gamma sRGB in range [0, 1]."""
    if v_lin <= 0.0031308:
        return 12.92 * v_lin
    return 1.055 * math.pow(v_lin, 1.0 / 2.4) - 0.055


def _is_in_srgb_gamut(r_lin: float, g_lin: float, b_lin: float, tol: float = 1e-4) -> bool:
    """Check if linear sRGB values fall within [0, 1]."""
    return (-tol <= r_lin <= 1.0 + tol and
            -tol <= g_lin <= 1.0 + tol and
            -tol <= b_lin <= 1.0 + tol)


def hcl_to_hex(h: float, c: float, l: float) -> str:
    """
    Convert (H, C, L) to a hex string (#RRGGBB).
    Uses binary search gamut clamping: if (H, C, L) is outside sRGB gamut,
    keeps H and L fixed and binary-searches for the maximum valid C.
    """
    l = max(0.0, min(100.0, float(l)))
    c = max(0.0, float(c))
    h = float(h) % 360.0

    r_lin, g_lin, b_lin = _hcl_to_linear_rgb(h, c, l)

    if not _is_in_srgb_gamut(r_lin, g_lin, b_lin):
        low, high = 0.0, c
        for _ in range(24):
            mid = (low + high) / 2.0
            r_test, g_test, b_test = _hcl_to_linear_rgb(h, mid, l)
            if _is_in_srgb_gamut(r_test, g_test, b_test):
                low = mid
            else:
                high = mid
        c = low
        r_lin, g_lin, b_lin = _hcl_to_linear_rgb(h, c, l)

    r = int(round(max(0.0, min(1.0, _linear_to_srgb(r_lin))) * 255.0))
    g = int(round(max(0.0, min(1.0, _linear_to_srgb(g_lin))) * 255.0))
    b = int(round(max(0.0, min(1.0, _linear_to_srgb(b_lin))) * 255.0))

    return f"#{r:02X}{g:02X}{b:02X}"


def common_c(hues: List[float], target_c: float, l: float) -> float:
    """Find the maximum chroma that is in-gamut for ALL given hues at luminance L."""
    l = max(0.0, min(100.0, float(l)))
    min_c = float(target_c)

    for h in hues:
        low, high = 0.0, float(target_c)
        r_lin, g_lin, b_lin = _hcl_to_linear_rgb(h, high, l)
        if not _is_in_srgb_gamut(r_lin, g_lin, b_lin):
            for _ in range(24):
                mid = (low + high) / 2.0
                r_test, g_test, b_test = _hcl_to_linear_rgb(h, mid, l)
                if _is_in_srgb_gamut(r_test, g_test, b_test):
                    low = mid
                else:
                    high = mid
            min_c = min(min_c, low)

    return round(min_c, 2)


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Parse #RGB or #RRGGBB into (r, g, b) integers (0..255)."""
    hex_clean = hex_code.strip().lstrip("#")
    if len(hex_clean) == 3:
        hex_clean = "".join([ch * 2 for ch in hex_clean])
    if len(hex_clean) != 6:
        return 0, 0, 0
    return int(hex_clean[0:2], 16), int(hex_clean[2:4], 16), int(hex_clean[4:6], 16)


def relative_luminance(hex_code: str) -> float:
    """Calculate CIE Relative Luminance Y from sRGB hex (WCAG 2.1 formula) in [0, 1]."""
    r, g, b = hex_to_rgb(hex_code)
    channels = [r / 255.0, g / 255.0, b / 255.0]
    lin_ch = [
        c / 12.92 if c <= 0.04045 else math.pow((c + 0.055) / 1.055, 2.4)
        for c in channels
    ]
    return lin_ch[0] * 0.2126 + lin_ch[1] * 0.7152 + lin_ch[2] * 0.0722


def ink(bg_hex: str, dark_ink: str = "#0F172A", light_ink: str = "#FFFFFF") -> str:
    """Auto-Ink selector using WCAG AA 4.5:1 golden crossover threshold (Y > 0.179)."""
    return dark_ink if relative_luminance(bg_hex) > 0.179 else light_ink


def wcag_contrast(fg_hex: str, bg_hex: str) -> float:
    """Calculate WCAG 2.1 contrast ratio between two hex colors."""
    y1 = relative_luminance(fg_hex)
    y2 = relative_luminance(bg_hex)
    return (max(y1, y2) + 0.05) / (min(y1, y2) + 0.05)


def gray(hex_code: str) -> str:
    """Simulate grayscale perception using CIE L* from sRGB."""
    y = relative_luminance(hex_code)
    if y > math.pow(6.0 / 29.0, 3.0):
        l_star = 116.0 * math.pow(y, 1.0 / 3.0) - 16.0
    else:
        l_star = y * math.pow(29.0 / 3.0, 3.0)
    val = int(round(max(0.0, min(100.0, l_star)) * 2.55))
    return f"#{val:02X}{val:02X}{val:02X}"


# -------------------------------------------------------------------------
# CIELAB Interpolation for Sequential & Diverging Scales
# -------------------------------------------------------------------------

def _rgb_to_xyz(r: int, g: int, b: int) -> Tuple[float, float, float]:
    channels = [r / 255.0, g / 255.0, b / 255.0]
    lin = [
        c / 12.92 if c <= 0.04045 else math.pow((c + 0.055) / 1.055, 2.4)
        for c in channels
    ]
    x = lin[0] * 0.4124564 + lin[1] * 0.3575761 + lin[2] * 0.1804375
    y = lin[0] * 0.2126729 + lin[1] * 0.7151522 + lin[2] * 0.0721750
    z = lin[0] * 0.0193339 + lin[1] * 0.1191920 + lin[2] * 0.9503041
    return x, y, z


def _xyz_to_lab(x: float, y: float, z: float) -> Tuple[float, float, float]:
    xr, yr, zr = x / XN, y / YN, z / ZN
    def f(t: float) -> float:
        return math.pow(t, 1.0 / 3.0) if t > 0.008856 else (7.787 * t) + (16.0 / 116.0)
    fx, fy, fz = f(xr), f(yr), f(zr)
    return (116.0 * fy) - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz)


def _lab_to_xyz(l_star: float, a_star: float, b_star: float) -> Tuple[float, float, float]:
    fy = (l_star + 16.0) / 116.0
    fx = a_star / 500.0 + fy
    fz = fy - b_star / 200.0
    def f_inv(t: float) -> float:
        return math.pow(t, 3.0) if t > 0.206897 else (t - 16.0 / 116.0) / 7.787
    return XN * f_inv(fx), YN * f_inv(fy), ZN * f_inv(fz)


def _xyz_to_rgb_clamped(x: float, y: float, z: float) -> Tuple[int, int, int]:
    r_lin =  3.2404542 * x - 1.5371385 * y - 0.4985314 * z
    g_lin = -0.9692660 * x + 1.8760108 * y + 0.0415560 * z
    b_lin =  0.0556434 * x - 0.2040259 * y + 1.0572252 * z
    r = int(round(max(0.0, min(1.0, _linear_to_srgb(r_lin))) * 255.0))
    g = int(round(max(0.0, min(1.0, _linear_to_srgb(g_lin))) * 255.0))
    b = int(round(max(0.0, min(1.0, _linear_to_srgb(b_lin))) * 255.0))
    return r, g, b


def hex_to_lab(hex_code: str) -> Tuple[float, float, float]:
    r, g, b = hex_to_rgb(hex_code)
    return _xyz_to_lab(*_rgb_to_xyz(r, g, b))


def lab_to_hex(l_star: float, a_star: float, b_star: float) -> str:
    r, g, b = _xyz_to_rgb_clamped(*_lab_to_xyz(l_star, a_star, b_star))
    return f"#{r:02X}{g:02X}{b:02X}"


def lab_interpolate(hex_list: List[str], t: float) -> str:
    """Interpolate between a list of hex colors in CIELAB space at normalized position t in [0, 1]."""
    if not hex_list:
        return "#000000"
    if len(hex_list) == 1:
        return hex_list[0]
    t = max(0.0, min(1.0, float(t)))
    n = len(hex_list) - 1
    scaled_t = t * n
    idx = int(math.floor(scaled_t))
    if idx >= n:
        return hex_list[-1]
    frac = scaled_t - idx
    l1, a1, b1 = hex_to_lab(hex_list[idx])
    l2, a2, b2 = hex_to_lab(hex_list[idx + 1])
    return lab_to_hex(l1 + frac * (l2 - l1), a1 + frac * (a2 - a1), b1 + frac * (b2 - b1))


# -------------------------------------------------------------------------
# Tri-Tier Area-Scaled HCL Derivation & Session Color Contract
# -------------------------------------------------------------------------

class AreaScaledHCL:
    """
    Derives 3 solid HEX tiers for any hue H based on visual area:
    - Tier 1: accent_dark  (L=38, C=56) -> borders, dark title text, icons
    - Tier 2: badge_fill   (L=46, C=62) -> solid pill fill with auto ink
    - Tier 3: surface_tint (L=96.5, C=8) -> large card background (solid hex)
    """
    def __init__(self, hue_deg: float, name: str = "", target_c: float = 60.0):
        self.hue = float(hue_deg) % 360.0
        self.name = name
        self.accent_dark = hcl_to_hex(self.hue, min(target_c, 56.0), 38.0)
        self.badge_fill = hcl_to_hex(self.hue, min(target_c, 62.0), 46.0)
        self.surface_tint = hcl_to_hex(self.hue, 8.5, 96.5)
        self.badge_ink = ink(self.badge_fill)
        self.surface_ink = ink(self.surface_tint)


DEFAULT_QUALITATIVE_HUES = [
    250.0,  # Deep Royal Blue (primary: Core System / Structure / Governance)
    35.0,   # Amber Ochre     (warn: Friction / Bottleneck / Transition)
    165.0,  # Emerald Teal    (success: Resolution / Action / Value)
    345.0,  # Rose Berry      (danger: Trap / Failure Mode / Alert)
    290.0,  # Purple Amethyst (synth: Synthesis / Cross-Domain Schema)
]

DIVERGING_HUES = (250.0, 25.0)


class SessionColorContract:
    """
    Global session color contract across Format A mindmaps, Format B PDF reports,
    Format C PPTX presentations, and Format D quantitative charts.
    Enforces universal semantic color roles:
    - primary (Core System / Structure / Governance) -> Blue (H=250)
    - warn    (Friction / Bottleneck / Transition)   -> Ochre (H=35)
    - success (Resolution / Action / Value)          -> Teal (H=165)
    - danger  (Trap / Failure Mode / Alert)          -> Rose (H=345)
    - synth   (Synthesis / Cross-Domain Schema)      -> Purple (H=290)
    """
    def __init__(self, hues: Optional[List[float]] = None):
        self.hues = hues or DEFAULT_QUALITATIVE_HUES
        eq_c = common_c(self.hues, 58.0, 42.0)

        self.blue = AreaScaledHCL(self.hues[0], "blue", target_c=eq_c)
        self.ochre = AreaScaledHCL(self.hues[1], "ochre", target_c=eq_c)
        self.teal = AreaScaledHCL(self.hues[2], "teal", target_c=eq_c)
        self.rose = AreaScaledHCL(self.hues[3], "rose", target_c=eq_c)
        self.purple = AreaScaledHCL(self.hues[4], "purple", target_c=eq_c)

        self.neutral_surface = "#F8FAFC"
        self.neutral_border = "#E2E8F0"
        self.neutral_dark = "#0F172A"
        self.neutral_muted = "#475569"

        self.mapping: Dict[str, AreaScaledHCL] = {
            "primary": self.blue,
            "warn": self.ochre,
            "success": self.teal,
            "danger": self.rose,
            "synth": self.purple,
        }

    def _as_dict(self) -> Dict[str, object]:
        return {
            "bg_canvas": self.neutral_surface,
            "bg_card": "#FFFFFF",
            "border_card": "#CBD5E1",
            "ink_primary": self.neutral_dark,
            "ink_secondary": "#334155",
            "ink_muted": self.neutral_muted,
            "primary_accent": self.blue.accent_dark,
            "primary_tint": self.blue.surface_tint,
            "warn_accent": self.ochre.accent_dark,
            "warn_tint": self.ochre.surface_tint,
            "success_accent": self.teal.accent_dark,
            "success_tint": self.teal.surface_tint,
            "danger_accent": self.rose.accent_dark,
            "danger_tint": self.rose.surface_tint,
            "synth_accent": self.purple.accent_dark,
            "synth_tint": self.purple.surface_tint,
            "gephi_qualitative_4": list(GEPHI_QUALITATIVE_HEX),
            "gephi_badge_tints_4": list(GEPHI_LIGHT_BADGE_TINTS),
            "gephi_other": GEPHI_DISCRETE_NEUTRALS["other_aggregated"],
            "gephi_na": GEPHI_DISCRETE_NEUTRALS["na_missing"],
        }

    def __getitem__(self, key: str) -> object:
        d = self._as_dict()
        if key in d:
            return d[key]
        if key in self.mapping:
            return self.mapping[key]
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Unknown key '{key}' in SessionColorContract")

    def get(self, key: str, default: object = None) -> object:
        try:
            return self[key]
        except KeyError:
            return default

    def get_sequential_ladder(self, steps: int = 3, base_h: float = 245.0) -> List[Tuple[str, str, str]]:
        """Returns a sequence of (border, badge_fill, surface_tint) with monotonic luminance."""
        ladder = []
        l_steps = [48.0, 39.0, 30.0] if steps == 3 else [52.0 - i * 8.0 for i in range(steps)]
        tint_steps = [97.5, 96.0, 94.5] if steps == 3 else [98.0 - i * 1.5 for i in range(steps)]
        for i in range(steps):
            accent = hcl_to_hex(base_h, 55.0, l_steps[i])
            badge = hcl_to_hex(base_h, 58.0, l_steps[i] + 4.0)
            tint = hcl_to_hex(base_h, 8.0, tint_steps[i])
            ladder.append((accent, badge, tint))
        return ladder

    def get_diverging_pair(self) -> Tuple[AreaScaledHCL, AreaScaledHCL]:
        """Returns balanced opposing hues for diverging contrast."""
        h_left, h_right = DIVERGING_HUES
        return AreaScaledHCL(h_left, "diverging_left", target_c=58.0), AreaScaledHCL(h_right, "diverging_right", target_c=58.0)


GLOBAL_COLOR_CONTRACT = SessionColorContract()


# -------------------------------------------------------------------------
# Chart & Data Dashboard Color Specification (Format D <-> Format E SSOT)
# Public Neutral Fallback Palette (automatically overridden by active user_preferences.json)
# -------------------------------------------------------------------------

LOCKED_CHART_PALETTE_URL = ""

# 2. Fixed Qualitative Palette (4 base categories in strict binding order)
GEPHI_QUALITATIVE_HEX: List[str] = [
    "#3B82F6",  # 1. Primary: Royal Blue
    "#0D9488",  # 2. Secondary: Teal
    "#F59E0B",  # 3. Tertiary: Warm Amber
    "#6366F1",  # 4. Quaternary: Indigo
]

GEPHI_QUALITATIVE_NAMED: Dict[str, str] = {
    "primary_orange": "#3B82F6",
    "secondary_blue": "#0D9488",
    "tertiary_pink": "#F59E0B",
    "quaternary_green": "#6366F1",
}

# 3. Four 5-Node Sequential Scales (0.00, 0.25, 0.50, 0.75, 1.00; low=light -> high=dark)
GEPHI_SEQUENTIAL_SCALES: Dict[str, List[str]] = {
    "orange": ["#F1F5FE", "#A4C2FB", "#3B82F6", "#234F97", "#0D244C"],  # (1) Primary sequential scale
    "blue":   ["#ECF6F5", "#94CBC5", "#0D9488", "#075951", "#022D28"],  # (2) Secondary sequential scale
    "pink":   ["#FEF6E9", "#FAD08C", "#F59E0B", "#9A6105", "#4D2E00"],  # (3) Tertiary sequential scale
    "green":  ["#F3F2FE", "#B3B2FA", "#6366F1", "#3B3D96", "#1B1C4E"],  # (4) Quaternary sequential scale
}

# 5. 9-Node Symmetric Diverging Scale (0.000 to 1.000, center=0.500 -> #F5F6F7)
GEPHI_DIVERGING_SCALE: List[str] = [
    "#022D28",  # 0.000 (-100% negative extreme)
    "#075951",  # 0.125 (-75%)
    "#0D9488",  # 0.250 (-50%)
    "#94CBC5",  # 0.375 (-25%)
    "#F5F6F7",  # 0.500 (0% neutral center)
    "#A4C2FB",  # 0.625 (+25%)
    "#3B82F6",  # 0.750 (+50%)
    "#234F97",  # 0.875 (+75%)
    "#0D244C",  # 1.000 (+100% positive extreme)
]

# 6. Neutral & Special Semantic Colors
GEPHI_DISCRETE_NEUTRALS: Dict[str, str] = {
    "diverging_center": "#F5F6F7",  # 發散中心（極低彩度中性冷灰）
    "na_missing": "#D9D9D9",        # 缺失值（NA / Null）預設標記色
    "other_aggregated": "#CBD5E1",  # 4+1 長尾聚合「其他項目」典雅淺灰
}


KNOWN_NA_STRINGS = {
    "na", "n/a", "null", "none", "nan", "",
    "-", "—", "--", "－", "...", "…", "＊", "*", "?", "？",
    "無資料", "缺漏", "未公布",
}

RESERVED_OTHER_LABELS = {
    "其他", "其它", "未分類", "其他項", "其他類", "其他項目",
    "其他項目合計", "其餘明細項目合計", "其餘明細與原表其他項合計",
    "other", "others", "unclassified",
}


_SEQUENTIAL_SCALE_ALIASES: Dict[str, str] = {
    "orange": "orange",
    "primary": "orange",
    "primary_orange": "orange",
    "1": "orange",
    "blue": "blue",
    "secondary": "blue",
    "secondary_blue": "blue",
    "2": "blue",
    "pink": "pink",
    "tertiary": "pink",
    "tertiary_pink": "pink",
    "3": "pink",
    "green": "green",
    "quaternary": "green",
    "quaternary_green": "green",
    "4": "green",
}


def get_sequential_color(
    value: object,
    v_min: float,
    v_max: float,
    scale: str = "orange",
    discrete_steps: bool = False,
    scale_key: Optional[str] = None,
) -> str:
    """
    Map a continuous or ordinal value to one of the 4 locked 5-node sequential scales.
    - Uses CIELAB piecewise linear interpolation (no alpha channel manipulation).
    - Returns #D9D9D9 for None, NaN, np.nan, or 'NA'/'null' strings.
    """
    from chart_data import _parse_numeric_or_na

    v = _parse_numeric_or_na(value)
    if v is None:
        return GEPHI_DISCRETE_NEUTRALS["na_missing"]
    chosen_scale = scale_key if scale_key is not None else scale
    resolved_key = _SEQUENTIAL_SCALE_ALIASES.get(str(chosen_scale).strip().lower())
    if resolved_key is None:
        raise ValueError(
            f"Unknown sequential scale '{chosen_scale}'. Locked palette only permits: "
            f"{list(GEPHI_SEQUENTIAL_SCALES.keys())}"
        )
    nodes = GEPHI_SEQUENTIAL_SCALES[resolved_key]
    if v_max <= v_min:
        return nodes[2]
    p = max(0.0, min(1.0, (v - float(v_min)) / (float(v_max) - float(v_min))))
    if discrete_steps:
        idx = int(round(p * 4.0))
        return nodes[max(0, min(4, idx))]
    return lab_interpolate(nodes, p)


def get_diverging_color(
    value: object,
    center: float = 0.0,
    max_span: Optional[float] = None,
    discrete_steps: bool = False,
) -> str:
    """
    Map a value with a meaningful reference center (e.g., 0% growth or 100% target achievement)
    symmetrically onto the 9-node diverging scale (Blue <- #F5F6F7 -> Orange).
    - Returns #D9D9D9 for None, NaN, np.nan, or 'NA'/'null' strings.
    """
    from chart_data import _parse_numeric_or_na

    v = _parse_numeric_or_na(value)
    if v is None:
        return GEPHI_DISCRETE_NEUTRALS["na_missing"]
    span = abs(float(max_span)) if (max_span is not None and abs(float(max_span)) > 0) else 1.0
    deviation = (v - float(center)) / span
    clamped_dev = max(-1.0, min(1.0, deviation))
    p = 0.5 + 0.5 * clamped_dev  # Maps [-1, +1] symmetrically to [0.0, 1.0] with 0 -> 0.5
    if discrete_steps:
        idx = int(round(p * 8.0))
        return GEPHI_DIVERGING_SCALE[max(0, min(8, idx))]
    return lab_interpolate(GEPHI_DIVERGING_SCALE, p)


def _resolve_lookup_color(
    label: object,
    category_color_map: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    """Read-only lookup for a pre-registered entity color (never registers new entities)."""
    if label is None:
        return None
    raw = str(label)
    stripped = raw.strip()
    if category_color_map:
        if raw in category_color_map:
            return category_color_map[raw]
        if stripped in category_color_map:
            return category_color_map[stripped]
    from color_registry import get_active_registry

    reg = get_active_registry()
    if reg is not None:
        return reg.hex_for(label)
    return None


def bind_qualitative_colors(
    categories: List[object],
    allow_top4_aggregation: bool = False,
    other_label: str = "其他項目合計",
    registry: Optional[object] = None,
) -> Dict[str, str]:
    """
    Bind unordered categories to fixed qualitative colors in strict order (`GEPHI_QUALITATIVE_HEX`).
    - When a CategoryColorRegistry is provided or active via `use_session_registry()`, delegates
      to the persistent session registry so identical categories keep identical colors across charts.
    - Deduplicates categories in order of first appearance so repeated occurrences in data rows
      never overwrite an already-bound category or inflate the unique category count.
    - Maps missing/NA category markers ('NA', 'Null', None, '', '-', '...', '＊', etc.) to #D9D9D9 without consuming a slot.
    - Enforces df_other / 4+1 disambiguation: reserved 'other/unclassified' labels ('其他', '未分類',
      '其餘明細項目合計', '其餘明細與原表其他項合計', `other_label`) never consume a top-4 primary color slot
      and always map to #CBD5E1 (`other_aggregated`).
    - If unique valid categories > 4 and allow_top4_aggregation is False, raises ValueError to enforce
      confirming expansion strategy with the user first.
    - If allow_top4_aggregation is True, binds the first 4 unique categories to the 4 primary colors and
      maps remaining categories (plus `other_label`) to #CBD5E1.
    """
    if registry is None:
        from color_registry import get_active_registry

        registry = get_active_registry()

    if registry is not None:
        result = registry.assign(
            categories,
            overflow="other" if allow_top4_aggregation else "raise",
        )
        if allow_top4_aggregation:
            result[other_label] = GEPHI_DISCRETE_NEUTRALS["other_aggregated"]
        return result

    bound: Dict[str, str] = {}
    unique_valid: List[str] = []

    for raw_cat in categories:
        if raw_cat is None:
            bound["NA"] = GEPHI_DISCRETE_NEUTRALS["na_missing"]
            continue
        cat = str(raw_cat).strip()
        cat_lower = cat.lower()
        if cat_lower in KNOWN_NA_STRINGS:
            bound[cat or "NA"] = GEPHI_DISCRETE_NEUTRALS["na_missing"]
            continue
        if cat == other_label or cat in RESERVED_OTHER_LABELS or cat_lower in RESERVED_OTHER_LABELS:
            bound[cat] = GEPHI_DISCRETE_NEUTRALS["other_aggregated"]
            continue
        if cat not in unique_valid:
            unique_valid.append(cat)

    if len(unique_valid) > 4 and not allow_top4_aggregation:
        raise ValueError(
            f"Unique category count ({len(unique_valid)}) exceeds the 4 locked qualitative colors. "
            "Per color specification Rule 5 & 7.5, either confirm expansion mode with the user "
            "or enable Smart 4+1 aggregation (allow_top4_aggregation=True)."
        )

    for idx, cat in enumerate(unique_valid):
        if idx < 4:
            bound[cat] = GEPHI_QUALITATIVE_HEX[idx]
        else:
            bound[cat] = GEPHI_DISCRETE_NEUTRALS["other_aggregated"]

    if allow_top4_aggregation:
        bound[other_label] = GEPHI_DISCRETE_NEUTRALS["other_aggregated"]
    return bound


# 7. Zero-Alpha Light Badge Tints (0.00 nodes of the 4 sequential scales)
GEPHI_LIGHT_BADGE_TINTS: List[str] = [
    "#F1F5FE",  # 1. Primary 0.00 light tint
    "#ECF6F5",  # 2. Secondary 0.00 light tint
    "#FEF6E9",  # 3. Tertiary 0.00 light tint
    "#F3F2FE",  # 4. Quaternary 0.00 light tint
]

GEPHI_LIGHT_BADGE_TINTS_MAP: Dict[str, str] = {
    "0": "#F1F5FE",
    "1": "#ECF6F5",
    "2": "#FEF6E9",
    "3": "#F3F2FE",
    "orange": "#F1F5FE",
    "primary": "#F1F5FE",
    "primary_orange": "#F1F5FE",
    "#3B82F6": "#F1F5FE",
    "blue": "#ECF6F5",
    "secondary": "#ECF6F5",
    "secondary_blue": "#ECF6F5",
    "#0D9488": "#ECF6F5",
    "pink": "#FEF6E9",
    "tertiary": "#FEF6E9",
    "tertiary_pink": "#FEF6E9",
    "#F59E0B": "#FEF6E9",
    "green": "#F3F2FE",
    "quaternary": "#F3F2FE",
    "quaternary_green": "#F3F2FE",
    "#6366F1": "#F3F2FE",
}


def get_category_badge_tint(
    cat_or_key: object,
    category_color_map: Optional[Dict[str, str]] = None,
) -> str:
    """
    Return the zero-alpha light badge surface tint corresponding to the 0.00 node
    of the 4 active sequential scales. Falls back to #F1F5F9 for aggregated 'other' or neutral items.
    """
    if isinstance(cat_or_key, int):
        if 0 <= cat_or_key < 4:
            return GEPHI_LIGHT_BADGE_TINTS[cat_or_key]
        return "#F1F5F9"
    key_str = str(cat_or_key).strip()
    if category_color_map and key_str in category_color_map:
        mapped_hex = category_color_map[key_str].upper()
        if mapped_hex in GEPHI_LIGHT_BADGE_TINTS_MAP:
            return GEPHI_LIGHT_BADGE_TINTS_MAP[mapped_hex]
    lookup = GEPHI_LIGHT_BADGE_TINTS_MAP.get(key_str) or GEPHI_LIGHT_BADGE_TINTS_MAP.get(key_str.upper()) or GEPHI_LIGHT_BADGE_TINTS_MAP.get(key_str.lower())
    return lookup if lookup else "#F1F5F9"


def _normalize_hex(hex_code: str) -> str:
    """Validate and normalize #RGB / RGB / #RRGGBB / RRGGBB to canonical uppercase #RRGGBB."""
    import re
    clean = str(hex_code or "").strip().lstrip("#")
    if len(clean) == 3:
        clean = "".join(ch * 2 for ch in clean)
    if len(clean) != 6 or not re.fullmatch(r"[0-9A-Fa-f]{6}", clean):
        raise ValueError(f"Invalid hex color: {hex_code!r}")
    return f"#{clean.upper()}"


def export_gephi_palette_js(
    output_path: str,
    palette_dict: Optional[Dict[str, object]] = None,
    registry: Optional[object] = None,
) -> str:
    """
    Export the standalone pure-JS CIELAB color engine (`gephi_palette.js`)
    to `output_path` so Format E web dashboards share 100% identical color math with Python.
    If `palette_dict` is provided, embeds that palette's colors into the generated JS file.
    If a CategoryColorRegistry is provided or active, embeds `entityColors` and `entityAliases`.
    """
    import json
    import re
    from pathlib import Path
    if registry is None:
        from color_registry import get_active_registry

        registry = get_active_registry()
    src_js = Path(__file__).resolve().parent / "gephi_palette.js"
    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    if not src_js.exists():
        raise FileNotFoundError(f"Master gephi_palette.js not found at {src_js}")
    content = src_js.read_text(encoding="utf-8")
    p_dict = palette_dict if palette_dict is not None else {
        "qualitative_4": list(GEPHI_QUALITATIVE_HEX),
        "light_badge_tints_4": list(GEPHI_LIGHT_BADGE_TINTS),
        "sequential_scales": dict(GEPHI_SEQUENTIAL_SCALES),
        "diverging_9": list(GEPHI_DIVERGING_SCALE),
        "discrete_neutrals": dict(GEPHI_DISCRETE_NEUTRALS),
    }
    cats = list(p_dict.get("qualitative_4") or p_dict.get("categories") or GEPHI_QUALITATIVE_HEX)
    tints = list(p_dict.get("light_badge_tints_4") or p_dict.get("badgeTints") or GEPHI_LIGHT_BADGE_TINTS)
    seqs = dict(p_dict.get("sequential_scales") or {})
    seq_orange = list(seqs.get("orange") or p_dict.get("seqOrange") or GEPHI_SEQUENTIAL_SCALES["orange"])
    seq_blue = list(seqs.get("blue") or p_dict.get("seqBlue") or GEPHI_SEQUENTIAL_SCALES["blue"])
    seq_pink = list(seqs.get("pink") or p_dict.get("seqPink") or GEPHI_SEQUENTIAL_SCALES["pink"])
    seq_green = list(seqs.get("green") or p_dict.get("seqGreen") or GEPHI_SEQUENTIAL_SCALES["green"])
    div9 = list(p_dict.get("diverging_9") or p_dict.get("divergingHex") or GEPHI_DIVERGING_SCALE)
    neutrals = dict(p_dict.get("discrete_neutrals") or {})
    other_hex = neutrals.get("other_aggregated") or p_dict.get("other") or "#CBD5E1"
    na_hex = neutrals.get("na_missing") or p_dict.get("na") or "#D9D9D9"
    div_center = neutrals.get("diverging_center") or p_dict.get("divergingCenter") or "#F5F6F7"
    entity_colors = registry.to_js_entity_colors() if registry is not None else dict(p_dict.get("entityColors") or {})
    entity_aliases = dict(registry.aliases) if registry is not None else dict(p_dict.get("entityAliases") or {})
    replacement_block = (
        "  const PALETTE = {\n"
        f"    categories: {json.dumps(cats)},\n"
        f"    badgeTints: {json.dumps(tints)},\n"
        f"    other: {json.dumps(other_hex)},\n"
        f"    na: {json.dumps(na_hex)},\n"
        f"    divergingCenter: {json.dumps(div_center)},\n"
        f"    seqOrange: {json.dumps(seq_orange)},\n"
        f"    seqBlue:   {json.dumps(seq_blue)},\n"
        f"    seqPink:   {json.dumps(seq_pink)},\n"
        f"    seqGreen:  {json.dumps(seq_green)},\n"
        f"    divergingHex: {json.dumps(div9)},\n"
        f"    entityColors: {json.dumps(entity_colors, ensure_ascii=False)},\n"
        f"    entityAliases: {json.dumps(entity_aliases, ensure_ascii=False)}\n"
        "  };"
    )
    content = re.sub(
        r"  const PALETTE = \{[\s\S]*?\n  \};",
        replacement_block,
        content,
        count=1,
    )
    out_file.write_text(content, encoding="utf-8")
    return str(out_file)


def build_palette_from_primary_hexes(
    hex_list: List[str],
    palette_id: str = "custom_cielab_palette",
    palette_name: str = "Custom CIELAB Palette",
    sync_js_path: Optional[str] = None,
) -> Dict[str, object]:
    """
    Build a complete Format D & E chart palette from 2 to 4 primary HEX colors using CIELAB interpolation:
    - Normalizes or expands 2~4 input colors into 4 qualitative base colors.
    - Derives `0.00` zero-alpha light badge surface tints (mixed 88% toward pure white #FFFFFF in CIELAB).
    - Derives 4 sets of 5-node sequential scales (`orange`/`primary`, `blue`/`secondary`, `pink`/`tertiary`, `green`/`quaternary`).
    - Derives a 9-node symmetric diverging scale (`secondary[1.00]` <-> `#F5F6F7` <-> `primary[1.00]`).
    - Optionally syncs and regenerates `gephi_palette.js` at `sync_js_path`.
    """
    raw_inputs = [str(h).strip() for h in (hex_list or []) if str(h).strip()]
    if len(raw_inputs) < 2 or len(raw_inputs) > 4:
        raise ValueError(f"build_palette_from_primary_hexes requires 2 to 4 hex colors; got {len(raw_inputs)}.")

    # Validate and normalize hex format to canonical #RRGGBB
    cleaned = [_normalize_hex(h) for h in raw_inputs]

    qual_4 = list(cleaned)
    if len(qual_4) == 2:
        # Derive 3rd and 4th balanced colors by rotating in Lab (a*, b*) plane at L*=72
        l1, a1, b1 = hex_to_lab(qual_4[0])
        l2, a2, b2 = hex_to_lab(qual_4[1])
        qual_4.append(lab_to_hex(72.0, -b1 * 0.85, a1 * 0.85))
        qual_4.append(lab_to_hex(72.0, -b2 * 0.85, a2 * 0.85))
    elif len(qual_4) == 3:
        l1, a1, b1 = hex_to_lab(qual_4[0])
        qual_4.append(lab_to_hex(72.0, -a1 * 0.75, -b1 * 0.75))

    scale_keys = ["orange", "blue", "pink", "green"]
    seq_scales: Dict[str, List[str]] = {}
    badge_tints: List[str] = []

    for idx, base_hex in enumerate(qual_4[:4]):
        l_b, a_b, b_b = hex_to_lab(base_hex)
        # 0.00 ultra-light zero-alpha tint (L* ≈ 96.5, low chroma)
        node_00 = lab_to_hex(96.5, a_b * 0.14, b_b * 0.14)
        # 0.25 light node
        node_25 = lab_interpolate([node_00, base_hex], 0.50)
        # 0.50 base color
        node_50 = base_hex
        # 1.00 ultra-deep node (L* ≈ 32, rich chroma)
        node_100 = lab_to_hex(max(26.0, min(36.0, l_b * 0.46)), a_b * 1.12, b_b * 1.12)
        # 0.75 deep node
        node_75 = lab_interpolate([base_hex, node_100], 0.50)

        seq_scales[scale_keys[idx]] = [node_00, node_25, node_50, node_75, node_100]
        badge_tints.append(node_00)

    neg_extreme = seq_scales["blue"][4]
    neg_mid = seq_scales["blue"][2]
    center_neutral = "#F5F6F7"
    pos_mid = seq_scales["orange"][2]
    pos_extreme = seq_scales["orange"][4]

    diverging_9 = [
        neg_extreme,
        lab_interpolate([neg_extreme, neg_mid], 0.50),
        neg_mid,
        lab_interpolate([neg_mid, center_neutral], 0.55),
        center_neutral,
        lab_interpolate([center_neutral, pos_mid], 0.45),
        pos_mid,
        lab_interpolate([pos_mid, pos_extreme], 0.50),
        pos_extreme,
    ]

    palette_obj: Dict[str, object] = {
        "palette_id": palette_id,
        "palette_name": palette_name,
        "owner_only": False,
        "qualitative_4": qual_4[:4],
        "light_badge_tints_4": badge_tints,
        "sequential_scales": seq_scales,
        "diverging_9": diverging_9,
        "discrete_neutrals": {
            "diverging_center": center_neutral,
            "na_missing": "#D9D9D9",
            "other_aggregated": "#CBD5E1",
            "context_baseline_gray": "#CBD5E1",
        },
        # JS-compatible aliases so objects can be passed interchangeably between Python and JS
        "categories": qual_4[:4],
        "badgeTints": badge_tints,
        "seqOrange": seq_scales["orange"],
        "seqBlue": seq_scales["blue"],
        "seqPink": seq_scales["pink"],
        "seqGreen": seq_scales["green"],
        "divergingHex": diverging_9,
    }

    if sync_js_path:
        export_gephi_palette_js(sync_js_path, palette_dict=palette_obj)

    return palette_obj


def activate_chart_palette(palette_dict_or_id: object, prefs_path: Optional[str] = None) -> Dict[str, object]:
    """
    Switch the active runtime palette in `hcl_color_engine` (updating module-level lists/dicts in-place
    so existing imports remain 100% synchronized).
    Accepts either a palette dict (from `build_palette_from_primary_hexes` or JS `buildPaletteFromPrimaryHexes`)
    or a `palette_id` string present in `config/user_preferences.json`.
    """
    if isinstance(palette_dict_or_id, str):
        from owner_sync import check_user_identity_and_load_prefs

        prefs = check_user_identity_and_load_prefs(prefs_path=prefs_path)
        palettes = prefs.get("color_sets", {}).get("chart_palettes", {})
        lookup_id = palette_dict_or_id
        if lookup_id not in palettes and lookup_id in ("gephi_pastel", "owner_gephi_pastel") and "gephi_pastel_locked" in palettes:
            lookup_id = "gephi_pastel_locked"
        if lookup_id not in palettes:
            raise KeyError(
                f"Palette '{palette_dict_or_id}' not found or isolated for current user. "
                f"Available palettes: {list(palettes.keys())}"
            )
        p_dict = palettes[lookup_id]
    elif isinstance(palette_dict_or_id, dict):
        p_dict = palette_dict_or_id
    else:
        raise TypeError("palette_dict_or_id must be a palette_id str or palette dict.")

    qual = [_normalize_hex(c) for c in (p_dict.get("qualitative_4") or p_dict.get("categories") or [])]
    tints = [_normalize_hex(c) for c in (p_dict.get("light_badge_tints_4") or p_dict.get("badgeTints") or [])]
    raw_seqs = dict(p_dict.get("sequential_scales") or {})
    seqs = {
        "orange": list(raw_seqs.get("orange") or p_dict.get("seqOrange") or GEPHI_SEQUENTIAL_SCALES["orange"]),
        "blue": list(raw_seqs.get("blue") or p_dict.get("seqBlue") or GEPHI_SEQUENTIAL_SCALES["blue"]),
        "pink": list(raw_seqs.get("pink") or p_dict.get("seqPink") or GEPHI_SEQUENTIAL_SCALES["pink"]),
        "green": list(raw_seqs.get("green") or p_dict.get("seqGreen") or GEPHI_SEQUENTIAL_SCALES["green"]),
    }
    div9 = list(p_dict.get("diverging_9") or p_dict.get("divergingHex") or GEPHI_DIVERGING_SCALE)
    neutrals = dict(p_dict.get("discrete_neutrals") or {})

    GEPHI_QUALITATIVE_HEX[:] = qual
    GEPHI_LIGHT_BADGE_TINTS[:] = tints
    for k in ("orange", "blue", "pink", "green"):
        if k in seqs:
            GEPHI_SEQUENTIAL_SCALES[k] = list(seqs[k])
    GEPHI_DIVERGING_SCALE[:] = div9
    GEPHI_DISCRETE_NEUTRALS.update(neutrals)

    GEPHI_QUALITATIVE_NAMED["primary_orange"] = qual[0]
    GEPHI_QUALITATIVE_NAMED["secondary_blue"] = qual[1]
    GEPHI_QUALITATIVE_NAMED["tertiary_pink"] = qual[2]
    GEPHI_QUALITATIVE_NAMED["quaternary_green"] = qual[3]

    GEPHI_LIGHT_BADGE_TINTS_MAP.clear()
    GEPHI_LIGHT_BADGE_TINTS_MAP.update({
        "0": tints[0], "1": tints[1], "2": tints[2], "3": tints[3],
        "orange": tints[0], "primary": tints[0], "primary_orange": tints[0], qual[0].upper(): tints[0],
        "blue": tints[1], "secondary": tints[1], "secondary_blue": tints[1], qual[1].upper(): tints[1],
        "pink": tints[2], "tertiary": tints[2], "tertiary_pink": tints[2], qual[2].upper(): tints[2],
        "green": tints[3], "quaternary": tints[3], "quaternary_green": tints[3], qual[3].upper(): tints[3],
    })
    return p_dict


def _auto_init_active_palette() -> None:
    """
    On module import, automatically restore local private config from `reading_sessions/_owner_private_config`
    if present and activate `active_chart_palette_id` from `config/user_preferences.json` so
    `GEPHI_QUALITATIVE_HEX` and related globals immediately reflect the user's or owner's active palette.
    """
    import json
    import shutil
    from pathlib import Path

    try:
        skill_root = Path(__file__).resolve().parents[1]
        workspace_root = skill_root.parents[2] if len(skill_root.parents) >= 3 else skill_root.parent
        cfg_dir = skill_root / "config"
        cfg_prefs = cfg_dir / "user_preferences.json"
        priv_cfg_dir = workspace_root / "reading_sessions" / "_owner_private_config"
        priv_prefs = priv_cfg_dir / "user_preferences.json"

        if not cfg_prefs.exists() and priv_prefs.exists():
            cfg_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(priv_prefs, cfg_prefs)
            priv_styles = priv_cfg_dir / "owner_styles"
            cfg_styles = cfg_dir / "owner_styles"
            if priv_styles.exists():
                cfg_styles.mkdir(parents=True, exist_ok=True)
                for src_md in priv_styles.glob("*.md"):
                    dst_md = cfg_styles / src_md.name
                    if not dst_md.exists():
                        shutil.copy2(src_md, dst_md)

        if cfg_prefs.exists():
            prefs = json.loads(cfg_prefs.read_text(encoding="utf-8"))
            color_sets = prefs.get("color_sets", {})
            active_pid = color_sets.get("active_chart_palette_id")
            palettes = color_sets.get("chart_palettes", {})
            if active_pid and isinstance(palettes, dict) and active_pid in palettes:
                activate_chart_palette(palettes[active_pid])
    except Exception:
        pass
_auto_init_active_palette()



THEMATIC_PALETTE_PRESETS: Dict[str, Tuple[str, List[str]]] = {
    "milk_tea": ("RE:LAB Milk Tea & Caramel Palette", ["#C87D55", "#5C8D89", "#D9A05B", "#8C5A3C"]),
    "bubble_tea": ("RE:LAB Bubble Tea & Caramel Palette", ["#C87D55", "#5C8D89", "#D9A05B", "#8C5A3C"]),
    "forest_eco": ("Forest Canopy & Eco Sustainability Palette", ["#3A7D44", "#2C6E8F", "#C98A3E", "#6B8E23"]),
    "matcha_forest": ("Matcha & Forest Botanical Palette", ["#3A7D44", "#2C6E8F", "#C98A3E", "#6B8E23"]),
    "ocean_blue": ("Pelagic Ocean & Hydro Palette", ["#0284C7", "#0D9488", "#E07A5F", "#4F46E5"]),
    "ocean_hydro": ("Pelagic Ocean & Hydro Palette", ["#0284C7", "#0D9488", "#E07A5F", "#4F46E5"]),
    "coffee_roast": ("Roasted Espresso & Crema Palette", ["#7F4F24", "#4A7C59", "#C68B59", "#9C6644"]),
    "pineapple_tropical": ("Tropical Pineapple & Agro Export Palette", ["#D97706", "#15803D", "#0284C7", "#B45309"]),
    "agri_gold": ("Tropical Pineapple & Agro Export Palette", ["#D97706", "#15803D", "#0284C7", "#B45309"]),
}


def _expand_single_hex_to_four(hex_code: str) -> List[str]:
    """Expand a single representative topic hex color into 4 perceptually balanced CIELAB base colors."""
    base_hex = _normalize_hex(hex_code)
    l_val, a_val, b_val = hex_to_lab(base_hex)
    target_l = max(52.0, min(72.0, l_val))
    c2 = lab_to_hex(target_l, -b_val * 0.88, a_val * 0.88)
    c3 = lab_to_hex(target_l, b_val * 0.82, -a_val * 0.82)
    c4 = lab_to_hex(target_l, -a_val * 0.78, -b_val * 0.78)
    return [base_hex, c2, c3, c4]


def derive_thematic_palette(
    theme_preset_or_hex: object,
    sync_js_path: Optional[str] = None,
    activate: bool = False,
    **kwargs,
) -> Dict[str, object]:
    """
    Data 7 RE:LAB Thematic CIELAB Palette Derivation:
    - Accepts a preset name (`"milk_tea"`, `"forest_eco"`, `"ocean_blue"`, `"coffee_roast"`, `"pineapple_tropical"`),
      a single topic HEX string (e.g. `"#C87D55"`), or a list of 1..4 HEX strings.
    - Derives a complete CIELAB-calibrated palette (4 qualitative colors, 4 zero-alpha light badge tints,
      four 5-node sequential scales, and 9-node symmetric diverging scale).
    - Optionally syncs `gephi_palette.js` at `sync_js_path` and activates the palette in-place if `activate=True`.
    """
    palette_id = str(kwargs.pop("palette_id", "thematic_cielab_palette"))
    palette_name = str(kwargs.pop("palette_name", "Thematic CIELAB Palette"))

    if isinstance(theme_preset_or_hex, str):
        key = theme_preset_or_hex.strip().lower().replace("-", "_").replace(" ", "_")
        if key in THEMATIC_PALETTE_PRESETS:
            preset_title, hex_list = THEMATIC_PALETTE_PRESETS[key]
            palette_id = f"thematic_{key}"
            palette_name = preset_title
        else:
            hex_list = _expand_single_hex_to_four(theme_preset_or_hex.strip())
    elif isinstance(theme_preset_or_hex, (list, tuple)):
        cleaned = [str(h).strip() for h in theme_preset_or_hex if str(h).strip()]
        if not cleaned:
            raise ValueError("derive_thematic_palette received an empty list.")
        hex_list = _expand_single_hex_to_four(cleaned[0]) if len(cleaned) == 1 else cleaned[:4]
    else:
        raise TypeError("theme_preset_or_hex must be a preset name str, a HEX str, or a sequence of HEX strings.")

    palette_obj = build_palette_from_primary_hexes(
        hex_list,
        palette_id=palette_id,
        palette_name=palette_name,
        sync_js_path=sync_js_path,
    )
    if activate:
        activate_chart_palette(palette_obj)
    return palette_obj


SLIDE_TOPIC_SEMANTIC_SEEDS: Dict[str, Tuple[str, str]] = {
    "academic": ("Academic Slate & Ink Theme", "#1D4ED8"),
    "tech": ("Deep Tech Cobalt Theme", "#2563EB"),
    "ai": ("Algorithmic Indigo & Slate Theme", "#4338CA"),
    "data": ("Empirical Cyan & Slate Theme", "#0369A1"),
    "finance": ("Institutional Forest & Brass Theme", "#166534"),
    "medical": ("Clinical Teal & Ceramic Theme", "#0F766E"),
    "healthcare": ("Clinical Teal & Ceramic Theme", "#0F766E"),
    "climate": ("Ecological Moss & Earth Theme", "#2E6F40"),
    "energy": ("Solar Amber & Graphite Theme", "#B45309"),
    "legal": ("Jurisprudence Burgundy & Ivory Theme", "#9F1239"),
    "education": ("Campus Cobalt & Warm Paper Theme", "#1E40AF"),
    "retail": ("Editorial Terracotta & Linen Theme", "#C2410C"),
}

# Ordered (seed_key, keywords) table for Chinese & English free-text topic routing
_SLIDE_TOPIC_KEYWORD_RULES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("milk_tea", ("奶茶", "手搖", "手搖飲", "茶飲", "飲料店", "bubble tea", "milk tea", "boba")),
    ("coffee_roast", ("咖啡", "烘豆", "烘焙", "拿鐵", "espresso", "coffee", "cafe", "roast")),
    ("pineapple_tropical", ("鳳梨", "農業", "農產", "水果", "食品", "pineapple", "agriculture", "agro", "farm")),
    ("ocean_blue", ("海洋", "水資源", "航運", "漁業", "觀光", "旅遊", "海運", "ocean", "marine", "hydro", "tourism", "travel")),
    ("medical", ("醫療", "醫學", "臨床", "健保", "醫院", "生技", "健康", "公衛", "癌症", "製藥", "medical", "healthcare", "clinical", "biotech", "hospital", "pharma")),
    ("climate", ("氣候", "環保", "永續", "碳排", "淨零", "森林", "生態", "環境", "綠能", "esg", "climate", "ecology", "sustainability", "carbon", "forest", "green")),
    ("finance", ("金融", "財報", "預算", "投資", "經濟", "銀行", "股市", "通膨", "稅制", "財政", "finance", "financial", "budget", "economy", "banking", "investment", "fiscal")),
    ("legal", ("法律", "法規", "司法", "政策", "治理", "合規", "隱私", "監管", "憲法", "legal", "law", "policy", "regulation", "governance", "compliance", "privacy")),
    ("energy", ("能源", "電力", "太陽能", "風電", "核能", "電網", "製造", "工業", "energy", "power", "solar", "grid", "manufacturing")),
    ("education", ("教育", "大學", "高中職", "升學", "課堂", "教學", "學習", "素養", "校園", "education", "university", "school", "curriculum", "learning", "campus")),
    ("retail", ("零售", "消費", "行銷", "電商", "品牌", "通路", "餐飲", "市場", "retail", "consumer", "marketing", "ecommerce", "brand")),
    ("ai", ("人工智慧", "生成式", "機器學習", "深度學習", "大語言模型", "演算法", "ai", "llm", "genai", "machine learning", "neural", "algorithm")),
    ("data", ("巨量資料", "大數據", "資料分析", "數據", "統計", "資料庫", "儀表板", "data", "analytics", "statistics", "big data", "dataset")),
    ("tech", ("科技", "軟體", "系統", "雲端", "資安", "晶片", "半導體", "科學園區", "網路", "tech", "software", "cloud", "cyber", "semiconductor", "chip")),
    ("academic", ("學術", "研究", "論文", "科學", "實驗", "理論", "academic", "research", "paper", "science")),
)


def _resolve_slide_topic_seed(
    raw_str: str,
    resolved_mode: str,
    theme_id: str,
    theme_name: str,
) -> Tuple[str, str, str]:
    """
    Resolve a topic string (preset key, semantic key, HEX code, Chinese/English free-text topic,
    or arbitrary unknown topic) into `(seed_hex, resolved_theme_id, resolved_theme_name)`.
    - Explicit `#...` strings are validated strictly as HEX (invalid `#...` raises ValueError).
    - Bare 6-digit hex strings (e.g. `C87D55`) are normalized as HEX.
    - Free-text Chinese/English topics match curated semantic domains first, then fall back to a
      deterministic SHA-256 -> HCL mid-chroma seed so unknown topic strings never crash.
    """
    import hashlib
    import re

    key = raw_str.lower().replace("-", "_").replace(" ", "_")
    if key in THEMATIC_PALETTE_PRESETS:
        preset_title, hex_list = THEMATIC_PALETTE_PRESETS[key]
        seed_hex = _normalize_hex(hex_list[0])
        return (
            seed_hex,
            theme_id or f"topic_{key}_{resolved_mode}",
            theme_name or f"{preset_title} ({resolved_mode})",
        )
    if key in SLIDE_TOPIC_SEMANTIC_SEEDS:
        seed_title, seed_raw = SLIDE_TOPIC_SEMANTIC_SEEDS[key]
        seed_hex = _normalize_hex(seed_raw)
        return (
            seed_hex,
            theme_id or f"topic_{key}_{resolved_mode}",
            theme_name or f"{seed_title} ({resolved_mode})",
        )
    if raw_str.startswith("#") or re.fullmatch(r"[0-9A-Fa-f]{6}", raw_str):
        seed_hex = _normalize_hex(raw_str)
        return (
            seed_hex,
            theme_id or f"topic_{seed_hex.lstrip('#').lower()}_{resolved_mode}",
            theme_name or f"Custom Topic {seed_hex} ({resolved_mode})",
        )

    # Free-text Chinese / English semantic keyword routing
    lower_raw = raw_str.lower()
    for target_key, keywords in _SLIDE_TOPIC_KEYWORD_RULES:
        matched = False
        for kw in keywords:
            if kw.isascii():
                if re.search(rf"(?<![a-z0-9]){re.escape(kw)}(?![a-z0-9])", lower_raw):
                    matched = True
                    break
            else:
                if kw in raw_str:
                    matched = True
                    break
        if matched:
            if target_key in THEMATIC_PALETTE_PRESETS:
                preset_title, hex_list = THEMATIC_PALETTE_PRESETS[target_key]
                seed_hex = _normalize_hex(hex_list[0])
                title = preset_title
            else:
                title, seed_raw = SLIDE_TOPIC_SEMANTIC_SEEDS[target_key]
                seed_hex = _normalize_hex(seed_raw)
            return (
                seed_hex,
                theme_id or f"topic_{target_key}_{resolved_mode}",
                theme_name or f"{title} ({resolved_mode})",
            )

    # Deterministic safe fallback for arbitrary unknown topic descriptions:
    # Hash raw_str -> tasteful hue in HCL space (C=48, L=44), avoiding muddy yellow-olive [70..115]
    digest = hashlib.sha256(raw_str.encode("utf-8")).digest()
    raw_angle = (int.from_bytes(digest[:4], "big") % 3150) / 10.0  # [0.0, 315.0)
    hue_deg = raw_angle if raw_angle < 70.0 else (raw_angle + 45.0) % 360.0
    seed_hex = hcl_to_hex(hue_deg, 48.0, 44.0)
    short_hash = digest.hex()[:8]
    return (
        seed_hex,
        theme_id or f"topic_auto_{short_hash}_{resolved_mode}",
        theme_name or f"Derived Topic {raw_str[:24]} ({resolved_mode})",
    )


def _ensure_wcag_contrast_in_lab(
    fg_hex: str,
    bg_hexes: Sequence[str],
    min_ratio: float = 4.6,
    prefer_darker: bool = True,
) -> str:
    """
    Adjust a color's CIELAB L* (preserving hue angle and graceful chroma roll-off)
    until its WCAG 2.1 contrast ratio against EVERY background in `bg_hexes` is >= `min_ratio`.
    """
    base = _normalize_hex(fg_hex)
    bgs = [_normalize_hex(b) for b in bg_hexes if b]
    if not bgs:
        return base

    def _min_cr(cand: str) -> float:
        return min(wcag_contrast(cand, bg) for bg in bgs)

    if _min_cr(base) >= min_ratio:
        return base

    l0, a0, b0 = hex_to_lab(base)
    target_l = 0.0 if prefer_darker else 100.0

    def _cand_at(t: float, chroma_decay: float = 0.35) -> str:
        lt = l0 + (target_l - l0) * t
        c_scale = max(0.0, 1.0 - chroma_decay * t)
        return lab_to_hex(lt, a0 * c_scale, b0 * c_scale)

    if _min_cr(_cand_at(1.0, chroma_decay=0.35)) >= min_ratio:
        lo, hi = 0.0, 1.0
        for _ in range(28):
            mid = (lo + hi) / 2.0
            if _min_cr(_cand_at(mid, chroma_decay=0.35)) >= min_ratio:
                hi = mid
            else:
                lo = mid
        return _cand_at(hi, chroma_decay=0.35)

    # Secondary fallback: decay chroma fully toward neutral dark/light anchor
    anchor = "#0F172A" if prefer_darker else "#F8FAFC"
    if _min_cr(anchor) >= min_ratio:
        lo, hi = 0.0, 1.0
        for _ in range(28):
            mid = (lo + hi) / 2.0
            cand = lab_interpolate([base, anchor], mid)
            if _min_cr(cand) >= min_ratio:
                hi = mid
            else:
                lo = mid
        return lab_interpolate([base, anchor], hi)

    return "#000000" if prefer_darker else "#FFFFFF"


def derive_slide_theme_from_topic(
    topic_or_hex: object,
    mode: str = "light_classroom",
    **kwargs,
) -> Dict[str, str]:
    """
    Format C Mode 3 Dynamic CIELAB Slide Theme Bridge:
    - Accepts a thematic preset key (`"milk_tea"`, `"forest_eco"`, `"ocean_blue"`, `"coffee_roast"`,
      `"pineapple_tropical"` and their aliases), a semantic domain key (`"healthcare"`, `"finance"`,
      `"tech"`, `"ai"`, `"climate"`, `"legal"`, etc.), a single representative HEX string (e.g. `"#C87D55"`),
      or a non-empty sequence of HEX strings.
    - Derives a complete `document_theme` dictionary 100% compatible with `pptx_slide_engine.py`
      in CIELAB perceptual space for either:
        * `mode="light_classroom"` (default, bright-room safe light canvas + high-contrast dark ink)
        * `mode="dark_stage"` (controlled dark keynote stage + luminous accents)
    - Enforces WCAG 2.1 AA (`wcag_contrast >= 4.5:1`) across every foreground/background & accent/surface pair.
    """
    raw_mode = str(mode or "light_classroom").strip().lower().replace("-", "_").replace(" ", "_")
    mode_aliases = {
        "light_classroom": "light_classroom",
        "light": "light_classroom",
        "classroom": "light_classroom",
        "day": "light_classroom",
        "dark_stage": "dark_stage",
        "dark": "dark_stage",
        "stage": "dark_stage",
        "keynote": "dark_stage",
    }
    resolved_mode = mode_aliases.get(raw_mode)
    if resolved_mode is None:
        raise ValueError(
            f"Unsupported slide theme mode '{mode}'. Use 'light_classroom' or 'dark_stage'."
        )

    raw_min_cr_arg = kwargs.get("min_contrast", 4.65)
    raw_min_cr = 4.65 if raw_min_cr_arg is None else float(raw_min_cr_arg)
    if not math.isfinite(raw_min_cr):
        raise ValueError(f"min_contrast must be a finite number; got {raw_min_cr_arg!r}.")
    min_contrast = max(4.5, raw_min_cr)
    theme_id = str(kwargs.get("theme_id", "")).strip()
    theme_name = str(kwargs.get("theme_name", "")).strip()

    if isinstance(topic_or_hex, str):
        raw_str = topic_or_hex.strip()
        if not raw_str:
            raise ValueError("topic_or_hex cannot be empty.")
        seed_hex, theme_id, theme_name = _resolve_slide_topic_seed(
            raw_str, resolved_mode, theme_id, theme_name
        )
    elif isinstance(topic_or_hex, (list, tuple)):
        cleaned = [str(h).strip() for h in topic_or_hex if str(h).strip()]
        if not cleaned:
            raise ValueError("derive_slide_theme_from_topic received an empty sequence.")
        seed_hex = _normalize_hex(cleaned[0])
        theme_id = theme_id or f"topic_{seed_hex.lstrip('#').lower()}_{resolved_mode}"
        theme_name = theme_name or f"Custom Topic {seed_hex} ({resolved_mode})"
    else:
        raise TypeError("topic_or_hex must be a topic/preset str, a HEX str, or a sequence of HEX strings.")

    l_seed, a_seed, b_seed = hex_to_lab(seed_hex)
    chroma_seed = math.hypot(a_seed, b_seed)
    hue_rad = math.atan2(b_seed, a_seed) if chroma_seed > 1e-3 else math.radians(245.0)
    cos_h, sin_h = math.cos(hue_rad), math.sin(hue_rad)
    has_chroma = chroma_seed > 2.0

    # Semantic HCL base hues (warn=amber, success=teal, danger=rose, synth=violet)
    sem_hues = {
        "warn": 42.0,
        "success": 165.0,
        "danger": 348.0,
        "synth": 282.0,
    }

    if resolved_mode == "light_classroom":
        bg_canvas = lab_to_hex(98.4, (1.4 * cos_h) if has_chroma else 0.0, (1.4 * sin_h) if has_chroma else 0.0)
        bg_card = "#FFFFFF"
        border_card = lab_to_hex(83.5, (3.2 * cos_h) if has_chroma else 0.0, (3.2 * sin_h) if has_chroma else 0.0)

        primary_tint = lab_to_hex(
            95.0,
            (min(8.5, chroma_seed * 0.22) * cos_h) if has_chroma else 0.0,
            (min(8.5, chroma_seed * 0.22) * sin_h) if has_chroma else 0.0,
        )
        sem_tints: Dict[str, str] = {
            role: hcl_to_hex(h_deg, 10.0, 95.2) for role, h_deg in sem_hues.items()
        }
        all_light_surfaces = [bg_canvas, bg_card, primary_tint, *sem_tints.values()]

        ink_primary = _ensure_wcag_contrast_in_lab(
            lab_to_hex(12.0, (4.0 * cos_h) if has_chroma else 0.0, (4.0 * sin_h) if has_chroma else 0.0),
            all_light_surfaces,
            min_ratio=max(min_contrast, 12.0),
            prefer_darker=True,
        )
        ink_secondary = _ensure_wcag_contrast_in_lab(
            lab_to_hex(24.0, (4.0 * cos_h) if has_chroma else 0.0, (4.0 * sin_h) if has_chroma else 0.0),
            all_light_surfaces,
            min_ratio=max(min_contrast, 8.0),
            prefer_darker=True,
        )
        ink_muted = _ensure_wcag_contrast_in_lab(
            lab_to_hex(44.0, (4.5 * cos_h) if has_chroma else 0.0, (4.5 * sin_h) if has_chroma else 0.0),
            all_light_surfaces,
            min_ratio=min_contrast,
            prefer_darker=True,
        )

        # Keep primary_accent vivid yet strictly >= min_contrast on bg_canvas, #FFFFFF, and primary_tint
        # (by WCAG symmetry, #FFFFFF text on primary_accent pill is also >= min_contrast)
        init_pri_l = min(46.0, max(26.0, l_seed))
        init_pri_c = min(chroma_seed, 58.0) if has_chroma else 0.0
        primary_accent = _ensure_wcag_contrast_in_lab(
            lab_to_hex(init_pri_l, init_pri_c * cos_h, init_pri_c * sin_h),
            [bg_canvas, bg_card, primary_tint, "#FFFFFF"],
            min_ratio=min_contrast,
            prefer_darker=True,
        )

        sem_accents: Dict[str, str] = {}
        for role, h_deg in sem_hues.items():
            tint_c = sem_tints[role]
            raw_acc = hcl_to_hex(h_deg, 54.0, 42.0)
            sem_accents[role] = _ensure_wcag_contrast_in_lab(
                raw_acc,
                [bg_canvas, bg_card, tint_c, "#FFFFFF"],
                min_ratio=min_contrast,
                prefer_darker=True,
            )

        bookend_dark_bg = _ensure_wcag_contrast_in_lab(
            lab_to_hex(12.5, (10.0 * cos_h) if has_chroma else 0.0, (10.0 * sin_h) if has_chroma else 0.0),
            ["#F8FAFC", "#FFFFFF"],
            min_ratio=11.0,
            prefer_darker=True,
        )
        bookend_accent = _ensure_wcag_contrast_in_lab(
            lab_to_hex(76.0, (min(46.0, max(24.0, chroma_seed * 0.85)) * cos_h) if has_chroma else 0.0,
                       (min(46.0, max(24.0, chroma_seed * 0.85)) * sin_h) if has_chroma else 0.0),
            [bookend_dark_bg],
            min_ratio=max(min_contrast, 5.5),
            prefer_darker=False,
        )
        pill_fg = "#FFFFFF"
    else:
        # Controlled dark_stage mode
        bg_canvas = _ensure_wcag_contrast_in_lab(
            lab_to_hex(11.0, (7.5 * cos_h) if has_chroma else 0.0, (7.5 * sin_h) if has_chroma else 0.0),
            ["#F8FAFC"],
            min_ratio=12.0,
            prefer_darker=True,
        )
        bg_card = _ensure_wcag_contrast_in_lab(
            lab_to_hex(17.5, (7.0 * cos_h) if has_chroma else 0.0, (7.0 * sin_h) if has_chroma else 0.0),
            ["#F8FAFC"],
            min_ratio=10.0,
            prefer_darker=True,
        )
        border_card = lab_to_hex(34.0, (7.0 * cos_h) if has_chroma else 0.0, (7.0 * sin_h) if has_chroma else 0.0)

        primary_tint = lab_to_hex(
            23.0,
            (min(18.0, max(8.0, chroma_seed * 0.35)) * cos_h) if has_chroma else 0.0,
            (min(18.0, max(8.0, chroma_seed * 0.35)) * sin_h) if has_chroma else 0.0,
        )
        sem_tints = {
            role: hcl_to_hex(h_deg, 16.0, 23.0) for role, h_deg in sem_hues.items()
        }
        all_dark_surfaces = [bg_canvas, bg_card, primary_tint, *sem_tints.values()]

        ink_primary = _ensure_wcag_contrast_in_lab(
            "#F8FAFC",
            all_dark_surfaces,
            min_ratio=max(min_contrast, 10.0),
            prefer_darker=False,
        )
        ink_secondary = _ensure_wcag_contrast_in_lab(
            lab_to_hex(88.0, (2.5 * cos_h) if has_chroma else 0.0, (2.5 * sin_h) if has_chroma else 0.0),
            all_dark_surfaces,
            min_ratio=max(min_contrast, 7.0),
            prefer_darker=False,
        )
        ink_muted = _ensure_wcag_contrast_in_lab(
            lab_to_hex(73.0, (3.5 * cos_h) if has_chroma else 0.0, (3.5 * sin_h) if has_chroma else 0.0),
            all_dark_surfaces,
            min_ratio=min_contrast,
            prefer_darker=False,
        )

        init_pri_c = min(48.0, max(24.0, chroma_seed * 0.85)) if has_chroma else 0.0
        primary_accent = _ensure_wcag_contrast_in_lab(
            lab_to_hex(76.0, init_pri_c * cos_h, init_pri_c * sin_h),
            [bg_canvas, bg_card, primary_tint],
            min_ratio=min_contrast,
            prefer_darker=False,
        )

        sem_accents = {}
        for role, h_deg in sem_hues.items():
            tint_c = sem_tints[role]
            raw_acc = hcl_to_hex(h_deg, 46.0, 76.0)
            sem_accents[role] = _ensure_wcag_contrast_in_lab(
                raw_acc,
                [bg_canvas, bg_card, tint_c],
                min_ratio=min_contrast,
                prefer_darker=False,
            )

        bookend_dark_bg = _ensure_wcag_contrast_in_lab(
            lab_to_hex(8.5, (8.0 * cos_h) if has_chroma else 0.0, (8.0 * sin_h) if has_chroma else 0.0),
            ["#F8FAFC"],
            min_ratio=13.0,
            prefer_darker=True,
        )
        bookend_accent = _ensure_wcag_contrast_in_lab(
            primary_accent,
            [bookend_dark_bg],
            min_ratio=max(min_contrast, 5.5),
            prefer_darker=False,
        )
        pill_fg = ink(primary_accent, dark_ink="#0F172A", light_ink="#FFFFFF")
        if wcag_contrast(pill_fg, primary_accent) < min_contrast:
            pill_fg = "#000000" if wcag_contrast("#000000", primary_accent) >= wcag_contrast("#FFFFFF", primary_accent) else "#FFFFFF"

    return {
        "theme_id": theme_id,
        "theme_name": theme_name,
        "mode": resolved_mode,
        "source_hex": seed_hex,
        "bg_canvas": bg_canvas,
        "bg_card": bg_card,
        "border_card": border_card,
        "ink_primary": ink_primary,
        "ink_secondary": ink_secondary,
        "ink_muted": ink_muted,
        "primary_accent": primary_accent,
        "primary_tint": primary_tint,
        "warn_accent": sem_accents["warn"],
        "warn_tint": sem_tints["warn"],
        "success_accent": sem_accents["success"],
        "success_tint": sem_tints["success"],
        "danger_accent": sem_accents["danger"],
        "danger_tint": sem_tints["danger"],
        "synth_accent": sem_accents["synth"],
        "synth_tint": sem_tints["synth"],
        "bookend_dark_bg": bookend_dark_bg,
        "bookend_accent": bookend_accent,
        "pill_fg": pill_fg,
    }
