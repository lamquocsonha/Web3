from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes for pages
@app.route('/')
def index():
    # Redirect to manual-trading as default page
    return redirect(url_for('manual_trading'))

@app.route('/manual-trading')
def manual_trading():
    return render_template('manual-trading.html')

@app.route('/bot-trading')
def bot_trading():
    return render_template('bot-trading.html')

@app.route('/strategy')
def strategy():
    return render_template('strategy.html')

@app.route('/backtest')
def backtest():
    return render_template('backtest.html')

@app.route('/optimize')
def optimize():
    return render_template('optimize.html')

@app.route('/hft')
def hft():
    return render_template('hft.html')

@app.route('/exchange')
def exchange():
    return render_template('exchange.html')

@app.route('/clients')
def clients():
    return render_template('clients.html')

@app.route('/test-modal')
def test_modal():
    return render_template('test-modal.html')

@app.route('/test-ema')
def test_ema():
    return render_template('test-ema.html')

@app.route('/debug-upload')
def debug_upload():
    return render_template('debug-upload.html')

# API endpoints for future development
@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    # TODO: Implement real market data fetching
    return jsonify({
        'symbol': 'VN30F1M',
        'price': 1892.00,
        'change': +0.50,
        'volume': 5781
    })

@app.route('/api/orders', methods=['GET', 'POST'])
def handle_orders():
    if request.method == 'POST':
        # TODO: Implement order placement
        order_data = request.json
        return jsonify({'status': 'success', 'order_id': '12345'})
    else:
        # TODO: Implement order listing
        return jsonify({'orders': []})

@app.route('/api/strategies', methods=['GET', 'POST'])
def handle_strategies():
    if request.method == 'POST':
        # TODO: Implement strategy saving
        strategy_data = request.json
        return jsonify({'status': 'success', 'strategy_id': '12345'})
    else:
        # TODO: Implement strategy listing
        return jsonify({'strategies': []})

@app.route('/api/backtest/run', methods=['POST'])
def run_backtest():
    # TODO: Implement backtest execution
    backtest_params = request.json
    return jsonify({
        'status': 'success',
        'results': {
            'net_profit': 0,
            'win_rate': 0,
            'total_trades': 0
        }
    })

@app.route('/api/optimize/run', methods=['POST'])
def run_optimization():
    # TODO: Implement optimization using genetic algorithm
    optimize_params = request.json
    return jsonify({
        'status': 'success',
        'results': []
    })

@app.route('/api/hft/start', methods=['POST'])
def start_hft():
    # TODO: Implement HFT start logic
    hft_params = request.json
    return jsonify({
        'status': 'success',
        'message': 'HFT started'
    })

@app.route('/api/hft/stop', methods=['POST'])
def stop_hft():
    # TODO: Implement HFT stop logic
    return jsonify({
        'status': 'success',
        'message': 'HFT stopped'
    })

@app.route('/api/hft/metrics', methods=['GET'])
def get_hft_metrics():
    # TODO: Implement real HFT metrics
    return jsonify({
        'orders': 0,
        'fill_rate': 0,
        'avg_latency': 0,
        'total_pnl': 0,
        'win_rate': 0
    })

@app.route('/api/exchange/profiles', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_exchange_profiles():
    # TODO: Implement exchange profile management
    if request.method == 'GET':
        return jsonify({'profiles': []})
    elif request.method == 'POST':
        profile_data = request.json
        return jsonify({'status': 'success', 'profile_id': '12345'})
    elif request.method == 'PUT':
        profile_data = request.json
        return jsonify({'status': 'success'})
    elif request.method == 'DELETE':
        profile_id = request.args.get('id')
        return jsonify({'status': 'success'})

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Get profiles filtered by type (data or trading)"""
    try:
        profile_type = request.args.get('type', 'all')  # 'data', 'trading', or 'all'
        
        # Mock data - in production, this would query from database
        mock_profiles = [
            {
                'id': '1',
                'name': 'DNSE Main Account',
                'exchange': 'DNSE',
                'use_for_data': True,
                'use_for_trading': True,
                'timeframe': '1m',
                'created_at': '2025-01-15 10:30:00'
            },
            {
                'id': '2',
                'name': 'Entrade Demo',
                'exchange': 'ENTRADE',
                'use_for_data': True,
                'use_for_trading': False,
                'timeframe': '5m',
                'created_at': '2025-01-16 14:20:00'
            },
            {
                'id': '3',
                'name': 'MT5 Demo Account',
                'exchange': 'MT5',
                'use_for_data': True,
                'use_for_trading': True,
                'timeframe': '15m',
                'created_at': '2025-01-17 09:15:00'
            },
            {
                'id': '4',
                'name': 'Binance Spot',
                'exchange': 'BINANCE',
                'use_for_data': True,
                'use_for_trading': True,
                'timeframe': '1m',
                'created_at': '2025-01-18 11:45:00'
            }
        ]
        
        # Filter by type
        filtered_profiles = []
        for profile in mock_profiles:
            if profile_type == 'all':
                filtered_profiles.append(profile)
            elif profile_type == 'data' and profile.get('use_for_data'):
                filtered_profiles.append(profile)
            elif profile_type == 'trading' and profile.get('use_for_trading'):
                filtered_profiles.append(profile)
        
        return jsonify({
            'status': 'success',
            'data': filtered_profiles,
            'count': len(filtered_profiles)
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/clients', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_clients():
    # TODO: Implement client management
    if request.method == 'GET':
        return jsonify({'clients': []})
    elif request.method == 'POST':
        client_data = request.json
        return jsonify({'status': 'success', 'client_id': '12345'})
    elif request.method == 'PUT':
        client_data = request.json
        return jsonify({'status': 'success'})
    elif request.method == 'DELETE':
        client_id = request.args.get('id')
        return jsonify({'status': 'success'})

# CSV Upload/Download endpoints
@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """Upload CSV file to server"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400

        file = request.files['file']

        # Check if file is selected
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400

        # Check file type
        if not allowed_file(file.filename):
            return jsonify({'status': 'error', 'message': 'Only CSV files are allowed'}), 400

        # Secure filename and add timestamp to make it unique
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{original_filename}"

        # Save file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Get file size
        file_size = os.path.getsize(filepath)
        file_size_mb = round(file_size / (1024 * 1024), 2)

        # Get additional metadata from form
        timeframe = request.form.get('timeframe', '1m')
        csv_utc = int(request.form.get('csv_utc', 7))

        return jsonify({
            'status': 'success',
            'filename': filename,
            'original_filename': original_filename,
            'file_size': file_size,
            'file_size_mb': file_size_mb,
            'timeframe': timeframe,
            'csv_utc': csv_utc,
            'message': 'File uploaded successfully'
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/get-csv/<filename>', methods=['GET'])
def get_csv(filename):
    """Download CSV file from server"""
    try:
        # Secure the filename
        safe_filename = secure_filename(filename)

        # Check if file exists
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404

        # Send file
        return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/list-csv', methods=['GET'])
def list_csv():
    """List all uploaded CSV files"""
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.endswith('.csv'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_size = os.path.getsize(filepath)
                file_size_mb = round(file_size / (1024 * 1024), 2)
                modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))

                files.append({
                    'filename': filename,
                    'size': file_size,
                    'size_mb': file_size_mb,
                    'modified': modified_time.strftime('%Y-%m-%d %H:%M:%S')
                })

        return jsonify({'status': 'success', 'files': files}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/delete-csv/<filename>', methods=['DELETE'])
def delete_csv(filename):
    """Delete CSV file from server"""
    try:
        safe_filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404

        os.remove(filepath)
        return jsonify({'status': 'success', 'message': 'File deleted successfully'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/resample-data', methods=['POST'])
def resample_data_api():
    """
    Resample OHLCV data to different timeframe
    Used for offline CSV data
    """
    try:
        from utils.timeframe_resampler import resample_data
        
        data = request.json
        raw_data = data.get('data')
        target_timeframe = data.get('timeframe', '5m')
        
        if not raw_data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Resample data
        resampled = resample_data(raw_data, target_timeframe)
        
        return jsonify({
            'status': 'success',
            'data': resampled,
            'timeframe': target_timeframe,
            'message': f'Resampled to {target_timeframe}'
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/connect-exchange', methods=['POST'])
def connect_exchange():
    """
    Connect to exchange and get historical data
    Used for online data from DNSE/Entrade
    """
    try:
        data = request.json
        exchange = data.get('exchange', '').lower()
        symbol = data.get('symbol')
        timeframe = data.get('timeframe', '5m')
        limit = data.get('limit', 1000)
        credentials = data.get('credentials', {})
        
        if not exchange or not symbol:
            return jsonify({
                'status': 'error',
                'message': 'Exchange and symbol are required'
            }), 400
        
        candles = []
        
        # Connect to DNSE
        if exchange == 'dnse':
            from exchanges.dnse_client import DNSEClient
            
            client = DNSEClient()
            
            # DNSE Chart API is public, no auth needed for data
            candles = client.get_historical_data(symbol, timeframe, limit)
            
        # Connect to Entrade
        elif exchange == 'entrade':
            from exchanges.entrade_client import EntradeClient
            
            username = credentials.get('username')
            password = credentials.get('password')
            is_demo = credentials.get('is_demo', False)
            
            if not username or not password:
                return jsonify({
                    'status': 'error',
                    'message': 'Username and password required for Entrade'
                }), 400
            
            client = EntradeClient(environment='demo' if is_demo else 'real')
            
            # Authenticate
            if not client.authenticate(username, password):
                return jsonify({
                    'status': 'error',
                    'message': 'Authentication failed'
                }), 401
            
            # Get historical data
            candles = client.get_historical_data(symbol, timeframe, limit)
            
        else:
            return jsonify({
                'status': 'error',
                'message': f'Unsupported exchange: {exchange}'
            }), 400
        
        if not candles:
            return jsonify({
                'status': 'error',
                'message': 'No data received from exchange'
            }), 404
        
        # Calculate date range
        start_date = datetime.fromtimestamp(candles[0]['time']).strftime('%Y-%m-%d %H:%M')
        end_date = datetime.fromtimestamp(candles[-1]['time']).strftime('%Y-%m-%d %H:%M')
        
        return jsonify({
            'status': 'success',
            'data': candles,
            'symbol': symbol,
            'timeframe': timeframe,
            'exchange': exchange.upper(),
            'start_date': start_date,
            'end_date': end_date,
            'total_candles': len(candles),
            'message': f'Loaded {len(candles)} candles from {exchange.upper()}'
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
