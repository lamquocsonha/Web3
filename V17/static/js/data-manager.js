/**
 * DATA MANAGER - Shared data upload and management for all pages
 * Handles CSV upload, IndexedDB storage, and data source switching
 */

// Global data storage (IMPORTANT: Must use window.offlineData to be accessible everywhere)
window.offlineData = null; // Offline CSV data (accessible globally) - USED BY STRATEGY
window.onlineData = null; // Online exchange data (accessible globally) - USED BY CHART IN ONLINE MODE
let currentDataSource = 'offline'; // Current data source: 'offline' or 'online'
let cachedTooltipInfo = null; // Cache tooltip info for later update
let activeIndicators = []; // Active indicators for chart display
let selectedTimeframe = '1m'; // Selected timeframe for uploaded data
let pendingFileUpload = null; // Store pending file upload event

// Sync offlineData with window for backward compatibility
let offlineData = null;
Object.defineProperty(window, 'offlineData', {
    get() { return offlineData; },
    set(value) {
        offlineData = value;
        console.log('✅ offlineData (CSV) synced:', value ? `${value.candlesticks?.length || 0} candles` : 'null');
    },
    configurable: true
});

// Sync onlineData with window
let onlineData = null;
Object.defineProperty(window, 'onlineData', {
    get() { return onlineData; },
    set(value) {
        onlineData = value;
        console.log('✅ onlineData (Exchange) synced:', value ? `${value.candlesticks?.length || 0} candles` : 'null');
    },
    configurable: true
});

// IndexedDB instance
let db;

/**
 * Initialize IndexedDB for large data storage
 */
function initIndexedDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('TradingSystemDB', 3); // Increased version to fix conflict
        
        request.onerror = () => {
            console.error('IndexedDB error:', request.error);
            reject(request.error);
        };
        
        request.onsuccess = () => {
            db = request.result;
            console.log('✅ IndexedDB initialized');
            resolve(db);
        };
        
        request.onupgradeneeded = (event) => {
            db = event.target.result;
            if (!db.objectStoreNames.contains('chartData')) {
                db.createObjectStore('chartData', { keyPath: 'id' });
            }
            // Store for active indicators with display settings
            if (!db.objectStoreNames.contains('indicators')) {
                db.createObjectStore('indicators', { keyPath: 'id' });
            }
            console.log('📦 IndexedDB schema created');
        };
    });
}

/**
 * Save data to IndexedDB
 */
async function saveToIndexedDB(data) {
    if (!db) {
        await initIndexedDB();
    }
    
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['chartData'], 'readwrite');
        const store = transaction.objectStore('chartData');
        const request = store.put({ id: 'offline_data', data: data });
        
        request.onsuccess = () => {
            console.log('💾 Data saved to IndexedDB');
            resolve();
        };
        
        request.onerror = () => {
            console.error('❌ IndexedDB save error:', request.error);
            reject(request.error);
        };
    });
}

/**
 * Load data from IndexedDB
 */
async function loadFromIndexedDB() {
    if (!db) {
        await initIndexedDB();
    }
    
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['chartData'], 'readonly');
        const store = transaction.objectStore('chartData');
        const request = store.get('offline_data');
        
        request.onsuccess = () => {
            if (request.result) {
                console.log('✅ Data loaded from IndexedDB');
                resolve(request.result.data);
            } else {
                console.log('ℹ️ No data in IndexedDB');
                resolve(null);
            }
        };
        
        request.onerror = () => {
            console.error('❌ IndexedDB load error:', request.error);
            reject(request.error);
        };
    });
}

/**
 * Clear offline data from IndexedDB
 */
async function clearOfflineData(silent = false) {
    if (!silent && !confirm('⚠️ Xóa dữ liệu offline?\n\nChart sẽ chuyển về chế độ Online.')) {
        return;
    }

    try {
        if (!db) {
            await initIndexedDB();
        }

        const transaction = db.transaction(['chartData'], 'readwrite');
        const store = transaction.objectStore('chartData');
        await store.delete('offline_data');

        offlineData = null;
        window.offlineData = null;

        // Clear chart data
        if (typeof window.candlestickSeries !== 'undefined' && window.candlestickSeries) {
            window.candlestickSeries.setData([]);
        }
        if (typeof window.volumeSeries !== 'undefined' && window.volumeSeries) {
            window.volumeSeries.setData([]);
        }
        if (typeof window.workspaceCandlestickSeries !== 'undefined' && window.workspaceCandlestickSeries) {
            window.workspaceCandlestickSeries.setData([]);
        }
        if (typeof window.workspaceVolumeSeries !== 'undefined' && window.workspaceVolumeSeries) {
            window.workspaceVolumeSeries.setData([]);
        }

        // Update tooltip
        updateDataTooltip(null);

        // Switch to online mode (only if not silent)
        if (!silent) {
            changeDataSource('online');
            alert('✅ Đã xóa dữ liệu offline');
        }

        console.log('🗑️ Offline data cleared');
    } catch (error) {
        console.error('❌ Clear data error:', error);
        if (!silent) {
            alert('❌ Lỗi xóa dữ liệu: ' + error.message);
        }
    }
}

/**
 * Update data tooltip display
 */
function updateDataTooltip(info) {
    try {
        // Cache info for later use
        if (info) {
            cachedTooltipInfo = info;
        }
        
        const tooltipStatus = document.getElementById('tooltipStatus');
        const tooltipFileName = document.getElementById('tooltipFileName');
        const tooltipStartDate = document.getElementById('tooltipStartDate');
        const tooltipEndDate = document.getElementById('tooltipEndDate');
        const tooltipCandles = document.getElementById('tooltipCandles');
        const tooltipSize = document.getElementById('tooltipSize');
        const tooltipOfflineTimeframe = document.getElementById('tooltipOfflineTimeframe');
        
        // Debug logging
        console.log('📊 updateDataTooltip called with:', info);
        console.log('  - Elements found:', {
            status: !!tooltipStatus,
            fileName: !!tooltipFileName,
            startDate: !!tooltipStartDate,
            endDate: !!tooltipEndDate,
            candles: !!tooltipCandles,
            size: !!tooltipSize,
            timeframe: !!tooltipOfflineTimeframe
        });
        
        // If no elements found, just cache and return
        if (!tooltipStatus && !tooltipFileName && !tooltipStartDate && !tooltipEndDate && !tooltipCandles && !tooltipSize) {
            console.log('ℹ️ Tooltip elements not found - data cached for later');
            return;
        }
        
        if (!info) {
            // No data
            if (tooltipStatus) tooltipStatus.innerHTML = 'Chưa có dữ liệu';
            if (tooltipFileName) {
                tooltipFileName.textContent = '--';
                tooltipFileName.title = '';
            }
            if (tooltipStartDate) tooltipStartDate.textContent = '--';
            if (tooltipEndDate) tooltipEndDate.textContent = '--';
            if (tooltipCandles) tooltipCandles.textContent = '--';
            if (tooltipSize) tooltipSize.textContent = '--';
        } else {
            // Has data
            if (tooltipStatus) {
                tooltipStatus.innerHTML = '✅ Đã lưu';
                console.log('  ✓ Updated status');
            }
            if (tooltipFileName && info.filename) {
                tooltipFileName.textContent = info.filename;
                tooltipFileName.title = info.filename; // Full filename on hover
                console.log('  ✓ Updated filename:', info.filename);
            }
            if (tooltipStartDate) {
                tooltipStartDate.textContent = formatDate(info.start_date);
                console.log('  ✓ Updated start date:', formatDate(info.start_date));
            }
            if (tooltipEndDate) {
                tooltipEndDate.textContent = formatDate(info.end_date);
                console.log('  ✓ Updated end date:', formatDate(info.end_date));
            }
            if (tooltipCandles) {
                tooltipCandles.textContent = info.total_candles ? info.total_candles.toLocaleString() : '--';
                console.log('  ✓ Updated candles:', info.total_candles);
            }
            if (tooltipSize) {
                tooltipSize.textContent = info.size || '--';
                console.log('  ✓ Updated size:', info.size);
            }
            if (tooltipOfflineTimeframe) {
                tooltipOfflineTimeframe.textContent = info.timeframe || '--';
                console.log('  ✓ Updated timeframe:', info.timeframe);
            }
            console.log('✅ Tooltip updated successfully');
        }
    } catch (error) {
        console.error('❌ Error in updateDataTooltip:', error);
        // Don't throw - just log and continue
    }
}

/**
 * Format date for display (DD/MM/YYYY)
 */
function formatDate(dateStr) {
    if (!dateStr) return '--';
    // Convert YYYY-MM-DD to DD/MM/YYYY
    const parts = dateStr.split('-');
    if (parts.length === 3) {
        return `${parts[2]}/${parts[1]}/${parts[0]}`;
    }
    return dateStr;
}

/**
 * Show timeframe modal first, then let user select file
 */
function showTimeframeModalFirst() {
    console.log('📊 Showing timeframe modal...');
    
    const modal = document.getElementById('timeframeModal');
    if (modal) {
        modal.style.display = 'flex';
        console.log('✅ Modal displayed');
    } else {
        console.error('❌ Modal not found!');
        // Fallback: open file picker directly
        document.getElementById('csvFileInput').click();
    }
}

/**
 * Handle CSV file upload (after timeframe is selected)
 * This function is an alias for proceedWithUpload for backward compatibility
 */
function handleFileUpload(event) {
    return proceedWithUpload(event);
}

/**
 * Close timeframe modal
 */
function closeTimeframeModal() {
    const modal = document.getElementById('timeframeModal');
    if (modal) {
        modal.style.display = 'none';
    }
    console.log('❌ User cancelled timeframe selection');
}

/**
 * Confirm timeframe and open file picker
 */
function confirmTimeframeAndUpload() {
    const timeframeSelect = document.getElementById('timeframeSelect');
    if (timeframeSelect) {
        selectedTimeframe = timeframeSelect.value;
        console.log('✅ Selected timeframe:', selectedTimeframe);
    }
    
    // Close modal
    const modal = document.getElementById('timeframeModal');
    if (modal) {
        modal.style.display = 'none';
    }
    
    // Open file picker
    const fileInput = document.getElementById('csvFileInput');
    if (fileInput) {
        console.log('📁 Opening file picker...');
        fileInput.click();
    } else {
        console.error('❌ File input not found!');
    }
}

/**
 * Proceed with actual file upload after timeframe is selected
 */
async function proceedWithUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Check if chart is ready (if chart exists on this page)
    // Only check if these variables are defined (not all pages have chart)
    if (typeof window.candlestickSeries !== 'undefined' && window.candlestickSeries !== null) {
        if (typeof window.chartInitialized !== 'undefined' && (!window.chartInitialized || !window.candlestickSeries)) {
            alert('⚠️ Chart đang khởi tạo...\n\nĐợi 3-5 giây và thử lại!');
            event.target.value = '';
            pendingFileUpload = null;
            return;
        }
    }
    
    // Show loading overlay
    showLoadingOverlay('📤 Đang upload file...');
    
    try {
        // Upload to server
        const formData = new FormData();
        formData.append('file', file);
        formData.append('timeframe', selectedTimeframe); // Add selected timeframe
        
        console.log('📤 Uploading to server with timeframe:', selectedTimeframe);
        updateLoadingMessage('⚙️ Đang xử lý CSV...');
        
        const uploadResponse = await fetch('/api/upload-csv', {
            method: 'POST',
            body: formData
        });
        
        const uploadResult = await uploadResponse.json();
        
        console.log('📦 Upload result:', {
            success: uploadResult.success,
            filename: uploadResult.filename,
            file_name_input: file.name,
            has_data: !!uploadResult.data,
            has_info: !!uploadResult.info
        });
        
        if (!uploadResult.success) {
            hideLoadingOverlay();
            
            let errorMsg = '❌ Lỗi upload CSV:\n\n' + uploadResult.error;
            
            // Add debug info if available
            if (uploadResult.debug_info) {
                const debug = uploadResult.debug_info;
                errorMsg += '\n\n📊 Thông tin debug:';
                
                if (debug.original_columns) {
                    errorMsg += '\n- Cột trong file: ' + debug.original_columns.join(', ');
                }
                if (debug.matched_columns) {
                    errorMsg += '\n- Cột đã nhận: ' + Object.keys(debug.matched_columns).join(', ');
                }
                if (debug.missing_columns && debug.missing_columns.length > 0) {
                    errorMsg += '\n- Cột thiếu: ' + debug.missing_columns.join(', ');
                }
                if (debug.date_sample) {
                    errorMsg += '\n- Mẫu ngày: ' + debug.date_sample;
                }
                if (debug.time_sample) {
                    errorMsg += '\n- Mẫu giờ: ' + debug.time_sample;
                }
                
                console.error('Debug info:', debug);
            }
            
            alert(errorMsg);
            event.target.value = '';
            return;
        }
        
        console.log('✅ Server parsed:', uploadResult.info);
        updateLoadingMessage('💾 Đang lưu dữ liệu...');
        
        // Convert to chart format
        const candlesticks = uploadResult.data;
        const volumes = uploadResult.data.map(d => ({
            time: d.time,
            value: d.volume,
            color: d.close >= d.open ? 'rgba(0, 150, 136, 0.5)' : 'rgba(255, 82, 82, 0.5)'
        }));
        
        const sizeInMB = (JSON.stringify(uploadResult.data).length / (1024 * 1024)).toFixed(2);
        
        const data = {
            candlesticks: candlesticks,
            volumes: volumes,
            symbol: uploadResult.info.ticker || 'VN30F1M',
            timeframe: selectedTimeframe, // Store timeframe
            metadata: {
                filename: uploadResult.original_filename || uploadResult.filename || file.name,
                start_date: uploadResult.info.start_date,
                end_date: uploadResult.info.end_date,
                total_candles: uploadResult.info.total_candles,
                size: sizeInMB + ' MB',
                timeframe: selectedTimeframe, // Store in metadata too
                uploadTime: new Date().toISOString()
            }
        };
        
        console.log(`✅ Loaded ${candlesticks.length} candles`);
        
        // Save to IndexedDB
        offlineData = data;
        try {
            await saveToIndexedDB(data);
            console.log('💾 Saved to IndexedDB');
        } catch (e) {
            console.error('IndexedDB error:', e);
        }
        
        // Update tooltip
        updateDataTooltip({
            filename: uploadResult.original_filename || uploadResult.filename || file.name,
            start_date: uploadResult.info.start_date,
            end_date: uploadResult.info.end_date,
            total_candles: uploadResult.info.total_candles,
            size: sizeInMB + ' MB',
            timeframe: selectedTimeframe
        });
        
        updateLoadingMessage('📊 Đang cập nhật chart...');
        
        // Update chart if available
        if (typeof window.candlestickSeries !== 'undefined' && window.candlestickSeries) {
            window.candlestickSeries.setData(data.candlesticks);
            if (typeof window.volumeSeries !== 'undefined' && window.volumeSeries && typeof window.volumeVisible !== 'undefined' && window.volumeVisible) {
                window.volumeSeries.setData(data.volumes);
            }
            
            // Update price display
            const lastCandle = data.candlesticks[data.candlesticks.length - 1];
            if (typeof updatePriceDisplay === 'function') {
                updatePriceDisplay(lastCandle);
            }
            
            // Update symbol
            const symbolEl = document.querySelector('.symbol');
            if (symbolEl) {
                symbolEl.textContent = data.symbol;
            }
            
            // Update timeframe badge
            const timeframeBadge = document.getElementById('timeframeBadge');
            if (timeframeBadge && data.timeframe) {
                timeframeBadge.textContent = data.timeframe;
            }
            
            // Fit chart
            setTimeout(() => {
                if (typeof fitChartContent === 'function') {
                    fitChartContent();
                }
            }, 100);
        }
        
        // Switch to offline mode
        changeDataSource('offline');
        
        hideLoadingOverlay();
        alert(`✅ Upload thành công!\n\n${uploadResult.message}`);
        event.target.value = '';
        pendingFileUpload = null;
        
    } catch (error) {
        hideLoadingOverlay();
        console.error('❌ Upload error:', error);
        alert('❌ Lỗi upload: ' + error.message);
        event.target.value = '';
        pendingFileUpload = null;
    }
}

/**
 * Change data source between offline and online
 */
function changeDataSource(source) {
    currentDataSource = source;
    
    // Save to localStorage
    localStorage.setItem('dataSource', source);
    console.log('💾 Saved data source preference:', source);
    
    const offlineBtn = document.getElementById('offlineDataBtn');
    const onlineBtn = document.getElementById('onlineDataBtn');
    
    if (source === 'offline') {
        // Switch to offline
        if (offlineBtn) {
            offlineBtn.classList.add('active');
            offlineBtn.style.background = '#2962ff';
            offlineBtn.style.color = 'white';
        }
        if (onlineBtn) {
            onlineBtn.classList.remove('active');
            onlineBtn.style.background = 'transparent';
            onlineBtn.style.color = '#787b86';
        }
        
        console.log('📁 Switched to OFFLINE mode');

        // Load offline data if available
        if (offlineData && typeof window.candlestickSeries !== 'undefined' && window.candlestickSeries) {
            window.candlestickSeries.setData(offlineData.candlesticks);
            if (typeof window.volumeSeries !== 'undefined' && window.volumeSeries && typeof window.volumeVisible !== 'undefined' && window.volumeVisible) {
                window.volumeSeries.setData(offlineData.volumes);
            }

            // Strategy signals will be reloaded automatically via chartDataLoaded event
            // No need to manually reload here
        }

        // Also load for workspace chart
        if (offlineData && typeof window.workspaceCandlestickSeries !== 'undefined' && window.workspaceCandlestickSeries) {
            window.workspaceCandlestickSeries.setData(offlineData.candlesticks);
            if (typeof window.workspaceVolumeSeries !== 'undefined' && window.workspaceVolumeSeries) {
                window.workspaceVolumeSeries.setData(offlineData.volumes);
            }
        }
    } else {
        // Switch to online
        if (offlineBtn) {
            offlineBtn.classList.remove('active');
            offlineBtn.style.background = 'transparent';
            offlineBtn.style.color = '#787b86';
        }
        if (onlineBtn) {
            onlineBtn.classList.add('active');
            onlineBtn.style.background = '#2962ff';
            onlineBtn.style.color = 'white';
        }
        
        console.log('🌐 Switched to ONLINE mode');
        
        // Online data will be loaded via header_common.html
        // No alert - just wait for exchange connection
    }
}

// Data source change listener - called from header_common.html
window.onDataSourceChanged = function(source) {
    currentDataSource = source;
    localStorage.setItem('dataSource', source);
    console.log('💾 Data source changed to:', source);
    
    if (source === 'offline') {
        console.log('📁 Loading OFFLINE data to chart...');

        // Use the proper loadOfflineData function if chart is initialized
        if (offlineData && typeof loadOfflineData === 'function') {
            loadOfflineData();
            console.log('✅ Loaded offline data using loadOfflineData()');

            // Strategy signals will be reloaded automatically via chartDataLoaded event
            // No need to manually reload here
        } else if (offlineData && typeof window.candlestickSeries !== 'undefined' && window.candlestickSeries) {
            // Fallback for cases where loadOfflineData is not available
            window.candlestickSeries.setData(offlineData.candlesticks);
            if (typeof window.volumeSeries !== 'undefined' && window.volumeSeries && typeof window.volumeVisible !== 'undefined' && window.volumeVisible) {
                window.volumeSeries.setData(offlineData.volumes);
            }

            // Strategy signals will be reloaded automatically via chartDataLoaded event
            // No need to manually reload here
        }

        // Also load for workspace chart
        if (offlineData && typeof window.workspaceCandlestickSeries !== 'undefined' && window.workspaceCandlestickSeries) {
            window.workspaceCandlestickSeries.setData(offlineData.candlesticks);
            if (typeof window.workspaceVolumeSeries !== 'undefined' && window.workspaceVolumeSeries) {
                window.workspaceVolumeSeries.setData(offlineData.volumes);
            }
        }
    } else {
        console.log('🌐 Online mode active - waiting for exchange connection...');
        // Online data will be loaded via connectOnlineData() in header_common.html
    }
};

// Online data loaded callback
window.onOnlineDataLoaded = function(data, info) {
    console.log('📊 Online data received:', data.length, 'candles from', info.exchange);
    
    // Convert to chart format
    const candlesticks = data.map(d => ({
        time: d.time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close
    }));
    
    const volumes = data.map(d => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? '#26a69a' : '#ef5350'
    }));
    
    // Update chart
    if (typeof window.candlestickSeries !== 'undefined' && window.candlestickSeries) {
        window.candlestickSeries.setData(candlesticks);
        if (typeof window.volumeSeries !== 'undefined' && window.volumeSeries && typeof window.volumeVisible !== 'undefined' && window.volumeVisible) {
            window.volumeSeries.setData(volumes);
        }
    }

    // Also load for workspace chart
    if (typeof window.workspaceCandlestickSeries !== 'undefined' && window.workspaceCandlestickSeries) {
        window.workspaceCandlestickSeries.setData(candlesticks);
        if (typeof window.workspaceVolumeSeries !== 'undefined' && window.workspaceVolumeSeries) {
            window.workspaceVolumeSeries.setData(volumes);
        }
    }
    
    console.log('✅ Online data loaded to chart');
};

/**
 * Initialize data manager on page load
 */
async function initDataManager() {
    console.log('🚀 Initializing Data Manager...');
    
    try {
        // Initialize IndexedDB
        await initIndexedDB();
        
        // Initialize indicators auto-save and load saved indicators
        await initIndicatorsAutoSave();
        
        // Try to load offline data
        const savedData = await loadFromIndexedDB();
        if (savedData) {
            offlineData = savedData;
            console.log('✅ Restored offline data:', offlineData.candlesticks.length, 'candles');
            
            // Check if metadata has filename - if not, clear old data
            if (!savedData.metadata || !savedData.metadata.filename) {
                console.warn('⚠️ Old data format detected (no filename), clearing...');
                await clearOfflineData(true); // Silent mode - no confirmation dialog
                console.log('✅ Old data cleared. Please upload CSV again.');
                return;
            }
            
            // Calculate tooltip info
            const tooltipInfo = {
                filename: null,
                start_date: null,
                end_date: null,
                total_candles: 0,
                size: '0 MB',
                timeframe: '1m' // Default timeframe
            };
            
            // Get filename and timeframe from metadata if available
            if (offlineData.metadata && offlineData.metadata.filename) {
                tooltipInfo.filename = offlineData.metadata.filename;
            }
            if (offlineData.metadata && offlineData.metadata.timeframe) {
                tooltipInfo.timeframe = offlineData.metadata.timeframe;
                selectedTimeframe = offlineData.metadata.timeframe; // Restore selected timeframe
            } else if (offlineData.timeframe) {
                tooltipInfo.timeframe = offlineData.timeframe;
                selectedTimeframe = offlineData.timeframe;
            }
            
            if (offlineData.candlesticks && offlineData.candlesticks.length > 0) {
                const firstCandle = offlineData.candlesticks[0];
                const lastCandle = offlineData.candlesticks[offlineData.candlesticks.length - 1];
                const startDate = new Date(firstCandle.time * 1000).toISOString().split('T')[0];
                const endDate = new Date(lastCandle.time * 1000).toISOString().split('T')[0];
                const sizeInMB = (JSON.stringify(offlineData).length / (1024 * 1024)).toFixed(2);
                
                tooltipInfo.start_date = startDate;
                tooltipInfo.end_date = endDate;
                tooltipInfo.total_candles = offlineData.candlesticks.length;
                tooltipInfo.size = sizeInMB + ' MB';
                
                // Use metadata if available, otherwise calculate from data
                if (offlineData.metadata) {
                    tooltipInfo.start_date = offlineData.metadata.start_date || startDate;
                    tooltipInfo.end_date = offlineData.metadata.end_date || endDate;
                    tooltipInfo.total_candles = offlineData.metadata.total_candles || offlineData.candlesticks.length;
                    tooltipInfo.size = offlineData.metadata.size || (sizeInMB + ' MB');
                }
            }
            
            // Cache and try to update tooltip multiple times
            cachedTooltipInfo = tooltipInfo;
            updateDataTooltip(tooltipInfo);
            
            // Update timeframe badge on chart
            const timeframeBadge = document.getElementById('timeframeBadge');
            if (timeframeBadge && tooltipInfo.timeframe) {
                timeframeBadge.textContent = tooltipInfo.timeframe;
            }
            
            // Retry after delays
            setTimeout(() => {
                console.log('🔄 Retrying tooltip update...');
                updateDataTooltip(tooltipInfo);
            }, 500);
            
            setTimeout(() => {
                console.log('🔄 Final tooltip update retry...');
                updateDataTooltip(tooltipInfo);
            }, 1500);
        } else {
            console.log('ℹ️ No offline data found');
            // Try to load latest processed file from uploads
            try {
                const response = await fetch('/api/load-latest-processed');
                const result = await response.json();
                
                if (result.success) {
                    console.log('📂 Found latest processed file:', result.filename);
                    
                    // Convert data to offline format
                    const candlesticks = result.data.map(d => ({
                        time: d.time,
                        open: d.open,
                        high: d.high,
                        low: d.low,
                        close: d.close
                    }));
                    
                    const volumes = result.data.map(d => ({
                        time: d.time,
                        value: d.volume,
                        color: d.close >= d.open ? '#26a69a' : '#ef5350'
                    }));
                    
                    offlineData = {
                        candlesticks: candlesticks,
                        volumes: volumes,
                        metadata: {
                            filename: result.original_filename || result.filename,
                            start_date: result.info.start_date,
                            end_date: result.info.end_date,
                            total_candles: result.info.total_candles,
                            ticker: result.info.ticker,
                            timeframe: result.info.timeframe || '1M',
                            timezone_offset: result.timezone_offset || 0,
                            size: (JSON.stringify(result.data).length / (1024 * 1024)).toFixed(2) + ' MB'
                        }
                    };
                    
                    // Save to IndexedDB for next time
                    await saveToIndexedDB(offlineData);
                    
                    // Update tooltip
                    const tooltipInfo = {
                        filename: offlineData.metadata.filename,
                        start_date: offlineData.metadata.start_date,
                        end_date: offlineData.metadata.end_date,
                        total_candles: offlineData.metadata.total_candles,
                        size: offlineData.metadata.size
                    };
                    cachedTooltipInfo = tooltipInfo;
                    updateDataTooltip(tooltipInfo);
                    
                    console.log('✅ Loaded latest processed file automatically');
                    
                    // Auto-load to chart if in offline mode (#2)
                    if (currentDataSource === 'offline') {
                        console.log('📊 Auto-loading processed file to chart (offline mode)');
                        if (typeof loadOfflineData === 'function') {
                            setTimeout(() => loadOfflineData(), 500);
                        }
                    }
                } else {
                    console.log('ℹ️ No processed files found');
                }
            } catch (error) {
                console.log('ℹ️ Could not auto-load processed file:', error.message);
            }
        }
        
        // Restore data source preference from localStorage
        const savedSource = localStorage.getItem('dataSource');
        if (savedSource) {
            console.log('📂 Restoring data source preference:', savedSource);
            changeDataSource(savedSource);
        } else {
            // Default: offline if data available, online otherwise
            if (savedData) {
                changeDataSource('offline');
            } else {
                changeDataSource('online');
            }
        }
        
    } catch (error) {
        console.error('❌ Data Manager init error:', error);
    }
}

/**
 * Show loading overlay
 */
function showLoadingOverlay(message) {
    let overlay = document.getElementById('loadingOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 99999;
        `;
        
        const spinner = document.createElement('div');
        spinner.style.cssText = `
            border: 4px solid #2a2e39;
            border-top: 4px solid #2962ff;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
        `;
        
        const text = document.createElement('div');
        text.id = 'loadingText';
        text.style.cssText = `
            color: white;
            font-size: 16px;
            margin-top: 20px;
        `;
        text.textContent = message;
        
        overlay.appendChild(spinner);
        overlay.appendChild(text);
        document.body.appendChild(overlay);
        
        // Add spinner animation
        if (!document.getElementById('spinnerStyle')) {
            const style = document.createElement('style');
            style.id = 'spinnerStyle';
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
    } else {
        overlay.style.display = 'flex';
        updateLoadingMessage(message);
    }
}

/**
 * Update loading message
 */
function updateLoadingMessage(message) {
    const text = document.getElementById('loadingText');
    if (text) {
        text.textContent = message;
    }
}

/**
 * Hide loading overlay
 */
function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// ==================== INDICATORS AUTO-SAVE ====================

let indicatorsAutoSaveTimer = null;

/**
 * Save activeIndicators to IndexedDB
 */
async function saveActiveIndicators() {
    try {
        if (!db) {
            await initIndexedDB();
        }
        
        const transaction = db.transaction(['indicators'], 'readwrite');
        const store = transaction.objectStore('indicators');
        
        const dataToSave = {
            id: 'active_indicators',
            indicators: activeIndicators,
            timestamp: Date.now()
        };
        
        store.put(dataToSave);
        console.log('💾 Auto-saved activeIndicators:', activeIndicators.length, 'indicators');
        
    } catch (error) {
        console.error('❌ Error auto-saving indicators:', error);
    }
}

/**
 * Load activeIndicators from IndexedDB
 */
async function loadActiveIndicators() {
    try {
        if (!db) {
            await initIndexedDB();
        }
        
        const transaction = db.transaction(['indicators'], 'readonly');
        const store = transaction.objectStore('indicators');
        const request = store.get('active_indicators');
        
        return new Promise((resolve, reject) => {
            request.onsuccess = () => {
                if (request.result && request.result.indicators) {
                    console.log('✅ Loaded activeIndicators from IndexedDB:', request.result.indicators.length, 'indicators');
                    resolve(request.result.indicators);
                } else {
                    console.log('ℹ️ No activeIndicators in IndexedDB');
                    resolve(null);
                }
            };
            request.onerror = () => {
                console.error('❌ Error loading indicators:', request.error);
                resolve(null);
            };
        });
        
    } catch (error) {
        console.error('❌ Error in loadActiveIndicators:', error);
        return null;
    }
}

/**
 * Trigger auto-save with debounce (1 second)
 */
function triggerIndicatorsAutoSave() {
    clearTimeout(indicatorsAutoSaveTimer);
    indicatorsAutoSaveTimer = setTimeout(() => {
        saveActiveIndicators();
    }, 1000); // Save after 1 second of no changes
}

/**
 * Initialize and restore indicators on page load
 */
async function initIndicatorsAutoSave() {
    try {
        // Try to load saved indicators
        const savedIndicators = await loadActiveIndicators();
        
        if (savedIndicators && savedIndicators.length > 0) {
            activeIndicators = savedIndicators;
            console.log('✅ Restored', activeIndicators.length, 'indicators with display settings');
            
            // Update display panel if it exists
            if (typeof updateIndicatorsDisplayPanel === 'function') {
                setTimeout(() => updateIndicatorsDisplayPanel(), 500);
            }
            
            // Render indicators on chart if available
            if (typeof calculateAndRenderIndicators === 'function') {
                setTimeout(() => calculateAndRenderIndicators(), 1000);
            }
        }
    } catch (error) {
        console.error('❌ Error initializing indicators auto-save:', error);
    }
}

// Export functions for global use
window.showTimeframeModalFirst = showTimeframeModalFirst;
window.handleFileUpload = handleFileUpload;
window.clearOfflineData = clearOfflineData;
window.saveActiveIndicators = saveActiveIndicators;
window.loadActiveIndicators = loadActiveIndicators;
window.triggerIndicatorsAutoSave = triggerIndicatorsAutoSave;
window.closeTimeframeModal = closeTimeframeModal;
window.confirmTimeframeAndUpload = confirmTimeframeAndUpload;

// Auto-initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDataManager);
} else {
    initDataManager();
}
