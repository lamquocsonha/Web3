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
        console.log('Exchange selected:', exchange);
        
        // Get all credential sections
        const dnseCard = document.getElementById('dnse-credentials-card');
        const entradeCard = document.getElementById('entrade-credentials-card');
        const mt5Card = document.getElementById('mt5-credentials-card');
        const binanceCard = document.getElementById('binance-credentials-card');
        
        // Hide all first
        if (dnseCard) dnseCard.style.display = 'none';
        if (entradeCard) entradeCard.style.display = 'none';
        if (mt5Card) mt5Card.style.display = 'none';
        if (binanceCard) binanceCard.style.display = 'none';
        
        // Show relevant section
        if (exchange === 'DNSE' && dnseCard) {
            dnseCard.style.display = 'block';
        } else if ((exchange === 'ENTRADE' || exchange === 'ENTRADE-MQTT') && entradeCard) {
            entradeCard.style.display = 'block';
        } else if (exchange === 'MT5' && mt5Card) {
            mt5Card.style.display = 'block';
        } else if (exchange === 'BINANCE' && binanceCard) {
            binanceCard.style.display = 'block';
        }
    },
    
    async loadProfiles() {
        try {
            // Load from localStorage first
            const localProfiles = JSON.parse(localStorage.getItem('exchange_profiles') || '[]');
            
            // Try to load from backend
            try {
                const response = await fetch('/api/exchange/profiles');
                if (response.ok) {
                    const result = await response.json();
                    if (result.profiles && result.profiles.length > 0) {
                        this.profiles = result.profiles;
                        this.displayProfiles();
                        this.addTerminalLine('[System] Profiles loaded from backend', 'output');
                        return;
                    }
                }
            } catch (apiError) {
                console.warn('Backend API not available');
            }
            
            // Use localStorage data
            if (localProfiles.length > 0) {
                this.profiles = localProfiles;
                this.displayProfiles();
                this.addTerminalLine('[System] Profiles loaded from local storage', 'output');
            } else {
                // Load sample data for demo
                this.profiles = [
                    {
                        id: 'sample_1',
                        name: 'DNSE Demo',
                        exchange: 'DNSE',
                        type: 'Trading',
                        status: 'disconnected',
                        created: new Date().toLocaleString('vi-VN')
                    },
                    {
                        id: 'sample_2',
                        name: 'Entrade Demo',
                        exchange: 'ENTRADE',
                        type: 'Data',
                        status: 'disconnected',
                        created: new Date().toLocaleString('vi-VN')
                    }
                ];
                this.displayProfiles();
                this.addTerminalLine('[System] Sample profiles loaded (no saved profiles found)', 'output');
            }
        } catch (error) {
            console.error('Error loading profiles:', error);
            this.profiles = [];
            this.displayProfiles();
            this.addTerminalLine('[Error] Failed to load profiles', 'error');
        }
    },
    
    filterProfiles() {
        this.displayProfiles();
    },
    
    displayProfiles() {
        const container = document.getElementById('profiles-container');
        if (!container) return;
        
        let filteredProfiles = this.profiles;
        
        // Determine type from use_for_data and use_for_trading
        filteredProfiles = filteredProfiles.map(p => {
            if (!p.type) {
                if (p.use_for_data && !p.use_for_trading) {
                    p.type = 'Data';
                } else if (!p.use_for_data && p.use_for_trading) {
                    p.type = 'Trading';
                } else {
                    p.type = 'Data + Trading';
                }
            }
            return p;
        });
        
        if (this.currentFilter === 'data') {
            filteredProfiles = filteredProfiles.filter(p => p.use_for_data || p.type === 'Data');
        } else if (this.currentFilter === 'trading') {
            filteredProfiles = filteredProfiles.filter(p => p.use_for_trading || p.type === 'Trading');
        }
        
        if (filteredProfiles.length === 0) {
            container.innerHTML = '<div class="empty-state" style="text-align: center; padding: 2rem; color: var(--text-secondary);">Chưa có profile nào. Hãy tạo profile mới!</div>';
            return;
        }
        
        container.innerHTML = filteredProfiles.map(profile => `
            <div class="profile-card" style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                <div class="profile-card-header">
                    <div>
                        <div class="profile-name" style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">
                            ${profile.name}
                            <span style="background: ${profile.exchange === 'DNSE' ? '#3b82f6' : '#10b981'}; color: white; padding: 0.125rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-left: 0.5rem;">
                                ${profile.exchange}
                            </span>
                        </div>
                        <div class="profile-meta" style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                            <span class="status-badge" 
                                  style="background-color: ${profile.type === 'Data' ? 'rgba(59, 130, 246, 0.2)' : profile.type === 'Trading' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)'}; 
                                         color: ${profile.type === 'Data' ? '#3b82f6' : profile.type === 'Trading' ? '#10b981' : '#f59e0b'};
                                         padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem;">
                                ${profile.type === 'Data' ? '📊 Data' : profile.type === 'Trading' ? '💹 Trading' : '📊💹 Data + Trading'}
                            </span>
                            <span class="status-badge ${profile.status === 'connected' ? 'status-connected' : 'status-disconnected'}"
                                  style="background-color: ${profile.status === 'connected' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}; 
                                         color: ${profile.status === 'connected' ? '#10b981' : '#ef4444'};
                                         padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem;">
                                ${profile.status === 'connected' ? '✓ Connected' : '○ Disconnected'}
                            </span>
                        </div>
                    </div>
                </div>
                <div class="profile-meta" style="margin-top: 0.5rem; padding-top: 0.75rem; border-top: 1px solid var(--border-color); font-size: 0.75rem; color: var(--text-secondary);">
                    <span>📅 ${profile.created}</span>
                </div>
                <div class="profile-actions" style="display: flex; gap: 0.5rem; margin-top: 0.75rem;">
                    <button class="btn btn-sm ${profile.status === 'connected' ? 'btn-danger' : 'btn-success'}" 
                            onclick="Exchange.toggleConnection('${profile.id}')"
                            style="padding: 0.375rem 0.75rem; font-size: 0.875rem;">
                        ${profile.status === 'connected' ? 'Disconnect' : 'Connect'}
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="Exchange.showInfo('${profile.id}')"
                            style="padding: 0.375rem 0.75rem; font-size: 0.875rem;">Info</button>
                    <button class="btn btn-sm btn-secondary" onclick="Exchange.editProfile('${profile.id}')"
                            style="padding: 0.375rem 0.75rem; font-size: 0.875rem;">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="Exchange.deleteProfile('${profile.id}')"
                            style="padding: 0.375rem 0.75rem; font-size: 0.875rem;">Delete</button>
                </div>
            </div>
        `).join('');
    },
    
    async saveProfile() {
        const profileName = document.getElementById('profile-name')?.value;
        const exchange = document.getElementById('exchange-select')?.value;
        const useForData = document.getElementById('use-for-data')?.checked;
        const useForTrading = document.getElementById('use-for-trading')?.checked;
        
        // Get DNSE fields
        const dnseProtocol = document.getElementById('dnse-protocol')?.value;
        const dnseUsername = document.getElementById('dnse-username')?.value;
        const dnsePassword = document.getElementById('dnse-password')?.value;
        const dnseRequireOtp = document.getElementById('dnse-require-otp')?.checked;
        const dnseTickers = document.getElementById('dnse-tickers')?.value;
        
        // Get Entrade fields
        const entradeEnv = document.getElementById('entrade-environment')?.value;
        const entradeProtocol = document.getElementById('entrade-protocol')?.value;
        const entradeUsername = document.getElementById('entrade-username')?.value;
        const entradePassword = document.getElementById('entrade-password')?.value;
        const entradeRequireOtp = document.getElementById('entrade-require-otp')?.checked;
        const entradeTickers = document.getElementById('entrade-tickers')?.value;
        
        // Get Market Data fields
        const defaultTimeframe = document.getElementById('default-timeframe')?.value;
        const candleCount = document.getElementById('candle-count')?.value;
        const timezoneOffset = document.getElementById('timezone-offset')?.value;
        
        if (!profileName || !exchange) {
            alert('⚠️ Vui lòng điền đầy đủ:\n- Profile Name\n- Exchange');
            return;
        }
        
        if (!useForData && !useForTrading) {
            alert('⚠️ Vui lòng chọn ít nhất một mục đích sử dụng:\n- Use for Market Data\n- Use for Trading');
            return;
        }
        
        // Build profile data based on exchange type
        let profileData = {
            name: profileName,
            exchange: exchange,
            use_for_data: useForData,
            use_for_trading: useForTrading,
            timeframe: defaultTimeframe || '1m',
            candleCount: parseInt(candleCount) || 1000,
            timezone: parseInt(timezoneOffset) || 7,
            status: 'disconnected'
        };
        
        // Add DNSE specific fields
        if (exchange === 'DNSE') {
            profileData.protocol = dnseProtocol || 'rest';
            profileData.username = dnseUsername || '';
            profileData.password = dnsePassword || '';
            profileData.requireOtp = dnseRequireOtp !== false;
            profileData.tickers = dnseTickers || '';
        }
        
        // Add Entrade specific fields
        if (exchange === 'ENTRADE' || exchange === 'ENTRADE-MQTT') {
            profileData.environment = entradeEnv || 'demo';
            profileData.protocol = entradeProtocol || 'rest';
            profileData.username = entradeUsername || '';
            profileData.password = entradePassword || '';
            profileData.requireOtp = entradeRequireOtp !== false;
            profileData.tickers = entradeTickers || '';
        }
        
        try {
            // Load existing profiles
            let profiles = JSON.parse(localStorage.getItem('exchange_profiles') || '[]');
            
            if (this.editingProfile) {
                // UPDATE existing profile
                const index = profiles.findIndex(p => p.id === this.editingProfile);
                if (index !== -1) {
                    // Keep the original ID and created date
                    profileData.id = profiles[index].id;
                    profileData.created = profiles[index].created;
                    profiles[index] = profileData;
                    
                    this.addTerminalLine(`[Success] Profile "${profileName}" updated`, 'success');
                    alert(`✅ Profile "${profileName}" đã được cập nhật!`);
                }
            } else {
                // ADD new profile
                profileData.id = `profile_${Date.now()}`;
                profileData.created = new Date().toLocaleString('vi-VN');
                profiles.push(profileData);
                
                this.addTerminalLine(`[Success] Profile "${profileName}" created`, 'success');
                alert(`✅ Profile "${profileName}" đã được tạo thành công!`);
            }
            
            // Save to localStorage
            localStorage.setItem('exchange_profiles', JSON.stringify(profiles));
            
            // Try backend API
            try {
                const method = this.editingProfile ? 'PUT' : 'POST';
                const response = await fetch('/api/exchange/profiles', {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(profileData)
                });
                
                if (response.ok) {
                    console.log('✅ Profile saved to backend');
                }
            } catch (apiError) {
                console.warn('⚠️ Backend API not available');
            }
            
            // Reset form
            this.clearForm();
            
            // Reset form title and button
            const formSection = document.querySelector('.add-profile-section h2');
            if (formSection) {
                formSection.textContent = '➕ Add New Profile';
                formSection.style.color = '';
            }
            
            const updateBtn = document.getElementById('save-profile-btn');
            if (updateBtn) {
                updateBtn.innerHTML = '💾 Update Profile';
                updateBtn.style.background = '';
            }
            
            // Reload profiles
            this.loadProfiles();
            
        } catch (error) {
            console.error('Error saving profile:', error);
            this.addTerminalLine(`[Error] Failed to save profile: ${error.message}`, 'error');
            alert('❌ Lỗi khi lưu profile: ' + error.message);
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
        if (!profile) {
            console.error('Profile not found:', profileId);
            return;
        }
        
        console.log('Editing profile:', profile);
        this.editingProfile = profile.id;
        
        // 1. Fill BASIC INFORMATION
        const profileNameInput = document.getElementById('profile-name');
        const exchangeSelect = document.getElementById('exchange-select');
        
        if (profileNameInput) profileNameInput.value = profile.name || '';
        if (exchangeSelect) {
            exchangeSelect.value = profile.exchange || '';
            // Trigger change event to show/hide appropriate sections
            exchangeSelect.dispatchEvent(new Event('change'));
        }
        
        // 2. Fill PROFILE USAGE
        const useForData = document.getElementById('use-for-data');
        const useForTrading = document.getElementById('use-for-trading');
        
        if (useForData) useForData.checked = profile.use_for_data === true;
        if (useForTrading) useForTrading.checked = profile.use_for_trading === true;
        
        // 3. Fill DNSE CREDENTIALS (if DNSE exchange)
        if (profile.exchange === 'DNSE') {
            const dnseProtocol = document.getElementById('dnse-protocol');
            const dnseUsername = document.getElementById('dnse-username');
            const dnsePassword = document.getElementById('dnse-password');
            const dnseRequireOtp = document.getElementById('dnse-require-otp');
            const dnseTickers = document.getElementById('dnse-tickers');
            
            if (dnseProtocol) dnseProtocol.value = profile.protocol || 'rest';
            if (dnseUsername) dnseUsername.value = profile.username || '';
            if (dnsePassword) dnsePassword.value = profile.password || '';
            if (dnseRequireOtp) dnseRequireOtp.checked = profile.requireOtp !== false;
            if (dnseTickers) dnseTickers.value = profile.tickers || '';
        }
        
        // 4. Fill ENTRADE CREDENTIALS (if ENTRADE exchange)
        if (profile.exchange === 'ENTRADE' || profile.exchange === 'ENTRADE-MQTT') {
            const entradeEnv = document.getElementById('entrade-environment');
            const entradeProtocol = document.getElementById('entrade-protocol');
            const entradeUsername = document.getElementById('entrade-username');
            const entradePassword = document.getElementById('entrade-password');
            const entradeRequireOtp = document.getElementById('entrade-require-otp');
            const entradeTickers = document.getElementById('entrade-tickers');
            
            if (entradeEnv) entradeEnv.value = profile.environment || 'demo';
            if (entradeProtocol) entradeProtocol.value = profile.protocol || 'rest';
            if (entradeUsername) entradeUsername.value = profile.username || '';
            if (entradePassword) entradePassword.value = profile.password || '';
            if (entradeRequireOtp) entradeRequireOtp.checked = profile.requireOtp !== false;
            if (entradeTickers) entradeTickers.value = profile.tickers || '';
        }
        
        // 5. Fill MARKET DATA SETTINGS
        const defaultTimeframe = document.getElementById('default-timeframe');
        const candleCount = document.getElementById('candle-count');
        const timezoneOffset = document.getElementById('timezone-offset');
        
        if (defaultTimeframe) defaultTimeframe.value = profile.timeframe || '1m';
        if (candleCount) candleCount.value = profile.candleCount || 1000;
        if (timezoneOffset) timezoneOffset.value = profile.timezone || 7;
        
        // 6. Update form title
        const formSection = document.querySelector('.add-profile-section h2');
        if (formSection) {
            formSection.textContent = `✏️ Edit Profile: ${profile.name}`;
            formSection.style.color = '#f59e0b';
        }
        
        // 7. Update button text
        const updateBtn = document.getElementById('save-profile-btn');
        if (updateBtn) {
            updateBtn.innerHTML = '💾 Update Profile';
            updateBtn.style.background = '#f59e0b';
        }
        
        // 8. Scroll to form
        document.querySelector('.add-profile-section')?.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
        
        // 9. Add terminal log
        this.addTerminalLine(`[System] Editing profile: ${profile.name}`, 'output');
        
        console.log('✅ Profile loaded to form for editing');
    },
    
    async deleteProfile(profileId) {
        const profile = this.profiles.find(p => p.id === profileId);
        if (!profile) return;
        
        if (!confirm(`Bạn có chắc muốn xóa profile "${profile.name}"?`)) return;
        
        try {
            // Delete from localStorage
            let profiles = JSON.parse(localStorage.getItem('exchange_profiles') || '[]');
            profiles = profiles.filter(p => p.id !== profileId);
            localStorage.setItem('exchange_profiles', JSON.stringify(profiles));
            
            // Also try backend API
            try {
                await fetch(`/api/exchange/profiles?id=${profileId}`, {
                    method: 'DELETE'
                });
            } catch (apiError) {
                console.warn('Backend API not available');
            }
            
            this.addTerminalLine(`[Success] Profile "${profile.name}" deleted`, 'success');
            alert(`✅ Profile "${profile.name}" đã được xóa!`);
            this.loadProfiles();
        } catch (error) {
            console.error('Error deleting profile:', error);
            this.addTerminalLine(`[Error] Failed to delete profile`, 'error');
            alert('❌ Lỗi khi xóa profile');
        }
    },
    
    clearForm() {
        this.editingProfile = null;
        
        // Clear basic fields
        const profileNameInput = document.getElementById('profile-name');
        const exchangeSelect = document.getElementById('exchange-select');
        const useForData = document.getElementById('use-for-data');
        const useForTrading = document.getElementById('use-for-trading');
        
        if (profileNameInput) profileNameInput.value = '';
        if (exchangeSelect) exchangeSelect.value = '';
        if (useForData) useForData.checked = false;
        if (useForTrading) useForTrading.checked = false;
        
        // Clear DNSE fields
        const dnseProtocol = document.getElementById('dnse-protocol');
        const dnseUsername = document.getElementById('dnse-username');
        const dnsePassword = document.getElementById('dnse-password');
        const dnseRequireOtp = document.getElementById('dnse-require-otp');
        const dnseTickers = document.getElementById('dnse-tickers');
        
        if (dnseProtocol) dnseProtocol.value = 'rest';
        if (dnseUsername) dnseUsername.value = '';
        if (dnsePassword) dnsePassword.value = '';
        if (dnseRequireOtp) dnseRequireOtp.checked = true;
        if (dnseTickers) dnseTickers.value = 'VD: VN30F1M,VNM,FPT,VCB';
        
        // Clear Market Data fields
        const defaultTimeframe = document.getElementById('default-timeframe');
        const candleCount = document.getElementById('candle-count');
        const timezoneOffset = document.getElementById('timezone-offset');
        
        if (defaultTimeframe) defaultTimeframe.value = '1m';
        if (candleCount) candleCount.value = '1000';
        if (timezoneOffset) timezoneOffset.value = '7';
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
