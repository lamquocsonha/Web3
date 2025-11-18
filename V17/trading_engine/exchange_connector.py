"""
Exchange Connector Module - Hỗ trợ đa sàn giao dịch
Binance Futures, MT5 (Forex/Gold), DNSE (Cổ phiếu + Phái sinh + OTP), Entrade (Phái sinh, không OTP)
"""

import os
import json
import time
import hmac
import hashlib
import requests
import base64
import ssl
from datetime import datetime
from typing import Dict, List, Optional, Any
import MetaTrader5 as mt5
import logging

logger = logging.getLogger(__name__)


class TickAggregator:
    """Aggregate tick data into OHLC candles"""
    
    def __init__(self, timeframe_seconds: int = 60):
        self.timeframe = timeframe_seconds
        self.current_candles = {}  # {symbol: {open, high, low, close, volume, start_time}}
        self.completed_candles = {}  # {symbol: [candles]}
    
    def add_tick(self, symbol: str, price: float, volume: float, timestamp: float) -> Optional[Dict]:
        """Add tick and return completed candle if any"""
        candle_start = int(timestamp // self.timeframe) * self.timeframe
        
        if symbol not in self.current_candles:
            self.current_candles[symbol] = {
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'volume': volume,
                'start_time': candle_start
            }
            return None
        
        candle = self.current_candles[symbol]
        
        # New candle period
        if candle_start > candle['start_time']:
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
            
            if len(self.completed_candles[symbol]) > 1000:
                self.completed_candles[symbol] = self.completed_candles[symbol][-1000:]
            
            # Start new candle
            self.current_candles[symbol] = {
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'volume': volume,
                'start_time': candle_start
            }
            
            return completed
        
        # Update current candle
        candle['high'] = max(candle['high'], price)
        candle['low'] = min(candle['low'], price)
        candle['close'] = price
        candle['volume'] += volume
        
        return None
    
    def get_candles(self, symbol: str, limit: int = 100) -> list:
        """Get completed candles"""
        if symbol not in self.completed_candles:
            return []
        return self.completed_candles[symbol][-limit:]


class TimeframeAggregator:
    """Aggregate lower timeframe candles into higher timeframes"""
    
    @staticmethod
    def aggregate(candles_1m: List[Dict], target_timeframe: str) -> List[Dict]:
        """
        Aggregate 1-minute candles into target timeframe
        
        Args:
            candles_1m: List of 1-minute OHLC candles
            target_timeframe: Target timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)
        
        Returns:
            List of aggregated OHLC candles
        """
        if not candles_1m:
            return []
        
        # Timeframe in minutes
        tf_minutes = {
            '1m': 1, 'M1': 1,
            '5m': 5, 'M5': 5,
            '15m': 15, 'M15': 15,
            '30m': 30, 'M30': 30,
            '1h': 60, 'H1': 60,
            '4h': 240, 'H4': 240,
            '1d': 1440, 'D1': 1440
        }
        
        target_minutes = tf_minutes.get(target_timeframe, 1)
        
        # If already 1m, return as is
        if target_minutes == 1:
            return candles_1m
        
        aggregated = []
        target_seconds = target_minutes * 60
        
        # Group candles by timeframe periods
        current_group = []
        current_period_start = None
        
        for candle in candles_1m:
            candle_time = candle['time']
            period_start = int(candle_time // target_seconds) * target_seconds
            
            if current_period_start is None:
                current_period_start = period_start
            
            if period_start == current_period_start:
                current_group.append(candle)
            else:
                # Aggregate current group
                if current_group:
                    agg_candle = TimeframeAggregator._aggregate_group(current_group, current_period_start)
                    aggregated.append(agg_candle)
                
                # Start new group
                current_group = [candle]
                current_period_start = period_start
        
        # Aggregate last group
        if current_group:
            agg_candle = TimeframeAggregator._aggregate_group(current_group, current_period_start)
            aggregated.append(agg_candle)
        
        return aggregated
    
    @staticmethod
    def _aggregate_group(candles: List[Dict], period_start: float) -> Dict:
        """Aggregate a group of candles into one"""
        return {
            'time': period_start,
            'open': candles[0]['open'],
            'high': max(c['high'] for c in candles),
            'low': min(c['low'] for c in candles),
            'close': candles[-1]['close'],
            'volume': sum(c['volume'] for c in candles)
        }


class ExchangeConnector:
    """Base class cho tất cả các sàn"""
    
    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        self.connected = False
        self.credentials = {}
        
    def connect(self, credentials: Dict) -> bool:
        """Kết nối tới sàn"""
        raise NotImplementedError
    
    def disconnect(self):
        """Ngắt kết nối"""
        raise NotImplementedError
    
    def get_account_info(self) -> Dict:
        """Lấy thông tin tài khoản"""
        raise NotImplementedError
    
    def get_positions(self) -> List[Dict]:
        """Lấy danh sách vị thế"""
        raise NotImplementedError
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: Optional[float] = None) -> Dict:
        """Đặt lệnh"""
        raise NotImplementedError
    
    def cancel_order(self, order_id: str) -> bool:
        """Hủy lệnh"""
        raise NotImplementedError
    
    def get_ticker(self, symbol: str) -> Dict:
        """Lấy giá hiện tại"""
        raise NotImplementedError


class BinanceConnector(ExchangeConnector):
    """Binance Futures Connector"""
    
    BASE_URL = "https://fapi.binance.com"
    
    def __init__(self):
        super().__init__("Binance")
        self.api_key = None
        self.api_secret = None
        
    def connect(self, credentials: Dict) -> bool:
        try:
            self.api_key = credentials.get('api_key')
            self.api_secret = credentials.get('api_secret')
            
            # Test connection
            response = self._request('GET', '/fapi/v2/account')
            if response:
                self.connected = True
                return True
            return False
        except Exception as e:
            logger.error(f"Binance connect error: {e}")
            return False
    
    def disconnect(self):
        self.connected = False
        self.api_key = None
        self.api_secret = None
    
    def _generate_signature(self, params: Dict) -> str:
        """Tạo chữ ký HMAC SHA256"""
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Gửi request tới Binance API"""
        if params is None:
            params = {}
        
        params['timestamp'] = int(time.time() * 1000)
        params['signature'] = self._generate_signature(params)
        
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, params=params, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, params=params, headers=headers, timeout=10)
            else:
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Binance API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
    
    def get_account_info(self) -> Dict:
        """Lấy thông tin tài khoản"""
        data = self._request('GET', '/fapi/v2/account')
        if data:
            return {
                'balance': float(data.get('totalWalletBalance', 0)),
                'equity': float(data.get('totalMarginBalance', 0)),
                'available': float(data.get('availableBalance', 0)),
                'positions_count': len([p for p in data.get('positions', []) if float(p.get('positionAmt', 0)) != 0])
            }
        return {}
    
    def get_positions(self) -> List[Dict]:
        """Lấy danh sách vị thế"""
        data = self._request('GET', '/fapi/v2/positionRisk')
        if data:
            positions = []
            for pos in data:
                amt = float(pos.get('positionAmt', 0))
                if amt != 0:
                    positions.append({
                        'symbol': pos.get('symbol'),
                        'side': 'LONG' if amt > 0 else 'SHORT',
                        'size': abs(amt),
                        'entry_price': float(pos.get('entryPrice', 0)),
                        'unrealized_pnl': float(pos.get('unRealizedProfit', 0)),
                        'leverage': int(pos.get('leverage', 1))
                    })
            return positions
        return []
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: Optional[float] = None) -> Dict:
        """Đặt lệnh"""
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': quantity
        }
        
        if order_type.upper() == 'LIMIT' and price:
            params['price'] = price
            params['timeInForce'] = 'GTC'
        
        data = self._request('POST', '/fapi/v1/order', params)
        if data:
            return {
                'order_id': data.get('orderId'),
                'status': data.get('status'),
                'symbol': data.get('symbol')
            }
        return {}
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Hủy lệnh"""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        data = self._request('DELETE', '/fapi/v1/order', params)
        return data is not None
    
    def get_ticker(self, symbol: str) -> Dict:
        """Lấy giá hiện tại"""
        try:
            url = f"{self.BASE_URL}/fapi/v1/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': data.get('symbol'),
                    'price': float(data.get('price', 0)),
                    'timestamp': int(time.time() * 1000)
                }
        except Exception as e:
            logger.error(f"Get ticker error: {e}")
        return {}


class MT5Connector(ExchangeConnector):
    """MetaTrader 5 Connector - Forex/Gold"""
    
    def __init__(self):
        super().__init__("MT5")
        self.broker = None
        
    def connect(self, credentials: Dict) -> bool:
        try:
            login = int(credentials.get('login', 0))
            password = credentials.get('password', '')
            server = credentials.get('server', '')
            self.broker = credentials.get('broker', 'Unknown')  # Exness, ICMarkets, etc.
            
            if not mt5.initialize():
                logger.error("MT5 initialize failed")
                return False
            
            authorized = mt5.login(login, password, server)
            if authorized:
                self.connected = True
                return True
            else:
                logger.error(f"MT5 login failed: {mt5.last_error()}")
                return False
        except Exception as e:
            logger.error(f"MT5 connect error: {e}")
            return False
    
    def disconnect(self):
        if self.connected:
            mt5.shutdown()
            self.connected = False
    
    def get_account_info(self) -> Dict:
        """Lấy thông tin tài khoản"""
        if not self.connected:
            return {}
        
        account_info = mt5.account_info()
        if account_info:
            return {
                'login': account_info.login,
                'broker': self.broker,
                'server': account_info.server,
                'balance': account_info.balance,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'free_margin': account_info.margin_free,
                'profit': account_info.profit,
                'leverage': account_info.leverage
            }
        return {}
    
    def get_positions(self) -> List[Dict]:
        """Lấy danh sách vị thế"""
        if not self.connected:
            return []
        
        positions = mt5.positions_get()
        if positions:
            result = []
            for pos in positions:
                result.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == 0 else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'profit': pos.profit,
                    'comment': pos.comment
                })
            return result
        return []
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: Optional[float] = None) -> Dict:
        """Đặt lệnh"""
        if not self.connected:
            return {}
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Symbol {symbol} not found")
            return {}
        
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                logger.error(f"Failed to select symbol {symbol}")
                return {}
        
        # Determine order type
        if side.upper() == 'BUY':
            order_type_mt5 = mt5.ORDER_TYPE_BUY if order_type.upper() == 'MARKET' else mt5.ORDER_TYPE_BUY_LIMIT
            price_value = mt5.symbol_info_tick(symbol).ask if price is None else price
        else:
            order_type_mt5 = mt5.ORDER_TYPE_SELL if order_type.upper() == 'MARKET' else mt5.ORDER_TYPE_SELL_LIMIT
            price_value = mt5.symbol_info_tick(symbol).bid if price is None else price
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL if order_type.upper() == 'MARKET' else mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": quantity,
            "type": order_type_mt5,
            "price": price_value,
            "deviation": 20,
            "magic": 234000,
            "comment": "Auto Trade",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return {
                'order': result.order,
                'volume': result.volume,
                'price': result.price,
                'comment': result.comment
            }
        else:
            logger.error(f"Order failed: {result.comment}")
            return {}
    
    def cancel_order(self, order_id: int) -> bool:
        """Hủy lệnh"""
        if not self.connected:
            return False
        
        request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": order_id,
        }
        
        result = mt5.order_send(request)
        return result.retcode == mt5.TRADE_RETCODE_DONE
    
    def get_ticker(self, symbol: str) -> Dict:
        """Lấy giá hiện tại"""
        if not self.connected:
            return {}
        
        tick = mt5.symbol_info_tick(symbol)
        if tick:
            return {
                'symbol': symbol,
                'bid': tick.bid,
                'ask': tick.ask,
                'last': tick.last,
                'time': tick.time
            }
        return {}


class DNSEConnector(ExchangeConnector):
    """DNSE Connector - Cổ phiếu cơ sở + Phái sinh (Có OTP Email)"""
    
    BASE_URL = "https://api.dnse.com.vn"
    
    def __init__(self):
        super().__init__("DNSE")
        self.jwt_token = None
        self.trading_token = None
        
    def connect(self, credentials: Dict) -> bool:
        """Kết nối DNSE - Chỉ verify OTP khi có code, không tự động request"""
        try:
            username = credentials.get('username')
            password = credentials.get('password')
            otp_code = credentials.get('otp')
            require_otp = credentials.get('require_otp', True)
            
            # Step 1: Login để lấy JWT token
            response = requests.post(
                f"{self.BASE_URL}/auth-service/login",
                json={'username': username, 'password': password},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"DNSE login failed: {response.text}")
                return False
                
            data = response.json()
            self.jwt_token = data.get('token')
            logger.info(f"✅ DNSE login successful, JWT token received")
            
            # Step 2: Nếu không cần OTP, kết nối thành công
            if not require_otp:
                self.connected = True
                logger.info(f"✅ DNSE connected without OTP")
                return True
            
            # Step 3: Nếu cần OTP nhưng chưa có code → Return False (frontend sẽ hiện modal)
            if not otp_code:
                logger.warning(f"⚠️ DNSE requires OTP but no code provided - need modal")
                return False
            
            # Step 4: Get trading token với OTP (OTP truyền qua HEADER theo API DNSE chính thức)
            headers = {
                'authorization': f'Bearer {self.jwt_token}',
                'otp': otp_code
            }
            otp_verify = requests.post(
                f"{self.BASE_URL}/order-service/trading-token",
                headers=headers,
                timeout=10
            )
            
            if otp_verify.status_code == 200:
                verify_data = otp_verify.json()
                self.trading_token = verify_data.get('tradingToken')
                self.connected = True
                logger.info(f"✅ DNSE connected with OTP successfully, trading token: {self.trading_token[:10]}...")
                return True
            else:
                logger.error(f"❌ OTP verify failed: {otp_verify.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ DNSE connect error: {e}")
            return False
    
    def disconnect(self):
        self.connected = False
        self.jwt_token = None
        self.trading_token = None
    
    def request_otp(self, username: str, password: str) -> Dict:
        """Request OTP qua EMAIL cho DNSE"""
        try:
            # Step 1: Login để lấy JWT token
            response = requests.post(
                f"{self.BASE_URL}/auth-service/login",
                json={'username': username, 'password': password},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"DNSE login failed: {response.text}")
                return {'success': False, 'error': f'Login failed: {response.status_code}'}
                
            data = response.json()
            jwt_token = data.get('token')
            
            if not jwt_token:
                return {'success': False, 'error': 'No JWT token received'}
            
            # Step 2: Request OTP qua EMAIL (API chính thức DNSE)
            headers = {
                'authorization': f'Bearer {jwt_token}',
                'Content-Type': 'application/json'
            }
            otp_response = requests.get(
                f"{self.BASE_URL}/auth-service/api/email-otp",
                headers=headers,
                timeout=10
            )
            
            if otp_response.status_code == 200:
                logger.info(f"✅ Email OTP sent successfully to {username}")
                return {'success': True, 'message': 'OTP đã được gửi qua Email (check hộp thư)'}
            else:
                logger.error(f"OTP request failed: {otp_response.text}")
                return {'success': False, 'error': f'OTP request failed: {otp_response.status_code}'}
                
        except Exception as e:
            logger.error(f"Request OTP error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_account_info(self) -> Dict:
        """Lấy thông tin tài khoản"""
        if not self.jwt_token:
            return {}
        
        try:
            headers = {'authorization': f'Bearer {self.jwt_token}'}
            response = requests.get(
                f"{self.BASE_URL}/user-service/api/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'account_id': data.get('id'),
                    'name': data.get('name'),
                    'email': data.get('email'),
                    'custody_code': data.get('custodyCode'),
                    'investor_id': data.get('investorId'),
                    'status': data.get('status')
                }
        except Exception as e:
            logger.error(f"Get account info error: {e}")
        return {}
    
    def get_positions(self) -> List[Dict]:
        """Lấy danh sách vị thế (phái sinh)"""
        if not self.jwt_token:
            return []
        
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            response = requests.get(
                f"{self.BASE_URL}/dnse-order-service/v2/positions",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                positions = []
                for pos in data.get('data', []):
                    positions.append({
                        'symbol': pos.get('symbol'),
                        'side': pos.get('side'),
                        'quantity': pos.get('quantity'),
                        'avg_price': pos.get('avgPrice'),
                        'unrealized_pnl': pos.get('unrealizedPnl')
                    })
                return positions
        except Exception as e:
            logger.error(f"Get positions error: {e}")
        return []
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: Optional[float] = None, 
                   account_no: str = None, asset_type: str = 'stock') -> Dict:
        """
        Đặt lệnh DNSE
        asset_type: 'stock' (cổ phiếu) hoặc 'derivative' (phái sinh)
        """
        if not self.trading_token:
            return {}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.jwt_token}',
                'trading-token': self.trading_token,
                'Content-Type': 'application/json'
            }
            
            order_data = {
                'symbol': symbol,
                'side': side.upper(),
                'orderType': order_type.upper(),
                'quantity': int(quantity)
            }
            
            if price:
                order_data['price'] = price
                
            if account_no:
                order_data['accountNo'] = account_no
            
            response = requests.post(
                f"{self.BASE_URL}/dnse-order-service/v2/orders",
                json=order_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'order_id': data.get('orderId'),
                    'status': data.get('status'),
                    'symbol': data.get('symbol')
                }
        except Exception as e:
            logger.error(f"Place order error: {e}")
        return {}
    
    def cancel_order(self, order_id: str) -> bool:
        """Hủy lệnh"""
        if not self.trading_token:
            return False
        
        try:
            headers = {
                'Authorization': f'Bearer {self.jwt_token}',
                'trading-token': self.trading_token
            }
            response = requests.delete(
                f"{self.BASE_URL}/dnse-order-service/v2/orders/{order_id}",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Cancel order error: {e}")
        return False
    
    def get_ticker(self, symbol: str) -> Dict:
        """Lấy giá hiện tại"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/dnse-market-service/api/quote/{symbol}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol,
                    'price': data.get('price', 0),
                    'change': data.get('change', 0),
                    'volume': data.get('volume', 0)
                }
        except Exception as e:
            logger.error(f"Get ticker error: {e}")
        return {}
    
    def get_historical_data(self, symbol: str, timeframe: str = 'M5', limit: int = 1000) -> List[Dict]:
        """Lấy dữ liệu lịch sử từ DNSE Chart API"""
        try:
            # Xác định loại tài sản: derivative (phái sinh) hoặc stock (cổ phiếu)
            asset_type = "derivative" if len(symbol) > 3 else "stock"
            
            # Convert timeframe: M1 → '1', M5 → '5', H1 → '1H', D1 → '1D'
            tf_map = {
                'M1': '1',
                'M5': '5',
                'M15': '15',
                'M30': '30',
                'H1': '1H',
                'H4': '4H',
                'D1': '1D',
                'W1': '1W'
            }
            resolution = tf_map.get(timeframe, '5')
            
            # Tính toán khoảng thời gian
            import time
            to_time = int(time.time())
            
            # Tính from_time dựa trên timeframe và limit
            seconds_per_candle = {
                '1': 60, '5': 300, '15': 900, '30': 1800,
                '1H': 3600, '4H': 14400, '1D': 86400, '1W': 604800
            }
            candle_seconds = seconds_per_candle.get(resolution, 300)
            from_time = to_time - (limit * candle_seconds)
            
            # DNSE Public Chart API (không cần authentication)
            url = f"{self.BASE_URL}/chart-api/v2/ohlcs/{asset_type}"
            params = {
                'symbol': symbol,
                'from': from_time,
                'to': to_time,
                'resolution': resolution
            }
            
            logger.info(f"📡 Calling DNSE Chart API: {asset_type} {symbol} {resolution} (limit={limit})")
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # API trả về format: {o: [...], h: [...], l: [...], c: [...], v: [...], t: [...]}
                times = data.get('t', [])
                opens = data.get('o', [])
                highs = data.get('h', [])
                lows = data.get('l', [])
                closes = data.get('c', [])
                volumes = data.get('v', [])
                
                if not times:
                    logger.warning(f"⚠️ No data returned from DNSE for {symbol}")
                    return []
                
                candles = []
                for i in range(len(times)):
                    candles.append({
                        'time': times[i],
                        'open': float(opens[i]),
                        'high': float(highs[i]),
                        'low': float(lows[i]),
                        'close': float(closes[i]),
                        'volume': float(volumes[i])
                    })
                
                logger.info(f"✅ DNSE loaded {len(candles)} candles for {symbol}")
                return candles
            else:
                logger.error(f"❌ DNSE API failed: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            logger.error(f"❌ Get historical data error: {e}")
            import traceback
            traceback.print_exc()
        
        return []


class DNSEPublicConnector(ExchangeConnector):
    """DNSE Public API Connector - Historical Data Only (NO Authentication Required)"""
    
    BASE_URL = "https://api.dnse.com.vn"
    
    def __init__(self):
        super().__init__("DNSE-Public")
        self.timezone = 'UTC'  # Default timezone
        self.gmt_offset = 0    # Default GMT offset
        
    def connect(self, credentials: Dict) -> bool:
        """Public API không cần authentication"""
        try:
            # Store timezone from credentials
            self.timezone = credentials.get('timezone', 'UTC')
            self.gmt_offset = credentials.get('gmt_offset', 0)
            
            # No authentication required for public API
            self.connected = True
            logger.info(f"✅ DNSE Public API connected (no auth required), timezone: {self.timezone} (GMT+{self.gmt_offset})")
            return True
        except Exception as e:
            logger.error(f"❌ DNSE Public connect error: {e}")
            return False
    
    def disconnect(self):
        self.connected = False
    
    def get_historical_data(self, symbol: str, timeframe: str = 'M5', limit: int = 1000) -> List[Dict]:
        """Lấy dữ liệu lịch sử từ Public API"""
        try:
            # Determine asset type from symbol
            # Phái sinh: VN30F1M, VN30F2M (>3 chars)
            # Cổ phiếu: VNM, FPT, HPG (<=3 chars)
            asset_type = "derivative" if len(symbol) > 3 else "stock"
            
            # Convert timeframe: M1 → '1', M5 → '5', H1 → '1H', D1 → '1D'
            tf_map = {
                'M1': '1',
                'M5': '5', 
                'M15': '15',
                'M30': '30',
                'H1': '1H',
                'H4': '4H',
                'D1': '1D',
                'W1': '1W'
            }
            resolution = tf_map.get(timeframe, '5')
            
            # Calculate time range
            import time
            to_time = int(time.time())
            
            # Calculate from_time based on timeframe and limit
            seconds_per_candle = {
                '1': 60,      # 1 minute
                '5': 300,     # 5 minutes
                '15': 900,    # 15 minutes
                '30': 1800,   # 30 minutes
                '1H': 3600,   # 1 hour
                '4H': 14400,  # 4 hours
                '1D': 86400,  # 1 day
                '1W': 604800  # 1 week
            }
            candle_seconds = seconds_per_candle.get(resolution, 300)
            from_time = to_time - (limit * candle_seconds)
            
            # Public API endpoint
            url = f"{self.BASE_URL}/chart-api/v2/ohlcs/{asset_type}"
            params = {
                'symbol': symbol,
                'from': from_time,
                'to': to_time,
                'resolution': resolution
            }
            
            logger.info(f"📡 Calling DNSE Public API: {asset_type} {symbol} {resolution}")
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # API returns: {o: [...], h: [...], l: [...], c: [...], v: [...], t: [...]}
                times = data.get('t', [])
                opens = data.get('o', [])
                highs = data.get('h', [])
                lows = data.get('l', [])
                closes = data.get('c', [])
                volumes = data.get('v', [])
                
                candles = []
                for i in range(len(times)):
                    candles.append({
                        'time': times[i],
                        'open': float(opens[i]),
                        'high': float(highs[i]),
                        'low': float(lows[i]),
                        'close': float(closes[i]),
                        'volume': float(volumes[i])
                    })
                
                logger.info(f"✅ DNSE Public API loaded {len(candles)} candles for {symbol}")
                return candles
            else:
                logger.error(f"❌ DNSE Public API failed: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            logger.error(f"❌ Get historical data error: {e}")
            import traceback
            traceback.print_exc()
        
        return []


class EntradeConnector(ExchangeConnector):
    """Entrade Connector - Chỉ Phái sinh (KHÔNG cần OTP)"""
    
    BASE_URL = "https://services.entrade.com.vn"
    
    def __init__(self):
        super().__init__("Entrade")
        self.jwt_token = None
        self.username = None
        self.is_demo = False  # Phân biệt Real/Demo
        
    def connect(self, credentials: Dict) -> bool:
        """Kết nối Entrade - KHÔNG cần OTP - Hỗ trợ Real/Demo"""
        try:
            self.username = credentials.get('username')
            password = credentials.get('password')
            self.is_demo = credentials.get('is_demo', False)  # Mặc định Real
            
            logger.info(f"🔐 Entrade connecting: username={self.username}")
            
            # Entrade API - KHÁC với DNSE API
            response = requests.post(
                f"{self.BASE_URL}/entrade-api/v2/auth",  # ← Entrade endpoint
                json={'username': self.username, 'password': password},
                timeout=10
            )
            
            logger.info(f"📡 Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get('token')
                self.connected = True
                account_type = "Demo" if self.is_demo else "Real"
                logger.info(f"✅ Entrade ({account_type}) connected: {self.username}")
                logger.info(f"🔑 JWT token received: {self.jwt_token[:20] if self.jwt_token else 'None'}...")
                return True
            else:
                logger.error(f"❌ Entrade login failed: status={response.status_code}")
                logger.error(f"❌ Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Entrade connect error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def disconnect(self):
        self.connected = False
        self.jwt_token = None
    
    def get_account_info(self) -> Dict:
        """Lấy thông tin tài khoản đầy đủ - Entrade API (theo SDK chính thức)"""
        if not self.jwt_token:
            logger.error("❌ No JWT token for get_account_info")
            return {}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.jwt_token}',
                'Content-Type': 'application/json'
            }
            
            # Xác định base_url theo môi trường
            api_base = f"{self.BASE_URL}/papertrade-entrade-api" if self.is_demo else f"{self.BASE_URL}/entrade-api"
            
            logger.info(f"🔑 Getting Entrade account info from {api_base}...")
            
            # 1. Lấy investorId từ /investors/_me (theo SDK chính thức)
            investor_id = None
            try:
                logger.info(f"📡 Getting investor info: {api_base}/investors/_me")
                response = requests.get(f"{api_base}/investors/_me", headers=headers, timeout=10)
                logger.info(f"📊 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    investor_info = response.json()
                    investor_id = investor_info.get('investorId')
                    logger.info(f"✅ Found investorId: {investor_id}")
                    logger.info(f"📄 Investor info: {investor_info}")
                else:
                    logger.error(f"❌ Failed to get investor info: {response.status_code} - {response.text}")
                    return {}
            except Exception as e:
                logger.error(f"❌ Error getting investor info: {e}")
                return {}
            
            if not investor_id:
                logger.error("❌ No investorId found")
                return {}
            
            # 2. Lấy balance từ /account_balances/{investorId}
            cash_balance = 0
            purchasing_power = 0
            try:
                logger.info(f"📡 Getting balance: {api_base}/account_balances/{investor_id}")
                response = requests.get(f"{api_base}/account_balances/{investor_id}", headers=headers, timeout=10)
                logger.info(f"📊 Balance response: {response.status_code}")
                
                if response.status_code == 200:
                    balance_data = response.json()
                    logger.info(f"💰 Balance data: {balance_data}")
                    
                    # Extract balance từ response - Entrade trả về nav và availableCash
                    cash_balance = balance_data.get('nav', balance_data.get('availableCash', 0))
                    purchasing_power = balance_data.get('availableCash', cash_balance)
                    
                    logger.info(f"✅ Balance: {cash_balance}, Power: {purchasing_power}")
                else:
                    logger.warning(f"⚠️ Balance error: {response.status_code} - {response.text[:200]}")
            except Exception as e:
                logger.warning(f"⚠️ Error getting balance: {e}")
            
            # 3. Lấy portfolios để có portfolio_id (nếu cần)
            portfolio_id = None
            try:
                logger.info(f"📡 Getting portfolios: {api_base}/investors/{investor_id}/derivative_margin_portfolios")
                response = requests.get(f"{api_base}/investors/{investor_id}/derivative_margin_portfolios", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    portfolios_data = response.json()
                    if portfolios_data.get('data') and len(portfolios_data['data']) > 0:
                        portfolio_id = portfolios_data['data'][0].get('id')
                        logger.info(f"✅ Found portfolio_id: {portfolio_id}")
            except Exception as e:
                logger.warning(f"⚠️ Error getting portfolios: {e}")
            
            # 4. Lấy deals từ /derivative/deals?investorId={investorId}
            deals = []
            try:
                logger.info(f"📡 Getting deals: {api_base}/derivative/deals?investorId={investor_id}")
                response = requests.get(
                    f"{api_base}/derivative/deals",
                    params={'investorId': investor_id, '_start': 0, '_end': 1000},
                    headers=headers,
                    timeout=10
                )
                logger.info(f"📊 Deals response: {response.status_code}")
                
                if response.status_code == 200:
                    deals_response = response.json()
                    deals_data = deals_response.get('data', deals_response) if isinstance(deals_response, dict) else deals_response
                    logger.info(f"📄 Deals data: {deals_data[:2] if deals_data else 'Empty'}")
                    
                    for deal in deals_data:
                        if deal.get('state') == 'OPEN':  # ← Check 'state' not 'status'
                            # Calculate unrealized PnL
                            pnl = deal.get('totalUnrealizedProfit', 0)
                            if pnl == 0:
                                # Fallback: use fixedNetProfit or calculate manually
                                pnl = deal.get('fixedNetProfit', 0)
                                if pnl == 0:
                                    # Manual calculation if needed
                                    entry_price = deal.get('averageCostPrice', 0)
                                    current_price = deal.get('costPrice', entry_price)
                                    quantity = deal.get('openQuantity', 0)
                                    side = deal.get('side', '')
                                    
                                    if entry_price and current_price and quantity:
                                        if side in ['NB', 'BUY']:  # LONG
                                            pnl = (current_price - entry_price) * quantity
                                        else:  # SHORT
                                            pnl = (entry_price - current_price) * quantity
                            
                            deals.append({
                                'symbol': deal.get('symbol', 'N/A'),
                                'side': 'LONG' if deal.get('side') in ['NB', 'BUY'] else 'SHORT',
                                'quantity': deal.get('openQuantity', deal.get('quantity', 0)),
                                'entry_price': deal.get('averageCostPrice', deal.get('avgPrice', 0)),
                                'unrealized_pnl': pnl,
                                'margin': deal.get('secure', deal.get('margin', 0))
                            })
                    
                    logger.info(f"✅ Got {len(deals)} open deals")
                else:
                    logger.warning(f"⚠️ Deals error: {response.status_code} - {response.text[:200]}")
            except Exception as e:
                logger.warning(f"⚠️ Error getting deals: {e}")
            
            # Tổng hợp thông tin
            result = {
                'account_id': investor_id,
                'account_type': 'Demo' if self.is_demo else 'Real',
                'username': self.username,
                'portfolio_id': portfolio_id,
                # Format chuẩn cho frontend
                'balance': cash_balance,           # Số dư (NAV)
                'equity': cash_balance,            # Vốn = NAV
                'available': purchasing_power,     # Khả dụng
                # Backward compatibility
                'cash_balance': cash_balance,
                'purchasing_power': purchasing_power,
                'debt': 0,
                'total_asset': cash_balance,
                'positions_count': len(deals),
                'positions': deals[:5] if len(deals) > 5 else deals,
                'status': 'Connected',
                'exchange': 'Entrade'
            }
            
            logger.info(f"✅ Final Entrade account info: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Get account info error: {e}")
            import traceback
            traceback.print_exc()
        return {}
    
    def get_positions(self) -> List[Dict]:
        """Lấy danh sách vị thế phái sinh - dùng Entrade API"""
        if not self.jwt_token:
            logger.error("❌ No JWT token for get_positions")
            return []
        
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            api_base = f"{self.BASE_URL}/papertrade-entrade-api" if self.is_demo else f"{self.BASE_URL}/entrade-api"
            
            # 1. Lấy investorId từ /investors/_me
            investor_id = None
            try:
                response = requests.get(f"{api_base}/investors/_me", headers=headers, timeout=10)
                if response.status_code == 200:
                    investor_id = response.json().get('investorId')
            except:
                pass
            
            if not investor_id:
                logger.warning("⚠️ No investorId found")
                return []
            
            # 2. Lấy deals từ /derivative/deals?investorId={investorId}
            logger.info(f"📡 Getting deals for investor: {investor_id}")
            response = requests.get(
                f"{api_base}/derivative/deals",
                params={'investorId': investor_id, '_start': 0, '_end': 1000},
                headers=headers,
                timeout=10
            )
            
            logger.info(f"📊 Deals response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                deals_data = data.get('data', []) if isinstance(data, dict) else data
                
                positions = []
                for deal in deals_data:
                    if deal.get('state') == 'OPEN':  # ← Check 'state' not 'status'
                        # Calculate unrealized PnL
                        pnl = deal.get('totalUnrealizedProfit', 0)
                        if pnl == 0:
                            # Fallback: use fixedNetProfit or calculate manually
                            pnl = deal.get('fixedNetProfit', 0)
                            if pnl == 0:
                                # Manual calculation if needed
                                entry_price = deal.get('averageCostPrice', 0)
                                current_price = deal.get('costPrice', entry_price)
                                quantity = deal.get('openQuantity', 0)
                                side = deal.get('side', '')
                                
                                if entry_price and current_price and quantity:
                                    if side in ['NB', 'BUY']:  # LONG
                                        pnl = (current_price - entry_price) * quantity
                                    else:  # SHORT
                                        pnl = (entry_price - current_price) * quantity
                        
                        positions.append({
                            'symbol': deal.get('symbol', 'N/A'),
                            'side': 'LONG' if deal.get('side') == 'NB' else 'SHORT',
                            'quantity': deal.get('openQuantity', 0),
                            'entry_price': deal.get('averageCostPrice', 0),
                            'current_price': deal.get('costPrice', 0),
                            'unrealized_pnl': pnl,
                            'margin': deal.get('secure', 0)
                        })
                
                logger.info(f"✅ Got {len(positions)} open positions")
                return positions
                    
        except Exception as e:
            logger.error(f"❌ Get positions error: {e}")
            import traceback
            traceback.print_exc()
        
        return []
    
    def get_orders(self) -> List[Dict]:
        """Lấy sổ lệnh đang chờ và lịch sử - dùng Entrade API"""
        if not self.jwt_token:
            logger.warning("No JWT token for get_orders")
            return []
        
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            api_base = f"{self.BASE_URL}/papertrade-entrade-api" if self.is_demo else f"{self.BASE_URL}/entrade-api"
            
            # Lấy investorId từ /investors/_me
            investor_id = None
            try:
                response = requests.get(f"{api_base}/investors/_me", headers=headers, timeout=10)
                if response.status_code == 200:
                    investor_id = response.json().get('investorId')
            except:
                pass
            
            if not investor_id:
                return []
            
            # Lấy orders từ /derivative/orders?investorId={investorId}
            logger.info(f"Getting orders for investor: {investor_id}")
            response = requests.get(
                f"{api_base}/derivative/orders",
                params={
                    'investorId': investor_id,
                    '_order': 'DESC',
                    '_sort': 'createdDate',
                    '_start': 0,
                    '_end': 100
                },
                headers=headers,
                timeout=10
            )
            
            logger.info(f"Orders response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                orders_data = data.get('data', []) if isinstance(data, dict) else data
                
                orders = []
                for order in orders_data[:50]:
                    orders.append({
                        'order_id': order.get('id', order.get('orderNo', 'N/A')),
                        'symbol': order.get('symbol', 'N/A'),
                        'side': order.get('side', 'N/A'),
                        'order_type': order.get('orderType', 'N/A'),
                        'quantity': order.get('quantity', 0),
                        'price': order.get('price', 0),
                        'filled': order.get('filledQty', order.get('filledQuantity', 0)),
                        'status': order.get('orderStatus', order.get('status', 'N/A')),
                        'time': order.get('createdDate', 'N/A')
                    })
                
                logger.info(f"✅ Got {len(orders)} orders")
                return orders
            
        except Exception as e:
            logger.error(f"Get orders error: {e}")
        return []
    
    def get_deals(self) -> List[Dict]:
        """Lấy danh sách deal/giao dịch - dùng Entrade API"""
        if not self.jwt_token:
            logger.warning("No JWT token for get_deals")
            return []
        
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            api_base = f"{self.BASE_URL}/papertrade-entrade-api" if self.is_demo else f"{self.BASE_URL}/entrade-api"
            
            # Lấy investorId từ /investors/_me
            investor_id = None
            try:
                response = requests.get(f"{api_base}/investors/_me", headers=headers, timeout=10)
                if response.status_code == 200:
                    investor_id = response.json().get('investorId')
            except:
                pass
            
            if not investor_id:
                return []
            
            # Lấy deals từ /derivative/deals?investorId={investorId}
            logger.info(f"Getting deals for investor: {investor_id}")
            response = requests.get(
                f"{api_base}/derivative/deals",
                params={'investorId': investor_id, '_start': 0, '_end': 1000},
                headers=headers,
                timeout=10
            )
            
            logger.info(f"Deals response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                deals_data = data.get('data', []) if isinstance(data, dict) else data
                
                deals = []
                for deal in deals_data[:50]:
                    deals.append({
                        'deal_id': deal.get('id', 'N/A'),
                        'symbol': deal.get('symbol', 'N/A'),
                        'side': deal.get('side', 'N/A'),
                        'quantity': deal.get('accumulateQuantity', deal.get('quantity', 0)),
                        'price': deal.get('averageCostPrice', 0),
                        'time': deal.get('createdDate', 'N/A'),
                        'status': deal.get('status', 'N/A')
                    })
                
                logger.info(f"✅ Got {len(deals)} deals")
                return deals
            
        except Exception as e:
            logger.error(f"Get deals error: {e}")
        return []
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: Optional[float] = None) -> Dict:
        """Đặt lệnh phái sinh Entrade - dùng Entrade API"""
        if not self.jwt_token:
            logger.error("❌ No JWT token for place_order")
            return {}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.jwt_token}',
                'Content-Type': 'application/json'
            }
            api_base = f"{self.BASE_URL}/papertrade-entrade-api" if self.is_demo else f"{self.BASE_URL}/entrade-api"
            
            # 1. Lấy investorId từ /investors/_me
            response = requests.get(f"{api_base}/investors/_me", headers=headers, timeout=10)
            if response.status_code != 200:
                logger.error(f"❌ Failed to get investor info: {response.status_code}")
                return {}
            
            investor_id = response.json().get('investorId')
            if not investor_id:
                logger.error("❌ No investorId found")
                return {}
            
            # 2. Lấy portfolio_id từ /investors/{investorId}/derivative_margin_portfolios
            response = requests.get(
                f"{api_base}/investors/{investor_id}/derivative_margin_portfolios",
                headers=headers,
                timeout=10
            )
            
            portfolio_id = None
            if response.status_code == 200:
                portfolios = response.json()
                if portfolios.get('data') and len(portfolios['data']) > 0:
                    portfolio_id = portfolios['data'][0].get('id')
            
            if not portfolio_id:
                logger.error("❌ No portfolio_id found")
                return {}
            
            # 3. Đặt lệnh qua /derivative/orders
            # Note: Real environment cần trading-token (OTP), Demo không cần
            order_data = {
                'bankMarginPortfolioId': portfolio_id,
                'investorId': investor_id,
                'symbol': symbol,
                'side': side.upper(),  # NB = Buy, NS = Sell
                'orderType': order_type.upper(),  # LO, MP, etc.
                'quantity': int(quantity)
            }
            
            if price:
                order_data['price'] = price
            
            logger.info(f"📤 Placing order: {order_data}")
            
            response = requests.post(
                f"{api_base}/derivative/orders",
                json=order_data,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"📊 Place order response: {response.status_code} - {response.text[:200]}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Order placed successfully: {data}")
                return {
                    'order_id': data.get('id', data.get('orderId')),
                    'status': data.get('status', data.get('orderStatus'))
                }
            else:
                logger.error(f"❌ Place order failed: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Place order error: {e}")
            import traceback
            traceback.print_exc()
        return {}
    
    def cancel_order(self, order_id: str) -> bool:
        """Hủy lệnh - dùng Entrade API"""
        if not self.jwt_token:
            logger.error("❌ No JWT token for cancel_order")
            return False
        
        try:
            headers = {
                'Authorization': f'Bearer {self.jwt_token}'
            }
            api_base = f"{self.BASE_URL}/papertrade-entrade-api" if self.is_demo else f"{self.BASE_URL}/entrade-api"
            
            # Note: Real environment cần trading-token (OTP), Demo không cần
            logger.info(f"🗑️ Canceling order: {order_id}")
            
            response = requests.delete(
                f"{api_base}/derivative/orders/{order_id}",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"📊 Cancel order response: {response.status_code} - {response.text[:200]}")
            
            if response.status_code == 200:
                logger.info(f"✅ Order {order_id} canceled successfully")
                return True
            else:
                logger.error(f"❌ Cancel order failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Cancel order error: {e}")
            import traceback
            traceback.print_exc()
        return False
    
    def get_ticker(self, symbol: str) -> Dict:
        """Lấy giá hiện tại"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/dnse-market-service/api/quote/{symbol}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol,
                    'price': data.get('price', 0),
                    'change': data.get('change', 0)
                }
        except Exception as e:
            logger.error(f"Get ticker error: {e}")
        return {}
    
    def get_historical_data(self, symbol: str, timeframe: str = 'M5', limit: int = 1000) -> List[Dict]:
        """Lấy dữ liệu lịch sử phái sinh"""
        logger.info(f"📊 EntradeConnector.get_historical_data called: symbol={symbol}, tf={timeframe}, limit={limit}")
        
        if not self.jwt_token:
            logger.error(f"❌ No jwt_token available!")
            return []
        
        logger.info(f"✅ jwt_token available: {self.jwt_token[:20]}...")
        
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            
            # Convert timeframe to minutes
            tf_map = {'M1': 1, 'M5': 5, 'M15': 15, 'M30': 30, 'H1': 60, 'H4': 240, 'D1': 1440}
            interval = tf_map.get(timeframe, 5)
            
            # Try Entrade-specific endpoint first
            url = f"{self.BASE_URL}/entrade-market-service/api/chart/{symbol}"
            params = {'interval': interval, 'limit': limit}
            
            logger.info(f"🔗 Calling Entrade Market API: {url}")
            logger.info(f"📦 Params: {params}")
            
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"📡 Response status: {response.status_code}")
            
            # If Entrade endpoint fails, fallback to DNSE endpoint
            if response.status_code != 200:
                logger.warning(f"⚠️ Entrade endpoint failed, trying DNSE endpoint...")
                url = f"{self.BASE_URL}/dnse-market-service/api/chart/{symbol}"
                logger.info(f"🔗 Fallback to: {url}")
                
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=30
                )
                logger.info(f"📡 Fallback response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"📊 Response data keys: {list(data.keys())}")
                logger.info(f"📊 Data length: {len(data.get('data', []))}")
                
                candles = []
                
                for item in data.get('data', []):
                    candles.append({
                        'time': item.get('time', 0) // 1000,  # Convert ms to seconds
                        'open': float(item.get('open', 0)),
                        'high': float(item.get('high', 0)),
                        'low': float(item.get('low', 0)),
                        'close': float(item.get('close', 0)),
                        'volume': float(item.get('volume', 0))
                    })
                
                logger.info(f"✅ Entrade loaded {len(candles)} candles for {symbol}")
                return candles
            else:
                logger.error(f"❌ API returned status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            logger.error(f"❌ Get historical data error: {e}")
            import traceback
            traceback.print_exc()
        return []


class DNSEMQTTConnector(ExchangeConnector):
    """DNSE MQTT WebSocket Connector - Realtime Market Data"""
    
    BASE_URL = "https://services.entrade.com.vn"
    MQTT_HOST = "datafeed-lts.dnse.com.vn"
    MQTT_PORT = 443
    MQTT_PATH = "/wss"
    
    def __init__(self):
        super().__init__("DNSE-MQTT")
        self.mqtt_client = None
        self.jwt_token = None
        self.investor_id = None
        self.subscribed_symbols = []
        self.market_data = {}  # Store realtime data: {symbol: {price, volume, ...}}
        self.ohlc_data = {}    # Store OHLC data: {symbol: [{time, open, high, low, close, volume}]}
        self.tickers = []      # List of tickers to subscribe
        self.tick_aggregator = TickAggregator(timeframe_seconds=60)  # 1-minute candles from ticks
        
    def connect(self, credentials: Dict) -> bool:
        """Kết nối MQTT WebSocket"""
        try:
            import paho.mqtt.client as mqtt
            import random
            
            username = credentials.get('username')
            password = credentials.get('password')
            tickers_str = credentials.get('tickers', '')
            
            # Parse tickers to subscribe
            self.tickers = [t.strip() for t in tickers_str.split(',') if t.strip()] if tickers_str else []
            logger.info(f"📋 Will subscribe to: {self.tickers}")
            
            # Step 1: Login to get JWT token
            logger.info(f"🔐 DNSE MQTT: Login for {username}")
            response = requests.post(
                f"{self.BASE_URL}/dnse-auth-service/login",
                json={'username': username, 'password': password},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Login failed: {response.text}")
                return False
            
            data = response.json()
            self.jwt_token = data.get('token')
            
            # Step 2: Get investor ID from JWT token (không cần API riêng)
            logger.info(f"📋 Extracting investor ID from JWT token...")
            
            # Method 1: Check if login response contains investorId
            self.investor_id = data.get('investorId') or data.get('investor_id')
            
            if self.investor_id:
                logger.info(f"✅ Got investor ID from login response: {self.investor_id}")
            else:
                # Method 2: Decode JWT token to extract investorId
                try:
                    import base64
                    import json
                    
                    # JWT format: header.payload.signature
                    payload_part = self.jwt_token.split('.')[1]
                    
                    # Add padding if needed
                    padding = 4 - len(payload_part) % 4
                    if padding != 4:
                        payload_part += '=' * padding
                    
                    # Decode base64
                    decoded = base64.b64decode(payload_part)
                    jwt_data = json.loads(decoded)
                    
                    # Extract investorId (có thể là 'sub', 'investorId', 'investor_id', 'userId')
                    self.investor_id = (
                        jwt_data.get('investorId') or 
                        jwt_data.get('investor_id') or
                        jwt_data.get('sub') or 
                        jwt_data.get('userId')
                    )
                    
                    if self.investor_id:
                        logger.info(f"✅ Got investor ID from JWT: {self.investor_id}")
                    else:
                        logger.error(f"❌ No investor ID in JWT payload. Keys: {list(jwt_data.keys())}")
                        # Fallback to username
                        self.investor_id = username
                        logger.warning(f"⚠️ Using username as investor ID: {self.investor_id}")
                        
                except Exception as e:
                    logger.error(f"❌ Could not decode JWT: {e}")
                    # Fallback to username
                    self.investor_id = username
                    logger.warning(f"⚠️ Using username as investor ID: {self.investor_id}")
            
            # Step 3: Connect MQTT with MQTTv5
            client_id = f"dnse-price-json-mqtt-ws-sub-{random.randint(1000, 2000)}"
            logger.info(f"🔌 Connecting MQTT: {self.MQTT_HOST}:{self.MQTT_PORT}")
            
            # Create MQTT client with MQTTv5
            self.mqtt_client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id,
                protocol=mqtt.MQTTv5,
                transport="websockets"
            )
            
            # Set credentials (investorId as username, JWT token as password)
            self.mqtt_client.username_pw_set(str(self.investor_id), self.jwt_token)
            
            # SSL/TLS configuration for wss://
            self.mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
            self.mqtt_client.tls_insecure_set(True)
            
            # Callbacks (MQTTv5 format)
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_message = self._on_message
            self.mqtt_client.on_disconnect = self._on_disconnect
            
            # Enable logging for debugging (optional)
            # self.mqtt_client.enable_logger()
            
            # WebSocket path
            self.mqtt_client.ws_set_options(path=self.MQTT_PATH)
            
            # Connect to broker
            self.mqtt_client.connect(self.MQTT_HOST, self.MQTT_PORT, keepalive=1200)
            self.mqtt_client.loop_start()
            
            self.connected = True
            logger.info(f"✅ DNSE MQTT connected")
            return True
            
        except Exception as e:
            logger.error(f"❌ DNSE MQTT connect error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _on_connect(self, client, userdata, flags, rc, properties):
        """MQTTv5 connection callback"""
        if rc == 0 and client.is_connected():
            logger.info(f'✅ DNSE MQTT Connected successfully')
            # Auto-subscribe to tickers
            if self.tickers:
                for symbol in self.tickers:
                    self.subscribe_symbol(symbol, 'tick')
                    self.subscribe_symbol(symbol, 'stockinfo')
                    self.subscribe_symbol(symbol, 'ohlc_1m')  # Subscribe to 1m OHLC for historical data
                logger.info(f'📊 Subscribed to {len(self.tickers)} symbols (tick + stockinfo + ohlc_1m)')
        else:
            logger.error(f"❌ MQTT Connection failed with code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            
            # DNSE tick data format: matchPrice, matchQtty, side, sendingTime
            if 'matchPrice' in payload:
                symbol = payload.get('symbol', '')
                match_price = float(payload.get('matchPrice', 0))
                match_quantity = int(payload.get('matchQtty', 0))
                side = payload.get('side', '')
                sending_time = payload.get('sendingTime', '')
                
                logger.debug(f"📊 {symbol}: {match_price} - Qty: {match_quantity} - Side: {side}")
                
                # Update market data
                if symbol:
                    if symbol not in self.market_data:
                        self.market_data[symbol] = {}
                    
                    self.market_data[symbol].update({
                        'symbol': symbol,
                        'price': match_price,
                        'last_qty': match_quantity,
                        'side': side,
                        'time': time.time(),
                        'sending_time': sending_time
                    })
                    
                    # Aggregate tick into OHLC candles
                    completed_candle = self.tick_aggregator.add_tick(
                        symbol, 
                        match_price, 
                        match_quantity, 
                        time.time()
                    )
                    
                    # If candle completed, add to ohlc_data
                    if completed_candle:
                        if symbol not in self.ohlc_data:
                            self.ohlc_data[symbol] = []
                        self.ohlc_data[symbol].append(completed_candle)
                        if len(self.ohlc_data[symbol]) > 1000:
                            self.ohlc_data[symbol] = self.ohlc_data[symbol][-1000:]
                        logger.info(f"🕯️ DNSE: Completed 1m candle for {symbol}: O={completed_candle['open']:.2f} C={completed_candle['close']:.2f}")
            
            # Parse other message types
            message_type = payload.get('channel', payload.get('type', ''))
            
            if 'STOCK_INFO' in message_type or 'StockInfo' in str(payload):
                # Realtime price data
                data = payload.get('data', payload)
                symbol = data.get('s') or data.get('symbol')
                if symbol:
                    self.market_data[symbol] = {
                        'symbol': symbol,
                        'price': data.get('lastPrice', data.get('c', 0)),
                        'open': data.get('open', data.get('o', 0)),
                        'high': data.get('high', data.get('h', 0)),
                        'low': data.get('low', data.get('l', 0)),
                        'volume': data.get('totalVol', data.get('v', 0)),
                        'change': data.get('change', 0),
                        'changePercent': data.get('changePercent', 0),
                        'bid': data.get('bidPrice', data.get('b', 0)),
                        'ask': data.get('askPrice', data.get('a', 0)),
                        'time': data.get('time', time.time())
                    }
                    logger.debug(f"📊 {symbol}: ${self.market_data[symbol]['price']}")
            
            elif 'OHLC' in message_type or 'ohlc' in msg.topic:
                # OHLC candle data
                data = payload.get('data', payload)
                symbol = data.get('s') or data.get('symbol')
                if symbol:
                    if symbol not in self.ohlc_data:
                        self.ohlc_data[symbol] = []
                    
                    candle = {
                        'time': data.get('time', data.get('t', time.time())),
                        'open': data.get('open', data.get('o', 0)),
                        'high': data.get('high', data.get('h', 0)),
                        'low': data.get('low', data.get('l', 0)),
                        'close': data.get('close', data.get('c', 0)),
                        'volume': data.get('volume', data.get('v', 0))
                    }
                    
                    # Keep only last 1000 candles
                    self.ohlc_data[symbol].append(candle)
                    if len(self.ohlc_data[symbol]) > 1000:
                        self.ohlc_data[symbol] = self.ohlc_data[symbol][-1000:]
                    
                    logger.debug(f"🕯️ {symbol} OHLC: C={candle['close']}")
            
        except Exception as e:
            logger.error(f"❌ Error processing MQTT message: {e}")
            logger.error(f"   Raw message: {msg.payload[:200] if len(msg.payload) > 0 else 'empty'}")
    
    def _on_disconnect(self, client, userdata, rc):
        logger.warning(f"⚠️ DNSE MQTT Disconnected with code: {rc}")
        if rc == 5:
            logger.error(f"❌ Code 5 = Authorization failed - Check investorId/JWT token")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        logger.info(f"✅ DNSE subscription confirmed: mid={mid}, qos={granted_qos}")
    
    def _on_log(self, client, userdata, level, buf):
        logger.debug(f"🐛 DNSE MQTT: {buf}")
    
    def disconnect(self):
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        self.connected = False
        logger.info(f"🔌 DNSE MQTT disconnected")
    
    def subscribe_symbol(self, symbol: str, data_type: str = 'tick'):
        """Subscribe to DNSE symbol data via MQTT"""
        if not self.mqtt_client or not self.connected:
            return False
        
        # DNSE/Entrade MQTT topic format: plaintext/quotes/krx/mdds/{type}/...
        topic_map = {
            'tick': f'plaintext/quotes/krx/mdds/tick/v1/roundlot/symbol/{symbol}',
            'stockinfo': f'plaintext/quotes/krx/mdds/stockinfo/v1/roundlot/symbol/{symbol}',
            
            # Derivative OHLC (VN30F1M, VN30F2M, etc) - v2 API
            'ohlc_1m': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/1/{symbol}',
            'ohlc_3m': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/3/{symbol}',
            'ohlc_5m': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/5/{symbol}',
            'ohlc_15m': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/15/{symbol}',
            'ohlc_30m': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/30/{symbol}',
            'ohlc_1h': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/1H/{symbol}',
            'ohlc_1d': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/1D/{symbol}',
            'ohlc_1w': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/W/{symbol}',
            
            # Stock OHLC (HPG, VNM, FPT, etc) - v2 API
            'ohlc_stock_1m': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/1/{symbol}',
            'ohlc_stock_3m': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/3/{symbol}',
            'ohlc_stock_5m': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/5/{symbol}',
            'ohlc_stock_15m': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/15/{symbol}',
            'ohlc_stock_30m': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/30/{symbol}',
            'ohlc_stock_1h': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/1H/{symbol}',
            'ohlc_stock_1d': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/1D/{symbol}',
            'ohlc_stock_1w': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/W/{symbol}'
        }
        
        topic = topic_map.get(data_type, topic_map['tick'])
        self.mqtt_client.subscribe(topic, qos=1)
        
        if symbol not in self.subscribed_symbols:
            self.subscribed_symbols.append(symbol)
        
        logger.info(f"📊 DNSE subscribed to {topic}")
        return True
    
    def get_account_info(self) -> Dict:
        return {
            'investor_id': self.investor_id,
            'protocol': 'MQTT WebSocket',
            'status': 'Connected' if self.connected else 'Disconnected'
        }
    
    def get_positions(self) -> List[Dict]:
        return []  # MQTT is for market data only
    
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: Optional[float] = None) -> Dict:
        return {'success': False, 'error': 'MQTT connector không hỗ trợ trading'}
    
    def cancel_order(self, order_id: str) -> bool:
        return False
    
    def get_ticker(self, symbol: str) -> Dict:
        """Return latest realtime data from MQTT"""
        if symbol in self.market_data:
            return self.market_data[symbol]
        return {}
    
    def get_historical_data(self, symbol: str, timeframe: str = '1m', limit: int = 1000) -> List[Dict]:
        """
        Return OHLC data từ MQTT stream or tick aggregation
        Supports multi-timeframe: 1m, 5m, 15m, 30m, 1h, 4h, 1d
        Priority: 1) Existing OHLC data, 2) Aggregated from ticks, 3) Subscribe and wait
        """
        import time
        
        # Always get 1m base data first
        candles_1m = []
        
        # Check if we already have OHLC data (from MQTT or aggregation)
        if symbol in self.ohlc_data and len(self.ohlc_data[symbol]) > 0:
            logger.info(f"✅ DNSE: Using existing OHLC data: {len(self.ohlc_data[symbol])} candles")
            candles_1m = self.ohlc_data[symbol]
        else:
            # Try to get from tick aggregator
            aggregated = self.tick_aggregator.get_candles(symbol, limit * 60)  # Get more 1m for aggregation
            if aggregated and len(aggregated) > 0:
                logger.info(f"✅ DNSE: Using tick-aggregated candles: {len(aggregated)} candles")
                # Copy to ohlc_data for future use
                self.ohlc_data[symbol] = aggregated
                candles_1m = aggregated
            else:
                # If no data, subscribe and wait for ticks
                logger.info(f"📊 DNSE: No OHLC data for {symbol}, subscribing to ticks and waiting...")
                
                # Subscribe if not already subscribed
                if symbol not in self.subscribed_symbols:
                    self.subscribe_symbol(symbol, 'tick')
                    self.subscribe_symbol(symbol, 'stockinfo')
                
                # Also try OHLC subscription (may or may not work)
                self.subscribe_symbol(symbol, 'ohlc_1m')
                
                # Wait up to 10 seconds for data to arrive (ticks or OHLC)
                max_wait = 10
                wait_interval = 0.5
                waited = 0
                
                logger.info(f"⏳ DNSE: Waiting up to {max_wait}s for data...")
                
                while waited < max_wait:
                    time.sleep(wait_interval)
                    waited += wait_interval
                    
                    # Check OHLC data
                    if symbol in self.ohlc_data and len(self.ohlc_data[symbol]) > 0:
                        logger.info(f"✅ DNSE: Received {len(self.ohlc_data[symbol])} OHLC candles")
                        candles_1m = self.ohlc_data[symbol]
                        break
                    
                    # Check aggregated ticks
                    aggregated = self.tick_aggregator.get_candles(symbol, limit * 60)
                    if aggregated and len(aggregated) > 0:
                        logger.info(f"✅ DNSE: Built {len(aggregated)} candles from ticks")
                        self.ohlc_data[symbol] = aggregated
                        candles_1m = aggregated
                        break
        
        # If no 1m data available
        if not candles_1m:
            logger.warning(f"⚠️ DNSE: No data received for {symbol}")
            logger.info(f"💡 DNSE: Tip - Make sure symbol format is correct (e.g., VN30F1M or 41I1F7000)")
            return []
        
        # Aggregate to target timeframe
        if timeframe.upper() in ['1M', '1m']:
            result = candles_1m[-limit:]
        else:
            logger.info(f"🔄 DNSE: Aggregating {len(candles_1m)} 1m candles to {timeframe}")
            aggregated = TimeframeAggregator.aggregate(candles_1m, timeframe)
            logger.info(f"✅ DNSE: Generated {len(aggregated)} {timeframe} candles")
            result = aggregated[-limit:]
        
        return result



class EntradeMQTTConnector(ExchangeConnector):
    """Entrade MQTT WebSocket Connector - Realtime Market Data (KRX)"""
    
    BASE_URL = "https://services.entrade.com.vn"
    MQTT_HOST = "datafeed-lts-krx.dnse.com.vn"
    MQTT_PORT = 443
    MQTT_PATH = "/wss"
    
    def __init__(self):
        super().__init__("Entrade-MQTT")
        self.mqtt_client = None
        self.jwt_token = None
        self.investor_id = None
        self.subscribed_symbols = []
        self.market_data = {}
        self.ohlc_data = {}
        self.tickers = []
        self.tick_aggregator = TickAggregator(timeframe_seconds=60)  # 1-minute candles from ticks
        
    def connect(self, credentials: Dict) -> bool:
        """Kết nối MQTT WebSocket"""
        try:
            import paho.mqtt.client as mqtt
            import random
            
            username = credentials.get('username')
            password = credentials.get('password')
            tickers_str = credentials.get('tickers', '')
            
            # Parse tickers to subscribe
            self.tickers = [t.strip() for t in tickers_str.split(',') if t.strip()] if tickers_str else []
            logger.info(f"📋 Will subscribe to KRX: {self.tickers}")
            
            # Step 1: Login to get JWT token (MQTT dùng DNSE auth service chung)
            logger.info(f"🔐 Entrade MQTT: Login for {username}")
            response = requests.post(
                f"{self.BASE_URL}/dnse-auth-service/login",
                json={'username': username, 'password': password},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Login failed: {response.text}")
                return False
            
            data = response.json()
            self.jwt_token = data.get('token')
            
            # Step 2: Get investor ID (dùng DNSE auth service endpoint)
            logger.info(f"📋 Getting investor ID...")
            account_response = requests.get(
                f"{self.BASE_URL}/dnse-auth-service/account",
                headers={'Authorization': f'Bearer {self.jwt_token}'},
                timeout=10
            )
            
            if account_response.status_code == 200:
                account_data = account_response.json()
                self.investor_id = account_data.get('investorId', username)
                logger.info(f"✅ Investor ID: {self.investor_id}")
            else:
                logger.error(f"❌ Failed to get investor ID: {account_response.status_code}")
                logger.error(f"   Response: {account_response.text[:200]}")
                # Try to use username as fallback
                self.investor_id = username
                logger.warning(f"⚠️ Using username as investor ID: {self.investor_id}")
            
            # Step 3: Connect MQTT with MQTTv5
            client_id = f"entrade-price-json-mqtt-ws-sub-{random.randint(1000, 2000)}"
            logger.info(f"🔌 Connecting MQTT: {self.MQTT_HOST}:{self.MQTT_PORT}")
            
            # Create MQTT client with MQTTv5
            self.mqtt_client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id,
                protocol=mqtt.MQTTv5,
                transport="websockets"
            )
            
            # Set credentials (investorId as username, JWT token as password)
            self.mqtt_client.username_pw_set(str(self.investor_id), self.jwt_token)
            
            # SSL/TLS configuration for wss://
            self.mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
            self.mqtt_client.tls_insecure_set(True)
            
            # Callbacks (MQTTv5 format)
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_message = self._on_message
            self.mqtt_client.on_disconnect = self._on_disconnect
            
            # Enable logging for debugging (optional)
            # self.mqtt_client.enable_logger()
            
            # WebSocket path
            self.mqtt_client.ws_set_options(path=self.MQTT_PATH)
            
            # Connect to broker
            self.mqtt_client.connect(self.MQTT_HOST, self.MQTT_PORT, keepalive=1200)
            self.mqtt_client.loop_start()
            
            self.connected = True
            logger.info(f"✅ Entrade MQTT connected")
            return True
            
        except Exception as e:
            logger.error(f"❌ Entrade MQTT connect error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _on_connect(self, client, userdata, flags, rc, properties):
        """MQTTv5 connection callback"""
        if rc == 0 and client.is_connected():
            logger.info(f"✅ Entrade MQTT Connected successfully")
            # Auto-subscribe to tickers
            if self.tickers:
                for symbol in self.tickers:
                    self.subscribe_symbol(symbol, 'tick')
                    self.subscribe_symbol(symbol, 'stockinfo')
                    self.subscribe_symbol(symbol, 'ohlc_1m')  # Subscribe to 1m OHLC for historical data
                logger.info(f'📊 Subscribed to {len(self.tickers)} KRX symbols (tick + stockinfo + ohlc_1m)')
        else:
            logger.error(f"❌ MQTT Connection failed with code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages for KRX data"""
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            
            # KRX tick data format: matchPrice, matchQtty, side, sendingTime
            if 'matchPrice' in payload:
                symbol = payload.get('symbol', '')
                match_price = float(payload.get('matchPrice', 0))
                match_quantity = int(payload.get('matchQtty', 0))
                side = payload.get('side', '')
                sending_time = payload.get('sendingTime', '')
                
                logger.debug(f"📊 KRX {symbol}: {match_price} - Qty: {match_quantity} - Side: {side}")
                
                # Update market data
                if symbol:
                    if symbol not in self.market_data:
                        self.market_data[symbol] = {}
                    
                    self.market_data[symbol].update({
                        'symbol': symbol,
                        'price': match_price,
                        'last_qty': match_quantity,
                        'side': side,
                        'time': time.time(),
                        'sending_time': sending_time
                    })
                    
                    # Aggregate tick into OHLC candles
                    completed_candle = self.tick_aggregator.add_tick(
                        symbol, 
                        match_price, 
                        match_quantity, 
                        time.time()
                    )
                    
                    # If candle completed, add to ohlc_data
                    if completed_candle:
                        if symbol not in self.ohlc_data:
                            self.ohlc_data[symbol] = []
                        self.ohlc_data[symbol].append(completed_candle)
                        if len(self.ohlc_data[symbol]) > 1000:
                            self.ohlc_data[symbol] = self.ohlc_data[symbol][-1000:]
                        logger.info(f"🕯️ KRX: Completed 1m candle for {symbol}: O={completed_candle['open']:.2f} C={completed_candle['close']:.2f}")
            
            # Parse other message types
            message_type = payload.get('channel', payload.get('type', ''))
            
            if 'STOCK_INFO' in message_type or 'StockInfo' in str(payload):
                data = payload.get('data', payload)
                symbol = data.get('s') or data.get('symbol')
                if symbol:
                    self.market_data[symbol] = {
                        'symbol': symbol,
                        'price': data.get('lastPrice', data.get('c', 0)),
                        'open': data.get('open', data.get('o', 0)),
                        'high': data.get('high', data.get('h', 0)),
                        'low': data.get('low', data.get('l', 0)),
                        'volume': data.get('totalVol', data.get('v', 0)),
                        'change': data.get('change', 0),
                        'changePercent': data.get('changePercent', 0),
                        'bid': data.get('bidPrice', data.get('b', 0)),
                        'ask': data.get('askPrice', data.get('a', 0)),
                        'time': data.get('time', time.time())
                    }
                    logger.debug(f"📊 KRX {symbol}: ${self.market_data[symbol]['price']}")
            
            elif 'OHLC' in message_type or 'ohlc' in msg.topic:
                data = payload.get('data', payload)
                symbol = data.get('s') or data.get('symbol')
                if symbol:
                    if symbol not in self.ohlc_data:
                        self.ohlc_data[symbol] = []
                    
                    candle = {
                        'time': data.get('time', data.get('t', time.time())),
                        'open': data.get('open', data.get('o', 0)),
                        'high': data.get('high', data.get('h', 0)),
                        'low': data.get('low', data.get('l', 0)),
                        'close': data.get('close', data.get('c', 0)),
                        'volume': data.get('volume', data.get('v', 0))
                    }
                    
                    self.ohlc_data[symbol].append(candle)
                    if len(self.ohlc_data[symbol]) > 1000:
                        self.ohlc_data[symbol] = self.ohlc_data[symbol][-1000:]
                    
                    logger.debug(f"🕯️ KRX {symbol} OHLC: C={candle['close']}")
            
        except Exception as e:
            logger.error(f"❌ Error processing MQTT message: {e}")
            logger.error(f"   Raw message: {msg.payload[:200] if len(msg.payload) > 0 else 'empty'}")
    
    def _on_disconnect(self, client, userdata, rc):
        logger.warning(f"⚠️ Entrade MQTT Disconnected with code: {rc}")
        if rc == 5:
            logger.error(f"❌ Code 5 = Authorization failed - Check investorId/JWT token")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        logger.info(f"✅ Entrade subscription confirmed: mid={mid}, qos={granted_qos}")
    
    def _on_log(self, client, userdata, level, buf):
        logger.debug(f"🐛 Entrade MQTT: {buf}")
    
    def disconnect(self):
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        self.connected = False
        logger.info(f"🔌 Entrade MQTT disconnected")
    
    def subscribe_symbol(self, symbol: str, data_type: str = 'tick'):
        """Subscribe to KRX symbol data via MQTT"""
        if not self.mqtt_client or not self.connected:
            return False
        
        # KRX/Entrade MQTT topic format
        topic_map = {
            'tick': f'plaintext/quotes/krx/mdds/tick/v1/roundlot/symbol/{symbol}',
            'stockinfo': f'plaintext/quotes/krx/mdds/stockinfo/v1/roundlot/symbol/{symbol}',
            
            # Derivative OHLC (VN30F1M, VN30F2M, etc) - v2 API
            'ohlc_1m': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/1/{symbol}',
            'ohlc_3m': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/3/{symbol}',
            'ohlc_5m': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/5/{symbol}',
            'ohlc_15m': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/15/{symbol}',
            'ohlc_30m': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/30/{symbol}',
            'ohlc_1h': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/1H/{symbol}',
            'ohlc_1d': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/1D/{symbol}',
            'ohlc_1w': f'plaintext/quotes/krx/mdds/v2/ohlc/derivative/W/{symbol}',
            
            # Stock OHLC (HPG, VNM, FPT, etc) - v2 API  
            'ohlc_stock_1m': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/1/{symbol}',
            'ohlc_stock_3m': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/3/{symbol}',
            'ohlc_stock_5m': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/5/{symbol}',
            'ohlc_stock_15m': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/15/{symbol}',
            'ohlc_stock_30m': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/30/{symbol}',
            'ohlc_stock_1h': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/1H/{symbol}',
            'ohlc_stock_1d': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/1D/{symbol}',
            'ohlc_stock_1w': f'plaintext/quotes/krx/mdds/v2/ohlc/stock/W/{symbol}'
        }
        
        topic = topic_map.get(data_type, topic_map['tick'])
        self.mqtt_client.subscribe(topic, qos=1)
        
        if symbol not in self.subscribed_symbols:
            self.subscribed_symbols.append(symbol)
        
        logger.info(f"📊 Entrade/KRX subscribed to {topic}")
        return True
    
    def get_account_info(self) -> Dict:
        return {
            'investor_id': self.investor_id,
            'protocol': 'MQTT WebSocket (KRX)',
            'status': 'Connected' if self.connected else 'Disconnected'
        }
    
    def get_positions(self) -> List[Dict]:
        return []
    
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: Optional[float] = None) -> Dict:
        return {'success': False, 'error': 'MQTT connector không hỗ trợ trading'}
    
    def cancel_order(self, order_id: str) -> bool:
        return False
    
    def get_ticker(self, symbol: str) -> Dict:
        """Return latest realtime data from MQTT"""
        if symbol in self.market_data:
            return self.market_data[symbol]
        return {}
    
    def get_historical_data(self, symbol: str, timeframe: str = '1m', limit: int = 1000) -> List[Dict]:
        """
        Return OHLC data từ MQTT stream (KRX) or tick aggregation
        Supports multi-timeframe: 1m, 5m, 15m, 30m, 1h, 4h, 1d
        Priority: 1) Existing OHLC data, 2) Aggregated from ticks, 3) Subscribe and wait
        """
        import time
        
        # Always get 1m base data first
        candles_1m = []
        
        # Check if we already have OHLC data (from MQTT or aggregation)
        if symbol in self.ohlc_data and len(self.ohlc_data[symbol]) > 0:
            logger.info(f"✅ KRX: Using existing OHLC data: {len(self.ohlc_data[symbol])} candles")
            candles_1m = self.ohlc_data[symbol]
        else:
            # Try to get from tick aggregator
            aggregated = self.tick_aggregator.get_candles(symbol, limit * 60)  # Get more 1m for aggregation
            if aggregated and len(aggregated) > 0:
                logger.info(f"✅ KRX: Using tick-aggregated candles: {len(aggregated)} candles")
                # Copy to ohlc_data for future use
                self.ohlc_data[symbol] = aggregated
                candles_1m = aggregated
            else:
                # If no data, subscribe and wait for ticks
                logger.info(f"📊 KRX: No OHLC data for {symbol}, subscribing to ticks and waiting...")
                
                # Subscribe if not already subscribed
                if symbol not in self.subscribed_symbols:
                    self.subscribe_symbol(symbol, 'tick')
                    self.subscribe_symbol(symbol, 'stockinfo')
                
                # Also try OHLC subscription (may or may not work)
                self.subscribe_symbol(symbol, 'ohlc_1m')
                
                # Wait up to 10 seconds for data to arrive (ticks or OHLC)
                max_wait = 10
                wait_interval = 0.5
                waited = 0
                
                logger.info(f"⏳ KRX: Waiting up to {max_wait}s for data...")
                
                while waited < max_wait:
                    time.sleep(wait_interval)
                    waited += wait_interval
                    
                    # Check OHLC data
                    if symbol in self.ohlc_data and len(self.ohlc_data[symbol]) > 0:
                        logger.info(f"✅ KRX: Received {len(self.ohlc_data[symbol])} OHLC candles")
                        candles_1m = self.ohlc_data[symbol]
                        break
                    
                    # Check aggregated ticks
                    aggregated = self.tick_aggregator.get_candles(symbol, limit * 60)
                    if aggregated and len(aggregated) > 0:
                        logger.info(f"✅ KRX: Built {len(aggregated)} candles from ticks")
                        self.ohlc_data[symbol] = aggregated
                        candles_1m = aggregated
                        break
        
        # If no 1m data available
        if not candles_1m:
            logger.warning(f"⚠️ KRX: No data received for {symbol}")
            logger.info(f"💡 KRX: Tip - Make sure symbol format is correct (e.g., VN30F1M or 41I1F7000)")
            return []
        
        # Aggregate to target timeframe
        if timeframe.upper() in ['1M', '1m']:
            result = candles_1m[-limit:]
        else:
            logger.info(f"🔄 KRX: Aggregating {len(candles_1m)} 1m candles to {timeframe}")
            aggregated = TimeframeAggregator.aggregate(candles_1m, timeframe)
            logger.info(f"✅ KRX: Generated {len(aggregated)} {timeframe} candles")
            result = aggregated[-limit:]
        
        return result



class ExchangeManager:
    """Quản lý tất cả các kết nối sàn"""
    
    PROFILES_FILE = 'exchange_profiles.json'
    
    def __init__(self):
        self.connectors = {
            'binance': BinanceConnector(),
            'mt5': MT5Connector(),
            'dnse': DNSEConnector(),
            'entrade': EntradeConnector(),
            'dnse-mqtt': DNSEMQTTConnector(),
            'entrade-mqtt': EntradeMQTTConnector(),
            'dnse-public': DNSEPublicConnector()  # Public API - no auth
        }
        self.active_connections = {}
        self.profiles = self._load_profiles()
        
        # Track active profiles for different purposes
        self.active_data_profile = None  # Profile for loading chart data
        self.active_trading_profile = None  # Profile for placing orders
    
    def _load_profiles(self) -> Dict:
        """Load profiles từ file"""
        if os.path.exists(self.PROFILES_FILE):
            try:
                with open(self.PROFILES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Extract active_profiles if exists
                    if 'active_profiles' in data:
                        active = data.pop('active_profiles')
                        self.active_data_profile = active.get('data')
                        self.active_trading_profile = active.get('trading')
                        logger.info(f"📊 Restored active profiles - Data: {self.active_data_profile}, Trading: {self.active_trading_profile}")
                    return data
            except Exception as e:
                logger.error(f"Load profiles error: {e}")
        return {}
    
    def _save_profiles(self):
        """Lưu profiles vào file (bao gồm active_profiles)"""
        data = dict(self.profiles)
        # Add active profiles tracking
        data['active_profiles'] = {
            'data': self.active_data_profile,
            'trading': self.active_trading_profile,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Profiles saved with active tracking")
    
    def _encrypt_credentials(self, credentials: Dict) -> str:
        """Mã hóa credentials bằng base64"""
        json_str = json.dumps(credentials)
        encoded = base64.b64encode(json_str.encode()).decode()
        return encoded
    
    def _decrypt_credentials(self, encrypted: str) -> Dict:
        """Giải mã credentials từ base64"""
        decoded = base64.b64decode(encrypted.encode()).decode()
        return json.loads(decoded)
    
    def add_profile(self, profile_name: str, exchange: str, credentials: Dict) -> bool:
        """Thêm profile mới"""
        try:
            # Map protocol to exchange type
            protocol = credentials.get('protocol', 'rest')
            if protocol == 'mqtt':
                # Map to MQTT connector
                if exchange == 'dnse':
                    exchange = 'dnse-mqtt'
                elif exchange == 'entrade':
                    exchange = 'entrade-mqtt'
            elif protocol == 'public_rest':
                # Map to public API connector (DNSE only)
                if exchange == 'dnse':
                    exchange = 'dnse-public'
            
            encrypted = self._encrypt_credentials(credentials)
            
            # Lưu thông tin không mã hóa để dễ xem
            display_info = {}
            if exchange == 'mt5':
                display_info['server'] = credentials.get('server')
                display_info['broker'] = credentials.get('broker')
            elif exchange in ['dnse', 'entrade', 'dnse-mqtt', 'entrade-mqtt', 'dnse-public']:
                # Only show username for exchanges that require auth
                if exchange not in ['dnse-public']:
                    display_info['username'] = credentials.get('username')
                
                if protocol == 'mqtt':
                    display_info['protocol'] = 'MQTT WebSocket'
                elif protocol == 'public_rest':
                    display_info['protocol'] = 'Public REST API'
                else:
                    display_info['protocol'] = 'REST API'
            
            # Add timeframe to display info
            timeframe = credentials.get('timeframe', 'M1')
            display_info['timeframe'] = timeframe
            
            # Profile usage flags
            use_for_data = credentials.get('use_for_data', True)
            use_for_trading = credentials.get('use_for_trading', True)
            
            self.profiles[profile_name] = {
                'exchange': exchange,
                'credentials': encrypted,
                'display_info': display_info,
                'timeframe': timeframe,  # Store timeframe at profile level
                'use_for_data': use_for_data,  # Load chart data
                'use_for_trading': use_for_trading,  # Place orders
                'created_at': datetime.now().isoformat()
            }
            self._save_profiles()
            return True
        except Exception as e:
            logger.error(f"Add profile error: {e}")
            return False
    
    def remove_profile(self, profile_name: str) -> bool:
        """Xóa profile"""
        if profile_name in self.profiles:
            del self.profiles[profile_name]
            self._save_profiles()
            return True
        return False
    
    def get_profiles(self) -> List[Dict]:
        """Lấy danh sách profiles"""
        result = []
        for name, data in self.profiles.items():
            # Read connected state from JSON file first, fallback to in-memory state
            connected_from_file = data.get('connected', False)
            connected_from_memory = name in self.active_connections
            
            # Use file state if available, otherwise use memory state
            is_connected = connected_from_file or connected_from_memory
            
            # Log to debug startup disconnect issue (#1)
            if connected_from_file:
                logger.info(f"📊 Profile {name}: connected from file = {connected_from_file}")
            
            profile_data = {
                'name': name,
                'exchange': data.get('exchange'),
                'display_info': data.get('display_info', {}),
                'timeframe': data.get('timeframe', 'M1'),  # Include timeframe
                'timezone': data.get('timezone', 'UTC'),  # Include timezone
                'gmt_offset': data.get('gmt_offset', 0),  # Include GMT offset
                'use_for_data': data.get('use_for_data', True),  # Default true for backward compatibility
                'use_for_trading': data.get('use_for_trading', True),  # Default true for backward compatibility
                'created_at': data.get('created_at'),
                'connected': is_connected
            }
            result.append(profile_data)
        return result
    
    def get_profile_credentials(self, profile_name: str) -> Optional[Dict]:
        """Lấy credentials đã giải mã"""
        if profile_name not in self.profiles:
            return None
        
        try:
            profile = self.profiles[profile_name]
            credentials = self._decrypt_credentials(profile['credentials'])
            return credentials
        except Exception as e:
            logger.error(f"Get profile credentials error: {e}")
            return None
    
    def connect_profile(self, profile_name: str, otp_code: Optional[str] = None) -> Dict:
        """Kết nối profile - Hỗ trợ OTP cho DNSE"""
        logger.info(f"🔌 Connecting profile: {profile_name}")
        
        if profile_name not in self.profiles:
            logger.error(f"❌ Profile not found: {profile_name}")
            logger.info(f"📋 Available profiles: {list(self.profiles.keys())}")
            return {'success': False, 'error': 'Profile không tồn tại'}
        
        profile = self.profiles[profile_name]
        exchange = profile['exchange']
        
        logger.info(f"📊 Profile details: exchange={exchange}")
        
        if exchange not in self.connectors:
            logger.error(f"❌ Exchange not supported: {exchange}")
            return {'success': False, 'error': 'Sàn không được hỗ trợ'}
        
        try:
            credentials = self._decrypt_credentials(profile['credentials'])
            logger.info(f"🔑 Credentials decrypted, username: {credentials.get('username', 'N/A')}")
            
            # Thêm OTP code vào credentials nếu có
            if otp_code:
                credentials['otp'] = otp_code
                logger.info(f"🔐 OTP code added to credentials")
            
            connector = self.connectors[exchange]
            
            if connector.connect(credentials):
                self.active_connections[profile_name] = connector
                
                # Update connected state in JSON file
                if profile_name in self.profiles:
                    self.profiles[profile_name]['connected'] = True
                    self._save_profiles()
                    logger.info(f"💾 Updated connected state to True for: {profile_name}")
                
                logger.info(f"✅ Profile connected successfully: {profile_name}")
                return {'success': True, 'message': f'Đã kết nối {exchange}'}
            else:
                # Check if DNSE and needs OTP
                if exchange == 'dnse' and credentials.get('require_otp', True) and not otp_code:
                    logger.info(f"📧 DNSE requires OTP - returning needs_otp")
                    return {
                        'success': False, 
                        'needs_otp': True,
                        'profile_name': profile_name,
                        'username': credentials.get('username'),
                        'message': 'Cần OTP để kết nối DNSE'
                    }
                
                logger.error(f"❌ Connector.connect() returned False")
                return {'success': False, 'error': 'Kết nối thất bại'}
        except Exception as e:
            logger.error(f"❌ Connect profile error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def disconnect_profile(self, profile_name: str):
        """Ngắt kết nối profile"""
        if profile_name in self.active_connections:
            connector = self.active_connections[profile_name]
            connector.disconnect()
            del self.active_connections[profile_name]
            
            # Update connected state in JSON file
            if profile_name in self.profiles:
                self.profiles[profile_name]['connected'] = False
                self._save_profiles()
                logger.info(f"💾 Updated connected state to False for: {profile_name}")
    
    def get_connector(self, profile_name: str) -> Optional[ExchangeConnector]:
        """Lấy connector đang active"""
        return self.active_connections.get(profile_name)
    
    def test_connection(self, exchange: str, credentials: Dict) -> Dict:
        """Test kết nối mà không lưu profile"""
        if exchange not in self.connectors:
            return {'success': False, 'error': 'Sàn không được hỗ trợ'}
        
        try:
            connector = self.connectors[exchange]
            if connector.connect(credentials):
                account_info = connector.get_account_info()
                connector.disconnect()
                return {
                    'success': True,
                    'message': 'Kết nối thành công',
                    'account_info': account_info
                }
            else:
                return {'success': False, 'error': 'Kết nối thất bại'}
        except Exception as e:
            logger.error(f"Test connection error: {e}")
            return {'success': False, 'error': str(e)}
    
    def set_active_data_profile(self, profile_name: Optional[str]) -> Dict:
        """Set profile for loading chart data"""
        if profile_name and profile_name not in self.profiles:
            return {'success': False, 'error': 'Profile không tồn tại'}
        
        self.active_data_profile = profile_name
        self._save_profiles()  # Auto-save active profiles
        logger.info(f"📊 Active data profile set to: {profile_name or 'None'}")
        return {'success': True, 'active_data_profile': profile_name}
    
    def set_active_trading_profile(self, profile_name: Optional[str]) -> Dict:
        """Set profile for placing orders"""
        if profile_name and profile_name not in self.profiles:
            return {'success': False, 'error': 'Profile không tồn tại'}
        
        self.active_trading_profile = profile_name
        self._save_profiles()  # Auto-save active profiles
        logger.info(f"📈 Active trading profile set to: {profile_name or 'None'}")
        return {'success': True, 'active_trading_profile': profile_name}
    
    def get_active_profiles(self) -> Dict:
        """Get currently active profiles"""
        return {
            'active_data_profile': self.active_data_profile,
            'active_trading_profile': self.active_trading_profile
        }
    
    def can_trade(self) -> Dict:
        """Check if trading is available (has active trading profile with proper connection)"""
        if not self.active_trading_profile:
            return {'can_trade': False, 'reason': 'No active trading profile'}
        
        if self.active_trading_profile not in self.active_connections:
            return {'can_trade': False, 'reason': 'Trading profile not connected'}
        
        # Check if DNSE and has trading token
        profile = self.profiles.get(self.active_trading_profile)
        if profile and profile.get('exchange') == 'dnse':
            connector = self.active_connections[self.active_trading_profile]
            if not hasattr(connector, 'trading_token') or not connector.trading_token:
                return {'can_trade': False, 'reason': 'DNSE requires trading token (OTP needed)'}
        
        return {'can_trade': True, 'profile': self.active_trading_profile}


# Global instance
exchange_manager = ExchangeManager()
