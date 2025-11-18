"""
Real-time Streaming Module
Streams MQTT data from DNSE/Entrade to WebSocket clients via Flask-SocketIO
"""

import logging
import time
import threading
from typing import Dict, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class RealtimeStreamer:
    """
    Real-time data streamer for MQTT exchanges
    Bridges MQTT data to Flask-SocketIO WebSocket
    """
    
    def __init__(self, socketio, exchange_manager):
        """
        Initialize streamer
        
        Args:
            socketio: Flask-SocketIO instance
            exchange_manager: ExchangeManager instance
        """
        self.socketio = socketio
        self.exchange_manager = exchange_manager
        
        # Streaming state
        self.active_streams = {}  # {profile_name: {symbol: thread}}
        self.stream_config = {}   # {profile_name: {symbols: [], interval: 0.1}}
        self.running = {}         # {profile_name: bool}
        
        logger.info("📡 RealtimeStreamer initialized")
    
    def start_stream(self, profile_name: str, symbols: list, interval: float = 0.1) -> Dict:
        """
        Start real-time streaming for a profile
        
        Args:
            profile_name: Profile name to stream
            symbols: List of symbols to stream
            interval: Update interval in seconds (default 0.1s = 100ms)
        
        Returns:
            Dict with success status and message
        """
        try:
            if profile_name in self.running and self.running[profile_name]:
                return {'success': False, 'error': 'Stream already running'}
            
            # Get connector
            connector = self.exchange_manager.get_connector(profile_name)
            if not connector:
                return {'success': False, 'error': 'Profile not connected'}
            
            # Check if it's MQTT connector
            if not hasattr(connector, 'mqtt_client'):
                return {'success': False, 'error': 'Profile is not MQTT-based'}
            
            # Subscribe to symbols
            for symbol in symbols:
                connector.subscribe_symbol(symbol, 'tick')
                connector.subscribe_symbol(symbol, 'stockinfo')
            
            # Store config
            self.stream_config[profile_name] = {
                'symbols': symbols,
                'interval': interval
            }
            
            # Start streaming thread
            self.running[profile_name] = True
            thread = threading.Thread(
                target=self._stream_worker,
                args=(profile_name, connector),
                daemon=True
            )
            thread.start()
            
            self.active_streams[profile_name] = thread
            
            logger.info(f"✅ Started streaming {profile_name}: {len(symbols)} symbols")
            return {
                'success': True,
                'message': f'Started streaming {len(symbols)} symbols',
                'symbols': symbols
            }
            
        except Exception as e:
            logger.error(f"❌ Start stream error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def stop_stream(self, profile_name: str) -> Dict:
        """
        Stop real-time streaming for a profile
        
        Args:
            profile_name: Profile name to stop
        
        Returns:
            Dict with success status
        """
        try:
            if profile_name not in self.running or not self.running[profile_name]:
                return {'success': False, 'error': 'Stream not running'}
            
            # Stop thread
            self.running[profile_name] = False
            
            # Wait for thread to finish
            if profile_name in self.active_streams:
                thread = self.active_streams[profile_name]
                if thread.is_alive():
                    thread.join(timeout=2)
                del self.active_streams[profile_name]
            
            # Clean up config
            if profile_name in self.stream_config:
                del self.stream_config[profile_name]
            
            logger.info(f"🛑 Stopped streaming {profile_name}")
            return {'success': True, 'message': 'Stream stopped'}
            
        except Exception as e:
            logger.error(f"❌ Stop stream error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _stream_worker(self, profile_name: str, connector):
        """
        Worker thread to stream data
        
        Args:
            profile_name: Profile name
            connector: MQTT connector instance
        """
        logger.info(f"🚀 Stream worker started for {profile_name}")
        
        config = self.stream_config[profile_name]
        symbols = config['symbols']
        interval = config['interval']
        
        # Initialize last update times
        last_tick_update = {symbol: 0 for symbol in symbols}
        last_candle_update = {symbol: 0 for symbol in symbols}
        
        while self.running.get(profile_name, False):
            try:
                current_time = time.time()
                
                for symbol in symbols:
                    # Stream tick data (high frequency)
                    if current_time - last_tick_update[symbol] >= interval:
                        ticker_data = connector.get_ticker(symbol)
                        if ticker_data:
                            self.socketio.emit('realtime_tick', {
                                'profile': profile_name,
                                'symbol': symbol,
                                'data': ticker_data,
                                'timestamp': datetime.now().isoformat()
                            })
                            last_tick_update[symbol] = current_time
                    
                    # Stream candle data (lower frequency - every 1 second)
                    if current_time - last_candle_update[symbol] >= 1.0:
                        candle_data = connector.get_historical_data(symbol, '1m', 100)
                        if candle_data:
                            self.socketio.emit('realtime_candle', {
                                'profile': profile_name,
                                'symbol': symbol,
                                'data': candle_data[-50:],  # Send last 50 candles
                                'timestamp': datetime.now().isoformat()
                            })
                            last_candle_update[symbol] = current_time
                
                # Sleep to control update frequency
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Stream worker error: {e}")
                time.sleep(1)  # Prevent rapid error loops
        
        logger.info(f"🛑 Stream worker stopped for {profile_name}")
    
    def get_active_streams(self) -> Dict:
        """
        Get list of active streams
        
        Returns:
            Dict with active streams info
        """
        result = {}
        for profile_name, running in self.running.items():
            if running:
                config = self.stream_config.get(profile_name, {})
                result[profile_name] = {
                    'symbols': config.get('symbols', []),
                    'interval': config.get('interval', 0.1),
                    'running': True
                }
        return result
    
    def stop_all_streams(self):
        """Stop all active streams"""
        profiles = list(self.running.keys())
        for profile_name in profiles:
            self.stop_stream(profile_name)
        logger.info("🛑 All streams stopped")


class TickAggregator:
    """
    Aggregates tick data into OHLC candles
    Useful for creating custom timeframe candles from tick data
    """
    
    def __init__(self, timeframe_seconds: int = 60):
        """
        Initialize aggregator
        
        Args:
            timeframe_seconds: Candle timeframe in seconds (default 60 = 1 minute)
        """
        self.timeframe = timeframe_seconds
        self.current_candles = {}  # {symbol: {open, high, low, close, volume, start_time}}
        self.completed_candles = {}  # {symbol: [candles]}
        
        logger.info(f"📊 TickAggregator initialized: {timeframe_seconds}s candles")
    
    def add_tick(self, symbol: str, price: float, volume: float, timestamp: float):
        """
        Add tick data and aggregate into candles
        
        Args:
            symbol: Trading symbol
            price: Tick price
            volume: Tick volume
            timestamp: Tick timestamp (unix)
        """
        # Calculate candle start time
        candle_start = int(timestamp // self.timeframe) * self.timeframe
        
        # Initialize candle if new
        if symbol not in self.current_candles:
            self.current_candles[symbol] = {
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'volume': volume,
                'start_time': candle_start,
                'count': 1
            }
            return None
        
        candle = self.current_candles[symbol]
        
        # Check if new candle period
        if candle_start > candle['start_time']:
            # Save completed candle
            completed = {
                'time': candle['start_time'],
                'open': candle['open'],
                'high': candle['high'],
                'low': candle['low'],
                'close': candle['close'],
                'volume': candle['volume']
            }
            
            if symbol not in self.completed_candles:
                self.completed_candles[symbol] = []
            self.completed_candles[symbol].append(completed)
            
            # Keep last 1000 candles
            if len(self.completed_candles[symbol]) > 1000:
                self.completed_candles[symbol] = self.completed_candles[symbol][-1000:]
            
            # Start new candle
            self.current_candles[symbol] = {
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'volume': volume,
                'start_time': candle_start,
                'count': 1
            }
            
            return completed
        
        # Update current candle
        candle['high'] = max(candle['high'], price)
        candle['low'] = min(candle['low'], price)
        candle['close'] = price
        candle['volume'] += volume
        candle['count'] += 1
        
        return None
    
    def get_candles(self, symbol: str, limit: int = 100) -> list:
        """
        Get completed candles for symbol
        
        Args:
            symbol: Trading symbol
            limit: Number of candles to return
        
        Returns:
            List of OHLC candles
        """
        if symbol not in self.completed_candles:
            return []
        return self.completed_candles[symbol][-limit:]
    
    def get_current_candle(self, symbol: str) -> Optional[Dict]:
        """
        Get current incomplete candle
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Current candle dict or None
        """
        if symbol not in self.current_candles:
            return None
        
        candle = self.current_candles[symbol]
        return {
            'time': candle['start_time'],
            'open': candle['open'],
            'high': candle['high'],
            'low': candle['low'],
            'close': candle['close'],
            'volume': candle['volume'],
            'incomplete': True
        }
