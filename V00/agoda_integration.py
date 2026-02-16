"""
Agoda Demand API Integration
Partner API for hotel search, content, and affiliate link generation.

API Reference: https://developer.agoda.com/demand/docs/getting-started

Implemented:
  ──── SEARCH ────
  POST /api/v2/search         → search_hotels()       — Availability & pricing for property IDs

  ──── CONTENT FEEDS ────
  GET  /datafeeds/feed/getfeed → get_feed()            — Static hotel data (details, images, cities)
       feed_id=3               → get_cities()           — City list with hotel counts
       feed_id=5               → get_hotels_by_city()   — Hotels in a city
       feed_id=19              → get_hotel_details()     — Full hotel profile
       feed_id=7               → get_hotel_images()      — Hotel photos

  ──── AFFILIATE LINKS ────
  build_affiliate_url()        → Generate booking URL with CID tracking
"""

import requests
from datetime import datetime, timedelta

# Vietnamese city ID mapping for Agoda
AGODA_CITY_IDS = {
    'ha-noi': 13170,
    'ho-chi-minh': 17072,
    'da-nang': 14537,
    'nha-trang': 16550,
    'phu-quoc': 28614,
    'da-lat': 17572,
    'hoi-an': 17579,
    'sa-pa': 17620,
    'hue': 13165,
    'hai-phong': 14543,
    'can-tho': 14550,
    'quang-ninh': 20028,
    'ninh-binh': 349498,
    'vung-tau': 17193,
    'quy-nhon': 16561,
    'ha-long': 20028,
    'mui-ne': 15621,
    'con-dao': 574889,
    'tam-dao': 463379,
    'cat-ba': 93511,
}

AGODA_CITY_NAMES = {
    'ha-noi': 'Hà Nội',
    'ho-chi-minh': 'TP. Hồ Chí Minh',
    'da-nang': 'Đà Nẵng',
    'nha-trang': 'Nha Trang',
    'phu-quoc': 'Phú Quốc',
    'da-lat': 'Đà Lạt',
    'hoi-an': 'Hội An',
    'sa-pa': 'Sa Pa',
    'hue': 'Huế',
    'hai-phong': 'Hải Phòng',
    'can-tho': 'Cần Thơ',
    'quang-ninh': 'Quảng Ninh',
    'ninh-binh': 'Ninh Bình',
    'vung-tau': 'Vũng Tàu',
    'quy-nhon': 'Quy Nhơn',
    'ha-long': 'Hạ Long',
    'mui-ne': 'Mũi Né',
    'con-dao': 'Côn Đảo',
    'tam-dao': 'Tam Đảo',
    'cat-ba': 'Cát Bà',
}


class AgodaAPI:
    """Agoda Demand API client for affiliate partners."""

    # Configurable endpoints (can be overridden via SiteSettings)
    SEARCH_URL = "https://affiliateapi7643.agoda.com/api/v2/search"
    CONTENT_FEED_URL = "https://affiliatefeed.agoda.com/datafeeds/feed/getfeed"

    def __init__(self, site_id, api_key):
        """
        Args:
            site_id: Agoda CID (e.g. '1959245')
            api_key: Full API key (e.g. '1959245:5669c3b3-...')
        """
        self.site_id = str(site_id)
        self.api_key = api_key
        self.auth_header = api_key  # format: siteId:secretKey

    # ─── SEARCH API (real-time availability & pricing) ───

    def search_hotels(self, property_ids, checkin=None, checkout=None,
                      rooms=1, adults=2, children=0, currency='VND',
                      language='vi', user_country='VN'):
        """Search for hotel availability and pricing.

        POST to Search API with property IDs.
        Returns rates and room availability.

        Args:
            property_ids: list of Agoda hotel IDs (max 100)
            checkin: YYYY-MM-DD (defaults to tomorrow)
            checkout: YYYY-MM-DD (defaults to day after tomorrow)
            rooms/adults/children: occupancy
            currency: VND, USD, etc.
            language: vi, en-us, etc.

        Returns:
            dict with 'properties' list containing availability data
        """
        if not checkin:
            checkin = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        if not checkout:
            checkout = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')

        payload = {
            "criteria": {
                "propertyIds": property_ids[:100],
                "checkIn": checkin,
                "checkOut": checkout,
                "rooms": rooms,
                "adults": adults,
                "children": children,
                "language": language,
                "currency": currency,
                "userCountry": user_country
            },
            "features": {
                "ratesPerProperty": 3 if len(property_ids) <= 30 else 1,
                "extra": ["content"]
            }
        }

        try:
            resp = requests.post(
                self.SEARCH_URL,
                json=payload,
                headers={
                    "Authorization": self.auth_header,
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return {"properties": []}

    # ─── CONTENT FEED API (static hotel data) ───

    def get_feed(self, feed_id, **params):
        """Get a content data feed from Agoda.

        Args:
            feed_id: Feed type (3=cities, 5=hotels, 7=images, 19=full profile)
            **params: Additional filter params (cityId, hotelId, etc.)

        Returns:
            list of feed items
        """
        try:
            query = {
                "token": self.api_key,
                "site_id": self.site_id,
                "feed_id": feed_id,
                **params
            }
            resp = requests.get(
                self.CONTENT_FEED_URL,
                params=query,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    return data
                return data.get('data', data.get('properties', data.get('results', [])))
        except Exception:
            pass
        return []

    def get_cities(self, country_id=192):
        """Get city list for a country (192 = Vietnam)."""
        return self.get_feed(3, countryId=country_id)

    def get_hotels_by_city(self, city_id, page=1, page_size=50):
        """Get hotels in a city using feed 5 (core hotel data)."""
        return self.get_feed(5, cityId=city_id, page=page, pageSize=page_size)

    def get_hotel_details(self, hotel_ids):
        """Get comprehensive hotel profiles (feed 19)."""
        if isinstance(hotel_ids, list):
            hotel_ids = ','.join(str(h) for h in hotel_ids)
        return self.get_feed(19, hotelIds=hotel_ids)

    def get_hotel_images(self, hotel_ids):
        """Get hotel pictures (feed 7)."""
        if isinstance(hotel_ids, list):
            hotel_ids = ','.join(str(h) for h in hotel_ids)
        return self.get_feed(7, hotelIds=hotel_ids)

    # ─── AFFILIATE LINK BUILDER ───

    def build_affiliate_url(self, hotel_id, checkin=None, checkout=None,
                            adults=2, children=0, rooms=1, currency='VND'):
        """Build Agoda affiliate booking URL with CID tracking.

        Args:
            hotel_id: Agoda property ID
            checkin/checkout: YYYY-MM-DD dates
            adults/children/rooms: occupancy

        Returns:
            str: Agoda affiliate URL
        """
        if not checkin:
            checkin = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        if not checkout:
            checkout = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')

        return (
            f"https://www.agoda.com/partners/partnersearch.aspx"
            f"?cid={self.site_id}"
            f"&hid={hotel_id}"
            f"&checkin={checkin}"
            f"&checkout={checkout}"
            f"&NumberofAdults={adults}"
            f"&NumberofChildren={children}"
            f"&Rooms={rooms}"
            f"&currency={currency}"
        )

    def build_city_search_url(self, city_id, checkin=None, checkout=None,
                              adults=2, rooms=1):
        """Build Agoda affiliate search URL for a city."""
        if not checkin:
            checkin = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        if not checkout:
            checkout = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')

        return (
            f"https://www.agoda.com/partners/partnersearch.aspx"
            f"?cid={self.site_id}"
            f"&city={city_id}"
            f"&checkin={checkin}"
            f"&checkout={checkout}"
            f"&NumberofAdults={adults}"
            f"&Rooms={rooms}"
            f"&currency=VND"
        )

    # ─── COMBINED HELPERS ───

    def search_city_hotels(self, destination_slug, checkin=None, checkout=None,
                           adults=2, rooms=1, currency='VND'):
        """High-level: search hotels by Vietnamese destination slug.

        Combines city ID lookup → content feed → pricing → affiliate links.

        Returns:
            list of hotel dicts ready to display
        """
        city_id = AGODA_CITY_IDS.get(destination_slug)
        if not city_id:
            return []

        # Get hotel list from content feed
        raw_hotels = self.get_hotels_by_city(city_id)

        results = []
        for h in raw_hotels[:50]:  # limit processing
            hotel_id = h.get('hotelId') or h.get('propertyId') or h.get('id')
            if not hotel_id:
                continue

            results.append({
                'agoda_id': hotel_id,
                'name': h.get('hotelName') or h.get('propertyName') or h.get('name', ''),
                'stars': h.get('starRating') or h.get('star_rating', 0),
                'rating': h.get('reviewScore') or h.get('rating', 0),
                'reviews_count': h.get('numberOfReviews') or h.get('reviews_count', 0),
                'latitude': h.get('latitude') or h.get('lat', 0),
                'longitude': h.get('longitude') or h.get('lng', 0),
                'address': h.get('address') or h.get('addressLine1', ''),
                'district': h.get('area') or h.get('district', ''),
                'image_url': h.get('hotelImage') or h.get('imageUrl') or h.get('image', ''),
                'price_from': h.get('dailyRate') or h.get('price') or h.get('price_from', 0),
                'amenities': h.get('facilities') or h.get('amenities', ''),
                'description': h.get('overview') or h.get('description', ''),
                'accommodation_type': h.get('accommodationType') or h.get('type', ''),
                'agoda_url': self.build_affiliate_url(hotel_id, checkin, checkout, adults, 0, rooms, currency),
                'destination': destination_slug,
                'destination_name': AGODA_CITY_NAMES.get(destination_slug, destination_slug),
            })

        # Try to get pricing if we have property IDs
        if results:
            property_ids = [r['agoda_id'] for r in results[:30]]
            pricing = self.search_hotels(property_ids, checkin, checkout, rooms, adults,
                                         currency=currency)
            price_map = {}
            for prop in pricing.get('properties', []):
                pid = prop.get('propertyId')
                rooms_data = prop.get('rooms', [])
                if rooms_data and pid:
                    cheapest = min(rooms_data, key=lambda r: r.get('totalPayment', {}).get('inclusive', 999999999))
                    price_map[pid] = {
                        'price': cheapest.get('totalPayment', {}).get('inclusive', 0),
                        'free_breakfast': cheapest.get('freeBreakfast', False),
                        'free_cancel': cheapest.get('freeCancellation', False),
                        'room_name': cheapest.get('roomName', ''),
                    }

            for r in results:
                p = price_map.get(r['agoda_id'], {})
                if p.get('price'):
                    r['price_from'] = p['price']
                r['free_breakfast'] = p.get('free_breakfast', False)
                r['free_cancel'] = p.get('free_cancel', False)
                r['room_name'] = p.get('room_name', '')

        return results

    def test_connection(self):
        """Test if API credentials are working.

        Tries a minimal search to verify auth.
        Returns dict with connection status.
        """
        try:
            # Try content feed first (lighter)
            resp = requests.get(
                self.CONTENT_FEED_URL,
                params={
                    "token": self.api_key,
                    "site_id": self.site_id,
                    "feed_id": 1,  # continents (smallest feed)
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if resp.status_code == 200:
                return {'connected': True, 'method': 'content_feed', 'status': resp.status_code}

            # Fallback: try search endpoint
            resp2 = requests.post(
                self.SEARCH_URL,
                json={
                    "criteria": {
                        "propertyIds": [12157],
                        "checkIn": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                        "checkOut": (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                        "rooms": 1, "adults": 2, "children": 0,
                        "language": "en-us", "currency": "USD", "userCountry": "VN"
                    }
                },
                headers={
                    "Authorization": self.auth_header,
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            return {'connected': resp2.status_code in (200, 201),
                    'method': 'search', 'status': resp2.status_code}
        except Exception as e:
            return {'connected': False, 'error': str(e)}


# ─── Singleton ───

_api_instance = None


def get_agoda_api(site_id=None, api_key=None):
    """Get or create Agoda API instance.

    Reads credentials from SiteSettings if not provided.
    """
    global _api_instance

    if site_id is None or api_key is None:
        from app import app, SiteSettings, AffiliateNetwork
        with app.app_context():
            if site_id is None:
                site_id = SiteSettings.get('agoda_cid', '')
            if api_key is None:
                api_key = SiteSettings.get('agoda_api_key', '')
                if not api_key:
                    net = AffiliateNetwork.query.filter_by(slug='agoda').first()
                    if net and net.api_key:
                        api_key = net.api_key

    if not site_id or not api_key:
        return None

    if _api_instance is None or _api_instance.site_id != str(site_id):
        _api_instance = AgodaAPI(site_id, api_key)

    return _api_instance
