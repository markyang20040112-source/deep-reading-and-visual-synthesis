import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

# 1. 設置字體
font_path = "C:/Windows/Fonts/msjh.ttc"
if not os.path.exists(font_path):
    font_path = "C:/Windows/Fonts/NotoSansTC-VF.ttf"
prop = fm.FontProperties(fname=font_path)
prop_bold = fm.FontProperties(fname="C:/Windows/Fonts/msjhbd.ttc" if os.path.exists("C:/Windows/Fonts/msjhbd.ttc") else font_path, weight='bold')

# 2. 載入資料
data_file = "reading_sessions/20261031_全國預算比較儀表板/data/budget_data.json"
with open(data_file, "r", encoding="utf-8") as f:
    d = json.load(f)

key = "115_exp"
records = d["records"][key]
population = d["population"]
counties = [c for c in d["counties"] if c != "中央"]

# 計算 Top 4 政事別
cat_totals = {}
for c in counties:
    for cat, val in records.get(c, {}).items():
        cat_totals[cat] = cat_totals.get(cat, 0) + val["budget"]

sorted_cats = sorted(cat_totals.keys(), key=lambda k: cat_totals[k], reverse=True)
top4_cats = sorted_cats[:4]
other_cats = sorted_cats[4:]

# 整理縣市資料
county_stats = []
for c in counties:
    rec = records.get(c, {})
    pop = population.get(c, 1)
    tot = sum(v["budget"] for v in rec.values())
    diff = sum(v["diff"] for v in rec.values())
    per_capita = tot / pop
    diff_rate = (diff / (tot - diff)) * 100 if (tot - diff) > 0 else 0
    
    top4_vals = [rec.get(cat, {}).get("budget", 0) for cat in top4_cats]
    other_val = tot - sum(top4_vals)
    
    county_stats.append({
        "county": c,
        "total": tot / 1e8,
        "diff": diff / 1e8,
        "diff_rate": diff_rate,
        "per_capita": per_capita,
        "top4": [v / 1e8 for v in top4_vals],
        "other": other_val / 1e8
    })

county_stats.sort(key=lambda x: x["total"], reverse=True)

grand_total = sum(x["total"] for x in county_stats)
grand_diff = sum(x["diff"] for x in county_stats)
grand_rate = (grand_diff / (grand_total - grand_diff)) * 100
med_percap = np.median([x["per_capita"] for x in county_stats])
top_cat_sum = sum(x["top4"][0] for x in county_stats)
top_cat_ratio = (top_cat_sum / grand_total) * 100

# 色彩配置
COLORS = {
    "c1": "#ECA072",     # 暖杏蜜橘
    "c2": "#5DBACD",     # 霧靄青藍
    "c3": "#E89BB6",     # 落櫻粉黛
    "c4": "#8FBA88",     # 鼠尾草綠
    "other": "#CBD5E1",  # 典雅灰
    "bg": "#F8FAFC",
    "card": "#FFFFFF",
    "border": "#CBD5E1",
    "text_dark": "#0F172A",
    "text_muted": "#475569"
}

# 建立畫布：24 x 14 英寸 (高解析度)
fig = plt.figure(figsize=(24, 14), dpi=120)
fig.patch.set_facecolor(COLORS["bg"])

# 佈局規劃：
# row 0: Header 資訊與 3 個 KPI 卡片 (高度比例 0.12)
# row 1 & 2: 主要視覺化區域 (左 4+1 堆疊，右上 人均榜，右下 年增減)
# hspace 設為 0.28，垂直間隔充裕乾淨
gs = fig.add_gridspec(3, 2, width_ratios=[1.25, 0.75], height_ratios=[0.12, 0.44, 0.44],
                       left=0.045, right=0.955, top=0.96, bottom=0.065,
                       wspace=0.15, hspace=0.28)

# 頂部 Header & KPI 卡片區域 (使用 GridSpec 內嵌 subplots，絕不位移或浮動)
gs_top = gs[0, :].subgridspec(1, 4, width_ratios=[1.3, 0.9, 0.9, 0.9], wspace=0.08)

# 1. 主標題區 (ax_title) - 乾淨雙行排版，底部預留充裕空白
ax_title = fig.add_subplot(gs_top[0, 0])
ax_title.set_facecolor(COLORS["bg"])
ax_title.axis('off')
ax_title.text(0.0, 0.85, "民國 115 年全台 21 縣市預算結構與人均支出比較",
              fontproperties=prop_bold, fontsize=20.5, color=COLORS["text_dark"], va="top")
ax_title.text(0.0, 0.35, "資料來源：行政院主計總處 與 OpenFun 預算平臺 · CIELAB 4色認知優化版",
              fontproperties=prop, fontsize=11.5, color=COLORS["text_muted"], va="top")

# 2. KPI 卡片 1: 地方總預算規模
ax_kpi1 = fig.add_subplot(gs_top[0, 1])
ax_kpi1.set_facecolor(COLORS["card"])
for spine in ax_kpi1.spines.values():
    spine.set_color(COLORS["border"])
    spine.set_linewidth(1.2)
ax_kpi1.set_xticks([])
ax_kpi1.set_yticks([])
ax_kpi1.text(0.08, 0.78, "全台地方總預算規模", fontproperties=prop, fontsize=10.5, color=COLORS["text_muted"], va="top")
ax_kpi1.text(0.08, 0.48, f"{grand_total:,.0f} 億元", fontproperties=prop_bold, fontsize=16, color=COLORS["text_dark"], va="top")
ax_kpi1.text(0.08, 0.18, f"年變動：+{grand_diff:.0f} 億 (+{grand_rate:.1f}%)", fontproperties=prop_bold, fontsize=10, color="#C2410C", va="top")

# 3. KPI 卡片 2: 人均中位數
ax_kpi2 = fig.add_subplot(gs_top[0, 2])
ax_kpi2.set_facecolor(COLORS["card"])
for spine in ax_kpi2.spines.values():
    spine.set_color(COLORS["border"])
    spine.set_linewidth(1.2)
ax_kpi2.set_xticks([])
ax_kpi2.set_yticks([])
ax_kpi2.text(0.08, 0.78, "每人人均預算中位數", fontproperties=prop, fontsize=10.5, color=COLORS["text_muted"], va="top")
ax_kpi2.text(0.08, 0.48, f"{med_percap:,.0f} 元/人", fontproperties=prop_bold, fontsize=16, color=COLORS["text_dark"], va="top")
ax_kpi2.text(0.08, 0.18, "本島最高：臺北市 8.8 萬", fontproperties=prop_bold, fontsize=10, color="#0E7490", va="top")

# 4. KPI 卡片 3: 第一大支柱
ax_kpi3 = fig.add_subplot(gs_top[0, 3])
ax_kpi3.set_facecolor(COLORS["card"])
for spine in ax_kpi3.spines.values():
    spine.set_color(COLORS["border"])
    spine.set_linewidth(1.2)
ax_kpi3.set_xticks([])
ax_kpi3.set_yticks([])
ax_kpi3.text(0.08, 0.78, f"第一大支柱：{top4_cats[0]}", fontproperties=prop, fontsize=10.5, color=COLORS["text_muted"], va="top")
ax_kpi3.text(0.08, 0.48, f"{top_cat_sum:,.0f} 億元", fontproperties=prop_bold, fontsize=16, color=COLORS["text_dark"], va="top")
ax_kpi3.text(0.08, 0.18, f"佔全體歲出比重 {top_cat_ratio:.1f}%", fontproperties=prop_bold, fontsize=10, color="#BE185D", va="top")


# ==========================================
# 左側主圖：4+1 結構堆疊圖 (跨 row 1 & row 2)
# ==========================================
ax_main = fig.add_subplot(gs[1:, 0])
ax_main.set_facecolor(COLORS["card"])
ax_main.grid(axis='x', color='#F1F5F9', linestyle='-', zorder=0)
for spine in ax_main.spines.values():
    spine.set_color(COLORS["border"])

y_pos = np.arange(len(county_stats))
county_names = [x["county"] for x in county_stats]

left_accum = np.zeros(len(county_stats))
bar_height = 0.62
labels = [top4_cats[0], top4_cats[1], top4_cats[2], top4_cats[3], "其他合計"]
cols = [COLORS["c1"], COLORS["c2"], COLORS["c3"], COLORS["c4"], COLORS["other"]]

for cat_idx in range(4):
    vals = np.array([x["top4"][cat_idx] for x in county_stats])
    ax_main.barh(y_pos, vals, left=left_accum, height=bar_height, color=cols[cat_idx],
                 label=labels[cat_idx], edgecolor='white', linewidth=0.6, zorder=3)
    left_accum += vals

other_vals = np.array([x["other"] for x in county_stats])
ax_main.barh(y_pos, other_vals, left=left_accum, height=bar_height, color=cols[4],
             label=labels[4], edgecolor='white', linewidth=0.6, zorder=3)
left_accum += other_vals

# 數值標註 (設有充足邊界，絕不碰撞)
max_total = max(left_accum)
for i, tot in enumerate(left_accum):
    ax_main.text(tot + (max_total * 0.012), i, f"{tot:,.1f} 億", fontproperties=prop, fontsize=10,
                 color=COLORS["text_dark"], va='center', zorder=4)

ax_main.set_xlim(0, max_total * 1.15)
ax_main.set_yticks(y_pos)
ax_main.set_yticklabels(county_names, fontproperties=prop_bold, fontsize=11.5, color=COLORS["text_dark"])
ax_main.invert_yaxis()
ax_main.set_xlabel("預算總額（新臺幣億元）", fontproperties=prop, fontsize=11, color=COLORS["text_muted"], labelpad=8)

# 標題與圖例並列於同一個頂部水平線：左側為標題，右側為圖例，垂直對齊完美！
ax_main.set_title("【核心結構視角】各縣市預算堆疊比較（前四大核心支柱 ＋ 其他項目合計）",
                  fontproperties=prop_bold, fontsize=12.5, color=COLORS["text_dark"], pad=14, loc='left')

ax_main.legend(loc='lower right', bbox_to_anchor=(1.0, 1.015), ncol=5, frameon=False,
               prop=prop, fontsize=10.5, handlelength=1.2, handletextpad=0.4, columnspacing=1.1)


# ==========================================
# 右上圖：人均預算排行 (前 10 高)
# ==========================================
ax_percap = fig.add_subplot(gs[1, 1])
ax_percap.set_facecolor(COLORS["card"])
ax_percap.grid(axis='x', color='#F1F5F9', linestyle='-', zorder=0)
for spine in ax_percap.spines.values():
    spine.set_color(COLORS["border"])

percap_sorted = sorted(county_stats, key=lambda x: x["per_capita"], reverse=True)[:10]
y_p = np.arange(len(percap_sorted))
p_names = [x["county"] for x in percap_sorted]
p_vals = [x["per_capita"] for x in percap_sorted]
max_p = max(p_vals)

seq_palette = ["#FFF3EA", "#FBD8C0", "#ECA072", "#CA6F35", "#97481B"]
p_colors = []
for v in p_vals:
    ratio = v / max_p
    if ratio < 0.25: c = seq_palette[1]
    elif ratio < 0.5: c = seq_palette[2]
    elif ratio < 0.75: c = seq_palette[3]
    else: c = seq_palette[4]
    p_colors.append(c)

ax_percap.barh(y_p, p_vals, height=0.58, color=p_colors, edgecolor='white', linewidth=0.6, zorder=3)
for i, v in enumerate(p_vals):
    ax_percap.text(v + (max_p * 0.02), i, f"{v:,.0f} 元", fontproperties=prop, fontsize=9.5,
                   color=COLORS["text_dark"], va='center', zorder=4)

ax_percap.set_xlim(0, max_p * 1.22)
ax_percap.set_yticks(y_p)
ax_percap.set_yticklabels(p_names, fontproperties=prop, fontsize=10.5, color=COLORS["text_dark"])
ax_percap.invert_yaxis()
ax_percap.set_xlabel("每人人均預算（新臺幣元 / 人）", fontproperties=prop, fontsize=10, color=COLORS["text_muted"], labelpad=6)
ax_percap.set_title("【人均視角】各縣市每人人均預算（前 10 高 · 循序色階）",
                    fontproperties=prop_bold, fontsize=12, color=COLORS["text_dark"], pad=14, loc='left')


# ==========================================
# 右下圖：年增減差異分析 (9 階發散色階)
# ==========================================
ax_diff = fig.add_subplot(gs[2, 1])
ax_diff.set_facecolor(COLORS["card"])
ax_diff.grid(axis='x', color='#F1F5F9', linestyle='-', zorder=0)
ax_diff.axvline(0, color='#94A3B8', linewidth=1, linestyle='--', zorder=2)
for spine in ax_diff.spines.values():
    spine.set_color(COLORS["border"])

diff_sorted = sorted(county_stats, key=lambda x: abs(x["diff"]), reverse=True)[:10]
y_d = np.arange(len(diff_sorted))
d_names = [x["county"] for x in diff_sorted]
d_vals = [x["diff"] for x in diff_sorted]
max_abs_diff = max(abs(min(d_vals)), abs(max(d_vals)), 1)

d_colors = ["#ECA072" if v >= 0 else "#257F92" for v in d_vals]

ax_diff.barh(y_d, d_vals, height=0.58, color=d_colors, edgecolor='white', linewidth=0.6, zorder=3)

# 標籤精準自適應定位 (正向靠右、負向靠左，絕對不壓字)
offset = max_abs_diff * 0.03
for i, v in enumerate(d_vals):
    sign = "+" if v >= 0 else ""
    if v >= 0:
        ax_diff.text(v + offset, i, f"{sign}{v:.1f} 億", fontproperties=prop, fontsize=9.5,
                     color=COLORS["text_dark"], va='center', ha='left', zorder=4)
    else:
        ax_diff.text(v - offset, i, f"{v:.1f} 億", fontproperties=prop, fontsize=9.5,
                     color=COLORS["text_dark"], va='center', ha='right', zorder=4)

ax_diff.set_xlim(-max_abs_diff * 1.35, max_abs_diff * 1.35)
ax_diff.set_yticks(y_d)
ax_diff.set_yticklabels(d_names, fontproperties=prop, fontsize=10.5, color=COLORS["text_dark"])
ax_diff.invert_yaxis()
ax_diff.set_xlabel("與去年預算增減額（新臺幣億元）", fontproperties=prop, fontsize=10, color=COLORS["text_muted"], labelpad=6)
ax_diff.set_title("【趨勢視角】預算年度增減額差異比較（青負 至 橘正）",
                  fontproperties=prop_bold, fontsize=12, color=COLORS["text_dark"], pad=10, loc='left')


# ==========================================
# 底部 Footer 與右下角優雅網址
# ==========================================
fig.text(0.045, 0.02, "製圖依據：個人圖表配色規範檔 (CIELAB 4色認知優化版) · 行政院主計總處資料 · OpenFun 預算平臺 (tw.openfun~api~tw.budget)",
         fontproperties=prop, fontsize=9.5, color="#94A3B8", va="bottom")

website_url = "https://markyang20040112-source.github.io/20261031_-/"
fig.text(0.955, 0.02, f"線上即時互動儀表板：{website_url}",
         fontproperties=prop_bold, fontsize=10.5, color="#475569", ha="right", va="bottom")

# 輸出圖檔
out_png = "reading_sessions/20261031_全國預算比較儀表板/全台預算比較儀表板_視覺化圖表.png"
plt.savefig(out_png, dpi=200, facecolor=fig.get_facecolor())
print(f"Refined chart successfully saved to {out_png}")
