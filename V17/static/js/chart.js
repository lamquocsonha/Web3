// Initialize Socket.IO
const socket = io();

// Chart variables
let chart;
let candlestickSeries;
let volumeSeries;
let tickSeries;
let chartInitialized = false;
let volumeVisible = true;
let currentChartMode = 'candle';
let tickData = [];
let baseTimeframe = 'M1';
let currentTimezoneOffset = 0;
// offlineData and currentDataSource are managed by data-manager.js


// Setup chartDataLoaded event listener IMMEDIATELY (before DOMContentLoaded)
window.addEventListener('chartDataLoaded', function(event) {
    console.log('📊 chartDataLoaded event received:', event.detail);

    if (!chartInitialized) {
        console.warn('⚠️ Chart not ready yet');
        // If chart not initialized yet, store event and retry after init
        console.log('⏳ Chart not initialized yet, will retry after chart init...');
        window._pendingChartData = event.detail;
        return;
    }

    try {
        console.log('🔄 Forcing chart update with new data...');

        // Determine which data to display based on current mode
        let displayData = null;
        if (typeof currentDataSource !== 'undefined' && currentDataSource === 'online') {
            // Online mode: display online data on chart
            if (typeof onlineData !== 'undefined' && onlineData) {
                displayData = onlineData;
                console.log('📊 Using ONLINE data for chart display:', {
                    candles: displayData.candlesticks?.length,
                    symbol: displayData.symbol
                });
            } else {
                console.warn('⚠️ Online mode but no online data available');
                return;
            }
        } else {
            // Offline mode: display offline data on chart
            if (typeof offlineData !== 'undefined' && offlineData) {
                displayData = offlineData;
                console.log('📊 Using OFFLINE data for chart display:', {
                    candles: displayData.candlesticks?.length,
                    symbol: displayData.symbol
                });
            } else {
                console.warn('⚠️ Offline mode but no offline data available');
                return;
            }
        }

        // Update chart with the appropriate data
        if (displayData && candlestickSeries) {
            candlestickSeries.setData(displayData.candlesticks);
            if (volumeVisible && volumeSeries && displayData.volumes) {
                volumeSeries.setData(displayData.volumes);
            }
            console.log('✅ Chart updated successfully');
        }

        // IMPORTANT: Strategy signals ALWAYS use OFFLINE data (CSV), not online data
        // This ensures strategy signals are calculated from the CSV file, not exchange data
        if (currentBotStrategy && typeof loadStrategySignals === 'function') {
            if (typeof offlineData !== 'undefined' && offlineData) {
                console.log('🔄 Reloading strategy signals with OFFLINE data (CSV)...');
                loadStrategySignals(currentBotStrategy);
                console.log('✅ Strategy signals regenerated with offline CSV data');
            } else {
                console.warn('⚠️ Cannot load strategy signals: No offline CSV data available');
            }
        }
    } catch (error) {
        console.error('❌ Error updating chart:', error);
    }
});

// Initialize chart on page load  
document.addEventListener('DOMContentLoaded', async function() {
    console.log('📱 Chart.js DOM loaded');
    console.log('📚 LightweightCharts available:', typeof LightweightCharts !== 'undefined');
    
    // offlineData is already loaded by data-manager.js
    // Just check and update UI
    if (typeof offlineData !== 'undefined' && offlineData) {
        console.log('📦 Using offline data from data-manager:', offlineData.candlesticks?.length, 'candles');
    }
    
    // Wait for library to load
    setTimeout(() => {
        console.log('🚀 Starting chart initialization...');
        initChart();
        
        // Load data after chart is ready
        setTimeout(() => {
            if (chartInitialized && typeof offlineData !== 'undefined' && offlineData) {
                console.log('📊 Loading offline data to chart');
                loadOfflineData();
                // Set default timeframe to 1m after loading offline data
                setTimeout(() => changeTimeframe('1m'), 200);
            } else {
                console.log('⏭️ No offline data, waiting for CSV upload...');
            }
        }, 500);
        
        setupSocketListeners();
    }, 500);
    
    updateTime();
    setInterval(updateTime, 1000);
    
    // Initialize bot/strategy lists
    setTimeout(() => {
        renderConditions('entry');
        renderConditions('exit');
        renderStrategiesList();
    }, 300);
});

// Initialize TradingView Lightweight Chart
function initChart() {
    const chartContainer = document.getElementById('chart');
    
    if (!chartContainer) {
        console.error('❌ Chart container not found!');
        return;
    }
    
    // Check if LightweightCharts is loaded
    if (typeof LightweightCharts === 'undefined' || !LightweightCharts.createChart) {
        console.warn('⏳ Waiting for LightweightCharts library...');
        setTimeout(initChart, 300);
        return;
    }
    
    try {
        console.log('🎨 Creating chart instance...');
        
        chart = LightweightCharts.createChart(chartContainer, {
            width: chartContainer.clientWidth,
            height: chartContainer.clientHeight,
            layout: {
                background: { color: '#131722' },
                textColor: '#d1d4dc',
            },
            grid: {
                vertLines: { color: '#1e222d' },
                horzLines: { color: '#1e222d' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: '#2a2e39',
                autoScale: true,
            },
            leftPriceScale: {
                visible: true,
                borderColor: '#2a2e39',
                mode: 0,  // 0 = Normal (absolute values), 1 = Logarithmic, 2 = Percentage
                alignLabels: false,
                scaleMargins: {
                    top: 0.8,  // Volume takes 20% of chart height (bottom 20%)
                    bottom: 0,
                },
            },
            timeScale: {
                borderColor: '#2a2e39',
                timeVisible: true,
                secondsVisible: false,
                rightOffset: 5,
                barSpacing: 6,
                fixLeftEdge: false,
                fixRightEdge: false,
                lockVisibleTimeRangeOnResize: true,
                rightBarStaysOnScroll: true,
            },
        });
        
        console.log('📊 Chart created:', typeof chart, chart);

        // Verify chart has required methods
        if (!chart || typeof chart.addCandlestickSeries !== 'function') {
            throw new Error('Chart object is invalid or missing addCandlestickSeries method');
        }

        // Add candlestick series
        candlestickSeries = chart.addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderUpColor: '#26a69a',
            borderDownColor: '#ef5350',
            wickUpColor: '#26a69a',
            wickDownColor: '#ef5350',
        });
        
        console.log('🕯️ Candlestick series added');

        // Add volume series with separate scale on left
        volumeSeries = chart.addHistogramSeries({
            color: '#26a69a',
            priceFormat: {
                type: 'volume',  // Use 'volume' format instead of 'price' to display full numbers
            },
            priceScaleId: 'left',
            base: 0, // Start from 0 - baseline fixed at bottom
            priceLineVisible: false,
            lastValueVisible: false,
        });
        
        console.log('📊 Volume series added');

        // Fixed volume scale at 20% height with normal mode (not percentage)
        chart.applyOptions({
            leftPriceScale: {
                visible: true,
                mode: 0,  // 0 = Normal, 1 = Logarithmic, 2 = Percentage
                alignLabels: false,
                scaleMargins: {
                    top: 0.8,  // 20% volume height
                    bottom: 0,
                },
            },
        });

        // Add tick series (line series) for tick data - initially hidden
        tickSeries = chart.addLineSeries({
            color: '#2962ff',
            lineWidth: 2,
            priceLineVisible: false,
            lastValueVisible: true,
            crosshairMarkerVisible: true,
            visible: false // Hidden by default
        });
        
        console.log('📈 Tick series added (hidden)');

        // Handle resize
        window.addEventListener('resize', () => {
            chart.applyOptions({
                width: chartContainer.clientWidth,
                height: chartContainer.clientHeight,
            });
        });
        
        // Add crosshair move handler to show OHLC info (#8)
        chart.subscribeCrosshairMove((param) => {
            if (!param || !param.time || !param.seriesData) {
                // Reset to last values when not hovering
                return;
            }

            const candleData = param.seriesData.get(candlestickSeries);

            if (candleData) {
                const { open, high, low, close, time } = candleData;

                // Update chart header
                const openEl = document.getElementById('openPrice');
                const highEl = document.getElementById('highPrice');
                const lowEl = document.getElementById('lowPrice');
                const closeEl = document.getElementById('closePrice');
                const volumeEl = document.getElementById('volumeDisplay');

                if (openEl && open !== undefined) openEl.textContent = open.toFixed(2);
                if (highEl && high !== undefined) highEl.textContent = high.toFixed(2);
                if (lowEl && low !== undefined) lowEl.textContent = low.toFixed(2);
                if (closeEl && close !== undefined) closeEl.textContent = close.toFixed(2);

                // Update volume - try multiple methods to get volume
                if (volumeEl) {
                    let volume = 0;

                    // Method 1: Get volume directly from candleData if available
                    if (candleData.volume !== undefined) {
                        volume = candleData.volume;
                        console.log('Volume from candleData:', volume);
                    }
                    // Method 2: Get from volumeSeries in param.seriesData
                    else if (volumeSeries) {
                        const volumeData = param.seriesData.get(volumeSeries);
                        if (volumeData) {
                            volume = volumeData.value !== undefined ? volumeData.value : volumeData;
                            console.log('Volume from volumeSeries:', volume);
                        }
                    }

                    // Method 3: Find from offlineData using time (fallback)
                    if (volume === 0 && offlineData) {
                        // Try volumes array first
                        if (offlineData.volumes && Array.isArray(offlineData.volumes)) {
                            const volumeData = offlineData.volumes.find(v => v.time === time);
                            if (volumeData && volumeData.value !== undefined) {
                                volume = volumeData.value;
                                console.log('Volume from offlineData.volumes:', volume);
                            }
                        }

                        // Fallback: check if candlestick has volume property
                        if (volume === 0 && offlineData.candlesticks && Array.isArray(offlineData.candlesticks)) {
                            const candle = offlineData.candlesticks.find(c => c.time === time);
                            if (candle && candle.volume !== undefined) {
                                volume = candle.volume;
                                console.log('Volume from offlineData.candlesticks:', volume);
                            }
                        }
                    }

                    // Display volume
                    if (volume > 0) {
                        volumeEl.textContent = Math.round(volume).toLocaleString();
                    } else {
                        volumeEl.textContent = '0';
                        console.warn('No volume found for time:', time);
                    }
                }
            }
        });
        
        chartInitialized = true;
        console.log('✅ Chart initialized successfully!');
        console.log('   - Chart:', !!chart);
        console.log('   - Candlestick:', !!candlestickSeries);
        console.log('   - Volume:', !!volumeSeries);
        
        // Check if there's pending chart data from early event
        if (window._pendingChartData) {
            console.log('⏳ Found pending chart data, loading now...');
            setTimeout(() => {
                window.dispatchEvent(new CustomEvent('chartDataLoaded', {
                    detail: window._pendingChartData
                }));
                delete window._pendingChartData;
            }, 100);
        }
        
    } catch (error) {
        console.error('❌ Error initializing chart:', error);
        console.error('   LightweightCharts:', typeof LightweightCharts);
        console.error('   Chart object:', chart);
        chartInitialized = false;
        
        // Retry after delay
        setTimeout(initChart, 500);
    }
}

// Load initial chart data
async function loadInitialData() {
    // DISABLED: Don't load mock data anymore
    // Only use offline CSV data or online API
    console.log('⏭️ loadInitialData disabled - use offline CSV or online API');
    return;
    
    /* 
    // Don't load mock data if we have offline data or in offline mode
    if (offlineData || currentDataSource === 'offline') {
        console.log('⏭️ Skipping mock data - using offline data');
        return;
    }
    
    try {
        const response = await fetch('/api/chart-data');
        const data = await response.json();
        
        // Only use mock data if in online mode
        if (currentDataSource === 'online') {
            // Set candlestick data
            candlestickSeries.setData(data);
            
            // Set volume data
            const volumeData = data.map(d => ({
                time: d.time,
                value: d.volume,
                color: d.close >= d.open ? '#26a69a80' : '#ef535080'
            }));
            if (volumeVisible) {
                if (volumeVisible && volumeSeries) volumeSeries.setData(volumeData);
            }
            
            // Update price display
            if (data.length > 0) {
                const lastCandle = data[data.length - 1];
                updatePriceDisplay(lastCandle, lastCandle.volume);
            }
        }
        
        // Load orders and positions
        loadOrders();
        loadPositions();
        
    } catch (error) {
        console.error('Error loading chart data:', error);
    }
    */
}

// Update price display
function updatePriceDisplay(candle, volume) {
    // Update OHLC
    const openEl = document.getElementById('openPrice');
    const highEl = document.getElementById('highPrice');
    const lowEl = document.getElementById('lowPrice');
    const closeEl = document.getElementById('closePrice');
    const volumeEl = document.getElementById('volumeDisplay');

    if (openEl && candle.open !== undefined) openEl.textContent = candle.open.toFixed(2);
    if (highEl && candle.high !== undefined) highEl.textContent = candle.high.toFixed(2);
    if (lowEl && candle.low !== undefined) lowEl.textContent = candle.low.toFixed(2);
    if (closeEl && candle.close !== undefined) closeEl.textContent = candle.close.toFixed(2);

    // Update volume if provided
    if (volume !== undefined && volumeEl) {
        volumeEl.textContent = Math.round(volume).toLocaleString();
    }

    // Update price input for manual trading
    const priceInput = document.getElementById('priceInput');
    if (priceInput && candle.close !== undefined) {
        priceInput.value = candle.close.toFixed(2);
    }
}

// Setup Socket.IO listeners
function setupSocketListeners() {
    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('price_update', (data) => {
        // DISABLED: Don't auto-update with mock data
        // Only update when using online/live data source
        if (currentDataSource !== 'online') {
            return;
        }
        
        /*
        // Update candlestick
        candlestickSeries.update(data.candle);
        
        // Update volume
        volumeSeries.update({
            time: data.candle.time,
            value: data.candle.volume,
            color: data.candle.close >= data.candle.open ? '#26a69a80' : '#ef535080'
        });
        
        // Update price display
        updatePriceDisplay(data.candle);
        */
    });

    socket.on('order_update', (data) => {
        renderOrders(data.orders);
    });

    socket.on('position_update', (data) => {
        renderPositions(data.positions);
    });
    
    // Real-time MQTT tick data handler
    socket.on('realtime_tick', (data) => {
        console.log('📊 Realtime tick:', data);
        
        // Store tick data
        if (data.data && data.data.price && data.data.time) {
            const tickPoint = {
                time: data.data.time,
                value: data.data.price
            };
            
            // Add to tick data array
            tickData.push(tickPoint);
            
            // Keep last 10000 ticks only
            if (tickData.length > 10000) {
                tickData.shift();
            }
            
            // Update tick series if in tick mode
            if (currentChartMode === 'tick' && tickSeries) {
                tickSeries.update(tickPoint);
            }
        }
        
        // Update current price display if symbol matches
        const currentSymbol = document.getElementById('symbolInput')?.value;
        if (data.symbol === currentSymbol && data.data.price) {
            updatePriceDisplay({
                close: data.data.price,
                time: data.data.time || Date.now() / 1000
            });
        }
    });
    
    // Real-time MQTT candle data handler
    socket.on('realtime_candle', (data) => {
        console.log('🕯️ Realtime candles:', data.symbol, data.data.length);
        
        // Update chart if symbol matches and chart is in online mode
        const currentSymbol = document.getElementById('symbolInput')?.value;
        if (data.symbol === currentSymbol && currentDataSource === 'online' && chartInitialized) {
            try {
                // Update candlestick series with new data
                const candles = data.data.map(c => ({
                    time: c.time,
                    open: c.open,
                    high: c.high,
                    low: c.low,
                    close: c.close
                }));
                
                if (candles.length > 0) {
                    candlestickSeries.setData(candles);
                    
                    // Update volume series
                    const volumes = data.data.map(c => ({
                        time: c.time,
                        value: c.volume,
                        color: c.close >= c.open ? '#26a69a80' : '#ef535080'
                    }));
                    if (volumeVisible && volumeSeries) volumeSeries.setData(volumes);

                    // Force scale update to ensure volume displays correctly
                    chart.applyOptions({
                        leftPriceScale: {
                            visible: true,
                            mode: 0,  // 0 = Normal (absolute values), not percentage
                            autoScale: true,
                            scaleMargins: {
                                top: 0.8,  // Volume takes 20% of chart height
                                bottom: 0,
                            },
                        },
                    });

                    // Update price display with latest candle
                    const lastCandle = candles[candles.length - 1];
                    const lastVolume = data.data[data.data.length - 1].volume;
                    updatePriceDisplay(lastCandle, lastVolume);
                    
                    console.log('✅ Chart updated with real-time data');
                }
            } catch (error) {
                console.error('❌ Error updating chart with realtime data:', error);
            }
        }
    });
}

// Place order
async function placeOrder(side) {
    const orderData = {
        symbol: document.getElementById('symbolInput').value,
        type: document.getElementById('orderType').value,
        side: side,
        price: parseFloat(document.getElementById('priceInput').value),
        volume: parseInt(document.getElementById('volumeInput').value)
    };

    try {
        const response = await fetch('/api/place-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });

        const result = await response.json();
        if (result.success) {
            alert(`Đặt lệnh ${side} thành công!`);
            loadOrders();
        }
    } catch (error) {
        console.error('Error placing order:', error);
        alert('Lỗi khi đặt lệnh!');
    }
}

// Load orders
async function loadOrders() {
    try {
        const response = await fetch('/api/orders');
        const orders = await response.json();
        renderOrders(orders);
    } catch (error) {
        console.error('Error loading orders:', error);
    }
}

// Render orders table
function renderOrders(orders) {
    const tbody = document.getElementById('ordersTableBody');
    
    if (orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="no-data">Không có lệnh nào</td></tr>';
        return;
    }

    tbody.innerHTML = orders.map(order => `
        <tr>
            <td>Demo</td>
            <td>${order.time}</td>
            <td style="color: ${order.side === 'LONG' ? '#26a69a' : '#ef5350'}">${order.side}</td>
            <td>${order.symbol}</td>
            <td>${order.price}</td>
            <td>-</td>
            <td>${order.volume}</td>
            <td>${order.status}</td>
            <td><button onclick="cancelOrder(${order.id})" style="color: #ef5350; cursor: pointer; background: none; border: none;">✕</button></td>
        </tr>
    `).join('');
}

// Load positions
async function loadPositions() {
    try {
        const response = await fetch('/api/positions');
        const positions = await response.json();
        renderPositions(positions);
    } catch (error) {
        console.error('Error loading positions:', error);
    }
}

// Render positions table
function renderPositions(positions) {
    const tbody = document.getElementById('positionsTableBody');
    
    if (positions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="no-data">Không có vị thế nào</td></tr>';
        return;
    }

    tbody.innerHTML = positions.map(position => `
        <tr>
            <td>Demo</td>
            <td>${position.symbol}</td>
            <td style="color: ${position.side === 'LONG' ? '#26a69a' : '#ef5350'}">${position.side}</td>
            <td>${position.entryPrice}</td>
            <td>${position.currentPrice}</td>
            <td>${position.volume}</td>
            <td style="color: ${position.pnl >= 0 ? '#26a69a' : '#ef5350'}">${position.pnl.toFixed(2)}</td>
            <td>Open</td>
            <td><button onclick="closePosition(${position.id})" style="color: #ef5350; cursor: pointer; background: none; border: none;">Đóng</button></td>
        </tr>
    `).join('');
}

// Switch tabs
function switchTab(tabName) {
    // Remove active class from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab
    if (tabName === 'orders') {
        document.querySelector('.tab-btn:nth-child(1)').classList.add('active');
        document.getElementById('ordersTab').classList.add('active');
    } else if (tabName === 'positions') {
        document.querySelector('.tab-btn:nth-child(2)').classList.add('active');
        document.getElementById('positionsTab').classList.add('active');
    } else if (tabName === 'botlogs') {
        document.querySelector('.tab-btn:nth-child(3)').classList.add('active');
        document.getElementById('botlogsTab').classList.add('active');
    }
}

// Close position
async function closePosition(positionId) {
    if (!confirm('Bạn có chắc muốn đóng vị thế này?')) return;
    
    try {
        const response = await fetch(`/api/close-position/${positionId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        if (result.success) {
            alert('Đóng vị thế thành công!');
            loadPositions();
        }
    } catch (error) {
        console.error('Error closing position:', error);
        alert('Lỗi khi đóng vị thế!');
    }
}

// Cancel order
function cancelOrder(orderId) {
    if (!confirm('Bạn có chắc muốn hủy lệnh này?')) return;
    alert('Chức năng đang phát triển!');
}

// Close all positions
function closeAllPositions() {
    if (!confirm('Bạn có chắc muốn đóng TẤT CẢ vị thế?')) return;
    alert('Chức năng đang phát triển!');
}

// Update time display
function updateTime() {
    const now = new Date();
    const timeString = now.toTimeString().split(' ')[0];
    document.getElementById('currentTime').textContent = `${timeString} (UTC+7)`;
}

// Chart Navigation Functions
function scrollToStart() {
    if (!chart) return;
    const timeScale = chart.timeScale();
    const logicalRange = timeScale.getVisibleLogicalRange();
    if (logicalRange) {
        timeScale.scrollToPosition(-logicalRange.from, false);
    }
}

function scrollLeft() {
    if (!chart) return;
    const timeScale = chart.timeScale();
    const logicalRange = timeScale.getVisibleLogicalRange();
    if (logicalRange) {
        const distance = (logicalRange.to - logicalRange.from) * 0.3;
        timeScale.scrollToPosition(-distance, true);
    }
}

function scrollRight() {
    if (!chart) return;
    const timeScale = chart.timeScale();
    const logicalRange = timeScale.getVisibleLogicalRange();
    if (logicalRange) {
        const distance = (logicalRange.to - logicalRange.from) * 0.3;
        timeScale.scrollToPosition(distance, true);
    }
}

function scrollToEnd() {
    if (!chart) return;
    const timeScale = chart.timeScale();
    timeScale.scrollToRealTime();
}

// Change timeframe
// Timeframe Aggregator for offline data
const TimeframeAggregator = {
    /**
     * Aggregate 1-minute candles into higher timeframes
     * @param {Array} candles1m - Array of 1-minute OHLC candles
     * @param {string} targetTF - Target timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)
     * @returns {Array} Aggregated candles
     */
    aggregate: function(candles1m, targetTF) {
        if (!candles1m || candles1m.length === 0) return [];
        
        const tfMinutes = {
            '1m': 1, 'M1': 1,
            '5m': 5, 'M5': 5,
            '15m': 15, 'M15': 15,
            '30m': 30, 'M30': 30,
            '1h': 60, 'H1': 60,
            '4h': 240, 'H4': 240,
            '1d': 1440, 'D1': 1440
        };
        
        const targetMinutes = tfMinutes[targetTF] || 1;
        
        // If already 1m, return as is
        if (targetMinutes === 1) return candles1m;
        
        const aggregated = [];
        const targetSeconds = targetMinutes * 60;
        
        let currentGroup = [];
        let currentPeriodStart = null;
        
        for (const candle of candles1m) {
            const candleTime = candle.time;
            const periodStart = Math.floor(candleTime / targetSeconds) * targetSeconds;
            
            if (currentPeriodStart === null) {
                currentPeriodStart = periodStart;
            }
            
            if (periodStart === currentPeriodStart) {
                currentGroup.push(candle);
            } else {
                // Aggregate current group
                if (currentGroup.length > 0) {
                    aggregated.push(this._aggregateGroup(currentGroup, currentPeriodStart));
                }
                
                // Start new group
                currentGroup = [candle];
                currentPeriodStart = periodStart;
            }
        }
        
        // Aggregate last group
        if (currentGroup.length > 0) {
            aggregated.push(this._aggregateGroup(currentGroup, currentPeriodStart));
        }
        
        console.log(`📊 Aggregated ${candles1m.length} candles → ${aggregated.length} ${targetTF} candles`);
        return aggregated;
    },
    
    _aggregateGroup: function(candles, periodStart) {
        return {
            time: periodStart,
            open: candles[0].open,
            high: Math.max(...candles.map(c => c.high)),
            low: Math.min(...candles.map(c => c.low)),
            close: candles[candles.length - 1].close,
            volume: candles.reduce((sum, c) => sum + (c.volume || 0), 0)
        };
    }
};

function changeTimeframe(tf) {
    if (!chart) return;
    
    console.log(`🔄 Changing timeframe to: ${tf}`);
    
    // Timeframe hierarchy for validation (#5)
    const tfHierarchy = {
        'M1': 1, '1m': 1,
        'M5': 5, '5m': 5,
        'M15': 15, '15m': 15,
        'M30': 30, '30m': 30,
        'H1': 60, '1h': 60,
        'H4': 240, '4h': 240,
        'D1': 1440, '1d': 1440
    };
    
    // Check if trying to downgrade from base timeframe
    const baseTFMinutes = tfHierarchy[baseTimeframe] || 1;
    const targetTFMinutes = tfHierarchy[tf] || 1;
    
    if (targetTFMinutes < baseTFMinutes) {
        console.warn(`⚠️ Cannot downgrade from ${baseTimeframe} to ${tf}. Base timeframe is ${baseTimeframe}.`);
        alert(`⚠️ Không thể chuyển xuống ${tf}. Timeframe gốc của profile là ${baseTimeframe}.\n\nChỉ có thể chuyển lên timeframe cao hơn (vd: ${baseTimeframe} → M5, M15, M30...)`);
        return;
    }
    
    // Update active button
    document.querySelectorAll('.tf-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tf') === tf) {
            btn.classList.add('active');
        }
    });
    
    // Handle TICK mode
    if (tf === 'tick') {
        console.log('📊 Switching to TICK chart mode');
        currentChartMode = 'tick';

        // Hide candlestick and volume series
        if (candlestickSeries) {
            chart.removeSeries(candlestickSeries);
            candlestickSeries = null;
        }
        if (volumeSeries) {
            chart.removeSeries(volumeSeries);
            volumeSeries = null;
        }

        // Show tick series
        if (!tickSeries) {
            tickSeries = chart.addLineSeries({
                color: '#2962ff',
                lineWidth: 2,
                priceLineVisible: false,
                lastValueVisible: true,
                crosshairMarkerVisible: true,
            });
        }

        // Load tick data if available
        if (tickData && tickData.length > 0) {
            tickSeries.setData(tickData);
            chart.timeScale().fitContent();
            console.log(`✅ Loaded ${tickData.length} tick data points`);
        } else {
            console.log('⚠️ No tick data available yet');
        }

        return;
    }
    
    // Switch back to candle mode if coming from tick
    if (currentChartMode === 'tick') {
        console.log('📊 Switching back to CANDLE chart mode');
        currentChartMode = 'candle';
        
        // Remove tick series
        if (tickSeries) {
            chart.removeSeries(tickSeries);
            tickSeries = null;
        }
        
        // Re-add candlestick series
        if (!candlestickSeries) {
            candlestickSeries = chart.addCandlestickSeries({
                upColor: '#26a69a',
                downColor: '#ef5350',
                borderUpColor: '#26a69a',
                borderDownColor: '#ef5350',
                wickUpColor: '#26a69a',
                wickDownColor: '#ef5350',
            });
        }
        
        // Re-add volume series
        if (!volumeSeries) {
            volumeSeries = chart.addHistogramSeries({
                color: '#26a69a',
                priceFormat: {
                    type: 'volume',  // Use 'volume' format instead of 'price' to display full numbers
                },
                priceScaleId: 'left', // Use left scale for volume
                base: 0, // Start from 0 - baseline fixed at bottom
                priceLineVisible: false,
                lastValueVisible: false,
            });
        }
        
        // Reload candle data
        if (currentDataSource === 'offline' && typeof offlineData !== 'undefined' && offlineData && offlineData.candlesticks) {
            const base1mData = offlineData.base1mData || offlineData.candlesticks;
            let aggregatedData = base1mData;

            if (tf !== '1m' && tf !== 'M1') {
                aggregatedData = TimeframeAggregator.aggregate(base1mData, tf);
            }

            if (aggregatedData && aggregatedData.length > 0) {
                candlestickSeries.setData(aggregatedData);

                const volumeData = aggregatedData.map(candle => ({
                    time: candle.time,
                    value: candle.volume || 0,
                    color: candle.close >= candle.open ? '#26a69a80' : '#ef535080'
                }));
                if (volumeVisible && volumeSeries) volumeSeries.setData(volumeData);

                // Fit content after restoring from tick mode
                setTimeout(() => {
                    chart.timeScale().fitContent();
                }, 100);

                console.log(`✅ Restored ${aggregatedData.length} candles after tick mode`);
            }
        }
    }
    
    // For offline data, re-aggregate from base 1m data
    if (currentDataSource === 'offline' && offlineData && offlineData.candlesticks) {
        console.log('📊 Offline mode: Aggregating data for timeframe:', tf);
        
        // Get base 1m data
        const base1mData = offlineData.base1mData || offlineData.candlesticks;
        
        // Aggregate to target timeframe
        let aggregatedData;
        if (tf === '1m' || tf === 'M1') {
            aggregatedData = base1mData;
        } else {
            aggregatedData = TimeframeAggregator.aggregate(base1mData, tf);
        }
        
        // Update chart with aggregated data
        if (aggregatedData && aggregatedData.length > 0) {
            candlestickSeries.setData(aggregatedData);
            
            // Update volume
            const volumeData = aggregatedData.map(candle => ({
                time: candle.time,
                value: candle.volume || 0,
                color: candle.close >= candle.open ? '#26a69a80' : '#ef535080'
            }));
            // Volume data - no normalization needed
            if (volumeVisible && volumeSeries) volumeSeries.setData(volumeData);
            
            // Fit content to show all data with timeout to ensure rendering is complete
            setTimeout(() => {
                chart.timeScale().fitContent();
            }, 100);
            
            console.log(`✅ Updated chart with ${aggregatedData.length} ${tf} candles`);
            return;
        }
    }
    
    // For online data with base 1m data available, also aggregate
    if (currentDataSource === 'online' && offlineData && offlineData.candlesticks && (tf === 'M5' || tf === 'M15' || tf === 'M30' || tf === '5m' || tf === '15m' || tf === '30m')) {
        console.log('📊 Online mode with M1 data: Aggregating to timeframe:', tf);
        
        // Get base 1m data
        const base1mData = offlineData.base1mData || offlineData.candlesticks;
        
        // Aggregate to target timeframe
        const aggregatedData = TimeframeAggregator.aggregate(base1mData, tf);
        
        // Update chart with aggregated data
        if (aggregatedData && aggregatedData.length > 0) {
            candlestickSeries.setData(aggregatedData);
            
            // Update volume
            const volumeData = aggregatedData.map(candle => ({
                time: candle.time,
                value: candle.volume || 0,
                color: candle.close >= candle.open ? '#26a69a80' : '#ef535080'
            }));
            // Volume data - no normalization needed
            if (volumeVisible && volumeSeries) volumeSeries.setData(volumeData);
            
            // Fit content to show all data with timeout to ensure rendering is complete
            setTimeout(() => {
                chart.timeScale().fitContent();
            }, 100);
            
            console.log(`✅ Updated chart with ${aggregatedData.length} ${tf} candles`);
            return;
        }
    }
    
    // For online data or time-range based view (legacy behavior)
    const timeScale = chart.timeScale();
    
    // For minute-based timeframes (M5, M15, M30) without base data, just fit content
    if (tf === 'M5' || tf === 'M15' || tf === 'M30') {
        setTimeout(() => {
            timeScale.fitContent();
        }, 100);
        console.log(`Timeframe changed to: ${tf} (fit content)`);
        return;
    }
    
    // Calculate visible range based on timeframe for date-based ranges
    const now = Math.floor(Date.now() / 1000);
    
    let from;
    switch(tf) {
        case '1d':
            from = now - (24 * 60 * 60);
            break;
        case '5d':
            from = now - (5 * 24 * 60 * 60);
            break;
        case '1m':
            from = now - (30 * 24 * 60 * 60);
            break;
        case '3m':
            from = now - (90 * 24 * 60 * 60);
            break;
        case '1y':
            from = now - (365 * 24 * 60 * 60);
            break;
        case '5y':
            from = now - (5 * 365 * 24 * 60 * 60);
            break;
        default:
            // If unknown, just fit content
            setTimeout(() => {
                timeScale.fitContent();
            }, 100);
            console.log(`Timeframe changed to: ${tf} (default fit)`);
            return;
    }
    
    timeScale.setVisibleRange({
        from: from,
        to: now
    });
    
    console.log(`Timeframe changed to: ${tf}`);
}

// Toggle volume visibility
function toggleVolume() {
    if (!volumeSeries) return;

    volumeVisible = !volumeVisible;
    const btn = document.getElementById('toggleVolumeBtn');

    if (volumeVisible) {
        volumeSeries.applyOptions({
            visible: true
        });
        btn.classList.remove('inactive');
        console.log('✅ Volume shown');
    } else {
        volumeSeries.applyOptions({
            visible: false
        });
        btn.classList.add('inactive');
        console.log('❌ Volume hidden');
    }
}

// Toggle position panel visibility for index chart
function toggleIndexPositionPanel() {
    window.showIndexPositionPanel = !window.showIndexPositionPanel;
    const btn = document.getElementById('indexTogglePositionPanel');

    if (window.showIndexPositionPanel) {
        btn.style.background = '#2962ff';
        console.log('✅ Index Position Panel ON');
    } else {
        btn.style.background = '';
        console.log('❌ Index Position Panel OFF');
    }

    // Refresh position markers if needed
    if (typeof updatePositionMarkers === 'function') {
        // This will be handled by the position markers system
    }
}

// Toggle buy signals visibility for index chart
function toggleIndexBuySignals() {
    window.showIndexBuySignals = !window.showIndexBuySignals;
    const btn = document.getElementById('indexToggleBuySignals');

    if (window.showIndexBuySignals) {
        btn.style.opacity = '1';
        console.log('✅ Index Buy Signals ON');
    } else {
        btn.style.opacity = '0.4';
        console.log('❌ Index Buy Signals OFF');
    }

    // Refresh markers if signal data is available
    // This will be handled by signal display functions
}

// Toggle short signals visibility for index chart
function toggleIndexShortSignals() {
    window.showIndexShortSignals = !window.showIndexShortSignals;
    const btn = document.getElementById('indexToggleShortSignals');

    if (window.showIndexShortSignals) {
        btn.style.opacity = '1';
        console.log('✅ Index Short Signals ON');
    } else {
        btn.style.opacity = '0.4';
        console.log('❌ Index Short Signals OFF');
    }

    // Refresh markers if signal data is available
    // This will be handled by signal display functions
}

// Change data source
function changeDataSource(source) {
    currentDataSource = source || 'offline';
    
    console.log('Data source changed to:', currentDataSource);
    
    // Update toggle button styles
    const offlineBtn = document.getElementById('offlineDataBtn');
    const onlineBtn = document.getElementById('onlineDataBtn');
    
    if (offlineBtn && onlineBtn) {
        if (currentDataSource === 'offline') {
            offlineBtn.style.background = '#2962ff';
            offlineBtn.style.color = 'white';
            onlineBtn.style.background = 'transparent';
            onlineBtn.style.color = '#787b86';
        } else {
            offlineBtn.style.background = 'transparent';
            offlineBtn.style.color = '#787b86';
            onlineBtn.style.background = '#2962ff';
            onlineBtn.style.color = 'white';
        }
    }

    if (currentDataSource === 'offline') {
        if (typeof offlineData !== 'undefined' && offlineData) {
            loadOfflineData();
        } else {
            console.log('⏭️ No offline data, waiting for CSV upload...');
        }
    } else {
        console.log('🌐 Online mode active - waiting for exchange connection...');
    }
}

// Load offline data
function loadOfflineData() {
    if (!offlineData || !chartInitialized) return;
    
    console.log('📦 Loading offline data:', offlineData.candlesticks.length, 'candles');
    
    try {
        // Store base 1m data for timeframe aggregation if not already stored
        if (!offlineData.base1mData) {
            offlineData.base1mData = [...offlineData.candlesticks]; // Clone array
            console.log('💾 Stored base 1m data for timeframe aggregation');
        }
        
        candlestickSeries.setData(offlineData.candlesticks);
        if (volumeVisible && offlineData.volumes) {
            if (volumeVisible && volumeSeries) volumeSeries.setData(offlineData.volumes);
        }

        // Force scale update to ensure volume displays correctly on first load
        chart.applyOptions({
            leftPriceScale: {
                visible: true,
                mode: 0,  // 0 = Normal (absolute values), not percentage
                autoScale: true,
                scaleMargins: {
                    top: 0.8,  // Volume takes 20% of chart height
                    bottom: 0,
                },
            },
        });

        // Update price display with volume
        const lastCandle = offlineData.candlesticks[offlineData.candlesticks.length - 1];
        const lastVolume = offlineData.volumes && offlineData.volumes.length > 0 
            ? offlineData.volumes[offlineData.volumes.length - 1].value 
            : 0;
        updatePriceDisplay(lastCandle, lastVolume);
        
        // Update symbol display
        const symbol = offlineData.symbol || offlineData.metadata?.ticker || 'VN30F1M';
        updateSymbolDisplay(symbol);
        
        // Fit content to show all data without scrolling to future
        setTimeout(() => {
            chart.timeScale().fitContent();
        }, 100);
        
        // Render indicators ONLY if bot strategy is selected (not for manual mode)
        setTimeout(() => {
            const botStrategySelect = document.getElementById('botStrategySelect');
            const hasStrategySelected = botStrategySelect && botStrategySelect.value !== '';

            if (hasStrategySelected && typeof activeIndicators !== 'undefined' && activeIndicators && activeIndicators.length > 0) {
                console.log('📊 Auto-rendering indicators for strategy:', activeIndicators.length);
                if (typeof calculateAndRenderIndicators === 'function') {
                    calculateAndRenderIndicators();
                }
            } else if (!hasStrategySelected) {
                console.log('ℹ️ Skipping auto-render - no strategy selected (manual mode)');
            }
        }, 300);
        
        console.log('✅ Offline data loaded');
        // Add timezone offset for Vietnam (UTC+7) = 7 * 60 * 60 * 1000 = 25200000 ms
        const timezoneOffset = 7 * 60 * 60 * 1000;
        console.log('📅 Data range:', 
            new Date(offlineData.candlesticks[0].time * 1000 + timezoneOffset).toLocaleString('vi-VN', {timeZone: 'UTC'}),
            'to',
            new Date(lastCandle.time * 1000 + timezoneOffset).toLocaleString('vi-VN', {timeZone: 'UTC'})
        );
    } catch (error) {
        console.error('Error loading offline data:', error);
    }
}

// Update data info panel
async function updateDataInfo() {
    const updateFields = (status, fromDate, toDate, candleCount, size, statusColor, filename) => {
        // Update tooltip fields
        document.getElementById('tooltipStatus').textContent = status;
        document.getElementById('tooltipStatus').style.color = statusColor;
        document.getElementById('tooltipStartDate').textContent = fromDate;
        document.getElementById('tooltipEndDate').textContent = toDate;
        document.getElementById('tooltipCandles').textContent = candleCount;
        document.getElementById('tooltipSize').textContent = size;
        
        // Update filename if provided
        const tooltipFileName = document.getElementById('tooltipFileName');
        if (tooltipFileName && filename) {
            tooltipFileName.textContent = filename;
            tooltipFileName.title = filename;
        }
    };
    
    if (!offlineData) {
        updateFields('Chưa có dữ liệu', '--', '--', '0', '0 KB', '#787b86', '--');
        return;
    }
    
    try {
        const firstCandle = offlineData.candlesticks[0];
        const lastCandle = offlineData.candlesticks[offlineData.candlesticks.length - 1];
        const candleCount = offlineData.candlesticks.length;
        
        // Calculate size
        const dataString = JSON.stringify(offlineData);
        const sizeKB = (dataString.length / 1024).toFixed(2);
        const sizeMB = (dataString.length / (1024 * 1024)).toFixed(2);
        const sizeDisplay = sizeMB > 1 ? `${sizeMB} MB` : `${sizeKB} KB`;
        
        // Check if saved in IndexedDB
        let isSaved = false;
        try {
            const savedData = await loadFromIndexedDB();
            isSaved = savedData !== null;
        } catch (e) {
            isSaved = false;
        }
        
        // Format dates
        const fromDate = new Date(firstCandle.time * 1000).toLocaleString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const toDate = new Date(lastCandle.time * 1000).toLocaleString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const status = isSaved ? '✅ Đã lưu' : '⚠️ Chỉ phiên này';
        const statusColor = isSaved ? '#26a69a' : '#f57c00';
        
        // Get filename from metadata
        const filename = offlineData.metadata?.filename || '--';
        
        updateFields(
            status,
            fromDate,
            toDate,
            candleCount.toLocaleString('vi-VN'),
            sizeDisplay,
            statusColor,
            filename
        );
        
        console.log('📊 Data info updated');
    } catch (error) {
        console.error('Error updating data info:', error);
    }
}

// Clear offline data
async function clearOfflineData(silent = false) {
    if (!silent && !confirm('⚠️ Xóa toàn bộ dữ liệu offline?\n\nBạn sẽ cần upload lại file CSV.')) {
        return;
    }
    
    try {
        // Clear from memory
        offlineData = null;
        
        // Clear from IndexedDB
        await clearIndexedDB();
        
        // Clear chart
        if (chartInitialized && candlestickSeries && volumeSeries) {
            candlestickSeries.setData([]);
            volumeSeries.setData([]);
        }
        
        // Update data info
        await updateDataInfo();
        
        if (!silent) {
            alert('✅ Đã xóa dữ liệu offline!');
        }
        console.log('🗑️ Offline data cleared');
    } catch (error) {
        console.error('Error clearing data:', error);
        if (!silent) {
            alert('❌ Lỗi khi xóa dữ liệu!');
        }
    }
}

// Show uploaded files on server
async function showUploadedFiles() {
    try {
        const response = await fetch('/api/list-csv-files');
        const result = await response.json();
        
        if (!result.success || result.files.length === 0) {
            alert('📂 Chưa có file nào trên server!');
            return;
        }
        
        let fileList = '📂 Danh sách file CSV trên server:\n\n';
        result.files.forEach((file, idx) => {
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            const date = new Date(file.modified).toLocaleString('vi-VN');
            fileList += `${idx + 1}. ${file.filename}\n`;
            fileList += `   Kích thước: ${sizeMB} MB\n`;
            fileList += `   Cập nhật: ${date}\n\n`;
        });
        
        const choice = prompt(fileList + 'Nhập số thứ tự file muốn load (hoặc 0 để hủy):');
        
        if (choice && choice !== '0') {
            const index = parseInt(choice) - 1;
            if (index >= 0 && index < result.files.length) {
                await loadServerFile(result.files[index].filename);
            }
        }
    } catch (error) {
        console.error('Error loading file list:', error);
        alert('❌ Lỗi khi load danh sách file!');
    }
}

// Load CSV file from server
async function loadServerFile(filename) {
    try {
        alert('⏳ Đang load file từ server...');
        
        const response = await fetch(`/api/load-csv/${filename}`);
        const result = await response.json();
        
        if (!result.success) {
            alert('❌ Không thể load file: ' + result.error);
            return;
        }
        
        console.log('📥 Loading file from server:', filename);
        const data = parseCSV(result.content);
        
        if (data && data.candlesticks && data.candlesticks.length > 0) {
            // Save to IndexedDB
            offlineData = data;
            await saveToIndexedDB(data);
            
            // Update chart
            candlestickSeries.setData(data.candlesticks);
            if (volumeVisible) {
                if (volumeVisible && volumeSeries) volumeSeries.setData(data.volumes);
            }
            
            // Update price display
            const lastCandle = data.candlesticks[data.candlesticks.length - 1];
            updatePriceDisplay(lastCandle);
            
            // Update symbol display
            updateSymbolDisplay(data.symbol || 'VN30F1M');
            
            // Update data info
            await updateDataInfo();
            
            // Fit content
            setTimeout(() => {
                chart.timeScale().fitContent();
            }, 100);
            
            alert(`✅ Đã load ${data.candlesticks.length} nến từ server!`);
        }
    } catch (error) {
        console.error('Error loading server file:', error);
        alert('❌ Lỗi khi load file từ server!');
    }
}

// Chart scale controls
function zoomIn() {
    if (!chart) return;
    const timeScale = chart.timeScale();
    const logicalRange = timeScale.getVisibleLogicalRange();
    if (logicalRange) {
        const center = (logicalRange.from + logicalRange.to) / 2;
        const newRange = (logicalRange.to - logicalRange.from) * 0.8;
        timeScale.setVisibleLogicalRange({
            from: center - newRange / 2,
            to: center + newRange / 2
        });
        console.log('🔍 Zoomed in');
    }
}

function zoomOut() {
    if (!chart) return;
    const timeScale = chart.timeScale();
    const logicalRange = timeScale.getVisibleLogicalRange();
    if (logicalRange) {
        const center = (logicalRange.from + logicalRange.to) / 2;
        const newRange = (logicalRange.to - logicalRange.from) * 1.25;
        timeScale.setVisibleLogicalRange({
            from: center - newRange / 2,
            to: center + newRange / 2
        });
        console.log('🔍 Zoomed out');
    }
}

function toggleChartType() {
    alert('📊 Chart type switching coming soon!\nSupported types: Candlestick, Line, Area, Bar');
}

function showIndicators() {
    console.log('🔍 showIndicators called');
    
    const panel = document.getElementById('indicatorsDisplayPanel');
    console.log('📋 Panel element:', panel ? 'found' : 'NOT FOUND');
    
    if (!panel) {
        console.error('❌ Indicators panel not found in DOM');
        alert('⚠️ Indicators panel not found. Please refresh the page.');
        return;
    }
    
    // Directly toggle the panel
    const isHidden = panel.classList.contains('hidden');
    console.log('👁️ Panel currently hidden:', isHidden);
    
    if (isHidden) {
        panel.classList.remove('hidden');
        console.log('✅ Panel shown');
        
        // Update content
        if (typeof updateIndicatorsDisplayPanel === 'function') {
            updateIndicatorsDisplayPanel();
        } else {
            const container = document.getElementById('indicatorsPanelContent');
            if (container) {
                if (typeof activeIndicators === 'undefined' || !activeIndicators || activeIndicators.length === 0) {
                    container.innerHTML = '<p class="empty-state">No indicators added yet.<br><br>Go to Strategy Builder → Indicators tab to add indicators first.</p>';
                }
            }
        }
    } else {
        panel.classList.add('hidden');
        console.log('✅ Panel hidden');
    }
}

function fitChartContent() {
    if (!chart) return;
    
    chart.timeScale().fitContent();
    console.log('📊 Auto-fit chart content');
}

// Navigation functions
function scrollChartLeft() {
    if (!chart) return;
    const timeScale = chart.timeScale();
    timeScale.scrollToPosition(-50, false);
}

function scrollChartRight() {
    if (!chart) return;
    const timeScale = chart.timeScale();
    timeScale.scrollToPosition(50, false);
}

function scrollChartStart() {
    if (!chart) return;
    chart.timeScale().scrollToRealTime();
}

function scrollChartEnd() {
    if (!chart) return;
    chart.timeScale().scrollToPosition(-999999, true);
}

// Switch sidebar content
function switchSidebar(panelName) {
    console.log('📍 Switching to:', panelName);
    
    // Navigate to fullscreen workspaces
    if (panelName === 'strategy') {
        console.log('→ Navigating to Strategy Builder');
        window.location.href = '/strategy-builder';
        return;
    }
    if (panelName === 'backtest') {
        console.log('→ Navigating to Backtest');
        window.location.href = '/backtest';
        return;
    }
    if (panelName === 'optimize') {
        console.log('→ Navigating to Optimize');
        window.location.href = '/optimize';
        return;
    }
    
    console.log('→ Switching sidebar panel');
    
    // Remove active class from all header tabs
    document.querySelectorAll('.header-tab').forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all sidebar panels
    document.querySelectorAll('.sidebar-content').forEach(panel => panel.classList.remove('active'));
    
    // Activate selected tab and panel
    if (panelName === 'trading') {
        console.log('  ✓ Activating Manual Trading');
        const tab = document.querySelector('.header-tab:nth-child(1)');
        const panel = document.getElementById('tradingPanel');
        
        if (tab) tab.classList.add('active');
        if (panel) panel.classList.add('active');
        else console.error('  ✗ tradingPanel not found!');
        
    } else if (panelName === 'bot') {
        console.log('  ✓ Activating Bot Trading');
        const tab = document.querySelector('.header-tab:nth-child(2)');
        const panel = document.getElementById('botPanel');
        
        if (tab) tab.classList.add('active');
        if (panel) {
            panel.classList.add('active');
            loadBotStrategies();
            
            // Force update tooltip with cached data
            if (typeof updateDataTooltip === 'function' && cachedTooltipInfo) {
                console.log('🔄 Force updating tooltip with cached data');
                updateDataTooltip(cachedTooltipInfo);
            }
            
            // Auto-load chart data if available
            if (chartInitialized && offlineData && offlineData.candlesticks) {
                console.log('📊 Auto-loading chart data for Bot Trading');
                setTimeout(() => {
                    loadOfflineData();
                }, 100);
            }
        } else {
            console.error('  ✗ botPanel not found!');
        }
    }
    
    console.log('✅ Switch complete');
}

// Run backtest
async function runBacktest() {
    const backtestData = {
        strategy: document.getElementById('strategySelect').value,
        symbol: document.getElementById('btSymbol').value,
        timeframe: document.getElementById('btTimeframe').value,
        startDate: document.getElementById('btStartDate').value,
        endDate: document.getElementById('btEndDate').value,
        capital: parseFloat(document.getElementById('btCapital').value),
        risk: parseFloat(document.getElementById('btRisk').value)
    };

    try {
        // Show loading
        document.getElementById('btTotalTrades').textContent = 'Running...';
        
        const response = await fetch('/api/run-backtest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(backtestData)
        });

        const result = await response.json();
        
        if (result.success) {
            // Display results
            document.getElementById('btTotalTrades').textContent = result.totalTrades;
            document.getElementById('btWinRate').textContent = result.winRate + '%';
            document.getElementById('btProfitFactor').textContent = result.profitFactor;
            document.getElementById('btNetProfit').textContent = formatCurrency(result.netProfit);
            document.getElementById('btMaxDD').textContent = result.maxDrawdown + '%';
            
            alert('Backtest hoàn thành!');
        }
    } catch (error) {
        console.error('Error running backtest:', error);
        alert('Lỗi khi chạy backtest!');
        document.getElementById('btTotalTrades').textContent = '-';
    }
}

// Optimize strategy
function optimizeStrategy() {
    alert('Chức năng tối ưu hóa đang được phát triển!\n\nSẽ sử dụng genetic algorithm để tìm parameters tốt nhất.');
}

// Save settings
async function saveSettings() {
    const settings = {
        mt5Account: document.getElementById('mt5Account').value,
        mt5Server: document.getElementById('mt5Server').value,
        mt5Password: document.getElementById('mt5Password').value,
        apiKey: document.getElementById('apiKey').value,
        apiSecret: document.getElementById('apiSecret').value,
        telegramToken: document.getElementById('telegramToken').value,
        telegramChatId: document.getElementById('telegramChatId').value,
        theme: document.getElementById('themeSelect').value,
        language: document.getElementById('languageSelect').value
    };

    try {
        const response = await fetch('/api/save-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings)
        });

        const result = await response.json();
        if (result.success) {
            alert('Đã lưu cài đặt thành công!');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        alert('Lỗi khi lưu cài đặt!');
    }
}

// Test connection
async function testConnection() {
    try {
        const response = await fetch('/api/test-connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                account: document.getElementById('mt5Account').value,
                server: document.getElementById('mt5Server').value,
                password: document.getElementById('mt5Password').value
            })
        });

        const result = await response.json();
        if (result.success) {
            alert('✅ Kết nối MT5 thành công!\n\nBalance: ' + formatCurrency(result.balance));
        } else {
            alert('❌ Không thể kết nối MT5!\n\nLỗi: ' + result.error);
        }
    } catch (error) {
        console.error('Error testing connection:', error);
        alert('❌ Lỗi khi test connection!');
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

// Handle CSV file upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    console.log('📁 File selected:', file.name);
    
    // Check chart ready
    if (!chartInitialized || !candlestickSeries || !volumeSeries) {
        alert('⚠️ Chart đang khởi tạo...\n\nĐợi 3-5 giây và thử lại!');
        event.target.value = '';
        return;
    }
    
    try {
        // Upload to server
        const formData = new FormData();
        formData.append('file', file);
        
        console.log('📤 Uploading to server...');
        const uploadResponse = await fetch('/api/upload-csv', {
            method: 'POST',
            body: formData
        });
        
        const uploadResult = await uploadResponse.json();
        
        if (!uploadResult.success) {
            let errorMsg = '❌ Lỗi upload CSV:\n\n' + uploadResult.error;
            
            // Add debug info if available
            if (uploadResult.debug_info) {
                const debug = uploadResult.debug_info;
                errorMsg += '\n\n📊 Thông tin debug:';
                
                if (debug.original_columns) {
                    errorMsg += '\n- Cột trong file: ' + debug.original_columns.join(', ');
                }
                if (debug.matched_columns) {
                    errorMsg += '\n- Cột đã nhận: ' + Object.keys(debug.matched_columns).join(', ');
                }
                if (debug.missing_columns && debug.missing_columns.length > 0) {
                    errorMsg += '\n- Cột thiếu: ' + debug.missing_columns.join(', ');
                }
                if (debug.date_sample) {
                    errorMsg += '\n- Mẫu ngày: ' + debug.date_sample;
                }
                if (debug.time_sample) {
                    errorMsg += '\n- Mẫu giờ: ' + debug.time_sample;
                }
                
                console.error('Debug info:', debug);
            }
            
            alert(errorMsg);
            event.target.value = '';
            return;
        }
        
        console.log('✅ Server parsed:', uploadResult.info);
        
        // Convert to chart format
        const candlesticks = uploadResult.data;
        const volumes = uploadResult.data.map(d => ({
            time: d.time,
            value: d.volume,
            color: d.close >= d.open ? 'rgba(0, 150, 136, 0.5)' : 'rgba(255, 82, 82, 0.5)'
        }));
        
        const data = {
            candlesticks: candlesticks,
            volumes: volumes,
            symbol: uploadResult.info.ticker || 'VN30F1M',
            metadata: {
                filename: file.name,
                start_date: uploadResult.info.start_date,
                end_date: uploadResult.info.end_date,
                total_candles: uploadResult.info.total_candles,
                timeframe: uploadResult.info.timeframe
            }
        };
        
        console.log(`✅ Loaded ${candlesticks.length} candles`);
        
        // Save to IndexedDB
        offlineData = data;
        try {
            await saveToIndexedDB(data);
            console.log('💾 Saved to IndexedDB');
        } catch (e) {
            console.error('IndexedDB error:', e);
        }
        
        // Update symbol display
        updateSymbolDisplay(data.symbol || uploadResult.info.ticker || 'VN30F1M');
        
        // Update data info panel
        await updateDataInfo();
        
        // Update chart
        candlestickSeries.setData(data.candlesticks);
        if (volumeVisible) {
            if (volumeVisible && volumeSeries) volumeSeries.setData(data.volumes);
        }
        
        // Update price
        const lastCandle = data.candlesticks[data.candlesticks.length - 1];
        updatePriceDisplay(lastCandle);
        
        // Update symbol
        document.querySelector('.symbol').textContent = data.symbol;
        
        // Update tooltip
        const tooltipStatus = document.getElementById('tooltipStatus');
        const tooltipStartDate = document.getElementById('tooltipStartDate');
        const tooltipEndDate = document.getElementById('tooltipEndDate');
        const tooltipCandles = document.getElementById('tooltipCandles');
        const tooltipSize = document.getElementById('tooltipSize');
        
        if (tooltipStatus) tooltipStatus.innerHTML = '✅ Đã lưu';
        if (tooltipStartDate) tooltipStartDate.textContent = uploadResult.info.start_date.replace(/-/g, '/').split('/').reverse().join('/').replace(/^(\d{2})\/(\d{2})\//, '$2:$1 $1/');
        if (tooltipEndDate) tooltipEndDate.textContent = uploadResult.info.end_date.replace(/-/g, '/').split('/').reverse().join('/').replace(/^(\d{2})\/(\d{2})\//, '$2:$1 $1/');
        if (tooltipCandles) tooltipCandles.textContent = uploadResult.info.total_candles.toLocaleString();
        if (tooltipSize) {
            const sizeInMB = (JSON.stringify(uploadResult.data).length / (1024 * 1024)).toFixed(2);
            tooltipSize.textContent = `${sizeInMB} MB`;
        }
        
        // Fit chart
        setTimeout(() => {
            chart.timeScale().fitContent();
        }, 100);
        
        console.log('✅ Chart updated successfully');
        alert(`✅ ${uploadResult.message}\n\nTicker: ${uploadResult.info.ticker}`);
        
    } catch (error) {
        console.error('❌ Upload error:', error);
        alert('❌ Lỗi khi upload!\n\n' + error.message);
    } finally {
        event.target.value = '';
    }
}

// Parse CSV file
function parseCSV(text) {
    try {
        const lines = text.trim().split('\n');
        if (lines.length < 2) {
            throw new Error('File CSV không có dữ liệu');
        }
        
        const candlesticks = [];
        const volumes = [];
        let symbol = 'VN30F1M';
        
        // Skip header
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            
            const cols = line.split(',');
            if (cols.length < 8) {
                console.warn(`Line ${i}: Invalid format, skipping...`);
                continue;
            }
            
            // Format: Ticker,Date,Time,Open,High,Low,Close,Volume
            symbol = cols[0].trim();
            const date = cols[1].trim();
            const time = cols[2].trim();
            const open = parseFloat(cols[3]);
            const high = parseFloat(cols[4]);
            const low = parseFloat(cols[5]);
            const close = parseFloat(cols[6]);
            const volume = parseFloat(cols[7]);
            
            // Validate numbers
            if (isNaN(open) || isNaN(high) || isNaN(low) || isNaN(close) || isNaN(volume)) {
                console.warn(`Line ${i}: Invalid numbers, skipping...`);
                continue;
            }
            
            // Convert to timestamp
            // Format: 2025-01-02 09:35:00
            const datetime = new Date(date + ' ' + time);
            if (isNaN(datetime.getTime())) {
                console.warn(`Line ${i}: Invalid datetime, skipping...`);
                continue;
            }
            const timestamp = Math.floor(datetime.getTime() / 1000);
            
            candlesticks.push({
                time: timestamp,
                open: open,
                high: high,
                low: low,
                close: close
            });
            
            volumes.push({
                time: timestamp,
                value: volume,
                color: close >= open ? '#26a69a80' : '#ef535080'
            });
        }
        
        if (candlesticks.length === 0) {
            throw new Error('Không có dữ liệu hợp lệ trong file CSV');
        }
        
        console.log(`Parsed ${candlesticks.length} candles from CSV`);
        
        return {
            symbol: symbol,
            candlesticks: candlesticks,
            volumes: volumes
        };
    } catch (error) {
        console.error('Parse CSV error:', error);
        throw error;
    }
}

// Strategy Builder Functions
let entryConditions = [];
let exitConditions = [];

function addCondition(type) {
    const container = type === 'entry' ? 
        document.querySelector('#strategyPanel .condition-builder:nth-of-type(1)') :
        document.querySelector('#strategyPanel .condition-builder:nth-of-type(2)');
    
    const indicator = container.querySelector('.condition-select').value;
    const operator = container.querySelector('.operator-select')?.value || '';
    const value = container.querySelector('.value-input').value;
    
    if (!value && type === 'entry') {
        alert('Vui lòng nhập giá trị!');
        return;
    }
    
    const condition = {
        indicator: indicator,
        operator: operator,
        value: value
    };
    
    if (type === 'entry') {
        entryConditions.push(condition);
        renderConditions('entry');
    } else {
        exitConditions.push(condition);
        renderConditions('exit');
    }
    
    // Clear inputs
    container.querySelector('.value-input').value = '';
}

function renderConditions(type) {
    const conditions = type === 'entry' ? entryConditions : exitConditions;
    const listId = type === 'entry' ? 'entryConditionsList' : 'exitConditionsList';
    const list = document.getElementById(listId);
    
    // Check if element exists (only in strategy builder page)
    if (!list) {
        return;
    }
    
    if (conditions.length === 0) {
        list.innerHTML = '<div class="no-data" style="padding: 10px; text-align: center; color: #787b86;">Chưa có điều kiện</div>';
        return;
    }
    
    list.innerHTML = conditions.map((cond, idx) => `
        <div class="condition-item">
            <span>${cond.indicator} ${cond.operator} ${cond.value}</span>
            <button onclick="removeCondition('${type}', ${idx})">✕</button>
        </div>
    `).join('');
}

function removeCondition(type, index) {
    if (type === 'entry') {
        entryConditions.splice(index, 1);
        renderConditions('entry');
    } else {
        exitConditions.splice(index, 1);
        renderConditions('exit');
    }
}

function saveStrategy() {
    const strategy = {
        name: document.getElementById('strategyName').value || 'Untitled Strategy',
        type: document.getElementById('strategyType').value,
        entryConditions: entryConditions,
        exitConditions: exitConditions,
        positionSize: document.getElementById('positionSize').value,
        maxPositions: document.getElementById('maxPositions').value,
        timestamp: new Date().toISOString()
    };
    
    // Save to localStorage
    let strategies = JSON.parse(localStorage.getItem('strategies') || '[]');
    strategies.push(strategy);
    localStorage.setItem('strategies', JSON.stringify(strategies));
    
    renderStrategiesList();
    alert('✅ Đã lưu strategy: ' + strategy.name);
}

function loadStrategy() {
    renderStrategiesList();
    alert('Chọn strategy từ danh sách bên dưới để load');
}

function renderStrategiesList() {
    const list = document.getElementById('strategiesList');
    
    // Check if element exists (only in strategy builder page)
    if (!list) {
        return;
    }
    
    // Load strategies from server API
    fetch('/api/list-strategies')
        .then(response => response.json())
        .then(data => {
            if (!data.success || !data.strategies || data.strategies.length === 0) {
                list.innerHTML = '<div class="no-data">Chưa có strategy nào</div>';
                return;
            }
            
            list.innerHTML = data.strategies.map((strategy, idx) => `
                <div class="strategy-item" onclick="loadStrategyFromFile('${strategy.filename}', '${strategy.name}')">
                    <div>
                        <div style="font-weight: bold;">${strategy.name}</div>
                        <div style="font-size: 11px; color: #787b86; margin-top: 3px;">
                            ${strategy.description || 'No description'}
                        </div>
                        <div style="font-size: 10px; color: #545862; margin-top: 2px;">
                            📄 ${strategy.filename}
                        </div>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Error loading strategies:', error);
            if (list) {
                list.innerHTML = '<div class="no-data" style="color: #ef5350;">❌ Error loading strategies</div>';
            }
        });
}

// Load strategy from server file
function loadStrategyFromFile(filename, strategyName) {
    console.log('📂 Loading strategy from file:', filename);
    
    fetch(`/api/load-strategy/${filename}`)
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert('❌ Error loading strategy: ' + data.error);
                return;
            }
            
            const strategy = data.strategy;
            
            // Set current strategy tracking (include filename for passing to Strategy Builder)
            currentBotStrategy = strategy;
            currentBotStrategy.filename = filename; // Store filename
            currentBotStrategyName = strategy.name;
            
            console.log('✅ Loaded strategy:', currentBotStrategyName);

            // NOTE: Indicators are NOT auto-loaded from strategy anymore
            // Users should manually add indicators via "Add Indicator" modal
            // Strategy indicators are stored in strategy object but not auto-rendered
            console.log(`ℹ️ Strategy has ${strategy.indicators?.length || 0} indicators defined (not auto-loaded)`);

            // Update UI
            const indicatorCount = strategy.indicators?.length || 0;
            const entryCount = (strategy.entry_conditions?.long?.length || 0) + (strategy.entry_conditions?.short?.length || 0);
            alert(`✅ Đã load strategy: ${strategy.name}\n\n` +
                  `Indicators in strategy: ${indicatorCount} (use Add Indicator button to add manually)\n` +
                  `Entry conditions: ${entryCount}`);
        })
        .catch(error => {
            console.error('❌ Error loading strategy:', error);
            alert('❌ Error loading strategy: ' + error.message);
        });
}

// Note: Bot Trading page loads strategies from server
// Editing and deleting is done in Strategy Builder page

function testStrategy() {
    if (!currentBotStrategy) {
        alert('⚠️ Vui lòng load strategy trước!');
        return;
    }
    
    if (!offlineData || !offlineData.candlesticks || offlineData.candlesticks.length === 0) {
        alert('⚠️ Vui lòng upload CSV data trước!');
        return;
    }
    
    alert(`🚀 Đang test strategy: ${currentBotStrategyName}\n\nSẽ chạy backtest với dữ liệu hiện tại trên chart.`);
    
    // TODO: Implement backtesting
}

// Bot Trading Variables
let botRunning = false;
let currentBotStrategy = null; // Track which strategy is loaded for bot trading
let currentBotStrategyName = null; // Track strategy name for display settings
let botStartTime = null;
let botRuntimeInterval = null;
let botStats = {
    totalTrades: 0,
    wins: 0,
    losses: 0,
    pnl: 0,
    openPositions: 0
};

// Load strategies for bot
async function loadBotStrategies() {
    try {
        const response = await fetch('/api/list-strategies');
        const result = await response.json();
        
        const select = document.getElementById('botStrategySelect');
        const currentValue = select.value; // Remember current selection
        select.innerHTML = '<option value="">-- Chọn strategy --</option>';
        
        if (result.success && result.strategies.length > 0) {
            result.strategies.forEach(strategy => {
                const option = document.createElement('option');
                option.value = strategy.filename;
                option.textContent = strategy.name;
                select.appendChild(option);
            });
            
            // Restore selection if it still exists
            if (currentValue && Array.from(select.options).some(opt => opt.value === currentValue)) {
                select.value = currentValue;
            } else {
                // Clear markers if no strategy selected
                if (candlestickSeries) {
                    candlestickSeries.setMarkers([]);
                    console.log('🗑️ Cleared signals (no strategy selected)');
                }
            }
            
            console.log(`✅ Loaded ${result.strategies.length} strategies for bot`);
            addBotLog(`✅ Loaded ${result.strategies.length} strategies`, 'success');
        } else {
            console.log('⚠️ No strategies found');
            addBotLog('⚠️ Chưa có strategy. Vui lòng tạo ở tab Strategy.', 'warning');
            
            // Clear markers
            if (candlestickSeries) {
                candlestickSeries.setMarkers([]);
            }
        }
    } catch (error) {
        console.error('Error loading strategies:', error);
        addBotLog('❌ Lỗi load strategies: ' + error.message, 'error');
    }
}

// Start Bot
async function startBot() {
    const strategyIdx = document.getElementById('botStrategySelect').value;
    
    if (!strategyIdx) {
        alert('⚠️ Vui lòng chọn strategy!');
        return;
    }
    
    const strategies = JSON.parse(localStorage.getItem('strategies') || '[]');
    const strategy = strategies[strategyIdx];
    
    if (!strategy) {
        alert('❌ Strategy không tồn tại!');
        return;
    }
    
    const symbol = document.getElementById('botSymbol').value;
    const timeframe = document.getElementById('botTimeframe').value;
    const account = document.getElementById('botAccountSelect').value;
    
    // Confirm start
    const confirm = window.confirm(
        `🤖 Khởi động Bot Trading?\n\n` +
        `Strategy: ${strategy.name}\n` +
        `Symbol: ${symbol}\n` +
        `Timeframe: ${timeframe}\n` +
        `Account: ${account.toUpperCase()}`
    );
    
    if (!confirm) return;
    
    // Start bot
    botRunning = true;
    botStartTime = new Date();
    
    // Update UI
    document.getElementById('botStatusDot').classList.add('running');
    document.getElementById('botStatusText').textContent = 'Đang chạy';
    document.getElementById('startBotBtn').style.display = 'none';
    document.getElementById('stopBotBtn').style.display = 'block';
    document.getElementById('startBotBtn').disabled = true;
    
    // Disable inputs
    document.getElementById('botStrategySelect').disabled = true;
    document.getElementById('botAccountSelect').disabled = true;
    document.getElementById('botSymbol').disabled = true;
    document.getElementById('botTimeframe').disabled = true;
    
    // Start runtime counter
    botRuntimeInterval = setInterval(updateBotRuntime, 1000);
    
    // Add logs
    addBotLog('✅ Bot khởi động thành công', 'success');
    addBotLog(`📊 Strategy: ${strategy.name}`, 'success');
    addBotLog(`💱 Symbol: ${symbol} | ${timeframe}`, 'success');
    addBotLog(`🔄 Đang theo dõi thị trường...`, '');
    
    // Simulate bot activity
    startBotSimulation();
    
    // Send to backend
    try {
        const response = await fetch('/api/start-bot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                strategy: strategy,
                symbol: symbol,
                timeframe: timeframe,
                account: account
            })
        });
        
        const result = await response.json();
        if (result.success) {
            addBotLog('🔗 Kết nối server thành công', 'success');
        }
    } catch (error) {
        addBotLog('⚠️ Không kết nối được server, chạy offline mode', 'warning');
    }
}

// Stop Bot
async function stopBot() {
    const confirm = window.confirm('⏹️ Dừng Bot Trading?');
    if (!confirm) return;
    
    botRunning = false;
    
    // Update UI
    document.getElementById('botStatusDot').classList.remove('running');
    document.getElementById('botStatusText').textContent = 'Đã dừng';
    document.getElementById('startBotBtn').style.display = 'block';
    document.getElementById('stopBotBtn').style.display = 'none';
    document.getElementById('startBotBtn').disabled = false;
    
    // Enable inputs
    document.getElementById('botStrategySelect').disabled = false;
    document.getElementById('botAccountSelect').disabled = false;
    document.getElementById('botSymbol').disabled = false;
    document.getElementById('botTimeframe').disabled = false;
    
    // Stop runtime counter
    if (botRuntimeInterval) {
        clearInterval(botRuntimeInterval);
        botRuntimeInterval = null;
    }
    
    addBotLog('⏹️ Bot đã dừng', 'error');
    
    // Send to backend
    try {
        await fetch('/api/stop-bot', { method: 'POST' });
    } catch (error) {
        console.error('Error stopping bot:', error);
    }
}

// Update bot runtime
function updateBotRuntime() {
    if (!botStartTime) return;
    
    const now = new Date();
    const diff = now - botStartTime;
    
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    
    const runtime = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    document.getElementById('botRuntime').textContent = runtime;
}

// Add bot log
function addBotLog(message, type = '') {
    const logsContainer = document.getElementById('botLogsList');
    const time = new Date().toLocaleTimeString('vi-VN');
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.innerHTML = `<span class="log-time">[${time}]</span> ${message}`;
    
    logsContainer.appendChild(logEntry);
    
    // Auto scroll to bottom
    logsContainer.scrollTop = logsContainer.scrollHeight;
    
    // Keep max 100 logs
    while (logsContainer.children.length > 100) {
        logsContainer.removeChild(logsContainer.firstChild);
    }
}

// Update bot stats display
function updateBotStats() {
    document.getElementById('botTotalTrades').textContent = botStats.totalTrades;
    document.getElementById('botWinLoss').textContent = `${botStats.wins} / ${botStats.losses}`;
    document.getElementById('botOpenPositions').textContent = botStats.openPositions;
    
    const pnlElement = document.getElementById('botPnl');
    pnlElement.textContent = formatCurrency(botStats.pnl);
    pnlElement.className = 'pnl-value' + (botStats.pnl < 0 ? ' negative' : '');
}

// Simulate bot activity (for demo)
function startBotSimulation() {
    let simulationInterval = setInterval(() => {
        if (!botRunning) {
            clearInterval(simulationInterval);
            return;
        }
        
        // Random events
        const rand = Math.random();
        
        if (rand < 0.1) {
            // Entry signal
            const side = Math.random() > 0.5 ? 'LONG' : 'SHORT';
            addBotLog(`📈 Entry signal detected: ${side}`, 'success');
            botStats.openPositions++;
            updateBotStats();
        } else if (rand < 0.15 && botStats.openPositions > 0) {
            // Exit signal
            const isWin = Math.random() > 0.6; // 60% win rate
            const pnl = isWin ? Math.random() * 500 + 100 : -(Math.random() * 300 + 50);
            
            botStats.openPositions--;
            botStats.pnl += pnl;
            
            if (isWin) {
                botStats.wins++;
                addBotLog(`✅ Position closed: +${formatCurrency(pnl)}`, 'success');
            } else {
                botStats.losses++;
                addBotLog(`❌ Position closed: ${formatCurrency(pnl)}`, 'error');
            }
            
            updateBotStats();
        } else if (rand < 0.18) {
            // Market update
            addBotLog(`📊 Market scan completed`, '');
        }
        
    }, 5000); // Check every 5 seconds
}

// Auto-load signals when strategy selected
setTimeout(() => {
    const botStrategySelect = document.getElementById("botStrategySelect");
    if (botStrategySelect) {
        botStrategySelect.addEventListener("change", function() {
            loadStrategySignals(this.value);
        });
    }
}, 1000);

// Load strategy signals
async function loadStrategySignals(strategyFilename) {
    if (!strategyFilename) {
        if (candlestickSeries) candlestickSeries.setMarkers([]);
        // Clear indicators
        if (typeof activeIndicators !== 'undefined') {
            activeIndicators = [];
        }
        // Clear chart indicators
        Object.values(indicatorSeries).forEach(series => {
            try {
                chart.removeSeries(series);
            } catch(e) {
                console.warn('Could not remove series:', e);
            }
        });
        indicatorSeries = {};
        return;
    }
    
    if (!offlineData || !offlineData.candlesticks) {
        console.warn("⚠️ No data available for signal generation");
        return;
    }
    
    try {
        console.log(`📊 Loading strategy: ${strategyFilename}`);
        
        // Load strategy config from server
        const response = await fetch(`/api/load-strategy/${strategyFilename}`);
        const result = await response.json();
        
        if (!result.success) {
            console.error('❌ Failed to load strategy:', result.error);
            return;
        }
        
        const strategy = result.strategy;
        currentBotStrategy = strategyFilename; // Track for display overrides
        console.log(`✅ Strategy loaded: ${strategy.name}`);
        console.log(`  - Indicators: ${strategy.indicators.length}`);
        console.log(`  - Long signals: ${strategy.entry_conditions.long.length}`);

        // NOTE: Indicators are NOT auto-loaded from strategy anymore
        // Users should manually add indicators via "Add Indicator" modal
        console.log(`ℹ️ Strategy '${strategy.name}' has ${strategy.indicators?.length || 0} indicators defined (not auto-loaded)`);

        // Check if signal engine is loaded
        if (typeof window.generateStrategySignals === 'undefined') {
            console.error('❌ Signal generation engine not loaded');
            return;
        }
        
        // Clear EMA cache
        Object.keys(window.emaCache).forEach(key => delete window.emaCache[key]);
        console.log('🗑️ Cleared EMA cache');
        
        // Generate signals
        const { buySignals, shortSignals } = window.generateStrategySignals(offlineData.candlesticks, strategy);
        
        console.log(`✅ Generated ${buySignals.length} buy + ${shortSignals.length} short signals`);
        
        // Create markers
        const markers = [];
        const buyColors = ['#26a69a', '#00bcd4', '#03a9f4', '#2196f3', '#3f51b5'];
        const shortColors = ['#ef5350', '#f44336', '#e91e63', '#9c27b0', '#673ab7'];
        
        // Group and add buy signals
        const buyGroups = {};
        buySignals.forEach(sig => {
            if (!buyGroups[sig.signalName]) buyGroups[sig.signalName] = [];
            buyGroups[sig.signalName].push(sig);
        });
        
        Object.keys(buyGroups).forEach((name, idx) => {
            const color = buyColors[idx % buyColors.length];
            buyGroups[name].forEach(sig => {
                // Format time
                const date = new Date(sig.time * 1000);
                const timeStr = date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
                
                markers.push({
                    time: sig.time,
                    position: 'belowBar',
                    color: color,
                    shape: 'arrowUp',
                    text: `${name}\n${sig.price.toFixed(2)} ${timeStr}`,
                    size: 1
                });
            });
            console.log(`  📍 ${name}: ${buyGroups[name].length} signals (${color})`);
        });
        
        // Group and add short signals
        const shortGroups = {};
        shortSignals.forEach(sig => {
            if (!shortGroups[sig.signalName]) shortGroups[sig.signalName] = [];
            shortGroups[sig.signalName].push(sig);
        });
        
        Object.keys(shortGroups).forEach((name, idx) => {
            const color = shortColors[idx % shortColors.length];
            shortGroups[name].forEach(sig => {
                // Format time
                const date = new Date(sig.time * 1000);
                const timeStr = date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
                
                markers.push({
                    time: sig.time,
                    position: 'aboveBar',
                    color: color,
                    shape: 'arrowDown',
                    text: `${name}\n${sig.price.toFixed(2)} ${timeStr}`,
                    size: 1
                });
            });
            console.log(`  📍 ${name}: ${shortGroups[name].length} signals (${color})`);
        });
        
        // Store signal markers globally and update chart
        window.signalMarkers = markers;
        updateChartMarkers();

    } catch (error) {
        console.error("❌ Error loading strategy signals:", error);
    }
}

/**
 * Update chart markers by merging all marker sources
 * (signal markers + position markers)
 */
function updateChartMarkers() {
    if (!candlestickSeries) {
        console.warn('⚠️ Candlestick series not available');
        return;
    }

    const allMarkers = [];

    // Add signal markers (if they exist and toggles are on)
    if (window.signalMarkers && Array.isArray(window.signalMarkers)) {
        window.signalMarkers.forEach(marker => {
            // Filter based on toggle states
            if (marker.position === 'belowBar' && window.showBuySignals !== false) {
                allMarkers.push(marker);
            } else if (marker.position === 'aboveBar' && window.showShortSignals !== false) {
                allMarkers.push(marker);
            }
        });
    }

    // Add position markers (if they exist)
    if (window.positionMarkers && Array.isArray(window.positionMarkers)) {
        allMarkers.push(...window.positionMarkers);
    }

    // Apply all markers to chart
    candlestickSeries.setMarkers(allMarkers);
    console.log(`✅ Applied ${allMarkers.length} total markers to chart (signals: ${window.signalMarkers?.length || 0}, positions: ${window.positionMarkers?.length || 0})`);
}

/**
 * Toggle buy signals visibility on chart
 */
function toggleBuySignals() {
    // Initialize if not set
    if (typeof window.showBuySignals === 'undefined') {
        window.showBuySignals = true;
    }

    // Toggle state
    window.showBuySignals = !window.showBuySignals;

    const btn = document.getElementById('toggleBuySignals');
    if (btn) {
        if (window.showBuySignals) {
            btn.style.opacity = '1';
            btn.style.background = '#26a69a';
            console.log('✅ Buy signals visible');
        } else {
            btn.style.opacity = '0.5';
            btn.style.background = '#434651';
            console.log('❌ Buy signals hidden');
        }
    }

    // Update chart markers
    updateChartMarkers();
}

/**
 * Toggle short signals visibility on chart
 */
function toggleShortSignals() {
    // Initialize if not set
    if (typeof window.showShortSignals === 'undefined') {
        window.showShortSignals = true;
    }

    // Toggle state
    window.showShortSignals = !window.showShortSignals;

    const btn = document.getElementById('toggleShortSignals');
    if (btn) {
        if (window.showShortSignals) {
            btn.style.opacity = '1';
            btn.style.background = '#ef5350';
            console.log('✅ Short signals visible');
        } else {
            btn.style.opacity = '0.5';
            btn.style.background = '#434651';
            console.log('❌ Short signals hidden');
        }
    }

    // Update chart markers
    updateChartMarkers();
}

// Expose all functions globally at the end of file
window.switchSidebar = switchSidebar;
window.handleFileUpload = handleFileUpload;
window.zoomIn = zoomIn;
window.zoomOut = zoomOut;
window.toggleChartType = toggleChartType;
window.showIndicators = showIndicators;
window.fitChartContent = fitChartContent;
window.scrollToStart = scrollToStart;
window.scrollLeft = scrollLeft;
window.scrollRight = scrollRight;
window.scrollToEnd = scrollToEnd;
window.changeTimeframe = changeTimeframe;
window.toggleVolume = toggleVolume;
window.changeDataSource = changeDataSource;
window.updateChartMarkers = updateChartMarkers;
window.toggleBuySignals = toggleBuySignals;
window.toggleShortSignals = toggleShortSignals;
console.log("✅ All functions exposed globally");

// Hash navigation handler
window.addEventListener('hashchange', function() {
    const hash = window.location.hash.substring(1); // Remove #
    console.log('🔗 Hash changed to:', hash);
    if (hash === 'trading' || hash === 'bot') {
        switchSidebar(hash);
    }
});

// Check hash on page load and initialize properly
// This runs AFTER chart initialization
setTimeout(() => {
    const hash = window.location.hash.substring(1);
    console.log('🔗 Initial hash:', hash);
    if (hash === 'trading' || hash === 'bot') {
        switchSidebar(hash);
    } else {
        // Default to trading if no hash
        console.log('🔗 No hash, defaulting to trading');
        switchSidebar('trading');
    }
}, 1000); // Wait for chart initialization


// ==================== INDICATORS DISPLAY PANEL ====================

let indicatorSeries = {}; // Store chart series for indicators

function toggleIndicatorsDisplayPanel() {
    console.log('🔄 toggleIndicatorsDisplayPanel called');
    
    const panel = document.getElementById('indicatorsDisplayPanel');
    if (!panel) {
        console.error('❌ Indicators panel not found in DOM');
        return;
    }
    
    const isHidden = panel.classList.contains('hidden');
    console.log('👁️ Panel state:', isHidden ? 'hidden' : 'visible');
    
    if (isHidden) {
        panel.classList.remove('hidden');
        console.log('✅ Panel shown');
        updateIndicatorsDisplayPanel();
    } else {
        panel.classList.add('hidden');
        console.log('✅ Panel hidden');
    }
}

function updateIndicatorsDisplayPanel() {
    console.log('🔄 updateIndicatorsDisplayPanel called');
    
    const container = document.getElementById('indicatorsPanelContent');
    if (!container) {
        console.error('❌ Indicators panel content container not found');
        return;
    }
    
    console.log('📊 activeIndicators:', typeof activeIndicators !== 'undefined' ? activeIndicators : 'undefined');
    console.log('📊 activeIndicators length:', typeof activeIndicators !== 'undefined' && activeIndicators ? activeIndicators.length : 0);
    
    // Get active indicators from strategy (from strategy-builder.js)
    if (typeof activeIndicators === 'undefined' || !activeIndicators || activeIndicators.length === 0) {
        container.innerHTML = '<p class="empty-state">No indicators added yet.<br><br>Go to Strategy Builder → Indicators tab to add indicators first.</p>';
        console.log('ℹ️ No indicators to display');
        return;
    }
    
    console.log('✅ Rendering', activeIndicators.length, 'indicators');
    
    let html = '';
    activeIndicators.forEach(ind => {
        const paramStr = Object.entries(ind.params || {})
            .map(([k, v]) => `${k}:${v}`)
            .join(', ');
        
        // Initialize display settings if not exist
        if (!ind.display) {
            ind.display = {
                show: true,
                color: getDefaultIndicatorColor(ind.type),
                lineStyle: 'solid',
                lineWidth: 2
            };
        }
        
        html += `
            <div class="indicator-display-item" data-ind-id="${ind.id}">
                <div class="indicator-header">
                    <label class="checkbox-label">
                        <input type="checkbox" ${ind.display.show ? 'checked' : ''} 
                               onchange="toggleIndicatorVisibility('${ind.id}', this.checked)">
                        <strong>${ind.type}</strong> 
                        <small>(${paramStr})</small>
                    </label>
                </div>
                <div class="indicator-settings">
                    <div class="setting-row">
                        <label>Color</label>
                        <input type="color" value="${ind.display.color}" 
                               onchange="updateIndicatorColor('${ind.id}', this.value)">
                    </div>
                    <div class="setting-row">
                        <label>Style</label>
                        <select onchange="updateIndicatorStyle('${ind.id}', this.value)">
                            <option value="solid" ${ind.display.lineStyle === 'solid' ? 'selected' : ''}>Solid</option>
                            <option value="dotted" ${ind.display.lineStyle === 'dotted' ? 'selected' : ''}>Dotted</option>
                            <option value="dashed" ${ind.display.lineStyle === 'dashed' ? 'selected' : ''}>Dashed</option>
                        </select>
                    </div>
                    <div class="setting-row">
                        <label>Width</label>
                        <select onchange="updateIndicatorWidth('${ind.id}', parseInt(this.value))">
                            ${[1,2,3,4,5].map(w => 
                                `<option value="${w}" ${ind.display.lineWidth === w ? 'selected' : ''}>${w}px</option>`
                            ).join('')}
                        </select>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function getDefaultIndicatorColor(type) {
    const colors = {
        'EMA': '#2962FF',
        'SMA': '#FF6D00',
        'WMA': '#9C27B0',
        'RSI': '#9C27B0',
        'MACD': '#00BCD4',
        'BB': '#4CAF50',
        'SuperTrend': '#FF5252',
        'ATR': '#FFA726'
    };
    return colors[type] || '#2962FF';
}


function updateIndicatorColor(indId, color) {
    const indicator = activeIndicators.find(i => i.id === indId);
    if (!indicator) return;
    
    indicator.display.color = color;
    
    // Sync back to strategyConfig if available
    if (typeof strategyConfig !== 'undefined') {
        const strategyInd = strategyConfig.indicators.find(i => i.id === indId);
        if (strategyInd) {
            if (!strategyInd.display) {
                strategyInd.display = {};
            }
            strategyInd.display.color = color;
        }
    }
    
    // Update chart series color
    if (indicatorSeries[indId]) {
        indicatorSeries[indId].applyOptions({ color: color });
    }
    
    // Trigger auto-save
    if (typeof triggerAutoSave === 'function') {
        triggerAutoSave();
    }
}

function updateIndicatorStyle(indId, style) {
    const indicator = activeIndicators.find(i => i.id === indId);
    if (!indicator) return;
    
    indicator.display.lineStyle = style;
    
    // Sync back to strategyConfig if available
    if (typeof strategyConfig !== 'undefined') {
        const strategyInd = strategyConfig.indicators.find(i => i.id === indId);
        if (strategyInd) {
            if (!strategyInd.display) {
                strategyInd.display = {};
            }
            strategyInd.display.lineStyle = style;
        }
    }
    
    const lineStyleMap = {
        'solid': LightweightCharts.LineStyle.Solid,
        'dotted': LightweightCharts.LineStyle.Dotted,
        'dashed': LightweightCharts.LineStyle.Dashed
    };
    
    if (indicatorSeries[indId]) {
        indicatorSeries[indId].applyOptions({ 
            lineStyle: lineStyleMap[style] 
        });
    }
    
    // Trigger auto-save
    if (typeof triggerAutoSave === 'function') {
        triggerAutoSave();
    }
}

function updateIndicatorWidth(indId, width) {
    const indicator = activeIndicators.find(i => i.id === indId);
    if (!indicator) return;
    
    indicator.display.lineWidth = width;
    
    // Sync back to strategyConfig if available
    if (typeof strategyConfig !== 'undefined') {
        const strategyInd = strategyConfig.indicators.find(i => i.id === indId);
        if (strategyInd) {
            if (!strategyInd.display) {
                strategyInd.display = {};
            }
            strategyInd.display.lineWidth = width;
        }
    }
    
    if (indicatorSeries[indId]) {
        indicatorSeries[indId].applyOptions({ lineWidth: width });
    }
    
    // Trigger auto-save
    if (typeof triggerAutoSave === 'function') {
        triggerAutoSave();
    }
}

function calculateAndRenderIndicators() {
    if (!offlineData || !offlineData.candlesticks || offlineData.candlesticks.length === 0) {
        console.log('⚠️ No data available for indicators');
        return;
    }
    
    if (typeof activeIndicators === 'undefined' || !activeIndicators || activeIndicators.length === 0) {
        console.log('⚠️ No active indicators to render');
        return;
    }
    
    // Clear existing indicator series
    Object.values(indicatorSeries).forEach(series => {
        try {
            chart.removeSeries(series);
        } catch(e) {
            console.warn('Could not remove series:', e);
        }
    });
    indicatorSeries = {};
    
    // Prepare data for API
    const candlesData = offlineData.candlesticks.map(c => ({
        time: c.time,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
        volume: c.volume || 0
    }));
    
    // Call API to calculate indicators
    fetch('/calculate_indicators', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            data: candlesData,
            indicators: activeIndicators
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('❌ Failed to calculate indicators:', data.error);
            return;
        }
        
        console.log('✅ Indicators calculated:', Object.keys(data.indicators));
        
        // Render indicators on chart
        activeIndicators.forEach(ind => {
            if (!ind.display || !ind.display.show) return;
            
            const lineStyleMap = {
                'solid': LightweightCharts.LineStyle.Solid,
                'dotted': LightweightCharts.LineStyle.Dotted,
                'dashed': LightweightCharts.LineStyle.Dashed
            };
            
            if (ind.type === 'MACD') {
                // MACD line
                if (data.indicators[ind.id + '_macd']) {
                    const macdSeries = chart.addLineSeries({
                        color: ind.display.color,
                        lineWidth: ind.display.lineWidth,
                        lineStyle: lineStyleMap[ind.display.lineStyle],
                        title: `${ind.type}_MACD`,
                        visible: ind.display.show
                    });
                    macdSeries.setData(data.indicators[ind.id + '_macd']);
                    indicatorSeries[ind.id + '_macd'] = macdSeries;
                }
                
                // Signal line
                if (data.indicators[ind.id + '_signal']) {
                    const signalSeries = chart.addLineSeries({
                        color: '#FF6D00',
                        lineWidth: ind.display.lineWidth,
                        lineStyle: lineStyleMap[ind.display.lineStyle],
                        title: `${ind.type}_Signal`,
                        visible: ind.display.show
                    });
                    signalSeries.setData(data.indicators[ind.id + '_signal']);
                    indicatorSeries[ind.id + '_signal'] = signalSeries;
                }
                
            } else if (ind.type === 'BB') {
                // Upper band
                if (data.indicators[ind.id + '_upper']) {
                    const upperSeries = chart.addLineSeries({
                        color: ind.display.color,
                        lineWidth: ind.display.lineWidth,
                        lineStyle: lineStyleMap[ind.display.lineStyle],
                        title: `${ind.type}_Upper`,
                        visible: ind.display.show
                    });
                    upperSeries.setData(data.indicators[ind.id + '_upper']);
                    indicatorSeries[ind.id + '_upper'] = upperSeries;
                }
                
                // Middle band
                if (data.indicators[ind.id + '_middle']) {
                    const middleSeries = chart.addLineSeries({
                        color: ind.display.color,
                        lineWidth: ind.display.lineWidth,
                        lineStyle: LightweightCharts.LineStyle.Dashed,
                        title: `${ind.type}_Middle`,
                        visible: ind.display.show
                    });
                    middleSeries.setData(data.indicators[ind.id + '_middle']);
                    indicatorSeries[ind.id + '_middle'] = middleSeries;
                }
                
                // Lower band
                if (data.indicators[ind.id + '_lower']) {
                    const lowerSeries = chart.addLineSeries({
                        color: ind.display.color,
                        lineWidth: ind.display.lineWidth,
                        lineStyle: lineStyleMap[ind.display.lineStyle],
                        title: `${ind.type}_Lower`,
                        visible: ind.display.show
                    });
                    lowerSeries.setData(data.indicators[ind.id + '_lower']);
                    indicatorSeries[ind.id + '_lower'] = lowerSeries;
                }
                
            } else {
                // Single line indicators
                if (data.indicators[ind.id]) {
                    const series = chart.addLineSeries({
                        color: ind.display.color,
                        lineWidth: ind.display.lineWidth,
                        lineStyle: lineStyleMap[ind.display.lineStyle],
                        title: `${ind.type}(${Object.values(ind.params).join(',')})`,
                        visible: ind.display.show
                    });
                    series.setData(data.indicators[ind.id]);
                    indicatorSeries[ind.id] = series;
                }
            }
        });
        
        console.log('✅ Indicators rendered on chart');
    })
    .catch(error => {
        console.error('❌ Error calculating indicators:', error);
    });
}

// Export functions for use in other scripts
window.calculateAndRenderIndicators = calculateAndRenderIndicators;
window.updateIndicatorsDisplayPanel = updateIndicatorsDisplayPanel;

// ==================== AUTO-SAVE SYSTEM ====================

let botStrategyDB;
let botAutoSaveTimer = null;
// currentBotStrategy and currentBotStrategyName are already declared at line 1540-1541

// Load display overrides for a specific strategy from localStorage
function loadDisplayOverrides(strategyFilename) {
    try {
        const key = `display_overrides_${strategyFilename}`;
        const saved = localStorage.getItem(key);
        if (saved) {
            const overrides = JSON.parse(saved);
            console.log(`📦 Loaded display overrides for ${strategyFilename}`);
            return overrides;
        }
    } catch (e) {
        console.warn('Error loading display overrides:', e);
    }
    return {};
}

// Save display overrides for current strategy to localStorage
function saveDisplayOverrides() {
    if (!currentBotStrategyName || !activeIndicators) {
        console.log('ℹ️ No bot strategy selected or no indicators to save');
        return;
    }
    
    try {
        const key = `bot_display_${currentBotStrategyName}`;
        const overrides = {};
        
        activeIndicators.forEach(ind => {
            if (ind.display) {
                overrides[ind.id] = {
                    show: ind.display.show,
                    color: ind.display.color,
                    lineStyle: ind.display.lineStyle,
                    lineWidth: ind.display.lineWidth
                };
            }
        });
        
        localStorage.setItem(key, JSON.stringify(overrides));
        console.log(`💾 Saved display settings for bot strategy: ${currentBotStrategyName}`);
    } catch (e) {
        console.error('Error saving display overrides:', e);
    }
}

// Initialize IndexedDB for auto-save (shared with strategy-builder)
function initStrategyDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('StrategyBuilderDB', 3); // Increased version to fix conflict
        
        request.onerror = () => {
            console.error('IndexedDB error:', request.error);
            reject(request.error);
        };
        
        request.onsuccess = () => {
            botStrategyDB = request.result;
            console.log('✅ Strategy DB initialized (chart.js)');
            resolve(botStrategyDB);
        };
        
        request.onupgradeneeded = (event) => {
            botStrategyDB = event.target.result;
            if (!botStrategyDB.objectStoreNames.contains('strategies')) {
                botStrategyDB.createObjectStore('strategies', { keyPath: 'id' });
                console.log('📦 Created strategies object store');
            }
        };
    });
}

// Auto-save - Bot Trading ONLY saves display overrides to localStorage
async function autoSaveStrategy() {
    // Bot Trading page: Only save display preferences per strategy
    // Do NOT touch IndexedDB 'current_strategy' (reserved for Strategy Builder)
    saveDisplayOverrides();
}

// Trigger auto-save with debounce
function triggerAutoSave() {
    clearTimeout(botAutoSaveTimer);
    botAutoSaveTimer = setTimeout(() => {
        autoSaveStrategy();
    }, 1000); // Save after 1 second of no changes
}

// Load auto-saved strategy on page load - Bot Trading does NOT auto-load
// User must select a strategy from dropdown
async function loadAutoSavedStrategy() {
    console.log('ℹ️ Bot Trading: User must select strategy from dropdown');
    // Do nothing - wait for user to select strategy
    return null;
}

// Initialize auto-save system on page load
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🚀 Initializing Bot Trading page');
    await initStrategyDB();
    // Do NOT auto-load strategy - wait for user selection
});

// Export auto-save functions
window.triggerAutoSave = triggerAutoSave;
window.autoSaveStrategy = autoSaveStrategy;

// ==================== ONLINE DATA CONNECTION ====================

/**
 * Show exchange connection dialog
 */
function showExchangeDialog() {
    // Use the modal in header_common.html
    if (typeof openOnlineModal === 'function') {
        openOnlineModal();
    } else {
        const modal = document.getElementById('onlineModal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }
}

/**
 * Close exchange connection dialog
 */
function closeExchangeDialog() {
    if (typeof closeOnlineModal === 'function') {
        closeOnlineModal();
    } else {
        const modal = document.getElementById('onlineModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
}

// Export functions
window.showExchangeDialog = showExchangeDialog;
window.closeExchangeDialog = closeExchangeDialog;

// ==================== SYMBOL SELECTOR ====================

let currentConnectedProfile = null; // Store current profile
let symbolHistory = []; // Store symbol history

/**
 * Toggle symbol dropdown
 */
/**
 * Update symbol display in header
 */
function updateSymbolDisplay(symbol) {
    if (!symbol) return;
    
    console.log('🔄 Updating symbol display to:', symbol);
    
    // Update symbol text in header button
    const currentSymbolText = document.getElementById('currentSymbolText');
    if (currentSymbolText) {
        currentSymbolText.textContent = symbol;
    }
    
    // Update symbol text in price display area
    const symbolElement = document.querySelector('.symbol');
    if (symbolElement) {
        symbolElement.textContent = symbol;
    }
}

function toggleSymbolSelector() {
    // Check if in offline mode
    if (typeof currentDataMode !== 'undefined' && currentDataMode === 'offline') {
        alert('ℹ️ Chức năng đổi symbol chỉ hoạt động ở chế độ Online.\n\nVui lòng chuyển sang Online mode.');
        return;
    }
    
    const dropdown = document.getElementById('symbolDropdown');
    if (!dropdown) return;
    
    if (dropdown.style.display === 'none' || !dropdown.style.display) {
        dropdown.style.display = 'block';
        loadSymbolList();
        // Focus on search input
        setTimeout(() => {
            const searchInput = document.getElementById('symbolSearchInput');
            if (searchInput) searchInput.focus();
        }, 100);
    } else {
        dropdown.style.display = 'none';
    }
}

/**
 * Load symbol list into dropdown
 */
function loadSymbolList() {
    const symbolList = document.getElementById('symbolList');
    if (!symbolList) return;
    
    symbolList.innerHTML = '';
    
    // Check if we have profile tickers (from connected profile)
    if (profileTickers && profileTickers.length > 0) {
        console.log('📊 Using profile tickers:', profileTickers);
        
        // Show profile tickers section
        const profileTitle = document.createElement('div');
        profileTitle.className = 'symbol-item';
        profileTitle.style.fontWeight = '600';
        profileTitle.style.fontSize = '11px';
        profileTitle.style.color = '#787b86';
        profileTitle.style.cursor = 'default';
        profileTitle.textContent = `PROFILE TICKERS (${profileExchange.toUpperCase()})`;
        symbolList.appendChild(profileTitle);
        
        profileTickers.forEach(ticker => {
            const div = createSymbolItem(ticker, profileExchange.toUpperCase(), 'profile');
            symbolList.appendChild(div);
        });
        
        return; // Don't show default symbols when profile is connected
    }
    
    // Load from localStorage (history)
    const saved = localStorage.getItem('symbolHistory');
    if (saved) {
        try {
            symbolHistory = JSON.parse(saved);
        } catch (e) {
            symbolHistory = [];
        }
    }
    
    // Default popular symbols (only shown when no profile connected)
    const defaultSymbols = [
        { symbol: 'XAUUSD', exchange: 'Forex', category: 'popular' },
        { symbol: 'BTCUSDT', exchange: 'Binance', category: 'popular' },
        { symbol: 'ETHUSDT', exchange: 'Binance', category: 'popular' },
        { symbol: 'EURUSD', exchange: 'Forex', category: 'popular' },
        { symbol: 'GBPUSD', exchange: 'Forex', category: 'popular' },
    ];
    
    // History section
    if (symbolHistory.length > 0) {
        const historyTitle = document.createElement('div');
        historyTitle.className = 'symbol-item';
        historyTitle.style.fontWeight = '600';
        historyTitle.style.fontSize = '11px';
        historyTitle.style.color = '#787b86';
        historyTitle.style.cursor = 'default';
        historyTitle.textContent = 'GẦN ĐÂY';
        symbolList.appendChild(historyTitle);
        
        symbolHistory.slice(0, 5).forEach(item => {
            const div = createSymbolItem(item.symbol, item.exchange || 'Unknown', 'recent');
            symbolList.appendChild(div);
        });
        
        const divider = document.createElement('div');
        divider.className = 'symbol-divider';
        symbolList.appendChild(divider);
    }
    
    // Popular symbols
    const popularTitle = document.createElement('div');
    popularTitle.className = 'symbol-item';
    popularTitle.style.fontWeight = '600';
    popularTitle.style.fontSize = '11px';
    popularTitle.style.color = '#787b86';
    popularTitle.style.cursor = 'default';
    popularTitle.textContent = 'PHỔ BIẾN';
    symbolList.appendChild(popularTitle);
    
    defaultSymbols.forEach(item => {
        const div = createSymbolItem(item.symbol, item.exchange, 'popular');
        symbolList.appendChild(div);
    });
}

/**
 * Create symbol item element
 */
function createSymbolItem(symbol, exchange, category) {
    const div = document.createElement('div');
    div.className = 'symbol-item';
    div.innerHTML = `
        <span>
            <span class="symbol-name">${symbol}</span>
            <span class="symbol-exchange">${exchange}</span>
        </span>
    `;
    div.onclick = () => selectSymbol(symbol, exchange);
    return div;
}

/**
 * Select symbol and reload data
 */
async function selectSymbol(symbol, exchange) {
    // Close dropdown
    document.getElementById('symbolDropdown').style.display = 'none';
    
    // Update display
    document.getElementById('currentSymbolText').textContent = symbol;
    document.querySelector('.symbol').textContent = symbol;
    
    // Save to history
    saveSymbolToHistory(symbol, exchange);
    
    // Check if online mode and has connected profile
    const dataSource = localStorage.getItem('dataSource');
    if (dataSource === 'online') {
        const connectionInfo = localStorage.getItem('onlineConnection');
        if (connectionInfo) {
            try {
                const info = JSON.parse(connectionInfo);
                await reloadOnlineData(info.profile, symbol, info.timeframe);
            } catch (e) {
                console.error('Error reloading data:', e);
                alert('❌ Không thể tải dữ liệu!\n\nVui lòng kết nối lại.');
            }
        } else {
            alert('⚠️ Chưa kết nối Exchange!\n\nVui lòng chọn profile trong tooltip Online.');
        }
    } else {
        alert('ℹ️ Chức năng đổi symbol chỉ hoạt động ở chế độ Online.\n\nVui lòng chuyển sang Online mode.');
    }
}

/**
 * Reload online data with new symbol
 */
async function reloadOnlineData(profileName, symbol, timeframe) {
    try {
        console.log('📡 Reloading data:', profileName, symbol, timeframe);
        
        const response = await fetch(`/api/exchange/load-data/${encodeURIComponent(profileName)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                symbol: symbol,
                timeframe: timeframe,
                candles: 1000
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Reloaded!', result.data.length, 'candles');
            
            // Update connection info
            const connectionInfo = {
                profile: profileName,
                exchange: result.exchange,
                symbol: result.symbol,
                timeframe: result.timeframe,
                candles: result.data.length,
                start_date: result.start_date,
                end_date: result.end_date
            };
            localStorage.setItem('onlineConnection', JSON.stringify(connectionInfo));
            
            // Convert and store data
            const candlesticks = result.data.map(d => ({
                time: d.time,
                open: d.open,
                high: d.high,
                low: d.low,
                close: d.close
            }));
            
            const volumes = result.data.map(d => ({
                time: d.time,
                value: d.volume || 0,
                color: d.close >= d.open ? '#26a69a80' : '#ef535080'
            }));
            
            offlineData = {
                candlesticks,
                volumes,
                symbol: result.symbol,
                timeframe: result.timeframe,
                exchange: result.exchange,
                profile: profileName,
                start_date: result.start_date,
                end_date: result.end_date
            };
            
            // Save to IndexedDB
            if (typeof saveToIndexedDB === 'function') {
                await saveToIndexedDB(offlineData);
            }
            
            // Load to chart
            loadOfflineData();
            
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('❌ Reload error:', error);
        alert(`❌ Lỗi tải dữ liệu!\n\n${error.message}`);
    }
}

/**
 * Save symbol to history
 */
function saveSymbolToHistory(symbol, exchange) {
    // Remove if already exists
    symbolHistory = symbolHistory.filter(item => item.symbol !== symbol);
    
    // Add to beginning
    symbolHistory.unshift({ symbol, exchange, timestamp: Date.now() });
    
    // Keep only last 20
    symbolHistory = symbolHistory.slice(0, 20);
    
    // Save to localStorage
    localStorage.setItem('symbolHistory', JSON.stringify(symbolHistory));
}

/**
 * Search symbols
 */
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('symbolSearchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.toUpperCase();
            if (query.length >= 2) {
                // Filter symbol list
                const items = document.querySelectorAll('.symbol-item .symbol-name');
                items.forEach(item => {
                    const parent = item.closest('.symbol-item');
                    if (item.textContent.includes(query)) {
                        parent.style.display = 'flex';
                    } else {
                        parent.style.display = 'none';
                    }
                });
            } else {
                // Show all
                const items = document.querySelectorAll('.symbol-item');
                items.forEach(item => {
                    item.style.display = 'flex';
                });
            }
        });
        
        // Enter to search/add custom symbol
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const symbol = e.target.value.toUpperCase().trim();
                if (symbol) {
                    selectSymbol(symbol, 'Custom');
                }
            }
        });
    }
});

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
    const wrapper = document.querySelector('.symbol-selector-wrapper');
    const dropdown = document.getElementById('symbolDropdown');
    if (wrapper && dropdown && !wrapper.contains(e.target)) {
        dropdown.style.display = 'none';
    }
});

// Export functions
window.toggleSymbolSelector = toggleSymbolSelector;
window.selectSymbol = selectSymbol;

// Store profile tickers globally
let profileTickers = [];
let profileExchange = '';

/**
 * Populate symbol dropdown with tickers from connected profile
 */
window.populateSymbolDropdown = function(tickers, currentSymbol, exchange) {
    console.log('📊 Populating symbol dropdown with profile tickers:', tickers);
    
    // Store globally
    profileTickers = tickers || [];
    profileExchange = exchange || '';
    
    // Update current symbol display
    if (currentSymbol) {
        document.getElementById('currentSymbolText').textContent = currentSymbol;
        document.querySelector('.symbol').textContent = currentSymbol;
    }
    
    // If dropdown is open, reload it
    const dropdown = document.getElementById('symbolDropdown');
    if (dropdown && dropdown.style.display !== 'none') {
        loadSymbolList();
    }
    
    console.log('✅ Symbol dropdown populated with', tickers.length, 'tickers');
};

// ==================== INDICATORS PANEL ====================

let indicatorsVisible = {};

function toggleIndicatorsPanel() {
    const panel = document.getElementById('indicatorsPanel');
    if (!panel) return;

    const isVisible = panel.style.display !== 'none';

    // Close all other panels
    const signalsPanel = document.getElementById('signalsPanel');
    if (signalsPanel) signalsPanel.style.display = 'none';

    const volumeScalePanel = document.getElementById('volumeScalePanel');
    if (volumeScalePanel) volumeScalePanel.style.display = 'none';

    panel.style.display = isVisible ? 'none' : 'block';

    if (!isVisible) {
        updateActiveIndicatorsList();
    }
}

function updateActiveIndicatorsList() {
    const list = document.getElementById('activeIndicatorsList');

    // Get active indicators from window.activeIndicators
    const indicators = window.activeIndicators || [];

    if (indicators.length === 0) {
        list.innerHTML = '<p style="color: #787b86; font-size: 12px; text-align: center; padding: 10px;">No indicators</p>';
        return;
    }

    // Clear and rebuild list
    list.innerHTML = '';

    indicators.forEach((ind, idx) => {
        const visible = indicatorsVisible[ind.id] !== false;
        const indicatorName = `${ind.id} (${ind.type})`;
        const paramText = ind.params ? Object.entries(ind.params).map(([k,v]) => `${k}=${v}`).join(', ') : '';
        const displayName = paramText ? `${indicatorName}: ${paramText}` : indicatorName;

        // Create elements
        const div = document.createElement('div');
        div.style.cssText = `display: flex; align-items: center; gap: 8px; padding: 6px 8px; border-radius: 4px; font-size: 12px; color: #d1d4dc; margin-bottom: 4px; background: ${visible ? '#2a2e39' : '#1e222d'};`;

        // Checkbox
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = visible;
        checkbox.style.cursor = 'pointer';
        checkbox.addEventListener('change', function() {
            toggleIndicatorVisibility(ind.id, this.checked);
        });

        // Indicator name (clickable to edit)
        const nameSpan = document.createElement('span');
        nameSpan.style.cssText = 'flex: 1; cursor: pointer;';
        nameSpan.textContent = displayName;
        nameSpan.title = 'Click để sửa';
        nameSpan.addEventListener('click', function() {
            editChartIndicator(ind.id);
        });

        // Delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.innerHTML = '&times;';
        deleteBtn.title = 'Xóa indicator';
        deleteBtn.style.cssText = 'background: transparent; border: none; color: #787b86; font-size: 18px; cursor: pointer; padding: 0 6px; line-height: 1; transition: color 0.2s;';
        deleteBtn.addEventListener('mouseover', function() { this.style.color = '#ef5350'; });
        deleteBtn.addEventListener('mouseout', function() { this.style.color = '#787b86'; });
        deleteBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            removeChartIndicator(ind.id);
        });

        // Append all elements
        div.appendChild(checkbox);
        div.appendChild(nameSpan);
        div.appendChild(deleteBtn);
        list.appendChild(div);
    });
}

function removeChartIndicator(indicatorId) {
    console.log('🗑️ Removing chart indicator:', indicatorId);

    // Remove from activeIndicators array
    window.activeIndicators = (window.activeIndicators || []).filter(ind => ind.id !== indicatorId);

    // Remove from strategyConfig.indicators (sync with strategy-builder)
    if (typeof strategyConfig !== 'undefined' && strategyConfig.indicators) {
        strategyConfig.indicators = strategyConfig.indicators.filter(ind => ind.id !== indicatorId);
    }

    // Remove from chart
    if (window.indicatorSeries && window.indicatorSeries[indicatorId]) {
        chart.removeSeries(window.indicatorSeries[indicatorId]);
        delete window.indicatorSeries[indicatorId];
    }

    // Remove visibility state
    delete indicatorsVisible[indicatorId];

    // Save to localStorage
    saveIndicatorsToLocalStorage();

    // Update UI
    updateActiveIndicatorsList();
    
    // Sync with strategy-builder if available
    if (typeof renderActiveIndicators === 'function') {
        renderActiveIndicators();
    }

    console.log('✅ Removed chart indicator:', indicatorId);
}

function editChartIndicator(indicatorId) {
    console.log('✏️ Editing chart indicator:', indicatorId);

    // Find the indicator
    const indicator = (window.activeIndicators || []).find(ind => ind.id === indicatorId);
    if (!indicator) {
        console.error('Indicator not found:', indicatorId);
        return;
    }

    // Open modal
    const modal = document.getElementById('indicatorSelectionModal');
    if (!modal) return;

    modal.style.display = 'block';

    // Set indicator type
    const typeSelect = document.getElementById('indicatorTypeSelect');
    if (typeSelect) {
        typeSelect.value = indicator.type;

        // Trigger parameter update
        setTimeout(() => {
            updateIndicatorParams();

            // Fill in parameter values
            if (indicator.params) {
                Object.entries(indicator.params).forEach(([key, value]) => {
                    const input = document.getElementById(`param_${key}`);
                    if (input) {
                        input.value = value;
                    }
                });
            }

            // Fill in display settings
            if (indicator.display) {
                const colorInput = document.getElementById('indicatorColor');
                const styleSelect = document.getElementById('indicatorLineStyle');
                const widthSelect = document.getElementById('indicatorLineWidth');

                if (colorInput && indicator.display.color) colorInput.value = indicator.display.color;
                if (styleSelect && indicator.display.lineStyle) styleSelect.value = indicator.display.lineStyle;
                if (widthSelect && indicator.display.lineWidth) widthSelect.value = indicator.display.lineWidth;
            }
        }, 50);
    }

    // Store the indicator ID being edited
    window.editingIndicatorId = indicatorId;

    console.log('📝 Opened edit mode for:', indicatorId);
}

function toggleIndicatorVisibility(indicatorId, visible) {
    indicatorsVisible[indicatorId] = visible;

    // Update indicator display.show in activeIndicators
    const indicator = (window.activeIndicators || []).find(i => i.id === indicatorId);
    if (indicator && indicator.display) {
        indicator.display.show = visible;
    }

    console.log(`${visible ? '👁️' : '🙈'} Indicator ${indicatorId}: ${visible ? 'visible' : 'hidden'}`);

    // Update the series visibility if chart has the indicator
    if (window.indicatorSeries && window.indicatorSeries[indicatorId]) {
        window.indicatorSeries[indicatorId].applyOptions({
            visible: visible
        });
    }

    // Handle multi-line indicators (MACD, BB, SuperTrend)
    if (window.indicatorSeries) {
        const multiLineKeys = Object.keys(window.indicatorSeries).filter(k => k.startsWith(indicatorId + '_'));
        multiLineKeys.forEach(key => {
            if (window.indicatorSeries[key]) {
                window.indicatorSeries[key].applyOptions({ visible: visible });
            }
        });
    }

    // Save to localStorage
    if (typeof saveIndicatorsToLocalStorage === 'function') {
        saveIndicatorsToLocalStorage();
    }
}

function hideAllIndicators() {
    const indicators = window.activeIndicators || [];
    indicators.forEach(ind => {
        indicatorsVisible[ind.id] = false;
        // Update display.show
        if (ind.display) {
            ind.display.show = false;
        }
        // Hide main series
        if (window.indicatorSeries && window.indicatorSeries[ind.id]) {
            window.indicatorSeries[ind.id].applyOptions({
                visible: false
            });
        }
        // Hide multi-line series (MACD, BB, SuperTrend)
        if (window.indicatorSeries) {
            const multiLineKeys = Object.keys(window.indicatorSeries).filter(k => k.startsWith(ind.id + '_'));
            multiLineKeys.forEach(key => {
                if (window.indicatorSeries[key]) {
                    window.indicatorSeries[key].applyOptions({ visible: false });
                }
            });
        }
    });
    // Save to localStorage
    if (typeof saveIndicatorsToLocalStorage === 'function') {
        saveIndicatorsToLocalStorage();
    }
    // Update UI immediately
    updateActiveIndicatorsList();
    console.log('🙈 All indicators hidden');
}

function showAllIndicators() {
    const indicators = window.activeIndicators || [];
    indicators.forEach(ind => {
        indicatorsVisible[ind.id] = true;
        // Update display.show
        if (ind.display) {
            ind.display.show = true;
        }
        // Show main series
        if (window.indicatorSeries && window.indicatorSeries[ind.id]) {
            window.indicatorSeries[ind.id].applyOptions({
                visible: true
            });
        }
        // Show multi-line series (MACD, BB, SuperTrend)
        if (window.indicatorSeries) {
            const multiLineKeys = Object.keys(window.indicatorSeries).filter(k => k.startsWith(ind.id + '_'));
            multiLineKeys.forEach(key => {
                if (window.indicatorSeries[key]) {
                    window.indicatorSeries[key].applyOptions({ visible: true });
                }
            });
        }
    });
    // Save to localStorage
    if (typeof saveIndicatorsToLocalStorage === 'function') {
        saveIndicatorsToLocalStorage();
    }
    // Update UI immediately
    updateActiveIndicatorsList();
    console.log('👁️ All indicators shown');
}

// ==================== SIGNALS PANEL ====================

let signalsVisible = {
    buy: true,
    sell: true,
    short: true,
    cover: true
};

function toggleSignalsPanel() {
    const panel = document.getElementById('signalsPanel');
    if (!panel) return;

    const isVisible = panel.style.display !== 'none';

    // Close all other panels
    const indicatorsPanel = document.getElementById('indicatorsPanel');
    if (indicatorsPanel) indicatorsPanel.style.display = 'none';

    const volumeScalePanel = document.getElementById('volumeScalePanel');
    if (volumeScalePanel) volumeScalePanel.style.display = 'none';

    panel.style.display = isVisible ? 'none' : 'block';
}

function toggleSignalVisibility(signalType, visible) {
    signalsVisible[signalType] = visible;
    
    // Update checkbox state
    const checkbox = document.getElementById(`show${signalType.charAt(0).toUpperCase() + signalType.slice(1)}Signals`);
    if (checkbox) {
        checkbox.checked = visible;
    }
    
    // TODO: Actually hide/show signals on chart
    console.log(`${visible ? '👁️' : '🙈'} ${signalType} signals: ${visible ? 'visible' : 'hidden'}`);
    
    // Update markers visibility
    if (window.signalMarkers && window.signalMarkers[signalType]) {
        window.signalMarkers[signalType].forEach(marker => {
            marker.visible = visible;
        });
        // Redraw markers
        if (typeof updateSignalMarkers === 'function') {
            updateSignalMarkers();
        }
    }
}

function hideAllSignals() {
    Object.keys(signalsVisible).forEach(type => {
        signalsVisible[type] = false;
        toggleSignalVisibility(type, false);
    });
    console.log('🙈 All signals hidden');
}

function showAllSignals() {
    Object.keys(signalsVisible).forEach(type => {
        signalsVisible[type] = true;
        toggleSignalVisibility(type, true);
    });
    console.log('👁️ All signals shown');
}

// ==================== VOLUME SCALE ====================
// Volume fixed at 30% height

// Close panels when clicking outside
document.addEventListener('click', function(e) {
    const indicatorsBtn = document.getElementById('indicatorsBtn');
    const indicatorsPanel = document.getElementById('indicatorsPanel');
    const signalsBtn = document.getElementById('signalsBtn');
    const signalsPanel = document.getElementById('signalsPanel');
    
    // Close indicators panel
    if (indicatorsPanel && indicatorsBtn) {
        if (!indicatorsBtn.contains(e.target) && !indicatorsPanel.contains(e.target)) {
            indicatorsPanel.style.display = 'none';
        }
    }
    
    // Close signals panel
    if (signalsPanel && signalsBtn) {
        if (!signalsBtn.contains(e.target) && !signalsPanel.contains(e.target)) {
            signalsPanel.style.display = 'none';
        }
    }
});

// ==================== INDICATOR SELECTION MODAL ====================

function showIndicatorModal() {
    const modal = document.getElementById('indicatorSelectionModal');
    if (modal) {
        modal.style.display = 'block';

        // Reset form
        const typeSelect = document.getElementById('indicatorTypeSelect');
        const paramsSection = document.getElementById('indicatorParamsSection');
        const displaySection = document.getElementById('indicatorDisplaySection');
        const paramsContainer = document.getElementById('indicatorParamsContainer');

        if (typeSelect) typeSelect.value = '';
        if (paramsSection) paramsSection.style.display = 'none';
        if (displaySection) displaySection.style.display = 'none';
        if (paramsContainer) paramsContainer.innerHTML = '';
    }
}

function closeIndicatorModal() {
    console.log('🔄 closeIndicatorModal called');
    const modal = document.getElementById('indicatorSelectionModal');
    if (modal) {
        modal.style.display = 'none';
        console.log('✅ Modal closed');
    } else {
        console.error('❌ Modal element not found');
    }
}

function updateIndicatorParams() {
    const type = document.getElementById('indicatorTypeSelect').value;
    const paramsSection = document.getElementById('indicatorParamsSection');
    const displaySection = document.getElementById('indicatorDisplaySection');
    const paramsContainer = document.getElementById('indicatorParamsContainer');

    if (!type) {
        paramsSection.style.display = 'none';
        displaySection.style.display = 'none';
        return;
    }

    // Show display section
    displaySection.style.display = 'block';

    // Define parameters for each indicator type
    const paramConfigs = {
        'EMA': [{ name: 'period', label: 'Period', default: 20, min: 1, max: 500 }],
        'SMA': [{ name: 'period', label: 'Period', default: 20, min: 1, max: 500 }],
        'WMA': [{ name: 'period', label: 'Period', default: 20, min: 1, max: 500 }],
        'RSI': [{ name: 'period', label: 'Period', default: 14, min: 2, max: 100 }],
        'MACD': [
            { name: 'fastPeriod', label: 'Fast Period', default: 12, min: 1, max: 100 },
            { name: 'slowPeriod', label: 'Slow Period', default: 26, min: 1, max: 100 },
            { name: 'signalPeriod', label: 'Signal Period', default: 9, min: 1, max: 100 }
        ],
        'BollingerBands': [
            { name: 'period', label: 'Period', default: 20, min: 1, max: 100 },
            { name: 'deviation', label: 'Std Deviation', default: 2, min: 0.1, max: 5, step: 0.1 }
        ],
        'ATR': [{ name: 'period', label: 'Period', default: 14, min: 1, max: 100 }],
        'Stochastic': [
            { name: 'kPeriod', label: 'K Period', default: 14, min: 1, max: 100 },
            { name: 'dPeriod', label: 'D Period', default: 3, min: 1, max: 100 }
        ],
        'ADX': [{ name: 'period', label: 'Period', default: 14, min: 1, max: 100 }],
        'CCI': [{ name: 'period', label: 'Period', default: 20, min: 1, max: 100 }],
        'ROC': [{ name: 'period', label: 'Period', default: 12, min: 1, max: 100 }],
        'MFI': [{ name: 'period', label: 'Period', default: 14, min: 1, max: 100 }]
    };

    const params = paramConfigs[type] || [];

    if (params.length > 0) {
        paramsSection.style.display = 'block';

        let html = '';
        params.forEach(param => {
            const step = param.step || 1;
            html += `
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-size: 12px; color: #787b86; margin-bottom: 5px;">${param.label}</label>
                    <input
                        type="number"
                        id="param_${param.name}"
                        value="${param.default}"
                        min="${param.min}"
                        max="${param.max}"
                        step="${step}"
                        style="width: 100%; padding: 8px; background: #131722; border: 1px solid #2a2e39; border-radius: 4px; color: #d1d4dc; font-size: 13px;">
                </div>
            `;
        });

        paramsContainer.innerHTML = html;
    } else {
        paramsSection.style.display = 'none';
        paramsContainer.innerHTML = '';
    }
}

function addSelectedIndicator() {
    const type = document.getElementById('indicatorTypeSelect').value;

    if (!type) {
        alert('⚠️ Please select an indicator type');
        return;
    }

    // Collect parameters
    const params = {};
    const paramInputs = document.querySelectorAll('#indicatorParamsContainer input[type="number"]');
    paramInputs.forEach(input => {
        const paramName = input.id.replace('param_', '');
        params[paramName] = parseFloat(input.value);
    });

    // Collect display settings
    const display = {
        show: true,
        color: document.getElementById('indicatorColor').value,
        lineStyle: document.getElementById('indicatorLineStyle').value,
        lineWidth: parseInt(document.getElementById('indicatorLineWidth').value)
    };

    // Initialize activeIndicators if needed
    if (typeof window.activeIndicators === 'undefined') {
        window.activeIndicators = [];
    }

    // Check if we're editing an existing indicator
    if (window.editingIndicatorId) {
        // Find and update existing indicator
        const index = window.activeIndicators.findIndex(ind => ind.id === window.editingIndicatorId);
        if (index !== -1) {
            // Keep the same ID but update everything else
            window.activeIndicators[index] = {
                id: window.editingIndicatorId,
                type: type,
                params: params,
                display: display
            };
            console.log('✅ Updated indicator:', window.activeIndicators[index]);
            alert(`✅ Updated ${type} indicator`);
        }

        // Remove old series from chart
        if (window.indicatorSeries && window.indicatorSeries[window.editingIndicatorId]) {
            chart.removeSeries(window.indicatorSeries[window.editingIndicatorId]);
            delete window.indicatorSeries[window.editingIndicatorId];
        }

        // Clear edit mode
        delete window.editingIndicatorId;
    } else {
        // Create new indicator
        const indicator = {
            id: `${type.toLowerCase()}_${Date.now()}`,
            type: type,
            params: params,
            display: display
        };

        // Add to activeIndicators
        window.activeIndicators.push(indicator);

        console.log('✅ Added indicator:', indicator);
        alert(`✅ Added ${type} indicator`);
    }

    // Save to localStorage
    saveIndicatorsToLocalStorage();
    
    // Sync with strategyConfig.indicators (for strategy-builder)
    if (typeof strategyConfig !== 'undefined') {
        strategyConfig.indicators = window.activeIndicators.map(ind => ({...ind}));
        console.log('🔄 Synced indicators to strategyConfig');
    }

    // Render indicator on chart if data is available
    if (typeof window.offlineData !== 'undefined' && window.offlineData && window.offlineData.candlesticks) {
        if (typeof calculateAndRenderIndicators === 'function') {
            setTimeout(() => calculateAndRenderIndicators(), 100);
        }
    }

    // Update indicators panel if open
    if (typeof updateActiveIndicatorsList === 'function') {
        updateActiveIndicatorsList();
    }
    
    // Sync with strategy-builder if available
    if (typeof renderActiveIndicators === 'function') {
        renderActiveIndicators();
    }

    // Close modal
    document.getElementById('indicatorSelectionModal').style.display = 'none';
}

function saveIndicatorsToLocalStorage() {
    try {
        const indicators = window.activeIndicators || [];
        localStorage.setItem('userSelectedIndicators', JSON.stringify(indicators));
        console.log('💾 Saved indicators to localStorage:', indicators.length);
    } catch (error) {
        console.error('Failed to save indicators:', error);
    }
}

function loadIndicatorsFromLocalStorage() {
    try {
        const saved = localStorage.getItem('userSelectedIndicators');
        if (saved) {
            window.activeIndicators = JSON.parse(saved);
            console.log('✅ Loaded indicators from localStorage:', window.activeIndicators.length);
        }
    } catch (error) {
        console.error('Failed to load indicators:', error);
    }
}

// Load indicators on page load (but don't render yet - wait for data)
document.addEventListener('DOMContentLoaded', function() {
    loadIndicatorsFromLocalStorage();
});

// Expose functions globally
window.showIndicatorModal = showIndicatorModal;
window.closeIndicatorModal = closeIndicatorModal;
window.updateIndicatorParams = updateIndicatorParams;
window.addSelectedIndicator = addSelectedIndicator;
window.editChartIndicator = editChartIndicator;
window.removeChartIndicator = removeChartIndicator;
window.saveIndicatorsToLocalStorage = saveIndicatorsToLocalStorage;
window.loadIndicatorsFromLocalStorage = loadIndicatorsFromLocalStorage;
window.toggleIndicatorsPanel = toggleIndicatorsPanel;
window.toggleIndicatorVisibility = toggleIndicatorVisibility;
window.hideAllIndicators = hideAllIndicators;
window.showAllIndicators = showAllIndicators;
window.toggleSignalsPanel = toggleSignalsPanel;
window.toggleSignalVisibility = toggleSignalVisibility;
window.hideAllSignals = hideAllSignals;
window.showAllSignals = showAllSignals;
window.updateActiveIndicatorsList = updateActiveIndicatorsList;

