// Backtest Module
let currentCSVFile = null;
let currentStrategy = null;
let equityChart = null;
let tradesData = [];
let lastBacktestResult = null; // Store last backtest result for PDF export
let selectedTimeframe = '1m'; // Selected timeframe for uploaded data

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadUploadedFiles();
    loadStrategies();
    setupEventListeners();
    restoreBacktestState();
});

function setupEventListeners() {
    // Button to trigger timeframe modal first (like index/strategy pages)
    document.getElementById('btnChooseFile').addEventListener('click', function() {
        showTimeframeModalForBacktest();
    });

    // CSV file upload (will be triggered after timeframe selection)
    document.getElementById('csvFile').addEventListener('change', handleCSVUpload);

    // Strategy selection
    document.getElementById('strategySelect').addEventListener('change', function() {
        checkReadyToBacktest();
        saveBacktestState();
    });

    // Run backtest button
    document.getElementById('runBacktest').addEventListener('click', function(e) {
        if (this.disabled) {
            e.preventDefault();
            const strategySelected = document.getElementById('strategySelect').value;
            if (!currentCSVFile && !strategySelected) {
                showNotification('⚠️ Vui lòng chọn CSV file và Strategy', 'warning');
            } else if (!currentCSVFile) {
                showNotification('⚠️ Vui lòng chọn CSV file', 'warning');
            } else if (!strategySelected) {
                showNotification('⚠️ Vui lòng chọn Strategy', 'warning');
            }
        } else {
            runBacktest();
        }
    });

    // Export PDF button
    document.getElementById('exportPDF').addEventListener('click', exportBacktestPDF);

    // Export trades button
    document.getElementById('exportTrades').addEventListener('click', exportTrades);

    // Save state when settings change
    ['initialCapital', 'commission', 'slippage', 'timeframe'].forEach(id => {
        const elem = document.getElementById(id);
        if (elem) {
            elem.addEventListener('change', saveBacktestState);
        }
    });
}

/**
 * Show timeframe modal for backtest (separate from index/strategy context)
 */
function showTimeframeModalForBacktest() {
    console.log('📊 [Backtest] Showing timeframe modal...');

    const modal = document.getElementById('timeframeModal');
    if (modal) {
        modal.style.display = 'flex';
        console.log('✅ [Backtest] Modal displayed');
    } else {
        console.error('❌ [Backtest] Modal not found!');
        // Fallback: open file picker directly
        document.getElementById('csvFile').click();
    }
}

/**
 * Close timeframe modal (same function as index/strategy)
 */
function closeTimeframeModalBacktest() {
    const modal = document.getElementById('timeframeModal');
    if (modal) {
        modal.style.display = 'none';
    }
    console.log('❌ [Backtest] User cancelled timeframe selection');
}

/**
 * Confirm timeframe and open file picker for backtest
 */
function confirmTimeframeAndUploadBacktest() {
    const timeframeSelect = document.getElementById('timeframeSelect');
    if (timeframeSelect) {
        selectedTimeframe = timeframeSelect.value;
        console.log('✅ [Backtest] Selected timeframe:', selectedTimeframe);
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
        // Restore saved file and timeframe from localStorage (shared with optimize)
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

            checkReadyToBacktest();
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

            // Save to localStorage (shared with optimize)
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

            checkReadyToBacktest();
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

function checkReadyToBacktest() {
    const strategySelected = document.getElementById('strategySelect').value;
    const canRun = currentCSVFile && strategySelected;
    const btn = document.getElementById('runBacktest');
    
    btn.disabled = !canRun;
    
    // Update tooltip
    if (!currentCSVFile && !strategySelected) {
        btn.title = '⚠️ Vui lòng chọn CSV file và Strategy';
    } else if (!currentCSVFile) {
        btn.title = '⚠️ Vui lòng chọn CSV file';
    } else if (!strategySelected) {
        btn.title = '⚠️ Vui lòng chọn Strategy';
    } else {
        btn.title = 'Click để chạy backtest';
    }
}

async function runBacktest() {
    const strategyFile = document.getElementById('strategySelect').value;
    const initialCapital = parseFloat(document.getElementById('initialCapital').value);
    const commission = parseFloat(document.getElementById('commission').value);
    const slippage = parseFloat(document.getElementById('slippage').value);
    const timeframe = document.getElementById('timeframe').value;

    // Auto-switch to Terminal tab
    switchBacktestTab('terminal');

    // Clear terminal and add starting logs
    clearBacktestTerminal();
    addBacktestTerminalLine('🚀 Starting backtest...', 'success');
    addBacktestTerminalLine('─'.repeat(60), 'default');
    addBacktestTerminalLine(`📊 Strategy: ${strategyFile}`, 'info');
    addBacktestTerminalLine(`📁 Data File: ${currentCSVFile}`, 'info');
    addBacktestTerminalLine(`⏰ Timeframe: ${timeframe}`, 'info');
    addBacktestTerminalLine(`💰 Initial Capital: $${initialCapital.toLocaleString()}`, 'info');
    addBacktestTerminalLine(`📈 Commission: ${commission} points`, 'info');
    addBacktestTerminalLine(`📉 Slippage: ${slippage} points`, 'info');
    addBacktestTerminalLine('─'.repeat(60), 'default');

    // Show loading
    const btn = document.getElementById('runBacktest');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="btn-icon">⏳</span> Running...';
    btn.disabled = true;

    // Track timing
    const startTime = Date.now();

    try {
        addBacktestTerminalLine('⏳ Loading data and strategy...', 'info');

        const response = await fetch('/run_backtest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                csv_file: currentCSVFile,
                strategy_file: strategyFile,
                initial_capital: initialCapital,
                commission: commission,
                slippage: slippage,
                timeframe: timeframe
            })
        });

        addBacktestTerminalLine('📦 Response received, processing results...', 'info');

        const result = await response.json();

        if (result.success) {
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
            addBacktestTerminalLine('─'.repeat(60), 'default');
            addBacktestTerminalLine('✅ Backtest completed successfully!', 'success');
            addBacktestTerminalLine(`⏱️  Execution time: ${elapsed}s`, 'info');
            addBacktestTerminalLine('─'.repeat(60), 'default');

            displayResults(result);
            showNotification('✅ Backtest completed!', 'success');
        } else {
            addBacktestTerminalLine('─'.repeat(60), 'default');
            addBacktestTerminalLine('❌ Backtest failed: ' + result.error, 'error');
            addBacktestTerminalLine('─'.repeat(60), 'default');
            showNotification('❌ ' + result.error, 'error');
        }
    } catch (error) {
        addBacktestTerminalLine('─'.repeat(60), 'default');
        addBacktestTerminalLine('❌ Error: ' + error.message, 'error');
        addBacktestTerminalLine('─'.repeat(60), 'default');
        showNotification('❌ Backtest failed: ' + error.message, 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function displayResults(result) {
    // Save result for PDF export
    lastBacktestResult = result;

    // Update statistics
    const stats = result.results;

    // Safely update stat cards with null checks
    const statElements = {
        'statTotalTrades': stats.total_trades,
        'statWinRate': stats.win_rate.toFixed(2) + '%',
        'statNetProfitPct': stats.total_return.toFixed(2) + '%',
        'statProfitFactor': stats.profit_factor.toFixed(2),
        'statMaxDrawdown': stats.max_drawdown.toFixed(2) + '%',
        'statSharpe': stats.sharpe_ratio.toFixed(2)
    };

    for (const [id, value] of Object.entries(statElements)) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    // Update Net Profit in dollars
    const netProfit = ((stats.total_return / 100) * parseFloat(document.getElementById('initialCapital').value));
    const netProfitEl = document.getElementById('statNetProfit');
    if (netProfitEl) {
        netProfitEl.textContent = '$' + netProfit.toFixed(2);
    }

    // Update Annual Return
    const annualReturnEl = document.getElementById('statAnnualReturn');
    if (annualReturnEl && stats.annual_return !== undefined) {
        annualReturnEl.textContent = stats.annual_return.toFixed(2) + '%';
    }

    // Add terminal summary
    addBacktestTerminalLine('📊 RESULTS SUMMARY', 'success');
    addBacktestTerminalLine('─'.repeat(60), 'default');
    addBacktestTerminalLine(`📈 Total Trades: ${stats.total_trades}`, 'info');
    addBacktestTerminalLine(`🎯 Win Rate: ${stats.win_rate.toFixed(2)}%`, stats.win_rate >= 50 ? 'success' : 'warning');
    addBacktestTerminalLine(`💰 Net Profit: $${netProfit.toFixed(2)} (${stats.total_return.toFixed(2)}%)`, netProfit >= 0 ? 'success' : 'error');
    addBacktestTerminalLine(`📊 Profit Factor: ${stats.profit_factor.toFixed(2)}`, stats.profit_factor >= 1.5 ? 'success' : 'warning');
    addBacktestTerminalLine(`📉 Max Drawdown: ${stats.max_drawdown.toFixed(2)}%`, 'error');
    addBacktestTerminalLine(`📐 Sharpe Ratio: ${stats.sharpe_ratio.toFixed(2)}`, stats.sharpe_ratio >= 1 ? 'success' : 'warning');

    if (stats.winning_trades !== undefined) {
        addBacktestTerminalLine(`✅ Winning Trades: ${stats.winning_trades}`, 'success');
        addBacktestTerminalLine(`❌ Losing Trades: ${stats.losing_trades}`, 'error');
    }

    addBacktestTerminalLine('─'.repeat(60), 'default');
    addBacktestTerminalLine('📊 Displaying charts and detailed statistics...', 'info');

    // Color code Net Profit % card
    const netProfitPctEl = document.getElementById('statNetProfitPct');
    if (netProfitPctEl && netProfitPctEl.parentElement) {
        const card = netProfitPctEl.parentElement;
        if (stats.total_return > 0) {
            card.classList.add('positive');
            card.classList.remove('negative');
        } else {
            card.classList.add('negative');
            card.classList.remove('positive');
        }
    }

    // Display detailed statistics
    displayDetailedStats(stats);

    // Display equity curve
    displayEquityCurve(result.equity_curve);

    // Display trades
    displayTrades(result.trades);

    // Save state for persistence
    saveBacktestState();
}

// Helper function to safely update element text content
function safeUpdateElement(elementId, textContent) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = textContent;
    }
}

function displayDetailedStats(stats) {
    // Legacy fields (still keep for other parts of UI) - with null checks
    safeUpdateElement('detailAvgWin', '$' + (stats.avg_win || 0).toFixed(2));
    safeUpdateElement('detailAvgLoss', '$' + (stats.avg_loss || 0).toFixed(2));
    safeUpdateElement('detailLargestWin', '$' + (stats.largest_win || 0).toFixed(2));
    safeUpdateElement('detailLargestLoss', '$' + (stats.largest_loss || 0).toFixed(2));
    safeUpdateElement('detailWinningTrades', stats.winning_trades || 0);
    safeUpdateElement('detailLosingTrades', stats.losing_trades || 0);

    const avgWin = Math.abs(stats.avg_win || 0);
    const avgLoss = Math.abs(stats.avg_loss || 0);
    const winLossRatio = avgLoss > 0 ? (avgWin / avgLoss) : 0;
    safeUpdateElement('detailWinLossRatio', winLossRatio.toFixed(2));

    const expectancy = stats.total_trades > 0 ?
        ((stats.total_return / 100) * stats.final_capital / stats.total_trades) : 0;
    safeUpdateElement('detailExpectancy', '$' + expectancy.toFixed(2));
    
    // NEW: Calculate Long/Short/All stats from lastBacktestResult.trades
    if (!lastBacktestResult || !lastBacktestResult.trades) return;
    
    const allTrades = lastBacktestResult.trades;
    const longTrades = allTrades.filter(t => t.direction === 'long');
    const shortTrades = allTrades.filter(t => t.direction === 'short');
    
    // Helper function to calculate stats for a trade list
    function calcTradeStats(trades) {
        if (!trades || trades.length === 0) {
            return {
                netProfit: 0, grossProfit: 0, grossLoss: 0,
                totalTrades: 0, winTrades: 0, loseTrades: 0,
                winRate: 0, profitFactor: 0,
                avgWin: 0, avgLoss: 0, largestWin: 0, largestLoss: 0,
                maxDD: 0, sharpe: 0
            };
        }
        
        const wins = trades.filter(t => t.profit_value > 0);
        const losses = trades.filter(t => t.profit_value <= 0);
        
        const grossProfit = wins.reduce((sum, t) => sum + t.profit_value, 0);
        const grossLoss = Math.abs(losses.reduce((sum, t) => sum + t.profit_value, 0));
        const netProfit = grossProfit - grossLoss;
        
        const winRate = trades.length > 0 ? (wins.length / trades.length * 100) : 0;
        const profitFactor = grossLoss > 0 ? (grossProfit / grossLoss) : 0;
        
        const avgWin = wins.length > 0 ? (grossProfit / wins.length) : 0;
        const avgLoss = losses.length > 0 ? (grossLoss / losses.length) : 0;
        
        const largestWin = wins.length > 0 ? Math.max(...wins.map(t => t.profit_value)) : 0;
        const largestLoss = losses.length > 0 ? Math.min(...losses.map(t => t.profit_value)) : 0;
        
        // Simple max drawdown calculation
        let peak = 0;
        let maxDD = 0;
        let cumulative = 0;
        trades.forEach(t => {
            cumulative += t.profit_value;
            if (cumulative > peak) peak = cumulative;
            const dd = peak - cumulative;
            if (dd > maxDD) maxDD = dd;
        });
        
        return {
            netProfit, grossProfit, grossLoss,
            totalTrades: trades.length,
            winTrades: wins.length,
            loseTrades: losses.length,
            winRate, profitFactor,
            avgWin, avgLoss, largestWin, largestLoss,
            maxDD, sharpe: 0 // Sharpe requires more complex calculation
        };
    }
    
    const longStats = calcTradeStats(longTrades);
    const shortStats = calcTradeStats(shortTrades);
    const allStats = calcTradeStats(allTrades);

    // Update Long column - with null checks
    safeUpdateElement('longNetProfit', '$' + longStats.netProfit.toFixed(2));
    safeUpdateElement('longGrossProfit', '$' + longStats.grossProfit.toFixed(2));
    safeUpdateElement('longGrossLoss', '$' + longStats.grossLoss.toFixed(2));
    safeUpdateElement('longTotalTrades', longStats.totalTrades);
    safeUpdateElement('longWinTrades', longStats.winTrades);
    safeUpdateElement('longLoseTrades', longStats.loseTrades);
    safeUpdateElement('longWinRate', longStats.winRate.toFixed(2) + '%');
    safeUpdateElement('longProfitFactor', longStats.profitFactor.toFixed(2));
    safeUpdateElement('longAvgWin', '$' + longStats.avgWin.toFixed(2));
    safeUpdateElement('longAvgLoss', '$' + longStats.avgLoss.toFixed(2));
    safeUpdateElement('longLargestWin', '$' + longStats.largestWin.toFixed(2));
    safeUpdateElement('longLargestLoss', '$' + longStats.largestLoss.toFixed(2));
    safeUpdateElement('longMaxDD', '$' + longStats.maxDD.toFixed(2));
    safeUpdateElement('longSharpe', (stats.sharpe_ratio || 0).toFixed(2));

    // Update Short column - with null checks
    safeUpdateElement('shortNetProfit', '$' + shortStats.netProfit.toFixed(2));
    safeUpdateElement('shortGrossProfit', '$' + shortStats.grossProfit.toFixed(2));
    safeUpdateElement('shortGrossLoss', '$' + shortStats.grossLoss.toFixed(2));
    safeUpdateElement('shortTotalTrades', shortStats.totalTrades);
    safeUpdateElement('shortWinTrades', shortStats.winTrades);
    safeUpdateElement('shortLoseTrades', shortStats.loseTrades);
    safeUpdateElement('shortWinRate', shortStats.winRate.toFixed(2) + '%');
    safeUpdateElement('shortProfitFactor', shortStats.profitFactor.toFixed(2));
    safeUpdateElement('shortAvgWin', '$' + shortStats.avgWin.toFixed(2));
    safeUpdateElement('shortAvgLoss', '$' + shortStats.avgLoss.toFixed(2));
    safeUpdateElement('shortLargestWin', '$' + shortStats.largestWin.toFixed(2));
    safeUpdateElement('shortLargestLoss', '$' + shortStats.largestLoss.toFixed(2));
    safeUpdateElement('shortMaxDD', '$' + shortStats.maxDD.toFixed(2));
    safeUpdateElement('shortSharpe', (stats.sharpe_ratio || 0).toFixed(2));

    // Update All column - with null checks
    safeUpdateElement('allNetProfit', '$' + allStats.netProfit.toFixed(2));
    safeUpdateElement('allGrossProfit', '$' + allStats.grossProfit.toFixed(2));
    safeUpdateElement('allGrossLoss', '$' + allStats.grossLoss.toFixed(2));
    safeUpdateElement('allTotalTrades', allStats.totalTrades);
    safeUpdateElement('allWinTrades', allStats.winTrades);
    safeUpdateElement('allLoseTrades', allStats.loseTrades);
    safeUpdateElement('allWinRate', allStats.winRate.toFixed(2) + '%');
    safeUpdateElement('allProfitFactor', allStats.profitFactor.toFixed(2));
    safeUpdateElement('allAvgWin', '$' + allStats.avgWin.toFixed(2));
    safeUpdateElement('allAvgLoss', '$' + allStats.avgLoss.toFixed(2));
    safeUpdateElement('allLargestWin', '$' + allStats.largestWin.toFixed(2));
    safeUpdateElement('allLargestLoss', '$' + allStats.largestLoss.toFixed(2));
    safeUpdateElement('allMaxDD', '$' + allStats.maxDD.toFixed(2));
    safeUpdateElement('allSharpe', (stats.sharpe_ratio || 0).toFixed(2));

    // Apply color coding
    applyColorCoding('longNetProfit', longStats.netProfit);
    applyColorCoding('shortNetProfit', shortStats.netProfit);
    applyColorCoding('allNetProfit', allStats.netProfit);
}

function applyColorCoding(elementId, value) {
    const elem = document.getElementById(elementId);
    if (!elem) return;
    elem.classList.remove('positive', 'negative');
    if (value > 0) {
        elem.classList.add('positive');
    } else if (value < 0) {
        elem.classList.add('negative');
    }
}


function displayEquityCurve(equityData) {
    const container = document.getElementById('equityChart');
    container.innerHTML = '';
    
    equityChart = LightweightCharts.createChart(container, {
        width: container.clientWidth,
        height: 300,
        layout: {
            background: { color: '#131722' },
            textColor: '#d1d4dc',
        },
        grid: {
            vertLines: { color: '#1e222d' },
            horzLines: { color: '#1e222d' },
        },
        timeScale: {
            borderColor: '#2b2b43',
            timeVisible: true,
            secondsVisible: false
        }
    });
    
    const equitySeries = equityChart.addLineSeries({
        color: '#2962ff',
        lineWidth: 2,
        title: 'Equity'
    });
    
    const chartData = equityData.map(point => ({
        time: point.time,
        value: point.equity
    }));
    
    equitySeries.setData(chartData);
    
    // Fit content with timeout to ensure rendering is complete
    setTimeout(() => {
        equityChart.timeScale().fitContent();
    }, 100);
    
    // Handle resize
    window.addEventListener('resize', () => {
        if (equityChart) {
            equityChart.applyOptions({ width: container.clientWidth });
        }
    });
}

function displayTrades(trades) {
    tradesData = trades;
    const tbody = document.getElementById('tradesTableBody');
    tbody.innerHTML = '';

    trades.forEach((trade, index) => {
        const row = tbody.insertRow();

        const profitClass = trade.profit_value > 0 ? 'profit' : 'loss';
        const directionClass = trade.direction === 'long' ? 'long' : 'short';

        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${trade.entry_time}</td>
            <td>${trade.entry_price.toFixed(2)}</td>
            <td>${trade.exit_time}</td>
            <td>${trade.exit_price.toFixed(2)}</td>
            <td><span class="badge ${directionClass}">${trade.direction.toUpperCase()}</span></td>
            <td class="${profitClass}">${trade.profit_value > 0 ? '+' : ''}${trade.profit_value.toFixed(2)}</td>
            <td class="${profitClass}">${trade.profit_points > 0 ? '+' : ''}${trade.profit_points.toFixed(2)}</td>
            <td><span class="exit-reason">${trade.exit_reason}</span></td>
        `;
    });

    // Add terminal log for trade history
    const longTrades = trades.filter(t => t.direction === 'long').length;
    const shortTrades = trades.filter(t => t.direction === 'short').length;
    const winTrades = trades.filter(t => t.profit_value > 0).length;
    const loseTrades = trades.filter(t => t.profit_value <= 0).length;

    addBacktestTerminalLine('📋 TRADE HISTORY', 'success');
    addBacktestTerminalLine('─'.repeat(60), 'default');
    addBacktestTerminalLine(`📊 Total Trades Loaded: ${trades.length}`, 'info');
    addBacktestTerminalLine(`🟢 Long Trades: ${longTrades}`, 'info');
    addBacktestTerminalLine(`🔴 Short Trades: ${shortTrades}`, 'info');
    addBacktestTerminalLine(`✅ Winning: ${winTrades}`, 'success');
    addBacktestTerminalLine(`❌ Losing: ${loseTrades}`, 'error');
    addBacktestTerminalLine('─'.repeat(60), 'default');
    addBacktestTerminalLine('✅ Backtest complete! Check the tabs for detailed results.', 'success');
}

function exportTrades() {
    if (tradesData.length === 0) {
        showNotification('⚠️ No trades to export', 'warning');
        return;
    }
    
    // Create CSV content
    let csv = 'No,Entry Time,Entry Price,Exit Time,Exit Price,Direction,P&L ($),P&L (pts),Exit Reason\n';
    
    tradesData.forEach((trade, index) => {
        csv += `${index + 1},${trade.entry_time},${trade.entry_price},${trade.exit_time},${trade.exit_price},${trade.direction},${trade.profit_value},${trade.profit_points},${trade.exit_reason}\n`;
    });
    
    // Download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `backtest_trades_${Date.now()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    showNotification('✅ Trades exported!', 'success');
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

async function exportBacktestPDF() {
    if (!lastBacktestResult) {
        showNotification('❌ No backtest results to export', 'error');
        return;
    }
    
    const btn = document.getElementById('exportPDF');
    const originalText = btn.innerHTML;
    btn.innerHTML = '⏳ Exporting...';
    btn.disabled = true;
    
    try {
        const strategyName = document.getElementById('strategySelect').value.replace('.json', '');
        
        const response = await fetch('/export_backtest_pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                results: lastBacktestResult.results,
                trades: lastBacktestResult.trades,
                equity_curve: lastBacktestResult.equity_curve,
                strategy_name: strategyName,
                csv_filename: currentCSVFile
            })
        });
        
        if (response.ok) {
            // Download PDF
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `backtest_${strategyName}_${new Date().getTime()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showNotification('✅ PDF exported successfully!', 'success');
        } else {
            const error = await response.json();
            showNotification('❌ Export failed: ' + error.error, 'error');
        }
    } catch (error) {
        showNotification('❌ Export failed: ' + error.message, 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// ===== STATE PERSISTENCE =====

/**
 * Save backtest state to localStorage
 */
function saveBacktestState() {
    try {
        const state = {
            csvFile: currentCSVFile,
            strategy: document.getElementById('strategySelect')?.value || null,
            initialCapital: parseFloat(document.getElementById('initialCapital')?.value || 10000),
            commission: parseFloat(document.getElementById('commission')?.value || 0),
            slippage: parseFloat(document.getElementById('slippage')?.value || 0),
            timeframe: document.getElementById('timeframe')?.value || '5m',
            lastBacktestResult: lastBacktestResult,
            tradesData: tradesData,
            activeTab: getActiveBacktestTab(),
            timestamp: Date.now()
        };

        localStorage.setItem('backtestState', JSON.stringify(state));
        console.log('✅ Backtest state saved');
    } catch (error) {
        console.error('Failed to save backtest state:', error);
    }
}

/**
 * Restore backtest state from localStorage
 */
function restoreBacktestState() {
    try {
        const savedState = localStorage.getItem('backtestState');
        if (!savedState) return;

        const state = JSON.parse(savedState);

        // Check if state is not too old (older than 7 days)
        const daysSinceLastSave = (Date.now() - (state.timestamp || 0)) / (1000 * 60 * 60 * 24);
        if (daysSinceLastSave > 7) {
            console.log('ℹ️ Backtest state is too old, skipping restore');
            return;
        }

        // Restore form inputs
        if (state.strategy) {
            // Wait for strategies to load first
            setTimeout(() => {
                const strategySelect = document.getElementById('strategySelect');
                if (strategySelect && state.strategy) {
                    strategySelect.value = state.strategy;
                    checkReadyToBacktest();
                }
            }, 500);
        }

        if (state.initialCapital) {
            const elem = document.getElementById('initialCapital');
            if (elem) elem.value = state.initialCapital;
        }

        if (state.commission !== undefined) {
            const elem = document.getElementById('commission');
            if (elem) elem.value = state.commission;
        }

        if (state.slippage !== undefined) {
            const elem = document.getElementById('slippage');
            if (elem) elem.value = state.slippage;
        }

        if (state.timeframe) {
            const elem = document.getElementById('timeframe');
            if (elem) elem.value = state.timeframe;
        }

        // Restore results if available
        if (state.lastBacktestResult) {
            lastBacktestResult = state.lastBacktestResult;
            tradesData = state.tradesData || [];

            // Re-display results after a short delay to ensure DOM is ready
            setTimeout(() => {
                displayResults(lastBacktestResult);

                // Restore active tab
                if (state.activeTab) {
                    switchBacktestTab(state.activeTab);
                }

                console.log('✅ Backtest state restored');
            }, 600);
        }

    } catch (error) {
        console.error('Failed to restore backtest state:', error);
    }
}

/**
 * Get current active backtest tab
 */
function getActiveBacktestTab() {
    const tabs = ['charts', 'performance', 'history', 'terminal'];
    for (const tab of tabs) {
        const panel = document.getElementById(tab + 'Tab');
        if (panel && panel.style.display !== 'none') {
            return tab;
        }
    }
    return 'charts'; // default
}

// Export functions for modal to call
window.closeTimeframeModal = closeTimeframeModalBacktest;
window.confirmTimeframeAndUpload = confirmTimeframeAndUploadBacktest;
