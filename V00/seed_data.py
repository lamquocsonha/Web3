from models import db, Vertical, Segment, Zone, Part, AffiliateLink, Voucher

def seed():
    """Seed Car vertical data - skip if already exists"""
    # Check if Car already exists
    car_vertical = Vertical.query.filter_by(slug='car').first()
    if car_vertical:
        print('[SKIP] Car vertical already exists')
        return

    print('[+] Seeding Car vertical...')
    # Vertical: Car
    car = Vertical(
        name='Car', slug='car', icon='🚗', color='#f39c12',
        description='Kiến thức chi tiết về ô tô — từ tổng thể đến từng bu-lông. Tìm hiểu, sửa chữa, nâng cấp.',
        status='live', style='car', template='general', default_mode='light'
    )
    db.session.add(car)
    db.session.flush()

    # Segments
    segments_data = [
        ('Sedan', 'sedan', '🚗', 'Xe sedan 4 cửa — Camry, Civic, Mazda 3...'),
        ('CUV', 'cuv', '🚙', 'Crossover đô thị — X-Trail, CR-V, CX-5, Tucson...'),
        ('SUV', 'suv', '🏔️', 'SUV 7 chỗ — Fortuner, Everest, Pajero Sport...'),
        ('Hatchback', 'hatchback', '🚘', 'Xe cỡ nhỏ — i10, Yaris, Mazda 2 Sport...'),
        ('MPV', 'mpv', '🚐', 'Xe đa dụng — Xpander, Veloz, Carnival...'),
        ('Pickup', 'pickup', '🛻', 'Xe bán tải — Ranger, Hilux, Triton, Navara...'),
    ]
    segments = {}
    for i, (name, slug, icon, desc) in enumerate(segments_data):
        s = Segment(vertical_id=car.id, name=name, slug=slug, icon=icon, description=desc, order=i)
        db.session.add(s)
        db.session.flush()
        segments[slug] = s

    # Zones cho CUV
    cuv = segments['cuv']
    zones_data = [
        ('Hệ thống treo', 'he-thong-treo', '🔩', '#fdcb6e', 'Phuộc, lò xo, cao su, rotuyn, thanh cân bằng — giữ xe êm ái trên mọi cung đường.'),
        ('Hệ thống phanh', 'he-thong-phanh', '🛑', '#ff7675', 'Má phanh, đĩa phanh, bầu trợ lực, ABS — an toàn là trên hết.'),
        ('Động cơ', 'dong-co', '⚙️', '#74b9ff', 'Block máy, bugi, kim phun, turbo — trái tim của chiếc xe.'),
        ('Hệ thống điện', 'he-thong-dien', '⚡', '#a29bfe', 'Ắc quy, máy phát, dây điện, cầu chì — hệ thần kinh của xe.'),
        ('Hệ thống lái', 'he-thong-lai', '🎯', '#00cec9', 'Thước lái, rô-tuyn lái, bơm trợ lực — điều khiển chính xác.'),
        ('Gầm xe', 'gam-xe', '🔧', '#fab1a0', 'Khung gầm, giảm chấn, chắn bùn, che gầm — bảo vệ phía dưới.'),
        ('Nội thất', 'noi-that', '💺', '#fd79a8', 'Ghế, taplo, vô-lăng, điều hòa — không gian bên trong.'),
        ('Ngoại thất', 'ngoai-that', '🪟', '#55efc4', 'Đèn, gương, cản, mâm — vẻ ngoài chiếc xe.'),
    ]
    zones = {}
    for i, (name, slug, icon, color, desc) in enumerate(zones_data):
        z = Zone(segment_id=cuv.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
        db.session.add(z)
        db.session.flush()
        zones[slug] = z

    # Parts cho Hệ thống treo
    ht_treo = zones['he-thong-treo']
    parts_treo = [
        {
            'name_vi': 'Cao su chân phuộc', 'name_en': 'Shock Absorber Bushing',
            'slug': 'cao-su-chan-phuoc',
            'description': 'Cao su giảm chấn gắn giữa phuộc nhún và thân xe, giúp hấp thụ rung động và giảm tiếng ồn từ mặt đường.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'oem_code': '54320-JD00A (Nissan), 51920-SWA-A01 (Honda)',
            'tags': 'cao su phuộc,giảm chấn,hệ thống treo,CUV,tiếng kêu lọc cọc,thay phụ tùng,DIY',
            'auto_category': 'phu-tung',
            'embed_code': '''<div class="at-carousel" data-network="accesstrade" data-campaign="shopee-auto" data-keyword="cao su chân phuộc ô tô" data-limit="6"></div>
<div class="at-carousel" data-network="accesstrade" data-campaign="lazada-auto" data-keyword="shock absorber bushing" data-limit="4"></div>''',
        },
        {
            'name_vi': 'Phuộc nhún', 'name_en': 'Shock Absorber',
            'slug': 'phuoc-nhun',
            'description': 'Bộ phận giảm chấn chính, hấp thụ dao động từ lò xo để xe đi êm ái và ổn định.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'oem_code': 'E4302-JD02A (Nissan), 51605-SWA-A04 (Honda)',
        },
        {
            'name_vi': 'Rotuyn', 'name_en': 'Ball Joint',
            'slug': 'rotuy',
            'description': 'Khớp cầu nối giữa đòn treo và trục xoay bánh xe, cho phép bánh xe xoay và di chuyển lên xuống.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'oem_code': '40160-JD00A (Nissan), 51220-SWA-A01 (Honda)',
        },
        {
            'name_vi': 'Thanh cân bằng', 'name_en': 'Stabilizer Bar',
            'slug': 'thanh-can-bang',
            'description': 'Thanh thép kết nối hai bên hệ thống treo, giúp giảm nghiêng thân xe khi vào cua.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'oem_code': '54668-JD000 (Nissan), 51306-SWA-A01 (Honda)',
        },
        {
            'name_vi': 'Lò xo giảm chấn', 'name_en': 'Coil Spring',
            'slug': 'lo-xo-giam-chan',
            'description': 'Lò xo xoắn bao quanh phuộc nhún, chịu trọng lượng xe và hấp thụ sốc ban đầu từ mặt đường.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'oem_code': '54010-JD02A (Nissan), 51401-SWA-A02 (Honda)',
        },
    ]

    for i, p_data in enumerate(parts_treo):
        p = Part(
            zone_id=ht_treo.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], oem_code=p_data.get('oem_code', ''),
            tags=p_data.get('tags', ''), auto_category=p_data.get('auto_category', ''),
            embed_code=p_data.get('embed_code', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

        # Sample affiliate links
        links = [
            ('shopee', f'{p_data["name_vi"]} chính hãng', 'https://shopee.vn/search?keyword=' + p_data['slug'], 150000 + i*50000),
            ('lazada', f'{p_data["name_vi"]} OEM', 'https://lazada.vn/search?q=' + p_data['slug'], 180000 + i*40000),
            ('tiki', f'{p_data["name_vi"]} cao cấp', 'https://tiki.vn/search?q=' + p_data['slug'], 200000 + i*30000),
        ]
        for net, pname, url, price in links:
            al = AffiliateLink(part_id=p.id, network=net, product_name=pname, url=url, price=price,
                image_url=f"https://placehold.co/400x300/f39c12/fff?text={p_data['slug'][:25]}")
            db.session.add(al)

    # Parts cho Hệ thống phanh
    ht_phanh = zones['he-thong-phanh']
    parts_phanh = [
        {
            'name_vi': 'Má phanh', 'name_en': 'Brake Pad',
            'slug': 'ma-phanh',
            'description': 'Miếng vật liệu ma sát ép vào đĩa phanh để giảm tốc và dừng xe.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'oem_code': 'D1060-JD00A (Nissan), 45022-SWA-A01 (Honda)',
        },
        {
            'name_vi': 'Đĩa phanh', 'name_en': 'Brake Disc',
            'slug': 'dia-phanh',
            'description': 'Đĩa kim loại gắn cùng bánh xe, bề mặt tiếp xúc với má phanh để tạo lực hãm.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'oem_code': '40206-JD00A (Nissan), 45251-SWA-A00 (Honda)',
        },
    ]

    for i, p_data in enumerate(parts_phanh):
        p = Part(
            zone_id=ht_phanh.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], oem_code=p_data.get('oem_code', ''),
            tags=p_data.get('tags', ''), auto_category=p_data.get('auto_category', ''),
            embed_code=p_data.get('embed_code', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()
        for net, price in [('shopee', 250000), ('lazada', 280000), ('tiki', 300000)]:
            al = AffiliateLink(part_id=p.id, network=net, product_name=f'{p_data["name_vi"]} chính hãng',
                             url=f'https://{net}.vn/search?q={p_data["slug"]}', price=price + i*100000,
                             image_url=f"https://placehold.co/400x300/f39c12/fff?text={p_data['slug'][:25]}")
            db.session.add(al)

    # Zones cho các segment khác (chỉ tạo zones, chưa có parts)
    for seg_slug in ['sedan', 'suv', 'hatchback', 'mpv', 'pickup']:
        seg = segments[seg_slug]
        for i, (name, slug, icon, color, desc) in enumerate(zones_data):
            z = Zone(segment_id=seg.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
            db.session.add(z)

    db.session.commit()
    print('✅ Seed data created successfully!')

def seed_networks():
    """Seed affiliate networks - skip if already exists"""
    from models import db, AffiliateNetwork, AffiliateCampaign, AffiliateStats, SiteSettings
    from datetime import date, timedelta
    import random

    # Check if networks already exist
    if AffiliateNetwork.query.first():
        print('[SKIP] Affiliate networks already exist')
        return

    print('[+] Seeding affiliate networks...')
    networks_data = [
        ('AccessTrade', 'accesstrade', '#e74c3c', '', '3-15%', 30, '~45 ngay', 'https://api.accesstrade.vn'),
        ('Shopee', 'shopee', '#ee4d2d', '', '2-10%', 7, '~30 ngay', 'https://affiliate.shopee.vn/api'),
        ('Lazada', 'lazada', '#f39c12', '', '3-12%', 7, '~30 ngay', 'https://affiliate.lazada.vn/api'),
        ('Tiki', 'tiki', '#1a94ff', '', '2-8%', 14, '~30 ngay', 'https://affiliate.tiki.vn/api'),
    ]
    for name, slug, color, icon, rate, cookie, cycle, api_url in networks_data:
        n = AffiliateNetwork(name=name, slug=slug, color=color, icon=icon,
            commission_rate=rate, cookie_days=cookie, payment_cycle=cycle, api_url=api_url)
        db.session.add(n)
        db.session.flush()

        # Sample campaigns
        for i, camp_name in enumerate([f'{name} - Electronics', f'{name} - Auto Parts', f'{name} - General']):
            c = AffiliateCampaign(network_id=n.id, name=camp_name,
                campaign_id_ext=f'CAMP-{slug.upper()}-{i+1:03d}',
                commission=rate, status='active', category='general')
            db.session.add(c)

    # Sample stats (30 days)
    for i in range(30):
        d = date.today() - timedelta(days=i)
        for net in ['accesstrade','shopee','lazada','tiki']:
            st = AffiliateStats(network=net, date=d,
                clicks=random.randint(50,500), conversions=random.randint(2,30),
                revenue=random.randint(500000,5000000), commission=random.randint(50000,500000))
            db.session.add(st)

    # Default settings
    for key, val, cat in [
        ('site_name','Unilab','general'), ('default_mode','minimal','general'),
        ('openai_key','','api'), ('claude_key','','api'),
        ('dalle_key','','api'), ('deepl_key','','api'),
    ]:
        SiteSettings.set_val(key, val, cat)

    db.session.commit()
    print('[OK] Networks & stats seeded!')

def seed_video():
    """Seed video/social data - skip if already exists"""
    from models import db, Vertical, SocialChannel, VideoProject, VideoPublish
    import random
    from datetime import datetime

    car = Vertical.query.filter_by(slug='car').first()
    if not car:
        return

    # Check if video data already exists
    if SocialChannel.query.first() or VideoProject.query.first():
        print('[SKIP] Video/social data already exists')
        return

    print('[+] Seeding video/social data...')
    channels_data = [
        (car.id, 'tiktok', 'UniCar VN', 'https://tiktok.com/@unicar.vn', 12500),
        (car.id, 'youtube', 'UniCar Channel', 'https://youtube.com/@unicar', 8200),
        (car.id, 'facebook', 'UniCar Fanpage', 'https://facebook.com/unicar.vn', 35000),
    ]
    channels = []
    for vid, platform, name, url, followers in channels_data:
        ch = SocialChannel(vertical_id=vid, platform=platform, channel_name=name,
            channel_url=url, status='connected', followers=followers)
        db.session.add(ch)
        db.session.flush()
        channels.append(ch)

    videos_data = [
        ('Cao su chan phuoc - Khi nao can thay?', 'short', '60s', 'published',
         '[Hook] Ban co nghe tieng loc coc duoi gam xe?\n[Content] Cao su chan phuoc la bo phan...\n[CTA] Xem chi tiet tai car.unilab.vn',
         '#oto #phuocnhun #caosuphuoc #suachuaoto #diyphutung'),
        ('5 dau hieu phanh xe co van de', 'short', '30s', 'published',
         '[Hook] 5 dau hieu nguy hiem ban khong nen bo qua\n[Content] 1. Tieng rit khi phanh...\n[CTA] Link bio',
         '#phanh #maphanh #antoan #oto #unicar'),
        ('Huong dan thay rotuy tai nha', 'long', '10min', 'ready',
         '[Intro] Rotuy la gi va tai sao can thay dung han\n[Buoc 1] Chuan bi dung cu...\n[Ket] Tong chi phi va luu y',
         '#DIY #rotuy #suachuaoto #huongdan'),
        ('So sanh phuoc dau vs phuoc gas', 'short', '60s', 'draft',
         '[Hook] Phuoc dau hay phuoc gas - cai nao tot hon?\n[So sanh] Gia, do ben, hieu suat...',
         '#phuoc #sosanhoto #kiemthucoto'),
    ]
    for title, vtype, dur, status, script, tags in videos_data:
        vp = VideoProject(title=title, vertical_slug='car', video_type=vtype,
            duration=dur, script=script, hashtags=tags, status=status,
            ai_provider='openai', caption=f'Video tu dong tu car.unilab.vn - {title}')
        db.session.add(vp)
        db.session.flush()

        if status == 'published':
            for ch in channels:
                pub = VideoPublish(video_id=vp.id, channel_id=ch.id, platform=ch.platform,
                    status='published', post_url=f'{ch.channel_url}/video/{vp.id}',
                    views=random.randint(500,15000), likes=random.randint(30,800),
                    shares=random.randint(10,200), comments=random.randint(5,100),
                    click_throughs=random.randint(20,500))
                db.session.add(pub)

    db.session.commit()
    print('[OK] Video channels & projects seeded!')

def seed_articles():
    """Seed articles - skip if already exists"""
    from models import db, Article

    # Check if articles already exist
    if Article.query.filter_by(tier='nganh').first():
        print('[SKIP] Articles already exist')
        return

    print('[+] Seeding articles...')
    articles = [
        # === TIER 1: NGANH (Industry knowledge - macro) ===
        {
            'title': 'Thị trường phụ tùng ô tô Việt Nam 2025 — Xu hướng & Cơ hội',
            'slug': 'thi-truong-phu-tung-oto-viet-nam-2025',
            'tier': 'nganh',
            'category': 'thi-truong',
            'tags': 'thị trường,phụ tùng,Việt Nam,2025,xu hướng,aftermarket',
            'excerpt': 'Phân tích toàn cảnh thị trường phụ tùng ô tô Việt Nam: quy mô 3.5 tỷ USD, tăng trưởng 12%/năm, và cơ hội cho người tiêu dùng thông minh.',
            'reading_time': 8,
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
        {
            'title': 'OEM vs Aftermarket vs Fake — Cách phân biệt phụ tùng ô tô',
            'slug': 'oem-vs-aftermarket-vs-fake',
            'tier': 'nganh',
            'category': 'kien-thuc-chung',
            'tags': 'OEM,aftermarket,hàng giả,phân biệt,chất lượng,mã phụ tùng',
            'excerpt': 'Hướng dẫn phân biệt 3 loại phụ tùng trên thị trường: OEM chính hãng, aftermarket chất lượng, và hàng nhái/fake. Cách đọc mã OEM và kiểm tra xuất xứ.',
            'reading_time': 10,
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
        {
            'title': 'Top 10 lỗi ô tô thường gặp và cách xử lý tại chỗ',
            'slug': 'top-10-loi-oto-thuong-gap',
            'tier': 'nganh',
            'category': 'xu-ly-su-co',
            'tags': 'lỗi thường gặp,xử lý sự cố,roadside,khẩn cấp,mẹo xe',
            'excerpt': '10 sự cố ô tô phổ biến nhất và cách xử lý ngay tại chỗ: từ xe không nổ máy, đèn cảnh báo, đến nổ lốp giữa đường.',
            'reading_time': 12,
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },

        # === TIER 2: CHUNG (System-level knowledge) ===
        {
            'title': 'Hệ thống treo ô tô — Cấu tạo, phân loại và nguyên lý hoạt động',
            'slug': 'he-thong-treo-oto-cau-tao',
            'tier': 'chung',
            'category': 'he-thong-treo',
            'related_segment_slug': 'cuv',
            'related_zone_slug': 'he-thong-treo',
            'tags': 'hệ thống treo,suspension,MacPherson,double wishbone,torsion beam,phuộc nhún',
            'excerpt': 'Toàn tập về hệ thống treo: 4 loại phổ biến, ưu nhược điểm, và cách nhận biết hệ thống treo cần bảo dưỡng.',
            'reading_time': 10,
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },

        # === TIER 3: CHI-TIET (Detailed part knowledge) ===
        {
            'title': 'Cao su chân phuộc — Tất cả kiến thức bạn cần biết',
            'slug': 'cao-su-chan-phuoc-tat-ca-kien-thuc',
            'tier': 'chi-tiet',
            'category': 'he-thong-treo',
            'related_zone_slug': 'he-thong-treo',
            'tags': 'cao su phuộc,giảm chấn,hệ thống treo,thay thế,60000km,polyurethane',
            'excerpt': 'Hướng dẫn toàn tập về cao su chân phuộc: chức năng, tuổi thọ, dấu hiệu hỏng, cách tự kiểm tra, so sánh OEM vs aftermarket.',
            'reading_time': 12,
            'embed_code': '<div class="at-carousel" data-network="accesstrade" data-keyword="cao su chan phuoc oto" data-limit="6"></div>',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
    ]

    for a_data in articles:
        a = Article(
            vertical_slug='car',
            title=a_data['title'], slug=a_data['slug'],
            excerpt=a_data.get('excerpt',''), content=a_data.get('content',''),
            tier=a_data.get('tier','chung'), category=a_data.get('category',''),
            tags=a_data.get('tags',''),
            related_segment_slug=a_data.get('related_segment_slug',''),
            related_zone_slug=a_data.get('related_zone_slug',''),
            embed_code=a_data.get('embed_code',''),
            ai_generated=True, reading_time=a_data.get('reading_time',5),
            views=__import__('random').randint(50, 3000)
        )
        db.session.add(a)
    db.session.commit()
    print(f'[OK] {len(articles)} articles seeded!')


# =============================================
# PET VERTICAL
# =============================================
def seed_pet():
    """Seed Pet vertical - skip if already exists"""
    from models import db, Vertical, Segment, Zone, Part
    import random

    # Check if Pet vertical already exists
    if Vertical.query.filter_by(slug='pet').first():
        print('[SKIP] Pet vertical already exists')
        return

    print('[+] Seeding Pet vertical...')
    v = Vertical(name='Pet', slug='pet', description='Kiến thức chăm sóc thú cưng — chó, mèo, và thú nhỏ', icon='🐾', color='#e17055', status='active', style='pet', template='general', default_mode='light')
    db.session.add(v)
    db.session.flush()

    segments_data = [
        {'name':'Chó','slug':'cho','icon':'🐕','desc':'Tất cả về chó: giống, chăm sóc, dinh dưỡng, bệnh lý, huấn luyện'},
        {'name':'Mèo','slug':'meo','icon':'🐈','desc':'Kiến thức mèo: giống, chăm sóc, dinh dưỡng, hành vi, y tế'},
        {'name':'Thú nhỏ','slug':'thu-nho','icon':'🐹','desc':'Hamster, thỏ, chim cảnh, cá cảnh — hướng dẫn chăm sóc'},
    ]

    zones_map = {
        'cho': [
            {'name':'Dinh dưỡng','slug':'dinh-duong','icon':'🍖','color':'#e74c3c',
             'desc':'Thức ăn, chế độ ăn, dinh dưỡng cho chó theo từng giai đoạn',
             'parts':[
                 {'vi':'Thức ăn hạt (Dry Food)','en':'Dry Dog Food','slug':'thuc-an-hat',
                  'desc':'Thức ăn khô dạng hạt — phổ biến nhất, tiện lợi, bảo quản lâu',
                  'oem':'Royal Canin / Pedigree / Taste of the Wild',
                  'tags':'thức ăn hạt,dry food,kibble,Royal Canin,dinh dưỡng chó',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Thức ăn ướt (Wet Food)','en':'Wet Dog Food','slug':'thuc-an-uot',
                  'desc':'Pate, thức ăn đóng hộp — hàm lượng nước cao, phù hợp chó biếng ăn',
                  'tags':'thức ăn ướt,pate,wet food,đóng hộp',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Vitamin & Supplement','en':'Dog Supplements','slug':'vitamin-supplement',
                  'desc':'Bổ sung vitamin, khoáng chất, glucosamine, omega-3 cho chó',
                  'tags':'vitamin,supplement,glucosamine,omega-3,canxi,bổ sung',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
            {'name':'Y tế & Bệnh lý','slug':'y-te','icon':'💉','color':'#3498db',
             'desc':'Vaccine, tẩy giun, bệnh thường gặp, phòng ngừa',
             'parts':[
                 {'vi':'Vaccine cơ bản','en':'Core Vaccines','slug':'vaccine-co-ban',
                  'desc':'Lịch tiêm vaccine cho chó: 5in1, 7in1, dại — phòng bệnh nguy hiểm',
                  'tags':'vaccine,tiêm phòng,5in1,7in1,dại,puppy',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Tẩy giun định kỳ','en':'Deworming','slug':'tay-giun',
                  'desc':'Lịch tẩy giun, loại thuốc, dấu hiệu nhiễm giun ở chó',
                  'tags':'tẩy giun,giun sán,deworming,phòng ngừa',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Ve & Bọ chét','en':'Flea & Tick Prevention','slug':'ve-bo-chet',
                  'desc':'Phòng trị ve, bọ chét — nhỏ gáy, vòng cổ, xịt',
                  'tags':'ve,bọ chét,flea,tick,nhỏ gáy,Nexgard,Frontline',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
            {'name':'Huấn luyện','slug':'huan-luyen','icon':'🎯','color':'#2ecc71',
             'desc':'Huấn luyện cơ bản, ngồi, nằm, đi vệ sinh đúng chỗ, xã hội hóa',
             'parts':[
                 {'vi':'Đi vệ sinh đúng chỗ','en':'Potty Training','slug':'di-ve-sinh-dung-cho',
                  'desc':'Hướng dẫn dạy chó con đi vệ sinh đúng nơi quy định',
                  'tags':'vệ sinh,potty training,chó con,huấn luyện cơ bản',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Lệnh cơ bản (Ngồi, Nằm, Lại đây)','en':'Basic Commands','slug':'lenh-co-ban',
                  'desc':'Dạy chó 5 lệnh cơ bản: Sit, Down, Come, Stay, Heel',
                  'tags':'lệnh cơ bản,sit,down,come,huấn luyện,clicker',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
            {'name':'Đồ dùng & Phụ kiện','slug':'do-dung','icon':'🦴','color':'#f39c12',
             'desc':'Chuồng, dây dắt, bát ăn, đồ chơi, quần áo cho chó',
             'parts':[
                 {'vi':'Dây dắt & Vòng cổ','en':'Leash & Collar','slug':'day-dat-vong-co',
                  'desc':'Chọn dây dắt, vòng cổ, yếm (harness) phù hợp theo size và giống chó',
                  'tags':'dây dắt,vòng cổ,harness,yếm,dạo phố',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Chuồng & Nệm ngủ','en':'Crate & Bed','slug':'chuong-nem',
                  'desc':'Chọn chuồng, nệm, ổ ngủ phù hợp cho chó',
                  'tags':'chuồng,nệm,giường,crate,ngủ',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
        ],
        'meo': [
            {'name':'Dinh dưỡng','slug':'dinh-duong','icon':'🐟','color':'#9b59b6',
             'desc':'Thức ăn mèo, chế độ ăn, dinh dưỡng theo tuổi',
             'parts':[
                 {'vi':'Thức ăn hạt cho mèo','en':'Dry Cat Food','slug':'thuc-an-hat-meo',
                  'desc':'Chọn thức ăn hạt cho mèo: protein cao, ít carb, đủ taurine',
                  'tags':'thức ăn mèo,dry food,Royal Canin,Whiskas,taurine',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Pate & Thức ăn ướt','en':'Wet Cat Food','slug':'pate-meo',
                  'desc':'Pate mèo, thức ăn ướt — bổ sung nước, phòng bệnh thận',
                  'tags':'pate mèo,wet food,thận,bổ sung nước',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
            {'name':'Y tế','slug':'y-te','icon':'💊','color':'#e74c3c',
             'desc':'Vaccine, triệt sản, bệnh thường gặp ở mèo',
             'parts':[
                 {'vi':'Vaccine mèo','en':'Cat Vaccines','slug':'vaccine-meo',
                  'desc':'Lịch tiêm vaccine cho mèo: 3in1, 4in1, dại',
                  'tags':'vaccine mèo,3in1,4in1,dại,FPV,FCV',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Triệt sản','en':'Spay/Neuter','slug':'triet-san',
                  'desc':'Triệt sản mèo: lợi ích, thời điểm, chi phí, chăm sóc sau phẫu thuật',
                  'tags':'triệt sản,spay,neuter,phẫu thuật,6 tháng',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
            {'name':'Đồ dùng','slug':'do-dung','icon':'🧶','color':'#1abc9c',
             'desc':'Khay cát, cây mèo, đồ chơi, bát ăn',
             'parts':[
                 {'vi':'Khay cát & Cát vệ sinh','en':'Litter Box & Litter','slug':'khay-cat',
                  'desc':'Chọn khay cát, loại cát phù hợp, mẹo khử mùi',
                  'tags':'khay cát,cát vệ sinh,litter box,bentonite,tofu',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Cây leo & Trụ cào','en':'Cat Tree & Scratcher','slug':'cay-leo-tru-cao',
                  'desc':'Cây mèo, trụ cào móng — thỏa mãn bản năng, bảo vệ nội thất',
                  'tags':'cây mèo,trụ cào,cat tree,scratcher,nội thất',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
        ],
        'thu-nho': [
            {'name':'Hamster','slug':'hamster','icon':'🐹','color':'#f1c40f',
             'desc':'Chăm sóc hamster: chuồng, thức ăn, bệnh lý',
             'parts':[
                 {'vi':'Chuồng & Lót chuồng','en':'Hamster Cage','slug':'chuong-hamster',
                  'desc':'Chọn chuồng, lót chuồng, phụ kiện cho hamster',
                  'tags':'chuồng hamster,lót chuồng,mùn cưa,cage',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Thức ăn hamster','en':'Hamster Food','slug':'thuc-an-hamster',
                  'desc':'Thức ăn hỗn hợp, hạt, rau quả cho hamster',
                  'tags':'thức ăn hamster,hạt hướng dương,rau,trái cây',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
            {'name':'Cá cảnh','slug':'ca-canh','icon':'🐠','color':'#3498db',
             'desc':'Cá cảnh nước ngọt, nước mặn, hồ thủy sinh',
             'parts':[
                 {'vi':'Bể & Lọc nước','en':'Aquarium & Filter','slug':'be-loc-nuoc',
                  'desc':'Chọn bể, hệ thống lọc, ánh sáng cho hồ cá',
                  'tags':'bể cá,lọc nước,filter,aquarium,thủy sinh',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Thức ăn cá','en':'Fish Food','slug':'thuc-an-ca',
                  'desc':'Thức ăn viên, lá, đông lạnh cho các loại cá cảnh',
                  'tags':'thức ăn cá,pellet,flake,artemia,cá cảnh',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
        ],
    }

    for sd in segments_data:
        s = Segment(vertical_id=v.id, name=sd['name'], slug=sd['slug'], icon=sd['icon'], description=sd['desc'])
        db.session.add(s)
        db.session.flush()
        for zd in zones_map.get(sd['slug'],[]):
            z = Zone(segment_id=s.id, name=zd['name'], slug=zd['slug'], icon=zd['icon'], color=zd['color'], description=zd['desc'])
            db.session.add(z)
            db.session.flush()
            for i, pd in enumerate(zd.get('parts',[])):
                p = Part(zone_id=z.id, name_vi=pd['vi'], name_en=pd.get('en',''), slug=pd['slug'],
                    description=pd['desc'], content=pd.get('content',''), oem_code=pd.get('oem',''),
                    tags=pd.get('tags',''), auto_category='san-pham', order=i)
                db.session.add(p)
    db.session.commit()
    print('[OK] Pet vertical seeded!')


def seed_pet_articles():
    """Seed pet articles - skip if already exists"""
    from models import db, Article
    import random

    # Check if pet articles already exist
    if Article.query.filter_by(vertical_slug='pet').first():
        print('[SKIP] Pet articles already exist')
        return

    print('[+] Seeding pet articles...')
    articles = [
        # T1: NGANH
        {'title':'Thị trường thú cưng Việt Nam 2025 — Bùng nổ & Cơ hội','slug':'thi-truong-thu-cung-vn-2025','tier':'nganh','category':'thi-truong',
         'tags':'thị trường,thú cưng,Việt Nam,2025,pet economy',
         'excerpt':'Thị trường thú cưng VN đạt 1.2 tỷ USD, tăng 25%/năm. Phân tích xu hướng, cơ hội kinh doanh, và thói quen chi tiêu của pet parent Việt.',
         'reading_time':8,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Chọn giống chó phù hợp — Hướng dẫn cho người mới','slug':'chon-giong-cho-phu-hop','tier':'nganh','category':'chon-giong',
         'tags':'giống chó,chọn giống,người mới,apartment,gia đình',
         'excerpt':'Hướng dẫn chọn giống chó phù hợp với điều kiện sống: chung cư, nhà rộng, có trẻ nhỏ, người bận rộn.',
         'reading_time':10,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Chi phí nuôi chó/mèo 1 năm — Tính sao cho đúng?','slug':'chi-phi-nuoi-cho-meo-1-nam','tier':'nganh','category':'chi-phi',
         'tags':'chi phí,nuôi chó,nuôi mèo,budget,1 năm',
         'excerpt':'Bảng tính chi phí nuôi chó/mèo chi tiết: thức ăn, vaccine, y tế, đồ dùng, làm đẹp — từ tiết kiệm đến premium.',
         'reading_time':7,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},

        # T2: CHUNG
        {'title':'Dinh dưỡng chó theo từng giai đoạn — Puppy, Adult, Senior','slug':'dinh-duong-cho-theo-giai-doan','tier':'chung','category':'dinh-duong',
         'related_segment_slug':'cho','related_zone_slug':'dinh-duong',
         'tags':'dinh dưỡng,puppy,adult,senior,protein,chất béo',
         'excerpt':'Nhu cầu dinh dưỡng chó thay đổi theo tuổi. Hướng dẫn chọn thức ăn đúng cho từng giai đoạn.',
         'reading_time':9,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Hành vi mèo — Giải mã ngôn ngữ cơ thể','slug':'hanh-vi-meo-giai-ma','tier':'chung','category':'hanh-vi',
         'related_segment_slug':'meo',
         'tags':'hành vi mèo,ngôn ngữ cơ thể,đuôi mèo,rên gừ,cắn',
         'excerpt':'Mèo giao tiếp bằng đuôi, tai, mắt, và âm thanh. Hiểu ngôn ngữ mèo để chăm sóc tốt hơn.',
         'reading_time':8,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'5 bệnh thường gặp ở chó và dấu hiệu nhận biết','slug':'5-benh-thuong-gap-o-cho','tier':'chung','category':'y-te',
         'related_segment_slug':'cho','related_zone_slug':'y-te',
         'tags':'bệnh chó,Parvo,Care,viêm ruột,nấm da',
         'excerpt':'5 bệnh nguy hiểm nhất ở chó: Parvo, Care, viêm ruột, nấm da, viêm tai — dấu hiệu và cách phòng.',
         'reading_time':10,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Cách tắm chó mèo đúng cách tại nhà','slug':'cach-tam-cho-meo-dung-cach','tier':'chung','category':'cham-soc',
         'tags':'tắm chó,tắm mèo,grooming,sữa tắm,lông',
         'excerpt':'Hướng dẫn tắm chó mèo tại nhà: tần suất, nhiệt độ nước, sữa tắm, sấy khô — tránh sai lầm gây bệnh da.',
         'reading_time':6,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},

        # T3: CHI TIET
        {'title':'Royal Canin vs Taste of the Wild — So sánh chi tiết','slug':'royal-canin-vs-taste-of-the-wild','tier':'chi-tiet','category':'dinh-duong',
         'related_zone_slug':'dinh-duong',
         'tags':'Royal Canin,Taste of the Wild,so sánh,thức ăn hạt,review',
         'excerpt':'So sánh 2 thương hiệu thức ăn chó nổi tiếng: thành phần, giá, ưu nhược điểm. Nên chọn loại nào?',
         'reading_time':7,
         'embed_code':'<div class="at-carousel" data-network="shopee" data-keyword="royal canin dog food" data-limit="6"></div>',
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Hướng dẫn chọn cát vệ sinh cho mèo — Bentonite vs Tofu vs Crystal','slug':'chon-cat-ve-sinh-meo','tier':'chi-tiet','category':'do-dung',
         'related_segment_slug':'meo','related_zone_slug':'do-dung',
         'tags':'cát vệ sinh,bentonite,tofu,crystal,khay cát,mèo',
         'excerpt':'So sánh 3 loại cát mèo phổ biến: bentonite, tofu, crystal. Ưu nhược điểm và chi phí hàng tháng.',
         'reading_time':6,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
    ]

    for ad in articles:
        img = ad.get('image_url', f"https://placehold.co/800x450/e17055/fff?text={ad['slug'][:30]}")
        a = Article(vertical_slug='pet', title=ad['title'], slug=ad['slug'], excerpt=ad.get('excerpt',''),
            content=ad.get('content',''), tier=ad.get('tier','chung'), category=ad.get('category',''),
            tags=ad.get('tags',''), related_segment_slug=ad.get('related_segment_slug',''),
            related_zone_slug=ad.get('related_zone_slug',''), embed_code=ad.get('embed_code',''),
            ai_generated=True, reading_time=ad.get('reading_time',5), views=random.randint(80,5000),
            image_url=img)
        db.session.add(a)
    db.session.commit()
    print(f'[OK] {len(articles)} pet articles seeded!')


def seed_pet_v2():
    """Expand Pet vertical with more zones, parts, articles, products.
    Safe to run multiple times — skips existing slugs."""
    from models import db, Vertical, Segment, Zone, Part, AffiliateLink, Article
    import random

    pet = Vertical.query.filter_by(slug='pet').first()
    if not pet:
        print('[SKIP] Pet vertical not found — run seed_pet() first')
        return

    print('[+] Expanding Pet content (v2)...')
    added_parts = 0
    added_articles = 0
    added_products = 0

    # ── Helper: get or create zone under a segment ──
    def get_or_create_zone(segment, zd):
        z = Zone.query.filter_by(segment_id=segment.id, slug=zd['slug']).first()
        if not z:
            z = Zone(segment_id=segment.id, name=zd['name'], slug=zd['slug'],
                     icon=zd['icon'], color=zd['color'], description=zd['desc'])
            db.session.add(z)
            db.session.flush()
        return z

    def add_part_if_new(zone, pd, order=0):
        nonlocal added_parts
        existing = Part.query.filter_by(zone_id=zone.id, slug=pd['slug']).first()
        if existing:
            return existing
        p = Part(zone_id=zone.id, name_vi=pd['vi'], name_en=pd.get('en',''), slug=pd['slug'],
                 description=pd['desc'], content=pd.get('content',''), oem_code=pd.get('oem',''),
                 tags=pd.get('tags',''), auto_category='san-pham', order=order)
        db.session.add(p)
        db.session.flush()
        added_parts += 1
        return p

    # ── Build segment lookup ──
    seg_map = {s.slug: s for s in pet.segments}

    # ================================================================
    # SEGMENT: CHÓ — thêm parts mới
    # ================================================================
    cho = seg_map.get('cho')
    if cho:
        # ── Zone: Dinh dưỡng — thêm parts ──
        z_dd = Zone.query.filter_by(segment_id=cho.id, slug='dinh-duong').first()
        if z_dd:
            new_parts_dd = [
                {'vi':'Thức ăn theo giống','en':'Breed-Specific Food','slug':'thuc-an-theo-giong',
                 'desc':'Thức ăn chuyên biệt cho từng giống: Poodle, Golden, Corgi, Husky, Phốc sóc',
                 'tags':'thức ăn theo giống,breed,poodle,golden,corgi,husky,phoc soc',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Snack & Treat thưởng','en':'Dog Treats','slug':'snack-treat-cho',
                 'desc':'Bánh thưởng, snack huấn luyện, xương gặm, thịt sấy cho chó',
                 'tags':'snack,treat,bánh thưởng,xương gặm,thịt sấy,jerky,dental stick',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Thức ăn chó con (Puppy)','en':'Puppy Food','slug':'thuc-an-cho-con',
                 'desc':'Thức ăn chuyên dụng cho chó con 2 tháng - 12 tháng tuổi',
                 'tags':'puppy,chó con,sữa chó,weaning,bổ sung canxi',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            ]
            for i, pd in enumerate(new_parts_dd):
                add_part_if_new(z_dd, pd, order=10+i)

        # ── Zone: Y tế — thêm parts ──
        z_yt = Zone.query.filter_by(segment_id=cho.id, slug='y-te').first()
        if z_yt:
            new_parts_yt = [
                {'vi':'Nấm da & Viêm da','en':'Skin Disease','slug':'nam-da-viem-da',
                 'desc':'Bệnh da liễu phổ biến ở chó: nấm, ghẻ, viêm da dị ứng, rụng lông',
                 'tags':'nấm da,viêm da,ghẻ,rụng lông,dị ứng,ngứa,dermatitis',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Bệnh đường ruột','en':'Digestive Issues','slug':'benh-duong-ruot',
                 'desc':'Tiêu chảy, nôn mửa, viêm dạ dày ruột ở chó — nguyên nhân và xử lý',
                 'tags':'tiêu chảy,nôn,viêm ruột,đường ruột,probiotic',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Chăm sóc răng miệng','en':'Dental Care','slug':'cham-soc-rang',
                 'desc':'Đánh răng, cao răng, viêm nướu ở chó — phòng ngừa và điều trị',
                 'tags':'răng miệng,đánh răng,cao răng,viêm nướu,dental,oral care',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            ]
            for i, pd in enumerate(new_parts_yt):
                add_part_if_new(z_yt, pd, order=10+i)

        # ── Zone: Huấn luyện — thêm parts ──
        z_hl = Zone.query.filter_by(segment_id=cho.id, slug='huan-luyen').first()
        if z_hl:
            new_parts_hl = [
                {'vi':'Xã hội hóa chó con','en':'Puppy Socialization','slug':'xa-hoi-hoa',
                 'desc':'Kỹ năng xã hội hóa chó con 3-14 tuần tuổi — giai đoạn vàng',
                 'tags':'xã hội hóa,socialization,chó con,puppy,giai đoạn vàng',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Chống sủa vô cớ','en':'Stop Excessive Barking','slug':'chong-sua-vo-co',
                 'desc':'Nguyên nhân và cách huấn luyện chó giảm sủa, phù hợp chung cư',
                 'tags':'sủa,barking,chung cư,tiếng ồn,huấn luyện',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Đi dạo & Kéo dây','en':'Leash Training','slug':'di-dao-keo-day',
                 'desc':'Dạy chó đi dạo đúng cách, không kéo dây dắt — loose leash walking',
                 'tags':'đi dạo,kéo dây,leash walking,dây dắt,dạo phố',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            ]
            for i, pd in enumerate(new_parts_hl):
                add_part_if_new(z_hl, pd, order=10+i)

        # ── Zone: Đồ dùng — thêm parts ──
        z_dd2 = Zone.query.filter_by(segment_id=cho.id, slug='do-dung').first()
        if z_dd2:
            new_parts_dd2 = [
                {'vi':'Đồ chơi cho chó','en':'Dog Toys','slug':'do-choi-cho',
                 'desc':'Đồ chơi gặm, bóng, kéo co, đồ chơi trí tuệ (puzzle) cho chó',
                 'tags':'đồ chơi,bóng,kéo co,puzzle,Kong,gặm,nhai',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Quần áo & Phụ kiện','en':'Dog Clothes','slug':'quan-ao-phu-kien',
                 'desc':'Quần áo, áo mưa, giày, kính cho chó — thời trang và bảo vệ',
                 'tags':'quần áo chó,áo mưa,giày chó,thời trang pet,mùa đông',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Bát ăn & Bình nước','en':'Food & Water Bowl','slug':'bat-an-binh-nuoc',
                 'desc':'Chọn bát ăn, bình nước tự động, đế chống lật cho chó',
                 'tags':'bát ăn,bình nước,tự động,chống lật,inox,ceramic',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            ]
            for i, pd in enumerate(new_parts_dd2):
                add_part_if_new(z_dd2, pd, order=10+i)

        # ── Zone MỚI: Làm đẹp & Grooming ──
        z_grooming = get_or_create_zone(cho, {
            'name':'Làm đẹp & Grooming','slug':'lam-dep','icon':'✂️','color':'#e84393',
            'desc':'Tắm, cắt lông, chăm sóc móng, tai, mắt cho chó'})
        grooming_parts = [
            {'vi':'Sữa tắm & Dầu xả','en':'Dog Shampoo','slug':'sua-tam-cho',
             'desc':'Sữa tắm chuyên dụng cho chó: chống ngứa, dưỡng lông, khử mùi',
             'tags':'sữa tắm,dầu gội,shampoo,dưỡng lông,khử mùi,chống ngứa',
             'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            {'vi':'Cắt lông & Tạo kiểu','en':'Dog Grooming','slug':'cat-long-tao-kieu',
             'desc':'Cắt lông, tạo kiểu cho chó: tại nhà và spa chuyên nghiệp',
             'tags':'cắt lông,grooming,tỉa lông,spa chó,tông đơ,kéo cắt',
             'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            {'vi':'Cắt móng & Vệ sinh tai','en':'Nail & Ear Care','slug':'cat-mong-ve-sinh-tai',
             'desc':'Cắt móng đúng cách, vệ sinh tai, mắt cho chó tại nhà',
             'tags':'cắt móng,vệ sinh tai,viêm tai,tai chó,mắt chó',
             'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        ]
        for i, pd in enumerate(grooming_parts):
            add_part_if_new(z_grooming, pd, order=i)

    # ================================================================
    # SEGMENT: MÈO — thêm zones và parts
    # ================================================================
    meo = seg_map.get('meo')
    if meo:
        # ── Zone: Dinh dưỡng — thêm parts ──
        z_dd_meo = Zone.query.filter_by(segment_id=meo.id, slug='dinh-duong').first()
        if z_dd_meo:
            new_parts_meo_dd = [
                {'vi':'Snack & Treat mèo','en':'Cat Treats','slug':'snack-treat-meo',
                 'desc':'Bánh thưởng, snack lỏng (Ciao Churu), thịt sấy cho mèo',
                 'tags':'snack mèo,treat,Ciao Churu,thưởng mèo,súp thưởng,inaba',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Thức ăn mèo con (Kitten)','en':'Kitten Food','slug':'thuc-an-meo-con',
                 'desc':'Thức ăn chuyên dụng cho mèo con 1-12 tháng, sữa thay thế',
                 'tags':'kitten,mèo con,sữa mèo,cai sữa,Royal Canin Kitten',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            ]
            for i, pd in enumerate(new_parts_meo_dd):
                add_part_if_new(z_dd_meo, pd, order=10+i)

        # ── Zone: Y tế — thêm parts ──
        z_yt_meo = Zone.query.filter_by(segment_id=meo.id, slug='y-te').first()
        if z_yt_meo:
            new_parts_meo_yt = [
                {'vi':'Bệnh thận & Tiết niệu','en':'Kidney & Urinary','slug':'benh-than-tiet-nieu',
                 'desc':'Bệnh thận mãn, sỏi bàng quang, viêm đường tiết niệu ở mèo',
                 'tags':'bệnh thận,thận mãn,sỏi,tiết niệu,FLUTD,CKD,uống nước',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Nấm da mèo','en':'Cat Ringworm','slug':'nam-da-meo',
                 'desc':'Nấm da (ringworm) ở mèo: triệu chứng, điều trị, phòng lây sang người',
                 'tags':'nấm da mèo,ringworm,rụng lông,lây người,antifungal',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Tẩy giun & Ve mèo','en':'Cat Deworming','slug':'tay-giun-ve-meo',
                 'desc':'Lịch tẩy giun, phòng ve bọ chét cho mèo trong nhà và ngoài trời',
                 'tags':'tẩy giun mèo,ve mèo,bọ chét,Broadline,Revolution,nhỏ gáy',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            ]
            for i, pd in enumerate(new_parts_meo_yt):
                add_part_if_new(z_yt_meo, pd, order=10+i)

        # ── Zone MỚI: Hành vi mèo ──
        z_hv = get_or_create_zone(meo, {
            'name':'Hành vi','slug':'hanh-vi','icon':'🧠','color':'#6c5ce7',
            'desc':'Hiểu tâm lý, hành vi mèo: cào, cắn, rên gừ, dấu hiệu stress'})
        hanh_vi_parts = [
            {'vi':'Mèo cào đồ — Xử lý đúng','en':'Cat Scratching','slug':'meo-cao-do',
             'desc':'Tại sao mèo cào, cách bảo vệ nội thất và hướng mèo cào đúng chỗ',
             'tags':'cào đồ,cào sofa,trụ cào,scratcher,hành vi mèo',
             'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            {'vi':'Mèo đi vệ sinh ngoài khay','en':'Litter Box Problems','slug':'di-ve-sinh-ngoai-khay',
             'desc':'Nguyên nhân và cách xử lý khi mèo bỏ khay, tiểu bậy',
             'tags':'tiểu bậy,bỏ khay,litter box,vệ sinh,stress mèo',
             'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            {'vi':'Stress & Lo âu ở mèo','en':'Cat Stress & Anxiety','slug':'stress-meo',
             'desc':'Dấu hiệu stress, nguyên nhân, cách giảm stress cho mèo',
             'tags':'stress mèo,lo âu,Feliway,giấu mình,bỏ ăn,liếm lông',
             'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        ]
        for i, pd in enumerate(hanh_vi_parts):
            add_part_if_new(z_hv, pd, order=i)

        # ── Zone: Đồ dùng — thêm parts ──
        z_dd_meo = Zone.query.filter_by(segment_id=meo.id, slug='do-dung').first()
        if z_dd_meo:
            new_parts_meo_dd = [
                {'vi':'Đồ chơi mèo','en':'Cat Toys','slug':'do-choi-meo',
                 'desc':'Cần câu, bóng, chuột giả, đồ chơi tương tác, catnip',
                 'tags':'đồ chơi mèo,cần câu,chuột giả,catnip,laser,tương tác',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Balo & Túi vận chuyển mèo','en':'Cat Carrier','slug':'balo-tui-van-chuyen',
                 'desc':'Balo mèo, túi vận chuyển, chuồng vận chuyển — đi bác sĩ, đi chơi',
                 'tags':'balo mèo,túi vận chuyển,carrier,đi máy bay,đi bác sĩ',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Bát ăn & Vòi nước mèo','en':'Cat Bowl & Fountain','slug':'bat-an-voi-nuoc-meo',
                 'desc':'Bát ăn nghiêng, vòi nước (pet fountain) khuyến khích mèo uống nước',
                 'tags':'bát ăn mèo,pet fountain,vòi nước,uống nước,phòng thận',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            ]
            for i, pd in enumerate(new_parts_meo_dd):
                add_part_if_new(z_dd_meo, pd, order=10+i)

        # ── Zone MỚI: Làm đẹp mèo ──
        z_groom_meo = get_or_create_zone(meo, {
            'name':'Làm đẹp','slug':'lam-dep','icon':'✨','color':'#fd79a8',
            'desc':'Tắm, chải lông, cắt móng, vệ sinh tai mắt cho mèo'})
        groom_meo_parts = [
            {'vi':'Chải lông & Chống rụng','en':'Cat Brushing','slug':'chai-long-meo',
             'desc':'Chải lông mèo đúng cách, giảm rụng lông, phòng búi lông (hairball)',
             'tags':'chải lông,rụng lông,hairball,búi lông,Furminator,lông mèo',
             'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            {'vi':'Sữa tắm mèo','en':'Cat Shampoo','slug':'sua-tam-meo',
             'desc':'Sữa tắm cho mèo: khi nào cần tắm, sản phẩm an toàn, tắm khô',
             'tags':'sữa tắm mèo,tắm mèo,tắm khô,shampoo cat,grooming',
             'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        ]
        for i, pd in enumerate(groom_meo_parts):
            add_part_if_new(z_groom_meo, pd, order=i)

    # ================================================================
    # SEGMENT: THÚ NHỎ — thêm zones mới
    # ================================================================
    thu_nho = seg_map.get('thu-nho')
    if thu_nho:
        # ── Zone MỚI: Thỏ ──
        z_tho = get_or_create_zone(thu_nho, {
            'name':'Thỏ','slug':'tho','icon':'🐰','color':'#e17055',
            'desc':'Chăm sóc thỏ cảnh: chuồng, thức ăn, bệnh lý, hành vi'})
        tho_parts = [
            {'vi':'Chuồng & Lót chuồng thỏ','en':'Rabbit Housing','slug':'chuong-tho',
             'desc':'Chọn chuồng, lót chuồng an toàn cho thỏ — kích thước, vật liệu',
             'tags':'chuồng thỏ,lót chuồng,cỏ khô,hay,rabbit cage,playpen',
             'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            {'vi':'Thức ăn thỏ','en':'Rabbit Diet','slug':'thuc-an-tho',
             'desc':'Chế độ ăn đúng cho thỏ: cỏ, rau, viên nén, trái cây',
             'tags':'thức ăn thỏ,cỏ Timothy,rau,hay,pellet,thỏ ăn gì',
             'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            {'vi':'Bệnh thường gặp ở thỏ','en':'Rabbit Health','slug':'benh-tho',
             'desc':'GI Stasis, quá nóng, bệnh răng, lông bết — nhận biết và phòng tránh',
             'tags':'bệnh thỏ,GI Stasis,tắc ruột,quá nóng,răng thỏ,bác sĩ thú y',
             'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        ]
        for i, pd in enumerate(tho_parts):
            add_part_if_new(z_tho, pd, order=i)

        # ── Zone MỚI: Chim cảnh ──
        z_chim = get_or_create_zone(thu_nho, {
            'name':'Chim cảnh','slug':'chim-canh','icon':'🦜','color':'#00b894',
            'desc':'Chăm sóc chim cảnh: vẹt, yến phụng, chào mào, chích chòe'})
        chim_parts = [
            {'vi':'Lồng & Phụ kiện chim','en':'Bird Cage','slug':'long-chim',
             'desc':'Chọn lồng, cầu đậu, đồ chơi, bát ăn cho chim cảnh',
             'tags':'lồng chim,cầu đậu,bird cage,phụ kiện chim,vẹt',
             'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            {'vi':'Thức ăn chim cảnh','en':'Bird Food','slug':'thuc-an-chim',
             'desc':'Hạt, trái cây, rau, thức ăn viên cho các loại chim cảnh',
             'tags':'thức ăn chim,hạt kê,hạt hướng dương,pellet bird,rau quả chim',
             'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        ]
        for i, pd in enumerate(chim_parts):
            add_part_if_new(z_chim, pd, order=i)

        # ── Zone: Hamster — thêm parts ──
        z_hamster = Zone.query.filter_by(segment_id=thu_nho.id, slug='hamster').first()
        if z_hamster:
            new_hamster = [
                {'vi':'Bệnh thường gặp ở hamster','en':'Hamster Health','slug':'benh-hamster',
                 'desc':'Wet tail, cảm lạnh, u bướu, bệnh da — nhận biết và phòng tránh',
                 'tags':'bệnh hamster,wet tail,u bướu,ướt đuôi,tiêu chảy',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Đồ chơi & Vận động hamster','en':'Hamster Toys','slug':'do-choi-hamster',
                 'desc':'Bánh xe chạy, đường ống, cầu, xích đu cho hamster',
                 'tags':'đồ chơi hamster,bánh xe,running wheel,ống chui,hamster ball',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            ]
            for i, pd in enumerate(new_hamster):
                add_part_if_new(z_hamster, pd, order=10+i)

        # ── Zone: Cá cảnh — thêm parts ──
        z_ca = Zone.query.filter_by(segment_id=thu_nho.id, slug='ca-canh').first()
        if z_ca:
            new_ca = [
                {'vi':'Cá Betta (cá xiêm)','en':'Betta Fish','slug':'ca-betta',
                 'desc':'Chăm sóc cá Betta: bể, nhiệt độ, thức ăn, bệnh thường gặp',
                 'tags':'cá Betta,cá xiêm,cá lia thia,betta fish,cá cảnh dễ nuôi',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                {'vi':'Hồ thủy sinh','en':'Aquascaping','slug':'ho-thuy-sinh',
                 'desc':'Setup hồ thủy sinh: cây, đá, nền, CO2, đèn — hướng dẫn cho người mới',
                 'tags':'thủy sinh,aquascape,cây thủy sinh,CO2,đá,nền thủy sinh',
                 'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
            ]
            for i, pd in enumerate(new_ca):
                add_part_if_new(z_ca, pd, order=10+i)

    # ================================================================
    # ARTICLES MỚI
    # ================================================================
    new_articles = [
        # T1: NGANH
        {'title':'Top 10 giống chó phù hợp chung cư Việt Nam 2025','slug':'top-10-giong-cho-chung-cu',
         'tier':'nganh','category':'chon-giong',
         'tags':'giống chó,chung cư,apartment,ít sủa,nhỏ gọn',
         'excerpt':'Chung cư hẹp, hàng xóm gần — giống chó nào phù hợp? Xếp hạng theo kích thước, mức sủa, năng lượng, và tính cách.',
         'reading_time':12,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Top 8 giống mèo được yêu thích nhất Việt Nam','slug':'top-giong-meo-yeu-thich-vn',
         'tier':'nganh','category':'chon-giong',
         'tags':'giống mèo,mèo Anh,mèo Ba Tư,mèo ta,Munchkin,Scottish Fold',
         'excerpt':'8 giống mèo phổ biến nhất VN: đặc điểm, giá mua, chi phí nuôi, và tính cách từng giống.',
         'reading_time':10,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},

        # T2: CHUNG
        {'title':'Hướng dẫn nhận nuôi chó mèo tại VN — Adopt Don\'t Shop','slug':'huong-dan-nhan-nuoi-adopt',
         'tier':'chung','category':'nhan-nuoi',
         'tags':'nhận nuôi,adopt,cứu hộ,trại chó,trại mèo,volunteer',
         'excerpt':'Quy trình nhận nuôi chó mèo từ trạm cứu hộ, điều kiện, chi phí, và danh sách trạm uy tín tại Việt Nam.',
         'reading_time':8,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Mèo ăn gì — Thực phẩm AN TOÀN và ĐỘC HẠI','slug':'meo-an-gi-an-toan-doc-hai',
         'tier':'chung','category':'dinh-duong',
         'related_segment_slug':'meo','related_zone_slug':'dinh-duong',
         'tags':'mèo ăn gì,thực phẩm độc,thực phẩm an toàn,hành,tỏi,sô-cô-la',
         'excerpt':'Danh sách đầy đủ thực phẩm mèo ăn được và KHÔNG được ăn. Một số thực phẩm tưởng an toàn nhưng cực kỳ nguy hiểm.',
         'reading_time':7,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Cách chăm sóc chó mèo mùa nóng — Phòng sốc nhiệt','slug':'cham-soc-mua-nong-soc-nhiet',
         'tier':'chung','category':'cham-soc',
         'tags':'mùa nóng,sốc nhiệt,heatstroke,quạt,điều hòa,nước',
         'excerpt':'Mùa hè VN nóng 35-40°C — chó mèo rất dễ sốc nhiệt. Hướng dẫn phòng ngừa và sơ cứu kịp thời.',
         'reading_time':6,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},

        # T3: CHI TIET
        {'title':'So sánh 5 loại cát vệ sinh mèo phổ biến nhất 2025','slug':'so-sanh-5-loai-cat-meo-2025',
         'tier':'chi-tiet','category':'do-dung',
         'related_segment_slug':'meo','related_zone_slug':'do-dung',
         'tags':'cát mèo,bentonite,tofu,crystal,đậu nành,so sánh',
         'excerpt':'So sánh chi tiết 5 loại cát mèo: Bentonite, Tofu, Crystal, Giấy, Gỗ thông — giá, ưu nhược điểm, và loại nào phù hợp.',
         'reading_time':8,
         'embed_code':'<div class="at-carousel" data-network="shopee" data-keyword="cat ve sinh meo" data-limit="6"></div>',
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Review Nexgard vs Frontline vs Bravecto — Thuốc phòng ve chó','slug':'review-nexgard-frontline-bravecto',
         'tier':'chi-tiet','category':'y-te',
         'related_segment_slug':'cho','related_zone_slug':'y-te',
         'tags':'Nexgard,Frontline,Bravecto,ve,bọ chét,so sánh,review',
         'excerpt':'So sánh 3 sản phẩm phòng ve chó bán chạy nhất: cách dùng, hiệu quả, giá, và tác dụng phụ.',
         'reading_time':9,
         'embed_code':'<div class="at-carousel" data-network="shopee" data-keyword="nexgard cho" data-limit="6"></div>',
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Ciao Churu, Inaba, JerHigh — Review top snack mèo 2025','slug':'review-top-snack-meo-2025',
         'tier':'chi-tiet','category':'dinh-duong',
         'related_segment_slug':'meo','related_zone_slug':'dinh-duong',
         'tags':'Ciao Churu,Inaba,JerHigh,snack mèo,treat,súp thưởng',
         'excerpt':'So sánh 3 dòng snack mèo hot nhất: Ciao Churu, Inaba, JerHigh — thành phần, giá, mèo thích loại nào nhất?',
         'reading_time':6,
         'embed_code':'<div class="at-carousel" data-network="shopee" data-keyword="ciao churu meo" data-limit="6"></div>',
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Hướng dẫn setup hồ thủy sinh đầu tiên — Budget 1 triệu','slug':'setup-ho-thuy-sinh-budget-1-trieu',
         'tier':'chi-tiet','category':'ca-canh',
         'related_segment_slug':'thu-nho','related_zone_slug':'ca-canh',
         'tags':'thủy sinh,aquascape,setup,người mới,budget,cây thủy sinh',
         'excerpt':'Setup hồ thủy sinh đẹp với chỉ 1 triệu đồng. Hướng dẫn từng bước cho người mới: bể, nền, cây, lọc, đèn.',
         'reading_time':10,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
    ]

    for ad in new_articles:
        existing = Article.query.filter_by(vertical_slug='pet', slug=ad['slug']).first()
        if existing:
            continue
        img = f"https://placehold.co/800x450/e17055/fff?text={ad['slug'][:30]}"
        a = Article(vertical_slug='pet', title=ad['title'], slug=ad['slug'],
            excerpt=ad.get('excerpt',''), content=ad.get('content',''),
            tier=ad.get('tier','chung'), category=ad.get('category',''),
            tags=ad.get('tags',''), related_segment_slug=ad.get('related_segment_slug',''),
            related_zone_slug=ad.get('related_zone_slug',''), embed_code=ad.get('embed_code',''),
            ai_generated=True, reading_time=ad.get('reading_time',5),
            views=random.randint(80, 5000), image_url=img)
        db.session.add(a)
        added_articles += 1

    # ================================================================
    # PRODUCTS MỚI — affiliate links
    # ================================================================
    new_products = {
        # Chó
        'thuc-an-theo-giong': [
            ('shopee', 'Royal Canin Poodle Adult 1.5kg', 'https://shope.ee/petv2-001', 355000),
            ('lazada', 'Royal Canin Golden Retriever Adult 12kg', 'https://s.lazada.vn/petv2-002', 1250000),
            ('tiki', 'Nutrience Subzero Canadian Pacific 5kg', 'https://tiki.vn/petv2-003', 850000),
        ],
        'snack-treat-cho': [
            ('shopee', 'Pedigree Dentastix Medium 7 thanh', 'https://shope.ee/petv2-010', 89000),
            ('lazada', 'JerHigh Stick Gà 420g', 'https://s.lazada.vn/petv2-011', 65000),
            ('shopee', 'Xương da bò cuộn 10cm x10 cái', 'https://shope.ee/petv2-012', 120000),
        ],
        'thuc-an-cho-con': [
            ('shopee', 'Royal Canin Medium Puppy 4kg', 'https://shope.ee/petv2-020', 520000),
            ('lazada', 'Taste of the Wild Puppy Pacific Stream 2.27kg', 'https://s.lazada.vn/petv2-021', 420000),
            ('shopee', 'Sữa bột chó con KMR PetAg 340g', 'https://shope.ee/petv2-022', 450000),
        ],
        'do-choi-cho': [
            ('shopee', 'Kong Classic Medium (đỏ)', 'https://shope.ee/petv2-030', 280000),
            ('lazada', 'Bóng tennis cho chó 3 quả', 'https://s.lazada.vn/petv2-031', 45000),
            ('tiki', 'Đồ chơi trí tuệ Nina Ottosson', 'https://tiki.vn/petv2-032', 520000),
        ],
        'sua-tam-cho': [
            ('shopee', 'Bio-Groom Super White Shampoo 355ml', 'https://shope.ee/petv2-040', 320000),
            ('lazada', 'Hartz Groomer Best Oatmeal 532ml', 'https://s.lazada.vn/petv2-041', 185000),
        ],
        # Mèo
        'snack-treat-meo': [
            ('shopee', 'Ciao Churu Cá Ngừ 14g x20 thanh', 'https://shope.ee/petv2-050', 195000),
            ('lazada', 'Inaba Grilled Tuna Fillet 25g x5', 'https://s.lazada.vn/petv2-051', 135000),
            ('shopee', 'Greenies Dental Cat Treat 60g', 'https://shope.ee/petv2-052', 110000),
        ],
        'thuc-an-meo-con': [
            ('shopee', 'Royal Canin Kitten 2kg', 'https://shope.ee/petv2-060', 380000),
            ('lazada', 'Royal Canin Babycat Milk 300g', 'https://s.lazada.vn/petv2-061', 420000),
        ],
        'do-choi-meo': [
            ('shopee', 'Cần câu lông gà cho mèo', 'https://shope.ee/petv2-070', 35000),
            ('lazada', 'Chuột giả catnip 3 con', 'https://s.lazada.vn/petv2-071', 49000),
            ('tiki', 'Đường hầm mèo 3 ngả', 'https://tiki.vn/petv2-072', 165000),
        ],
        'bat-an-voi-nuoc-meo': [
            ('shopee', 'Catit Flower Fountain 3L', 'https://shope.ee/petv2-080', 450000),
            ('lazada', 'PetKit Eversweet Solo 2 1.8L', 'https://s.lazada.vn/petv2-081', 680000),
            ('shopee', 'Bát ăn nghiêng 15° ceramic mèo', 'https://shope.ee/petv2-082', 89000),
        ],
        'balo-tui-van-chuyen': [
            ('shopee', 'Balo phi hành gia mèo', 'https://shope.ee/petv2-090', 350000),
            ('lazada', 'Chuồng vận chuyển nhựa IATA size M', 'https://s.lazada.vn/petv2-091', 280000),
        ],
        # Thú nhỏ
        'thuc-an-tho': [
            ('shopee', 'Cỏ Timothy hay 1kg', 'https://shope.ee/petv2-100', 75000),
            ('lazada', 'Viên nén Oxbow Adult Rabbit 2.27kg', 'https://s.lazada.vn/petv2-101', 350000),
        ],
        'long-chim': [
            ('shopee', 'Lồng vẹt yến phụng 45x45x60cm', 'https://shope.ee/petv2-110', 450000),
            ('lazada', 'Bộ phụ kiện lồng chim (cầu + bát + xích đu)', 'https://s.lazada.vn/petv2-111', 120000),
        ],
        'ca-betta': [
            ('shopee', 'Bể cá Betta mini kèm đèn LED', 'https://shope.ee/petv2-120', 120000),
            ('lazada', 'Thức ăn cá Betta Hikari 5g', 'https://s.lazada.vn/petv2-121', 55000),
        ],
        'ho-thuy-sinh': [
            ('shopee', 'Combo setup thủy sinh 40cm (bể+lọc+đèn+nền)', 'https://shope.ee/petv2-130', 850000),
            ('lazada', 'Rêu Java + Anubias Nana combo 5 bụi', 'https://s.lazada.vn/petv2-131', 95000),
        ],
    }

    for part_slug, products in new_products.items():
        part = Part.query.filter_by(slug=part_slug).first()
        if not part:
            continue
        for net, pname, url, price in products:
            existing = AffiliateLink.query.filter_by(part_id=part.id, url=url).first()
            if existing:
                continue
            al = AffiliateLink(part_id=part.id, network=net, product_name=pname,
                url=url, price=price, clicks=random.randint(10, 500),
                conversions=random.randint(0, 30),
                image_url=f"https://placehold.co/400x300/e17055/fff?text={pname.replace(' ','+')[:25]}")
            db.session.add(al)
            added_products += 1

    db.session.commit()
    print(f'[OK] Pet v2 expanded: +{added_parts} parts, +{added_articles} articles, +{added_products} products')


# =============================================
# TRAVEL VERTICAL
# =============================================
def seed_travel():
    """Seed Travel vertical - skip if already exists"""
    from models import db, Vertical, Segment, Zone, Part
    import random

    # Check if Travel vertical already exists
    if Vertical.query.filter_by(slug='travel').first():
        print('[SKIP] Travel vertical already exists')
        return

    print('[+] Seeding Travel vertical...')
    v = Vertical(name='Travel', slug='travel', description='Du lịch & Khách sạn — Khám phá, đặt phòng, trải nghiệm', icon='✈️', color='#0984e3', status='active', style='travel', template='general', default_mode='light')
    db.session.add(v)
    db.session.flush()

    segments_data = [
        {'name':'Trong nước','slug':'trong-nuoc','icon':'🇻🇳','desc':'Du lịch nội địa Việt Nam: biển, núi, phố cổ, miệt vườn'},
        {'name':'Quốc tế','slug':'quoc-te','icon':'🌏','desc':'Du lịch nước ngoài: Đông Nam Á, Đông Á, Châu Âu, Mỹ'},
        {'name':'Khách sạn & Resort','slug':'khach-san','icon':'🏨','desc':'Review, so sánh, đặt phòng khách sạn — từ budget đến 5 sao'},
    ]

    zones_map = {
        'trong-nuoc': [
            {'name':'Miền Bắc','slug':'mien-bac','icon':'⛰️','color':'#2ecc71',
             'desc':'Hà Nội, Sapa, Hạ Long, Ninh Bình, Tràng An',
             'parts':[
                 {'vi':'Hạ Long Bay','en':'Ha Long Bay','slug':'ha-long-bay',
                  'desc':'Vịnh Hạ Long — Di sản UNESCO, 1,969 hòn đảo đá vôi, du thuyền, kayak',
                  'tags':'Hạ Long,du thuyền,UNESCO,Quảng Ninh,biển',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Sapa & Fansipan','en':'Sapa & Fansipan','slug':'sapa-fansipan',
                  'desc':'Sapa — phố sương mù, ruộng bậc thang, chinh phục Fansipan 3,143m',
                  'tags':'Sapa,Fansipan,Lào Cai,trekking,ruộng bậc thang',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Ninh Bình — Tràng An','en':'Ninh Binh — Trang An','slug':'ninh-binh-trang-an',
                  'desc':'Tràng An — Di sản kép UNESCO, thuyền chèo qua hang động, cảnh núi non',
                  'tags':'Ninh Bình,Tràng An,Tam Cốc,thuyền,di sản',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
            {'name':'Miền Trung','slug':'mien-trung','icon':'🏛️','color':'#3498db',
             'desc':'Đà Nẵng, Hội An, Huế, Phong Nha, Quy Nhơn',
             'parts':[
                 {'vi':'Hội An — Phố cổ','en':'Hoi An Ancient Town','slug':'hoi-an-pho-co',
                  'desc':'Phố cổ Hội An — đèn lồng, ẩm thực, may đo áo dài, đêm rằm',
                  'tags':'Hội An,phố cổ,đèn lồng,ẩm thực,UNESCO,Quảng Nam',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Đà Nẵng — Biển & Bà Nà','en':'Da Nang','slug':'da-nang',
                  'desc':'Đà Nẵng — biển Mỹ Khê, Bà Nà Hills, Cầu Vàng, Ngũ Hành Sơn',
                  'tags':'Đà Nẵng,Bà Nà,Cầu Vàng,Mỹ Khê,biển',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Phong Nha — Hang động','en':'Phong Nha Caves','slug':'phong-nha',
                  'desc':'Vườn Quốc gia Phong Nha — Sơn Đoòng, Thiên Đường, Phong Nha',
                  'tags':'Phong Nha,Sơn Đoòng,hang động,Quảng Bình,UNESCO',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
            {'name':'Miền Nam','slug':'mien-nam','icon':'🌴','color':'#e74c3c',
             'desc':'TP.HCM, Phú Quốc, Đà Lạt, Cần Thơ, Vũng Tàu',
             'parts':[
                 {'vi':'Phú Quốc — Đảo ngọc','en':'Phu Quoc Island','slug':'phu-quoc',
                  'desc':'Phú Quốc — bãi biển đẹp, VinWonders, cáp treo, sunset, nước mắm',
                  'tags':'Phú Quốc,đảo,resort,VinWonders,biển,Kiên Giang',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Đà Lạt — Thành phố sương mù','en':'Da Lat','slug':'da-lat',
                  'desc':'Đà Lạt — hoa, cà phê, thác, kiến trúc Pháp, cắm trại',
                  'tags':'Đà Lạt,Lâm Đồng,sương mù,cà phê,hoa,núi',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
        ],
        'quoc-te': [
            {'name':'Đông Nam Á','slug':'dong-nam-a','icon':'🏝️','color':'#f39c12',
             'desc':'Thái Lan, Bali, Singapore, Malaysia — gần, rẻ, dễ đi',
             'parts':[
                 {'vi':'Bangkok & Pattaya','en':'Bangkok & Pattaya','slug':'bangkok-pattaya',
                  'desc':'Thái Lan — chùa, chợ đêm, street food, show, biển Pattaya',
                  'tags':'Bangkok,Pattaya,Thái Lan,chùa,street food,Chatuchak',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Bali — Đảo thần tiên','en':'Bali Island','slug':'bali',
                  'desc':'Bali — ruộng bậc thang, đền thiêng, lướt sóng, yoga retreat',
                  'tags':'Bali,Indonesia,đền,yoga,lướt sóng,Ubud,Seminyak',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
            {'name':'Đông Á','slug':'dong-a','icon':'🗼','color':'#e74c3c',
             'desc':'Nhật Bản, Hàn Quốc, Đài Loan — văn hóa, ẩm thực, mua sắm',
             'parts':[
                 {'vi':'Tokyo — Nhật Bản','en':'Tokyo Japan','slug':'tokyo',
                  'desc':'Tokyo — truyền thống & hiện đại, sushi, anime, cherry blossom',
                  'tags':'Tokyo,Nhật Bản,Japan,sushi,anime,sakura,Shibuya',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Seoul — Hàn Quốc','en':'Seoul South Korea','slug':'seoul',
                  'desc':'Seoul — K-pop, K-drama, BBQ, skincare, cung điện, Myeongdong',
                  'tags':'Seoul,Hàn Quốc,Korea,K-pop,Myeongdong,BBQ',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
        ],
        'khach-san': [
            {'name':'Budget & Hostel','slug':'budget','icon':'🏠','color':'#27ae60',
             'desc':'Khách sạn giá rẻ, hostel, homestay — dưới 500k/đêm',
             'parts':[
                 {'vi':'Cách đặt phòng giá rẻ','en':'Budget Booking Tips','slug':'cach-dat-phong-gia-re',
                  'desc':'Mẹo đặt phòng giá tốt: so sánh OTA, flash sale, loyalty program',
                  'tags':'đặt phòng,giá rẻ,OTA,Booking,Agoda,flash sale',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Homestay vs Hostel vs Hotel','en':'Accommodation Types','slug':'homestay-hostel-hotel',
                  'desc':'So sánh 3 loại hình lưu trú: homestay, hostel, hotel — phù hợp với ai?',
                  'tags':'homestay,hostel,hotel,so sánh,lưu trú,backpacker',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
            {'name':'4-5 Sao & Resort','slug':'resort','icon':'🌟','color':'#9b59b6',
             'desc':'Resort cao cấp, khách sạn 5 sao — trải nghiệm sang trọng',
             'parts':[
                 {'vi':'Top Resort Việt Nam','en':'Best Vietnam Resorts','slug':'top-resort-viet-nam',
                  'desc':'Top 10 resort đẹp nhất Việt Nam: InterContinental, Six Senses, Amanoi',
                  'tags':'resort,5 sao,InterContinental,Six Senses,Amanoi,luxury',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
                 {'vi':'Cách chọn resort phù hợp','en':'How to Choose a Resort','slug':'cach-chon-resort',
                  'desc':'Tiêu chí chọn resort: vị trí, view, F&B, spa, pool, giá trị thực',
                  'tags':'chọn resort,tiêu chí,review,đánh giá,value',
                  'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
             ]},
        ],
    }

    for sd in segments_data:
        s = Segment(vertical_id=v.id, name=sd['name'], slug=sd['slug'], icon=sd['icon'], description=sd['desc'])
        db.session.add(s)
        db.session.flush()
        for zd in zones_map.get(sd['slug'],[]):
            z = Zone(segment_id=s.id, name=zd['name'], slug=zd['slug'], icon=zd['icon'], color=zd['color'], description=zd['desc'])
            db.session.add(z)
            db.session.flush()
            for i, pd in enumerate(zd.get('parts',[])):
                p = Part(zone_id=z.id, name_vi=pd['vi'], name_en=pd.get('en',''), slug=pd['slug'],
                    description=pd['desc'], content=pd.get('content',''), oem_code=pd.get('oem',''),
                    tags=pd.get('tags',''), order=i)
                db.session.add(p)
    db.session.commit()
    print('[OK] Travel vertical seeded!')


def seed_travel_articles():
    """Seed travel articles - skip if already exists"""
    from models import db, Article
    import random

    # Check if travel articles already exist
    if Article.query.filter_by(vertical_slug='travel').first():
        print('[SKIP] Travel articles already exist')
        return

    print('[+] Seeding travel articles...')
    articles = [
        # T1: NGANH
        {'title':'Du lịch Việt Nam 2025 — Xu hướng & Điểm đến hot','slug':'du-lich-viet-nam-2025','tier':'nganh','category':'xu-huong',
         'tags':'du lịch,Việt Nam,2025,xu hướng,điểm đến',
         'excerpt':'Phân tích xu hướng du lịch VN 2025: staycation, du lịch trải nghiệm, digital nomad, và 5 điểm đến hot nhất.',
         'reading_time':8,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Cách lên kế hoạch du lịch tiết kiệm — Hướng dẫn A-Z','slug':'cach-len-ke-hoach-du-lich-tiet-kiem','tier':'nganh','category':'huong-dan',
         'tags':'tiết kiệm,kế hoạch,budget,mẹo,đặt vé,lịch trình',
         'excerpt':'Hướng dẫn lên kế hoạch du lịch từ A-Z: đặt vé rẻ, chọn lưu trú, lên lịch trình, và mẹo tiết kiệm tới 50%.',
         'reading_time':10,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Bảo hiểm du lịch — Có cần thiết không? Chọn gói nào?','slug':'bao-hiem-du-lich','tier':'nganh','category':'bao-hiem',
         'tags':'bảo hiểm,du lịch,quốc tế,trễ chuyến,hành lý,y tế',
         'excerpt':'Bảo hiểm du lịch: khi nào cần mua, gói nào phù hợp, và cách claim bồi thường.',
         'reading_time':7,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},

        # T2: CHUNG
        {'title':'Du lịch miền Bắc — Lịch trình 5N4Đ hoàn hảo','slug':'du-lich-mien-bac-5n4d','tier':'chung','category':'lich-trinh',
         'related_segment_slug':'trong-nuoc','related_zone_slug':'mien-bac',
         'tags':'miền Bắc,Hà Nội,Hạ Long,Sapa,Ninh Bình,5 ngày',
         'excerpt':'Lịch trình 5 ngày 4 đêm khám phá miền Bắc: Hà Nội → Hạ Long → Ninh Bình → Sapa. Budget 5-10 triệu.',
         'reading_time':12,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Ẩm thực đường phố Việt Nam — 20 món phải thử','slug':'am-thuc-duong-pho-viet-nam','tier':'chung','category':'am-thuc',
         'tags':'ẩm thực,street food,phở,bún chả,bánh mì,Việt Nam',
         'excerpt':'20 món ăn đường phố Việt Nam nổi tiếng thế giới: phở, bún chả, bánh mì, bún bò Huế...',
         'reading_time':8,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Visa du lịch — Hướng dẫn xin visa các nước phổ biến','slug':'visa-du-lich-huong-dan','tier':'chung','category':'visa',
         'tags':'visa,hộ chiếu,miễn visa,eVisa,Schengen,Nhật',
         'excerpt':'Hướng dẫn xin visa du lịch: Nhật, Hàn, Schengen, Mỹ, Úc. Điều kiện, hồ sơ, và mẹo đậu visa.',
         'reading_time':10,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},

        # T3: CHI TIET
        {'title':'Review InterContinental Đà Nẵng Sun Peninsula — Có đáng giá?','slug':'review-intercontinental-da-nang','tier':'chi-tiet','category':'review-resort',
         'related_segment_slug':'khach-san','related_zone_slug':'resort',
         'tags':'InterContinental,Đà Nẵng,resort,5 sao,review,Sun Peninsula',
         'excerpt':'Review chi tiết InterContinental Đà Nẵng: phòng, view, F&B, spa, pool — và liệu giá 5-15 triệu/đêm có xứng đáng?',
         'reading_time':8,
         'embed_code':'<div class="at-carousel" data-network="agoda" data-keyword="InterContinental Da Nang" data-limit="3"></div>',
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'Hướng dẫn trekking Sapa — Lịch trình, chuẩn bị, chi phí','slug':'huong-dan-trekking-sapa','tier':'chi-tiet','category':'trekking',
         'related_segment_slug':'trong-nuoc','related_zone_slug':'mien-bac',
         'tags':'trekking,Sapa,Fansipan,bản Cát Cát,ruộng bậc thang',
         'excerpt':'Hướng dẫn chi tiết trekking Sapa: chuẩn bị gì, mang gì, lịch trình 2N1Đ và 3N2Đ, chi phí từ 1 đến 5 triệu.',
         'reading_time':10,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
        {'title':'So sánh Agoda vs Booking.com vs Traveloka — Đặt ở đâu rẻ nhất?','slug':'agoda-vs-booking-vs-traveloka','tier':'chi-tiet','category':'dat-phong',
         'related_segment_slug':'khach-san',
         'tags':'Agoda,Booking,Traveloka,OTA,đặt phòng,so sánh,giá rẻ',
         'excerpt':'So sánh 3 OTA lớn nhất: Agoda, Booking.com, Traveloka. Giá, ưu đãi, chính sách hủy, và mẹo chọn nền tảng.',
         'reading_time':7,
         'content':'<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'},
    ]

    for ad in articles:
        img = ad.get('image_url', f"https://placehold.co/800x450/0984e3/fff?text={ad['slug'][:30]}")
        a = Article(vertical_slug='travel', title=ad['title'], slug=ad['slug'], excerpt=ad.get('excerpt',''),
            content=ad.get('content',''), tier=ad.get('tier','chung'), category=ad.get('category',''),
            tags=ad.get('tags',''), related_segment_slug=ad.get('related_segment_slug',''),
            related_zone_slug=ad.get('related_zone_slug',''), embed_code=ad.get('embed_code',''),
            ai_generated=True, reading_time=ad.get('reading_time',5), views=random.randint(100,8000),
            image_url=img)
        db.session.add(a)
    db.session.commit()
    print(f'[OK] {len(articles)} travel articles seeded!')

def seed_products_pet_travel():
    """Seed affiliate product links for Pet and Travel - skip if already exists"""
    from models import db, Vertical, Segment, Zone, Part, AffiliateLink, Voucher
    import random

    # Check if affiliate links already exist
    if AffiliateLink.query.first():
        print('[SKIP] Affiliate product links already exist')
        return

    print('[+] Seeding affiliate product links for Pet and Travel...')
    # Pet products
    pet = Vertical.query.filter_by(slug='pet').first()
    if pet:
        pet_products = {
            'thuc-an-hat': [
                ('shopee', 'Royal Canin Medium Adult 10kg', 'https://shope.ee/pet001', 850000),
                ('lazada', 'Pedigree Adult Chicken 10kg', 'https://s.lazada.vn/pet002', 420000),
                ('tiki', 'SmartHeart Gold Lamb 10kg', 'https://tiki.vn/pet003', 380000),
            ],
            'thuc-an-hat-meo': [
                ('shopee', 'Royal Canin Indoor Cat 4kg', 'https://shope.ee/pet010', 650000),
                ('lazada', 'Whiskas Ocean Fish 7kg', 'https://s.lazada.vn/pet011', 280000),
            ],
            'vaccine-co-ban': [
                ('shopee', 'Combo tiêm vaccine 5 bệnh + dại', 'https://shope.ee/pet020', 450000),
                ('accesstrade', 'Gói khám sức khỏe tổng quát chó', 'https://at.vn/pet021', 350000),
            ],
            'vaccine-meo': [
                ('shopee', 'Vaccine 3 bệnh mèo Tricat', 'https://shope.ee/pet030', 250000),
            ],
            'day-dat-vong-co': [
                ('shopee', 'Dây dắt chó tự động Flexi 5m', 'https://shope.ee/pet040', 320000),
                ('lazada', 'Vòng cổ LED phát sáng size M', 'https://s.lazada.vn/pet041', 89000),
                ('tiki', 'Bộ yếm dắt chó chống kéo size L', 'https://tiki.vn/pet042', 150000),
            ],
            'khay-cat': [
                ('shopee', 'Khay cát mèo có nắp đậy size L', 'https://shope.ee/pet050', 280000),
                ('lazada', 'Cát vệ sinh mèo Tofu 6L x3', 'https://s.lazada.vn/pet051', 195000),
            ],
            'chuong-hamster': [
                ('shopee', 'Chuồng hamster 2 tầng có ống chui', 'https://shope.ee/pet060', 350000),
                ('lazada', 'Combo chuồng + đệm + máng ăn', 'https://s.lazada.vn/pet061', 420000),
            ],
            'be-loc-nuoc': [
                ('shopee', 'Bể cá mini 30cm có lọc + đèn LED', 'https://shope.ee/pet070', 280000),
                ('tiki', 'Máy lọc nước bể cá Sunsun 600L/h', 'https://tiki.vn/pet071', 185000),
            ],
            'di-ve-sinh-dung-cho': [
                ('shopee', 'Bộ khay vệ sinh + tấm lót cho chó', 'https://shope.ee/pet080', 165000),
                ('lazada', 'Tấm lót vệ sinh chó 50 tấm size L', 'https://s.lazada.vn/pet081', 120000),
            ],
        }
        for seg in pet.segments:
            for z in seg.zones:
                for p in z.parts:
                    if p.slug in pet_products:
                        for net, pname, url, price in pet_products[p.slug]:
                            al = AffiliateLink(part_id=p.id, network=net, product_name=pname,
                                url=url, price=price, clicks=random.randint(10, 500),
                                conversions=random.randint(0, 30),
                                image_url=f"https://placehold.co/400x300/e17055/fff?text={pname.replace(' ','+')[:25]}")
                            db.session.add(al)

    # Travel products
    travel = Vertical.query.filter_by(slug='travel').first()
    if travel:
        travel_products = {
            'ha-long-bay': [
                ('agoda', 'Paradise Elegance Cruise 2N1Đ', 'https://agoda.com/tr001', 4500000),
                ('traveloka', 'Vinpearl Resort Hạ Long 5*', 'https://traveloka.com/tr002', 3200000),
                ('booking', 'FLC Ha Long Bay Golf Club & Luxury Resort', 'https://booking.com/tr003', 2800000),
            ],
            'hoi-an-pho-co': [
                ('agoda', 'Anantara Hoi An Resort 5*', 'https://agoda.com/tr010', 3800000),
                ('traveloka', 'Little Riverside Hoi An 4*', 'https://traveloka.com/tr011', 1800000),
                ('booking', 'Hoi An Ancient House Village', 'https://booking.com/tr012', 850000),
            ],
            'phu-quoc': [
                ('agoda', 'InterContinental Phu Quoc Long Beach', 'https://agoda.com/tr020', 6500000),
                ('traveloka', 'Vinpearl VinWonders Phu Quoc', 'https://traveloka.com/tr021', 880000),
                ('booking', 'Nam Nghi Phu Quoc Island 5*', 'https://booking.com/tr022', 4200000),
            ],
            'bangkok-pattaya': [
                ('agoda', 'Bangkok Marriott Marquis Queen\'s Park', 'https://agoda.com/tr030', 2200000),
                ('traveloka', 'Tour Bangkok-Pattaya 4N3Đ', 'https://traveloka.com/tr031', 8900000),
            ],
            'tokyo': [
                ('agoda', 'Shinjuku Granbell Hotel 4*', 'https://agoda.com/tr040', 3500000),
                ('booking', 'Tour Tokyo-Osaka 6N5Đ', 'https://booking.com/tr041', 25000000),
            ],
            'cach-dat-phong-gia-re': [
                ('agoda', 'Voucher giảm 15% Agoda', 'https://agoda.com/tr050', 0),
                ('traveloka', 'Flash Sale đêm thứ 6 Traveloka', 'https://traveloka.com/tr051', 0),
            ],
            'top-resort-viet-nam': [
                ('agoda', 'Six Senses Ninh Van Bay', 'https://agoda.com/tr060', 12000000),
                ('booking', 'Amanoi Vinh Hy Bay Ninh Thuận', 'https://booking.com/tr061', 18000000),
                ('traveloka', 'Fusion Resort Cam Ranh', 'https://traveloka.com/tr062', 5500000),
            ],
        }
        for seg in travel.segments:
            for z in seg.zones:
                for p in z.parts:
                    if p.slug in travel_products:
                        for net, pname, url, price in travel_products[p.slug]:
                            al = AffiliateLink(part_id=p.id, network=net, product_name=pname,
                                url=url, price=price, clicks=random.randint(20, 800),
                                conversions=random.randint(0, 40),
                                image_url=f"https://placehold.co/400x300/0984e3/fff?text={pname.replace(' ','+')[:25]}")
                            db.session.add(al)

    db.session.commit()
    pet_count = AffiliateLink.query.join(Part).join(Zone).join(Segment).join(Vertical).filter(Vertical.slug=='pet').count() if pet else 0
    travel_count = AffiliateLink.query.join(Part).join(Zone).join(Segment).join(Vertical).filter(Vertical.slug=='travel').count() if travel else 0
    print(f'[OK] Products seeded: Pet={pet_count}, Travel={travel_count}')

def seed_hotels():
    """Seed hotels - skip if already exists"""
    from models import db, Hotel
    import random

    # Check if hotels already exist
    if Hotel.query.first():
        print('[SKIP] Hotels already exist')
        return

    print('[+] Seeding hotels...')
    hotels_data = [
        # Da Nang
        ('Vinpearl Luxury Đà Nẵng','da-nang','Đà Nẵng',5,'Sơn Trà','Resort 5 sao hướng biển với hồ bơi vô cực','Hồ bơi vô cực, Spa, Gym, Biển riêng, Nhà hàng',9.2,1847,4200000),
        ('Hyatt Regency Danang','da-nang','Đà Nẵng',5,'Ngũ Hành Sơn','Khu nghỉ dưỡng đẳng cấp bên bờ biển Non Nước','Hồ bơi, Nhà hàng, Bar, Beach Club, Kids Club',9.0,2103,3800000),
        ('Novotel Danang Premier','da-nang','Đà Nẵng',5,'Hải Châu','Khách sạn trung tâm với view sông Hàn','Hồ bơi tầng thượng, Spa, Gym, Rooftop Bar',8.7,1562,2500000),
        ('Melia Danang Beach Resort','da-nang','Đà Nẵng',4,'Ngũ Hành Sơn','Resort gia đình bên biển Mỹ Khê','Biển riêng, Hồ bơi, Kids club, Buffet sáng',8.5,980,2200000),
        ('Sala Danang Beach Hotel','da-nang','Đà Nẵng',4,'Sơn Trà','Boutique hotel gần biển Mỹ Khê','View biển, Nhà hàng, Xe đưa đón sân bay',8.8,654,1200000),
        ('Fivitel Da Nang','da-nang','Đà Nẵng',3,'Hải Châu','Khách sạn giá tốt trung tâm thành phố','WiFi, Bãi xe, Bữa sáng, Dịch vụ giặt ủi',8.2,423,650000),
        # Phu Quoc
        ('InterContinental Phu Quoc','phu-quoc','Phú Quốc',5,'Long Beach','Resort sang trọng bậc nhất Phú Quốc','Biển riêng, 4 nhà hàng, Spa, Hồ bơi',9.5,2341,6800000),
        ('JW Marriott Phu Quoc','phu-quoc','Phú Quốc',5,'Bãi Kem','Kiến trúc độc đáo lấy cảm hứng từ Đại học','Spa, Golf, 5 nhà hàng, Beach bar',9.3,1876,5500000),
        ('Salinda Resort Phu Quoc','phu-quoc','Phú Quốc',5,'Long Beach','Resort boutique với hồ bơi vô cực hướng hoàng hôn','Hồ bơi vô cực, Sunset bar, Spa',9.0,892,3200000),
        ('Lahana Resort Phu Quoc','phu-quoc','Phú Quốc',4,'Dương Đông','Resort nhiệt đới yên tĩnh','Hồ bơi, Vườn nhiệt đới, Xe đạp miễn phí',8.6,567,1800000),
        # Nha Trang
        ('Sheraton Nha Trang','nha-trang','Nha Trang',5,'Trung tâm','Khách sạn 5 sao view biển trung tâm','View biển panorama, Hồ bơi, Spa, Gym',9.1,1654,3500000),
        ('Vinpearl Resort Nha Trang','nha-trang','Nha Trang',5,'Hòn Tre','Resort trên đảo với cáp treo vượt biển','VinWonders, Biển riêng, Aquarium, Cáp treo',8.9,2876,4000000),
        ('Mia Resort Nha Trang','nha-trang','Nha Trang',4,'Cam Ranh','Beach villa yên tĩnh vịnh Cam Ranh','Beach villa, Spa, Yoga, Nhà hàng Pháp',9.0,743,2200000),
        # Ha Noi
        ('Sofitel Legend Metropole','ha-noi','Hà Nội',5,'Hoàn Kiếm','Khách sạn huyền thoại từ 1901','Hồ bơi, Spa, 3 nhà hàng, Bar, Heritage wing',9.4,3210,5200000),
        ('JW Marriott Hanoi','ha-noi','Hà Nội',5,'Nam Từ Liêm','Khách sạn 5 sao hiện đại nhất Hà Nội','Hồ bơi trong nhà, Spa, 5 nhà hàng',9.1,2145,3000000),
        # HCM
        ('Park Hyatt Saigon','ho-chi-minh','TP.HCM',5,'Quận 1','Khách sạn luxury trung tâm Sài Gòn','Hồ bơi, Spa Xuan, Opera restaurant',9.3,1876,4500000),
        ('Rex Hotel Saigon','ho-chi-minh','TP.HCM',5,'Quận 1','Khách sạn lịch sử trên đường Nguyễn Huệ','Rooftop bar, Hồ bơi, Crown lounge',8.8,2543,2800000),
    ]
    for name,dest,dest_name,stars,district,desc,amenities,rating,reviews,price in hotels_data:
        slug = name.lower().replace(' ','-').replace("'","").replace('.','')[:60]
        h = Hotel(name=name,slug=slug,destination=dest,destination_name=dest_name,
            stars=stars,district=district,description=desc,amenities=amenities,
            rating=rating,reviews_count=reviews,price_from=price,
            agoda_url=f'https://www.agoda.com/search?q={slug}',
            is_active=True,is_featured=stars==5,
            clicks=random.randint(50,1000),conversions=random.randint(0,50))
        db.session.add(h)
    db.session.commit()
    print(f'[OK] {Hotel.query.count()} hotels seeded!')

def seed_attractions():
    """Seed attractions - skip if already exists"""
    from models import db, Attraction
    import random

    # Check if attractions already exist
    if Attraction.query.first():
        print('[SKIP] Attractions already exist')
        return

    print('[+] Seeding attractions...')
    CAT_ICONS = {'zoo':'🦁','aquarium':'🐠','cable_car':'🚡','theme_park':'🎢','museum':'🏛️','tour':'🚌','show':'🎭','waterpark':'🌊'}
    data = [
        # Da Nang
        ('Bà Nà Hills & Cầu Vàng','da-nang','Đà Nẵng','cable_car','Khu du lịch Bà Nà Hills với Cầu Vàng nổi tiếng thế giới','Bà Nà Hills, Đà Nẵng',900000,1200000,25,'klook'),
        ('Sun World Danang Wonders','da-nang','Đà Nẵng','theme_park','Công viên giải trí châu Á Park bên sông Hàn','1 Phan Đăng Lưu, Hải Châu',200000,300000,33,'klook'),
        ('Cù Lao Chàm Tour 1 ngày','da-nang','Đà Nẵng','tour','Tour lặn ngắm san hô + tham quan làng chài','Cù Lao Chàm, Quảng Nam',650000,850000,24,'accesstrade'),
        # Phu Quoc
        ('VinWonders Phú Quốc','phu-quoc','Phú Quốc','theme_park','Công viên giải trí & Aquarium lớn nhất VN','Bãi Dài, Phú Quốc',880000,1100000,20,'klook'),
        ('Safari Phú Quốc','phu-quoc','Phú Quốc','zoo','Vườn thú bán hoang dã lớn nhất VN — 3000+ động vật','Bãi Dài, Phú Quốc',650000,850000,24,'klook'),
        ('Cáp treo Hòn Thơm','phu-quoc','Phú Quốc','cable_car','Cáp treo vượt biển dài nhất thế giới 7.9km','An Thới, Phú Quốc',350000,500000,30,'accesstrade'),
        ('Sunset Town Tour','phu-quoc','Phú Quốc','tour','Tour ngắm hoàng hôn + show nhạc nước Kiss of the Sea','Nam Phú Quốc',400000,0,0,'agoda'),
        # Nha Trang
        ('VinWonders Nha Trang','nha-trang','Nha Trang','theme_park','Công viên giải trí trên đảo Hòn Tre','Hòn Tre, Nha Trang',950000,1200000,21,'klook'),
        ('Tháp Bà Ponagar','nha-trang','Nha Trang','museum','Di tích Chăm Pa cổ hơn 1000 năm tuổi','2 Tháng 4, Vĩnh Phước',22000,0,0,'accesstrade'),
        ('I-Resort Nha Trang','nha-trang','Nha Trang','waterpark','Suối khoáng nóng + tắm bùn + công viên nước','19/5 Phước Đồng',350000,450000,22,'klook'),
        # Ha Noi
        ('Hoàng thành Thăng Long','ha-noi','Hà Nội','museum','Di sản UNESCO — Trung tâm quyền lực 13 thế kỷ','19C Hoàng Diệu, Ba Đình',30000,0,0,'accesstrade'),
        ('Hà Nội Street Food Tour','ha-noi','Hà Nội','tour','Tour ẩm thực phố cổ 3h với hướng dẫn viên','Phố cổ Hà Nội',650000,850000,24,'klook'),
        ('Nhà tù Hỏa Lò','ha-noi','Hà Nội','museum','Di tích lịch sử "Hanoi Hilton"','1 Hoả Lò, Hoàn Kiếm',30000,0,0,'accesstrade'),
        # HCM
        ('Địa đạo Củ Chi','ho-chi-minh','TP.HCM','tour','Tour nửa ngày khám phá hệ thống địa đạo huyền thoại','Củ Chi, TP.HCM',280000,400000,30,'klook'),
        ('Sở thú Sài Gòn','ho-chi-minh','TP.HCM','zoo','Thảo Cầm Viên — vườn thú lâu đời nhất Đông Nam Á','Nguyễn Bỉnh Khiêm, Q1',50000,0,0,'accesstrade'),
        ('Đêm Sài Gòn Tour','ho-chi-minh','TP.HCM','tour','Tour xe máy đêm Sài Gòn + ẩm thực đường phố','Quận 1, TP.HCM',850000,1100000,23,'klook'),
        # Da Lat
        ('Cáp treo Đà Lạt','da-lat','Đà Lạt','cable_car','Cáp treo dài 2.3km ngắm thung lũng Prenn','Phường 3, Đà Lạt',100000,0,0,'accesstrade'),
        ('Thung lũng Tình Yêu','da-lat','Đà Lạt','theme_park','Công viên hoa + thuyền thiên nga + đồi cỏ hồng','Phường 8, Đà Lạt',100000,150000,33,'klook'),
        # Hoi An
        ('Hội An Eco Tour','hoi-an','Hội An','tour','Tour đạp xe + làng rau Trà Quế + thả đèn hoa đăng','Phố cổ Hội An',350000,500000,30,'klook'),
        ('Phố cổ Hội An Night Tour','hoi-an','Hội An','tour','Tour đi bộ phố cổ ban đêm + thả đèn lồng','Phố cổ Hội An',250000,350000,29,'accesstrade'),
    ]
    for name,dest,dest_name,cat,desc,addr,price,orig,disc,net in data:
        slug = name.lower().replace(' ','-').replace("'","").replace('.','')[:60]
        a = Attraction(name=name,slug=slug,destination=dest,destination_name=dest_name,
            category=cat,description=desc,address=addr,price_from=price,
            price_original=orig,discount_pct=disc,network=net,
            affiliate_url=f'https://{net}.com/attract/{slug}',
            rating=round(random.uniform(7.5,9.5),1),reviews_count=random.randint(100,3000),
            is_active=True,is_featured=disc>=25,
            clicks=random.randint(30,600),conversions=random.randint(0,40))
        db.session.add(a)
    db.session.commit()
    print(f'[OK] {Attraction.query.count()} attractions seeded!')

def seed_bike():
    """Seed Bike vertical - skip if already exists"""
    from models import db, Vertical, Segment, Zone, Part, AffiliateLink, Voucher, Article

    # Check if Bike vertical already exists
    if Vertical.query.filter_by(slug='bike').first():
        print('[SKIP] Bike vertical already exists')
        return

    print('[+] Seeding Bike vertical...')

    # Create Bike Vertical
    bike = Vertical(
        name='Bike',
        slug='bike',
        icon='🚴',
        color='#00cec9',
        description='Kiến thức về xe đạp và phụ kiện đạp xe — từ chọn xe phù hợp đến nâng cấp chi tiết.',
        status='live', style='bike', template='general', default_mode='light'
    )
    db.session.add(bike)
    db.session.flush()

    # Segments (Loại xe đạp)
    segments_data = [
        ('Road Bike', 'road-bike', '🚴‍♂️', 'Xe đạp đường trường — tốc độ cao, trọng lượng nhẹ, thích hợp đường nhựa phẳng'),
        ('Mountain Bike', 'mountain-bike', '🚵‍♂️', 'Xe đạp địa hình — phuộc dầu, lốp gai, chinh phục mọi địa hình'),
        ('Hybrid', 'hybrid', '🚲', 'Xe đạp lai — kết hợp ưu điểm road và MTB, đa năng cho đô thị'),
        ('Touring', 'touring', '🚵', 'Xe đạp touring — chở đồ đường dài, ổn định và bền bỉ'),
        ('BMX', 'bmx', '🛹', 'Xe đạp BMX — biểu diễn kỹ thuật, nhỏ gọn, cứng cáp'),
    ]
    segments = {}
    for i, (name, slug, icon, desc) in enumerate(segments_data):
        s = Segment(vertical_id=bike.id, name=name, slug=slug, icon=icon, description=desc, order=i)
        db.session.add(s)
        db.session.flush()
        segments[slug] = s

    # Zones (Hệ thống xe đạp) - Áp dụng cho Road Bike
    road_bike = segments['road-bike']
    zones_data = [
        ('Khung xe', 'khung-xe', '🏗️', '#00b894', 'Khung sườn, phuộc trước — bộ khung chính của xe, quyết định độ bền và trọng lượng'),
        ('Hệ thống phanh', 'he-thong-phanh', '🛑', '#ff7675', 'Phanh đĩa (disc brake), phanh lốp (rim brake) — an toàn khi xuống dốc'),
        ('Hệ thống truyền động', 'he-thong-truyen-dong', '⚙️', '#fdcb6e', 'Líp, sên, đùm, tay đề — truyền lực từ chân đạp đến bánh xe'),
        ('Bánh xe', 'banh-xe', '⭕', '#74b9ff', 'Vành, căm, lốp, săm — tiếp xúc với mặt đường, ảnh hưởng tốc độ và độ bám'),
        ('Yên & Tay lái', 'yen-va-tay-lai', '🦾', '#a29bfe', 'Yên xe, tay lái (handlebar), thân nâng — điều khiển và tư thế đạp'),
        ('Phụ kiện', 'phu-kien', '🔦', '#00cec9', 'Đèn, chuông, chắn bùn, bình nước, khoá xe — trang bị thêm'),
    ]
    zones = {}
    for i, (name, slug, icon, color, desc) in enumerate(zones_data):
        z = Zone(segment_id=road_bike.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
        db.session.add(z)
        db.session.flush()
        zones[slug] = z

    # Parts cho Hệ thống truyền động
    truyen_dong = zones['he-thong-truyen-dong']
    parts_data = [
        {
            'name_vi': 'Líp (Chainring)', 'name_en': 'Chainring',
            'slug': 'lip-chainring',
            'description': 'Đĩa răng phía trước gắn với bàn đạp, truyền lực từ chân đạp sang sên.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'oem_code': 'FC-R7000 (Shimano 105), FC-RS510 (Shimano Tiagra)',
            'tags': 'líp,chainring,truyền động,road bike,50/34T,53/39T,nâng cấp',
            'auto_category': 'phu-tung',
        },
        {
            'name_vi': 'Sên xe đạp', 'name_en': 'Chain',
            'slug': 'sen-xe-dap',
            'description': 'Dây xích truyền lực từ líp đến pít-tông (cassette), là bộ phận tiêu hao nhất.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'oem_code': 'CN-HG601-11 (Shimano 11s), CN-HG71 (Shimano 10s)',
            'tags': 'sên,chain,11 speed,bảo dưỡng,thay sên,road bike',
            'auto_category': 'bao-duong',
        },
        {
            'name_vi': 'Cassette (Pít-tông)', 'name_en': 'Cassette',
            'slug': 'cassette-pittong',
            'description': 'Bộ đĩa răng phía sau, gắn với đùm sau, có 8-12 líp với số răng tăng dần.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'oem_code': 'CS-R7000 11-30T (Shimano 105)',
            'tags': 'cassette,pít-tông,11-28T,11-32T,leo dốc,road bike',
            'auto_category': 'nang-cap',
        },
        {
            'name_vi': 'Tay đề (Shifter)', 'name_en': 'Shifter',
            'slug': 'tay-de-shifter',
            'description': 'Tay chuyển số tích hợp phanh (brifter), điều khiển chuyển líp trước và sau.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'oem_code': 'ST-R7000 (Shimano 105 11s)',
            'tags': 'tay đề,shifter,brifter,Shimano STI,SRAM DoubleTap,road bike',
            'auto_category': 'nang-cap',
        },
    ]
    for p_data in parts_data:
        p = Part(zone_id=truyen_dong.id, **p_data, status='published')
        db.session.add(p)
        db.session.flush()
        # Add affiliate links
        for net, base_price in [('shopee', 500000), ('lazada', 550000), ('tiki', 600000)]:
            al = AffiliateLink(
                part_id=p.id, network=net,
                product_name=f'{p_data["name_vi"]} chính hãng',
                url=f'https://{net}.vn/search?q={p_data["slug"]}',
                price=base_price,
                is_active=True,
                image_url=f"https://placehold.co/400x300/00cec9/fff?text={p_data['slug'][:25]}"
            )
            db.session.add(al)

    # Parts cho Bánh xe
    banh_xe = zones['banh-xe']
    parts_banh_xe = [
        {
            'name_vi': 'Vành xe đạp', 'name_en': 'Rim',
            'slug': 'vanh-xe-dap',
            'description': 'Vành bánh xe (rim), ảnh hưởng trọng lượng, độ khí động và độ cứng.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'vành,rim,carbon,nhôm,50mm,road bike,nâng cấp',
            'auto_category': 'nang-cap',
        },
        {
            'name_vi': 'Lốp xe đạp', 'name_en': 'Tire',
            'slug': 'lop-xe-dap',
            'description': 'Lốp road bike (700x23C, 700x25C, 700x28C), ảnh hưởng tốc độ và độ êm.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'lốp,tire,700x25C,tubeless,Continental GP5000,road bike',
            'auto_category': 'phu-tung',
        },
    ]
    for p_data in parts_banh_xe:
        p = Part(zone_id=banh_xe.id, **p_data, status='published')
        db.session.add(p)
        db.session.flush()
        for net, base_price in [('shopee', 300000), ('lazada', 350000), ('tiki', 400000)]:
            al = AffiliateLink(
                part_id=p.id, network=net,
                product_name=f'{p_data["name_vi"]} chính hãng',
                url=f'https://{net}.vn/search?q={p_data["slug"]}',
                price=base_price,
                is_active=True,
                image_url=f"https://placehold.co/400x300/00cec9/fff?text={p_data['slug'][:25]}"
            )
            db.session.add(al)

    # Clone zones cho các segment khác (mountain bike, hybrid,...)
    for seg_slug in ['mountain-bike', 'hybrid', 'touring', 'bmx']:
        seg = segments[seg_slug]
        for i, (name, slug, icon, color, desc) in enumerate(zones_data):
            z = Zone(segment_id=seg.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
            db.session.add(z)

    # Tạo articles mẫu
    articles_data = [
        {
            'title': 'Chọn xe đạp Road Bike cho người mới: Từ 10 triệu đến 30 triệu',
            'tier': 'nganh',
            'category': 'mua-xe',
            'excerpt': 'Hướng dẫn chi tiết cách chọn xe đạp đường trường phù hợp với ngân sách và nhu cầu sử dụng.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'reading_time': 8,
            'tags': 'road bike,mua xe mới,Shimano 105,Giant,Specialized,ngân sách',
        },
        {
            'title': 'Hệ thống truyền động xe đạp: Groupset Shimano 105 vs Ultegra vs Dura-Ace',
            'tier': 'chung',
            'category': 'truyen-dong',
            'excerpt': 'So sánh chi tiết 3 dòng groupset phổ biến nhất của Shimano, giúp bạn quyết định nâng cấp.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'reading_time': 10,
            'tags': 'groupset,Shimano 105,Ultegra,Dura-Ace,so sánh,nâng cấp',
            'related_segment_slug': 'road-bike',
        },
        {
            'title': 'Bảo dưỡng sên xe đạp: Vệ sinh, tra dầu và thay thế đúng cách',
            'tier': 'chi-tiet',
            'category': 'bao-duong',
            'excerpt': 'Hướng dẫn từng bước vệ sinh và tra dầu sên, giúp tăng tuổi thọ hệ thống truyền động.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'reading_time': 7,
            'tags': 'bảo dưỡng sên,tra dầu sên,vệ sinh sên,chain lube,thay sên',
            'related_zone_slug': 'he-thong-truyen-dong',
        },
    ]
    for a_data in articles_data:
        slug = a_data['title'].lower().replace(' ','-').replace(':','').replace(',','')[:60]
        a_data.setdefault('image_url', f"https://placehold.co/800x450/00cec9/fff?text={slug[:30]}")
        a = Article(
            vertical_slug='bike',
            slug=slug,
            status='published',
            ai_generated=False,
            **a_data
        )
        db.session.add(a)

    db.session.commit()
    print(f'✅ Bike vertical seeded: {Segment.query.filter_by(vertical_id=bike.id).count()} segments, {Zone.query.join(Segment).filter(Segment.vertical_id==bike.id).count()} zones, {Part.query.join(Zone).join(Segment).filter(Segment.vertical_id==bike.id).count()} parts, {Article.query.filter_by(vertical_slug="bike").count()} articles')

def seed_vouchers():
    """Seed voucher data - skip if already exists"""
    from datetime import datetime, timedelta

    # Check if vouchers already exist
    if Voucher.query.first():
        print('[SKIP] Vouchers already exist')
        return

    print('[+] Seeding vouchers...')
    vouchers_data = [
        # Shopee Vouchers
        {
            'code': 'SHOPEE50K',
            'title': 'Giảm 50K cho đơn hàng từ 200K',
            'description': 'Voucher giảm giá 50,000đ áp dụng cho đơn hàng từ 200,000đ trở lên.',
            'merchant': 'Shopee',
            'category': 'shopping',
            'discount_type': 'fixed_amount',
            'discount_value': 50000,
            'min_order': 200000,
            'max_discount': 0,
            'valid_to': datetime.utcnow() + timedelta(days=30),
            'usage_limit': 1000,
            'network': 'shopee',
            'terms': '- Áp dụng cho đơn hàng từ 200K\n- Không áp dụng với mã khác\n- Số lượng có hạn',
            'icon': '🛍️',
            'color': '#ee4d2d',
            'is_featured': True,
            'is_exclusive': False,
        },
        {
            'code': 'SHOPEE15',
            'title': 'Giảm 15% tối đa 100K',
            'description': 'Giảm 15% giá trị đơn hàng, tối đa 100,000đ.',
            'merchant': 'Shopee',
            'category': 'shopping',
            'discount_type': 'percentage',
            'discount_value': 15,
            'min_order': 150000,
            'max_discount': 100000,
            'valid_to': datetime.utcnow() + timedelta(days=25),
            'usage_limit': 500,
            'network': 'shopee',
            'icon': '🛍️',
            'color': '#ee4d2d',
            'is_featured': True,
        },
        # Lazada Vouchers
        {
            'code': 'LAZADA20',
            'title': 'Giảm 20% cho đơn đầu tiên',
            'description': 'Giảm ngay 20% cho đơn hàng đầu tiên, tối đa 150K.',
            'merchant': 'Lazada',
            'category': 'shopping',
            'discount_type': 'percentage',
            'discount_value': 20,
            'min_order': 0,
            'max_discount': 150000,
            'valid_to': datetime.utcnow() + timedelta(days=45),
            'usage_limit': 0,  # Unlimited
            'network': 'lazada',
            'icon': '🛒',
            'color': '#0f146d',
            'is_featured': True,
        },
        # Grab Food Vouchers
        {
            'code': 'GRABFOOD30K',
            'title': 'Giảm 30K đơn GrabFood',
            'description': 'Giảm 30,000đ cho đơn GrabFood từ 99,000đ.',
            'merchant': 'Grab',
            'category': 'food',
            'discount_type': 'fixed_amount',
            'discount_value': 30000,
            'min_order': 99000,
            'max_discount': 0,
            'valid_to': datetime.utcnow() + timedelta(days=15),
            'usage_limit': 300,
            'network': 'grab',
            'icon': '🍔',
            'color': '#00b14f',
            'is_featured': True,
        },
        {
            'code': 'GRABFREE',
            'title': 'Freeship GrabFood 0đ',
            'description': 'Miễn phí vận chuyển cho đơn từ 50K.',
            'merchant': 'Grab',
            'category': 'food',
            'discount_type': 'free_shipping',
            'discount_value': 0,
            'min_order': 50000,
            'max_discount': 25000,
            'valid_to': datetime.utcnow() + timedelta(days=20),
            'usage_limit': 0,
            'network': 'grab',
            'icon': '🚚',
            'color': '#00b14f',
        },
        # Tiki Vouchers
        {
            'code': 'TIKI100K',
            'title': 'Giảm 100K cho đơn từ 500K',
            'description': 'Mã giảm giá 100,000đ áp dụng cho đơn hàng từ 500,000đ.',
            'merchant': 'Tiki',
            'category': 'tech',
            'discount_type': 'fixed_amount',
            'discount_value': 100000,
            'min_order': 500000,
            'max_discount': 0,
            'valid_to': datetime.utcnow() + timedelta(days=35),
            'usage_limit': 200,
            'network': 'tiki',
            'icon': '💻',
            'color': '#189eff',
        },
        # Travel Vouchers
        {
            'code': 'AGODA15',
            'title': 'Giảm 15% booking khách sạn',
            'description': 'Giảm 15% chi phí đặt phòng qua Agoda, tối đa 500K.',
            'merchant': 'Agoda',
            'category': 'travel',
            'discount_type': 'percentage',
            'discount_value': 15,
            'min_order': 1000000,
            'max_discount': 500000,
            'valid_to': datetime.utcnow() + timedelta(days=60),
            'usage_limit': 100,
            'network': 'agoda',
            'icon': '✈️',
            'color': '#e84c4f',
            'is_featured': True,
            'is_exclusive': True,
        },
        {
            'code': 'KLOOK200K',
            'title': 'Giảm 200K vé tham quan',
            'description': 'Giảm 200K cho tour & vé tham quan qua Klook.',
            'merchant': 'Klook',
            'category': 'travel',
            'discount_type': 'fixed_amount',
            'discount_value': 200000,
            'min_order': 800000,
            'max_discount': 0,
            'valid_to': datetime.utcnow() + timedelta(days=40),
            'usage_limit': 50,
            'network': 'klook',
            'icon': '🎫',
            'color': '#ff5722',
            'is_exclusive': True,
        },
        # Services
        {
            'code': 'GRAB50',
            'title': 'Giảm 50% phí Grab Bike',
            'description': 'Giảm 50% phí xe công nghệ Grab Bike, tối đa 20K.',
            'merchant': 'Grab',
            'category': 'services',
            'discount_type': 'percentage',
            'discount_value': 50,
            'min_order': 0,
            'max_discount': 20000,
            'valid_to': datetime.utcnow() + timedelta(days=10),
            'usage_limit': 0,
            'network': 'grab',
            'icon': '🚴',
            'color': '#00b14f',
        },
        # Entertainment
        {
            'code': 'CGV100K',
            'title': 'Giảm 100K vé xem phim',
            'description': 'Combo vé + bắp nước giảm 100K tại CGV.',
            'merchant': 'CGV',
            'category': 'entertainment',
            'discount_type': 'fixed_amount',
            'discount_value': 100000,
            'min_order': 250000,
            'max_discount': 0,
            'valid_to': datetime.utcnow() + timedelta(days=20),
            'usage_limit': 150,
            'network': 'cgv',
            'icon': '🎬',
            'color': '#e50914',
        },
        # More varied vouchers
        {
            'code': 'TIKI25',
            'title': 'Giảm 25% sản phẩm công nghệ',
            'description': 'Giảm 25% cho điện thoại, laptop, phụ kiện.',
            'merchant': 'Tiki',
            'category': 'tech',
            'discount_type': 'percentage',
            'discount_value': 25,
            'min_order': 2000000,
            'max_discount': 1000000,
            'valid_to': datetime.utcnow() + timedelta(days=50),
            'usage_limit': 75,
            'network': 'tiki',
            'icon': '📱',
            'color': '#189eff',
            'is_featured': True,
        },
        {
            'code': 'SHOPEE500K',
            'title': 'Voucher 500K cho thời trang',
            'description': 'Giảm ngay 500K khi mua thời trang, giày dép từ 2 triệu.',
            'merchant': 'Shopee',
            'category': 'shopping',
            'discount_type': 'fixed_amount',
            'discount_value': 500000,
            'min_order': 2000000,
            'max_discount': 0,
            'valid_to': datetime.utcnow() + timedelta(days=28),
            'usage_limit': 50,
            'network': 'shopee',
            'terms': '- Chỉ áp dụng cho danh mục thời trang\n- Không áp dụng cùng voucher khác\n- Số lượng có hạn',
            'icon': '👗',
            'color': '#ee4d2d',
            'is_exclusive': True,
        },
        {
            'code': 'HEALTHFIRST',
            'title': 'Giảm 30% sản phẩm sức khỏe',
            'description': 'Giảm 30% vitamin, thực phẩm chức năng, tối đa 200K.',
            'merchant': 'Lazada',
            'category': 'health',
            'discount_type': 'percentage',
            'discount_value': 30,
            'min_order': 300000,
            'max_discount': 200000,
            'valid_to': datetime.utcnow() + timedelta(days=30),
            'usage_limit': 100,
            'network': 'lazada',
            'icon': '💊',
            'color': '#0f146d',
        },
    ]

    for v_data in vouchers_data:
        v = Voucher(**v_data)
        db.session.add(v)

    db.session.commit()
    print(f'✅ Vouchers seeded: {Voucher.query.count()} vouchers, {len([v for v in Voucher.query.all() if v.is_valid()])} valid now')

def seed_beauty():
    """Seed Beauty vertical data for cosmetics, skincare, beauty"""

    # Check if Beauty already exists
    beauty_vertical = Vertical.query.filter_by(slug='beauty').first()
    if beauty_vertical:
        print('[SKIP] Beauty vertical already exists')
        return

    print('[+] Seeding Beauty vertical...')
    # Vertical: Beauty
    beauty = Vertical(
        name='Beauty',
        slug='beauty',
        icon='💄',
        color='#e84393',
        description='Làm đẹp & Chăm sóc — Mỹ phẩm, skincare, makeup từ cơ bản đến nâng cao',
        status='live', style='beauty', template='general', default_mode='light'
    )
    db.session.add(beauty)
    db.session.flush()

    # Segments
    segments_data = [
        ('Skincare', 'skincare', '✨', 'Chăm sóc da — Serum, kem dưỡng, toner, mặt nạ...'),
        ('Makeup', 'makeup', '💋', 'Trang điểm — Son, phấn, mascara, cushion...'),
        ('Haircare', 'haircare', '💆‍♀️', 'Chăm sóc tóc — Dầu gội, dầu xả, serum dưỡng tóc...'),
        ('Bodycare', 'bodycare', '🧴', 'Chăm sóc cơ thể — Sữa tắm, kem body, tẩy tế bào chết...'),
        ('Perfume', 'perfume', '🌸', 'Nước hoa — Eau de Parfum, Eau de Toilette...'),
        ('Tools', 'tools', '🪮', 'Dụng cụ — Cọ makeup, máy rửa mặt, máy massage...'),
    ]

    segments = {}
    for i, (name, slug, icon, desc) in enumerate(segments_data):
        s = Segment(vertical_id=beauty.id, name=name, slug=slug, icon=icon, description=desc, order=i)
        db.session.add(s)
        db.session.flush()
        segments[slug] = s

    # Zones for Skincare segment
    skincare = segments['skincare']
    zones_data = [
        ('Làm sạch', 'lam-sach', '🧼', '#4fc3f7', 'Sữa rửa mặt, tẩy trang, gel rửa mặt'),
        ('Toner & Essence', 'toner-essence', '💧', '#81c784', 'Nước hoa hồng, essence, nước cân bằng'),
        ('Serum', 'serum', '✨', '#ba68c8', 'Serum vitamin C, retinol, niacinamide'),
        ('Kem dưỡng', 'kem-duong', '🧴', '#ffb74d', 'Kem dưỡng ẩm, kem dưỡng trắng'),
        ('Chống nắng', 'chong-nang', '☀️', '#ff8a65', 'Kem chống nắng, xịt chống nắng'),
        ('Mặt nạ', 'mat-na', '🎭', '#4db6ac', 'Mặt nạ giấy, mặt nạ ngủ, mặt nạ đất sét'),
    ]

    zones = {}
    for i, (name, slug, icon, color, desc) in enumerate(zones_data):
        z = Zone(segment_id=skincare.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
        db.session.add(z)
        db.session.flush()
        zones[slug] = z

    # Parts/Products for Serum zone
    serum_zone = zones['serum']
    parts_serum = [
        {
            'name_vi': 'Serum Vitamin C', 'name_en': 'Vitamin C Serum',
            'slug': 'serum-vitamin-c',
            'description': 'Serum dưỡng trắng, mờ thâm nám, chống lão hóa với vitamin C nguyên chất.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'serum,vitamin c,làm trắng da,chống lão hóa,skincare',
        },
        {
            'name_vi': 'Serum Niacinamide', 'name_en': 'Niacinamide Serum',
            'slug': 'serum-niacinamide',
            'description': 'Serum se khít lỗ chân lông, kiểm soát dầu, mờ thâm với niacinamide 10%.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'serum,niacinamide,se lỗ chân lông,da dầu,skincare',
        },
        {
            'name_vi': 'Serum Retinol', 'name_en': 'Retinol Serum',
            'slug': 'serum-retinol',
            'description': 'Serum chống lão hóa mạnh mẽ với retinol, giảm nếp nhăn, tái tạo da.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'serum,retinol,chống lão hóa,nếp nhăn,skincare',
        },
    ]

    for i, p_data in enumerate(parts_serum):
        p = Part(
            zone_id=serum_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Làm sạch zone (4 products) ---
    lam_sach_zone = zones['lam-sach']
    parts_lam_sach = [
        {
            'name_vi': 'Sữa rửa mặt CeraVe', 'name_en': 'CeraVe Foaming Cleanser',
            'slug': 'sua-rua-mat-cerave',
            'description': 'Sữa rửa mặt CeraVe dịu nhẹ, chứa ceramide phục hồi hàng rào da, pH 5.5.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'CeraVe,sữa rửa mặt,làm sạch,ceramide,da dầu,skincare',
        },
        {
            'name_vi': 'Tẩy trang dầu DHC', 'name_en': 'DHC Deep Cleansing Oil',
            'slug': 'tay-trang-dau-dhc',
            'description': 'Dầu tẩy trang DHC olive, làm sạch makeup chống nước, không gây mụn.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'DHC,tẩy trang,dầu tẩy trang,double cleanse,skincare',
        },
        {
            'name_vi': 'Gel rửa mặt La Roche-Posay', 'name_en': 'La Roche-Posay Effaclar Gel',
            'slug': 'gel-rua-mat-la-roche-posay',
            'description': 'Gel rửa mặt cho da dầu mụn, chứa zinc PCA kiểm soát bã nhờn, pH 5.5.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'La Roche-Posay,Effaclar,gel rửa mặt,da dầu mụn,skincare',
        },
        {
            'name_vi': 'Nước tẩy trang Bioderma', 'name_en': 'Bioderma Sensibio H2O',
            'slug': 'nuoc-tay-trang-bioderma',
            'description': 'Nước tẩy trang micellar Bioderma Sensibio, dịu nhẹ cho da nhạy cảm.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Bioderma,nước tẩy trang,micellar,da nhạy cảm,skincare',
        },
    ]
    for i, p_data in enumerate(parts_lam_sach):
        p = Part(
            zone_id=lam_sach_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Toner & Essence zone (3 products) ---
    toner_zone = zones['toner-essence']
    parts_toner = [
        {
            'name_vi': 'Toner Klairs Supple Preparation', 'name_en': 'Klairs Supple Preparation Toner',
            'slug': 'toner-klairs',
            'description': 'Toner dưỡng ẩm Klairs không cồn, dịu nhẹ, cấp nước sâu cho da khô.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Klairs,toner,dưỡng ẩm,K-beauty,da nhạy cảm,skincare',
        },
        {
            'name_vi': 'Essence SK-II Facial Treatment', 'name_en': 'SK-II Facial Treatment Essence',
            'slug': 'essence-sk-ii',
            'description': 'Nước thần SK-II chứa 90% Pitera, trẻ hóa da, cải thiện kết cấu da rõ rệt.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'SK-II,nước thần,Pitera,essence,chống lão hóa,skincare',
        },
        {
            'name_vi': 'Toner Some By Mi AHA-BHA-PHA', 'name_en': 'Some By Mi AHA BHA PHA Toner',
            'slug': 'toner-some-by-mi',
            'description': 'Toner tẩy da chết hóa học 3 trong 1, cải thiện da mụn trong 30 ngày.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Some By Mi,toner,AHA,BHA,PHA,tẩy da chết,da mụn,skincare',
        },
    ]
    for i, p_data in enumerate(parts_toner):
        p = Part(
            zone_id=toner_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Kem dưỡng zone (4 products) ---
    kem_duong_zone = zones['kem-duong']
    parts_kem_duong = [
        {
            'name_vi': 'Kem dưỡng ẩm CeraVe', 'name_en': 'CeraVe Moisturizing Cream',
            'slug': 'kem-duong-am-cerave',
            'description': 'Kem dưỡng ẩm CeraVe chứa 3 ceramide, phục hồi hàng rào da, dùng cả mặt và body.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'CeraVe,kem dưỡng ẩm,ceramide,moisturizer,skincare',
        },
        {
            'name_vi': 'Kem dưỡng Laneige Water Bank', 'name_en': 'Laneige Water Bank Cream',
            'slug': 'kem-duong-laneige',
            'description': 'Kem dưỡng cấp nước Laneige, công nghệ Blue Hyaluronic Acid, da căng bóng.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Laneige,kem dưỡng,cấp nước,Blue HA,K-beauty,skincare',
        },
        {
            'name_vi': 'Kem dưỡng trắng Pond\'s', 'name_en': 'Pond\'s White Beauty Cream',
            'slug': 'kem-duong-trang-ponds',
            'description': 'Kem dưỡng trắng da Pond\'s chứa niacinamide, giá bình dân, hiệu quả rõ.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Pond\'s,kem dưỡng trắng,niacinamide,bình dân,skincare',
        },
        {
            'name_vi': 'Kem dưỡng Innisfree Green Tea', 'name_en': 'Innisfree Green Tea Cream',
            'slug': 'kem-duong-innisfree',
            'description': 'Kem dưỡng trà xanh Innisfree, cấp ẩm sâu, thành phần tự nhiên từ đảo Jeju.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Innisfree,trà xanh,green tea,Jeju,kem dưỡng,skincare',
        },
    ]
    for i, p_data in enumerate(parts_kem_duong):
        p = Part(
            zone_id=kem_duong_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Chống nắng zone (3 products) ---
    chong_nang_zone = zones['chong-nang']
    parts_chong_nang = [
        {
            'name_vi': 'Kem chống nắng Anessa', 'name_en': 'Anessa Perfect UV Sunscreen',
            'slug': 'kem-chong-nang-anessa',
            'description': 'Kem chống nắng Anessa SPF50+ PA++++ vàng, chống nước, bền bỉ ngoài trời.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Anessa,chống nắng,SPF50,Shiseido,chống nước,skincare',
        },
        {
            'name_vi': 'Kem chống nắng Skin Aqua Tone Up', 'name_en': 'Skin Aqua Tone Up UV Essence',
            'slug': 'kem-chong-nang-skin-aqua',
            'description': 'Kem chống nắng Skin Aqua nâng tông, giá bình dân, texture nhẹ không bết.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Skin Aqua,chống nắng,nâng tông,bình dân,Rohto,skincare',
        },
        {
            'name_vi': 'Xịt chống nắng Neutrogena', 'name_en': 'Neutrogena Ultra Sheer Spray',
            'slug': 'xit-chong-nang-neutrogena',
            'description': 'Xịt chống nắng Neutrogena tiện lợi, dễ bôi lại, không để lại vệt trắng.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Neutrogena,xịt chống nắng,spray,SPF70,bôi lại,skincare',
        },
    ]
    for i, p_data in enumerate(parts_chong_nang):
        p = Part(
            zone_id=chong_nang_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Mặt nạ zone (3 products) ---
    mat_na_zone = zones['mat-na']
    parts_mat_na = [
        {
            'name_vi': 'Mặt nạ giấy Mediheal', 'name_en': 'Mediheal Sheet Mask',
            'slug': 'mat-na-giay-mediheal',
            'description': 'Mặt nạ giấy Mediheal N.M.F Aquaring, cấp ẩm sâu, best-seller Hàn Quốc.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Mediheal,mặt nạ giấy,N.M.F,cấp ẩm,K-beauty,skincare',
        },
        {
            'name_vi': 'Mặt nạ ngủ Laneige', 'name_en': 'Laneige Water Sleeping Mask',
            'slug': 'mat-na-ngu-laneige',
            'description': 'Mặt nạ ngủ Laneige cấp ẩm qua đêm, thức dậy da căng mọng, rạng rỡ.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Laneige,mặt nạ ngủ,sleeping mask,cấp ẩm,K-beauty,skincare',
        },
        {
            'name_vi': 'Mặt nạ đất sét Innisfree', 'name_en': 'Innisfree Volcanic Clay Mask',
            'slug': 'mat-na-dat-set-innisfree',
            'description': 'Mặt nạ đất sét núi lửa Jeju, hút bã nhờn, se lỗ chân lông, sạch sâu.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Innisfree,mặt nạ đất sét,volcanic clay,da dầu,se lỗ chân lông,skincare',
        },
    ]
    for i, p_data in enumerate(parts_mat_na):
        p = Part(
            zone_id=mat_na_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # Create zones for other segments (makeup, haircare, bodycare, perfume, tools)
    for seg_slug in ['makeup', 'haircare', 'bodycare', 'perfume', 'tools']:
        seg = segments[seg_slug]
        for i, (name, slug, icon, color, desc) in enumerate(zones_data):
            z = Zone(segment_id=seg.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
            db.session.add(z)

    db.session.commit()
    print('✅ Beauty vertical seeded with zones and parts!')

def seed_tech():
    """Seed Tech vertical data for phones, headphones, audio, gadgets"""
    # Check if Tech already exists
    tech_vertical = Vertical.query.filter_by(slug='tech').first()
    if tech_vertical:
        print('[SKIP] Tech vertical already exists')
        return

    print('[+] Seeding Tech vertical...')
    # Vertical: Tech
    tech = Vertical(
        name='Tech',
        slug='tech',
        icon='📱',
        color='#6c5ce7',
        description='Công nghệ & Thiết bị — Điện thoại, tai nghe, âm thanh, gadgets từ cơ bản đến cao cấp',
        status='live', style='tech', template='general', default_mode='light'
    )
    db.session.add(tech)
    db.session.flush()

    # Segments
    segments_data = [
        ('Smartphone', 'smartphone', '📱', 'Điện thoại thông minh — iPhone, Samsung, Xiaomi, OPPO...'),
        ('Headphones', 'headphones', '🎧', 'Tai nghe — AirPods, Sony, Bose, JBL...'),
        ('Speakers', 'speakers', '🔊', 'Loa — Bluetooth, smart speaker, soundbar...'),
        ('Laptops', 'laptops', '💻', 'Máy tính xách tay — MacBook, ThinkPad, Dell XPS...'),
        ('Watches', 'watches', '⌚', 'Đồng hồ thông minh — Apple Watch, Galaxy Watch...'),
        ('Accessories', 'accessories', '🔌', 'Phụ kiện — Sạc, cáp, ốp lưng, bảo vệ màn hình...'),
    ]

    segments = {}
    for i, (name, slug, icon, desc) in enumerate(segments_data):
        s = Segment(vertical_id=tech.id, name=name, slug=slug, icon=icon, description=desc, order=i)
        db.session.add(s)
        db.session.flush()
        segments[slug] = s

    # Zones for Smartphone segment
    smartphone = segments['smartphone']
    zones_data = [
        ('Màn hình', 'man-hinh', '📱', '#4fc3f7', 'OLED, AMOLED, LCD, tần số quét'),
        ('Chip xử lý', 'chip-xu-ly', '⚙️', '#ba68c8', 'Snapdragon, Apple A-series, Dimensity'),
        ('Camera', 'camera', '📷', '#81c784', 'Camera chính, camera góc rộng, zoom'),
        ('Pin & Sạc', 'pin-sac', '🔋', '#ff8a65', 'Dung lượng pin, sạc nhanh, sạc không dây'),
        ('Bộ nhớ', 'bo-nho', '💾', '#ffb74d', 'RAM, ROM, mở rộng lưu trữ'),
        ('Thiết kế', 'thiet-ke', '🎨', '#4db6ac', 'Vật liệu, màu sắc, kích thước'),
    ]

    zones = {}
    for i, (name, slug, icon, color, desc) in enumerate(zones_data):
        z = Zone(segment_id=smartphone.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
        db.session.add(z)
        db.session.flush()
        zones[slug] = z

    # Parts/Products for Camera zone
    camera_zone = zones['camera']
    parts_camera = [
        {
            'name_vi': 'Camera chính', 'name_en': 'Main Camera',
            'slug': 'camera-chinh',
            'description': 'Camera chính 50MP, cảm biến lớn, chụp đẹp cả ngày lẫn đêm.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'camera,smartphone,chụp ảnh,cảm biến,tech',
        },
        {
            'name_vi': 'Camera góc rộng', 'name_en': 'Ultrawide Camera',
            'slug': 'camera-goc-rong',
            'description': 'Camera góc rộng 12MP, góc chụp 120°, chụp phong cảnh đẹp.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'camera,góc rộng,ultrawide,smartphone,tech',
        },
        {
            'name_vi': 'Camera zoom', 'name_en': 'Telephoto Camera',
            'slug': 'camera-zoom',
            'description': 'Camera zoom quang học 3x-5x, chụp xa không mất chất lượng.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'camera,zoom,telephoto,smartphone,tech',
        },
    ]

    for i, p_data in enumerate(parts_camera):
        p = Part(
            zone_id=camera_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Màn hình zone (4 products) ---
    man_hinh_zone = zones['man-hinh']
    parts_man_hinh = [
        {
            'name_vi': 'Màn hình OLED', 'name_en': 'OLED Display',
            'slug': 'man-hinh-oled',
            'description': 'Công nghệ OLED cho màu sắc rực rỡ, đen tuyệt đối, tiết kiệm pin.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'OLED,màn hình,smartphone,display,tech',
        },
        {
            'name_vi': 'Màn hình AMOLED', 'name_en': 'AMOLED Display',
            'slug': 'man-hinh-amoled',
            'description': 'Super AMOLED của Samsung — sáng hơn, tiết kiệm pin hơn OLED truyền thống.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'AMOLED,Super AMOLED,Samsung,màn hình,tech',
        },
        {
            'name_vi': 'Kính cường lực', 'name_en': 'Tempered Glass',
            'slug': 'kinh-cuong-luc',
            'description': 'Kính bảo vệ màn hình Gorilla Glass, chống xước, chống vỡ hiệu quả.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'kính cường lực,Gorilla Glass,bảo vệ màn hình,tech',
        },
        {
            'name_vi': 'Tần số quét 120Hz', 'name_en': '120Hz Refresh Rate',
            'slug': 'tan-so-quet-120hz',
            'description': 'Màn hình 120Hz cho thao tác mượt mà, cuộn trang siêu mịn, chơi game đỉnh.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': '120Hz,tần số quét,LTPO,màn hình mượt,tech',
        },
    ]
    for i, p_data in enumerate(parts_man_hinh):
        p = Part(
            zone_id=man_hinh_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Chip xử lý zone (3 products) ---
    chip_zone = zones['chip-xu-ly']
    parts_chip = [
        {
            'name_vi': 'Snapdragon 8 Gen 3', 'name_en': 'Snapdragon 8 Gen 3',
            'slug': 'snapdragon-8-gen-3',
            'description': 'Chip flagship Qualcomm mạnh nhất, AI on-device, GPU Adreno 750 cho game đỉnh.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Snapdragon,Qualcomm,chip,processor,flagship,tech',
        },
        {
            'name_vi': 'Apple A17 Pro', 'name_en': 'Apple A17 Pro',
            'slug': 'apple-a17-pro',
            'description': 'Chip 3nm đầu tiên trên smartphone, ray tracing hardware, hiệu năng vượt trội.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Apple,A17 Pro,chip,3nm,iPhone,tech',
        },
        {
            'name_vi': 'Dimensity 9300', 'name_en': 'Dimensity 9300',
            'slug': 'dimensity-9300',
            'description': 'Chip MediaTek all big-core, hiệu năng ngang Snapdragon, giá tốt hơn.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Dimensity,MediaTek,chip,processor,tech',
        },
    ]
    for i, p_data in enumerate(parts_chip):
        p = Part(
            zone_id=chip_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Pin & Sạc zone (4 products) ---
    pin_zone = zones['pin-sac']
    parts_pin = [
        {
            'name_vi': 'Pin lithium-polymer', 'name_en': 'Lithium-Polymer Battery',
            'slug': 'pin-lithium-polymer',
            'description': 'Pin Li-Po mỏng, nhẹ, dung lượng 4500-6000mAh cho smartphone hiện đại.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'pin,lithium,battery,smartphone,tech',
        },
        {
            'name_vi': 'Sạc nhanh 120W', 'name_en': '120W Fast Charging',
            'slug': 'sac-nhanh-120w',
            'description': 'Công nghệ sạc nhanh 120W — đầy pin trong 15 phút, an toàn với bảo vệ đa lớp.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'sạc nhanh,120W,fast charging,smartphone,tech',
        },
        {
            'name_vi': 'Sạc không dây Qi2', 'name_en': 'Qi2 Wireless Charging',
            'slug': 'sac-khong-day-qi2',
            'description': 'Sạc không dây chuẩn Qi2 với nam châm MagSafe, tốc độ 15W, tiện lợi.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'sạc không dây,Qi2,MagSafe,wireless charging,tech',
        },
        {
            'name_vi': 'Pin dự phòng 20000mAh', 'name_en': 'Power Bank 20000mAh',
            'slug': 'pin-du-phong-20000mah',
            'description': 'Pin sạc dự phòng 20000mAh, sạc nhanh 65W, mang lên máy bay được.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'pin dự phòng,power bank,sạc dự phòng,20000mAh,tech',
        },
    ]
    for i, p_data in enumerate(parts_pin):
        p = Part(
            zone_id=pin_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Bộ nhớ zone (3 products) ---
    bo_nho_zone = zones['bo-nho']
    parts_bo_nho = [
        {
            'name_vi': 'RAM LPDDR5X', 'name_en': 'LPDDR5X RAM',
            'slug': 'ram-lpddr5x',
            'description': 'RAM LPDDR5X 8-16GB, tốc độ 8533Mbps, đa nhiệm mượt mà.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'RAM,LPDDR5X,bộ nhớ,đa nhiệm,tech',
        },
        {
            'name_vi': 'Bộ nhớ UFS 4.0', 'name_en': 'UFS 4.0 Storage',
            'slug': 'bo-nho-ufs-4',
            'description': 'Bộ nhớ trong UFS 4.0, tốc độ đọc 4200MB/s, mở app cực nhanh.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'UFS 4.0,bộ nhớ trong,storage,tốc độ,tech',
        },
        {
            'name_vi': 'Thẻ nhớ microSD', 'name_en': 'microSD Card',
            'slug': 'the-nho-microsd',
            'description': 'Thẻ nhớ mở rộng microSD A2 U3, tốc độ đọc 160MB/s, mở rộng lưu trữ.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'thẻ nhớ,microSD,mở rộng,lưu trữ,tech',
        },
    ]
    for i, p_data in enumerate(parts_bo_nho):
        p = Part(
            zone_id=bo_nho_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Thiết kế zone (3 products) ---
    thiet_ke_zone = zones['thiet-ke']
    parts_thiet_ke = [
        {
            'name_vi': 'Ốp lưng silicon', 'name_en': 'Silicone Case',
            'slug': 'op-lung-silicon',
            'description': 'Ốp lưng silicon mềm, chống sốc, bám tay, nhiều màu sắc thời trang.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'ốp lưng,silicon,case,bảo vệ,thời trang,tech',
        },
        {
            'name_vi': 'Khung viền titanium', 'name_en': 'Titanium Frame',
            'slug': 'khung-vien-titanium',
            'description': 'Khung viền titanium cao cấp — nhẹ hơn thép, cứng hơn nhôm, sang trọng.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'titanium,khung viền,vật liệu,flagship,thiết kế,tech',
        },
        {
            'name_vi': 'Kính lưng Ceramic', 'name_en': 'Ceramic Back Glass',
            'slug': 'kinh-lung-ceramic',
            'description': 'Mặt lưng kính ceramic shield — chống xước, chống vỡ, hỗ trợ sạc không dây.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'kính lưng,ceramic,Gorilla Glass,thiết kế,tech',
        },
    ]
    for i, p_data in enumerate(parts_thiet_ke):
        p = Part(
            zone_id=thiet_ke_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # Create zones for other segments (headphones, speakers, laptops, watches, accessories)
    for seg_slug in ['headphones', 'speakers', 'laptops', 'watches', 'accessories']:
        seg = segments[seg_slug]
        for i, (name, slug, icon, color, desc) in enumerate(zones_data):
            z = Zone(segment_id=seg.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
            db.session.add(z)

    db.session.commit()
    print('✅ Tech vertical seeded with zones and parts!')

def seed_beauty_articles():
    """Seed Beauty articles - 3-tier content"""
    from models import Article
    
    # Check if Beauty articles exist
    if Article.query.filter_by(vertical_slug='beauty', tier='nganh').first():
        print('[SKIP] Beauty articles already exist')
        return
    
    print('[+] Seeding Beauty articles...')
    articles = [
        # === TIER 1: NGANH (Industry - Beauty market) ===
        {
            'title': 'Thị trường mỹ phẩm Việt Nam 2025 — Xu hướng & Cơ hội',
            'slug': 'thi-truong-my-pham-viet-nam-2025',
            'tier': 'nganh',
            'category': 'thi-truong',
            'tags': 'thị trường,mỹ phẩm,skincare,Việt Nam,2025,xu hướng,K-beauty',
            'excerpt': 'Phân tích toàn cảnh thị trường mỹ phẩm Việt Nam: quy mô 2.8 tỷ USD, tăng trưởng 18%/năm, và xu hướng skincare bùng nổ.',
            'reading_time': 8,
            'vertical_slug': 'beauty',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
        {
            'title': 'Skincare Routine — Quy trình chăm sóc da cơ bản cho người mới',
            'slug': 'skincare-routine-co-ban',
            'tier': 'nganh',
            'category': 'kien-thuc-chung',
            'tags': 'skincare,quy trình,chăm sóc da,cleanse,moisturize,SPF',
            'excerpt': 'Hướng dẫn quy trình skincare cơ bản 5 bước cho người mới: làm sạch, toner, serum, kem dưỡng, chống nắng.',
            'reading_time': 10,
            'vertical_slug': 'beauty',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
        {
            'title': 'AHA vs BHA vs PHA — Acid tẩy da chết nên chọn loại nào?',
            'slug': 'aha-bha-pha-acid-tay-da-chet',
            'tier': 'nganh',
            'category': 'thanh-phan',
            'tags': 'AHA,BHA,PHA,acid,tẩy tế bào chết,exfoliate,mụn',
            'excerpt': 'So sánh 3 loại acid phổ biến: AHA (glycolic, lactic), BHA (salicylic), PHA. Loại nào phù hợp với từng loại da.',
            'reading_time': 7,
            'vertical_slug': 'beauty',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
    ]
    
    for a_data in articles:
        img = a_data.get('image_url', f"https://placehold.co/800x450/e84393/fff?text={a_data['slug'][:30]}")
        a = Article(
            title=a_data['title'],
            slug=a_data['slug'],
            tier=a_data['tier'],
            category=a_data['category'],
            tags=a_data['tags'],
            excerpt=a_data['excerpt'],
            reading_time=a_data['reading_time'],
            vertical_slug=a_data['vertical_slug'],
            content=a_data['content'],
            status='published',
            ai_generated=False,
            image_url=img
        )
        db.session.add(a)

    db.session.commit()
    print(f'✅ Beauty articles seeded: {len(articles)} articles')

def seed_tech_articles():
    """Seed Tech articles - 3-tier content"""
    from models import Article
    
    # Check if Tech articles exist
    if Article.query.filter_by(vertical_slug='tech', tier='nganh').first():
        print('[SKIP] Tech articles already exist')
        return
    
    print('[+] Seeding Tech articles...')
    articles = [
        # === TIER 1: NGANH (Industry - Tech market) ===
        {
            'title': 'Thị trường smartphone Việt Nam 2025 — Xu hướng & Top brands',
            'slug': 'thi-truong-smartphone-viet-nam-2025',
            'tier': 'nganh',
            'category': 'thi-truong',
            'tags': 'thị trường,smartphone,điện thoại,Việt Nam,2025,iPhone,Samsung',
            'excerpt': 'Phân tích thị trường điện thoại Việt Nam: Samsung dẫn đầu 28%, Apple tăng mạnh, Xiaomi áp đảo phân khúc tầm trung.',
            'reading_time': 8,
            'vertical_slug': 'tech',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
        {
            'title': 'Chip smartphone 2025 — Snapdragon vs Apple A-series vs Dimensity',
            'slug': 'chip-smartphone-snapdragon-apple-dimensity',
            'tier': 'nganh',
            'category': 'kien-thuc-chung',
            'tags': 'chip,processor,Snapdragon,Apple A17,Dimensity,hiệu năng',
            'excerpt': 'So sánh 3 dòng chip hàng đầu: Snapdragon 8 Gen 3, Apple A17 Pro, Dimensity 9300. Chip nào mạnh nhất, tiết kiệm pin nhất?',
            'reading_time': 10,
            'vertical_slug': 'tech',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
        {
            'title': 'Camera smartphone — Megapixel cao không phải là tất cả',
            'slug': 'camera-smartphone-megapixel',
            'tier': 'nganh',
            'category': 'camera',
            'tags': 'camera,megapixel,cảm biến,sensor,chụp ảnh,nhiếp ảnh',
            'excerpt': 'Tại sao iPhone 48MP chụp đẹp hơn nhiều Android 200MP? Giải mã vai trò của kích thước cảm biến, khẩu độ, xử lý ảnh.',
            'reading_time': 7,
            'vertical_slug': 'tech',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
    ]
    
    for a_data in articles:
        img = a_data.get('image_url', f"https://placehold.co/800x450/6c5ce7/fff?text={a_data['slug'][:30]}")
        a = Article(
            title=a_data['title'],
            slug=a_data['slug'],
            tier=a_data['tier'],
            category=a_data['category'],
            tags=a_data['tags'],
            excerpt=a_data['excerpt'],
            reading_time=a_data['reading_time'],
            vertical_slug=a_data['vertical_slug'],
            content=a_data['content'],
            status='published',
            ai_generated=False,
            image_url=img
        )
        db.session.add(a)

    db.session.commit()
    print(f'✅ Tech articles seeded: {len(articles)} articles')


def seed_products_beauty_tech():
    """Seed affiliate product links for Beauty and Tech verticals"""
    from models import db, Vertical, Segment, Zone, Part, AffiliateLink
    import random

    seeded = 0

    # ── Beauty products ──
    beauty = Vertical.query.filter_by(slug='beauty').first()
    if beauty:
        existing = AffiliateLink.query.join(Part).join(Zone).join(Segment).join(Vertical).filter(Vertical.slug == 'beauty').count()
        if existing:
            print(f'[SKIP] Beauty already has {existing} affiliate links')
        else:
            print('[+] Seeding Beauty affiliate links...')
            beauty_products = {
                'serum-vitamin-c': [
                    ('shopee', 'Serum Vitamin C Melano CC Rohto 20ml', 'https://shope.ee/beauty001', 185000),
                    ('lazada', 'Serum Obagi Vitamin C 15% 30ml', 'https://s.lazada.vn/beauty002', 1250000),
                    ('tiki', 'Serum Klairs Vitamin C 35ml', 'https://tiki.vn/beauty003', 350000),
                ],
                'serum-niacinamide': [
                    ('shopee', "The Ordinary Niacinamide 10% 30ml", 'https://shope.ee/beauty010', 195000),
                    ('lazada', 'Paula\'s Choice 10% Niacinamide Booster', 'https://s.lazada.vn/beauty011', 780000),
                ],
                'serum-retinol': [
                    ('shopee', 'The Ordinary Retinol 0.5% 30ml', 'https://shope.ee/beauty020', 220000),
                    ('lazada', 'CeraVe Resurfacing Retinol Serum', 'https://s.lazada.vn/beauty021', 450000),
                ],
                'sua-rua-mat-cerave': [
                    ('shopee', 'CeraVe Foaming Cleanser 236ml', 'https://shope.ee/beauty030', 285000),
                    ('lazada', 'CeraVe Hydrating Cleanser 473ml', 'https://s.lazada.vn/beauty031', 380000),
                    ('tiki', 'CeraVe SA Smoothing Cleanser 236ml', 'https://tiki.vn/beauty032', 320000),
                ],
                'tay-trang-dau-dhc': [
                    ('shopee', 'DHC Deep Cleansing Oil 200ml', 'https://shope.ee/beauty040', 520000),
                    ('lazada', 'DHC Deep Cleansing Oil 70ml', 'https://s.lazada.vn/beauty041', 250000),
                ],
                'gel-rua-mat-la-roche-posay': [
                    ('shopee', 'La Roche-Posay Effaclar Gel 400ml', 'https://shope.ee/beauty050', 485000),
                    ('tiki', 'La Roche-Posay Effaclar Duo+ 40ml', 'https://tiki.vn/beauty051', 520000),
                ],
                'nuoc-tay-trang-bioderma': [
                    ('shopee', 'Bioderma Sensibio H2O 500ml', 'https://shope.ee/beauty060', 385000),
                    ('lazada', 'Bioderma Sensibio H2O 250ml', 'https://s.lazada.vn/beauty061', 250000),
                ],
                'toner-klairs': [
                    ('shopee', 'Klairs Supple Preparation Toner 180ml', 'https://shope.ee/beauty070', 320000),
                    ('lazada', 'Klairs Supple Preparation Unscented 180ml', 'https://s.lazada.vn/beauty071', 335000),
                ],
                'essence-sk-ii': [
                    ('shopee', 'SK-II Facial Treatment Essence 230ml', 'https://shope.ee/beauty080', 3800000),
                    ('tiki', 'SK-II Facial Treatment Essence 75ml', 'https://tiki.vn/beauty081', 1650000),
                ],
                'toner-some-by-mi': [
                    ('shopee', 'Some By Mi AHA-BHA-PHA Toner 150ml', 'https://shope.ee/beauty090', 265000),
                    ('lazada', 'Some By Mi AHA-BHA-PHA Serum 50ml', 'https://s.lazada.vn/beauty091', 280000),
                ],
                'kem-duong-am-cerave': [
                    ('shopee', 'CeraVe Moisturizing Cream 340g', 'https://shope.ee/beauty100', 385000),
                    ('lazada', 'CeraVe PM Facial Moisturizing Lotion 52ml', 'https://s.lazada.vn/beauty101', 350000),
                ],
                'kem-duong-laneige': [
                    ('shopee', 'Laneige Water Bank Blue HA Cream 50ml', 'https://shope.ee/beauty110', 750000),
                    ('tiki', 'Laneige Water Bank Gel Cream 50ml', 'https://tiki.vn/beauty111', 680000),
                ],
                'kem-duong-trang-ponds': [
                    ('shopee', 'Pond\'s White Beauty 50g', 'https://shope.ee/beauty120', 89000),
                    ('lazada', 'Pond\'s Age Miracle Night Cream 50g', 'https://s.lazada.vn/beauty121', 210000),
                ],
                'kem-duong-innisfree': [
                    ('shopee', 'Innisfree Green Tea Seed Cream 50ml', 'https://shope.ee/beauty130', 420000),
                    ('lazada', 'Innisfree Green Tea Seed Serum 80ml', 'https://s.lazada.vn/beauty131', 380000),
                ],
                'kem-chong-nang-anessa': [
                    ('shopee', 'Anessa Perfect UV Milk SPF50+ 60ml', 'https://shope.ee/beauty140', 450000),
                    ('lazada', 'Anessa Perfect UV Gel SPF50+ 90g', 'https://s.lazada.vn/beauty141', 520000),
                    ('tiki', 'Anessa Whitening UV Gel SPF50+ 90g', 'https://tiki.vn/beauty142', 480000),
                ],
                'kem-chong-nang-skin-aqua': [
                    ('shopee', 'Skin Aqua Tone Up UV Essence 80g', 'https://shope.ee/beauty150', 155000),
                    ('lazada', 'Skin Aqua Super Moisture Milk SPF50 40ml', 'https://s.lazada.vn/beauty151', 125000),
                ],
                'xit-chong-nang-neutrogena': [
                    ('shopee', 'Neutrogena Ultra Sheer Spray SPF70 141g', 'https://shope.ee/beauty160', 280000),
                    ('tiki', 'Neutrogena Ultra Sheer Dry-Touch SPF55 88ml', 'https://tiki.vn/beauty161', 245000),
                ],
                'mat-na-giay-mediheal': [
                    ('shopee', 'Mediheal N.M.F Aquaring Ampoule Mask 10 miếng', 'https://shope.ee/beauty170', 155000),
                    ('lazada', 'Mediheal Tea Tree Mask 10 miếng', 'https://s.lazada.vn/beauty171', 160000),
                ],
                'mat-na-ngu-laneige': [
                    ('shopee', 'Laneige Water Sleeping Mask 70ml', 'https://shope.ee/beauty180', 580000),
                    ('lazada', 'Laneige Lip Sleeping Mask 20g', 'https://s.lazada.vn/beauty181', 350000),
                ],
                'mat-na-dat-set-innisfree': [
                    ('shopee', 'Innisfree Super Volcanic Pore Clay Mask 100ml', 'https://shope.ee/beauty190', 280000),
                    ('tiki', 'Innisfree Volcanic Color Clay Mask 70ml', 'https://tiki.vn/beauty191', 250000),
                ],
            }
            for seg in beauty.segments:
                for z in seg.zones:
                    for p in z.parts:
                        if p.slug in beauty_products:
                            for net, pname, url, price in beauty_products[p.slug]:
                                al = AffiliateLink(part_id=p.id, network=net, product_name=pname,
                                    url=url, price=price, clicks=random.randint(20, 800),
                                    conversions=random.randint(1, 40),
                                    image_url=f"https://placehold.co/400x300/e84393/fff?text={pname.replace(' ','+')[:25]}")
                                db.session.add(al)
                                seeded += 1

    # ── Tech products ──
    tech = Vertical.query.filter_by(slug='tech').first()
    if tech:
        existing = AffiliateLink.query.join(Part).join(Zone).join(Segment).join(Vertical).filter(Vertical.slug == 'tech').count()
        if existing:
            print(f'[SKIP] Tech already has {existing} affiliate links')
        else:
            print('[+] Seeding Tech affiliate links...')
            tech_products = {
                'camera-chinh': [
                    ('shopee', 'Samsung Galaxy S24 Ultra 200MP', 'https://shope.ee/tech001', 31990000),
                    ('lazada', 'iPhone 15 Pro Max 48MP', 'https://s.lazada.vn/tech002', 34990000),
                    ('tiki', 'Xiaomi 14 Ultra Leica 50MP', 'https://tiki.vn/tech003', 23990000),
                ],
                'camera-goc-rong': [
                    ('shopee', 'Google Pixel 8 Pro Ultrawide', 'https://shope.ee/tech010', 22990000),
                    ('lazada', 'Samsung Galaxy S24+ Ultrawide 12MP', 'https://s.lazada.vn/tech011', 25990000),
                ],
                'camera-zoom': [
                    ('shopee', 'Samsung Galaxy S24 Ultra Zoom 5x', 'https://shope.ee/tech020', 31990000),
                    ('tiki', 'iPhone 15 Pro Max Telephoto 5x', 'https://tiki.vn/tech021', 34990000),
                ],
                'man-hinh-oled': [
                    ('shopee', 'Samsung Galaxy A55 OLED 120Hz', 'https://shope.ee/tech030', 9990000),
                    ('lazada', 'OPPO Reno 11 OLED 120Hz', 'https://s.lazada.vn/tech031', 10490000),
                ],
                'man-hinh-amoled': [
                    ('shopee', 'Samsung Galaxy S24 Ultra Dynamic AMOLED 2X', 'https://shope.ee/tech040', 31990000),
                    ('lazada', 'OnePlus 12 LTPO AMOLED 120Hz', 'https://s.lazada.vn/tech041', 19990000),
                ],
                'kinh-cuong-luc': [
                    ('shopee', 'Kính cường lực Nillkin iPhone 15 Pro Max', 'https://shope.ee/tech050', 89000),
                    ('lazada', 'Kính cường lực Spigen Samsung S24 Ultra', 'https://s.lazada.vn/tech051', 120000),
                    ('tiki', 'Kính cường lực ZAGG Glass XTR3 iPhone', 'https://tiki.vn/tech052', 350000),
                ],
                'tan-so-quet-120hz': [
                    ('shopee', 'Redmi Note 13 Pro 120Hz AMOLED', 'https://shope.ee/tech060', 6990000),
                    ('lazada', 'Samsung Galaxy A35 120Hz Super AMOLED', 'https://s.lazada.vn/tech061', 8490000),
                ],
                'snapdragon-8-gen-3': [
                    ('shopee', 'Samsung Galaxy S24 Ultra Snapdragon 8 Gen 3', 'https://shope.ee/tech070', 31990000),
                    ('lazada', 'OnePlus 12 Snapdragon 8 Gen 3', 'https://s.lazada.vn/tech071', 19990000),
                    ('tiki', 'Xiaomi 14 Pro Snapdragon 8 Gen 3', 'https://tiki.vn/tech072', 18990000),
                ],
                'apple-a17-pro': [
                    ('shopee', 'iPhone 15 Pro 256GB', 'https://shope.ee/tech080', 28990000),
                    ('tiki', 'iPhone 15 Pro Max 256GB', 'https://tiki.vn/tech081', 34990000),
                ],
                'dimensity-9300': [
                    ('shopee', 'vivo X100 Pro Dimensity 9300', 'https://shope.ee/tech090', 19990000),
                    ('lazada', 'OPPO Find X7 Ultra Dimensity 9300', 'https://s.lazada.vn/tech091', 24990000),
                ],
                'pin-lithium-polymer': [
                    ('shopee', 'Samsung Galaxy M55 5000mAh', 'https://shope.ee/tech100', 8990000),
                    ('lazada', 'Xiaomi Redmi Note 13 5000mAh', 'https://s.lazada.vn/tech101', 4990000),
                ],
                'sac-nhanh-120w': [
                    ('shopee', 'Xiaomi 14 120W HyperCharge', 'https://shope.ee/tech110', 17990000),
                    ('lazada', 'Bộ sạc nhanh Xiaomi 120W GaN chính hãng', 'https://s.lazada.vn/tech111', 450000),
                    ('tiki', 'Bộ sạc OPPO SuperVOOC 100W', 'https://tiki.vn/tech112', 380000),
                ],
                'sac-khong-day-qi2': [
                    ('shopee', 'Apple MagSafe Charger 15W', 'https://shope.ee/tech120', 950000),
                    ('lazada', 'Anker MagGo Qi2 15W', 'https://s.lazada.vn/tech121', 650000),
                    ('tiki', 'Belkin BoostCharge Qi2 15W', 'https://tiki.vn/tech122', 750000),
                ],
                'pin-du-phong-20000mah': [
                    ('shopee', 'Anker PowerCore 20000mAh 65W', 'https://shope.ee/tech130', 890000),
                    ('lazada', 'Xiaomi Power Bank 20000mAh 50W', 'https://s.lazada.vn/tech131', 450000),
                    ('tiki', 'Baseus Blade 20000mAh 100W', 'https://tiki.vn/tech132', 1250000),
                ],
                'ram-lpddr5x': [
                    ('shopee', 'Samsung Galaxy S24 Ultra 12GB LPDDR5X', 'https://shope.ee/tech140', 31990000),
                    ('lazada', 'OnePlus 12 16GB LPDDR5X', 'https://s.lazada.vn/tech141', 22990000),
                ],
                'bo-nho-ufs-4': [
                    ('shopee', 'Samsung Galaxy S24 Ultra 512GB UFS 4.0', 'https://shope.ee/tech150', 37990000),
                    ('tiki', 'iPhone 15 Pro Max 1TB', 'https://tiki.vn/tech151', 46990000),
                ],
                'the-nho-microsd': [
                    ('shopee', 'Samsung EVO Plus 256GB A2 U3', 'https://shope.ee/tech160', 350000),
                    ('lazada', 'SanDisk Extreme 256GB A2 U3', 'https://s.lazada.vn/tech161', 380000),
                    ('tiki', 'Kingston Canvas Go Plus 128GB A2', 'https://tiki.vn/tech162', 250000),
                ],
                'op-lung-silicon': [
                    ('shopee', 'Ốp silicon Apple MagSafe iPhone 15 Pro', 'https://shope.ee/tech170', 1290000),
                    ('lazada', 'Ốp Spigen Liquid Air Samsung S24 Ultra', 'https://s.lazada.vn/tech171', 350000),
                    ('tiki', 'Ốp UAG Civilian iPhone 15 Pro Max', 'https://tiki.vn/tech172', 890000),
                ],
                'khung-vien-titanium': [
                    ('shopee', 'iPhone 15 Pro Max Titanium 256GB', 'https://shope.ee/tech180', 34990000),
                    ('tiki', 'Samsung Galaxy S24 Ultra Titanium 256GB', 'https://tiki.vn/tech181', 31990000),
                ],
                'kinh-lung-ceramic': [
                    ('shopee', 'Samsung Galaxy S24 Ultra Gorilla Armor', 'https://shope.ee/tech190', 31990000),
                    ('lazada', 'iPhone 15 Pro Ceramic Shield', 'https://s.lazada.vn/tech191', 28990000),
                ],
            }
            for seg in tech.segments:
                for z in seg.zones:
                    for p in z.parts:
                        if p.slug in tech_products:
                            for net, pname, url, price in tech_products[p.slug]:
                                al = AffiliateLink(part_id=p.id, network=net, product_name=pname,
                                    url=url, price=price, clicks=random.randint(30, 1200),
                                    conversions=random.randint(2, 60),
                                    image_url=f"https://placehold.co/400x300/6c5ce7/fff?text={pname.replace(' ','+')[:25]}")
                                db.session.add(al)
                                seeded += 1

    db.session.commit()
    beauty_count = AffiliateLink.query.join(Part).join(Zone).join(Segment).join(Vertical).filter(Vertical.slug == 'beauty').count() if beauty else 0
    tech_count = AffiliateLink.query.join(Part).join(Zone).join(Segment).join(Vertical).filter(Vertical.slug == 'tech').count() if tech else 0
    print(f'✅ Beauty+Tech products seeded: Beauty={beauty_count}, Tech={tech_count}')


# =============================================
# SPORT VERTICAL
# =============================================

def seed_sport():
    """Seed Sport vertical data for running, gym, football, cycling, swimming, nutrition"""

    # Check if Sport already exists
    sport_vertical = Vertical.query.filter_by(slug='sport').first()
    if sport_vertical:
        print('[SKIP] Sport vertical already exists')
        return

    print('[+] Seeding Sport vertical...')
    sport = Vertical(
        name='Sport',
        slug='sport',
        icon='⚽',
        color='#00b894',
        description='Thể thao & Fitness — Giày chạy, đồ gym, dinh dưỡng thể thao, thiết bị tập luyện',
        status='live',
        style='sport',
        template='general',
        default_mode='light'
    )
    db.session.add(sport)
    db.session.flush()

    # Segments (6 bộ môn)
    segments_data = [
        ('Running', 'running', '🏃', 'Chạy bộ — Giày chạy, đồ chạy, đồng hồ GPS, dinh dưỡng marathon'),
        ('Gym & Fitness', 'gym-fitness', '💪', 'Tập gym — Máy tập, quần áo, whey protein, phụ kiện'),
        ('Football', 'football', '⚽', 'Bóng đá — Giày đá bóng, quần áo, bóng, phụ kiện sân cỏ'),
        ('Cycling', 'cycling', '🚴', 'Đạp xe thể thao — Xe đạp road/MTB, mũ bảo hiểm, phụ kiện'),
        ('Swimming', 'swimming', '🏊', 'Bơi lội — Đồ bơi, kính bơi, mũ bơi, phụ kiện bể bơi'),
        ('Nutrition', 'nutrition', '🥗', 'Dinh dưỡng thể thao — Whey, BCAA, creatine, pre-workout'),
    ]

    segments = {}
    for i, (name, slug, icon, desc) in enumerate(segments_data):
        s = Segment(vertical_id=sport.id, name=name, slug=slug, icon=icon, description=desc, order=i)
        db.session.add(s)
        db.session.flush()
        segments[slug] = s

    # ── Zones for Running segment (6 zones) ──
    running = segments['running']
    running_zones_data = [
        ('Giày chạy', 'giay-chay', '👟', '#4fc3f7', 'Giày chạy bộ — Nike, Adidas, ASICS, Hoka, New Balance'),
        ('Đồ chạy', 'do-chay', '🩳', '#81c784', 'Quần áo chạy bộ — Áo singlet, quần short, compression'),
        ('Đồng hồ GPS', 'dong-ho-gps', '⌚', '#ba68c8', 'Đồng hồ GPS — Garmin, COROS, Apple Watch, Suunto'),
        ('Phụ kiện chạy', 'phu-kien-chay', '🎧', '#ffb74d', 'Đai chạy, bình nước, tai nghe, arm band'),
        ('Dinh dưỡng chạy', 'dinh-duong-chay', '🥤', '#ff8a65', 'Gel năng lượng, electrolyte, energy bar'),
        ('Sự kiện & Giải', 'su-kien-giai', '🏅', '#4db6ac', 'Marathon, half marathon, fun run, trail running'),
    ]

    running_zones = {}
    for i, (name, slug, icon, color, desc) in enumerate(running_zones_data):
        z = Zone(segment_id=running.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
        db.session.add(z)
        db.session.flush()
        running_zones[slug] = z

    # --- Parts for Giày chạy zone (4 products) ---
    giay_chay_zone = running_zones['giay-chay']
    parts_giay_chay = [
        {
            'name_vi': 'Nike Pegasus 41', 'name_en': 'Nike Pegasus 41',
            'slug': 'nike-pegasus-41',
            'description': 'Giày chạy bộ đa năng hàng đầu Nike, đệm React foam + Zoom Air, phù hợp mọi cự ly.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Nike,Pegasus,giày chạy,running,React,Zoom Air',
        },
        {
            'name_vi': 'ASICS Gel-Nimbus 26', 'name_en': 'ASICS Gel-Nimbus 26',
            'slug': 'asics-gel-nimbus-26',
            'description': 'Giày chạy êm nhất của ASICS, công nghệ FF BLAST PLUS ECO + PureGEL, lý tưởng cho long run.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'ASICS,Gel-Nimbus,giày chạy,running,cushion,marathon',
        },
        {
            'name_vi': 'Hoka Clifton 9', 'name_en': 'Hoka Clifton 9',
            'slug': 'hoka-clifton-9',
            'description': 'Giày chạy siêu nhẹ Hoka, đệm dày max-cushion nhưng chỉ nặng 248g, meta-rocker êm ái.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Hoka,Clifton,giày chạy,running,max-cushion,nhẹ',
        },
        {
            'name_vi': 'Nike Vaporfly 3', 'name_en': 'Nike Vaporfly 3',
            'slug': 'nike-vaporfly-3',
            'description': 'Giày chạy thi đấu carbon plate, ZoomX foam, phá kỷ lục marathon, dành cho race day.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Nike,Vaporfly,carbon plate,giày đua,marathon,racing',
        },
    ]
    for i, p_data in enumerate(parts_giay_chay):
        p = Part(
            zone_id=giay_chay_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Đồng hồ GPS zone (3 products) ---
    gps_zone = running_zones['dong-ho-gps']
    parts_gps = [
        {
            'name_vi': 'Garmin Forerunner 265', 'name_en': 'Garmin Forerunner 265',
            'slug': 'garmin-forerunner-265',
            'description': 'Đồng hồ GPS chạy bộ AMOLED, Training Readiness, Race Predictor, pin 13 ngày.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Garmin,Forerunner,GPS,đồng hồ,chạy bộ,running',
        },
        {
            'name_vi': 'COROS PACE 3', 'name_en': 'COROS PACE 3',
            'slug': 'coros-pace-3',
            'description': 'Đồng hồ GPS siêu nhẹ 39g, pin 24 ngày, GPS dual-frequency, giá tốt nhất phân khúc.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'COROS,PACE 3,GPS,đồng hồ,running,siêu nhẹ',
        },
        {
            'name_vi': 'Apple Watch Ultra 2', 'name_en': 'Apple Watch Ultra 2',
            'slug': 'apple-watch-ultra-2',
            'description': 'Smartwatch cao cấp nhất Apple, GPS dual-frequency, Precision Finding, 36h pin.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Apple Watch,Ultra,GPS,smartwatch,chạy bộ,bơi lội',
        },
    ]
    for i, p_data in enumerate(parts_gps):
        p = Part(
            zone_id=gps_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Đồ chạy zone (3 products) ---
    do_chay_zone = running_zones['do-chay']
    parts_do_chay = [
        {
            'name_vi': 'Áo chạy Nike Dri-FIT', 'name_en': 'Nike Dri-FIT Running Singlet',
            'slug': 'ao-chay-nike-dri-fit',
            'description': 'Áo singlet chạy bộ Nike Dri-FIT, thoáng khí, nhanh khô, nhẹ chỉ 90g.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Nike,Dri-FIT,áo chạy,singlet,running,thoáng khí',
        },
        {
            'name_vi': 'Quần short chạy 2-in-1', 'name_en': '2-in-1 Running Shorts',
            'slug': 'quan-short-chay-2-in-1',
            'description': 'Quần short chạy 2 lớp, lớp ngoài nhẹ + lớp compression bên trong, túi đựng điện thoại.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'quần short,2-in-1,running,compression,chạy bộ',
        },
        {
            'name_vi': 'Tất chạy Balega Hidden Comfort', 'name_en': 'Balega Hidden Comfort Socks',
            'slug': 'tat-chay-balega',
            'description': 'Tất chạy bộ Balega chống phồng rộp, đệm gót, thoáng khí, best-seller #1 running socks.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Balega,tất chạy,running socks,chống phồng rộp,marathon',
        },
    ]
    for i, p_data in enumerate(parts_do_chay):
        p = Part(
            zone_id=do_chay_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Dinh dưỡng chạy zone (3 products) ---
    dd_chay_zone = running_zones['dinh-duong-chay']
    parts_dd_chay = [
        {
            'name_vi': 'Gel năng lượng GU', 'name_en': 'GU Energy Gel',
            'slug': 'gel-nang-luong-gu',
            'description': 'Gel năng lượng GU chứa 100 calo + caffeine + electrolyte, tiếp năng lượng nhanh khi chạy.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'GU,gel năng lượng,energy gel,marathon,running,dinh dưỡng',
        },
        {
            'name_vi': 'Viên muối điện giải SaltStick', 'name_en': 'SaltStick Electrolyte Caps',
            'slug': 'vien-muoi-dien-giai-saltstick',
            'description': 'Viên bù điện giải SaltStick chứa Na, K, Mg, Ca — chống chuột rút khi chạy dài.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'SaltStick,điện giải,electrolyte,chuột rút,marathon,running',
        },
        {
            'name_vi': 'Bột điện giải Nuun Sport', 'name_en': 'Nuun Sport Electrolyte Tablets',
            'slug': 'bot-dien-giai-nuun',
            'description': 'Viên sủi điện giải Nuun Sport không đường, bù nước nhanh, nhiều vị trái cây.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Nuun,điện giải,electrolyte,hydration,running,không đường',
        },
    ]
    for i, p_data in enumerate(parts_dd_chay):
        p = Part(
            zone_id=dd_chay_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # ── Zones for Gym & Fitness segment (6 zones) ──
    gym = segments['gym-fitness']
    gym_zones_data = [
        ('Whey Protein', 'whey-protein', '🥛', '#4fc3f7', 'Whey concentrate, isolate, hydrolyzed, plant-based'),
        ('Creatine', 'creatine', '💊', '#ba68c8', 'Creatine monohydrate, HCL, buffered, micronized'),
        ('Máy tập', 'may-tap', '🏋️', '#81c784', 'Máy chạy, xe đạp tập, tạ, bench press, dây kháng lực'),
        ('Quần áo gym', 'quan-ao-gym', '👕', '#ffb74d', 'Quần short, áo tank, legging, găng tay, đai lưng'),
        ('Pre-Workout', 'pre-workout', '⚡', '#ff8a65', 'Pre-workout, caffeine, beta-alanine, citrulline'),
        ('Phụ kiện gym', 'phu-kien-gym', '🧤', '#4db6ac', 'Găng tay, đai lưng, dây kéo, bình lắc, foam roller'),
    ]

    gym_zones = {}
    for i, (name, slug, icon, color, desc) in enumerate(gym_zones_data):
        z = Zone(segment_id=gym.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
        db.session.add(z)
        db.session.flush()
        gym_zones[slug] = z

    # --- Parts for Whey Protein zone (3 products) ---
    whey_zone = gym_zones['whey-protein']
    parts_whey = [
        {
            'name_vi': 'Whey Protein Isolate', 'name_en': 'Whey Protein Isolate',
            'slug': 'whey-protein-isolate',
            'description': 'Whey Isolate 90%+ protein, ít lactose, ít fat, hấp thụ nhanh, phù hợp giảm cân.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'whey,protein,isolate,WPI,tập gym,tăng cơ',
        },
        {
            'name_vi': 'Optimum Nutrition Gold Standard', 'name_en': 'ON Gold Standard Whey',
            'slug': 'on-gold-standard-whey',
            'description': 'Whey protein bán chạy nhất thế giới, blend WPI + WPC, 24g protein/scoop, 120+ calo.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'Optimum Nutrition,Gold Standard,whey,protein,gym,tăng cơ',
        },
        {
            'name_vi': 'Mass Gainer tăng cân', 'name_en': 'Serious Mass Gainer',
            'slug': 'mass-gainer-tang-can',
            'description': 'Mass Gainer 1200+ calo/serving, dành cho người gầy muốn tăng cân tăng cơ nhanh.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'mass gainer,tăng cân,tăng cơ,bulking,protein,gym',
        },
    ]
    for i, p_data in enumerate(parts_whey):
        p = Part(
            zone_id=whey_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Creatine zone (3 products) ---
    creatine_zone = gym_zones['creatine']
    parts_creatine = [
        {
            'name_vi': 'Creatine Monohydrate', 'name_en': 'Creatine Monohydrate',
            'slug': 'creatine-monohydrate',
            'description': 'Creatine dạng cơ bản nhất, nghiên cứu nhiều nhất, hiệu quả tăng sức mạnh đã chứng minh.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'creatine,monohydrate,tăng sức mạnh,supplement,gym',
        },
        {
            'name_vi': 'Creatine HCL', 'name_en': 'Creatine HCL',
            'slug': 'creatine-hcl',
            'description': 'Creatine HCL tan nhanh, hấp thụ tốt hơn, liều thấp hơn monohydrate, ít đầy bụng.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'creatine,HCL,supplement,tập gym,tăng sức mạnh',
        },
    ]
    for i, p_data in enumerate(parts_creatine):
        p = Part(
            zone_id=creatine_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # --- Parts for Máy tập zone (3 products) ---
    may_tap_zone = gym_zones['may-tap']
    parts_may_tap = [
        {
            'name_vi': 'Máy chạy bộ điện', 'name_en': 'Electric Treadmill',
            'slug': 'may-chay-bo-dien',
            'description': 'Máy chạy bộ điện tại nhà, tốc độ 0-16km/h, nghiêng tự động, đo nhịp tim.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'máy chạy bộ,treadmill,cardio,tập tại nhà,gym',
        },
        {
            'name_vi': 'Tạ đơn điều chỉnh', 'name_en': 'Adjustable Dumbbell',
            'slug': 'ta-don-dieu-chinh',
            'description': 'Tạ đơn điều chỉnh 2-24kg, thay đổi trọng lượng nhanh, tiết kiệm không gian.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'tạ đơn,dumbbell,adjustable,home gym,tập tại nhà',
        },
        {
            'name_vi': 'Dây kháng lực', 'name_en': 'Resistance Bands Set',
            'slug': 'day-khang-luc',
            'description': 'Bộ dây kháng lực 5 mức độ, tập toàn thân tại nhà, gọn nhẹ mang đi du lịch.',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>''',
            'tags': 'dây kháng lực,resistance bands,home gym,tập tại nhà,gọn nhẹ',
        },
    ]
    for i, p_data in enumerate(parts_may_tap):
        p = Part(
            zone_id=may_tap_zone.id,
            name_vi=p_data['name_vi'], name_en=p_data['name_en'],
            slug=p_data['slug'], description=p_data['description'],
            content=p_data['content'], tags=p_data.get('tags', ''),
            order=i
        )
        db.session.add(p)
        db.session.flush()

    # ── Zones for Football segment (4 zones) ──
    football = segments['football']
    football_zones_data = [
        ('Giày đá bóng', 'giay-da-bong', '👟', '#4fc3f7', 'Giày đá bóng — Nike, Adidas, Puma, sân cỏ nhân tạo/tự nhiên'),
        ('Quần áo bóng đá', 'quan-ao-bong-da', '👕', '#81c784', 'Áo đấu, quần short, tất, găng tay thủ môn'),
        ('Bóng thi đấu', 'bong-thi-dau', '⚽', '#ffb74d', 'Bóng FIFA Quality, bóng tập, bóng mini'),
        ('Phụ kiện bóng đá', 'phu-kien-bong-da', '🧤', '#ff8a65', 'Bảo vệ ống đồng, băng keo, bình nước, túi đựng'),
    ]
    for i, (name, slug, icon, color, desc) in enumerate(football_zones_data):
        z = Zone(segment_id=football.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
        db.session.add(z)
        db.session.flush()

    # ── Zones for Cycling segment (4 zones) ──
    cycling = segments['cycling']
    cycling_zones_data = [
        ('Xe đạp thể thao', 'xe-dap-the-thao', '🚲', '#4fc3f7', 'Road bike, MTB, gravel, touring, fixie'),
        ('Mũ bảo hiểm', 'mu-bao-hiem', '⛑️', '#ba68c8', 'Mũ road, MTB, aero, MIPS, full-face'),
        ('Quần áo đạp xe', 'quan-ao-dap-xe', '🩱', '#81c784', 'Jersey, bib short, áo gió, găng tay'),
        ('Phụ kiện đạp xe', 'phu-kien-dap-xe', '🔧', '#ffb74d', 'Đèn, bơm, khóa, túi yên, đồng hồ cycling'),
    ]
    for i, (name, slug, icon, color, desc) in enumerate(cycling_zones_data):
        z = Zone(segment_id=cycling.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
        db.session.add(z)
        db.session.flush()

    # ── Zones for Swimming segment (4 zones) ──
    swimming = segments['swimming']
    swimming_zones_data = [
        ('Đồ bơi', 'do-boi', '🩱', '#4fc3f7', 'Quần bơi, áo bơi, bikini, đồ bơi thi đấu'),
        ('Kính bơi', 'kinh-boi', '🥽', '#ba68c8', 'Kính bơi tập, thi đấu, open water, cận'),
        ('Mũ bơi', 'mu-boi', '🧢', '#81c784', 'Mũ bơi silicone, latex, vải, mũ thi đấu'),
        ('Phụ kiện bơi', 'phu-kien-boi', '🏊', '#ffb74d', 'Phao tập, paddle, chân vịt, pull buoy'),
    ]
    for i, (name, slug, icon, color, desc) in enumerate(swimming_zones_data):
        z = Zone(segment_id=swimming.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
        db.session.add(z)
        db.session.flush()

    # ── Zones for Nutrition segment (4 zones) ──
    nutrition = segments['nutrition']
    nutrition_zones_data = [
        ('Protein', 'protein', '🥛', '#4fc3f7', 'Whey, casein, plant-based, protein bar'),
        ('BCAA & EAA', 'bcaa-eaa', '💧', '#ba68c8', 'BCAA 2:1:1, EAA, recovery drink'),
        ('Vitamin & Khoáng', 'vitamin-khoang', '💊', '#81c784', 'Multivitamin, omega-3, vitamin D, ZMA'),
        ('Thực phẩm healthy', 'thuc-pham-healthy', '🥑', '#ffb74d', 'Granola, yến mạch, hạt mix, protein snack'),
    ]
    for i, (name, slug, icon, color, desc) in enumerate(nutrition_zones_data):
        z = Zone(segment_id=nutrition.id, name=name, slug=slug, icon=icon, color=color, description=desc, order=i)
        db.session.add(z)
        db.session.flush()

    db.session.commit()
    print('✅ Sport vertical seeded with zones and parts!')


def seed_sport_articles():
    """Seed Sport articles - 3-tier content"""
    from models import Article

    # Check if Sport articles exist
    if Article.query.filter_by(vertical_slug='sport', tier='nganh').first():
        print('[SKIP] Sport articles already exist')
        return

    print('[+] Seeding Sport articles...')
    articles = [
        # === TIER 1: NGANH (Industry - Sport market) ===
        {
            'title': 'Thị trường thể thao Việt Nam 2025 — Running, Gym & Fitness bùng nổ',
            'slug': 'thi-truong-the-thao-viet-nam-2025',
            'tier': 'nganh',
            'category': 'thi-truong',
            'tags': 'thị trường,thể thao,running,gym,fitness,Việt Nam,2025',
            'excerpt': 'Phân tích toàn cảnh thị trường thể thao Việt Nam: running community tăng 300%, chuỗi gym mở rộng, chi tiêu trung bình 5-15 triệu/năm.',
            'reading_time': 8,
            'vertical_slug': 'sport',
            'image_url': 'https://placehold.co/800x450/00b894/ffffff?text=Sport+Market+2025',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
        {
            'title': 'Hướng dẫn chọn giày chạy bộ — Từ A đến Z cho người mới',
            'slug': 'huong-dan-chon-giay-chay-bo',
            'tier': 'nganh',
            'category': 'kien-thuc-chung',
            'tags': 'giày chạy,running,chọn giày,foot type,pronation,Nike,ASICS',
            'excerpt': 'Cách chọn giày chạy phù hợp: phân biệt neutral vs stability, đo foot type, chọn đệm mỏng hay dày, budget hợp lý.',
            'reading_time': 10,
            'vertical_slug': 'sport',
            'image_url': 'https://placehold.co/800x450/2d3436/ffffff?text=Running+Shoes+Guide',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
        {
            'title': 'Dinh dưỡng thể thao cơ bản — Protein, Carb, Fat cho người tập',
            'slug': 'dinh-duong-the-thao-co-ban',
            'tier': 'nganh',
            'category': 'dinh-duong',
            'tags': 'dinh dưỡng,protein,carb,fat,macro,TDEE,tập gym,chạy bộ',
            'excerpt': 'Hướng dẫn dinh dưỡng cho người tập thể thao: tính TDEE, chia macro, timing ăn uống trước/sau tập.',
            'reading_time': 9,
            'vertical_slug': 'sport',
            'image_url': 'https://placehold.co/800x450/6c5ce7/ffffff?text=Sport+Nutrition',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },

        # === TIER 2: CHUNG (General - Systems/Methods) ===
        {
            'title': 'Chương trình tập gym cho người mới — 12 tuần từ zero đến hero',
            'slug': 'chuong-trinh-tap-gym-nguoi-moi-12-tuan',
            'tier': 'chung',
            'category': 'chuong-trinh-tap',
            'tags': 'gym,người mới,chương trình tập,12 tuần,full body,PPL',
            'excerpt': 'Lộ trình tập gym 12 tuần cho người mới: 4 tuần full body → 4 tuần upper/lower → 4 tuần PPL. Bài tập, số set, rep chi tiết.',
            'reading_time': 12,
            'vertical_slug': 'sport',
            'image_url': 'https://placehold.co/800x450/e17055/ffffff?text=Gym+12+Weeks',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
        {
            'title': 'Kế hoạch chạy Half Marathon (21km) cho người mới — 16 tuần',
            'slug': 'ke-hoach-chay-half-marathon-16-tuan',
            'tier': 'chung',
            'category': 'ke-hoach-tap',
            'tags': 'half marathon,21km,kế hoạch chạy,training plan,running,16 tuần',
            'excerpt': 'Training plan chạy Half Marathon 16 tuần cho người mới: từ chạy 3km đến hoàn thành 21km. Phân bổ easy run, tempo, long run.',
            'reading_time': 11,
            'vertical_slug': 'sport',
            'image_url': 'https://placehold.co/800x450/0984e3/ffffff?text=Half+Marathon+Plan',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
        {
            'title': 'Phòng chống chấn thương thể thao — Warm-up, Cool-down & Recovery',
            'slug': 'phong-chong-chan-thuong-the-thao',
            'tier': 'chung',
            'category': 'suc-khoe',
            'tags': 'chấn thương,warm-up,cool-down,recovery,stretching,foam roller',
            'excerpt': 'Hướng dẫn phòng chống chấn thương: quy trình warm-up 10 phút, cool-down, stretching, foam rolling, khi nào cần nghỉ.',
            'reading_time': 8,
            'vertical_slug': 'sport',
            'image_url': 'https://placehold.co/800x450/00cec9/ffffff?text=Injury+Prevention',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },

        # === TIER 3: CHI-TIET (Detailed product reviews) ===
        {
            'title': 'Nike Pegasus 41 vs ASICS Nimbus 26 vs Hoka Clifton 9 — So sánh chi tiết',
            'slug': 'nike-pegasus-vs-asics-nimbus-vs-hoka-clifton',
            'tier': 'chi-tiet',
            'category': 'so-sanh',
            'tags': 'Nike Pegasus,ASICS Nimbus,Hoka Clifton,so sánh,giày chạy,review',
            'excerpt': 'So sánh 3 giày chạy bộ phổ biến nhất: Pegasus (đa năng), Nimbus (êm nhất), Clifton (nhẹ nhất). Nên chọn đôi nào?',
            'reading_time': 10,
            'vertical_slug': 'sport',
            'image_url': 'https://placehold.co/800x450/2d3436/00b894?text=Pegasus+vs+Nimbus+vs+Clifton',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
        {
            'title': 'Review Garmin Forerunner 265 — Đồng hồ chạy bộ tốt nhất 2025',
            'slug': 'review-garmin-forerunner-265',
            'tier': 'chi-tiet',
            'category': 'review',
            'tags': 'Garmin,Forerunner 265,đồng hồ GPS,review,running,AMOLED',
            'excerpt': 'Review chi tiết Garmin Forerunner 265 sau 6 tháng sử dụng: GPS chính xác, AMOLED đẹp, Training Readiness hữu ích, pin 13 ngày.',
            'reading_time': 9,
            'vertical_slug': 'sport',
            'image_url': 'https://placehold.co/800x450/636e72/00b894?text=Garmin+FR265+Review',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
        {
            'title': 'Review Optimum Nutrition Gold Standard Whey — Whey #1 thế giới có xứng đáng?',
            'slug': 'review-on-gold-standard-whey',
            'tier': 'chi-tiet',
            'category': 'review',
            'tags': 'ON,Gold Standard,whey protein,review,gym,supplement,tăng cơ',
            'excerpt': 'Review chi tiết ON Gold Standard Whey: 24g protein/scoop, vị ngon, tan tốt, giá hợp lý. So sánh với MuscleTech, MyProtein.',
            'reading_time': 7,
            'vertical_slug': 'sport',
            'image_url': 'https://placehold.co/800x450/fdcb6e/2d3436?text=ON+Gold+Standard+Review',
            'content': '''<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'''
        },
    ]

    for a_data in articles:
        a = Article(
            title=a_data['title'],
            slug=a_data['slug'],
            tier=a_data['tier'],
            category=a_data['category'],
            tags=a_data['tags'],
            excerpt=a_data['excerpt'],
            reading_time=a_data['reading_time'],
            vertical_slug=a_data['vertical_slug'],
            content=a_data['content'],
            image_url=a_data.get('image_url', ''),
            status='published',
            ai_generated=False
        )
        db.session.add(a)

    db.session.commit()
    print(f'✅ Sport articles seeded: {len(articles)} articles')


def seed_products_sport():
    """Seed affiliate product links for Sport vertical"""
    from models import db, Vertical, Segment, Zone, Part, AffiliateLink
    import random

    sport = Vertical.query.filter_by(slug='sport').first()
    if not sport:
        print('[SKIP] Sport vertical not found — run seed_sport() first')
        return

    existing = AffiliateLink.query.join(Part).join(Zone).join(Segment).join(Vertical).filter(Vertical.slug == 'sport').count()
    if existing:
        print(f'[SKIP] Sport already has {existing} affiliate links')
        return

    print('[+] Seeding Sport affiliate links...')
    sport_products = {
        # Running — Giày chạy
        'nike-pegasus-41': [
            ('shopee', 'Nike Pegasus 41 Nam — Black/White', 'https://shope.ee/sport001', 3290000, 'https://placehold.co/400x300/2d3436/ffffff?text=Pegasus+41'),
            ('lazada', 'Nike Pegasus 41 Nữ — Pink/White', 'https://s.lazada.vn/sport002', 3290000, 'https://placehold.co/400x300/e84393/ffffff?text=Pegasus+41+W'),
            ('tiki', 'Nike Pegasus 41 — Thunder Blue', 'https://tiki.vn/sport003', 3490000, 'https://placehold.co/400x300/0984e3/ffffff?text=Pegasus+41'),
        ],
        'asics-gel-nimbus-26': [
            ('shopee', 'ASICS Gel-Nimbus 26 Nam — Black/Blue', 'https://shope.ee/sport010', 4190000, 'https://placehold.co/400x300/2d3436/4fc3f7?text=Nimbus+26'),
            ('lazada', 'ASICS Gel-Nimbus 26 Nữ — Lavender', 'https://s.lazada.vn/sport011', 4190000, 'https://placehold.co/400x300/a29bfe/ffffff?text=Nimbus+26+W'),
        ],
        'hoka-clifton-9': [
            ('shopee', 'Hoka Clifton 9 Nam — Black/White', 'https://shope.ee/sport020', 3690000, 'https://placehold.co/400x300/2d3436/ffffff?text=Clifton+9'),
            ('lazada', 'Hoka Clifton 9 Nữ — Airy Blue', 'https://s.lazada.vn/sport021', 3690000, 'https://placehold.co/400x300/74b9ff/ffffff?text=Clifton+9+W'),
            ('tiki', 'Hoka Clifton 9 Wide — All Black', 'https://tiki.vn/sport022', 3890000, 'https://placehold.co/400x300/636e72/ffffff?text=Clifton+9+Wide'),
        ],
        'nike-vaporfly-3': [
            ('shopee', 'Nike Vaporfly 3 — Volt/Black', 'https://shope.ee/sport030', 5690000, 'https://placehold.co/400x300/00b894/2d3436?text=Vaporfly+3'),
            ('lazada', 'Nike Vaporfly 3 — White/Bright Crimson', 'https://s.lazada.vn/sport031', 5890000, 'https://placehold.co/400x300/e17055/ffffff?text=Vaporfly+3'),
        ],
        # Running — Đồng hồ GPS
        'garmin-forerunner-265': [
            ('shopee', 'Garmin Forerunner 265 Black', 'https://shope.ee/sport040', 10990000, 'https://placehold.co/400x300/2d3436/00b894?text=FR265'),
            ('lazada', 'Garmin Forerunner 265S Whitestone', 'https://s.lazada.vn/sport041', 10990000, 'https://placehold.co/400x300/dfe6e9/2d3436?text=FR265S'),
            ('tiki', 'Garmin Forerunner 265 Aqua', 'https://tiki.vn/sport042', 10990000, 'https://placehold.co/400x300/00cec9/ffffff?text=FR265+Aqua'),
        ],
        'coros-pace-3': [
            ('shopee', 'COROS PACE 3 GPS — Black Silicone', 'https://shope.ee/sport050', 5990000, 'https://placehold.co/400x300/2d3436/ffffff?text=COROS+PACE+3'),
            ('lazada', 'COROS PACE 3 GPS — White Nylon', 'https://s.lazada.vn/sport051', 5990000, 'https://placehold.co/400x300/dfe6e9/2d3436?text=COROS+PACE+3'),
        ],
        'apple-watch-ultra-2': [
            ('shopee', 'Apple Watch Ultra 2 Titanium 49mm', 'https://shope.ee/sport060', 18990000, 'https://placehold.co/400x300/636e72/ff7f50?text=AW+Ultra+2'),
            ('tiki', 'Apple Watch Ultra 2 + Alpine Loop', 'https://tiki.vn/sport061', 19990000, 'https://placehold.co/400x300/e17055/ffffff?text=AW+Ultra+2'),
        ],
        # Running — Đồ chạy
        'ao-chay-nike-dri-fit': [
            ('shopee', 'Nike Dri-FIT Miler Singlet Nam', 'https://shope.ee/sport070', 790000, 'https://placehold.co/400x300/2d3436/ffffff?text=Dri-FIT+Singlet'),
            ('lazada', 'Nike Dri-FIT ADV AeroSwift Singlet', 'https://s.lazada.vn/sport071', 1290000, 'https://placehold.co/400x300/00b894/ffffff?text=AeroSwift'),
        ],
        'quan-short-chay-2-in-1': [
            ('shopee', 'Quần short 2-in-1 Under Armour Launch', 'https://shope.ee/sport080', 890000, 'https://placehold.co/400x300/636e72/ffffff?text=UA+2in1'),
            ('lazada', 'Nike Dri-FIT Stride 2-in-1 Short', 'https://s.lazada.vn/sport081', 990000, 'https://placehold.co/400x300/2d3436/ffffff?text=Stride+2in1'),
        ],
        'tat-chay-balega': [
            ('shopee', 'Balega Hidden Comfort No Show', 'https://shope.ee/sport090', 380000, 'https://placehold.co/400x300/dfe6e9/2d3436?text=Balega+HC'),
            ('tiki', 'Balega Blister Resist No Show', 'https://tiki.vn/sport091', 350000, 'https://placehold.co/400x300/b2bec3/2d3436?text=Balega+BR'),
        ],
        # Running — Dinh dưỡng chạy
        'gel-nang-luong-gu': [
            ('shopee', 'GU Energy Gel Tri-Berry x24 gói', 'https://shope.ee/sport100', 720000, 'https://placehold.co/400x300/6c5ce7/ffffff?text=GU+Gel+x24'),
            ('lazada', 'GU Energy Gel Salted Caramel x8 gói', 'https://s.lazada.vn/sport101', 280000, 'https://placehold.co/400x300/fdcb6e/2d3436?text=GU+Caramel'),
        ],
        'vien-muoi-dien-giai-saltstick': [
            ('shopee', 'SaltStick Caps 100 viên', 'https://shope.ee/sport110', 550000, 'https://placehold.co/400x300/dfe6e9/e17055?text=SaltStick+100'),
            ('lazada', 'SaltStick Fastchews 60 viên', 'https://s.lazada.vn/sport111', 380000, 'https://placehold.co/400x300/ffeaa7/2d3436?text=SaltStick+FC'),
        ],
        'bot-dien-giai-nuun': [
            ('shopee', 'Nuun Sport Mixed Pack 4 ống', 'https://shope.ee/sport120', 450000, 'https://placehold.co/400x300/00b894/ffffff?text=Nuun+Mix'),
            ('tiki', 'Nuun Sport Citrus Fruit 10 viên', 'https://tiki.vn/sport121', 150000, 'https://placehold.co/400x300/ffeaa7/e17055?text=Nuun+Citrus'),
        ],
        # Gym — Whey Protein
        'whey-protein-isolate': [
            ('shopee', 'Rule 1 R1 Whey Isolate 5lbs', 'https://shope.ee/sport130', 1890000, 'https://placehold.co/400x300/0984e3/ffffff?text=R1+Isolate'),
            ('lazada', 'Dymatize ISO100 Hydrolyzed 5lbs', 'https://s.lazada.vn/sport131', 2290000, 'https://placehold.co/400x300/6c5ce7/ffffff?text=ISO100'),
        ],
        'on-gold-standard-whey': [
            ('shopee', 'ON Gold Standard 100% Whey 5lbs Chocolate', 'https://shope.ee/sport140', 1790000, 'https://placehold.co/400x300/fdcb6e/2d3436?text=ON+Gold+5lbs'),
            ('lazada', 'ON Gold Standard Whey 2lbs Vanilla', 'https://s.lazada.vn/sport141', 890000, 'https://placehold.co/400x300/ffeaa7/2d3436?text=ON+Gold+2lbs'),
            ('tiki', 'ON Gold Standard Whey 5lbs Cookies & Cream', 'https://tiki.vn/sport142', 1850000, 'https://placehold.co/400x300/636e72/ffffff?text=ON+Gold+C%26C'),
        ],
        'mass-gainer-tang-can': [
            ('shopee', 'ON Serious Mass 12lbs Chocolate', 'https://shope.ee/sport150', 1490000, 'https://placehold.co/400x300/e17055/ffffff?text=Serious+Mass'),
            ('lazada', 'MuscleTech Mass Tech 7lbs', 'https://s.lazada.vn/sport151', 1190000, 'https://placehold.co/400x300/d63031/ffffff?text=Mass+Tech'),
        ],
        # Gym — Creatine
        'creatine-monohydrate': [
            ('shopee', 'ON Micronized Creatine 300g', 'https://shope.ee/sport160', 350000, 'https://placehold.co/400x300/2d3436/fdcb6e?text=ON+Creatine'),
            ('lazada', 'MuscleTech Platinum Creatine 400g', 'https://s.lazada.vn/sport161', 320000, 'https://placehold.co/400x300/636e72/ffffff?text=MT+Creatine'),
            ('tiki', 'MyProtein Creatine Monohydrate 500g', 'https://tiki.vn/sport162', 380000, 'https://placehold.co/400x300/0984e3/ffffff?text=MP+Creatine'),
        ],
        'creatine-hcl': [
            ('shopee', 'Kaged Muscle C-HCl 75 servings', 'https://shope.ee/sport170', 650000, 'https://placehold.co/400x300/00b894/ffffff?text=Kaged+C-HCl'),
            ('lazada', 'MuscleTech Creactor HCl 120 servings', 'https://s.lazada.vn/sport171', 590000, 'https://placehold.co/400x300/e17055/ffffff?text=Creactor'),
        ],
        # Gym — Máy tập
        'may-chay-bo-dien': [
            ('shopee', 'Kingsport MAX-08 3.0HP', 'https://shope.ee/sport180', 12900000, 'https://placehold.co/400x300/2d3436/ffffff?text=Kingsport+MAX'),
            ('lazada', 'Elip Marathon Pro 3.5HP', 'https://s.lazada.vn/sport181', 18900000, 'https://placehold.co/400x300/636e72/ffffff?text=Elip+Pro'),
            ('tiki', 'Máy chạy Xiaomi WalkingPad R2', 'https://tiki.vn/sport182', 8900000, 'https://placehold.co/400x300/e17055/ffffff?text=WalkingPad'),
        ],
        'ta-don-dieu-chinh': [
            ('shopee', 'Bowflex SelectTech 552 Adjustable 2-24kg', 'https://shope.ee/sport190', 8900000, 'https://placehold.co/400x300/2d3436/e17055?text=Bowflex+552'),
            ('lazada', 'PowerBlock Elite 2.5-22kg', 'https://s.lazada.vn/sport191', 6900000, 'https://placehold.co/400x300/636e72/fdcb6e?text=PowerBlock'),
        ],
        'day-khang-luc': [
            ('shopee', 'Bộ dây kháng lực 5 mức Aolikes', 'https://shope.ee/sport200', 189000, 'https://placehold.co/400x300/00b894/ffffff?text=Bands+5pc'),
            ('lazada', 'Theraband CLX Resistance Band', 'https://s.lazada.vn/sport201', 450000, 'https://placehold.co/400x300/fdcb6e/2d3436?text=Theraband'),
            ('tiki', 'Bộ tube bands 11 món có tay cầm', 'https://tiki.vn/sport202', 250000, 'https://placehold.co/400x300/6c5ce7/ffffff?text=Tube+Bands'),
        ],
    }

    seeded = 0
    for seg in sport.segments:
        for z in seg.zones:
            for p in z.parts:
                if p.slug in sport_products:
                    for net, pname, url, price, img in sport_products[p.slug]:
                        al = AffiliateLink(part_id=p.id, network=net, product_name=pname,
                            url=url, price=price, image_url=img,
                            clicks=random.randint(20, 1000),
                            conversions=random.randint(1, 50))
                        db.session.add(al)
                        seeded += 1

    db.session.commit()
    sport_count = AffiliateLink.query.join(Part).join(Zone).join(Segment).join(Vertical).filter(Vertical.slug == 'sport').count()
    print(f'✅ Sport products seeded: {sport_count} affiliate links')
