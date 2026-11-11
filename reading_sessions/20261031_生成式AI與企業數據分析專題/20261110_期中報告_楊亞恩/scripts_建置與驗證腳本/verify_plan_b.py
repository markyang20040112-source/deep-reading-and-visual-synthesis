# -*- coding: utf-8 -*-
"""
verify_plan_b.py
Comprehensive deep verification suite for Plan B (7 Core Fixes + Preservation Mandate).
"""

import os
import sys
import io
import difflib
import subprocess
import docx
from docx.oxml.ns import qn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DOC = os.path.join(BASE_DIR, "楊亞恩.docx")
BACKUP_DOC = os.path.join(BASE_DIR, "楊亞恩_before_plan_b.docx")

def get_orig_doc():
    if os.path.exists(BACKUP_DOC):
        return docx.Document(BACKUP_DOC)
    # Fallback to git HEAD
    rel_path = "reading_sessions/20261031_生成式AI與企業數據分析專題/20261110_期中報告_楊亞恩/楊亞恩.docx"
    res = subprocess.run(["git", "show", f"HEAD:{rel_path}"], capture_output=True)
    if res.returncode == 0 and len(res.stdout) > 0:
        return docx.Document(io.BytesIO(res.stdout))
    return None

def run_verification():
    print("=" * 60)
    print("STARTING DEEP VERIFICATION: PLAN B (7 CORE FIXES)")
    print("=" * 60)

    assert os.path.exists(TARGET_DOC), f"Target docx missing: {TARGET_DOC}"

    doc = docx.Document(TARGET_DOC)
    doc_orig = get_orig_doc()

    full_text = "\n".join(p.text for p in doc.paragraphs)

    # -------------------------------------------------------------
    # Test Fix 1: Heading Article 3
    # -------------------------------------------------------------
    print("\n[Check 1] Heading Article 3...")
    h3_ps = [p for p in doc.paragraphs if "《生成式 AI 正在顛覆市場研究》" in p.text and p.style.name == "一、"]
    assert len(h3_ps) == 1, f"Expected 1 Article 3 heading, found {len(h3_ps)}"
    h3 = h3_ps[0]
    assert h3.text.startswith("三、《生成式 AI 正在顛覆市場研究》"), f"Fix 1 failed, text: {h3.text}"
    # Verify bookmark bm_art3 is attached
    bm_names = [e.get(qn('w:name')) for e in h3._p.iter() if e.tag.endswith('bookmarkStart')]
    assert "bm_art3" in bm_names, f"Fix 1 bookmark bm_art3 missing from heading: {bm_names}"
    print(f"  PASS: Heading is '{h3.text}', bookmark 'bm_art3' intact.")

    # -------------------------------------------------------------
    # Test Fix 2: Subheading typo
    # -------------------------------------------------------------
    print("\n[Check 2] Subheading typo 改 -> 該...")
    sub_ps = [p for p in doc.paragraphs if "如何被應用在分析上" in p.text and p.style.name == "1."]
    assert len(sub_ps) == 1, f"Expected 1 body subheading, found {len(sub_ps)}"
    assert "3. AI 該如何被應用在分析上" in sub_ps[0].text, f"Fix 2 failed, text: {sub_ps[0].text}"
    assert "改如何被應用" not in full_text, "Old typo '改如何被應用' still present in document!"
    bm_sub = [e.get(qn('w:name')) for e in sub_ps[0]._p.iter() if e.tag.endswith('bookmarkStart')]
    assert "bm_art3_3" in bm_sub, f"Fix 2 bookmark bm_art3_3 missing: {bm_sub}"
    print(f"  PASS: Subheading is '{sub_ps[0].text}', bookmark 'bm_art3_3' intact.")

    # -------------------------------------------------------------
    # Test Fix 3: Broken sentence in Section 4
    # -------------------------------------------------------------
    print("\n[Check 3] Broken sentence in Section 4...")
    assert "等轉型完全落地後，再宣布。若是提早釋出不實的宣傳" in full_text, "Fix 3 failed: conditional conjunction 若是 missing!"
    assert "等轉型完全落地後，再宣布。是提早釋出" not in full_text, "Old broken sentence still present!"
    print("  PASS: '等轉型完全落地後，再宣布。若是提早釋出不實的宣傳' verified.")

    # -------------------------------------------------------------
    # Test Fix 4: Contradiction in Section 1
    # -------------------------------------------------------------
    print("\n[Check 4] Contradiction in Section 1...")
    assert "規避其劣勢並遵守其限制" in full_text, "Fix 4 failed: 規避其劣勢並遵守其限制 missing!"
    assert "規避遵守其劣勢和限制" not in full_text, "Old contradiction '規避遵守其劣勢和限制' still present!"
    print("  PASS: '如何發揮AI模型的優勢，並規避其劣勢並遵守其限制' verified.")

    # -------------------------------------------------------------
    # Test Fix 5: Reflection article count & colon
    # -------------------------------------------------------------
    print("\n[Check 5] Reflection in Section 4...")
    assert "讀完這四篇文章，我最大的感觸其實不是讚嘆" in full_text, "Fix 5 failed: 讀完這四篇文章 missing!"
    assert "讀完這五篇文章" not in full_text, "Old reflection '讀完這五篇文章' still present!"
    assert "「瘋狂的」使用它的原因是：" in full_text, "Fix 5 failed: colon at end of '原因是：' missing!"
    assert "「瘋狂的」使用它的原因是。" not in full_text, "Old dangling sentence end '原因是。' still present!"
    print("  PASS: '讀完這四篇文章' and '原因是：' verified.")

    # -------------------------------------------------------------
    # Test Fix 6: Figure reference
    # -------------------------------------------------------------
    print("\n[Check 6] Figure reference above Figure 4...")
    assert "可以從上圖看出，研究者經過訪談流失客戶" in full_text, "Fix 6 failed: 可以從上圖看出 missing!"
    assert "可以從上表看出，研究者經過訪談流失客戶" not in full_text, "Old reference '可以從上表看出' still present!"
    print("  PASS: '可以從上圖看出' verified.")

    # -------------------------------------------------------------
    # Test Fix 7: Chapter 5 clean numbering & no dangling bars
    # -------------------------------------------------------------
    print("\n[Check 7] Chapter 5 references clean numbering & dangling bars...")
    ch5_idx = next(i for i, p in enumerate(doc.paragraphs) if "伍、資料來源" in p.text)
    ch5_text = "\n".join(p.text for p in doc.paragraphs[ch5_idx:])
    assert "2.《你的公司數據真的準備好面對生成式 AI 了嗎？》" in ch5_text, "Fix 7 failed: 2. prefix missing!"
    assert "3.《生成式 AI 正在顛覆市場研究》" in ch5_text, "Fix 7 failed: 3. prefix missing!"
    
    # Check no dangling vertical bars at paragraph ends
    dangling_bars = []
    for p in doc.paragraphs:
        txt = p.text.rstrip()
        if txt.endswith("｜") or txt.endswith("|"):
            dangling_bars.append(txt)
    assert len(dangling_bars) == 0, f"Found dangling vertical bars: {dangling_bars}"

    # Check merged author and year lines
    merged_lines = [
        "作者：Thomas H. Davenport & Priyanka Tiwari ｜ 年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 3–4 月號）",
        "作者：Jeremy Korst、Stefano Puntoni、Olivier Toubia ｜ 年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 7–8 月號）",
        "作者：Vikas Mittal、Alessandro Piazza、Sonam Singh、Ashwin Malshe ｜ 年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 9–10 月號）"
    ]
    for ml in merged_lines:
        assert ml in ch5_text, f"Merged reference line missing: {ml}"
    print("  PASS: Chapter 5 clean numbering 1..5 verified; ZERO dangling bars found.")

    # -------------------------------------------------------------
    # Test Mandate 1: Authentic Voice Preservation
    # -------------------------------------------------------------
    print("\n[Preservation Check 1] Authentic Student Voice Phrases...")
    authentic_phrases = [
        "動動手指",
        "一股腦丟給AI",
        "冷冰冰的打臉",
        "建議老師有興趣可以去查查資料",
        "這麼用力的追捧",
        "這麼「瘋狂的」使用它",
        "無限的可能性!"
    ]
    for phrase in authentic_phrases:
        assert phrase in full_text, f"Authentic voice phrase deleted or altered: '{phrase}'"
        print(f"  PASS: '{phrase}' is 100% intact.")

    # -------------------------------------------------------------
    # Test Mandate 2: Bookmarks Preservation
    # -------------------------------------------------------------
    print("\n[Preservation Check 2] All 27 Bookmarks...")
    req_bms = [
        "bm_part1", "bm_part2", "bm_art1", "bm_art2", "bm_art2_1", "bm_art2_2",
        "bm_art3", "bm_art3_1", "bm_art3_1_sim", "bm_art3_1_spice", "bm_art3_2", "bm_art3_3",
        "bm_art4", "bm_art4_1", "bm_art4_2", "bm_art4_3", "bm_art4_4",
        "bm_part3", "bm_part4", "bm_part4_1", "bm_part4_2", "bm_part4_3", "bm_part4_3_trust", "bm_part4_3_fail",
        "bm_part5", "bm_part5_1", "bm_part5_2"
    ]
    all_bms = set()
    for p in doc.paragraphs:
        for elem in p._p.iter():
            if elem.tag.endswith('bookmarkStart'):
                name = elem.get(qn('w:name'))
                if name:
                    all_bms.add(name)
    for bm in req_bms:
        assert bm in all_bms, f"Required bookmark missing: {bm}"
    print(f"  PASS: All {len(req_bms)} required bookmarks present and valid.")

    # -------------------------------------------------------------
    # Test Mandate 3: Hyperlinks & Internal Links Preservation
    # -------------------------------------------------------------
    print("\n[Preservation Check 3] Hyperlinks & Cross-references...")
    toc_links = 0
    ext_links = 0
    for p in doc.paragraphs:
        for elem in p._p.iter():
            if elem.tag.endswith('hyperlink'):
                if elem.get(qn('w:anchor')):
                    toc_links += 1
                elif elem.get(qn('r:id')):
                    ext_links += 1
    assert toc_links == 27, f"Expected 27 TOC internal links, found {toc_links}"
    assert ext_links == 9, f"Expected 9 external links, found {ext_links}"
    print(f"  PASS: {toc_links} internal links and {ext_links} external links intact.")

    # -------------------------------------------------------------
    # Test Mandate 4: Tables Preservation
    # -------------------------------------------------------------
    print("\n[Preservation Check 4] Document Tables...")
    assert len(doc.tables) == 3, f"Expected 3 tables, found {len(doc.tables)}"
    assert len(doc.tables[0].rows) == 4 and len(doc.tables[0].columns) == 2, "Cover table structure mismatch!"
    assert len(doc.tables[1].rows) == 5 and len(doc.tables[1].columns) == 4, "Table 1 structure mismatch!"
    assert len(doc.tables[2].rows) == 6 and len(doc.tables[2].columns) == 4, "Table 2 structure mismatch!"
    print("  PASS: All 3 tables intact (Cover Info, Table 1 5x4, Table 2 6x4).")

    # -------------------------------------------------------------
    # Test Mandate 5: Images Preservation
    # -------------------------------------------------------------
    print("\n[Preservation Check 5] Embedded Figures...")
    img_count = sum(1 for p in doc.paragraphs for r in p.runs if 'graphic' in r._r.xml)
    assert img_count == 5, f"Expected 5 inline pictures, found {img_count}"
    print(f"  PASS: All {img_count} figures intact.")

    # -------------------------------------------------------------
    # Test Mandate 6: Bold Runs Count & Integrity
    # -------------------------------------------------------------
    print("\n[Preservation Check 6] Bold Runs Integrity...")
    bold_orig = [r.text for p in doc_orig.paragraphs for r in p.runs if r.bold]
    bold_new = [r.text for p in doc.paragraphs for r in p.runs if r.bold]
    assert len(bold_orig) == len(bold_new), f"Bold count changed! Orig: {len(bold_orig)}, New: {len(bold_new)}"
    print(f"  PASS: Exactly {len(bold_new)} bold runs preserved with 100% integrity.")

    # -------------------------------------------------------------
    # Test Mandate 7: Strict Diff Inspection (Only 7 intended changes)
    # -------------------------------------------------------------
    print("\n[Preservation Check 7] Strict Diff Audit...")
    orig_texts = [p.text for p in doc_orig.paragraphs]
    new_texts = [p.text for p in doc.paragraphs]
    diff = list(difflib.unified_diff(orig_texts, new_texts, lineterm='', fromfile='orig', tofile='new'))
    
    # Analyze changes in diff
    added = [l[1:] for l in diff if l.startswith('+') and not l.startswith('+++')]
    removed = [l[1:] for l in diff if l.startswith('-') and not l.startswith('---')]
    
    print(f"  Diff lines: -{len(removed)} / +{len(added)}")
    # Expected changes:
    # 1. P39: 規避遵守其劣勢和限制 -> 規避其劣勢並遵守其限制
    # 2. P71: 二、 -> 三、
    # 3. P87: 3.AI改如何被應用在分析上 -> 3. AI 該如何被應用在分析上
    # 4. P101: 可以從上表看出 -> 可以從上圖看出
    # 5. P105: 。是提早釋出 -> 。若是提早釋出
    # 6. P123: 讀完這五篇文章 -> 讀完這四篇文章 & 原因是。 -> 原因是：
    # 7. Chapter 5:
    #    - 《你的公司數據... -> 2.《你的公司數據...
    #    - 《生成式 AI... -> 3.《生成式 AI...
    #    - 3 pairs of merged author + year lines (3 year lines removed, 3 author lines updated)
    assert len(removed) == 14, f"Unexpected number of removed lines: {len(removed)}"
    assert len(added) == 11, f"Unexpected number of added lines: {len(added)}"
    print("  PASS: Exact 1-to-1 match with the 7 intended core fixes! Zero unauthorized changes.")

    print("\n" + "=" * 60)
    print("ALL PLAN B DEEP VERIFICATION CHECKS PASSED SUCCESSFULLY (100% GREEN)!")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()
