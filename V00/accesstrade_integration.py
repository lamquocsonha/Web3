"""
AccessTrade API Integration
Full integration of AccessTrade Publisher API for affiliate marketing.

API Reference: https://developers.accesstrade.vn/api-publisher-vietnamese

Implemented endpoints:
  ──── PRODUCTS & CATALOG ────
  GET  /v1/datafeeds             → get_datafeeds()          — Search products from Shopee/Lazada/Tiki
  GET  /v1/top_products          → get_top_products()       — Bestselling products
  GET  /v1/product_detail        → get_product_detail()     — Single product detail (brand, shop, desc)

  ──── LINK GENERATION ────
  POST /v1/product_link/create   → create_tracking_link()   — Convert URLs → affiliate links

  ──── TIKTOK SHOP ────
  GET  /v2/tiktokshop_product_feeds           → tiktok_search_products() — Search TikTok products
  POST /v2/tiktokshop_product_feeds/create_link → tiktok_create_link()  — TikTok affiliate link

  ──── OFFERS & COUPONS ────
  GET  /v1/offers_informations               → get_offers()              — Promotions list
  GET  /v1/offers_informations (scope=expiring) → get_offers_expiring()  — Ending soon
  GET  /v1/offers_informations (coupon=1)    → get_offers_with_coupons() — Offers with codes
  GET  /v1/offers_informations/coupon        → get_coupons()             — Search coupons
  GET  /v1/offers_informations/coupon_hot    → get_coupons_hot()         — Hot coupons
  GET  /v1/offers_informations/coupon?URL=   → search_coupons_by_url()   — Coupons for product URL
  POST /v1/offers_informations/multi_link_2_coupons → search_coupons_by_urls() — Bulk URL→coupons

  ──── METADATA ────
  GET  /v1/offers_informations/merchant_list     → get_merchant_list()     — Merchant list
  GET  /v1/offers_informations/keyword_list      → get_keyword_list()      — Campaign keywords
  GET  /v1/offers_informations/icontext_list     → get_merchant_keywords() — Merchant keywords
  GET  /v1/offers_informations/list_category_coupons → get_category_list() — Industry categories

  ──── CAMPAIGNS & ORDERS ────
  GET  /v1/campaigns             → get_campaigns()          — Campaign list
  GET  /v1/campaigns (by id)     → get_campaign_by_id()     — Single campaign
  GET  /v1/transactions          → get_transactions()       — Transaction stats
  GET  /v1/order-list            → get_order_list()         — Detailed orders v2
  GET  /v1/me                    → get_account_info()       — Account info

Integration points in the project:
  - Admin Dashboard  (/admin)                → stats, campaigns, offers, order list widget
  - Admin Products   (/admin/products)       → tracking link tool, TikTok search tool
  - Admin Datafeeds  (/admin/products/datafeeds) → datafeeds product import
  - Admin Voucher    (/admin/vouchers/sync)  → offers/coupons sync
  - Shop page        (/shop)                 → hot products carousel
  - All sidebar      (shared partials)       → hot products sidebar widget
  - API endpoints    (/admin/api/*)          → AJAX order-list, tracking-link, tiktok
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
    # CREATE TRACKING LINK  (affiliate link generator)
    # Docs: https://developers.accesstrade.vn/api-publisher-vietnamese/tao-tracking-link
    # ═══════════════════════════════════════

    def create_tracking_link(self, campaign_id, urls=None, utm_source=None,
                             utm_medium=None, utm_campaign=None, utm_content=None,
                             sub1=None, sub2=None, sub3=None, sub4=None):
        """Create affiliate tracking links from product URLs.

        POST /v1/product_link/create

        Args:
            campaign_id: Campaign ID (required)
            urls:        List of product URLs (uses campaign URL if omitted)
            utm_source:  Custom tracking param
            utm_medium:  Custom tracking param
            utm_campaign: Custom tracking param
            utm_content: Custom tracking param
            sub1-sub4:   Custom sub-tracking params

        Returns dict with:
            'success': bool
            'success_link': list of {aff_link, short_link, first_link, url_origin}
            'error_link': list of failed URLs
            'suspend_url': list of suspended URLs
        """
        try:
            payload = {'campaign_id': str(campaign_id)}
            if urls:
                payload['urls'] = ','.join(urls) if isinstance(urls, list) else urls
            if utm_source:
                payload['utm_source'] = utm_source
            if utm_medium:
                payload['utm_medium'] = utm_medium
            if utm_campaign:
                payload['utm_campaign'] = utm_campaign
            if utm_content:
                payload['utm_content'] = utm_content
            if sub1:
                payload['sub1'] = sub1
            if sub2:
                payload['sub2'] = sub2
            if sub3:
                payload['sub3'] = sub3
            if sub4:
                payload['sub4'] = sub4

            response = requests.post(
                f"{self.base_url}/product_link/create",
                headers=self.headers,
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                result = data.get('data', {})
                return {
                    'success': data.get('success', False),
                    'success_link': result.get('success_link', []),
                    'error_link': result.get('error_link', []),
                    'suspend_url': result.get('suspend_url', []),
                }
        except Exception:
            pass
        return {'success': False, 'success_link': [], 'error_link': [], 'suspend_url': []}

    # ═══════════════════════════════════════
    # ORDER LIST v2  (detailed order tracking)
    # Docs: https://developers.accesstrade.vn/api-publisher-vietnamese/lay-danh-sach-don-hang-v2
    # ═══════════════════════════════════════

    def get_order_list(self, since, until, page=1, limit=30, status=None,
                       merchant=None, utm_source=None, utm_campaign=None,
                       utm_medium=None, utm_content=None):
        """Get detailed order list (v2 — richer than transactions).

        GET /v1/order-list
        Rate limit: 10 req/min, cache 1 min

        Args:
            since:        Start time ISO 8601 (e.g. '2024-01-01T00:00:00Z') REQUIRED
            until:        End time ISO 8601 REQUIRED
            page:         Page number (default 1)
            limit:        Results per page (default 30, max 300)
            status:       0=pending, 1=approved, 2=rejected
            merchant:     Filter by merchant (e.g. 'shopee')
            utm_source:   Filter by UTM source
            utm_campaign: Filter by UTM campaign
            utm_medium:   Filter by UTM medium
            utm_content:  Filter by UTM content

        Returns dict with:
            'data': list of order dicts (order_id, billing, pub_commission,
                    merchant, click_time, sales_time, products_count, ...)
            'total': total orders
        """
        try:
            params = {
                'since': since,
                'until': until,
                'page': page,
                'limit': min(limit, 300),
            }
            if status is not None:
                params['status'] = status
            if merchant:
                params['merchant'] = merchant
            if utm_source:
                params['utm_source'] = utm_source
            if utm_campaign:
                params['utm_campaign'] = utm_campaign
            if utm_medium:
                params['utm_medium'] = utm_medium
            if utm_content:
                params['utm_content'] = utm_content

            response = requests.get(
                f"{self.base_url}/order-list",
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
    # PRODUCT DETAIL  (single product info)
    # Docs: https://developers.accesstrade.vn/api-publisher-vietnamese/lay-thong-tin-chi-tiet-san-pham
    # ═══════════════════════════════════════

    def get_product_detail(self, merchant, product_id, transaction_id):
        """Get detailed information about a specific product.

        GET /v1/product_detail

        Args:
            merchant:       Merchant name (e.g. 'lazada', 'shopee')
            product_id:     Product identifier
            transaction_id: Transaction code

        Returns dict with:
            name, price, discount, link, image, desc, short_desc,
            brand, shop_name, shop_id, category_id, category_name
        """
        try:
            params = {
                'merchant': merchant,
                'product_id': product_id,
                'transaction_id': transaction_id,
            }

            response = requests.get(
                f"{self.base_url}/product_detail",
                headers=self.headers,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}) if isinstance(data.get('data'), dict) else data
        except Exception:
            pass
        return {}

    # ═══════════════════════════════════════
    # TIKTOK SHOP  (product search + link creation)
    # Docs: https://developers.accesstrade.vn/api-publisher-vietnamese/tich-hop-api-publisher-at-cho-chien-dich-tiktok-shop
    # ═══════════════════════════════════════

    def tiktok_search_products(self, title_keywords, sort_field='RECOMMENDED',
                               limit=20, page_token=None, product_ids=None):
        """Search TikTok Shop products.

        GET /v2/tiktokshop_product_feeds

        Args:
            title_keywords: Search keywords (required)
            sort_field:     RECOMMENDED, BEST_SELLERS, LOW_PRICE, HIGH_PRICE,
                           NEWLY_RELEASED, HIGH_COMMISSION_RATE
            limit:          Results per page
            page_token:     Pagination token from previous response
            product_ids:    Specific product IDs to retrieve

        Returns dict with:
            'products': list of product dicts (id, title, units_sold,
                       main_image_url, detail_link, shop, original_price,
                       sales_price, commission, category_chains)
            'total_count': total matching products
            'next_page_token': token for next page
        """
        try:
            params = {
                'title_keywords': title_keywords,
                'sort_field': sort_field,
                'limit': limit,
            }
            if page_token:
                params['page_token'] = page_token
            if product_ids:
                params['product_ids'] = product_ids

            response = requests.get(
                f"https://api.accesstrade.vn/v2/tiktokshop_product_feeds",
                headers=self.headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                result = data.get('data', {})
                return {
                    'products': result.get('products', []),
                    'total_count': result.get('total_count', 0),
                    'next_page_token': result.get('next_page_token', ''),
                }
        except Exception:
            pass
        return {'products': [], 'total_count': 0, 'next_page_token': ''}

    def tiktok_create_link(self, product_url, product_id=None,
                           utm_source=None, utm_medium=None,
                           utm_campaign=None, utm_content=None,
                           sub_1=None, sub_2=None, sub_3=None, sub_4=None):
        """Create TikTok Shop affiliate tracking link.

        POST /v2/tiktokshop_product_feeds/create_link

        Args:
            product_url: TikTok product URL (required)
            product_id:  Product identifier (optional)
            utm_*:       Tracking params
            sub_1-4:     Custom tracking params

        Returns dict with:
            'status': bool
            'aff_url': full affiliate link
            'aff_short_url': shortened affiliate link
            'product_id': product ID
            'product_name': product name
            'product_image': image URL
            'product_price': {amount, currency}
            'product_commission': {amount, currency, rate}
        """
        try:
            payload = {'product_url': product_url}
            if product_id:
                payload['product_id'] = product_id
            if utm_source:
                payload['utm_source'] = utm_source
            if utm_medium:
                payload['utm_medium'] = utm_medium
            if utm_campaign:
                payload['utm_campaign'] = utm_campaign
            if utm_content:
                payload['utm_content'] = utm_content
            if sub_1:
                payload['sub_1'] = sub_1
            if sub_2:
                payload['sub_2'] = sub_2
            if sub_3:
                payload['sub_3'] = sub_3
            if sub_4:
                payload['sub_4'] = sub_4

            response = requests.post(
                f"https://api.accesstrade.vn/v2/tiktokshop_product_feeds/create_link",
                headers=self.headers,
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                result = data.get('data', {})
                return {
                    'status': data.get('status', False),
                    'message': data.get('message', ''),
                    'aff_url': result.get('aff_url', ''),
                    'aff_short_url': result.get('aff_short_url', ''),
                    'product_id': result.get('product_id', ''),
                    'product_name': result.get('product_name', ''),
                    'product_image': result.get('product_image', ''),
                    'product_price': result.get('product_price', {}),
                    'product_commission': result.get('product_commission', {}),
                }
        except Exception:
            pass
        return {'status': False, 'message': 'Request failed', 'aff_url': '', 'aff_short_url': ''}

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
            api_key = SiteSettings.get('accesstrade_api_key', 'byMkvHrygyW5bZCaP3O2AZDv4P4DY34F')
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
