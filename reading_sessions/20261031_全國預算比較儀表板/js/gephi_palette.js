/**
 * gephi_palette.js
 * Locked Chart & Data Dashboard Color Engine (Format D <-> Format E SSOT).
 * Grounded in ggsci Gephi · pastel (CIELAB / HCL L*≈72 balanced), Brewer (1994), and Zeileis et al. (2020).
 *
 * Provides:
 * - PALETTE: Locked 4 qualitative colors, 4 zero-alpha light badge tints, four 5-node sequential scales, 9-node diverging scale.
 * - labInterpolate(hexList, t): True CIELAB piecewise linear interpolation (zero alpha channel abuse).
 * - getSequentialColor(val, min, max, scale, discreteSteps): Proper (v - min) / (max - min) normalization.
 * - getDivergingColor(val, center, maxSpan, discreteSteps): Symmetric 9-node diverging mapping around center (#F5F6F7).
 * - bindQualitativeColors(categories, allowTop4Aggregation, otherLabel): Global category color + zero-alpha badge tint binding.
 * - getCategoryBadgeTint(catOrKey, badgeTintMap): Returns #FFF3EA / #EBF7F9 / #FFF0F5 / #F1F7EE (or #F1F5F9).
 */

(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.GephiPalette = factory();
  }
})(typeof globalThis !== 'undefined' ? globalThis : typeof window !== 'undefined' ? window : this, function () {
  'use strict';

  const XN = 0.95047;
  const YN = 1.00000;
  const ZN = 1.08883;

  const PALETTE = {
    categories: [
      '#ECA072', // 1. 主色：暖杏蜜橘 (Warm Apricot Orange)
      '#5DBACD', // 2. 次色：霧靄青藍 (Misty Cyan-Blue)
      '#E89BB6', // 3. 第三色：落櫻粉黛 (Sakura Rose Pink)
      '#8FBA88'  // 4. 第四色：鼠尾草綠 (Sage Green)
    ],
    badgeTints: [
      '#FFF3EA', // 1. 主色暖杏橘系 0.00 極淺底色 (零 Alpha 表格/UI 徽章底色)
      '#EBF7F9', // 2. 次色霧靄藍系 0.00 極淺底色
      '#FFF0F5', // 3. 第三色落櫻粉系 0.00 極淺底色
      '#F1F7EE'  // 4. 第四色鼠尾草綠系 0.00 極淺底色
    ],
    other: '#CBD5E1',           // 4+1 長尾聚合「其他項目」典雅淺灰
    na: '#D9D9D9',              // 缺失值（NA / Null）預設標記色
    divergingCenter: '#F5F6F7', // 發散中心（極低彩度中性冷灰）

    seqOrange: ['#FFF3EA', '#FBD8C0', '#ECA072', '#CA6F35', '#97481B'],
    seqBlue:   ['#EBF7F9', '#BCE2EB', '#5DBACD', '#2C8B9F', '#0E5B6B'],
    seqPink:   ['#FFF0F5', '#F9CEE0', '#E89BB6', '#C46487', '#8D3658'],
    seqGreen:  ['#F1F7EE', '#D0E5CC', '#8FBA88', '#5E8F56', '#396032'],

    divergingHex: [
      '#0E5B6B', // 0.000 (-100% 偏差極端：負向極值深墨青)
      '#257F92', // 0.125 (-75% 偏差：負向中深)
      '#5DBACD', // 0.250 (-50% 偏差：負向中度)
      '#B2DFE9', // 0.375 (-25% 偏差：負向輕度)
      '#F5F6F7', // 0.500 (0% 偏差：中立基準中心)
      '#FBD9C2', // 0.625 (+25% 偏差：正向輕度)
      '#ECA072', // 0.750 (+50% 偏差：正向中度)
      '#B4693A', // 0.875 (+75% 偏差：正向中深)
      '#884725'  // 1.000 (+100% 偏差極端：正向極值深栗橘)
    ]
  };

  const SCALE_ALIASES = {
    orange: PALETTE.seqOrange,
    primary: PALETTE.seqOrange,
    primary_orange: PALETTE.seqOrange,
    '1': PALETTE.seqOrange,
    blue: PALETTE.seqBlue,
    secondary: PALETTE.seqBlue,
    secondary_blue: PALETTE.seqBlue,
    '2': PALETTE.seqBlue,
    pink: PALETTE.seqPink,
    tertiary: PALETTE.seqPink,
    tertiary_pink: PALETTE.seqPink,
    '3': PALETTE.seqPink,
    green: PALETTE.seqGreen,
    quaternary: PALETTE.seqGreen,
    quaternary_green: PALETTE.seqGreen,
    '4': PALETTE.seqGreen
  };

  const BADGE_TINT_LOOKUP = {
    '0': '#FFF3EA',
    '1': '#EBF7F9',
    '2': '#FFF0F5',
    '3': '#F1F7EE',
    orange: '#FFF3EA',
    blue: '#EBF7F9',
    pink: '#FFF0F5',
    green: '#F1F7EE',
    '#ECA072': '#FFF3EA',
    '#5DBACD': '#EBF7F9',
    '#E89BB6': '#FFF0F5',
    '#8FBA88': '#F1F7EE'
  };

  function hexToRgb(hexCode) {
    let clean = String(hexCode || '').trim().replace(/^#/, '');
    if (clean.length === 3) {
      clean = clean[0] + clean[0] + clean[1] + clean[1] + clean[2] + clean[2];
    }
    if (clean.length !== 6) return [0, 0, 0];
    return [
      parseInt(clean.slice(0, 2), 16) || 0,
      parseInt(clean.slice(2, 4), 16) || 0,
      parseInt(clean.slice(4, 6), 16) || 0
    ];
  }

  function linearToSrgb(vLin) {
    if (vLin <= 0.0031308) return 12.92 * vLin;
    return 1.055 * Math.pow(vLin, 1.0 / 2.4) - 0.055;
  }

  function hexToLab(hexCode) {
    const [r, g, b] = hexToRgb(hexCode);
    const lin = [r / 255.0, g / 255.0, b / 255.0].map(c =>
      c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
    );
    const x = lin[0] * 0.4124564 + lin[1] * 0.3575761 + lin[2] * 0.1804375;
    const y = lin[0] * 0.2126729 + lin[1] * 0.7151522 + lin[2] * 0.0721750;
    const z = lin[0] * 0.0193339 + lin[1] * 0.1191920 + lin[2] * 0.9503041;

    const f = t => (t > 0.008856 ? Math.pow(t, 1.0 / 3.0) : 7.787 * t + 16.0 / 116.0);
    const fx = f(x / XN);
    const fy = f(y / YN);
    const fz = f(z / ZN);
    return [116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz)];
  }

  function labToHex(lStar, aStar, bStar) {
    const fy = (lStar + 16.0) / 116.0;
    const fx = aStar / 500.0 + fy;
    const fz = fy - bStar / 200.0;
    const fInv = t => (t > 0.206897 ? Math.pow(t, 3.0) : (t - 16.0 / 116.0) / 7.787);

    const x = XN * fInv(fx);
    const y = YN * fInv(fy);
    const z = ZN * fInv(fz);

    const rLin =  3.2404542 * x - 1.5371385 * y - 0.4985314 * z;
    const gLin = -0.9692660 * x + 1.8760108 * y + 0.0415560 * z;
    const bLin =  0.0556434 * x - 0.2040259 * y + 1.0572252 * z;

    const toByte = v => Math.round(Math.max(0.0, Math.min(1.0, linearToSrgb(v))) * 255.0);
    const r = toByte(rLin).toString(16).padStart(2, '0').toUpperCase();
    const g = toByte(gLin).toString(16).padStart(2, '0').toUpperCase();
    const b = toByte(bLin).toString(16).padStart(2, '0').toUpperCase();
    return `#${r}${g}${b}`;
  }

  function labInterpolate(hexList, t) {
    if (!Array.isArray(hexList) || hexList.length === 0) return '#000000';
    if (hexList.length === 1) return hexList[0];
    const clampedT = Math.max(0.0, Math.min(1.0, Number(t) || 0.0));
    const n = hexList.length - 1;
    const scaledT = clampedT * n;
    const idx = Math.floor(scaledT);
    if (idx >= n) return hexList[n];
    const frac = scaledT - idx;
    const [l1, a1, b1] = hexToLab(hexList[idx]);
    const [l2, a2, b2] = hexToLab(hexList[idx + 1]);
    return labToHex(
      l1 + frac * (l2 - l1),
      a1 + frac * (a2 - a1),
      b1 + frac * (b2 - b1)
    );
  }

  function parseNumericOrNa(val) {
    if (val === null || val === undefined || typeof val === 'boolean') return null;
    if (typeof val === 'string') {
      const s = val.trim();
      if (!s || ['na', 'n/a', 'null', 'none', 'nan', '-', '—'].includes(s.toLowerCase())) {
        return null;
      }
      const num = Number(s);
      return Number.isFinite(num) ? num : null;
    }
    const num = Number(val);
    return Number.isFinite(num) ? num : null;
  }

  function getSequentialColor(val, min, max, scale = 'orange', discreteSteps = false) {
    const v = parseNumericOrNa(val);
    if (v === null) return PALETTE.na;
    const nodes = Array.isArray(scale)
      ? scale
      : SCALE_ALIASES[String(scale || 'orange').trim().toLowerCase()];
    if (!nodes) {
      throw new Error(`Unknown sequential scale '${scale}'. Allowed: orange, blue, pink, green.`);
    }
    const vMin = Number(min);
    const vMax = Number(max);
    if (!Number.isFinite(vMin) || !Number.isFinite(vMax) || vMax <= vMin) {
      return nodes[2];
    }
    const p = Math.max(0.0, Math.min(1.0, (v - vMin) / (vMax - vMin)));
    if (discreteSteps) {
      const idx = Math.max(0, Math.min(4, Math.round(p * 4.0)));
      return nodes[idx];
    }
    return labInterpolate(nodes, p);
  }

  function getDivergingColor(val, center = 0.0, maxSpan = 1.0, discreteSteps = false) {
    const v = parseNumericOrNa(val);
    if (v === null) return PALETTE.na;
    const c = Number(center) || 0.0;
    const span = maxSpan !== null && maxSpan !== undefined && Math.abs(Number(maxSpan)) > 0
      ? Math.abs(Number(maxSpan))
      : 1.0;
    const deviation = (v - c) / span;
    const clampedDev = Math.max(-1.0, Math.min(1.0, deviation));
    const p = 0.5 + 0.5 * clampedDev;
    if (discreteSteps) {
      const idx = Math.max(0, Math.min(8, Math.round(p * 8.0)));
      return PALETTE.divergingHex[idx];
    }
    return labInterpolate(PALETTE.divergingHex, p);
  }

  function bindQualitativeColors(categories, allowTop4Aggregation = false, otherLabel = '其他項目合計') {
    const colorMap = {};
    const badgeTintMap = {};
    const uniqueValid = [];
    const naTokens = new Set(['na', 'n/a', 'null', 'none', 'nan', '']);

    (categories || []).forEach(rawCat => {
      if (rawCat === null || rawCat === undefined) {
        colorMap['NA'] = PALETTE.na;
        badgeTintMap['NA'] = '#F1F5F9';
        return;
      }
      const cat = String(rawCat).trim();
      if (naTokens.has(cat.toLowerCase())) {
        const key = cat || 'NA';
        colorMap[key] = PALETTE.na;
        badgeTintMap[key] = '#F1F5F9';
        return;
      }
      if (cat === otherLabel) {
        colorMap[cat] = PALETTE.other;
        badgeTintMap[cat] = '#F1F5F9';
        return;
      }
      if (!uniqueValid.includes(cat)) {
        uniqueValid.push(cat);
      }
    });

    if (uniqueValid.length > 4 && !allowTop4Aggregation) {
      throw new Error(
        `Unique category count (${uniqueValid.length}) exceeds the 4 locked qualitative colors. ` +
        `Either confirm expansion mode or enable Smart 4+1 aggregation (allowTop4Aggregation=true).`
      );
    }

    uniqueValid.forEach((cat, idx) => {
      if (idx < 4) {
        colorMap[cat] = PALETTE.categories[idx];
        badgeTintMap[cat] = PALETTE.badgeTints[idx];
      } else {
        colorMap[cat] = PALETTE.other;
        badgeTintMap[cat] = '#F1F5F9';
      }
    });

    if (allowTop4Aggregation) {
      colorMap[otherLabel] = PALETTE.other;
      badgeTintMap[otherLabel] = '#F1F5F9';
    }

    return {
      colorMap,
      badgeTintMap,
      top4Categories: uniqueValid.slice(0, 4),
      otherCategories: uniqueValid.slice(4)
    };
  }

  function getCategoryBadgeTint(catOrKey, badgeTintMap) {
    if (typeof catOrKey === 'number') {
      return catOrKey >= 0 && catOrKey < 4 ? PALETTE.badgeTints[catOrKey] : '#F1F5F9';
    }
    const key = String(catOrKey || '').trim();
    if (badgeTintMap && badgeTintMap[key]) {
      return badgeTintMap[key];
    }
    return (
      BADGE_TINT_LOOKUP[key] ||
      BADGE_TINT_LOOKUP[key.toUpperCase()] ||
      BADGE_TINT_LOOKUP[key.toLowerCase()] ||
      '#F1F5F9'
    );
  }

  return {
    PALETTE,
    hexToRgb,
    hexToLab,
    labToHex,
    labInterpolate,
    getSequentialColor,
    getDivergingColor,
    bindQualitativeColors,
    getCategoryBadgeTint
  };
});
