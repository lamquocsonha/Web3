"""
AccessTrade API Integration
Fetches campaigns, offers, and statistics from AccessTrade
"""
import requests
from datetime import datetime, timedelta

class AccessTradeAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.accesstrade.vn/v1"
        self.headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        }

    def get_account_info(self):
        """Get account information"""
        try:
            response = requests.get(
                f"{self.base_url}/me",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {})
        except:
            pass
        return {}

    def get_campaigns(self, limit=50, status=None):
        """
        Get campaign list
        status: None (all), 1 (active), 0 (inactive)
        """
        try:
            params = {"limit": limit}
            if status is not None:
                params['status'] = status

            response = requests.get(
                f"{self.base_url}/campaigns",
                headers=self.headers,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except:
            pass
        return []

    def get_offers(self, limit=100):
        """Get available offers and coupons"""
        try:
            response = requests.get(
                f"{self.base_url}/offers_informations",
                headers=self.headers,
                params={"limit": limit},
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except:
            pass
        return []

    def get_transactions(self, start_date=None, end_date=None):
        """
        Get transaction statistics
        start_date, end_date: YYYY-MM-DD format
        """
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            response = requests.get(
                f"{self.base_url}/transactions",
                headers=self.headers,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except:
            pass
        return []

    def get_statistics_summary(self, days=30):
        """Get summary statistics for last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        transactions = self.get_transactions(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        total_clicks = sum(t.get('click', 0) for t in transactions)
        total_conversions = sum(t.get('conversion', 0) for t in transactions)
        total_commission = sum(float(t.get('commission', 0)) for t in transactions)

        return {
            'clicks': total_clicks,
            'conversions': total_conversions,
            'commission': total_commission,
            'period_days': days,
            'campaigns_count': len(self.get_campaigns())
        }

    def get_campaign_by_id(self, campaign_id):
        """Get specific campaign details"""
        campaigns = self.get_campaigns()
        for c in campaigns:
            if str(c.get('id')) == str(campaign_id):
                return c
        return None

    def get_coupons_from_offers(self, limit=50):
        """Extract all coupons from offers"""
        offers = self.get_offers(limit=limit)
        all_coupons = []

        for offer in offers:
            if offer.get('coupons'):
                for coupon in offer['coupons']:
                    all_coupons.append({
                        'code': coupon.get('coupon_code', ''),
                        'description': coupon.get('coupon_description', ''),
                        'merchant': offer.get('merchant', {}).get('name', 'N/A'),
                        'offer_name': offer.get('name', ''),
                        'start_date': offer.get('start_time', ''),
                        'end_date': offer.get('end_time', ''),
                        'aff_link': offer.get('aff_link', ''),
                    })

        return all_coupons


# Singleton instance
_api_instance = None

def get_accesstrade_api(api_key=None):
    """Get or create AccessTrade API instance"""
    global _api_instance

    if api_key is None:
        # Try to get from database
        from app import app, SiteSettings
        with app.app_context():
            api_key = SiteSettings.get('accesstrade_api_key', '')

    if not api_key:
        return None

    if _api_instance is None or _api_instance.api_key != api_key:
        _api_instance = AccessTradeAPI(api_key)

    return _api_instance
