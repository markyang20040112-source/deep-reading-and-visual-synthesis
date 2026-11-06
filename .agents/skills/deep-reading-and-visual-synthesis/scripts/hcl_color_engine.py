"""
hcl_color_engine.py
HCL Color Science Engine for Deep Reading & Visual Synthesis.
Grounded in Zeileis et al. (2009, 2020), Brewer (1994), Stone et al. (2014), and WCAG 2.1.

Implements:
1. CIELUV Polar HCL (polarLUV, D65 white point) with binary-search sRGB gamut clamping.
2. common_c(hues, target_c, l) for perceptually equal qualitative scales.
3. ink(hex) & wcag_contrast(fg, bg) using WCAG 2.1 relative luminance (Y > 0.179 threshold).
4. lab_interpolate(hex_list, t) for sequential and diverging scales in CIELAB space.
5. AreaScaledHCL: Size-dependent Tri-tier scaling (Accent L=38, Badge L=46, Surface Tint L=96.5).
6. SessionColorContract: Cross-format semantic color lock (primary, warn, success, danger, synth).
7. Gephi · pastel Locked Chart & Data Dashboard Palette (Format D <-> Format E SSOT):
   Fixed 4-color qualitative binding, four 5-node CIELAB sequential scales, and 9-node symmetric diverging scale.
"""

import math
from typing import List, Tuple, Dict, Optional

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
# Locked Chart & Data Dashboard Color Specification (Format D <-> Format E SSOT)
# Source: https://docs.google.com/document/d/1puNpLGR7hYcyvZL1DZMdUpmP9fXM-TQcxu1N6QyGb1E/edit?usp=sharing
# Derived from ggsci Gephi · pastel (CIELAB / HCL L*≈72 balanced)
# -------------------------------------------------------------------------

LOCKED_CHART_PALETTE_URL = (
    "https://docs.google.com/document/d/1puNpLGR7hYcyvZL1DZMdUpmP9fXM-TQcxu1N6QyGb1E/edit?usp=sharing"
)

# 2. Fixed Qualitative Palette (4 base categories in strict binding order)
GEPHI_QUALITATIVE_HEX: List[str] = [
    "#ECA072",  # 1. 主色：暖杏蜜橘 (Warm Apricot Orange)
    "#5DBACD",  # 2. 次色：霧靄青藍 (Misty Cyan-Blue)
    "#E89BB6",  # 3. 第三色：落櫻粉黛 (Sakura Rose Pink)
    "#8FBA88",  # 4. 第四色：鼠尾草綠 (Sage Green)
]

GEPHI_QUALITATIVE_NAMED: Dict[str, str] = {
    "primary_orange": "#ECA072",
    "secondary_blue": "#5DBACD",
    "tertiary_pink": "#E89BB6",
    "quaternary_green": "#8FBA88",
}

# 3. Four 5-Node Sequential Scales (0.00, 0.25, 0.50, 0.75, 1.00; low=light -> high=dark)
GEPHI_SEQUENTIAL_SCALES: Dict[str, List[str]] = {
    "orange": ["#FFF3EA", "#FBD8C0", "#ECA072", "#CA6F35", "#97481B"],  # (1) 主色循序（暖杏橘系，預設數值尺度）
    "blue":   ["#EBF7F9", "#BCE2EB", "#5DBACD", "#2C8B9F", "#0E5B6B"],  # (2) 次色循序（霧靄藍系，對比雙指標／深鑽尺度）
    "pink":   ["#FFF0F5", "#F9CEE0", "#E89BB6", "#C46487", "#8D3658"],  # (3) 第三色循序（落櫻粉系）
    "green":  ["#F1F7EE", "#D0E5CC", "#8FBA88", "#5E8F56", "#396032"],  # (4) 第四色循序（鼠尾草綠系）
}

# 5. 9-Node Symmetric Diverging Scale (0.000 to 1.000, center=0.500 -> #F5F6F7)
GEPHI_DIVERGING_SCALE: List[str] = [
    "#0E5B6B",  # 0.000 (-100% 偏差極端：負向極值深墨青)
    "#257F92",  # 0.125 (-75% 偏差：負向中深)
    "#5DBACD",  # 0.250 (-50% 偏差：負向中度)
    "#B2DFE9",  # 0.375 (-25% 偏差：負向輕度)
    "#F5F6F7",  # 0.500 (0% 偏差：中立基準中心)
    "#FBD9C2",  # 0.625 (+25% 偏差：正向輕度)
    "#ECA072",  # 0.750 (+50% 偏差：正向中度)
    "#B4693A",  # 0.875 (+75% 偏差：正向中深)
    "#884725",  # 1.000 (+100% 偏差極端：正向極值深栗橘)
]

# 6. Neutral & Special Semantic Colors
GEPHI_DISCRETE_NEUTRALS: Dict[str, str] = {
    "diverging_center": "#F5F6F7",  # 發散中心（極低彩度中性冷灰）
    "na_missing": "#D9D9D9",        # 缺失值（NA / Null）預設標記色
    "other_aggregated": "#CBD5E1",  # 4+1 長尾聚合「其他項目」典雅淺灰
}


def _parse_numeric_or_na(value: object) -> Optional[float]:
    """Return float(value) if valid finite number, or None if missing/NA/NaN."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str):
        s = value.strip()
        if not s or s.lower() in {"na", "n/a", "null", "none", "nan", "-", "—"}:
            return None
        try:
            v = float(s)
        except ValueError:
            return None
    else:
        try:
            v = float(value)  # Handles int, float, np.floating, Decimal, etc.
        except (TypeError, ValueError):
            return None
    if math.isnan(v):
        return None
    return v


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
) -> str:
    """
    Map a continuous or ordinal value to one of the 4 locked 5-node sequential scales.
    - Uses CIELAB piecewise linear interpolation (no alpha channel manipulation).
    - Returns #D9D9D9 for None, NaN, np.nan, or 'NA'/'null' strings.
    """
    v = _parse_numeric_or_na(value)
    if v is None:
        return GEPHI_DISCRETE_NEUTRALS["na_missing"]
    scale_key = _SEQUENTIAL_SCALE_ALIASES.get(str(scale).strip().lower())
    if scale_key is None:
        raise ValueError(
            f"Unknown sequential scale '{scale}'. Locked palette only permits: "
            f"{list(GEPHI_SEQUENTIAL_SCALES.keys())}"
        )
    nodes = GEPHI_SEQUENTIAL_SCALES[scale_key]
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


def bind_qualitative_colors(
    categories: List[object],
    allow_top4_aggregation: bool = False,
    other_label: str = "其他項目合計",
) -> Dict[str, str]:
    """
    Bind unordered categories to fixed qualitative colors in strict order (#ECA072, #5DBACD, #E89BB6, #8FBA88).
    - Deduplicates categories in order of first appearance so repeated occurrences in data rows
      never overwrite an already-bound category or inflate the unique category count.
    - Maps missing/NA category markers ('NA', 'Null', None, '') to #D9D9D9 without consuming a slot.
    - If unique valid categories > 4 and allow_top4_aggregation is False, raises ValueError to enforce
      confirming expansion strategy with the user first.
    - If allow_top4_aggregation is True, binds the first 4 unique categories to the 4 primary colors and
      maps remaining categories (plus `other_label`) to #CBD5E1.
    """
    bound: Dict[str, str] = {}
    unique_valid: List[str] = []
    na_tokens = {"na", "n/a", "null", "none", "nan", ""}

    for raw_cat in categories:
        if raw_cat is None:
            bound["NA"] = GEPHI_DISCRETE_NEUTRALS["na_missing"]
            continue
        cat = str(raw_cat).strip()
        if cat.lower() in na_tokens:
            bound[cat or "NA"] = GEPHI_DISCRETE_NEUTRALS["na_missing"]
            continue
        if cat == other_label:
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


