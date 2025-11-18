"""
Entrade Exchange Client
Kết nối với sàn Entrade (Phái sinh)
API Documentation: https://services.entrade.com.vn/docs
"""

import requests
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class EntradeClient:
    """
    Client để kết nối với Entrade Exchange
    Hỗ trợ: Phái sinh (Futures VN30)
    """
    
    REAL_BASE_URL = "https://services.entrade.com.vn/entrade-api"
    DEMO_BASE_URL = "https://services.entrade.com.vn/papertrade-entrade-api"
    AUTH_URL = "https://services.entrade.com.vn/entrade-api/v2/auth"
    
    def __init__(self, environment="demo"):
        """
        Khởi tạo Entrade Client
        
        Args:
            environment: "demo" hoặc "real"
        """
        self.environment = environment
        self.base_url = self.DEMO_BASE_URL if environment == "demo" else self.REAL_BASE_URL
        self.token: Optional[str] = None
        self.trading_token: Optional[str] = None
        self.session = requests.Session()
        self.investor_id: Optional[str] = None
        self.portfolio_id: Optional[str] = None
        
    def authenticate(self, username: str, password: str) -> bool:
        """
        Đăng nhập Entrade
        
        Args:
            username: Email hoặc số điện thoại
            password: Mật khẩu
            
        Returns:
            True nếu thành công
        """
        try:
            headers = {
                "accept": "*/*",
                "content-type": "application/json"
            }
            payload = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(self.AUTH_URL, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get("token")
            
            if not self.token:
                raise ValueError("Token not found in response")
                
            logger.info(f"✅ Entrade ({self.environment}) authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Entrade authentication failed: {e}")
            return False
    
    def request_otp(self) -> bool:
        """
        Yêu cầu mã OTP (chỉ cho Real account)
        Demo account không cần OTP
        
        Returns:
            True nếu OTP đã được gửi hoặc không cần (demo)
        """
        if self.environment == "demo":
            logger.info("📝 Demo environment: Skipping OTP")
            return True
            
        try:
            url = f"{self.base_url}/otp"
            headers = {
                "accept": "*/*",
                "authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            logger.info("✅ OTP sent")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to request OTP: {e}")
            return False
    
    def get_trading_token(self, otp_code: Optional[str] = None) -> bool:
        """
        Lấy trading token
        
        Args:
            otp_code: Mã OTP (bắt buộc cho Real, None cho Demo)
            
        Returns:
            True nếu thành công
        """
        try:
            url = "https://services.entrade.com.vn/entrade-api/otp/trading-token"
            headers = {
                "accept": "*/*",
                "authorization": f"Bearer {self.token}"
            }
            
            if otp_code:
                headers["otp"] = otp_code
            
            response = self.session.get(url, headers=headers)
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
    
    def get_investor_info(self) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin nhà đầu tư
        
        Returns:
            Dictionary chứa thông tin investor
        """
        try:
            url = f"{self.base_url}/investors/_me"
            headers = {
                "accept": "*/*",
                "authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.investor_id = data.get("investorId")
            
            logger.info(f"✅ Investor info retrieved: {data.get('fullName')}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to get investor info: {e}")
            return None
    
    def get_account_balance(self, investor_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy số dư tài khoản
        
        Args:
            investor_id: ID nhà đầu tư
            
        Returns:
            Dictionary chứa thông tin số dư
        """
        try:
            url = f"{self.base_url}/account_balances/{investor_id}"
            headers = {
                "accept": "*/*",
                "authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Account balance retrieved")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to get account balance: {e}")
            return None
    
    def get_derivative_portfolios(self, investor_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Lấy danh sách portfolios phái sinh
        
        Args:
            investor_id: ID nhà đầu tư
            
        Returns:
            List portfolios
        """
        try:
            url = f"{self.base_url}/investors/{investor_id}/derivative_margin_portfolios"
            headers = {
                "accept": "*/*",
                "authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            portfolios = data.get("data", [])
            
            if portfolios:
                self.portfolio_id = portfolios[0].get("id")
            
            logger.info(f"✅ Retrieved {len(portfolios)} portfolios")
            return portfolios
            
        except Exception as e:
            logger.error(f"❌ Failed to get portfolios: {e}")
            return None
    
    def get_buying_power(
        self,
        investor_id: str,
        portfolio_id: str,
        symbol: str,
        price: float,
        side: str = "NB"
    ) -> Optional[Dict[str, Any]]:
        """
        Tính sức mua (PPSE)
        
        Args:
            investor_id: ID nhà đầu tư
            portfolio_id: ID portfolio
            symbol: Mã symbol (VN30F1M, VN30F2M, etc.)
            price: Giá dự kiến
            side: "NB" (Mua) hoặc "NS" (Bán)
            
        Returns:
            Dictionary chứa thông tin sức mua
        """
        try:
            url = f"{self.base_url}/derivative/investors/{investor_id}/ppse"
            params = {
                "bankMarginPortfolioId": portfolio_id,
                "price": price,
                "side": side,
                "symbol": symbol
            }
            headers = {
                "accept": "*/*",
                "authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Buying power calculated")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to get buying power: {e}")
            return None
    
    def place_order(
        self,
        investor_id: str,
        portfolio_id: str,
        symbol: str,
        price: float,
        quantity: int,
        side: str = "NB",
        order_type: str = "LO"
    ) -> Optional[Dict[str, Any]]:
        """
        Đặt lệnh
        
        Args:
            investor_id: ID nhà đầu tư
            portfolio_id: ID portfolio
            symbol: Mã symbol (VN30F1M)
            price: Giá
            quantity: Số lượng
            side: "NB" (Mua) hoặc "NS" (Bán)
            order_type: "LO" (Limit Order) hoặc "MP" (Market Price)
            
        Returns:
            Dictionary chứa thông tin order
        """
        try:
            url = f"{self.base_url}/derivative/orders"
            headers = {
                "accept": "*/*",
                "content-type": "application/json",
                "authorization": f"Bearer {self.token}",
                "trading-token": self.trading_token
            }
            payload = {
                "bankMarginPortfolioId": portfolio_id,
                "investorId": investor_id,
                "symbol": symbol,
                "price": price,
                "orderType": order_type,
                "side": side,
                "quantity": quantity
            }
            
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Order placed: {data.get('id')}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to place order: {e}")
            return None
    
    def get_order_list(
        self,
        investor_id: str,
        limit: int = 100
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Lấy danh sách lệnh
        
        Args:
            investor_id: ID nhà đầu tư
            limit: Số lượng lệnh tối đa
            
        Returns:
            List các order
        """
        try:
            url = f"{self.base_url}/derivative/orders"
            params = {
                "investorId": investor_id,
                "_order": "DESC",
                "_sort": "createdDate",
                "_start": 0,
                "_end": limit
            }
            headers = {
                "accept": "*/*",
                "authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            orders = data.get("data", [])
            
            logger.info(f"✅ Retrieved {len(orders)} orders")
            return orders
            
        except Exception as e:
            logger.error(f"❌ Failed to get order list: {e}")
            return None
    
    def get_pending_orders(self, investor_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Lấy danh sách lệnh chờ khớp
        
        Args:
            investor_id: ID nhà đầu tư
            
        Returns:
            List các pending order
        """
        orders = self.get_order_list(investor_id)
        if not orders:
            return None
            
        pending = [
            order for order in orders 
            if order.get("orderStatus") in ["New", "PartiallyFilled"]
        ]
        
        logger.info(f"✅ Found {len(pending)} pending orders")
        return pending
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Hủy lệnh
        
        Args:
            order_id: ID của order
            
        Returns:
            True nếu thành công
        """
        try:
            url = f"{self.base_url}/derivative/orders/{order_id}"
            headers = {
                "accept": "*/*",
                "authorization": f"Bearer {self.token}",
                "trading-token": self.trading_token
            }
            
            response = self.session.delete(url, headers=headers)
            response.raise_for_status()
            
            logger.info(f"✅ Order {order_id} cancelled")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel order: {e}")
            return False
    
    def cancel_all_orders(self, investor_id: str) -> int:
        """
        Hủy tất cả lệnh chờ
        
        Args:
            investor_id: ID nhà đầu tư
            
        Returns:
            Số lượng lệnh đã hủy
        """
        orders = self.get_pending_orders(investor_id)
        if not orders:
            return 0
            
        cancelled_count = 0
        for order in orders:
            if self.cancel_order(order["id"]):
                cancelled_count += 1
        
        logger.info(f"✅ Cancelled {cancelled_count} orders")
        return cancelled_count
    
    def get_current_deals(self, investor_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Lấy danh sách các deal đang mở
        
        Args:
            investor_id: ID nhà đầu tư
            
        Returns:
            List các open deal
        """
        try:
            url = f"{self.base_url}/derivative/deals"
            params = {
                "_start": 0,
                "_end": 1000,
                "investorId": investor_id
            }
            headers = {
                "accept": "*/*",
                "authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            all_deals = data.get("data", [])
            
            # Filter only OPEN deals
            open_deals = [
                deal for deal in all_deals 
                if deal.get("status") == "OPEN"
            ]
            
            logger.info(f"✅ Retrieved {len(open_deals)} open deals")
            return open_deals
            
        except Exception as e:
            logger.error(f"❌ Failed to get deals: {e}")
            return None
    
    def get_derivatives_info(self) -> Optional[List[Dict[str, Any]]]:
        """
        Lấy thông tin các hợp đồng phái sinh
        
        Returns:
            List thông tin derivatives
        """
        try:
            url = f"{self.base_url}/derivatives"
            headers = {
                "accept": "*/*",
                "authorization": f"Bearer {self.token}"
            }
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Retrieved derivatives info")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to get derivatives info: {e}")
            return None
    
    def get_symbol_info(self, symbol_type: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin symbol cụ thể
        
        Args:
            symbol_type: Loại symbol (VN30F1M, VN30F2M)
            
        Returns:
            Dictionary chứa thông tin symbol
        """
        derivatives = self.get_derivatives_info()
        if not derivatives:
            return None
            
        for derivative in derivatives:
            if derivative.get("type") == symbol_type:
                logger.info(f"✅ Found symbol info for {symbol_type}")
                return derivative
        
        logger.warning(f"⚠️ Symbol {symbol_type} not found")
        return None
    
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
        self.portfolio_id = None
        self.session.close()
        logger.info(f"🔌 Entrade ({self.environment}) disconnected")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Demo mode
    client = EntradeClient(environment="demo")
    
    # Step 1: Authenticate
    success = client.authenticate("your_username", "your_password")
    if not success:
        exit(1)
    
    # Step 2: Request OTP (demo skip this)
    client.request_otp()
    
    # Step 3: Get trading token (no OTP for demo)
    success = client.get_trading_token(None)
    if not success:
        exit(1)
    
    # Step 4: Get investor info
    investor_info = client.get_investor_info()
    print(f"Logged in as: {investor_info.get('fullName')}")
    
    investor_id = investor_info["investorId"]
    
    # Step 5: Get portfolios
    portfolios = client.get_derivative_portfolios(investor_id)
    if portfolios:
        print(f"Portfolio ID: {portfolios[0]['id']}")
    
    # Ready to trade
    print(f"Ready to trade: {client.is_ready_to_trade()}")
