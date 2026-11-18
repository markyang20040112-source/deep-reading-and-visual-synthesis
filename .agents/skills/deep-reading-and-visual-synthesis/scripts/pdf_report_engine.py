"""
pdf_report_engine.py
A4 Portrait Print CSS, Content-Adaptive Smart Pagination & Chromium PDF Compiler Engine for Format B (.md / .pdf).
Grounded in Paivio (1986) Dual-Coding Cadence, Sweller (2011) Cognitive Load, Tufte (2006) Ehrenberg Three-Line Tables,
W3C CSS Fragmentation Level 3, and W3C CLReq Traditional Chinese Layout Requirements.

Decoupling Rule:
- Format A panoramic knowledge diagrams are strictly decoupled and prohibited inside Format B PDFs.
- Lightweight visual diagrams embedded in Format B must be A4-portrait-native (189mm / 7.44").

Provides reusable building blocks:
- load_document_theme(doc_theme_id=None) -> Dict[str, str]
- build_report_css(theme="modern_sans", body_pt=10.9, doc_theme_id=None) -> str
- apply_content_adaptive_rules(body_html, short_table_max_rows=5) -> str
- wrap_report_html(title, body_html, theme="modern_sans", body_pt=10.9, extra_css="", doc_theme_id=None, adaptive_layout=True) -> str
- compile_html_to_pdf(html_content_or_path, output_pdf_path, cleanup_temp_html=True, wait_ms=400) -> str
- compile_adaptive_report_pdf(title, body_html, output_pdf_path, theme="modern_sans", body_pt=10.9, ..., genre=None, min_remaining_ratio=None) -> str | dict
"""

import html
from html.parser import HTMLParser
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union


GENRE_MIN_REMAINING_RATIOS: Dict[str, float] = {
    "memo": 0.34,
    "executive_memo": 0.34,
    "executive_strategy_memo": 0.34,
    "blueprint": 0.34,
    "methodological_blueprint": 0.34,
    "genre2": 0.34,
    "genre3": 0.34,
    "synthesis": 0.22,
    "comprehensive_synthesis": 0.22,
    "cards": 0.22,
    "knowledge_cards": 0.22,
    "atomic_knowledge_cards": 0.22,
    "genre1": 0.22,
    "genre4": 0.22,
}

VOID_HTML_TAGS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})


def resolve_min_remaining_ratio(
    genre: Optional[str] = None,
    min_remaining_ratio: Optional[float] = None,
) -> float:
    """Resolve genre-adaptive `<h2>` remaining-space threshold for smart pagination."""
    if min_remaining_ratio is not None:
        return max(0.05, min(0.80, float(min_remaining_ratio)))
    if genre:
        key = str(genre).strip().lower().replace("-", "_").replace(" ", "_")
        if key in GENRE_MIN_REMAINING_RATIOS:
            return GENRE_MIN_REMAINING_RATIOS[key]
    return 0.32


def load_document_theme(doc_theme_id: Optional[str] = None) -> Dict[str, str]:
    """Load the active document_theme from config/user_preferences.json (with safe defaults)."""
    default_theme = {
        "bg_canvas": "#FFFFFF",
        "bg_card": "#FFFFFF",
        "border_card": "#CBD5E1",
        "ink_primary": "#0F172A",
        "ink_secondary": "#1E293B",
        "ink_muted": "#475569",
        "primary_accent": "#0284C7",
        "primary_tint": "#E0F2FE",
        "warn_accent": "#D97706",
        "warn_tint": "#FEF3C7",
        "success_accent": "#0D9488",
        "success_tint": "#CCFBF1",
        "danger_accent": "#E11D48",
        "danger_tint": "#FFE4E6",
    }
    try:
        prefs_file = Path(__file__).resolve().parents[1] / "config" / "user_preferences.json"
        if prefs_file.exists():
            prefs = json.loads(prefs_file.read_text(encoding="utf-8"))
            color_sets = prefs.get("color_sets", {})
            themes = color_sets.get("document_themes", {})
            chosen_id = doc_theme_id or color_sets.get("active_document_theme_id") or "modern_academic_slate"
            if chosen_id in themes:
                merged = dict(default_theme)
                merged.update(themes[chosen_id])
                return merged
    except Exception:
        pass
    return default_theme


def build_report_css(
    theme: str = "modern_sans",
    body_pt: float = 10.9,
    doc_theme_id: Optional[str] = None,
) -> str:
    """
    Generate publication-grade A4 Portrait print CSS with:
    - 189mm expansive printable width (@page margin: 11mm 10.5mm 12mm 10.5mm)
    - Comfortable typography: Body 10.8pt-11.2pt (line-height 1.70), Tables/Cards 9.6pt-10.0pt, Captions 9.0pt
    - Typography theme support:
      * "modern_sans": Microsoft JhengHei / PingFang TC / Noto Sans CJK TC, clean unindented paragraphs
      * "clreq_kaiti": DFKai-SB (標楷體) + Times New Roman, with `p { text-indent: 2em; }` for narrative paragraphs
    - Layered Document Color Theme support (`doc_theme_id` from `config/user_preferences.json`)
    - Content-adaptive fragmentation rules:
      * `h2, h3, h4, caption { break-after: avoid; }`, `p { orphans: 3; widows: 3; }`
      * `thead { display: table-header-group; }`, `tr { break-inside: avoid; }`
      * `table.table-short { break-inside: avoid; }` vs `table.table-long { break-inside: auto; }`
      * `.callout { break-inside: avoid; }` + `.callout.keep-with-prev { break-before: avoid; }`
    """
    is_kaiti = str(theme).strip().lower() in {"clreq_kaiti", "kaiti", "dfkai", "academic_kaiti"}
    if is_kaiti:
        font_stack = '"DFKai-SB", "標楷體", "BiauKai", "Times New Roman", serif'
        p_indent_rule = "text-indent: 2em;"
    else:
        font_stack = '"Microsoft JhengHei", "PingFang TC", "Noto Sans CJK TC", -apple-system, sans-serif'
        p_indent_rule = "text-indent: 0;"

    dt = load_document_theme(doc_theme_id)
    primary_acc = dt.get("primary_accent", "#0284C7")
    primary_tint = dt.get("primary_tint", "#E0F2FE")
    ink_pri = dt.get("ink_primary", "#0F172A")
    ink_sec = dt.get("ink_secondary", "#1E293B")
    ink_muted = dt.get("ink_muted", "#475569")
    border_c = dt.get("border_card", "#CBD5E1")
    bg_card = dt.get("bg_card", "#FFFFFF")

    pt_val = max(10.0, min(11.6, float(body_pt)))

    return f"""
@page {{
  size: A4 portrait;
  margin: 11mm 10.5mm 12mm 10.5mm;
}}

* {{
  box-sizing: border-box;
  -webkit-print-color-adjust: exact !important;
  print-color-adjust: exact !important;
}}

html, body {{
  margin: 0;
  padding: 0;
  font-family: {font_stack};
  font-size: {pt_val}pt;
  line-height: 1.70;
  color: {ink_sec};
  background-color: #FFFFFF;
}}

h1 {{
  font-size: 21pt;
  font-weight: 800;
  color: {ink_pri};
  line-height: 1.3;
  margin: 0 0 8px 0;
}}

h2 {{
  font-size: 14.5pt;
  font-weight: 700;
  color: {ink_pri};
  border-bottom: 2px solid {primary_acc};
  padding-bottom: 4px;
  margin: 20px 0 10px 0;
  break-after: avoid;
  page-break-after: avoid;
}}

h2.first-chapter {{
  margin-top: 14px;
}}

h2.chapter-start, .page-break {{
  break-before: page;
  page-break-before: always;
  margin-top: 0;
}}

h3 {{
  font-size: 12pt;
  font-weight: 700;
  color: {ink_pri};
  margin: 14px 0 6px 0;
  break-after: avoid;
  page-break-after: avoid;
}}

h4 {{
  font-size: 11pt;
  font-weight: 700;
  color: {ink_pri};
  margin: 10px 0 5px 0;
  break-after: avoid;
  page-break-after: avoid;
}}

p {{
  margin: 0 0 8px 0;
  line-height: 1.70;
  text-align: justify;
  orphans: 3;
  widows: 3;
  {p_indent_rule}
}}

/* Unindented paragraphs inside structured containers */
td p, th p, .card p, .card-body p, .callout p, .equation-box p, figcaption, .no-indent {{
  text-indent: 0 !important;
}}

.nowrap {{
  white-space: nowrap;
}}

/* Border-Safe Flex / Grid Cards (Zero fixed height, zero overflow:hidden) */
.card-grid-2 {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin: 10px 0;
  align-items: stretch;
}}

.card-grid-3 {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 9px;
  margin: 10px 0;
  align-items: stretch;
}}

.card, .matrix-box, .callout, .equation-box, figure, tr, .light-tail-group, .keep-with-callout {{
  break-inside: avoid;
  page-break-inside: avoid;
}}

.callout.keep-with-prev, .keep-with-prev {{
  break-before: avoid;
  page-break-before: avoid;
}}

.card {{
  border: 1.5px solid {border_c};
  border-radius: 8px;
  background: {bg_card};
  display: flex;
  flex-direction: column;
}}

.card-header {{
  padding: 6px 10px;
  font-size: 10.5pt;
  font-weight: 700;
  color: {ink_pri};
  background: {primary_tint};
  border-bottom: 1px solid {border_c};
  border-radius: 6px 6px 0 0;
}}

.card-body {{
  padding: 8px 10px;
  font-size: 9.8pt;
  line-height: 1.54;
  color: {ink_sec};
}}

.badge {{
  display: inline-block;
  padding: 1px 7px;
  font-size: 9pt;
  font-weight: 700;
  border-radius: 999px;
  background: {primary_tint};
  color: {primary_acc};
  white-space: nowrap;
}}

/* Callout / Insight Box */
.callout {{
  margin: 8px 0 10px 0;
  padding: 8px 12px;
  background: {primary_tint};
  border-left: 4px solid {primary_acc};
  border-top: 1px solid {border_c};
  border-right: 1px solid {border_c};
  border-bottom: 1px solid {border_c};
  border-radius: 0 6px 6px 0;
  font-size: 9.8pt;
  line-height: 1.54;
  color: {ink_sec};
}}

.callout strong {{
  color: {primary_acc};
}}

/* Ehrenberg Three-Line Table (Content-Adaptive Short vs Long) */
table {{
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0 12px 0;
  font-size: 9.8pt;
  line-height: 1.52;
}}

table.table-short {{
  break-inside: avoid;
  page-break-inside: avoid;
}}

table.table-long {{
  break-inside: auto;
  page-break-inside: auto;
}}

caption {{
  break-after: avoid;
  page-break-after: avoid;
  margin-bottom: 5px;
  font-weight: 700;
  color: {ink_muted};
  font-size: 9.6pt;
  text-align: left;
}}

thead {{
  display: table-header-group;
}}

tfoot {{
  display: table-footer-group;
}}

thead tr {{
  border-top: 2px solid {ink_pri};
  border-bottom: 1.5px solid {ink_pri};
  background: #F8FAFC;
}}

tbody tr {{
  border-bottom: 1px solid #E2E8F0;
}}

tbody tr:last-child {{
  border-bottom: 2px solid {ink_pri};
}}

th, td {{
  padding: 6px 8px;
  text-align: left;
  vertical-align: top;
}}

th {{
  font-weight: 700;
  color: {ink_pri};
}}

/* Display Equation Box (Formula Sandwich) */
.equation-box {{
  margin: 10px 0;
  padding: 9px 14px;
  background: #F8FAFC;
  border-left: 4px solid {primary_acc};
  border-top: 1px solid #E2E8F0;
  border-right: 1px solid #E2E8F0;
  border-bottom: 1px solid #E2E8F0;
  border-radius: 0 6px 6px 0;
}}

.equation-formula {{
  text-align: center;
  font-weight: 700;
  font-size: 11pt;
  color: {ink_pri};
  margin-bottom: 5px;
}}

/* Figures (A4 Portrait Native Diagrams & Single-Panel Charts) */
figure {{
  margin: 10px 0 12px 0;
  text-align: center;
}}

figure img {{
  max-width: 100%;
  height: auto;
  border: 1px solid {border_c};
  border-radius: 6px;
}}

figcaption {{
  margin-top: 5px;
  font-size: 9.0pt;
  color: {ink_muted};
  line-height: 1.45;
  text-align: left;
}}
""".strip()


# ==============================================================================
# HTML STRUCTURE PARSER & CONTENT-ADAPTIVE FRAGMENTATION ENGINE
# ==============================================================================
class _SpanNode:
    __slots__ = ("tag", "attrs", "start_idx", "start_tag_end_idx", "end_idx", "children", "parent", "text_parts")

    def __init__(self, tag: str, attrs: List[Tuple[str, Optional[str]]], start_idx: int, start_tag_end_idx: int, parent=None):
        self.tag = tag.lower()
        self.attrs = attrs
        self.start_idx = start_idx
        self.start_tag_end_idx = start_tag_end_idx
        self.end_idx = start_tag_end_idx
        self.children: List["_SpanNode"] = []
        self.parent = parent
        self.text_parts: List[str] = []

    def class_list(self) -> List[str]:
        for k, v in self.attrs:
            if k.lower() == "class" and v:
                return v.split()
        return []

    def plain_text(self, html_src: str) -> str:
        raw_inner = html_src[self.start_tag_end_idx:self.end_idx] if self.end_idx > self.start_tag_end_idx else ""
        stripped = re.sub(r"<[^>]+>", " ", raw_inner)
        return re.sub(r"\s+", " ", html.unescape(stripped)).strip()


class _SpanHTMLTreeParser(HTMLParser):
    def __init__(self, html_src: str):
        super().__init__(convert_charrefs=False)
        self.html_src = html_src
        self.line_starts = [0]
        for idx, ch in enumerate(html_src):
            if ch == "\n":
                self.line_starts.append(idx + 1)
        self.root = _SpanNode("__root__", [], 0, 0, parent=None)
        self.root.end_idx = len(html_src)
        self.stack: List[_SpanNode] = [self.root]
        self.all_nodes: List[_SpanNode] = []

    def _to_index(self, pos: Tuple[int, int]) -> int:
        lineno, col = pos
        if lineno <= 0 or lineno > len(self.line_starts):
            return len(self.html_src)
        return self.line_starts[lineno - 1] + col

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        t_low = tag.lower()
        start_idx = self._to_index(self.getpos())
        raw_tag = self.get_starttag_text() or ""
        end_tag_idx = start_idx + len(raw_tag)
        parent = self.stack[-1]
        node = _SpanNode(t_low, attrs, start_idx, end_tag_idx, parent=parent)
        parent.children.append(node)
        self.all_nodes.append(node)
        if t_low not in VOID_HTML_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        t_low = tag.lower()
        start_idx = self._to_index(self.getpos())
        raw_tag = self.get_starttag_text() or ""
        end_tag_idx = start_idx + len(raw_tag)
        parent = self.stack[-1]
        node = _SpanNode(t_low, attrs, start_idx, end_tag_idx, parent=parent)
        node.end_idx = end_tag_idx
        parent.children.append(node)
        self.all_nodes.append(node)

    def handle_endtag(self, tag: str) -> None:
        t_low = tag.lower()
        if t_low in VOID_HTML_TAGS:
            return
        cur_pos = self._to_index(self.getpos())
        close_end = self.html_src.find(">", cur_pos)
        close_end = (close_end + 1) if close_end != -1 else cur_pos
        for idx in range(len(self.stack) - 1, 0, -1):
            if self.stack[idx].tag == t_low:
                while len(self.stack) - 1 >= idx:
                    popped = self.stack.pop()
                    popped.end_idx = close_end
                break


def _parse_html_tree(html_src: str) -> Tuple[_SpanNode, List[_SpanNode]]:
    parser = _SpanHTMLTreeParser(html_src)
    parser.feed(html_src)
    parser.close()
    return parser.root, parser.all_nodes


def _add_class_to_start_tag(start_tag_html: str, new_class: str) -> str:
    m = re.search(r"""\bclass\s*=\s*(["'])(.*?)\1""", start_tag_html, re.IGNORECASE | re.DOTALL)
    if m:
        existing = m.group(2).split()
        if new_class in existing:
            return start_tag_html
        updated = " ".join(existing + [new_class])
        quote = m.group(1)
        return start_tag_html[:m.start()] + f'class={quote}{updated}{quote}' + start_tag_html[m.end():]
    insert_at = start_tag_html.rfind("/>")
    if insert_at == -1:
        insert_at = start_tag_html.rfind(">")
    if insert_at == -1:
        return start_tag_html
    return start_tag_html[:insert_at] + f' class="{new_class}"' + start_tag_html[insert_at:]


def _count_table_body_rows(table_node: _SpanNode) -> int:
    """Count body `<tr>` rows belonging directly to `table_node` (excluding `<thead>` / `<tfoot>`)."""
    count = 0

    def walk(node: _SpanNode, section: Optional[str]) -> None:
        nonlocal count
        for ch in node.children:
            if ch.tag == "table":
                continue  # Ignore nested tables
            if ch.tag in ("thead", "tbody", "tfoot"):
                walk(ch, ch.tag)
            elif ch.tag == "tr":
                if section not in ("thead", "tfoot"):
                    count += 1
            else:
                walk(ch, section)

    walk(table_node, None)
    return count


def _is_lightweight_preceding_block(node: Optional[_SpanNode], html_src: str) -> bool:
    """
    Returns True only for lightweight blocks that can safely stay bound to a short closing callout
    without dragging a large figure or long table across a page break.
    """
    if node is None:
        return False
    classes = set(node.class_list())
    text_len = len(node.plain_text(html_src))

    if node.tag == "figure" or "keep-with-callout" in classes:
        return False
    if node.tag == "p":
        return text_len <= 240
    if "equation-box" in classes:
        return text_len <= 420
    if "card-grid-2" in classes or "card-grid-3" in classes:
        return text_len <= 650
    if node.tag == "table":
        return _count_table_body_rows(node) <= 3 and text_len <= 600
    return False


def apply_content_adaptive_rules(
    body_html: str,
    short_table_max_rows: int = 5,
) -> str:
    """
    Content-adaptive HTML post-processor for Format B:
    1. Classifies every `<table>` into `table-short` (<= `short_table_max_rows` body rows -> `break-inside: avoid`)
       vs. `table-long` (> `short_table_max_rows` body rows -> clean cross-page splits with repeating `<thead>`).
    2. Prevents short closing `.callout` blocks from becoming orphaned at the top of a new page by adding
       `keep-with-prev` ONLY when immediately preceded by a lightweight block (short `<p>`, `.equation-box`,
       compact card grid, or <=3-row small table), never dragging a large `<figure>` or long table.
    """
    _root, all_nodes = _parse_html_tree(body_html)
    edits: List[Tuple[int, int, str]] = []

    for node in all_nodes:
        classes = set(node.class_list())
        if node.tag == "table":
            if "table-short" not in classes and "table-long" not in classes:
                body_rows = _count_table_body_rows(node)
                cls = "table-short" if body_rows <= short_table_max_rows else "table-long"
                raw_start = body_html[node.start_idx:node.start_tag_end_idx]
                edits.append((node.start_idx, node.start_tag_end_idx, _add_class_to_start_tag(raw_start, cls)))
        elif "callout" in classes and "keep-with-prev" not in classes and node.parent is not None:
            siblings = node.parent.children
            try:
                pos = siblings.index(node)
            except ValueError:
                pos = -1
            prev_node = siblings[pos - 1] if pos > 0 else None
            callout_len = len(node.plain_text(body_html))
            if callout_len <= 380 and _is_lightweight_preceding_block(prev_node, body_html):
                raw_start = body_html[node.start_idx:node.start_tag_end_idx]
                edits.append((node.start_idx, node.start_tag_end_idx, _add_class_to_start_tag(raw_start, "keep-with-prev")))

    if not edits:
        return body_html

    out = body_html
    for s_idx, e_idx, replacement in sorted(edits, key=lambda x: x[0], reverse=True):
        out = out[:s_idx] + replacement + out[e_idx:]
    return out


def extract_h2_headings(body_html: str) -> List[Dict[str, Any]]:
    """Extract all `<h2>` headings in document order with exact tag spans and plain text."""
    _root, all_nodes = _parse_html_tree(body_html)
    h2s: List[Dict[str, Any]] = []
    for node in all_nodes:
        if node.tag == "h2":
            h2s.append({
                "index": len(h2s),
                "start_idx": node.start_idx,
                "start_tag_end_idx": node.start_tag_end_idx,
                "end_idx": node.end_idx,
                "classes": node.class_list(),
                "text": node.plain_text(body_html),
            })
    return h2s


def extract_h1_texts(body_html: str) -> Set[str]:
    """Extract normalized plain texts of all `<h1>` headings so `<h2>` measurement never confuses `<h1>`."""
    _root, all_nodes = _parse_html_tree(body_html)
    out: Set[str] = set()
    for node in all_nodes:
        if node.tag == "h1":
            norm = re.sub(r"\s+", "", node.plain_text(body_html))
            if norm:
                out.add(norm)
    return out


def inject_h2_page_breaks(body_html: str, break_indices: Set[int]) -> str:
    """Inject `chapter-start` class on `<h2>` tags at `break_indices` without altering inner content."""
    if not break_indices:
        return body_html
    h2s = extract_h2_headings(body_html)
    edits: List[Tuple[int, int, str]] = []
    for h in h2s:
        if h["index"] in break_indices:
            raw_start = body_html[h["start_idx"]:h["start_tag_end_idx"]]
            edits.append((h["start_idx"], h["start_tag_end_idx"], _add_class_to_start_tag(raw_start, "chapter-start")))
    out = body_html
    for s_idx, e_idx, replacement in sorted(edits, key=lambda x: x[0], reverse=True):
        out = out[:s_idx] + replacement + out[e_idx:]
    return out


def measure_h2_positions_in_pdf(
    pdf_path: str,
    h2_list: List[Dict[str, Any]],
    top_margin_mm: float = 11.0,
    bot_margin_mm: float = 12.0,
    min_h2_pt: float = 12.5,
    exclude_texts: Optional[Set[str]] = None,
) -> Tuple[Dict[int, Dict[str, Any]], int]:
    """
    Measure exact rendered page index and remaining vertical space ratio below every `<h2>`
    in a compiled PDF using PyMuPDF (sequentially across any language or heading prefix).
    Returns ({h2_idx: {"page": int, "y0": float, "rem_ratio": float, "text": str}}, total_pages).
    """
    try:
        import pymupdf as fitz  # PyMuPDF >= 1.24
    except ImportError:
        try:
            import fitz  # legacy PyMuPDF alias
        except ImportError:
            return {}, 0

    pt_per_mm = 72.0 / 25.4
    top_margin = top_margin_mm * pt_per_mm
    bot_margin = bot_margin_mm * pt_per_mm

    targets = [re.sub(r"\s+", "", h["text"]) for h in h2_list]
    excluded = {re.sub(r"\s+", "", t) for t in (exclude_texts or set()) if t}
    found: Dict[int, Dict[str, Any]] = {}
    curr_idx = 0

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    for p_idx, page in enumerate(doc):
        if curr_idx >= len(targets):
            break
        page_h = page.rect.height
        printable_h = page_h - top_margin - bot_margin
        printable_bot = page_h - bot_margin
        d = page.get_text("dict")
        for block in d.get("blocks", []):
            if block.get("type") != 0 or curr_idx >= len(targets):
                continue
            lines = block.get("lines", [])
            if not lines:
                continue
            max_block_size = 0.0
            block_parts: List[str] = []
            first_y0: Optional[float] = None
            for line in lines:
                spans = line.get("spans", [])
                if not spans:
                    continue
                line_max = max(s.get("size", 0.0) for s in spans)
                max_block_size = max(max_block_size, line_max)
                if line_max >= min_h2_pt:
                    if first_y0 is None:
                        first_y0 = float(line["bbox"][1])
                    block_parts.append("".join(s.get("text", "") for s in spans))
            if max_block_size < min_h2_pt or not block_parts or first_y0 is None:
                continue
            block_norm = re.sub(r"\s+", "", "".join(block_parts))
            if not block_norm or (block_norm in excluded and block_norm != targets[curr_idx]):
                continue

            matched_idx: Optional[int] = None
            # 1. Prefer exact match at curr_idx or lookahead exact match (never skip on loose substring)
            for cand_idx in range(curr_idx, len(targets)):
                t_norm = targets[cand_idx]
                if t_norm and block_norm == t_norm:
                    matched_idx = cand_idx
                    break
            # 2. Fallback to bounded prefix/substring match ONLY for the immediate next expected heading
            if matched_idx is None:
                t_norm = targets[curr_idx]
                if t_norm and (
                    block_norm.startswith(t_norm)
                    or (t_norm in block_norm and len(block_norm) <= len(t_norm) * 1.25)
                ):
                    matched_idx = curr_idx

            if matched_idx is not None:
                rem_ratio = (printable_bot - first_y0) / printable_h if printable_h > 0 else 1.0
                found[matched_idx] = {
                    "page": p_idx + 1,
                    "y0": first_y0,
                    "rem_ratio": rem_ratio,
                    "text": h2_list[matched_idx]["text"],
                }
                curr_idx = matched_idx + 1
    doc.close()
    return found, total_pages


def wrap_report_html(
    title: str,
    body_html: str,
    theme: str = "modern_sans",
    body_pt: float = 10.9,
    extra_css: str = "",
    doc_theme_id: Optional[str] = None,
    adaptive_layout: bool = True,
) -> str:
    """Wrap report HTML body with standardized DOCTYPE, UTF-8 meta, content-adaptive classes, and A4 print CSS."""
    base_css = build_report_css(theme=theme, body_pt=body_pt, doc_theme_id=doc_theme_id)
    processed_body = apply_content_adaptive_rules(body_html) if adaptive_layout else body_html
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
{base_css}
{extra_css}
  </style>
</head>
<body>
{processed_body}
</body>
</html>
"""


def _find_chromium_binary() -> Optional[str]:
    """Locate a local Chrome or Edge binary for headless PDF printing."""
    import shutil

    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("msedge"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def compile_html_to_pdf(
    html_content_or_path: str,
    output_pdf_path: str,
    cleanup_temp_html: bool = True,
    wait_ms: int = 400,
) -> str:
    """
    Compile an HTML string or existing .html file path to an A4 print-grade PDF via Playwright Chromium
    or local headless Chrome/Edge CLI.
    Automatically removes temporary .html files when `cleanup_temp_html=True` so `02_outputs/` stays clean.
    """
    import shutil
    import subprocess

    out_pdf = Path(output_pdf_path).resolve()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    potential_path = Path(html_content_or_path) if "\n" not in html_content_or_path and len(html_content_or_path) < 260 else None
    created_temp = False

    if potential_path is not None and potential_path.exists() and potential_path.is_file():
        html_file = potential_path.resolve()
    else:
        fd, temp_name = tempfile.mkstemp(suffix=".html", prefix="_tmp_report_", dir=str(out_pdf.parent))
        os.close(fd)
        html_file = Path(temp_name).resolve()
        html_file.write_text(html_content_or_path, encoding="utf-8")
        created_temp = True

    try:
        compiled = False
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(html_file.as_uri(), wait_until="networkidle")
                if wait_ms > 0:
                    page.wait_for_timeout(wait_ms)
                page.pdf(
                    path=str(out_pdf),
                    print_background=True,
                    prefer_css_page_size=True,
                )
                browser.close()
                compiled = out_pdf.exists() and out_pdf.stat().st_size > 500
        except Exception:
            compiled = False

        if not compiled:
            browser_bin = _find_chromium_binary()
            if not browser_bin:
                raise RuntimeError(
                    "Neither Playwright nor a local Chrome/Edge binary was found to compile HTML to PDF."
                )
            temp_profile = tempfile.mkdtemp(prefix="chrome_pdf_")
            temp_pdf = os.path.join(temp_profile, "output.pdf")
            try:
                args = [
                    browser_bin,
                    "--headless=new",
                    "--disable-gpu",
                    f"--user-data-dir={temp_profile}",
                    f"--print-to-pdf={temp_pdf}",
                    "--no-pdf-header-footer",
                    str(html_file),
                ]
                subprocess.run(
                    args,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=60,
                    check=False,
                )
                if not (os.path.exists(temp_pdf) and os.path.getsize(temp_pdf) > 500) and os.name == "nt":
                    env = os.environ.copy()
                    env["PDF_BROWSER_BIN"] = str(browser_bin)
                    env["PDF_TEMP_PROFILE"] = str(temp_profile)
                    env["PDF_TEMP_OUT"] = str(temp_pdf)
                    env["PDF_HTML_FILE"] = str(html_file)
                    ps_cmd = [
                        "powershell",
                        "-NoProfile",
                        "-Command",
                        (
                            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
                            '$argList = @("--headless=new", "--disable-gpu", '
                            '"--user-data-dir=$env:PDF_TEMP_PROFILE", '
                            '"--print-to-pdf=$env:PDF_TEMP_OUT", '
                            '"--no-pdf-header-footer", "$env:PDF_HTML_FILE"); '
                            'Start-Process -FilePath $env:PDF_BROWSER_BIN -ArgumentList $argList -Wait'
                        ),
                    ]
                    subprocess.run(
                        ps_cmd,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        env=env,
                        timeout=60,
                        check=False,
                    )

                if os.path.exists(temp_pdf) and os.path.getsize(temp_pdf) > 500:
                    shutil.copyfile(temp_pdf, str(out_pdf))
                else:
                    raise RuntimeError(f"Headless browser failed to produce PDF from {html_file}")
            finally:
                shutil.rmtree(temp_profile, ignore_errors=True)
    finally:
        fname_lower = html_file.name.lower()
        is_temp_file = (
            created_temp
            or fname_lower.startswith(("_tmp_", "temp_", "tmp_"))
            or fname_lower.endswith(".tmp.html")
        )
        if cleanup_temp_html and is_temp_file and html_file.exists():
            try:
                html_file.unlink(missing_ok=True)
            except OSError:
                pass

    return str(out_pdf)


def compile_adaptive_report_pdf(
    title: str,
    body_html: str,
    output_pdf_path: str,
    theme: str = "modern_sans",
    body_pt: float = 10.9,
    extra_css: str = "",
    doc_theme_id: Optional[str] = None,
    genre: Optional[str] = None,
    min_remaining_ratio: Optional[float] = None,
    skip_first_h2: bool = True,
    adaptive_layout: bool = True,
    cleanup_temp_html: bool = True,
    wait_ms: int = 400,
    return_diagnostics: bool = False,
) -> Union[str, Dict[str, Any]]:
    """
    Generic Content-Adaptive Smart Pagination PDF compiler for ANY Format B report:
    1. Applies short-vs-long table classification (`<= 5` vs `> 5` body rows) & light-tail callout rules.
    2. Iteratively compiles drafts via Chromium and measures real rendered `<h2>` coordinates across ALL
       headings (zero hardcoded chapter prefixes).
    3. Allows natural flow when sufficient vertical space remains (>= `min_remaining_ratio`), and inserts
       `chapter-start` page breaks ONLY on `<h2>` headings whose remaining space falls below threshold.
       Genre-adaptive thresholds: `~0.30-0.35` (default 0.34) for structured memos/blueprints;
       `~0.20-0.25` (default 0.22) for continuous narrative synthesis/cards.
    """
    threshold = resolve_min_remaining_ratio(genre=genre, min_remaining_ratio=min_remaining_ratio)
    prepared_body = apply_content_adaptive_rules(body_html) if adaptive_layout else body_html
    h2_list = extract_h2_headings(prepared_body)
    h1_texts = extract_h1_texts(prepared_body)

    break_indices: Set[int] = set()
    for h in h2_list:
        if "chapter-start" in h["classes"]:
            break_indices.add(h["index"])

    positions: Dict[int, Dict[str, Any]] = {}
    total_pages = 0
    passes = 0

    if h2_list:
        with tempfile.TemporaryDirectory(prefix="adaptive_pdf_") as tmp_dir:
            tmp_pdf = Path(tmp_dir) / "_adaptive_draft.pdf"
            max_passes = len(h2_list) + 2
            for it in range(1, max_passes + 1):
                passes = it
                iter_body = inject_h2_page_breaks(prepared_body, break_indices)
                full_html = wrap_report_html(
                    title=title,
                    body_html=iter_body,
                    theme=theme,
                    body_pt=body_pt,
                    extra_css=extra_css,
                    doc_theme_id=doc_theme_id,
                    adaptive_layout=False,
                )
                compile_html_to_pdf(full_html, str(tmp_pdf), cleanup_temp_html=True, wait_ms=wait_ms)
                positions, total_pages = measure_h2_positions_in_pdf(
                    str(tmp_pdf), h2_list, exclude_texts=h1_texts
                )
                if not positions:
                    break

                added_idx = None
                for h in h2_list:
                    idx = h["index"]
                    if idx in break_indices or idx not in positions:
                        continue
                    if skip_first_h2 and idx == 0:
                        continue
                    if "first-chapter" in h["classes"] or "no-auto-break" in h["classes"]:
                        continue
                    rem = positions[idx]["rem_ratio"]
                    if rem < threshold and rem < 0.93:
                        break_indices.add(idx)
                        added_idx = idx
                        break

                if added_idx is None:
                    break

    final_body = inject_h2_page_breaks(prepared_body, break_indices)
    final_html = wrap_report_html(
        title=title,
        body_html=final_body,
        theme=theme,
        body_pt=body_pt,
        extra_css=extra_css,
        doc_theme_id=doc_theme_id,
        adaptive_layout=False,
    )
    out_path = compile_html_to_pdf(final_html, output_pdf_path, cleanup_temp_html=cleanup_temp_html, wait_ms=wait_ms)
    if h2_list:
        positions, total_pages = measure_h2_positions_in_pdf(
            out_path, h2_list, exclude_texts=h1_texts
        )

    if return_diagnostics:
        return {
            "pdf_path": out_path,
            "total_pages": total_pages,
            "passes": passes,
            "threshold": threshold,
            "break_indices": sorted(break_indices),
            "headings": [
                {
                    "index": h["index"],
                    "text": h["text"],
                    "break": h["index"] in break_indices,
                    **positions.get(h["index"], {}),
                }
                for h in h2_list
            ],
        }
    return out_path
