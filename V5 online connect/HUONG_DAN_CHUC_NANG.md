# HƯỚNG DẪN CHỨC NĂNG CÁC FILE EXCHANGE API

## 📋 TỔNG QUAN

Hệ thống giao dịch hỗ trợ kết nối với nhiều sàn giao dịch khác nhau thông qua các API client. Dưới đây là chi tiết về từng file và chức năng của chúng.

---

## 📁 CẤU TRÚC FILE NGUỒN (SOURCE.zip)

### 1. **DNSE_API.py** - Client cho sàn DNSE (Cổ phiếu + Phái sinh)

#### Mục đích:
- Kết nối với sàn DNSE để giao dịch cổ phiếu và phái sinh
- Sử dụng REST API với xác thực OTP qua email

#### Chức năng chính:

**Authentication & Authorization:**
- `authenticate(email, password)` - Đăng nhập lấy token
- `get_otp()` - Yêu cầu mã OTP gửi về email
- `get_trading_token(otp)` - Lấy trading token sau khi nhập OTP

**Account Management:**
- `get_account_info()` - Lấy thông tin nhà đầu tư
- `get_investor_account_info()` - Lấy thông tin tiểu khoản
- `get_account_balance_info(investor_account_id)` - Kiểm tra số dư tài khoản

**Trading Operations:**
- `GetDeals(investor_account_id)` - Lấy danh sách các deal đang mở
- `CloseDeal(deal_id, investor_account_id)` - Đóng deal
- `GetDealInfos(deal_id, investor_account_id)` - Xem chi tiết deal

**Derivatives Management:**
- `DepositDerivative()` - Nộp tiền ký quỹ vào tài khoản phái sinh
- `WithdrawDerivative()` - Rút tiền ký quỹ từ tài khoản phái sinh

#### Đặc điểm:
- ✅ **Yêu cầu OTP**: Bắt buộc xác thực email OTP khi trading
- 🔐 **Security**: Sử dụng Bearer token + Trading token
- 🌐 **Base URL**: `https://api.dnse.com.vn`

---

### 2. **EntradeAPI.py** - Client cơ bản cho sàn Entrade

#### Mục đích:
- Kết nối với sàn Entrade (cả Real và Demo)
- Giao dịch phái sinh futures (VN30F1M, VN30F2M, etc.)

#### Chức năng chính:

**Authentication:**
- `authenticate(email, password)` - Đăng nhập chung cho cả Real/Demo
- `get_otp()` - Lấy OTP (chỉ cho Real account, Demo skip)
- `get_trading_token(otp_code)` - Lấy trading token

**Account & Portfolio:**
- `get_investor_info()` - Thông tin nhà đầu tư
- `get_investor_account_info(investor_id)` - Số dư tài khoản
- `get_derivative_margin_portfolios(investor_id)` - Danh sách portfolios
- `get_buying_power()` - Tính sức mua (PPSE)

**Order Management:**
- `place_order()` - Đặt lệnh (NB=Mua, NS=Bán)
- `get_order_list(investor_id)` - Danh sách lệnh
- `get_pending_orders(investor_id)` - Lệnh chờ khớp
- `get_order(order_id)` - Chi tiết 1 lệnh
- `cancel_order(order_id)` - Hủy lệnh
- `cancel_all_orders(investor_id)` - Hủy tất cả lệnh

**Deals:**
- `get_current_deals(investor_id)` - Các deal đang mở
- `get_derivative_info()` - Thông tin các hợp đồng phái sinh
- `get_symbol_info(symbol_type)` - Thông tin symbol cụ thể

#### Đặc điểm:
- 🎮 **Demo Mode**: Hỗ trợ paper trading không cần OTP
- 💰 **Real Mode**: Trading thật yêu cầu OTP
- 🌐 **Base URLs**: 
  - Real: `https://services.entrade.com.vn/entrade-api`
  - Demo: `https://services.entrade.com.vn/papertrade-entrade-api`

---

### 3. **EntradeAPI2.py** - Client nâng cao cho Entrade (Smart Order)

#### Mục đích:
- Version nâng cao với Smart Order API
- Hỗ trợ các chiến lược giao dịch phức tạp hơn

#### Chức năng bổ sung:

**Smart Order Features:**
- Đặt lệnh thông minh với điều kiện
- Stop Loss / Take Profit tự động
- Trailing Stop
- OCO (One Cancels Other)
- Bracket Orders

**Portfolio Analytics:**
- Phân tích danh mục
- Risk management
- Position sizing

#### Đặc điểm:
- 🚀 **Advanced**: Smart order với nhiều tính năng
- 🌐 **Base URLs**:
  - Real: `https://services.entrade.com.vn/smart-order`
  - Demo: `https://services.entrade.com.vn/papertrade-smart-order`

---

### 4. **MQTT.rar** - Real-time Market Data

#### Mục đích:
- Nhận dữ liệu thị trường real-time qua MQTT protocol
- Subscribe vào các topic để nhận tick data

#### Chức năng (dự kiến):
- Kết nối MQTT broker
- Subscribe symbols (VN30F1M, VN30F2M, etc.)
- Nhận real-time quotes
- Stream market depth
- Real-time trade updates

#### Đặc điểm:
- ⚡ **Real-time**: Dữ liệu tick-by-tick
- 📡 **Protocol**: MQTT (lightweight messaging)
- 🔔 **Push-based**: Server push data thay vì polling

---

## 🔄 SO SÁNH CÁC API

| Tính năng | DNSE | Entrade | Entrade2 (Smart) |
|-----------|------|---------|------------------|
| **Cổ phiếu** | ✅ | ❌ | ❌ |
| **Phái sinh** | ✅ | ✅ | ✅ |
| **Demo account** | ❌ | ✅ | ✅ |
| **OTP required** | ✅ (Always) | ✅ (Real only) | ✅ (Real only) |
| **Smart orders** | ❌ | ❌ | ✅ |
| **MQTT support** | ⚠️ | ⚠️ | ⚠️ |

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

```
┌─────────────────────────────────────────┐
│         WEB APPLICATION (Flask)         │
│    - Manual Trading                     │
│    - Bot Trading                        │
│    - Strategy Builder                   │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
    ┌───▼────┐         ┌────▼────┐
    │ DNSE   │         │ Entrade │
    │ Client │         │ Client  │
    └───┬────┘         └────┬────┘
        │                   │
    ┌───▼─────────────┬────▼─────────────┐
    │  REST API       │   REST API       │
    │  + OTP Email    │   + OTP (Real)   │
    └─────────────────┴──────────────────┘
```

---

## 📝 LƯU Ý QUAN TRỌNG

### Environment Variables (.env)
Tất cả các file đều yêu cầu file `.env`:
```
usernameDNSE=0919990540
password=your_password_here
```

### Authentication Flow

**DNSE:**
```
1. authenticate() → token
2. get_otp() → Email OTP sent
3. User nhập OTP
4. get_trading_token(otp) → trading_token
5. Ready to trade
```

**Entrade (Real):**
```
1. authenticate() → token
2. get_otp() → OTP sent
3. User nhập OTP
4. get_trading_token(otp) → trading_token
5. Ready to trade
```

**Entrade (Demo):**
```
1. authenticate() → token
2. get_trading_token(None) → trading_token (no OTP)
3. Ready to trade
```

---

## 🎯 CÁCH SỬ DỤNG TRONG HỆ THỐNG

### 1. Exchange Profile Creation
Người dùng tạo profile trên trang Exchange với thông tin:
- Profile name
- Exchange (DNSE/Entrade)
- Protocol (REST API/MQTT)
- Credentials (username/password)
- Tickers quan tâm
- Timeframe mặc định
- Timezone

### 2. Connection Flow
```python
# Trong backend (app.py)
if exchange == "DNSE":
    client = DNSEClient()
    client.authenticate(username, password)
    client.get_otp()  # Send OTP
    # Frontend hiển thị modal nhập OTP
    client.get_trading_token(otp_from_user)
    
elif exchange == "ENTRADE":
    client = EntradeClient(environment="real" or "demo")
    client.authenticate(username, password)
    if environment == "real":
        client.get_otp()
        # Frontend modal OTP
        client.get_trading_token(otp_from_user)
    else:
        client.get_trading_token(None)  # Demo no OTP
```

### 3. Data Streaming
**Offline Mode**: Load CSV data đã upload
**Online Mode**: 
- REST API: Polling mỗi X giây
- MQTT: Real-time push data

---

## 🚀 TRIỂN KHAI

### Bước 1: Tạo Exchange Clients
- Tích hợp `DNSE_API.py` vào backend
- Tích hợp `EntradeAPI.py` vào backend
- Wrapper classes để thống nhất interface

### Bước 2: Connection Manager
- Quản lý multiple connections
- Auto-reconnect
- Token refresh
- Error handling

### Bước 3: Market Data Handler
- REST polling cho Offline data
- MQTT streaming cho Online data
- Data normalization
- Chart updates

### Bước 4: Trading Engine
- Order placement
- Position tracking
- PnL calculation
- Risk management

---

## 📚 TÀI LIỆU THAM KHẢO

- **DNSE API Docs**: Contact DNSE support
- **Entrade API Docs**: https://services.entrade.com.vn/docs
- **MQTT Protocol**: https://mqtt.org/
- **Python Requests**: https://docs.python-requests.org/

---

## ⚠️ SECURITY WARNINGS

1. ❌ **KHÔNG BAO GIỜ** commit credentials vào Git
2. 🔐 **BẮT BUỘC** sử dụng `.env` file với gitignore
3. 🛡️ **MÃ HÓA** trading tokens trong database
4. 🔒 **HTTPS ONLY** cho production
5. ⏰ **TOKEN EXPIRY** - Implement auto-refresh
6. 🚨 **RATE LIMITING** - Tránh spam API

---

**Tác giả**: Trading System Development Team  
**Cập nhật**: November 2025  
**Version**: 1.0
