// Chart Manager for Strategy Builder Page (Offline only - no ConnectionManager)
class ChartStrategy {
    constructor(containerId) {
        this.containerId = containerId;
        this.chart = null;
        this.candlestickSeries = null;
        this.volumeSeries = null;
        this.currentSymbol = 'VN30F1M';
        this.currentTimeframe = '1m';
        this.utcOffset = 7; // UTC+7 default
        this.showVolume = true;
        this.volumeScaleHeight = 0.2;
        
        // Current price data
        this.currentData = {
            open: 0,
            high: 0,
            low: 0,
            close: 0,
            volume: 0,
            position: 'FLAT'
        };
        
        // Strategy signals for backtesting visualization
        this.signals = [];
    }
    
    init() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error('Chart container not found');
            return;
        }
        
        // Create chart (same as manual)
        this.chart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: container.clientHeight,
            layout: {
                background: { color: '#141824' },
                textColor: '#a0a0a0',
            },
            grid: {
                vertLines: { color: '#1a1f2e' },
                horzLines: { color: '#1a1f2e' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            leftPriceScale: {
                visible: true,
                borderColor: '#2d3748',
            },
            rightPriceScale: {
                borderColor: '#2d3748',
            },
            timeScale: {
                borderColor: '#2d3748',
                timeVisible: true,
                secondsVisible: false,
            },
            localization: {
                timeFormatter: (time) => {
                    // Convert to UTC+offset time for display
                    const date = new Date(time * 1000);
                    const utcTime = date.getTime() + (this.utcOffset * 3600 * 1000);
                    const displayDate = new Date(utcTime);
                    
                    const hours = displayDate.getUTCHours().toString().padStart(2, '0');
                    const minutes = displayDate.getUTCMinutes().toString().padStart(2, '0');
                    return `${hours}:${minutes}`;
                }
            }
        });
        
        // Create candlestick series
        this.candlestickSeries = this.chart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#ef4444',
            borderUpColor: '#10b981',
            borderDownColor: '#ef4444',
            wickUpColor: '#10b981',
            wickDownColor: '#ef4444',
            priceScaleId: 'right',
        });
        
        // Create volume series
        this.createVolumeSeries();
        
        // Setup handlers
        window.addEventListener('resize', () => this.handleResize());
        this.setupTimeframeButtons();
        this.setupVolumeScaleDrag();
        this.setupUTCSelector();
        this.setupVolumeToggle();
        this.chart.subscribeCrosshairMove(this.handleCrosshairMove.bind(this));
        
        // Initialize indicators modal
        this.indicatorsModal = new ChartIndicatorsModal(this.chart, 'strategy');
        window.chartIndicatorsModal = this.indicatorsModal;
        
        // Load uploaded data if available first
        this.checkAndLoadUploadedData();
        
        // Load initial data after delay (to allow upload check)
        setTimeout(() => {
            this.loadChartData();
        }, 600);
    }
    
    checkAndLoadUploadedData() {
        setTimeout(() => {
            if (window.UploadDataManager && window.UploadDataManager.csvData) {
                window.UploadDataManager.loadToChart();
            }
        }, 500);
    }
    
    loadUploadedData(chartData, volumeData, metadata) {
        console.log('=== Strategy: loadUploadedData called ===');
        console.log('Chart data:', chartData ? chartData.length : 0, 'bars');
        
        if (!chartData || chartData.length === 0) {
            console.warn('No data to load');
            return;
        }
        
        console.log('Loading uploaded data to strategy chart:', chartData.length, 'bars');
        
        // Clear existing data first
        console.log('Clearing existing data...');
        this.candlestickSeries.setData([]);
        if (this.volumeSeries) {
            this.volumeSeries.setData([]);
        }
        
        // Set new data
        console.log('Setting new data...');
        this.candlestickSeries.setData(chartData);
        
        if (this.volumeSeries && volumeData) {
            this.volumeSeries.setData(volumeData);
        }
        
        console.log('Fitting content...');
        this.chart.timeScale().fitContent();
        
        const lastBar = chartData[chartData.length - 1];
        console.log('Updating OHLCV with last bar:', lastBar);
        this.updateOHLCV(lastBar, metadata ? metadata.lastBar : null);
        
        console.log('=== Strategy: loadUploadedData completed ===');
    }
    
    updateOHLCV(bar, csvBar) {
        // Update date and time if available
        if (csvBar) {
            const dateEl = document.getElementById('price-date');
            const timeEl = document.getElementById('price-time');
            if (dateEl) dateEl.textContent = csvBar.date;
            if (timeEl) timeEl.textContent = csvBar.time;
        }
        
        document.getElementById('price-open').textContent = bar.open.toFixed(2);
        document.getElementById('price-high').textContent = bar.high.toFixed(2);
        document.getElementById('price-low').textContent = bar.low.toFixed(2);
        document.getElementById('price-close').textContent = bar.close.toFixed(2);
        
        const volEl = document.getElementById('price-volume');
        if (volEl && csvBar) {
            volEl.textContent = csvBar.volume.toLocaleString();
        }
    }
    
    clearChart() {
        this.candlestickSeries.setData([]);
        if (this.volumeSeries) {
            this.volumeSeries.setData([]);
        }
    }
    
    createVolumeSeries() {
        if (this.volumeSeries) {
            this.chart.removeSeries(this.volumeSeries);
        }
        
        // FIX: Volume scale - đáy cố định bottom=0, top thay đổi
        this.volumeSeries = this.chart.addHistogramSeries({
            color: '#3b82f6',
            priceFormat: {
                type: 'volume',
            },
            priceScaleId: 'left',
            scaleMargins: {
                top: 1 - this.volumeScaleHeight, // Top thay đổi
                bottom: 0, // Đáy cố định tại y=0
            },
        });
        
        // Configure left price scale - DISABLE interaction để tránh kéo sai
        this.chart.priceScale('left').applyOptions({
            scaleMargins: {
                top: 1 - this.volumeScaleHeight,
                bottom: 0,
            },
            // Disable mouse interaction on left scale
            visible: true,
        });
        
        // Override CSS to prevent dragging left scale
        this.addLeftScaleProtection();
    }
    
    addLeftScaleProtection() {
        const container = document.getElementById(this.containerId);
        if (!container) return;
        
        // Add CSS to disable pointer events on left scale
        const style = document.createElement('style');
        style.textContent = `
            #${this.containerId} .tv-lightweight-charts table tr td:first-child {
                pointer-events: none !important;
            }
        `;
        if (!document.getElementById('volume-scale-protection')) {
            style.id = 'volume-scale-protection';
            document.head.appendChild(style);
        }
    }
    
    setupTimeframeButtons() {
        const buttons = document.querySelectorAll('.timeframe-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                buttons.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                
                // FIX: Lấy timeframe từ data-timeframe attribute
                const timeframe = e.target.getAttribute('data-timeframe') || e.target.textContent.toLowerCase();
                this.currentTimeframe = timeframe;
                this.changeTimeframe(timeframe);
            });
        });
        
        // Setup navigation buttons
        this.setupNavigationButtons();
    }
    
    setupNavigationButtons() {
        const navButtons = document.querySelectorAll('.chart-zoom-buttons button');
        if (navButtons.length >= 2) {
            // Button 0: Previous (◀)
            navButtons[0].addEventListener('click', () => {
                this.navigateChart(-1);
            });
            
            // Button 1: Next (▶)
            navButtons[1].addEventListener('click', () => {
                this.navigateChart(1);
            });
        }
    }
    
    // FIX: Timeframe navigation - nhảy đúng theo timeframe
    navigateChart(direction) {
        const timeframeSeconds = this.getTimeframeSeconds();
        const timeScale = this.chart.timeScale();
        const logicalRange = timeScale.getVisibleLogicalRange();
        
        if (logicalRange) {
            // Tính số bars hiện tại đang hiển thị
            const visibleBars = logicalRange.to - logicalRange.from;
            
            // Nhảy 1 khoảng bằng số bars hiện tại
            const offset = direction * visibleBars;
            
            timeScale.setVisibleLogicalRange({
                from: logicalRange.from + offset,
                to: logicalRange.to + offset
            });
        }
    }
    
    getTimeframeSeconds() {
        const timeframeMap = {
            'tick': 1,
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '30m': 1800,
            '4h': 14400,
            '1d': 86400
        };
        
        return timeframeMap[this.currentTimeframe] || 60;
    }
    
    changeTimeframe(timeframe) {
        console.log('Changing timeframe to:', timeframe);
        
        // Update badge
        const badge = document.querySelector('.symbol-timeframe');
        if (badge) {
            badge.textContent = timeframe.toUpperCase();
        }
        
        // Reload chart data for new timeframe
        this.loadChartData();
        
        // Fit content
        this.chart.timeScale().fitContent();
    }
    
    setupVolumeScaleDrag() {
        // DISABLED - Volume scale drag removed to prevent errors
        // Volume height is fixed at 20%
        return;
    }
    
    setupUTCSelector() {
        const utcSelector = document.getElementById('utc-selector');
        if (utcSelector) {
            utcSelector.addEventListener('change', (e) => {
                this.utcOffset = parseInt(e.target.value);
                this.updateClockDisplay();
                this.chart.applyOptions({
                    localization: {
                        timeFormatter: (time) => {
                            const date = new Date(time * 1000);
                            return this.formatTimeWithUTC(date);
                        }
                    }
                });
            });
        }
        
        // Update clock every second
        this.updateClockDisplay();
        setInterval(() => this.updateClockDisplay(), 1000);
    }
    
    updateClockDisplay() {
        const clockEl = document.getElementById('chart-time');
        if (clockEl) {
            const now = new Date();
            const utcTime = now.getTime() + (this.utcOffset * 3600 * 1000);
            const adjustedDate = new Date(utcTime);
            
            const hours = String(adjustedDate.getUTCHours()).padStart(2, '0');
            const minutes = String(adjustedDate.getUTCMinutes()).padStart(2, '0');
            const seconds = String(adjustedDate.getUTCSeconds()).padStart(2, '0');
            
            const utcSign = this.utcOffset >= 0 ? '+' : '';
            clockEl.textContent = `${hours}:${minutes}:${seconds} (UTC${utcSign}${this.utcOffset})`;
        }
    }
    
    setupVolumeToggle() {
        const volumeToggle = document.querySelector('.volume-toggle');
        if (volumeToggle) {
            volumeToggle.addEventListener('change', (e) => {
                this.showVolume = e.target.checked;
                this.toggleVolume();
            });
        }
    }
    
    formatTimeWithUTC(date) {
        const hours = date.getUTCHours() + this.utcOffset;
        const minutes = date.getUTCMinutes();
        const seconds = date.getUTCSeconds();
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    handleCrosshairMove(param) {
        if (!param.time || !param.seriesData) return;
        
        const data = param.seriesData.get(this.candlestickSeries);
        if (data) {
            this.currentData.open = data.open;
            this.currentData.high = data.high;
            this.currentData.low = data.low;
            this.currentData.close = data.close;
            
            const volumeData = param.seriesData.get(this.volumeSeries);
            if (volumeData) {
                this.currentData.volume = volumeData.value;
            }
            
            // Update date and time display with UTC offset
            const date = new Date(param.time * 1000);
            
            // Apply UTC offset
            const utcTime = date.getTime() + (this.utcOffset * 3600 * 1000);
            const adjustedDate = new Date(utcTime);
            
            const dateStr = adjustedDate.getUTCFullYear() + '-' + 
                           String(adjustedDate.getUTCMonth() + 1).padStart(2, '0') + '-' + 
                           String(adjustedDate.getUTCDate()).padStart(2, '0');
            const timeStr = String(adjustedDate.getUTCHours()).padStart(2, '0') + ':' + 
                           String(adjustedDate.getUTCMinutes()).padStart(2, '0');
            
            const dateEl = document.getElementById('price-date');
            const timeEl = document.getElementById('price-time');
            if (dateEl) dateEl.textContent = dateStr;
            if (timeEl) timeEl.textContent = timeStr;
            
            this.updateOHLCVDisplay();
        }
    }
    
    updateOHLCVDisplay() {
        const elements = {
            open: document.getElementById('price-open'),
            high: document.getElementById('price-high'),
            low: document.getElementById('price-low'),
            close: document.getElementById('price-close'),
            volume: document.getElementById('price-volume'),
            position: document.getElementById('price-position')
        };
        
        if (elements.open) elements.open.textContent = this.currentData.open.toFixed(2);
        if (elements.high) elements.high.textContent = this.currentData.high.toFixed(2);
        if (elements.low) elements.low.textContent = this.currentData.low.toFixed(2);
        if (elements.close) elements.close.textContent = this.currentData.close.toFixed(2);
        if (elements.volume) elements.volume.textContent = this.formatVolume(this.currentData.volume);
        if (elements.position) {
            elements.position.textContent = this.currentData.position;
            elements.position.className = 'position-display position-' + this.currentData.position.toLowerCase();
        }
    }
    
    formatVolume(volume) {
        if (volume >= 1000000) {
            return (volume / 1000000).toFixed(2) + 'M';
        } else if (volume >= 1000) {
            return (volume / 1000).toFixed(2) + 'K';
        }
        return volume.toFixed(0);
    }
    
    async loadChartData() {
        try {
            // Check if uploaded data exists and load it immediately
            if (window.UploadDataManager && window.UploadDataManager.csvData && window.UploadDataManager.csvData.length > 0) {
                console.log('✅ Found uploaded data:', window.UploadDataManager.csvData.length, 'bars');
                console.log('Loading uploaded data to chart...');
                
                // Convert CSV data to chart format
                const chartData = [];
                const volumeData = [];
                
                for (let i = 0; i < window.UploadDataManager.csvData.length; i++) {
                    const bar = window.UploadDataManager.csvData[i];
                    const csvUtcOffset = window.UploadDataManager.fileInfo?.csvUtc || 7;
                    
                    const dateParts = bar.date.split('-');
                    const timeParts = bar.time.split(':');
                    
                    const year = parseInt(dateParts[0]);
                    const month = parseInt(dateParts[1]) - 1;
                    const day = parseInt(dateParts[2]);
                    const hour = parseInt(timeParts[0]);
                    const minute = parseInt(timeParts[1]);
                    const second = parseInt(timeParts[2] || 0);
                    
                    const csvTimestamp = Date.UTC(year, month, day, hour, minute, second);
                    const utcTimestamp = csvTimestamp - (csvUtcOffset * 3600 * 1000);
                    const timestamp = Math.floor(utcTimestamp / 1000);
                    
                    chartData.push({
                        time: timestamp,
                        open: parseFloat(bar.open),
                        high: parseFloat(bar.high),
                        low: parseFloat(bar.low),
                        close: parseFloat(bar.close)
                    });
                    
                    volumeData.push({
                        time: timestamp,
                        value: parseFloat(bar.volume || 0),
                        color: bar.close >= bar.open ? '#10b98180' : '#ef444480'
                    });
                }
                
                console.log('Setting chart data:', chartData.length, 'bars');
                this.candlestickSeries.setData(chartData);
                if (this.volumeSeries) {
                    this.volumeSeries.setData(volumeData);
                }
                
                // Update OHLCV with last bar
                if (chartData.length > 0) {
                    const lastBar = chartData[chartData.length - 1];
                    this.currentData.open = lastBar.open;
                    this.currentData.high = lastBar.high;
                    this.currentData.low = lastBar.low;
                    this.currentData.close = lastBar.close;
                    if (volumeData.length > 0) {
                        this.currentData.volume = volumeData[volumeData.length - 1].value;
                    }
                    this.updateOHLCVDisplay();
                }
                
                this.chart.timeScale().fitContent();
                console.log('✅ Chart loaded successfully');
                return;
            }
            
            // No data available - leave chart empty
            console.log('ℹ️ No data available. Please upload CSV or connect to data feed.');
            this.candlestickSeries.setData([]);
            if (this.volumeSeries) {
                this.volumeSeries.setData([]);
            }
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
    }
    
    generateMockData(count) {
    }
    
    generateMockData(count) {
        const candles = [];
        const volumes = [];
        const basePrice = 1900;
        let currentPrice = basePrice;
        const now = Math.floor(Date.now() / 1000);
        
        const interval = this.getTimeframeSeconds();
        
        for (let i = 0; i < count; i++) {
            const time = now - (count - i) * interval;
            const change = (Math.random() - 0.5) * 10;
            currentPrice += change;
            
            const open = currentPrice;
            const close = currentPrice + (Math.random() - 0.5) * 5;
            const high = Math.max(open, close) + Math.random() * 3;
            const low = Math.min(open, close) - Math.random() * 3;
            
            candles.push({
                time: time,
                open: parseFloat(open.toFixed(2)),
                high: parseFloat(high.toFixed(2)),
                low: parseFloat(low.toFixed(2)),
                close: parseFloat(close.toFixed(2)),
            });
            
            volumes.push({
                time: time,
                value: Math.floor(Math.random() * 10000) + 1000,
                color: close > open ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)',
            });
            
            currentPrice = close;
        }
        
        return { candles, volumes };
    }
    
    changeSymbol(symbol) {
        this.currentSymbol = symbol;
        this.loadChartData();
        this.updateSymbolInfo();
    }
    
    updateSymbolInfo() {
        const symbolElement = document.querySelector('.symbol-name');
        if (symbolElement) {
            symbolElement.textContent = this.currentSymbol;
        }
    }
    
    toggleVolume() {
        if (this.showVolume && !this.volumeSeries) {
            this.createVolumeSeries();
            this.loadChartData();
        } else if (!this.showVolume && this.volumeSeries) {
            this.chart.removeSeries(this.volumeSeries);
            this.volumeSeries = null;
        }
    }
    
    updatePosition(position) {
        this.currentData.position = position;
        this.updateOHLCVDisplay();
    }
    
    // Strategy visualization methods
    addSignal(type, time, price) {
        // Add buy/sell signal marker
        const marker = {
            time: time,
            position: type === 'buy' ? 'belowBar' : 'aboveBar',
            color: type === 'buy' ? '#10b981' : '#ef4444',
            shape: type === 'buy' ? 'arrowUp' : 'arrowDown',
            text: type === 'buy' ? 'BUY' : 'SELL'
        };
        
        this.signals.push(marker);
        this.candlestickSeries.setMarkers(this.signals);
    }
    
    clearSignals() {
        this.signals = [];
        this.candlestickSeries.setMarkers([]);
    }
    
    // Test strategy with mock signals
    testStrategy() {
        this.clearSignals();
        
        // Add some mock signals for demo
        const data = this.candlestickSeries.data();
        if (data && data.length > 10) {
            for (let i = 10; i < data.length; i += 20) {
                const candle = data[i];
                const type = Math.random() > 0.5 ? 'buy' : 'sell';
                this.addSignal(type, candle.time, candle.close);
            }
        }
    }
    
    handleResize() {
        const container = document.getElementById(this.containerId);
        if (container && this.chart) {
            this.chart.applyOptions({
                width: container.clientWidth,
                height: container.clientHeight,
            });
        }
    }
    
    destroy() {
        if (this.chart) {
            this.chart.remove();
            this.chart = null;
        }
    }
}

// Initialize chart when page loads
document.addEventListener('DOMContentLoaded', () => {
    const chartContainer = document.getElementById('trading-chart');
    if (chartContainer) {
        window.chartStrategy = new ChartStrategy('trading-chart');
        window.chartStrategy.init();
    }
});
