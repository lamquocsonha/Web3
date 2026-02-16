# 🏢 Unilab - Multi-Vertical Affiliate Platform

Hệ thống quản lý đa ngành dọc (vertical) với affiliate marketing tích hợp.

## 📁 Project Structure

```
V00/
├── 📄 app.py                          # Main Flask application
├── 📄 models.py                       # Database models (SQLAlchemy)
├── 📄 seed_data.py                    # Database seeding
├── 📄 migrate_db.py                   # Auto-migration script
├── 📄 accesstrade_integration.py      # AccessTrade API integration
├── 📄 requirements.txt                # Python dependencies
├──
├── 🚀 run.bat                         # Main startup script (Windows)
├── 🚀 install.bat                     # Setup & install dependencies
├──
├── 📂 templates/                      # Jinja2 templates
│   ├── admin/                         # Admin panel templates
│   └── shared/                        # Public site templates
├──
├── 📂 static/                         # Static assets
│   └── css/                           # CSS files (general, travel, blog, finance templates)
├──
├── 📂 scripts/                        # Utility scripts & migrations
│   ├── auto_generate_content.py
│   ├── generate_lorem_articles.py
│   ├── test_accesstrade_api.py
│   └── ...
├──
├── 📂 docs/                           # Documentation
│   └── uni-flow.html                  # System flow documentation
├──
├── 📂 venv/                           # Python virtual environment
└── 📄 .gitignore                      # Git ignore rules
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
install.bat
```

### 2. Run Application
```bash
run.bat
```

### 3. Access
- 🌐 Admin: http://localhost:7000/admin
- 🚗 UniCar: http://localhost:7000/car
- 🐕 Pet: http://localhost:7000/pet
- 🚴 Bike: http://localhost:7000/bike
- ✈️ Travel: http://localhost:7000/travel

## 🎨 Features

### ✨ Multi-Vertical System
- 4 template presets: **General**, **Travel**, **Blog**, **Finance**
- Easy vertical creation with auto-styling
- Shared components across verticals

### 🔗 Affiliate Integration (AccessTrade API)
- **28 API methods** tich hop day du tu AccessTrade Publisher API
- Xem chi tiet ben duoi: [AccessTrade API Integration](#-accesstrade-api-integration)

### 📝 Content Management
- Auto-generate lorem ipsum articles
- SEO content for product categories
- Article sidebar with featured/related content
- Banner ad management

### 🗄️ Database
- SQLite (auto-created on first run)
- Auto-migration on startup
- Seed data included

## 📦 Dependencies

- Flask 3.1.0
- Flask-SQLAlchemy 3.1.1
- Requests 2.31.0

## 🛠️ Development

### Database Migrations
Auto-migrations run on app startup. Manual migration:
```bash
python migrate_db.py
```

### Generate Content
```bash
python scripts/auto_generate_content.py
```

### Test AccessTrade API
```bash
python scripts/test_accesstrade_api.py
```

## 🔗 AccessTrade API Integration

File: `accesstrade_integration.py` — Class `AccessTradeAPI`
API Docs: https://developers.accesstrade.vn/api-publisher-vietnamese

### Cau hinh

1. Vao **Admin > Settings > General**
2. Nhap **AccessTrade API Key** (lay tu https://publisher.accesstrade.vn)
3. Hoac tao record trong bang `AffiliateNetwork` voi `slug='accesstrade'`

### Danh sach API Methods

#### San pham & Catalog

| Method | Endpoint | Mo ta |
|--------|----------|-------|
| `get_datafeeds()` | `GET /v1/datafeeds` | Tim san pham tu Shopee/Lazada/Tiki. Filter theo domain, keyword, gia, discount |
| `get_top_products()` | `GET /v1/top_products` | Top san pham ban chay nhat (co aff_link san) |
| `get_product_detail()` | `GET /v1/product_detail` | Chi tiet 1 san pham: brand, shop_name, mo ta, hinh |

#### Tao Link Affiliate

| Method | Endpoint | Mo ta |
|--------|----------|-------|
| `create_tracking_link()` | `POST /v1/product_link/create` | Dan URL san pham → tu dong tao affiliate link + short link |

#### TikTok Shop

| Method | Endpoint | Mo ta |
|--------|----------|-------|
| `tiktok_search_products()` | `GET /v2/tiktokshop_product_feeds` | Tim SP tren TikTok Shop (sort: BEST_SELLERS, HIGH_COMMISSION_RATE...) |
| `tiktok_create_link()` | `POST /v2/tiktokshop_product_feeds/create_link` | Tao affiliate link tu TikTok product URL |

#### Khuyen mai & Voucher

| Method | Endpoint | Mo ta |
|--------|----------|-------|
| `get_offers()` | `GET /v1/offers_informations` | Danh sach khuyen mai (filter merchant, domain, coupon, scope) |
| `get_offers_expiring()` | — | Khuyen mai sap het han |
| `get_offers_with_coupons()` | — | Chi khuyen mai co ma giam gia |
| `get_coupons()` | `GET /v1/offers_informations/coupon` | Tim kiem ma giam gia |
| `get_coupons_hot()` | `GET /v1/offers_informations/coupon_hot` | Ma giam gia hot (tuan/thang) |
| `search_coupons_by_url()` | `GET /v1/offers_informations/coupon?URL=` | Tim voucher ap dung cho 1 URL san pham |
| `search_coupons_by_urls()` | `POST /v1/offers_informations/multi_link_2_coupons` | Tim voucher cho nhieu URL (max 5/request) |
| `get_offers_detailed()` | — | Offers voi full detail (ket hop nhieu endpoint) |
| `get_coupons_detailed()` | — | Coupons voi data phong phu |

#### Metadata

| Method | Endpoint | Mo ta |
|--------|----------|-------|
| `get_merchant_list()` | `GET /v1/offers_informations/merchant_list` | DS merchant (logo, so offer) |
| `get_keyword_list()` | `GET /v1/offers_informations/keyword_list` | DS keyword/tag (ShopeePay, FlashSale...) |
| `get_merchant_keywords()` | `GET /v1/offers_informations/icontext_list` | Keyword cua 1 merchant |
| `get_category_list()` | `GET /v1/offers_informations/list_category_coupons` | DS nganh (E-COMMERCE, BEAUTY, TRAVEL...) |

#### Campaigns & Don hang

| Method | Endpoint | Mo ta |
|--------|----------|-------|
| `get_campaigns()` | `GET /v1/campaigns` | DS chien dich (filter status active/inactive) |
| `get_campaign_by_id()` | — | Chi tiet 1 chien dich theo ID |
| `get_transactions()` | `GET /v1/transactions` | Thong ke giao dich (clicks, conversions, commission) |
| `get_order_list()` | `GET /v1/order-list` | DS don hang v2 (order_id, billing, commission, products_count, status) |
| `get_statistics_summary()` | — | Tong hop thong ke N ngay (clicks, conversions, commission) |
| `get_account_info()` | `GET /v1/me` | Thong tin tai khoan |

### Vi tri tich hop trong du an

```
Admin Dashboard (/admin)
├── KPI cards: clicks, conversions, commission (get_statistics_summary)
├── Campaigns table (get_campaigns)
├── Offers & Coupons (get_offers)
└── Don hang gan day — AJAX widget (get_order_list)

Admin Products (/admin/products)
├── [Tool] Tao Link Affiliate — paste URL → aff link (create_tracking_link)
├── [Tool] TikTok Shop Search — tim SP + tao link (tiktok_search/create_link)
└── Product table — existing products

Admin Datafeeds (/admin/products/datafeeds)
└── Tim & import SP tu AT Datafeeds (get_datafeeds)

Admin Voucher Sync (/admin/vouchers/sync)
└── Dong bo voucher tu AT (get_offers, get_coupons, get_coupons_hot)

Shop (/shop)
└── "San pham ban chay" carousel (get_top_products) — setting: hot_products_show_shop

All Sidebars (article, products, travel, shop)
└── Hot Products sidebar widget (get_top_products) — setting: hot_products_show_sidebar
```

### Admin API Endpoints (AJAX)

| Route | Method | Mo ta |
|-------|--------|-------|
| `/admin/api/create-tracking-link` | POST | Body: `{campaign_id, urls: [...]}` → tra ve aff_link + short_link |
| `/admin/api/order-list` | GET | Params: `since, until, status, merchant` → DS don hang |
| `/admin/api/tiktok-search` | GET | Params: `q, sort, limit` → DS san pham TikTok |
| `/admin/api/tiktok-create-link` | POST | Body: `{product_url}` → tra ve aff_url |

### Settings (Admin > Settings > General)

| Key | Mo ta | Default |
|-----|-------|---------|
| `accesstrade_api_key` | API key tu AccessTrade Publisher | — |
| `hot_products_enabled` | Bat/tat hot products | `0` |
| `hot_products_count` | So luong SP hien thi | `8` |
| `hot_products_show_shop` | Hien thi tren trang Shop | `1` |
| `hot_products_show_sidebar` | Hien thi sidebar cac trang khac | `1` |

## 📚 Documentation

See `docs/uni-flow.html` for detailed system flow and architecture.

---

**Developed with Claude Code** 🤖
