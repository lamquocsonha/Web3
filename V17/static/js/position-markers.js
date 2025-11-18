/**
 * Position Markers Manager
 * Hiển thị trạng thái mở lệnh Long/Short trên chart
 */

// Global state for position markers
let activePositionMarkers = {};
let positionPriceLines = {};

/**
 * Add position marker to chart
 * @param {Object} position - Position object {id, side, entryPrice, entryTime, symbol}
 */
function addPositionMarker(position) {
    // Check if chart exists (strategy uses workspaceChart, index uses chart)
    const chartInstance = typeof workspaceChart !== 'undefined' ? workspaceChart : (typeof chart !== 'undefined' ? chart : null);
    const candleSeries = typeof workspaceCandlestickSeries !== 'undefined' ? workspaceCandlestickSeries : (typeof window.candlestickSeries !== 'undefined' ? window.candlestickSeries : null);

    if (!chartInstance || !candleSeries) {
        console.warn('Chart not ready for position marker');
        return;
    }

    // Remove existing marker if any
    if (activePositionMarkers[position.id]) {
        removePositionMarker(position.id);
    }

    const isLong = position.side === 'LONG' || position.side === 'BUY';
    const bgColor = isLong ? 'rgba(38, 166, 154, 0.15)' : 'rgba(239, 83, 80, 0.15)';
    const borderColor = isLong ? '#26a69a' : '#ef5350';
    const textColor = isLong ? '#26a69a' : '#ef5350';

    // Format entry time
    const entryTime = position.entryTime || new Date().toLocaleTimeString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });

    // Create marker box
    const markerBox = document.createElement('div');
    markerBox.id = `position-marker-${position.id}`;
    markerBox.style.cssText = `
        position: fixed;
        top: 100px;
        right: ${isLong ? '20px' : '180px'};
        background: ${bgColor};
        border: 2px solid ${borderColor};
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 13px;
        font-weight: 600;
        color: ${textColor};
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        min-width: 140px;
        animation: slideInRight 0.3s ease-out;
    `;

    markerBox.innerHTML = `
        <div style="font-size: 16px; font-weight: 700; margin-bottom: 8px; text-align: center;">
            ${isLong ? '📈 LONG' : '📉 SHORT'}
        </div>
        <div style="font-size: 12px; color: #d1d4dc; margin-bottom: 4px;">
            Entry: <span style="color: ${textColor}; font-weight: 700;">${position.entryPrice.toFixed(2)}</span>
        </div>
        <div style="font-size: 11px; color: #787b86;">
            ${entryTime}
        </div>
    `;

    // Add to DOM
    document.body.appendChild(markerBox);

    // Store reference
    activePositionMarkers[position.id] = markerBox;

    // Add price line on chart
    try {
        const priceLine = candleSeries.createPriceLine({
            price: position.entryPrice,
            color: borderColor,
            lineWidth: 2,
            lineStyle: 2, // Dashed
            axisLabelVisible: true,
            title: `${isLong ? 'Long' : 'Short'} Entry`,
        });

        positionPriceLines[position.id] = priceLine;
        console.log(`✅ Added ${position.side} position marker at ${position.entryPrice}`);
    } catch (e) {
        console.error('Error adding price line:', e);
    }
}

/**
 * Remove position marker from chart
 * @param {number|string} positionId - Position ID
 */
function removePositionMarker(positionId) {
    // Remove marker box
    if (activePositionMarkers[positionId]) {
        activePositionMarkers[positionId].remove();
        delete activePositionMarkers[positionId];
    }

    // Remove price line
    const candleSeries = typeof workspaceCandlestickSeries !== 'undefined' ? workspaceCandlestickSeries : (typeof window.candlestickSeries !== 'undefined' ? window.candlestickSeries : null);

    if (positionPriceLines[positionId] && candleSeries) {
        try {
            candleSeries.removePriceLine(positionPriceLines[positionId]);
            delete positionPriceLines[positionId];
            console.log(`✅ Removed position marker ${positionId}`);
        } catch (e) {
            console.error('Error removing price line:', e);
        }
    }
}

/**
 * Update position markers based on positions array
 * @param {Array} positions - Array of position objects
 */
function updatePositionMarkers(positions) {
    console.log('📊 Updating position markers, count:', positions ? positions.length : 0);

    // Remove all existing markers
    Object.keys(activePositionMarkers).forEach(id => {
        removePositionMarker(id);
    });

    // Add markers for open positions
    if (positions && positions.length > 0) {
        positions.forEach(position => {
            if (position.status === 'Open' || !position.status) {
                addPositionMarker(position);
            }
        });
    }
}

/**
 * Clear all position markers
 */
function clearAllPositionMarkers() {
    Object.keys(activePositionMarkers).forEach(id => {
        removePositionMarker(id);
    });
    console.log('🗑️ Cleared all position markers');
}

// Initialize - listen for position updates if socket is available
if (typeof socket !== 'undefined') {
    socket.on('position_update', (data) => {
        console.log('📡 Position update received:', data);
        if (data.positions) {
            updatePositionMarkers(data.positions);
        }
    });

    // Also listen for position_opened event (if exists)
    socket.on('position_opened', (position) => {
        console.log('📡 Position opened:', position);
        addPositionMarker(position);
    });

    // Listen for position_closed event
    socket.on('position_closed', (data) => {
        console.log('📡 Position closed:', data);
        if (data.positionId || data.id) {
            removePositionMarker(data.positionId || data.id);
        }
    });
}

/**
 * Test function - Add test position markers
 */
function testPositionMarkers() {
    console.log('🧪 Testing position markers...');

    // Test Long position
    const testLongPosition = {
        id: 'test_long_' + Date.now(),
        side: 'LONG',
        entryPrice: 1875.50,
        entryTime: new Date().toLocaleTimeString('vi-VN'),
        symbol: 'VN30F1M',
        status: 'Open'
    };

    // Test Short position
    const testShortPosition = {
        id: 'test_short_' + Date.now(),
        side: 'SHORT',
        entryPrice: 1880.00,
        entryTime: new Date().toLocaleTimeString('vi-VN'),
        symbol: 'VN30F1M',
        status: 'Open'
    };

    addPositionMarker(testLongPosition);
    setTimeout(() => {
        addPositionMarker(testShortPosition);
    }, 500);

    console.log('✅ Test markers added. Use clearAllPositionMarkers() to remove.');
}

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

console.log('✅ Position Markers Manager initialized');
console.log('💡 Use testPositionMarkers() to test markers manually');
