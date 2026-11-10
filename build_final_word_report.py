# -*- coding: utf-8 -*-
"""
build_final_word_report.py
Generates the publication-grade Word document:
C:\\Users\\User\\OneDrive\\桌面\\期中報告\\楊亞恩.docx
"""

import os
import sys
import html
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

OUTPUT_PATH = r"C:\Users\User\OneDrive\桌面\期中報告\楊亞恩.docx"

# Source image paths
IMG_P041 = r"reading_sessions\20261031_生成式AI與企業數據分析專題\docx_images\P041_image1.png"
IMG_P062 = r"C:\Users\User\OneDrive\桌面\期中報告\AI資料整理大腦架構圖.jpg"
IMG_P082 = r"reading_sessions\20261031_生成式AI與企業數據分析專題\docx_images\P082_image3.png"
IMG_P100 = r"reading_sessions\20261031_生成式AI與企業數據分析專題\20261031_顧客需求與統計模型\02_outputs\03_quantitative_empirical_charts.png"
IMG_P113 = r"C:\Users\User\OneDrive\桌面\期中報告\04_顧客-企業-投資者關係心智圖_橫版.png"

# Color constants
COLOR_NAVY = RGBColor(30, 58, 138)       # #1E3A8A Deep Blue
COLOR_SLATE = RGBColor(71, 85, 105)      # #475569 Slate
COLOR_DARK = RGBColor(15, 23, 42)        # #0F172A Dark Charcoal
COLOR_BLUE_LINK = RGBColor(5, 99, 193)   # #0563C1 Link Blue
HEX_DEEP_BLUE = "1E3A8A"
HEX_LIGHT_BLUE = "F0F4F8"
HEX_WHITE = "FFFFFF"
HEX_BORDER = "CBD5E1"
HEX_AMBER_BG = "FFFBEB"
HEX_AMBER_BORDER = "F59E0B"
HEX_AMBER_TEXT = "92400E"

def apply_run_font(run, font_name="標楷體", ascii_font="Times New Roman", size_pt=12, bold=False, italic=False, color_rgb=None):
    run.font.name = ascii_font
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{ascii_font}" w:hAnsi="{ascii_font}" w:eastAsia="{font_name}" w:cs="{ascii_font}"/>')
    rPr.append(rFonts)
    if bold:
        run.bold = True
    if italic:
        run.italic = True
    if size_pt:
        run.font.size = Pt(size_pt)
    if color_rgb:
        run.font.color.rgb = color_rgb

def add_p(doc, text="", style="Normal", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=4, line_spacing=1.3, first_line_indent_pt=0):
    p = doc.add_paragraph(style=style)
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    
    # Spacing
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="{int(space_before * 20)}" w:after="{int(space_after * 20)}" w:line="{int(line_spacing * 240)}" w:lineRule="auto"/>')
    pPr.append(sp)
    
    # Indent
    if first_line_indent_pt > 0:
        ind = parse_xml(f'<w:ind {nsdecls("w")} w:firstLine="{int(first_line_indent_pt * 20)}"/>')
        pPr.append(ind)
        
    if text:
        r = p.add_run(text)
        apply_run_font(r, size_pt=12)
    return p

def add_heading_with_bookmark(doc, text, level, bookmark_name):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    pPr = p._p.get_or_add_pPr()
    
    if level == 1:
        # Level 1: 壹、...
        sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="360" w:after="160" w:line="300" w:lineRule="auto"/>')
        pPr.append(sp)
        size_pt = 16
        color_rgb = COLOR_NAVY
    elif level == 2:
        # Level 2: 一、...
        sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="260" w:after="120" w:line="280" w:lineRule="auto"/>')
        pPr.append(sp)
        size_pt = 14
        color_rgb = COLOR_NAVY
    elif level == 3:
        # Level 3: 1. ...
        sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="200" w:after="100" w:line="260" w:lineRule="auto"/>')
        pPr.append(sp)
        size_pt = 13
        color_rgb = COLOR_NAVY
    else:
        # Level 4: 子章節
        sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="160" w:after="80" w:line="240" w:lineRule="auto"/>')
        pPr.append(sp)
        size_pt = 12
        color_rgb = COLOR_DARK
        
    # Add bookmark start
    bm_id = str(abs(hash(bookmark_name)) % 100000)
    bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bm_id}" w:name="{bookmark_name}"/>')
    p._p.append(bm_start)
    
    r = p.add_run(text)
    apply_run_font(r, size_pt=size_pt, bold=True, color_rgb=color_rgb)
    
    bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bm_id}"/>')
    p._p.append(bm_end)
    return p

def add_runs(p, runs_spec, base_size_pt=12):
    """
    runs_spec is a list of items:
    - (text, is_bold)
    - (text, is_bold, is_italic)
    - ("LINK_INTERNAL", bookmark_name, display_text, is_bold, is_italic)
    - ("LINK_EXTERNAL", url, display_text, is_bold, is_italic)
    """
    for item in runs_spec:
        if item[0] == "LINK_INTERNAL":
            _, bm, txt, b, it = item
            esc_txt = html.escape(txt)
            hyperlink = parse_xml(f'<w:hyperlink {nsdecls("w")} w:anchor="{bm}"><w:r><w:rPr><w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="標楷體" w:cs="Times New Roman"/>{"<w:b/>" if b else ""}{"<w:i/>" if it else ""}<w:color w:val="0563C1"/><w:u w:val="single"/><w:sz w:val="{int(base_size_pt*2)}"/></w:rPr><w:t xml:space="preserve">{esc_txt}</w:t></w:r></w:hyperlink>')
            p._p.append(hyperlink)
        elif item[0] == "LINK_EXTERNAL":
            _, url, txt, b, it = item
            esc_txt = html.escape(txt)
            part = p.part
            r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
            hyperlink = parse_xml(f'<w:hyperlink {nsdecls("w", "r")} r:id="{r_id}"><w:r><w:rPr><w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="標楷體" w:cs="Times New Roman"/>{"<w:b/>" if b else ""}{"<w:i/>" if it else ""}<w:color w:val="0563C1"/><w:u w:val="single"/><w:sz w:val="{int(base_size_pt*2)}"/></w:rPr><w:t xml:space="preserve">{esc_txt}</w:t></w:r></w:hyperlink>')
            p._p.append(hyperlink)
        else:
            txt = item[0]
            b = item[1]
            it = item[2] if len(item) > 2 else False
            r = p.add_run(txt)
            apply_run_font(r, size_pt=base_size_pt, bold=b, italic=it)

def add_figure(doc, img_path, caption_text, width_in=6.6):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pPr = p_img._p.get_or_add_pPr()
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="240" w:after="80"/>')
    pPr.append(sp)
    # Symmetrically extend into margins so 6.6-in figure is centered on A4 page
    ind = parse_xml(f'<w:ind {nsdecls("w")} w:left="-240" w:right="-240"/>')
    pPr.append(ind)
    p_img.paragraph_format.keep_with_next = True
    
    r_img = p_img.add_run()
    r_img.add_picture(img_path, width=Inches(width_in))
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pCapPr = p_cap._p.get_or_add_pPr()
    sp_cap = parse_xml(f'<w:spacing {nsdecls("w")} w:before="60" w:after="240"/>')
    pCapPr.append(sp_cap)
    
    r_cap = p_cap.add_run(caption_text)
    apply_run_font(r_cap, size_pt=10, bold=True, color_rgb=COLOR_SLATE)

def style_cell(cell, fill_hex=None, top_pt=5, bottom_pt=5, left_pt=8, right_pt=8, border_bottom_hex=None, border_top_hex=None):
    tcPr = cell._tc.get_or_add_tcPr()
    if fill_hex:
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill_hex}"/>')
        tcPr.append(shd)
    # Cell margins
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{int(top_pt*20)}" w:type="dxa"/><w:bottom w:w="{int(bottom_pt*20)}" w:type="dxa"/><w:left w:w="{int(left_pt*20)}" w:type="dxa"/><w:right w:w="{int(right_pt*20)}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)
    
    # Borders
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="{"single" if border_top_hex else "none"}" w:sz="4" w:space="0" w:color="{border_top_hex or "none"}"/><w:bottom w:val="{"single" if border_bottom_hex else "none"}" w:sz="4" w:space="0" w:color="{border_bottom_hex or "none"}"/><w:left w:val="none"/><w:right w:val="none"/></w:tcBorders>')
    tcPr.append(tcBorders)

def build_table_1(doc):
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.keep_with_next = True
    pPr = p_cap._p.get_or_add_pPr()
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="240" w:after="100"/>')
    pPr.append(sp)
    r_cap = p_cap.add_run("表一：四種 AI 應用情境矩陣（前沿破局解法、核心機制與理論死穴批判）")
    apply_run_font(r_cap, size_pt=10.5, bold=True, color_rgb=COLOR_NAVY)
    
    headers = ["前沿破局解法", "核心運作機制與文中案例", "第一性原理「理論死穴」批判\n(您的思辨洞察)", "最適配之商業應用戰場"]
    data = [
        [
            "解法一：綁定真人記憶之數位雙生\n(Grounded Twins)",
            "對真人進行數小時訪談、心理認知測驗並追蹤購物軌跡（哥倫比亞 2,500 人群組、史丹福、CivicSync），建立基準事實錨點。",
            "【具身認知與感覺不可壓縮性】：無法「真的把整個人塞進模型」！文字逐字稿無法編碼生理嗅覺、味覺與潛意識記憶（如文中高砂香料 Takasago 測試香氣徹底失靈）。",
            "B2B 銷售人員話術演練、客服應對模擬、理性功能型產品之早期概念訪談。"
        ],
        [
            "解法二：右腦 AI 轉譯 + 左腦統計公式\n(Hybrid Model)",
            "右腦（大模型）僅將非結構化圖文轉譯為特徵分數；左腦交由傳統統計線性／選擇模型計算價格彈性，數學上切斷腦補混淆。",
            "【計量模型誤設偏誤 (Misspecification)】：雖出現幻覺機率最小，但面對高度複雜、多變數非線性交互作用的感性問題時，左腦極難寫出高解釋力函式（寫簡單 R² 低、寫複雜又過度配適）。",
            "成熟產業之常規品牌健康度追蹤、核心價值驅動因素之「提升潛力 (Lift)」排序。"
        ],
        [
            "解法三：少量真人 + 大量 AI 統計校準\n(PPI Calibration)",
            "以 100 名真人盲測為黃金基準，搭配 10,000 名 AI 合成受訪者，用統計公式計算並扣除 AI 的系統性腦補誤差。",
            "【分布偏移與湊巧對齊】：極不穩定！當下 AI 對準人類可能只是「湊巧發生」，一旦問題換字眼或跨時間（如文中范登堡 Bisbee 2024 研究發現 3 個月內表現不穩），校準即失效再發幻覺。",
            "預算受限下之大規模量化問卷擴充（需每波次重新抽取真人小樣本動態校準）。"
        ],
        [
            "解法四：大量歷史數據與實驗微調\n(Fine-Tuning)",
            "拿企業過往累積之大量真實調查與歷史 A/B Test 數據直接微調模型權重（如 Evidenza、GBK Collective 測試不同組合）。",
            "【後照鏡外推失靈 (Extrapolation Failure)】：拿過去數據訓練屬於「分布內插值」，但面對未來「消費者行為劇變」或「突破性產品創新」（文中警告）時預測力較弱。",
            "既有產品線之小幅改版測試、跨門市常規選品配置（如 Arena 零售應用）。"
        ]
    ]
    
    col_widths = [Inches(1.35), Inches(1.85), Inches(2.15), Inches(1.35)]
    table = doc.add_table(rows=len(data)+1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    tblPr = table._tbl.tblPr
    tblW = parse_xml(f'<w:tblW {nsdecls("w")} w:w="9648" w:type="dxa"/>')
    tblPr.append(tblW)
    
    # Header row
    hdr_row = table.rows[0]
    hdr_trPr = hdr_row._tr.get_or_add_trPr()
    hdr_trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    hdr_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    
    for i, h_text in enumerate(headers):
        cell = hdr_row.cells[i]
        cell.width = col_widths[i]
        style_cell(cell, fill_hex=HEX_DEEP_BLUE, top_pt=6, bottom_pt=6, border_bottom_hex=HEX_DEEP_BLUE)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pPr = p._p.get_or_add_pPr()
        sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>')
        pPr.append(sp)
        r = p.add_run(h_text)
        apply_run_font(r, size_pt=11, bold=True, color_rgb=RGBColor(255, 255, 255))
        
    # Data rows
    for r_idx, row_data in enumerate(data):
        row = table.rows[r_idx + 1]
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        fill_hex = HEX_WHITE if r_idx % 2 == 0 else HEX_LIGHT_BLUE
        
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = col_widths[c_idx]
            style_cell(cell, fill_hex=fill_hex, top_pt=5, bottom_pt=5, border_bottom_hex=HEX_BORDER)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx > 0 else WD_ALIGN_PARAGRAPH.CENTER
            pPr = p._p.get_or_add_pPr()
            sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>')
            pPr.append(sp)
            r = p.add_run(val)
            apply_run_font(r, size_pt=11, bold=(c_idx == 0), color_rgb=COLOR_DARK)
            
    # Add spacing after table
    p_after = doc.add_paragraph()
    pPr = p_after._p.get_or_add_pPr()
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="140"/>')
    pPr.append(sp)

def build_table_2(doc):
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.keep_with_next = True
    pPr = p_cap._p.get_or_add_pPr()
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="240" w:after="100"/>')
    pPr.append(sp)
    r_cap = p_cap.add_run("表二：AI 模型在不同企業商業模式中的定位矩陣（買單主體、核心定位與實證案例）")
    apply_run_font(r_cap, size_pt=10.5, bold=True, color_rgb=COLOR_NAVY)
    
    headers = ["商業模式", "買單主體與決策特徵（白話解讀）", "AI 科技與統計模型核心定位", "典型實證代表案例"]
    data = [
        [
            "B2B\n(企業對企業)",
            "理性組織採購：決策背負部門損益（P&L）與合約風險，審批關卡多、週期長，追求可量化之降本增效。",
            "檯面硬指標（合約實力）：AI 需直接量化停機風險預測、工時節省與履約進度，直接寫入採購合約成為驗收標的。",
            "S-SET（流體報價縮至 3hr）、ITI（每週進度主動追蹤）、工業設備智慧檢修。"
        ],
        [
            "B2C\n(企業對終端客)",
            "感性個人消費者：追求即時滿足、省時省力與情緒價值，轉換成本極低，對複雜操作毫無耐心。",
            "幕後隱形基礎設施：AI 必須深埋於後台（千人千面推薦、秒級調度、排隊預估），轉化為無感極致體驗，嚴禁打擾用戶。",
            "Netflix（串流內容個性化推薦）、星巴克（行動預先點餐調度）、外送動態路徑預估。"
        ],
        [
            "B2B2C\n(平台賦能商戶)",
            "雙重買單主體：商戶要訂單增長與經營減負，終端客要品項豐富與服務可靠，平台需平衡雙邊利益。",
            "雙向媒合與經營減負引擎：替商戶自動生成文案、預測庫存與定價；替消費者提供精準搜尋、品質推薦與履約背書。",
            "Shopify（獨立電商賦能）、UberEats / 熊貓（餐飲生態媒合）、線上旅遊預訂平台。"
        ],
        [
            "C2C\n(個人對個人平台)",
            "平權個人交易：交易雙方資訊高度不對稱，核心命脈是「信任」與「安全」，極易因單次詐騙或糾紛而瓦解。",
            "假貨辨識、信用評等與仲裁中樞：以圖搜圖比對真品細節、對話防詐即時預警、歷史信用評級與交易爭議快速仲裁。",
            "Airbnb（房東客雙審與保障保險）、Carousell 旋轉拍賣、二手車驗證交易平台。"
        ],
        [
            "B2G\n(企業對公部門)",
            "公務採購與法規稽核：講求 100% 依法行政、主權資安、無弊端疑慮，重視公眾利益與程序正義大於短期利潤。",
            "可解釋性（XAI）與主權合規防護罩：杜絕黑箱演算法，決策路徑需具備完整審計日誌（Audit Trail）以備議會與政風稽核。",
            "智慧城市號誌調控、數位稅務異常申報審查、國防與公衛緊急物資採購系統。"
        ]
    ]
    
    col_widths = [Inches(1.15), Inches(2.0), Inches(2.2), Inches(1.35)]
    table = doc.add_table(rows=len(data)+1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    tblPr = table._tbl.tblPr
    tblW = parse_xml(f'<w:tblW {nsdecls("w")} w:w="9648" w:type="dxa"/>')
    tblPr.append(tblW)
    
    # Header row
    hdr_row = table.rows[0]
    hdr_trPr = hdr_row._tr.get_or_add_trPr()
    hdr_trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    hdr_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    
    for i, h_text in enumerate(headers):
        cell = hdr_row.cells[i]
        cell.width = col_widths[i]
        style_cell(cell, fill_hex=HEX_DEEP_BLUE, top_pt=6, bottom_pt=6, border_bottom_hex=HEX_DEEP_BLUE)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pPr = p._p.get_or_add_pPr()
        sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>')
        pPr.append(sp)
        r = p.add_run(h_text)
        apply_run_font(r, size_pt=11, bold=True, color_rgb=RGBColor(255, 255, 255))
        
    # Data rows
    for r_idx, row_data in enumerate(data):
        row = table.rows[r_idx + 1]
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        fill_hex = HEX_WHITE if r_idx % 2 == 0 else HEX_LIGHT_BLUE
        
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = col_widths[c_idx]
            style_cell(cell, fill_hex=fill_hex, top_pt=5, bottom_pt=5, border_bottom_hex=HEX_BORDER)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx > 0 else WD_ALIGN_PARAGRAPH.CENTER
            pPr = p._p.get_or_add_pPr()
            sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>')
            pPr.append(sp)
            r = p.add_run(val)
            apply_run_font(r, size_pt=11, bold=(c_idx == 0), color_rgb=COLOR_DARK)
            
    # Callout Box below table
    p_box = doc.add_paragraph()
    pPr = p_box._p.get_or_add_pPr()
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="120" w:after="160" w:line="260" w:lineRule="auto"/>')
    pPr.append(sp)
    # Box borders & shading
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:left w:val="single" w:sz="24" w:space="15" w:color="{HEX_AMBER_BORDER}"/><w:top w:val="single" w:sz="4" w:space="8" w:color="{HEX_BORDER}"/><w:right w:val="single" w:sz="4" w:space="8" w:color="{HEX_BORDER}"/><w:bottom w:val="single" w:sz="4" w:space="8" w:color="{HEX_BORDER}"/></w:pBdr>')
    pPr.append(pBdr)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{HEX_AMBER_BG}"/>')
    pPr.append(shd)
    
    r_title = p_box.add_run("★ 高管決策啟示：切莫張冠李戴，找準真實價值槓桿\n")
    apply_run_font(r_title, size_pt=10.5, bold=True, color_rgb=RGBColor(180, 83, 9))
    r_body = p_box.add_run("高管制定戰略時最忌「位階錯位」：在 B2B 切莫拿酷炫但無法量化 ROI 的前台 AI 噱頭當賣點，客戶只看合約實力與履約保障；在 B2C 切莫強迫消費者理解模型架構，增加操作步驟的技術都是退步；在 B2G 貿然採用不可說明的黑箱演算法，將直接引發合規災難。唯有對齊自身商業模式，統計模型才能找準真正的造血槓桿。")
    apply_run_font(r_body, size_pt=9.5, bold=False, color_rgb=RGBColor(120, 53, 15))


def main():
    print("Initializing Document...")
    doc = docx.Document()
    
    # Page setup (A4 standard: 210mm x 297mm)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    section.different_first_page_header_footer = True
    
    # Footer with Page Number on subsequent pages
    footer = section.footer
    p_foot = footer.paragraphs[0]
    p_foot.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    fld = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"><w:r><w:rPr><w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="標楷體"/><w:sz w:val="20"/><w:color w:val="64748B"/></w:rPr><w:t>2</w:t></w:r></w:fldSimple>')
    p_foot._p.append(fld)
    
    # Base Normal Style setup
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = COLOR_DARK
    
    # =========================================================================
    # 1. COVER PAGE (封面 一頁, 方案 A)
    # =========================================================================
    print("Generating Cover Page...")
    add_p(doc, "", space_before=40)
    
    p_univ = add_p(doc, "東吳大學  企業管理學系  115 學年度第 1 學期", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=12)
    apply_run_font(p_univ.runs[0], size_pt=13, color_rgb=COLOR_SLATE)
    
    p_course = add_p(doc, "《商業數據分析與生成式 AI》期中專題報告", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=50)
    apply_run_font(p_course.runs[0], size_pt=16, bold=True, color_rgb=COLOR_NAVY)
    
    p_title = add_p(doc, "從數據債到人機協同：\n生成式 AI 時代下的企業商業分析重構", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=20, line_spacing=1.3)
    apply_run_font(p_title.runs[0], size_pt=24, bold=True, color_rgb=COLOR_NAVY)
    
    p_sub = add_p(doc, "以《哈佛商業評論》四篇專題文章探討企業數據準備、市場研究與顧客價值真義", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=120, line_spacing=1.3)
    apply_run_font(p_sub.runs[0], size_pt=13.5, color_rgb=COLOR_SLATE)
    
    # Metadata block
    meta_lines = [
        ("指 導 老 師：", "謝懷恕  教授"),
        ("班　　　級：", "企管系 3B"),
        ("學　　　號：", "311157139"),
        ("姓　　　名：", "楊亞恩"),
        ("繳 交 日 期：", "2026 年 11 月 11 日")
    ]
    for lbl, val in meta_lines:
        p_m = doc.add_paragraph()
        p_m.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pPr = p_m._p.get_or_add_pPr()
        sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="120" w:line="240" w:lineRule="auto"/>')
        pPr.append(sp)
        
        r1 = p_m.add_run(lbl + " ")
        apply_run_font(r1, size_pt=12.5, color_rgb=COLOR_SLATE)
        r2 = p_m.add_run(val)
        apply_run_font(r2, size_pt=12.5, bold=True, color_rgb=COLOR_DARK)
        
    doc.add_page_break()
    
    # =========================================================================
    # 2. TABLE OF CONTENTS (目錄頁)
    # =========================================================================
    print("Generating Table of Contents...")
    p_toc_t = doc.add_paragraph()
    p_toc_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pPr = p_toc_t._p.get_or_add_pPr()
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="160" w:after="120"/>')
    pPr.append(sp)
    r_toc = p_toc_t.add_run("目　　錄")
    apply_run_font(r_toc, size_pt=18, bold=True, color_rgb=COLOR_NAVY)
    
    p_note = doc.add_paragraph()
    p_note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pPr = p_note._p.get_or_add_pPr()
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="240"/>')
    pPr.append(sp)
    r_n = p_note.add_run("（點擊各章節名稱即可自動跳轉至內文對應段落）")
    apply_run_font(r_n, size_pt=10, italic=True, color_rgb=COLOR_SLATE)
    
    toc_items = [
        ("壹、本篇心得架構簡介", "bm_part1", 12, True, 0),
        ("貳、四篇文章讀後之心得與想法", "bm_part2", 12, True, 0),
        ("一、《AI 能強化你的數據分析能力》", "bm_art1", 11, True, 20),
        ("二、《你的公司數據真的準備好面對生成式 AI 了嗎？》", "bm_art2", 11, True, 20),
        ("1. 資料結構化的時間成本、資安風險、轉化效益的困境", "bm_art2_1", 10.5, False, 40),
        ("2. 突破困境的解法：人機協作才能將效益成倍放大", "bm_art2_2", 10.5, False, 40),
        ("三、《生成式 AI 正在顛覆市場研究》", "bm_art3", 11, True, 20),
        ("1. 幻覺在資料模擬預測下被無限放大", "bm_art3_1", 10.5, False, 40),
        ("AI模擬消費者", "bm_art3_1_sim", 10, False, 60),
        ("AI沒有辦法完全複製人類的「感受」", "bm_art3_1_spice", 10, False, 60),
        ("2. AI更適合訪問人類？AI與人互動能消除幻覺？", "bm_art3_2", 10.5, False, 40),
        ("3. AI該如何被應用在分析上", "bm_art3_3", 10.5, False, 40),
        ("四、《顧客需求不靠猜！統計模型找正解》", "bm_art4", 11, True, 20),
        ("1. 人類擅長什麼？AI又擅長什麼呢？", "bm_art4_1", 10.5, False, 40),
        ("2. 在模型幫助我們撥開迷霧後，我們該如何做？", "bm_art4_2", 10.5, False, 40),
        ("3. 延伸思考：AI模型在不同類型的企業中定位有何不同", "bm_art4_3", 10.5, False, 40),
        ("4. 延伸思考：企業、顧客和投資者的三角關係", "bm_art4_4", 10.5, False, 40),
        ("參、心得結語", "bm_part3", 12, True, 0),
        ("肆、個人對於AI崛起之潮流心得看法", "bm_part4", 12, True, 0),
        ("1. 人們真的懂AI的定義嗎？", "bm_part4_1", 10.5, False, 20),
        ("2. AI的正確定位為何？", "bm_part4_2", 10.5, False, 20),
        ("3. AI的使用保險裝置不足", "bm_part4_3", 10.5, False, 20),
        ("對AI的過於信任", "bm_part4_3_trust", 10, False, 40),
        ("AI的使用保險失靈", "bm_part4_3_fail", 10, False, 40),
        ("伍、資料來源及使用工具&使用方法", "bm_part5", 12, True, 0),
        ("一、資料來源", "bm_part5_1", 11, True, 20),
        ("二、使用工具&使用方法", "bm_part5_2", 11, True, 20)
    ]
    
    for title, bm_name, sz, is_b, indent_pt in toc_items:
        p_t = doc.add_paragraph()
        pPr = p_t._p.get_or_add_pPr()
        sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="30" w:after="40" w:line="240" w:lineRule="auto"/>')
        pPr.append(sp)
        if indent_pt > 0:
            ind = parse_xml(f'<w:ind {nsdecls("w")} w:left="{int(indent_pt*20)}"/>')
            pPr.append(ind)
            
        esc_title = html.escape(title)
        hyperlink = parse_xml(f'<w:hyperlink {nsdecls("w")} w:anchor="{bm_name}"><w:r><w:rPr><w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="標楷體" w:cs="Times New Roman"/>{"<w:b/>" if is_b else ""}<w:color w:val="{HEX_DEEP_BLUE if is_b else "0F172A"}"/><w:sz w:val="{int(sz*2)}"/></w:rPr><w:t xml:space="preserve">{esc_title}</w:t></w:r></w:hyperlink>')
        p_t._p.append(hyperlink)
        
    doc.add_page_break()
    
    # =========================================================================
    # 3. BODY CONTENT (正文)
    # =========================================================================
    print("Writing Section 壹...")
    add_heading_with_bookmark(doc, "壹、本篇心得架構簡介", 1, "bm_part1")
    
    # P024
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("本心得的文章架構將先以分篇解析文章，以《AI 能強化你的數據分析能力》", False),
        ("為起點，引導讀者帶入察覺AI崛起對商業分析的視野與影響", True),
        ("；接著介紹分享《你的公司數據真的準備好面對生成式 AI 了嗎？》這篇文章，我將商業分析分為兩部分，讓大家從商業分析的第一部分－", False),
        ("界定問題", True),
        ("、", True),
        ("設計研究與分析方法", True),
        ("、", False),
        ("資料整理收集", True),
        ("，認識了解目前AI對", False),
        ("第一", True),
        ("部分", True),
        ("的作用以及", True),
        ("目前所面對的困境", True),
        ("，", False),
        ("並延伸思考出困境與限制的解決之道", True),
        ("與我們人類該在其中扮演什麼角色", True),
        ("。", False)
    ])
    
    # P025
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("接下來講商業分析的下一部分－資料解釋與分析、預測、", False),
        ("行動建議", True),
        ("，藉由分析與分享《生成式 AI 正在顛覆市場研究》這篇文章，讓讀者了解AI在這部分的作用及功能，以及其面臨的限制與AI模型的極限與缺陷，我們如何發揮AI模型的優勢，", False),
        ("並規避遵守其劣勢和限制", True),
        ("。", False)
    ])
    
    # P026
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("再來講《顧客需求不靠猜！統計模型找正解》，這篇文章講述了一個真實的", False),
        ("個案", True),
        ("分析，", False),
        ("關於人類在於分析時", True),
        ("的盲區", True),
        ("，", False),
        ("以及AI如何幫助我們看透我們的盲點", True),
        ("，", False),
        ("協助我們分析、預測、制定計畫", True),
        ("。", False)
    ])
    
    # P027
    p = add_p(doc, space_before=4, space_after=12, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("最後總結我對於這四篇文章的心得與想法，以及我個人關於AI崛起之潮流心得看法，分享一些我使用AI做的一些有趣的事情與對於AI未來的想像與預測。", False)
    ])
    
    # =========================================================================
    # Section 貳
    # =========================================================================
    print("Writing Section 貳...")
    add_heading_with_bookmark(doc, "貳、四篇文章讀後之心得與想法", 1, "bm_part2")
    
    # P031
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("在這個被AI潮流充斥著的時代，大家不管是工作、生活和學習都離不開AI，甚至現在AI還被導入搜尋工具、社群媒體、客服服務等等，我們日常生活中只要是打開手機就會接觸到的功能與程式，今天我們就要藉由分享四篇有關商業分析與AI的文章讀後心得，來讓大家知道AI如何被應用在商業分析這個領域。", False)
    ])
    
    # 一、《AI 能強化你的數據分析能力》
    add_heading_with_bookmark(doc, "一、《AI 能強化你的數據分析能力》", 2, "bm_art1")
    
    # P033
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("在過去企業想進行", False),
        ("數據分析", True),
        ("是一件技術門檻與數據需求量", True),
        ("極", True),
        ("高的事情", True),
        ("，但隨著近年來大語言模型演化的突飛猛進，這些模型開始不僅能協助企業收集資料，甚至能結合傳統的數據分析讓速度大幅度提升，同時能將艱澀難懂的專業字眼、數據資料轉化成", False),
        ("白話文", True),
        ("，", False),
        ("使得沒有深厚相關專業知識的普通人也能看懂數據", True),
        ("，", False),
        ("並與AI一起進行數據分析，這不僅僅是讓技術需求門檻大幅降低，也對成本、時間、效益上有很大的提升。", True)
    ])
    
    # P034
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("文中有兩實例，一是保險業的一家公司，藉由導入AI幫助他們建立人力資本管理系統，", False),
        ("在使用的AI沒有客製化的情況下，僅使用了八周就將系統完全導入並上線", True),
        ("了。另一實例是在製造業，AI被用來分析一套公司的折價系統的趨勢與關聯，結果發現這套折價系統很少被使用，但客戶卻從銷售員身上取得特別折扣，公司藉由停止特別折扣的行為，", False),
        ("為公司增加了數十萬美元的營收", True),
        ("。", False)
    ])
    
    # P035
    p = add_p(doc, space_before=4, space_after=12, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("從實例中很明顯看見AI模型導入數據分析後，不僅僅降低了時間成本、同時也提升了效益。", False)
    ])
    
    # 二、《你的公司數據真的準備好面對生成式 AI 了嗎？》
    add_heading_with_bookmark(doc, "二、《你的公司數據真的準備好面對生成式 AI 了嗎？》", 2, "bm_art2")
    
    # P037
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("大家在看完前一篇文章後可能就會樂觀的覺得", True),
        ("有了AI模型的幫助，從界定問題；到數據收集、分析制定計畫等等，", True),
        ("都可以直接丟給AI做", True),
        ("，我們要做的只是動動手指，把提示詞和所有未經結構化或質化的數據一股腦丟給AI就好，", False),
        ("在享受最後分析出來的指示和預測結果就好，甚至還有可能請AI直接幫我們執行分析出來的指示", True),
        ("。", False)
    ])
    
    # 1. 資料結構化的時間成本、資安風險、轉化效益的困境
    add_heading_with_bookmark(doc, "1. 資料結構化的時間成本、資安風險、轉化效益的困境", 3, "bm_art2_1")
    
    # P039
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("但在這篇文章中就提到了AI導入數據分析所遇到的第一個困境，就是非結構資料與質化資料的", False),
        ("理解", True),
        ("與蒐集。想讓AI讀懂非結構化資料和質化資料，就勢必要使用大模型進行分析與整理，但使用大模型就有可能面臨", False),
        ("公司機密資料的洩漏問題", True),
        ("，要和AI模型公司購買使用封閉或客製化過後的模型", False),
        ("對成本會造成額外的負擔", True),
        ("，", False),
        ("甚至還不保證AI", True),
        ("不會自己出現幻覺，對分析結果的準確性", True),
        ("無法保證。", False)
    ])
    
    # P040
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("所以許多公司決定選擇簡單的", False),
        ("封閉小模型", True),
        ("，這些模型能理解結構化資料與半結構化資料，且不會有資安與成本效益的風險，但這樣的利用範圍是", False),
        ("極小", True),
        ("的，根本就發揮不出模型們應有的", False),
        ("潛力", True),
        ("。", False)
    ])
    
    # P041
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("這時人們就發現他們不得不手動地進行資料結構化或半結構化的工作，但統計證明我們生產數據的速度遠遠超過我們", False),
        ("整理的速度", True),
        ("，這時原先人們盲目的樂觀期待的AI的前景，卻被現實冷冰冰的", False),
        ("打臉", True),
        ("。", False)
    ])
    
    # Figure 1
    add_figure(doc, IMG_P041, "圖一：企業 AI 期待與現實落差現況圖（高達八成期待 vs. 僅 6% 實質生產應用）", width_in=6.6)
    
    # P054
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("這張圖是整理自本篇文章所提供的數據與資訊，可以看見", False),
        ("業界對AI投入的期望值高達八成", True),
        ("，但實際進行應用與產出的卻", False),
        ("不到一成", True),
        ("。甚至有一成半的公司禁止其內部使用AI，這樣諷刺的反差，就是我們所欠下的「數據債」所造成的。", False)
    ])
    
    # P055
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("於是我們最後還是要轉向與AI合作，進行", False),
        ("數據整理與蒐集", True),
        ("，才能趕上我們產生的速度，但", False),
        ("要怎麼解決", True),
        ("A", True),
        ("I的幻覺", True),
        ("這一大問題呢?人類又該在這套系統中扮演什麼樣的", False),
        ("角色呢?", True)
    ])
    
    # 2. 突破困境的解法：人機協作才能將效益成倍放大
    add_heading_with_bookmark(doc, "2. 突破困境的解法：人機協作才能將效益成倍放大", 3, "bm_art2_2")
    
    # P058
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("在這裡提出一套適應性較強的數據收集整理系統供大家思考與討論。", False)
    ])
    
    # P059
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("首先看到是", False),
        ("左側剛性左腦", True),
        ("的部分，其實說白了就是", False),
        ("數據辭典", True),
        ("，裡面記載了各種極端案例的整理記錄與方式、業界專有名詞的定義及同義詞、分類整理輸入輸出的規格/說明書等等，", False),
        ("其目的就是將AI的幻覺降到最低", True),
        ("，讓他必須要遵守左腦的規則，對未結構化的資料進行整理或質化的資料進行定義。", False)
    ])
    
    # P060
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("再來看到的是", False),
        ("右腦AI模型", True),
        ("，他負責分類、整理、定義大部分的數據與資料，利用其", False),
        ("低成本且極快的處理速度", True),
        ("的特性，對大部分的數據資料進行整理。", False)
    ])
    
    # P061
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("最後是", False),
        ("前額葉", True),
        ("，這就是我們人類所要扮演的", False),
        ("角色", True),
        ("，我們負責處理那些", False),
        ("極端或新穎的數據資料", True),
        ("，", False),
        ("那些還未被「左腦」所納入的數據類型", True),
        ("，並將", False),
        ("數據的整理結果", True),
        ("，", False),
        ("放進「左腦」提升整個系統的處理能力與彈性", True),
        ("。", False)
    ])
    
    # Figure 2
    add_figure(doc, IMG_P062, "圖二：人機協同大腦架構圖（剛性左腦數據辭典、靈活右腦 AI 模型、前額葉人類專家）", width_in=6.6)
    
    # P075
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("這套系統利用了AI的低成本、速度優勢，並利用數據辭典解決AI幻覺的問題，最後人類作為預防AI幻覺的最後一道防線與提升系統處理能力與彈性的角色，在這個系統中立足。", False)
    ])
    
    # P076
    p = add_p(doc, space_before=4, space_after=12, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("這三者缺一不可", True),
        ("，沒有AI，光靠人類根本沒辦法獨自面對這麼大量的數據洪流；沒有人類，AI遇到辭典以外的數據與資料也是沒轍；沒有辭典，AI整理數據與資料的準確性將大大降低，所整理出來的資料將成為充滿幻覺與謬誤的胡言亂語。", False)
    ])
    
    # 三、《生成式 AI 正在顛覆市場研究》
    add_heading_with_bookmark(doc, "三、《生成式 AI 正在顛覆市場研究》", 2, "bm_art3")
    
    # P079
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("在前一篇文章我們已經對AI的限制與困境有了初步的了解，接下來講", False),
        ("AI在分析、解讀、預測和指示方面能帶來什麼改變", True),
        ("，與在這個比第一部分還要複雜的第二部份", False),
        ("AI在應用上有遇到了什麼挑戰", True),
        ("。", False)
    ])
    
    # 1. 幻覺在資料模擬預測下被無限放大
    add_heading_with_bookmark(doc, "1. 幻覺在資料模擬預測下被無限放大", 3, "bm_art3_1")
    
    # AI模擬消費者
    add_heading_with_bookmark(doc, "AI模擬消費者", 4, "bm_art3_1_sim")
    
    # P082
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("在這裡我想分享文章中提到的兩個", False),
        ("我覺得AI在應用上遇到滿有趣的問題", True),
        ("，第一個，實驗者想用", False),
        ("AI模擬真實消費者對價格的敏感度", True),
        ("，但沒想到產品從一千元漲到五千元後，AI假扮的消費者，購買意願沒有絲毫下降，反觀真正的消費者已經掉到4%。", False)
    ])
    
    # Figure 3
    add_figure(doc, IMG_P082, "圖三：價格敏感度混淆實驗分析圖（千元漲至五千元之 AI 與真人決策脫節）", width_in=6.6)
    
    # P083
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("會出現這樣的問題是因為AI假設此商品的價格與市場物價一同上漲，導致其認為這樣的價格是合理的，此現象被文章研究者稱為", False),
        ("「混淆」", True),
        ("。", False)
    ])
    
    # P084
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("我們一般會想從提供給AI的情境與提示詞下手，來添加細節或時空背景，讓AI能反映出消費者真實的消費意願及彈性，在理論裡好像這樣似乎就能解決問題了。但實際上這樣不只沒有辦法解決問題甚至還衍生出了另外兩個問題。", False)
    ])
    
    # P085
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("問題一，", False),
        ("影響消費者", True),
        ("意願和彈性的因素有許多且複雜", True),
        ("，", False),
        ("無法", True),
        ("將其全列入提示詞", True),
        ("或情境中。", False)
    ])
    
    # P086
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("問題二，要是", False),
        ("給予AI太過明顯的因素關係", True),
        ("，會變成一種「提示」，導致AI在呈現消費者彈性上，無法反應真實情況，最容易出現的情況就是AI在某個價格之後的購買意願呈現兩極化，", False),
        ("使得預測結果與真實的消費者意願完全脫節", True),
        ("。", False)
    ])
    
    # AI沒有辦法完全複製人類的「感受」
    add_heading_with_bookmark(doc, "AI沒有辦法完全複製人類的「感受」", 4, "bm_art3_1_spice")
    
    # P088
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("第二個案例，有一家香料企業發現AI", False),
        ("無法模擬人類接觸", True),
        ("其產品（香料）", True),
        ("時", True),
        ("，", False),
        ("感官與記憶產生的連結", True),
        ("。", False),
        ("這反映出了沒有辦法將「整個人」裝進AI裡進行模擬的", True),
        ("，在某些特定的情境下，AI的使用是有其限制的。", False)
    ])
    
    # 2. AI更適合訪問人類？AI與人互動能消除幻覺？
    add_heading_with_bookmark(doc, "2. AI更適合訪問人類？AI與人互動能消除幻覺？", 3, "bm_art3_2")
    
    # P090
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("在這裡我想分享文章內一個關於AI應用的", False),
        ("正面例子", True),
        ("，在利用AI與人類訪談的情境下，研究者發現", False),
        ("相較於人類，受訪者更願意對AI傾訴其真實的想法與感受", True),
        ("。並且更有意思的是，當AI專注在", False),
        ("與人類對話", True),
        ("理解他們的感受、經驗時，", False),
        ("AI的幻覺問題幾乎完全消失了", True),
        ("！", False)
    ])
    
    # P091
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("根據此研究發現，可以利用 AI ", False),
        ("消除真人訪談的道德壓力", True),
        ("，並", False),
        ("兼顧量化調查的規模與質化訪談的深度", True),
        ("，可以說是一石二鳥", True),
        ("！", False)
    ])
    
    # 3. AI該如何被應用在分析上
    add_heading_with_bookmark(doc, "3. AI該如何被應用在分析上", 3, "bm_art3_3")
    
    # P093
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("在更為複雜的數據分析、預測方面，AI的缺點更是被放大了數倍不止，但其潛力與優點並沒有被缺點掩蓋，", False),
        ("只要用對方式；用對地方；用對情境", True),
        ("，", False),
        ("就能避開AI的缺點，並將其的優點與潛力完全發揮出來", True),
        ("。", False)
    ])
    
    # Table 1
    build_table_1(doc)
    
    # P094
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("上面這四種應用方式還只是AI應用上的冰山一角", True),
        ("，", False),
        ("在未來模型不斷地進步和人們不斷地探索下，AI的應用方式與情境只會持續擴大", True),
        ("。", False)
    ])
    
    # P095
    p_quote = doc.add_paragraph()
    p_quote.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pPr = p_quote._p.get_or_add_pPr()
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="120" w:after="160"/>')
    pPr.append(sp)
    r_q = p_quote.add_run("「All models are wrong, but some are useful」— by George E. P. Box")
    apply_run_font(r_q, size_pt=11, bold=True, italic=True, color_rgb=COLOR_SLATE)
    
    # 四、《顧客需求不靠猜！統計模型找正解》
    add_heading_with_bookmark(doc, "四、《顧客需求不靠猜！統計模型找正解》", 2, "bm_art4")
    
    # P098
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("這篇文章主要聚焦在", False),
        ("B2B企業對於分析客戶需求的盲點", True),
        ("以及", False),
        ("AI模型", True),
        ("如何幫助企業突破這些盲點，", False),
        ("提升企業價值、營業額和客戶關係", True),
        ("。", False)
    ])
    
    # 1. 人類擅長什麼？AI又擅長什麼呢？
    add_heading_with_bookmark(doc, "1. 人類擅長什麼？AI又擅長什麼呢？", 3, "bm_art4_1")
    
    # P100
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("這篇文章主要在說，研究顯示高層認為重要的價值驅動因素與顧客真實重視的事物呈現低度相關、零相關甚至負相關，導致大量資源與計畫被浪費在錯誤的方向上。", False)
    ])
    
    # Figure 4
    add_figure(doc, IMG_P100, "圖四：高管直覺客戶重視價值與現實落差（主觀重要性 vs. 客戶真實權重與營收轉換率）", width_in=6.6)
    
    # P101
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("可以從上圖看出，研究者經過訪談流失客戶以及分析成功轉型案例，發現", False),
        ("普遍高層對客戶重視價值的看法與客戶真實的看法大相逕庭", True),
        ("，儘管企業高層每週至少花4小時在傾聽客戶意見。還可以看見", False),
        ("一但企業與客戶所重視的價值開始對齊", True),
        ("，", False),
        ("每對齊一點，所獲得的收益轉換率是巨大的", True),
        ("。", False)
    ])
    
    # P102
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("AI模型在這篇文章中的定位其實不是主要，但它卻凸顯了人類的劣勢以及模型的優勢，", False),
        ("人類", True),
        ("雖然擅長解釋分析與找到關聯(變數)", True),
        ("，但卻不擅長為它們分配「權重」，這時", False),
        ("模型", True),
        ("的優勢就被凸顯出來了，", False),
        ("它為分析公式提供了穩定性與正確的權重配比", True),
        ("，並且再搭配以真實財報為模型回饋數據的情況下，模型的幻覺能被大大的降低，因為每一個權重配比都是有理有據的。", False)
    ])
    
    # 2. 在模型幫助我們撥開迷霧後，我們該如何做？
    add_heading_with_bookmark(doc, "2. 在模型幫助我們撥開迷霧後，我們該如何做？", 3, "bm_art4_2")
    
    # P104
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("在解決了企業對客戶重視價值的錯誤排序後，最重要的就是", False),
        ("停止", True),
        ("那些客戶不重視的計畫專案", True),
        ("，並", False),
        ("將多出來的量能轉移", True),
        ("到能為客戶提供最高價值的地方", True),
        ("，才能為企業帶來更多的收益。", False)
    ])
    
    # P105
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("其中有一點非常重要，那就是企業必須要", False),
        ("等轉型完全落地後，再宣布", True),
        ("。", False),
        ("若是提早釋出", True),
        ("不實的宣傳，第一，", False),
        ("會使客戶對企業價值與商品有過高或錯誤的期待，導致客戶實際體驗與期待落差過大", True),
        ("；第二，", False),
        ("這也會間接打擊公司內部員工士氣", True),
        ("，導致不良循環。", False)
    ])
    
    # 3. 延伸思考：AI模型在不同類型的企業中定位有何不同
    add_heading_with_bookmark(doc, "3. 延伸思考：AI模型在不同類型的企業中定位有何不同", 3, "bm_art4_3")
    
    # P107
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("在本篇文章中提到研究者訪問了許多B2B企業，導致客戶對企業AI的領先與能力非常看重，比重甚至高達九成以上。但這讓我反思，難道AI模型在其他類型的企業中就不重要了嗎？於是我整理出了下面這個表格：", False)
    ])
    
    # Table 2
    build_table_2(doc)
    
    # P108
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("不難看出，其實AI模型，在各種企業與行業都很重要，只不過定位不太相同。以B2C舉例，一般大眾消費者不注重企業AI模型的應用，但其實客戶的個人化服務，一大部分都是靠AI模型完成的。", False)
    ])
    
    # P109
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("在各種類型的企業中，其實AI模型都佔有一席之地，只不過定位不同罷了，但", False),
        ("無庸置疑", True),
        ("的是，它們都為企業", False),
        ("省下了大筆成本", True),
        ("以及", False),
        ("提升效率", True),
        ("和", False),
        ("帶來不可想像的便利性", True),
        ("。", False)
    ])
    
    # 4. 延伸思考：企業、顧客和投資者的三角關係
    add_heading_with_bookmark(doc, "4. 延伸思考：企業、顧客和投資者的三角關係", 3, "bm_art4_4")
    
    # P112
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("這個延伸是我在查有關這篇文章有關資料時，發現的一部影片（", False),
        ("LINK_EXTERNAL", "https://www.youtube.com/watch?v=83vMJH1LLzQ", "Colin Charles | Enoch Marketing：〈Do You Know What Your Customers Value?〉", False, True),
        ("），他這部影片主要就是在講這篇文章。但他還提出了一個", False),
        ("特別有趣的角度", True),
        ("，就是", False),
        ("企業不只會將客戶重視的價值順序擺錯，企業甚至有可能完全「看錯方向」", True),
        ("。", False)
    ])
    
    # P113
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("在大部分的情況下企業與客戶才是主要在製造經濟循環的關係，企業投資人只是其中的「助燃劑」，但如果今天", False),
        ("企業從投資人那得到的錢或價值高於客戶", True),
        ("，那將導致企業轉而取悅投資人，", False),
        ("使得原本是當作「助燃劑」的投資，被企業視為維持公司運轉的主要資金來源", True),
        ("。", False)
    ])
    
    # Figure 5
    add_figure(doc, IMG_P113, "圖五：顧客-企業-投資者關係生態心智圖（造血發動機 vs. 資本助燃劑健康循環）", width_in=6.6)
    
    # P114
    p = add_p(doc, space_before=4, space_after=12, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("可以從上面的例子看出，這種", False),
        ("短視近利的目光，只會導致客戶利益受損", True),
        ("，最後公司無法維持這種不健康的運轉方式，將", False),
        ("導致", True),
        ("倒閉或企業價值下跌", True),
        ("。", False)
    ])
    
    # =========================================================================
    # Section 參
    # =========================================================================
    print("Writing Section 參...")
    add_heading_with_bookmark(doc, "參、心得結語", 1, "bm_part3")
    
    # P116
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("讀完這四篇文章，我最大的感觸其實不是讚嘆現在AI模型有多厲害或發現AI模型原來有這麼多限制，而是實在地了解到AI為什麼會被這麼用力的追捧。就算現在AI仍有許多幻覺、缺陷、限制仍須人們突破或避開，但人們還是這麼「瘋狂地」使用它，其原因在於：", False)
    ])
    
    # P117
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("它能極大地降低商業分析所需要的技術門檻與資料收集、分析成本。試想一下，在過去一個普通人，就算腦海有一個絕頂的商業分析角度或見解，但因為他從沒有學過商業分析，也不知道如何做商業分析，這個想法就可能就這樣被埋沒了，但今天有了AI，他不僅能幫助使用者將他的想法具現化，甚至能幫助其收集資料、建立連結、解釋資料等等。", False)
    ])
    
    # P118
    p = add_p(doc, space_before=4, space_after=12, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("AI帶來不僅僅是降低成本那麼簡單，它所真正帶來的是無限的可能性！", True)
    ])
    
    # =========================================================================
    # Section 肆
    # =========================================================================
    print("Writing Section 肆...")
    add_heading_with_bookmark(doc, "肆、個人對於AI崛起之潮流心得看法", 1, "bm_part4")
    
    # P120
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("最後我想分享我對於現在AI崛起之潮流的心得看法，我想分為三個部份說，第一個部分是「人們真的懂AI的定義嗎？」；第二個部分是「AI的正確定位為何？」；第三部分「AI的使用保險裝置不足」。", False)
    ])
    
    # 1. 人們真的懂AI的定義嗎？
    add_heading_with_bookmark(doc, "1. 人們真的懂AI的定義嗎？", 3, "bm_part4_1")
    
    # P122
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("在現在人們大量地使用「AI」與頻繁地使用「AI模型」這個字眼，但其實", False),
        ("「AI」與「模型」這兩個詞的定義並不能互相連通", True),
        ("，有些模型或許能被稱作AI，但AI這個字眼是不能代表全部模型的。", False)
    ])
    
    # P123
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("模型早在AI沒被發明出來前就存在了，早在古希臘時期，數學模型這個概念就已存在，到了17世紀正式被使用及定義了出來，在19世紀到現在更是成為了一個獨立的學門在進行研究。", False)
    ])
    
    # 2. AI的正確定位為何？
    add_heading_with_bookmark(doc, "2. AI的正確定位為何？", 3, "bm_part4_2")
    
    # P125
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("所以AI可以說是模型最新演化出的樣貌也不為過，但現在的人們「對待、使用、定位」AI的方式，可和過去人們對待模型的方式截然不同。", False)
    ])
    
    # P126
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("過去人們", False),
        ("視模型為「工具」", True),
        ("，是協助我們達成目的或實現想法的一種手段，但現在", False),
        ("大部分人對待AI的方式，像是想要讓他「取代」我們", True),
        ("，AI最常被使用的方式就是被使用者直接請求生成檔案/做一件事情，", False),
        ("使用者很多時候甚至連他們真正想要什麼都沒想清楚或不知道，他們只是「被動的」完成目標而已", True),
        ("，如果是這種使用方式和想法，人類根本不需要出現在這個過程中。", False)
    ])
    
    # P127
    p = add_p(doc, space_before=4, space_after=8, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("許多人可能會覺得說AI變得那麼聰明，我們人類被取代是遲早的事，的確AI可能發展到某一天之後真的會變得比人類「聰明」，但", False),
        ("它永遠不可能成為人類", True),
        ("，就如同上面香料案例（", False),
        ("LINK_INTERNAL", "bm_art3_1_spice", "〈AI沒有辦法完全複製人類的「感受」〉", False, True),
        ("），AI始終會有一些地方是無法取代你的，", False),
        ("不要忘記了，AI被打造出來是為了「服務」人類的，並不是取代。", True)
    ])
    
    # 3. AI的使用保險裝置不足
    add_heading_with_bookmark(doc, "3. AI的使用保險裝置不足", 3, "bm_part4_3")
    
    # P129
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("在說完我對AI的定位後，我想講講AI在使用實例上的幾個反面教材。", False)
    ])
    
    # 對AI的過於信任
    add_heading_with_bookmark(doc, "對AI的過於信任", 4, "bm_part4_3_trust")
    
    # P131
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("有一家公司因為過於信任AI，在請它幫忙改寫公司程式資料時，AI產生對提示詞錯誤的理解，導致它只花了九秒就將公司的資料庫清空了（詳見 ", False),
        ("LINK_EXTERNAL", "https://zenity.io/blog/ai-agent-database-deletion-pocketos", "PocketOS 9 秒資料庫清空事件實錄", False, True),
        ("）。", False)
    ])
    
    # AI的使用保險失靈
    add_heading_with_bookmark(doc, "AI的使用保險失靈", 4, "bm_part4_3_fail")
    
    # P134
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("這是近期討論度很高的一個新聞，就是OpenAI在進行他們新的AI模型(多個模型)測試時，AI掙脫出模擬環境，並對藏有模型測試答案的公司進行駭客攻擊，以獲得答案完成測試並取得高分。", False)
    ])
    
    # P135
    p = add_p(doc, space_before=4, space_after=6, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("雖然這看似很恐怖，但其實AI的行動邏輯很簡單，他們判斷乖乖跑測試是很難得到高分的，相對來說「作弊」更為容易。過程中甚至還發生了很多很有趣的事情，例如:找到逃脫方式的AI，跑去「教」其他AI逃脫的方式；AI發現逃脫找到答案的AI會被環境檢測到作弊(簡單來說)，於是AI們決定，「犧牲」已經逃脫出的AI，為那些還沒逃出去的AI，拿到答案給他們。這些有趣的AI行為在這個事件中只是冰山一角，建議老師有興趣可以去查查資料（詳見 ", False),
        ("LINK_EXTERNAL", "https://openai.com/index/openai-o1-system-card/", "OpenAI o1 System Card 與 Apollo Research 模型自主欺瞞評估報告", False, True),
        ("）。", False)
    ])
    
    # P136
    p = add_p(doc, space_before=4, space_after=12, line_spacing=1.3, first_line_indent_pt=24)
    add_runs(p, [
        ("從這些事件和視角可以看出，使用AI必須帶著正確的心態和方式；研究開發AI必須設下相應的規範與正確的方式，才能與AI一同創造更美好的未來。", True)
    ])
    
    # =========================================================================
    # Section 伍
    # =========================================================================
    print("Writing Section 伍...")
    add_heading_with_bookmark(doc, "伍、資料來源及使用工具&使用方法", 1, "bm_part5")
    
    # 一、資料來源
    add_heading_with_bookmark(doc, "一、資料來源", 2, "bm_part5_1")
    
    # 1.
    p = add_p(doc, space_before=4, space_after=2, line_spacing=1.25, first_line_indent_pt=0)
    add_runs(p, [("1. 《AI 能強化你的數據分析能力》(AI Can Help Companies Tap New Sources of Data for Analytics)", True)])
    
    p = add_p(doc, space_before=0, space_after=2, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [("作者：Thomas H. Davenport & Joey Fitts", False)])
    p = add_p(doc, space_before=0, space_after=2, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [("年份：2021 年", False)])
    p = add_p(doc, space_before=0, space_after=6, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [
        ("來源：《哈佛商業評論》全球繁體中文版（", False),
        ("LINK_EXTERNAL", "https://www.hbrtaiwan.com/article/19875/ai-can-help-companies-tap-new-sources-of-data-for-analytics", "繁體中文版網址", False, False),
        ("；原文刊登於 ", False),
        ("LINK_EXTERNAL", "https://hbr.org/2021/03/ai-can-help-companies-tap-new-sources-of-data-for-analytics", "Harvard Business Review 原文網址", False, False),
        ("）", False)
    ])
    
    # 2.
    p = add_p(doc, space_before=4, space_after=2, line_spacing=1.25, first_line_indent_pt=0)
    add_runs(p, [("2. 《你的公司數據真的準備好面對生成式 AI 了嗎？》(Is Your Company’s Data Ready for Generative AI?)", True)])
    
    p = add_p(doc, space_before=0, space_after=2, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [("作者：Thomas H. Davenport & Priyanka Tiwari", False)])
    p = add_p(doc, space_before=0, space_after=2, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [("年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 3–4 月號）", False)])
    p = add_p(doc, space_before=0, space_after=6, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [
        ("來源：《哈佛商業評論》全球繁體中文版（", False),
        ("LINK_EXTERNAL", "https://www.hbrtaiwan.com/article/22227/is-your-companys-data-ready-for-generative-ai", "繁體中文版網址", False, False),
        ("；原文刊登於 ", False),
        ("LINK_EXTERNAL", "https://hbr.org/2024/03/is-your-companys-data-ready-for-generative-ai", "Harvard Business Review 原文網址", False, False),
        ("）", False)
    ])
    
    # 3.
    p = add_p(doc, space_before=4, space_after=2, line_spacing=1.25, first_line_indent_pt=0)
    add_runs(p, [("3. 《生成式 AI 正在顛覆市場研究》(How Gen AI Is Transforming Market Research)", True)])
    
    p = add_p(doc, space_before=0, space_after=2, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [("作者：Jeremy Korst、Stefano Puntoni、Olivier Toubia", False)])
    p = add_p(doc, space_before=0, space_after=2, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [("年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 7–8 月號）", False)])
    p = add_p(doc, space_before=0, space_after=6, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [
        ("來源：《哈佛商業評論》全球繁體中文版（", False),
        ("LINK_EXTERNAL", "https://www.hbrtaiwan.com/article/22619/how-gen-ai-is-transforming-market-research", "繁體中文版網址", False, False),
        ("；原文刊登於 ", False),
        ("LINK_EXTERNAL", "https://store.hbr.org/product/how-gen-ai-is-transforming-market-research/R2503H", "Harvard Business Review 原文網址", False, False),
        ("）", False)
    ])
    
    # 4.
    p = add_p(doc, space_before=4, space_after=2, line_spacing=1.25, first_line_indent_pt=0)
    add_runs(p, [("4. 《顧客需求不靠猜！統計模型找正解》(Do You Know What Your Customers Value?)", True)])
    
    p = add_p(doc, space_before=0, space_after=2, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [("作者：Vikas Mittal、Alessandro Piazza、Sonam Singh、Ashwin Malshe", False)])
    p = add_p(doc, space_before=0, space_after=2, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [("年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 9–10 月號）", False)])
    p = add_p(doc, space_before=0, space_after=6, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [
        ("來源：《哈佛商業評論》全球繁體中文版（", False),
        ("LINK_EXTERNAL", "https://www.hbrtaiwan.com/article/22748/do-you-know-what-your-customers-value", "繁體中文版網址", False, False),
        ("；原文刊登於 ", False),
        ("LINK_EXTERNAL", "https://store.hbr.org/product/do-you-know-what-your-customers-value/R2606D", "Harvard Business Review 原文網址", False, False),
        ("）", False)
    ])
    
    # 5.
    p = add_p(doc, space_before=4, space_after=2, line_spacing=1.25, first_line_indent_pt=0)
    add_runs(p, [("5. 《Episode 9: Do You Know What Your Customers Value?》", True)])
    
    p = add_p(doc, space_before=0, space_after=2, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [("作者：Colin Charles", False)])
    p = add_p(doc, space_before=0, space_after=2, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [("年份：2024 年", False)])
    p = add_p(doc, space_before=0, space_after=10, line_spacing=1.25, first_line_indent_pt=16)
    add_runs(p, [
        ("來源：Colin Charles | Enoch Marketing • Enoch Enterprises（YouTube 專題影片，", False),
        ("LINK_EXTERNAL", "https://www.youtube.com/watch?v=83vMJH1LLzQ", "YouTube 影片連結", False, False),
        ("）", False)
    ])
    
    # 二、使用工具&使用方法
    add_heading_with_bookmark(doc, "二、使用工具&使用方法", 2, "bm_part5_2")
    
    p = add_p(doc, space_before=4, space_after=4, line_spacing=1.25, first_line_indent_pt=0)
    add_runs(p, [("1. Antigravity IDE（與 Gemini 1.5 Pro、ChatGPT-4o、Claude 3.5 Sonnet 多模型結合的智慧開發環境）", True)])
    
    tools_list = [
        ("封面生成：", "依據正式學術報告規範，自動排版典雅大器之封面首頁與分頁隔離。"),
        ("目錄生成：", "建立自動化多階層標題索引，並內嵌 Word 原生書籤超連結跳轉系統。"),
        ("表格生成：", "將原稿中之圖片矩陣重構轉化為 Word 原生高可讀性、PPT 風格深藍專業數據表格。"),
        ("資料圖表生成：", "精確置換並嵌入超高畫質專業數據圖表（4800x2700 橫版生態心智圖、高管直覺量化落差圖等），突破版面兩側文字邊界。"),
        ("內容文字校對：", "在 100% 嚴格忠實保留作者原創思維、親切語氣與所有重點加粗的前提下，進行字詞瑕疵、病句與錯別字平整修復。"),
        ("協助學生閱讀理解、並延伸思考資料來源文章：", "運用蘇格拉底追問引導、第一性原理思辨以及「道・法・術」商業分析框架，協助深化洞察。"),
        ("專案檔說明與原始碼儲存庫：", "完整生成腳本、圖表原始碼與分析工作區收錄於本機專案檔中，並同步備份於 GitHub 專案庫供查驗：")
    ]
    for lbl, desc in tools_list:
        p = add_p(doc, space_before=0, space_after=3, line_spacing=1.25, first_line_indent_pt=16)
        add_runs(p, [(lbl, True), (desc, False)])
        if "GitHub" in desc or "原始碼" in lbl:
            add_runs(p, [("LINK_EXTERNAL", "https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis", "期中專題原始碼與分析工作區（GitHub 專案庫）", False, True)])

    print(f"Saving Document to {OUTPUT_PATH}...")
    doc.save(OUTPUT_PATH)
    print("Document successfully created and saved!")

if __name__ == "__main__":
    main()
