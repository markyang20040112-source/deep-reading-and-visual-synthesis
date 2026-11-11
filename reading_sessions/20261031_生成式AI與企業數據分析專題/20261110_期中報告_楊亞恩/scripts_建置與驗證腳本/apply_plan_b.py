# -*- coding: utf-8 -*-
"""
apply_plan_b.py
Implements Plan B: Minimal Intervention / 7 Core Fixes Only.
Strictly preserves the author's authentic voice, bold runs, bookmarks, hyperlinks, tables, and styles.

7 Core Fixes:
1. Heading: 二、《生成式 AI 正在顛覆市場研究》 -> 三、《生成式 AI 正在顛覆市場研究》 (preserve bm_art3 bookmark).
2. Subheading typo: 3.AI改如何被應用在分析上 -> 3. AI 該如何被應用在分析上 (改 -> 該).
3. Broken sentence in Section 4: ...再宣布。是提早釋出不實的宣傳... -> ...再宣布。若是提早釋出不實的宣傳...
4. Contradiction in Section 1: 規避遵守其劣勢和限制 -> 規避其劣勢並遵守其限制
5. Reflection in Section 4: 讀完這五篇文章 -> 讀完這四篇文章; ...使用它的原因是。 -> ...使用它的原因是：
6. Figure reference in Section 4: 可以從上表看出 -> 可以從上圖看出
7. Chapter 5 clean numbering 2. and 3. without dangling vertical bars ｜ .
"""

import os
import sys
import docx
from docx.oxml.ns import qn

def apply_plan_b(docx_path):
    print(f"Applying Plan B to: {docx_path}")
    doc = docx.Document(docx_path)

    # 1. Fix heading: 二、《生成式 AI 正在顛覆市場研究》 -> 三、《生成式 AI 正在顛覆市場研究》
    found_h3 = False
    for p in doc.paragraphs:
        if "《生成式 AI 正在顛覆市場研究》" in p.text and p.style.name == "一、":
            found_h3 = True
            if p.text.startswith("三、"):
                print("Fix 1 already applied: Heading Article 3 is already '三、'")
            else:
                for t in p.runs[0]._r.xpath(".//w:t"):
                    if t.text == "二、":
                        t.text = "三、"
                print("Fix 1 complete: Heading Article 3 updated to 三、")
            break
    assert found_h3, "Article 3 heading not found!"

    # 2. Fix subheading typo: 3.AI改如何被應用在分析上 -> 3. AI 該如何被應用在分析上
    found_sub = False
    for p in doc.paragraphs:
        if "如何被應用在分析上" in p.text and p.style.name == "1.":
            found_sub = True
            if "3. AI 該如何被應用在分析上" in p.text:
                print("Fix 2 already applied: Subheading is already '3. AI 該如何被應用在分析上'")
            else:
                for r in p.runs:
                    for t in r._r.xpath(".//w:t"):
                        if "3.AI改如何被應用在分析上" in t.text or "3. AI 改如何被應用在分析上" in t.text:
                            t.text = "3. AI 該如何被應用在分析上"
                        elif "改如何被應用" in t.text:
                            t.text = t.text.replace("改如何被應用", "該如何被應用")
                print("Fix 2 complete: Subheading typo 改 -> 該 fixed")
            break
    assert found_sub, "Article 3 subheading not found!"

    # 3. Fix broken sentence in Section 4: ...再宣布。是提早釋出... -> ...再宣布。若是提早釋出...
    found_s4 = False
    for p in doc.paragraphs:
        if "必須要等轉型完全落地後，再宣布" in p.text:
            found_s4 = True
            if "。若是提早釋出" in p.text:
                print("Fix 3 already applied: Sentence already contains '。若是提早釋出'")
            elif "。是提早釋出" in p.text:
                for r in p.runs:
                    for t in r._r.xpath(".//w:t"):
                        if t.text == "。是":
                            t.text = "。若是"
                        elif "。是提早釋出" in t.text:
                            t.text = t.text.replace("。是提早釋出", "。若是提早釋出")
                print("Fix 3 complete: Broken sentence conditional conjunction 若是 added")
            break
    assert found_s4, "Section 4 broken sentence paragraph not found!"

    # 4. Fix contradiction in Section 1: 規避遵守其劣勢和限制 -> 規避其劣勢並遵守其限制
    found_s1 = False
    for p in doc.paragraphs:
        if "商業分析的下一部分－資料解釋與分析" in p.text and "限制" in p.text:
            found_s1 = True
            if "規避其劣勢並遵守其限制" in p.text:
                print("Fix 4 already applied: Contradiction already resolved to 規避其劣勢並遵守其限制")
            elif "規避遵守其劣勢和限制" in p.text:
                for r in p.runs:
                    for t in r._r.xpath(".//w:t"):
                        if "規避遵守其劣勢和限制" in t.text:
                            t.text = t.text.replace("規避遵守其劣勢和限制", "規避其劣勢並遵守其限制")
                print("Fix 4 complete: Contradiction resolved to 規避其劣勢並遵守其限制")
            break
    assert found_s1, "Section 1 contradiction paragraph not found!"

    # 5. Fix reflection: 讀完這五篇文章 -> 讀完這四篇文章 and 原因是。 -> 原因是：
    found_refl = False
    for p in doc.paragraphs:
        if "我最大的感觸其實不是讚嘆" in p.text:
            found_refl = True
            if "讀完這四篇文章" in p.text and "原因是：" in p.text:
                print("Fix 5 already applied: Reflection article count (四) and colon already fixed")
            else:
                for r in p.runs:
                    for t in r._r.xpath(".//w:t"):
                        if "讀完這五篇文章" in t.text:
                            t.text = t.text.replace("讀完這五篇文章", "讀完這四篇文章")
                        if "原因是。" in t.text:
                            t.text = t.text.replace("原因是。", "原因是：")
                print("Fix 5 complete: Reflection article count (四) and colon fixed")
            break
    assert found_refl, "Reflection paragraph not found!"

    # 6. Fix figure reference: 可以從上表看出 -> 可以從上圖看出
    found_fig = False
    for p in doc.paragraphs:
        if "研究者經過訪談流失客戶以及分析成功轉型案例" in p.text:
            found_fig = True
            if "可以從上圖看出" in p.text:
                print("Fix 6 already applied: Figure reference already 上圖")
            elif "可以從上表看出" in p.text:
                for r in p.runs:
                    for t in r._r.xpath(".//w:t"):
                        if "可以從上表看出" in t.text:
                            t.text = t.text.replace("可以從上表看出", "可以從上圖看出")
                print("Fix 6 complete: Figure reference 上表 -> 上圖 fixed")
            break
    assert found_fig, "Figure reference paragraph not found!"

    # 7. Chapter 5 clean numbering 2. and 3. without dangling vertical bars
    ch5_idx = None
    for i, p in enumerate(doc.paragraphs):
        if "伍、資料來源及使用工具&使用方法" in p.text:
            ch5_idx = i
            break
    assert ch5_idx is not None, "Chapter 5 heading not found!"

    # Fix numbering 2. and 3.
    for p in doc.paragraphs[ch5_idx:]:
        if p.text.strip() == "《你的公司數據真的準備好面對生成式 AI 了嗎？》":
            num_pr = p._p.pPr.find(qn("w:numPr"))
            if num_pr is not None:
                p._p.pPr.remove(num_pr)
            first_t = p.runs[0]._r.find(qn("w:t"))
            first_t.text = "2." + first_t.text
            print("Fix 7 (2.) complete: Added 2. prefix to reference 2")
        elif p.text.strip().startswith("2.《你的公司數據真的準備好面對生成式 AI 了嗎？》"):
            print("Fix 7 (2.) already applied: Reference 2 already numbered 2.")
        elif p.text.strip() == "《生成式 AI 正在顛覆市場研究》":
            num_pr = p._p.pPr.find(qn("w:numPr"))
            if num_pr is not None:
                p._p.pPr.remove(num_pr)
            first_t = p.runs[0]._r.find(qn("w:t"))
            first_t.text = "3." + first_t.text
            print("Fix 7 (3.) complete: Added 3. prefix to reference 3")
        elif p.text.strip().startswith("3.《生成式 AI 正在顛覆市場研究》"):
            print("Fix 7 (3.) already applied: Reference 3 already numbered 3.")

    # Merge author and year paragraphs in Chapter 5 if split
    pairs_to_merge = [
        ("Thomas H. Davenport & Priyanka Tiwari ｜", "年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 3–4 月號）"),
        ("Jeremy Korst、Stefano Puntoni、Olivier Toubia ｜", "年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 7–8 月號）"),
        ("Vikas Mittal、Alessandro Piazza、Sonam Singh、Ashwin Malshe ｜", "年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 9–10 月號）"),
    ]

    for author_sub, year_sub in pairs_to_merge:
        for i in range(ch5_idx, len(doc.paragraphs) - 1):
            p_auth = doc.paragraphs[i]
            p_yr = doc.paragraphs[i + 1]
            if author_sub in p_auth.text and year_sub in p_yr.text:
                for r in list(p_yr._p.xpath("./w:r")):
                    p_auth._p.append(r)
                p_yr._p.getparent().remove(p_yr._p)
                print(f"Fix 7 (merge) complete: Merged author and year for {author_sub[:30]}...")
                break
        else:
            already_merged = any((author_sub in p.text and year_sub in p.text) for p in doc.paragraphs[ch5_idx:])
            if already_merged:
                print(f"Fix 7 (merge) already applied: {author_sub[:30]}... already merged")

    doc.save(docx_path)
    print(f"Successfully saved updated document to: {docx_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = os.path.join(base_dir, "楊亞恩.docx")
    apply_plan_b(target)
