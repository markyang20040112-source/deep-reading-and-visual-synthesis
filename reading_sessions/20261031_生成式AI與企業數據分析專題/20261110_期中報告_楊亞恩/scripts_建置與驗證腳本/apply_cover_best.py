# -*- coding: utf-8 -*-
import docx, sys, os
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

orig_file = r'C:\Users\User\OneDrive\桌面\期中報告\楊亞恩—初稿.docx'
target_file = r'C:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\楊亞恩.docx'

doc = docx.Document(orig_file)

# 1. Remove paragraphs 0 to 22 (the initial instruction page from the draft)
for i in range(22, -1, -1):
    p = doc.paragraphs[i]
    p._p.getparent().remove(p._p)

first_p = doc.paragraphs[0]

def insert_p_before(ref_p, text='', style='Normal', align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=0):
    new_p = doc.add_paragraph()
    ref_p._p.addprevious(new_p._p)
    new_p.text = text
    new_p.style = doc.styles[style]
    new_p.alignment = align
    if space_before:
        new_p.paragraph_format.space_before = Pt(space_before)
    if space_after:
        new_p.paragraph_format.space_after = Pt(space_after)
    return new_p

def insert_spacer(ref_p, pt_height):
    p = doc.add_paragraph()
    ref_p._p.addprevious(p._p)
    p.paragraph_format.line_spacing = Pt(pt_height)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run('\u00A0')
    r.font.size = Pt(pt_height)
    return p

# ==================== COVER PAGE (Pure Minimalist Golden Ratio) ====================
# Zone 1: Top Breathing Space (Sky) - ~105 pt down from top margin
insert_spacer(first_p, 105)

# Main Title: STRICTLY ONE SINGLE LINE (15.5pt, Bold, Deep Navy)
p_title = insert_p_before(first_p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)
pPr_t = p_title._p.get_or_add_pPr()
pPr_t.append(parse_xml(f'<w:ind {nsdecls("w")} w:left="-360" w:right="-360"/>'))

r_title = p_title.add_run('從數據債到人機協同：生成式 AI 時代下的企業商業分析重構')
r_title.bold = True
r_title.font.name = '標楷體'
r_title.font.size = Pt(15.5)
r_title.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D) # Deep Navy
r_title._r.get_or_add_rPr().append(parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="標楷體" w:ascii="標楷體" w:hAnsi="標楷體"/>'))

# Subtitle Line 1 (Staggered left-center)
p_sub1 = insert_p_before(first_p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
pPr_s1 = p_sub1._p.get_or_add_pPr()
pPr_s1.append(parse_xml(f'<w:ind {nsdecls("w")} w:right="1440"/>')) # shifted left

r_sub1 = p_sub1.add_run('以《哈佛商業評論》四篇專題文章')
r_sub1.font.name = '標楷體'
r_sub1.font.size = Pt(13)
r_sub1.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
r_sub1._r.get_or_add_rPr().append(parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="標楷體" w:ascii="標楷體" w:hAnsi="標楷體"/>'))

# Subtitle Line 2 (Staggered right-center)
p_sub2 = insert_p_before(first_p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=32)
pPr_s2 = p_sub2._p.get_or_add_pPr()
pPr_s2.append(parse_xml(f'<w:ind {nsdecls("w")} w:left="1440"/>')) # shifted right

r_sub2 = p_sub2.add_run('探討企業數據準備、市場研究與顧客價值真義')
r_sub2.font.name = '標楷體'
r_sub2.font.size = Pt(13)
r_sub2.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
r_sub2._r.get_or_add_rPr().append(parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="標楷體" w:ascii="標楷體" w:hAnsi="標楷體"/>'))

# Zone 2: Pure Elegant Negative Space (Generous Golden Ratio Meadow - NO ARTIFICIAL LINE)
insert_spacer(first_p, 85)
insert_spacer(first_p, 85)
insert_spacer(first_p, 85)

# Zone 3: Student Info Table (Lower Third Anchor)
tbl = doc.add_table(rows=4, cols=2)
first_p._p.addprevious(tbl._tbl)
tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
tblPr = tbl._tbl.tblPr
tblPr.append(parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/></w:tblBorders>'))

info_rows = [
    ('指 導 老 師：', '謝懷恕 教授'),
    ('班          級：', '企管系 3B'),
    ('學          號：', '311157139'),
    ('姓          名：', '楊亞恩')
]

for r_idx, (k, v) in enumerate(info_rows):
    row = tbl.rows[r_idx]
    c0, c1 = row.cells[0], row.cells[1]
    c0.width = Inches(2.3)
    c1.width = Inches(2.7)
    
    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p0.paragraph_format.space_after = Pt(18)
    p0.paragraph_format.line_spacing = 1.35
    r0 = p0.add_run(k)
    r0.bold = True
    r0.font.name = '標楷體'
    r0.font.size = Pt(13)
    r0.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    r0._r.get_or_add_rPr().append(parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="標楷體" w:ascii="標楷體" w:hAnsi="標楷體"/>'))
    
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p1.paragraph_format.space_after = Pt(18)
    p1.paragraph_format.line_spacing = 1.35
    r1 = p1.add_run(v)
    r1.bold = True
    r1.font.name = '標楷體'
    r1.font.size = Pt(13)
    r1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    r1._r.get_or_add_rPr().append(parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="標楷體" w:ascii="標楷體" w:hAnsi="標楷體"/>'))

# Page break after Cover
p_break1 = insert_p_before(first_p)
p_break1.add_run().add_break(docx.enum.text.WD_BREAK.PAGE)

# ==================== TABLE OF CONTENTS ====================
p_toc = insert_p_before(first_p, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=20)
r_toc = p_toc.add_run('目　　錄')
r_toc.bold = True
r_toc.font.name = '標楷體'
r_toc.font.size = Pt(18)
r_toc.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
r_toc._r.get_or_add_rPr().append(parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="標楷體" w:ascii="標楷體" w:hAnsi="標楷體"/>'))

toc_items = [
    (1, '壹、本篇心得架構簡介', 'bm_part1', 'P. 2'),
    (1, '貳、四篇文章讀後之心得與想法', 'bm_part2', 'P. 2'),
    (2, '一、《AI 能強化你的數據分析能力》', 'bm_art1', 'P. 2'),
    (2, '二、《你的公司數據真的準備好面對生成式 AI 了嗎？》', 'bm_art2', 'P. 3'),
    (3, '1. 資料結構化的時間成本、資安風險、轉化效益的困境', 'bm_art2_1', 'P. 3'),
    (3, '2. 突破困境的解法：人機協作才能將效益成倍放大', 'bm_art2_2', 'P. 4'),
    (2, '三、《生成式 AI 正在顛覆市場研究》', 'bm_art3', 'P. 5'),
    (3, '1. 幻覺在資料模擬預測下被無限放大', 'bm_art3_1', 'P. 5'),
    (4, 'AI模擬消費者', 'bm_art3_1_sim', 'P. 5'),
    (4, 'AI沒有辦法完全複製人類的「感受」', 'bm_art3_1_spice', 'P. 6'),
    (3, '2. AI更適合訪問人類？AI與人互動能消除幻覺？', 'bm_art3_2', 'P. 6'),
    (3, '3. AI該如何被應用在分析上', 'bm_art3_3', 'P. 7'),
    (2, '四、《顧客需求不靠猜！統計模型找正解》', 'bm_art4', 'P. 8'),
    (3, '1. 人類擅長什麼？AI又擅長什麼呢？', 'bm_art4_1', 'P. 8'),
    (3, '2. 在模型幫助我們撥開迷霧後，我們該如何做？', 'bm_art4_2', 'P. 9'),
    (3, '3. 延伸思考：AI模型在不同類型的企業中定位有何不同', 'bm_art4_3', 'P. 9'),
    (3, '4. 延伸思考：企業、顧客和投資者的三角關係', 'bm_art4_4', 'P. 10'),
    (1, '參、心得結語', 'bm_part3', 'P. 11'),
    (1, '肆、個人對於AI崛起之潮流心得看法', 'bm_part4', 'P. 11'),
    (3, '1. 人們真的懂AI的定義嗎？', 'bm_part4_1', 'P. 11'),
    (3, '2. AI的正確定位為何？', 'bm_part4_2', 'P. 12'),
    (3, '3. AI的使用保險裝置不足', 'bm_part4_3', 'P. 12'),
    (4, '對AI的過於信任', 'bm_part4_3_trust', 'P. 12'),
    (4, 'AI的使用保險失靈', 'bm_part4_3_fail', 'P. 13'),
    (1, '伍、資料來源及使用工具&使用方法', 'bm_part5', 'P. 13'),
    (2, '一、資料來源', 'bm_part5_1', 'P. 13'),
    (2, '二、使用工具&使用方法', 'bm_part5_2', 'P. 14')
]

TAB_POS_DXA = 9028

for level, title, bm_name, page_str in toc_items:
    p_item = insert_p_before(first_p, space_before=1.5, space_after=2.5)
    p_item.paragraph_format.line_spacing = 1.25
    
    pPr = p_item._p.get_or_add_pPr()
    tabs_xml = parse_xml(f'<w:tabs {nsdecls("w")}><w:tab w:val="right" w:leader="dot" w:pos="{TAB_POS_DXA}"/></w:tabs>')
    pPr.append(tabs_xml)
    
    indent_chars = (level - 1) * 2
    if indent_chars > 0:
        p_item.paragraph_format.left_indent = Pt(indent_chars * 11)
        
    size_pt = 13 if level == 1 else (12 if level == 2 else 11)
    is_bold = (level == 1)
    color_hex = "1B365D" if level <= 2 else "2563EB"
    
    clean_title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    hyperlink = parse_xml(f'<w:hyperlink {nsdecls("w")} w:anchor="{bm_name}"/>')
    
    r_t = parse_xml(f'<w:r {nsdecls("w")}><w:rPr><w:rFonts w:ascii="標楷體" w:eastAsia="標楷體" w:hAnsi="標楷體"/><w:sz w:val="{int(size_pt*2)}"/><w:color w:val="{color_hex}"/><w:u w:val="single"/>{"<w:b/>" if is_bold else ""}</w:rPr><w:t>{clean_title}</w:t></w:r>')
    hyperlink.append(r_t)
    
    r_tab = parse_xml(f'<w:r {nsdecls("w")}><w:rPr><w:rFonts w:ascii="標楷體" w:eastAsia="標楷體" w:hAnsi="標楷體"/><w:sz w:val="{int(size_pt*2)}"/><w:color w:val="94A3B8"/></w:rPr><w:tab/></w:r>')
    hyperlink.append(r_tab)
    
    r_p = parse_xml(f'<w:r {nsdecls("w")}><w:rPr><w:rFonts w:ascii="Times New Roman" w:eastAsia="標楷體" w:hAnsi="Times New Roman"/><w:sz w:val="{int(size_pt*2)}"/><w:color w:val="{color_hex}"/><w:u w:val="single"/>{"<w:b/>" if is_bold else ""}</w:rPr><w:t>{page_str}</w:t></w:r>')
    hyperlink.append(r_p)
    
    p_item._p.append(hyperlink)

# Page break after TOC
p_break2 = insert_p_before(first_p)
p_break2.add_run().add_break(docx.enum.text.WD_BREAK.PAGE)

# Add bookmarks to body headings so TOC links work
bm_map = {
    '壹－本篇心得架構簡介': 'bm_part1',
    '貳－四篇文章讀後之心得與想法': 'bm_part2',
    '一、《AI 能強化你的數據分析能力》': 'bm_art1',
    '二、《你的公司數據真的準備好面對生成式 AI 了嗎？》': 'bm_art2',
    '1.資料結構化的時間成本、資安風險、轉化效益的困境': 'bm_art2_1',
    '2.突破困境的解法/人機協做才能將效益成倍放大': 'bm_art2_2',
    '二、《生成式 AI 正在顛覆市場研究》': 'bm_art3',
    '幻覺在資料模擬預測下被無限放大': 'bm_art3_1',
    'AI模擬消費者': 'bm_art3_1_sim',
    'AI沒有辦法完全複製人類的「感受」': 'bm_art3_1_spice',
    '2.AI更適合訪問人類？AI與人互動能消除幻覺？': 'bm_art3_2',
    '3.AI改如何被應用在分析上': 'bm_art3_3',
    '四、《顧客需求不靠猜！統計模型找正解》': 'bm_art4',
    '人類擅長什麼? AI又擅長什麼呢?': 'bm_art4_1',
    '2.在模型幫助我們撥開迷霧後，我們該如何做？': 'bm_art4_2',
    '延伸思考—AI模型在不同類型的企業中定位有和不同': 'bm_art4_3',
    '4.延伸思考—企業、顧客和投資者的三角關係': 'bm_art4_4',
    '伍—心得結語': 'bm_part3',
    '陸—個人對於AI崛起之潮流心得看法': 'bm_part4',
    '人們真的懂AI的定義嗎?': 'bm_part4_1',
    'AI的正確定位為何?': 'bm_part4_2',
    'AI的使用保險裝置不足': 'bm_part4_3',
    '對AI的過於信任': 'bm_part4_3_trust',
    'AI的使用保險失靈': 'bm_part4_3_fail',
    '柒—資料來源及使用工具&使用方法': 'bm_part5',
    '一、資料來源': 'bm_part5_1',
    '二、使用工具&使用方法': 'bm_part5_2'
}

bm_id = 100
for p in doc.paragraphs:
    t = p.text.strip()
    if t in bm_map:
        name = bm_map[t]
        bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bm_id}" w:name="{name}"/>')
        bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bm_id}"/>')
        p._p.insert(0, bm_start)
        p._p.append(bm_end)
        bm_id += 1

doc.save(target_file)
print('SUCCESS: Updated project Word doc with Pure Minimalist Cover (No artificial line)!')
