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
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)
    network = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(300), default='')
    url = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.Float, default=0)
    image_url = db.Column(db.String(500), default='')
    is_active = db.Column(db.Boolean, default=True)
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)

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
