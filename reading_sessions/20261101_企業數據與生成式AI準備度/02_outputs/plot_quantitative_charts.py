"""
plot_quantitative_charts.py
Generates executive-grade quantitative chart following:
- Tufte (1983): Zero Lie Factor (LF = 1.0), Unified Common Scale [0, 100]
- Cleveland & McGill (1984): Position along common scale for maximum perceptual accuracy
- Knaflic (2015) & Schwabish (2021): Expectation vs. Reality narrative tension & preattentive spotlight
Article source: Thomas H. Davenport & Priyanka Tiwari (MIT Sloan / AWS, N=334 CDOs).
"""

import matplotlib.pyplot as plt
import numpy as np

# Font configuration
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "PingFang TC", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 7.8), dpi=240)
fig.patch.set_facecolor("#F8FAFC")

# ------------------------------------------------------------------------------
# PANEL 1: 【主觀預期 vs. 客觀現實】認知剪刀差 (Unified Scale 0 - 100%)
# ------------------------------------------------------------------------------
ax1.set_facecolor("#F8FAFC")

metrics1 = [
    "【預期】認為生成式 AI 將徹底重構商業環境",
    "【預算】計畫增加生成式 AI 研發與專案支出",
    "【撞牆】視「數據品質不良」為首要落地死穴",
    "【躺平】至今未對企業數據策略做任何修改",
    "【防守】自認已具備適合新一代 AI 數據基礎",
    "【警惕】強烈同意自家數據基礎已完全準備好",
    "★【真理】已正式部署至核心業務生產環境"
]
values1 = [80, 62, 46, 57, 37, 11, 6]

colors1 = [
    "#2563EB",  # 80% Expectation Hype (Royal Blue)
    "#38BDF8",  # 62% Budget flow (Sky Blue)
    "#DC2626",  # 46% Data Quality Wall (Crimson Red)
    "#EA580C",  # 57% Strategy Freeze (Deep Amber)
    "#94A3B8",  # 37% Moderate agree (Slate)
    "#64748B",  # 11% Strong agree (Dark Slate)
    "#10B981"   # 6% Reality: Production (Emerald Green Spotlight)
]

y_pos1 = np.arange(len(metrics1))
bars1 = ax1.barh(y_pos1, values1, color=colors1, height=0.58, edgecolor="none", zorder=3)

for bar, val in zip(bars1, values1):
    weight = "bold"
    textColor = "#047857" if val == 6 else ("#B91C1C" if val in [46, 57] else "#1E293B")
    ax1.text(val + 1.8, bar.get_y() + bar.get_height()/2.0, f"{val}%",
             va="center", ha="left", fontsize=11.5, fontweight=weight, color=textColor)

ax1.set_yticks(y_pos1)
ax1.set_yticklabels(metrics1, fontsize=10.8, color="#1E293B", fontweight="medium")
ax1.invert_yaxis()
ax1.set_xlim(0, 100)  # UNIFIED SCALE 0-100% (Tufte Lie Factor = 1.0)
ax1.set_xlabel("數據長 (CDO) 受訪比例 (%) — 基準軸 [0 - 100%]", fontsize=10.5, color="#64748B", labelpad=8)
ax1.set_title("【預期 vs. 現實剪刀差】80% 熱潮跌落至 6% 生產之巨大鴻溝", 
              fontsize=13.8, fontweight="bold", color="#0F172A", pad=16, loc="left")

ax1.grid(axis="x", linestyle="--", alpha=0.4, color="#CBD5E1", zorder=1)
for spine in ["top", "right", "left"]:
    ax1.spines[spine].set_visible(False)
ax1.spines["bottom"].set_color("#CBD5E1")


# ------------------------------------------------------------------------------
# PANEL 2: 【企業落地成熟度漏斗】Adoption Funnel (Unified Scale 0 - 100%)
# ------------------------------------------------------------------------------
ax2.set_facecolor("#F8FAFC")

stages = [
    "① 個人層級自主嘗試 (無企業案例)",
    "② 訂定使用指引但仍在摸索階段",
    "③ 部門或事業單位層級試點 (POC)",
    "④ 下令全面禁止員工使用 (安全顧慮)",
    "★ ⑤ 正式投入核心業務生產環境 (Production)"
]
stage_vals = [33, 21, 19, 16, 6]

stage_colors = [
    "#64748B",  # 33% Individual (Slate)
    "#94A3B8",  # 21% Guidelines (Light Slate)
    "#0284C7",  # 19% Dept POC (Blue)
    "#EF4444",  # 16% Corporate Ban (Red)
    "#059669"   # 6% Core Production (Emerald Green Spotlight)
]

y_pos2 = np.arange(len(stages))
bars2 = ax2.barh(y_pos2, stage_vals, color=stage_colors, height=0.58, edgecolor="none", zorder=3)

for bar, val in zip(bars2, stage_vals):
    weight = "bold" if val == 6 else "normal"
    textColor = "#047857" if val == 6 else "#1E293B"
    ax2.text(val + 1.8, bar.get_y() + bar.get_height()/2.0, f"{val}%",
             va="center", ha="left", fontsize=11.5, fontweight=weight, color=textColor)

ax2.set_yticks(y_pos2)
ax2.set_yticklabels(stages, fontsize=10.8, color="#1E293B", fontweight="medium")
ax2.invert_yaxis()
ax2.set_xlim(0, 100)  # UNIFIED SCALE 0-100% (Identical to Panel 1)
ax2.set_xlabel("受訪企業佔比 (%) — 基準軸 [0 - 100%]", fontsize=10.5, color="#64748B", labelpad=8)
ax2.set_title("【落地成熟度漏斗】僅 6% 跨越生產鴻溝：未治理地基引發的停滯", 
              fontsize=13.8, fontweight="bold", color="#0F172A", pad=16, loc="left")

ax2.grid(axis="x", linestyle="--", alpha=0.4, color="#CBD5E1", zorder=1)
for spine in ["top", "right", "left"]:
    ax2.spines[spine].set_visible(False)
ax2.spines["bottom"].set_color("#CBD5E1")


# ------------------------------------------------------------------------------
# SUPER TITLE & TUFTE DATA-INK ANNOTATION
# ------------------------------------------------------------------------------
plt.suptitle("MIT Sloan & AWS 數據長 (CDO) 調查實證：統一尺度下的企業 AI 數據赤字全景 ($N=334$)",
             fontsize=15.5, fontweight="bold", color="#0F172A", y=0.98)
plt.figtext(0.5, 0.02, 
            "★ Tufte 謊言因子嚴格防護 (Lie Factor ≡ 1.00)：左右兩面板共享完全相同之 0~100% 物理座標軸，視覺長度即真實比例。資料來源：Davenport & Tiwari (MIT Sloan)",
            ha="center", fontsize=9.8, color="#475569")

plt.tight_layout(rect=[0.01, 0.05, 0.99, 0.93])

out_path = "reading_sessions/20261101_企業數據與生成式AI準備度/02_outputs/03_cdo_survey_quantitative_charts.png"
plt.savefig(out_path, dpi=240, bbox_inches="tight")
print(f"[OK] High-narrative chart with unified scale saved to: {out_path}")
