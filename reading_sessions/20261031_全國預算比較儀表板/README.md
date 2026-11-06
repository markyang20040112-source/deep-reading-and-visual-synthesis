# 全國預算比較儀表板 (National Budget Comparison Dashboard)

> 專為解決政府預算資料「項目繁雜、彩虹沙拉色盤、認知超載」痛點而生的現代化資料儀表板。嚴格遵循個人圖表配色規範（CIELAB 4 色認知平衡、循序色階、9 階對稱發散色階），並封裝為可直接上傳至獨立 Git 儲存庫並一鍵發布為網站的獨立專案。

---

## 🌟 核心特色與改進亮點

### 1. 拒絕「彩虹沙拉」色盤，首創「智慧 4+1 聚焦視角」
- **原版痛點**：將 37 個政事別/歲入來源一股腦塞入長條圖，每種項目各配一個高飽和刺眼顏色，如同混亂的彩虹條碼，讀者無法聚焦。
- **新版設計**：自動計算出佔全體逾 60% 的前四大核心支柱（如：教育支出、交通支出、福利服務、民政支出），分別賦予四個規範顏色，其餘 30+ 個零散長尾項目自動聚合為典雅的「其他項目（中性灰）」，結構一目了然。

### 2. 嚴格貫徹 CIELAB 感知配色規範
- **類別四色均一化**：明度精確錨定在 $L^* \approx 71 \sim 72\%$，在白底背景上對比清晰，四色視覺重量等權，粉藍不再發灰、綠色擺脫黃濁感。
- **5 階物理等差循序色階**：用於各縣市排行榜與深鑽熱力，漸層平滑自然，消除舊版前半段黏滯、後半段斷崖黑沉的問題。
- **9 階對稱發散色階（年增減專用）**：雙向對稱（負向墨青 `#0E5B6B` ➔ 中立冷灰 `#F5F6F7` ➔ 正向深栗橘 `#884725`），杜絕正向過豔帶來的認知偏差。

### 3. 多維度視覺化切換（4 大視角）
1. **結構堆疊視角（4+1 聚合長條圖）**：橫向長條完整呈現 21 縣市預算結構，支援排序與百分比切換。
2. **縣市排行榜（Ranking Leaderboard）**：總額與人均預算由高至低完整排行，套用專屬循序色階。
3. **增減發散分析（Growth & Deviation）**：針對「與去年差異」特化，雙向展示各縣市年度預算擴張或緊縮。
4. **單一項目深鑽（Deep-dive Explorer）**：可任意選擇單一政事別（如：教育支出、環境保護、醫療保健），獨立檢視各縣市投放力度與佔比。

### 4. 完整明細表與 CSV 下載
- 內建各縣市人口、預算總規模、人均、年增減與結構明細。
- 支援即時關鍵字搜尋與「一鍵匯出 CSV」。

---

## 📂 專案檔案結構

本專案完全自包含（Self-contained），無任何外部後端依賴：

```text
20261031_全國預算比較儀表板/
├── index.html                        # 主頁面（響應式 UI、控制列、KPI 卡與圖表容器，採 ./ 純相對路徑）
├── css/
│   └── style.css                     # 配色規範 CSS 變數與微調樣式
├── js/
│   └── dashboard.js                  # 資料處理引擎、全域固定類別色碼映射、ECharts 驅動與狀態管理
├── data/
│   ├── budget_data.js                # 預編譯離線資料包（保證雙擊 index.html 即可本機秒開）
│   └── budget_data.json              # 標準結構化 JSON 資料
├── generate_chart.py                 # 出版級靜態全景儀表板圖生成腳本（Matplotlib GridSpec）
├── 全台預算比較儀表板_視覺化圖表.png  # 出版級高解析度靜態全景儀表板圖
├── .nojekyll                         # GitHub Pages 免 Jekyll 編譯加速標記檔
├── .gitignore                        # Git 獨立版控忽略設定清單
└── README.md                         # 專案說明與獨立 Git 網站發布指南
```

---

## 🚀 本機預覽方式

### 方式 A：直接雙擊開啟（最簡單，零安裝）
因為本專案已將預算資料預先載入至 `./data/budget_data.js`，並全面採用 `./` 純相對路徑，您可以**直接在檔案總管中雙擊 `index.html`**，瀏覽器便能直接離線運行所有圖表與互動功能！

### 方式 B：使用靜態本機伺服器
若您習慣在本地 HTTP 伺服器預覽，可在本專案目錄下執行：
```bash
# Python
python -m http.server 8000

# 或 Node.js
npx serve .
```
接著在瀏覽器打開 `http://localhost:8000` 即可。

---

## 🌐 如何綁定獨立 Git 儲存庫並架設成網站（GitHub Pages / Vercel）

本專案已封裝為 **Git-Ready 零後端靜態網站結構**（內含 `.nojekyll`、`.gitignore` 與 `./` 純相對路徑），完美相容於 GitHub Pages 子路徑（`https://<username>.github.io/<repo-name>/`）與根網域。以下提供三種標準部署方式：

### 方式一：使用 GitHub CLI (`gh`) 一鍵自動建庫＋開通 GitHub Pages（最快）
若您的終端機已安裝並登入 GitHub CLI（`gh auth status`），只需執行：
```bash
cd "reading_sessions/20261031_全國預算比較儀表板"

git init
git config user.name "markyang20040112-source"
git config user.email "markyang20040112-source@users.noreply.github.com"
git add -A
git commit -m "feat(dashboard): initial release of taiwan budget comparison dashboard"
git branch -M main

# 自動在 GitHub 建立公開儲存庫並推送
gh repo create taiwan-budget-dashboard --public --source=. --remote=origin --push

# 一鍵啟用 GitHub Pages（參數加引號相容 PowerShell 與 Bash）
gh api repos/{owner}/{repo}/pages -X POST -F build_type=legacy -F "source[branch]=main" -F "source[path]=/"

# 【雙倉庫防衝突護欄】若本目錄同時位於外層知識庫主倉庫內，推送後請立即移除內層 .git 避免外層產生 gitlink 空指標：
# PowerShell: Remove-Item -Recurse -Force .git
# Bash:       rm -rf .git
```

### 方式二：手動綁定新建的空白 Git 儲存庫（支援 `main` 或 `gh-pages` 分支）
1. 前往 [GitHub](https://github.com/new) 建立空白 Public 儲存庫（例如 `taiwan-budget-dashboard`，不要勾選初始化 README）。
2. 於終端機執行推送：
```bash
cd "reading_sessions/20261031_全國預算比較儀表板"

git init
git config user.name "markyang20040112-source"
git config user.email "markyang20040112-source@users.noreply.github.com"
git add -A
git commit -m "feat(dashboard): initial commit of taiwan budget comparison dashboard"
git branch -M main
git remote add origin https://github.com/<您的使用者名稱>/taiwan-budget-dashboard.git

# 推送至 main 分支（若欲推送至 gh-pages 分支可改用 git push -u origin main:gh-pages --force）
git push -u origin main

# 【雙倉庫防衝突護欄】若本目錄位於外層主倉庫內，推送成功後請移除內層 .git 以確保外層主倉庫完整備份所有前端檔案：
# PowerShell: Remove-Item -Recurse -Force .git
# Bash:       rm -rf .git
```
3. 進入該 GitHub 專案頁面 ➔ **Settings** ➔ **Pages** ➔ **Branch** 選擇 `main`（或 `gh-pages`）與 `/(root)` ➔ **Save**，約 1 分鐘後即可造訪 `https://<您的使用者名稱>.github.io/taiwan-budget-dashboard/`！

### 方式三：從外層主倉庫直接執行 `git subtree` 推送（零內層 `.git`）
若本專案已先 commit 至外層 `deep-reading-and-visual-synthesis` 主倉庫，可直接在外層根目錄執行：
```bash
git subtree split --prefix="reading_sessions/20261031_全國預算比較儀表板" -b dashboard-deploy
git push https://github.com/<您的使用者名稱>/taiwan-budget-dashboard.git dashboard-deploy:main --force
git branch -D dashboard-deploy
```

*(備註：亦完全支援直接匯入 Vercel 或 Netlify，只需選擇該 Git Repo，無須任何建置指令即可一鍵發布。)*

---

## 🎨 配色規範對照速查

| 角色 | 色彩名稱 | HEX 色碼 | 適用場景 |
| :---: | :---: | :---: | :--- |
| **主色** | 暖杏蜜橘 | `#ECA072` | 類別第一大項、循序色階基準、發散正向中度 |
| **次色** | 霧靄青藍 | `#5DBACD` | 類別第二大項、深鑽對比尺度、發散負向中度 |
| **第三色** | 落櫻粉黛 | `#E89BB6` | 類別第三大項、莫蘭迪玫瑰調 |
| **第四色** | 鼠尾草綠 | `#8FBA88` | 類別第四大項、清新草木調 |
| **長尾收斂** | 典雅灰 | `#CBD5E1` | 4+1 聚合之其他項目總和 |
| **中立基準** | 冷灰白 | `#F5F6F7` | 發散色階中心（偏差 0%） |
| **發散極值** | 墨青／深栗橘 | `#0E5B6B` / `#884725` | 預算大幅縮減 (-100%) / 大幅擴張 (+100%) |

---

## 📊 資料來源與授權聲明
- **上游平臺**：[OpenFun 預算查詢平臺](https://budget.openfun.app/national-comparison)
- **原始資料集**：`openfun-history.csv`（歷年 92 ~ 116 年中央與 22 縣市歲入歲出資料）
- **官方依據**：行政院主計總處各年度政府總預算案與法定預算書。
