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

    # 留出寬敞垂直走廊，供放置不重疊的垂直連動連接標籤與箭頭
    cur_y = inv_y - 0.36

    # =========================================================================
    # 3. 中間雙核心造血迴路：企業（左） ↔ 客戶（右）
    # 嚴格實施 3 行水平平行對稱（Parallel Row Alignment）
    # =========================================================================
    loop_top = cur_y
    node_w = 5.70
    center_w = CONTENT_W - 2 * node_w  # 14.80 - 11.40 = 3.40 吋
    node_h = 2.14
    node_y = loop_top - node_h

    # (3A) 左側節點：核心樞紐：企業（Company）
    comp_x = MX
    rounded_box(ax, comp_x, node_y, node_w, node_h, face="#F8FAFC", edge="#0284C7", lw=1.8, radius=0.08, z=2)
    rounded_box(ax, comp_x, loop_top - 0.40, node_w, 0.40, face="#E0F2FE", edge="#0284C7", lw=1.0, radius=0.06, z=3)
    ax.text(comp_x + node_w / 2, loop_top - 0.20, "核心樞紐：企業（Company）",
            fontproperties=fp(14.8, bold=True), color="#0369A1", va="center", ha="center", zorder=5)

    # (3B) 右側節點：價值源頭：客戶（Customer）
    cust_x = MX + node_w + center_w
    rounded_box(ax, cust_x, node_y, node_w, node_h, face="#F0FDF4", edge="#0D9488", lw=1.8, radius=0.08, z=2)
    rounded_box(ax, cust_x, loop_top - 0.40, node_w, 0.40, face="#CCFBF1", edge="#0D9488", lw=1.0, radius=0.06, z=3)
    ax.text(cust_x + node_w / 2, loop_top - 0.20, "價值源頭：客戶（Customer）",
            fontproperties=fp(14.8, bold=True), color="#0F766E", va="center", ha="center", zorder=5)

    # 3 個平行列槽（左：企業 vs 右：客戶，嚴格水平 100% 齊平）
    # Row 1：【想要什麼】（產值利潤 vs. 超額效益）
    # Row 2：【核心考驗】（抗拒估值誘惑 vs. 24hr解決與每週進度）
    # Row 3：【本質定律】（玩具的故事 vs. 買單是唯一地基）
    row_slot_h_node = 0.46
    row_gap_node = 0.08
    y_node_rows = [
        loop_top - 0.44,
        loop_top - 0.44 - (row_slot_h_node + row_gap_node),
        loop_top - 0.44 - 2 * (row_slot_h_node + row_gap_node),
    ]

    comp_items = [
        ("【想要什麼】", "追求健康營收與實質毛利，合理承接資本助燃以加速規模擴張。"),
        ("【核心考驗】", "抗拒短期估值誘惑，以統計模型科學排查並徹底對齊真實需求。"),
        ("【本質定律】", "《玩具的故事》— 聚焦客戶「真正珍視之物」，才能創造真價值。"),
    ]
    cust_items = [
        ("【想要什麼】", "付出的每分錢換到超額效益，業務痛點與急迫需求迅速徹底解決。"),
        ("【核心考驗】", "跨產業最在乎：出問題 24hr 搞定（85%）、每週進度更新（48%）。"),
        ("【本質定律】", "商業鐵律 — 價值在雙方交換時誕生，客戶買單是撐起估值唯一地基。"),
    ]

    for r_idx in range(3):
        ry_top = y_node_rows[r_idx]
        ry_box = ry_top - row_slot_h_node
        
        # 左欄（企業）列槽背景與文字
        rounded_box(ax, comp_x + 0.14, ry_box, node_w - 0.28, row_slot_h_node,
                    face="#F1F5F9", edge="#BAE6FD", lw=0.8, radius=0.04, z=3)
        c_label, c_desc = comp_items[r_idx]
        p_comp = Paragraph(f"**{c_label}** {c_desc}", 10.2, node_w - 0.44,
                           color="#1E293B", bold_color="#0369A1", leading=1.25)
        p_comp.draw(ax, comp_x + 0.22, ry_top - 0.12)

        # 右欄（客戶）列槽背景與文字
        rounded_box(ax, cust_x + 0.14, ry_box, node_w - 0.28, row_slot_h_node,
                    face="#F0FDF4", edge="#99F6E4", lw=0.8, radius=0.04, z=3)
        k_label, k_desc = cust_items[r_idx]
        p_cust = Paragraph(f"**{k_label}** {k_desc}", 10.2, node_w - 0.44,
                           color="#1E293B", bold_color="#0F766E", leading=1.25)
        p_cust.draw(ax, cust_x + 0.22, ry_top - 0.12)

    # (3C) 中央走廊：雙向造血箭頭加粗置中
    cx_mid = MX + node_w + center_w / 2
    cy_mid = (loop_top + node_y) / 2  # 垂直幾何中心

    # 上箭頭（企業 -> 客戶）：提供高效益（加粗至 2.8）
    arrow_y_top = cy_mid + 0.44
    ax.annotate("", xy=(cust_x - 0.08, arrow_y_top), xytext=(comp_x + node_w + 0.08, arrow_y_top),
                arrowprops=dict(arrowstyle="->,head_width=0.36,head_length=0.52", color="#0D9488", lw=2.8), zorder=4)
    rounded_box(ax, cx_mid - 1.45, arrow_y_top + 0.08, 2.90, 0.36, face="#E6FFFA", edge="#0D9488", lw=1.2, radius=0.06, z=5)
    ax.text(cx_mid, arrow_y_top + 0.26, "提供高效益（精準解決痛點） →",
            fontproperties=fp(11.5, bold=True), color="#0F766E", va="center", ha="center", zorder=6)

    # 中央大徽章：雙向造血主迴路（置中）
    rounded_box(ax, cx_mid - 1.55, cy_mid - 0.18, 3.10, 0.36, face="#0F172A", edge="#38BDF8", lw=1.5, radius=0.07, z=5)
    ax.text(cx_mid, cy_mid, "★ 雙向造血主迴路（生命之源）",
            fontproperties=fp(12.0, bold=True), color="#38BDF8", va="center", ha="center", zorder=6)

    # 下箭頭（客戶 -> 企業）：回饋真實營收毛利（加粗至 2.8）
    arrow_y_bot = cy_mid - 0.44
    ax.annotate("", xy=(comp_x + node_w + 0.08, arrow_y_bot), xytext=(cust_x - 0.08, arrow_y_bot),
                arrowprops=dict(arrowstyle="->,head_width=0.36,head_length=0.52", color="#0284C7", lw=2.8), zorder=4)
    rounded_box(ax, cx_mid - 1.45, arrow_y_bot - 0.44, 2.90, 0.36, face="#F0F9FF", edge="#0284C7", lw=1.2, radius=0.06, z=5)
    ax.text(cx_mid, arrow_y_bot - 0.26, "← 回饋真實營收與毛利（真金白銀）",
            fontproperties=fp(11.5, bold=True), color="#0369A1", va="center", ha="center", zorder=6)

    # 外部輔助垂直雙向連動（投資人 ↔ 企業：在走廊中絕對對稱居中，杜絕重疊）
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

    cur_y = node_y - 0.14

    # =========================================================================
    # 4. 單一深度焦點卡片：結構性失靈——當「助燃劑」反客為主（全寬紅橘色深度卡）
    # 嚴格實施「水平平行對齊列槽（Parallel Row Alignment）」
    # =========================================================================
    focus_top = cur_y
    focus_h = 2.76
    focus_y = focus_top - focus_h

    rounded_box(ax, MX, focus_y, CONTENT_W, focus_h, face="#FFF7F2", edge="#DC2626", lw=1.8, radius=0.08, z=2)
    # 頂部警示標題條
    rounded_box(ax, MX, focus_top - 0.36, CONTENT_W, 0.36, face="#FEE2E2", edge="#DC2626", lw=1.0, radius=0.06, z=3)
    ax.text(MX + 0.25, focus_top - 0.18,
            "● 深度焦點：【結構性失靈——當「助燃劑」反客為主（討好投資人 > 服務客戶）】",
            fontproperties=fp(14.2, bold=True), color="#991B1B", va="center", ha="left", zorder=5)

    # 副標題（誘因錯位解釋）
    ax.text(MX + 0.25, focus_top - 0.46,
            "【誘因錯位】高層為迎合資本市場每季短期估值，把心力用於取悅投資人而非服務客戶，形成「尾巴搖狗」的致命倒退：",
            fontproperties=fp(11.6, bold=True), color="#7F1D1D", va="top", ha="left", zorder=5)

    # 3 大反面案例並列子卡（等寬等高，嚴格水平平行對齊列槽）
    col_w_case = (CONTENT_W - 0.40 - 2 * 0.24) / 3  # 4.64 吋
    c_y_top = focus_top - 0.66
    c_h = 1.98  # 等高

    cases_data = [
        {
            "title": "案例一：波音 737 MAX 飛安災難",
            "rows": [
                ("【迎合短期股價】", "大搞庫藏股護盤，優先追求華爾街季度利潤"),
                ("【大砍研發品管】", "核心軟體工程低價外包，忽視工程飛安文化"),
                ("【空難重創商譽】", "釀成兩起重大空難，全球停飛、市值大蒸發"),
            ]
        },
        {
            "title": "案例二：迪士尼「賣玩具廣告」迷失",
            "rows": [
                ("【追逐周邊授權】", "追求玩具利潤，讓商業授權凌駕原創故事"),
                ("【電影淪為型錄】", "劇本硬塞無關周邊角色，犧牲核心故事品質"),
                ("【核心觀眾流失】", "影視口碑大跌，IP 光環受損導致周邊反跌"),
            ]
        },
        {
            "title": "案例三：AI 與串流泡沫的虛榮指標",
            "rows": [
                ("【盲目衝刺虛榮】", "補貼衝免洗註冊與訂閱，追求短期假象估值"),
                ("【忽視客戶留存】", "缺乏真實造血能力與 ROI，無自我造血現金流"),
                ("【熱錢退潮枯竭】", "外部資本一旦收緊，缺乏客戶買單瞬間倒閉"),
            ]
        },
    ]

    # 三列槽之全域統一 Y 座標（跨卡橫向掃視 100% 水平對齊）
    row_names = [
        "Row 1【誘因錯位】（淺層迷思）",
        "Row 2【致命短視】（中層作為）",
        "Row 3【崩盤代價】（深層惡果）",
    ]
    row_slot_h = 0.46
    row_slot_gap = 0.05
    y_case_rows = [
        c_y_top - 0.34,
        c_y_top - 0.34 - (row_slot_h + row_slot_gap),
        c_y_top - 0.34 - 2 * (row_slot_h + row_slot_gap),
    ]

    slot_styles = [
        {"face": "#FFF5F5", "edge": "#FECACA", "tag_color": "#991B1B"},  # Row 1 淺層
        {"face": "#FFF7ED", "edge": "#FED7AA", "tag_color": "#C2410C"},  # Row 2 中層
        {"face": "#FEF2F2", "edge": "#FCA5A5", "tag_color": "#7F1D1D"},  # Row 3 深層
    ]

    for c_idx, c_info in enumerate(cases_data):
        c_x = MX + 0.20 + c_idx * (col_w_case + 0.24)
        # 卡片外框
        rounded_box(ax, c_x, c_y_top - c_h, col_w_case, c_h, face="#FFFFFF", edge="#FCA5A5", lw=1.2, radius=0.06, z=3)
        # 子卡標題列
        rounded_box(ax, c_x, c_y_top - 0.28, col_w_case, 0.28, face="#FFF1F2", edge="#FCA5A5", lw=0.8, radius=0.04, z=4)
        ax.text(c_x + col_w_case / 2, c_y_top - 0.14, c_info["title"],
                fontproperties=fp(12.0, bold=True), color="#991B1B", va="center", ha="center", zorder=5)

        # 3 個列槽逐行繪製（使用絕對 Y 座標，杜絕任何行高累積偏差）
        for r_idx in range(3):
            ry_top = y_case_rows[r_idx]
            ry_box = ry_top - row_slot_h
            st = slot_styles[r_idx]
            
            # 列槽獨立圓角背景
            rounded_box(ax, c_x + 0.08, ry_box, col_w_case - 0.16, row_slot_h,
                        face=st["face"], edge=st["edge"], lw=0.8, radius=0.04, z=4)

            # 行標籤與內文（兩層結構：Row 類別 + 實質作為）
            r_tag, r_desc = c_info["rows"][r_idx]
            # 頂部小標題列：Row 名稱
            ax.text(c_x + 0.16, ry_top - 0.12, row_names[r_idx],
                    fontproperties=fp(9.2, bold=True), color=st["tag_color"], va="center", ha="left", zorder=6)
            # 內文敘述
            p_row = Paragraph(f"**{r_tag}** {r_desc}", 10.8, col_w_case - 0.32,
                              color="#1E293B", bold_color=st["tag_color"], leading=1.25)
            p_row.draw(ax, c_x + 0.16, ry_top - 0.22)

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
