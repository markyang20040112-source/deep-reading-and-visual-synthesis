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
13. Public Fallback Chart & Data Dashboard Palette (Format D <-> Format E SSOT; overridden by active config/user_preferences.json):
   Fixed 4-color qualitative binding, four 5-node CIELAB sequential scales, and 9-node symmetric diverging scale.
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

DEFAULT_SUBTOTAL_KEYWORDS = (
    "總計", "合計", "小計", "總合", "總額", "全區", "全國", "全縣", "全市", "計",
    "total", "subtotal", "grand total",
)


def _parse_numeric_or_na(value: object) -> Optional[float]:
    """Return float(value) if valid finite number (stripping thousands commas), or None if missing/NA/NaN."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str):
        s = value.strip()
        if not s or s.lower() in KNOWN_NA_STRINGS:
            return None
        s_clean = s.replace(",", "")
        try:
            v = float(s_clean)
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
    scale_key: Optional[str] = None,
) -> str:
    """
    Map a continuous or ordinal value to one of the 4 locked 5-node sequential scales.
    - Uses CIELAB piecewise linear interpolation (no alpha channel manipulation).
    - Returns #D9D9D9 for None, NaN, np.nan, or 'NA'/'null' strings.
    """
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
    Bind unordered categories to fixed qualitative colors in strict order (`GEPHI_QUALITATIVE_HEX`).
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


def despine_axes(
    ax: object,
    grid_axis: Optional[str] = "y",
    grid_color: str = "#CBD5E1",
    grid_linestyle: str = "--",
    grid_alpha: float = 0.65,
    spine_color: str = "#CBD5E1",
) -> None:
    """
    Apply publication-grade despined axis formatting to a Matplotlib Axes object:
    - Hides top and right spines.
    - Colors bottom and left spines with `spine_color`.
    - Enables subtle dashed reference grid on `grid_axis` ('x', 'y', 'both', or None).
    """
    if hasattr(ax, "spines"):
        if "top" in ax.spines:
            ax.spines["top"].set_visible(False)
        if "right" in ax.spines:
            ax.spines["right"].set_visible(False)
        for side in ("bottom", "left"):
            if side in ax.spines:
                ax.spines[side].set_color(spine_color)
                ax.spines[side].set_linewidth(1.0)
    if grid_axis in ("x", "y", "both") and hasattr(ax, "grid"):
        ax.grid(False)
        ax.grid(axis=grid_axis, linestyle=grid_linestyle, color=grid_color, alpha=grid_alpha, zorder=0)


def _normalize_hex(hex_code: str) -> str:
    """Validate and normalize #RGB / RGB / #RRGGBB / RRGGBB to canonical uppercase #RRGGBB."""
    import re
    clean = str(hex_code or "").strip().lstrip("#")
    if len(clean) == 3:
        clean = "".join(ch * 2 for ch in clean)
    if len(clean) != 6 or not re.fullmatch(r"[0-9A-Fa-f]{6}", clean):
        raise ValueError(f"Invalid hex color: {hex_code!r}")
    return f"#{clean.upper()}"


def export_gephi_palette_js(output_path: str, palette_dict: Optional[Dict[str, object]] = None) -> str:
    """
    Export the standalone pure-JS CIELAB color engine (`gephi_palette.js`)
    to `output_path` so Format E web dashboards share 100% identical color math with Python.
    If `palette_dict` is provided, embeds that palette's colors into the generated JS file.
    """
    import json
    import re
    from pathlib import Path
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
        f"    divergingHex: {json.dumps(div9)}\n"
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


# -------------------------------------------------------------------------
# User Identity Verification, Owner Isolation & Multi-Palette Derivation
# -------------------------------------------------------------------------

OWNER_GITHUB_ID = "markyang20040112-source"
OWNER_PRIVATE_REPO_URL = "https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis-Private-.git"


def ensure_owner_private_assets(
    pull_remote: bool = False,
    push_remote: bool = False,
    commit_msg: str = "chore(sync): sync owner sessions and private config",
) -> Dict[str, object]:
    """
    Sync owner private vault (`reading_sessions/` + `_owner_private_config/`) with the
    private GitHub repository and mirror `user_preferences.json` / `owner_styles/*.md`
    to `.agents/skills/deep-reading-and-visual-synthesis/config/` (ignored by the Public repo).
    """
    import shutil
    import subprocess
    from pathlib import Path

    skill_root = Path(__file__).resolve().parents[1]
    workspace_root = skill_root.parents[2] if len(skill_root.parents) >= 3 else skill_root.parent
    sessions_dir = workspace_root / "reading_sessions"
    private_cfg_dir = sessions_dir / "_owner_private_config"
    cfg_dir = skill_root / "config"

    actions: List[str] = []
    errors: List[str] = []

    def _run_git(args: List[str], cwd: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )

    need_remote_bootstrap = not (cfg_dir / "user_preferences.json").exists() and not (
        private_cfg_dir / "user_preferences.json"
    ).exists()

    if pull_remote or need_remote_bootstrap:
        if not (sessions_dir / ".git").exists():
            if not sessions_dir.exists() or not any(sessions_dir.iterdir()):
                sessions_dir.parent.mkdir(parents=True, exist_ok=True)
                if sessions_dir.exists():
                    sessions_dir.rmdir()
                res = _run_git(["clone", OWNER_PRIVATE_REPO_URL, str(sessions_dir)], workspace_root)
                if res.returncode == 0:
                    actions.append("cloned_private_repo")
                else:
                    errors.append(f"clone failed: {(res.stderr or res.stdout).strip()}")
            else:
                _run_git(["init"], sessions_dir)
                _run_git(["branch", "-M", "main"], sessions_dir)
                _run_git(["remote", "add", "origin", OWNER_PRIVATE_REPO_URL], sessions_dir)
                res_fetch = _run_git(["fetch", "origin", "main"], sessions_dir)
                if res_fetch.returncode == 0:
                    _run_git(["reset", "--mixed", "origin/main"], sessions_dir)
                    _run_git(["checkout", "--", "."], sessions_dir)
                    actions.append("initialized_and_pulled_private_repo")
                else:
                    errors.append(f"fetch failed: {(res_fetch.stderr or res_fetch.stdout).strip()}")
        else:
            res_pull = _run_git(["pull", "--rebase", "origin", "main"], sessions_dir)
            if res_pull.returncode == 0:
                actions.append("pulled_private_repo")
            else:
                errors.append(f"pull failed: {(res_pull.stderr or res_pull.stdout).strip()}")

    # Bidirectional sync between reading_sessions/_owner_private_config and skill config/
    cfg_dir.mkdir(parents=True, exist_ok=True)
    priv_prefs = private_cfg_dir / "user_preferences.json"
    cfg_prefs = cfg_dir / "user_preferences.json"

    if priv_prefs.exists() and (not cfg_prefs.exists() or pull_remote):
        shutil.copy2(priv_prefs, cfg_prefs)
        actions.append("restored_user_preferences")
    elif cfg_prefs.exists():
        private_cfg_dir.mkdir(parents=True, exist_ok=True)
        if not priv_prefs.exists() or cfg_prefs.read_bytes() != priv_prefs.read_bytes():
            shutil.copy2(cfg_prefs, priv_prefs)
            actions.append("backed_up_user_preferences_to_vault")

    priv_styles = private_cfg_dir / "owner_styles"
    cfg_styles = cfg_dir / "owner_styles"
    cfg_styles.mkdir(parents=True, exist_ok=True)
    if priv_styles.exists():
        for src_md in priv_styles.glob("*.md"):
            dst_md = cfg_styles / src_md.name
            if not dst_md.exists() or pull_remote:
                shutil.copy2(src_md, dst_md)
                actions.append(f"restored_style:{src_md.name}")
    if cfg_styles.exists():
        priv_styles.mkdir(parents=True, exist_ok=True)
        for src_md in cfg_styles.glob("*.md"):
            dst_md = priv_styles / src_md.name
            if not dst_md.exists() or src_md.read_bytes() != dst_md.read_bytes():
                shutil.copy2(src_md, dst_md)
                actions.append(f"backed_up_style:{src_md.name}")

    if push_remote and (sessions_dir / ".git").exists():
        _run_git(["add", "-A"], sessions_dir)
        st = _run_git(["status", "--porcelain"], sessions_dir)
        if (st.stdout or "").strip():
            c_res = _run_git(["commit", "-m", commit_msg], sessions_dir)
            if c_res.returncode == 0:
                actions.append("committed_private_vault")
            else:
                errors.append(f"commit failed: {(c_res.stderr or c_res.stdout).strip()}")
        p_res = _run_git(["push", "-u", "origin", "main"], sessions_dir)
        if p_res.returncode == 0:
            actions.append("pushed_private_repo")
        else:
            errors.append(f"push failed: {(p_res.stderr or p_res.stdout).strip()}")

    return {
        "ok": len(errors) == 0,
        "sessions_dir": str(sessions_dir),
        "private_cfg_dir": str(private_cfg_dir),
        "actions": actions,
        "errors": errors,
    }


def _detect_local_git_user(repo_dir: Optional[str] = None) -> str:
    """Detect current Git user identity via env override, git config user.name, or user.email."""
    import os
    import subprocess
    from pathlib import Path

    env_user = os.environ.get("DEEP_READING_GIT_USER")
    if env_user is not None:
        return env_user.strip()

    cwd = str(Path(repo_dir).resolve()) if repo_dir else str(Path(__file__).resolve().parents[1])
    for cmd in (["git", "config", "user.name"], ["git", "config", "user.email"]):
        try:
            res = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=3,
                check=False,
            )
            val = (res.stdout or "").strip()
            if val:
                if "@" in val:
                    val = val.split("@", 1)[0].strip()
                return val
        except Exception:
            continue
    return ""


def _detect_local_os_user() -> str:
    """Detect current OS login username for Git-less external user persistence."""
    import getpass
    import os
    env_override = os.environ.get("DEEP_READING_LOCAL_USER")
    if env_override is not None:
        return env_override.strip()
    try:
        return (getpass.getuser() or "").strip()
    except Exception:
        return (os.environ.get("USERNAME") or os.environ.get("USER") or "").strip()


def _is_gh_owner_authenticated() -> bool:
    """Return True if GitHub CLI (`gh`) is logged in as OWNER_GITHUB_ID."""
    import shutil
    import subprocess
    if not shutil.which("gh"):
        return False
    try:
        res = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=4,
            check=False,
        )
        return res.returncode == 0 and res.stdout.strip().lower() == OWNER_GITHUB_ID.lower()
    except Exception:
        return False


def check_user_identity_and_load_prefs(
    prefs_path: Optional[str] = None,
    override_git_user: Optional[str] = None,
    allow_workspace_fallback: bool = True,
    override_local_user: Optional[str] = None,
) -> Dict[str, object]:
    """
    Verify local Git / OS user identity and load `config/user_preferences.json`.
    - Owner Dual-Device Seamless Sync: Verified via local Git identity (`markyang20040112-source`),
      authenticated `gh` CLI login, or private home-directory marker `~/.deep_reading_owner_verified`
      (never by public repo files like `reading_sessions/` alone, preventing clone false-positives).
    - Strict External User Isolation: Strips and isolates all `owner_only: true` palettes and
      `available_owner_styles` for non-owners. Supports both Git-bound (`bound_git_user`) and
      Git-less local OS-bound (`bound_local_user`) persistence once onboarding is completed.
    """
    import copy
    import json
    from pathlib import Path

    skill_root = Path(__file__).resolve().parents[1]
    workspace_root = skill_root.parents[2] if len(skill_root.parents) >= 3 else skill_root.parent
    cfg_dir = skill_root / "config"
    target_prefs = Path(prefs_path).resolve() if prefs_path else (cfg_dir / "user_preferences.json")
    template_prefs = cfg_dir / "user_preferences.template.json"

    if target_prefs.exists():
        raw_prefs = json.loads(target_prefs.read_text(encoding="utf-8"))
    elif template_prefs.exists():
        raw_prefs = json.loads(template_prefs.read_text(encoding="utf-8"))
    else:
        raw_prefs = {}

    detected_user = (
        override_git_user.strip()
        if override_git_user is not None
        else _detect_local_git_user(str(workspace_root))
    )
    detected_local_user = (
        override_local_user.strip()
        if override_local_user is not None
        else _detect_local_os_user()
    )

    bound_user = str(raw_prefs.get("bound_git_user") or "").strip()
    bound_local_user = str(raw_prefs.get("bound_local_user") or "").strip()
    is_owner = False

    if detected_user.lower() == OWNER_GITHUB_ID.lower():
        is_owner = True
    elif not detected_user and allow_workspace_fallback and override_git_user is None:
        owner_marker = Path.home() / ".deep_reading_owner_verified"
        if owner_marker.exists() or _is_gh_owner_authenticated():
            is_owner = True

    if is_owner:
        if prefs_path is None and (not target_prefs.exists() or not (cfg_dir / "owner_styles").exists()):
            ensure_owner_private_assets(pull_remote=True)
            if target_prefs.exists():
                raw_prefs = json.loads(target_prefs.read_text(encoding="utf-8"))
        effective = copy.deepcopy(raw_prefs)
        effective["is_owner"] = True
        effective["isolated_external_user"] = False
        effective["detected_git_user"] = detected_user or OWNER_GITHUB_ID
        effective["detected_local_user"] = detected_local_user
        effective["onboarding_completed"] = True
        return effective

    # External user path: check if external user already completed onboarding (via Git OR local OS identity)
    git_matched = bool(
        detected_user
        and bound_user
        and detected_user.lower() == bound_user.lower()
        and bound_user.lower() != OWNER_GITHUB_ID.lower()
    )
    local_matched = bool(
        not detected_user
        and detected_local_user
        and bound_local_user
        and detected_local_user.lower() == bound_local_user.lower()
        and bound_user.lower() != OWNER_GITHUB_ID.lower()
    )

    if (git_matched or local_matched) and bool(raw_prefs.get("onboarding_completed", False)):
        effective = copy.deepcopy(raw_prefs)
        # Still ensure owner_only items remain isolated
        palettes = effective.get("color_sets", {}).get("chart_palettes", {})
        effective.setdefault("color_sets", {})["chart_palettes"] = {
            k: v for k, v in palettes.items() if not v.get("owner_only", False)
        }
        effective.setdefault("writing_styles", {})["available_owner_styles"] = []
        effective["is_owner"] = False
        effective["isolated_external_user"] = False
        effective["detected_git_user"] = detected_user
        effective["detected_local_user"] = detected_local_user
        return effective

    # External uninitialized user: strictly isolate all owner_only assets and force onboarding
    if template_prefs.exists():
        effective = json.loads(template_prefs.read_text(encoding="utf-8"))
    else:
        effective = copy.deepcopy(raw_prefs)

    palettes = effective.get("color_sets", {}).get("chart_palettes", {})
    effective.setdefault("color_sets", {})["chart_palettes"] = {
        k: v for k, v in palettes.items() if not v.get("owner_only", False)
    }
    effective["color_sets"]["active_chart_palette_id"] = None
    effective.setdefault("writing_styles", {})["available_owner_styles"] = []
    effective["writing_styles"]["active_style_id"] = None
    effective["bound_git_user"] = detected_user or None
    effective["bound_local_user"] = detected_local_user or None
    effective["is_owner"] = False
    effective["isolated_external_user"] = True
    effective["detected_git_user"] = detected_user
    effective["detected_local_user"] = detected_local_user
    effective["onboarding_completed"] = False
    return effective


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


# -------------------------------------------------------------------------
# Distribution & Density Chart Guardrail Helpers (Step 4 Spec Integration)
# -------------------------------------------------------------------------

def add_halo_vline(
    ax: object,
    x: float,
    color: Optional[str] = None,
    linestyle: str = "--",
    linewidth: float = 2.2,
    halo_color: str = "#FFFFFF",
    halo_width: float = 4.8,
    label: Optional[str] = None,
    zorder: int = 5,
):
    """
    Draw a vertical reference line (e.g. Mean / Median on a Histogram or KDE plot) with a mandatory
    white outer stroke/halo so it never visually merges with dark bars or bin boundaries.
    """
    import matplotlib.patheffects as patheffects

    resolved_color = color if color is not None else GEPHI_QUALITATIVE_HEX[0]
    line = ax.axvline(
        x=float(x),
        color=resolved_color,
        linestyle=linestyle,
        linewidth=linewidth,
        label=label,
        zorder=zorder,
    )
    line.set_path_effects([
        patheffects.Stroke(linewidth=halo_width, foreground=halo_color),
        patheffects.Normal(),
    ])
    return line


def annotate_floor_extreme(
    ax: object,
    x: float,
    y_floor: float = 0.0,
    label_text: str = "",
    dot_color: Optional[str] = None,
    dot_size: float = 46.0,
    arrow_height_ratio: float = 0.14,
    text_offset_x: float = 0.0,
    fontsize: float = 9.5,
    zorder: int = 6,
    label: Optional[str] = None,
    color: Optional[str] = None,
):
    """
    Safely annotate a right-tail extreme value whose histogram bar height is tiny (e.g. n=1, ~0.3% of Y-axis)
    and sits nearly flat on the horizontal axis:
    - Places a high-contrast anchor dot directly on the bottom axis at `(x, y_floor)` (with white halo).
    - Uses a short vertical arrow pointing straight down to the anchor dot instead of a long diagonal
      arrow pointing at empty air.
    """
    if label is not None and not label_text:
        label_text = label
    if color is not None:
        dot_color = color
    resolved_dot_color = dot_color if dot_color is not None else GEPHI_SEQUENTIAL_SCALES["orange"][4]
    y_min, y_max = ax.get_ylim()
    y_span = max(1e-6, y_max - y_min)
    text_y = float(y_floor) + y_span * float(arrow_height_ratio)

    ax.scatter(
        [float(x)],
        [float(y_floor)],
        s=dot_size,
        color=resolved_dot_color,
        edgecolors="#FFFFFF",
        linewidths=1.5,
        zorder=zorder + 1,
        clip_on=False,
    )
    ann = ax.annotate(
        str(label_text),
        xy=(float(x), float(y_floor)),
        xytext=(float(x) + float(text_offset_x), text_y),
        ha="center",
        va="bottom",
        fontsize=fontsize,
        fontweight="bold",
        color="#0F172A",
        bbox=dict(boxstyle="round,pad=0.3", facecolor=GEPHI_LIGHT_BADGE_TINTS[0], edgecolor=resolved_dot_color, linewidth=1.1),
        arrowprops=dict(arrowstyle="-|>", color=resolved_dot_color, lw=1.6, shrinkA=2, shrinkB=4),
        zorder=zorder + 2,
    )
    return ann


def compute_clipped_kde(
    data: Sequence[float],
    x_min: Optional[float] = 0.0,
    x_max: Optional[float] = None,
    bw_method: object = "scott",
    grid_size: int = 512,
) -> Tuple[object, object, float]:
    """
    Compute a 1D Gaussian Kernel Density Estimate with strict boundary clipping (e.g. `x >= 0` for non-negative
    variables like income/revenue) and area renormalization so `integral(density, x_min..x_max) == 1.0`.
    Returns `(x_grid, density_normalized, bandwidth_h)`.
    """
    import numpy as np

    arr = np.asarray([float(v) for v in data if _parse_numeric_or_na(v) is not None], dtype="float64")
    if arr.size == 0:
        raise ValueError("compute_clipped_kde received empty numeric data.")

    low_bound = float(x_min) if x_min is not None else float(arr.min())
    high_bound = float(x_max) if x_max is not None else float(arr.max())
    if high_bound <= low_bound:
        high_bound = low_bound + 1.0

    n = arr.size
    std_val = float(np.std(arr, ddof=1)) if n > 1 else 1.0
    iqr_val = float(np.percentile(arr, 75) - np.percentile(arr, 25)) if n > 1 else std_val
    sigma = min(std_val, iqr_val / 1.34) if (iqr_val > 0 and std_val > 0) else max(std_val, 1e-6)

    if isinstance(bw_method, (int, float)):
        h = float(bw_method)
    elif str(bw_method).lower() == "silverman":
        h = 0.9 * sigma * (n ** (-0.2))
    else:
        # Scott's rule default
        h = 1.06 * std_val * (n ** (-0.2))
    h = max(h, (high_bound - low_bound) * 1e-3)

    x_grid = np.linspace(low_bound, high_bound, int(max(64, grid_size)))
    diffs = (x_grid[:, None] - arr[None, :]) / h
    raw_density = np.mean(np.exp(-0.5 * (diffs ** 2)), axis=1) / (h * math.sqrt(2.0 * math.pi))

    trapz_fn = getattr(np, "trapezoid", None) or getattr(np, "trapz")
    area = float(trapz_fn(raw_density, x_grid))
    if area > 1e-12:
        density_norm = raw_density / area
    else:
        density_norm = raw_density

    return x_grid, density_norm, float(h)


def plot_clipped_kde(
    ax: object,
    data: Sequence[float],
    x_min: Optional[float] = 0.0,
    x_max: Optional[float] = None,
    bw_method: object = "scott",
    grid_size: int = 512,
    color: Optional[str] = None,
    fill_color: Optional[str] = None,
    fill_alpha: float = 0.28,
    linewidth: float = 2.2,
    label: Optional[str] = None,
    zorder: int = 3,
) -> Tuple[object, object, float]:
    """
    Plot a boundary-clipped, unit-area-renormalized (`Area = 1.0`) KDE curve on `ax`.
    Prevents Gaussian kernel spillover into impossible negative regions (`x < 0`).
    """
    resolved_color = color if color is not None else GEPHI_QUALITATIVE_HEX[0]
    x_grid, density_norm, h = compute_clipped_kde(
        data, x_min=x_min, x_max=x_max, bw_method=bw_method, grid_size=grid_size
    )
    ax.plot(x_grid, density_norm, color=resolved_color, linewidth=linewidth, label=label, zorder=zorder)
    if fill_color is not None or fill_alpha > 0:
        fc = fill_color if fill_color is not None else resolved_color
        ax.fill_between(x_grid, 0.0, density_norm, color=fc, alpha=fill_alpha, zorder=max(1, zorder - 1))
    return x_grid, density_norm, h


def setup_context_overlay_grid(
    n_panels: int,
    ncols: int = 4,
    figsize_per_panel: Tuple[float, float] = (4.2, 3.2),
    dpi: int = 300,
    xlim: Optional[Tuple[float, float]] = None,
    ylim: Optional[Tuple[float, float]] = None,
    baseline_data: Optional[Sequence[float]] = None,
    baseline_x_min: float = 0.0,
    baseline_bw: object = "scott",
    baseline_color: str = "#CBD5E1",
    baseline_fill_alpha: float = 0.35,
    baseline_label: str = "全體基準分布 (Context)",
):
    """
    Create a small-multiples facet grid enforcing the 8 Iron Laws of Context Overlay / Shadow Distribution:
    1. Plots the identical light-gray (`#CBD5E1`) full-population / baseline-year normalized density curve
       in the background of every active subplot (`zorder=1`).
    2. Locks identical X and Y axis limits across all panels (`sharex=True, sharey=True`), preventing deceptive
       per-panel auto-scaling.
    3. Returns `(fig, active_axes, baseline_info)` where `baseline_info` contains `{"x_grid", "density", "h"}`.
    """
    import matplotlib.pyplot as plt

    n_panels = max(1, int(n_panels))
    ncols = max(1, min(int(ncols), n_panels))
    nrows = int(math.ceil(n_panels / float(ncols)))

    fig_w = figsize_per_panel[0] * ncols
    fig_h = figsize_per_panel[1] * nrows
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(fig_w, fig_h),
        dpi=dpi,
        sharex=True,
        sharey=True,
        squeeze=False,
    )
    axes_flat = [ax for row in axes for ax in row]

    baseline_info = None
    if baseline_data is not None and len(baseline_data) > 0:
        x_max_bound = xlim[1] if xlim is not None else None
        x_min_bound = xlim[0] if xlim is not None else baseline_x_min
        bg_x, bg_y, bg_h = compute_clipped_kde(
            baseline_data, x_min=x_min_bound, x_max=x_max_bound, bw_method=baseline_bw
        )
        baseline_info = {"x_grid": bg_x, "density": bg_y, "h": bg_h}

    active_axes = []
    for idx, ax in enumerate(axes_flat):
        if idx >= n_panels:
            ax.set_visible(False)
            continue
        despine_axes(ax, grid_axis="y")
        if baseline_info is not None:
            ax.plot(
                baseline_info["x_grid"],
                baseline_info["density"],
                color="#94A3B8",
                linewidth=1.3,
                linestyle="-",
                label=baseline_label if idx == 0 else None,
                zorder=1,
            )
            ax.fill_between(
                baseline_info["x_grid"],
                0.0,
                baseline_info["density"],
                color=baseline_color,
                alpha=baseline_fill_alpha,
                zorder=1,
            )
        if xlim is not None:
            ax.set_xlim(xlim[0], xlim[1])
        if ylim is not None:
            ax.set_ylim(ylim[0], ylim[1])
        active_axes.append(ax)

    return fig, active_axes, baseline_info


class _LiteSeries:
    """Lightweight pandas.Series-compatible wrapper over a Python list + numpy for environments without pandas."""
    def __init__(self, data: List[object], name: str = ""):
        self._data = list(data)
        self.name = name

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, idx):
        if isinstance(idx, _LiteSeries):
            return _LiteSeries([v for v, m in zip(self._data, idx._data) if bool(m)], name=self.name)
        if isinstance(idx, (list, tuple)) and all(isinstance(x, bool) for x in idx):
            return _LiteSeries([v for v, m in zip(self._data, idx) if m], name=self.name)
        return self._data[idx]

    @property
    def values(self):
        import numpy as np
        return np.array(self._data, dtype=object)

    def tolist(self) -> List[object]:
        return list(self._data)

    def apply(self, func):
        return _LiteSeries([func(x) for x in self._data], name=self.name)

    def isna(self):
        def _check_na(x) -> bool:
            if x is None:
                return True
            if isinstance(x, float) and math.isnan(x):
                return True
            return False
        return _LiteSeries([_check_na(x) for x in self._data], name=self.name)

    def dropna(self):
        return _LiteSeries(
            [x for x in self._data if x is not None and not (isinstance(x, float) and math.isnan(x))],
            name=self.name,
        )

    def _numeric_array(self):
        import numpy as np
        clean = [float(x) for x in self.dropna()._data]
        return np.array(clean, dtype="float64")

    def sum(self) -> float:
        arr = self._numeric_array()
        if arr.size == 0:
            return float(sum(1 for x in self._data if x is True))
        return float(arr.sum())

    def min(self) -> Optional[float]:
        arr = self._numeric_array()
        return float(arr.min()) if arr.size > 0 else None

    def max(self) -> Optional[float]:
        arr = self._numeric_array()
        return float(arr.max()) if arr.size > 0 else None

    def mean(self) -> Optional[float]:
        arr = self._numeric_array()
        return float(arr.mean()) if arr.size > 0 else None

    def median(self) -> Optional[float]:
        import numpy as np
        arr = self._numeric_array()
        return float(np.median(arr)) if arr.size > 0 else None

    def skew(self) -> float:
        import numpy as np
        arr = self._numeric_array()
        n = arr.size
        if n < 3:
            return 0.0
        mean_v = float(arr.mean())
        std_v = float(arr.std(ddof=1))
        if std_v <= 1e-12:
            return 0.0
        m3 = float(np.mean((arr - mean_v) ** 3))
        return float((math.sqrt(n * (n - 1)) / (n - 2)) * (m3 / (float(arr.std(ddof=0)) ** 3)))

    def nlargest(self, n: int = 4):
        arr = sorted(self._numeric_array().tolist(), reverse=True)
        return _LiteSeries(arr[: max(0, int(n))], name=self.name)


class _LiteGroupBy:
    """Lightweight groupby helper for _LiteDataFrame."""
    def __init__(self, df: "_LiteDataFrame", by_col: str):
        self._df = df
        self._by_col = by_col

    def __getitem__(self, val_col: str):
        groups: Dict[str, List[float]] = {}
        keys = self._df[self._by_col].tolist()
        vals = self._df[val_col].tolist()
        for k, v in zip(keys, vals):
            if v is None or (isinstance(v, float) and math.isnan(v)):
                continue
            groups.setdefault(str(k), []).append(float(v))

        class _AggResult:
            def __init__(self, g: Dict[str, List[float]]):
                self._g = g
            def sum(self) -> Dict[str, float]:
                return {k: float(sum(vs)) for k, vs in self._g.items()}
            def mean(self) -> Dict[str, float]:
                return {k: float(sum(vs) / len(vs)) for k, vs in self._g.items() if vs}
            def count(self) -> Dict[str, int]:
                return {k: len(vs) for k, vs in self._g.items()}
        return _AggResult(groups)


class _LiteDataFrame:
    """Lightweight pandas.DataFrame-compatible wrapper built on stdlib csv + numpy when pandas is not installed."""
    def __init__(self, columns: List[str], rows: List[Dict[str, object]]):
        self.columns: List[str] = list(columns)
        self._rows: List[Dict[str, object]] = [dict(r) for r in rows]

    def __len__(self) -> int:
        return len(self._rows)

    @property
    def shape(self) -> Tuple[int, int]:
        return (len(self._rows), len(self.columns))

    def copy(self) -> "_LiteDataFrame":
        return _LiteDataFrame(self.columns, self._rows)

    def __getitem__(self, key):
        if isinstance(key, str):
            if key not in self.columns:
                raise KeyError(f"Column '{key}' not in {self.columns}")
            return _LiteSeries([r.get(key) for r in self._rows], name=key)
        if isinstance(key, _LiteSeries):
            return self[key.tolist()]
        if isinstance(key, (list, tuple)):
            if len(key) == len(self._rows) and all(isinstance(x, bool) for x in key):
                return _LiteDataFrame(self.columns, [r for r, m in zip(self._rows, key) if m])
            if all(isinstance(x, str) for x in key):
                sub_cols = list(key)
                return _LiteDataFrame(sub_cols, [{c: r.get(c) for c in sub_cols} for r in self._rows])
        raise KeyError(f"Unsupported indexing key: {key!r}")

    def __setitem__(self, col: str, val):
        if col not in self.columns:
            self.columns.append(col)
        vals = val.tolist() if hasattr(val, "tolist") else list(val)
        if len(vals) != len(self._rows):
            raise ValueError(f"Length mismatch assigning column '{col}': {len(vals)} != {len(self._rows)}")
        for r, v in zip(self._rows, vals):
            r[col] = v

    def iterrows(self):
        for idx, r in enumerate(self._rows):
            yield idx, dict(r)

    def to_dict(self, orient: str = "records"):
        if orient == "records":
            return [dict(r) for r in self._rows]
        return {c: [r.get(c) for r in self._rows] for c in self.columns}

    def groupby(self, by_col: str) -> _LiteGroupBy:
        return _LiteGroupBy(self, by_col)


def load_and_split_csv(
    csv_path: str,
    numeric_cols: Optional[List[str]] = None,
    label_cols: Optional[List[str]] = None,
    subtotal_keywords: Optional[List[str]] = None,
    other_keywords: Optional[List[str]] = None,
    known_na_tokens: Optional[List[str]] = None,
):
    """
    Data Codebook Stage 1 & 2 Black-Box Loader, Two-Stage Safe Caster & Normalized 3-Way Splitter.
    Works seamlessly with `pandas` (if installed) or stdlib `csv` + `numpy` (`_LiteDataFrame` fallback).
    1. Strict encoding probing: utf-8-sig -> utf-8 -> cp950 -> big5.
    2. Header strip & embedded BOM (\\ufeff / \\u200b) cleanup + duplicate column name check.
    3. Initial dtype=str loading (keep_default_na=False) to protect leading zeros in codes.
    4. Two-Stage Safe Casting on `numeric_cols`:
       - Stage 1: Maps known legal missing symbols ('', '-', '...', 'N/A', '＊', etc.) to np.nan and counts NAs.
       - Stage 2: Strips thousands commas ',' and validates strict float conversion; raises ValueError on unknown non-numeric tokens.
    5. Normalized 3-Way Split (`df_detail`, `df_other`, `df_subtotal`) with mandatory conservation `assert`:
       `assert len(df_detail) + len(df_other) + len(df_subtotal) == len(df_raw)`
    6. Pure-detail `df_detail` statistics recalculation (detail_min/max vs. raw_min/max, median, mean, skewness, IQR, CR4, NA count).

    Returns:
        Tuple[DataFrame, DataFrame, DataFrame, DataFrame, Dict[str, object]]:
        `(df_raw, df_detail, df_other, df_subtotal, stats_report)`
    """
    import csv as _csv
    import numpy as np

    try:
        import pandas as pd  # type: ignore
        has_pandas = True
    except ImportError:
        pd = None
        has_pandas = False

    encodings = ("utf-8-sig", "utf-8", "cp950", "big5")
    used_encoding = None
    last_err = None
    raw_headers: List[str] = []
    raw_rows_list: List[List[str]] = []

    for enc in encodings:
        try:
            with open(csv_path, "r", encoding=enc, newline="") as f:
                reader = list(_csv.reader(f))
            if not reader:
                raise ValueError(f"CSV file '{csv_path}' is empty.")
            raw_headers = reader[0]
            raw_rows_list = reader[1:]
            used_encoding = enc
            break
        except UnicodeDecodeError as e:
            last_err = e
            continue

    if used_encoding is None:
        raise ValueError(f"Failed to decode CSV '{csv_path}' with encodings {encodings}: {last_err}")

    # Clean column headers (strip whitespace and embedded BOM / zero-width spaces)
    cleaned_cols: List[str] = [
        str(c).replace("\ufeff", "").replace("\u200b", "").strip() for c in raw_headers
    ]
    if len(set(cleaned_cols)) != len(cleaned_cols):
        raise ValueError(f"Duplicate column names detected after BOM/whitespace cleanup: {cleaned_cols}")

    # Build cleaned string records preserving leading zeros
    records: List[Dict[str, object]] = []
    for row_vals in raw_rows_list:
        if not any(str(cell).strip() for cell in row_vals):
            continue
        rec: Dict[str, object] = {}
        for idx, col_name in enumerate(cleaned_cols):
            cell_val = row_vals[idx] if idx < len(row_vals) else ""
            rec[col_name] = str(cell_val).replace("\ufeff", "").replace("\u200b", "").strip()
        records.append(rec)

    num_cols = list(numeric_cols) if numeric_cols else []
    na_vocab = set(KNOWN_NA_STRINGS)
    if known_na_tokens:
        na_vocab.update(str(t).strip().lower() for t in known_na_tokens)

    na_counts: Dict[str, int] = {}
    for col in num_cols:
        if col not in cleaned_cols:
            raise KeyError(f"Numeric column '{col}' not found in CSV columns: {cleaned_cols}")
        na_cnt = 0
        for row_idx, rec in enumerate(records):
            raw_val = rec.get(col, "")
            s = str(raw_val).strip()
            # Stage 1: Explicit mapping of known legal missing tokens to np.nan
            if s == "" or s.lower() in na_vocab or s in na_vocab:
                rec[col] = float("nan")
                na_cnt += 1
                continue
            # Stage 2: Strict numeric conversion (after stripping thousands commas)
            s_num = s.replace(",", "")
            try:
                rec[col] = float(s_num)
            except ValueError as exc:
                raise ValueError(
                    f"Two-Stage Safe Casting failed at column '{col}', row index {row_idx}: "
                    f"unknown non-numeric value {raw_val!r}."
                ) from exc
        na_counts[col] = na_cnt

    # Normalized 3-Way Split (df_detail, df_other, df_subtotal)
    check_cols = (
        list(label_cols)
        if label_cols is not None
        else [c for c in cleaned_cols if c not in num_cols]
    )
    sub_exact = {k.lower() for k in DEFAULT_SUBTOTAL_KEYWORDS}
    if subtotal_keywords:
        sub_exact.update(str(k).strip().lower() for k in subtotal_keywords)
    sub_suffixes = ("總計", "合計", "小計", "總合", "subtotal", "total")

    oth_exact = {
        "其他", "其它", "未分類", "其他項", "其他類", "其他項目", "other", "others", "unclassified"
    }
    if other_keywords:
        oth_exact.update(str(k).strip().lower() for k in other_keywords)

    def _is_subtotal_cell(val: object) -> bool:
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return False
        s = str(val).strip()
        if not s:
            return False
        sl = s.lower()
        if sl in sub_exact or s in sub_exact:
            return True
        return any(s.endswith(sfx) or sl.endswith(sfx) for sfx in sub_suffixes)

    def _is_other_cell(val: object) -> bool:
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return False
        s = str(val).strip()
        if not s:
            return False
        sl = s.lower()
        return sl in oth_exact or s in oth_exact

    detail_rows: List[Dict[str, object]] = []
    other_rows: List[Dict[str, object]] = []
    subtotal_rows: List[Dict[str, object]] = []

    for rec in records:
        if check_cols and any(_is_subtotal_cell(rec.get(c)) for c in check_cols):
            subtotal_rows.append(rec)
        elif check_cols and any(_is_other_cell(rec.get(c)) for c in check_cols):
            other_rows.append(rec)
        else:
            detail_rows.append(rec)

    if has_pandas and pd is not None:
        df_raw = pd.DataFrame(records, columns=cleaned_cols)
        df_detail = pd.DataFrame(detail_rows, columns=cleaned_cols)
        df_other = pd.DataFrame(other_rows, columns=cleaned_cols)
        df_subtotal = pd.DataFrame(subtotal_rows, columns=cleaned_cols)
    else:
        df_raw = _LiteDataFrame(cleaned_cols, records)
        df_detail = _LiteDataFrame(cleaned_cols, detail_rows)
        df_other = _LiteDataFrame(cleaned_cols, other_rows)
        df_subtotal = _LiteDataFrame(cleaned_cols, subtotal_rows)

    assert len(df_detail) + len(df_other) + len(df_subtotal) == len(df_raw), (
        f"三層互斥分流筆數不守恆！detail({len(df_detail)}) + other({len(df_other)}) + "
        f"subtotal({len(df_subtotal)}) != raw({len(df_raw)})"
    )

    # Recalculate pure-detail statistics on df_detail (vs. df_raw)
    col_stats: Dict[str, Dict[str, object]] = {}
    for col in num_cols:
        s_raw = df_raw[col].dropna()
        s_det = df_detail[col].dropna()
        s_oth = df_other[col].dropna()
        s_sub = df_subtotal[col].dropna()
        if len(s_det) > 0:
            det_vals = [float(x) for x in s_det.tolist()]
            q75, q25 = float(np.percentile(det_vals, 75)), float(np.percentile(det_vals, 25))
            det_sum = float(sum(det_vals))
            top4_sum = float(sum(sorted(det_vals, reverse=True)[: min(4, len(det_vals))]))
            cr4 = (top4_sum / det_sum) if det_sum > 0 else None
            col_stats[col] = {
                "detail_min": float(s_det.min()),
                "detail_max": float(s_det.max()),
                "raw_min": float(s_raw.min()) if len(s_raw) > 0 else None,
                "raw_max": float(s_raw.max()) if len(s_raw) > 0 else None,
                "median": float(s_det.median()),
                "mean": float(s_det.mean()),
                "skewness": float(s_det.skew()) if len(s_det) >= 3 else 0.0,
                "iqr": q75 - q25,
                "cr4_share": cr4,
                "detail_sum": det_sum,
                "other_sum": float(s_oth.sum()) if len(s_oth) > 0 else 0.0,
                "subtotal_max": float(s_sub.max()) if len(s_sub) > 0 else None,
                "na_count_raw": int(na_counts.get(col, 0)),
                "na_count_detail": int(df_detail[col].isna().sum()),
            }
        else:
            col_stats[col] = {
                "detail_min": None,
                "detail_max": None,
                "raw_min": float(s_raw.min()) if len(s_raw) > 0 else None,
                "raw_max": float(s_raw.max()) if len(s_raw) > 0 else None,
                "median": None,
                "mean": None,
                "skewness": None,
                "iqr": None,
                "cr4_share": None,
                "detail_sum": 0.0,
                "other_sum": 0.0,
                "subtotal_max": None,
                "na_count_raw": int(na_counts.get(col, 0)),
                "na_count_detail": int(df_detail[col].isna().sum()),
            }

    stats_report: Dict[str, object] = {
        "encoding": used_encoding,
        "columns": cleaned_cols,
        "counts": {
            "raw": len(df_raw),
            "detail": len(df_detail),
            "other": len(df_other),
            "subtotal": len(df_subtotal),
        },
        "numeric_stats": col_stats,
    }
    return df_raw, df_detail, df_other, df_subtotal, stats_report


if __name__ == "__main__":
    import argparse
    import json
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="HCL Color Science Engine & Owner Private Vault Sync CLI."
    )
    parser.add_argument(
        "--restore-private",
        action="store_true",
        help="Pull owner Private repo into reading_sessions/ and restore user_preferences.json & owner_styles/.",
    )
    parser.add_argument(
        "--sync-private",
        action="store_true",
        help="Pull latest Private repo, sync local owner configs into _owner_private_config/, commit and push to Private repo.",
    )
    parser.add_argument(
        "--message",
        "-m",
        type=str,
        default="chore(sync): sync owner sessions and private config",
        help="Commit message used with --sync-private.",
    )
    args = parser.parse_args()

    if args.sync_private:
        res = ensure_owner_private_assets(pull_remote=True, push_remote=True, commit_msg=args.message)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0 if res.get("ok") else 1)
    elif args.restore_private:
        res = ensure_owner_private_assets(pull_remote=True, push_remote=False)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0 if res.get("ok") else 1)
    else:
        prefs = check_user_identity_and_load_prefs()
        print(json.dumps({
            "is_owner": prefs.get("is_owner"),
            "detected_git_user": prefs.get("detected_git_user"),
            "active_qualitative_hex": GEPHI_QUALITATIVE_HEX,
        }, ensure_ascii=False, indent=2))






