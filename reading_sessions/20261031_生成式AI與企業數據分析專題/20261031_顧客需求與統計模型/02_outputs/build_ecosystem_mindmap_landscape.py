# -*- coding: utf-8 -*-
"""
build_ecosystem_mindmap_landscape.py
橫版 16:9 「顧客-企業-投資者」生態價值循環全景圖。
嚴格遵循用戶核准之優化計劃：
1. 比例：16:9 Landscape (16.0 x 9.0 吋, 4800 x 2700 px, 300 DPI)
2. 內容精簡與空間釋放：
   (a) 頂部：外部輔助迴路【投資人／資本市場（角色：助燃劑 Catalyst）】
   (b) 中間雙核心迴路：【核心樞紐：企業（Company）】與【價值源頭：客戶（Customer）】之間的雙向造血主迴路，標明「提供高效益」與「回饋真實營收毛利」
   (c) 單一深度焦點卡片：【結構性失靈——當「助燃劑」反客為主（討好投資人 > 服務客戶）】，完整保留誘因錯位與波音（737 MAX）、迪士尼（賣玩具廣告）、AI/串流泡沫三大反面案例
   (d) 底部寬幅結論橫幅（抗拒短期誘惑，對齊造血引擎，投資人才能共享長期成果）
3. 字體大幅放大：內文 11.8pt~12.5pt，卡片與節點標題 14.5pt~19pt，寬敞通透，字體飽滿清晰。
輸出：02_outputs/04_顧客-企業-投資者關係心智圖_橫版.png
"""

import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# 導入小型排版工具
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from word_layout_engine import Paragraph, rounded_box, new_canvas, fp, DPI

OUT_PATH = os.path.join(SCRIPT_DIR, "04_顧客-企業-投資者關係心智圖_橫版.png")

# 畫布尺寸：16:9
W_IN = 16.0
H_IN = 9.0
MX = 0.60
MY_TOP = 0.35
CONTENT_W = W_IN - 2 * MX  # 14.80 吋


def build_landscape_mindmap():
    fig, ax = new_canvas(W_IN, H_IN, bg="#FFFFFF")

    # =========================================================================
    # 1. 頂部大標題區 (Header)
    # =========================================================================
    title_text = "企業、客戶與投資人的價值循環：用統計模型找出顧客真正在乎的事"
    subtitle_text = "「企業與客戶」是創造價值的造血引擎，「投資人」是幫忙加速的助燃劑；本末倒置，企業就會失靈"

    p_title = Paragraph(title_text, 19.5, CONTENT_W, color="#0F172A", align="center", leading=1.2)
    p_sub = Paragraph(subtitle_text, 12.0, CONTENT_W, color="#475569", align="center", leading=1.3, space_before=0.04)

    cur_y = H_IN - MY_TOP
    cur_y = p_title.draw(ax, MX, cur_y)
    cur_y = p_sub.draw(ax, MX, cur_y)
    cur_y -= 0.10  # 標題與投資人卡片的垂直間距

    # =========================================================================
    # 2. 外部輔助迴路：投資人／資本市場（全寬橫卡，內含 3 欄並列子卡）
    # =========================================================================
    inv_top = cur_y
    inv_h = 1.16
    inv_y = inv_top - inv_h

    # 投資人背景大卡片（暖琥珀金色調）
    rounded_box(ax, MX, inv_y, CONTENT_W, inv_h, face="#FFFDF5", edge="#D97706", lw=1.6, radius=0.08, z=2)

    # 投資人標題列
    ax.text(MX + 0.22, inv_top - 0.20,
            "★ 外部輔助迴路：投資人／資本市場（角色：助燃劑 Catalyst）",
            fontproperties=fp(14.5, bold=True), color="#92400E", va="top", ha="left", zorder=5)

    # 3 個橫向項目
    col_w_inv = (CONTENT_W - 0.44 - 2 * 0.25) / 3
    inv_items = [
        ("【想要什麼】", "企業產值提高 → 自身投資獲利提高 → 願意再加碼投資擴張。"),
        ("【核心角色】", "提供擴張所需資金，事後合理分享「企業與客戶」共同創造的成果。"),
        ("【危險訊號】", "資本熱錢遠超客戶營收時，助燃劑反客為主綁架方向，導致尾巴搖狗。"),
    ]

    for idx, (label, desc) in enumerate(inv_items):
        item_x = MX + 0.22 + idx * (col_w_inv + 0.25)
        item_y = inv_top - 0.44
        p_item = Paragraph(f"**{label}** {desc}", 11.5, col_w_inv, color="#451A03", bold_color="#92400E", leading=1.35)
        p_item.draw(ax, item_x, item_y)

    # 留出 0.38 吋寬敞垂直走廊，供放置不重疊的垂直連動連接標籤與箭頭
    cur_y = inv_y - 0.38

    # =========================================================================
    # 3. 中間雙核心造血迴路：企業（左） ↔ 客戶（右）
    # =========================================================================
    loop_top = cur_y
    node_w = 5.70
    center_w = CONTENT_W - 2 * node_w  # 14.80 - 11.40 = 3.40 吋
    node_h = 2.08
    node_y = loop_top - node_h

    # (3A) 左側節點：核心樞紐：企業（Company）
    comp_x = MX
    rounded_box(ax, comp_x, node_y, node_w, node_h, face="#F8FAFC", edge="#0284C7", lw=1.8, radius=0.08, z=2)
    rounded_box(ax, comp_x, loop_top - 0.42, node_w, 0.42, face="#E0F2FE", edge="#0284C7", lw=1.0, radius=0.06, z=3)
    ax.text(comp_x + node_w / 2, loop_top - 0.21, "核心樞紐：企業（Company）",
            fontproperties=fp(15.0, bold=True), color="#0369A1", va="center", ha="center", zorder=5)

    comp_bullets = [
        "**核心任務**：抗拒短期估值誘惑，以統計模型科學排查並對齊客戶真實需求。",
        "**雙向能量**：一端合理承接投資人資金，一端向客戶交付高效益產品與服務。",
        "**經典隱喻**：《玩具的故事》—— 唯有聚焦客戶「真正珍視之物」，才能創造真價值。",
    ]
    comp_y = loop_top - 0.52
    for b in comp_bullets:
        pb = Paragraph(b, 11.6, node_w - 0.42, bullet="●", color="#1E293B", bold_color="#0369A1", leading=1.34, space_before=0.04)
        comp_y = pb.draw(ax, comp_x + 0.21, comp_y)

    # (3B) 右側節點：價值源頭：客戶（Customer）
    cust_x = MX + node_w + center_w
    rounded_box(ax, cust_x, node_y, node_w, node_h, face="#F0FDF4", edge="#0D9488", lw=1.8, radius=0.08, z=2)
    rounded_box(ax, cust_x, loop_top - 0.42, node_w, 0.42, face="#CCFBF1", edge="#0D9488", lw=1.0, radius=0.06, z=3)
    ax.text(cust_x + node_w / 2, loop_top - 0.21, "價值源頭：客戶（Customer）",
            fontproperties=fp(15.0, bold=True), color="#0F766E", va="center", ha="center", zorder=5)

    cust_bullets = [
        "**想要什麼**：付出的每一分錢換到更大的效益，痛點能迅速被徹底解決。",
        "**跨產業最在乎**：出問題時 24 小時內搞定（85%）；主動清楚的每週進度更新（48%）。",
        "**商業鐵律**：價值只在「企業與客戶」之間誕生，客戶買單是撐起估值的唯一地基。",
    ]
    cust_y = loop_top - 0.52
    for b in cust_bullets:
        pb = Paragraph(b, 11.6, node_w - 0.42, bullet="●", color="#1E293B", bold_color="#0F766E", leading=1.34, space_before=0.04)
        cust_y = pb.draw(ax, cust_x + 0.21, cust_y)

    # (3C) 中央走廊：雙向造血箭頭與說明膠囊
    cx_mid = MX + node_w + center_w / 2

    # 上箭頭（企業 -> 客戶）：提供高效益
    arrow_y_top = loop_top - 0.62
    ax.annotate("", xy=(cust_x - 0.08, arrow_y_top), xytext=(comp_x + node_w + 0.08, arrow_y_top),
                arrowprops=dict(arrowstyle="->,head_width=0.32,head_length=0.48", color="#0D9488", lw=2.2), zorder=4)
    rounded_box(ax, cx_mid - 1.45, arrow_y_top + 0.08, 2.90, 0.38, face="#E6FFFA", edge="#0D9488", lw=1.2, radius=0.06, z=5)
    ax.text(cx_mid, arrow_y_top + 0.27, "提供高效益（精準解決痛點） →",
            fontproperties=fp(11.6, bold=True), color="#0F766E", va="center", ha="center", zorder=6)

    # 中央大徽章：雙向造血主迴路
    badge_y = loop_top - 1.05
    rounded_box(ax, cx_mid - 1.55, badge_y - 0.18, 3.10, 0.36, face="#0F172A", edge="#38BDF8", lw=1.4, radius=0.07, z=5)
    ax.text(cx_mid, badge_y, "★ 雙向造血主迴路（生命之源）",
            fontproperties=fp(12.0, bold=True), color="#38BDF8", va="center", ha="center", zorder=6)

    # 下箭頭（客戶 -> 企業）：回饋真實營收毛利
    arrow_y_bot = loop_top - 1.48
    ax.annotate("", xy=(comp_x + node_w + 0.08, arrow_y_bot), xytext=(cust_x - 0.08, arrow_y_bot),
                arrowprops=dict(arrowstyle="->,head_width=0.32,head_length=0.48", color="#0284C7", lw=2.2), zorder=4)
    rounded_box(ax, cx_mid - 1.45, arrow_y_bot - 0.44, 2.90, 0.38, face="#F0F9FF", edge="#0284C7", lw=1.2, radius=0.06, z=5)
    ax.text(cx_mid, arrow_y_bot - 0.25, "← 回饋真實營收與毛利（真金白銀）",
            fontproperties=fp(11.6, bold=True), color="#0369A1", va="center", ha="center", zorder=6)

    # 外部輔助垂直雙向連動（投資人 ↔ 企業：在 0.38 吋寬走廊中絕對對稱居中，杜絕重疊）
    comp_cx = comp_x + node_w / 2  # 企業卡幾何中心 X
    gap_mid_y = (inv_y + loop_top) / 2  # 垂直間距幾何中心
    con_w = 2.90
    con_h = 0.26
    rounded_box(ax, comp_cx - con_w / 2, gap_mid_y - con_h / 2, con_w, con_h,
                face="#FFFBEB", edge="#D97706", lw=1.1, radius=0.05, z=5)
    ax.text(comp_cx, gap_mid_y, "資本挹注（助燃）與 投資回報（共享）",
            fontproperties=fp(10.2, bold=True), color="#92400E", va="center", ha="center", zorder=6)

    # 兩側輔助雙向垂直箭頭
    arr_lx = comp_cx - con_w / 2 - 0.20
    arr_rx = comp_cx + con_w / 2 + 0.20
    ax.annotate("", xy=(arr_lx, loop_top + 0.03), xytext=(arr_lx, inv_y - 0.03),
                arrowprops=dict(arrowstyle="->,head_width=0.22,head_length=0.32", color="#D97706", lw=1.6), zorder=4)
    ax.annotate("", xy=(arr_rx, inv_y - 0.03), xytext=(arr_rx, loop_top + 0.03),
                arrowprops=dict(arrowstyle="->,head_width=0.22,head_length=0.32", color="#D97706", lw=1.6), zorder=4)

    cur_y = node_y - 0.16

    # =========================================================================
    # 4. 單一深度焦點卡片：結構性失靈——當「助燃劑」反客為主（全寬紅橘色深度卡）
    # =========================================================================
    focus_top = cur_y
    focus_h = 2.76
    focus_y = focus_top - focus_h

    rounded_box(ax, MX, focus_y, CONTENT_W, focus_h, face="#FFF7F2", edge="#DC2626", lw=1.8, radius=0.08, z=2)
    # 頂部警示標題條
    rounded_box(ax, MX, focus_top - 0.38, CONTENT_W, 0.38, face="#FEE2E2", edge="#DC2626", lw=1.0, radius=0.06, z=3)
    ax.text(MX + 0.25, focus_top - 0.19,
            "● 深度焦點：【點 1：結構性失靈——當「助燃劑」反客為主（討好投資人 > 服務客戶）】",
            fontproperties=fp(14.5, bold=True), color="#991B1B", va="center", ha="left", zorder=5)

    # 副標題（誘因錯位解釋）
    ax.text(MX + 0.25, focus_top - 0.50,
            "【誘因錯位】高層為迎合資本市場每季短期估值，把心力用於取悅投資人而非服務客戶，形成「尾巴搖狗」的致命倒退：",
            fontproperties=fp(11.8, bold=True), color="#7F1D1D", va="top", ha="left", zorder=5)

    # 3 大反面案例並列子卡（寬幅 3 欄佈局，垂直高度由 1.70 擴展至 1.96 吋，徹底杜絕文字溢出卡片）
    col_w_case = (CONTENT_W - 0.40 - 2 * 0.24) / 3
    cases = [
        ("案例一：波音 737 MAX 飛安災難", [
            ("轉向股東價值至上", "重心由工程飛安轉為華爾街每季獲利。"),
            ("大砍品管研發預算", "大筆現金用於庫藏股護盤，外包核心軟體工程。"),
            ("致命慘痛代價", "釀成兩起重大空難，全球停飛、商譽掃地，市值蒸發。"),
        ]),
        ("案例二：迪士尼「賣玩具廣告」迷失", [
            ("周邊利潤反客為主", "為追求玩具與周邊授權利潤，策略凌駕創作故事。"),
            ("電影淪為廣告展示", "劇本強塞無意義之周邊角色，犧牲故事品質與口碑。"),
            ("衍生連鎖反噬", "核心影視受眾流失，品牌光環受損，周邊銷售連帶下滑。"),
        ]),
        ("案例三：AI 與串流泡沫的虛榮指標", [
            ("追逐短暫假象指標", "盲目補貼衝刺免洗註冊量與紙面訂閱數以推高估值。"),
            ("漠視客戶真實留存", "忽視客戶實質留存率與商業 ROI，缺乏真實現金流。"),
            ("熱錢退潮瞬間枯竭", "外部資本一旦收緊，缺乏自我造血能力的企業應聲倒地。"),
        ]),
    ]

    c_y_top = focus_top - 0.70
    c_h = focus_h - 0.80  # 1.96 吋，空間極度寬裕
    for c_idx, (c_title, c_bullets) in enumerate(cases):
        c_x = MX + 0.20 + c_idx * (col_w_case + 0.24)
        rounded_box(ax, c_x, focus_y + 0.10, col_w_case, c_h, face="#FFFFFF", edge="#FCA5A5", lw=1.2, radius=0.06, z=3)
        # 子卡標題
        rounded_box(ax, c_x, c_y_top - 0.32, col_w_case, 0.32, face="#FFF1F2", edge="#FCA5A5", lw=0.8, radius=0.04, z=4)
        ax.text(c_x + col_w_case / 2, c_y_top - 0.16, c_title,
                fontproperties=fp(12.2, bold=True), color="#991B1B", va="center", ha="center", zorder=5)

        # 案例列表（嚴密量測，留出 0.3 吋以上安全下底邊界）
        by = c_y_top - 0.38
        for b_tag, b_desc in c_bullets:
            p_b = Paragraph(f"**{b_tag}**：{b_desc}", 11.2, col_w_case - 0.30, bullet="•",
                            color="#334155", bold_color="#991B1B", leading=1.30, space_before=0.02)
            by = p_b.draw(ax, c_x + 0.15, by)

    cur_y = focus_y - 0.12

    # =========================================================================
    # 5. 底部寬幅結論橫幅（深色穩健大底）
    # =========================================================================
    banner_top = cur_y
    banner_h = 0.92
    banner_y = banner_top - banner_h

    rounded_box(ax, MX, banner_y, CONTENT_W, banner_h, face="#0F172A", edge="#38BDF8", lw=1.5, radius=0.08, z=2)

    ax.text(MX + 0.25, banner_top - 0.20,
            "★ 核心策略結論：抗拒短期誘惑，對齊造血引擎，投資人才能共享長期成果",
            fontproperties=fp(13.5, bold=True), color="#FBBF24", va="top", ha="left", zorder=5)

    conclusion_body = (
        "真正的商業價值永遠誕生於「企業與客戶」的雙向造血迴路，資本市場的資金只是加速的助燃劑。"
        "企業唯有放下直覺執念，用統計模型找出客戶真正在乎的少數關鍵並徹底對齊，才能以健康的真金白銀營收毛利，"
        "支撐起長期穩健的市值溢價。"
    )
    p_banner = Paragraph(conclusion_body, 11.5, CONTENT_W - 0.50, color="#F8FAFC", bold_color="#FBBF24", leading=1.35)
    p_banner.draw(ax, MX + 0.25, banner_top - 0.46)

    # 底部來源備註
    source_text = "資料來源：Vikas Mittal et al. (2025), Harvard Business Review; Thomas H. Davenport & J. Fitts (2025)."
    ax.text(MX, 0.16, source_text,
            fontproperties=fp(9.0), color="#64748B", va="top", ha="left", zorder=5)

    plt.savefig(OUT_PATH, dpi=DPI, facecolor="#FFFFFF")
    plt.close(fig)
    print("Landscape ecosystem mindmap successfully saved:", OUT_PATH)


if __name__ == "__main__":
    build_landscape_mindmap()
