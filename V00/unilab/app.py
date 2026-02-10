from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Vertical, Segment, Zone, Part, AffiliateLink, AffiliateNetwork, AffiliateCampaign, AffiliateStats, AIContent, SiteSettings, SocialChannel, VideoProject, VideoPublish, Article, Hotel, Attraction
from datetime import datetime, date, timedelta
import os, random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unilab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'unilab-secret-2026'
db.init_app(app)

@app.context_processor
def inject_globals():
    try:
        return {
            'sidebar_verticals': Vertical.query.order_by(Vertical.name).all(),
            'now': datetime.utcnow()
        }
    except:
        return {'sidebar_verticals': [], 'now': datetime.utcnow()}

def slugify(text):
    import re, unicodedata
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')

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

    return render_template('admin/dashboard.html',
        verticals=verticals,
        total_parts=total_parts, total_links=total_links,
        total_clicks=total_clicks, total_conversions=total_conversions,
        total_ai=total_ai, networks=networks,
        demo_traffic=demo_traffic, demo_revenue=demo_revenue)

# =============================================
# ADMIN — VERTICALS CRUD
# =============================================
@app.route('/admin/verticals')
def admin_verticals():
    verticals = Vertical.query.order_by(Vertical.created_at.desc()).all()
    return render_template('admin/verticals.html', verticals=verticals)

@app.route('/admin/vertical/new', methods=['GET','POST'])
def admin_vertical_new():
    if request.method == 'POST':
        v = Vertical(
            name=request.form['name'], slug=slugify(request.form['name']),
            icon=request.form.get('icon',''), color=request.form.get('color','#6c5ce7'),
            description=request.form.get('description',''), status='draft'
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

# =============================================
# ADMIN — ARTICLES (Knowledge Base)
# =============================================
@app.route('/admin/articles')
def admin_articles():
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('admin/articles.html', articles=articles)

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
            slug=request.form.get('name','').lower().replace(' ','-').replace("'","")[:60],
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
            slug=request.form.get('name','').lower().replace(' ','-').replace("'","")[:60],
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
# CAR PUBLIC ROUTES
# =============================================
@app.route('/car')
def car_index():
    v = Vertical.query.filter_by(slug='car').first_or_404()
    articles_nganh = Article.query.filter_by(vertical_slug='car', tier='nganh', status='published').order_by(Article.created_at.desc()).limit(4).all()
    articles_chung = Article.query.filter_by(vertical_slug='car', tier='chung', status='published').order_by(Article.created_at.desc()).limit(6).all()
    articles_chitiet = Article.query.filter_by(vertical_slug='car', tier='chi-tiet', status='published').order_by(Article.created_at.desc()).limit(6).all()
    recent_articles = Article.query.filter_by(vertical_slug='car', status='published').order_by(Article.created_at.desc()).limit(8).all()
    return render_template('car/index.html', vertical=v, articles_nganh=articles_nganh,
        articles_chung=articles_chung, articles_chitiet=articles_chitiet, recent_articles=recent_articles)

@app.route('/car/kien-thuc')
def car_knowledge():
    v = Vertical.query.filter_by(slug='car').first_or_404()
    articles_nganh = Article.query.filter_by(vertical_slug='car', tier='nganh', status='published').order_by(Article.created_at.desc()).all()
    articles_chung = Article.query.filter_by(vertical_slug='car', tier='chung', status='published').order_by(Article.created_at.desc()).all()
    articles_chitiet = Article.query.filter_by(vertical_slug='car', tier='chi-tiet', status='published').order_by(Article.created_at.desc()).all()
    return render_template('car/knowledge.html', vertical=v, articles_nganh=articles_nganh,
        articles_chung=articles_chung, articles_chitiet=articles_chitiet)

@app.route('/car/san-pham')
def car_products():
    v = Vertical.query.filter_by(slug='car').first_or_404()
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
    # Count products per zone
    zone_counts = dict(db.session.query(Zone.slug, db.func.count(AffiliateLink.id)).join(
        Part, Zone.id == Part.zone_id).join(AffiliateLink, Part.id == AffiliateLink.part_id
    ).filter(AffiliateLink.is_active == True).group_by(Zone.slug).all())
    networks = db.session.query(AffiliateLink.network).join(Part).join(Zone).join(Segment).filter(
        Segment.vertical_id == v.id).distinct().all()
    return render_template('car/products.html', vertical=v, products=products,
        segments=segments, zone_counts=zone_counts, networks=[n[0] for n in networks],
        f_zone=f_zone, f_network=f_network, product_url='car_products')

@app.route('/car/bai-viet/<slug>')
def car_article(slug):
    v = Vertical.query.filter_by(slug='car').first_or_404()
    a = Article.query.filter_by(vertical_slug='car', slug=slug, status='published').first_or_404()
    a.views += 1
    db.session.commit()
    # Related articles: same category or tags overlap
    related = Article.query.filter(Article.id != a.id, Article.vertical_slug=='car', Article.status=='published',
        db.or_(Article.category==a.category, Article.tier==a.tier)
    ).order_by(Article.views.desc()).limit(4).all()
    # Products from same zone if chi-tiet
    related_parts = []
    if a.related_zone_slug:
        z = Zone.query.filter_by(slug=a.related_zone_slug).first()
        if z:
            related_parts = Part.query.filter_by(zone_id=z.id, status='published').limit(6).all()
    return render_template('car/article.html', vertical=v, article=a, related=related, related_parts=related_parts)

@app.route('/car/<segment_slug>')
def car_segment(segment_slug):
    v = Vertical.query.filter_by(slug='car').first_or_404()
    s = Segment.query.filter_by(vertical_id=v.id, slug=segment_slug).first_or_404()
    articles = Article.query.filter_by(vertical_slug='car', related_segment_slug=segment_slug, status='published').order_by(Article.created_at.desc()).limit(4).all()
    return render_template('car/segment.html', vertical=v, segment=s, articles=articles)

@app.route('/car/<segment_slug>/<zone_slug>')
def car_zone(segment_slug, zone_slug):
    v = Vertical.query.filter_by(slug='car').first_or_404()
    s = Segment.query.filter_by(vertical_id=v.id, slug=segment_slug).first_or_404()
    z = Zone.query.filter_by(segment_id=s.id, slug=zone_slug).first_or_404()
    articles = Article.query.filter_by(vertical_slug='car', related_zone_slug=zone_slug, status='published').order_by(Article.created_at.desc()).limit(4).all()
    if not articles:
        articles = Article.query.filter_by(vertical_slug='car', category=zone_slug, status='published').limit(4).all()
    return render_template('car/zone.html', vertical=v, segment=s, zone=z, articles=articles)

@app.route('/car/<segment_slug>/<zone_slug>/<part_slug>')
def car_part(segment_slug, zone_slug, part_slug):
    v = Vertical.query.filter_by(slug='car').first_or_404()
    s = Segment.query.filter_by(vertical_id=v.id, slug=segment_slug).first_or_404()
    z = Zone.query.filter_by(segment_id=s.id, slug=zone_slug).first_or_404()
    p = Part.query.filter_by(zone_id=z.id, slug=part_slug).first_or_404()
    # Related articles by tags overlap or same zone
    related_articles = Article.query.filter_by(vertical_slug='car', related_zone_slug=zone_slug, status='published').limit(3).all()
    if not related_articles:
        related_articles = Article.query.filter_by(vertical_slug='car', tier='chi-tiet', status='published').limit(3).all()
    # Related parts in same zone (exclude current)
    related_parts = Part.query.filter(Part.zone_id==z.id, Part.id!=p.id, Part.status=='published').limit(4).all()
    return render_template('car/part.html', vertical=v, segment=s, zone=z, part=p,
        related_articles=related_articles, related_parts=related_parts)

# =============================================
# PET PUBLIC ROUTES
# =============================================
@app.route('/pet')
def pet_index():
    v = Vertical.query.filter_by(slug='pet').first_or_404()
    articles_nganh = Article.query.filter_by(vertical_slug='pet', tier='nganh', status='published').order_by(Article.created_at.desc()).limit(4).all()
    articles_chung = Article.query.filter_by(vertical_slug='pet', tier='chung', status='published').order_by(Article.created_at.desc()).limit(6).all()
    articles_chitiet = Article.query.filter_by(vertical_slug='pet', tier='chi-tiet', status='published').order_by(Article.created_at.desc()).limit(6).all()
    recent_articles = Article.query.filter_by(vertical_slug='pet', status='published').order_by(Article.created_at.desc()).limit(8).all()
    return render_template('pet/index.html', vertical=v, articles_nganh=articles_nganh, articles_chung=articles_chung, articles_chitiet=articles_chitiet, recent_articles=recent_articles)

@app.route('/pet/kien-thuc')
def pet_knowledge():
    v = Vertical.query.filter_by(slug='pet').first_or_404()
    articles_nganh = Article.query.filter_by(vertical_slug='pet', tier='nganh', status='published').all()
    articles_chung = Article.query.filter_by(vertical_slug='pet', tier='chung', status='published').all()
    articles_chitiet = Article.query.filter_by(vertical_slug='pet', tier='chi-tiet', status='published').all()
    return render_template('pet/knowledge.html', vertical=v, articles_nganh=articles_nganh, articles_chung=articles_chung, articles_chitiet=articles_chitiet)

@app.route('/pet/san-pham')
def pet_products():
    v = Vertical.query.filter_by(slug='pet').first_or_404()
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
    return render_template('pet/products.html', vertical=v, products=products,
        segments=segments, zone_counts=zone_counts, networks=[n[0] for n in networks],
        f_zone=f_zone, f_network=f_network, product_url='pet_products')

@app.route('/pet/bai-viet/<slug>')
def pet_article(slug):
    v = Vertical.query.filter_by(slug='pet').first_or_404()
    a = Article.query.filter_by(vertical_slug='pet', slug=slug, status='published').first_or_404()
    a.views += 1; db.session.commit()
    related = Article.query.filter(Article.id != a.id, Article.vertical_slug=='pet', Article.status=='published',
        db.or_(Article.category==a.category, Article.tier==a.tier)).order_by(Article.views.desc()).limit(4).all()
    related_parts = []
    if a.related_zone_slug:
        z = Zone.query.filter_by(slug=a.related_zone_slug).first()
        if z: related_parts = Part.query.filter_by(zone_id=z.id, status='published').limit(6).all()
    return render_template('pet/article.html', vertical=v, article=a, related=related, related_parts=related_parts)

@app.route('/pet/<segment_slug>')
def pet_segment(segment_slug):
    v = Vertical.query.filter_by(slug='pet').first_or_404()
    s = Segment.query.filter_by(vertical_id=v.id, slug=segment_slug).first_or_404()
    articles = Article.query.filter_by(vertical_slug='pet', related_segment_slug=segment_slug, status='published').limit(4).all()
    return render_template('pet/segment.html', vertical=v, segment=s, articles=articles)

@app.route('/pet/<segment_slug>/<zone_slug>')
def pet_zone(segment_slug, zone_slug):
    v = Vertical.query.filter_by(slug='pet').first_or_404()
    s = Segment.query.filter_by(vertical_id=v.id, slug=segment_slug).first_or_404()
    z = Zone.query.filter_by(segment_id=s.id, slug=zone_slug).first_or_404()
    articles = Article.query.filter_by(vertical_slug='pet', related_zone_slug=zone_slug, status='published').limit(4).all()
    if not articles: articles = Article.query.filter_by(vertical_slug='pet', category=zone_slug, status='published').limit(4).all()
    return render_template('pet/zone.html', vertical=v, segment=s, zone=z, articles=articles)

@app.route('/pet/<segment_slug>/<zone_slug>/<part_slug>')
def pet_part(segment_slug, zone_slug, part_slug):
    v = Vertical.query.filter_by(slug='pet').first_or_404()
    s = Segment.query.filter_by(vertical_id=v.id, slug=segment_slug).first_or_404()
    z = Zone.query.filter_by(segment_id=s.id, slug=zone_slug).first_or_404()
    p = Part.query.filter_by(zone_id=z.id, slug=part_slug).first_or_404()
    related_articles = Article.query.filter_by(vertical_slug='pet', related_zone_slug=zone_slug, status='published').limit(3).all()
    if not related_articles: related_articles = Article.query.filter_by(vertical_slug='pet', tier='chi-tiet', status='published').limit(3).all()
    related_parts = Part.query.filter(Part.zone_id==z.id, Part.id!=p.id, Part.status=='published').limit(4).all()
    return render_template('pet/part.html', vertical=v, segment=s, zone=z, part=p, related_articles=related_articles, related_parts=related_parts)

# =============================================
# TRAVEL PUBLIC ROUTES
# =============================================
@app.route('/travel')
def travel_index():
    v = Vertical.query.filter_by(slug='travel').first_or_404()
    articles_nganh = Article.query.filter_by(vertical_slug='travel', tier='nganh', status='published').order_by(Article.created_at.desc()).limit(4).all()
    articles_chung = Article.query.filter_by(vertical_slug='travel', tier='chung', status='published').order_by(Article.created_at.desc()).limit(6).all()
    articles_chitiet = Article.query.filter_by(vertical_slug='travel', tier='chi-tiet', status='published').order_by(Article.created_at.desc()).limit(6).all()
    recent_articles = Article.query.filter_by(vertical_slug='travel', status='published').order_by(Article.created_at.desc()).limit(8).all()
    return render_template('travel/index.html', vertical=v, articles_nganh=articles_nganh, articles_chung=articles_chung, articles_chitiet=articles_chitiet, recent_articles=recent_articles)

@app.route('/travel/kien-thuc')
def travel_knowledge():
    v = Vertical.query.filter_by(slug='travel').first_or_404()
    articles_nganh = Article.query.filter_by(vertical_slug='travel', tier='nganh', status='published').all()
    articles_chung = Article.query.filter_by(vertical_slug='travel', tier='chung', status='published').all()
    articles_chitiet = Article.query.filter_by(vertical_slug='travel', tier='chi-tiet', status='published').all()
    return render_template('travel/knowledge.html', vertical=v, articles_nganh=articles_nganh, articles_chung=articles_chung, articles_chitiet=articles_chitiet)

@app.route('/travel/san-pham')
def travel_products():
    v = Vertical.query.filter_by(slug='travel').first_or_404()
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
    return render_template('travel/products.html', vertical=v, products=products,
        segments=segments, zone_counts=zone_counts, networks=[n[0] for n in networks],
        f_zone=f_zone, f_network=f_network, product_url='travel_products')

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

@app.route('/travel/bai-viet/<slug>')
def travel_article(slug):
    v = Vertical.query.filter_by(slug='travel').first_or_404()
    a = Article.query.filter_by(vertical_slug='travel', slug=slug, status='published').first_or_404()
    a.views += 1; db.session.commit()
    related = Article.query.filter(Article.id != a.id, Article.vertical_slug=='travel', Article.status=='published',
        db.or_(Article.category==a.category, Article.tier==a.tier)).order_by(Article.views.desc()).limit(4).all()
    related_parts = []
    if a.related_zone_slug:
        z = Zone.query.filter_by(slug=a.related_zone_slug).first()
        if z: related_parts = Part.query.filter_by(zone_id=z.id, status='published').limit(6).all()
    return render_template('travel/article.html', vertical=v, article=a, related=related, related_parts=related_parts)

@app.route('/travel/<segment_slug>')
def travel_segment(segment_slug):
    v = Vertical.query.filter_by(slug='travel').first_or_404()
    s = Segment.query.filter_by(vertical_id=v.id, slug=segment_slug).first_or_404()
    articles = Article.query.filter_by(vertical_slug='travel', related_segment_slug=segment_slug, status='published').limit(4).all()
    return render_template('travel/segment.html', vertical=v, segment=s, articles=articles)

@app.route('/travel/<segment_slug>/<zone_slug>')
def travel_zone(segment_slug, zone_slug):
    v = Vertical.query.filter_by(slug='travel').first_or_404()
    s = Segment.query.filter_by(vertical_id=v.id, slug=segment_slug).first_or_404()
    z = Zone.query.filter_by(segment_id=s.id, slug=zone_slug).first_or_404()
    articles = Article.query.filter_by(vertical_slug='travel', related_zone_slug=zone_slug, status='published').limit(4).all()
    if not articles: articles = Article.query.filter_by(vertical_slug='travel', category=zone_slug, status='published').limit(4).all()
    return render_template('travel/zone.html', vertical=v, segment=s, zone=z, articles=articles)

@app.route('/travel/<segment_slug>/<zone_slug>/<part_slug>')
def travel_part(segment_slug, zone_slug, part_slug):
    v = Vertical.query.filter_by(slug='travel').first_or_404()
    s = Segment.query.filter_by(vertical_id=v.id, slug=segment_slug).first_or_404()
    z = Zone.query.filter_by(segment_id=s.id, slug=zone_slug).first_or_404()
    p = Part.query.filter_by(zone_id=z.id, slug=part_slug).first_or_404()
    related_articles = Article.query.filter_by(vertical_slug='travel', related_zone_slug=zone_slug, status='published').limit(3).all()
    if not related_articles: related_articles = Article.query.filter_by(vertical_slug='travel', tier='chi-tiet', status='published').limit(3).all()
    related_parts = Part.query.filter(Part.zone_id==z.id, Part.id!=p.id, Part.status=='published').limit(4).all()
    return render_template('travel/part.html', vertical=v, segment=s, zone=z, part=p, related_articles=related_articles, related_parts=related_parts)

# =============================================
# INIT
# =============================================
if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('instance/unilab.db'):
            db.create_all()
            from seed_data import seed, seed_networks, seed_video, seed_articles, seed_pet, seed_pet_articles, seed_travel, seed_travel_articles, seed_products_pet_travel, seed_hotels, seed_attractions
            seed()
            seed_networks()
            seed_video()
            seed_articles()
            seed_pet()
            seed_pet_articles()
            seed_travel()
            seed_travel_articles()
            seed_products_pet_travel()
            seed_hotels()
            seed_attractions()
            print('[OK] Database created & seeded')
        else:
            db.create_all()
    app.run(host='0.0.0.0', port=7000, debug=True)
