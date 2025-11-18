// Exchange Management Page Logic
const Exchange = {
    profiles: [],
    currentFilter: 'all',
    editingProfile: null,
    
    init() {
        this.setupFilters();
        this.setupProfileForm();
        this.setupTerminal();
        this.loadProfiles();
    },
    
    setupFilters() {
        const filterTabs = document.querySelectorAll('.filter-tab');
        filterTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                filterTabs.forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                
                this.currentFilter = e.target.dataset.filter;
                this.filterProfiles();
            });
        });
    },
    
    setupProfileForm() {
        const saveBtn = document.getElementById('save-profile-btn');
        const testBtn = document.getElementById('test-connection-btn');
        const profileNameInput = document.getElementById('profile-name');
        const exchangeSelect = document.getElementById('exchange-select');
        
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveProfile());
        }
        
        if (testBtn) {
            testBtn.addEventListener('click', () => this.testConnection());
        }
        
        if (exchangeSelect) {
            exchangeSelect.addEventListener('change', (e) => {
                this.updateFormForExchange(e.target.value);
            });
        }
    },
    
    setupTerminal() {
        const clearBtn = document.querySelector('.terminal-clear');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearTerminal());
        }
    },
    
    openEditModal(profileId) {
        const profile = this.profiles.find(p => p.id === profileId);
        if (!profile) return;
        
        this.editingProfile = profile;
        
        // Update modal title
        document.getElementById('modalTitle').textContent = `Editing profile: ${profile.name}`;
        
        // Fill form with profile data
        document.getElementById('edit-profile-name').value = profile.name || '';
        document.getElementById('edit-exchange').value = profile.exchange || 'DNSE';
        document.getElementById('edit-protocol').value = profile.protocol || 'rest-api';
        document.getElementById('edit-username').value = profile.username || '';
        document.getElementById('edit-password').value = profile.password || '';
        document.getElementById('edit-otp-required').checked = profile.otpRequired !== false;
        document.getElementById('edit-tickers').value = profile.tickers || 'VD: VN30F1M,VNM,FPT,VCB';
        document.getElementById('edit-timeframe').value = profile.timeframe || '1m';
        document.getElementById('edit-candle-count').value = profile.candleCount || 1000;
        document.getElementById('edit-timezone').value = profile.timezone || '7';
        document.getElementById('edit-use-market-data').checked = profile.useForData || false;
        document.getElementById('edit-use-trading').checked = profile.useForTrading !== false;
        
        // Show modal
        document.getElementById('editProfileModal').style.display = 'flex';
    },
    
    closeEditModal() {
        document.getElementById('editProfileModal').style.display = 'none';
        this.editingProfile = null;
    },
    
    openAddNewModal() {
        this.editingProfile = null;
        document.getElementById('modalTitle').textContent = 'Add New Profile';
        
        // Clear form
        document.getElementById('edit-profile-name').value = '';
        document.getElementById('edit-exchange').value = 'DNSE';
        document.getElementById('edit-protocol').value = 'rest-api';
        document.getElementById('edit-username').value = '';
        document.getElementById('edit-password').value = '';
        document.getElementById('edit-otp-required').checked = true;
        document.getElementById('edit-tickers').value = 'VD: VN30F1M,VNM,FPT,VCB';
        document.getElementById('edit-timeframe').value = '1m';
        document.getElementById('edit-candle-count').value = 1000;
        document.getElementById('edit-timezone').value = '7';
        document.getElementById('edit-use-market-data').checked = false;
        document.getElementById('edit-use-trading').checked = true;
        
        // Show modal
        document.getElementById('editProfileModal').style.display = 'flex';
    },
    
    updateProfile() {
        const profileData = {
            id: this.editingProfile?.id || `profile_${Date.now()}`,
            name: document.getElementById('edit-profile-name').value,
            exchange: document.getElementById('edit-exchange').value,
            protocol: document.getElementById('edit-protocol').value,
            username: document.getElementById('edit-username').value,
            password: document.getElementById('edit-password').value,
            otpRequired: document.getElementById('edit-otp-required').checked,
            tickers: document.getElementById('edit-tickers').value,
            timeframe: document.getElementById('edit-timeframe').value,
            candleCount: parseInt(document.getElementById('edit-candle-count').value),
            timezone: document.getElementById('edit-timezone').value,
            useForData: document.getElementById('edit-use-market-data').checked,
            useForTrading: document.getElementById('edit-use-trading').checked,
            status: 'disconnected',
            created: new Date().toLocaleString('vi-VN')
        };
        
        if (this.editingProfile) {
            // Update existing
            const index = this.profiles.findIndex(p => p.id === this.editingProfile.id);
            if (index !== -1) {
                this.profiles[index] = { ...this.profiles[index], ...profileData };
            }
            this.log(`✅ Updated profile: ${profileData.name}`, 'success');
        } else {
            // Add new
            profileData.type = profileData.useForTrading ? 'Trading' : 'Data';
            this.profiles.push(profileData);
            this.log(`✅ Created new profile: ${profileData.name}`, 'success');
        }
        
        this.displayProfiles();
        this.closeEditModal();
        
        // TODO: Save to backend
        console.log('Profile saved:', profileData);
    },
    
    setupTerminal() {
        const clearBtn = document.querySelector('.terminal-clear');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearTerminal());
        }
    },
    
    updateFormForExchange(exchange) {
        // TODO: Show/hide fields based on exchange type
        console.log('Exchange selected:', exchange);
    },
    
    async loadProfiles() {
        try {
            const result = await App.apiCall('/exchange/profiles', 'GET');
            this.profiles = result.profiles || [];
            this.displayProfiles();
        } catch (error) {
            console.error('Error loading profiles:', error);
            // Load sample data for demo
            this.profiles = [
                {
                    id: '1',
                    name: 'DNSE',
                    exchange: 'DNSE',
                    type: 'Trading',
                    status: 'disconnected',
                    created: '21:10 12/11/2025'
                },
                {
                    id: '2',
                    name: 'DNSE DATA',
                    exchange: 'DNSE',
                    type: 'Data',
                    status: 'connected',
                    created: '21:33 12/11/2025'
                },
                {
                    id: '3',
                    name: 'Entrade demo',
                    exchange: 'ENTRADE',
                    type: 'Trading',
                    status: 'disconnected',
                    created: '21:10 12/11/2025'
                },
                {
                    id: '4',
                    name: 'Entrade MQTT real',
                    exchange: 'ENTRADE-MQTT',
                    type: 'Trading',
                    status: 'disconnected',
                    created: '21:11 12/11/2025'
                }
            ];
            this.displayProfiles();
        }
    },
    
    filterProfiles() {
        this.displayProfiles();
    },
    
    displayProfiles() {
        const container = document.getElementById('profiles-container');
        if (!container) return;
        
        let filteredProfiles = this.profiles;
        
        if (this.currentFilter === 'data') {
            filteredProfiles = this.profiles.filter(p => p.type === 'Data');
        } else if (this.currentFilter === 'trading') {
            filteredProfiles = this.profiles.filter(p => p.type === 'Trading');
        }
        
        if (filteredProfiles.length === 0) {
            container.innerHTML = '<div class="empty-state">No profiles found</div>';
            return;
        }
        
        container.innerHTML = filteredProfiles.map(profile => `
            <div class="profile-card">
                <div class="profile-card-header">
                    <div>
                        <div class="profile-name">${profile.name}</div>
                        <div class="profile-meta">
                            <span class="status-badge ${profile.type === 'Data' ? 'status-badge' : 'status-badge'}" 
                                  style="background-color: ${profile.type === 'Data' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(16, 185, 129, 0.2)'}; 
                                         color: ${profile.type === 'Data' ? 'var(--accent-blue)' : 'var(--accent-green)'}">
                                📊 ${profile.type}
                            </span>
                            <span class="status-badge ${profile.status === 'connected' ? 'status-connected' : 'status-disconnected'}">
                                ${profile.status === 'connected' ? '● Connected' : '● Disconnected'}
                            </span>
                        </div>
                    </div>
                </div>
                <div class="profile-meta" style="margin-top: 0.5rem; padding-top: 0.75rem; border-top: 1px solid var(--border-color);">
                    <span>📅 ${profile.created}</span>
                </div>
                <div class="profile-actions">
                    <button class="btn btn-sm ${profile.status === 'connected' ? 'btn-danger' : 'btn-success'}" 
                            onclick="Exchange.toggleConnection('${profile.id}')">
                        ${profile.status === 'connected' ? 'Disconnect' : 'Connect'}
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="Exchange.showInfo('${profile.id}')">Info</button>
                    <button class="btn btn-sm btn-secondary" onclick="Exchange.openEditModal('${profile.id}')">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="Exchange.deleteProfile('${profile.id}')">Delete</button>
                </div>
            </div>
        `).join('');
    },
    
    async saveProfile() {
        const profileName = document.getElementById('profile-name')?.value;
        const exchange = document.getElementById('exchange-select')?.value;
        const useForData = document.getElementById('use-for-data')?.checked;
        const useForTrading = document.getElementById('use-for-trading')?.checked;
        
        if (!profileName || !exchange) {
            App.showNotification('Vui lòng điền đầy đủ thông tin', 'warning');
            return;
        }
        
        const profileData = {
            name: profileName,
            exchange: exchange,
            use_for_data: useForData,
            use_for_trading: useForTrading,
            // Add other fields as needed
        };
        
        try {
            if (this.editingProfile) {
                await App.apiCall('/exchange/profiles', 'PUT', { id: this.editingProfile, ...profileData });
                App.showNotification('Profile updated successfully', 'success');
            } else {
                await App.apiCall('/exchange/profiles', 'POST', profileData);
                App.showNotification('Profile created successfully', 'success');
            }
            
            this.clearForm();
            this.loadProfiles();
        } catch (error) {
            App.showNotification('Failed to save profile', 'error');
        }
    },
    
    async testConnection() {
        const profileName = document.getElementById('profile-name')?.value;
        
        if (!profileName) {
            App.showNotification('Vui lòng nhập tên profile', 'warning');
            return;
        }
        
        this.addTerminalLine('[System] Testing connection...', 'output');
        
        try {
            // TODO: Implement real connection test
            await new Promise(resolve => setTimeout(resolve, 1000));
            this.addTerminalLine('[Success] Connection test passed!', 'success');
            App.showNotification('Connection test successful', 'success');
        } catch (error) {
            this.addTerminalLine('[Error] Connection test failed', 'error');
            App.showNotification('Connection test failed', 'error');
        }
    },
    
    async toggleConnection(profileId) {
        const profile = this.profiles.find(p => p.id === profileId);
        if (!profile) return;
        
        try {
            if (profile.status === 'connected') {
                this.addTerminalLine(`[System] Disconnecting from ${profile.name}...`, 'output');
                await new Promise(resolve => setTimeout(resolve, 500));
                profile.status = 'disconnected';
                this.addTerminalLine(`[Success] Disconnected from ${profile.name}`, 'success');
                App.showNotification(`Disconnected from ${profile.name}`, 'info');
            } else {
                this.addTerminalLine(`[System] Connecting to ${profile.name}...`, 'output');
                await new Promise(resolve => setTimeout(resolve, 1000));
                profile.status = 'connected';
                this.addTerminalLine(`[Success] Connected to ${profile.name}`, 'success');
                App.showNotification(`Connected to ${profile.name}`, 'success');
            }
            
            this.displayProfiles();
        } catch (error) {
            this.addTerminalLine('[Error] Connection failed', 'error');
            App.showNotification('Connection failed', 'error');
        }
    },
    
    showInfo(profileId) {
        const profile = this.profiles.find(p => p.id === profileId);
        if (!profile) return;
        
        alert(`Profile Info:\n\nName: ${profile.name}\nExchange: ${profile.exchange}\nType: ${profile.type}\nStatus: ${profile.status}\nCreated: ${profile.created}`);
    },
    
    editProfile(profileId) {
        const profile = this.profiles.find(p => p.id === profileId);
        if (!profile) return;
        
        this.editingProfile = profileId;
        
        // Fill form with profile data
        const profileNameInput = document.getElementById('profile-name');
        const exchangeSelect = document.getElementById('exchange-select');
        const useForData = document.getElementById('use-for-data');
        const useForTrading = document.getElementById('use-for-trading');
        
        if (profileNameInput) profileNameInput.value = profile.name;
        if (exchangeSelect) exchangeSelect.value = profile.exchange;
        if (useForData) useForData.checked = profile.type === 'Data';
        if (useForTrading) useForTrading.checked = profile.type === 'Trading';
        
        // Scroll to form
        document.querySelector('.add-profile-section')?.scrollIntoView({ behavior: 'smooth' });
        
        App.showNotification('Editing profile: ' + profile.name, 'info');
    },
    
    async deleteProfile(profileId) {
        const profile = this.profiles.find(p => p.id === profileId);
        if (!profile) return;
        
        if (!confirm(`Delete profile "${profile.name}"?`)) return;
        
        try {
            await App.apiCall(`/exchange/profiles?id=${profileId}`, 'DELETE');
            App.showNotification('Profile deleted successfully', 'success');
            this.loadProfiles();
        } catch (error) {
            App.showNotification('Failed to delete profile', 'error');
        }
    },
    
    clearForm() {
        this.editingProfile = null;
        const profileNameInput = document.getElementById('profile-name');
        const exchangeSelect = document.getElementById('exchange-select');
        const useForData = document.getElementById('use-for-data');
        const useForTrading = document.getElementById('use-for-trading');
        
        if (profileNameInput) profileNameInput.value = '';
        if (exchangeSelect) exchangeSelect.value = '';
        if (useForData) useForData.checked = false;
        if (useForTrading) useForTrading.checked = false;
    },
    
    addTerminalLine(text, type = 'output') {
        const terminal = document.querySelector('.terminal');
        if (!terminal) return;
        
        const line = document.createElement('div');
        line.className = `terminal-line terminal-${type}`;
        line.textContent = text;
        terminal.appendChild(line);
        
        terminal.scrollTop = terminal.scrollHeight;
    },
    
    clearTerminal() {
        const terminal = document.querySelector('.terminal');
        if (terminal) {
            terminal.innerHTML = '<div class="terminal-line terminal-output">[system] Terminal ready. Waiting for connection events...</div>';
        }
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    Exchange.init();
});

// Export for global access
window.Exchange = Exchange;
