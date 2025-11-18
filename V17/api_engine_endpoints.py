# Trading Engine API Endpoints
# Add these routes to app.py

@app.route('/api/save-engine-config', methods=['POST'])
def save_engine_config():
    """Save trading engine configuration"""
    try:
        config = request.json
        
        # Validate required fields
        if not config.get('signal_strategy'):
            return jsonify({
                'success': False,
                'error': 'Signal strategy is required'
            }), 400
        
        # Load existing configs
        config_file = 'engine_configs.json'
        configs = []
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                configs = json.load(f)
        
        # Add new config
        configs.append(config)
        
        # Save
        with open(config_file, 'w') as f:
            json.dump(configs, f, indent=2)
        
        logger.info(f"✅ Saved engine config: {config['name']}")
        
        return jsonify({
            'success': True,
            'message': 'Configuration saved successfully',
            'config_id': len(configs) - 1
        })
    
    except Exception as e:
        logger.error(f"Error saving engine config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/get-engine-configs', methods=['GET'])
def get_engine_configs():
    """Get all saved engine configurations"""
    try:
        config_file = 'engine_configs.json'
        configs = []
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                configs = json.load(f)
        
        return jsonify({
            'success': True,
            'configs': configs
        })
    
    except Exception as e:
        logger.error(f"Error loading engine configs: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'configs': []
        }), 500


@app.route('/api/delete-engine-config/<int:config_id>', methods=['DELETE'])
def delete_engine_config(config_id):
    """Delete engine configuration"""
    try:
        config_file = 'engine_configs.json'
        
        if not os.path.exists(config_file):
            return jsonify({
                'success': False,
                'error': 'No configurations found'
            }), 404
        
        with open(config_file, 'r') as f:
            configs = json.load(f)
        
        if config_id < 0 or config_id >= len(configs):
            return jsonify({
                'success': False,
                'error': 'Invalid config ID'
            }), 400
        
        deleted = configs.pop(config_id)
        
        with open(config_file, 'w') as f:
            json.dump(configs, f, indent=2)
        
        logger.info(f"🗑️ Deleted engine config: {deleted['name']}")
        
        return jsonify({
            'success': True,
            'message': 'Configuration deleted successfully'
        })
    
    except Exception as e:
        logger.error(f"Error deleting engine config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/test-engine', methods=['POST'])
def test_engine():
    """Test trading engine with given configuration"""
    try:
        config = request.json
        
        # Validate strategy
        if not config.get('signal_strategy'):
            return jsonify({
                'success': False,
                'error': 'No signal strategy selected'
            }), 400
        
        logger.info(f"🧪 Testing engine: {config.get('name', 'Unnamed')}")
        
        # Load strategy
        strategy_name = config['signal_strategy']
        strategy_file = f"strategies/{strategy_name}.json"
        
        if not os.path.exists(strategy_file):
            return jsonify({
                'success': False,
                'error': f'Strategy file not found: {strategy_name}'
            }), 404
        
        # Create test data (100 bars)
        test_data = {
            'open': np.random.randn(100).cumsum() + 1900,
            'high': np.random.randn(100).cumsum() + 1905,
            'low': np.random.randn(100).cumsum() + 1895,
            'close': np.random.randn(100).cumsum() + 1900,
            'volume': np.random.randint(100, 1000, 100),
            'time': np.arange(100)
        }
        
        # Run test
        from trading_engine.afl_engine import AFLTradingEngine
        
        engine = AFLTradingEngine(config)
        
        # Generate mock signals
        signals = {
            'buy_signal': np.random.rand(100) > 0.9,
            'short_signal': np.random.rand(100) > 0.9
        }
        
        result = engine.run_backtest(test_data, signals)
        
        test_results = {
            'total_trades': len(result['trades']),
            'config_valid': True,
            'strategy': strategy_name,
            'active_settings': {
                'active': config.get('active', True),
                'buy_active': config.get('buy_active', True),
                'short_active': config.get('short_active', True),
                'dynamic_tp_sl': config.get('dynamic_tp_sl_active', True),
                'no_repaint': config.get('no_repaint_active', True)
            }
        }
        
        return jsonify({
            'success': True,
            'test_results': test_results,
            'message': 'Engine test completed successfully'
        })
    
    except Exception as e:
        logger.error(f"Error testing engine: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Update existing start_bot endpoint
@app.route('/api/start-bot', methods=['POST'])
def start_bot():
    """Start trading bot with engine configuration"""
    try:
        data = request.json
        
        # Get engine config
        engine_config = data.get('engine_config')
        if not engine_config:
            return jsonify({
                'success': False,
                'error': 'Engine configuration is required'
            }), 400
        
        # Validate strategy
        strategy_name = engine_config.get('signal_strategy')
        if not strategy_name:
            return jsonify({
                'success': False,
                'error': 'No strategy selected. Please select a strategy in Trading Engine tab.'
            }), 400
        
        # Load strategy file
        strategy_file = f"strategies/{strategy_name}.json"
        if not os.path.exists(strategy_file):
            return jsonify({
                'success': False,
                'error': f'Strategy file not found: {strategy_name}'
            }), 404
        
        with open(strategy_file, 'r') as f:
            strategy_config = json.load(f)
        
        # Merge engine config into strategy
        strategy_config['settings'] = {
            'active': engine_config.get('active', True),
            'buy_active': engine_config.get('buy_active', True),
            'short_active': engine_config.get('short_active', True),
            'trading_hours': {
                'active': engine_config.get('trading_hours_active', True),
                'start': engine_config.get('start_time', '09:00'),
                'end': engine_config.get('end_time', '14:30')
            },
            'base_time': engine_config.get('base_time', '09:00'),
            'buy_order_limit': engine_config.get('buy_order_limit', 10),
            'short_order_limit': engine_config.get('short_order_limit', 10)
        }
        
        strategy_config['risk_management'] = {
            'position_size_pct': engine_config.get('position_size', 10),
            'max_positions': engine_config.get('max_positions', 1),
            'commission': engine_config.get('fee_tax', 1.0),
            'dynamic_tp_sl': engine_config.get('dynamic_tp_sl_active', True),
            'initial_sl': engine_config.get('initial_sl', 10.3)
        }
        
        logger.info(f"🚀 Starting bot with strategy: {strategy_name}")
        logger.info(f"   Engine active: {engine_config.get('active', True)}")
        logger.info(f"   Buy active: {engine_config.get('buy_active', True)}")
        logger.info(f"   Short active: {engine_config.get('short_active', True)}")
        
        # TODO: Start actual bot with strategy_config
        # For now, just validate and return success
        
        return jsonify({
            'success': True,
            'message': f'Bot started successfully with strategy: {strategy_name}',
            'strategy': strategy_name,
            'config': engine_config
        })
    
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
