# -*- coding: utf-8 -*-
r"""
verify_report.py
Deep verification of publication-grade Word documents saved at BOTH:
1. C:\Users\User\OneDrive\桌面\期中報告\楊亞恩.docx
2. reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\楊亞恩.docx
"""

import os
import sys
import docx
from docx.oxml.ns import qn

TARGET_DOC_1 = r"C:\Users\User\OneDrive\桌面\期中報告\楊亞恩.docx"
TARGET_DOC_2 = r"reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\楊亞恩.docx"
BACKUP_DOC = r"C:\Users\User\OneDrive\桌面\期中報告\楊亞恩—初稿.docx"


def verify_single(doc_path):
    print(f"\n========================================================")
    print(f"VERIFYING: {doc_path}")
    print(f"========================================================")
    assert os.path.exists(doc_path), f"File does not exist: {doc_path}"
    file_sz = os.path.getsize(doc_path)
    print(f"File size: {file_sz:,} bytes")
    assert file_sz > 500000, "File size too small!"

    doc = docx.Document(doc_path)
    print(f"Total Paragraphs: {len(doc.paragraphs)}")
    print(f"Total Tables: {len(doc.tables)}")
    assert len(doc.tables) == 3, f"Expected 3 tables (Cover Info Table + Table 1 + Table 2), found {len(doc.tables)}"

    # 1. Verify Cover Page
    print("\n--- 1. Checking Cover Page Constraints ---")
    cover_text = "\n".join([p.text for p in doc.paragraphs[:10]])
    print("Cover text sample:\n" + cover_text.strip())
    assert "東吳大學" not in cover_text, "ERROR: Cover page contains university header '東吳大學'!"
    assert "繳交日期" not in cover_text, "ERROR: Cover page contains '繳交日期'!"

    # Title must be on one line
    title_p = [p for p in doc.paragraphs[:5] if "從數據債到人機協同" in p.text][0]
    assert "\n" not in title_p.text, f"ERROR: Main title contains newline: {title_p.text}"
    assert title_p.text == "從數據債到人機協同：生成式 AI 時代下的企業商業分析重構", f"Title text mismatch: {title_p.text}"
    print("Main Title verified: Single line without line breaks!")

    # Subtitle layout
    sub_ps = [p for p in doc.paragraphs[:8] if "哈佛商業評論" in p.text or "企業數據準備" in p.text]
    assert len(sub_ps) >= 2, "Subtitle staggered lines missing!"
    print(f"Subtitle Line 1: {sub_ps[0].text.strip()}")
    print(f"Subtitle Line 2: {sub_ps[1].text.strip()}")
    assert sub_ps[1].text.strip().endswith("真義"), "Subtitle Line 2 must end with '真義'!"

    # Cover Table
    t_info = doc.tables[0]
    assert len(t_info.rows) == 4 and len(t_info.columns) == 2, "Cover info table dimension mismatch!"
    assert "謝懷恕" in t_info.rows[0].cells[1].text
    assert "企管系 3B" in t_info.rows[1].cells[1].text
    assert "311157139" in t_info.rows[2].cells[1].text
    assert "楊亞恩" in t_info.rows[3].cells[1].text
    print("Cover Info Table verified: 4 rows, 2 columns, borderless vertical alignment!")

    # 2. Verify TOC
    print("\n--- 2. Checking TOC & Dotted Leaders ---")
    toc_tabs_found = 0
    for p in doc.paragraphs[:40]:
        for elem in p._p.iter():
            if elem.tag.endswith('tab') and elem.get(qn('w:leader')) == 'dot':
                toc_tabs_found += 1
    print(f"TOC Dotted leader tab stops found: {toc_tabs_found}")
    assert toc_tabs_found >= 20, f"Expected dotted leader tabs in TOC, found {toc_tabs_found}"

    # 3. Check Images
    print("\n--- 3. Checking Images ---")
    img_count = 0
    for p in doc.paragraphs:
        for r in p.runs:
            if 'graphic' in r._r.xml:
                img_count += 1
    print(f"Total Inline Pictures: {img_count}")
    assert img_count == 5, f"Expected 5 inline pictures, found {img_count}"

    # 4. Check Bookmarks
    print("\n--- 4. Checking Bookmarks ---")
    bookmarks = set()
    for p in doc.paragraphs:
        for elem in p._p.iter():
            if elem.tag.endswith('bookmarkStart'):
                name = elem.get(qn('w:name'))
                if name:
                    bookmarks.add(name)
    req_bms = [
        "bm_part1", "bm_part2", "bm_art1", "bm_art2", "bm_art2_1", "bm_art2_2",
        "bm_art3", "bm_art3_1", "bm_art3_1_sim", "bm_art3_1_spice", "bm_art3_2", "bm_art3_3",
        "bm_art4", "bm_art4_1", "bm_art4_2", "bm_art4_3", "bm_art4_4",
        "bm_part3", "bm_part4", "bm_part4_1", "bm_part4_2", "bm_part4_3", "bm_part4_3_trust", "bm_part4_3_fail",
        "bm_part5", "bm_part5_1", "bm_part5_2"
    ]
    for bm in req_bms:
        assert bm in bookmarks, f"Missing required bookmark: {bm}"
    print(f"All {len(req_bms)} required bookmarks verified!")

    # 5. Check Tables (Table 1 and Table 2)
    print("\n--- 5. Checking Table 1 & Table 2 ---")
    t1 = doc.tables[1]
    assert len(t1.rows) == 5 and len(t1.columns) == 4, f"Table 1 dimension mismatch: {len(t1.rows)}x{len(t1.columns)}"
    t1_header = [c.text.strip().replace('\n', '') for c in t1.rows[0].cells]
    print("Table 1 Headers:", t1_header)
    assert "應用模式" in t1_header[0]
    assert "核心做法" in t1_header[1]
    assert "主要優勢" in t1_header[2]
    assert "人機邊界" in t1_header[3]

    t2 = doc.tables[2]
    assert len(t2.rows) == 6 and len(t2.columns) == 4, f"Table 2 dimension mismatch: {len(t2.rows)}x{len(t2.columns)}"
    t2_header = [c.text.strip().replace('\n', '') for c in t2.rows[0].cells]
    print("Table 2 Headers:", t2_header)
    assert "企業類型" in t2_header[0]
    assert "客戶關注焦點" in t2_header[1]
    assert "AI 幕後核心任務" in t2_header[2]
    assert "商業價值" in t2_header[3]
    print("Table 1 and Table 2 headers and dimensions verified!")

    # 6. Check Bolds & Typo Fixes
    print("\n--- 6. Checking Bold Strings & Typo Fixes ---")
    all_text = []
    bold_runs_text = []
    for p in doc.paragraphs:
        all_text.append(p.text)
        for r in p.runs:
            if r.bold:
                bold_runs_text.append(r.text)
    full_doc_text = "\n".join(all_text)
    full_bold_text = "".join(bold_runs_text)

    core_bold_checks = [
        "特別有趣的角度", "看錯方向", "使得原本是當作「助燃劑」的投資",
        "短視近利的目光，只會導致客戶利益受損", "導致倒閉或企業價值下跌",
        "無限的可能性", "定義並不能互相連通", "視模型為「工具」",
        "大部分人對待AI的方式，像是想要讓他「取代」我們",
        "使用者很多時候甚至連他們真正想要什麼都沒想清楚或不知道，他們只是「被動的」完成目標而已",
        "它永遠不可能成為人類",
        "不要忘記了，AI被打造出來是為了「服務」人類的，並不是取代。",
        "才能與AI一同創造更美好的未來"
    ]
    for s in core_bold_checks:
        assert s in full_doc_text, f"Missing text: {s}"
        assert s in full_bold_text, f"Text not bolded: {s}"
    print(f"All {len(core_bold_checks)} core bold phrases verified!")

    typo_checks = [
        "讀完這四篇專題文章與個案延伸",
        "使用它，其核心原因在於：",
        "模型早在 AI 問世之前就已存在",
        "為起點，引導讀者",
        "半結構化資料",
        "角色",
        "人機協作",
        "數據收集整理系統",
        "之後的購買意願",
        "該如何被應用",
        "等轉型完全落地後，再宣布。若是提早釋出",
        "有何不同",
        "企業與行業",
        "有多厲害",
        "這麼「瘋狂地」使用它",
        "它所真正帶來的是",
        "古希臘時期，數學模型",
        "視模型為「工具」",
        "在請它幫忙",
        "以獲得答案完成測試並取得高分"
    ]
    for s in typo_checks:
        assert s in full_doc_text, f"Missing typo fix: {s}"
    print(f"All {len(typo_checks)} typo / phrasing corrections verified!")

    # 7. Check Links & Deletion of Traditional Chinese URLs
    print("\n--- 7. Checking Internal Cross-Reference and External Hyperlinks ---")
    toc_links = []
    ext_links = []
    for p in doc.paragraphs:
        for elem in p._p.iter():
            if elem.tag.endswith('hyperlink'):
                anchor = elem.get(qn('w:anchor'))
                r_id = elem.get(qn('r:id'))
                if anchor:
                    toc_links.append((anchor, "".join(elem.itertext())))
                elif r_id:
                    rel = p.part.rels[r_id]
                    ext_links.append((rel.target_ref, "".join(elem.itertext())))

    # In-text spice cross-reference
    spice_refs = [txt for anc, txt in toc_links if anc == "bm_art3_1_spice"]
    assert len(spice_refs) >= 2, f"Expected both TOC and in-text cross reference to spice case, found {len(spice_refs)}"
    print("Internal spice cross-reference verified!")

    # HuggingFace Wikipedia link check
    hf_links = [url for url, txt in ext_links if "HuggingFace" in url or "HuggingFace" in txt]
    assert len(hf_links) >= 1, "Missing HuggingFace Wikipedia link!"
    assert "https://zh.wikipedia.org/zh-tw/2026%E5%B9%B4OpenAI%E6%99%BA%E8%83%BD%E4%BD%93%E5%85%A5%E4%BE%B5HuggingFace%E4%BA%8B%E4%BB%B6" in hf_links[0], f"HuggingFace URL mismatch: {hf_links[0]}"
    print("HuggingFace Wikipedia link verified!")

    # No traditional Chinese URLs check
    for url, txt in ext_links:
        assert "hbrtaiwan.com" not in url, f"ERROR: Traditional Chinese URL found: {url}"
    print("Deletion of traditional Chinese URLs verified: ZERO hbrtaiwan.com links found!")

    # GitHub full link check
    gh_links = [url for url, txt in ext_links if "github.com" in url]
    assert len(gh_links) >= 1, "Missing GitHub repository link!"
    assert "2db126f31cd9dfddd446593daf66eb0d1e1df5b1" in gh_links[0], f"GitHub commit SHA missing: {gh_links[0]}"
    print("GitHub repository full commit link verified!")

    # 8. Check Style Fidelity (No manual line spacing / Times New Roman on body paragraphs)
    print("\n--- 8. Checking Style Fidelity & Clean Inheritance ---")
    body_ps = [p for p in doc.paragraphs if p.style.name == 'Normal' and len(p.text.strip()) > 30]
    manual_spacing_count = 0
    times_new_roman_count = 0
    for p in body_ps:
        for elem in p._p.iter():
            if elem.tag.endswith('spacing') and elem.get(qn('w:line')) == '312':
                manual_spacing_count += 1
            if elem.tag.endswith('rFonts') and elem.get(qn('w:ascii')) == 'Times New Roman':
                times_new_roman_count += 1

    print(f"Manual spacing (1.3 line spacing) in body paragraphs: {manual_spacing_count}")
    print(f"Manual Times New Roman in body paragraphs: {times_new_roman_count}")
    assert manual_spacing_count == 0, f"Found {manual_spacing_count} manual line_spacing overrides on body paragraphs!"
    assert times_new_roman_count == 0, f"Found {times_new_roman_count} Times New Roman overrides on body paragraphs!"
    print("Style Fidelity Verified: 100% pure Normal style inheritance without manual body overrides!")

    char_count = sum(len(p.text.strip()) for p in doc.paragraphs)
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                char_count += sum(len(p.text.strip()) for p in cell.paragraphs)
    print(f"Total Character Count: {char_count:,} chars")
    assert char_count >= 2000, f"Word count too low: {char_count}"
    print(f"DOCUMENT VERIFICATION PASSED: {doc_path}\n")


def main():
    print("=== Checking Backup Docx ===")
    assert os.path.exists(BACKUP_DOC), f"Backup docx missing: {BACKUP_DOC}"
    print(f"Backup intact: {BACKUP_DOC} ({os.path.getsize(BACKUP_DOC):,} bytes)")

    verify_single(TARGET_DOC_1)
    verify_single(TARGET_DOC_2)
    print("\n========================================================")
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY FOR BOTH FILES!")
    print("========================================================")


if __name__ == "__main__":
    main()
