import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as patches
import numpy as np
import os

# 1. 設置中文字體
font_path = "C:/Windows/Fonts/msjh.ttc"
if not os.path.exists(font_path):
    font_path = "C:/Windows/Fonts/NotoSansTC-VF.ttf"
prop = fm.FontProperties(fname=font_path)
prop_bold = fm.FontProperties(fname="C:/Windows/Fonts/msjhbd.ttc" if os.path.exists("C:/Windows/Fonts/msjhbd.ttc") else font_path, weight='bold')

# 2. 載入 115 年資料
data_file = "reading_sessions/20261031_全國預算比較儀表板/data/budget_data.json"
with open(data_file, "r", encoding="utf-8") as f:
    d = json.load(f)

key = "115_exp"
records = d["records"][key]
population = d["population"]

# 排除中央，取 21 縣市
counties = [c for c in d["counties"] if c != "中央"]

# 計算 Top 4 政事別
cat_totals = {}
for c in counties:
    for cat, val in records.get(c, {}).items():
        cat_totals[cat] = cat_totals.get(cat, 0) + val["budget"]

sorted_cats = sorted(cat_totals.keys(), key=lambda k: cat_totals[k], reverse=True)
top4_cats = sorted_cats[:4]
other_cats = sorted_cats[4:]

# 準備每個縣市的數據
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
        "total": tot / 1e8, # 億元
        "diff": diff / 1e8, # 億元
        "diff_rate": diff_rate,
        "per_capita": per_capita, # 元/人
        "top4": [v / 1e8 for v in top4_vals],
        "other": other_val / 1e8
    })

# 依總預算降序排序
county_stats.sort(key=lambda x: x["total"], reverse=True)

# 色彩配置 (個人規範)
COLORS = {
    "c1": "#ECA072", # 暖杏蜜橘
    "c2": "#5DBACD", # 霧靄青藍
    "c3": "#E89BB6", # 落櫻粉黛
    "c4": "#8FBA88", # 鼠尾草綠
    "other": "#CBD5E1", # 典雅灰
    "bg": "#F8FAFC",
    "card": "#FFFFFF",
    "border": "#E2E8F0",
    "text_dark": "#0F172A",
    "text_muted": "#475569"
}

# 建立畫布 (高解析度寬螢幕 16:9, 2400 x 1350 px)
fig = plt.figure(figsize=(24, 13.5), dpi=100)
fig.patch.set_facecolor(COLORS["bg"])

# 使用 GridSpec 規劃三欄佈局
# [ Header ]
# [ Left: 4+1 堆疊結構圖 (佔 60% 寬度) ] | [ Right: 人均榜 + 增減發散 (佔 40% 寬度) ]
# [ Footer: 說明與右下角網址 ]
gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 0.75], height_ratios=[1, 1],
                       left=0.04, right=0.96, top=0.88, bottom=0.06,
                       wspace=0.14, hspace=0.22)

ax_main = fig.add_subplot(gs[:, 0]) # 左側大圖 (跨兩行)
ax_percap = fig.add_subplot(gs[0, 1]) # 右上：人均榜
ax_diff = fig.add_subplot(gs[1, 1]) # 右下：年增減

# ==========================================
# 頂部 Header & KPI 卡片
# ==========================================
grand_total = sum(x["total"] for x in county_stats)
grand_diff = sum(x["diff"] for x in county_stats)
grand_rate = (grand_diff / (grand_total - grand_diff)) * 100
med_percap = np.median([x["per_capita"] for x in county_stats])
top_cat_sum = sum(x["top4"][0] for x in county_stats)
top_cat_ratio = (top_cat_sum / grand_total) * 100

# 標題文字
fig.text(0.04, 0.955, "民國 115 年全台 21 縣市地方政府預算結構與人均支出比較",
         fontproperties=prop_bold, fontsize=24, color=COLORS["text_dark"], va="top")
fig.text(0.04, 0.915, "依據行政院主計總處暨 OpenFun 預算平臺公開資料 · CIELAB 4 色認知優化規範 (4+1 核心支柱視角)",
         fontproperties=prop, fontsize=13, color=COLORS["text_muted"], va="top")

# KPI 指標徽章 (右上方)
kpis = [
    ("全台地方總預算", f"{grand_total:,.0f} 億元", f"年變動 +{grand_diff:.0f} 億 (+{grand_rate:.1f}%)", "#ECA072"),
    ("每人人均預算中位數", f"{med_percap:,.0f} 元/人", "本島最高：臺北市 8.8 萬", "#5DBACD"),
    (f"第一大支柱：{top4_cats[0]}", f"{top_cat_sum:,.0f} 億元", f"佔全體歲出 {top_cat_ratio:.1f}%", "#E89BB6")
]

kpi_start_x = 0.52
kpi_w = 0.14
for i, (k_title, k_val, k_sub, k_col) in enumerate(kpis):
    kx = kpi_start_x + i * (kpi_w + 0.015)
    # 繪製小卡背景
    rect = patches.FancyBboxPatch((kx, 0.905), kpi_w, 0.075,
                                  boxstyle="round,pad=0.008,rounding_size=0.012",
                                  facecolor=COLORS["card"], edgecolor=COLORS["border"],
                                  transform=fig.transFigure, clip_on=False, zorder=5)
    fig.patches.append(rect)
    # 左側顏色飾條
    bar = patches.FancyBboxPatch((kx, 0.905), 0.004, 0.075,
                                 boxstyle="round,pad=0,rounding_size=0.002",
                                 facecolor=k_col, edgecolor="none",
                                 transform=fig.transFigure, clip_on=False, zorder=6)
    fig.patches.append(bar)
    fig.text(kx + 0.01, 0.970, k_title, fontproperties=prop, fontsize=10, color=COLORS["text_muted"], va="top")
    fig.text(kx + 0.01, 0.948, k_val, fontproperties=prop_bold, fontsize=14, color=COLORS["text_dark"], va="top")
    fig.text(kx + 0.01, 0.922, k_sub, fontproperties=prop, fontsize=9.5, color=k_col, va="top", weight='bold')

# ==========================================
# 左側主圖：4+1 結構堆疊圖 (橫向長條)
# ==========================================
ax_main.set_facecolor(COLORS["card"])
ax_main.grid(axis='x', color='#F1F5F9', linestyle='-', zorder=0)
for spine in ax_main.spines.values():
    spine.set_color(COLORS["border"])

y_pos = np.arange(len(county_stats))
county_names = [x["county"] for x in county_stats]

# 堆疊繪製
left_accum = np.zeros(len(county_stats))
bar_height = 0.65
labels = [top4_cats[0], top4_cats[1], top4_cats[2], top4_cats[3], "其他項目合計"]
cols = [COLORS["c1"], COLORS["c2"], COLORS["c3"], COLORS["c4"], COLORS["other"]]

for cat_idx in range(4):
    vals = np.array([x["top4"][cat_idx] for x in county_stats])
    ax_main.barh(y_pos, vals, left=left_accum, height=bar_height, color=cols[cat_idx],
                 label=labels[cat_idx], edgecolor='white', linewidth=0.5, zorder=3)
    left_accum += vals

# 其他項目
other_vals = np.array([x["other"] for x in county_stats])
ax_main.barh(y_pos, other_vals, left=left_accum, height=bar_height, color=cols[4],
             label=labels[4], edgecolor='white', linewidth=0.5, zorder=3)
left_accum += other_vals

# 數值標註在長條右側
for i, tot in enumerate(left_accum):
    ax_main.text(tot + 15, i, f"{tot:,.1f} 億", fontproperties=prop, fontsize=10,
                 color=COLORS["text_dark"], va='center', zorder=4)

ax_main.set_yticks(y_pos)
ax_main.set_yticklabels(county_names, fontproperties=prop_bold, fontsize=12, color=COLORS["text_dark"])
ax_main.invert_yaxis() # 第一名在最上方
ax_main.set_xlabel("預算總額（新臺幣億元）", fontproperties=prop, fontsize=11, color=COLORS["text_muted"])
ax_main.set_title("【核心視角】各縣市預算結構堆疊比較（前四大支柱 ＋ 其他項目）", fontproperties=prop_bold,
                  fontsize=14, color=COLORS["text_dark"], pad=14, loc='left')

# 圖例 (放置在圖表下方)
leg = ax_main.legend(loc='lower center', bbox_to_anchor=(0.5, -0.075), ncol=5, frameon=False,
                     prop=prop, fontsize=11)

# ==========================================
# 右上圖：每人人均預算排行 (循序色階)
# ==========================================
ax_percap.set_facecolor(COLORS["card"])
ax_percap.grid(axis='x', color='#F1F5F9', linestyle='-', zorder=0)
for spine in ax_percap.spines.values():
    spine.set_color(COLORS["border"])

# 人均排序 (前 10 名)
percap_sorted = sorted(county_stats, key=lambda x: x["per_capita"], reverse=True)[:10]
y_p = np.arange(len(percap_sorted))
p_names = [x["county"] for x in percap_sorted]
p_vals = [x["per_capita"] for x in percap_sorted]
max_p = max(p_vals)

# 循序顏色映射 (暖橘漸層)
seq_palette = ["#FFF3EA", "#FBD8C0", "#ECA072", "#CA6F35", "#97481B"]
p_colors = []
for v in p_vals:
    ratio = v / max_p
    if ratio < 0.25: c = seq_palette[1]
    elif ratio < 0.5: c = seq_palette[2]
    elif ratio < 0.75: c = seq_palette[3]
    else: c = seq_palette[4]
    p_colors.append(c)

ax_percap.barh(y_p, p_vals, height=0.6, color=p_colors, edgecolor='white', linewidth=0.5, zorder=3)
for i, v in enumerate(p_vals):
    ax_percap.text(v + 3000, i, f"{v:,.0f} 元", fontproperties=prop, fontsize=9.5,
                   color=COLORS["text_dark"], va='center', zorder=4)

ax_percap.set_yticks(y_p)
ax_percap.set_yticklabels(p_names, fontproperties=prop, fontsize=11, color=COLORS["text_dark"])
ax_percap.invert_yaxis()
ax_percap.set_xlabel("人均預算（新臺幣元 / 人）", fontproperties=prop, fontsize=10, color=COLORS["text_muted"])
ax_percap.set_title("【人均視角】各縣市每人人均預算排行（前 10 高 · 循序色階）", fontproperties=prop_bold,
                    fontsize=12, color=COLORS["text_dark"], pad=10, loc='left')

# ==========================================
# 右下圖：年增減差異分析 (9 階發散色階)
# ==========================================
ax_diff.set_facecolor(COLORS["card"])
ax_diff.grid(axis='x', color='#F1F5F9', linestyle='-', zorder=0)
ax_diff.axvline(0, color='#94A3B8', linewidth=1, linestyle='--', zorder=2)
for spine in ax_diff.spines.values():
    spine.set_color(COLORS["border"])

# 取前 10 大變動縣市 (依增減額絕對值排序)
diff_sorted = sorted(county_stats, key=lambda x: abs(x["diff"]), reverse=True)[:10]
y_d = np.arange(len(diff_sorted))
d_names = [x["county"] for x in diff_sorted]
d_vals = [x["diff"] for x in diff_sorted]

# 發散顏色 (正向橘、負向青)
d_colors = ["#ECA072" if v >= 0 else "#257F92" for v in d_vals]

ax_diff.barh(y_d, d_vals, height=0.6, color=d_colors, edgecolor='white', linewidth=0.5, zorder=3)
for i, v in enumerate(d_vals):
    sign = "+" if v >= 0 else ""
    x_pos = v + 3 if v >= 0 else v - 18
    ax_diff.text(x_pos, i, f"{sign}{v:.1f} 億", fontproperties=prop, fontsize=9.5,
                 color=COLORS["text_dark"], va='center', zorder=4)

ax_diff.set_yticks(y_d)
ax_diff.set_yticklabels(d_names, fontproperties=prop, fontsize=11, color=COLORS["text_dark"])
ax_diff.invert_yaxis()
ax_diff.set_xlabel("與去年預算增減額（新臺幣億元）", fontproperties=prop, fontsize=10, color=COLORS["text_muted"])
ax_diff.set_title("【趨勢視角】預算年度增減額差異比較（發散色階：青負 至 橘正）", fontproperties=prop_bold,
                  fontsize=12, color=COLORS["text_dark"], pad=10, loc='left')

# ==========================================
# 底部 Footer 與右上角 / 右下角網址偷偷塞入
# ==========================================
fig.text(0.04, 0.02, "製圖依據：個人圖表配色規範檔 (CIELAB 4色認知優化版) 與 行政院主計總處資料、OpenFun 預算平臺 (tw.openfun~api~tw.budget)",
         fontproperties=prop, fontsize=9.5, color="#94A3B8", va="bottom")

# 偷偷在右下角落塞入網站連結（精緻低調、優雅高解析度）
website_url = "https://markyang20040112-source.github.io/20261031_-/"
fig.text(0.96, 0.02, f"線上即時互動儀表板：{website_url}",
         fontproperties=prop_bold, fontsize=10.5, color="#64748B", ha="right", va="bottom")

# 存檔
out_png = "reading_sessions/20261031_全國預算比較儀表板/全台預算比較儀表板_視覺化圖表.png"
plt.savefig(out_png, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"Chart successfully saved to {out_png}")
