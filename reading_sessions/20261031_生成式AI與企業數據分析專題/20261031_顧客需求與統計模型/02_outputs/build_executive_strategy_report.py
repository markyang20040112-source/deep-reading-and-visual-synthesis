# -*- coding: utf-8 -*-
"""
build_executive_strategy_report.py
產出 Format B 結構化決策報告：
- 02_outputs/01_executive_strategy_report.md (Markdown 版本)
- 02_outputs/01_executive_strategy_report.pdf (高解析 A4 印刷級 PDF)
嚴格遵循 phase2_output/document_report_spec.md 與 scripts/pdf_report_engine.py 規範：
- 筆風堅持「白話直覺先行、由淺入深、杜絕晦澀黑話堆砌」
- 完整涵蓋：執行摘要、三方生態循環（造血引擎 vs 助燃劑）、道斯模型本質、少做多得五步驟、真實企業案例、商模差異與四道防偏見防線、自測清單
- 嵌入優化後的心智圖與量化圖表
- 調用 compile_html_to_pdf 與 verify_visual_outputs 逐頁驗收
"""

import os
import sys
from pathlib import Path

# 導入底層 pdf_report_engine 與 verify_visual_outputs
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
root_dir = SCRIPT_DIR
while root_dir and os.path.basename(root_dir) != "deep-reading-and-visual-synthesis":
    parent = os.path.dirname(root_dir)
    if parent == root_dir:
        break
    root_dir = parent

SKILLS_SCRIPTS = os.path.join(root_dir, ".agents", "skills", "deep-reading-and-visual-synthesis", "scripts")
if SKILLS_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILLS_SCRIPTS)

from pdf_report_engine import wrap_report_html, compile_html_to_pdf
from verify_visual_outputs import render_pdf_to_pngs, cleanup_preview_artifacts

OUT_DIR = SCRIPT_DIR
MD_OUT = os.path.join(OUT_DIR, "01_executive_strategy_report.md")
PDF_OUT = os.path.join(OUT_DIR, "01_executive_strategy_report.pdf")


def build_report_content():
    # 建立大章節內容（HTML 格式，配合 pdf_report_engine 印刷樣式）
    body_html = """
<!-- ========================================================================= -->
<!-- 第 1 頁：封面與壹、執行摘要 -->
<!-- ========================================================================= -->
<header style="margin-bottom: 20px; border-bottom: 3px solid #0284C7; padding-bottom: 12px;">
  <div style="font-size: 10pt; font-weight: 700; color: #0284C7; letter-spacing: 0.08em; text-transform: uppercase;">
    Executive Strategy Memo ｜ 深度決策策略備忘錄
  </div>
  <h1 style="font-size: 20pt; font-weight: 800; color: #0F172A; margin: 6px 0 6px 0; line-height: 1.25;">
    顧客需求不靠猜：用統計模型找回企業真金白銀的成長引擎
  </h1>
  <div style="font-size: 10.6pt; color: #475569; line-height: 1.45; font-weight: 500;">
    破除高管「自以為了得」的兩大盲點、解鎖少做多得的五步驟科學落地手冊，重建企業與客戶的造血正循環
  </div>
  <div style="margin-top: 10px; font-size: 8.8pt; color: #64748B;">
    <strong>主要研究依據：</strong> Vikas Mittal 等教授 7 年跨國實證研究（涵蓋 104 家上市 B2B 企業、18,840 位真實顧客、4,540 家企業 21 年 10-K 財報） ｜ <strong>編制日期：</strong> 2026 年 11 月
  </div>
</header>

<h2 style="margin-top: 0;">壹、執行摘要：為什麼高管每週開會 12 小時，卻在 72% 的時候猜錯客戶要什麼？</h2>

<p>
  在激烈的市場競爭中，幾乎所有企業領導人都堅信自己「非常了解客戶」。數據顯示，高達 93% 的企業高階主管，每週平均花費 4 到 12 個小時親自翻閱客訴紀錄、分析競爭對手動態，並召開跨部門策略會議。然而，一項長達 7 年、深入調查 104 家上市 B2B 公司與近兩萬名真實客戶的權威研究，卻揭露了一個令人震驚的殘酷真相：<strong>在 72% 的企業中，高管認定「客戶最在乎的事」，與客戶真實重視的需求幾乎毫無關係，甚至完全相反！</strong>
</p>

<p>
  問題從來不是出在主管「不夠認真」或「缺乏數據」，而是人類大腦天生存在嚴重的判斷偏誤。主管容易被眼前的顯眼事件（如昨天的某通嚴重客訴、對手新推出的酷炫功能）牽著走，或是憑直覺臆測未經驗證的因果關係。更嚴重的是，有高達 85.5% 的企業每兩年就徹底推翻一次策略優先順序，導致第一線員工疲於奔命，企業資源像胡亂撒胡椒粉一樣被稀釋殆盡。
</p>

<div class="card-grid-2" style="margin-top: 14px;">
  <div class="card" style="border-left: 4px solid #C2410C;">
    <div class="card-header" style="background: #FFF7F2; color: #9A3412;">
      ● 高管常犯的兩大直覺病灶（為什麼直覺不可靠？）
    </div>
    <div class="card-body">
      <p><strong>1. 選錯重點（抓小放大）：</strong> 誤把及格標準當作核心優勢。例如主管整天煩惱品質與降價，卻不知道客戶真正在乎的是「出問題時能不能 24 小時內幫我搞定」。</p>
      <p><strong>2. 頻繁換方向（策略陀螺）：</strong> 缺乏客觀數據支撐，會議上誰聲音大就聽誰的。必帝公司曾在一波流行下，一年內把「品質」從第 1 名降到第 8 名，客戶無所適從。</p>
    </div>
  </div>
  <div class="card" style="border-left: 4px solid #0284C7;">
    <div class="card-header" style="background: #F0F9FF; color: #075985;">
      ● 科學破局的巨大財務回饋（認知對齊的真金白銀）
    </div>
    <div class="card-body">
      <p><strong>營收成長 +9.2%：</strong> 當主管與客戶對「價值」的認知一致度每提高 12.5 分（量表 -100～+100），客戶回購與採購意願顯著放大。</p>
      <p><strong>毛利改善 +5.2% & 現金流 +8.8%：</strong> 不必再陷入價格血拼，具備強大定價自主權，把無效支出轉化為實質營運現金流。</p>
      <p><strong>市值提升 +11.1%：</strong> 資本市場給予清晰聚焦企業極高的長期估值溢價。</p>
    </div>
  </div>
</div>

<!-- ========================================================================= -->
<!-- 第 2 頁：貳、生態解剖導讀 -->
<!-- ========================================================================= -->
<h2 class="chapter-start">貳、生態解剖：企業、客戶與投資人的三方循環——別把「助燃劑」當成「造血引擎」</h2>

<p>
  要從根本解決策略失焦的問題，企業領導者必須先看清商業體系的能量流動本質。在商業世界中，存在「企業」、「客戶」與「投資人」三個關鍵角色，但他們的地位絕對不是對等的。
</p>

<p>
  <strong>「企業 ↔ 客戶」是唯一的價值造血引擎。</strong> 真正的商業價值，只有在客戶掏出真金白銀購買企業產品與服務的那一瞬間才會誕生。客戶之所以願意持續買單，是因為企業切中了他最在乎的痛點，給予他超越付費金額的實質效益；企業由此獲取營收與毛利，這才是公司長期存活與繁榮的唯一生命泉源。如果脫離了客戶的真實滿意，任何商業模式都是無源之水。
</p>

<p>
  <strong>「投資人」只是外部的輔助助燃劑。</strong> 資本市場提供的資金，本質是為了幫助造血引擎加快擴張腳步（例如興建新廠房、招募頂尖研發團隊），事後再合理分享「企業與客戶」共同創造的經營成果。投資人需要的是企業產值提升後帶來的投資回報，但投資人本身並不產出客戶價值。
</p>

<div class="card" style="margin: 14px 0; border-left: 4px solid #DC2626;">
  <div class="card-header" style="background: #FEF2F2; color: #991B1B;">
    ● 警惕危險訊號：當助燃劑反客為主的「結構性失靈」
  </div>
  <div class="card-body">
    <p>
      當外部熱錢過度湧入（如牛市或概念泡沫期），企業收到的投資資金甚至高於客戶付費營收時，高管極易陷入「討好投資人、忽視真客戶」的致命陷阱。高管為了滿足分析師每季的 EPS 預期或拉抬短期股價，往往採取以下毀滅性手段：
    </p>
    <ul>
      <li><strong>波音（Boeing）的悲劇：</strong> 將重心由「工程與飛安卓越」轉向「股東價值至上」，大幅削減核心機型的研發與品管支出，將現金大舉用於庫藏股護盤，終致 737 MAX 飛安災難與商譽崩盤。</li>
      <li><strong>迪士尼（Disney）的迷失：</strong> 為了追逐周邊商品與玩具衍生商機，讓部分影視作品淪為「大型賣玩具廣告」，強塞無助劇情的周邊角色，犧牲觀眾體驗與核心口碑。</li>
      <li><strong>AI 與 SaaS 泡沫的虛榮指標：</strong> 盲目補貼衝刺免洗註冊量或紙面訂閱數以推高估值，卻忽略客戶是否具備續約意願與真實 ROI。</li>
    </ul>
    <p style="margin-bottom: 0;">
      <strong>鐵律總結：</strong> 客戶買單才是撐起估值的唯一地基。下一頁我們將透過全景架構圖，完整拆解這套價值循環體系。
    </p>
  </div>
</div>

<!-- ========================================================================= -->
<!-- 第 3 頁：心智圖全景專頁（嚴格控制單頁高度，杜絕斷頁裁切） -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<figure style="margin: 0; padding: 0; text-align: center;">
  <img src="04_顧客-企業-投資者關係心智圖_Word直式版.png" alt="企業、客戶與投資人的價值循環架構圖"
       style="max-height: 252mm; width: auto; max-width: 98%; border: 1.5px solid #CBD5E1; border-radius: 8px;">
  <figcaption style="font-size: 8.8pt; color: #475569; text-align: center; margin-top: 6px;">
    <strong>圖 1｜商業生態核心價值循環架構圖：</strong> 堅守「企業 ↔ 客戶」造血核心，以統計模型為指針，讓投資人助燃劑發揮正向加速效應。
  </figcaption>
</figure>

<!-- ========================================================================= -->
<!-- 第 4 頁：參、科學破局（道斯模型、公式與三大反直覺實證案例） -->
<!-- ========================================================================= -->
<h2 class="chapter-start">參、科學破局：道斯線性模型與「提升潛力」的白話本質</h2>

<p>
  很多領導人會問：「我們天天在看數據，為什麼還是排不準優先順序？」心理學大師羅賓．道斯（Robyn Dawes）早在 1979 年的一篇經典研究中就給出了解答：<strong>人類專家擅長挑選相關變數（知道哪些事情有影響），但人類大腦天生極不擅長替變數排出精準的權重（分不清哪件事的影響力是大 5 倍還是大 10 倍）。</strong>
</p>

<p>
  這就像一位廚師知道一道名菜需要鹽、糖、醬油與香菜，但他若全憑心情隨意抓比例，味道一定每次都走樣。在企業策略中，品質、價格、售後服務、業務拜訪、AI 科技等都是大家熟知的變數，但主管憑直覺開會時，往往把每樣都當成「第一優先」，結果全員精力分散，什麼都做不好。
</p>

<div class="equation-box">
  <div class="equation-formula" style="font-size: 10.5pt; color: #0284C7; margin-bottom: 5px;">
    整體顧客價值（滿意度） ＝ 基準分 ＋ ∑ (各因素提升潛力 × 表現評分)
  </div>
  <div class="equation-formula" style="font-size: 10.5pt; color: #075985; margin-bottom: 6px;">
    每位客戶實際利潤貢獻 ＝ 基礎利潤 ＋ (價值財務轉換係數 × 整體顧客價值)
  </div>
  <p style="font-size: 8.8pt; color: #475569; margin-bottom: 0;">
    <strong>白話翻譯：</strong> 第一層模型算出改善某個環節能讓客戶整體評價跳升多少（提升潛力 Lift %）；第二層模型把評價對接內部會計總帳，檢驗高評價客戶是否真金白銀為公司帶來更多利潤。
  </p>
</div>

<p>
  當研究團隊運用雙層統計模型對真實企業進行診斷時，發現了令人震撼的「直覺剪刀差」：
</p>

<div class="card-grid-3" style="margin-top: 10px;">
  <div class="card" style="border-top: 3px solid #0284C7;">
    <div class="card-header" style="font-size: 9.6pt; color: #0284C7;">
      ● 教育服務機構
    </div>
    <div class="card-body" style="font-size: 9.0pt;">
      <p><strong>主管直覺：</strong> 認為 8 項服務要素均等重要，平均各分配 12.5% 預算。</p>
      <p><strong>真實數據：</strong>「24 小時內解決問題」提升潛力獨佔 <strong>85.0%</strong>！現場培訓僅 11%，其餘皆趨近零。主管原先浪費了 85% 的資源在無效處。</p>
    </div>
  </div>
  <div class="card" style="border-top: 3px solid #0F766E;">
    <div class="card-header" style="font-size: 9.6pt; color: #0F766E;">
      ● 工業維修公司
    </div>
    <div class="card-body" style="font-size: 9.0pt;">
      <p><strong>主管直覺：</strong> 認為加強現場作業安全規範頂多讓客戶價值感增加 2.3%。</p>
      <p><strong>真實數據：</strong> 客戶實際提升潛力高達 <strong>19.5%（相差 8.5 倍！）</strong>。因工業客戶停工一天損失數百萬，安全履約是巨大的隱形價值。</p>
    </div>
  </div>
  <div class="card" style="border-top: 3px solid #D97706;">
    <div class="card-header" style="font-size: 9.6pt; color: #D97706;">
      ● ITI 海外製造商
    </div>
    <div class="card-body" style="font-size: 9.0pt;">
      <p><strong>主管直覺：</strong> 整天想著低價與規格比拼，認為低報價才能贏得訂單。</p>
      <p><strong>真實數據：</strong>「低價與規格」只是基本門檻（提升潛力趨近零）；真正具 <strong>48% 提升潛力</strong>的是「每週主動更新進度」與「持續支援」。</p>
    </div>
  </div>
</div>

<!-- ========================================================================= -->
<!-- 第 5 頁：量化實證圖表專頁與財務回報剖析 -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h3 style="margin-top: 0; margin-bottom: 8px;">● 核心量化證據：直覺剪刀差反差圖與認知對齊之財務槓桿</h3>

<figure style="margin: 6px 0 12px 0; text-align: center;">
  <img src="03_quantitative_empirical_charts.png" alt="高管直覺預估與顧客真實提升潛力的剪刀差反差圖"
       style="max-width: 99%; height: auto; border: 1.5px solid #CBD5E1; border-radius: 8px;">
  <figcaption style="font-size: 8.8pt; color: #475569; text-align: center; margin-top: 4px;">
    <strong>圖 2｜實證量化證據：</strong> （左圖 1A）高管直覺預估 vs. 顧客實際提升潛力剪刀差；（右圖 1B）認知一致度每提高 12.5 分所驅動之各項財務與市場回報。
  </figcaption>
</figure>

<p>
  圖 2B 揭示了認知對齊帶來的真金白銀回報。研究顯示，高管與顧客的認知一致度在 -100 分到 +100 分的量表上，<strong>每提高 12.5 分，將釋放出驚人的經營紅利：</strong>
</p>

<ul>
  <li><strong>營業收入增加 +9.2%：</strong> 當企業不再胡亂推銷客戶不想要的功能，而是聚焦在客戶最在乎的痛點時，客戶續約率與採購規模顯著擴大。</li>
  <li><strong>毛利率實質改善 +5.2%：</strong> 卓越的服務讓客戶產生信賴與依賴，企業不再被迫參與無底線的價格戰，取得強大定價自主權。</li>
  <li><strong>自由現金流提升 +8.8%：</strong> 砍除大量無效的跨部門專案與行政流程，釋放沉澱資金與人力，讓營運活動轉化為充沛的真實造血現金。</li>
  <li><strong>企業市值躍升 +11.1%：</strong> 資本市場始終獎勵專注且具備強大造血能力的企業，給予更高的本益比溢價。</li>
</ul>

<!-- ========================================================================= -->
<!-- 第 6 頁：肆、落地實戰（少做多得五步驟整頁緊湊收斂） -->
<!-- ========================================================================= -->
<h2 class="chapter-start">肆、落地實戰：少做多得的「五步驟」操作手冊與真實企業案例</h2>

<p>
  哈佛商業評論研究團隊與數十家企業反覆試驗，提煉出經過嚴格實證檢驗的「少做多得（Do Less, Get More）」五步驟落地法：
</p>

<div class="card-grid-2" style="margin: 10px 0;">
  <div class="card" style="border-left: 4px solid #0F766E;">
    <div class="card-header" style="background: #F2FAF8; color: #115E59; font-size: 9.6pt;">
      ● 步驟一：用數據揭露認知落差
    </div>
    <div class="card-body" style="font-size: 8.9pt;">
      <p><strong>正視瞎忙真相：</strong> ITI 製造商調查前 97% 員工自認清楚策略，調查後發現有 65 種說法，全員只有 24% 時間面對客戶；S-SET 營收 5,000 萬美元卻同時跑 42 項專案。</p>
      <p><strong>行動處方：</strong> 進行雙盲量化調查，讓主管親眼看見直覺與客戶心聲的零相關，破除內部盲目自滿。</p>
    </div>
  </div>
  <div class="card" style="border-left: 4px solid #0284C7;">
    <div class="card-header" style="background: #F0F9FF; color: #075985; font-size: 9.6pt;">
      ● 步驟二：只選提升潛力最高的 1～2 項
    </div>
    <div class="card-body" style="font-size: 8.9pt;">
      <p><strong>展現策略勇氣：</strong> 統計模型會將所有因素依提升潛力排序，管理層必須嚴格限制自己「只挑前 1 到 2 項」，嚴禁貪多！</p>
      <p><strong>實例印證：</strong> ITI 鎖定每週進度更新與持續支援（預期營收+9.8%）；S-SET 鎖定「快速報價」（預估帶動營收+18.6%）。</p>
    </div>
  </div>
  <div class="card" style="border-left: 4px solid #D97706;">
    <div class="card-header" style="background: #FFFBEB; color: #B45309; font-size: 9.6pt;">
      ● 步驟三：把這 1～2 件事融入全員每天日常
    </div>
    <div class="card-body" style="font-size: 8.9pt;">
      <p><strong>化為肌肉記憶：</strong> 策略不是口號，必須排入每天行程。ITI 將「每週三主動寄進度報告」納入全員職務，年報告由 &lt;30次 暴增至 <strong>3,524 次</strong>！</p>
      <p><strong>工具賦能：</strong> S-SET 為客服配備頂級報價軟體與高速電腦，報價時間由 18 小時劇降至 <strong>3 小時以內</strong>。</p>
    </div>
  </div>
  <div class="card" style="border-left: 4px solid #DC2626;">
    <div class="card-header" style="background: #FEF2F2; color: #991B1B; font-size: 9.6pt;">
      ● 步驟四：大膽砍掉沒有價值的冗餘活動
    </div>
    <div class="card-body" style="font-size: 8.9pt;">
      <p><strong>化解政治角力：</strong> 過去砍專案是政治鬥爭；有模型數據撐腰，提升潛力為零的活動就能客觀停辦，釋放逾 <strong>30% 寶貴工時</strong>。</p>
      <p><strong>驚人成效：</strong> ITI 四年間銷售高於同業 19.3%，利潤率+43%，<strong>股價暴漲 162%（標普僅34%）</strong>；S-SET 人均銷售激增 52%。</p>
    </div>
  </div>
</div>

<div class="card" style="border-left: 4px solid #4F46E5; margin-top: 6px;">
  <div class="card-header" style="background: #EEF2FF; color: #3730A3; font-size: 9.6pt;">
    ● 步驟五：做到卓越水準之後，才對外大張旗鼓宣傳
  </div>
  <div class="card-body" style="font-size: 8.9pt;">
    <p>
      <strong>先做再說的誠信紀律：</strong> 平庸公司習慣在執行尚未達標前搶先打行銷廣告，結果客戶一體驗就跳票。S-SET 刻意等到報價時間穩定縮至 5 小時內，才對外宣布「快速報價保證」，並將報價速度綁定員工獎金；ITI 也是在進度系統運作兩年後，才主打「透明、可預測、負責到底」，使<strong>定價能力提高 20% 到 30%</strong>！規模 800 億美元的跨國銀行同樣循此步驟，鎖定縮短等候時間與線上安全，6 年內滿意度提升 18%，營收成長 33%，<strong>股價大漲 200%（道瓊僅 140%）</strong>。
    </p>
  </div>
</div>

<!-- ========================================================================= -->
<!-- 第 7 頁：伍、延伸防禦（商模差異與四道防偏見防線） -->
<!-- ========================================================================= -->
<h2 class="chapter-start">伍、延伸防禦：商業模式差異與防範演算法偏見的「四道關卡」</h2>

<p>
  當企業將這套方法論推廣至更多事業單位時，必須釐清兩項深層認知：商業模式的本質差異，以及如何防範統計模型淪為《大數據的傲慢與偏見》中所警惕的「偏見擴大器」。
</p>

<h3>1. 商業模式差異：B2B 的檯面硬指標 vs. B2C 的幕後絲滑體驗</h3>
<p>
  <strong>B2B 客戶是理性組織採購：</strong> 客戶購買企業服務時，背負著自身財務損益責任。因此，供應商若能展示領先的「AI 能力」與「專案執行力」，客戶就能在自身財報上具體量化出節省的成本與增加的產能。這兩者在 B2B 會直接成為<strong>採購合約中的硬指標</strong>。
</p>
<p>
  <strong>B2C 客戶買的是最終體驗：</strong> 消費者使用 Netflix 或叫外送時，根本不在乎幕後採用了什麼複雜模型。消費者要的是「推薦有沒有打中我」、「外送有沒有 20 分鐘熱騰騰送達」。在 B2C 環境中，AI 必須<strong>隱身於幕後</strong>，轉化為無感的極致體驗。
</p>

<h3>2. 建立防範演算法偏見的四道防線（破除垃圾進、垃圾出）</h3>
<p>
  統計模型能消除人類隨機雜訊，但若輸入的問卷題目或目標函數本身就帶有高管的主觀盲點，模型將淪為加速犯錯的工具。企業必須落實以下四道防線：
</p>

<table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
  <thead>
    <tr>
      <th style="width: 22%; border-top: 2px solid #0F172A; border-bottom: 1.5px solid #0F172A; padding: 6px 8px;">防線關卡</th>
      <th style="width: 40%; border-top: 2px solid #0F172A; border-bottom: 1.5px solid #0F172A; padding: 6px 8px;">核心作法（白話解釋）</th>
      <th style="width: 38%; border-top: 2px solid #0F172A; border-bottom: 1.5px solid #0F172A; padding: 6px 8px;">防範的致命盲點</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="font-weight: 700; padding: 6px 8px; border-bottom: 1px solid #E2E8F0;">第一關：開放式痛點探索</td>
      <td style="padding: 6px 8px; border-bottom: 1px solid #E2E8F0;">先深入訪談最近流失的客戶與第一線核心客訴，由客戶口中講出的痛點決定問卷題目。</td>
      <td style="padding: 6px 8px; border-bottom: 1px solid #E2E8F0;">防範「題目遺漏偏誤」：避免問卷只問高管自認得意的話題，漏掉真實致命問題。</td>
    </tr>
    <tr>
      <td style="font-weight: 700; padding: 6px 8px; border-bottom: 1px solid #E2E8F0;">第二關：間接推導而非直問</td>
      <td style="padding: 6px 8px; border-bottom: 1px solid #E2E8F0;">不要直接問客戶「哪項對你重要」（客戶會每項都勾重要），而是讓客戶評分各項表現與總體滿意度，由模型推導出權重。</td>
      <td style="padding: 6px 8px; border-bottom: 1px solid #E2E8F0;">防範「社會期許偏誤」：客戶口頭說永續很重要，但下單時只看報價與交期。</td>
    </tr>
    <tr>
      <td style="font-weight: 700; padding: 6px 8px; border-bottom: 1px solid #E2E8F0;">第三關：綁定真實會計帳本</td>
      <td style="padding: 6px 8px; border-bottom: 1px solid #E2E8F0;">將滿意度調查結果直接串接 ERP/財務系統，看給予高分的客戶是否真的有較高毛利與回購率。</td>
      <td style="padding: 6px 8px; border-bottom: 1px solid #E2E8F0;">防範「虛榮指標陷阱」：避免公司自嗨滿意度高達 90%，但公司實際上一直在虧損。</td>
    </tr>
    <tr>
      <td style="font-weight: 700; padding: 6px 8px; border-bottom: 2px solid #0F172A;">第四關：隨機對照實驗（A/B Test）</td>
      <td style="padding: 6px 8px; border-bottom: 2px solid #0F172A;">大規模推廣前，先在小範圍分組實驗（如市值 800 億美元銀行測試大廳等候與線上交易安全）。</td>
      <td style="padding: 6px 8px; border-bottom: 2px solid #0F172A;">防範「假性相關（Correlation ≠ Causation）」：確保該動作真的能帶來業績，而非碰巧市場景氣好。</td>
    </tr>
  </tbody>
</table>

<!-- ========================================================================= -->
<!-- 第 8 頁：陸、高管自測檢核清單與結語 -->
<!-- ========================================================================= -->
<h2 class="chapter-start">陸、高管自測檢核清單：我們公司是否正陷入「直覺失焦」？</h2>

<p>
  請企業管理團隊在每季策略會議開始前，誠實檢視以下五大健康檢查問題。若勾選「是」超過兩項，代表貴公司的造血引擎已出現失焦警訊：
</p>

<table style="width: 100%; border-collapse: collapse; margin: 12px 0;">
  <thead>
    <tr>
      <th style="width: 10%; text-align: center; border-top: 2px solid #0F172A; border-bottom: 1.5px solid #0F172A; padding: 6px 8px;">項次</th>
      <th style="width: 32%; border-top: 2px solid #0F172A; border-bottom: 1.5px solid #0F172A; padding: 6px 8px;">自測檢視項目</th>
      <th style="width: 30%; border-top: 2px solid #0F172A; border-bottom: 1.5px solid #0F172A; padding: 6px 8px;">現況危險徵兆（自問）</th>
      <th style="width: 28%; border-top: 2px solid #0F172A; border-bottom: 1.5px solid #0F172A; padding: 6px 8px;">科學矯正處方</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align: center; font-weight: 700; border-bottom: 1px solid #E2E8F0; padding: 6px 8px;">1</td>
      <td style="border-bottom: 1px solid #E2E8F0; padding: 6px 8px;"><strong>策略版本一致度</strong></td>
      <td style="border-bottom: 1px solid #E2E8F0; padding: 6px 8px;">問 5 位主管公司今年的第一優先是什麼，能得到 3 種以上不同答案？</td>
      <td style="border-bottom: 1px solid #E2E8F0; padding: 6px 8px;">啟動客觀顧客調查，強制對齊單一量表。</td>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: 700; border-bottom: 1px solid #E2E8F0; padding: 6px 8px;">2</td>
      <td style="border-bottom: 1px solid #E2E8F0; padding: 6px 8px;"><strong>在線專案數量</strong></td>
      <td style="border-bottom: 1px solid #E2E8F0; padding: 6px 8px;">公司同時運作超過 15 個以上標榜「高度重要」的跨部門專案？</td>
      <td style="border-bottom: 1px solid #E2E8F0; padding: 6px 8px;">利用模型提升潛力，只留前 1～2 項，其餘封存。</td>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: 700; border-bottom: 1px solid #E2E8F0; padding: 6px 8px;">3</td>
      <td style="border-bottom: 1px solid #E2E8F0; padding: 6px 8px;"><strong>優先順序變動頻率</strong></td>
      <td style="border-bottom: 1px solid #E2E8F0; padding: 6px 8px;">過去 3 年內，公司核心追求的 KPI 主軸是否已經大改過 2 次以上？</td>
      <td style="border-bottom: 1px solid #E2E8F0; padding: 6px 8px;">認知到顧客深層需求極度穩定，維持戰略定力。</td>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: 700; border-bottom: 1px solid #E2E8F0; padding: 6px 8px;">4</td>
      <td style="border-bottom: 1px solid #E2E8F0; padding: 6px 8px;"><strong>一線員工客戶工時</strong></td>
      <td style="border-bottom: 1px solid #E2E8F0; padding: 6px 8px;">第一線銷售與服務人員每天花在客戶身上的時間低於總工時的 40%？</td>
      <td style="border-bottom: 1px solid #E2E8F0; padding: 6px 8px;">砍除無效內部行政與對帳追單，釋放 30% 工時。</td>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: 700; border-bottom: 2px solid #0F172A; padding: 6px 8px;">5</td>
      <td style="border-bottom: 2px solid #0F172A; padding: 6px 8px;"><strong>宣傳與執行的時序</strong></td>
      <td style="border-bottom: 2px solid #0F172A; padding: 6px 8px;">是否常在服務品質尚未達到產業頂尖前，就搶先對市場做行銷承諾？</td>
      <td style="border-bottom: 2px solid #0F172A; padding: 6px 8px;">堅持「做到卓越才對外宣揚」，保護品牌定價權。</td>
    </tr>
  </tbody>
</table>

<div style="margin-top: 18px; padding: 14px 18px; background: #0F172A; color: #F8FAFC; border-radius: 8px;">
  <div style="font-size: 10.5pt; font-weight: 700; color: #38BDF8; margin-bottom: 5px;">
    ★ 結語：少做多得，找回企業最純粹的造血力量
  </div>
  <div style="font-size: 9.3pt; line-height: 1.62; color: #E2E8F0;">
    卓越的企業領導人從來不需要比別人聰明十倍，而是懂得放下「我懂客戶」的直覺執念，用簡單卻穩健的統計線性模型看清現實。真正的商業成長，永遠不是來自把每件事都做得平庸，而是敢於砍掉 90% 不具提升潛力的瑣碎計畫，傾全公司之力，把客戶真正在乎的那一兩件事做到徹底卓越。當客戶為此主動回購與推薦，企業的造血循環便生生不息，投資人亦能共享長期豐碩的果實。
  </div>
</div>
"""
    return body_html


def build_markdown_report():
    md_content = """# 顧客需求不靠猜：用統計模型找回企業真金白銀的成長引擎
> **文件屬性**：高階決策備忘錄（Executive Strategy Memo） ｜ Format B 結構化綜合報告  
> **研究依據**：Vikas Mittal 等教授 7 年跨國實證研究（104 家上市 B2B 企業、18,840 位顧客、4,540 家企業 21 年 10-K 財報）  
> **發布日期**：2026 年 11 月  

---

## 壹、執行摘要：為什麼高管每週開會 12 小時，卻在 72% 的時候猜錯客戶要什麼？

在激烈的市場競爭中，幾乎所有企業領導人都堅信自己「非常了解客戶」。數據顯示，高達 93% 的企業高階主管，每週平均花費 4 到 12 個小時親自翻閱客訴紀錄、分析競爭對手動態，並召開跨部門策略會議。然而，一項長達 7 年、深入調查 104 家上市 B2B 公司與近兩萬名真實客戶的權威研究，卻揭露了一個令人震驚的殘酷真相：**在 72% 的企業中，高管認定「客戶最在乎的事」，與客戶真實重視的需求幾乎毫無關係，甚至完全相反！**

問題從來不是出在主管「不夠認真」或「缺乏數據」，而是人類大腦天生存在嚴重的判斷偏誤。主管容易被眼前的顯眼事件（如昨天的某通嚴重客訴、對手新推出的酷炫功能）牽著走，或是憑直覺臆測未經驗證的因果關係。更嚴重的是，有高達 85.5% 的企業每兩年就徹底推翻一次策略優先順序，導致第一線員工疲於奔命，企業資源像胡亂撒胡椒粉一樣被稀釋殆盡。

### ● 高管常犯的兩大直覺病灶
1. **選錯重點（抓小放大）**：誤把及格標準當作核心優勢。例如主管整天煩惱品質與降價，卻不知道客戶真正在乎的是「出問題時能不能 24 小時內幫我搞定」。
2. **頻繁換方向（策略陀螺）**：缺乏客觀數據支撐，會議上誰聲音大就聽誰的。必帝公司曾在一波流行下，一年內把「品質」從第 1 名降到第 8 名，客戶無所適從。

### ● 科學破局的巨大財務回饋（認知對齊的真金白銀）
- **營收成長 +9.2%**：當主管與客戶對「價值」的認知一致度每提高 12.5 分（量表 -100～+100），客戶回購與採購意願顯著放大。
- **毛利改善 +5.2% & 現金流 +8.8%**：不必再陷入價格血拼，具備強大定價自主權，把無效支出轉化為實質營運現金流。
- **市值提升 +11.1%**：資本市場給予清晰聚焦企業極高的長期估值溢價。

---

## 貳、生態解剖：企業、客戶與投資人的三方循環——別把「助燃劑」當成「造血引擎」

要從根本解決策略失焦的問題，企業領導者必須先看清商業體系的能量流動本質。在商業世界中，存在「企業」、「客戶」與「投資人」三個關鍵角色，但他們的地位絕對不是對等的。

- **「企業 ↔ 客戶」是唯一的價值造血引擎**：真正的商業價值，只有在客戶掏出真金白銀購買企業產品與服務的那一瞬間才會誕生。客戶之所以願意持續買單，是因為企業切中了他最在乎的痛點，給予他超越付費金額的實質效益；企業由此獲取營收與毛利，這才是公司長期存活與繁榮的唯一生命泉源。
- **「投資人」只是外部的輔助助燃劑**：資本市場提供的資金，本質是為了幫助造血引擎加快擴張腳步（例如興建新廠房、招募頂尖研發團隊），事後再合理分享「企業與客戶」共同創造的經營成果。
- **助燃劑反客為主的結構性失靈**：當外部熱錢過度湧入時，高管極易陷入「討好投資人、輕忽真客戶」的致命陷阱。例如波音公司為迎合華爾街短期估值與股息，過度樽節工程研發與品管成本，終致 737 MAX 嚴重飛安危機；迪士尼部分影視為賣周邊玩具而硬塞角色，犧牲故事品質。一旦造血引擎熄火，崩盤只是時間問題。

![圖 1｜商業生態核心價值循環圖](./04_顧客-企業-投資者關係心智圖_Word直式版.png)

---

## 參、科學破局：道斯線性模型與「提升潛力」的白話本質

很多領導人會問：「我們天天在看數據，為什麼還是排不準優先順序？」心理學大師羅賓．道斯（Robyn Dawes）早在 1979 年的一篇經典研究中就給出了解答：**人類專家擅長挑選相關變數（知道哪些事情有影響），但人類大腦天生極不擅長替變數排出精準的權重（分不清哪件事的影響力是大 5 倍還是大 10 倍）。**

這就像一位廚師知道一道名菜需要鹽、糖、醬油與香菜，但他若全憑心情隨意抓比例，味道一定每次都走樣。在企業策略中，品質、價格、售後服務、業務拜訪、AI 科技等都是大家熟知的變數，但主管憑直覺開會時，往往把每一樣都當成「絕對重要」，結果全員精力分散，什麼都做不好。

### 雙層統計模型本質
1. **第一層模型（顧客價值層）**：利用客觀統計迴歸，計算出改善單一項目對整體顧客價值的「提升潛力（Lift Potential）」。
2. **第二層模型（會計連結層）**：將顧客價值評估直接串接公司內部的真實會計總帳，檢驗高評價是否真的帶來營收、毛利率與客戶留存的同步增長。

![圖 2｜實證量化證據：直覺剪刀差與財務槓桿](./03_quantitative_empirical_charts.png)

### 反直覺實證案例拆解
1. **教育服務機構**：主管直覺以為 8 個項目重要度均等（各 12.5%），但數據顯示「24 小時內解決顧客問題」一項的提升潛力獨佔 **85.0%**，現場培訓僅 11%，其餘皆趨近於零！
2. **工業維修公司**：主管直覺認為現場遵守安全作業頂多提升顧客價值 2.3%，但客戶實際提升潛力高達 **19.5%（差距 8.5 倍！）**。
3. **ITI 製造商**：主管以為低價與品質是制勝關鍵，但模型揭露這兩項只是及格門檻（提升潛力不到 4%），真正驅動高達 48% 提升潛力的是「每週主動更新進度」與「持續支援」。

---

## 肆、落地實戰：少做多得的「五步驟」操作手冊與真實企業案例

哈佛商業評論研究團隊提煉出經過嚴謹驗證的「少做多得（Do Less, Get More）」五步驟落地法：

1. **第一步：用數據揭露認知落差（正視「全員都在瞎忙」的真相）**
   - *案例*：ITI 製造商調查前 97% 員工自認清楚策略，調查後發現有 65 種版本，全員只有 24% 時間服務客戶；S-SET 流體經銷商 5,000 萬美元營收卻跑 42 項專案。
2. **第二步：用統計模型只挑選提升潛力最高的 1 到 2 個核心因素**
   - *原則*：絕不貪多，嚴格鎖定前兩項。ITI 鎖定「每週進度更新」與「持續支援」；S-SET 鎖定「快速報價」。
3. **第三步：把這 1～2 件事徹底融入每位員工的每天日常**
   - *落實*：ITI 將「每週三主動發送進度 Email」納入全員職務，年報告次數從不到 30 次暴增至 **3,524 次**；S-SET 汰除 2.2 萬個重複 SKU，引進頂級報價工具，報價時間從 18 小時縮至 **3 小時內**。
4. **第四步：依據模型數據大膽砍掉沒有價值的冗餘活動（化解辦公室政治角力）**
   - *成效*：有數據撐腰，砍計畫不再是政治鬥爭。ITI 釋放三成工時，4 年間銷售額高出同業 19.3%，利潤率提升 43%，**股價暴漲 162%（同期標普 34%、羅素 8%）**；S-SET 業務多出 35% 時間接觸客戶，人均銷售激增 52%。
5. **第五步：做到卓越水準之後，才對外大張旗鼓宣傳**
   - *紀律*：拒絕承諾跳票。S-SET 報價壓進 5 小時後才推出品牌保證並連結績效獎金；ITI 卓越後主打「透明可預測」，**定價能力提高 20%～30%**。市值 800 億美元銀行改善等候時間與線上安全，營收增 33%，**股價大漲 200%（道瓊 140%）**。

---

## 伍、延伸防禦：商業模式差異與防範演算法偏見的「四道關卡」

### 1. 商業模式差異：B2B 的硬指標 vs. B2C 的幕後絲滑體驗
- **B2B 客戶是理性組織**：採購決策直接影響其自身財務獲利，故「AI 科技實力」與「專案執行力」會直接成為合約上的硬指標。
- **B2C 客戶看重最終體驗**：消費者買的是省時、好玩、便宜。AI 一樣至關重要，但必須隱藏在推薦、派單與風控的幕後。

### 2. 防範「數學毀滅武器」的四道防線
1. **第一關（開放式探索）**：深入訪談流失客戶與真實客訴，由客戶痛點產生問卷題目，防止高管自戀式出題。
2. **第二關（間接推導重要性）**：用統計迴歸推算權重，不直接問「哪項重要」，破除客戶每項都勾重要的社會期許偏誤。
3. **第三關（對接會計帳本）**：將滿意度串連 ERP 真實利潤與回購，杜絕自嗨虛榮指標。
4. **第四關（隨機對照實驗 A/B Test）**：小規模分組實驗驗證因果關係，避免把巧合當因果。

---

## 陸、高管自測檢核清單

| 項次 | 檢視面向 | 現況危險徵兆（若符合請打勾） | 科學矯正處方 |
| :---: | :--- | :--- | :--- |
| **1** | **策略版本一致度** | 問 5 位主管公司今年第一優先，得到 3 種以上答案 | 啟動顧客雙盲調查，強制量化對齊 |
| **2** | **在線專案數量** | 公司同時運作超過 15 個跨部門重要專案 | 依提升潛力只留前 1～2 項，其餘封存 |
| **3** | **優先順序變動** | 過去 3 年核心 KPI 主軸已經大改過 2 次以上 | 認知客戶深層需求極度穩定，維持定力 |
| **4** | **一線客戶工時** | 業務與服務人員面對客戶工時低於 40% | 砍除無效內部行政，釋放 30% 工時 |
| **5** | **宣傳與執行的時序** | 服務品質尚未頂尖前，就搶先向市場做行銷承諾 | 堅持「做到卓越才宣揚」，保障定價權 |

---

> **結語**：真正的商業成長，從來不是來自把每件事都做得平庸，而是敢於砍掉 90% 不具提升潛力的瑣碎計畫，傾全公司之力，把客戶真正在乎的那一兩件事做到徹底卓越。
"""
    return md_content


def main():
    print("1. Generating Markdown report...")
    md_text = build_markdown_report()
    Path(MD_OUT).write_text(md_text, encoding="utf-8")
    print("Saved:", MD_OUT)

    print("2. Generating HTML report & compiling to PDF...")
    body_html = build_report_content()
    html_content = wrap_report_html(
        title="顧客需求不靠猜：用統計模型找回企業真金白銀的成長引擎（高階策略備忘錄）",
        body_html=body_html,
        theme="modern_sans",
        body_pt=10.5,
    )
    
    # 將 html 寫入臨時檔以便相對路徑圖片讀取
    tmp_html = os.path.join(OUT_DIR, "_tmp_report_preview.html")
    Path(tmp_html).write_text(html_content, encoding="utf-8")
    
    try:
        compiled_pdf = compile_html_to_pdf(tmp_html, PDF_OUT, cleanup_temp_html=False)
        print("PDF compiled successfully:", compiled_pdf)
    finally:
        if os.path.exists(tmp_html):
            os.remove(tmp_html)

    print("3. Verifying visual output using render_pdf_to_pngs...")
    png_previews = render_pdf_to_pngs(PDF_OUT, out_dir=OUT_DIR, dpi=180)
    print(f"Generated {len(png_previews)} preview pages:")
    for p in png_previews:
        print("  -", p)

    return png_previews


if __name__ == "__main__":
    main()
