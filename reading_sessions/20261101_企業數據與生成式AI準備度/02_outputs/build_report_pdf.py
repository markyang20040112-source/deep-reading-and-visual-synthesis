"""
build_report_pdf.py
Compiles 01_executive_strategy_report.md into a publication-grade PDF document
(01_executive_strategy_report.pdf) in 100% compliance with:
- document_report_spec.md (B1 1:3:25 Executive Strategy Whitepaper & Chapter-Boundary Page Breaks)
- visual_cognition_principles.md (CIELUV HCL Tri-Tier Solid Colors, W3C CLREQ Typography)
- [INS-09] Zero Single-Character Widows in Table Cells (text-wrap: pretty, nowrap locks)
- [INS-11] Closed 4-Sided Solid Borders on Parallel Cards
"""

import os
import subprocess
import shutil
import tempfile

html_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>【高階決策白皮書】從流沙到混凝土：生成式 AI 時代的企業數據治理與資產準備度策略</title>
<style>
  @page {
    size: A4 portrait;
    margin: 11.5mm 10.5mm 13mm 10.5mm;
    @bottom-center {
      content: "— " counter(page) " / " counter(pages) " —";
      font-size: 8.5pt;
      color: #64748B;
      font-family: "Microsoft JhengHei", "PingFang TC", sans-serif;
    }
  }

  * {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  body {
    font-family: "Microsoft JhengHei", "PingFang TC", "Noto Sans TC", sans-serif;
    color: #0F172A;
    background-color: #FFFFFF;
    line-height: 1.66;
    font-size: 10.0pt;
    margin: 0;
    padding: 0;
    text-wrap: pretty;
    line-break: strict;
  }

  .nowrap {
    white-space: nowrap !important;
    text-wrap: nowrap !important;
  }

  /* Strict Chapter-Boundary Page Break */
  .chapter-break {
    page-break-before: always;
    break-before: page;
  }

  /* Header Cover Banner (HCL Deep Royal Blue H=250) */
  .header-cover {
    background-color: #0F172A;
    color: #FFFFFF;
    border-top: 5px solid #1A48A0;
    border-bottom: 3px solid #38BDF8;
    border-radius: 6px;
    padding: 11px 16px;
    margin-bottom: 10px;
  }
  .badge-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
  }
  .doc-badge {
    display: inline-block;
    background-color: #2659B8;
    color: #FFFFFF;
    font-weight: 700;
    font-size: 8pt;
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: 0.2px;
    white-space: nowrap;
  }
  .doc-id {
    font-size: 7.8pt;
    color: #94A3B8;
    font-family: Consolas, monospace;
    white-space: nowrap;
  }
  h1 {
    color: #FFFFFF;
    font-size: 15.2pt;
    margin: 2px 0 3px 0;
    line-height: 1.28;
    font-weight: 800;
  }
  .subtitle {
    color: #CBD5E1;
    font-size: 9.2pt;
    font-weight: 500;
    margin-bottom: 6px;
  }
  .meta-bar {
    font-size: 7.8pt;
    color: #E2E8F0;
    border-top: 1px solid #334155;
    padding-top: 4px;
    display: flex;
    justify-content: space-between;
    white-space: nowrap;
  }

  /* Section 1: Main Messages Box (HCL Blue Tint #EEF3FE) */
  .main-message-box {
    background-color: #EEF3FE;
    border: 1.5px solid #1A48A0;
    border-left: 6px solid #1A48A0;
    border-radius: 6px;
    padding: 9px 14px;
    margin: 0 0 10px 0;
    break-inside: avoid;
  }
  .main-message-title {
    color: #1A48A0;
    font-weight: 800;
    font-size: 10.3pt;
    margin-bottom: 5px;
    border-bottom: 1px solid #BFDBFE;
    padding-bottom: 3px;
  }

  /* High-Scent Layer-Cake Major Chapter Headings (Always at Top of Chapter Page) */
  h2 {
    color: #0F172A;
    font-size: 11.4pt;
    font-weight: 800;
    background-color: #F8FAFC;
    border-left: 5px solid #1A48A0;
    border-bottom: 1.5px solid #CBD5E1;
    padding: 6px 11px;
    margin-top: 0;
    margin-bottom: 7px;
    break-after: avoid;
    page-break-after: avoid;
  }
  h3 {
    color: #1A48A0;
    font-size: 10.0pt;
    font-weight: 800;
    margin-top: 8px;
    margin-bottom: 5px;
    break-after: avoid;
    page-break-after: avoid;
  }

  p {
    margin: 4px 0 6px 0;
    text-align: justify;
    line-height: 1.64;
    text-wrap: pretty;
    orphans: 3;
    widows: 3;
  }

  ul.clean-list {
    list-style: none;
    margin: 4px 0;
    padding-left: 2px;
  }
  ul.clean-list li {
    margin-bottom: 5px;
    line-height: 1.60;
    text-align: justify;
    text-wrap: pretty;
  }
  .bullet-dot {
    color: #1A48A0;
    font-weight: 900;
    margin-right: 4px;
  }
  .anchor-tag {
    font-weight: 800;
    color: #0F172A;
  }
  .highlight-stat {
    color: #AC1953;
    font-weight: 700;
  }
  .highlight-good {
    color: #006B58;
    font-weight: 700;
  }

  /* Ehrenberg (1977) Scientific Booktabs 3-Line Table */
  table.ehrenberg {
    width: 100%;
    border-collapse: collapse;
    margin: 5px 0 9px 0;
    font-size: 8.9pt;
    line-height: 1.52;
    break-inside: avoid;
  }
  table.ehrenberg th {
    border-top: 2px solid #0F172A;
    border-bottom: 1.5px solid #0F172A;
    padding: 5px 7px;
    background-color: #F8FAFC;
    color: #0F172A;
    font-weight: 800;
    text-align: left;
    white-space: nowrap;
  }
  table.ehrenberg th.num-col,
  table.ehrenberg td.num-col {
    text-align: center;
    white-space: nowrap !important;
    text-wrap: nowrap !important;
  }
  table.ehrenberg td {
    padding: 5px 7px;
    border-bottom: 1px solid #E2E8F0;
    vertical-align: middle;
    text-align: left;
    text-wrap: pretty;
  }
  table.ehrenberg tr.bottom-line td {
    border-top: 1.5px solid #0F172A;
    border-bottom: 2px solid #0F172A;
    background-color: #EEF3FE;
    font-weight: 700;
    color: #1A48A0;
  }

  .stat-line {
    white-space: nowrap;
    display: block;
    line-height: 1.52;
  }

  /* Three-Tier Chart Embed Container */
  .figure-box {
    background-color: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 7px 10px;
    margin: 6px 0 8px 0;
    break-inside: avoid;
  }
  .figure-header {
    font-size: 9.2pt;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 5px;
    border-left: 4px solid #1A48A0;
    padding-left: 8px;
  }
  .figure-img {
    width: 100%;
    max-width: 100%;
    display: block;
    margin: 0 auto;
    border-radius: 4px;
  }
  .figure-footnote {
    font-size: 8.3pt;
    color: #475569;
    margin-top: 5px;
    border-top: 1px dashed #CBD5E1;
    padding-top: 4px;
    text-align: justify;
    line-height: 1.48;
  }

  /* Formula Sandwich Protocol */
  .formula-sandwich {
    border: 1.5px solid #1A48A0;
    border-radius: 6px;
    overflow: hidden;
    margin: 6px 0 10px 0;
    break-inside: avoid;
  }
  .sandwich-top {
    background-color: #EEF3FE;
    padding: 7px 12px;
    font-size: 9.1pt;
    color: #0F172A;
    border-bottom: 1px solid #BFDBFE;
    line-height: 1.58;
  }
  .sandwich-mid {
    background-color: #0F172A;
    color: #FFFFFF;
    text-align: center;
    padding: 9px 14px;
  }
  .math-expr {
    font-family: "Cambria Math", "Times New Roman", Georgia, serif;
    font-size: 12.8pt;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #38BDF8;
  }
  .sandwich-bot {
    background-color: #F8FAFC;
    padding: 7px 12px;
    font-size: 8.9pt;
    color: #1E293B;
    border-top: 1px solid #CBD5E1;
    line-height: 1.58;
  }

  /* Parallel Row-Aligned Grid Cards */
  .parallel-grid-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 6px 0;
    margin: 2px 0;
  }
  .parallel-grid-table td.card-header {
    padding: 6px 8px;
    font-weight: 800;
    font-size: 9.2pt;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    text-align: center;
    white-space: nowrap;
  }
  .parallel-grid-table td.card-row {
    padding: 6px 9px;
    font-size: 8.9pt;
    line-height: 1.52;
    vertical-align: top;
    text-wrap: pretty;
  }
  .parallel-grid-table td.card-footer {
    padding: 6px 9px;
    font-size: 8.9pt;
    font-weight: 700;
    line-height: 1.48;
    vertical-align: top;
    border-bottom-left-radius: 5px;
    border-bottom-right-radius: 5px;
    text-wrap: pretty;
  }
  .b-crimson { border-left: 2px solid #AC1953 !important; border-right: 2px solid #AC1953 !important; border-top: 1px solid #E5A3B8 !important; border-bottom: 1px solid #E5A3B8 !important; }
  .b-crimson-foot { border-left: 2px solid #AC1953 !important; border-right: 2px solid #AC1953 !important; border-top: 1px solid #AC1953 !important; border-bottom: 2px solid #AC1953 !important; }
  .b-ochre { border-left: 2px solid #9C5100 !important; border-right: 2px solid #9C5100 !important; border-top: 1px solid #DFB88C !important; border-bottom: 1px solid #DFB88C !important; }
  .b-ochre-foot { border-left: 2px solid #9C5100 !important; border-right: 2px solid #9C5100 !important; border-top: 1px solid #9C5100 !important; border-bottom: 2px solid #9C5100 !important; }
  .b-blue { border-left: 2px solid #1A48A0 !important; border-right: 2px solid #1A48A0 !important; border-top: 1px solid #93C5FD !important; border-bottom: 1px solid #93C5FD !important; }
  .b-blue-foot { border-left: 2px solid #1A48A0 !important; border-right: 2px solid #1A48A0 !important; border-top: 1px solid #1A48A0 !important; border-bottom: 2px solid #1A48A0 !important; }
  .b-teal { border-left: 2px solid #006B58 !important; border-right: 2px solid #006B58 !important; border-top: 1px solid #6EE7B7 !important; border-bottom: 1px solid #6EE7B7 !important; }
  .b-teal-foot { border-left: 2px solid #006B58 !important; border-right: 2px solid #006B58 !important; border-top: 1px solid #006B58 !important; border-bottom: 2px solid #006B58 !important; }

  /* Native Vector Structural Diagram: Bicameral Architecture */
  .bicameral-diagram {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    padding: 6px 9px;
    margin: 2px 0;
  }
  .prefrontal-box {
    background-color: #FBF1EA;
    border: 2px solid #9C5100;
    border-radius: 5px;
    padding: 5px 11px;
    width: 94%;
    margin: 0 auto 3px auto;
    text-align: center;
  }
  .brain-connector {
    text-align: center;
    font-size: 8.6pt;
    font-weight: 700;
    color: #9C5100;
    margin: 3px 0 5px 0;
  }

  /* Gantt Roadmap Visual Matrix */
  .gantt-bar-bg {
    background-color: #E2E8F0;
    border-radius: 3px;
    height: 12px;
    width: 100%;
    position: relative;
    overflow: hidden;
    margin-bottom: 2px;
  }
  .gantt-fill-1 { background-color: #2659B8; height: 100%; border-radius: 3px; }
  .gantt-fill-2 { background-color: #9C5100; height: 100%; border-radius: 3px; }
  .gantt-fill-3 { background-color: #006B58; height: 100%; border-radius: 3px; }

  /* Kahneman Closing Block & Action Seal */
  .closing-seal {
    background-color: #0F172A;
    color: #F8FAFC;
    border-radius: 6px;
    padding: 10px 14px;
    margin-top: 8px;
    border: 1.5px solid #1A48A0;
    border-left: 6px solid #006B58;
    break-inside: avoid;
  }
  .closing-grid {
    display: grid;
    grid-template-columns: 49% 49%;
    gap: 2%;
    margin-top: 6px;
  }
  .closing-subbox {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 5px;
    padding: 7px 10px;
    font-size: 8.7pt;
    line-height: 1.52;
  }
  .closing-subbox-title {
    color: #38BDF8;
    font-weight: 800;
    font-size: 9.2pt;
    margin-bottom: 4px;
    border-bottom: 1px solid #334155;
    padding-bottom: 3px;
  }
  .sign-off-footer {
    margin-top: 8px;
    padding-top: 5px;
    border-top: 1.5px solid #0F172A;
    display: flex;
    justify-content: space-between;
    font-size: 8.4pt;
    color: #475569;
    font-weight: 700;
    break-inside: avoid;
  }
</style>
</head>
<body>

<!-- ==================== PAGE 1: COVER + CHAPTER 壹 (MAIN MESSAGES & MASTER STRUCTURE MAP) ==================== -->
<div class="header-cover">
  <div class="badge-row">
    <span class="doc-badge">B1 高階決策與策略白皮書 (1:3:25 Executive Strategy Whitepaper)</span>
    <span class="doc-id">DOC-REF: MIT-CDO-20261101-B1 ｜ CIELUV HCL Calibrated</span>
  </div>
  <h1>從流沙到混凝土：生成式 AI 時代的企業數據治理與資產準備度策略</h1>
  <div class="subtitle">Enterprise Data Readiness &amp; Governance Strategy for Generative AI: From Quicksand to Concrete</div>
  <div class="meta-bar">
    <span><strong>實證基準</strong>：Davenport &amp; Tiwari (MIT Sloan / AWS 全球 335 位 CDO 實證研究)</span>
    <span><strong>適用決策層</strong>：董事會 / CEO / CDO / CIO / CTO</span>
    <span><strong>版本</strong>：v2.2 Final (Chapter-Aligned)</span>
  </div>
</div>

<div class="main-message-box">
  <div class="main-message-title">壹、【決策主訊息】破除算力迷思與流沙微調：三大 So-What 戰略行動斷言 (Main Messages)</div>
  <ul class="clean-list">
    <li><span class="bullet-dot">●</span><span class="anchor-tag">【破除資料短缺迷思】</span> — 企業非結構化數據佔比高達 80%～90% 且以年增 50% 指數膨脹，但全球 <span class="highlight-stat">80% 的變革預期僅轉化為 6% 的核心生產落地</span>；高達 <span class="highlight-stat">46% 數據長指認「數據品質不良與多源衝突」為首要死穴</span>。大語言模型無法自動消歧矛盾事實，將未治理的流沙暗數據餵給 AI，只會以極高效率自動化放大組織錯誤。</li>
    <li><span class="bullet-dot">●</span><span class="anchor-tag">【終結提示詞萬能論】</span> — 波蘭尼默會知識悖論證明「人類知道的遠比能說出來的多」，企圖在 Prompt 撰寫窮盡規則必然遭遇組合爆炸與長尾邊緣案例的「自信偽陽性」。企業必須建構 <span class="highlight-good">「剛性左腦（受控本體庫 Ontology、主數據管理 MDM）」&times;「靈性右腦（LLM 高維語義抽取）」&times;「前額葉（領域專家 HITL 仲裁 &lt;5% 邊緣衝突）」</span> 之三層協同體系。</li>
    <li><span class="bullet-dot">●</span><span class="anchor-tag">【非對稱試點破局法】</span> — 高達 <span class="highlight-stat">71% 數據長因傳統數據債未清與跨部門權力爭奪而選擇觀望</span>，57% 至今未修改數據策略。破局之道在於嚴禁直接拿高風險財務或臨床數據試錯，優先切入 <span class="highlight-good">「客服坐席輔助（真人覆核防護網）」與「軟體工程代碼生成（編譯器確定性驗證）」</span> 兩大非對稱優勢場景，於 90 天內跑通治理飛輪。</li>
  </ul>
</div>

<div class="figure-box">
  <div class="figure-header">圖 1（格式 A 全景主圖實體內嵌）：企業數據資產面對生成式 AI 的準備度與治理策略 —— 由淺入深四階全景結構圖</div>
  <img src="01_article_master_structure_map.png" class="figure-img" alt="企業數據準備度與治理策略全景主圖">
  <div class="figure-footnote">
    <strong>全景結構導讀（Ausubel 前導組織體）</strong>：中央脊椎收斂從「看清表面落差」到「挑對起點破局」之四步核心主軸；左右四象限依「淺層現象 &rarr; 中層機制 &rarr; 深層決策」展開表面亂象、深層病因、雙腦系統解法與安全試點步驟。
  </div>
</div>

<!-- ==================== PAGE 2: CHAPTER 貳 (SITUATION DIAGNOSIS + SCQA TABLE + QUANTITATIVE CHART) ==================== -->
<div class="chapter-break"></div>
<h2>貳、【現狀與衝突診斷】為何 80% 投資熱潮僅換來 6% 生產落地：流沙地基引發的全面停滯</h2>
<p>全球企業高層對生成式 AI 抱持空前期待，但絕大多數組織卻困在「個人零星試用」與「局部概念驗證（POC）」的泥沼中無法創造實質經濟價值。下表依據 <strong>Ehrenberg (1977) 科學化三線表規範</strong>，完整收斂 MIT Sloan 針對數據長（CDO）之核心實證與標竿案例對照，並於下方圖 2 呈現統一 Y 軸高度下之準備度留存斷崖：</p>

<table class="ehrenberg">
  <thead>
    <tr>
      <th style="width: 13%;">SCQA 維度</th>
      <th style="width: 37%;">核心組織現實與因果機制推演</th>
      <th style="width: 24%;">關鍵實證統計 (N = 335)</th>
      <th style="width: 26%;">標竿企業正反實踐對照</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="nowrap"><strong>情境<br>(Situation)</strong></td>
      <td>生成式 AI 突破過往僅能處理二維結構化數字表格的限制，開始吞吐文本、語音與影像等非結構化資產，引發董事會空前關注與預算挹注。</td>
      <td>
        <span class="stat-line">• <strong>80%</strong> 預期徹底重構商業</span>
        <span class="stat-line">• <strong>62%</strong> 計畫擴大 AI 經費</span>
        <span class="stat-line">• <strong>93%</strong> 認同數據策略關鍵</span>
      </td>
      <td>數據長（CDO）從幕後走向台前，成為企業數位轉型「舞會上的焦點」。</td>
    </tr>
    <tr>
      <td class="nowrap"><strong>衝突<br>(Complication)</strong></td>
      <td>企業內部非結構化內容長期缺乏治理，跨部門指標互斥、連結失效、版本過期；大模型直接吞食髒數據引發嚴重幻覺級聯與資安封鎖。</td>
      <td>
        <span class="stat-line">• <span class="highlight-stat">僅 6%</span> 部署至核心生產</span>
        <span class="stat-line">• <span class="highlight-stat">46%</span> 視數據品質為死穴</span>
        <span class="stat-line">• <span class="highlight-stat">57%</span> 至今未改數據策略</span>
        <span class="stat-line">• <span class="highlight-stat">16%</span> 因資安下令全面禁用</span>
      </td>
      <td>高達 <strong>89%</strong> 企業停滯於個人摸索（33%）、指引制定（21%）、部門試點（19%）或全面禁用（16%）。</td>
    </tr>
    <tr>
      <td class="nowrap"><strong>核心問題<br>(Question)</strong></td>
      <td>當非結構化數據生成速度以指數級壓倒人工整理速度時，如何在不損失高維語義的前提下，建立零幻覺的「單一真實來源（SSOT）」？</td>
      <td>
        <span class="stat-line">• <strong>僅 37%</strong> 具備 AI 數據基礎</span>
        <span class="stat-line">• <span class="highlight-stat">僅 11%</span> 強烈同意已就緒</span>
        <span class="stat-line">• <strong>71%</strong> 優先處理傳統數據</span>
      </td>
      <td>傳統 ETL 線性處理通量 vs. 非結構化暗數據指數膨脹之結構性剪刀差。</td>
    </tr>
    <tr class="bottom-line">
      <td class="nowrap"><strong>★ 策略解答<br>(Answer)</strong></td>
      <td>放棄「將所有文字壓平為二維表」與「純靠 Prompt 硬解」，轉向「雙腦分層認知架構」＋「非對稱 MVP 試點」雙軌推進。</td>
      <td>
        <span class="stat-line">• <strong>25%</strong> 聚焦數據整合清理</span>
        <span class="stat-line">• <strong>18%</strong> 盤點高價值數據集</span>
        <span class="stat-line">• <strong>17%</strong> 啟動領域文本策劃</span>
      </td>
      <td>
        <span class="stat-line">• 摩根士丹利：5 年審核評分體系</span>
        <span class="stat-line">• 默克與賽諾菲：混凝土地基架構</span>
      </td>
    </tr>
  </tbody>
</table>

<div class="figure-box">
  <div class="figure-header">圖 2（格式 D 量化圖表實體內嵌）：2024 全球數據長調查實證 —— 80% 商業預期崩跌至 6% 核心投產之「空間重力折線斷崖與雙圖接力全景」</div>
  <img src="03_cdo_survey_quantitative_charts.png" class="figure-img" alt="MIT Sloan CDO 調查量化全景圖">
  <div class="figure-footnote">
    <strong>統計與視覺解讀（Tversky 空間重力映射 &amp; Brewer 同質單色相漸層）</strong>：左右雙圖共用相同之 Y 軸高度比例尺（0%～100%）。左圖（皇家藍同質漸層）將反向阻礙換算為正向留存率（54% 品質過關、43% 策略行動），刻劃出從左上 80% 預期一路俯衝至右下 6% 核心投產之單調斷崖（&Delta; = -74%）；右圖（深青綠同質漸層）接力拆解未投產企業之真實去向（73% 停留在早期摸索與部門試點 + 16% 全面禁用）。
  </div>
</div>

<!-- ==================== PAGE 3: CHAPTER 參 (THEORETICAL LIMITS + FORMULA SANDWICH + 3 TRAPS MATRIX) ==================== -->
<div class="chapter-break"></div>
<h2>參、【底層機制與理論壁壘】為何單靠 Prompt 無法取代數據治理：非結構化剪刀差與三大陷阱</h2>
<p>許多技術團隊誤以為只要透過長視窗提示詞（Prompt Engineering）與少樣本範例（Few-Shot In-Context Learning），即可讓大語言模型自動清洗海量內部文件。以下透過<strong>「非結構化數據剪刀差積分方程」</strong>與<strong>「三大深層工程陷阱平行解剖矩陣」</strong>，嚴密論證為何缺乏主數據地基的 AI 必然引發系統性崩潰：</p>

<div class="formula-sandwich">
  <div class="sandwich-top">
    <strong>(上) 直覺問題意識</strong>：傳統結構化資料僅佔企業數據冰山一角（10%～20%），而會議紀錄、客訴工單、合約與研究報告等非結構化文本佔比高達 80%～90%。為何企業不能跳過耗時的底層數據清理，直接把海量歷史檔案丟給大語言模型自動結構化？
  </div>
  <div class="sandwich-mid">
    <div style="font-size: 8.5pt; color: #94A3B8; margin-bottom: 3px;">【非結構化數據剪刀差與技術數據債累積積分方程 (Formula Sandwich Protocol)】</div>
    <div class="math-expr">
      &Delta;<sub>Debt</sub>(<i>t</i>) = &int;<sub>0</sub><sup><i>t</i></sup> <span style="font-size: 14pt;">[</span> &alpha; &middot; <i>e</i><sup>&lambda;&tau;</sup> &minus; ( &beta;<sub>human</sub> &middot; <i>M</i>(&tau;) + &gamma;<sub>AI</sub> &middot; <i>I</i><sub>MDM</sub>(&tau;) ) <span style="font-size: 14pt;">]</span> <i>d</i>&tau;
    </div>
  </div>
  <div class="sandwich-bot">
    <strong>(下) 參數物理意義與極端邊界推演</strong>：<br>
    • <strong>&alpha; &middot; e<sup>&lambda;&tau;</sup></strong>：企業非結構化暗數據之指數生成速率（年複合增長率 &lambda; &ge; 50%）；<strong>&beta;<sub>human</sub> &middot; M(&tau;)</strong>：純依賴人工審核與傳統關聯式 Schema 的線性處理通量。<br>
    • <strong>&gamma;<sub>AI</sub> &middot; I<sub>MDM</sub>(&tau;)</strong>：導入大模型弱監督抽取之有效治理通量，其槓桿倍數直接受制於<strong>底層主數據架構完備度指標 I<sub>MDM</sub> &isin; [0, 1]</strong>。<br>
    • <strong>極端邊界推演</strong>：當企業未建立主數據標準與受控詞表（<strong>I<sub>MDM</sub> &rarr; 0</strong>）時，有效 AI 治理項歸零，隨時間 <strong>t &rarr; &infin;，數據債 &Delta;<sub>Debt</sub>(t) &rarr; +&infin;</strong>（淪為流沙數據沼澤）；唯有先打造剛性主數據地基（<strong>I<sub>MDM</sub> &rarr; 1</strong>），方能觸發 &gamma;<sub>AI</sub> &gg; &alpha; 之自動化治理飛輪。
  </div>
</div>

<div class="figure-box" style="background-color: #FFFFFF;">
  <div class="figure-header">圖 3（原生向量結構圖）：為何單靠 Prompt 必然失效 —— 三大深層工程陷阱平行解剖矩陣（淺層機制 &rarr; 中層失效 &rarr; 深層對策）</div>
  <table class="parallel-grid-table">
    <tr>
      <td class="card-header" style="width: 33.3%; background-color: #AC1953; color: #FFFFFF;">陷阱一：波蘭尼悖論與長尾偽陽性</td>
      <td class="card-header" style="width: 33.3%; background-color: #9C5100; color: #FFFFFF;">陷阱二：局部抽取 vs. 全局實體斷層</td>
      <td class="card-header" style="width: 33.3%; background-color: #1A48A0; color: #FFFFFF;">陷阱三：資訊壓平損耗 vs. 後設缺失</td>
    </tr>
    <tr>
      <td class="card-row b-crimson" style="background-color: #FEECF0;">
        <strong>● 【淺層直覺：有些事只可意會】</strong>波蘭尼悖論指出「人類知道的遠比能說出來的多」。<span class="nowrap">Few-Shot</span> 範例僅能覆蓋 80% 常態分布，無法窮盡隱含法規與歷史默會脈絡。
      </td>
      <td class="card-row b-ochre" style="background-color: #FBF1EA;">
        <strong>● 【淺層直覺：看單篇都很合理】</strong>大模型擅長在「單篇文檔」內以 98% 準確率提取欄位，但天生缺乏跨 10 萬份檔案的「全局實體唯一性校驗（Entity Resolution）」能力。
      </td>
      <td class="card-row b-blue" style="background-color: #EEF3FE;">
        <strong>● 【淺層直覺：硬塞表格反失真】</strong>生成式 AI 的革命性優勢在於高維潛在向量空間（Embeddings）的語境理解；強行將所有文本壓平回二維表格屬於降維倒退。
      </td>
    </tr>
    <tr>
      <td class="card-row b-crimson" style="background-color: #FFFFFF;">
        <strong>● 【中層失效：不懂裝懂最致命】</strong>遇到 20% 罕見長尾合約（如特殊違約豁免條款）時，模型不會承認不懂，而是<strong>極度自信地硬套常規範本</strong>，輸出格式完美但語意相反的致命錯誤。
      </td>
      <td class="card-row b-ochre" style="background-color: #FFFFFF;">
        <strong>● 【中層失效：同名不同人亂成團】</strong>文件 A 寫「台積電」、文件 B 寫「TSMC」、文件 C 寫「3nm 專案組」且記載信用額度互斥，LLM 無法判定何者為最新權威事實，導致資料庫自相矛盾。
      </td>
      <td class="card-row b-blue" style="background-color: #FFFFFF;">
        <strong>● 【中層失效：抹殺語氣與急迫度】</strong>將客戶投訴錄音壓成「情緒：負面、類別：退貨」兩個死板欄位，徹底抹殺了語氣急迫度、潛在訴訟威脅與細微產品缺陷脈絡。
      </td>
    </tr>
    <tr>
      <td class="card-footer b-crimson-foot" style="background-color: #FEECF0; color: #881337;">
        ★ 深層對策：設置 90% 置信度閘門，攔截 &lt;5% 長尾難題轉交前額葉人類專家仲裁。
      </td>
      <td class="card-footer b-ochre-foot" style="background-color: #FBF1EA; color: #7C2D12;">
        ★ 深層對策：建立剛性「主數據管理（MDM）」與受控本體庫，鎖定單一真實來源。
      </td>
      <td class="card-footer b-blue-foot" style="background-color: #EEF3FE; color: #1E3A8A;">
        ★ 深層對策：保留原文高維向量，改為治理「後設資料層（時效、權威度、評分）」。
      </td>
    </tr>
  </table>
</div>

<!-- ==================== PAGE 4: CHAPTER 肆 (BICAMERAL ARCHITECTURE + EHRENBERG COMPARISON TABLE) ==================== -->
<div class="chapter-break"></div>
<h2>肆、【破局系統架構】雙腦分層認知系統與 Ehrenberg 科學對照實證</h2>
<p>為同時達成「100% 事實零幻覺」與「海量非結構化文本之高維語義理解」，企業必須建構仿生學之<strong>「雙腦分層認知架構（Bicameral Cognitive Architecture）」</strong>，將確定性規則與機率性生成嚴格解耦：</p>

<div class="figure-box" style="background-color: #F8FAFC;">
  <div class="figure-header">圖 4（原生向量拓撲圖）：現代企業數據準備度之「雙腦分層認知架構與前額葉仲裁迴路」</div>
  <div class="bicameral-diagram">
    <div class="prefrontal-box">
      <div style="font-weight: 800; font-size: 9.6pt; color: #9C5100;">【前額葉：Human-in-the-Loop 領域專家與知識策劃人 (Knowledge Curator)】</div>
      <div style="font-size: 8.8pt; color: #1E293B; margin-top: 2px; line-height: 1.50;">
        • <strong>置信度路由閘門（Confidence Gate）</strong>：95% 高置信度樣本自動放行；僅攔截 <strong>&lt; 5% 跨文件衝突或長尾罕見案例</strong> 由人類專家拍板。<br>
        • <strong>雙向動態反哺飛輪</strong>：專家每次仲裁結果，同步更新「左腦受控本體詞庫」並追加為「右腦 <span class="nowrap">Few-Shot</span> 黃金範例」。
      </div>
    </div>

    <div class="brain-connector">
      ▲ 衝突升級攔截 (置信度 &lt; 90%) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ▼ 權威規則下發與黃金範例反哺
    </div>

    <table class="parallel-grid-table" style="margin-bottom: 0;">
      <tr>
        <td class="card-header" style="width: 47.5%; background-color: #1A48A0; color: #FFFFFF;">
          【剛性左腦：確定性數據地基 (Deterministic Core)】
        </td>
        <td style="width: 5%; text-align: center; vertical-align: middle; font-weight: 800; color: #0F172A; font-size: 8.4pt;">
          實體<br>校驗<br>◄═►<br>語義<br>對齊
        </td>
        <td class="card-header" style="width: 47.5%; background-color: #006B58; color: #FFFFFF;">
          【靈性右腦：高維語義大模型 (Probabilistic LLM)】
        </td>
      </tr>
      <tr>
        <td class="card-row b-blue" style="background-color: #EEF3FE;">
          <strong>1. 受控本體詞庫 (Ontology)</strong>：統一部門術語與指標定義，消滅同名異義與部門穀倉。
        </td>
        <td></td>
        <td class="card-row b-teal" style="background-color: #EAF4F1;">
          <strong>1. 多模態非結構化吞吐</strong>：直接理解文本、語音、合約與財報之隱含語境與情緒。
        </td>
      </tr>
      <tr>
        <td class="card-row b-blue" style="background-color: #FFFFFF;">
          <strong>2. 主數據管理 (MDM / SSOT)</strong>：鎖定跨 10 萬份文檔之唯一權威事實版本，拒絕多頭矛盾。
        </td>
        <td></td>
        <td class="card-row b-teal" style="background-color: #FFFFFF;">
          <strong>2. 弱監督實體與關係抽取</strong>：依左腦定義之 Schema 自動抽取候選結構化標籤與血緣。
        </td>
      </tr>
      <tr>
        <td class="card-row b-blue" style="background-color: #EEF3FE;">
          <strong>3. 後設資料與數據經緯 (Data Fabric)</strong>：標註時效戳記、作者權威度與審核分數（對標摩根士丹利與默克混凝土架構）。
        </td>
        <td></td>
        <td class="card-row b-teal" style="background-color: #EAF4F1;">
          <strong>3. 高維向量嵌入與檢索生成 (GraphRAG)</strong>：保留微觀脈絡，拒絕粗暴二維表格壓平損耗。
        </td>
      </tr>
      <tr>
        <td class="card-footer b-blue-foot" style="background-color: #DBEAFE; color: #1E3A8A;">
          ★ 物理特性：100% 確定性演算法、零幻覺、扮演「企業事實憲法」。
        </td>
        <td></td>
        <td class="card-footer b-teal-foot" style="background-color: #D1FAE5; color: #065F46;">
          ★ 物理特性：高泛化力、強聯想匹配、受左腦本體庫嚴格邊界約束。
        </td>
      </tr>
    </table>
  </div>
</div>

<h3>二、 Ehrenberg 科學化架構對照表：三種數據整理與治理模式之極限檢驗</h3>
<table class="ehrenberg">
  <thead>
    <tr>
      <th style="width: 25%;">評估維度與核心指標</th>
      <th class="num-col" style="width: 25%;">模式 A：純人工專家整理<br><span style="font-weight: 400; font-size: 8.0pt; color: #64748B;">(傳統精英工匠模式)</span></th>
      <th class="num-col" style="width: 25%;">模式 B：純 Prompt / Few&#8209;Shot<br><span style="font-weight: 400; font-size: 8.0pt; color: #64748B;">(輕信技術直覺模式)</span></th>
      <th class="num-col" style="width: 25%;">模式 C：雙腦分層人機協同<br><span style="font-weight: 400; font-size: 8.0pt; color: #1A48A0;">(現代數據工程最佳實踐)</span></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="nowrap"><strong>1. 單位文檔治理成本</strong></td>
      <td class="num-col">$45 / 篇 (極高昂)</td>
      <td class="num-col">$0.02 / 篇 (極低廉)</td>
      <td class="num-col"><strong>$1.2 / 篇 (最適成本效益)</strong></td>
    </tr>
    <tr>
      <td class="nowrap"><strong>2. 單日處理通量上限</strong></td>
      <td class="num-col">20 篇 / 人 (線性瓶頸)</td>
      <td class="num-col">50,000 篇 (無校驗狂奔)</td>
      <td class="num-col"><strong>10,000 篇 (受控高通量)</strong></td>
    </tr>
    <tr>
      <td class="nowrap"><strong>3. 長尾案例幻覺錯誤率</strong></td>
      <td class="num-col">&lt; 0.5% (專家嚴格把關)</td>
      <td class="num-col"><span class="highlight-stat">18% (高且具隱蔽偽陽性)</span></td>
      <td class="num-col"><span class="highlight-good">&lt; 1.0% (前額葉閘門攔截)</span></td>
    </tr>
    <tr>
      <td class="nowrap"><strong>4. 跨來源實體消歧準確率</strong></td>
      <td class="num-col">65% (受限人腦記憶跨度)</td>
      <td class="num-col"><span class="highlight-stat">12% (完全缺乏全局校驗)</span></td>
      <td class="num-col"><span class="highlight-good">95% (左腦 MDM 圖譜對齊)</span></td>
    </tr>
    <tr>
      <td class="nowrap"><strong>5. 高維非結構化語義保留</strong></td>
      <td class="num-col">40% (人工摘要丟失細節)</td>
      <td class="num-col">30% (強行壓平二維表損耗)</td>
      <td class="num-col"><span class="highlight-good">88% (向量嵌入 + Metadata)</span></td>
    </tr>
    <tr>
      <td class="nowrap"><strong>6. 組織建置與見效週期</strong></td>
      <td class="num-col">3～5 年 (緩慢累積)</td>
      <td class="num-col">1 週 (上線即埋下數據債)</td>
      <td class="num-col"><strong>3～6 個月 (分領域漸進飛輪)</strong></td>
    </tr>
    <tr class="bottom-line">
      <td class="nowrap"><strong>★ 核心決策收斂底線</strong></td>
      <td class="num-col">僅適用於頂級合規資產</td>
      <td class="num-col" style="color: #AC1953;">★ 嚴禁單獨用於核心生產</td>
      <td class="num-col" style="color: #006B58;">★ 跨越 6% 生產鴻溝唯一正解</td>
    </tr>
  </tbody>
</table>

<!-- ==================== PAGE 5: CHAPTER 伍 (MVP ROADMAP + GANTT MATRIX + RACI MATRIX) ==================== -->
<div class="chapter-break"></div>
<h2>伍、【落地路線圖與權責矩陣】破除 71% 組織觀望：非對稱 MVP 試點與 18 個月推進計畫</h2>
<p>調查顯示高達 <strong>71% 數據長坦言「目前更重視從其他傳統數據方案取得實際價值」</strong>，主因在於傳統結構化數據債未清、CDO/CIO/CTO 主導權爭奪內耗，以及恐懼大模型出錯引發合規災難。企業切忌試圖一次性清理全公司所有非結構化數據，必須優先鎖定<strong>具備天然安全網與確定性反饋</strong>的兩大非對稱優勢領域：</p>
<ul class="clean-list">
  <li><span class="bullet-dot">●</span><span class="anchor-tag">【第一優先：顧客經營（客服坐席輔助）】</span> — AI 檢索內部知識庫並草擬回覆，但<strong>由真人客服坐席先覆核再發送給客戶（天然 Human-in-the-Loop 防火牆）</strong>，外部合規風險趨近於零，且能立即縮短 30% 案件查找與通話處置時間。</li>
  <li><span class="bullet-dot">●</span><span class="anchor-tag">【第二優先：軟體工程（代碼生成輔助）】</span> — 具備<strong>編譯器（Compiler）、語法檢查器（Linter）與自動化單元測試組成的「毫秒級確定性驗證迴圈」</strong>，AI 生成的程式碼好壞瞬間見真章（如環球音樂亦於核心研發探索受版權保護之 AI 協作）。</li>
</ul>

<div class="figure-box" style="background-color: #FFFFFF;">
  <div class="figure-header">圖 5（原生向量甘特矩陣）：企業生成式 AI 數據準備度 18 個月三階段漸進式落地路線圖</div>
  <table class="ehrenberg" style="margin: 3px 0 0 0;">
    <thead>
      <tr>
        <th style="width: 24%;">轉型階段與核心目標</th>
        <th style="width: 37%;">關鍵交付物與數據工程行動</th>
        <th class="num-col" style="width: 13%;">M1–M4</th>
        <th class="num-col" style="width: 13%;">M5–M10</th>
        <th class="num-col" style="width: 13%;">M11–M18</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="nowrap"><strong>Phase 1：地基盤點與詞庫</strong><br><span style="font-size: 8pt; color: #1A48A0;">(對標 18% 先行者盤點實踐)</span></td>
        <td>
          <span class="stat-line">• 盤點高價值非結構化數據，剔除失效連結</span>
          <span class="stat-line">• 編纂首部業務受控本體詞庫與品質評分卡</span>
        </td>
        <td class="num-col"><div class="gantt-bar-bg"><div class="gantt-fill-1" style="width: 100%;"></div></div><span style="font-size: 7.8pt; color: #1A48A0; font-weight: 700;">100% 集中攻堅</span></td>
        <td class="num-col"><div class="gantt-bar-bg"><div class="gantt-fill-1" style="width: 35%;"></div></div><span style="font-size: 7.8pt; color: #64748B;">持續迭代</span></td>
        <td class="num-col"><span style="font-size: 7.8pt; color: #94A3B8;">常態維運</span></td>
      </tr>
      <tr>
        <td class="nowrap"><strong>Phase 2：雙軌 MVP 與經緯</strong><br><span style="font-size: 8pt; color: #9C5100;">(對標默克 Data Fabric 基建)</span></td>
        <td>
          <span class="stat-line">• 上線「客服輔助」與「代碼生成」雙試點</span>
          <span class="stat-line">• 部署後設資料層與 &lt;5% 專家仲裁閘門</span>
        </td>
        <td class="num-col"><span style="font-size: 7.8pt; color: #94A3B8;">環境準備</span></td>
        <td class="num-col"><div class="gantt-bar-bg"><div class="gantt-fill-2" style="width: 100%;"></div></div><span style="font-size: 7.8pt; color: #9C5100; font-weight: 700;">雙試點上線驗證</span></td>
        <td class="num-col"><div class="gantt-bar-bg"><div class="gantt-fill-2" style="width: 50%;"></div></div><span style="font-size: 7.8pt; color: #64748B;">跨部門擴展</span></td>
      </tr>
      <tr class="bottom-line">
        <td class="nowrap"><strong>★ Phase 3：主數據規模生產</strong><br><span style="font-size: 8pt; color: #006B58;">(對標摩根士丹利與賽諾菲)</span></td>
        <td>
          <span class="stat-line">• 打通跨部門實體消歧與企業級 GraphRAG</span>
          <span class="stat-line">• 全面賦能行銷與研發核心，跨越 6% 鴻溝</span>
        </td>
        <td class="num-col"><span style="font-size: 7.8pt; color: #94A3B8;">架構設計</span></td>
        <td class="num-col"><div class="gantt-bar-bg"><div class="gantt-fill-3" style="width: 30%;"></div></div><span style="font-size: 7.8pt; color: #64748B;">局部對接</span></td>
        <td class="num-col"><div class="gantt-bar-bg"><div class="gantt-fill-3" style="width: 100%;"></div></div><span style="font-size: 7.8pt; color: #006B58; font-weight: 800;">★ 核心生產落地</span></td>
      </tr>
    </tbody>
  </table>
</div>

<h3>二、 跨職能 RACI 權責劃分矩陣（終結 CDO / CIO / CTO 多頭馬車內耗）</h3>
<table class="ehrenberg">
  <thead>
    <tr>
      <th style="width: 32%;">轉型里程碑與核心治理任務</th>
      <th class="num-col" style="width: 17%;">數據長 (CDO)</th>
      <th class="num-col" style="width: 17%;">資訊/技術長 (CIO)</th>
      <th class="num-col" style="width: 17%;">業務專家 (Curator)</th>
      <th class="num-col" style="width: 17%;">法務合規長 (CLO)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="nowrap"><strong>1. 業務受控本體詞表 (Ontology) 定義</strong></td>
      <td class="num-col"><strong>A (主責審定)</strong></td>
      <td class="num-col">C (相容性諮詢)</td>
      <td class="num-col"><strong>R (撰寫領域詞條)</strong></td>
      <td class="num-col">C (合規術語審查)</td>
    </tr>
    <tr>
      <td class="nowrap"><strong>2. 數據經緯 (Data Fabric) 與向量基建</strong></td>
      <td class="num-col">C (定義治理規格)</td>
      <td class="num-col"><strong>A / R (架構實施)</strong></td>
      <td class="num-col">I (知會存取介面)</td>
      <td class="num-col">C (資安邊界審核)</td>
    </tr>
    <tr>
      <td class="nowrap"><strong>3. 非對稱 MVP 試點 (客服/代碼) 選型</strong></td>
      <td class="num-col"><strong>A (價值統籌)</strong></td>
      <td class="num-col">R (API 模型整合)</td>
      <td class="num-col"><strong>R (業務場景實測)</strong></td>
      <td class="num-col">I (知會上線範圍)</td>
    </tr>
    <tr>
      <td class="nowrap"><strong>4. 前額葉人機迴路 (HITL) 衝突仲裁</strong></td>
      <td class="num-col">R (設計評分流)</td>
      <td class="num-col">I (提供標註工具)</td>
      <td class="num-col"><strong>A / R (專家仲裁)</strong></td>
      <td class="num-col">C (免責版權界定)</td>
    </tr>
    <tr class="bottom-line">
      <td class="nowrap"><strong>★ 5. 主數據管理 (MDM) 單一真理鎖定</strong></td>
      <td class="num-col"><strong>★ A / R (唯一真理)</strong></td>
      <td class="num-col"><strong>R (管線強制對齊)</strong></td>
      <td class="num-col"><strong>C (跨部門協商)</strong></td>
      <td class="num-col"><strong>I (稽核軌跡備查)</strong></td>
    </tr>
  </tbody>
</table>

<!-- ==================== PAGE 6: CHAPTER 陸 (BICAMERAL DEEP-DIVE DIAGRAM + EXECUTIVE CLOSING SEAL) ==================== -->
<div class="chapter-break"></div>
<h2>陸、【終章收束與立即行動檢核】雙腦落地三層流程全圖、董事會黃金鐵律與星期一啟動清單</h2>
<p>為確保技術與業務團隊在執行時具備一致的工程藍圖，下圖 6 完整展開「剛性左腦 &times; 中間裁判 &times; 靈性右腦」從標準字典建立、跨檔案消歧到安全試點上線之三層九宮格實作流程，並於底部收斂董事會立即行動檢核清單：</p>

<div class="figure-box">
  <div class="figure-header">圖 6（格式 A 專題圖譜實體內嵌）：企業資料「左右腦分工」與安全落地三層流程圖 (Bicameral Data Architecture &amp; Governance Pipeline)</div>
  <img src="02_bicameral_data_architecture.png" class="figure-img" alt="企業資料左右腦分工與安全落地三層流程圖">
  <div class="figure-footnote">
    <strong>專題架構導讀</strong>：橫向對應「第 1 層：統一標準字典與語境保留 &rarr; 第 2 層：唯一客戶名冊與專家拍板 &rarr; 第 3 層：文件身分證過濾與自帶安全網雙試點」；縱向展現左腦死規矩、中間真人裁判與右腦活聯想之閉環協同。
  </div>
</div>

<div class="closing-seal">
  <div style="font-weight: 800; font-size: 10.2pt; color: #FFFFFF; border-bottom: 1px solid #334155; padding-bottom: 4px;">
    ★ 終章決策收束：董事會三大黃金鐵律與「星期一立即啟動」四步檢核清單 (Executive Closing &amp; Action Seal)
  </div>
  <div class="closing-grid">
    <div class="closing-subbox">
      <div class="closing-subbox-title">★ 董事會與高階主管「三大黃金決策鐵律」</div>
      <div style="margin-bottom: 4px;"><strong>1. 數據治理非事後補丁</strong>：大模型只是燃油，經過審核、具備單一真實來源（SSOT）與後設資料的企業知識庫才是引擎。</div>
      <div style="margin-bottom: 4px;"><strong>2. 左腦與右腦缺一不可</strong>：不建立外部本體詞庫與 MDM，企圖只靠 Prompt 微調解決數據混亂，如同在流沙上蓋摩天大樓。</div>
      <div><strong>3. 短反饋試點啟動飛輪</strong>：拒絕拿高風險核心資產裸奔；從客服與代碼生成切入，邊創造實質價值邊償還非結構化數據債。</div>
    </div>
    <div class="closing-subbox">
      <div class="closing-subbox-title">☑ 決策層「星期一立即啟動」四步檢核清單</div>
      <div style="margin-bottom: 4px;"><strong>[ &check; ] Step 1｜終結權力爭奪</strong>：召開 CDO-CIO-BU 聯席會，簽署 RACI 矩陣，確立 CDO 最終數據審定權。</div>
      <div style="margin-bottom: 4px;"><strong>[ &check; ] Step 2｜凍結盲目微調</strong>：立即暫停將未清洗、未標註時效與權威度之歷史文檔直接灌入模型微調。</div>
      <div style="margin-bottom: 4px;"><strong>[ &check; ] Step 3｜編纂首部本體庫</strong>：指派知識策劃人（Curator）於 60 天內完成首個業務領域受控詞表。</div>
      <div><strong>[ &check; ] Step 4｜立項雙軌 MVP</strong>：啟動 90 天「客服輔助」或「代碼生成」試點，強制綁定真人覆核迴路。</div>
    </div>
  </div>
</div>

<div class="sign-off-footer">
  <span>核准簽署：企業 AI 與數據治理轉型委員會 (CDO / CIO / CTO Joint Steering Committee)</span>
  <span>機密等級：內部高階決策專用 (Executive Eyes Only)</span>
</div>

</body>
</html>
"""

output_dir = os.path.abspath("reading_sessions/20261101_企業數據與生成式AI準備度/02_outputs")
html_path = os.path.join(output_dir, "01_executive_strategy_report.html")
pdf_path = os.path.join(output_dir, "01_executive_strategy_report.pdf")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"[OK] Temporary W3C CLREQ HTML written to: {html_path}")

chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
temp_profile = tempfile.mkdtemp(prefix="chrome_pdf_")
temp_pdf = os.path.join(temp_profile, "output.pdf")

if os.path.exists(chrome_path):
    cmd = [
        "powershell", "-Command",
        f'Start-Process -FilePath "{chrome_path}" -ArgumentList "--headless=new", "--disable-gpu", "--user-data-dir={temp_profile}", "--print-to-pdf={temp_pdf}", "--no-pdf-header-footer", "{html_path}" -Wait'
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(temp_pdf) and os.path.getsize(temp_pdf) > 1000:
        try:
            shutil.copyfile(temp_pdf, pdf_path)
            print(f"[OK] Publication-grade PDF compiled to: {pdf_path} (Size: {os.path.getsize(pdf_path):,} bytes)")
        except PermissionError:
            fallback_pdf = os.path.abspath(r"C:\Users\User\.gemini\antigravity\brain\768c9608-42ca-4d16-9c26-9f6299016f4f\01_executive_strategy_report_preview.pdf")
            shutil.copyfile(temp_pdf, fallback_pdf)
            print(f"[LOCKED] {pdf_path} is currently open in a PDF viewer. Saved preview to: {fallback_pdf} (Size: {os.path.getsize(fallback_pdf):,} bytes)")
    else:
        print(f"[FAIL] PDF compilation failed: {res.stderr}")
else:
    print(f"[WARN] Chrome not found at {chrome_path}")

shutil.rmtree(temp_profile, ignore_errors=True)

if os.path.exists(html_path):
    os.remove(html_path)
    print(f"[CLEAN] Removed intermediate HTML file: {html_path}")
