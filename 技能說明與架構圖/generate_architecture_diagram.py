#!/usr/bin/env python3
"""
generate_architecture_diagram.py
生成「深度閱讀引導與視覺化知識統整技能 — 核心架構圖」（一般使用者視角、清爽白話版）。

設計依據：
- 參考 `.agents/skills/deep-reading-and-visual-synthesis/scripts/generate_mindmap.py` 之
  CJK 字型設定、缺字替換與防撞原則。
- 內建 `verify_visual_outputs.check_matplotlib_text_collisions()` 零文字碰撞預檢。
- 規格與重繪提示詞詳見同目錄 `architecture_diagram_spec.md`。

使用方式：
    python 技能說明與架構圖/generate_architecture_diagram.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# ---------------------------------------------------------------------------
# 1. 路徑與技能底層工具匯入（沿用 generate_mindmap 與 verify_visual_outputs）
# ---------------------------------------------------------------------------
THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent
SCRIPTS_DIR = (
    REPO_ROOT
    / ".agents"
    / "skills"
    / "deep-reading-and-visual-synthesis"
    / "scripts"
)
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from generate_mindmap import configure_cjk_fonts, sanitize_cjk_glyphs  # noqa: E402
from verify_visual_outputs import check_matplotlib_text_collisions  # noqa: E402

OUTPUT_PNG = THIS_DIR / "skill_architecture_overview.png"

# ---------------------------------------------------------------------------
# 2. 全域畫布、字級與色票常數（日後微調版面只需修改此區）
# ---------------------------------------------------------------------------
FIG_SIZE = (24.0, 15.2)
DPI = 240

FONT_SIZES = {
    "main_title": 27.5,
    "subtitle": 15.2,
    "zone_title": 16.2,
    "badge": 12.6,
    "card_title": 14.8,
    "card_title_compact": 14.0,
    "body": 13.0,
    "body_compact": 12.4,
    "arrow_label": 11.8,
}

LINE_SPACING = 1.58

COLORS = {
    "canvas_bg": "#FAFBFD",
    "ink_dark": "#0F172A",
    "ink_body": "#334155",
    "ink_muted": "#475569",
    # 灰藍（開始使用）
    "slate_border": "#1E293B",
    "slate_fill": "#F8FAFC",
    # 藍（第零關）
    "blue_border": "#2563EB",
    "blue_fill": "#EFF6FF",
    "blue_text": "#1D4ED8",
    # 橘（核心特色 1：初始化精靈）
    "orange_border": "#EA580C",
    "orange_fill": "#FFF7ED",
    "orange_card_border": "#FB923C",
    "orange_text": "#C2410C",
    # 綠（核心特色 2：30 天無損更新）
    "green_border": "#16A34A",
    "green_fill": "#F0FDF4",
    "green_card_fill": "#DCFCE7",
    "green_card_border": "#4ADE80",
    "green_text": "#15803D",
    # 紫（第一階段：深度閱讀與資料探索）
    "purple_border": "#7C3AED",
    "purple_fill": "#F5F3FF",
    "purple_soft_fill": "#EDE9FE",
    "purple_card_border": "#A78BFA",
    "purple_text": "#6D28D9",
    # 青（第二階段：視覺化合成）
    "teal_border": "#0891B2",
    "teal_fill": "#ECFEFF",
    "teal_soft_fill": "#CFFAFE",
    "teal_card_border": "#22D3EE",
    "teal_text": "#0E7490",
    # 紅（核心特色 3：進化與回饋閉環）
    "red_border": "#DC2626",
    "red_fill": "#FEF2F2",
    "red_soft_fill": "#FEE2E2",
    "red_card_border": "#F87171",
    "red_text": "#B91C1C",
    # 連線與中性灰
    "arrow_neutral": "#64748B",
    "white": "#FFFFFF",
}


# ---------------------------------------------------------------------------
# 3. 繪圖基礎原語（圓角容器、徽章、卡片、精準箭頭與文字膠囊）
# ---------------------------------------------------------------------------
def draw_rounded_box(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    facecolor: str,
    edgecolor: str,
    lw: float = 2.0,
    rounding: float = 0.85,
    zorder: int = 2,
    linestyle: str = "-",
) -> tuple[float, float, float, float]:
    """繪製圓角矩形，回傳 (x, y, w, h) 便於後續錨點連線。"""
    pad = 0.0
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad={pad},rounding_size={rounding}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=lw,
        linestyle=linestyle,
        zorder=zorder,
    )
    ax.add_patch(patch)
    return (x, y, w, h)


def draw_zone(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    facecolor: str,
    edgecolor: str,
    title_color: str,
    badge_text: str | None = None,
    badge_color: str | None = None,
    zorder: int = 1,
) -> tuple[float, float, float, float]:
    """繪製外層宏觀分區（含左上標題與選配右上實心徽章）。"""
    box = draw_rounded_box(
        ax,
        x,
        y,
        w,
        h,
        facecolor=facecolor,
        edgecolor=edgecolor,
        lw=2.2,
        rounding=1.0,
        zorder=zorder,
    )
    header_y = y + h - 2.45
    ax.text(
        x + 1.5,
        header_y,
        sanitize_cjk_glyphs(title),
        fontsize=FONT_SIZES["zone_title"],
        fontweight="bold",
        color=title_color,
        ha="left",
        va="center",
        zorder=zorder + 2,
    )
    if badge_text and badge_color:
        badge_w = 8.4
        badge_h = 2.55
        bx = x + w - badge_w - 1.3
        by = header_y - badge_h / 2.0
        draw_rounded_box(
            ax,
            bx,
            by,
            badge_w,
            badge_h,
            facecolor=badge_color,
            edgecolor="none",
            lw=0,
            rounding=0.75,
            zorder=zorder + 2,
        )
        ax.text(
            bx + badge_w / 2.0,
            header_y,
            sanitize_cjk_glyphs(badge_text),
            fontsize=FONT_SIZES["badge"],
            fontweight="bold",
            color=COLORS["white"],
            ha="center",
            va="center",
            zorder=zorder + 3,
        )
    return box


def draw_card(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    body_lines: list[str],
    edgecolor: str,
    facecolor: str = "#FFFFFF",
    title_color: str = "#0F172A",
    body_color: str = "#334155",
    title_size: float | None = None,
    body_size: float | None = None,
    align: str = "center",
    lw: float = 1.6,
    zorder: int = 3,
) -> tuple[float, float, float, float]:
    """繪製內層卡片（標題＋高可讀行距內文，自動垂直置中對齊）。"""
    box = draw_rounded_box(
        ax,
        x,
        y,
        w,
        h,
        facecolor=facecolor,
        edgecolor=edgecolor,
        lw=lw,
        rounding=0.75,
        zorder=zorder,
    )
    tsize = title_size or FONT_SIZES["card_title"]
    bsize = body_size or FONT_SIZES["body"]

    clean_title = sanitize_cjk_glyphs(title)
    clean_body = "\n".join(sanitize_cjk_glyphs(line) for line in body_lines)

    # 依行數與卡片高度決定標題與內文的垂直重心，避免上下擁擠或中段過空
    n_lines = len(body_lines)
    if n_lines == 0:
        title_y = y + h * 0.50
        body_y = None
    elif n_lines == 1:
        title_y = y + h * 0.65
        body_y = y + h * 0.32
    elif n_lines == 2:
        if h >= 12.0:
            title_y = y + h * 0.65
            body_y = y + h * 0.37
        else:
            title_y = y + h * 0.70
            body_y = y + h * 0.33
    else:
        if h >= 12.0:
            title_y = y + h * 0.73
            body_y = y + h * 0.37
        else:
            title_y = y + h * 0.77
            body_y = y + h * 0.36

    tx = x + w / 2.0 if align == "center" else x + 1.3
    ha = "center" if align == "center" else "left"

    ax.text(
        tx,
        title_y,
        clean_title,
        fontsize=tsize,
        fontweight="bold",
        color=title_color,
        ha=ha,
        va="center",
        zorder=zorder + 1,
    )
    if body_y is not None:
        ax.text(
            tx,
            body_y,
            clean_body,
            fontsize=bsize,
            color=body_color,
            ha=ha,
            va="center",
            linespacing=LINE_SPACING,
            zorder=zorder + 1,
        )
    return box


def draw_arrow(
    ax,
    p0: tuple[float, float],
    p1: tuple[float, float],
    color: str,
    lw: float = 2.0,
    linestyle: str = "-",
    rad: float = 0.0,
    zorder: int = 5,
) -> None:
    """繪製平滑箭頭連線。"""
    arrow = FancyArrowPatch(
        p0,
        p1,
        arrowstyle="-|>,head_length=8.5,head_width=5.2",
        connectionstyle=f"arc3,rad={rad}",
        color=color,
        linewidth=lw,
        linestyle=linestyle,
        shrinkA=2,
        shrinkB=2,
        zorder=zorder,
    )
    ax.add_patch(arrow)


def draw_polyline_arrow(
    ax,
    points: list[tuple[float, float]],
    color: str,
    lw: float = 2.0,
    linestyle: str = "-",
    zorder: int = 5,
) -> None:
    """繪製多段正交折線並在末段加箭頭（避免穿過方塊）。"""
    xs = [p[0] for p in points[:-1]]
    ys = [p[1] for p in points[:-1]]
    # 先畫前面折線段（含末段起點）
    ax.plot(
        xs + [points[-1][0] * 0.0 + points[-2][0]],
        ys + [points[-2][1]],
        color=color,
        linewidth=lw,
        linestyle=linestyle,
        solid_capstyle="round",
        solid_joinstyle="round",
        zorder=zorder,
    )
    if len(points) >= 2:
        # 前 n-2 段純折線
        if len(points) > 2:
            ax.plot(
                [p[0] for p in points[:-1]],
                [p[1] for p in points[:-1]],
                color=color,
                linewidth=lw,
                linestyle=linestyle,
                solid_capstyle="round",
                solid_joinstyle="round",
                zorder=zorder,
            )
        # 最後一段帶箭頭
        arrow = FancyArrowPatch(
            points[-2],
            points[-1],
            arrowstyle="-|>,head_length=8.5,head_width=5.2",
            color=color,
            linewidth=lw,
            linestyle=linestyle,
            shrinkA=0,
            shrinkB=2,
            zorder=zorder,
        )
        ax.add_patch(arrow)


def draw_pill_label(
    ax,
    x: float,
    y: float,
    text: str,
    text_color: str,
    bg_color: str = "#FAFBFD",
    border_color: str | None = None,
    zorder: int = 7,
) -> None:
    """在箭頭上方繪製帶白底的清晰標籤，不壓字不糊線。"""
    ax.text(
        x,
        y,
        sanitize_cjk_glyphs(text),
        fontsize=FONT_SIZES["arrow_label"],
        fontweight="bold",
        color=text_color,
        ha="center",
        va="center",
        bbox=dict(
            boxstyle="round,pad=0.28,rounding_size=0.4",
            facecolor=bg_color,
            edgecolor=border_color or "none",
            linewidth=1.0 if border_color else 0.0,
        ),
        zorder=zorder,
    )


# ---------------------------------------------------------------------------
# 4. 主繪圖流程
# ---------------------------------------------------------------------------
def build_architecture_diagram(output_path: Path = OUTPUT_PNG) -> Path:
    configure_cjk_fonts()

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(COLORS["canvas_bg"])
    ax.set_facecolor(COLORS["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # =========================================================================
    # 頂部主標題與副標題 (Y: 92.2 ~ 98.5)
    # =========================================================================
    ax.text(
        50.0,
        96.4,
        sanitize_cjk_glyphs("深度閱讀引導與視覺化知識統整技能 — 核心架構圖"),
        fontsize=FONT_SIZES["main_title"],
        fontweight="bold",
        color=COLORS["ink_dark"],
        ha="center",
        va="center",
        zorder=10,
    )
    ax.text(
        50.0,
        93.0,
        sanitize_cjk_glyphs(
            "三大核心特色：首次啟用專屬初始化  ｜  每月一次無損檢查更新  ｜  不中斷流程三通道回饋"
        ),
        fontsize=FONT_SIZES["subtitle"],
        color=COLORS["ink_muted"],
        ha="center",
        va="center",
        zorder=10,
    )

    # =========================================================================
    # 頂列：開始使用 ＋ 第零關 ＋ 初始化精靈 (特色1) ＋ 無損更新 (特色2)
    # Y: 67.2 ~ 88.2（上方預留 Y=88.2~91.2 作為既有使用者綠色通道）
    # =========================================================================
    box_start = draw_card(
        ax,
        x=2.0,
        y=79.0,
        w=19.2,
        h=9.2,
        title="開始使用",
        body_lines=["提供文章 / 網頁 / YouTube", "PDF / DOCX 或 數據集＋說明書"],
        edgecolor=COLORS["slate_border"],
        facecolor=COLORS["slate_fill"],
        title_color=COLORS["ink_dark"],
        lw=2.2,
    )
    box_gate0 = draw_card(
        ax,
        x=2.0,
        y=67.2,
        w=19.2,
        h=8.8,
        title="第零關：啟動檢查與把關",
        body_lines=["自動辨識首次新朋友", "或已初始化之既有使用者"],
        edgecolor=COLORS["blue_border"],
        facecolor=COLORS["blue_fill"],
        title_color=COLORS["blue_text"],
        lw=2.2,
    )
    draw_arrow(
        ax,
        (box_start[0] + box_start[2] / 2.0, box_start[1]),
        (box_gate0[0] + box_gate0[2] / 2.0, box_gate0[1] + box_gate0[3]),
        color=COLORS["slate_border"],
        lw=2.1,
    )

    # 核心特色 1：首次啟用初始化精靈 (X: 25.4 ~ 67.2, Y: 67.2 ~ 88.2)
    zone_onboard = draw_zone(
        ax,
        x=25.4,
        y=67.2,
        w=41.8,
        h=21.0,
        title="首次啟用初始化精靈（一次設定，永久生效）",
        facecolor=COLORS["orange_fill"],
        edgecolor=COLORS["orange_border"],
        title_color=COLORS["orange_text"],
        badge_text="核心特色 1",
        badge_color=COLORS["orange_border"],
    )
    onboard_steps = [
        ("1. 環境健檢", ["分級檢查工具", "無帳號也能用"]),
        ("2. 專屬配色", ["自選主色或由", "AI 依場景設計"]),
        ("3. 個人筆風", ["歷史文章萃取", "口述或 AI 生成"]),
        ("4. 偏好存檔", ["確認產出習慣", "與個人化設定"]),
    ]
    sub_w = 9.2
    sub_gap = 0.85
    sub_x0 = zone_onboard[0] + 1.25
    for idx, (st_title, st_lines) in enumerate(onboard_steps):
        sx = sub_x0 + idx * (sub_w + sub_gap)
        draw_card(
            ax,
            x=sx,
            y=69.2,
            w=sub_w,
            h=13.4,
            title=st_title,
            body_lines=st_lines,
            edgecolor=COLORS["orange_card_border"],
            facecolor=COLORS["white"],
            title_color=COLORS["orange_text"],
            title_size=FONT_SIZES["card_title_compact"],
            body_size=FONT_SIZES["body_compact"],
            lw=1.6,
        )

    # 核心特色 2：每月一次無損檢查更新 (X: 69.6 ~ 98.0, Y: 67.2 ~ 88.2)
    zone_update = draw_zone(
        ax,
        x=69.6,
        y=67.2,
        w=28.4,
        h=21.0,
        title="每月一次無損檢查更新",
        facecolor=COLORS["green_fill"],
        edgecolor=COLORS["green_border"],
        title_color=COLORS["green_text"],
        badge_text="核心特色 2",
        badge_color=COLORS["green_border"],
    )
    box_upd_left = draw_card(
        ax,
        x=71.0,
        y=76.4,
        w=12.4,
        h=7.0,
        title="30 天節流檢查",
        body_lines=["未滿 30 天零等待", "有新版先展示摘要"],
        edgecolor=COLORS["green_card_border"],
        facecolor=COLORS["white"],
        title_color=COLORS["green_text"],
        title_size=FONT_SIZES["card_title_compact"],
        body_size=FONT_SIZES["body_compact"],
    )
    box_upd_right = draw_card(
        ax,
        x=84.4,
        y=76.4,
        w=12.2,
        h=7.0,
        title="同意後無損升級",
        body_lines=["僅更新官方核心", "規則與運作流程"],
        edgecolor=COLORS["green_card_border"],
        facecolor=COLORS["white"],
        title_color=COLORS["green_text"],
        title_size=FONT_SIZES["card_title_compact"],
        body_size=FONT_SIZES["body_compact"],
    )
    box_upd_bot = draw_card(
        ax,
        x=71.0,
        y=68.6,
        w=25.6,
        h=6.2,
        title="嚴格保護不覆蓋個人心血",
        body_lines=["100% 保留：個人偏好、專屬配色、自建筆風與歷史產出"],
        edgecolor=COLORS["green_border"],
        facecolor=COLORS["green_card_fill"],
        title_color=COLORS["green_text"],
        title_size=FONT_SIZES["card_title_compact"],
        body_size=FONT_SIZES["body_compact"],
    )
    draw_arrow(
        ax,
        (box_upd_right[0] + box_upd_right[2] / 2.0, box_upd_right[1]),
        (box_upd_right[0] + box_upd_right[2] / 2.0, box_upd_bot[1] + box_upd_bot[3]),
        color=COLORS["green_border"],
        lw=1.8,
    )

    # 頂列路由箭頭
    # 1. 第零關 -> 初始化精靈（首次使用）
    draw_arrow(
        ax,
        (box_gate0[0] + box_gate0[2], 74.2),
        (zone_onboard[0], 74.2),
        color=COLORS["orange_border"],
        lw=2.1,
    )
    draw_pill_label(
        ax,
        23.3,
        76.8,
        "首次使用",
        text_color=COLORS["orange_text"],
        bg_color=COLORS["canvas_bg"],
    )

    # 2. 第零關 -> 每月無損更新（走上方走廊 Y=90.0，不穿任何方塊）
    draw_polyline_arrow(
        ax,
        [
            (box_gate0[0] + box_gate0[2], 70.6),
            (23.3, 70.6),
            (23.3, 90.0),
            (83.8, 90.0),
            (83.8, zone_update[1] + zone_update[3]),
        ],
        color=COLORS["green_border"],
        lw=2.0,
    )
    draw_pill_label(
        ax,
        54.0,
        90.0,
        "已初始化使用者（每 30 天檢查一次）",
        text_color=COLORS["green_text"],
        bg_color=COLORS["canvas_bg"],
    )

    # =========================================================================
    # 中左：第一階段 — 深度閱讀與資料探索 (X: 2.0 ~ 70.4, Y: 40.5 ~ 63.0)
    # =========================================================================
    zone_p1 = draw_zone(
        ax,
        x=2.0,
        y=40.5,
        w=68.4,
        h=22.5,
        title="第一階段：深度閱讀與資料探索（自動擷取歸檔，不中斷思辨）",
        facecolor=COLORS["purple_fill"],
        edgecolor=COLORS["purple_border"],
        title_color=COLORS["purple_text"],
    )
    box_p1_ingest = draw_card(
        ax,
        x=3.5,
        y=42.5,
        w=15.4,
        h=15.4,
        title="自動擷取與分流",
        body_lines=["網頁 / 影片 / PDF /", "CSV 一鍵歸檔整理", "自動辨識四大閱讀模式"],
        edgecolor=COLORS["purple_card_border"],
        facecolor=COLORS["white"],
        title_color=COLORS["purple_text"],
        body_size=FONT_SIZES["body_compact"],
    )
    box_p1_m1 = draw_card(
        ax,
        x=21.2,
        y=50.9,
        w=30.6,
        h=7.0,
        title="模式一：文獻與多檔深度導讀",
        body_lines=["單篇 / 多檔診斷 / 跨篇統整 → 蘇格拉底五步提問與跨域類比"],
        edgecolor=COLORS["purple_card_border"],
        facecolor=COLORS["white"],
        title_color=COLORS["purple_text"],
        body_size=FONT_SIZES["body_compact"],
    )
    box_p1_m2 = draw_card(
        ax,
        x=21.2,
        y=42.5,
        w=30.6,
        h=7.0,
        title="模式二：數據集探索與分配導學",
        body_lines=["CSV ＋ 資料說明書 → 三層分流驗算 → 故事切角與 10 大分配圖"],
        edgecolor=COLORS["purple_card_border"],
        facecolor=COLORS["white"],
        title_color=COLORS["purple_text"],
        body_size=FONT_SIZES["body_compact"],
    )
    box_p1_log = draw_card(
        ax,
        x=54.1,
        y=42.5,
        w=14.8,
        h=15.4,
        title="即時保存思辨軌跡",
        body_lines=["完整留存討論脈絡", "與關鍵數據驗算", "（亦支援跳關直通）"],
        edgecolor=COLORS["purple_border"],
        facecolor=COLORS["purple_soft_fill"],
        title_color=COLORS["purple_text"],
        body_size=FONT_SIZES["body_compact"],
    )

    # 第一階段內部箭頭
    draw_arrow(
        ax,
        (box_p1_ingest[0] + box_p1_ingest[2], 52.8),
        (box_p1_m1[0], 54.4),
        color=COLORS["purple_border"],
        lw=2.0,
    )
    draw_arrow(
        ax,
        (box_p1_ingest[0] + box_p1_ingest[2], 47.6),
        (box_p1_m2[0], 46.0),
        color=COLORS["purple_border"],
        lw=2.0,
    )
    draw_arrow(
        ax,
        (box_p1_m1[0] + box_p1_m1[2], 54.4),
        (box_p1_log[0], 52.8),
        color=COLORS["purple_border"],
        lw=2.0,
    )
    draw_arrow(
        ax,
        (box_p1_m2[0] + box_p1_m2[2], 46.0),
        (box_p1_log[0], 47.6),
        color=COLORS["purple_border"],
        lw=2.0,
    )

    # 頂列 -> 第一階段連線
    draw_arrow(
        ax,
        (box_gate0[0] + box_gate0[2] / 2.0, box_gate0[1]),
        (box_gate0[0] + box_gate0[2] / 2.0, zone_p1[1] + zone_p1[3]),
        color=COLORS["arrow_neutral"],
        lw=2.1,
    )
    draw_arrow(
        ax,
        (zone_onboard[0] + zone_onboard[2] / 2.0, zone_onboard[1]),
        (zone_onboard[0] + zone_onboard[2] / 2.0, zone_p1[1] + zone_p1[3]),
        color=COLORS["orange_border"],
        lw=2.1,
    )
    draw_polyline_arrow(
        ax,
        [
            (74.5, zone_update[1]),
            (74.5, 65.1),
            (62.5, 65.1),
            (62.5, zone_p1[1] + zone_p1[3]),
        ],
        color=COLORS["green_border"],
        lw=2.0,
    )

    # =========================================================================
    # 底左：第二階段 — 樹狀分枝規劃與五大視覺化成果合成 (X: 2.0 ~ 70.4, Y: 2.2 ~ 36.2)
    # =========================================================================
    zone_p2 = draw_zone(
        ax,
        x=2.0,
        y=2.2,
        w=68.4,
        h=34.0,
        title="第二階段：樹狀分枝規劃與五大視覺化成果合成",
        facecolor=COLORS["teal_fill"],
        edgecolor=COLORS["teal_border"],
        title_color=COLORS["teal_text"],
    )
    box_p2_trunk = draw_card(
        ax,
        x=3.5,
        y=24.6,
        w=31.1,
        h=7.0,
        title="主幹定裝：格式範圍 × 表達三支柱",
        body_lines=["先拍板格式，再統一訂定設計光譜 (1/2/3)、筆風與配色"],
        edgecolor=COLORS["teal_border"],
        facecolor=COLORS["white"],
        title_color=COLORS["teal_text"],
        body_size=FONT_SIZES["body_compact"],
    )
    box_p2_branch = draw_card(
        ax,
        x=37.8,
        y=24.6,
        w=31.1,
        h=7.0,
        title="獨立分枝規劃與隔離建構",
        body_lines=["未選格式零讀取；各格式獨立執行規劃、生成與驗收"],
        edgecolor=COLORS["teal_border"],
        facecolor=COLORS["white"],
        title_color=COLORS["teal_text"],
        body_size=FONT_SIZES["body_compact"],
    )
    draw_arrow(
        ax,
        (box_p2_trunk[0] + box_p2_trunk[2], 28.1),
        (box_p2_branch[0], 28.1),
        color=COLORS["teal_border"],
        lw=2.1,
    )

    # 五大視覺化格式卡片 (Y: 12.2 ~ 21.6)
    formats_spec = [
        ("格式 A\n知識圖譜", ["多主題防撞", "高解析全景圖"]),
        ("格式 B\n報告與專欄", ["PDF（含內建簡圖）", "或 Medium 專欄"]),
        ("格式 C\n高階簡報", ["視距自適應", "多元版型防撞"]),
        ("格式 D\n量化統計圖", ["5 大家族 30+ 圖", "與 10 大分配圖"]),
        ("格式 E\n數據儀表板", ["單頁互動網頁", "支援一鍵部署"]),
    ]
    fmt_w = 12.15
    fmt_gap = 1.16
    fmt_x0 = 3.5
    fmt_boxes = []
    for idx, (ftitle, flines) in enumerate(formats_spec):
        fx = fmt_x0 + idx * (fmt_w + fmt_gap)
        fbox = draw_rounded_box(
            ax,
            fx,
            12.2,
            fmt_w,
            9.4,
            facecolor=COLORS["white"],
            edgecolor=COLORS["teal_border"],
            lw=1.7,
            rounding=0.75,
            zorder=3,
        )
        ax.text(
            fx + fmt_w / 2.0,
            18.85,
            sanitize_cjk_glyphs(ftitle),
            fontsize=FONT_SIZES["card_title_compact"],
            fontweight="bold",
            color=COLORS["teal_text"],
            ha="center",
            va="center",
            linespacing=1.28,
            zorder=4,
        )
        ax.text(
            fx + fmt_w / 2.0,
            14.4,
            "\n".join(sanitize_cjk_glyphs(l) for l in flines),
            fontsize=FONT_SIZES["body_compact"],
            color=COLORS["ink_body"],
            ha="center",
            va="center",
            linespacing=1.45,
            zorder=4,
        )
        fmt_boxes.append(fbox)

    # 底部品質驗收與交付列 (Y: 3.8 ~ 9.8)
    box_p2_qa = draw_card(
        ax,
        x=9.5,
        y=3.8,
        w=54.5,
        h=6.0,
        title="自動化視覺品質驗收 ＋ 乾淨交付",
        body_lines=["自動檢查版面防撞與配色一致性、清除中介暫存檔，交付完整正式成果"],
        edgecolor=COLORS["teal_border"],
        facecolor=COLORS["teal_soft_fill"],
        title_color=COLORS["teal_text"],
        body_size=FONT_SIZES["body_compact"],
    )

    # 主幹分枝 -> 五大格式（乾淨匯流線，避免雜亂放射交錯）
    bus_y_top = 23.1
    ax.plot(
        [box_p2_branch[0] + box_p2_branch[2] / 2.0, box_p2_branch[0] + box_p2_branch[2] / 2.0],
        [box_p2_branch[1], bus_y_top],
        color=COLORS["teal_border"],
        linewidth=1.9,
        zorder=4,
    )
    leftmost_cx = fmt_boxes[0][0] + fmt_boxes[0][2] / 2.0
    rightmost_cx = fmt_boxes[-1][0] + fmt_boxes[-1][2] / 2.0
    ax.plot(
        [leftmost_cx, rightmost_cx],
        [bus_y_top, bus_y_top],
        color=COLORS["teal_border"],
        linewidth=1.9,
        zorder=4,
    )
    for fb in fmt_boxes:
        cx = fb[0] + fb[2] / 2.0
        draw_arrow(
            ax,
            (cx, bus_y_top),
            (cx, fb[1] + fb[3]),
            color=COLORS["teal_border"],
            lw=1.7,
        )
        draw_arrow(
            ax,
            (cx, fb[1]),
            (cx, box_p2_qa[1] + box_p2_qa[3]),
            color=COLORS["teal_border"],
            lw=1.7,
        )

    # 第一階段 -> 第二階段連線（乾淨折線＋白底標籤）
    draw_polyline_arrow(
        ax,
        [
            (box_p1_log[0] + box_p1_log[2] / 2.0, box_p1_log[1]),
            (box_p1_log[0] + box_p1_log[2] / 2.0, 38.4),
            (19.3, 38.4),
            (19.3, zone_p2[1] + zone_p2[3]),
        ],
        color=COLORS["purple_border"],
        lw=2.1,
    )
    draw_pill_label(
        ax,
        40.5,
        38.4,
        "討論收斂完成（或顯式跳關直出）",
        text_color=COLORS["purple_text"],
        bg_color=COLORS["canvas_bg"],
    )

    # =========================================================================
    # 右欄：核心特色 3 — 靈感與進化回饋閉環 (X: 75.4 ~ 98.0, Y: 2.2 ~ 63.0)
    # =========================================================================
    zone_fb = draw_zone(
        ax,
        x=75.4,
        y=2.2,
        w=22.6,
        h=60.8,
        title="靈感與進化回饋閉環",
        facecolor=COLORS["red_fill"],
        edgecolor=COLORS["red_border"],
        title_color=COLORS["red_text"],
        badge_text="核心特色 3",
        badge_color=COLORS["red_border"],
    )
    box_fb1 = draw_card(
        ax,
        x=76.8,
        y=47.2,
        w=19.8,
        h=10.6,
        title="靈感與問題暫存清單",
        body_lines=["過程中發現異常或構想", "先靜默記錄，絕不打斷主流程"],
        edgecolor=COLORS["red_card_border"],
        facecolor=COLORS["white"],
        title_color=COLORS["red_text"],
        body_size=FONT_SIZES["body_compact"],
    )
    box_fb2 = draw_card(
        ax,
        x=76.8,
        y=33.8,
        w=19.8,
        h=9.6,
        title="成果驗收後統一啟動回報",
        body_lines=["依流程、視覺、筆風、程式、", "異常等類別自動標記整理"],
        edgecolor=COLORS["red_card_border"],
        facecolor=COLORS["white"],
        title_color=COLORS["red_text"],
        body_size=FONT_SIZES["body_compact"],
    )
    box_fb3 = draw_card(
        ax,
        x=76.8,
        y=17.4,
        w=19.8,
        h=12.6,
        title="三通道無障礙回報至原作者",
        body_lines=[
            "● 通道 A：開發者工具直接建單",
            "● 通道 B：無帳號匿名自動建單",
            "● 通道 C：離線產生預填網址",
        ],
        edgecolor=COLORS["red_border"],
        facecolor=COLORS["red_soft_fill"],
        title_color=COLORS["red_text"],
        body_size=FONT_SIZES["body_compact"],
    )
    box_fb4 = draw_card(
        ax,
        x=76.8,
        y=3.8,
        w=19.8,
        h=9.8,
        title="本機實證進化與創意入庫",
        body_lines=["經同意後查證依據、更新規範", "沉澱優秀創意並清空暫存清單"],
        edgecolor=COLORS["red_card_border"],
        facecolor=COLORS["white"],
        title_color=COLORS["red_text"],
        body_size=FONT_SIZES["body_compact"],
    )

    # 回饋閉環內部垂直箭頭
    fb_cx = 86.7
    for upper, lower in [(box_fb1, box_fb2), (box_fb2, box_fb3), (box_fb3, box_fb4)]:
        draw_arrow(
            ax,
            (fb_cx, upper[1]),
            (fb_cx, lower[1] + lower[3]),
            color=COLORS["red_border"],
            lw=2.0,
        )

    # 跨區連線：Phase 1 / Phase 2 -> 回饋閉環（X=70.4~75.4 寬裕雙軌走廊，零重疊零穿框）
    # 1. Phase 1 -> 暫存清單（不中斷記錄）
    draw_arrow(
        ax,
        (zone_p1[0] + zone_p1[2], 52.8),
        (box_fb1[0], 52.8),
        color=COLORS["red_border"],
        lw=1.9,
        linestyle="--",
    )
    draw_pill_label(
        ax,
        72.9,
        55.4,
        "不中斷記錄",
        text_color=COLORS["red_text"],
        bg_color=COLORS["canvas_bg"],
    )

    # 2. Phase 2 過程中 -> 暫存清單（虛線走左軌 X=72.2 往上匯入）
    draw_polyline_arrow(
        ax,
        [
            (zone_p2[0] + zone_p2[2], 28.0),
            (72.2, 28.0),
            (72.2, 50.0),
            (box_fb1[0], 50.0),
        ],
        color=COLORS["red_border"],
        lw=1.7,
        linestyle="--",
    )

    # 3. Phase 2 品質驗收 -> 統一啟動回報（實線走右軌 X=73.7 往上匯入）
    draw_polyline_arrow(
        ax,
        [
            (box_p2_qa[0] + box_p2_qa[2], 6.8),
            (73.7, 6.8),
            (73.7, 38.6),
            (box_fb2[0], 38.6),
        ],
        color=COLORS["red_border"],
        lw=2.0,
    )
    draw_pill_label(
        ax,
        67.2,
        6.8,
        "驗收後觸發",
        text_color=COLORS["red_text"],
        bg_color=COLORS["teal_fill"],
    )

    # =========================================================================
    # 5. 自動化文字防撞預檢與無損輸出
    # =========================================================================
    fig.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)
    collision_report = check_matplotlib_text_collisions(
        fig, shrink_pt=1.5, print_report=True
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_path,
        dpi=DPI,
        facecolor=COLORS["canvas_bg"],
        edgecolor="none",
    )
    plt.close(fig)

    print(f"[OK] Saved architecture diagram -> {output_path}")
    if collision_report.get("collision_count", 0) > 0:
        print(
            f"[WARN] Detected {collision_report['collision_count']} text collisions; "
            "please inspect and adjust coordinates."
        )
    return output_path


if __name__ == "__main__":
    build_architecture_diagram()
