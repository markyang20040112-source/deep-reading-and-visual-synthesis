# -*- coding: utf-8 -*-
"""
generate_perfect_step2_figures.py
Generates / prepares all 5 figures with publication quality, high resolution (300 DPI),
large legible typography (Word-equivalent 9.5pt~12pt), and tight borders:
- Fig 1: Dual-panel 7-stage retention waterfall (80% -> 6%) + 5-stage maturity breakdown
- Fig 2: Brain architecture diagram (cropped tightly from source)
- Fig 3: Real empirical confounding price sensitivity curve (Human 79%->35%->4% vs AI 67%->64%->62%)
- Fig 4: Customer value lift potential & financial leverage (cropped tightly to eliminate whitespace)
- Fig 5: Customer-Company-Investor ecosystem mindmap (cropped tightly to eliminate whitespace)
"""

import os
import shutil
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, ConnectionPatch

matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'PingFang TC', 'Noto Sans CJK TC', 'DFKai-SB', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False

BASE_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩"
ASSETS_DIR = os.path.join(BASE_DIR, "assets_原始素材與圖表")
os.makedirs(ASSETS_DIR, exist_ok=True)


def generate_figure1():
    out_path = os.path.join(ASSETS_DIR, "fig1_cdo_dual_panel.png")
    fig = plt.figure(figsize=(13.6, 8.2), dpi=300, facecolor='#FFFFFF')
    gs = fig.add_gridspec(
        nrows=1, ncols=2,
        width_ratios=[1.38, 1.0],
        left=0.065, right=0.975,
        top=0.83, bottom=0.25,
        wspace=0.18
    )

    ax1 = fig.add_subplot(gs[0, 0], facecolor='#FFFFFF')
    ax2 = fig.add_subplot(gs[0, 1], facecolor='#FFFFFF')

    # Master Header
    fig.text(0.065, 0.955, '2024 全球數據長（CDO）實證調查：80% 商業期望 vs. 6% 核心投產之「準備度大斷崖」',
             fontsize=17.5, fontweight='bold', color='#0F172A', ha='left', va='top')
    fig.text(0.065, 0.902, '【XY 軸重力折線圖】左圖：企業通往核心投產之 7 階正向留存軌跡 │ 右圖：未投產企業停滯於 5 大成熟度階段結構分布',
             fontsize=12, fontweight='bold', color='#334155', ha='left', va='top')

    # Decorative line
    header_line = plt.Line2D([0.065, 0.975], [0.875, 0.875], transform=fig.transFigure, color='#CBD5E1', linewidth=1.5)
    fig.add_artist(header_line)
    header_accent = plt.Line2D([0.065, 0.32], [0.875, 0.875], transform=fig.transFigure, color='#1E3A8A', linewidth=3.5)
    fig.add_artist(header_accent)

    # ---------------- Left Panel ----------------
    x1 = np.arange(7)
    y1 = np.array([80, 62, 54, 43, 37, 11, 6])
    blue_bars = ['#1E3A8A', '#1D4ED8', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE']
    tier1_p1 = ['【商業預期】', '【預算投入】', '【品質過關】', '【策略行動】', '【基礎信心】', '【高度完備】', '【核心投產】']
    tier2_p1 = ['看好生成式 AI\n重塑商業環境', '計畫於今年度\n擴大 AI 投資', '未受困於基礎\n數據品質死穴',
                '已針對 AI 實施\n翻修數據策略', '自認具備合格\nAI 數據基盤', '強烈同意數據\n已完全準備好', '真正部署核心\n業務規模投產']

    ax1.fill_between(x1, y1, 0, color='#3B82F6', alpha=0.08, zorder=1)
    ax1.bar(x1, y1, width=0.48, color=blue_bars, edgecolor='#1E3A8A', linewidth=1.0, alpha=0.88, zorder=2)
    ax1.fill_between(x1, 80, y1, color='#EFF6FF', alpha=0.55, hatch='//', edgecolor='#BFDBFE', linewidth=0.0, zorder=1)
    ax1.plot([0, 6], [80, 80], linestyle='--', color='#64748B', linewidth=1.3, zorder=2)

    ax1.plot(x1, y1, color='#0F172A', linewidth=3.5, zorder=4)
    ax1.plot(x1, y1, color='#1E3A8A', linewidth=2.6, marker='o', markersize=12,
             markerfacecolor='#1E3A8A', markeredgecolor='#FFFFFF', markeredgewidth=2.2, zorder=5)
    ax1.plot([6], [6], marker='o', markersize=14, markerfacecolor='#0F172A', markeredgecolor='#FFFFFF', markeredgewidth=2.5, zorder=6)

    for i, (xi, yi) in enumerate(zip(x1, y1)):
        shift_x = -0.15 if i in (2, 3) else 0.0
        offset_y = 3.5
        ax1.text(xi + shift_x, yi + offset_y, f'{yi}%', ha='center', va='bottom', fontsize=14, fontweight='bold',
                 color='#0F172A' if i < 6 else '#1E3A8A',
                 bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='none', alpha=0.88), zorder=7)

    ax1.annotate('▼ 反面死穴：46% 視品質不良為死穴', xy=(2.12, 54.5), xytext=(2.45, 69.5),
                 ha='center', va='center', fontsize=10.5, fontweight='bold', color='#1E3A8A',
                 bbox=dict(boxstyle='round,pad=0.32', facecolor='#EFF6FF', edgecolor='#3B82F6', linewidth=1.2),
                 arrowprops=dict(arrowstyle='->', color='#2563EB', lw=1.5, connectionstyle='arc3,rad=-0.15'), zorder=8)

    ax1.annotate('▼ 反面死穴：57% 至今未改數據策略', xy=(3.12, 43.5), xytext=(3.65, 58.0),
                 ha='center', va='center', fontsize=10.5, fontweight='bold', color='#1E3A8A',
                 bbox=dict(boxstyle='round,pad=0.32', facecolor='#EFF6FF', edgecolor='#3B82F6', linewidth=1.2),
                 arrowprops=dict(arrowstyle='->', color='#2563EB', lw=1.5, connectionstyle='arc3,rad=-0.15'), zorder=8)

    ax1.annotate('', xy=(6.0, 9.5), xytext=(6.0, 79.2),
                 arrowprops=dict(arrowstyle='<->', color='#1E3A8A', lw=2.3, shrinkA=0, shrinkB=0), zorder=6)
    ax1.annotate('▼ 總斷崖落差 Δ = -74 個百分點\n（80% 商業看好 → 僅 6% 真正規模投產）',
                 xy=(6.0, 72.0), xytext=(4.35, 87.5),
                 ha='center', va='center', fontsize=11.5, fontweight='bold', color='#FFFFFF',
                 bbox=dict(boxstyle='round,pad=0.45', facecolor='#1E3A8A', edgecolor='#0F172A', linewidth=1.5),
                 arrowprops=dict(arrowstyle='->', color='#1E3A8A', lw=1.8, connectionstyle='arc3,rad=-0.15'), zorder=9)

    ax1.set_title('【左圖：企業 AI 準備度留存斷崖】7 階正向留存率（同質單色相漸層）',
                  fontsize=13, fontweight='bold', color='#0F172A', loc='left', pad=12)

    # ---------------- Right Panel ----------------
    x2 = np.arange(5)
    y2 = np.array([33, 21, 19, 16, 6])
    teal_bars = ['#115E59', '#0F766E', '#0D9488', '#2DD4BF', '#99F6E4']
    tier1_p2 = ['【個人摸索】', '【指引規範】', '【部門試點】', '【防禦禁用】', '【核心投產】']
    tier2_p2 = ['員工零星試用\n無企業級專案', '剛訂內部守則\n仍在早期探索', '局限單一部門\n未跨部門打通',
                '擔憂資安出錯\n下令全面禁用', '數據地基打通\n規模創造價值']

    ax2.fill_between(x2, y2, 0, color='#0D9488', alpha=0.08, zorder=1)
    ax2.bar(x2, y2, width=0.46, color=teal_bars, edgecolor='#115E59', linewidth=1.0, alpha=0.88, zorder=2)

    early_box = FancyBboxPatch((-0.38, 0), 2.76, 52.0, boxstyle='round,pad=0.02,rounding_size=0.15',
                               facecolor='#F0FDFA', edgecolor='#0D9488', linewidth=1.4, linestyle='--', alpha=0.75, zorder=1)
    ax2.add_patch(early_box)
    ax2.text(1.0, 46.5, '◆ 早期摸索與局部試點合計 Σ = 73%\n（33% 個人試用 + 21% 剛訂指引 + 19% 單一部門試點）',
             ha='center', va='center', fontsize=10.5, fontweight='bold', color='#115E59',
             bbox=dict(boxstyle='round,pad=0.32', facecolor='#CCFBF1', edgecolor='#0F766E', linewidth=1.2), zorder=8)

    ax2.plot(x2, y2, color='#0F172A', linewidth=3.3, zorder=4)
    ax2.plot(x2, y2, color='#0F766E', linewidth=2.5, marker='o', markersize=12,
             markerfacecolor='#0F766E', markeredgecolor='#FFFFFF', markeredgewidth=2.2, zorder=5)

    for i, (xi, yi) in enumerate(zip(x2, y2)):
        ax2.text(xi, yi + 3.2, f'{yi}%', ha='center', va='bottom', fontsize=14, fontweight='bold',
                 color='#115E59' if i < 4 else '#0F172A',
                 bbox=dict(boxstyle='round,pad=0.18', facecolor='#FFFFFF', edgecolor='none', alpha=0.85), zorder=7)

    ax2.text(2.15, 78.5,
             '★ 1 + 1 > 2 雙圖接力洞察：\n'
             '左圖顯示 94% 企業未能進入核心投產；\n'
             '右圖進一步拆解這群企業的真實去向：\n'
             '• 73% 停留在個人試用與局部試點\n'
             '• 16% 因畏懼資安與幻覺而全面禁用\n'
             '• 僅 6% 完成雙模數據地基、規模投產',
             ha='center', va='center', fontsize=11, fontweight='bold', color='#0F172A', linespacing=1.45,
             bbox=dict(boxstyle='round,pad=0.55', facecolor='#F0FDFA', edgecolor='#0F766E', linewidth=1.6), zorder=8)

    ax2.set_title('【右圖：企業 AI 落地成熟度拆解】未投產企業 5 大階段分布',
                  fontsize=13, fontweight='bold', color='#0F172A', loc='left', pad=12)

    # Shared axes config
    for ax in (ax1, ax2):
        ax.set_ylim(0, 102)
        ax.set_yticks([0, 20, 40, 60, 80, 100])
        ax.set_yticklabels([f'{v}%' for v in [0, 20, 40, 60, 80, 100]], fontsize=12, fontweight='bold', color='#475569')
        ax.yaxis.grid(True, linestyle='--', color='#CBD5E1', alpha=0.75, zorder=0)
        ax.xaxis.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#94A3B8')
        ax.spines['bottom'].set_color('#64748B')
        ax.spines['bottom'].set_linewidth(1.4)
        ax.tick_params(axis='x', length=0)

    ax1.set_ylabel('企業佔比 / 留存率（%）', fontsize=12.5, fontweight='bold', color='#1E293B', labelpad=8)
    ax2.set_ylabel('各階段企業分布佔比（%）', fontsize=12.5, fontweight='bold', color='#115E59', labelpad=8)

    ax1.set_xlim(-0.55, 6.55)
    ax2.set_xlim(-0.55, 4.55)
    ax1.set_xticks(x1)
    ax1.set_xticklabels([''] * len(x1))
    ax2.set_xticks(x2)
    ax2.set_xticklabels([''] * len(x2))

    # X-axis label blocks
    for xi, t1, t2 in zip(x1, tier1_p1, tier2_p1):
        ax1.text(xi, -5.5, t1, ha='center', va='top', fontsize=12, fontweight='bold', color='#1E3A8A', clip_on=False)
        ax1.text(xi, -11.8, t2, ha='center', va='top', fontsize=10.5, color='#334155', linespacing=1.3, clip_on=False)

    for xi, t1, t2 in zip(x2, tier1_p2, tier2_p2):
        ax2.text(xi, -5.5, t1, ha='center', va='top', fontsize=12, fontweight='bold', color='#115E59', clip_on=False)
        ax2.text(xi, -11.8, t2, ha='center', va='top', fontsize=10.5, color='#334155', linespacing=1.3, clip_on=False)

    # Cross panel connector
    con = ConnectionPatch(xyA=(6.15, 6), coordsA=ax1.transData, xyB=(-0.42, 33), coordsB=ax2.transData,
                          arrowstyle='->,head_width=0.45,head_length=0.45', color='#0F766E', linestyle='--', linewidth=2.0,
                          connectionstyle='arc3,rad=-0.18', zorder=10)
    fig.add_artist(con)

    # Footer banner
    footer_box = FancyBboxPatch((0.065, 0.02), 0.91, 0.065, boxstyle='round,pad=0.008,rounding_size=0.01',
                                transform=fig.transFigure, facecolor='#F1F5F9', edgecolor='#CBD5E1', linewidth=1.0)
    fig.add_artist(footer_box)

    fig.text(0.075, 0.058, '■ 數據來源與說明：AWS 與 MIT CDOIQ《2024 全球數據長（CDO）實證調查報告》（樣本數 N = 335 位企業數據長與高階主管）。',
             fontsize=10.5, fontweight='bold', color='#1E293B', ha='left', va='center')
    fig.text(0.075, 0.032, '• 同質性轉換說明：為確保左圖 X 軸全數為正向留存率，反向障礙已依法轉換為互補過關率（100%-46%=54% 品質過關；100%-57%=43% 策略行動）。右圖另有 5% 屬其他/未表態。',
             fontsize=9.8, color='#475569', ha='left', va='center')

    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Fig 1 generated:", out_path)


def generate_figure2():
    src_path = os.path.join(ASSETS_DIR, "AI資料整理大腦架構圖.jpg")
    out_path = os.path.join(ASSETS_DIR, "fig2_brain_architecture.png")
    im = Image.open(src_path)
    # Tight crop (Bounding box: left=8, top=2, right=2177, bottom=1306)
    im_cropped = im.crop((8, 2, 2177, 1306))
    im_cropped.save(out_path, quality=95)
    print("Fig 2 cropped and saved:", out_path)


def generate_figure3():
    out_path = os.path.join(ASSETS_DIR, "fig3_price_sensitivity_confounding.png")
    fig, ax = plt.subplots(figsize=(10.5, 6.2), dpi=300)
    fig.subplots_adjust(left=0.09, right=0.96, top=0.75, bottom=0.12)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    prices_pts = np.array([1000, 3000, 5000])
    human_pts = np.array([79, 35, 4])
    ai_pts = np.array([67, 64, 62])

    prices_smooth = np.linspace(1000, 5000, 200)
    human_smooth = 88.0 / (1.0 + np.exp(0.00135 * (prices_smooth - 2650)))
    ai_smooth = 67.0 - 5.0 * ((prices_smooth - 1000.0) / 4000.0)

    # Shaded gap
    ax.fill_between(prices_smooth, human_smooth, ai_smooth, color='#FEE2E2', alpha=0.35, zorder=2)

    # Curves
    ax.plot(prices_smooth, human_smooth, color='#1D4ED8', lw=3.2, zorder=3,
            label='真實消費者盲測（正常價格彈性：價格提高，購買意願自 79% 暴跌至 4%）')
    ax.plot(prices_smooth, ai_smooth, color='#BE123C', lw=3.2, linestyle='--', zorder=3,
            label='AI 模擬受訪者（發生「混淆」偏誤：腦補物價同漲，意願凍結於 67%~62% 幾無彈性）')

    # Data points
    for px, py_h, py_a in zip(prices_pts, human_pts, ai_pts):
        ax.scatter([px], [py_h], color='#1D4ED8', s=80, zorder=5)
        ax.scatter([px], [py_a], color='#BE123C', s=80, marker='s', zorder=5)

    # Value callout badges
    ax.text(1000, 79 + 4.0, '79%', ha='center', va='bottom', fontsize=12.5, fontweight='bold', color='#1D4ED8',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#EFF6FF', edgecolor='#93C5FD', lw=1.2, alpha=0.95), zorder=6)
    ax.text(1000, 67 - 5.0, '67%', ha='center', va='top', fontsize=12.5, fontweight='bold', color='#BE123C',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#FFF1F2', edgecolor='#FECDD3', lw=1.2, alpha=0.95), zorder=6)

    ax.text(3000, 64 + 4.0, '64%', ha='center', va='bottom', fontsize=12.5, fontweight='bold', color='#BE123C',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#FFF1F2', edgecolor='#FECDD3', lw=1.2, alpha=0.95), zorder=6)
    ax.text(3000, 35 - 5.0, '35%', ha='center', va='top', fontsize=12.5, fontweight='bold', color='#1D4ED8',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#EFF6FF', edgecolor='#93C5FD', lw=1.2, alpha=0.95), zorder=6)

    ax.text(5000, 62 + 4.0, '62%', ha='center', va='bottom', fontsize=12.5, fontweight='bold', color='#BE123C',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#FFF1F2', edgecolor='#FECDD3', lw=1.2, alpha=0.95), zorder=6)
    ax.text(5000, 4 + 4.0, '4%', ha='center', va='bottom', fontsize=12.5, fontweight='bold', color='#1D4ED8',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#EFF6FF', edgecolor='#93C5FD', lw=1.2, alpha=0.95), zorder=6)

    # Reflective Callout Boxes
    bbox_ai_box = dict(boxstyle='round,pad=0.5', fc='#FFF1F2', ec='#BE123C', lw=1.5)
    ax.text(3750, 80, '【AI 語境腦補「混淆」陷阱】\n大模型誤設外部通膨等情境物價齊漲，\n導致價格上漲 5 倍時購買意願僅降 5%！',
            ha='center', va='center', fontsize=11, fontweight='bold', color='#9F1239', bbox=bbox_ai_box, zorder=6)

    bbox_human_box = dict(boxstyle='round,pad=0.5', fc='#EFF6FF', ec='#1D4ED8', lw=1.5)
    ax.text(1850, 20, '【真實消費者價格敏感度】\n符合微觀經濟學第一性原理（負斜率需求）：\n高價位（5,000 元）購買意願銳減至 4%（重挫 -95%）',
            ha='center', va='center', fontsize=11, fontweight='bold', color='#1E40AF', bbox=bbox_human_box, zorder=6)

    # Formatting
    ax.set_xlim(700, 5300)
    ax.set_ylim(-3, 102)
    ax.set_xticks([1000, 2000, 3000, 4000, 5000])
    ax.set_xticklabels(['$ 1,000', '$ 2,000', '$ 3,000', '$ 4,000', '$ 5,000'], fontsize=12, fontweight='bold', color='#0F172A')
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_yticklabels(['0%', '20%', '40%', '60%', '80%', '100%'], fontsize=12, fontweight='bold', color='#0F172A')
    ax.set_xlabel('測試產品定價 (新台幣 / 美元)', fontsize=12.5, fontweight='bold', color='#334155', labelpad=8)
    ax.set_ylabel('購買意願機率 (%)', fontsize=12.5, fontweight='bold', color='#334155', labelpad=8)
    ax.grid(True, linestyle=':', alpha=0.6, color='#CBD5E1', zorder=1)

    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.spines['left'].set_color('#94A3B8')
    ax.spines['bottom'].set_color('#94A3B8')

    ax.legend(loc='lower left', bbox_to_anchor=(0.0, 1.02), frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=10.5)

    fig.text(0.09, 0.965, '市場研究實證：真實消費者 vs. AI 模擬受訪者之價格敏感度混淆實驗',
             fontsize=15, fontweight='bold', color='#1E3A8A', ha='left', va='top')
    fig.text(0.09, 0.915, '因果推論實證對照：AI 腦補物價同漲導致需求曲線平坦失靈，與微觀經濟學客觀規律嚴重脫節',
             fontsize=11, color='#64748B', ha='left', va='top')

    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Fig 3 generated:", out_path)


def generate_figure4():
    src_path = r"reading_sessions\20261031_生成式AI與企業數據分析專題\20261031_顧客需求與統計模型\02_outputs\03_quantitative_empirical_charts.png"
    out_path = os.path.join(ASSETS_DIR, "fig4_customer_value_gap.png")
    im = Image.open(src_path).convert('RGB')
    # Tight crop: content bbox is (78, 91, 4071, 2131)
    im_cropped = im.crop((70, 80, 4080, 2140))
    im_cropped.save(out_path, quality=95)
    print("Fig 4 cropped and saved:", out_path)


def generate_figure5():
    src_path = os.path.join(ASSETS_DIR, "04_顧客-企業-投資者關係心智圖_橫版.png")
    out_path = os.path.join(ASSETS_DIR, "fig5_ecosystem_mindmap.png")
    im = Image.open(src_path).convert('RGB')
    # Tight crop: content bbox is (176, 110, 4624, 2695)
    im_cropped = im.crop((170, 105, 4630, 2700))
    im_cropped.save(out_path, quality=95)
    print("Fig 5 cropped and saved:", out_path)


if __name__ == "__main__":
    generate_figure1()
    generate_figure2()
    generate_figure3()
    generate_figure4()
    generate_figure5()
    print("All 5 figures generated / cropped successfully!")
