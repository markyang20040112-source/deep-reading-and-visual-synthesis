# -*- coding: utf-8 -*-
"""
三大科學園區產業營業額與公司分布數據敘事 — 出版級單面板統計圖生成腳本
嚴格遵守：
1. 黑盒呼叫 scripts/hcl_color_engine.py (Gephi · pastel 鎖定色票與 CIELAB 插值)
2. 兩段式安全轉型與三層互斥分流斷言 (assert len(df_detail) + len(df_other) + len(df_subtotal) == len(df_raw))
3. Medium 模式 2 張獨立單面板 300 DPI .png 跨檔色彩接力 (圖 1 暖杏蜜橘 #ECA072 破題 -> 圖 2 霧靄青藍 #5DBACD 深挖)
4. 零 Emoji 鐵律 (僅用微軟正黑體原生幾何符號 ★ ▲ ● ■) 與底部三重時間戳記官方圖註
"""

import os
import sys
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 載入黑盒色彩與防呆分流引擎
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(os.path.dirname(SESSION_DIR))
ENGINE_DIR = os.path.join(PROJECT_ROOT, ".agents", "skills", "deep-reading-and-visual-synthesis", "scripts")
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

from hcl_color_engine import (
    GEPHI_QUALITATIVE_HEX,
    GEPHI_LIGHT_BADGE_TINTS,
    GEPHI_SEQUENTIAL_SCALES,
    GEPHI_DIVERGING_SCALE,
    GEPHI_DISCRETE_NEUTRALS,
    get_sequential_color,
    get_diverging_color,
    bind_qualitative_colors,
    get_category_badge_tint,
    despine_axes,
    load_and_split_csv,
)

# 設定全局無襯線正黑體與負號顯示
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "PingFang TC", "Noto Sans CJK TC", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.facecolor"] = "#F8FAFC"
plt.rcParams["axes.facecolor"] = "#FFFFFF"


def _df_to_records(df_obj):
    if hasattr(df_obj, "_rows"):
        return list(df_obj._rows)
    return df_obj.to_dict("records")


def load_all_verified_datasets():
    """
    依《資料說明書》規範執行 UTF-8 BOM 探測、兩段式安全轉型與三層互斥分流斷言。
    """
    data_dir = os.path.join(SESSION_DIR, "data")

    # 1. 營業額統計表 (Dataset ID: 7597)
    rev_path = os.path.join(data_dir, "國家科學及技術委員會科學園區產業營業額統計表.csv")
    rev_num_cols = [
        "積體電路產業營業額(億元)", "光電產業營業額(億元)", "電腦及周邊產業營業額(億元)",
        "通訊產業營業額(億元)", "精密機械產業營業額(億元)", "生物技術產業營業額(億元)",
        "其他產業營業額(億元)", "總計營業額(億元)"
    ]
    df_rev_raw, df_rev_detail, df_rev_other, df_rev_subtotal, _ = load_and_split_csv(
        rev_path,
        numeric_cols=rev_num_cols,
        label_cols=["園區別", "子園區"],
        subtotal_keywords=["合計", "總計", "小計"],
        other_keywords=["其他"],
    )
    assert len(df_rev_detail) + len(df_rev_other) + len(df_rev_subtotal) == len(df_rev_raw), "營業額三層互斥分流筆數不守恆！"
    assert len(df_rev_detail) == 15 and len(df_rev_subtotal) == 4, f"營業額分流列數異常：{len(df_rev_detail)}, {len(df_rev_subtotal)}"

    # 2. 產業類別及家數統計 (Dataset ID: 7596)
    cnt_path = os.path.join(data_dir, "國家科學及技術委員會科學園區產業類別及家數統計.csv")
    cnt_num_cols = [
        "積體電路(家)", "光電(家)", "電腦及周邊(家)", "通訊(家)",
        "精密機械(家)", "生物技術(家)", "其他家數", "總計家數"
    ]
    df_cnt_raw, df_cnt_detail, df_cnt_other, df_cnt_subtotal, _ = load_and_split_csv(
        cnt_path,
        numeric_cols=cnt_num_cols,
        label_cols=["園區別", "子園區"],
        subtotal_keywords=["合計", "總計", "小計"],
        other_keywords=["其他"],
    )
    assert len(df_cnt_detail) + len(df_cnt_other) + len(df_cnt_subtotal) == len(df_cnt_raw), "廠商家數三層互斥分流筆數不守恆！"
    assert len(df_cnt_detail) == 34 and len(df_cnt_subtotal) == 8, f"廠商家數分流列數異常：{len(df_cnt_detail)}, {len(df_cnt_subtotal)}"

    cnt_records = _df_to_records(df_cnt_detail)
    cnt_reg_records = [r for r in cnt_records if r["統計項目"] == "已入區登記廠商家數"]
    cnt_app_records = [r for r in cnt_records if r["統計項目"] == "有效核准廠商家數"]
    assert len(cnt_reg_records) == 17 and len(cnt_app_records) == 17

    # 3. 從業員工數統計 (Dataset ID: 7599)
    emp_path = os.path.join(data_dir, "國家科學及技術委員會科學園區從業員工數統計.csv")
    emp_num_cols = ["博士(人)", "碩士(人)", "大學(人)", "專科(人)", "高中(人)", "其他(人)", "總人數"]
    df_emp_raw, df_emp_detail, df_emp_other, df_emp_subtotal, _ = load_and_split_csv(
        emp_path,
        numeric_cols=emp_num_cols,
        label_cols=["園區別", "子園區"],
        subtotal_keywords=["合計", "總計", "小計"],
        other_keywords=["其他"],
    )
    assert len(df_emp_detail) + len(df_emp_other) + len(df_emp_subtotal) == len(df_emp_raw), "員工數三層互斥分流筆數不守恆！"
    assert len(df_emp_detail) == 17 and len(df_emp_subtotal) == 4, f"員工數分流列數異常：{len(df_emp_detail)}, {len(df_emp_subtotal)}"

    return {
        "rev_records": _df_to_records(df_rev_detail),
        "cnt_reg_records": cnt_reg_records,
        "cnt_app_records": cnt_app_records,
        "emp_records": _df_to_records(df_emp_detail),
    }


def draw_chart_01_hook(datasets, out_path):
    """
    圖 1 (01_chart_hook.png)：暖杏蜜橘 (#ECA072) 破題單面板配對雙柱＋剪刀差標註圖
    比較六大核心產業＋原表其他項之「已入區登記廠商家數占比 (%)」vs.「營業額占比 (%)」
    """
    rev_recs = datasets["rev_records"]
    reg_recs = datasets["cnt_reg_records"]
    app_recs = datasets["cnt_app_records"]

    def sum_col(recs, col):
        return sum(float(r[col]) for r in recs)

    industries = [
        {
            "key": "生物技術",
            "tier1": "【生物技術】",
            "tier2": "入區241家奪冠\n核准287家第一",
            "reg_cnt": int(round(sum_col(reg_recs, "生物技術(家)"))),
            "app_cnt": int(round(sum_col(app_recs, "生物技術(家)"))),
            "rev_val": sum_col(rev_recs, "生物技術產業營業額(億元)"),
            "is_other": False,
        },
        {
            "key": "積體電路",
            "tier1": "【積體電路】",
            "tier2": "入區236家第二\n晶圓製造巨艦群",
            "reg_cnt": int(round(sum_col(reg_recs, "積體電路(家)"))),
            "app_cnt": int(round(sum_col(app_recs, "積體電路(家)"))),
            "rev_val": sum_col(rev_recs, "積體電路產業營業額(億元)"),
            "is_other": False,
        },
        {
            "key": "精密機械",
            "tier1": "【精密機械】",
            "tier2": "入區162家第三\n中南科核准第一",
            "reg_cnt": int(round(sum_col(reg_recs, "精密機械(家)"))),
            "app_cnt": int(round(sum_col(app_recs, "精密機械(家)"))),
            "rev_val": sum_col(rev_recs, "精密機械產業營業額(億元)"),
            "is_other": False,
        },
        {
            "key": "光電產業",
            "tier1": "【光電產業】",
            "tier2": "入區156家第四\n面板與光學聚落",
            "reg_cnt": int(round(sum_col(reg_recs, "光電(家)"))),
            "app_cnt": int(round(sum_col(app_recs, "光電(家)"))),
            "rev_val": sum_col(rev_recs, "光電產業營業額(億元)"),
            "is_other": False,
        },
        {
            "key": "電腦及周邊",
            "tier1": "【電腦周邊】",
            "tier2": "入區88家第五\nAI伺服器與硬體",
            "reg_cnt": int(round(sum_col(reg_recs, "電腦及周邊(家)"))),
            "app_cnt": int(round(sum_col(app_recs, "電腦及周邊(家)"))),
            "rev_val": sum_col(rev_recs, "電腦及周邊產業營業額(億元)"),
            "is_other": False,
        },
        {
            "key": "通訊產業",
            "tier1": "【通訊產業】",
            "tier2": "入區59家第六\n網通與衛星設備",
            "reg_cnt": int(round(sum_col(reg_recs, "通訊(家)"))),
            "app_cnt": int(round(sum_col(app_recs, "通訊(家)"))),
            "rev_val": sum_col(rev_recs, "通訊產業營業額(億元)"),
            "is_other": False,
        },
        {
            "key": "原表其他項",
            "tier1": "【原表其他】",
            "tier2": "入區42家未細分\n非六大核心事業",
            "reg_cnt": int(round(sum_col(reg_recs, "其他家數"))),
            "app_cnt": int(round(sum_col(app_recs, "其他家數"))),
            "rev_val": sum_col(rev_recs, "其他產業營業額(億元)"),
            "is_other": True,
        },
    ]

    total_reg = sum(d["reg_cnt"] for d in industries)
    total_app = sum(d["app_cnt"] for d in industries)
    total_rev = sum_col(rev_recs, "總計營業額(億元)")
    assert total_reg == 984 and total_app == 1181, f"純明細家數總和驗證失敗：{total_reg}, {total_app}"
    assert abs(total_rev - 58010.23) < 0.05, f"純明細營業額總和驗證失敗：{total_rev}"

    for d in industries:
        d["reg_pct"] = d["reg_cnt"] / total_reg * 100.0
        d["app_pct"] = d["app_cnt"] / total_app * 100.0
        d["rev_pct"] = d["rev_val"] / total_rev * 100.0

    # 建立單面板畫布 (14.2" x 8.6", 300 DPI)
    fig, ax = plt.subplots(figsize=(14.2, 8.6), dpi=300)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#FFFFFF")
    plt.subplots_adjust(left=0.068, right=0.965, top=0.80, bottom=0.22)

    x = np.arange(len(industries))
    width = 0.35

    orange_main = GEPHI_QUALITATIVE_HEX[0]               # #ECA072
    orange_deep = GEPHI_SEQUENTIAL_SCALES["orange"][3]   # #CA6F35
    orange_dark = GEPHI_SEQUENTIAL_SCALES["orange"][4]   # #97481B
    blue_main = GEPHI_QUALITATIVE_HEX[1]                 # #5DBACD
    blue_deep = GEPHI_SEQUENTIAL_SCALES["blue"][3]       # #2C8B9F
    blue_dark = GEPHI_SEQUENTIAL_SCALES["blue"][4]       # #0E5B6B
    gray_other = GEPHI_DISCRETE_NEUTRALS["other_aggregated"]  # #CBD5E1

    left_colors, left_edges, right_colors, right_edges = [], [], [], []
    for d in industries:
        if d["is_other"]:
            left_colors.append(gray_other)
            left_edges.append("#94A3B8")
            right_colors.append("#E2E8F0")
            right_edges.append("#94A3B8")
        elif d["key"] == "生物技術":
            left_colors.append(orange_deep)
            left_edges.append(orange_dark)
            right_colors.append(blue_main)
            right_edges.append(blue_deep)
        elif d["key"] == "積體電路":
            left_colors.append(orange_main)
            left_edges.append(orange_deep)
            right_colors.append(blue_deep)
            right_edges.append(blue_dark)
        else:
            left_colors.append(orange_main)
            left_edges.append(orange_deep)
            right_colors.append(blue_main)
            right_edges.append(blue_deep)

    reg_pcts = [d["reg_pct"] for d in industries]
    rev_pcts = [d["rev_pct"] for d in industries]

    # 為焦點「生物技術」繪製極淡暖杏背景高亮帶 (#FFF3EA 零 Alpha 節點色)
    ax.axvspan(-0.48, 0.48, color=GEPHI_LIGHT_BADGE_TINTS[0], zorder=0)
    ax.text(
        0.0, 95.5, "★ 全區家數雙料冠軍",
        ha="center", va="center", fontsize=10.2, fontweight="bold", color=orange_dark,
        bbox=dict(boxstyle="round,pad=0.32", facecolor="#FFFFFF", edgecolor=orange_deep, linewidth=1.3),
        zorder=5
    )

    ax.bar(
        x - width / 2, reg_pcts, width=width,
        color=left_colors, edgecolor=left_edges, linewidth=1.4, zorder=3,
        label="已入區登記廠商家數占比（%，全國共 984 家）"
    )
    ax.bar(
        x + width / 2, rev_pcts, width=width,
        color=right_colors, edgecolor=right_edges, linewidth=1.4, zorder=3,
        label="全年營業額占比（%，全國共 58,010.23 億元）"
    )

    despine_axes(ax, grid_axis="y", grid_color="#CBD5E1", grid_linestyle="--", grid_alpha=0.65)
    ax.set_ylim(0, 103)
    ax.set_xlim(-0.58, len(industries) - 0.42)
    ax.set_ylabel("占全國科學園區總計之百分比（%）", fontsize=11.5, fontweight="bold", color="#1E293B", labelpad=8)
    ax.tick_params(axis="y", labelsize=10.5, colors="#334155")
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_yticklabels(["0%", "20%", "40%", "60%", "80%", "100%"])

    ax.set_xticks(x)
    ax.set_xticklabels([""] * len(industries))
    ax.tick_params(axis="x", length=0)

    # 繪製柱頂直接數據標籤
    for idx, d in enumerate(industries):
        lx = x[idx] - width / 2
        rx = x[idx] + width / 2
        ly = d["reg_pct"]
        ry = d["rev_pct"]

        ax.text(
            lx, ly + 1.3,
            f"{ly:.1f}%\n({d['reg_cnt']}家)",
            ha="center", va="bottom",
            fontsize=9.8 if idx < 4 else 9.2,
            fontweight="bold" if idx < 3 else "normal",
            color=orange_dark if idx == 0 else "#1E293B",
            linespacing=1.15,
            zorder=5
        )

        if idx == 0:
            ax.text(
                rx + 0.02, ry + 1.1,
                f"{ry:.2f}%\n(520億)",
                ha="center", va="bottom",
                fontsize=9.8, fontweight="bold", color=blue_dark,
                linespacing=1.15, zorder=5
            )
        elif idx == 1:
            ax.text(
                rx, ry + 1.3,
                f"{ry:.1f}%\n(48,293億)",
                ha="center", va="bottom",
                fontsize=10.0, fontweight="bold", color=blue_dark,
                linespacing=1.15, zorder=5
            )
        else:
            rev_str = f"{d['rev_val']:,.0f}億"
            ax.text(
                rx, ry + 1.3,
                f"{ry:.1f}%\n({rev_str})",
                ha="center", va="bottom",
                fontsize=9.2, fontweight="normal", color="#334155",
                linespacing=1.15, zorder=5
            )

    # === 顯式剪刀差標註 1：生物技術（置於 x=0 正上方高亮區內，完全不碰觸 x=1 積體電路柱與箭頭！） ===
    x_bio_l = x[0] - width / 2
    x_bio_r = x[0] + width / 2
    ax.plot([x_bio_l, x_bio_r + 0.08], [24.49, 24.49], linestyle="--", color=orange_dark, linewidth=1.3, zorder=4)
    ax.annotate(
        "", xy=(x_bio_r, 24.3), xytext=(x_bio_r, 10.2),
        arrowprops=dict(arrowstyle="<->", color=orange_dark, lw=1.8),
        zorder=5
    )
    ax.annotate(
        "▲ 生技 27.2 倍反差\n"
        "• 入區241家(24.5%)奪冠\n"
        "• 核准287家(24.3%)第一\n"
        "• 營收僅520億(0.90%)，\n"
        "  處臨床與高階研發期\n"
        "  (竹科進口年增+28.2%)",
        xy=(x_bio_l, 33.8), xytext=(0.0, 62.5),
        ha="center", va="center", fontsize=9.3, color="#1E293B", linespacing=1.35,
        bbox=dict(boxstyle="round,pad=0.42", facecolor="#FFFFFF", edgecolor=orange_deep, linewidth=1.5),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.0", color=orange_deep, lw=1.6),
        zorder=6
    )

    # === 顯式剪刀差標註 2：積體電路（24.0% 廠商撐起 83.2% 營業額，置於 x=1.75 右側開闊區） ===
    x_ic_l = x[1] - width / 2
    x_ic_r = x[1] + width / 2
    ax.plot([x_ic_l - 0.05, x_ic_r], [83.25, 83.25], linestyle="--", color=blue_dark, linewidth=1.3, zorder=4)
    ax.annotate(
        "", xy=(x_ic_l, 83.0), xytext=(x_ic_l, 33.5),
        arrowprops=dict(arrowstyle="<->", color=blue_dark, lw=1.8),
        zorder=5
    )
    ax.annotate(
        "● 晶圓製造巨艦效應（Δ = +59.3 個百分點）\n"
        "• 236 家廠商 (24.0%) 創造 48,292.6 億元 (83.25%)\n"
        "• 平均每家營收高達 204.6 億元（生技每家 2.16 億元）",
        xy=(x_ic_r + 0.04, 75.5), xytext=(1.75, 75.5),
        ha="left", va="center", fontsize=9.8, color="#1E293B", linespacing=1.36,
        bbox=dict(boxstyle="round,pad=0.48", facecolor=GEPHI_LIGHT_BADGE_TINTS[1], edgecolor=blue_deep, linewidth=1.5),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.08", color=blue_deep, lw=1.6),
        zorder=6
    )

    # === 結構對照標註 3：精密機械與非 IC 隱形冠軍群（置於 x=2.35 右側中段開闊區） ===
    ax.annotate(
        "■ 精密機械穩居第 3 大聚落（入區 162 家 / 核准 228 家）\n"
        "• 在中科 (核准 89 家) 與南科 (核准 84 家) 廠商家數皆高居該園區第 1 名！\n"
        "• 支撐半導體與生醫自動化設備，114 年精密機械進口額亦穩健年增 +12.85%",
        xy=(x[2] - width / 2, 25.0), xytext=(2.35, 45.5),
        ha="left", va="center", fontsize=9.6, color="#1E293B", linespacing=1.36,
        bbox=dict(boxstyle="round,pad=0.46", facecolor=GEPHI_LIGHT_BADGE_TINTS[2], edgecolor=GEPHI_QUALITATIVE_HEX[2], linewidth=1.4),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.15", color="#C46487", lw=1.5),
        zorder=6
    )

    # === 底部 X 軸雙層水平 0° 對齊標籤 ===
    for idx, d in enumerate(industries):
        t1_color = orange_dark if idx == 0 else ("#475569" if d["is_other"] else "#0F172A")
        t2_color = "#64748B" if d["is_other"] else "#334155"
        ax.text(
            x[idx], -4.2, d["tier1"],
            ha="center", va="top", fontsize=10.8, fontweight="bold", color=t1_color,
            clip_on=False
        )
        ax.text(
            x[idx], -9.2, d["tier2"],
            ha="center", va="top", fontsize=9.2, fontweight="normal", color=t2_color,
            linespacing=1.28, clip_on=False
        )

    leg = ax.legend(
        loc="upper right", bbox_to_anchor=(0.99, 0.99), ncol=2, frameon=True,
        facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=10.2
    )
    leg.get_frame().set_linewidth(1.1)

    fig.text(
        0.04, 0.935,
        "營收僅占 0.9% 卻撐起最多企業！生物技術奪下科學園區廠商家數雙料冠軍",
        fontsize=17.5, fontweight="bold", color="#0F172A", ha="left", va="top"
    )
    fig.text(
        0.04, 0.885,
        "三大科學園區各產業「已入區登記廠商家數占比」vs.「全年營業額占比」剪刀差對比 —— 跳脫產值單一視角，看見 241 家生技與 162 家精密機械的聚落底氣",
        fontsize=11.5, fontweight="normal", color="#475569", ha="left", va="top"
    )

    footnote_text = (
        "資料來源：國家科學及技術委員會《國家科學及技術委員會科學園區產業類別及家數統計》(政府資料開放平臺 dataset/7596) 及《國家科學及技術委員會科學園區產業營業額統計表》(dataset/7597)。\n"
        "時間戳記：營業額涵蓋期間為 2025 年（民國 114 年）全年（平臺更新：2026-06-22）；廠商家數為最新存量快照（平臺更新：2026-09-29）；本次檢視與分析日期：2026-11-07。\n"
        "統計樣本與雙重消歧說明：全數依剔除園區合計與全區總計列後之純子園區明細重算（家數明細 N = 17 子園區，已入區總計 984 家、有效核准總計 1,181 家；營業額明細 N = 15 子園區，總計 58,010.23 億元；\n"
        "最右側【原表其他】為官方原表未歸入六大核心產業之園區事業合計：已入區 42 家占 4.27%、營業額 294.39 億元占 0.51%，以中性淺灰 #CBD5E1 獨立標示）。授權條款：政府資料開放授權條款－第 1 版。"
    )
    fig.text(
        0.04, 0.015, footnote_text,
        fontsize=8.8, color="#475569", ha="left", va="bottom", linespacing=1.32
    )

    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"[Chart 1 生成完畢] -> {out_path}")


def draw_chart_02_drilldown(datasets, out_path):
    """
    圖 2 (02_chart_drilldown.png)：霧靄青藍 (#5DBACD) 次色循序漸層深挖單面板圖
    拆解科學園區子園區「博士研發人才密度 (%)」排行與「碩博士占比／生技及非 IC 產值結構」交叉對照
    """
    emp_recs = datasets["emp_records"]
    park_short = {"新竹科學園區": "竹科", "中部科學園區": "中科", "南部科學園區": "南科"}

    merged = []
    for er in emp_recs:
        tot_n = int(round(float(er["總人數"])))
        phd_n = int(round(float(er["博士(人)"])))
        ms_n = int(round(float(er["碩士(人)"])))
        phd_pct = (phd_n / tot_n * 100.0) if tot_n > 0 else float("nan")
        ms_phd_pct = ((phd_n + ms_n) / tot_n * 100.0) if tot_n > 0 else float("nan")
        lbl = f"{park_short.get(er['園區別'], er['園區別'])}・{er['子園區']}"
        merged.append({
            "園區別": er["園區別"],
            "子園區": er["子園區"],
            "label": lbl,
            "總人數": tot_n,
            "博士(人)": phd_n,
            "碩士(人)": ms_n,
            "phd_pct": phd_pct,
            "ms_phd_pct": ms_phd_pct,
        })

    valid_vals = [r["phd_pct"] for r in merged if not math.isnan(r["phd_pct"])]
    na_count = sum(1 for r in merged if math.isnan(r["phd_pct"]))
    assert len(valid_vals) == 16 and na_count == 1, "子園區博士占比有效與 NA 筆數不符預期！"
    v_min = min(valid_vals)  # 0.00%
    v_max = max(valid_vals)  # 6.994%

    merged.sort(key=lambda r: (-1.0 if math.isnan(r["phd_pct"]) else r["phd_pct"], r["總人數"]))

    role_annotations = {
        "中科・中興園區": "★ 博士密度全國第 1｜碩博占 44.0%｜生技占營收 88.6%（總營收 20.6 億）",
        "竹科・新竹生醫園區": "★ 博士密度全國第 2｜碩博占 44.7%｜100% 純生技聚落（入區 70 家／46.2 億）",
        "竹科・新竹園區": "● IC 設計與研發總部核心｜碩博占 45.7%｜博士 4,822 人（總營收 15,863.8 億）",
        "竹科・竹南園區": "● 光電與精機研發基地｜碩博占 31.7%｜非 IC 占 91.0%（生技 41.8 億／精機 154.0 億）",
        "南科・高雄園區": "■ 南台灣醫材與精機重鎮｜入區生技 33 家、精機 21 家｜非 IC 占 80.0%（1,153.5 億）",
        "中科・后里園區": "● 記憶體與封測基地｜碩博占 34.4%｜IC 占 88.1%、精機 96.2 億（2,198.8 億）",
        "南科・臺南園區": "▲ 全國最大晶圓製造巨艦｜營收 28,551.3 億占全國 49.2%（生技 113.0 億亦居第 2）",
        "竹科・龍潭園區": "● 先進封裝與光電基地｜碩博占 23.5%｜總營收 315.3 億元",
        "南科・楠梓園區": "● 先進製程擴建新園區｜碩博占 49.1%（6,082 人已進駐，統計期營收帳面 0 億）",
        "中科・台中園區": "▲ 中台灣晶圓量產主力｜營收 8,854.5 億全國第 3（生技營收 115.4 億高居全國第 1！）",
        "竹科・宜蘭園區": "■ 數位軟體與生技輕製造｜非 IC 占 100%（生技營收占 43.0%｜入區生技 13 家）",
        "南科・嘉義園區": "● 新設先進封裝與生醫園區｜碩博占 49.1%（2,175 人進駐，核准生技 3 家、精機 1 家）",
        "中科・虎尾園區": "■ 製藥與生技高成長聚落｜非 IC 占 100%（生技營收 20.0 億占該區 34.8%）",
        "竹科・銅鑼園區": "● 車用半導體與生技基地｜總營收 196.7 億元（生技 24.5 億、精機 20.7 億）",
        "中科・二林園區": "■ 精密機械擴建新基地｜核准精機 20 家、生技 4 家｜總營收 172.4 億元",
        "南科・橋頭園區": "● 初期營運新設園區｜總人數 440 人（博士 0 人，核准精機 12 家、生技 3 家）",
        "南科・屏東園區": "■ 籌備建廠期（總人數 0 人，博士占比分母為 0 屬合法 NA 缺漏，核准 12 家）",
    }

    fig, ax = plt.subplots(figsize=(14.8, 9.8), dpi=300)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#FFFFFF")
    plt.subplots_adjust(left=0.14, right=0.965, top=0.79, bottom=0.155)

    y = np.arange(len(merged))
    bar_height = 0.64

    ax.axhspan(len(merged) - 2.48, len(merged) - 0.42, color=GEPHI_LIGHT_BADGE_TINTS[1], zorder=0)

    bar_colors, bar_edges, plot_vals = [], [], []
    for row in merged:
        val = row["phd_pct"]
        if math.isnan(val):
            bar_colors.append(GEPHI_DISCRETE_NEUTRALS["na_missing"])  # #D9D9D9
            bar_edges.append("#94A3B8")
            plot_vals.append(0.18)
        else:
            c = get_sequential_color(float(val), v_min, v_max, scale="blue", discrete_steps=False)
            bar_colors.append(c)
            if val >= 6.0:
                bar_edges.append("#0E5B6B")
            elif val >= 2.0:
                bar_edges.append("#2C8B9F")
            else:
                bar_edges.append("#5DBACD")
            plot_vals.append(float(val))

    ax.barh(
        y, plot_vals, height=bar_height,
        color=bar_colors, edgecolor=bar_edges, linewidth=1.35, zorder=3
    )

    despine_axes(ax, grid_axis="x", grid_color="#CBD5E1", grid_linestyle="--", grid_alpha=0.65)
    ax.set_xlim(0, 15.8)
    ax.set_ylim(-0.65, len(merged) - 0.25)
    ax.set_xlabel("博士學歷從業員工占比（% = 博士人數 ÷ 該子園區從業員工總人數）", fontsize=11.5, fontweight="bold", color="#1E293B", labelpad=8)
    ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7])
    ax.set_xticklabels(["0%", "1%", "2%", "3%", "4%", "5%", "6%", "7%"], fontsize=10.5, color="#334155")

    ax.set_yticks(y)
    y_labels = [r["label"] for r in merged]
    ax.set_yticklabels(y_labels, fontsize=10.6, fontweight="bold", color="#0F172A")
    for tick_idx, tick_label in enumerate(ax.get_yticklabels()):
        lbl_str = y_labels[tick_idx]
        if lbl_str in ("中科・中興園區", "竹科・新竹生醫園區"):
            tick_label.set_color("#0E5B6B")
            tick_label.set_fontsize(11.2)
        elif lbl_str in ("南科・臺南園區", "中科・台中園區"):
            tick_label.set_color("#97481B")
        elif lbl_str == "南科・屏東園區":
            tick_label.set_color("#64748B")

    # 全國科學園區總平均基準線 (6,956 / 348,689 = 1.99%) —— 標籤置於虛線最頂端畫布外，零遮擋！
    nat_avg = 6956.0 / 348689.0 * 100.0
    ax.axvline(nat_avg, color="#CA6F35", linestyle="--", linewidth=1.7, zorder=2)
    ax.text(
        nat_avg, len(merged) - 0.12,
        f"▼ 全國園區博士占比總平均：{nat_avg:.2f}%（6,956 / 348,689 人）",
        fontsize=9.4, fontweight="bold", color="#97481B", ha="center", va="bottom",
        bbox=dict(boxstyle="round,pad=0.28", facecolor="#FFF3EA", edgecolor="#CA6F35", linewidth=1.25),
        clip_on=False, zorder=7
    )

    for idx, row in enumerate(merged):
        lbl = row["label"]
        val = row["phd_pct"]
        phd_n = row["博士(人)"]
        tot_n = row["總人數"]
        role_txt = role_annotations.get(lbl, "")

        if math.isnan(val):
            ax.text(
                0.28, y[idx],
                f"NA（0 / 0 人）  {role_txt}",
                ha="left", va="center", fontsize=9.2, color="#64748B", fontweight="normal",
                bbox=dict(boxstyle="square,pad=0.06", facecolor="#FFFFFF", edgecolor="none"),
                zorder=5
            )
        else:
            is_top2 = val >= 6.0
            is_fab = lbl in ("南科・臺南園區", "中科・台中園區")
            val_str = f"{val:.2f}%（{phd_n:,} / {tot_n:,}人）"
            text_x = float(val) + 0.14

            # 對跨越 x=1.99% 基準虛線的文字加上純白微底襯，防止虛線穿字
            txt_bg = "#EBF7F9" if is_top2 else "#FFFFFF"
            ax.text(
                text_x, y[idx],
                f"{val_str}  {role_txt}",
                ha="left", va="center",
                fontsize=9.6 if (is_top2 or is_fab) else 9.15,
                fontweight="bold" if (is_top2 or is_fab) else "normal",
                color="#0E5B6B" if is_top2 else ("#97481B" if is_fab else "#1E293B"),
                bbox=dict(boxstyle="square,pad=0.06", facecolor=txt_bg, edgecolor="none"),
                zorder=5
            )

    # 右下角空白區（x=10.05 ~ 15.6, y=0.3 ~ 5.3，此處各列文字最右僅到 x=9.5）放置「雙腦分工」科普解讀卡
    ax.text(
        9.95, 2.55,
        "★ 科學園區「雙腦分工」科普解讀：\n"
        "1.【高純度研發大腦】（中興 6.99%、新竹生醫 6.85%）\n"
        "   • 博士密度達全國均值 (1.99%) 的 3.5 倍、臺南園區 7.7 倍！\n"
        "   • 聚焦新藥臨床、細胞治療與精準農業研發，產值雖在百億內，\n"
        "     卻是含金量最高、碩博士逾 44% 的創新實驗室引擎。\n"
        "2.【巨型先進量產基地】（臺南 0.90%、台中 0.72%）\n"
        "   • 兩大園區撐起全國 64.5% 產值（合計逾 3.74 兆元），\n"
        "     且台中 (115.4億) 與臺南 (113.0億) 亦包辦生技產值冠亞軍！",
        fontsize=9.25, color="#0F172A", ha="left", va="center", linespacing=1.35,
        bbox=dict(boxstyle="round,pad=0.48", facecolor="#FFFFFF", edgecolor="#2C8B9F", linewidth=1.5),
        zorder=6
    )

    fig.text(
        0.04, 0.848,
        "■ 色階編碼（Gephi · pastel 霧靄藍 5 階 CIELAB 循序插值）：極淺藍 #EBF7F9 (0.00% 最低) --> 基準青藍 #5DBACD --> 極深墨青 #0E5B6B (6.99% 最高) ｜ ■ 中性淺灰 #D9D9D9：分母為 0 之 NA 缺漏（屏東園區）",
        fontsize=9.15, fontweight="bold", color="#2C8B9F", ha="left", va="center"
    )

    fig.text(
        0.04, 0.94,
        "產值小卻是最高純度研發大腦！中興與新竹生醫園區博士密度近 7% 稱霸全國",
        fontsize=17.5, fontweight="bold", color="#0F172A", ha="left", va="top"
    )
    fig.text(
        0.04, 0.892,
        "三大科學園區轄下 17 個子園區「博士研發人才占比（%）」排行與產值結構交叉對照 —— 揭開「實驗室研發聚落 vs. 晶圓量產巨艦」的人才密度反差",
        fontsize=11.5, fontweight="normal", color="#475569", ha="left", va="top"
    )

    footnote_text = (
        "資料來源：國家科學及技術委員會《國家科學及技術委員會科學園區從業員工數統計》(政府資料開放平臺 dataset/7599)、《科學園區產業營業額統計表》(dataset/7597) 及《科學園區產業類別及家數統計》(dataset/7596)。\n"
        "時間戳記：從業員工數與廠商家數平臺更新日期為 2026-09-29（在職存量快照）；營業額涵蓋期間為 2025 年（民國 114 年）全年（平臺更新：2026-06-22）；本次檢視與分析日期：2026-11-07。\n"
        "統計樣本與前處理說明：依剔除合計／總計列後之純子園區明細重算（員工數與家數明細 N = 17 子園區，其中 16 處有在職人員［Min = 0.00% 橋頭、Max = 6.99% 中興、Median = 0.80%］，屏東園區總人數為 0 故博士占比為 NA 缺漏，\n"
        "依規範以 #D9D9D9 標記；嘉義與屏東園區為新設子園區，尚未列入 2025 年營業額統計表之 15 個子園區中）。注意：官方定義從業員工數含園區事業、育成中心與研究機構人員，不含營造廠或承攬商僱用人員。"
    )
    fig.text(
        0.04, 0.012, footnote_text,
        fontsize=8.7, color="#475569", ha="left", va="bottom", linespacing=1.32
    )

    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"[Chart 2 生成完畢] -> {out_path}")


if __name__ == "__main__":
    os.makedirs(SCRIPT_DIR, exist_ok=True)
    datasets = load_all_verified_datasets()
    chart1_path = os.path.join(SCRIPT_DIR, "01_chart_hook.png")
    chart2_path = os.path.join(SCRIPT_DIR, "02_chart_drilldown.png")
    draw_chart_01_hook(datasets, chart1_path)
    draw_chart_02_drilldown(datasets, chart2_path)
