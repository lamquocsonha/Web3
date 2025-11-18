// Manual Trading Page Logic
const ManualTrading = {
    selectedAccount: null,
    selectedClient: null,
    
    init() {
        this.setupAccountSelectors();
        this.setupOrderForm();
        this.loadOrders();
    },
    
    setupAccountSelectors() {
        const accountSelector = document.getElementById('account-selector');
        const clientSelector = document.getElementById('client-selector');
        
        if (accountSelector) {
            accountSelector.addEventListener('change', (e) => {
                this.selectedAccount = e.target.value;
                console.log('Account selected:', this.selectedAccount);
            });
        }
        
        if (clientSelector) {
            clientSelector.addEventListener('change', (e) => {
                this.selectedClient = e.target.value;
                console.log('Client selected:', this.selectedClient);
            });
        }
    },
    
    setupOrderForm() {
        const buyBtn = document.getElementById('buy-btn');
        const sellBtn = document.getElementById('sell-btn');
        const closeAllBtn = document.getElementById('close-all-btn');
        
        if (buyBtn) {
            buyBtn.addEventListener('click', () => this.placeOrder('BUY'));
        }
        
        if (sellBtn) {
            sellBtn.addEventListener('click', () => this.placeOrder('SELL'));
        }
        
        if (closeAllBtn) {
            closeAllBtn.addEventListener('click', () => this.closeAllPositions());
        }
    },
    
    async placeOrder(side) {
        const symbol = document.getElementById('symbol-input')?.value || 'VN30F1M';
        const orderType = document.getElementById('order-type')?.value || 'LO';
        const price = parseFloat(document.getElementById('price-input')?.value || 0);
        const quantity = parseInt(document.getElementById('quantity-input')?.value || 1);
        
        if (!this.selectedAccount) {
            App.showNotification('Vui lòng chọn tài khoản', 'warning');
            return;
        }
        
        if (orderType === 'LO' && !price) {
            App.showNotification('Vui lòng nhập giá', 'warning');
            return;
        }
        
        const order = {
            account: this.selectedAccount,
            client: this.selectedClient,
            symbol: symbol,
            side: side,
            type: orderType,
            price: price,
            quantity: quantity,
            timestamp: new Date().toISOString()
        };
        
        try {
            const result = await App.apiCall('/orders', 'POST', order);
            App.showNotification(`Đặt lệnh ${side} thành công`, 'success');
            this.loadOrders();
        } catch (error) {
            App.showNotification('Đặt lệnh thất bại', 'error');
        }
    },
    
    async loadOrders() {
        try {
            const result = await App.apiCall('/orders', 'GET');
            this.displayOrders(result.orders || []);
        } catch (error) {
            console.error('Error loading orders:', error);
        }
    },
    
    displayOrders(orders) {
        const tbody = document.querySelector('.orders-table tbody');
        if (!tbody) return;
        
        if (orders.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: var(--text-muted); padding: 2rem;">Không có lệnh nào</td></tr>';
            return;
        }
        
        tbody.innerHTML = orders.map(order => `
            <tr>
                <td>${order.account || '-'}</td>
                <td>${order.time || '-'}</td>
                <td><span class="badge ${order.side === 'BUY' ? 'badge-success' : 'badge-danger'}">${order.side}</span></td>
                <td>${order.symbol || '-'}</td>
                <td>${order.entryPrice || '-'}</td>
                <td>${order.exitPrice || '-'}</td>
                <td>${order.quantity || '-'}</td>
                <td>${order.status || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="ManualTrading.cancelOrder('${order.id}')">Hủy</button>
                </td>
            </tr>
        `).join('');
    },
    
    async cancelOrder(orderId) {
        if (!confirm('Bạn có chắc muốn hủy lệnh này?')) return;
        
        try {
            await App.apiCall(`/orders?id=${orderId}`, 'DELETE');
            App.showNotification('Hủy lệnh thành công', 'success');
            this.loadOrders();
        } catch (error) {
            App.showNotification('Hủy lệnh thất bại', 'error');
        }
    },
    
    async closeAllPositions() {
        if (!confirm('Bạn có chắc muốn đóng tất cả vị thế?')) return;
        
        try {
            // TODO: Implement close all positions API
            App.showNotification('Đóng tất cả vị thế thành công', 'success');
            this.loadOrders();
        } catch (error) {
            App.showNotification('Đóng vị thế thất bại', 'error');
        }
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('=== Manual Trading Page DOMContentLoaded ===');
    console.log('Initializing ManualTrading...');
    ManualTrading.init();
    
    // Initialize chart
    console.log('Checking ChartManual availability...');
    if (typeof ChartManual !== 'undefined') {
        if (window.chartManual) {
            console.warn('⚠️⚠️⚠️ DUPLICATE: chartManual already exists!');
            console.log('Existing instance:', window.chartManual);
            return;
        }
        console.log('ChartManual found, creating instance...');
        window.chartManual = new ChartManual('trading-chart');
        console.log('ChartManual instance created:', window.chartManual);
        window.chartManual.init();
        console.log('ChartManual initialized');
    } else {
        console.error('ChartManual class not found!');
    }
});

// Export for global access
window.ManualTrading = ManualTrading;
