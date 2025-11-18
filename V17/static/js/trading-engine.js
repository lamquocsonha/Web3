/**
 * Trading Engine Configuration Management
 * Handles saving, loading, and testing engine configurations
 */

// Get current engine configuration
function getEngineConfig() {
    return {
        // Engine Control
        active: document.getElementById('engineActive').checked,
        buy_active: document.getElementById('buyActive').checked,
        short_active: document.getElementById('shortActive').checked,
        
        // Trading Hours
        trading_hours_active: document.getElementById('tradingHoursActive').checked,
        start_time: document.getElementById('startTime').value,
        end_time: document.getElementById('endTime').value,
        base_time: document.getElementById('baseTime').value,
        
        // Order Limits
        order_limits_active: document.getElementById('orderLimitsActive').checked,
        buy_order_limit: parseInt(document.getElementById('buyOrderLimit').value),
        short_order_limit: parseInt(document.getElementById('shortOrderLimit').value),
        
        // Position Sizing
        position_sizing_active: document.getElementById('positionSizingActive').checked,
        position_size: parseFloat(document.getElementById('positionSize').value),
        max_positions: parseInt(document.getElementById('maxPositions').value),
        
        // TP/SL Configuration
        dynamic_tp_sl_active: document.getElementById('dynamicTpSlActive').checked,
        initial_sl: parseFloat(document.getElementById('initialSL').value),
        fee_tax: parseFloat(document.getElementById('feeTax').value),
        
        // Entry/Exit Rules
        no_repaint_active: document.getElementById('noRepaintActive').checked,
        exit_in_candle_active: document.getElementById('exitInCandleActive').checked,
        
        // Pivot Levels
        pivot_levels_active: document.getElementById('pivotLevelsActive').checked,
        hhv_llv_active: document.getElementById('hhvLlvActive').checked,
        
        // Strategy Selection
        signal_strategy: document.getElementById('signalStrategy').value,
        
        // Metadata
        name: `Engine Config ${new Date().toISOString().slice(0, 19)}`,
        created_at: new Date().toISOString()
    };
}

// Set engine configuration
function setEngineConfig(config) {
    // Engine Control
    document.getElementById('engineActive').checked = config.active !== false;
    document.getElementById('buyActive').checked = config.buy_active !== false;
    document.getElementById('shortActive').checked = config.short_active !== false;
    
    // Trading Hours
    if (config.trading_hours_active !== undefined) {
        document.getElementById('tradingHoursActive').checked = config.trading_hours_active;
    }
    if (config.start_time) document.getElementById('startTime').value = config.start_time;
    if (config.end_time) document.getElementById('endTime').value = config.end_time;
    if (config.base_time) document.getElementById('baseTime').value = config.base_time;
    
    // Order Limits
    if (config.order_limits_active !== undefined) {
        document.getElementById('orderLimitsActive').checked = config.order_limits_active;
    }
    if (config.buy_order_limit) {
        document.getElementById('buyOrderLimit').value = config.buy_order_limit;
    }
    if (config.short_order_limit) {
        document.getElementById('shortOrderLimit').value = config.short_order_limit;
    }
    
    // Position Sizing
    if (config.position_sizing_active !== undefined) {
        document.getElementById('positionSizingActive').checked = config.position_sizing_active;
    }
    if (config.position_size) {
        document.getElementById('positionSize').value = config.position_size;
    }
    if (config.max_positions) {
        document.getElementById('maxPositions').value = config.max_positions;
    }
    
    // TP/SL Configuration
    if (config.dynamic_tp_sl_active !== undefined) {
        document.getElementById('dynamicTpSlActive').checked = config.dynamic_tp_sl_active;
    }
    if (config.initial_sl) {
        document.getElementById('initialSL').value = config.initial_sl;
    }
    if (config.fee_tax) {
        document.getElementById('feeTax').value = config.fee_tax;
    }
    
    // Entry/Exit Rules
    if (config.no_repaint_active !== undefined) {
        document.getElementById('noRepaintActive').checked = config.no_repaint_active;
    }
    if (config.exit_in_candle_active !== undefined) {
        document.getElementById('exitInCandleActive').checked = config.exit_in_candle_active;
    }
    
    // Pivot Levels
    if (config.pivot_levels_active !== undefined) {
        document.getElementById('pivotLevelsActive').checked = config.pivot_levels_active;
    }
    if (config.hhv_llv_active !== undefined) {
        document.getElementById('hhvLlvActive').checked = config.hhv_llv_active;
    }
    
    // Strategy Selection
    if (config.signal_strategy) {
        document.getElementById('signalStrategy').value = config.signal_strategy;
    }
}

// Save engine configuration
async function saveEngineConfig() {
    const config = getEngineConfig();
    
    // Validate strategy selection
    if (!config.signal_strategy) {
        alert('⚠️ Please select a signal strategy before saving!');
        return;
    }
    
    // Prompt for config name
    const name = prompt('Enter configuration name:', config.name);
    if (!name) return;
    
    config.name = name;
    
    try {
        const response = await fetch('/api/save-engine-config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        if (result.success) {
            alert('✅ Engine configuration saved successfully!');
            loadSavedConfigs();
        } else {
            alert('❌ Failed to save configuration: ' + result.error);
        }
    } catch (error) {
        console.error('Error saving config:', error);
        alert('❌ Error saving configuration');
    }
}

// Load engine configuration
async function loadEngineConfig() {
    try {
        const response = await fetch('/api/get-engine-configs');
        const result = await response.json();
        
        if (result.success && result.configs.length > 0) {
            // Show config selection dialog
            let options = result.configs.map((cfg, idx) => 
                `${idx + 1}. ${cfg.name} (${cfg.created_at})`
            ).join('\n');
            
            const selection = prompt(`Select configuration to load:\n\n${options}\n\nEnter number:`);
            if (!selection) return;
            
            const idx = parseInt(selection) - 1;
            if (idx >= 0 && idx < result.configs.length) {
                setEngineConfig(result.configs[idx]);
                alert('✅ Configuration loaded successfully!');
            } else {
                alert('❌ Invalid selection');
            }
        } else {
            alert('ℹ️ No saved configurations found');
        }
    } catch (error) {
        console.error('Error loading config:', error);
        alert('❌ Error loading configurations');
    }
}

// Test engine with current configuration
async function testEngine() {
    const config = getEngineConfig();
    
    // Validate
    if (!config.signal_strategy) {
        alert('⚠️ Please select a signal strategy first!');
        return;
    }
    
    console.log('🧪 Testing engine with config:', config);
    alert('🧪 Engine test started! Check console for details.');
    
    try {
        const response = await fetch('/api/test-engine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        if (result.success) {
            alert(`✅ Engine test passed!\n\nResults:\n${JSON.stringify(result.test_results, null, 2)}`);
        } else {
            alert('❌ Engine test failed: ' + result.error);
        }
    } catch (error) {
        console.error('Error testing engine:', error);
        alert('❌ Error testing engine');
    }
}

// Export engine configuration as JSON
function exportEngineConfig() {
    const config = getEngineConfig();
    
    if (!config.signal_strategy) {
        alert('⚠️ Please select a signal strategy before exporting!');
        return;
    }
    
    const dataStr = JSON.stringify(config, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `engine_config_${Date.now()}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    alert('✅ Configuration exported successfully!');
}

// Load saved configurations list
async function loadSavedConfigs() {
    try {
        const response = await fetch('/api/get-engine-configs');
        const result = await response.json();
        
        const container = document.getElementById('engineConfigsList');
        if (!container) return;
        
        if (result.success && result.configs.length > 0) {
            container.innerHTML = result.configs.map((cfg, idx) => `
                <div class="config-item">
                    <div class="config-name">${cfg.name}</div>
                    <div class="config-date">${new Date(cfg.created_at).toLocaleString()}</div>
                    <div class="config-actions">
                        <button class="btn-config-load" onclick="loadConfigById(${idx})">Load</button>
                        <button class="btn-config-delete" onclick="deleteConfig(${idx})">Delete</button>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="no-data">Chưa có config nào</div>';
        }
    } catch (error) {
        console.error('Error loading saved configs:', error);
    }
}

// Load configuration by ID
async function loadConfigById(idx) {
    try {
        const response = await fetch('/api/get-engine-configs');
        const result = await response.json();
        
        if (result.success && result.configs[idx]) {
            setEngineConfig(result.configs[idx]);
            alert('✅ Configuration loaded!');
        }
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

// Delete configuration
async function deleteConfig(idx) {
    if (!confirm('Are you sure you want to delete this configuration?')) return;
    
    try {
        const response = await fetch(`/api/delete-engine-config/${idx}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        if (result.success) {
            alert('✅ Configuration deleted!');
            loadSavedConfigs();
        }
    } catch (error) {
        console.error('Error deleting config:', error);
    }
}

// Load saved configs on page load
document.addEventListener('DOMContentLoaded', () => {
    loadSavedConfigs();
});
