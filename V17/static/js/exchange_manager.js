// Exchange Manager Frontend Logic

let profiles = [];
let realtimeInterval = null;
let currentLoadedProfile = null;
// Terminal logging functions
function logToTerminal(message, type = 'info') {
    const terminal = document.getElementById('terminalContent');
    if (!terminal) return;
    
    const timestamp = new Date().toLocaleTimeString('vi-VN', { hour12: false });
    const line = document.createElement('div');
    line.className = `terminal-line ${type}`;
    
    const icon = {
        'info': '🔵',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️'
    }[type] || 'ℹ️';
    
    line.innerHTML = `
        <span class="terminal-timestamp">[${timestamp}]</span>
        <span>${icon} ${message}</span>
    `;
    
    terminal.appendChild(line);
    
    // Auto-scroll to bottom
    terminal.scrollTop = terminal.scrollHeight;
}

function clearTerminal() {
    const terminal = document.getElementById('terminalContent');
    if (!terminal) return;
    
    terminal.innerHTML = `
        <div class="terminal-line info">
            <span class="terminal-timestamp">[System]</span>
            <span>Terminal cleared.</span>
        </div>
    `;
}

// MT5 Broker-Server Mapping
const mt5BrokerServers = {
    exness: [
        // Real Servers
        'ExnessMU-MT5Real',
        'ExnessMU-MT5Real2',
        'ExnessMU-MT5Real3',
        'ExnessMU-MT5Real4',
        'ExnessMU-MT5Real5',
        'ExnessMU-MT5Real6',
        'ExnessMU-MT5Real7',
        'ExnessMU-MT5Real8',
        'ExnessMU-MT5Real9',
        'ExnessMU-MT5Real10',
        'ExnessMU-MT5Real11',
        'ExnessMU-MT5Real12',
        'ExnessMU-MT5Real13',
        'ExnessMU-MT5Real14',
        'ExnessMU-MT5Real15',
        'ExnessMU-MT5Real16',
        'ExnessMU-MT5Real17',
        'ExnessMU-MT5Real18',
        'ExnessMU-MT5Real19',
        'ExnessMU-MT5Real20',
        // Demo/Trial Servers
        'Exness-MT5Trial',
        'Exness-MT5Trial2',
        'Exness-MT5Trial3',
        'Exness-MT5Trial4',
        'Exness-MT5Trial5',
        'Exness-MT5Trial6',
        'Exness-MT5Trial7',
        'Exness-MT5Trial8',
        'Exness-MT5Trial9',
        'Exness-MT5Trial10',
        'Exness-MT5Trial11',
        'Exness-MT5Trial12',
        'Exness-MT5Trial13',
        'Exness-MT5Trial14',
        'Exness-MT5Trial15',
        'Exness-MT5Trial16',
        'Exness-MT5Trial17',
        'Exness-MT5Trial18',
        'Exness-MT5Trial19',
        'Exness-MT5Trial20'
    ],
    icmarkets: [
        'ICMarkets-Demo',
        'ICMarkets-Demo02',
        'ICMarkets-Demo03',
        'ICMarkets-Live',
        'ICMarkets-Live02',
        'ICMarkets-Live03'
    ],
    xm: [
        'XMGlobal-Demo',
        'XMGlobal-Demo 2',
        'XMGlobal-Demo 3',
        'XMGlobal-Real',
        'XMGlobal-Real 2',
        'XMGlobal-Real 3'
    ],
    alpari: [
        'Alpari-MT5-Demo',
        'Alpari-MT5-Real'
    ],
    fxtm: [
        'ForexTimeFXTM-Demo',
        'ForexTimeFXTM-Demo02',
        'ForexTimeFXTM-Real',
        'ForexTimeFXTM-Real02'
    ],
    pepperstone: [
        'Pepperstone-Demo',
        'Pepperstone-Live',
        'Pepperstone-Live02'
    ],
    tickmill: [
        'Tickmill-Demo',
        'Tickmill-Live'
    ],
    roboforex: [
        'RoboForex-Demo',
        'RoboForex-Demo-2',
        'RoboForex-Real',
        'RoboForex-Real-2'
    ]
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadProfiles();
    
    document.getElementById('exchangeSelect').addEventListener('change', function() {
        showCredentialsForm(this.value);
    });
    
    // MT5 Broker dropdown handler
    const mt5BrokerSelect = document.getElementById('mt5Broker');
    if (mt5BrokerSelect) {
        mt5BrokerSelect.addEventListener('change', function() {
            loadMT5Servers(this.value);
        });
    }
    
    // MT5 Server dropdown handler
    const mt5ServerSelect = document.getElementById('mt5Server');
    if (mt5ServerSelect) {
        mt5ServerSelect.addEventListener('change', function() {
            const customGroup = document.getElementById('mt5CustomServerGroup');
            if (this.value === 'custom') {
                customGroup.style.display = 'block';
            } else {
                customGroup.style.display = 'none';
            }
        });
    }
    
    document.getElementById('profileForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveProfile();
    });
});

// Load MT5 servers based on selected broker
function loadMT5Servers(broker) {
    const serverSelect = document.getElementById('mt5Server');
    const customGroup = document.getElementById('mt5CustomServerGroup');
    
    // Clear current options
    serverSelect.innerHTML = '<option value="">-- Select Server --</option>';
    
    if (!broker) {
        serverSelect.disabled = true;
        customGroup.style.display = 'none';
        return;
    }
    
    serverSelect.disabled = false;
    
    if (broker === 'other') {
        // Show custom input for other brokers
        customGroup.style.display = 'block';
        serverSelect.innerHTML = '<option value="custom">Enter Custom Server Below</option>';
        serverSelect.value = 'custom';
    } else {
        // Load servers for selected broker
        customGroup.style.display = 'none';
        const servers = mt5BrokerServers[broker] || [];
        
        servers.forEach(server => {
            const option = document.createElement('option');
            option.value = server;
            option.textContent = server;
            serverSelect.appendChild(option);
        });
        
        // Add custom option at the end
        const customOption = document.createElement('option');
        customOption.value = 'custom';
        customOption.textContent = '-- Custom Server --';
        serverSelect.appendChild(customOption);
    }
}

// Load profiles from server
async function loadProfiles() {
    try {
        const response = await fetch('/api/exchange/profiles');
        const data = await response.json();
        
        if (data.success) {
            profiles = data.profiles;
            renderProfiles();
        }
    } catch (error) {
        console.error('Load profiles error:', error);
    }
}

// Render profiles list
function renderProfiles(filteredProfiles = null) {
    const container = document.getElementById('profilesList');
    
    // Use filtered profiles if provided, otherwise use all profiles
    const profilesToRender = filteredProfiles !== null ? filteredProfiles : profiles;
    
    if (profilesToRender.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M10,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V8C22,6.89 21.1,6 20,6H12L10,4Z" />
                </svg>
                <p>No profiles ${filteredProfiles !== null ? 'match this filter' : 'yet'}</p>
            </div>
        `;
        return;
    }
    
    // Sort profiles alphabetically by name (A-Z, case-insensitive)
    const sortedProfiles = [...profilesToRender].sort((a, b) => 
        a.name.toLowerCase().localeCompare(b.name.toLowerCase())
    );
    
    let html = '';
    sortedProfiles.forEach(profile => {
        const statusClass = profile.connected ? 'status-connected' : 'status-disconnected';
        const statusText = profile.connected ? 'Connected' : 'Disconnected';
        const connectBtnText = profile.connected ? 'Disconnect' : 'Connect';
        const connectBtnClass = profile.connected ? 'btn-danger' : 'btn-success';
        
        // Show usage badges
        const usageBadges = [];
        if (profile.use_for_data !== false) {
            usageBadges.push('<span style="font-size: 10px; padding: 2px 6px; background: rgba(41, 98, 255, 0.2); color: #2962ff; border-radius: 3px; margin-right: 4px;">📊 Data</span>');
        }
        if (profile.use_for_trading !== false) {
            usageBadges.push('<span style="font-size: 10px; padding: 2px 6px; background: rgba(76, 175, 80, 0.2); color: #4caf50; border-radius: 3px;">📈 Trading</span>');
        }
        
        html += `
            <div class="profile-item" onclick="editProfile('${profile.name}')" style="cursor: pointer;">
                <div class="profile-header">
                    <div class="profile-name">${profile.name}</div>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="profile-meta">
                    <span class="exchange-badge">${profile.exchange.toUpperCase()}</span>
                    <span>${formatDate(profile.created_at)}</span>
                </div>
                ${usageBadges.length > 0 ? `<div style="margin: 8px 0;">${usageBadges.join('')}</div>` : ''}
                <div class="profile-actions" onclick="event.stopPropagation();">
                    <button class="btn ${connectBtnClass} btn-sm" onclick="toggleConnection('${profile.name}')">
                        ${connectBtnText}
                    </button>
                    <button class="btn btn-info btn-sm" onclick="showAccountInfo('${profile.name}')" title="Xem thông tin tài khoản">
                        Info
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="editProfile('${profile.name}'); event.stopPropagation();">
                        Edit
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteProfile('${profile.name}')">
                        Delete
                    </button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Filter profiles by usage type
function filterProfiles(mode) {
    console.log(`🔍 Filtering profiles: ${mode}`);
    
    // Update button states
    document.querySelectorAll('.profile-filter-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.style.background = '';
        btn.style.color = '';
        btn.style.border = '';
    });
    
    const activeBtn = document.getElementById(`filter${mode.charAt(0).toUpperCase() + mode.slice(1)}`);
    if (activeBtn) {
        activeBtn.classList.add('active');
        if (mode === 'all') {
            activeBtn.style.background = '#2962ff';
            activeBtn.style.color = 'white';
            activeBtn.style.border = 'none';
        } else if (mode === 'data') {
            activeBtn.style.background = '#2962ff';
            activeBtn.style.color = 'white';
            activeBtn.style.border = 'none';
        } else if (mode === 'trading') {
            activeBtn.style.background = '#4caf50';
            activeBtn.style.color = 'white';
            activeBtn.style.border = 'none';
        }
    }
    
    // Filter profiles
    let filtered;
    if (mode === 'all') {
        filtered = profiles;
    } else if (mode === 'data') {
        filtered = profiles.filter(p => p.use_for_data !== false);
    } else if (mode === 'trading') {
        filtered = profiles.filter(p => p.use_for_trading !== false);
    } else {
        filtered = profiles;
    }
    
    console.log(`   Found ${filtered.length} profiles for filter: ${mode}`);
    renderProfiles(filtered);
}

// Show credentials form based on exchange
function showCredentialsForm(exchange) {
    // Hide all forms
    document.querySelectorAll('.credentials-form').forEach(form => {
        form.classList.remove('active');
    });
    
    // Show selected form
    if (exchange) {
        const formId = exchange + 'Credentials';
        const form = document.getElementById(formId);
        if (form) {
            form.classList.add('active');
        }
    }
}

// Get credentials from form
function getCredentials(exchange) {
    const credentials = {};
    
    switch(exchange) {
        case 'binance':
            credentials.api_key = document.getElementById('binanceApiKey').value;
            credentials.api_secret = document.getElementById('binanceApiSecret').value;
            credentials.tickers = document.getElementById('binanceTickers').value;
            credentials.timeframe = document.getElementById('binanceTimeframe').value || 'M1';
            credentials.display_candles = document.getElementById('binanceDisplayCandles').value || '1000';
            credentials.timezone = document.getElementById('binanceTimezone').value || '0';
            break;
        case 'mt5':
            credentials.login = document.getElementById('mt5Login').value;
            credentials.password = document.getElementById('mt5Password').value;
            credentials.broker = document.getElementById('mt5Broker').value;
            
            // Get server from dropdown or custom input
            const serverSelect = document.getElementById('mt5Server').value;
            if (serverSelect === 'custom') {
                credentials.server = document.getElementById('mt5CustomServer').value;
            } else {
                credentials.server = serverSelect;
            }
            credentials.tickers = document.getElementById('mt5Tickers').value;
            credentials.timeframe = document.getElementById('mt5Timeframe').value || 'M1';
            credentials.display_candles = document.getElementById('mt5DisplayCandles').value || '1000';
            credentials.timezone = document.getElementById('mt5Timezone').value || '0';
            break;
        case 'dnse':
            credentials.protocol = document.getElementById('dnseProtocol').value;
            // Only get username/password if NOT public_rest protocol
            if (credentials.protocol !== 'public_rest') {
                credentials.username = document.getElementById('dnseUsername').value;
                credentials.password = document.getElementById('dnsePassword').value;
                credentials.require_otp = document.getElementById('dnseRequireOTP')?.checked || false;
            } else {
                // Public API không cần credentials
                credentials.username = '';
                credentials.password = '';
                credentials.require_otp = false;
            }
            credentials.tickers = document.getElementById('dnseTickers').value;
            credentials.timeframe = document.getElementById('dnseTimeframe').value || 'M1';
            credentials.display_candles = document.getElementById('dnseDisplayCandles').value || '1000';
            credentials.timezone = document.getElementById('dnseTimezone').value || '7';
            break;
        case 'entrade':
            credentials.protocol = document.getElementById('entradeProtocol').value;
            credentials.username = document.getElementById('entradeUsername').value;
            credentials.password = document.getElementById('entradePassword').value;
            credentials.tickers = document.getElementById('entradeTickers').value;
            credentials.is_demo = document.getElementById('entradeIsDemo')?.checked || false;
            credentials.timeframe = document.getElementById('entradeTimeframe').value || 'M1';
            credentials.display_candles = document.getElementById('entradeDisplayCandles').value || '1000';
            credentials.timezone = document.getElementById('entradeTimezone').value || '7';
            break;
    }
    
    return credentials;
}

// Test connection
async function testConnection() {
    const exchange = document.getElementById('exchangeSelect').value;
    
    if (!exchange) {
        showAlert('Vui lòng chọn sàn', 'error');
        logToTerminal('Test failed: No exchange selected', 'error');
        return;
    }
    
    const credentials = getCredentials(exchange);
    
    // Special handling for DNSE - show OTP modal if required
    if (exchange === 'dnse') {
        // Public REST API không cần username/password
        if (credentials.protocol === 'public_rest') {
            // Skip username/password validation for public API
        } else if (!credentials.username || !credentials.password) {
            showAlert('Vui lòng điền Username và Password DNSE', 'error');
            logToTerminal('Test failed: Missing DNSE credentials', 'error');
            return;
        }
        
        // Check if OTP is required
        if (credentials.require_otp) {
            // Show OTP modal
            showDNSEOTPModal();
            return;
        }
        // If OTP not required, proceed with normal connection
    }
    
    // Special validation for MT5
    if (exchange === 'mt5') {
        const broker = document.getElementById('mt5Broker').value;
        if (!broker) {
            showAlert('Vui lòng chọn Broker', 'error');
            logToTerminal('Test failed: No broker selected', 'error');
            return;
        }
        if (!credentials.login || !credentials.password || !credentials.server) {
            showAlert('Vui lòng điền đầy đủ thông tin MT5', 'error');
            logToTerminal('Test failed: Missing MT5 credentials', 'error');
            return;
        }
    } else {
        // Validate other exchanges
        const hasEmptyFields = Object.values(credentials).some(val => !val);
        if (hasEmptyFields) {
            showAlert('Vui lòng điền đầy đủ thông tin', 'error');
            logToTerminal('Test failed: Missing credentials', 'error');
            return;
        }
    }
    
    // Show loading
    const spinner = document.getElementById('testSpinner');
    const testBtn = document.querySelector('button[onclick="testConnection()"]');
    
    if (spinner) spinner.classList.add('show');
    if (testBtn) {
        testBtn.disabled = true;
        testBtn.style.opacity = '0.6';
    }
    
    logToTerminal(`Testing connection to ${exchange.toUpperCase()}...`, 'info');
    if (exchange === 'mt5') {
        logToTerminal(`Server: ${credentials.server}, Login: ${credentials.login}`, 'info');
    }
    
    console.log('🔄 Testing connection...', { exchange, credentials: {...credentials, password: '***'} });
    showAlert('🔄 Đang kết nối... Vui lòng đợi...', 'info');
    
    try {
        const response = await fetch('/api/exchange/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                exchange: exchange,
                credentials: credentials
            })
        });
        
        console.log('📡 Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('📦 Response data:', data);
        
        if (data.success) {
            console.log('✅ Connection successful!');
            logToTerminal(`Connection successful to ${exchange.toUpperCase()}!`, 'success');
            
            if (data.account_info) {
                const info = data.account_info;
                if (exchange === 'mt5') {
                    logToTerminal(`Balance: $${info.balance}, Equity: $${info.equity}`, 'success');
                } else if (exchange === 'binance') {
                    logToTerminal(`Balance: $${info.balance}, Available: $${info.available}`, 'success');
                }
            }
            
            showAlert('✓ Kết nối thành công!', 'success');
            
            // Display account info
            if (data.account_info) {
                displayAccountInfo(data.account_info, exchange);
            }
        } else {
            console.error('❌ Connection failed:', data.error);
            logToTerminal(`Connection failed: ${data.error}`, 'error');
            showAlert('✗ Kết nối thất bại: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('❌ Test connection error:', error);
        logToTerminal(`Connection error: ${error.message}`, 'error');
        showAlert('✗ Lỗi kết nối: ' + error.message, 'error');
    } finally {
        if (spinner) spinner.classList.remove('show');
        if (testBtn) {
            testBtn.disabled = false;
            testBtn.style.opacity = '1';
        }
    }
}

// Display account info
function displayAccountInfo(info, exchange) {
    const container = document.getElementById('accountInfo');
    const content = document.getElementById('accountInfoContent');
    
    let html = '';
    
    if (exchange === 'binance') {
        html = `
            <div class="info-item">
                <div class="info-label">Balance</div>
                <div class="info-value">$${formatNumber(info.balance)}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Equity</div>
                <div class="info-value">$${formatNumber(info.equity)}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Available</div>
                <div class="info-value">$${formatNumber(info.available)}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Positions</div>
                <div class="info-value">${info.positions_count || 0}</div>
            </div>
        `;
    } else if (exchange === 'mt5') {
        html = `
            <div class="info-item">
                <div class="info-label">Balance</div>
                <div class="info-value">$${formatNumber(info.balance)}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Equity</div>
                <div class="info-value">$${formatNumber(info.equity)}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Free Margin</div>
                <div class="info-value">$${formatNumber(info.free_margin)}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Profit</div>
                <div class="info-value" style="color: ${info.profit >= 0 ? '#48bb78' : '#f56565'}">
                    $${formatNumber(info.profit)}
                </div>
            </div>
        `;
    } else if (exchange === 'dnse') {
        html = `
            <div class="info-item">
                <div class="info-label">Cash</div>
                <div class="info-value">${formatNumber(info.cash)} VNĐ</div>
            </div>
            <div class="info-item">
                <div class="info-label">Stock Value</div>
                <div class="info-value">${formatNumber(info.stock_value)} VNĐ</div>
            </div>
            <div class="info-item">
                <div class="info-label">Total Asset</div>
                <div class="info-value">${formatNumber(info.total_asset)} VNĐ</div>
            </div>
            <div class="info-item">
                <div class="info-label">Buying Power</div>
                <div class="info-value">${formatNumber(info.buying_power)} VNĐ</div>
            </div>
        `;
    } else if (exchange === 'entrade') {
        // Entrade Derivatives Account
        const accountType = info.account_type || 'Real';
        const accountTypeBadge = accountType === 'Demo' 
            ? '<span style="background: #ff9800; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px;">DEMO</span>'
            : '<span style="background: #4caf50; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px;">REAL</span>';
        
        html = `
            <div style="background: #131722; padding: 12px; border-radius: 6px; margin-bottom: 15px;">
                <div style="font-size: 12px; color: #787b86; margin-bottom: 8px;">
                    <strong>Tài khoản:</strong> ${info.username || 'N/A'} ${accountTypeBadge}
                </div>
                <div style="font-size: 11px; color: #787b86;">
                    <strong>Account ID:</strong> ${info.account_id || 'N/A'}
                </div>
            </div>
            
            <div class="info-section-title">💰 Thông tin tiền</div>
            <div class="info-item">
                <div class="info-label">Số dư tiền</div>
                <div class="info-value">${formatNumber(info.cash_balance || 0)} VNĐ</div>
            </div>
            <div class="info-item">
                <div class="info-label">Sức mua</div>
                <div class="info-value">${formatNumber(info.purchasing_power || 0)} VNĐ</div>
            </div>
            <div class="info-item">
                <div class="info-label">Dư nợ</div>
                <div class="info-value" style="color: ${(info.debt || 0) > 0 ? '#f56565' : '#48bb78'}">
                    ${formatNumber(info.debt || 0)} VNĐ
                </div>
            </div>
            <div class="info-item">
                <div class="info-label">Tổng tài sản</div>
                <div class="info-value" style="font-weight: bold; color: #2962ff;">
                    ${formatNumber(info.total_asset || 0)} VNĐ
                </div>
            </div>
            
            <div class="info-section-title" style="margin-top: 15px;">📊 Vị thế</div>
            <div class="info-item">
                <div class="info-label">Số vị thế đang giữ</div>
                <div class="info-value">${info.positions_count || 0}</div>
            </div>
            
            ${info.positions && info.positions.length > 0 ? `
                <div style="margin-top: 10px;">
                    <div style="font-size: 11px; color: #787b86; margin-bottom: 8px;">Top vị thế:</div>
                    ${info.positions.map(pos => `
                        <div style="background: #0d1117; padding: 8px; border-radius: 4px; margin-bottom: 6px; font-size: 11px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                <span style="color: #d1d4dc; font-weight: 600;">${pos.symbol}</span>
                                <span style="color: ${pos.side === 'LONG' ? '#48bb78' : '#f56565'}; font-weight: 600;">
                                    ${pos.side}
                                </span>
                            </div>
                            <div style="display: flex; justify-content: space-between; color: #787b86;">
                                <span>SL: ${pos.quantity}</span>
                                <span>Giá: ${formatNumber(pos.entry_price)}</span>
                            </div>
                            <div style="color: ${(pos.unrealized_pnl || 0) >= 0 ? '#48bb78' : '#f56565'}; font-weight: 600; margin-top: 4px;">
                                P/L: ${formatNumber(pos.unrealized_pnl || 0)} VNĐ
                            </div>
                        </div>
                    `).join('')}
                    ${info.positions_count > 5 ? `
                        <div style="text-align: center; color: #787b86; font-size: 11px; margin-top: 8px;">
                            ... và ${info.positions_count - 5} vị thế khác
                        </div>
                    ` : ''}
                </div>
            ` : ''}
        `;
    }
    
    content.innerHTML = html;
    container.style.display = 'block';
}

// Save profile
async function saveProfile() {
    const profileName = document.getElementById('profileName').value.trim();
    const exchange = document.getElementById('exchangeSelect').value;
    const originalName = document.getElementById('profileName').dataset.originalName;
    
    if (!profileName || !exchange) {
        showAlert('Vui lòng điền đầy đủ thông tin', 'error');
        logToTerminal('Save failed: Missing profile name or exchange', 'error');
        return;
    }
    
    const credentials = getCredentials(exchange);
    
    // Validate credentials (bỏ qua các boolean và optional fields)
    const requiredFields = Object.entries(credentials).filter(([key, val]) => {
        // Bỏ qua boolean fields và optional fields
        if (typeof val === 'boolean') return false;
        // Bỏ qua OTP nếu Entrade hoặc protocol=mqtt
        if (key === 'otp' && (exchange === 'entrade' || credentials.protocol === 'mqtt')) return false;
        if (key === 'tickers') return false; // Tickers là optional
        if (key === 'protocol') return false; // Protocol field
        // Bỏ qua username/password nếu protocol=public_rest (Public API không cần credentials)
        if (credentials.protocol === 'public_rest' && (key === 'username' || key === 'password')) return false;
        return true;
    });
    
    const hasEmptyFields = requiredFields.some(([key, val]) => !val);
    if (hasEmptyFields) {
        showAlert('Vui lòng điền đầy đủ thông tin xác thực', 'error');
        logToTerminal('Save failed: Missing credentials', 'error');
        return;
    }
    
    // Check if this is a rename operation
    const isRename = originalName && originalName !== profileName;
    
    if (isRename) {
        logToTerminal(`Renaming profile: ${originalName} → ${profileName}`, 'info');
    } else {
        logToTerminal(`Saving profile: ${profileName} (${exchange.toUpperCase()})`, 'info');
    }
    
    try {
        // If renaming, delete old profile first
        if (isRename) {
            logToTerminal(`Deleting old profile: ${originalName}`, 'info');
            const deleteResponse = await fetch(`/api/exchange/profile/${encodeURIComponent(originalName)}`, {
                method: 'DELETE'
            });
            
            const deleteData = await deleteResponse.json();
            if (!deleteData.success) {
                throw new Error('Failed to delete old profile: ' + deleteData.error);
            }
            logToTerminal(`Old profile deleted`, 'success');
        }
        
        // Get profile usage flags from checkboxes
        const useForData = document.getElementById('useForData').checked;
        const useForTrading = document.getElementById('useForTrading').checked;
        
        // Add flags to credentials
        credentials.use_for_data = useForData;
        credentials.use_for_trading = useForTrading;
        
        // Save new/updated profile
        const response = await fetch('/api/exchange/profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                profile_name: profileName,
                exchange: exchange,
                credentials: credentials
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (isRename) {
                logToTerminal(`Profile renamed: ${originalName} → ${profileName}`, 'success');
                showAlert('✓ Đã đổi tên profile thành công!', 'success');
            } else {
                logToTerminal(`Profile saved: ${profileName}`, 'success');
                showAlert('✓ Đã lưu profile thành công!', 'success');
            }
            resetForm();
            await loadProfiles();
            
            // Update Connection modal dropdown
            console.log('🔄 Updating Connection modal dropdown...');
            if (typeof window.loadQuickProfileSelect === 'function') {
                await window.loadQuickProfileSelect();
                console.log('✅ Connection modal dropdown updated');
            } else {
                console.warn('⚠️ window.loadQuickProfileSelect is not a function');
            }
        } else {
            logToTerminal(`Save failed: ${data.error}`, 'error');
            showAlert('✗ Lưu profile thất bại: ' + data.error, 'error');
        }
    } catch (error) {
        logToTerminal(`Save error: ${error.message}`, 'error');
        showAlert('✗ Lỗi: ' + error.message, 'error');
    }
}

// Toggle connection
async function toggleConnection(profileName) {
    const profile = profiles.find(p => p.name === profileName);
    
    if (!profile) return;
    
    // Find the button and show loading
    const buttons = document.querySelectorAll('.profile-item button');
    let connectBtn = null;
    buttons.forEach(btn => {
        if (btn.textContent.includes('Connect') || btn.textContent.includes('Disconnect')) {
            const profileItem = btn.closest('.profile-item');
            const nameDiv = profileItem.querySelector('.profile-name');
            if (nameDiv && nameDiv.textContent === profileName) {
                connectBtn = btn;
            }
        }
    });
    
    if (connectBtn) {
        connectBtn.disabled = true;
        connectBtn.style.opacity = '0.6';
    }
    
    try {
        if (profile.connected) {
            // Disconnect
            console.log('🔌 Disconnecting:', profileName);
            logToTerminal(`Disconnecting profile: ${profileName}`, 'info');
            showAlert('🔄 Đang ngắt kết nối...', 'info');
            
            const response = await fetch(`/api/exchange/disconnect/${profileName}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            console.log('📦 Disconnect response:', data);
            
            if (data.success) {
                console.log('✅ Disconnected successfully');
                logToTerminal(`Disconnected: ${profileName}`, 'success');
                showAlert('✓ Đã ngắt kết nối', 'success');
                await loadProfiles();
                
                // Update Connection modal dropdown (remove ✅ mark)
                if (typeof window.loadQuickProfileSelect === 'function') {
                    window.loadQuickProfileSelect();
                }
            } else {
                console.error('❌ Disconnect failed:', data.error);
                logToTerminal(`Disconnect failed: ${data.error}`, 'error');
                showAlert('✗ Ngắt kết nối thất bại: ' + data.error, 'error');
            }
        } else {
            // Connect
            console.log('🔌 Connecting:', profileName);
            logToTerminal(`Connecting profile: ${profileName} (${profile.exchange.toUpperCase()})`, 'info');
            showAlert('🔄 Đang kết nối... Vui lòng đợi...', 'info');
            
            const response = await fetch(`/api/exchange/connect/${profileName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            console.log('📦 Connect response:', data);
            
            if (data.success) {
                console.log('✅ Connected successfully');
                logToTerminal(`Connected: ${profileName} - ${data.message || 'Success'}`, 'success');
                showAlert('✓ Đã kết nối thành công!', 'success');
                await loadProfiles();
                
                // Update Connection modal dropdown (add ✅ mark)
                if (typeof window.loadQuickProfileSelect === 'function') {
                    window.loadQuickProfileSelect();
                }
            } else if (data.needs_otp) {
                // DNSE cần OTP - hiện modal
                console.log('📧 DNSE needs OTP - showing modal');
                logToTerminal(`DNSE requires OTP - Opening OTP modal`, 'info');
                showDNSEProfileOTPModal(profileName, data.username);
            } else {
                console.error('❌ Connect failed:', data.error);
                logToTerminal(`Connect failed: ${data.error}`, 'error');
                showAlert('✗ Kết nối thất bại: ' + data.error, 'error');
            }
        }
    } catch (error) {
        console.error('❌ Toggle connection error:', error);
        logToTerminal(`Connection error: ${error.message}`, 'error');
        showAlert('✗ Lỗi: ' + error.message, 'error');
    } finally {
        if (connectBtn) {
            connectBtn.disabled = false;
            connectBtn.style.opacity = '1';
        }
    }
}

// View account info
async function viewAccountInfo(profileName) {
    try {
        const response = await fetch(`/api/exchange/account/${profileName}`);
        const data = await response.json();
        
        if (data.success) {
            const profile = profiles.find(p => p.name === profileName);
            displayAccountInfo(data.account_info, profile.exchange);
            showAlert('✓ Đã tải thông tin tài khoản', 'success');
        } else {
            showAlert('✗ Không thể lấy thông tin: ' + data.error, 'error');
        }
    } catch (error) {
        showAlert('✗ Lỗi: ' + error.message, 'error');
    }
}

// Edit profile - Load credentials into form
async function editProfile(profileName) {
    try {
        const profile = profiles.find(p => p.name === profileName);
        if (!profile) {
            showAlert('✗ Không tìm thấy profile', 'error');
            return;
        }
        
        // Update panel title and show Add New button
        const panelTitle = document.getElementById('formPanelTitle');
        const addNewBtn = document.getElementById('addNewBtn');
        
        if (panelTitle) {
            panelTitle.innerHTML = `
                <span>✏️</span>
                <span>Editing profile: ${profileName}</span>
            `;
        }
        
        // Show Add New button when editing
        if (addNewBtn) {
            addNewBtn.style.display = 'block';
        }
        
        // Scroll to form
        const formSection = document.querySelector('.exchange-main');
        if (formSection) {
            formSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Fill profile name and keep old name for reference
        document.getElementById('profileName').value = profileName;
        document.getElementById('profileName').readOnly = false; // Allow renaming
        document.getElementById('profileName').dataset.originalName = profileName; // Store original name
        
        // Normalize exchange name (dnse-mqtt -> dnse, dnse-public -> dnse, entrade-mqtt -> entrade)
        let baseExchange = profile.exchange;
        let isMqtt = false;
        let isPublic = false;
        
        if (profile.exchange.endsWith('-mqtt')) {
            baseExchange = profile.exchange.replace('-mqtt', '');
            isMqtt = true;
        } else if (profile.exchange.endsWith('-public')) {
            baseExchange = profile.exchange.replace('-public', '');
            isPublic = true;
        }
        
        // Select exchange
        document.getElementById('exchangeSelect').value = baseExchange;
        showCredentialsForm(baseExchange);
        
        // Load credentials from API
        try {
            const response = await fetch(`/api/exchange/profile/${encodeURIComponent(profileName)}/credentials`);
            const data = await response.json();
            
            if (data.success && data.credentials) {
                const creds = data.credentials;
                
                // Fill credentials based on exchange type
                if (baseExchange === 'mt5') {
                    document.getElementById('mt5Login').value = creds.login || '';
                    document.getElementById('mt5Password').value = creds.password || '';
                    document.getElementById('mt5Tickers').value = creds.tickers || '';
                    document.getElementById('mt5Timeframe').value = creds.timeframe || 'M1';
                    document.getElementById('mt5DisplayCandles').value = creds.display_candles || '1000';
                    document.getElementById('mt5Timezone').value = creds.timezone || '0';
                    
                    // Load broker and server
                    if (creds.server) {
                        let detectedBroker = null;
                        
                        // Try to match server name with broker
                        for (const [broker, servers] of Object.entries(mt5BrokerServers)) {
                            if (servers.some(s => s === creds.server)) {
                                detectedBroker = broker;
                                break;
                            }
                        }
                        
                        if (detectedBroker) {
                            document.getElementById('mt5Broker').value = detectedBroker;
                            loadMT5Servers(detectedBroker);
                            setTimeout(() => {
                                document.getElementById('mt5Server').value = creds.server;
                            }, 100);
                        } else {
                            // Unknown broker
                            document.getElementById('mt5Broker').value = 'other';
                            loadMT5Servers('other');
                            setTimeout(() => {
                                document.getElementById('mt5CustomServer').value = creds.server;
                            }, 100);
                        }
                    }
                } else if (baseExchange === 'binance') {
                    document.getElementById('binanceApiKey').value = creds.api_key || '';
                    document.getElementById('binanceApiSecret').value = creds.api_secret || '';
                    document.getElementById('binanceTickers').value = creds.tickers || '';
                    document.getElementById('binanceTimeframe').value = creds.timeframe || 'M1';
                    document.getElementById('binanceDisplayCandles').value = creds.display_candles || '1000';
                    document.getElementById('binanceTimezone').value = creds.timezone || '0';
                } else if (baseExchange === 'dnse') {
                    // Set protocol first (detect from exchange suffix or credentials)
                    const protocol = creds.protocol || (isMqtt ? 'mqtt' : isPublic ? 'public_rest' : 'rest');
                    document.getElementById('dnseProtocol').value = protocol;
                    
                    // Trigger UI update to show/hide fields based on protocol
                    if (typeof toggleDnseCredentials === 'function') {
                        toggleDnseCredentials();
                    }
                    
                    // Fill fields
                    document.getElementById('dnseUsername').value = creds.username || '';
                    document.getElementById('dnsePassword').value = creds.password || '';
                    document.getElementById('dnseTickers').value = creds.tickers || '';
                    document.getElementById('dnseTimeframe').value = creds.timeframe || 'M1';
                    document.getElementById('dnseDisplayCandles').value = creds.display_candles || '1000';
                    document.getElementById('dnseTimezone').value = creds.timezone || '7';
                    
                    // Load OTP requirement checkbox
                    const requireOTPCheckbox = document.getElementById('dnseRequireOTP');
                    if (requireOTPCheckbox) {
                        requireOTPCheckbox.checked = creds.require_otp || false;
                    }
                } else if (baseExchange === 'entrade') {
                    // Set protocol first
                    const protocol = creds.protocol || (isMqtt ? 'mqtt' : 'rest');
                    document.getElementById('entradeProtocol').value = protocol;
                    
                    // Fill fields
                    document.getElementById('entradeUsername').value = creds.username || '';
                    document.getElementById('entradePassword').value = creds.password || '';
                    document.getElementById('entradeTickers').value = creds.tickers || '';
                    document.getElementById('entradeTimeframe').value = creds.timeframe || 'M1';
                    document.getElementById('entradeDisplayCandles').value = creds.display_candles || '1000';
                    document.getElementById('entradeTimezone').value = creds.timezone || '7';
                    document.getElementById('entradeIsDemo').checked = creds.is_demo || false;
                }
            }
        } catch (error) {
            console.error('Load credentials error:', error);
            showAlert('ℹ️ Không thể load credentials. Vui lòng nhập lại.', 'info');
        }
        
        // Load profile usage checkboxes
        const useForDataCheckbox = document.getElementById('useForData');
        const useForTradingCheckbox = document.getElementById('useForTrading');
        
        if (useForDataCheckbox) {
            useForDataCheckbox.checked = profile.use_for_data !== false; // Default true
        }
        
        if (useForTradingCheckbox) {
            useForTradingCheckbox.checked = profile.use_for_trading !== false; // Default true
        }
        
        // Change button text
        const submitBtn = document.querySelector('#profileForm button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerHTML = '<span>💾</span><span>Update Profile</span>';
        }
        
        logToTerminal(`Editing profile: ${profileName} (Data: ${profile.use_for_data !== false}, Trading: ${profile.use_for_trading !== false})`, 'info');
        
    } catch (error) {
        showAlert('✗ Lỗi: ' + error.message, 'error');
        logToTerminal(`Edit error: ${error.message}`, 'error');
    }
}

// Delete profile
async function deleteProfile(profileName) {
    if (!confirm(`Bạn có chắc muốn xóa profile "${profileName}"?`)) {
        logToTerminal(`Delete cancelled: ${profileName}`, 'warning');
        return;
    }
    
    logToTerminal(`Deleting profile: ${profileName}`, 'info');
    
    try {
        // Encode profile name for URL
        const encodedName = encodeURIComponent(profileName);
        const response = await fetch(`/api/exchange/profile/${encodedName}`, {
            method: 'DELETE'
        });
        
        console.log('Delete response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Delete response data:', data);
        
        if (data.success) {
            logToTerminal(`Profile deleted: ${profileName}`, 'success');
            showAlert('✓ Đã xóa profile', 'success');
            await loadProfiles();
            
            // Update Connection modal dropdown
            if (typeof window.loadQuickProfileSelect === 'function') {
                window.loadQuickProfileSelect();
            }
        } else {
            logToTerminal(`Delete failed: ${data.error}`, 'error');
            showAlert('✗ Xóa profile thất bại: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        logToTerminal(`Delete error: ${error.message}`, 'error');
        showAlert('✗ Lỗi: ' + error.message, 'error');
    }
}

// Reset form
function resetForm() {
    document.getElementById('profileForm').reset();
    document.querySelectorAll('.credentials-form').forEach(form => {
        form.classList.remove('active');
    });
    document.getElementById('accountInfo').style.display = 'none';
    
    // Reset MT5 broker and server
    const mt5BrokerSelect = document.getElementById('mt5Broker');
    const mt5ServerSelect = document.getElementById('mt5Server');
    const customGroup = document.getElementById('mt5CustomServerGroup');
    
    if (mt5BrokerSelect) mt5BrokerSelect.value = '';
    if (mt5ServerSelect) {
        mt5ServerSelect.innerHTML = '<option value="">-- Select Broker First --</option>';
        mt5ServerSelect.disabled = true;
    }
    if (customGroup) customGroup.style.display = 'none';
    
    // Reset profile name readonly and clear original name
    const profileNameInput = document.getElementById('profileName');
    profileNameInput.readOnly = false;
    delete profileNameInput.dataset.originalName;
    
    // Reset button text
    const submitBtn = document.querySelector('#profileForm button[type="submit"]');
    if (submitBtn) {
        submitBtn.innerHTML = '<span>💾</span><span>Save Profile</span>';
    }
}

// Show alert
function showAlert(message, type) {
    const alertBox = document.getElementById('alertBox');
    alertBox.className = `alert alert-${type} show`;
    alertBox.textContent = message;
    
    setTimeout(() => {
        alertBox.classList.remove('show');
    }, 5000);
}

// Format number
function formatNumber(num) {
    if (num === undefined || num === null) return '0';
    return parseFloat(num).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Format date
function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Toggle DNSE OTP field based on protocol

// Show account info modal
async function showAccountInfo(profileName) {
    try {
        const profile = profiles.find(p => p.name === profileName);
        if (!profile) {
            showAlert('✗ Không tìm thấy profile', 'error');
            return;
        }
        
        logToTerminal(`Fetching account info for: ${profileName}`, 'info');
        
        // Check if connected
        if (!profile.connected) {
            showAlert('⚠️ Profile chưa kết nối. Vui lòng kết nối trước.', 'warning');
            return;
        }
        
        // Fetch all data in parallel
        const [accountResponse, positionsResponse, ordersResponse, dealsResponse] = await Promise.all([
            fetch(`/api/exchange/account/${encodeURIComponent(profileName)}`),
            fetch(`/api/exchange/positions/${encodeURIComponent(profileName)}`),
            fetch(`/api/exchange/orders/${encodeURIComponent(profileName)}`),
            fetch(`/api/exchange/deals/${encodeURIComponent(profileName)}`)
        ]);
        
        const accountData = await accountResponse.json();
        const positionsData = await positionsResponse.json();
        const ordersData = await ordersResponse.json();
        const dealsData = await dealsResponse.json();
        
        if (!accountData.success) {
            showAlert('✗ Không thể lấy thông tin tài khoản: ' + accountData.error, 'error');
            return;
        }
        
        // Build modal with tabs
        const accountInfo = accountData.account_info || {};
        const positions = positionsData.positions || [];
        const orders = ordersData.orders || [];
        const deals = dealsData.deals || [];
        
        let infoHTML = `
            <div class="account-info-modal">
                <div class="info-header">
                    <h3>📊 Account Info: ${profileName}</h3>
                    <span class="exchange-badge">${profile.exchange.toUpperCase()}</span>
                </div>
                
                <!-- Tabs -->
                <div class="modal-tabs">
                    <button class="tab-btn active" onclick="switchTab(event, 'accountTab')">
                        💰 Tài khoản
                    </button>
                    <button class="tab-btn" onclick="switchTab(event, 'tradingTab')">
                        📈 Giao dịch
                    </button>
                </div>
                
                <!-- Account Tab -->
                <div id="accountTab" class="tab-content active">
                    <div class="info-section">
                        <h4>💰 Thông tin tài khoản</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                            <!-- Column 1 -->
                            <table class="info-table">
        `;
        
        // Column 1: Basic Info
        if (accountInfo.account_id) infoHTML += `<tr><td>Account ID:</td><td><strong>${accountInfo.account_id}</strong></td></tr>`;
        if (accountInfo.account_type) infoHTML += `<tr><td>Loại TK:</td><td><strong>${accountInfo.account_type}</strong></td></tr>`;
        if (accountInfo.username) infoHTML += `<tr><td>Username:</td><td><strong>${accountInfo.username}</strong></td></tr>`;
        if (accountInfo.cash_balance !== undefined) infoHTML += `<tr><td>Số dư tiền:</td><td><strong>${formatCurrency(accountInfo.cash_balance)}</strong></td></tr>`;
        if (accountInfo.purchasing_power !== undefined) infoHTML += `<tr><td>Sức mua:</td><td><strong>${formatCurrency(accountInfo.purchasing_power)}</strong></td></tr>`;
        if (accountInfo.debt !== undefined) infoHTML += `<tr><td>Nợ:</td><td><strong>${formatCurrency(accountInfo.debt)}</strong></td></tr>`;
        
        infoHTML += `
                            </table>
                            <!-- Column 2 -->
                            <table class="info-table">
        `;
        
        // Column 2: Financial Info
        if (accountInfo.total_asset !== undefined) infoHTML += `<tr><td>Tổng tài sản:</td><td><strong>${formatCurrency(accountInfo.total_asset)}</strong></td></tr>`;
        if (accountInfo.balance !== undefined) infoHTML += `<tr><td>Số dư:</td><td><strong>${formatCurrency(accountInfo.balance)}</strong></td></tr>`;
        if (accountInfo.equity !== undefined) infoHTML += `<tr><td>Equity:</td><td><strong>${formatCurrency(accountInfo.equity)}</strong></td></tr>`;
        if (accountInfo.available !== undefined) infoHTML += `<tr><td>Khả dụng:</td><td><strong>${formatCurrency(accountInfo.available)}</strong></td></tr>`;
        if (accountInfo.positions_count !== undefined) infoHTML += `<tr><td>Số vị thế:</td><td><strong>${accountInfo.positions_count}</strong></td></tr>`;
        if (accountInfo.status) infoHTML += `<tr><td>Trạng thái:</td><td><strong style="color: #26a69a;">${accountInfo.status}</strong></td></tr>`;
        
        infoHTML += `
                            </table>
                        </div>
                    </div>
                    
                    <!-- Realtime Data Section -->
                    <div class="info-section" style="background: linear-gradient(135deg, #1a1e2b 0%, #131722 100%); border: 1px solid #2962ff; border-radius: 8px; padding: 15px; margin-top: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <h4 style="margin: 0; color: #2962ff;">📡 Realtime Data</h4>
                            <span id="realtimeTimestamp" style="font-size: 11px; color: #787b86;"></span>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                            <div style="text-align: center; padding: 10px; background: rgba(41, 98, 255, 0.1); border-radius: 6px;">
                                <div style="font-size: 11px; color: #787b86; margin-bottom: 5px;">Balance</div>
                                <div id="realtimeBalance" style="font-size: 18px; font-weight: 700; color: #d1d4dc;">${formatNumber(accountInfo.balance || 0)}</div>
                            </div>
                            <div style="text-align: center; padding: 10px; background: rgba(41, 98, 255, 0.1); border-radius: 6px;">
                                <div style="font-size: 11px; color: #787b86; margin-bottom: 5px;">Equity</div>
                                <div id="realtimeEquity" style="font-size: 18px; font-weight: 700; color: #d1d4dc;">${formatNumber(accountInfo.equity || 0)}</div>
                            </div>
                            <div style="text-align: center; padding: 10px; background: rgba(41, 98, 255, 0.1); border-radius: 6px;">
                                <div style="font-size: 11px; color: #787b86; margin-bottom: 5px;">P&L</div>
                                <div id="realtimePnL" class="${((accountInfo.equity || 0) - (accountInfo.balance || 0)) >= 0 ? 'text-success' : 'text-danger'}" style="font-size: 18px; font-weight: 700;">${formatNumber((accountInfo.equity || 0) - (accountInfo.balance || 0))}</div>
                            </div>
                        </div>
                        <div style="text-align: center; margin-top: 10px; font-size: 10px; color: #787b86;">
                            ⚡ Tự động cập nhật mỗi 2 giây
                        </div>
                    </div>
        `;
        
        // Display positions if any
        if (positions.length > 0) {
            infoHTML += `
                    <div class="info-section">
                        <h4>📈 Vị thế đang nắm giữ (${positions.length})</h4>
                        <table class="positions-table">
                            <thead>
                                <tr>
                                    <th>Symbol</th>
                                    <th>Side</th>
                                    <th>Size</th>
                                    <th>Entry Price</th>
                                    <th>P&L</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            
            positions.forEach(pos => {
                const pnlClass = (pos.unrealized_pnl || 0) >= 0 ? 'text-success' : 'text-danger';
                const sideClass = pos.side === 'LONG' || pos.side === 'BUY' ? 'text-success' : 'text-danger';
                infoHTML += `
                    <tr>
                        <td><strong>${pos.symbol}</strong></td>
                        <td class="${sideClass}">${pos.side}</td>
                        <td>${pos.size || pos.quantity || '--'}</td>
                        <td>${formatCurrency(pos.entry_price || pos.entryPrice || 0)}</td>
                        <td class="${pnlClass}">${formatCurrency(pos.unrealized_pnl || pos.unrealizedPnl || 0)}</td>
                    </tr>
                `;
            });
            
            infoHTML += `
                            </tbody>
                        </table>
                    </div>
            `;
        }
        
        infoHTML += `</div>`; // Close accountTab
        
        // Trading Tab
        infoHTML += `
                <div id="tradingTab" class="tab-content">
                    <!-- Orders Section -->
                    <div class="info-section">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h4>📋 Sổ lệnh (${orders.length})</h4>
                            ${orders.length > 0 ? `
                                <div style="display: flex; gap: 8px;">
                                    <select id="orderStatusFilter" onchange="filterOrders()" style="padding: 6px 10px; background: #131722; border: 1px solid #2a2e39; color: #d1d4dc; border-radius: 4px; font-size: 11px;">
                                        <option value="all">Tất cả</option>
                                        <option value="FILLED">Đã khớp</option>
                                        <option value="PENDING">Chờ khớp</option>
                                        <option value="CANCELLED">Đã hủy</option>
                                    </select>
                                </div>
                            ` : ''}
                        </div>
        `;
        
        if (orders.length > 0) {
            infoHTML += `
                        <div class="orders-container" id="ordersContainer">
                            <table class="positions-table">
                                <thead>
                                    <tr>
                                        <th style="width: 15%;">Time</th>
                                        <th style="width: 12%;">Symbol</th>
                                        <th style="width: 8%;">Side</th>
                                        <th style="width: 10%;">Type</th>
                                        <th style="width: 10%;">Qty</th>
                                        <th style="width: 12%;">Price</th>
                                        <th style="width: 10%;">Filled</th>
                                        <th style="width: 12%;">Status</th>
                                        <th style="width: 11%;">Order ID</th>
                                    </tr>
                                </thead>
                                <tbody id="ordersTableBody">
        `;
            
            orders.forEach(order => {
                const sideClass = order.side === 'BUY' || order.side === 'NB' ? 'text-success' : 'text-danger';
                const statusColor = order.status === 'FILLED' ? '#26a69a' : 
                                  order.status === 'PENDING' || order.status === 'NEW' ? '#ffa726' : 
                                  order.status === 'CANCELLED' ? '#ef5350' : '#787b86';
                infoHTML += `
                    <tr class="order-row" data-status="${order.status}">
                        <td style="font-size: 10px;">${formatTime(order.time)}</td>
                        <td><strong>${order.symbol}</strong></td>
                        <td class="${sideClass}">${order.side}</td>
                        <td>${order.order_type}</td>
                        <td>${order.quantity}</td>
                        <td>${formatNumber(order.price)}</td>
                        <td>${order.filled || 0}</td>
                        <td style="color: ${statusColor}; font-weight: 600;">${order.status}</td>
                        <td style="font-size: 9px;">${String(order.order_id).substring(0, 12)}...</td>
                    </tr>
                `;
            });
            
            infoHTML += `
                                </tbody>
                            </table>
                        </div>
                        <div style="text-align: center; color: #787b86; font-size: 11px; margin-top: 10px;">
                            Hiển thị ${Math.min(50, orders.length)} / ${orders.length} lệnh gần nhất
                        </div>
            `;
        } else {
            infoHTML += `<p style="color: #787b86; text-align: center; padding: 30px;">Không có lệnh nào</p>`;
        }
        
        infoHTML += `
                    </div>
                    
                    <!-- Deals Section -->
                    <div class="info-section">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h4>📊 Lịch sử giao dịch (${deals.length})</h4>
                        </div>
        `;
        
        if (deals.length > 0) {
            infoHTML += `
                        <div class="orders-container">
                            <table class="positions-table">
                                <thead>
                                    <tr>
                                        <th style="width: 18%;">Time</th>
                                        <th style="width: 15%;">Symbol</th>
                                        <th style="width: 12%;">Side</th>
                                        <th style="width: 12%;">Qty</th>
                                        <th style="width: 15%;">Price</th>
                                        <th style="width: 15%;">Value</th>
                                        <th style="width: 13%;">Deal ID</th>
                                    </tr>
                                </thead>
                                <tbody>
        `;
            
            deals.forEach(deal => {
                const sideClass = deal.side === 'BUY' || deal.side === 'NB' ? 'text-success' : 'text-danger';
                const value = deal.price * deal.quantity;
                infoHTML += `
                    <tr>
                        <td style="font-size: 10px;">${formatTime(deal.time)}</td>
                        <td><strong>${deal.symbol}</strong></td>
                        <td class="${sideClass}" style="font-weight: 600;">${deal.side}</td>
                        <td>${deal.quantity}</td>
                        <td>${formatNumber(deal.price)}</td>
                        <td><strong>${formatNumber(value)}</strong></td>
                        <td style="font-size: 9px;">${String(deal.deal_id).substring(0, 12)}...</td>
                    </tr>
                `;
            });
            
            infoHTML += `
                                </tbody>
                            </table>
                        </div>
                        <div style="text-align: center; color: #787b86; font-size: 11px; margin-top: 10px;">
                            Hiển thị ${Math.min(50, deals.length)} / ${deals.length} giao dịch gần nhất
                        </div>
            `;
        } else {
            infoHTML += `<p style="color: #787b86; text-align: center; padding: 30px;">Chưa có giao dịch nào</p>`;
        }
        
        infoHTML += `
                    </div>
                </div>
        `;
        
        infoHTML += `
                <div class="info-footer">
                    <button class="btn btn-primary" onclick="closeAccountInfoModal()">Đóng</button>
                </div>
            </div>
        `;
        
        // Show modal
        // Show modal
        showModal(infoHTML);
        logToTerminal(`✅ Account info loaded for ${profileName}`, 'success');
        
        // Start realtime updates
        startRealtimeUpdates(profileName);
        
    } catch (error) {
        showAlert('✗ Lỗi: ' + error.message, 'error');
        logToTerminal(`Account info error: ${error.message}`, 'error');
    }
}

// Switch tab function
function switchTab(event, tabId) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to clicked tab and corresponding content
    event.target.classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

// Helper functions
function formatCurrency(value) {
    if (value === null || value === undefined) return '--';
    return parseFloat(value).toLocaleString('vi-VN') + ' ₫';
}

function formatNumber(value) {
    if (value === null || value === undefined) return '--';
    return parseFloat(value).toLocaleString('vi-VN');
}

function formatTime(timeStr) {
    if (!timeStr || timeStr === 'N/A') return '--';
    try {
        const date = new Date(timeStr);
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const seconds = date.getSeconds().toString().padStart(2, '0');
        return `${hours}:${minutes}:${seconds}`;
    } catch {
        return timeStr;
    }
}

function filterOrders() {
    const filter = document.getElementById('orderStatusFilter').value;
    const rows = document.querySelectorAll('.order-row');
    
    rows.forEach(row => {
        const status = row.dataset.status;
        if (filter === 'all' || status === filter) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function showModal(content) {
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.id = 'accountInfoOverlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    const modal = document.createElement('div');
    modal.style.cssText = `
        background: #1e222d;
        border-radius: 8px;
        padding: 0;
        max-width: 800px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    `;
    
    modal.innerHTML = content;
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    // Click outside to close
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            closeAccountInfoModal();
        }
    });
}

function closeAccountInfoModal() {
    const overlay = document.getElementById('accountInfoOverlay');
    if (overlay) {
        overlay.remove();
    }
    
    // Stop realtime updates
    stopRealtimeUpdates();
}

// Start realtime updates for loaded profile
function startRealtimeUpdates(profileName) {
    // Stop existing interval if any
    stopRealtimeUpdates();
    
    currentLoadedProfile = profileName;
    
    // Update every 2 seconds
    realtimeInterval = setInterval(async () => {
        await updateRealtimeData(profileName);
    }, 2000);
    
    logToTerminal(`Started realtime updates for ${profileName}`, 'info');
}

// Stop realtime updates
function stopRealtimeUpdates() {
    if (realtimeInterval) {
        clearInterval(realtimeInterval);
        realtimeInterval = null;
        
        if (currentLoadedProfile) {
            logToTerminal(`Stopped realtime updates for ${currentLoadedProfile}`, 'info');
            currentLoadedProfile = null;
        }
    }
}

// Update realtime data
async function updateRealtimeData(profileName) {
    try {
        const response = await fetch(`/api/exchange/realtime/${profileName}`);
        const data = await response.json();
        
        if (data.success && data.account_info) {
            // Update balance display
            const balanceEl = document.getElementById('realtimeBalance');
            const equityEl = document.getElementById('realtimeEquity');
            const pnlEl = document.getElementById('realtimePnL');
            const timestampEl = document.getElementById('realtimeTimestamp');
            
            if (balanceEl) {
                balanceEl.textContent = formatNumber(data.account_info.balance || 0);
            }
            if (equityEl) {
                equityEl.textContent = formatNumber(data.account_info.equity || 0);
            }
            if (pnlEl) {
                const pnl = (data.account_info.equity || 0) - (data.account_info.balance || 0);
                const pnlClass = pnl >= 0 ? 'text-success' : 'text-danger';
                pnlEl.className = pnlClass;
                pnlEl.textContent = (pnl >= 0 ? '+' : '') + formatNumber(pnl);
            }
            if (timestampEl) {
                const now = new Date();
                timestampEl.textContent = now.toLocaleTimeString('vi-VN', { hour12: false });
            }
        }
    } catch (error) {
        console.error('Update realtime data error:', error);
    }
}

// ==================== DNSE OTP MODAL FUNCTIONS ====================

function showDNSEOTPModal() {
    const modal = document.getElementById('dnseOTPModal');
    if (modal) {
        modal.style.display = 'block';
        // Clear previous OTP
        document.getElementById('dnseModalOTP').value = '';
        // Reset status
        const statusDiv = document.getElementById('dnseOTPStatus');
        if (statusDiv) statusDiv.style.display = 'none';
        
        logToTerminal('📧 DNSE OTP Modal opened - Request OTP to continue', 'info');
    }
}

function closeDNSEOTPModal() {
    const modal = document.getElementById('dnseOTPModal');
    if (modal) {
        modal.style.display = 'none';
        logToTerminal('DNSE OTP Modal closed', 'info');
    }
}

async function requestDNSEModalOTP() {
    const btn = document.getElementById('btnRequestDNSEModalOTP');
    const statusDiv = document.getElementById('dnseOTPStatus');
    
    // Get credentials
    const username = document.getElementById('dnseUsername').value;
    const password = document.getElementById('dnsePassword').value;
    
    if (!username || !password) {
        showStatusMessage('❌ Please enter Username and Password first', 'error');
        return;
    }
    
    // Disable button and show loading
    btn.disabled = true;
    btn.innerHTML = '⏳ Requesting...';
    
    logToTerminal('📧 Requesting OTP from DNSE...', 'info');
    
    try {
        const response = await fetch('/api/exchange/request-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                exchange: 'dnse',
                username: username,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatusMessage('✅ OTP sent to your email! Check your inbox.', 'success');
            logToTerminal('✅ OTP request successful - Check your email', 'success');
        } else {
            showStatusMessage('❌ ' + (data.error || 'Failed to request OTP'), 'error');
            logToTerminal('❌ OTP request failed: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        showStatusMessage('❌ Connection error: ' + error.message, 'error');
        logToTerminal('❌ OTP request error: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '📱 Request OTP';
    }
}

function showStatusMessage(message, type) {
    const statusDiv = document.getElementById('dnseOTPStatus');
    if (!statusDiv) return;
    
    const colors = {
        success: { bg: 'rgba(76, 175, 80, 0.1)', border: '#4CAF50', text: '#4CAF50' },
        error: { bg: 'rgba(244, 67, 54, 0.1)', border: '#f44336', text: '#f44336' },
        info: { bg: 'rgba(33, 150, 243, 0.1)', border: '#2196F3', text: '#2196F3' }
    };
    
    const color = colors[type] || colors.info;
    
    statusDiv.style.display = 'block';
    statusDiv.style.background = color.bg;
    statusDiv.style.borderLeft = `4px solid ${color.border}`;
    statusDiv.style.color = color.text;
    statusDiv.innerHTML = message;
}

async function submitDNSEOTP() {
    const otp = document.getElementById('dnseModalOTP').value.trim();
    const btn = document.getElementById('btnSubmitDNSEOTP');
    
    if (!otp) {
        showStatusMessage('❌ Please enter OTP code', 'error');
        return;
    }
    
    if (otp.length !== 6) {
        showStatusMessage('❌ OTP must be 6 digits', 'error');
        return;
    }
    
    // Get credentials
    const username = document.getElementById('dnseUsername').value;
    const password = document.getElementById('dnsePassword').value;
    const protocol = document.getElementById('dnseProtocol').value;
    const tickers = document.getElementById('dnseTickers').value;
    const timeframe = document.getElementById('dnseTimeframe').value;
    
    const credentials = {
        username: username,
        password: password,
        protocol: protocol,
        otp: otp,
        tickers: tickers,
        timeframe: timeframe
    };
    
    // Disable button
    btn.disabled = true;
    btn.innerHTML = '⏳ Connecting...';
    
    logToTerminal('🔐 Connecting to DNSE with OTP...', 'info');
    
    try {
        const response = await fetch('/api/exchange/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                exchange: 'dnse',
                credentials: credentials
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatusMessage('✅ Connection successful!', 'success');
            logToTerminal('✅ DNSE connection successful!', 'success');
            
            if (data.account_info) {
                logToTerminal(`Account: ${data.account_info.name || 'N/A'}`, 'success');
                displayAccountInfo(data.account_info, 'dnse');
            }
            
            // Close modal after 1 second
            setTimeout(() => {
                closeDNSEOTPModal();
                showAlert('✓ DNSE kết nối thành công!', 'success');
            }, 1000);
        } else {
            showStatusMessage('❌ ' + (data.error || 'Connection failed'), 'error');
            logToTerminal('❌ DNSE connection failed: ' + (data.error || 'Unknown error'), 'error');
            showAlert('✗ Kết nối thất bại: ' + data.error, 'error');
        }
    } catch (error) {
        showStatusMessage('❌ Connection error: ' + error.message, 'error');
        logToTerminal('❌ Connection error: ' + error.message, 'error');
        showAlert('✗ Lỗi kết nối: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🚀 Connect with OTP';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('dnseOTPModal');
    if (event.target === modal) {
        closeDNSEOTPModal();
    }
    
    const profileModal = document.getElementById('dnseProfileOTPModal');
    if (event.target === profileModal) {
        closeDNSEProfileOTPModal();
    }
}

// ==================== DNSE PROFILE OTP MODAL (cho saved profiles) ====================

function showDNSEProfileOTPModal(profileName, username) {
    // Tạo modal nếu chưa tồn tại
    let modal = document.getElementById('dnseProfileOTPModal');
    if (!modal) {
        const modalHTML = `
            <div id="dnseProfileOTPModal" class="modal" style="display: none;">
                <div class="modal-content" style="max-width: 500px;">
                    <div class="modal-header">
                        <h3>🔐 DNSE OTP Required</h3>
                        <button class="close-btn" onclick="closeDNSEProfileOTPModal()">×</button>
                    </div>
                    <div class="modal-body">
                        <div style="margin-bottom: 20px;">
                            <p><strong>Profile:</strong> <span id="profileOTPName"></span></p>
                            <p><strong>Username:</strong> <span id="profileOTPUsername"></span></p>
                        </div>
                        
                        <div id="profileOTPStatus" style="display: none; padding: 12px; margin-bottom: 15px; border-radius: 4px;"></div>
                        
                        <div style="margin-bottom: 15px;">
                            <button id="btnRequestProfileOTP" onclick="requestDNSEProfileOTP()" 
                                    class="btn btn-primary" style="width: 100%;">
                                📱 Request OTP (Email)
                            </button>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 500;">OTP Code:</label>
                            <input type="text" id="profileOTPCode" placeholder="Enter 6-digit OTP" 
                                   maxlength="6" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
                        </div>
                        
                        <button id="btnSubmitProfileOTP" onclick="submitDNSEProfileOTP()" 
                                class="btn btn-success" style="width: 100%;">
                            🚀 Connect with OTP
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        modal = document.getElementById('dnseProfileOTPModal');
    }
    
    // Set profile info
    document.getElementById('profileOTPName').textContent = profileName;
    document.getElementById('profileOTPUsername').textContent = username;
    document.getElementById('profileOTPCode').value = '';
    
    // Store profile name for later use
    modal.dataset.profileName = profileName;
    
    // Show modal
    modal.style.display = 'block';
    logToTerminal(`📧 OTP Modal opened for profile: ${profileName}`, 'info');
}

function closeDNSEProfileOTPModal() {
    const modal = document.getElementById('dnseProfileOTPModal');
    if (modal) {
        modal.style.display = 'none';
        logToTerminal('OTP Modal closed', 'info');
    }
}

async function requestDNSEProfileOTP() {
    const modal = document.getElementById('dnseProfileOTPModal');
    const profileName = modal.dataset.profileName;
    const btn = document.getElementById('btnRequestProfileOTP');
    const statusDiv = document.getElementById('profileOTPStatus');
    
    // Disable button
    btn.disabled = true;
    btn.innerHTML = '⏳ Requesting...';
    
    logToTerminal('📧 Requesting OTP from DNSE...', 'info');
    
    try {
        const response = await fetch('/api/exchange/request-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                exchange: 'dnse',
                profile_name: profileName  // Backend sẽ lấy credentials từ profile
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showProfileOTPStatus('✅ OTP sent to your email! Check your inbox.', 'success');
            logToTerminal('✅ OTP request successful - Check your email', 'success');
        } else {
            showProfileOTPStatus('❌ ' + (data.error || 'Failed to request OTP'), 'error');
            logToTerminal('❌ OTP request failed: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        showProfileOTPStatus('❌ Connection error: ' + error.message, 'error');
        logToTerminal('❌ OTP request error: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '📱 Request OTP (Email)';
    }
}

async function submitDNSEProfileOTP() {
    const modal = document.getElementById('dnseProfileOTPModal');
    const profileName = modal.dataset.profileName;
    const otpCode = document.getElementById('profileOTPCode').value.trim();
    const btn = document.getElementById('btnSubmitProfileOTP');
    
    if (!otpCode) {
        showProfileOTPStatus('❌ Please enter OTP code', 'error');
        return;
    }
    
    if (otpCode.length !== 6) {
        showProfileOTPStatus('❌ OTP must be 6 digits', 'error');
        return;
    }
    
    // Disable button
    btn.disabled = true;
    btn.innerHTML = '⏳ Connecting...';
    
    logToTerminal(`🔐 Connecting to DNSE with OTP for profile: ${profileName}`, 'info');
    
    try {
        const response = await fetch(`/api/exchange/connect/${profileName}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ otp: otpCode })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showProfileOTPStatus('✅ Connection successful!', 'success');
            logToTerminal('✅ DNSE connection successful!', 'success');
            showAlert('✓ DNSE kết nối thành công!', 'success');
            
            // Close modal and reload profiles
            setTimeout(async () => {
                closeDNSEProfileOTPModal();
                await loadProfiles();
            }, 1000);
        } else {
            showProfileOTPStatus('❌ ' + (data.error || 'Connection failed'), 'error');
            logToTerminal('❌ DNSE connection failed: ' + (data.error || 'Unknown error'), 'error');
            showAlert('✗ Kết nối thất bại: ' + data.error, 'error');
        }
    } catch (error) {
        showProfileOTPStatus('❌ Connection error: ' + error.message, 'error');
        logToTerminal('❌ Connection error: ' + error.message, 'error');
        showAlert('✗ Lỗi kết nối: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🚀 Connect with OTP';
    }
}

function showProfileOTPStatus(message, type) {
    const statusDiv = document.getElementById('profileOTPStatus');
    if (!statusDiv) return;
    
    const colors = {
        success: { bg: 'rgba(76, 175, 80, 0.1)', border: '#4CAF50', text: '#4CAF50' },
        error: { bg: 'rgba(244, 67, 54, 0.1)', border: '#f44336', text: '#f44336' },
        info: { bg: 'rgba(33, 150, 243, 0.1)', border: '#2196F3', text: '#2196F3' }
    };
    
    const color = colors[type] || colors.info;
    
    statusDiv.style.display = 'block';
    statusDiv.style.background = color.bg;
    statusDiv.style.borderLeft = `4px solid ${color.border}`;
    statusDiv.style.color = color.text;
    statusDiv.innerHTML = message;
}

// ==================== END DNSE PROFILE OTP MODAL ====================

// Show new profile form (clear all fields)
function showNewProfileForm() {
    console.log('📝 Showing new profile form');
    
    // Update panel title and hide Add New button
    const panelTitle = document.getElementById('formPanelTitle');
    const addNewBtn = document.getElementById('addNewBtn');
    
    if (panelTitle) {
        panelTitle.innerHTML = `
            <span>➕</span>
            <span>Add New Profile</span>
        `;
    }
    
    // Hide Add New button when creating new profile
    if (addNewBtn) {
        addNewBtn.style.display = 'none';
    }
    
    // Clear form
    document.getElementById('profileForm').reset();
    
    // Clear profile name and enable editing
    const profileNameInput = document.getElementById('profileName');
    if (profileNameInput) {
        profileNameInput.value = '';
        profileNameInput.readOnly = false;
        delete profileNameInput.dataset.originalName;
    }
    
    // Reset exchange select to default
    const exchangeSelect = document.getElementById('exchangeSelect');
    if (exchangeSelect) {
        exchangeSelect.value = '';
    }
    
    // Hide all credential forms
    const forms = ['binanceCredentials', 'mt5Credentials', 'dnseCredentials', 'entradeCredentials', 'entradeMqttCredentials'];
    forms.forEach(formId => {
        const form = document.getElementById(formId);
        if (form) {
            form.style.display = 'none';
        }
    });
    
    // Reset profile usage checkboxes to default (both checked)
    const useForDataCheckbox = document.getElementById('useForData');
    const useForTradingCheckbox = document.getElementById('useForTrading');
    
    if (useForDataCheckbox) {
        useForDataCheckbox.checked = true;
    }
    
    if (useForTradingCheckbox) {
        useForTradingCheckbox.checked = true;
    }
    
    // Reset submit button text
    const submitBtn = document.querySelector('#profileForm button[type="submit"]');
    if (submitBtn) {
        submitBtn.innerHTML = '<span>💾</span><span>Save Profile</span>';
    }
    
    // Clear alert
    const alertBox = document.getElementById('alertBox');
    if (alertBox) {
        alertBox.style.display = 'none';
        alertBox.innerHTML = '';
    }
    
    // Scroll to form
    const formSection = document.querySelector('.exchange-main');
    if (formSection) {
        formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    console.log('✅ Form cleared and ready for new profile');
}

