# -*- coding: utf-8 -*-
"""
generate_report_figures.py
Generates publication-grade Matplotlib figures for Figures 1, 2, and 3:
- Figure 1: 企業對 AI 期望 (80%) vs 實際商業應用落地 (8%) vs 企業內部禁用 (15%) 的「數據債」落差圖
- Figure 2: 人機協同大腦架構圖 (剛性左腦數據辭典 + 靈活右腦大模型 + 前額葉人類專家)
- Figure 3: 價格敏感度混淆實驗分析圖 (價格從 1000 漲到 5000 元，真人 vs AI 購買意願)
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Set font family
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'DFKai-SB', 'SimHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR_1 = r"reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\assets_原始素材與圖表"
OUTPUT_DIR_2 = r"C:\Users\User\OneDrive\桌面\期中報告"

os.makedirs(OUTPUT_DIR_1, exist_ok=True)
os.makedirs(OUTPUT_DIR_2, exist_ok=True)

# -----------------------------------------------------------------------------
# Figure 1: 企業對 AI 期望 vs 實際落地 vs 內部禁用 (數據債落差圖)
# -----------------------------------------------------------------------------
def generate_fig1():
    # Adjusted figure size and margins so labels never get cut off
    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=300)
    fig.subplots_adjust(left=0.22, right=0.92, top=0.88, bottom=0.14)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    categories = [
        '企業內部\n全面禁用/限用',
        '實際商業應用\n落地與生產級產出',
        '企業高層對 AI\n投入之樂觀期望'
    ]
    values = [15, 8, 80]
    colors = ['#64748B', '#EF4444', '#1E3A8A']
    
    y_pos = np.arange(len(categories))
    bars = ax.barh(y_pos, values, color=colors, height=0.48, edgecolor='none', zorder=3)
    
    # Value labels beside bars
    for bar, val, col in zip(bars, values, colors):
        # Position label cleanly to the right of the bar
        ax.text(val + 1.8, bar.get_y() + bar.get_height()/2, f"{val}%", 
                va='center', ha='left', fontsize=14, fontweight='bold', color=col, zorder=6)

    # Bracket showing the gap between 80% and 8%
    # Placed at y = 1.35 (above the 8% bar) so it does NOT touch the bar or the "8%" text
    gap_y = 1.32
    ax.plot([8, 80], [gap_y, gap_y], color='#B91C1C', linestyle='--', linewidth=1.8, zorder=4)
    ax.plot([8, 8], [gap_y - 0.12, gap_y + 0.04], color='#B91C1C', linewidth=1.8, zorder=4)
    ax.plot([80, 80], [gap_y - 0.12, gap_y + 0.04], color='#B91C1C', linewidth=1.8, zorder=4)
    ax.scatter([8, 80], [gap_y, gap_y], color='#B91C1C', s=35, zorder=5)
    
    # Gap callout box centered above the bracket
    bbox_props = dict(boxstyle="round,pad=0.5", fc="#FEF2F2", ec="#EF4444", lw=1.5)
    ax.text(44, 1.70, "「數據債」巨幅鴻溝：-72%\n（非結構化資料無法直接被大模型可靠消化）", 
            ha='center', va='center', fontsize=11, fontweight='bold', color='#991B1B', bbox=bbox_props, zorder=6)
    
    # Detail note for 15% ban placed cleanly with ample buffer (x=25, well past "15%" at 16.8)
    bbox_ban = dict(boxstyle="round,pad=0.35", fc="#F1F5F9", ec="#94A3B8", lw=1.0)
    ax.text(25, 0, "資安隱私疑慮與幻覺風險導致明文禁用", va='center', ha='left', 
            fontsize=10, color='#334155', bbox=bbox_ban, zorder=6)

    # Formatting
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 2.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontsize=12, fontweight='bold', color='#0F172A')
    ax.set_xlabel('企業受訪比例 (%)', fontsize=11, fontweight='bold', color='#334155', labelpad=10)
    ax.xaxis.grid(True, linestyle=':', alpha=0.6, color='#CBD5E1', zorder=1)
    ax.set_axisbelow(True)
    
    # Spines styling
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.spines['left'].set_color('#94A3B8')
    ax.spines['bottom'].set_color('#94A3B8')
    
    # In-chart clean header
    plt.title('企業 AI 期望與現實落差現況（高達 80% 期待 vs. 僅 8% 實質商業落地）', 
              fontsize=13.5, fontweight='bold', color='#1E3A8A', pad=16)
    
    out1 = os.path.join(OUTPUT_DIR_1, "fig1_data_debt_gap.png")
    out2 = os.path.join(OUTPUT_DIR_2, "fig1_data_debt_gap.png")
    plt.savefig(out1, dpi=300)
    plt.savefig(out2, dpi=300)
    plt.close()
    print("Fig 1 generated successfully:", out1)


# -----------------------------------------------------------------------------
# Figure 2: 人機協同大腦架構圖 (剛性數據辭典 + 靈活大模型 + 前額葉人類專家)
# -----------------------------------------------------------------------------
def generate_fig2():
    fig, ax = plt.subplots(figsize=(12.0, 7.0), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    ax.set_xlim(0, 12.0)
    ax.set_ylim(0, 7.0)
    ax.axis('off')

    # Draw Title
    ax.text(6.0, 6.6, "人機協同數據治理大腦架構圖", 
            ha='center', va='center', fontsize=15.5, fontweight='bold', color='#1E3A8A')
    ax.text(6.0, 6.2, "剛性數據辭典（左腦） + 靈活大模型（右腦） + 前額葉人類專家（最後防線）", 
            ha='center', va='center', fontsize=11, color='#475569')

    # Helper function to draw rounded module cards
    def draw_card(x, y, w, h, bg_color, border_color, title, subtitle, bullets, badge_txt, badge_color):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=0.2",
                             facecolor=bg_color, edgecolor=border_color, linewidth=2, zorder=2)
        ax.add_patch(box)
        
        # Badge
        badge = FancyBboxPatch((x + 0.25, y + h - 0.42), 1.6, 0.30, boxstyle="round,pad=0.0,rounding_size=0.08",
                               facecolor=badge_color, edgecolor='none', zorder=3)
        ax.add_patch(badge)
        ax.text(x + 1.05, y + h - 0.27, badge_txt, ha='center', va='center', 
                fontsize=9.5, fontweight='bold', color='#FFFFFF', zorder=4)
        
        # Title
        ax.text(x + 0.25, y + h - 0.74, title, ha='left', va='center', 
                fontsize=13, fontweight='bold', color='#0F172A', zorder=3)
        ax.text(x + 0.25, y + h - 1.04, subtitle, ha='left', va='center', 
                fontsize=9.5, color='#64748B', style='italic', zorder=3)
        
        # Bullets
        for i, b in enumerate(bullets):
            ax.text(x + 0.25, y + h - 1.42 - (i * 0.40), f"• {b}", ha='left', va='center', 
                    fontsize=9.5, color='#1E293B', zorder=3)

    card_y = 1.45
    card_h = 4.35
    card_w = 3.2

    # 1. Left Card: 剛性左腦 (數據辭典) [0.5 -> 3.7]
    draw_card(
        x=0.5, y=card_y, w=card_w, h=card_h,
        bg_color='#EFF6FF', border_color='#3B82F6',
        title='剛性數據辭典 (左腦)',
        subtitle='結構化秩序與第一性原理規則錨點',
        bullets=[
            '極端案例與例外歷史處置庫',
            '跨部門業務專有名詞同義表',
            '資料清洗與入庫規範規格書',
            '強制約束大模型運算邊界',
            '從源頭徹底掐滅 AI 幻覺'
        ],
        badge_txt='規範約束核心', badge_color='#2563EB'
    )

    # 2. Middle Card: 靈活右腦 (大語言模型) [4.4 -> 7.6]
    draw_card(
        x=4.4, y=card_y, w=card_w, h=card_h,
        bg_color='#F5F3FF', border_color='#8B5CF6',
        title='靈活大模型 (右腦)',
        subtitle='湧現語義轉譯與低成本海量處理',
        bullets=[
            '非結構化圖文資料高速解析',
            '半結構化日誌格式快速規整',
            '對齊數據辭典進行語義貼標',
            '提供初步關聯挖掘與猜想',
            '處理 90% 常態化數據洪流'
        ],
        badge_txt='高能運算引擎', badge_color='#7C3AED'
    )

    # 3. Right Card: 前額葉 (人類專家防線) [8.3 -> 11.5]
    draw_card(
        x=8.3, y=card_y, w=card_w, h=card_h,
        bg_color='#FEF2F2', border_color='#EF4444',
        title='人類最後防線 (前額葉)',
        subtitle='直覺審查、價值仲裁與戰略反思',
        bullets=[
            '審查未知與模糊之邊界個案',
            '識別全新市場信號與突變',
            '權衡商業價值與合約倫理',
            '仲裁 AI 疑義並修正決策',
            '將新經驗回饋擴充「左腦」'
        ],
        badge_txt='戰略仲裁中樞', badge_color='#DC2626'
    )

    # Connective arrows between cards (3.7 -> 4.4, and 7.6 -> 8.3)
    arrow_props_1 = dict(facecolor='#2563EB', edgecolor='#1D4ED8', width=2.5, headwidth=7, headlength=7)
    arrow_props_2 = dict(facecolor='#7C3AED', edgecolor='#6D28D9', width=2.5, headwidth=7, headlength=7)

    # Left to Middle arrow
    ax.annotate('', xy=(4.35, 3.6), xytext=(3.75, 3.6), arrowprops=arrow_props_1, zorder=5)
    bbox_lbl1 = dict(boxstyle="round,pad=0.25", fc="#FFFFFF", ec="#3B82F6", lw=1.2)
    ax.text(4.05, 4.05, "規則錨定", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1D4ED8', bbox=bbox_lbl1, zorder=6)

    # Middle to Right arrow
    ax.annotate('', xy=(8.25, 3.6), xytext=(7.65, 3.6), arrowprops=arrow_props_2, zorder=5)
    bbox_lbl2 = dict(boxstyle="round,pad=0.25", fc="#FFFFFF", ec="#8B5CF6", lw=1.2)
    ax.text(7.95, 4.05, "疑難個案", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#6D28D9', bbox=bbox_lbl2, zorder=6)

    # Bottom Feedback Loop Arrow: Frontal lobe enriches Left brain dictionary
    # Starts at right card center (9.9, 1.45) -> ends at left card center (2.1, 1.45)
    style = "arc3,rad=-0.12"
    arrowprops_feedback = dict(arrowstyle="->,head_width=0.45,head_length=0.65",
                               connectionstyle=style, color="#DC2626", lw=2.2, ls='--')
    ax.annotate('', xy=(2.1, 1.42), xytext=(9.9, 1.42),
                arrowprops=arrowprops_feedback, zorder=5)
    
    # Label placed safely at y=0.32 (well below the arc at y=0.75)
    bbox_feed = dict(boxstyle="round,pad=0.4", fc="#FEF2F2", ec="#DC2626", lw=1.2)
    ax.text(6.0, 0.32, "經驗沉澱與規則迭代更新（持續進化迴路：將專家智慧結構化固化至左腦）", 
            ha='center', va='center', fontsize=10.5, fontweight='bold', color='#991B1B', 
            bbox=bbox_feed, zorder=6)

    plt.tight_layout()
    out1 = os.path.join(OUTPUT_DIR_1, "fig2_brain_architecture.png")
    out2 = os.path.join(OUTPUT_DIR_2, "fig2_brain_architecture.png")
    plt.savefig(out1, dpi=300)
    plt.savefig(out2, dpi=300)
    plt.close()
    print("Fig 2 generated successfully:", out1)


# -----------------------------------------------------------------------------
# Figure 3: 價格敏感度混淆實驗分析圖 (真人 vs AI)
# -----------------------------------------------------------------------------
def generate_fig3():
    # Expanded y-limits and height to provide ample room for legend and annotations
    fig, ax = plt.subplots(figsize=(10.5, 5.6), dpi=300)
    fig.subplots_adjust(left=0.10, right=0.95, top=0.90, bottom=0.12)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    prices = [1000, 2000, 3000, 4000, 5000]
    human_intent = [45, 28, 16, 9, 4]
    ai_intent = [82, 81, 80, 81, 80]

    # Plot human line
    line_human, = ax.plot(prices, human_intent, marker='o', markersize=8, linewidth=2.8, 
                          color='#2563EB', label='真實消費者（符合正常價格彈性，意願暴跌）', zorder=4)
    # Plot AI line
    line_ai, = ax.plot(prices, ai_intent, marker='s', markersize=8, linewidth=2.8, 
                       color='#E11D48', linestyle='--', label='AI 合成受訪者（發生「混淆」陷阱，意願幾乎凍結不變）', zorder=4)

    # Shaded fill under curves to emphasize divergence
    ax.fill_between(prices, human_intent, ai_intent, color='#FEE2E2', alpha=0.35, zorder=2)

    # Data point labels for Human
    for p, h in zip(prices, human_intent):
        ax.text(p, h + 3.5, f"{h}%", ha='center', va='bottom', fontsize=11, fontweight='bold', color='#1D4ED8', zorder=6)

    # Data point labels for AI
    for p, a in zip(prices, ai_intent):
        ax.text(p, a + 3.5, f"{a}%", ha='center', va='bottom', fontsize=11, fontweight='bold', color='#BE123C', zorder=6)

    # Callout for Confounding error (placed in the large clear space at x=2800, y=55)
    bbox_ai = dict(boxstyle="round,pad=0.5", fc="#FFF1F2", ec="#E11D48", lw=1.5)
    ax.text(3200, 56, "AI 嚴重混淆（Confounding）：\n誤將商品漲價視為全體市場通膨，\n認定商品仍屬合理價格，導致預測完全失真！",
            ha='left', va='center', fontsize=10.5, color='#9F1239', fontweight='bold', bbox=bbox_ai, zorder=6)

    # Callout for Human Drop (placed at x=1100, y=14)
    bbox_human = dict(boxstyle="round,pad=0.5", fc="#EFF6FF", ec="#2563EB", lw=1.5)
    ax.text(1050, 14, "真人真實價格彈性：\n從 1,000 元漲至 5,000 元，\n購買意願重挫 -91%（僅剩 4%）",
            ha='left', va='center', fontsize=10, color='#1E40AF', fontweight='bold', bbox=bbox_human, zorder=6)

    # Axes and layout
    ax.set_ylim(0, 115)
    ax.set_xlim(800, 5200)
    ax.set_xticks(prices)
    ax.set_xticklabels(['1,000 元', '2,000 元', '3,000 元', '4,000 元', '5,000 元'], fontsize=11, fontweight='bold', color='#0F172A')
    ax.set_ylabel('購買意願百分比 (%)', fontsize=11, fontweight='bold', color='#334155', labelpad=10)
    ax.set_xlabel('測試產品定價 (新台幣)', fontsize=11, fontweight='bold', color='#334155', labelpad=10)
    
    ax.grid(True, linestyle=':', alpha=0.6, color='#CBD5E1', zorder=1)
    ax.set_axisbelow(True)

    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.spines['left'].set_color('#94A3B8')
    ax.spines['bottom'].set_color('#94A3B8')

    plt.title('價格敏感度混淆實驗分析（1,000 漲至 5,000 元之 AI 與真人決策脫節）', 
              fontsize=13.5, fontweight='bold', color='#1E3A8A', pad=16)
    
    # Legend at upper right (y=95 to 110 zone) - zero collision with data labels at y=85
    ax.legend(loc='upper right', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=10)

    out1 = os.path.join(OUTPUT_DIR_1, "fig3_price_sensitivity_confounding.png")
    out2 = os.path.join(OUTPUT_DIR_2, "fig3_price_sensitivity_confounding.png")
    plt.savefig(out1, dpi=300)
    plt.savefig(out2, dpi=300)
    plt.close()
    print("Fig 3 generated successfully:", out1)

if __name__ == "__main__":
    generate_fig1()
    generate_fig2()
    generate_fig3()
