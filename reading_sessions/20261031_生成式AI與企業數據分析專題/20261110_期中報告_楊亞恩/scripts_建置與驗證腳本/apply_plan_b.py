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
    p71 = doc.paragraphs[71]
    assert "《生成式 AI 正在顛覆市場研究》" in p71.text, f"P71 text unexpected: {p71.text}"
    for t in p71.runs[0]._r.xpath(".//w:t"):
        if t.text == "二、":
            t.text = "三、"
    print("Fix 1 complete: Heading Article 3 updated to 三、")

    # 2. Fix subheading typo: 3.AI改如何被應用在分析上 -> 3. AI 該如何被應用在分析上
    p87 = doc.paragraphs[87]
    assert "改如何被應用" in p87.text, f"P87 text unexpected: {p87.text}"
    for t in p87.runs[0]._r.xpath(".//w:t"):
        if "3.AI改如何被應用在分析上" in t.text:
            t.text = "3. AI 該如何被應用在分析上"
    print("Fix 2 complete: Subheading typo 改 -> 該 fixed")

    # 3. Fix broken sentence in Section 4: ...再宣布。是提早釋出... -> ...再宣布。若是提早釋出...
    p105 = doc.paragraphs[105]
    assert "再宣布。是提早釋出" in p105.text, f"P105 text unexpected: {p105.text}"
    for t in p105.runs[2]._r.xpath(".//w:t"):
        if t.text == "。是":
            t.text = "。若是"
    print("Fix 3 complete: Broken sentence conditional conjunction 若是 added")

    # 4. Fix contradiction in Section 1: 規避遵守其劣勢和限制 -> 規避其劣勢並遵守其限制
    p39 = doc.paragraphs[39]
    assert "規避遵守其劣勢和限制" in p39.text, f"P39 text unexpected: {p39.text}"
    for t in p39.runs[9]._r.xpath(".//w:t"):
        if "規避遵守其劣勢和限制" in t.text:
            t.text = t.text.replace("規避遵守其劣勢和限制", "規避其劣勢並遵守其限制")
    print("Fix 4 complete: Contradiction resolved to 規避其劣勢並遵守其限制")

    # 5. Fix reflection: 讀完這五篇文章 -> 讀完這四篇文章 and 原因是。 -> 原因是：
    p123 = doc.paragraphs[123]
    assert "讀完這五篇文章" in p123.text, f"P123 text unexpected: {p123.text}"
    assert "原因是。" in p123.text, f"P123 text unexpected: {p123.text}"
    for t in p123.runs[0]._r.xpath(".//w:t"):
        if "讀完這五篇文章" in t.text:
            t.text = t.text.replace("讀完這五篇文章", "讀完這四篇文章")
    for t in p123.runs[4]._r.xpath(".//w:t"):
        if "原因是。" in t.text:
            t.text = t.text.replace("原因是。", "原因是：")
    print("Fix 5 complete: Reflection article count (四) and colon fixed")

    # 6. Fix figure reference: 可以從上表看出 -> 可以從上圖看出
    p101 = doc.paragraphs[101]
    assert "可以從上表看出" in p101.text, f"P101 text unexpected: {p101.text}"
    for t in p101.runs[0]._r.xpath(".//w:t"):
        if "可以從上表看出" in t.text:
            t.text = t.text.replace("可以從上表看出", "可以從上圖看出")
    print("Fix 6 complete: Figure reference 上表 -> 上圖 fixed")

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
        elif p.text.strip() == "《生成式 AI 正在顛覆市場研究》":
            num_pr = p._p.pPr.find(qn("w:numPr"))
            if num_pr is not None:
                p._p.pPr.remove(num_pr)
            first_t = p.runs[0]._r.find(qn("w:t"))
            first_t.text = "3." + first_t.text
            print("Fix 7 (3.) complete: Added 3. prefix to reference 3")

    # Merge author and year paragraphs in Chapter 5
    pairs_to_merge = [
        ("Thomas H. Davenport & Priyanka Tiwari ｜", "年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 3–4 月號）"),
        ("Jeremy Korst、Stefano Puntoni、Olivier Toubia ｜", "年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 7–8 月號）"),
        ("Vikas Mittal、Alessandro Piazza、Sonam Singh、Ashwin Malshe ｜", "年份：2024 年（《哈佛商業評論》全球繁體中文版 2024 年 9–10 月號）"),
    ]

    for author_sub, year_sub in pairs_to_merge:
        found = False
        for i in range(ch5_idx, len(doc.paragraphs) - 1):
            p_auth = doc.paragraphs[i]
            p_yr = doc.paragraphs[i + 1]
            if author_sub in p_auth.text and year_sub in p_yr.text:
                for r in list(p_yr._p.xpath("./w:r")):
                    p_auth._p.append(r)
                p_yr._p.getparent().remove(p_yr._p)
                print(f"Fix 7 (merge) complete: Merged author and year for {author_sub[:30]}...")
                found = True
                break
        assert found, f"Could not find pair: {author_sub}"

    doc.save(docx_path)
    print(f"Successfully saved updated document to: {docx_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = os.path.join(base_dir, "楊亞恩.docx")
    apply_plan_b(target)
