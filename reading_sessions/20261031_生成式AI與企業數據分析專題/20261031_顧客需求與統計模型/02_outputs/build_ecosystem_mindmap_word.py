# -*- coding: utf-8 -*-
"""
build_ecosystem_mindmap_word.py
重製《『顧客-企業-投資者』關係-心智圖(延伸)》為「Word 直式 A4 友善版」。

- 畫布寬 6.27 吋（= Word A4 預設內文寬度），以實際印刷字級設計：
  主標題 13.5pt、卡片標題 9.8pt、內文 8.4pt、註腳 7pt（舊版縮入 Word 後內文約只剩 2～3pt）。
- 版面由「左右三欄橫式」改為「上方價值迴路 + 下方 2 欄 × 3 列卡片」的直式結構，
  保留原圖完整架構：中央三角色迴路 + 六大知識卡 + 底部總結。
- 文字以「白話先行、保留案例與數字」為原則精簡；細節完整收錄於 PDF 報告。
輸出：02_outputs/04_顧客-企業-投資者關係心智圖_Word直式版.png（原 jpg 保留不動）
"""
import os
from word_layout_engine import (Paragraph, rounded_box, new_canvas, text_width_in, fp,
                                WORD_TEXT_WIDTH_IN, DPI)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "04_顧客-企業-投資者關係心智圖_Word直式版.png")

W = WORD_TEXT_WIDTH_IN
M = 0.10                     # 外邊界
BODY = 8.4
HEAD = 9.8
INK = "#1E293B"
MUTED = "#475569"

# ---------------------------------------------------------------- 內容
TITLE = "企業、客戶與投資人的價值循環：用統計模型找出顧客真正在乎的事"
SUBTITLE = "「企業與客戶」是創造價值的造血引擎，「投資人」是幫忙加速的助燃劑；本末倒置，企業就會失靈"

INVESTOR = {
    "title": "外部輔助迴路：投資人／資本市場（角色：助燃劑）",
    "bullets": [
        "**想要什麼**：企業產值提高 → 自己的投資獲利提高 → 就願意再加碼投資。",
        "**該扮演的角色**：提供擴張所需的資金，事後分享「企業與客戶」共同創造的成果。",
        "**危險訊號**：當投資人給的錢比客戶付的錢還多（如泡沫期），助燃劑就會反過來綁架企業方向。",
    ],
}
COMPANY = {
    "title": "核心樞紐：企業（Company）",
    "bullets": [
        "**想要什麼**：產值提高；資源同時來自客戶營收與投資人資金。",
        "**關鍵抉擇**：迎合投資人的短期估值？還是用科學方法看清客戶的真實需求？",
        "**封面隱喻**：《玩具的故事》—— 找出並聚焦客戶「真正珍視的東西」才能創造價值。",
    ],
}
CUSTOMER = {
    "title": "價值源頭：客戶（Customer）",
    "bullets": [
        "**想要什麼**：花的錢換到更大的效益，就願意持續買單、帶給企業價值。",
        "**跨產業最被看重的兩件事**：主動清楚的進度溝通；出問題時馬上有人處理。",
        "**鐵律**：價值只在「企業與客戶」之間誕生，客戶買單才是撐起估值的唯一地基。",
    ],
}

CARDS = [
    {   # row 1
        "no": "1", "title": "結構性失靈：當「助燃劑」反客為主（討好投資人 > 服務客戶）", "theme": "red",
        "bullets": [
            "**誘因錯位**：高層為了迎合股東對短期估值的期待，把心力放在取悅投資人而非服務客戶，形成「尾巴搖狗」。",
            "**迪士尼**：為了周邊商品營收，讓電影淪為「賣玩具的大型廣告」，犧牲故事與觀眾體驗。",
            "**波音**：從重視工程與飛安，轉向股東價值至上，大砍研發與品管成本，終致 737 MAX 危機與商譽重創。",
            "**串流與 AI 泡沫**：只衝投資人愛看的短期數字（如灌訂閱數），忽略客戶是否真的留下。",
        ],
    },
    {
        "no": "2", "title": "主管常犯的「兩大錯誤」與背後的「兩大心理盲點」", "theme": "red",
        "bullets": [
            "**錯誤① 選錯重點**：72% 的上市 B2B 公司，主管的看法和客戶實際在意的事幾乎無關、甚至相反（教育公司以為 8 項都一樣重要，其實「24 小時內解決問題」提升潛力就高達 85%）。",
            "**錯誤② 一直換重點**：74.6% 的公司改過優先順序、85.5% 每兩年就大改一次（必帝一年內把品質從第 1 降到第 8），但客戶需求其實很穩定。",
            "**盲點① 只看顯眼的事**：被單一客訴或對手動作牽著走（漢堡王總裁親接 2 萬通電話；80% 的策略會議都在談對手）；SWOT、4P 只能整理，不能排序。",
            "**盲點② 沒驗證就相信**：軟體公司砸 1,000 萬美元提升員工投入度卻沒帶動銷售（不到 12% 員工會接觸客戶）；真正關鍵是訂價帳單（43%）與產品升級（26%）。",
        ],
    },
    {   # row 2
        "no": "3", "title": "科學解方：道斯線性模型——人會判斷，但模型排得更準", "theme": "blue",
        "bullets": [
            "**道斯（Robyn Dawes）的發現**：專家不是不知道該看哪些因素，而是排不準「哪個影響最大、大多少」；統計模型的排序始終比專家直覺準。",
            "**第一層模型**：請客戶替 8 項因素打分，算出每一項能把整體價值拉高多少（提升潛力）。",
            "**第二層模型**：再接上會計帳上的真實營收與利潤率，檢查是否真的帶來財務貢獻。",
            "**財務證據**：主管與客戶看法的一致度每提高 12.5 分（量表 -100～+100），營收 +9.2%、毛利率 +5.2%、自由現金流 +8.8%、市值 +11.1%。",
        ],
    },
    {
        "no": "4", "title": "落地處方：少做多得「五步驟」", "theme": "blue",
        "bullets": [
            "**① 揭露落差**：ITI 員工用 65 種說法描述公司策略、只有 24% 時間面對客戶；S-SET 營收 5,000 萬美元卻同時跑 42 項計畫。",
            "**② 只挑提升潛力最高的 1～2 項**：ITI 選「每週進度溝通」與「持續支援」（品質、低價只是基本門檻）；S-SET 選「快速報價」。",
            "**③ 融入每天的工作**：ITI 每週主動寄進度報告（一年不到 30 次 → 3,524 次）；S-SET 報價從 18 小時縮到 5 小時內。",
            "**④ 砍掉沒價值的活動**：有數據撐腰，砍計畫就不再是「別砍我的」政治角力；ITI 釋放三成以上工時，股價漲 162%。",
            "**⑤ 做到了再對外宣傳**：太早宣傳會打擊士氣；ITI 做到後才主打「透明、可預測」，訂價能力提高 20～30%。",
        ],
    },
    {   # row 3
        "no": "5", "title": "數據分析的演進與 AI 助力（結合〈AI 能強化你的數據分析能力〉）", "theme": "teal",
        "bullets": [
            "**分析四層次**：發生了什麼（描述）→ 為什麼發生（診斷）→ 接下來會怎樣（預測）→ 該怎麼做（指示）。",
            "**接上背景資訊**：把跨部門的情境資料嵌進 ERP、CRM 等日常系統，如人資系統自動配對履歷、供應鏈提前預測瓶頸；AXA XL 只花 8 週就導入全公司人資指標系統。",
            "**AI 擴增分析**：用口語提問、自動產生摘要，讓非專家也能做分析（如製造商查出業務未經授權的特別折扣，挽回數十萬美元營收）。",
        ],
    },
    {
        "no": "6", "title": "延伸思考：商業模式差異與防範模型偏見的四道關卡", "theme": "teal",
        "bullets": [
            "**B2B vs. B2C**：B2B 客戶把「AI 能力」「專案執行力」當採購硬指標；B2C 客戶買的是體驗，AI 一樣重要但藏在幕後（推薦、派單、防詐）。",
            "**模型也會夾帶偏見**（《大數據的傲慢與偏見》），所以要過四關：",
            "**① 先聽再出題**：先訪談流失客戶、整理真實客訴，不由主管憑直覺決定問卷題目。",
            "**② 推算而非直問**：用迴歸算出各因素對總分的影響，避免客戶把每項都勾「重要」。",
            "**③ 對帳** 接上真實營收與毛利；**④ 做實驗** 用 A/B 測試確認因果。",
        ],
    },
]

FOOTER = ("**總結**　真正的商業價值誕生於「企業與客戶」的雙向迴路，投資人的資金只是助燃劑。"
          "企業要抗拒短期估值的誘惑，用統計模型與 AI 找出客戶真正看重的少數因素，把它融入日常工作、砍掉無效計畫，"
          "並持續用實驗驗證，才能讓「客戶買單 → 企業產值提升 → 投資人共享長期回報」健康運轉。")
SOURCE = ("整理自：Mittal, Piazza, Singh & Malshe〈Do You Know What Your Customers Value?〉；"
          "Davenport & Fitts〈AI Can Help Companies Tap New Sources of Data for Analytics〉")

THEMES = {
    "red":  {"edge": "#C2410C", "fill": "#FFF7F2", "head": "#9A3412"},
    "blue": {"edge": "#2563EB", "fill": "#F5F8FF", "head": "#1E40AF"},
    "teal": {"edge": "#0F766E", "fill": "#F2FAF8", "head": "#115E59"},
}

# ---------------------------------------------------------------- 量測
PAD = 0.085            # 卡片內距
GAP = 0.10             # 卡片間距
COL_W = (W - 2 * M - GAP) / 2


def card_blocks(title, bullets, width, head_color, body_color=INK, bold_color=None, title_size=HEAD):
    inner = width - 2 * PAD
    blocks = [Paragraph(title, title_size, inner, color=head_color, leading=1.30)]
    for i, b in enumerate(bullets):
        blocks.append(Paragraph(b, BODY, inner, bullet="●", color=body_color,
                                bold_color=bold_color or head_color, leading=1.40,
                                space_before=0.055 if i == 0 else 0.028))
    return blocks


def blocks_height(blocks):
    return sum(b.height for b in blocks) + 2 * PAD


def draw_blocks(ax, blocks, x, y_top):
    y = y_top - PAD
    for b in blocks:
        y = b.draw(ax, x + PAD, y)
    return y


def main():
    # 標題區
    title_p = Paragraph(TITLE, 13.5, W - 2 * M, color="#0F172A", leading=1.25, align="center")
    sub_p = Paragraph(SUBTITLE, 8.6, W - 2 * M, color=MUTED, leading=1.35, align="center", space_before=0.04)
    header_h = title_p.height + sub_p.height + 0.10

    # 投資人（全寬）
    inv_blocks = card_blocks(INVESTOR["title"], INVESTOR["bullets"], W - 2 * M, "#92400E")
    inv_h = blocks_height(inv_blocks)

    # 核心迴路
    LOOP_PAD = 0.09
    LOOP_GAP = 0.78                                   # 企業與客戶之間的箭頭走廊
    loop_head_h = 0.27
    node_w = (W - 2 * M - 2 * LOOP_PAD - LOOP_GAP) / 2
    comp_blocks = card_blocks(COMPANY["title"], COMPANY["bullets"], node_w, "#FFFFFF",
                              body_color="#E2E8F0", bold_color="#7DD3FC")
    cust_blocks = card_blocks(CUSTOMER["title"], CUSTOMER["bullets"], node_w, "#FFFFFF",
                              body_color="#E2E8F0", bold_color="#86EFAC")
    node_h = max(blocks_height(comp_blocks), blocks_height(cust_blocks))
    loop_h = loop_head_h + node_h + LOOP_PAD
    arrow_zone = 0.44                                 # 投資人與企業之間的箭頭區

    # 卡片列
    rows = []
    for r in range(3):
        pair = []
        for c in range(2):
            card = CARDS[r * 2 + c]
            th = THEMES[card["theme"]]
            blocks = card_blocks(f"{card['no']}. {card['title']}", card["bullets"], COL_W, th["head"])
            pair.append((card, blocks))
        rows.append((pair, max(blocks_height(b) for _, b in pair)))

    foot_p = Paragraph(FOOTER, BODY, W - 2 * M - 2 * 0.11, color="#F1F5F9", bold_color="#FCD34D", leading=1.42)
    foot_h = foot_p.height + 2 * 0.085
    src_p = Paragraph(SOURCE, 6.8, W - 2 * M, color="#64748B", leading=1.3)

    total_h = (M + header_h + inv_h + arrow_zone + loop_h + 0.14 +
               sum(h for _, h in rows) + GAP * 3 + foot_h + 0.06 + src_p.height + M + 0.05)
    print(f"canvas = {W:.2f} x {total_h:.2f} in")

    # ------------------------------------------------------------ 繪製
    fig, ax = new_canvas(W, total_h)
    y = total_h - M
    y = title_p.draw(ax, M, y)
    y = sub_p.draw(ax, M, y)
    y -= 0.10

    # 投資人框（虛線＝外部）
    rounded_box(ax, M, y - inv_h, W - 2 * M, inv_h, "#FFFBEB", "#D97706", lw=1.1, ls=(0, (4, 2.5)))
    draw_blocks(ax, inv_blocks, M, y)
    inv_bottom = y - inv_h
    y = inv_bottom - arrow_zone

    # 核心迴路外框
    loop_top = y
    rounded_box(ax, M, loop_top - loop_h, W - 2 * M, loop_h, "#EFF8FF", "#0369A1", lw=1.4, radius=0.08, z=1)
    ax.text(W / 2, loop_top - 0.145, "★ 核心主迴路：企業與客戶是創造價值的「造血引擎」（獲利的真正源頭）",
            fontproperties=fp(9.2, True), color="#075985", ha="center", va="center", zorder=6)
    ny_top = loop_top - loop_head_h
    cx = M + LOOP_PAD
    sx = cx + node_w + LOOP_GAP
    rounded_box(ax, cx, ny_top - node_h, node_w, node_h, "#0F172A", "#38BDF8", lw=1.3)
    draw_blocks(ax, comp_blocks, cx, ny_top)
    rounded_box(ax, sx, ny_top - node_h, node_w, node_h, "#064E3B", "#34D399", lw=1.3)
    draw_blocks(ax, cust_blocks, sx, ny_top)

    # 企業與客戶之間的雙向箭頭
    gx0, gx1 = cx + node_w + 0.04, sx - 0.04
    ya = ny_top - node_h * 0.30
    yb = ny_top - node_h * 0.72
    ax.annotate("", xy=(gx1, ya), xytext=(gx0, ya),
                arrowprops=dict(arrowstyle="-|>,head_length=0.5,head_width=0.25", color="#0284C7", lw=1.8), zorder=5)
    ax.annotate("", xy=(gx0, yb), xytext=(gx1, yb),
                arrowprops=dict(arrowstyle="-|>,head_length=0.5,head_width=0.25", color="#059669", lw=1.8), zorder=5)
    mid = (gx0 + gx1) / 2
    for txt, yy, col in [("聚焦關鍵因素\n給客戶更高效益", ya + 0.17, "#0369A1"),
                         ("回購・營收・毛利\n回饋真實價值", yb - 0.17, "#047857")]:
        ax.text(mid, yy, txt, fontproperties=fp(7.0, True), color=col, ha="center", va="center",
                linespacing=1.25, zorder=6)

    # 投資人與企業之間的雙向箭頭（調整 X 座標與標籤對齊，防止左側文字溢出切斷）
    ax_l = cx + 0.32
    ax_r = cx + node_w - 0.32
    ax.annotate("", xy=(ax_l, ny_top + 0.01), xytext=(ax_l, inv_bottom - 0.01),
                arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.22", color="#D97706", lw=1.5,
                                linestyle=(0, (3, 2))), zorder=5)
    ax.annotate("", xy=(ax_r, inv_bottom - 0.01), xytext=(ax_r, ny_top + 0.01),
                arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.22", color="#D97706", lw=1.5,
                                linestyle=(0, (3, 2))), zorder=5)
    lab_y = (inv_bottom + loop_top) / 2
    ax.text(ax_l + 0.08, lab_y, "注入資金（附帶短期估值壓力）", fontproperties=fp(7.0, True), color="#B45309",
            ha="left", va="bottom", zorder=6)
    ax.text(ax_r - 0.08, lab_y, "回報真實財務成果", fontproperties=fp(7.0, True), color="#B45309",
            ha="right", va="top", zorder=6)
    ax.text(sx + node_w / 2, lab_y, "客戶不直接面對投資人：\n投資人的回報，最終來自客戶買單",
            fontproperties=fp(7.0), color=MUTED, ha="center", va="center", linespacing=1.25, zorder=6)

    y = loop_top - loop_h - 0.14

    # 六張知識卡
    for pair, rh in rows:
        for c, (card, blocks) in enumerate(pair):
            th = THEMES[card["theme"]]
            x = M + c * (COL_W + GAP)
            rounded_box(ax, x, y - rh, COL_W, rh, th["fill"], th["edge"], lw=1.1)
            ax.plot([x + 0.05, x + COL_W - 0.05], [y - 0.012, y - 0.012], color=th["edge"], lw=2.2,
                    solid_capstyle="round", zorder=4)
            draw_blocks(ax, blocks, x, y)
        y -= rh + GAP

    # 底部總結
    y += GAP - 0.06
    rounded_box(ax, M, y - foot_h, W - 2 * M, foot_h, "#1E293B", "#1E293B", lw=0.8)
    foot_p.draw(ax, M + 0.11, y - 0.085)
    y -= foot_h + 0.06
    src_p.draw(ax, M, y)

    fig.savefig(OUT, dpi=DPI, facecolor="white")
    print("saved:", OUT)


if __name__ == "__main__":
    main()
