/**
 * Trading Engine Core
 * Heart of the trading system - manages positions and execution logic
 */

// Global state
const tradingEngine = {
    // Configuration
    config: {
        entryAfterCandle: [1], // Array: can include 1 and/or 2
        positionMode: 'long_only', // 'long_only', 'short_only', 'long_and_short'
        entryPriceType: 'C', // 'O', 'H', 'L', 'C'
        exitTiming: 'same_candle', // 'same_candle' or 'after_1_candle'

        // Exit methods
        exitMethods: {
            bySignal: true,    // Exit when opposite signal appears
            byTP: false,       // Exit by Take Profit
            bySL: false,       // Exit by Stop Loss
            byTrailing: false, // Exit by Trailing Stop
            byExpiry: false    // Exit on Expiry Day
        },

        // Profit-based exit config
        profitConfig: {
            tpBuyPoints: 10,
            tpShortPoints: 10,
            stopLossPoints: 20,       // SL for LONG
            slShortPoints: 20         // SL for SHORT
        },

        // Trailing stop config
        trailingConfig: {
            type: 'fixed',  // 'fixed' or 'dynamic'

            // Fixed trailing (original)
            fixedBuyPoints: 5,
            fixedShortPoints: 5,

            // Dynamic tiered trailing
            dynamicTiers: [
                { minProfit: 0,  maxProfit: 20,  trailingPercent: 30 },
                { minProfit: 20, maxProfit: 50,  trailingPercent: 50 },
                { minProfit: 50, maxProfit: 9999, trailingPercent: 70 }
            ],

            // Skip long candle (applies to both fixed and dynamic)
            skipLongCandle: false,
            longCandleSize: 50
        },

        // Expiry exit config
        expiryConfig: {
            dates: [],        // Array of Date objects (parsed from DDMMYY format)
            time: '143000'    // HHMMSS format
        },

        // Base time for HHV/LLV indicators (timestamp or null for full data)
        baseTime: null
    },

    // Position state
    positions: {
        long: 0,
        short: 0,
        currentStatus: 'FLAT', // 'FLAT', 'LONG', 'SHORT'
        entryPrice: null,
        entryTime: null,
        hhvSinceEntry: null,   // Highest high since entry (for long trailing)
        llvSinceEntry: null,   // Lowest low since entry (for short trailing)
        hhvPrevious: null,     // HHV from previous candle (for no-repaint trailing)
        llvPrevious: null      // LLV from previous candle (for no-repaint trailing)
    },

    // Pending signals waiting for entry
    pendingSignals: [],

    // Pending exits waiting for execution
    pendingExits: [],

    // Signal history
    signalHistory: [],

    // Position entry markers for chart
    positionEntries: []
};

/**
 * Parse expiry date from DDMMYY format to Date object
 * @param {string} dateStr - Date string in DDMMYY format
 * @returns {Date|null} - Date object or null if invalid
 */
function parseExpiryDate(dateStr) {
    if (!dateStr || dateStr.length !== 6) return null;

    const day = parseInt(dateStr.substring(0, 2));
    const month = parseInt(dateStr.substring(2, 4)) - 1; // JavaScript months are 0-indexed
    const year = 2000 + parseInt(dateStr.substring(4, 6));

    const date = new Date(year, month, day);

    // Validate date
    if (isNaN(date.getTime())) return null;
    if (date.getDate() !== day || date.getMonth() !== month) return null;

    return date;
}

/**
 * Parse expiry time from HHMMSS format to comparable number
 * @param {string} timeStr - Time string in HHMMSS format
 * @returns {number} - Time as number (HHMMSS)
 */
function parseExpiryTime(timeStr) {
    if (!timeStr || timeStr.length !== 6) return null;
    return parseInt(timeStr);
}

/**
 * Calculate dynamic trailing based on profit and tiers
 * @param {number} entryPrice - Entry price
 * @param {number} hhvOrLlv - HHV (for LONG) or LLV (for SHORT)
 * @param {Array} tiers - Array of tier config objects
 * @param {string} side - 'LONG' or 'SHORT'
 * @returns {Object} - {trailingLine, trailingPoints, maxProfit, tier}
 */
function calculateDynamicTrailing(entryPrice, hhvOrLlv, tiers, side) {
    // Calculate max profit
    const maxProfit = side === 'LONG'
        ? (hhvOrLlv - entryPrice)   // LONG: HHV - Entry
        : (entryPrice - hhvOrLlv);   // SHORT: Entry - LLV

    // Find appropriate tier
    const tier = tiers.find(t =>
        maxProfit >= t.minProfit && maxProfit < t.maxProfit
    );

    if (!tier || maxProfit <= 0) {
        return { trailingLine: entryPrice, trailingPoints: 0, maxProfit, tier: null };
    }

    // Calculate trailing points based on percentage
    const trailingPoints = maxProfit * (tier.trailingPercent / 100);

    // Calculate trailing line
    const trailingLine = side === 'LONG'
        ? entryPrice + (maxProfit - trailingPoints)  // LONG: Entry + (Profit - Trailing)
        : entryPrice - (maxProfit - trailingPoints);  // SHORT: Entry - (Profit - Trailing)

    return { trailingLine, trailingPoints, maxProfit, tier };
}

/**
 * Initialize Trading Engine
 */
function initTradingEngine() {
    console.log('⚙️ Initializing Trading Engine Core...');

    // Initialize toggle states (default: all ON)
    window.showPositionPanel = true;
    window.showBuySignals = true;
    window.showShortSignals = true;

    // Update button states
    const posBtn = document.getElementById('togglePositionPanel');
    const buyBtn = document.getElementById('toggleBuySignals');
    const shortBtn = document.getElementById('toggleShortSignals');

    if (posBtn) posBtn.style.background = '#2962ff';
    if (buyBtn) buyBtn.style.opacity = '1';
    if (shortBtn) shortBtn.style.opacity = '1';

    // Load config from UI
    loadEngineConfig();

    // Set up event listeners
    setupEngineListeners();

    // Update position display
    updatePositionDisplay();

    // Check initial state of Exit by Signal
    const exitBySignal = document.getElementById('exitBySignal');
    const exitTimingSameCandle = document.getElementById('exitTimingSameCandle');
    const exitTimingAfter1 = document.querySelector('input[name="exitTiming"][value="after_1_candle"]');

    if (exitBySignal && exitBySignal.checked) {
        // Hide same candle option if Exit by Signal is checked
        if (exitTimingSameCandle) {
            exitTimingSameCandle.style.display = 'none';
        }
        // Force select after 1 candle
        if (exitTimingAfter1) {
            exitTimingAfter1.checked = true;
            tradingEngine.config.exitTiming = 'after_1_candle';
        }
    }

    console.log('✅ Trading Engine initialized');
    console.log('📊 Config:', tradingEngine.config);
    console.log('🎯 Position:', tradingEngine.positions);
}

/**
 * Load configuration from UI
 */
function loadEngineConfig() {
    // Entry After Candle (checkboxes - can select both 1 and 2)
    const entryAfterArray = [];
    const entryAfter1 = document.getElementById('entryAfter1');
    const entryAfter2 = document.getElementById('entryAfter2');
    if (entryAfter1 && entryAfter1.checked) entryAfterArray.push(1);
    if (entryAfter2 && entryAfter2.checked) entryAfterArray.push(2);
    if (entryAfterArray.length > 0) {
        tradingEngine.config.entryAfterCandle = entryAfterArray;
    }

    // Exit Timing (radio buttons)
    const exitTimingRadio = document.querySelector('input[name="exitTiming"]:checked');
    if (exitTimingRadio) {
        tradingEngine.config.exitTiming = exitTimingRadio.value;
    }

    // Position Mode
    const modeRadio = document.querySelector('input[name="positionMode"]:checked');
    if (modeRadio) {
        tradingEngine.config.positionMode = modeRadio.value;
    }

    // Entry Price Type
    const priceRadio = document.querySelector('input[name="entryPriceType"]:checked');
    if (priceRadio) {
        tradingEngine.config.entryPriceType = priceRadio.value;
    }

    // Exit Methods (individual checkboxes)
    const exitBySignal = document.getElementById('exitBySignal');
    if (exitBySignal) {
        tradingEngine.config.exitMethods.bySignal = exitBySignal.checked;
    }

    const exitByTP = document.getElementById('exitByTP');
    if (exitByTP) {
        tradingEngine.config.exitMethods.byTP = exitByTP.checked;
    }

    const exitBySL = document.getElementById('exitBySL');
    if (exitBySL) {
        tradingEngine.config.exitMethods.bySL = exitBySL.checked;
    }

    const exitByTrailing = document.getElementById('exitByTrailing');
    if (exitByTrailing) {
        tradingEngine.config.exitMethods.byTrailing = exitByTrailing.checked;
    }

    const exitByExpiry = document.getElementById('exitByExpiry');
    if (exitByExpiry) {
        tradingEngine.config.exitMethods.byExpiry = exitByExpiry.checked;
    }

    // Expiry Config (if exitByExpiry is enabled)
    if (tradingEngine.config.exitMethods.byExpiry) {
        const expiryDates = document.getElementById('expiryDates');
        const expiryTime = document.getElementById('expiryTime');

        if (expiryDates && expiryDates.value.trim()) {
            // Parse dates from DDMMYY format
            const dateStrings = expiryDates.value.split(',').map(s => s.trim());
            tradingEngine.config.expiryConfig.dates = dateStrings.map(parseExpiryDate).filter(d => d !== null);
        }

        if (expiryTime && expiryTime.value.trim()) {
            tradingEngine.config.expiryConfig.time = expiryTime.value.trim();
        }
    }

    // Profit Config (TP/SL)
    const anyProfitExit = tradingEngine.config.exitMethods.byTP ||
                          tradingEngine.config.exitMethods.bySL ||
                          tradingEngine.config.exitMethods.byTrailing;

    if (anyProfitExit) {
        const tpBuy = document.getElementById('tpBuyPoints');
        const tpShort = document.getElementById('tpShortPoints');
        const sl = document.getElementById('stopLossPoints');
        const slShort = document.getElementById('slShortPoints');

        if (tpBuy) tradingEngine.config.profitConfig.tpBuyPoints = parseFloat(tpBuy.value);
        if (tpShort) tradingEngine.config.profitConfig.tpShortPoints = parseFloat(tpShort.value);
        if (sl) tradingEngine.config.profitConfig.stopLossPoints = parseFloat(sl.value);
        if (slShort) tradingEngine.config.profitConfig.slShortPoints = parseFloat(slShort.value);
    }

    // Trailing Config (if trailing exit is enabled)
    if (tradingEngine.config.exitMethods.byTrailing) {
        // Trailing type
        const trailingType = document.querySelector('input[name="trailingType"]:checked');
        if (trailingType) {
            tradingEngine.config.trailingConfig.type = trailingType.value;
        }

        // Fixed trailing points
        const fixedBuy = document.getElementById('fixedTrailingBuyPoints');
        const fixedShort = document.getElementById('fixedTrailingShortPoints');
        if (fixedBuy) tradingEngine.config.trailingConfig.fixedBuyPoints = parseFloat(fixedBuy.value);
        if (fixedShort) tradingEngine.config.trailingConfig.fixedShortPoints = parseFloat(fixedShort.value);

        // Dynamic tiers (will be loaded from UI dynamically)
        // For now, keep default tiers in config
    }

    // Skip Long Candle Config (applies to both trailing types)
    const skipLongCandle = document.getElementById('skipLongCandleForTrailing');
    if (skipLongCandle) {
        tradingEngine.config.trailingConfig.skipLongCandle = skipLongCandle.checked;
    }

    if (tradingEngine.config.trailingConfig.skipLongCandle) {
        const longCandleSize = document.getElementById('longCandleSize');
        if (longCandleSize) {
            tradingEngine.config.trailingConfig.longCandleSize = parseFloat(longCandleSize.value);
        }
    }

    console.log('⚙️ Loaded config:', tradingEngine.config);
}

/**
 * Set up event listeners for config changes
 */
function setupEngineListeners() {
    // Entry After Candle checkboxes (can select both 1 and 2)
    const entryAfter1 = document.getElementById('entryAfter1');
    const entryAfter2 = document.getElementById('entryAfter2');

    if (entryAfter1) {
        entryAfter1.addEventListener('change', () => {
            loadEngineConfig();
            console.log('🕐 Entry After Candle updated:', tradingEngine.config.entryAfterCandle);
        });
    }

    if (entryAfter2) {
        entryAfter2.addEventListener('change', () => {
            loadEngineConfig();
            console.log('🕐 Entry After Candle updated:', tradingEngine.config.entryAfterCandle);
        });
    }

    // Exit Timing radio buttons
    document.querySelectorAll('input[name="exitTiming"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            tradingEngine.config.exitTiming = e.target.value;
            console.log('⏱️ Exit Timing changed to:', tradingEngine.config.exitTiming);
        });
    });

    // Position Mode change
    document.querySelectorAll('input[name="positionMode"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            tradingEngine.config.positionMode = e.target.value;
            console.log('📊 Position Mode changed to:', tradingEngine.config.positionMode);
        });
    });

    // Entry Price Type change
    document.querySelectorAll('input[name="entryPriceType"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            tradingEngine.config.entryPriceType = e.target.value;
            console.log('💰 Entry Price Type changed to:', tradingEngine.config.entryPriceType);
        });
    });

    // Exit by Signal checkbox
    const exitBySignal = document.getElementById('exitBySignal');
    if (exitBySignal) {
        exitBySignal.addEventListener('change', (e) => {
            tradingEngine.config.exitMethods.bySignal = e.target.checked;
            console.log('🔄 Exit by Signal:', e.target.checked);

            // If Exit by Signal is checked, hide "Exit in Same Candle" option
            // and force "Exit After 1 Candle"
            const exitTimingSameCandle = document.getElementById('exitTimingSameCandle');
            const exitTimingAfter1 = document.querySelector('input[name="exitTiming"][value="after_1_candle"]');

            if (e.target.checked) {
                // Hide same candle option
                if (exitTimingSameCandle) {
                    exitTimingSameCandle.style.display = 'none';
                }
                // Force select after 1 candle
                if (exitTimingAfter1) {
                    exitTimingAfter1.checked = true;
                    tradingEngine.config.exitTiming = 'after_1_candle';
                }
            } else {
                // Show same candle option again
                if (exitTimingSameCandle) {
                    exitTimingSameCandle.style.display = 'flex';
                }
            }
        });
    }

    // Exit by TP checkbox
    const exitByTP = document.getElementById('exitByTP');
    if (exitByTP) {
        exitByTP.addEventListener('change', (e) => {
            tradingEngine.config.exitMethods.byTP = e.target.checked;
            console.log('✅ Exit by TP:', e.target.checked);
            loadEngineConfig(); // Reload profit config if needed
        });
    }

    // Exit by SL checkbox
    const exitBySL = document.getElementById('exitBySL');
    if (exitBySL) {
        exitBySL.addEventListener('change', (e) => {
            tradingEngine.config.exitMethods.bySL = e.target.checked;
            console.log('🛑 Exit by SL:', e.target.checked);
            loadEngineConfig(); // Reload profit config if needed
        });
    }

    // Exit by Trailing checkbox
    const exitByTrailing = document.getElementById('exitByTrailing');
    if (exitByTrailing) {
        exitByTrailing.addEventListener('change', (e) => {
            tradingEngine.config.exitMethods.byTrailing = e.target.checked;
            console.log('📉 Exit by Trailing:', e.target.checked);
            loadEngineConfig(); // Reload profit config if needed
        });
    }

    // Exit by Expiry checkbox
    const exitByExpiry = document.getElementById('exitByExpiry');
    if (exitByExpiry) {
        exitByExpiry.addEventListener('change', (e) => {
            tradingEngine.config.exitMethods.byExpiry = e.target.checked;
            console.log('📅 Exit by Expiry:', e.target.checked);

            // Toggle expiry config section visibility
            const expiryConfigSection = document.getElementById('expiryConfig');
            if (expiryConfigSection) {
                expiryConfigSection.style.display = e.target.checked ? 'block' : 'none';
            }

            // Load expiry config values
            if (e.target.checked) {
                loadEngineConfig();
            }
        });
    }

    // Expiry config value changes
    const expiryInputs = ['expiryDates', 'expiryTime'];
    expiryInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('change', () => {
                loadEngineConfig();
                console.log('📅 Expiry config updated:', tradingEngine.config.expiryConfig);
            });
        }
    });

    // Profit config value changes
    const profitInputs = ['tpBuyPoints', 'tpShortPoints', 'stopLossPoints', 'slShortPoints', 'trailingBuyPoints', 'trailingShortPoints'];
    profitInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('change', () => {
                loadEngineConfig();
                console.log('💹 Profit config updated');
            });
        }
    });

    // Trailing Type radio buttons
    document.querySelectorAll('input[name="trailingType"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            tradingEngine.config.trailingConfig.type = e.target.value;
            console.log('⚙️ Trailing Type changed to:', e.target.value);

            // Toggle visibility of Fixed/Dynamic config sections
            const fixedSection = document.getElementById('fixedTrailingConfig');
            const dynamicSection = document.getElementById('dynamicTrailingConfig');

            if (fixedSection) {
                fixedSection.style.display = e.target.value === 'fixed' ? 'block' : 'none';
            }
            if (dynamicSection) {
                dynamicSection.style.display = e.target.value === 'dynamic' ? 'block' : 'none';
            }

            loadEngineConfig();
        });
    });

    // Fixed trailing points inputs
    const fixedTrailingInputs = ['fixedTrailingBuyPoints', 'fixedTrailingShortPoints'];
    fixedTrailingInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('change', () => {
                loadEngineConfig();
                console.log('📊 Fixed Trailing Points updated');
            });
        }
    });

    // Skip Long Candle Options
    const skipLongCandleCheckbox = document.getElementById('skipLongCandleForTrailing');
    if (skipLongCandleCheckbox) {
        skipLongCandleCheckbox.addEventListener('change', (e) => {
            tradingEngine.config.trailingConfig.skipLongCandle = e.target.checked;
            console.log('📏 Skip Long Candle for Trailing:', e.target.checked);

            // Toggle long candle config section visibility
            const longCandleConfigSection = document.getElementById('longCandleConfig');
            if (longCandleConfigSection) {
                longCandleConfigSection.style.display = e.target.checked ? 'block' : 'none';
            }

            // Load config values if enabled
            if (e.target.checked) {
                loadEngineConfig();
            }
        });
    }

    // Long Candle Size input
    const longCandleSizeInput = document.getElementById('longCandleSize');
    if (longCandleSizeInput) {
        longCandleSizeInput.addEventListener('change', () => {
            loadEngineConfig();
            console.log('📏 Long Candle Size updated:', tradingEngine.config.trailingConfig.longCandleSize);
        });
    }
}

/**
 * Check if can open position based on current state and mode
 * @param {string} side - 'LONG' or 'SHORT'
 * @returns {boolean}
 */
function canOpenPosition(side) {
    const { positionMode } = tradingEngine.config;
    const { currentStatus } = tradingEngine.positions;

    // If not flat and mode is long_and_short, cannot open
    if (positionMode === 'long_and_short' && currentStatus !== 'FLAT') {
        console.log('❌ Cannot open', side, '- position not FLAT');
        return false;
    }

    // If trying to open long but mode is short_only
    if (side === 'LONG' && positionMode === 'short_only') {
        console.log('❌ Cannot open LONG - mode is short_only');
        return false;
    }

    // If trying to open short but mode is long_only
    if (side === 'SHORT' && positionMode === 'long_only') {
        console.log('❌ Cannot open SHORT - mode is long_only');
        return false;
    }

    return true;
}

/**
 * Open position
 * @param {string} side - 'LONG' or 'SHORT'
 * @param {number} price - Entry price
 * @param {string} time - Entry time
 */
function openPosition(side, price, time) {
    if (!canOpenPosition(side)) {
        return false;
    }

    if (side === 'LONG') {
        tradingEngine.positions.long++;
        tradingEngine.positions.currentStatus = 'LONG';
    } else if (side === 'SHORT') {
        tradingEngine.positions.short++;
        tradingEngine.positions.currentStatus = 'SHORT';
    }

    // Store entry price and time for profit-based exits
    tradingEngine.positions.entryPrice = price;
    tradingEngine.positions.entryTime = time;

    // Reset HHV/LLV for trailing stop
    tradingEngine.positions.hhvSinceEntry = price; // Start with entry price
    tradingEngine.positions.llvSinceEntry = price; // Start with entry price
    tradingEngine.positions.hhvPrevious = price;   // Initialize previous HHV
    tradingEngine.positions.llvPrevious = price;   // Initialize previous LLV

    // Track entry for chart markers
    tradingEngine.positionEntries.push({
        time: time,
        price: price,
        side: side
    });

    // Update display
    updatePositionDisplay();

    // Log
    console.log(`✅ Opened ${side} position at ${price} @ ${time}`);

    // Create position for marker display
    const position = {
        id: `pos_${Date.now()}`,
        side: side,
        entryPrice: price,
        entryTime: time,
        status: 'Open'
    };

    // Add position marker if function exists
    if (typeof addPositionMarker === 'function') {
        addPositionMarker(position);
    }

    return true;
}

/**
 * Close position
 * @param {string} side - 'LONG' or 'SHORT'
 */
function closePosition(side) {
    if (side === 'LONG' && tradingEngine.positions.long > 0) {
        tradingEngine.positions.long--;
    } else if (side === 'SHORT' && tradingEngine.positions.short > 0) {
        tradingEngine.positions.short--;
    }

    // Update status
    if (tradingEngine.positions.long === 0 && tradingEngine.positions.short === 0) {
        tradingEngine.positions.currentStatus = 'FLAT';

        // Reset entry price and time
        tradingEngine.positions.entryPrice = null;
        tradingEngine.positions.entryTime = null;

        // Reset HHV/LLV
        tradingEngine.positions.hhvSinceEntry = null;
        tradingEngine.positions.llvSinceEntry = null;
        tradingEngine.positions.hhvPrevious = null;
        tradingEngine.positions.llvPrevious = null;
    }

    // Update display
    updatePositionDisplay();

    console.log(`✅ Closed ${side} position`);
}

/**
 * Update position display on UI
 */
function updatePositionDisplay() {
    // Update counts
    const longCount = document.getElementById('longPositionCount');
    const shortCount = document.getElementById('shortPositionCount');
    const status = document.getElementById('currentPositionStatus');

    if (longCount) {
        longCount.textContent = tradingEngine.positions.long;
    }

    if (shortCount) {
        shortCount.textContent = tradingEngine.positions.short;
    }

    if (status) {
        status.textContent = tradingEngine.positions.currentStatus;

        // Update color based on status
        if (tradingEngine.positions.currentStatus === 'LONG') {
            status.style.color = '#26a69a';
        } else if (tradingEngine.positions.currentStatus === 'SHORT') {
            status.style.color = '#ef5350';
        } else {
            status.style.color = '#787b86';
        }
    }

    // Update chart OHLCV display
    updateChartPositionDisplay();

    // Update position overlay on chart (if function exists)
    if (typeof updatePositionOverlay === 'function') {
        updatePositionOverlay();
    }
}

/**
 * Update chart position display (near OHLCV)
 */
function updateChartPositionDisplay() {
    const chartStatus = document.getElementById('chartPositionStatus');

    if (chartStatus) {
        chartStatus.textContent = tradingEngine.positions.currentStatus;

        // Update color based on status
        if (tradingEngine.positions.currentStatus === 'LONG') {
            chartStatus.style.color = '#26a69a';
        } else if (tradingEngine.positions.currentStatus === 'SHORT') {
            chartStatus.style.color = '#ef5350';
        } else {
            chartStatus.style.color = '#787b86';
        }
    }
}

/**
 * Render position entry markers on chart
 */
function renderPositionMarkers() {
    if (!window.candlestickSeries) {
        console.warn('⚠️ Candlestick series not available for position markers');
        return;
    }

    if (!window.showPositionPanel) {
        // Position panel toggle is off - don't show markers
        return;
    }

    try {
        const markers = [];

        // Add entry markers
        tradingEngine.positionEntries.forEach(entry => {
            const date = new Date(entry.time * 1000);
            const timeStr = date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });

            if (entry.side === 'LONG') {
                markers.push({
                    time: entry.time,
                    position: 'belowBar',
                    color: '#26a69a',
                    shape: 'circle',
                    text: `LONG\n${entry.price.toFixed(2)} ${timeStr}`,
                    size: 2
                });
            } else if (entry.side === 'SHORT') {
                markers.push({
                    time: entry.time,
                    position: 'aboveBar',
                    color: '#ef5350',
                    shape: 'circle',
                    text: `SHORT\n${entry.price.toFixed(2)} ${timeStr}`,
                    size: 2
                });
            }
        });

        console.log(`📍 Rendering ${markers.length} position entry markers`);

        // Note: We need to merge these with existing signal markers
        // This will be handled by updateChartMarkers function
        window.positionMarkers = markers;
        updateChartMarkers();

    } catch (error) {
        console.error('❌ Error rendering position markers:', error);
    }
}

/**
 * Toggle position panel visibility
 */
function togglePositionPanel() {
    window.showPositionPanel = !window.showPositionPanel;
    const btn = document.getElementById('togglePositionPanel');

    if (window.showPositionPanel) {
        btn.style.background = '#2962ff';
        console.log('✅ Position Panel ON');
    } else {
        btn.style.background = '';
        console.log('❌ Position Panel OFF');
    }

    renderPositionMarkers();
}

/**
 * Toggle buy signals visibility
 */
function toggleBuySignals() {
    window.showBuySignals = !window.showBuySignals;
    const btn = document.getElementById('toggleBuySignals');

    if (window.showBuySignals) {
        btn.style.opacity = '1';
        console.log('✅ Buy Signals ON');
    } else {
        btn.style.opacity = '0.4';
        console.log('❌ Buy Signals OFF');
    }

    // Refresh markers on chart
    if (typeof updateChartMarkers === 'function') {
        updateChartMarkers();
    }
}

/**
 * Toggle short signals visibility
 */
function toggleShortSignals() {
    window.showShortSignals = !window.showShortSignals;
    const btn = document.getElementById('toggleShortSignals');

    if (window.showShortSignals) {
        btn.style.opacity = '1';
        console.log('✅ Short Signals ON');
    } else {
        btn.style.opacity = '0.4';
        console.log('❌ Short Signals OFF');
    }

    // Refresh markers on chart
    if (typeof updateChartMarkers === 'function') {
        updateChartMarkers();
    }
}

/**
 * Process signal and add to pending queue
 * @param {string} signalType - 'BUY' or 'SELL'
 * @param {number} candleIndex - Index of signal candle
 */
function processSignal(signalType, candleIndex) {
    const entryAfterArray = tradingEngine.config.entryAfterCandle;

    // Handle both array and single value for backward compatibility
    const delays = Array.isArray(entryAfterArray) ? entryAfterArray : [entryAfterArray];

    // Create pending signal for each selected delay
    delays.forEach(delay => {
        const entryCandle = candleIndex + delay;

        tradingEngine.pendingSignals.push({
            type: signalType,
            signalCandle: candleIndex,
            entryCandle: entryCandle,
            delay: delay,
            status: 'pending'
        });

        console.log(`📝 Signal ${signalType} at candle ${candleIndex}, will enter at candle ${entryCandle} (delay: ${delay})`);
    });
}

/**
 * Get entry price based on config and candle data
 * @param {Object} candleData - Candle data {open, high, low, close}
 * @returns {number}
 */
function getEntryPrice(candleData) {
    const priceType = tradingEngine.config.entryPriceType;

    switch(priceType) {
        case 'O':
            return candleData.open;
        case 'H':
            return candleData.high;
        case 'L':
            return candleData.low;
        case 'C':
        default:
            return candleData.close;
    }
}

/**
 * Execute pending signals at current candle
 * @param {number} currentCandleIndex
 * @param {Object} candleData - {open, high, low, close, time}
 */
function executePendingSignals(currentCandleIndex, candleData) {
    tradingEngine.pendingSignals.forEach((signal, index) => {
        if (signal.entryCandle === currentCandleIndex && signal.status === 'pending') {
            const side = signal.type === 'BUY' ? 'LONG' : 'SHORT';
            const entryPrice = getEntryPrice(candleData);
            const entryTime = candleData.time || new Date().toLocaleTimeString('vi-VN');

            if (openPosition(side, entryPrice, entryTime)) {
                signal.status = 'executed';
                signal.executedPrice = entryPrice;
                signal.executedTime = entryTime;
                tradingEngine.signalHistory.push(signal);
            } else {
                signal.status = 'rejected';
            }
        }
    });

    // Clean up executed/rejected signals
    tradingEngine.pendingSignals = tradingEngine.pendingSignals.filter(s => s.status === 'pending');
}

/**
 * Process exit signal and add to pending queue
 * @param {string} exitType - 'SELL' or 'COVER'
 * @param {number} candleIndex - Index of exit signal candle
 */
function processExitSignal(exitType, candleIndex) {
    const exitTiming = tradingEngine.config.exitTiming;
    const exitCandle = exitTiming === 'same_candle' ? candleIndex : candleIndex + 1;

    tradingEngine.pendingExits.push({
        type: exitType,
        signalCandle: candleIndex,
        exitCandle: exitCandle,
        status: 'pending'
    });

    console.log(`📝 Exit ${exitType} at candle ${candleIndex}, will exit at candle ${exitCandle}`);
}

/**
 * Execute pending exits at current candle
 * @param {number} currentCandleIndex
 * @param {Object} candleData - {open, high, low, close, time}
 */
function executePendingExits(currentCandleIndex, candleData) {
    tradingEngine.pendingExits.forEach((exit, index) => {
        if (exit.exitCandle === currentCandleIndex && exit.status === 'pending') {
            const side = exit.type === 'SELL' ? 'LONG' : 'SHORT';
            const exitPrice = getEntryPrice(candleData);
            const exitTime = candleData.time || new Date().toLocaleTimeString('vi-VN');

            closePosition(side);
            exit.status = 'executed';
            exit.executedPrice = exitPrice;
            exit.executedTime = exitTime;

            console.log(`✅ Executed ${exit.type} at ${exitPrice} @ ${exitTime}`);
        }
    });

    // Clean up executed exits
    tradingEngine.pendingExits = tradingEngine.pendingExits.filter(e => e.status === 'pending');
}

/**
 * Check and execute profit-based exits (TP/SL/Trailing)
 * @param {Object} candle - Current candle {open, high, low, close, time}
 * @param {number} currentIndex - Current candle index
 */
function checkProfitExit(candle, currentIndex) {
    const pos = tradingEngine.positions;
    const profitCfg = tradingEngine.config.profitConfig;
    const exitMethods = tradingEngine.config.exitMethods;
    const trailingCfg = tradingEngine.config.trailingConfig;

    // Skip if no profit-based exit methods are enabled
    if (!exitMethods.byTP && !exitMethods.bySL && !exitMethods.byTrailing) return;

    if (pos.currentStatus === 'FLAT' || pos.entryPrice === null) return;

    // Check if this is a "long candle" (for skip option)
    const candleSize = candle.high - candle.low;
    const isLongCandle = trailingCfg.skipLongCandle && (candleSize >= trailingCfg.longCandleSize);

    if (pos.currentStatus === 'LONG') {
        // Save previous HHV BEFORE updating (for no-repaint trailing)
        pos.hhvPrevious = pos.hhvSinceEntry;

        // Update HHV since entry (skip if long candle and option enabled)
        if (!isLongCandle) {
            if (pos.hhvSinceEntry === null || candle.high > pos.hhvSinceEntry) {
                pos.hhvSinceEntry = candle.high;
            }
        } else {
            console.log(`📏 Skipped HHV update - Long candle detected (size: ${candleSize.toFixed(2)})`);
        }

        // Check TP (High touches TP line) - only if enabled
        if (exitMethods.byTP) {
            const tpLine = pos.entryPrice + profitCfg.tpBuyPoints;
            if (candle.high >= tpLine) {
                closePosition('LONG');
                console.log(`✅ LONG closed by TP at ${tpLine} (Entry: ${pos.entryPrice})`);
                return;
            }
        }

        // Check SL (Low touches SL line) - only if enabled
        if (exitMethods.bySL) {
            const slLine = pos.entryPrice - profitCfg.stopLossPoints;
            if (candle.low <= slLine) {
                closePosition('LONG');
                console.log(`🛑 LONG closed by SL at ${slLine} (Entry: ${pos.entryPrice})`);
                return;
            }
        }

        // Check Trailing (Low touches trailing line from HHV) - only if enabled
        if (exitMethods.byTrailing) {
            // Use previous HHV for trailing line (no-repaint)
            const hhvForTrailing = pos.hhvPrevious !== null ? pos.hhvPrevious : pos.hhvSinceEntry;

            let trailingLine;
            let trailingInfo;

            if (trailingCfg.type === 'dynamic') {
                // Dynamic trailing based on profit tiers
                const result = calculateDynamicTrailing(pos.entryPrice, hhvForTrailing, trailingCfg.dynamicTiers, 'LONG');
                trailingLine = result.trailingLine;
                trailingInfo = `Profit: ${result.maxProfit.toFixed(2)}, Tier: ${result.tier ? result.tier.trailingPercent : 0}%`;
            } else {
                // Fixed trailing
                trailingLine = hhvForTrailing - trailingCfg.fixedBuyPoints;
                trailingInfo = `HHV[n-1]: ${hhvForTrailing}`;
            }

            if (candle.low <= trailingLine) {
                closePosition('LONG');
                console.log(`📉 LONG closed by Trailing at ${trailingLine} (${trailingInfo})`);
                return;
            }
        }
    }
    else if (pos.currentStatus === 'SHORT') {
        // Save previous LLV BEFORE updating (for no-repaint trailing)
        pos.llvPrevious = pos.llvSinceEntry;

        // Update LLV since entry (skip if long candle and option enabled)
        if (!isLongCandle) {
            if (pos.llvSinceEntry === null || candle.low < pos.llvSinceEntry) {
                pos.llvSinceEntry = candle.low;
            }
        } else {
            console.log(`📏 Skipped LLV update - Long candle detected (size: ${candleSize.toFixed(2)})`);
        }

        // Check TP (Low touches TP line) - only if enabled
        if (exitMethods.byTP) {
            const tpLine = pos.entryPrice - profitCfg.tpShortPoints;
            if (candle.low <= tpLine) {
                closePosition('SHORT');
                console.log(`✅ SHORT closed by TP at ${tpLine} (Entry: ${pos.entryPrice})`);
                return;
            }
        }

        // Check SL (High touches SL line) - only if enabled
        if (exitMethods.bySL) {
            const slLine = pos.entryPrice + profitCfg.slShortPoints;
            if (candle.high >= slLine) {
                closePosition('SHORT');
                console.log(`🛑 SHORT closed by SL at ${slLine} (Entry: ${pos.entryPrice})`);
                return;
            }
        }

        // Check Trailing (High touches trailing line from LLV) - only if enabled
        if (exitMethods.byTrailing) {
            // Use previous LLV for trailing line (no-repaint)
            const llvForTrailing = pos.llvPrevious !== null ? pos.llvPrevious : pos.llvSinceEntry;

            let trailingLine;
            let trailingInfo;

            if (trailingCfg.type === 'dynamic') {
                // Dynamic trailing based on profit tiers
                const result = calculateDynamicTrailing(pos.entryPrice, llvForTrailing, trailingCfg.dynamicTiers, 'SHORT');
                trailingLine = result.trailingLine;
                trailingInfo = `Profit: ${result.maxProfit.toFixed(2)}, Tier: ${result.tier ? result.tier.trailingPercent : 0}%`;
            } else {
                // Fixed trailing
                trailingLine = llvForTrailing + trailingCfg.fixedShortPoints;
                trailingInfo = `LLV[n-1]: ${llvForTrailing}`;
            }

            if (candle.high >= trailingLine) {
                closePosition('SHORT');
                console.log(`📈 SHORT closed by Trailing at ${trailingLine} (${trailingInfo})`);
                return;
            }
        }
    }
}

/**
 * Check and execute signal-based exits (opposite signal)
 * @param {string} signalType - 'BUY' or 'SHORT'
 * @param {number} currentIndex - Current candle index
 */
function checkSignalExit(signalType, currentIndex) {
    if (!tradingEngine.config.exitMethods.bySignal) return;

    const pos = tradingEngine.positions;

    // Đang LONG mà có SHORT signal → đóng LONG
    if (pos.currentStatus === 'LONG' && signalType === 'SHORT') {
        closePosition('LONG');
        console.log(`🔄 LONG closed by opposite SHORT signal at candle ${currentIndex}`);
    }
    // Đang SHORT mà có BUY signal → đóng SHORT
    else if (pos.currentStatus === 'SHORT' && signalType === 'BUY') {
        closePosition('SHORT');
        console.log(`🔄 SHORT closed by opposite BUY signal at candle ${currentIndex}`);
    }
}

/**
 * Check and execute expiry-based exits
 * @param {Object} candle - Current candle with date/time info
 * @param {number} currentIndex - Current candle index
 */
function checkExpiryExit(candle, currentIndex) {
    if (!tradingEngine.config.exitMethods.byExpiry) return;

    const pos = tradingEngine.positions;
    const expiryCfg = tradingEngine.config.expiryConfig;

    // Skip if no position is open
    if (pos.currentStatus === 'FLAT') return;

    // Skip if no expiry dates configured
    if (!expiryCfg.dates || expiryCfg.dates.length === 0) return;

    // Parse current candle date and time
    // Assume candle has a 'date' property (Date object) or we need to parse from 'time'
    let currentDate;

    if (candle.date instanceof Date) {
        currentDate = candle.date;
    } else if (candle.time) {
        // Try to parse from time string or timestamp
        currentDate = new Date(candle.time);
    } else {
        return; // Cannot determine current date
    }

    // Normalize to date only (remove time component for comparison)
    const currentDateOnly = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate());

    // Check if current date matches any expiry date
    const isExpiryDate = expiryCfg.dates.some(expiryDate => {
        const expiryDateOnly = new Date(expiryDate.getFullYear(), expiryDate.getMonth(), expiryDate.getDate());
        return currentDateOnly.getTime() === expiryDateOnly.getTime();
    });

    if (!isExpiryDate) return;

    // Date matches, now check time
    const currentTime = currentDate.getHours() * 10000 +
                        currentDate.getMinutes() * 100 +
                        currentDate.getSeconds();

    const expiryTime = parseExpiryTime(expiryCfg.time);

    if (currentTime >= expiryTime) {
        // Close all positions
        if (pos.currentStatus === 'LONG') {
            closePosition('LONG');
            console.log(`📅 LONG closed by Expiry at ${currentDate.toLocaleString('vi-VN')} (Expiry: ${expiryCfg.time})`);
        } else if (pos.currentStatus === 'SHORT') {
            closePosition('SHORT');
            console.log(`📅 SHORT closed by Expiry at ${currentDate.toLocaleString('vi-VN')} (Expiry: ${expiryCfg.time})`);
        }
    }
}

/**
 * Get current engine state
 */
function getEngineState() {
    return {
        config: tradingEngine.config,
        positions: tradingEngine.positions,
        pendingSignals: tradingEngine.pendingSignals.length,
        pendingExits: tradingEngine.pendingExits.length,
        signalHistory: tradingEngine.signalHistory.length
    };
}

/**
 * Reset engine state
 */
function resetEngineState() {
    tradingEngine.positions.long = 0;
    tradingEngine.positions.short = 0;
    tradingEngine.positions.currentStatus = 'FLAT';
    tradingEngine.positions.entryPrice = null;
    tradingEngine.positions.entryTime = null;
    tradingEngine.positions.hhvSinceEntry = null;
    tradingEngine.positions.llvSinceEntry = null;
    tradingEngine.positions.hhvPrevious = null;
    tradingEngine.positions.llvPrevious = null;
    tradingEngine.pendingSignals = [];
    tradingEngine.pendingExits = [];
    tradingEngine.signalHistory = [];
    tradingEngine.positionEntries = [];

    updatePositionDisplay();

    console.log('🔄 Engine state reset');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Small delay to ensure all elements are loaded
    setTimeout(() => {
        initTradingEngine();
    }, 500);
});

// Export for testing and integration
if (typeof window !== 'undefined') {
    window.tradingEngine = tradingEngine;
    window.openPosition = openPosition;
    window.closePosition = closePosition;
    window.processSignal = processSignal;
    window.processExitSignal = processExitSignal;
    window.executePendingSignals = executePendingSignals;
    window.executePendingExits = executePendingExits;
    window.checkProfitExit = checkProfitExit;
    window.checkSignalExit = checkSignalExit;
    window.checkExpiryExit = checkExpiryExit;
    window.getEngineState = getEngineState;
    window.resetEngineState = resetEngineState;
}
