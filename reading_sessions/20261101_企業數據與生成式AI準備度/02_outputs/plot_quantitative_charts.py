# -*- coding: utf-8 -*-
"""
Format D: Quantitative Empirical Charts (Publication-Grade Economist / Pew Style)
Article: 企業數據與生成式AI準備度 (2024 CDO Survey, N = 335, AWS & CDOIQ)

Implements the 4 Core Visual Cognition Breakthroughs (quantitative_chart_spec.md):
1. XY-Axis Spatial Gravity Swap:
   - X-axis (Left -> Right): Stage progression / maturity hierarchy.
   - Y-axis (Bottom -> Top, 0% ~ 100%): Percentage height, creating a true top-left (80%)
     to bottom-right (6%) physical "Cliff Drop" trajectory.
2. Line + Column Combo Trajectory (折線軌跡為主、漸層直柱與斷崖落差帶為輔):
   - Bold drop trajectory line + prominent circular nodes + supporting bars + shaded cliff zone.
3. Single-Hue Chroma/Luminance Gradient Within Panel & Hue Separation Across Panels:
   - Panel A (Macro Readiness Retention Funnel): Royal Blue single-hue sequential gradient.
   - Panel B (Micro Maturity Stage Breakdown): Deep Teal-Ochre single-hue sequential gradient.
   - Connected by a 1+1>2 visual relay bridge.
4. 100% Homogeneous Metric Polarity & Two-Tier 0-Degree Aligned X-Axis Label Blocks:
   - Negative obstacles (46% quality flaw, 57% strategy inaction) are mathematically converted
     into homogeneous positive retention rates (54% quality pass, 43% strategy action) with
     explicit inverse bottleneck annotations.
   - Bottom X-axis uses 0-degree horizontal Tier 1 [4-char Bold Pill] + Tier 2 [2-line parallel description].
"""

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, ConnectionPatch

# Configure CJK Font
matplotlib.rcParams['font.sans-serif'] = [
    'Microsoft JhengHei', 'PingFang TC', 'Noto Sans CJK TC', 'SimHei', 'Arial Unicode MS'
]
matplotlib.rcParams['axes.unicode_minus'] = False


def render_cdo_quantitative_charts(output_path: str):
    fig = plt.figure(figsize=(19.2, 9.8), dpi=300, facecolor='#F8FAFC')

    # GridSpec: Left Panel (7 stages) vs Right Panel (5 stages) sharing identical Y-axis height
    gs = fig.add_gridspec(
        nrows=1, ncols=2,
        width_ratios=[1.35, 1.0],
        left=0.055, right=0.965,
        top=0.80, bottom=0.21,
        wspace=0.15
    )

    ax1 = fig.add_subplot(gs[0, 0], facecolor='#FFFFFF')
    ax2 = fig.add_subplot(gs[0, 1], facecolor='#FFFFFF')

    # =========================================================================
    # TOP MASTER HEADER BANNER (Assertion-Evidence Title + Dual-Panel Guide)
    # =========================================================================
    fig.text(
        0.055, 0.945,
        "2024 全球數據長（CDO）實證調查：80% 商業高調看好 vs. 6% 核心業務投產的「準備度大斷崖」",
        fontsize=17.5, fontweight='bold', color='#0F172A', ha='left', va='top'
    )
    fig.text(
        0.055, 0.902,
        "【XY 軸空間重力折線複合圖】左圖追蹤企業通過 7 道 AI 準備度考驗的「同質正向留存軌跡（皇家藍漸層）」；右圖接力拆解未投產企業停滯於 5 大成熟度階段的「結構分佈（深青綠漸層）」",
        fontsize=11.5, fontweight='bold', color='#334155', ha='left', va='top'
    )

    # Top decorative accent rule
    header_line = plt.Line2D([0.055, 0.965], [0.875, 0.875], transform=fig.transFigure,
                             color='#CBD5E1', linewidth=1.5)
    fig.add_artist(header_line)
    header_accent = plt.Line2D([0.055, 0.28], [0.875, 0.875], transform=fig.transFigure,
                               color='#1E3A8A', linewidth=3.5)
    fig.add_artist(header_accent)

    # =========================================================================
    # PANEL A (LEFT): 7-Stage Homogeneous Positive Retention Cliff (Royal Blue)
    # =========================================================================
    x1 = np.arange(7)
    y1 = np.array([80, 62, 54, 43, 37, 11, 6])

    # Homogeneous Royal Blue Sequential Scale (Dark Rich Blue -> Pale Ice Blue)
    blue_bars = [
        '#1E3A8A',  # 80% Deepest Royal Blue
        '#1D4ED8',  # 62% Strong Royal Blue
        '#2563EB',  # 54% Medium-Deep Blue
        '#3B82F6',  # 43% Primary Blue
        '#60A5FA',  # 37% Sky Blue
        '#93C5FD',  # 11% Light Blue
        '#BFDBFE',  # 6%  Pale Ice Blue
    ]

    # Two-Tier Homogeneous X-Axis Labels (Tier 1: 4-char Pill, Tier 2: 2-line parallel phrase)
    tier1_p1 = [
        "【商業預期】",
        "【預算投入】",
        "【品質過關】",
        "【策略行動】",
        "【基礎信心】",
        "【高度完備】",
        "【核心投產】",
    ]
    tier2_p1 = [
        "看好生成式 AI\n重塑商業環境",
        "計畫於今年度\n擴大 AI 投資",
        "未受困於基礎\n數據品質死穴",
        "已針對 AI 實質\n翻修數據策略",
        "自認具備合格\nAI 數據基礎",
        "強烈同意數據\n已完全準備好",
        "真正部署核心\n業務規模投產",
    ]

    # Subtle shaded cliff area under the trajectory line
    ax1.fill_between(x1, y1, 0, color='#3B82F6', alpha=0.08, zorder=1)

    # Supporting vertical bars with single-hue luminance gradient
    ax1.bar(
        x1, y1, width=0.48, color=blue_bars,
        edgecolor='#1E3A8A', linewidth=1.0, alpha=0.88, zorder=2
    )

    # Shaded Cliff Drop Zone between 80% baseline and trajectory line
    ax1.fill_between(
        x1, 80, y1, color='#EFF6FF', alpha=0.55, hatch='//',
        edgecolor='#BFDBFE', linewidth=0.0, zorder=1
    )
    ax1.plot([0, 6], [80, 80], linestyle='--', color='#64748B', linewidth=1.3, zorder=2)

    # Primary Drop Trajectory Line (Bold Line + Prominent Circular Nodes)
    ax1.plot(
        x1, y1, color='#0F172A', linewidth=3.5, zorder=4
    )
    ax1.plot(
        x1, y1, color='#1E3A8A', linewidth=2.6, marker='o',
        markersize=11, markerfacecolor='#1E3A8A',
        markeredgecolor='#FFFFFF', markeredgewidth=2.2, zorder=5
    )
    # Highlight the final 6% cliff node with a double ring in dark navy
    ax1.plot(
        [6], [6], marker='o', markersize=13,
        markerfacecolor='#0F172A', markeredgecolor='#FFFFFF', markeredgewidth=2.5, zorder=6
    )

    # Direct Percentage Callouts above each node (shifted slightly left on nodes 2 & 3 so callout arrows don't cross text)
    for i, (xi, yi) in enumerate(zip(x1, y1)):
        shift_x = -0.14 if i in (2, 3) else 0.0
        offset_y = 3.2
        ax1.text(
            xi + shift_x, yi + offset_y, f"{yi}%",
            ha='center', va='bottom', fontsize=13, fontweight='bold',
            color='#0F172A' if i < 6 else '#1E3A8A',
            bbox=dict(boxstyle='round,pad=0.16', facecolor='#FFFFFF', edgecolor='none', alpha=0.88),
            zorder=7
        )

    # Inverse Bottleneck Callout Badges for Stage 3 (54% <- 46% obstacle) and Stage 4 (43% <- 57% inaction)
    ax1.annotate(
        "▼ 反面流失：46% 視品質不良為死穴",
        xy=(2.12, 54.5), xytext=(2.42, 69.5),
        ha='center', va='center', fontsize=9.2, fontweight='bold', color='#1E3A8A',
        bbox=dict(boxstyle='round,pad=0.32', facecolor='#EFF6FF', edgecolor='#3B82F6', linewidth=1.2),
        arrowprops=dict(arrowstyle='->', color='#2563EB', lw=1.4, connectionstyle='arc3,rad=-0.15'),
        zorder=8
    )
    ax1.annotate(
        "▼ 反面流失：57% 至今未改數據策略",
        xy=(3.12, 43.5), xytext=(3.62, 58.0),
        ha='center', va='center', fontsize=9.2, fontweight='bold', color='#1E3A8A',
        bbox=dict(boxstyle='round,pad=0.32', facecolor='#EFF6FF', edgecolor='#3B82F6', linewidth=1.2),
        arrowprops=dict(arrowstyle='->', color='#2563EB', lw=1.4, connectionstyle='arc3,rad=-0.15'),
        zorder=8
    )

    # Total Cliff Drop Callout Arrow at x = 6.0 (from 80% down to 6%)
    ax1.annotate(
        "", xy=(6.0, 9.5), xytext=(6.0, 79.2),
        arrowprops=dict(arrowstyle='<->', color='#1E3A8A', lw=2.3, shrinkA=0, shrinkB=0),
        zorder=6
    )
    ax1.annotate(
        "▼ 總斷崖落差 Δ = -74 個百分點\n（80% 商業看好 → 僅 6% 真正規模投產）",
        xy=(6.0, 72.0), xytext=(4.45, 87.5),
        ha='center', va='center', fontsize=10.5, fontweight='bold', color='#FFFFFF',
        bbox=dict(boxstyle='round,pad=0.45', facecolor='#1E3A8A', edgecolor='#0F172A', linewidth=1.5),
        arrowprops=dict(arrowstyle='->', color='#1E3A8A', lw=1.8, connectionstyle='arc3,rad=-0.15'),
        zorder=9
    )

    # Panel A Title Banner
    ax1.set_title(
        "【左圖：企業 AI 準備度留存斷崖】從商業預期到核心投產的 7 階正向留存率（同質單色相漸層）",
        fontsize=12.2, fontweight='bold', color='#0F172A', loc='left', pad=14
    )

    # =========================================================================
    # PANEL B (RIGHT): 5-Stage Maturity Breakdown (Deep Teal Single-Hue Scale)
    # =========================================================================
    x2 = np.arange(5)
    y2 = np.array([33, 21, 19, 16, 6])

    # Homogeneous Deep Teal Sequential Scale (Distinct from Panel A's Royal Blue!)
    teal_bars = [
        '#115E59',  # 33% Deepest Pine Teal
        '#0F766E',  # 21% Rich Teal
        '#0D9488',  # 19% Medium Teal
        '#2DD4BF',  # 16% Mint Teal
        '#99F6E4',  # 6%  Pale Aqua Teal
    ]

    tier1_p2 = [
        "【個人摸索】",
        "【指引規範】",
        "【部門試點】",
        "【防禦禁用】",
        "【核心投產】",
    ]
    tier2_p2 = [
        "員工零星試用\n無企業級專案",
        "剛訂內部守則\n仍在早期探索",
        "局限單一部門\n未跨部門打通",
        "擔憂資安出錯\n下令全面禁用",
        "數據地基打通\n規模創造價值",
    ]

    # Subtle shaded area under Panel B trajectory line
    ax2.fill_between(x2, y2, 0, color='#0D9488', alpha=0.08, zorder=1)

    # Supporting vertical bars in Deep Teal gradient
    ax2.bar(
        x2, y2, width=0.46, color=teal_bars,
        edgecolor='#115E59', linewidth=1.0, alpha=0.88, zorder=2
    )

    # Shaded Grouping Box for the First 3 Early Exploration Stages (33% + 21% + 19% = 73%)
    early_box = FancyBboxPatch(
        (-0.38, 0), 2.76, 48.5,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        facecolor='#F0FDFA', edgecolor='#0D9488', linewidth=1.4, linestyle='--', alpha=0.75, zorder=1
    )
    ax2.add_patch(early_box)
    ax2.text(
        1.0, 43.5,
        "◆ 早期摸索與局部試點合計 Σ = 73%\n（33% 個人試用 + 21% 剛訂指引 + 19% 單一部門試點）",
        ha='center', va='center', fontsize=9.6, fontweight='bold', color='#115E59',
        bbox=dict(boxstyle='round,pad=0.32', facecolor='#CCFBF1', edgecolor='#0F766E', linewidth=1.2),
        zorder=8
    )

    # Primary Trajectory Line for Panel B
    ax2.plot(
        x2, y2, color='#0F172A', linewidth=3.3, zorder=4
    )
    ax2.plot(
        x2, y2, color='#0F766E', linewidth=2.5, marker='o',
        markersize=11, markerfacecolor='#0F766E',
        markeredgecolor='#FFFFFF', markeredgewidth=2.2, zorder=5
    )

    # Direct Percentage Callouts above each node in Panel B
    for i, (xi, yi) in enumerate(zip(x2, y2)):
        ax2.text(
            xi, yi + 3.0, f"{yi}%",
            ha='center', va='bottom', fontsize=13, fontweight='bold',
            color='#115E59' if i < 4 else '#0F172A',
            bbox=dict(boxstyle='round,pad=0.18', facecolor='#FFFFFF', edgecolor='none', alpha=0.85),
            zorder=7
        )

    # Explanatory Synthesis Box in Panel B upper area (matching Y-scale height nicely)
    ax2.text(
        2.15, 78.0,
        "★ 1 + 1 > 2 雙圖接力洞察：\n"
        "左圖顯示 94% 企業未能進入核心投產；\n"
        "右圖進一步拆解這群企業的真實去向：\n"
        "• 73% 停留在個人試用與局部試點\n"
        "• 16% 因畏懼資安與幻覺而全面禁用\n"
        "• 僅 6% 完成雙模數據地基、規模投產",
        ha='center', va='center', fontsize=10.0, fontweight='bold', color='#0F172A',
        linespacing=1.48,
        bbox=dict(boxstyle='round,pad=0.55', facecolor='#F0FDFA', edgecolor='#0F766E', linewidth=1.6),
        zorder=8
    )

    # Panel B Title Banner
    ax2.set_title(
        "【右圖：企業 AI 落地成熟度拆解】未投產企業實際停滯之 5 大階段分佈（跨圖色相區隔）",
        fontsize=12.2, fontweight='bold', color='#0F172A', loc='left', pad=14
    )

    # =========================================================================
    # SHARED Y-AXIS CONFIGURATION & TWO-TIER 0° HORIZONTAL X-AXIS LABELS
    # =========================================================================
    for ax in (ax1, ax2):
        ax.set_ylim(0, 102)
        ax.set_yticks([0, 20, 40, 60, 80, 100])
        ax.set_yticklabels([f"{v}%" for v in [0, 20, 40, 60, 80, 100]], fontsize=10.5, fontweight='bold', color='#475569')
        ax.yaxis.grid(True, linestyle='--', color='#CBD5E1', alpha=0.75, zorder=0)
        ax.xaxis.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#94A3B8')
        ax.spines['bottom'].set_color('#64748B')
        ax.spines['bottom'].set_linewidth(1.4)
        ax.tick_params(axis='x', length=0)  # Hide raw ticks; use custom 2-tier aligned blocks

    ax1.set_ylabel("企業佔比 / 留存率（%）", fontsize=11.5, fontweight='bold', color='#1E293B', labelpad=8)
    ax2.set_ylabel("各階段企業分佈佔比（%）", fontsize=11.5, fontweight='bold', color='#115E59', labelpad=8)

    ax1.set_xlim(-0.55, 6.55)
    ax2.set_xlim(-0.55, 4.55)
    ax1.set_xticks(x1)
    ax1.set_xticklabels([""] * len(x1))
    ax2.set_xticks(x2)
    ax2.set_xticklabels([""] * len(x2))

    # Draw Two-Tier 0-Degree Aligned X-Axis Label Blocks for Panel A
    for xi, t1, t2 in zip(x1, tier1_p1, tier2_p1):
        # Tier 1: Bold 4-character stage pill (100% horizontally aligned at y = -4.8)
        ax1.text(
            xi, -4.8, t1,
            ha='center', va='top', fontsize=10.5, fontweight='bold', color='#1E3A8A',
            clip_on=False
        )
        # Tier 2: 2-line parallel homogeneous description (aligned at y = -10.8)
        ax1.text(
            xi, -10.8, t2,
            ha='center', va='top', fontsize=9.2, color='#334155',
            linespacing=1.32, clip_on=False
        )

    # Draw Two-Tier 0-Degree Aligned X-Axis Label Blocks for Panel B
    for xi, t1, t2 in zip(x2, tier1_p2, tier2_p2):
        ax2.text(
            xi, -4.8, t1,
            ha='center', va='top', fontsize=10.5, fontweight='bold', color='#115E59',
            clip_on=False
        )
        ax2.text(
            xi, -10.8, t2,
            ha='center', va='top', fontsize=9.2, color='#334155',
            linespacing=1.32, clip_on=False
        )

    # Connect Panel A's 6% node to Panel B with a subtle cross-panel ConnectionPatch
    con = ConnectionPatch(
        xyA=(6.15, 6), coordsA=ax1.transData,
        xyB=(-0.42, 33), coordsB=ax2.transData,
        arrowstyle="->,head_width=0.4,head_length=0.4",
        color='#0F766E', linestyle='--', linewidth=1.8,
        connectionstyle="arc3,rad=-0.18", zorder=10
    )
    fig.add_artist(con)

    # =========================================================================
    # BOTTOM METHODOLOGY & HOMOGENEITY FOOTNOTE BANNER
    # =========================================================================
    footer_box = FancyBboxPatch(
        (0.055, 0.022), 0.91, 0.068,
        boxstyle="round,pad=0.008,rounding_size=0.01",
        transform=fig.transFigure,
        facecolor='#F1F5F9', edgecolor='#CBD5E1', linewidth=1.0
    )
    fig.add_artist(footer_box)

    fig.text(
        0.068, 0.064,
        "■ 數據來源與統計同質化換算說明：AWS 與 MIT CDOIQ 合作《2024 全球數據長（CDO）實證調查報告》（樣本數 N = 335 位企業數據長與高階主管）。",
        fontsize=9.8, fontweight='bold', color='#1E293B', ha='left', va='center'
    )
    fig.text(
        0.068, 0.038,
        "• 同質性轉換：為確保左圖 X 軸全數為「正向準備度／留存率」，原文兩項反向障礙指標已依法轉換為互補過關率（100% - 46% 品質死穴 = 54% 品質過關；100% - 57% 未改策略 = 43% 策略行動）。右圖另有 5% 屬其他／未表態。",
        fontsize=9.2, color='#475569', ha='left', va='center'
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[SUCCESS] Generated Format D chart: {output_path}")


if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "03_cdo_survey_quantitative_charts.png")
    render_cdo_quantitative_charts(out_file)
