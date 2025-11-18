// Backtest Page Logic
const Backtest = {
    currentResults: null,
    
    init() {
        this.setupFileUpload();
        this.setupStrategySelector();
        this.setupSettings();
        this.setupRunButton();
        this.setupTabs();
    },
    
    setupFileUpload() {
        const fileInput = document.getElementById('csv-file-input');
        const uploadArea = document.querySelector('.file-upload-area');
        
        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', () => fileInput.click());
            
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = 'var(--accent-blue)';
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.style.borderColor = 'var(--border-color)';
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = 'var(--border-color)';
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileUpload(files[0]);
                }
            });
            
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileUpload(e.target.files[0]);
                }
            });
        }
    },
    
    async handleFileUpload(file) {
        if (!file.name.endsWith('.csv')) {
            App.showNotification('Vui lòng chọn file CSV', 'warning');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            // TODO: Upload file to server
            App.showNotification('File uploaded: ' + file.name, 'success');
            console.log('Uploaded file:', file.name);
        } catch (error) {
            App.showNotification('Upload failed', 'error');
        }
    },
    
    setupStrategySelector() {
        const strategySelector = document.getElementById('strategy-selector-backtest');
        if (strategySelector) {
            strategySelector.addEventListener('change', (e) => {
                console.log('Strategy selected:', e.target.value);
                this.loadStrategyForBacktest(e.target.value);
            });
            
            this.loadStrategies();
        }
    },
    
    async loadStrategies() {
        try {
            const result = await App.apiCall('/strategies', 'GET');
            const selector = document.getElementById('strategy-selector-backtest');
            
            if (selector && result.strategies) {
                selector.innerHTML = '<option value="">Select strategy...</option>' +
                    result.strategies.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
            }
        } catch (error) {
            console.error('Error loading strategies:', error);
        }
    },
    
    async loadStrategyForBacktest(strategyId) {
        if (!strategyId) return;
        
        try {
            // TODO: Load strategy details
            console.log('Loading strategy:', strategyId);
        } catch (error) {
            console.error('Error loading strategy:', error);
        }
    },
    
    setupSettings() {
        // Settings are handled via form inputs
        console.log('Backtest settings initialized');
    },
    
    setupRunButton() {
        const runBtn = document.getElementById('run-backtest-btn');
        const exportBtn = document.getElementById('export-pdf-btn');
        
        if (runBtn) {
            runBtn.addEventListener('click', () => this.runBacktest());
        }
        
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportPDF());
        }
    },
    
    setupTabs() {
        const tabs = document.querySelectorAll('.chart-tab');
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
        const tabContents = document.querySelectorAll('.tab-content-backtest');
        tabContents.forEach(content => {
            content.style.display = content.dataset.tab === tabName ? 'block' : 'none';
        });
    },
    
    async runBacktest() {
        const strategyId = document.getElementById('strategy-selector-backtest')?.value;
        const initialCapital = document.getElementById('initial-capital')?.value;
        const commission = document.getElementById('commission')?.value;
        const slippage = document.getElementById('slippage')?.value;
        const timeframe = document.getElementById('timeframe-backtest')?.value;
        
        if (!strategyId) {
            App.showNotification('Vui lòng chọn strategy', 'warning');
            return;
        }
        
        const backtestParams = {
            strategy_id: strategyId,
            initial_capital: parseFloat(initialCapital) || 10000,
            commission: parseFloat(commission) || 0.5,
            slippage: parseFloat(slippage) || 0.1,
            timeframe: timeframe || '1 Hour'
        };
        
        try {
            App.showNotification('Đang chạy backtest...', 'info');
            const result = await App.apiCall('/backtest/run', 'POST', backtestParams);
            
            this.currentResults = result.results;
            this.displayResults(result.results);
            App.showNotification('Backtest hoàn thành', 'success');
        } catch (error) {
            App.showNotification('Backtest thất bại', 'error');
        }
    },
    
    displayResults(results) {
        // Update metrics
        this.updateMetric('net-profit', results.net_profit || 0);
        this.updateMetric('net-profit-pct', results.net_profit_pct || 0);
        this.updateMetric('total-trades', results.total_trades || 0);
        this.updateMetric('win-rate', results.win_rate || 0);
        this.updateMetric('max-drawdown', results.max_drawdown || 0);
        this.updateMetric('profit-factor', results.profit_factor || 0);
        this.updateMetric('sharpe-ratio', results.sharpe_ratio || 0);
        this.updateMetric('annual-return', results.annual_return || 0);
        
        // Display performance table
        this.displayPerformanceTable(results.performance || {});
        
        // Display history table
        this.displayHistoryTable(results.history || []);
    },
    
    updateMetric(id, value) {
        const element = document.getElementById(id);
        if (element) {
            if (typeof value === 'number') {
                element.textContent = value.toFixed(2);
            } else {
                element.textContent = value;
            }
        }
    },
    
    displayPerformanceTable(performance) {
        const tbody = document.querySelector('.performance-table tbody');
        if (!tbody) return;
        
        const metrics = [
            { label: 'Total Net Profit', long: performance.long_net_profit || 0, short: performance.short_net_profit || 0 },
            { label: 'Gross Profit', long: performance.long_gross_profit || 0, short: performance.short_gross_profit || 0 },
            { label: 'Gross Loss', long: performance.long_gross_loss || 0, short: performance.short_gross_loss || 0 },
            { label: 'Total # of Trades', long: performance.long_trades || 0, short: performance.short_trades || 0 },
            { label: 'Winning Trades', long: performance.long_winning || 0, short: performance.short_winning || 0 },
            { label: 'Losing Trades', long: performance.long_losing || 0, short: performance.short_losing || 0 },
            { label: 'Win Rate %', long: performance.long_win_rate || 0, short: performance.short_win_rate || 0 },
            { label: 'Profit Factor', long: performance.long_profit_factor || 0, short: performance.short_profit_factor || 0 },
            { label: 'Average Win', long: performance.long_avg_win || 0, short: performance.short_avg_win || 0 },
            { label: 'Average Loss', long: performance.long_avg_loss || 0, short: performance.short_avg_loss || 0 },
            { label: 'Largest Win', long: performance.long_largest_win || 0, short: performance.short_largest_win || 0 },
            { label: 'Largest Loss', long: performance.long_largest_loss || 0, short: performance.short_largest_loss || 0 },
            { label: 'Max Drawdown', long: performance.long_max_dd || 0, short: performance.short_max_dd || 0 }
        ];
        
        tbody.innerHTML = metrics.map(metric => {
            const allValue = (parseFloat(metric.long) + parseFloat(metric.short)) || 0;
            return `
                <tr>
                    <td>${metric.label}</td>
                    <td class="${metric.long >= 0 ? 'text-success' : 'text-danger'}">${typeof metric.long === 'number' ? metric.long.toFixed(2) : metric.long}</td>
                    <td class="${metric.short >= 0 ? 'text-success' : 'text-danger'}">${typeof metric.short === 'number' ? metric.short.toFixed(2) : metric.short}</td>
                    <td class="${allValue >= 0 ? 'text-success' : 'text-danger'}">${allValue.toFixed(2)}</td>
                </tr>
            `;
        }).join('');
    },
    
    displayHistoryTable(history) {
        const tbody = document.querySelector('.history-table tbody');
        if (!tbody) return;
        
        if (history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 2rem;">Chưa có dữ liệu</td></tr>';
            return;
        }
        
        tbody.innerHTML = history.map(trade => `
            <tr>
                <td>${trade.entry_time || '-'}</td>
                <td>${trade.exit_time || '-'}</td>
                <td><span class="badge ${trade.type === 'Long' ? 'badge-success' : 'badge-danger'}">${trade.type}</span></td>
                <td>${trade.entry_price || '-'}</td>
                <td>${trade.exit_price || '-'}</td>
                <td>${trade.quantity || '-'}</td>
                <td class="${trade.pnl >= 0 ? 'text-success' : 'text-danger'}">${trade.pnl || '-'}</td>
                <td>${trade.pnl_pct ? trade.pnl_pct.toFixed(2) + '%' : '-'}</td>
                <td>${trade.mae || '-'}</td>
                <td>${trade.mfe || '-'}</td>
            </tr>
        `).join('');
    },
    
    async exportPDF() {
        if (!this.currentResults) {
            App.showNotification('Vui lòng chạy backtest trước', 'warning');
            return;
        }
        
        try {
            App.showNotification('Đang xuất PDF...', 'info');
            // TODO: Implement PDF export
            console.log('Exporting PDF:', this.currentResults);
            App.showNotification('PDF đã được xuất', 'success');
        } catch (error) {
            App.showNotification('Xuất PDF thất bại', 'error');
        }
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    Backtest.init();
});

// Export for global access
window.Backtest = Backtest;
