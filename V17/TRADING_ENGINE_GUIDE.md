# Trading Engine - Hướng Dẫn Chi Tiết

## 📋 Mục Lục
1. [Giới Thiệu](#giới-thiệu)
2. [Trading Rules](#trading-rules)
3. [Entry Configuration](#entry-configuration)
4. [Exit Configuration](#exit-configuration)
5. [Testing Guide](#testing-guide)
6. [Console Commands](#console-commands)
7. [Examples](#examples)

---

## 🎯 Giới Thiệu

Trading Engine là hệ thống giao dịch tự động được thiết kế để:
- Tự động mở/đóng positions dựa trên signals
- Quản lý risk với TP/SL/Trailing Stop
- Hỗ trợ cả Long và Short positions
- Kiểm soát timing entry và exit

## 📊 Trading Rules

### 1. Position States
Trading Engine có 3 trạng thái position:
- **FLAT**: Không có position nào đang mở
- **LONG**: Đang giữ position Long
- **SHORT**: Đang giữ position Short

### 2. Trading Flow
```
Signal xuất hiện → Pending Signal (delay N candles) → Execute Entry → Monitor Exit Conditions → Close Position
```

### 3. Priority Order
Khi xử lý mỗi candle, hệ thống kiểm tra theo thứ tự:
1. **Expiry Exit** (Check expiry date/time first)
2. **Profit-based Exit** (TP/SL/Trailing)
3. **Signal-based Exit** (Opposite signal)
4. **Entry Signals** (New positions)
5. **Execute Pending Entries**

**Lưu ý**: Expiry Exit có ưu tiên cao nhất vì đây là điều kiện bắt buộc theo thời gian.

---

## 🚀 Entry Configuration

### Entry Price Type
Chọn giá sử dụng khi vào lệnh:
- **O (Open)**: Giá mở cửa của candle
- **H (High)**: Giá cao nhất của candle
- **L (Low)**: Giá thấp nhất của candle
- **C (Close)**: Giá đóng cửa của candle (mặc định)

### Entry After Candle
Delay trước khi vào lệnh sau khi signal xuất hiện:
- **After 1 Candle**: Vào lệnh ngay candle tiếp theo (nhanh)
- **After 2 Candles**: Vào lệnh sau 2 candles (xác nhận)
- **Có thể chọn cả hai**: Hệ thống sẽ tạo 2 pending signals

**Ví dụ:**
```
Candle 10: BUY signal xuất hiện
- Nếu chọn "After 1": Vào lệnh tại candle 11
- Nếu chọn "After 2": Vào lệnh tại candle 12
- Nếu chọn cả hai: Vào lệnh cả candle 11 và 12
```

### Position Mode
Kiểm soát loại positions được phép mở:

#### Long Only
- Chỉ mở Long positions
- Bỏ qua SHORT signals
- Khi đang LONG: có thể đóng và mở LONG mới

#### Short Only
- Chỉ mở Short positions
- Bỏ qua BUY signals
- Khi đang SHORT: có thể đóng và mở SHORT mới

#### Long and Short
- Có thể mở cả Long và Short
- **Điều kiện**: Chỉ mở position mới khi đang FLAT
- Không mở position mới khi đang giữ position khác

---

## 🚪 Exit Configuration

### Exit Methods

Có thể chọn nhiều exit methods cùng lúc:

#### 1. Exit by Opposite Signal (🔄)
- **Long**: Đóng khi SHORT signal xuất hiện
- **Short**: Đóng khi BUY signal xuất hiện
- **Lưu ý**: Khi chọn này, bắt buộc phải "Exit After 1 Candle"

#### 2. Exit by Take Profit (✅)
- **Long**: Đóng khi High chạm `Entry Price + TP Points`
- **Short**: Đóng khi Low chạm `Entry Price - TP Points`

**Ví dụ Long:**
```
Entry Price: 100
TP Points: 10
→ Đóng lệnh khi High ≥ 110
```

#### 3. Exit by Stop Loss (🛑)
- **Long**: Đóng khi Low chạm `Entry Price - SL Points`
- **Short**: Đóng khi High chạm `Entry Price + SL Points`

**Ví dụ Long:**
```
Entry Price: 100
SL Points: 20
→ Đóng lệnh khi Low ≤ 80
```

#### 4. Exit by Trailing Stop (📉)
- **Long**: Đóng khi Low chạm `HHV (Highest High since Entry) - Trailing Points`
- **Short**: Đóng khi High chạm `LLV (Lowest Low since Entry) + Trailing Points`

**Ví dụ Long:**
```
Entry Price: 100
Candle 1: High = 105 → HHV = 105
Candle 2: High = 110 → HHV = 110
Candle 3: High = 108 (không update HHV)
Trailing Points: 5
→ Đóng lệnh khi Low ≤ 110 - 5 = 105
```

#### 5. Exit by Expiry Day (📅)
- **Cả Long và Short**: Đóng tất cả positions vào ngày/giờ đáo hạn
- **Format ngày**: DDMMYY (ví dụ: 150125 = 15/01/2025)
- **Format giờ**: HHMMSS (ví dụ: 143000 = 14:30:00)
- Có thể cấu hình nhiều ngày đáo hạn (cách nhau bởi dấu phẩy)

**Ví dụ:**
```
Expiry Dates: 150125,200125,250125
Expiry Time: 143000
→ Đóng tất cả positions vào:
  - 15/01/2025 lúc 14:30:00
  - 20/01/2025 lúc 14:30:00
  - 25/01/2025 lúc 14:30:00
```

**Cách hoạt động:**
- Hệ thống kiểm tra mỗi candle
- Nếu ngày của candle trùng với ngày đáo hạn
- Và thời gian của candle >= thời gian đáo hạn
- → Đóng tất cả positions đang mở

### Trailing Stop Advanced Options (⚙️)

#### Skip Long Candle for HHV/LLV Update

Tính năng này giúp **giảm repaint** khi có nến dài xuất hiện:

**Vấn đề của Trailing Stop thông thường:**
- HHV/LLV được update liên tục khi có candle mới
- Khi có nến dài (big candle), HHV/LLV thay đổi đột ngột
- Trailing line repaint → tín hiệu không ổn định

**Giải pháp:**
1. **Skip Long Candle**: Không update HHV/LLV khi gặp nến dài
2. **Use Previous HHV/LLV**: Tính trailing line dựa trên giá trị của nến trước (n-1)

**Cấu hình:**
- **Checkbox**: "Skip Long Candle for HHV/LLV Update"
- **Long Candle Size**: Độ dài nến (H - L) để xác định "nến dài"
  - Ví dụ: 50 → nến có (H - L) >= 50 points sẽ bị skip

**Công thức:**
```
Trailing Stop thông thường:
- Trailing Line (LONG) = HHV[n] - Trailing Points
- HHV[n] = HHV của candle hiện tại (có thể repaint)

Trailing Stop No-Repaint:
- Trailing Line (LONG) = HHV[n-1] - Trailing Points
- HHV[n-1] = HHV của candle trước đó (không repaint)
- Nếu candle hiện tại là "long candle" → không update HHV
```

**Ví dụ Long Position:**
```
Entry: 100
Trailing Points: 5
Long Candle Size: 50

Candle 1: H=105, L=101 (size=4) → Update HHV=105, HHV[n-1]=100
  Trailing Line = HHV[n-1] - 5 = 100 - 5 = 95

Candle 2: H=110, L=106 (size=4) → Update HHV=110, HHV[n-1]=105
  Trailing Line = HHV[n-1] - 5 = 105 - 5 = 100

Candle 3: H=160, L=108 (size=52, long candle!) → SKIP update HHV
  HHV vẫn = 110 (không update)
  HHV[n-1] = 110
  Trailing Line = 110 - 5 = 105

Candle 4: H=112, L=109 (size=3) → Update HHV=112, HHV[n-1]=110
  Trailing Line = 110 - 5 = 105
```

**Lợi ích:**
- Giảm repaint khi có nến dài
- Trailing line ổn định hơn
- Tín hiệu exit đáng tin cậy hơn

### Trailing Type: Fixed vs Dynamic (💎)

Trading Engine hỗ trợ 2 loại trailing stop:

#### Fixed Trailing Stop (📊)
Trailing stop cố định theo số điểm:
- **Long**: Trailing Line = HHV[n-1] - Fixed Points
- **Short**: Trailing Line = LLV[n-1] + Fixed Points
- Đơn giản, dễ hiểu, phù hợp cho mọi market

#### Dynamic Tiered Trailing Stop (💎)
Trailing stop thích ứng theo % lợi nhuận đạt được:
- **Ý tưởng**: Càng profit cao → càng giữ lợi nhuận chặt chẽ hơn
- **Tier-based**: Chia profit thành các tiers, mỗi tier có % trailing khác nhau
- **Tự động điều chỉnh**: Trailing tightens khi profit tăng

**Config Structure:**
```javascript
trailingConfig: {
    type: 'fixed',  // hoặc 'dynamic'

    // Fixed mode
    fixedBuyPoints: 5,
    fixedShortPoints: 5,

    // Dynamic mode
    dynamicTiers: [
        { minProfit: 0,  maxProfit: 20,  trailingPercent: 30 },  // Tier 1
        { minProfit: 20, maxProfit: 50,  trailingPercent: 50 },  // Tier 2
        { minProfit: 50, maxProfit: 9999, trailingPercent: 70 }  // Tier 3
    ]
}
```

**Công thức Dynamic Trailing:**

Cho LONG position:
```
1. Tính Max Profit = HHV[n-1] - Entry Price
2. Tìm tier phù hợp dựa trên Max Profit
3. Trailing Points = Max Profit × (Tier Percent / 100)
4. Trailing Line = Entry + (Max Profit - Trailing Points)
```

Cho SHORT position:
```
1. Tính Max Profit = Entry Price - LLV[n-1]
2. Tìm tier phù hợp dựa trên Max Profit
3. Trailing Points = Max Profit × (Tier Percent / 100)
4. Trailing Line = Entry - (Max Profit - Trailing Points)
```

**Ví dụ Dynamic Trailing (LONG):**

Config: 3 tiers như trên
```
Entry = 100
HHV[n-1] = 125
Max Profit = 125 - 100 = 25 points

→ 25 points thuộc Tier 2 (20-50: 50%)
→ Trailing Points = 25 × 50% = 12.5 points
→ Trailing Line = 100 + (25 - 12.5) = 112.5

Exit khi Low ≤ 112.5
```

**So sánh Fixed vs Dynamic:**
```
Entry = 100
HHV[n-1] = 125 (Max Profit = 25)

Fixed (5 points):
  Trailing Line = 125 - 5 = 120
  → Exit khi Low ≤ 120
  → Giữ được 20 points profit

Dynamic (Tier 2: 50%):
  Trailing Line = 100 + (25 - 12.5) = 112.5
  → Exit khi Low ≤ 112.5
  → Giữ được 12.5 points profit
  → Thoát sớm hơn, an toàn hơn khi profit cao
```

**Khi nào profit thấp:**
```
Entry = 100
HHV[n-1] = 110 (Max Profit = 10)

Fixed (5 points):
  Trailing Line = 110 - 5 = 105
  → Exit khi Low ≤ 105
  → Giữ được 5 points profit

Dynamic (Tier 1: 30%):
  Trailing Line = 100 + (10 - 3) = 107
  → Exit khi Low ≤ 107
  → Giữ được 7 points profit
  → Trailing lỏng hơn, cho phép price breathe
```

**Lợi ích Dynamic Trailing:**
- **Adaptive**: Tự động điều chỉnh theo profit level
- **Risk Management**: Bảo vệ profit tốt hơn khi profit cao
- **Flexibility**: Cho phép price di chuyển tự do hơn khi profit thấp
- **Optimizable**: Có thể optimize các tier parameters

**Lưu ý:**
- Skip Long Candle áp dụng cho cả Fixed và Dynamic
- Luôn dùng HHV[n-1]/LLV[n-1] để tránh repaint
- Console log hiển thị tier info cho Dynamic mode
- Tier cuối cùng nên có maxProfit = 9999 (infinity)

### Exit Timing

#### Exit in Same Candle
- Đóng lệnh ngay trong candle mà exit condition được triggered
- Dùng cho TP/SL/Trailing
- **Không khả dụng** khi chọn "Exit by Opposite Signal"

#### Exit After 1 Candle
- Đóng lệnh ở candle tiếp theo
- **Bắt buộc** khi chọn "Exit by Opposite Signal"

### Exit Points Configuration

Các points được cấu hình ở **Exit tab**:

#### Long Position Exit Points
- **Take Profit (points)**: Khoảng cách từ entry đến TP
- **Stop Loss (points)**: Khoảng cách từ entry đến SL (chung cho cả Long/Short)
- **Trailing Stop (points)**: Khoảng cách từ HHV đến trailing line

#### Short Position Exit Points
- **Take Profit (points)**: Khoảng cách từ entry đến TP
- **Trailing Stop (points)**: Khoảng cách từ LLV đến trailing line
- **Stop Loss**: Sử dụng chung với Long (cấu hình ở Long tab)

---

## 🧪 Testing Guide

### Bước 1: Kiểm Tra Configuration

Mở Console (F12) và chạy:

```javascript
// Xem toàn bộ config hiện tại
tradingEngine.config

// Xem từng phần cụ thể
tradingEngine.config.entryAfterCandle  // [1] hoặc [1, 2]
tradingEngine.config.exitTiming        // 'same_candle' hoặc 'after_1_candle'
tradingEngine.config.positionMode      // 'long_only', 'short_only', 'long_and_short'
tradingEngine.config.exitMethods       // {bySignal, byTP, bySL, byTrailing, byExpiry}
tradingEngine.config.profitConfig      // {tpBuyPoints, tpShortPoints, ...}
tradingEngine.config.expiryConfig      // {dates: [Date objects], time: 'HHMMSS'}
```

### Bước 2: Kiểm Tra Position State

```javascript
// Xem trạng thái position hiện tại
tradingEngine.positions

// Các field quan trọng:
tradingEngine.positions.currentStatus    // 'FLAT', 'LONG', 'SHORT'
tradingEngine.positions.long            // Số lượng LONG positions
tradingEngine.positions.short           // Số lượng SHORT positions
tradingEngine.positions.entryPrice      // Giá vào lệnh
tradingEngine.positions.hhvSinceEntry   // Highest High since entry
tradingEngine.positions.llvSinceEntry   // Lowest Low since entry
```

### Bước 3: Test Entry Signals

```javascript
// Giả lập BUY signal tại candle index 10
processSignal('BUY', 10)

// Kiểm tra pending signals
tradingEngine.pendingSignals

// Giả lập candle data để execute pending signal
const candleData = {
    open: 100,
    high: 102,
    low: 99,
    close: 101,
    time: '10:30'
}

// Execute pending signals tại candle 11 (nếu entry after 1 candle)
executePendingSignals(11, candleData)

// Kiểm tra position đã mở chưa
tradingEngine.positions.currentStatus  // Nên là 'LONG'
```

### Bước 4: Test Exit Conditions

#### Test TP Exit
```javascript
// Giả sử đang LONG với Entry = 100, TP = 10
const candleWithTP = {
    open: 105,
    high: 110,  // Chạm TP line (100 + 10)
    low: 104,
    close: 109
}

checkProfitExit(candleWithTP, 15)

// Kiểm tra position đã đóng chưa
tradingEngine.positions.currentStatus  // Nên là 'FLAT'
```

#### Test SL Exit
```javascript
// Giả sử đang LONG với Entry = 100, SL = 20
const candleWithSL = {
    open: 85,
    high: 87,
    low: 80,  // Chạm SL line (100 - 20)
    close: 82
}

checkProfitExit(candleWithSL, 20)

// Kiểm tra position đã đóng chưa
tradingEngine.positions.currentStatus  // Nên là 'FLAT'
```

#### Test Trailing Exit
```javascript
// Giả sử đang LONG với Entry = 100, Trailing = 5
// HHV = 110 (từ candles trước)

const candleWithTrailing = {
    open: 107,
    high: 108,
    low: 105,  // Chạm Trailing line (110 - 5)
    close: 106
}

checkProfitExit(candleWithTrailing, 25)

// Kiểm tra position đã đóng chưa
tradingEngine.positions.currentStatus  // Nên là 'FLAT'
```

#### Test Signal Exit
```javascript
// Giả sử đang LONG
processSignal('BUY', 10)
executePendingSignals(11, {...})  // Mở LONG

// Xuất hiện SHORT signal
checkSignalExit('SHORT', 30)

// Kiểm tra position đã đóng chưa
tradingEngine.positions.currentStatus  // Nên là 'FLAT'
```

#### Test Expiry Exit
```javascript
// Bước 1: Cấu hình expiry exit
tradingEngine.config.exitMethods.byExpiry = true
tradingEngine.config.expiryConfig.dates = [new Date(2025, 0, 15)]  // 15/01/2025
tradingEngine.config.expiryConfig.time = '143000'  // 14:30:00

// Bước 2: Mở position
openPosition('LONG', 100, '10:00')

// Bước 3: Test candle trước thời gian đáo hạn (chưa đóng)
const candleBeforeExpiry = {
    open: 105,
    high: 107,
    low: 104,
    close: 106,
    time: new Date(2025, 0, 15, 14, 0, 0),  // 15/01/2025 14:00:00 (trước 14:30)
    date: new Date(2025, 0, 15)
}

checkExpiryExit(candleBeforeExpiry, 20)
tradingEngine.positions.currentStatus  // Vẫn 'LONG' (chưa đến giờ đáo hạn)

// Bước 4: Test candle đúng thời gian đáo hạn (đóng)
const candleAtExpiry = {
    open: 106,
    high: 108,
    low: 105,
    close: 107,
    time: new Date(2025, 0, 15, 14, 30, 0),  // 15/01/2025 14:30:00
    date: new Date(2025, 0, 15)
}

checkExpiryExit(candleAtExpiry, 21)
tradingEngine.positions.currentStatus  // Nên là 'FLAT' (đã đóng vì đến giờ đáo hạn)

// Bước 5: Test với nhiều ngày đáo hạn
tradingEngine.config.expiryConfig.dates = [
    new Date(2025, 0, 15),  // 15/01/2025
    new Date(2025, 0, 20),  // 20/01/2025
    new Date(2025, 0, 25)   // 25/01/2025
]

// Position sẽ đóng vào bất kỳ ngày nào trong danh sách
```

**Lưu ý khi test Expiry Exit:**
- Candle phải có thuộc tính `date` (Date object) hoặc `time` (timestamp/date string)
- Thời gian được so sánh theo format HHMMSS (số nguyên)
- Nếu ngày trùng nhưng thời gian < expiry time → không đóng
- Có thể test với nhiều ngày đáo hạn khác nhau

#### Test Trailing Stop with Skip Long Candle

```javascript
// Bước 1: Cấu hình
tradingEngine.config.exitMethods.byTrailing = true
tradingEngine.config.profitConfig.trailingBuyPoints = 5
tradingEngine.config.trailingAdvanced.skipLongCandleForTrailing = true
tradingEngine.config.trailingAdvanced.longCandleSize = 50

// Bước 2: Mở LONG position
openPosition('LONG', 100, '10:00')
console.log('HHV:', tradingEngine.positions.hhvSinceEntry)  // 100
console.log('HHV[n-1]:', tradingEngine.positions.hhvPrevious)  // 100

// Bước 3: Candle thông thường (update HHV)
const candle1 = {open: 101, high: 105, low: 101, close: 104}
checkProfitExit(candle1, 1)
console.log('HHV:', tradingEngine.positions.hhvSinceEntry)  // 105
console.log('HHV[n-1]:', tradingEngine.positions.hhvPrevious)  // 100
// Trailing Line = 100 - 5 = 95 (dùng HHV[n-1])

// Bước 4: Candle thông thường (update HHV)
const candle2 = {open: 105, high: 110, low: 105, close: 108}
checkProfitExit(candle2, 2)
console.log('HHV:', tradingEngine.positions.hhvSinceEntry)  // 110
console.log('HHV[n-1]:', tradingEngine.positions.hhvPrevious)  // 105
// Trailing Line = 105 - 5 = 100

// Bước 5: Long candle (KHÔNG update HHV)
const candle3 = {open: 108, high: 160, low: 108, close: 155}
// Candle size = 160 - 108 = 52 >= 50 (long candle!)
checkProfitExit(candle3, 3)
console.log('HHV:', tradingEngine.positions.hhvSinceEntry)  // 110 (không đổi)
console.log('HHV[n-1]:', tradingEngine.positions.hhvPrevious)  // 110
// Console: "📏 Skipped HHV update - Long candle detected (size: 52.00)"
// Trailing Line = 110 - 5 = 105

// Bước 6: Candle trigger trailing
const candle4 = {open: 112, high: 112, low: 104, close: 106}
checkProfitExit(candle4, 4)
// Low = 104 <= Trailing Line (105)
tradingEngine.positions.currentStatus  // Nên là 'FLAT'
// Console: "📉 LONG closed by Trailing at 105 (HHV[n-1]: 110)"
```

**Test không có Skip Long Candle:**
```javascript
// Cấu hình: TẮT skip long candle
tradingEngine.config.trailingAdvanced.skipLongCandleForTrailing = false

openPosition('LONG', 100, '10:00')

const candle1 = {open: 101, high: 105, low: 101, close: 104}
checkProfitExit(candle1, 1)  // HHV = 105

// Long candle VẪN update HHV (vì tắt skip)
const candle2 = {open: 105, high: 160, low: 105, close: 155}
checkProfitExit(candle2, 2)
console.log('HHV:', tradingEngine.positions.hhvSinceEntry)  // 160 (đã update!)
console.log('HHV[n-1]:', tradingEngine.positions.hhvPrevious)  // 105

// Trailing Line = 105 - 5 = 100 (dùng HHV[n-1])
// Nếu dùng HHV[n], Trailing Line = 160 - 5 = 155 (repaint!)
```

#### Test Dynamic Tiered Trailing

```javascript
// Bước 1: Cấu hình Dynamic Trailing
tradingEngine.config.exitMethods.byTrailing = true
tradingEngine.config.trailingConfig.type = 'dynamic'
tradingEngine.config.trailingConfig.dynamicTiers = [
    { minProfit: 0,  maxProfit: 20,  trailingPercent: 30 },  // Tier 1: 30%
    { minProfit: 20, maxProfit: 50,  trailingPercent: 50 },  // Tier 2: 50%
    { minProfit: 50, maxProfit: 9999, trailingPercent: 70 }  // Tier 3: 70%
]

// Bước 2: Mở LONG position
openPosition('LONG', 100, '10:00')

// Bước 3: Profit thấp (Tier 1)
const candle1 = {open: 101, high: 105, low: 101, close: 104}
checkProfitExit(candle1, 1)
// HHV = 105, HHV[n-1] = 100
// Max Profit = 100 - 100 = 0 → Tier 1 (30%)
// Trailing Points = 0 × 30% = 0
// Trailing Line = 100 + (0 - 0) = 100

const candle2 = {open: 105, high: 110, low: 105, close: 108}
checkProfitExit(candle2, 2)
// HHV = 110, HHV[n-1] = 105
// Max Profit = 105 - 100 = 5 → Tier 1 (30%)
// Trailing Points = 5 × 30% = 1.5
// Trailing Line = 100 + (5 - 1.5) = 103.5
console.log('Console: "📉 Profit: 5.00, Tier: 30%"')

// Bước 4: Profit trung bình (Tier 2)
const candle3 = {open: 110, high: 125, low: 109, close: 123}
checkProfitExit(candle3, 3)
// HHV = 125, HHV[n-1] = 110
// Max Profit = 110 - 100 = 10 → Tier 1 (30%)
// Trailing Points = 10 × 30% = 3
// Trailing Line = 100 + (10 - 3) = 107

const candle4 = {open: 124, high: 130, low: 123, close: 128}
checkProfitExit(candle4, 4)
// HHV = 130, HHV[n-1] = 125
// Max Profit = 125 - 100 = 25 → Tier 2 (50%)
// Trailing Points = 25 × 50% = 12.5
// Trailing Line = 100 + (25 - 12.5) = 112.5
console.log('Console: "📉 Profit: 25.00, Tier: 50%"')

// Bước 5: Profit cao (Tier 3)
const candle5 = {open: 129, high: 155, low: 128, close: 152}
checkProfitExit(candle5, 5)
// HHV = 155, HHV[n-1] = 130
// Max Profit = 130 - 100 = 30 → Tier 2 (50%)
// Trailing Points = 30 × 50% = 15
// Trailing Line = 100 + (30 - 15) = 115

const candle6 = {open: 153, high: 160, low: 152, close: 158}
checkProfitExit(candle6, 6)
// HHV = 160, HHV[n-1] = 155
// Max Profit = 155 - 100 = 55 → Tier 3 (70%)
// Trailing Points = 55 × 70% = 38.5
// Trailing Line = 100 + (55 - 38.5) = 116.5
console.log('Console: "📉 Profit: 55.00, Tier: 70%"')

// Bước 6: Trigger exit (Low chạm trailing line)
const candle7 = {open: 157, high: 159, low: 115, close: 118}
checkProfitExit(candle7, 7)
// Low = 115 <= Trailing Line (116.5)
tradingEngine.positions.currentStatus  // Nên là 'FLAT'
console.log('Console: "📉 LONG closed by Trailing at 116.5 (Profit: 60.00, Tier: 70%)"')
```

**So sánh với Fixed Trailing:**
```javascript
// Nếu dùng Fixed Trailing với fixedBuyPoints = 5
// Candle 6: HHV[n-1] = 155
// Trailing Line = 155 - 5 = 150
// → Exit khi Low ≤ 150 (giữ được ~50 points)

// Với Dynamic Tier 3 (70%):
// Max Profit = 55
// Trailing Points = 55 × 70% = 38.5
// Trailing Line = 100 + (55 - 38.5) = 116.5
// → Exit khi Low ≤ 116.5 (giữ được ~16.5 points)
// → Bảo vệ profit chặt chẽ hơn khi profit cao
```

**Test Dynamic Trailing với SHORT:**
```javascript
// Cấu hình: Same tiers
openPosition('SHORT', 200, '11:00')

const candleS1 = {open: 199, high: 199, low: 195, close: 196}
checkProfitExit(candleS1, 10)
// LLV = 195, LLV[n-1] = 200
// Max Profit = 200 - 200 = 0 → Tier 1 (30%)
// Trailing Line = 200 - (0 - 0) = 200

const candleS2 = {open: 196, high: 196, low: 175, close: 178}
checkProfitExit(candleS2, 11)
// LLV = 175, LLV[n-1] = 195
// Max Profit = 200 - 195 = 5 → Tier 1 (30%)
// Trailing Points = 5 × 30% = 1.5
// Trailing Line = 200 - (5 - 1.5) = 196.5

const candleS3 = {open: 179, high: 179, low: 170, close: 172}
checkProfitExit(candleS3, 12)
// LLV = 170, LLV[n-1] = 175
// Max Profit = 200 - 175 = 25 → Tier 2 (50%)
// Trailing Points = 25 × 50% = 12.5
// Trailing Line = 200 - (25 - 12.5) = 187.5
console.log('Console: "📈 Profit: 25.00, Tier: 50%"')

// Exit khi High ≥ 187.5
const candleS4 = {open: 175, high: 188, low: 174, close: 186}
checkProfitExit(candleS4, 13)
tradingEngine.positions.currentStatus  // Nên là 'FLAT'
console.log('Console: "📈 SHORT closed by Trailing at 187.5 (Profit: 30.00, Tier: 50%)"')
```

### Bước 5: Test Full Workflow

```javascript
// Reset hệ thống
resetEngineState()

// 1. BUY Signal tại candle 5
processSignal('BUY', 5)
console.log('Pending Signals:', tradingEngine.pendingSignals)

// 2. Execute entry tại candle 6 (after 1 candle)
const entryCandle = {
    open: 100,
    high: 101,
    low: 99,
    close: 100.5,
    time: '09:30'
}
executePendingSignals(6, entryCandle)
console.log('Position Status:', tradingEngine.positions.currentStatus)  // 'LONG'
console.log('Entry Price:', tradingEngine.positions.entryPrice)  // 100.5

// 3. Candle thường (không trigger exit)
const normalCandle = {
    open: 101,
    high: 103,
    low: 100,
    close: 102
}
checkProfitExit(normalCandle, 7)
console.log('Position Status:', tradingEngine.positions.currentStatus)  // Vẫn 'LONG'

// 4. Candle trigger TP (Entry = 100.5, TP = 10)
const tpCandle = {
    open: 109,
    high: 111,  // Chạm 110.5
    low: 108,
    close: 110
}
checkProfitExit(tpCandle, 8)
console.log('Position Status:', tradingEngine.positions.currentStatus)  // 'FLAT'
```

---

## 💻 Console Commands

### Kiểm Tra State

```javascript
// Xem toàn bộ state
getEngineState()

// Reset hệ thống
resetEngineState()

// Xem signal history
tradingEngine.signalHistory
```

### Thao Tác Thủ Công

```javascript
// Mở position thủ công
openPosition('LONG', 100, '10:30')
openPosition('SHORT', 200, '11:00')

// Đóng position thủ công
closePosition('LONG')
closePosition('SHORT')

// Xem có mở được position không
canOpenPosition('LONG')   // true/false
canOpenPosition('SHORT')  // true/false
```

### Debug

```javascript
// Bật log chi tiết trong code
// Tất cả functions đã có console.log

// Ví dụ: Trace một candle
const candle = {open: 100, high: 105, low: 99, close: 102}

console.log('=== Processing Candle 10 ===')
checkProfitExit(candle, 10)
checkSignalExit('SHORT', 10)
processSignal('BUY', 10)
executePendingSignals(10, candle)
console.log('=== Done ===')
```

### Trailing Config Commands

```javascript
// Xem config trailing hiện tại
tradingEngine.config.trailingConfig

// Chuyển sang Fixed Trailing
tradingEngine.config.trailingConfig.type = 'fixed'
tradingEngine.config.trailingConfig.fixedBuyPoints = 5
tradingEngine.config.trailingConfig.fixedShortPoints = 5

// Chuyển sang Dynamic Trailing
tradingEngine.config.trailingConfig.type = 'dynamic'
tradingEngine.config.trailingConfig.dynamicTiers = [
    { minProfit: 0,  maxProfit: 20,  trailingPercent: 30 },
    { minProfit: 20, maxProfit: 50,  trailingPercent: 50 },
    { minProfit: 50, maxProfit: 9999, trailingPercent: 70 }
]

// Bật/tắt Skip Long Candle (áp dụng cho cả Fixed và Dynamic)
tradingEngine.config.trailingConfig.skipLongCandle = true
tradingEngine.config.trailingConfig.longCandleSize = 50

// Test Dynamic Trailing calculation
const result = calculateDynamicTrailing(
    100,      // Entry price
    125,      // HHV[n-1]
    tradingEngine.config.trailingConfig.dynamicTiers,
    'LONG'
)
console.log(result)
// Output: {
//   trailingLine: 112.5,
//   trailingPoints: 12.5,
//   maxProfit: 25,
//   tier: { minProfit: 20, maxProfit: 50, trailingPercent: 50 }
// }

// So sánh Fixed vs Dynamic
const entry = 100
const hhv = 125

// Fixed
const fixedLine = hhv - 5  // 120
console.log('Fixed Trailing Line:', fixedLine)

// Dynamic
const dynamicResult = calculateDynamicTrailing(entry, hhv, [
    { minProfit: 0,  maxProfit: 20,  trailingPercent: 30 },
    { minProfit: 20, maxProfit: 50,  trailingPercent: 50 },
    { minProfit: 50, maxProfit: 9999, trailingPercent: 70 }
], 'LONG')
console.log('Dynamic Trailing Line:', dynamicResult.trailingLine)  // 112.5
console.log('Tier used:', dynamicResult.tier.trailingPercent + '%')  // 50%
```

---

## 📝 Examples

### Example 1: Long Only với TP/SL

**Configuration:**
```
Entry Price Type: Close (C)
Entry After Candle: [1]
Position Mode: Long Only
Exit Methods: ✅ TP, ✅ SL
Exit Timing: Same Candle
TP Points: 15
SL Points: 10
```

**Scenario:**
```javascript
// Candle 5: BUY signal
processSignal('BUY', 5)

// Candle 6: Execute entry at Close = 100
executePendingSignals(6, {open: 99, high: 101, low: 98, close: 100})
// → Mở LONG tại 100

// Candle 7-10: Price di chuyển bình thường
// High max = 110, Low min = 95

// Candle 11: High chạm TP (115)
checkProfitExit({open: 112, high: 115, low: 111, close: 114}, 11)
// → Đóng LONG tại TP line (115)
// Console: "✅ LONG closed by TP at 115 (Entry: 100)"
```

### Example 2: Long and Short với Signal Exit

**Configuration:**
```
Entry Price Type: Close (C)
Entry After Candle: [1]
Position Mode: Long and Short
Exit Methods: ✅ Exit by Opposite Signal
Exit Timing: After 1 Candle (bắt buộc)
```

**Scenario:**
```javascript
// Candle 5: BUY signal
processSignal('BUY', 5)

// Candle 6: Execute LONG
executePendingSignals(6, {open: 100, high: 101, low: 99, close: 100})
// → Status: LONG

// Candle 10: SHORT signal
checkSignalExit('SHORT', 10)
// → Đóng LONG
// Console: "🔄 LONG closed by opposite SHORT signal at candle 10"

// Vì mode là Long and Short, nhưng signal exit đóng LONG
// Nên SHORT signal không được execute (vì không FLAT)
processSignal('SHORT', 10)  // Sẽ tạo pending signal
executePendingSignals(11, {...})  // Có thể mở SHORT vì đã FLAT
```

### Example 3: Trailing Stop

**Configuration:**
```
Entry Price Type: Close (C)
Entry After Candle: [1]
Position Mode: Long Only
Exit Methods: ✅ Trailing Stop
Exit Timing: Same Candle
Trailing Points: 5
```

**Scenario:**
```javascript
// Entry tại 100
openPosition('LONG', 100, '10:00')

// Candle 1: High = 105
checkProfitExit({open: 101, high: 105, low: 100, close: 103}, 1)
// HHV = 105, Trailing line = 105 - 5 = 100

// Candle 2: High = 110
checkProfitExit({open: 104, high: 110, low: 103, close: 108}, 2)
// HHV = 110, Trailing line = 110 - 5 = 105

// Candle 3: Low = 104 (không chạm trailing line)
checkProfitExit({open: 107, high: 109, low: 104, close: 106}, 3)
// Vẫn giữ LONG

// Candle 4: Low = 104 (chạm trailing line 105)
checkProfitExit({open: 106, high: 107, low: 104, close: 105}, 4)
// → Đóng LONG
// Console: "📉 LONG closed by Trailing at 105 (HHV: 110)"
```

### Example 4: Dynamic Tiered Trailing Stop

**Configuration:**
```
Entry Price Type: Close (C)
Entry After Candle: [1]
Position Mode: Long Only
Exit Methods: ✅ Trailing Stop
Exit Timing: Same Candle
Trailing Type: Dynamic
Dynamic Tiers:
  - Tier 1: 0-20 points → 30% trailing
  - Tier 2: 20-50 points → 50% trailing
  - Tier 3: 50+ points → 70% trailing
```

**Scenario:**
```javascript
// Entry tại 100
openPosition('LONG', 100, '10:00')

// Candle 1: Profit = 5 (Tier 1: 30%)
checkProfitExit({open: 101, high: 105, low: 100, close: 103}, 1)
// HHV[n-1] = 100, Max Profit = 0
// Trailing Line = 100 + (0 - 0) = 100
// Console: "📉 Profit: 0.00, Tier: 30%"

// Candle 2: Profit = 10 (Tier 1: 30%)
checkProfitExit({open: 104, high: 110, low: 103, close: 108}, 2)
// HHV[n-1] = 105, Max Profit = 5
// Trailing Points = 5 × 30% = 1.5
// Trailing Line = 100 + (5 - 1.5) = 103.5
// Console: "📉 Profit: 5.00, Tier: 30%"

// Candle 3: Profit = 25 (Tier 2: 50%)
checkProfitExit({open: 109, high: 125, low: 108, close: 123}, 3)
// HHV[n-1] = 110, Max Profit = 10
// Trailing Points = 10 × 30% = 3
// Trailing Line = 100 + (10 - 3) = 107
// Console: "📉 Profit: 10.00, Tier: 30%"

// Candle 4: Profit lên Tier 2
checkProfitExit({open: 124, high: 130, low: 123, close: 128}, 4)
// HHV[n-1] = 125, Max Profit = 25
// Trailing Points = 25 × 50% = 12.5
// Trailing Line = 100 + (25 - 12.5) = 112.5
// Console: "📉 Profit: 25.00, Tier: 50%"
// → Trailing chặt hơn khi profit tăng

// Candle 5: Profit lên Tier 3 (70%)
checkProfitExit({open: 129, high: 155, low: 128, close: 152}, 5)
// HHV[n-1] = 130, Max Profit = 30
// Trailing Points = 30 × 50% = 15
// Trailing Line = 100 + (30 - 15) = 115
// Console: "📉 Profit: 30.00, Tier: 50%"

// Candle 6: Profit = 55 (Tier 3)
checkProfitExit({open: 153, high: 160, low: 152, close: 158}, 6)
// HHV[n-1] = 155, Max Profit = 55
// Trailing Points = 55 × 70% = 38.5
// Trailing Line = 100 + (55 - 38.5) = 116.5
// Console: "📉 Profit: 55.00, Tier: 70%"
// → Trailing rất chặt để bảo vệ profit cao

// Candle 7: Price giảm, trigger trailing
checkProfitExit({open: 157, high: 159, low: 115, close: 118}, 7)
// Low = 115 <= Trailing Line (116.5)
// → Đóng LONG, giữ được ~16.5 points profit
// Console: "📉 LONG closed by Trailing at 116.5 (Profit: 60.00, Tier: 70%)"
```

**So sánh Fixed vs Dynamic:**
```
Cùng tình huống trên, nếu dùng Fixed Trailing = 5 points:

Candle 6: HHV[n-1] = 155
  Fixed Trailing Line = 155 - 5 = 150
  → Exit khi Low ≤ 150
  → Giữ được ~50 points profit (nhiều hơn!)

Dynamic Trailing Line = 116.5
  → Exit khi Low ≤ 116.5
  → Giữ được ~16.5 points profit (ít hơn!)

Tại sao lại dùng Dynamic?
- Bảo vệ profit chặt chẽ hơn khi profit cao
- Giảm risk khi market đảo chiều
- Trade-off: Thoát sớm hơn nhưng an toàn hơn
- Phù hợp cho trader ưu tiên bảo toàn profit
```

### Example 5: Multiple Entry Delays

**Configuration:**
```
Entry After Candle: [1, 2] (chọn cả hai)
Position Mode: Long Only
```

**Scenario:**
```javascript
// Candle 10: BUY signal
processSignal('BUY', 10)

// Tạo 2 pending signals:
// - Signal 1: entry tại candle 11
// - Signal 2: entry tại candle 12

// Candle 11: Execute signal 1
executePendingSignals(11, {open: 100, high: 101, low: 99, close: 100})
// → Mở LONG tại 100

// Candle 12: Signal 2 bị reject
executePendingSignals(12, {open: 101, high: 102, low: 100, close: 101})
// → Không mở LONG mới (đã có LONG rồi, mode = long_only)
// Console: "❌ Cannot open LONG - position not FLAT"
```

### Example 5: Expiry Day Exit

**Configuration:**
```
Entry Price Type: Close (C)
Entry After Candle: [1]
Position Mode: Long and Short
Exit Methods: ✅ Exit by Expiry Day
Expiry Dates: 150125,200125  (15/01/2025, 20/01/2025)
Expiry Time: 143000  (14:30:00)
```

**Scenario:**
```javascript
// Ngày 10/01/2025 09:00 - BUY signal
processSignal('BUY', 5)

// Ngày 10/01/2025 09:30 - Execute LONG tại 100
executePendingSignals(6, {
    open: 99,
    high: 101,
    low: 98,
    close: 100,
    time: new Date(2025, 0, 10, 9, 30, 0),
    date: new Date(2025, 0, 10)
})
// → Status: LONG

// Ngày 12/01/2025 - Candles bình thường (không phải ngày đáo hạn)
checkExpiryExit({...candle, date: new Date(2025, 0, 12)}, 20)
// → Vẫn giữ LONG (chưa đến ngày đáo hạn)

// Ngày 15/01/2025 14:00 - Trước giờ đáo hạn
checkExpiryExit({
    open: 105, high: 107, low: 104, close: 106,
    time: new Date(2025, 0, 15, 14, 0, 0),
    date: new Date(2025, 0, 15)
}, 50)
// → Vẫn giữ LONG (đúng ngày nhưng chưa đến giờ)

// Ngày 15/01/2025 14:30 - Đúng giờ đáo hạn
checkExpiryExit({
    open: 106, high: 108, low: 105, close: 107,
    time: new Date(2025, 0, 15, 14, 30, 0),
    date: new Date(2025, 0, 15)
}, 51)
// → Đóng LONG
// Console: "📅 LONG closed by Expiry at 15/01/2025 14:30:00 (Expiry: 143000)"
// Status: FLAT

// Có thể mở position mới sau khi expiry
processSignal('SHORT', 52)
executePendingSignals(53, {close: 105, ...})  // Mở SHORT tại 105

// Ngày 20/01/2025 14:30 - Ngày đáo hạn thứ 2
checkExpiryExit({
    open: 103, high: 104, low: 102, close: 103,
    time: new Date(2025, 0, 20, 14, 30, 0),
    date: new Date(2025, 0, 20)
}, 100)
// → Đóng SHORT
// Console: "📅 SHORT closed by Expiry at 20/01/2025 14:30:00 (Expiry: 143000)"
```

**Use cases:**
- Đóng tất cả positions trước cuối tuần (expiry: thứ 6 15:00)
- Đóng positions vào các ngày đáo hạn hợp đồng futures
- Tự động exit vào các mốc thời gian quan trọng (báo cáo kinh tế, sự kiện)

---

## 🎯 Best Practices

### 1. Testing Strategy
- Luôn test từng exit method riêng lẻ trước
- Test với edge cases (price chạm đúng line, vượt qua line)
- Kiểm tra position state sau mỗi operation

### 2. Configuration Tips
- **Long Only**: Phù hợp cho uptrend market
- **Short Only**: Phù hợp cho downtrend market
- **Long and Short**: Cần exit method rõ ràng để tránh hold position quá lâu

### 3. Exit Methods Combination
- **TP + SL**: Cơ bản, phù hợp cho mọi strategy
- **TP + Trailing**: Tối đa hóa profit trong trend
- **Signal Exit**: Theo dõi thay đổi xu hướng
- **Tất cả**: Đa dạng exit conditions

### 4. Debugging
- Luôn check `tradingEngine.positions` sau mỗi operation
- Sử dụng `console.log` có sẵn trong code
- Test với data thật từ chart

---

## ❓ FAQ

**Q: Tại sao không mở được position mới?**
A: Kiểm tra:
- Position mode có cho phép không? (`canOpenPosition('LONG')`)
- Đang FLAT chưa? (nếu mode = long_and_short)
- Entry candle index đúng chưa?

**Q: Exit by Signal không hoạt động?**
A: Đảm bảo:
- Checkbox "Exit by Opposite Signal" đã được tick
- Exit Timing là "After 1 Candle" (bắt buộc)
- Đang giữ position ngược chiều (LONG vs SHORT signal)

**Q: Trailing Stop không trigger?**
A: Kiểm tra:
- HHV/LLV có được update đúng không? (`tradingEngine.positions.hhvSinceEntry`)
- Low có chạm trailing line không? (HHV - Trailing Points)
- Checkbox "Exit by Trailing Stop" đã được tick

**Q: Làm sao biết candle nào trigger exit?**
A: Xem console log:
```
✅ LONG closed by TP at 110 (Entry: 100)
🛑 LONG closed by SL at 90 (Entry: 100)
📉 LONG closed by Trailing at 105 (HHV: 110)
🔄 LONG closed by opposite SHORT signal at candle 30
📅 LONG closed by Expiry at 15/01/2025 14:30:00 (Expiry: 143000)
```

**Q: Expiry Exit không hoạt động?**
A: Kiểm tra:
- Checkbox "Exit by Expiry Day" đã được tick chưa?
- Format ngày đúng chưa? (DDMMYY, ví dụ: 150125)
- Format giờ đúng chưa? (HHMMSS, ví dụ: 143000)
- Xem config đã load đúng chưa: `tradingEngine.config.expiryConfig`
- Candle data có thuộc tính `date` hoặc `time` chưa?

**Q: Tại sao position đóng sớm hơn expiry time?**
A: Vì hệ thống so sánh `>=` expiry time. Nếu candle time >= expiry time thì đóng.
Ví dụ: Expiry = 14:30:00, candle đầu tiên từ 14:30 trở đi sẽ trigger exit.

**Q: Có thể có nhiều ngày đáo hạn không?**
A: Có! Nhập nhiều ngày cách nhau bởi dấu phẩy:
- Ví dụ: `150125,200125,250125` (3 ngày đáo hạn)
- Position sẽ đóng vào bất kỳ ngày nào trong danh sách

**Q: Skip Long Candle là gì? Khi nào dùng?**
A: Tính năng giúp giảm repaint của Trailing Stop:
- **Vấn đề**: Khi có nến dài xuất hiện, HHV/LLV thay đổi đột ngột → Trailing line repaint
- **Giải pháp**: Skip update HHV/LLV khi gặp nến dài + dùng HHV/LLV của nến trước (n-1)
- **Khi nào dùng**: Khi trade trên timeframe có nhiều nến dài (gaps, news events)

**Q: Làm sao biết nến có phải "long candle" không?**
A: Kiểm tra công thức:
```javascript
const candleSize = candle.high - candle.low
const isLongCandle = candleSize >= longCandleSize

// Ví dụ: longCandleSize = 50
// Candle: H=160, L=105 → size = 55 → Long candle!
// Console: "📏 Skipped HHV update - Long candle detected (size: 55.00)"
```

**Q: Trailing line dùng HHV[n] hay HHV[n-1]?**
A: **LUÔN dùng HHV[n-1]** (giá trị của nến trước) để tránh repaint:
```javascript
// HHV[n-1] = giá trị HHV của nến trước đó
// Trailing Line = HHV[n-1] - Trailing Points

// Ví dụ:
// Candle hiện tại: HHV = 110, HHV[n-1] = 105
// Trailing Line = 105 - 5 = 100 (dùng HHV[n-1], không repaint)
// Nếu dùng HHV[n]: Trailing Line = 110 - 5 = 105 (có thể repaint!)
```

**Q: Nếu TẮT Skip Long Candle thì sao?**
A: HHV/LLV sẽ update bình thường cho MỌI candle (kể cả nến dài):
- Trailing line vẫn dùng HHV[n-1] (không repaint)
- Nhưng HHV có thể thay đổi nhiều hơn
- Phù hợp khi muốn trailing stop nhạy hơn

**Q: Dynamic Trailing khác gì Fixed Trailing?**
A: So sánh chi tiết:

| Aspect | Fixed Trailing | Dynamic Trailing |
|--------|----------------|------------------|
| **Cách tính** | Trailing Line = HHV[n-1] - Fixed Points | Trailing Line = Entry + (Profit - Profit × Tier%) |
| **Thay đổi** | Không đổi (cố định số points) | Thay đổi theo profit level (%) |
| **Khi profit thấp** | Có thể thoát sớm | Lỏng hơn, cho price breathe |
| **Khi profit cao** | Giữ nhiều profit | Chặt hơn, bảo vệ profit |
| **Complexity** | Đơn giản (1 param) | Phức tạp (5+ params) |
| **Optimization** | Khó optimize | Dễ optimize với nhiều params |

**Q: Khi nào nên dùng Dynamic Trailing?**
A: Dynamic Trailing phù hợp khi:
- **Ưu tiên bảo toàn profit**: Muốn bảo vệ profit chặt chẽ khi đã có profit cao
- **Market volatile**: Price di chuyển mạnh, cần trailing adaptive
- **Strategy optimization**: Muốn optimize nhiều parameters
- **Risk-averse trader**: Chấp nhận thoát sớm để đảm bảo profit

Fixed Trailing phù hợp khi:
- **Maximize profit**: Muốn giữ position lâu hơn trong trend
- **Simple strategy**: Ưu tiên đơn giản, ít parameters
- **Strong trend**: Market có xu hướng rõ ràng, ít đảo chiều
- **Aggressive trader**: Sẵn sàng risk để lấy profit cao hơn

**Q: Làm sao xem tier nào đang được dùng?**
A: Xem trong console log khi trailing được check:
```javascript
// Dynamic mode:
console.log('📉 Profit: 25.00, Tier: 50%')
console.log('📉 LONG closed by Trailing at 112.5 (Profit: 25.00, Tier: 50%)')

// Fixed mode:
console.log('📉 LONG closed by Trailing at 120 (HHV[n-1]: 125)')
```

**Q: Có thể thay đổi tier parameters không?**
A: Hiện tại tier parameters được cài cứng trong config:
```javascript
tradingEngine.config.trailingConfig.dynamicTiers = [
    { minProfit: 0,  maxProfit: 20,  trailingPercent: 30 },
    { minProfit: 20, maxProfit: 50,  trailingPercent: 50 },
    { minProfit: 50, maxProfit: 9999, trailingPercent: 70 }
]
```
Có thể edit trực tiếp trong console hoặc trong code để test các tier khác.

**Q: Tier cuối cùng phải có maxProfit là bao nhiêu?**
A: Tier cuối cùng nên có `maxProfit = 9999` (hoặc số rất lớn) để cover tất cả profit levels:
```javascript
// ✅ ĐÚNG: Tier cuối cover tất cả profit >= 50
{ minProfit: 50, maxProfit: 9999, trailingPercent: 70 }

// ❌ SAI: Nếu profit > 100 thì không match tier nào
{ minProfit: 50, maxProfit: 100, trailingPercent: 70 }
```

**Q: Dynamic Trailing có dùng HHV[n-1] để tránh repaint không?**
A: **CÓ!** Dynamic Trailing vẫn dùng HHV[n-1]/LLV[n-1] giống Fixed Trailing:
```javascript
// Calculate max profit based on HHV[n-1] (not HHV[n])
const hhvForTrailing = pos.hhvPrevious !== null ? pos.hhvPrevious : pos.hhvSinceEntry
const result = calculateDynamicTrailing(pos.entryPrice, hhvForTrailing, tiers, 'LONG')

// Formula sử dụng HHV[n-1]:
// Max Profit = HHV[n-1] - Entry
// Trailing Points = Max Profit × (Tier% / 100)
// Trailing Line = Entry + (Max Profit - Trailing Points)
```

**Q: Skip Long Candle có áp dụng cho Dynamic Trailing không?**
A: **CÓ!** Skip Long Candle áp dụng cho cả Fixed và Dynamic Trailing:
```javascript
tradingEngine.config.trailingConfig.skipLongCandle = true
tradingEngine.config.trailingConfig.longCandleSize = 50

// Khi candle size >= 50:
// - Không update HHV/LLV
// - Dynamic Trailing vẫn tính dựa trên HHV[n-1]
// - Tier calculation không bị ảnh hưởng bởi long candle
```

---

## 📚 Tài Liệu Tham Khảo

- `trading-engine-core.js`: Core logic
- `workspace.js`: Signal processing integration
- `strategy-builder.js`: Save/load configuration
- `strategy_builder.html`: UI configuration

---

**Version:** 1.1
**Last Updated:** 2025-01-17
**Author:** Trading Engine Team
**Features:** Entry/Exit Methods, TP/SL/Trailing (Fixed & Dynamic), Expiry Exit, Skip Long Candle
