"""
render_knowledge_diagrams.py
Generates the publication-grade Visual Knowledge Diagrams:
1. 01_article_master_structure_map.png (and .jpg)
2. 02_bicameral_data_architecture.png (and .jpg)
Following Ausubel-Sweller segmenting principle, Cowan 4±1, Müller-Brockmann Swiss grid, and HCL color science.
"""

import sys
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Import local engine
script_dir = os.path.abspath(".agents/skills/deep-reading-and-visual-synthesis/scripts")
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import generate_mindmap as gm
from generate_mindmap import THEMES, configure_cjk_fonts, draw_macro_zone, draw_modern_card, \
    draw_labeled_bezier, draw_canvas_header_and_footer, save_publication_figure

configure_cjk_fonts()

output_dir = os.path.abspath("reading_sessions/20261101_企業數據與生成式AI準備度/02_outputs")
os.makedirs(output_dir, exist_ok=True)


# ==============================================================================
# DIAGRAM 1: ARTICLE MASTER STRUCTURE MAP (全景主架構圖)
# ==============================================================================
def render_master_structure_map():
    theme = THEMES["swiss_editorial"]
    fig, ax = plt.subplots(figsize=(28, 18.5), dpi=240)
    ax.set_facecolor(theme["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Header and Footer
    draw_canvas_header_and_footer(
        ax,
        title="【全景主圖】企業數據資產面對生成式 AI 的準備度與治理策略",
        subtitle="Thomas H. Davenport & Priyanka Tiwari (MIT Sloan / AWS, N=334 CDO 調查實證) ｜ 瑞士網格宏觀結構架構圖",
        takeaway_title="★ 董事會與高層決策鐵律：數據治理非事後補丁，而是模型落地的唯一物理限制",
        takeaway_body="企業私有知識的護城河不在於直接吞吐海量數據，而在於將流沙般的暗數據轉化為具備後設資料標籤、權威審核與單一真實來源 (SSOT) 的混凝土基底。",
        theme=theme
    )

    # 1. Palmer Macro Zones (4 Zones, 2 Left, 2 Right)
    # Left Top: Danger / Pain
    draw_macro_zone(ax, 3.8, 52.5, 30.2, 37.0, "壹、80% 熱潮與 6% 生產落地鴻溝 (Hype vs. Production)", theme)
    # Left Bottom: Warn / Theoretical Bottlenecks
    draw_macro_zone(ax, 3.8, 11.5, 30.2, 38.5, "貳、非結構化數據治理的三大理論壁壘 (Theoretical Barriers)", theme)
    # Right Top: Success / Bicameral Architecture
    draw_macro_zone(ax, 66.0, 52.5, 30.2, 37.0, "參、破局解法：雙腦分層與數據經緯 (Bicameral Architecture)", theme)
    # Right Bottom: Primary / Organizational Strategy
    draw_macro_zone(ax, 66.0, 11.5, 30.2, 38.5, "肆、組織動態學與非對稱 MVP 策略 (Actionable Roadmap)", theme)

    # 2. Central Hub
    hub_x, hub_y, hub_w, hub_h = 36.5, 41.5, 27.0, 17.5
    hub_box = FancyBboxPatch(
        (hub_x, hub_y), hub_w, hub_h,
        boxstyle="round,pad=0.3,rounding_size=1.2",
        linewidth=2.2, edgecolor=theme["hub_border"], facecolor=theme["hub_bg"], zorder=3
    )
    ax.add_patch(hub_box)

    ax.text(hub_x + hub_w/2.0, hub_y + hub_h - 2.0, "【核心焦點】從流沙到混凝土",
            fontsize=15.5, fontweight="bold", color=theme["hub_text"], ha="center", va="top", zorder=4)
    ax.text(hub_x + hub_w/2.0, hub_y + hub_h - 4.4, "跨越企業生成式 AI 的「數據準備度赤字」",
            fontsize=11.2, color=theme["hub_sub"], ha="center", va="top", zorder=4)
    ax.plot([hub_x + 1.5, hub_x + hub_w - 1.5], [hub_y + hub_h - 5.5, hub_y + hub_h - 5.5],
            color=theme["hub_border"], lw=1.0, alpha=0.7, zorder=3.5)

    hub_bullets = [
        "● 範式躍遷：從傳統結構化數字表格 → 非結構化文本/語音/影像",
        "● 最大瓶頸：46% 數據長直指數據品質不良阻礙模型落地",
        "● 致命盲點：大模型天生無法自動消歧數據來源衝突與陳舊事實",
        "● 破局之道：以受控本體庫與主數據管理打造高可靠混凝土基底"
    ]
    by = hub_y + hub_h - 7.0
    for b in hub_bullets:
        ax.text(hub_x + 1.8, by, b, fontsize=9.8, color="#F8FAFC", ha="left", va="top", zorder=4)
        by -= 2.45

    # 3. Sub-cards inside Zones
    # Card 1.1
    c11 = draw_modern_card(
        ax, 5.0, 71.8, 27.8,
        title="80% 熱潮 vs. 6% 落地斷崖",
        bullets=[
            "● 【投資預算膨脹】— 80% 數據主管預期重構商業，62% 擴大 AI 支出",
            "● 【生產環境斷崖】— 僅 6% 真正進入核心業務生產，16% 甚至下令禁止",
            "● 【個人嘗試停滯】— 逾 50% 企業仍停留在個人摸索或部門 POC 階段"
        ],
        theme=theme, accent_key="danger", badge_text="調查實證", fixed_height=15.2
    )
    # Card 1.2
    c12 = draw_modern_card(
        ax, 5.0, 54.2, 27.8,
        title="46% 數據品質瓶頸與暗數據沼澤",
        bullets=[
            "● 【首要落地挑戰】— 46% CDO 認證數據品質不良為最大阻礙",
            "● 【多源衝突失靈】— 大模型無法自動裁決來源矛盾與過期數據",
            "● 【策略嚴重脫節】— 57% 企業未修改數據策略，僅 11% 強烈同意準備就緒"
        ],
        theme=theme, accent_key="danger", badge_text="核心痛點", fixed_height=15.2
    )

    # Card 2.1
    c21 = draw_modern_card(
        ax, 5.0, 31.5, 27.8,
        title="波蘭尼悖論與長尾 OOD 偽陽性",
        bullets=[
            "● 【默會知識難窮盡】— 人類知道的遠比能說出來的多，規則撰寫易組合爆炸",
            "● 【長尾案例過度自信】— 遇未見邊緣案例模型自信套用範本，產出偽陽性標籤",
            "● 【規則衝突陷阱】— 規則過度詳盡反而引發邏輯衝突與注意分散"
        ],
        theme=theme, accent_key="warn", badge_text="語言學壁壘", fixed_height=16.0
    )
    # Card 2.2
    c22 = draw_modern_card(
        ax, 5.0, 13.2, 27.8,
        title="局部單篇抽取 vs. 全局主數據 (MDM)",
        bullets=[
            "● 【單篇正確全局失效】— 範本能抽單篇欄位，無法校驗跨 10 萬份文檔衝突",
            "● 【缺乏單一真實來源】— 缺乏 MDM 實體消歧，同客戶不同別名導致帳目混亂",
            "● 【維度壓平損耗】— 強將文字壓入表格反而抹殺語氣、情緒與隱含因果"
        ],
        theme=theme, accent_key="warn", badge_text="工程壁壘", fixed_height=16.0
    )

    # Card 3.1
    c31 = draw_modern_card(
        ax, 67.2, 71.8, 27.8,
        title="剛性左腦：本體庫與數據經緯",
        bullets=[
            "● 【受控本體詞表 (Ontology)】— 統一代碼與術語字典，杜絕模型自由腦補",
            "● 【主數據管理 (MDM)】— 跨文檔實體對齊消歧，建立不可篡改的 SSOT",
            "● 【數據經緯 (Data Fabric)】— 打造端到端數據目錄、血緣追蹤與後設資料層"
        ],
        theme=theme, accent_key="success", badge_text="確定性基底", fixed_height=15.2
    )
    # Card 3.2
    c32 = draw_modern_card(
        ax, 67.2, 54.2, 27.8,
        title="靈性右腦與前額葉人機協同 (HITL)",
        bullets=[
            "● 【右腦高維語義】— LLM 專注非結構化文字語境理解、模糊匹配與弱監督",
            "● 【前額葉專家裁決】— 領域專家僅仲裁 <5% 左右腦衝突之關鍵邊緣案例",
            "● 【摩根士丹利典範】— 5 年團隊逐篇人工審核打分，奠定金融高可靠底座"
        ],
        theme=theme, accent_key="success", badge_text="雙腦協同", fixed_height=15.2
    )

    # Card 4.1
    c41 = draw_modern_card(
        ax, 67.2, 31.5, 27.8,
        title="破除 71% 觀望與跨職能權力爭奪",
        bullets=[
            "● 【守舊慣性束縛】— 71% CDO 因傳統數據債未清而選擇觀望其他數據專案",
            "● 【組織政治僵局】— CDO、CIO、CTO、數位長爭奪生成式 AI 戰略主導權",
            "● 【凍結盲目微調】— 嚴禁將未清洗的內部流沙數據直接灌入模型微調"
        ],
        theme=theme, accent_key="primary", badge_text="組織動力", fixed_height=16.0
    )
    # Card 4.2
    c42 = draw_modern_card(
        ax, 67.2, 13.2, 27.8,
        title="非對稱 MVP 策略：客服與代碼先發",
        bullets=[
            "● 【非對稱風險收益】— 優先選擇容錯空間大、具即時驗證迴圈之低敏感場景",
            "● 【客服輔助試點】— 真人坐席即時把關，對外風險受控且能顯著提升效能",
            "● 【軟體工程試點】— 編譯器 (Compiler) 與測試套件自動檢驗，反饋週期毫秒級"
        ],
        theme=theme, accent_key="primary", badge_text="落地處方", fixed_height=16.0
    )

    # 4. Connecting Connectors with Novak Relational Phrase Pills
    # Central Hub to Left Zones
    draw_labeled_bezier(ax, (hub_x, hub_y + 12.0), (34.0, 78.0), "引發痛點", theme=theme, accent_key="danger")
    draw_labeled_bezier(ax, (hub_x, hub_y + 4.0), (34.0, 26.0), "遭遇壁壘", theme=theme, accent_key="warn")

    # Central Hub to Right Zones
    draw_labeled_bezier(ax, (hub_x + hub_w, hub_y + 12.0), (66.0, 78.0), "系統破局", theme=theme, accent_key="success")
    draw_labeled_bezier(ax, (hub_x + hub_w, hub_y + 4.0), (66.0, 26.0), "組織落地", theme=theme, accent_key="primary")

    out_png = os.path.join(output_dir, "01_article_master_structure_map.png")
    save_publication_figure(fig, out_png, theme, dpi=240)
    print(f"[OK] Diagram 1 generated at {out_png}")


# ==============================================================================
# DIAGRAM 2: BICAMERAL DATA ARCHITECTURE & GOVERNANCE PIPELINE (專題拓撲圖)
# ==============================================================================
def render_bicameral_architecture_map():
    theme = THEMES["mckinsey_executive"]
    fig, ax = plt.subplots(figsize=(28, 18.5), dpi=240)
    ax.set_facecolor(theme["canvas_bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    draw_canvas_header_and_footer(
        ax,
        title="【專題圖譜】企業數據雙腦架構與非對稱治理推進管線",
        subtitle="Bicameral Data Architecture & Asymmetric Governance Pipeline ｜ 人機分層協同與工程拓撲",
        takeaway_title="★ 系統架構結論：以確定性左腦約束語義右腦，前額葉專家僅仲裁高價值長尾邊緣",
        takeaway_body="左腦知識圖譜與主數據管理提供 100% 零幻覺錨點，右腦大語言模型提供高泛化語義抽取；二者在數據經緯中動態校驗，消除模型自噬性污染。",
        theme=theme
    )

    # Left Container: Rigid Left-Brain (Data Fabric & MDM)
    draw_macro_zone(ax, 3.8, 12.5, 28.5, 76.5, "【剛性左腦】確定性符號與主數據基底 (Zero Hallucination)", theme)
    # Middle Container: Prefrontal Cortex & Validation Engine
    draw_macro_zone(ax, 35.8, 12.5, 28.5, 76.5, "【前額葉核心】人機協同仲裁與數據經緯 (Data Fabric & HITL)", theme)
    # Right Container: Fluid Right-Brain (GenAI & LLM)
    draw_macro_zone(ax, 67.8, 12.5, 28.5, 76.5, "【靈性右腦】高維語義大模型與模糊抽取 (High Generalization)", theme)

    # Cards in Left-Brain
    c_l1 = draw_modern_card(
        ax, 5.0, 68.0, 26.0,
        title="受控本體詞表 (Ontology)",
        bullets=[
            "● 【統一領域術語庫】— 預先定義業務代碼、標準實體名稱與別名關係",
            "● 【消除自由腦補】— 限制模型分類標籤為封閉集合，杜絕術語飄移",
            "● 【多國語言對齊】— 跨國藥廠/金融機構之跨地區專有名詞標準映射"
        ],
        theme=theme, accent_key="primary", badge_text="字典層", fixed_height=18.0
    )
    c_l2 = draw_modern_card(
        ax, 5.0, 43.5, 26.0,
        title="主數據管理 (MDM / SSOT)",
        bullets=[
            "● 【跨文檔實體消歧】— 判定台積電、TSMC 與專案小組為同一商業主體",
            "● 【權威版本裁決】— 合約/財務數據衝突時，強制以已審定版本為準",
            "● 【血緣與 Provenance】— 記錄每筆數據之來源系統、時間戳與修改記錄"
        ],
        theme=theme, accent_key="primary", badge_text="真理層", fixed_height=18.0
    )
    c_l3 = draw_modern_card(
        ax, 5.0, 15.5, 26.0,
        title="後設資料層 (Metadata Layer)",
        bullets=[
            "● 【非結構化打分體系】— 借鏡摩根士丹利為每篇內部報告評分與標註",
            "● 【時效性戳記】— 動態標註過期或廢止文檔，防範過時策略被模型吸納",
            "● 【存取邊界過濾】— 在進入模型檢索前實施嚴格的角色權限 (RBAC) 隔離"
        ],
        theme=theme, accent_key="primary", badge_text="防禦層", fixed_height=21.0
    )

    # Cards in Middle (Prefrontal / Fabric)
    c_m1 = draw_modern_card(
        ax, 37.0, 68.0, 26.0,
        title="雙腦動態校驗閘門 (Gate)",
        bullets=[
            "● 【雙向一致性比對】— 右腦抽取之 JSON 欄位直接對齊左腦本體庫",
            "● 【置信度評估引擎】— 若置信度 < 0.90 或觸發未定義實體，即刻攔截",
            "● 【零幻覺解碼約束】— 強制透過 Pydantic / Outlines 約束輸出語法"
        ],
        theme=theme, accent_key="warn", badge_text="校驗閘門", fixed_height=18.0
    )
    c_m2 = draw_modern_card(
        ax, 37.0, 43.5, 26.0,
        title="前額葉人機迴路 (HITL)",
        bullets=[
            "● 【長尾案例專家仲裁】— 僅 <5% 邊緣衝突案例由領域業務專家審查",
            "● 【主動學習反饋】— 專家修正結果自動沉澱為本體庫新增規則",
            "● 【消滅模型自噬】— 防止微小幻覺沉積為後續微調的受污染數據源"
        ],
        theme=theme, accent_key="warn", badge_text="專家迴路", fixed_height=18.0
    )
    c_m3 = draw_modern_card(
        ax, 37.0, 15.5, 26.0,
        title="非對稱 MVP 試點管線",
        bullets=[
            "● 【第一優先：客服輔助】— 真人坐席覆核，毫無外洩風險，縮短 30% 工時",
            "● 【第二優先：代碼生成】— 編譯器 (Compiler) 毫秒級確定性反饋跑通流程",
            "● 【經驗無損遷移】— 在低風險場景磨合 Prompt 範本後再揮軍核心資產"
        ],
        theme=theme, accent_key="warn", badge_text="試點推進", fixed_height=21.0
    )

    # Cards in Right-Brain
    c_r1 = draw_modern_card(
        ax, 69.0, 68.0, 26.0,
        title="高維語義向量嵌入 (Embeddings)",
        bullets=[
            "● 【保留完整情境語境】— 拒絕二維表格暴力壓平，保留情緒、語氣與隱含脈絡",
            "● 【語義相似度檢索】— 跨語意關聯搜尋，解決傳統關鍵字匹配之斷裂",
            "● 【多模態關聯挖掘】— 連接文字報告、專案圖表與客戶語音錄音"
        ],
        theme=theme, accent_key="success", badge_text="向量潛在空間", fixed_height=18.0
    )
    c_r2 = draw_modern_card(
        ax, 69.0, 43.5, 26.0,
        title="弱監督與上下文抽取 (ICL)",
        bullets=[
            "● 【少樣本範例導航】— 提供 3～5 個高代表性範例進行快速分類",
            "● 【初階候選實體抽取】— 快速掃描非結構化全文並生成候選標籤",
            "● 【非結構化摘要生成】— 自動產出高密度段落摘要並附帶原文引用標記"
        ],
        theme=theme, accent_key="success", badge_text="語義抽取", fixed_height=18.0
    )
    c_r3 = draw_modern_card(
        ax, 69.0, 15.5, 26.0,
        title="檢索增強生成 (GraphRAG)",
        bullets=[
            "● 【知識圖譜錨定】— 檢索時結合左腦知識圖譜，杜絕大模型憑空捏造事實",
            "● 【上下文動態注入】— 將審核通過之最新後設資料即時餵入推論環境",
            "● 【端到端自助洞察】— 實現默克集團倡導的自助式數據見解生成 (Self-Service)"
        ],
        theme=theme, accent_key="success", badge_text="終極應用", fixed_height=21.0
    )

    # Connectors across columns
    draw_labeled_bezier(ax, (31.0, 77.0), (37.0, 77.0), "提供約束", theme=theme, accent_key="primary")
    draw_labeled_bezier(ax, (69.0, 77.0), (63.0, 77.0), "提交候選", theme=theme, accent_key="success")
    draw_labeled_bezier(ax, (50.0, 68.0), (50.0, 61.5), "低置信度升級", theme=theme, accent_key="warn")
    draw_labeled_bezier(ax, (50.0, 43.5), (50.0, 36.5), "成功經驗沉澱", theme=theme, accent_key="primary")

    out_png = os.path.join(output_dir, "02_bicameral_data_architecture.png")
    save_publication_figure(fig, out_png, theme, dpi=240)
    print(f"[OK] Diagram 2 generated at {out_png}")


if __name__ == "__main__":
    render_master_structure_map()
    render_bicameral_architecture_map()
