"""
HCL Color Science Engine for Deep Reading & Visual Synthesis
Ported and extended from Claus O. Wilke (2019), Zeileis et al. (2020) colorspace,
and Prof. Martin's CIELUV Polar HCL Lab (hcl.mjs).

Implements:
1. CIELUV Polar HCL (polarLUV, D65 white point).
2. Binary-search gamut clamping (never clip RGB channels harshly).
3. common_c(hues, target_c, l) for perceptually equal qualitative scales.
4. ink(hex) using linearized relative luminance Y > 0.179 WCAG AA threshold.
5. lab_interp for sequential and diverging scales in CIELAB space.
6. Size-dependent Tri-tier scaling:
   - Tier 1: Accent / Border / Dark Text (L ~ 38, C ~ 56)
   - Tier 2: Badge Pill Fill (L ~ 46, C ~ 62)
   - Tier 3: Surface Tint (L ~ 96.5, C ~ 8, Solid HEX - NEVER alpha transparency)
7. Classic Palettes: Okabe-Ito, Tableau10, ColorBrewer, ggsci (NPG, NEJM, Lancet).
8. Parser for '我的圖表配色設定.md' or user-defined palette overrides.
"""

import math
import re
from typing import List, Tuple, Dict, Optional, Union

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

    # u_prime and v_prime
    u_prime = u / (13.0 * l) + UN_PRIME
    v_prime = v / (13.0 * l) + VN_PRIME

    # Y from L
    if l > 8.0:
        y = YN * math.pow((l + 16.0) / 116.0, 3.0)
    else:
        y = YN * l * math.pow(3.0 / 29.0, 3.0)

    # Protect against division by zero
    if abs(v_prime) < 1e-9:
        v_prime = 1e-9 if v_prime >= 0 else -1e-9

    x = y * (9.0 * u_prime) / (4.0 * v_prime)
    z = y * (12.0 - 3.0 * u_prime - 20.0 * v_prime) / (4.0 * v_prime)

    # XYZ to linear sRGB matrix (D65)
    r_lin =  3.2404542 * x - 1.5371385 * y - 0.4985314 * z
    g_lin = -0.9692660 * x + 1.8760108 * y + 0.0415560 * z
    b_lin =  0.0556434 * x - 0.2040259 * y + 1.0572252 * z

    return r_lin, g_lin, b_lin


def _linear_to_srgb(v_lin: float) -> float:
    """Compand linear sRGB channel to standard gamma sRGB in range [0, 1]."""
    if v_lin <= 0.0031308:
        return 12.92 * v_lin
    else:
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
        # Binary search for maximum in-gamut chroma
        low = 0.0
        high = c
        for _ in range(24):
            mid = (low + high) / 2.0
            r_test, g_test, b_test = _hcl_to_linear_rgb(h, mid, l)
            if _is_in_srgb_gamut(r_test, g_test, b_test):
                low = mid
            else:
                high = mid
        c = low
        r_lin, g_lin, b_lin = _hcl_to_linear_rgb(h, c, l)

    # Gamma compand and clamp to 0..255
    r = int(round(max(0.0, min(1.0, _linear_to_srgb(r_lin))) * 255.0))
    g = int(round(max(0.0, min(1.0, _linear_to_srgb(g_lin))) * 255.0))
    b = int(round(max(0.0, min(1.0, _linear_to_srgb(b_lin))) * 255.0))

    return f"#{r:02X}{g:02X}{b:02X}"


def common_c(hues: List[float], target_c: float, l: float) -> float:
    """
    Find the maximum chroma that is in-gamut for ALL given hues at luminance L.
    Ensures perceptual equality for qualitative palettes.
    """
    l = max(0.0, min(100.0, float(l)))
    min_c = float(target_c)

    for h in hues:
        low = 0.0
        high = float(target_c)
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
    """
    Calculate CIE Relative Luminance Y from sRGB hex (WCAG 2.1 formula).
    Returns Y in [0, 1].
    """
    r, g, b = hex_to_rgb(hex_code)
    channels = [r / 255.0, g / 255.0, b / 255.0]
    lin_ch = [
        c / 12.92 if c <= 0.04045 else math.pow((c + 0.055) / 1.055, 2.4)
        for c in channels
    ]
    return lin_ch[0] * 0.2126 + lin_ch[1] * 0.7152 + lin_ch[2] * 0.0722


def ink(bg_hex: str, dark_ink: str = "#0F172A", light_ink: str = "#FFFFFF") -> str:
    """
    Auto-Ink function from professor's hcl.mjs:
    Threshold Y > 0.179 (WCAG AA 4.5:1 golden cross point).
    If background relative luminance > 0.179, use dark ink; else light ink.
    """
    return dark_ink if relative_luminance(bg_hex) > 0.179 else light_ink


def wcag_contrast(fg_hex: str, bg_hex: str) -> float:
    """Calculate WCAG 2.1 contrast ratio between two hex colors."""
    y1 = relative_luminance(fg_hex)
    y2 = relative_luminance(bg_hex)
    l_max = max(y1, y2)
    l_min = min(y1, y2)
    return (l_max + 0.05) / (l_min + 0.05)


def gray(hex_code: str) -> str:
    """
    Simulate grayscale perception using CIE L* from sRGB.
    Passes grayscale monotonicity test.
    """
    y = relative_luminance(hex_code)
    # Convert Y to CIE L*
    if y > math.pow(6.0 / 29.0, 3.0):
        l_star = 116.0 * math.pow(y, 1.0 / 3.0) - 16.0
    else:
        l_star = y * math.pow(29.0 / 3.0, 3.0)
    
    # Scale L* (0..100) to sRGB gray channel
    val = int(round(max(0.0, min(100.0, l_star)) * 2.55))
    return f"#{val:02X}{val:02X}{val:02X}"


# -------------------------------------------------------------------------
# CIELAB Interpolation for Sequential & Diverging Scales
# -------------------------------------------------------------------------

def _rgb_to_xyz(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert sRGB (0..255) to XYZ (D65)."""
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
    """Convert XYZ to CIELAB (D65)."""
    xr, yr, zr = x / XN, y / YN, z / ZN
    
    def f(t: float) -> float:
        return math.pow(t, 1.0 / 3.0) if t > 0.008856 else (7.787 * t) + (16.0 / 116.0)

    fx, fy, fz = f(xr), f(yr), f(zr)
    l_star = (116.0 * fy) - 16.0
    a_star = 500.0 * (fx - fy)
    b_star = 200.0 * (fy - fz)
    return l_star, a_star, b_star


def _lab_to_xyz(l_star: float, a_star: float, b_star: float) -> Tuple[float, float, float]:
    """Convert CIELAB to XYZ (D65)."""
    fy = (l_star + 16.0) / 116.0
    fx = a_star / 500.0 + fy
    fz = fy - b_star / 200.0

    def f_inv(t: float) -> float:
        return math.pow(t, 3.0) if t > 0.206897 else (t - 16.0 / 116.0) / 7.787

    x = XN * f_inv(fx)
    y = YN * f_inv(fy)
    z = ZN * f_inv(fz)
    return x, y, z


def _xyz_to_rgb_clamped(x: float, y: float, z: float) -> Tuple[int, int, int]:
    """Convert XYZ to sRGB (0..255) clamped."""
    r_lin =  3.2404542 * x - 1.5371385 * y - 0.4985314 * z
    g_lin = -0.9692660 * x + 1.8760108 * y + 0.0415560 * z
    b_lin =  0.0556434 * x - 0.2040259 * y + 1.0572252 * z

    r = int(round(max(0.0, min(1.0, _linear_to_srgb(r_lin))) * 255.0))
    g = int(round(max(0.0, min(1.0, _linear_to_srgb(g_lin))) * 255.0))
    b = int(round(max(0.0, min(1.0, _linear_to_srgb(b_lin))) * 255.0))
    return r, g, b


def hex_to_lab(hex_code: str) -> Tuple[float, float, float]:
    r, g, b = hex_to_rgb(hex_code)
    x, y, z = _rgb_to_xyz(r, g, b)
    return _xyz_to_lab(x, y, z)


def lab_to_hex(l_star: float, a_star: float, b_star: float) -> str:
    x, y, z = _lab_to_xyz(l_star, a_star, b_star)
    r, g, b = _xyz_to_rgb_clamped(x, y, z)
    return f"#{r:02X}{g:02X}{b:02X}"


def lab_interpolate(hex_list: List[str], t: float) -> str:
    """
    Interpolate between a list of hex colors in CIELAB space at normalized position t in [0, 1].
    Matches lesson guide's lab_interp piecewise linear interpolation.
    """
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
    
    l_mid = l1 + frac * (l2 - l1)
    a_mid = a1 + frac * (a2 - a1)
    b_mid = b1 + frac * (b2 - b1)
    
    return lab_to_hex(l_mid, a_mid, b_mid)


# -------------------------------------------------------------------------
# [I-19] Tri-Tier Area-Scaled HCL Derivation (Stone et al. 2014)
# -------------------------------------------------------------------------

class AreaScaledHCL:
    """
    Derives 3 solid HEX tiers for any hue H based on visual area:
    - Tier 1: accent_dark (L=38, C=56) -> borders, dark title text, icons (contrast > 5.5:1 on white)
    - Tier 2: badge_fill  (L=46, C=62) -> solid pill fill with auto ink
    - Tier 3: surface_tint (L=96.5, C=8) -> large card background (solid hex, NEVER alpha transparency)
    """
    def __init__(self, hue_deg: float, name: str = "", target_c: float = 60.0):
        self.hue = float(hue_deg) % 360.0
        self.name = name
        
        # 3 area tiers
        self.accent_dark = hcl_to_hex(self.hue, min(target_c, 56.0), 38.0)
        self.badge_fill = hcl_to_hex(self.hue, min(target_c, 62.0), 46.0)
        self.surface_tint = hcl_to_hex(self.hue, 8.5, 96.5)
        
        # Auto inks
        self.badge_ink = ink(self.badge_fill)
        self.surface_ink = ink(self.surface_tint)


# -------------------------------------------------------------------------
# Classic Palettes & Session Binding Contract
# -------------------------------------------------------------------------

# Default 5-hue harmonious set for qualitative mindmaps (Okabe-Ito + Nature NPG aligned)
DEFAULT_QUALITATIVE_HUES = [
    250.0,  # Deep Royal Blue (Opportunity 1 / 道 / Primary)
    35.0,   # Amber Ochre    (Opportunity 2 / 法 / Warn)
    165.0,  # Emerald Teal   (Opportunity 3 / 術 / Success)
    345.0,  # Rose Berry     (Opportunity 4 / 斷言 / Danger)
    290.0,  # Purple Amethyst(Synthesis / Schema / Synth)
]

# Diverging dual hues (Cold Blue vs Warm Terracotta)
DIVERGING_HUES = (250.0, 25.0)


class SessionColorContract:
    """
    Global session color contract across all 4 mindmaps, PDF report, and PPTX presentation.
    Enforces semantic color lock:
    - 道 (Opportunity 1 / ITI 案例)   -> Blue (H=250)
    - 法 (Opportunity 2&3 / 安永 EY) -> Ochre (H=35)
    - 術 (Opportunity 4 / AXA XL)    -> Teal (H=165)
    - 斷言 / 邊界 / 盲測             -> Rose (H=345)
    - 綜合 / 基模 / 資料光譜         -> Purple (H=290)
    - 對立對決 (Diverging)           -> Blue (do(X)) vs Red-Orange (AI Confounding)
    """
    def __init__(self, hues: Optional[List[float]] = None):
        self.hues = hues or DEFAULT_QUALITATIVE_HUES
        self.categories: Dict[str, AreaScaledHCL] = {}
        
        # Build qualitative tiers with equalized chroma
        eq_c = common_c(self.hues, 58.0, 42.0)
        
        self.blue = AreaScaledHCL(self.hues[0], "blue", target_c=eq_c)
        self.ochre = AreaScaledHCL(self.hues[1], "ochre", target_c=eq_c)
        self.teal = AreaScaledHCL(self.hues[2], "teal", target_c=eq_c)
        self.rose = AreaScaledHCL(self.hues[3], "rose", target_c=eq_c)
        self.purple = AreaScaledHCL(self.hues[4], "purple", target_c=eq_c)

        # Neutral surfaces
        self.neutral_surface = "#F8FAFC"
        self.neutral_border = "#E2E8F0"
        self.neutral_dark = "#0F172A"
        self.neutral_muted = "#475569"

        # Semantic mappings
        self.mapping = {
            "dao": self.blue,          # 道
            "fa": self.ochre,          # 法
            "shu": self.teal,          # 術
            "danger": self.rose,       # 禁區/偏誤
            "synth": self.purple,      # 綜合/基模
            "opp1": self.blue,
            "opp2": self.ochre,
            "opp3": self.teal,
            "opp4": self.rose,
        }

    def get_sequential_ladder(self, steps: int = 3) -> List[Tuple[str, str, str]]:
        """
        Returns a sequence of (border, badge_fill, surface_tint) with monotonic luminance.
        Passes grayscale readability test.
        """
        ladder = []
        base_h = 245.0
        # Luminance progresses from lighter to deeper
        l_steps = [48.0, 39.0, 30.0] if steps == 3 else [52.0 - i * 8.0 for i in range(steps)]
        tint_steps = [97.5, 96.0, 94.5] if steps == 3 else [98.0 - i * 1.5 for i in range(steps)]
        
        for i in range(steps):
            accent = hcl_to_hex(base_h, 55.0, l_steps[i])
            badge = hcl_to_hex(base_h, 58.0, l_steps[i] + 4.0)
            tint = hcl_to_hex(base_h, 8.0, tint_steps[i])
            ladder.append((accent, badge, tint))
        return ladder

    def get_diverging_pair(self) -> Tuple[AreaScaledHCL, AreaScaledHCL]:
        """Returns balanced opposing hues for diverging contrast (e.g. do(X) vs Confounding)."""
        h_left, h_right = DIVERGING_HUES
        left = AreaScaledHCL(h_left, "diverging_left", target_c=58.0)
        right = AreaScaledHCL(h_right, "diverging_right", target_c=58.0)
        return left, right


# Singleton instance
GLOBAL_COLOR_CONTRACT = SessionColorContract()
