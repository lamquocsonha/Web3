from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Vertical, Segment, Zone, Part, AffiliateLink, AffiliateNetwork, AffiliateCampaign, AffiliateStats, AIContent, SiteSettings, SocialChannel, VideoProject, VideoPublish, Article, Banner, Hotel, Attraction, Voucher, ArticleFeedback, ScheduledCSVImport, VoucherWidget, ContentEvent, AutoContentRule, ContentQueue
from datetime import datetime, date, timedelta
import os, random, json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unilab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'unilab-secret-2026'
# SQLite concurrency: WAL mode allows reads during writes, busy_timeout waits instead of failing
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'timeout': 30},  # sqlite3 connect timeout (seconds)
}
db.init_app(app)

# Set SQLite pragmas for better concurrency (WAL + busy_timeout)
def _set_sqlite_pragmas(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

from sqlalchemy import event
with app.app_context():
    event.listen(db.engine, "connect", _set_sqlite_pragmas)

# ═══════════════════════════════════════════
# THEME STYLES CONFIG
# ═══════════════════════════════════════════
THEME_STYLES = {
    # ── Fallback / generic ──────────────────────────────────────
    'classic': {
        'font_primary': "'DM Sans', 'Inter', -apple-system, system-ui, sans-serif",
        'font_secondary': "'DM Mono', 'Inter', sans-serif",
        'bg_light': '#ffffff', 'bg_dark': '#1a1a1a',
        'surface_light': '#f8f9fa', 'surface_dark': '#2d2d2d',
        'border_light': '#dee2e6', 'border_dark': '#444444',
        'text_light': '#212529', 'text_dark': '#f8f9fa',
        'text_dim_light': '#6c757d', 'text_dim_dark': '#adb5bd',
        'accent': '#007bff', 'accent_hover': '#0056b3',
        'radius': '8px',
    },
    'modern': {
        'font_primary': "'Inter', -apple-system, system-ui, sans-serif",
        'font_secondary': "'DM Mono', monospace",
        'bg_light': '#fafafa', 'bg_dark': '#0a0a0a',
        'surface_light': '#ffffff', 'surface_dark': '#161616',
        'border_light': '#e5e5e5', 'border_dark': '#2a2a2a',
        'text_light': '#0a0a0a', 'text_dark': '#fafafa',
        'text_dim_light': '#737373', 'text_dim_dark': '#a3a3a3',
        'accent': '#111111', 'accent_hover': '#444444',
        'radius': '12px',
    },

    # ── Car  ·  Mạnh mẽ, cơ khí, premium ───────────────────────
    'car': {
        'font_primary': "'Barlow', 'Roboto', -apple-system, sans-serif",
        'font_secondary': "'Barlow Condensed', 'Roboto Condensed', sans-serif",
        'bg_light': '#f4f3f0', 'bg_dark': '#111111',
        'surface_light': '#ffffff', 'surface_dark': '#1c1c1c',
        'border_light': '#ddd9d0', 'border_dark': '#333333',
        'text_light': '#1a1a1a', 'text_dark': '#f0ede8',
        'text_dim_light': '#7a756b', 'text_dim_dark': '#9e9889',
        'accent': '#f39c12', 'accent_hover': '#d68910',
        'radius': '6px',
    },

    # ── Beauty  ·  Sang trọng, nữ tính, thanh lịch ─────────────
    'beauty': {
        'font_primary': "'Playfair Display', 'DM Sans', -apple-system, sans-serif",
        'font_secondary': "'Montserrat', sans-serif",
        'bg_light': '#fdf6f9', 'bg_dark': '#1a0f16',
        'surface_light': '#ffffff', 'surface_dark': '#2a1a24',
        'border_light': '#f2d5e0', 'border_dark': '#4a2d40',
        'text_light': '#2a1a24', 'text_dark': '#fdf6f9',
        'text_dim_light': '#957a8a', 'text_dim_dark': '#c5a3b5',
        'accent': '#e84393', 'accent_hover': '#d63384',
        'radius': '16px',
    },

    # ── Tech  ·  Sắc nét, tối giản, hi-tech ────────────────────
    'tech': {
        'font_primary': "'Space Grotesk', 'Inter', -apple-system, sans-serif",
        'font_secondary': "'JetBrains Mono', 'Fira Code', monospace",
        'bg_light': '#f0f1f5', 'bg_dark': '#09090b',
        'surface_light': '#ffffff', 'surface_dark': '#131318',
        'border_light': '#d4d4dc', 'border_dark': '#27272f',
        'text_light': '#09090b', 'text_dark': '#f0f1f5',
        'text_dim_light': '#62626b', 'text_dim_dark': '#9494a0',
        'accent': '#6c5ce7', 'accent_hover': '#5a4bd1',
        'radius': '4px',
    },

    # ── Pet  ·  Ấm áp, thân thiện, vui nhộn ────────────────────
    'pet': {
        'font_primary': "'Quicksand', 'Nunito', sans-serif",
        'font_secondary': "'Nunito', sans-serif",
        'bg_light': '#fef9f3', 'bg_dark': '#181410',
        'surface_light': '#ffffff', 'surface_dark': '#262018',
        'border_light': '#f0dfc8', 'border_dark': '#443a28',
        'text_light': '#2c2416', 'text_dark': '#fef9f3',
        'text_dim_light': '#8a7a64', 'text_dim_dark': '#b8a88e',
        'accent': '#e17055', 'accent_hover': '#d35a3f',
        'radius': '20px',
    },

    # ── Travel  ·  Phiêu lưu, thoáng đãng, tự do ──────────────
    'travel': {
        'font_primary': "'Outfit', 'Inter', -apple-system, sans-serif",
        'font_secondary': "'DM Sans', 'Inter', sans-serif",
        'bg_light': '#f4f8fc', 'bg_dark': '#0c1218',
        'surface_light': '#ffffff', 'surface_dark': '#161e28',
        'border_light': '#d0dfe8', 'border_dark': '#2a3a4a',
        'text_light': '#0c1218', 'text_dark': '#f4f8fc',
        'text_dim_light': '#5a7a90', 'text_dim_dark': '#7fa0b8',
        'accent': '#0984e3', 'accent_hover': '#0770c2',
        'radius': '12px',
    },

    # ── Bike  ·  Năng động, đô thị, trẻ trung ──────────────────
    'bike': {
        'font_primary': "'Archivo', 'Inter', -apple-system, sans-serif",
        'font_secondary': "'Archivo Narrow', 'Roboto Condensed', sans-serif",
        'bg_light': '#f2f8f8', 'bg_dark': '#0a1214',
        'surface_light': '#ffffff', 'surface_dark': '#141e22',
        'border_light': '#c8e2e2', 'border_dark': '#2a3e42',
        'text_light': '#0a1214', 'text_dark': '#f2f8f8',
        'text_dim_light': '#5a7a7e', 'text_dim_dark': '#7ea8ae',
        'accent': '#00cec9', 'accent_hover': '#00b3af',
        'radius': '8px',
    },

    # ── Sport  ·  Năng lượng, mạnh mẽ, tập trung ───────────────
    'sport': {
        'font_primary': "'Exo 2', 'Barlow', -apple-system, sans-serif",
        'font_secondary': "'Exo 2', 'Roboto', sans-serif",
        'bg_light': '#f3f7f4', 'bg_dark': '#0c110e',
        'surface_light': '#ffffff', 'surface_dark': '#161e1a',
        'border_light': '#c4dcc8', 'border_dark': '#2a3e30',
        'text_light': '#0c110e', 'text_dark': '#f3f7f4',
        'text_dim_light': '#5a7a62', 'text_dim_dark': '#7eaa88',
        'accent': '#00b894', 'accent_hover': '#009b7d',
        'radius': '6px',
    },
}

AVAILABLE_FONTS = [
    ("'Inter', -apple-system, system-ui, sans-serif", "Inter"),
    ("'DM Sans', 'Inter', sans-serif", "DM Sans"),
    ("'DM Mono', monospace", "DM Mono"),
    ("'Barlow', 'Roboto', sans-serif", "Barlow"),
    ("'Barlow Condensed', 'Roboto Condensed', sans-serif", "Barlow Condensed"),
    ("'Playfair Display', 'DM Sans', serif", "Playfair Display"),
    ("'Montserrat', sans-serif", "Montserrat"),
    ("'Space Grotesk', 'Inter', sans-serif", "Space Grotesk"),
    ("'JetBrains Mono', 'Fira Code', monospace", "JetBrains Mono"),
    ("'Quicksand', 'Nunito', sans-serif", "Quicksand"),
    ("'Nunito', sans-serif", "Nunito"),
    ("'Outfit', 'Inter', sans-serif", "Outfit"),
    ("'Archivo', 'Inter', sans-serif", "Archivo"),
    ("'Archivo Narrow', 'Roboto Condensed', sans-serif", "Archivo Narrow"),
    ("'Exo 2', 'Barlow', sans-serif", "Exo 2"),
]

def get_theme_styles():
    """Get theme styles — merge DB custom styles with hardcoded defaults"""
    styles = dict(THEME_STYLES)
    try:
        stored = SiteSettings.get('theme_styles_custom', '')
        if stored:
            custom = json.loads(stored)
            styles.update(custom)
    except:
        pass
    return styles

@app.context_processor
def inject_globals():
    try:
        site_mode = SiteSettings.get('site_mode', 'demo')
        logo_url = SiteSettings.get('logo_url', '')
        favicon_url = SiteSettings.get('favicon_url', '')

        # Voucher sidebar widget
        sidebar_vouchers = []
        vs_enabled = SiteSettings.get('voucher_sidebar_enabled', '1')
        if vs_enabled == '1':
            vs_count = int(SiteSettings.get('voucher_sidebar_count', '4'))
            sidebar_vouchers = Voucher.query.filter_by(
                is_active=True
            ).filter(
                Voucher.valid_to > datetime.utcnow()
            ).order_by(
                Voucher.is_featured.desc(),
                Voucher.discount_value.desc(),
                Voucher.created_at.desc()
            ).limit(vs_count).all()

        # Hot products widget (AccessTrade top products)
        hot_products = []
        hp_enabled = SiteSettings.get('hot_products_enabled', '0')
        hp_show_shop = SiteSettings.get('hot_products_show_shop', '1')
        hp_show_sidebar = SiteSettings.get('hot_products_show_sidebar', '1')
        if hp_enabled == '1':
            try:
                from accesstrade_integration import get_accesstrade_api
                hp_api = get_accesstrade_api()
                if hp_api:
                    hp_count = int(SiteSettings.get('hot_products_count', '8'))
                    result = hp_api.get_top_products()
                    hot_products = (result.get('data') or [])[:hp_count]
            except Exception:
                pass

        return {
            'sidebar_verticals': Vertical.query.order_by(Vertical.name).all(),
            'now': datetime.utcnow(),
            'THEME_STYLES': get_theme_styles(),
            'site_mode': site_mode,
            'site_logo_url': logo_url,
            'site_favicon_url': favicon_url,
            'sidebar_vouchers': sidebar_vouchers,
            'voucher_sidebar_position': SiteSettings.get('voucher_sidebar_position', 'after_popular'),
            'custom_head_code': SiteSettings.get('custom_head_code', ''),
            'hot_products': hot_products,
            'hot_products_show_shop': hp_show_shop,
            'hot_products_show_sidebar': hp_show_sidebar,
        }
    except:
        return {'sidebar_verticals': [], 'now': datetime.utcnow(), 'THEME_STYLES': THEME_STYLES, 'site_mode': 'demo', 'site_logo_url': '', 'site_favicon_url': '', 'sidebar_vouchers': [], 'voucher_sidebar_position': 'after_popular', 'custom_head_code': '', 'hot_products': [], 'hot_products_show_shop': '1', 'hot_products_show_sidebar': '1'}

def slugify(text):
    """Convert Vietnamese text to URL-friendly slug (no diacritics)"""
    import re, unicodedata

    # Vietnamese character mapping
    vietnamese_map = {
        'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
        'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
        'ì': 'i', 'í': 'i', 'ĩ': 'i', 'ỉ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
        'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
        'đ': 'd',
        'À': 'A', 'Á': 'A', 'Ạ': 'A', 'Ả': 'A', 'Ã': 'A',
        'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ậ': 'A', 'Ẩ': 'A', 'Ẫ': 'A',
        'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ặ': 'A', 'Ẳ': 'A', 'Ẵ': 'A',
        'È': 'E', 'É': 'E', 'Ẹ': 'E', 'Ẻ': 'E', 'Ẽ': 'E',
        'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ệ': 'E', 'Ể': 'E', 'Ễ': 'E',
        'Ì': 'I', 'Í': 'I', 'Ĩ': 'I', 'Ỉ': 'I', 'Ị': 'I',
        'Ò': 'O', 'Ó': 'O', 'Ọ': 'O', 'Ỏ': 'O', 'Õ': 'O',
        'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ộ': 'O', 'Ổ': 'O', 'Ỗ': 'O',
        'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ợ': 'O', 'Ở': 'O', 'Ỡ': 'O',
        'Ù': 'U', 'Ú': 'U', 'Ụ': 'U', 'Ủ': 'U', 'Ũ': 'U',
        'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ự': 'U', 'Ử': 'U', 'Ữ': 'U',
        'Ỳ': 'Y', 'Ý': 'Y', 'Ỵ': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y',
        'Đ': 'D'
    }

    # Replace Vietnamese characters
    for vn_char, latin_char in vietnamese_map.items():
        text = text.replace(vn_char, latin_char)

    # Normalize and remove remaining diacritics
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')

    # Remove special characters, keep only alphanumeric, spaces, and hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())

    # Replace spaces with hyphens
    text = re.sub(r'[-\s]+', '-', text)

    return text.strip('-')

# =============================================
# ADMIN — DASHBOARD
# =============================================
@app.route('/admin')
def admin_dashboard():
    verticals = Vertical.query.all()
    total_parts = Part.query.count()
    total_links = AffiliateLink.query.count()
    total_clicks = db.session.query(db.func.sum(AffiliateLink.clicks)).scalar() or 0
    total_conversions = db.session.query(db.func.sum(AffiliateLink.conversions)).scalar() or 0
    total_ai = AIContent.query.count()
    networks = AffiliateNetwork.query.all()

    # Fake analytics for demo
    demo_traffic = random.randint(1200, 5800)
    demo_revenue = random.randint(500000, 3500000)

    # Check if AccessTrade API is configured (no API calls here)
    from accesstrade_integration import get_accesstrade_api
    api = get_accesstrade_api()
    accesstrade_data = {'connected': api is not None}

    return render_template('admin/dashboard.html',
        verticals=verticals,
        total_parts=total_parts, total_links=total_links,
        total_clicks=total_clicks, total_conversions=total_conversions,
        total_ai=total_ai, networks=networks,
        demo_traffic=demo_traffic, demo_revenue=demo_revenue,
        accesstrade=accesstrade_data)

@app.route('/admin/api/accesstrade-data')
def admin_api_accesstrade_data():
    """Load AccessTrade data async — called via AJAX from dashboard"""
    from accesstrade_integration import get_accesstrade_api
    api = get_accesstrade_api()
    if not api:
        return jsonify({'connected': False})
    try:
        account = api.get_account_info()
        stats = api.get_statistics_summary(days=30)
        campaigns = api.get_campaigns(limit=10)
        offers = api.get_offers(limit=10)
        return jsonify({
            'connected': True,
            'account': account,
            'stats': stats,
            'campaigns': campaigns,
            'offers': offers
        })
    except Exception:
        return jsonify({'connected': False})

# =============================================
# ADMIN — VERTICALS CRUD
# =============================================
@app.route('/admin/verticals')
def admin_verticals():
    verticals = Vertical.query.order_by(Vertical.created_at.desc()).all()
    verticals_data = []
    for v in verticals:
        products_count = AffiliateLink.query.join(Part).join(Zone).join(Segment).filter(Segment.vertical_id == v.id).count()
        articles_count = Article.query.filter_by(vertical_slug=v.slug).count()
        verticals_data.append({
            'vertical': v,
            'products': products_count,
            'articles': articles_count
        })
    return render_template('admin/verticals.html', verticals=verticals, verticals_data=verticals_data)

@app.route('/admin/vertical/new', methods=['GET','POST'])
def admin_vertical_new():
    if request.method == 'POST':
        v = Vertical(
            name=request.form['name'], slug=slugify(request.form['name']),
            icon=request.form.get('icon',''), color=request.form.get('color','#6c5ce7'),
            description=request.form.get('description',''), status='draft',
            template=request.form.get('template','general'),
            style=request.form.get('style','classic'),
            shop_link=request.form.get('shop_link','')
        )
        db.session.add(v)
        db.session.commit()
        flash(f'Da tao: {v.name}', 'success')
        return redirect(url_for('admin_vertical_detail', vid=v.id))
    return render_template('admin/vertical_form.html', vertical=None)

@app.route('/admin/vertical/<int:vid>')
def admin_vertical_detail(vid):
    v = Vertical.query.get_or_404(vid)
    return render_template('admin/vertical_detail.html', vertical=v)

@app.route('/admin/vertical/<int:vid>/edit', methods=['GET','POST'])
def admin_vertical_edit(vid):
    v = Vertical.query.get_or_404(vid)
    if request.method == 'POST':
        v.name = request.form['name']
        v.icon = request.form.get('icon','')
        v.color = request.form.get('color','#6c5ce7')
        v.description = request.form.get('description','')
        v.default_mode = request.form.get('default_mode','minimal')
        v.template = request.form.get('template','general')
        v.style = request.form.get('style','classic')
        v.shop_link = request.form.get('shop_link','')
        db.session.commit()
        flash(f'Da cap nhat: {v.name}', 'success')
        return redirect(url_for('admin_vertical_detail', vid=v.id))
    return render_template('admin/vertical_form.html', vertical=v)

@app.route('/admin/vertical/<int:vid>/toggle', methods=['POST'])
def admin_vertical_toggle(vid):
    v = Vertical.query.get_or_404(vid)
    v.status = 'live' if v.status == 'draft' else 'draft'
    db.session.commit()
    flash(f'{v.name} -> {v.status.upper()}', 'success')
    return redirect(request.referrer or url_for('admin_verticals'))

@app.route('/admin/vertical/<int:vid>/delete', methods=['POST'])
def admin_vertical_delete(vid):
    v = Vertical.query.get_or_404(vid)
    db.session.delete(v)
    db.session.commit()
    flash(f'Da xoa: {v.name}', 'success')
    return redirect(url_for('admin_verticals'))

# SEGMENT CRUD
@app.route('/admin/segment/<int:sid>')
def admin_segment_detail(sid):
    s = Segment.query.get_or_404(sid)
    return render_template('admin/segment_detail.html', segment=s)

@app.route('/admin/segment/new/<int:vid>', methods=['GET','POST'])
def admin_segment_new(vid):
    v = Vertical.query.get_or_404(vid)
    if request.method == 'POST':
        s = Segment(vertical_id=v.id, name=request.form['name'], slug=slugify(request.form['name']),
                    icon=request.form.get('icon',''), description=request.form.get('description',''))
        db.session.add(s)
        db.session.commit()
        flash(f'Da tao segment: {s.name}', 'success')
        return redirect(url_for('admin_vertical_detail', vid=v.id))
    return render_template('admin/segment_form.html', vertical=v, segment=None)

@app.route('/admin/segment/<int:sid>/edit', methods=['GET','POST'])
def admin_segment_edit(sid):
    s = Segment.query.get_or_404(sid)
    if request.method == 'POST':
        s.name = request.form['name']
        s.icon = request.form.get('icon','')
        s.description = request.form.get('description','')
        db.session.commit()
        flash(f'Da cap nhat: {s.name}', 'success')
        return redirect(url_for('admin_segment_detail', sid=s.id))
    return render_template('admin/segment_form.html', vertical=s.vertical, segment=s)

@app.route('/admin/segment/<int:sid>/delete', methods=['POST'])
def admin_segment_delete(sid):
    s = Segment.query.get_or_404(sid)
    vid = s.vertical_id
    db.session.delete(s)
    db.session.commit()
    flash(f'Da xoa segment: {s.name}', 'success')
    return redirect(url_for('admin_vertical_detail', vid=vid))

# ZONE CRUD
@app.route('/admin/zone/<int:zid>')
def admin_zone_detail(zid):
    z = Zone.query.get_or_404(zid)
    return render_template('admin/zone_detail.html', zone=z)

@app.route('/admin/zone/new/<int:sid>', methods=['GET','POST'])
def admin_zone_new(sid):
    s = Segment.query.get_or_404(sid)
    if request.method == 'POST':
        z = Zone(segment_id=s.id, name=request.form['name'], slug=slugify(request.form['name']),
                 icon=request.form.get('icon',''), color=request.form.get('color','#fdcb6e'),
                 description=request.form.get('description',''))
        db.session.add(z)
        db.session.commit()
        flash(f'Da tao zone: {z.name}', 'success')
        return redirect(url_for('admin_segment_detail', sid=s.id))
    return render_template('admin/zone_form.html', segment=s, zone=None)

@app.route('/admin/zone/<int:zid>/edit', methods=['GET','POST'])
def admin_zone_edit(zid):
    z = Zone.query.get_or_404(zid)
    if request.method == 'POST':
        z.name = request.form['name']
        z.icon = request.form.get('icon','')
        z.color = request.form.get('color','#fdcb6e')
        z.description = request.form.get('description','')
        db.session.commit()
        flash(f'Da cap nhat: {z.name}', 'success')
        return redirect(url_for('admin_zone_detail', zid=z.id))
    return render_template('admin/zone_form.html', segment=z.segment, zone=z)

@app.route('/admin/zone/<int:zid>/delete', methods=['POST'])
def admin_zone_delete(zid):
    z = Zone.query.get_or_404(zid)
    sid = z.segment_id
    db.session.delete(z)
    db.session.commit()
    flash(f'Da xoa zone: {z.name}', 'success')
    return redirect(url_for('admin_segment_detail', sid=sid))

# PART CRUD
@app.route('/admin/part/new/<int:zid>', methods=['GET','POST'])
def admin_part_new(zid):
    z = Zone.query.get_or_404(zid)
    if request.method == 'POST':
        p = Part(zone_id=z.id, name_vi=request.form['name_vi'], name_en=request.form.get('name_en',''),
                 slug=slugify(request.form['name_vi']), description=request.form.get('description',''),
                 content=request.form.get('content',''), oem_code=request.form.get('oem_code',''),
                 tags=request.form.get('tags',''), auto_category=request.form.get('auto_category',''),
                 embed_code=request.form.get('embed_code',''))
        db.session.add(p)
        db.session.commit()
        flash(f'Da them: {p.name_vi}', 'success')
        return redirect(url_for('admin_zone_detail', zid=z.id))
    return render_template('admin/part_form.html', zone=z, part=None)

@app.route('/admin/part/<int:pid>', methods=['GET','POST'])
def admin_part_edit(pid):
    p = Part.query.get_or_404(pid)
    if request.method == 'POST':
        p.name_vi = request.form['name_vi']
        p.name_en = request.form.get('name_en','')
        p.description = request.form.get('description','')
        p.content = request.form.get('content','')
        p.oem_code = request.form.get('oem_code','')
        p.tags = request.form.get('tags','')
        p.auto_category = request.form.get('auto_category','')
        p.embed_code = request.form.get('embed_code','')
        db.session.commit()
        flash(f'Da cap nhat: {p.name_vi}', 'success')
        return redirect(url_for('admin_zone_detail', zid=p.zone_id))
    return render_template('admin/part_form.html', zone=p.zone, part=p)

@app.route('/admin/part/<int:pid>/delete', methods=['POST'])
def admin_part_delete(pid):
    p = Part.query.get_or_404(pid)
    zid = p.zone_id
    db.session.delete(p)
    db.session.commit()
    flash(f'Da xoa: {p.name_vi}', 'success')
    return redirect(url_for('admin_zone_detail', zid=zid))

@app.route('/admin/part/<int:pid>/add-link', methods=['POST'])
def admin_add_link(pid):
    p = Part.query.get_or_404(pid)
    al = AffiliateLink(part_id=p.id, network=request.form['network'],
        product_name=request.form.get('product_name',''), url=request.form['url'],
        price=float(request.form.get('price',0)))
    db.session.add(al)
    db.session.commit()
    flash('Da them affiliate link', 'success')
    return redirect(url_for('admin_part_edit', pid=p.id))

@app.route('/admin/link/<int:lid>/delete', methods=['POST'])
def admin_delete_link(lid):
    al = AffiliateLink.query.get_or_404(lid)
    pid = al.part_id
    db.session.delete(al)
    db.session.commit()
    flash('Da xoa link', 'success')
    return redirect(url_for('admin_part_edit', pid=pid))

# =============================================
# ADMIN — AFFILIATE HUB
# =============================================
@app.route('/admin/affiliate')
def admin_affiliate():
    networks = AffiliateNetwork.query.all()
    total_clicks = db.session.query(db.func.sum(AffiliateLink.clicks)).scalar() or 0
    total_conv = db.session.query(db.func.sum(AffiliateLink.conversions)).scalar() or 0
    total_links = AffiliateLink.query.count()
    return render_template('admin/affiliate.html', networks=networks,
        total_clicks=total_clicks, total_conv=total_conv, total_links=total_links)

@app.route('/admin/affiliate/network/<int:nid>')
def admin_affiliate_network(nid):
    n = AffiliateNetwork.query.get_or_404(nid)
    extra = {}
    if n.slug == 'agoda':
        extra = {
            'site_id': SiteSettings.get('agoda_site_id', ''),
            'cid': SiteSettings.get('agoda_cid', ''),
            'enabled': SiteSettings.get('agoda_enabled', '0') == '1',
        }
    return render_template('admin/affiliate_network.html', network=n, extra=extra)

@app.route('/admin/affiliate/network/<int:nid>/connect', methods=['POST'])
def admin_affiliate_connect(nid):
    n = AffiliateNetwork.query.get_or_404(nid)
    n.api_key = request.form.get('api_key','')
    n.status = 'connected' if n.api_key else 'disconnected'
    n.last_sync = datetime.utcnow()
    # Handle Agoda extra fields
    if n.slug == 'agoda':
        SiteSettings.set_val('agoda_api_key', n.api_key, 'api')
        SiteSettings.set_val('agoda_site_id', request.form.get('site_id', ''), 'api')
        SiteSettings.set_val('agoda_cid', request.form.get('cid', ''), 'api')
        enabled = '1' if request.form.get('enabled') else '0'
        SiteSettings.set_val('agoda_enabled', enabled, 'general')
        n.status = 'connected' if enabled == '1' and n.api_key else 'disconnected'
    db.session.commit()
    flash(f'{n.name} -> {"Connected" if n.status=="connected" else "Disconnected"}', 'success')
    return redirect(url_for('admin_affiliate_network', nid=n.id))

@app.route('/admin/affiliate/network/<int:nid>/sync', methods=['POST'])
def admin_affiliate_sync(nid):
    """Sync campaigns from affiliate network API"""
    n = AffiliateNetwork.query.get_or_404(nid)
    if not n.api_key:
        flash('API key required to sync', 'error')
        return redirect(url_for('admin_affiliate_network', nid=n.id))

    try:
        import requests as req
        synced = 0

        if n.slug == 'accesstrade':
            headers = {'Authorization': f'Token {n.api_key}', 'Content-Type': 'application/json'}
            cat_map = {'26':'Insurance','29':'Finance','35':'Banking','59':'E-Commerce',
                       '60':'Retail','63':'Travel','65':'Education','66':'Services',
                       '67':'Food & Beverage','68':'Beauty & Health','69':'Technology','71':'Telecom'}
            # Fetch all pages of campaigns
            all_campaigns = []
            page = 1
            while True:
                r = req.get(f'https://api.accesstrade.vn/v1/campaigns?page={page}', headers=headers, timeout=30)
                if r.status_code != 200:
                    break
                data = r.json()
                all_campaigns.extend(data.get('data', []))
                total_pages = int(data.get('total_page', 1))
                if page >= total_pages:
                    break
                page += 1

            # Clear old campaigns for this network
            AffiliateCampaign.query.filter_by(network_id=n.id).delete()

            # Insert fresh data
            for c in all_campaigns:
                cat = c.get('category', '')
                if cat.isdigit():
                    cat = cat_map.get(cat, cat)
                sub = c.get('sub_category', '')
                if sub and not sub.isdigit():
                    cat = sub.split(',')[0]
                camp = AffiliateCampaign(
                    network_id=n.id,
                    name=c.get('name', ''),
                    campaign_id_ext=str(c.get('id', '')),
                    commission=str(c.get('max_com', '')),
                    status='active' if c.get('status') == 1 else 'inactive',
                    category=cat,
                    url=c.get('url', '')
                )
                db.session.add(camp)
                synced += 1

            # Also sync offers/vouchers
            import re as re_mod
            try:
                r2 = req.get('https://api.accesstrade.vn/v1/offers_informations', headers=headers, timeout=60)
                if r2.status_code == 200:
                    offers = r2.json().get('data', [])
                    Voucher.query.filter_by(sync_mode='api', network='accesstrade').delete()
                    voucher_count = 0
                    for o in offers:
                        oname = o.get('name', '')
                        coupons = o.get('coupons', [])
                        coupon_code = coupons[0].get('coupon_code', '') if coupons else ''
                        coupon_desc = coupons[0].get('coupon_desc', '') if coupons else ''
                        desc_text = coupon_desc or oname
                        d_type, d_val, d_min, d_max = 'percentage', 0, 0, 0
                        pct = re_mod.search(r'Giảm (\d+)%', desc_text)
                        if pct:
                            d_val = float(pct.group(1))
                        fix = re_mod.search(r'Giảm ([\d,]+)\s*VNĐ', desc_text)
                        if fix and not pct:
                            d_type, d_val = 'fixed_amount', float(fix.group(1).replace(',', ''))
                        mx = re_mod.search(r'tối đa ([\d,]+)\s*VNĐ', desc_text)
                        if mx:
                            d_max = float(mx.group(1).replace(',', ''))
                        mn = re_mod.search(r'tối thiểu ([\d,]+)\s*VNĐ', desc_text)
                        if mn:
                            d_min = float(mn.group(1).replace(',', ''))
                        merchant = o.get('merchant', 'shopee')
                        bm = re_mod.match(r'\[(.+?)\]', oname)
                        if bm:
                            merchant = bm.group(1)
                        st = o.get('start_time', '')
                        et = o.get('end_time', '')
                        try:
                            vf = datetime.strptime(st, '%Y-%m-%d') if st else datetime.utcnow()
                            vt = datetime.strptime(et, '%Y-%m-%d') if et else datetime.utcnow()
                        except:
                            vf = vt = datetime.utcnow()
                        v = Voucher(code=coupon_code or o.get('id', ''), title=oname, description=coupon_desc,
                                    merchant=merchant, category='shopping', discount_type=d_type,
                                    discount_value=d_val, min_order=d_min, max_discount=d_max,
                                    valid_from=vf, valid_to=vt, network='accesstrade',
                                    affiliate_url=o.get('aff_link', ''), image_url=o.get('image', ''),
                                    is_active=True, sync_mode='api')
                        db.session.add(v)
                        voucher_count += 1
                    synced += voucher_count
            except:
                pass  # Voucher sync is optional, don't fail the whole sync

        n.last_sync = datetime.utcnow()
        db.session.commit()
        flash(f'Synced {synced} campaigns from {n.name}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Sync error: {str(e)}', 'error')

    return redirect(url_for('admin_affiliate_network', nid=n.id))

@app.route('/admin/affiliate/performance')
def admin_affiliate_performance():
    networks = AffiliateNetwork.query.all()
    stats = AffiliateStats.query.order_by(AffiliateStats.date.desc()).limit(30).all()
    return render_template('admin/affiliate_performance.html', networks=networks, stats=stats)

@app.route('/admin/affiliate/deeplinks')
def admin_deeplinks():
    """Manage deeplink templates for affiliate networks"""
    networks = AffiliateNetwork.query.all()
    return render_template('admin/deeplinks.html', networks=networks)

@app.route('/admin/affiliate/deeplink/<int:nid>/update', methods=['POST'])
def admin_deeplink_update(nid):
    """Update deeplink template for a network"""
    network = AffiliateNetwork.query.get_or_404(nid)
    network.deeplink_template = request.form.get('deeplink_template', '')
    db.session.commit()
    flash(f'Đã cập nhật deeplink template cho {network.name}', 'success')
    return redirect(url_for('admin_deeplinks'))

# =============================================
# ADMIN — AI CONTENT
# =============================================
@app.route('/admin/content')
def admin_content():
    contents = AIContent.query.order_by(AIContent.created_at.desc()).all()
    total_cost = db.session.query(db.func.sum(AIContent.cost_vnd)).scalar() or 0
    return render_template('admin/content.html', contents=contents, total_cost=total_cost)

@app.route('/admin/content/generate', methods=['GET','POST'])
def admin_content_generate():
    verticals = Vertical.query.all()
    if request.method == 'POST':
        ai = AIContent(
            title=request.form['title'], content_type=request.form.get('content_type','article'),
            ai_provider=request.form.get('ai_provider','openai'), prompt=request.form.get('prompt',''),
            result='[AI content will be generated here when API is connected]',
            status='draft', vertical_slug=request.form.get('vertical_slug',''),
            cost_tokens=random.randint(500,2000), cost_vnd=random.randint(800,2000)
        )
        db.session.add(ai)
        db.session.commit()
        flash(f'Da tao content: {ai.title}', 'success')
        return redirect(url_for('admin_content'))
    return render_template('admin/content_generate.html', verticals=verticals)

@app.route('/admin/content/<int:cid>')
def admin_content_detail(cid):
    c = AIContent.query.get_or_404(cid)
    return render_template('admin/content_detail.html', content=c)

@app.route('/admin/content/<int:cid>/delete', methods=['POST'])
def admin_content_delete(cid):
    c = AIContent.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    flash('Da xoa content', 'success')
    return redirect(url_for('admin_content'))

# =============================================
# ADMIN — ANALYTICS
# =============================================
@app.route('/admin/analytics')
def admin_analytics():
    verticals = Vertical.query.all()
    return render_template('admin/analytics.html', verticals=verticals)

# =============================================
# ADMIN — SETTINGS
# =============================================
@app.route('/admin/settings', methods=['GET','POST'])
def admin_settings():
    tab = request.args.get('tab', 'general')
    if request.method == 'POST':
        tab = request.form.get('_tab', 'general')
        # Only save keys relevant to current tab (avoid wiping other tabs)
        tab_keys = {
            'general': ['site_mode', 'site_name', 'default_mode', 'carousel_product_limit', 'logo_url', 'favicon_url',
                        'voucher_sidebar_enabled', 'voucher_sidebar_count', 'voucher_sidebar_position',
                        'shop_display_mode', 'custom_head_code',
                        'hot_products_enabled', 'hot_products_count',
                        'hot_products_show_shop', 'hot_products_show_sidebar'],
            'api': ['openai_key', 'claude_key', 'dalle_key', 'deepl_key'],
        }
        keys_to_save = tab_keys.get(tab, [])
        for key in keys_to_save:
            val = request.form.get(key, '')
            cat = 'api' if '_key' in key or '_id' in key or '_cid' in key else 'general'
            SiteSettings.set_val(key, val, cat)
        flash('Settings saved!', 'success')
        return redirect(url_for('admin_settings', tab=tab))
    settings = {s.key: s.value for s in SiteSettings.query.all()}
    styles = get_theme_styles()
    # Determine which are custom (editable) vs default
    custom_raw = SiteSettings.get('theme_styles_custom', '{}')
    try:
        custom_names = set(json.loads(custom_raw).keys())
    except:
        custom_names = set()
    return render_template('admin/settings.html', settings=settings, styles=styles,
                           active_tab=tab, custom_names=custom_names,
                           default_names=set(THEME_STYLES.keys()),
                           available_fonts=AVAILABLE_FONTS)

@app.route('/admin/settings/styles', methods=['POST'])
def admin_settings_styles():
    action = request.form.get('action', 'save')
    name = request.form.get('style_name', '').strip().lower().replace(' ', '-')

    if action == 'delete' and name:
        custom = json.loads(SiteSettings.get('theme_styles_custom', '{}'))
        custom.pop(name, None)
        SiteSettings.set_val('theme_styles_custom', json.dumps(custom), 'styles')
        flash(f'Deleted style "{name}"', 'success')
    elif action == 'save' and name:
        style = {
            'font_primary': request.form.get('font_primary', "'Inter', sans-serif"),
            'font_secondary': request.form.get('font_secondary', "'DM Mono', monospace"),
            'bg_light': request.form.get('bg_light', '#ffffff'),
            'bg_dark': request.form.get('bg_dark', '#1a1a1a'),
            'surface_light': request.form.get('surface_light', '#f8f9fa'),
            'surface_dark': request.form.get('surface_dark', '#2d2d2d'),
            'border_light': request.form.get('border_light', '#dee2e6'),
            'border_dark': request.form.get('border_dark', '#444444'),
            'text_light': request.form.get('text_light', '#212529'),
            'text_dark': request.form.get('text_dark', '#f8f9fa'),
            'text_dim_light': request.form.get('text_dim_light', '#6c757d'),
            'text_dim_dark': request.form.get('text_dim_dark', '#adb5bd'),
            'accent': request.form.get('accent', '#007bff'),
            'accent_hover': request.form.get('accent_hover', '#0056b3'),
            'radius': request.form.get('radius', '8px'),
        }
        custom = json.loads(SiteSettings.get('theme_styles_custom', '{}'))
        custom[name] = style
        SiteSettings.set_val('theme_styles_custom', json.dumps(custom), 'styles')
        flash(f'Style "{name}" saved!', 'success')

    return redirect(url_for('admin_settings', tab='styles'))

@app.route('/admin/toggle-mode', methods=['POST'])
def admin_toggle_mode():
    """Quick toggle site mode between demo and live"""
    current = SiteSettings.get('site_mode', 'demo')
    new_mode = 'live' if current == 'demo' else 'demo'
    SiteSettings.set_val('site_mode', new_mode, 'general')
    flash(f'Site mode switched to {new_mode.upper()}', 'success')
    return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/admin/deployment')
def admin_deployment():
    """Deployment guide and workflow documentation"""
    return render_template('admin/deployment.html')

# =============================================
# ADMIN — SEED DATA
# =============================================
@app.route('/admin/seed-data', methods=['GET', 'POST'])
def admin_seed_data():
    """Seed data management - manually trigger seeding"""
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'seed_car':
            from seed_data import seed, seed_articles, seed_networks, seed_products_pet_travel
            try:
                seed()
                seed_articles()
                seed_networks()
                flash('✅ Car vertical seeded successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error seeding Car: {str(e)}', 'error')

        elif action == 'seed_pet':
            from seed_data import seed_pet, seed_pet_articles, seed_products_pet_travel, seed_pet_v2
            try:
                seed_pet()
                seed_pet_articles()
                seed_pet_v2()
                flash('✅ Pet vertical seeded successfully! (v2 included)', 'success')
            except Exception as e:
                flash(f'❌ Error seeding Pet: {str(e)}', 'error')

        elif action == 'seed_travel':
            from seed_data import seed_travel, seed_travel_articles, seed_hotels, seed_attractions, seed_products_pet_travel
            try:
                seed_travel()
                seed_travel_articles()
                seed_hotels()
                seed_attractions()
                flash('✅ Travel vertical seeded successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error seeding Travel: {str(e)}', 'error')

        elif action == 'seed_bike':
            from seed_data import seed_bike
            try:
                seed_bike()
                flash('✅ Bike vertical seeded successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error seeding Bike: {str(e)}', 'error')

        elif action == 'seed_beauty':
            from seed_data import seed_beauty, seed_beauty_articles, seed_products_beauty_tech
            try:
                seed_beauty()
                seed_beauty_articles()
                seed_products_beauty_tech()
                flash('✅ Beauty vertical seeded successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error seeding Beauty: {str(e)}', 'error')

        elif action == 'seed_tech':
            from seed_data import seed_tech, seed_tech_articles, seed_products_beauty_tech
            try:
                seed_tech()
                seed_tech_articles()
                seed_products_beauty_tech()
                flash('✅ Tech vertical seeded successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error seeding Tech: {str(e)}', 'error')

        elif action == 'seed_sport':
            from seed_data import seed_sport, seed_sport_articles, seed_products_sport
            try:
                seed_sport()
                seed_sport_articles()
                seed_products_sport()
                flash('✅ Sport vertical seeded successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error seeding Sport: {str(e)}', 'error')

        elif action == 'seed_all':
            from seed_data import (seed, seed_articles, seed_networks, seed_video,
                seed_pet, seed_pet_articles, seed_pet_v2, seed_travel, seed_travel_articles,
                seed_products_pet_travel, seed_hotels, seed_attractions,
                seed_bike, seed_vouchers, seed_beauty, seed_beauty_articles,
                seed_tech, seed_tech_articles, seed_products_beauty_tech,
                seed_sport, seed_sport_articles, seed_products_sport)
            try:
                seed()
                seed_articles()
                seed_networks()
                seed_pet()
                seed_pet_articles()
                seed_pet_v2()
                seed_travel()
                seed_travel_articles()
                seed_products_pet_travel()
                seed_hotels()
                seed_attractions()
                seed_bike()
                seed_vouchers()
                seed_beauty()
                seed_beauty_articles()
                seed_tech()
                seed_tech_articles()
                seed_products_beauty_tech()
                seed_sport()
                seed_sport_articles()
                seed_products_sport()
                flash('✅ All verticals seeded successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error seeding all: {str(e)}', 'error')

        return redirect(url_for('admin_seed_data'))

    # Get stats for each vertical
    verticals_data = []
    for v in Vertical.query.all():
        segments_count = len(v.segments)
        zones_count = Zone.query.join(Segment).filter(Segment.vertical_id == v.id).count()
        parts_count = Part.query.join(Zone).join(Segment).filter(Segment.vertical_id == v.id).count()
        articles_count = Article.query.filter_by(vertical_slug=v.slug).count()
        products_count = AffiliateLink.query.join(Part).join(Zone).join(Segment).filter(Segment.vertical_id == v.id).count()

        verticals_data.append({
            'vertical': v,
            'segments': segments_count,
            'zones': zones_count,
            'parts': parts_count,
            'articles': articles_count,
            'products': products_count
        })

    return render_template('admin/seed_data.html', verticals_data=verticals_data)

# =============================================
# ADMIN — AI CHAT ASSISTANT
# =============================================
@app.route('/admin/ai-chat', methods=['POST'])
def admin_ai_chat():
    """AI Assistant endpoint - handles chat messages and executes actions"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Get OpenAI API key from settings
        openai_key = SiteSettings.get_val('openai_key')
        if not openai_key:
            return jsonify({
                'response': 'OpenAI API key chưa được cấu hình. Vui lòng thêm API key trong Settings.'
            })

        # Prepare system context
        verticals = Vertical.query.all()
        total_articles = Article.query.count()
        total_products = AffiliateLink.query.count()

        system_prompt = f"""You are an AI assistant for the Unilab admin panel. You help administrators manage content, products, and operations.

Current System State:
- Verticals: {', '.join([v.name for v in verticals])}
- Total Articles: {total_articles}
- Total Products: {total_products}

You can help with:
1. Writing articles (provide title, content, tier, vertical)
2. Adding products (provide product info)
3. Creating verticals
4. Analyzing data
5. General admin tasks

When the user requests an action, respond in Vietnamese with:
1. A confirmation message
2. If creating content, provide the structure in JSON format

Keep responses concise and actionable."""

        # Call OpenAI API
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content

        # Parse response for actions
        action = None

        # Check if AI wants to create an article
        if 'tạo bài' in user_message.lower() or 'viết bài' in user_message.lower():
            # Suggest redirecting to article creation page
            action = {
                'type': 'redirect',
                'url': '/admin/article/new'
            }

        return jsonify({
            'response': ai_response,
            'action': action
        })

    except Exception as e:
        return jsonify({
            'response': f'Có lỗi xảy ra: {str(e)}'
        }), 500

# =============================================
# ADMIN — ARTICLES (Knowledge Base)
# =============================================
@app.route('/admin/articles')
def admin_articles():
    # Get filter parameters
    vertical_filter = request.args.get('vertical', '')
    tier_filter = request.args.get('tier', '')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at')  # default sort by created_at
    sort_order = request.args.get('order', 'desc')  # default descending

    # Build query
    query = Article.query

    # Apply filters
    if vertical_filter:
        query = query.filter_by(vertical_slug=vertical_filter)
    if tier_filter:
        query = query.filter_by(tier=tier_filter)
    if search_query:
        query = query.filter(
            db.or_(
                Article.title.ilike(f'%{search_query}%'),
                Article.category.ilike(f'%{search_query}%'),
                Article.tags.ilike(f'%{search_query}%')
            )
        )

    # Apply sorting
    if sort_by == 'title':
        sort_col = Article.title
    elif sort_by == 'created_at':
        sort_col = Article.created_at
    else:
        sort_col = Article.created_at

    if sort_order == 'asc':
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    articles = query.all()

    # Get all verticals for filter dropdown
    verticals = Vertical.query.order_by(Vertical.name).all()

    # Calculate stats for all articles (not filtered)
    all_articles = Article.query.all()
    stats = {
        'total': len(all_articles),
        'nganh': len([a for a in all_articles if a.tier == 'nganh']),
        'chung': len([a for a in all_articles if a.tier == 'chung']),
        'chi_tiet': len([a for a in all_articles if a.tier == 'chi-tiet'])
    }

    return render_template('admin/articles.html',
                         articles=articles,
                         verticals=verticals,
                         stats=stats,
                         current_vertical=vertical_filter,
                         current_tier=tier_filter,
                         current_search=search_query,
                         current_sort=sort_by,
                         current_order=sort_order)

@app.route('/admin/article/new', methods=['GET','POST'])
def admin_article_new():
    verticals = Vertical.query.all()
    if request.method == 'POST':
        a = Article(
            vertical_slug=request.form.get('vertical_slug',''),
            title=request.form['title'], slug=slugify(request.form['title']),
            excerpt=request.form.get('excerpt',''), content=request.form.get('content',''),
            image_url=request.form.get('image_url',''),
            tier=request.form.get('tier','chung'), category=request.form.get('category',''),
            tags=request.form.get('tags',''),
            related_segment_slug=request.form.get('related_segment_slug',''),
            related_zone_slug=request.form.get('related_zone_slug',''),
            embed_code=request.form.get('embed_code',''),
            ai_generated='ai_generated' in request.form,
            reading_time=int(request.form.get('reading_time',5)),
            status=request.form.get('status','published')
        )
        db.session.add(a)
        db.session.commit()
        flash(f'Da tao bai viet: {a.title}', 'success')
        return redirect(url_for('admin_articles'))
    return render_template('admin/article_form.html', article=None, verticals=verticals)

@app.route('/admin/article/<int:aid>/edit', methods=['GET','POST'])
def admin_article_edit(aid):
    a = Article.query.get_or_404(aid)
    verticals = Vertical.query.all()
    if request.method == 'POST':
        a.title = request.form['title']
        a.excerpt = request.form.get('excerpt','')
        a.content = request.form.get('content','')
        a.image_url = request.form.get('image_url','')
        a.tier = request.form.get('tier','chung')
        a.category = request.form.get('category','')
        a.tags = request.form.get('tags','')
        a.related_segment_slug = request.form.get('related_segment_slug','')
        a.related_zone_slug = request.form.get('related_zone_slug','')
        a.embed_code = request.form.get('embed_code','')
        a.ai_generated = 'ai_generated' in request.form
        a.reading_time = int(request.form.get('reading_time',5))
        a.status = request.form.get('status','published')
        db.session.commit()
        flash(f'Da cap nhat: {a.title}', 'success')
        return redirect(url_for('admin_articles'))
    return render_template('admin/article_form.html', article=a, verticals=verticals)

@app.route('/admin/article/<int:aid>/delete', methods=['POST'])
def admin_article_delete(aid):
    a = Article.query.get_or_404(aid)
    db.session.delete(a)
    db.session.commit()
    flash('Da xoa bai viet', 'success')
    return redirect(url_for('admin_articles'))

# =============================================
# ADMIN — ARTICLE FEEDBACKS
# =============================================
@app.route('/admin/feedbacks')
def admin_feedbacks():
    """View all article feedbacks"""
    status_filter = request.args.get('status', 'all')

    if status_filter == 'all':
        feedbacks = ArticleFeedback.query.order_by(ArticleFeedback.created_at.desc()).all()
    else:
        feedbacks = ArticleFeedback.query.filter_by(status=status_filter).order_by(ArticleFeedback.created_at.desc()).all()

    # Count by status
    pending_count = ArticleFeedback.query.filter_by(status='pending').count()
    reviewed_count = ArticleFeedback.query.filter_by(status='reviewed').count()
    resolved_count = ArticleFeedback.query.filter_by(status='resolved').count()
    dismissed_count = ArticleFeedback.query.filter_by(status='dismissed').count()

    return render_template('admin/feedbacks.html',
        feedbacks=feedbacks,
        status_filter=status_filter,
        pending_count=pending_count,
        reviewed_count=reviewed_count,
        resolved_count=resolved_count,
        dismissed_count=dismissed_count)

@app.route('/admin/feedback/<int:fid>')
def admin_feedback_detail(fid):
    """View feedback detail"""
    feedback = ArticleFeedback.query.get_or_404(fid)
    article = Article.query.get(feedback.article_id)
    return render_template('admin/feedback_detail.html', feedback=feedback, article=article)

@app.route('/admin/feedback/<int:fid>/update-status', methods=['POST'])
def admin_feedback_update_status(fid):
    """Update feedback status"""
    feedback = ArticleFeedback.query.get_or_404(fid)
    feedback.status = request.form.get('status', 'pending')
    feedback.admin_note = request.form.get('admin_note', '')

    if feedback.status in ['reviewed', 'resolved', 'dismissed']:
        feedback.reviewed_at = datetime.utcnow()

    db.session.commit()
    flash('Đã cập nhật trạng thái phản hồi', 'success')
    return redirect(url_for('admin_feedbacks'))

@app.route('/admin/feedback/<int:fid>/delete', methods=['POST'])
def admin_feedback_delete(fid):
    """Delete feedback"""
    feedback = ArticleFeedback.query.get_or_404(fid)
    db.session.delete(feedback)
    db.session.commit()
    flash('Đã xóa phản hồi', 'success')
    return redirect(url_for('admin_feedbacks'))

# =============================================
# ADMIN — PRODUCTS (Quản lý sản phẩm tập trung)
# =============================================
@app.route('/admin/products')
def admin_products():
    # Get filter params
    f_vertical = request.args.get('vertical', '')
    f_network = request.args.get('network', '')
    f_status = request.args.get('status', '')
    f_search = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 50

    # Query with joins to get full path
    q = db.session.query(AffiliateLink, Part, Zone, Segment, Vertical).join(
        Part, AffiliateLink.part_id == Part.id
    ).join(Zone, Part.zone_id == Zone.id
    ).join(Segment, Zone.segment_id == Segment.id
    ).join(Vertical, Segment.vertical_id == Vertical.id)

    if f_vertical:
        q = q.filter(Vertical.slug == f_vertical)
    if f_network:
        q = q.filter(AffiliateLink.network == f_network)
    if f_status == 'active':
        q = q.filter(AffiliateLink.is_active == True)
    elif f_status == 'inactive':
        q = q.filter(AffiliateLink.is_active == False)
    if f_search:
        q = q.filter(db.or_(
            AffiliateLink.product_name.ilike(f'%{f_search}%'),
            Part.name_vi.ilike(f'%{f_search}%'),
            AffiliateLink.url.ilike(f'%{f_search}%')
        ))

    pagination = q.order_by(AffiliateLink.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    verticals = Vertical.query.all()
    # Get unique networks
    networks = db.session.query(AffiliateLink.network).distinct().all()
    networks = [n[0] for n in networks]

    # Stats
    total = AffiliateLink.query.count()
    active = AffiliateLink.query.filter_by(is_active=True).count()
    total_clicks = db.session.query(db.func.sum(AffiliateLink.clicks)).scalar() or 0
    total_conv = db.session.query(db.func.sum(AffiliateLink.conversions)).scalar() or 0

    return render_template('admin/products.html',
        products=products, verticals=verticals, networks=networks,
        f_vertical=f_vertical, f_network=f_network, f_status=f_status, f_search=f_search,
        total=total, active=active, total_clicks=total_clicks, total_conv=total_conv,
        pagination=pagination, page=page)

@app.route('/admin/product/new', methods=['GET','POST'])
def admin_product_new():
    if request.method == 'POST':
        al = AffiliateLink(
            part_id=int(request.form['part_id']),
            network=request.form['network'],
            product_name=request.form.get('product_name',''),
            url=request.form['url'],
            price=float(request.form.get('price', 0)),
            image_url=request.form.get('image_url',''),
            is_active='is_active' in request.form
        )
        db.session.add(al)
        db.session.commit()
        flash(f'Da them san pham: {al.product_name}', 'success')
        return redirect(url_for('admin_products'))
    # Get all parts grouped by vertical > segment > zone
    parts_tree = []
    for v in Vertical.query.all():
        for s in v.segments:
            for z in s.zones:
                for p in z.parts:
                    parts_tree.append({
                        'id': p.id,
                        'label': f'{v.icon} {v.name} › {s.name} › {z.name} › {p.name_vi}'
                    })
    return render_template('admin/product_form.html', product=None, parts_tree=parts_tree)

@app.route('/admin/product/<int:pid>/edit', methods=['GET','POST'])
def admin_product_edit(pid):
    al = AffiliateLink.query.get_or_404(pid)
    if request.method == 'POST':
        al.part_id = int(request.form['part_id'])
        al.network = request.form['network']
        al.product_name = request.form.get('product_name','')
        al.url = request.form['url']
        al.price = float(request.form.get('price', 0))
        al.image_url = request.form.get('image_url','')
        al.is_active = 'is_active' in request.form
        db.session.commit()
        flash(f'Da cap nhat: {al.product_name}', 'success')
        return redirect(url_for('admin_products'))
    parts_tree = []
    for v in Vertical.query.all():
        for s in v.segments:
            for z in s.zones:
                for p in z.parts:
                    parts_tree.append({
                        'id': p.id,
                        'label': f'{v.icon} {v.name} › {s.name} › {z.name} › {p.name_vi}'
                    })
    return render_template('admin/product_form.html', product=al, parts_tree=parts_tree)

@app.route('/admin/product/<int:pid>/toggle', methods=['POST'])
def admin_product_toggle(pid):
    al = AffiliateLink.query.get_or_404(pid)
    al.is_active = not al.is_active
    db.session.commit()
    flash(f'{"Bat" if al.is_active else "Tat"}: {al.product_name}', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/product/<int:pid>/delete', methods=['POST'])
def admin_product_delete(pid):
    al = AffiliateLink.query.get_or_404(pid)
    db.session.delete(al)
    db.session.commit()
    flash('Da xoa san pham', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/products/bulk-delete', methods=['POST'])
def admin_products_bulk_delete():
    """Delete products in bulk: by filter, by network, or all"""
    action = request.form.get('action', '')
    f_vertical = request.form.get('vertical', '')
    f_network = request.form.get('network', '')

    q = AffiliateLink.query
    label = 'tat ca'

    if action == 'delete_filtered':
        # Delete by current filters
        if f_vertical:
            q = q.join(Part).join(Zone).join(Segment).join(Vertical).filter(Vertical.slug == f_vertical)
            label = f'vertical "{f_vertical}"'
        if f_network:
            q = q.filter(AffiliateLink.network == f_network)
            label = f'network "{f_network}"' if not f_vertical else f'{label} + network "{f_network}"'
    elif action == 'delete_all':
        label = 'tat ca'
    else:
        flash('Action khong hop le', 'error')
        return redirect(url_for('admin_products'))

    count = q.count()
    if count == 0:
        flash('Khong co san pham nao de xoa', 'warning')
        return redirect(url_for('admin_products'))

    q.delete(synchronize_session=False)
    db.session.commit()
    flash(f'Da xoa {count:,} san pham ({label})', 'success')
    return redirect(url_for('admin_products'))

# =============================================
# AI CONTROL CENTER - Unified AI Operations Hub
# =============================================

@app.route('/admin/ai-center')
def admin_ai_center():
    """Unified AI Control Center - all AI operations in one place"""
    from sqlalchemy import func

    openai_key = SiteSettings.get('openai_key')
    claude_key = SiteSettings.get('claude_key')
    has_ai = bool(openai_key or claude_key)

    # ── Product Health Stats ──
    total_products = AffiliateLink.query.count()
    active_products = AffiliateLink.query.filter_by(is_active=True).count()

    # Duplicate URLs
    dup_sub = db.session.query(
        AffiliateLink.url, func.count(AffiliateLink.id).label('cnt')
    ).group_by(AffiliateLink.url).having(func.count(AffiliateLink.id) > 1).subquery()
    dup_urls = db.session.query(func.count()).select_from(dup_sub).scalar() or 0

    # Missing images
    no_image = AffiliateLink.query.filter(
        db.or_(AffiliateLink.image_url == '', AffiliateLink.image_url == None)
    ).count()

    # Price issues (0 or null)
    zero_price = AffiliateLink.query.filter(
        db.or_(AffiliateLink.price == 0, AffiliateLink.price == None)
    ).count()

    # Stale products (0 clicks)
    stale_products = AffiliateLink.query.filter(AffiliateLink.clicks == 0).count()

    # High clicks but 0 conversions (potential link issues)
    suspect_links = AffiliateLink.query.filter(
        AffiliateLink.clicks > 10, AffiliateLink.conversions == 0
    ).count()

    # Inactive products
    inactive_products = AffiliateLink.query.filter_by(is_active=False).count()

    # ── Article Health Stats ──
    total_articles = Article.query.count()
    # Thin content (content < 500 chars ~ approx 100 words)
    thin_articles = Article.query.filter(
        db.or_(func.length(Article.content) < 500, Article.content == '', Article.content == None)
    ).count()
    # No views
    zero_view_articles = Article.query.filter(
        db.or_(Article.views == 0, Article.views == None)
    ).count()
    # Articles without embed code (no products linked)
    no_product_articles = Article.query.filter(
        db.or_(Article.embed_code == '', Article.embed_code == None)
    ).count()
    # AI-generated articles
    ai_articles = Article.query.filter_by(ai_generated=True).count()

    # ── Vertical Health ──
    verticals = Vertical.query.all()
    vert_health = []
    for v in verticals:
        prod_count = db.session.query(AffiliateLink).join(Part).join(Zone).join(Segment).filter(
            Segment.vertical_id == v.id).count()
        art_count = Article.query.filter_by(vertical_slug=v.slug).count()
        part_count = db.session.query(Part).join(Zone).join(Segment).filter(
            Segment.vertical_id == v.id).count()
        # Parts with no products
        parts_no_prod = db.session.query(Part).join(Zone).join(Segment).filter(
            Segment.vertical_id == v.id
        ).outerjoin(AffiliateLink).filter(AffiliateLink.id == None).count()
        vert_health.append({
            'id': v.id, 'name': v.name, 'icon': v.icon, 'slug': v.slug,
            'products': prod_count, 'articles': art_count,
            'parts': part_count, 'parts_empty': parts_no_prod,
            'status': v.status
        })

    # ── Network Health ──
    networks = db.session.query(
        AffiliateLink.network,
        func.count(AffiliateLink.id),
        func.sum(AffiliateLink.clicks),
        func.sum(AffiliateLink.conversions)
    ).group_by(AffiliateLink.network).all()
    net_stats = [{'name': n[0], 'count': n[1], 'clicks': n[2] or 0, 'conv': n[3] or 0} for n in networks]

    # Score: overall health (0-100)
    issues_total = dup_urls + no_image + zero_price + suspect_links + thin_articles
    health_score = max(0, 100 - min(issues_total, 100))

    return render_template('admin/ai_center.html',
        has_ai=has_ai, health_score=health_score,
        total_products=total_products, active_products=active_products,
        dup_urls=dup_urls, no_image=no_image, zero_price=zero_price,
        stale_products=stale_products, suspect_links=suspect_links,
        inactive_products=inactive_products,
        total_articles=total_articles, thin_articles=thin_articles,
        zero_view_articles=zero_view_articles, no_product_articles=no_product_articles,
        ai_articles=ai_articles,
        vert_health=vert_health, net_stats=net_stats,
        verticals=verticals)

# Keep old route as redirect for backwards compatibility
@app.route('/admin/products/ai-classify')
def admin_products_ai_classify():
    return redirect(url_for('admin_ai_center'))


@app.route('/admin/ai-center/health-detail', methods=['POST'])
def admin_ai_center_health_detail():
    """AJAX: Get detailed list for a specific health issue"""
    from sqlalchemy import func
    data = request.get_json()
    issue_type = data.get('type', '')
    page = data.get('page', 1)
    per_page = 50

    results = []

    if issue_type == 'dup_urls':
        dup_urls = db.session.query(AffiliateLink.url).group_by(
            AffiliateLink.url).having(func.count(AffiliateLink.id) > 1).all()
        dup_url_list = [u[0] for u in dup_urls]
        items = AffiliateLink.query.filter(AffiliateLink.url.in_(dup_url_list)).order_by(
            AffiliateLink.url).offset((page-1)*per_page).limit(per_page).all()
        for al in items:
            results.append({'id': al.id, 'name': al.product_name, 'detail': al.url[:80],
                           'network': al.network, 'price': al.price})

    elif issue_type == 'no_image':
        items = AffiliateLink.query.filter(
            db.or_(AffiliateLink.image_url == '', AffiliateLink.image_url == None)
        ).offset((page-1)*per_page).limit(per_page).all()
        for al in items:
            results.append({'id': al.id, 'name': al.product_name, 'detail': 'Thieu hinh anh',
                           'network': al.network, 'price': al.price})

    elif issue_type == 'zero_price':
        items = AffiliateLink.query.filter(
            db.or_(AffiliateLink.price == 0, AffiliateLink.price == None)
        ).offset((page-1)*per_page).limit(per_page).all()
        for al in items:
            results.append({'id': al.id, 'name': al.product_name, 'detail': 'Gia = 0',
                           'network': al.network, 'price': 0})

    elif issue_type == 'suspect_links':
        items = AffiliateLink.query.filter(
            AffiliateLink.clicks > 10, AffiliateLink.conversions == 0
        ).order_by(AffiliateLink.clicks.desc()).offset((page-1)*per_page).limit(per_page).all()
        for al in items:
            results.append({'id': al.id, 'name': al.product_name,
                           'detail': f'{al.clicks} clicks, 0 conv',
                           'network': al.network, 'price': al.price})

    elif issue_type == 'stale':
        items = AffiliateLink.query.filter(
            AffiliateLink.clicks == 0
        ).offset((page-1)*per_page).limit(per_page).all()
        for al in items:
            results.append({'id': al.id, 'name': al.product_name, 'detail': '0 clicks',
                           'network': al.network, 'price': al.price})

    elif issue_type == 'thin_articles':
        from sqlalchemy import func as fn
        items = Article.query.filter(
            db.or_(fn.length(Article.content) < 500, Article.content == '', Article.content == None)
        ).offset((page-1)*per_page).limit(per_page).all()
        for a in items:
            results.append({'id': a.id, 'name': a.title,
                           'detail': f'{len(a.content or "")} ky tu', 'network': a.vertical_slug})

    elif issue_type == 'no_product_articles':
        items = Article.query.filter(
            db.or_(Article.embed_code == '', Article.embed_code == None)
        ).offset((page-1)*per_page).limit(per_page).all()
        for a in items:
            results.append({'id': a.id, 'name': a.title,
                           'detail': 'Chua gan san pham', 'network': a.vertical_slug})

    elif issue_type == 'parts_empty':
        vid = data.get('vertical_id')
        q = db.session.query(Part, Zone, Segment, Vertical).join(
            Zone, Part.zone_id == Zone.id).join(
            Segment, Zone.segment_id == Segment.id).join(
            Vertical, Segment.vertical_id == Vertical.id
        ).outerjoin(AffiliateLink).filter(AffiliateLink.id == None)
        if vid:
            q = q.filter(Vertical.id == vid)
        items = q.offset((page-1)*per_page).limit(per_page).all()
        for part, zone, seg, vert in items:
            results.append({'id': part.id, 'name': part.name_vi,
                           'detail': f'{vert.icon} {vert.name} > {zone.name}', 'network': ''})

    return jsonify({'results': results, 'page': page})


@app.route('/admin/ai-center/bulk-action', methods=['POST'])
def admin_ai_center_bulk_action():
    """AJAX: Perform bulk actions on products/articles from AI Center"""
    data = request.get_json()
    action = data.get('action')
    item_type = data.get('item_type', 'product')  # product or article
    ids = data.get('ids', [])

    if not ids:
        return jsonify({'error': 'Khong co item nao duoc chon'}), 400

    if item_type == 'product':
        if action == 'delete':
            count = AffiliateLink.query.filter(AffiliateLink.id.in_(ids)).delete(synchronize_session=False)
            db.session.commit()
            return jsonify({'success': True, 'message': f'Da xoa {count} san pham'})
        elif action == 'deactivate':
            AffiliateLink.query.filter(AffiliateLink.id.in_(ids)).update(
                {'is_active': False}, synchronize_session=False)
            db.session.commit()
            return jsonify({'success': True, 'message': f'Da tat {len(ids)} san pham'})
    elif item_type == 'article':
        if action == 'delete':
            count = Article.query.filter(Article.id.in_(ids)).delete(synchronize_session=False)
            db.session.commit()
            return jsonify({'success': True, 'message': f'Da xoa {count} bai viet'})

    return jsonify({'error': 'Action khong hop le'}), 400


@app.route('/admin/ai-center/ai-scan', methods=['POST'])
def admin_ai_center_ai_scan():
    """AJAX: AI-powered scan for product classification"""
    import requests as req

    data = request.get_json()
    vertical_id = data.get('vertical_id')
    offset = data.get('offset', 0)
    batch_size = min(data.get('batch_size', 20), 30)

    q = db.session.query(AffiliateLink, Part, Zone, Segment, Vertical).join(
        Part, AffiliateLink.part_id == Part.id
    ).join(Zone, Part.zone_id == Zone.id
    ).join(Segment, Zone.segment_id == Segment.id
    ).join(Vertical, Segment.vertical_id == Vertical.id)

    if vertical_id:
        q = q.filter(Vertical.id == vertical_id)

    total = q.count()
    products = q.order_by(AffiliateLink.id).offset(offset).limit(batch_size).all()

    if not products:
        return jsonify({'done': True, 'results': [], 'total': total, 'processed': offset})

    # Build vertical + zone context
    all_verticals = Vertical.query.all()
    vert_zones = {}
    for v in all_verticals:
        zones = []
        for s in v.segments:
            for z in s.zones:
                zones.append(z.name)
        vert_zones[v.name] = zones

    product_list = []
    for al, part, zone, seg, vert in products:
        product_list.append({
            'id': al.id, 'name': al.product_name or part.name_vi,
            'current_vertical': vert.name, 'current_zone': zone.name,
            'current_part': part.name_vi, 'url': (al.url or '')[:100], 'price': al.price,
        })

    # Build AI prompt
    vert_context = ""
    for vname, zones in vert_zones.items():
        vert_context += f"\n- {vname}: {', '.join(zones[:15])}"

    prompt = f"""Ban la chuyen gia phan loai san pham. Phan tich danh sach san pham duoi day va xac dinh chung thuoc nganh hang (vertical) nao.

Danh sach Verticals va cac Zone:{vert_context}

San pham can phan loai:
"""
    for i, p in enumerate(product_list):
        prompt += f"\n{i+1}. [{p['id']}] \"{p['name']}\" (hien tai: {p['current_vertical']} > {p['current_zone']})"

    prompt += """

Tra loi CHINH XAC theo format JSON array:
[{"id": <product_id>, "correct_vertical": "<ten vertical dung>", "confidence": "high/medium/low", "reason": "<ly do ngan>"}]

Chi tra ve JSON array, KHONG giai thich them. Neu san pham dang o dung vertical thi correct_vertical = vertical hien tai."""

    ai_results = _call_ai_api(prompt)

    if not ai_results:
        err_detail = getattr(_call_ai_api, 'last_error', '')
        return jsonify({'error': f'AI API loi: {err_detail}' if err_detail else 'Khong the ket noi AI API. Kiem tra API key trong Settings.'}), 500

    # Compare and build results
    results = []
    for p in product_list:
        ai_item = next((r for r in ai_results if r.get('id') == p['id']), None)
        if ai_item:
            suggested = ai_item.get('correct_vertical', p['current_vertical'])
            is_mismatch = suggested.strip().lower() != p['current_vertical'].strip().lower()
            results.append({
                'id': p['id'], 'name': p['name'],
                'current_vertical': p['current_vertical'], 'current_zone': p['current_zone'],
                'suggested_vertical': suggested,
                'confidence': ai_item.get('confidence', 'low'),
                'reason': ai_item.get('reason', ''), 'mismatch': is_mismatch,
            })
        else:
            results.append({
                'id': p['id'], 'name': p['name'],
                'current_vertical': p['current_vertical'], 'current_zone': p['current_zone'],
                'suggested_vertical': p['current_vertical'],
                'confidence': 'low', 'reason': 'AI khong phan loai duoc', 'mismatch': False,
            })

    return jsonify({
        'done': offset + batch_size >= total,
        'results': results, 'total': total,
        'processed': min(offset + batch_size, total),
        'next_offset': offset + batch_size
    })


def _call_ai_api(prompt):
    """Unified AI API caller - tries Claude first, then OpenAI. Returns parsed JSON or None.
    Sets _call_ai_api.last_error with debug info if all attempts fail."""
    import requests as req
    _call_ai_api.last_error = ''
    claude_key = SiteSettings.get('claude_key')
    openai_key = SiteSettings.get('openai_key')

    if not claude_key and not openai_key:
        _call_ai_api.last_error = 'Chua co API key nao. Vao Settings > AI API Keys de them.'
        return None

    if claude_key:
        try:
            resp = req.post('https://api.anthropic.com/v1/messages',
                headers={'x-api-key': claude_key, 'anthropic-version': '2023-06-01',
                         'content-type': 'application/json'},
                json={'model': 'claude-sonnet-4-5-20250929', 'max_tokens': 4000,
                      'messages': [{'role': 'user', 'content': prompt}]},
                timeout=60)
            if resp.status_code == 200:
                result = _parse_ai_json_response(resp.json()['content'][0]['text'])
                if result:
                    return result
                _call_ai_api.last_error = 'Claude tra loi nhung khong parse duoc JSON'
            else:
                err_body = resp.text[:300]
                _call_ai_api.last_error = f'Claude API loi {resp.status_code}: {err_body}'
        except Exception as e:
            _call_ai_api.last_error = f'Claude exception: {str(e)}'

    if openai_key:
        try:
            resp = req.post('https://api.openai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {openai_key}', 'Content-Type': 'application/json'},
                json={'model': 'gpt-4o-mini',
                      'messages': [
                          {'role': 'system', 'content': 'You are a product classification expert. Always respond with valid JSON.'},
                          {'role': 'user', 'content': prompt}],
                      'max_tokens': 4000, 'temperature': 0.2},
                timeout=60)
            if resp.status_code == 200:
                result = _parse_ai_json_response(resp.json()['choices'][0]['message']['content'])
                if result:
                    return result
                _call_ai_api.last_error = 'OpenAI tra loi nhung khong parse duoc JSON'
            else:
                err_body = resp.text[:300]
                _call_ai_api.last_error = f'OpenAI API loi {resp.status_code}: {err_body}'
        except Exception as e:
            _call_ai_api.last_error = f'OpenAI exception: {str(e)}'
    return None


def _parse_ai_json_response(text):
    """Parse AI response, extract JSON array"""
    import json, re
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\[[\s\S]*\]', text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


# Keep old apply route as alias
@app.route('/admin/products/ai-classify/apply', methods=['POST'])
def admin_products_ai_classify_apply():
    return admin_ai_center_bulk_action()


def _build_part_keyword_index():
    """Build keyword index from ALL Parts across ALL verticals for auto-mapping.
    Returns list of {part_id, keywords: set(), zone_name, part_name, ...}
    """
    import unicodedata, re
    def normalize(text):
        """Lowercase + strip Vietnamese diacritics for fuzzy matching"""
        text = text.lower().strip()
        nfkd = unicodedata.normalize('NFKD', text)
        return ''.join(c for c in nfkd if not unicodedata.combining(c))

    q = db.session.query(Part, Zone, Segment, Vertical).join(
        Zone, Part.zone_id == Zone.id
    ).join(Segment, Zone.segment_id == Segment.id
    ).join(Vertical, Segment.vertical_id == Vertical.id)

    index = []
    for part, zone, seg, vert in q.all():
        keywords = set()
        keywords.add(normalize(part.name_vi))
        if part.name_en:
            keywords.add(normalize(part.name_en))
        if part.tags:
            for tag in part.tags.split(','):
                tag = tag.strip()
                if len(tag) >= 2:
                    keywords.add(normalize(tag))
        if part.oem_code:
            for code in re.findall(r'[A-Za-z0-9]+-[A-Za-z0-9]+', part.oem_code):
                keywords.add(code.lower())

        index.append({
            'part_id': part.id,
            'keywords': keywords,
            'zone_name': zone.name,
            'zone_slug': zone.slug,
            'part_name': part.name_vi,
            'seg_name': seg.name,
            'vert_name': vert.name,
            'vert_slug': vert.slug,
        })

    # Zone-level keyword map — ALL verticals (fallback when no Part matches)
    # Keywords are normalized (no diacritics, lowercase)
    zone_keywords = {
        # === CAR / OTO ===
        'he-thong-treo': ['phuoc', 'giam chan', 'lo xo', 'cao su', 'rotuy', 'rotuyn', 'thanh can bang',
                          'shock', 'absorber', 'spring', 'bushing', 'ball joint', 'suspension',
                          'giam xoc', 'nhun', 'stabilizer', 'sway bar', 'gat phuoc',
                          'cao su cang a', 'cao su thanh giang', 'thanh giang',
                          'bilstein', 'kayaba', 'kyb', 'monroe', 'sachs',
                          'chup mui', 'op bi', 'bi dien'],
        'he-thong-phanh': ['ma phanh', 'dia phanh', 'bau tro luc', 'caliper',
                           'brake pad', 'brake disc', 'dau phanh', 'tang bua',
                           'bo kep phanh', 'phanh tay', 'phanh dia', 'phanh tang trong',
                           'brembo', 'akebono', 'bendix', 'ferodo', 'bosch brake',
                           'ong dau phanh', 'tro luc phanh', 'bua phanh'],
        'dong-co': ['dong co', 'engine', 'bugi', 'spark plug', 'kim phun', 'turbo', 'block may',
                    'loc gio', 'loc dau', 'loc nhien lieu', 'dau may', 'oil filter', 'air filter',
                    'piston', 'xi lanh', 'truc khuyu', 'crankshaft', 'gasket',
                    'gioang', 'day curoa', 'bom nuoc', 'water pump', 'bom xang',
                    'injector', 'throttle', 'nap may', 'supap', 'cam', 'truc cam',
                    'dau nhot', 'nhot dong co', 'castrol', 'mobil 1', 'shell helix',
                    'total quartz', 'motul', 'liqui moly', 'denso', 'ngk',
                    'turbo tang ap', 'intercooler', 'supercharger',
                    'ron nap may', 'phot dau', 'gioang quy lat'],
        'he-thong-dien': ['ac quy', 'battery oto', 'may phat', 'alternator',
                          'bong den oto', 'day dien oto',
                          'cau chi', 'cam bien', 'sensor', 'ecu', 'relay',
                          'gat mua', 'wiper', 'starter', 'khoi dong',
                          'den pha', 'den hau', 'den xi nhan', 'den led oto',
                          'philips oto', 'osram', 'bosch oto', 'varta',
                          'cam bien oxy', 'cam bien nhiet do', 'cam bien toc do',
                          'hop den', 'day co', 'cuon danh lua'],
        'he-thong-lai': ['thuoc lai', 'tro luc lai', 'vo lang',
                         'power steering', 'rack', 'tie rod', 'tay lai',
                         'cao su ro tuyn', 'rotuy lai', 'bom tro luc lai',
                         'dau tro luc lai', 'tay lai xe'],
        'gam-xe': ['gam xe', 'khung gam', 'chassis', 'chan bun', 'underbody', 'che gam',
                   'lop oto', 'mam oto', 'bac dan', 'bearing', 'moay o',
                   'lop xe oto', 'michelin', 'bridgestone', 'goodyear', 'dunlop',
                   'continental', 'hankook', 'yokohama', 'kumho', 'maxxis',
                   'mam xe oto', 'la zang', 'lazang', 'bu long banh xe',
                   'bi moay o', 'phot moay o'],
        'noi-that': ['noi that oto', 'ghe oto', 'taplo', 'dashboard', 'tham oto',
                     'dieu hoa oto', 'guong chieu hau', 'boc ghe oto', 'boc vo lang',
                     'tham lot san oto', 'tham san oto', 'nem tua lung oto',
                     'camera hanh trinh', 'dashcam', 'dvd oto', 'man hinh oto',
                     'loc dieu hoa', 'loc gio lanh'],
        'ngoai-that': ['ngoai that oto', 'can oto', 'bumper', 'guong oto',
                       'kinh oto', 'windshield', 'capo', 'hood', 'cop xe',
                       'tem xe', 'decal', 'ong xa oto', 'exhaust',
                       'thanh gia noc', 'baga noc', 'can truoc', 'can sau',
                       'op ca lang', 'body kit', 'spoiler', 'cua gio oto',
                       'chay bam', 'phu kinh', 'khung bao ve'],
        # === PET ===
        'dinh-duong': ['thuc an cho', 'thuc an meo', 'dog food', 'cat food', 'hat cho', 'hat meo',
                       'royal canin', 'pedigree', 'whiskas', 'taste of the wild', 'nutrience',
                       'smartheart', 'ganador', 'natural core', 'snack cho', 'snack meo',
                       'pate cho', 'pate meo', 'sua cho', 'sua meo', 'puppy food',
                       'kitten food', 'dinh duong thu cung', 'pet food',
                       'thuc an cho cho', 'thuc an cho meo',
                       'pro plan', 'proplan', 'hills', 'science diet',
                       'acana', 'orijen', 'ziwi peak', 'wellness', 'nutro',
                       'brit care', 'monge', 'reflex', 'minino', 'catsrang',
                       'iskhan', 'jerhigh', 'inaba', 'ciao churu',
                       'treats cho', 'treats meo', 'banh thuong cho', 'banh thuong meo',
                       'thuc an hat', 'thuc an uot', 'thuc an kho'],
        'y-te': ['vaccine cho', 'vaccine meo', 'tay giun', 'thuoc ve', 'thuoc ran',
                 'frontline', 'nexgard', 'heartgard', 'revolution', 'thuoc nho gay',
                 'thuoc tri nam', 'thuoc tri ve', 'y te thu cung',
                 'thuoc cho cho', 'thuoc cho meo',
                 'advantage', 'advocate', 'bravecto', 'simparica', 'seresto',
                 'drontal', 'milbemax', 'panacur', 'vetrimec',
                 'sua tam cho', 'sua tam meo', 'dau goi cho', 'dau goi meo',
                 've sinh tai', 've sinh rang', 'kem danh rang cho',
                 'thuoc sat trung', 'biotic', 'probiotic thu cung',
                 'vitamin thu cung', 'canxi cho', 'canxi meo'],
        'huan-luyen': ['huan luyen cho', 'day cho', 'treat huan luyen',
                       'clicker', 'muzzle', 'day dan cho',
                       'ro mom cho', 'bang khen', 'huan luyen thu cung'],
        'do-dung': ['chuong cho', 'chuong meo', 'long cho', 'long meo', 'bat an', 'binh nuoc',
                    'vong co', 'day dat', 'leash', 'collar', 'ao cho', 'ao meo',
                    'nem cho', 'giuong cho', 'nha meo', 'cat tree', 'cay leo meo',
                    'do choi cho', 'do choi meo', 'balo thu cung', 'tui van chuyen',
                    'xe day thu cung', 'pet carrier', 'khay ve sinh', 'cat ve sinh',
                    'cat toan', 'bentonite', 'tofu cat', 'crystal cat',
                    'pet fountain', 'phu kien thu cung',
                    'harness', 'yem cho', 'dai yem cho',
                    'chuong van chuyen', 'long van chuyen',
                    'balo meo', 'tui meo', 'nha cho', 'o cho', 'o meo',
                    'qua bong cho', 'xuong gam', 'cau cao meo',
                    'mieng lot khay', 'ta cho', 'bim cho',
                    'mang bat', 'may loc nuoc thu cung',
                    'luoc chai long', 'keo cat long', 'may cat long',
                    'ban chai long', 'gang tam', 'may say long'],
        'hamster': ['hamster', 'chuot hamster', 'long hamster', 'thuc an hamster',
                    'banh xe hamster', 'cat lot hamster', 'chuot lang', 'guinea pig',
                    'bo hamster', 'binh nuoc hamster', 'nha hamster'],
        'ca-canh': ['ca canh', 'be ca', 'aquarium', 'loc nuoc be ca', 'thuc an ca',
                    'den be ca', 'co thuy sinh', 'nen be ca', 'ca betta', 'ca vang',
                    'may bom oxy', 'may sui', 'loc be ca', 'may loc be ca',
                    'da trang tri be ca', 'lu be ca', 'kinh be ca'],
        # === BEAUTY ===
        'lam-sach': ['sua rua mat', 'tay trang', 'dau tay trang', 'nuoc tay trang', 'cleansing',
                     'micellar', 'foam rua mat', 'gel rua mat', 'oil cleanser', 'lam sach da',
                     'cerave cleanser', 'la roche posay cleanser', 'cetaphil',
                     'bioderma', 'garnier micellar', 'simple cleanser',
                     'rua mat', 'kem rua mat', 'bot rua mat',
                     'tay te bao chet', 'scrub', 'exfoliate', 'peeling gel'],
        'toner-essence': ['toner', 'nuoc hoa hong', 'essence', 'tinh chat lot', 'lotion',
                          'nuoc can bang', 'first treatment',
                          'klairs toner', 'thayers', 'hada labo', 'laneige',
                          'some by mi toner', 'cosrx toner', 'innisfree toner',
                          'nuoc than', 'nuoc than thanh xuan'],
        'serum': ['serum', 'tinh chat', 'ampoule', 'vitamin c serum', 'retinol', 'niacinamide',
                  'hyaluronic', 'peptide', 'serum duong',
                  'the ordinary', 'cerave serum', 'la roche posay serum',
                  'obagi', 'skinceuticals', 'paula choice', 'drunk elephant',
                  'cosrx serum', 'some by mi serum', 'klairs serum',
                  'serum tri mun', 'serum trang da', 'serum chong lao hoa',
                  'tinh chat duong', 'dac tri'],
        'kem-duong': ['kem duong', 'moisturizer', 'cream', 'kem duong am', 'night cream',
                      'day cream', 'gel duong', 'emulsion', 'kem mat',
                      'cerave cream', 'la roche posay cream', 'laneige cream',
                      'innisfree cream', 'sulwhasoo', 'whoo', 'sk-ii',
                      'kem lot', 'primer', 'kem nen', 'foundation',
                      'kem duong da', 'kem duong mat', 'kem duong the',
                      'body lotion', 'sua duong the', 'kem tay'],
        'chong-nang': ['chong nang', 'sunscreen', 'kem chong nang', 'sun cream',
                       'uv protection', 'sunblock',
                       'anessa', 'skin aqua', 'biore uv', 'la roche posay uv',
                       'eucerin sun', 'neutrogena sun', 'innisfree sun',
                       'chong nang da mat', 'chong nang body', 'xit chong nang',
                       'gel chong nang', 'sua chong nang'],
        'mat-na': ['mat na', 'mask', 'sheet mask', 'sleeping mask', 'clay mask',
                   'mat na giay', 'mat na dat set', 'mat na ngu', 'peel off',
                   'mat na vita', 'mat na collagen', 'mat na hyaluron',
                   'mediheal', 'jayjun', 'dr jart', 'papa recipe',
                   'mat na duong', 'mat na trang da', 'mat na tri mun'],
        'trang-diem': ['son moi', 'lipstick', 'son kem', 'lip tint', 'son duong',
                       'phan ma', 'blush', 'phan mat', 'eyeshadow', 'mascara',
                       'ke mat', 'eyeliner', 'ke may', 'eyebrow', 'phan phu',
                       'cushion', 'bb cream', 'cc cream', 'highlight', 'contour',
                       'mac', 'maybelline', 'loreal', 'nyx', 'revlon',
                       'rom&nd', 'romand', 'peripera', '3ce', 'black rouge',
                       'clio', 'etude', 'missha', 'the saem', 'espoir',
                       'phan nuoc', 'trang diem', 'makeup', 'kem nen'],
        'nuoc-hoa': ['nuoc hoa', 'parfum', 'perfume', 'eau de toilette', 'edt', 'edp',
                     'cologne', 'body mist', 'xit thom',
                     'chanel', 'dior perfume', 'gucci perfume', 'versace',
                     'calvin klein', 'narciso', 'jo malone', 'tom ford'],
        'cham-soc-toc': ['dau goi', 'dau xa', 'shampoo', 'conditioner', 'kem u toc',
                         'dau duong toc', 'hair serum', 'hair mask',
                         'nhuom toc', 'uon toc', 'duoi toc', 'keo noi toc',
                         'pantene', 'dove', 'tresemme', 'loreal hair',
                         'moroccanoil', 'olaplex', 'kerastase',
                         'gel vuot toc', 'sap vuot toc', 'keo xit toc',
                         'may say toc', 'may uon toc', 'may la toc',
                         'luoc', 'luoc go', 'luoc chai'],
        # === TECH ===
        'dien-thoai': ['dien thoai', 'smartphone', 'iphone', 'samsung galaxy', 'xiaomi',
                       'oppo', 'vivo', 'realme', 'poco', 'oneplus', 'google pixel',
                       'huawei', 'nokia', 'asus rog phone', 'nothing phone',
                       'iphone 15', 'iphone 16', 'galaxy s24', 'galaxy s25',
                       'redmi', 'redmi note'],
        'laptop': ['laptop', 'macbook', 'thinkpad', 'dell xps', 'asus zenbook',
                   'hp envy', 'hp pavilion', 'acer swift', 'lenovo ideapad',
                   'surface', 'chromebook', 'gaming laptop',
                   'asus vivobook', 'msi gaming', 'acer nitro', 'legion',
                   'may tinh xach tay', 'ultrabook'],
        'tablet': ['tablet', 'ipad', 'galaxy tab', 'xiaomi pad',
                   'may tinh bang', 'kindle', 'but cam ung', 'apple pencil'],
        'man-hinh': ['man hinh', 'monitor', 'man hinh may tinh', 'man hinh gaming',
                     'cuong luc', 'dan man hinh', 'tempered glass',
                     'man hinh 4k', 'man hinh cong', 'ultrawide'],
        'pin-sac': ['power bank', 'sac nhanh', 'sac khong day',
                    'wireless charging', 'cap sac', 'adapter', 'magsafe', 'pin du phong',
                    'anker', 'baseus', 'ugreen', 'belkin', 'aukey',
                    'cap type c', 'cap lightning', 'cap usb', 'cu sac',
                    'sac iphone', 'sac samsung', 'sac xe hoi'],
        'tai-nghe': ['tai nghe', 'headphone', 'earphone', 'earbuds', 'airpods',
                     'galaxy buds', 'sony wh', 'sony wf', 'jabra', 'jbl',
                     'bose', 'sennheiser', 'beats', 'marshall',
                     'tai nghe bluetooth', 'tai nghe khong day', 'tai nghe gaming',
                     'true wireless', 'chong on', 'noise cancelling'],
        'loa': ['loa bluetooth', 'loa di dong', 'loa thong minh', 'soundbar',
                'jbl speaker', 'harman kardon', 'marshall speaker', 'bose speaker',
                'loa karaoke', 'loa keo', 'loa sub', 'amply'],
        'dong-ho-thong-minh': ['smartwatch', 'dong ho thong minh', 'apple watch',
                               'galaxy watch', 'amazfit', 'huawei watch', 'mi band',
                               'fitbit', 'garmin venu', 'vong deo tay thong minh',
                               'day dong ho', 'day apple watch'],
        'phu-kien-tech': ['op lung', 'case', 'bao da', 'mieng dan',
                          'gia do dien thoai', 'tripod', 'selfie stick',
                          'the nho', 'sd card', 'usb', 'ssd', 'o cung',
                          'hub usb', 'dock', 'chuot', 'ban phim',
                          'webcam', 'microphone', 'ring light',
                          'tui chong soc', 'balo laptop'],
        # === BIKE ===
        'khung-xe': ['khung xe dap', 'frame', 'suon xe dap', 'carbon frame', 'nhom frame',
                     'giant', 'trek', 'specialized', 'cannondale', 'merida',
                     'xe dap dua', 'xe dap dia hinh', 'xe dap the thao',
                     'xe dap gap', 'xe dap touring', 'xe dap fixed gear'],
        'he-thong-truyen-dong': ['truyen dong', 'shimano', 'sram', 'xich xe dap',
                                  'bat dia', 'tay de', 'shifter', 'derailleur', 'groupset',
                                  'cassette', 'pedal', 'ban dap',
                                  'shimano deore', 'shimano 105', 'shimano ultegra',
                                  'shimano dura ace', 'sram eagle', 'sram rival',
                                  'campagnolo', 'truc giua', 'bottom bracket'],
        'banh-xe': ['banh xe dap', 'lop xe dap', 'vanh xe dap', 'nan hoa', 'hub xe dap',
                    'sam xe dap', 'tire bike', 'wheelset', 'tubeless',
                    'continental tire', 'schwalbe', 'vittoria', 'maxxis tire',
                    'mavic', 'dt swiss', 'fulcrum', 'lop 700c', 'lop 26', 'lop 29'],
        'yen-va-tay-lai': ['yen xe dap', 'tay lai xe dap', 'ghi dong', 'stem', 'saddle',
                           'handlebar', 'bar tape', 'grip',
                           'fizik', 'selle italia', 'brooks saddle', 'ergon',
                           'phuoc xe dap', 'fox', 'rockshox'],
        'phu-kien-xe-dap': ['mu bao hiem xe dap', 'helmet bike', 'gang tay dap xe', 'kinh dap xe',
                            'den xe dap', 'binh nuoc xe dap', 'bom xe dap', 'dong ho xe dap',
                            'garmin edge', 'wahoo', 'khoa xe dap',
                            'ao dap xe', 'quan dap xe', 'giay dap xe',
                            'tui xe dap', 'gac xe dap', 'baga xe dap',
                            'chuong xe dap', 'ke xe dap', 'bao tay xe dap'],
        # === SPORT ===
        'giay-chay': ['giay chay', 'running shoes', 'nike running', 'adidas running',
                      'asics', 'hoka', 'new balance running', 'saucony', 'brooks',
                      'giay chay bo', 'giay the thao',
                      'nike pegasus', 'nike vaporfly', 'adidas ultraboost',
                      'asics gel', 'asics nimbus', 'asics kayano',
                      'hoka clifton', 'hoka bondi', 'hoka speedgoat',
                      'on running', 'on cloud', 'mizuno', 'under armour'],
        'do-chay': ['do chay bo', 'quan chay', 'ao chay', 'running wear',
                    'shorts chay', 'tights', 'compression',
                    'ao tank', 'ao singlet', 'quan short chay',
                    'nike dri fit', 'adidas climalite', 'under armour heatgear',
                    'ao giu nhiet', 'ao chong nang chay'],
        'dong-ho-gps': ['dong ho gps', 'garmin forerunner', 'garmin fenix', 'coros',
                        'apple watch ultra', 'suunto', 'polar', 'dong ho the thao',
                        'coros pace', 'coros apex', 'coros vertix',
                        'garmin 255', 'garmin 265', 'garmin 965',
                        'polar vantage', 'polar pacer', 'suunto race'],
        'phu-kien-chay': ['dai deo dien thoai', 'running belt', 'ba lo chay',
                          'vo chay', 'running socks', 'headband', 'arm sleeve',
                          'mu chay', 'kinh chay', 'gang tay chay',
                          'dai deo nguc', 'heart rate monitor', 'hrm',
                          'flip belt', 'nathan', 'salomon vest'],
        'dinh-duong-chay': ['gel nang luong', 'energy gel', 'nuoc uong the thao',
                            'electrolyte', 'bcaa', 'whey protein', 'energy bar',
                            'gu energy', 'maurten', 'spring energy', 'tailwind',
                            'nuoc tang luc', 'binh nuoc chay', 'binh nau'],
        # === TRAVEL ===
        'mien-bac': ['ha noi', 'sa pa', 'ha long', 'ninh binh', 'ha giang', 'cao bang',
                     'moc chau', 'mai chau', 'tam dao', 'cat ba', 'du lich mien bac',
                     'fansipan', 'dong van', 'ban gioc', 'bac son', 'mu cang chai',
                     'yen bai', 'lang son', 'bac kan', 'thai nguyen', 'tuyen quang'],
        'mien-trung': ['da nang', 'hoi an', 'hue', 'nha trang', 'da lat', 'quy nhon',
                       'phu yen', 'quang binh', 'phong nha', 'du lich mien trung',
                       'son tra', 'ba na hills', 'cu lao cham', 'eo gio',
                       'ninh thuan', 'binh thuan', 'ly son', 'kon tum'],
        'mien-nam': ['sai gon', 'ho chi minh', 'vung tau', 'can tho', 'phu quoc',
                     'con dao', 'mekong', 'du lich mien nam',
                     'mui ne', 'long hai', 'ho tram', 'binh chau',
                     'ben tre', 'tien giang', 'an giang', 'chau doc'],
        'dong-nam-a': ['thai lan', 'singapore', 'malaysia', 'bali', 'indonesia',
                       'philippines', 'cambodia', 'myanmar', 'lao',
                       'bangkok', 'phuket', 'boracay', 'siem reap', 'luang prabang'],
        'dong-a': ['nhat ban', 'han quoc', 'dai loan', 'trung quoc', 'hong kong',
                   'tokyo', 'osaka', 'kyoto', 'seoul', 'busan', 'jeju'],
        'budget': ['hostel', 'homestay', 'nha nghi', 'budget hotel', 'backpacker',
                   'airbnb', 'phong tro', 'nha dan', 'camping', 'glamping'],
        'resort': ['resort', 'khach san', 'hotel 5 sao', 'hotel 4 sao', 'villa',
                   'spa resort', 'beach resort',
                   'vinpearl', 'melia', 'pullman', 'intercontinental',
                   'marriott', 'hilton', 'accor', 'hyatt', 'six senses',
                   'amanoi', 'jw marriott'],
        # === FASHION ===
        'ao-nam': ['ao polo', 'ao thun nam', 'ao so mi nam', 'ao khoac nam',
                   'ao vest', 'blazer nam', 'ao hoodie', 'ao len nam',
                   'ao dai tay nam', 'ao ngan tay nam'],
        'ao-nu': ['ao thun nu', 'ao so mi nu', 'ao khoac nu', 'ao dai',
                  'ao croptop', 'ao kiem', 'ao hai day', 'cardigan',
                  'ao len nu', 'ao choang'],
        'quan': ['quan jeans', 'quan tay', 'quan kaki', 'quan short',
                 'quan jogger', 'quan the thao', 'quan dai',
                 'quan au', 'quan ong rong', 'quan ong dung'],
        'vay-dam': ['dam', 'vay', 'dam lien', 'dam xoe', 'dam suong',
                    'chan vay', 'vay midi', 'vay maxi', 'jumpsuit',
                    'dam du tiec', 'dam cong so'],
        'giay-dep': ['giay nam', 'giay nu', 'giay sneaker', 'giay boot',
                     'giay cao got', 'giay the thao', 'dep', 'sandal',
                     'nike', 'adidas', 'converse', 'vans', 'puma',
                     'giay da', 'giay luoi', 'giay tay'],
        'tui-xach': ['tui xach', 'balo', 'vi', 'clutch', 'tui deo cheo',
                     'tui tote', 'tui deo vai', 'vi nam', 'vi nu',
                     'charles keith', 'pedro', 'coach', 'michael kors'],
        'phu-kien-thoi-trang': ['kinh mat', 'dong ho', 'vong tay', 'day chuyen',
                                'nhan', 'bong tai', 'khan', 'that lung',
                                'mu non', 'non ket', 'non luoi trai',
                                'trang suc', 'phu kien toc'],
        # === HOME & KITCHEN ===
        'nha-bep': ['noi', 'chao', 'xoong', 'noi com dien', 'lo vi song',
                    'may xay sinh to', 'may ep', 'binh dun nuoc',
                    'noi chien khong dau', 'air fryer', 'lo nuong',
                    'bep tu', 'bep gas', 'bep dien',
                    'dao', 'thot', 'muong', 'dia', 'chen', 'bat',
                    'tupperware', 'lock lock', 'tefal', 'sunhouse',
                    'supor', 'kangaroo', 'electrolux', 'philips'],
        'noi-that-nha': ['ban', 'ghe', 'tu', 'giuong', 'nem', 'goi',
                         'ga giuong', 'chan ga', 'rem cua', 'tham',
                         'den trang tri', 'tranh treo tuong',
                         'ke sach', 'tu quan ao', 'ban lam viec',
                         'sofa', 'ghe van phong', 'tu giay'],
        've-sinh': ['may hut bui', 'robot hut bui', 'may lau nha',
                    'nuoc lau san', 'nuoc rua chen', 'nuoc giat',
                    'nuoc xa', 'bot giat', 'vim', 'sunlight',
                    'comfort', 'downy', 'ariel', 'omo',
                    'giay ve sinh', 'khan giay', 'tui rac'],
        'dien-gia-dung': ['may giat', 'tu lanh', 'may lanh', 'dieu hoa',
                          'quat', 'may loc khong khi', 'may hut am',
                          'may loc nuoc', 'binh nong lanh',
                          'samsung', 'lg', 'panasonic', 'toshiba',
                          'sharp', 'daikin', 'mitsubishi'],
        # === HEALTH ===
        'thuc-pham-chuc-nang': ['vitamin', 'omega 3', 'dau ca', 'collagen',
                                'canxi', 'sat', 'kem', 'magie',
                                'vitamin c', 'vitamin d', 'vitamin e',
                                'thuc pham chuc nang', 'tpcn', 'bao',
                                'dhc', 'blackmores', 'swisse', 'nature made',
                                'kirkland', 'centrum', 'solgar', 'now foods',
                                'bo sung dinh duong', 'vien uong',
                                'tang can', 'giam can', 'detox'],
        'dung-cu-y-te': ['nhiet ke', 'may do huyet ap', 'may do duong huyet',
                         'may xong', 'may xong khi dung', 'khau trang',
                         'bang ca nhan', 'on dinh huyet ap',
                         'omron', 'microlife', 'beurer', 'yuwell'],
        # === BABY & KIDS ===
        'do-tre-em': ['ta em be', 'bim', 'sua bot', 'binh sua',
                      'xe day tre em', 'ghe an dam', 'noi em be',
                      'do choi tre em', 'lego', 'xe day', 'carseat',
                      'ta dan', 'ta quan', 'bobby', 'huggies',
                      'merries', 'moony', 'pampers', 'mamypoko',
                      'sua nan', 'sua ensure', 'sua abbott', 'similac',
                      'vinamilk', 'nutifood', 'friso', 'meiji'],
    }

    # Power keywords: highly distinctive brands/terms — single hit is enough
    # These map directly to zone slugs and give bonus score
    power_keywords = {
        # PET brands → dinh-duong
        'royal canin': 'dinh-duong', 'pedigree': 'dinh-duong', 'whiskas': 'dinh-duong',
        'taste of the wild': 'dinh-duong', 'acana': 'dinh-duong', 'orijen': 'dinh-duong',
        'smartheart': 'dinh-duong', 'ganador': 'dinh-duong', 'nutrience': 'dinh-duong',
        'pro plan': 'dinh-duong', 'hills science diet': 'dinh-duong', 'catsrang': 'dinh-duong',
        'minino': 'dinh-duong', 'ziwi peak': 'dinh-duong', 'jerhigh': 'dinh-duong',
        'ciao churu': 'dinh-duong', 'inaba': 'dinh-duong',
        # PET health → y-te
        'frontline': 'y-te', 'nexgard': 'y-te', 'heartgard': 'y-te',
        'bravecto': 'y-te', 'simparica': 'y-te', 'seresto': 'y-te',
        'advocate': 'y-te', 'revolution': 'y-te', 'drontal': 'y-te',
        # PET accessories → do-dung
        'bentonite': 'do-dung', 'tofu cat': 'do-dung', 'crystal cat': 'do-dung',
        'cat tree': 'do-dung', 'pet carrier': 'do-dung', 'pet fountain': 'do-dung',
        # BEAUTY brands
        'cerave': 'lam-sach', 'la roche posay': 'lam-sach', 'cetaphil': 'lam-sach',
        'bioderma': 'lam-sach', 'the ordinary': 'serum', 'obagi': 'serum',
        'skinceuticals': 'serum', 'paula choice': 'serum',
        'anessa': 'chong-nang', 'skin aqua': 'chong-nang', 'biore uv': 'chong-nang',
        'mediheal': 'mat-na', 'dr jart': 'mat-na',
        'romand': 'trang-diem', 'peripera': 'trang-diem', '3ce': 'trang-diem',
        'black rouge': 'trang-diem', 'maybelline': 'trang-diem',
        'moroccanoil': 'cham-soc-toc', 'olaplex': 'cham-soc-toc', 'kerastase': 'cham-soc-toc',
        # TECH brands
        'iphone': 'dien-thoai', 'samsung galaxy': 'dien-thoai', 'xiaomi': 'dien-thoai',
        'macbook': 'laptop', 'thinkpad': 'laptop', 'dell xps': 'laptop',
        'airpods': 'tai-nghe', 'galaxy buds': 'tai-nghe', 'sony wh': 'tai-nghe',
        'jbl speaker': 'loa', 'harman kardon': 'loa', 'marshall speaker': 'loa',
        'apple watch': 'dong-ho-thong-minh', 'galaxy watch': 'dong-ho-thong-minh',
        'amazfit': 'dong-ho-thong-minh',
        'anker': 'pin-sac', 'baseus': 'pin-sac', 'ugreen': 'pin-sac',
        # CAR brands
        'bilstein': 'he-thong-treo', 'kayaba': 'he-thong-treo', 'kyb': 'he-thong-treo',
        'brembo': 'he-thong-phanh', 'akebono': 'he-thong-phanh',
        'castrol': 'dong-co', 'mobil 1': 'dong-co', 'shell helix': 'dong-co',
        'liqui moly': 'dong-co', 'motul': 'dong-co',
        'michelin': 'gam-xe', 'bridgestone': 'gam-xe', 'goodyear': 'gam-xe',
        'continental': 'gam-xe', 'hankook': 'gam-xe', 'yokohama': 'gam-xe',
        # BIKE brands
        'shimano': 'he-thong-truyen-dong', 'sram': 'he-thong-truyen-dong',
        'campagnolo': 'he-thong-truyen-dong',
        'giant': 'khung-xe', 'trek': 'khung-xe', 'specialized': 'khung-xe',
        'rockshox': 'yen-va-tay-lai',
        # SPORT brands
        'nike pegasus': 'giay-chay', 'nike vaporfly': 'giay-chay',
        'adidas ultraboost': 'giay-chay', 'hoka clifton': 'giay-chay',
        'hoka bondi': 'giay-chay', 'on running': 'giay-chay',
        'garmin forerunner': 'dong-ho-gps', 'garmin fenix': 'dong-ho-gps',
        'coros pace': 'dong-ho-gps', 'suunto race': 'dong-ho-gps',
        'maurten': 'dinh-duong-chay', 'gu energy': 'dinh-duong-chay',
        # BABY brands
        'huggies': 'do-tre-em', 'pampers': 'do-tre-em', 'merries': 'do-tre-em',
        'moony': 'do-tre-em', 'bobby': 'do-tre-em', 'mamypoko': 'do-tre-em',
        'similac': 'do-tre-em', 'friso': 'do-tre-em',
        # HOME brands
        'tefal': 'nha-bep', 'sunhouse': 'nha-bep', 'lock lock': 'nha-bep',
        'air fryer': 'nha-bep', 'noi chien khong dau': 'nha-bep',
        'robot hut bui': 've-sinh', 'may hut bui': 've-sinh',
        'daikin': 'dien-gia-dung', 'mitsubishi': 'dien-gia-dung',
        # HEALTH brands
        'blackmores': 'thuc-pham-chuc-nang', 'swisse': 'thuc-pham-chuc-nang',
        'nature made': 'thuc-pham-chuc-nang', 'now foods': 'thuc-pham-chuc-nang',
        'centrum': 'thuc-pham-chuc-nang', 'kirkland': 'thuc-pham-chuc-nang',
        'omron': 'dung-cu-y-te', 'microlife': 'dung-cu-y-te',
        # TRAVEL brands
        'vinpearl': 'resort', 'six senses': 'resort', 'jw marriott': 'resort',
    }
    return index, zone_keywords, power_keywords, normalize

def _kw_match(kw, text, words):
    """Match a keyword against text with word-boundary awareness.
    Short keywords (< 5 chars): whole-word match only.
    Long keywords (>= 5 chars): substring match OK (more specific).
    Multi-word keywords: all words must be present.
    Returns score (0 = no match)."""
    if not kw or len(kw) < 2:
        return 0
    kw_words = kw.split()
    if len(kw_words) > 1:
        # Multi-word keyword: all words must be present as whole words
        if all(w in words for w in kw_words if len(w) >= 2):
            return len(kw) + 5
        return 0
    # Single-word keyword
    if len(kw) < 5:
        # Short: whole-word match only (avoid "day" matching "day dien")
        if kw in words:
            return len(kw) + 2
        return 0
    else:
        # Long (>= 5 chars): substring OK, more specific
        if kw in text:
            return len(kw) + 4
        return 0

def _match_product_to_part(product_name, category, part_index, zone_keywords, normalize_fn, power_keywords=None):
    """Match a product to best Part across all verticals.
    Returns (part_id, detected_category) tuple. part_id can be None.
    Uses 4-phase strategy: Power keywords → Part keywords → Zone keywords → CSV category."""
    text = normalize_fn(f"{product_name} {category}")
    words = set(text.split())

    # Phase 0: Power keywords — brand names so distinctive 1 hit is enough
    if power_keywords:
        best_pw_zone = None
        best_pw_score = 0
        for pw, zone_slug in power_keywords.items():
            s = _kw_match(pw, text, words)
            if s > 0 and s > best_pw_score:
                best_pw_score = s
                best_pw_zone = zone_slug
        if best_pw_zone and best_pw_score >= 6:
            first_part = Part.query.join(Zone).filter(Zone.slug == best_pw_zone).first()
            if first_part:
                return first_part.id, best_pw_zone

    best_part_id = None
    best_score = 0
    best_hits = 0
    best_entry = None

    # Phase 1: match against Part keywords
    for entry in part_index:
        score = 0
        hits = 0
        for kw in entry['keywords']:
            s = _kw_match(kw, text, words)
            if s > 0:
                score += s
                hits += 1
        if score > best_score:
            best_score = score
            best_hits = hits
            best_part_id = entry['part_id']
            best_entry = entry

    # Require score >= 10 AND at least 2 keyword hits for confidence
    if best_score >= 10 and best_hits >= 2:
        cat = best_entry['zone_slug'] if best_entry else ''
        return best_part_id, cat

    # Phase 2: fallback to Zone-level keywords
    best_zone_slug = None
    best_zone_score = 0
    best_zone_hits = 0
    for zone_slug, kws in zone_keywords.items():
        score = 0
        hits = 0
        for kw in kws:
            s = _kw_match(kw, text, words)
            if s > 0:
                score += s
                hits += 1
        if score > best_zone_score:
            best_zone_score = score
            best_zone_hits = hits
            best_zone_slug = zone_slug

    # Require score >= 8 AND at least 1 hit (relaxed for zone-level)
    if best_zone_slug and best_zone_score >= 8 and best_zone_hits >= 1:
        first_part = Part.query.join(Zone).filter(Zone.slug == best_zone_slug).first()
        if first_part:
            return first_part.id, best_zone_slug
        return None, best_zone_slug

    # Phase 3: use CSV category directly as fallback (exact zone slug match only)
    if category:
        cat_norm = normalize_fn(category)
        cat_slug = cat_norm.replace(' ', '-')
        for zone_slug in zone_keywords:
            if cat_slug == zone_slug or cat_norm == zone_slug.replace('-', ' '):
                first_part = Part.query.join(Zone).filter(Zone.slug == zone_slug).first()
                if first_part:
                    return first_part.id, zone_slug

    return None, ''


def _clean_csv_value(val):
    """Clean CSV cell value — handle nan/null/None from pandas/Excel exports."""
    if val is None:
        return ''
    s = str(val).strip()
    if s.lower() in ('nan', 'null', 'none', 'n/a', 'na', '#n/a', ''):
        return ''
    return s

def _get_or_create_hub_part(category_name):
    """Auto-create Hub vertical + Zone + Part for unmatched products.
    Products go into Hub first, can be reassigned to proper verticals later.
    Uses category_name from CSV to create/find a Zone."""
    cat = _clean_csv_value(category_name)
    if not cat:
        cat = 'Chua phan loai'
    cat_slug = slugify(cat)
    if not cat_slug:
        cat_slug = 'chua-phan-loai'

    # Find or create the Hub vertical
    hub = Vertical.query.filter_by(slug='hub').first()
    if not hub:
        hub = Vertical(name='Hub', slug='hub', icon='🛒', color='#10b981',
                        description='Kho san pham tong — chua phan loai vao vertical', status='published')
        db.session.add(hub)
        db.session.flush()

    # Find or create default segment
    seg = Segment.query.filter_by(vertical_id=hub.id, slug='san-pham').first()
    if not seg:
        seg = Segment(vertical_id=hub.id, name='San pham', slug='san-pham',
                       icon='📦', description='San pham import tu CSV', order=0)
        db.session.add(seg)
        db.session.flush()

    # Find or create Zone from category
    zone = Zone.query.filter_by(segment_id=seg.id, slug=cat_slug).first()
    if not zone:
        zone = Zone(segment_id=seg.id, name=cat[:100], slug=cat_slug,
                     icon='📁', description=f'Tu dong tao tu CSV category: {cat}', order=0)
        db.session.add(zone)
        db.session.flush()

    # Find or create a generic Part in this Zone
    part = Part.query.filter_by(zone_id=zone.id).first()
    if not part:
        part = Part(zone_id=zone.id, name_vi=cat[:200], slug=cat_slug,
                     description=f'San pham {cat}', status='published')
        db.session.add(part)
        db.session.flush()

    return part.id

@app.route('/admin/products/import-csv', methods=['GET', 'POST'])
def admin_products_import_csv():
    """Import products from CSV — all products go into hub, auto-create categories if needed"""
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('Không có file CSV', 'error')
            return redirect(request.url)

        file = request.files['csv_file']
        if file.filename == '':
            flash('Chưa chọn file', 'error')
            return redirect(request.url)

        if not file.filename.endswith('.csv'):
            flash('File phải có định dạng CSV', 'error')
            return redirect(request.url)

        # Read CSV
        import csv
        import io

        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        # Normalize fieldnames to lowercase for case-insensitive matching
        if csv_reader.fieldnames:
            csv_reader.fieldnames = [f.strip().lower() for f in csv_reader.fieldnames]

        # Get form data
        mapping_mode = request.form.get('mapping_mode', 'auto')  # auto or manual
        part_id = request.form.get('part_id')
        network = request.form.get('network', 'shopee')
        apply_deeplink = 'apply_deeplink' in request.form

        if mapping_mode == 'manual' and not part_id:
            flash('Chưa chọn Part để gắn sản phẩm', 'error')
            return redirect(request.url)

        # Build auto-mapping index
        part_index = None
        zone_kw = None
        normalize_fn = None
        if mapping_mode == 'auto':
            part_index, zone_kw, power_kw, normalize_fn = _build_part_keyword_index()

        # Get network for deeplink
        network_obj = None
        if apply_deeplink:
            network_obj = AffiliateNetwork.query.filter_by(slug=network).first()

        count = 0
        skipped = 0
        auto_created = 0
        mapped_zones = {}  # Track mapping stats: zone_name -> count
        hub_zones = {}  # Track auto-created hub categories
        for row in csv_reader:
            # CSV format: sku, name, url, price, discount, image, desc, category
            # Clean all values (handle nan/null from pandas exports)
            product_name = _clean_csv_value(row.get('name', ''))[:200]
            url = _clean_csv_value(row.get('url', ''))
            category = _clean_csv_value(row.get('category', ''))

            if not product_name and not url:
                skipped += 1
                continue

            # Apply deeplink if enabled and template exists
            if apply_deeplink and network_obj and network_obj.deeplink_template and url:
                import urllib.parse
                url = network_obj.deeplink_template.replace('{url}', urllib.parse.quote(url))

            price_val = 0
            price_raw = _clean_csv_value(row.get('price', ''))
            try:
                price_val = float(price_raw) if price_raw else 0
            except (ValueError, TypeError):
                pass
            image_url = _clean_csv_value(row.get('image', ''))

            if mapping_mode == 'auto':
                # Step 1: ALWAYS create in Hub (from CSV category)
                hub_part_id = _get_or_create_hub_part(category)
                cat_label = category or 'Chua phan loai'
                hub_zones[cat_label] = hub_zones.get(cat_label, 0) + 1

                try:
                    al_hub = AffiliateLink(
                        part_id=hub_part_id,
                        network=network,
                        product_name=product_name,
                        url=url,
                        price=price_val,
                        image_url=image_url,
                        is_active=True,
                        category=slugify(category) if category else 'chua-phan-loai',
                    )
                    db.session.add(al_hub)
                    count += 1
                except (ValueError, TypeError):
                    skipped += 1
                    continue

                # Step 2: ALSO match to vertical (if keywords match)
                if part_index:
                    matched_part_id, detected_category = _match_product_to_part(
                        product_name, category, part_index, zone_kw, normalize_fn, power_kw)
                    if matched_part_id:
                        al_vert = AffiliateLink(
                            part_id=matched_part_id,
                            network=network,
                            product_name=product_name,
                            url=url,
                            price=price_val,
                            image_url=image_url,
                            is_active=True,
                            category=detected_category,
                        )
                        db.session.add(al_vert)
                        auto_created += 1
                        # Track vertical mapping stats
                        for entry in (part_index or []):
                            if entry['part_id'] == matched_part_id:
                                zone_label = f"{entry['vert_name']} › {entry['zone_name']} › {entry['part_name']}"
                                mapped_zones[zone_label] = mapped_zones.get(zone_label, 0) + 1
                                break
            else:
                # Manual mode: single Part assignment
                try:
                    al = AffiliateLink(
                        part_id=int(part_id),
                        network=network,
                        product_name=product_name,
                        url=url,
                        price=price_val,
                        image_url=image_url,
                        is_active=True,
                        category=category[:100],
                    )
                    db.session.add(al)
                    count += 1
                except (ValueError, TypeError):
                    skipped += 1

            # Batch commit every 200 rows to reduce lock duration
            if (count + skipped) % 200 == 0:
                db.session.commit()

        db.session.commit()

        # Build result message
        msg = f'Import {count} sản phẩm vào Hub thành công!'
        if auto_created:
            msg += f' + {auto_created} cũng match vào vertical'
        if skipped:
            msg += f' ({skipped} bỏ qua - thiếu tên/url)'
        if hub_zones:
            top_hub = sorted(hub_zones.items(), key=lambda x: -x[1])[:5]
            detail = ', '.join(f'{name}: {cnt}' for name, cnt in top_hub)
            msg += f' | Hub categories: {detail}'
        if mapped_zones:
            top_vert = sorted(mapped_zones.items(), key=lambda x: -x[1])[:5]
            detail = ', '.join(f'{name}: {cnt}' for name, cnt in top_vert)
            msg += f' | Vertical match: {detail}'
        flash(msg, 'success')
        return redirect(url_for('admin_products'))

    # GET request - show form
    parts_tree = []
    for v in Vertical.query.all():
        for s in v.segments:
            for z in s.zones:
                for p in z.parts:
                    parts_tree.append({
                        'id': p.id,
                        'label': f'{v.icon} {v.name} › {s.name} › {z.name} › {p.name_vi}'
                    })

    networks = AffiliateNetwork.query.all()
    return render_template('admin/products_import_csv.html',
        parts_tree=parts_tree, networks=networks)

@app.route('/admin/products/datafeeds', methods=['GET', 'POST'])
def admin_products_datafeeds():
    """Browse & import products from AccessTrade Datafeeds API"""
    from accesstrade_integration import get_accesstrade_api

    api = get_accesstrade_api()
    if not api:
        flash('Chua cau hinh AccessTrade API key. Vao Affiliate Network de thiet lap.', 'error')
        return redirect(url_for('admin_products'))

    # ── POST: Import selected products ──
    if request.method == 'POST':
        selected = request.form.getlist('selected_products')
        if not selected:
            flash('Chua chon san pham nao de import', 'warning')
            return redirect(request.url)

        import json as _json
        network = 'accesstrade'
        apply_deeplink = 'apply_deeplink' in request.form
        network_obj = AffiliateNetwork.query.filter_by(slug='accesstrade').first()

        # Build auto-mapping index
        part_index, zone_kw, power_kw, normalize_fn = _build_part_keyword_index()

        count = 0
        matched = 0
        for item_json in selected:
            try:
                item = _json.loads(item_json)
            except (ValueError, TypeError):
                continue

            product_name = (item.get('name') or '')[:200]
            url = item.get('url') or item.get('deep_link') or ''
            image_url = item.get('image') or ''
            category = item.get('category') or ''

            if not product_name and not url:
                continue

            # Use deep_link (affiliate link) if available, else apply deeplink template
            aff_url = item.get('deep_link') or url
            if apply_deeplink and network_obj and network_obj.deeplink_template and url and not item.get('deep_link'):
                import urllib.parse
                aff_url = network_obj.deeplink_template.replace('{url}', urllib.parse.quote(url))

            price_val = 0
            try:
                price_val = float(item.get('price') or item.get('promotion_price') or 0)
            except (ValueError, TypeError):
                pass

            # Always create in Hub
            hub_part_id = _get_or_create_hub_part(category)
            al_hub = AffiliateLink(
                part_id=hub_part_id,
                network=network,
                product_name=product_name,
                url=aff_url,
                price=price_val,
                image_url=image_url,
                is_active=True,
                category=slugify(category) if category else 'chua-phan-loai',
            )
            db.session.add(al_hub)
            count += 1

            # Also match to vertical
            if part_index:
                matched_part_id, detected_cat = _match_product_to_part(
                    product_name, category, part_index, zone_kw, normalize_fn, power_kw)
                if matched_part_id:
                    al_vert = AffiliateLink(
                        part_id=matched_part_id,
                        network=network,
                        product_name=product_name,
                        url=aff_url,
                        price=price_val,
                        image_url=image_url,
                        is_active=True,
                        category=detected_cat,
                    )
                    db.session.add(al_vert)
                    matched += 1

        db.session.commit()
        msg = f'Import {count} san pham tu Datafeeds thanh cong!'
        if matched:
            msg += f' + {matched} match vao vertical'
        flash(msg, 'success')
        return redirect(url_for('admin_products'))

    # ── GET: Browse datafeeds ──
    keyword = request.args.get('keyword', '')
    domain = request.args.get('domain', '')
    campaign = request.args.get('campaign', '')
    page = request.args.get('page', 1, type=int)
    limit = 50

    products = []
    total = 0

    # Only call API if there's a search query
    if keyword or domain or campaign:
        result = api.get_datafeeds(
            keyword=keyword or None,
            domain=domain or None,
            campaign=campaign or None,
            page=page,
            limit=limit,
        )
        products = result.get('data', [])
        total = result.get('total', 0)

    # Get campaigns for dropdown filter
    campaigns = api.get_campaigns(limit=100, status=1)

    total_pages = (total + limit - 1) // limit if total > 0 else 0

    return render_template('admin/products_datafeeds.html',
        products=products, total=total, campaigns=campaigns,
        keyword=keyword, domain=domain, campaign=campaign,
        page=page, total_pages=total_pages)


@app.route('/admin/api/create-tracking-link', methods=['POST'])
def admin_api_create_tracking_link():
    """API endpoint: convert product URLs to affiliate tracking links."""
    from accesstrade_integration import get_accesstrade_api
    api = get_accesstrade_api()
    if not api:
        return jsonify({'success': False, 'error': 'AccessTrade API not configured'}), 400

    data = request.get_json() or {}
    campaign_id = data.get('campaign_id', '')
    urls = data.get('urls', [])
    if not campaign_id:
        return jsonify({'success': False, 'error': 'campaign_id is required'}), 400
    if not urls:
        return jsonify({'success': False, 'error': 'urls list is required'}), 400

    result = api.create_tracking_link(
        campaign_id=campaign_id,
        urls=urls,
        utm_source=data.get('utm_source'),
        utm_campaign=data.get('utm_campaign'),
    )
    return jsonify(result)


@app.route('/admin/api/order-list')
def admin_api_order_list():
    """API endpoint: get AccessTrade order list v2."""
    from accesstrade_integration import get_accesstrade_api
    api = get_accesstrade_api()
    if not api:
        return jsonify({'data': [], 'total': 0, 'error': 'AccessTrade API not configured'}), 400

    since = request.args.get('since', '')
    until = request.args.get('until', '')
    if not since or not until:
        return jsonify({'data': [], 'total': 0, 'error': 'since and until are required'}), 400

    result = api.get_order_list(
        since=since,
        until=until,
        page=request.args.get('page', 1, type=int),
        limit=request.args.get('limit', 30, type=int),
        status=request.args.get('status', None, type=int),
        merchant=request.args.get('merchant', None),
    )
    return jsonify(result)


@app.route('/admin/api/tiktok-search')
def admin_api_tiktok_search():
    """API endpoint: search TikTok Shop products."""
    from accesstrade_integration import get_accesstrade_api
    api = get_accesstrade_api()
    if not api:
        return jsonify({'products': [], 'total_count': 0, 'error': 'API not configured'}), 400

    keywords = request.args.get('q', '')
    if not keywords:
        return jsonify({'products': [], 'total_count': 0, 'error': 'q is required'}), 400

    result = api.tiktok_search_products(
        title_keywords=keywords,
        sort_field=request.args.get('sort', 'RECOMMENDED'),
        limit=request.args.get('limit', 20, type=int),
        page_token=request.args.get('page_token', None),
    )
    return jsonify(result)


@app.route('/admin/api/tiktok-create-link', methods=['POST'])
def admin_api_tiktok_create_link():
    """API endpoint: create TikTok Shop affiliate link."""
    from accesstrade_integration import get_accesstrade_api
    api = get_accesstrade_api()
    if not api:
        return jsonify({'status': False, 'error': 'API not configured'}), 400

    data = request.get_json() or {}
    product_url = data.get('product_url', '')
    if not product_url:
        return jsonify({'status': False, 'error': 'product_url is required'}), 400

    result = api.tiktok_create_link(
        product_url=product_url,
        product_id=data.get('product_id'),
        utm_source=data.get('utm_source'),
    )
    return jsonify(result)


@app.route('/admin/products/reclassify-hub', methods=['POST'])
def admin_products_reclassify_hub():
    """Re-run matching on Hub products → move matched ones to verticals.
    Called after creating new verticals/parts to classify existing Hub products."""
    hub = Vertical.query.filter_by(slug='hub').first()
    if not hub:
        flash('Chưa có vertical Hub nào.', 'warning')
        return redirect(url_for('admin_products'))

    # Get all Hub segment/zone/part IDs
    hub_part_ids = set()
    for seg in hub.segments:
        for zone in seg.zones:
            for part in zone.parts:
                hub_part_ids.add(part.id)

    if not hub_part_ids:
        flash('Hub không có sản phẩm nào.', 'warning')
        return redirect(url_for('admin_products'))

    # Get all products in Hub
    hub_products = AffiliateLink.query.filter(AffiliateLink.part_id.in_(hub_part_ids)).all()
    if not hub_products:
        flash('Hub không có sản phẩm nào cần phân loại.', 'info')
        return redirect(url_for('admin_products'))

    # Build matching index (excluding Hub parts)
    part_index, zone_kw, power_kw, normalize_fn = _build_part_keyword_index()
    # Filter out Hub parts from index
    part_index = [e for e in part_index if e['vert_slug'] != 'hub']

    if not part_index and not zone_kw:
        flash('Chưa có vertical/zone nào để match. Hãy tạo vertical trước.', 'warning')
        return redirect(url_for('admin_products'))

    matched = 0
    mapped_zones = {}
    for al in hub_products:
        matched_part_id, detected_category = _match_product_to_part(
            al.product_name, al.category or '', part_index, zone_kw, normalize_fn, power_kw)
        if matched_part_id:
            # Create a copy in the matched vertical (keep original in Hub)
            existing = AffiliateLink.query.filter_by(
                part_id=matched_part_id, url=al.url).first()
            if not existing:
                al_vert = AffiliateLink(
                    part_id=matched_part_id,
                    network=al.network,
                    product_name=al.product_name,
                    url=al.url,
                    price=al.price,
                    image_url=al.image_url,
                    is_active=True,
                    category=detected_category,
                )
                db.session.add(al_vert)
                matched += 1
                # Track stats
                for entry in part_index:
                    if entry['part_id'] == matched_part_id:
                        label = f"{entry['vert_name']} › {entry['zone_name']} › {entry['part_name']}"
                        mapped_zones[label] = mapped_zones.get(label, 0) + 1
                        break

    db.session.commit()

    msg = f'Re-classify: {matched}/{len(hub_products)} sản phẩm Hub được match vào vertical.'
    if mapped_zones:
        top = sorted(mapped_zones.items(), key=lambda x: -x[1])[:8]
        detail = ', '.join(f'{name}: {cnt}' for name, cnt in top)
        msg += f' | {detail}'
    flash(msg, 'success' if matched > 0 else 'info')
    return redirect(url_for('admin_products'))

@app.route('/admin/scheduled-imports')
def admin_scheduled_imports():
    """List all scheduled CSV imports"""
    jobs = ScheduledCSVImport.query.order_by(ScheduledCSVImport.created_at.desc()).all()
    return render_template('admin/scheduled_imports.html', jobs=jobs)

@app.route('/admin/scheduled-import/create', methods=['POST'])
def admin_scheduled_import_create():
    """Create a new scheduled CSV import job"""
    from datetime import timedelta

    job = ScheduledCSVImport(
        name=request.form['name'],
        csv_url=request.form['csv_url'],
        part_id=int(request.form['part_id']),
        network=request.form.get('network', 'shopee'),
        apply_deeplink='apply_deeplink' in request.form,
        update_interval_days=int(request.form.get('update_interval_days', 7)),
        is_active=True
    )

    # Set next import time
    job.next_import_at = datetime.utcnow() + timedelta(days=job.update_interval_days)

    db.session.add(job)
    db.session.commit()

    # Run import now if requested
    if 'run_now' in request.form:
        return redirect(url_for('admin_scheduled_import_run', job_id=job.id))

    flash(f'Đã tạo scheduled import: {job.name}', 'success')
    return redirect(url_for('admin_scheduled_imports'))

@app.route('/admin/scheduled-import/<int:job_id>/run')
def admin_scheduled_import_run(job_id):
    """Manually trigger a scheduled import"""
    from datetime import timedelta
    import urllib.request
    import csv
    import io

    job = ScheduledCSVImport.query.get_or_404(job_id)

    try:
        # Fetch CSV from URL
        req = urllib.request.Request(job.csv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            csv_content = response.read().decode('utf-8')

        # Parse CSV
        stream = io.StringIO(csv_content)
        csv_reader = csv.DictReader(stream)

        # Get network for deeplink
        network_obj = None
        if job.apply_deeplink:
            network_obj = AffiliateNetwork.query.filter_by(slug=job.network).first()

        # Delete old products for this part from this network (optional - for refresh)
        # AffiliateLink.query.filter_by(part_id=job.part_id, network=job.network).delete()

        count = 0
        for row in csv_reader:
            url = row.get('url', '')

            # Apply deeplink if enabled and template exists
            if job.apply_deeplink and network_obj and network_obj.deeplink_template and url:
                import urllib.parse
                url = network_obj.deeplink_template.replace('{url}', urllib.parse.quote(url))

            # Check if product already exists (by URL)
            existing = AffiliateLink.query.filter_by(part_id=job.part_id, url=url).first()
            if existing:
                # Update existing product
                existing.product_name = row.get('name', '')[:200]
                existing.price = float(row.get('price', 0))
                existing.image_url = row.get('image', '')
            else:
                # Create new product
                al = AffiliateLink(
                    part_id=job.part_id,
                    network=job.network,
                    product_name=row.get('name', '')[:200],
                    url=url,
                    price=float(row.get('price', 0)),
                    image_url=row.get('image', ''),
                    is_active=True
                )
                db.session.add(al)
            count += 1

        # Update job status
        job.last_import_at = datetime.utcnow()
        job.last_import_count = count
        job.last_import_status = 'success'
        job.last_error = ''
        job.next_import_at = datetime.utcnow() + timedelta(days=job.update_interval_days)

        db.session.commit()
        flash(f'✓ Import thành công {count} sản phẩm từ {job.name}', 'success')

    except Exception as e:
        job.last_import_status = 'error'
        job.last_error = str(e)
        db.session.commit()
        flash(f'Lỗi khi import: {str(e)}', 'error')

    return redirect(url_for('admin_scheduled_imports'))

@app.route('/admin/scheduled-import/<int:job_id>/toggle', methods=['POST'])
def admin_scheduled_import_toggle(job_id):
    """Toggle scheduled import active status"""
    job = ScheduledCSVImport.query.get_or_404(job_id)
    job.is_active = not job.is_active
    db.session.commit()
    flash(f'Đã {"kích hoạt" if job.is_active else "tắt"} scheduled import: {job.name}', 'success')
    return redirect(url_for('admin_scheduled_imports'))

@app.route('/admin/scheduled-import/<int:job_id>/delete', methods=['POST'])
def admin_scheduled_import_delete(job_id):
    """Delete a scheduled import job"""
    job = ScheduledCSVImport.query.get_or_404(job_id)
    name = job.name
    db.session.delete(job)
    db.session.commit()
    flash(f'Đã xóa scheduled import: {name}', 'success')
    return redirect(url_for('admin_scheduled_imports'))

# =============================================
# ADMIN — VIDEO PRODUCTION
# =============================================
@app.route('/admin/video')
def admin_video():
    videos = VideoProject.query.order_by(VideoProject.created_at.desc()).all()
    channels = SocialChannel.query.all()
    total_views = db.session.query(db.func.sum(VideoPublish.views)).scalar() or 0
    total_published = VideoPublish.query.filter_by(status='published').count()
    return render_template('admin/video.html', videos=videos, channels=channels,
        total_views=total_views, total_published=total_published)

@app.route('/admin/video/channels')
def admin_video_channels():
    channels = SocialChannel.query.all()
    verticals = Vertical.query.all()
    return render_template('admin/video_channels.html', channels=channels, verticals=verticals)

@app.route('/admin/video/channel/add', methods=['POST'])
def admin_video_channel_add():
    ch = SocialChannel(
        vertical_id=int(request.form['vertical_id']),
        platform=request.form['platform'],
        channel_name=request.form['channel_name'],
        channel_url=request.form.get('channel_url',''),
        api_key=request.form.get('api_key',''),
        status='connected' if request.form.get('api_key') else 'disconnected'
    )
    db.session.add(ch)
    db.session.commit()
    flash(f'Da them channel: {ch.channel_name}', 'success')
    return redirect(url_for('admin_video_channels'))

@app.route('/admin/video/channel/<int:cid>/delete', methods=['POST'])
def admin_video_channel_delete(cid):
    ch = SocialChannel.query.get_or_404(cid)
    db.session.delete(ch)
    db.session.commit()
    flash('Da xoa channel', 'success')
    return redirect(url_for('admin_video_channels'))

@app.route('/admin/video/channel/<int:cid>/connect', methods=['POST'])
def admin_video_channel_connect(cid):
    ch = SocialChannel.query.get_or_404(cid)
    ch.api_key = request.form.get('api_key','')
    ch.status = 'connected' if ch.api_key else 'disconnected'
    db.session.commit()
    flash(f'{ch.channel_name} -> {ch.status}', 'success')
    return redirect(url_for('admin_video_channels'))

@app.route('/admin/video/create', methods=['GET','POST'])
def admin_video_create():
    verticals = Vertical.query.all()
    parts = Part.query.order_by(Part.name_vi).all()
    if request.method == 'POST':
        vp = VideoProject(
            title=request.form['title'],
            vertical_slug=request.form.get('vertical_slug',''),
            part_id=int(request.form['part_id']) if request.form.get('part_id') else None,
            video_type=request.form.get('video_type','short'),
            duration=request.form.get('duration','60s'),
            script=request.form.get('script',''),
            voiceover_text=request.form.get('voiceover_text',''),
            ai_provider=request.form.get('ai_provider','openai'),
            caption=request.form.get('caption',''),
            hashtags=request.form.get('hashtags',''),
            status='draft'
        )
        db.session.add(vp)
        db.session.commit()
        flash(f'Da tao video project: {vp.title}', 'success')
        return redirect(url_for('admin_video_detail', vid=vp.id))
    return render_template('admin/video_create.html', verticals=verticals, parts=parts)

@app.route('/admin/video/<int:vid>')
def admin_video_detail(vid):
    v = VideoProject.query.get_or_404(vid)
    channels = SocialChannel.query.filter_by(status='connected').all()
    if v.vertical_slug:
        channels = [c for c in channels if c.vertical and c.vertical.slug == v.vertical_slug] or channels
    return render_template('admin/video_detail.html', video=v, channels=channels)

@app.route('/admin/video/<int:vid>/delete', methods=['POST'])
def admin_video_delete(vid):
    v = VideoProject.query.get_or_404(vid)
    db.session.delete(v)
    db.session.commit()
    flash('Da xoa video', 'success')
    return redirect(url_for('admin_video'))

@app.route('/admin/video/<int:vid>/publish', methods=['POST'])
def admin_video_publish(vid):
    v = VideoProject.query.get_or_404(vid)
    channel_ids = request.form.getlist('channel_ids')
    for cid in channel_ids:
        ch = SocialChannel.query.get(int(cid))
        if ch:
            vp = VideoPublish(
                video_id=v.id, channel_id=ch.id, platform=ch.platform,
                status='queued',
                views=random.randint(100,5000), likes=random.randint(10,500),
                shares=random.randint(5,100), comments=random.randint(2,50),
                click_throughs=random.randint(5,200)
            )
            db.session.add(vp)
    v.status = 'published'
    db.session.commit()
    flash(f'Da publish len {len(channel_ids)} channels', 'success')
    return redirect(url_for('admin_video_detail', vid=v.id))

@app.route('/admin/video/analytics')
def admin_video_analytics():
    publishes = VideoPublish.query.order_by(VideoPublish.id.desc()).all()
    channels = SocialChannel.query.all()
    total_views = db.session.query(db.func.sum(VideoPublish.views)).scalar() or 0
    total_clicks = db.session.query(db.func.sum(VideoPublish.click_throughs)).scalar() or 0
    return render_template('admin/video_analytics.html',
        publishes=publishes, channels=channels, total_views=total_views, total_clicks=total_clicks)

# =============================================
# ADMIN — HOTELS (Quản lý khách sạn)
# =============================================
@app.route('/admin/hotels')
def admin_hotels():
    f_dest = request.args.get('destination', '')
    f_stars = request.args.get('stars', '')
    f_status = request.args.get('status', '')
    q = Hotel.query
    if f_dest:
        q = q.filter(Hotel.destination == f_dest)
    if f_stars:
        q = q.filter(Hotel.stars == int(f_stars))
    if f_status == 'active':
        q = q.filter(Hotel.is_active == True)
    elif f_status == 'inactive':
        q = q.filter(Hotel.is_active == False)
    hotels = q.order_by(Hotel.is_featured.desc(), Hotel.rating.desc()).all()
    destinations = db.session.query(Hotel.destination, Hotel.destination_name).distinct().all()
    total = Hotel.query.count()
    active = Hotel.query.filter_by(is_active=True).count()
    total_clicks = db.session.query(db.func.sum(Hotel.clicks)).scalar() or 0
    total_conv = db.session.query(db.func.sum(Hotel.conversions)).scalar() or 0
    return render_template('admin/hotels.html', hotels=hotels, destinations=destinations,
        f_dest=f_dest, f_stars=f_stars, f_status=f_status,
        total=total, active=active, total_clicks=total_clicks, total_conv=total_conv)

@app.route('/admin/hotel/new', methods=['GET','POST'])
def admin_hotel_new():
    if request.method == 'POST':
        h = Hotel(
            name=request.form['name'],
            slug=slugify(request.form['name'])[:60],
            destination=request.form['destination'],
            destination_name=request.form.get('destination_name',''),
            stars=int(request.form.get('stars',4)),
            district=request.form.get('district',''),
            description=request.form.get('description',''),
            amenities=request.form.get('amenities',''),
            rating=float(request.form.get('rating',8.0)),
            reviews_count=int(request.form.get('reviews_count',0)),
            price_from=float(request.form.get('price_from',0)),
            image_url=request.form.get('image_url',''),
            agoda_url=request.form.get('agoda_url',''),
            booking_url=request.form.get('booking_url',''),
            traveloka_url=request.form.get('traveloka_url',''),
            is_active='is_active' in request.form,
            is_featured='is_featured' in request.form
        )
        db.session.add(h); db.session.commit()
        flash(f'Da them: {h.name}', 'success')
        return redirect(url_for('admin_hotels'))
    return render_template('admin/hotel_form.html', hotel=None)

@app.route('/admin/hotel/<int:hid>/edit', methods=['GET','POST'])
def admin_hotel_edit(hid):
    h = Hotel.query.get_or_404(hid)
    if request.method == 'POST':
        h.name = request.form['name']
        h.destination = request.form['destination']
        h.destination_name = request.form.get('destination_name','')
        h.stars = int(request.form.get('stars',4))
        h.district = request.form.get('district','')
        h.description = request.form.get('description','')
        h.amenities = request.form.get('amenities','')
        h.rating = float(request.form.get('rating',8.0))
        h.reviews_count = int(request.form.get('reviews_count',0))
        h.price_from = float(request.form.get('price_from',0))
        h.image_url = request.form.get('image_url','')
        h.agoda_url = request.form.get('agoda_url','')
        h.booking_url = request.form.get('booking_url','')
        h.traveloka_url = request.form.get('traveloka_url','')
        h.is_active = 'is_active' in request.form
        h.is_featured = 'is_featured' in request.form
        db.session.commit()
        flash(f'Da cap nhat: {h.name}', 'success')
        return redirect(url_for('admin_hotels'))
    return render_template('admin/hotel_form.html', hotel=h)

@app.route('/admin/hotel/<int:hid>/toggle', methods=['POST'])
def admin_hotel_toggle(hid):
    h = Hotel.query.get_or_404(hid)
    h.is_active = not h.is_active; db.session.commit()
    return redirect(url_for('admin_hotels'))

@app.route('/admin/hotel/<int:hid>/delete', methods=['POST'])
def admin_hotel_delete(hid):
    h = Hotel.query.get_or_404(hid)
    db.session.delete(h); db.session.commit()
    flash('Da xoa khach san', 'success')
    return redirect(url_for('admin_hotels'))

# =============================================
# ADMIN — ATTRACTIONS (Vé tham quan)
# =============================================
ATTRACTION_CATS = [
    ('zoo','🦁 Sở thú'),('aquarium','🐠 Thủy cung'),('cable_car','🚡 Cáp treo'),
    ('theme_park','🎢 Công viên'),('museum','🏛️ Bảo tàng'),('tour','🚌 Tour'),
    ('show','🎭 Show diễn'),('waterpark','🌊 Công viên nước')
]
ATTRACTION_CAT_MAP = dict(ATTRACTION_CATS)

@app.route('/admin/attractions')
def admin_attractions():
    f_dest = request.args.get('destination', '')
    f_cat = request.args.get('category', '')
    f_net = request.args.get('network', '')
    q = Attraction.query
    if f_dest:
        q = q.filter(Attraction.destination == f_dest)
    if f_cat:
        q = q.filter(Attraction.category == f_cat)
    if f_net:
        q = q.filter(Attraction.network == f_net)
    items = q.order_by(Attraction.is_featured.desc(), Attraction.clicks.desc()).all()
    destinations = db.session.query(Attraction.destination, Attraction.destination_name).distinct().all()
    total = Attraction.query.count()
    active = Attraction.query.filter_by(is_active=True).count()
    total_clicks = db.session.query(db.func.sum(Attraction.clicks)).scalar() or 0
    total_conv = db.session.query(db.func.sum(Attraction.conversions)).scalar() or 0
    return render_template('admin/attractions.html', items=items, destinations=destinations,
        cats=ATTRACTION_CATS, cat_map=ATTRACTION_CAT_MAP,
        f_dest=f_dest, f_cat=f_cat, f_net=f_net,
        total=total, active=active, total_clicks=total_clicks, total_conv=total_conv)

@app.route('/admin/attraction/new', methods=['GET','POST'])
def admin_attraction_new():
    if request.method == 'POST':
        a = Attraction(
            name=request.form['name'],
            slug=slugify(request.form['name'])[:60],
            destination=request.form['destination'],
            destination_name=request.form.get('destination_name',''),
            category=request.form.get('category','tour'),
            description=request.form.get('description',''),
            address=request.form.get('address',''),
            price_from=float(request.form.get('price_from',0)),
            price_original=float(request.form.get('price_original',0)),
            discount_pct=int(request.form.get('discount_pct',0)),
            image_url=request.form.get('image_url',''),
            network=request.form.get('network','klook'),
            affiliate_url=request.form.get('affiliate_url',''),
            is_active='is_active' in request.form,
            is_featured='is_featured' in request.form
        )
        db.session.add(a); db.session.commit()
        flash(f'Da them: {a.name}', 'success')
        return redirect(url_for('admin_attractions'))
    return render_template('admin/attraction_form.html', attraction=None, cats=ATTRACTION_CATS)

@app.route('/admin/attraction/<int:aid>/edit', methods=['GET','POST'])
def admin_attraction_edit(aid):
    a = Attraction.query.get_or_404(aid)
    if request.method == 'POST':
        a.name = request.form['name']
        a.destination = request.form['destination']
        a.destination_name = request.form.get('destination_name','')
        a.category = request.form.get('category','tour')
        a.description = request.form.get('description','')
        a.address = request.form.get('address','')
        a.price_from = float(request.form.get('price_from',0))
        a.price_original = float(request.form.get('price_original',0))
        a.discount_pct = int(request.form.get('discount_pct',0))
        a.image_url = request.form.get('image_url','')
        a.network = request.form.get('network','klook')
        a.affiliate_url = request.form.get('affiliate_url','')
        a.is_active = 'is_active' in request.form
        a.is_featured = 'is_featured' in request.form
        db.session.commit()
        flash(f'Da cap nhat: {a.name}', 'success')
        return redirect(url_for('admin_attractions'))
    return render_template('admin/attraction_form.html', attraction=a, cats=ATTRACTION_CATS)

@app.route('/admin/attraction/<int:aid>/toggle', methods=['POST'])
def admin_attraction_toggle(aid):
    a = Attraction.query.get_or_404(aid)
    a.is_active = not a.is_active; db.session.commit()
    return redirect(url_for('admin_attractions'))

@app.route('/admin/attraction/<int:aid>/delete', methods=['POST'])
def admin_attraction_delete(aid):
    a = Attraction.query.get_or_404(aid)
    db.session.delete(a); db.session.commit()
    flash('Da xoa ve tham quan', 'success')
    return redirect(url_for('admin_attractions'))

# =============================================
# ADMIN — VOUCHERS (Mã giảm giá)
# =============================================
VOUCHER_CATS = [
    ('food','🍔 Ăn uống'),('shopping','🛍️ Mua sắm'),('travel','✈️ Du lịch'),
    ('services','🔧 Dịch vụ'),('entertainment','🎬 Giải trí'),('tech','💻 Công nghệ'),
    ('health','💊 Sức khỏe'),('education','📚 Giáo dục')
]
VOUCHER_CAT_MAP = dict(VOUCHER_CATS)

VOUCHER_TYPES = [
    ('percentage','% Phần trăm'),('fixed_amount','₫ Số tiền'),('free_shipping','🚚 Freeship')
]
VOUCHER_TYPE_MAP = dict(VOUCHER_TYPES)

def _voucher_valid_filter(q):
    """Apply SQL-level is_valid() filter: active, within date range, usage not exceeded"""
    now = datetime.utcnow()
    q = q.filter(Voucher.is_active == True)
    q = q.filter(db.or_(Voucher.valid_from == None, Voucher.valid_from <= now))
    q = q.filter(db.or_(Voucher.valid_to == None, Voucher.valid_to >= now))
    q = q.filter(db.or_(
        Voucher.usage_limit == None,
        Voucher.usage_limit == 0,
        Voucher.usage_count < Voucher.usage_limit
    ))
    return q

@app.route('/admin/vouchers')
def admin_vouchers():
    f_cat = request.args.get('category', '')
    f_merchant = request.args.get('merchant', '')
    f_status = request.args.get('status', '')  # valid, expired, used_up
    q = Voucher.query
    if f_cat:
        q = q.filter_by(category=f_cat)
    if f_merchant:
        q = q.filter(Voucher.merchant.ilike(f'%{f_merchant}%'))

    # Filter by status in SQL instead of Python
    if f_status == 'valid':
        q = _voucher_valid_filter(q)
    elif f_status == 'expired':
        now = datetime.utcnow()
        q = q.filter(db.or_(
            Voucher.is_active == False,
            db.and_(Voucher.valid_to != None, Voucher.valid_to < now),
            db.and_(Voucher.usage_limit != None, Voucher.usage_limit > 0, Voucher.usage_count >= Voucher.usage_limit)
        ))

    items = q.order_by(Voucher.created_at.desc()).all()

    merchants = db.session.query(Voucher.merchant).distinct().all()
    merchants = sorted([m[0] for m in merchants])
    total = Voucher.query.count()
    active = _voucher_valid_filter(Voucher.query).count()
    total_clicks = db.session.query(db.func.sum(Voucher.clicks)).scalar() or 0
    total_conv = db.session.query(db.func.sum(Voucher.conversions)).scalar() or 0
    return render_template('admin/vouchers.html', items=items, merchants=merchants,
        cats=VOUCHER_CATS, cat_map=VOUCHER_CAT_MAP, types=VOUCHER_TYPES,
        f_cat=f_cat, f_merchant=f_merchant, f_status=f_status,
        total=total, active=active, total_clicks=total_clicks, total_conv=total_conv)

@app.route('/admin/voucher/new', methods=['GET','POST'])
def admin_voucher_new():
    if request.method == 'POST':
        from datetime import datetime
        v = Voucher(
            code=request.form['code'].upper().strip(),
            title=request.form['title'],
            description=request.form.get('description',''),
            merchant=request.form['merchant'],
            category=request.form.get('category','general'),
            discount_type=request.form.get('discount_type','percentage'),
            discount_value=float(request.form.get('discount_value',0)),
            min_order=float(request.form.get('min_order',0)),
            max_discount=float(request.form.get('max_discount',0)),
            valid_from=datetime.strptime(request.form.get('valid_from'), '%Y-%m-%d') if request.form.get('valid_from') else datetime.utcnow(),
            valid_to=datetime.strptime(request.form['valid_to'], '%Y-%m-%d'),
            usage_limit=int(request.form.get('usage_limit',0)),
            network=request.form.get('network','shopee'),
            affiliate_url=request.form.get('affiliate_url',''),
            terms=request.form.get('terms',''),
            icon=request.form.get('icon','🎫'),
            color=request.form.get('color','#e74c3c'),
            is_active=request.form.get('is_active') == 'on',
            is_featured=request.form.get('is_featured') == 'on',
            is_exclusive=request.form.get('is_exclusive') == 'on',
            sync_mode=request.form.get('sync_mode','manual')
        )
        db.session.add(v); db.session.commit()
        flash(f'Da them voucher: {v.code}', 'success')
        return redirect(url_for('admin_vouchers'))
    return render_template('admin/voucher_form.html', voucher=None, cats=VOUCHER_CATS, types=VOUCHER_TYPES)

@app.route('/admin/voucher/<int:vid>', methods=['GET','POST'])
def admin_voucher_edit(vid):
    v = Voucher.query.get_or_404(vid)
    if request.method == 'POST':
        from datetime import datetime
        v.code = request.form['code'].upper().strip()
        v.title = request.form['title']
        v.description = request.form.get('description','')
        v.merchant = request.form['merchant']
        v.category = request.form.get('category','general')
        v.discount_type = request.form.get('discount_type','percentage')
        v.discount_value = float(request.form.get('discount_value',0))
        v.min_order = float(request.form.get('min_order',0))
        v.max_discount = float(request.form.get('max_discount',0))
        v.valid_from = datetime.strptime(request.form.get('valid_from'), '%Y-%m-%d') if request.form.get('valid_from') else v.valid_from
        v.valid_to = datetime.strptime(request.form['valid_to'], '%Y-%m-%d')
        v.usage_limit = int(request.form.get('usage_limit',0))
        v.network = request.form.get('network','shopee')
        v.affiliate_url = request.form.get('affiliate_url','')
        v.terms = request.form.get('terms','')
        v.icon = request.form.get('icon','🎫')
        v.color = request.form.get('color','#e74c3c')
        v.is_active = request.form.get('is_active') == 'on'
        v.is_featured = request.form.get('is_featured') == 'on'
        v.is_exclusive = request.form.get('is_exclusive') == 'on'
        v.embed_code = request.form.get('embed_code', '')
        v.sync_mode = request.form.get('sync_mode', 'manual')
        v.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Da cap nhat voucher: {v.code}', 'success')
        return redirect(url_for('admin_vouchers'))
    return render_template('admin/voucher_form.html', voucher=v, cats=VOUCHER_CATS, types=VOUCHER_TYPES)

@app.route('/admin/voucher/<int:vid>/delete', methods=['POST'])
def admin_voucher_delete(vid):
    v = Voucher.query.get_or_404(vid)
    db.session.delete(v); db.session.commit()
    flash('Da xoa voucher', 'success')
    return redirect(url_for('admin_vouchers'))

# =============================================
# ADMIN — VOUCHER WIDGETS (AccessTrade, etc.)
# =============================================
@app.route('/admin/voucher-widgets')
def admin_voucher_widgets():
    """Manage voucher embed widgets from affiliate networks"""
    widgets = VoucherWidget.query.order_by(VoucherWidget.position, VoucherWidget.created_at.desc()).all()
    return render_template('admin/voucher_widgets.html', widgets=widgets)

@app.route('/admin/voucher-widget/new', methods=['GET','POST'])
def admin_voucher_widget_new():
    """Create new voucher widget"""
    if request.method == 'POST':
        w = VoucherWidget(
            name=request.form['name'],
            network=request.form.get('network', 'accesstrade'),
            embed_code=request.form['embed_code'],
            description=request.form.get('description', ''),
            placement=request.form.get('placement', 'voucher_page'),
            position=int(request.form.get('position', 1)),
            is_active=request.form.get('is_active') == 'on'
        )
        db.session.add(w)
        db.session.commit()
        flash(f'Đã thêm widget: {w.name}', 'success')
        return redirect(url_for('admin_voucher_widgets'))
    return render_template('admin/voucher_widget_form.html', widget=None)

@app.route('/admin/voucher-widget/<int:wid>', methods=['GET','POST'])
def admin_voucher_widget_edit(wid):
    """Edit voucher widget"""
    w = VoucherWidget.query.get_or_404(wid)
    if request.method == 'POST':
        w.name = request.form['name']
        w.network = request.form.get('network', 'accesstrade')
        w.embed_code = request.form['embed_code']
        w.description = request.form.get('description', '')
        w.placement = request.form.get('placement', 'voucher_page')
        w.position = int(request.form.get('position', 1))
        w.is_active = request.form.get('is_active') == 'on'
        w.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Đã cập nhật widget: {w.name}', 'success')
        return redirect(url_for('admin_voucher_widgets'))
    return render_template('admin/voucher_widget_form.html', widget=w)

@app.route('/admin/voucher-widget/<int:wid>/toggle', methods=['POST'])
def admin_voucher_widget_toggle(wid):
    """Toggle widget active status"""
    w = VoucherWidget.query.get_or_404(wid)
    w.is_active = not w.is_active
    db.session.commit()
    flash(f'Widget {w.name}: {"Hiển thị" if w.is_active else "Ẩn"}', 'success')
    return redirect(url_for('admin_voucher_widgets'))

@app.route('/admin/voucher-widget/<int:wid>/delete', methods=['POST'])
def admin_voucher_widget_delete(wid):
    """Delete voucher widget"""
    w = VoucherWidget.query.get_or_404(wid)
    name = w.name
    db.session.delete(w)
    db.session.commit()
    flash(f'Đã xóa widget: {name}', 'success')
    return redirect(url_for('admin_voucher_widgets'))

# =============================================
# ADMIN — VOUCHER SYNC (AccessTrade Auto-Import)
# =============================================

# Merchant → category mapping for auto-categorization
MERCHANT_CAT_MAP = {
    'shopee': 'shopping', 'lazada': 'shopping', 'tiki': 'shopping', 'sendo': 'shopping',
    'tiktok': 'shopping', 'yes24': 'shopping', 'jd': 'shopping',
    'grab': 'food', 'grabfood': 'food', 'shopeefood': 'food', 'baemin': 'food',
    'gojek': 'food', 'loship': 'food',
    'traveloka': 'travel', 'agoda': 'travel', 'klook': 'travel', 'booking': 'travel',
    'vietnam airlines': 'travel', 'vietjet': 'travel', 'trip.com': 'travel', 'vntrip': 'travel',
    'fpt shop': 'tech', 'cellphones': 'tech', 'dien may xanh': 'tech', 'phong vu': 'tech',
    'the gioi di dong': 'tech', 'gearvn': 'tech',
    'guardian': 'health', 'hasaki': 'health', 'pharmacity': 'health',
    'cgv': 'entertainment', 'galaxy': 'entertainment', 'lotte cinema': 'entertainment',
}

# Merchant → icon mapping
MERCHANT_ICON_MAP = {
    'shopee': '🟠', 'lazada': '🔵', 'tiki': '🔷', 'sendo': '🔴',
    'grab': '🟢', 'grabfood': '🟢', 'traveloka': '🔵', 'agoda': '🏨',
    'klook': '🟠', 'fpt shop': '💻', 'cellphones': '📱', 'dien may xanh': '💚',
    'tiktok': '🎵', 'cgv': '🎬', 'momo': '💜',
}

# Merchant → color mapping
MERCHANT_COLOR_MAP = {
    'shopee': '#ee4d2d', 'lazada': '#0f146d', 'tiki': '#1a94ff', 'sendo': '#ee2624',
    'grab': '#00b14f', 'traveloka': '#0064d2', 'agoda': '#5392f9', 'klook': '#ff5722',
    'fpt shop': '#d70018', 'cellphones': '#d70018', 'tiktok': '#000000',
}

def _guess_category(merchant_name):
    """Guess voucher category from merchant name"""
    name_lower = (merchant_name or '').lower()
    for key, cat in MERCHANT_CAT_MAP.items():
        if key in name_lower:
            return cat
    return 'shopping'

def _guess_icon(merchant_name):
    name_lower = (merchant_name or '').lower()
    for key, icon in MERCHANT_ICON_MAP.items():
        if key in name_lower:
            return icon
    return '🎫'

def _guess_color(merchant_name):
    name_lower = (merchant_name or '').lower()
    for key, color in MERCHANT_COLOR_MAP.items():
        if key in name_lower:
            return color
    return '#e74c3c'

def _parse_discount(text):
    """Try to parse discount type & value from offer text"""
    import re
    text = (text or '').lower()
    # Match "giảm 50%" or "50%" or "discount 30%"
    m = re.search(r'(\d+)\s*%', text)
    if m:
        return 'percentage', float(m.group(1))
    # Match "giảm 50k" or "giảm 50.000đ" or "50,000đ"
    m = re.search(r'(\d[\d.,]*)\s*(k|đ|d|vnd)', text)
    if m:
        val_str = m.group(1).replace('.', '').replace(',', '')
        val = float(val_str)
        if m.group(2) == 'k':
            val *= 1000
        return 'fixed_amount', val
    # Match "freeship" or "free ship"
    if 'freeship' in text or 'free ship' in text or 'miễn phí' in text:
        return 'free_shipping', 0
    return 'percentage', 0

def _parse_datetime(date_str):
    """Parse various date formats from AccessTrade"""
    if not date_str:
        return None
    from datetime import datetime as dt
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return dt.strptime(date_str.strip()[:19], fmt)
        except:
            continue
    return None

@app.route('/admin/voucher-sync')
def admin_voucher_sync():
    """Dashboard for AccessTrade voucher auto-sync"""
    from accesstrade_integration import get_accesstrade_api
    api = get_accesstrade_api()
    api_connected = api is not None

    # Stats
    total_synced = Voucher.query.filter_by(sync_mode='api').count()
    total_active = _voucher_valid_filter(Voucher.query.filter_by(sync_mode='api')).count()
    total_manual = Voucher.query.filter_by(sync_mode='manual').count()

    # Sync settings from SiteSettings
    auto_sync_enabled = SiteSettings.get('voucher_auto_sync', 'off') == 'on'
    sync_interval = SiteSettings.get('voucher_sync_interval', '6')
    last_sync = SiteSettings.get('voucher_last_sync', '')
    last_sync_count = SiteSettings.get('voucher_last_sync_count', '0')
    last_sync_error = SiteSettings.get('voucher_last_sync_error', '')

    # Recent API-synced vouchers
    recent = Voucher.query.filter_by(sync_mode='api').order_by(Voucher.created_at.desc()).limit(20).all()

    return render_template('admin/voucher_sync.html',
        api_connected=api_connected,
        total_synced=total_synced, total_active=total_active, total_manual=total_manual,
        auto_sync_enabled=auto_sync_enabled, sync_interval=sync_interval,
        last_sync=last_sync, last_sync_count=last_sync_count, last_sync_error=last_sync_error,
        recent=recent)

@app.route('/admin/voucher-sync/merchants')
def admin_voucher_sync_merchants():
    """Get merchant list from AccessTrade API for dropdown filter"""
    from accesstrade_integration import get_accesstrade_api
    api = get_accesstrade_api()
    if not api:
        return {'merchants': []}
    try:
        merchants = api.get_merchant_list()
        return {'merchants': merchants}
    except Exception:
        return {'merchants': []}

@app.route('/admin/voucher-sync/fetch', methods=['POST'])
def admin_voucher_sync_fetch():
    """Fetch offers from AccessTrade API (preview before import).

    Supports multiple sources via JSON body:
      source: 'all' (default) | 'hot' | 'expiring' | 'url'
      merchant: filter by merchant (for source='all')
      period: 1=weekly, 2=monthly (for source='hot')
      product_url: product link (for source='url')
    """
    from accesstrade_integration import get_accesstrade_api
    api = get_accesstrade_api()
    if not api:
        return {'error': 'AccessTrade API chưa cấu hình. Vào Settings → API để nhập key.'}, 400

    try:
        data = request.get_json(silent=True) or {}
        source = data.get('source', 'all')
        merchant = data.get('merchant', '')

        if source == 'hot':
            period = data.get('period', 1)
            raw = api.get_coupons_hot(limit=50, date=period)
            offers = [api._parse_offer(o) for o in raw]
        elif source == 'expiring':
            offers = api.get_offers_detailed(limit=50, scope='expiring')
        elif source == 'url':
            product_url = data.get('product_url', '').strip()
            if not product_url:
                return {'error': 'Vui lòng nhập link sản phẩm'}, 400
            raw = api.search_coupons_by_url(product_url)
            offers = [api._parse_offer(o) for o in raw]
        else:
            offers = api.get_offers_detailed(limit=100, merchant=merchant or None)

        # Count total coupons
        total_coupons = sum(len(o.get('coupons', [])) for o in offers)
        # Mark which ones already exist
        existing_ids = set()
        for v in Voucher.query.filter(Voucher.accesstrade_offer_id != '', Voucher.accesstrade_offer_id != None).all():
            existing_ids.add(v.accesstrade_offer_id)
        existing_codes = set(v.code.upper() for v in Voucher.query.all())

        for o in offers:
            oid = o['offer_id']
            o['already_imported'] = oid in existing_ids
            for c in o.get('coupons', []):
                c['already_imported'] = (c.get('code', '') or '').upper() in existing_codes

        return {
            'offers': offers,
            'total_offers': len(offers),
            'total_coupons': total_coupons,
            'existing_count': len(existing_ids)
        }
    except Exception as e:
        return {'error': f'Lỗi khi lấy dữ liệu: {str(e)}'}, 500

@app.route('/admin/voucher-sync/import', methods=['POST'])
def admin_voucher_sync_import():
    """Import selected offers as vouchers"""
    from accesstrade_integration import get_accesstrade_api
    data = request.get_json() or {}
    selected = data.get('selected', [])  # list of {offer_id, code, merchant, ...}

    if not selected:
        return {'error': 'Chưa chọn voucher nào để import'}, 400

    api = get_accesstrade_api()
    if not api:
        return {'error': 'AccessTrade API chưa cấu hình'}, 400

    imported = 0
    skipped = 0
    errors = []

    for item in selected:
        try:
            code = (item.get('code') or '').upper().strip()
            if not code:
                code = f"AT-{item.get('offer_id', 'X')}-{imported+1}"

            # Check duplicate
            existing = Voucher.query.filter(
                db.or_(Voucher.code == code,
                       db.and_(Voucher.accesstrade_offer_id == item.get('offer_id', ''),
                               Voucher.accesstrade_offer_id != ''))
            ).first()

            if existing:
                skipped += 1
                continue

            merchant = item.get('merchant', 'N/A')
            title = item.get('title') or item.get('offer_name') or f'Ưu đãi {merchant}'
            desc = item.get('description', '')

            # Use API discount fields if available, fallback to parsing title
            api_disc_val = item.get('discount_value')
            api_disc_pct = item.get('discount_percentage')
            api_min_spend = item.get('min_spend')
            api_max_value = item.get('max_value')

            if api_disc_pct and float(api_disc_pct) > 0:
                d_type = 'percentage'
                d_val = float(api_disc_pct)
            elif api_disc_val and float(api_disc_val) > 0:
                d_type = 'fixed_amount'
                d_val = float(api_disc_val)
            else:
                d_type, d_val = _parse_discount(title + ' ' + desc)

            # Parse dates
            valid_from = _parse_datetime(item.get('start_date')) or datetime.utcnow()
            valid_to = _parse_datetime(item.get('end_date'))
            if not valid_to:
                valid_to = datetime.utcnow() + timedelta(days=30)

            v = Voucher(
                code=code,
                title=title[:300],
                description=desc[:2000] if desc else '',
                merchant=merchant,
                category=_guess_category(merchant),
                discount_type=d_type,
                discount_value=d_val,
                min_order=float(api_min_spend) if api_min_spend else 0,
                max_discount=float(api_max_value) if api_max_value else 0,
                valid_from=valid_from,
                valid_to=valid_to,
                network='accesstrade',
                affiliate_url=item.get('aff_link', ''),
                icon=_guess_icon(merchant),
                color=_guess_color(merchant),
                is_active=True,
                sync_mode='api',
                accesstrade_offer_id=item.get('offer_id', ''),
            )
            db.session.add(v)
            imported += 1
        except Exception as e:
            errors.append(f"{item.get('code','?')}: {str(e)}")

    db.session.commit()

    # Update sync stats
    SiteSettings.set_val('voucher_last_sync', datetime.utcnow().strftime('%Y-%m-%d %H:%M'))
    SiteSettings.set_val('voucher_last_sync_count', str(imported))

    return {
        'imported': imported,
        'skipped': skipped,
        'errors': errors,
        'message': f'Đã import {imported} voucher, bỏ qua {skipped} trùng lặp'
    }

@app.route('/admin/voucher-sync/auto', methods=['POST'])
def admin_voucher_sync_auto():
    """Toggle auto-sync and save settings"""
    data = request.get_json() or {}
    enabled = data.get('enabled', False)
    interval = data.get('interval', '6')

    SiteSettings.set_val('voucher_auto_sync', 'on' if enabled else 'off')
    SiteSettings.set_val('voucher_sync_interval', str(interval))
    db.session.commit()

    return {'status': 'ok', 'auto_sync': enabled, 'interval': interval}

@app.route('/admin/voucher-sync/run', methods=['POST'])
def admin_voucher_sync_run():
    """Run sync now — fetch all offers and auto-import new ones"""
    from accesstrade_integration import get_accesstrade_api
    api = get_accesstrade_api()
    if not api:
        return {'error': 'AccessTrade API chưa cấu hình'}, 400

    try:
        offers = api.get_offers_detailed(limit=100)
        existing_codes = set(v.code for v in Voucher.query.all())
        existing_at_ids = set()
        for v in Voucher.query.filter(Voucher.accesstrade_offer_id != '', Voucher.accesstrade_offer_id != None).all():
            existing_at_ids.add(v.accesstrade_offer_id)

        imported = 0
        for offer in offers:
            oid = offer['offer_id']
            if oid in existing_at_ids:
                continue
            merchant = offer.get('merchant', 'N/A')
            # Import offer-level voucher
            coupons = offer.get('coupons', [])
            # Extract API discount fields
            api_disc_pct = offer.get('discount_percentage')
            api_disc_val = offer.get('discount_value')
            api_min_spend = offer.get('min_spend')
            api_max_value = offer.get('max_value')

            if coupons:
                for c in coupons:
                    code = (c.get('code', '') or '').upper().strip()
                    if not code or code in existing_codes:
                        continue
                    title = c.get('description') or offer.get('offer_name') or f'Ưu đãi {merchant}'

                    if api_disc_pct and float(api_disc_pct) > 0:
                        d_type, d_val = 'percentage', float(api_disc_pct)
                    elif api_disc_val and float(api_disc_val) > 0:
                        d_type, d_val = 'fixed_amount', float(api_disc_val)
                    else:
                        d_type, d_val = _parse_discount(title)

                    valid_from = _parse_datetime(c.get('start_date') or offer.get('start_date')) or datetime.utcnow()
                    valid_to = _parse_datetime(c.get('end_date') or offer.get('end_date'))
                    if not valid_to:
                        valid_to = datetime.utcnow() + timedelta(days=30)

                    v = Voucher(
                        code=code, title=title[:300],
                        description=offer.get('description', '')[:2000],
                        merchant=merchant, category=_guess_category(merchant),
                        discount_type=d_type, discount_value=d_val,
                        min_order=float(api_min_spend) if api_min_spend else 0,
                        max_discount=float(api_max_value) if api_max_value else 0,
                        valid_from=valid_from, valid_to=valid_to,
                        network='accesstrade', affiliate_url=offer.get('aff_link', ''),
                        icon=_guess_icon(merchant), color=_guess_color(merchant),
                        is_active=True, sync_mode='api',
                        accesstrade_offer_id=oid,
                    )
                    db.session.add(v)
                    existing_codes.add(code)
                    imported += 1
            else:
                # Offer without coupon codes — create as deal
                code = f"AT-{oid}"
                if code in existing_codes:
                    continue
                title = offer.get('offer_name') or f'Ưu đãi {merchant}'

                if api_disc_pct and float(api_disc_pct) > 0:
                    d_type, d_val = 'percentage', float(api_disc_pct)
                elif api_disc_val and float(api_disc_val) > 0:
                    d_type, d_val = 'fixed_amount', float(api_disc_val)
                else:
                    d_type, d_val = _parse_discount(title + ' ' + offer.get('description', ''))

                valid_from = _parse_datetime(offer.get('start_date')) or datetime.utcnow()
                valid_to = _parse_datetime(offer.get('end_date'))
                if not valid_to:
                    valid_to = datetime.utcnow() + timedelta(days=30)
                v = Voucher(
                    code=code, title=title[:300],
                    description=offer.get('description', '')[:2000],
                    merchant=merchant, category=_guess_category(merchant),
                    discount_type=d_type, discount_value=d_val,
                    min_order=float(api_min_spend) if api_min_spend else 0,
                    max_discount=float(api_max_value) if api_max_value else 0,
                    valid_from=valid_from, valid_to=valid_to,
                    network='accesstrade', affiliate_url=offer.get('aff_link', ''),
                    icon=_guess_icon(merchant), color=_guess_color(merchant),
                    is_active=True, sync_mode='api',
                    accesstrade_offer_id=oid,
                )
                db.session.add(v)
                existing_codes.add(code)
                imported += 1

        # Auto-deactivate expired API vouchers
        expired_count = 0
        for v in Voucher.query.filter_by(sync_mode='api', is_active=True).all():
            if v.valid_to and v.valid_to < datetime.utcnow():
                v.is_active = False
                expired_count += 1

        db.session.commit()

        SiteSettings.set_val('voucher_last_sync', datetime.utcnow().strftime('%Y-%m-%d %H:%M'))
        SiteSettings.set_val('voucher_last_sync_count', str(imported))
        SiteSettings.set_val('voucher_last_sync_error', '')

        return {
            'imported': imported, 'expired': expired_count,
            'message': f'Đã import {imported} voucher mới, vô hiệu {expired_count} voucher hết hạn'
        }
    except Exception as e:
        SiteSettings.set_val('voucher_last_sync_error', str(e))
        db.session.commit()
        return {'error': str(e)}, 500

@app.route('/admin/voucher-sync/cleanup', methods=['POST'])
def admin_voucher_sync_cleanup():
    """Remove all expired API-synced vouchers"""
    expired = Voucher.query.filter(
        Voucher.sync_mode == 'api',
        Voucher.valid_to < datetime.utcnow()
    ).all()
    count = len(expired)
    for v in expired:
        db.session.delete(v)
    db.session.commit()
    return {'deleted': count, 'message': f'Đã xóa {count} voucher hết hạn'}

# =============================================
# AI AUTO-CONTENT ENGINE
# =============================================

@app.route('/admin/content-calendar')
def admin_content_calendar():
    """Content Calendar - monthly overview with events and scheduled content"""
    import calendar as cal_mod
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)

    # Get calendar data
    first_day = date(year, month, 1)
    days_in_month = cal_mod.monthrange(year, month)[1]
    last_day = date(year, month, days_in_month)

    # Get events for this month
    events = ContentEvent.query.filter(
        ContentEvent.start_date <= last_day,
        db.or_(ContentEvent.end_date >= first_day, ContentEvent.end_date.is_(None)),
        ContentEvent.is_active == True
    ).all()

    # Get scheduled queue items
    queue_items = ContentQueue.query.filter(
        ContentQueue.scheduled_at >= datetime(year, month, 1),
        ContentQueue.scheduled_at <= datetime(year, month, days_in_month, 23, 59, 59)
    ).all()

    # Build calendar grid
    cal = cal_mod.Calendar(firstweekday=0)
    weeks = cal.monthdatescalendar(year, month)

    # Map events and queue items to dates
    date_events = {}
    for e in events:
        d = e.start_date
        end = e.end_date or e.start_date
        while d <= end and d <= last_day:
            if d >= first_day:
                date_events.setdefault(d, []).append({'type': 'event', 'obj': e})
            d += timedelta(days=1)

    for q in queue_items:
        if q.scheduled_at:
            qd = q.scheduled_at.date()
            date_events.setdefault(qd, []).append({'type': 'queue', 'obj': q})

    # Navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    verticals = Vertical.query.filter_by(status='published').all()

    return render_template('admin/content_calendar.html',
        year=year, month=month, weeks=weeks, date_events=date_events,
        events=events, queue_items=queue_items,
        prev_year=prev_year, prev_month=prev_month,
        next_year=next_year, next_month=next_month,
        month_name=cal_mod.month_name[month],
        today=date.today(), verticals=verticals)


@app.route('/admin/content-calendar/event', methods=['POST'])
def admin_content_event_save():
    """Save a content event"""
    event_id = request.form.get('event_id', type=int)
    if event_id:
        event = ContentEvent.query.get_or_404(event_id)
    else:
        event = ContentEvent(name='', start_date=date.today())
        db.session.add(event)

    event.name = request.form.get('name', '')
    event.event_type = request.form.get('event_type', 'holiday')
    event.start_date = datetime.strptime(request.form.get('start_date', ''), '%Y-%m-%d').date()
    end = request.form.get('end_date', '')
    event.end_date = datetime.strptime(end, '%Y-%m-%d').date() if end else None
    event.keywords = request.form.get('keywords', '')
    event.verticals = request.form.get('verticals', 'all')
    event.icon = request.form.get('icon', '')
    event.recurrence = request.form.get('recurrence', 'yearly')
    event.auto_generate = 'auto_generate' in request.form
    event.is_active = True
    db.session.commit()
    flash(f'Event saved: {event.name}', 'success')
    return redirect(url_for('admin_content_calendar'))


@app.route('/admin/content-calendar/event/<int:eid>/delete', methods=['POST'])
def admin_content_event_delete(eid):
    """Delete a content event"""
    e = ContentEvent.query.get_or_404(eid)
    db.session.delete(e)
    db.session.commit()
    flash('Event deleted', 'success')
    return redirect(url_for('admin_content_calendar'))


@app.route('/admin/auto-rules')
def admin_auto_rules():
    """Auto content rules - configure frequency/tone/layer per vertical"""
    verticals = Vertical.query.filter_by(status='published').order_by(Vertical.name).all()
    rules = AutoContentRule.query.all()
    rules_map = {r.vertical_id: r for r in rules}
    return render_template('admin/auto_rules.html', verticals=verticals, rules_map=rules_map)


@app.route('/admin/auto-rules/save', methods=['POST'])
def admin_auto_rules_save():
    """Save auto content rules for a vertical"""
    vid = request.form.get('vertical_id', type=int)
    rule = AutoContentRule.query.filter_by(vertical_id=vid).first()
    if not rule:
        rule = AutoContentRule(vertical_id=vid)
        db.session.add(rule)

    rule.frequency = request.form.get('frequency', 'daily')
    rule.articles_per_day = request.form.get('articles_per_day', 1, type=int)
    rule.knowledge_layer = request.form.get('knowledge_layer', 'auto')
    rule.tone = request.form.get('tone', 'seo')
    rule.auto_publish = 'auto_publish' in request.form
    rule.is_active = 'is_active' in request.form
    rule.topics_to_avoid = request.form.get('topics_to_avoid', '')
    rule.focus_keywords = request.form.get('focus_keywords', '')
    db.session.commit()
    flash(f'Rules saved for vertical', 'success')
    return redirect(url_for('admin_auto_rules'))


@app.route('/admin/content-queue')
def admin_content_queue():
    """Content Queue - review AI-suggested topics"""
    status_filter = request.args.get('status', 'all')
    vertical_filter = request.args.get('vertical', 'all')

    query = ContentQueue.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    if vertical_filter != 'all':
        v = Vertical.query.filter_by(slug=vertical_filter).first()
        if v:
            query = query.filter_by(vertical_id=v.id)

    queue = query.order_by(ContentQueue.created_at.desc()).all()
    verticals = Vertical.query.filter_by(status='published').all()

    stats = {
        'pending': ContentQueue.query.filter_by(status='pending').count(),
        'review': ContentQueue.query.filter_by(status='review').count(),
        'published': ContentQueue.query.filter_by(status='published').count(),
        'skipped': ContentQueue.query.filter_by(status='skipped').count(),
    }

    return render_template('admin/content_queue.html',
        queue=queue, verticals=verticals,
        status_filter=status_filter, vertical_filter=vertical_filter,
        stats=stats)


@app.route('/admin/content-queue/add', methods=['POST'])
def admin_content_queue_add():
    """Add item to content queue"""
    item = ContentQueue(
        vertical_id=request.form.get('vertical_id', type=int),
        topic=request.form.get('topic', ''),
        keywords=request.form.get('keywords', ''),
        knowledge_layer=request.form.get('knowledge_layer', 'L1'),
        source_type='manual',
        status='pending'
    )
    scheduled = request.form.get('scheduled_at', '')
    if scheduled:
        item.scheduled_at = datetime.strptime(scheduled, '%Y-%m-%dT%H:%M')
    db.session.add(item)
    db.session.commit()
    flash(f'Added to queue: {item.topic}', 'success')
    return redirect(url_for('admin_content_queue'))


@app.route('/admin/content-queue/<int:qid>/action', methods=['POST'])
def admin_content_queue_action(qid):
    """Approve/Skip/Edit queue item"""
    item = ContentQueue.query.get_or_404(qid)
    action = request.form.get('action', '')
    if action == 'approve':
        item.status = 'review'
    elif action == 'skip':
        item.status = 'skipped'
    elif action == 'publish':
        item.status = 'published'
        item.published_at = datetime.utcnow()
    elif action == 'edit':
        item.topic = request.form.get('topic', item.topic)
        item.keywords = request.form.get('keywords', item.keywords)
        item.knowledge_layer = request.form.get('knowledge_layer', item.knowledge_layer)
    db.session.commit()
    return redirect(url_for('admin_content_queue'))


@app.route('/admin/content-queue/<int:qid>/delete', methods=['POST'])
def admin_content_queue_delete(qid):
    """Delete queue item"""
    item = ContentQueue.query.get_or_404(qid)
    db.session.delete(item)
    db.session.commit()
    flash('Queue item deleted', 'success')
    return redirect(url_for('admin_content_queue'))


@app.route('/admin/gap-analysis')
def admin_gap_analysis():
    """Gap Analysis - AI analyzes content gaps and suggests auto-fill"""
    verticals = Vertical.query.filter_by(status='published').order_by(Vertical.name).all()

    analysis = []
    for v in verticals:
        segments = Segment.query.filter_by(vertical_id=v.id).all()
        total_zones = 0
        zones_with_content = 0
        empty_zones = []

        for seg in segments:
            zones = Zone.query.filter_by(segment_id=seg.id).all()
            for z in zones:
                total_zones += 1
                parts_count = Part.query.filter_by(zone_id=z.id).count()
                has_seo = bool(z.seo_content and len(z.seo_content.strip()) > 50)
                if parts_count > 0 or has_seo:
                    zones_with_content += 1
                else:
                    empty_zones.append({'segment': seg.name, 'zone': z.name, 'zone_id': z.id})

        articles_count = Article.query.filter_by(vertical_slug=v.slug, status='published').count()
        queue_pending = ContentQueue.query.filter_by(vertical_id=v.id, status='pending').count()
        rule = AutoContentRule.query.filter_by(vertical_id=v.id).first()

        coverage = round(zones_with_content / total_zones * 100) if total_zones > 0 else 0

        analysis.append({
            'vertical': v,
            'total_zones': total_zones,
            'zones_with_content': zones_with_content,
            'coverage': coverage,
            'empty_zones': empty_zones[:5],
            'articles_count': articles_count,
            'queue_pending': queue_pending,
            'has_rule': rule is not None and rule.is_active if rule else False,
            'suggestions': _generate_gap_suggestions(v, coverage, empty_zones, articles_count)
        })

    return render_template('admin/gap_analysis.html', analysis=analysis, verticals=verticals)


def _generate_gap_suggestions(vertical, coverage, empty_zones, articles_count):
    """Generate content gap suggestions based on analysis"""
    suggestions = []
    if coverage < 30:
        suggestions.append({'priority': 'high', 'text': f'Coverage only {coverage}% - need bulk content for {vertical.name}', 'action': 'auto_fill'})
    elif coverage < 70:
        suggestions.append({'priority': 'medium', 'text': f'{len(empty_zones)} zones without content in {vertical.name}', 'action': 'fill_zones'})

    if articles_count < 3:
        suggestions.append({'priority': 'high', 'text': f'Only {articles_count} articles - need knowledge base content', 'action': 'create_articles'})
    elif articles_count < 10:
        suggestions.append({'priority': 'medium', 'text': f'Add more L2/L3 depth articles for {vertical.name}', 'action': 'create_articles'})

    if not suggestions:
        suggestions.append({'priority': 'low', 'text': f'{vertical.name} looking good! Consider seasonal content.', 'action': 'seasonal'})

    return suggestions


# =============================================
# UNILAB HOMEPAGE — Article aggregation from all verticals
# =============================================
@app.route('/')
def unilab_home():
    """Homepage: aggregate articles from all verticals with WordPress Newspaper theme"""
    # Get all active verticals
    verticals = Vertical.query.filter_by(status='published').order_by(Vertical.name).all()

    # Featured article (most recent)
    featured = Article.query.filter_by(status='published').order_by(Article.created_at.desc()).first()

    # Recent articles from all verticals (exclude featured)
    recent_query = Article.query.filter_by(status='published')
    if featured:
        recent_query = recent_query.filter(Article.id != featured.id)
    recent_articles = recent_query.order_by(Article.created_at.desc()).limit(12).all()

    # Popular articles (by views)
    popular_articles = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(6).all()

    # Articles by vertical (for category sections)
    vertical_articles = {}
    for v in verticals:
        articles = Article.query.filter_by(vertical_slug=v.slug, status='published').order_by(Article.created_at.desc()).limit(4).all()
        if articles:
            vertical_articles[v.slug] = {'vertical': v, 'articles': articles}

    return render_template('unilab_home.html',
        featured=featured,
        recent_articles=recent_articles,
        popular_articles=popular_articles,
        verticals=verticals,
        vertical_articles=vertical_articles)

@app.route('/bai-viet/<slug>')
def unilab_article(slug):
    """Article detail page on homepage - read articles without leaving UniLab"""
    article = Article.query.filter_by(slug=slug, status='published').first_or_404()

    # Increment views
    article.views += 1
    db.session.commit()

    # Get vertical info
    vertical = Vertical.query.filter_by(slug=article.vertical_slug).first()

    # Get related articles (same vertical, exclude current)
    related_articles = Article.query.filter_by(
        vertical_slug=article.vertical_slug,
        status='published'
    ).filter(Article.id != article.id).order_by(Article.views.desc()).limit(6).all()

    # Popular articles from all verticals
    popular_articles = Article.query.filter_by(status='published')\
        .order_by(Article.views.desc()).limit(5).all()

    return render_template('unilab_article.html',
        article=article,
        vertical=vertical,
        related_articles=related_articles,
        popular_articles=popular_articles)

@app.route('/robots.txt')
def robots_txt():
    """Serve robots.txt to control search engine indexing"""
    from flask import send_from_directory
    return send_from_directory('static', 'robots.txt', mimetype='text/plain')

# =============================================
# =============================================
# OLD ROUTES REMOVED
# All car/pet/travel common routes now use shared routes:
# /<vertical_slug>, /<vertical_slug>/kien-thuc, etc.
# Only travel special routes kept below:
# =============================================

@app.route('/travel/khach-san')
def travel_hotels():
    v = Vertical.query.filter_by(slug='travel').first_or_404()
    destination = request.args.get('destination', '')
    checkin = request.args.get('checkin', '')
    checkout = request.args.get('checkout', '')
    guests = request.args.get('guests', '2')
    stars = request.args.get('stars', '')

    agoda_enabled = SiteSettings.get('agoda_enabled', '0') == '1'
    api_status = 'configured' if agoda_enabled else 'local_db'

    hotels = []
    if destination:
        q = Hotel.query.filter_by(is_active=True, destination=destination)
        if stars:
            q = q.filter(Hotel.stars == int(stars))
        hotels = q.order_by(Hotel.is_featured.desc(), Hotel.rating.desc()).all()

    # Popular destinations from DB
    dest_counts = db.session.query(Hotel.destination, Hotel.destination_name, db.func.count(Hotel.id)
        ).filter(Hotel.is_active == True).group_by(Hotel.destination, Hotel.destination_name).all()
    dest_icons = {'da-nang':'🏖️','phu-quoc':'🌴','nha-trang':'🌊','ha-noi':'🏯','ho-chi-minh':'🏙️','da-lat':'🌸','hoi-an':'🏮','sa-pa':'🏔️'}
    popular = [{'slug': d[0], 'name': d[1], 'icon': dest_icons.get(d[0],'📍'), 'count': d[2]} for d in dest_counts]

    return render_template('travel/hotels.html', vertical=v, hotels=hotels,
        destination=destination, checkin=checkin, checkout=checkout, guests=guests,
        stars=stars, api_status=api_status, agoda_enabled=agoda_enabled, popular=popular)


@app.route('/travel/ve-tham-quan')
def travel_attractions():
    v = Vertical.query.filter_by(slug='travel').first_or_404()
    f_dest = request.args.get('destination', '')
    f_cat = request.args.get('category', '')
    f_net = request.args.get('network', '')

    q = Attraction.query.filter_by(is_active=True)
    if f_dest:
        q = q.filter(Attraction.destination == f_dest)
    if f_cat:
        q = q.filter(Attraction.category == f_cat)
    if f_net:
        q = q.filter(Attraction.network == f_net)
    items = q.order_by(Attraction.is_featured.desc(), Attraction.rating.desc()).all()

    destinations = db.session.query(Attraction.destination, Attraction.destination_name
        ).filter(Attraction.is_active == True).distinct().all()
    cat_icons = {'zoo':'🦁','aquarium':'🐠','cable_car':'🚡','theme_park':'🎢','museum':'🏛️','tour':'🚌','show':'🎭','waterpark':'🌊'}
    cat_names = {'zoo':'Sở thú','aquarium':'Thủy cung','cable_car':'Cáp treo','theme_park':'Công viên','museum':'Bảo tàng','tour':'Tour','show':'Show diễn','waterpark':'Công viên nước'}
    cats_available = db.session.query(Attraction.category, db.func.count(Attraction.id)
        ).filter(Attraction.is_active == True).group_by(Attraction.category).all()

    return render_template('travel/attractions.html', vertical=v, items=items,
        destinations=destinations, cats_available=cats_available,
        cat_icons=cat_icons, cat_names=cat_names,
        f_dest=f_dest, f_cat=f_cat, f_net=f_net)


# SHARED VERTICAL ROUTES (Dynamic)
# =============================================
def get_template_path(vertical_slug, template_name):
    """Get the correct template path for a vertical.
    All verticals use shared templates. Extra nav (hotels, attractions)
    is handled via conditional block in shared/base.html."""
    return f'shared/{template_name}'

def get_vertical_config(vertical_slug):
    """Get vertical-specific customization config"""
    configs = {
        'car': {
            'hero_title': 'Kiến thức ô tô',
            'hero_subtitle': 'từ tổng thể đến từng bu-lông',
            'hero_desc': 'Tìm hiểu chi tiết về phụ tùng, hệ thống xe, bảo dưỡng và nâng cấp. Tra cứu mã OEM, so sánh giá, và mua đúng sản phẩm.',
            'hero_cta1': 'Khám phá phân khúc',
            'segments_label': 'phân khúc xe',
            'segments_heading': 'Phân khúc xe',
            'tier1_desc': 'Thị trường, xu hướng, OEM vs aftermarket, chi phí bảo dưỡng tổng quan.',
            'tier2_desc': 'Hệ thống treo, phanh, điện, động cơ — cấu tạo và nguyên lý hoạt động.',
            'tier3_desc': 'Bài viết sâu về từng phụ tùng: khi nào thay, chọn loại nào, mẹo tiết kiệm.',
            'cta_title': 'Không tìm thấy phụ tùng cần tra cứu?',
            'cta_desc': 'Hệ thống kiến thức ô tô đang được mở rộng mỗi ngày. Chọn phân khúc xe để xem chi tiết từng hệ thống.',
            'cta_button': 'Chọn phân khúc →',
            'products_title': 'Sản phẩm phụ tùng ô tô',
            'products_subtitle': 'Giá tốt nhất từ các sàn TMĐT — Shopee, Lazada, Tiki',
            'products_icon': '🛒',
            'parts_label': 'phụ tùng',
            'parts_heading': 'Phụ tùng',
        },
        'pet': {
            'hero_title': 'Kiến thức thú cưng',
            'hero_subtitle': 'chăm sóc đúng cách từ ngày đầu',
            'hero_desc': 'Tìm hiểu dinh dưỡng, sức khỏe, huấn luyện cho chó, mèo, cá cảnh. Review sản phẩm, so sánh giá.',
            'hero_cta1': 'Khám phá',
            'segments_label': 'danh mục',
            'segments_heading': 'Danh mục',
            'tier1_desc': 'Tổng quan thị trường, xu hướng, chi phí.',
            'tier2_desc': 'Hệ thống, quy trình, phương pháp.',
            'tier3_desc': 'Review sản phẩm, so sánh, hướng dẫn cụ thể.',
            'cta_title': 'Khám phá thêm kiến thức',
            'cta_desc': 'Hệ thống kiến thức đang được mở rộng mỗi ngày.',
            'cta_button': 'Khám phá ngay →',
            'products_title': 'Sản phẩm thú cưng',
            'products_subtitle': 'Review chi tiết, giá tốt từ các sàn TMĐT',
            'products_icon': '🛒',
            'parts_label': 'sản phẩm',
            'parts_heading': 'Sản phẩm',
        },
        'travel': {
            'hero_title': 'Khám phá du lịch',
            'hero_subtitle': 'trải nghiệm đáng nhớ từng điểm đến',
            'hero_desc': 'Khách sạn, tour, vé tham quan, hướng dẫn chi tiết. Giá tốt từ Agoda, Klook, Traveloka.',
            'hero_cta1': 'Khám phá điểm đến',
            'segments_label': 'điểm đến',
            'segments_heading': 'Điểm đến',
            'tier1_desc': 'Xu hướng du lịch, chi phí tổng quan.',
            'tier2_desc': 'Hướng dẫn, kinh nghiệm, tips du lịch.',
            'tier3_desc': 'Review khách sạn, tour, vé tham quan cụ thể.',
            'cta_title': 'Lên kế hoạch chuyến đi',
            'cta_desc': 'Khám phá các điểm đến và trải nghiệm tuyệt vời.',
            'cta_button': 'Xem điểm đến →',
            'products_title': 'Khách sạn & Vé tham quan',
            'products_subtitle': 'Giá tốt nhất từ Agoda, Klook, Traveloka',
            'products_icon': '🏨',
            'parts_label': 'trải nghiệm',
            'parts_heading': 'Trải nghiệm',
        },
        'bike': {
            'hero_title': 'Kiến thức xe đạp',
            'hero_subtitle': 'từ chọn xe đến nâng cấp chi tiết',
            'hero_desc': 'Road bike, MTB, touring — chọn xe phù hợp, bảo dưỡng đúng cách, nâng cấp hiệu quả. Tư vấn groupset, bánh xe, phụ kiện.',
            'hero_cta1': 'Khám phá loại xe',
            'segments_label': 'loại xe',
            'segments_heading': 'Loại xe đạp',
            'tier1_desc': 'Thị trường xe đạp, xu hướng, chi phí tổng quan, chọn xe phù hợp.',
            'tier2_desc': 'Hệ thống truyền động, phanh, bánh xe — cấu tạo và nguyên lý.',
            'tier3_desc': 'Review chi tiết từng bộ phận: groupset, vành, lốp, yên, tay lái.',
            'cta_title': 'Bắt đầu hành trình đạp xe?',
            'cta_desc': 'Khám phá kiến thức từ chọn xe đến nâng cấp, bảo dưỡng chuyên sâu.',
            'cta_button': 'Chọn loại xe →',
            'products_title': 'Phụ tùng & Phụ kiện xe đạp',
            'products_subtitle': 'Groupset, vành, lốp, phụ kiện — giá tốt từ Shopee, Lazada, Tiki',
            'products_icon': '🚴',
            'parts_label': 'phụ tùng',
            'parts_heading': 'Phụ tùng xe đạp',
        },
        'beauty': {
            'hero_title': 'Kiến thức làm đẹp',
            'hero_subtitle': 'skincare, makeup & chăm sóc bản thân',
            'hero_desc': 'Review mỹ phẩm, hướng dẫn skincare routine, so sánh thành phần. Serum, kem dưỡng, chống nắng — chọn đúng cho da bạn.',
            'hero_cta1': 'Khám phá danh mục',
            'segments_label': 'danh mục',
            'segments_heading': 'Danh mục làm đẹp',
            'tier1_desc': 'Thị trường mỹ phẩm, xu hướng K-beauty, clean beauty.',
            'tier2_desc': 'Quy trình skincare, phương pháp chăm sóc da theo loại da.',
            'tier3_desc': 'Review chi tiết sản phẩm: thành phần, cách dùng, so sánh giá.',
            'cta_title': 'Chưa tìm thấy sản phẩm phù hợp?',
            'cta_desc': 'Hệ thống review mỹ phẩm đang mở rộng mỗi ngày. Khám phá thêm theo danh mục.',
            'cta_button': 'Xem danh mục →',
            'products_title': 'Mỹ phẩm & Skincare',
            'products_subtitle': 'Review chi tiết, giá tốt từ Shopee, Lazada, Tiki',
            'products_icon': '💄',
            'parts_label': 'sản phẩm',
            'parts_heading': 'Sản phẩm',
        },
        'tech': {
            'hero_title': 'Kiến thức công nghệ',
            'hero_subtitle': 'smartphone, tai nghe & gadgets',
            'hero_desc': 'So sánh chip, camera, màn hình. Review điện thoại, tai nghe, phụ kiện. Chọn thiết bị phù hợp nhu cầu và ngân sách.',
            'hero_cta1': 'Khám phá danh mục',
            'segments_label': 'danh mục',
            'segments_heading': 'Danh mục thiết bị',
            'tier1_desc': 'Thị trường smartphone, xu hướng AI, chip mới nhất.',
            'tier2_desc': 'Hệ thống camera, màn hình, pin — cấu tạo và so sánh.',
            'tier3_desc': 'Review chi tiết: benchmark, camera test, pin thực tế.',
            'cta_title': 'Cần tư vấn chọn thiết bị?',
            'cta_desc': 'So sánh chi tiết giữa các thiết bị, phụ kiện theo ngân sách.',
            'cta_button': 'Xem danh mục →',
            'products_title': 'Điện thoại & Phụ kiện',
            'products_subtitle': 'Giá tốt nhất từ Shopee, Lazada, Tiki, CellphoneS',
            'products_icon': '📱',
            'parts_label': 'thiết bị',
            'parts_heading': 'Thiết bị',
        },
        'sport': {
            'hero_title': 'Kiến thức thể thao',
            'hero_subtitle': 'từ tập luyện đến thi đấu chuyên nghiệp',
            'hero_desc': 'Giày chạy, đồ gym, dinh dưỡng thể thao, thiết bị tập luyện. Review chi tiết, so sánh giá, hướng dẫn chọn đúng.',
            'hero_cta1': 'Khám phá bộ môn',
            'segments_label': 'bộ môn',
            'segments_heading': 'Bộ môn thể thao',
            'tier1_desc': 'Thị trường thể thao, xu hướng fitness, chi phí tập luyện.',
            'tier2_desc': 'Kỹ thuật tập luyện, phương pháp, chương trình training.',
            'tier3_desc': 'Review chi tiết gear: giày, đồ tập, thiết bị, dinh dưỡng.',
            'cta_title': 'Bắt đầu hành trình thể thao?',
            'cta_desc': 'Khám phá kiến thức từ cơ bản đến nâng cao cho mọi bộ môn.',
            'cta_button': 'Chọn bộ môn →',
            'products_title': 'Đồ thể thao & Thiết bị',
            'products_subtitle': 'Giày, quần áo, gear — giá tốt từ Shopee, Lazada, Decathlon',
            'products_icon': '🏋️',
            'parts_label': 'sản phẩm',
            'parts_heading': 'Sản phẩm',
        },
    }
    return configs.get(vertical_slug, {})

@app.route('/<vertical_slug>')
def vertical_index(vertical_slug):
    v = Vertical.query.filter_by(slug=vertical_slug).first_or_404()
    articles_nganh = Article.query.filter_by(vertical_slug=vertical_slug, tier='nganh', status='published').order_by(Article.created_at.desc()).limit(4).all()
    articles_chung = Article.query.filter_by(vertical_slug=vertical_slug, tier='chung', status='published').order_by(Article.created_at.desc()).limit(6).all()
    articles_chitiet = Article.query.filter_by(vertical_slug=vertical_slug, tier='chi-tiet', status='published').order_by(Article.created_at.desc()).limit(6).all()
    recent_articles = Article.query.filter_by(vertical_slug=vertical_slug, status='published').order_by(Article.created_at.desc()).limit(8).all()
    config = get_vertical_config(vertical_slug)
    template = get_template_path(vertical_slug, 'index.html')
    return render_template(template, vertical=v, articles_nganh=articles_nganh,
        articles_chung=articles_chung, articles_chitiet=articles_chitiet, recent_articles=recent_articles, **config)

@app.route('/<vertical_slug>/kien-thuc')
def vertical_knowledge(vertical_slug):
    v = Vertical.query.filter_by(slug=vertical_slug).first_or_404()
    articles_nganh = Article.query.filter_by(vertical_slug=vertical_slug, tier='nganh', status='published').order_by(Article.created_at.desc()).all()
    articles_chung = Article.query.filter_by(vertical_slug=vertical_slug, tier='chung', status='published').order_by(Article.created_at.desc()).all()
    articles_chitiet = Article.query.filter_by(vertical_slug=vertical_slug, tier='chi-tiet', status='published').order_by(Article.created_at.desc()).all()
    template = get_template_path(vertical_slug, 'knowledge.html')
    return render_template(template, vertical=v, articles_nganh=articles_nganh,
        articles_chung=articles_chung, articles_chitiet=articles_chitiet)

@app.route('/<vertical_slug>/san-pham')
def vertical_products(vertical_slug):
    v = Vertical.query.filter_by(slug=vertical_slug).first_or_404()
    f_zone = request.args.get('zone', '')
    f_network = request.args.get('network', '')
    page = request.args.get('page', 1, type=int)
    per_page = 24
    q = db.session.query(AffiliateLink, Part, Zone, Segment).join(
        Part, AffiliateLink.part_id == Part.id
    ).join(Zone, Part.zone_id == Zone.id
    ).join(Segment, Zone.segment_id == Segment.id
    ).filter(Segment.vertical_id == v.id, AffiliateLink.is_active == True)
    if f_zone:
        q = q.filter(Zone.slug == f_zone)
    if f_network:
        q = q.filter(AffiliateLink.network == f_network)
    total_count = q.count()
    pagination = q.order_by(AffiliateLink.price.desc()).paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    segments = Segment.query.filter_by(vertical_id=v.id).all()
    zone_counts = dict(db.session.query(Zone.slug, db.func.count(AffiliateLink.id)).join(
        Part, Zone.id == Part.zone_id).join(AffiliateLink, Part.id == AffiliateLink.part_id
    ).join(Segment, Zone.segment_id == Segment.id).filter(
        Segment.vertical_id == v.id, AffiliateLink.is_active == True
    ).group_by(Zone.slug).all())
    networks = db.session.query(AffiliateLink.network).join(Part).join(Zone).join(Segment).filter(
        Segment.vertical_id == v.id).distinct().all()
    config = get_vertical_config(vertical_slug)
    template = get_template_path(vertical_slug, 'products.html')
    return render_template(template, vertical=v, products=products,
        segments=segments, zone_counts=zone_counts, networks=[n[0] for n in networks],
        f_zone=f_zone, f_network=f_network, product_url='vertical_products',
        pagination=pagination, total_count=total_count, page=page, **config)

@app.route('/<vertical_slug>/bai-viet/<slug>')
def vertical_article(vertical_slug, slug):
    v = Vertical.query.filter_by(slug=vertical_slug).first_or_404()
    a = Article.query.filter_by(vertical_slug=vertical_slug, slug=slug, status='published').first_or_404()
    a.views += 1
    db.session.commit()

    # Related articles (same category or tier)
    related = Article.query.filter(Article.id != a.id, Article.vertical_slug==vertical_slug, Article.status=='published',
        db.or_(Article.category==a.category, Article.tier==a.tier)
    ).order_by(Article.views.desc()).limit(4).all()

    # Featured articles (top by views, different from current)
    featured = Article.query.filter(Article.id != a.id, Article.vertical_slug==vertical_slug, Article.status=='published'
    ).order_by(Article.views.desc()).limit(5).all()

    # Related parts for product carousel — flatten to individual affiliate cards
    carousel_items = []
    if a.related_zone_slug:
        z = Zone.query.filter_by(slug=a.related_zone_slug).first()
        if z:
            carousel_limit = int(SiteSettings.get('carousel_product_limit', '3'))
            parts = Part.query.filter_by(zone_id=z.id, status='published').all()
            for p in parts:
                for al in p.affiliate_links:
                    if al.is_active:
                        carousel_items.append(al)
                        if len(carousel_items) >= carousel_limit:
                            break
                if len(carousel_items) >= carousel_limit:
                    break

    # Banners for sidebar (vertical-specific or global)
    banners = Banner.query.filter(
        Banner.is_active==True,
        Banner.placement=='sidebar',
        db.or_(Banner.vertical_slug=='', Banner.vertical_slug==vertical_slug)
    ).order_by(Banner.position).all()

    return render_template('shared/article.html', vertical=v, article=a, related=related, featured=featured, carousel_items=carousel_items, banners=banners)

@app.route('/article/<int:article_id>/feedback', methods=['POST'])
def submit_article_feedback(article_id):
    """Submit feedback on article accuracy"""
    article = Article.query.get_or_404(article_id)

    feedback = ArticleFeedback(
        article_id=article_id,
        feedback_type=request.form.get('feedback_type', 'other'),
        description=request.form.get('description', ''),
        user_email=request.form.get('user_email', ''),
        status='pending'
    )

    db.session.add(feedback)
    db.session.commit()

    flash('Cảm ơn phản hồi của bạn! Chúng tôi sẽ xem xét và cải thiện nội dung.', 'success')
    return redirect(request.referrer or url_for('vertical_article', vertical_slug=article.vertical_slug, slug=article.slug))

@app.route('/<vertical_slug>/<segment_slug>')
def vertical_segment(vertical_slug, segment_slug):
    v = Vertical.query.filter_by(slug=vertical_slug).first_or_404()
    s = Segment.query.filter_by(vertical_id=v.id, slug=segment_slug).first_or_404()
    articles = Article.query.filter_by(vertical_slug=vertical_slug, related_segment_slug=segment_slug, status='published').order_by(Article.created_at.desc()).limit(4).all()
    config = get_vertical_config(vertical_slug)
    return render_template('shared/segment.html', vertical=v, segment=s, articles=articles, **config)

@app.route('/<vertical_slug>/<segment_slug>/<zone_slug>')
def vertical_zone(vertical_slug, segment_slug, zone_slug):
    v = Vertical.query.filter_by(slug=vertical_slug).first_or_404()
    s = Segment.query.filter_by(vertical_id=v.id, slug=segment_slug).first_or_404()
    z = Zone.query.filter_by(segment_id=s.id, slug=zone_slug).first_or_404()
    articles = Article.query.filter_by(vertical_slug=vertical_slug, related_zone_slug=zone_slug, status='published').order_by(Article.created_at.desc()).limit(4).all()
    if not articles:
        articles = Article.query.filter_by(vertical_slug=vertical_slug, category=zone_slug, status='published').limit(4).all()
    config = get_vertical_config(vertical_slug)
    return render_template('shared/zone.html', vertical=v, segment=s, zone=z, articles=articles, **config)

@app.route('/<vertical_slug>/<segment_slug>/<zone_slug>/<part_slug>')
def vertical_part(vertical_slug, segment_slug, zone_slug, part_slug):
    v = Vertical.query.filter_by(slug=vertical_slug).first_or_404()
    s = Segment.query.filter_by(vertical_id=v.id, slug=segment_slug).first_or_404()
    z = Zone.query.filter_by(segment_id=s.id, slug=zone_slug).first_or_404()
    p = Part.query.filter_by(zone_id=z.id, slug=part_slug).first_or_404()
    related_articles = Article.query.filter_by(vertical_slug=vertical_slug, related_zone_slug=zone_slug, status='published').limit(3).all()
    if not related_articles:
        related_articles = Article.query.filter_by(vertical_slug=vertical_slug, tier='chi-tiet', status='published').limit(3).all()
    related_parts = Part.query.filter(Part.zone_id==z.id, Part.id!=p.id, Part.status=='published').limit(4).all()
    config = get_vertical_config(vertical_slug)
    return render_template('shared/part.html', vertical=v, segment=s, zone=z, part=p,
        related_articles=related_articles, related_parts=related_parts, **config)

# =============================================
# SHOP ROUTES (Standalone e-commerce aggregator)
# =============================================
@app.route('/shop')
def shop_index():
    """UniShop — aggregated product listing"""
    # Shop display mode from settings
    shop_mode = SiteSettings.get('shop_display_mode', 'hub')  # hub (default) or vertical_only

    # Filters
    f_vertical = request.args.get('vertical', '')
    f_zone = request.args.get('zone', '')
    f_network = request.args.get('network', '')
    f_q = request.args.get('q', '').strip()
    f_sort = request.args.get('sort', 'popular')
    f_price_min = request.args.get('price_min', '', type=str)
    f_price_max = request.args.get('price_max', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 24

    # Base query: join all the way to Vertical
    q = db.session.query(AffiliateLink, Part, Zone, Segment, Vertical).join(
        Part, AffiliateLink.part_id == Part.id
    ).join(Zone, Part.zone_id == Zone.id
    ).join(Segment, Zone.segment_id == Segment.id
    ).join(Vertical, Segment.vertical_id == Vertical.id
    ).filter(AffiliateLink.is_active == True)

    # vertical_only mode: only show products from published verticals
    if shop_mode == 'vertical_only':
        q = q.filter(Vertical.status == 'published')

    # Apply filters
    if f_vertical:
        q = q.filter(Vertical.slug == f_vertical)
    if f_zone:
        q = q.filter(Zone.slug == f_zone)
    if f_network:
        q = q.filter(AffiliateLink.network == f_network)
    if f_q:
        search = f'%{f_q}%'
        q = q.filter(db.or_(
            AffiliateLink.product_name.ilike(search),
            Part.name_vi.ilike(search),
            Part.tags.ilike(search),
        ))
    if f_price_min:
        try:
            q = q.filter(AffiliateLink.price >= float(f_price_min))
        except ValueError:
            pass
    if f_price_max:
        try:
            q = q.filter(AffiliateLink.price <= float(f_price_max))
        except ValueError:
            pass

    # Sorting
    if f_sort == 'price_asc':
        q = q.order_by(AffiliateLink.price.asc())
    elif f_sort == 'price_desc':
        q = q.order_by(AffiliateLink.price.desc())
    elif f_sort == 'newest':
        q = q.order_by(AffiliateLink.id.desc())
    else:  # popular
        q = q.order_by(AffiliateLink.clicks.desc(), AffiliateLink.price.desc())

    # Paginate (already includes total count internally)
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    filtered_count = pagination.total

    # All verticals for nav (in vertical_only mode, only published non-hub verticals)
    if shop_mode == 'vertical_only':
        verticals = Vertical.query.filter(Vertical.status == 'published', Vertical.slug != 'hub').order_by(Vertical.name).all()
    else:
        verticals = Vertical.query.order_by(Vertical.name).all()

    # Per-vertical counts + total in one query
    vc_rows = db.session.query(Vertical.slug, db.func.count(AffiliateLink.id)).join(
        Segment, Vertical.id == Segment.vertical_id
    ).join(Zone, Segment.id == Zone.segment_id
    ).join(Part, Zone.id == Part.zone_id
    ).join(AffiliateLink, Part.id == AffiliateLink.part_id
    ).filter(AffiliateLink.is_active == True
    ).group_by(Vertical.slug).all()
    vertical_counts = dict(vc_rows)
    total_products = sum(c for _, c in vc_rows)

    # Sidebar: single query for all zone counts (replaces N+1)
    zone_count_q = db.session.query(
        Zone.id, Zone.slug, Zone.name, Zone.icon, Zone.color, Zone.segment_id, Zone.order,
        db.func.count(AffiliateLink.id).label('cnt')
    ).join(Part, Zone.id == Part.zone_id
    ).join(AffiliateLink, Part.id == AffiliateLink.part_id
    ).filter(AffiliateLink.is_active == True)
    if f_vertical:
        zone_count_q = zone_count_q.join(Segment, Zone.segment_id == Segment.id
        ).join(Vertical, Segment.vertical_id == Vertical.id
        ).filter(Vertical.slug == f_vertical)
    zone_count_q = zone_count_q.group_by(Zone.id).all()

    # Build zone lookup: segment_id -> [(slug, name, icon, color, count)]
    zone_by_seg = {}
    active_seg_ids = set()
    for zid, zslug, zname, zicon, zcolor, zsid, zorder, zcnt in zone_count_q:
        if zcnt > 0:
            zone_by_seg.setdefault(zsid, []).append((zorder, zslug, zname, zicon, zcolor, zcnt))
            active_seg_ids.add(zsid)

    # Get segments that have active zones
    sidebar_segments = []
    if active_seg_ids:
        seg_q = Segment.query.filter(Segment.id.in_(active_seg_ids)).order_by(Segment.order)
        for seg in seg_q.all():
            zones_data = [(s, n, i, c, cnt) for _, s, n, i, c, cnt in sorted(zone_by_seg.get(seg.id, []))]
            if zones_data:
                sidebar_segments.append((seg.name, seg.icon, zones_data))

    # Network stats
    net_q = db.session.query(
        AffiliateLink.network, db.func.count(AffiliateLink.id)
    ).filter(AffiliateLink.is_active == True)
    if f_vertical:
        net_q = net_q.join(Part).join(Zone).join(Segment).join(Vertical).filter(Vertical.slug == f_vertical)
    network_stats = net_q.group_by(AffiliateLink.network).order_by(
        db.func.count(AffiliateLink.id).desc()).all()

    # Active names for display
    active_vertical_name = ''
    active_zone_name = ''
    if f_vertical:
        vt_obj = Vertical.query.filter_by(slug=f_vertical).first()
        if vt_obj:
            active_vertical_name = vt_obj.name
    if f_zone:
        z_obj = Zone.query.filter_by(slug=f_zone).first()
        if z_obj:
            active_zone_name = z_obj.name

    return render_template('shop/index.html',
        products=products,
        pagination=pagination,
        verticals=verticals,
        total_products=total_products,
        total_verticals=len(verticals),
        filtered_count=filtered_count,
        vertical_counts=vertical_counts,
        sidebar_segments=sidebar_segments,
        network_stats=network_stats,
        shop_mode=shop_mode,
        f_vertical=f_vertical,
        f_zone=f_zone,
        f_network=f_network,
        f_q=f_q,
        f_sort=f_sort,
        f_price_min=f_price_min,
        f_price_max=f_price_max,
        active_vertical_name=active_vertical_name,
        active_zone_name=active_zone_name,
    )


# =============================================
# VOUCHER ROUTES (Standalone feature)
# =============================================
@app.route('/voucher')
def voucher_index():
    """Voucher listing page with filters"""
    from sqlalchemy import func
    f_category = request.args.get('category', '')
    f_merchant = request.args.get('merchant', '')
    f_type = request.args.get('type', '')  # percentage, fixed_amount, free_shipping
    f_platform = request.args.get('platform', '')  # shopee, lazada, grab...
    f_sort = request.args.get('sort', 'newest')  # newest, discount, expiring

    # Build query
    q = Voucher.query.filter_by(is_active=True)
    if f_category:
        q = q.filter_by(category=f_category)
    if f_merchant:
        q = q.filter(Voucher.merchant.ilike(f'%{f_merchant}%'))
    if f_type:
        q = q.filter_by(discount_type=f_type)
    if f_platform:
        q = q.filter(db.or_(
            Voucher.merchant.ilike(f'%{f_platform}%'),
            Voucher.network.ilike(f'%{f_platform}%')
        ))

    # Get valid vouchers only
    all_vouchers = q.all()
    vouchers = [v for v in all_vouchers if v.is_valid()]

    # Sort
    if f_sort == 'discount':
        vouchers.sort(key=lambda v: v.discount_value or 0, reverse=True)
    elif f_sort == 'expiring':
        vouchers.sort(key=lambda v: v.valid_to or datetime.max)
    else:
        vouchers.sort(key=lambda v: v.created_at or datetime.min, reverse=True)

    # Featured: top discount vouchers as featured if none marked
    featured = Voucher.query.filter_by(is_active=True, is_featured=True).limit(6).all()
    featured = [v for v in featured if v.is_valid()]
    if not featured:
        # Auto-feature: highest discount % vouchers
        featured = sorted(
            [v for v in Voucher.query.filter_by(is_active=True, discount_type='percentage').all() if v.is_valid()],
            key=lambda v: v.discount_value or 0, reverse=True
        )[:6]

    # Get category counts
    cat_counts = db.session.query(Voucher.category, func.count(Voucher.id)).filter_by(is_active=True).group_by(Voucher.category).all()
    categories = dict(cat_counts)

    # Get merchant list with counts
    merchant_counts = db.session.query(Voucher.merchant, func.count(Voucher.id)).filter_by(is_active=True).group_by(Voucher.merchant).order_by(func.count(Voucher.id).desc()).all()
    merchants = [m[0] for m in merchant_counts]
    merchant_count_map = dict(merchant_counts)

    # Platform stats (group by network/domain)
    platform_stats = {}
    for v in Voucher.query.filter_by(is_active=True).all():
        # Determine platform from merchant name or network
        name = (v.merchant or '').lower()
        if 'shopee' in name:
            p = 'Shopee'
        elif 'lazada' in name:
            p = 'Lazada'
        elif 'tiki' in name:
            p = 'Tiki'
        elif 'grab' in name:
            p = 'Grab'
        elif 'traveloka' in name:
            p = 'Traveloka'
        else:
            p = 'Khác'
        platform_stats[p] = platform_stats.get(p, 0) + 1

    # Expiring soon (within 3 days)
    expiring_soon = sorted(
        [v for v in vouchers if v.valid_to and (v.valid_to - datetime.utcnow()).days <= 3],
        key=lambda v: v.valid_to
    )[:6]

    # Get active voucher widgets for display
    widgets = VoucherWidget.query.filter_by(is_active=True, placement='voucher_page').order_by(VoucherWidget.position).all()

    return render_template('voucher/index.html',
        vouchers=vouchers, featured=featured, categories=categories,
        merchants=merchants, merchant_count_map=merchant_count_map,
        platform_stats=platform_stats, expiring_soon=expiring_soon,
        widgets=widgets, f_category=f_category, f_merchant=f_merchant,
        f_type=f_type, f_platform=f_platform, f_sort=f_sort,
        now=datetime.utcnow())

@app.route('/voucher/<code>')
def voucher_detail(code):
    """Voucher detail page"""
    v = Voucher.query.filter_by(code=code).first_or_404()

    # Track click
    v.clicks = (v.clicks or 0) + 1
    db.session.commit()

    # Related vouchers (same category or merchant)
    related = Voucher.query.filter(
        Voucher.id != v.id,
        Voucher.is_active == True,
        db.or_(Voucher.category == v.category, Voucher.merchant == v.merchant)
    ).limit(6).all()
    related = [r for r in related if r.is_valid()]

    return render_template('voucher/detail.html', voucher=v, related=related)

@app.route('/voucher/<int:vid>/use', methods=['POST'])
def voucher_use(vid):
    """Track voucher usage"""
    v = Voucher.query.get_or_404(vid)
    v.usage_count = (v.usage_count or 0) + 1
    v.conversions = (v.conversions or 0) + 1
    db.session.commit()
    return {'status': 'ok', 'usage_count': v.usage_count}

# =============================================
# INIT
# =============================================
def _get_table_columns(table_name):
    """Get set of column names for a table using PRAGMA (single query)."""
    try:
        rows = db.session.execute(db.text(f"PRAGMA table_info({table_name})")).fetchall()
        return {row[1] for row in rows}
    except:
        return set()

def _table_exists(table_name):
    """Check if a table exists."""
    try:
        rows = db.session.execute(db.text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=:t"
        ), {'t': table_name}).fetchall()
        return len(rows) > 0
    except:
        return False

def _ensure_column(table_name, col_name, col_def, existing_cols):
    """Add column if missing. Returns True if added."""
    if col_name not in existing_cols:
        print(f'  [+] Adding {table_name}.{col_name}')
        db.session.execute(db.text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}"))
        return True
    return False

def _run_schema_migration():
    """Fast schema migration — uses PRAGMA to batch-check columns."""
    import time
    t0 = time.time()
    print('[*] Checking database schema...')

    changed = False

    # --- Zone table ---
    zone_cols = _get_table_columns('zone')
    if _ensure_column('zone', 'seo_content', "TEXT DEFAULT ''", zone_cols):
        changed = True

    # --- Banner table ---
    if not _table_exists('banner'):
        print('  [+] Creating banner table')
        db.session.execute(db.text("""
            CREATE TABLE IF NOT EXISTS banner (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                placement VARCHAR(50) DEFAULT 'sidebar',
                vertical_slug VARCHAR(50) DEFAULT '',
                image_url VARCHAR(500) DEFAULT '',
                link_url VARCHAR(500) DEFAULT '',
                html_code TEXT DEFAULT '',
                position INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                impressions INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        changed = True

    # --- Vertical table ---
    vert_cols = _get_table_columns('vertical')
    if _ensure_column('vertical', 'template', "VARCHAR(20) DEFAULT 'general'", vert_cols):
        changed = True
    if _ensure_column('vertical', 'style', "VARCHAR(20) DEFAULT 'classic'", vert_cols):
        changed = True
    if _ensure_column('vertical', 'shop_link', "VARCHAR(500) DEFAULT ''", vert_cols):
        changed = True

    # --- Performance indexes for shop page ---
    try:
        db.session.execute(db.text("CREATE INDEX IF NOT EXISTS ix_affiliate_link_part_id ON affiliate_link (part_id)"))
        db.session.execute(db.text("CREATE INDEX IF NOT EXISTS ix_affiliate_link_is_active ON affiliate_link (is_active)"))
        db.session.execute(db.text("CREATE INDEX IF NOT EXISTS ix_affiliate_link_network ON affiliate_link (network)"))
        db.session.execute(db.text("CREATE INDEX IF NOT EXISTS ix_part_zone_id ON part (zone_id)"))
        db.session.execute(db.text("CREATE INDEX IF NOT EXISTS ix_zone_segment_id ON zone (segment_id)"))
        db.session.execute(db.text("CREATE INDEX IF NOT EXISTS ix_segment_vertical_id ON segment (vertical_id)"))
    except Exception:
        pass

    # --- AffiliateLink table ---
    al_cols = _get_table_columns('affiliate_link')
    if _ensure_column('affiliate_link', 'category', "VARCHAR(100) DEFAULT ''", al_cols):
        changed = True

    # --- Affiliate Network table ---
    an_cols = _get_table_columns('affiliate_network')
    if _ensure_column('affiliate_network', 'deeplink_template', "VARCHAR(1000) DEFAULT ''", an_cols):
        changed = True

    # --- Voucher table ---
    v_cols = _get_table_columns('voucher')
    if _ensure_column('voucher', 'embed_code', "TEXT DEFAULT ''", v_cols):
        changed = True
    if _ensure_column('voucher', 'sync_mode', "VARCHAR(20) DEFAULT 'manual'", v_cols):
        changed = True
    if _ensure_column('voucher', 'accesstrade_offer_id', "VARCHAR(100) DEFAULT ''", v_cols):
        changed = True

    # --- Scheduled CSV Import table ---
    if not _table_exists('scheduled_csv_import'):
        print('  [+] Creating scheduled_csv_import table')
        db.session.execute(db.text("""
            CREATE TABLE IF NOT EXISTS scheduled_csv_import (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                csv_url VARCHAR(1000) NOT NULL,
                part_id INTEGER NOT NULL,
                network VARCHAR(50) DEFAULT 'shopee',
                apply_deeplink BOOLEAN DEFAULT 0,
                update_interval_days INTEGER DEFAULT 7,
                is_active BOOLEAN DEFAULT 1,
                last_import_at DATETIME,
                next_import_at DATETIME,
                last_import_count INTEGER DEFAULT 0,
                last_import_status VARCHAR(20) DEFAULT 'pending',
                last_error TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (part_id) REFERENCES part(id)
            )
        """))
        changed = True

    # --- Voucher Widget table ---
    if not _table_exists('voucher_widget'):
        print('  [+] Creating voucher_widget table')
        db.session.execute(db.text("""
            CREATE TABLE IF NOT EXISTS voucher_widget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                network VARCHAR(50) DEFAULT 'accesstrade',
                embed_code TEXT NOT NULL,
                description TEXT DEFAULT '',
                placement VARCHAR(50) DEFAULT 'voucher_page',
                position INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        changed = True

    if changed:
        db.session.commit()

    elapsed = round((time.time() - t0) * 1000)
    print(f'[*] Schema check done ({elapsed}ms)')


if __name__ == '__main__':
    import os

    # Only init DB once (skip on Werkzeug reloader child process)
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        with app.app_context():
            db.create_all()
            _run_schema_migration()

        # Auto-open browser after server is ready (only once, not on reload)
        import threading, webbrowser
        threading.Timer(1.5, webbrowser.open, args=['http://localhost:7000/admin']).start()

    app.run(host='0.0.0.0', port=7000, debug=True)
