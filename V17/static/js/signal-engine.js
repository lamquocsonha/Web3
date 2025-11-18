/**
 * Signal Generation Engine
 * Shared between workspace.js and chart.js
 */

// EMA Cache
const emaCache = {};
window.emaCache = emaCache;

// Generate signals based on strategy conditions
function generateStrategySignals(candleData, config) {
    if (!config || !config.entry_conditions) {
        console.log('⚠️ No strategy config available');
        return { buySignals: [], shortSignals: [] };
    }
    
    console.log('📊 Generating signals with config:', config.name || 'Unknown');
    console.log(`  - Indicators: ${config.indicators?.length || 0}`);
    console.log(`  - Long conditions: ${config.entry_conditions.long?.length || 0}`);
    console.log(`  - Short conditions: ${config.entry_conditions.short?.length || 0}`);
    
    const buySignals = [];
    const shortSignals = [];
    
    // Process each candle
    candleData.forEach((candle, index) => {
        if (index === 0) return; // Skip first candle
        
        const prevCandle = candleData[index - 1];
        
        // Check long entry conditions
        if (config.entry_conditions.long) {
            config.entry_conditions.long.forEach(signal => {
                if (evaluateSignalConditions(signal, candle, prevCandle, candleData, index, config)) {
                    buySignals.push({
                        time: candle.time,
                        signalName: signal.name,
                        price: candle.close
                    });
                }
            });
        }
        
        // Check short entry conditions
        if (config.entry_conditions.short) {
            config.entry_conditions.short.forEach(signal => {
                if (evaluateSignalConditions(signal, candle, prevCandle, candleData, index, config)) {
                    shortSignals.push({
                        time: candle.time,
                        signalName: signal.name,
                        price: candle.close
                    });
                }
            });
        }
    });
    
    console.log(`📈 Generated ${buySignals.length} buy signals and ${shortSignals.length} short signals`);
    
    return { buySignals, shortSignals };
}

// Evaluate signal conditions
function evaluateSignalConditions(signal, candle, prevCandle, allCandles, currentIndex, config) {
    // Support both formats:
    // 1. Old format: signal.condition = "close > ma1 AND rsi < 30" (string)
    // 2. New format: signal.conditions = [{left, operator, right, logic}] (array)
    
    // Check for old format (condition string)
    if (signal.condition && typeof signal.condition === 'string') {
        return evaluateConditionString(signal.condition, candle, prevCandle, allCandles, currentIndex, config);
    }
    
    // Check for new format (conditions array)
    if (!signal.conditions || signal.conditions.length === 0) return false;
    
    let result = true;
    let currentLogic = 'AND';
    
    for (let i = 0; i < signal.conditions.length; i++) {
        const cond = signal.conditions[i];
        const condResult = evaluateSingleCondition(cond, candle, prevCandle, allCandles, currentIndex, config);
        
        if (i === 0) {
            result = condResult;
        } else {
            if (currentLogic === 'AND') {
                result = result && condResult;
            } else {
                result = result || condResult;
            }
        }
        
        currentLogic = cond.logic;
    }
    
    return result;
}

// Evaluate condition string (old format support)
function evaluateConditionString(conditionStr, candle, prevCandle, allCandles, currentIndex, config) {
    // Simple parser for conditions like "close > ma1 AND rsi < 30"
    // This is a basic implementation - can be enhanced
    
    try {
        // Split by AND/OR
        const parts = conditionStr.split(/\s+(AND|OR)\s+/i);
        
        let result = true;
        let currentLogic = 'AND';
        
        for (let i = 0; i < parts.length; i++) {
            const part = parts[i].trim();
            
            // Skip logic operators
            if (part.toUpperCase() === 'AND' || part.toUpperCase() === 'OR') {
                currentLogic = part.toUpperCase();
                continue;
            }
            
            // Parse single condition
            const condResult = parseSingleCondition(part, candle, prevCandle, allCandles, currentIndex, config);
            
            if (i === 0) {
                result = condResult;
            } else {
                if (currentLogic === 'AND') {
                    result = result && condResult;
                } else {
                    result = result || condResult;
                }
            }
        }
        
        return result;
    } catch (error) {
        console.error('Error parsing condition string:', conditionStr, error);
        return false;
    }
}

// Parse single condition from string
function parseSingleCondition(condStr, candle, prevCandle, allCandles, currentIndex, config) {
    // Handle cross_above, cross_below
    if (condStr.includes('cross_above')) {
        const match = condStr.match(/(.+?)\s*cross_above\s*(.+)/i);
        if (match) {
            const left = match[1].trim();
            const right = match[2].trim();
            return evaluateSingleCondition({
                left: left,
                operator: 'cross_above',
                right: right,
                leftOffset: 0,
                rightOffset: 0
            }, candle, prevCandle, allCandles, currentIndex, config);
        }
    }
    
    if (condStr.includes('cross_below')) {
        const match = condStr.match(/(.+?)\s*cross_below\s*(.+)/i);
        if (match) {
            const left = match[1].trim();
            const right = match[2].trim();
            return evaluateSingleCondition({
                left: left,
                operator: 'cross_below',
                right: right,
                leftOffset: 0,
                rightOffset: 0
            }, candle, prevCandle, allCandles, currentIndex, config);
        }
    }
    
    // Handle comparison operators
    const operators = ['>=', '<=', '>', '<', '==', '!='];
    for (const op of operators) {
        if (condStr.includes(op)) {
            const parts = condStr.split(op);
            if (parts.length === 2) {
                const left = parts[0].trim();
                const right = parts[1].trim();
                
                return evaluateSingleCondition({
                    left: left,
                    operator: op,
                    right: isNaN(right) ? right : parseFloat(right),
                    leftOffset: 0,
                    rightOffset: 0
                }, candle, prevCandle, allCandles, currentIndex, config);
            }
        }
    }
    
    console.warn('Could not parse condition:', condStr);
    return false;
}

// Evaluate single condition
function evaluateSingleCondition(cond, candle, prevCandle, allCandles, currentIndex, config) {
    // Get left value with offset
    const leftOffset = cond.leftOffset || 0;
    const leftIndex = currentIndex + leftOffset; // leftOffset is negative, so this goes back
    if (leftIndex < 0 || leftIndex >= allCandles.length) return false;
    
    const leftCandle = allCandles[leftIndex];
    const leftPrevCandle = leftIndex > 0 ? allCandles[leftIndex - 1] : leftCandle;
    const leftValue = getValueFromOperand(cond.left, leftCandle, leftPrevCandle, allCandles, leftIndex, config);
    
    // Get right value with offset
    let rightValue;
    if (typeof cond.right === 'number') {
        rightValue = cond.right;
    } else {
        const rightOffset = cond.rightOffset || 0;
        const rightIndex = currentIndex + rightOffset;
        if (rightIndex < 0 || rightIndex >= allCandles.length) return false;
        
        const rightCandle = allCandles[rightIndex];
        const rightPrevCandle = rightIndex > 0 ? allCandles[rightIndex - 1] : rightCandle;
        rightValue = getValueFromOperand(cond.right, rightCandle, rightPrevCandle, allCandles, rightIndex, config);
    }
    
    if (leftValue === null || rightValue === null) return false;
    
    // Evaluate operator
    switch (cond.operator) {
        case '>': return leftValue > rightValue;
        case '<': return leftValue < rightValue;
        case '>=': return leftValue >= rightValue;
        case '<=': return leftValue <= rightValue;
        case '==': return Math.abs(leftValue - rightValue) < 0.0001;
        case '!=': return Math.abs(leftValue - rightValue) >= 0.0001;
        case 'is_true': return leftValue === 1 || leftValue === true;
        case 'is_false': return leftValue === 0 || leftValue === false;
        case 'cross_above':
            if (leftIndex < 1) return false;
            const prevLeft = getValueFromOperand(cond.left, leftPrevCandle, allCandles[leftIndex - 2] || leftPrevCandle, allCandles, leftIndex - 1, config);
            const prevRight = typeof cond.right === 'number' ? 
                cond.right : 
                getValueFromOperand(cond.right, allCandles[leftIndex - 1], allCandles[leftIndex - 2] || allCandles[leftIndex - 1], allCandles, leftIndex - 1, config);
            if (prevLeft === null || prevRight === null) return false;
            return prevLeft <= prevRight && leftValue > rightValue;
        case 'cross_below':
            if (leftIndex < 1) return false;
            const prevLeft2 = getValueFromOperand(cond.left, leftPrevCandle, allCandles[leftIndex - 2] || leftPrevCandle, allCandles, leftIndex - 1, config);
            const prevRight2 = typeof cond.right === 'number' ? 
                cond.right : 
                getValueFromOperand(cond.right, allCandles[leftIndex - 1], allCandles[leftIndex - 2] || allCandles[leftIndex - 1], allCandles, leftIndex - 1, config);
            if (prevLeft2 === null || prevRight2 === null) return false;
            return prevLeft2 >= prevRight2 && leftValue < rightValue;
        default: return false;
    }
}

// Get value from operand
function getValueFromOperand(operand, candle, prevCandle, allCandles, currentIndex, config) {
    switch (operand) {
        case 'open': return candle.open;
        case 'high': return candle.high;
        case 'low': return candle.low;
        case 'close': return candle.close;
    }
    
    const indicator = config.indicators.find(ind => ind.id === operand);
    if (!indicator) {
        console.warn(`Indicator ${operand} not found`);
        return null;
    }
    
    switch (indicator.type) {
        case 'EMA':
            return calculateEMA(allCandles, currentIndex, indicator.params.period);
        case 'SMA':
            return calculateSMA(allCandles, currentIndex, indicator.params.period);
        case 'RSI':
            return calculateRSI(allCandles, currentIndex, indicator.params.period);
        case 'ADX':
            return calculateADX(allCandles, currentIndex, indicator.params.period);
        // Trend Indicators
        case 'MAuptrend':
            return calculateMAuptrend(allCandles, currentIndex);
        case 'MAdowntrend':
            return calculateMAdowntrend(allCandles, currentIndex);
        case 'Alluptrend':
            return calculateAlluptrend(allCandles, currentIndex);
        case 'Alldowntrend':
            return calculateAlldowntrend(allCandles, currentIndex);
        case 'SlopeMA1':
            return calculateSlopeMA1(allCandles, currentIndex);
        case 'GMA12':
            return calculateGMA12(allCandles, currentIndex);
        case 'GMA23':
            return calculateGMA23(allCandles, currentIndex);
        case 'GMA45':
            return calculateGMA45(allCandles, currentIndex);
        case 'MArange':
            return calculateMArange(allCandles, currentIndex);
        case 'MA7range':
            return calculateMA7range(allCandles, currentIndex);
        // Pivot Points
        case 'PP':
            return calculatePivotPoint(allCandles, currentIndex, 'PP');
        case 'R1':
            return calculatePivotPoint(allCandles, currentIndex, 'R1');
        case 'R2':
            return calculatePivotPoint(allCandles, currentIndex, 'R2');
        case 'R3':
            return calculatePivotPoint(allCandles, currentIndex, 'R3');
        case 'S1':
            return calculatePivotPoint(allCandles, currentIndex, 'S1');
        case 'S2':
            return calculatePivotPoint(allCandles, currentIndex, 'S2');
        case 'S3':
            return calculatePivotPoint(allCandles, currentIndex, 'S3');
        // Candlestick patterns
        case 'Green':
            return candle.close >= candle.open ? 1 : 0;
        case 'Red':
            return candle.close < candle.open ? 1 : 0;
        case 'Length':
            return candle.high - candle.low;
        // Custom AFL indicators
        case 'HHVsinceopen':
            return calculateHHVsinceopen(allCandles, currentIndex, config);
        case 'LLVsinceopen':
            return calculateLLVsinceopen(allCandles, currentIndex, config);
        case 'HHVsincebuy':
            return calculateHHVsincebuy(allCandles, currentIndex);
        case 'LLVsinceshort':
            return calculateLLVsinceshort(allCandles, currentIndex);
        case 'HHVresline':
            return calculateHHVsinceopen(allCandles, currentIndex, config) - 0.5;
        case 'LLVresline':
            return calculateLLVsinceopen(allCandles, currentIndex, config) + 0.5;
        case 'HHVresline1':
            return calculateHHVsinceopen(allCandles, currentIndex, config) - 1.0; // -0.5 -0.5
        case 'LLVresline1':
            return calculateLLVsinceopen(allCandles, currentIndex, config) + 1.0; // +0.5 +0.5
        case 'HHVresline2':
            return calculateHHVsinceopen(allCandles, currentIndex, config) - 1.5; // -0.5 -0.5 -0.5
        case 'LLVresline2':
            return calculateLLVsinceopen(allCandles, currentIndex, config) + 1.5; // +0.5 +0.5 +0.5
        case 'HHVresline3':
            return calculateHHVsinceopen(allCandles, currentIndex, config) - 2.0; // -0.5 -0.5 -0.5 -0.5
        case 'LLVresline3':
            return calculateLLVsinceopen(allCandles, currentIndex, config) + 2.0; // +0.5 +0.5 +0.5 +0.5
        case 'HHVresline4':
            return calculateHHVsinceopen(allCandles, currentIndex, config) - 2.5; // -0.5 x5
        case 'LLVresline4':
            return calculateLLVsinceopen(allCandles, currentIndex, config) + 2.5; // +0.5 x5
        case 'resHL':
            return calculateResHL(allCandles, currentIndex, config);
        case 'AvgHL':
            return calculateAvgHL(allCandles, currentIndex, config);
        case 'RealtimeOH':
            return calculateRealtimeOH(allCandles, currentIndex, config);
        case 'RealtimeOL':
            return calculateRealtimeOL(allCandles, currentIndex, config);
        case 'RangetoHHV':
            return calculateRangetoHHV(allCandles, currentIndex, config);
        case 'RangetoLLV':
            return calculateRangetoLLV(allCandles, currentIndex, config);
        case 'Baseprice':
            return calculateBaseprice(allCandles, currentIndex, config);
        default:
            console.warn(`Indicator ${indicator.type} not implemented`);
            return candle.close;
    }
}

// Calculate EMA with caching
function calculateEMA(candles, currentIndex, period) {
    if (currentIndex < period - 1) return null;
    
    const cacheKey = `${period}_${currentIndex}`;
    if (emaCache[cacheKey] !== undefined) {
        return emaCache[cacheKey];
    }
    
    const multiplier = 2 / (period + 1);
    
    if (currentIndex === period - 1) {
        let sum = 0;
        for (let i = 0; i < period; i++) {
            sum += candles[i].close;
        }
        const result = sum / period;
        emaCache[cacheKey] = result;
        return result;
    }
    
    const previousEMA = calculateEMA(candles, currentIndex - 1, period);
    if (previousEMA === null) return null;
    
    const result = (candles[currentIndex].close - previousEMA) * multiplier + previousEMA;
    emaCache[cacheKey] = result;
    return result;
}

// Calculate SMA
function calculateSMA(candles, currentIndex, period) {
    if (currentIndex < period - 1) return null;
    
    let sum = 0;
    for (let i = currentIndex - period + 1; i <= currentIndex; i++) {
        sum += candles[i].close;
    }
    return sum / period;
}

// Calculate RSI
function calculateRSI(candles, currentIndex, period) {
    if (currentIndex < period) return null;
    
    let gains = 0;
    let losses = 0;
    
    for (let i = currentIndex - period + 1; i <= currentIndex; i++) {
        const change = candles[i].close - candles[i - 1].close;
        if (change > 0) {
            gains += change;
        } else {
            losses -= change;
        }
    }
    
    const avgGain = gains / period;
    const avgLoss = losses / period;
    
    if (avgLoss === 0) return 100;
    
    const rs = avgGain / avgLoss;
    return 100 - (100 / (1 + rs));
}

// Calculate ADX (Average Directional Index)
function calculateADX(candles, currentIndex, period = 14) {
    if (currentIndex < period + 1) return null;
    
    let plusDM = 0;
    let minusDM = 0;
    let tr = 0;
    
    // Calculate +DM, -DM, and TR over period
    for (let i = currentIndex - period + 1; i <= currentIndex; i++) {
        const highDiff = candles[i].high - candles[i - 1].high;
        const lowDiff = candles[i - 1].low - candles[i].low;
        
        // +DM and -DM
        if (highDiff > lowDiff && highDiff > 0) {
            plusDM += highDiff;
        }
        if (lowDiff > highDiff && lowDiff > 0) {
            minusDM += lowDiff;
        }
        
        // True Range
        const high_low = candles[i].high - candles[i].low;
        const high_close = Math.abs(candles[i].high - candles[i - 1].close);
        const low_close = Math.abs(candles[i].low - candles[i - 1].close);
        tr += Math.max(high_low, high_close, low_close);
    }
    
    // Calculate +DI and -DI
    const plusDI = (plusDM / tr) * 100;
    const minusDI = (minusDM / tr) * 100;
    
    // Calculate DX
    const diDiff = Math.abs(plusDI - minusDI);
    const diSum = plusDI + minusDI;
    
    if (diSum === 0) return 0;
    
    const dx = (diDiff / diSum) * 100;
    
    // ADX is smoothed DX (simplified version)
    return dx;
}

// ============================================
//         TREND INDICATORS (AFL)
// ============================================
// MA1=5, MA2=19, MA3=44, MA4=99, MA5=245, MA7=dynamic

// Calculate MA7 dynamic: IIf(C>1600, EMA(1050), IIf(C>1400, EMA(1020), IIf(C>1000, EMA(1000), EMA(900))))
function calculateMA7(candles, currentIndex) {
    const close = candles[currentIndex].close;
    let period;
    
    if (close > 1600) period = 1050;
    else if (close > 1400) period = 1020;
    else if (close > 1000) period = 1000;
    else period = 900;
    
    return calculateEMA(candles, currentIndex, period);
}

// Calculate MAuptrend: C > MA2 AND MA2 > MA3 AND MA3 > MA5 AND MA4 > MA5
function calculateMAuptrend(candles, currentIndex) {
    const close = candles[currentIndex].close;
    const ma2 = calculateEMA(candles, currentIndex, 19);
    const ma3 = calculateEMA(candles, currentIndex, 44);
    const ma4 = calculateEMA(candles, currentIndex, 99);
    const ma5 = calculateEMA(candles, currentIndex, 245);
    
    if (ma2 === null || ma3 === null || ma4 === null || ma5 === null) return 0;
    
    return (close > ma2 && ma2 > ma3 && ma3 > ma5 && ma4 > ma5) ? 1 : 0;
}

// Calculate MAdowntrend: C < MA2 AND MA2 < MA3 AND MA3 < MA5 AND MA4 < MA5
function calculateMAdowntrend(candles, currentIndex) {
    const close = candles[currentIndex].close;
    const ma2 = calculateEMA(candles, currentIndex, 19);
    const ma3 = calculateEMA(candles, currentIndex, 44);
    const ma4 = calculateEMA(candles, currentIndex, 99);
    const ma5 = calculateEMA(candles, currentIndex, 245);
    
    if (ma2 === null || ma3 === null || ma4 === null || ma5 === null) return 0;
    
    return (close < ma2 && ma2 < ma3 && ma3 < ma5 && ma4 < ma5) ? 1 : 0;
}

// Calculate Alluptrend: MA2 > MA3 AND MA3 > MA4 AND MA4 > MA5 AND C > MA7
function calculateAlluptrend(candles, currentIndex) {
    const close = candles[currentIndex].close;
    const ma2 = calculateEMA(candles, currentIndex, 19);
    const ma3 = calculateEMA(candles, currentIndex, 44);
    const ma4 = calculateEMA(candles, currentIndex, 99);
    const ma5 = calculateEMA(candles, currentIndex, 245);
    const ma7 = calculateMA7(candles, currentIndex);
    
    if (ma2 === null || ma3 === null || ma4 === null || ma5 === null || ma7 === null) return 0;
    
    return (ma2 > ma3 && ma3 > ma4 && ma4 > ma5 && close > ma7) ? 1 : 0;
}

// Calculate Alldowntrend: MA2 < MA3 AND MA3 < MA4 AND MA4 < MA5 AND C < MA7
function calculateAlldowntrend(candles, currentIndex) {
    const close = candles[currentIndex].close;
    const ma2 = calculateEMA(candles, currentIndex, 19);
    const ma3 = calculateEMA(candles, currentIndex, 44);
    const ma4 = calculateEMA(candles, currentIndex, 99);
    const ma5 = calculateEMA(candles, currentIndex, 245);
    const ma7 = calculateMA7(candles, currentIndex);
    
    if (ma2 === null || ma3 === null || ma4 === null || ma5 === null || ma7 === null) return 0;
    
    return (ma2 < ma3 && ma3 < ma4 && ma4 < ma5 && close < ma7) ? 1 : 0;
}

// Calculate SlopeMA1: MA1 - Ref(MA1,-1)
function calculateSlopeMA1(candles, currentIndex) {
    if (currentIndex < 1) return 0;
    
    const ma1 = calculateEMA(candles, currentIndex, 5);
    const ma1_prev = calculateEMA(candles, currentIndex - 1, 5);
    
    if (ma1 === null || ma1_prev === null) return 0;
    
    return ma1 - ma1_prev;
}

// Calculate GMA12: (MA1 + MA2) / 2
function calculateGMA12(candles, currentIndex) {
    const ma1 = calculateEMA(candles, currentIndex, 5);
    const ma2 = calculateEMA(candles, currentIndex, 19);
    
    if (ma1 === null || ma2 === null) return null;
    
    return (ma1 + ma2) / 2;
}

// Calculate GMA23: (MA2 + MA3) / 2
function calculateGMA23(candles, currentIndex) {
    const ma2 = calculateEMA(candles, currentIndex, 19);
    const ma3 = calculateEMA(candles, currentIndex, 44);
    
    if (ma2 === null || ma3 === null) return null;
    
    return (ma2 + ma3) / 2;
}

// Calculate GMA45: (MA4 + MA5) / 2
function calculateGMA45(candles, currentIndex) {
    const ma4 = calculateEMA(candles, currentIndex, 99);
    const ma5 = calculateEMA(candles, currentIndex, 245);
    
    if (ma4 === null || ma5 === null) return null;
    
    return (ma4 + ma5) / 2;
}

// Calculate MArange: Max(MA5, MA4, MA3, MA2) - Min(MA5, MA4, MA3, MA2)
function calculateMArange(candles, currentIndex) {
    const ma2 = calculateEMA(candles, currentIndex, 19);
    const ma3 = calculateEMA(candles, currentIndex, 44);
    const ma4 = calculateEMA(candles, currentIndex, 99);
    const ma5 = calculateEMA(candles, currentIndex, 245);
    
    if (ma2 === null || ma3 === null || ma4 === null || ma5 === null) return null;
    
    const maxMA = Math.max(ma5, ma4, ma3, ma2);
    const minMA = Math.min(ma5, ma4, ma3, ma2);
    
    return maxMA - minMA;
}

// Calculate MA7range: abs(MA7 - C)
function calculateMA7range(candles, currentIndex) {
    const close = candles[currentIndex].close;
    const ma7 = calculateMA7(candles, currentIndex);
    
    if (ma7 === null) return null;
    
    return Math.abs(ma7 - close);
}

// Calculate HHVsinceopen - Highest high since session open (base_time from config)
function calculateHHVsinceopen(candles, currentIndex, config) {
    const currentCandle = candles[currentIndex];
    const currentTime = new Date(currentCandle.time * 1000);

    // Get base time from config (default 09:00 if not set)
    const baseTimeStr = config?.exit_rules?.base_time || '09:00';
    const [baseHour, baseMinute] = baseTimeStr.split(':').map(Number);

    // Get current date (year, month, day) to ensure we only look at same day
    const currentYear = currentTime.getFullYear();
    const currentMonth = currentTime.getMonth();
    const currentDay = currentTime.getDate();

    // Find session open (base_time) on the SAME DAY
    let sessionStartIndex = currentIndex;
    for (let i = currentIndex; i >= 0; i--) {
        const time = new Date(candles[i].time * 1000);
        const year = time.getFullYear();
        const month = time.getMonth();
        const day = time.getDate();
        const hour = time.getHours();
        const minute = time.getMinutes();

        // If we've gone to a different day, stop searching
        if (year !== currentYear || month !== currentMonth || day !== currentDay) {
            // Use the first candle of current day as session start
            sessionStartIndex = i + 1;
            break;
        }

        // If we hit base_time on same day, this is session start
        if (hour === baseHour && minute === baseMinute) {
            sessionStartIndex = i;
            break;
        }

        // If we go before base_time on same day, next candle is session start
        if (hour < baseHour || (hour === baseHour && minute < baseMinute)) {
            sessionStartIndex = i + 1;
            break;
        }
    }

    // Find highest high from session start to current
    let hhv = candles[sessionStartIndex].high;
    for (let i = sessionStartIndex; i <= currentIndex; i++) {
        if (candles[i].high > hhv) {
            hhv = candles[i].high;
        }
    }

    return hhv;
}

// Calculate LLVsinceopen - Lowest low since session open (base_time from config)
function calculateLLVsinceopen(candles, currentIndex, config) {
    const currentCandle = candles[currentIndex];
    const currentTime = new Date(currentCandle.time * 1000);

    // Get base time from config (default 09:00 if not set)
    const baseTimeStr = config?.exit_rules?.base_time || '09:00';
    const [baseHour, baseMinute] = baseTimeStr.split(':').map(Number);

    // Get current date (year, month, day) to ensure we only look at same day
    const currentYear = currentTime.getFullYear();
    const currentMonth = currentTime.getMonth();
    const currentDay = currentTime.getDate();

    // Find session open (base_time) on the SAME DAY
    let sessionStartIndex = currentIndex;
    for (let i = currentIndex; i >= 0; i--) {
        const time = new Date(candles[i].time * 1000);
        const year = time.getFullYear();
        const month = time.getMonth();
        const day = time.getDate();
        const hour = time.getHours();
        const minute = time.getMinutes();

        // If we've gone to a different day, stop searching
        if (year !== currentYear || month !== currentMonth || day !== currentDay) {
            // Use the first candle of current day as session start
            sessionStartIndex = i + 1;
            break;
        }

        // If we hit base_time on same day, this is session start
        if (hour === baseHour && minute === baseMinute) {
            sessionStartIndex = i;
            break;
        }

        // If we go before base_time on same day, next candle is session start
        if (hour < baseHour || (hour === baseHour && minute < baseMinute)) {
            sessionStartIndex = i + 1;
            break;
        }
    }

    // Find lowest low from session start to current
    let llv = candles[sessionStartIndex].low;
    for (let i = sessionStartIndex; i <= currentIndex; i++) {
        if (candles[i].low < llv) {
            llv = candles[i].low;
        }
    }
    
    return llv;
}

// Calculate resHL - abs(HHVsinceopen - LLVsinceopen)
function calculateResHL(candles, currentIndex, config) {
    const hhv = calculateHHVsinceopen(candles, currentIndex, config);
    const llv = calculateLLVsinceopen(candles, currentIndex, config);

    if (hhv === null || llv === null) return null;

    return Math.abs(hhv - llv);
}

// Calculate AvgHL - (HHVsinceopen + LLVsinceopen) / 2
function calculateAvgHL(candles, currentIndex, config) {
    const hhv = calculateHHVsinceopen(candles, currentIndex, config);
    const llv = calculateLLVsinceopen(candles, currentIndex, config);

    if (hhv === null || llv === null) return null;

    return (hhv + llv) / 2;
}

// Calculate Baseprice - Open price at base_time
function calculateBaseprice(candles, currentIndex, config) {
    // Get base time from config (default 09:00 if not set)
    const baseTimeStr = config?.exit_rules?.base_time || '09:00';
    const [baseHour, baseMinute] = baseTimeStr.split(':').map(Number);

    const currentCandle = candles[currentIndex];
    const currentTime = new Date(currentCandle.time * 1000);

    // Get current date to ensure we only look at same day
    const currentYear = currentTime.getFullYear();
    const currentMonth = currentTime.getMonth();
    const currentDay = currentTime.getDate();

    // Find base_time candle on SAME DAY
    for (let i = currentIndex; i >= 0; i--) {
        const time = new Date(candles[i].time * 1000);
        const year = time.getFullYear();
        const month = time.getMonth();
        const day = time.getDate();
        const hour = time.getHours();
        const minute = time.getMinutes();

        // If we've gone to a different day, stop
        if (year !== currentYear || month !== currentMonth || day !== currentDay) {
            break;
        }

        // If we hit base_time on same day
        if (hour === baseHour && minute === baseMinute) {
            return candles[i].open;
        }

        // Stop if we go before base_time
        if (hour < baseHour || (hour === baseHour && minute < baseMinute)) {
            break;
        }
    }

    // If not found, use first candle of current day
    // Find first candle of same day
    for (let i = currentIndex; i >= 0; i--) {
        const time = new Date(candles[i].time * 1000);
        const year = time.getFullYear();
        const month = time.getMonth();
        const day = time.getDate();

        if (year !== currentYear || month !== currentMonth || day !== currentDay) {
            // candles[i+1] is first candle of current day
            return candles[i + 1]?.open || candles[0].open;
        }
    }

    // If all candles are same day, use first candle
    return candles[0].open;
}

// Calculate Pivot Points (PP, R1-R3, S1-S3)
// Formula from AFL:
// PP = (DayH + DayL + DayC) / 3
// R1 = (PP * 2) - DayL
// S1 = (PP * 2) - DayH
// R2 = PP + R1 - S1
// S2 = PP - R1 + S1
// R3 = PP + R2 - S1
// S3 = PP - R2 + S1
function calculatePivotPoint(candles, currentIndex, type) {
    // Find previous day's high, low, close
    const currentTime = new Date(candles[currentIndex].time * 1000);
    const currentDay = currentTime.getDate();
    
    let dayH = null, dayL = null, dayC = null;
    
    // Look back to find previous day's data
    for (let i = currentIndex - 1; i >= 0; i--) {
        const time = new Date(candles[i].time * 1000);
        const day = time.getDate();
        
        if (day !== currentDay) {
            // Found previous day, get its HLC
            let prevDayCandles = [];
            for (let j = i; j >= 0; j--) {
                const t = new Date(candles[j].time * 1000);
                if (t.getDate() === day) {
                    prevDayCandles.push(candles[j]);
                } else {
                    break;
                }
            }
            
            if (prevDayCandles.length > 0) {
                dayH = Math.max(...prevDayCandles.map(c => c.high));
                dayL = Math.min(...prevDayCandles.map(c => c.low));
                dayC = prevDayCandles[0].close; // Last candle of previous day
            }
            break;
        }
    }
    
    if (dayH === null || dayL === null || dayC === null) {
        return null;
    }
    
    // Calculate pivot point
    const PP = (dayH + dayL + dayC) / 3;
    const R1 = (PP * 2) - dayL;
    const S1 = (PP * 2) - dayH;
    const R2 = PP + R1 - S1;
    const S2 = PP - R1 + S1;
    const R3 = PP + R2 - S1;
    const S3 = PP - R2 + S1;
    
    switch (type) {
        case 'PP': return PP;
        case 'R1': return R1;
        case 'R2': return R2;
        case 'R3': return R3;
        case 'S1': return S1;
        case 'S2': return S2;
        case 'S3': return S3;
        default: return null;
    }
}

// Calculate RealtimeOH - HHVsinceopen - Baseprice
function calculateRealtimeOH(candles, currentIndex, config) {
    const hhv = calculateHHVsinceopen(candles, currentIndex, config);
    const baseprice = calculateBaseprice(candles, currentIndex, config);

    if (hhv === null || baseprice === null) return null;

    return hhv - baseprice;
}

// Calculate RealtimeOL - Baseprice - LLVsinceopen
function calculateRealtimeOL(candles, currentIndex, config) {
    const baseprice = calculateBaseprice(candles, currentIndex, config);
    const llv = calculateLLVsinceopen(candles, currentIndex, config);

    if (baseprice === null || llv === null) return null;

    return baseprice - llv;
}

// Calculate RangetoHHV - HHVsinceopen - Close
function calculateRangetoHHV(candles, currentIndex, config) {
    const hhv = calculateHHVsinceopen(candles, currentIndex, config);
    const close = candles[currentIndex].close;

    if (hhv === null) return null;

    return hhv - close;
}

// Calculate RangetoLLV - Close - LLVsinceopen
function calculateRangetoLLV(candles, currentIndex, config) {
    const llv = calculateLLVsinceopen(candles, currentIndex, config);
    const close = candles[currentIndex].close;

    if (llv === null) return null;

    return close - llv;
}

// Calculate HHVsincebuy - Highest High since Long entry
function calculateHHVsincebuy(candles, currentIndex) {
    // Get position info from trading engine
    if (typeof tradingEngine === 'undefined' || !tradingEngine.positions) {
        return null;
    }

    const pos = tradingEngine.positions;

    // Only valid when in LONG position
    if (pos.currentStatus !== 'LONG' || pos.hhvSinceEntry === null) {
        return null;
    }

    return pos.hhvSinceEntry;
}

// Calculate LLVsinceshort - Lowest Low since Short entry
function calculateLLVsinceshort(candles, currentIndex) {
    // Get position info from trading engine
    if (typeof tradingEngine === 'undefined' || !tradingEngine.positions) {
        return null;
    }

    const pos = tradingEngine.positions;

    // Only valid when in SHORT position
    if (pos.currentStatus !== 'SHORT' || pos.llvSinceEntry === null) {
        return null;
    }

    return pos.llvSinceEntry;
}

// Expose globally
window.generateStrategySignals = generateStrategySignals;
window.emaCache = emaCache;

console.log('✅ Signal generation engine loaded');
