# -*- coding: utf-8 -*-
"""
word_layout_engine.py
小型排版工具：讓 matplotlib 圖片「以實際印刷尺寸」設計，插入 Word / A4 直式頁面時字級不縮水。

設計原則
- 畫布寬度 = Word 預設內文寬度 6.27 吋（A4、左右邊界 2.54 cm），座標單位直接用「吋」。
  因此程式裡寫 8.3pt，貼進 Word 後印出來就是 8.3pt。
- 支援行內粗體（以 **粗體** 標記）、懸掛縮排、中文避頭尾與英數字不拆字。
"""
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch

FONT_FAMILY = "Microsoft JhengHei"
DPI = 300
WORD_TEXT_WIDTH_IN = 6.27

NO_LINE_START = set("，、。；：！？）》」』】〕％,.;:!?)%…～·")
NO_LINE_END = set("（《「『【〔(")
ASCII_TOKEN = re.compile(r"[A-Za-z0-9.,%+\-/~$×]+")

plt.rcParams["font.family"] = FONT_FAMILY
plt.rcParams["axes.unicode_minus"] = False

_measure_fig = plt.figure(dpi=DPI)
_renderer = _measure_fig.canvas.get_renderer()
_width_cache = {}


def fp(size, bold=False):
    return FontProperties(family=FONT_FAMILY, size=size, weight="bold" if bold else "normal")


def text_width_in(s, size, bold=False):
    key = (s, size, bold)
    if key not in _width_cache:
        w, _, _ = _renderer.get_text_width_height_descent(s, fp(size, bold), ismath=False)
        _width_cache[key] = w / DPI
    return _width_cache[key]


def parse_runs(text):
    """'**粗體**一般' -> [(token, bold), ...]，英數字串視為不可拆的單一 token。"""
    runs = []
    parts = re.split(r"(\*\*.+?\*\*)", text)
    for part in parts:
        if not part:
            continue
        bold = part.startswith("**") and part.endswith("**")
        body = part[2:-2] if bold else part
        pos = 0
        for m in ASCII_TOKEN.finditer(body):
            for ch in body[pos:m.start()]:
                runs.append((ch, bold))
            runs.append((m.group(0), bold))
            pos = m.end()
        for ch in body[pos:]:
            runs.append((ch, bold))
    return runs


def wrap_runs(text, size, max_w):
    """回傳 lines：每行為 [(segment_text, bold), ...]，含避頭尾處理。"""
    tokens = parse_runs(text)
    lines, cur, cur_w = [], [], 0.0
    for tok, bold in tokens:
        w = text_width_in(tok, size, bold)
        if cur and cur_w + w > max_w:
            carry = []
            if tok in NO_LINE_START:
                # 避頭：標點不放行首，將前一非標點字元連同標點移至下一行，絕不強行懸掛溢出卡片
                while cur and (cur[-1][0] in NO_LINE_START or cur[-1][0] in NO_LINE_END):
                    carry.insert(0, cur.pop())
                if cur:
                    carry.insert(0, cur.pop())
                while cur and cur[-1][0] in NO_LINE_END:
                    carry.insert(0, cur.pop())
                if cur:
                    lines.append(cur)
                cur = carry + [(tok, bold)]
                cur_w = sum(text_width_in(t, size, b) for t, b in cur)
            else:
                # 避尾：開括號不留行尾 → 移到下一行
                while cur and cur[-1][0] in NO_LINE_END:
                    carry.insert(0, cur.pop())
                if cur:
                    lines.append(cur)
                cur = carry + [(tok, bold)]
                cur_w = sum(text_width_in(t, size, b) for t, b in cur)
        else:
            if not cur and tok == " ":
                continue
            cur.append((tok, bold)); cur_w += w
    if cur:
        lines.append(cur)
    # 合併同樣式的相鄰 token 以減少繪圖物件
    merged = []
    for line in lines:
        segs = []
        for t, b in line:
            if segs and segs[-1][1] == b:
                segs[-1] = (segs[-1][0] + t, b)
            else:
                segs.append((t, b))
        merged.append(segs)
    return merged


def draw_runs_line(ax, x, y_baseline, segs, size, color, bold_color=None):
    for t, b in segs:
        ax.text(x, y_baseline, t, fontproperties=fp(size, b), color=(bold_color if (b and bold_color) else color),
                ha="left", va="baseline", zorder=6)
        x += text_width_in(t, size, b)


class Paragraph:
    """一段（可帶項目符號、可縮排）的量測與繪製。"""

    def __init__(self, text, size, width, bullet=None, indent=0.0, color="#1E293B", bold_color=None,
                 leading=1.42, space_before=0.0, align="left"):
        self.text, self.size, self.width = text, size, width
        self.bullet, self.indent, self.color, self.bold_color = bullet, indent, color, bold_color
        self.leading, self.space_before, self.align = leading, space_before, align
        self.bullet_w = text_width_in(bullet + " ", size) if bullet else 0.0
        self.lines = wrap_runs(text, size, width - indent - self.bullet_w)

    @property
    def line_h(self):
        return self.size * self.leading / 72.0

    @property
    def height(self):
        return self.space_before + len(self.lines) * self.line_h

    def draw(self, ax, x, y_top):
        y = y_top - self.space_before
        ascent = self.size * 0.80 / 72.0
        pad_top = (self.line_h - self.size / 72.0) / 2
        for i, segs in enumerate(self.lines):
            base = y - pad_top - ascent - i * self.line_h
            lx = x + self.indent
            if self.align == "center":
                lw = sum(text_width_in(t, self.size, b) for t, b in segs)
                lx = x + (self.width - lw) / 2
            if i == 0 and self.bullet:
                ax.text(lx, base, self.bullet, fontproperties=fp(self.size * 0.82), color=self.bold_color or self.color,
                        ha="left", va="baseline", zorder=6)
            draw_runs_line(ax, lx + self.bullet_w, base, segs, self.size, self.color, self.bold_color)
        return y_top - self.height


def rounded_box(ax, x, y, w, h, face, edge, lw=1.0, ls="-", radius=0.06, z=3):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                       facecolor=face, edgecolor=edge, linewidth=lw, linestyle=ls, zorder=z)
    ax.add_patch(p)
    return p


def new_canvas(width_in, height_in, bg="#FFFFFF"):
    fig = plt.figure(figsize=(width_in, height_in), dpi=DPI)
    fig.patch.set_facecolor(bg)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width_in)
    ax.set_ylim(0, height_in)
    ax.axis("off")
    return fig, ax
