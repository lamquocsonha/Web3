// Strategy Builder Page Logic
const StrategyBuilder = {
    currentStrategy: {
        name: 'My Strategy',
        description: '',
        entry: {
            long: [],
            short: []
        },
        exit: {
            long: [],
            short: []
        },
        indicators: [],
        tradingEngine: {}
    },
    savedStrategies: [],
    currentTab: 'entry',
    currentEntryType: 'long',
    
    init() {
        this.setupTabs();
        this.setupEntryTypeButtons();
        this.setupActions();
        this.loadSavedStrategies();
    },
    
    setupTabs() {
        const tabs = document.querySelectorAll('.strategy-tab');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                e.target.classList.add('active');
                const tabId = e.target.dataset.tab;
                document.getElementById(`${tabId}-tab`).classList.add('active');
            });
        });
    },
    
    setupEntryTypeButtons() {
        const entryBtns = document.querySelectorAll('.entry-btn');
        entryBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                entryBtns.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
    },
    
    setupActions() {
        // Setup quick action buttons
        const quickBtns = document.querySelectorAll('.quick-action-btn');
        quickBtns.forEach((btn, index) => {
            btn.addEventListener('click', () => {
                if (index === 0) this.testStrategy();
                if (index === 1) this.refreshStrategy();
                if (index === 2) this.clearStrategy();
            });
        });
    },
    
    newStrategy() {
        if (confirm('Create new strategy? Current unsaved changes will be lost.')) {
            this.currentStrategy = {
                name: 'My Strategy',
                description: '',
                entry: { long: [], short: [] },
                exit: { long: [], short: [] },
                indicators: [],
                tradingEngine: {}
            };
            document.getElementById('strategy-name').value = 'My Strategy';
            document.getElementById('strategy-description').value = '';
        }
    },
    
    saveStrategy() {
        const name = document.getElementById('strategy-name').value.trim() || 'My Strategy';
        const description = document.getElementById('strategy-description').value.trim();
        
        this.currentStrategy.name = name;
        this.currentStrategy.description = description;
        this.currentStrategy.savedAt = new Date().toISOString();
        
        // Check if strategy already exists
        const existingIndex = this.savedStrategies.findIndex(s => s.name === name);
        if (existingIndex !== -1) {
            this.savedStrategies[existingIndex] = { ...this.currentStrategy };
        } else {
            this.savedStrategies.push({ ...this.currentStrategy });
        }
        
        // Save to localStorage
        localStorage.setItem('savedStrategies', JSON.stringify(this.savedStrategies));
        
        // Show notification
        this.showSaveNotification(name);
    },
    
    showSaveNotification(strategyName) {
        const notification = document.getElementById('saveNotification');
        const nameElement = document.getElementById('savedStrategyName');
        
        nameElement.textContent = strategyName;
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    },
    
    loadSavedStrategies() {
        const saved = localStorage.getItem('savedStrategies');
        if (saved) {
            this.savedStrategies = JSON.parse(saved);
        } else {
            // Demo data
            this.savedStrategies = [
                {
                    name: 'Chiến lược 11',
                    filename: 'Chien_luoc_11.json',
                    description: 'EMA crossover strategy',
                    savedAt: new Date('2024-01-15').toISOString()
                },
                {
                    name: 'Chiến lược 11 copy',
                    filename: 'Chien_luoc_11_copy.json',
                    description: 'Modified EMA strategy',
                    savedAt: new Date('2024-01-16').toISOString()
                },
                {
                    name: 'EMA',
                    filename: 'EMA.json',
                    description: 'Simple EMA strategy',
                    savedAt: new Date('2024-01-17').toISOString()
                },
                {
                    name: 'My Strategy',
                    filename: 'My_Strategy.json',
                    description: '',
                    savedAt: new Date('2024-01-18').toISOString()
                },
                {
                    name: 'My Strategy 1',
                    filename: 'My_Strategy_1.json',
                    description: '',
                    savedAt: new Date('2024-01-19').toISOString()
                },
                {
                    name: 'Strategy Template',
                    filename: 'strategy_template.json',
                    description: 'Base template',
                    savedAt: new Date('2024-01-20').toISOString()
                },
                {
                    name: 'TempTest',
                    filename: 'TempTest.json',
                    description: 'Test strategy',
                    savedAt: new Date('2024-01-21').toISOString()
                }
            ];
        }
    },
    
    openLoadModal() {
        const modal = document.getElementById('loadStrategyModal');
        const listContainer = document.getElementById('strategyList');
        
        listContainer.innerHTML = this.savedStrategies.map((strategy, index) => `
            <div class="strategy-list-item">
                <div class="strategy-item-content" onclick="StrategyBuilder.loadStrategy(${index})">
                    <div class="strategy-item-number">${index + 1}.</div>
                    <div class="strategy-item-info">
                        <div class="strategy-item-name">${strategy.name}</div>
                        <div class="strategy-item-filename">${strategy.filename || strategy.name.replace(/\s+/g, '_') + '.json'}</div>
                    </div>
                </div>
                <button class="btn btn-sm btn-danger" onclick="StrategyBuilder.deleteStrategy(${index}, event)">
                    🗑️ Delete
                </button>
            </div>
        `).join('');
        
        modal.style.display = 'flex';
    },
    
    closeLoadModal() {
        document.getElementById('loadStrategyModal').style.display = 'none';
    },
    
    loadStrategy(index) {
        const strategy = this.savedStrategies[index];
        if (!strategy) return;
        
        this.currentStrategy = { ...strategy };
        document.getElementById('strategy-name').value = strategy.name;
        document.getElementById('strategy-description').value = strategy.description || '';
        
        this.closeLoadModal();
        
        // Show brief notification
        const tempNotif = document.createElement('div');
        tempNotif.className = 'temp-notification';
        tempNotif.textContent = `Loaded: ${strategy.name}`;
        document.body.appendChild(tempNotif);
        
        setTimeout(() => tempNotif.remove(), 2000);
    },
    
    deleteStrategy(index, event) {
        event.stopPropagation();
        
        const strategy = this.savedStrategies[index];
        if (!confirm(`Delete "${strategy.name}"?\n\nThis action cannot be undone.`)) return;
        
        this.savedStrategies.splice(index, 1);
        localStorage.setItem('savedStrategies', JSON.stringify(this.savedStrategies));
        
        this.openLoadModal(); // Refresh the list
    },
    
    testStrategy() {
        alert('Testing strategy...');
    },
    
    refreshStrategy() {
        location.reload();
    },
    
    clearStrategy() {
        if (confirm('Clear all strategy data?')) {
            this.newStrategy();
        }
    },
    
    setupEntryTypeButtons() {
        const longBtn = document.getElementById('long-entry-btn');
        const shortBtn = document.getElementById('short-entry-btn');
        
        if (longBtn) {
            longBtn.addEventListener('click', () => {
                this.currentEntryType = 'long';
                longBtn.classList.add('active');
                if (shortBtn) shortBtn.classList.remove('active');
                this.renderConditions();
            });
        }
        
        if (shortBtn) {
            shortBtn.addEventListener('click', () => {
                this.currentEntryType = 'short';
                shortBtn.classList.add('active');
                if (longBtn) longBtn.classList.remove('active');
                this.renderConditions();
            });
        }
    },
    
    setupActions() {
        const newBtn = document.getElementById('new-strategy-btn');
        const saveBtn = document.getElementById('save-strategy-btn');
        const loadBtn = document.getElementById('load-strategy-btn');
        const testBtn = document.getElementById('test-strategy-btn');
        const refreshBtn = document.getElementById('refresh-strategy-btn');
        const clearBtn = document.getElementById('clear-strategy-btn');
        const addConditionBtn = document.getElementById('add-condition-btn');
        
        if (newBtn) newBtn.addEventListener('click', () => this.newStrategy());
        if (saveBtn) saveBtn.addEventListener('click', () => this.saveStrategy());
        if (loadBtn) loadBtn.addEventListener('click', () => this.loadStrategy());
        if (testBtn) testBtn.addEventListener('click', () => this.testStrategy());
        if (refreshBtn) refreshBtn.addEventListener('click', () => this.refreshChart());
        if (clearBtn) clearBtn.addEventListener('click', () => this.clearStrategy());
        if (addConditionBtn) addConditionBtn.addEventListener('click', () => this.addCondition());
    },
    
    showTabContent(tab) {
        const contents = document.querySelectorAll('.tab-content');
        contents.forEach(content => {
            content.style.display = content.dataset.tab === tab ? 'block' : 'none';
        });
    },
    
    addCondition() {
        const condition = {
            id: Date.now(),
            indicator1: '',
            operator: '',
            indicator2: '',
            value: ''
        };
        
        if (this.currentTab === 'entry') {
            this.currentStrategy.entry[this.currentEntryType].push(condition);
        } else if (this.currentTab === 'exit') {
            this.currentStrategy.exit[this.currentEntryType].push(condition);
        }
        
        this.renderConditions();
    },
    
    removeCondition(id) {
        if (this.currentTab === 'entry') {
            this.currentStrategy.entry[this.currentEntryType] = 
                this.currentStrategy.entry[this.currentEntryType].filter(c => c.id !== id);
        } else if (this.currentTab === 'exit') {
            this.currentStrategy.exit[this.currentEntryType] = 
                this.currentStrategy.exit[this.currentEntryType].filter(c => c.id !== id);
        }
        
        this.renderConditions();
    },
    
    renderConditions() {
        const container = document.getElementById('conditions-container');
        if (!container) return;
        
        let conditions = [];
        if (this.currentTab === 'entry') {
            conditions = this.currentStrategy.entry[this.currentEntryType];
        } else if (this.currentTab === 'exit') {
            conditions = this.currentStrategy.exit[this.currentEntryType];
        }
        
        if (conditions.length === 0) {
            container.innerHTML = '<div class="empty-state">No conditions added yet</div>';
            return;
        }
        
        container.innerHTML = conditions.map((condition, index) => `
            <div class="condition-item">
                <div class="condition-header">
                    <span class="condition-number">Condition ${index + 1}</span>
                    <button class="condition-remove" onclick="StrategyBuilder.removeCondition(${condition.id})">×</button>
                </div>
                <div class="condition-fields">
                    <select class="form-control" onchange="StrategyBuilder.updateCondition(${condition.id}, 'indicator1', this.value)">
                        <option value="">-- Select Indicator --</option>
                        <option value="price">Price</option>
                        <option value="ema">EMA</option>
                        <option value="sma">SMA</option>
                        <option value="rsi">RSI</option>
                        <option value="macd">MACD</option>
                    </select>
                    <select class="form-control" onchange="StrategyBuilder.updateCondition(${condition.id}, 'operator', this.value)">
                        <option value="">-- Operator --</option>
                        <option value=">">&gt;</option>
                        <option value="<">&lt;</option>
                        <option value=">=">&gt;=</option>
                        <option value="<=">&lt;=</option>
                        <option value="==">==</option>
                        <option value="crosses_above">Crosses Above</option>
                        <option value="crosses_below">Crosses Below</option>
                    </select>
                    <input type="text" class="form-control" placeholder="Value or Indicator" 
                           onchange="StrategyBuilder.updateCondition(${condition.id}, 'value', this.value)">
                </div>
            </div>
        `).join('');
    },
    
    updateCondition(id, field, value) {
        let conditions = [];
        if (this.currentTab === 'entry') {
            conditions = this.currentStrategy.entry[this.currentEntryType];
        } else if (this.currentTab === 'exit') {
            conditions = this.currentStrategy.exit[this.currentEntryType];
        }
        
        const condition = conditions.find(c => c.id === id);
        if (condition) {
            condition[field] = value;
        }
    },
    
    async loadIndicators() {
        // TODO: Load available indicators
        const indicators = ['EMA', 'SMA', 'RSI', 'MACD', 'Bollinger Bands'];
        console.log('Available indicators:', indicators);
    },
    
    newStrategy() {
        if (confirm('Create new strategy? Current work will be lost.')) {
            this.currentStrategy = {
                name: 'My Strategy',
                description: '',
                entry: { long: [], short: [] },
                exit: { long: [], short: [] },
                indicators: [],
                tradingEngine: {}
            };
            this.renderConditions();
            App.showNotification('New strategy created', 'info');
        }
    },
    
    async saveStrategy() {
        const nameInput = document.getElementById('strategy-name');
        if (nameInput) {
            this.currentStrategy.name = nameInput.value;
        }
        
        try {
            const result = await App.apiCall('/strategies', 'POST', this.currentStrategy);
            App.showNotification('Strategy saved successfully', 'success');
        } catch (error) {
            App.showNotification('Failed to save strategy', 'error');
        }
    },
    
    async loadStrategy() {
        // TODO: Implement strategy loading dialog
        App.showNotification('Load strategy feature coming soon', 'info');
    },
    
    async testStrategy() {
        if (this.currentStrategy.entry.long.length === 0 && this.currentStrategy.entry.short.length === 0) {
            App.showNotification('Please add entry conditions first', 'warning');
            return;
        }
        
        try {
            // TODO: Implement strategy testing
            App.showNotification('Testing strategy...', 'info');
            console.log('Testing strategy:', this.currentStrategy);
        } catch (error) {
            App.showNotification('Strategy test failed', 'error');
        }
    },
    
    refreshChart() {
        if (window.chartManager) {
            window.chartManager.loadChartData();
            App.showNotification('Chart refreshed', 'info');
        }
    },
    
    clearStrategy() {
        if (confirm('Clear all conditions?')) {
            if (this.currentTab === 'entry') {
                this.currentStrategy.entry[this.currentEntryType] = [];
            } else if (this.currentTab === 'exit') {
                this.currentStrategy.exit[this.currentEntryType] = [];
            }
            this.renderConditions();
            App.showNotification('Conditions cleared', 'info');
        }
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    StrategyBuilder.init();
    
    // Initialize chart
    if (typeof ChartStrategy !== 'undefined') {
        window.chartStrategy = new ChartStrategy('trading-chart');
        window.chartStrategy.init();
    }
});

// Export for global access
window.StrategyBuilder = StrategyBuilder;
