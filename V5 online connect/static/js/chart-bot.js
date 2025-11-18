// Chart Manager for Manual Trading Page
class ChartBot {
    constructor(containerId) {
        this.containerId = containerId;
        this.chart = null;
        this.candlestickSeries = null;
        this.volumeSeries = null;
        this.currentSymbol = 'VN30F1M';
        this.currentTimeframe = '1m';
        this.utcOffset = 7; // UTC+7 default
        this.showVolume = true;
        this.volumeScaleHeight = 0.2; // 20% of chart height
        
        // Current price data
        this.currentData = {
            open: 0,
            high: 0,
            low: 0,
            close: 0,
            volume: 0,
            position: 'FLAT'
        };
        
        // Connection manager
        this.connectionManager = window.ConnectionManager;
        
        // Bind events
        this.setupConnectionEvents();
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
        
        // Create candlestick series (use right scale)
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
        
        // Setup resize handler
        window.addEventListener('resize', () => this.handleResize());
        
        // Setup timeframe buttons
        this.setupTimeframeButtons();
        
        // Setup volume scale drag
        this.setupVolumeScaleDrag();
        
        // Setup UTC selector
        this.setupUTCSelector();
        
        // Setup volume toggle
        this.setupVolumeToggle();
        
        // Subscribe to crosshair move for OHLCV display
        this.chart.subscribeCrosshairMove(this.handleCrosshairMove.bind(this));
        
        // Initialize indicators modal
        this.indicatorsModal = new ChartIndicatorsModal(this.chart, 'bot');
        window.chartIndicatorsModal = this.indicatorsModal;

        // Load initial data after delay to ensure UploadDataManager is ready
        // Single call with appropriate delay
        setTimeout(() => {
            console.log('📊 ChartBot: Loading chart data...');
            this.loadChartData();
        }, 1000);
    }
    
    loadUploadedData(chartData, volumeData, metadata) {
        console.log('=== Bot: loadUploadedData called ===');
        console.log('Chart data:', chartData ? chartData.length : 0, 'bars');
        console.log('Metadata:', metadata);
        
        if (!chartData || chartData.length === 0) {
            console.warn('No data to load');
            return;
        }
        
        console.log('Loading uploaded data to bot chart:', chartData.length, 'bars');
        
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
        
        console.log('=== Bot: loadUploadedData completed ===');
    }
    
    async loadOnlineData(connection) {
        console.log('=== Bot: loadOnlineData called ===');
        console.log('Connection:', connection);
        
        if (!connection || !connection.profile) {
            console.error('❌ Invalid connection data');
            alert('⚠️ Lỗi: Thông tin kết nối không hợp lệ');
            return;
        }
        
        const { profile, symbol } = connection;
        
        console.log('📡 Bot Chart: Loading online data for:', profile.exchange, '-', symbol);
        
        try {
            // Show loading
            const statusEl = document.querySelector('.connection-status');
            if (statusEl) {
                statusEl.textContent = 'LOADING...';
                statusEl.style.background = '#f59e0b';
            }
            
            // Fetch data (reuse from chart-manual or create shared function)
            const response = await this.fetchExchangeData(profile, symbol);
            
            if (!response || !response.data || response.data.length === 0) {
                throw new Error('No data received from exchange');
            }
            
            console.log('✅ Bot: Received', response.data.length, 'candles');
            
            // Transform data
            const chartData = response.data.map(candle => ({
                time: candle.time,
                open: candle.open,
                high: candle.high,
                low: candle.low,
                close: candle.close
            }));
            
            const volumeData = response.data.map(candle => ({
                time: candle.time,
                value: candle.volume,
                color: candle.close >= candle.open ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)'
            }));
            
            // Clear & load
            this.candlestickSeries.setData([]);
            if (this.volumeSeries) this.volumeSeries.setData([]);
            
            this.candlestickSeries.setData(chartData);
            if (this.volumeSeries) this.volumeSeries.setData(volumeData);
            
            this.chart.timeScale().fitContent();
            
            // Update OHLCV
            const lastCandle = response.data[response.data.length - 1];
            this.updateOHLCV(lastCandle, {
                date: new Date(lastCandle.time * 1000).toLocaleDateString('vi-VN'),
                time: new Date(lastCandle.time * 1000).toLocaleTimeString('vi-VN'),
                volume: lastCandle.volume
            });
            
            if (statusEl) {
                statusEl.textContent = 'ONLINE';
                statusEl.style.background = '#10b981';
            }
            
            console.log('✅ Bot: Online data loaded');
            this.startRealtimeUpdates(profile, symbol);
            
        } catch (error) {
            console.error('❌ Bot: Error loading online data:', error);
            alert('❌ Bot: Lỗi khi tải dữ liệu online: ' + error.message);
            
            const statusEl = document.querySelector('.connection-status');
            if (statusEl) {
                statusEl.textContent = 'ERROR';
                statusEl.style.background = '#ef4444';
            }
        }
    }
    
    async fetchExchangeData(profile, symbol) {
        // Same as chart-manual
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const now = Math.floor(Date.now() / 1000);
        const data = [];
        
        for (let i = 100; i >= 0; i--) {
            const time = now - (i * 60);
            const basePrice = 1350;
            const volatility = 20;
            
            const open = basePrice + (Math.random() - 0.5) * volatility;
            const close = open + (Math.random() - 0.5) * volatility;
            const high = Math.max(open, close) + Math.random() * volatility / 2;
            const low = Math.min(open, close) - Math.random() * volatility / 2;
            const volume = Math.floor(Math.random() * 1000) + 100;
            
            data.push({
                time: time,
                open: parseFloat(open.toFixed(2)),
                high: parseFloat(high.toFixed(2)),
                low: parseFloat(low.toFixed(2)),
                close: parseFloat(close.toFixed(2)),
                volume: volume
            });
        }
        
        return { data: data };
    }
    
    startRealtimeUpdates(profile, symbol) {
        if (this.realtimeInterval) clearInterval(this.realtimeInterval);
        
        this.realtimeInterval = setInterval(async () => {
            try {
                const latestCandle = await this.fetchLatestCandle(profile, symbol);
                
                if (latestCandle) {
                    this.candlestickSeries.update({
                        time: latestCandle.time,
                        open: latestCandle.open,
                        high: latestCandle.high,
                        low: latestCandle.low,
                        close: latestCandle.close
                    });
                    
                    if (this.volumeSeries) {
                        this.volumeSeries.update({
                            time: latestCandle.time,
                            value: latestCandle.volume,
                            color: latestCandle.close >= latestCandle.open ? 
                                'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)'
                        });
                    }
                    
                    this.updateOHLCV(latestCandle, {
                        date: new Date(latestCandle.time * 1000).toLocaleDateString('vi-VN'),
                        time: new Date(latestCandle.time * 1000).toLocaleTimeString('vi-VN'),
                        volume: latestCandle.volume
                    });
                }
            } catch (error) {
                console.error('Bot: Error updating:', error);
            }
        }, 1000);
    }
    
    async fetchLatestCandle(profile, symbol) {
        const now = Math.floor(Date.now() / 1000);
        const basePrice = 1350;
        const volatility = 20;
        
        const open = basePrice + (Math.random() - 0.5) * volatility;
        const close = open + (Math.random() - 0.5) * volatility;
        const high = Math.max(open, close) + Math.random() * volatility / 2;
        const low = Math.min(open, close) - Math.random() * volatility / 2;
        const volume = Math.floor(Math.random() * 1000) + 100;
        
        return {
            time: now,
            open: parseFloat(open.toFixed(2)),
            high: parseFloat(high.toFixed(2)),
            low: parseFloat(low.toFixed(2)),
            close: parseFloat(close.toFixed(2)),
            volume: volume
        };
    }
    
    stopRealtimeUpdates() {
        if (this.realtimeInterval) {
            clearInterval(this.realtimeInterval);
            this.realtimeInterval = null;
        }
    }
    
    updateOHLCV(bar, csvBar) {
        // Update date and time if available
        if (csvBar) {
            const dateEl = document.getElementById('price-date');
            const timeEl = document.getElementById('price-time');
            if (dateEl) dateEl.textContent = csvBar.date;
            if (timeEl) timeEl.textContent = csvBar.time;
        }
        
        // Update OHLCV
        document.getElementById('price-open').textContent = bar.open.toFixed(2);
        document.getElementById('price-high').textContent = bar.high.toFixed(2);
        document.getElementById('price-low').textContent = bar.low.toFixed(2);
        document.getElementById('price-close').textContent = bar.close.toFixed(2);
        
        // Update volume if present
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
    
    setupConnectionEvents() {
        // Listen to connection events
        this.connectionManager.on('connected', (data) => {
            console.log('Chart connected:', data);
            this.onConnected();
        });
        
        this.connectionManager.on('disconnected', (data) => {
            console.log('Chart disconnected:', data);
            this.onDisconnected();
        });
        
        this.connectionManager.on('tick', (tick) => {
            this.onTickReceived(tick);
        });
    }
    
    onConnected() {
        // Subscribe to current symbol
        this.connectionManager.subscribe(this.currentSymbol, this.currentTimeframe);
        // Show online indicator
        this.updateConnectionStatus(true);
    }
    
    onDisconnected() {
        // Show offline indicator
        this.updateConnectionStatus(false);
    }
    
    onTickReceived(tick) {
        // Update chart with new tick
        this.updateChartWithTick(tick);
        
        // Update OHLCV display
        this.currentData = {
            open: tick.open,
            high: tick.high,
            low: tick.low,
            close: tick.close,
            volume: tick.volume,
            position: this.currentData.position
        };
        this.updateOHLCVDisplay();
    }
    
    updateChartWithTick(tick) {
        const time = Math.floor(new Date(tick.timestamp).getTime() / 1000);
        
        // Add candle
        this.candlestickSeries.update({
            time: time,
            open: tick.open,
            high: tick.high,
            low: tick.low,
            close: tick.close,
        });
        
        // Add volume
        if (this.volumeSeries) {
            this.volumeSeries.update({
                time: time,
                value: tick.volume,
                color: tick.close > tick.open ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)',
            });
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
        
        // Resubscribe if connected
        if (this.connectionManager.isConnected) {
            this.connectionManager.unsubscribe(this.currentSymbol);
            this.connectionManager.subscribe(this.currentSymbol, timeframe);
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
    
    updateConnectionStatus(isConnected) {
        const statusEl = document.querySelector('.connection-status');
        if (statusEl) {
            statusEl.textContent = isConnected ? 'ONLINE' : 'OFFLINE';
            statusEl.className = 'connection-status ' + (isConnected ? 'status-online' : 'status-offline');
        }
    }
    
    async loadChartData() {
        try {
            // PRIORITY 1: Check if uploaded CSV data exists
            if (window.UploadDataManager && window.UploadDataManager.csvData && window.UploadDataManager.csvData.length > 0) {
                console.log('✅ Found uploaded data:', window.UploadDataManager.csvData.length, 'bars');
                console.log('Loading uploaded data to chart...');
                
                // STEP 1: Convert CSV data to raw format
                const rawBars = [];
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

                    rawBars.push({
                        time: timestamp,
                        open: parseFloat(bar.open),
                        high: parseFloat(bar.high),
                        low: parseFloat(bar.low),
                        close: parseFloat(bar.close),
                        volume: parseFloat(bar.volume || 0)
                    });
                }

                // STEP 2: Resample bars according to current timeframe
                const resampledBars = this.resampleBars(rawBars, this.currentTimeframe);

                // STEP 3: Split into chart data and volume data
                const chartData = [];
                const volumeData = [];
                for (const bar of resampledBars) {
                    chartData.push({
                        time: bar.time,
                        open: bar.open,
                        high: bar.high,
                        low: bar.low,
                        close: bar.close
                    });

                    volumeData.push({
                        time: bar.time,
                        value: bar.volume,
                        color: bar.close >= bar.open ? '#10b98180' : '#ef444480'
                    });
                }

                console.log('Setting chart data:', chartData.length, 'bars (from', rawBars.length, 'raw bars)');
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
                console.log('✅ Chart loaded successfully from uploaded CSV');
                return;
            }

            // PRIORITY 2: If connected to WebSocket, data comes from real-time feed
            if (this.connectionManager.isConnected) {
                console.log('ℹ️ No uploaded data. Waiting for WebSocket data feed...');
                return;
            }

            // PRIORITY 3: No data available - show empty chart
            console.log('ℹ️ No data available. Please upload CSV or connect to data feed.');
            this.candlestickSeries.setData([]);
            if (this.volumeSeries) {
                this.volumeSeries.setData([]);
            }
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
    }

    // Resample bars to different timeframe
    resampleBars(rawBars, targetTimeframe) {
        if (!rawBars || rawBars.length === 0) {
            return [];
        }

        // Get target interval in seconds
        const targetInterval = this.getTimeframeSeconds();

        // If target is same as source (assume source is 1m), return as is
        const sourceTimeframe = window.UploadDataManager?.fileInfo?.timeframe || '1m';
        if (targetTimeframe === sourceTimeframe) {
            console.log('No resampling needed:', targetTimeframe, '==', sourceTimeframe);
            return rawBars;
        }

        console.log('Resampling from', sourceTimeframe, 'to', targetTimeframe, '(', targetInterval, 'seconds )');

        const resampled = [];
        let currentBucket = null;
        let bucketStart = null;

        for (const bar of rawBars) {
            // Calculate which bucket this bar belongs to
            const barBucketStart = Math.floor(bar.time / targetInterval) * targetInterval;

            // If new bucket, save previous and start new
            if (bucketStart !== barBucketStart) {
                if (currentBucket) {
                    resampled.push(currentBucket);
                }

                // Start new bucket
                bucketStart = barBucketStart;
                currentBucket = {
                    time: barBucketStart,
                    open: bar.open,
                    high: bar.high,
                    low: bar.low,
                    close: bar.close,
                    volume: bar.volume || 0
                };
            } else {
                // Update current bucket
                currentBucket.high = Math.max(currentBucket.high, bar.high);
                currentBucket.low = Math.min(currentBucket.low, bar.low);
                currentBucket.close = bar.close; // Last close
                currentBucket.volume += (bar.volume || 0);
            }
        }

        // Don't forget last bucket
        if (currentBucket) {
            resampled.push(currentBucket);
        }

        console.log('Resampled:', rawBars.length, '→', resampled.length, 'bars');
        return resampled;
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
        
        if (this.connectionManager.isConnected) {
            this.connectionManager.unsubscribe(this.currentSymbol);
            this.connectionManager.subscribe(symbol, this.currentTimeframe);
        }
        
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
        window.chartBot = new ChartBot('trading-chart');
        window.chartBot.init();
    }
});
