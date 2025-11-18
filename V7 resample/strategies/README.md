# Strategy JSON Structure (V17 Format)

Cấu trúc JSON để lưu strategy theo chuẩn V17.

## Cấu trúc tổng quan

```json
{
  "name": "Tên strategy",
  "description": "Mô tả strategy",
  "indicators": [...],
  "entry_conditions": {...},
  "exit_rules": {...},
  "trading_engine": {...},
  "risk_management": {...}
}
```

## Chi tiết các phần

### 1. Indicators (Danh sách chỉ báo)

```json
"indicators": [
  {
    "id": "ema_20",           // ID duy nhất cho indicator
    "type": "EMA",            // Loại indicator: EMA, SMA, RSI, MACD, etc.
    "params": {               // Tham số của indicator
      "period": 20
    },
    "display": {              // Cài đặt hiển thị trên chart
      "show": true,
      "color": "#2962FF",
      "lineStyle": "solid",
      "lineWidth": 2
    }
  }
]
```

**Các loại indicator hỗ trợ:**
- **Trend**: EMA, SMA, WMA, DEMA, TEMA, MAuptrend, MAdowntrend, Alluptrend, Alldowntrend
- **Momentum**: RSI, MACD, Stochastic, CCI, MFI
- **Volatility**: BollingerBands, ATR, KeltnerChannel, DonchianChannel
- **Volume**: OBV, VWAP
- **Custom**: HHVsinceopen, LLVsinceopen, Baseprice, etc.

### 2. Entry Conditions (Điều kiện vào lệnh)

```json
"entry_conditions": {
  "long": [
    {
      "name": "Buy1",         // Tên signal
      "conditions": [
        {
          "left": "close",           // Toán hạng trái (close, open, high, low, indicator_id)
          "leftOffset": 0,           // Offset của toán hạng trái (0=hiện tại, -1=nến trước)
          "operator": "cross_above", // Toán tử: >, <, >=, <=, ==, !=, cross_above, cross_below
          "right": "ema_20",         // Toán hạng phải
          "rightOffset": 0,          // Offset của toán hạng phải
          "rightType": "indicator",  // Loại: "indicator" hoặc "number"
          "logic": "AND"             // Logic kết hợp: AND hoặc OR
        }
      ]
    }
  ],
  "short": [
    {
      "name": "Short1",
      "conditions": [...]
    }
  ]
}
```

**Các operator hỗ trợ:**
- `>` : Greater than
- `<` : Less than
- `>=` : Greater or equal
- `<=` : Less or equal
- `==` : Equal
- `!=` : Not equal
- `cross_above` : Cross lên trên
- `cross_below` : Cross xuống dưới
- `is_true` : Là True
- `is_false` : Là False

### 3. Exit Rules (Luật thoát lệnh)

```json
"exit_rules": {
  "long": {
    "dynamic_tp_sl": true,     // Bật/tắt TP/SL động theo profit
    "time_exit": "14:30",      // Giờ thoát lệnh cố định
    "tp_sl_table": [           // Bảng TP/SL theo từng mức profit
      {
        "profit_range": [0, 2],  // Mức profit từ 0-2 points
        "tp": 5,                 // Take Profit
        "sl": 10.3,              // Stop Loss
        "trailing": 11.9         // Trailing stop
      },
      {
        "profit_range": [2, 4],
        "tp": 8,
        "sl": 10.8,
        "trailing": 13.9
      }
    ]
  },
  "short": {
    "dynamic_tp_sl": true,
    "time_exit": "14:30",
    "tp_sl_table": [...]
  },
  "base_time": "09:00"         // Thời gian base để tính HHV/LLV
}
```

**TP/SL Table:**
- Mỗi row trong table áp dụng khi profit nằm trong `profit_range`
- `tp`: Mức Take Profit (points từ entry price)
- `sl`: Mức Stop Loss (points từ entry price)
- `trailing`: Khoảng cách trailing stop từ HHV/LLV

### 4. Trading Engine (Cấu hình engine)

```json
"trading_engine": {
  "entryAfterCandle": [1, 2],     // Vào lệnh sau 1 hoặc 2 nến
  "exitTiming": "same_candle",    // "same_candle" hoặc "after_1_candle"
  "positionMode": "long_only",    // "long_only", "short_only", "long_and_short"
  "entryPriceType": "C",          // "O", "H", "L", "C"

  "exitMethods": {                // Các phương thức thoát lệnh
    "bySignal": true,             // Thoát khi có signal ngược
    "byTP": false,                // Thoát khi chạm TP
    "bySL": false,                // Thoát khi chạm SL
    "byTrailing": false,          // Thoát khi chạm trailing stop
    "byExpiry": false             // Thoát vào ngày expiry
  },

  "profitConfig": {               // Cấu hình TP/SL cố định
    "tpBuyPoints": 10,            // TP cho Long
    "tpShortPoints": 10,          // TP cho Short
    "stopLossPoints": 20,         // SL cho Long
    "slShortPoints": 20           // SL cho Short
  },

  "trailingConfig": {
    "type": "fixed",              // "fixed" hoặc "dynamic"
    "fixedBuyPoints": 5,          // Trailing points cho Long (nếu fixed)
    "fixedShortPoints": 5,        // Trailing points cho Short (nếu fixed)
    "dynamicTiers": [             // Các mức trailing động (nếu dynamic)
      {
        "minProfit": 0,
        "maxProfit": 20,
        "trailingPercent": 30     // Trailing = 30% của profit hiện tại
      },
      {
        "minProfit": 20,
        "maxProfit": 50,
        "trailingPercent": 50
      }
    ],
    "skipLongCandle": false,      // Bỏ qua nến dài khi tính HHV/LLV
    "longCandleSize": 50          // Kích thước nến dài (H-L)
  },

  "expiryConfig": {
    "dates": ["150125", "200125"], // Ngày expiry format DDMMYY
    "time": "143000"               // Giờ expiry format HHMMSS
  }
}
```

**Entry Price Type:**
- `O`: Open price
- `H`: High price
- `L`: Low price
- `C`: Close price

**Position Mode:**
- `long_only`: Chỉ vào lệnh Long
- `short_only`: Chỉ vào lệnh Short
- `long_and_short`: Cho phép cả Long và Short (nhưng chỉ khi Flat)

**Exit Timing:**
- `same_candle`: Thoát ngay trong nến hiện tại khi điều kiện thỏa
- `after_1_candle`: Thoát ở nến tiếp theo

**Trailing Type:**
- `fixed`: Dùng points cố định (fixedBuyPoints, fixedShortPoints)
- `dynamic`: Dùng % của profit theo từng tier

### 5. Risk Management (Quản lý rủi ro)

```json
"risk_management": {
  "max_positions": 1,           // Số lệnh tối đa mở cùng lúc
  "position_size_pct": 10,      // % vốn cho mỗi lệnh
  "max_daily_loss": 50,         // Lỗ tối đa trong ngày (points)
  "trading_hours": {
    "start": "09:00",           // Giờ bắt đầu giao dịch
    "end": "14:30"              // Giờ kết thúc giao dịch
  }
}
```

## Ví dụ strategy hoàn chỉnh

Xem file `strategy_template.json` trong cùng thư mục.

## Lưu ý quan trọng

1. **Indicator ID phải unique**: Mỗi indicator cần có ID riêng (ví dụ: ema_20, rsi_14)
2. **Entry conditions logic**: Các điều kiện trong cùng 1 signal được kết hợp bằng AND/OR
3. **Exit rules**: Long và Short có exit rules riêng biệt
4. **Trailing stop**:
   - Fixed: Dùng khoảng cách cố định từ HHV/LLV
   - Dynamic: Trailing = trailingPercent% * current_profit
5. **Base time**: Thời gian bắt đầu session để tính HHV/LLV (thường là 09:00)
6. **Expiry dates**: Format DDMMYY (ví dụ: 150125 = 15/01/2025)
7. **Expiry time**: Format HHMMSS (ví dụ: 143000 = 14:30:00)

## API Endpoints

### Save Strategy
```
POST /api/save-strategy
Body: {JSON strategy object}
```

### Load Strategy
```
GET /api/load-strategy?name=Strategy_Name
```

### List Strategies
```
GET /api/list-strategies
```
