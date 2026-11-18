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

    cfg_dir.mkdir(parents=True, exist_ok=True)
    priv_prefs = private_cfg_dir / "user_preferences.json"
    cfg_prefs = cfg_dir / "user_preferences.json"
    priv_styles = private_cfg_dir / "owner_styles"
    cfg_styles = cfg_dir / "owner_styles"
    cfg_styles.mkdir(parents=True, exist_ok=True)

    def _restore_priv_to_cfg(overwrite: bool = False) -> None:
        if priv_prefs.exists() and (not cfg_prefs.exists() or (overwrite and cfg_prefs.read_bytes() != priv_prefs.read_bytes())):
            shutil.copy2(priv_prefs, cfg_prefs)
            actions.append("restored_user_preferences")
        if priv_styles.exists():
            for src_md in priv_styles.glob("*.md"):
                dst_md = cfg_styles / src_md.name
                if not dst_md.exists() or (overwrite and dst_md.read_bytes() != src_md.read_bytes()):
                    shutil.copy2(src_md, dst_md)
                    actions.append(f"restored_style:{src_md.name}")

    def _backup_cfg_to_priv(only_missing: bool = False) -> None:
        if cfg_prefs.exists():
            private_cfg_dir.mkdir(parents=True, exist_ok=True)
            if not priv_prefs.exists() or (not only_missing and cfg_prefs.read_bytes() != priv_prefs.read_bytes()):
                shutil.copy2(cfg_prefs, priv_prefs)
                actions.append("backed_up_user_preferences_to_vault")
        if cfg_styles.exists():
            priv_styles.mkdir(parents=True, exist_ok=True)
            for src_md in cfg_styles.glob("*.md"):
                dst_md = priv_styles / src_md.name
                if not dst_md.exists() or (not only_missing and src_md.read_bytes() != dst_md.read_bytes()):
                    shutil.copy2(src_md, dst_md)
                    actions.append(f"backed_up_style:{src_md.name}")

    def _init_or_clone_sessions_git(allow_checkout: bool = True) -> None:
        if (sessions_dir / ".git").exists():
            return
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
                if allow_checkout:
                    _run_git(["checkout", "--", "."], sessions_dir)
                actions.append("initialized_and_pulled_private_repo")
            else:
                errors.append(f"fetch failed: {(res_fetch.stderr or res_fetch.stdout).strip()}")

    need_remote_bootstrap = not cfg_prefs.exists() and not priv_prefs.exists()

    if push_remote:
        # Sync/push workflow: backup local config/ -> vault FIRST, commit, then pull --rebase, then push.
        if pull_remote or need_remote_bootstrap:
            _init_or_clone_sessions_git(allow_checkout=False)
        _restore_priv_to_cfg(overwrite=False)
        _backup_cfg_to_priv(only_missing=False)

        if (sessions_dir / ".git").exists():
            _run_git(["add", "-A"], sessions_dir)
            st = _run_git(["status", "--porcelain"], sessions_dir)
            if (st.stdout or "").strip():
                c_res = _run_git(["commit", "-m", commit_msg], sessions_dir)
                if c_res.returncode == 0:
                    actions.append("committed_private_vault")
                else:
                    errors.append(f"commit failed: {(c_res.stderr or c_res.stdout).strip()}")

            if pull_remote:
                res_ls = _run_git(["ls-remote", "--heads", "origin", "main"], sessions_dir)
                if res_ls.returncode != 0:
                    errors.append(f"pull failed: {(res_ls.stderr or res_ls.stdout).strip()}")
                elif (res_ls.stdout or "").strip():
                    res_pull = _run_git(["pull", "--rebase", "--autostash", "origin", "main"], sessions_dir)
                    if res_pull.returncode == 0:
                        actions.append("pulled_private_repo")
                        _restore_priv_to_cfg(overwrite=True)
                    else:
                        errors.append(f"pull failed: {(res_pull.stderr or res_pull.stdout).strip()}")

            if not errors:
                p_res = _run_git(["push", "-u", "origin", "main"], sessions_dir)
                if p_res.returncode == 0:
                    actions.append("pushed_private_repo")
                else:
                    errors.append(f"push failed: {(p_res.stderr or p_res.stdout).strip()}")
    else:
        if pull_remote or need_remote_bootstrap:
            if not (sessions_dir / ".git").exists():
                _init_or_clone_sessions_git(allow_checkout=True)
            else:
                res_pull = _run_git(["pull", "--rebase", "--autostash", "origin", "main"], sessions_dir)
                if res_pull.returncode == 0:
                    actions.append("pulled_private_repo")
                else:
                    errors.append(f"pull failed: {(res_pull.stderr or res_pull.stdout).strip()}")

        if pull_remote:
            _restore_priv_to_cfg(overwrite=True)
            _backup_cfg_to_priv(only_missing=True)
        else:
            _restore_priv_to_cfg(overwrite=False)
            _backup_cfg_to_priv(only_missing=False)

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


# -------------------------------------------------------------------------
# Stage 1 Armory & Chart Families High-Precision Black-Box Engine
# (a) Editorial Narrative Components (Data 8 & Data 100 Mode)
# (b) 5 Chart Families High-Precision Plotting Helpers
# (c) RE:LAB 6-Channel Bespoke Metaphor & Thematic Palette Helpers (Data 7 Mode)
# -------------------------------------------------------------------------

def _ensure_cjk_font() -> None:
    """Ensure Matplotlib has CJK-capable sans-serif fonts registered and unicode_minus disabled."""
    try:
        import matplotlib.pyplot as plt
        current = list(plt.rcParams.get("font.sans-serif", []))
        cjk_candidates = [
            "Microsoft JhengHei",
            "PingFang TC",
            "Noto Sans CJK TC",
            "Heiti TC",
            "SimHei",
            "Arial Unicode MS",
        ]
        missing = [c for c in cjk_candidates if c not in current]
        if missing:
            plt.rcParams["font.sans-serif"] = cjk_candidates + [c for c in current if c not in cjk_candidates]
        plt.rcParams["axes.unicode_minus"] = False
    except Exception:
        pass


class _SpotlightStyleResult(dict):
    """
    Dictionary-compatible container returned by `apply_spotlight_colors`.
    Supports:
    - Dict key access: `res["colors"]`, `res["point_colors"]`, `res["text_colors"]`,
      `res["fontweights"]`, `res["sizes"]`, `res["is_highlight"]`, `res["highlight_indices"]`
    - Attribute access: `res.colors`, `res.text_colors`, `res.fontweights`, `res.sizes`
    - 3-tuple unpacking: `colors, text_colors, fontweights = apply_spotlight_colors(...)`
    """
    def __getattr__(self, name: str) -> object:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __iter__(self):
        return iter((self["colors"], self["text_colors"], self["fontweights"]))


def apply_spotlight_colors(
    values_or_labels: Sequence[object],
    top_n: int = 1,
    bottom_n: int = 1,
    highlight_indices: Optional[Sequence[int]] = None,
    highlight_color: Optional[str] = None,
    context_color: str = "#94A3B8",
    **kwargs,
) -> _SpotlightStyleResult:
    """
    Data 8 Editorial Spotlight vs. Context Hierarchy Styling.
    Highlights top_n, bottom_n, and/or explicit `highlight_indices` (or `highlight_labels` via kwargs)
    with deep accent color (`highlight_color`), bold `#0F172A` text, and enlarged dot sizes,
    while pushing remaining context items to muted slate (`context_color="#94A3B8"`) and `#475569` regular text.
    """
    items = list(values_or_labels) if values_or_labels is not None else []
    n = len(items)
    resolved_hl_color = (
        highlight_color
        if highlight_color is not None
        else GEPHI_SEQUENTIAL_SCALES.get("blue", ["#EBF7F9", "#BCE2EB", "#5DBACD", "#2C8B9F", "#0E5B6B"])[4]
    )
    hl_text_color = str(kwargs.get("highlight_text_color", "#0F172A"))
    ctx_text_color = str(kwargs.get("context_text_color", "#475569"))
    hl_weight = str(kwargs.get("highlight_fontweight", "bold"))
    ctx_weight = str(kwargs.get("context_fontweight", "normal"))
    hl_size = float(kwargs.get("highlight_size", 105.0))
    ctx_size = float(kwargs.get("context_size", 54.0))

    if n == 0:
        return _SpotlightStyleResult({
            "colors": [],
            "point_colors": [],
            "dot_colors": [],
            "text_colors": [],
            "label_colors": [],
            "fontweights": [],
            "weights": [],
            "sizes": [],
            "dot_sizes": [],
            "is_highlight": [],
            "highlight_indices": [],
        })

    hl_set = set()
    if highlight_indices is not None:
        for idx in highlight_indices:
            try:
                i_val = int(idx)
                if i_val < 0:
                    i_val = n + i_val
                if 0 <= i_val < n:
                    hl_set.add(i_val)
            except (TypeError, ValueError):
                continue

    highlight_labels = kwargs.get("highlight_labels")
    if highlight_labels:
        hl_label_strs = {str(lbl).strip() for lbl in highlight_labels}
        for i, item in enumerate(items):
            if str(item).strip() in hl_label_strs:
                hl_set.add(i)

    parsed_nums: List[Tuple[float, int]] = []
    for i, item in enumerate(items):
        v = _parse_numeric_or_na(item)
        if v is not None:
            parsed_nums.append((v, i))

    t_n = max(0, int(top_n))
    b_n = max(0, int(bottom_n))
    if t_n > 0 or b_n > 0:
        if len(parsed_nums) > 0:
            sorted_asc = sorted(parsed_nums, key=lambda pair: (pair[0], pair[1]))
            for _, i_low in sorted_asc[:b_n]:
                hl_set.add(i_low)
            for _, i_high in sorted_asc[max(0, len(sorted_asc) - t_n):]:
                hl_set.add(i_high)
        else:
            for i_top in range(min(n, t_n)):
                hl_set.add(i_top)
            for i_bot in range(max(0, n - b_n), n):
                hl_set.add(i_bot)

    is_hl = [i in hl_set for i in range(n)]
    colors = [resolved_hl_color if flag else context_color for flag in is_hl]
    text_colors = [hl_text_color if flag else ctx_text_color for flag in is_hl]
    fontweights = [hl_weight if flag else ctx_weight for flag in is_hl]
    sizes = [hl_size if flag else ctx_size for flag in is_hl]

    return _SpotlightStyleResult({
        "colors": colors,
        "point_colors": colors,
        "dot_colors": colors,
        "text_colors": text_colors,
        "label_colors": text_colors,
        "fontweights": fontweights,
        "weights": fontweights,
        "sizes": sizes,
        "dot_sizes": sizes,
        "is_highlight": is_hl,
        "highlight_indices": sorted(hl_set),
    })


class _BadgeVLineResult(tuple):
    """
    Native tuple `(line, badge_annotation)` returned by `add_badge_vline` with attribute and dict-key access.
    """
    def __new__(cls, line: object, badge: object):
        obj = super().__new__(cls, (line, badge))
        obj.line = line
        obj.badge = badge
        obj.annotation = badge
        return obj

    def __getitem__(self, key):
        if key == "line":
            return self.line
        if key in ("badge", "annotation"):
            return self.badge
        return super().__getitem__(key)


def _estimate_badge_width_pts(text: str, fontsize: float, pad_pts: float = 18.0) -> float:
    """Estimate horizontal width in points of a multi-line CJK/ASCII pill badge."""
    lines = str(text or "").splitlines() or [""]
    max_w = 0.0
    for ln in lines:
        w = 0.0
        for ch in ln:
            w += (1.04 * fontsize) if ord(ch) > 127 else (0.60 * fontsize)
        max_w = max(max_w, w)
    return max_w + pad_pts


def _rebalance_badge_vlines_on_ax(ax: object) -> None:
    """
    Automatic horizontal collision avoidance when multiple `add_badge_vline` calls are made on the same `ax`.
    Shifts colliding top pill badges horizontally in offset points while keeping their leader lines anchored
    to the exact `(x, 1.0)` top of each vertical reference line.
    When an renderer is available, measures real rendered bbox widths for exact multi-badge de-collision.
    """
    registry = getattr(ax, "_badge_vlines_registry", None)
    if not registry or len(registry) < 2:
        return
    try:
        fig = ax.figure
        fig_w_pts = float(fig.get_figwidth()) * 72.0
        fig_h_pts = float(fig.get_figheight()) * 72.0
        pos = ax.get_position()
        ax_w_pts = max(100.0, fig_w_pts * float(pos.width))
        ax_h_pts = max(80.0, fig_h_pts * float(pos.height))
        x_min, x_max = ax.get_xlim()
        x_span = float(x_max - x_min)
        if abs(x_span) < 1e-9:
            return
    except Exception:
        return

    # Sort items by data x position
    ordered = sorted(registry, key=lambda item: float(item["x"]))
    n = len(ordered)
    x_centers_pts = [((float(item["x"]) - float(x_min)) / x_span) * ax_w_pts for item in ordered]

    # Try to measure real rendered pill widths in points if a canvas renderer exists
    widths_pts = [float(item["width_pts"]) for item in ordered]
    try:
        dpi = float(fig.dpi) if hasattr(fig, "dpi") and float(fig.dpi) > 0 else 72.0
        renderer = fig.canvas.get_renderer() if hasattr(fig.canvas, "get_renderer") else None
        if renderer is not None:
            for idx, item in enumerate(ordered):
                patch = item["ann"].get_bbox_patch()
                if patch is not None:
                    ext = patch.get_window_extent(renderer=renderer)
                    if ext.width > 1.0:
                        widths_pts[idx] = max(widths_pts[idx], float(ext.width) * 72.0 / dpi)
    except Exception:
        pass

    offsets = [float(item["user_x_offset_pts"]) for item in ordered]
    locked = [bool(item["user_locked"]) for item in ordered]

    min_gap_pts = 8.0
    for _pass in range(28):
        changed = False
        for i in range(n - 1):
            c_left = x_centers_pts[i] + offsets[i]
            c_right = x_centers_pts[i + 1] + offsets[i + 1]
            req_dist = 0.5 * (widths_pts[i] + widths_pts[i + 1]) + min_gap_pts
            actual_dist = c_right - c_left
            if actual_dist < req_dist - 0.05:
                overlap = req_dist - actual_dist
                if not locked[i] and not locked[i + 1]:
                    offsets[i] -= 0.51 * overlap
                    offsets[i + 1] += 0.51 * overlap
                    changed = True
                elif not locked[i]:
                    offsets[i] -= overlap
                    changed = True
                elif not locked[i + 1]:
                    offsets[i + 1] += overlap
                    changed = True
        if not changed:
            break

    for item, eff_offset in zip(ordered, offsets):
        item["effective_x_offset_pts"] = eff_offset
        ann = item["ann"]
        lift_pts = max(6.0, (float(item["badge_y_axes"]) - 1.0) * ax_h_pts)
        ann.set_position((eff_offset, lift_pts))


def add_badge_vline(
    ax: object,
    x: float,
    badge_text: str,
    color: Optional[str] = None,
    linestyle: str = "--",
    linewidth: float = 2.0,
    badge_y_axes: float = 1.03,
    x_offset_pts: float = 0.0,
    zorder: int = 6,
    **kwargs,
) -> _BadgeVLineResult:
    """
    Data 8 Editorial Dual/Multi Benchmark Reference Line + Top Rounded Callout Pill Badge.
    - Draws a white-halo vertical reference dashed line at `x`.
    - Places a white-background, colored-border rounded pill badge at the top of the plot area (`badge_y_axes`).
    - Automatically avoids horizontal pill collisions when multiple `add_badge_vline` calls share the same `ax`.
    """
    _ensure_cjk_font()
    import matplotlib.patheffects as patheffects

    existing_count = len(getattr(ax, "_badge_vlines_registry", []))
    if color is not None:
        resolved_color = str(color)
    else:
        palette_choices = [
            GEPHI_SEQUENTIAL_SCALES.get("blue", ["#EBF7F9", "#BCE2EB", "#5DBACD", "#2C8B9F", "#0E5B6B"])[3],
            GEPHI_SEQUENTIAL_SCALES.get("orange", ["#FFF3EA", "#FBD8C0", "#ECA072", "#CA6F35", "#97481B"])[3],
            GEPHI_SEQUENTIAL_SCALES.get("pink", ["#FFF0F5", "#F9CEE0", "#E89BB6", "#C46487", "#8D3658"])[3],
            GEPHI_SEQUENTIAL_SCALES.get("green", ["#F1F7EE", "#D0E5CC", "#8FBA88", "#5E8F56", "#396032"])[3],
        ]
        resolved_color = palette_choices[existing_count % len(palette_choices)]

    halo_color = str(kwargs.pop("halo_color", "#FFFFFF"))
    halo_width = float(kwargs.pop("halo_width", linewidth + 2.2))
    fontsize = float(kwargs.pop("fontsize", 9.5))
    fontweight = str(kwargs.pop("fontweight", "bold"))
    badge_bg = str(kwargs.pop("badge_bg", "#FFFFFF"))
    badge_text_color = str(kwargs.pop("badge_text_color", resolved_color))
    badge_border_lw = float(kwargs.pop("badge_border_lw", 1.5))
    ymax_line = float(kwargs.pop("ymax", 1.005))
    ymin_line = float(kwargs.pop("ymin", 0.0))
    line_zorder = float(kwargs.pop("line_zorder", 3.0))

    line = ax.axvline(
        x=float(x),
        ymin=ymin_line,
        ymax=ymax_line,
        color=resolved_color,
        linestyle=linestyle,
        linewidth=linewidth,
        zorder=line_zorder,
        clip_on=False,
        **{k: v for k, v in kwargs.items() if k in ("alpha", "label")},
    )
    line.set_path_effects([
        patheffects.Stroke(linewidth=halo_width, foreground=halo_color),
        patheffects.Normal(),
    ])

    try:
        fig = ax.figure
        ax_h_pts = max(80.0, float(fig.get_figheight()) * 72.0 * float(ax.get_position().height))
    except Exception:
        ax_h_pts = 280.0
    lift_pts = max(6.0, (float(badge_y_axes) - 1.0) * ax_h_pts)

    bbox_props = dict(
        boxstyle="round,pad=0.38,rounding_size=0.45",
        facecolor=badge_bg,
        edgecolor=resolved_color,
        linewidth=badge_border_lw,
    )
    if "bbox" in kwargs and isinstance(kwargs["bbox"], dict):
        bbox_props.update(kwargs["bbox"])

    ann = ax.annotate(
        str(badge_text),
        xy=(float(x), 1.0),
        xycoords=("data", "axes fraction"),
        xytext=(float(x_offset_pts), lift_pts),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=fontsize,
        fontweight=fontweight,
        color=badge_text_color,
        bbox=bbox_props,
        arrowprops=dict(
            arrowstyle="-",
            color=resolved_color,
            lw=1.3,
            shrinkA=0,
            shrinkB=1,
        ),
        zorder=zorder + 1,
        annotation_clip=False,
    )

    if not hasattr(ax, "_badge_vlines_registry"):
        ax._badge_vlines_registry = []
        try:
            ax.callbacks.connect("xlim_changed", lambda target_ax: _rebalance_badge_vlines_on_ax(target_ax))
        except Exception:
            pass

    ax._badge_vlines_registry.append({
        "x": float(x),
        "badge_text": str(badge_text),
        "ann": ann,
        "line": line,
        "badge_y_axes": float(badge_y_axes),
        "user_x_offset_pts": float(x_offset_pts),
        "effective_x_offset_pts": float(x_offset_pts),
        "user_locked": abs(float(x_offset_pts)) > 1e-6,
        "width_pts": _estimate_badge_width_pts(str(badge_text), fontsize=fontsize),
    })
    _rebalance_badge_vlines_on_ax(ax)

    return _BadgeVLineResult(line, ann)


def add_editorial_footer(
    fig: object,
    footer_lines: object,
    y_top: float = 0.088,
    line_spacing: float = 0.022,
    rule_color: str = "#CBD5E1",
    fontsize: float = 9.0,
    **kwargs,
) -> List[object]:
    """
    Data 8 Editorial 4-Tier Structured Footer (`資料補充 / 註 / 來源 / 提醒`).
    - Draws a crisp horizontal top separator rule across the figure bottom margin.
    - Renders structured multi-line editorial notes with bold lead tags (`#0F172A`) and slate body text (`#475569`).
    - Accepts `footer_lines` as a `List[str]`, `Dict[str, str]`, `List[Tuple[str, str]]`, or multi-line `str`.
    """
    _ensure_cjk_font()
    from matplotlib.lines import Line2D

    x_left = float(kwargs.pop("x_left", 0.04))
    x_right = float(kwargs.pop("x_right", 0.96))
    text_color = str(kwargs.pop("text_color", "#475569"))
    prefix_color = str(kwargs.pop("prefix_color", "#0F172A"))
    rule_linewidth = float(kwargs.pop("rule_linewidth", 0.9))
    rule_offset = float(kwargs.pop("rule_offset", 0.012))
    auto_adjust_bottom = bool(kwargs.pop("auto_adjust_bottom", True))

    normalized_lines: List[Tuple[Optional[str], str]] = []
    if isinstance(footer_lines, dict):
        for k, v in footer_lines.items():
            normalized_lines.append((str(k).strip(), str(v).strip()))
    elif isinstance(footer_lines, str):
        for raw_ln in footer_lines.splitlines():
            s = raw_ln.strip()
            if s:
                normalized_lines.append((None, s))
    elif isinstance(footer_lines, (list, tuple)):
        for item in footer_lines:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                normalized_lines.append((str(item[0]).strip(), str(item[1]).strip()))
            elif item is not None:
                normalized_lines.append((None, str(item).strip()))

    # Parse `Prefix：Body` when prefix wasn't passed as a tuple/dict
    parsed_entries: List[Tuple[Optional[str], str]] = []
    for pfx, body in normalized_lines:
        if pfx is not None:
            clean_pfx = pfx.rstrip(":：")
            parsed_entries.append((f"{clean_pfx}：", body))
        else:
            split_done = False
            for sep in ("：", ":"):
                if sep in body:
                    head, tail = body.split(sep, 1)
                    if 1 <= len(head.strip()) <= 10:
                        parsed_entries.append((f"{head.strip()}：", tail.strip()))
                        split_done = True
                        break
            if not split_done:
                parsed_entries.append((None, body))

    if auto_adjust_bottom:
        try:
            needed_bottom = float(y_top) + 0.088
            if hasattr(fig, "subplotpars") and float(fig.subplotpars.bottom) < needed_bottom:
                fig.subplots_adjust(bottom=min(0.32, needed_bottom))
        except Exception:
            pass

    artists: List[object] = []
    rule_y = float(y_top) + rule_offset
    rule_line = Line2D(
        [x_left, x_right],
        [rule_y, rule_y],
        transform=fig.transFigure,
        color=rule_color,
        linewidth=rule_linewidth,
        zorder=10,
    )
    fig.add_artist(rule_line)
    artists.append(rule_line)

    renderer = None
    try:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
    except Exception:
        renderer = None

    for idx, (pfx, body) in enumerate(parsed_entries):
        y_curr = float(y_top) - idx * float(line_spacing)
        if pfx:
            t_pfx = fig.text(
                x_left,
                y_curr,
                pfx,
                fontsize=fontsize,
                fontweight="bold",
                color=prefix_color,
                ha="left",
                va="top",
                **kwargs,
            )
            artists.append(t_pfx)
            if renderer is not None:
                try:
                    bbox_fig = t_pfx.get_window_extent(renderer=renderer).transformed(fig.transFigure.inverted())
                    x_body = float(bbox_fig.x1) + 0.002
                except Exception:
                    x_body = x_left + len(pfx) * (fontsize * 0.00145)
            else:
                x_body = x_left + len(pfx) * (fontsize * 0.00145)
            t_body = fig.text(
                x_body,
                y_curr,
                body,
                fontsize=fontsize,
                fontweight="normal",
                color=text_color,
                ha="left",
                va="top",
                **kwargs,
            )
            artists.append(t_body)
        else:
            t_full = fig.text(
                x_left,
                y_curr,
                body,
                fontsize=fontsize,
                fontweight="normal",
                color=text_color,
                ha="left",
                va="top",
                **kwargs,
            )
            artists.append(t_full)

    return artists


def add_regime_shading_and_events(
    ax: object,
    regimes: Optional[Sequence[object]] = None,
    events: Optional[Sequence[object]] = None,
    **kwargs,
) -> Dict[str, List[object]]:
    """
    Data 7《臺灣數據百閱》Time-Series Regime Background Shading Bands & Historical/Policy Event Callout Boxes.
    - `regimes`: list of dicts `{"start": x0, "end": x1, "label": "...", "color": "#F1F5F9", "alpha": 0.55}`
      or tuples `(x0, x1, label[, color])`.
    - `events`: list of dicts `{"x": x_val, "y": y_val (optional), "label": "...", "color": "#CA6F35"}`
      or tuples `(x_val, label)` / `(x_val, y_val, label[, color])`.
    """
    _ensure_cjk_font()
    regime_patches: List[object] = []
    regime_texts: List[object] = []
    event_annotations: List[object] = []
    event_lines: List[object] = []

    default_band_Palette = [
        GEPHI_LIGHT_BADGE_TINTS[1] if len(GEPHI_LIGHT_BADGE_TINTS) > 1 else "#EBF7F9",
        "#F1F5F9",
        GEPHI_LIGHT_BADGE_TINTS[0] if len(GEPHI_LIGHT_BADGE_TINTS) > 0 else "#FFF3EA",
        GEPHI_LIGHT_BADGE_TINTS[3] if len(GEPHI_LIGHT_BADGE_TINTS) > 3 else "#F1F7EE",
    ]
    fontsize = float(kwargs.pop("fontsize", 9.0))

    if regimes:
        for idx, reg in enumerate(regimes):
            if isinstance(reg, dict):
                x0 = reg.get("start", reg.get("x0", reg.get("xmin", reg.get("from"))))
                x1 = reg.get("end", reg.get("x1", reg.get("xmax", reg.get("to"))))
                label = str(reg.get("label", reg.get("title", reg.get("name", ""))))
                color = str(reg.get("color", default_band_Palette[idx % len(default_band_Palette)]))
                alpha = float(reg.get("alpha", 0.55))
                text_color = str(reg.get("text_color", "#334155"))
                label_y = float(reg.get("label_y", 0.965))
            elif isinstance(reg, (list, tuple)) and len(reg) >= 2:
                x0, x1 = reg[0], reg[1]
                label = str(reg[2]) if len(reg) >= 3 else ""
                color = str(reg[3]) if len(reg) >= 4 else default_band_Palette[idx % len(default_band_Palette)]
                alpha = 0.55
                text_color = "#334155"
                label_y = 0.965
            else:
                continue

            if x0 is None or x1 is None:
                continue
            span_patch = ax.axvspan(float(x0), float(x1), color=color, alpha=alpha, zorder=0, lw=0)
            regime_patches.append(span_patch)
            if label:
                mid_x = 0.5 * (float(x0) + float(x1))
                t_obj = ax.text(
                    mid_x,
                    label_y,
                    label,
                    transform=ax.get_xaxis_transform(),
                    ha="center",
                    va="top",
                    fontsize=fontsize,
                    fontweight="bold",
                    color=text_color,
                    bbox=dict(boxstyle="round,pad=0.22", facecolor="#FFFFFF", edgecolor="none", alpha=0.78),
                    zorder=2,
                )
                regime_texts.append(t_obj)

    if events:
        default_ev_color = GEPHI_SEQUENTIAL_SCALES.get("orange", ["#FFF3EA", "#FBD8C0", "#ECA072", "#CA6F35", "#97481B"])[3]
        stagger_levels = [0.84, 0.70, 0.56, 0.77]
        for idx, ev in enumerate(events):
            y_val = None
            color = default_ev_color
            dx_pts = 0.0
            dy_pts = 26.0
            y_axes = stagger_levels[idx % len(stagger_levels)]
            draw_vline = True

            if isinstance(ev, dict):
                x_val = ev.get("x")
                y_val = ev.get("y")
                label = str(ev.get("label", ev.get("text", ev.get("title", ""))))
                color = str(ev.get("color", default_ev_color))
                dx_pts = float(ev.get("dx_pts", ev.get("x_offset_pts", 0.0)))
                dy_pts = float(ev.get("dy_pts", ev.get("y_offset_pts", 26.0)))
                if "y_axes" in ev:
                    y_axes = float(ev["y_axes"])
                draw_vline = bool(ev.get("vline", y_val is None))
            elif isinstance(ev, (list, tuple)):
                if len(ev) == 2:
                    x_val, label = ev[0], str(ev[1])
                elif len(ev) >= 3:
                    if isinstance(ev[1], (int, float)) and not isinstance(ev[1], bool):
                        x_val, y_val, label = ev[0], float(ev[1]), str(ev[2])
                        draw_vline = False
                        if len(ev) >= 4:
                            color = str(ev[3])
                    else:
                        x_val, label, color = ev[0], str(ev[1]), str(ev[2])
                else:
                    continue
            else:
                continue

            if x_val is None:
                continue

            if draw_vline:
                vl = ax.axvline(float(x_val), color=color, linestyle=":", linewidth=1.4, alpha=0.85, zorder=3)
                event_lines.append(vl)

            bbox_ev = dict(
                boxstyle="round,pad=0.35,rounding_size=0.35",
                facecolor="#FFFFFF",
                edgecolor=color,
                linewidth=1.3,
            )
            if y_val is not None:
                ax.scatter(
                    [float(x_val)],
                    [float(y_val)],
                    s=58,
                    color=color,
                    edgecolors="#FFFFFF",
                    linewidths=1.5,
                    zorder=5,
                )
                ann = ax.annotate(
                    label,
                    xy=(float(x_val), float(y_val)),
                    xycoords="data",
                    xytext=(dx_pts, dy_pts),
                    textcoords="offset points",
                    ha="center",
                    va="bottom" if dy_pts >= 0 else "top",
                    fontsize=fontsize,
                    fontweight="bold",
                    color="#0F172A",
                    bbox=bbox_ev,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.3, shrinkA=2, shrinkB=4),
                    zorder=6,
                )
            else:
                ann = ax.annotate(
                    label,
                    xy=(float(x_val), y_axes),
                    xycoords=("data", "axes fraction"),
                    xytext=(dx_pts, 0.0),
                    textcoords="offset points",
                    ha="center",
                    va="center",
                    fontsize=fontsize,
                    fontweight="bold",
                    color="#0F172A",
                    bbox=bbox_ev,
                    zorder=6,
                )
            event_annotations.append(ann)

    return {
        "regime_patches": regime_patches,
        "regime_texts": regime_texts,
        "event_lines": event_lines,
        "event_annotations": event_annotations,
    }


def add_inset_leaderboard(
    ax: object,
    labels: Sequence[str],
    values: Sequence[float],
    bbox: Tuple[float, float, float, float] = (0.62, 0.08, 0.34, 0.32),
    title: str = "",
    color: Optional[str] = None,
    **kwargs,
) -> object:
    """
    Data 7 Bubble Tea Density Map Mode: Rounded white-card Inset Leaderboard in a corner of the main chart.
    Returns the created `inset_ax` Matplotlib Axes object.
    """
    _ensure_cjk_font()
    import numpy as np

    bg_color = str(kwargs.pop("bg_color", "#FFFFFF"))
    border_color = str(kwargs.pop("border_color", "#CBD5E1"))
    value_fmt = str(kwargs.pop("value_fmt", "{:.1f}"))
    max_items = int(kwargs.pop("max_items", 5))
    fontsize = float(kwargs.pop("fontsize", 8.5))
    sort_desc = bool(kwargs.pop("sort_desc", False))
    zorder = int(kwargs.pop("zorder", 8))

    resolved_color = color if color is not None else GEPHI_QUALITATIVE_HEX[0]
    top_color = GEPHI_SEQUENTIAL_SCALES.get("orange", ["#FFF3EA", "#FBD8C0", "#ECA072", "#CA6F35", "#97481B"])[3]

    pairs = [(str(lbl), float(val)) for lbl, val in zip(labels, values) if _parse_numeric_or_na(val) is not None]
    if sort_desc:
        pairs.sort(key=lambda item: item[1], reverse=True)
    pairs = pairs[:max(1, max_items)]

    inset_ax = ax.inset_axes(list(bbox), zorder=zorder)
    inset_ax.set_facecolor(bg_color)
    for side in ("top", "right", "bottom", "left"):
        if side in inset_ax.spines:
            inset_ax.spines[side].set_visible(True)
            inset_ax.spines[side].set_color(border_color)
            inset_ax.spines[side].set_linewidth(1.2)

    if not pairs:
        inset_ax.set_xticks([])
        inset_ax.set_yticks([])
        return inset_ax

    # Reverse so rank #1 is at top of horizontal bar chart
    display_pairs = list(reversed(pairs))
    y_pos = np.arange(len(display_pairs))
    disp_labels = [p[0] for p in display_pairs]
    disp_vals = [p[1] for p in display_pairs]
    v_max = max(max(disp_vals), 1e-6)

    bar_colors = [
        (top_color if color is None else resolved_color) if idx == len(display_pairs) - 1 else resolved_color
        for idx in range(len(display_pairs))
    ]
    inset_ax.barh(y_pos, [v_max * 1.05] * len(display_pairs), height=0.58, color="#F1F5F9", edgecolor="none", zorder=1)
    inset_ax.barh(y_pos, disp_vals, height=0.58, color=bar_colors, edgecolor="none", zorder=2)

    inset_ax.set_yticks(y_pos)
    inset_ax.set_yticklabels(disp_labels, fontsize=fontsize, fontweight="bold", color="#1E293B")
    inset_ax.tick_params(axis="y", length=0, pad=4)
    inset_ax.set_xticks([])
    inset_ax.set_xlim(0, v_max * 1.34)
    inset_ax.set_ylim(-0.65, len(display_pairs) - 0.30)

    for y_i, val in zip(y_pos, disp_vals):
        inset_ax.text(
            val + v_max * 0.04,
            y_i,
            value_fmt.format(val),
            va="center",
            ha="left",
            fontsize=fontsize,
            fontweight="bold",
            color="#0F172A",
            zorder=3,
        )

    if title:
        inset_ax.set_title(
            title,
            fontsize=fontsize + 0.8,
            fontweight="bold",
            color="#0F172A",
            loc="left",
            pad=5,
        )

    return inset_ax


# -------------------------------------------------------------------------
# (b) 5 Chart Families High-Precision Plotting Helpers
# -------------------------------------------------------------------------

def plot_cleveland_dot(
    ax: object,
    labels: Sequence[str],
    values: Sequence[float],
    top_n: int = 1,
    bottom_n: int = 1,
    highlight_indices: Optional[Sequence[int]] = None,
    highlight_color: Optional[str] = None,
    context_color: str = "#94A3B8",
    stem_color: str = "#CBD5E1",
    stem_linestyle: str = "--",
    stem_linewidth: float = 1.0,
    value_fmt: str = "{:.1f}",
    value_offset_pts: float = 7.0,
    sort_values: bool = True,
    ascending: bool = True,
    x_padding_ratio: float = 0.14,
    **kwargs,
) -> Dict[str, object]:
    """
    Data 8 Editorial Cleveland Dot Plot:
    - Focuses X-axis on the true non-zero variation interval (unless `force_zero=True`).
    - Replaces heavy solid bars with horizontal dashed guide stems (`#CBD5E1`) + spotlight/context dots.
    - Applies `apply_spotlight_colors` to highlight top_n / bottom_n extremes in both dot color/size and Y-tick typography.
    - Places direct value labels immediately to the right of every dot.
    """
    _ensure_cjk_font()
    import numpy as np

    pairs = [
        (str(lbl), float(val))
        for lbl, val in zip(labels, values)
        if _parse_numeric_or_na(val) is not None
    ]
    if not pairs:
        return {"scatter": None, "stems": None, "annotations": [], "spotlight": None, "ax": ax}

    if sort_values:
        pairs.sort(key=lambda item: item[1], reverse=not ascending)

    sorted_labels = [p[0] for p in pairs]
    sorted_vals = [p[1] for p in pairs]
    n = len(pairs)
    y_pos = np.arange(n)

    spot = apply_spotlight_colors(
        sorted_vals,
        top_n=top_n,
        bottom_n=bottom_n,
        highlight_indices=highlight_indices,
        highlight_color=highlight_color,
        context_color=context_color,
        highlight_size=kwargs.pop("highlight_size", 110.0),
        context_size=kwargs.pop("context_size", 56.0),
    )

    v_min = min(sorted_vals)
    v_max = max(sorted_vals)
    span = max(1e-6, v_max - v_min)
    force_zero = bool(kwargs.pop("force_zero", False))
    custom_xlim = kwargs.pop("xlim", None)

    if custom_xlim is not None:
        x_left, x_right = float(custom_xlim[0]), float(custom_xlim[1])
    elif force_zero:
        x_left = 0.0
        x_right = v_max + span * max(0.16, float(x_padding_ratio))
    else:
        x_left = v_min - span * 0.11
        x_right = v_max + span * max(0.16, float(x_padding_ratio))

    ax.set_xlim(x_left, x_right)
    ax.set_ylim(-0.75, n - 0.25)

    stems = ax.hlines(
        y=y_pos,
        xmin=x_left,
        xmax=sorted_vals,
        color=stem_color,
        linestyle=stem_linestyle,
        linewidth=stem_linewidth,
        zorder=2,
    )

    sc = ax.scatter(
        sorted_vals,
        y_pos,
        s=spot["sizes"],
        c=spot["colors"],
        edgecolors="#FFFFFF",
        linewidths=1.5,
        zorder=4,
        **kwargs,
    )

    ax.set_yticks(y_pos)
    tick_labels = ax.set_yticklabels(sorted_labels, fontsize=10.5)
    for tick_lbl, t_color, t_weight in zip(tick_labels, spot["text_colors"], spot["fontweights"]):
        tick_lbl.set_color(t_color)
        tick_lbl.set_fontweight(t_weight)
    ax.tick_params(axis="y", length=0, pad=6)

    anns = []
    import matplotlib.patheffects as patheffects
    fontsize_val = float(kwargs.get("value_fontsize", 9.8))
    for i, (val, y_i) in enumerate(zip(sorted_vals, y_pos)):
        txt = value_fmt(val) if callable(value_fmt) else value_fmt.format(val)
        ann = ax.annotate(
            txt,
            xy=(val, float(y_i)),
            xytext=(float(value_offset_pts), 0.0),
            textcoords="offset points",
            va="center",
            ha="left",
            fontsize=fontsize_val,
            fontweight=spot["fontweights"][i],
            color=spot["text_colors"][i],
            zorder=7,
        )
        ann.set_path_effects([
            patheffects.Stroke(linewidth=2.8, foreground="#FFFFFF"),
            patheffects.Normal(),
        ])
        anns.append(ann)

    despine_axes(ax, grid_axis="x", grid_alpha=0.45)
    return {
        "scatter": sc,
        "stems": stems,
        "annotations": anns,
        "spotlight": spot,
        "labels": sorted_labels,
        "values": sorted_vals,
        "ax": ax,
    }


def plot_dumbbell(
    ax: object,
    labels: Sequence[str],
    val_start: Sequence[float],
    val_end: Sequence[float],
    label_start: str = "期初 / 基準",
    label_end: str = "期末 / 現況",
    color_start: Optional[str] = None,
    color_end: Optional[str] = None,
    bar_color: str = "#CBD5E1",
    bar_linewidth: float = 3.2,
    dot_size: float = 90.0,
    show_delta: bool = True,
    delta_fmt: str = "{:+.1f}",
    sort_by: Optional[str] = "end",
    **kwargs,
) -> Dict[str, object]:
    """
    Data 7 Dumbbell Span Plot with connecting bars and signed delta callouts.
    """
    _ensure_cjk_font()
    import numpy as np

    c_start = color_start if color_start is not None else GEPHI_QUALITATIVE_HEX[1]
    c_end = color_end if color_end is not None else GEPHI_QUALITATIVE_HEX[0]

    rows = []
    for lbl, vs, ve in zip(labels, val_start, val_end):
        ps, pe = _parse_numeric_or_na(vs), _parse_numeric_or_na(ve)
        if ps is not None and pe is not None:
            rows.append((str(lbl), float(ps), float(pe), float(pe - ps)))

    if not rows:
        return {"scatter_start": None, "scatter_end": None, "bars": None, "annotations": [], "ax": ax}

    if sort_by == "end":
        rows.sort(key=lambda r: r[2])
    elif sort_by == "start":
        rows.sort(key=lambda r: r[1])
    elif sort_by == "delta":
        rows.sort(key=lambda r: r[3])

    n = len(rows)
    y_pos = np.arange(n)
    r_labels = [r[0] for r in rows]
    r_start = [r[1] for r in rows]
    r_end = [r[2] for r in rows]
    r_delta = [r[3] for r in rows]

    bars = ax.hlines(
        y=y_pos,
        xmin=[min(a, b) for a, b in zip(r_start, r_end)],
        xmax=[max(a, b) for a, b in zip(r_start, r_end)],
        color=bar_color,
        linewidth=bar_linewidth,
        zorder=2,
    )
    sc_start = ax.scatter(
        r_start,
        y_pos,
        s=dot_size,
        color=c_start,
        edgecolors="#FFFFFF",
        linewidths=1.5,
        label=label_start,
        zorder=4,
    )
    sc_end = ax.scatter(
        r_end,
        y_pos,
        s=dot_size,
        color=c_end,
        edgecolors="#FFFFFF",
        linewidths=1.5,
        label=label_end,
        zorder=5,
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(r_labels, fontsize=10.5, fontweight="bold", color="#1E293B")
    ax.tick_params(axis="y", length=0, pad=6)

    all_vals = r_start + r_end
    v_min, v_max = min(all_vals), max(all_vals)
    span = max(1e-6, v_max - v_min)
    ax.set_xlim(v_min - span * 0.10, v_max + span * 0.16)
    ax.set_ylim(-0.65, n - 0.30)

    anns = []
    if show_delta:
        pos_ink = GEPHI_SEQUENTIAL_SCALES.get("orange", ["#FFF3EA", "#FBD8C0", "#ECA072", "#CA6F35", "#97481B"])[3]
        neg_ink = GEPHI_SEQUENTIAL_SCALES.get("blue", ["#EBF7F9", "#BCE2EB", "#5DBACD", "#2C8B9F", "#0E5B6B"])[3]
        for y_i, vs, ve, d_val in zip(y_pos, r_start, r_end, r_delta):
            x_right_dot = max(vs, ve)
            d_txt = delta_fmt.format(d_val)
            d_col = pos_ink if d_val >= 0 else neg_ink
            ann = ax.annotate(
                d_txt,
                xy=(x_right_dot, float(y_i)),
                xytext=(8.0, 0.0),
                textcoords="offset points",
                va="center",
                ha="left",
                fontsize=9.5,
                fontweight="bold",
                color=d_col,
                zorder=6,
            )
            anns.append(ann)

    despine_axes(ax, grid_axis="x", grid_alpha=0.45)
    if kwargs.get("show_legend", True):
        ax.legend(frameon=False, loc="upper right", fontsize=9.5)

    return {
        "scatter_start": sc_start,
        "scatter_end": sc_end,
        "bars": bars,
        "annotations": anns,
        "ax": ax,
    }


def _decollide_1d_positions(positions: List[float], min_dist: float) -> List[float]:
    """Relax 1D vertical label coordinates so adjacent labels maintain at least `min_dist` separation."""
    if len(positions) <= 1 or min_dist <= 0:
        return list(positions)
    indexed = sorted(enumerate(positions), key=lambda pair: pair[1])
    adjusted = [p for _, p in indexed]
    for _ in range(12):
        moved = False
        for i in range(len(adjusted) - 1):
            gap = adjusted[i + 1] - adjusted[i]
            if gap < min_dist:
                push = 0.5 * (min_dist - gap)
                adjusted[i] -= push
                adjusted[i + 1] += push
                moved = True
        if not moved:
            break
    out = [0.0] * len(positions)
    for (orig_idx, _), adj_val in zip(indexed, adjusted):
        out[orig_idx] = adj_val
    return out


def plot_slope_chart(
    ax: object,
    labels: Sequence[str],
    val_t1: Sequence[float],
    val_t2: Sequence[float],
    t1_label: str = "期初 (T1)",
    t2_label: str = "期末 (T2)",
    up_color: Optional[str] = None,
    down_color: Optional[str] = None,
    neutral_color: str = "#94A3B8",
    value_fmt: str = "{:.1f}",
    linewidth: float = 2.4,
    dot_size: float = 75.0,
    **kwargs,
) -> Dict[str, object]:
    """
    Data 5 & Data 7 Two-Period Ranking & Trajectory Slope Chart with 1D vertical label collision avoidance.
    """
    _ensure_cjk_font()

    c_up = up_color if up_color is not None else GEPHI_QUALITATIVE_HEX[0]
    c_down = down_color if down_color is not None else GEPHI_QUALITATIVE_HEX[1]
    threshold = float(kwargs.pop("threshold", 1e-6))

    rows = []
    for lbl, v1, v2 in zip(labels, val_t1, val_t2):
        p1, p2 = _parse_numeric_or_na(v1), _parse_numeric_or_na(v2)
        if p1 is not None and p2 is not None:
            rows.append((str(lbl), float(p1), float(p2)))

    if not rows:
        return {"lines": [], "annotations": [], "ax": ax}

    v_all = [r[1] for r in rows] + [r[2] for r in rows]
    v_min, v_max = min(v_all), max(v_all)
    v_span = max(1e-6, v_max - v_min)

    ax.axvline(0.0, color="#CBD5E1", linestyle="--", linewidth=1.2, zorder=1)
    ax.axvline(1.0, color="#CBD5E1", linestyle="--", linewidth=1.2, zorder=1)

    y1_adj = _decollide_1d_positions([r[1] for r in rows], min_dist=v_span * 0.055)
    y2_adj = _decollide_1d_positions([r[2] for r in rows], min_dist=v_span * 0.055)

    lines = []
    anns = []
    for idx, (lbl, v1, v2) in enumerate(rows):
        diff = v2 - v1
        if diff > threshold:
            col = c_up
            fw = "bold"
            t_col = "#0F172A"
        elif diff < -threshold:
            col = c_down
            fw = "bold"
            t_col = "#0F172A"
        else:
            col = neutral_color
            fw = "normal"
            t_col = "#475569"

        ln = ax.plot([0.0, 1.0], [v1, v2], color=col, linewidth=linewidth, zorder=3)[0]
        ax.scatter([0.0, 1.0], [v1, v2], s=dot_size, color=col, edgecolors="#FFFFFF", linewidths=1.5, zorder=4)
        lines.append(ln)

        ann_left = ax.annotate(
            f"{lbl}  {value_fmt.format(v1)}",
            xy=(0.0, v1),
            xytext=(-0.05, y1_adj[idx]),
            textcoords="data",
            ha="right",
            va="center",
            fontsize=9.8,
            fontweight=fw,
            color=t_col,
            zorder=5,
        )
        ann_right = ax.annotate(
            f"{value_fmt.format(v2)}  {lbl}",
            xy=(1.0, v2),
            xytext=(1.05, y2_adj[idx]),
            textcoords="data",
            ha="left",
            va="center",
            fontsize=9.8,
            fontweight=fw,
            color=t_col,
            zorder=5,
        )
        anns.extend([ann_left, ann_right])

    ax.set_xlim(-0.42, 1.42)
    ax.set_ylim(v_min - v_span * 0.10, v_max + v_span * 0.12)
    ax.set_xticks([0.0, 1.0])
    ax.set_xticklabels([t1_label, t2_label], fontsize=11.0, fontweight="bold", color="#0F172A")
    ax.set_yticks([])
    for side in ("top", "right", "left", "bottom"):
        if side in ax.spines:
            ax.spines[side].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=8)

    return {"lines": lines, "annotations": anns, "ax": ax}


def plot_bullet(
    ax: object,
    labels: Sequence[str],
    actuals: Sequence[float],
    targets: Sequence[float],
    bands: Optional[Sequence[Sequence[float]]] = None,
    band_colors: Optional[Sequence[str]] = None,
    actual_color: Optional[str] = None,
    target_color: str = "#0F172A",
    bar_height: float = 0.60,
    actual_height: float = 0.28,
    value_fmt: str = "{:.1f}",
    **kwargs,
) -> Dict[str, object]:
    """
    Data 5 Stephen Few (2006) Bullet Graph:
    Encodes actual performance bar, target perpendicular reference marker, and 3-tier qualitative background ranges.
    """
    _ensure_cjk_font()
    import numpy as np

    n = min(len(labels), len(actuals), len(targets))
    if n == 0:
        return {"actual_bars": None, "target_lines": [], "band_bars": [], "ax": ax}

    c_actual = (
        actual_color
        if actual_color is not None
        else GEPHI_SEQUENTIAL_SCALES.get("blue", ["#EBF7F9", "#BCE2EB", "#5DBACD", "#2C8B9F", "#0E5B6B"])[3]
    )
    b_colors = list(band_colors) if band_colors is not None else ["#CBD5E1", "#E2E8F0", "#F1F5F9"]

    y_pos = np.arange(n)
    clean_labels = [str(labels[i]) for i in range(n)]
    clean_actuals = [float(actuals[i]) for i in range(n)]
    clean_targets = [float(targets[i]) for i in range(n)]

    resolved_bands: List[List[float]] = []
    if bands is not None and len(bands) > 0:
        if isinstance(bands[0], (int, float)):
            shared = sorted(float(x) for x in bands)
            resolved_bands = [list(shared) for _ in range(n)]
        else:
            for i in range(n):
                row_b = bands[i] if i < len(bands) else bands[-1]
                resolved_bands.append(sorted(float(x) for x in row_b))
    else:
        for act, tgt in zip(clean_actuals, clean_targets):
            ref = max(act, tgt, 1.0)
            resolved_bands.append([0.65 * ref, 0.95 * ref, 1.20 * ref])

    band_bars = []
    max_x = 0.0
    for i, y_i in enumerate(y_pos):
        tiers = resolved_bands[i]
        max_x = max(max_x, tiers[-1], clean_actuals[i], clean_targets[i])
        prev = 0.0
        for t_idx, tier_end in enumerate(tiers):
            w = max(0.0, tier_end - prev)
            col = b_colors[min(t_idx, len(b_colors) - 1)]
            b_patch = ax.barh(
                y_i,
                w,
                left=prev,
                height=bar_height,
                color=col,
                edgecolor="none",
                zorder=1,
            )
            band_bars.append(b_patch)
            prev = tier_end

    actual_bars = ax.barh(
        y_pos,
        clean_actuals,
        height=actual_height,
        color=c_actual,
        edgecolor="none",
        zorder=3,
        label=kwargs.get("actual_label", "實際值 (Actual)"),
    )

    target_lines = []
    for i, (y_i, tgt) in enumerate(zip(y_pos, clean_targets)):
        tl = ax.plot(
            [tgt, tgt],
            [y_i - bar_height * 0.44, y_i + bar_height * 0.44],
            color=target_color,
            linewidth=2.6,
            zorder=4,
            label=kwargs.get("target_label", "目標值 (Target)") if i == 0 else None,
        )[0]
        target_lines.append(tl)

    anns = []
    for y_i, act, tgt, tiers in zip(y_pos, clean_actuals, clean_targets, resolved_bands):
        right_edge = max(tiers[-1], act, tgt)
        pct = (act / tgt * 100.0) if abs(tgt) > 1e-9 else 0.0
        ann = ax.annotate(
            f"{value_fmt.format(act)} / 目標 {value_fmt.format(tgt)} ({pct:.0f}%)",
            xy=(right_edge, float(y_i)),
            xytext=(8.0, 0.0),
            textcoords="offset points",
            va="center",
            ha="left",
            fontsize=9.2,
            fontweight="bold",
            color="#0F172A",
            zorder=5,
        )
        anns.append(ann)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(clean_labels, fontsize=10.5, fontweight="bold", color="#0F172A")
    ax.tick_params(axis="y", length=0, pad=6)
    ax.set_xlim(0.0, max_x * 1.28)
    ax.set_ylim(-0.65, n - 0.30)
    despine_axes(ax, grid_axis="x", grid_alpha=0.40)

    return {
        "actual_bars": actual_bars,
        "target_lines": target_lines,
        "band_bars": band_bars,
        "annotations": anns,
        "ax": ax,
    }


def plot_marimekko(
    ax: object,
    categories: Sequence[str],
    weights: Sequence[float],
    sub_matrix_pct: Sequence[Sequence[float]],
    sub_labels: Sequence[str],
    colors: Optional[Sequence[str]] = None,
    edgecolor: str = "#FFFFFF",
    linewidth: float = 1.6,
    show_cell_labels: bool = True,
    min_pct_for_label: float = 7.5,
    show_weight_header: bool = True,
    weight_fmt: str = "{:.0f}",
    **kwargs,
) -> Dict[str, object]:
    """
    Data 7 2D Marimekko / Mekko Chart:
    - Column X-width is proportional to each entity's scale/weight (`weights`), normalized to 0..100%.
    - Column Y-height is a 0..100% stacked composition across `sub_labels`.
    - Automatically checks WCAG contrast via `ink()` for direct in-cell labels.
    """
    _ensure_cjk_font()
    from matplotlib.patches import Rectangle
    import numpy as np

    n_cats = len(categories)
    n_subs = len(sub_labels)
    if n_cats == 0 or n_subs == 0:
        return {"patches": [], "annotations": [], "x_edges": [], "ax": ax}

    w_arr = np.asarray([max(0.0, float(w)) for w in weights[:n_cats]], dtype="float64")
    total_w = float(w_arr.sum())
    if total_w <= 0:
        w_shares = np.full(n_cats, 100.0 / n_cats)
    else:
        w_shares = (w_arr / total_w) * 100.0

    mat = np.asarray(sub_matrix_pct, dtype="float64")
    if mat.shape == (n_cats, n_subs):
        cat_sub_mat = mat.copy()
    elif mat.shape == (n_subs, n_cats):
        cat_sub_mat = mat.T.copy()
    else:
        raise ValueError(
            f"sub_matrix_pct shape {mat.shape} does not match categories ({n_cats}) x sub_labels ({n_subs})."
        )

    # Normalize each category column to sum to 100%
    for i in range(n_cats):
        col_sum = float(cat_sub_mat[i].sum())
        if col_sum > 0:
            cat_sub_mat[i] = (cat_sub_mat[i] / col_sum) * 100.0

    if colors is not None:
        sub_colors = list(colors)
    else:
        base_cols = list(GEPHI_QUALITATIVE_HEX)
        if n_subs > 4:
            base_cols.append(GEPHI_DISCRETE_NEUTRALS["other_aggregated"])
            while len(base_cols) < n_subs:
                base_cols.append("#94A3B8")
        sub_colors = base_cols[:n_subs]

    x_edges = [0.0]
    for w_s in w_shares:
        x_edges.append(x_edges[-1] + float(w_s))

    patches = []
    anns = []
    legend_handles = []

    for j in range(n_subs):
        col_hex = sub_colors[j % len(sub_colors)]
        proxy = Rectangle((0, 0), 1, 1, facecolor=col_hex, edgecolor=edgecolor, linewidth=linewidth, label=str(sub_labels[j]))
        legend_handles.append(proxy)

    for i in range(n_cats):
        x0 = x_edges[i]
        w = w_shares[i]
        y_bot = 0.0
        for j in range(n_subs):
            h_pct = float(cat_sub_mat[i, j])
            col_hex = sub_colors[j % len(sub_colors)]
            rect = Rectangle(
                (x0, y_bot),
                w,
                h_pct,
                facecolor=col_hex,
                edgecolor=edgecolor,
                linewidth=linewidth,
                zorder=2,
            )
            ax.add_patch(rect)
            patches.append(rect)

            if show_cell_labels and h_pct >= min_pct_for_label and w >= 7.5:
                cell_ink = ink(col_hex)
                label_str = f"{sub_labels[j]}\n{h_pct:.1f}%" if (h_pct >= 13.5 and w >= 12.0) else f"{h_pct:.1f}%"
                ann = ax.text(
                    x0 + 0.5 * w,
                    y_bot + 0.5 * h_pct,
                    label_str,
                    ha="center",
                    va="center",
                    fontsize=8.8 if w >= 12.0 else 8.0,
                    fontweight="bold",
                    color=cell_ink,
                    zorder=4,
                )
                anns.append(ann)
            y_bot += h_pct

        if show_weight_header:
            w_txt = weight_fmt.format(w_arr[i])
            hdr = ax.text(
                x0 + 0.5 * w,
                101.5,
                w_txt,
                ha="center",
                va="bottom",
                fontsize=8.8,
                fontweight="bold",
                color="#334155",
                zorder=4,
            )
            anns.append(hdr)

    x_mids = [0.5 * (x_edges[i] + x_edges[i + 1]) for i in range(n_cats)]
    x_tick_labels = [f"{categories[i]}\n({w_shares[i]:.1f}%)" for i in range(n_cats)]
    ax.set_xticks(x_mids)
    ax.set_xticklabels(x_tick_labels, fontsize=9.8, fontweight="bold", color="#0F172A")
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_xlim(0.0, 100.0)
    ax.set_ylim(0.0, 108.0 if show_weight_header else 101.0)
    ax.set_ylabel("結構佔比 (%)", fontsize=10.5, fontweight="bold", color="#0F172A")
    despine_axes(ax, grid_axis=None)
    if hasattr(ax, "spines") and "left" in ax.spines:
        ax.spines["left"].set_bounds(0.0, 100.0)

    title_str = kwargs.get("title")
    show_leg = bool(kwargs.get("show_legend", True))
    legend_ncol = int(kwargs.get("legend_ncol", min(n_subs, 5)))
    legend_rows = max(1, (n_subs + max(1, legend_ncol) - 1) // max(1, legend_ncol)) if show_leg else 0
    default_title_pad = (28.0 + 18.0 * (legend_rows - 1)) if show_leg else 14.0
    title_pad = float(kwargs.get("title_pad", default_title_pad))

    if show_leg and hasattr(ax, "set_title"):
        _orig_set_title = getattr(ax, "_marimekko_orig_set_title", ax.set_title)
        ax._marimekko_orig_set_title = _orig_set_title
        ax._marimekko_min_title_pad = title_pad

        def _safe_set_title(label, fontdict=None, loc=None, pad=None, **st_kwargs):
            min_pad = getattr(ax, "_marimekko_min_title_pad", title_pad)
            eff_pad = max(float(pad), min_pad) if pad is not None else min_pad
            return _orig_set_title(label, fontdict=fontdict, loc=loc, pad=eff_pad, **st_kwargs)

        ax.set_title = _safe_set_title

    if title_str:
        ax.set_title(
            str(title_str),
            loc=str(kwargs.get("title_loc", "left")),
            fontsize=float(kwargs.get("title_fontsize", 12.5)),
            fontweight="bold",
            color="#0F172A",
            pad=title_pad,
        )
    elif show_leg and hasattr(ax, "get_title"):
        for _loc, _attr in (("left", "_left_title"), ("center", "title"), ("right", "_right_title")):
            existing_t = ax.get_title(loc=_loc)
            if existing_t:
                t_obj = getattr(ax, _attr, None)
                saved_fs = t_obj.get_fontsize() if t_obj is not None else None
                saved_fw = t_obj.get_fontweight() if t_obj is not None else None
                saved_col = t_obj.get_color() if t_obj is not None else None
                st_kw = {"loc": _loc, "pad": title_pad}
                if saved_fs is not None:
                    st_kw["fontsize"] = saved_fs
                if saved_fw is not None:
                    st_kw["fontweight"] = saved_fw
                if saved_col is not None:
                    st_kw["color"] = saved_col
                ax.set_title(existing_t, **st_kw)

    if show_leg:
        legend_loc = str(kwargs.get("legend_loc", "lower left"))
        default_anchor = (0.0, 1.005 if show_weight_header else 1.01)
        legend_anchor = kwargs.get("legend_bbox_to_anchor", default_anchor)
        ax.legend(
            handles=legend_handles,
            loc=legend_loc,
            bbox_to_anchor=legend_anchor,
            ncol=max(1, legend_ncol),
            frameon=False,
            fontsize=8.8,
            columnspacing=1.2,
            handletextpad=0.45,
            borderaxespad=0.0,
        )

    return {
        "patches": patches,
        "annotations": anns,
        "x_edges": x_edges,
        "width_shares": w_shares.tolist(),
        "ax": ax,
    }


def plot_waterfall(
    ax: object,
    step_labels: Sequence[str],
    deltas: Sequence[float],
    is_total_flags: Optional[Sequence[bool]] = None,
    pos_color: Optional[str] = None,
    neg_color: Optional[str] = None,
    total_color: str = "#334155",
    connector_color: str = "#94A3B8",
    connector_linestyle: str = "--",
    bar_width: float = 0.56,
    value_fmt: str = "{:+.1f}",
    total_fmt: str = "{:.1f}",
    **kwargs,
) -> Dict[str, object]:
    """
    Data 2, 3 & 7 Bridge Waterfall Chart with floating positive/negative bars and horizontal dashed step connectors.
    """
    _ensure_cjk_font()
    import numpy as np

    n = min(len(step_labels), len(deltas))
    if n == 0:
        return {"bars": None, "connectors": [], "annotations": [], "ax": ax}

    c_pos = pos_color if pos_color is not None else GEPHI_QUALITATIVE_HEX[0]
    c_neg = neg_color if neg_color is not None else GEPHI_QUALITATIVE_HEX[1]

    clean_labels = [str(step_labels[i]) for i in range(n)]
    clean_vals = [float(deltas[i]) for i in range(n)]

    if is_total_flags is not None:
        totals_mask = [bool(f) for f in is_total_flags[:n]]
    else:
        totals_mask = [False] * n
        totals_mask[0] = True
        if n >= 3 and abs(sum(clean_vals[:-1]) - clean_vals[-1]) <= max(1e-4, abs(clean_vals[-1]) * 1e-3):
            totals_mask[-1] = True
        elif any(any(k in clean_labels[-1].lower() for k in ("期末", "總計", "合計", "total", "net")) for _ in (0,)):
            totals_mask[-1] = True

    bottoms: List[float] = []
    heights: List[float] = []
    end_levels: List[float] = []
    bar_colors: List[str] = []

    running = 0.0
    for i, (val, is_tot) in enumerate(zip(clean_vals, totals_mask)):
        if is_tot:
            # If user passed 0 or match for final total, use running sum if val == 0 and i > 0
            eff_tot = running if (i > 0 and abs(val) < 1e-12) else val
            bottoms.append(0.0)
            heights.append(eff_tot)
            running = eff_tot
            end_levels.append(running)
            bar_colors.append(total_color)
        else:
            bottoms.append(running)
            heights.append(val)
            running += val
            end_levels.append(running)
            bar_colors.append(c_pos if val >= 0 else c_neg)

    x_pos = np.arange(n)
    bars = ax.bar(
        x_pos,
        heights,
        bottom=bottoms,
        width=bar_width,
        color=bar_colors,
        edgecolor="#FFFFFF",
        linewidth=1.3,
        zorder=3,
    )

    connectors = []
    for i in range(n - 1):
        y_conn = end_levels[i]
        ln = ax.plot(
            [x_pos[i] + bar_width * 0.5, x_pos[i + 1] - bar_width * 0.5],
            [y_conn, y_conn],
            color=connector_color,
            linestyle=connector_linestyle,
            linewidth=1.2,
            zorder=2,
        )[0]
        connectors.append(ln)

    ax.axhline(0.0, color="#CBD5E1", linewidth=1.0, zorder=1)

    all_y = [0.0] + bottoms + end_levels
    y_min, y_max = min(all_y), max(all_y)
    y_span = max(1e-6, y_max - y_min)
    ax.set_ylim(y_min - y_span * 0.14 if y_min < 0 else 0.0, y_max + y_span * 0.16)

    anns = []
    for i, (x_i, bot, h_val, end_v, is_tot) in enumerate(zip(x_pos, bottoms, heights, end_levels, totals_mask)):
        if is_tot:
            txt = total_fmt.format(h_val)
            y_anchor = max(0.0, h_val)
            va_align = "bottom"
            dy = 5.0
        else:
            txt = value_fmt.format(h_val)
            if h_val >= 0:
                y_anchor = bot + h_val
                va_align = "bottom"
                dy = 5.0
            else:
                y_anchor = bot + h_val
                va_align = "top"
                dy = -5.0
        ann = ax.annotate(
            txt,
            xy=(float(x_i), y_anchor),
            xytext=(0.0, dy),
            textcoords="offset points",
            ha="center",
            va=va_align,
            fontsize=9.5,
            fontweight="bold",
            color="#0F172A" if is_tot else bar_colors[i],
            zorder=5,
        )
        anns.append(ann)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(clean_labels, fontsize=10.0, fontweight="bold", color="#0F172A")
    despine_axes(ax, grid_axis="y", grid_alpha=0.45)

    return {
        "bars": bars,
        "connectors": connectors,
        "annotations": anns,
        "end_levels": end_levels,
        "ax": ax,
    }


# -------------------------------------------------------------------------
# (c) RE:LAB 6-Channel Bespoke Metaphor & Thematic Palette Helpers (Data 7 Mode)
# -------------------------------------------------------------------------

def _build_tapered_cup_path(
    x_center: float,
    y_bottom: float,
    y_top: float,
    w_bottom: float,
    w_top: float,
    corner_r_x: float = 0.06,
    corner_r_y_ratio: float = 0.06,
):
    """Build a smooth Matplotlib Path for a tapered glass tumbler with a rounded bottom."""
    from matplotlib.path import Path

    h = max(1e-6, y_top - y_bottom)
    ry = h * corner_r_y_ratio
    rx = min(corner_r_x, w_bottom * 0.35)

    x_tl = x_center - 0.5 * w_top
    x_tr = x_center + 0.5 * w_top
    x_bl = x_center - 0.5 * w_bottom
    x_br = x_center + 0.5 * w_bottom

    verts = [
        (x_tl, y_top),
        (x_bl, y_bottom + ry),
        (x_bl, y_bottom),
        (x_bl + rx, y_bottom),
        (x_br - rx, y_bottom),
        (x_br, y_bottom),
        (x_br, y_bottom + ry),
        (x_tr, y_top),
        (x_tl, y_top),
    ]
    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.CURVE3,
        Path.CURVE3,
        Path.LINETO,
        Path.CURVE3,
        Path.CURVE3,
        Path.LINETO,
        Path.CLOSEPOLY,
    ]
    return Path(verts, codes)


def plot_liquid_container_bars(
    ax: object,
    labels: Sequence[str],
    values: Sequence[float],
    max_capacity: Optional[float] = None,
    container_style: str = "glass_cup",
    liquid_color: str = "#FFFFFF",
    canvas_bg: str = "#5BC0EB",
    glass_edge_color: str = "#E2F1F8",
    value_fmt: str = "{:.0f} ml",
    subtitle_values: Optional[Sequence[str]] = None,
    **kwargs,
) -> Dict[str, object]:
    """
    Data 7 RE:LAB NT$100 Milk Purchasing Power High-Gloss Container Chart:
    - Renders multi-layered vector glass cups (or battery/test-tube containers) with rim thickness,
      heavy curved glass base cushion, left/right specular reflection strips, and an exact `clip_path`
      liquid fill + 3D meniscus surface ellipse.
    """
    _ensure_cjk_font()
    from matplotlib.patches import Ellipse, FancyBboxPatch, PathPatch, Polygon, Rectangle

    clean_pairs = [
        (str(lbl), float(val))
        for lbl, val in zip(labels, values)
        if _parse_numeric_or_na(val) is not None
    ]
    n = len(clean_pairs)
    if n == 0:
        return {"containers": [], "liquids": [], "highlights": [], "annotations": [], "ax": ax}

    c_labels = [p[0] for p in clean_pairs]
    c_vals = [p[1] for p in clean_pairs]
    v_max = max(c_vals)
    cap = float(max_capacity) if (max_capacity is not None and float(max_capacity) >= v_max) else (v_max * 1.12)
    cap = max(cap, 1.0)

    set_fig_bg = bool(kwargs.pop("set_fig_bg", True))
    ax.set_facecolor(canvas_bg)
    if set_fig_bg and hasattr(ax, "figure") and ax.figure is not None:
        ax.figure.patch.set_facecolor(canvas_bg)

    bg_lum = relative_luminance(canvas_bg)
    primary_ink = str(kwargs.pop("text_color", "#FFFFFF" if bg_lum < 0.42 else "#0F172A"))
    secondary_ink = str(kwargs.pop("subtitle_color", "#E0F2FE" if primary_ink == "#FFFFFF" else "#334155"))

    containers = []
    liquids = []
    highlights = []
    anns = []

    style_key = str(container_style or "glass_cup").strip().lower()
    w_top = float(kwargs.pop("cup_top_width", 0.62))
    w_bot = float(kwargs.pop("cup_bottom_width", 0.46 if style_key == "glass_cup" else 0.58))
    wall_dx = 0.038
    base_thick = cap * 0.055

    for idx, (lbl, val) in enumerate(zip(c_labels, c_vals)):
        xc = float(idx)
        fill_h = max(0.0, min(cap, val))

        # 1. Outer Glass Silhouette + Heavy Glass Base Cushion
        outer_path = _build_tapered_cup_path(
            xc,
            y_bottom=-base_thick,
            y_top=cap * 1.02,
            w_bottom=w_bot + 2.0 * wall_dx,
            w_top=w_top + 2.0 * wall_dx,
        )
        outer_patch = PathPatch(
            outer_path,
            facecolor="#FFFFFF",
            alpha=0.22,
            edgecolor=glass_edge_color,
            linewidth=2.0,
            zorder=2,
        )
        ax.add_patch(outer_patch)
        containers.append(outer_patch)

        # Heavy bottom glass base refraction cushion
        base_path = _build_tapered_cup_path(
            xc,
            y_bottom=-base_thick,
            y_top=0.0,
            w_bottom=w_bot + 1.6 * wall_dx,
            w_top=w_bot + 1.8 * wall_dx,
            corner_r_y_ratio=0.35,
        )
        base_patch = PathPatch(
            base_path,
            facecolor="#FFFFFF",
            alpha=0.36,
            edgecolor="none",
            zorder=2.5,
        )
        ax.add_patch(base_patch)

        # 2. Inner Cavity Clip Path & Exact Liquid Level Fill
        inner_path = _build_tapered_cup_path(
            xc,
            y_bottom=0.0,
            y_top=cap,
            w_bottom=w_bot,
            w_top=w_top,
            corner_r_y_ratio=0.04,
        )
        inner_clip_patch = PathPatch(
            inner_path,
            facecolor="#FFFFFF",
            alpha=0.08,
            edgecolor="#FFFFFF",
            linewidth=0.8,
            zorder=3,
        )
        ax.add_patch(inner_clip_patch)

        if fill_h > 0:
            liq_rect = Rectangle(
                (xc - 0.6 * w_top, -base_thick * 0.2),
                1.2 * w_top,
                fill_h + base_thick * 0.2,
                facecolor=liquid_color,
                alpha=0.95,
                edgecolor="none",
                zorder=3.5,
            )
            ax.add_patch(liq_rect)
            liq_rect.set_clip_path(inner_clip_patch)
            liquids.append(liq_rect)

            # 3D liquid meniscus ellipse at height fill_h
            ratio_h = fill_h / cap
            w_at_fill = w_bot + ratio_h * (w_top - w_bot)
            meniscus = Ellipse(
                (xc, fill_h),
                width=w_at_fill * 0.98,
                height=cap * 0.032,
                facecolor=liquid_color,
                edgecolor="#E2E8F0",
                linewidth=1.1,
                alpha=0.98,
                zorder=4,
            )
            ax.add_patch(meniscus)
            liquids.append(meniscus)

        # 3. High-Gloss Vertical Glass Specular Reflection Strips & Top Rim
        # Left primary reflection band (tapered matching the cup wall)
        y_r0, y_r1 = cap * 0.06, cap * 0.94
        w_at_r0 = w_bot + 0.06 * (w_top - w_bot)
        w_at_r1 = w_bot + 0.94 * (w_top - w_bot)
        left_strip = Polygon(
            [
                (xc - 0.41 * w_at_r0, y_r0),
                (xc - 0.31 * w_at_r0, y_r0),
                (xc - 0.31 * w_at_r1, y_r1),
                (xc - 0.41 * w_at_r1, y_r1),
            ],
            closed=True,
            facecolor="#FFFFFF",
            alpha=0.38,
            edgecolor="none",
            zorder=5,
        )
        ax.add_patch(left_strip)
        highlights.append(left_strip)

        # Right subtle rim reflection strip
        right_strip = Polygon(
            [
                (xc + 0.33 * w_at_r0, cap * 0.10),
                (xc + 0.39 * w_at_r0, cap * 0.10),
                (xc + 0.39 * w_at_r1, cap * 0.90),
                (xc + 0.33 * w_at_r1, cap * 0.90),
            ],
            closed=True,
            facecolor="#FFFFFF",
            alpha=0.22,
            edgecolor="none",
            zorder=5,
        )
        ax.add_patch(right_strip)
        highlights.append(right_strip)

        # Top glass rim ellipse ring
        top_rim = Ellipse(
            (xc, cap * 1.02),
            width=w_top + 2.0 * wall_dx,
            height=cap * 0.038,
            facecolor="none",
            edgecolor=glass_edge_color,
            linewidth=1.8,
            alpha=0.88,
            zorder=6,
        )
        ax.add_patch(top_rim)
        highlights.append(top_rim)

        if style_key == "battery":
            term = FancyBboxPatch(
                (xc - 0.12 * w_top, cap * 1.02),
                0.24 * w_top,
                cap * 0.045,
                boxstyle="round,pad=0.01",
                facecolor=glass_edge_color,
                edgecolor="none",
                zorder=6,
            )
            ax.add_patch(term)

        # 4. Direct Value Label & Country/Category Footer Label
        val_str = value_fmt(val) if callable(value_fmt) else value_fmt.format(val)
        has_sub = bool(subtitle_values and idx < len(subtitle_values) and subtitle_values[idx])
        val_y = cap * 1.135 if has_sub else cap * 1.075
        t_val = ax.text(
            xc,
            val_y,
            val_str,
            ha="center",
            va="bottom",
            fontsize=13.5,
            fontweight="bold",
            color=primary_ink,
            zorder=7,
        )
        anns.append(t_val)

        if has_sub:
            t_sub = ax.text(
                xc,
                cap * 1.062,
                str(subtitle_values[idx]),
                ha="center",
                va="bottom",
                fontsize=9.5,
                fontweight="bold",
                color=secondary_ink,
                zorder=7,
            )
            anns.append(t_sub)

        t_lbl = ax.text(
            xc,
            -base_thick - cap * 0.06,
            lbl,
            ha="center",
            va="top",
            fontsize=12.5,
            fontweight="bold",
            color=primary_ink,
            zorder=7,
        )
        anns.append(t_lbl)

    ax.set_xlim(-0.70, (n - 1) + 0.70)
    ax.set_ylim(-base_thick - cap * 0.22, cap * 1.28)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right", "bottom", "left"):
        if side in ax.spines:
            ax.spines[side].set_visible(False)

    return {
        "containers": containers,
        "liquids": liquids,
        "highlights": highlights,
        "annotations": anns,
        "max_capacity": cap,
        "ax": ax,
    }


def _generate_procedural_pineapple_texture(size: int = 512):
    """
    Generate a rich, high-resolution procedural organic pineapple cross-section texture (`size x size x 4` RGBA uint8)
    used when `texture_img_path` is not provided or as a fallback.
    """
    import numpy as np

    yy, xx = np.mgrid[-1.0:1.0:complex(0, size), -1.0:1.0:complex(0, size)]
    rr = np.sqrt(xx ** 2 + yy ** 2)
    theta = np.arctan2(yy, xx)

    rgba = np.zeros((size, size, 4), dtype=np.uint8)
    inside = rr <= 1.0

    # Base golden yellow flesh gradient
    radial_wave = 0.5 + 0.5 * np.cos(16.0 * theta)
    fibrous_ripples = 0.5 + 0.5 * np.sin(38.0 * rr - 16.0 * theta)

    r_ch = np.clip(248.0 - 22.0 * rr + 10.0 * radial_wave, 0, 255)
    g_ch = np.clip(208.0 - 38.0 * (rr ** 1.4) + 14.0 * radial_wave + 8.0 * fibrous_ripples, 0, 255)
    b_ch = np.clip(46.0 + 25.0 * (1.0 - rr) + 12.0 * fibrous_ripples, 0, 255)

    # Central lighter core (r < 0.23)
    core_mask = rr < 0.23
    r_ch = np.where(core_mask, 254.0, r_ch)
    g_ch = np.where(core_mask, 240.0 - 25.0 * (rr / 0.23), g_ch)
    b_ch = np.where(core_mask, 138.0 - 30.0 * (rr / 0.23), b_ch)

    # Radial carpel septum lines (16 segments between r=0.23 and r=0.88)
    septum = (rr >= 0.23) & (rr <= 0.88) & (np.abs(np.sin(8.0 * theta)) < 0.045)
    r_ch = np.where(septum, r_ch * 0.90, r_ch)
    g_ch = np.where(septum, g_ch * 0.84, g_ch)
    b_ch = np.where(septum, b_ch * 0.70, b_ch)

    # Ring of 16 seed pockets around r = 0.74
    for k in range(16):
        ang = (2.0 * math.pi * k) / 16.0 + (math.pi / 16.0)
        sx, sy = 0.74 * math.cos(ang), 0.74 * math.sin(ang)
        d_seed = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2)
        seed_dot = d_seed < 0.042
        r_ch = np.where(seed_dot, 180.0, r_ch)
        g_ch = np.where(seed_dot, 83.0, g_ch)
        b_ch = np.where(seed_dot, 9.0, b_ch)

    # Scalloped golden-brown rind outer ring (0.90 <= r <= 1.05, clipped by vector Wedge r=1.0)
    rind_boundary = 0.905 + 0.022 * np.cos(24.0 * theta)
    rind_mask = rr >= rind_boundary
    r_ch = np.where(rind_mask, 194.0, r_ch)
    g_ch = np.where(rind_mask, 106.0, g_ch)
    b_ch = np.where(rind_mask, 18.0, b_ch)

    rgba[..., 0] = r_ch.astype(np.uint8)
    rgba[..., 1] = g_ch.astype(np.uint8)
    rgba[..., 2] = b_ch.astype(np.uint8)
    rgba[..., 3] = 255
    return rgba


def plot_masked_texture_wedge(
    ax: object,
    pct_value: float,
    texture_img_path: Optional[str] = None,
    title: str = "",
    subtitle: str = "",
    base_disc_color: str = "#E2E8F0",
    wedge_edge_color: str = "#FFFFFF",
    start_angle: float = 90.0,
    clockwise: bool = True,
    value_fmt: Optional[str] = None,
    **kwargs,
) -> Dict[str, object]:
    """
    Data 7 RE:LAB Pineapple Export Wedge / Small-Multiples Texture Mask Chart:
    - Draws a muted 100% full reference disc (`base_disc_color`).
    - Loads a text-free texture image (from `image-generator` or procedural pineapple cross-section fallback)
      and clips it with a mathematically exact `matplotlib.patches.Wedge` of angle `360 * pct`.
    """
    _ensure_cjk_font()
    import os
    from matplotlib.patches import Circle, Wedge
    import numpy as np

    raw_v = float(pct_value)
    p_norm = (raw_v / 100.0) if raw_v > 1.0 else raw_v
    p_clamped = max(0.0, min(1.0, p_norm))
    pct_display = p_clamped * 100.0

    img_arr = None
    if texture_img_path and os.path.exists(str(texture_img_path)):
        try:
            from PIL import Image
            pil_img = Image.open(str(texture_img_path)).convert("RGBA")
            w, h = pil_img.size
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            pil_sq = pil_img.crop((left, top, left + side, top + side)).resize((512, 512))
            img_arr = np.asarray(pil_sq)
        except Exception:
            img_arr = None

    if img_arr is None:
        img_arr = _generate_procedural_pineapple_texture(size=512)

    base_disc = Circle(
        (0.0, 0.0),
        radius=1.0,
        facecolor=base_disc_color,
        edgecolor="#CBD5E1",
        linewidth=1.4,
        zorder=1,
    )
    ax.add_patch(base_disc)

    angle_span = 360.0 * p_clamped
    if p_clamped >= 0.9999:
        theta1, theta2 = 0.0, 360.0
    elif clockwise:
        theta1 = float(start_angle) - angle_span
        theta2 = float(start_angle)
    else:
        theta1 = float(start_angle)
        theta2 = float(start_angle) + angle_span

    im = ax.imshow(
        img_arr,
        extent=[-1.0, 1.0, -1.0, 1.0],
        origin="upper",
        zorder=2,
    )

    wedge_patch = Wedge(
        (0.0, 0.0),
        r=1.0,
        theta1=theta1,
        theta2=theta2,
        facecolor="none",
        edgecolor=wedge_edge_color,
        linewidth=2.4,
        zorder=3,
    )
    ax.add_patch(wedge_patch)
    im.set_clip_path(wedge_patch)

    # Redraw wedge border on top so slice boundary is razor sharp
    border_wedge = Wedge(
        (0.0, 0.0),
        r=1.0,
        theta1=theta1,
        theta2=theta2,
        facecolor="none",
        edgecolor=wedge_edge_color,
        linewidth=2.2,
        zorder=4,
    )
    ax.add_patch(border_wedge)

    val_text = value_fmt.format(pct_display) if value_fmt else f"{pct_display:.1f}%"
    badge_color = kwargs.pop("badge_color", "#B45309")
    t_pct = ax.text(
        0.0,
        -1.18,
        val_text,
        ha="center",
        va="top",
        fontsize=15.0,
        fontweight="bold",
        color=badge_color,
        zorder=5,
    )

    t_title = None
    if title:
        t_title = ax.text(
            0.0,
            1.14,
            str(title),
            ha="center",
            va="bottom",
            fontsize=12.5,
            fontweight="bold",
            color="#0F172A",
            zorder=5,
        )

    t_sub = None
    if subtitle:
        t_sub = ax.text(
            0.0,
            -1.38,
            str(subtitle),
            ha="center",
            va="top",
            fontsize=9.5,
            color="#475569",
            zorder=5,
        )

    ax.set_xlim(-1.22, 1.22)
    ax.set_ylim(-1.52 if subtitle else -1.35, 1.32 if title else 1.15)
    ax.set_aspect("equal")
    ax.axis("off")

    return {
        "image": im,
        "wedge": wedge_patch,
        "border_wedge": border_wedge,
        "base_disc": base_disc,
        "pct_text": t_pct,
        "title_text": t_title,
        "subtitle_text": t_sub,
        "ax": ax,
    }


def _generate_procedural_coffee_bean_sprite(size: int = 128):
    """Generate a crisp 128x128 RGBA roasted coffee bean icon with 3D shading and central S-crease."""
    import numpy as np

    yy, xx = np.mgrid[-1.0:1.0:complex(0, size), -1.0:1.0:complex(0, size)]
    # Tilted oval bean (rotated by 28 degrees)
    ang = math.radians(28.0)
    xr = xx * math.cos(ang) + yy * math.sin(ang)
    yr = -xx * math.sin(ang) + yy * math.cos(ang)

    ellipse_d = (xr / 0.62) ** 2 + (yr / 0.84) ** 2
    bean_mask = ellipse_d <= 1.0

    # S-curve central crease along yr
    crease_center_x = 0.09 * np.sin(2.6 * yr)
    crease_dist = np.abs(xr - crease_center_x)
    crease_mask = (crease_dist < 0.055) & (ellipse_d <= 0.88)

    # 3D Lambertian highlight on upper-left
    light = np.clip(1.0 - 0.55 * ((xr + 0.22) ** 2 + (yr + 0.25) ** 2), 0.35, 1.08)

    rgba = np.zeros((size, size, 4), dtype=np.uint8)
    r_ch = np.where(crease_mask, 42.0, np.clip(122.0 * light, 35, 168))
    g_ch = np.where(crease_mask, 22.0, np.clip(74.0 * light, 18, 108))
    b_ch = np.where(crease_mask, 12.0, np.clip(38.0 * light, 10, 62))

    # Crisp rim outline
    rim_mask = (ellipse_d > 0.86) & bean_mask
    r_ch = np.where(rim_mask, 58.0, r_ch)
    g_ch = np.where(rim_mask, 32.0, g_ch)
    b_ch = np.where(rim_mask, 16.0, b_ch)

    rgba[..., 0] = r_ch.astype(np.uint8)
    rgba[..., 1] = g_ch.astype(np.uint8)
    rgba[..., 2] = b_ch.astype(np.uint8)
    rgba[..., 3] = np.where(bean_mask, 255, 0).astype(np.uint8)
    return rgba


def plot_sprite_scatter(
    ax: object,
    x_vals: Sequence[float],
    y_vals: Sequence[float],
    sprite_img_path: Optional[str] = None,
    labels: Optional[Sequence[str]] = None,
    zoom: float = 0.18,
    auto_remove_white_bg: bool = True,
    white_threshold: int = 242,
    **kwargs,
) -> Dict[str, object]:
    """
    Data 7 RE:LAB Coffee Bean Sprite Scatter Plot:
    - Loads a sprite icon (or procedural roasted coffee bean fallback), automatically strips solid white
      backgrounds via PIL when `auto_remove_white_bg=True`, and anchors sprites at exact `(x, y)` coordinates
      using `OffsetImage` & `AnnotationBbox` with leader-line callouts.
    """
    _ensure_cjk_font()
    import os
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage
    import numpy as np

    pts = []
    for idx, (xv, yv) in enumerate(zip(x_vals, y_vals)):
        px, py = _parse_numeric_or_na(xv), _parse_numeric_or_na(yv)
        if px is not None and py is not None:
            lbl = str(labels[idx]) if (labels is not None and idx < len(labels) and labels[idx] is not None) else ""
            pts.append((float(px), float(py), lbl))

    if not pts:
        return {"artists": [], "annotations": [], "ax": ax}

    sprite_rgba = None
    if sprite_img_path and os.path.exists(str(sprite_img_path)):
        try:
            from PIL import Image
            pil_img = Image.open(str(sprite_img_path)).convert("RGBA")
            arr = np.asarray(pil_img).copy()
            if auto_remove_white_bg:
                white_mask = (
                    (arr[..., 0] >= white_threshold)
                    & (arr[..., 1] >= white_threshold)
                    & (arr[..., 2] >= white_threshold)
                )
                arr[white_mask, 3] = 0
            sprite_rgba = arr
        except Exception:
            sprite_rgba = None

    if sprite_rgba is None:
        sprite_rgba = _generate_procedural_coffee_bean_sprite(size=128)

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.scatter(xs, ys, s=10, alpha=0.0, zorder=1)

    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_span = max(1e-6, x_max - x_min)
    y_span = max(1e-6, y_max - y_min)
    ax.set_xlim(x_min - x_span * 0.12, x_max + x_span * 0.16)
    ax.set_ylim(y_min - y_span * 0.14, y_max + y_span * 0.16)

    artists = []
    anns = []
    offsets_cycle = [(14, 14), (14, -16), (-14, 14), (-14, -16), (18, 0), (-18, 0)]

    for idx, (px, py, lbl) in enumerate(pts):
        oi = OffsetImage(sprite_rgba, zoom=float(zoom))
        ab = AnnotationBbox(oi, (px, py), frameon=False, zorder=4)
        ax.add_artist(ab)
        artists.append(ab)

        if lbl:
            dx, dy = offsets_cycle[idx % len(offsets_cycle)]
            ha_align = "left" if dx >= 0 else "right"
            ann = ax.annotate(
                lbl,
                xy=(px, py),
                xytext=(float(dx), float(dy)),
                textcoords="offset points",
                ha=ha_align,
                va="center",
                fontsize=9.2,
                fontweight="bold",
                color="#0F172A",
                arrowprops=dict(arrowstyle="-", color="#64748B", lw=1.0, shrinkA=0, shrinkB=6),
                zorder=5,
            )
            anns.append(ann)

    despine_axes(ax, grid_axis="both", grid_alpha=0.45)
    return {"artists": artists, "annotations": anns, "ax": ax}


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






