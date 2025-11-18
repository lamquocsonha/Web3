// HFT (High-Frequency Trading) Page Logic
const HFT = {
    isRunning: false,
    isConnected: false,
    startTime: null,
    uptimeInterval: null,
    tickInterval: null,
    latencyData: [],
    maxLatencyPoints: 100,
    
    // Metrics
    metrics: {
        orders: 0,
        fillRate: 0,
        avgLatency: 0,
        totalPnl: 0,
        winRate: 0,
        ordersPerSec: 0,
        bestTrade: 0,
        worstTrade: 0,
        slippage: 0,
        uptime: '00:00:00'
    },
    
    init() {
        this.setupControls();
        this.setupTabs();
        this.initLatencyChart();
    },
    
    setupControls() {
        const mockdataBtn = document.getElementById('mockdata-btn');
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');
        
        if (mockdataBtn) {
            mockdataBtn.addEventListener('click', () => this.loadMockData());
        }
        
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startHFT());
        }
        
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopHFT());
        }
    },
    
    setupTabs() {
        const tabs = document.querySelectorAll('.hft-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                tabs.forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                
                const tabName = e.target.dataset.tab;
                this.showTab(tabName);
            });
        });
    },
    
    showTab(tabName) {
        const contents = document.querySelectorAll('.hft-tab-content');
        contents.forEach(content => {
            content.style.display = content.dataset.tab === tabName ? 'block' : 'none';
        });
    },
    
    loadMockData() {
        this.isConnected = true;
        this.updateStatus();
        App.showNotification('Mock data loaded', 'success');
        
        // Start generating mock ticks
        this.startMockTicks();
    },
    
    async startHFT() {
        const strategy = document.getElementById('strategy-selector')?.value;
        const exchange = document.getElementById('exchange-selector')?.value;
        
        if (!exchange) {
            App.showNotification('Please select an exchange', 'warning');
            return;
        }
        
        if (!this.isConnected) {
            App.showNotification('Please connect to exchange first', 'warning');
            return;
        }
        
        try {
            this.isRunning = true;
            this.startTime = Date.now();
            this.updateStatus();
            this.startUptime();
            this.startMetricsUpdate();
            
            // Update buttons
            const startBtn = document.getElementById('start-btn');
            const stopBtn = document.getElementById('stop-btn');
            if (startBtn) startBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = false;
            
            App.showNotification('HFT started successfully', 'success');
        } catch (error) {
            App.showNotification('Failed to start HFT', 'error');
        }
    },
    
    stopHFT() {
        if (!confirm('Stop HFT trading?')) return;
        
        this.isRunning = false;
        this.updateStatus();
        
        if (this.uptimeInterval) {
            clearInterval(this.uptimeInterval);
            this.uptimeInterval = null;
        }
        
        if (this.tickInterval) {
            clearInterval(this.tickInterval);
            this.tickInterval = null;
        }
        
        // Update buttons
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');
        if (startBtn) startBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = true;
        
        App.showNotification('HFT stopped', 'info');
    },
    
    updateStatus() {
        const statusEl = document.getElementById('hft-status');
        const connectionEl = document.getElementById('connection-status');
        const pingEl = document.getElementById('ping-value');
        
        if (statusEl) {
            if (this.isRunning) {
                statusEl.textContent = 'RUNNING';
                statusEl.className = 'status-value status-running';
            } else {
                statusEl.textContent = 'STOPPED';
                statusEl.className = 'status-value status-stopped';
            }
        }
        
        if (connectionEl) {
            if (this.isConnected) {
                connectionEl.textContent = 'CONNECTED';
                connectionEl.className = 'status-value status-connected';
                if (pingEl) pingEl.textContent = Math.floor(Math.random() * 5) + 1 + 'ms';
            } else {
                connectionEl.textContent = 'DISCONNECTED';
                connectionEl.className = 'status-value status-disconnected';
                if (pingEl) pingEl.textContent = '--';
            }
        }
    },
    
    startUptime() {
        this.uptimeInterval = setInterval(() => {
            if (!this.isRunning || !this.startTime) return;
            
            const elapsed = Date.now() - this.startTime;
            const hours = Math.floor(elapsed / 3600000);
            const minutes = Math.floor((elapsed % 3600000) / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            
            this.metrics.uptime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            this.updateMetricDisplay('metric-uptime', this.metrics.uptime);
        }, 1000);
    },
    
    startMockTicks() {
        const tbody = document.getElementById('market-data-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        this.tickInterval = setInterval(() => {
            if (!this.isConnected) return;
            
            const now = new Date();
            const time = now.toLocaleTimeString();
            const price = (Math.random() * 100 + 1850).toFixed(2);
            const volume = Math.floor(Math.random() * 1000) + 100;
            const side = Math.random() > 0.5 ? 'BUY' : 'SELL';
            
            const row = document.createElement('tr');
            row.className = side === 'BUY' ? 'tick-buy' : 'tick-sell';
            row.innerHTML = `
                <td>${time}</td>
                <td class="${side === 'BUY' ? 'text-success' : 'text-danger'}">${price}</td>
                <td>${volume}</td>
                <td><span class="badge ${side === 'BUY' ? 'badge-success' : 'badge-danger'}">${side}</span></td>
            `;
            
            tbody.insertBefore(row, tbody.firstChild);
            
            // Keep only last 50 rows
            while (tbody.children.length > 50) {
                tbody.removeChild(tbody.lastChild);
            }
            
            // Update latency chart
            const latency = Math.floor(Math.random() * 10) + 1;
            this.addLatencyPoint(latency);
            
        }, 500); // New tick every 500ms
    },
    
    startMetricsUpdate() {
        setInterval(() => {
            if (!this.isRunning) return;
            
            // Simulate metrics updates
            this.metrics.orders += Math.floor(Math.random() * 5);
            this.metrics.fillRate = Math.min(100, this.metrics.fillRate + Math.random() * 2);
            this.metrics.avgLatency = Math.floor(Math.random() * 3) + 1;
            this.metrics.totalPnl += (Math.random() - 0.4) * 50;
            this.metrics.winRate = Math.min(100, 50 + Math.random() * 20);
            this.metrics.ordersPerSec = Math.floor(Math.random() * 10);
            this.metrics.bestTrade = Math.max(this.metrics.bestTrade, Math.random() * 100);
            this.metrics.worstTrade = Math.min(this.metrics.worstTrade, -(Math.random() * 50));
            this.metrics.slippage = Math.floor(Math.random() * 5);
            
            this.updateAllMetrics();
        }, 2000);
    },
    
    updateAllMetrics() {
        this.updateMetricDisplay('metric-orders', this.metrics.orders);
        this.updateMetricDisplay('metric-fill-rate', this.metrics.fillRate.toFixed(1) + '%');
        this.updateMetricDisplay('metric-latency', this.metrics.avgLatency + 'ms');
        this.updateMetricDisplay('metric-pnl', '$' + this.metrics.totalPnl.toFixed(0));
        this.updateMetricDisplay('metric-win-rate', this.metrics.winRate.toFixed(1) + '%');
        this.updateMetricDisplay('metric-orders-sec', this.metrics.ordersPerSec);
        this.updateMetricDisplay('metric-best', '$' + this.metrics.bestTrade.toFixed(0));
        this.updateMetricDisplay('metric-worst', '$' + this.metrics.worstTrade.toFixed(0));
        this.updateMetricDisplay('metric-slippage', this.metrics.slippage + ' pts');
    },
    
    updateMetricDisplay(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    },
    
    initLatencyChart() {
        const chartDiv = document.getElementById('latency-chart');
        if (!chartDiv) return;
        
        const data = [{
            y: [],
            type: 'scatter',
            mode: 'lines',
            name: 'Latency (ms)',
            line: {
                color: '#3b82f6',
                width: 2
            }
        }];
        
        const layout = {
            title: 'Latency Over Time',
            paper_bgcolor: '#141824',
            plot_bgcolor: '#1a1f2e',
            font: {
                color: '#a0a0a0'
            },
            xaxis: {
                title: 'Time',
                gridcolor: '#2d3748',
                showgrid: true
            },
            yaxis: {
                title: 'Latency (ms)',
                gridcolor: '#2d3748',
                showgrid: true,
                range: [0, 1.0]
            },
            margin: {
                l: 50,
                r: 30,
                t: 50,
                b: 40
            }
        };
        
        const config = {
            responsive: true,
            displayModeBar: false
        };
        
        Plotly.newPlot(chartDiv, data, layout, config);
    },
    
    addLatencyPoint(latency) {
        this.latencyData.push(latency / 1000); // Convert to seconds for chart
        
        if (this.latencyData.length > this.maxLatencyPoints) {
            this.latencyData.shift();
        }
        
        const chartDiv = document.getElementById('latency-chart');
        if (chartDiv && Plotly) {
            Plotly.update(chartDiv, {
                y: [this.latencyData]
            });
        }
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    HFT.init();
});

// Export for global access
window.HFT = HFT;
