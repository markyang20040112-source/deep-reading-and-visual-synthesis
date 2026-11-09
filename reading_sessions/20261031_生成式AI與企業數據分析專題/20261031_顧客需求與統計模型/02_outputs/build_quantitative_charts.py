# -*- coding: utf-8 -*-
"""
build_quantitative_charts.py
Format D: 量化實證數據圖表（Quantitative Empirical Charts）
嚴格遵循 phase2_output/quantitative_chart_spec.md 與 scripts/hcl_color_engine.py 規範：
- 鎖定版 Gephi · pastel CIELAB 均衡色盤（主色暖杏橘 #ECA072、次色霧靄青藍 #5DBACD、第三色 #E89BB6、第四色 #8FBA88）
- 配對雙柱與顯式剪刀差落差膠囊（Paired Dual-Bar with Explicit Delta Callouts）
- 底部 X 軸雙層零旋轉標籤（Two-Tier Zero-Tilt Aligned Label Blocks）
- 極簡座標軸去框（despine_axes）
- 零 Emoji 鐵律（微軟正黑體原生符號 ▲, ●, ■, ★）
- 頂部斷言主標題（Assertion-Evidence 模式）與精簡官方資料來源圖註
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# 導入底層 HCL 色彩引擎
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 尋找 deep-reading-and-visual-synthesis 根目錄下的 .agents/skills/deep-reading-and-visual-synthesis/scripts
root_dir = SCRIPT_DIR
while root_dir and os.path.basename(root_dir) != "deep-reading-and-visual-synthesis":
    parent = os.path.dirname(root_dir)
    if parent == root_dir:
        break
    root_dir = parent

SKILLS_SCRIPTS = os.path.join(root_dir, ".agents", "skills", "deep-reading-and-visual-synthesis", "scripts")
if SKILLS_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILLS_SCRIPTS)

from hcl_color_engine import (
    GEPHI_QUALITATIVE_HEX,
    GEPHI_LIGHT_BADGE_TINTS,
    GEPHI_SEQUENTIAL_SCALES,
    despine_axes,
)

FONT_FAMILY = "Microsoft JhengHei"
plt.rcParams["font.family"] = FONT_FAMILY
plt.rcParams["axes.unicode_minus"] = False

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(OUT_DIR, "03_quantitative_empirical_charts.png")


def draw_capsule(ax, x, y, text, color="#0F172A", bg="#F1F5F9", border="#CBD5E1", fontsize=9.0):
    """繪製微型資訊膠囊標籤"""
    bbox_props = dict(boxstyle="round,pad=0.28,rounding_size=0.25", fc=bg, ec=border, lw=0.9)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, weight="bold",
            color=color, bbox=bbox_props, zorder=7)


def build_charts():
    # 擴展畫布高度以提供足夠呼吸空間，杜絕重疊
    fig = plt.figure(figsize=(14.2, 7.4), dpi=300, facecolor="#FFFFFF")
    
    # 頂部大標題與副標題（Assertion-Evidence 模式）
    fig.text(
        0.055, 0.96,
        "顧客需求不靠猜：高管直覺預估與顧客真實價值的巨大剪刀差，以及認知對齊的財務槓桿",
        fontsize=15.5, weight="bold", color="#0F172A", ha="left", va="top"
    )
    fig.text(
        0.055, 0.915,
        "72% 上市 B2B 企業高管直覺與顧客重視事項零或負相關；統計模型揭露真實提升潛力，認知一致度每提高 12.5 分驅動營收 +9.2%、市值 +11.1%",
        fontsize=9.8, color="#475569", ha="left", va="top"
    )

    # 左右雙面板格局：GridSpec（保留底部 0.16 給雙層標籤與圖註，杜絕重疊）
    gs = fig.add_gridspec(1, 2, left=0.055, right=0.955, top=0.84, bottom=0.18, wspace=0.22)
    ax_left = fig.add_subplot(gs[0, 0])
    ax_right = fig.add_subplot(gs[0, 1])

    # =========================================================================
    # 左面板：型態 B 同案雙維反差配對雙柱＋剪刀差落差圖
    # =========================================================================
    categories = [
        "【問題解決】\n24小時內解決問題\n（教育公司服務）",
        "【安全規範】\n現場作業安全履約\n（工業服務公司）",
        "【溝通回饋】\n每週專案進度更新\n（製造商 ITI）",
        "【品質低價】\n規格符合與低報價\n（基本衛生因子門檻）",
    ]
    x = np.arange(len(categories))
    width = 0.30

    # 數據（百分比）
    exec_estimate = [12.5, 2.3, 10.0, 42.0]     # 高管直覺預估重要度/提升感
    cust_actual   = [85.0, 19.5, 48.0, 4.0]      # 顧客實際提升潛力（Lift Potential）

    c_exec = GEPHI_QUALITATIVE_HEX[0]   # 主色暖杏橘 #ECA072 (高管直覺)
    c_cust = GEPHI_QUALITATIVE_HEX[1]   # 次色霧靄藍 #5DBACD (顧客真實)
    c_exec_edge = "#CA6F35"
    c_cust_edge = "#2C8B9F"

    bars1 = ax_left.bar(x - width/2, exec_estimate, width, label="高管直覺預估／均分權重",
                        color=c_exec, edgecolor=c_exec_edge, linewidth=1.1, zorder=3)
    bars2 = ax_left.bar(x + width/2, cust_actual, width, label="統計模型測出之顧客實際提升潛力",
                        color=c_cust, edgecolor=c_cust_edge, linewidth=1.1, zorder=3)

    # 標註柱頂數值
    for bar in bars1:
        h = bar.get_height()
        ax_left.text(bar.get_x() + bar.get_width()/2, h + 1.2, f"{h:.1f}%",
                     ha="center", va="bottom", fontsize=9.0, weight="bold", color=c_exec_edge)
    for bar in bars2:
        h = bar.get_height()
        ax_left.text(bar.get_x() + bar.get_width()/2, h + 1.2, f"{h:.1f}%",
                     ha="center", va="bottom", fontsize=9.0, weight="bold", color=c_cust_edge)

    # 垂直雙向剪刀差標註帶（Explicit Gap Callouts）
    # 案例 0：24小時問題解決（85% vs 12.5% -> Δ = +72.5%）
    ax_left.plot([x[0] - width/2, x[0] + width/2], [12.5, 12.5], color="#94A3B8", linestyle=":", lw=1.2)
    ax_left.annotate("", xy=(x[0] + width/2, 83.5), xytext=(x[0] + width/2, 14.0),
                     arrowprops=dict(arrowstyle="<->", color="#0E5B6B", lw=1.4))
    draw_capsule(ax_left, x[0] + width/2 + 0.02, 48.0, "Δ = +72.5%\n(暴增 6.8 倍)",
                 color="#0E5B6B", bg="#EBF7F9", border="#5DBACD", fontsize=8.0)

    # 案例 1：安全規範（19.5% vs 2.3% -> Δ = +17.2%）
    ax_left.plot([x[1] - width/2, x[1] + width/2], [2.3, 2.3], color="#94A3B8", linestyle=":", lw=1.2)
    ax_left.annotate("", xy=(x[1] + width/2, 18.5), xytext=(x[1] + width/2, 3.2),
                     arrowprops=dict(arrowstyle="<->", color="#0E5B6B", lw=1.4))
    draw_capsule(ax_left, x[1] + width/2 + 0.02, 11.0, "Δ = +17.2%\n(暴增 8.5 倍)",
                 color="#0E5B6B", bg="#EBF7F9", border="#5DBACD", fontsize=8.0)

    # 案例 2：溝通進度（48% vs 10% -> Δ = +38.0%）
    ax_left.plot([x[2] - width/2, x[2] + width/2], [10.0, 10.0], color="#94A3B8", linestyle=":", lw=1.2)
    ax_left.annotate("", xy=(x[2] + width/2, 46.5), xytext=(x[2] + width/2, 11.5),
                     arrowprops=dict(arrowstyle="<->", color="#0E5B6B", lw=1.4))
    draw_capsule(ax_left, x[2] + width/2 + 0.02, 29.0, "Δ = +38.0%\n(核心驅動)",
                 color="#0E5B6B", bg="#EBF7F9", border="#5DBACD", fontsize=8.0)

    # 案例 3：品質低價（4% vs 42% -> 高管嚴重過度高估）
    ax_left.plot([x[3] - width/2, x[3] + width/2], [4.0, 4.0], color="#94A3B8", linestyle=":", lw=1.2)
    ax_left.annotate("", xy=(x[3] - width/2, 40.5), xytext=(x[3] - width/2, 5.2),
                     arrowprops=dict(arrowstyle="<->", color="#97481B", lw=1.4))
    draw_capsule(ax_left, x[3] - width/2 - 0.02, 23.0, "Δ = -38.0%\n(衛生因子陷阱)",
                 color="#97481B", bg="#FFF3EA", border="#ECA072", fontsize=8.0)

    ax_left.set_title("圖 1A｜高階主管直覺預估 vs. 顧客實際提升潛力（雙維反差剪刀差）",
                      fontsize=11.0, weight="bold", color="#0F172A", pad=12)
    ax_left.set_ylabel("價值重要性 / 統計提升潛力（Lift %）", fontsize=9.2, color="#334155")
    ax_left.set_xticks(x)
    ax_left.set_xticklabels(categories, fontsize=8.4, linespacing=1.25)
    ax_left.tick_params(axis="x", pad=6)
    ax_left.set_ylim(0, 100)
    despine_axes(ax_left, grid_axis="y")
    ax_left.legend(loc="upper left", frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=8.4)

    # =========================================================================
    # 右面板：認知對齊帶來的財務槓桿與市值回報（由大到小排序長條圖）
    # =========================================================================
    metrics = [
        "【企業市值增幅】\n資本市場長期信心回報",
        "【營業收入增加】\n客戶持續回購與擴大採購",
        "【自由現金流提升】\n造血引擎充裕營運現金",
        "【毛利率實質改善】\n具定價權、擺脫價格血拼",
    ]
    # 依幅度由大至小排列（由上而下視覺自然）
    returns = [11.1, 9.2, 8.8, 5.2]
    # y 軸位置：4, 3, 2, 1
    y_pos = np.array([3.6, 2.6, 1.6, 0.6])

    # 使用循序藍色階（高值深、低值淺）
    bar_colors = ["#0E5B6B", "#2C8B9F", "#5DBACD", "#8ED4E2"]
    edge_colors = ["#0A3E49", "#1B5D6B", "#2C8B9F", "#4FAABF"]
    label_colors = ["#0A3E49", "#1B5D6B", "#2C8B9F", "#1B5D6B"]  # 確保在白底上對比度 >= 4.5:1

    bars_r = ax_right.barh(y_pos, returns, height=0.55, color=bar_colors, edgecolor=edge_colors,
                           linewidth=1.1, zorder=3)

    for i, (bar, val) in enumerate(zip(bars_r, returns)):
        w = bar.get_width()
        ax_right.text(w + 0.32, bar.get_y() + bar.get_height()/2, f"+{val:.1f}%",
                      ha="left", va="center", fontsize=10.0, weight="bold", color=label_colors[i])

    ax_right.set_title("圖 1B｜認知一致度每提升 12.5 分（量表 -100~+100）之財務槓桿",
                       fontsize=11.0, weight="bold", color="#0F172A", pad=12)
    ax_right.set_xlabel("公司財務與市場指標平均成長率（%）", fontsize=9.2, color="#334155")
    ax_right.set_yticks(y_pos)
    ax_right.set_yticklabels(metrics, fontsize=8.6, linespacing=1.25)
    ax_right.tick_params(axis="y", pad=6)
    ax_right.set_ylim(-1.3, 4.4)
    ax_right.set_xlim(0, 14.5)
    despine_axes(ax_right, grid_axis="x")

    # 在右圖右下方空檔區（y < 0.3 無任何長條覆蓋）放置落地成效卡
    card_text = (
        "★ 實證案例 4 年落地總體回報：\n"
        "● ITI Manufacturing：進度報告由 <30次 增至 3,524次，\n"
        "  釋放 30%+ 工時，股價上漲 +162%（vs. 標普 34%、羅素 8%）\n"
        "● S-SET 流體經銷：報價時間 18hr 縮至 <3hr，人均銷售 +52%\n"
        "● 800 億美元銀行：滿意度 +18%，營收 +33%，股價 +200%"
    )
    ax_right.text(
        0.98, 0.05, card_text,
        transform=ax_right.transAxes,
        ha="right", va="bottom",
        fontsize=7.8, linespacing=1.35,
        color="#1E293B",
        bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.15", fc="#F8FAFC", ec="#CBD5E1", lw=0.9)
    )

    # 底部精簡官方資料來源圖註（安全放在 y=0.035，杜絕與 X 軸重疊）
    fig.text(
        0.055, 0.038,
        "資料來源：V. Mittal, A. Piazza, S. Singh & A. Malshe (2025), 'Do You Know What Your Customers Value?', Harvard Business Review.\n"
        "涵蓋範圍：104 家上市 B2B 企業及其 18,840 名顧客之 10-K 財報自然語言分析與雙層統計模型驗證；涵蓋期間 1999–2024 年。",
        fontsize=7.8, color="#64748B", ha="left", va="bottom", linespacing=1.3
    )

    plt.savefig(OUT_PATH, dpi=300, facecolor="#FFFFFF")
    plt.close(fig)
    print("Quantitative empirical chart successfully saved:", OUT_PATH)


if __name__ == "__main__":
    build_charts()
