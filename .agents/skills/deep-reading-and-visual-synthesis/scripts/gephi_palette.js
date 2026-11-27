/**
 * gephi_palette.js
 * Chart & Data Dashboard Color Engine (Format D <-> Format E SSOT).
 * Grounded in CIELAB / HCL perceptual spacing, Brewer (1994), and Zeileis et al. (2020).
 *
 * Provides:
 * - PALETTE: 4 qualitative colors, 4 zero-alpha light badge tints, four 5-node sequential scales, 9-node diverging scale.
 * - labInterpolate(hexList, t): True CIELAB piecewise linear interpolation (zero alpha channel abuse).
 * - getSequentialColor(val, min, max, scale, discreteSteps): Proper (v - min) / (max - min) normalization.
 * - getDivergingColor(val, center, maxSpan, discreteSteps): Symmetric 9-node diverging mapping around center (#F5F6F7).
 * - bindQualitativeColors(categories, allowTop4Aggregation, otherLabel): Global category color + zero-alpha badge tint binding.
 * - getCategoryBadgeTint(catOrKey, badgeTintMap): Returns the zero-alpha 0.00 badge tint (or #F1F5F9 fallback).
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
      '#3B82F6', // 1. Primary: Royal Blue
      '#0D9488', // 2. Secondary: Teal
      '#F59E0B', // 3. Tertiary: Warm Amber
      '#6366F1'  // 4. Quaternary: Indigo
    ],
    badgeTints: [
      '#F1F5FE', // 1. Primary 0.00 light tint
      '#ECF6F5', // 2. Secondary 0.00 light tint
      '#FEF6E9', // 3. Tertiary 0.00 light tint
      '#F3F2FE'  // 4. Quaternary 0.00 light tint
    ],
    other: '#CBD5E1',           // 4+1 長尾聚合「其他項目」典雅淺灰
    na: '#D9D9D9',              // 缺失值（NA / Null）預設標記色
    divergingCenter: '#F5F6F7', // 發散中心（極低彩度中性冷灰）

    seqOrange: ['#F1F5FE', '#A4C2FB', '#3B82F6', '#234F97', '#0D244C'],
    seqBlue:   ['#ECF6F5', '#94CBC5', '#0D9488', '#075951', '#022D28'],
    seqPink:   ['#FEF6E9', '#FAD08C', '#F59E0B', '#9A6105', '#4D2E00'],
    seqGreen:  ['#F3F2FE', '#B3B2FA', '#6366F1', '#3B3D96', '#1B1C4E'],

    divergingHex: [
      '#022D28', // 0.000 (-100% negative extreme)
      '#075951', // 0.125 (-75%)
      '#0D9488', // 0.250 (-50%)
      '#94CBC5', // 0.375 (-25%)
      '#F5F6F7', // 0.500 (0% neutral center)
      '#A4C2FB', // 0.625 (+25%)
      '#3B82F6', // 0.750 (+50%)
      '#234F97', // 0.875 (+75%)
      '#0D244C'  // 1.000 (+100% positive extreme)
    ],
    entityColors: {},
    entityAliases: {}
  };

  const SCALE_ALIASES = {};
  const BADGE_TINT_LOOKUP = {};

  function normalizeHex(hexCode) {
    let clean = String(hexCode || '').trim().replace(/^#/, '');
    if (clean.length === 3) {
      clean = clean[0] + clean[0] + clean[1] + clean[1] + clean[2] + clean[2];
    }
    if (clean.length !== 6 || !/^[0-9A-Fa-f]{6}$/.test(clean)) {
      throw new Error(`Invalid hex color: '${hexCode}'`);
    }
    return `#${clean.toUpperCase()}`;
  }

  function rebuildLookups() {
    SCALE_ALIASES.orange = PALETTE.seqOrange;
    SCALE_ALIASES.primary = PALETTE.seqOrange;
    SCALE_ALIASES.primary_orange = PALETTE.seqOrange;
    SCALE_ALIASES['1'] = PALETTE.seqOrange;
    SCALE_ALIASES.blue = PALETTE.seqBlue;
    SCALE_ALIASES.secondary = PALETTE.seqBlue;
    SCALE_ALIASES.secondary_blue = PALETTE.seqBlue;
    SCALE_ALIASES['2'] = PALETTE.seqBlue;
    SCALE_ALIASES.pink = PALETTE.seqPink;
    SCALE_ALIASES.tertiary = PALETTE.seqPink;
    SCALE_ALIASES.tertiary_pink = PALETTE.seqPink;
    SCALE_ALIASES['3'] = PALETTE.seqPink;
    SCALE_ALIASES.green = PALETTE.seqGreen;
    SCALE_ALIASES.quaternary = PALETTE.seqGreen;
    SCALE_ALIASES.quaternary_green = PALETTE.seqGreen;
    SCALE_ALIASES['4'] = PALETTE.seqGreen;

    Object.keys(BADGE_TINT_LOOKUP).forEach(k => {
      delete BADGE_TINT_LOOKUP[k];
    });
    const tints = PALETTE.badgeTints || [];
    const cats = PALETTE.categories || [];
    if (tints.length >= 4) {
      BADGE_TINT_LOOKUP['0'] = tints[0];
      BADGE_TINT_LOOKUP['1'] = tints[1];
      BADGE_TINT_LOOKUP['2'] = tints[2];
      BADGE_TINT_LOOKUP['3'] = tints[3];
      BADGE_TINT_LOOKUP.orange = tints[0];
      BADGE_TINT_LOOKUP.primary = tints[0];
      BADGE_TINT_LOOKUP.primary_orange = tints[0];
      BADGE_TINT_LOOKUP.blue = tints[1];
      BADGE_TINT_LOOKUP.secondary = tints[1];
      BADGE_TINT_LOOKUP.secondary_blue = tints[1];
      BADGE_TINT_LOOKUP.pink = tints[2];
      BADGE_TINT_LOOKUP.tertiary = tints[2];
      BADGE_TINT_LOOKUP.tertiary_pink = tints[2];
      BADGE_TINT_LOOKUP.green = tints[3];
      BADGE_TINT_LOOKUP.quaternary = tints[3];
      BADGE_TINT_LOOKUP.quaternary_green = tints[3];
      for (let i = 0; i < 4; i++) {
        if (cats[i]) {
          BADGE_TINT_LOOKUP[String(cats[i]).toUpperCase()] = tints[i];
        }
      }
    }
  }

  rebuildLookups();

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

  const KNOWN_NA_TOKENS = new Set([
    'na', 'n/a', 'null', 'none', 'nan', '',
    '-', '—', '--', '－', '...', '…', '＊', '*', '?', '？',
    '無資料', '缺漏', '未公布'
  ]);

  const RESERVED_OTHER_TOKENS = new Set([
    '其他', '其它', '未分類', '其他項', '其他類', '其他項目',
    '其他項目合計', '其餘明細項目合計', '其餘明細與原表其他項合計',
    'other', 'others', 'unclassified'
  ]);

  function parseNumericOrNa(val) {
    if (val === null || val === undefined || typeof val === 'boolean') return null;
    if (typeof val === 'string') {
      const s = val.trim();
      if (!s || KNOWN_NA_TOKENS.has(s.toLowerCase()) || KNOWN_NA_TOKENS.has(s)) {
        return null;
      }
      const num = Number(s.replace(/,/g, ''));
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

  function normalizeEntityKey(name) {
    if (name === null || name === undefined) return '';
    let s = String(name).normalize('NFKC').trim();
    s = s.replace(/[A-Za-z]+/g, m => m.toLowerCase());
    const aliases = (PALETTE && PALETTE.entityAliases) || {};
    const seen = new Set();
    while (Object.prototype.hasOwnProperty.call(aliases, s) && !seen.has(s)) {
      seen.add(s);
      s = aliases[s];
    }
    return s;
  }

  function getEntityColor(name, fallback = null) {
    if (name === null || name === undefined) return PALETTE.na;
    const raw = String(name).trim();
    const rawLower = raw.toLowerCase();
    if (!raw || KNOWN_NA_TOKENS.has(rawLower) || KNOWN_NA_TOKENS.has(raw)) {
      return PALETTE.na;
    }
    if (RESERVED_OTHER_TOKENS.has(raw) || RESERVED_OTHER_TOKENS.has(rawLower)) {
      return PALETTE.other;
    }
    const key = normalizeEntityKey(raw);
    const entityColors = (PALETTE && PALETTE.entityColors) || {};
    if (Object.prototype.hasOwnProperty.call(entityColors, key)) {
      return entityColors[key];
    }
    if (Object.prototype.hasOwnProperty.call(entityColors, raw)) {
      return entityColors[raw];
    }
    return fallback;
  }

  function bindQualitativeColors(categories, allowTop4Aggregation = false, otherLabel = '其他項目合計') {
    const colorMap = {};
    const badgeTintMap = {};
    const top4Categories = [];
    const otherCategories = [];
    const unregisteredUnique = [];
    const unregisteredSeen = new Set();

    const catHexNorm = PALETTE.categories.map(c => normalizeHex(c));
    const entityColors = (PALETTE && PALETTE.entityColors) || {};
    const usedEntityHexes = new Set(
      Object.values(entityColors).map(c => {
        try { return normalizeHex(c); } catch (_) { return String(c).toUpperCase(); }
      })
    );

    const freeSlots = [];
    PALETTE.categories.forEach((hex, idx) => {
      if (!usedEntityHexes.has(catHexNorm[idx])) {
        freeSlots.push({
          hex,
          tint: (PALETTE.badgeTints && PALETTE.badgeTints[idx]) || '#F1F5F9'
        });
      }
    });

    (categories || []).forEach(rawCat => {
      if (rawCat === null || rawCat === undefined) {
        colorMap['NA'] = PALETTE.na;
        badgeTintMap['NA'] = '#F1F5F9';
        return;
      }
      const cat = String(rawCat).trim();
      const catLower = cat.toLowerCase();
      if (KNOWN_NA_TOKENS.has(catLower) || KNOWN_NA_TOKENS.has(cat)) {
        const key = cat || 'NA';
        colorMap[key] = PALETTE.na;
        badgeTintMap[key] = '#F1F5F9';
        return;
      }
      if (cat === otherLabel || RESERVED_OTHER_TOKENS.has(cat) || RESERVED_OTHER_TOKENS.has(catLower)) {
        colorMap[cat] = PALETTE.other;
        badgeTintMap[cat] = '#F1F5F9';
        if (cat !== otherLabel && !otherCategories.includes(cat)) {
          otherCategories.push(cat);
        }
        return;
      }
      const registeredHex = getEntityColor(cat, null);
      if (registeredHex !== null) {
        colorMap[cat] = registeredHex;
        const normReg = normalizeHex(registeredHex);
        const slotIdx = catHexNorm.indexOf(normReg);
        badgeTintMap[cat] = slotIdx >= 0
          ? ((PALETTE.badgeTints && PALETTE.badgeTints[slotIdx]) || '#F1F5F9')
          : (BADGE_TINT_LOOKUP[normReg] || '#F1F5F9');
        if (!top4Categories.includes(cat)) {
          top4Categories.push(cat);
        }
        return;
      }
      if (!unregisteredSeen.has(cat)) {
        unregisteredSeen.add(cat);
        unregisteredUnique.push(cat);
      }
    });

    if (unregisteredUnique.length > freeSlots.length && !allowTop4Aggregation) {
      throw new Error(
        `Unique category count exceeds the 4 locked qualitative colors (${unregisteredUnique.length} new vs ${freeSlots.length} free slot(s)). ` +
        `Either confirm expansion mode or enable Smart 4+1 aggregation (allowTop4Aggregation=true).`
      );
    }

    unregisteredUnique.forEach((cat, idx) => {
      if (idx < freeSlots.length) {
        colorMap[cat] = freeSlots[idx].hex;
        badgeTintMap[cat] = freeSlots[idx].tint;
        top4Categories.push(cat);
      } else {
        colorMap[cat] = PALETTE.other;
        badgeTintMap[cat] = '#F1F5F9';
        if (!otherCategories.includes(cat)) {
          otherCategories.push(cat);
        }
      }
    });

    if (allowTop4Aggregation) {
      colorMap[otherLabel] = PALETTE.other;
      badgeTintMap[otherLabel] = '#F1F5F9';
    }

    return {
      colorMap,
      badgeTintMap,
      top4Categories: top4Categories.slice(0, 4),
      otherCategories
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

  function buildPaletteFromPrimaryHexes(hexList) {
    const rawList = (hexList || []).map(h => String(h || '').trim()).filter(Boolean);
    if (rawList.length < 2 || rawList.length > 4) {
      throw new Error(`buildPaletteFromPrimaryHexes requires 2 to 4 hex colors; got ${rawList.length}`);
    }
    const cleaned = rawList.map(h => normalizeHex(h));
    const qual4 = cleaned.slice();
    if (qual4.length === 2) {
      const [, a1, b1] = hexToLab(qual4[0]);
      const [, a2, b2] = hexToLab(qual4[1]);
      qual4.push(labToHex(72.0, -b1 * 0.85, a1 * 0.85));
      qual4.push(labToHex(72.0, -b2 * 0.85, a2 * 0.85));
    } else if (qual4.length === 3) {
      const [, a1, b1] = hexToLab(qual4[0]);
      qual4.push(labToHex(72.0, -a1 * 0.75, -b1 * 0.75));
    }

    const scaleKeys = ['seqOrange', 'seqBlue', 'seqPink', 'seqGreen'];
    const badgeTints = [];
    const seqs = {};

    qual4.slice(0, 4).forEach((baseHex, idx) => {
      const [lb, ab, bb] = hexToLab(baseHex);
      const node00 = labToHex(96.5, ab * 0.14, bb * 0.14);
      const node25 = labInterpolate([node00, baseHex], 0.50);
      const node50 = baseHex;
      const node100 = labToHex(Math.max(26.0, Math.min(36.0, lb * 0.46)), ab * 1.12, bb * 1.12);
      const node75 = labInterpolate([baseHex, node100], 0.50);
      seqs[scaleKeys[idx]] = [node00, node25, node50, node75, node100];
      badgeTints.push(node00);
    });

    const negExtreme = seqs.seqBlue[4];
    const negMid = seqs.seqBlue[2];
    const centerNeutral = '#F5F6F7';
    const posMid = seqs.seqOrange[2];
    const posExtreme = seqs.seqOrange[4];

    const divergingHex = [
      negExtreme,
      labInterpolate([negExtreme, negMid], 0.50),
      negMid,
      labInterpolate([negMid, centerNeutral], 0.55),
      centerNeutral,
      labInterpolate([centerNeutral, posMid], 0.45),
      posMid,
      labInterpolate([posMid, posExtreme], 0.50),
      posExtreme
    ];

    return {
      categories: qual4.slice(0, 4),
      badgeTints,
      other: '#CBD5E1',
      na: '#D9D9D9',
      divergingCenter: centerNeutral,
      seqOrange: seqs.seqOrange,
      seqBlue: seqs.seqBlue,
      seqPink: seqs.seqPink,
      seqGreen: seqs.seqGreen,
      divergingHex,
      qualitative_4: qual4.slice(0, 4),
      light_badge_tints_4: badgeTints,
      sequential_scales: {
        orange: seqs.seqOrange,
        blue: seqs.seqBlue,
        pink: seqs.seqPink,
        green: seqs.seqGreen
      },
      diverging_9: divergingHex,
      discrete_neutrals: {
        diverging_center: centerNeutral,
        na_missing: '#D9D9D9',
        other_aggregated: '#CBD5E1',
        context_baseline_gray: '#CBD5E1'
      }
    };
  }

  function setActivePalette(customPalette) {
    if (!customPalette || typeof customPalette !== 'object') return PALETTE;
    const cats = customPalette.categories || customPalette.qualitative_4;
    if (Array.isArray(cats) && cats.length === 4) {
      PALETTE.categories = cats.map(c => normalizeHex(c));
    }
    const tints = customPalette.badgeTints || customPalette.light_badge_tints_4;
    if (Array.isArray(tints) && tints.length === 4) {
      PALETTE.badgeTints = tints.map(c => normalizeHex(c));
    }
    const pySeqs = customPalette.sequential_scales || {};
    const seqMapping = {
      seqOrange: customPalette.seqOrange || pySeqs.orange,
      seqBlue: customPalette.seqBlue || pySeqs.blue,
      seqPink: customPalette.seqPink || pySeqs.pink,
      seqGreen: customPalette.seqGreen || pySeqs.green
    };
    Object.keys(seqMapping).forEach(k => {
      if (Array.isArray(seqMapping[k]) && seqMapping[k].length > 0) {
        PALETTE[k] = seqMapping[k].slice();
      }
    });
    const div9 = customPalette.divergingHex || customPalette.diverging_9;
    if (Array.isArray(div9) && div9.length > 0) {
      PALETTE.divergingHex = div9.slice();
    }
    if (customPalette.entityColors && typeof customPalette.entityColors === 'object') {
      PALETTE.entityColors = { ...customPalette.entityColors };
    }
    if (customPalette.entityAliases && typeof customPalette.entityAliases === 'object') {
      PALETTE.entityAliases = { ...customPalette.entityAliases };
    }
    rebuildLookups();
    return PALETTE;
  }

  const THEMATIC_PRESETS = {
    milk_tea: ['#C87D55', '#5C8D89', '#D9A05B', '#8C5A3C'],
    bubble_tea: ['#C87D55', '#5C8D89', '#D9A05B', '#8C5A3C'],
    forest_eco: ['#3A7D44', '#2C6E8F', '#C98A3E', '#6B8E23'],
    matcha_forest: ['#3A7D44', '#2C6E8F', '#C98A3E', '#6B8E23'],
    ocean_blue: ['#0284C7', '#0D9488', '#E07A5F', '#4F46E5'],
    ocean_hydro: ['#0284C7', '#0D9488', '#E07A5F', '#4F46E5'],
    coffee_roast: ['#7F4F24', '#4A7C59', '#C68B59', '#9C6644'],
    pineapple_tropical: ['#D97706', '#15803D', '#0284C7', '#B45309'],
    agri_gold: ['#D97706', '#15803D', '#0284C7', '#B45309']
  };

  function expandSingleHexToFour(hexCode) {
    const baseHex = normalizeHex(hexCode);
    const [l, a, b] = hexToLab(baseHex);
    const targetL = Math.max(52.0, Math.min(72.0, l));
    const c2 = labToHex(targetL, -b * 0.88, a * 0.88);
    const c3 = labToHex(targetL, b * 0.82, -a * 0.82);
    const c4 = labToHex(targetL, -a * 0.78, -b * 0.78);
    return [baseHex, c2, c3, c4];
  }

  function deriveThematicPalette(themePresetOrHex, options = {}) {
    let hexList = null;
    if (Array.isArray(themePresetOrHex)) {
      const cleaned = themePresetOrHex.map(h => String(h || '').trim()).filter(Boolean);
      hexList = cleaned.length === 1 ? expandSingleHexToFour(cleaned[0]) : cleaned;
    } else if (typeof themePresetOrHex === 'string') {
      const key = themePresetOrHex.trim().toLowerCase().replace(/[\s-]+/g, '_');
      if (THEMATIC_PRESETS[key]) {
        hexList = THEMATIC_PRESETS[key].slice();
      } else {
        hexList = expandSingleHexToFour(themePresetOrHex.trim());
      }
    } else {
      throw new Error('deriveThematicPalette expects a preset name, a hex string, or an array of hex strings.');
    }
    const built = buildPaletteFromPrimaryHexes(hexList);
    if (options && options.activate) {
      setActivePalette(built);
    }
    return built;
  }

  return {
    PALETTE,
    THEMATIC_PRESETS,
    hexToRgb,
    hexToLab,
    labToHex,
    labInterpolate,
    getSequentialColor,
    getDivergingColor,
    getEntityColor,
    bindQualitativeColors,
    getCategoryBadgeTint,
    buildPaletteFromPrimaryHexes,
    deriveThematicPalette,
    setActivePalette
  };
});
