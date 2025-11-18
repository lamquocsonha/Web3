// ConnectionManager - Singleton quản lý kết nối cho Manual & Bot Trading
class ConnectionManager {
    constructor() {
        if (ConnectionManager.instance) {
            return ConnectionManager.instance;
        }
        
        this.isConnected = false;
        this.websocket = null;
        this.selectedExchange = null;
        this.selectedProfile = null;
        this.listeners = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        ConnectionManager.instance = this;
    }
    
    // Singleton instance
    static getInstance() {
        if (!ConnectionManager.instance) {
            ConnectionManager.instance = new ConnectionManager();
        }
        return ConnectionManager.instance;
    }
    
    // Kết nối tới exchange
    async connect(exchange, profile) {
        if (this.isConnected) {
            console.log('Already connected');
            return;
        }
        
        this.selectedExchange = exchange;
        this.selectedProfile = profile;
        
        try {
            // TODO: Implement real WebSocket connection
            // this.websocket = new WebSocket(`ws://localhost:8080/market-data`);
            
            // Simulate connection
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            this.isConnected = true;
            this.reconnectAttempts = 0;
            
            this.emit('connected', {
                exchange: exchange,
                profile: profile,
                timestamp: new Date().toISOString()
            });
            
            // Start market data feed
            this.startMarketDataFeed();
            
            return { success: true, message: 'Connected successfully' };
            
        } catch (error) {
            console.error('Connection failed:', error);
            this.emit('error', { message: 'Connection failed', error: error });
            throw error;
        }
    }
    
    // Ngắt kết nối
    disconnect() {
        if (!this.isConnected) {
            console.log('Not connected');
            return;
        }
        
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        this.isConnected = false;
        this.stopMarketDataFeed();
        
        this.emit('disconnected', {
            timestamp: new Date().toISOString()
        });
        
        return { success: true, message: 'Disconnected successfully' };
    }
    
    // Start market data feed (simulate)
    startMarketDataFeed() {
        this.marketDataInterval = setInterval(() => {
            if (!this.isConnected) return;
            
            // Generate mock tick data
            const tick = {
                symbol: 'VN30F1M',
                timestamp: new Date().toISOString(),
                open: this.randomPrice(1900, 1920),
                high: this.randomPrice(1920, 1940),
                low: this.randomPrice(1880, 1900),
                close: this.randomPrice(1900, 1920),
                volume: Math.floor(Math.random() * 10000) + 1000
            };
            
            this.emit('tick', tick);
        }, 1000); // Every 1 second
    }
    
    // Stop market data feed
    stopMarketDataFeed() {
        if (this.marketDataInterval) {
            clearInterval(this.marketDataInterval);
            this.marketDataInterval = null;
        }
    }
    
    // Subscribe to market data for specific symbol
    subscribe(symbol, timeframe) {
        if (!this.isConnected) {
            console.warn('Cannot subscribe: not connected');
            return;
        }
        
        // TODO: Send subscription message via WebSocket
        console.log(`Subscribed to ${symbol} ${timeframe}`);
        
        this.emit('subscribed', {
            symbol: symbol,
            timeframe: timeframe
        });
    }
    
    // Unsubscribe from market data
    unsubscribe(symbol) {
        if (!this.isConnected) {
            return;
        }
        
        // TODO: Send unsubscription message via WebSocket
        console.log(`Unsubscribed from ${symbol}`);
        
        this.emit('unsubscribed', {
            symbol: symbol
        });
    }
    
    // Event listener registration
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }
    
    // Remove event listener
    off(event, callback) {
        if (!this.listeners[event]) return;
        
        this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
    
    // Emit event to all listeners
    emit(event, data) {
        if (!this.listeners[event]) return;
        
        this.listeners[event].forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`Error in event listener for ${event}:`, error);
            }
        });
    }
    
    // Get connection status
    getStatus() {
        return {
            isConnected: this.isConnected,
            exchange: this.selectedExchange,
            profile: this.selectedProfile,
            reconnectAttempts: this.reconnectAttempts
        };
    }
    
    // Helper: Generate random price
    randomPrice(min, max) {
        return parseFloat((Math.random() * (max - min) + min).toFixed(2));
    }
    
    // Auto reconnect
    async autoReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnect attempts reached');
            this.emit('reconnect_failed', {
                attempts: this.reconnectAttempts
            });
            return;
        }
        
        this.reconnectAttempts++;
        
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
        
        try {
            await this.connect(this.selectedExchange, this.selectedProfile);
        } catch (error) {
            console.error('Reconnect failed:', error);
            // Try again after delay
            setTimeout(() => this.autoReconnect(), 5000);
        }
    }
}

// Export singleton instance
window.ConnectionManager = ConnectionManager.getInstance();
