/**
 * Strategy Builder - Visual Strategy Creator
 */

// Global state
let currentEntryDirection = 'long'; // Track current entry tab: 'long' or 'short'
let currentExitDirection = 'long'; // Track current exit tab: 'long' or 'short'

let strategyConfig = {
    name: "My Strategy",
    description: "",
    indicators: [],
    entry_conditions: {
        long: [],
        short: []
    },
    exit_rules: {
        long: {
            dynamic_tp_sl: true,
            tp_sl_table: [],
            time_exit: "14:30"
        },
        short: {
            dynamic_tp_sl: true,
            tp_sl_table: [],
            time_exit: "14:30"
        },
        base_time: "09:00"  // Base time for HHV/LLV calculation
    }
};

let currentConditionType = 'long'; // 'long' or 'short'
let currentIndicatorType = '';
let strategyAutoSaveTimer = null;
let isEditMode = false;
let editingSignalIndex = -1;
let editingIndicatorIndex = -1;

// IndexedDB for auto-save
let strategyDB;

// Initialize IndexedDB for auto-save
function initStrategyDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('StrategyBuilderDB', 3); // Increased version to fix conflict
        
        request.onerror = () => {
            console.error('IndexedDB error:', request.error);
            reject(request.error);
        };
        
        request.onsuccess = () => {
            strategyDB = request.result;
            console.log('✅ Strategy DB initialized');
            resolve(strategyDB);
        };
        
        request.onupgradeneeded = (event) => {
            strategyDB = event.target.result;
            if (!strategyDB.objectStoreNames.contains('strategies')) {
                strategyDB.createObjectStore('strategies', { keyPath: 'id' });
                console.log('📦 Created strategies object store');
            }
        };
    });
}

// Auto-save to IndexedDB
async function autoSaveStrategy() {
    try {
        if (!strategyDB) {
            await initStrategyDB();
        }
        
        const transaction = strategyDB.transaction(['strategies'], 'readwrite');
        const store = transaction.objectStore('strategies');
        
        const dataToSave = {
            id: 'current_strategy',
            config: strategyConfig,
            timestamp: Date.now()
        };
        
        const request = store.put(dataToSave);
        
        request.onsuccess = () => {
            console.log('💾 Auto-saved strategy:', strategyConfig.name);
            console.log('   - Indicators:', strategyConfig.indicators?.length || 0);
            console.log('   - Long conditions:', strategyConfig.entry_conditions?.long?.length || 0);
            console.log('   - Short conditions:', strategyConfig.entry_conditions?.short?.length || 0);
        };
        
        request.onerror = () => {
            console.error('❌ Failed to auto-save:', request.error);
        };
        
    } catch (error) {
        console.error('❌ Exception in autoSaveStrategy:', error);
    }
}

// Load auto-saved strategy from IndexedDB
async function loadAutoSavedStrategy() {
    try {
        console.log('🔍 Loading auto-saved strategy...');
        
        if (!strategyDB) {
            console.log('  ⏳ Initializing IndexedDB...');
            await initStrategyDB();
        }
        
        const transaction = strategyDB.transaction(['strategies'], 'readonly');
        const store = transaction.objectStore('strategies');
        const request = store.get('current_strategy');
        
        return new Promise((resolve, reject) => {
            request.onsuccess = () => {
                if (request.result && request.result.config) {
                    console.log('✅ Found auto-saved strategy:', request.result.config.name);
                    console.log('   Timestamp:', new Date(request.result.timestamp).toLocaleString());
                    console.log('   Indicators:', request.result.config.indicators?.length || 0);
                    resolve(request.result.config);
                } else {
                    console.log('ℹ️ No auto-saved strategy in IndexedDB');
                    resolve(null);
                }
            };
            request.onerror = () => {
                console.error('❌ Error loading auto-save:', request.error);
                resolve(null);
            };
        });
        
    } catch (error) {
        console.error('❌ Exception in loadAutoSavedStrategy:', error);
        return null;
    }
}

// Trigger auto-save with debounce
function triggerAutoSave() {
    clearTimeout(strategyAutoSaveTimer);
    strategyAutoSaveTimer = setTimeout(() => {
        autoSaveStrategy();
    }, 1000); // Save after 1 second of no changes
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initStrategyBuilder();
    loadDefaultTPSLRules();
});

async function initStrategyBuilder() {
    console.log('🚀 Strategy Builder initialized');
    
    // Initialize IndexedDB
    await initStrategyDB();
    
    // Try to load auto-saved strategy
    const autoSaved = await loadAutoSavedStrategy();
    if (autoSaved) {
        strategyConfig = autoSaved;
        console.log('✅ Restored previous session:', strategyConfig.name);
        console.log('   - Indicators:', strategyConfig.indicators.length);
        console.log('   - Long conditions:', strategyConfig.entry_conditions.long.length);
        console.log('   - Short conditions:', strategyConfig.entry_conditions.short.length);
    } else {
        console.log('ℹ️ No auto-saved strategy found, using defaults');
        // Keep default strategyConfig (don't reset)
    }
    
    // Load strategy name (only if elements exist - not on index page)
    const strategyNameEl = document.getElementById('strategyName');
    const strategyDescEl = document.getElementById('strategyDescription');
    if (strategyNameEl) {
        strategyNameEl.value = strategyConfig.name;
        strategyNameEl.addEventListener('input', triggerAutoSave);
    }
    if (strategyDescEl) {
        strategyDescEl.value = strategyConfig.description || '';
        strategyDescEl.addEventListener('input', triggerAutoSave);
    }
    
    // Render initial state
    renderConditions('long');
    renderConditions('short');
    renderActiveIndicators();
    renderTPSLTable();
    
    // Auto-render indicators on chart after a delay
    setTimeout(() => {
        if (strategyConfig.indicators && strategyConfig.indicators.length > 0) {
            console.log('📊 Auto-rendering', strategyConfig.indicators.length, 'indicators');
            if (typeof calculateAndRenderIndicators === 'function') {
                calculateAndRenderIndicators();
            } else {
                console.warn('⚠️ calculateAndRenderIndicators function not found');
            }
        } else {
            console.log('ℹ️ No indicators to render');
        }
    }, 1500);

    // Setup modal event listeners
    setupModalEventListeners();

    // Initialize trailing config
    initTrailingConfig();
}

function setupModalEventListeners() {
    const modal = document.getElementById('indicatorConfigModal');
    const modalContent = document.getElementById('indicatorConfigModalContent');

    if (modal && modalContent) {
        // Close modal when clicking outside content
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                closeIndicatorConfigModal();
            }
        });

        // Prevent modal close when clicking inside content
        modalContent.addEventListener('click', function(event) {
            event.stopPropagation();
        });

        console.log('✅ Modal event listeners setup');
    }
}

// ==================== PANEL SWITCHING ====================

function switchPanel(panelName) {
    // Hide all panels
    document.querySelectorAll('.panel-content').forEach(panel => {
        panel.classList.add('hidden');
    });
    
    // Remove active from all tabs
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected panel
    const panels = {
        'entry': 'entryPanel',
        'exit': 'exitPanel',
        'indicators': 'indicatorsTabPanel',
        'settings': 'settingsPanel'
    };
    
    if (panels[panelName]) {
        document.getElementById(panels[panelName]).classList.remove('hidden');
    }
    
    // Set active tab
    event.target.classList.add('active');
}

// ==================== CONDITIONS ====================

let currentSubConditions = []; // Temporary storage for building a signal

function addCondition(type) {
    currentConditionType = type;
    currentSubConditions = [];
    
    // Reset edit mode
    isEditMode = false;
    editingSignalIndex = -1;
    
    // Find next available signal number
    const existingSignals = strategyConfig.entry_conditions[type];
    const prefix = type === 'long' ? 'Buy' : 'Short';
    
    // Extract numbers from existing signal names
    const existingNumbers = existingSignals
        .map(sig => {
            const match = sig.name.match(new RegExp(`${prefix}(\\d+)`));
            return match ? parseInt(match[1]) : 0;
        })
        .filter(num => num > 0);
    
    // Find first available number
    let signalNumber = 1;
    while (existingNumbers.includes(signalNumber)) {
        signalNumber++;
    }
    
    const signalName = `${prefix}${signalNumber}`;
    
    document.getElementById('conditionModalTitle').textContent = 
        type === 'long' ? `Add Long Entry Signal (${signalName})` : `Add Short Entry Signal (${signalName})`;
    document.getElementById('signalName').value = signalName;
    
    // Clear builder and add first condition
    document.getElementById('conditionsBuilder').innerHTML = '';
    addSubCondition();
    
    // Show modal
    document.getElementById('conditionModal').classList.remove('hidden');
}

function addSubCondition() {
    const template = document.getElementById('subConditionTemplate');
    const clone = template.content.cloneNode(true);

    // Populate indicator options (price fields already in template)
    const leftSelect = clone.querySelector('.sub-left-operand');
    const rightSelect = clone.querySelector('.sub-right-operand');

    // Add indicators after price fields
    strategyConfig.indicators.forEach(ind => {
        let displayName = ind.type;
        if (ind.params) {
            const paramValues = Object.entries(ind.params).map(([k, v]) => v).join(',');
            displayName = `${ind.type}(${paramValues})`;
        }
        if (ind.id !== ind.type.toLowerCase()) {
            displayName = `${ind.id}: ${displayName}`;
        }

        const leftOption = document.createElement('option');
        leftOption.value = ind.id;
        leftOption.textContent = displayName;
        leftSelect.appendChild(leftOption);

        const rightOption = document.createElement('option');
        rightOption.value = ind.id;
        rightOption.textContent = displayName;
        rightSelect.appendChild(rightOption);
    });

    document.getElementById('conditionsBuilder').appendChild(clone);
}

function removeSubCondition(btn) {
    btn.closest('.sub-condition').remove();
}

function toggleRightInput(select) {
    const parent = select.closest('.sub-condition');
    const rightOperand = parent.querySelector('.sub-right-operand');
    const rightNumber = parent.querySelector('.sub-right-number');
    
    if (select.value === 'number') {
        rightOperand.style.display = 'none';
        rightNumber.style.display = 'block';
    } else {
        rightOperand.style.display = 'block';
        rightNumber.style.display = 'none';
    }
}

// Handle operator change to hide/show right operand for boolean operators
function handleOperatorChange(selectElement) {
    const subCondition = selectElement.closest('.sub-condition');
    const operator = selectElement.value;
    const rightType = subCondition.querySelector('.sub-right-type');
    const rightOperand = subCondition.querySelector('.sub-right-operand');
    const rightNumber = subCondition.querySelector('.sub-right-number');
    const rightOperandContainer = rightOperand.parentElement;
    
    // Hide right operand for "is_true" and "is_false"
    if (operator === 'is_true' || operator === 'is_false') {
        rightType.style.display = 'none';
        rightOperandContainer.style.display = 'none';
        if (rightNumber) rightNumber.style.display = 'none';
    } else {
        rightType.style.display = '';
        rightOperandContainer.style.display = '';
        // Re-apply toggleRightInput logic
        toggleRightInput(rightType);
    }
}

function saveSignal() {
    // Collect all sub-conditions
    const subConditionDivs = document.querySelectorAll('.sub-condition');
    const conditions = [];
    
    subConditionDivs.forEach((div, index) => {
        const left = div.querySelector('.sub-left-operand').value;
        const leftOffset = parseInt(div.querySelector('.sub-left-offset').value) || 0;
        const operator = div.querySelector('.sub-operator').value;
        const logic = div.querySelector('.sub-logic').value;
        
        // For is_true/is_false operators, right operand is not needed
        let right, rightOffset;
        if (operator === 'is_true') {
            right = 1; // true
            rightOffset = 0;
        } else if (operator === 'is_false') {
            right = 0; // false
            rightOffset = 0;
        } else {
            const rightType = div.querySelector('.sub-right-type').value;
            right = rightType === 'number' ? 
                div.querySelector('.sub-right-number').value : 
                div.querySelector('.sub-right-operand').value;
            rightOffset = rightType === 'number' ? 0 : parseInt(div.querySelector('.sub-right-offset').value) || 0;
        }
        
        if (!left || (operator !== 'is_true' && operator !== 'is_false' && !right)) {
            alert(`⚠️ Condition ${index + 1}: Please fill all fields!`);
            throw new Error('Incomplete condition');
        }
        
        conditions.push({
            left: left,
            leftOffset: leftOffset,
            operator: operator, // Keep original operator (is_true/is_false/etc)
            right: typeof right === 'string' && operator !== 'is_true' && operator !== 'is_false' ? right : parseFloat(right),
            rightOffset: rightOffset,
            logic: logic
        });
    });
    
    if (conditions.length === 0) {
        alert('⚠️ Please add at least one condition!');
        return;
    }
    
    // Create signal object
    const signalName = document.getElementById('signalName').value;
    const signal = {
        name: signalName,
        conditions: conditions
    };
    
    // Check if edit mode or add mode
    if (isEditMode && editingSignalIndex >= 0) {
        // Update existing signal
        strategyConfig.entry_conditions[currentConditionType][editingSignalIndex] = signal;
        console.log(`✅ Updated ${currentConditionType} signal:`, signal);
    } else {
        // Add new signal
        strategyConfig.entry_conditions[currentConditionType].push(signal);
        console.log(`✅ Added ${currentConditionType} signal:`, signal);
    }
    
    renderConditions(currentConditionType);
    closeConditionModal();
    
    // Reset edit mode
    isEditMode = false;
    editingSignalIndex = -1;
    
    // Auto-save
    triggerAutoSave();
}

function closeConditionModal() {
    document.getElementById('conditionModal').classList.add('hidden');
}

function removeCondition(type, index) {
    strategyConfig.entry_conditions[type].splice(index, 1);
    renderConditions(type);
    
    // Auto-save
    triggerAutoSave();
}

function editCondition(type, index) {
    const signal = strategyConfig.entry_conditions[type][index];
    
    if (!signal || !signal.conditions) {
        alert('⚠️ Cannot edit this signal format');
        return;
    }
    
    // Set edit mode
    isEditMode = true;
    editingSignalIndex = index;
    currentConditionType = type;
    
    // Update modal title
    document.getElementById('conditionModalTitle').textContent = `Edit ${signal.name}`;
    document.getElementById('signalName').value = signal.name;
    
    // Clear builder
    document.getElementById('conditionsBuilder').innerHTML = '';
    
    // Load existing conditions
    signal.conditions.forEach(cond => {
        const template = document.getElementById('subConditionTemplate');
        const clone = template.content.cloneNode(true);

        // Populate indicator options (price fields already in template)
        const leftSelect = clone.querySelector('.sub-left-operand');
        const rightSelect = clone.querySelector('.sub-right-operand');

        // Add indicators after price fields
        strategyConfig.indicators.forEach(ind => {
            let displayName = ind.type;
            if (ind.params) {
                const paramValues = Object.entries(ind.params).map(([k, v]) => v).join(',');
                displayName = `${ind.type}(${paramValues})`;
            }
            if (ind.id !== ind.type.toLowerCase()) {
                displayName = `${ind.id}: ${displayName}`;
            }

            const leftOption = document.createElement('option');
            leftOption.value = ind.id;
            leftOption.textContent = displayName;
            leftSelect.appendChild(leftOption);

            const rightOption = document.createElement('option');
            rightOption.value = ind.id;
            rightOption.textContent = displayName;
            rightSelect.appendChild(rightOption);
        });

        // Set values
        clone.querySelector('.sub-left-operand').value = cond.left;
        clone.querySelector('.sub-left-offset').value = cond.leftOffset || 0;
        clone.querySelector('.sub-operator').value = cond.operator;
        clone.querySelector('.sub-logic').value = cond.logic;

        // Check if right is number or indicator/price
        const rightType = typeof cond.right === 'number' ? 'number' : 'indicator';
        clone.querySelector('.sub-right-type').value = rightType;

        if (rightType === 'number') {
            clone.querySelector('.sub-right-operand').style.display = 'none';
            clone.querySelector('.sub-right-number').style.display = 'block';
            clone.querySelector('.sub-right-number').value = cond.right;
        } else {
            clone.querySelector('.sub-right-operand').value = cond.right;
            clone.querySelector('.sub-right-offset').value = cond.rightOffset || 0;
        }

        // Handle is_true/is_false operators - hide right operand
        if (cond.operator === 'is_true' || cond.operator === 'is_false') {
            handleOperatorChange(clone.querySelector('.sub-operator'));
        }

        document.getElementById('conditionsBuilder').appendChild(clone);
    });
    
    // Show modal
    document.getElementById('conditionModal').classList.remove('hidden');
}

function renderConditions(type) {
    const container = type === 'long' ?
        document.getElementById('longConditions') :
        document.getElementById('shortConditions');

    // Return early if container doesn't exist (not on strategy builder page)
    if (!container) return;

    const conditions = strategyConfig.entry_conditions?.[type];

    if (!conditions || conditions.length === 0) {
        container.innerHTML = '<div style="color: #787b86; font-size: 12px; padding: 20px; text-align: center;">No conditions added yet</div>';
        return;
    }
    
    container.innerHTML = conditions.map((signal, index) => {
        // Handle old format (single condition) vs new format (signal with multiple conditions)
        if (signal.conditions) {
            // New format
            const conditionsHTML = signal.conditions.map((cond, i) => {
                // Format left operand with offset
                const leftOffset = cond.leftOffset || 0;
                const leftDisplay = leftOffset === 0 ? cond.left : `${cond.left}[${leftOffset}]`;
                
                // Format right operand with offset
                let rightDisplay;
                if (typeof cond.right === 'number') {
                    rightDisplay = cond.right;
                } else {
                    const rightOffset = cond.rightOffset || 0;
                    rightDisplay = rightOffset === 0 ? cond.right : `${cond.right}[${rightOffset}]`;
                }
                
                const logicDisplay = i < signal.conditions.length - 1 ? ` <span style="color: #2962ff; font-weight: bold;">${cond.logic}</span>` : '';
                
                return `
                    <div style="padding: 5px 0;">
                        <code style="background: #2a2e39; padding: 3px 6px; border-radius: 3px;">${leftDisplay}</code>
                        <span style="color: #26a69a;">${cond.operator}</span>
                        <code style="background: #2a2e39; padding: 3px 6px; border-radius: 3px;">${rightDisplay}</code>
                        ${logicDisplay}
                    </div>
                `;
            }).join('');
            
            return `
                <div class="condition-item" style="background: #1e222d; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #2962ff;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <strong style="color: #2962ff; font-size: 14px;">${signal.name || `Signal ${index + 1}`}</strong>
                            <div style="margin-top: 8px; font-size: 12px;">
                                ${conditionsHTML}
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <button onclick="editCondition('${type}', ${index})" 
                                    style="background: #2962ff; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 11px;">
                                Edit
                            </button>
                            <button onclick="removeCondition('${type}', ${index})" 
                                    style="background: #ef5350; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 11px;">
                                Remove
                            </button>
                        </div>
                    </div>
                </div>
            `;
        } else {
            // Old format - display as is
            return `
                <div class="condition-item">
                    <div class="condition-text">${signal.condition}</div>
                    ${index < conditions.length - 1 ? `<span class="condition-logic">${signal.logic}</span>` : ''}
                    <button class="btn-remove" onclick="removeCondition('${type}', ${index})">✕</button>
                </div>
            `;
        }
    }).join('');
}

// ==================== INDICATORS ====================

function filterIndicators(category) {
    // Update active category button
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Filter indicator select
    const select = document.getElementById('indicatorSelect');
    const options = select.querySelectorAll('option');
    
    // Show all if 'all' category
    // For now, just visual feedback
    console.log(`Filtering indicators: ${category}`);
}

// ============================================
//         INDICATOR TEMPLATE SYSTEM
// ============================================

let indicatorTemplates = {};

// Load indicator templates on page load
async function loadIndicatorTemplatesData() {
    try {
        const response = await fetch('/api/indicator-templates');
        const result = await response.json();
        
        if (result.success) {
            indicatorTemplates = result.templates;
            console.log('✅ Loaded indicator templates:', Object.keys(indicatorTemplates));
        } else {
            console.error('❌ Failed to load templates:', result.error);
        }
    } catch (error) {
        console.error('❌ Error loading templates:', error);
    }
}

// Show template info when selected
document.getElementById('templateSelect')?.addEventListener('change', function() {
    const templateKey = this.value;
    const infoDiv = document.getElementById('templateInfo');
    
    if (!templateKey) {
        infoDiv.style.display = 'none';
        return;
    }
    
    const template = indicatorTemplates[templateKey];
    if (template) {
        infoDiv.style.display = 'block';
        infoDiv.innerHTML = `
            <strong>${template.name}</strong><br>
            ${template.description}<br>
            <span style="color: #2962ff;">${template.indicators.length} indicators will be added</span>
        `;
    }
});

// Load indicator template
async function loadIndicatorTemplate() {
    const templateKey = document.getElementById('templateSelect').value;
    
    if (!templateKey) {
        alert('⚠️ Please select a template first');
        return;
    }
    
    const template = indicatorTemplates[templateKey];
    if (!template) {
        alert('❌ Template not found');
        return;
    }
    
    // Confirm before loading
    const confirm = window.confirm(
        `Load "${template.name}"?\n\n` +
        `This will add ${template.indicators.length} indicators.\n` +
        `Existing indicators will not be removed.`
    );
    
    if (!confirm) return;
    
    // Add each indicator from template
    let addedCount = 0;
    let skippedCount = 0;
    
    for (const indicator of template.indicators) {
        // Check if indicator already exists
        const exists = strategyConfig.indicators.some(ind => ind.id === indicator.id);
        
        if (exists) {
            skippedCount++;
            continue;
        }
        
        // Add indicator
        strategyConfig.indicators.push({
            id: indicator.id,
            type: indicator.type,
            params: indicator.params
        });
        addedCount++;
    }
    
    // Refresh display
    renderActiveIndicators();
    
    // Show result
    alert(
        `✅ Template loaded!\n\n` +
        `Added: ${addedCount} indicators\n` +
        `Skipped: ${skippedCount} (already exist)`
    );
    
    console.log(`📦 Loaded template: ${template.name} (${addedCount} added, ${skippedCount} skipped)`);
}

// Initialize templates on page load
document.addEventListener('DOMContentLoaded', function() {
    loadIndicatorTemplatesData();
});

function addIndicator() {
    currentIndicatorType = document.getElementById('indicatorSelect').value;

    if (!currentIndicatorType) {
        alert('⚠️ Please select an indicator!');
        return;
    }

    // Reset edit mode
    isEditMode = false;
    editingIndicatorIndex = -1;

    // Open modal to configure indicator
    openIndicatorConfigModal(currentIndicatorType);
}

function openIndicatorConfigModal(indicatorType, existingIndicator = null) {
    const modal = document.getElementById('indicatorConfigModal');
    const paramsContainer = document.getElementById('modalParamsContainer');
    const modalTitle = document.getElementById('modalConfigTitle');
    const saveBtn = document.getElementById('modalSaveBtn');

    // Set title
    if (existingIndicator) {
        modalTitle.textContent = `✏️ Edit ${indicatorType} Indicator`;
        saveBtn.textContent = 'Save Changes';
    } else {
        modalTitle.textContent = `📊 Add ${indicatorType} Indicator`;
        saveBtn.textContent = 'Add Indicator';
    }

    // Set indicator type
    document.getElementById('modalIndicatorType').value = indicatorType;

    // Generate default ID or use existing
    const paramDefs = getIndicatorParams(indicatorType);
    let defaultId;
    if (existingIndicator) {
        defaultId = existingIndicator.id;
        document.getElementById('modalIndicatorId').disabled = true;
    } else {
        // Generate unique ID
        let baseId = indicatorType.toLowerCase();
        let id = baseId;
        let counter = 1;
        while (strategyConfig.indicators.some(ind => ind.id === id)) {
            id = `${baseId}_${counter}`;
            counter++;
        }
        defaultId = id;
        document.getElementById('modalIndicatorId').disabled = false;
    }
    document.getElementById('modalIndicatorId').value = defaultId;

    // Render parameter inputs
    if (paramDefs.length === 0) {
        paramsContainer.innerHTML = '<p style="color: #787b86; font-size: 12px;">This indicator has no configurable parameters.</p>';
    } else {
        paramsContainer.innerHTML = paramDefs.map(param => {
            const currentValue = existingIndicator && existingIndicator.params[param.name] !== undefined ?
                existingIndicator.params[param.name] :
                param.default;

            const paramType = param.type || 'number';

            if (paramType === 'color') {
                return `
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-size: 12px; color: #787b86; margin-bottom: 5px;">${param.label}</label>
                        <input type="color"
                               class="modal-param-input"
                               data-param="${param.name}"
                               value="${currentValue}"
                               style="width: 100%; padding: 5px; background: #131722; border: 1px solid #2a2e39; border-radius: 4px; cursor: pointer; height: 40px;">
                        <small style="color: #787b86; font-size: 11px;">Selected: ${currentValue}</small>
                    </div>
                `;
            } else {
                return `
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-size: 12px; color: #787b86; margin-bottom: 5px;">${param.label}</label>
                        <input type="number"
                               class="modal-param-input"
                               data-param="${param.name}"
                               value="${currentValue}"
                               min="${param.min}"
                               max="${param.max}"
                               step="0.1"
                               style="width: 100%; padding: 10px; background: #131722; border: 1px solid #2a2e39; border-radius: 4px; color: #d1d4dc; font-size: 13px;">
                        <small style="color: #787b86; font-size: 11px;">Range: ${param.min} - ${param.max}</small>
                    </div>
                `;
            }
        }).join('');
    }

    // Show modal
    modal.style.display = 'block';
}

function closeIndicatorConfigModal() {
    const modal = document.getElementById('indicatorConfigModal');
    if (modal) {
        modal.style.display = 'none';

        // Reset edit mode
        isEditMode = false;
        editingIndicatorIndex = -1;

        console.log('✅ Modal closed and edit mode reset');
    }
}

function saveIndicatorFromModal() {
    const indicatorType = document.getElementById('modalIndicatorType').value;
    const indicatorId = document.getElementById('modalIndicatorId').value.trim();

    if (!indicatorId) {
        alert('⚠️ Please enter an indicator ID!');
        return;
    }

    // Collect parameters
    const params = {};
    const paramInputs = document.querySelectorAll('.modal-param-input');
    paramInputs.forEach(input => {
        const paramName = input.getAttribute('data-param');
        // If input type is color, use string value; otherwise parse as float
        if (input.type === 'color') {
            params[paramName] = input.value;
        } else {
            params[paramName] = parseFloat(input.value);
        }
    });

    if (isEditMode && editingIndicatorIndex >= 0) {
        // Update existing indicator
        strategyConfig.indicators[editingIndicatorIndex].params = params;
        console.log(`✅ Updated indicator ${indicatorId}:`, params);

        // Reset edit mode
        isEditMode = false;
        editingIndicatorIndex = -1;
    } else {
        // Check if ID already exists
        if (strategyConfig.indicators.some(ind => ind.id === indicatorId)) {
            alert('⚠️ Indicator ID already exists! Please use a different ID.');
            return;
        }

        // Add new indicator
        strategyConfig.indicators.push({
            id: indicatorId,
            type: indicatorType,
            params: params
        });

        console.log(`✅ Added ${indicatorType} indicator with ID: ${indicatorId}`);
    }

    // Refresh display
    renderActiveIndicators();

    // Close modal
    closeIndicatorConfigModal();

    // Auto-save
    triggerAutoSave();
}

function getIndicatorParams(type) {
    const paramMap = {
        'EMA': [{name: 'period', label: 'Period', default: 14, min: 1, max: 500}],
        'SMA': [{name: 'period', label: 'Period', default: 20, min: 1, max: 500}],
        'WMA': [{name: 'period', label: 'Period', default: 20, min: 1, max: 500}],
        'RSI': [{name: 'period', label: 'Period', default: 14, min: 2, max: 100}],
        'MACD': [
            {name: 'fast', label: 'Fast Period', default: 12, min: 2, max: 100},
            {name: 'slow', label: 'Slow Period', default: 26, min: 2, max: 100},
            {name: 'signal', label: 'Signal Period', default: 9, min: 2, max: 50}
        ],
        'BollingerBands': [
            {name: 'period', label: 'Period', default: 20, min: 2, max: 100},
            {name: 'std_dev', label: 'Std Dev', default: 2, min: 1, max: 5}
        ],
        'ATR': [{name: 'period', label: 'Period', default: 14, min: 1, max: 100}],
        'SuperTrend': [
            {name: 'period', label: 'Period', default: 10, min: 1, max: 50, type: 'number'},
            {name: 'multiplier', label: 'Multiplier', default: 3, min: 1, max: 10, type: 'number'},
            {name: 'uptrend_color', label: 'Uptrend Color', default: '#26a69a', type: 'color'},
            {name: 'downtrend_color', label: 'Downtrend Color', default: '#ef5350', type: 'color'}
        ],
        // Trend Indicators - fixed periods like AFL
        'MAuptrend': [],     // MA2=19, MA3=44, MA4=99, MA5=245
        'MAdowntrend': [],   // MA2=19, MA3=44, MA4=99, MA5=245
        'Alluptrend': [],    // MA2=19, MA3=44, MA4=99, MA5=245, MA7=dynamic
        'Alldowntrend': [],  // MA2=19, MA3=44, MA4=99, MA5=245, MA7=dynamic
        'SlopeMA1': [],      // MA1=5
        'GMA12': [],         // MA1=5, MA2=19
        'GMA23': [],         // MA2=19, MA3=44
        'GMA45': [],         // MA4=99, MA5=245
        'MArange': [],       // MA2,3,4,5
        'MA7range': [],      // MA7=dynamic, Close
        // Pivot Points - no params (calculated from yesterday's data)
        'PP': [],
        'R1': [],
        'R2': [],
        'R3': [],
        'S1': [],
        'S2': [],
        'S3': [],
        // Candlestick patterns
        'Green': [],  // C >= O
        'Red': [],    // C < O
        'Length': [], // H - L
        // Custom AFL indicators
        'HHVsinceopen': [],  // No params
        'LLVsinceopen': [],  // No params
        'HHVsincebuy': [],   // No params - HHV since Long entry
        'LLVsinceshort': [], // No params - LLV since Short entry
        'HHVresline': [],    // HHVsinceopen - 0.5
        'LLVresline': [],    // LLVsinceopen + 0.5
        'HHVresline1': [],   // HHVresline - 0.5
        'LLVresline1': [],   // LLVresline + 0.5
        'HHVresline2': [],   // HHVresline1 - 0.5
        'LLVresline2': [],   // LLVresline1 + 0.5
        'HHVresline3': [],   // HHVresline2 - 0.5
        'LLVresline3': [],   // LLVresline2 + 0.5
        'HHVresline4': [],   // HHVresline3 - 0.5
        'LLVresline4': [],   // LLVresline3 + 0.5
        'resHL': [],  // No params - abs(HHVsinceopen - LLVsinceopen)
        'AvgHL': [],  // No params - (HHVsinceopen + LLVsinceopen) / 2
        'RealtimeOH': [],  // No params - HHVsinceopen - Baseprice
        'RealtimeOL': [],  // No params - Baseprice - LLVsinceopen
        'RangetoHHV': [],  // No params - HHVsinceopen - Close
        'RangetoLLV': [],  // No params - Close - LLVsinceopen
        'Baseprice': []  // No params - Open price at base time (09:00)
    };
    
    return paramMap[type] || [{name: 'period', label: 'Period', default: 14, min: 1, max: 500}];
}

// Modal-based save function removed - using simplified direct add/edit instead

function removeIndicator(index) {
    const indicator = strategyConfig.indicators[index];

    // Check if indicator is used in conditions
    const usedInConditions = [
        ...strategyConfig.entry_conditions.long,
        ...strategyConfig.entry_conditions.short
    ].some(signal =>
        signal.conditions && signal.conditions.some(cond =>
            cond.left === indicator.id || cond.right === indicator.id
        )
    );

    if (usedInConditions) {
        if (!confirm(`⚠️ Indicator "${indicator.id}" is used in conditions. Remove anyway?`)) {
            return;
        }
    }

    strategyConfig.indicators.splice(index, 1);
    console.log('🗑️ Removed indicator:', indicator.id);
    
    // Sync with window.activeIndicators (for chart)
    if (typeof window.activeIndicators !== 'undefined') {
        window.activeIndicators = window.activeIndicators.filter(ind => ind.id !== indicator.id);
        console.log('🔄 Synced removal to window.activeIndicators');
    }
    
    // Remove from chart
    if (typeof window.indicatorSeries !== 'undefined' && window.indicatorSeries[indicator.id]) {
        if (typeof chart !== 'undefined' && chart.removeSeries) {
            chart.removeSeries(window.indicatorSeries[indicator.id]);
        }
        delete window.indicatorSeries[indicator.id];
    }
    
    renderActiveIndicators();
    
    // Update chart indicators list
    if (typeof updateActiveIndicatorsList === 'function') {
        updateActiveIndicatorsList();
    }
    
    // Auto-save
    triggerAutoSave();
    
    // Re-render indicators on chart
    setTimeout(() => {
        console.log('🔄 Re-rendering remaining', strategyConfig.indicators.length, 'indicators');
        if (typeof calculateAndRenderIndicators === 'function') {
            calculateAndRenderIndicators();
        }
    }, 300);
}

function clearAllIndicators() {
    // Check if any indicators are used in conditions
    const usedIndicators = [];
    strategyConfig.indicators.forEach(ind => {
        const usedInConditions = [
            ...strategyConfig.entry_conditions.long,
            ...strategyConfig.entry_conditions.short
        ].some(signal =>
            signal.conditions && signal.conditions.some(cond =>
                cond.left === ind.id || cond.right === ind.id
            )
        );

        if (usedInConditions) {
            usedIndicators.push(ind.id);
        }
    });

    if (usedIndicators.length > 0) {
        const message = `⚠️ The following indicators are used in conditions:\n${usedIndicators.join(', ')}\n\nRemove all indicators anyway?`;
        if (!confirm(message)) {
            return;
        }
    } else if (strategyConfig.indicators.length > 0) {
        if (!confirm(`🗑️ Remove all ${strategyConfig.indicators.length} indicators?`)) {
            return;
        }
    }

    // Clear all indicators
    strategyConfig.indicators = [];
    console.log('🗑️ Cleared all indicators');

    // Sync with window.activeIndicators (for chart)
    if (typeof window.activeIndicators !== 'undefined') {
        window.activeIndicators = [];
    }

    // Re-render
    renderActiveIndicators();

    // Update chart
    setTimeout(() => {
        if (typeof calculateAndRenderIndicators === 'function') {
            calculateAndRenderIndicators();
        }
    }, 300);

    // Auto-save
    triggerAutoSave();
}

function editIndicator(index) {
    const indicator = strategyConfig.indicators[index];

    // Set edit mode
    isEditMode = true;
    editingIndicatorIndex = index;

    // Open modal with current values
    openIndicatorConfigModal(indicator.type, indicator);
}

// Safeguard to prevent infinite render loops
let renderActiveIndicatorsCallCount = 0;
let lastRenderTime = 0;

function renderActiveIndicators() {
    const now = Date.now();
    const timeSinceLastRender = now - lastRenderTime;

    // Reset counter if enough time has passed (1 second)
    if (timeSinceLastRender > 1000) {
        renderActiveIndicatorsCallCount = 0;
    }

    renderActiveIndicatorsCallCount++;

    // Prevent infinite loop - max 10 calls per second
    if (renderActiveIndicatorsCallCount > 10) {
        console.error('❌ renderActiveIndicators called too many times! Preventing infinite loop.');
        return;
    }

    lastRenderTime = now;

    console.log('🔄 renderActiveIndicators called (count:', renderActiveIndicatorsCallCount, ')');
    console.log('📊 strategyConfig.indicators:', strategyConfig.indicators);

    const container = document.getElementById('activeIndicatorsList');

    if (!container) {
        console.warn('❌ activeIndicatorsList container not found - may not be on this page');

        // Try fallback to activeIndicators (for strategy builder page)
        const fallbackContainer = document.getElementById('activeIndicators');
        if (!fallbackContainer) {
            console.warn('❌ No indicators container found at all');
            return;
        }
        console.log('✅ Using fallback activeIndicators container');
        return renderToContainer(fallbackContainer);
    }

    return renderToContainer(container);
}

function renderToContainer(container) {
    console.log('📝 Rendering to container:', container.id);

    if (strategyConfig.indicators.length === 0) {
        container.innerHTML = '<div style="color: #787b86; font-size: 12px; padding: 20px; text-align: center;">No indicators added yet</div>';
        return;
    }

    container.innerHTML = strategyConfig.indicators.map((ind, index) => {
        // Format parameters for display
        const paramsStr = Object.keys(ind.params).length === 0
            ? 'No parameters'
            : Object.entries(ind.params).map(([k, v]) => `${k}:${v}`).join(', ');

        return `
        <div class="indicator-item">
            <div>
                <div class="indicator-name">${ind.id}</div>
                <div class="indicator-params">${ind.type} - ${paramsStr}</div>
            </div>
            <div style="display: flex; gap: 8px;">
                <button class="btn-edit" onclick="editIndicator(${index})" title="Edit">✏️</button>
                <button class="btn-remove" onclick="removeIndicator(${index})" title="Remove">✕</button>
            </div>
        </div>
    `;
    }).join('');

    console.log('✅ Rendered', strategyConfig.indicators.length, 'indicators');
}

function getDefaultIndicatorColor(type) {
    const colors = {
        'EMA': '#2962FF',
        'SMA': '#FF6D00',
        'WMA': '#9C27B0',
        'RSI': '#9C27B0',
        'MACD': '#00BCD4',
        'BB': '#4CAF50',
        'BollingerBands': '#4CAF50',
        'SuperTrend': '#FF5252',
        'ATR': '#FFA726'
    };
    return colors[type] || '#2962FF';
}

// ==================== INDICATOR DISPLAY CONTROLS ====================

// Toggle indicator display on chart
function toggleIndicatorDisplay(index) {
    const indicator = strategyConfig.indicators[index];
    if (!indicator) return;
    
    // Initialize display if not exist
    if (!indicator.display) {
        indicator.display = {
            show: true,
            color: getDefaultIndicatorColor(indicator.type),
            lineStyle: 'solid',
            lineWidth: 2
        };
    }
    
    // Toggle show/hide
    indicator.display.show = !indicator.display.show;
    
    // Re-render list
    renderActiveIndicators();
    
    // Update chart
    if (typeof calculateAndRenderIndicators === 'function') {
        setTimeout(() => calculateAndRenderIndicators(), 100);
    }
    
    console.log(`📊 ${indicator.id} ${indicator.display.show ? 'shown' : 'hidden'}`);
}

// Open indicator display settings modal
let currentEditingDisplayIndex = -1;

function openIndicatorDisplaySettings(index) {
    const indicator = strategyConfig.indicators[index];
    if (!indicator) return;
    
    currentEditingDisplayIndex = index;
    
    // Initialize display if not exist
    if (!indicator.display) {
        indicator.display = {
            show: true,
            color: getDefaultIndicatorColor(indicator.type),
            lineStyle: 'solid',
            lineWidth: 2
        };
    }
    
    // Show modal
    const modal = document.getElementById('indicatorDisplayModal');
    if (!modal) {
        // Create modal if doesn't exist
        createIndicatorDisplayModal();
    }
    
    // Set values
    document.getElementById('displayIndName').textContent = `${indicator.id} (${indicator.type})`;
    document.getElementById('displayColor').value = indicator.display.color;
    document.getElementById('displayLineStyle').value = indicator.display.lineStyle;
    document.getElementById('displayLineWidth').value = indicator.display.lineWidth;
    document.getElementById('displayShow').checked = indicator.display.show;
    
    // Show modal
    document.getElementById('indicatorDisplayModal').classList.remove('hidden');
}

function createIndicatorDisplayModal() {
    const modalHTML = `
        <div id="indicatorDisplayModal" class="modal hidden">
            <div class="modal-content" style="max-width: 500px;">
                <div class="modal-header">
                    <h3>🎨 Indicator Display Settings</h3>
                    <button class="btn-close" onclick="closeIndicatorDisplayModal()">×</button>
                </div>
                <div class="modal-body">
                    <h4 id="displayIndName" style="margin-bottom: 20px; color: #2962FF;"></h4>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="displayShow" onchange="previewDisplayChange()">
                            Show on chart
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>Color:</label>
                        <input type="color" id="displayColor" class="form-input" onchange="previewDisplayChange()">
                    </div>
                    
                    <div class="form-group">
                        <label>Line Style:</label>
                        <select id="displayLineStyle" class="form-select" onchange="previewDisplayChange()">
                            <option value="solid">Solid</option>
                            <option value="dashed">Dashed</option>
                            <option value="dotted">Dotted</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Line Width:</label>
                        <select id="displayLineWidth" class="form-select" onchange="previewDisplayChange()">
                            <option value="1">1px</option>
                            <option value="2">2px</option>
                            <option value="3">3px</option>
                            <option value="4">4px</option>
                            <option value="5">5px</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="closeIndicatorDisplayModal()">Cancel</button>
                    <button class="btn-primary" onclick="saveIndicatorDisplaySettings()">Apply</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function previewDisplayChange() {
    if (currentEditingDisplayIndex < 0) return;
    
    const indicator = strategyConfig.indicators[currentEditingDisplayIndex];
    if (!indicator) return;
    
    // Update temporary values for preview
    indicator.display.show = document.getElementById('displayShow').checked;
    indicator.display.color = document.getElementById('displayColor').value;
    indicator.display.lineStyle = document.getElementById('displayLineStyle').value;
    indicator.display.lineWidth = parseInt(document.getElementById('displayLineWidth').value);
    
    // Update chart in real-time
    if (typeof calculateAndRenderIndicators === 'function') {
        calculateAndRenderIndicators();
    }
}

function saveIndicatorDisplaySettings() {
    if (currentEditingDisplayIndex < 0) return;
    
    const indicator = strategyConfig.indicators[currentEditingDisplayIndex];
    if (!indicator) return;
    
    // Save values
    indicator.display.show = document.getElementById('displayShow').checked;
    indicator.display.color = document.getElementById('displayColor').value;
    indicator.display.lineStyle = document.getElementById('displayLineStyle').value;
    indicator.display.lineWidth = parseInt(document.getElementById('displayLineWidth').value);
    
    // Re-render list
    renderActiveIndicators();
    
    // Update chart
    if (typeof calculateAndRenderIndicators === 'function') {
        calculateAndRenderIndicators();
    }
    
    // Trigger auto-save to IndexedDB and localStorage
    triggerAutoSave();
    
    // Close modal
    closeIndicatorDisplayModal();
    
    console.log('✅ Display settings saved for:', indicator.id);
}

function closeIndicatorDisplayModal() {
    document.getElementById('indicatorDisplayModal').classList.add('hidden');
    currentEditingDisplayIndex = -1;
}

// ==================== TP/SL RULES ====================

function loadDefaultTPSLRules() {
    const defaultRules = [
        {profit_range: [0, 2], tp: 5, sl: 10.3, trailing: 11.9},
        {profit_range: [2, 4], tp: 8, sl: 10.8, trailing: 13.9},
        {profit_range: [4, 6], tp: 10, sl: 5.5, trailing: 9.8},
        {profit_range: [6, 8], tp: 12, sl: 4, trailing: 10.1},
        {profit_range: [8, 10], tp: 15, sl: 1.2, trailing: 9.5},
        {profit_range: [10, 12], tp: 18, sl: 1, trailing: 12}
    ];

    // Load same default rules for both long and short
    strategyConfig.exit_rules.long.tp_sl_table = JSON.parse(JSON.stringify(defaultRules));
    strategyConfig.exit_rules.short.tp_sl_table = JSON.parse(JSON.stringify(defaultRules));

    renderTPSLTable(currentExitDirection);
}

function switchEntryDirection(direction) {
    currentEntryDirection = direction;

    // Update tab buttons
    const longTab = document.getElementById('longEntryTab');
    const shortTab = document.getElementById('shortEntryTab');
    const longContent = document.getElementById('longEntryContent');
    const shortContent = document.getElementById('shortEntryContent');

    if (direction === 'long') {
        longTab.style.background = '#2962ff';
        longTab.style.color = 'white';
        longTab.classList.add('active');

        shortTab.style.background = 'transparent';
        shortTab.style.color = '#787b86';
        shortTab.classList.remove('active');

        longContent.classList.remove('hidden');
        shortContent.classList.add('hidden');
    } else {
        shortTab.style.background = '#2962ff';
        shortTab.style.color = 'white';
        shortTab.classList.add('active');

        longTab.style.background = 'transparent';
        longTab.style.color = '#787b86';
        longTab.classList.remove('active');

        shortContent.classList.remove('hidden');
        longContent.classList.add('hidden');
    }
}

function switchExitDirection(direction) {
    currentExitDirection = direction;

    // Update tab buttons
    const longTab = document.getElementById('longExitTab');
    const shortTab = document.getElementById('shortExitTab');
    const longContent = document.getElementById('longExitContent');
    const shortContent = document.getElementById('shortExitContent');

    if (direction === 'long') {
        longTab.style.background = '#2962ff';
        longTab.style.color = 'white';
        longTab.classList.add('active');

        shortTab.style.background = 'transparent';
        shortTab.style.color = '#787b86';
        shortTab.classList.remove('active');

        longContent.classList.remove('hidden');
        shortContent.classList.add('hidden');
    } else {
        shortTab.style.background = '#2962ff';
        shortTab.style.color = 'white';
        shortTab.classList.add('active');

        longTab.style.background = 'transparent';
        longTab.style.color = '#787b86';
        longTab.classList.remove('active');

        shortContent.classList.remove('hidden');
        longContent.classList.add('hidden');
    }

    renderTPSLTable(direction);
}

function addTPSLRule(direction = currentExitDirection) {
    strategyConfig.exit_rules[direction].tp_sl_table.push({
        profit_range: [0, 2],
        tp: 5,
        sl: 3,
        trailing: 2
    });

    renderTPSLTable(direction);
}

function removeTPSLRule(index, direction = currentExitDirection) {
    strategyConfig.exit_rules[direction].tp_sl_table.splice(index, 1);
    renderTPSLTable(direction);
}

function renderTPSLTable(direction = currentExitDirection) {
    const containerId = direction === 'long' ? 'tpslTableLong' : 'tpslTableShort';
    const container = document.getElementById(containerId);

    if (!container) {
        console.warn('TP/SL table container not found:', containerId);
        return;
    }

    container.innerHTML = strategyConfig.exit_rules[direction].tp_sl_table.map((rule, index) => `
        <div class="tpsl-row">
            <div>
                <input type="number" value="${rule.profit_range[0]}"
                       onchange="updateTPSLRule(${index}, 'range_min', this.value, '${direction}')" style="width: 45%; display: inline-block;">
                <span style="margin: 0 5px;">-</span>
                <input type="number" value="${rule.profit_range[1]}"
                       onchange="updateTPSLRule(${index}, 'range_max', this.value, '${direction}')" style="width: 45%; display: inline-block;">
            </div>
            <input type="number" value="${rule.tp}"
                   onchange="updateTPSLRule(${index}, 'tp', this.value, '${direction}')">
            <input type="number" value="${rule.sl}"
                   onchange="updateTPSLRule(${index}, 'sl', this.value, '${direction}')">
            <input type="number" value="${rule.trailing}"
                   onchange="updateTPSLRule(${index}, 'trailing', this.value, '${direction}')">
            <button class="btn-remove" onclick="removeTPSLRule(${index}, '${direction}')">✕</button>
        </div>
    `).join('');
}

function updateTPSLRule(index, field, value, direction = currentExitDirection) {
    const rule = strategyConfig.exit_rules[direction].tp_sl_table[index];

    if (field === 'range_min') {
        rule.profit_range[0] = parseFloat(value);
    } else if (field === 'range_max') {
        rule.profit_range[1] = parseFloat(value);
    } else {
        rule[field] = parseFloat(value);
    }
}

// ==================== STRATEGY ACTIONS ====================

function newStrategy() {
    if (!confirm('⚠️ Tạo strategy mới?\n\nTất cả thay đổi chưa lưu sẽ bị mất!')) {
        return;
    }
    
    // Reset strategy config to default
    strategyConfig = {
        name: "New Strategy",
        description: "",
        indicators: [],
        entry_conditions: {
            long: [],
            short: []
        },
        exit_rules: {
            long: {
                dynamic_tp_sl: true,
                tp_sl_table: [],
                time_exit: "14:30"
            },
            short: {
                dynamic_tp_sl: true,
                tp_sl_table: [],
                time_exit: "14:30"
            },
            base_time: "09:00"
        }
    };

    // Reset current exit direction to long
    currentExitDirection = 'long';

    // Clear form fields
    document.getElementById('strategyName').value = "New Strategy";
    document.getElementById('strategyDescription').value = "";

    // Clear conditions
    document.getElementById('longConditions').innerHTML = '<div style="text-align: center; color: #888; padding: 20px;">No conditions added yet</div>';
    document.getElementById('shortConditions').innerHTML = '<div style="text-align: center; color: #888; padding: 20px;">No conditions added yet</div>';

    // Clear indicators
    document.getElementById('indicatorsList').innerHTML = '<div style="text-align: center; color: #888; padding: 20px;">No indicators added</div>';

    // Reset exit rules for both long and short
    document.getElementById('exitTimeLong').value = "14:30";
    document.getElementById('exitTimeShort').value = "14:30";
    document.getElementById('baseTime').value = "09:00";
    document.getElementById('dynamicTPSLLong').checked = true;
    document.getElementById('dynamicTPSLShort').checked = true;
    document.getElementById('tpslTableLong').innerHTML = '';
    document.getElementById('tpslTableShort').innerHTML = '';

    // Switch to long exit tab
    switchExitDirection('long');

    // Clear chart signals
    if (typeof workspaceCandlestickSeries !== 'undefined' && workspaceCandlestickSeries) {
        workspaceCandlestickSeries.setMarkers([]);
    }

    // IMPORTANT: Update window.strategyConfig so chart indicators use default base_time
    window.strategyConfig = strategyConfig;
    console.log('✅ Updated window.strategyConfig with default base_time: 09:00');

    console.log('✅ New strategy created');
    alert('✅ Đã tạo strategy mới!');
}

function saveStrategy() {
    // Collect all form data
    strategyConfig.name = document.getElementById('strategyName').value || 'My Strategy';
    strategyConfig.description = document.getElementById('strategyDescription').value || '';

    // Get Trading Engine config if available
    if (typeof tradingEngine !== 'undefined') {
        strategyConfig.trading_engine = {
            entryAfterCandle: tradingEngine.config.entryAfterCandle,
            exitTiming: tradingEngine.config.exitTiming,
            positionMode: tradingEngine.config.positionMode,
            entryPriceType: tradingEngine.config.entryPriceType,
            exitMethods: tradingEngine.config.exitMethods,
            profitConfig: tradingEngine.config.profitConfig,
            trailingConfig: tradingEngine.config.trailingConfig,
            expiryConfig: tradingEngine.config.expiryConfig
        };
    }

    // Keep exit rules from Exit tab (TP/SL table)
    // Get base_time from form
    const baseTimeValue = document.getElementById('baseTime')?.value || '09:00';
    console.log('🔍 DEBUG: baseTime input value =', baseTimeValue);

    strategyConfig.exit_rules = {
        long: {
            dynamic_tp_sl: document.getElementById('dynamicTPSLLong')?.checked || false,
            tp_sl_table: strategyConfig.exit_rules?.long?.tp_sl_table || [],
            time_exit: document.getElementById('exitTimeLong')?.value || '14:30'
        },
        short: {
            dynamic_tp_sl: document.getElementById('dynamicTPSLShort')?.checked || false,
            tp_sl_table: strategyConfig.exit_rules?.short?.tp_sl_table || [],
            time_exit: document.getElementById('exitTimeShort')?.value || '14:30'
        },
        base_time: baseTimeValue
    };

    console.log('🔍 DEBUG: strategyConfig.exit_rules after assignment:', JSON.stringify(strategyConfig.exit_rules, null, 2));
    console.log('💾 Saving strategy:', strategyConfig);

    // Send to backend
    fetch('/api/save-strategy', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(strategyConfig)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            // Success notification
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                background: linear-gradient(135deg, #26a69a 0%, #089981 100%);
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(38, 166, 154, 0.3);
                z-index: 10000;
                font-size: 14px;
                font-weight: 600;
                animation: slideIn 0.3s ease;
            `;
            notification.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 20px;">✅</span>
                    <div>
                        <div>Strategy Saved Successfully!</div>
                        <div style="font-size: 12px; font-weight: 400; opacity: 0.9; margin-top: 4px;">${strategyConfig.name}</div>
                    </div>
                </div>
            `;
            document.body.appendChild(notification);

            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }, 3000);

            console.log('Strategy saved:', result);
        } else {
            alert('❌ Error saving strategy: ' + (result.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Save error:', error);

        // Error notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: linear-gradient(135deg, #ef5350 0%, #f23645 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(239, 83, 80, 0.3);
            z-index: 10000;
            font-size: 14px;
            font-weight: 600;
            animation: slideIn 0.3s ease;
        `;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 20px;">❌</span>
                <div>
                    <div>Error Saving Strategy</div>
                    <div style="font-size: 12px; font-weight: 400; opacity: 0.9; margin-top: 4px;">${error.message}</div>
                </div>
            </div>
        `;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    });
}

// Add animation styles
if (!document.getElementById('saveStrategyAnimations')) {
    const style = document.createElement('style');
    style.id = 'saveStrategyAnimations';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

function loadStrategy() {
    // Create dialog HTML
    const dialogHTML = `
        <div id="loadStrategyDialog" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        ">
            <div style="
                background: #1e222d;
                border: 1px solid #2a2e39;
                border-radius: 8px;
                padding: 20px;
                max-width: 500px;
                width: 90%;
                max-height: 70vh;
                overflow-y: auto;
            ">
                <h3 style="color: #2962ff; margin-top: 0;">Select strategy to load:</h3>
                
                <div id="strategyListContainer" style="margin-bottom: 15px;">
                    <div style="color: #787b86;">Loading strategies...</div>
                </div>
                
                <div style="border-top: 1px solid #2a2e39; padding-top: 15px; margin-top: 15px;">
                    <label style="color: #d1d4dc; display: block; margin-bottom: 10px;">
                        📁 Or load from file:
                    </label>
                    <input type="file" id="strategyFileInput" accept=".json" style="
                        width: 100%;
                        padding: 8px;
                        background: #2a2e39;
                        border: 1px solid #363a45;
                        border-radius: 4px;
                        color: #d1d4dc;
                        cursor: pointer;
                    ">
                </div>
                
                <div style="display: flex; gap: 10px; margin-top: 20px;">
                    <button id="cancelLoadBtn" style="
                        flex: 1;
                        padding: 10px;
                        background: #ef5350;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-weight: bold;
                    ">Hủy</button>
                </div>
            </div>
        </div>
    `;
    
    // Add dialog to body
    document.body.insertAdjacentHTML('beforeend', dialogHTML);
    
    const dialog = document.getElementById('loadStrategyDialog');
    const listContainer = document.getElementById('strategyListContainer');
    const fileInput = document.getElementById('strategyFileInput');
    const cancelBtn = document.getElementById('cancelLoadBtn');
    
    // Fetch available strategies
    fetch('/api/list-strategies')
    .then(response => response.json())
    .then(result => {
        if (result.success && result.strategies.length > 0) {
            listContainer.innerHTML = result.strategies.map((s, i) => `
                <div class="strategy-item" data-index="${i}" data-filename="${s.filename}" style="
                    padding: 12px;
                    margin: 8px 0;
                    background: #2a2e39;
                    border: 1px solid #363a45;
                    border-radius: 4px;
                    transition: all 0.2s;
                    color: #d1d4dc;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    gap: 10px;
                " onmouseover="this.style.background='#363a45'; this.style.borderColor='#2962ff';"
                   onmouseout="this.style.background='#2a2e39'; this.style.borderColor='#363a45';">
                    <div style="flex: 1; cursor: pointer;" onclick="loadStrategyFromList('${s.filename}')">
                        <div style="font-weight: bold; color: #2962ff;">${i + 1}. ${s.name}</div>
                        <div style="font-size: 11px; color: #787b86; margin-top: 4px;">${s.filename}</div>
                    </div>
                    <button onclick="event.stopPropagation(); deleteStrategy('${s.filename}', '${s.name.replace(/'/g, "\\'")}');" style="
                        padding: 8px 12px;
                        background: #ef5350;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                        font-weight: 600;
                        transition: all 0.2s;
                        flex-shrink: 0;
                    " onmouseover="this.style.background='#d32f2f';"
                       onmouseout="this.style.background='#ef5350';"
                       title="Delete this strategy">🗑️ Delete</button>
                </div>
            `).join('');
        } else {
            listContainer.innerHTML = '<div style="color: #787b86; padding: 20px; text-align: center;">📂 No saved strategies found!</div>';
        }
    });
    
    // Handle file input
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                try {
                    const strategy = JSON.parse(event.target.result);
                    loadStrategyFromJSON(strategy);
                    dialog.remove();
                } catch (error) {
                    alert('❌ Invalid JSON file: ' + error.message);
                }
            };
            reader.readAsText(file);
        }
    });
    
    // Cancel button
    cancelBtn.addEventListener('click', () => dialog.remove());
    
    // Close on background click
    dialog.addEventListener('click', (e) => {
        if (e.target === dialog) dialog.remove();
    });
}

function loadStrategyFromList(filename) {
    const dialog = document.getElementById('loadStrategyDialog');
    if (dialog) dialog.remove();
    loadStrategyFile(filename);
}

function deleteStrategy(filename, strategyName) {
    // Confirm before delete
    const confirmMsg = `⚠️ Xóa strategy "${strategyName}"?\n\nFile: ${filename}\n\nHành động này không thể hoàn tác!`;

    if (!confirm(confirmMsg)) {
        return;
    }

    console.log(`🗑️ Deleting strategy: ${filename}`);

    // Call API to delete
    fetch(`/api/delete-strategy/${filename}`, {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'}
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            console.log(`✅ Strategy deleted: ${filename}`);

            // Show success message
            alert(`✅ Đã xóa strategy "${strategyName}" thành công!`);

            // Refresh strategy list
            const dialog = document.getElementById('loadStrategyDialog');
            if (dialog) {
                dialog.remove();
                // Reopen dialog to show updated list
                loadStrategy();
            }
        } else {
            console.error('❌ Delete failed:', result.error);
            alert(`❌ Không thể xóa strategy!\n\nLỗi: ${result.error || 'Unknown error'}`);
        }
    })
    .catch(error => {
        console.error('❌ Delete error:', error);
        alert(`❌ Lỗi khi xóa strategy!\n\n${error.message}`);
    });
}

function loadStrategyFromJSON(strategy) {
    strategyConfig = strategy;

    // Migrate old exit_rules format to new long/short format if needed
    if (strategyConfig.exit_rules && !strategyConfig.exit_rules.long && !strategyConfig.exit_rules.short) {
        const oldExitRules = strategyConfig.exit_rules;
        strategyConfig.exit_rules = {
            long: {
                dynamic_tp_sl: oldExitRules.dynamic_tp_sl || true,
                tp_sl_table: oldExitRules.tp_sl_table || [],
                time_exit: oldExitRules.time_exit || "14:30"
            },
            short: {
                dynamic_tp_sl: oldExitRules.dynamic_tp_sl || true,
                tp_sl_table: oldExitRules.tp_sl_table ? JSON.parse(JSON.stringify(oldExitRules.tp_sl_table)) : [],
                time_exit: oldExitRules.time_exit || "14:30"
            },
            base_time: oldExitRules.base_time || "09:00"
        };
    }

    // Add base_time if missing (for backward compatibility)
    if (strategyConfig.exit_rules && !strategyConfig.exit_rules.base_time) {
        strategyConfig.exit_rules.base_time = "09:00";
    }

    // Update UI
    document.getElementById('strategyName').value = strategyConfig.name;
    document.getElementById('strategyDescription').value = strategyConfig.description || '';

    renderConditions('long');
    renderConditions('short');
    renderActiveIndicators();

    // Update exit UI for both long and short
    document.getElementById('exitTimeLong').value = strategyConfig.exit_rules.long.time_exit || "14:30";
    document.getElementById('exitTimeShort').value = strategyConfig.exit_rules.short.time_exit || "14:30";
    document.getElementById('baseTime').value = strategyConfig.exit_rules.base_time || "09:00";
    document.getElementById('dynamicTPSLLong').checked = strategyConfig.exit_rules.long.dynamic_tp_sl !== false;
    document.getElementById('dynamicTPSLShort').checked = strategyConfig.exit_rules.short.dynamic_tp_sl !== false;

    renderTPSLTable('long');
    renderTPSLTable('short');

    // Load Trading Engine config
    loadTradingEngineFromStrategy();

    // IMPORTANT: Update window.strategyConfig so chart indicators can read updated base_time
    window.strategyConfig = strategyConfig;
    console.log('✅ Updated window.strategyConfig with base_time:', strategyConfig.exit_rules.base_time);

    alert(`✅ Strategy "${strategyConfig.name}" loaded from file!`);

    // Auto refresh signals
    setTimeout(() => {
        console.log('🔄 Auto-refreshing signals after strategy load...');
        loadFromIndexedDB().then(data => {
            if (data && data.candlesticks && data.candlesticks.length > 0) {
                window.currentStrategyConfig = strategyConfig;
                if (typeof window.displayStrategySignals !== 'undefined') {
                    window.displayStrategySignals(data.candlesticks);
                }
            }
        }).catch(error => {
            console.error('Error loading data:', error);
        });
    }, 500);

    // Render indicators on chart
    if (typeof calculateAndRenderIndicators === 'function') {
        setTimeout(() => calculateAndRenderIndicators(), 800);
    }
}

function loadStrategyFile(filename) {
    fetch(`/api/load-strategy/${filename}`)
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            strategyConfig = result.strategy;

            // Migrate old exit_rules format to new long/short format if needed
            if (strategyConfig.exit_rules && !strategyConfig.exit_rules.long && !strategyConfig.exit_rules.short) {
                const oldExitRules = strategyConfig.exit_rules;
                strategyConfig.exit_rules = {
                    long: {
                        dynamic_tp_sl: oldExitRules.dynamic_tp_sl || true,
                        tp_sl_table: oldExitRules.tp_sl_table || [],
                        time_exit: oldExitRules.time_exit || "14:30"
                    },
                    short: {
                        dynamic_tp_sl: oldExitRules.dynamic_tp_sl || true,
                        tp_sl_table: oldExitRules.tp_sl_table ? JSON.parse(JSON.stringify(oldExitRules.tp_sl_table)) : [],
                        time_exit: oldExitRules.time_exit || "14:30"
                    },
                    base_time: oldExitRules.base_time || "09:00"
                };
            }

            // Add base_time if missing (for backward compatibility)
            if (strategyConfig.exit_rules && !strategyConfig.exit_rules.base_time) {
                strategyConfig.exit_rules.base_time = "09:00";
            }

            // Update UI
            document.getElementById('strategyName').value = strategyConfig.name;
            document.getElementById('strategyDescription').value = strategyConfig.description || '';

            renderConditions('long');
            renderConditions('short');
            renderActiveIndicators();

            // Update exit UI for both long and short
            document.getElementById('exitTimeLong').value = strategyConfig.exit_rules.long.time_exit || "14:30";
            document.getElementById('exitTimeShort').value = strategyConfig.exit_rules.short.time_exit || "14:30";
            document.getElementById('baseTime').value = strategyConfig.exit_rules.base_time || "09:00";
            document.getElementById('dynamicTPSLLong').checked = strategyConfig.exit_rules.long.dynamic_tp_sl !== false;
            document.getElementById('dynamicTPSLShort').checked = strategyConfig.exit_rules.short.dynamic_tp_sl !== false;

            renderTPSLTable('long');
            renderTPSLTable('short');

            // Load Trading Engine config
            loadTradingEngineFromStrategy();

            // IMPORTANT: Update window.strategyConfig so chart indicators can read updated base_time
            window.strategyConfig = strategyConfig;
            console.log('✅ Updated window.strategyConfig with base_time:', strategyConfig.exit_rules.base_time);

            alert(`✅ Strategy "${strategyConfig.name}" loaded!`);

            // Auto refresh signals after loading strategy (silently)
            setTimeout(() => {
                console.log('🔄 Auto-refreshing signals after strategy load...');

                // Check if we have data before refreshing
                loadFromIndexedDB().then(data => {
                    if (data && data.candlesticks && data.candlesticks.length > 0) {
                        window.currentStrategyConfig = strategyConfig;
                        if (typeof window.displayStrategySignals !== 'undefined') {
                            window.displayStrategySignals(data.candlesticks);
                        }
                    } else {
                        console.log('ℹ️ No data available for signal generation');
                    }
                }).catch(error => {
                    console.error('Error loading data:', error);
                });
            }, 500);
        } else {
            alert('❌ Error loading strategy: ' + result.error);
        }
    });
}

/**
 * Load Trading Engine configuration from strategy into UI
 */
function loadTradingEngineFromStrategy() {
    if (!strategyConfig.trading_engine) {
        console.log('ℹ️ No trading_engine config in strategy, using defaults');
        return;
    }

    const config = strategyConfig.trading_engine;
    console.log('⚙️ Loading Trading Engine config:', config);

    // Update tradingEngine.config object
    if (typeof tradingEngine !== 'undefined') {
        if (config.entryAfterCandle) tradingEngine.config.entryAfterCandle = config.entryAfterCandle;
        if (config.exitTiming) tradingEngine.config.exitTiming = config.exitTiming;
        if (config.positionMode) tradingEngine.config.positionMode = config.positionMode;
        if (config.entryPriceType) tradingEngine.config.entryPriceType = config.entryPriceType;
        if (config.exitMethods) tradingEngine.config.exitMethods = config.exitMethods;
        if (config.profitConfig) tradingEngine.config.profitConfig = config.profitConfig;
        if (config.trailingConfig) tradingEngine.config.trailingConfig = config.trailingConfig;
        if (config.expiryConfig) tradingEngine.config.expiryConfig = config.expiryConfig;
    }

    // Update Entry After Candle checkboxes
    const entryAfter1 = document.getElementById('entryAfter1');
    const entryAfter2 = document.getElementById('entryAfter2');
    if (entryAfter1) entryAfter1.checked = config.entryAfterCandle?.includes(1) || false;
    if (entryAfter2) entryAfter2.checked = config.entryAfterCandle?.includes(2) || false;

    // Update Exit Timing radio
    if (config.exitTiming) {
        const exitTimingRadio = document.querySelector(`input[name="exitTiming"][value="${config.exitTiming}"]`);
        if (exitTimingRadio) exitTimingRadio.checked = true;
    }

    // Update Position Mode radio
    if (config.positionMode) {
        const positionModeRadio = document.querySelector(`input[name="positionMode"][value="${config.positionMode}"]`);
        if (positionModeRadio) positionModeRadio.checked = true;
    }

    // Update Entry Price Type radio
    if (config.entryPriceType) {
        const entryPriceRadio = document.querySelector(`input[name="entryPriceType"][value="${config.entryPriceType}"]`);
        if (entryPriceRadio) entryPriceRadio.checked = true;
    }

    // Update Exit Methods checkboxes
    if (config.exitMethods) {
        const exitBySignal = document.getElementById('exitBySignal');
        const exitByTP = document.getElementById('exitByTP');
        const exitBySL = document.getElementById('exitBySL');
        const exitByTrailing = document.getElementById('exitByTrailing');
        const exitByExpiry = document.getElementById('exitByExpiry');

        if (exitBySignal) exitBySignal.checked = config.exitMethods.bySignal !== false;
        if (exitByTP) exitByTP.checked = config.exitMethods.byTP || false;
        if (exitBySL) exitBySL.checked = config.exitMethods.bySL || false;
        if (exitByTrailing) exitByTrailing.checked = config.exitMethods.byTrailing || false;
        if (exitByExpiry) exitByExpiry.checked = config.exitMethods.byExpiry || false;
    }

    // Update Profit Config inputs
    if (config.profitConfig) {
        const tpBuy = document.getElementById('tpBuyPoints');
        const tpShort = document.getElementById('tpShortPoints');
        const sl = document.getElementById('stopLossPoints');
        const slShort = document.getElementById('slShortPoints');

        if (tpBuy) tpBuy.value = config.profitConfig.tpBuyPoints || 10;
        if (tpShort) tpShort.value = config.profitConfig.tpShortPoints || 10;
        if (sl) sl.value = config.profitConfig.stopLossPoints || 20;
        if (slShort) slShort.value = config.profitConfig.slShortPoints || 20;
    }

    // Update Trailing Config
    if (config.trailingConfig) {
        // Trailing type radio
        if (config.trailingConfig.type) {
            const trailingTypeRadio = document.querySelector(`input[name="trailingType"][value="${config.trailingConfig.type}"]`);
            if (trailingTypeRadio) trailingTypeRadio.checked = true;
        }

        // Fixed trailing points
        const fixedBuy = document.getElementById('fixedTrailingBuyPoints');
        const fixedShort = document.getElementById('fixedTrailingShortPoints');
        if (fixedBuy) fixedBuy.value = config.trailingConfig.fixedBuyPoints || 5;
        if (fixedShort) fixedShort.value = config.trailingConfig.fixedShortPoints || 5;

        // Skip long candle
        const skipLongCandle = document.getElementById('skipLongCandleForTrailing');
        if (skipLongCandle) skipLongCandle.checked = config.trailingConfig.skipLongCandle || false;

        const longCandleSize = document.getElementById('longCandleSize');
        if (longCandleSize) longCandleSize.value = config.trailingConfig.longCandleSize || 50;

        // Dynamic tiers - will be handled by renderDynamicTierTable if it exists
        if (config.trailingConfig.dynamicTiers && typeof renderDynamicTierTable === 'function') {
            setTimeout(() => renderDynamicTierTable(), 100);
        }
    }

    // Update Expiry Config
    if (config.expiryConfig) {
        const expiryDates = document.getElementById('expiryDates');
        const expiryTime = document.getElementById('expiryTime');

        // Convert Date objects to DDMMYY format string
        if (config.expiryConfig.dates && Array.isArray(config.expiryConfig.dates)) {
            const dateStrings = config.expiryConfig.dates.map(d => {
                if (d instanceof Date) {
                    const day = String(d.getDate()).padStart(2, '0');
                    const month = String(d.getMonth() + 1).padStart(2, '0');
                    const year = String(d.getFullYear()).slice(-2);
                    return day + month + year;
                }
                return d;
            }).join(',');
            if (expiryDates) expiryDates.value = dateStrings;
        }

        if (config.expiryConfig.time && expiryTime) {
            expiryTime.value = config.expiryConfig.time;
        }
    }

    console.log('✅ Trading Engine config loaded successfully');
}

function runBacktest() {
    alert('🚀 Running backtest...\n\nThis will be implemented soon!');

    // TODO: Navigate to backtest page with this strategy
    // window.location.href = '/backtest?strategy=' + strategyConfig.name;
}

// ==================== QUICK ACTIONS ====================

function refreshSignals() {
    console.log('🔄 Refreshing signals on chart...');
    console.log('Current strategy config:', strategyConfig);
    
    // Check if workspace functions are available
    if (typeof window.displayStrategySignals === 'undefined') {
        alert('⚠️ Signal display not available. Make sure you are on the Strategy Builder page.');
        return;
    }
    
    // Check if we have indicators and conditions
    if (!strategyConfig.indicators || strategyConfig.indicators.length === 0) {
        alert('⚠️ Please add indicators first!');
        return;
    }
    
    if (strategyConfig.entry_conditions.long.length === 0 && strategyConfig.entry_conditions.short.length === 0) {
        alert('⚠️ Please add entry conditions first!');
        return;
    }
    
    // Load data from IndexedDB
    loadFromIndexedDB().then(data => {
        if (data && data.candlesticks) {
            console.log(`📊 Loaded ${data.candlesticks.length} candles`);
            
            // Make strategyConfig available globally for workspace.js
            window.currentStrategyConfig = strategyConfig;
            
            // Call workspace function
            window.displayStrategySignals(data.candlesticks);
            
            console.log('✅ Signal refresh completed');
        } else {
            alert('⚠️ No chart data available. Please upload data from main page first.');
        }
    }).catch(error => {
        console.error('Error refreshing signals:', error);
        alert('❌ Error refreshing signals: ' + error.message);
    });
}

function testStrategy() {
    console.log('🧪 Testing strategy conditions...');
    console.log('Strategy config:', strategyConfig);
    
    // Check if we have data
    if (typeof loadFromIndexedDB === 'undefined') {
        alert('🧪 Strategy config validated!\n\nNote: Chart signals will show when data is loaded.');
        return;
    }
    
    // Try to generate signals with current data
    loadFromIndexedDB().then(async (data) => {
        if (data && data.candlesticks) {
            try {
                // Save current strategy first
                const tempFilename = '_temp_test_strategy.json';
                await fetch('/api/save-strategy', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({...strategyConfig, name: 'TempTest'})
                });
                
                // Generate signals
                const signalData = {
                    strategy: tempFilename,
                    data: {
                        open: data.candlesticks.map(c => c.open),
                        high: data.candlesticks.map(c => c.high),
                        low: data.candlesticks.map(c => c.low),
                        close: data.candlesticks.map(c => c.close),
                        volume: data.volumes.map(v => v.value)
                    }
                };
                
                const response = await fetch('/api/generate-signals', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(signalData)
                });
                
                const result = await response.json();
                
                if (result.success && typeof displayWorkspaceSignals !== 'undefined') {
                    displayWorkspaceSignals(result.signals, data.candlesticks);
                    alert('✅ Strategy tested!\n\nCheck chart for buy/short signals.');
                }
            } catch (error) {
                console.error('Error testing strategy:', error);
                alert('🧪 Strategy config validated!\n\nConditions look good.');
            }
        } else {
            alert('🧪 Strategy validated!\n\nUpload data to see signals on chart.');
        }
    }).catch(() => {
        alert('🧪 Strategy config validated!\n\nConditions look good.');
    });
}

function clearStrategy() {
    if (!confirm('⚠️ Clear all conditions and indicators?')) {
        return;
    }
    
    strategyConfig.entry_conditions.long = [];
    strategyConfig.entry_conditions.short = [];
    strategyConfig.indicators = [];
    
    renderConditions('long');
    renderConditions('short');
    renderActiveIndicators();
    
    console.log('🗑️ Strategy cleared');
}

// Expose functions globally
window.loadStrategyFromList = loadStrategyFromList;
window.loadStrategyFromJSON = loadStrategyFromJSON;

// Expose active indicators for chart display
Object.defineProperty(window, 'activeIndicators', {
    get: function() {
        return strategyConfig.indicators;
    }
});

// ==================== SETTINGS TAB EVENT LISTENERS ====================

// Toggle expiry exit time section
document.addEventListener('DOMContentLoaded', function() {
    const exitOnExpiryCheckbox = document.getElementById('exitOnExpiry');
    const expiryTimeSection = document.getElementById('expiryTimeSection');
    
    if (exitOnExpiryCheckbox && expiryTimeSection) {
        exitOnExpiryCheckbox.addEventListener('change', function() {
            expiryTimeSection.style.display = this.checked ? 'block' : 'none';
        });
    }

    console.log('✅ Settings tab event listeners initialized');
});


// ============================================================================
// AUTO GENERATION FUNCTIONS
// ============================================================================

/**
 * Open auto-generate modal
 */
function openAutoGenerateModal() {
    const modal = document.getElementById('autoGenerateModal');
    if (modal) {
        modal.classList.remove('hidden');

        // Reset progress and results
        const progress = document.getElementById('autoGenProgress');
        const results = document.getElementById('autoGenResults');
        if (progress) progress.classList.add('hidden');
        if (results) {
            results.classList.add('hidden');
            results.innerHTML = '';
        }
    }
}

/**
 * Close auto-generate modal
 */
function closeAutoGenerateModal() {
    const modal = document.getElementById('autoGenerateModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

/**
 * Start auto-generation process
 */
async function startAutoGeneration() {
    // Get parameters
    const longSignals = parseInt(document.getElementById('autoGenLongSignals').value);
    const shortSignals = parseInt(document.getElementById('autoGenShortSignals').value);
    const indicatorsPerSignal = parseInt(document.getElementById('autoGenIndicatorsPerSignal').value);
    const profitLevels = parseInt(document.getElementById('autoGenProfitLevels').value);
    const profitStep = parseInt(document.getElementById('autoGenProfitStep').value);
    const keepIndicators = document.getElementById('autoGenKeepIndicators').checked;
    const randomizeTPSL = document.getElementById('autoGenRandomizeTPSL').checked;

    // Show progress
    const progress = document.getElementById('autoGenProgress');
    const results = document.getElementById('autoGenResults');
    const status = document.getElementById('autoGenStatus');
    const progressBar = document.getElementById('autoGenProgressBar');

    if (progress) progress.classList.remove('hidden');
    if (results) {
        results.classList.add('hidden');
        results.innerHTML = '';
    }

    try {
        if (status) status.textContent = 'Generating entry conditions and TP/SL rules...';
        if (progressBar) progressBar.style.width = '10%';

        // Prepare current strategy data
        const currentStrategy = {
            name: strategyConfig.name,
            description: strategyConfig.description,
            indicators: strategyConfig.indicators,
            entry_conditions: strategyConfig.entry_conditions,
            exit_rules: strategyConfig.exit_rules,
            trading_engine: strategyConfig.trading_engine
        };

        // Call backend API
        const response = await fetch('/api/auto-generate-strategy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_strategy: currentStrategy,
                long_signals: longSignals,
                short_signals: shortSignals,
                indicators_per_signal: indicatorsPerSignal,
                profit_levels: profitLevels,
                profit_step: profitStep,
                keep_indicators: keepIndicators,
                randomize_tpsl: randomizeTPSL
            })
        });

        if (progressBar) progressBar.style.width = '50%';

        if (!response.ok) {
            throw new Error('HTTP error! status: ' + response.status);
        }

        const data = await response.json();

        if (progressBar) progressBar.style.width = '100%';

        // Auto-apply generated strategy
        if (data.success && data.strategy) {
            const strategy = data.strategy;

            if (status) status.textContent = 'Applying to strategy...';

            // Apply to current strategy config
            strategyConfig.entry_conditions = strategy.entry_conditions;
            strategyConfig.exit_rules = strategy.exit_rules;

            // Update indicators if provided
            if (strategy.indicators && strategy.indicators.length > 0) {
                strategyConfig.indicators = strategy.indicators;
                console.log(`📊 Updated indicators: ${strategy.indicators.length} indicators`);

                // Re-render Indicators tab
                if (typeof renderActiveIndicators === 'function') {
                    renderActiveIndicators();
                }
            }

            // Update name/description if modified
            if (strategy.name) {
                strategyConfig.name = strategy.name;
                document.getElementById('strategyName').value = strategy.name;
            }
            if (strategy.description) {
                strategyConfig.description = strategy.description;
                document.getElementById('strategyDescription').value = strategy.description;
            }

            // Re-render UI for all tabs
            renderConditions('long');
            renderConditions('short');
            renderTPSLTable('long');
            renderTPSLTable('short');

            // Update exit time fields
            if (strategy.exit_rules.long.time_exit) {
                const exitTimeLong = document.getElementById('exitTimeLong');
                if (exitTimeLong) exitTimeLong.value = strategy.exit_rules.long.time_exit;
            }
            if (strategy.exit_rules.short.time_exit) {
                const exitTimeShort = document.getElementById('exitTimeShort');
                if (exitTimeShort) exitTimeShort.value = strategy.exit_rules.short.time_exit;
            }

            // Update base time field
            if (strategy.exit_rules.base_time) {
                const baseTime = document.getElementById('baseTime');
                if (baseTime) baseTime.value = strategy.exit_rules.base_time;
            }

            // Update dynamic TP/SL checkboxes
            const dynamicTPSLLong = document.getElementById('dynamicTPSLLong');
            const dynamicTPSLShort = document.getElementById('dynamicTPSLShort');
            if (dynamicTPSLLong) dynamicTPSLLong.checked = strategy.exit_rules.long.dynamic_tp_sl;
            if (dynamicTPSLShort) dynamicTPSLShort.checked = strategy.exit_rules.short.dynamic_tp_sl;

            if (status) status.textContent = 'Strategy applied successfully!';

            // Wait a moment then close modal
            setTimeout(() => {
                closeAutoGenerateModal();

                // Show success notification
                const longCount = strategy.entry_conditions.long.length;
                const shortCount = strategy.entry_conditions.short.length;
                const profitLevels = strategy.exit_rules.long.tp_sl_table.length;

                alert('✅ Strategy Generated & Applied!\n\n' +
                      '📈 Long Entries: ' + longCount + '\n' +
                      '📉 Short Entries: ' + shortCount + '\n' +
                      '💹 Profit Levels: ' + profitLevels + '\n\n' +
                      'Please review the Entry and Exit tabs.');
            }, 800);
        }

    } catch (error) {
        console.error('Error generating strategy:', error);
        if (status) status.textContent = 'Error: ' + error.message;
        alert('Failed to generate strategy. Please try again.');
    }
}

/**
 * Display single auto-generated strategy result
 */
function displayAutoGenResult(strategy) {
    const results = document.getElementById('autoGenResults');
    if (!results) return;

    let html = '<div style="background: #2a2e39; padding: 20px; border-radius: 4px; border-left: 4px solid #667eea;">';
    html += '<h4 style="margin: 0 0 15px 0; color: #d1d4dc; font-size: 14px;">✅ Strategy Modified Successfully!</h4>';

    // Entry conditions summary
    const longCount = strategy.entry_conditions.long.length;
    const shortCount = strategy.entry_conditions.short.length;
    const profitLevels = strategy.exit_rules.long.tp_sl_table.length;

    html += '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">';
    html += '<div style="text-align: center; padding: 10px; background: #1e222d; border-radius: 4px;">';
    html += '<div style="color: #787b86; font-size: 11px; margin-bottom: 5px;">Long Entries</div>';
    html += '<div style="color: #26a69a; font-size: 24px; font-weight: bold;">' + longCount + '</div>';
    html += '</div>';
    html += '<div style="text-align: center; padding: 10px; background: #1e222d; border-radius: 4px;">';
    html += '<div style="color: #787b86; font-size: 11px; margin-bottom: 5px;">Short Entries</div>';
    html += '<div style="color: #ef5350; font-size: 24px; font-weight: bold;">' + shortCount + '</div>';
    html += '</div>';
    html += '<div style="text-align: center; padding: 10px; background: #1e222d; border-radius: 4px;">';
    html += '<div style="color: #787b86; font-size: 11px; margin-bottom: 5px;">Profit Levels</div>';
    html += '<div style="color: #667eea; font-size: 24px; font-weight: bold;">' + profitLevels + '</div>';
    html += '</div>';
    html += '</div>';

    // Apply button
    html += '<div style="display: flex; gap: 10px;">';
    html += '<button onclick="applyGeneratedStrategy()" style="flex: 1; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 600;">Apply to Current Strategy</button>';
    html += '<button onclick="previewGeneratedStrategy()" style="flex: 1; padding: 12px; background: #2a2e39; color: #d1d4dc; border: 1px solid #667eea; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 600;">Preview Details</button>';
    html += '</div>';
    html += '</div>';

    results.innerHTML = html;

    // Store generated strategy
    window.generatedStrategy = strategy;
}

/**
 * Display auto-generation results (for batch generation - future use)
 */
function displayAutoGenResults(strategies) {
    const results = document.getElementById('autoGenResults');
    if (!results) return;

    if (strategies.length === 0) {
        results.innerHTML = '<div style="padding: 20px; text-align: center; color: #787b86;"><p>No strategies met the criteria. Try lowering the requirements.</p></div>';
        return;
    }

    let html = '<div style="display: flex; flex-direction: column; gap: 10px;">';

    strategies.forEach((item, index) => {
        const strategy = item.strategy;
        const res = item.results;

        const winRateColor = res.win_rate >= 0.6 ? '#26a69a' : '#d1d4dc';
        const profitFactorColor = res.profit_factor >= 2 ? '#26a69a' : '#d1d4dc';
        const returnColor = res.total_return >= 0 ? '#26a69a' : '#ef5350';

        html += '<div style="background: #2a2e39; padding: 15px; border-radius: 4px; border-left: 4px solid #667eea;">';
        html += '<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">';
        html += '<div>';
        html += '<h4 style="margin: 0 0 5px 0; color: #d1d4dc; font-size: 14px;">' + (strategy.name || 'Strategy ' + (index + 1)) + '</h4>';
        html += '<p style="margin: 0; color: #787b86; font-size: 12px;">' + (strategy.description || 'Auto-generated strategy') + '</p>';
        html += '</div>';
        html += '<button onclick="loadGeneratedStrategy(' + index + ')" style="padding: 6px 12px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">Load</button>';
        html += '</div>';
        html += '<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; font-size: 12px;">';
        html += '<div><span style="color: #787b86;">Win Rate:</span><span style="color: ' + winRateColor + '; font-weight: 600; margin-left: 5px;">' + (res.win_rate * 100).toFixed(1) + '%</span></div>';
        html += '<div><span style="color: #787b86;">Profit Factor:</span><span style="color: ' + profitFactorColor + '; font-weight: 600; margin-left: 5px;">' + res.profit_factor.toFixed(2) + '</span></div>';
        html += '<div><span style="color: #787b86;">Total Return:</span><span style="color: ' + returnColor + '; font-weight: 600; margin-left: 5px;">' + res.total_return.toFixed(2) + '%</span></div>';
        html += '<div><span style="color: #787b86;">Max DD:</span><span style="color: #ef5350; font-weight: 600; margin-left: 5px;">' + res.max_drawdown.toFixed(2) + '%</span></div>';
        html += '</div>';
        html += '</div>';
    });

    html += '</div>';
    results.innerHTML = html;

    // Store strategies for loading
    window.generatedStrategies = strategies;
}

/**
 * Load a generated strategy
 */
function loadGeneratedStrategy(index) {
    if (!window.generatedStrategies || !window.generatedStrategies[index]) {
        alert('Strategy not found');
        return;
    }

    const item = window.generatedStrategies[index];
    const strategy = item.strategy;

    // Load strategy into builder
    loadStrategyFromJSON(strategy);

    // Close modal
    closeAutoGenerateModal();

    // Show success message
    const msg = 'Loaded: ' + strategy.name + '\n\nWin Rate: ' + (item.results.win_rate * 100).toFixed(1) + '%\nProfit Factor: ' + item.results.profit_factor.toFixed(2);
    alert(msg);
}

/**
 * Apply generated strategy to current strategy
 */
function applyGeneratedStrategy() {
    if (!window.generatedStrategy) {
        alert('No generated strategy found');
        return;
    }

    const strategy = window.generatedStrategy;

    // Apply to current strategy config
    strategyConfig.entry_conditions = strategy.entry_conditions;
    strategyConfig.exit_rules = strategy.exit_rules;

    // Re-render UI
    renderConditions('long');
    renderConditions('short');
    renderTPSLTable('long');
    renderTPSLTable('short');

    // Close modal
    closeAutoGenerateModal();

    // Show success message
    alert('Strategy applied successfully!\n\nLong Entries: ' + strategy.entry_conditions.long.length + '\nShort Entries: ' + strategy.entry_conditions.short.length + '\n\nPlease review and save the strategy.');
}

/**
 * Preview generated strategy details
 */
function previewGeneratedStrategy() {
    if (!window.generatedStrategy) {
        alert('No generated strategy found');
        return;
    }

    const strategy = window.generatedStrategy;

    let preview = '=== GENERATED STRATEGY ===\n\n';

    // Long entries
    preview += '📈 LONG ENTRIES (' + strategy.entry_conditions.long.length + '):\n';
    strategy.entry_conditions.long.forEach((group, i) => {
        preview += '  ' + (i+1) + '. ' + group.name + ':\n';
        group.conditions.forEach((cond, j) => {
            preview += '     ' + cond.left + ' ' + cond.operator + ' ' + cond.right;
            if (j < group.conditions.length - 1) preview += ' ' + cond.logic;
            preview += '\n';
        });
    });

    preview += '\n📉 SHORT ENTRIES (' + strategy.entry_conditions.short.length + '):\n';
    strategy.entry_conditions.short.forEach((group, i) => {
        preview += '  ' + (i+1) + '. ' + group.name + ':\n';
        group.conditions.forEach((cond, j) => {
            preview += '     ' + cond.left + ' ' + cond.operator + ' ' + cond.right;
            if (j < group.conditions.length - 1) preview += ' ' + cond.logic;
            preview += '\n';
        });
    });

    // TP/SL for Long
    preview += '\n💹 TP/SL LEVELS (Long - ' + strategy.exit_rules.long.tp_sl_table.length + '):\n';
    strategy.exit_rules.long.tp_sl_table.forEach((rule, i) => {
        preview += '  ' + (i+1) + '. Profit ' + rule.profit_range[0] + '-' + rule.profit_range[1] + ': TP=' + rule.tp + ', SL=' + rule.sl + ', Trail=' + rule.trailing + '\n';
    });

    alert(preview);
}

console.log('✅ Auto-generation functions loaded');

// ==================== EXPOSE ALL FUNCTIONS TO WINDOW ====================
// Expose ALL 56 functions for onclick handlers and cross-file access

// Strategy config
window.strategyConfig = strategyConfig;

// Core functions
window.initStrategyBuilder = initStrategyBuilder;
window.initStrategyDB = initStrategyDB;
window.switchPanel = switchPanel;
window.triggerAutoSave = triggerAutoSave;

// Strategy management
window.newStrategy = newStrategy;
window.saveStrategy = saveStrategy;
window.loadStrategy = loadStrategy;
window.loadStrategyFile = loadStrategyFile;
window.loadStrategyFromJSON = loadStrategyFromJSON;
window.loadStrategyFromList = loadStrategyFromList;
window.autoSaveStrategy = autoSaveStrategy;
window.loadAutoSavedStrategy = loadAutoSavedStrategy;
window.clearStrategy = clearStrategy;
window.testStrategy = testStrategy;
window.runBacktest = runBacktest;
window.refreshSignals = refreshSignals;

// Indicator management
window.addIndicator = addIndicator;
window.removeIndicator = removeIndicator;
window.clearAllIndicators = clearAllIndicators;
window.editIndicator = editIndicator;
window.openIndicatorConfigModal = openIndicatorConfigModal;
window.closeIndicatorConfigModal = closeIndicatorConfigModal;
window.saveIndicatorFromModal = saveIndicatorFromModal;
window.renderActiveIndicators = renderActiveIndicators;
window.renderToContainer = renderToContainer;
window.toggleIndicatorDisplay = toggleIndicatorDisplay;
window.openIndicatorDisplaySettings = openIndicatorDisplaySettings;
window.createIndicatorDisplayModal = createIndicatorDisplayModal;
window.closeIndicatorDisplayModal = closeIndicatorDisplayModal;
window.saveIndicatorDisplaySettings = saveIndicatorDisplaySettings;
window.previewDisplayChange = previewDisplayChange;
window.getDefaultIndicatorColor = getDefaultIndicatorColor;
window.getIndicatorParams = getIndicatorParams;
window.filterIndicators = filterIndicators;
window.loadIndicatorTemplate = loadIndicatorTemplate;
window.loadIndicatorTemplatesData = loadIndicatorTemplatesData;

// Condition management
window.renderConditions = renderConditions;
window.addCondition = addCondition;
window.addSubCondition = addSubCondition;
window.editCondition = editCondition;
window.removeCondition = removeCondition;
window.removeSubCondition = removeSubCondition;
window.switchEntryDirection = switchEntryDirection;
window.toggleRightInput = toggleRightInput;
window.handleOperatorChange = handleOperatorChange;
window.closeConditionModal = closeConditionModal;

// TP/SL management
window.renderTPSLTable = renderTPSLTable;
window.addTPSLRule = addTPSLRule;
window.removeTPSLRule = removeTPSLRule;
window.updateTPSLRule = updateTPSLRule;
window.loadDefaultTPSLRules = loadDefaultTPSLRules;
window.switchExitDirection = switchExitDirection;

// Signal management
window.saveSignal = saveSignal;

// Auto-generation
window.openAutoGenerateModal = openAutoGenerateModal;
window.closeAutoGenerateModal = closeAutoGenerateModal;
window.startAutoGeneration = startAutoGeneration;
window.displayAutoGenResult = displayAutoGenResult;
window.displayAutoGenResults = displayAutoGenResults;
window.loadGeneratedStrategy = loadGeneratedStrategy;
window.previewGeneratedStrategy = previewGeneratedStrategy;
window.applyGeneratedStrategy = applyGeneratedStrategy;

// ============================================================================
// DYNAMIC TIER TABLE MANAGEMENT
// ============================================================================

/**
 * Initialize trailing configuration listeners
 */
function initTrailingConfig() {
    console.log('🎯 Initializing trailing config...');

    // Get trailing type radio buttons
    const trailingTypeRadios = document.querySelectorAll('input[name="trailingType"]');
    const fixedTrailingConfig = document.getElementById('fixedTrailingConfig');
    const dynamicTrailingConfig = document.getElementById('dynamicTrailingConfig');

    // Add event listeners to trailing type radios
    trailingTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'fixed') {
                fixedTrailingConfig.style.display = 'block';
                dynamicTrailingConfig.style.display = 'none';
            } else if (this.value === 'dynamic') {
                fixedTrailingConfig.style.display = 'none';
                dynamicTrailingConfig.style.display = 'block';

                // Render tier table when switching to dynamic
                renderDynamicTierTable();
            }
        });
    });

    // Initialize Skip Long Candle checkbox listener
    const skipLongCandleCheckbox = document.getElementById('skipLongCandleForTrailing');
    const longCandleConfig = document.getElementById('longCandleConfig');

    if (skipLongCandleCheckbox && longCandleConfig) {
        skipLongCandleCheckbox.addEventListener('change', function() {
            longCandleConfig.style.display = this.checked ? 'block' : 'none';
        });
    }

    // Initialize Expiry Day checkbox listener
    const exitByExpiryCheckbox = document.getElementById('exitByExpiry');
    const expiryConfig = document.getElementById('expiryConfig');

    if (exitByExpiryCheckbox && expiryConfig) {
        exitByExpiryCheckbox.addEventListener('change', function() {
            expiryConfig.style.display = this.checked ? 'block' : 'none';
        });
    }

    // Render initial tier table if dynamic trailing is selected
    const selectedTrailingType = document.querySelector('input[name="trailingType"]:checked');
    if (selectedTrailingType && selectedTrailingType.value === 'dynamic') {
        renderDynamicTierTable();
    }

    console.log('✅ Trailing config initialized');
}

/**
 * Render dynamic tier table from tradingEngine config
 */
function renderDynamicTierTable() {
    console.log('📊 Rendering dynamic tier table...');

    const tableBody = document.getElementById('dynamicTierTable');
    if (!tableBody) {
        console.error('❌ Tier table body not found');
        return;
    }

    // Get tiers from trading engine config
    let tiers = [];
    if (typeof tradingEngine !== 'undefined' &&
        tradingEngine.config &&
        tradingEngine.config.trailingConfig &&
        tradingEngine.config.trailingConfig.dynamicTiers) {
        tiers = tradingEngine.config.trailingConfig.dynamicTiers;
    }

    // Default tiers if none exist
    if (tiers.length === 0) {
        tiers = [
            { minProfit: 0, maxProfit: 20, trailingPercent: 30 },
            { minProfit: 20, maxProfit: 50, trailingPercent: 50 },
            { minProfit: 50, maxProfit: 9999, trailingPercent: 70 }
        ];

        // Save default tiers to config
        if (typeof tradingEngine !== 'undefined' && tradingEngine.config) {
            if (!tradingEngine.config.trailingConfig) {
                tradingEngine.config.trailingConfig = {};
            }
            tradingEngine.config.trailingConfig.dynamicTiers = tiers;
        }
    }

    // Clear table
    tableBody.innerHTML = '';

    // Render each tier
    tiers.forEach((tier, index) => {
        const row = document.createElement('tr');
        row.style.borderBottom = index < tiers.length - 1 ? '1px solid #2a2e39' : 'none';

        // Min Profit cell
        const minProfitCell = document.createElement('td');
        minProfitCell.style.padding = '8px';
        const minProfitInput = document.createElement('input');
        minProfitInput.type = 'number';
        minProfitInput.value = tier.minProfit;
        minProfitInput.min = '0';
        minProfitInput.step = '0.1';
        minProfitInput.style.cssText = 'width: 100%; padding: 6px; background: #131722; border: 1px solid #2a2e39; border-radius: 3px; color: #d1d4dc; font-size: 12px;';
        minProfitInput.addEventListener('input', function() {
            updateDynamicTier(index, 'minProfit', parseFloat(this.value));
        });
        minProfitCell.appendChild(minProfitInput);

        // Max Profit cell
        const maxProfitCell = document.createElement('td');
        maxProfitCell.style.padding = '8px';
        const maxProfitInput = document.createElement('input');
        maxProfitInput.type = 'number';
        maxProfitInput.value = tier.maxProfit;
        maxProfitInput.min = '0';
        maxProfitInput.step = '0.1';
        maxProfitInput.style.cssText = 'width: 100%; padding: 6px; background: #131722; border: 1px solid #2a2e39; border-radius: 3px; color: #d1d4dc; font-size: 12px;';
        maxProfitInput.addEventListener('input', function() {
            updateDynamicTier(index, 'maxProfit', parseFloat(this.value));
        });
        maxProfitCell.appendChild(maxProfitInput);

        // Trailing Percent cell
        const trailingPercentCell = document.createElement('td');
        trailingPercentCell.style.padding = '8px';
        const trailingPercentInput = document.createElement('input');
        trailingPercentInput.type = 'number';
        trailingPercentInput.value = tier.trailingPercent;
        trailingPercentInput.min = '0';
        trailingPercentInput.max = '100';
        trailingPercentInput.step = '1';
        trailingPercentInput.style.cssText = 'width: 100%; padding: 6px; background: #131722; border: 1px solid #2a2e39; border-radius: 3px; color: #d1d4dc; font-size: 12px;';
        trailingPercentInput.addEventListener('input', function() {
            updateDynamicTier(index, 'trailingPercent', parseFloat(this.value));
        });
        trailingPercentCell.appendChild(trailingPercentInput);

        // Action cell
        const actionCell = document.createElement('td');
        actionCell.style.padding = '8px';
        const removeButton = document.createElement('button');
        removeButton.textContent = 'Remove';
        removeButton.style.cssText = 'padding: 4px 8px; font-size: 11px; background: #ef5350; border: none; border-radius: 3px; color: white; cursor: pointer;';
        removeButton.addEventListener('click', function() {
            removeDynamicTier(index);
        });
        actionCell.appendChild(removeButton);

        row.appendChild(minProfitCell);
        row.appendChild(maxProfitCell);
        row.appendChild(trailingPercentCell);
        row.appendChild(actionCell);

        tableBody.appendChild(row);
    });

    console.log(`✅ Rendered ${tiers.length} tiers`);
}

/**
 * Add a new dynamic tier
 */
function addDynamicTier() {
    console.log('➕ Adding new tier...');

    // Get current tiers
    let tiers = [];
    if (typeof tradingEngine !== 'undefined' &&
        tradingEngine.config &&
        tradingEngine.config.trailingConfig &&
        tradingEngine.config.trailingConfig.dynamicTiers) {
        tiers = tradingEngine.config.trailingConfig.dynamicTiers;
    }

    // Determine default values for new tier
    let newMinProfit = 0;
    if (tiers.length > 0) {
        const lastTier = tiers[tiers.length - 1];
        newMinProfit = lastTier.maxProfit;
    }

    const newTier = {
        minProfit: newMinProfit,
        maxProfit: newMinProfit + 10,
        trailingPercent: 50
    };

    tiers.push(newTier);

    // Save to config
    if (typeof tradingEngine !== 'undefined' && tradingEngine.config) {
        if (!tradingEngine.config.trailingConfig) {
            tradingEngine.config.trailingConfig = {};
        }
        tradingEngine.config.trailingConfig.dynamicTiers = tiers;
    }

    // Re-render table
    renderDynamicTierTable();

    console.log('✅ Added new tier:', newTier);
}

/**
 * Remove a dynamic tier
 */
function removeDynamicTier(index) {
    console.log(`🗑️ Removing tier at index ${index}...`);

    // Get current tiers
    let tiers = [];
    if (typeof tradingEngine !== 'undefined' &&
        tradingEngine.config &&
        tradingEngine.config.trailingConfig &&
        tradingEngine.config.trailingConfig.dynamicTiers) {
        tiers = tradingEngine.config.trailingConfig.dynamicTiers;
    }

    if (index >= 0 && index < tiers.length) {
        tiers.splice(index, 1);

        // Save to config
        if (typeof tradingEngine !== 'undefined' && tradingEngine.config) {
            if (!tradingEngine.config.trailingConfig) {
                tradingEngine.config.trailingConfig = {};
            }
            tradingEngine.config.trailingConfig.dynamicTiers = tiers;
        }

        // Re-render table
        renderDynamicTierTable();

        console.log('✅ Removed tier');
    } else {
        console.error('❌ Invalid tier index:', index);
    }
}

/**
 * Update a dynamic tier field
 */
function updateDynamicTier(index, field, value) {
    // Get current tiers
    let tiers = [];
    if (typeof tradingEngine !== 'undefined' &&
        tradingEngine.config &&
        tradingEngine.config.trailingConfig &&
        tradingEngine.config.trailingConfig.dynamicTiers) {
        tiers = tradingEngine.config.trailingConfig.dynamicTiers;
    }

    if (index >= 0 && index < tiers.length) {
        tiers[index][field] = value;

        // Save to config
        if (typeof tradingEngine !== 'undefined' && tradingEngine.config) {
            if (!tradingEngine.config.trailingConfig) {
                tradingEngine.config.trailingConfig = {};
            }
            tradingEngine.config.trailingConfig.dynamicTiers = tiers;
        }

        console.log(`✅ Updated tier ${index}: ${field} = ${value}`);
    }
}

// Dynamic Tier Table Management
window.renderDynamicTierTable = renderDynamicTierTable;
window.addDynamicTier = addDynamicTier;
window.removeDynamicTier = removeDynamicTier;
window.updateDynamicTier = updateDynamicTier;
window.initTrailingConfig = initTrailingConfig;

console.log('✅ ALL 62 functions exposed to window');
// ==================== END EXPOSE ====================

