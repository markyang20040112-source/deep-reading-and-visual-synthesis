# -*- coding: utf-8 -*-
"""
build_quantitative_charts.py
Generates scientific quantitative charts (Format D) based on the newly evolved
quantitative_chart_spec.md and the Dynamic Tri-Axial Visual Decision Engine.

1. chart_demand_curve_confounding.png:
   - Data Form: Paired response curves (Price X vs Purchase Probability Y).
   - Story Intent: Diverging Tension / Mechanism Breakdown (True Random Blind vs AI Hallucination).
   - Style: Tufte high data-ink ratio, Direct Labeling on lines, HCL Blue (#425A80) vs Rose (#8A3E56).

2. chart_gbk_ai_adoption.png:
   - Data Form: Ranked percentages across market research tasks (GBK Collective 170-expert survey).
   - Story Intent: Comparison & Ranking + Knaflic 80/20 Spotlight.
   - Style: Horizontal bar chart, direct value labels, HCL Spotlight.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

SCRIPT_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\.agents\skills\deep-reading-and-visual-synthesis\scripts"
sys.path.insert(0, SCRIPT_DIR)

from hcl_color_engine import GLOBAL_COLOR_CONTRACT

OUT_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI顛覆市場研究\02_outputs"
os.makedirs(OUT_DIR, exist_ok=True)

# Font setup for Windows Microsoft JhengHei
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False


def generate_demand_curve_chart():
    """Generates the Paired Coordinate Demand Curves demonstrating Confounding."""
    fig, ax = plt.subplots(figsize=(6.4, 4.4), dpi=260)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")

    # X axis: Test Price from 1,000 to 5,000
    prices = np.linspace(1000, 5000, 100)
    
    # Human Blind Test: Standard downward sloping demand curve
    # 85% at 1000 down to 15% at 5000
    y_human = 0.88 / (1.0 + np.exp(0.0013 * (prices - 2700)))
    
    # AI Confounded: Flat demand curve hovering at ~65%
    y_ai = 0.67 - 0.05 * ((prices - 1000) / 4000.0)

    c_blue = GLOBAL_COLOR_CONTRACT.blue.accent_dark  # #425A80
    c_rose = GLOBAL_COLOR_CONTRACT.rose.accent_dark  # #8A3E56

    # Plot lines with smooth linewidth
    ax.plot(prices, y_human * 100, color=c_blue, lw=3.2, label="真人隨機盲測 (do(X))")
    ax.plot(prices, y_ai * 100, color=c_rose, lw=3.2, linestyle="--", label="AI 語境腦補混淆 (P_LLM)")

    # Data markers at key points
    pts_x = [1000, 3000, 5000]
    for px in pts_x:
        # Human
        py_h = float(0.88 / (1.0 + np.exp(0.0013 * (px - 2700)))) * 100
        ax.scatter([px], [py_h], color=c_blue, s=55, zorder=5)
        ax.text(px, py_h - 6.5, f"{py_h:.0f}%", fontsize=9.2, fontweight="bold", color=c_blue, ha="center")
        
        # AI
        py_a = float(0.67 - 0.05 * ((px - 1000) / 4000.0)) * 100
        ax.scatter([px], [py_a], color=c_rose, s=55, zorder=5)
        ax.text(px, py_a + 4.0, f"{py_a:.0f}%", fontsize=9.2, fontweight="bold", color=c_rose, ha="center")

    # Direct Labeling at curve tails (Tufte / Knaflic rule: zero separate legend)
    ax.text(4950, 12.0, "● 真人隨機盲測 P(Y|do(X))\n  [價格彈性正常：貴了不買]",
            fontsize=9.5, fontweight="bold", color=c_blue, ha="right", va="bottom")
    ax.text(4950, 69.5, "● AI 語境腦補混淆 P_LLM(Y|X)\n  [需求曲線平坦失真：腦補物價同漲]",
            fontsize=9.5, fontweight="bold", color=c_rose, ha="right", va="bottom")

    # Tufte decluttering: remove top/right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CBD5E1")
    ax.spines["bottom"].set_color("#CBD5E1")

    # Gridlines: subtle horizontal only
    ax.yaxis.grid(True, linestyle=":", alpha=0.55, color="#CBD5E1")
    ax.xaxis.grid(False)

    ax.set_xlim(800, 5200)
    ax.set_ylim(0, 100)
    ax.set_xticks([1000, 2000, 3000, 4000, 5000])
    ax.set_xticklabels(["$1,000", "$2,000", "$3,000", "$4,000", "$5,000"], fontsize=10, color="#334155")
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=10, color="#334155")

    ax.set_xlabel("測試產品標價 X (測試價格)", fontsize=10.5, fontweight="bold", color="#0F172A", labelpad=8)
    ax.set_ylabel("購買意願率 Y (%)", fontsize=10.5, fontweight="bold", color="#0F172A", labelpad=8)

    ax.set_title("因果推論實證對照：定價需求曲線失靈機制",
                 fontsize=12.2, fontweight="bold", color="#0F172A", pad=12, ha="center")

    out_file = os.path.join(OUT_DIR, "chart_demand_curve_confounding.png")
    plt.tight_layout()
    fig.savefig(out_file, dpi=260, facecolor="#F8FAFC")
    plt.close(fig)
    print(f"[OK] Generated Quantitative Chart: {out_file}")


def generate_gbk_adoption_chart():
    """Generates the Horizontal Ranked Bar Chart with 80/20 Spotlight."""
    fig, ax = plt.subplots(figsize=(6.4, 4.4), dpi=260)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")

    tasks = [
        "純合成數據極高價值認同",
        "撰寫市調報告與視覺化",
        "編碼與量化數據分析",
        "統整訪談文字逐字稿",
        "★ 釋放策略敘事時間",
    ]
    vals = [31, 54, 58, 62, 80]
    
    c_blue = GLOBAL_COLOR_CONTRACT.blue.accent_dark  # #425A80 (Spotlight)
    c_rose = GLOBAL_COLOR_CONTRACT.rose.accent_dark  # #8A3E56 (Alert)
    c_muted = "#94A3B8"                              # Neutral Slate for non-focal

    colors = [c_rose, c_muted, c_muted, c_muted, c_blue]

    y_pos = np.arange(len(tasks))
    bars = ax.barh(y_pos, vals, color=colors, height=0.55, edgecolor="none", zorder=3)

    # Direct Labeling at bar ends
    for i, (v, bar) in enumerate(zip(vals, bars)):
        color = colors[i]
        suffix = " (僅31%認同獨立價值)" if i == 0 else (" (80%+ 核心痛點破局)" if i == 4 else "")
        ax.text(v + 1.8, bar.get_y() + bar.get_height() / 2.0, f"{v}%{suffix}",
                fontsize=9.5, fontweight="bold", color=color, va="center")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#CBD5E1")

    ax.xaxis.grid(True, linestyle=":", alpha=0.55, color="#CBD5E1", zorder=1)
    ax.yaxis.grid(False)

    ax.set_xlim(0, 105)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(tasks, fontsize=10.2, fontweight="bold", color="#0F172A")
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=10, color="#475569")

    ax.set_title("GBK 實證調查：生成式 AI 市調任務滲透與價值認同",
                 fontsize=12.0, fontweight="bold", color="#0F172A", pad=12, ha="center")

    out_file = os.path.join(OUT_DIR, "chart_gbk_ai_adoption.png")
    plt.tight_layout()
    fig.savefig(out_file, dpi=260, facecolor="#F8FAFC")
    plt.close(fig)
    print(f"[OK] Generated Quantitative Chart: {out_file}")


if __name__ == "__main__":
    generate_demand_curve_chart()
    generate_gbk_adoption_chart()
