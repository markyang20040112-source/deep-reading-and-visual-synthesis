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
    Bind unordered categories to fixed qualitative colors in strict order (#ECA072, #5DBACD, #E89BB6, #8FBA88).
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
    "#FFF3EA",  # 1. 主色暖杏橘系 0.00 極淺底色
    "#EBF7F9",  # 2. 次色霧靄藍系 0.00 極淺底色
    "#FFF0F5",  # 3. 第三色落櫻粉系 0.00 極淺底色
    "#F1F7EE",  # 4. 第四色鼠尾草綠系 0.00 極淺底色
]

GEPHI_LIGHT_BADGE_TINTS_MAP: Dict[str, str] = {
    "0": "#FFF3EA",
    "1": "#EBF7F9",
    "2": "#FFF0F5",
    "3": "#F1F7EE",
    "orange": "#FFF3EA",
    "primary": "#FFF3EA",
    "primary_orange": "#FFF3EA",
    "#ECA072": "#FFF3EA",
    "blue": "#EBF7F9",
    "secondary": "#EBF7F9",
    "secondary_blue": "#EBF7F9",
    "#5DBACD": "#EBF7F9",
    "pink": "#FFF0F5",
    "tertiary": "#FFF0F5",
    "tertiary_pink": "#FFF0F5",
    "#E89BB6": "#FFF0F5",
    "green": "#F1F7EE",
    "quaternary": "#F1F7EE",
    "quaternary_green": "#F1F7EE",
    "#8FBA88": "#F1F7EE",
}


def get_category_badge_tint(
    cat_or_key: object,
    category_color_map: Optional[Dict[str, str]] = None,
) -> str:
    """
    Return the zero-alpha light badge surface tint (#FFF3EA, #EBF7F9, #FFF0F5, #F1F7EE)
    corresponding to the 0.00 node of the 4 locked sequential scales.
    Falls back to #F1F5F9 for aggregated 'other' or neutral items.
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


def export_gephi_palette_js(output_path: str) -> str:
    """
    Export the standalone pure-JS Gephi · pastel CIELAB color engine (`gephi_palette.js`)
    to `output_path` so Format E web dashboards share 100% identical color math with Python.
    """
    from pathlib import Path
    src_js = Path(__file__).resolve().parent / "gephi_palette.js"
    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    if src_js.exists():
        content = src_js.read_text(encoding="utf-8")
        out_file.write_text(content, encoding="utf-8")
    else:
        raise FileNotFoundError(f"Master gephi_palette.js not found at {src_js}")
    return str(out_file)


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





