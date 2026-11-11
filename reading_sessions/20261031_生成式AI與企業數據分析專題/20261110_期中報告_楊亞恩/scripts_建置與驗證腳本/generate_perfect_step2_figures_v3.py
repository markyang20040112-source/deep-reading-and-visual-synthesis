# -*- coding: utf-8 -*-
"""
generate_perfect_step2_figures_v3.py
High-impact, PPT-grade executive visual assets for 楊亞恩.docx:
- Fig 1: CDO 7-stage Waterfall & 5-stage Maturity (Widened, spacious, zero clipping, large readable fonts)
- Fig 2: Brain Architecture (Left-to-Right 3-pillar PPT card pipeline: Left Brain -> Right Brain -> Frontal Lobe -> Feedback Loop)
- Fig 3: Market Research Price Sensitivity Confounding Curve (Preserved empirical data, balanced margins)
- Fig 4: Customer Value Gap & Financial Leverage (Extra wide, large bold bars, high-contrast delta capsules, big case study cards)
- Fig 5: Customer-Company-Investor Ecosystem Loop (Left-to-Right PPT 3-pillar cards + 3 failure warning cards, ZERO text overlap, large readable fonts)
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, ConnectionPatch

matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'PingFang TC', 'Noto Sans CJK TC', 'DFKai-SB', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False

BASE_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩"
ASSETS_DIR = os.path.join(BASE_DIR, "assets_原始素材與圖表")
os.makedirs(ASSETS_DIR, exist_ok=True)


# =============================================================================
# FIGURE 1: CDO 7-STAGE RETENTION WATERFALL & 5-STAGE MATURITY BREAKDOWN
# Canvas: 16.0 x 8.0, with left=0.085 to prevent y-axis label clipping
# =============================================================================
def generate_figure1():
    out_path = os.path.join(ASSETS_DIR, "fig1_cdo_dual_panel.png")
    fig = plt.figure(figsize=(16.0, 8.0), dpi=300, facecolor='#FFFFFF')
    gs = fig.add_gridspec(
        nrows=1, ncols=2,
        width_ratios=[1.35, 1.0],
        left=0.085, right=0.970,
        top=0.81, bottom=0.22,
        wspace=0.25
    )

    ax1 = fig.add_subplot(gs[0, 0], facecolor='#FFFFFF')
    ax2 = fig.add_subplot(gs[0, 1], facecolor='#FFFFFF')

    # Master Header
    fig.text(0.085, 0.955, '2024 全球數據長（CDO）實證調查：80% 商業期望 vs. 6% 核心投產之「準備度大斷崖」',
             fontsize=20, fontweight='bold', color='#0F172A', ha='left', va='top')
    fig.text(0.085, 0.900, '【雙面板對照分析】左圖：企業通往核心投產之 7 階正向留存軌跡 │ 右圖：未投產企業停滯於 5 大成熟度階段結構分布',
             fontsize=14, fontweight='bold', color='#334155', ha='left', va='top')

    # Decorative line
    header_line = plt.Line2D([0.085, 0.970], [0.865, 0.865], transform=fig.transFigure, color='#CBD5E1', linewidth=1.5)
    fig.add_artist(header_line)
    header_accent = plt.Line2D([0.085, 0.38], [0.865, 0.865], transform=fig.transFigure, color='#1E3A8A', linewidth=3.5)
    fig.add_artist(header_accent)

    # ---------------- Left Panel: 7-Stage Retention Waterfall ----------------
    x1 = np.arange(7)
    y1 = np.array([80, 62, 54, 43, 37, 11, 6])
    blue_bars = ['#1E3A8A', '#1D4ED8', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE']
    tier1_p1 = ['【商業預期】', '【預算投入】', '【品質過關】', '【策略行動】', '【基礎信心】', '【高度完備】', '【核心投產】']
    tier2_p1 = ['看好生成式 AI\n重塑商業環境', '計畫於今年度\n擴大 AI 投資', '未受困於基礎\n數據品質死穴',
                '已針對 AI 實施\n翻修數據策略', '自認具備合格\nAI 數據基盤', '強烈同意數據\n已完全準備好', '真正部署核心\n業務規模投產']

    ax1.fill_between(x1, y1, 0, color='#3B82F6', alpha=0.08, zorder=1)
    ax1.bar(x1, y1, width=0.52, color=blue_bars, edgecolor='#1E3A8A', linewidth=1.2, alpha=0.90, zorder=2)
    ax1.fill_between(x1, 80, y1, color='#EFF6FF', alpha=0.50, hatch='//', edgecolor='#BFDBFE', linewidth=0.0, zorder=1)
    ax1.plot([0, 6], [80, 80], linestyle='--', color='#64748B', linewidth=1.4, zorder=2)

    ax1.plot(x1, y1, color='#0F172A', linewidth=3.6, zorder=4)
    ax1.plot(x1, y1, color='#1E3A8A', linewidth=2.8, marker='o', markersize=13,
             markerfacecolor='#1E3A8A', markeredgecolor='#FFFFFF', markeredgewidth=2.4, zorder=5)
    ax1.plot([6], [6], marker='o', markersize=15, markerfacecolor='#0F172A', markeredgecolor='#FFFFFF', markeredgewidth=2.6, zorder=6)

    for i, (xi, yi) in enumerate(zip(x1, y1)):
        shift_x = -0.10 if i in (2, 3) else 0.0
        offset_y = 3.8
        ax1.text(xi + shift_x, yi + offset_y, f'{yi}%', ha='center', va='bottom', fontsize=16, fontweight='bold',
                 color='#0F172A' if i < 6 else '#1E3A8A',
                 bbox=dict(boxstyle='round,pad=0.20', facecolor='#FFFFFF', edgecolor='none', alpha=0.92), zorder=7)

    ax1.annotate('▼ 反面死穴：46% 視品質不良為死穴', xy=(2.12, 54.5), xytext=(2.45, 70.0),
                 ha='center', va='center', fontsize=12, fontweight='bold', color='#1E3A8A',
                 bbox=dict(boxstyle='round,pad=0.35', facecolor='#EFF6FF', edgecolor='#3B82F6', linewidth=1.3),
                 arrowprops=dict(arrowstyle='->', color='#2563EB', lw=1.6, connectionstyle='arc3,rad=-0.15'), zorder=8)

    ax1.annotate('▼ 反面死穴：57% 至今未改數據策略', xy=(3.12, 43.5), xytext=(3.65, 59.0),
                 ha='center', va='center', fontsize=12, fontweight='bold', color='#1E3A8A',
                 bbox=dict(boxstyle='round,pad=0.35', facecolor='#EFF6FF', edgecolor='#3B82F6', linewidth=1.3),
                 arrowprops=dict(arrowstyle='->', color='#2563EB', lw=1.6, connectionstyle='arc3,rad=-0.15'), zorder=8)

    ax1.annotate('', xy=(6.0, 9.5), xytext=(6.0, 79.2),
                 arrowprops=dict(arrowstyle='<->', color='#1E3A8A', lw=2.4, shrinkA=0, shrinkB=0), zorder=6)
    ax1.annotate('▼ 總斷崖落差 Δ = -74 個百分點\n（80% 商業看好 → 僅 6% 真正規模投產）',
                 xy=(6.0, 72.0), xytext=(4.30, 88.0),
                 ha='center', va='center', fontsize=13, fontweight='bold', color='#FFFFFF',
                 bbox=dict(boxstyle='round,pad=0.48', facecolor='#1E3A8A', edgecolor='#0F172A', linewidth=1.5),
                 arrowprops=dict(arrowstyle='->', color='#1E3A8A', lw=2.0, connectionstyle='arc3,rad=-0.15'), zorder=9)

    ax1.set_title('【左圖：企業 AI 準備度留存斷崖】7 階正向留存率（同質單色相漸層）',
                   fontsize=15, fontweight='bold', color='#0F172A', loc='left', pad=14)

    # ---------------- Right Panel: 5-Stage Maturity Breakdown ----------------
    x2 = np.arange(5)
    y2 = np.array([33, 21, 19, 16, 6])
    teal_bars = ['#115E59', '#0F766E', '#0D9488', '#2DD4BF', '#99F6E4']
    tier1_p2 = ['【個人摸索】', '【指引規範】', '【部門試點】', '【防禦禁用】', '【核心投產】']
    tier2_p2 = ['員工零星試用\n無企業級專案', '剛訂內部守則\n仍在早期探索', '局限單一部門\n未跨部門打通',
                '擔憂資安出錯\n下令全面禁用', '數據地基打通\n規模創造價值']

    ax2.fill_between(x2, y2, 0, color='#0D9488', alpha=0.08, zorder=1)
    ax2.bar(x2, y2, width=0.50, color=teal_bars, edgecolor='#115E59', linewidth=1.2, alpha=0.90, zorder=2)

    early_box = FancyBboxPatch((-0.38, 0), 2.76, 52.0, boxstyle='round,pad=0.02,rounding_size=0.15',
                               facecolor='#F0FDFA', edgecolor='#0D9488', linewidth=1.5, linestyle='--', alpha=0.75, zorder=1)
    ax2.add_patch(early_box)
    ax2.text(1.0, 46.5, '◆ 早期摸索與局部試點合計 Σ = 73%\n（33% 個人試用 + 21% 剛訂指引 + 19% 單一部門試點）',
             ha='center', va='center', fontsize=12, fontweight='bold', color='#115E59',
             bbox=dict(boxstyle='round,pad=0.35', facecolor='#CCFBF1', edgecolor='#0F766E', linewidth=1.3), zorder=8)

    ax2.plot(x2, y2, color='#0F172A', linewidth=3.4, zorder=4)
    ax2.plot(x2, y2, color='#0F766E', linewidth=2.6, marker='o', markersize=13,
             markerfacecolor='#0F766E', markeredgecolor='#FFFFFF', markeredgewidth=2.4, zorder=5)

    for i, (xi, yi) in enumerate(zip(x2, y2)):
        ax2.text(xi, yi + 3.4, f'{yi}%', ha='center', va='bottom', fontsize=16, fontweight='bold',
                 color='#115E59' if i < 4 else '#0F172A',
                 bbox=dict(boxstyle='round,pad=0.20', facecolor='#FFFFFF', edgecolor='none', alpha=0.88), zorder=7)

    ax2.text(2.15, 78.5,
             '★ 1 + 1 > 2 雙圖接力洞察：\n'
             '左圖顯示 94% 企業未能進入核心投產；\n'
             '右圖進一步拆解這群企業的真實去向：\n'
             '• 73% 停留在個人試用與局部試點\n'
             '• 16% 因畏懼資安與幻覺而全面禁用\n'
             '• 僅 6% 完成雙模數據地基、規模投產',
             ha='center', va='center', fontsize=12.5, fontweight='bold', color='#0F172A', linespacing=1.45,
             bbox=dict(boxstyle='round,pad=0.55', facecolor='#F0FDFA', edgecolor='#0F766E', linewidth=1.6), zorder=8)

    ax2.set_title('【右圖：企業 AI 落地成熟度拆解】未投產企業 5 大階段分布',
                   fontsize=15, fontweight='bold', color='#0F172A', loc='left', pad=14)

    # Shared axes styling
    for ax in (ax1, ax2):
        ax.set_ylim(0, 102)
        ax.set_yticks([0, 20, 40, 60, 80, 100])
        ax.set_yticklabels([f'{v}%' for v in [0, 20, 40, 60, 80, 100]], fontsize=13, fontweight='bold', color='#475569')
        ax.yaxis.grid(True, linestyle='--', color='#CBD5E1', alpha=0.75, zorder=0)
        ax.xaxis.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#94A3B8')
        ax.spines['bottom'].set_color('#64748B')
        ax.spines['bottom'].set_linewidth(1.4)
        ax.tick_params(axis='x', length=0)

    ax1.set_ylabel('企業佔比 / 留存率（%）', fontsize=14, fontweight='bold', color='#1E293B', labelpad=10)
    ax2.set_ylabel('各階段企業分布佔比（%）', fontsize=14, fontweight='bold', color='#115E59', labelpad=10)

    ax1.set_xlim(-0.55, 6.55)
    ax2.set_xlim(-0.55, 4.55)
    ax1.set_xticks(x1)
    ax1.set_xticklabels([''] * len(x1))
    ax2.set_xticks(x2)
    ax2.set_xticklabels([''] * len(x2))

    # X-axis labels
    for xi, t1, t2 in zip(x1, tier1_p1, tier2_p1):
        ax1.text(xi, -5.5, t1, ha='center', va='top', fontsize=13, fontweight='bold', color='#1E3A8A', clip_on=False)
        ax1.text(xi, -12.5, t2, ha='center', va='top', fontsize=11.5, color='#334155', linespacing=1.3, clip_on=False)

    for xi, t1, t2 in zip(x2, tier1_p2, tier2_p2):
        ax2.text(xi, -5.5, t1, ha='center', va='top', fontsize=13, fontweight='bold', color='#115E59', clip_on=False)
        ax2.text(xi, -12.5, t2, ha='center', va='top', fontsize=11.5, color='#334155', linespacing=1.3, clip_on=False)

    # Cross panel connector
    con = ConnectionPatch(xyA=(6.15, 6), coordsA=ax1.transData, xyB=(-0.42, 33), coordsB=ax2.transData,
                          arrowstyle='->,head_width=0.45,head_length=0.45', color='#0F766E', linestyle='--', linewidth=2.2,
                          connectionstyle='arc3,rad=-0.18', zorder=10)
    fig.add_artist(con)

    # Footer banner
    footer_box = FancyBboxPatch((0.085, 0.02), 0.885, 0.065, boxstyle='round,pad=0.008,rounding_size=0.01',
                                transform=fig.transFigure, facecolor='#F1F5F9', edgecolor='#CBD5E1', linewidth=1.0)
    fig.add_artist(footer_box)

    fig.text(0.095, 0.058, '■ 數據來源與說明：AWS 與 MIT CDOIQ《2024 全球數據長（CDO）實證調查報告》（樣本數 N = 335 位企業數據長與高階主管）。',
             fontsize=11.5, fontweight='bold', color='#1E293B', ha='left', va='center')
    fig.text(0.095, 0.032, '• 同質性轉換說明：為確保左圖 X 軸全數為正向留存率，反向障礙已依法轉換為互補過關率（100%-46%=54% 品質過關；100%-57%=43% 策略行動）。右圖另有 5% 屬其他/未表態。',
             fontsize=10.5, color='#475569', ha='left', va='center')

    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Fig 1 generated successfully:", out_path)


# =============================================================================
# FIGURE 2: BRAIN ARCHITECTURE (LEFT-TO-RIGHT PPT 3-PILLAR PIPELINE)
# Canvas: 16.0 x 8.8, generous card spacing, zero subtitle overlap, large bold fonts
# =============================================================================
def generate_figure2():
    out_path = os.path.join(ASSETS_DIR, "fig2_brain_architecture.png")
    fig = plt.figure(figsize=(16.0, 8.8), dpi=300, facecolor='#FFFFFF')
    ax = fig.add_axes([0, 0, 1, 1], facecolor='#FFFFFF')
    ax.set_xlim(0, 16.0)
    ax.set_ylim(0, 8.8)
    ax.axis('off')

    # Master Header
    ax.text(0.60, 8.45, "人機協同數據治理大腦架構：剛性左腦 → 靈活右腦 → 前額葉人類專家防線",
            fontsize=21, fontweight='bold', color='#0F172A', ha='left', va='top')
    ax.text(0.60, 8.00, "【水平流水線導向】AI 承接 90% 海量運算，數據辭典約束語義邊界，人類專家仲裁極端案例並動態反哺擴充",
            fontsize=13.5, fontweight='bold', color='#475569', ha='left', va='top')

    # Accent line
    ax.plot([0.60, 15.40], [7.75, 7.75], color='#CBD5E1', lw=1.5)
    ax.plot([0.60, 4.80], [7.75, 7.75], color='#1E3A8A', lw=3.8)

    # 3 Horizontal Cards (Left -> Middle -> Right)
    card_y = 1.25
    card_h = 6.25
    card_w = 4.45
    gap = 0.72
    x_left = 0.60
    x_mid = x_left + card_w + gap
    x_right = x_mid + card_w + gap

    def draw_pillar_card(x, y, w, h, bg_color, border_color, badge_txt, badge_bg,
                         title, subtitle, bullets, foot_pill, foot_bg, foot_color):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=0.18",
                             facecolor=bg_color, edgecolor=border_color, linewidth=2.2, zorder=2)
        ax.add_patch(box)

        # Badge
        badge = FancyBboxPatch((x + 0.28, y + h - 0.52), 2.35, 0.40, boxstyle="round,pad=0.0,rounding_size=0.08",
                               facecolor=badge_bg, edgecolor='none', zorder=3)
        ax.add_patch(badge)
        ax.text(x + 1.45, y + h - 0.32, badge_txt, ha='center', va='center',
                fontsize=13, fontweight='bold', color='#FFFFFF', zorder=4)

        # Title & Subtitle (with generous vertical separation)
        ax.text(x + 0.28, y + h - 0.95, title, ha='left', va='center',
                fontsize=18, fontweight='bold', color='#0F172A', zorder=3)
        ax.text(x + 0.28, y + h - 1.35, subtitle, ha='left', va='center',
                fontsize=12.5, color='#475569', zorder=3)

        # Bullets: first box starts safely below subtitle!
        bullet_start_y = y + h - 2.15
        for i, (b_title, b_desc) in enumerate(bullets):
            by = bullet_start_y - i * 0.85
            b_box = FancyBboxPatch((x + 0.24, by - 0.12), w - 0.48, 0.72, boxstyle="round,pad=0.0,rounding_size=0.08",
                                   facecolor='#FFFFFF', edgecolor=border_color, linewidth=1.1, alpha=0.95, zorder=3)
            ax.add_patch(b_box)
            ax.text(x + 0.38, by + 0.36, b_title, ha='left', va='center',
                    fontsize=13.0, fontweight='bold', color=border_color, zorder=4)
            ax.text(x + 0.38, by + 0.10, b_desc, ha='left', va='center',
                    fontsize=11.5, color='#334155', linespacing=1.2, zorder=4)

        # Footer Pill
        foot = FancyBboxPatch((x + 0.24, y + 0.22), w - 0.48, 0.48, boxstyle="round,pad=0.0,rounding_size=0.08",
                              facecolor=foot_bg, edgecolor=border_color, linewidth=1.3, zorder=3)
        ax.add_patch(foot)
        ax.text(x + w / 2, y + 0.46, foot_pill, ha='center', va='center',
                fontsize=12.2, fontweight='bold', color=foot_color, zorder=4)

    # 1. Left Card: 剛性左腦（數據辭典）
    draw_pillar_card(
        x=x_left, y=card_y, w=card_w, h=card_h,
        bg_color='#F0F7FF', border_color='#1E3A8A',
        badge_txt='■ 規範約束核心', badge_bg='#1E3A8A',
        title='剛性左腦（數據辭典）',
        subtitle='結構化秩序與第一性原理規則錨點',
        bullets=[
            ('• 極端案例與例外歷史處置庫', '沉澱過往邊界條件、特殊業務處理紀錄與例外邏輯'),
            ('• 專有名詞同義詞庫與標準定義', '打通跨部門術語壁壘，消除業務語義混淆歧義'),
            ('• 資料清洗與入庫規範規格書', '提供非結構化輸入與結構化輸出的明確數據格式'),
            ('• 約束大模型運算邊界', '從源頭建立確定性地基，徹底掐滅 AI 幻覺謬誤')
        ],
        foot_pill='【核心定位】AI 必須遵守的第一性原理地基',
        foot_bg='#EFF6FF', foot_color='#1E3A8A'
    )

    # 2. Middle Card: 靈活右腦（大語言模型）
    draw_pillar_card(
        x=x_mid, y=card_y, w=card_w, h=card_h,
        bg_color='#FAF5FF', border_color='#7C3AED',
        badge_txt='◆ 高能運算引擎', badge_bg='#7C3AED',
        title='靈活右腦（AI 大模型）',
        subtitle='高維語義轉譯與低成本海量處理',
        bullets=[
            ('• 非結構化圖文資料高速解析', '秒級自海量合約、PDF、日誌中提取關鍵語義實體'),
            ('• 半結構化日誌格式快速規整', '遵循左腦辭典規範，自動完成結構化打標與轉換'),
            ('• 常態化海量數據高速清洗', '以極低邊際成本承接 90% 繁重、重複之數據洪流'),
            ('• 潛在關聯性挖掘與假設生成', '提供跨維度關聯猜想，輔助人類進行多維度分析')
        ],
        foot_pill='【核心定位】極速承接數據洪流的倍增引擎',
        foot_bg='#F3E8FF', foot_color='#6D28D9'
    )

    # 3. Right Card: 前額葉（人類專家最後防線）
    draw_pillar_card(
        x=x_right, y=card_y, w=card_w, h=card_h,
        bg_color='#FFF1F2', border_color='#DC2626',
        badge_txt='★ 戰略仲裁防線', badge_bg='#DC2626',
        title='前額葉（人類專家防線）',
        subtitle='直覺審查、價值仲裁與戰略反思',
        bullets=[
            ('• 審查極端與未知邊界個案', '專門處置未納入左腦辭典之新型罕見突變個案'),
            ('• 識別突發市場信號與商業突變', '敏銳捕捉無法量化、涉及人性與合約倫理之轉折'),
            ('• 承擔最終決策與合約倫理責任', '仲裁 AI 疑義與邊界衝突，守護合規與商業信譽'),
            ('• 動態反哺與知識沈澱回饋', '將專家仲裁經驗規格化，反哺沉澱至「左腦」庫存')
        ],
        foot_pill='【核心定位】預防致命風險、賦予適應彈性之核心',
        foot_bg='#FEE2E2', foot_color='#991B1B'
    )

    # Connecting Arrows (Left -> Middle -> Right)
    # Arrow 1: Left to Middle
    ax.annotate('', xy=(x_mid - 0.06, 4.75), xytext=(x_left + card_w + 0.06, 4.75),
                arrowprops=dict(arrowstyle="->,head_width=0.45,head_length=0.60", color='#1D4ED8', lw=3.2), zorder=5)
    bbox_p1 = dict(boxstyle="round,pad=0.28", fc="#EFF6FF", ec="#1D4ED8", lw=1.3)
    ax.text((x_left + card_w + x_mid) / 2, 5.25, "規則錨定\n規格約束", ha='center', va='center',
            fontsize=12.2, fontweight='bold', color='#1D4ED8', bbox=bbox_p1, zorder=6)

    # Arrow 2: Middle to Right
    ax.annotate('', xy=(x_right - 0.06, 4.75), xytext=(x_mid + card_w + 0.06, 4.75),
                arrowprops=dict(arrowstyle="->,head_width=0.45,head_length=0.60", color='#7C3AED', lw=3.2), zorder=5)
    bbox_p2 = dict(boxstyle="round,pad=0.28", fc="#FAF5FF", ec="#7C3AED", lw=1.3)
    ax.text((x_mid + card_w + x_right) / 2, 5.25, "疑難個案\n異常上報", ha='center', va='center',
            fontsize=12.2, fontweight='bold', color='#6D28D9', bbox=bbox_p2, zorder=6)

    # Bottom Feedback Loop Arrow (Right -> Left)
    style = "arc3,rad=-0.08"
    arrowprops_feedback = dict(arrowstyle="->,head_width=0.55,head_length=0.75",
                               connectionstyle=style, color="#DC2626", lw=2.8, ls='--')
    ax.annotate('', xy=(x_left + card_w / 2, card_y - 0.06), xytext=(x_right + card_w / 2, card_y - 0.06),
                arrowprops=arrowprops_feedback, zorder=5)

    bbox_feed = dict(boxstyle="round,pad=0.42,rounding_size=0.12", fc="#FFF1F2", ec="#DC2626", lw=1.5)
    ax.text(8.0, 0.62,
            "★ 動態反哺與持續進化迴路：人類專家將仲裁經驗轉化為新規則，回饋擴充「剛性左腦數據辭典」，使系統越用越聰明、疆界持續擴張",
            ha='center', va='center', fontsize=12.8, fontweight='bold', color='#991B1B',
            bbox=bbox_feed, zorder=6)

    # Footer note
    ax.text(8.0, 0.16,
            "■ 三位一體定律：無 AI 則人類無法面對數據洪流；無人類則 AI 遭遇邊界即崩潰；無辭典則 AI 產出充斥幻覺。三者缺一不可。",
            ha='center', va='center', fontsize=11.5, color='#475569', zorder=6)

    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Fig 2 generated successfully:", out_path)


# =============================================================================
# FIGURE 3: PRICE SENSITIVITY CONFOUNDING (PRESERVED & CENTERING BALANCED)
# Canvas: 12.0 x 6.5, balanced margins
# =============================================================================
def generate_figure3():
    out_path = os.path.join(ASSETS_DIR, "fig3_price_sensitivity_confounding.png")
    fig, ax = plt.subplots(figsize=(12.0, 6.5), dpi=300)
    fig.subplots_adjust(left=0.095, right=0.965, top=0.76, bottom=0.12)
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
    ax.plot(prices_smooth, human_smooth, color='#1D4ED8', lw=3.4, zorder=3,
            label='真實消費者盲測（正常價格彈性：價格提高，購買意願自 79% 暴跌至 4%）')
    ax.plot(prices_smooth, ai_smooth, color='#BE123C', lw=3.4, linestyle='--', zorder=3,
            label='AI 模擬受訪者（發生「混淆」偏誤：腦補物價同漲，意願凍結於 67%~62% 幾無彈性）')

    # Data points
    for px, py_h, py_a in zip(prices_pts, human_pts, ai_pts):
        ax.scatter([px], [py_h], color='#1D4ED8', s=95, zorder=5)
        ax.scatter([px], [py_a], color='#BE123C', s=95, marker='s', zorder=5)

    # Value callout badges
    ax.text(1000, 79 + 4.2, '79%', ha='center', va='bottom', fontsize=14, fontweight='bold', color='#1D4ED8',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#EFF6FF', edgecolor='#93C5FD', lw=1.3, alpha=0.95), zorder=6)
    ax.text(1000, 67 - 5.2, '67%', ha='center', va='top', fontsize=14, fontweight='bold', color='#BE123C',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#FFF1F2', edgecolor='#FECDD3', lw=1.3, alpha=0.95), zorder=6)

    ax.text(3000, 64 + 4.2, '64%', ha='center', va='bottom', fontsize=14, fontweight='bold', color='#BE123C',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#FFF1F2', edgecolor='#FECDD3', lw=1.3, alpha=0.95), zorder=6)
    ax.text(3000, 35 - 5.2, '35%', ha='center', va='top', fontsize=14, fontweight='bold', color='#1D4ED8',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#EFF6FF', edgecolor='#93C5FD', lw=1.3, alpha=0.95), zorder=6)

    ax.text(5000, 62 + 4.2, '62%', ha='center', va='bottom', fontsize=14, fontweight='bold', color='#BE123C',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#FFF1F2', edgecolor='#FECDD3', lw=1.3, alpha=0.95), zorder=6)
    ax.text(5000, 4 + 4.2, '4%', ha='center', va='bottom', fontsize=14, fontweight='bold', color='#1D4ED8',
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#EFF6FF', edgecolor='#93C5FD', lw=1.3, alpha=0.95), zorder=6)

    # Reflective Callout Boxes
    bbox_ai_box = dict(boxstyle='round,pad=0.5', fc='#FFF1F2', ec='#BE123C', lw=1.6)
    ax.text(3750, 80, '【AI 語境腦補「混淆」陷阱】\n大模型誤設外部通膨等情境物價齊漲，\n導致價格上漲 5 倍時購買意願僅降 5%！',
            ha='center', va='center', fontsize=12, fontweight='bold', color='#9F1239', bbox=bbox_ai_box, zorder=6)

    bbox_human_box = dict(boxstyle='round,pad=0.5', fc='#EFF6FF', ec='#1D4ED8', lw=1.6)
    ax.text(1850, 20, '【真實消費者價格敏感度】\n符合微觀經濟學第一性原理（負斜率需求）：\n高價位（5,000 元）購買意願銳減至 4%（重挫 -95%）',
            ha='center', va='center', fontsize=12, fontweight='bold', color='#1E40AF', bbox=bbox_human_box, zorder=6)

    # Formatting
    ax.set_xlim(700, 5300)
    ax.set_ylim(-3, 102)
    ax.set_xticks([1000, 2000, 3000, 4000, 5000])
    ax.set_xticklabels(['$ 1,000', '$ 2,000', '$ 3,000', '$ 4,000', '$ 5,000'], fontsize=13, fontweight='bold', color='#0F172A')
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_yticklabels(['0%', '20%', '40%', '60%', '80%', '100%'], fontsize=13, fontweight='bold', color='#0F172A')
    ax.set_xlabel('測試產品定價 (新台幣 / 美元)', fontsize=13.5, fontweight='bold', color='#334155', labelpad=8)
    ax.set_ylabel('購買意願機率 (%)', fontsize=13.5, fontweight='bold', color='#334155', labelpad=8)
    ax.grid(True, linestyle=':', alpha=0.6, color='#CBD5E1', zorder=1)

    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.spines['left'].set_color('#94A3B8')
    ax.spines['bottom'].set_color('#94A3B8')

    ax.legend(loc='lower left', bbox_to_anchor=(0.0, 1.02), frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=12)

    fig.text(0.095, 0.965, '市場研究實證：真實消費者 vs. AI 模擬受訪者之價格敏感度混淆實驗',
             fontsize=17, fontweight='bold', color='#1E3A8A', ha='left', va='top')
    fig.text(0.095, 0.915, '因果推論實證對照：AI 腦補物價同漲導致需求曲線平坦失靈，與微觀經濟學客觀規律嚴重脫節',
             fontsize=12.5, color='#64748B', ha='left', va='top')

    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Fig 3 generated successfully:", out_path)


# =============================================================================
# FIGURE 4: CUSTOMER VALUE GAP & FINANCIAL LEVERAGE (ENLARGED & HIGH IMPACT)
# Canvas: 16.0 x 8.4, extra wide, bold typography, clear capsules, prominent cards
# =============================================================================
def generate_figure4():
    out_path = os.path.join(ASSETS_DIR, "fig4_customer_value_gap.png")
    fig = plt.figure(figsize=(16.0, 8.4), dpi=300, facecolor='#FFFFFF')
    gs = fig.add_gridspec(
        nrows=1, ncols=2,
        width_ratios=[1.25, 1.0],
        left=0.085, right=0.965,
        top=0.81, bottom=0.18,
        wspace=0.26
    )

    ax1 = fig.add_subplot(gs[0, 0], facecolor='#FFFFFF')
    ax2 = fig.add_subplot(gs[0, 1], facecolor='#FFFFFF')

    # Master Header
    fig.text(0.085, 0.955, '顧客需求不靠猜：高管直覺預估與顧客真實價值的巨大剪刀差，以及認知對齊的財務槓桿',
             fontsize=19.5, fontweight='bold', color='#0F172A', ha='left', va='top')
    fig.text(0.085, 0.900, '【實證落差與財務轉換】72% 上市 B2B 企業高管直覺與顧客重視事項零或負相關；統計模型揭露真實提升潛力，驅動顯著財務槓桿',
             fontsize=13.5, fontweight='bold', color='#334155', ha='left', va='top')

    # Decorative line
    header_line = plt.Line2D([0.085, 0.965], [0.865, 0.865], transform=fig.transFigure, color='#CBD5E1', linewidth=1.5)
    fig.add_artist(header_line)
    header_accent = plt.Line2D([0.085, 0.38], [0.865, 0.865], transform=fig.transFigure, color='#CA6F35', linewidth=3.5)
    fig.add_artist(header_accent)

    # ---------------- Left Panel: Paired Dual Bar & Scissors Gap ----------------
    categories = [
        "【問題解決】\n24小時內解決問題\n（教育公司服務）",
        "【安全規範】\n現場作業安全履約\n（工業服務公司）",
        "【溝通回饋】\n每週專案進度更新\n（製造商 ITI）",
        "【品質低價】\n規格符合與低報價\n（基本衛生因子門檻）",
    ]
    x = np.arange(len(categories)) * 1.35
    bar_w = 0.38
    gap = 0.03
    x_exec = x - bar_w/2 - gap/2
    x_cust = x + bar_w/2 + gap/2

    exec_estimate = [12.5, 2.3, 10.0, 42.0]
    cust_actual   = [85.0, 19.5, 48.0, 4.0]

    c_exec = "#ECA072"
    c_cust = "#5DBACD"
    c_exec_edge = "#CA6F35"
    c_cust_edge = "#0E5B6B"

    bars1 = ax1.bar(x_exec, exec_estimate, bar_w, label="高管直覺預估／均分權重（直覺猜想）",
                    color=c_exec, edgecolor=c_exec_edge, linewidth=1.4, zorder=3)
    bars2 = ax1.bar(x_cust, cust_actual, bar_w, label="統計模型測出之顧客實際提升潛力（真實需求）",
                    color=c_cust, edgecolor=c_cust_edge, linewidth=1.4, zorder=3)

    # Bar top numbers
    for b in bars1:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width()/2, h + 1.8, f"{h:.1f}%",
                 ha="center", va="bottom", fontsize=13.5, fontweight="bold", color=c_exec_edge, zorder=6)
    for b in bars2:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width()/2, h + 1.8, f"{h:.1f}%",
                 ha="center", va="bottom", fontsize=13.5, fontweight="bold", color=c_cust_edge, zorder=6)

    def draw_capsule(ax, cx, cy, text, color, bg, border):
        bbox_props = dict(boxstyle="round,pad=0.32,rounding_size=0.18", fc=bg, ec=border, lw=1.4)
        ax.text(cx, cy, text, ha="center", va="center", fontsize=11.2, fontweight="bold",
                color=color, bbox=bbox_props, zorder=7)

    # Delta Arrows & Capsules
    # Case 0: 24h problem resolution
    ax1.plot([x_exec[0] - bar_w/2, x_cust[0] + bar_w/2], [85.0, 85.0], color="#94A3B8", linestyle=":", lw=1.5, zorder=2)
    ax1.annotate("", xy=(x_exec[0], 85.0), xytext=(x_exec[0], 17.5),
                 arrowprops=dict(arrowstyle="<->", color="#0E5B6B", lw=2.0), zorder=5)
    draw_capsule(ax1, x_exec[0], 51.0, "Δ = +72.5%\n(+6.8倍關鍵)", "#0E5B6B", "#EBF7F9", "#5DBACD")

    # Case 1: Safety compliance (Capsule positioned safely above bars, zero overlap with 2.3%!)
    ax1.plot([x_exec[1] - bar_w/2, x_cust[1] + bar_w/2], [19.5, 19.5], color="#94A3B8", linestyle=":", lw=1.5, zorder=2)
    ax1.annotate("", xy=(x_exec[1], 19.5), xytext=(x_exec[1], 33.0),
                 arrowprops=dict(arrowstyle="->", color="#0E5B6B", lw=1.8), zorder=5)
    draw_capsule(ax1, x_exec[1], 40.0, "Δ = +17.2%\n(+8.5倍被低估)", "#0E5B6B", "#EBF7F9", "#5DBACD")

    # Case 2: Weekly progress update
    ax1.plot([x_exec[2] - bar_w/2, x_cust[2] + bar_w/2], [48.0, 48.0], color="#94A3B8", linestyle=":", lw=1.5, zorder=2)
    ax1.annotate("", xy=(x_exec[2], 48.0), xytext=(x_exec[2], 14.5),
                 arrowprops=dict(arrowstyle="<->", color="#0E5B6B", lw=2.0), zorder=5)
    draw_capsule(ax1, x_exec[2], 31.0, "Δ = +38.0%\n(核心業務驅動)", "#0E5B6B", "#EBF7F9", "#5DBACD")

    # Case 3: Hygiene factor (Price/Quality)
    ax1.plot([x_exec[3] - bar_w/2, x_cust[3] + bar_w/2], [42.0, 42.0], color="#94A3B8", linestyle=":", lw=1.5, zorder=2)
    ax1.annotate("", xy=(x_cust[3], 42.0), xytext=(x_cust[3], 8.5),
                 arrowprops=dict(arrowstyle="<->", color="#97481B", lw=2.0), zorder=5)
    draw_capsule(ax1, x_cust[3], 25.0, "Δ = -38.0%\n(基本衛生因子\n嚴重過度高估)", "#97481B", "#FFF3EA", "#ECA072")

    ax1.set_title("【左圖：高管直覺預估 vs. 顧客實際提升潛力】剪刀差落差對照",
                  fontsize=14.5, fontweight="bold", color="#0F172A", loc="left", pad=14)
    ax1.set_ylabel("價值重要性 / 統計提升潛力（Lift %）", fontsize=13.5, fontweight="bold", color="#334155")
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=12.0, fontweight="bold", linespacing=1.25)
    ax1.set_xlim(-0.70, 3 * 1.35 + 0.70)
    ax1.set_ylim(0, 102)
    ax1.set_yticks([0, 20, 40, 60, 80, 100])
    ax1.set_yticklabels([f"{v}%" for v in [0, 20, 40, 60, 80, 100]], fontsize=13, fontweight="bold", color="#475569")
    ax1.yaxis.grid(True, linestyle="--", color="#CBD5E1", alpha=0.75, zorder=0)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color('#94A3B8')
    ax1.spines['bottom'].set_color('#64748B')
    ax1.legend(loc="upper left", frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=11.5)

    # ---------------- Right Panel: Financial Leverage ----------------
    metrics = [
        "【企業市值增幅】\n資本市場長期信心回報",
        "【營業收入增加】\n客戶持續復購與擴大採購",
        "【自由現金流提升】\n造血引擎充裕營運現金",
        "【毛利率實質改善】\n具定價權、擺脫價格血拼",
    ]
    returns = [11.1, 9.2, 8.8, 5.2]
    y_pos = np.array([3.6, 2.6, 1.6, 0.6])

    bar_colors = ["#0E5B6B", "#2C8B9F", "#5DBACD", "#8ED4E2"]
    edge_colors = ["#0A3E49", "#1B5D6B", "#2C8B9F", "#4FAABF"]

    bars_r = ax2.barh(y_pos, returns, height=0.55, color=bar_colors, edgecolor=edge_colors, linewidth=1.4, zorder=3)

    for i, (bar, val) in enumerate(zip(bars_r, returns)):
        w = bar.get_width()
        ax2.text(w + 0.38, bar.get_y() + bar.get_height()/2, f"+{val:.1f}%",
                 ha="left", va="center", fontsize=14.5, fontweight="bold", color="#0A3E49")

    ax2.set_title("【右圖：認知對齊之財務槓桿】指標增幅（對齊度每增12.5分）",
                  fontsize=14.5, fontweight="bold", color="#0F172A", loc="left", pad=14)
    ax2.set_xlabel("公司財務與市場指標平均成長率（%）", fontsize=13.5, fontweight="bold", color="#334155")
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(metrics, fontsize=12.0, fontweight="bold", linespacing=1.25)
    ax2.set_ylim(-1.4, 4.4)
    ax2.set_xlim(0, 14.5)
    ax2.xaxis.grid(True, linestyle="--", color="#CBD5E1", alpha=0.75, zorder=0)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color('#94A3B8')
    ax2.spines['bottom'].set_color('#64748B')

    card_text = (
        "★ 實證案例 4 年落地總體回報：\n"
        "• ITI 製造商：進度報告由 <30次 增至 3,524次，\n"
        "  釋放 30%+ 工時，股價上漲 +162%（vs. 標普 34%、羅素 8%）\n"
        "• S-SET 流體經銷：報價時間 18hr 縮至 <3hr，人均銷售 +52%\n"
        "• 800 億美元跨國銀行：滿意度 +18%，營收 +33%，市值大增 +200%"
    )
    ax2.text(
        0.98, 0.04, card_text,
        transform=ax2.transAxes,
        ha="right", va="bottom",
        fontsize=11.2, linespacing=1.45, fontweight="bold",
        color="#1E293B",
        bbox=dict(boxstyle="round,pad=0.55,rounding_size=0.15", fc="#F8FAFC", ec="#0E5B6B", lw=1.3)
    )

    # Footer banner
    footer_box = FancyBboxPatch((0.085, 0.02), 0.880, 0.065, boxstyle='round,pad=0.008,rounding_size=0.01',
                                transform=fig.transFigure, facecolor='#F1F5F9', edgecolor='#CBD5E1', linewidth=1.0)
    fig.add_artist(footer_box)

    fig.text(0.095, 0.058, '■ 資料來源：Vikas Mittal, A. Piazza, S. Singh & A. Malshe (2025), "Do You Know What Your Customers Value?", Harvard Business Review.',
             fontsize=11.5, fontweight='bold', color='#1E293B', ha='left', va='center')
    fig.text(0.095, 0.032, '• 研究範疇：涵蓋 104 家上市 B2B 企業及其 18,840 名顧客之 10-K 財報自然語言分析與雙層統計模型驗證；涵蓋期間 1999–2024 年。',
             fontsize=10.5, color='#475569', ha='left', va='center')

    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Fig 4 generated successfully:", out_path)


# =============================================================================
# FIGURE 5: ECOSYSTEM VALUE LOOP (LEFT-TO-RIGHT PPT 3-PILLAR & FAILURE WARNINGS)
# Canvas: 16.0 x 9.6, zero text collisions, generous connector spacing, big readable fonts
# =============================================================================
def generate_figure5():
    out_path = os.path.join(ASSETS_DIR, "fig5_ecosystem_mindmap.png")
    fig = plt.figure(figsize=(16.0, 9.6), dpi=300, facecolor='#FFFFFF')
    ax = fig.add_axes([0, 0, 1, 1], facecolor='#FFFFFF')
    ax.set_xlim(0, 16.0)
    ax.set_ylim(0, 9.6)
    ax.axis('off')

    # Master Header
    ax.text(0.55, 9.25, "企業、顧客與投資者生態價值循環：造血發動機 vs. 資本助燃劑之平衡架構",
            fontsize=21, fontweight='bold', color='#0F172A', ha='left', va='top')
    ax.text(0.55, 8.80, "【商業第一性原理】「企業與顧客」是唯一造血引擎，「投資人」是外部加速助燃劑；短視討好投資人必將釀成結構性失靈",
            fontsize=13.5, fontweight='bold', color='#475569', ha='left', va='top')

    # Accent line
    ax.plot([0.55, 15.45], [8.55, 8.55], color='#CBD5E1', lw=1.5)
    ax.plot([0.55, 5.00], [8.55, 8.55], color='#0284C7', lw=3.8)

    # 3 Horizontal Cards (Top Row)
    # Available width from 0.55 to 15.45 = 14.90
    # card_w = 4.10, gap = 1.30
    top_y = 4.80
    top_h = 3.65
    col_w = 4.10
    gap = 1.30
    x1 = 0.55
    x2 = x1 + col_w + gap
    x3 = x2 + col_w + gap

    def draw_top_card(x, y, w, h, bg_color, border_color, badge_txt, badge_bg,
                      title, subtitle, bullets, foot_pill, foot_bg, foot_color):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=0.15",
                             facecolor=bg_color, edgecolor=border_color, linewidth=2.2, zorder=2)
        ax.add_patch(box)

        # Badge
        badge = FancyBboxPatch((x + 0.20, y + h - 0.46), 2.20, 0.36, boxstyle="round,pad=0.0,rounding_size=0.06",
                               facecolor=badge_bg, edgecolor='none', zorder=3)
        ax.add_patch(badge)
        ax.text(x + 1.30, y + h - 0.28, badge_txt, ha='center', va='center',
                fontsize=12.2, fontweight='bold', color='#FFFFFF', zorder=4)

        # Title & Subtitle
        ax.text(x + 0.20, y + h - 0.82, title, ha='left', va='center',
                fontsize=17.5, fontweight='bold', color='#0F172A', zorder=3)
        ax.text(x + 0.20, y + h - 1.15, subtitle, ha='left', va='center',
                fontsize=11.8, color='#475569', zorder=3)

        # Bullets: generous vertical spacing ensuring ZERO overlap with footer pill!
        for i, (tag, desc) in enumerate(bullets):
            by = y + h - 1.58 - i * 0.58
            ax.text(x + 0.20, by, f"{tag}", ha='left', va='center',
                    fontsize=12.2, fontweight='bold', color=border_color, zorder=4)
            ax.text(x + 0.20, by - 0.24, f"{desc}", ha='left', va='center',
                    fontsize=11.2, color='#334155', zorder=4)

        # Foot
        foot = FancyBboxPatch((x + 0.18, y + 0.16), w - 0.36, 0.40, boxstyle="round,pad=0.0,rounding_size=0.06",
                              facecolor=foot_bg, edgecolor=border_color, linewidth=1.2, zorder=3)
        ax.add_patch(foot)
        ax.text(x + w / 2, y + 0.36, foot_pill, ha='center', va='center',
                fontsize=10.5, fontweight='bold', color=foot_color, zorder=4)

    # 1. Left Card: 投資人／資本市場
    draw_top_card(
        x=x1, y=top_y, w=col_w, h=top_h,
        bg_color='#FFFDF5', border_color='#D97706',
        badge_txt='◆ 外部助燃加速', badge_bg='#D97706',
        title='投資人／資本市場',
        subtitle='提供外部擴張資本，分享造血成果',
        bullets=[
            ('【核心角色：助燃劑】', '提供成長擴張資金，事後合理共享市值紅利'),
            ('【合理訴求：產值提高】', '期望健康營收毛利擴張，放大長期投資回報'),
            ('【致命誘因：反客為主】', '熱錢若超客戶營收，將誘使高管轉向短期炒作')
        ],
        foot_pill='【健康定位】外部加速助燃劑，非日常造血水源',
        foot_bg='#FEF3C7', foot_color='#92400E'
    )

    # 2. Middle Card: 企業核心樞紐
    draw_top_card(
        x=x2, y=top_y, w=col_w, h=top_h,
        bg_color='#F0F9FF', border_color='#0284C7',
        badge_txt='■ 價值造血發動機', badge_bg='#0284C7',
        title='企業核心樞紐（Company）',
        subtitle='抗拒短期估值誘惑，以模型對齊需求',
        bullets=[
            ('【核心角色：造血發動機】', '將資源轉化為真實商業價值，創造正向現金流'),
            ('【首要考驗：抗拒短視】', '放下取悅華爾街衝動，以統計模型挖掘真痛點'),
            ('【策略落地：資源挪移】', '果斷停損低效專案，全量集中對齊核心需求')
        ],
        foot_pill='【健康定位】100% 心力服務客戶，創造真金白銀',
        foot_bg='#E0F2FE', foot_color='#0369A1'
    )

    # 3. Right Card: 客戶／價值源頭
    draw_top_card(
        x=x3, y=top_y, w=col_w, h=top_h,
        bg_color='#F0FDF4', border_color='#0D9488',
        badge_txt='★ 真實價值源頭', badge_bg='#0D9488',
        title='客戶／價值源頭（Customer）',
        subtitle='商業第一性原理，買單是唯一地基',
        bullets=[
            ('【核心角色：價值真源頭】', '客戶真金白銀買單，是支撐企業運轉唯一地基'),
            ('【超額回報：痛點速解】', '最在乎 24hr 解決問題（85%）與進度定期更新'),
            ('【客觀鐵律：交換誕生】', '價值在交換時誕生；客戶不買單一切皆泡影')
        ],
        foot_pill='【健康定位】商業唯一泉源，檢驗價值的終極裁判',
        foot_bg='#CCFBF1', foot_color='#0F766E'
    )

    # Connectors between Top Cards (1.30 inch wide gap, ZERO collision!)
    # Gap 1: between Card 1 (ends 4.65) and Card 2 (starts 5.95). Center = 5.30
    # Top arrow: 資本助燃
    ax.annotate('', xy=(5.85, top_y + 2.25), xytext=(4.75, top_y + 2.25),
                arrowprops=dict(arrowstyle="->,head_width=0.40,head_length=0.50", color='#D97706', lw=2.4), zorder=5)
    ax.text(5.30, top_y + 2.55, "資本助燃 →", ha='center', va='center',
            fontsize=11.5, fontweight='bold', color='#92400E', zorder=6)

    # Bottom arrow: 共享市值
    ax.annotate('', xy=(4.75, top_y + 1.35), xytext=(5.85, top_y + 1.35),
                arrowprops=dict(arrowstyle="->,head_width=0.40,head_length=0.50", color='#0284C7', lw=2.4), zorder=5)
    ax.text(5.30, top_y + 1.65, "← 共享市值", ha='center', va='center',
            fontsize=11.5, fontweight='bold', color='#0369A1', zorder=6)

    # Gap 2: between Card 2 (ends 10.05) and Card 3 (starts 11.35). Center = 10.70
    # Top arrow: 解顧客痛點
    ax.annotate('', xy=(11.25, top_y + 2.35), xytext=(10.15, top_y + 2.35),
                arrowprops=dict(arrowstyle="->,head_width=0.42,head_length=0.55", color='#0D9488', lw=2.8), zorder=5)
    ax.text(10.70, top_y + 2.65, "解顧客痛點 →", ha='center', va='center',
            fontsize=11.8, fontweight='bold', color='#0F766E', zorder=6)

    # Center badge: ★ 雙向造血主迴路 ★
    bbox_core = dict(boxstyle="round,pad=0.25,rounding_size=0.10", fc="#0F172A", ec="#38BDF8", lw=1.5)
    ax.text(10.70, top_y + 1.75, "★ 雙向造血 ★\n（主迴路）", ha='center', va='center',
            fontsize=11.0, fontweight='bold', color='#38BDF8', bbox=bbox_core, zorder=6)

    # Bottom arrow: 回饋真實營收
    ax.annotate('', xy=(10.15, top_y + 1.15), xytext=(11.25, top_y + 1.15),
                arrowprops=dict(arrowstyle="->,head_width=0.42,head_length=0.55", color='#0284C7', lw=2.8), zorder=5)
    ax.text(10.70, top_y + 0.85, "← 真金白銀", ha='center', va='center',
            fontsize=11.8, fontweight='bold', color='#0369A1', zorder=6)

    # ---------------- Lower Tier: 3 Structural Failure Warning Cards ----------------
    warn_y = 1.20
    warn_h = 3.30
    warn_w = 14.90
    warn_x = 0.55

    box_warn = FancyBboxPatch((warn_x, warn_y), warn_w, warn_h, boxstyle="round,pad=0.0,rounding_size=0.15",
                              facecolor="#FFF7F2", edgecolor="#DC2626", linewidth=2.2, zorder=2)
    ax.add_patch(box_warn)

    # Header bar
    h_bar = FancyBboxPatch((warn_x, warn_y + warn_h - 0.44), warn_w, 0.44, boxstyle="round,pad=0.0,rounding_size=0.08",
                           facecolor="#FEE2E2", edgecolor="#DC2626", linewidth=1.2, zorder=3)
    ax.add_patch(h_bar)
    ax.text(warn_x + 0.25, warn_y + warn_h - 0.22,
            "● 深度警戒：【結構性失靈——當「助燃劑」反客為主（討好投資人 ＞ 服務客戶）的三大慘痛教訓】",
            fontsize=14.5, fontweight="bold", color="#991B1B", va="center", ha="left", zorder=5)

    ax.text(warn_x + 0.25, warn_y + warn_h - 0.64,
            "【誘因錯位惡果】管理階層為迎合每季股價炒作，將心力用於取悅資本市場而非服務客戶，最終導致「尾巴搖狗」的毀滅性崩壞：",
            fontsize=12.2, fontweight="bold", color="#7F1D1D", va="top", ha="left", zorder=5)

    # 3 Parallel Warning Cards
    case_w = 4.70
    case_h = 2.00
    case_y = warn_y + 0.20
    cx_list = [warn_x + 0.20, warn_x + 0.20 + case_w + 0.20, warn_x + 0.20 + (case_w + 0.20) * 2]

    cases = [
        {
            "title": "案例一：波音 737 MAX 飛安災難",
            "items": [
                ("迎合短期股價", "大搞庫藏股護盤取悅華爾街季度利潤"),
                ("大砍研發品管", "核心軟體外包，忽視嚴謹工程飛安文化"),
                ("慘痛歷史代價", "兩起重大空難，全球停飛，市值大崩盤")
            ]
        },
        {
            "title": "案例二：迪士尼「賣玩具廣告」迷失",
            "items": [
                ("追逐周邊授權", "追求玩具利潤，讓商業授權凌駕原創故事"),
                ("電影淪為型錄", "劇本硬塞無關角色，犧牲故事核心品質"),
                ("慘痛歷史代價", "影視口碑大跌，觀眾流失，IP光環受損")
            ]
        },
        {
            "title": "案例三：AI 與串流泡沫的虛榮指標",
            "items": [
                ("盲目衝刺虛榮", "瘋狂補貼衝免洗註冊與短期假象估值"),
                ("忽視真實留存", "缺乏自我造血能力與真實 ROI 商業邏輯"),
                ("慘痛歷史代價", "熱錢退潮資金枯竭，無人買單瞬間倒閉")
            ]
        }
    ]

    for c_idx, c in enumerate(cases):
        cx = cx_list[c_idx]
        c_box = FancyBboxPatch((cx, case_y), case_w, case_h, boxstyle="round,pad=0.0,rounding_size=0.08",
                               facecolor="#FFFFFF", edgecolor="#FCA5A5", linewidth=1.3, zorder=3)
        ax.add_patch(c_box)

        # Title bar
        t_bar = FancyBboxPatch((cx, case_y + case_h - 0.36), case_w, 0.36, boxstyle="round,pad=0.0,rounding_size=0.05",
                               facecolor="#FFF1F2", edgecolor="#FCA5A5", linewidth=0.9, zorder=4)
        ax.add_patch(t_bar)
        ax.text(cx + case_w / 2, case_y + case_h - 0.18, c["title"],
                fontsize=13.0, fontweight="bold", color="#991B1B", va="center", ha="center", zorder=5)

        for r_idx, (r_head, r_body) in enumerate(c["items"]):
            ry = case_y + case_h - 0.65 - r_idx * 0.44
            ax.text(cx + 0.20, ry, f"• 【{r_head}】", fontsize=11.8, fontweight="bold", color="#991B1B", va="center", ha="left", zorder=5)
            ax.text(cx + 0.20, ry - 0.18, f"   {r_body}", fontsize=11.0, color="#1E293B", va="center", ha="left", zorder=5)

    # Bottom Master Banner
    banner_box = FancyBboxPatch((warn_x, 0.15), warn_w, 0.85, boxstyle="round,pad=0.0,rounding_size=0.10",
                                facecolor="#0F172A", edgecolor="#38BDF8", linewidth=1.6, zorder=2)
    ax.add_patch(banner_box)
    ax.text(warn_x + 0.25, 0.70, "★ 商業第一性原理結論：", fontsize=13.0, fontweight="bold", color="#FBBF24", va="center", ha="left", zorder=5)
    ax.text(warn_x + 0.25, 0.40, "真正的商業價值永遠誕生於「企業與客戶」的雙向造血迴路；資本市場的資金只是加速的助燃劑。\n"
                                  "企業唯有放下直覺執念，用統計模型找出顧客真正在乎的事，才能以健康的真金白銀支撐起長期穩健的市值溢價。",
            fontsize=11.2, color="#F8FAFC", linespacing=1.35, va="center", ha="left", zorder=5)

    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Fig 5 generated successfully:", out_path)


if __name__ == "__main__":
    generate_figure1()
    generate_figure2()
    generate_figure3()
    generate_figure4()
    generate_figure5()
    print("\nAll 5 figures generated with V3 high-impact standards!")
