// Clients Management Page Logic
const Clients = {
    clients: [],
    editingClient: null,
    exchangeProfilesCount: 0,
    
    init() {
        this.setupAddButton();
        this.setupTradeFilters();
        this.loadClients();
    },
    
    setupAddButton() {
        const addBtn = document.getElementById('add-client-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.openModal());
        }
    },
    
    setupTradeFilters() {
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                filterBtns.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.filterTrades(e.target.dataset.filter);
            });
        });
    },
    
    async loadClients() {
        try {
            const result = await App.apiCall('/clients', 'GET');
            this.clients = result.clients || [];
            this.displayClients();
        } catch (error) {
            console.error('Error loading clients:', error);
            // Load sample data for demo
            this.clients = [
                {
                    id: '1',
                    name: 'Nguyễn Thành Luân',
                    nickname: 'Tí chuột',
                    email: 'nguyenvanb@gmail.com',
                    phone: '123456789',
                    status: 'active',
                    profiles: [
                        { name: 'Entrade', status: 'disconnected' }
                    ],
                    totalTrades: 0,
                    totalPnl: 0
                },
                {
                    id: '2',
                    name: 'Lê Quang Hưng',
                    nickname: 'Hưng rèo',
                    email: 'nguyenvana@example.com',
                    phone: '0912345678',
                    status: 'active',
                    profiles: [
                        { name: 'Entrade Real', status: 'disconnected' }
                    ],
                    totalTrades: 0,
                    totalPnl: 0
                }
            ];
            this.displayClients();
        }
    },
    
    displayClients() {
        const container = document.getElementById('clients-container');
        if (!container) return;
        
        if (this.clients.length === 0) {
            container.innerHTML = '<div class="empty-state" style="padding: 3rem; text-align: center; color: var(--text-muted);">Chưa có client nào. Click "Thêm Client" để thêm mới.</div>';
            return;
        }
        
        container.innerHTML = this.clients.map(client => `
            <div class="client-card">
                <div class="client-header">
                    <div>
                        <div class="client-name">${client.name}</div>
                        <div class="client-nickname">(${client.nickname})</div>
                    </div>
                    <span class="status-badge status-${client.status}">
                        ${client.status === 'active' ? '✓ Active' : '● Inactive'}
                    </span>
                </div>
                
                <div class="client-info">
                    <div class="client-info-item">
                        <span>📧</span>
                        <span>${client.email}</span>
                    </div>
                    <div class="client-info-item">
                        <span>📱</span>
                        <span>${client.phone}</span>
                    </div>
                </div>
                
                <div class="client-profiles">
                    <div class="client-profiles-title">Exchange Profiles:</div>
                    ${client.profiles.map(profile => `
                        <div class="client-profile-item">
                            <span>${profile.name}</span>
                            <span class="status-badge status-${profile.status}">
                                ${profile.status === 'connected' ? '● Connected' : '● Disconnected'}
                            </span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="client-stats">
                    <div class="client-stat">
                        <div class="client-stat-label">TOTAL TRADES</div>
                        <div class="client-stat-value">${client.totalTrades}</div>
                    </div>
                    <div class="client-stat">
                        <div class="client-stat-label">TOTAL PNL</div>
                        <div class="client-stat-value ${client.totalPnl >= 0 ? 'text-success' : 'text-danger'}">
                            ${client.totalPnl >= 0 ? '+' : ''}${client.totalPnl} VND
                        </div>
                    </div>
                </div>
                
                <div class="client-actions">
                    <button class="btn btn-primary" onclick="Clients.editClient('${client.id}')">
                        ✏️ Edit
                    </button>
                    <button class="btn btn-warning" onclick="Clients.viewReports('${client.id}')">
                        📊 Reports
                    </button>
                    <button class="btn btn-danger" onclick="Clients.deleteClient('${client.id}')">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `).join('');
    },
    
    openModal(clientId = null) {
        this.editingClient = clientId ? this.clients.find(c => c.id === clientId) : null;
        this.exchangeProfilesCount = 0;
        
        // Update modal title
        document.getElementById('clientModalTitle').textContent = clientId ? 'Chỉnh Sửa Client' : 'Thêm Client Mới';
        
        // Fill form
        if (this.editingClient) {
            document.getElementById('client-name').value = this.editingClient.name + (this.editingClient.nickname ? ` (${this.editingClient.nickname})` : '');
            document.getElementById('client-email').value = this.editingClient.email || '';
            document.getElementById('client-phone').value = this.editingClient.phone || '';
            document.getElementById('client-notes').value = this.editingClient.notes || '';
            
            // Load exchange profiles
            const profilesList = document.getElementById('exchangeProfilesList');
            profilesList.innerHTML = '';
            if (this.editingClient.profiles && this.editingClient.profiles.length > 0) {
                this.editingClient.profiles.forEach((profile, index) => {
                    this.addExchangeProfile(profile);
                });
            }
        } else {
            // Clear form
            document.getElementById('client-name').value = '';
            document.getElementById('client-email').value = '';
            document.getElementById('client-phone').value = '';
            document.getElementById('client-notes').value = '';
            document.getElementById('exchangeProfilesList').innerHTML = '';
        }
        
        // Show modal
        document.getElementById('clientModal').style.display = 'flex';
    },
    
    closeModal() {
        document.getElementById('clientModal').style.display = 'none';
        this.editingClient = null;
        this.exchangeProfilesCount = 0;
    },
    
    addExchangeProfile(existingProfile = null) {
        const profileId = `profile_${this.exchangeProfilesCount++}`;
        const container = document.getElementById('exchangeProfilesList');
        
        const profileDiv = document.createElement('div');
        profileDiv.className = 'exchange-profile-item';
        profileDiv.id = profileId;
        profileDiv.innerHTML = `
            <div class="profile-item-header">
                <h6>Exchange Profile ${this.exchangeProfilesCount}</h6>
                <button class="btn btn-sm btn-danger" onclick="Clients.removeExchangeProfile('${profileId}')">
                    🗑️ Xóa
                </button>
            </div>
            
            <div class="form-group">
                <label class="form-label">Tên Profile</label>
                <input type="text" class="form-control profile-name" placeholder="Entrade" value="${existingProfile?.name || ''}">
            </div>
            
            <div class="form-row">
                <div class="form-group" style="flex: 1;">
                    <label class="form-label">Exchange</label>
                    <select class="form-control profile-exchange">
                        <option value="Entrade" ${existingProfile?.exchange === 'Entrade' ? 'selected' : ''}>Entrade</option>
                        <option value="DNSE" ${existingProfile?.exchange === 'DNSE' ? 'selected' : ''}>DNSE</option>
                        <option value="MT5" ${existingProfile?.exchange === 'MT5' ? 'selected' : ''}>MT5</option>
                    </select>
                </div>
                <div class="form-group" style="flex: 1;">
                    <label class="form-label">Protocol</label>
                    <select class="form-control profile-protocol">
                        <option value="REST API" ${existingProfile?.protocol === 'REST API' ? 'selected' : ''}>REST API</option>
                        <option value="WebSocket" ${existingProfile?.protocol === 'WebSocket' ? 'selected' : ''}>WebSocket</option>
                        <option value="MQTT" ${existingProfile?.protocol === 'MQTT' ? 'selected' : ''}>MQTT</option>
                    </select>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group" style="flex: 1;">
                    <label class="form-label">Username</label>
                    <input type="text" class="form-control profile-username" placeholder="Username" value="${existingProfile?.username || ''}">
                </div>
                <div class="form-group" style="flex: 1;">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-control profile-password" placeholder="Password" value="${existingProfile?.password || ''}">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group" style="flex: 1;">
                    <label class="form-label">Volume Multiplier</label>
                    <input type="number" class="form-control profile-volume-multiplier" value="${existingProfile?.volumeMultiplier || 1}" min="1">
                </div>
                <div class="form-group" style="flex: 1;">
                    <label class="form-label">Max Position Size</label>
                    <input type="number" class="form-control profile-max-position" value="${existingProfile?.maxPosition || 5}" min="1">
                </div>
            </div>
        `;
        
        container.appendChild(profileDiv);
    },
    
    removeExchangeProfile(profileId) {
        const element = document.getElementById(profileId);
        if (element) {
            element.remove();
        }
    },
    
    saveClient() {
        const name = document.getElementById('client-name').value.trim();
        const email = document.getElementById('client-email').value.trim();
        const phone = document.getElementById('client-phone').value.trim();
        const notes = document.getElementById('client-notes').value.trim();
        
        if (!name || !email || !phone) {
            alert('Vui lòng điền đầy đủ thông tin bắt buộc (Tên, Email, Số điện thoại)');
            return;
        }
        
        // Extract nickname from name if present
        let clientName = name;
        let nickname = '';
        const nicknameMatch = name.match(/\(([^)]+)\)/);
        if (nicknameMatch) {
            nickname = nicknameMatch[1];
            clientName = name.replace(/\s*\([^)]+\)/, '').trim();
        }
        
        // Collect exchange profiles
        const profiles = [];
        document.querySelectorAll('.exchange-profile-item').forEach(item => {
            profiles.push({
                name: item.querySelector('.profile-name').value,
                exchange: item.querySelector('.profile-exchange').value,
                protocol: item.querySelector('.profile-protocol').value,
                username: item.querySelector('.profile-username').value,
                password: item.querySelector('.profile-password').value,
                volumeMultiplier: parseInt(item.querySelector('.profile-volume-multiplier').value),
                maxPosition: parseInt(item.querySelector('.profile-max-position').value),
                status: 'disconnected'
            });
        });
        
        const clientData = {
            id: this.editingClient?.id || `client_${Date.now()}`,
            name: clientName,
            nickname: nickname,
            email: email,
            phone: phone,
            notes: notes,
            profiles: profiles,
            status: 'active',
            totalTrades: this.editingClient?.totalTrades || 0,
            totalPnl: this.editingClient?.totalPnl || 0
        };
        
        if (this.editingClient) {
            // Update existing
            const index = this.clients.findIndex(c => c.id === this.editingClient.id);
            if (index !== -1) {
                this.clients[index] = clientData;
            }
        } else {
            // Add new
            this.clients.push(clientData);
        }
        
        this.displayClients();
        this.closeModal();
    },
    
    editClient(clientId) {
        this.openModal(clientId);
    },
    
    viewReports(clientId) {
        const client = this.clients.find(c => c.id === clientId);
        if (!client) return;
        
        // Hide main content, show reports page
        document.querySelector('.clients-grid').closest('div').style.display = 'none';
        document.getElementById('clientReportsPage').style.display = 'block';
        
        // Update reports page data
        document.getElementById('reportsClientName').textContent = client.name + (client.nickname ? ` (${client.nickname})` : '');
        document.getElementById('reportsClientContact').textContent = `${client.email} • ${client.phone}`;
        document.getElementById('reportsTotalTrades').textContent = client.totalTrades || 0;
        document.getElementById('reportsWinRate').textContent = '0.0%';
        document.getElementById('reportsTotalPnl').textContent = `${client.totalPnl >= 0 ? '+' : ''}${client.totalPnl} VND`;
        document.getElementById('reportsAvgWin').textContent = '+0';
        document.getElementById('reportsAvgLoss').textContent = '0';
        document.getElementById('reportsProfitFactor').textContent = '0.00';
        
        // Load trade history (placeholder)
        this.loadTradeHistory(clientId);
    },
    
    closeReportsPage() {
        document.getElementById('clientReportsPage').style.display = 'none';
        document.querySelector('.clients-grid').closest('div').style.display = 'block';
    },
    
    loadTradeHistory(clientId) {
        // Placeholder - will be populated with real data
        const tbody = document.getElementById('tradeHistoryBody');
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px; color: var(--text-muted);">No trades found</td></tr>';
    },
    
    filterTrades(filter) {
        // Placeholder for trade filtering
        console.log('Filter trades:', filter);
    },
    
    async deleteClient(clientId) {
        const client = this.clients.find(c => c.id === clientId);
        if (!client) return;
        
        if (!confirm(`Xóa client "${client.name}"?\n\nThao tác này không thể hoàn tác.`)) return;
        
        try {
            await App.apiCall(`/clients?id=${clientId}`, 'DELETE');
            App.showNotification('Xóa client thành công', 'success');
            this.loadClients();
        } catch (error) {
            App.showNotification('Xóa client thất bại', 'error');
        }
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    Clients.init();
});

// Export for global access
window.Clients = Clients;
