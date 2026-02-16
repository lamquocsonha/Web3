from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# === CORE ===
class Vertical(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.String(10), default='')
    color = db.Column(db.String(7), default='#6c5ce7')
    description = db.Column(db.Text, default='')
    status = db.Column(db.String(10), default='draft')
    default_mode = db.Column(db.String(10), default='minimal')
    template = db.Column(db.String(20), default='general')  # Layout: general, blog, newspaper
    style = db.Column(db.String(20), default='classic')  # Theme: classic, modern, tech, beauty, car, pet
    shop_link = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    segments = db.relationship('Segment', backref='vertical', cascade='all,delete-orphan', lazy=True)

class Segment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vertical_id = db.Column(db.Integer, db.ForeignKey('vertical.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(10), default='')
    description = db.Column(db.Text, default='')
    order = db.Column(db.Integer, default=0)
    zones = db.relationship('Zone', backref='segment', cascade='all,delete-orphan', lazy=True)

class Zone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    segment_id = db.Column(db.Integer, db.ForeignKey('segment.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(10), default='')
    color = db.Column(db.String(7), default='#fdcb6e')
    description = db.Column(db.Text, default='')
    seo_content = db.Column(db.Text, default='')  # SEO content with H3-H4 headings, 100-200 lines
    order = db.Column(db.Integer, default=0)
    parts = db.relationship('Part', backref='zone', cascade='all,delete-orphan', lazy=True)

class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('zone.id'), nullable=False)
    name_vi = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), default='')
    slug = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    content = db.Column(db.Text, default='')
    image_url = db.Column(db.String(500), default='')
    oem_code = db.Column(db.String(100), default='')
    specs = db.Column(db.Text, default='')
    order = db.Column(db.Integer, default=0)
    status = db.Column(db.String(10), default='published')
    tags = db.Column(db.String(500), default='')              # auto-generated tags, comma separated
    auto_category = db.Column(db.String(100), default='')     # AI detected: phu-tung, bao-duong, nang-cap, diy
    embed_code = db.Column(db.Text, default='')               # AccessTrade/network product carousel shortcode
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    affiliate_links = db.relationship('AffiliateLink', backref='part', cascade='all,delete-orphan', lazy=True)

# === AFFILIATE ===
class AffiliateNetwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    api_key = db.Column(db.String(500), default='')
    api_url = db.Column(db.String(500), default='')
    deeplink_template = db.Column(db.String(1000), default='')  # Template for deeplink generation, e.g. "https://link.accesstrade.vn/deep_link/tp?url={url}&at_aid=123"
    color = db.Column(db.String(7), default='#6c5ce7')
    icon = db.Column(db.String(10), default='')
    commission_rate = db.Column(db.String(20), default='')
    cookie_days = db.Column(db.Integer, default=7)
    payment_cycle = db.Column(db.String(50), default='')
    status = db.Column(db.String(15), default='disconnected')
    last_sync = db.Column(db.DateTime)
    campaigns = db.relationship('AffiliateCampaign', backref='network', cascade='all,delete-orphan', lazy=True)

class AffiliateCampaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    network_id = db.Column(db.Integer, db.ForeignKey('affiliate_network.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    campaign_id_ext = db.Column(db.String(100), default='')
    commission = db.Column(db.String(50), default='')
    status = db.Column(db.String(15), default='active')
    category = db.Column(db.String(100), default='')
    url = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AffiliateLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False, index=True)
    network = db.Column(db.String(50), nullable=False, index=True)
    product_name = db.Column(db.String(300), default='')
    url = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.Float, default=0)
    image_url = db.Column(db.String(500), default='')
    is_active = db.Column(db.Boolean, default=True, index=True)
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100), default='', index=True)  # Hub category (auto-detected)

class AffiliateStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    network = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    revenue = db.Column(db.Float, default=0)
    commission = db.Column(db.Float, default=0)

# === AI CONTENT ===
class AIContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    content_type = db.Column(db.String(20), default='article')
    ai_provider = db.Column(db.String(30), default='')
    prompt = db.Column(db.Text, default='')
    result = db.Column(db.Text, default='')
    status = db.Column(db.String(15), default='draft')
    vertical_slug = db.Column(db.String(50), default='')
    part_id = db.Column(db.Integer)
    cost_tokens = db.Column(db.Integer, default=0)
    cost_vnd = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# === SETTINGS ===
class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, default='')
    category = db.Column(db.String(50), default='general')

    @staticmethod
    def get(key, default=''):
        s = SiteSettings.query.filter_by(key=key).first()
        return s.value if s else default

    @staticmethod
    def set_val(key, value, category='general'):
        s = SiteSettings.query.filter_by(key=key).first()
        if s:
            s.value = value
        else:
            s = SiteSettings(key=key, value=value, category=category)
            db.session.add(s)
        db.session.commit()

# === AI AUTO-CONTENT ENGINE ===
class ContentEvent(db.Model):
    """Calendar events: holidays, seasons, trending topics"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(20), default='holiday')  # holiday / seasonal / trending / custom
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    keywords = db.Column(db.Text, default='')
    verticals = db.Column(db.String(500), default='all')  # comma-separated slugs or 'all'
    icon = db.Column(db.String(10), default='')
    recurrence = db.Column(db.String(20), default='yearly')  # yearly / one-time
    auto_generate = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

class AutoContentRule(db.Model):
    """Rules for automatic content generation per vertical"""
    id = db.Column(db.Integer, primary_key=True)
    vertical_id = db.Column(db.Integer, db.ForeignKey('vertical.id'), nullable=False)
    vertical = db.relationship('Vertical', backref='content_rules')
    frequency = db.Column(db.String(20), default='daily')  # daily / 3x_week / weekly
    articles_per_day = db.Column(db.Integer, default=1)
    knowledge_layer = db.Column(db.String(10), default='auto')  # L1 / L2 / L3 / L4 / auto
    tone = db.Column(db.String(20), default='seo')  # casual / professional / seo
    auto_publish = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    topics_to_avoid = db.Column(db.Text, default='')
    focus_keywords = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=db.func.now())

class ContentQueue(db.Model):
    """Queue of AI-generated content items"""
    id = db.Column(db.Integer, primary_key=True)
    vertical_id = db.Column(db.Integer, db.ForeignKey('vertical.id'), nullable=False)
    vertical = db.relationship('Vertical', backref='content_queue')
    topic = db.Column(db.String(500), nullable=False)
    keywords = db.Column(db.Text, default='')
    knowledge_layer = db.Column(db.String(5), default='L1')  # L1-L4
    source_type = db.Column(db.String(20), default='ai')  # ai / manual / event
    source_event_id = db.Column(db.Integer, db.ForeignKey('content_event.id'), nullable=True)
    source_event = db.relationship('ContentEvent')
    status = db.Column(db.String(20), default='pending')  # pending / generating / review / published / skipped
    generated_content = db.Column(db.Text, default='')
    word_count = db.Column(db.Integer, default=0)
    seo_score = db.Column(db.Integer, default=0)
    scheduled_at = db.Column(db.DateTime)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.now())

# === VIDEO PRODUCTION ===
class SocialChannel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vertical_id = db.Column(db.Integer, db.ForeignKey('vertical.id'), nullable=False)
    platform = db.Column(db.String(20), nullable=False)  # tiktok / youtube / facebook
    channel_name = db.Column(db.String(200), nullable=False)
    channel_url = db.Column(db.String(500), default='')
    api_key = db.Column(db.String(500), default='')
    status = db.Column(db.String(15), default='disconnected')  # connected / disconnected
    followers = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    vertical = db.relationship('Vertical', backref='channels')

class VideoProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    vertical_slug = db.Column(db.String(50), default='')
    part_id = db.Column(db.Integer)
    video_type = db.Column(db.String(20), default='short')  # short / long / reel
    duration = db.Column(db.String(10), default='60s')       # 30s / 60s / 3min / 10min
    script = db.Column(db.Text, default='')
    voiceover_text = db.Column(db.Text, default='')
    ai_provider = db.Column(db.String(30), default='')
    status = db.Column(db.String(15), default='draft')  # draft / rendering / ready / published / failed
    thumbnail_url = db.Column(db.String(500), default='')
    video_url = db.Column(db.String(500), default='')
    caption = db.Column(db.Text, default='')
    hashtags = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    publishes = db.relationship('VideoPublish', backref='video', cascade='all,delete-orphan', lazy=True)

class VideoPublish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video_project.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('social_channel.id'), nullable=False)
    platform = db.Column(db.String(20), nullable=False)
    post_url = db.Column(db.String(500), default='')
    status = db.Column(db.String(15), default='queued')  # queued / published / failed
    scheduled_at = db.Column(db.DateTime)
    published_at = db.Column(db.DateTime)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    click_throughs = db.Column(db.Integer, default=0)
    channel = db.relationship('SocialChannel')

# === KNOWLEDGE ARTICLES ===
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vertical_slug = db.Column(db.String(50), default='')
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), nullable=False)
    excerpt = db.Column(db.Text, default='')
    content = db.Column(db.Text, default='')
    image_url = db.Column(db.String(500), default='')
    tier = db.Column(db.String(20), default='chung')  # nganh / chung / chi-tiet
    category = db.Column(db.String(100), default='')   # he-thong-treo, dong-co, phanh...
    tags = db.Column(db.String(500), default='')
    related_segment_slug = db.Column(db.String(100), default='')
    related_zone_slug = db.Column(db.String(100), default='')
    embed_code = db.Column(db.Text, default='')
    ai_generated = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(10), default='published')
    views = db.Column(db.Integer, default=0)
    reading_time = db.Column(db.Integer, default=5)  # minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    placement = db.Column(db.String(50), default='sidebar')  # sidebar / top / inline
    vertical_slug = db.Column(db.String(50), default='')  # empty = all verticals
    image_url = db.Column(db.String(500), default='')
    link_url = db.Column(db.String(500), default='')
    html_code = db.Column(db.Text, default='')  # custom HTML/script for ads
    position = db.Column(db.Integer, default=1)  # 1 = top, 2 = middle, 3 = bottom
    is_active = db.Column(db.Boolean, default=True)
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(100), nullable=False)  # da-nang, phu-quoc
    destination_name = db.Column(db.String(100), default='')
    stars = db.Column(db.Integer, default=4)
    district = db.Column(db.String(200), default='')
    description = db.Column(db.Text, default='')
    amenities = db.Column(db.String(500), default='')
    rating = db.Column(db.Float, default=8.0)
    reviews_count = db.Column(db.Integer, default=0)
    price_from = db.Column(db.Float, default=0)
    price_original = db.Column(db.Float, default=0)
    image_url = db.Column(db.String(500), default='')
    agoda_url = db.Column(db.String(1000), default='')
    booking_url = db.Column(db.String(1000), default='')
    traveloka_url = db.Column(db.String(1000), default='')
    source = db.Column(db.String(50), default='manual')  # manual, agoda_api, import
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)

class Attraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    destination_name = db.Column(db.String(100), default='')
    category = db.Column(db.String(100), default='')  # zoo, aquarium, cable_car, theme_park, museum, tour
    description = db.Column(db.Text, default='')
    address = db.Column(db.String(500), default='')
    price_from = db.Column(db.Float, default=0)
    price_original = db.Column(db.Float, default=0)
    discount_pct = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500), default='')
    rating = db.Column(db.Float, default=8.0)
    reviews_count = db.Column(db.Integer, default=0)
    network = db.Column(db.String(50), default='klook')  # klook, accesstrade, agoda
    affiliate_url = db.Column(db.String(1000), default='')
    source = db.Column(db.String(50), default='manual')
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)

class Voucher(db.Model):
    """Voucher/Discount code model - standalone feature, not tied to verticals"""
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), nullable=False, unique=True, index=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, default='')
    merchant = db.Column(db.String(100), nullable=False)  # Shopee, Lazada, Grab, etc.
    category = db.Column(db.String(50), default='general')  # food, shopping, travel, services, entertainment, tech
    discount_type = db.Column(db.String(20), default='percentage')  # percentage, fixed_amount, free_shipping
    discount_value = db.Column(db.Float, default=0)  # 10 (for 10% or 10k)
    min_order = db.Column(db.Float, default=0)  # Minimum order value
    max_discount = db.Column(db.Float, default=0)  # Maximum discount amount (for percentage)
    valid_from = db.Column(db.DateTime, default=datetime.utcnow)
    valid_to = db.Column(db.DateTime, nullable=False)
    usage_limit = db.Column(db.Integer, default=0)  # 0 = unlimited
    usage_count = db.Column(db.Integer, default=0)
    network = db.Column(db.String(50), default='shopee')  # shopee, lazada, tiki, grab, accesstrade
    affiliate_url = db.Column(db.String(1000), default='')
    terms = db.Column(db.Text, default='')  # Terms and conditions
    image_url = db.Column(db.String(500), default='')
    icon = db.Column(db.String(10), default='🎫')
    color = db.Column(db.String(7), default='#e74c3c')
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_exclusive = db.Column(db.Boolean, default=False)  # Exclusive to UniLab
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    embed_code = db.Column(db.Text, default='')  # HTML/JavaScript embed code for displaying voucher on websites
    sync_mode = db.Column(db.String(20), default='manual')  # manual, api - Data entry mode: manual entry or API sync from AccessTrade
    accesstrade_offer_id = db.Column(db.String(100), default='')  # AccessTrade offer ID for dedup during auto-sync
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_valid(self):
        """Check if voucher is currently valid"""
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        if (self.usage_limit or 0) > 0 and (self.usage_count or 0) >= self.usage_limit:
            return False
        return True

    def get_discount_text(self):
        """Get human-readable discount text"""
        val = self.discount_value or 0
        if self.discount_type == 'percentage':
            return f'Giảm {int(val)}%'
        elif self.discount_type == 'fixed_amount':
            return f'Giảm {int(val):,}đ'
        elif self.discount_type == 'free_shipping':
            return 'Freeship'
        return f'Giảm {int(val)}%'
class ArticleFeedback(db.Model):
    """User feedback on article accuracy"""
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    feedback_type = db.Column(db.String(50), nullable=False)  # inaccurate, outdated, incomplete, misleading, other
    description = db.Column(db.Text, default='')  # Optional user description
    user_email = db.Column(db.String(200), default='')  # Optional user email
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, resolved, dismissed
    admin_note = db.Column(db.Text, default='')  # Admin notes on feedback
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    article = db.relationship('Article', backref=db.backref('feedbacks', lazy=True))

class ScheduledCSVImport(db.Model):
    """Scheduled CSV import jobs for auto-updating products"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # Job name for identification
    csv_url = db.Column(db.String(1000), nullable=False)  # URL to CSV file (Google Sheets, Dropbox, etc.)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)  # Target part for products
    network = db.Column(db.String(50), default='shopee')  # Affiliate network
    apply_deeplink = db.Column(db.Boolean, default=False)  # Apply deeplink template
    update_interval_days = db.Column(db.Integer, default=7)  # Auto-update every N days
    is_active = db.Column(db.Boolean, default=True)
    last_import_at = db.Column(db.DateTime, nullable=True)  # Last successful import
    next_import_at = db.Column(db.DateTime, nullable=True)  # Next scheduled import
    last_import_count = db.Column(db.Integer, default=0)  # Number of products in last import
    last_import_status = db.Column(db.String(20), default='pending')  # pending, success, error
    last_error = db.Column(db.Text, default='')  # Last error message if any
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    part = db.relationship('Part', backref=db.backref('scheduled_imports', lazy=True))

class HotDeal(db.Model):
    """Hot deal campaigns uploaded from Excel (Hot_deal.xlsx)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    campaign = db.Column(db.String(200), default='')
    product_link = db.Column(db.String(1000), default='')
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='')
    hot_day = db.Column(db.String(100), default='')
    banner = db.Column(db.Text, default='')  # JSON array of banner image URLs
    detail = db.Column(db.Text, default='')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_valid(self):
        """Check if deal is currently active and not expired"""
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    def get_banner_urls(self):
        """Parse banner JSON to get list of image URLs"""
        if not self.banner:
            return []
        try:
            import json
            data = json.loads(self.banner)
            if isinstance(data, list):
                return [item.get('link', '') for item in data if item.get('link')]
            return []
        except:
            return []

class VoucherWidget(db.Model):
    """Voucher embed widgets from affiliate networks (AccessTrade, etc.)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # Widget name for identification
    network = db.Column(db.String(50), default='accesstrade')  # accesstrade, shopee, lazada
    embed_code = db.Column(db.Text, nullable=False)  # HTML/JavaScript embed code from network
    description = db.Column(db.Text, default='')  # Description or notes
    placement = db.Column(db.String(50), default='voucher_page')  # voucher_page, sidebar, homepage
    position = db.Column(db.Integer, default=1)  # Display order
    is_active = db.Column(db.Boolean, default=True)  # Show/hide widget
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
