# -*- coding: utf-8 -*-
"""
build_pdf_report.py
Renders the publication-grade PDF report (Format B) following the upgraded document_report_spec.md:
1. W3C CSS Fragmentation Level 3: Continuous flow layout from Page 1 to the end (zero awkward bottom-of-page
   whitespace gaps on Page 1 or any other page, and headings never detach from their content).
2. ISO 9241 Visual Acuity Compliance: ZERO shrunk/unreadable mindmap .jpg images embedded in the PDF!
   All structural diagrams inside the PDF are rendered as Native Large-Font HTML/CSS Schematics (>= 9.5pt-10.5pt)
   that are 100% legible without zooming.
3. Müller-Brockmann Parallel Row Alignment & W3C CLREQ Bullet Ergonomics: Side-by-side bullet points use true
   table-row baseline locking so Bullet 1, Bullet 2, Bullet 3 across columns are 100% horizontally parallel!
4. Kahneman Peak-End Rule Closing Section: Dedicated final summary, 3-step action checklist, and colophon seal.
"""

import os
import subprocess

OUT_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI顛覆市場研究\02_outputs"
HTML_PATH = os.path.join(OUT_DIR, "_temp_report.html")
PDF_PATH = os.path.join(OUT_DIR, "生成式AI顛覆市場研究_深度閱讀與三篇合體決策白皮書.pdf")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>《生成式 AI 正在顛覆市場研究》深度閱讀與「三篇合體」企業科學決策白皮書</title>
<style>
  @page {
    size: A4 portrait;
    margin: 12mm 14mm 12mm 14mm;
  }
  * {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  body {
    font-family: "Microsoft JhengHei", "PingFang TC", "Noto Sans CJK TC", sans-serif;
    font-size: 10pt;
    line-height: 1.66;
    color: #1E293B;
    background-color: #FFFFFF;
    margin: 0;
    padding: 0;
  }
  p {
    margin: 0 0 7px 0;
    text-align: justify;
    orphans: 3;
    widows: 3;
  }

  /* Section Continuity Lock: keeps heading + intro + first block glued together */
  .keep-together {
    display: inline-block;
    width: 100%;
    break-inside: avoid;
    page-break-inside: avoid;
  }

  /* Header Cover Banner */
  .report-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
    color: #FFFFFF;
    padding: 14px 18px;
    border-radius: 7px;
    margin-bottom: 10px;
    border-bottom: 3.5px solid #38BDF8;
  }
  .report-header .doc-tag {
    display: inline-block;
    background-color: rgba(56, 189, 248, 0.2);
    color: #7DD3FC;
    border: 1px solid #38BDF8;
    font-size: 8pt;
    font-weight: 700;
    padding: 1.5px 9px;
    border-radius: 4px;
    margin-bottom: 5px;
    letter-spacing: 0.5px;
  }
  .report-header h1 {
    font-size: 16.5pt;
    font-weight: 800;
    line-height: 1.30;
    margin: 0 0 5px 0;
    color: #FFFFFF;
  }
  .report-header .subtitle {
    font-size: 9.2pt;
    color: #CBD5E1;
    margin: 0 0 6px 0;
    line-height: 1.45;
  }
  .report-header .meta-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    font-size: 8.2pt;
    color: #94A3B8;
    border-top: 1px solid rgba(255,255,255,0.18);
    padding-top: 5px;
  }
  .report-header .meta-grid span strong {
    color: #E2E8F0;
  }

  /* Main Messages Executive Box (1:3:25 Rule) */
  .main-messages {
    background-color: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-left: 5px solid #1E40AF;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 12px;
  }
  .main-messages-title {
    font-size: 10.6pt;
    font-weight: 800;
    color: #1E40AF;
    margin-bottom: 5px;
  }
  .main-messages ol {
    margin: 0;
    padding-left: 18px;
  }
  .main-messages li {
    margin-bottom: 4px;
    font-size: 9.4pt;
    line-height: 1.56;
    color: #1E293B;
  }
  .main-messages li:last-child {
    margin-bottom: 0;
  }

  /* Section Headings (Layer-Cake High Information Scent) */
  h2 {
    font-size: 12.2pt;
    font-weight: 800;
    color: #0F172A;
    background-color: #F1F5F9;
    border-left: 4.5px solid #0F172A;
    padding: 5px 11px;
    margin: 12px 0 6px 0;
    border-radius: 0 4px 4px 0;
    break-after: avoid;
    page-break-after: avoid;
  }
  h3 {
    font-size: 10.5pt;
    font-weight: 700;
    color: #1E3A8A;
    margin: 9px 0 5px 0;
    break-after: avoid;
    page-break-after: avoid;
  }

  /* Native Large-Font Architecture Schematic with True Parallel Row Table! */
  .native-schematic {
    border: 1.5px solid #94A3B8;
    border-radius: 7px;
    background-color: #F8FAFC;
    padding: 8px 10px;
    margin: 8px 0 11px 0;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .schematic-header {
    background-color: #0F172A;
    color: #FFFFFF;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 9.8pt;
    font-weight: 800;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .schematic-header span.badge {
    background-color: #0284C7;
    color: #FFFFFF;
    white-space: nowrap;
    font-size: 8pt;
    padding: 1.5px 8px;
    border-radius: 4px;
    margin-left: 8px;
  }
  table.schematic-parallel-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 6px 0;
  }
  table.schematic-parallel-table th {
    width: 33.33%;
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-top: 3.5px solid #425A80;
    border-bottom: none;
    border-radius: 5px 5px 0 0;
    padding: 6px 9px;
    text-align: left;
    font-size: 9.6pt;
    font-weight: 800;
    color: #0F172A;
    vertical-align: top;
  }
  table.schematic-parallel-table th.col-dao {
    border-top-color: #425A80; /* Blue H=250 */
  }
  table.schematic-parallel-table th.col-fa {
    border-top-color: #8C581E; /* Ochre H=35 */
  }
  table.schematic-parallel-table th.col-shu {
    border-top-color: #1D6E58; /* Teal H=165 */
  }
  table.schematic-parallel-table td {
    width: 33.33%;
    background-color: #FFFFFF;
    border-left: 1px solid #CBD5E1;
    border-right: 1px solid #CBD5E1;
    border-top: 1px dashed #E2E8F0;
    padding: 6px 9px;
    font-size: 9.2pt;
    line-height: 1.56;
    vertical-align: top;
    color: #1E293B;
  }
  table.schematic-parallel-table tr.last-row td {
    border-bottom: 1px solid #CBD5E1;
    border-radius: 0 0 5px 5px;
  }

  /* Parallel Row Bullet Table for 2-Column Comparisons */
  .parallel-bullet-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 8px 0;
    margin: 6px 0 10px 0;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .parallel-bullet-table td {
    width: 50%;
    vertical-align: top;
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-left: 4.5px solid #425A80;
    border-radius: 5px;
    padding: 8px 11px;
    font-size: 9.4pt;
    line-height: 1.64;
  }
  .parallel-bullet-table td.east-wall {
    border-left-color: #8C581E; /* Ochre H=35 */
    background-color: #FFF8EE;
  }
  .parallel-bullet-table td.west-wall {
    border-left-color: #8A3E56; /* Rose H=345 */
    background-color: #FFF1F4;
  }
  .bullet-hook {
    display: block;
    font-weight: 800;
    font-size: 9.7pt;
    color: #0F172A;
    margin-bottom: 3px;
  }
  .east-wall .bullet-hook {
    color: #78350F;
  }
  .west-wall .bullet-hook {
    color: #881337;
  }

  /* Structured Single-Column Bullet Cards */
  .structured-list {
    margin: 5px 0 10px 0;
  }
  .structured-item {
    background-color: #F1F5FF;
    border: 1px solid #CBD5E1;
    border-left: 4px solid #425A80;
    border-radius: 5px;
    padding: 7px 11px;
    margin-bottom: 6px;
    font-size: 9.5pt;
    line-height: 1.62;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .structured-item.item-purple {
    border-left-color: #8C581E;
    background-color: #FFF8EE;
  }
  .structured-item.item-teal {
    border-left-color: #1D6E58;
    background-color: #EEFBF6;
  }

  /* Callout Boxes */
  .callout {
    padding: 8px 12px;
    border-radius: 5px;
    margin: 7px 0 10px 0;
    font-size: 9.4pt;
    line-height: 1.60;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .callout-synth {
    background-color: #FBF5FD;
    border: 1px solid #EADCF0;
    border-left: 4.5px solid #704882;
    color: #3B1E48;
  }
  .callout-title {
    font-weight: 800;
    font-size: 9.8pt;
    margin-bottom: 2px;
    display: block;
  }

  /* Ehrenberg & Few Booktabs Scientific Supertables (NO vertical lines!) */
  table.booktabs {
    width: 100%;
    border-collapse: collapse;
    margin: 6px 0 12px 0;
    font-size: 9.0pt;
    line-height: 1.50;
    border-top: 2.2px solid #0F172A;
    border-bottom: 2.2px solid #0F172A;
  }
  table.booktabs tr {
    break-inside: avoid;
    page-break-inside: avoid;
  }
  table.booktabs thead th {
    background-color: #F1F5F9;
    color: #0F172A;
    font-weight: 800;
    text-align: left;
    padding: 6px 8px;
    border-bottom: 1.4px solid #334155;
  }
  table.booktabs tbody td {
    padding: 6px 8px;
    border-bottom: 0.6px solid #CBD5E1;
    vertical-align: top;
    color: #1E293B;
  }
  table.booktabs tbody tr:nth-child(even) td {
    background-color: #F8FAFC;
  }
  table.booktabs tbody tr.bottom-line-row td {
    background-color: #EFF6FF !important;
    color: #1E3A8A;
    font-weight: 700;
    border-top: 1.4px solid #1E40AF;
    border-bottom: none;
    padding: 7px 8px;
  }
  .num-highlight {
    font-weight: 800;
    color: #0F172A;
  }

  /* Compact Formula Sandwich Protocol */
  .formula-sandwich {
    border: 1.2px solid #CBD5E1;
    border-radius: 6px;
    background-color: #FFFFFF;
    margin: 7px 0 11px 0;
    overflow: hidden;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .formula-top {
    background-color: #F8FAFC;
    padding: 6px 11px;
    border-bottom: 1px dashed #CBD5E1;
    font-size: 9.3pt;
    color: #334155;
  }
  .formula-mid {
    padding: 8px 11px;
    text-align: center;
    background-color: #FFFBEB;
    font-family: "Cambria Math", "Times New Roman", serif;
    font-size: 10.2pt;
    color: #0F172A;
  }
  .formula-mid .math-row {
    display: flex;
    justify-content: space-between;
    align-items: stretch;
    gap: 10px;
  }
  .formula-mid .math-box {
    background: #FFFFFF;
    border: 1.2px solid #F59E0B;
    border-radius: 5px;
    padding: 5px 9px;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .formula-mid .math-caption {
    display: block;
    font-family: "Microsoft JhengHei", sans-serif;
    font-size: 8.3pt;
    color: #B45309;
    font-weight: 700;
    margin-top: 2px;
  }
  .formula-bot {
    background-color: #F8FAFC;
    padding: 7px 11px;
    border-top: 1px dashed #CBD5E1;
    font-size: 9.2pt;
    line-height: 1.54;
    color: #334155;
  }

  /* Peak-End Closing Block (Kahneman 1993 Rule) */
  .closing-seal-box {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    color: #FFFFFF;
    border-radius: 8px;
    padding: 14px 18px;
    margin-top: 12px;
    border-top: 4px solid #38BDF8;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .closing-seal-box h3 {
    color: #38BDF8;
    font-size: 11.4pt;
    margin: 0 0 8px 0;
  }
  table.closing-parallel-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 8px 0;
    margin-bottom: 10px;
  }
  table.closing-parallel-table th {
    width: 33.33%;
    background-color: rgba(56, 189, 248, 0.16);
    border: 1px solid rgba(56, 189, 248, 0.45);
    border-bottom: none;
    border-radius: 5px 5px 0 0;
    padding: 6px 10px;
    text-align: left;
    color: #7DD3FC;
    font-size: 9.5pt;
    font-weight: 800;
  }
  table.closing-parallel-table td {
    width: 33.33%;
    background-color: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(56, 189, 248, 0.45);
    border-top: 1px dashed rgba(56, 189, 248, 0.3);
    border-radius: 0 0 5px 5px;
    padding: 7px 10px;
    font-size: 9.1pt;
    line-height: 1.55;
    color: #F1F5F9;
    vertical-align: top;
  }
  .closing-footer-bar {
    border-top: 1px solid rgba(255, 255, 255, 0.22);
    padding-top: 7px;
    font-size: 8.5pt;
    line-height: 1.5;
    color: #CBD5E1;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
  }
  .closing-footer-bar span:last-child {
    white-space: nowrap;
    color: #38BDF8;
  }
</style>
</head>
<body>

  <!-- COVER BANNER -->
  <div class="report-header">
    <div class="doc-tag">EXECUTIVE STRATEGY &amp; CONCEPT-CENTRIC WHITE PAPER (B1 × B3)</div>
    <h1>《生成式 AI 正在顛覆市場研究》深度閱讀與「三篇合體」企業科學決策白皮書</h1>
    <div class="subtitle">整合 HBR 全篇脈絡架構 × 三類數據結構與大小模型分工 × 盲測訂價「混淆現象」因果公式 × 四大前沿解法死穴批判 × 「道・法・術」三階閉環</div>
    <div class="meta-grid">
      <span><strong>主文獻：</strong>Jeremy Korst, Stefano Puntoni, Olivier Toubia (HBR)</span>
      <span><strong>跨篇合體：</strong>《顧客需求不靠猜》(Mittal et al.) ＋ 《AI 能強化你的數據分析能力》(Davenport &amp; Fitts)</span>
      <span><strong>產出日期：</strong>2026-10-31</span>
    </div>
  </div>

  <!-- MAIN MESSAGES -->
  <div class="main-messages">
    <div class="main-messages-title">★ Main Messages 決策主訊息框：四大核心行動斷言 (So-What Assertions)</div>
    <ol>
      <li><strong>【AI 訪談員破除人類道德偽裝】</strong>：當生成式 AI 擔任「動態訪談員（如 Outset.ai）」時，因不會觸發受訪者的<strong>「心理與道德修飾機制（社會期許偏誤）」</strong>，反而能比真人訪談挖出更坦誠的深層痛點，同時兼顧量化調查的規模與質化訪談的深度。</li>
      <li><strong>【資料結構決定大小模型分工】</strong>：企業私有小型模型（如 Rockfish Data）雖具絕對隱私，但僅能學習<strong>結構化（數字型／類別型）</strong>與<strong>半結構化數據</strong>之統計機率；唯有具備人類世界知識先驗的公開大型模型，方能處理並生成<strong>非結構化質化數據</strong>（最佳折衷解為以內部私有數據微調大型模型）。</li>
      <li><strong>【警惕盲測訂價混淆與感官失靈】</strong>：生成式 AI 天生運算的是「語境條件聯想 <em>P(Y|X)</em>」而非「獨立因果干預 <em>P(Y|do(X))</em>」，在盲測訂價實驗中會自動腦補歷史價與競品價同步變貴（<strong>混淆現象 Confounding</strong>），且無法模擬生理嗅覺與潛意識記憶（如高砂香料案例）；單靠修改提示詞只會淪為「挖東牆補西牆」。</li>
      <li><strong>【放棄萬能模型，執行「道・法・術」情境權變】</strong>：四大前沿修補解法各有理論死穴（具身感官不可壓縮、複雜函式誤設、跨時間分布偏移、歷史微調外推失靈）；企業必須以《顧客需求不靠猜》定錨關鍵問題（<strong>道</strong>）、以《AI 強化數據分析》打通 ERP/CRM 情境底座（<strong>法</strong>），再以《生成式 AI 顛覆市場研究》依商業情境權變配置工具（<strong>術</strong>）。</li>
    </ol>
  </div>

  <!-- SECTION 1 (Fits continuously right on Page 1!) -->
  <h2>壹、【全篇內容架構總覽】生成式 AI 如何以四大核心能力重塑市場研究價值鏈</h2>
  <p>傳統市場研究長期受困於「成本高昂、時程漫長」以及「量化調查廣度 vs. 質化訪談深度不可兼得」的結構性瓶頸。根據本文作者與 GBK Collective 針對 170 位市場研究從業人員與企業用戶的實證調查，高達 <strong>45% 受訪者已在數據與見解活動中使用生成式 AI，另有 45% 正規畫導入</strong>（其中 62% 用於統整冗長訪談逐字稿、58% 用於分析數據、54% 用於撰寫報告），逾 80% 認同其能大幅提升生產力並騰出時間進行高價值的策略說故事。</p>

  <!-- Native Large-Font Schematic 1 with True Parallel Rows -->
  <div class="native-schematic">
    <div class="schematic-header">
      <span>【原生結構圖一】《生成式 AI 正在顛覆市場研究》全篇脈絡總覽架構圖（Ausubel 宏觀結構）</span>
      <span class="badge">免放大清晰大字版</span>
    </div>
    <table class="schematic-parallel-table">
      <thead>
        <tr>
          <th>① 四大能力 × 三大市調階段</th>
          <th class="col-success">② 四大變革機會與接地氣三機制</th>
          <th class="col-danger">③ 四大風險局限與四大破局解法</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>● [核心能力]：</strong>統整摘要 (62%)、編碼清理分析 (58%)、人機互動追問、報告寫作 (54%)。</td>
          <td><strong>● [四大機會]：</strong>強化實務（Outset.ai）→ 取代問卷（安永 95% 一致）→ 補缺口（30%）→ 數位雙生（85% 信度）。</td>
          <td><strong>● [四大局限]：</strong>人口偏誤（偏自由派高學歷）、跨期搖擺（Bisbee 3 個月）、感官失靈（高砂香料）、訂價混淆。</td>
        </tr>
        <tr class="last-row">
          <td><strong>● [三大階段]：</strong>設計研究與找機會 → 蒐集與分析數據 → 報告影響，變身「全天候智慧引擎」。</td>
          <td><strong>● [三大錨定]：</strong>純合成僅 31% 認同高價值，須結合 Few-shot 範例 ＋ RAG 知識庫 ＋ 內部數據微調。</td>
          <td><strong>● [四大解法]：</strong>綁定真人數位雙生、右腦 AI＋左腦統計、少量真人＋AI 校準、歷史實驗微調。</td>
        </tr>
      </tbody>
    </table>
  </div>

  <h3>表一：生成式 AI 賦能市場研究之「能力 × 階段 × 機會」科學對照總表 (Booktabs 三線表)</h3>
  <table class="booktabs">
    <thead>
      <tr>
        <th style="width: 15%;">變革機會層級</th>
        <th style="width: 19%;">核心機制與代表案例</th>
        <th style="width: 20%;">階段一：設計研究與找機會</th>
        <th style="width: 21%;">階段二：蒐集與分析數據</th>
        <th style="width: 25%;">階段三：報告影響與實證表現</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>1. 強化現有實務</strong><br><em>(Enhance)</em></td>
        <td><strong>統整＋互動＋編碼</strong><br>Meaningful / Outset.ai / WeightWatchers</td>
        <td>摘要過往文獻研究、以聊天機器人腦力激盪並從現有數據挖掘假設</td>
        <td><strong>AI 動態訪談員</strong>依前次回答追問；自動在網頁設置問卷並從文本提取見解</td>
        <td>自動闡述重點與生成視覺化；<span class="num-highlight">80%+</span> 認同提升效率，AI 訪談消除道德修飾且幾乎無幻覺</td>
      </tr>
      <tr>
        <td><strong>2. 取代現有實務</strong><br><em>(Replace)</em></td>
        <td><strong>合成數據 (Synthetic)</strong><br>Evidenza × 安永 EY / Synthetic Users</td>
        <td>建立詳細假想顧客樣貌（Persona）與產品使用情境假設</td>
        <td>創造合成受訪者填寫量化問卷，或對合成角色進行深入<strong>質化訪談</strong></td>
        <td><span class="num-highlight">81%</span> 已用或計畫使用；安永雙盲測試 1,000 名合成 CEO 結論與真人高達 <span class="num-highlight">95%</span> 相同</td>
      </tr>
      <tr>
        <td><strong>3. 填補現有缺口</strong><br><em>(Fill Gaps)</em></td>
        <td><strong>全天候智慧引擎</strong><br>通用磨坊 / Arena / Rockfish Data</td>
        <td>針對過往因時間或預算不足而憑直覺拍板的決策，即時提供經驗證據</td>
        <td>模擬極難接觸之 B2B 客戶或跨門市地方客群偏好，加速早期產品發想</td>
        <td><span class="num-highlight">30%</span> 用於引導過去無外部數據之決策；估算市場定位對財務長重視之 ROI 指標影響</td>
      </tr>
      <tr>
        <td><strong>4. 創造新型態見解</strong><br><em>(Create New)</em></td>
        <td><strong>顧客數位雙生</strong><br>哥倫比亞 2,500 人群組 / 史丹福 / CivicSync</td>
        <td>以真人心理、認知、行為測驗或線上購物軌跡建立「基準事實」分身</td>
        <td>讓 B2B 業務與永不疲勞的<strong>客戶數位雙生</strong>事前演練話術、測試廣告共鳴</td>
        <td><span class="num-highlight">82%</span> 已實驗或計畫實驗；史丹福重測數位雙生與真人兩週後回答相似度達 <span class="num-highlight">85%</span></td>
      </tr>
      <tr class="bottom-line-row">
        <td>★ 決策收斂底線</td>
        <td colspan="4"><strong>AI 訪談員負責採集無道德偽裝之真心話，合成數據與數位雙生負責百倍速擴大早期探索廣度；但現階段僅 31% 認為純合成數據價值極高，必須搭配「提示範例＋知識庫提取（RAG）＋微調參數」三大錨定機制，且不可取代最終真人盲測。</strong></td>
      </tr>
    </tbody>
  </table>

  <div style="text-align: center; margin: 9px 0 12px 0; break-inside: avoid; page-break-inside: avoid;">
    <img src="chart_gbk_ai_adoption.png" style="width: 78%; max-width: 540px; border-radius: 6px; border: 1px solid #CBD5E1;" alt="GBK 實證調查：生成式 AI 市調任務滲透與價值認同">
    <div style="font-size: 8.4pt; color: #64748B; margin-top: 4px; font-weight: bold;">
      ▲ 圖 1：GBK Collective 170 位市調專家調查：各核心任務滲透率與 Knaflic 80/20 策略時間釋放聚光燈
    </div>
  </div>

  <!-- SECTION 2 -->
  <h2>貳、【概念拆解一】資料結構光譜與「私有小型模型 vs. 公開大型模型」之取捨機制</h2>
  <p>在導入客製化合成數據時，企業首當其衝面臨<strong>「數據機密隱私」與「模型語意理解深度」的兩難權衡</strong>（見原文第 10 頁）。要理解為何小型私有模型（如美國陸軍與國土安全部採用的 Rockfish Data）大多只能處理結構化與半結構化數據，而公開大型模型才能處理非結構化質化數據，必須從資料科學的三階結構光譜拆解：</p>
  <div class="structured-list">
    <div class="structured-item">
      <span class="bullet-hook">● 【第一階：結構化數據（Structured Data）】—— 固定二維表格欄位（小型私有模型即可精準建模）</span>
      指具備嚴格固定欄位、可直接存入關聯式資料庫或 Excel 表格的數據。文中特別指明其包含兩類統計尺度：① <strong>數字型數據（Numerical Data）</strong>，即可直接進行算術運算的量化數值（如顧客年齡 <code>34</code> 歲、年消費額 <code>28,500</code> 元、網頁停留秒數）；② <strong>類別型數據（Categorical Data）</strong>，即代表分類標籤或等級順序的離散屬性（如性別、居住城市、會員卡別、李克特五點滿意度選項）。
    </div>
    <div class="structured-item item-purple">
      <span class="bullet-hook">● 【第二階：半結構化數據（Semi-Structured Data）】—— 自帶標籤之巢狀行為日誌（小型私有模型可處理）</span>
      指無法直接塞入死板二維表格（因每位顧客的行為序列長短不一、具巢狀階層），但內部自帶<strong>結構標籤（Tags / Keys）</strong>而能被電腦直接解析的資料。典型市調實例包括網站與 App 點擊流日誌（JSON 格式之瀏覽軌跡）、帶有固定標頭欄位的電子郵件與客服工單紀錄。
    </div>
    <div class="structured-item item-teal">
      <span class="bullet-hook">● 【第三階：非結構化質化數據（Unstructured Qualitative Data）】—— 自然語言與深層動機（唯有公開大型模型能駕馭）</span>
      指完全無預先定義格式、承載人類自然語言脈絡、情緒轉折、隱喻與深層動機（回答 <em>Why</em> 與 <em>How</em>）的原始資料。典型實例包含深度訪談逐字稿、焦點團體錄影、社群媒體長篇抱怨貼文與開放式問卷作答（如威斯康辛商學院研究與 Synthetic Users 平台之合成深度訪談）。
    </div>
  </div>

  <div class="callout callout-synth">
    <span class="callout-title">💡 為什麼小型私有模型無法處理質化數據？——「世界知識先驗（World Knowledge Prior）」的關鍵差距</span>
    小型生成式 AI 模型僅在企業內部封閉的表格與系統日誌上訓練，本質上只學會欄位與數字間的統計聯合機率分布 <em>P(X₁, X₂, ..., Xₚ)</em>，<strong>從未讀過全人類的書籍、論壇與日常對話，因此不懂人類語言的言外之意與心理脈絡</strong>。反之，公開大型語言模型預訓練於數兆字人類文本，具備深厚的「人類常識與語意先驗」。因此，<strong>「以企業內部獨有數據微調（Fine-tune）大型公開模型」</strong>正是兼顧機密隱私與質化深度的黃金折衷解。
  </div>

  <!-- SECTION 3 -->
  <h2>參、【概念拆解二】為何人類對 AI 訪談員更誠實？兼論盲測訂價實驗之「混淆現象」</h2>
  <p>本文揭示了生成式 AI 在市場研究中極具啟發性的雙面特性：當 AI 擔任<strong>「訪談提問者」</strong>時能消除人類的心理防禦；但當 AI 擔任<strong>「盲測實驗受試者」</strong>時卻會因語境腦補而破壞實驗因果。</p>
  <h3>一、 心理與道德修飾機制的解除：AI 動態訪談員的優勢</h3>
  <p>在 WeightWatchers 與 Outset.ai 的合作實證中，受訪者面對 AI 訪談員反而比面對真人更坦誠。正如第一階段思辨所點破：<strong>人類在與其他「人」互動時，會自動啟動「心理與道德修飾機制」（即行為科學的社會期許偏誤 Social Desirability Bias 與評價焦慮）</strong>，為了顧及面子或合乎道德規範而修飾答案（這也完美解釋了為何在《顧客需求不靠猜》中，顧客口頭上 100% 宣稱重視 ESG 永續，統計模型算出的實際購買提升潛力卻為零）。當提問者換成無道德批判眼神的機器時，這套防禦機制不復觸發，使企業得以獲取最真實的消費者痛點。</p>

  <h3>二、 盲測訂價實驗中的「混淆現象（Confounding）」與因果公式三明治</h3>
  <p>相反地，當研究人員模仿真人盲測，讓不同組別的 AI 數位受訪者看到同一產品的不同價格 <em>X</em> 並詢問購買意願 <em>Y</em> 時，AI 產生的需求曲線卻幾乎不隨價格上漲而下降。以下透過因果推論公式拆解此一失靈機制：</p>

  <div class="formula-sandwich">
    <div class="formula-top">
      <strong>(上) 直覺問題意識：</strong>為何真人盲測能測出「價格越貴、買的人越少」的向下傾斜需求曲線，而生成式 AI 卻會在看到高價時自己偷偷腦補「外界物價與競品也一樣貴」，導致需求曲線平坦失真？
    </div>
    <div class="formula-mid">
      <div class="math-row">
        <div class="math-box" style="border-color: #425A80; background-color: #F1F5FF;">
          <strong style="color: #0F172A;">P(Y | do(X = x)) = ∑<sub>z</sub> P(Y | X = x, Z = z) · P(Z = z)</strong>
          <span class="math-caption" style="color: #345B8C;">【真人隨機盲測】背景物價與競品價格 Z 獨立於測試價格 X（P(Z|X) = P(Z)）</span>
        </div>
        <div style="font-size: 16pt; font-weight: 800; color: #8A3E56; align-self: center;">≠</div>
        <div class="math-box" style="border-color: #8A3E56; background-color: #FFF1F4;">
          <strong style="color: #0F172A;">P<sub>LLM</sub>(Y | X = x) = ∑<sub>z</sub> P(Y | X = x, Z = z) · P<sub>LLM</sub>(Z = z | X = x)</strong>
          <span class="math-caption" style="color: #881337;">【AI 語境腦補混淆】看到高價 X 時自動調高 P<sub>LLM</sub>(Z|X)，腦補競品與歷史價也同步變貴！</span>
        </div>
      </div>
    </div>
    <div class="formula-bot">
      <strong>(下) 參數物理意義與極端邊界推演：</strong><br>
      • <strong>自變數 X（測試價格）與應變數 Y（購買決策）</strong>：研究員欲測量單純調高 X（如 1,000 元 → 5,000 元）對 Y 的獨立因果效應。<br>
      • <strong>混淆變數 Z（Confounder：歷史價格／店內競品價格）</strong>：在真人盲測中，受試者活在真實物價世界，看到測試商品標價 5,000 元時，心中對其他競品價格 Z（1,200 元）的認知不變，故果斷拒買。但生成式 AI 難以將價格 X 視為隨機抽樣，看到 5,000 元時會自動在隱空間調高 Z（腦補「店內其他產品或歷史價格也都是 5,000 元」），使高價購買顯得合理，徹底打亂 X 與 Y 的真實關係！
    </div>
  </div>

  <div style="text-align: center; margin: 9px 0 12px 0; break-inside: avoid; page-break-inside: avoid;">
    <img src="chart_demand_curve_confounding.png" style="width: 78%; max-width: 540px; border-radius: 6px; border: 1px solid #CBD5E1;" alt="因果推論實證對照：定價需求曲線失靈機制">
    <div style="font-size: 8.4pt; color: #64748B; margin-top: 4px; font-weight: bold;">
      ▲ 圖 2：真人隨機盲測 P(Y|do(X)) 向下傾斜需求曲線 vs. AI 語境腦補混淆 P_LLM(Y|X) 平坦失真曲線實證對照（HCL 科學色尺對照）
    </div>
  </div>

  <!-- SECTION 4 -->
  <div class="keep-together">
    <h2>肆、【方法論交鋒】為何純改提示詞淪為「挖東牆補西牆」？四大前沿解法與死穴批判</h2>
    <p>針對上述實驗混淆現象，若僅試圖在提示詞（Prompt）中寫入更詳細的數據情境規範，在結構上必然陷入<strong>「挖東牆補西牆」</strong>的雙重死胡同（以下採<strong>水平平行對齊列點</strong>對照呈現）：</p>

    <table class="parallel-bullet-table">
      <tr>
        <td class="east-wall">
          <span class="bullet-hook">● 【東牆：未知腦補變數永遠鎖不完（無限混淆）】</span>
          就算研究員在提示詞中死鎖「歷史價與店內競品價皆為 1,200 元」，具備數千億參數的 AI 看到標價 5,000 元時，仍會在高維度隱空間自動繞道腦補<strong>「現在正值全球大缺貨、頂級巨星聯名代言、或特殊節慶限量溢價」</strong>。人類研究員永遠無法事前窮舉並鎖死所有潛在的混淆變數 <em>Z</em>！
        </td>
        <td class="west-wall">
          <span class="bullet-hook">● 【西牆：寫太白引發需求特徵劇透（焦點錯覺）】</span>
          反之，若在提示詞中刻意強調「別家一模一樣都賣 1,200 元，唯獨這家賣 5,000 元，請決定買不買」，在心理學上會觸發<strong>「需求特徵（Demand Characteristics，受試者猜出實驗目的）」與「焦點錯覺」</strong>，使 AI 從「過度遲鈍」瞬間跳到「100% 拒買的比大小計算機」，依然測不出真實人類的價格彈性！
        </td>
      </tr>
    </table>
  </div>

  <p>為跳出純文字提示詞的死胡同，學術界發展出四大根本性解法；然而，正如第一階段深度思辨所批判，<strong>這四種解法各自皆存在無法根除的「理論死穴」，因此企業必須放棄尋找萬能單一模型，改採「情境權變投資組合（Contingency Portfolio）」</strong>：</p>

  <h3>表二：四大前沿破局解法之運作機制、理論死穴批判與商業情境配置矩陣</h3>
  <table class="booktabs">
    <thead>
      <tr>
        <th style="width: 18%;">前沿破局解法</th>
        <th style="width: 25%;">核心運作機制與文中案例</th>
        <th style="width: 32%;">第一性原理「理論死穴」批判 (您的思辨洞察)</th>
        <th style="width: 25%;">最適配之商業應用戰場</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>解法一：綁定真人記憶之數位雙生</strong><br><em>(Grounded Twins)</em></td>
        <td>對真人進行數小時訪談、心理認知測驗並追蹤購物軌跡（哥倫比亞 2,500 人群組、史丹福、CivicSync），建立基準事實錨點</td>
        <td><strong>【具身認知與感質不可壓縮性】</strong>：無法「真的把一整個人塞進模型」！文字逐字稿無法編碼生理嗅覺、味覺與潛意識記憶（如文中<strong>高砂香料 Takasago</strong> 測試香氣徹底失靈）</td>
        <td>B2B 銷售人員話術演練、客服應對模擬、理性功能型產品之早期概念訪談</td>
      </tr>
      <tr>
        <td><strong>解法二：右腦 AI 轉譯＋左腦統計公式</strong><br><em>(Hybrid Model)</em></td>
        <td>右腦（大模型）僅將非結構化圖文轉譯為特徵分數；左腦交由傳統統計線性／選擇模型計算價格彈性，數學上切斷腦補混淆</td>
        <td><strong>【計量模型誤設偏誤 (Misspecification)】</strong>：雖出現幻覺機率最小，但面對高度複雜、多變數非線性交互作用的感性問題時，左腦極難寫出高解釋力函式（寫簡單 R² 低、寫複雜又過度配適）</td>
        <td>成熟產業之常規品牌健康度追蹤、核心價值驅動因素之「提升潛力（Lift）」排序</td>
      </tr>
      <tr>
        <td><strong>解法三：少量真人＋大量 AI 統計校準</strong><br><em>(PPI Calibration)</em></td>
        <td>以 100 名真人盲測為黃金基準，搭配 10,000 名 AI 合成受訪者，用統計公式計算並扣除 AI 的系統性腦補誤差</td>
        <td><strong>【分布偏移與湊巧對齊】</strong>：極不穩定！當下 AI 對準人類可能只是「湊巧發生」，一旦問題換字眼或跨時間（如文中<strong>范登堡 Bisbee 2024 研究</strong>發現 3 個月內表現不穩），校準即失效再發幻覺</td>
        <td>預算受限下之大規模量化問卷擴充（需每波次重新抽取真人小樣本動態校準）</td>
      </tr>
      <tr>
        <td><strong>解法四：大量歷史數據與實驗微調</strong><br><em>(Fine-Tuning)</em></td>
        <td>拿企業過往累積之大量真實調查與歷史 A/B Test 數據直接微調模型權重（如 Evidenza、GBK Collective 測試不同組合）</td>
        <td><strong>【後照鏡外推失靈 (Extrapolation Failure)】</strong>：拿過去數據訓練屬於「分布內插值」，但面對未來<strong>「消費者行為劇變」或「突破性產品創新」</strong>（文中第 15 頁警告）時預測力較弱</td>
        <td>既有產品線之小幅改版測試、跨門市常規選品配置（如 Arena 零售應用）</td>
      </tr>
      <tr class="bottom-line-row">
        <td>★ 權變配置底線</td>
        <td colspan="3"><strong>統計大師 George Box 鐵律：「所有模型都是錯的，但有些在特定情境極度有用。」—— 早期發想用「解法一＋四」衝百倍速度；常規診斷用「AI 訪談員＋解法二」抓高 Lift 關鍵因素；最終定價、多感官（香水/食品）與突破性創新則強制回歸「真人隨機盲測（A/B Test）」！</strong></td>
      </tr>
    </tbody>
  </table>

  <!-- SECTION 5: True Parallel Row Table so Bullet 1 and Bullet 2 align horizontally across all 3 columns! -->
  <div class="keep-together">
    <h2>伍、【三篇合體終極藍圖】企業數據科學與生成式 AI 決策之「道・法・術」三階閉環</h2>
    <p>綜合本次深度閱讀的三篇 HBR 經典文獻，企業若想建立真正的科學決策護城河，必須按照您在思辨中提出的<strong>「道（界定問題與方向）→ 法（盤點能力與情境底座）→ 術（前線市調實操與權變）」</strong>三階次序，將三篇文章串聯為一個有機閉環：</p>

    <div class="native-schematic">
      <div class="schematic-header">
        <span>【原生結構圖二】三篇 HBR 合體「道・法・術」三階企業科學決策閉環（水平平行對齊矩陣）</span>
        <span class="badge">道 → 法 → 術 貫通藍圖</span>
      </div>
      <table class="schematic-parallel-table">
        <thead>
          <tr>
            <th class="col-dao">第一階【道：界定問題與方向】<br>《顧客需求不靠猜！統計模型找正解》</th>
            <th class="col-fa">第二階【法：能力與情境底座】<br>《AI 能強化你的數據分析能力》</th>
            <th class="col-shu">第三階【術：前線市調與權變】<br>《生成式 AI 正在顛覆市場研究》</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>● [定位盲點] 破除高層直覺偏誤：</strong><br>72% 上市 B2B 高層認知與顧客真實重視呈零或負相關，85.5% 每兩年大改優先順序（受顯眼客訴與盲從對手誤導）。</td>
            <td><strong>● [定位盲點] 打破數據孤島與虛假相關：</strong><br>將分析直接內嵌於 ERP 與 CRM 系統，由人類專家預先設定「背景情境（Contextual Information）」因果護欄。</td>
            <td><strong>● [定位盲點] 突破廣度與深度兩難：</strong><br>針對第一階鎖定的 X*，派出 AI 動態訪談員（Outset.ai）解除受訪者「心理與道德修飾機制」，並以 ERP 數據微調雙生。</td>
          </tr>
          <tr class="last-row">
            <td><strong>● [核心武器] 道斯模型鎖定 X*：</strong><br>用雙層統計模型量化各因素對真實營收 Y 之「提升潛力（Lift）」，嚴格鎖定 1~2 個關鍵因素 X*（ITI 股價漲 162%），為 AI 指明靶心。</td>
            <td><strong>● [核心武器] 擴增分析與 L1 正則化：</strong><br>結合 ML + NLP 口說提問 + NLG 自動摘要賦能平民分析師（挽回數十萬美元折扣），並以 Adjusted R² 與 Lasso 過濾雜訊。</td>
            <td><strong>● [核心武器] 四道關卡真人終審：</strong><br>嚴守價格混淆、多感官與突破性創新三大禁區，通過「開放探索 → 迴歸推導 → 綁定帳本 → 真人隨機盲測（A/B Test）」完成閉環！</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- SECTION 6: PEAK-END CLOSING & ACTION CHECKLIST BLOCK (Parallel Table + Formal Seal) -->
  <div class="closing-seal-box">
    <h3>陸、【終章收束與立即行動檢核】企業導入生成式 AI 市場研究之三步落地守則 (Executive Closing)</h3>
    <table class="closing-parallel-table">
      <thead>
        <tr>
          <th>Step 1：檢核問題靶心（道）</th>
          <th>Step 2：配置資料與模型（法）</th>
          <th>Step 3：執行人機權變閉環（術）</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>在啟動任何 AI 市調專案前，先以道斯線性統計模型檢視現有客戶調查與真實財報毛利 Y，確認本次研究聚焦於高提升潛力（Lift）的 1~2 個核心驅動因素 X*，果斷淘汰零價值口號。</td>
          <td>盤點待分析資料結構：結構化表格與半結構化點擊流可交由私有小模型保機密；涉及非結構化質化訪談則採用「內部 ERP/CRM 歷史數據微調公開大模型」＋ RAG 知識庫錨定。</td>
          <td>以「AI 動態訪談員」收集無道德修飾之痛點、以「顧客數位雙生」百倍速淘汰早期弱點子；在上市最終訂價、五感體驗與突破性創新關頭，強制執行真人隨機 A/B Test 終審！</td>
        </tr>
      </tbody>
    </table>
    <div class="closing-footer-bar">
      <span><strong>獨立高解析全景心智圖附錄（240 DPI `.jpg` 另附於專案目錄）：</strong><code>00_全篇脈絡總覽圖</code> ｜ <code>01_四大機會與資料結構圖</code> ｜ <code>02_實驗混淆與解法批判圖</code> ｜ <code>03_三篇合體藍圖</code></span>
      <span><strong>END OF REPORT ｜ 深度閱讀與視覺化知識統整白皮書</strong></span>
    </div>
  </div>

</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_exe):
    edge_exe = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

cmd = [
    edge_exe,
    "--headless",
    "--disable-gpu",
    f"--print-to-pdf={PDF_PATH}",
    "--no-pdf-header-footer",
    HTML_PATH,
]
subprocess.run(cmd, check=True)

if os.path.exists(HTML_PATH):
    os.remove(HTML_PATH)

print(f"[OK] Generated PDF Report: {PDF_PATH} ({os.path.getsize(PDF_PATH)} bytes)")
