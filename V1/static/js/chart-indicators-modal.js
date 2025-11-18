// Chart Indicators & Signals Modal Component
class ChartIndicatorsModal {
    constructor(chartInstance, chartType = 'manual') {
        this.chart = chartInstance;
        this.chartType = chartType; // 'manual', 'bot', 'strategy'
        this.indicators = new Map(); // Store active indicators
        this.indicatorSeries = new Map(); // Store indicator series on chart
        this.signals = {
            buy: [],
            sell: [],
            short: [],
            cover: []
        };
        
        // Load saved indicators for this chart type
        this.loadIndicatorsFromStorage();
        
        // Available indicators configuration
        this.availableIndicators = {
            EMA: {
                name: 'EMA',
                displayName: 'Exponential Moving Average',
                category: 'Trend',
                defaultParams: { length: 20 },
                color: '#ff9100'
            },
            SMA: {
                name: 'SMA',
                displayName: 'Simple Moving Average',
                category: 'Trend',
                defaultParams: { length: 50 },
                color: '#2196f3'
            },
            WMA: {
                name: 'WMA',
                displayName: 'Weighted Moving Average',
                category: 'Trend',
                defaultParams: { length: 20 },
                color: '#9c27b0'
            },
            DEMA: {
                name: 'DEMA',
                displayName: 'Double Exponential Moving Average',
                category: 'Trend',
                defaultParams: { length: 20 },
                color: '#00bcd4'
            },
            TEMA: {
                name: 'TEMA',
                displayName: 'Triple Exponential Moving Average',
                category: 'Trend',
                defaultParams: { length: 20 },
                color: '#4caf50'
            },
            RSI: {
                name: 'RSI',
                displayName: 'Relative Strength Index',
                category: 'Momentum',
                defaultParams: { length: 14, overbought: 70, oversold: 30 },
                color: '#ff5722',
                overlay: false
            },
            MACD: {
                name: 'MACD',
                displayName: 'MACD',
                category: 'Momentum',
                defaultParams: { fast: 12, slow: 26, signal: 9 },
                color: '#3f51b5',
                overlay: false
            },
            Stochastic: {
                name: 'Stochastic',
                displayName: 'Stochastic Oscillator',
                category: 'Momentum',
                defaultParams: { k_period: 14, d_period: 3, overbought: 80, oversold: 20 },
                color: '#e91e63',
                overlay: false
            },
            CCI: {
                name: 'CCI',
                displayName: 'Commodity Channel Index',
                category: 'Momentum',
                defaultParams: { length: 20 },
                color: '#ff9800',
                overlay: false
            },
            MFI: {
                name: 'MFI',
                displayName: 'Money Flow Index',
                category: 'Volume',
                defaultParams: { length: 14 },
                color: '#00acc1',
                overlay: false
            },
            'Bollinger Bands': {
                name: 'Bollinger Bands',
                displayName: 'Bollinger Bands',
                category: 'Volatility',
                defaultParams: { length: 20, stdDev: 2 },
                color: '#9c27b0',
                overlay: true
            },
            ATR: {
                name: 'ATR',
                displayName: 'Average True Range',
                category: 'Volatility',
                defaultParams: { length: 14 },
                color: '#f44336',
                overlay: false
            },
            'Highest High': {
                name: 'Highest High',
                displayName: 'Highest High',
                category: 'Custom',
                defaultParams: { length: 20 },
                color: '#4caf50',
                overlay: true
            },
            'Lowest Low': {
                name: 'Lowest Low',
                displayName: 'Lowest Low',
                category: 'Custom',
                defaultParams: { length: 20 },
                color: '#f44336',
                overlay: true
            }
        };
        
        this.initModal();
    }
    
    initModal() {
        // Create indicators modal
        const indicatorsModal = `
            <div id="chartIndicatorsModal" class="modal">
                <div class="modal-content" style="max-width: 900px;">
                    <div class="modal-header">
                        <h5><i class="fas fa-chart-line"></i> Chart Indicators</h5>
                        <button class="close-btn" onclick="window.chartIndicatorsModal.closeIndicatorsModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="indicators-tabs">
                            <button class="tab-btn active" data-tab="all">All</button>
                            <button class="tab-btn" data-tab="trend">Trend</button>
                            <button class="tab-btn" data-tab="momentum">Momentum</button>
                            <button class="tab-btn" data-tab="volatility">Volatility</button>
                            <button class="tab-btn" data-tab="volume">Volume</button>
                            <button class="tab-btn" data-tab="custom">Custom</button>
                        </div>
                        
                        <div class="indicators-section">
                            <h6>Active Indicators on Chart</h6>
                            <div id="activeIndicatorsList" class="indicators-list">
                                <p class="no-data">No indicators added yet</p>
                            </div>
                        </div>
                        
                        <div class="indicators-section">
                            <h6>Available Indicators</h6>
                            <div id="availableIndicatorsList" class="indicators-grid">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Create configure indicator modal
        const configureModal = `
            <div id="configureIndicatorModal" class="modal">
                <div class="modal-content" style="max-width: 700px;">
                    <div class="modal-header">
                        <h5><i class="fas fa-cog"></i> Configure Indicator</h5>
                        <button class="close-btn" onclick="window.chartIndicatorsModal.closeConfigureModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label>Indicator Type</label>
                            <input type="text" id="indicatorType" class="form-control" readonly>
                        </div>
                        
                        <div class="form-group">
                            <label>Display Name</label>
                            <input type="text" id="indicatorDisplayName" class="form-control">
                        </div>
                        
                        <div class="form-group">
                            <label>Line Color</label>
                            <div style="display: flex; gap: 10px; align-items: center;">
                                <input type="color" id="indicatorColor" class="color-picker">
                                <input type="text" id="indicatorColorHex" class="form-control" style="width: 120px;">
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label>Line Width</label>
                            <input type="number" id="indicatorLineWidth" class="form-control" min="1" max="5" value="2">
                        </div>
                        
                        <div id="indicatorParams">
                            <!-- Dynamic parameters will be added here -->
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="window.chartIndicatorsModal.closeConfigureModal()">Cancel</button>
                        <button class="btn btn-primary" onclick="window.chartIndicatorsModal.saveIndicator()">
                            <span id="saveIndicatorBtnText">Add to Chart</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Create signals modal
        const signalsModal = `
            <div id="chartSignalsModal" class="modal">
                <div class="modal-content" style="max-width: 900px;">
                    <div class="modal-header">
                        <h5><i class="fas fa-signal"></i> Chart Signals</h5>
                        <button class="close-btn" onclick="window.chartIndicatorsModal.closeSignalsModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="signals-summary">
                            <h6>Signals Summary</h6>
                            <div class="signals-stats">
                                <div class="signal-stat buy">
                                    <div class="stat-label">BUY SIGNALS</div>
                                    <div class="stat-value" id="buySignalsCount">0</div>
                                </div>
                                <div class="signal-stat sell">
                                    <div class="stat-label">SELL SIGNALS</div>
                                    <div class="stat-value" id="sellSignalsCount">0</div>
                                </div>
                                <div class="signal-stat short">
                                    <div class="stat-label">SHORT SIGNALS</div>
                                    <div class="stat-value" id="shortSignalsCount">0</div>
                                </div>
                                <div class="signal-stat cover">
                                    <div class="stat-label">COVER SIGNALS</div>
                                    <div class="stat-value" id="coverSignalsCount">0</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="signals-controls">
                            <h6>Chart Display Controls</h6>
                            <div class="control-buttons">
                                <button class="control-btn" onclick="window.chartIndicatorsModal.toggleDisplay('position')">
                                    <i class="fas fa-layer-group"></i> Position Panel
                                </button>
                                <button class="control-btn active" onclick="window.chartIndicatorsModal.toggleDisplay('buy')">
                                    <i class="fas fa-arrow-up"></i> Buy Signals
                                </button>
                                <button class="control-btn active" onclick="window.chartIndicatorsModal.toggleDisplay('short')">
                                    <i class="fas fa-arrow-down"></i> Short Signals
                                </button>
                            </div>
                        </div>
                        
                        <div class="signals-list-section">
                            <h6>Recent Signals</h6>
                            <div id="recentSignalsList" class="signals-list">
                                <p class="no-data">No signals detected yet. Signals will appear here when chart is loaded.</p>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="window.chartIndicatorsModal.closeSignalsModal()">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add modals to document
        const modalsContainer = document.createElement('div');
        modalsContainer.innerHTML = indicatorsModal + configureModal + signalsModal;
        document.body.appendChild(modalsContainer);
        
        // Add styles
        this.addStyles();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Render available indicators
        this.renderAvailableIndicators();
    }
    
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .indicators-tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                border-bottom: 2px solid #2d3748;
                padding-bottom: 10px;
            }
            
            .tab-btn {
                padding: 8px 16px;
                background: transparent;
                border: none;
                color: #a0aec0;
                cursor: pointer;
                border-radius: 4px;
                transition: all 0.2s;
            }
            
            .tab-btn:hover {
                background: #2d3748;
                color: #fff;
            }
            
            .tab-btn.active {
                background: #3b82f6;
                color: #fff;
            }
            
            .indicators-section {
                margin-bottom: 30px;
            }
            
            .indicators-section h6 {
                color: #e2e8f0;
                margin-bottom: 15px;
                font-size: 14px;
                font-weight: 600;
            }
            
            .indicators-list {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            
            .indicator-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 16px;
                background: #1a202c;
                border-radius: 8px;
                border-left: 4px solid;
            }
            
            .indicator-info {
                flex: 1;
            }
            
            .indicator-name {
                color: #e2e8f0;
                font-weight: 500;
                margin-bottom: 4px;
            }
            
            .indicator-params {
                color: #718096;
                font-size: 12px;
            }
            
            .indicator-actions {
                display: flex;
                gap: 8px;
            }
            
            .indicator-actions button {
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.2s;
            }
            
            .btn-edit {
                background: #3b82f6;
                color: white;
            }
            
            .btn-hide {
                background: #64748b;
                color: white;
            }
            
            .btn-remove {
                background: #ef4444;
                color: white;
            }
            
            .indicators-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 12px;
            }
            
            .available-indicator {
                padding: 16px;
                background: #1a202c;
                border-radius: 8px;
                border: 2px solid transparent;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .available-indicator:hover {
                border-color: #3b82f6;
                background: #2d3748;
            }
            
            .available-indicator-name {
                color: #e2e8f0;
                font-weight: 500;
                margin-bottom: 4px;
            }
            
            .available-indicator-params {
                color: #718096;
                font-size: 12px;
            }
            
            .color-picker {
                width: 60px;
                height: 40px;
                border: 2px solid #2d3748;
                border-radius: 4px;
                cursor: pointer;
            }
            
            .signals-summary {
                margin-bottom: 30px;
            }
            
            .signals-stats {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-top: 15px;
            }
            
            .signal-stat {
                padding: 20px;
                background: #1a202c;
                border-radius: 8px;
                border-left: 4px solid;
            }
            
            .signal-stat.buy {
                border-left-color: #10b981;
            }
            
            .signal-stat.sell {
                border-left-color: #ef4444;
            }
            
            .signal-stat.short {
                border-left-color: #f59e0b;
            }
            
            .signal-stat.cover {
                border-left-color: #3b82f6;
            }
            
            .stat-label {
                color: #9ca3af;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.5px;
                margin-bottom: 8px;
            }
            
            .stat-value {
                color: #e2e8f0;
                font-size: 32px;
                font-weight: 700;
            }
            
            .signals-controls {
                margin-bottom: 30px;
            }
            
            .control-buttons {
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }
            
            .control-btn {
                padding: 10px 20px;
                background: #2d3748;
                border: 2px solid #2d3748;
                color: #a0aec0;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .control-btn:hover {
                border-color: #3b82f6;
                color: #fff;
            }
            
            .control-btn.active {
                background: #10b981;
                border-color: #10b981;
                color: white;
            }
            
            .control-btn i {
                font-size: 14px;
            }
            
            .signals-list {
                max-height: 300px;
                overflow-y: auto;
            }
            
            .signal-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 16px;
                background: #1a202c;
                border-radius: 6px;
                margin-bottom: 8px;
                border-left: 4px solid;
            }
            
            .signal-item.buy {
                border-left-color: #10b981;
            }
            
            .signal-item.sell {
                border-left-color: #ef4444;
            }
            
            .signal-item.short {
                border-left-color: #f59e0b;
            }
            
            .signal-item.cover {
                border-left-color: #3b82f6;
            }
            
            .signal-time {
                color: #9ca3af;
                font-size: 12px;
            }
            
            .signal-type {
                color: #e2e8f0;
                font-weight: 600;
            }
            
            .signal-price {
                color: #3b82f6;
                font-weight: 500;
            }
            
            .no-data {
                color: #718096;
                text-align: center;
                padding: 40px 20px;
                font-style: italic;
            }
        `;
        document.head.appendChild(style);
    }
    
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.filterIndicators(e.target.dataset.tab);
            });
        });
        
        // Color picker sync
        const colorPicker = document.getElementById('indicatorColor');
        const colorHex = document.getElementById('indicatorColorHex');
        
        if (colorPicker && colorHex) {
            colorPicker.addEventListener('change', (e) => {
                colorHex.value = e.target.value;
            });
            
            colorHex.addEventListener('change', (e) => {
                colorPicker.value = e.target.value;
            });
        }
    }
    
    renderAvailableIndicators(filter = 'all') {
        const container = document.getElementById('availableIndicatorsList');
        container.innerHTML = '';
        
        Object.entries(this.availableIndicators).forEach(([key, indicator]) => {
            if (filter !== 'all' && indicator.category.toLowerCase() !== filter) {
                return;
            }
            
            const paramStr = Object.entries(indicator.defaultParams)
                .map(([k, v]) => `${k}: ${v}`)
                .join(', ');
            
            const div = document.createElement('div');
            div.className = 'available-indicator';
            div.innerHTML = `
                <div class="available-indicator-name">${indicator.displayName}</div>
                <div class="available-indicator-params">${paramStr}</div>
            `;
            div.onclick = () => this.openConfigureModal(key);
            container.appendChild(div);
        });
    }
    
    filterIndicators(category) {
        this.renderAvailableIndicators(category);
    }
    
    openIndicatorsModal() {
        document.getElementById('chartIndicatorsModal').style.display = 'flex';
        this.renderActiveIndicators();
    }
    
    closeIndicatorsModal() {
        document.getElementById('chartIndicatorsModal').style.display = 'none';
    }
    
    openConfigureModal(indicatorType, existingIndicator = null) {
        const modal = document.getElementById('configureIndicatorModal');
        const indicator = this.availableIndicators[indicatorType];
        
        document.getElementById('indicatorType').value = indicatorType;
        document.getElementById('indicatorDisplayName').value = existingIndicator?.displayName || indicator.displayName;
        document.getElementById('indicatorColor').value = existingIndicator?.color || indicator.color;
        document.getElementById('indicatorColorHex').value = existingIndicator?.color || indicator.color;
        document.getElementById('indicatorLineWidth').value = existingIndicator?.lineWidth || 2;
        
        // Render parameters
        const paramsContainer = document.getElementById('indicatorParams');
        paramsContainer.innerHTML = '';
        
        const params = existingIndicator?.params || indicator.defaultParams;
        Object.entries(params).forEach(([key, value]) => {
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';
            formGroup.innerHTML = `
                <label>${this.formatParamName(key)}</label>
                <input type="number" id="param_${key}" class="form-control" value="${value}">
            `;
            paramsContainer.appendChild(formGroup);
        });
        
        document.getElementById('saveIndicatorBtnText').textContent = existingIndicator ? 'Update' : 'Add to Chart';
        modal.dataset.indicatorId = existingIndicator?.id || '';
        modal.style.display = 'flex';
    }
    
    closeConfigureModal() {
        document.getElementById('configureIndicatorModal').style.display = 'none';
    }
    
    formatParamName(name) {
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    saveIndicator() {
        const modal = document.getElementById('configureIndicatorModal');
        const indicatorType = document.getElementById('indicatorType').value;
        const indicator = this.availableIndicators[indicatorType];
        
        const config = {
            id: modal.dataset.indicatorId || `ind_${Date.now()}`,
            type: indicatorType,
            displayName: document.getElementById('indicatorDisplayName').value,
            color: document.getElementById('indicatorColor').value,
            lineWidth: parseInt(document.getElementById('indicatorLineWidth').value),
            params: {}
        };
        
        // Get parameters
        Object.keys(indicator.defaultParams).forEach(key => {
            const input = document.getElementById(`param_${key}`);
            if (input) {
                config.params[key] = parseFloat(input.value);
            }
        });
        
        // Add or update indicator
        this.indicators.set(config.id, config);
        
        // Save to localStorage
        this.saveIndicatorsToStorage();
        
        // Calculate and draw indicator
        this.calculateAndDrawIndicator(config);
        
        this.closeConfigureModal();
        this.renderActiveIndicators();
    }
    
    calculateAndDrawIndicator(config) {
        console.log('🎨 Drawing indicator:', config);
        
        // Remove existing series if updating
        const existingSeries = this.indicatorSeries.get(config.id);
        if (existingSeries && this.chart) {
            console.log('Removing existing series for', config.id);
            this.chart.removeSeries(existingSeries);
            this.indicatorSeries.delete(config.id);
        }
        
        // Get chart candlestick data
        let chartData = [];
        let dataSource = 'unknown';
        
        // Try to get data from different chart instances
        if (window.chartManual && window.chartManual.candlestickSeries) {
            try {
                const data = window.chartManual.candlestickSeries.data();
                if (data && data.length > 0) {
                    chartData = data;
                    dataSource = 'chartManual.candlestickSeries';
                }
            } catch (e) {
                console.warn('Cannot get data from chartManual:', e);
            }
        }
        
        if (chartData.length === 0 && window.chartBot && window.chartBot.candlestickSeries) {
            try {
                const data = window.chartBot.candlestickSeries.data();
                if (data && data.length > 0) {
                    chartData = data;
                    dataSource = 'chartBot.candlestickSeries';
                }
            } catch (e) {
                console.warn('Cannot get data from chartBot:', e);
            }
        }
        
        if (chartData.length === 0 && window.chartStrategy && window.chartStrategy.candlestickSeries) {
            try {
                const data = window.chartStrategy.candlestickSeries.data();
                if (data && data.length > 0) {
                    chartData = data;
                    dataSource = 'chartStrategy.candlestickSeries';
                }
            } catch (e) {
                console.warn('Cannot get data from chartStrategy:', e);
            }
        }
        
        // Also try to get from UploadDataManager
        if (chartData.length === 0 && window.UploadDataManager && window.UploadDataManager.csvData) {
            console.log('Getting data from UploadDataManager');
            try {
                const csvData = window.UploadDataManager.csvData;
                chartData = csvData.map(bar => ({
                    time: Math.floor(new Date(`${bar.date}T${bar.time}`).getTime() / 1000),
                    open: parseFloat(bar.open),
                    high: parseFloat(bar.high),
                    low: parseFloat(bar.low),
                    close: parseFloat(bar.close),
                    volume: parseFloat(bar.volume || 0)
                }));
                dataSource = 'UploadDataManager';
            } catch (e) {
                console.error('Error getting data from UploadDataManager:', e);
            }
        }
        
        if (chartData.length === 0) {
            console.error('❌ No chart data available to calculate indicator');
            alert('Không có dữ liệu chart để tính indicator. Vui lòng upload file CSV hoặc kết nối data feed.');
            return;
        }
        
        console.log('✅ Chart data loaded from:', dataSource, '- Length:', chartData.length);
        console.log('Sample data point:', chartData[0]);
        
        // Calculate indicator based on type
        let indicatorData = [];
        
        switch (config.type) {
            case 'EMA':
                indicatorData = this.calculateEMA(chartData, config.params.length);
                break;
            case 'SMA':
                indicatorData = this.calculateSMA(chartData, config.params.length);
                break;
            case 'WMA':
                indicatorData = this.calculateWMA(chartData, config.params.length);
                break;
            case 'DEMA':
                indicatorData = this.calculateDEMA(chartData, config.params.length);
                break;
            case 'TEMA':
                indicatorData = this.calculateTEMA(chartData, config.params.length);
                break;
            case 'RSI':
                indicatorData = this.calculateRSI(chartData, config.params.length);
                break;
            case 'MFI':
                indicatorData = this.calculateMFI(chartData, config.params.length);
                break;
            case 'MACD':
                indicatorData = this.calculateMACD(chartData, config.params);
                break;
            case 'BB':
                indicatorData = this.calculateBollingerBands(chartData, config.params);
                break;
            default:
                console.warn('Indicator type not implemented:', config.type);
                return;
        }
        
        console.log('Calculated', config.type, 'data points:', indicatorData.length);
        
        if (indicatorData.length === 0) {
            console.warn('No indicator data calculated');
            return;
        }
        
        // Create line series on chart
        const lineSeries = this.chart.addLineSeries({
            color: config.color,
            lineWidth: config.lineWidth,
            title: config.displayName,
            priceScaleId: 'right',
            lastValueVisible: true,
            priceLineVisible: false
        });
        
        lineSeries.setData(indicatorData);
        this.indicatorSeries.set(config.id, lineSeries);
        
        console.log('✅ Indicator drawn successfully:', config.displayName);
    }
    
    calculateEMA(chartData, period) {
        if (chartData.length < period) return [];
        
        const result = [];
        const multiplier = 2 / (period + 1);
        
        // Calculate initial SMA for first EMA value
        let sum = 0;
        for (let i = 0; i < period; i++) {
            sum += chartData[i].close;
        }
        let ema = sum / period;
        
        result.push({
            time: chartData[period - 1].time,
            value: ema
        });
        
        // Calculate EMA for remaining values
        for (let i = period; i < chartData.length; i++) {
            ema = (chartData[i].close - ema) * multiplier + ema;
            result.push({
                time: chartData[i].time,
                value: ema
            });
        }
        
        return result;
    }
    
    calculateSMA(chartData, period) {
        if (chartData.length < period) return [];
        
        const result = [];
        
        for (let i = period - 1; i < chartData.length; i++) {
            let sum = 0;
            for (let j = 0; j < period; j++) {
                sum += chartData[i - j].close;
            }
            result.push({
                time: chartData[i].time,
                value: sum / period
            });
        }
        
        return result;
    }
    
    calculateWMA(chartData, period) {
        if (chartData.length < period) return [];
        
        const result = [];
        const weights = Array.from({length: period}, (_, i) => i + 1);
        const weightSum = weights.reduce((a, b) => a + b, 0);
        
        for (let i = period - 1; i < chartData.length; i++) {
            let sum = 0;
            for (let j = 0; j < period; j++) {
                sum += chartData[i - j].close * weights[period - 1 - j];
            }
            result.push({
                time: chartData[i].time,
                value: sum / weightSum
            });
        }
        
        return result;
    }
    
    calculateDEMA(chartData, period) {
        if (chartData.length < period * 2) return [];
        
        // Calculate first EMA
        const ema1 = this.calculateEMA(chartData, period);
        
        // Calculate EMA of EMA
        const ema2 = this.calculateEMAFromValues(ema1.map(d => d.value), period);
        
        // DEMA = 2 * EMA - EMA(EMA)
        const result = [];
        const startIdx = Math.max(0, ema1.length - ema2.length);
        
        for (let i = 0; i < ema2.length; i++) {
            const ema1Val = ema1[startIdx + i].value;
            const ema2Val = ema2[i];
            result.push({
                time: ema1[startIdx + i].time,
                value: 2 * ema1Val - ema2Val
            });
        }
        
        return result;
    }
    
    calculateTEMA(chartData, period) {
        if (chartData.length < period * 3) return [];
        
        // Calculate first EMA
        const ema1 = this.calculateEMA(chartData, period);
        
        // Calculate EMA of EMA
        const ema2 = this.calculateEMAFromValues(ema1.map(d => d.value), period);
        
        // Calculate EMA of EMA of EMA
        const ema3 = this.calculateEMAFromValues(ema2, period);
        
        // TEMA = 3 * EMA - 3 * EMA(EMA) + EMA(EMA(EMA))
        const result = [];
        const minLength = Math.min(ema1.length, ema2.length, ema3.length);
        const start1 = ema1.length - minLength;
        const start2 = ema2.length - minLength;
        
        for (let i = 0; i < ema3.length; i++) {
            const ema1Val = ema1[start1 + i].value;
            const ema2Val = ema2[start2 + i];
            const ema3Val = ema3[i];
            result.push({
                time: ema1[start1 + i].time,
                value: 3 * ema1Val - 3 * ema2Val + ema3Val
            });
        }
        
        return result;
    }
    
    calculateEMAFromValues(values, period) {
        if (values.length < period) return [];
        
        const result = [];
        const multiplier = 2 / (period + 1);
        
        // Calculate initial SMA
        let sum = 0;
        for (let i = 0; i < period; i++) {
            sum += values[i];
        }
        let ema = sum / period;
        result.push(ema);
        
        // Calculate EMA for remaining values
        for (let i = period; i < values.length; i++) {
            ema = (values[i] - ema) * multiplier + ema;
            result.push(ema);
        }
        
        return result;
    }
    
    calculateRSI(chartData, period) {
        if (chartData.length < period + 1) return [];
        
        const result = [];
        let gains = [];
        let losses = [];
        
        // Calculate initial average gain and loss
        for (let i = 1; i <= period; i++) {
            const change = chartData[i].close - chartData[i - 1].close;
            if (change > 0) {
                gains.push(change);
                losses.push(0);
            } else {
                gains.push(0);
                losses.push(Math.abs(change));
            }
        }
        
        let avgGain = gains.reduce((a, b) => a + b, 0) / period;
        let avgLoss = losses.reduce((a, b) => a + b, 0) / period;
        
        let rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
        let rsi = 100 - (100 / (1 + rs));
        
        result.push({
            time: chartData[period].time,
            value: rsi
        });
        
        // Calculate RSI for remaining values
        for (let i = period + 1; i < chartData.length; i++) {
            const change = chartData[i].close - chartData[i - 1].close;
            const gain = change > 0 ? change : 0;
            const loss = change < 0 ? Math.abs(change) : 0;
            
            avgGain = ((avgGain * (period - 1)) + gain) / period;
            avgLoss = ((avgLoss * (period - 1)) + loss) / period;
            
            rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
            rsi = 100 - (100 / (1 + rs));
            
            result.push({
                time: chartData[i].time,
                value: rsi
            });
        }
        
        return result;
    }
    
    calculateMFI(chartData, period) {
        if (chartData.length < period + 1) return [];
        
        const result = [];
        
        for (let i = period; i < chartData.length; i++) {
            let positiveFlow = 0;
            let negativeFlow = 0;
            
            for (let j = 0; j < period; j++) {
                const idx = i - j;
                const typicalPrice = (chartData[idx].high + chartData[idx].low + chartData[idx].close) / 3;
                const prevTypicalPrice = (chartData[idx - 1].high + chartData[idx - 1].low + chartData[idx - 1].close) / 3;
                const moneyFlow = typicalPrice * (chartData[idx].volume || 1000);
                
                if (typicalPrice > prevTypicalPrice) {
                    positiveFlow += moneyFlow;
                } else if (typicalPrice < prevTypicalPrice) {
                    negativeFlow += moneyFlow;
                }
            }
            
            const moneyFlowRatio = negativeFlow === 0 ? 100 : positiveFlow / negativeFlow;
            const mfi = 100 - (100 / (1 + moneyFlowRatio));
            
            result.push({
                time: chartData[i].time,
                value: mfi
            });
        }
        
        return result;
    }
    
    calculateMACD(chartData, params) {
        const fastPeriod = params.fast || 12;
        const slowPeriod = params.slow || 26;
        const signalPeriod = params.signal || 9;
        
        if (chartData.length < slowPeriod) return [];
        
        // Calculate fast and slow EMA
        const fastEMA = this.calculateEMA(chartData, fastPeriod);
        const slowEMA = this.calculateEMA(chartData, slowPeriod);
        
        // Calculate MACD line
        const macdLine = [];
        const startIdx = slowEMA.length - fastEMA.length;
        
        for (let i = 0; i < slowEMA.length; i++) {
            macdLine.push({
                time: slowEMA[i].time,
                value: fastEMA[startIdx + i].value - slowEMA[i].value
            });
        }
        
        // Calculate signal line (EMA of MACD)
        const signalValues = this.calculateEMAFromValues(macdLine.map(d => d.value), signalPeriod);
        
        // Return MACD line
        const result = [];
        const signalStart = macdLine.length - signalValues.length;
        
        for (let i = 0; i < signalValues.length; i++) {
            result.push({
                time: macdLine[signalStart + i].time,
                value: macdLine[signalStart + i].value
            });
        }
        
        return result;
    }
    
    calculateBollingerBands(chartData, params) {
        const period = params.length || 20;
        const stdDev = params.stdDev || 2;
        
        if (chartData.length < period) return [];
        
        const result = [];
        const sma = this.calculateSMA(chartData, period);
        
        for (let i = 0; i < sma.length; i++) {
            const dataIdx = period - 1 + i;
            
            // Calculate standard deviation
            let sumSquares = 0;
            for (let j = 0; j < period; j++) {
                const diff = chartData[dataIdx - j].close - sma[i].value;
                sumSquares += diff * diff;
            }
            const std = Math.sqrt(sumSquares / period);
            
            result.push({
                time: sma[i].time,
                value: sma[i].value + (stdDev * std) // Upper band
            });
        }
        
        return result;
    }
    
    renderActiveIndicators() {
        const container = document.getElementById('activeIndicatorsList');
        
        if (this.indicators.size === 0) {
            container.innerHTML = '<p class="no-data">No indicators added yet</p>';
            return;
        }
        
        container.innerHTML = '';
        this.indicators.forEach((indicator, id) => {
            const paramStr = Object.entries(indicator.params)
                .map(([k, v]) => `${k}: ${v}`)
                .join(', ');
            
            const div = document.createElement('div');
            div.className = 'indicator-item';
            div.style.borderLeftColor = indicator.color;
            div.innerHTML = `
                <div class="indicator-info">
                    <div class="indicator-name">${indicator.displayName}</div>
                    <div class="indicator-params">${paramStr}</div>
                </div>
                <div class="indicator-actions">
                    <button class="btn-edit" onclick="window.chartIndicatorsModal.editIndicator('${id}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn-hide" onclick="window.chartIndicatorsModal.toggleIndicator('${id}')">
                        <i class="fas fa-eye"></i> Hide
                    </button>
                    <button class="btn-remove" onclick="window.chartIndicatorsModal.removeIndicator('${id}')">
                        <i class="fas fa-times"></i> Remove
                    </button>
                </div>
            `;
            container.appendChild(div);
        });
    }
    
    editIndicator(id) {
        const indicator = this.indicators.get(id);
        if (indicator) {
            this.openConfigureModal(indicator.type, indicator);
        }
    }
    
    toggleIndicator(id) {
        // Toggle indicator visibility
        console.log('Toggle indicator:', id);
    }
    
    removeIndicator(id) {
        if (confirm('Remove this indicator from chart?')) {
            this.indicators.delete(id);
            
            // Remove from chart
            const series = this.indicatorSeries.get(id);
            if (series && this.chart) {
                this.chart.removeSeries(series);
            }
            this.indicatorSeries.delete(id);
            
            // Save to localStorage
            this.saveIndicatorsToStorage();
            
            this.renderActiveIndicators();
        }
    }
    
    openSignalsModal() {
        document.getElementById('chartSignalsModal').style.display = 'flex';
        this.updateSignalsCounts();
        this.renderRecentSignals();
    }
    
    closeSignalsModal() {
        document.getElementById('chartSignalsModal').style.display = 'none';
    }
    
    updateSignalsCounts() {
        document.getElementById('buySignalsCount').textContent = this.signals.buy.length;
        document.getElementById('sellSignalsCount').textContent = this.signals.sell.length;
        document.getElementById('shortSignalsCount').textContent = this.signals.short.length;
        document.getElementById('coverSignalsCount').textContent = this.signals.cover.length;
    }
    
    renderRecentSignals() {
        const container = document.getElementById('recentSignalsList');
        const allSignals = [
            ...this.signals.buy.map(s => ({...s, type: 'buy'})),
            ...this.signals.sell.map(s => ({...s, type: 'sell'})),
            ...this.signals.short.map(s => ({...s, type: 'short'})),
            ...this.signals.cover.map(s => ({...s, type: 'cover'}))
        ].sort((a, b) => b.time - a.time).slice(0, 20);
        
        if (allSignals.length === 0) {
            container.innerHTML = '<p class="no-data">No signals detected yet. Signals will appear here when chart is loaded.</p>';
            return;
        }
        
        container.innerHTML = allSignals.map(signal => `
            <div class="signal-item ${signal.type}">
                <div>
                    <div class="signal-type">${signal.type.toUpperCase()}</div>
                    <div class="signal-time">${new Date(signal.time * 1000).toLocaleString()}</div>
                </div>
                <div class="signal-price">${signal.price.toFixed(2)}</div>
            </div>
        `).join('');
    }
    
    toggleDisplay(type) {
        const btn = event.target.closest('.control-btn');
        btn.classList.toggle('active');
        console.log('Toggle display:', type);
    }
    
    addSignal(type, time, price) {
        this.signals[type].push({ time, price });
        this.updateSignalsCounts();
    }
    
    // ========== LOCAL STORAGE METHODS ==========
    
    getStorageKey() {
        return `chartIndicators_${this.chartType}`;
    }
    
    saveIndicatorsToStorage() {
        try {
            // Convert Map to array for JSON serialization
            const indicatorsArray = Array.from(this.indicators.entries());
            localStorage.setItem(this.getStorageKey(), JSON.stringify(indicatorsArray));
            console.log(`✅ Saved ${indicatorsArray.length} indicators for ${this.chartType} chart`);
        } catch (error) {
            console.error('Error saving indicators:', error);
        }
    }
    
    loadIndicatorsFromStorage() {
        try {
            const stored = localStorage.getItem(this.getStorageKey());
            if (stored) {
                const indicatorsArray = JSON.parse(stored);
                this.indicators = new Map(indicatorsArray);
                console.log(`📂 Loaded ${this.indicators.size} indicators for ${this.chartType} chart`);
                
                // Redraw indicators after chart data is loaded
                setTimeout(() => {
                    this.redrawAllIndicators();
                }, 1000);
            }
        } catch (error) {
            console.error('Error loading indicators:', error);
        }
    }
    
    redrawAllIndicators() {
        console.log('🔄 Redrawing all saved indicators...');
        this.indicators.forEach((config, id) => {
            this.calculateAndDrawIndicator(config);
        });
    }
    
    clearStoredIndicators() {
        localStorage.removeItem(this.getStorageKey());
        console.log(`🗑️ Cleared stored indicators for ${this.chartType} chart`);
    }
}

// Make it globally accessible
window.ChartIndicatorsModal = ChartIndicatorsModal;
