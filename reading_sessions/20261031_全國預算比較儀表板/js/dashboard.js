/**
 * 全國預算比較儀表板核心邏輯
 * 依據個人配色規範（四色系統、循序色階、發散色階）進行視覺化與資料處理
 */

(function () {
  'use strict';

  // 配色規範常量
  const PALETTE = {
    // 類別四色 (Categorical)
    categories: [
      '#ECA072', // 1. 主色 (暖杏蜜橘)
      '#5DBACD', // 2. 次色 (霧靄青藍)
      '#E89BB6', // 3. 第三色 (落櫻粉黛)
      '#8FBA88', // 4. 第四色 (鼠尾草綠)
    ],
    other: '#CBD5E1', // 其他/長尾聚合 (雅灰)

    // 循序色階 (主色暖橘系)
    seqOrange: ['#FFF3EA', '#FBD8C0', '#ECA072', '#CA6F35', '#97481B'],
    // 循序色階 (次色霧藍系)
    seqBlue: ['#EBF7F9', '#BCE2EB', '#5DBACD', '#2C8B9F', '#0E5B6B'],
    // 循序色階 (落櫻粉系)
    seqPink: ['#FFF0F5', '#F9CEE0', '#E89BB6', '#C46487', '#8D3658'],
    // 循序色階 (鼠尾綠系)
    seqGreen: ['#F1F7EE', '#D0E5CC', '#8FBA88', '#5E8F56', '#396032'],

    // 發散色階 (9 階)
    diverging: [
      { pos: -1.0, color: '#0E5B6B', label: '深墨青 (-100%)' },
      { pos: -0.75, color: '#257F92', label: '中深青 (-75%)' },
      { pos: -0.5, color: '#5DBACD', label: '青藍 (-50%)' },
      { pos: -0.25, color: '#B2DFE9', label: '淡青 (-25%)' },
      { pos: 0.0, color: '#F5F6F7', label: '中立灰 (0%)' },
      { pos: 0.25, color: '#FBD9C2', label: '淡杏 (+25%)' },
      { pos: 0.5, color: '#ECA072', label: '暖杏 (+50%)' },
      { pos: 0.75, color: '#B4693A', label: '中深橘 (+75%)' },
      { pos: 1.0, color: '#884725', label: '深栗橘 (+100%)' }
    ]
  };

  // 全域狀態
  const state = {
    year: '115',
    io: 'exp', // 'exp' (歲出) | 'rev' (歲入)
    metric: 'total', // 'total' (億元) | 'perCapita' (元/人) | 'ratio' (%) | 'diff' (年增減)
    group: 'all', // 'all' | 'six' | 'nonSix' | 'islands' | 'withCentral'
    colorMode: 'top4', // 'top4' (智慧 4+1) | 'all' (全細項)
    activeTab: 'stacked', // 'stacked' | 'ranking' | 'diverging' | 'deepdive'
    deepdiveCategory: '',
    sortOrder: 'desc', // 'desc' | 'asc' | 'default'
    chartInstance: null,
    searchKeyword: ''
  };

  let rawData = null;

  // 初始化
  async function init() {
    initChart();
    await loadData();
    bindEvents();
    renderAll();
  }

  // 資料載入
  async function loadData() {
    if (window.BUDGET_DATA) {
      rawData = window.BUDGET_DATA;
    } else {
      try {
        const res = await fetch('data/budget_data.json');
        rawData = await res.json();
      } catch (err) {
        console.error('無法載入 budget_data.json:', err);
        return;
      }
    }

    // 填充年份下拉選單
    const yearSelect = document.getElementById('select-year');
    if (yearSelect && rawData.years) {
      yearSelect.innerHTML = '';
      rawData.years.forEach(y => {
        const opt = document.createElement('option');
        opt.value = y;
        opt.textContent = `民國 ${y} 年`;
        if (y === state.year) opt.selected = true;
        yearSelect.appendChild(opt);
      });
    }
  }

  // 初始化 ECharts
  function initChart() {
    const chartDom = document.getElementById('main-chart');
    if (!chartDom) return;
    state.chartInstance = echarts.init(chartDom, null, { renderer: 'canvas' });
    window.addEventListener('resize', () => {
      if (state.chartInstance) state.chartInstance.resize();
    });
  }

  // 取得篩選後縣市名單
  function getFilteredCounties() {
    if (!rawData) return [];
    let list = [];
    const all21 = [
      '臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市',
      '基隆市', '新竹市', '新竹縣', '宜蘭縣', '苗栗縣', '彰化縣',
      '南投縣', '雲林縣', '嘉義市', '嘉義縣', '屏東縣', '花蓮縣',
      '臺東縣', '澎湖縣', '金門縣', '連江縣'
    ];

    if (state.group === 'six') {
      list = rawData.county_groups['六都'] || [];
    } else if (state.group === 'nonSix') {
      list = all21.filter(c => !rawData.county_groups['六都'].includes(c));
    } else if (state.group === 'islands') {
      list = rawData.county_groups['離島'] || [];
    } else if (state.group === 'withCentral') {
      list = ['中央', ...all21];
    } else {
      list = all21;
    }
    return list;
  }

  // 取得發散顏色 (依據變化率或正負數值)
  function getDivergingColor(value, maxAbs) {
    if (maxAbs === 0 || value === 0) return PALETTE.diverging[4].color;
    const ratio = Math.max(-1, Math.min(1, value / maxAbs));
    // 映射至 9 個節點
    if (ratio < -0.75) return PALETTE.diverging[0].color;
    if (ratio < -0.5) return PALETTE.diverging[1].color;
    if (ratio < -0.25) return PALETTE.diverging[2].color;
    if (ratio < -0.05) return PALETTE.diverging[3].color;
    if (ratio <= 0.05) return PALETTE.diverging[4].color;
    if (ratio <= 0.25) return PALETTE.diverging[5].color;
    if (ratio <= 0.5) return PALETTE.diverging[6].color;
    if (ratio <= 0.75) return PALETTE.diverging[7].color;
    return PALETTE.diverging[8].color;
  }

  // 取得循序階梯顏色 (0~1)
  function getSequentialColor(ratio, paletteSeq = PALETTE.seqOrange) {
    const p = Math.max(0, Math.min(1, ratio));
    if (p <= 0.2) return paletteSeq[0];
    if (p <= 0.4) return paletteSeq[1];
    if (p <= 0.6) return paletteSeq[2];
    if (p <= 0.8) return paletteSeq[3];
    return paletteSeq[4];
  }

  // 計算並整理當前檢視所需的資料集
  function prepareCurrentData() {
    if (!rawData) return null;
    const key = `${state.year}_${state.io}`;
    const yearRecords = rawData.records[key] || {};
    const counties = getFilteredCounties();

    // 統計各政事別在所選縣市的加總金額，找出 Top 4
    const categoryTotals = {};
    counties.forEach(county => {
      const cRec = yearRecords[county] || {};
      Object.keys(cRec).forEach(cat => {
        categoryTotals[cat] = (categoryTotals[cat] || 0) + (cRec[cat].budget || 0);
      });
    });

    const sortedCats = Object.keys(categoryTotals).sort((a, b) => categoryTotals[b] - categoryTotals[a]);
    const top4Cats = sortedCats.slice(0, 4);
    const otherCats = sortedCats.slice(4);

    // 建立每個縣市的詳細彙整
    const countyDataList = counties.map(county => {
      const cRec = yearRecords[county] || {};
      const pop = rawData.population[county] || 1;
      let totalBudget = 0;
      let totalDiff = 0;
      const catMap = {};

      Object.keys(cRec).forEach(cat => {
        const b = cRec[cat].budget || 0;
        const d = cRec[cat].diff || 0;
        totalBudget += b;
        totalDiff += d;
        catMap[cat] = b;
      });

      // 4+1 聚合計算
      const top4Map = {};
      let top4Sum = 0;
      top4Cats.forEach(cat => {
        const b = catMap[cat] || 0;
        top4Map[cat] = b;
        top4Sum += b;
      });
      const otherSum = totalBudget - top4Sum;

      return {
        county,
        population: pop,
        totalBudget,
        totalDiff,
        diffRate: (totalBudget - totalDiff) > 0 ? (totalDiff / (totalBudget - totalDiff)) * 100 : 0,
        perCapita: totalBudget / pop,
        catMap,
        top4Map,
        otherSum
      };
    });

    // 排序
    if (state.sortOrder === 'desc') {
      countyDataList.sort((a, b) => {
        if (state.metric === 'perCapita') return b.perCapita - a.perCapita;
        if (state.metric === 'diff') return b.totalDiff - a.totalDiff;
        return b.totalBudget - a.totalBudget;
      });
    } else if (state.sortOrder === 'asc') {
      countyDataList.sort((a, b) => {
        if (state.metric === 'perCapita') return a.perCapita - b.perCapita;
        if (state.metric === 'diff') return a.totalDiff - b.totalDiff;
        return a.totalBudget - b.totalBudget;
      });
    }

    return {
      counties: countyDataList.map(d => d.county),
      countyDataList,
      sortedCats,
      top4Cats,
      otherCats
    };
  }

  // 渲染 KPI 指標卡
  function renderKPICards(data) {
    if (!data) return;
    const { countyDataList, sortedCats } = data;

    // 總預算
    const grandTotal = countyDataList.reduce((acc, cur) => acc + cur.totalBudget, 0);
    const grandDiff = countyDataList.reduce((acc, cur) => acc + cur.totalDiff, 0);
    const baseTotal = grandTotal - grandDiff;
    const grandDiffRate = baseTotal > 0 ? (grandDiff / baseTotal) * 100 : 0;

    // 人均中位數 (排除中央)
    const localCounties = countyDataList.filter(c => c.county !== '中央');
    const perCapitas = localCounties.map(c => c.perCapita).sort((a, b) => a - b);
    const medianPerCapita = perCapitas.length > 0
      ? perCapitas[Math.floor(perCapitas.length / 2)]
      : 0;

    // 前第一大項目與佔比
    const topCatName = sortedCats[0] || '無';
    const topCatTotal = countyDataList.reduce((acc, cur) => acc + (cur.catMap[topCatName] || 0), 0);
    const topCatRatio = grandTotal > 0 ? (topCatTotal / grandTotal) * 100 : 0;

    // 人均最高縣市
    const topPerCapitaCounty = [...localCounties].sort((a, b) => b.perCapita - a.perCapita)[0];

    // 更新 DOM
    document.getElementById('kpi-total-amount').textContent = `${(grandTotal / 1e8).toLocaleString('zh-TW', { maximumFractionDigits: 1 })} 億元`;
    
    const diffEl = document.getElementById('kpi-total-diff');
    if (diffEl) {
      const sign = grandDiff >= 0 ? '+' : '';
      diffEl.textContent = `年增減：${sign}${(grandDiff / 1e8).toFixed(1)} 億 (${sign}${grandDiffRate.toFixed(1)}%)`;
      diffEl.className = grandDiff >= 0 ? 'text-xs text-amber-700 font-medium' : 'text-xs text-cyan-700 font-medium';
    }

    document.getElementById('kpi-median-percapita').textContent = `${Math.round(medianPerCapita).toLocaleString()} 元/人`;
    if (topPerCapitaCounty) {
      document.getElementById('kpi-top-percapita').textContent = `最高：${topPerCapitaCounty.county} (${Math.round(topPerCapitaCounty.perCapita).toLocaleString()} 元)`;
    }

    document.getElementById('kpi-top-category').textContent = topCatName;
    document.getElementById('kpi-top-category-ratio').textContent = `${(topCatTotal / 1e8).toFixed(0)} 億元 (佔 ${topCatRatio.toFixed(1)}%)`;
  }

  // 渲染 Tab 1: 結構堆疊圖 (4+1 簡潔聚焦)
  function renderStackedChart(data) {
    const { counties, countyDataList, top4Cats, sortedCats } = data;
    const isTop4Mode = state.colorMode === 'top4';
    const activeCats = isTop4Mode ? top4Cats : sortedCats;

    const series = [];

    activeCats.forEach((cat, idx) => {
      const color = isTop4Mode ? PALETTE.categories[idx] : PALETTE.seqOrange[idx % 5];
      series.push({
        name: cat,
        type: 'bar',
        stack: 'total',
        emphasis: { focus: 'series' },
        itemStyle: {
          color: color,
          borderRadius: 2
        },
        data: countyDataList.map(item => {
          const val = item.catMap[cat] || 0;
          if (state.metric === 'perCapita') {
            return Math.round(val / item.population);
          } else if (state.metric === 'ratio') {
            return item.totalBudget > 0 ? Number(((val / item.totalBudget) * 100).toFixed(2)) : 0;
          }
          return Number((val / 1e8).toFixed(2));
        })
      });
    });

    // 4+1 模式加入「其他項目」
    if (isTop4Mode) {
      series.push({
        name: '其他項目合計',
        type: 'bar',
        stack: 'total',
        emphasis: { focus: 'series' },
        itemStyle: {
          color: PALETTE.other,
          borderRadius: [0, 4, 4, 0]
        },
        data: countyDataList.map(item => {
          const val = item.otherSum;
          if (state.metric === 'perCapita') {
            return Math.round(val / item.population);
          } else if (state.metric === 'ratio') {
            return item.totalBudget > 0 ? Number(((val / item.totalBudget) * 100).toFixed(2)) : 0;
          }
          return Number((val / 1e8).toFixed(2));
        })
      });
    }

    const unitText = state.metric === 'perCapita' ? '元/人' : (state.metric === 'ratio' ? '%' : '億元');

    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#E2E8F0',
        textStyle: { color: '#1E293B' },
        formatter: function (params) {
          if (!params || params.length === 0) return '';
          let tip = `<div class="font-bold text-sm mb-1 pb-1 border-b border-slate-200">${params[0].axisValue}</div>`;
          let sum = 0;
          params.forEach(p => {
            sum += Number(p.value);
            tip += `
              <div class="flex items-center justify-between text-xs py-0.5 gap-4">
                <span class="flex items-center gap-1.5">
                  <span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${p.color};"></span>
                  <span>${p.seriesName}</span>
                </span>
                <span class="font-mono font-bold">${p.value.toLocaleString()} ${unitText}</span>
              </div>
            `;
          });
          if (state.metric !== 'ratio') {
            tip += `<div class="mt-1 pt-1 border-t border-slate-200 flex justify-between text-xs font-bold text-slate-800"><span>合計</span><span class="font-mono">${sum.toLocaleString()} ${unitText}</span></div>`;
          }
          return tip;
        }
      },
      legend: {
        bottom: 0,
        type: 'scroll',
        textStyle: { color: '#64748B', fontSize: 12 }
      },
      grid: {
        left: '2%',
        right: '4%',
        bottom: '12%',
        top: '4%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: unitText,
        splitLine: { lineStyle: { color: '#F1F5F9' } },
        axisLabel: { color: '#64748B', fontSize: 11 }
      },
      yAxis: {
        type: 'category',
        data: counties,
        inverse: true, // 最高在上方
        axisLine: { lineStyle: { color: '#CBD5E1' } },
        axisLabel: { color: '#334155', fontWeight: 500, fontSize: 12 }
      },
      series: series
    };

    state.chartInstance.setOption(option, true);
  }

  // 渲染 Tab 2: 縣市排行榜 (循序色階漸進)
  function renderRankingChart(data) {
    const { counties, countyDataList } = data;
    const isPerCapita = state.metric === 'perCapita';
    const values = countyDataList.map(item => isPerCapita ? item.perCapita : item.totalBudget / 1e8);
    const maxVal = Math.max(...values, 1);
    const unitText = isPerCapita ? '元/人' : '億元';

    const seriesData = countyDataList.map(item => {
      const val = isPerCapita ? item.perCapita : item.totalBudget / 1e8;
      const ratio = val / maxVal;
      return {
        value: Number(val.toFixed(2)),
        itemStyle: {
          color: getSequentialColor(ratio, PALETTE.seqOrange),
          borderRadius: [0, 4, 4, 0]
        }
      };
    });

    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: function (params) {
          const p = params[0];
          return `
            <div class="font-bold text-sm">${p.axisValue}</div>
            <div class="text-xs text-slate-600 mt-1">
              ${isPerCapita ? '人均預算' : '總預算'}：<span class="font-mono font-bold text-slate-900">${p.value.toLocaleString()} ${unitText}</span>
            </div>
          `;
        }
      },
      grid: {
        left: '2%',
        right: '6%',
        bottom: '4%',
        top: '4%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: unitText,
        splitLine: { lineStyle: { color: '#F1F5F9' } }
      },
      yAxis: {
        type: 'category',
        data: counties,
        inverse: true,
        axisLine: { lineStyle: { color: '#CBD5E1' } },
        axisLabel: { color: '#334155', fontWeight: 500, fontSize: 12 }
      },
      series: [
        {
          name: isPerCapita ? '人均預算' : '預算總額',
          type: 'bar',
          data: seriesData,
          label: {
            show: true,
            position: 'right',
            formatter: '{c} ' + unitText,
            color: '#64748B',
            fontSize: 11
          }
        }
      ]
    };

    state.chartInstance.setOption(option, true);
  }

  // 渲染 Tab 3: 發散色階 (年增減差異分析)
  function renderDivergingChart(data) {
    const { counties, countyDataList } = data;
    const diffs = countyDataList.map(item => item.totalDiff / 1e8);
    const maxAbs = Math.max(...diffs.map(Math.abs), 1);

    const seriesData = countyDataList.map(item => {
      const val = Number((item.totalDiff / 1e8).toFixed(2));
      const color = getDivergingColor(val, maxAbs);
      return {
        value: val,
        rate: item.diffRate.toFixed(1),
        itemStyle: {
          color: color,
          borderRadius: val >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4]
        }
      };
    });

    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: function (params) {
          const p = params[0];
          const val = p.value;
          const sign = val >= 0 ? '+' : '';
          const raw = p.data;
          return `
            <div class="font-bold text-sm">${p.axisValue}</div>
            <div class="text-xs text-slate-600 mt-1">
              年預算變動：<span class="font-mono font-bold ${val >= 0 ? 'text-amber-700' : 'text-cyan-700'}">${sign}${val.toLocaleString()} 億元</span>
            </div>
            <div class="text-xs text-slate-500">
              增減幅度：<span class="font-mono font-semibold">${sign}${raw.rate}%</span>
            </div>
          `;
        }
      },
      grid: {
        left: '2%',
        right: '6%',
        bottom: '8%',
        top: '6%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: '億元',
        splitLine: { lineStyle: { color: '#E2E8F0', type: 'dashed' } },
        axisLine: { lineStyle: { color: '#94A3B8' } }
      },
      yAxis: {
        type: 'category',
        data: counties,
        inverse: true,
        axisLine: { lineStyle: { color: '#CBD5E1' } },
        axisLabel: { color: '#334155', fontWeight: 500, fontSize: 12 }
      },
      series: [
        {
          name: '與去年差異',
          type: 'bar',
          data: seriesData,
          label: {
            show: true,
            position: function (point, params) {
              return params.value >= 0 ? 'right' : 'left';
            },
            formatter: function (params) {
              const sign = params.value >= 0 ? '+' : '';
              return `${sign}${params.value} 億`;
            },
            fontSize: 10,
            color: '#64748B'
          }
        }
      ]
    };

    state.chartInstance.setOption(option, true);
  }

  // 渲染 Tab 4: 單一項目深鑽 (Deep-dive)
  function renderDeepdiveChart(data) {
    const { counties, countyDataList, sortedCats } = data;
    if (!state.deepdiveCategory || !sortedCats.includes(state.deepdiveCategory)) {
      state.deepdiveCategory = sortedCats[0];
    }

    // 更新下拉選單
    const selectEl = document.getElementById('select-deepdive-cat');
    if (selectEl) {
      selectEl.innerHTML = '';
      sortedCats.forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat;
        opt.textContent = cat;
        if (cat === state.deepdiveCategory) opt.selected = true;
        selectEl.appendChild(opt);
      });
    }

    const catName = state.deepdiveCategory;
    const catValues = countyDataList.map(item => (item.catMap[catName] || 0) / 1e8);
    const maxVal = Math.max(...catValues, 0.01);

    const seriesData = countyDataList.map(item => {
      const val = Number(((item.catMap[catName] || 0) / 1e8).toFixed(2));
      const ratio = item.totalBudget > 0 ? ((item.catMap[catName] || 0) / item.totalBudget * 100).toFixed(1) : 0;
      return {
        value: val,
        ratio: ratio,
        itemStyle: {
          color: getSequentialColor(val / maxVal, PALETTE.seqBlue),
          borderRadius: [0, 4, 4, 0]
        }
      };
    });

    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: function (params) {
          const p = params[0];
          const raw = p.data;
          return `
            <div class="font-bold text-sm">${p.axisValue}</div>
            <div class="text-xs text-slate-700 mt-1">
              ${catName}：<span class="font-mono font-bold text-slate-900">${p.value.toLocaleString()} 億元</span>
            </div>
            <div class="text-xs text-slate-500">
              佔自身預算比重：<span class="font-mono font-semibold">${raw.ratio}%</span>
            </div>
          `;
        }
      },
      grid: {
        left: '2%',
        right: '6%',
        bottom: '4%',
        top: '4%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: '億元',
        splitLine: { lineStyle: { color: '#F1F5F9' } }
      },
      yAxis: {
        type: 'category',
        data: counties,
        inverse: true,
        axisLine: { lineStyle: { color: '#CBD5E1' } },
        axisLabel: { color: '#334155', fontWeight: 500, fontSize: 12 }
      },
      series: [
        {
          name: catName,
          type: 'bar',
          data: seriesData,
          label: {
            show: true,
            position: 'right',
            formatter: '{c} 億',
            color: '#64748B',
            fontSize: 11
          }
        }
      ]
    };

    state.chartInstance.setOption(option, true);
  }

  // 渲染底部資料表格
  function renderTable(data) {
    const tbody = document.getElementById('table-body');
    if (!tbody || !data) return;
    const { countyDataList, top4Cats } = data;

    // 關鍵字搜尋過濾
    const kw = state.searchKeyword.trim().toLowerCase();
    const filteredList = kw
      ? countyDataList.filter(item => item.county.toLowerCase().includes(kw))
      : countyDataList;

    tbody.innerHTML = '';
    filteredList.forEach(item => {
      const tr = document.createElement('tr');
      tr.className = 'border-b border-slate-100 hover:bg-slate-50/80 transition-colors text-xs';

      const sign = item.totalDiff >= 0 ? '+' : '';
      const diffColorClass = item.totalDiff >= 0 ? 'text-amber-700' : 'text-cyan-700';

      tr.innerHTML = `
        <td class="py-3 px-4 font-bold text-slate-800">${item.county}</td>
        <td class="py-3 px-4 font-mono text-slate-600 text-right">${item.population.toLocaleString()}</td>
        <td class="py-3 px-4 font-mono font-bold text-slate-900 text-right">${(item.totalBudget / 1e8).toLocaleString('zh-TW', { maximumFractionDigits: 1 })} 億</td>
        <td class="py-3 px-4 font-mono text-slate-700 text-right">${Math.round(item.perCapita).toLocaleString()} 元</td>
        <td class="py-3 px-4 font-mono font-semibold text-right ${diffColorClass}">${sign}${(item.totalDiff / 1e8).toFixed(1)} 億 (${sign}${item.diffRate.toFixed(1)}%)</td>
        <td class="py-3 px-4 text-slate-600">
          <div class="flex items-center gap-1.5 flex-wrap">
            ${top4Cats.map((cat, idx) => {
              const amt = item.catMap[cat] || 0;
              const ratio = item.totalBudget > 0 ? (amt / item.totalBudget * 100).toFixed(0) : 0;
              return `<span class="px-1.5 py-0.5 rounded text-[10px] font-medium" style="background:${PALETTE.categories[idx]}20;color:#1E293B;">${cat} ${ratio}%</span>`;
            }).join('')}
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  // 匯出 CSV 功能
  function exportCSV(data) {
    if (!data) return;
    const { countyDataList, sortedCats } = data;
    const headers = ['縣市', '人口', '總預算(元)', '人均預算(元/人)', '與去年差異(元)', '年增減率(%)', ...sortedCats];
    
    const rows = countyDataList.map(item => {
      const diffRate = item.diffRate.toFixed(2);
      const catAmts = sortedCats.map(cat => item.catMap[cat] || 0);
      return [item.county, item.population, item.totalBudget, Math.round(item.perCapita), item.totalDiff, diffRate, ...catAmts];
    });

    let csvContent = '\uFEFF' + headers.join(',') + '\n';
    rows.forEach(r => {
      csvContent += r.join(',') + '\n';
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `台灣縣市預算比較_${state.year}年_${state.io === 'exp' ? '歲出' : '歲入'}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  // 總渲染排程
  function renderAll() {
    const data = prepareCurrentData();
    if (!data) return;

    renderKPICards(data);

    // 依據 Tab 渲染
    if (state.activeTab === 'stacked') {
      renderStackedChart(data);
    } else if (state.activeTab === 'ranking') {
      renderRankingChart(data);
    } else if (state.activeTab === 'diverging') {
      renderDivergingChart(data);
    } else if (state.activeTab === 'deepdive') {
      renderDeepdiveChart(data);
    }

    renderTable(data);
  }

  // 事件監聽與綁定
  function bindEvents() {
    // 年份選擇
    const yearSelect = document.getElementById('select-year');
    if (yearSelect) {
      yearSelect.addEventListener('change', e => {
        state.year = e.target.value;
        renderAll();
      });
    }

    // 收支切換 (歲出 / 歲入)
    document.querySelectorAll('.btn-io').forEach(btn => {
      btn.addEventListener('click', e => {
        document.querySelectorAll('.btn-io').forEach(b => b.classList.remove('filter-btn-active'));
        btn.classList.add('filter-btn-active');
        state.io = btn.dataset.io;
        renderAll();
      });
    });

    // 指標維度切換 (總額 / 人均 / 比例 / 年增減)
    document.querySelectorAll('.btn-metric').forEach(btn => {
      btn.addEventListener('click', e => {
        document.querySelectorAll('.btn-metric').forEach(b => b.classList.remove('filter-btn-active'));
        btn.classList.add('filter-btn-active');
        state.metric = btn.dataset.metric;
        if (state.metric === 'diff') {
          // 自動切換到發散 Tab
          switchTab('diverging');
        } else {
          renderAll();
        }
      });
    });

    // 縣市分組切換 (全部 / 六都 / 非六都 / 離島 / 含中央)
    document.querySelectorAll('.btn-group').forEach(btn => {
      btn.addEventListener('click', e => {
        document.querySelectorAll('.btn-group').forEach(b => b.classList.remove('filter-btn-active'));
        btn.classList.add('filter-btn-active');
        state.group = btn.dataset.group;
        renderAll();
      });
    });

    // 色彩模式切換 (4+1 聚焦 vs 全部展開)
    const colorModeToggle = document.getElementById('toggle-colormode');
    if (colorModeToggle) {
      colorModeToggle.addEventListener('change', e => {
        state.colorMode = e.target.checked ? 'top4' : 'all';
        renderAll();
      });
    }

    // 排序切換
    const sortSelect = document.getElementById('select-sort');
    if (sortSelect) {
      sortSelect.addEventListener('change', e => {
        state.sortOrder = e.target.value;
        renderAll();
      });
    }

    // Tab 切換
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        switchTab(btn.dataset.tab);
      });
    });

    // 深鑽政事別選擇
    const deepdiveSelect = document.getElementById('select-deepdive-cat');
    if (deepdiveSelect) {
      deepdiveSelect.addEventListener('change', e => {
        state.deepdiveCategory = e.target.value;
        const data = prepareCurrentData();
        renderDeepdiveChart(data);
      });
    }

    // 搜尋框
    const searchInput = document.getElementById('input-search');
    if (searchInput) {
      searchInput.addEventListener('input', e => {
        state.searchKeyword = e.target.value;
        const data = prepareCurrentData();
        renderTable(data);
      });
    }

    // 匯出 CSV 按鈕
    const exportBtn = document.getElementById('btn-export-csv');
    if (exportBtn) {
      exportBtn.addEventListener('click', () => {
        const data = prepareCurrentData();
        exportCSV(data);
      });
    }
  }

  // 切換 Tab
  function switchTab(tabId) {
    state.activeTab = tabId;
    document.querySelectorAll('.tab-btn').forEach(b => {
      if (b.dataset.tab === tabId) {
        b.classList.add('tab-btn-active');
      } else {
        b.classList.remove('tab-btn-active');
      }
    });

    // 深鑽控制項顯示/隱藏
    const deepdiveBar = document.getElementById('deepdive-control-bar');
    if (deepdiveBar) {
      deepdiveBar.style.display = tabId === 'deepdive' ? 'flex' : 'none';
    }

    renderAll();
  }

  // 啟動
  document.addEventListener('DOMContentLoaded', init);
})();
