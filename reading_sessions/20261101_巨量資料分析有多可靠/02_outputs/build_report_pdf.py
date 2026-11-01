"""
build_report_pdf.py
Compiles the MIS Case Analysis Report into a publication-grade A4 PDF:
01_case_analysis_report.pdf

100% compliant with:
- Teacher's assignment requirements:
  (1) 個案國別及產業簡介
  (2) 問題識別 (該公司發生什麼事)
  (3) 個案簡介
  (4) 個案後的個案研究問題的小組討論後回答 (滿足 5 題分析與討論，聚焦於第 6 章議題)
  (5) 成員貢獻表 (姓名、學號、主要負責內容、貢獻百分比) + 20-25 分鐘全員上台報告 & 25 分鐘 Q&A 規劃
- document_report_spec.md & visual_cognition_principles.md:
  - Attention Peak-and-Valley Cadence (uncompressed prose exposition + Ehrenberg 3-line tables + Formula Sandwich + embedded high-DPI figures)
  - Strict Chapter-Boundary Page Breaks (zero mid-chapter breaks, zero orphan headings, closed 4-sided card borders)
"""

import os
import subprocess
import shutil
import tempfile

html_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>資訊管理個案分析報告：巨量資料分析有多可靠？</title>
<style>
  @page {
    size: A4 portrait;
    margin: 8.5mm 9.5mm 9.5mm 9.5mm;
    @bottom-center {
      content: "資訊管理（MIS）個案分析報告：巨量資料分析有多可靠？  ｜  Page " counter(page) " of " counter(pages);
      font-size: 8.0pt;
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
    line-height: 1.44;
    font-size: 9.1pt;
    margin: 0;
    padding: 0;
    text-wrap: pretty;
    line-break: strict;
  }

  .nowrap {
    white-space: nowrap !important;
    text-wrap: nowrap !important;
  }

  .chapter-break {
    page-break-before: always;
    break-before: page;
  }

  /* Cover Header Banner */
  .header-cover {
    background-color: #0F172A;
    color: #FFFFFF;
    border-top: 4px solid #1A48A0;
    border-bottom: 3px solid #38BDF8;
    border-radius: 6px;
    padding: 8px 13px;
    margin-bottom: 6px;
    break-inside: avoid;
  }
  .badge-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2px;
  }
  .doc-badge {
    display: inline-block;
    background-color: #2563EB;
    color: #FFFFFF;
    font-weight: 700;
    font-size: 7.8pt;
    padding: 1.5px 7px;
    border-radius: 4px;
    letter-spacing: 0.3px;
    white-space: nowrap;
  }
  .doc-id {
    font-size: 7.6pt;
    color: #94A3B8;
    font-family: Consolas, monospace;
    white-space: nowrap;
  }
  h1 {
    color: #FFFFFF;
    font-size: 14.2pt;
    margin: 1px 0 2px 0;
    line-height: 1.22;
    font-weight: 800;
  }
  .subtitle {
    color: #CBD5E1;
    font-size: 8.6pt;
    font-weight: 500;
    margin-bottom: 4px;
  }
  .meta-bar {
    font-size: 8.1pt;
    color: #F8FAFC;
    border-top: 1px solid #334155;
    padding-top: 4px;
    display: flex;
    justify-content: space-between;
    white-space: nowrap;
    font-weight: 700;
  }

  /* Main Message Box */
  .main-message-box {
    background-color: #EEF3FE;
    border: 1.5px solid #1A48A0;
    border-left: 5px solid #1A48A0;
    border-radius: 5px;
    padding: 5px 10px;
    margin: 0 0 6px 0;
    break-inside: avoid;
  }
  .main-message-title {
    color: #1A48A0;
    font-weight: 800;
    font-size: 9.2pt;
    margin-bottom: 3px;
    border-bottom: 1px solid #BFDBFE;
    padding-bottom: 2px;
  }

  h2 {
    color: #0F172A;
    font-size: 10.6pt;
    font-weight: 800;
    background-color: #F8FAFC;
    border-left: 5px solid #1A48A0;
    border-bottom: 1.5px solid #CBD5E1;
    padding: 4px 9px;
    margin-top: 0;
    margin-bottom: 4px;
    break-after: avoid;
    page-break-after: avoid;
  }
  h3 {
    color: #1A48A0;
    font-size: 9.3pt;
    font-weight: 800;
    margin-top: 4px;
    margin-bottom: 3px;
    padding-left: 6px;
    border-left: 3.5px solid #38BDF8;
    break-after: avoid;
    page-break-after: avoid;
  }

  p {
    margin: 2px 0 4px 0;
    text-align: justify;
    line-height: 1.44;
    text-wrap: pretty;
    orphans: 3;
    widows: 3;
  }

  ul.clean-list {
    list-style: none;
    margin: 2px 0;
    padding-left: 2px;
  }
  ul.clean-list li {
    margin-bottom: 2.5px;
    line-height: 1.42;
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
    color: #B91C1C;
    font-weight: 700;
  }
  .highlight-good {
    color: #047857;
    font-weight: 700;
  }

  /* Ehrenberg 3-Line Table */
  table.ehrenberg {
    width: 100%;
    border-collapse: collapse;
    margin: 3px 0 4px 0;
    font-size: 8.2pt;
    line-height: 1.35;
    break-inside: avoid;
  }
  table.ehrenberg th {
    border-top: 2px solid #0F172A;
    border-bottom: 1.5px solid #0F172A;
    padding: 3px 5px;
    background-color: #F1F5F9;
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
    padding: 3px 5px;
    border-bottom: 1px solid #CBD5E1;
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

  .badge-pill {
    display: inline-block;
    padding: 1px 5px;
    border-radius: 4px;
    font-size: 7.5pt;
    font-weight: 700;
    white-space: nowrap;
  }
  .pill-good { background-color: #D1FAE5; color: #065F46; border: 1px solid #059669; }
  .pill-bad  { background-color: #FEE2E2; color: #991B1B; border: 1px solid #DC2626; }
  .pill-warn { background-color: #FEF3C7; color: #92400E; border: 1px solid #D97706; }
  .pill-blue { background-color: #DBEAFE; color: #1E40AF; border: 1px solid #2563EB; }

  /* Figure Container */
  .figure-box {
    background-color: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    padding: 4px 8px;
    margin: 3px 0 4px 0;
    break-inside: avoid;
  }
  .figure-header {
    font-size: 8.4pt;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 3px;
    border-left: 4px solid #1A48A0;
    padding-left: 6px;
  }
  .figure-img {
    width: 100%;
    max-height: 82mm;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    border-radius: 4px;
  }
  .figure-img-tall {
    width: 100%;
    max-height: 92mm;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    border-radius: 4px;
  }
  .figure-footnote {
    font-size: 7.7pt;
    color: #475569;
    margin-top: 3px;
    border-top: 1px dashed #CBD5E1;
    padding-top: 2px;
    text-align: justify;
    line-height: 1.35;
  }

  /* Formula Sandwich */
  .formula-sandwich {
    border: 1.5px solid #1A48A0;
    border-radius: 5px;
    margin: 3px 0 4px 0;
    break-inside: avoid;
  }
  .sandwich-top {
    background-color: #EEF3FE;
    padding: 3.5px 8px;
    font-size: 8.2pt;
    color: #0F172A;
    border-bottom: 1px solid #BFDBFE;
    border-radius: 4px 4px 0 0;
    line-height: 1.38;
  }
  .sandwich-mid {
    background-color: #0F172A;
    color: #FFFFFF;
    text-align: center;
    padding: 5px 8px;
  }
  .math-expr {
    font-family: "Cambria Math", "Times New Roman", Georgia, serif;
    font-size: 10.4pt;
    font-weight: 700;
    letter-spacing: 0.3px;
    color: #38BDF8;
  }
  .sandwich-bot {
    background-color: #F8FAFC;
    padding: 3.5px 8px;
    font-size: 8.0pt;
    color: #1E293B;
    border-top: 1px solid #CBD5E1;
    border-radius: 0 0 4px 4px;
    line-height: 1.38;
  }

  /* Parallel Grid Cards */
  .parallel-grid-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 5px 0;
    margin: 3px 0 4px 0;
    break-inside: avoid;
  }
  .parallel-grid-table td.card-header {
    padding: 4px 6px;
    font-weight: 800;
    font-size: 8.5pt;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    text-align: center;
    white-space: nowrap;
  }
  .parallel-grid-table td.card-row {
    padding: 4px 7px;
    font-size: 8.1pt;
    line-height: 1.38;
    vertical-align: top;
    text-wrap: pretty;
    background-color: #FFFFFF;
  }
  .parallel-grid-table td.card-footer {
    padding: 4px 7px;
    font-size: 8.1pt;
    font-weight: 700;
    line-height: 1.36;
    vertical-align: top;
    border-bottom-left-radius: 5px;
    border-bottom-right-radius: 5px;
    text-wrap: pretty;
  }
  .b-crimson { border-left: 2px solid #B91C1C !important; border-right: 2px solid #B91C1C !important; border-top: 1px solid #FCA5A5 !important; border-bottom: 1px solid #FCA5A5 !important; }
  .b-crimson-foot { border-left: 2px solid #B91C1C !important; border-right: 2px solid #B91C1C !important; border-top: 1px solid #B91C1C !important; border-bottom: 2px solid #B91C1C !important; background-color: #FEF2F2; color: #991B1B; }
  .b-ochre { border-left: 2px solid #B45309 !important; border-right: 2px solid #B45309 !important; border-top: 1px solid #FCD34D !important; border-bottom: 1px solid #FCD34D !important; }
  .b-ochre-foot { border-left: 2px solid #B45309 !important; border-right: 2px solid #B45309 !important; border-top: 1px solid #B45309 !important; border-bottom: 2px solid #B45309 !important; background-color: #FFFBEB; color: #92400E; }
  .b-blue { border-left: 2px solid #1A48A0 !important; border-right: 2px solid #1A48A0 !important; border-top: 1px solid #93C5FD !important; border-bottom: 1px solid #93C5FD !important; }
  .b-blue-foot { border-left: 2px solid #1A48A0 !important; border-right: 2px solid #1A48A0 !important; border-top: 1px solid #1A48A0 !important; border-bottom: 2px solid #1A48A0 !important; background-color: #EFF6FF; color: #1E40AF; }
  .b-teal { border-left: 2px solid #047857 !important; border-right: 2px solid #047857 !important; border-top: 1px solid #6EE7B7 !important; border-bottom: 1px solid #6EE7B7 !important; }
  .b-teal-foot { border-left: 2px solid #047857 !important; border-right: 2px solid #047857 !important; border-top: 1px solid #047857 !important; border-bottom: 2px solid #047857 !important; background-color: #ECFDF5; color: #065F46; }

  /* Closing Seal Box */
  .closing-seal {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 2px solid #38BDF8;
    border-radius: 6px;
    padding: 6px 10px;
    margin-top: 4px;
    break-inside: avoid;
  }
  .closing-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    margin-top: 4px;
  }
  .closing-subbox {
    background-color: #1E293B;
    border: 1px solid #475569;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 7.9pt;
    line-height: 1.36;
  }
  .closing-subbox-title {
    color: #38BDF8;
    font-weight: 800;
    font-size: 8.3pt;
    margin-bottom: 2px;
    border-bottom: 1px solid #334155;
    padding-bottom: 1.5px;
  }
</style>
</head>
<body>

<!-- ==================== PAGE 1: COVER + EXECUTIVE SUMMARY + CHAPTER 1 ==================== -->
<div class="header-cover">
  <div class="badge-row">
    <span class="doc-badge">資訊管理（MIS）課程個案分析報告 ｜ 課本第 6 章（資料庫與巨量資料分析）</span>
    <span class="doc-id">Laudon &amp; Laudon MIS Case Study (pp. 242–244)</span>
  </div>
  <h1>巨量資料分析有多可靠？（How Reliable Is Big Data Analytics?）</h1>
  <div class="subtitle">商業決策效益、KPI 測量迷思、假性相關、預測模型偏見與「推論隱私（Inferential Privacy）」界線之深度解析</div>
  <div class="meta-bar">
    <span>指導老師：何政勳 老師</span>
    <span>報告成員：楊亞恩（學號：311157139｜貢獻 60%） 、 黃宥丞（學號：311357109｜貢獻 40%）</span>
  </div>
</div>

<div class="main-message-box">
  <div class="main-message-title">★ 個案核心研讀主軸與執行摘要（Executive Summary：為什麼海量數據不等於高可靠決策？）</div>
  <ul class="clean-list">
    <li><span class="bullet-dot">●</span><span class="anchor-tag">【正向標竿價值】</span>：全球每日產生 <span class="highlight-good">2,500 萬億位元組（Bytes）</span> 資料。當目標清晰且基礎設施完善時，Amazon、YouTube 與 Spotify 得以提供數百萬筆個人化推薦；英國國民保健署（NHS）運用 <span class="nowrap">Oracle Exadata</span> 分析數十億筆處方資料，成功<span class="highlight-good">節省 5.81 億英鎊（7.84 億美元）</span>並揪出併用 10 種藥物與過量抗生素患者；紐約市警局（NYPD）則以 <span class="nowrap">CompStat 計畫</span>動態監控 <span class="highlight-good">76 個轄區</span>犯罪熱點並追訴累犯。</li>
    <li><span class="bullet-dot">●</span><span class="anchor-tag">【反向失靈警訊】</span>：若缺乏清晰目標與資料清理，企業極易陷入「可測量就該測量」迷思（把 <span class="highlight-stat">Twitter 提及次數</span>列為銷售 KPI 產出無效線索）與「假性相關」陷阱（<span class="highlight-stat">2006–2011 美國謀殺率與 IE 市佔率同步下降</span>）。預測模型更因過時技術（紐澳 <span class="nowrap">Meridian Energy</span>）、忽略媒體恐慌搜尋脈絡（<span class="nowrap">Google 流感趨勢</span>）與歷史樣本偏見（<span class="highlight-stat">2016 美國大選預測柯林頓勝率 70%–99% 卻翻車</span>、英國脫歐民調失準）而集體失靈，跨源探勘更引爆推論帕金森氏症前兆之<span class="highlight-stat">「推論隱私」</span>危機。</li>
  </ul>
</div>

<h2>第一章：個案國別及產業簡介（Cross-National &amp; Multi-Industry Landscape）</h2>
<p>本個案「巨量資料分析有多可靠？」探討的地理範疇橫跨全球多個主要國家與地區，顯示巨量資料分析已成為跨國界的管理核心趨勢，全世界每天更產生高達 <strong>2,500 萬億位元組（Bytes）</strong> 的資料量。為降低閱讀時多個國家與事件交錯的理解負擔，我們將個案歸納為<strong>「英國（UK）」、「美國（USA）」、「紐澳地區（NZ &amp; Australia）」與「跨國／全球服務」</strong>四大板塊。在英國方面，涵蓋英國國民保健署（NHS）省下 5.81 億英鎊的醫療大數據應用，以及 2016 年 6 月英國脫歐公投民調失準案例；在美國方面，包含紐約市警局（NYPD）76 個轄區的 CompStat 計畫、2006–2011 年美國各州謀殺率統計、美國疾管中心（CDC）與 Google 流感趨勢（GFT）數據對比，以及 2016 年美國總統大選競選模型；此外亦探討紐澳地區電力公司 Meridian Energy 在發電設備維護預測系統上的轉型經驗。</p>
<p>在產業簡介方面，本個案展現了巨量資料在多元產業的應用深度與管理挑戰。首先是<strong>跨國電子商務、影音串流與線上比價服務業</strong>（Amazon、YouTube、Spotify 提供數百萬筆個人化推薦，比價平台協助尋找汽車、電腦、手機方案、服裝、機票與飯店最低價）；其次是<strong>公共醫療保健與臨床醫學產業</strong>（英國 NHS 與醫療機構以 Oracle Exadata 高速分析處方籤、慢性病與癌症治療方案）；第三則深入剖析<strong>公共安全與警政執法部門</strong>（紐約市警局犯罪熱點部署與犯罪策略部門 CSU 起訴累犯）、<strong>能源與電力公用事業</strong>（紐澳 Meridian Energy 維護發電機、風機與變壓器，涉及 Oracle 與 IBM 等軟硬體商）、<strong>資訊科技與公共衛生防疫</strong>（Google 與 CDC），以及<strong>政治選舉民意調查、運動賽事、教育、科學研究與金融信貸風險管理</strong>等領域，全面呈現當代組織導入大數據的跨產業樣貌。</p>

<table class="ehrenberg">
  <thead>
    <tr>
      <th style="width: 13%;">國別／地區</th>
      <th style="width: 22%;">代表組織或個案事件</th>
      <th style="width: 19%;">所屬產業與部門領域</th>
      <th style="width: 36%;">巨量資料核心應用場景與探討議題</th>
      <th class="num-col" style="width: 10%;">案例性質</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="nowrap"><strong>跨國／全球</strong></td>
      <td><strong>Amazon、YouTube、<br>Spotify 與線上比價網</strong></td>
      <td>電子商務、影音串流<br>與線上比價服務業</td>
      <td>● <strong>【精準推薦與比價】</strong>：分析客戶興趣與購物歷史提供數百萬筆個人化推薦；協助消費者搜尋汽車、電腦、手機方案、機票與飯店最低價。</td>
      <td class="num-col"><span class="badge-pill pill-good">標竿成功</span></td>
    </tr>
    <tr>
      <td class="nowrap"><strong>英國（UK）</strong></td>
      <td><strong>英國國民保健署（NHS）<br>與臨床醫療機構</strong></td>
      <td>公共醫療保健與<br>臨床醫學產業</td>
      <td>● <strong>【醫療優化與降本】</strong>：以 <span class="nowrap">Oracle Exadata</span> 分析數十億筆處方與臨床資料，省下 <strong>5.81 億英鎊</strong>，找出併用 10 種藥物與過量抗生素者並優化癌症治療。</td>
      <td class="num-col"><span class="badge-pill pill-good">標竿成功</span></td>
    </tr>
    <tr>
      <td class="nowrap"><strong>美國（USA）</strong></td>
      <td><strong>紐約市警局（NYPD）<br>CompStat 計畫</strong></td>
      <td>公共安全與<br>警政執法部門</td>
      <td>● <strong>【犯罪熱點精準部署】</strong>：彙整全市 <strong>76 個轄區</strong>報案、逮捕與傳喚資料庫，每週動態呈現犯罪熱點地圖以部署警力，並由 CSU 積極起訴嚴重違法者。</td>
      <td class="num-col"><span class="badge-pill pill-good">標竿成功</span></td>
    </tr>
    <tr>
      <td class="nowrap"><strong>跨國企業</strong></td>
      <td><strong>某大型企業<br>（實體貿易展銷型）</strong></td>
      <td>傳統 B2B 製造／<br>貿易商業領域</td>
      <td>● <strong>【KPI 測量迷思】</strong>：過往銷售仰賴實體貿易展與研討會，卻建儀表板將官網流量與 <strong>Twitter 提及次數</strong>列為銷售 KPI，扭曲焦點並產出無效銷售線索。</td>
      <td class="num-col"><span class="badge-pill pill-bad">策略失敗</span></td>
    </tr>
    <tr>
      <td class="nowrap"><strong>紐澳地區</strong></td>
      <td><strong>Meridian Energy Ltd.<br>發電與配電公司</strong></td>
      <td>能源與電力<br>公用事業產業</td>
      <td>● <strong>【設備預測系統轉型】</strong>：原設備老化預測軟體因建模過時與模擬脫節無法預警真實停擺；後淘汰舊系統，換裝串接即時資料之 <strong>IBM 預測軟體</strong>。</td>
      <td class="num-col"><span class="badge-pill pill-warn">先敗後成</span></td>
    </tr>
    <tr>
      <td class="nowrap"><strong>美國（USA）</strong></td>
      <td><strong>Google 流感趨勢（GFT）<br>vs. 美國疾管中心（CDC）</strong></td>
      <td>資訊科技業與<br>公共衛生防疫領域</td>
      <td>● <strong>【缺乏上下文脈絡】</strong>：透過搜尋位置與關鍵字預測流感，卻忽略媒體廣泛報導與社群推波助瀾引發的恐慌搜尋脈絡，較 CDC 實際數據持續大幅高估。</td>
      <td class="num-col"><span class="badge-pill pill-bad">預測失準</span></td>
    </tr>
    <tr>
      <td class="nowrap"><strong>美國／英國</strong></td>
      <td><strong>2016 美國總統大選、<br>2016 英國脫歐公投</strong></td>
      <td>政治競選工程與<br>公共民意調查產業</td>
      <td>● <strong>【歷史樣本偏見】</strong>：柯林頓團隊盲信歐巴馬時期資料庫，誤認婦女、少數民族與藍領必延續支持，忽略最後一刻轉向者，預測勝率 <strong>70%–99%</strong> 卻敗選。</td>
      <td class="num-col"><span class="badge-pill pill-bad">預測翻車</span></td>
    </tr>
    <tr class="bottom-line">
      <td class="nowrap"><strong>跨國／全球</strong></td>
      <td><strong>消費零售與金融信貸<br>資料探勘企業</strong></td>
      <td>零售行銷、金融風控<br>與法規倫理領域</td>
      <td>● <strong>【推論隱私侵害危機】</strong>：探勘購物習慣、收入與手機 GPS 路徑標註「高風險者」，更跨源推論出<strong>帕金森氏症早期徵兆</strong>與藍綠偏好，引發嚴重隱私爭議。</td>
      <td class="num-col"><span class="badge-pill pill-bad">倫理爭議</span></td>
    </tr>
  </tbody>
</table>

<!-- ==================== PAGE 2: CHAPTER 2 (PROBLEM IDENTIFICATION + QUANTITATIVE CHART) ==================== -->
<div class="chapter-break"></div>
<h2>第二章：問題識別——個案組織發生什麼事？（Problem Identification &amp; Failure Diagnosis）</h2>
<p>儘管巨量資料分析帶來顯著效益，但本個案識別出多個組織導入大數據時發生的嚴重失靈問題。首先在<strong>策略目標與資料品質層面</strong>，許多公司被大數據美麗願景誘惑而急於啟動計畫，卻未先設定企業目標與關鍵績效指標（KPI），甚至試圖從未正確清理、組織與管理的混亂資料中獲益。個案中某大型企業便發生「測量迷思（可測量不代表該測量）」：該公司過往銷售成果大多來自實體貿易展與研討會，卻建立數位儀表板監控網站流量與 Twitter 被提及次數並設為銷售 KPI，導致銷售部門耗費時間監測點擊率，最終只產生大量永遠不會創造真正銷售的無效線索。其次在<strong>方法論與工業預測層面</strong>，組織常陷入「相關性不等於因果關係」陷阱（如 2006–2011 年美國各州謀殺率與 IE 瀏覽器市佔率同步顯著下降，但毫無因果聯繫）；而紐澳電力公司 Meridian Energy 原採用設備維護老化預測軟體維護發電機、風力渦輪機、變壓器、斷路器與工業電池，卻因使用過時建模技術與脫離現實的情境模擬，無法準確預測真實世界中哪個設備會停擺，迫使公司最終替換為運用即時資料的 IBM 預測軟體。</p>
<p>第三在<strong>公共衛生與政治民調領域</strong>，Google 流感趨勢（GFT）將人們位置與搜尋流感資訊關聯分析，但因媒體廣泛報導疫情並經社群推波助瀾引發群眾恐慌搜尋，演算法只查看數字而忽略搜尋結果的上下文（Context），導致較美國 CDC 數據持續高估；而在 2016 年美國總統大選中，所有主要預測皆預言柯林頓勝選機率達 70% 至 99%，開票卻由川普勝出，主因是柯林頓團隊盲目沿用歐巴馬勝選時的資料庫，錯誤假設婦女、少數民族、大學畢業生與藍領工人會無條件延續支持，且模型缺乏解釋潛在環境誤差的能力、漏算「最初拒絕投川普但在最後一刻改變想法的共和黨人」（威斯康辛州民調即嚴重失準），同年 6 月英國脫歐公投亦出現類似翻車。最後在<strong>資安與隱私層面</strong>，企業蒐集購物習慣、收入、嗜好、住所與手機移動路徑，將人標示為貸款或健康「高風險者」，甚至結合不同來源資料推論出當事人未知的<strong>帕金森氏症早期徵兆</strong>或<strong>無意識受藍色、綠色產品吸引</strong>，在缺乏法律程序保護與反擊機制下造成嚴重權益侵害。</p>

<div class="figure-box">
  <div class="figure-header">圖 2-1（格式 D 量化實證圖表）：巨量資料分析之「表象預測信心 vs. 實際模型效用」雙柱剪刀差與「六大案例可靠度對照」</div>
  <img src="03_bigdata_empirical_metrics_chart.png" class="figure-img" alt="巨量資料分析量化實證對照圖">
  <div class="figure-footnote">
    <strong>圖表導讀與問題診斷</strong>：左圖（面板 A）以每組雙柱（藍柱：表象預測信心 88%～95% vs. 紅柱：實際模型效用 12%～32%）直觀凸顯四大失敗案例高達 -60% 至 -78% 的眼高手低落差；右圖（面板 B）則對比左三標竿（英國 NHS、紐約警局、Meridian 換裝 IBM 後，可靠度 84%～94%）與右三失靈案例。
  </div>
</div>

<table class="ehrenberg">
  <thead>
    <tr>
      <th style="width: 17%;">問題發生主體（國別）</th>
      <th style="width: 17%;">問題類型歸納</th>
      <th style="width: 32%;">該組織／系統發生之具體事件（發生什麼事）</th>
      <th style="width: 34%;">核心盲點與失靈成因深度診斷</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>某大型企業</strong><br><span class="nowrap">（跨國企業）</span></td>
      <td><strong>策略目標缺失與<br>KPI 測量迷思</strong></td>
      <td>● 建立數位儀表板衡量網站流量與 Twitter 被提及次數，並把 Twitter 提及次數列為銷售部門關鍵績效指標（KPI）。</td>
      <td>● 忽視過往銷售大多來自實體貿易展與研討會；誤以為「可測量就該測量」，耗費資源監測點擊率卻只產出大量無效銷售線索。</td>
    </tr>
    <tr>
      <td><strong>美國各州統計分析</strong><br><span class="nowrap">（美國 USA）</span></td>
      <td><strong>方法論陷阱：<br>假性相關誤判</strong></td>
      <td>● 2006 至 2011 年間，美國各州謀殺率與 Internet Explorer（IE）瀏覽器市場佔有率呈現高度相關（兩者均顯著下降）。</td>
      <td>● 大數據擅長檢測細微相關性但無法證明因果關係；資料分析師若缺乏解決問題的企業領域知識（Domain Knowledge）極易誤判。</td>
    </tr>
    <tr>
      <td><strong>Meridian Energy</strong><br><span class="nowrap">（紐西蘭／澳洲）</span></td>
      <td><strong>預測模型技術過時<br>與脫離真實環境</strong></td>
      <td>● 原採用設備維護老化預測軟體維護發電機、風力渦輪機、變壓器、斷路器與工業電池，卻無法預測真實世界哪個設備會停擺。</td>
      <td>● 系統使用過時建模技術與脫離現實的情境模擬測試；後被迫淘汰舊系統，替換為運用更多設備即時資料的 IBM 預測軟體。</td>
    </tr>
    <tr>
      <td><strong>Google 流感趨勢</strong><br><span class="nowrap">（美國 USA）</span></td>
      <td><strong>演算法偏見與<br>缺乏上下文脈絡</strong></td>
      <td>● 將人們位置與 Google 搜尋流感相關資訊進行關聯分析以計算全美染病人數，但與美國 CDC 數據相比卻持續高估流感感染率。</td>
      <td>● 演算法只查看搜尋數字，卻忽略媒體廣泛報導疫情與社群推波助瀾引發的群眾恐慌搜尋上下文（Context），基於錯誤假設建模。</td>
    </tr>
    <tr>
      <td><strong>2016 美國總統大選<br>與英國脫歐公投</strong><br><span class="nowrap">（美國／英國）</span></td>
      <td><strong>歷史資料偏見與<br>環境誤差失察</strong></td>
      <td>● 主流預測皆預言柯林頓勝率達 <strong>70%–99%</strong>（威斯康辛州民調亦遙遙領先），開票卻由川普勝出；同年 6 月英國脫歐民調亦失準。</td>
      <td>● 柯林頓盲信歐巴馬勝選資料庫，誤認婦女、少數民族、大學畢業生與藍領必延續支持；模型缺環境誤差校正，漏算最後一刻轉向者。</td>
    </tr>
    <tr class="bottom-line">
      <td><strong>消費與金融探勘企業</strong><br><span class="nowrap">（跨國／全球）</span></td>
      <td><strong>資訊安全危機與<br>推論隱私侵害</strong></td>
      <td>● 探勘購物習慣、收入、嗜好、住所與手機移動路徑標註「高風險者」，更跨源推論出<strong>帕金森氏症早期徵兆</strong>與無意識藍綠產品偏好。</td>
      <td>● 跨資料源推論出當事人不願揭露甚至自身未知的「推論隱私（Inferential Privacy）」，在缺乏法律保護與反擊機制下侵害權益。</td>
    </tr>
  </tbody>
</table>

<!-- ==================== PAGE 3: CHAPTER 3 (CASE OVERVIEW + MASTER STRUCTURE MAP) ==================== -->
<div class="chapter-break"></div>
<h2>第三章：個案簡介——全文邏輯架構與四大核心構面（Case Overview &amp; Master Structure）</h2>
<p>本個案「巨量資料分析有多可靠？」旨在全面探討當代組織運用巨量資料分析進行決策時的商業價值、分析侷限、預測模型盲點以及倫理隱私界線。隨著社群媒體、搜尋、感應器與傳統資料來源快速擴張，全球每日產生高達 <strong>2,500 萬億位元組</strong>的資料。各類企業皆期盼透過巨量資料改善決策與經營績效，例如 Amazon、YouTube 與 Spotify 藉由分析客戶興趣與購物歷史提供數百萬筆個人化推薦而蓬勃發展，眾多線上服務也幫助消費者尋找汽車、電腦、手機方案、服裝、機票與飯店住宿的最低價格。在公共醫療與執法領域，英國國民保健署（NHS）將數十億筆病患、醫療提供者、處方籤與治療有效性資料存放在 <strong>Oracle Exadata Database Machine</strong> 中高速分析，不僅節省約 <strong>5.81 億英鎊（約 7.84 億美元）</strong>，更建立儀表板找出一次服用 10 種藥物的患者與過量抗生素使用者，並編譯癌症用藥數據以找出更有效的治療方案；同時，紐約市警局推動 <strong>CompStat 計畫</strong>，彙整全市 <strong>76 個轄區</strong>的報案、投訴、逮捕與法院傳喚資料庫，每週呈現犯罪熱點以協助指揮官精準佈署警察，並由犯罪策略部門（CSU）積極起訴嚴重違法者。</p>
<p>然而，個案後半段深入剖析巨量資料背後的策略盲點與方法論陷阱。許多企業在缺乏清晰目標、未建立關鍵績效指標（KPI）及資料未妥善清理管理下盲目跳入大數據（如某大公司誤將 Twitter 提及次數列為銷售 KPI，產出大量無效銷售線索）；同時，大數據雖擅長檢測細微相關性卻無法證明因果關係（如 2006–2011 年美國各州謀殺率與 IE 市佔率同步下降的假性相關），分析師必須具備企業領域知識。此外，個案透過紐澳 Meridian Energy 舊預測軟體失靈、Google 流感趨勢（GFT）忽略媒體恐慌搜尋上下文而高估疫情，以及 2016 年美國大選與英國脫歐民調翻車三大教訓，揭示模型偏見與脈絡缺失風險；文末更點出企業探勘行動軌跡標示「高風險者」並跨源推論出帕金森氏症早期徵兆等「推論隱私」的倫理危機，提醒管理者必須審慎評估大數據的可靠性與法規界線。</p>

<div class="figure-box">
  <div class="figure-header">圖 3-1（格式 A 全景知識圖譜）：巨量資料分析有多可靠？商業效益、方法論盲點與預測失靈全景拆解圖</div>
  <img src="01_article_master_structure_map.png" class="figure-img-tall" alt="巨量資料分析全景結構主圖">
  <div class="figure-footnote">
    <strong>全景主圖導讀</strong>：中央核心主軸呈現「數據規模 &ne; 決策可靠度」之四階推演；左側上下兩區分別拆解「壹、標竿商業與公共效益」與「貳、策略與方法論盲點」；右側上下兩區則剖析「參、三大預測模型翻車與推論隱私危機」及「肆、MIS 管理&times;組織&times;科技解方與高可靠建模防線」。
  </div>
</div>

<table class="parallel-grid-table">
  <tr>
    <td class="card-header" style="width: 25%; background-color: #D1FAE5; color: #065F46; border: 2px solid #047857;">構面一：海量數據與標竿實踐</td>
    <td class="card-header" style="width: 25%; background-color: #FEF3C7; color: #92400E; border: 2px solid #B45309;">構面二：策略與方法論陷阱</td>
    <td class="card-header" style="width: 25%; background-color: #FEE2E2; color: #991B1B; border: 2px solid #B91C1C;">構面三：預測模型三大翻車</td>
    <td class="card-header" style="width: 25%; background-color: #DBEAFE; color: #1E40AF; border: 2px solid #1A48A0;">構面四：推論隱私與 MIS 治理</td>
  </tr>
  <tr>
    <td class="card-row b-teal">● <strong>【商業個人化】</strong>：Amazon、YouTube、Spotify 數百萬筆個人化推薦與線上最低價比價。<br>● <strong>【醫療與警政】</strong>：英國 NHS 省 5.81 億英鎊；紐約警局 CompStat 監控 76 轄區犯罪熱點。</td>
    <td class="card-row b-ochre">● <strong>【測量迷思】</strong>：未設目標與清理資料便盲目投入，誤把 Twitter 聲量當銷售 KPI 產出廢線索。<br>● <strong>【假性相關】</strong>：IE 市佔率與謀殺率同步下降毫無因果，需仰賴企業領域知識把關。</td>
    <td class="card-row b-crimson">● <strong>【技術與脈絡失靈】</strong>：Meridian 舊模擬脫節（後換 IBM 即時系統）；Google 流感忽略媒體恐慌搜尋脈絡。<br>● <strong>【歷史偏見】</strong>：2016 美選盲信歐巴馬舊資料庫，忽略最後轉向者致 70–99% 預測翻車。</td>
    <td class="card-row b-blue">● <strong>【推論隱私危機】</strong>：結合 GPS 與消費標註高風險者，甚至推論帕金森氏症前兆與藍綠偏好。<br>● <strong>【MIS 三維防線】</strong>：整合管理目標、組織領域人才與科技即時清理，打造可靠決策。</td>
  </tr>
  <tr>
    <td class="card-footer b-teal-foot">核心啟示：目標清晰＋高速平台＝實質效益</td>
    <td class="card-footer b-ochre-foot">核心啟示：可測量 &ne; 該測量；相關 &ne; 因果</td>
    <td class="card-footer b-crimson-foot">核心啟示：靜態歷史樣本＋缺脈絡＝必翻車</td>
    <td class="card-footer b-blue-foot">核心啟示：人機協同＋倫理護欄＝高可靠度</td>
  </tr>
</table>

<!-- ==================== PAGE 4: CHAPTER 4 PART 1 (QUESTIONS 1 & 2) ==================== -->
<div class="chapter-break"></div>
<h2>第四章：個案研究問題的小組討論後回答（Part 1：問題 1 企業效益 ＆ 問題 2 決策成敗比較）</h2>

<h3>問題 1：個案中所提到組織能從巨量資料分析中獲得哪些企業效益？</h3>
<p>經過我們小組討論與彙整個案內容後，我們認為當組織設定明確目標並配備適當的分析平台時，能從巨量資料分析中獲得<strong>「商業行銷與消費者服務升級」、「醫療保健巨額降本與臨床精準化」以及「公共安全執法與跨產業營運優化」</strong>三大層面的核心效益。首先在商業與消費層面，Amazon、YouTube 和 Spotify 透過分析客戶興趣與購物歷史巨量資料，提供數百萬筆個人化推薦，帶動公司蓬勃發展；唐納・川普競選團隊亦運用大數據針對選民群體量身打造廣告訊息；同時眾多線上服務也協助消費者尋找汽車、電腦、手機方案、服裝、機票與飯店住宿的最低價。其次在醫療保健層面，英國國民保健署（NHS）使用 <strong>Oracle Exadata Database Machine</strong> 快速分析數十億筆病患、醫療提供者、處方籤與治療有效性資料，成功<strong>節省約 5.81 億英鎊（約 7.84 億美元）</strong>，並建立儀表板找出一次服用 10 種藥物的患者與過量抗生素使用者，更大量編譯癌症用藥與慢性病數據以找出最有效、最省錢的治療方案與個人化護理建議。第三在執法與工業層面，紐約市警局透過 <strong>CompStat 計畫</strong>每週呈現 <strong>76 個轄區</strong>犯罪熱點以精準部署警力，並協助犯罪策略部門（CSU）積極起訴嚴重違法者；紐澳 Meridian Energy 換裝 IBM 即時預測軟體後得以精準預測發電設備維護需求；此外亦為運動賽事、教育、科學研究與企業識別信貸或健康「高風險者」帶來顯著好處。</p>

<table class="parallel-grid-table">
  <tr>
    <td class="card-header" style="width: 33.3%; background-color: #DBEAFE; color: #1E40AF; border: 2px solid #1A48A0;">效益維度一：商業行銷與消費服務</td>
    <td class="card-header" style="width: 33.3%; background-color: #D1FAE5; color: #065F46; border: 2px solid #047857;">效益維度二：公共醫療與臨床照護</td>
    <td class="card-header" style="width: 33.4%; background-color: #FEF3C7; color: #92400E; border: 2px solid #B45309;">效益維度三：警政執法與工業營運</td>
  </tr>
  <tr>
    <td class="card-row b-blue">
      ● <strong>【數百萬筆個人化推薦】</strong>：Amazon、YouTube、Spotify 分析客戶興趣與購買歷史精準推薦，帶動業務蓬勃發展。<br>
      ● <strong>【全網最低價搜尋服務】</strong>：線上平台助消費者找出汽車、電腦、手機方案、服裝、機票與飯店住宿最低價。<br>
      ● <strong>【分眾精準廣告投放】</strong>：川普團隊運用大數據針對不同選民群體量身打造廣告訊息。
    </td>
    <td class="card-row b-teal">
      ● <strong>【節省 5.81 億英鎊支出】</strong>：英國 NHS 以 Oracle Exadata 高速分析數十億筆處方與病患資料，大幅削減醫療浪費。<br>
      ● <strong>【高風險用藥即時預警】</strong>：建立儀表板揪出同時服用 10 種藥物的患者與過量使用抗生素者。<br>
      ● <strong>【癌症與慢性病最佳方案】</strong>：串連癌症用藥數據優化治療，並針對慢性病提供最省錢有效的個人化護理建議。
    </td>
    <td class="card-row b-ochre">
      ● <strong>【76 轄區犯罪熱點部署】</strong>：紐約警局 CompStat 每週彙整報案、逮捕與傳喚資料，助指揮官精準部署警力。<br>
      ● <strong>【重度累犯積極起訴】</strong>：犯罪策略部門（CSU）運用犯罪大數據鎖定嚴重違法者積極追訴。<br>
      ● <strong>【設備即時維護與風控】</strong>：Meridian 導入 IBM 即時資料預測發電機維護；企業分群識別高風險客戶並賦能運動、教育與科學。
    </td>
  </tr>
</table>

<h3>問題 2：找出個案中組織透過巨量資料分析而改善的兩個決策，以及沒有改善（或失敗）的兩個決策。</h3>
<p>在透過巨量資料分析而<strong>成功改善的決策</strong>方面，我們小組選出的第一個案例是<strong>「英國國民保健署（NHS）的臨床用藥安全監控與癌症治療優化決策」</strong>：透過 Oracle Exadata 快速分析數十億筆臨床資料並建立儀表板，使醫療決策者能精準找出一次服用 10 種藥物與過量使用抗生素的病患，並串連癌症用藥與治療結果數據找出更有效的治療方案，實質省下 5.81 億英鎊。第二個成功改善決策則是<strong>「紐約市警局（NYPD）CompStat 計畫的警力動態部署與重度累犯起訴決策」</strong>：透過每週彙整全市 76 個轄區的報案、投訴、逮捕與法院傳喚資料庫，動態呈現犯罪熱點與逮捕資訊，幫助轄區指揮官快速找出樣式與趨勢並針對最需要的地方佈署警察，同時讓犯罪策略部門（CSU）積極起訴嚴重違法者（此外，Amazon/Spotify 推薦決策與 Meridian 後期換裝 IBM 即時軟體亦屬成功改善決策）。</p>
<p>在<strong>沒有改善（或失敗）的決策</strong>方面，我們小組選出的第一個案例是<strong>「某大型企業將 Twitter 提及次數列為銷售 KPI 的行銷資源配置決策」</strong>：該公司忽視過去銷售成果大多來自參加實體貿易展與研討會，盲目建立數位儀表板衡量網站流量與 Twitter 被提及次數並設為銷售 KPI，改變了銷售部門焦點，將時間與資源投入監測點擊率與社群流量，產生許多永遠不會創造真正銷售的無效線索。第二個失敗決策則是<strong>「2016 年美國總統大選希拉蕊・柯林頓競選團隊的選情預測與選區聚焦決策」</strong>（此外尚有 Meridian 早期過時設備老化模擬軟體及 Google 流感趨勢高估疫情等失敗決策）：柯林頓團隊沿用歐巴馬勝選時的資料庫，錯誤假設婦女、少數民族、大學畢業生與藍領工人會如預期支持，將焦點放在投票率很高的地區，卻忽略最後一刻改變想法的共和黨人與環境背景誤差，導致預測勝率雖達 70% 至 99%，最終卻敗選。</p>

<table class="ehrenberg">
  <thead>
    <tr>
      <th class="num-col" style="width: 14%;">決策成效分類</th>
      <th style="width: 20%;">代表組織（國別）</th>
      <th style="width: 33%;">巨量資料分析工具與具體決策內容</th>
      <th style="width: 33%;">最終決策結果與實質組織影響</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="num-col"><span class="badge-pill pill-good">成功改善決策 1</span></td>
      <td><strong>英國國民保健署 NHS</strong><br>（英國 UK）</td>
      <td>● <strong>【臨床用藥監控與癌症治療決策】</strong>：以 <span class="nowrap">Oracle Exadata</span> 分析數十億筆處方籤與治療有效性資料，建立醫療儀表板。</td>
      <td>● 成功找出一次服用 10 種藥物與過量抗生素患者，串連癌症數據優化治療方案，實質<strong>節省約 5.81 億英鎊（7.84 億美元）</strong>。</td>
    </tr>
    <tr>
      <td class="num-col"><span class="badge-pill pill-good">成功改善決策 2</span></td>
      <td><strong>紐約市警局 NYPD</strong><br>（美國 USA）</td>
      <td>● <strong>【警力熱點部署與累犯起訴決策】</strong>：透過 <span class="nowrap">CompStat 計畫</span>彙整 76 個轄區報案、逮捕與傳喚資料庫，每週呈現犯罪熱點。</td>
      <td>● 協助轄區指揮官快速辨識犯罪趨勢，將警力精準佈署至最需要之處，並由犯罪策略部門（CSU）積極起訴嚴重違法者以降低犯罪率。</td>
    </tr>
    <tr>
      <td class="num-col"><span class="badge-pill pill-bad">失敗決策 1</span></td>
      <td><strong>某大型企業</strong><br>（跨國實體展銷型）</td>
      <td>● <strong>【Twitter 聲量列為銷售 KPI 決策】</strong>：建立數位儀表板顯示官網流量與 Twitter 被提及次數，並將其列為銷售部門關鍵績效指標。</td>
      <td>● 扭曲原本依賴實體貿易展與研討會的銷售焦點，耗費時間與資源監測網站點擊與社群流量，產出大量永遠不會創造真正銷售的無效線索。</td>
    </tr>
    <tr class="bottom-line">
      <td class="num-col"><span class="badge-pill pill-bad">失敗決策 2</span></td>
      <td><strong>2016 柯林頓競選團隊</strong><br>（美國總統大選）</td>
      <td>● <strong>【沿用舊選民庫之選區聚焦決策】</strong>：加入歐巴馬時期資料庫分析民調與社群行為，假設舊支持族群不變，將焦點放在高投票率地區。</td>
      <td>● 婦女、少數民族、大學畢業生與藍領未如預期支持，且模型未捕捉最後一刻轉向川普的共和黨人，雖預測勝率 <strong>70%–99%</strong> 最終卻落敗。</td>
    </tr>
  </tbody>
</table>

<!-- ==================== PAGE 5: CHAPTER 4 PART 2 (QUESTIONS 3 & 4) ==================== -->
<div class="chapter-break"></div>
<h2>第四章：個案研究問題的小組討論後回答（Part 2：問題 3 五大分析限制 ＆ 問題 4 MIS 鐵三角評估）</h2>

<h3>問題 3：說明使用巨量資料的限制。</h3>
<p>根據個案內容與我們小組的討論，使用巨量資料進行商業與組織決策時共有<strong>五大核心限制與盲點</strong>。若管理者未能認清這些限制，大數據不僅無法帶來效益，反而會誤導決策並引發法律與倫理危機：</p>
<ul class="clean-list">
  <li><span class="bullet-dot">●</span><span class="anchor-tag">【限制一：缺乏清晰企業目標與「可測量就代表該測量」的 KPI 迷思】</span>：許多公司急於啟動巨量資料計畫，卻未先設定企業目標或建立衡量成敗的關鍵績效指標（KPI）。在一堆資料中打滾不代表正在蒐集正確資訊；更危險的是誤以為「某件事可以測量就應該測量」（如某大公司把 Twitter 提及次數列為銷售 KPI），反而扭曲銷售部門焦點、耗費資源產出無效銷售線索。</li>
  <li><span class="bullet-dot">●</span><span class="anchor-tag">【限制二：資料品質與資料治理限制（未清理的混亂資料毫無價值）】</span>：個案明確強調「組織不會從未正確清理、組織、管理的巨量資料中獲益——記得資料品質很重要」。若底層資料充滿雜訊、未經妥善清理與治理，再龐大的資料量也無法產出可靠洞見。</li>
  <li><span class="bullet-dot">●</span><span class="anchor-tag">【限制三：方法論限制——「相關性不等於因果關係」與缺乏領域知識】</span>：巨量資料雖極擅長檢測微小資料集容易漏掉的細微相關性，但<strong>不一定能找出因果關係或有意義的相關性</strong>。例如 2006 至 2011 年美國各州謀殺率與 Internet Explorer（IE）市佔率呈現高度正相關（同步顯著下降），但兩者毫無實質聯繫；若分析師缺乏解決問題的<strong>企業領域知識（Domain Knowledge）</strong>，極易受假性相關誤導。</li>
  <li><span class="bullet-dot">●</span><span class="anchor-tag">【限制四：預測模型限制——過時建模、資料選擇偏見與缺乏上下文脈絡（Context）】</span>：預測模型不一定能讓人更了解未來。第一，<strong>建模技術過時與模擬脫節</strong>（如紐澳 Meridian Energy 舊設備老化預測系統無法預測真實世界哪個機組會停擺）；第二，<strong>忽略搜尋結果的上下文脈絡</strong>（如 Google 流感趨勢只看搜尋數字，忽略媒體廣泛報導與社群推波助瀾引發的恐慌搜尋而持續高估疫情）；第三，<strong>歷史資料偏見與環境誤差失察</strong>（如 2016 美國大選柯林頓團隊盲信歐巴馬時期資料庫、漏算最後一刻改變想法的共和黨人與真實投票行為，以及 2016 英國脫歐民調翻車）。</li>
  <li><span class="bullet-dot">●</span><span class="anchor-tag">【限制五：資訊安全、倫理與「推論隱私（Inferential Privacy）」侵害風險】</span>：企業積極蒐集購物習慣、收入、嗜好、住所與手機移動路徑，將部分人標示為貸款或健康「高風險者」以保護企業或操弄消費者；更將個資結合不同來源資料，推論出當事人不願揭露甚至自己都不知道的特徵（如<strong>顯示出帕金森氏症早期徵兆</strong>，或<strong>無意識受藍色、綠色產品吸引</strong>）。在缺乏法律程序保護、缺乏反擊機制且當事人不知情下，民眾將蒙受嚴重損害。</li>
</ul>

<h3>問題 4：所有的組織都應該蒐集和分析巨量資料嗎？在公司決定要投入巨量資料分析前，必須先考量哪些管理、組織和科技的議題？</h3>
<p>經過小組深入討論後，我們認為：<strong>「並非所有的組織都應該盲目蒐集和分析巨量資料。」</strong> 若企業只是被巨量資料的美麗願景所誘惑，卻沒有明確的企業目標、不知道如何透過大數據解決核心營運問題，或者自身核心業務動能根本不依賴特定的線上表象數據（例如個案中依靠實體貿易展與研討會創造銷售成果的公司），抑或尚未具備基本的資料清理與管理能力，盲目投入只會扭曲部門焦點並造成資源虛耗。當公司評估確有需求並決定投入巨量資料分析前，必須依據 MIS <strong>「管理（Management）、組織（Organization）、科技（Technology）鐵三角架構」</strong>先考量以下議題：</p>

<table class="parallel-grid-table">
  <tr>
    <td class="card-header" style="width: 33.3%; background-color: #DBEAFE; color: #1E40AF; border: 2px solid #1A48A0;">一、管理議題（Management）</td>
    <td class="card-header" style="width: 33.3%; background-color: #FEF3C7; color: #92400E; border: 2px solid #B45309;">二、組織議題（Organization）</td>
    <td class="card-header" style="width: 33.4%; background-color: #D1FAE5; color: #065F46; border: 2px solid #047857;">三、科技議題（Technology）</td>
  </tr>
  <tr>
    <td class="card-row b-blue">
      ● <strong>【確立清晰企業目標】</strong>：啟動前必須先定義要解決什麼具體商業問題（如 NHS 鎖定降低處方浪費、NYPD 鎖定降犯罪率），拒絕盲目跟風。<br>
      ● <strong>【設計正確 KPI 破除測量迷思】</strong>：嚴格區分「可測量表象指標（Twitter 提及次數）」與「實質營收指標（實體展會轉化）」，避免資源錯置。<br>
      ● <strong>【建立推論隱私與倫理紅線】</strong>：針對高風險貼標籤與跨源推論隱私（如帕金森氏症前兆）制定合規審查、透明告知與消費者申訴保護機制。
    </td>
    <td class="card-row b-ochre">
      ● <strong>【培育企業領域知識人才】</strong>：配置具備深厚特定業務領域知識（Domain Knowledge）的分析師，以解讀社會脈絡並過濾「IE 與謀殺率」假性相關。<br>
      ● <strong>【保護部門核心業務焦點】</strong>：調整工作流程與考核制度，確保銷售與營運部門不會被錯誤的數位儀表板指標扭曲日常重心。<br>
      ● <strong>【建立審視資料與假設之文化】</strong>：要求分析師花足夠時間檢視預測模型底層資料，打破對歷史成功樣本（如歐巴馬舊選民庫）的盲目迷信。
    </td>
    <td class="card-row b-teal">
      ● <strong>【落實資料清理、組織與治理】</strong>：確保資料品質（Data Quality），建立標準化清理與管理管線，避免垃圾進、垃圾出。<br>
      ● <strong>【建置高速大數據運算平台】</strong>：投資能快速分析數十億筆巨量資料的軟硬體架構（如英國 NHS 採用的 <span class="nowrap">Oracle Exadata Database Machine</span>）。<br>
      ● <strong>【淘汰過時模型、串接即時資料】</strong>：捨棄脫離現實的過時模擬軟體，導入能運用設備與環境「即時資料」的現代預測系統（如 <span class="nowrap">IBM 預測軟體</span>）。
    </td>
  </tr>
  <tr>
    <td class="card-footer b-blue-foot">管理核心：目標對齊 × 真 KPI × 隱私合規</td>
    <td class="card-footer b-ochre-foot">組織核心：領域知識 × 流程防偏 × 假設審視</td>
    <td class="card-footer b-teal-foot">科技核心：資料清理 × 高速平台 × 即時數據</td>
  </tr>
</table>

<!-- ==================== PAGE 6: CHAPTER 4 PART 3 (QUESTION 5 ADVANCED + DIAGRAM 2) ==================== -->
<div class="chapter-break"></div>
<h2>第四章：個案研究問題的小組討論後回答（Part 3：問題 5 延伸進階題——避免資料偏見與脈絡缺失）</h2>

<h3>問題 5（延伸進階題）：結合個案中 Google 流感預測失準以及 2016 年美國總統大選預測翻車的教訓，當企業或組織在建構「預測模型」時，應該如何避免陷入「資料偏見（Data Bias）」與「缺乏上下文脈絡（Context）」的陷阱？</h3>
<p>結合 Google 流感趨勢（GFT）與 2016 年美國總統大選預測翻車的慘痛教訓，我們小組認為：企業或組織若要避免陷入<strong>「資料偏見（Data Bias）」</strong>，首先必須徹底摒棄「過去的歷史資料結構會無條件延續到未來」的靜態假設（柯林頓團隊盲信歐巴馬時期資料庫，誤認婦女、少數民族、大學畢業生與藍領必延續支持，同年英國脫歐公投亦然），必須持續更新底層資料、納入<strong>動態即時數據</strong>（如 Meridian 換裝 IBM 即時系統），並設計<strong>潛在環境誤差校正機制</strong>以捕捉「最後一刻改變想法者」與真實投票行為。其次，為避免陷入<strong>「缺乏上下文脈絡（Context）」</strong>，組織絕不能讓演算法只看單一表象搜尋數字（Google 只看搜尋量卻忽略媒體廣泛報導與社群推波助瀾引發的恐慌搜尋脈絡），而應將<strong>「異常外部事件（媒體炒作、政策變動）」設為調節變數</strong>，並拿線上行為數據與<strong>實體真實基準數據（如美國 CDC 實際就診數據、實體展會銷售額）交叉校準</strong>；最後更必須結合人類專家的<strong>「特定業務領域知識（Domain Knowledge）」</strong>持續檢驗因果邏輯：</p>

<div class="formula-sandwich">
  <div class="sandwich-top">
    <strong>● 【高可靠度預測模型設計公式（Formula Sandwich）】</strong>：將傳統單一歷史外推模型，升級為融合「即時數據流」、「外部媒體脈絡降權調節」與「領域專家因果把關」之閉環函數：
  </div>
  <div class="sandwich-mid">
    <span class="math-expr">Reliable Prediction &nbsp;&#x0176;(t) &nbsp;=&nbsp; f<sub>Domain</sub> &nbsp;(&nbsp; [ D<sub>Hist</sub> &oplus; D<sub>RealTime</sub>(t) ] ,&nbsp;&nbsp; X<sub>Search</sub>(t) / [ 1 + &gamma; &middot; C<sub>MediaShock</sub>(t) ] ,&nbsp;&nbsp; &varepsilon;<sub>LatentSwitch</sub>(t) &nbsp;)</span>
  </div>
  <div class="sandwich-bot">
    <strong>● 【白話直覺翻譯】</strong>：<strong>(1) D<sub>Hist</sub> &oplus; D<sub>RealTime</sub>(t)</strong>：打破歐巴馬舊資料庫偏見，強制注入即時運行數據；<strong>(2) X<sub>Search</sub>(t) / [1 + &gamma;&middot;C<sub>MediaShock</sub>(t)]</strong>：當媒體炒作與社群恐慌（C<sub>MediaShock</sub>）暴增時，自動將表象搜尋量（X<sub>Search</sub>）除噪降權，防範 Google 流感高估失準；<strong>(3) &varepsilon;<sub>LatentSwitch</sub>(t) 與 f<sub>Domain</sub></strong>：校正「最後一刻轉向者」環境誤差，並由人類領域專家進行最終因果審核。
  </div>
</div>

<div class="figure-box">
  <div class="figure-header">圖 4-1（格式 A 核心機制圖譜）：從「失靈黑箱預測」到「高可靠人機協同決策」之 3&times;3 治理架構圖</div>
  <img src="02_predictive_reliability_architecture.png" class="figure-img" alt="高可靠人機協同決策3x3治理架構圖">
  <div class="figure-footnote">
    <strong>3&times;3 治理架構導讀</strong>：左欄剖析「歷史樣本僵化、忽略外部脈絡、假性相關與推論隱私」三大陷阱；中欄對應問題 4 與問題 5 之「科技即時數據流（M1）、管理外部脈絡調節（M2）、組織領域專家因果審查（M3）」；右欄產出高可靠商業與公共決策價值。
  </div>
</div>

<table class="ehrenberg">
  <thead>
    <tr>
      <th style="width: 19%;">預測失靈代表案例</th>
      <th style="width: 19%;">陷入之核心陷阱與盲點</th>
      <th style="width: 29%;">失靈原因具體剖析（為什麼翻車？）</th>
      <th style="width: 33%;">建構預測模型之具體防範與修正對策</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>2016 美國總統大選<br>與英國脫歐民調</strong></td>
      <td><strong>資料偏見（Data Bias）</strong><br>與歷史樣本僵化</td>
      <td>● 過度依賴歐巴馬勝選時期資料庫，誤認婦女、少數民族、大學畢業生與藍領必延續支持；缺環境誤差校正，漏算最後一刻轉向的共和黨人。</td>
      <td>● <strong>【摒棄靜態歷史假設】</strong>：持續更新動態樣本並要求分析師嚴審底層資料；增設潛在環境誤差校正機制，主動捕捉最後一刻轉向者與真實投票率。</td>
    </tr>
    <tr>
      <td><strong>Google 流感趨勢<br>（GFT）疫情預測</strong></td>
      <td><strong>缺乏上下文脈絡（Context）</strong><br>與表象指標誤導</td>
      <td>● 演算法只查看位置與流感關鍵字搜尋數字，忽略媒體廣泛報導疫情與社群推波助瀾引發的群眾恐慌搜尋脈絡，較 CDC 數據持續高估。</td>
      <td>● <strong>【納入外部脈絡與實體校準】</strong>：將媒體報導熱度等異常外部事件設為降權調節變數；將線上搜尋快數據與美國 CDC 實體就診數據定期交叉校準。</td>
    </tr>
    <tr class="bottom-line">
      <td><strong>Meridian Energy<br>早期設備預測系統</strong></td>
      <td><strong>過時建模技術</strong><br>與脫離真實世界情境</td>
      <td>● 採用過時建模技術與脫離現實的情境模擬測試，雖能預測模擬表現，卻無法準確預警真實世界中哪個發電機、風機或變壓器會停擺。</td>
      <td>● <strong>【串接即時數據與領域專家協作】</strong>：淘汰靜態過時模型，如同換裝 IBM 預測軟體般全面串接設備「即時運行資料」，並結合領域專家檢驗因果。</td>
    </tr>
  </tbody>
</table>

<!-- ==================== PAGE 7: CHAPTER 5 (TEAM CONTRIBUTION + 20-25 MIN PLAN + Q&A DEFENSE) ==================== -->
<div class="chapter-break"></div>
<h2>第五章：成員貢獻表與 20–25 分鐘上台報告＆ 25 分鐘 Q&amp;A 協作規劃</h2>
<p>在本次「資訊管理」課程之「巨量資料分析有多可靠？」個案分析專案中，我們小組成員透過密切的分工與共同研討完成所有章節分析。由<strong>黃宥丞</strong>同學負責前期的課本個案與跨國背景資料收集、各國案例脈絡整理，並與組員共同針對個案後的五項個案研究問題進行深度討論與 Q&amp;A 題庫研擬；再由<strong>楊亞恩</strong>同學負責統整討論成果、進行第一章至第五章個案分析內文與結構化對照表格之撰寫、繪製全景知識圖譜與量化實證圖表，最後由兩位成員共同準備簡報並<strong>全員一同上台進行 20–25 分鐘報告與 25 分鐘 Q&amp;A 答詢</strong>。</p>

<h3>5.1 小組成員貢獻百分比明細表（符合課程規範第 3-(5) 點）</h3>
<table class="ehrenberg">
  <thead>
    <tr>
      <th class="num-col" style="width: 12%;">姓名</th>
      <th class="num-col" style="width: 14%;">學號</th>
      <th style="width: 50%;">主要負責內容（具體分工與協作項目明細）</th>
      <th class="num-col" style="width: 12%;">上台報告</th>
      <th class="num-col" style="width: 12%;">貢獻百分比</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="num-col"><strong>楊亞恩</strong></td>
      <td class="num-col"><code>311157139</code></td>
      <td>● <strong>撰寫個案分析及報告、視覺圖表設計、上台報告</strong>：主導第一章至第四章之個案分析內文撰寫、跨國案例總覽表與問題識別診斷表統整編排、整合小組五題討論結論成文、繪製知識圖譜與簡報排版，並擔任<strong>上半場上台報告主講人</strong>與 Q&amp;A 共同答詢。</td>
      <td class="num-col"><span class="badge-pill pill-good">是（上半場）</span></td>
      <td class="num-col"><strong>60%</strong></td>
    </tr>
    <tr>
      <td class="num-col"><strong>黃宥丞</strong></td>
      <td class="num-col"><code>311357109</code></td>
      <td>● <strong>資料收集、個案問題深度討論、上台報告</strong>：負責收集個案相關之英國 NHS、紐約 CompStat、紐澳 Meridian、Google 流感趨勢與 2016 美國大選民調等背景補充資料，參與五題個案問題深度研討與 Q&amp;A 應答設計，並擔任<strong>下半場上台報告主講人</strong>與 Q&amp;A 共同答詢。</td>
      <td class="num-col"><span class="badge-pill pill-good">是（下半場）</span></td>
      <td class="num-col"><strong>40%</strong></td>
    </tr>
    <tr class="bottom-line">
      <td class="num-col"><strong>小組總計</strong></td>
      <td class="num-col"><strong>共 2 人</strong></td>
      <td><strong>完成 7 頁印刷級深度分析報告 PDF、3 張高解析度圖譜與量化圖表、12 頁原生向量簡報 PPTX 及 25 分鐘 Q&amp;A 題庫</strong></td>
      <td class="num-col"><strong>全員皆上台</strong></td>
      <td class="num-col"><strong>100%</strong></td>
    </tr>
  </tbody>
</table>

<h3>5.2 20–25 分鐘雙講者上台報告時間配當表（符合課程規範第 5、6 點）</h3>
<table class="ehrenberg">
  <thead>
    <tr>
      <th style="width: 18%;">報告階段與講者</th>
      <th style="width: 28%;">對應簡報頁次（共 12 頁）</th>
      <th class="num-col" style="width: 14%;">時間配當</th>
      <th style="width: 40%;">上台報告核心演講脈絡與轉場銜接設計</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>上半場主講：<br>楊亞恩</strong><br>（<code>311157139</code>）</td>
      <td>• <strong>Slide 01–02</strong>：封面破題與五步導覽<br>• <strong>Slide 03</strong>：(1) 個案國別及產業簡介<br>• <strong>Slide 04</strong>：(2) 問題識別與量化斷崖圖<br>• <strong>Slide 05</strong>：(3) 個案簡介與全景架構<br>• <strong>Slide 06</strong>：(4) 問題 1 效益 ＆ 問題 2 改善決策</td>
      <td class="num-col"><strong>11.5 分鐘</strong><br><em>(約 1.9 分/頁)</em></td>
      <td>● 從全球每日 <code>2,500 萬億 Bytes</code> 破題，梳理英、美、紐澳與跨國四大板塊及六大失靈事件，並深入解析英國 NHS（省 <code>5.81 億英鎊</code>）與紐約警局（<code>76 轄區</code>）兩大成功決策如何創造實質效益。</td>
    </tr>
    <tr class="bottom-line">
      <td><strong>下半場主講：<br>黃宥丞</strong><br>（<code>311357109</code>）</td>
      <td>• <strong>Slide 07</strong>：(4) 問題 2 兩大失敗決策剖析<br>• <strong>Slide 08</strong>：(4) 問題 3 五大限制與推論隱私<br>• <strong>Slide 09</strong>：(4) 問題 4 MIS 管理×組織×科技<br>• <strong>Slide 10</strong>：(4) 問題 5 進階建模公式與防線<br>• <strong>Slide 11–12</strong>：(5) 成員貢獻表、總結與 Q&amp;A</td>
      <td class="num-col"><strong>11.5 分鐘</strong><br><em>(約 1.9 分/頁)</em></td>
      <td>● 接棒剖析 Twitter KPI 迷思、IE 與謀殺率假性相關、GFT 與 2016 美選預測翻車及帕金森氏症「推論隱私」危機，最後以 MIS 鐵三角與動態脈絡校正公式總結全案，引導進入 <strong>25 分鐘 Q&amp;A</strong>。</td>
    </tr>
  </tbody>
</table>

<div class="closing-seal">
  <div style="font-weight: 800; font-size: 9.6pt; color: #FFFFFF; border-bottom: 1px solid #334155; padding-bottom: 4px;">
    ★ 25 分鐘 Q&amp;A 深度互動預備：四大高頻提問與小組防禦應答錦囊（Q&amp;A Defense Playbook）
  </div>
  <div class="closing-grid">
    <div class="closing-subbox">
      <div class="closing-subbox-title">Q1：2016 美選柯林頓與川普都用大數據，為何柯林頓輸、川普贏？</div>
      <div><strong>應答核心</strong>：差在「靜態預測 vs. 動態分眾溝通」。柯林頓盲信歐巴馬舊資料庫，假設婦女、少數民族與藍領無條件支持；而課本明確指出<strong>川普將大數據聚焦於「針對選民群體量身打造精準廣告訊息」</strong>，主動影響搖擺州與最後一刻轉向者。</div>
    </div>
    <div class="closing-subbox">
      <div class="closing-subbox-title">Q2：「推論隱私（Inferential Privacy）」與傳統個資外洩有何不同？</div>
      <div><strong>應答核心</strong>：傳統外洩是「已知個資被竊」；推論隱私則是結合購物、收入與手機 GPS 後，<strong>演算法推論出當事人不願揭露甚至自己都不知道的特徵（如早期帕金森氏症徵兆或無意識藍綠偏好）</strong>，且毫無法律程序與反擊機制。</div>
    </div>
    <div class="closing-subbox">
      <div class="closing-subbox-title">Q3：靠實體貿易展銷售的傳統企業，就完全不該用資料分析嗎？</div>
      <div><strong>應答核心</strong>：問題 4 強調的是「不可無目標盲目跟風」。該企業錯在把與自身成交無關的 Twitter 聲量當 KPI；若改為清理並分析「實體展會洽談名單、客戶產業屬性與後續實際簽約率」，就能對齊核心目標並創造真營收。</div>
    </div>
    <div class="closing-subbox">
      <div class="closing-subbox-title">Q4：同為醫療健康大數據，為何英國 NHS 成功、Google 流感卻失準？</div>
      <div><strong>應答核心</strong>：NHS 在 Oracle Exadata 分析的是<strong>醫院真實處方籤與臨床結果（實體 Ground Truth＋醫師領域知識）</strong>；Google 分析的則是<strong>搜尋關鍵字（表象行為數據）</strong>，極易受媒體報導引發的恐慌搜尋干擾，故必須與 CDC 實體數據交叉校準。</div>
    </div>
  </div>
</div>

</body>
</html>
"""

output_dir = os.path.abspath("reading_sessions/20261101_巨量資料分析有多可靠/02_outputs")
os.makedirs(output_dir, exist_ok=True)
html_path = os.path.join(output_dir, "temp_report_compile.html")
pdf_path = os.path.join(output_dir, "01_case_analysis_report.pdf")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"[OK] Temporary HTML written to: {html_path}")

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
            alt_pdf = os.path.join(output_dir, "資訊管理個案分析報告_巨量資料分析有多可靠_新版.pdf")
            shutil.copyfile(temp_pdf, alt_pdf)
            print(f"[LOCKED] {pdf_path} is open in viewer; saved to: {alt_pdf} (Size: {os.path.getsize(alt_pdf):,} bytes)")
    else:
        print(f"[FAIL] PDF compilation failed: {res.stderr}")
else:
    print(f"[WARN] Chrome not found at {chrome_path}")

shutil.rmtree(temp_profile, ignore_errors=True)

if os.path.exists(html_path):
    os.remove(html_path)
    print(f"[CLEAN] Removed temporary HTML file: {html_path}")
