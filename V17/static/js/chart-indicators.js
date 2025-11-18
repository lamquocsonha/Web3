/**
 * Chart Indicators Manager
 * Quản lý indicators hiển thị trên chart (độc lập với sidebar)
 */

// Global state cho chart indicators
let chartIndicators = [];
let chartIndicatorSeries = {}; // Lưu trữ series của indicators trên chart
let currentChartCategory = 'all';

// LocalStorage key
const CHART_INDICATORS_STORAGE_KEY = 'strategy_chart_indicators';

// Danh sách indicators có sẵn (giống như trong sidebar)
const availableIndicators = {
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
        { type: 'SuperTrend', name: 'SuperTrend', params: {
            period: 10,
            multiplier: 3,
            uptrend_color: '#26a69a',
            downtrend_color: '#ef5350'
        } },
        { type: 'PivotPoints', name: 'Pivot Points', params: {
            pp_color: '#ffd600',
            r1_color: '#26a69a', r2_color: '#089981', r3_color: '#00695c',
            s1_color: '#ef5350', s2_color: '#f23645', s3_color: '#c62828'
        } },
        { type: 'HHV', name: 'Highest High (from Base)', params: {} },
        { type: 'LLV', name: 'Lowest Low (from Base)', params: {} }
    ]
};

/**
 * Save chart indicators to localStorage
 */
function saveChartIndicatorsToStorage() {
    try {
        const indicatorsData = chartIndicators.map(ind => ({
            id: ind.id,
            type: ind.type,
            name: ind.name,
            params: ind.params,
            color: ind.color,
            lineWidth: ind.lineWidth,
            visible: ind.visible
        }));
        localStorage.setItem(CHART_INDICATORS_STORAGE_KEY, JSON.stringify(indicatorsData));
        console.log('💾 Saved', indicatorsData.length, 'indicators to localStorage');
    } catch (e) {
        console.error('❌ Error saving indicators to localStorage:', e);
    }
}

/**
 * Load chart indicators from localStorage
 */
function loadChartIndicatorsFromStorage() {
    try {
        const stored = localStorage.getItem(CHART_INDICATORS_STORAGE_KEY);
        if (stored) {
            const indicatorsData = JSON.parse(stored);
            console.log('📂 Loading', indicatorsData.length, 'indicators from localStorage');

            // Clear existing indicators
            chartIndicators = [];
            // Get chart instance once at the beginning
            const chartInstance = typeof workspaceChart !== 'undefined' ? workspaceChart : (typeof chart !== 'undefined' ? chart : null);
            
            // Remove all existing series first
            Object.keys(chartIndicatorSeries).forEach(id => {
                if (chartInstance && chartIndicatorSeries[id]) {
                    try {
                        // Check if it's an array of series (multiple) or single series
                        if (Array.isArray(chartIndicatorSeries[id])) {
                            chartIndicatorSeries[id].forEach(series => {
                                chartInstance.removeSeries(series);
                            });
                        } else {
                            chartInstance.removeSeries(chartIndicatorSeries[id]);
                        }
                    } catch (e) {
                        console.error('Error removing series:', e);
                    }
                }
            });
            chartIndicatorSeries = {};
            
            // IMPORTANT: Clear chartIndicators array to prevent duplicates
            chartIndicators = [];

            // Restore indicators
            indicatorsData.forEach(ind => {
                chartIndicators.push(ind);
                // Draw indicator on chart if chart is ready
                if (chartInstance && typeof offlineData !== 'undefined' && offlineData && offlineData.candlesticks && offlineData.candlesticks.length > 0) {
                    drawIndicatorOnChart(ind);
                }
            });

            console.log('✅ Loaded', chartIndicators.length, 'indicators');
        }
    } catch (e) {
        console.error('❌ Error loading indicators from localStorage:', e);
    }
}

/**
 * Mở modal Chart Indicators
 */
function openChartIndicatorsModal() {
    const modal = document.getElementById('chartIndicatorsModal');
    modal.classList.remove('hidden');

    // Populate available indicators
    populateChartAvailableIndicators();

    // Update active indicators list
    updateChartActiveIndicatorsList();
}

/**
 * Đóng modal Chart Indicators
 */
function closeChartIndicatorsModal() {
    const modal = document.getElementById('chartIndicatorsModal');
    modal.classList.add('hidden');
}

/**
 * Populate danh sách indicators có sẵn
 */
function populateChartAvailableIndicators() {
    const container = document.getElementById('chartAvailableIndicatorsList');
    container.innerHTML = '';

    // Get indicators based on current category
    let indicatorsToShow = [];
    if (currentChartCategory === 'all') {
        Object.values(availableIndicators).forEach(category => {
            indicatorsToShow = indicatorsToShow.concat(category);
        });
    } else {
        indicatorsToShow = availableIndicators[currentChartCategory] || [];
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
        card.addEventListener('click', () => addChartIndicator(indicator));

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
function filterChartIndicators(category) {
    currentChartCategory = category;

    // Update active category button
    document.querySelectorAll('#chartIndicatorsModal .category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Re-populate indicators
    populateChartAvailableIndicators();
}

// Global state for config modal
let currentConfigIndicator = null;
let isEditingIndicator = false;
let editingIndicatorId = null;

/**
 * Thêm indicator vào chart (mở config modal trước)
 */
function addChartIndicator(indicator) {
    // Open config modal instead of adding directly
    openChartIndicatorConfigModal(indicator);
}

/**
 * Mở config modal để configure indicator
 */
function openChartIndicatorConfigModal(indicator, existingIndicatorId = null) {
    currentConfigIndicator = { ...indicator };
    isEditingIndicator = !!existingIndicatorId;
    editingIndicatorId = existingIndicatorId;

    const modal = document.getElementById('chartIndicatorConfigModal');
    modal.classList.remove('hidden');

    // Set indicator type
    document.getElementById('chartConfigIndicatorType').value = indicator.type;

    // Set indicator name
    if (isEditingIndicator) {
        const existing = chartIndicators.find(ind => ind.id === existingIndicatorId);
        document.getElementById('chartConfigIndicatorName').value = existing ? existing.name : indicator.name;

        // Set existing color and line width
        const color = existing ? existing.color : getRandomColor();
        const lineWidth = existing ? (existing.lineWidth || 2) : 2;

        document.getElementById('chartConfigColor').value = color;
        document.getElementById('chartConfigColorHex').value = color;
        document.getElementById('chartConfigLineWidth').value = lineWidth;

        // Update button text
        document.querySelector('#chartIndicatorConfigModal .btn-primary').textContent = 'Update Indicator';
    } else {
        document.getElementById('chartConfigIndicatorName').value = indicator.name;

        // Set random color
        const randomColor = getRandomColor();
        document.getElementById('chartConfigColor').value = randomColor;
        document.getElementById('chartConfigColorHex').value = randomColor;
        document.getElementById('chartConfigLineWidth').value = 2;

        // Update button text
        document.querySelector('#chartIndicatorConfigModal .btn-primary').textContent = 'Add to Chart';
    }

    // Sync color picker and hex input
    document.getElementById('chartConfigColor').addEventListener('input', function() {
        document.getElementById('chartConfigColorHex').value = this.value;
    });
    document.getElementById('chartConfigColorHex').addEventListener('input', function() {
        if (/^#[0-9A-F]{6}$/i.test(this.value)) {
            document.getElementById('chartConfigColor').value = this.value;
        }
    });

    // Populate dynamic parameters
    populateChartConfigParams(indicator, existingIndicatorId);
}

/**
 * Đóng config modal
 */
function closeChartIndicatorConfigModal() {
    const modal = document.getElementById('chartIndicatorConfigModal');
    modal.classList.add('hidden');
    currentConfigIndicator = null;
    isEditingIndicator = false;
    editingIndicatorId = null;
}

/**
 * Populate dynamic params vào config modal
 */
function populateChartConfigParams(indicator, existingIndicatorId = null) {
    const container = document.getElementById('chartConfigParamsContainer');
    container.innerHTML = '';

    if (!indicator.params || Object.keys(indicator.params).length === 0) {
        return;
    }

    // Get existing values if editing
    let currentParams = { ...indicator.params };
    if (isEditingIndicator && existingIndicatorId) {
        const existing = chartIndicators.find(ind => ind.id === existingIndicatorId);
        if (existing) {
            currentParams = { ...existing.params };
        }
    }

    // Create input for each parameter
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
 * Save indicator config và add/update vào chart
 */
function saveChartIndicatorConfig() {
    if (!currentConfigIndicator) return;

    // Get values from modal
    const name = document.getElementById('chartConfigIndicatorName').value || currentConfigIndicator.name;
    const color = document.getElementById('chartConfigColor').value;
    const lineWidth = parseInt(document.getElementById('chartConfigLineWidth').value) || 2;

    // Get params from dynamic inputs
    const params = {};
    document.querySelectorAll('#chartConfigParamsContainer input').forEach(input => {
        const key = input.dataset.paramKey;
        const value = input.type === 'number' ? parseFloat(input.value) : input.value;
        params[key] = value;
    });

    if (isEditingIndicator && editingIndicatorId) {
        // Update existing indicator
        const existingIndex = chartIndicators.findIndex(ind => ind.id === editingIndicatorId);
        if (existingIndex !== -1) {
            chartIndicators[existingIndex].name = name;
            chartIndicators[existingIndex].color = color;
            chartIndicators[existingIndex].lineWidth = lineWidth;
            chartIndicators[existingIndex].params = Object.keys(params).length > 0 ? params : chartIndicators[existingIndex].params;

            // Remove old series
            const chartInstance = typeof workspaceChart !== 'undefined' ? workspaceChart : (typeof chart !== 'undefined' ? chart : null);

            if (chartIndicatorSeries[editingIndicatorId] && chartInstance) {
                try {
                    // Check if it's an array of series (multiple) or single series
                    if (Array.isArray(chartIndicatorSeries[editingIndicatorId])) {
                        chartIndicatorSeries[editingIndicatorId].forEach(series => {
                            chartInstance.removeSeries(series);
                        });
                    } else {
                        chartInstance.removeSeries(chartIndicatorSeries[editingIndicatorId]);
                    }
                    delete chartIndicatorSeries[editingIndicatorId];
                } catch (e) {
                    console.error('Error removing old series:', e);
                }
            }

            // Redraw indicator
            drawIndicatorOnChart(chartIndicators[existingIndex]);
            updateChartActiveIndicatorsList();
            showNotification(`Updated ${name}`, 'success');
        }
    } else {
        // Add new indicator
        const id = `${currentConfigIndicator.type}_${Date.now()}`;

        const chartIndicator = {
            id: id,
            type: currentConfigIndicator.type,
            name: name,
            params: Object.keys(params).length > 0 ? params : currentConfigIndicator.params,
            color: color,
            lineWidth: lineWidth,
            visible: true
        };

        chartIndicators.push(chartIndicator);

        // Draw indicator on chart
        drawIndicatorOnChart(chartIndicator);

        // Update active indicators list
        updateChartActiveIndicatorsList();

        // Show notification
        showNotification(`Added ${name} to chart`, 'success');
    }

    // Save to localStorage
    saveChartIndicatorsToStorage();

    // Close modal
    closeChartIndicatorConfigModal();
}

/**
 * Edit indicator configuration
 */
function editChartIndicator(id) {
    const indicator = chartIndicators.find(ind => ind.id === id);
    if (!indicator) {
        console.error('Indicator not found:', id);
        return;
    }

    // Find original indicator template
    const originalType = indicator.type;
    let originalIndicator = null;

    // Search in all categories
    Object.values(availableIndicators).forEach(category => {
        const found = category.find(ind => ind.type === originalType);
        if (found) originalIndicator = found;
    });

    if (!originalIndicator) {
        console.error('Original indicator template not found');
        return;
    }

    // Open config modal in edit mode
    openChartIndicatorConfigModal(indicator, id);
}

/**
 * Xóa indicator khỏi chart
 */
function removeChartIndicator(id) {
    // Remove from array
    chartIndicators = chartIndicators.filter(ind => ind.id !== id);

    // Remove series from chart
    const chartInstance = typeof workspaceChart !== 'undefined' ? workspaceChart : (typeof chart !== 'undefined' ? chart : null);

    if (chartIndicatorSeries[id] && chartInstance) {
        try {
            // Check if it's an array of series (multiple) or single series
            if (Array.isArray(chartIndicatorSeries[id])) {
                chartIndicatorSeries[id].forEach(series => {
                    chartInstance.removeSeries(series);
                });
            } else {
                chartInstance.removeSeries(chartIndicatorSeries[id]);
            }
            delete chartIndicatorSeries[id];
        } catch (e) {
            console.error('Error removing indicator series:', e);
        }
    }

    // Update active indicators list
    updateChartActiveIndicatorsList();

    // Save to localStorage
    saveChartIndicatorsToStorage();

    showNotification('Indicator removed from chart', 'info');
}

/**
 * Update danh sách active indicators
 */
function updateChartActiveIndicatorsList() {
    const container = document.getElementById('chartActiveIndicatorsList');

    if (chartIndicators.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; color: #787b86; padding: 20px;">
                No indicators added yet. Add indicators from the list below.
            </div>
        `;
        return;
    }

    container.innerHTML = '';

    chartIndicators.forEach(indicator => {
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
                <button onclick="editChartIndicator('${indicator.id}')"
                    style="padding: 6px 10px; background: #2962ff; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 11px;">
                    ✏️ Edit
                </button>
                <button onclick="toggleChartIndicatorVisibility('${indicator.id}')"
                    style="padding: 6px 10px; background: #2a2e39; color: #d1d4dc; border: none; border-radius: 3px; cursor: pointer; font-size: 11px;">
                    ${indicator.visible ? '👁️ Hide' : '👁️‍🗨️ Show'}
                </button>
                <button onclick="removeChartIndicator('${indicator.id}')"
                    style="padding: 6px 10px; background: #ef5350; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 11px;">
                    ✕
                </button>
            </div>
        `;

        container.appendChild(item);
    });
}

/**
 * Toggle indicator visibility
 */
function toggleChartIndicatorVisibility(id) {
    const indicator = chartIndicators.find(ind => ind.id === id);
    if (indicator) {
        indicator.visible = !indicator.visible;

        // Toggle series visibility on chart
        if (chartIndicatorSeries[id]) {
            try {
                // Check if it's an array of series (multiple) or single series
                if (Array.isArray(chartIndicatorSeries[id])) {
                    chartIndicatorSeries[id].forEach(series => {
                        series.applyOptions({ visible: indicator.visible });
                    });
                } else {
                    chartIndicatorSeries[id].applyOptions({ visible: indicator.visible });
                }
            } catch (e) {
                console.error('Error toggling indicator visibility:', e);
            }
        }

        updateChartActiveIndicatorsList();

        // Save to localStorage
        saveChartIndicatorsToStorage();
    }
}

/**
 * Vẽ indicator lên chart
 */
function drawIndicatorOnChart(indicator) {
    // Check if chart exists (strategy uses workspaceChart)
    const chartInstance = typeof workspaceChart !== 'undefined' ? workspaceChart : (typeof chart !== 'undefined' ? chart : null);

    if (!chartInstance) {
        console.error('❌ Chart not initialized');
        showNotification('Chart not ready. Please wait...', 'error');
        return;
    }

    // Get candle data from offlineData (defined in data-manager.js)
    const candleData = (typeof offlineData !== 'undefined' && offlineData && offlineData.candlesticks)
        ? offlineData.candlesticks
        : null;

    if (!candleData || candleData.length === 0) {
        console.error('❌ No candle data available');
        showNotification('No data available. Please load data first.', 'error');
        return;
    }

    console.log('✅ Drawing indicator on chart:', indicator.name, 'with', candleData.length, 'candles');

    // Calculate indicator values
    const indicatorData = calculateIndicatorValues(indicator, candleData);

    if (!indicatorData) {
        console.error('❌ No indicator data calculated');
        showNotification('Failed to calculate indicator values', 'error');
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

                    const lineSeries = chartInstance.addLineSeries({
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
            chartIndicatorSeries[indicator.id] = seriesArray;
            showNotification(`${indicator.name} added successfully`, 'success');

        } else {
            // Single series (regular indicators)
            if (!indicatorData || indicatorData.length === 0) {
                console.error('❌ No indicator data calculated');
                showNotification('Failed to calculate indicator values', 'error');
                return;
            }

            console.log('✅ Calculated indicator data:', indicatorData.length, 'points');

            const lineSeries = chartInstance.addLineSeries({
                color: indicator.color,
                lineWidth: indicator.lineWidth || 2,
                title: indicator.name,
                priceScaleId: 'right',
                visible: indicator.visible
            });

            lineSeries.setData(indicatorData);

            // Store single series
            chartIndicatorSeries[indicator.id] = lineSeries;

            console.log(`✅ Drew ${indicator.name} on chart with ${indicatorData.length} points`);
            showNotification(`${indicator.name} added successfully`, 'success');
        }
    } catch (e) {
        console.error('❌ Error drawing indicator on chart:', e);
        showNotification('Failed to draw indicator on chart', 'error');
    }
}

/**
 * Calculate indicator values
 * Returns either array of {time, value} or {type: 'multiple', series: [...]}
 */
function calculateIndicatorValues(indicator, candles) {
    console.log('📊 Calculating indicator:', indicator.type, 'with params:', indicator.params);

    try {
        switch (indicator.type) {
            case 'EMA':
            case 'SMA':
            case 'WMA':
                return calculateMovingAverage(candles, indicator.params.length, indicator.type);

            case 'RSI':
                return calculateRSI(candles, indicator.params.length);

            case 'BollingerBands':
                return calculateBollingerBands(candles, indicator.params.length, indicator.params.std);

            case 'SuperTrend':
                return calculateSuperTrend(candles, indicator.params);

            case 'ATR':
                return calculateATR(candles, indicator.params.length || 14);

            case 'DEMA':
            case 'TEMA':
                // Use EMA calculation for now
                return calculateMovingAverage(candles, indicator.params.length, 'EMA');

            case 'PivotPoints':
                return calculatePivotPoints(candles, indicator.params);

            case 'HHV':
                return calculateHHV(candles);

            case 'LLV':
                return calculateLLV(candles);

            case 'MACD':
            case 'Stochastic':
            case 'CCI':
            case 'MFI':
            case 'KeltnerChannel':
            case 'DonchianChannel':
            case 'OBV':
            case 'VWAP':
                console.warn(`⚠️ Indicator type ${indicator.type} not fully implemented yet, using SMA as placeholder`);
                return calculateMovingAverage(candles, 20, 'SMA');

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
function calculateMovingAverage(candles, length, type) {
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
        // WMA = (P1*n + P2*(n-1) + ... + Pn*1) / (n + (n-1) + ... + 1)
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
function calculateRSI(candles, length) {
    const result = [];
    const gains = [];
    const losses = [];

    // Calculate price changes
    for (let i = 1; i < candles.length; i++) {
        const change = candles[i].close - candles[i - 1].close;
        gains.push(change > 0 ? change : 0);
        losses.push(change < 0 ? -change : 0);
    }

    // Calculate initial average gain and loss
    let avgGain = gains.slice(0, length).reduce((sum, g) => sum + g, 0) / length;
    let avgLoss = losses.slice(0, length).reduce((sum, l) => sum + l, 0) / length;

    // Calculate RSI
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
function calculateATR(candles, length) {
    const result = [];
    const trueRanges = [];

    // Calculate True Range for each candle
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

    // Calculate initial ATR (SMA of TR)
    let atr = trueRanges.slice(0, length).reduce((sum, tr) => sum + tr, 0) / length;

    // Calculate smoothed ATR
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
 * Calculate SuperTrend (using library formula)
 * Returns {type: 'multiple', series: [...]}
 */
function calculateSuperTrend(candles, params) {
    const period = params.period || 10;
    const multiplier = params.multiplier || 3;
    const uptrendColor = params.uptrend_color || '#26a69a';
    const downtrendColor = params.downtrend_color || '#ef5350';

    console.log(`📈 Calculating SuperTrend with period ${period}, multiplier ${multiplier}`);

    if (!candles || candles.length < period + 1) {
        console.error('❌ Not enough candles for SuperTrend calculation');
        return { type: 'multiple', series: [] };
    }

    // Calculate ATR using EMA smoothing (matching Python library)
    const atrValues = calculateATRArray(candles, period);

    // Calculate HL average
    const hlAvg = candles.map(c => (c.high + c.low) / 2);

    // Calculate basic upper and lower bands
    const basicUpper = [];
    const basicLower = [];

    for (let i = 0; i < candles.length; i++) {
        basicUpper[i] = hlAvg[i] + (multiplier * atrValues[i]);
        basicLower[i] = hlAvg[i] - (multiplier * atrValues[i]);
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
 * Calculate ATR as array (EMA smoothing - matching Python library)
 */
function calculateATRArray(candles, period) {
    const trueRanges = new Array(candles.length);

    // Calculate True Range for each candle
    trueRanges[0] = candles[0].high - candles[0].low;

    for (let i = 1; i < candles.length; i++) {
        const high = candles[i].high;
        const low = candles[i].low;
        const prevClose = candles[i - 1].close;

        trueRanges[i] = Math.max(
            high - low,
            Math.abs(high - prevClose),
            Math.abs(low - prevClose)
        );
    }

    // Calculate ATR using EMA
    const atr = new Array(candles.length);
    const multiplier = 2 / (period + 1);

    // Initialize with first TR value
    atr[0] = trueRanges[0];

    // Calculate EMA of TR
    for (let i = 1; i < candles.length; i++) {
        atr[i] = (trueRanges[i] - atr[i - 1]) * multiplier + atr[i - 1];
    }

    return atr;
}

/**
 * Calculate Bollinger Bands
 * Returns {type: 'multiple', series: [...]}
 */
function calculateBollingerBands(candles, length, std) {
    console.log(`📈 Calculating Bollinger Bands with length ${length}, std ${std}`);

    const upperData = [];
    const middleData = [];
    const lowerData = [];

    for (let i = length - 1; i < candles.length; i++) {
        // Calculate SMA (middle band)
        let sum = 0;
        for (let j = 0; j < length; j++) {
            sum += candles[i - j].close;
        }
        const sma = sum / length;

        // Calculate standard deviation
        let variance = 0;
        for (let j = 0; j < length; j++) {
            variance += Math.pow(candles[i - j].close - sma, 2);
        }
        const stdDev = Math.sqrt(variance / length);

        // Calculate bands
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
 * Calculate Pivot Points (Classic Daily)
 * Returns {type: 'multiple', series: [...]}
 */
function calculatePivotPoints(candles, params) {
    console.log(`📈 Calculating Pivot Points`);

    if (!candles || candles.length < 2) {
        console.error('❌ Not enough candles for Pivot Points calculation');
        return { type: 'multiple', series: [] };
    }

    // Use last complete candle (yesterday's data)
    const lastCandle = candles[candles.length - 2];
    const h = lastCandle.high;
    const l = lastCandle.low;
    const c = lastCandle.close;

    // Calculate pivot and levels
    const pp = (h + l + c) / 3;
    const r1 = (2 * pp) - l;
    const s1 = (2 * pp) - h;
    const r2 = pp + (r1 - s1);
    const s2 = pp - (r1 - s1);
    const r3 = pp + (r2 - s1);
    const s3 = pp - (r2 - s1);

    // Create horizontal lines for all candles
    const createLine = (value, color) => {
        return candles.map(c => ({ time: c.time, value }));
    };

    // Get colors from params or use defaults
    const ppColor = params.pp_color || '#ffd600';
    const r1Color = params.r1_color || '#26a69a';
    const r2Color = params.r2_color || '#089981';
    const r3Color = params.r3_color || '#00695c';
    const s1Color = params.s1_color || '#ef5350';
    const s2Color = params.s2_color || '#f23645';
    const s3Color = params.s3_color || '#c62828';

    console.log(`✅ Pivot Points calculated: PP=${pp.toFixed(2)}, R1=${r1.toFixed(2)}, R2=${r2.toFixed(2)}, R3=${r3.toFixed(2)}, S1=${s1.toFixed(2)}, S2=${s2.toFixed(2)}, S3=${s3.toFixed(2)}`);

    return {
        type: 'multiple',
        series: [
            { name: 'PP', data: createLine(pp, ppColor), color: ppColor, lineWidth: 2 },
            { name: 'R1', data: createLine(r1, r1Color), color: r1Color, lineWidth: 1 },
            { name: 'R2', data: createLine(r2, r2Color), color: r2Color, lineWidth: 1 },
            { name: 'R3', data: createLine(r3, r3Color), color: r3Color, lineWidth: 1 },
            { name: 'S1', data: createLine(s1, s1Color), color: s1Color, lineWidth: 1 },
            { name: 'S2', data: createLine(s2, s2Color), color: s2Color, lineWidth: 1 },
            { name: 'S3', data: createLine(s3, s3Color), color: s3Color, lineWidth: 1 }
        ]
    };
}

/**
 * Calculate HHV (Highest High from Base Time) - Resets daily
 */
function calculateHHV(candles) {
    console.log(`📈 Calculating HHV from base time`);

    if (!candles || candles.length === 0) {
        console.error('❌ No candles for HHV calculation');
        return [];
    }

    // Get base time from strategy config (default 09:00)
    let baseTimeStr = '09:00';
    if (typeof window.strategyConfig !== 'undefined' &&
        window.strategyConfig?.exit_rules?.base_time) {
        baseTimeStr = window.strategyConfig.exit_rules.base_time;
    } else if (typeof window.currentStrategyConfig !== 'undefined' &&
               window.currentStrategyConfig?.exit_rules?.base_time) {
        baseTimeStr = window.currentStrategyConfig.exit_rules.base_time;
    }

    const [baseHour, baseMinute] = baseTimeStr.split(':').map(Number);
    console.log(`📊 Using base time: ${baseTimeStr} (${baseHour}:${baseMinute})`);

    const result = [];

    for (let i = 0; i < candles.length; i++) {
        const currentCandle = candles[i];
        const currentTime = new Date(currentCandle.time * 1000);
        const currentYear = currentTime.getFullYear();
        const currentMonth = currentTime.getMonth();
        const currentDay = currentTime.getDate();

        // Find session start (base_time) on SAME DAY
        let sessionStartIndex = i;
        for (let j = i; j >= 0; j--) {
            const time = new Date(candles[j].time * 1000);
            const year = time.getFullYear();
            const month = time.getMonth();
            const day = time.getDate();
            const hour = time.getHours();
            const minute = time.getMinutes();

            // If we've gone to a different day, stop
            if (year !== currentYear || month !== currentMonth || day !== currentDay) {
                sessionStartIndex = j + 1;
                break;
            }

            // If we hit base_time on same day
            if (hour === baseHour && minute === baseMinute) {
                sessionStartIndex = j;
                break;
            }

            // If we go before base_time on same day
            if (hour < baseHour || (hour === baseHour && minute < baseMinute)) {
                sessionStartIndex = j + 1;
                break;
            }
        }

        // Calculate HHV from session start to current
        let hhv = candles[sessionStartIndex].high;
        for (let j = sessionStartIndex; j <= i; j++) {
            if (candles[j].high > hhv) {
                hhv = candles[j].high;
            }
        }

        result.push({ time: currentCandle.time, value: hhv });
    }

    console.log(`✅ HHV calculated: ${result.length} points (resets daily at ${baseTimeStr})`);
    return result;
}

/**
 * Calculate LLV (Lowest Low from Base Time) - Resets daily
 */
function calculateLLV(candles) {
    console.log(`📈 Calculating LLV from base time`);

    if (!candles || candles.length === 0) {
        console.error('❌ No candles for LLV calculation');
        return [];
    }

    // Get base time from strategy config (default 09:00)
    let baseTimeStr = '09:00';
    if (typeof window.strategyConfig !== 'undefined' &&
        window.strategyConfig?.exit_rules?.base_time) {
        baseTimeStr = window.strategyConfig.exit_rules.base_time;
    } else if (typeof window.currentStrategyConfig !== 'undefined' &&
               window.currentStrategyConfig?.exit_rules?.base_time) {
        baseTimeStr = window.currentStrategyConfig.exit_rules.base_time;
    }

    const [baseHour, baseMinute] = baseTimeStr.split(':').map(Number);
    console.log(`📊 Using base time: ${baseTimeStr} (${baseHour}:${baseMinute})`);

    const result = [];

    for (let i = 0; i < candles.length; i++) {
        const currentCandle = candles[i];
        const currentTime = new Date(currentCandle.time * 1000);
        const currentYear = currentTime.getFullYear();
        const currentMonth = currentTime.getMonth();
        const currentDay = currentTime.getDate();

        // Find session start (base_time) on SAME DAY
        let sessionStartIndex = i;
        for (let j = i; j >= 0; j--) {
            const time = new Date(candles[j].time * 1000);
            const year = time.getFullYear();
            const month = time.getMonth();
            const day = time.getDate();
            const hour = time.getHours();
            const minute = time.getMinutes();

            // If we've gone to a different day, stop
            if (year !== currentYear || month !== currentMonth || day !== currentDay) {
                sessionStartIndex = j + 1;
                break;
            }

            // If we hit base_time on same day
            if (hour === baseHour && minute === baseMinute) {
                sessionStartIndex = j;
                break;
            }

            // If we go before base_time on same day
            if (hour < baseHour || (hour === baseHour && minute < baseMinute)) {
                sessionStartIndex = j + 1;
                break;
            }
        }

        // Calculate LLV from session start to current
        let llv = candles[sessionStartIndex].low;
        for (let j = sessionStartIndex; j <= i; j++) {
            if (candles[j].low < llv) {
                llv = candles[j].low;
            }
        }

        result.push({ time: currentCandle.time, value: llv });
    }

    console.log(`✅ LLV calculated: ${result.length} points (resets daily at ${baseTimeStr})`);
    return result;
}

/**
 * Get random color for indicator
 */
function getRandomColor() {
    const colors = [
        '#2962ff', '#ff6d00', '#00c853', '#d500f9', '#00b8d4',
        '#ffd600', '#ff1744', '#651fff', '#00e676', '#ff9100'
    ];
    return colors[Math.floor(Math.random() * colors.length)];
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);

    // Create toast notification
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

    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Mở modal Chart Signals
 */
function openChartSignalsModal() {
    const modal = document.getElementById('chartSignalsModal');
    modal.classList.remove('hidden');

    // Update signals display
    updateChartSignalsDisplay();
}

/**
 * Đóng modal Chart Signals
 */
function closeChartSignalsModal() {
    const modal = document.getElementById('chartSignalsModal');
    modal.classList.add('hidden');
}

/**
 * Update signals display
 */
function updateChartSignalsDisplay() {
    // Get signals from strategy config
    const longSignals = strategyConfig?.entry_conditions?.long || [];
    const shortSignals = strategyConfig?.entry_conditions?.short || [];

    // Update counts
    document.getElementById('chartLongSignalsCount').textContent = longSignals.length;
    document.getElementById('chartShortSignalsCount').textContent = shortSignals.length;
    document.getElementById('chartTotalSignalsCount').textContent = longSignals.length + shortSignals.length;

    // Update long signals list
    const longSignalsList = document.getElementById('chartLongSignalsList');
    if (longSignals.length === 0) {
        longSignalsList.innerHTML = `
            <div style="text-align: center; color: #787b86; padding: 15px;">
                No long entry signals configured
            </div>
        `;
    } else {
        longSignalsList.innerHTML = '';
        longSignals.forEach((signal, index) => {
            const item = createSignalItem(signal, index, 'long');
            longSignalsList.appendChild(item);
        });
    }

    // Update short signals list
    const shortSignalsList = document.getElementById('chartShortSignalsList');
    if (shortSignals.length === 0) {
        shortSignalsList.innerHTML = `
            <div style="text-align: center; color: #787b86; padding: 15px;">
                No short entry signals configured
            </div>
        `;
    } else {
        shortSignalsList.innerHTML = '';
        shortSignals.forEach((signal, index) => {
            const item = createSignalItem(signal, index, 'short');
            shortSignalsList.appendChild(item);
        });
    }
}

/**
 * Create signal item element
 */
function createSignalItem(signal, index, type) {
    const item = document.createElement('div');
    item.style.cssText = `
        background: #1e222d;
        border: 1px solid #2a2e39;
        border-left: 3px solid ${type === 'long' ? '#089981' : '#f23645'};
        border-radius: 4px;
        padding: 12px;
        margin-bottom: 10px;
    `;

    const conditionsCount = signal.conditions?.length || 0;
    const conditionText = signal.condition || 'No condition defined';

    item.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="font-weight: 600; color: ${type === 'long' ? '#089981' : '#f23645'}; font-size: 14px;">
                ${signal.name || `${type.charAt(0).toUpperCase() + type.slice(1)} Signal ${index + 1}`}
            </div>
            <div style="font-size: 11px; color: #787b86;">
                ${conditionsCount} condition${conditionsCount !== 1 ? 's' : ''}
            </div>
        </div>
        <div style="font-size: 12px; color: #d1d4dc; background: #131722; padding: 8px; border-radius: 3px; font-family: monospace;">
            ${conditionText.substring(0, 150)}${conditionText.length > 150 ? '...' : ''}
        </div>
    `;

    return item;
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Chart Indicators Manager initialized');

    // Load indicators from localStorage after a short delay to ensure chart is ready
    setTimeout(() => {
        loadChartIndicatorsFromStorage();
    }, 1000);
});
