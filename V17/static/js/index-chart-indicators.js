/**
 * Index Chart Indicators Manager
 * Quản lý indicators và signals hiển thị trên chart của index (độc lập với strategy)
 */

// Global state cho index chart indicators
let indexChartIndicators = [];
let indexChartIndicatorSeries = {}; // Lưu trữ series của indicators trên chart
let currentIndexCategory = 'all';

// LocalStorage key
const INDEX_CHART_INDICATORS_STORAGE_KEY = 'index_chart_indicators';

// Danh sách indicators có sẵn (giống strategy)
const indexAvailableIndicators = {
    trend: [
        { type: 'EMA', name: 'EMA', params: { length: 20 } },
        { type: 'SMA', name: 'SMA', params: { length: 50 } },
        { type: 'WMA', name: 'WMA', params: { length: 20 } },
        { type: 'DEMA', name: 'DEMA', params: { length: 20 } },
        { type: 'TEMA', name: 'TEMA', params: { length: 20 } }
    ],
    momentum: [
        { type: 'RSI', name: 'RSI', params: { length: 14, overbought: 70, oversold: 30 } },
        { type: 'MACD', name: 'MACD', params: { fast: 12, slow: 26, signal: 9 } },
        { type: 'Stochastic', name: 'Stochastic', params: { k_period: 14, d_period: 3, overbought: 80, oversold: 20 } },
        { type: 'CCI', name: 'CCI', params: { length: 20 } },
        { type: 'MFI', name: 'MFI', params: { length: 14 } }
    ],
    volatility: [
        { type: 'BollingerBands', name: 'Bollinger Bands', params: { length: 20, std: 2 } },
        { type: 'ATR', name: 'ATR', params: { length: 14 } },
        { type: 'KeltnerChannel', name: 'Keltner Channel', params: { length: 20, multiplier: 2 } },
        { type: 'DonchianChannel', name: 'Donchian Channel', params: { length: 20 } }
    ],
    volume: [
        { type: 'OBV', name: 'OBV', params: {} },
        { type: 'VWAP', name: 'VWAP', params: {} }
    ],
    custom: [
        { type: 'SuperTrend', name: 'SuperTrend', params: { atr_period: 10, multiplier: 3 } },
        { type: 'PivotPoints', name: 'Pivot Points', params: { type: 'standard' } },
        { type: 'HHV', name: 'Highest High', params: { length: 20 } },
        { type: 'LLV', name: 'Lowest Low', params: { length: 20 } }
    ]
};

/**
 * Save index chart indicators to localStorage
 */
function saveIndexChartIndicatorsToStorage() {
    try {
        const indicatorsData = indexChartIndicators.map(ind => ({
            id: ind.id,
            type: ind.type,
            name: ind.name,
            params: ind.params,
            color: ind.color,
            lineWidth: ind.lineWidth,
            visible: ind.visible
        }));
        localStorage.setItem(INDEX_CHART_INDICATORS_STORAGE_KEY, JSON.stringify(indicatorsData));
        console.log('💾 Saved', indicatorsData.length, 'index indicators to localStorage');
    } catch (e) {
        console.error('❌ Error saving index indicators to localStorage:', e);
    }
}

/**
 * Load index chart indicators from localStorage
 */
function loadIndexChartIndicatorsFromStorage() {
    try {
        const stored = localStorage.getItem(INDEX_CHART_INDICATORS_STORAGE_KEY);
        if (stored) {
            const indicatorsData = JSON.parse(stored);
            console.log('📂 Loading', indicatorsData.length, 'index indicators from localStorage');

            // Clear existing indicators
            indexChartIndicators = [];
            Object.keys(indexChartIndicatorSeries).forEach(id => {
                if (chart && indexChartIndicatorSeries[id]) {
                    try {
                        // Check if it's an array of series (multiple) or single series
                        if (Array.isArray(indexChartIndicatorSeries[id])) {
                            indexChartIndicatorSeries[id].forEach(series => {
                                chart.removeSeries(series);
                            });
                        } else {
                            chart.removeSeries(indexChartIndicatorSeries[id]);
                        }
                    } catch (e) {
                        console.error('Error removing series:', e);
                    }
                }
            });
            indexChartIndicatorSeries = {};

            // Restore indicators
            indicatorsData.forEach(ind => {
                indexChartIndicators.push(ind);
                // Draw indicator on chart if chart is ready
                if (typeof chart !== 'undefined' && chart && typeof candleData !== 'undefined' && candleData && candleData.length > 0) {
                    drawIndexIndicatorOnChart(ind);
                }
            });

            console.log('✅ Loaded', indexChartIndicators.length, 'index indicators');
        }
    } catch (e) {
        console.error('❌ Error loading index indicators from localStorage:', e);
    }
}

/**
 * Mở modal Index Indicators
 */
function openIndexIndicatorsModal() {
    const modal = document.getElementById('indexIndicatorsModal');
    modal.classList.remove('hidden');

    // Populate available indicators
    populateIndexAvailableIndicators();

    // Update active indicators list
    updateIndexActiveIndicatorsList();
}

/**
 * Đóng modal Index Indicators
 */
function closeIndexIndicatorsModal() {
    const modal = document.getElementById('indexIndicatorsModal');
    modal.classList.add('hidden');
}

/**
 * Populate danh sách indicators có sẵn
 */
function populateIndexAvailableIndicators() {
    const container = document.getElementById('indexAvailableIndicatorsList');
    container.innerHTML = '';

    // Get indicators based on current category
    let indicatorsToShow = [];
    if (currentIndexCategory === 'all') {
        Object.values(indexAvailableIndicators).forEach(category => {
            indicatorsToShow = indicatorsToShow.concat(category);
        });
    } else {
        indicatorsToShow = indexAvailableIndicators[currentIndexCategory] || [];
    }

    // Create indicator cards
    indicatorsToShow.forEach((indicator, index) => {
        const card = document.createElement('div');
        card.className = 'indicator-card';
        card.style.cssText = `
            background: #1e222d;
            border: 1px solid #2a2e39;
            border-radius: 6px;
            padding: 12px;
            cursor: pointer;
            transition: all 0.2s;
        `;

        card.innerHTML = `
            <div style="font-weight: 600; color: #2962ff; font-size: 13px; margin-bottom: 5px;">
                ${indicator.name}
            </div>
            <div style="font-size: 11px; color: #787b86;">
                ${Object.entries(indicator.params).map(([k, v]) => `${k}: ${v}`).join(', ') || 'No parameters'}
            </div>
        `;

        // Add click handler
        card.addEventListener('click', () => addIndexIndicator(indicator));

        // Hover effects
        card.addEventListener('mouseenter', function() {
            this.style.background = '#252933';
            this.style.borderColor = '#2962ff';
        });
        card.addEventListener('mouseleave', function() {
            this.style.background = '#1e222d';
            this.style.borderColor = '#2a2e39';
        });

        container.appendChild(card);
    });

    if (indicatorsToShow.length === 0) {
        container.innerHTML = '<div style="text-align: center; color: #787b86; padding: 20px;">No indicators in this category</div>';
    }
}

/**
 * Filter indicators by category
 */
function filterIndexIndicators(category) {
    currentIndexCategory = category;

    // Update active category button
    document.querySelectorAll('#indexIndicatorsModal .category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Re-populate indicators
    populateIndexAvailableIndicators();
}

/**
 * Thêm indicator vào index chart (mở config modal trước)
 */
function addIndexIndicator(indicator) {
    // Open config modal instead of adding directly
    openIndexIndicatorConfigModal(indicator);
}

/**
 * Xóa indicator khỏi index chart
 */
function removeIndexIndicator(id) {
    // Remove from array
    indexChartIndicators = indexChartIndicators.filter(ind => ind.id !== id);

    // Remove series from chart
    if (indexChartIndicatorSeries[id]) {
        try {
            // Check if it's an array of series (multiple) or single series
            if (Array.isArray(indexChartIndicatorSeries[id])) {
                indexChartIndicatorSeries[id].forEach(series => {
                    chart.removeSeries(series);
                });
            } else {
                chart.removeSeries(indexChartIndicatorSeries[id]);
            }
            delete indexChartIndicatorSeries[id];
        } catch (e) {
            console.error('Error removing indicator series:', e);
        }
    }

    // Update active indicators list
    updateIndexActiveIndicatorsList();

    // Save to localStorage
    saveIndexChartIndicatorsToStorage();

    showIndexNotification('Indicator removed from chart', 'info');
}

/**
 * Update danh sách active indicators
 */
function updateIndexActiveIndicatorsList() {
    const container = document.getElementById('indexActiveIndicatorsList');

    if (indexChartIndicators.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; color: #787b86; padding: 20px;">
                No indicators added yet. Add indicators from the list below.
            </div>
        `;
        return;
    }

    container.innerHTML = '';

    indexChartIndicators.forEach(indicator => {
        const item = document.createElement('div');
        item.className = 'indicator-item';
        item.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px;
            background: #1e222d;
            border: 1px solid #2a2e39;
            border-radius: 4px;
            margin-bottom: 8px;
        `;

        item.innerHTML = `
            <div style="flex: 1;">
                <div style="font-weight: 600; color: ${indicator.color}; font-size: 13px;">
                    ${indicator.name}
                </div>
                <div style="font-size: 11px; color: #787b86; margin-top: 3px;">
                    ${Object.entries(indicator.params).map(([k, v]) => `${k}: ${v}`).join(', ')}
                </div>
            </div>
            <div style="display: flex; gap: 6px;">
                <button onclick="editIndexIndicator('${indicator.id}')"
                    style="padding: 6px 10px; background: #2962ff; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 11px;">
                    ✏️ Edit
                </button>
                <button onclick="toggleIndexIndicatorVisibility('${indicator.id}')"
                    style="padding: 6px 10px; background: #2a2e39; color: #d1d4dc; border: none; border-radius: 3px; cursor: pointer; font-size: 11px;">
                    ${indicator.visible ? '👁️ Hide' : '👁️‍🗨️ Show'}
                </button>
                <button onclick="removeIndexIndicator('${indicator.id}')"
                    style="padding: 6px 10px; background: #ef5350; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 11px;">
                    ✕ Remove
                </button>
            </div>
        `;

        container.appendChild(item);
    });
}

/**
 * Toggle indicator visibility
 */
function toggleIndexIndicatorVisibility(id) {
    const indicator = indexChartIndicators.find(ind => ind.id === id);
    if (indicator) {
        indicator.visible = !indicator.visible;

        // Toggle series visibility on chart
        if (indexChartIndicatorSeries[id]) {
            try {
                // Check if it's an array of series (multiple) or single series
                if (Array.isArray(indexChartIndicatorSeries[id])) {
                    indexChartIndicatorSeries[id].forEach(series => {
                        series.applyOptions({ visible: indicator.visible });
                    });
                } else {
                    indexChartIndicatorSeries[id].applyOptions({ visible: indicator.visible });
                }
            } catch (e) {
                console.error('Error toggling indicator visibility:', e);
            }
        }

        updateIndexActiveIndicatorsList();

        // Save to localStorage
        saveIndexChartIndicatorsToStorage();
    }
}

/**
 * Vẽ indicator lên index chart
 */
function drawIndexIndicatorOnChart(indicator) {
    // Check if chart exists
    if (typeof chart === 'undefined' || !chart) {
        console.error('❌ Chart not initialized');
        showIndexNotification('Chart not ready. Please wait...', 'error');
        return;
    }

    // Get candle data from offlineData (defined in data-manager.js)
    const candleData = (typeof offlineData !== 'undefined' && offlineData && offlineData.candlesticks)
        ? offlineData.candlesticks
        : null;

    if (!candleData || candleData.length === 0) {
        console.error('❌ No candle data available');
        showIndexNotification('No data available. Please load data first.', 'error');
        return;
    }

    console.log('✅ Drawing indicator on index chart:', indicator.name, 'with', candleData.length, 'candles');

    // Calculate indicator values
    const indicatorData = calculateIndexIndicatorValues(indicator, candleData);

    if (!indicatorData) {
        console.error('❌ No indicator data calculated');
        showIndexNotification('Failed to calculate indicator values', 'error');
        return;
    }

    try {
        // Check if multiple series (SuperTrend, Bollinger Bands)
        if (indicatorData.type === 'multiple' && indicatorData.series) {
            const seriesArray = [];

            indicatorData.series.forEach((seriesData, index) => {
                if (seriesData.data && seriesData.data.length > 0) {
                    // Only show title for first segment to avoid multiple labels
                    const seriesTitle = index === 0 ? indicator.name : '';

                    const lineSeries = chart.addLineSeries({
                        color: seriesData.color,
                        lineWidth: seriesData.lineWidth || indicator.lineWidth || 2,
                        title: seriesTitle,
                        priceScaleId: 'right',
                        visible: indicator.visible
                    });

                    lineSeries.setData(seriesData.data);
                    seriesArray.push(lineSeries);
                    console.log(`✅ Drew ${indicator.name} segment ${index + 1} with ${seriesData.data.length} points`);
                }
            });

            // Store multiple series as array
            indexChartIndicatorSeries[indicator.id] = seriesArray;
            showIndexNotification(`${indicator.name} added successfully`, 'success');

        } else {
            // Single series (regular indicators)
            if (!indicatorData || indicatorData.length === 0) {
                console.error('❌ No indicator data calculated');
                showIndexNotification('Failed to calculate indicator values', 'error');
                return;
            }

            console.log('✅ Calculated indicator data:', indicatorData.length, 'points');

            const lineSeries = chart.addLineSeries({
                color: indicator.color,
                lineWidth: indicator.lineWidth || 2,
                title: indicator.name,
                priceScaleId: 'right',
                visible: indicator.visible
            });

            lineSeries.setData(indicatorData);

            // Store single series
            indexChartIndicatorSeries[indicator.id] = lineSeries;

            console.log(`✅ Drew ${indicator.name} on index chart with ${indicatorData.length} points`);
            showIndexNotification(`${indicator.name} added successfully`, 'success');
        }
    } catch (e) {
        console.error('❌ Error drawing indicator on chart:', e);
        showIndexNotification('Failed to draw indicator on chart', 'error');
    }
}

/**
 * Calculate indicator values (same as strategy but for index)
 */
function calculateIndexIndicatorValues(indicator, candles) {
    console.log('📊 Calculating indicator:', indicator.type, 'with params:', indicator.params);

    try {
        switch (indicator.type) {
            case 'EMA':
            case 'SMA':
            case 'WMA':
                return calculateIndexMovingAverage(candles, indicator.params.length, indicator.type);

            case 'RSI':
                return calculateIndexRSI(candles, indicator.params.length);

            case 'BollingerBands':
                return calculateIndexBollingerBands(candles, indicator.params.length, indicator.params.std);

            case 'SuperTrend':
                return calculateIndexSuperTrend(candles, indicator.params.atr_period, indicator.params.multiplier);

            case 'ATR':
                return calculateIndexATR(candles, indicator.params.length || 14);

            case 'DEMA':
            case 'TEMA':
                return calculateIndexMovingAverage(candles, indicator.params.length, 'EMA');

            case 'MACD':
            case 'Stochastic':
            case 'CCI':
            case 'MFI':
            case 'KeltnerChannel':
            case 'DonchianChannel':
            case 'OBV':
            case 'VWAP':
            case 'PivotPoints':
            case 'HHV':
            case 'LLV':
                console.warn(`⚠️ Indicator type ${indicator.type} not fully implemented yet, using SMA as placeholder`);
                return calculateIndexMovingAverage(candles, 20, 'SMA');

            default:
                console.warn(`⚠️ Unknown indicator type ${indicator.type}`);
                return [];
        }
    } catch (error) {
        console.error('❌ Error calculating indicator:', error);
        return [];
    }
}

/**
 * Calculate Moving Average (EMA, SMA, WMA)
 */
function calculateIndexMovingAverage(candles, length, type) {
    console.log(`📈 Calculating ${type} with length ${length} on ${candles.length} candles`);
    const result = [];

    if (!candles || candles.length < length) {
        console.error('❌ Not enough candles for calculation');
        return result;
    }

    if (type === 'SMA') {
        for (let i = length - 1; i < candles.length; i++) {
            let sum = 0;
            for (let j = 0; j < length; j++) {
                sum += candles[i - j].close;
            }
            result.push({
                time: candles[i].time,
                value: sum / length
            });
        }
        console.log(`✅ SMA calculated: ${result.length} points`);
    } else if (type === 'EMA') {
        const multiplier = 2 / (length + 1);
        let ema = candles.slice(0, length).reduce((sum, c) => sum + c.close, 0) / length;

        result.push({ time: candles[length - 1].time, value: ema });

        for (let i = length; i < candles.length; i++) {
            ema = (candles[i].close - ema) * multiplier + ema;
            result.push({ time: candles[i].time, value: ema });
        }
        console.log(`✅ EMA calculated: ${result.length} points`);
    } else if (type === 'WMA') {
        const divisor = (length * (length + 1)) / 2;
        for (let i = length - 1; i < candles.length; i++) {
            let sum = 0;
            for (let j = 0; j < length; j++) {
                sum += candles[i - j].close * (length - j);
            }
            result.push({
                time: candles[i].time,
                value: sum / divisor
            });
        }
        console.log(`✅ WMA calculated: ${result.length} points`);
    }

    return result;
}

/**
 * Calculate RSI
 */
function calculateIndexRSI(candles, length) {
    const result = [];
    const gains = [];
    const losses = [];

    for (let i = 1; i < candles.length; i++) {
        const change = candles[i].close - candles[i - 1].close;
        gains.push(change > 0 ? change : 0);
        losses.push(change < 0 ? -change : 0);
    }

    let avgGain = gains.slice(0, length).reduce((sum, g) => sum + g, 0) / length;
    let avgLoss = losses.slice(0, length).reduce((sum, l) => sum + l, 0) / length;

    for (let i = length; i < gains.length; i++) {
        avgGain = (avgGain * (length - 1) + gains[i]) / length;
        avgLoss = (avgLoss * (length - 1) + losses[i]) / length;

        const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
        const rsi = 100 - (100 / (1 + rs));

        result.push({
            time: candles[i + 1].time,
            value: rsi
        });
    }

    return result;
}

/**
 * Calculate ATR (Average True Range)
 */
function calculateIndexATR(candles, length) {
    const result = [];
    const trueRanges = [];

    for (let i = 1; i < candles.length; i++) {
        const high = candles[i].high;
        const low = candles[i].low;
        const prevClose = candles[i - 1].close;

        const tr = Math.max(
            high - low,
            Math.abs(high - prevClose),
            Math.abs(low - prevClose)
        );
        trueRanges.push(tr);
    }

    let atr = trueRanges.slice(0, length).reduce((sum, tr) => sum + tr, 0) / length;

    for (let i = length; i < trueRanges.length; i++) {
        atr = (atr * (length - 1) + trueRanges[i]) / length;
        result.push({
            time: candles[i + 1].time,
            value: atr
        });
    }

    return result;
}

/**
 * Calculate SuperTrend
 * Returns {type: 'multiple', series: [...]} with continuous segments
 */
function calculateIndexSuperTrend(candles, atrPeriod, multiplier) {
    console.log(`📈 Calculating SuperTrend with ATR ${atrPeriod}, multiplier ${multiplier}`);

    const uptrendColor = '#26a69a';
    const downtrendColor = '#ef5350';

    if (!candles || candles.length < atrPeriod + 1) {
        console.error('❌ Not enough candles for SuperTrend calculation');
        return { type: 'multiple', series: [] };
    }

    const atrValues = [];
    const trueRanges = [];

    for (let i = 1; i < candles.length; i++) {
        const high = candles[i].high;
        const low = candles[i].low;
        const prevClose = candles[i - 1].close;
        const tr = Math.max(high - low, Math.abs(high - prevClose), Math.abs(low - prevClose));
        trueRanges.push(tr);
    }

    let atr = trueRanges.slice(0, atrPeriod).reduce((sum, tr) => sum + tr, 0) / atrPeriod;
    for (let i = 0; i < atrPeriod; i++) {
        atrValues.push(atr);
    }

    for (let i = atrPeriod; i < trueRanges.length; i++) {
        atr = (atr * (atrPeriod - 1) + trueRanges[i]) / atrPeriod;
        atrValues.push(atr);
    }

    // Calculate basic upper and lower bands
    const basicUpper = [];
    const basicLower = [];

    for (let i = 0; i < candles.length; i++) {
        const hl2 = (candles[i].high + candles[i].low) / 2;
        const atrValue = i > 0 ? (atrValues[i - 1] || atr) : atr;

        basicUpper.push(hl2 + multiplier * atrValue);
        basicLower.push(hl2 - multiplier * atrValue);
    }

    // Calculate final bands and supertrend
    const finalUpper = new Array(candles.length);
    const finalLower = new Array(candles.length);
    const supertrend = new Array(candles.length);
    const direction = new Array(candles.length);

    // Initialize first value
    finalUpper[0] = basicUpper[0];
    finalLower[0] = basicLower[0];
    supertrend[0] = finalUpper[0];
    direction[0] = 1; // 1 = uptrend, -1 = downtrend

    // Calculate for remaining candles
    for (let i = 1; i < candles.length; i++) {
        const close = candles[i].close;
        const prevClose = candles[i - 1].close;

        // Calculate final upper band
        if (basicUpper[i] < finalUpper[i - 1] || prevClose > finalUpper[i - 1]) {
            finalUpper[i] = basicUpper[i];
        } else {
            finalUpper[i] = finalUpper[i - 1];
        }

        // Calculate final lower band
        if (basicLower[i] > finalLower[i - 1] || prevClose < finalLower[i - 1]) {
            finalLower[i] = basicLower[i];
        } else {
            finalLower[i] = finalLower[i - 1];
        }

        // Determine trend direction
        if (close <= finalUpper[i]) {
            direction[i] = -1; // Downtrend
            supertrend[i] = finalUpper[i];
        } else {
            direction[i] = 1; // Uptrend
            supertrend[i] = finalLower[i];
        }
    }

    // Create continuous segments with color changes
    const segments = [];
    let currentSegment = {
        data: [{ time: candles[0].time, value: supertrend[0] }],
        color: direction[0] === 1 ? uptrendColor : downtrendColor,
        name: direction[0] === 1 ? 'Uptrend' : 'Downtrend'
    };

    for (let i = 1; i < candles.length; i++) {
        const point = { time: candles[i].time, value: supertrend[i] };

        // Check if trend changed
        if (direction[i] !== direction[i - 1]) {
            // Add overlap point to current segment (end of old trend)
            currentSegment.data.push(point);

            // Push completed segment
            segments.push(currentSegment);

            // Start new segment with overlap point (start of new trend)
            currentSegment = {
                data: [point],
                color: direction[i] === 1 ? uptrendColor : downtrendColor,
                name: direction[i] === 1 ? 'Uptrend' : 'Downtrend'
            };
        } else {
            // Same trend, just add point
            currentSegment.data.push(point);
        }
    }

    // Push last segment
    if (currentSegment.data.length > 0) {
        segments.push(currentSegment);
    }

    console.log(`✅ SuperTrend calculated: ${segments.length} segments`);

    return {
        type: 'multiple',
        series: segments.map(seg => ({
            name: seg.name,
            data: seg.data,
            color: seg.color,
            lineWidth: 2
        }))
    };
}

/**
 * Calculate Bollinger Bands
 * Returns {type: 'multiple', series: [...]}
 */
function calculateIndexBollingerBands(candles, length, std) {
    console.log(`📈 Calculating Bollinger Bands with length ${length}, std ${std}`);

    const upperData = [];
    const middleData = [];
    const lowerData = [];

    for (let i = length - 1; i < candles.length; i++) {
        let sum = 0;
        for (let j = 0; j < length; j++) {
            sum += candles[i - j].close;
        }
        const sma = sum / length;

        let variance = 0;
        for (let j = 0; j < length; j++) {
            variance += Math.pow(candles[i - j].close - sma, 2);
        }
        const stdDev = Math.sqrt(variance / length);

        const upper = sma + std * stdDev;
        const lower = sma - std * stdDev;

        upperData.push({ time: candles[i].time, value: upper });
        middleData.push({ time: candles[i].time, value: sma });
        lowerData.push({ time: candles[i].time, value: lower });
    }

    console.log(`✅ Bollinger Bands calculated: ${middleData.length} points`);

    return {
        type: 'multiple',
        series: [
            { name: 'Upper', data: upperData, color: '#787b86', lineWidth: 1 },
            { name: 'Middle', data: middleData, color: '#2962ff', lineWidth: 2 },
            { name: 'Lower', data: lowerData, color: '#787b86', lineWidth: 1 }
        ]
    };
}

/**
 * Get random color for indicator
 */
function getIndexRandomColor() {
    const colors = [
        '#2962ff', '#ff6d00', '#00c853', '#d500f9', '#00b8d4',
        '#ffd600', '#ff1744', '#651fff', '#00e676', '#ff9100'
    ];
    return colors[Math.floor(Math.random() * colors.length)];
}

/**
 * Show notification
 */
function showIndexNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);

    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === 'success' ? '#089981' : type === 'error' ? '#f23645' : '#2962ff'};
        color: white;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        z-index: 99999;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        animation: slideInRight 0.3s ease-out;
    `;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Mở modal Index Signals
 */
function openIndexSignalsModal() {
    const modal = document.getElementById('indexSignalsModal');
    modal.classList.remove('hidden');

    // Update signals display
    updateIndexSignalsDisplay();
}

/**
 * Đóng modal Index Signals
 */
function closeIndexSignalsModal() {
    const modal = document.getElementById('indexSignalsModal');
    modal.classList.add('hidden');
}

/**
 * Update signals display for index
 */
function updateIndexSignalsDisplay() {
    // Count signals from chart markers
    let buyCount = 0;
    let sellCount = 0;
    let shortCount = 0;
    let coverCount = 0;

    // Try to get markers from global markers array if exists
    if (typeof markers !== 'undefined' && Array.isArray(markers)) {
        markers.forEach(marker => {
            const position = marker.position || '';
            if (position === 'belowBar') buyCount++;
            else if (position === 'aboveBar') {
                if (marker.color === '#ef5350') sellCount++;
                else if (marker.color === '#ff9800') shortCount++;
                else if (marker.color === '#2196f3') coverCount++;
            }
        });
    }

    // Update counts
    document.getElementById('indexBuySignalsCount').textContent = buyCount;
    document.getElementById('indexSellSignalsCount').textContent = sellCount;
    document.getElementById('indexShortSignalsCount').textContent = shortCount;
    document.getElementById('indexCoverSignalsCount').textContent = coverCount;

    // Update recent signals list
    updateIndexRecentSignalsList();
}

/**
 * Update recent signals timeline
 */
function updateIndexRecentSignalsList() {
    const container = document.getElementById('indexRecentSignalsList');

    if (typeof markers === 'undefined' || !Array.isArray(markers) || markers.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; color: #787b86; padding: 30px;">
                No signals detected yet. Signals will appear here when chart is loaded.
            </div>
        `;
        return;
    }

    // Sort markers by time (newest first)
    const sortedMarkers = [...markers].sort((a, b) => b.time - a.time).slice(0, 50);

    container.innerHTML = '';

    sortedMarkers.forEach(marker => {
        const item = document.createElement('div');
        const signalType = marker.position === 'belowBar' ? 'BUY' :
                          marker.color === '#ef5350' ? 'SELL' :
                          marker.color === '#ff9800' ? 'SHORT' : 'COVER';

        const signalColor = marker.position === 'belowBar' ? '#089981' :
                           marker.color === '#ef5350' ? '#f23645' :
                           marker.color === '#ff9800' ? '#ff9800' : '#2196f3';

        const date = new Date(marker.time * 1000);
        const timeStr = date.toLocaleString('vi-VN');

        item.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 12px;
            background: #1e222d;
            border-left: 3px solid ${signalColor};
            border-radius: 4px;
            margin-bottom: 6px;
        `;

        item.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
                <div style="font-weight: 700; color: ${signalColor}; font-size: 12px; min-width: 60px;">
                    ${signalType}
                </div>
                <div style="font-size: 12px; color: #787b86;">
                    ${timeStr}
                </div>
            </div>
            <div style="font-size: 12px; color: #d1d4dc;">
                ${marker.text || ''}
            </div>
        `;

        container.appendChild(item);
    });
}

// Global state for config modal
let currentIndexConfigIndicator = null;
let isEditingIndexIndicator = false;
let editingIndexIndicatorId = null;

/**
 * Mở config modal để configure indicator
 */
function openIndexIndicatorConfigModal(indicator, existingIndicatorId = null) {
    currentIndexConfigIndicator = { ...indicator };
    isEditingIndexIndicator = !!existingIndicatorId;
    editingIndexIndicatorId = existingIndicatorId;

    const modal = document.getElementById('indexIndicatorConfigModal');
    modal.classList.remove('hidden');

    document.getElementById('indexConfigIndicatorType').value = indicator.type;

    if (isEditingIndexIndicator) {
        const existing = indexChartIndicators.find(ind => ind.id === existingIndicatorId);
        document.getElementById('indexConfigIndicatorName').value = existing ? existing.name : indicator.name;

        const color = existing ? existing.color : getIndexRandomColor();
        const lineWidth = existing ? (existing.lineWidth || 2) : 2;

        document.getElementById('indexConfigColor').value = color;
        document.getElementById('indexConfigColorHex').value = color;
        document.getElementById('indexConfigLineWidth').value = lineWidth;

        document.querySelector('#indexIndicatorConfigModal .btn-primary').textContent = 'Update Indicator';
    } else {
        document.getElementById('indexConfigIndicatorName').value = indicator.name;

        const randomColor = getIndexRandomColor();
        document.getElementById('indexConfigColor').value = randomColor;
        document.getElementById('indexConfigColorHex').value = randomColor;
        document.getElementById('indexConfigLineWidth').value = 2;

        document.querySelector('#indexIndicatorConfigModal .btn-primary').textContent = 'Add to Chart';
    }

    // Sync color picker and hex input
    document.getElementById('indexConfigColor').addEventListener('input', function() {
        document.getElementById('indexConfigColorHex').value = this.value;
    });
    document.getElementById('indexConfigColorHex').addEventListener('input', function() {
        if (/^#[0-9A-F]{6}$/i.test(this.value)) {
            document.getElementById('indexConfigColor').value = this.value;
        }
    });

    populateIndexConfigParams(indicator, existingIndicatorId);
}

/**
 * Đóng config modal
 */
function closeIndexIndicatorConfigModal() {
    const modal = document.getElementById('indexIndicatorConfigModal');
    modal.classList.add('hidden');
    currentIndexConfigIndicator = null;
    isEditingIndexIndicator = false;
    editingIndexIndicatorId = null;
}

/**
 * Populate dynamic params
 */
function populateIndexConfigParams(indicator, existingIndicatorId = null) {
    const container = document.getElementById('indexConfigParamsContainer');
    container.innerHTML = '';

    if (!indicator.params || Object.keys(indicator.params).length === 0) {
        return;
    }

    let currentParams = { ...indicator.params };
    if (isEditingIndexIndicator && existingIndicatorId) {
        const existing = indexChartIndicators.find(ind => ind.id === existingIndicatorId);
        if (existing) currentParams = { ...existing.params };
    }

    Object.entries(currentParams).forEach(([key, value]) => {
        const paramDiv = document.createElement('div');
        paramDiv.style.marginBottom = '15px';

        const label = document.createElement('label');
        label.style.cssText = 'display: block; font-size: 12px; color: #787b86; margin-bottom: 5px;';
        label.textContent = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');

        const input = document.createElement('input');
        input.type = typeof value === 'number' ? 'number' : 'text';
        input.value = value;
        input.dataset.paramKey = key;
        input.style.cssText = 'width: 100%; padding: 8px; background: #131722; border: 1px solid #2a2e39; border-radius: 4px; color: #d1d4dc; font-size: 13px;';

        if (typeof value === 'number') {
            input.step = value % 1 === 0 ? '1' : '0.01';
            input.min = '0';
        }

        paramDiv.appendChild(label);
        paramDiv.appendChild(input);
        container.appendChild(paramDiv);
    });
}

/**
 * Save indicator config
 */
function saveIndexIndicatorConfig() {
    if (!currentIndexConfigIndicator) return;

    const name = document.getElementById('indexConfigIndicatorName').value || currentIndexConfigIndicator.name;
    const color = document.getElementById('indexConfigColor').value;
    const lineWidth = parseInt(document.getElementById('indexConfigLineWidth').value) || 2;

    const params = {};
    document.querySelectorAll('#indexConfigParamsContainer input').forEach(input => {
        const key = input.dataset.paramKey;
        const value = input.type === 'number' ? parseFloat(input.value) : input.value;
        params[key] = value;
    });

    if (isEditingIndexIndicator && editingIndexIndicatorId) {
        const existingIndex = indexChartIndicators.findIndex(ind => ind.id === editingIndexIndicatorId);
        if (existingIndex !== -1) {
            indexChartIndicators[existingIndex].name = name;
            indexChartIndicators[existingIndex].color = color;
            indexChartIndicators[existingIndex].lineWidth = lineWidth;
            indexChartIndicators[existingIndex].params = Object.keys(params).length > 0 ? params : indexChartIndicators[existingIndex].params;

            if (indexChartIndicatorSeries[editingIndexIndicatorId]) {
                try {
                    // Check if it's an array of series (multiple) or single series
                    if (Array.isArray(indexChartIndicatorSeries[editingIndexIndicatorId])) {
                        indexChartIndicatorSeries[editingIndexIndicatorId].forEach(series => {
                            chart.removeSeries(series);
                        });
                    } else {
                        chart.removeSeries(indexChartIndicatorSeries[editingIndexIndicatorId]);
                    }
                    delete indexChartIndicatorSeries[editingIndexIndicatorId];
                } catch (e) {
                    console.error('Error removing old series:', e);
                }
            }

            drawIndexIndicatorOnChart(indexChartIndicators[existingIndex]);
            updateIndexActiveIndicatorsList();
            showIndexNotification(`Updated ${name}`, 'success');
        }
    } else {
        const id = `idx_${currentIndexConfigIndicator.type}_${Date.now()}`;

        const indexIndicator = {
            id: id,
            type: currentIndexConfigIndicator.type,
            name: name,
            params: Object.keys(params).length > 0 ? params : currentIndexConfigIndicator.params,
            color: color,
            lineWidth: lineWidth,
            visible: true
        };

        indexChartIndicators.push(indexIndicator);
        drawIndexIndicatorOnChart(indexIndicator);
        updateIndexActiveIndicatorsList();
        showIndexNotification(`Added ${name} to chart`, 'success');
    }

    // Save to localStorage
    saveIndexChartIndicatorsToStorage();

    closeIndexIndicatorConfigModal();
}

/**
 * Edit indicator
 */
function editIndexIndicator(id) {
    const indicator = indexChartIndicators.find(ind => ind.id === id);
    if (!indicator) {
        console.error('Indicator not found:', id);
        return;
    }

    let originalIndicator = null;
    Object.values(indexAvailableIndicators).forEach(category => {
        const found = category.find(ind => ind.type === indicator.type);
        if (found) originalIndicator = found;
    });

    if (!originalIndicator) {
        console.error('Original indicator template not found');
        return;
    }

    openIndexIndicatorConfigModal(indicator, id);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Index Chart Indicators Manager initialized');

    // Load indicators from localStorage after a short delay to ensure chart is ready
    setTimeout(() => {
        loadIndexChartIndicatorsFromStorage();
    }, 1000);
});
