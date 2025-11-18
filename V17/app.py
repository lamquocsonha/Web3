from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import random
from datetime import datetime, timedelta
import json
import os
import time
from werkzeug.utils import secure_filename
import pandas as pd
import logging
from trading_engine.indicators import Indicators
from trading_engine.exchange_connector import exchange_manager
from realtime_streamer import RealtimeStreamer
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Auto reload templates
app.jinja_env.auto_reload = True  # Force Jinja2 to reload templates
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable static file cache

# Disable all browser caching during development
@app.after_request
def add_no_cache_headers(response):
    """Add headers to disable browser caching completely during development"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Create uploads directory if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('strategies', exist_ok=True)

socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=100 * 1024 * 1024)

# Initialize real-time streamer
realtime_streamer = RealtimeStreamer(socketio, exchange_manager)

# Mock data storage
positions = []
orders = []
current_price = 1873.80

def generate_ohlc_data(days=1):
    """Generate mock OHLC data for chart"""
    data = []
    base_price = 1870
    current_time = datetime.now() - timedelta(days=days)
    
    for i in range(100):
        open_price = base_price + random.uniform(-5, 5)
        high = open_price + random.uniform(0, 3)
        low = open_price - random.uniform(0, 3)
        close = random.uniform(low, high)
        volume = random.randint(500, 2000)
        
        data.append({
            'time': int(current_time.timestamp()),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        })
        
        current_time += timedelta(minutes=5)
        base_price = close
    
    return data

def parse_csv_data(filepath, timezone_offset=0):
    """
    Parse CSV file and auto-detect format
    Supports:
    1. Python format: Ticker,Date,Time,Open,High,Low,Close,Volume (YYYY-MM-DD)
    2. AmiBroker format: Ticker,Date,Open,High,Low,Close,Volume,Time (DD/MM/YYYY)
    
    Flexible column matching (case-insensitive)
    
    Args:
        filepath: Path to CSV file
        timezone_offset: Timezone offset in hours (e.g. +7 for Vietnam)
    """
    debug_info = {}
    try:
        logger.info(f"📂 Parsing CSV: {filepath} (timezone: {timezone_offset:+d}h)")
        
        # Read CSV with multiple encoding fallbacks
        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
        df = None
        used_encoding = None
        for encoding in encodings:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                used_encoding = encoding
                logger.info(f"✅ Read {len(df)} rows with encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            return {
                'success': False, 
                'error': 'Không thể đọc file với các encoding được hỗ trợ (utf-8, latin1, cp1252)',
                'debug_info': {'tried_encodings': encodings}
            }
        
        debug_info['encoding'] = used_encoding
        debug_info['total_rows'] = len(df)
        
        if len(df) == 0:
            return {
                'success': False, 
                'error': 'File CSV không có dữ liệu',
                'debug_info': debug_info
            }
        
        # Normalize column names
        original_columns = list(df.columns)
        df.columns = df.columns.str.strip().str.lower()
        debug_info['original_columns'] = original_columns
        debug_info['normalized_columns'] = list(df.columns)
        
        # Show first 3 rows for debugging
        debug_info['first_rows'] = df.head(3).to_dict('records')
        
        logger.info(f"📋 Original columns: {original_columns}")
        logger.info(f"📋 Normalized columns: {list(df.columns)}")
        
        # Column mapping (flexible)
        column_mapping = {
            'ticker': ['ticker', 'symbol', 'code', 'stock'],
            'date': ['date', 'ngay', 'datetime'],
            'time': ['time', 'gio', 'hour'],
            'open': ['open', 'o', 'mo', 'mo_cua'],
            'high': ['high', 'h', 'cao', 'cao_nhat'],
            'low': ['low', 'l', 'thap', 'thap_nhat'],
            'close': ['close', 'c', 'dong', 'dong_cua'],
            'volume': ['volume', 'vol', 'v', 'klgd', 'kl']
        }
        
        # Find matching columns
        matched_cols = {}
        missing_cols = []
        for standard_name, possible_names in column_mapping.items():
            found = False
            for col in df.columns:
                if col in possible_names:
                    matched_cols[standard_name] = col
                    found = True
                    logger.info(f"✅ '{standard_name}' → '{col}'")
                    break
            if not found:
                missing_cols.append(standard_name)
                
        debug_info['matched_columns'] = matched_cols
        debug_info['missing_columns'] = missing_cols
        
        if missing_cols:
            error_msg = f"❌ Thiếu các cột: {', '.join(missing_cols)}\n\n"
            error_msg += f"📋 Cột trong file: {', '.join(original_columns)}\n\n"
            error_msg += "💡 File cần có ít nhất: Ticker, Date, Time, Open, High, Low, Close, Volume"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg, 'debug_info': debug_info}
        
        # Rename to standard
        df = df.rename(columns={
            matched_cols['ticker']: 'Ticker',
            matched_cols['date']: 'Date',
            matched_cols['time']: 'Time',
            matched_cols['open']: 'Open',
            matched_cols['high']: 'High',
            matched_cols['low']: 'Low',
            matched_cols['close']: 'Close',
            matched_cols['volume']: 'Volume'
        })
        
        # Clean data - remove rows with NaN values
        initial_count = len(df)
        df = df.dropna(subset=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
        if len(df) < initial_count:
            logger.warning(f"⚠️ Removed {initial_count - len(df)} rows with missing data")
            debug_info['removed_rows'] = initial_count - len(df)
        
        if len(df) == 0:
            return {
                'success': False, 
                'error': 'Không có dòng dữ liệu hợp lệ sau khi lọc (tất cả rows có NaN)',
                'debug_info': debug_info
            }
        
        # Parse datetime
        date_sample = str(df['Date'].iloc[0]).strip()
        time_sample = str(df['Time'].iloc[0]).strip()
        debug_info['date_sample'] = date_sample
        debug_info['time_sample'] = time_sample
        logger.info(f"📅 Sample: Date='{date_sample}', Time='{time_sample}'")
        
        try:
            if '-' in date_sample:
                # Python format: YYYY-MM-DD
                df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str))
                debug_info['date_format'] = 'Python (YYYY-MM-DD)'
                logger.info("✅ Python format (YYYY-MM-DD)")
            elif '/' in date_sample:
                # AmiBroker format: DD/MM/YYYY
                df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str), dayfirst=True)
                debug_info['date_format'] = 'AmiBroker (DD/MM/YYYY)'
                logger.info("✅ AmiBroker format (DD/MM/YYYY)")
            else:
                return {
                    'success': False, 
                    'error': f"❌ Định dạng ngày không được hỗ trợ: '{date_sample}'\n\nChỉ hỗ trợ: YYYY-MM-DD hoặc DD/MM/YYYY",
                    'debug_info': debug_info
                }
        except Exception as e:
            return {
                'success': False, 
                'error': f"❌ Không parse được datetime:\n{str(e)}\n\nMẫu: {date_sample} {time_sample}",
                'debug_info': debug_info
            }
        
        # Apply timezone offset
        if timezone_offset != 0:
            df['DateTime'] = df['DateTime'] + pd.Timedelta(hours=timezone_offset)
            logger.info(f"🌍 Applied timezone offset: {timezone_offset:+d} hours")
        
        # Sort by datetime
        df = df.sort_values('DateTime')
        
        # Convert to chart format
        chart_data = []
        conversion_errors = 0
        error_samples = []
        for idx, row in df.iterrows():
            try:
                # Validate OHLCV values
                open_val = float(row['Open'])
                high_val = float(row['High'])
                low_val = float(row['Low'])
                close_val = float(row['Close'])
                volume_val = int(float(row['Volume']))
                
                # Basic validation
                if high_val < low_val:
                    raise ValueError(f"High ({high_val}) < Low ({low_val})")
                if volume_val < 0:
                    raise ValueError(f"Volume âm: {volume_val}")
                
                chart_data.append({
                    'time': int(row['DateTime'].timestamp()),
                    'open': open_val,
                    'high': high_val,
                    'low': low_val,
                    'close': close_val,
                    'volume': volume_val
                })
            except Exception as e:
                conversion_errors += 1
                if conversion_errors <= 5:
                    error_samples.append(f"Row {idx}: {str(e)}")
                    logger.warning(f"⚠️ Skip row {idx}: {str(e)}")
                continue
        
        if conversion_errors > 0:
            debug_info['conversion_errors'] = conversion_errors
            debug_info['error_samples'] = error_samples
            logger.warning(f"⚠️ Total conversion errors: {conversion_errors}")

        
        if len(chart_data) == 0:
            error_msg = 'Không có dòng dữ liệu hợp lệ sau khi convert sang chart format\n\n'
            error_msg += f'📊 Thông tin debug:\n'
            error_msg += f'- Số dòng ban đầu: {debug_info["total_rows"]}\n'
            error_msg += f'- Số dòng sau khi lọc NaN: {len(df)}\n'
            if conversion_errors > 0:
                error_msg += f'- Lỗi convert: {conversion_errors} dòng\n\n'
            error_msg += f'💡 Kiểm tra:\n'
            error_msg += f'- Các cột OHLCV phải chứa số hợp lệ\n'
            error_msg += f'- Cột DateTime phải có format đúng\n'
            error_msg += f'- Volume phải là số nguyên dương'
            
            return {
                'success': False, 
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Stats
        ticker = str(df['Ticker'].iloc[0]).strip()
        start_date = df['DateTime'].min().strftime('%Y-%m-%d %H:%M')
        end_date = df['DateTime'].max().strftime('%Y-%m-%d %H:%M')
        total_candles = len(chart_data)
        
        logger.info(f"✅ {ticker}: {total_candles} candles ({start_date} → {end_date})")
        
        return {
            'success': True,
            'data': chart_data,
            'info': {
                'ticker': ticker,
                'start_date': start_date,
                'end_date': end_date,
                'total_candles': total_candles,
                'timeframe': '1M',
                'timezone_offset': timezone_offset
            }
        }
        
    except Exception as e:
        error = f'Parse error: {str(e)}'
        logger.error(f"❌ {error}")
        logger.exception(e)  # Full traceback
        return {'success': False, 'error': error, 'debug_info': debug_info}
    """
    Parse CSV file and auto-detect format
    Supports:
    1. Python format: Ticker,Date,Time,Open,High,Low,Close,Volume (YYYY-MM-DD)
    2. AmiBroker format: Ticker,Date,Open,High,Low,Close,Volume,Time (DD/MM/YYYY)
    
    Flexible column matching (case-insensitive)
    """
    try:
        logger.info(f"📂 Parsing CSV: {filepath}")
        
        # Read CSV with multiple encoding fallbacks
        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
        df = None
        for encoding in encodings:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                logger.info(f"✅ Read {len(df)} rows with encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            return {'success': False, 'error': 'Cannot decode file with supported encodings'}
        
        if len(df) == 0:
            return {'success': False, 'error': 'File CSV không có dữ liệu'}
        
        # Normalize column names
        original_columns = list(df.columns)
        df.columns = df.columns.str.strip().str.lower()
        logger.info(f"📋 Original columns: {original_columns}")
        logger.info(f"📋 Normalized columns: {list(df.columns)}")
        
        # Column mapping (flexible)
        column_mapping = {
            'ticker': ['ticker', 'symbol', 'code', 'stock'],
            'date': ['date', 'ngay', 'datetime'],
            'time': ['time', 'gio', 'hour'],
            'open': ['open', 'o', 'mo', 'mo_cua'],
            'high': ['high', 'h', 'cao', 'cao_nhat'],
            'low': ['low', 'l', 'thap', 'thap_nhat'],
            'close': ['close', 'c', 'dong', 'dong_cua'],
            'volume': ['volume', 'vol', 'v', 'klgd', 'kl']
        }
        
        # Find matching columns
        matched_cols = {}
        for standard_name, possible_names in column_mapping.items():
            found = False
            for col in df.columns:
                if col in possible_names:
                    matched_cols[standard_name] = col
                    found = True
                    logger.info(f"✅ '{standard_name}' → '{col}'")
                    break
            if not found:
                error = f'❌ Không tìm thấy cột [{standard_name}]\n\n'
                error += f'Cột hiện có: {original_columns}\n\n'
                error += f'Cột được hỗ trợ cho {standard_name}: {possible_names}'
                logger.error(f"❌ {error}")
                return {'success': False, 'error': error}
        
        # Rename to standard
        df = df.rename(columns={
            matched_cols['ticker']: 'Ticker',
            matched_cols['date']: 'Date',
            matched_cols['time']: 'Time',
            matched_cols['open']: 'Open',
            matched_cols['high']: 'High',
            matched_cols['low']: 'Low',
            matched_cols['close']: 'Close',
            matched_cols['volume']: 'Volume'
        })
        
        # Clean data - remove rows with NaN values
        initial_count = len(df)
        df = df.dropna(subset=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
        if len(df) < initial_count:
            logger.warning(f"⚠️ Removed {initial_count - len(df)} rows with missing data")
        
        if len(df) == 0:
            error = f'❌ Không có dòng dữ liệu hợp lệ sau khi lọc!\n\n'
            error += f'Đã đọc {initial_count} dòng nhưng tất cả có giá trị null/NaN.\n'
            error += f'Kiểm tra lại file CSV.'
            return {'success': False, 'error': error}
        
        # Parse datetime
        date_sample = str(df['Date'].iloc[0]).strip()
        time_sample = str(df['Time'].iloc[0]).strip()
        logger.info(f"📅 Sample: Date='{date_sample}', Time='{time_sample}'")
        
        try:
            if '-' in date_sample:
                # Python format: YYYY-MM-DD
                df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str))
                logger.info("✅ Python format (YYYY-MM-DD)")
            elif '/' in date_sample:
                # AmiBroker format: DD/MM/YYYY
                df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str), dayfirst=True)
                logger.info("✅ AmiBroker format (DD/MM/YYYY)")
            else:
                return {'success': False, 'error': f'Unknown date format: {date_sample}'}
        except Exception as e:
            return {'success': False, 'error': f'Cannot parse datetime: {str(e)}\nSample: {date_sample} {time_sample}'}
        
        # Sort by datetime
        df = df.sort_values('DateTime')
        
        # Convert to chart format
        chart_data = []
        for idx, row in df.iterrows():
            try:
                chart_data.append({
                    'time': int(row['DateTime'].timestamp()),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(float(row['Volume']))
                })
            except Exception as e:
                logger.warning(f"⚠️ Skip row {idx}: {str(e)}")
                continue
        
        if len(chart_data) == 0:
            return {'success': False, 'error': 'Không convert được dữ liệu sang chart format'}
        
        # Stats
        ticker = str(df['Ticker'].iloc[0]).strip()
        start_date = df['DateTime'].min().strftime('%Y-%m-%d')
        end_date = df['DateTime'].max().strftime('%Y-%m-%d')
        total_candles = len(chart_data)
        
        logger.info(f"✅ {ticker}: {total_candles} candles ({start_date} → {end_date})")
        
        return {
            'success': True,
            'data': chart_data,
            'info': {
                'ticker': ticker,
                'start_date': start_date,
                'end_date': end_date,
                'total_candles': total_candles,
                'timeframe': '1M'
            }
        }
        
    except Exception as e:
        error = f'Parse error: {str(e)}'
        logger.error(f"❌ {error}")
        logger.exception(e)  # Full traceback
        return {'success': False, 'error': error}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/strategy-builder')
def strategy_builder():
    return render_template('strategy_builder.html')

@app.route('/backtest')
def backtest():
    return render_template('backtest.html')

@app.route('/optimize')
def optimize():
    return render_template('optimize.html')

@app.route('/hft')
def hft():
    return render_template('hft.html')

@app.route('/api/chart-data')
def get_chart_data():
    """Get initial chart data"""
    return jsonify(generate_ohlc_data())

@app.route('/api/positions')
def get_positions():
    """Get current positions"""
    return jsonify(positions)

@app.route('/api/orders')
def get_orders():
    """Get pending orders"""
    return jsonify(orders)

@app.route('/api/place-order', methods=['POST'])
def place_order():
    """Place new order"""
    data = request.json
    order = {
        'id': len(orders) + 1,
        'symbol': data.get('symbol', 'VN30F1M'),
        'type': data.get('type', 'LO'),
        'side': data.get('side', 'LONG'),
        'price': data.get('price'),
        'volume': data.get('volume', 1),
        'time': datetime.now().strftime('%H:%M:%S'),
        'status': 'Pending'
    }
    orders.append(order)
    
    # Broadcast to all clients
    socketio.emit('order_update', {'orders': orders})
    
    return jsonify({'success': True, 'order': order})

@app.route('/api/close-position/<int:position_id>', methods=['POST'])
def close_position(position_id):
    """Close a position"""
    global positions
    positions = [p for p in positions if p['id'] != position_id]
    socketio.emit('position_update', {'positions': positions})
    return jsonify({'success': True})

@app.route('/api/run-backtest', methods=['POST'])
def run_backtest_mock():
    """Run backtest with given parameters (mock for dashboard)"""
    data = request.json
    
    # Mock backtest results
    import time
    time.sleep(2)  # Simulate backtest running
    
    results = {
        'success': True,
        'totalTrades': random.randint(50, 200),
        'winRate': round(random.uniform(45, 65), 2),
        'profitFactor': round(random.uniform(1.2, 2.5), 2),
        'netProfit': random.randint(5000000, 50000000),
        'maxDrawdown': round(random.uniform(10, 25), 2)
    }
    
    return jsonify(results)

@app.route('/api/save-settings', methods=['POST'])
def save_settings():
    """Save user settings"""
    data = request.json
    # In production, save to database or config file
    print('Settings saved:', data)
    return jsonify({'success': True})

@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Test MT5 connection"""
    data = request.json
    
    # Mock connection test
    import time
    time.sleep(1)
    
    # Simulate random success/failure
    if random.random() > 0.3:
        return jsonify({
            'success': True,
            'balance': random.randint(50000000, 200000000)
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Invalid credentials or server not responding'
        })

@app.route('/api/start-bot', methods=['POST'])
def start_bot():
    """Start trading bot"""
    data = request.json
    print('Bot started with config:', data)
    
    # In production: Start actual bot with strategy
    return jsonify({
        'success': True,
        'message': 'Bot started successfully'
    })

@app.route('/api/stop-bot', methods=['POST'])
def stop_bot():
    """Stop trading bot"""
    print('Bot stopped')
    
    # In production: Stop actual bot
    return jsonify({
        'success': True,
        'message': 'Bot stopped successfully'
    })

@app.route('/api/connect-exchange', methods=['POST'])
def connect_exchange():
    """Connect to exchange and get historical data"""
    try:
        data = request.json
        exchange = data.get('exchange')
        credentials = data.get('credentials', {})
        symbol = data.get('symbol')
        timeframe = data.get('timeframe')
        candles = data.get('candles', 1000)
        
        logger.info(f"📡 Connecting to {exchange} for {symbol} {timeframe}")
        
        # Create connector based on exchange
        if exchange == 'mt5':
            from trading_engine.exchange_connector import MT5Connector
            connector = MT5Connector()
        elif exchange == 'binance':
            from trading_engine.exchange_connector import BinanceConnector
            connector = BinanceConnector()
        elif exchange == 'dnse':
            from trading_engine.exchange_connector import DNSEConnector
            connector = DNSEConnector()
        else:
            return jsonify({'success': False, 'error': 'Unsupported exchange'}), 400
        
        # Connect
        if not connector.connect(credentials):
            return jsonify({'success': False, 'error': 'Failed to connect to exchange'}), 400
        
        # Get historical data
        if hasattr(connector, 'get_historical_data'):
            historical_data = connector.get_historical_data(symbol, timeframe, candles)
        else:
            connector.disconnect()
            return jsonify({'success': False, 'error': 'Exchange does not support historical data'}), 400
        
        if not historical_data:
            connector.disconnect()
            return jsonify({'success': False, 'error': 'No data received from exchange'}), 400
        
        # Format dates
        from datetime import datetime
        start_date = datetime.fromtimestamp(historical_data[0]['time']).strftime('%Y-%m-%d %H:%M')
        end_date = datetime.fromtimestamp(historical_data[-1]['time']).strftime('%Y-%m-%d %H:%M')
        
        # Disconnect
        connector.disconnect()
        
        logger.info(f"✅ Connected! Loaded {len(historical_data)} candles")
        
        return jsonify({
            'success': True,
            'data': historical_data,
            'start_date': start_date,
            'end_date': end_date,
            'symbol': symbol,
            'timeframe': timeframe,
            'exchange': exchange
        })
        
    except Exception as e:
        logger.error(f"❌ Exchange connection error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload-csv', methods=['POST'])
@app.route('/upload_data', methods=['POST'])
def upload_csv():
    """Upload CSV file and parse data"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        timezone_offset = int(request.form.get('timezone_offset', 0))  # Get timezone offset from form
        timeframe = request.form.get('timeframe', '1m')  # Get timeframe from form
        
        logger.info(f"📤 Upload request: file={file.filename}, timezone={timezone_offset}, timeframe={timeframe}")
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if file and file.filename.endswith('.csv'):
            # Store original filename for display
            original_filename = file.filename
            
            # Generate safe filename
            filename = secure_filename(file.filename)
            
            # Fallback if secure_filename returns empty or just ".csv"
            if not filename or filename == '.csv' or len(filename) < 5:
                import time
                filename = f"data_{int(time.time())}.csv"
                logger.warning(f"⚠️ secure_filename failed for '{original_filename}', using fallback: {filename}")
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Overwrite if exists
            if os.path.exists(filepath):
                logger.info(f"🔄 Overwriting: {filename}")
                os.remove(filepath)
            
            file.save(filepath)
            logger.info(f"💾 Saved: {filepath} (original: {original_filename})")
            
            # Parse CSV with timezone
            result = parse_csv_data(filepath, timezone_offset)
            
            if result['success']:
                # Save processed data as JSON for persistence
                processed_filename = filename.replace('.csv', '_processed.json')
                processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
                
                processed_data = {
                    'original_filename': original_filename,
                    'processed_at': datetime.now().isoformat(),
                    'timezone_offset': timezone_offset,
                    'data': result['data'],
                    'info': result['info']
                }
                
                with open(processed_filepath, 'w', encoding='utf-8') as f:
                    json.dump(processed_data, f, ensure_ascii=False)
                logger.info(f"💾 Saved processed file: {processed_filename}")
                
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'original_filename': original_filename,
                    'processed_filename': processed_filename,
                    'data': result['data'],
                    'info': result['info'],
                    'timeframe': timeframe,  # Return selected timeframe
                    'message': f"Loaded {result['info']['total_candles']} candles ({result['info']['start_date']} → {result['info']['end_date']})"
                })
            else:
                # Return detailed error with debug info
                error_response = {
                    'success': False,
                    'error': result['error'],
                    'debug_info': result.get('debug_info', {})
                }
                logger.error(f"❌ Parse failed: {result['error']}")
                if 'debug_info' in result:
                    logger.error(f"Debug info: {result['debug_info']}")
                return jsonify(error_response), 400
        
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
    except Exception as e:
        logger.error(f"❌ Upload error: {str(e)}")
        logger.exception(e)
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/api/list-csv-files')
def list_csv_files():
    """List all uploaded CSV files"""
    try:
        files = []
        upload_dir = app.config['UPLOAD_FOLDER']
        
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(upload_dir, filename)
                    file_stat = os.stat(filepath)
                    files.append({
                        'filename': filename,
                        'size': file_stat.st_size,
                        'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                    })
        
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/load-latest-processed')
def load_latest_processed():
    """Load latest processed JSON file from uploads"""
    try:
        upload_dir = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_dir):
            return jsonify({'success': False, 'error': 'Upload directory not found'})
        
        # Find all processed JSON files
        processed_files = []
        for filename in os.listdir(upload_dir):
            if filename.endswith('_processed.json'):
                filepath = os.path.join(upload_dir, filename)
                file_stat = os.stat(filepath)
                processed_files.append({
                    'filename': filename,
                    'filepath': filepath,
                    'modified': file_stat.st_mtime
                })
        
        if not processed_files:
            return jsonify({'success': False, 'error': 'No processed files found'})
        
        # Get latest file by modification time
        latest_file = max(processed_files, key=lambda x: x['modified'])
        
        with open(latest_file['filepath'], 'r', encoding='utf-8') as f:
            processed_data = json.load(f)
        
        logger.info(f"📂 Loaded latest processed file: {latest_file['filename']}")
        
        return jsonify({
            'success': True,
            'filename': latest_file['filename'],
            'data': processed_data['data'],
            'info': processed_data['info'],
            'original_filename': processed_data.get('original_filename', ''),
            'processed_at': processed_data.get('processed_at', ''),
            'timezone_offset': processed_data.get('timezone_offset', 0)
        })
    except Exception as e:
        logger.error(f"❌ Load latest processed error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/load-csv/<filename>')
def load_csv_file(filename):
    """Load CSV file from server"""
    try:
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'content': content,
            'filename': filename
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save-strategy', methods=['POST'])
@app.route('/save_strategy', methods=['POST'])
def save_strategy():
    """Save strategy configuration"""
    try:
        strategy = request.json
        
        if not strategy or 'name' not in strategy:
            return jsonify({'success': False, 'error': 'Invalid strategy data'}), 400
        
        # Create strategies directory if not exists
        strategies_dir = 'strategies'
        os.makedirs(strategies_dir, exist_ok=True)
        
        # Generate safe filename (remove Vietnamese characters)
        import unicodedata
        name = strategy['name']
        # Normalize and remove accents
        name_normalized = unicodedata.normalize('NFKD', name)
        name_ascii = ''.join([c for c in name_normalized if not unicodedata.combining(c)])
        # Replace spaces and special chars
        filename = f"{name_ascii.replace(' ', '_')}.json"
        filepath = os.path.join(strategies_dir, filename)
        
        # Save strategy with UTF-8 encoding
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': f"Strategy '{strategy['name']}' saved successfully"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/strategies/<filename>')
def get_strategy_file(filename):
    """Serve strategy JSON file"""
    try:
        filename = secure_filename(filename)
        filepath = os.path.join('strategies', filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'Strategy not found'}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            strategy = json.load(f)
        
        return jsonify(strategy)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auto-generate-strategy', methods=['POST'])
def auto_generate_strategy():
    """Auto-modify current strategy with new entry conditions and TP/SL"""
    try:
        from trading_engine.auto_generator import StrategyAutoGenerator

        # Get parameters
        data = request.json
        current_strategy = data.get('current_strategy', {})
        long_signals = data.get('long_signals', 2)
        short_signals = data.get('short_signals', 2)
        indicators_per_signal = data.get('indicators_per_signal', 2)
        profit_levels = data.get('profit_levels', 4)
        profit_step = data.get('profit_step', 3)
        keep_indicators = data.get('keep_indicators', True)
        randomize_tpsl = data.get('randomize_tpsl', True)

        logger.info(f"🤖 Auto-modifying strategy: {current_strategy.get('name', 'Unknown')}")
        logger.info(f"   Long signals: {long_signals}, Short signals: {short_signals}")
        logger.info(f"   Indicators per signal: {indicators_per_signal}")
        logger.info(f"   Profit levels: {profit_levels}, Step: {profit_step}")

        # Initialize generator
        generator = StrategyAutoGenerator()

        # Modify strategy
        modified_strategy = generator.modify_strategy(
            current_strategy=current_strategy,
            long_signals=long_signals,
            short_signals=short_signals,
            indicators_per_signal=indicators_per_signal,
            profit_levels=profit_levels,
            profit_step=profit_step,
            keep_indicators=keep_indicators,
            randomize_tpsl=randomize_tpsl
        )

        logger.info(f"✅ Strategy modified successfully")
        logger.info(f"   Long entries: {len(modified_strategy['entry_conditions']['long'])}")
        logger.info(f"   Short entries: {len(modified_strategy['entry_conditions']['short'])}")
        logger.info(f"   TP/SL levels: {len(modified_strategy['exit_rules']['long']['tp_sl_table'])}")

        return jsonify({
            'success': True,
            'strategy': modified_strategy
        })

    except Exception as e:
        logger.error(f"❌ Error auto-modifying strategy: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auto-generate-strategies', methods=['POST'])
def auto_generate_strategies():
    """Auto-generate strategies from templates (for batch generation in Optimize page)"""
    try:
        from trading_engine.auto_generator import StrategyAutoGenerator

        # Get parameters
        data = request.json
        count = data.get('count', 10)
        template = data.get('template', 'random')
        min_win_rate = data.get('min_win_rate', 0.55)
        min_profit_factor = data.get('min_profit_factor', 1.5)
        optimize = data.get('optimize', False)

        logger.info(f"🤖 Auto-generating {count} strategies from template: {template}")

        # Initialize generator
        generator = StrategyAutoGenerator()

        # Generate strategies
        strategies_list = generator.generate_batch(count, template)

        logger.info(f"✅ Generated {len(strategies_list)} strategies")

        # For now, return strategies without backtest
        # TODO: Add backtest integration when CSV data is available
        results = []

        for i, strategy in enumerate(strategies_list):
            # Simulate backtest results (placeholder)
            # In production, this would call backtest_engine
            mock_results = {
                'win_rate': random.uniform(0.45, 0.7),
                'profit_factor': random.uniform(1.2, 3.0),
                'total_return': random.uniform(-10, 50),
                'max_drawdown': random.uniform(-15, -5),
                'total_trades': random.randint(50, 200)
            }

            # Filter by criteria
            if (mock_results['win_rate'] >= min_win_rate and
                mock_results['profit_factor'] >= min_profit_factor):
                results.append({
                    'strategy': strategy,
                    'results': mock_results
                })

        logger.info(f"✅ {len(results)} strategies passed filters")

        return jsonify({
            'success': True,
            'strategies': results,
            'total_generated': len(strategies_list),
            'passed_filter': len(results)
        })

    except Exception as e:
        logger.error(f"❌ Error auto-generating strategies: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/list-strategies')
@app.route('/list_strategies')
def list_strategies():
    """List all saved strategies"""
    try:
        strategies_dir = 'strategies'
        strategies = []
        
        logger.info(f"📂 Listing strategies from: {strategies_dir}")
        
        if os.path.exists(strategies_dir):
            files = [f for f in os.listdir(strategies_dir) if f.endswith('.json')]
            logger.info(f"📄 Found {len(files)} JSON files")
            
            for filename in files:
                filepath = os.path.join(strategies_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        strategy = json.load(f)
                        strategies.append({
                            'filename': filename,
                            'name': strategy.get('name', 'Unknown'),
                            'description': strategy.get('description', ''),
                            'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                        })
                        logger.info(f"  ✅ Loaded: {filename} - {strategy.get('name', 'Unknown')}")
                except Exception as e:
                    logger.error(f"  ❌ Error loading {filename}: {str(e)}")
        else:
            logger.warning(f"⚠️ Directory not found: {strategies_dir}")
        
        logger.info(f"✅ Returning {len(strategies)} strategies")
        return jsonify({'success': True, 'strategies': strategies})
    except Exception as e:
        logger.error(f"❌ Error listing strategies: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/load-strategy/<filename>')
def load_strategy(filename):
    """Load strategy configuration"""
    try:
        filename = secure_filename(filename)
        filepath = os.path.join('strategies', filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'Strategy not found'}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            strategy = json.load(f)
        
        return jsonify({
            'success': True,
            'strategy': strategy,
            'filename': filename
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/indicator-templates')
def get_indicator_templates():
    """Get available indicator templates"""
    try:
        template_file = os.path.join('templates', 'indicator_templates.json')
        
        if not os.path.exists(template_file):
            return jsonify({'success': False, 'error': 'Templates file not found'}), 404
        
        with open(template_file, 'r', encoding='utf-8') as f:
            templates = json.load(f)
        
        return jsonify({
            'success': True,
            'templates': templates
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete-strategy/<filename>', methods=['DELETE'])
def delete_strategy(filename):
    """Delete strategy file"""
    try:
        filename = secure_filename(filename)
        filepath = os.path.join('strategies', filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'success': True, 'message': 'Strategy deleted'})
        else:
            return jsonify({'success': False, 'error': 'Strategy not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-signals', methods=['POST'])
def generate_signals():
    """Generate trading signals from strategy and data"""
    try:
        data = request.json
        strategy_filename = data.get('strategy')
        chart_data = data.get('data')  # OHLCV data
        
        if not strategy_filename or not chart_data:
            return jsonify({'success': False, 'error': 'Missing strategy or data'}), 400
        
        # Load strategy
        strategy_path = os.path.join('strategies', secure_filename(strategy_filename))
        if not os.path.exists(strategy_path):
            return jsonify({'success': False, 'error': 'Strategy not found'}), 404
        
        with open(strategy_path, 'r') as f:
            strategy_config = json.load(f)
        
        # Convert chart data to candlestick format for signal engine
        candlesticks = []
        for i in range(len(chart_data['close'])):
            candlesticks.append({
                'time': i,  # Use index as time
                'open': chart_data['open'][i],
                'high': chart_data['high'][i],
                'low': chart_data['low'][i],
                'close': chart_data['close'][i],
                'volume': chart_data['volume'][i] if i < len(chart_data['volume']) else 0
            })
        
        # Initialize signals arrays
        buy_signals = [False] * len(chart_data['close'])
        short_signals = [False] * len(chart_data['close'])
        
        # Generate signals using strategy conditions
        for index, candle in enumerate(candlesticks):
            if index == 0:
                continue  # Skip first candle
            
            prev_candle = candlesticks[index - 1]
            
            # Check long entry conditions
            if strategy_config.get('entry_conditions', {}).get('long'):
                for signal in strategy_config['entry_conditions']['long']:
                    if evaluate_signal_conditions_python(signal, candle, prev_candle, candlesticks, index, strategy_config):
                        buy_signals[index] = True
                        break
            
            # Check short entry conditions
            if strategy_config.get('entry_conditions', {}).get('short'):
                for signal in strategy_config['entry_conditions']['short']:
                    if evaluate_signal_conditions_python(signal, candle, prev_candle, candlesticks, index, strategy_config):
                        short_signals[index] = True
                        break
        
        return jsonify({
            'success': True,
            'signals': {
                'buy': buy_signals,
                'short': short_signals,
                'sell': [False] * len(chart_data['close']),
                'cover': [False] * len(chart_data['close'])
            },
            'strategy_name': strategy_config.get('name', 'Unknown')
        })
        
    except Exception as e:
        logger.error(f"Generate signals error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def evaluate_signal_conditions_python(signal, candle, prev_candle, all_candles, current_index, config):
    """Evaluate signal conditions (Python version matching JavaScript logic)"""
    if not signal.get('conditions') or len(signal['conditions']) == 0:
        return False
    
    result = True
    current_logic = 'AND'
    
    for i, cond in enumerate(signal['conditions']):
        cond_result = evaluate_single_condition_python(cond, candle, prev_candle, all_candles, current_index, config)
        
        if i == 0:
            result = cond_result
        else:
            if current_logic == 'AND':
                result = result and cond_result
            else:
                result = result or cond_result
        
        current_logic = cond.get('logic', 'AND')
    
    return result


def evaluate_single_condition_python(cond, candle, prev_candle, all_candles, current_index, config):
    """Evaluate single condition (Python version)"""
    try:
        # Get left value
        left_val = get_operand_value_python(cond['left'], candle, prev_candle, all_candles, current_index, config, cond.get('leftOffset', 0))
        
        # Get operator
        operator = cond['operator']
        
        # Handle boolean operators
        if operator == 'is_true':
            return bool(left_val)
        elif operator == 'is_false':
            return not bool(left_val)
        
        # Get right value
        right = cond['right']
        if isinstance(right, (int, float)):
            right_val = float(right)
        else:
            right_val = get_operand_value_python(right, candle, prev_candle, all_candles, current_index, config, cond.get('rightOffset', 0))
        
        if left_val is None or right_val is None:
            return False
        
        # Evaluate comparison
        if operator == '>':
            return left_val > right_val
        elif operator == '<':
            return left_val < right_val
        elif operator == '>=':
            return left_val >= right_val
        elif operator == '<=':
            return left_val <= right_val
        elif operator == '==':
            return abs(left_val - right_val) < 0.0001
        elif operator == '!=':
            return abs(left_val - right_val) >= 0.0001
        elif operator == 'cross_above':
            if current_index == 0:
                return False
            prev_left = get_operand_value_python(cond['left'], prev_candle, None, all_candles, current_index - 1, config, cond.get('leftOffset', 0))
            prev_right = get_operand_value_python(right, prev_candle, None, all_candles, current_index - 1, config, cond.get('rightOffset', 0)) if not isinstance(right, (int, float)) else right_val
            return prev_left is not None and prev_right is not None and prev_left <= prev_right and left_val > right_val
        elif operator == 'cross_below':
            if current_index == 0:
                return False
            prev_left = get_operand_value_python(cond['left'], prev_candle, None, all_candles, current_index - 1, config, cond.get('leftOffset', 0))
            prev_right = get_operand_value_python(right, prev_candle, None, all_candles, current_index - 1, config, cond.get('rightOffset', 0)) if not isinstance(right, (int, float)) else right_val
            return prev_left is not None and prev_right is not None and prev_left >= prev_right and left_val < right_val
        
        return False
    except Exception as e:
        logger.error(f"Condition evaluation error: {e}")
        return False


def get_operand_value_python(operand, candle, prev_candle, all_candles, current_index, config, offset=0):
    """Get operand value (Python version)"""
    # Basic OHLCV
    if operand == 'open':
        return candle['open']
    elif operand == 'high':
        return candle['high']
    elif operand == 'low':
        return candle['low']
    elif operand == 'close':
        return candle['close']
    elif operand == 'volume':
        return candle.get('volume', 0)
    
    # Check if it's an indicator
    for ind in config.get('indicators', []):
        if ind['id'] == operand:
            # Calculate indicator value
            return calculate_indicator_value_python(ind, all_candles, current_index + offset)
    
    return None


def calculate_indicator_value_python(indicator, all_candles, index):
    """Calculate indicator value at specific index (Python version)"""
    if index < 0 or index >= len(all_candles):
        return None
    
    ind_type = indicator['type']
    params = indicator.get('params', {})
    
    try:
        if ind_type == 'EMA':
            period = params.get('period', 20)
            close_prices = [c['close'] for c in all_candles[:index + 1]]
            if len(close_prices) < period:
                return None
            ema_values = Indicators.ema(np.array(close_prices), period)
            return float(ema_values[-1])
        
        elif ind_type == 'SMA':
            period = params.get('period', 20)
            close_prices = [c['close'] for c in all_candles[:index + 1]]
            if len(close_prices) < period:
                return None
            sma_values = Indicators.sma(np.array(close_prices), period)
            return float(sma_values[-1])
        
        elif ind_type == 'RSI':
            period = params.get('period', 14)
            close_prices = [c['close'] for c in all_candles[:index + 1]]
            if len(close_prices) < period + 1:
                return None
            rsi_values = Indicators.rsi(np.array(close_prices), period)
            return float(rsi_values[-1])
        
        # Add more indicators as needed
        
    except Exception as e:
        logger.error(f"Indicator calculation error: {e}")
        return None
    
    return None

@app.route('/calculate_indicators', methods=['POST'])
def calculate_indicators():
    """Calculate indicators for chart display"""
    try:
        data = request.json
        indicators_config = data.get('indicators', [])
        ohlcv_data = data.get('data', [])
        
        if not ohlcv_data:
            return jsonify({'success': False, 'error': 'No data provided'})
        
        # Convert to DataFrame
        df = pd.DataFrame(ohlcv_data)
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        
        # Ensure timestamps are numeric (Unix timestamp)
        timestamps = df['time'].values
        # Handle both string and numeric timestamps
        if isinstance(timestamps[0], str):
            # Try to parse as datetime string
            try:
                timestamps = pd.to_datetime(timestamps).astype(int) // 10**9
            except:
                # If that fails, try direct conversion to int
                timestamps = df['time'].astype(int).values
        else:
            timestamps = timestamps.astype(int)
        
        logger.info(f"Calculating {len(indicators_config)} indicators for {len(timestamps)} candles")
        logger.debug(f"Time range: {timestamps[0]} to {timestamps[-1]}")
        
        result = {}
        
        for ind_config in indicators_config:
            ind_type = ind_config['type']
            params = ind_config.get('params', {})
            ind_id = ind_config['id']
            
            try:
                if ind_type == 'EMA':
                    period = params.get('period', 20)
                    values = Indicators.ema(close, period)
                    result[ind_id] = [
                        {'time': int(timestamps[i]), 'value': float(values[i])}
                        for i in range(len(values)) if not np.isnan(values[i])
                    ]
                    logger.debug(f"Calculated EMA({period}): {len(result[ind_id])} points")
                
                elif ind_type == 'SMA':
                    period = params.get('period', 20)
                    values = Indicators.sma(close, period)
                    result[ind_id] = [
                        {'time': int(timestamps[i]), 'value': float(values[i])}
                        for i in range(len(values)) if not np.isnan(values[i])
                    ]
                    logger.debug(f"Calculated SMA({period}): {len(result[ind_id])} points")
                
                elif ind_type == 'WMA':
                    period = params.get('period', 20)
                    values = Indicators.wma(close, period)
                    result[ind_id] = [
                        {'time': int(timestamps[i]), 'value': float(values[i])}
                        for i in range(len(values)) if not np.isnan(values[i])
                    ]
                    logger.debug(f"Calculated WMA({period}): {len(result[ind_id])} points")
                
                elif ind_type == 'RSI':
                    period = params.get('period', 14)
                    values = Indicators.rsi(close, period)
                    result[ind_id] = [
                        {'time': int(timestamps[i]), 'value': float(values[i])}
                        for i in range(len(values)) if not np.isnan(values[i])
                    ]
                    logger.debug(f"Calculated RSI({period}): {len(result[ind_id])} points")
                
                elif ind_type == 'MACD':
                    fast = params.get('fast', 12)
                    slow = params.get('slow', 26)
                    signal = params.get('signal', 9)
                    macd_line, signal_line, histogram = Indicators.macd(close, fast, slow, signal)
                    
                    result[ind_id + '_macd'] = [
                        {'time': int(timestamps[i]), 'value': float(macd_line[i])}
                        for i in range(len(macd_line)) if not np.isnan(macd_line[i])
                    ]
                    result[ind_id + '_signal'] = [
                        {'time': int(timestamps[i]), 'value': float(signal_line[i])}
                        for i in range(len(signal_line)) if not np.isnan(signal_line[i])
                    ]
                    logger.debug(f"Calculated MACD: {len(result[ind_id + '_macd'])} points")
                
                elif ind_type == 'BB' or ind_type == 'BollingerBands':
                    period = params.get('period', 20)
                    std = params.get('std_dev', 2)
                    upper, middle, lower = Indicators.bollinger_bands(close, period, std)
                    
                    result[ind_id + '_upper'] = [
                        {'time': int(timestamps[i]), 'value': float(upper[i])}
                        for i in range(len(upper)) if not np.isnan(upper[i])
                    ]
                    result[ind_id + '_middle'] = [
                        {'time': int(timestamps[i]), 'value': float(middle[i])}
                        for i in range(len(middle)) if not np.isnan(middle[i])
                    ]
                    result[ind_id + '_lower'] = [
                        {'time': int(timestamps[i]), 'value': float(lower[i])}
                        for i in range(len(lower)) if not np.isnan(lower[i])
                    ]
                    logger.debug(f"Calculated BB({period}): {len(result[ind_id + '_upper'])} points")
                
                elif ind_type == 'SuperTrend':
                    period = params.get('period', 10)
                    multiplier = params.get('multiplier', 3)
                    st_values, direction = Indicators.supertrend(high, low, close, period, multiplier)
                    
                    result[ind_id] = [
                        {'time': int(timestamps[i]), 'value': float(st_values[i])}
                        for i in range(len(st_values)) if not np.isnan(st_values[i])
                    ]
                    logger.debug(f"Calculated SuperTrend: {len(result[ind_id])} points")
                
                elif ind_type == 'ATR':
                    period = params.get('period', 14)
                    values = Indicators.atr(high, low, close, period)
                    result[ind_id] = [
                        {'time': int(timestamps[i]), 'value': float(values[i])}
                        for i in range(len(values)) if not np.isnan(values[i])
                    ]
                    logger.debug(f"Calculated ATR({period}): {len(result[ind_id])} points")
                    
            except Exception as ind_error:
                logger.error(f"Error calculating {ind_type}: {str(ind_error)}")
                continue
        
        logger.info(f"Successfully calculated {len(result)} indicator series")
        return jsonify({
            'success': True,
            'indicators': result
        })
        
    except Exception as e:
        logger.error(f"Error in calculate_indicators: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/list_uploaded_files')
def list_uploaded_files():
    """List all uploaded CSV files"""
    try:
        upload_dir = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_dir):
            return jsonify({'success': True, 'files': []})
        
        files = []
        for filename in os.listdir(upload_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(upload_dir, filename)
                file_stat = os.stat(filepath)
                files.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Sort by modified time, newest first
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/run_backtest', methods=['POST'])
def run_backtest():
    """Run backtest on uploaded data with selected strategy"""
    try:
        data = request.json
        csv_filename = data.get('csv_file')
        strategy_filename = data.get('strategy_file')
        initial_capital = float(data.get('initial_capital', 10000))
        commission = float(data.get('commission', 0.5))
        slippage = float(data.get('slippage', 0.1))
        timeframe = data.get('timeframe', '1H')  # Default to 1H if not provided

        if not csv_filename or not strategy_filename:
            return jsonify({'success': False, 'error': 'Missing CSV or strategy file'}), 400

        # Load CSV data
        csv_path = os.path.join('uploads', secure_filename(csv_filename))
        if not os.path.exists(csv_path):
            return jsonify({'success': False, 'error': 'CSV file not found'}), 404

        result = parse_csv_data(csv_path)
        if not result['success']:
            return jsonify(result), 400

        chart_data = result['data']

        # Resample data to selected timeframe (if needed)
        from trading_engine.timeframe_resampler import resample_data

        # Convert chart_data list to dict format for resampling
        data_dict = {
            'times': [candle['time'] for candle in chart_data],
            'opens': [candle['open'] for candle in chart_data],
            'highs': [candle['high'] for candle in chart_data],
            'lows': [candle['low'] for candle in chart_data],
            'closes': [candle['close'] for candle in chart_data],
            'volumes': [candle['volume'] for candle in chart_data]
        }

        # Resample if timeframe is not the source timeframe
        if timeframe and timeframe != '1H':  # Assuming source data is 1H
            resampled_data = resample_data(data_dict, timeframe)

            # Convert back to chart_data list format
            chart_data = [
                {
                    'time': resampled_data['times'][i],
                    'open': resampled_data['opens'][i],
                    'high': resampled_data['highs'][i],
                    'low': resampled_data['lows'][i],
                    'close': resampled_data['closes'][i],
                    'volume': resampled_data['volumes'][i]
                }
                for i in range(len(resampled_data['times']))
            ]
        
        # Load strategy
        strategy_path = os.path.join('strategies', secure_filename(strategy_filename))
        if not os.path.exists(strategy_path):
            return jsonify({'success': False, 'error': 'Strategy not found'}), 404
        
        with open(strategy_path, 'r') as f:
            strategy_config = json.load(f)
        
        # Import trading engine
        from trading_engine.strategy import Strategy
        from trading_engine.backtest_engine import BacktestEngine
        
        # Create strategy and backtest
        strategy = Strategy(strategy_config)
        backtest = BacktestEngine(strategy, initial_capital, commission, slippage)
        
        # Convert chart data from list of dicts to dict of numpy arrays
        # chart_data is a list: [{'time': 123, 'open': 100, ...}, ...]
        # Need to convert to: {'time': [123, 124, ...], 'open': [100, 101, ...]}
        bt_data = {
            'time': np.array([candle['time'] for candle in chart_data]),
            'open': np.array([candle['open'] for candle in chart_data]),
            'high': np.array([candle['high'] for candle in chart_data]),
            'low': np.array([candle['low'] for candle in chart_data]),
            'close': np.array([candle['close'] for candle in chart_data]),
            'volume': np.array([candle['volume'] for candle in chart_data])
        }
        
        # Run backtest
        results = backtest.run(bt_data)
        
        # Helper function to safely round numbers (handle NaN, inf)
        def safe_round(value, decimals=2):
            """Safely round a value, handling NaN and infinity"""
            if value is None:
                return 0
            if np.isnan(value) or np.isinf(value):
                return 0
            try:
                return round(float(value), decimals)
            except (ValueError, TypeError):
                return 0
        
        # Format results for frontend
        response = {
            'success': True,
            'results': {
                'total_trades': int(results['total_trades']),
                'winning_trades': int(results['winning_trades']),
                'losing_trades': int(results['losing_trades']),
                'win_rate': safe_round(results['win_rate']),
                'final_capital': safe_round(results['final_capital']),
                'total_return': safe_round(results['total_return']),
                'max_drawdown': safe_round(results['max_drawdown']),
                'profit_factor': safe_round(results['profit_factor']),
                'sharpe_ratio': safe_round(results['sharpe_ratio']),
                'avg_win': safe_round(results['avg_win']),
                'avg_loss': safe_round(results['avg_loss']),
                'largest_win': safe_round(results['largest_win']),
                'largest_loss': safe_round(results['largest_loss'])
            },
            'trades': [
                {
                    'entry_time': str(t['entry_time']),
                    'entry_price': safe_round(t['entry_price']),
                    'exit_time': str(t['exit_time']),
                    'exit_price': safe_round(t['exit_price']),
                    'direction': t['direction'],
                    'profit_value': safe_round(t['profit_value']),
                    'profit_points': safe_round(t['profit_points']),
                    'exit_reason': t['exit_reason']
                }
                for t in results['trades']
            ],
            'equity_curve': [
                {
                    'time': int(e['time']) if e['time'] else 0,
                    'equity': safe_round(e['equity']),
                    'capital': safe_round(e['capital'])
                }
                for e in results['equity_curve']
            ]
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Backtest error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/export_backtest_pdf', methods=['POST'])
def export_backtest_pdf():
    """Export backtest results to PDF with Long/Short/Total performance"""
    try:
        data = request.json
        results = data.get('results', {})
        trades = data.get('trades', [])
        equity_curve = data.get('equity_curve', [])
        strategy_name = data.get('strategy_name', 'Strategy')
        csv_filename = data.get('csv_filename', 'Data')
        
        # Create PDF
        pdf_filename = f"backtest_{strategy_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join('uploads', pdf_filename)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            alignment=1  # Center
        )
        elements.append(Paragraph(f"BACKTEST REPORT", title_style))
        elements.append(Paragraph(f"{strategy_name}", styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Info
        info_text = f"<b>Data:</b> {csv_filename}<br/><b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elements.append(Paragraph(info_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Calculate Long/Short/Total performance
        long_trades = [t for t in trades if t.get('direction') == 'long']
        short_trades = [t for t in trades if t.get('direction') == 'short']
        
        def calc_stats(trade_list):
            if not trade_list:
                return {
                    'trades': 0, 'wins': 0, 'losses': 0, 'win_rate': 0,
                    'profit': 0, 'avg_win': 0, 'avg_loss': 0, 'profit_factor': 0
                }
            wins = [t for t in trade_list if t.get('profit_value', 0) > 0]
            losses = [t for t in trade_list if t.get('profit_value', 0) <= 0]
            total_profit = sum(t.get('profit_value', 0) for t in trade_list)
            avg_win = sum(t.get('profit_value', 0) for t in wins) / len(wins) if wins else 0
            avg_loss = sum(t.get('profit_value', 0) for t in losses) / len(losses) if losses else 0
            gross_profit = sum(t.get('profit_value', 0) for t in wins)
            gross_loss = abs(sum(t.get('profit_value', 0) for t in losses))
            pf = gross_profit / gross_loss if gross_loss > 0 else 0
            
            return {
                'trades': len(trade_list),
                'wins': len(wins),
                'losses': len(losses),
                'win_rate': (len(wins) / len(trade_list) * 100) if trade_list else 0,
                'profit': total_profit,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': pf
            }
        
        long_stats = calc_stats(long_trades)
        short_stats = calc_stats(short_trades)
        total_stats = {
            'trades': results.get('total_trades', 0),
            'wins': results.get('winning_trades', 0),
            'losses': results.get('losing_trades', 0),
            'win_rate': results.get('win_rate', 0),
            'profit': results.get('final_capital', 0) - 10000,  # Assuming 10000 initial
            'avg_win': results.get('avg_win', 0),
            'avg_loss': results.get('avg_loss', 0),
            'profit_factor': results.get('profit_factor', 0)
        }
        
        # Performance Table - 3 columns
        elements.append(Paragraph("<b>PERFORMANCE SUMMARY</b>", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        
        perf_data = [
            ['Metric', 'LONG', 'SHORT', 'TOTAL'],
            ['Total Trades', str(long_stats['trades']), str(short_stats['trades']), str(total_stats['trades'])],
            ['Winning Trades', str(long_stats['wins']), str(short_stats['wins']), str(total_stats['wins'])],
            ['Losing Trades', str(long_stats['losses']), str(short_stats['losses']), str(total_stats['losses'])],
            ['Win Rate (%)', f"{long_stats['win_rate']:.2f}%", f"{short_stats['win_rate']:.2f}%", f"{total_stats['win_rate']:.2f}%"],
            ['Net Profit', f"${long_stats['profit']:.2f}", f"${short_stats['profit']:.2f}", f"${total_stats['profit']:.2f}"],
            ['Avg Win', f"${long_stats['avg_win']:.2f}", f"${short_stats['avg_win']:.2f}", f"${total_stats['avg_win']:.2f}"],
            ['Avg Loss', f"${long_stats['avg_loss']:.2f}", f"${short_stats['avg_loss']:.2f}", f"${total_stats['avg_loss']:.2f}"],
            ['Profit Factor', f"{long_stats['profit_factor']:.2f}", f"{short_stats['profit_factor']:.2f}", f"{total_stats['profit_factor']:.2f}"]
        ]
        
        perf_table = Table(perf_data, colWidths=[2.2*inch, 1.3*inch, 1.3*inch, 1.3*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (1, 1), (1, -1), colors.HexColor('#dcfce7')),  # Light green for LONG
            ('BACKGROUND', (2, 1), (2, -1), colors.HexColor('#fee2e2')),  # Light red for SHORT
            ('BACKGROUND', (3, 1), (3, -1), colors.HexColor('#dbeafe'))   # Light blue for TOTAL
        ]))
        elements.append(perf_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Additional Metrics
        elements.append(Paragraph("<b>RISK METRICS</b>", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        
        risk_data = [
            ['Metric', 'Value'],
            ['Max Drawdown', f"{results.get('max_drawdown', 0):.2f}%"],
            ['Sharpe Ratio', f"{results.get('sharpe_ratio', 0):.2f}"],
            ['Largest Win', f"${results.get('largest_win', 0):.2f}"],
            ['Largest Loss', f"${results.get('largest_loss', 0):.2f}"],
            ['Final Capital', f"${results.get('final_capital', 0):.2f}"],
            ['Total Return', f"{results.get('total_return', 0):.2f}%"]
        ]
        
        risk_table = Table(risk_data, colWidths=[3*inch, 3*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold')
        ]))
        elements.append(risk_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Equity Curve Chart
        if equity_curve:
            elements.append(Paragraph("<b>EQUITY CURVE</b>", styles['Heading3']))
            elements.append(Spacer(1, 0.1*inch))
            
            fig, ax = plt.subplots(figsize=(7, 3))
            times = [e['time'] for e in equity_curve]
            equity = [e['equity'] for e in equity_curve]
            ax.plot(times, equity, color='#1e40af', linewidth=2)
            ax.set_xlabel('Time')
            ax.set_ylabel('Equity ($)')
            ax.set_title('Equity Curve')
            ax.grid(True, alpha=0.3)
            
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            from reportlab.platypus import Image
            img = Image(img_buffer, width=6*inch, height=2.5*inch)
            elements.append(img)
            elements.append(PageBreak())
        
        # Trade List
        elements.append(Paragraph("<b>TRADE LIST</b>", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        
        if trades:
            # First 50 trades only
            trade_data = [['#', 'Entry Time', 'Direction', 'Entry', 'Exit', 'P/L', 'Reason']]
            for i, trade in enumerate(trades[:50], 1):
                trade_data.append([
                    str(i),
                    trade.get('entry_time', '')[:16],
                    trade.get('direction', '').upper(),
                    f"${trade.get('entry_price', 0):.2f}",
                    f"${trade.get('exit_price', 0):.2f}",
                    f"${trade.get('profit_value', 0):.2f}",
                    trade.get('exit_reason', '')[:10]
                ])
            
            trade_table = Table(trade_data, colWidths=[0.4*inch, 1.3*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch])
            trade_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
            ]))
            elements.append(trade_table)
            
            if len(trades) > 50:
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(f"<i>Showing first 50 of {len(trades)} trades</i>", styles['Normal']))
        else:
            elements.append(Paragraph("No trades executed", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        return send_file(pdf_path, as_attachment=True, download_name=pdf_filename, mimetype='application/pdf')
        
    except Exception as e:
        logger.error(f"PDF export error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/run_optimize', methods=['POST'])
def run_optimize():
    """Run genetic algorithm optimization"""
    try:
        data = request.json
        csv_filename = data.get('csv_file')
        strategy_filename = data.get('strategy_file')
        param_ranges = data.get('param_ranges', [])
        population_size = int(data.get('population_size', 50))
        generations = int(data.get('generations', 20))
        timeframe = data.get('timeframe', '1H')  # Default to 1H if not provided

        if not csv_filename or not strategy_filename or not param_ranges:
            return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

        # Load CSV data
        csv_path = os.path.join('uploads', secure_filename(csv_filename))
        if not os.path.exists(csv_path):
            return jsonify({'success': False, 'error': 'CSV file not found'}), 404

        result = parse_csv_data(csv_path)
        if not result['success']:
            return jsonify(result), 400

        chart_data = result['data']

        # Resample data to selected timeframe (if needed)
        from trading_engine.timeframe_resampler import resample_data

        # Convert chart_data list to dict format for resampling
        data_dict = {
            'times': [candle['time'] for candle in chart_data],
            'opens': [candle['open'] for candle in chart_data],
            'highs': [candle['high'] for candle in chart_data],
            'lows': [candle['low'] for candle in chart_data],
            'closes': [candle['close'] for candle in chart_data],
            'volumes': [candle['volume'] for candle in chart_data]
        }

        # Resample if timeframe is not the source timeframe
        if timeframe and timeframe != '1H':  # Assuming source data is 1H
            resampled_data = resample_data(data_dict, timeframe)
            # Update chart_data dict format (optimizer expects dict not list)
            chart_data = {
                'time': resampled_data['times'],
                'open': resampled_data['opens'],
                'high': resampled_data['highs'],
                'low': resampled_data['lows'],
                'close': resampled_data['closes'],
                'volume': resampled_data['volumes']
            }
        else:
            # Convert to dict format even if no resampling
            chart_data = {
                'time': data_dict['times'],
                'open': data_dict['opens'],
                'high': data_dict['highs'],
                'low': data_dict['lows'],
                'close': data_dict['closes'],
                'volume': data_dict['volumes']
            }
        
        # Load strategy
        strategy_path = os.path.join('strategies', secure_filename(strategy_filename))
        if not os.path.exists(strategy_path):
            return jsonify({'success': False, 'error': 'Strategy not found'}), 404
        
        with open(strategy_path, 'r') as f:
            strategy_config = json.load(f)
        
        # Import trading engine
        from trading_engine.strategy import Strategy
        from trading_engine.optimizer import GeneticOptimizer
        
        # Convert chart data to numpy arrays
        opt_data = {
            'time': np.array(chart_data['time']),
            'open': np.array(chart_data['open']),
            'high': np.array(chart_data['high']),
            'low': np.array(chart_data['low']),
            'close': np.array(chart_data['close']),
            'volume': np.array(chart_data['volume'])
        }
        
        # Create strategy and optimizer
        strategy = Strategy(strategy_config)
        optimizer = GeneticOptimizer(strategy, opt_data, population_size, generations)
        
        # Add parameters
        for param in param_ranges:
            optimizer.add_parameter(
                param['path'],
                param['min'],
                param['max'],
                param.get('step', 1),
                param.get('type', 'int')
            )
        
        # Run optimization
        opt_result = optimizer.optimize()
        
        return jsonify({
            'success': True,
            'best_params': opt_result['best_params'],
            'best_fitness': round(opt_result['best_fitness'], 2),
            'history': [
                {
                    'generation': i,
                    'best_fitness': round(h['best_fitness'], 2),
                    'avg_fitness': round(h['avg_fitness'], 2)
                }
                for i, h in enumerate(opt_result['history'])
            ],
            'final_population': [
                {
                    'params': ind['params'],
                    'fitness': round(ind['fitness'], 2)
                }
                for ind in opt_result['final_population'][:20]  # Top 20
            ]
        })
        
    except Exception as e:
        logger.error(f"Optimize error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# HFT WebSocket handlers
hft_running = {}  # Dictionary to track HFT sessions per client

@socketio.on('start_hft')
def handle_start_hft(data):
    """Start HFT trading simulation"""
    client_id = request.sid
    print(f'HFT started for client {client_id}')
    
    hft_running[client_id] = True
    
    # Start HFT simulation in background
    socketio.start_background_task(run_hft_simulation, client_id, data)
    
    emit('hft_started', {'message': 'HFT started successfully'})

@socketio.on('pause_hft')
def handle_pause_hft():
    """Pause HFT trading"""
    client_id = request.sid
    if client_id in hft_running:
        hft_running[client_id] = False
    emit('hft_paused', {'message': 'HFT paused'})

@socketio.on('resume_hft')
def handle_resume_hft():
    """Resume HFT trading"""
    client_id = request.sid
    if client_id in hft_running:
        hft_running[client_id] = True
    emit('hft_resumed', {'message': 'HFT resumed'})

@socketio.on('stop_hft')
def handle_stop_hft():
    """Stop HFT trading"""
    client_id = request.sid
    if client_id in hft_running:
        del hft_running[client_id]
    emit('hft_stopped', {'message': 'HFT stopped'})

@socketio.on('emergency_stop')
def handle_emergency_stop():
    """Emergency stop - close all positions"""
    client_id = request.sid
    if client_id in hft_running:
        del hft_running[client_id]
    emit('hft_emergency_stopped', {'message': 'Emergency stop executed'})

@socketio.on('close_position')
def handle_close_position(data):
    """Close a specific position"""
    position_id = data.get('id')
    emit('hft_position_closed', {
        'id': position_id,
        'message': f'Position {position_id} closed'
    })

def run_hft_simulation(client_id, settings):
    """Simulate HFT trading"""
    max_orders_per_sec = settings.get('maxOrdersPerSec', 10)
    position_size = settings.get('positionSize', 0.1)
    
    base_price = 1873.50
    position_counter = 0
    
    while client_id in hft_running and hft_running.get(client_id, False):
        # Random delay between trades (simulate high frequency)
        delay = random.uniform(0.05, 1.0 / max_orders_per_sec)
        socketio.sleep(delay)
        
        # Simulate trade
        side = random.choice(['LONG', 'SHORT'])
        price = base_price + random.uniform(-5, 5)
        profit = random.uniform(-10, 20)
        duration = random.uniform(0.1, 5.0)
        
        position_counter += 1
        
        # Emit trade event
        socketio.emit('hft_trade', {
            'time': datetime.now().isoformat(),
            'side': side,
            'size': position_size,
            'price': price,
            'profit': profit,
            'duration': duration
        }, room=client_id)
        
        # Randomly open positions (10% chance)
        if random.random() < 0.1:
            pos_id = f'pos_{position_counter}'
            socketio.emit('hft_position_opened', {
                'id': pos_id,
                'side': side,
                'size': position_size,
                'entryPrice': price,
                'currentPrice': price,
                'pnl': 0,
                'openTime': int(datetime.now().timestamp() * 1000)
            }, room=client_id)
            
            # Close position after random time
            socketio.start_background_task(close_position_after_delay, client_id, pos_id, random.uniform(1, 10))
        
        # Simulate latency
        if random.random() < 0.1:  # 10% chance
            latency = random.uniform(8, 25)
            socketio.emit('hft_latency', {
                'latency': latency
            }, room=client_id)
        
        # Vary base price slightly
        base_price += random.uniform(-0.1, 0.1)

def close_position_after_delay(client_id, position_id, delay):
    """Close a position after a delay"""
    socketio.sleep(delay)
    socketio.emit('hft_position_closed', {
        'id': position_id
    }, room=client_id)

def update_price():
    """Background task to update price"""
    global current_price
    while True:
        socketio.sleep(1)
        # Simulate price movement
        change = random.uniform(-0.5, 0.5)
        current_price += change
        current_price = round(current_price, 2)
        
        # Generate new candle data point
        new_candle = {
            'time': int(datetime.now().timestamp()),
            'open': current_price,
            'high': current_price + random.uniform(0, 0.3),
            'low': current_price - random.uniform(0, 0.3),
            'close': current_price,
            'volume': random.randint(500, 1000)
        }
        
        socketio.emit('price_update', {
            'price': current_price,
            'candle': new_candle
        })

# ==================== EXCHANGE CONNECTION ROUTES ====================

@app.route('/exchange-settings')
def exchange_settings():
    """Exchange Settings Page"""
    return render_template('exchange_settings.html')

@app.route('/api/exchange/profiles', methods=['GET'])
def get_exchange_profiles():
    """Get all saved profiles"""
    try:
        profiles = exchange_manager.get_profiles()
        return jsonify({'success': True, 'profiles': profiles})
    except Exception as e:
        logger.error(f"Get profiles error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/profile', methods=['POST'])
def add_exchange_profile():
    """Add new exchange profile"""
    try:
        data = request.json
        profile_name = data.get('profile_name')
        exchange = data.get('exchange')
        credentials = data.get('credentials')
        
        if not all([profile_name, exchange, credentials]):
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        success = exchange_manager.add_profile(profile_name, exchange, credentials)
        
        if success:
            return jsonify({'success': True, 'message': 'Profile saved successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save profile'})
    except Exception as e:
        logger.error(f"Add profile error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/profile/<profile_name>', methods=['DELETE'])
def delete_exchange_profile(profile_name):
    """Delete exchange profile"""
    try:
        success = exchange_manager.remove_profile(profile_name)
        
        if success:
            return jsonify({'success': True, 'message': 'Profile deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Profile not found'})
    except Exception as e:
        logger.error(f"Delete profile error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/profile/<profile_name>/credentials', methods=['GET'])
def get_profile_credentials(profile_name):
    """Get decrypted credentials for editing profile"""
    try:
        credentials = exchange_manager.get_profile_credentials(profile_name)
        if credentials:
            return jsonify({'success': True, 'credentials': credentials})
        else:
            return jsonify({'success': False, 'error': 'Profile not found'})
    except Exception as e:
        logger.error(f"Get credentials error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/test', methods=['POST'])
def test_exchange_connection():
    """Test exchange connection without saving"""
    try:
        data = request.json
        exchange = data.get('exchange')
        credentials = data.get('credentials')
        
        if not all([exchange, credentials]):
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        result = exchange_manager.test_connection(exchange, credentials)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Test connection error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/connect/<profile_name>', methods=['POST'])
def connect_exchange_profile(profile_name):
    """Connect to exchange using saved profile - Hỗ trợ OTP cho DNSE"""
    try:
        data = request.get_json(silent=True) or {}
        otp_code = data.get('otp') if data else None
        
        logger.info(f"🔌 Connect request: {profile_name}, OTP: {'Yes' if otp_code else 'No'}")
        
        result = exchange_manager.connect_profile(profile_name, otp_code)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Connect profile error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/disconnect/<profile_name>', methods=['POST'])
def disconnect_exchange_profile(profile_name):
    """Disconnect from exchange"""
    try:
        exchange_manager.disconnect_profile(profile_name)
        return jsonify({'success': True, 'message': 'Disconnected successfully'})
    except Exception as e:
        logger.error(f"Disconnect profile error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/update-connection-status', methods=['POST'])
def update_connection_status():
    """Update connection status in profile JSON"""
    try:
        data = request.json
        profile_name = data.get('profile_name')
        connected = data.get('connected', False)
        
        # Load profiles
        profiles_file = 'exchange_profiles.json'
        with open(profiles_file, 'r', encoding='utf-8') as f:
            profiles = json.load(f)
        
        # Update connected status
        if profile_name in profiles:
            profiles[profile_name]['connected'] = connected
            
            # Save back to file
            with open(profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Updated connection status for {profile_name}: {connected}")
            return jsonify({'success': True, 'message': 'Connection status updated'})
        else:
            return jsonify({'success': False, 'error': 'Profile not found'})
    except Exception as e:
        logger.error(f"Update connection status error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/set-active-data', methods=['POST'])
def set_active_data_profile():
    """Set active data profile and persist to file"""
    try:
        data = request.json
        profile_name = data.get('profile_name')
        result = exchange_manager.set_active_data_profile(profile_name)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Set active data profile error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/set-active-trading', methods=['POST'])
def set_active_trading_profile():
    """Set active trading profile and persist to file"""
    try:
        data = request.json
        profile_name = data.get('profile_name')
        result = exchange_manager.set_active_trading_profile(profile_name)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Set active trading profile error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/get-active-profiles', methods=['GET'])
def get_active_profiles_api():
    """Get currently active profiles"""
    try:
        result = exchange_manager.get_active_profiles()
        return jsonify({'success': True, 'profiles': result})
    except Exception as e:
        logger.error(f"Get active profiles error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/request-otp', methods=['POST'])
def request_exchange_otp():
    """Request OTP for DNSE exchange - Hỗ trợ cả saved profile và new credentials"""
    try:
        data = request.get_json(silent=True) or {}
        exchange = data.get('exchange', 'dnse')
        profile_name = data.get('profile_name')  # Optional: cho saved profiles
        username = data.get('username')
        password = data.get('password')
        
        # Chỉ DNSE cần OTP
        if exchange != 'dnse':
            return jsonify({'success': False, 'error': 'Exchange không hỗ trợ OTP'}), 400
        
        # Nếu có profile_name, lấy credentials từ profile
        if profile_name:
            logger.info(f"🔑 Getting credentials from profile: {profile_name}")
            credentials = exchange_manager.get_profile_credentials(profile_name)
            if not credentials:
                return jsonify({'success': False, 'error': 'Profile không tồn tại hoặc lỗi credentials'}), 400
            username = credentials.get('username')
            password = credentials.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username và Password là bắt buộc'}), 400
        
        # Get DNSE connector
        connector = exchange_manager.connectors.get('dnse')
        if not connector:
            return jsonify({'success': False, 'error': 'DNSE connector không tồn tại'}), 500
        
        # Request OTP
        result = connector.request_otp(username, password)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Request OTP error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/exchange/can-trade', methods=['GET'])
def can_trade():
    """Check if trading is available"""
    try:
        result = exchange_manager.can_trade()
        return jsonify({'success': True, **result})
    except Exception as e:
        logger.error(f"Can trade check error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/load-data/<profile_name>', methods=['POST'])
def load_data_from_profile(profile_name):
    """Connect to exchange profile and load historical data"""
    try:
        data = request.json
        symbol = data.get('symbol')
        timeframe = data.get('timeframe', 'M5')
        candles = data.get('candles', 1000)
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol is required'}), 400
        
        logger.info(f"📡 Loading data from profile: {profile_name}, {symbol} {timeframe}")
        
        # Connect profile if not connected
        connector = exchange_manager.get_connector(profile_name)
        if not connector:
            logger.info(f"🔌 Profile not connected, connecting now...")
            result = exchange_manager.connect_profile(profile_name)
            if not result.get('success'):
                return jsonify(result), 400
            connector = exchange_manager.get_connector(profile_name)
            
            # For MQTT connectors, wait a bit for connection to stabilize
            if connector and hasattr(connector, 'mqtt_client'):
                logger.info(f"⏳ MQTT connection detected, waiting 2s for subscription...")
                import time
                time.sleep(2)
        
        if not connector:
            return jsonify({'success': False, 'error': 'Failed to get connector'}), 400
        
        # Check if MQTT connector
        is_mqtt = hasattr(connector, 'mqtt_client')
        
        # Get historical data
        logger.info(f"🔍 Checking if connector has get_historical_data method...")
        if hasattr(connector, 'get_historical_data'):
            logger.info(f"✅ Calling get_historical_data({symbol}, {timeframe}, {candles})")
            
            # For MQTT, this may take up to 5 seconds to subscribe and receive data
            if is_mqtt:
                logger.info(f"📡 MQTT: Subscribing to {symbol} and waiting for OHLC data...")
            
            historical_data = connector.get_historical_data(symbol, timeframe, candles)
            logger.info(f"📊 Received data: {type(historical_data)}, length: {len(historical_data) if historical_data else 0}")
        else:
            logger.error(f"❌ Connector does not have get_historical_data method")
            return jsonify({'success': False, 'error': 'Exchange does not support historical data'}), 400
        
        if not historical_data:
            error_msg = 'No data received from exchange'
            if is_mqtt:
                error_msg = f'No OHLC data received for {symbol}. MQTT broker may not be sending OHLC messages for this symbol, or the symbol format is incorrect. Try tick data streaming instead.'
            
            logger.error(f"❌ {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Format dates
        from datetime import datetime
        start_date = datetime.fromtimestamp(historical_data[0]['time']).strftime('%Y-%m-%d %H:%M')
        end_date = datetime.fromtimestamp(historical_data[-1]['time']).strftime('%Y-%m-%d %H:%M')
        
        # Get exchange name from profile
        profile = exchange_manager.profiles.get(profile_name, {})
        exchange = profile.get('exchange', 'unknown')
        
        logger.info(f"✅ Loaded {len(historical_data)} candles from {profile_name}")
        
        return jsonify({
            'success': True,
            'data': historical_data,
            'start_date': start_date,
            'end_date': end_date,
            'symbol': symbol,
            'timeframe': timeframe,
            'exchange': exchange,
            'profile_name': profile_name,
            'is_mqtt': is_mqtt
        })
        
    except Exception as e:
        logger.error(f"❌ Load data error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/exchange/account/<profile_name>', methods=['GET'])
def get_exchange_account_info(profile_name):
    """Get account information from connected exchange"""
    try:
        connector = exchange_manager.get_connector(profile_name)
        
        if not connector:
            return jsonify({'success': False, 'error': 'Profile not connected'})
        
        account_info = connector.get_account_info()
        return jsonify({'success': True, 'account_info': account_info})
    except Exception as e:
        logger.error(f"Get account info error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/positions/<profile_name>', methods=['GET'])
def get_exchange_positions(profile_name):
    """Get positions from connected exchange"""
    try:
        connector = exchange_manager.get_connector(profile_name)
        
        if not connector:
            return jsonify({'success': False, 'error': 'Profile not connected'})
        
        positions = connector.get_positions()
        return jsonify({'success': True, 'positions': positions})
    except Exception as e:
        logger.error(f"Get positions error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/orders/<profile_name>', methods=['GET'])
def get_exchange_orders(profile_name):
    """Get orders from connected exchange"""
    try:
        connector = exchange_manager.get_connector(profile_name)
        
        if not connector:
            return jsonify({'success': False, 'error': 'Profile not connected'})
        
        # Check if connector has get_orders method
        if hasattr(connector, 'get_orders'):
            orders = connector.get_orders()
            return jsonify({'success': True, 'orders': orders})
        else:
            return jsonify({'success': False, 'error': 'Orders not supported for this exchange'})
    except Exception as e:
        logger.error(f"Get orders error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/deals/<profile_name>', methods=['GET'])
def get_exchange_deals(profile_name):
    """Get deals/trade history from connected exchange"""
    try:
        connector = exchange_manager.get_connector(profile_name)
        
        if not connector:
            return jsonify({'success': False, 'error': 'Profile not connected'})
        
        # Check if connector has get_deals method
        if hasattr(connector, 'get_deals'):
            deals = connector.get_deals()
            return jsonify({'success': True, 'deals': deals})
        else:
            return jsonify({'success': False, 'error': 'Deals not supported for this exchange'})
    except Exception as e:
        logger.error(f"Get deals error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/order/<profile_name>', methods=['POST'])
def place_exchange_order(profile_name):
    """Place order on connected exchange"""
    try:
        connector = exchange_manager.get_connector(profile_name)
        
        if not connector:
            return jsonify({'success': False, 'error': 'Profile not connected'})
        
        data = request.json
        symbol = data.get('symbol')
        side = data.get('side')
        order_type = data.get('order_type', 'MARKET')
        quantity = float(data.get('quantity', 0))
        price = float(data.get('price', 0)) if data.get('price') else None
        
        if not all([symbol, side, quantity]):
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        result = connector.place_order(symbol, side, order_type, quantity, price)
        
        if result:
            return jsonify({'success': True, 'order': result})
        else:
            return jsonify({'success': False, 'error': 'Failed to place order'})
    except Exception as e:
        logger.error(f"Place order error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/realtime/<profile_name>', methods=['GET'])
def get_exchange_realtime(profile_name):
    """Get realtime snapshot (account info + ticker prices)"""
    try:
        connector = exchange_manager.get_connector(profile_name)
        
        if not connector:
            return jsonify({'success': False, 'error': 'Profile not connected'})
        
        # Get account info
        account_info = connector.get_account_info()
        
        # Get ticker for symbols if available
        # symbols = request.args.get('symbols', '').split(',')
        # tickers = {}
        # for symbol in symbols:
        #     if symbol.strip():
        #         ticker = connector.get_ticker(symbol.strip())
        #         if ticker:
        #             tickers[symbol.strip()] = ticker
        
        return jsonify({
            'success': True,
            'account_info': account_info,
            # 'tickers': tickers,
            'timestamp': int(time.time() * 1000)
        })
    except Exception as e:
        logger.error(f"Get realtime data error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exchange/ticker/<profile_name>/<symbol>', methods=['GET'])
def get_exchange_ticker(profile_name, symbol):
    """Get ticker price from connected exchange"""
    try:
        connector = exchange_manager.get_connector(profile_name)
        
        if not connector:
            return jsonify({'success': False, 'error': 'Profile not connected'})
        
        ticker = connector.get_ticker(symbol)
        
        if ticker:
            return jsonify({'success': True, 'ticker': ticker})
        else:
            return jsonify({'success': False, 'error': 'Failed to get ticker'})
    except Exception as e:
        logger.error(f"Get ticker error: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ==================== REAL-TIME STREAMING ROUTES ====================

@app.route('/api/stream/start/<profile_name>', methods=['POST'])
def start_realtime_stream(profile_name):
    """Start real-time MQTT streaming for profile"""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        interval = data.get('interval', 0.1)  # Default 100ms update rate
        
        if not symbols:
            return jsonify({'success': False, 'error': 'No symbols provided'})
        
        result = realtime_streamer.start_stream(profile_name, symbols, interval)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Start stream error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stream/stop/<profile_name>', methods=['POST'])
def stop_realtime_stream(profile_name):
    """Stop real-time streaming for profile"""
    try:
        result = realtime_streamer.stop_stream(profile_name)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Stop stream error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stream/status', methods=['GET'])
def get_stream_status():
    """Get status of all active streams"""
    try:
        active_streams = realtime_streamer.get_active_streams()
        return jsonify({
            'success': True,
            'streams': active_streams
        })
    except Exception as e:
        logger.error(f"Get stream status error: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ==================== END REAL-TIME STREAMING ROUTES ====================

# ==================== END EXCHANGE CONNECTION ROUTES ====================

# ==================== CLIENT MANAGEMENT ROUTES ====================

@app.route('/client-management')
def client_management():
    """Client Management Page"""
    return render_template('client_management.html')

@app.route('/client-reports/<client_id>')
def client_reports(client_id):
    """Client Reports Page"""
    return render_template('client_reports.html', client_id=client_id)

@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Get all clients"""
    try:
        clients_file = 'clients.json'
        if os.path.exists(clients_file):
            with open(clients_file, 'r', encoding='utf-8') as f:
                clients = json.load(f)
                return jsonify(clients)
        return jsonify({})
    except Exception as e:
        logger.error(f"Error loading clients: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clients/<client_id>', methods=['GET'])
def get_client(client_id):
    """Get single client by ID"""
    try:
        clients_file = 'clients.json'
        if os.path.exists(clients_file):
            with open(clients_file, 'r', encoding='utf-8') as f:
                clients = json.load(f)
                if client_id in clients:
                    return jsonify(clients[client_id])
                return jsonify({'error': 'Client not found'}), 404
        return jsonify({'error': 'No clients found'}), 404
    except Exception as e:
        logger.error(f"Error loading client: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clients', methods=['POST'])
def save_client():
    """Create or update client"""
    try:
        client_data = request.json
        client_id = client_data.get('client_id')
        
        if not client_id:
            return jsonify({'error': 'Client ID is required'}), 400
        
        clients_file = 'clients.json'
        clients = {}
        
        if os.path.exists(clients_file):
            with open(clients_file, 'r', encoding='utf-8') as f:
                clients = json.load(f)
        
        # Add timestamp if new client
        if client_id not in clients:
            client_data['created_at'] = datetime.now().isoformat()
            client_data['total_trades'] = 0
            client_data['total_pnl'] = 0
        else:
            # Preserve existing stats
            if 'total_trades' in clients[client_id]:
                client_data['total_trades'] = clients[client_id]['total_trades']
            if 'total_pnl' in clients[client_id]:
                client_data['total_pnl'] = clients[client_id]['total_pnl']
        
        clients[client_id] = client_data
        
        with open(clients_file, 'w', encoding='utf-8') as f:
            json.dump(clients, f, indent=2, ensure_ascii=False)
        
        # Initialize trades file if not exists
        trades_file = 'client_trades.json'
        if os.path.exists(trades_file):
            with open(trades_file, 'r', encoding='utf-8') as f:
                trades_data = json.load(f)
        else:
            trades_data = {}
        
        if client_id not in trades_data:
            trades_data[client_id] = {
                'trades': [],
                'summary': {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'total_pnl': 0,
                    'win_rate': 0,
                    'average_win': 0,
                    'average_loss': 0,
                    'largest_win': 0,
                    'largest_loss': 0,
                    'profit_factor': 0
                }
            }
            with open(trades_file, 'w', encoding='utf-8') as f:
                json.dump(trades_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True, 'client': client_data})
    except Exception as e:
        logger.error(f"Error saving client: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clients/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Delete client"""
    try:
        clients_file = 'clients.json'
        if not os.path.exists(clients_file):
            return jsonify({'error': 'No clients found'}), 404
        
        with open(clients_file, 'r', encoding='utf-8') as f:
            clients = json.load(f)
        
        if client_id not in clients:
            return jsonify({'error': 'Client not found'}), 404
        
        del clients[client_id]
        
        with open(clients_file, 'w', encoding='utf-8') as f:
            json.dump(clients, f, indent=2, ensure_ascii=False)
        
        # Also delete trades
        trades_file = 'client_trades.json'
        if os.path.exists(trades_file):
            with open(trades_file, 'r', encoding='utf-8') as f:
                trades_data = json.load(f)
            
            if client_id in trades_data:
                del trades_data[client_id]
                
                with open(trades_file, 'w', encoding='utf-8') as f:
                    json.dump(trades_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting client: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clients/<client_id>/trades', methods=['GET'])
def get_client_trades(client_id):
    """Get trades for a client"""
    try:
        trades_file = 'client_trades.json'
        if not os.path.exists(trades_file):
            return jsonify({
                'trades': [],
                'summary': {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'total_pnl': 0,
                    'win_rate': 0,
                    'average_win': 0,
                    'average_loss': 0,
                    'largest_win': 0,
                    'largest_loss': 0,
                    'profit_factor': 0
                }
            })
        
        with open(trades_file, 'r', encoding='utf-8') as f:
            trades_data = json.load(f)
        
        if client_id in trades_data:
            return jsonify(trades_data[client_id])
        
        return jsonify({
            'trades': [],
            'summary': {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_pnl': 0,
                'win_rate': 0,
                'average_win': 0,
                'average_loss': 0,
                'largest_win': 0,
                'largest_loss': 0,
                'profit_factor': 0
            }
        })
    except Exception as e:
        logger.error(f"Error loading client trades: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clients/<client_id>/trades', methods=['POST'])
def add_client_trade(client_id):
    """Add a new trade for a client"""
    try:
        trade = request.json
        trades_file = 'client_trades.json'
        
        if os.path.exists(trades_file):
            with open(trades_file, 'r', encoding='utf-8') as f:
                trades_data = json.load(f)
        else:
            trades_data = {}
        
        if client_id not in trades_data:
            trades_data[client_id] = {
                'trades': [],
                'summary': {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'total_pnl': 0,
                    'win_rate': 0,
                    'average_win': 0,
                    'average_loss': 0,
                    'largest_win': 0,
                    'largest_loss': 0,
                    'profit_factor': 0
                }
            }
        
        # Add trade
        trades_data[client_id]['trades'].append(trade)
        
        # Update summary
        summary = trades_data[client_id]['summary']
        summary['total_trades'] += 1
        
        pnl = trade.get('pnl', 0)
        summary['total_pnl'] += pnl
        
        if pnl > 0:
            summary['winning_trades'] += 1
            summary['largest_win'] = max(summary['largest_win'], pnl)
        else:
            summary['losing_trades'] += 1
            summary['largest_loss'] = min(summary['largest_loss'], pnl)
        
        # Calculate averages
        if summary['winning_trades'] > 0:
            winning_trades = [t for t in trades_data[client_id]['trades'] if t['pnl'] > 0]
            summary['average_win'] = sum(t['pnl'] for t in winning_trades) / len(winning_trades)
        
        if summary['losing_trades'] > 0:
            losing_trades = [t for t in trades_data[client_id]['trades'] if t['pnl'] <= 0]
            summary['average_loss'] = sum(t['pnl'] for t in losing_trades) / len(losing_trades)
        
        # Calculate win rate
        summary['win_rate'] = (summary['winning_trades'] / summary['total_trades']) * 100 if summary['total_trades'] > 0 else 0
        
        # Calculate profit factor
        total_wins = sum(t['pnl'] for t in trades_data[client_id]['trades'] if t['pnl'] > 0)
        total_losses = abs(sum(t['pnl'] for t in trades_data[client_id]['trades'] if t['pnl'] <= 0))
        summary['profit_factor'] = total_wins / total_losses if total_losses > 0 else 0
        
        with open(trades_file, 'w', encoding='utf-8') as f:
            json.dump(trades_data, f, indent=2, ensure_ascii=False)
        
        # Update client stats
        clients_file = 'clients.json'
        if os.path.exists(clients_file):
            with open(clients_file, 'r', encoding='utf-8') as f:
                clients = json.load(f)
            
            if client_id in clients:
                clients[client_id]['total_trades'] = summary['total_trades']
                clients[client_id]['total_pnl'] = summary['total_pnl']
                
                with open(clients_file, 'w', encoding='utf-8') as f:
                    json.dump(clients, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        logger.error(f"Error adding client trade: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/accounts/all', methods=['GET'])
def get_all_accounts():
    """Get all accounts (both user profiles and client accounts)"""
    try:
        logger.info("🔄 Loading all accounts...")
        result = {
            'your_accounts': [],
            'client_accounts': []
        }
        
        # Load user profiles
        profiles_file = 'exchange_profiles.json'
        if os.path.exists(profiles_file):
            with open(profiles_file, 'r', encoding='utf-8') as f:
                profiles = json.load(f)
                
                logger.info(f"📂 Found {len(profiles)} profiles in exchange_profiles.json")
                
                for profile_name, profile_data in profiles.items():
                    # Skip special keys
                    if profile_name == 'active_profiles':
                        continue
                        
                    if profile_data.get('use_for_trading', False):
                        account = {
                            'id': f"profile_{profile_name}",
                            'name': profile_name,
                            'type': 'your_account',
                            'exchange': profile_data.get('exchange', ''),
                            'connected': profile_data.get('connected', False),
                            'display_info': profile_data.get('display_info', {})
                        }
                        result['your_accounts'].append(account)
                        logger.info(f"  ✅ Your account: {profile_name} ({profile_data.get('exchange', 'unknown')})")
        else:
            logger.warning(f"⚠️ {profiles_file} not found")
        
        # Load client accounts
        clients_file = 'clients.json'
        if os.path.exists(clients_file):
            with open(clients_file, 'r', encoding='utf-8') as f:
                clients = json.load(f)
                
                logger.info(f"📂 Found {len(clients)} clients in clients.json")
                
                for client_id, client_data in clients.items():
                    if not client_data.get('active', True):
                        logger.info(f"  ⏭️ Skipping inactive client: {client_id}")
                        continue
                    
                    client_name = client_data.get('name', client_id)
                    exchange_profiles = client_data.get('exchange_profiles', {})
                    
                    logger.info(f"  👤 Client: {client_name} ({len(exchange_profiles)} profiles)")
                    
                    for profile_name, profile_data in exchange_profiles.items():
                        account = {
                            'id': f"client_{client_id}_{profile_name}",
                            'name': f"{client_name} - {profile_name}",
                            'type': 'client_account',
                            'client_id': client_id,
                            'client_name': client_name,
                            'profile_name': profile_name,
                            'exchange': profile_data.get('exchange', ''),
                            'connected': profile_data.get('connected', False),
                            'volume_multiplier': profile_data.get('volume_multiplier', 1.0),
                            'max_position_size': profile_data.get('max_position_size', 5),
                            'display_info': profile_data.get('display_info', {})
                        }
                        result['client_accounts'].append(account)
                        logger.info(f"    ✅ {profile_name} ({profile_data.get('exchange', 'unknown')})")
        else:
            logger.warning(f"⚠️ {clients_file} not found")
        
        logger.info(f"✅ Total accounts loaded: {len(result['your_accounts'])} yours + {len(result['client_accounts'])} clients")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"❌ Error getting all accounts: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# ==================== END CLIENT MANAGEMENT ROUTES ====================

# ==================== ENGINE CONFIGS ROUTES ====================
@app.route('/api/get-engine-configs', methods=['GET'])
def get_engine_configs():
    """Get saved engine configurations"""
    try:
        # Check if config file exists
        config_file = 'strategies/engine_configs.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                configs = json.load(f)
            return jsonify({'success': True, 'configs': configs})
        else:
            # Return empty configs
            return jsonify({'success': True, 'configs': {}})
    except Exception as e:
        logger.error(f"Error loading engine configs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save-engine-configs', methods=['POST'])
def save_engine_configs():
    """Save engine configurations"""
    try:
        configs = request.json
        config_file = 'strategies/engine_configs.json'
        with open(config_file, 'w') as f:
            json.dump(configs, f, indent=2)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error saving engine configs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
# ==================== END ENGINE CONFIGS ROUTES ====================

# ==================== TEST ROUTE ====================
@app.route('/test-header')
def test_header():
    """Test route to verify header_common.html loads correctly"""
    return render_template('test_header.html')
# ==================== END TEST ROUTE ====================

if __name__ == '__main__':
    # Start background price update
    socketio.start_background_task(update_price)
    socketio.run(app, host='0.0.0.0', port=5555, debug=True)
