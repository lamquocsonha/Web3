/**
 * STRATEGY BUILDER
 * Handle 4 tabs: Entry, Exit, Indicator, Trading Engine
 */

// Global strategy config
let strategyConfig = {
    name: 'My Strategy',
    description: '',
    indicators: [],
    entry_conditions: {
        long: [],
        short: []
    },
    exit_rules: {
        long: {
            tp_points: 10,
            sl_points: 20,
            trailing_points: 5,
            time_exit: '14:30'
        },
        short: {
            tp_points: 10,
            sl_points: 20,
            trailing_points: 5,
            time_exit: '14:30'
        }
    },
    trading_engine: {
        entry_price_type: 'C',
        entry_after_candle: [1],
        position_mode: 'long_only'
    }
};

let currentEntryDirection = 'long';
let currentExitDirection = 'long';

function initStrategyBuilder() {
    loadStrategyFromLocalStorage();
    renderAllTabs();
}

function switchPanel(tabName) {
    document.querySelectorAll('.panel-tab').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    document.querySelectorAll('.panel-content').forEach(panel => panel.classList.add('hidden'));
    
    const panel = document.getElementById(tabName + 'Panel');
    if (panel) panel.classList.remove('hidden');
}

function switchEntryDirection(direction) {
    currentEntryDirection = direction;
    document.getElementById('longEntryTab').classList.toggle('active', direction === 'long');
    document.getElementById('shortEntryTab').classList.toggle('active', direction === 'short');
    document.getElementById('longEntryContent').classList.toggle('hidden', direction !== 'long');
    document.getElementById('shortEntryContent').classList.toggle('hidden', direction !== 'short');
    renderConditions(direction);
}

function switchExitDirection(direction) {
    currentExitDirection = direction;
    document.getElementById('longExitTab').classList.toggle('active', direction === 'long');
    document.getElementById('shortExitTab').classList.toggle('active', direction === 'short');
    document.getElementById('longExitContent').classList.toggle('hidden', direction !== 'long');
    document.getElementById('shortExitContent').classList.toggle('hidden', direction !== 'short');
}

function addCondition(direction) {
    const group = {
        name: `${direction === 'long' ? 'Buy' : 'Short'}_${strategyConfig.entry_conditions[direction].length + 1}`,
        conditions: [{ left: 'close', leftOffset: 0, operator: '>', right: 'open', rightOffset: 0, logic: 'AND' }]
    };
    strategyConfig.entry_conditions[direction].push(group);
    renderConditions(direction);
    saveStrategyToLocalStorage();
}

function removeConditionGroup(direction, index) {
    if (confirm('Remove this condition group?')) {
        strategyConfig.entry_conditions[direction].splice(index, 1);
        renderConditions(direction);
        saveStrategyToLocalStorage();
    }
}

function renderConditions(direction) {
    const container = document.getElementById(direction === 'long' ? 'longConditions' : 'shortConditions');
    if (!container) return;
    
    const conditions = strategyConfig.entry_conditions[direction];
    if (conditions.length === 0) {
        container.innerHTML = '<p style="color: #787b86;">No conditions yet.</p>';
        return;
    }
    
    let html = '';
    conditions.forEach((group, idx) => {
        html += `
        <div class="condition-group" style="background: #1e222d; padding: 15px; border-radius: 6px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <input type="text" value="${group.name}" style="background: #131722; border: 1px solid #2a2e39; padding: 8px; border-radius: 4px; color: #d1d4dc;">
                <button onclick="removeConditionGroup('${direction}', ${idx})" style="background: #ef5350; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;">🗑️</button>
            </div>
            <div style="font-size: 12px; color: #787b86;">${group.conditions.length} condition(s)</div>
        </div>`;
    });
    container.innerHTML = html;
}

function renderAllTabs() {
    renderConditions('long');
    renderConditions('short');
}

function newStrategy() {
    if (confirm('Create new strategy?')) {
        strategyConfig = {
            name: 'New Strategy',
            description: '',
            indicators: [],
            entry_conditions: { long: [], short: [] },
            exit_rules: {
                long: { tp_points: 10, sl_points: 20, trailing_points: 5, time_exit: '14:30' },
                short: { tp_points: 10, sl_points: 20, trailing_points: 5, time_exit: '14:30' }
            },
            trading_engine: { entry_price_type: 'C', entry_after_candle: [1], position_mode: 'long_only' }
        };
        document.getElementById('strategyName').value = 'New Strategy';
        document.getElementById('strategyDescription').value = '';
        renderAllTabs();
    }
}

async function saveStrategy() {
    strategyConfig.name = document.getElementById('strategyName').value || 'Unnamed';
    strategyConfig.description = document.getElementById('strategyDescription').value || '';
    
    try {
        const response = await fetch('/api/strategies', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(strategyConfig)
        });
        const result = await response.json();
        if (result.status === 'success') {
            alert('✅ Saved: ' + result.filename);
            saveStrategyToLocalStorage();
        } else {
            alert('❌ Error: ' + result.message);
        }
    } catch (error) {
        alert('❌ Failed to save');
    }
}

async function loadStrategy() {
    try {
        const response = await fetch('/api/strategies');
        const result = await response.json();
        if (result.status !== 'success' || !result.strategies.length) {
            alert('No saved strategies');
            return;
        }
        let html = 'Select:\n\n';
        result.strategies.forEach((s, i) => html += `${i + 1}. ${s.name}\n`);
        const index = prompt(html);
        if (!index) return;
        
        const selected = result.strategies[parseInt(index) - 1];
        const loadResponse = await fetch(`/api/strategies/${selected.filename}`);
        const loadResult = await loadResponse.json();
        
        if (loadResult.status === 'success') {
            strategyConfig = loadResult.strategy;
            document.getElementById('strategyName').value = strategyConfig.name;
            document.getElementById('strategyDescription').value = strategyConfig.description || '';
            renderAllTabs();
            alert('✅ Loaded: ' + strategyConfig.name);
        }
    } catch (error) {
        alert('❌ Failed to load');
    }
}

function openAutoGenerateModal() {
    document.getElementById('autoGenerateModal').style.display = 'flex';
}

function closeAutoGenerateModal() {
    document.getElementById('autoGenerateModal').style.display = 'none';
}

async function generateStrategy() {
    const config = {
        current_strategy: strategyConfig,
        long_signals: parseInt(document.getElementById('autoGenLongSignals').value) || 2,
        short_signals: parseInt(document.getElementById('autoGenShortSignals').value) || 2,
        indicators_per_signal: parseInt(document.getElementById('autoGenIndicatorsPerSignal').value) || 2,
        profit_levels: parseInt(document.getElementById('autoGenProfitLevels').value) || 4,
        profit_step: parseInt(document.getElementById('autoGenProfitStep').value) || 3,
        keep_indicators: document.getElementById('autoGenKeepIndicators').checked,
        randomize_tpsl: document.getElementById('autoGenRandomizeTPSL').checked
    };
    
    try {
        const response = await fetch('/api/auto-generate-strategy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        const result = await response.json();
        
        if (result.success) {
            strategyConfig = result.strategy;
            document.getElementById('strategyName').value = strategyConfig.name;
            renderAllTabs();
            closeAutoGenerateModal();
            alert(`✅ Generated!\nLong: ${strategyConfig.entry_conditions.long.length}\nShort: ${strategyConfig.entry_conditions.short.length}`);
        } else {
            alert('❌ Error: ' + result.error);
        }
    } catch (error) {
        alert('❌ Failed');
    }
}

function saveStrategyToLocalStorage() {
    try {
        localStorage.setItem('currentStrategy', JSON.stringify(strategyConfig));
    } catch (e) {}
}

function loadStrategyFromLocalStorage() {
    try {
        const saved = localStorage.getItem('currentStrategy');
        if (saved) strategyConfig = JSON.parse(saved);
    } catch (e) {}
}

document.addEventListener('DOMContentLoaded', initStrategyBuilder);
