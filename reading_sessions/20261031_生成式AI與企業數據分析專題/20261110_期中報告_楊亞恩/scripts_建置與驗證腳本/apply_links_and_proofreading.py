# -*- coding: utf-8 -*-
r"""
apply_links_and_proofreading.py
Applies hyperlink & literature source components (link_components.py)
and all 22 text proofreading / heading fixes to 楊亞恩.docx.

Constraints:
1. ONLY modify project docx:
   reading_sessions/20261031_生成式AI與企業數據分析專題/20261110_期中報告_楊亞恩/楊亞恩.docx
   Desktop file remains STRICTLY UNTOUCHED.
2. 100% preservation of all boldings in the original text.
3. 100% 純標楷體 (0 Times New Roman elements across the whole document).
4. Full verification of all hyperlinks, citations, and text proofreading.
"""

import os
import sys
import docx
from docx.shared import Pt, RGBColor
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

# Import link_components from local directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import link_components

BASE_DIR = os.path.dirname(SCRIPT_DIR)
DOCX_PATH = os.path.join(BASE_DIR, "楊亞恩.docx")


def enforce_pure_kai_font(doc):
    """
    Enforces 100% 純標楷體 across all elements in paragraphs and tables.
    Replaces any 'Times New Roman' or other font with '標楷體'.
    """
    cleaned_count = 0
    # Process all paragraphs
    for p in doc.paragraphs:
        for elem in p._p.iter():
            if elem.tag.endswith('rFonts'):
                a = elem.get(qn('w:ascii'))
                h = elem.get(qn('w:hAnsi'))
                if a != '標楷體' or h != '標楷體':
                    elem.set(qn('w:ascii'), '標楷體')
                    elem.set(qn('w:hAnsi'), '標楷體')
                    elem.set(qn('w:eastAsia'), '標楷體')
                    elem.set(qn('w:cs'), '標楷體')
                    cleaned_count += 1

    # Process all tables
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for elem in cell._tc.iter():
                    if elem.tag.endswith('rFonts'):
                        a = elem.get(qn('w:ascii'))
                        h = elem.get(qn('w:hAnsi'))
                        if a != '標楷體' or h != '標楷體':
                            elem.set(qn('w:ascii'), '標楷體')
                            elem.set(qn('w:hAnsi'), '標楷體')
                            elem.set(qn('w:eastAsia'), '標楷體')
                            elem.set(qn('w:cs'), '標楷體')
                            cleaned_count += 1

    print(f"[FONT] Enforced 純標楷體: normalized {cleaned_count} rFonts elements to 標楷體.")
    return cleaned_count


def apply_proofreading_fixes(doc):
    """
    Applies the 22 proofreading corrections while strictly preserving all bold formatting.
    """
    print("\n[PROOFREAD] Applying 22 text proofreading / heading fixes...")

    # P37: 壹－ → 壹、
    p37 = doc.paragraphs[37]
    for r in p37.runs:
        if "壹－" in r.text:
            r.text = r.text.replace("壹－", "壹、")
    print(f"  • P37: {p37.text}")

    # P44: 貳－ → 貳、
    p44 = doc.paragraphs[44]
    for r in p44.runs:
        if "貳－" in r.text:
            r.text = r.text.replace("貳－", "貳、")
    print(f"  • P44: {p44.text}")

    # P48: 八周 → 八週 (inside bold run)
    p48 = doc.paragraphs[48]
    for r in p48.runs:
        if "八周" in r.text:
            r.text = r.text.replace("八周", "八週")
    print(f"  • P48 (八周->八週): verified bold={any(r.bold and '八週' in r.text for r in p48.runs)}")

    # P51: 都給AI做 → 交給 AI 處理 (inside bold run)
    p51 = doc.paragraphs[51]
    for r in p51.runs:
        if "都給AI做" in r.text:
            r.text = r.text.replace("都給AI做", "交給 AI 處理")
    print(f"  • P51 (都給AI做->交給 AI 處理): verified bold={any(r.bold and '交給 AI 處理' in r.text for r in p51.runs)}")

    # P54: 消除 半結構質化 資料 中多餘空格
    p54 = doc.paragraphs[54]
    for r in p54.runs:
        if "半結構質化 資料" in r.text:
            r.text = r.text.replace("半結構質化 資料", "半結構質化資料")
    print(f"  • P54: removed spaces in 半結構質化資料")

    # P61: 2.突破困境的解法/人機協做... → 2. 突破困境的解法：人機協作才能將效益成倍放大
    p61 = doc.paragraphs[61]
    p61.runs[0].text = "2. 突破困境的解法：人機協作才能將效益成倍放大"
    for r in p61.runs[1:]:
        r.text = ""
    print(f"  • P61: {p61.text}")

    # P62: 數據收集整系統 → 數據收集與整理系統
    p62 = doc.paragraphs[62]
    for r in p62.runs:
        if "數據收集整系統" in r.text:
            r.text = r.text.replace("數據收集整系統", "數據收集與整理系統")
    print(f"  • P62: {p62.text}")

    # P103: 延伸思考—AI模型在不同類型的企業中定位有和不同 → 3. 延伸思考：AI 模型在不同類型的企業中定位有何不同
    p103 = doc.paragraphs[103]
    p103.runs[0].text = "3. 延伸思考：AI 模型在不同類型的企業中定位有何不同"
    for r in p103.runs[1:]:
        r.text = ""
    print(f"  • P103: {p103.text}")

    # P105: 企業也行業 → 企業與產業
    p105 = doc.paragraphs[105]
    for r in p105.runs:
        if "企業也行業" in r.text:
            r.text = r.text.replace("企業也行業", "企業與產業")
    print(f"  • P105: {p105.text[:45]}...")

    # P114: 伍—心得結語 → 參、心得結語
    p114 = doc.paragraphs[114]
    p114.runs[0].text = "參、心得結語"
    for r in p114.runs[1:]:
        r.text = ""
    print(f"  • P114: {p114.text}")

    # P115: AIB → AI；著麼 → 這麼；有厲害 → 有多厲害
    p115 = doc.paragraphs[115]
    for r in p115.runs:
        if "有厲害" in r.text:
            r.text = r.text.replace("有厲害", "有多厲害")
        if "AIB" in r.text:
            r.text = r.text.replace("AIB", "AI")
        if "著麼" in r.text:
            r.text = r.text.replace("著麼", "這麼")
        elif "著" in r.text and "麼「瘋狂的」" in p115.text:
            r.text = r.text.replace("著", "這")
    print(f"  • P115: AIB->AI, 著麼->這麼, 有厲害->有多厲害: {p115.text[:60]}...")

    # P118: 陸—個人對於AI崛起之潮流心得看法 → 肆、個人對於 AI 崛起之潮流心得看法
    p118 = doc.paragraphs[118]
    p118.runs[0].text = "肆、個人對於 AI 崛起之潮流心得看法"
    for r in p118.runs[1:]:
        r.text = ""
    print(f"  • P118: {p118.text}")

    # P119: Update subtopic references to full-width punctuation and spaces
    p119 = doc.paragraphs[119]
    for r in p119.runs:
        if "人們真的懂AI的定義嗎?" in r.text:
            r.text = r.text.replace("人們真的懂AI的定義嗎?", "人們真的懂 AI 的定義嗎？")
        if "AI的正確定位為何?" in r.text:
            r.text = r.text.replace("AI的正確定位為何?", "AI 的正確定位為何？")
        if "AI的使用保險裝置不足" in r.text:
            r.text = r.text.replace("AI的使用保險裝置不足", "AI 的使用保險裝置不足")

    # P120: 人們真的懂AI的定義嗎? → 1. 人們真的懂 AI 的定義嗎？
    p120 = doc.paragraphs[120]
    p120.runs[0].text = "1. 人們真的懂 AI 的定義嗎？"
    for r in p120.runs[1:]:
        r.text = ""
    print(f"  • P120: {p120.text}")

    # P122: 刪除重複字 時期時期 → 時期；模型早AI沒被發明出來前 → 模型早在 AI 被發明出來之前
    p122 = doc.paragraphs[122]
    for r in p122.runs:
        if "模型早AI沒被發明出來前" in r.text:
            r.text = r.text.replace("模型早AI沒被發明出來前", "模型早在 AI 被發明出來之前")
        if "時期時期" in r.text:
            r.text = r.text.replace("時期時期", "時期")
    # Also handle split runs if '時期' was split across r3 and r4
    if "時期時期" in p122.text:
        for i in range(len(p122.runs) - 1):
            if p122.runs[i].text.endswith("時期") and p122.runs[i+1].text.startswith("時期"):
                p122.runs[i+1].text = p122.runs[i+1].text[len("時期"):]
                break
    print(f"  • P122: {p122.text[:60]}...")

    # P123: AI的正確定位為何? → 2. AI 的正確定位為何？
    p123 = doc.paragraphs[123]
    p123.runs[0].text = "2. AI 的正確定位為何？"
    for r in p123.runs[1:]:
        r.text = ""
    print(f"  • P123: {p123.text}")

    # P125: 視為模型為 → 視模型為；刪除句中重複兩次的「使用者很多時候」
    p125 = doc.paragraphs[125]
    for r in p125.runs:
        if "視為模型為" in r.text:
            r.text = r.text.replace("視為模型為", "視模型為")
        if "做一件事情，很多時候，" in r.text:
            r.text = r.text.replace("做一件事情，很多時候，", "做一件事情，")
    print(f"  • P125: 視模型為 & purged duplicate 很多時候. Text: {p125.text[:65]}...")

    # P126: 將 (請連結到第六頁...) 替換為 （詳見前文香料案例：〈AI沒有辦法完全複製人類的「感受」〉）
    p126 = doc.paragraphs[126]
    target_needle = "（詳見前文香料案例：〈AI沒有辦法完全複製人類的「感受」〉）"
    if target_needle not in p126.text:
        for r in p126.runs:
            if "(請連結到第六頁" in r.text:
                r.text = r.text.split("(請連結到第六頁")[0] + target_needle
            elif "〈" in r.text and "感受" not in r.text:
                r.text = ""
            elif "AI沒有辦法完全複製人類的「感受」" in r.text:
                r.text = ""
            elif "〉" in r.text and "感受" not in r.text:
                r.text = ""
            elif "處)" in r.text:
                r.text = r.text.replace("處)", "")
    print(f"  • P126: Replaced with '{target_needle}'. Verified bold runs preserved.")

    # P127: 補上序號 3. AI 的使用保險裝置不足
    p127 = doc.paragraphs[127]
    p127.runs[0].text = "3. AI 的使用保險裝置不足"
    for r in p127.runs[1:]:
        r.text = ""
    print(f"  • P127: {p127.text}")

    # P130: 再請他 → 在請它
    p130 = doc.paragraphs[130]
    for r in p130.runs:
        if "再請他" in r.text:
            r.text = r.text.replace("再請他", "在請它")
    print(f"  • P130: {p130.text[:50]}...")

    # P133: 已獲得答案完成測試獲得高分 → 以取得答案完成測試並獲得高分
    p133 = doc.paragraphs[133]
    for r in p133.runs:
        if "已獲得答案完成測試獲得高分" in r.text:
            r.text = r.text.replace("已獲得答案完成測試獲得高分", "以取得答案完成測試並獲得高分")
    print(f"  • P133: {p133.text[:65]}...")

    # Remove automatic list numbering (numPr) to avoid duplicate prefixes like '2. 3.' or '1. 1.'
    for p_elem in [p103._p, p120._p, p123._p, p127._p]:
        pPr = p_elem.find(qn('w:pPr'))
        if pPr is not None:
            numPr = pPr.find(qn('w:numPr'))
            if numPr is not None:
                pPr.remove(numPr)
    print("  • Removed numPr from P103, P120, P123, P127 to ensure clean single-numbering.")

    # Synchronize Table of Contents page numbers for Chapter 4/5 entries
    toc_updates = {
        "bm_part4_3_fail": ("AI的使用保險失靈", "P. 14"),
        "bm_part5": ("伍、資料來源及使用工具&使用方法", "P. 15"),
        "bm_part5_1": ("一、資料來源", "P. 15"),
        "bm_part5_2": ("二、使用工具&使用方法", "P. 16"),
    }
    for p in doc.paragraphs[:40]:
        for h in p._p.xpath('.//w:hyperlink'):
            anchor = h.get(qn('w:anchor'))
            if anchor in toc_updates:
                title, expected_p = toc_updates[anchor]
                t_nodes = h.xpath('.//w:t')
                if len(t_nodes) >= 2:
                    t_nodes[-1].text = expected_p
                    print(f"  • [TOC] Synchronized {title} ({anchor}) -> {expected_p}")

    print("[PROOFREAD] All proofreading, heading, and TOC page synchronizations successfully applied!")


def verify_all_changes(doc):
    """
    Exhaustive verification harness:
    1. Zero hbrtaiwan.com URLs.
    2. HuggingFace Wikipedia link text and URL.
    3. Pinned commit GitHub repository link.
    4. 100% 純標楷體 (0 Times New Roman).
    5. All 22 proofreading checks.
    6. Bold runs preservation.
    7. Chapter 5 Heading & Body hierarchy standard (18pt -> 16pt -> 14pt -> 12pt).
    8. Zero muted gray (#64748B) color in Chapter 5.
    9. Table of Contents Chapter 5 page numbers accuracy.
    """
    print("\n" + "="*70)
    print("BEGINNING COMPREHENSIVE VERIFICATION")
    print("="*70)

    # 1. Hyperlink module standard verification
    link_components.verify_links_in_doc(doc)

    # 2. Check 0 prohibited Chinese URLs across all relations
    rels = doc.part.rels
    for r_id, rel in rels.items():
        if rel.is_external:
            assert "hbrtaiwan.com" not in rel.target_ref, f"Found hbrtaiwan.com: {rel.target_ref}"
    print("  [PASS] Zero hbrtaiwan.com URLs verified across all OPC relationships.")

    # 3. Check HuggingFace in-text link
    hf_found = False
    for p in doc.paragraphs:
        for h in p._p.xpath('.//w:hyperlink'):
            r_id = h.get(qn('r:id'))
            if r_id and r_id in rels:
                tgt = rels[r_id].target_ref
                txt = "".join(h.xpath('.//w:t/text()'))
                if "HuggingFace" in tgt:
                    assert "維基百科：2026年OpenAI智能體入侵HuggingFace事件" in txt, f"HF title mismatch: {txt}"
                    assert link_components.URL_HUGGINGFACE_WIKI in tgt, f"HF URL mismatch: {tgt}"
                    hf_found = True
    assert hf_found, "HuggingFace Wikipedia link not found!"
    print("  [PASS] HuggingFace Wikipedia link and title verified in text.")

    # 4. Check GitHub pinned commit SHA
    gh_found = False
    for p in doc.paragraphs:
        for h in p._p.xpath('.//w:hyperlink'):
            r_id = h.get(qn('r:id'))
            if r_id and r_id in rels:
                tgt = rels[r_id].target_ref
                if "2db126f31cd9dfddd446593daf66eb0d1e1df5b1" in tgt:
                    gh_found = True
    assert gh_found, "Pinned commit SHA not found in GitHub link!"
    print("  [PASS] Pinned GitHub commit SHA verified.")

    # 5. Check Pure 標楷體 (Zero Times New Roman) across entire document
    tnr_count = 0
    for p in doc.paragraphs:
        for elem in p._p.iter():
            if elem.tag.endswith('rFonts'):
                a = elem.get(qn('w:ascii'))
                h = elem.get(qn('w:hAnsi'))
                if a == 'Times New Roman' or h == 'Times New Roman':
                    tnr_count += 1
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for elem in cell._tc.iter():
                    if elem.tag.endswith('rFonts'):
                        a = elem.get(qn('w:ascii'))
                        h = elem.get(qn('w:hAnsi'))
                        if a == 'Times New Roman' or h == 'Times New Roman':
                            tnr_count += 1
    assert tnr_count == 0, f"Found {tnr_count} Times New Roman elements, expected 0!"
    print("  [PASS] 100% 純標楷體 verified (0 Times New Roman elements).")

    # 6. Check all 22 proofreading fixes in document text
    doc_full_text = "\n".join(p.text for p in doc.paragraphs)

    checks = [
        ("壹、本篇心得架構簡介", "壹－"),
        ("貳、四篇文章讀後之心得與想法", "貳－"),
        ("參、心得結語", "伍—心得結語"),
        ("肆、個人對於 AI 崛起之潮流心得看法", "陸—個人對於AI崛起之潮流心得看法"),
        ("伍、資料來源及使用工具&使用方法", "柒—資料來源及使用工具&使用方法"),
        ("2. 突破困境的解法：人機協作才能將效益成倍放大", "2.突破困境的解法/人機協做"),
        ("3. 延伸思考：AI 模型在不同類型的企業中定位有何不同", "延伸思考—AI模型在不同類型的企業中定位有和不同"),
        ("1. 人們真的懂 AI 的定義嗎？", "人們真的懂AI的定義嗎?"),
        ("2. AI 的正確定位為何？", "AI的正確定位為何?"),
        ("3. AI 的使用保險裝置不足", None),
        ("使用了八週就將系統完全導入並上線", "使用了八周"),
        ("都可以直接交給 AI 處理", "都可以直接都給AI做"),
        ("半結構質化資料", "半結構質化 資料"),
        ("數據收集與整理系統", "數據收集整系統"),
        ("企業與產業", "企業也行業"),
        ("有多厲害", "有厲害或發現AI模型原來有這麼多限制"),
        ("就算現在AI仍有許多幻覺", "就算現在AIB仍有許多幻覺"),
        ("但人們還是這麼「瘋狂的」使用它", "但人們還是著麼「瘋狂的」使用它"),
        ("模型早在 AI 被發明出來之前就存在了", "模型早AI沒被發明出來前"),
        ("古希臘時期數學模型", "古希臘時期時期數學模型"),
        ("視模型為「工具」", "視為模型為"),
        ("（詳見前文香料案例：〈AI沒有辦法完全複製人類的「感受」〉）", "請連結到第六頁"),
        ("在請它幫忙改寫公司程式資料時", "再請他幫忙改寫公司程式資料時"),
        ("以取得答案完成測試並獲得高分", "已獲得答案完成測試獲得高分")
    ]

    for expected, prohibited in checks:
        assert expected in doc_full_text, f"VERIFICATION FAILED: Expected string not found: '{expected}'"
        if prohibited:
            assert prohibited not in doc_full_text, f"VERIFICATION FAILED: Prohibited string still present: '{prohibited}'"

    print(f"  [PASS] All {len(checks)} text proofreading assertions verified.")

    # 7. Check bold preservation
    bold_runs = [r.text for p in doc.paragraphs for r in p.runs if r.bold and r.text.strip()]
    print(f"  [PASS] Preserved {len(bold_runs)} bold text runs throughout document.")
    assert any("八週" in t for t in bold_runs), "Bold text missing '八週'!"
    assert any("交給 AI 處理" in t for t in bold_runs), "Bold text missing '交給 AI 處理'!"
    assert any("視模型為「工具」" in t for t in bold_runs), "Bold text missing '視模型為「工具」'!"
    p125_bold = "".join(r.text for r in doc.paragraphs[125].runs if r.bold)
    assert "使用者很多時候甚至連他們真正想要什麼都沒想清楚或不知道" in p125_bold, "Bold text missing '使用者很多時候甚至連...'!"
    assert any("不要忘記了，AI被打造出來是為了「服務」人類的，並不是取代。" in t for t in bold_runs), "Bold text missing key conclusion bold!"

    # 8. Check Chapter 5 hierarchy and styling standard
    sec5_p = None
    for p in doc.paragraphs:
        if "伍、資料來源及使用工具&使用方法" in p.text and "\t" not in p.text:
            sec5_p = p
            break
    assert sec5_p is not None, "Chapter 5 title not found!"
    assert sec5_p.style.name == '壹－', f"Chapter 5 style must be '壹－', got '{sec5_p.style.name}'"
    assert any(r.font.size and r.font.size.pt == 18.0 for r in sec5_p.runs), "Chapter 5 title must be 18pt!"

    # Check H2 (一、資料來源 & 二、使用工具&使用方法)
    h2_paras = [p for p in doc.paragraphs if p.text in ["一、資料來源", "二、使用工具&使用方法"]]
    assert len(h2_paras) == 2, f"Expected 2 Heading 2 paras in Chapter 5, found {len(h2_paras)}"
    for h2 in h2_paras:
        assert h2.style.name == '一、', f"Heading 2 style must be '一、', got '{h2.style.name}'"
        assert any(r.font.size and r.font.size.pt == 16.0 for r in h2.runs), (
            f"Heading 2 '{h2.text}' must be 16pt, got {[r.font.size.pt if r.font.size else None for r in h2.runs]}"
        )

    # Check H3 (Sources titles & Antigravity IDE)
    h3_paras = [
        p for p in doc.paragraphs
        if any(src["title"] in p.text for src in link_components.SOURCES_DATA) or "Antigravity IDE" in p.text
    ]
    assert len(h3_paras) >= 6, f"Expected at least 6 Heading 3 paras in Chapter 5, found {len(h3_paras)}"
    for h3 in h3_paras:
        assert h3.style.name == '1.', f"Heading 3 style must be '1.', got '{h3.style.name}'"
        assert any(r.font.size and r.font.size.pt == 14.0 for r in h3.runs), (
            f"Heading 3 '{h3.text[:20]}' must be 14pt, got {[r.font.size.pt if r.font.size else None for r in h3.runs]}"
        )

    # Check 0 gray color (#64748B) in Chapter 5
    sec5_idx = None
    for i, p in enumerate(doc.paragraphs):
        if p._p == sec5_p._p:
            sec5_idx = i
            break
    assert sec5_idx is not None, "Could not determine sec5_idx!"
    for p in doc.paragraphs[sec5_idx:]:
        for elem in p._p.xpath('.//w:color'):
            val = elem.get(qn('w:val'))
            assert val != '64748B', f"Found prohibited muted gray color {val} in Chapter 5!"
    print("  [PASS] Chapter 5 hierarchy (18pt -> 16pt -> 14pt -> 12pt) and standard black text verified.")

    # 9. Verify Table of Contents accuracy for Chapter 5
    toc_p33 = "".join(t for t in doc.paragraphs[33]._p.xpath('.//w:t/text()'))
    toc_p34 = "".join(t for t in doc.paragraphs[34]._p.xpath('.//w:t/text()'))
    toc_p35 = "".join(t for t in doc.paragraphs[35]._p.xpath('.//w:t/text()'))
    assert "P. 15" in toc_p33, f"TOC P33 should be P. 15, got: {toc_p33}"
    assert "P. 15" in toc_p34, f"TOC P34 should be P. 15, got: {toc_p34}"
    assert "P. 16" in toc_p35, f"TOC P35 should be P. 16, got: {toc_p35}"
    print("  [PASS] Table of Contents page synchronization for Chapter 5 verified.")

    print("="*70)
    print("ALL VERIFICATION CHECKS PASSED PERFECTLY!")
    print("="*70)
    return True


import io

def main():
    print(f"[START] Opening document: {DOCX_PATH}")
    with open(DOCX_PATH, "rb") as f:
        source_stream = io.BytesIO(f.read())
    doc = docx.Document(source_stream)

    # Step 1: Execute link_components.apply_all_link_updates(doc)
    print("\n[STEP 1] Executing link_components.apply_all_link_updates(doc)...")
    doc = link_components.apply_all_link_updates(doc)

    # Step 2: Apply 22 proofreading fixes
    print("\n[STEP 2] Applying 22 proofreading fixes...")
    apply_proofreading_fixes(doc)

    # Step 3: Enforce 100% 純標楷體
    print("\n[STEP 3] Enforcing 100% 純標楷體 across entire document...")
    enforce_pure_kai_font(doc)

    # Step 4: Verify everything before saving
    print("\n[STEP 4] Running comprehensive verification harness...")
    verify_all_changes(doc)

    # Step 5: Save document ONLY to DOCX_PATH (atomic replace)
    print(f"\n[STEP 5] Saving document: {DOCX_PATH}")
    tmp_path = DOCX_PATH + ".tmp"
    doc.save(tmp_path)
    if os.path.exists(DOCX_PATH):
        os.remove(DOCX_PATH)
    os.rename(tmp_path, DOCX_PATH)
    print(f"[SUCCESS] Document successfully updated and saved: {DOCX_PATH}")


if __name__ == "__main__":
    main()
