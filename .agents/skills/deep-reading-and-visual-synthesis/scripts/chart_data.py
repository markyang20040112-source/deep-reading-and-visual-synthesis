"""
chart_data.py
Lightweight CSV ingestion, numeric/NA parsing, and 3-tier detail/other/subtotal splitting.
Note: `hcl_color_engine` is the public entry point.
"""

import math
from typing import Dict, List, Optional, Sequence, Tuple

from color_core import KNOWN_NA_STRINGS

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
