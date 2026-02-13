from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Vertical, Segment, Zone, Part, AffiliateLink, AffiliateNetwork, AffiliateCampaign, AffiliateStats, AIContent, SiteSettings, SocialChannel, VideoProject, VideoPublish, Article, Banner, Hotel, Attraction, Voucher, ArticleFeedback, ScheduledCSVImport, VoucherWidget
from datetime import datetime, date, timedelta
import os, random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unilab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'unilab-secret-2026'
db.init_app(app)

# ═══════════════════════════════════════════
# THEME STYLES CONFIG
# ═══════════════════════════════════════════
THEME_STYLES = {
    'classic': {
        'font_primary': "'Georgia', 'Times New Roman', serif",
        'font_secondary': "'Arial', sans-serif",
        'bg_light': '#ffffff',
        'bg_dark': '#1a1a1a',
        'surface_light': '#f8f9fa',
        'surface_dark': '#2d2d2d',
        'border_light': '#dee2e6',
        'border_dark': '#444',
        'text_light': '#212529',
        'text_dark': '#f8f9fa',
        'text_dim_light': '#6c757d',
        'text_dim_dark': '#adb5bd',
        'accent': '#007bff',
        'accent_hover': '#0056b3',
        'radius': '8px',
    },
    'modern': {
        'font_primary': "'Inter', 'SF Pro Display', -apple-system, system-ui, sans-serif",
        'font_secondary': "'Inter', sans-serif",
        'bg_light': '#fafafa',
        'bg_dark': '#0a0a0a',
        'surface_light': '#ffffff',
        'surface_dark': '#1a1a1a',
        'border_light': '#e5e5e5',
        'border_dark': '#333',
        'text_light': '#0a0a0a',
        'text_dark': '#fafafa',
        'text_dim_light': '#737373',
        'text_dim_dark': '#a3a3a3',
        'accent': '#000000',
        'accent_hover': '#404040',
        'radius': '12px',
    },
    'tech': {
        'font_primary': "'Rajdhani', 'Inter', -apple-system, system-ui, sans-serif",
        'font_secondary': "'Roboto', 'Inter', sans-serif",
        'bg_light': '#f0f0f3',
        'bg_dark': '#000000',
        'surface_light': '#ffffff',
        'surface_dark': '#111111',
        'border_light': '#d5d5d5',
        'border_dark': '#2a2a2a',
        'text_light': '#111111',
        'text_dark': '#f5f5f5',
        'text_dim_light': '#666666',
        'text_dim_dark': '#999999',
        'accent': '#eb0028',
        'accent_hover': '#c70022',
        'radius': '0px',
    },
    'beauty': {
        'font_primary': "'Lora', 'Cormorant Garamond', Georgia, serif",
        'font_secondary': "'Montserrat', sans-serif",
        'bg_light': '#fef5f8',
        'bg_dark': '#1a0d1f',
        'surface_light': '#ffffff',
        'surface_dark': '#2d1b2e',
        'border_light': '#ffd6e7',
        'border_dark': '#4a2d4f',
        'text_light': '#2d1b2e',
        'text_dark': '#fef5f8',
        'text_dim_light': '#8b6a8f',
        'text_dim_dark': '#c5a3ca',
        'accent': '#e91e63',
        'accent_hover': '#c2185b',
        'radius': '12px',
    },
    'car': {
        'font_primary': "'Roboto', -apple-system, system-ui, sans-serif",
        'font_secondary': "'Roboto Mono', monospace",
        'bg_light': '#f8f9fa',
        'bg_dark': '#1a1a1a',
        'surface_light': '#ffffff',
        'surface_dark': '#2d2d2d',
        'border_light': '#e3e3e3',
        'border_dark': '#444',
        'text_light': '#212529',
        'text_dark': '#f8f9fa',
        'text_dim_light': '#6c757d',
        'text_dim_dark': '#adb5bd',
        'accent': '#fdcb6e',
        'accent_hover': '#f1b44c',
        'radius': '8px',
    },
    'pet': {
        'font_primary': "'Nunito', 'Comic Sans MS', cursive",
        'font_secondary': "'Nunito', sans-serif",
        'bg_light': '#fff9f0',
        'bg_dark': '#1a1410',
        'surface_light': '#ffffff',
        'surface_dark': '#2d2820',
        'border_light': '#ffe4c4',
        'border_dark': '#4a3f2d',
        'text_light': '#2d2820',
        'text_dark': '#fff9f0',
        'text_dim_light': '#8b7355',
        'text_dim_dark': '#c5b299',
        'accent': '#ff9ff3',
        'accent_hover': '#e68ae0',
        'radius': '16px',
    },
}

@app.context_processor
def inject_globals():
    try:
        return {
            'sidebar_verticals': Vertical.query.order_by(Vertical.name).all(),
            'now': datetime.utcnow(),
            'THEME_STYLES': THEME_STYLES
        }
    except:
        return {'sidebar_verticals': [], 'now': datetime.utcnow(), 'THEME_STYLES': THEME_STYLES}

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

    # AccessTrade integration
    from accesstrade_integration import get_accesstrade_api
    accesstrade_data = {}
    api = get_accesstrade_api()
    if api:
        try:
            accesstrade_data = {
                'account': api.get_account_info(),
                'stats': api.get_statistics_summary(days=30),
                'campaigns': api.get_campaigns(limit=10),
                'offers': api.get_offers(limit=10),
                'connected': True
            }
        except:
            accesstrade_data['connected'] = False

    return render_template('admin/dashboard.html',
        verticals=verticals,
        total_parts=total_parts, total_links=total_links,
        total_clicks=total_clicks, total_conversions=total_conversions,
        total_ai=total_ai, networks=networks,
        demo_traffic=demo_traffic, demo_revenue=demo_revenue,
        accesstrade=accesstrade_data)

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
            style=request.form.get('style','classic')
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
    return render_template('admin/affiliate_network.html', network=n)

@app.route('/admin/affiliate/network/<int:nid>/connect', methods=['POST'])
def admin_affiliate_connect(nid):
    n = AffiliateNetwork.query.get_or_404(nid)
    n.api_key = request.form.get('api_key','')
    n.status = 'connected' if n.api_key else 'disconnected'
    n.last_sync = datetime.utcnow()
    db.session.commit()
    flash(f'{n.name} -> {"Connected" if n.status=="connected" else "Disconnected"}', 'success')
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
    if request.method == 'POST':
        for key in ['openai_key','claude_key','dalle_key','deepl_key','site_name','default_mode',
                     'agoda_api_key','agoda_site_id','agoda_cid','agoda_enabled']:
            val = request.form.get(key,'')
            cat = 'api' if '_key' in key or '_id' in key or '_cid' in key else 'general'
            SiteSettings.set_val(key, val, cat)
        flash('Da luu settings', 'success')
        return redirect(url_for('admin_settings'))
    settings = {s.key: s.value for s in SiteSettings.query.all()}
    return render_template('admin/settings.html', settings=settings)

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
            from seed_data import seed_pet, seed_pet_articles, seed_products_pet_travel
            try:
                seed_pet()
                seed_pet_articles()
                flash('✅ Pet vertical seeded successfully!', 'success')
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

        elif action == 'seed_all':
            from seed_data import (seed, seed_articles, seed_networks, seed_video,
                seed_pet, seed_pet_articles, seed_travel, seed_travel_articles,
                seed_products_pet_travel, seed_hotels, seed_attractions,
                seed_bike, seed_vouchers, seed_beauty, seed_beauty_articles,
                seed_tech, seed_tech_articles, seed_products_beauty_tech)
            try:
                seed()
                seed_articles()
                seed_networks()
                seed_pet()
                seed_pet_articles()
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
        import openai
        openai.api_key = openai_key

        response = openai.ChatCompletion.create(
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

    products = q.order_by(AffiliateLink.id.desc()).all()
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
        total=total, active=active, total_clicks=total_clicks, total_conv=total_conv)

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

@app.route('/admin/products/import-csv', methods=['GET', 'POST'])
def admin_products_import_csv():
    """Import products from CSV file (Shopee format)"""
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

        # Get form data
        part_id = request.form.get('part_id')
        network = request.form.get('network', 'shopee')
        apply_deeplink = 'apply_deeplink' in request.form

        if not part_id:
            flash('Chưa chọn Part để gắn sản phẩm', 'error')
            return redirect(request.url)

        # Get network for deeplink
        network_obj = None
        if apply_deeplink:
            network_obj = AffiliateNetwork.query.filter_by(slug=network).first()

        count = 0
        for row in csv_reader:
            # CSV format: sku, name, url, price, discount, image, desc, category
            url = row.get('url', '')

            # Apply deeplink if enabled and template exists
            if apply_deeplink and network_obj and network_obj.deeplink_template and url:
                import urllib.parse
                url = network_obj.deeplink_template.replace('{url}', urllib.parse.quote(url))

            al = AffiliateLink(
                part_id=int(part_id),
                network=network,
                product_name=row.get('name', '')[:200],
                url=url,
                price=float(row.get('price', 0)),
                image_url=row.get('image', ''),
                is_active=True
            )
            db.session.add(al)
            count += 1

        db.session.commit()
        flash(f'Đã import {count} sản phẩm thành công!', 'success')
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
    return render_template('admin/products_import_csv.html', parts_tree=parts_tree, networks=networks)

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

    all_vouchers = q.order_by(Voucher.created_at.desc()).all()

    # Filter by status
    if f_status == 'valid':
        items = [v for v in all_vouchers if v.is_valid()]
    elif f_status == 'expired':
        items = [v for v in all_vouchers if not v.is_valid()]
    else:
        items = all_vouchers

    merchants = db.session.query(Voucher.merchant).distinct().all()
    merchants = sorted([m[0] for m in merchants])
    total = Voucher.query.count()
    active = len([v for v in Voucher.query.all() if v.is_valid()])
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
        }
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
    q = db.session.query(AffiliateLink, Part, Zone, Segment).join(
        Part, AffiliateLink.part_id == Part.id
    ).join(Zone, Part.zone_id == Zone.id
    ).join(Segment, Zone.segment_id == Segment.id
    ).filter(Segment.vertical_id == v.id, AffiliateLink.is_active == True)
    if f_zone:
        q = q.filter(Zone.slug == f_zone)
    if f_network:
        q = q.filter(AffiliateLink.network == f_network)
    products = q.order_by(AffiliateLink.price.desc()).all()
    segments = Segment.query.filter_by(vertical_id=v.id).all()
    zone_counts = dict(db.session.query(Zone.slug, db.func.count(AffiliateLink.id)).join(
        Part, Zone.id == Part.zone_id).join(AffiliateLink, Part.id == AffiliateLink.part_id
    ).filter(AffiliateLink.is_active == True).group_by(Zone.slug).all())
    networks = db.session.query(AffiliateLink.network).join(Part).join(Zone).join(Segment).filter(
        Segment.vertical_id == v.id).distinct().all()
    config = get_vertical_config(vertical_slug)
    template = get_template_path(vertical_slug, 'products.html')
    return render_template(template, vertical=v, products=products,
        segments=segments, zone_counts=zone_counts, networks=[n[0] for n in networks],
        f_zone=f_zone, f_network=f_network, product_url='vertical_products', **config)

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

    # Related parts for product carousel
    related_parts = []
    if a.related_zone_slug:
        z = Zone.query.filter_by(slug=a.related_zone_slug).first()
        if z:
            related_parts = Part.query.filter_by(zone_id=z.id, status='published').limit(6).all()

    # Banners for sidebar (vertical-specific or global)
    banners = Banner.query.filter(
        Banner.is_active==True,
        Banner.placement=='sidebar',
        db.or_(Banner.vertical_slug=='', Banner.vertical_slug==vertical_slug)
    ).order_by(Banner.position).all()

    return render_template('shared/article.html', vertical=v, article=a, related=related, featured=featured, related_parts=related_parts, banners=banners)

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
# VOUCHER ROUTES (Standalone feature)
# =============================================
@app.route('/voucher')
def voucher_index():
    """Voucher listing page with filters"""
    f_category = request.args.get('category', '')
    f_merchant = request.args.get('merchant', '')
    f_type = request.args.get('type', '')  # percentage, fixed_amount, free_shipping

    # Build query
    q = Voucher.query.filter_by(is_active=True)
    if f_category:
        q = q.filter_by(category=f_category)
    if f_merchant:
        q = q.filter(Voucher.merchant.ilike(f'%{f_merchant}%'))
    if f_type:
        q = q.filter_by(discount_type=f_type)

    # Get valid vouchers only
    all_vouchers = q.all()
    vouchers = [v for v in all_vouchers if v.is_valid()]

    # Featured vouchers
    featured = Voucher.query.filter_by(is_active=True, is_featured=True).limit(6).all()
    featured = [v for v in featured if v.is_valid()]

    # Get category counts
    from sqlalchemy import func
    cat_counts = db.session.query(Voucher.category, func.count(Voucher.id)).filter_by(is_active=True).group_by(Voucher.category).all()
    categories = dict(cat_counts)

    # Get merchant list
    merchants = db.session.query(Voucher.merchant).filter_by(is_active=True).distinct().all()
    merchants = sorted([m[0] for m in merchants])

    # Get active voucher widgets for display
    widgets = VoucherWidget.query.filter_by(is_active=True, placement='voucher_page').order_by(VoucherWidget.position).all()

    return render_template('voucher/index.html',
        vouchers=vouchers, featured=featured, categories=categories, merchants=merchants,
        widgets=widgets, f_category=f_category, f_merchant=f_merchant, f_type=f_type)

@app.route('/voucher/<code>')
def voucher_detail(code):
    """Voucher detail page"""
    v = Voucher.query.filter_by(code=code).first_or_404()

    # Track click
    v.clicks += 1
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
    v.usage_count += 1
    v.conversions += 1
    db.session.commit()
    return {'status': 'ok', 'usage_count': v.usage_count}

# =============================================
# INIT
# =============================================
if __name__ == '__main__':
    with app.app_context():
        # Create any missing tables
        db.create_all()

        # Auto-migrate: Add missing columns to existing tables
        print('[*] Checking database schema...')
        try:
            # Check if seo_content column exists in zone table
            db.session.execute(db.text("SELECT seo_content FROM zone LIMIT 1"))
        except:
            db.session.rollback()
            print('[+] Adding seo_content column to zone table...')
            db.session.execute(db.text("ALTER TABLE zone ADD COLUMN seo_content TEXT DEFAULT ''"))
            db.session.commit()

        try:
            # Check if banner table exists
            db.session.execute(db.text("SELECT id FROM banner LIMIT 1"))
        except:
            db.session.rollback()
            print('[+] Creating banner table...')
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
            db.session.commit()

        # Add template column to vertical table (if not exists)
        try:
            db.session.execute(db.text("SELECT template FROM vertical LIMIT 1"))
        except:
            db.session.rollback()
            print('[+] Adding template column to vertical table...')
            db.session.execute(db.text("ALTER TABLE vertical ADD COLUMN template VARCHAR(20) DEFAULT 'general'"))
            db.session.commit()

        # Add style column to vertical table (if not exists)
        try:
            db.session.execute(db.text("SELECT style FROM vertical LIMIT 1"))
        except:
            db.session.rollback()
            print('[+] Adding style column to vertical table...')
            db.session.execute(db.text("ALTER TABLE vertical ADD COLUMN style VARCHAR(20) DEFAULT 'classic'"))
            db.session.commit()

        # Set defaults for template/style on existing verticals
        try:
            template_mapping = {'car': 'general', 'pet': 'general', 'bike': 'general', 'travel': 'travel'}
            style_mapping = {'car': 'car', 'pet': 'pet', 'bike': 'bike', 'travel': 'travel'}
            verticals = Vertical.query.all()
            changed = False
            for v in verticals:
                if not v.template or v.template == 'general':
                    new_tmpl = template_mapping.get(v.slug, 'general')
                    if v.template != new_tmpl:
                        v.template = new_tmpl
                        changed = True
                if not v.style or v.style == 'classic':
                    new_style = style_mapping.get(v.slug, 'classic')
                    if v.style != new_style:
                        v.style = new_style
                        changed = True
            if changed:
                db.session.commit()
                print('[+] Set template/style for existing verticals')
        except:
            db.session.rollback()

        # Add deeplink_template column to affiliate_network table (if not exists)
        try:
            db.session.execute(db.text("SELECT deeplink_template FROM affiliate_network LIMIT 1"))
        except:
            db.session.rollback()
            print('[+] Adding deeplink_template column to affiliate_network table...')
            db.session.execute(db.text("ALTER TABLE affiliate_network ADD COLUMN deeplink_template VARCHAR(1000) DEFAULT ''"))
            db.session.commit()

        # Add embed_code column to voucher table (if not exists)
        try:
            db.session.execute(db.text("SELECT embed_code FROM voucher LIMIT 1"))
        except:
            db.session.rollback()
            print('[+] Adding embed_code column to voucher table...')
            db.session.execute(db.text("ALTER TABLE voucher ADD COLUMN embed_code TEXT DEFAULT ''"))
            db.session.commit()

        # Add sync_mode column to voucher table (if not exists)
        try:
            db.session.execute(db.text("SELECT sync_mode FROM voucher LIMIT 1"))
        except:
            db.session.rollback()
            print('[+] Adding sync_mode column to voucher table...')
            db.session.execute(db.text("ALTER TABLE voucher ADD COLUMN sync_mode VARCHAR(20) DEFAULT 'manual'"))
            db.session.commit()

        # Create scheduled_csv_import table (if not exists)
        try:
            db.session.execute(db.text("SELECT id FROM scheduled_csv_import LIMIT 1"))
        except:
            db.session.rollback()
            print('[+] Creating scheduled_csv_import table...')
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
            db.session.commit()

        # Create voucher_widget table (if not exists)
        try:
            db.session.execute(db.text("SELECT id FROM voucher_widget LIMIT 1"))
        except:
            db.session.rollback()
            print('[+] Creating voucher_widget table...')
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
            db.session.commit()

        # Auto-seeding disabled - use admin panel Seed Data page instead
        # Manual seeding via: Admin → Tools → Seed Data
        # print('[*] Checking seed data...')
        # from seed_data import seed, seed_networks, seed_video, seed_articles, seed_pet, seed_pet_articles, seed_travel, seed_travel_articles, seed_products_pet_travel, seed_hotels, seed_attractions, seed_bike, seed_vouchers, seed_beauty, seed_tech
        # seed()
        # seed_networks()
        # seed_video()
        # seed_articles()
        # seed_pet()
        # seed_pet_articles()
        # seed_travel()
        # seed_travel_articles()
        # seed_products_pet_travel()
        # seed_hotels()
        # seed_attractions()
        # seed_bike()
        # seed_vouchers()
        # seed_beauty()
        # seed_tech()
        # print('[✓] Seed check complete!')

        # Auto-generate content disabled - use AI Assistant or manual creation instead
        # print('[*] Checking content generation...')
        # from scripts.auto_generate_content import auto_generate_article_content, auto_generate_zone_seo
        # auto_generate_article_content()
        # auto_generate_zone_seo()
        # print('[✓] Content check complete!')

    app.run(host='0.0.0.0', port=7000, debug=True)
