// Bot Trading Page Logic
const BotTrading = {
    botRunning: false,
    selectedStrategy: null,
    
    init() {
        this.setupStrategySelector();
        this.setupBotControls();
        this.updateBotStatus();
    },
    
    setupStrategySelector() {
        const strategySelector = document.getElementById('strategy-selector');
        if (strategySelector) {
            strategySelector.addEventListener('change', (e) => {
                this.selectedStrategy = e.target.value;
                console.log('Strategy selected:', this.selectedStrategy);
                this.loadStrategyDetails();
            });
            
            // Load available strategies
            this.loadStrategies();
        }
    },
    
    setupBotControls() {
        const startBtn = document.getElementById('start-bot-btn');
        const stopBtn = document.getElementById('stop-bot-btn');
        
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startBot());
        }
        
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopBot());
        }
    },
    
    async loadStrategies() {
        try {
            const result = await App.apiCall('/strategies', 'GET');
            const strategySelector = document.getElementById('strategy-selector');
            
            if (strategySelector && result.strategies) {
                strategySelector.innerHTML = '<option value="">-- Chọn strategy --</option>' +
                    result.strategies.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
            }
        } catch (error) {
            console.error('Error loading strategies:', error);
        }
    },
    
    async loadStrategyDetails() {
        if (!this.selectedStrategy) return;
        
        try {
            // TODO: Load strategy details from API
            console.log('Loading strategy details for:', this.selectedStrategy);
        } catch (error) {
            console.error('Error loading strategy details:', error);
        }
    },
    
    async startBot() {
        if (!this.selectedStrategy) {
            App.showNotification('Vui lòng chọn strategy', 'warning');
            return;
        }
        
        const accountSelector = document.getElementById('account-selector');
        const clientSelector = document.getElementById('client-selector');
        const symbolInput = document.getElementById('symbol-input');
        const timeframeInput = document.getElementById('timeframe-input');
        
        const botConfig = {
            strategy: this.selectedStrategy,
            account: accountSelector?.value,
            client: clientSelector?.value,
            symbol: symbolInput?.value || 'VN30F1M',
            timeframe: timeframeInput?.value || '1m'
        };
        
        try {
            // TODO: Start bot via API
            this.botRunning = true;
            this.updateBotStatus();
            App.showNotification('Bot đã khởi động', 'success');
            
            // Update button states
            const startBtn = document.getElementById('start-bot-btn');
            const stopBtn = document.getElementById('stop-bot-btn');
            if (startBtn) startBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = false;
            
        } catch (error) {
            App.showNotification('Không thể khởi động bot', 'error');
        }
    },
    
    async stopBot() {
        if (!confirm('Bạn có chắc muốn dừng bot?')) return;
        
        try {
            // TODO: Stop bot via API
            this.botRunning = false;
            this.updateBotStatus();
            App.showNotification('Bot đã dừng', 'info');
            
            // Update button states
            const startBtn = document.getElementById('start-bot-btn');
            const stopBtn = document.getElementById('stop-bot-btn');
            if (startBtn) startBtn.disabled = false;
            if (stopBtn) stopBtn.disabled = true;
            
        } catch (error) {
            App.showNotification('Không thể dừng bot', 'error');
        }
    },
    
    updateBotStatus() {
        const statusBadge = document.querySelector('.bot-status-badge');
        if (statusBadge) {
            if (this.botRunning) {
                statusBadge.className = 'status-badge status-running';
                statusBadge.innerHTML = '● Đang chạy';
            } else {
                statusBadge.className = 'status-badge status-stopped';
                statusBadge.innerHTML = '● Đã dừng';
            }
        }
    },
    
    async loadBotLogs() {
        try {
            // TODO: Load bot logs from API
            const logs = [];
            this.displayBotLogs(logs);
        } catch (error) {
            console.error('Error loading bot logs:', error);
        }
    },
    
    displayBotLogs(logs) {
        const tbody = document.querySelector('.bot-logs-table tbody');
        if (!tbody) return;
        
        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">Không có lệnh nào</td></tr>';
            return;
        }
        
        tbody.innerHTML = logs.map(log => `
            <tr>
                <td>${log.account || '-'}</td>
                <td>${log.time || '-'}</td>
                <td><span class="badge ${log.side === 'BUY' ? 'badge-success' : 'badge-danger'}">${log.side}</span></td>
                <td>${log.symbol || '-'}</td>
                <td>${log.price || '-'}</td>
                <td>${log.quantity || '-'}</td>
                <td class="${log.pnl >= 0 ? 'text-success' : 'text-danger'}">${log.pnl || '-'}</td>
                <td>${log.status || '-'}</td>
            </tr>
        `).join('');
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🟢 DOMContentLoaded - bot-trading.js');
    BotTrading.init();
    
    // Initialize chart
    if (typeof ChartBot !== 'undefined') {
        if (window.chartBot) {
            console.warn('⚠️⚠️⚠️ DUPLICATE: chartBot already exists!');
            return;
        }
        console.log('📊 Creating ChartBot...');
        window.chartBot = new ChartBot('trading-chart');
        window.chartBot.init();
        console.log('✅ ChartBot initialized');
    }
});

// Export for global access
window.BotTrading = BotTrading;
