from models import db, Vertical, Segment, Zone, Part, AffiliateLink

def seed():
    # Vertical: UniCar
    car = Vertical(
        name='UniCar', slug='car', icon='🚗', color='#fdcb6e',
        description='Kiến thức chi tiết về ô tô — từ tổng thể đến từng bu-lông. Tìm hiểu, sửa chữa, nâng cấp.',
        status='live'
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
            'content': '''<h2>Cao su chân phuộc là gì?</h2>
<p>Cao su chân phuộc (Shock Absorber Bushing) là chi tiết bằng cao su hoặc polyurethane, nằm ở vị trí kết nối giữa phuộc nhún với thân xe. Đây là bộ phận quan trọng trong hệ thống treo, giúp:</p>
<ul>
<li><strong>Hấp thụ rung động</strong> — Giảm truyền rung từ bánh xe lên thân xe</li>
<li><strong>Giảm tiếng ồn</strong> — Ngăn tiếng lọc cọc khi đi qua ổ gà, gờ giảm tốc</li>
<li><strong>Bảo vệ phuộc</strong> — Giảm ma sát giữa phuộc và điểm gắn trên xe</li>
</ul>

<h2>Khi nào cần thay?</h2>
<p>Cao su chân phuộc thường cần thay sau <strong>60,000 - 80,000 km</strong> hoặc khi có dấu hiệu:</p>
<ul>
<li>Nghe tiếng kêu lọc cọc khi đi qua ổ gà</li>
<li>Xe bị rung lắc nhiều hơn bình thường</li>
<li>Cao su bị nứt, rách, biến dạng khi kiểm tra trực quan</li>
<li>Phuộc bị lệch hoặc nghiêng</li>
</ul>

<h2>Chi phí thay thế</h2>
<p>Giá cao su chân phuộc dao động từ <strong>80,000 - 350,000 VNĐ/cái</strong> tùy hãng xe và chất liệu. Công thay tại garage khoảng 100,000 - 200,000 VNĐ.</p>''',
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
            'content': '''<h2>Phuộc nhún là gì?</h2>
<p>Phuộc nhún (Shock Absorber) là bộ phận giảm chấn chính trong hệ thống treo. Nó hoạt động bằng cách chuyển đổi năng lượng dao động thành nhiệt năng thông qua dầu thủy lực bên trong.</p>

<h2>Phân loại</h2>
<ul>
<li><strong>Phuộc dầu (Twin-tube)</strong> — Phổ biến, giá rẻ, phù hợp đi phố</li>
<li><strong>Phuộc gas (Monotube)</strong> — Hiệu suất cao hơn, giá đắt hơn</li>
<li><strong>Phuộc điện tử (Adaptive)</strong> — Tự điều chỉnh theo điều kiện đường</li>
</ul>

<h2>Khi nào cần thay?</h2>
<p>Thay sau <strong>80,000 - 100,000 km</strong> hoặc khi rò rỉ dầu, xe bị nhún quá nhiều sau khi qua ổ gà.</p>''',
            'oem_code': 'E4302-JD02A (Nissan), 51605-SWA-A04 (Honda)',
        },
        {
            'name_vi': 'Rotuyn', 'name_en': 'Ball Joint',
            'slug': 'rotuy',
            'description': 'Khớp cầu nối giữa đòn treo và trục xoay bánh xe, cho phép bánh xe xoay và di chuyển lên xuống.',
            'content': '''<h2>Rotuyn là gì?</h2>
<p>Rotuyn (Ball Joint) là khớp nối dạng cầu, cho phép chuyển động xoay đa hướng giữa các chi tiết trong hệ thống treo. Có 2 loại chính:</p>
<ul>
<li><strong>Rotuyn trên/dưới</strong> — Nối đòn treo với trục bánh xe</li>
<li><strong>Rotuyn lái</strong> — Nối thước lái với cam lái</li>
</ul>

<h2>Dấu hiệu hỏng</h2>
<ul>
<li>Xe bị lệch lái, tay lái nặng bất thường</li>
<li>Nghe tiếng kêu khi đánh lái hoặc đi qua gờ giảm tốc</li>
<li>Lốp xe mòn không đều</li>
</ul>''',
            'oem_code': '40160-JD00A (Nissan), 51220-SWA-A01 (Honda)',
        },
        {
            'name_vi': 'Thanh cân bằng', 'name_en': 'Stabilizer Bar',
            'slug': 'thanh-can-bang',
            'description': 'Thanh thép kết nối hai bên hệ thống treo, giúp giảm nghiêng thân xe khi vào cua.',
            'content': '''<h2>Thanh cân bằng là gì?</h2>
<p>Thanh cân bằng (Stabilizer Bar / Sway Bar) là thanh thép hình chữ U, kết nối hệ thống treo bên trái và bên phải. Khi xe vào cua, thanh cân bằng chống lại lực nghiêng, giữ xe ổn định.</p>

<h2>Các bộ phận liên quan</h2>
<ul>
<li><strong>Cao su thanh cân bằng</strong> — Bọc quanh thanh tại điểm gắn vào khung xe</li>
<li><strong>Nối thanh cân bằng (Link)</strong> — Kết nối thanh với phuộc/đòn treo</li>
</ul>''',
            'oem_code': '54668-JD000 (Nissan), 51306-SWA-A01 (Honda)',
        },
        {
            'name_vi': 'Lò xo giảm chấn', 'name_en': 'Coil Spring',
            'slug': 'lo-xo-giam-chan',
            'description': 'Lò xo xoắn bao quanh phuộc nhún, chịu trọng lượng xe và hấp thụ sốc ban đầu từ mặt đường.',
            'content': '''<h2>Lò xo giảm chấn là gì?</h2>
<p>Lò xo giảm chấn (Coil Spring) là bộ phận chịu lực chính trong hệ thống treo. Lò xo hấp thụ sốc từ mặt đường, giữ xe ở độ cao phù hợp, và phối hợp với phuộc nhún để mang lại cảm giác lái êm ái.</p>''',
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
            al = AffiliateLink(part_id=p.id, network=net, product_name=pname, url=url, price=price)
            db.session.add(al)

    # Parts cho Hệ thống phanh
    ht_phanh = zones['he-thong-phanh']
    parts_phanh = [
        {
            'name_vi': 'Má phanh', 'name_en': 'Brake Pad',
            'slug': 'ma-phanh',
            'description': 'Miếng vật liệu ma sát ép vào đĩa phanh để giảm tốc và dừng xe.',
            'content': '''<h2>Má phanh là gì?</h2>
<p>Má phanh (Brake Pad) là chi tiết hao mòn quan trọng nhất trong hệ thống phanh. Khi bạn đạp phanh, xy-lanh phanh ép má phanh vào đĩa phanh, tạo ma sát để giảm tốc độ.</p>

<h2>Khi nào cần thay?</h2>
<p>Thay sau <strong>30,000 - 50,000 km</strong> hoặc khi má mỏng dưới 3mm, nghe tiếng rít kim loại khi phanh.</p>''',
            'oem_code': 'D1060-JD00A (Nissan), 45022-SWA-A01 (Honda)',
        },
        {
            'name_vi': 'Đĩa phanh', 'name_en': 'Brake Disc',
            'slug': 'dia-phanh',
            'description': 'Đĩa kim loại gắn cùng bánh xe, bề mặt tiếp xúc với má phanh để tạo lực hãm.',
            'content': '''<h2>Đĩa phanh là gì?</h2>
<p>Đĩa phanh (Brake Disc/Rotor) là đĩa kim loại xoay cùng bánh xe. Má phanh kẹp vào hai bên đĩa để tạo lực hãm. Đĩa thường làm từ gang xám hoặc thép carbon.</p>''',
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
                             url=f'https://{net}.vn/search?q={p_data["slug"]}', price=price + i*100000)
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
    from models import db, AffiliateNetwork, AffiliateCampaign, AffiliateStats, SiteSettings
    from datetime import date, timedelta
    import random

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
    from models import db, Vertical, SocialChannel, VideoProject, VideoPublish
    import random
    from datetime import datetime

    car = Vertical.query.filter_by(slug='car').first()
    if not car:
        return

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
    from models import db, Article

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
            'content': '''<h2>Quy mô thị trường</h2>
<p>Thị trường phụ tùng ô tô Việt Nam đạt giá trị khoảng <strong>3.5 tỷ USD</strong> trong năm 2024, với tốc độ tăng trưởng trung bình 12%/năm. Số lượng xe ô tô lưu hành trên cả nước đã vượt mốc <strong>6.5 triệu xe</strong>, tạo nhu cầu rất lớn cho việc bảo dưỡng và thay thế phụ tùng.</p>

<h2>3 xu hướng lớn năm 2025</h2>
<p><strong>1. Phụ tùng OEM thay thế (aftermarket) lên ngôi</strong> — Người dùng ngày càng chuyển từ phụ tùng chính hãng sang các thương hiệu aftermarket uy tín với giá chỉ 30-50% so với chính hãng nhưng chất lượng tương đương.</p>
<p><strong>2. Mua online tăng mạnh</strong> — Các sàn TMDT (Shopee, Lazada) ghi nhận doanh số phụ tùng ô tô tăng 85% YoY. Người mua đã quen với việc tra cứu mã OEM và đặt hàng online.</p>
<p><strong>3. DIY (Do-It-Yourself) phát triển</strong> — Cộng đồng tự sửa xe tại nhà ngày càng đông, đặc biệt với các bộ phận đơn giản như cao su, lọc gió, bóng đèn.</p>

<h2>Cơ hội cho người tiêu dùng</h2>
<p>Với sự cạnh tranh ngày càng cao, giá phụ tùng aftermarket đã giảm 15-20% so với 3 năm trước. Người tiêu dùng thông minh có thể tiết kiệm hàng triệu đồng mỗi năm bằng cách:</p>
<ul>
<li>Tự tra cứu mã OEM chính xác trước khi mua</li>
<li>So sánh giá từ nhiều nguồn (online + offline)</li>
<li>Học cách tự thay các phụ tùng đơn giản</li>
</ul>'''
        },
        {
            'title': 'OEM vs Aftermarket vs Fake — Cách phân biệt phụ tùng ô tô',
            'slug': 'oem-vs-aftermarket-vs-fake',
            'tier': 'nganh',
            'category': 'kien-thuc-chung',
            'tags': 'OEM,aftermarket,hàng giả,phân biệt,chất lượng,mã phụ tùng',
            'excerpt': 'Hướng dẫn phân biệt 3 loại phụ tùng trên thị trường: OEM chính hãng, aftermarket chất lượng, và hàng nhái/fake. Cách đọc mã OEM và kiểm tra xuất xứ.',
            'reading_time': 10,
            'content': '''<h2>3 loại phụ tùng trên thị trường</h2>
<p><strong>OEM (Original Equipment Manufacturer)</strong> — Phụ tùng do chính hãng xe sản xuất hoặc đặt hàng từ nhà cung cấp cấp 1. Đắt nhất nhưng đảm bảo 100% tương thích.</p>
<p><strong>Aftermarket</strong> — Phụ tùng do các hãng thứ 3 sản xuất theo tiêu chuẩn OEM. Giá rẻ hơn 30-60%, chất lượng từ trung bình đến rất tốt tùy thương hiệu.</p>
<p><strong>Hàng nhái/Fake</strong> — Phụ tùng kém chất lượng, thường copy bao bì hàng chính hãng. Nguy hiểm và cần tránh tuyệt đối.</p>

<h2>Cách đọc mã OEM</h2>
<p>Mỗi phụ tùng ô tô đều có <strong>mã OEM</strong> (Part Number) riêng biệt. Ví dụ:</p>
<ul>
<li><strong>54320-JD00A</strong> — Mã Nissan. 5 số đầu = nhóm phụ tùng (543 = hệ thống treo). Suffix JD00A = đời xe cụ thể.</li>
<li><strong>51920-SWA-A01</strong> — Mã Honda. SWA = dòng CR-V. A01 = phiên bản.</li>
<li><strong>48609-0D050</strong> — Mã Toyota. 48609 = base giảm chấn. 0D050 = Vios/Yaris.</li>
</ul>

<h2>5 cách nhận biết hàng fake</h2>
<ul>
<li>Bao bì in mờ, font chữ không sắc nét</li>
<li>Không có mã QR hoặc hologram xác thực</li>
<li>Giá rẻ bất thường (dưới 50% giá aftermarket)</li>
<li>Trọng lượng nhẹ hơn hàng thật</li>
<li>Không có thông tin nhà sản xuất rõ ràng trên sản phẩm</li>
</ul>'''
        },
        {
            'title': 'Chi phí bảo dưỡng ô tô theo từng mốc km — Bảng tính chi tiết',
            'slug': 'chi-phi-bao-duong-oto-theo-km',
            'tier': 'nganh',
            'category': 'bao-duong',
            'tags': 'bảo dưỡng,chi phí,mốc km,lịch bảo dưỡng,tiết kiệm',
            'excerpt': 'Bảng tính chi phí bảo dưỡng chi tiết theo từng mốc 5,000km đến 100,000km. Biết trước để chuẩn bị ngân sách và không bị "chém" tại garage.',
            'reading_time': 7,
            'content': '''<h2>Lịch bảo dưỡng theo mốc km</h2>
<p>Mỗi chiếc xe đều cần bảo dưỡng định kỳ. Dưới đây là các mốc quan trọng nhất:</p>

<h3>5,000 — 10,000 km: Thay dầu máy</h3>
<p>Chi phí: <strong>500,000 — 1,200,000đ</strong> (tùy loại dầu). Đây là bảo dưỡng cơ bản nhất, nên làm đúng hạn để bảo vệ động cơ.</p>

<h3>20,000 km: Thay lọc gió + lọc điều hòa</h3>
<p>Chi phí: <strong>200,000 — 500,000đ</strong>. Lọc bẩn khiến xe yếu, tốn xăng. Đây là phụ tùng bạn hoàn toàn có thể tự thay tại nhà.</p>

<h3>40,000 km: Thay má phanh + dầu phanh</h3>
<p>Chi phí: <strong>800,000 — 2,500,000đ</strong>. Má phanh mòn ảnh hưởng trực tiếp đến an toàn. Kiểm tra mỗi 20,000km, thay khi còn dưới 3mm.</p>

<h3>60,000 — 80,000 km: Thay cao su hệ thống treo</h3>
<p>Chi phí: <strong>2,000,000 — 8,000,000đ</strong> (tùy số lượng). Cao su chân phuộc, cao su cân bằng, rotuyn... đều cần kiểm tra và thay ở mốc này.</p>

<h3>100,000 km: Đại tu lớn</h3>
<p>Chi phí: <strong>10,000,000 — 25,000,000đ</strong>. Thay dây curoa, bugi, bơm nước, thermostat, và tổng kiểm tra toàn bộ hệ thống.</p>'''
        },
        {
            'title': 'Top 10 lỗi ô tô thường gặp và cách xử lý tại chỗ',
            'slug': 'top-10-loi-oto-thuong-gap',
            'tier': 'nganh',
            'category': 'xu-ly-su-co',
            'tags': 'lỗi thường gặp,xử lý sự cố,roadside,khẩn cấp,mẹo xe',
            'excerpt': '10 sự cố ô tô phổ biến nhất và cách xử lý ngay tại chỗ: từ xe không nổ máy, đèn cảnh báo, đến nổ lốp giữa đường.',
            'reading_time': 12,
            'content': '''<h2>1. Xe không nổ máy</h2>
<p><strong>Nguyên nhân:</strong> Ắc-quy yếu (80% trường hợp), bugi hỏng, bơm xăng lỗi.</p>
<p><strong>Xử lý:</strong> Thử câu bình từ xe khác. Nếu không được → gọi cứu hộ.</p>

<h2>2. Đèn Check Engine sáng</h2>
<p><strong>Nguyên nhân:</strong> Cảm biến oxy, nắp bình xăng chưa đóng chặt, bộ chuyển đổi xúc tác.</p>
<p><strong>Xử lý:</strong> Kiểm tra nắp xăng trước. Nếu đèn vẫn sáng → đọc mã lỗi bằng OBD2 scanner.</p>

<h2>3. Xe bị rung lắc khi chạy tốc độ cao</h2>
<p><strong>Nguyên nhân:</strong> Mất cân bằng lốp, cao su hệ thống treo mòn, rotuyn lỏng.</p>
<p><strong>Xử lý:</strong> Cân chỉnh lốp. Kiểm tra cao su chân phuộc và rotuyn.</p>

<h2>4. Tiếng kêu lọc cọc dưới gầm</h2>
<p><strong>Nguyên nhân:</strong> Cao su chân phuộc hỏng, thanh cân bằng lỏng, giảm chấn mòn.</p>
<p><strong>Xử lý:</strong> Kiểm tra trực quan hệ thống treo. Thay cao su nếu bị nứt/biến dạng.</p>

<h2>5. Phanh kêu rít</h2>
<p><strong>Nguyên nhân:</strong> Má phanh mòn hết, đĩa phanh bị trầy xước, bụi bẩn kẹt.</p>
<p><strong>Xử lý:</strong> Kiểm tra má phanh ngay. Nếu còn dưới 2mm → thay ngay, không trì hoãn.</p>'''
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
            'content': '''<h2>Hệ thống treo là gì?</h2>
<p>Hệ thống treo (Suspension System) là tập hợp các bộ phận kết nối <strong>bánh xe với thân xe</strong>, có chức năng hấp thụ dao động từ mặt đường, giữ cho xe ổn định và hành khách thoải mái.</p>

<h2>4 loại hệ thống treo phổ biến</h2>
<h3>1. MacPherson Strut</h3>
<p>Phổ biến nhất trên xe con. Cấu tạo đơn giản: phuộc nhún kết hợp lò xo thành 1 cụm. Dùng trên: Toyota Vios, Honda City, Hyundai Accent.</p>

<h3>2. Double Wishbone (tay đòn kép)</h3>
<p>2 tay đòn trên và dưới hình chữ A. Khả năng xử lý tốt hơn MacPherson. Dùng trên: Honda CR-V, Toyota Camry, Mazda CX-5.</p>

<h3>3. Multi-link (đa liên kết)</h3>
<p>Dùng nhiều thanh nối cho phép điều chỉnh chính xác góc bánh xe. Thường dùng ở cầu sau xe cao cấp: Mercedes, BMW, Audi.</p>

<h3>4. Torsion Beam (thanh xoắn)</h3>
<p>Cấu tạo đơn giản, rẻ, nhẹ. Thường dùng ở cầu sau xe hạng B-C: Toyota Vios, Hyundai i10. Nhược điểm: kém linh hoạt trên đường xấu.</p>

<h2>Dấu hiệu hệ thống treo cần bảo dưỡng</h2>
<ul>
<li>Xe nghiêng khi vào cua, cảm giác "bồng bềnh"</li>
<li>Tiếng kêu lọc cọc khi qua ổ gà</li>
<li>Lốp mòn không đều</li>
<li>Tay lái bị rung ở tốc độ cao</li>
</ul>'''
        },
        {
            'title': 'Hệ thống phanh — Từ đĩa phanh đến ABS, EBD hoạt động ra sao?',
            'slug': 'he-thong-phanh-tu-dia-den-abs',
            'tier': 'chung',
            'category': 'he-thong-phanh',
            'related_segment_slug': 'cuv',
            'related_zone_slug': 'he-thong-phanh',
            'tags': 'phanh,ABS,EBD,đĩa phanh,má phanh,dầu phanh,an toàn',
            'excerpt': 'Giải thích chi tiết hệ thống phanh từ cơ bản đến nâng cao: phanh đĩa vs phanh tang trống, ABS, EBD, BA và cách bảo dưỡng.',
            'reading_time': 9,
            'content': '''<h2>Nguyên lý phanh ô tô</h2>
<p>Khi nhấn bàn đạp phanh → xy-lanh chính tạo áp suất dầu → dầu truyền qua đường ống → đẩy má phanh ép vào đĩa phanh → ma sát tạo lực hãm → xe giảm tốc.</p>

<h2>Phanh đĩa vs Phanh tang trống</h2>
<p><strong>Phanh đĩa:</strong> Hiệu quả cao, tản nhiệt tốt, dùng phổ biến ở bánh trước và cả 4 bánh xe đời mới.</p>
<p><strong>Phanh tang trống:</strong> Rẻ hơn, dùng ở bánh sau xe phổ thông. Tản nhiệt kém hơn nhưng đủ cho xe nhỏ.</p>

<h2>ABS, EBD, BA — Công nghệ phanh hiện đại</h2>
<p><strong>ABS (Anti-lock Braking System):</strong> Chống bó cứng phanh. Khi phanh gấp, ABS nhả-đạp liên tục 15 lần/giây, giúp xe không bị trượt.</p>
<p><strong>EBD (Electronic Brakeforce Distribution):</strong> Phân phối lực phanh thông minh giữa 4 bánh tùy theo tải trọng và tốc độ.</p>
<p><strong>BA (Brake Assist):</strong> Hỗ trợ lực phanh. Khi phát hiện phanh gấp nhưng lực đạp không đủ, BA tự động tăng áp suất phanh.</p>'''
        },
        {
            'title': 'Hệ thống điện ô tô — Ắc-quy, máy phát, và mạng CAN Bus',
            'slug': 'he-thong-dien-oto-ac-quy-can-bus',
            'tier': 'chung',
            'category': 'he-thong-dien',
            'tags': 'điện ô tô,ắc-quy,máy phát,CAN Bus,cảm biến,ECU',
            'excerpt': 'Tổng quan hệ thống điện trên xe hơi hiện đại: từ ắc-quy 12V, máy phát điện, đến mạng CAN Bus kết nối hàng chục ECU.',
            'reading_time': 8,
            'content': '''<h2>Ắc-quy — Trái tim điện của xe</h2>
<p>Ắc-quy 12V cung cấp điện cho hệ thống khởi động, đèn, và các thiết bị điện tử khi xe chưa nổ máy. Tuổi thọ trung bình: 2-4 năm.</p>

<h2>CAN Bus — Hệ thần kinh của xe hiện đại</h2>
<p>Xe đời mới có tới <strong>50-100 ECU</strong> (bộ điều khiển điện tử) giao tiếp qua mạng CAN Bus. Mỗi ECU quản lý một chức năng: động cơ, phanh, túi khí, điều hòa...</p>'''
        },
        {
            'title': 'Động cơ ô tô — Xăng vs Diesel vs Hybrid: nên chọn loại nào?',
            'slug': 'dong-co-xang-diesel-hybrid-so-sanh',
            'tier': 'chung',
            'category': 'dong-co',
            'tags': 'động cơ,xăng,diesel,hybrid,so sánh,tiết kiệm nhiên liệu',
            'excerpt': 'So sánh chi tiết 3 loại động cơ phổ biến: xăng, diesel, hybrid. Ưu nhược điểm, chi phí vận hành, và lời khuyên chọn xe.',
            'reading_time': 9,
            'content': '''<h2>Động cơ xăng</h2>
<p>Phổ biến nhất tại VN. Ưu điểm: êm, mạnh ở vòng tua cao, chi phí bảo dưỡng thấp. Nhược: tốn nhiên liệu hơn diesel 15-20%.</p>

<h2>Động cơ diesel</h2>
<p>Mạnh ở vòng tua thấp, tiết kiệm nhiên liệu. Phù hợp xe bán tải, SUV. Nhược: ồn hơn, chi phí sửa chữa cao, ít lựa chọn xe tại VN.</p>

<h2>Hybrid</h2>
<p>Kết hợp xăng + điện. Tiết kiệm 30-50% nhiên liệu trong thành phố. Xu hướng tương lai nhưng giá cao hơn 100-200 triệu so với bản xăng.</p>'''
        },
        {
            'title': 'Hệ thống lái — Trợ lực điện EPS vs thủy lực: khác biệt gì?',
            'slug': 'he-thong-lai-eps-vs-thuy-luc',
            'tier': 'chung',
            'category': 'he-thong-lai',
            'tags': 'hệ thống lái,EPS,trợ lực,thủy lực,tay lái,vô-lăng',
            'excerpt': 'So sánh 2 loại trợ lực lái phổ biến: EPS (điện) và trợ lực thủy lực. Cách nhận biết hỏng trợ lực lái.',
            'reading_time': 6,
            'content': '''<h2>Trợ lực thủy lực</h2>
<p>Dùng bơm dầu trợ lực lấy công suất từ động cơ → tạo áp suất hỗ trợ xoay vô-lăng. Cảm giác lái tốt nhưng tốn nhiên liệu và nặng hơn EPS.</p>

<h2>Trợ lực điện EPS</h2>
<p>Motor điện hỗ trợ trực tiếp trên trục lái. Tiết kiệm nhiên liệu, nhẹ, và có thể tùy chỉnh độ nặng nhẹ tay lái theo tốc độ. Phổ biến trên hầu hết xe đời mới.</p>'''
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
            'content': '''<h2>Cao su chân phuộc nằm ở đâu?</h2>
<p>Cao su chân phuộc nằm ở <strong>2 đầu của phuộc nhún</strong>: đầu trên (gắn vào thân xe/tháp phuộc) và đầu dưới (gắn vào cam quay/tay đòn). Mỗi xe có 4 phuộc → 8 cao su chân phuộc.</p>

<h2>Chất liệu: Cao su vs Polyurethane</h2>
<p><strong>Cao su tự nhiên (OEM):</strong> Mềm, êm, giảm tiếng ồn tốt. Tuổi thọ 60,000-80,000km.</p>
<p><strong>Polyurethane:</strong> Cứng hơn, bền hơn gấp 2-3 lần, phù hợp xe thường xuyên đi đường xấu. Nhược: hơi ồn hơn.</p>

<h2>5 dấu hiệu cần thay</h2>
<ul>
<li>Tiếng lọc cọc khi qua ổ gà, gờ giảm tốc</li>
<li>Xe bồng bềnh, mất cảm giác đường ở tốc độ cao</li>
<li>Lốp mòn lệch (mòn 1 bên nhiều hơn)</li>
<li>Nhìn thấy cao su nứt, rách khi kiểm tra trực quan</li>
<li>Phuộc bị lệch, nghiêng khi kích xe lên</li>
</ul>

<h2>Chi phí thay thế theo hãng xe</h2>
<p><strong>Toyota:</strong> 120,000-250,000đ/cái (OEM). <strong>Honda:</strong> 150,000-300,000đ/cái. <strong>Hyundai/Kia:</strong> 80,000-200,000đ/cái. Công thay: 100,000-200,000đ/cái.</p>

<h2>Tự thay tại nhà được không?</h2>
<p>Với cao su chân phuộc <strong>đầu dưới</strong>: Có thể tự thay nếu có cầu nâng hoặc kích xe. Cần dụng cụ: kích, cờ-lê, búa cao su.</p>
<p>Với cao su <strong>đầu trên</strong>: Khó hơn, cần tháo cụm phuộc. Nên mang ra garage.</p>'''
        },
        {
            'title': 'Má phanh — Khi nào thay, chọn loại nào, và mẹo tiết kiệm',
            'slug': 'ma-phanh-khi-nao-thay-chon-loai-nao',
            'tier': 'chi-tiet',
            'category': 'he-thong-phanh',
            'related_zone_slug': 'he-thong-phanh',
            'tags': 'má phanh,brake pad,ceramic,semi-metallic,thay má phanh,an toàn',
            'excerpt': 'Tất tần tật về má phanh: 3 loại phổ biến, cách kiểm tra độ mòn, thời điểm thay, và bí quyết chọn má phanh tốt giá rẻ.',
            'reading_time': 8,
            'embed_code': '<div class="at-carousel" data-network="accesstrade" data-keyword="ma phanh oto" data-limit="6"></div>',
            'content': '''<h2>3 loại má phanh phổ biến</h2>
<p><strong>Organic:</strong> Mềm, êm, rẻ. Phù hợp xe đi phố. Mòn nhanh.</p>
<p><strong>Semi-metallic:</strong> Pha kim loại 30-65%. Bền, phanh tốt ở nhiệt độ cao. Hơi ồn. Phổ biến nhất.</p>
<p><strong>Ceramic:</strong> Bền nhất, êm nhất, ít bụi. Giá cao gấp 2-3x. Phù hợp xe cao cấp.</p>

<h2>Kiểm tra độ mòn</h2>
<p>Má phanh mới dày 10-12mm. Cần thay khi còn <strong>dưới 3mm</strong>. Nhiều xe có cảm biến cảnh báo tự động.</p>'''
        },
        {
            'title': 'Rotuyn — Bộ phận nhỏ nhưng cực kỳ quan trọng cho an toàn',
            'slug': 'rotuy-bo-phan-quan-trong-an-toan',
            'tier': 'chi-tiet',
            'category': 'he-thong-treo',
            'related_zone_slug': 'he-thong-treo',
            'tags': 'rotuyn,ball joint,lái,an toàn,hệ thống treo,thay thế',
            'excerpt': 'Rotuyn là gì, nằm ở đâu, hỏng thì nguy hiểm ra sao? Hướng dẫn kiểm tra rotuyn tại nhà và chi phí thay thế.',
            'reading_time': 7,
            'content': '''<h2>Rotuyn là gì?</h2>
<p>Rotuyn (Ball Joint) là khớp cầu kết nối các bộ phận di động trong hệ thống treo và hệ thống lái. Cho phép xoay và di chuyển đa hướng.</p>

<h2>Hỏng rotuyn có nguy hiểm không?</h2>
<p><strong>Rất nguy hiểm!</strong> Rotuyn hỏng nặng có thể khiến bánh xe tách khỏi hệ thống treo khi đang chạy → mất lái hoàn toàn. Đây là lỗi CẦN sửa ngay.</p>

<h2>Chi phí thay</h2>
<p>Rotuyn lái: 200,000-500,000đ/cái. Rotuyn treo: 300,000-800,000đ/cái. Công thay: 150,000-300,000đ.</p>'''
        },
        {
            'title': 'Lọc gió động cơ — Phụ tùng rẻ nhất nhưng hay bị quên',
            'slug': 'loc-gio-dong-co-phu-tung-re-nhat',
            'tier': 'chi-tiet',
            'category': 'dong-co',
            'tags': 'lọc gió,air filter,thay lọc gió,DIY,tiết kiệm xăng',
            'excerpt': 'Lọc gió bẩn khiến xe yếu, tốn xăng 10-15%. Hướng dẫn tự thay lọc gió trong 5 phút, không cần dụng cụ.',
            'reading_time': 5,
            'content': '''<h2>Tại sao lọc gió quan trọng?</h2>
<p>Động cơ cần hút không khí sạch để đốt nhiên liệu hiệu quả. Lọc gió bẩn = ít không khí = đốt không hết = <strong>yếu máy + tốn xăng 10-15%</strong>.</p>

<h2>Tự thay trong 5 phút</h2>
<p>Lọc gió là phụ tùng <strong>dễ thay nhất</strong> trên ô tô. Chỉ cần mở nắp hộp lọc (thường dùng 2-4 kẹp), lấy lọc cũ ra, lắp lọc mới vào. Không cần bất kỳ dụng cụ nào.</p>

<h2>Chi phí</h2>
<p>Lọc gió OEM: 150,000-300,000đ. Aftermarket: 50,000-150,000đ. Thay mỗi 15,000-20,000km.</p>'''
        },
        {
            'title': 'Bugi — Linh hồn đánh lửa, chọn sai bugi xe yếu hẳn',
            'slug': 'bugi-linh-hon-danh-lua',
            'tier': 'chi-tiet',
            'category': 'dong-co',
            'tags': 'bugi,spark plug,đánh lửa,iridium,platinum,nguyên lý',
            'excerpt': 'Bugi Iridium vs Platinum vs thường: khác biệt gì? Khi nào cần thay và cách đọc nhiệt trị bugi.',
            'reading_time': 7,
            'content': '''<h2>3 loại bugi</h2>
<p><strong>Bugi thường (Nickel):</strong> Rẻ (30,000-50,000đ/cái). Thay mỗi 20,000-30,000km.</p>
<p><strong>Bugi Platinum:</strong> Bền hơn 2x (80,000-120,000đ/cái). Thay mỗi 60,000km.</p>
<p><strong>Bugi Iridium:</strong> Bền nhất, đánh lửa mạnh nhất (150,000-250,000đ/cái). Thay mỗi 100,000km. Tiết kiệm xăng 2-3%.</p>

<h2>Nhiệt trị bugi</h2>
<p>Nhiệt trị thể hiện khả năng tản nhiệt. Số cao = bugi "lạnh" (tản nhiệt nhanh, cho xe turbo). Số thấp = bugi "nóng" (cho xe phổ thông).</p>'''
        },
        {
            'title': 'Dầu động cơ — 5W30 hay 5W40? Synthetic hay mineral?',
            'slug': 'dau-dong-co-5w30-5w40-synthetic',
            'tier': 'chi-tiet',
            'category': 'dong-co',
            'tags': 'dầu máy,5W30,5W40,synthetic,mineral,thay dầu,viscosity',
            'excerpt': 'Giải mã ký hiệu dầu nhớt: 5W-30 nghĩa là gì? Synthetic (tổng hợp) khác gì mineral (khoáng)? Chọn loại nào cho xe bạn?',
            'reading_time': 8,
            'content': '''<h2>Đọc hiểu ký hiệu dầu nhớt</h2>
<p><strong>5W-30:</strong> Số 5W = độ nhớt ở nhiệt độ thấp (W = Winter). Số 30 = độ nhớt ở nhiệt độ hoạt động. Số càng nhỏ = dầu càng loãng.</p>

<h2>5W-30 vs 5W-40</h2>
<p><strong>5W-30:</strong> Phù hợp xe đời mới, tiết kiệm nhiên liệu hơn. Toyota, Honda khuyến cáo dùng 5W-30.</p>
<p><strong>5W-40:</strong> Bảo vệ tốt hơn ở nhiệt độ cao, phù hợp xe turbo hoặc xe cũ có khe hở lớn.</p>

<h2>Synthetic vs Mineral</h2>
<p><strong>Mineral (khoáng):</strong> Rẻ, thay mỗi 5,000km. Giá 150,000-300,000đ/lít.</p>
<p><strong>Semi-synthetic:</strong> Cân bằng, thay mỗi 7,500km. Giá 250,000-400,000đ/lít.</p>
<p><strong>Full synthetic (tổng hợp):</strong> Tốt nhất, thay mỗi 10,000km. Giá 400,000-800,000đ/lít. Tiết kiệm dài hạn.</p>'''
        },
        {
            'title': 'Lốp ô tô — Đọc thông số, chọn đúng loại, và khi nào cần thay',
            'slug': 'lop-oto-doc-thong-so-chon-dung',
            'tier': 'chi-tiet',
            'category': 'lop-xe',
            'tags': 'lốp xe,tire,195/65R15,chọn lốp,thay lốp,mòn lốp,DOT',
            'excerpt': 'Cách đọc thông số lốp 195/65R15 91H, kiểm tra DOT (ngày sản xuất), và 4 dấu hiệu cần thay lốp ngay.',
            'reading_time': 9,
            'content': '''<h2>Đọc thông số lốp: 195/65R15 91H</h2>
<p><strong>195</strong> = chiều rộng mặt lốp (mm). <strong>65</strong> = tỉ lệ chiều cao/chiều rộng (%). <strong>R</strong> = Radial. <strong>15</strong> = đường kính lazang (inch). <strong>91</strong> = chỉ số tải. <strong>H</strong> = tốc độ tối đa (210km/h).</p>

<h2>Kiểm tra tuổi lốp (mã DOT)</h2>
<p>Trên thành lốp có 4 số cuối mã DOT. VD: <strong>2523</strong> = sản xuất tuần 25, năm 2023. Lốp nên dùng trong <strong>5 năm</strong> kể từ ngày sản xuất.</p>

<h2>4 dấu hiệu cần thay</h2>
<ul>
<li>Gai lốp mòn dưới 1.6mm (dùng đồng xu kiểm tra)</li>
<li>Nứt thành lốp, phồng rộp</li>
<li>Lốp quá 5 năm tuổi</li>
<li>Xe bị lệch lái, rung tay lái</li>
</ul>'''
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
    from models import db, Vertical, Segment, Zone, Part
    import random

    v = Vertical(name='Pet', slug='pet', description='Kiến thức chăm sóc thú cưng — chó, mèo, và thú nhỏ', icon='🐾', status='active')
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
                  'content':'<h2>Thức ăn hạt là gì?</h2><p>Dry food (kibble) là loại thức ăn chó phổ biến nhất thế giới, chiếm 60% thị trường. Được sấy khô ở nhiệt độ cao, có hàm lượng nước chỉ 6-10%.</p><h2>Cách chọn thức ăn hạt</h2><p>Xem thành phần: <strong>protein từ thịt</strong> phải đứng đầu danh sách. Tránh sản phẩm có ngô, lúa mì làm thành phần chính. Chọn theo size: Small breed (< 10kg), Medium (10-25kg), Large (> 25kg).</p><h2>Top thương hiệu</h2><p><strong>Premium:</strong> Royal Canin, Hill\'s Science Diet — 300-500k/kg. <strong>Super Premium:</strong> Taste of the Wild, Acana — 400-700k/kg. <strong>Phổ thông:</strong> Pedigree, SmartHeart — 80-150k/kg.</p>'},
                 {'vi':'Thức ăn ướt (Wet Food)','en':'Wet Dog Food','slug':'thuc-an-uot',
                  'desc':'Pate, thức ăn đóng hộp — hàm lượng nước cao, phù hợp chó biếng ăn',
                  'tags':'thức ăn ướt,pate,wet food,đóng hộp',
                  'content':'<h2>Ưu điểm thức ăn ướt</h2><p>Hàm lượng nước 75-85% giúp chó bổ sung nước. Mùi vị hấp dẫn, phù hợp chó biếng ăn hoặc chó già răng yếu.</p><h2>Nhược điểm</h2><p>Đắt hơn dry food 3-5 lần. Mở ra phải dùng trong 24h (tủ lạnh). Không tốt cho răng như dry food.</p>'},
                 {'vi':'Vitamin & Supplement','en':'Dog Supplements','slug':'vitamin-supplement',
                  'desc':'Bổ sung vitamin, khoáng chất, glucosamine, omega-3 cho chó',
                  'tags':'vitamin,supplement,glucosamine,omega-3,canxi,bổ sung',
                  'content':'<h2>Khi nào cần bổ sung?</h2><p>Chó ăn thức ăn hạt premium thường đã đủ dinh dưỡng. Cần bổ sung khi: chó mang thai/cho con bú, chó già > 7 tuổi, chó bệnh hồi phục, chó ăn cơm nhà.</p>'},
             ]},
            {'name':'Y tế & Bệnh lý','slug':'y-te','icon':'💉','color':'#3498db',
             'desc':'Vaccine, tẩy giun, bệnh thường gặp, phòng ngừa',
             'parts':[
                 {'vi':'Vaccine cơ bản','en':'Core Vaccines','slug':'vaccine-co-ban',
                  'desc':'Lịch tiêm vaccine cho chó: 5in1, 7in1, dại — phòng bệnh nguy hiểm',
                  'tags':'vaccine,tiêm phòng,5in1,7in1,dại,puppy',
                  'content':'<h2>Lịch vaccine cho chó con</h2><p><strong>6-8 tuần:</strong> Mũi 1 (5in1 hoặc 7in1). <strong>9-11 tuần:</strong> Mũi 2. <strong>12-14 tuần:</strong> Mũi 3 + vaccine dại. <strong>Hàng năm:</strong> Nhắc lại 1 mũi tổng hợp + dại.</p><h2>Chi phí</h2><p>Vaccine 5in1: 150-250k/mũi. Vaccine 7in1: 200-350k/mũi. Vaccine dại: 100-200k/mũi.</p>'},
                 {'vi':'Tẩy giun định kỳ','en':'Deworming','slug':'tay-giun',
                  'desc':'Lịch tẩy giun, loại thuốc, dấu hiệu nhiễm giun ở chó',
                  'tags':'tẩy giun,giun sán,deworming,phòng ngừa',
                  'content':'<h2>Lịch tẩy giun</h2><p>Chó con: mỗi 2 tuần từ 2-12 tuần tuổi. Chó trưởng thành: mỗi 3-6 tháng. Thuốc phổ biến: Drontal, Milbemax — giá 50-120k/viên.</p>'},
                 {'vi':'Ve & Bọ chét','en':'Flea & Tick Prevention','slug':'ve-bo-chet',
                  'desc':'Phòng trị ve, bọ chét — nhỏ gáy, vòng cổ, xịt',
                  'tags':'ve,bọ chét,flea,tick,nhỏ gáy,Nexgard,Frontline',
                  'content':'<h2>3 phương pháp phòng ve</h2><p><strong>Nhỏ gáy (Spot-on):</strong> Frontline, Revolution — nhỏ 1 lần/tháng. 150-300k/tuýp. <strong>Viên uống:</strong> Nexgard, Bravecto — hiệu quả 1-3 tháng. 200-500k/viên. <strong>Vòng cổ:</strong> Seresto — hiệu quả 8 tháng. 400-600k.</p>'},
             ]},
            {'name':'Huấn luyện','slug':'huan-luyen','icon':'🎯','color':'#2ecc71',
             'desc':'Huấn luyện cơ bản, ngồi, nằm, đi vệ sinh đúng chỗ, xã hội hóa',
             'parts':[
                 {'vi':'Đi vệ sinh đúng chỗ','en':'Potty Training','slug':'di-ve-sinh-dung-cho',
                  'desc':'Hướng dẫn dạy chó con đi vệ sinh đúng nơi quy định',
                  'tags':'vệ sinh,potty training,chó con,huấn luyện cơ bản',
                  'content':'<h2>Nguyên tắc vàng</h2><p>Chó con cần đi vệ sinh mỗi 2-3 giờ. Đưa chó đến vị trí quy định <strong>ngay sau khi</strong>: ăn xong, ngủ dậy, chơi xong. Khen thưởng ngay khi chó đi đúng chỗ.</p>'},
                 {'vi':'Lệnh cơ bản (Ngồi, Nằm, Lại đây)','en':'Basic Commands','slug':'lenh-co-ban',
                  'desc':'Dạy chó 5 lệnh cơ bản: Sit, Down, Come, Stay, Heel',
                  'tags':'lệnh cơ bản,sit,down,come,huấn luyện,clicker',
                  'content':'<h2>5 lệnh nền tảng</h2><p><strong>Sit (Ngồi):</strong> Đưa treat lên cao → chó tự ngồi → khen + thưởng. Luyện 5-10 lần/ngày. <strong>Down (Nằm):</strong> Từ tư thế ngồi, đưa treat xuống đất. <strong>Come (Lại đây):</strong> Bắt đầu ở khoảng cách ngắn, tăng dần.</p>'},
             ]},
            {'name':'Đồ dùng & Phụ kiện','slug':'do-dung','icon':'🦴','color':'#f39c12',
             'desc':'Chuồng, dây dắt, bát ăn, đồ chơi, quần áo cho chó',
             'parts':[
                 {'vi':'Dây dắt & Vòng cổ','en':'Leash & Collar','slug':'day-dat-vong-co',
                  'desc':'Chọn dây dắt, vòng cổ, yếm (harness) phù hợp theo size và giống chó',
                  'tags':'dây dắt,vòng cổ,harness,yếm,dạo phố',
                  'content':'<h2>3 loại dây dắt</h2><p><strong>Dây cố định:</strong> Dài 1.2-1.8m, phổ biến nhất. <strong>Dây rút (Flexi):</strong> Tự cuộn, dài 3-8m. Phù hợp công viên. <strong>Yếm (Harness):</strong> An toàn hơn vòng cổ, không gây áp lực lên cổ. Nên dùng cho giống nhỏ.</p>'},
                 {'vi':'Chuồng & Nệm ngủ','en':'Crate & Bed','slug':'chuong-nem',
                  'desc':'Chọn chuồng, nệm, ổ ngủ phù hợp cho chó',
                  'tags':'chuồng,nệm,giường,crate,ngủ',
                  'content':'<h2>Chọn size chuồng</h2><p>Chuồng phải đủ lớn để chó <strong>đứng, xoay, nằm thoải mái</strong>. Đo chiều dài chó (mũi → gốc đuôi) + 5-10cm. Chó con: mua size trưởng thành + dùng vách ngăn.</p>'},
             ]},
        ],
        'meo': [
            {'name':'Dinh dưỡng','slug':'dinh-duong','icon':'🐟','color':'#9b59b6',
             'desc':'Thức ăn mèo, chế độ ăn, dinh dưỡng theo tuổi',
             'parts':[
                 {'vi':'Thức ăn hạt cho mèo','en':'Dry Cat Food','slug':'thuc-an-hat-meo',
                  'desc':'Chọn thức ăn hạt cho mèo: protein cao, ít carb, đủ taurine',
                  'tags':'thức ăn mèo,dry food,Royal Canin,Whiskas,taurine',
                  'content':'<h2>Mèo cần gì?</h2><p>Mèo là <strong>động vật ăn thịt bắt buộc</strong>. Thức ăn phải có protein > 30%, chất béo > 15%, và bắt buộc có <strong>taurine</strong> (mèo không tự tổng hợp được).</p><h2>Top thương hiệu</h2><p><strong>Premium:</strong> Royal Canin, Hill\'s — 300-500k/kg. <strong>Super Premium:</strong> Orijen, Acana — 500-800k/kg. <strong>Phổ thông:</strong> Whiskas, Me-O — 60-120k/kg.</p>'},
                 {'vi':'Pate & Thức ăn ướt','en':'Wet Cat Food','slug':'pate-meo',
                  'desc':'Pate mèo, thức ăn ướt — bổ sung nước, phòng bệnh thận',
                  'tags':'pate mèo,wet food,thận,bổ sung nước',
                  'content':'<h2>Tại sao mèo cần ăn ướt?</h2><p>Mèo bản năng uống ít nước. Thức ăn ướt chứa 75-85% nước, giúp phòng <strong>bệnh thận</strong> và <strong>sỏi tiết niệu</strong> — 2 bệnh phổ biến nhất ở mèo.</p>'},
             ]},
            {'name':'Y tế','slug':'y-te','icon':'💊','color':'#e74c3c',
             'desc':'Vaccine, triệt sản, bệnh thường gặp ở mèo',
             'parts':[
                 {'vi':'Vaccine mèo','en':'Cat Vaccines','slug':'vaccine-meo',
                  'desc':'Lịch tiêm vaccine cho mèo: 3in1, 4in1, dại',
                  'tags':'vaccine mèo,3in1,4in1,dại,FPV,FCV',
                  'content':'<h2>Lịch vaccine mèo</h2><p><strong>8 tuần:</strong> Mũi 1 (3in1: FPV + FCV + FHV). <strong>12 tuần:</strong> Mũi 2. <strong>16 tuần:</strong> Mũi 3 + dại. <strong>Hàng năm:</strong> Nhắc lại. Chi phí: 150-300k/mũi.</p>'},
                 {'vi':'Triệt sản','en':'Spay/Neuter','slug':'triet-san',
                  'desc':'Triệt sản mèo: lợi ích, thời điểm, chi phí, chăm sóc sau phẫu thuật',
                  'tags':'triệt sản,spay,neuter,phẫu thuật,6 tháng',
                  'content':'<h2>Nên triệt sản khi nào?</h2><p>Thời điểm lý tưởng: <strong>5-6 tháng tuổi</strong>, trước khi mèo vào kỳ động dục đầu tiên. Chi phí: Mèo đực 300-600k, mèo cái 500-1,000k.</p>'},
             ]},
            {'name':'Đồ dùng','slug':'do-dung','icon':'🧶','color':'#1abc9c',
             'desc':'Khay cát, cây mèo, đồ chơi, bát ăn',
             'parts':[
                 {'vi':'Khay cát & Cát vệ sinh','en':'Litter Box & Litter','slug':'khay-cat',
                  'desc':'Chọn khay cát, loại cát phù hợp, mẹo khử mùi',
                  'tags':'khay cát,cát vệ sinh,litter box,bentonite,tofu',
                  'content':'<h2>2 loại cát phổ biến</h2><p><strong>Bentonite (cát khoáng):</strong> Vón cục tốt, rẻ (30-60k/5L). Nhược: bụi, nặng. <strong>Tofu (cát đậu nành):</strong> Ít bụi, nhẹ, xả được bồn cầu. Giá 80-150k/6L.</p>'},
                 {'vi':'Cây leo & Trụ cào','en':'Cat Tree & Scratcher','slug':'cay-leo-tru-cao',
                  'desc':'Cây mèo, trụ cào móng — thỏa mãn bản năng, bảo vệ nội thất',
                  'tags':'cây mèo,trụ cào,cat tree,scratcher,nội thất',
                  'content':'<h2>Tại sao cần trụ cào?</h2><p>Mèo <strong>bắt buộc</strong> phải cào. Không có trụ cào → mèo cào sofa, rèm, tường. Chọn trụ cao hơn mèo khi đứng (tối thiểu 60cm). Vật liệu tốt nhất: dây thừng sisal.</p>'},
             ]},
        ],
        'thu-nho': [
            {'name':'Hamster','slug':'hamster','icon':'🐹','color':'#f1c40f',
             'desc':'Chăm sóc hamster: chuồng, thức ăn, bệnh lý',
             'parts':[
                 {'vi':'Chuồng & Lót chuồng','en':'Hamster Cage','slug':'chuong-hamster',
                  'desc':'Chọn chuồng, lót chuồng, phụ kiện cho hamster',
                  'tags':'chuồng hamster,lót chuồng,mùn cưa,cage',
                  'content':'<h2>Kích thước tối thiểu</h2><p>Chuồng hamster cần tối thiểu <strong>450 cm² sàn</strong> (VD: 60x30cm). Lớn hơn = hamster vui hơn. Lót chuồng: mùn cưa (phổ thông) hoặc giấy xé (an toàn hơn). KHÔNG dùng bông gòn.</p>'},
                 {'vi':'Thức ăn hamster','en':'Hamster Food','slug':'thuc-an-hamster',
                  'desc':'Thức ăn hỗn hợp, hạt, rau quả cho hamster',
                  'tags':'thức ăn hamster,hạt hướng dương,rau,trái cây',
                  'content':'<h2>Chế độ ăn</h2><p>Chủ yếu: thức ăn hỗn hợp chuyên dụng (30-50k/gói). Bổ sung: rau (bông cải, cà rốt), protein (trứng luộc, sâu khô). <strong>TRÁNH:</strong> hành, tỏi, sô-cô-la, cam quýt.</p>'},
             ]},
            {'name':'Cá cảnh','slug':'ca-canh','icon':'🐠','color':'#3498db',
             'desc':'Cá cảnh nước ngọt, nước mặn, hồ thủy sinh',
             'parts':[
                 {'vi':'Bể & Lọc nước','en':'Aquarium & Filter','slug':'be-loc-nuoc',
                  'desc':'Chọn bể, hệ thống lọc, ánh sáng cho hồ cá',
                  'tags':'bể cá,lọc nước,filter,aquarium,thủy sinh',
                  'content':'<h2>Bể đầu tiên</h2><p>Bể tối thiểu <strong>40 lít</strong> cho người mới. Bể lớn = nước ổn định hơn = dễ chăm hơn. Hệ thống lọc: lọc thác (rẻ, đơn giản) hoặc lọc tràn (hiệu quả, cho bể lớn).</p>'},
                 {'vi':'Thức ăn cá','en':'Fish Food','slug':'thuc-an-ca',
                  'desc':'Thức ăn viên, lá, đông lạnh cho các loại cá cảnh',
                  'tags':'thức ăn cá,pellet,flake,artemia,cá cảnh',
                  'content':'<h2>3 loại thức ăn</h2><p><strong>Viên/Flake:</strong> Tiện, phổ thông (20-50k). <strong>Đông lạnh:</strong> Trùn chỉ, artemia — dinh dưỡng cao. <strong>Sống:</strong> Bo bo, trùn chỉ sống — kích thích bản năng săn mồi.</p>'},
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
    from models import db, Article
    import random

    articles = [
        # T1: NGANH
        {'title':'Thị trường thú cưng Việt Nam 2025 — Bùng nổ & Cơ hội','slug':'thi-truong-thu-cung-vn-2025','tier':'nganh','category':'thi-truong',
         'tags':'thị trường,thú cưng,Việt Nam,2025,pet economy',
         'excerpt':'Thị trường thú cưng VN đạt 1.2 tỷ USD, tăng 25%/năm. Phân tích xu hướng, cơ hội kinh doanh, và thói quen chi tiêu của pet parent Việt.',
         'reading_time':8,
         'content':'<h2>Quy mô thị trường</h2><p>Việt Nam có khoảng <strong>12 triệu hộ gia đình</strong> nuôi thú cưng, chi tiêu trung bình 2-5 triệu/tháng. Thị trường pet food chiếm 45%, dịch vụ y tế 25%, đồ dùng 20%, dịch vụ làm đẹp 10%.</p><h2>Xu hướng 2025</h2><p><strong>Humanization:</strong> Pet được đối xử như thành viên gia đình. <strong>Premium hóa:</strong> Chuyển từ hàng rẻ sang thương hiệu uy tín. <strong>Online shopping:</strong> Mua online chiếm 40%+ doanh số pet food.</p>'},
        {'title':'Chọn giống chó phù hợp — Hướng dẫn cho người mới','slug':'chon-giong-cho-phu-hop','tier':'nganh','category':'chon-giong',
         'tags':'giống chó,chọn giống,người mới,apartment,gia đình',
         'excerpt':'Hướng dẫn chọn giống chó phù hợp với điều kiện sống: chung cư, nhà rộng, có trẻ nhỏ, người bận rộn.',
         'reading_time':10,
         'content':'<h2>Chọn theo điều kiện sống</h2><p><strong>Chung cư nhỏ:</strong> Poodle, Corgi, Shih Tzu, Pomeranian — nhỏ, ít sủa. <strong>Nhà có sân:</strong> Golden Retriever, Labrador, Husky — cần không gian. <strong>Có trẻ nhỏ:</strong> Golden, Beagle, Pug — hiền, kiên nhẫn.</p>'},
        {'title':'Chi phí nuôi chó/mèo 1 năm — Tính sao cho đúng?','slug':'chi-phi-nuoi-cho-meo-1-nam','tier':'nganh','category':'chi-phi',
         'tags':'chi phí,nuôi chó,nuôi mèo,budget,1 năm',
         'excerpt':'Bảng tính chi phí nuôi chó/mèo chi tiết: thức ăn, vaccine, y tế, đồ dùng, làm đẹp — từ tiết kiệm đến premium.',
         'reading_time':7,
         'content':'<h2>Chó (size trung bình)</h2><p><strong>Thức ăn:</strong> 1.5-4 triệu/tháng. <strong>Vaccine năm 1:</strong> 1-2 triệu. <strong>Tẩy giun + ve:</strong> 500k-1.5 triệu/năm. <strong>Đồ dùng:</strong> 1-3 triệu (ban đầu). <strong>Y tế khẩn cấp:</strong> dự phòng 3-5 triệu. Tổng năm 1: <strong>25-65 triệu.</strong></p><h2>Mèo</h2><p>Thường rẻ hơn chó 20-30%: thức ăn ít hơn, ít cần dắt đi dạo, ít tắm. Tổng năm 1: <strong>15-40 triệu.</strong></p>'},

        # T2: CHUNG
        {'title':'Dinh dưỡng chó theo từng giai đoạn — Puppy, Adult, Senior','slug':'dinh-duong-cho-theo-giai-doan','tier':'chung','category':'dinh-duong',
         'related_segment_slug':'cho','related_zone_slug':'dinh-duong',
         'tags':'dinh dưỡng,puppy,adult,senior,protein,chất béo',
         'excerpt':'Nhu cầu dinh dưỡng chó thay đổi theo tuổi. Hướng dẫn chọn thức ăn đúng cho từng giai đoạn.',
         'reading_time':9,
         'content':'<h2>Puppy (0-12 tháng)</h2><p>Cần <strong>protein 28-32%</strong>, chất béo 17-20%. Ăn 3-4 bữa/ngày. Chọn thức ăn ghi "Puppy" hoặc "Growth".</p><h2>Adult (1-7 tuổi)</h2><p>Protein 22-28%, chất béo 12-16%. Ăn 2 bữa/ngày. Kiểm soát cân nặng.</p><h2>Senior (> 7 tuổi)</h2><p>Ít calo hơn, bổ sung glucosamine cho khớp, omega-3 cho não.</p>'},
        {'title':'Hành vi mèo — Giải mã ngôn ngữ cơ thể','slug':'hanh-vi-meo-giai-ma','tier':'chung','category':'hanh-vi',
         'related_segment_slug':'meo',
         'tags':'hành vi mèo,ngôn ngữ cơ thể,đuôi mèo,rên gừ,cắn',
         'excerpt':'Mèo giao tiếp bằng đuôi, tai, mắt, và âm thanh. Hiểu ngôn ngữ mèo để chăm sóc tốt hơn.',
         'reading_time':8,
         'content':'<h2>Đuôi mèo nói gì?</h2><p><strong>Đuôi dựng thẳng:</strong> Vui, tự tin, chào hỏi. <strong>Đuôi phồng to:</strong> Sợ hãi hoặc hung dữ. <strong>Đuôi quẫy nhanh:</strong> Khó chịu, bực bội (KHÁC với chó!). <strong>Đuôi cuộn quanh người:</strong> Thân thiện, tin tưởng.</p>'},
        {'title':'5 bệnh thường gặp ở chó và dấu hiệu nhận biết','slug':'5-benh-thuong-gap-o-cho','tier':'chung','category':'y-te',
         'related_segment_slug':'cho','related_zone_slug':'y-te',
         'tags':'bệnh chó,Parvo,Care,viêm ruột,nấm da',
         'excerpt':'5 bệnh nguy hiểm nhất ở chó: Parvo, Care, viêm ruột, nấm da, viêm tai — dấu hiệu và cách phòng.',
         'reading_time':10,
         'content':'<h2>1. Parvo (Parvovirus)</h2><p><strong>Triệu chứng:</strong> Nôn mửa, tiêu chảy ra máu, bỏ ăn, sốt cao. <strong>Nguy hiểm:</strong> Tỷ lệ tử vong 80% nếu không điều trị. <strong>Phòng:</strong> Vaccine đầy đủ.</p><h2>2. Care (Distemper)</h2><p><strong>Triệu chứng:</strong> Chảy dịch mũi/mắt, ho, co giật, liệt. <strong>Phòng:</strong> Vaccine 5in1/7in1.</p>'},
        {'title':'Cách tắm chó mèo đúng cách tại nhà','slug':'cach-tam-cho-meo-dung-cach','tier':'chung','category':'cham-soc',
         'tags':'tắm chó,tắm mèo,grooming,sữa tắm,lông',
         'excerpt':'Hướng dẫn tắm chó mèo tại nhà: tần suất, nhiệt độ nước, sữa tắm, sấy khô — tránh sai lầm gây bệnh da.',
         'reading_time':6,
         'content':'<h2>Tần suất tắm</h2><p><strong>Chó:</strong> 2-4 tuần/lần (tùy giống lông). Chó lông dài: 2 tuần. Chó lông ngắn: 3-4 tuần. <strong>Mèo:</strong> 1-3 tháng/lần. Mèo tự làm sạch rất tốt.</p><h2>Lưu ý quan trọng</h2><p>Nước ấm 37-38°C. Dùng sữa tắm <strong>CHUYÊN DỤNG</strong> cho pet (pH 7.0-7.5), KHÔNG dùng sữa tắm người (pH 5.5 — quá acid cho da pet).</p>'},

        # T3: CHI TIET
        {'title':'Royal Canin vs Taste of the Wild — So sánh chi tiết','slug':'royal-canin-vs-taste-of-the-wild','tier':'chi-tiet','category':'dinh-duong',
         'related_zone_slug':'dinh-duong',
         'tags':'Royal Canin,Taste of the Wild,so sánh,thức ăn hạt,review',
         'excerpt':'So sánh 2 thương hiệu thức ăn chó nổi tiếng: thành phần, giá, ưu nhược điểm. Nên chọn loại nào?',
         'reading_time':7,
         'embed_code':'<div class="at-carousel" data-network="shopee" data-keyword="royal canin dog food" data-limit="6"></div>',
         'content':'<h2>Royal Canin</h2><p><strong>Ưu:</strong> Nghiên cứu khoa học, chia theo giống chó cụ thể, dễ mua tại VN. <strong>Nhược:</strong> Chứa ngô/bột phụ phẩm, giá cao (350-500k/kg).</p><h2>Taste of the Wild</h2><p><strong>Ưu:</strong> Grain-free, protein từ thịt thật (bò rừng, cá hồi, hươu), không phụ phẩm. <strong>Nhược:</strong> Ít lựa chọn theo giống, khó mua hơn (400-600k/kg).</p>'},
        {'title':'Hướng dẫn chọn cát vệ sinh cho mèo — Bentonite vs Tofu vs Crystal','slug':'chon-cat-ve-sinh-meo','tier':'chi-tiet','category':'do-dung',
         'related_segment_slug':'meo','related_zone_slug':'do-dung',
         'tags':'cát vệ sinh,bentonite,tofu,crystal,khay cát,mèo',
         'excerpt':'So sánh 3 loại cát mèo phổ biến: bentonite, tofu, crystal. Ưu nhược điểm và chi phí hàng tháng.',
         'reading_time':6,
         'content':'<h2>Bentonite (cát khoáng)</h2><p>Vón cục tốt, mèo thích. Giá rẻ (30-60k/5L). Nhược: bụi nhiều, nặng, không xả bồn cầu được.</p><h2>Tofu (đậu nành)</h2><p>Ít bụi, nhẹ, xả bồn cầu OK. Giá 80-150k/6L. Nhược: vón kém hơn bentonite, ẩm dễ mốc.</p><h2>Crystal (silica)</h2><p>Hút mùi cực tốt, thay 1 lần/tháng. Giá 60-120k/3.8L. Nhược: không vón cục, mèo khó quen.</p>'},
    ]

    for ad in articles:
        a = Article(vertical_slug='pet', title=ad['title'], slug=ad['slug'], excerpt=ad.get('excerpt',''),
            content=ad.get('content',''), tier=ad.get('tier','chung'), category=ad.get('category',''),
            tags=ad.get('tags',''), related_segment_slug=ad.get('related_segment_slug',''),
            related_zone_slug=ad.get('related_zone_slug',''), embed_code=ad.get('embed_code',''),
            ai_generated=True, reading_time=ad.get('reading_time',5), views=random.randint(80,5000))
        db.session.add(a)
    db.session.commit()
    print(f'[OK] {len(articles)} pet articles seeded!')


# =============================================
# TRAVEL VERTICAL
# =============================================
def seed_travel():
    from models import db, Vertical, Segment, Zone, Part
    import random

    v = Vertical(name='Travel', slug='travel', description='Du lịch & Khách sạn — Khám phá, đặt phòng, trải nghiệm', icon='✈️', status='active')
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
                  'content':'<h2>Tổng quan</h2><p>Vịnh Hạ Long nằm ở Quảng Ninh, cách Hà Nội 170km. Di sản Thiên nhiên Thế giới UNESCO với <strong>1,969 hòn đảo</strong> đá vôi. Địa điểm du lịch #1 miền Bắc.</p><h2>Chi phí</h2><p><strong>Du thuyền 1 đêm:</strong> 1.5-8 triệu/người. <strong>Tour trong ngày:</strong> 500k-1.5 triệu. <strong>Kayak:</strong> 150-300k/giờ.</p><h2>Mùa đẹp nhất</h2><p>Tháng 3-5 và 9-11: thời tiết đẹp, ít mưa, tầm nhìn xa.</p>'},
                 {'vi':'Sapa & Fansipan','en':'Sapa & Fansipan','slug':'sapa-fansipan',
                  'desc':'Sapa — phố sương mù, ruộng bậc thang, chinh phục Fansipan 3,143m',
                  'tags':'Sapa,Fansipan,Lào Cai,trekking,ruộng bậc thang',
                  'content':'<h2>Sapa</h2><p>Thị trấn sương mù ở độ cao 1,600m, Lào Cai. Nổi tiếng với ruộng bậc thang, bản làng người H\'Mông, và đỉnh Fansipan.</p><h2>Chinh phục Fansipan</h2><p><strong>Cáp treo:</strong> 700k/người, 15 phút. <strong>Trekking:</strong> 2 ngày 1 đêm, 1.5-3 triệu (có porter). Nóc nhà Đông Dương — 3,143m.</p>'},
                 {'vi':'Ninh Bình — Tràng An','en':'Ninh Binh — Trang An','slug':'ninh-binh-trang-an',
                  'desc':'Tràng An — Di sản kép UNESCO, thuyền chèo qua hang động, cảnh núi non',
                  'tags':'Ninh Bình,Tràng An,Tam Cốc,thuyền,di sản',
                  'content':'<h2>Tràng An</h2><p>Di sản Văn hóa & Thiên nhiên Thế giới (kép). Hành trình thuyền chèo 2-3 giờ qua <strong>12 hang động</strong> và các đền chùa cổ. Vé: 200k/người.</p>'},
             ]},
            {'name':'Miền Trung','slug':'mien-trung','icon':'🏛️','color':'#3498db',
             'desc':'Đà Nẵng, Hội An, Huế, Phong Nha, Quy Nhơn',
             'parts':[
                 {'vi':'Hội An — Phố cổ','en':'Hoi An Ancient Town','slug':'hoi-an-pho-co',
                  'desc':'Phố cổ Hội An — đèn lồng, ẩm thực, may đo áo dài, đêm rằm',
                  'tags':'Hội An,phố cổ,đèn lồng,ẩm thực,UNESCO,Quảng Nam',
                  'content':'<h2>Phố cổ Hội An</h2><p>Di sản Văn hóa Thế giới UNESCO. Nổi tiếng với kiến trúc cổ, đèn lồng, và ẩm thực đặc sắc (Cao lầu, Mì Quảng, Bánh mì Phượng).</p><h2>Chi phí</h2><p>Vé tham quan phố cổ: 80k (5 điểm). Homestay: 200-500k/đêm. Ăn uống: 50-150k/bữa.</p>'},
                 {'vi':'Đà Nẵng — Biển & Bà Nà','en':'Da Nang','slug':'da-nang',
                  'desc':'Đà Nẵng — biển Mỹ Khê, Bà Nà Hills, Cầu Vàng, Ngũ Hành Sơn',
                  'tags':'Đà Nẵng,Bà Nà,Cầu Vàng,Mỹ Khê,biển',
                  'content':'<h2>Đà Nẵng</h2><p>Thành phố đáng sống nhất Việt Nam. <strong>Biển Mỹ Khê:</strong> Top 25 bãi biển đẹp nhất Châu Á. <strong>Bà Nà Hills:</strong> 600k vé cáp treo, khu vui chơi, Cầu Vàng iconic.</p>'},
                 {'vi':'Phong Nha — Hang động','en':'Phong Nha Caves','slug':'phong-nha',
                  'desc':'Vườn Quốc gia Phong Nha — Sơn Đoòng, Thiên Đường, Phong Nha',
                  'tags':'Phong Nha,Sơn Đoòng,hang động,Quảng Bình,UNESCO',
                  'content':'<h2>Hang Sơn Đoòng</h2><p>Hang động lớn nhất thế giới. Tour 4 ngày 3 đêm: ~70 triệu/người (giới hạn 1,000 khách/năm). <strong>Hang Thiên Đường:</strong> 250k vé, 31km dài. <strong>Phong Nha:</strong> 150k, đi thuyền.</p>'},
             ]},
            {'name':'Miền Nam','slug':'mien-nam','icon':'🌴','color':'#e74c3c',
             'desc':'TP.HCM, Phú Quốc, Đà Lạt, Cần Thơ, Vũng Tàu',
             'parts':[
                 {'vi':'Phú Quốc — Đảo ngọc','en':'Phu Quoc Island','slug':'phu-quoc',
                  'desc':'Phú Quốc — bãi biển đẹp, VinWonders, cáp treo, sunset, nước mắm',
                  'tags':'Phú Quốc,đảo,resort,VinWonders,biển,Kiên Giang',
                  'content':'<h2>Phú Quốc</h2><p>Đảo lớn nhất Việt Nam, Kiên Giang. <strong>Bãi Sao:</strong> bãi biển đẹp nhất. <strong>VinWonders:</strong> 880k vé. <strong>Cáp treo Hòn Thơm:</strong> 150k, dài nhất thế giới (7.9km).</p>'},
                 {'vi':'Đà Lạt — Thành phố sương mù','en':'Da Lat','slug':'da-lat',
                  'desc':'Đà Lạt — hoa, cà phê, thác, kiến trúc Pháp, cắm trại',
                  'tags':'Đà Lạt,Lâm Đồng,sương mù,cà phê,hoa,núi',
                  'content':'<h2>Đà Lạt</h2><p>Thành phố ngàn hoa, cao 1,500m. Nhiệt độ quanh năm 18-25°C. <strong>Highlight:</strong> Hồ Xuân Hương, Đường hầm Đất Sét, Thác Datanla, vườn hoa. Cà phê: 30-60k/ly (chất lượng rất cao).</p>'},
             ]},
        ],
        'quoc-te': [
            {'name':'Đông Nam Á','slug':'dong-nam-a','icon':'🏝️','color':'#f39c12',
             'desc':'Thái Lan, Bali, Singapore, Malaysia — gần, rẻ, dễ đi',
             'parts':[
                 {'vi':'Bangkok & Pattaya','en':'Bangkok & Pattaya','slug':'bangkok-pattaya',
                  'desc':'Thái Lan — chùa, chợ đêm, street food, show, biển Pattaya',
                  'tags':'Bangkok,Pattaya,Thái Lan,chùa,street food,Chatuchak',
                  'content':'<h2>Bangkok</h2><p>Thủ đô Thái Lan. <strong>Must-see:</strong> Grand Palace (500 baht), Wat Pho, Chatuchak Weekend Market, Chinatown. <strong>Street food:</strong> 40-100 baht/món (30-70k VND).</p><h2>Budget</h2><p>Vé bay VN-Bangkok: 1.5-4 triệu. Hostel: 200-400k/đêm. Ăn: 100-200k/ngày. Tour 4N3Đ: 5-10 triệu tổng.</p>'},
                 {'vi':'Bali — Đảo thần tiên','en':'Bali Island','slug':'bali',
                  'desc':'Bali — ruộng bậc thang, đền thiêng, lướt sóng, yoga retreat',
                  'tags':'Bali,Indonesia,đền,yoga,lướt sóng,Ubud,Seminyak',
                  'content':'<h2>Bali</h2><p>Đảo của thần — Indonesia. <strong>Ubud:</strong> Ruộng bậc thang Tegallalang, Monkey Forest. <strong>Seminyak:</strong> Beach club, sunset. <strong>Uluwatu:</strong> Đền trên vách đá, múa Kecak.</p>'},
             ]},
            {'name':'Đông Á','slug':'dong-a','icon':'🗼','color':'#e74c3c',
             'desc':'Nhật Bản, Hàn Quốc, Đài Loan — văn hóa, ẩm thực, mua sắm',
             'parts':[
                 {'vi':'Tokyo — Nhật Bản','en':'Tokyo Japan','slug':'tokyo',
                  'desc':'Tokyo — truyền thống & hiện đại, sushi, anime, cherry blossom',
                  'tags':'Tokyo,Nhật Bản,Japan,sushi,anime,sakura,Shibuya',
                  'content':'<h2>Tokyo</h2><p>Thủ đô Nhật Bản. <strong>Must-see:</strong> Shibuya Crossing, Asakusa/Senso-ji, Akihabara, Shinjuku Gyoen, Meiji Shrine. <strong>Ẩm thực:</strong> Sushi Tsukiji (500-3000 yen), Ramen (800-1500 yen).</p><h2>Budget</h2><p>Vé bay: 4-10 triệu. Hotel: 600k-2 triệu/đêm. JR Pass 7 ngày: 50,000 yen. Tour 7N: 20-40 triệu.</p>'},
                 {'vi':'Seoul — Hàn Quốc','en':'Seoul South Korea','slug':'seoul',
                  'desc':'Seoul — K-pop, K-drama, BBQ, skincare, cung điện, Myeongdong',
                  'tags':'Seoul,Hàn Quốc,Korea,K-pop,Myeongdong,BBQ',
                  'content':'<h2>Seoul</h2><p><strong>Must-see:</strong> Gyeongbokgung Palace (hanbok miễn phí vào), Myeongdong shopping, Bukchon Hanok Village, Namsan Tower. <strong>Ẩm thực:</strong> Korean BBQ (15,000-30,000 won), tteokbokki street food.</p>'},
             ]},
        ],
        'khach-san': [
            {'name':'Budget & Hostel','slug':'budget','icon':'🏠','color':'#27ae60',
             'desc':'Khách sạn giá rẻ, hostel, homestay — dưới 500k/đêm',
             'parts':[
                 {'vi':'Cách đặt phòng giá rẻ','en':'Budget Booking Tips','slug':'cach-dat-phong-gia-re',
                  'desc':'Mẹo đặt phòng giá tốt: so sánh OTA, flash sale, loyalty program',
                  'tags':'đặt phòng,giá rẻ,OTA,Booking,Agoda,flash sale',
                  'content':'<h2>5 mẹo đặt phòng giá tốt</h2><p><strong>1. So sánh OTA:</strong> Cùng phòng, Agoda có thể rẻ hơn Booking 20%. <strong>2. Đặt trước 2-3 tháng.</strong> <strong>3. Dùng VPN:</strong> Giá hiển thị khác nhau theo quốc gia. <strong>4. Đặt trực tiếp:</strong> Hotel website thường có best rate guarantee. <strong>5. Flash sale:</strong> Agoda 11/11, Booking Black Friday.</p>'},
                 {'vi':'Homestay vs Hostel vs Hotel','en':'Accommodation Types','slug':'homestay-hostel-hotel',
                  'desc':'So sánh 3 loại hình lưu trú: homestay, hostel, hotel — phù hợp với ai?',
                  'tags':'homestay,hostel,hotel,so sánh,lưu trú,backpacker',
                  'content':'<h2>Homestay</h2><p>Ở cùng gia đình bản địa. Giá: 100-400k/đêm. Phù hợp: trải nghiệm văn hóa, trekking.</p><h2>Hostel</h2><p>Giường dorm chia sẻ. Giá: 100-250k/đêm. Phù hợp: solo traveler, backpacker, kết bạn.</p><h2>Hotel</h2><p>Phòng riêng, tiện nghi. Giá từ 300k+. Phù hợp: gia đình, cặp đôi, cần riêng tư.</p>'},
             ]},
            {'name':'4-5 Sao & Resort','slug':'resort','icon':'🌟','color':'#9b59b6',
             'desc':'Resort cao cấp, khách sạn 5 sao — trải nghiệm sang trọng',
             'parts':[
                 {'vi':'Top Resort Việt Nam','en':'Best Vietnam Resorts','slug':'top-resort-viet-nam',
                  'desc':'Top 10 resort đẹp nhất Việt Nam: InterContinental, Six Senses, Amanoi',
                  'tags':'resort,5 sao,InterContinental,Six Senses,Amanoi,luxury',
                  'content':'<h2>Top 5 Resort</h2><p><strong>1. Amanoi (Ninh Thuận):</strong> Ultra-luxury, 20-50 triệu/đêm. <strong>2. Six Senses Côn Đảo:</strong> 15-30 triệu/đêm. <strong>3. InterContinental Đà Nẵng:</strong> 5-15 triệu/đêm, Sun Peninsula. <strong>4. The Nam Hai Hội An:</strong> 8-20 triệu/đêm. <strong>5. Fusion Maia Đà Nẵng:</strong> 3-8 triệu/đêm, all-spa-inclusive.</p>'},
                 {'vi':'Cách chọn resort phù hợp','en':'How to Choose a Resort','slug':'cach-chon-resort',
                  'desc':'Tiêu chí chọn resort: vị trí, view, F&B, spa, pool, giá trị thực',
                  'tags':'chọn resort,tiêu chí,review,đánh giá,value',
                  'content':'<h2>6 tiêu chí đánh giá</h2><p><strong>1. Vị trí:</strong> Beachfront hay hillside? <strong>2. View phòng:</strong> Sea view thường đắt hơn 30-50%. <strong>3. F&B:</strong> Nhà hàng trong resort có ngon không? <strong>4. Pool & Beach:</strong> Private beach hay public? <strong>5. Spa:</strong> In-house hay outsource? <strong>6. Giá trị thực:</strong> So sánh giá/trải nghiệm.</p>'},
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
    from models import db, Article
    import random

    articles = [
        # T1: NGANH
        {'title':'Du lịch Việt Nam 2025 — Xu hướng & Điểm đến hot','slug':'du-lich-viet-nam-2025','tier':'nganh','category':'xu-huong',
         'tags':'du lịch,Việt Nam,2025,xu hướng,điểm đến',
         'excerpt':'Phân tích xu hướng du lịch VN 2025: staycation, du lịch trải nghiệm, digital nomad, và 5 điểm đến hot nhất.',
         'reading_time':8,
         'content':'<h2>5 xu hướng lớn</h2><p><strong>1. Staycation:</strong> Nghỉ dưỡng gần nhà, resort ngoại ô. <strong>2. Du lịch trải nghiệm:</strong> Trekking, homestay bản địa, farm tour. <strong>3. Digital nomad:</strong> Làm việc + du lịch, Đà Lạt & Hội An là hub chính. <strong>4. Wellness travel:</strong> Yoga retreat, detox, spa. <strong>5. Du lịch xanh:</strong> Eco-resort, bảo tồn, zero waste.</p>'},
        {'title':'Cách lên kế hoạch du lịch tiết kiệm — Hướng dẫn A-Z','slug':'cach-len-ke-hoach-du-lich-tiet-kiem','tier':'nganh','category':'huong-dan',
         'tags':'tiết kiệm,kế hoạch,budget,mẹo,đặt vé,lịch trình',
         'excerpt':'Hướng dẫn lên kế hoạch du lịch từ A-Z: đặt vé rẻ, chọn lưu trú, lên lịch trình, và mẹo tiết kiệm tới 50%.',
         'reading_time':10,
         'content':'<h2>1. Đặt vé bay</h2><p>Đặt trước 2-3 tháng. Theo dõi flash sale VietJet, Bamboo Airways. Dùng Google Flights so sánh. Bay thứ 3-4 rẻ nhất.</p><h2>2. Chọn lưu trú</h2><p>So sánh Agoda vs Booking vs Traveloka. Đặt phòng free cancellation. Check review gần nhất (< 3 tháng).</p>'},
        {'title':'Bảo hiểm du lịch — Có cần thiết không? Chọn gói nào?','slug':'bao-hiem-du-lich','tier':'nganh','category':'bao-hiem',
         'tags':'bảo hiểm,du lịch,quốc tế,trễ chuyến,hành lý,y tế',
         'excerpt':'Bảo hiểm du lịch: khi nào cần mua, gói nào phù hợp, và cách claim bồi thường.',
         'reading_time':7,
         'content':'<h2>Khi nào cần?</h2><p><strong>Bắt buộc:</strong> Du lịch Schengen (EU), một số nước yêu cầu. <strong>Nên mua:</strong> Tour dài ngày, sport adventure, đi xa. <strong>Có thể bỏ qua:</strong> Tour ngắn trong nước, gần nhà.</p><h2>Gói phổ biến</h2><p>Bảo Việt, Liberty, AIG — 50-200k/ngày. Cover: y tế (500 triệu+), trễ chuyến (1-3 triệu), mất hành lý (5-15 triệu).</p>'},

        # T2: CHUNG
        {'title':'Du lịch miền Bắc — Lịch trình 5N4Đ hoàn hảo','slug':'du-lich-mien-bac-5n4d','tier':'chung','category':'lich-trinh',
         'related_segment_slug':'trong-nuoc','related_zone_slug':'mien-bac',
         'tags':'miền Bắc,Hà Nội,Hạ Long,Sapa,Ninh Bình,5 ngày',
         'excerpt':'Lịch trình 5 ngày 4 đêm khám phá miền Bắc: Hà Nội → Hạ Long → Ninh Bình → Sapa. Budget 5-10 triệu.',
         'reading_time':12,
         'content':'<h2>Ngày 1-2: Hà Nội</h2><p>Phố cổ, Hồ Gươm, Bún chả, Phở, Egg Coffee. <strong>Ngày 2:</strong> Temple of Literature, West Lake, Train Street.</p><h2>Ngày 3: Hạ Long</h2><p>Du thuyền 1 ngày: 800k-2 triệu. Hang Sửng Sốt, Đảo Ti Tớp, kayak.</p><h2>Ngày 4: Ninh Bình</h2><p>Tràng An (thuyền 2-3h, 200k), Hang Múa (100k), Bích Động.</p><h2>Ngày 5: Về HN</h2><p>Mua quà: ô mai, cốm, bánh cốm.</p>'},
        {'title':'Ẩm thực đường phố Việt Nam — 20 món phải thử','slug':'am-thuc-duong-pho-viet-nam','tier':'chung','category':'am-thuc',
         'tags':'ẩm thực,street food,phở,bún chả,bánh mì,Việt Nam',
         'excerpt':'20 món ăn đường phố Việt Nam nổi tiếng thế giới: phở, bún chả, bánh mì, bún bò Huế...',
         'reading_time':8,
         'content':'<h2>Miền Bắc</h2><p><strong>Phở Hà Nội:</strong> 40-60k. <strong>Bún chả:</strong> 40-50k (Obama ate at Bún Chả Hương Liên). <strong>Bún đậu mắm tôm:</strong> 50-80k.</p><h2>Miền Trung</h2><p><strong>Mì Quảng:</strong> 30-50k. <strong>Bún bò Huế:</strong> 40-60k. <strong>Bánh mì Phượng (Hội An):</strong> 25k — CNN Top 25 street food.</p><h2>Miền Nam</h2><p><strong>Bánh mì Sài Gòn:</strong> 15-30k. <strong>Hủ tiếu:</strong> 30-50k. <strong>Cơm tấm:</strong> 30-50k.</p>'},
        {'title':'Visa du lịch — Hướng dẫn xin visa các nước phổ biến','slug':'visa-du-lich-huong-dan','tier':'chung','category':'visa',
         'tags':'visa,hộ chiếu,miễn visa,eVisa,Schengen,Nhật',
         'excerpt':'Hướng dẫn xin visa du lịch: Nhật, Hàn, Schengen, Mỹ, Úc. Điều kiện, hồ sơ, và mẹo đậu visa.',
         'reading_time':10,
         'content':'<h2>Miễn visa (hộ chiếu VN)</h2><p>Thái Lan (30 ngày), Singapore (30), Malaysia (30), Indonesia (30), Philippines (21), Campuchia (30), Myanmar (14). Tổng: ~25 nước miễn visa.</p><h2>Visa dễ xin</h2><p><strong>Nhật:</strong> eVisa online, 3-5 ngày. <strong>Hàn:</strong> Cần chứng minh tài chính. <strong>Đài Loan:</strong> Miễn visa nếu có visa Nhật/Hàn/Schengen còn hạn.</p>'},

        # T3: CHI TIET
        {'title':'Review InterContinental Đà Nẵng Sun Peninsula — Có đáng giá?','slug':'review-intercontinental-da-nang','tier':'chi-tiet','category':'review-resort',
         'related_segment_slug':'khach-san','related_zone_slug':'resort',
         'tags':'InterContinental,Đà Nẵng,resort,5 sao,review,Sun Peninsula',
         'excerpt':'Review chi tiết InterContinental Đà Nẵng: phòng, view, F&B, spa, pool — và liệu giá 5-15 triệu/đêm có xứng đáng?',
         'reading_time':8,
         'embed_code':'<div class="at-carousel" data-network="agoda" data-keyword="InterContinental Da Nang" data-limit="3"></div>',
         'content':'<h2>Tổng quan</h2><p>Thiết kế bởi Bill Bensley trên bán đảo Sơn Trà. 4 tầng: Heaven, Sky, Earth, Sea — mỗi tầng một concept khác nhau.</p><h2>Điểm cộng</h2><p>View biển tuyệt đẹp, kiến trúc độc đáo, La Maison 1888 (fine dining top VN), private beach, spa chất lượng.</p><h2>Điểm trừ</h2><p>Xa trung tâm (30 phút), giá premium (đặc biệt minibar), bể bơi infinity đông vào cuối tuần.</p>'},
        {'title':'Hướng dẫn trekking Sapa — Lịch trình, chuẩn bị, chi phí','slug':'huong-dan-trekking-sapa','tier':'chi-tiet','category':'trekking',
         'related_segment_slug':'trong-nuoc','related_zone_slug':'mien-bac',
         'tags':'trekking,Sapa,Fansipan,bản Cát Cát,ruộng bậc thang',
         'excerpt':'Hướng dẫn chi tiết trekking Sapa: chuẩn bị gì, mang gì, lịch trình 2N1Đ và 3N2Đ, chi phí từ 1 đến 5 triệu.',
         'reading_time':10,
         'content':'<h2>Chuẩn bị</h2><p><strong>Giày:</strong> Giày trekking chống trượt (bắt buộc). <strong>Quần áo:</strong> Layers (nhiều lớp), áo gió, áo mưa. <strong>Balô:</strong> 20-30L. <strong>Khác:</strong> Gậy trekking, kem chống nắng, thuốc cá nhân.</p><h2>Lịch trình 2N1Đ</h2><p><strong>Ngày 1:</strong> Sapa → Bản Cát Cát → Bản Tả Van (trekking 5-6h). Ngủ homestay. <strong>Ngày 2:</strong> Tả Van → Bản Giang Tà Chải → Sapa (4-5h). Chi phí: 1.5-3 triệu (guide + homestay + ăn).</p>'},
        {'title':'So sánh Agoda vs Booking.com vs Traveloka — Đặt ở đâu rẻ nhất?','slug':'agoda-vs-booking-vs-traveloka','tier':'chi-tiet','category':'dat-phong',
         'related_segment_slug':'khach-san',
         'tags':'Agoda,Booking,Traveloka,OTA,đặt phòng,so sánh,giá rẻ',
         'excerpt':'So sánh 3 OTA lớn nhất: Agoda, Booking.com, Traveloka. Giá, ưu đãi, chính sách hủy, và mẹo chọn nền tảng.',
         'reading_time':7,
         'content':'<h2>Agoda</h2><p>Giá thường rẻ nhất Đông Nam Á. Flash sale thường xuyên. AgodaCash 5-7% hoàn tiền. Nhược: UI hơi rối, giá ẩn phí.</p><h2>Booking.com</h2><p>Phòng nhiều nhất thế giới. Free cancellation phổ biến. Genius program giảm 10-15%. Nhược: Giá đôi khi cao hơn Agoda 10-20% khu vực Châu Á.</p><h2>Traveloka</h2><p>Tích hợp vé bay + hotel. PayLater trả sau. Mạnh ở VN & Indonesia. Nhược: Ít lựa chọn quốc tế.</p>'},
    ]

    for ad in articles:
        a = Article(vertical_slug='travel', title=ad['title'], slug=ad['slug'], excerpt=ad.get('excerpt',''),
            content=ad.get('content',''), tier=ad.get('tier','chung'), category=ad.get('category',''),
            tags=ad.get('tags',''), related_segment_slug=ad.get('related_segment_slug',''),
            related_zone_slug=ad.get('related_zone_slug',''), embed_code=ad.get('embed_code',''),
            ai_generated=True, reading_time=ad.get('reading_time',5), views=random.randint(100,8000))
        db.session.add(a)
    db.session.commit()
    print(f'[OK] {len(articles)} travel articles seeded!')

def seed_products_pet_travel():
    from models import db, Vertical, Segment, Zone, Part, AffiliateLink
    import random

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
                                conversions=random.randint(0, 30))
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
                                conversions=random.randint(0, 40))
                            db.session.add(al)

    db.session.commit()
    pet_count = AffiliateLink.query.join(Part).join(Zone).join(Segment).join(Vertical).filter(Vertical.slug=='pet').count() if pet else 0
    travel_count = AffiliateLink.query.join(Part).join(Zone).join(Segment).join(Vertical).filter(Vertical.slug=='travel').count() if travel else 0
    print(f'[OK] Products seeded: Pet={pet_count}, Travel={travel_count}')

def seed_hotels():
    from models import db, Hotel
    import random
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
    from models import db, Attraction
    import random
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
