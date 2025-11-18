// Optimize Module
let currentCSVFile = null;
let currentStrategy = null;
let currentStrategyData = null;
let selectedTimeframe = '1m'; // Selected timeframe for uploaded data
let selectedParameters = new Map(); // Map of parameter path -> {min, max, step, type, originalValue}
let parameters = [];
let progressChart = null;
let bestParams = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadUploadedFiles();
    loadStrategies();
    setupEventListeners();
    restoreOptimizeState();
});

function setupEventListeners() {
    // Button to trigger timeframe modal first (like index/strategy/backtest pages)
    document.getElementById('btnChooseFile').addEventListener('click', function() {
        showTimeframeModalForOptimize();
    });

    // CSV file upload (will be triggered after timeframe selection)
    document.getElementById('csvFile').addEventListener('change', handleCSVUpload);

    // Strategy selection
    document.getElementById('strategySelect').addEventListener('change', async function() {
        const strategyFile = this.value;
        if (strategyFile) {
            await loadStrategyParameters(strategyFile);
        } else {
            clearParameterTree();
        }
        checkReadyToOptimize();
    });

    // Add parameter button (if exists - for old optimize page compatibility)
    const addParamBtn = document.getElementById('addParam');
    if (addParamBtn) {
        addParamBtn.addEventListener('click', addParameter);
    }

    // Run optimize button
    const runOptBtn = document.getElementById('runOptimize');
    if (runOptBtn) {
        runOptBtn.addEventListener('click', startOptimization);
    }

    // Save state when optimization settings change
    ['populationSize', 'numGenerations', 'mutationRate', 'crossoverRate', 'targetMetric', 'maxResults'].forEach(id => {
        const elem = document.getElementById(id);
        if (elem) {
            elem.addEventListener('change', saveOptimizeState);
        }
    });
}

/**
 * Show timeframe modal for optimize (separate from other pages)
 */
function showTimeframeModalForOptimize() {
    console.log('📊 [Optimize] Showing timeframe modal...');

    const modal = document.getElementById('timeframeModal');
    if (modal) {
        modal.style.display = 'flex';
        console.log('✅ [Optimize] Modal displayed');
    } else {
        console.error('❌ [Optimize] Modal not found!');
        // Fallback: open file picker directly
        document.getElementById('csvFile').click();
    }
}

/**
 * Close timeframe modal
 */
function closeTimeframeModalOptimize() {
    const modal = document.getElementById('timeframeModal');
    if (modal) {
        modal.style.display = 'none';
    }
    console.log('❌ [Optimize] User cancelled timeframe selection');
}

/**
 * Confirm timeframe and open file picker for optimize
 */
function confirmTimeframeAndUploadOptimize() {
    const timeframeSelect = document.getElementById('timeframeSelect');
    if (timeframeSelect) {
        selectedTimeframe = timeframeSelect.value;
        console.log('✅ [Optimize] Selected timeframe:', selectedTimeframe);
    }

    // Close modal
    const modal = document.getElementById('timeframeModal');
    if (modal) {
        modal.style.display = 'none';
    }

    // Open file picker
    const fileInput = document.getElementById('csvFile');
    if (fileInput) {
        fileInput.click();
    }
}

async function loadUploadedFiles() {
    try {
        // Restore saved file and timeframe from localStorage (shared with backtest)
        const savedFile = localStorage.getItem('backtestSelectedFile');
        const savedTimeframe = localStorage.getItem('backtestDataTimeframe');

        if (savedFile) {
            currentCSVFile = savedFile;

            const btnFileName = document.getElementById('csvFileName');
            const fileBtn = document.getElementById('btnChooseFile');

            if (btnFileName && fileBtn) {
                // Truncate filename if > 30 chars
                const displayName = savedFile.length > 30
                    ? savedFile.substring(0, 27) + '...'
                    : savedFile;
                btnFileName.textContent = displayName;

                // Set full filename as tooltip
                fileBtn.title = savedFile;
                fileBtn.style.borderColor = '#2962ff';
                fileBtn.style.background = '#2e3241';
            }

            // Restore timeframe
            if (savedTimeframe) {
                selectedTimeframe = savedTimeframe;
                updateTimeframeDisplay(savedTimeframe);
            }

            checkReadyToOptimize();
        }
    } catch (error) {
        console.error('Error loading uploaded files:', error);
    }
}

/**
 * Update timeframe display in sidebar
 */
function updateTimeframeDisplay(timeframe) {
    // Find or create timeframe display element in sidebar
    let timeframeDisplay = document.getElementById('dataTimeframeDisplay');

    if (!timeframeDisplay) {
        // Create timeframe display after file upload section
        const fileGroup = document.querySelector('.form-group');
        if (fileGroup && fileGroup.parentElement) {
            timeframeDisplay = document.createElement('div');
            timeframeDisplay.id = 'dataTimeframeDisplay';
            timeframeDisplay.style.cssText = `
                padding: 8px 12px;
                background: #2a2e39;
                border: 1px solid #434651;
                border-radius: 4px;
                margin-top: 10px;
                font-size: 13px;
                color: #d1d4dc;
            `;
            fileGroup.parentElement.insertBefore(timeframeDisplay, fileGroup.nextSibling);
        }
    }

    if (timeframeDisplay) {
        timeframeDisplay.innerHTML = `
            <span style="color: #787b86;">📊 Data Timeframe:</span>
            <span style="color: #2962ff; font-weight: 600; margin-left: 8px;">${timeframe}</span>
        `;
    }
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

async function loadStrategies() {
    try {
        const response = await fetch('/list_strategies');
        
        if (!response.ok) {
            console.error('Failed to fetch strategies:', response.status);
            return;
        }
        
        const data = await response.json();
        console.log('Strategies loaded:', data);
        
        const select = document.getElementById('strategySelect');
        select.innerHTML = '<option value="">Select strategy...</option>';
        
        if (data.success && data.strategies && data.strategies.length > 0) {
            data.strategies.forEach(strategy => {
                const option = document.createElement('option');
                option.value = strategy.filename;
                option.textContent = strategy.name;
                select.appendChild(option);
            });
            console.log(`Loaded ${data.strategies.length} strategies`);
        } else {
            console.log('No strategies found');
        }
    } catch (error) {
        console.error('Error loading strategies:', error);
    }
}

async function handleCSVUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Show loading notification
    showNotification('⏳ Đang upload ' + file.name + '...', 'info');
    
    // Update UI with filename - show uploading
    const btnFileName = document.getElementById('csvFileName');
    const fileBtn = document.getElementById('btnChooseFile');
    
    btnFileName.textContent = `Uploading ${file.name}...`;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/upload_data', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentCSVFile = result.filename;

            // Save to localStorage
            localStorage.setItem('backtestSelectedFile', result.filename);
            localStorage.setItem('backtestDataTimeframe', selectedTimeframe);

            // Update button with uploaded filename
            const displayName = result.filename.length > 30
                ? result.filename.substring(0, 27) + '...'
                : result.filename;
            btnFileName.textContent = displayName;

            // Set full filename as tooltip
            fileBtn.title = result.filename;
            fileBtn.style.borderColor = '#2962ff';
            fileBtn.style.background = '#2e3241';

            // Update timeframe display
            updateTimeframeDisplay(selectedTimeframe);

            showNotification('✅ CSV uploaded successfully!', 'success');

            checkReadyToOptimize();
        } else {
            btnFileName.textContent = 'Choose CSV File...';
            showNotification('❌ ' + result.error, 'error');
            currentCSVFile = null;
        }
    } catch (error) {
        btnFileName.textContent = 'Choose CSV File...';
        showNotification('❌ Upload failed: ' + error.message, 'error');
        currentCSVFile = null;
    }
    
    // Reset file input
    event.target.value = '';
}

// ==================== PARAMETER TREE FUNCTIONS ====================

async function loadStrategyParameters(strategyFile) {
    try {
        addTerminalLine(`📊 Loading strategy: ${strategyFile}`, 'info');

        const response = await fetch(`/strategies/${strategyFile}`);
        if (!response.ok) {
            throw new Error('Failed to load strategy');
        }

        currentStrategyData = await response.json();
        currentStrategy = strategyFile;

        console.log('Strategy loaded:', currentStrategyData);

        // Build parameter tree from strategy
        buildParameterTree(currentStrategyData);

        addTerminalLine('✅ Strategy loaded successfully', 'success');
        addTerminalLine(`📋 Found ${selectedParameters.size} optimizable parameters`, 'info');

    } catch (error) {
        console.error('Error loading strategy:', error);
        addTerminalLine('❌ Failed to load strategy: ' + error.message, 'error');
        clearParameterTree();
    }
}

function buildParameterTree(strategy) {
    const entryParamTree = document.getElementById('entryParamTree');
    const exitParamTree = document.getElementById('exitParamTree');

    if (!entryParamTree || !exitParamTree) return;

    // Clear existing trees
    selectedParameters.clear();

    // Build ENTRY tab content
    let entryHTML = '';

    // 1. ENTRY CONDITIONS - LONG
    if (strategy.entry_conditions && strategy.entry_conditions.long) {
        entryHTML += buildEntrySection('Long Entry', strategy.entry_conditions.long, 'long');
    }

    // 2. ENTRY CONDITIONS - SHORT
    if (strategy.entry_conditions && strategy.entry_conditions.short) {
        entryHTML += buildEntrySection('Short Entry', strategy.entry_conditions.short, 'short');
    }

    entryParamTree.innerHTML = entryHTML || '<div style="text-align: center; color: #787b86; padding: 30px 10px; font-size: 12px;">No entry parameters found</div>';

    // Build EXIT tab content
    let exitHTML = '';

    // 3. EXIT RULES - LONG
    if (strategy.exit_rules && strategy.exit_rules.long) {
        exitHTML += buildExitSection('Long Exit', strategy.exit_rules.long, 'long');
    }

    // 4. EXIT RULES - SHORT
    if (strategy.exit_rules && strategy.exit_rules.short) {
        exitHTML += buildExitSection('Short Exit', strategy.exit_rules.short, 'short');
    }

    exitParamTree.innerHTML = exitHTML || '<div style="text-align: center; color: #787b86; padding: 30px 10px; font-size: 12px;">No exit parameters found</div>';
}

function buildEntrySection(title, entryData, direction) {
    if (!entryData || entryData.length === 0) return '';

    let html = `
        <div class="tree-section">
            <div class="tree-header" onclick="toggleTree(this)">
                <span><strong>${direction === 'long' ? '🟢' : '🔴'} ${title}</strong></span>
                <span class="arrow">▼</span>
            </div>
            <div class="tree-content">
    `;

    // Entry conditions are groups of signals
    entryData.forEach((group, groupIndex) => {
        const groupName = group.name || `Signal ${groupIndex + 1}`;
        html += `<div style="margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #2a2e39;">
            <div style="font-size: 12px; color: #d1d4dc; margin-bottom: 6px; font-weight: 600;">${groupName}</div>
        `;

        // Each group has conditions
        if (group.conditions && group.conditions.length > 0) {
            group.conditions.forEach((condition, condIndex) => {
                // Only show conditions with numeric comparisons that can be optimized
                if (condition.left && condition.operator && condition.right) {
                    const paramPath = `entry_conditions.${direction}.${groupIndex}.conditions.${condIndex}`;
                    const paramLabel = `${condition.left} ${condition.operator} ${condition.right}`;

                    html += `
                        <div class="tree-item">
                            <label>
                                <input type="checkbox" onchange="toggleParameter('${paramPath}', this.checked, 'condition')" />
                                <span style="font-size: 12px;">${paramLabel}</span>
                            </label>
                            <div class="param-range" style="display: none;" id="range-${paramPath.replace(/\./g, '-')}">
                                <div>
                                    <label>Min</label>
                                    <input type="number" class="param-min" data-path="${paramPath}" value="0" step="0.1" />
                                </div>
                                <div>
                                    <label>Max</label>
                                    <input type="number" class="param-max" data-path="${paramPath}" value="100" step="0.1" />
                                </div>
                                <div>
                                    <label>Step</label>
                                    <input type="number" class="param-step" data-path="${paramPath}" value="1" step="0.1" />
                                </div>
                            </div>
                        </div>
                    `;
                }
            });
        }

        html += `</div>`;
    });

    html += `
            </div>
        </div>
    `;

    return html;
}

function buildExitSection(title, exitData, direction) {
    if (!exitData) return '';

    let html = `
        <div class="tree-section">
            <div class="tree-header" onclick="toggleTree(this)">
                <span><strong>${direction === 'long' ? '🟢' : '🔴'} ${title}</strong></span>
                <span class="arrow">▼</span>
            </div>
            <div class="tree-content">
    `;

    // TP/SL Table
    if (exitData.tp_sl_table && exitData.tp_sl_table.length > 0) {
        exitData.tp_sl_table.forEach((tpsl, index) => {
            const prefix = `exit_rules.${direction}.tp_sl_table.${index}`;

            // Take Profit
            if (tpsl.tp !== undefined) {
                const tpPath = `${prefix}.tp`;
                html += `
                    <div class="tree-item">
                        <label>
                            <input type="checkbox" onchange="toggleParameter('${tpPath}', this.checked, 'exit')" />
                            <span>📈 Take Profit (${tpsl.tp} pts)</span>
                        </label>
                        <div class="param-range" style="display: none;" id="range-${tpPath.replace(/\./g, '-')}">
                            <div>
                                <label>Min</label>
                                <input type="number" class="param-min" data-path="${tpPath}" value="${Math.max(5, tpsl.tp * 0.5)}" step="1" />
                            </div>
                            <div>
                                <label>Max</label>
                                <input type="number" class="param-max" data-path="${tpPath}" value="${tpsl.tp * 2}" step="1" />
                            </div>
                            <div>
                                <label>Step</label>
                                <input type="number" class="param-step" data-path="${tpPath}" value="1" step="0.1" />
                            </div>
                        </div>
                    </div>
                `;
            }

            // Stop Loss
            if (tpsl.sl !== undefined) {
                const slPath = `${prefix}.sl`;
                html += `
                    <div class="tree-item">
                        <label>
                            <input type="checkbox" onchange="toggleParameter('${slPath}', this.checked, 'exit')" />
                            <span>📉 Stop Loss (${tpsl.sl} pts)</span>
                        </label>
                        <div class="param-range" style="display: none;" id="range-${slPath.replace(/\./g, '-')}">
                            <div>
                                <label>Min</label>
                                <input type="number" class="param-min" data-path="${slPath}" value="${Math.max(1, tpsl.sl * 0.5)}" step="0.1" />
                            </div>
                            <div>
                                <label>Max</label>
                                <input type="number" class="param-max" data-path="${slPath}" value="${tpsl.sl * 2}" step="0.1" />
                            </div>
                            <div>
                                <label>Step</label>
                                <input type="number" class="param-step" data-path="${slPath}" value="0.1" step="0.1" />
                            </div>
                        </div>
                    </div>
                `;
            }

            // Trailing Stop
            if (tpsl.trailing !== undefined && tpsl.trailing > 0) {
                const trailPath = `${prefix}.trailing`;
                html += `
                    <div class="tree-item">
                        <label>
                            <input type="checkbox" onchange="toggleParameter('${trailPath}', this.checked, 'exit')" />
                            <span>🔄 Trailing (${tpsl.trailing} pts)</span>
                        </label>
                        <div class="param-range" style="display: none;" id="range-${trailPath.replace(/\./g, '-')}">
                            <div>
                                <label>Min</label>
                                <input type="number" class="param-min" data-path="${trailPath}" value="${Math.max(1, tpsl.trailing * 0.5)}" step="0.1" />
                            </div>
                            <div>
                                <label>Max</label>
                                <input type="number" class="param-max" data-path="${trailPath}" value="${tpsl.trailing * 2}" step="0.1" />
                            </div>
                            <div>
                                <label>Step</label>
                                <input type="number" class="param-step" data-path="${trailPath}" value="0.1" step="0.1" />
                            </div>
                        </div>
                    </div>
                `;
            }
        });
    }

    html += `
            </div>
        </div>
    `;

    return html;
}

// buildIndicatorsSection removed - indicators are no longer optimizable in this UI

function toggleParameter(path, checked, type) {
    const rangeDiv = document.getElementById(`range-${path.replace(/\./g, '-')}`);

    if (checked) {
        // Show range inputs
        if (rangeDiv) {
            rangeDiv.style.display = 'grid';
        }

        // Get range values
        const minInput = document.querySelector(`.param-min[data-path="${path}"]`);
        const maxInput = document.querySelector(`.param-max[data-path="${path}"]`);
        const stepInput = document.querySelector(`.param-step[data-path="${path}"]`);

        // Get original value from strategy data
        let originalValue = null;
        if (currentStrategyData) {
            originalValue = getValueByPath(currentStrategyData, path);
        }

        if (minInput && maxInput && stepInput) {
            selectedParameters.set(path, {
                min: parseFloat(minInput.value),
                max: parseFloat(maxInput.value),
                step: parseFloat(stepInput.value),
                type: type,
                originalValue: originalValue
            });

            // Update listeners to track changes
            const updateParam = () => {
                selectedParameters.set(path, {
                    min: parseFloat(minInput.value),
                    max: parseFloat(maxInput.value),
                    step: parseFloat(stepInput.value),
                    type: type,
                    originalValue: originalValue
                });
            };

            minInput.addEventListener('input', updateParam);
            maxInput.addEventListener('input', updateParam);
            stepInput.addEventListener('input', updateParam);
        }

        addTerminalLine(`✅ Selected: ${path} (original: ${originalValue})`, 'success');
    } else {
        // Hide range inputs
        if (rangeDiv) {
            rangeDiv.style.display = 'none';
        }

        selectedParameters.delete(path);
        addTerminalLine(`❌ Deselected: ${path}`, 'info');
    }

    checkReadyToOptimize();
    saveOptimizeState();
}

// Helper function to get value from object by path string
function getValueByPath(obj, path) {
    const keys = path.split('.');
    let value = obj;

    for (const key of keys) {
        if (value && typeof value === 'object') {
            value = value[key];
        } else {
            return null;
        }
    }

    return value;
}

function clearParameterTree() {
    const entryParamTree = document.getElementById('entryParamTree');
    const exitParamTree = document.getElementById('exitParamTree');

    if (entryParamTree) {
        entryParamTree.innerHTML = '<div style="text-align: center; color: #787b86; padding: 30px 10px; font-size: 12px;">Select a strategy to view entry parameters</div>';
    }

    if (exitParamTree) {
        exitParamTree.innerHTML = '<div style="text-align: center; color: #787b86; padding: 30px 10px; font-size: 12px;">Select a strategy to view exit parameters</div>';
    }

    selectedParameters.clear();
    currentStrategyData = null;
}

function addParameter() {
    const paramId = Date.now();
    const paramDiv = document.createElement('div');
    paramDiv.className = 'param-item';
    paramDiv.dataset.paramId = paramId;
    paramDiv.innerHTML = `
        <div class="param-row">
            <input type="text" class="param-path" placeholder="Parameter path (e.g., indicators.0.params.period)" />
            <button class="btn-remove" onclick="removeParameter(${paramId})">❌</button>
        </div>
        <div class="param-row">
            <input type="number" class="param-min" placeholder="Min" step="any" />
            <input type="number" class="param-max" placeholder="Max" step="any" />
            <input type="number" class="param-step" placeholder="Step" value="1" step="any" />
            <select class="param-type">
                <option value="int">Int</option>
                <option value="float">Float</option>
            </select>
        </div>
    `;
    
    document.getElementById('paramsList').appendChild(paramDiv);
    parameters.push(paramId);
    checkReadyToOptimize();
}

function removeParameter(paramId) {
    const paramDiv = document.querySelector(`[data-param-id="${paramId}"]`);
    if (paramDiv) {
        paramDiv.remove();
        parameters = parameters.filter(id => id !== paramId);
        checkReadyToOptimize();
    }
}

function checkReadyToOptimize() {
    const strategySelected = document.getElementById('strategySelect').value;
    const hasParams = selectedParameters.size > 0;
    const canRun = currentCSVFile && strategySelected && hasParams;

    const runBtn = document.getElementById('runOptimize');
    if (runBtn) {
        runBtn.disabled = !canRun;
        runBtn.style.opacity = canRun ? '1' : '0.5';
        runBtn.style.cursor = canRun ? 'pointer' : 'not-allowed';
    }

    // Also enable/disable Auto Optimization button
    const autoBtn = document.getElementById('runAutoOptimize');
    if (autoBtn) {
        autoBtn.disabled = !canRun;
        autoBtn.style.opacity = canRun ? '1' : '0.5';
        autoBtn.style.cursor = canRun ? 'pointer' : 'not-allowed';
    }
}

function collectParameters() {
    const paramRanges = [];

    // Use selectedParameters Map (new tree system)
    if (selectedParameters.size > 0) {
        for (const [path, config] of selectedParameters.entries()) {
            paramRanges.push({
                path: path,
                min: config.min,
                max: config.max,
                step: config.step,
                type: config.type === 'indicator' ? 'int' : 'float' // Default type based on param type
            });
        }
        return paramRanges;
    }

    // Fallback to old DOM-based collection (for backward compatibility)
    document.querySelectorAll('.param-item').forEach(item => {
        const path = item.querySelector('.param-path').value.trim();
        const min = parseFloat(item.querySelector('.param-min').value);
        const max = parseFloat(item.querySelector('.param-max').value);
        const step = parseFloat(item.querySelector('.param-step').value);
        const typeSelect = item.querySelector('.param-type');
        const type = typeSelect ? typeSelect.value : 'float';

        if (path && !isNaN(min) && !isNaN(max)) {
            paramRanges.push({
                path: path,
                min: min,
                max: max,
                step: step,
                type: type
            });
        }
    });

    return paramRanges;
}

// Alias for compatibility with new optimize_new.html
function startOptimization() {
    return runOptimize();
}

async function runOptimize() {
    const strategyFile = document.getElementById('strategySelect').value;
    const populationSize = parseInt(document.getElementById('populationSize').value);
    const generations = parseInt(document.getElementById('generations').value);
    const timeframe = document.getElementById('timeframe').value;
    const paramRanges = collectParameters();

    if (paramRanges.length === 0) {
        showNotification('⚠️ Please select at least one parameter to optimize', 'warning');
        addTerminalLine('❌ No parameters selected', 'error');
        return;
    }

    // Reset UI for new optimization run
    resetOptimizationUI();

    addTerminalLine('🚀 Starting optimization...', 'success');
    addTerminalLine(`📊 Strategy: ${strategyFile}`, 'info');
    addTerminalLine(`⏰ Timeframe: ${timeframe}`, 'info');
    addTerminalLine(`🎯 Parameters: ${paramRanges.length}`, 'info');
    paramRanges.forEach((param, idx) => {
        addTerminalLine(`   ${idx + 1}. ${param.path}: [${param.min}, ${param.max}] step ${param.step}`, 'info');
    });
    addTerminalLine(`👥 Population: ${populationSize}`, 'info');
    addTerminalLine(`🔄 Generations: ${generations}`, 'info');
    addTerminalLine('─'.repeat(50), 'info');

    // Update UI elements
    const totalGenEl = document.getElementById('totalGen');
    if (totalGenEl) totalGenEl.textContent = generations;

    // Show loading
    const btn = document.getElementById('runOptimize');
    const originalText = btn.innerHTML;
    btn.innerHTML = '⏳ Optimizing...';
    btn.disabled = true;

    // Track timing
    const startTime = Date.now();
    let timeInterval = null;

    try {
        // Start time tracker
        timeInterval = setInterval(() => {
            updateElapsedTime(startTime);
        }, 1000);

        const response = await fetch('/run_optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                csv_file: currentCSVFile,
                strategy_file: strategyFile,
                param_ranges: paramRanges,
                population_size: populationSize,
                generations: generations,
                timeframe: timeframe
            })
        });

        const result = await response.json();

        if (result.success) {
            clearInterval(timeInterval);

            addTerminalLine('─'.repeat(50), 'info');
            addTerminalLine('✅ Optimization completed successfully!', 'success');
            addTerminalLine(`⏱️  Total time: ${formatTime(Date.now() - startTime)}`, 'info');
            addTerminalLine(`🏆 Best fitness: ${result.best_fitness.toFixed(4)}`, 'success');

            bestParams = result.best_params;
            displayResults(result);
            showNotification('✅ Optimization completed!', 'success');
        } else {
            clearInterval(timeInterval);
            addTerminalLine('❌ Optimization failed: ' + result.error, 'error');
            showNotification('❌ ' + result.error, 'error');
        }
    } catch (error) {
        clearInterval(timeInterval);
        addTerminalLine('❌ Optimization failed: ' + error.message, 'error');
        showNotification('❌ Optimization failed: ' + error.message, 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function resetOptimizationUI() {
    // Note: Progress indicators, metrics, and best solution display have been removed from UI
    // Only reset results table

    // Clear results table
    const resultsBody = document.getElementById('resultsTableBody');
    if (resultsBody) {
        resultsBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #787b86; padding: 20px;">Optimization running...</td></tr>';
    }
}

function updateElapsedTime(startTime) {
    // Time display removed from UI - keeping function for terminal logging only
    const elapsed = Date.now() - startTime;
    return formatTime(elapsed);
}

function formatTime(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) {
        return `${hours}:${String(minutes % 60).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
    } else {
        return `${String(minutes).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
    }
}

function displayResults(result) {
    // Note: Progress bar, metrics grid, and best solution panel have been removed from UI
    // Results are now shown in terminal and results table only

    // Log results to terminal
    addTerminalLine('─'.repeat(50), 'info');
    addTerminalLine('📊 OPTIMIZATION RESULTS', 'success');
    addTerminalLine('─'.repeat(50), 'info');
    addTerminalLine(`🏆 Best Fitness: ${result.best_fitness.toFixed(4)}`, 'success');

    if (result.backtest_results) {
        const br = result.backtest_results;
        addTerminalLine(`📈 Win Rate: ${br.win_rate.toFixed(1)}%`, br.win_rate >= 50 ? 'success' : 'warning');
        addTerminalLine(`💰 Total Return: ${br.total_return.toFixed(2)} pts`, br.total_return >= 0 ? 'success' : 'error');
        addTerminalLine(`📉 Max Drawdown: ${br.max_drawdown.toFixed(1)}%`, 'error');
        addTerminalLine(`🎯 Profit Factor: ${br.profit_factor.toFixed(2)}`, br.profit_factor >= 1.5 ? 'success' : 'warning');
    }

    // Log best parameters to terminal
    addTerminalLine('─'.repeat(50), 'info');
    addTerminalLine('🎯 BEST PARAMETERS', 'success');
    addTerminalLine('─'.repeat(50), 'info');
    for (const [param, optimizedValue] of Object.entries(result.best_params)) {
        const paramConfig = selectedParameters.get(param);
        const originalValue = paramConfig ? paramConfig.originalValue : null;

        const shortParam = param.split('.').slice(-2).join('.');
        const displayOptimized = typeof optimizedValue === 'number' ? optimizedValue.toFixed(3) : optimizedValue;
        const displayOriginal = originalValue !== null && typeof originalValue === 'number' ? originalValue.toFixed(3) : (originalValue || '-');

        if (originalValue !== null && typeof originalValue === 'number' && typeof optimizedValue === 'number') {
            const diff = optimizedValue - originalValue;
            const changeText = diff > 0 ? `+${diff.toFixed(2)}` : diff.toFixed(2);
            addTerminalLine(`  ${shortParam}: ${displayOriginal} → ${displayOptimized} (${changeText})`, diff > 0 ? 'success' : (diff < 0 ? 'warning' : 'info'));
        } else {
            addTerminalLine(`  ${shortParam}: ${displayOriginal} → ${displayOptimized}`, 'info');
        }
    }
    addTerminalLine('─'.repeat(50), 'info');

    // Display results table
    if (result.final_population) {
        displayOptimizationResults(result.final_population);
        addTerminalLine(`📊 Results table populated with top ${Math.min(result.final_population.length, 10)} solutions`, 'info');
    }

    // Save state for persistence
    saveOptimizeState();
}

// Update to match new results table structure
function displayOptimizationResults(population) {
    const tbody = document.getElementById('resultsTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    // Get top results (limited by maxResults setting)
    const maxResults = parseInt(document.getElementById('maxResults')?.value || 10);
    const topResults = population.slice(0, maxResults);

    topResults.forEach((individual, index) => {
        const row = tbody.insertRow();

        // Rank
        const rankCell = row.insertCell();
        rankCell.textContent = index + 1;
        rankCell.style.fontWeight = index === 0 ? 'bold' : 'normal';
        rankCell.style.color = index === 0 ? '#2962ff' : '#d1d4dc';

        // Extract stats (from individual backtest results if available)
        const stats = individual.backtest_results || {};

        // Win Rate
        const winRateCell = row.insertCell();
        const winRate = stats.win_rate || 0;
        winRateCell.textContent = winRate.toFixed(1) + '%';
        winRateCell.style.color = winRate >= 50 ? '#26a69a' : '#ef5350';

        // Profit (pts)
        const profitCell = row.insertCell();
        const profit = stats.total_return || 0;
        profitCell.textContent = (profit >= 0 ? '+' : '') + profit.toFixed(2);
        profitCell.style.color = profit >= 0 ? '#26a69a' : '#ef5350';

        // Drawdown
        const ddCell = row.insertCell();
        const dd = stats.max_drawdown || 0;
        ddCell.textContent = dd.toFixed(1) + '%';
        ddCell.style.color = '#ef5350';

        // Profit Factor
        const pfCell = row.insertCell();
        const pf = stats.profit_factor || 0;
        pfCell.textContent = pf.toFixed(2);
        pfCell.style.color = pf > 1 ? '#26a69a' : '#787b86';

        // Trades
        const tradesCell = row.insertCell();
        tradesCell.textContent = stats.total_trades || 0;

        // Fitness
        const fitnessCell = row.insertCell();
        fitnessCell.textContent = individual.fitness.toFixed(4);
        fitnessCell.style.fontWeight = index === 0 ? 'bold' : 'normal';
        fitnessCell.style.color = individual.fitness > 0 ? '#26a69a' : '#787b86';

        // Actions
        const actionsCell = row.insertCell();
        actionsCell.innerHTML = `
            <div class="action-buttons">
                <button class="btn-small btn-view" onclick="viewSolution(${index})" title="View Details">View</button>
                <button class="btn-small btn-apply" onclick="applySolution(${index})" title="Apply to Strategy">Apply</button>
                <button class="btn-small btn-save" onclick="saveSolution(${index})" title="Save as New">Save As</button>
            </div>
        `;
    });

    // Store results globally for action buttons
    window.optimizationResults = population;
}

// Display fitness evolution using Chart.js
// displayFitnessChart removed - fitness evolution chart no longer displayed in UI

// ==================== ACTION BUTTON HANDLERS ====================

function viewSolution(index) {
    if (!window.optimizationResults || !window.optimizationResults[index]) {
        showNotification('⚠️ Solution not found', 'warning');
        return;
    }

    const solution = window.optimizationResults[index];

    // Build modal content
    let html = `
        <div style="background: #1e222d; border-radius: 8px; padding: 20px; max-width: 600px; color: #d1d4dc;">
            <h3 style="margin: 0 0 15px 0; color: #2962ff;">Solution #${index + 1} Details</h3>

            <div style="margin-bottom: 15px;">
                <h4 style="margin: 0 0 10px 0; font-size: 14px; color: #787b86;">Fitness Score</h4>
                <div style="font-size: 24px; font-weight: bold; color: #26a69a;">${solution.fitness.toFixed(4)}</div>
            </div>

            <div style="margin-bottom: 15px;">
                <h4 style="margin: 0 0 10px 0; font-size: 14px; color: #787b86;">Parameters (Original → Optimized)</h4>
                <table style="width: 100%; font-size: 12px; border-collapse: collapse; background: #252933; border-radius: 4px; overflow: hidden;">
                    <thead>
                        <tr style="background: #1e222d;">
                            <th style="padding: 8px; text-align: left; color: #787b86; font-size: 11px;">Parameter</th>
                            <th style="padding: 8px; text-align: right; color: #787b86; font-size: 11px;">Original</th>
                            <th style="padding: 8px; text-align: right; color: #787b86; font-size: 11px;">Optimized</th>
                            <th style="padding: 8px; text-align: right; color: #787b86; font-size: 11px;">Δ</th>
                        </tr>
                    </thead>
                    <tbody>
    `;

    for (const [param, optimizedValue] of Object.entries(solution.params || {})) {
        const paramConfig = selectedParameters.get(param);
        const originalValue = paramConfig ? paramConfig.originalValue : null;

        const shortParam = param.split('.').slice(-2).join('.');
        const displayOptimized = typeof optimizedValue === 'number' ? optimizedValue.toFixed(3) : optimizedValue;
        const displayOriginal = originalValue !== null && typeof originalValue === 'number' ? originalValue.toFixed(3) : (originalValue || '-');

        // Calculate change
        let changeHTML = '-';
        let changeColor = '#787b86';
        if (originalValue !== null && typeof originalValue === 'number' && typeof optimizedValue === 'number') {
            const diff = optimizedValue - originalValue;
            if (Math.abs(diff) > 0.001) {
                changeColor = diff > 0 ? '#26a69a' : '#ef5350';
                const sign = diff > 0 ? '+' : '';
                changeHTML = `${sign}${diff.toFixed(2)}`;
            } else {
                changeHTML = '0';
            }
        }

        html += `
            <tr style="border-top: 1px solid #2a2e39;">
                <td style="padding: 8px; color: #d1d4dc;">${shortParam}</td>
                <td style="padding: 8px; text-align: right; color: #787b86; font-family: monospace;">${displayOriginal}</td>
                <td style="padding: 8px; text-align: right; color: #2962ff; font-weight: bold; font-family: monospace;">${displayOptimized}</td>
                <td style="padding: 8px; text-align: right; color: ${changeColor}; font-family: monospace;">${changeHTML}</td>
            </tr>
        `;
    }

    html += `
                    </tbody>
                </table>
            </div>

            <div style="margin-bottom: 15px;">
                <h4 style="margin: 0 0 10px 0; font-size: 14px; color: #787b86;">Backtest Results</h4>
                <div style="background: #252933; padding: 12px; border-radius: 4px; font-size: 12px;">
    `;

    if (solution.backtest_results) {
        const br = solution.backtest_results;
        html += `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div>Win Rate: <strong>${(br.win_rate || 0).toFixed(1)}%</strong></div>
                <div>Total Trades: <strong>${br.total_trades || 0}</strong></div>
                <div>Profit: <strong style="color: ${(br.total_return || 0) >= 0 ? '#26a69a' : '#ef5350'}">${(br.total_return || 0).toFixed(2)} pts</strong></div>
                <div>Drawdown: <strong style="color: #ef5350">${(br.max_drawdown || 0).toFixed(1)}%</strong></div>
                <div>Profit Factor: <strong>${(br.profit_factor || 0).toFixed(2)}</strong></div>
                <div>Sharpe Ratio: <strong>${(br.sharpe_ratio || 0).toFixed(2)}</strong></div>
            </div>
        `;
    } else {
        html += '<div style="color: #787b86;">No backtest results available</div>';
    }

    html += `
                </div>
            </div>

            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button onclick="closeModal()" style="padding: 8px 16px; background: #2a2e39; border: 1px solid #3a3e49; border-radius: 4px; color: #d1d4dc; cursor: pointer;">
                    Close
                </button>
                <button onclick="closeModal(); applySolution(${index})" style="padding: 8px 16px; background: #26a69a; border: none; border-radius: 4px; color: white; cursor: pointer; font-weight: bold;">
                    Apply This Solution
                </button>
            </div>
        </div>
    `;

    showModal(html);
}

function applySolution(index) {
    if (!window.optimizationResults || !window.optimizationResults[index]) {
        showNotification('⚠️ Solution not found', 'warning');
        return;
    }

    const solution = window.optimizationResults[index];
    applyBestParameters(solution.params);
}

function saveSolution(index) {
    if (!window.optimizationResults || !window.optimizationResults[index]) {
        showNotification('⚠️ Solution not found', 'warning');
        return;
    }

    const solution = window.optimizationResults[index];

    // Prompt for new strategy name
    const newName = prompt('Enter name for new strategy:', currentStrategyData.name + ` (Opt #${index + 1})`);
    if (!newName) return;

    saveParametersAsNewStrategy(solution.params, newName);
}

async function saveParametersAsNewStrategy(params, newName) {
    const strategyFile = document.getElementById('strategySelect').value;

    if (!strategyFile || !params) {
        showNotification('⚠️ No strategy or parameters to save', 'warning');
        return;
    }

    try {
        addTerminalLine(`💾 Saving as new strategy: ${newName}`, 'info');

        // Load current strategy
        const response = await fetch(`/strategies/${strategyFile}`);
        const strategy = await response.json();

        // Apply parameters
        for (const [path, value] of Object.entries(params)) {
            const keys = path.split('.');
            let obj = strategy;

            for (let i = 0; i < keys.length - 1; i++) {
                obj = obj[keys[i]];
            }

            obj[keys[keys.length - 1]] = value;
        }

        // Set new name
        strategy.name = newName;

        const saveResponse = await fetch('/save_strategy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(strategy)
        });

        const saveResult = await saveResponse.json();

        if (saveResult.success) {
            addTerminalLine(`✅ Strategy saved successfully: ${newName}`, 'success');
            showNotification('✅ Strategy saved as: ' + newName, 'success');
            loadStrategies(); // Reload strategy list
        } else {
            addTerminalLine(`❌ Failed to save: ${saveResult.error}`, 'error');
            showNotification('❌ Failed to save: ' + saveResult.error, 'error');
        }
    } catch (error) {
        addTerminalLine(`❌ Error saving strategy: ${error.message}`, 'error');
        showNotification('❌ Error: ' + error.message, 'error');
    }
}

function exportResultsCSV() {
    if (!window.optimizationResults || window.optimizationResults.length === 0) {
        showNotification('⚠️ No results to export', 'warning');
        return;
    }

    addTerminalLine('📥 Exporting results to CSV...', 'info');

    // Build CSV content
    let csv = 'Rank,Fitness,Win Rate (%),Profit (pts),Drawdown (%),Profit Factor,Trades,';

    // Add parameter columns
    const firstResult = window.optimizationResults[0];
    const paramKeys = Object.keys(firstResult.params || {});
    csv += paramKeys.join(',') + '\n';

    // Add data rows
    window.optimizationResults.forEach((result, index) => {
        const br = result.backtest_results || {};

        csv += `${index + 1},`;
        csv += `${result.fitness.toFixed(4)},`;
        csv += `${(br.win_rate || 0).toFixed(1)},`;
        csv += `${(br.total_return || 0).toFixed(2)},`;
        csv += `${(br.max_drawdown || 0).toFixed(1)},`;
        csv += `${(br.profit_factor || 0).toFixed(2)},`;
        csv += `${br.total_trades || 0},`;

        // Add parameter values
        paramKeys.forEach(key => {
            const value = result.params[key];
            csv += typeof value === 'number' ? value.toFixed(3) : value;
            csv += ',';
        });

        csv += '\n';
    });

    // Download CSV
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `optimization_results_${Date.now()}.csv`;
    link.click();
    URL.revokeObjectURL(url);

    addTerminalLine(`✅ Exported ${window.optimizationResults.length} results to CSV`, 'success');
    showNotification('✅ Results exported to CSV', 'success');
}

function showModal(html) {
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.id = 'modalOverlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;

    overlay.innerHTML = html;
    overlay.onclick = (e) => {
        if (e.target === overlay) closeModal();
    };

    document.body.appendChild(overlay);
}

function closeModal() {
    const overlay = document.getElementById('modalOverlay');
    if (overlay) overlay.remove();
}

async function applyBestParameters(params) {
    const strategyFile = document.getElementById('strategySelect').value;

    if (!strategyFile || !params) {
        showNotification('⚠️ No parameters to apply', 'warning');
        return;
    }

    try {
        addTerminalLine('🔧 Applying optimized parameters...', 'info');

        // Load current strategy
        const response = await fetch(`/strategies/${strategyFile}`);
        const strategy = await response.json();

        // Apply parameters
        for (const [path, value] of Object.entries(params)) {
            const keys = path.split('.');
            let obj = strategy;

            for (let i = 0; i < keys.length - 1; i++) {
                obj = obj[keys[i]];
            }

            obj[keys[keys.length - 1]] = value;
        }

        // Save updated strategy with new name
        const newName = strategy.name + ' (Optimized)';
        strategy.name = newName;

        const saveResponse = await fetch('/save_strategy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(strategy)
        });

        const saveResult = await saveResponse.json();

        if (saveResult.success) {
            addTerminalLine(`✅ Optimized strategy saved: ${newName}`, 'success');
            showNotification('✅ Optimized strategy saved as: ' + newName, 'success');
            loadStrategies(); // Reload strategy list
        } else {
            addTerminalLine(`❌ Failed to save: ${saveResult.error}`, 'error');
            showNotification('❌ Failed to save: ' + saveResult.error, 'error');
        }
    } catch (error) {
        addTerminalLine(`❌ Error applying parameters: ${error.message}`, 'error');
        showNotification('❌ Error applying parameters: ' + error.message, 'error');
    }
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#f59e0b'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ==================== EXIT RULES QUICK ADD ====================

const EXIT_RULE_PRESETS = {
    'long_sl': {
        label: 'Long Stop Loss',
        path: 'exit_rules.tp_sl_table.0.sl',
        min: 5,
        max: 50,
        step: 0.1,
        type: 'float',
        badge: 'exit',
        icon: '📉'
    },
    'long_tp': {
        label: 'Long Take Profit',
        path: 'exit_rules.tp_sl_table.0.tp',
        min: 10,
        max: 100,
        step: 1,
        type: 'float',
        badge: 'exit',
        icon: '📈'
    },
    'long_trail': {
        label: 'Long Trailing Stop',
        path: 'exit_rules.tp_sl_table.0.trailing',
        min: 5,
        max: 30,
        step: 0.1,
        type: 'float',
        badge: 'exit',
        icon: '🔄'
    },
    'short_sl': {
        label: 'Short Stop Loss',
        path: 'exit_rules.tp_sl_table.0.sl',
        min: 5,
        max: 50,
        step: 0.1,
        type: 'float',
        badge: 'exit',
        icon: '📈'
    },
    'short_tp': {
        label: 'Short Take Profit',
        path: 'exit_rules.tp_sl_table.0.tp',
        min: 10,
        max: 100,
        step: 1,
        type: 'float',
        badge: 'exit',
        icon: '📉'
    },
    'short_trail': {
        label: 'Short Trailing Stop',
        path: 'exit_rules.tp_sl_table.0.trailing',
        min: 5,
        max: 30,
        step: 0.1,
        type: 'float',
        badge: 'exit',
        icon: '🔄'
    }
};

function quickAddParam(presetKey) {
    const preset = EXIT_RULE_PRESETS[presetKey];
    if (!preset) return;
    
    // Check if already exists
    const existingParams = document.querySelectorAll('.param-item');
    for (const item of existingParams) {
        const pathInput = item.querySelector('.param-path');
        if (pathInput && pathInput.value === preset.path) {
            showNotification('⚠️ Parameter already added: ' + preset.label, 'warning');
            return;
        }
    }
    
    const paramId = Date.now();
    const paramDiv = document.createElement('div');
    paramDiv.className = 'param-item exit-rule';
    paramDiv.dataset.paramId = paramId;
    paramDiv.innerHTML = `
        <div class="param-header">
            <div class="param-label">
                <span>${preset.icon}</span>
                <span>${preset.label}</span>
                <span class="param-badge ${preset.badge}">${preset.badge.toUpperCase()}</span>
            </div>
            <button class="btn-remove" onclick="removeParameter(${paramId})" title="Remove">×</button>
        </div>
        <input type="hidden" class="param-path" value="${preset.path}" />
        <div class="param-row" style="display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 6px;">
            <div>
                <label style="font-size: 10px; color: #787b86;">Min</label>
                <input type="number" class="param-min form-control" value="${preset.min}" step="${preset.step}" style="padding: 6px;" />
            </div>
            <div>
                <label style="font-size: 10px; color: #787b86;">Max</label>
                <input type="number" class="param-max form-control" value="${preset.max}" step="${preset.step}" style="padding: 6px;" />
            </div>
            <div>
                <label style="font-size: 10px; color: #787b86;">Step</label>
                <input type="number" class="param-step form-control" value="${preset.step}" step="any" style="padding: 6px;" />
            </div>
            <div style="display: flex; align-items: flex-end;">
                <select class="param-type form-control" style="padding: 6px; width: 60px;">
                    <option value="int" ${preset.type === 'int' ? 'selected' : ''}>Int</option>
                    <option value="float" ${preset.type === 'float' ? 'selected' : ''}>Float</option>
                </select>
            </div>
        </div>
        <div style="margin-top: 8px; font-size: 11px; color: #787b86;">
            Path: <code style="background: #131722; padding: 2px 6px; border-radius: 3px; font-size: 10px;">${preset.path}</code>
        </div>
    `;
    
    document.getElementById('paramsList').appendChild(paramDiv);
    parameters.push(paramId);
    checkReadyToOptimize();
    
    showNotification('✅ Added: ' + preset.label, 'success');
}

// ==================== PARAMETER TEMPLATES ====================

const PARAMETER_TEMPLATES = {
    'all_exits': {
        name: 'All Exit Rules',
        params: ['long_sl', 'long_tp', 'long_trail', 'short_sl', 'short_tp', 'short_trail']
    },
    'long_exits': {
        name: 'Long Exits Only',
        params: ['long_sl', 'long_tp', 'long_trail']
    },
    'short_exits': {
        name: 'Short Exits Only',
        params: ['short_sl', 'short_tp', 'short_trail']
    },
    'indicators': {
        name: 'Common Indicators',
        params: [
            {
                label: 'EMA Fast Period',
                path: 'indicators.0.params.period',
                min: 3,
                max: 20,
                step: 1,
                type: 'int',
                badge: 'indicator',
                icon: '📊'
            },
            {
                label: 'EMA Slow Period',
                path: 'indicators.1.params.period',
                min: 10,
                max: 50,
                step: 5,
                type: 'int',
                badge: 'indicator',
                icon: '📊'
            }
        ]
    }
};

function loadTemplate() {
    const templateKey = document.getElementById('templateSelect').value;
    if (!templateKey) {
        showNotification('⚠️ Please select a template', 'warning');
        return;
    }
    
    const template = PARAMETER_TEMPLATES[templateKey];
    if (!template) return;
    
    // Clear existing parameters
    document.getElementById('paramsList').innerHTML = '';
    parameters = [];
    
    // Add template parameters
    let addedCount = 0;
    template.params.forEach(paramKey => {
        if (typeof paramKey === 'string') {
            // Preset key
            quickAddParam(paramKey);
            addedCount++;
        } else {
            // Custom parameter object
            addCustomParameter(paramKey);
            addedCount++;
        }
    });
    
    showNotification(`✅ Loaded template: ${template.name} (${addedCount} params)`, 'success');
}

function addCustomParameter(config) {
    const paramId = Date.now() + Math.random();
    const paramDiv = document.createElement('div');
    paramDiv.className = 'param-item indicator';
    paramDiv.dataset.paramId = paramId;
    paramDiv.innerHTML = `
        <div class="param-header">
            <div class="param-label">
                <span>${config.icon || '⚙️'}</span>
                <span>${config.label}</span>
                <span class="param-badge ${config.badge}">${config.badge.toUpperCase()}</span>
            </div>
            <button class="btn-remove" onclick="removeParameter(${paramId})" title="Remove">×</button>
        </div>
        <input type="hidden" class="param-path" value="${config.path}" />
        <div class="param-row" style="display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 6px;">
            <div>
                <label style="font-size: 10px; color: #787b86;">Min</label>
                <input type="number" class="param-min form-control" value="${config.min}" step="${config.step}" style="padding: 6px;" />
            </div>
            <div>
                <label style="font-size: 10px; color: #787b86;">Max</label>
                <input type="number" class="param-max form-control" value="${config.max}" step="${config.step}" style="padding: 6px;" />
            </div>
            <div>
                <label style="font-size: 10px; color: #787b86;">Step</label>
                <input type="number" class="param-step form-control" value="${config.step}" step="any" style="padding: 6px;" />
            </div>
            <div style="display: flex; align-items: flex-end;">
                <select class="param-type form-control" style="padding: 6px; width: 60px;">
                    <option value="int" ${config.type === 'int' ? 'selected' : ''}>Int</option>
                    <option value="float" ${config.type === 'float' ? 'selected' : ''}>Float</option>
                </select>
            </div>
        </div>
        <div style="margin-top: 8px; font-size: 11px; color: #787b86;">
            Path: <code style="background: #131722; padding: 2px 6px; border-radius: 3px; font-size: 10px;">${config.path}</code>
        </div>
    `;
    
    document.getElementById('paramsList').appendChild(paramDiv);
    parameters.push(paramId);
}

// ===== STATE PERSISTENCE =====

/**
 * Save optimize state to localStorage
 */
function saveOptimizeState() {
    try {
        const state = {
            csvFile: currentCSVFile,
            strategy: document.getElementById('strategySelect')?.value || null,
            selectedParameters: Array.from(selectedParameters.entries()),
            populationSize: parseInt(document.getElementById('populationSize')?.value || 50),
            numGenerations: parseInt(document.getElementById('numGenerations')?.value || 30),
            mutationRate: parseFloat(document.getElementById('mutationRate')?.value || 0.1),
            crossoverRate: parseFloat(document.getElementById('crossoverRate')?.value || 0.8),
            targetMetric: document.getElementById('targetMetric')?.value || 'profit_factor',
            resultsTableHTML: document.getElementById('resultsTable')?.innerHTML || '',
            currentStrategyData: currentStrategyData,
            bestParams: bestParams,
            timestamp: Date.now()
        };

        localStorage.setItem('optimizeState', JSON.stringify(state));
        console.log('✅ Optimize state saved');
    } catch (error) {
        console.error('Failed to save optimize state:', error);
    }
}

/**
 * Restore optimize state from localStorage
 */
function restoreOptimizeState() {
    try {
        const savedState = localStorage.getItem('optimizeState');
        if (!savedState) return;

        const state = JSON.parse(savedState);

        // Check if state is not too old (older than 7 days)
        const daysSinceLastSave = (Date.now() - (state.timestamp || 0)) / (1000 * 60 * 60 * 24);
        if (daysSinceLastSave > 7) {
            console.log('ℹ️ Optimize state is too old, skipping restore');
            return;
        }

        // Restore strategy selection
        if (state.strategy) {
            setTimeout(async () => {
                const strategySelect = document.getElementById('strategySelect');
                if (strategySelect && state.strategy) {
                    strategySelect.value = state.strategy;

                    // Restore strategy data
                    if (state.currentStrategyData) {
                        currentStrategyData = state.currentStrategyData;
                        buildParameterTree(currentStrategyData);
                    } else {
                        await loadStrategyParameters(state.strategy);
                    }

                    // Restore selected parameters
                    if (state.selectedParameters && state.selectedParameters.length > 0) {
                        selectedParameters = new Map(state.selectedParameters);

                        // Re-check checkboxes and populate inputs
                        setTimeout(() => {
                            state.selectedParameters.forEach(([path, config]) => {
                                const checkbox = document.querySelector(`input[data-param-path="${path}"]`);
                                if (checkbox) {
                                    checkbox.checked = true;

                                    // Show config controls
                                    const controls = checkbox.closest('.param-item').querySelector('.param-config');
                                    if (controls) {
                                        controls.style.display = 'grid';
                                        controls.querySelector('.param-min').value = config.min;
                                        controls.querySelector('.param-max').value = config.max;
                                        controls.querySelector('.param-step').value = config.step;
                                        controls.querySelector('.param-type').value = config.type;
                                    }
                                }
                            });

                            updateParameterCount();
                            checkReadyToOptimize();
                        }, 300);
                    }
                }
            }, 500);
        }

        // Restore optimization settings
        if (state.populationSize) {
            const elem = document.getElementById('populationSize');
            if (elem) elem.value = state.populationSize;
        }

        if (state.numGenerations) {
            const elem = document.getElementById('numGenerations');
            if (elem) elem.value = state.numGenerations;
        }

        if (state.mutationRate !== undefined) {
            const elem = document.getElementById('mutationRate');
            if (elem) elem.value = state.mutationRate;
        }

        if (state.crossoverRate !== undefined) {
            const elem = document.getElementById('crossoverRate');
            if (elem) elem.value = state.crossoverRate;
        }

        if (state.targetMetric) {
            const elem = document.getElementById('targetMetric');
            if (elem) elem.value = state.targetMetric;
        }

        // Restore results table
        if (state.resultsTableHTML && state.resultsTableHTML.trim() !== '') {
            setTimeout(() => {
                const resultsTable = document.getElementById('resultsTable');
                if (resultsTable) {
                    resultsTable.innerHTML = state.resultsTableHTML;
                }

                // Restore bestParams
                if (state.bestParams) {
                    bestParams = state.bestParams;
                }

                console.log('✅ Optimize state restored');
            }, 600);
        }

    } catch (error) {
        console.error('Failed to restore optimize state:', error);
    }
}

// Export functions for modal to call
window.closeTimeframeModal = closeTimeframeModalOptimize;
window.confirmTimeframeAndUpload = confirmTimeframeAndUploadOptimize;
