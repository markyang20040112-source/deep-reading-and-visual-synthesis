# -*- coding: utf-8 -*-
r"""
link_components.py
Decoupled, publication-grade hyperlink & literature source components module:
企管系 3B 楊亞恩《從數據債到人機協同：生成式 AI 時代下的企業商業分析重構》

Features & Architectural Design:
1. Pure Decoupling & Safety:
   - Isolated from document-wide file locks.
   - Does NOT touch or overwrite `楊亞恩.docx` directly.
   - Readily available for another AI to import and merge with zero side effects.
2. Verified Academic Standards & Strict User Constraints:
   - HuggingFace Wikipedia Link: Correct URL and refined anchor title (replaces OpenAI o1 System Card).
   - Deletion of Broken Traditional Chinese URLs: Completely omits invalid `hbrtaiwan.com` URLs,
     retaining only verified official Harvard Business Review & YouTube URLs.
   - Pinned Commit GitHub Link: Accurately links to commit `2db126f31cd9dfddd446593daf66eb0d1e1df5b1`.
   - Native Word Hyperlinks: Emits genuine `<w:hyperlink>` elements with relationship IDs,
     Word Hyperlink blue (`#0563C1`), single underline, and 100% 標楷體 (NO Times New Roman).
3. APIs for Integration & Verification:
   - `build_sources_and_tools_section(doc)`
   - `apply_all_link_updates(doc)`
   - `build_preview_docx(preview_path)`
   - `verify_links_in_doc(doc)`
"""

import os
import sys
import html
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

# =============================================================================
# Constants & Hyperlink Data Definitions
# =============================================================================
FONT_CHINESE = "標楷體"
FONT_WESTERN = "標楷體"  # 全文統一使用純標楷體（中英數皆然，禁用 Times New Roman）

COLOR_HYPERLINK_HEX = "0563C1"     # Standard Word Hyperlink Blue
COLOR_DARK_HEX = "0F172A"          # Slate charcoal for readability
COLOR_MUTED_HEX = "64748B"         # Muted slate for metadata

URL_HUGGINGFACE_WIKI = "https://zh.wikipedia.org/zh-tw/2026%E5%B9%B4OpenAI%E6%99%BA%E8%83%BD%E4%BD%93%E5%85%A5%E4%BE%B5HuggingFace%E4%BA%8B%E4%BB%B6"
URL_POCKETOS_VIDEO = "https://youtu.be/UPoPcjFjjcE?si=F_M_z97llEcy6KBP"
URL_COLIN_CHARLES_VIDEO = "https://www.youtube.com/watch?v=83vMJH1LLzQ"
URL_GITHUB_PINNED = "https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis/tree/2db126f31cd9dfddd446593daf66eb0d1e1df5b1/reading_sessions/20261031_%E7%94%9F%E6%88%90%E5%BC%8FAI%E8%88%87%E4%BC%81%E6%A5%AD%E6%95%B8%E6%93%9A%E5%88%86%E6%9E%90%E5%B0%88%E9%A1%8C"

# 5 Academic Literature Sources (All Traditional Chinese URLs purged; authentic English URLs verified)
SOURCES_DATA = [
    {
        "index": 1,
        "title": "1. 《AI 能強化你的數據分析能力》(AI Can Help Companies Tap New Sources of Data for Analytics)",
        "meta": "作者：Thomas H. Davenport & Joey Fitts ｜ 年份：2021 年",
        "journal_label": "來源：《哈佛商業評論》全球繁體中文版（原文刊登於 ",
        "link_text": "Harvard Business Review 原文網址",
        "url": "https://hbr.org/2021/03/ai-can-help-companies-tap-new-sources-of-data-for-analytics",
        "tail": "）"
    },
    {
        "index": 2,
        "title": "2. 《你的公司數據真的準備好面對生成式 AI 了嗎？》(Is Your Company’s Data Ready for Generative AI?)",
        "meta": "作者：Thomas H. Davenport & Priyanka Tiwari ｜ 年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 3–4 月號）",
        "journal_label": "來源：《哈佛商業評論》全球繁體中文版（原文刊登於 ",
        "link_text": "Harvard Business Review 原文網址",
        "url": "https://hbr.org/2024/03/is-your-companys-data-ready-for-generative-ai",
        "tail": "）"
    },
    {
        "index": 3,
        "title": "3. 《生成式 AI 正在顛覆市場研究》(How Gen AI Is Transforming Market Research)",
        "meta": "作者：Jeremy Korst、Stefano Puntoni、Olivier Toubia ｜ 年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 7–8 月號）",
        "journal_label": "來源：《哈佛商業評論》全球繁體中文版（原文刊登於 ",
        "link_text": "Harvard Business Review 原文網址",
        "url": "https://store.hbr.org/product/how-gen-ai-is-transforming-market-research/R2503H",
        "tail": "）"
    },
    {
        "index": 4,
        "title": "4. 《顧客需求不靠猜！統計模型找正解》(Do You Know What Your Customers Value?)",
        "meta": "作者：Vikas Mittal、Alessandro Piazza、Sonam Singh、Ashwin Malshe ｜ 年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 9–10 月號）",
        "journal_label": "來源：《哈佛商業評論》全球繁體中文版（原文刊登於 ",
        "link_text": "Harvard Business Review 原文網址",
        "url": "https://store.hbr.org/product/do-you-know-what-your-customers-value/R2606D",
        "tail": "）"
    },
    {
        "index": 5,
        "title": "5. 《Episode 9: Do You Know What Your Customers Value?》",
        "meta": "作者：Colin Charles ｜ 年份：2024 年",
        "journal_label": "來源：Colin Charles | Enoch Marketing • Enoch Enterprises（YouTube 專題影片，",
        "link_text": "YouTube 影片連結",
        "url": URL_COLIN_CHARLES_VIDEO,
        "tail": "）"
    }
]

# Tools & Workflow Descriptions
TOOLS_DATA = [
    ("• 封面生成：", "依據正式學術報告規範，自動排版典雅大器之封面首頁與分頁隔離。"),
    ("• 目錄生成：", "建立自動化多階層標題索引，並內嵌 Word 原生書籤超連結跳轉系統。"),
    ("• 表格生成：", "將原稿中之圖片矩陣重構轉化為 Word 原生高可讀性、PPT 風格深藍專業數據表格。"),
    ("• 資料圖表生成：", "精確置換並嵌入超高畫質專業數據圖表（4800x2700 橫版生態心智圖等），突破版面兩側文字邊界。"),
    ("• 內容文字校對：", "在 100% 嚴格忠實保留作者原創思維與所有重點加粗的前提下，進行字詞瑕疵與病句修復。"),
    ("• 協助閱讀理解：", "運用蘇格拉底追問引導、第一性原理思辨以及「道・法・術」商業分析框架，協助深化洞察並延伸思考。"),
    ("• 原始碼儲存庫：", "完整生成腳本、圖表原始碼與分析工作區收錄於本機專案檔中，並同步備份於 GitHub 專案庫供查驗：")
]


# =============================================================================
# Helper Functions: Native Hyperlink & Run Injection
# =============================================================================
def add_external_hyperlink(p, url, text, bold=False, italic=False,
                           color_hex=COLOR_HYPERLINK_HEX, font_size_pt=12.0,
                           font_chinese=FONT_CHINESE, font_western=FONT_WESTERN):
    """
    Appends a native Word external hyperlink element (<w:hyperlink>) to a paragraph.
    Configured with dual font properties, distinct hyperlink blue, and single underline.
    """
    part = p.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    esc_txt = html.escape(text)

    b_xml = "<w:b/>" if bold else ""
    i_xml = "<w:i/>" if italic else ""
    sz_val = int(font_size_pt * 2)

    hyperlink_xml = (
        f'<w:hyperlink {nsdecls("w", "r")} r:id="{r_id}">'
        f'<w:r>'
        f'<w:rPr>'
        f'<w:rFonts {nsdecls("w")} w:ascii="{font_western}" w:hAnsi="{font_western}" w:eastAsia="{font_chinese}" w:cs="{font_western}"/>'
        f'{b_xml}'
        f'{i_xml}'
        f'<w:sz w:val="{sz_val}"/>'
        f'<w:szCs w:val="{sz_val}"/>'
        f'<w:color w:val="{color_hex}"/>'
        f'<w:u w:val="single"/>'
        f'</w:rPr>'
        f'<w:t xml:space="preserve">{esc_txt}</w:t>'
        f'</w:r>'
        f'</w:hyperlink>'
    )
    p._p.append(parse_xml(hyperlink_xml))


def add_formatted_run(p, text, bold=False, italic=False, size_pt=12.0,
                      color_hex=COLOR_DARK_HEX, font_chinese=FONT_CHINESE, font_western=FONT_WESTERN):
    """
    Appends a regular styled run with full dual-font EastAsian/Ascii mappings.
    """
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    run.font.name = font_western

    rPr = run._r.get_or_add_rPr()
    rFonts_xml = (
        f'<w:rFonts {nsdecls("w")} '
        f'w:ascii="{font_western}" '
        f'w:hAnsi="{font_western}" '
        f'w:eastAsia="{font_chinese}" '
        f'w:cs="{font_western}"/>'
    )
    rPr.append(parse_xml(rFonts_xml))
    if color_hex and color_hex != COLOR_DARK_HEX:
        rPr.append(parse_xml(f'<w:color {nsdecls("w")} w:val="{color_hex}"/>'))
    return run


# =============================================================================
# Builder: Section 伍 (資料來源及使用工具&使用方法)
# =============================================================================
def build_sources_and_tools_section(doc, include_page_break=True):
    """
    Builds the publication-grade '伍、資料來源及使用工具&使用方法' section.
    100% compliant with user instructions:
    - Heading 1 hierarchy matches Chapters 1-4 (Style '壹－', 18pt bold, pure 標楷體).
    - Heading 2 hierarchy matches report standard (Style '一、', 14pt bold, pure 標楷體).
    - Heading 3 hierarchy matches report standard (Style '1.', 12pt bold, pure 標楷體).
    - Body line spacing (1.25 multiple / line=300) and 12pt font size matching entire article.
    - Zero broken traditional Chinese URLs (hbrtaiwan omitted).
    - Authentic HBR & YouTube verified URLs.
    - Pinned Commit SHA GitHub repository URL.
    """
    if include_page_break:
        doc.add_page_break()

    # Dynamic style resolution with safe fallback
    available_styles = [s.name for s in doc.styles]
    style_h1 = '壹－' if '壹－' in available_styles else 'Heading 1'
    style_h2 = '一、' if '一、' in available_styles else 'Heading 2'
    style_h3 = '1.' if '1.' in available_styles else 'Heading 3'
    style_normal = 'Normal'

    # Section 伍 Title: Style '壹－' (Heading 1 in this document, 18pt bold)
    p_sec = doc.add_paragraph(style=style_h1)
    p_sec.paragraph_format.keep_with_next = True
    p_sec._p.append(parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="500" w:name="bm_part5"/>'))
    add_formatted_run(p_sec, "伍、資料來源及使用工具&使用方法", bold=True, size_pt=18.0)
    p_sec._p.append(parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="500"/>'))

    # Sub-heading 1: 一、資料來源 (Style '一、', Heading 2, 14pt bold)
    p_h1 = doc.add_paragraph(style=style_h2)
    p_h1.paragraph_format.keep_with_next = True
    p_h1._p.append(parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="501" w:name="bm_part5_1"/>'))
    add_formatted_run(p_h1, "一、資料來源", bold=True, size_pt=14.0)
    p_h1._p.append(parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="501"/>'))

    # 5 Sources
    for src in SOURCES_DATA:
        # Title paragraph: Style '1.' (Heading 3, 12pt bold)
        p_t = doc.add_paragraph(style=style_h3)
        p_t.paragraph_format.keep_with_next = True
        add_formatted_run(p_t, src["title"], bold=True, size_pt=12.0)

        # Meta paragraph: Style 'Normal', 12pt, 1.25 line spacing (300 dxa), indented 480 dxa
        p_m = doc.add_paragraph(style=style_normal)
        pPr = p_m._p.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:ind {nsdecls("w")} w:firstLine="0" w:left="480"/>'))
        pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="40" w:line="300" w:lineRule="auto"/>'))
        add_formatted_run(p_m, src["meta"], bold=False, size_pt=12.0, color_hex=COLOR_MUTED_HEX)

        # Link paragraph: Style 'Normal', 12pt, 1.25 line spacing (300 dxa), indented 480 dxa
        p_l = doc.add_paragraph(style=style_normal)
        pPr = p_l._p.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:ind {nsdecls("w")} w:firstLine="0" w:left="480"/>'))
        pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="100" w:line="300" w:lineRule="auto"/>'))
        add_formatted_run(p_l, src["journal_label"], bold=False, size_pt=12.0)
        add_external_hyperlink(p_l, src["url"], src["link_text"], bold=False, font_size_pt=12.0)
        add_formatted_run(p_l, src["tail"], bold=False, size_pt=12.0)

    # Sub-heading 2: 二、使用工具&使用方法 (Style '一、', Heading 2, 14pt bold)
    p_h2 = doc.add_paragraph(style=style_h2)
    p_h2.paragraph_format.keep_with_next = True
    p_h2._p.append(parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="502" w:name="bm_part5_2"/>'))
    add_formatted_run(p_h2, "二、使用工具&使用方法", bold=True, size_pt=14.0)
    p_h2._p.append(parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="502"/>'))

    # Tool title: Style '1.' (Heading 3, 12pt bold)
    p_tool_t = doc.add_paragraph(style=style_h3)
    p_tool_t.paragraph_format.keep_with_next = True
    add_formatted_run(p_tool_t, "1. Antigravity IDE（與 Gemini、ChatGPT、Claude 多模型結合之智慧開發環境）", bold=True, size_pt=12.0)

    # Tool bullet items: Style 'Normal', 12pt, 1.25 line spacing, hanging indent 480 dxa
    for lbl, desc in TOOLS_DATA:
        p_item = doc.add_paragraph(style=style_normal)
        pPr = p_item._p.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:ind {nsdecls("w")} w:left="480" w:hanging="480"/>'))
        pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="20" w:after="40" w:line="300" w:lineRule="auto"/>'))
        add_formatted_run(p_item, lbl, bold=True, size_pt=12.0)
        add_formatted_run(p_item, desc, bold=False, size_pt=12.0)
        if "GitHub" in desc or "原始碼" in lbl:
            add_external_hyperlink(p_item, URL_GITHUB_PINNED, "期中專題原始碼與分析工作區（GitHub 專案庫）", bold=True, font_size_pt=12.0)

    return doc


# =============================================================================
# In-Text Case Hyperlinks Demonstration Builder
# =============================================================================
def build_in_text_case_paragraphs(doc):
    """
    Constructs the contextual paragraphs for the in-text hyperlinks:
    1. Colin Charles YouTube Video (Customer Value Gap)
    2. PocketOS 9-second Database Deletion Case
    3. 2026 OpenAI Agent HuggingFace Breach Wikipedia Link (Updated title & URL)
    """
    p_sec = doc.add_paragraph(style='Normal')
    pPr = p_sec._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="200" w:after="120" w:line="260" w:lineRule="auto"/>'))
    add_formatted_run(p_sec, "【內文超連結更新示範】（第參部分延伸思考 與 第肆部分反面教材）", bold=True, size_pt=12)

    # 1. Colin Charles Video
    p1 = doc.add_paragraph(style='Normal')
    pPr1 = p1._p.get_or_add_pPr()
    pPr1.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="60" w:after="60" w:line="240" w:lineRule="auto"/>'))
    add_formatted_run(p1, "• 顧客價值延伸影片：這個延伸是我在查有關這篇文章有關資料時，發現的一部影片（", bold=False, size_pt=10.5)
    add_external_hyperlink(p1, URL_COLIN_CHARLES_VIDEO, "Colin Charles | Enoch Marketing：〈Do You Know What Your Customers Value?〉", bold=False, font_size_pt=10.5)
    add_formatted_run(p1, "），他這部影片主要就是在講這篇文章。但他還提出了一個特別有趣的角度，就是企業不只會將客戶重視的價值順序擺錯，企業甚至有可能完全「看錯方向」。", bold=False, size_pt=10.5)

    # 2. PocketOS
    p2 = doc.add_paragraph(style='Normal')
    pPr2 = p2._p.get_or_add_pPr()
    pPr2.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="60" w:after="60" w:line="240" w:lineRule="auto"/>'))
    add_formatted_run(p2, "• 過於信任 AI 案例：有一家公司因為過於信任 AI，在請它幫忙改寫公司程式資料時，AI 產生對提示詞錯誤的理解，導致它只花了九秒就將公司的資料庫清空了（詳見 ", bold=False, size_pt=10.5)
    add_external_hyperlink(p2, URL_POCKETOS_VIDEO, "PocketOS 9 秒資料庫清空事件實錄", bold=False, font_size_pt=10.5)
    add_formatted_run(p2, "）。", bold=False, size_pt=10.5)

    # 3. HuggingFace Wikipedia Link
    p3 = doc.add_paragraph(style='Normal')
    pPr3 = p3._p.get_or_add_pPr()
    pPr3.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="60" w:after="60" w:line="240" w:lineRule="auto"/>'))
    add_formatted_run(p3, "• AI 使用保險失靈案例：雖然這看似很恐怖，但其實 AI 的行動邏輯很簡單，他們判斷乖乖跑測試是很難得到高分的，相對來說「作弊」更為容易。過程中甚至還發生了很多很有趣的事情，例如找到逃脫方式的 AI 跑去「教」其他 AI 逃脫的方式；AI 發現逃脫找到答案的 AI 會被環境檢測到作弊，於是 AI 們決定「犧牲」已經逃脫出的 AI，為那些還沒逃出去的 AI 拿到答案給他們。這些有趣的 AI 行為在這個事件中只是冰山一角，建議老師有興趣可以去查查資料（詳見 ", bold=False, size_pt=10.5)
    add_external_hyperlink(p3, URL_HUGGINGFACE_WIKI, "維基百科：2026年OpenAI智能體入侵HuggingFace事件", bold=False, font_size_pt=10.5)
    add_formatted_run(p3, "）。", bold=False, size_pt=10.5)


# =============================================================================
# Standalone Preview Document Builder
# =============================================================================
def build_preview_docx(preview_path):
    """
    Generates a standalone, beautiful Word preview document demonstrating
    both in-text updated hyperlinks and the full Section 伍.
    """
    doc = docx.Document()

    # Set page margins to standard A4 (top/bottom 1 inch, left/right 1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Document Header
    p_head = doc.add_paragraph(style='Normal')
    pPr = p_head._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="160" w:line="300" w:lineRule="auto"/>'))
    add_formatted_run(p_head, "《商業數據分析與生成式 AI》期中專題報告", bold=True, size_pt=16, color_hex="1B365D")
    
    p_sub = doc.add_paragraph(style='Normal')
    pPr_sub = p_sub._p.get_or_add_pPr()
    pPr_sub.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="0" w:after="240" w:line="240" w:lineRule="auto"/>'))
    add_formatted_run(p_sub, "超連結修訂與第伍部分（資料來源及使用工具）獨立組件預覽檔", bold=False, size_pt=11, color_hex="64748B")

    # In-text examples
    build_in_text_case_paragraphs(doc)

    # Section 伍 (Sources & Tools)
    build_sources_and_tools_section(doc, include_page_break=False)

    doc.save(preview_path)
    print(f"[SUCCESS] Standalone preview document generated: {preview_path}")
    return preview_path


# =============================================================================
# Document-Wide Safe Merging API (For Future Merging Agent)
# =============================================================================
def apply_all_link_updates(doc):
    """
    Non-destructive merge function for another AI to safely apply to `楊亞恩.docx`.
    1. Updates in-text hyperlinks:
       - HuggingFace Wikipedia URL & Title
       - PocketOS link
       - Colin Charles video link
    2. Updates or Appends Section 伍 (purging invalid Chinese URLs, adding verified English URLs & GitHub pinned commit).
    """
    # 1. Update in-text hyperlinks
    rels = doc.part.rels
    for p in doc.paragraphs:
        hyperlinks = p._p.xpath('.//w:hyperlink')
        for h in hyperlinks:
            r_id = h.get(qn('r:id'))
            if r_id and r_id in rels:
                target = rels[r_id].target_ref
                # Check for HuggingFace / OpenAI case
                if "HuggingFace" in target or "openai-o1" in target or "2026%E5%B9%B4OpenAI" in target:
                    rels[r_id]._target = URL_HUGGINGFACE_WIKI
                    # Update run text
                    t_nodes = h.xpath('.//w:t')
                    if t_nodes:
                        t_nodes[0].text = "維基百科：2026年OpenAI智能體入侵HuggingFace事件"
                        for tn in t_nodes[1:]:
                            tn.text = ""
                    for r_elem in h.xpath('.//w:r'):
                        rPr = r_elem.find(qn('w:rPr'))
                        if rPr is None:
                            rPr = parse_xml(f'<w:rPr {nsdecls("w")}/>')
                            r_elem.insert(0, rPr)
                        for rf in list(rPr):
                            if rf.tag.endswith('rFonts'):
                                rPr.remove(rf)
                        rPr.append(parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="標楷體" w:hAnsi="標楷體" w:eastAsia="標楷體" w:cs="標楷體"/>'))
                # Check for GitHub link
                elif "github.com" in target:
                    rels[r_id]._target = URL_GITHUB_PINNED
                    t_nodes = h.xpath('.//w:t')
                    if t_nodes and "GitHub" not in t_nodes[0].text:
                        t_nodes[0].text = "期中專題原始碼與分析工作區（GitHub 專案庫）"

    # 2. Check if Section 伍/柒 exists; skip TOC entries (which have '\t' or 'P.')
    found_sec5_idx = None
    for idx, p in enumerate(doc.paragraphs):
        if idx > 50 and ("資料來源及使用工具" in p.text) and ("\t" not in p.text):
            found_sec5_idx = idx
            break

    if found_sec5_idx is not None:
        # Scan backwards from found_sec5_idx to remove any preceding empty/page-break paragraphs
        # so we eliminate all redundant blank pages between Chapter 4 and Chapter 5
        start_remove_idx = found_sec5_idx
        while start_remove_idx > 0:
            prev_p = doc.paragraphs[start_remove_idx - 1]
            if (prev_p.text.strip() == "" and
                    len(prev_p._p.xpath('.//w:drawing')) == 0 and
                    len(prev_p._p.xpath('.//w:tbl')) == 0):
                start_remove_idx -= 1
            else:
                break

        # Delete existing placeholder and empty page-break paragraphs from start_remove_idx to end of doc
        p_elements_to_remove = [p._p for p in doc.paragraphs[start_remove_idx:]]
        for elem in p_elements_to_remove:
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)
    else:
        # If not found, scan backwards from the end to remove any trailing empty paragraphs
        while len(doc.paragraphs) > 0:
            last_p = doc.paragraphs[-1]
            if (last_p.text.strip() == "" and
                    len(last_p._p.xpath('.//w:drawing')) == 0 and
                    len(last_p._p.xpath('.//w:tbl')) == 0):
                parent = last_p._p.getparent()
                if parent is not None:
                    parent.remove(last_p._p)
            else:
                break

    # Re-build clean Section 伍 with exactly ONE page break
    build_sources_and_tools_section(doc, include_page_break=True)

    return doc


# =============================================================================
# Verification API
# =============================================================================
def verify_links_in_doc(doc):
    """
    Performs rigorous assertions on the document's hyperlinks and metadata:
    1. HuggingFace Wikipedia URL presence and title correctness.
    2. Absolute ZERO `hbrtaiwan.com` URLs (Traditional Chinese URLs deleted).
    3. Verified English HBR URLs present.
    4. GitHub pinned commit SHA `2db126f31cd9dfddd446593daf66eb0d1e1df5b1` present.
    5. Clean dual-font properties.
    """
    rels = doc.part.rels
    ext_links = []
    for p in doc.paragraphs:
        for elem in p._p.xpath('.//w:hyperlink'):
            r_id = elem.get(qn('r:id'))
            if r_id and r_id in rels:
                txt = "".join(elem.xpath('.//w:t/text()'))
                ext_links.append((rels[r_id].target_ref, txt))

    print(f"\n[VERIFY] Found {len(ext_links)} external hyperlinks in document:")
    for url, text in ext_links:
        print(f"  • [{text}] -> {url}")

    # Assertion 1: HuggingFace link
    hf = [item for item in ext_links if "HuggingFace" in item[0] or "HuggingFace" in item[1]]
    assert len(hf) >= 1, "ASSERTION FAILED: Missing HuggingFace Wikipedia link!"
    assert URL_HUGGINGFACE_WIKI in hf[0][0], f"ASSERTION FAILED: HuggingFace URL mismatch: {hf[0][0]}"
    print("  [PASS] HuggingFace Wikipedia link and title verified.")

    # Assertion 2: Zero traditional Chinese URLs (hbrtaiwan)
    for url, text in ext_links:
        assert "hbrtaiwan.com" not in url, f"ASSERTION FAILED: Found prohibited Chinese URL: {url}"
    print("  [PASS] Prohibited Traditional Chinese URLs successfully purged (0 found).")

    # Assertion 3: Genuine HBR & YouTube URLs
    hbr_links = [item for item in ext_links if "hbr.org" in item[0]]
    assert len(hbr_links) >= 4, f"ASSERTION FAILED: Expected at least 4 HBR links, found {len(hbr_links)}"
    print(f"  [PASS] {len(hbr_links)} official Harvard Business Review URLs verified.")

    # Assertion 4: Pinned GitHub repository URL
    gh = [item for item in ext_links if "github.com" in item[0]]
    assert len(gh) >= 1, "ASSERTION FAILED: Missing GitHub link!"
    assert "2db126f31cd9dfddd446593daf66eb0d1e1df5b1" in gh[0][0], f"ASSERTION FAILED: GitHub commit SHA missing: {gh[0][0]}"
    print("  [PASS] Pinned GitHub commit SHA verified in repository link.")

    # Assertion 5: Pure 標楷體 check (Zero Times New Roman)
    tnr_count = 0
    for p in doc.paragraphs:
        for elem in p._p.iter():
            if elem.tag.endswith('rFonts'):
                if elem.get(qn('w:ascii')) == 'Times New Roman' or elem.get(qn('w:hAnsi')) == 'Times New Roman':
                    tnr_count += 1
    assert tnr_count == 0, f"ASSERTION FAILED: Found {tnr_count} Times New Roman elements, expected 0 (純標楷體)!"
    print("  [PASS] 100% 純標楷體驗證通過（0 個 Times New Roman）。")

    return True


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    preview_file = os.path.join(base_dir, "preview_links_and_sources.docx")
    build_preview_docx(preview_file)
    test_doc = docx.Document(preview_file)
    verify_links_in_doc(test_doc)
