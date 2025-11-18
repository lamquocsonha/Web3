/**
 * Workspace - Common functions for Strategy/Backtest/Optimize
 * VERSION: 17.7
 */

console.log('🚀 workspace.js v17.7 loaded - timeframe fix applied');

let workspaceChart;
let workspaceCandlestickSeries;
let workspaceVolumeSeries;
let workspaceTickSeries; // Tick line series for tick mode
let workspaceIndicatorSeries = {}; // Store indicator series for workspace chart
let currentTimeframe = '1m'; // Default timeframe
let currentWorkspaceChartMode = 'candle'; // 'candle' or 'tick'

// ==================== WORKSPACE UI NAMESPACE ====================
const WorkspaceUI = {};

// Initialize workspace chart
document.addEventListener('DOMContentLoaded', function() {
    initWorkspaceChart();
});

function initWorkspaceChart() {
    const chartContainer = document.getElementById('strategyChart');
    
    if (!chartContainer) return;
    
    workspaceChart = LightweightCharts.createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: chartContainer.clientHeight,
        layout: {
            background: { color: '#131722' },
            textColor: '#d1d4dc',
        },
        grid: {
            vertLines: { color: '#1e222d' },
            horzLines: { color: '#1e222d' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: '#2a2e39',
        },
        leftPriceScale: {
            visible: true,
            borderColor: '#2a2e39',
            mode: 0, // Normal mode
            alignLabels: false,
            scaleMargins: {
                top: 0.8,
                bottom: 0,
            },
        },
        timeScale: {
            borderColor: '#2a2e39',
            timeVisible: true,
            secondsVisible: false,
            rightOffset: 5,
            barSpacing: 6,
            fixLeftEdge: false,
            fixRightEdge: false,
            lockVisibleTimeRangeOnResize: true,
            rightBarStaysOnScroll: true,
        },
    });
    
    // Create candlestick series
    workspaceCandlestickSeries = workspaceChart.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderUpColor: '#26a69a',
        borderDownColor: '#ef5350',
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
    });
    
    // Create volume series
    workspaceVolumeSeries = workspaceChart.addHistogramSeries({
        color: '#26a69a',
        priceFormat: {
            type: 'price',
            precision: 0,
            minMove: 1,
        },
        priceScaleId: 'left',
        base: 0, // Start from 0 - baseline fixed at bottom
        priceLineVisible: false,
        lastValueVisible: false,
    });

    // Add tick series (line series) for tick data - initially hidden
    workspaceTickSeries = workspaceChart.addLineSeries({
        color: '#2962ff',
        lineWidth: 2,
        priceLineVisible: false,
        lastValueVisible: true,
        crosshairMarkerVisible: true,
        visible: false // Hidden by default
    });

    console.log('📈 Workspace tick series added (hidden)');

    // Add crosshair event handler to update OHLCV display
    workspaceChart.subscribeCrosshairMove((param) => {
        if (!param || !param.time || !param.seriesData) {
            return;
        }

        const candleData = param.seriesData.get(workspaceCandlestickSeries);

        if (candleData) {
            const { open, high, low, close, time } = candleData;

            // Update OHLC elements
            const openEl = document.getElementById('openPrice');
            const highEl = document.getElementById('highPrice');
            const lowEl = document.getElementById('lowPrice');
            const closeEl = document.getElementById('closePrice');
            const volumeEl = document.getElementById('volumeDisplay');

            if (openEl && open !== undefined) openEl.textContent = open.toFixed(2);
            if (highEl && high !== undefined) highEl.textContent = high.toFixed(2);
            if (lowEl && low !== undefined) lowEl.textContent = low.toFixed(2);
            if (closeEl && close !== undefined) closeEl.textContent = close.toFixed(2);

            // Volume lookup with multiple methods
            if (volumeEl) {
                let volume = 0;

                // Method 1: Direct from candleData.volume
                if (candleData.volume !== undefined) {
                    volume = candleData.volume;
                    console.log('Volume from candleData:', volume);
                }
                // Method 2: From volumeSeries in param.seriesData
                else if (workspaceVolumeSeries) {
                    const volumeData = param.seriesData.get(workspaceVolumeSeries);
                    if (volumeData) {
                        volume = volumeData.value !== undefined ? volumeData.value : volumeData;
                        console.log('Volume from volumeSeries:', volume);
                    }
                }

                // Method 3: Lookup from offlineData (if available globally)
                if (volume === 0 && typeof offlineData !== 'undefined' && offlineData) {
                    // Check volumes array
                    if (offlineData.volumes && Array.isArray(offlineData.volumes)) {
                        const volumeData = offlineData.volumes.find(v => v.time === time);
                        if (volumeData && volumeData.value !== undefined) {
                            volume = volumeData.value;
                            console.log('Volume from offlineData.volumes:', volume);
                        }
                    }

                    // Check candlesticks array
                    if (volume === 0 && offlineData.candlesticks && Array.isArray(offlineData.candlesticks)) {
                        const candle = offlineData.candlesticks.find(c => c.time === time);
                        if (candle && candle.volume !== undefined) {
                            volume = candle.volume;
                            console.log('Volume from offlineData.candlesticks:', volume);
                        }
                    }
                }

                // Display volume
                if (volume > 0) {
                    volumeEl.textContent = Math.round(volume).toLocaleString();
                } else {
                    volumeEl.textContent = '0';
                    console.warn('No volume found for time:', time);
                }
            }
        }
    });

    // Load data from IndexedDB or mock data
    loadWorkspaceData();
    
    // Handle resize
    window.addEventListener('resize', () => {
        workspaceChart.applyOptions({
            width: chartContainer.clientWidth,
            height: chartContainer.clientHeight
        });
    });
    
    console.log('✅ Workspace chart initialized');
}

// Generate signals based on strategy conditions
function generateStrategySignals(candleData) {
    // Use global strategyConfig if available (check window first)
    const config = window.currentStrategyConfig 
        || (typeof window.strategyConfig !== 'undefined' ? window.strategyConfig : null)
        || (typeof strategyConfig !== 'undefined' ? strategyConfig : null);
    
    if (!config || !config.entry_conditions) {
        console.log('⚠️ No strategy config available');
        return { buySignals: [], shortSignals: [] };
    }
    
    console.log('📊 Generating signals with config:', config);
    console.log(`  - Indicators: ${config.indicators.length}`);
    console.log(`  - Long conditions: ${config.entry_conditions.long.length}`);
    console.log(`  - Short conditions: ${config.entry_conditions.short.length}`);
    
    const buySignals = [];
    const shortSignals = [];
    
    // Process each candle
    candleData.forEach((candle, index) => {
        if (index === 0) return; // Skip first candle (need previous for cross detection)
        
        const prevCandle = candleData[index - 1];
        
        // Check long entry conditions
        config.entry_conditions.long.forEach(signal => {
            if (evaluateSignalConditions(signal, candle, prevCandle, candleData, index, config)) {
                buySignals.push({
                    time: candle.time,
                    signalName: signal.name,
                    price: candle.close
                });
                console.log(`✓ Buy signal: ${signal.name} at time ${candle.time}, price ${candle.close}`);
            }
        });
        
        // Check short entry conditions
        config.entry_conditions.short.forEach(signal => {
            if (evaluateSignalConditions(signal, candle, prevCandle, candleData, index, config)) {
                shortSignals.push({
                    time: candle.time,
                    signalName: signal.name,
                    price: candle.close
                });
                console.log(`✓ Short signal: ${signal.name} at time ${candle.time}, price ${candle.close}`);
            }
        });
    });
    
    console.log(`📈 Generated ${buySignals.length} buy signals and ${shortSignals.length} short signals`);
    
    return { buySignals, shortSignals };
}


// Display signals on chart
function displayStrategySignals(candleData) {
    if (!workspaceCandlestickSeries || !candleData || candleData.length === 0) {
        console.log('⚠️ Cannot display signals: No chart or data');
        return;
    }

    console.log(`📊 Chart has ${candleData.length} candles, time range: ${candleData[0].time} to ${candleData[candleData.length-1].time}`);

    // Clear EMA cache before generating new signals
    if (window.emaCache) {
        Object.keys(window.emaCache).forEach(key => delete window.emaCache[key]);
    }
    console.log('🗑️ Cleared EMA cache');

    // Reset trading engine state before processing new signals
    if (typeof resetEngineState === 'function') {
        resetEngineState();
        console.log('🔄 Reset trading engine state');
    }

    // Generate signals
    const { buySignals, shortSignals } = generateStrategySignals(candleData);

    // Process signals through trading engine
    if (typeof processSignal === 'function') {
        console.log('⚙️ Processing signals through trading engine...');

        // Create index map for candles by time
        const candleIndexMap = {};
        candleData.forEach((candle, idx) => {
            candleIndexMap[candle.time] = idx;
        });

        // Build signal map for checking exits
        const signalMap = {};
        buySignals.forEach(signal => {
            const candleIndex = candleIndexMap[signal.time];
            if (candleIndex !== undefined) {
                if (!signalMap[candleIndex]) signalMap[candleIndex] = [];
                signalMap[candleIndex].push({ type: 'BUY', name: signal.signalName });
            }
        });
        shortSignals.forEach(signal => {
            const candleIndex = candleIndexMap[signal.time];
            if (candleIndex !== undefined) {
                if (!signalMap[candleIndex]) signalMap[candleIndex] = [];
                signalMap[candleIndex].push({ type: 'SHORT', name: signal.signalName });
            }
        });

        // Process all candles in sequence
        candleData.forEach((candle, idx) => {
            // 1. Check profit-based exit first (TP/SL/Trailing)
            if (typeof checkProfitExit === 'function') {
                checkProfitExit(candle, idx);
            }

            // 2. Check signal-based exit (opposite signal)
            if (signalMap[idx] && typeof checkSignalExit === 'function') {
                signalMap[idx].forEach(sig => {
                    checkSignalExit(sig.type, idx);
                });
            }

            // 3. Process new entry signals
            if (signalMap[idx]) {
                signalMap[idx].forEach(sig => {
                    processSignal(sig.type, idx);
                    console.log(`  → ${sig.type} signal ${sig.name} at candle ${idx}`);
                });
            }

            // 4. Execute pending entry signals
            executePendingSignals(idx, candle);
        });

        console.log('✅ Processed all signals through trading engine');
        console.log('📊 Final engine state:', getEngineState());
    }
    
    if (buySignals.length === 0 && shortSignals.length === 0) {
        console.log('ℹ️ No signals generated from current strategy');
        workspaceCandlestickSeries.setMarkers([]);
        // Don't show alert, just log to console
        return;
    }
    
    // Create markers with different colors for each signal
    const markers = [];
    
    // Color palette for buy signals
    const buyColors = ['#26a69a', '#00bcd4', '#03a9f4', '#2196f3', '#3f51b5'];
    
    // Add buy signals
    const buySignalGroups = {};
    buySignals.forEach(sig => {
        if (!buySignalGroups[sig.signalName]) {
            buySignalGroups[sig.signalName] = [];
        }
        buySignalGroups[sig.signalName].push(sig);
    });
    
    Object.keys(buySignalGroups).forEach((signalName, idx) => {
        const color = buyColors[idx % buyColors.length];
        buySignalGroups[signalName].forEach(sig => {
            // Ensure time is numeric (Unix timestamp)
            const markerTime = typeof sig.time === 'number' ? sig.time : parseInt(sig.time);
            
            // Format time and price for display
            const date = new Date(markerTime * 1000);
            const timeStr = date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
            const priceStr = sig.price.toFixed(2);
            
            markers.push({
                time: markerTime,
                position: 'belowBar',
                color: color,
                shape: 'arrowUp',
                text: `${signalName} ${priceStr}`,
                size: 1.5
            });
            console.log(`📍 Buy marker: ${signalName} at time=${markerTime}, price=${sig.price}`);
        });
    });
    
    // Color palette for short signals
    const shortColors = ['#ef5350', '#f44336', '#e91e63', '#9c27b0', '#673ab7'];
    
    // Add short signals
    const shortSignalGroups = {};
    shortSignals.forEach(sig => {
        if (!shortSignalGroups[sig.signalName]) {
            shortSignalGroups[sig.signalName] = [];
        }
        shortSignalGroups[sig.signalName].push(sig);
    });
    
    Object.keys(shortSignalGroups).forEach((signalName, idx) => {
        const color = shortColors[idx % shortColors.length];
        shortSignalGroups[signalName].forEach(sig => {
            // Ensure time is numeric (Unix timestamp)
            const markerTime = typeof sig.time === 'number' ? sig.time : parseInt(sig.time);
            
            // Format time and price for display
            const date = new Date(markerTime * 1000);
            const timeStr = date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
            const priceStr = sig.price.toFixed(2);
            
            markers.push({
                time: markerTime,
                position: 'aboveBar',
                color: color,
                shape: 'arrowDown',
                text: `${signalName} ${priceStr}`,
                size: 1.5
            });
            console.log(`📍 Short marker: ${signalName} at time=${markerTime}, price=${sig.price}`);
        });
    });
    
    // Store signal markers globally
    window.signalMarkers = markers;

    // Set workspace candlestick series globally for marker merging
    window.candlestickSeries = workspaceCandlestickSeries;

    // Merge and apply all markers (signals + positions)
    if (typeof updateChartMarkers === 'function') {
        updateChartMarkers();
    } else {
        // Fallback if updateChartMarkers not available
        workspaceCandlestickSeries.setMarkers(markers);
        console.log(`✅ Applied ${markers.length} markers (${buySignals.length} buy, ${shortSignals.length} short)`);
    }

    // Render position entry markers
    if (typeof renderPositionMarkers === 'function') {
        renderPositionMarkers();
    }

    // Fit content to show all markers
    if (markers.length > 0) {
        try {
            workspaceChart.timeScale().fitContent();
        } catch(e) {
            console.warn('Could not fit content:', e);
        }
    }
}

// Expose functions globally
window.displayStrategySignals = displayStrategySignals;
window.generateStrategySignals = generateStrategySignals;
window.changeTimeframe = changeTimeframe;

async function loadWorkspaceData() {
    try {
        console.log('🔄 Loading workspace data...');
        
        // Use shared loadFromIndexedDB from data-manager.js
        const savedData = await loadFromIndexedDB();
        
        if (savedData && savedData.candlesticks) {
            console.log(`📦 Found ${savedData.candlesticks.length} candles`);

            // Store in window.offlineData for timeframe switching
            window.offlineData = {
                candlesticks: savedData.candlesticks,
                base1mData: savedData.candlesticks, // Assume loaded data is 1m base data
                metadata: savedData.metadata || {}
            };
            console.log('💾 Saved to window.offlineData for timeframe switching');

            workspaceCandlestickSeries.setData(savedData.candlesticks);

            // Create volume data from candlesticks (same as chart.js)
            const volumeData = savedData.candlesticks.map(candle => ({
                time: candle.time,
                value: candle.volume || 0,
                color: candle.close >= candle.open ? '#26a69a80' : '#ef535080'
            }));
            workspaceVolumeSeries.setData(volumeData);
            
            // Wait a bit for DOM to be fully ready
            setTimeout(() => {
                // Update tooltip with data info
                try {
                    if (typeof updateDataTooltip === 'function') {
                        const firstCandle = savedData.candlesticks[0];
                        const lastCandle = savedData.candlesticks[savedData.candlesticks.length - 1];
                        const startDate = new Date(firstCandle.time * 1000).toISOString().split('T')[0];
                        const endDate = new Date(lastCandle.time * 1000).toISOString().split('T')[0];
                        const sizeInMB = (JSON.stringify(savedData).length / (1024 * 1024)).toFixed(2);
                        
                        const dataInfo = {
                            start_date: startDate,
                            end_date: endDate,
                            total_candles: savedData.candlesticks.length,
                            size: sizeInMB + ' MB'
                        };
                        
                        console.log('📊 Updating tooltip with:', dataInfo);
                        updateDataTooltip(dataInfo);
                        console.log('✅ Tooltip updated');
                    } else {
                        console.warn('⚠️ updateDataTooltip function not found');
                    }
                } catch (error) {
                    console.warn('⚠️ Error updating tooltip (non-critical):', error.message);
                    // Continue execution even if tooltip update fails
                }
                
                // Display strategy signals if available
                workspaceChart.timeScale().fitContent();
                
                // Check if strategy config exists (use window.strategyConfig or local reference)
                const config = window.currentStrategyConfig 
                    || (typeof window.strategyConfig !== 'undefined' ? window.strategyConfig : null)
                    || (typeof strategyConfig !== 'undefined' ? strategyConfig : null);
                    
                if (config && config.entry_conditions) {
                    console.log('📈 Strategy config found:');
                    console.log(`   - Long conditions: ${config.entry_conditions.long?.length || 0}`);
                    console.log(`   - Short conditions: ${config.entry_conditions.short?.length || 0}`);
                    
                    if (config.entry_conditions.long) {
                        console.log('   - Long condition details:', config.entry_conditions.long);
                    }
                    if (config.entry_conditions.short) {
                        console.log('   - Short condition details:', config.entry_conditions.short);
                    }
                } else {
                    console.warn('⚠️ No strategy config available');
                }
                
                displayStrategySignals(savedData.candlesticks);
            }, 300);
            
            console.log('✅ Loaded data from IndexedDB');
        } else {
            console.log('⚠️ No data available. Please upload CSV from main page.');
        }
    } catch (error) {
        console.error('❌ Error loading workspace data:', error);
    }
}

// Timeframe Aggregator for workspace chart
const WorkspaceTimeframeAggregator = {
    /**
     * Aggregate 1-minute candles into higher timeframes
     * @param {Array} candles1m - Array of 1-minute OHLC candles
     * @param {string} targetTF - Target timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)
     * @returns {Array} Aggregated candles
     */
    aggregate: function(candles1m, targetTF) {
        if (!candles1m || candles1m.length === 0) return [];

        const tfMinutes = {
            '1m': 1, 'M1': 1,
            '5m': 5, 'M5': 5,
            '15m': 15, 'M15': 15,
            '30m': 30, 'M30': 30,
            '1h': 60, 'H1': 60,
            '4h': 240, 'H4': 240,
            '1d': 1440, 'D1': 1440
        };

        const targetMinutes = tfMinutes[targetTF] || 1;

        // If already 1m, return as is
        if (targetMinutes === 1) return candles1m;

        const aggregated = [];
        const targetSeconds = targetMinutes * 60;

        let currentGroup = [];
        let currentPeriodStart = null;

        for (const candle of candles1m) {
            const candleTime = candle.time;
            const periodStart = Math.floor(candleTime / targetSeconds) * targetSeconds;

            if (currentPeriodStart === null) {
                currentPeriodStart = periodStart;
            }

            if (periodStart === currentPeriodStart) {
                currentGroup.push(candle);
            } else {
                // Aggregate current group
                if (currentGroup.length > 0) {
                    aggregated.push(this._aggregateGroup(currentGroup, currentPeriodStart));
                }

                // Start new group
                currentGroup = [candle];
                currentPeriodStart = periodStart;
            }
        }

        // Aggregate last group
        if (currentGroup.length > 0) {
            aggregated.push(this._aggregateGroup(currentGroup, currentPeriodStart));
        }

        console.log(`📊 Aggregated ${candles1m.length} candles → ${aggregated.length} ${targetTF} candles`);

        // Debug: Show first few timestamps and spacing
        if (aggregated.length > 0) {
            console.log(`📊 First 3 candle times:`);
            for (let i = 0; i < Math.min(3, aggregated.length); i++) {
                const date = new Date(aggregated[i].time * 1000);
                console.log(`   [${i}] ${date.toLocaleString()} (timestamp: ${aggregated[i].time})`);
            }

            if (aggregated.length > 1) {
                const spacing = aggregated[1].time - aggregated[0].time;
                console.log(`📊 Time spacing: ${spacing} seconds = ${spacing / 60} minutes`);
                console.log(`📊 Expected spacing: ${targetSeconds} seconds = ${targetMinutes} minutes`);

                if (spacing !== targetSeconds) {
                    console.error(`❌ SPACING MISMATCH! Got ${spacing}s but expected ${targetSeconds}s`);
                }
            }
        }

        return aggregated;
    },

    _aggregateGroup: function(candles, periodStart) {
        return {
            time: periodStart,
            open: candles[0].open,
            high: Math.max(...candles.map(c => c.high)),
            low: Math.min(...candles.map(c => c.low)),
            close: candles[candles.length - 1].close,
            volume: candles.reduce((sum, c) => sum + (c.volume || 0), 0)
        };
    }
};

function changeTimeframe(tf) {
    if (!workspaceChart) {
        console.warn('⚠️ Chart not initialized yet');
        return;
    }

    console.log(`🔄 Changing timeframe from ${currentTimeframe} to ${tf}`);

    // Update current timeframe
    currentTimeframe = tf;

    // Update active class on buttons
    document.querySelectorAll('.tf-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tf') === tf) {
            btn.classList.add('active');
        }
    });

    // Handle TICK mode
    if (tf === 'tick') {
        console.log('📊 Switching to TICK chart mode');
        currentWorkspaceChartMode = 'tick';

        // Hide candlestick and volume series
        if (workspaceCandlestickSeries) {
            workspaceChart.removeSeries(workspaceCandlestickSeries);
            workspaceCandlestickSeries = null;
        }
        if (workspaceVolumeSeries) {
            workspaceChart.removeSeries(workspaceVolumeSeries);
            workspaceVolumeSeries = null;
        }

        // Show tick series
        if (!workspaceTickSeries) {
            workspaceTickSeries = workspaceChart.addLineSeries({
                color: '#2962ff',
                lineWidth: 2,
                priceLineVisible: false,
                lastValueVisible: true,
                crosshairMarkerVisible: true,
            });
        }

        // Load tick data if available
        if (typeof window.offlineData !== 'undefined' && window.offlineData) {
            const tickData = window.offlineData.ticks || window.offlineData.tickData || [];

            if (tickData && tickData.length > 0) {
                workspaceTickSeries.setData(tickData);
                workspaceChart.timeScale().fitContent();
                console.log(`✅ Loaded ${tickData.length} tick data points`);
            } else {
                console.log('⚠️ No tick data available yet');
            }
        } else {
            console.log('⚠️ No tick data available');
        }

        return;
    }

    // Switch back to candle mode if coming from tick
    if (currentWorkspaceChartMode === 'tick') {
        console.log('📊 Switching back to CANDLE chart mode');
        currentWorkspaceChartMode = 'candle';

        // Remove tick series
        if (workspaceTickSeries) {
            workspaceChart.removeSeries(workspaceTickSeries);
            workspaceTickSeries = null;
        }

        // Re-add candlestick series
        if (!workspaceCandlestickSeries) {
            workspaceCandlestickSeries = workspaceChart.addCandlestickSeries({
                upColor: '#26a69a',
                downColor: '#ef5350',
                borderUpColor: '#26a69a',
                borderDownColor: '#ef5350',
                wickUpColor: '#26a69a',
                wickDownColor: '#ef5350',
            });
        }

        // Re-add volume series
        if (!workspaceVolumeSeries) {
            workspaceVolumeSeries = workspaceChart.addHistogramSeries({
                color: '#26a69a',
                priceFormat: {
                    type: 'price',
                    precision: 0,
                    minMove: 1,
                },
                priceScaleId: 'left',
                base: 0,
                priceLineVisible: false,
                lastValueVisible: false,
            });
        }
    }

    // Check if we have offline data to aggregate
    if (typeof window.offlineData !== 'undefined' && window.offlineData && window.offlineData.candlesticks) {
        console.log('📊 Aggregating data for timeframe:', tf);

        // Get base 1m data
        const base1mData = window.offlineData.base1mData || window.offlineData.candlesticks;

        // Store base data if not already stored
        if (!window.offlineData.base1mData) {
            window.offlineData.base1mData = [...window.offlineData.candlesticks];
        }

        let aggregatedData;

        // For 1m, use base data directly
        if (tf === '1m' || tf === 'M1') {
            aggregatedData = base1mData;
        } else {
            // Aggregate from 1m to target timeframe
            aggregatedData = WorkspaceTimeframeAggregator.aggregate(base1mData, tf);
        }

        // Update chart with aggregated data (same logic as chart.js in index page)
        if (aggregatedData && aggregatedData.length > 0) {
            console.log(`🔄 Setting chart data for ${tf} timeframe...`);
            console.log(`   Total candles: ${aggregatedData.length}`);

            // Check first few candles before setting
            console.log(`   First 3 candles being set to chart:`);
            for (let i = 0; i < Math.min(3, aggregatedData.length); i++) {
                const date = new Date(aggregatedData[i].time * 1000);
                console.log(`      [${i}] ${date.toLocaleString()} - O:${aggregatedData[i].open} H:${aggregatedData[i].high} L:${aggregatedData[i].low} C:${aggregatedData[i].close}`);
            }

            // Simply update data on existing series (DO NOT recreate series)
            // This allows LightweightCharts to automatically detect the new time interval
            workspaceCandlestickSeries.setData(aggregatedData);
            console.log(`   ✓ Candlestick data set`);

            // Update volume
            const volumeData = aggregatedData.map(candle => ({
                time: candle.time,
                value: candle.volume || 0,
                color: candle.close >= candle.open ? '#26a69a80' : '#ef535080'
            }));
            if (workspaceVolumeSeries) {
                workspaceVolumeSeries.setData(volumeData);
                console.log(`   ✓ Volume data set`);
            }

            // Fit content to show all data with timeout to ensure rendering is complete
            setTimeout(() => {
                workspaceChart.timeScale().fitContent();
                console.log(`   ✓ Chart fitted to content`);
            }, 100);

            console.log(`✅ Updated chart with ${aggregatedData.length} ${tf} candles`);
        } else {
            console.error('❌ Failed to aggregate data');
        }
    } else {
        console.warn('⚠️ No offline data available. Please upload CSV data first.');

        // Just fit content
        workspaceChart.timeScale().fitContent();
    }
}

// Add buy/short signal markers to chart
function addSignalMarkers(buySignals, shortSignals, candlesticks) {
    const markers = [];
    
    buySignals.forEach((signal, index) => {
        if (signal) {
            markers.push({
                time: candlesticks[index].time,
                position: 'belowBar',
                color: '#26a69a',
                shape: 'arrowUp',
                text: 'BUY'
            });
        }
    });
    
    shortSignals.forEach((signal, index) => {
        if (signal) {
            markers.push({
                time: candlesticks[index].time,
                position: 'aboveBar',
                color: '#ef5350',
                shape: 'arrowDown',
                text: 'SHORT'
            });
        }
    });
    
    workspaceCandlestickSeries.setMarkers(markers);
    console.log(`✅ Added ${markers.length} signal markers to chart`);
}

// Clear all markers
function clearSignalMarkers() {
    if (workspaceCandlestickSeries) {
        workspaceCandlestickSeries.setMarkers([]);
    }
}

// Display trading signals on workspace chart
function displayWorkspaceSignals(signals, candlesticks) {
    if (!workspaceCandlestickSeries || !signals || !candlesticks) {
        return;
    }
    
    const markers = [];
    
    signals.buy.forEach((isBuy, index) => {
        if (isBuy && candlesticks[index]) {
            markers.push({
                time: candlesticks[index].time,
                position: "belowBar",
                color: "#26a69a",
                shape: "arrowUp",
                text: "BUY"
            });
        }
    });
    
    signals.short.forEach((isShort, index) => {
        if (isShort && candlesticks[index]) {
            markers.push({
                time: candlesticks[index].time,
                position: "aboveBar",
                color: "#ef5350",
                shape: "arrowDown",
                text: "SHORT"
            });
        }
    });
    
    workspaceCandlestickSeries.setMarkers(markers);
    console.log(`✅ Displayed ${markers.length} signals on strategy builder chart`);
}

// ==================== CHART CONTROLS ====================

function zoomIn() {
    if (!workspaceChart) return;
    const timeScale = workspaceChart.timeScale();
    const logicalRange = timeScale.getVisibleLogicalRange();
    if (logicalRange) {
        const center = (logicalRange.from + logicalRange.to) / 2;
        const newRange = (logicalRange.to - logicalRange.from) * 0.8;
        timeScale.setVisibleLogicalRange({
            from: center - newRange / 2,
            to: center + newRange / 2
        });
    }
}

function zoomOut() {
    if (!workspaceChart) return;
    const timeScale = workspaceChart.timeScale();
    const logicalRange = timeScale.getVisibleLogicalRange();
    if (logicalRange) {
        const center = (logicalRange.from + logicalRange.to) / 2;
        const newRange = (logicalRange.to - logicalRange.from) * 1.25;
        timeScale.setVisibleLogicalRange({
            from: center - newRange / 2,
            to: center + newRange / 2
        });
    }
}

function toggleVolume() {
    if (!workspaceVolumeSeries) return;
    const btn = document.getElementById('toggleVolumeBtn');
    const isVisible = btn.classList.contains('active');
    
    workspaceVolumeSeries.applyOptions({
        visible: !isVisible
    });
    
    btn.classList.toggle('active');
    console.log(isVisible ? '📊 Volume hidden' : '📊 Volume shown');
}

// Note: Scroll functions are defined later in the file (lines ~1182-1215)
// to avoid duplication and use proper logical range calculations

function downloadChartCSV() {
    loadFromIndexedDB().then(data => {
        if (!data || !data.candlesticks || data.candlesticks.length === 0) {
            alert('⚠️ No data to download');
            return;
        }
        
        // Convert to CSV
        let csv = 'Date,Time,Open,High,Low,Close,Volume\n';
        data.candlesticks.forEach(candle => {
            const date = new Date(candle.time * 1000);
            const dateStr = date.toLocaleDateString('vi-VN');
            const timeStr = date.toLocaleTimeString('vi-VN');
            csv += `${dateStr},${timeStr},${candle.open},${candle.high},${candle.low},${candle.close},${candle.volume || 0}\n`;
        });
        
        // Download
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chart_data_${Date.now()}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
        
        console.log('💾 Downloaded CSV file');
    });
}

async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    console.log(`📁 Uploading file: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`);

    try {
        const text = await file.text();
        const lines = text.split('\n').filter(line => line.trim());

        if (lines.length < 2) {
            alert('❌ File CSV không hợp lệ!');
            return;
        }

        // Parse header to detect format
        const header = lines[0].toLowerCase();
        const hasTicker = header.includes('ticker');
        const hasDateTime = header.includes('datetime');

        console.log(`📋 CSV format detected: ${hasTicker ? 'Ticker,Date,Time' : hasDateTime ? 'DateTime' : 'Unknown'}`);

        // Timezone offset for Vietnam (UTC+7) in seconds
        const UTC_OFFSET = 7 * 60 * 60;

        // Parse CSV
        const candlesticks = [];
        for (let i = 1; i < lines.length; i++) {
            const parts = lines[i].split(',');
            if (parts.length < 6) continue;

            let dateTime;
            let dataStart;

            if (hasTicker) {
                // Format: Ticker,Date,Time,Open,High,Low,Close,Volume
                // parts[0] = Ticker, parts[1] = Date, parts[2] = Time
                const dateStr = parts[1].trim();
                const timeStr = parts[2].trim();
                dateTime = new Date(`${dateStr} ${timeStr}`);
                dataStart = 3; // OHLCV starts at index 3
            } else {
                // Format: DateTime,Open,High,Low,Close,Volume
                // parts[0] = DateTime
                dateTime = new Date(parts[0]);
                dataStart = 1; // OHLCV starts at index 1
            }

            if (isNaN(dateTime)) {
                console.warn(`⚠️ Invalid date at line ${i}: ${parts[0]}`);
                continue;
            }

            // Convert to Unix timestamp and add UTC+7 offset
            // CSV data is in UTC+0, chart displays in local time, so we add 7 hours
            candlesticks.push({
                time: Math.floor(dateTime.getTime() / 1000) + UTC_OFFSET,
                open: parseFloat(parts[dataStart]),
                high: parseFloat(parts[dataStart + 1]),
                low: parseFloat(parts[dataStart + 2]),
                close: parseFloat(parts[dataStart + 3]),
                volume: parseFloat(parts[dataStart + 4] || 0)
            });
        }

        if (candlesticks.length === 0) {
            alert('❌ Không tìm thấy dữ liệu hợp lệ trong file!\n\nFormat hỗ trợ:\n1. Ticker,Date,Time,Open,High,Low,Close,Volume\n2. DateTime,Open,High,Low,Close,Volume');
            return;
        }

        console.log(`✅ Parsed ${candlesticks.length} candles successfully`);
        
        // Sort by time
        candlesticks.sort((a, b) => a.time - b.time);

        // Save to IndexedDB
        await saveToIndexedDB({
            candlesticks: candlesticks,
            metadata: {
                filename: file.name,
                uploadDate: Date.now(),
                candleCount: candlesticks.length,
                fromDate: new Date(candlesticks[0].time * 1000).toISOString(),
                toDate: new Date(candlesticks[candlesticks.length - 1].time * 1000).toISOString()
            }
        });

        // Store in window.offlineData for timeframe switching
        window.offlineData = {
            candlesticks: candlesticks,
            base1mData: candlesticks, // Assume uploaded data is 1m base data
            metadata: {
                filename: file.name,
                uploadDate: Date.now(),
                candleCount: candlesticks.length
            }
        };

        console.log('💾 Saved to window.offlineData for timeframe switching');

        // Display on chart
        workspaceCandlestickSeries.setData(candlesticks);
        
        const volumeData = candlesticks.map(c => ({
            time: c.time,
            value: c.volume || 0,
            color: c.close >= c.open ? '#26a69a80' : '#ef535080'
        }));
        
        // DEBUG: Check volume values
        console.log('📊 Volume data sample:', volumeData.slice(0, 5));
        console.log('📊 Volume min/max:', Math.min(...volumeData.map(v => v.value)), Math.max(...volumeData.map(v => v.value)));
        
        workspaceVolumeSeries.setData(volumeData);
        
        // Update tooltip
        updateDataTooltip(candlesticks.length, file.name, file.size);
        
        // Update price display
        updatePriceDisplay(candlesticks[candlesticks.length - 1]);
        
        alert(`✅ Đã tải ${candlesticks.length} nến thành công!`);
        console.log(`✅ Loaded ${candlesticks.length} candles`);
        
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('❌ Lỗi khi đọc file: ' + error.message);
    }
}

// updateDataTooltip is now in data-manager.js - removed duplicate

function updatePriceDisplay(candle) {
    if (!candle) return;

    const currentPrice = document.getElementById('currentPrice');
    const highPrice = document.getElementById('highPrice');
    const lowPrice = document.getElementById('lowPrice');
    const closePrice = document.getElementById('closePrice');
    const changeEl = document.getElementById('priceChange');

    // Only update if elements exist (may not be on all pages)
    if (currentPrice) currentPrice.textContent = candle.close.toFixed(2);
    if (highPrice) highPrice.textContent = 'H: ' + candle.high.toFixed(2);
    if (lowPrice) lowPrice.textContent = 'L: ' + candle.low.toFixed(2);
    if (closePrice) closePrice.textContent = 'C: ' + candle.close.toFixed(2);

    if (changeEl) {
        const change = candle.close - candle.open;
        const changePct = (change / candle.open * 100).toFixed(2);
        changeEl.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)} (${changePct}%)`;
        changeEl.style.color = change >= 0 ? '#26a69a' : '#ef5350';
    }
}

function showUploadedFiles() {
    loadFromIndexedDB().then(data => {
        if (!data || !data.metadata) {
            alert('📂 Chưa có file nào được lưu');
            return;
        }
        
        const info = `📊 Thông tin file đã lưu:\n\n` +
            `Tên file: ${data.metadata.filename}\n` +
            `Số nến: ${data.metadata.candleCount.toLocaleString()}\n` +
            `Từ: ${new Date(data.metadata.fromDate).toLocaleString('vi-VN')}\n` +
            `Đến: ${new Date(data.metadata.toDate).toLocaleString('vi-VN')}\n` +
            `Upload: ${new Date(data.metadata.uploadDate).toLocaleString('vi-VN')}`;
        
        alert(info);
    });
}

async function clearOfflineData(silent = false) {
    if (!silent && !confirm('⚠️ Bạn có chắc muốn xóa toàn bộ dữ liệu đã lưu?')) return;
    
    try {
        const request = indexedDB.deleteDatabase('ChartDataDB');
        request.onsuccess = () => {
            if (!silent) {
                alert('✅ Đã xóa dữ liệu thành công!');
                location.reload();
            } else {
                console.log('✅ Old data cleared silently');
            }
        };
        request.onerror = () => {
            if (!silent) {
                alert('❌ Lỗi khi xóa dữ liệu');
            }
        };
    } catch (error) {
        console.error('Error clearing data:', error);
        if (!silent) {
            alert('❌ Lỗi: ' + error.message);
        }
    }
}


// ==================== CHART CONTROL FUNCTIONS ====================

function changeDataSource() {
    const select = document.getElementById('dataSourceSelect');
    if (!select) return;
    console.log('Data source changed to:', select.value);
    // Implementation will sync with main page
}

function scrollToStart() {
    if (!workspaceChart) return;
    const timeScale = workspaceChart.timeScale();
    const logicalRange = timeScale.getVisibleLogicalRange();
    if (logicalRange) {
        timeScale.scrollToPosition(-logicalRange.from, false);
    }
}

function scrollLeft() {
    if (!workspaceChart) return;
    const timeScale = workspaceChart.timeScale();
    const logicalRange = timeScale.getVisibleLogicalRange();
    if (logicalRange) {
        // Calculate scroll distance based on current timeframe
        // Each timeframe should scroll by a few candles (e.g., 5-10 candles)
        const tfMinutes = {
            'tick': 0.01,  // Tick mode
            '1m': 1, 'M1': 1,
            '5m': 5, 'M5': 5,
            '15m': 15, 'M15': 15,
            '30m': 30, 'M30': 30,
            '1h': 60, 'H1': 60,
            '4h': 240, 'H4': 240,
            '1d': 1440, 'D1': 1440
        };

        const currentMinutes = tfMinutes[currentTimeframe] || 1;
        const candlesToScroll = 5; // Scroll by 5 candles
        const timeInSeconds = currentMinutes * 60 * candlesToScroll;

        // Convert time to logical distance (approximate)
        // For most charts, 1 logical unit ≈ 1 candle
        const distance = candlesToScroll;

        timeScale.scrollToPosition(-distance, true);
    }
}

function scrollRight() {
    if (!workspaceChart) return;
    const timeScale = workspaceChart.timeScale();
    const logicalRange = timeScale.getVisibleLogicalRange();
    if (logicalRange) {
        // Calculate scroll distance based on current timeframe
        const tfMinutes = {
            'tick': 0.01,
            '1m': 1, 'M1': 1,
            '5m': 5, 'M5': 5,
            '15m': 15, 'M15': 15,
            '30m': 30, 'M30': 30,
            '1h': 60, 'H1': 60,
            '4h': 240, 'H4': 240,
            '1d': 1440, 'D1': 1440
        };

        const currentMinutes = tfMinutes[currentTimeframe] || 1;
        const candlesToScroll = 5; // Scroll by 5 candles
        const timeInSeconds = currentMinutes * 60 * candlesToScroll;

        // Convert time to logical distance
        const distance = candlesToScroll;

        timeScale.scrollToPosition(distance, true);
    }
}

function scrollToEnd() {
    if (!workspaceChart) return;
    const timeScale = workspaceChart.timeScale();
    timeScale.scrollToRealTime();
}

// zoomIn() and zoomOut() functions are defined earlier in the file (lines 506-532)

function toggleChartType() {
    console.log('Toggle chart type - to be implemented');
}

function showIndicators() {
    console.log('🔍 showIndicators called (workspace)');
    
    const panel = document.getElementById('indicatorsDisplayPanel');
    console.log('📋 Panel element:', panel ? 'found' : 'NOT FOUND');
    
    if (!panel) {
        console.error('❌ Indicators panel not found in DOM');
        alert('⚠️ Indicators panel not found. Please refresh the page.');
        return;
    }
    
    // Directly toggle the panel
    const isHidden = panel.classList.contains('hidden');
    console.log('👁️ Panel currently hidden:', isHidden);
    
    if (isHidden) {
        panel.classList.remove('hidden');
        console.log('✅ Panel shown');
        
        // Update content
        if (typeof updateIndicatorsDisplayPanel === 'function') {
            updateIndicatorsDisplayPanel();
        } else {
            const container = document.getElementById('indicatorsPanelContent');
            if (container) {
                if (typeof activeIndicators === 'undefined' || !activeIndicators || activeIndicators.length === 0) {
                    container.innerHTML = '<p class="empty-state">No indicators added yet.<br><br>Go to Strategy Builder → Indicators tab to add indicators first.</p>';
                }
            }
        }
    } else {
        panel.classList.add('hidden');
        console.log('✅ Panel hidden');
    }
}

function fitChartContent() {
    if (!workspaceChart) return;
    workspaceChart.timeScale().fitContent();
}

function showUploadedFiles() {
    console.log('Show uploaded files');
    // To be implemented
}

function clearOfflineData(silent = false) {
    if (!silent && !confirm('⚠️ Xóa toàn bộ dữ liệu offline?')) {
        return;
    }
    
    // Clear IndexedDB
    indexedDB.deleteDatabase('TradingDataDB');
    if (!silent) {
        alert('✅ Đã xóa dữ liệu offline');
        location.reload();
    } else {
        console.log('✅ Old data cleared silently');
    }
}

function downloadChartCSV() {
    console.log('Download CSV - to be implemented');
}

// ==================== INDICATORS DISPLAY PANEL ====================

let indicatorSeries = {}; // Store chart series for indicators

function toggleIndicatorsDisplayPanel() {
    console.log('🔄 toggleIndicatorsDisplayPanel called (workspace)');
    
    const panel = document.getElementById('indicatorsDisplayPanel');
    if (!panel) {
        console.error('❌ Indicators panel not found in DOM');
        return;
    }
    
    const isHidden = panel.classList.contains('hidden');
    console.log('👁️ Panel state:', isHidden ? 'hidden' : 'visible');
    
    if (isHidden) {
        panel.classList.remove('hidden');
        console.log('✅ Panel shown');
        updateIndicatorsDisplayPanel();
    } else {
        panel.classList.add('hidden');
        console.log('✅ Panel hidden');
    }
}

function updateIndicatorsDisplayPanel() {
    console.log('🔄 updateIndicatorsDisplayPanel called (workspace)');
    
    const container = document.getElementById('indicatorsPanelContent');
    if (!container) {
        console.warn('⚠️ Indicators panel content container not found (may not be on this page)');
        return;
    }
    
    console.log('📊 activeIndicators:', typeof activeIndicators !== 'undefined' ? activeIndicators : 'undefined');
    console.log('📊 activeIndicators length:', typeof activeIndicators !== 'undefined' && activeIndicators ? activeIndicators.length : 0);
    
    // Get active indicators from strategy (from strategy-builder.js)
    if (typeof activeIndicators === 'undefined' || !activeIndicators || activeIndicators.length === 0) {
        container.innerHTML = '<p class="empty-state">No indicators added yet.<br><br>Add indicators in the Indicators tab first.</p>';
        console.log('ℹ️ No indicators to display');
        return;
    }
    
    console.log('✅ Rendering', activeIndicators.length, 'indicators');
    
    let html = '';
    activeIndicators.forEach(ind => {
        const paramStr = Object.entries(ind.params || {})
            .map(([k, v]) => `${k}:${v}`)
            .join(', ');
        
        // Initialize display settings if not exist
        if (!ind.display) {
            ind.display = {
                show: true,
                color: getDefaultIndicatorColor(ind.type),
                lineStyle: 'solid',
                lineWidth: 2
            };
        }
        
        html += `
            <div class="indicator-display-item" data-ind-id="${ind.id}">
                <div class="indicator-header">
                    <label class="checkbox-label">
                        <input type="checkbox" ${ind.display.show ? 'checked' : ''} 
                               onchange="toggleIndicatorVisibility('${ind.id}', this.checked)">
                        <strong>${ind.type}</strong> 
                        <small>(${paramStr})</small>
                    </label>
                </div>
                <div class="indicator-settings">
                    <div class="setting-row">
                        <label>Color</label>
                        <input type="color" value="${ind.display.color}" 
                               onchange="updateIndicatorColor('${ind.id}', this.value)">
                    </div>
                    <div class="setting-row">
                        <label>Style</label>
                        <select onchange="updateIndicatorStyle('${ind.id}', this.value)">
                            <option value="solid" ${ind.display.lineStyle === 'solid' ? 'selected' : ''}>Solid</option>
                            <option value="dotted" ${ind.display.lineStyle === 'dotted' ? 'selected' : ''}>Dotted</option>
                            <option value="dashed" ${ind.display.lineStyle === 'dashed' ? 'selected' : ''}>Dashed</option>
                        </select>
                    </div>
                    <div class="setting-row">
                        <label>Width</label>
                        <select onchange="updateIndicatorWidth('${ind.id}', parseInt(this.value))">
                            ${[1,2,3,4,5].map(w => 
                                `<option value="${w}" ${ind.display.lineWidth === w ? 'selected' : ''}>${w}px</option>`
                            ).join('')}
                        </select>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
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

function toggleIndicatorVisibility(indId, show) {
    // Find indicator in activeIndicators
    const indicator = activeIndicators.find(i => i.id === indId);
    if (!indicator) return;
    
    indicator.display.show = show;
    
    // Sync back to strategyConfig (if available)
    if (typeof strategyConfig !== 'undefined' && strategyConfig && strategyConfig.indicators) {
        const strategyInd = strategyConfig.indicators.find(i => i.id === indId);
        if (strategyInd) {
            if (!strategyInd.display) {
                strategyInd.display = {};
            }
            strategyInd.display.show = show;
        }
    }
    
    // Update chart series visibility
    if (indicatorSeries[indId]) {
        indicatorSeries[indId].applyOptions({ visible: show });
    }
    
    // Handle multi-line indicators (MACD, BB)
    const multiLineKeys = Object.keys(indicatorSeries).filter(k => k.startsWith(indId + '_'));
    multiLineKeys.forEach(key => {
        if (indicatorSeries[key]) {
            indicatorSeries[key].applyOptions({ visible: show });
        }
    });
    
    // Trigger auto-save (strategy builder)
    if (typeof triggerAutoSave === 'function') {
        triggerAutoSave();
    }
    
    // Trigger auto-save (indicators only - for Bot Trading page)
    if (typeof triggerIndicatorsAutoSave === 'function') {
        triggerIndicatorsAutoSave();
    }
}

function updateIndicatorColor(indId, color) {
    const indicator = activeIndicators.find(i => i.id === indId);
    if (!indicator) return;
    
    indicator.display.color = color;
    
    // Sync back to strategyConfig (if available)
    if (typeof strategyConfig !== 'undefined' && strategyConfig && strategyConfig.indicators) {
        const strategyInd = strategyConfig.indicators.find(i => i.id === indId);
        if (strategyInd) {
            if (!strategyInd.display) {
                strategyInd.display = {};
            }
            strategyInd.display.color = color;
        }
    }
    
    // Update chart series color
    if (indicatorSeries[indId]) {
        indicatorSeries[indId].applyOptions({ color: color });
    }
    
    // Trigger auto-save
    if (typeof triggerAutoSave === 'function') {
        triggerAutoSave();
    }
}

function updateIndicatorStyle(indId, style) {
    const indicator = activeIndicators.find(i => i.id === indId);
    if (!indicator) return;
    
    indicator.display.lineStyle = style;
    
    // Sync back to strategyConfig (if available)
    if (typeof strategyConfig !== 'undefined' && strategyConfig && strategyConfig.indicators) {
        const strategyInd = strategyConfig.indicators.find(i => i.id === indId);
        if (strategyInd) {
            if (!strategyInd.display) {
                strategyInd.display = {};
            }
            strategyInd.display.lineStyle = style;
        }
    }
    
    const lineStyleMap = {
        'solid': LightweightCharts.LineStyle.Solid,
        'dotted': LightweightCharts.LineStyle.Dotted,
        'dashed': LightweightCharts.LineStyle.Dashed
    };
    
    if (indicatorSeries[indId]) {
        indicatorSeries[indId].applyOptions({ 
            lineStyle: lineStyleMap[style] 
        });
    }
    
    // Trigger auto-save
    if (typeof triggerAutoSave === 'function') {
        triggerAutoSave();
    }
}

function updateIndicatorWidth(indId, width) {
    const indicator = activeIndicators.find(i => i.id === indId);
    if (!indicator) return;
    
    indicator.display.lineWidth = width;
    
    // Sync back to strategyConfig (if available)
    if (typeof strategyConfig !== 'undefined' && strategyConfig && strategyConfig.indicators) {
        const strategyInd = strategyConfig.indicators.find(i => i.id === indId);
        if (strategyInd) {
            if (!strategyInd.display) {
                strategyInd.display = {};
            }
            strategyInd.display.lineWidth = width;
        }
    }
    
    if (indicatorSeries[indId]) {
        indicatorSeries[indId].applyOptions({ lineWidth: width });
    }
    
    // Trigger auto-save
    if (typeof triggerAutoSave === 'function') {
        triggerAutoSave();
    }
}

// ==================== INDICATORS AND SIGNALS PANEL ====================




function saveIndicatorsToLocalStorage() {
    try {
        const indicators = window.activeIndicators || [];
        localStorage.setItem('userSelectedIndicators', JSON.stringify(indicators));
        console.log('💾 Saved indicators to localStorage:', indicators.length);
    } catch (error) {
        console.error('Failed to save indicators:', error);
    }
}

function loadIndicatorsFromLocalStorage() {
    try {
        const saved = localStorage.getItem('userSelectedIndicators');
        if (saved) {
            window.activeIndicators = JSON.parse(saved);
            console.log('✅ Loaded indicators from localStorage:', window.activeIndicators.length);

            // Render if data available
            if (typeof window.offlineData !== 'undefined' && window.offlineData && window.offlineData.candlesticks) {
                if (typeof calculateAndRenderIndicators === 'function') {
                    setTimeout(() => calculateAndRenderIndicators(), 300);
                }
            }
        }
    } catch (error) {
        console.error('Failed to load indicators:', error);
    }
}

// Load indicators on page load
document.addEventListener('DOMContentLoaded', function() {
    loadIndicatorsFromLocalStorage();
});


// Export functions
window.toggleIndicatorsDisplayPanel = toggleIndicatorsDisplayPanel;
window.updateIndicatorsDisplayPanel = updateIndicatorsDisplayPanel;
window.toggleIndicatorVisibility = toggleIndicatorVisibility;
window.updateIndicatorColor = updateIndicatorColor;
window.updateIndicatorStyle = updateIndicatorStyle;
window.updateIndicatorWidth = updateIndicatorWidth;
window.saveIndicatorsToLocalStorage = saveIndicatorsToLocalStorage;
window.loadIndicatorsFromLocalStorage = loadIndicatorsFromLocalStorage;

// ==================== RENDER INDICATORS ON CHART ====================

function calculateAndRenderIndicators() {
    console.log('🎨 calculateAndRenderIndicators called (workspace)');
    
    if (!offlineData || !offlineData.candlesticks || offlineData.candlesticks.length === 0) {
        console.log('⚠️ No data available for indicators');
        return;
    }
    
    // Get indicators from strategyConfig or activeIndicators
    const indicators = (typeof strategyConfig !== 'undefined' && strategyConfig.indicators)
        || (typeof activeIndicators !== 'undefined' && activeIndicators)
        || [];
    
    if (!indicators || indicators.length === 0) {
        console.log('⚠️ No active indicators to render');
        return;
    }
    
    console.log('📊 Rendering', indicators.length, 'indicators');
    
    // Clear existing indicator series
    Object.values(workspaceIndicatorSeries).forEach(series => {
        try {
            workspaceChart.removeSeries(series);
        } catch(e) {
            console.warn('Could not remove series:', e);
        }
    });
    workspaceIndicatorSeries = {};
    
    // Prepare data for API
    const candlesData = offlineData.candlesticks.map(c => ({
        time: c.time,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
        volume: c.volume || 0
    }));
    
    // Call API to calculate indicators
    fetch('/calculate_indicators', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            data: candlesData,
            indicators: indicators
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('❌ Failed to calculate indicators:', data.error);
            return;
        }
        
        console.log('✅ Indicators calculated:', Object.keys(data.indicators));
        
        // Render indicators on chart
        indicators.forEach(ind => {
            if (!ind.display || !ind.display.show) return;
            
            const lineStyleMap = {
                'solid': LightweightCharts.LineStyle.Solid,
                'dotted': LightweightCharts.LineStyle.Dotted,
                'dashed': LightweightCharts.LineStyle.Dashed
            };
            
            if (ind.type === 'MACD') {
                // MACD line
                if (data.indicators[ind.id + '_macd']) {
                    const macdSeries = workspaceChart.addLineSeries({
                        color: ind.display.color,
                        lineWidth: ind.display.lineWidth,
                        lineStyle: lineStyleMap[ind.display.lineStyle] || LightweightCharts.LineStyle.Solid,
                        title: `${ind.type}_MACD`,
                        visible: ind.display.show,
                        priceScaleId: 'macd', // Use separate scale for MACD
                        priceFormat: {
                            type: 'price',
                            precision: 4,
                            minMove: 0.0001
                        }
                    });
                    macdSeries.setData(data.indicators[ind.id + '_macd']);
                    workspaceIndicatorSeries[ind.id + '_macd'] = macdSeries;
                }
                
                // Signal line
                if (data.indicators[ind.id + '_signal']) {
                    const signalSeries = workspaceChart.addLineSeries({
                        color: '#FF6D00',
                        lineWidth: ind.display.lineWidth,
                        lineStyle: lineStyleMap[ind.display.lineStyle] || LightweightCharts.LineStyle.Solid,
                        title: `${ind.type}_Signal`,
                        visible: ind.display.show,
                        priceScaleId: 'macd', // Same scale as MACD
                        priceFormat: {
                            type: 'price',
                            precision: 4,
                            minMove: 0.0001
                        }
                    });
                    signalSeries.setData(data.indicators[ind.id + '_signal']);
                    workspaceIndicatorSeries[ind.id + '_signal'] = signalSeries;
                }
                
            } else if (ind.type === 'BB') {
                // Upper band
                if (data.indicators[ind.id + '_upper']) {
                    const upperSeries = workspaceChart.addLineSeries({
                        color: ind.display.color,
                        lineWidth: ind.display.lineWidth,
                        lineStyle: lineStyleMap[ind.display.lineStyle] || LightweightCharts.LineStyle.Solid,
                        title: `${ind.type}_Upper`,
                        visible: ind.display.show,
                        priceScaleId: 'right', // Use main price scale
                        priceFormat: {
                            type: 'price',
                            precision: 2,
                            minMove: 0.01
                        }
                    });
                    upperSeries.setData(data.indicators[ind.id + '_upper']);
                    workspaceIndicatorSeries[ind.id + '_upper'] = upperSeries;
                }
                
                // Middle band
                if (data.indicators[ind.id + '_middle']) {
                    const middleSeries = workspaceChart.addLineSeries({
                        color: ind.display.color,
                        lineWidth: ind.display.lineWidth,
                        lineStyle: LightweightCharts.LineStyle.Dashed,
                        title: `${ind.type}_Middle`,
                        visible: ind.display.show,
                        priceScaleId: 'right', // Use main price scale
                        priceFormat: {
                            type: 'price',
                            precision: 2,
                            minMove: 0.01
                        }
                    });
                    middleSeries.setData(data.indicators[ind.id + '_middle']);
                    workspaceIndicatorSeries[ind.id + '_middle'] = middleSeries;
                }
                
                // Lower band
                if (data.indicators[ind.id + '_lower']) {
                    const lowerSeries = workspaceChart.addLineSeries({
                        color: ind.display.color,
                        lineWidth: ind.display.lineWidth,
                        lineStyle: lineStyleMap[ind.display.lineStyle] || LightweightCharts.LineStyle.Solid,
                        title: `${ind.type}_Lower`,
                        visible: ind.display.show,
                        priceScaleId: 'right', // Use main price scale
                        priceFormat: {
                            type: 'price',
                            precision: 2,
                            minMove: 0.01
                        }
                    });
                    lowerSeries.setData(data.indicators[ind.id + '_lower']);
                    workspaceIndicatorSeries[ind.id + '_lower'] = lowerSeries;
                }
                
            } else if (ind.type === 'RSI' || ind.type === 'ADX') {
                // RSI and ADX use separate scale (0-100)
                if (data.indicators[ind.id]) {
                    const series = workspaceChart.addLineSeries({
                        color: ind.display.color,
                        lineWidth: ind.display.lineWidth,
                        lineStyle: lineStyleMap[ind.display.lineStyle] || LightweightCharts.LineStyle.Solid,
                        title: `${ind.type}(${Object.values(ind.params).join(',')})`,
                        visible: ind.display.show,
                        priceScaleId: 'rsi', // Separate scale for oscillators
                        priceFormat: {
                            type: 'price',
                            precision: 2,
                            minMove: 0.01
                        }
                    });
                    series.setData(data.indicators[ind.id]);
                    workspaceIndicatorSeries[ind.id] = series;
                    console.log(`✅ Rendered ${ind.type} with ${data.indicators[ind.id].length} data points on 'rsi' scale`);
                }
            } else {
                // EMA, SMA, WMA - use main price scale
                if (data.indicators[ind.id]) {
                    const series = workspaceChart.addLineSeries({
                        color: ind.display.color,
                        lineWidth: ind.display.lineWidth,
                        lineStyle: lineStyleMap[ind.display.lineStyle] || LightweightCharts.LineStyle.Solid,
                        title: `${ind.type}(${Object.values(ind.params).join(',')})`,
                        visible: ind.display.show,
                        priceScaleId: 'right', // Use main price scale
                        priceFormat: {
                            type: 'price',
                            precision: 2,
                            minMove: 0.01
                        }
                    });
                    series.setData(data.indicators[ind.id]);
                    workspaceIndicatorSeries[ind.id] = series;
                    console.log(`✅ Rendered ${ind.type} with ${data.indicators[ind.id].length} data points on 'right' scale`);
                }
            }
        });
        
        console.log('✅ Indicators rendered on workspace chart');
    })
    .catch(error => {
        console.error('❌ Error calculating indicators:', error);
    });
}

// ==================== WORKSPACE UI NAMESPACE EXPORTS ====================
WorkspaceUI.calculateAndRenderIndicators = calculateAndRenderIndicators;

// Export for global access (backward compatibility)
window.calculateAndRenderIndicators = calculateAndRenderIndicators;
window.WorkspaceUI = WorkspaceUI;

