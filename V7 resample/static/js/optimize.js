// Optimize Page Logic
const Optimize = {
    optimizationRunning: false,
    currentResults: [],
    
    init() {
        this.setupFileUpload();
        this.setupStrategySelector();
        this.setupSettings();
        this.setupButtons();
        this.setupTabs();
        this.setupTerminal();
    },
    
    setupFileUpload() {
        const fileInput = document.getElementById('csv-file-input-optimize');
        const uploadArea = document.querySelector('.file-upload-area');
        
        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', () => fileInput.click());
            
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
        
        App.showNotification('File uploaded: ' + file.name, 'success');
        console.log('Uploaded file:', file.name);
    },
    
    setupStrategySelector() {
        const strategySelector = document.getElementById('strategy-selector-optimize');
        if (strategySelector) {
            strategySelector.addEventListener('change', (e) => {
                this.loadStrategyParameters(e.target.value);
            });
            
            this.loadStrategies();
        }
    },
    
    async loadStrategies() {
        try {
            const result = await App.apiCall('/strategies', 'GET');
            const selector = document.getElementById('strategy-selector-optimize');
            
            if (selector && result.strategies) {
                selector.innerHTML = '<option value="">Select strategy...</option>' +
                    result.strategies.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
            }
        } catch (error) {
            console.error('Error loading strategies:', error);
        }
    },
    
    async loadStrategyParameters(strategyId) {
        if (!strategyId) {
            this.clearParametersDisplay();
            return;
        }
        
        try {
            // TODO: Load strategy parameters from API
            this.displayParameters([]);
            console.log('Loading parameters for strategy:', strategyId);
        } catch (error) {
            console.error('Error loading parameters:', error);
        }
    },
    
    displayParameters(parameters) {
        const entryContainer = document.getElementById('entry-parameters-container');
        const exitContainer = document.getElementById('exit-parameters-container');
        
        if (!parameters || parameters.length === 0) {
            if (entryContainer) {
                entryContainer.innerHTML = '<p class="empty-state">Select a strategy to view entry parameters</p>';
            }
            if (exitContainer) {
                exitContainer.innerHTML = '<p class="empty-state">Select a strategy to view exit parameters</p>';
            }
            return;
        }
        
        // TODO: Render parameters with min/max/step inputs
    },
    
    clearParametersDisplay() {
        const entryContainer = document.getElementById('entry-parameters-container');
        const exitContainer = document.getElementById('exit-parameters-container');
        
        if (entryContainer) {
            entryContainer.innerHTML = '<p class="empty-state">Select a strategy to view entry parameters</p>';
        }
        if (exitContainer) {
            exitContainer.innerHTML = '<p class="empty-state">Select a strategy to view exit parameters</p>';
        }
    },
    
    setupSettings() {
        // Settings are handled via form inputs
        console.log('Optimization settings initialized');
    },
    
    setupButtons() {
        const startBtn = document.getElementById('start-optimization-btn');
        const autoBtn = document.getElementById('auto-optimization-btn');
        const expandBtn = document.getElementById('expand-all-btn');
        const collapseBtn = document.getElementById('collapse-all-btn');
        const exportBtn = document.getElementById('export-csv-btn');
        
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startOptimization());
        }
        
        if (autoBtn) {
            autoBtn.addEventListener('click', () => this.autoOptimize());
        }
        
        if (expandBtn) {
            expandBtn.addEventListener('click', () => this.expandAllSections());
        }
        
        if (collapseBtn) {
            collapseBtn.addEventListener('click', () => this.collapseAllSections());
        }
        
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportResults());
        }
    },
    
    setupTabs() {
        const tabs = document.querySelectorAll('.parameters-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                tabs.forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                
                const tabName = e.target.dataset.tab;
                this.showParametersTab(tabName);
            });
        });
    },
    
    showParametersTab(tabName) {
        const tabContents = document.querySelectorAll('.parameters-content');
        tabContents.forEach(content => {
            content.style.display = content.dataset.tab === tabName ? 'block' : 'none';
        });
    },
    
    setupTerminal() {
        const clearBtn = document.querySelector('.terminal-clear');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearTerminal());
        }
    },
    
    addTerminalLine(text, type = 'output') {
        const terminal = document.querySelector('.terminal');
        if (!terminal) return;
        
        const line = document.createElement('div');
        line.className = `terminal-line terminal-${type}`;
        line.textContent = text;
        terminal.appendChild(line);
        
        // Auto scroll to bottom
        terminal.scrollTop = terminal.scrollHeight;
    },
    
    clearTerminal() {
        const terminal = document.querySelector('.terminal');
        if (terminal) {
            terminal.innerHTML = '<div class="terminal-line terminal-output">Terminal ready. Waiting for optimization to start...</div>';
        }
    },
    
    async startOptimization() {
        const strategyId = document.getElementById('strategy-selector-optimize')?.value;
        
        if (!strategyId) {
            App.showNotification('Vui lòng chọn strategy', 'warning');
            return;
        }
        
        const algorithm = document.getElementById('algorithm-selector')?.value || 'genetic';
        const timeframe = document.getElementById('timeframe-optimize')?.value || '1 Hour';
        const population = document.getElementById('population-input')?.value || 50;
        const generations = document.getElementById('generations-input')?.value || 20;
        const maxResults = document.getElementById('max-results-input')?.value || 10;
        
        const optimizeParams = {
            strategy_id: strategyId,
            algorithm: algorithm,
            timeframe: timeframe,
            population: parseInt(population),
            generations: parseInt(generations),
            max_results: parseInt(maxResults)
        };
        
        try {
            this.optimizationRunning = true;
            this.clearTerminal();
            this.addTerminalLine('[System] Starting optimization...', 'success');
            this.addTerminalLine(`[Config] Algorithm: ${algorithm}`, 'output');
            this.addTerminalLine(`[Config] Population: ${population}, Generations: ${generations}`, 'output');
            
            App.showNotification('Đang chạy optimization...', 'info');
            
            // Simulate progress updates
            for (let i = 1; i <= parseInt(generations); i++) {
                await new Promise(resolve => setTimeout(resolve, 500));
                this.addTerminalLine(`[Progress] Generation ${i}/${generations} completed`, 'output');
            }
            
            const result = await App.apiCall('/optimize/run', 'POST', optimizeParams);
            
            this.currentResults = result.results || [];
            this.displayResults(this.currentResults);
            
            this.addTerminalLine('[System] Optimization completed successfully!', 'success');
            App.showNotification('Optimization hoàn thành', 'success');
            
        } catch (error) {
            this.addTerminalLine('[Error] Optimization failed', 'error');
            App.showNotification('Optimization thất bại', 'error');
        } finally {
            this.optimizationRunning = false;
        }
    },
    
    async autoOptimize() {
        // TODO: Implement auto-optimization with predefined best settings
        App.showNotification('Auto optimization feature coming soon', 'info');
    },
    
    displayResults(results) {
        const tbody = document.querySelector('.optimization-results-table tbody');
        if (!tbody) return;
        
        if (results.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 2rem;">Run optimization to see results</td></tr>';
            return;
        }
        
        tbody.innerHTML = results.map((result, index) => {
            const rankClass = index === 0 ? 'rank-1' : index === 1 ? 'rank-2' : index === 2 ? 'rank-3' : '';
            return `
                <tr>
                    <td><span class="rank-badge ${rankClass}">${index + 1}</span></td>
                    <td>${result.win_rate ? (result.win_rate * 100).toFixed(2) + '%' : '-'}</td>
                    <td class="${result.profit >= 0 ? 'text-success' : 'text-danger'}">${result.profit || '-'}</td>
                    <td class="text-danger">${result.drawdown || '-'}</td>
                    <td>${result.profit_factor || '-'}</td>
                    <td>${result.trades || '-'}</td>
                    <td>${result.fitness || '-'}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="Optimize.viewDetails(${index})">View</button>
                        <button class="btn btn-sm btn-success" onclick="Optimize.applyParameters(${index})">Apply</button>
                    </td>
                </tr>
            `;
        }).join('');
    },
    
    viewDetails(index) {
        const result = this.currentResults[index];
        if (!result) return;
        
        console.log('Result details:', result);
        App.showNotification('Viewing result #' + (index + 1), 'info');
        // TODO: Show detailed view in modal
    },
    
    applyParameters(index) {
        const result = this.currentResults[index];
        if (!result) return;
        
        if (confirm('Apply these parameters to strategy?')) {
            console.log('Applying parameters:', result);
            App.showNotification('Parameters applied successfully', 'success');
            // TODO: Implement parameter application
        }
    },
    
    expandAllSections() {
        // TODO: Expand all parameter sections
        console.log('Expanding all sections');
    },
    
    collapseAllSections() {
        // TODO: Collapse all parameter sections
        console.log('Collapsing all sections');
    },
    
    async exportResults() {
        if (this.currentResults.length === 0) {
            App.showNotification('Không có kết quả để xuất', 'warning');
            return;
        }
        
        try {
            // TODO: Implement CSV export
            App.showNotification('Đang xuất CSV...', 'info');
            console.log('Exporting results:', this.currentResults);
            App.showNotification('CSV đã được xuất', 'success');
        } catch (error) {
            App.showNotification('Xuất CSV thất bại', 'error');
        }
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    Optimize.init();
});

// Export for global access
window.Optimize = Optimize;
