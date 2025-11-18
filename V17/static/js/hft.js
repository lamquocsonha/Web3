// HFT Trading Module
let isRunning = false;
let isMarketDataRunning = false;
let orderCounter = 0;
let tickCounter = 0;
let startTime = null;
let uptimeInterval = null;
let mockInterval = null;
let marketDataInterval = null;
let currentFilter = 'all';

// Market Data State
let lastPrice = 1873.45;
let marketTicks = [];

// Statistics
let stats = {
    totalOrders: 0,
    filledOrders: 0,
    rejectedOrders: 0,
    totalLatency: 0,
    totalPnL: 0,
    winningTrades: 0,
    losingTrades: 0,
    bestTrade: 0,
    worstTrade: 0,
    slippage: 0,
    ordersPerSecond: 0
};

// Chart
let chart = null;
let chartData = {
    latency: { labels: [], data: [] },
    pnl: { labels: [], data: [] },
    orderflow: { labels: ['BUY', 'SELL', 'PARTIAL', 'REJECTED', 'CANCELLED'], data: [0, 0, 0, 0, 0] }
};
let currentChartType = 'latency';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    initChart();
});

function setupEventListeners() {
    document.getElementById('btnMockData').addEventListener('click', startMockData);
    document.getElementById('btnStart').addEventListener('click', startTrading);
    document.getElementById('btnStop').addEventListener('click', stopTrading);
    document.getElementById('btnExport').addEventListener('click', exportLog);
    document.getElementById('btnClear').addEventListener('click', clearTerminal);
    
    // Filter radio buttons
    document.querySelectorAll('input[name="filter"]').forEach(radio => {
        radio.addEventListener('change', function() {
            currentFilter = this.value;
            applyFilter();
        });
    });
    
    // Chart tabs
    document.querySelectorAll('.chart-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            currentChartType = this.dataset.chart;
            updateChart();
        });
    });
}

function startMockData() {
    if (isMarketDataRunning) {
        console.log('Market data already running');
        return;
    }
    
    isMarketDataRunning = true;
    tickCounter = 0;
    
    // Tạo 100 ticks ngay lập tức
    console.log('🎯 Generating 100 market ticks...');
    for (let i = 0; i < 100; i++) {
        setTimeout(() => {
            generateMarketTick();
        }, i * 30); // Stagger by 30ms
    }
    
    // Sau đó chạy market data live
    setTimeout(() => {
        startLiveMarketData();
        console.log('✅ Live market data started');
    }, 3000);
}

function startLiveMarketData() {
    if (marketDataInterval) {
        clearInterval(marketDataInterval);
    }
    
    // Generate tick mỗi 200-500ms
    function scheduleNextTick() {
        const delay = Math.random() * 300 + 200; // 200-500ms
        marketDataInterval = setTimeout(() => {
            generateMarketTick();
            if (isMarketDataRunning) {
                scheduleNextTick();
            }
        }, delay);
    }
    
    scheduleNextTick();
}

function generateMarketTick() {
    const now = new Date();
    const time = now.toLocaleTimeString('en-GB', { hour12: false }) + '.' + String(now.getMilliseconds()).padStart(3, '0');
    
    // Simulate price movement
    const change = (Math.random() - 0.5) * 0.5; // -0.25 to +0.25
    lastPrice = lastPrice + change;
    const price = lastPrice.toFixed(2);
    
    // Random volume
    const volume = (Math.random() * 5 + 0.5).toFixed(2);
    
    // Random side
    const side = Math.random() > 0.5 ? 'BUY' : 'SELL';
    
    // Add to market data display
    addTickToMarketData(time, price, volume, side);
    
    tickCounter++;
}

function addTickToMarketData(time, price, volume, side) {
    const tbody = document.getElementById('marketDataBody');
    
    // Remove empty message
    const emptyRow = tbody.querySelector('.terminal-empty');
    if (emptyRow) emptyRow.remove();
    
    const row = tbody.insertRow(0);
    
    // Time
    row.insertCell(0).textContent = time;
    
    // Price
    const priceCell = row.insertCell(1);
    priceCell.textContent = price;
    priceCell.style.fontWeight = '600';
    
    // Volume
    row.insertCell(2).textContent = volume;
    
    // Side
    const sideCell = row.insertCell(3);
    sideCell.innerHTML = `<span class="order-type ${side.toLowerCase()}">${side}</span>`;
    
    // Limit to 10 rows (show only recent ticks)
    if (tbody.rows.length > 10) {
        tbody.deleteRow(tbody.rows.length - 1);
    }
    
    // Scroll to top
    const marketDataContent = document.getElementById('marketDataContent');
    marketDataContent.scrollTop = 0;
}

function startTrading() {
    if (isRunning) return;
    
    isRunning = true;
    startTime = Date.now();
    
    // Update UI
    document.getElementById('btnStart').disabled = true;
    document.getElementById('btnStop').disabled = false;
    document.getElementById('hftStatus').textContent = 'RUNNING';
    document.getElementById('hftStatus').className = 'status-value running';
    document.getElementById('connectionStatus').textContent = 'CONNECTED';
    document.getElementById('connectionStatus').className = 'status-value connected';
    document.getElementById('serverPing').textContent = '8ms';
    
    // Start uptime counter
    uptimeInterval = setInterval(updateUptime, 1000);
    
    // Start mock order generator
    startMockOrders();
    
    // Sound notification
    playSound('start');
}

function stopTrading() {
    if (!isRunning) return;
    
    isRunning = false;
    
    // Update UI
    document.getElementById('btnStart').disabled = false;
    document.getElementById('btnStop').disabled = true;
    document.getElementById('hftStatus').textContent = 'STOPPED';
    document.getElementById('hftStatus').className = 'status-value stopped';
    document.getElementById('connectionStatus').textContent = 'DISCONNECTED';
    document.getElementById('connectionStatus').className = 'status-value disconnected';
    document.getElementById('serverPing').textContent = '--';
    
    // Stop timers
    clearInterval(uptimeInterval);
    clearInterval(mockInterval);
    
    // Sound notification
    playSound('stop');
}

function startMockOrders() {
    // Generate orders at random intervals (20-200ms) for faster demo
    function scheduleNextOrder() {
        if (!isRunning) return;

        const delay = Math.random() * 180 + 20; // 20-200ms (faster than before)
        mockInterval = setTimeout(() => {
            // 20% chance to generate burst of 2-4 orders at once
            if (Math.random() < 0.2) {
                const burstSize = Math.floor(Math.random() * 3) + 2; // 2-4 orders
                for (let i = 0; i < burstSize; i++) {
                    setTimeout(() => generateMockOrder(), i * 10); // Stagger by 10ms
                }
            } else {
                generateMockOrder();
            }
            scheduleNextOrder();
        }, delay);
    }

    scheduleNextOrder();
}

function generateMockOrder() {
    const now = new Date();
    const timestamp = now.toLocaleTimeString('en-GB', { hour12: false }) + '.' + String(now.getMilliseconds()).padStart(3, '0');
    
    const types = ['BUY', 'SELL'];
    const statuses = ['FILLED', 'FILLED', 'FILLED', 'PARTIAL', 'REJECTED']; // Weighted towards FILLED
    
    const type = types[Math.floor(Math.random() * types.length)];
    const price = (1873 + Math.random() * 2 - 1).toFixed(2);
    const qty = (Math.random() * 0.3 + 0.1).toFixed(1);
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    const latency = Math.floor(Math.random() * 40 + 8); // 8-48ms
    
    let pnl = null;
    if (status === 'FILLED') {
        pnl = (Math.random() * 20 - 5).toFixed(2); // -5 to +15
    }
    
    // Add to terminal
    addOrderToTerminal(timestamp, type, price, qty, status, latency, pnl);
    
    // Update stats
    updateStatistics(type, status, latency, pnl);
    
    // Update charts
    updateChartData(latency, pnl);
    
    // Check risk limits
    checkRiskLimits();
    
    // Sound alert
    if (status === 'FILLED' && pnl && parseFloat(pnl) > 5) {
        playSound('profit');
    } else if (status === 'REJECTED') {
        playSound('error');
    }
}

function addOrderToTerminal(timestamp, type, price, qty, status, latency, pnl) {
    const tbody = document.getElementById('tradesBody');
    
    // Remove empty message
    const emptyRow = tbody.querySelector('.terminal-empty');
    if (emptyRow) emptyRow.remove();
    
    const row = tbody.insertRow(0);
    row.dataset.filter = status.toLowerCase();
    
    orderCounter++;
    
    // Order #
    const numCell = row.insertCell(0);
    numCell.textContent = orderCounter;
    numCell.style.color = '#787b86';
    numCell.style.fontSize = '11px';
    
    // Time (short format)
    const timeCell = row.insertCell(1);
    timeCell.textContent = timestamp;
    timeCell.style.fontSize = '11px';
    
    // Side
    const typeCell = row.insertCell(2);
    typeCell.innerHTML = `<span class="order-type ${type.toLowerCase()}">${type}</span>`;
    
    // Price
    const priceCell = row.insertCell(3);
    priceCell.textContent = price;
    priceCell.style.fontWeight = '600';
    
    // Qty
    row.insertCell(4).textContent = qty;
    
    // Status
    const statusCell = row.insertCell(5);
    statusCell.innerHTML = `<span class="order-status ${status.toLowerCase()}">${status}</span>`;
    
    // PnL
    const pnlCell = row.insertCell(6);
    if (pnl !== null) {
        const pnlValue = parseFloat(pnl);
        const pnlClass = pnlValue > 0 ? 'positive' : 'negative';
        const pnlSign = pnlValue > 0 ? '+' : '';
        pnlCell.innerHTML = `<span class="stat-value ${pnlClass}">${pnlSign}$${pnl}</span>`;
    } else {
        pnlCell.textContent = '--';
    }
    
    // Auto-scroll
    if (document.getElementById('autoScroll').checked) {
        const tradesContent = document.getElementById('tradesContent');
        tradesContent.scrollTop = 0;
    }
    
    // Apply current filter
    if (currentFilter !== 'all') {
        row.style.display = (currentFilter === 'filled' && status === 'FILLED') ||
                           (currentFilter === 'errors' && status === 'REJECTED') ? '' : 'none';
    }
    
    // Limit rows
    if (tbody.rows.length > 500) {
        tbody.deleteRow(tbody.rows.length - 1);
    }
}

function updateStatistics(type, status, latency, pnl) {
    stats.totalOrders++;
    
    if (status === 'FILLED') {
        stats.filledOrders++;
    } else if (status === 'REJECTED') {
        stats.rejectedOrders++;
    }
    
    stats.totalLatency += latency;
    
    if (pnl !== null) {
        const pnlValue = parseFloat(pnl);
        stats.totalPnL += pnlValue;
        
        if (pnlValue > 0) {
            stats.winningTrades++;
            if (pnlValue > stats.bestTrade) stats.bestTrade = pnlValue;
        } else if (pnlValue < 0) {
            stats.losingTrades++;
            if (pnlValue < stats.worstTrade) stats.worstTrade = pnlValue;
        }
    }
    
    // Update chart data
    if (type === 'BUY' && status === 'FILLED') chartData.orderflow.data[0]++;
    if (type === 'SELL' && status === 'FILLED') chartData.orderflow.data[1]++;
    if (status === 'PARTIAL') chartData.orderflow.data[2]++;
    if (status === 'REJECTED') chartData.orderflow.data[3]++;
    
    // Calculate orders per second
    const elapsedSeconds = (Date.now() - startTime) / 1000;
    stats.ordersPerSecond = (stats.totalOrders / elapsedSeconds).toFixed(1);
    
    // Update UI
    document.getElementById('statOrders').textContent = stats.totalOrders.toLocaleString();
    
    const fillRate = ((stats.filledOrders / stats.totalOrders) * 100).toFixed(1);
    document.getElementById('statFillRate').textContent = fillRate + '%';
    
    const avgLatency = (stats.totalLatency / stats.totalOrders).toFixed(1);
    document.getElementById('statLatency').textContent = avgLatency + 'ms';
    
    const pnlElem = document.getElementById('statPnL');
    pnlElem.textContent = (stats.totalPnL >= 0 ? '+' : '') + '$' + stats.totalPnL.toFixed(2);
    pnlElem.className = 'stat-value ' + (stats.totalPnL >= 0 ? 'positive' : 'negative');

    document.getElementById('statOrdersPerSec').textContent = stats.ordersPerSecond;
    
    // Update Win Rate
    const totalTrades = stats.winningTrades + stats.losingTrades;
    if (totalTrades > 0) {
        const winRate = ((stats.winningTrades / totalTrades) * 100).toFixed(1);
        document.getElementById('statWinRate').textContent = winRate + '%';
    }
    
    // Update Best/Worst Trade
    if (stats.bestTrade > 0) {
        document.getElementById('statBestTrade').textContent = '+$' + stats.bestTrade.toFixed(2);
    }
    if (stats.worstTrade < 0) {
        document.getElementById('statWorstTrade').textContent = '$' + stats.worstTrade.toFixed(2);
    }
}

function updateChartData(latency, pnl) {
    const now = new Date().toLocaleTimeString('en-GB', { hour12: false });

    // Add latency data
    chartData.latency.labels.push(now);
    chartData.latency.data.push(latency);
    if (chartData.latency.data.length > 50) {
        chartData.latency.labels.shift();
        chartData.latency.data.shift();
    }

    // Add PnL data
    if (pnl !== null) {
        chartData.pnl.labels.push(now);
        chartData.pnl.data.push(parseFloat(pnl));
        if (chartData.pnl.data.length > 50) {
            chartData.pnl.labels.shift();
            chartData.pnl.data.shift();
        }
    }

    // Update chart if visible
    if (chart && currentChartType !== 'orderflow') {
        updateChart();
    }
}

function initChart() {
    const ctx = document.getElementById('hftChart');
    if (!ctx) {
        console.warn('Chart canvas not found');
        return;
    }

    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Latency (ms)',
                data: [],
                borderColor: '#2962ff',
                backgroundColor: 'rgba(41, 98, 255, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: { color: '#d1d4dc' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#787b86' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                x: {
                    ticks: { color: '#787b86' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                }
            }
        }
    });
}

function updateChart() {
    if (!chart) return;

    if (currentChartType === 'latency') {
        chart.config.type = 'line';
        chart.data.labels = chartData.latency.labels;
        chart.data.datasets = [{
            label: 'Latency (ms)',
            data: chartData.latency.data,
            borderColor: '#2962ff',
            backgroundColor: 'rgba(41, 98, 255, 0.1)',
            tension: 0.4
        }];
    } else if (currentChartType === 'pnl') {
        chart.config.type = 'line';
        chart.data.labels = chartData.pnl.labels;
        chart.data.datasets = [{
            label: 'P&L ($)',
            data: chartData.pnl.data,
            borderColor: '#4caf50',
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            tension: 0.4
        }];
    } else if (currentChartType === 'orderflow') {
        chart.config.type = 'bar';
        chart.data.labels = chartData.orderflow.labels;
        chart.data.datasets = [{
            label: 'Order Flow',
            data: chartData.orderflow.data,
            backgroundColor: ['#4caf50', '#ef5350', '#ff9800', '#9e9e9e', '#607d8b']
        }];
    }

    chart.update();
}

function updateUptime() {
    if (!startTime) return;

    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const hours = Math.floor(elapsed / 3600).toString().padStart(2, '0');
    const minutes = Math.floor((elapsed % 3600) / 60).toString().padStart(2, '0');
    const seconds = (elapsed % 60).toString().padStart(2, '0');

    document.getElementById('statUptime').textContent = `${hours}:${minutes}:${seconds}`;
}

function checkRiskLimits() {
    const maxLoss = parseFloat(document.getElementById('maxLoss').value);

    if (stats.totalPnL < -maxLoss) {
        console.warn('Max loss limit reached!');
        stopTrading();
        alert('⚠️ Max loss limit reached! Trading stopped.');
    }
}

function applyFilter() {
    const tbody = document.getElementById('tradesBody');
    const rows = tbody.querySelectorAll('tr:not(.terminal-empty)');

    rows.forEach(row => {
        if (currentFilter === 'all') {
            row.style.display = '';
        } else {
            const status = row.dataset.filter;
            row.style.display = (currentFilter === 'filled' && status === 'filled') ||
                               (currentFilter === 'errors' && status === 'rejected') ? '' : 'none';
        }
    });
}

function clearTerminal() {
    // Clear trades terminal
    const tradesBody = document.getElementById('tradesBody');
    tradesBody.innerHTML = '<tr class="terminal-empty"><td colspan="7" style="text-align: center; color: #787b86; padding: 30px;">Press START to begin trading...</td></tr>';
    
    // Clear market data terminal
    const marketDataBody = document.getElementById('marketDataBody');
    marketDataBody.innerHTML = '<tr class="terminal-empty"><td colspan="4" style="text-align: center; color: #787b86; padding: 20px;">Waiting for ticks...</td></tr>';
    
    // Reset counters
    orderCounter = 0;
    tickCounter = 0;

    // Reset stats
    stats = {
        totalOrders: 0,
        filledOrders: 0,
        rejectedOrders: 0,
        totalLatency: 0,
        totalPnL: 0,
        winningTrades: 0,
        losingTrades: 0,
        bestTrade: 0,
        worstTrade: 0,
        slippage: 0,
        ordersPerSecond: 0
    };

    // Reset chart data
    chartData.latency.labels = [];
    chartData.latency.data = [];
    chartData.pnl.labels = [];
    chartData.pnl.data = [];
    chartData.orderflow.data = [0, 0, 0, 0, 0];

    updateChart();
}

function exportLog() {
    const tbody = document.getElementById('tradesBody');
    const rows = Array.from(tbody.querySelectorAll('tr:not(.terminal-empty)'));

    if (rows.length === 0) {
        alert('No data to export');
        return;
    }

    let csv = '#,Time,Side,Price,Qty,Status,PnL\n';

    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const rowData = Array.from(cells).map(cell => cell.textContent.trim()).join(',');
        csv += rowData + '\n';
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hft_trades_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

function playSound(type) {
    // Sound effects placeholder - can be implemented with Web Audio API
    console.log(`Sound: ${type}`);
}