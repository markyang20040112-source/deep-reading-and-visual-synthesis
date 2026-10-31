"""
plot_quantitative_charts.py
Generates executive-grade quantitative chart following Mackinlay (1986), Tufte (1983), Few (2012), and Knaflic (2015).
Article source: Thomas H. Davenport & Priyanka Tiwari (MIT Sloan / AWS, N=334 CDOs).
"""

import matplotlib.pyplot as plt
import numpy as np

# Font configuration
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "PingFang TC", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7.5), dpi=220)
fig.patch.set_facecolor("#F8FAFC")

# -------------------------------------------------------------
# Panel 1: CDO 認知落差與數據準備度赤字 (Perception vs. Reality Gap)
# -------------------------------------------------------------
ax1.set_facecolor("#F8FAFC")
metrics = [
    "認為生成式 AI 將徹底重構商業環境",
    "更重視從其他傳統數據方案獲取價值",
    "計畫增加生成式 AI 研發與專案支出",
    "至今未對企業數據策略做任何修改",
    "視「數據品質不良」為最大落地挑戰",
    "自認已具備適合新一代 AI 數據基礎",
    "強烈同意自家數據基礎已完全準備好"
]
values = [80, 71, 62, 57, 46, 37, 11]
# Highlight colors: High contrast, preattentive spotlight
colors = [
    "#3B82F6",  # 80% Blue hype
    "#F59E0B",  # 71% Amber hesitation
    "#60A5FA",  # 62% Light blue budget
    "#EF4444",  # 57% Red inertia
    "#DC2626",  # 46% Dark Red bottleneck
    "#94A3B8",  # 37% Grey
    "#64748B"   # 11% Slate grey reality
]

y_pos = np.arange(len(metrics))
bars = ax1.barh(y_pos, values, color=colors, height=0.62, edgecolor="none", zorder=3)

# Value annotations directly on bars
for bar, val in zip(bars, values):
    ax1.text(val + 1.5, bar.get_y() + bar.get_height()/2.0, f"{val}%",
             va="center", ha="left", fontsize=11, fontweight="bold", color="#1E293B")

ax1.set_yticks(y_pos)
ax1.set_yticklabels(metrics, fontsize=10.5, color="#1E293B", fontweight="medium")
ax1.invert_yaxis()  # top-down
ax1.set_xlim(0, 95)
ax1.set_xlabel("數據長 (CDO) 受訪比例 (%)", fontsize=10, color="#64748B", labelpad=8)
ax1.set_title("【痛點診斷】80% 熱潮 vs. 11% 準備度：企業數據赤字鴻溝", 
              fontsize=13.5, fontweight="bold", color="#0F172A", pad=16, loc="left")

# Grid & spines
ax1.grid(axis="x", linestyle="--", alpha=0.35, color="#CBD5E1", zorder=1)
for spine in ["top", "right", "left"]:
    ax1.spines[spine].set_visible(False)
ax1.spines["bottom"].set_color("#CBD5E1")

# -------------------------------------------------------------
# Panel 2: 企業落地成熟度分佈 (Enterprise Adoption & Production Gap)
# -------------------------------------------------------------
ax2.set_facecolor("#F8FAFC")
stages = [
    "個人層級自主嘗試 (無企業案例)",
    "訂定使用指引但仍在摸索",
    "部門或事業單位層級試點 (POC)",
    "下令全面禁止員工使用 (安全顧慮)",
    "★ 正式投入核心業務生產環境 (Production)"
]
stage_vals = [33, 21, 19, 16, 6]
stage_colors = [
    "#94A3B8",  # 33% Slate
    "#CBD5E1",  # 21% Light grey
    "#38BDF8",  # 19% Sky blue
    "#F87171",  # 16% Red ban
    "#10B981"   # 6% Emerald Green (Production spotlight)
]

y_pos2 = np.arange(len(stages))
bars2 = ax2.barh(y_pos2, stage_vals, color=stage_colors, height=0.58, edgecolor="none", zorder=3)

for bar, val in zip(bars2, stage_vals):
    weight = "bold" if val == 6 else "normal"
    textColor = "#047857" if val == 6 else "#1E293B"
    ax2.text(val + 1.2, bar.get_y() + bar.get_height()/2.0, f"{val}%",
             va="center", ha="left", fontsize=11, fontweight=weight, color=textColor)

ax2.set_yticks(y_pos2)
ax2.set_yticklabels(stages, fontsize=10.5, color="#1E293B", fontweight="medium")
ax2.invert_yaxis()
ax2.set_xlim(0, 42)
ax2.set_xlabel("受訪企業佔比 (%)", fontsize=10, color="#64748B", labelpad=8)
ax2.set_title("【成熟度分佈】僅 6% 真正進入生產環境：試點到落地的斷崖", 
              fontsize=13.5, fontweight="bold", color="#0F172A", pad=16, loc="left")

ax2.grid(axis="x", linestyle="--", alpha=0.35, color="#CBD5E1", zorder=1)
for spine in ["top", "right", "left"]:
    ax2.spines[spine].set_visible(False)
ax2.spines["bottom"].set_color("#CBD5E1")

# Subtitle / Footer
plt.suptitle("MIT Sloan & AWS 數據長 (CDO) 調查實證：企業生成式 AI 準備度全景 ($N=334$)",
             fontsize=15, fontweight="bold", color="#0F172A", y=0.98)
plt.figtext(0.5, 0.02, 
            "資料來源：Thomas H. Davenport & Priyanka Tiwari, 《你的公司數據真的準備好面對生成式 AI 了嗎？》 (MIT Sloan Review)",
            ha="center", fontsize=9.5, color="#64748B")

plt.tight_layout(rect=[0.02, 0.05, 0.98, 0.94])

out_path = "reading_sessions/20261101_企業數據與生成式AI準備度/02_outputs/03_cdo_survey_quantitative_charts.png"
plt.savefig(out_path, dpi=220, bbox_inches="tight")
print(f"Chart saved to {out_path}")
