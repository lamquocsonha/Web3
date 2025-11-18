"""
DNSE Exchange Client
Kết nối với sàn DNSE (Cổ phiếu + Phái sinh)
API Documentation: Contact DNSE Support
"""

import requests
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class DNSEClient:
    """
    Client để kết nối với DNSE Exchange
    Hỗ trợ: Cổ phiếu, Phái sinh (Futures)
    """
    
    def __init__(self, environment="demo"):
        """
        Khởi tạo DNSE Client
        
        Args:
            environment: "demo" or "real" (DNSE không có demo, luôn là real)
        """
        self.token: Optional[str] = None
        self.trading_token: Optional[str] = None
        self.environment = environment
        self.base_url = "https://api.dnse.com.vn"
        self.session = requests.Session()
        self.investor_id: Optional[str] = None
        
    def authenticate(self, username: str, password: str) -> bool:
        """
        Đăng nhập DNSE
        
        Args:
            username: Email hoặc số điện thoại
            password: Mật khẩu
            
        Returns:
            True nếu thành công
        """
        try:
            url = f"{self.base_url}/auth-service/login"
            payload = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get("token")
            
            if not self.token:
                raise ValueError("Token not found in response")
                
            logger.info("✅ DNSE authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ DNSE authentication failed: {e}")
            return False
    
    def request_otp(self) -> bool:
        """
        Yêu cầu mã OTP gửi về email
        
        Returns:
            True nếu OTP đã được gửi
        """
        try:
            url = f"{self.base_url}/auth-service/api/email-otp"
            headers = {
                "authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            logger.info("✅ OTP sent to email")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to request OTP: {e}")
            return False
    
    def get_trading_token(self, otp: str) -> bool:
        """
        Lấy trading token bằng mã OTP
        
        Args:
            otp: Mã OTP từ email
            
        Returns:
            True nếu thành công
        """
        try:
            url = f"{self.base_url}/order-service/trading-token"
            headers = {
                "authorization": f"Bearer {self.token}",
                "otp": otp
            }
            
            response = self.session.post(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.trading_token = data.get("tradingToken")
            
            if not self.trading_token:
                raise ValueError("Trading token not found in response")
                
            logger.info("✅ Trading token obtained")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to get trading token: {e}")
            return False
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin tài khoản nhà đầu tư
        
        Returns:
            Dictionary chứa thông tin tài khoản
        """
        try:
            url = f"{self.base_url}/user-service/api/me"
            headers = {
                "authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.investor_id = data.get("investorId")
            
            logger.info(f"✅ Account info retrieved: {data.get('fullName')}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to get account info: {e}")
            return None
    
    def get_investor_accounts(self) -> Optional[List[Dict[str, Any]]]:
        """
        Lấy danh sách các tiểu khoản
        
        Returns:
            List các tiểu khoản
        """
        try:
            url = f"{self.base_url}/order-service/accounts"
            headers = {
                "authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            accounts = data.get("accounts", [])
            
            logger.info(f"✅ Retrieved {len(accounts)} accounts")
            return accounts
            
        except Exception as e:
            logger.error(f"❌ Failed to get investor accounts: {e}")
            return None
    
    def get_account_balance(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy số dư tài khoản
        
        Args:
            account_id: ID tiểu khoản
            
        Returns:
            Dictionary chứa thông tin số dư
        """
        try:
            url = f"{self.base_url}/order-service/account-balances/{account_id}"
            headers = {
                "authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Balance retrieved for account {account_id}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to get account balance: {e}")
            return None
    
    def get_deals(self, account_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Lấy danh sách các deal đang mở
        
        Args:
            account_id: ID tiểu khoản
            
        Returns:
            List các deal
        """
        try:
            url = f"{self.base_url}/deal-service/deals"
            params = {
                "accountNo": account_id
            }
            headers = {
                "authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            deals = data.get("deals", [])
            
            logger.info(f"✅ Retrieved {len(deals)} deals")
            return deals
            
        except Exception as e:
            logger.error(f"❌ Failed to get deals: {e}")
            return None
    
    def close_deal(self, deal_id: str, account_id: str) -> bool:
        """
        Đóng deal
        
        Args:
            deal_id: ID của deal
            account_id: ID tiểu khoản
            
        Returns:
            True nếu thành công
        """
        try:
            url = f"{self.base_url}/order-service/v2/orders/{deal_id}"
            params = {
                "accountNo": account_id
            }
            headers = {
                "authorization": f"Bearer {self.token}",
                "trading-token": self.trading_token
            }
            
            response = self.session.post(url, params=params, headers=headers)
            response.raise_for_status()
            
            logger.info(f"✅ Deal {deal_id} closed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to close deal: {e}")
            return False
    
    def deposit_derivative(
        self, 
        deal_account_id: str,
        source_account_id: str,
        amount: float,
        via: str,
        loan_package_id: Optional[str] = None
    ) -> bool:
        """
        Nộp tiền ký quỹ vào tài khoản phái sinh
        
        Args:
            deal_account_id: Tài khoản phái sinh
            source_account_id: Tài khoản nguồn
            amount: Số tiền
            via: Phương thức chuyển
            loan_package_id: ID gói vay (optional)
            
        Returns:
            True nếu thành công
        """
        try:
            url = f"{self.base_url}/derivative-asset-service/deposit"
            headers = {
                "authorization": f"Bearer {self.token}",
                "trading-token": self.trading_token
            }
            payload = {
                "accountNo": deal_account_id,
                "sourceAccountNo": source_account_id,
                "amount": amount,
                "via": via
            }
            if loan_package_id:
                payload["loanPackageId"] = loan_package_id
            
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            logger.info(f"✅ Deposited {amount} to derivative account")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to deposit: {e}")
            return False
    
    def withdraw_derivative(
        self,
        deal_account_id: str,
        source_account_id: str,
        amount: float,
        via: str,
        loan_package_id: Optional[str] = None
    ) -> bool:
        """
        Rút tiền ký quỹ từ tài khoản phái sinh
        
        Args:
            deal_account_id: Tài khoản phái sinh
            source_account_id: Tài khoản đích
            amount: Số tiền
            via: Phương thức chuyển
            loan_package_id: ID gói vay (optional)
            
        Returns:
            True nếu thành công
        """
        try:
            url = f"{self.base_url}/derivative-asset-service/withdraw"
            headers = {
                "authorization": f"Bearer {self.token}",
                "trading-token": self.trading_token
            }
            payload = {
                "accountNo": deal_account_id,
                "sourceAccountNo": source_account_id,
                "amount": amount,
                "via": via
            }
            if loan_package_id:
                payload["loanPackageId"] = loan_package_id
            
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            logger.info(f"✅ Withdrew {amount} from derivative account")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to withdraw: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Kiểm tra xem đã authenticate chưa"""
        return self.token is not None
    
    def is_ready_to_trade(self) -> bool:
        """Kiểm tra xem đã sẵn sàng trade chưa"""
        return self.token is not None and self.trading_token is not None
    
    def disconnect(self):
        """Ngắt kết nối và clear tokens"""
        self.token = None
        self.trading_token = None
        self.investor_id = None
        self.session.close()
        logger.info("🔌 DNSE disconnected")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    client = DNSEClient()
    
    # Step 1: Authenticate
    success = client.authenticate("0919990540", "your_password")
    if not success:
        exit(1)
    
    # Step 2: Request OTP
    client.request_otp()
    
    # Step 3: Wait for user to enter OTP
    otp = input("Enter OTP from email: ")
    
    # Step 4: Get trading token
    success = client.get_trading_token(otp)
    if not success:
        exit(1)
    
    # Step 5: Get account info
    account_info = client.get_account_info()
    print(f"Logged in as: {account_info.get('fullName')}")
    
    # Ready to trade
    print(f"Ready to trade: {client.is_ready_to_trade()}")
    
    def get_historical_data(self, symbol: str, timeframe: str = '5m', limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Lấy dữ liệu lịch sử OHLC từ DNSE Chart API (Public - không cần auth)
        
        Args:
            symbol: Mã chứng khoán/phái sinh (VD: VN30F1M, HPG, VNM)
            timeframe: Khung thời gian ('1m', '5m', '15m', '30m', '1H', '4H', '1D')
            limit: Số lượng nến
            
        Returns:
            List các nến OHLC
        """
        try:
            # Xác định loại tài sản
            asset_type = "derivative" if len(symbol) > 3 else "stock"
            
            # Convert timeframe
            tf_map = {
                '1m': '1',
                '5m': '5', 
                '15m': '15',
                '30m': '30',
                '1H': '1H',
                '4H': '4H',
                '1D': '1D',
                '1W': '1W'
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
            
            # DNSE Public Chart API
            url = f"https://api.dnse.com.vn/chart-api/v2/ohlcs/{asset_type}"
            params = {
                'symbol': symbol,
                'from': from_time,
                'to': to_time,
                'resolution': resolution
            }
            
            logger.info(f"📡 DNSE Chart API: {asset_type} {symbol} {resolution} (limit={limit})")
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                candles = []
                
                # DNSE trả về format: {t: [], o: [], h: [], l: [], c: [], v: []}
                times = data.get('t', [])
                opens = data.get('o', [])
                highs = data.get('h', [])
                lows = data.get('l', [])
                closes = data.get('c', [])
                volumes = data.get('v', [])
                
                for i in range(len(times)):
                    candles.append({
                        'time': times[i],
                        'open': float(opens[i]),
                        'high': float(highs[i]),
                        'low': float(lows[i]),
                        'close': float(closes[i]),
                        'volume': float(volumes[i])
                    })
                
                logger.info(f"✅ Loaded {len(candles)} candles for {symbol} ({timeframe})")
                return candles
            else:
                logger.error(f"❌ Chart API failed: {response.status_code} - {response.text[:200]}")
                return []
                
        except Exception as e:
            logger.error(f"❌ get_historical_data error: {e}")
            import traceback
            traceback.print_exc()
            return []
