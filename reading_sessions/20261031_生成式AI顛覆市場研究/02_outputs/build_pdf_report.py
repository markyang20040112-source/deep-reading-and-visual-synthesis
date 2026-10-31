# -*- coding: utf-8 -*-
"""
build_pdf_report.py
Renders the publication-grade PDF report following document_report_spec.md:
- W3C CLREQ Traditional Chinese typography (11pt body, 1.72 leading, 1.2em paragraph spacing)
- Booktabs 3-line scientific supertables (zero vertical lines, bottom-line takeaway row)
- Formula Sandwich block with clear mathematical notation
- Callout boxes with 4px left semantic accent strip
- Embedded high-DPI knowledge diagrams
"""

import os
import subprocess

OUT_DIR = r"c:\Users\User\.gemini\antigravity\scratch\deep-reading-and-visual-synthesis\reading_sessions\20261031_生成式AI顛覆市場研究\02_outputs"
HTML_PATH = os.path.join(OUT_DIR, "_temp_report.html")
PDF_PATH = os.path.join(OUT_DIR, "生成式AI顛覆市場研究_深度閱讀與三篇合體決策白皮書.pdf")

IMG1 = "01_生成式AI顛覆市場研究_四大機會與核心實務圖.jpg"
IMG2 = "02_生成式AI市調局限_實驗混淆與四大前沿解法思辨圖.jpg"
IMG3 = "03_三篇合體_顧客價值與AI數據科學決策終極藍圖.jpg"

HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>《生成式 AI 正在顛覆市場研究》深度閱讀與「三篇合體」企業科學決策白皮書</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 18mm 16mm 18mm 16mm;
  }}
  @page :first {{
    margin-top: 15mm;
  }}
  @page landscape_diagram {{
    size: A4 landscape;
    margin: 10mm 14mm 10mm 14mm;
  }}
  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}
  body {{
    font-family: "Microsoft JhengHei", "PingFang TC", "Noto Sans CJK TC", sans-serif;
    font-size: 10.5pt;
    line-height: 1.72;
    color: #1E293B;
    background-color: #FFFFFF;
    margin: 0;
    padding: 0;
  }}
  /* Header Cover Banner */
  .report-header {{
    background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
    color: #FFFFFF;
    padding: 22px 26px;
    border-radius: 8px;
    margin-bottom: 18px;
    border-bottom: 4px solid #38BDF8;
  }}
  .report-header .doc-tag {{
    display: inline-block;
    background-color: rgba(56, 189, 248, 0.2);
    color: #7DD3FC;
    border: 1px solid #38BDF8;
    font-size: 8.5pt;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 4px;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
  }}
  .report-header h1 {{
    font-size: 18.5pt;
    font-weight: 800;
    line-height: 1.35;
    margin: 0 0 8px 0;
    color: #FFFFFF;
  }}
  .report-header .subtitle {{
    font-size: 9.8pt;
    color: #CBD5E1;
    margin: 0 0 10px 0;
    line-height: 1.5;
  }}
  .report-header .meta-grid {{
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    font-size: 8.5pt;
    color: #94A3B8;
    border-top: 1px solid rgba(255,255,255,0.15);
    padding-top: 8px;
  }}
  .report-header .meta-grid span strong {{
    color: #E2E8F0;
  }}

  /* Main Messages Executive Box (1:3:25 Rule) */
  .main-messages {{
    background-color: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-left: 5px solid #1E40AF;
    border-radius: 6px;
    padding: 14px 18px;
    margin-bottom: 20px;
  }}
  .main-messages-title {{
    font-size: 11.5pt;
    font-weight: 800;
    color: #1E40AF;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
  }}
  .main-messages ol {{
    margin: 0;
    padding-left: 20px;
  }}
  .main-messages li {{
    margin-bottom: 6px;
    font-size: 9.8pt;
    line-height: 1.62;
    color: #1E293B;
  }}
  .main-messages li:last-child {{
    margin-bottom: 0;
  }}

  /* Section Headings (Layer-Cake High Information Scent) */
  h2 {{
    font-size: 13.5pt;
    font-weight: 800;
    color: #0F172A;
    background-color: #F1F5F9;
    border-left: 4px solid #0F172A;
    padding: 7px 12px;
    margin: 22px 0 12px 0;
    border-radius: 0 4px 4px 0;
    page-break-after: avoid;
  }}
  h3 {{
    font-size: 11.2pt;
    font-weight: 700;
    color: #1E3A8A;
    margin: 14px 0 6px 0;
    page-break-after: avoid;
  }}
  p {{
    margin: 0 0 10px 0;
    text-align: justify;
  }}
  ul.bullet-list {{
    list-style: none;
    margin: 6px 0 12px 0;
    padding-left: 0;
  }}
  ul.bullet-list li {{
    margin-bottom: 7px;
    text-align: justify;
  }}
  .anchor-bold {{
    color: #0F172A;
    font-weight: 700;
  }}

  /* Callout Boxes (4px left strip) */
  .callout {{
    padding: 11px 15px;
    border-radius: 5px;
    margin: 12px 0;
    font-size: 9.8pt;
    page-break-inside: avoid;
  }}
  .callout-synth {{
    background-color: #F5F3FF;
    border-left: 4px solid #5B21B6;
    color: #2E1065;
  }}
  .callout-warn {{
    background-color: #FFF1F2;
    border-left: 4px solid #BE123C;
    color: #4C0519;
  }}
  .callout-success {{
    background-color: #ECFDF5;
    border-left: 4px solid #047857;
    color: #064E3B;
  }}
  .callout-title {{
    font-weight: 800;
    margin-bottom: 4px;
    display: block;
  }}

  /* Ehrenberg & Few Booktabs Scientific Supertables (NO vertical lines!) */
  table.booktabs {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 16px 0;
    font-size: 9.0pt;
    line-height: 1.52;
    border-top: 2.2px solid #0F172A;
    border-bottom: 2.2px solid #0F172A;
    page-break-inside: avoid;
  }}
  table.booktabs thead th {{
    background-color: #F8FAFC;
    color: #0F172A;
    font-weight: 800;
    text-align: left;
    padding: 8px 10px;
    border-bottom: 1.4px solid #334155;
     border-left: none;
    border-right: none;
  }}
  table.booktabs tbody td {{
    padding: 8px 10px;
    border-bottom: 0.6px solid #E2E8F0;
    border-left: none;
    border-right: none;
    vertical-align: top;
    color: #334155;
  }}
  table.booktabs tbody tr:nth-child(even) td {{
    background-color: #FAFBFD;
  }}
  table.booktabs tbody tr.bottom-line-row td {{
    background-color: #EFF6FF !important;
    color: #1E3A8A;
    font-weight: 700;
    border-top: 1.4px solid #1E40AF;
    border-bottom: none;
    padding: 9px 10px;
  }}
  .num-highlight {{
    font-weight: 800;
    color: #0F172A;
  }}

  /* Formula Sandwich Protocol */
  .formula-sandwich {{
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    background-color: #FFFFFF;
    margin: 14px 0;
    overflow: hidden;
    page-break-inside: avoid;
  }}
  .formula-top {{
    background-color: #F8FAFC;
    padding: 8px 14px;
    border-bottom: 1px dashed #CBD5E1;
    font-size: 9.5pt;
    color: #334155;
  }}
  .formula-mid {{
    padding: 14px 16px;
    text-align: center;
    background-color: #FFFBEB;
    font-family: "Cambria Math", "Times New Roman", serif;
    font-size: 11pt;
    color: #0F172A;
  }}
  .formula-mid .math-row {{
    display: flex;
    justify-content: space-around;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }}
  .formula-mid .math-box {{
    background: #FFFFFF;
    border: 1px solid #F59E0B;
    border-radius: 5px;
    padding: 8px 12px;
    flex: 1;
  }}
  .formula-mid .math-caption {{
    display: block;
    font-family: "Microsoft JhengHei", sans-serif;
    font-size: 8.5pt;
    color: #B45309;
    font-weight: 700;
    margin-top: 4px;
  }}
  .formula-bot {{
    background-color: #F8FAFC;
    padding: 10px 14px;
    border-top: 1px dashed #CBD5E1;
    font-size: 9.4pt;
    color: #334155;
  }}

  /* Landscape / Full-width Diagram Showcase Pages */
  .diagram-page {{
    page: landscape_diagram;
    page-break-before: always;
    page-break-inside: avoid;
  }}
  .diagram-page h2 {{
    margin: 0 0 6px 0;
    padding: 5px 10px;
    font-size: 12pt;
  }}
  .diagram-card {{
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 6px 10px;
    background-color: #F8FAFC;
    page-break-inside: avoid;
  }}
  .diagram-card h3 {{
    margin: 0 0 2px 0;
    font-size: 10.2pt;
    color: #0F172A;
  }}
  .diagram-card p {{
    font-size: 8.5pt;
    color: #475569;
    margin: 0 0 4px 0;
  }}
  .diagram-card img {{
    width: auto;
    max-width: 100%;
    max-height: 152mm;
    object-fit: contain;
    border-radius: 4px;
    border: 1px solid #E2E8F0;
    display: block;
    margin: 0 auto;
  }}
</style>
</head>
<body>

  <!-- COVER BANNER -->
  <div class="report-header">
    <div class="doc-tag">EXECUTIVE STRATEGY &amp; CONCEPT-CENTRIC WHITE PAPER (B1 × B3)</div>
    <h1>《生成式 AI 正在顛覆市場研究》深度閱讀與「三篇合體」企業科學決策白皮書</h1>
    <div class="subtitle">整合 HBR 核心實證 × 三類數據結構與大小模型分工 × 盲測訂價「混淆現象」因果公式 × 四大前沿解法死穴批判 × 「道・法・術」三階閉環</div>
    <div class="meta-grid">
      <span><strong>主文獻：</strong>Jeremy Korst, Stefano Puntoni, Olivier Toubia (HBR)</span>
      <span><strong>跨篇合體：</strong>《顧客需求不靠猜》(Mittal et al.) ＋ 《AI 能強化你的數據分析能力》(Davenport &amp; Fitts)</span>
      <span><strong>產出日期：</strong>2026-10-31</span>
    </div>
  </div>

  <!-- MAIN MESSAGES (10% Budget) -->
  <div class="main-messages">
    <div class="main-messages-title">★ Main Messages 決策主訊息框：四大核心行動斷言 (So-What Assertions)</div>
    <ol>
      <li><strong>【AI 訪談員破除人類道德偽裝】</strong>：當生成式 AI 擔任「動態訪談員（如 Outset.ai）」時，因不會觸發受訪者的<strong>「心理與道德修飾機制（社會期許偏誤）」</strong>，反而能比真人訪談挖出更坦誠的深層痛點，同時兼顧量化調查的規模與質化訪談的深度。</li>
      <li><strong>【資料結構決定大小模型分工】</strong>：企業私有小型模型（如 Rockfish Data）雖具絕對隱私，但僅能學習<strong>結構化（數字型／類別型）</strong>與<strong>半結構化數據</strong>之統計機率；唯有具備人類世界知識先驗的公開大型模型，方能處理並生成<strong>非結構化質化數據</strong>（最佳折衷解為以內部私有數據微調大型模型）。</li>
      <li><strong>【警惕盲測訂價混淆與感官失靈】</strong>：生成式 AI 天生運算的是「語境條件聯想 <em>P(Y|X)</em>」而非「獨立因果干預 <em>P(Y|do(X))</em>」，在盲測訂價實驗中會自動腦補歷史價與競品價同步變貴（<strong>混淆現象 Confounding</strong>），且無法模擬生理嗅覺與潛意識記憶（如高砂香料案例）；單靠修改提示詞只會淪為「挖東牆補西牆」。</li>
      <li><strong>【放棄萬能模型，執行「道・法・術」情境權變】</strong>：四大前沿修補解法各有理論死穴（具身感官不可壓縮、複雜函式誤設、跨時間分布偏移、歷史微調外推失靈）；企業必須以《顧客需求不靠猜》定錨關鍵問題（<strong>道</strong>）、以《AI 強化數據分析》打通 ERP/CRM 情境底座（<strong>法</strong>），再以《生成式 AI 顛覆市場研究》依商業情境權變配置工具（<strong>術</strong>）。</li>
    </ol>
  </div>

  <!-- SECTION 1 -->
  <h2>壹、【高階總覽與變革架構】生成式 AI 如何以四大核心能力重塑市場研究價值鏈</h2>
  <p>傳統市場研究長期受困於「成本高昂、時程漫長」以及「量化調查廣度 vs. 質化訪談深度不可兼得」的結構性瓶頸。根據本文作者與 GBK Collective 針對 170 位市場研究從業人員與企業用戶的實證調查，高達 <strong>45% 受訪者已在數據與見解活動中使用生成式 AI，另有 45% 正規畫導入</strong>（其中 62% 用於統整冗長訪談逐字稿、58% 用於分析數據、54% 用於撰寫報告），逾 80% 認同其能大幅提升生產力並騰出時間進行高價值的策略說故事。</p>
  <p>作者將生成式 AI 的 <strong>4 大核心能力（統整、編寫程式碼、人機互動、寫作）</strong> 映射至市場研究的 <strong>3 大流程階段（設計研究、蒐集分析、報告傳播）</strong>，並歸納出由淺入深的 <strong>4 大變革機會類型</strong>：強化現有實務、取代現有實務、填補現有缺口，以及創造新型態見解。</p>

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

  <!-- SECTION 2 -->
  <h2>貳、【概念拆解一】資料結構光譜與「私有小型模型 vs. 公開大型模型」之取捨機制</h2>
  <p>在導入客製化合成數據時，企業首當其衝面臨<strong>「數據機密隱私」與「模型語意理解深度」的兩難權衡</strong>（見原文第 10 頁）。要理解為何小型私有模型（如美國陸軍與國土安全部採用的 Rockfish Data）大多只能處理結構化與半結構化數據，而公開大型模型才能處理非結構化質化數據，必須從資料科學的三階結構光譜拆解：</p>
  <ul class="bullet-list">
    <li><span class="anchor-bold">● [結構化數據（Structured Data）]</span> — 指具備嚴格固定欄位、可直接存入關聯式資料庫或 Excel 二維表格的數據。文中特別指明其包含兩類統計尺度：① <strong>數字型數據（Numerical Data）</strong>，即可直接進行算術運算的量化數值（如顧客年齡 <code>34</code> 歲、年消費額 <code>28,500</code> 元、網頁停留秒數）；② <strong>類別型數據（Categorical Data）</strong>，即代表分類標籤或等級順序的離散屬性（如性別、居住城市、會員卡別、李克特五點滿意度選項）。</li>
    <li><span class="anchor-bold">● [半結構化數據（Semi-Structured Data）]</span> — 指無法直接塞入死板表格（因每位顧客的行為序列長短不一、具巢狀階層），但內部自帶<strong>結構標籤（Tags / Keys）</strong>而能被電腦直接解析的資料。典型市調實例包括網站與 App 點擊流日誌（JSON 格式之瀏覽軌跡）、帶有固定標頭欄位的電子郵件與客服工單紀錄。</li>
    <li><span class="anchor-bold">● [非結構化質化數據（Unstructured Qualitative Data）]</span> — 指完全無預先定義格式、承載人類自然語言脈絡、情緒轉折、隱喻與深層動機（回答 <em>Why</em> 與 <em>How</em>）的原始資料。典型實例包含深度訪談逐字稿、焦點團體錄影、社群媒體長篇抱怨貼文與開放式問卷作答（如威斯康辛商學院研究與 Synthetic Users 平台之合成深度訪談）。</li>
  </ul>

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
        <div class="math-box">
          <strong>P(Y | do(X = x)) = ∑<sub>z</sub> P(Y | X = x, Z = z) · P(Z = z)</strong>
          <span class="math-caption">【真人隨機盲測】背景物價與競品價格 Z 獨立於測試價格 X（P(Z|X) = P(Z)）</span>
        </div>
        <div style="font-size: 16pt; font-weight: bold; color: #BE123C;">≠</div>
        <div class="math-box" style="border-color: #BE123C;">
          <strong>P<sub>LLM</sub>(Y | X = x) = ∑<sub>z</sub> P(Y | X = x, Z = z) · P<sub>LLM</sub>(Z = z | X = x)</strong>
          <span class="math-caption" style="color: #BE123C;">【AI 語境腦補混淆】看到高價 X 時自動調高 P<sub>LLM</sub>(Z|X)，腦補競品與歷史價也同步變貴！</span>
        </div>
      </div>
    </div>
    <div class="formula-bot">
      <strong>(下) 參數物理意義與極端邊界推演：</strong><br>
      • <strong>自變數 X（測試價格）與應變數 Y（購買決策）</strong>：研究員欲測量單純調高 X（如 1,000 元 → 5,000 元）對 Y 的獨立因果效應。<br>
      • <strong>混淆變數 Z（Confounder：歷史價格／店內競品價格）</strong>：在真人盲測中，受試者活在真實物價世界，看到測試商品標價 5,000 元時，心中對其他競品價格 Z（1,200 元）的認知不變，故果斷拒買。但生成式 AI 難以將價格 X 視為隨機抽樣，看到 5,000 元時會自動在隱空間調高 Z（腦補「店內其他產品或歷史價格也都是 5,000 元」），使高價購買顯得合理，徹底打亂 X 與 Y 的真實關係！
    </div>
  </div>

  <!-- SECTION 4 -->
  <h2>肆、【方法論交鋒】為何純改提示詞淪為「挖東牆補西牆」？四大前沿解法與理論死穴批判</h2>
  <p>針對上述實驗混淆現象，若僅試圖在提示詞（Prompt）中寫入更詳細的數據情境規範，在結構上必然陷入<strong>「挖東牆補西牆」</strong>的困境：① <strong>東牆（未知腦補變數永遠鎖不完）</strong>——鎖死歷史價與競品價後，具備數千億參數的 AI 又會偷偷腦補「大缺貨、巨星代言或限量溢價」，人工無法事前窮舉；② <strong>西牆（寫太白引發需求特徵劇透與焦點錯覺）</strong>——若在 Prompt 刻意強調「別家都賣 1,200、只有這家賣 5,000」，等於明示 AI 拒買，使 AI 從「過度遲鈍」跳到「過度理性的比大小計算機」，依然測不出真實人類的價格彈性。</p>
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

  <!-- SECTION 5 -->
  <h2>伍、【三篇合體終極藍圖】企業數據科學與生成式 AI 決策之「道・法・術」三階閉環</h2>
  <p>綜合本次深度閱讀的三篇 HBR 經典文獻，企業若想建立真正的科學決策護城河，必須按照您在思辨中提出的<strong>「道（界定問題與方向）→ 法（盤點能力與情境底座）→ 術（前線市調實操與權變）」</strong>三階次序，將三篇文章串聯為一個有機閉環：</p>

  <div class="callout callout-warn">
    <span class="callout-title">第一階【道：界定問題與改進方向】——《顧客需求不靠猜！統計模型找正解》</span>
    ● <strong>破除高層直覺偏誤</strong>：72% 上市 B2B 公司高層認知與顧客真實重視呈零或負相關，85.5% 每兩年大改優先順序（受顯眼客訴與盲從對手誤導）。<br>
    ● <strong>道斯線性模型定錨 X* 與 Y</strong>：運用雙層統計模型量化各因素對整體價值與真實會計營收／毛利 Y 的「提升潛力（Lift）」，嚴格鎖定 1~2 個關鍵驅動因素 X*（如 ITI 鎖定「每週主動進度報告」使股價大漲 162%；S-SET 鎖定「3 小時快速報價」使人均銷售增 52%），砍除無效計畫並明確界定 AI 介入的改進方向。
  </div>

  <div class="callout callout-synth">
    <span class="callout-title">第二階【法：盤點能力與打通情境底座】——《AI 能強化你的數據分析能力》</span>
    ● <strong>內嵌 ERP/CRM 跨部門「背景情境（Contextual Information）」</strong>：打破數據孤島，由人類領域專家在交易系統中預先設定合理因果邊界（防止醫療 AI「肺炎合併氣喘死亡率低」等虛假相關災難）。<br>
    ● <strong>擴增分析與正則化雜訊過濾</strong>：結合 ML + NLP（口說提問）+ NLG（自動摘要）賦能平民分析師（如製造商揪出業務未授權折扣挽回數十萬美元），並以統計自由度懲罰（Adjusted R² 與 Lasso L1 正則化）防止盲目擴充參數 p 導致過度配適。
  </div>

  <div class="callout callout-success">
    <span class="callout-title">第三階【術：前線市調實操與人機權變驗證】——《生成式 AI 正在顛覆市場研究》</span>
    ● <strong>前線高頻實操</strong>：在前兩階確立的目標 X* 與 ERP/CRM 情境底座上，派出 <strong>AI 動態訪談員（Outset.ai）</strong> 消除受訪者心理與道德修飾，並以內部數據微調大模型打造<strong>合成受眾與顧客數位雙生</strong>，進行高速早期策略篩選與銷售話術演練。<br>
    ● <strong>終局真人實驗閉環</strong>：嚴守「盲測訂價混淆、多感官失靈、未來劇變外推」三大禁區，通過「開放式探索 → 迴歸推導重要性 → 綁定真實會計帳本 → 真人隨機對照實驗（A/B Test，如 800 億美元銀行案例）」四道關卡，驅動「企業 ↔ 客戶」核心造血引擎健康運轉！
  </div>

  <!-- SECTION 6: EMBEDDED DIAGRAMS (A4 LANDSCAPE PAGES) -->
  <div class="diagram-page">
    <h2 style="margin-top: 0;">陸、【全景視覺化圖譜附錄（一）】核心實務與數據結構心智圖</h2>
    <div class="diagram-card">
      <h3>圖譜一：《生成式 AI 正在顛覆市場研究》核心實務與數據結構心智圖 (T5 瑞士網格放射拓撲)</h3>
      <p>涵蓋 4 大核心能力 × 3 大市調階段、Outset.ai 消除心理與道德修飾偏誤、合成數據雙盲實證、三類數據結構（結構化〔數字/類別〕、半結構化、非結構化質化）與大小模型權衡，以及顧客數位雙生。</p>
      <img src="{IMG1}" alt="圖譜一">
    </div>
  </div>

  <div class="diagram-page">
    <h2 style="margin-top: 0;">陸、【全景視覺化圖譜附錄（二）】實驗混淆機制與四大前沿解法批判圖</h2>
    <div class="diagram-card">
      <h3>圖譜二：實驗混淆機制（Confounding）與四大前沿解法批判圖 (T4 對照矩陣拓撲)</h3>
      <p>深度拆解盲測訂價實驗為何因 AI 語境腦補而失靈、為何純改提示詞淪為「挖東牆補西牆」，以及四大前沿解法與您的四大理論死穴批判、George Box 情境權變組合矩陣。</p>
      <img src="{IMG2}" alt="圖譜二">
    </div>
  </div>

  <div class="diagram-page">
    <h2 style="margin-top: 0;">陸、【全景視覺化圖譜附錄（三）】三篇合體「道・法・術」企業決策終極藍圖</h2>
    <div class="diagram-card">
      <h3>圖譜三：【三篇合體終極藍圖】企業數據科學與生成式 AI 決策之「道・法・術」三階架構 (T2 演進流程拓撲)</h3>
      <p>將《顧客需求不靠猜》（道：界定問題與方向）→《AI 能強化你的數據分析能力》（法：盤點能力與 ERP/CRM 情境底座）→《生成式 AI 正在顛覆市場研究》（術：前線市調實操與權變終審）完整貫通。</p>
      <img src="{IMG3}" alt="圖譜三">
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
