"""
AccessTrade API Integration
Fetches campaigns, offers, coupons, and statistics from AccessTrade.

Docs:
- Offers/Coupons: https://developers.accesstrade.vn/api-publisher-vietnamese/lay-thong-tin-vouchers-coupons-deals/tim-kiem-danh-sach-thong-tin-khuyen-mai
- Active Promos:  https://developers.accesstrade.vn/api-publisher-vietnamese/lay-thong-tin-cac-khuyen-mai-dang-hoat-dong
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

    # ═══════════════════════════════════════
    # DATAFEEDS  (product catalog from merchants)
    # Docs: https://developers.accesstrade.vn/api-publisher-vietnamese/lay-thong-tin-datafeeds
    # ═══════════════════════════════════════

    def get_datafeeds(self, campaign=None, domain=None, keyword=None,
                      price_from=None, price_to=None,
                      discount_from=None, discount_to=None,
                      discount=None, page=1, limit=50,
                      update_from=None, update_to=None):
        """Get product datafeeds from AccessTrade merchants.

        GET /v1/datafeeds

        Args:
            campaign:       Filter by campaign ID
            domain:         Filter by merchant domain (e.g. "shopee.vn")
            keyword:        Search product name
            price_from/to:  Price range filter
            discount_from/to: Discount percentage range
            discount:       1 = only discounted, 0 = no discount, None = all
            page:           Page number (1-based)
            limit:          Products per page (max 200)
            update_from/to: Date range filter (dd/mm/yyyy)

        Returns dict with:
            'data': list of product dicts
            'total': total matching products
        """
        try:
            params = {"page": page, "limit": min(limit, 200)}
            if campaign:
                params['campaign'] = campaign
            if domain:
                params['domain'] = domain
            if keyword:
                params['keyword'] = keyword
            if price_from is not None:
                params['price_from'] = price_from
            if price_to is not None:
                params['price_to'] = price_to
            if discount_from is not None:
                params['discount_from'] = discount_from
            if discount_to is not None:
                params['discount_to'] = discount_to
            if discount is not None:
                params['discount'] = discount
            if update_from:
                params['update_from'] = update_from
            if update_to:
                params['update_to'] = update_to

            response = requests.get(
                f"{self.base_url}/datafeeds",
                headers=self.headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'data': data.get('data', []),
                    'total': data.get('total', 0)
                }
        except Exception:
            pass
        return {'data': [], 'total': 0}

    # ═══════════════════════════════════════
    # TOP PRODUCTS  (bestselling products)
    # Docs: https://developers.accesstrade.vn/api-publisher-vietnamese/top-cac-san-pham-ban-chay-nhat
    # ═══════════════════════════════════════

    def get_top_products(self, merchant=None, date_from=None, date_to=None):
        """Get top bestselling products from AccessTrade merchants.

        GET /v1/top_products

        Args:
            merchant:   Filter by merchant (e.g. 'lazada', 'shopee')
            date_from:  Start date (DD-MM-YYYY)
            date_to:    End date (DD-MM-YYYY)

        Returns dict with:
            'data': list of up to 50 product dicts (product_id, name, price,
                    discount, image, link, aff_link, brand, category_name, desc)
            'total': number of products
        """
        try:
            params = {}
            if merchant:
                params['merchant'] = merchant
            if date_from:
                params['date_from'] = date_from
            if date_to:
                params['date_to'] = date_to

            response = requests.get(
                f"{self.base_url}/top_products",
                headers=self.headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'data': data.get('data', []),
                    'total': data.get('total', 0)
                }
        except Exception:
            pass
        return {'data': [], 'total': 0}

    # ═══════════════════════════════════════
    # OFFERS / PROMOTIONS  (offers_informations)
    # ═══════════════════════════════════════

    def get_offers(self, limit=100, page=1, merchant=None, categories=None,
                   domain=None, coupon=None, status=None, scope=None):
        """Get active promotions with filters.

        GET /v1/offers_informations

        Args:
            limit:      Records per page (default 100)
            page:       Page number
            merchant:   Filter by merchant owner name (e.g. "lazada", "shopee")
            categories: Filter by category_name, comma-separated
            domain:     Filter by domain (e.g. "lazada.vn")
            coupon:     1 = only offers with codes, 0 = without codes, None = all
            status:     1 = active, 0 = expired, None = all
            scope:      "expiring" = ending soon, None = all
        """
        try:
            params = {"limit": limit, "page": page}
            if merchant:
                params['merchant'] = merchant
            if categories:
                params['categories'] = categories
            if domain:
                params['domain'] = domain
            if coupon is not None:
                params['coupon'] = coupon
            if status is not None:
                params['status'] = status
            if scope:
                params['scope'] = scope

            response = requests.get(
                f"{self.base_url}/offers_informations",
                headers=self.headers,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except Exception:
            pass
        return []

    def get_offers_expiring(self, limit=50):
        """Get promotions ending soon.

        Shortcut for get_offers(scope='expiring')
        """
        return self.get_offers(limit=limit, scope='expiring')

    def get_offers_with_coupons(self, limit=100, merchant=None):
        """Get only offers that have coupon codes.

        Shortcut for get_offers(coupon=1)
        """
        return self.get_offers(limit=limit, coupon=1, merchant=merchant)

    # ═══════════════════════════════════════
    # COUPONS / VOUCHERS  (offers_informations/coupon)
    # ═══════════════════════════════════════

    def get_coupons(self, keyword=None, merchant=None, is_next_day=None,
                    limit=50, page=1):
        """Search coupons with filters.

        GET /v1/offers_informations/coupon

        Args:
            keyword:     Keyword UID from keyword_list
            merchant:    Merchant UID from merchant_list
            is_next_day: True = upcoming, False = active, None = all
            limit:       Records per page
            page:        Page number

        Returns list of coupon offers, each containing:
            id, name, merchant, content, image, link, prod_link,
            start_date, end_date, time_left, percentage_used,
            discount_value, discount_percentage, min_spend, max_value,
            coin_cap, coin_percentage, categories, coupons[], banners[]
        """
        try:
            params = {"limit": limit, "page": page}
            if keyword:
                params['keyword'] = keyword
            if merchant:
                params['merchant'] = merchant
            if is_next_day is not None:
                params['is_next_day_coupon'] = 'true' if is_next_day else 'false'

            response = requests.get(
                f"{self.base_url}/offers_informations/coupon",
                headers=self.headers,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except Exception:
            pass
        return []

    def get_coupons_hot(self, limit=50, date=1):
        """Get hot/priority coupons.

        GET /v1/offers_informations/coupon_hot

        Args:
            limit: Records per page
            date:  1 = weekly hot, 2 = monthly hot
        """
        try:
            response = requests.get(
                f"{self.base_url}/offers_informations/coupon_hot",
                headers=self.headers,
                params={"limit": limit, "date": date},
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except Exception:
            pass
        return []

    def search_coupons_by_url(self, product_url):
        """Search applicable coupons for a product URL.

        GET /v1/offers_informations/coupon?URL=...
        Supports: Shopee & Tiki product links (including short links)

        Returns list of coupons applicable to the product.
        """
        try:
            response = requests.get(
                f"{self.base_url}/offers_informations/coupon",
                headers=self.headers,
                params={"URL": product_url},
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except Exception:
            pass
        return []

    def search_coupons_by_urls(self, urls):
        """Search coupons for multiple product URLs at once.

        POST /v1/offers_informations/multi_link_2_coupons

        Args:
            urls: list of product URLs (max 5 per request)

        Returns list of {origin_url, status, list_voucher[]}
        Each voucher: {aff_link, coupon_code, coupon_desc, remain, time_left,
                       start_time, end_time}

        Rate limit: 30 requests/minute
        """
        try:
            response = requests.post(
                f"{self.base_url}/offers_informations/multi_link_2_coupons",
                headers=self.headers,
                json={"URLS": ",".join(urls[:5])},
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except Exception:
            pass
        return []

    # ═══════════════════════════════════════
    # METADATA  (merchant list, keywords, categories)
    # ═══════════════════════════════════════

    def get_merchant_list(self):
        """Get list of all merchants with logo and offer counts.

        GET /v1/offers_informations/merchant_list

        Returns list of {id, display_name, login_name, logo, total_offer}
        """
        try:
            response = requests.get(
                f"{self.base_url}/offers_informations/merchant_list",
                headers=self.headers,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except Exception:
            pass
        return []

    def get_keyword_list(self):
        """Get campaign keyword list (e.g. ShopeePay, FlashSale...).

        GET /v1/offers_informations/keyword_list

        Returns list of {id, icon_text, total_offer}
        """
        try:
            response = requests.get(
                f"{self.base_url}/offers_informations/keyword_list",
                headers=self.headers,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except Exception:
            pass
        return []

    def get_merchant_keywords(self, merchant_id):
        """Get category keywords for a specific merchant.

        GET /v1/offers_informations/icontext_list?merchant=...

        Returns list of {icon_text, merchant, total_offer}
        """
        try:
            response = requests.get(
                f"{self.base_url}/offers_informations/icontext_list",
                headers=self.headers,
                params={"merchant": merchant_id},
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except Exception:
            pass
        return []

    def get_category_list(self):
        """Get coupon category/industry list.

        GET /v1/offers_informations/list_category_coupons

        Returns list of {category: [{category_name, category_name_show, category_no}],
                         count, type}
        Types: E-COMMERCE, BEAUTY, FINANCE, TRAVEL, etc.
        """
        try:
            response = requests.get(
                f"{self.base_url}/offers_informations/list_category_coupons",
                headers=self.headers,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
        except Exception:
            pass
        return []

    # ═══════════════════════════════════════
    # CAMPAIGNS & TRANSACTIONS
    # ═══════════════════════════════════════

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
            # merchant is a string in real API (e.g. "shopee")
            merchant_raw = offer.get('merchant', '')
            if isinstance(merchant_raw, dict):
                merchant_name = merchant_raw.get('name', 'N/A')
            else:
                merchant_name = str(merchant_raw) if merchant_raw else 'N/A'

            if offer.get('coupons'):
                for coupon in offer['coupons']:
                    all_coupons.append({
                        'code': coupon.get('coupon_code', ''),
                        'description': coupon.get('coupon_desc', '') or coupon.get('coupon_description', ''),
                        'merchant': merchant_name,
                        'offer_name': offer.get('name', ''),
                        'start_date': offer.get('start_time', ''),
                        'end_date': offer.get('end_time', ''),
                        'aff_link': offer.get('aff_link', ''),
                    })

        return all_coupons

    def get_offers_detailed(self, limit=100, merchant=None, scope=None):
        """Get offers with full detail for voucher sync.

        Combines data from both offers_informations and coupon endpoints.

        Fields from offers_informations:
            id, name, merchant, domain, content, image, aff_link,
            start_time, end_time, coupons[], categories[]

        Extra fields from coupon endpoint:
            discount_value, discount_percentage, min_spend, max_value,
            coin_cap, coin_percentage, percentage_used, time_left, prod_link
        """
        offers = self.get_offers(limit=limit, merchant=merchant, scope=scope)
        results = []
        for offer in offers:
            item = self._parse_offer(offer)
            results.append(item)
        return results

    def get_coupons_detailed(self, keyword=None, merchant=None, limit=100):
        """Get coupons with full detail from the coupon endpoint.

        Returns richer data than get_offers_detailed, including
        discount_value, min_spend, max_value, time_left, percentage_used.
        """
        offers = self.get_coupons(
            keyword=keyword, merchant=merchant, limit=limit
        )
        results = []
        for offer in offers:
            item = self._parse_offer(offer)
            results.append(item)
        return results

    def _parse_offer(self, offer):
        """Parse a single offer/coupon response into a normalized dict."""
        # merchant can be string ("shopee") or dict (older API versions)
        merchant_raw = offer.get('merchant', '')
        if isinstance(merchant_raw, dict):
            merchant_name = merchant_raw.get('name', '') or 'N/A'
            merchant_logo = (merchant_raw.get('image', '') or
                            merchant_raw.get('logo', '') or '')
        else:
            merchant_name = (str(merchant_raw).capitalize()
                            if merchant_raw else 'N/A')
            merchant_logo = offer.get('image', '')

        coupons = offer.get('coupons') or []
        offer_name = offer.get('name', '')
        offer_desc = (offer.get('content', '') or
                      offer.get('description', '') or '')

        # Extract category from categories list
        cats = offer.get('categories') or []
        cat_name = cats[0].get('category_name_show', '') if cats else ''

        item = {
            'offer_id': str(offer.get('id', '')),
            'offer_name': offer_name,
            'description': offer_desc,
            'merchant': merchant_name,
            'merchant_logo': merchant_logo,
            'domain': offer.get('domain', ''),
            'category': cat_name,
            'aff_link': (offer.get('aff_link', '') or
                         offer.get('prod_link', '') or
                         offer.get('link', '')),
            'start_date': offer.get('start_time', '') or offer.get('start_date', ''),
            'end_date': offer.get('end_time', '') or offer.get('end_date', ''),
            # Coupon-endpoint extra fields
            'discount_value': offer.get('discount_value'),
            'discount_percentage': offer.get('discount_percentage'),
            'min_spend': offer.get('min_spend'),
            'max_value': offer.get('max_value'),
            'coin_cap': offer.get('coin_cap'),
            'coin_percentage': offer.get('coin_percentage'),
            'percentage_used': offer.get('percentage_used'),
            'time_left': offer.get('time_left', ''),
            'coupons': [],
        }

        for c in coupons:
            item['coupons'].append({
                'code': c.get('coupon_code', ''),
                'description': (c.get('coupon_desc', '') or
                                c.get('coupon_description', '')),
                'discount': (c.get('discount', '') or
                             c.get('coupon_value', '')),
                'remain': c.get('remain'),
                'time_left': c.get('time_left', ''),
            })

        return item


# Singleton instance
_api_instance = None

def get_accesstrade_api(api_key=None):
    """Get or create AccessTrade API instance"""
    global _api_instance

    if api_key is None:
        # Try to get from database
        from app import app, SiteSettings, AffiliateNetwork
        with app.app_context():
            api_key = SiteSettings.get('accesstrade_api_key', '')
            # Fallback: check AffiliateNetwork table
            if not api_key:
                at = AffiliateNetwork.query.filter_by(slug='accesstrade').first()
                if at and at.api_key:
                    api_key = at.api_key

    if not api_key:
        return None

    if _api_instance is None or _api_instance.api_key != api_key:
        _api_instance = AccessTradeAPI(api_key)

    return _api_instance
