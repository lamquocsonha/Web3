// Chart management using TradingView Lightweight Charts
class ChartManager {
    constructor(containerId) {
        this.containerId = containerId;
        this.chart = null;
        this.candlestickSeries = null;
        this.volumeSeries = null;
        this.indicators = [];
        this.currentSymbol = 'VN30F1M';
        this.currentTimeframe = '1m';
        this.showVolume = true;
    }
    
    init() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error('Chart container not found');
            return;
        }
        
        // Create chart
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
            rightPriceScale: {
                borderColor: '#2d3748',
            },
            timeScale: {
                borderColor: '#2d3748',
                timeVisible: true,
                secondsVisible: false,
            },
        });
        
        // Create candlestick series
        this.candlestickSeries = this.chart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#ef4444',
            borderUpColor: '#10b981',
            borderDownColor: '#ef4444',
            wickUpColor: '#10b981',
            wickDownColor: '#ef4444',
        });
        
        // Create volume series
        if (this.showVolume) {
            this.volumeSeries = this.chart.addHistogramSeries({
                color: '#3b82f6',
                priceFormat: {
                    type: 'volume',
                },
                priceScaleId: '',
                scaleMargins: {
                    top: 0.8,
                    bottom: 0,
                },
            });
        }
        
        // Load initial data
        this.loadChartData();
        
        // Setup resize handler
        window.addEventListener('resize', () => this.handleResize());
        
        // Setup timeframe buttons
        this.setupTimeframeButtons();
    }
    
    setupTimeframeButtons() {
        const timeframeButtons = document.querySelectorAll('.timeframe-btn');
        timeframeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                timeframeButtons.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentTimeframe = e.target.textContent;
                this.loadChartData();
            });
        });
    }
    
    async loadChartData() {
        try {
            // Generate sample data (replace with real API call)
            const data = this.generateSampleData(200);
            this.candlestickSeries.setData(data.candles);
            
            if (this.volumeSeries && data.volumes) {
                this.volumeSeries.setData(data.volumes);
            }
            
            // Fit content
            this.chart.timeScale().fitContent();
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
    }
    
    generateSampleData(count) {
        const candles = [];
        const volumes = [];
        const basePrice = 1900;
        let currentPrice = basePrice;
        const now = Math.floor(Date.now() / 1000);
        
        for (let i = 0; i < count; i++) {
            const time = now - (count - i) * 60; // 1 minute intervals
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
    
    addIndicator(type, params) {
        // TODO: Implement various technical indicators
        console.log(`Adding indicator: ${type}`, params);
    }
    
    toggleVolume() {
        this.showVolume = !this.showVolume;
        
        if (this.showVolume && !this.volumeSeries) {
            this.volumeSeries = this.chart.addHistogramSeries({
                color: '#3b82f6',
                priceFormat: {
                    type: 'volume',
                },
                priceScaleId: '',
                scaleMargins: {
                    top: 0.8,
                    bottom: 0,
                },
            });
            this.loadChartData();
        } else if (!this.showVolume && this.volumeSeries) {
            this.chart.removeSeries(this.volumeSeries);
            this.volumeSeries = null;
        }
    }
    
    changeSymbol(symbol) {
        this.currentSymbol = symbol;
        this.loadChartData();
        this.updateSymbolInfo();
    }
    
    updateSymbolInfo() {
        // Update symbol display in header
        const symbolElement = document.querySelector('.symbol-name');
        if (symbolElement) {
            symbolElement.textContent = this.currentSymbol;
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
        window.chartManager = new ChartManager('trading-chart');
        window.chartManager.init();
    }
    
    // Setup indicators button
    const indicatorsBtn = document.querySelector('.btn-indicators');
    const indicatorsPanel = document.querySelector('.indicators-panel');
    
    if (indicatorsBtn && indicatorsPanel) {
        indicatorsBtn.addEventListener('click', () => {
            indicatorsPanel.style.display = indicatorsPanel.style.display === 'none' ? 'block' : 'none';
        });
        
        const closeBtn = indicatorsPanel.querySelector('.indicators-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                indicatorsPanel.style.display = 'none';
            });
        }
    }
    
    // Setup signals button
    const signalsBtn = document.querySelector('.btn-signals');
    const signalsPanel = document.querySelector('.signals-panel');
    
    if (signalsBtn && signalsPanel) {
        signalsBtn.addEventListener('click', () => {
            signalsPanel.style.display = signalsPanel.style.display === 'none' ? 'block' : 'none';
        });
        
        const closeBtn = signalsPanel.querySelector('.signals-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                signalsPanel.style.display = 'none';
            });
        }
    }
    
    // Setup volume toggle
    const volumeToggle = document.querySelector('.volume-toggle');
    if (volumeToggle && window.chartManager) {
        volumeToggle.addEventListener('change', (e) => {
            window.chartManager.toggleVolume();
        });
    }
    
    // Setup symbol selector
    const symbolSelector = document.getElementById('symbol-selector');
    if (symbolSelector && window.chartManager) {
        symbolSelector.addEventListener('change', (e) => {
            window.chartManager.changeSymbol(e.target.value);
        });
    }
});
