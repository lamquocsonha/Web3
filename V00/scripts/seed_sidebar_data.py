"""
Seed sidebar data: Articles + Banners
Run: python scripts/seed_sidebar_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Vertical, Article, Banner
from datetime import datetime, timedelta
import random

def run_migrations():
    """Run necessary database migrations"""
    print('[+] Running database migrations...')

    # Add template column to vertical table (if not exists)
    try:
        db.session.execute(db.text("SELECT template FROM vertical LIMIT 1"))
        print('  ✓ Template column already exists')
    except:
        print('  + Adding template column to vertical table...')
        db.session.execute(db.text("ALTER TABLE vertical ADD COLUMN template VARCHAR(20) DEFAULT 'general'"))
        db.session.commit()

        # Set templates for existing verticals
        template_mapping = {'car': 'general', 'pet': 'general', 'bike': 'general', 'travel': 'travel'}
        verticals = Vertical.query.all()
        for v in verticals:
            v.template = template_mapping.get(v.slug, 'general')
        db.session.commit()
        print('  ✓ Template column added and populated')

    # Create banner table (if not exists)
    try:
        db.session.execute(db.text("SELECT COUNT(*) FROM banner LIMIT 1"))
        print('  ✓ Banner table already exists')
    except:
        print('  + Creating banner table...')
        db.session.execute(db.text("""
            CREATE TABLE banner (
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
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        db.session.commit()
        print('  ✓ Banner table created')


def seed_articles():
    """Create additional articles for each vertical"""
    print('[+] Seeding articles for sidebar...')

    verticals = Vertical.query.filter_by(status='published').all()

    article_templates = {
        'bike': [
            {
                'title': 'Hệ thống truyền động xe đạp: Groupset Shimano 105 vs Ultegra vs Dura-Ace',
                'tier': 'chung',
                'category': 'he-thong-truyen-dong',
                'excerpt': 'So sánh chi tiết 3 dòng groupset phổ biến nhất của Shimano: giúp bạn quyết định nâng cấp phù hợp với ngân sách và nhu cầu sử dụng.',
                'reading_time': 10,
                'views': 8520
            },
            {
                'title': 'Chọn xe đạp Road Bike cho người mới: Từ 10 triệu đến 30 triệu',
                'tier': 'nganh',
                'category': 'mua-xe',
                'excerpt': 'Hướng dẫn chi tiết cách chọn road bike phù hợp với ngân sách và mục đích sử dụng cho người mới bắt đầu.',
                'reading_time': 8,
                'views': 12340
            },
            {
                'title': 'Tại sao phải bảo dưỡng sên?',
                'tier': 'chi-tiet',
                'category': 'bao-duong',
                'excerpt': 'Sên là bộ phận tiếp xúc trực tiếp với bìn đất, nước mưa, bụi bẩn. Nếu không vệ sinh thường xuyên, sên sẽ gỉ sét, kéu cọt kẹt, mòn nhanh và làm hỏng cassette.',
                'reading_time': 5,
                'views': 4230
            },
            {
                'title': 'Lịch bảo dưỡng xe đạp định kỳ theo km',
                'tier': 'chung',
                'category': 'bao-duong',
                'excerpt': 'Lịch trình bảo dưỡng chi tiết theo từng mốc km: 500km, 1000km, 3000km, 5000km - giúp xe luôn hoạt động tốt nhất.',
                'reading_time': 12,
                'views': 9870
            },
            {
                'title': 'Cách điều chỉnh phanh đĩa xe đạp không bị kêu',
                'tier': 'chi-tiet',
                'category': 'phanh',
                'excerpt': 'Hướng dẫn từng bước điều chỉnh phanh đĩa cơ và dầu để không bị kêu, cọ má phanh, đảm bảo hiệu suất phanh tốt nhất.',
                'reading_time': 7,
                'views': 6540
            }
        ],
        'car': [
            {
                'title': 'So sánh động cơ Turbo và động cơ hút khí tự nhiên',
                'tier': 'chung',
                'category': 'dong-co',
                'excerpt': 'Phân tích ưu nhược điểm của động cơ turbo và NA: công suất, mô-men xoắn, tiêu hao nhiên liệu, độ bền và chi phí bảo dưỡng.',
                'reading_time': 10,
                'views': 15230
            },
            {
                'title': 'Chọn xe SUV 7 chỗ: Honda CR-V vs Mazda CX-8 vs Hyundai Santa Fe',
                'tier': 'nganh',
                'category': 'mua-xe',
                'excerpt': 'So sánh toàn diện 3 mẫu SUV 7 chỗ phổ biến nhất thị trường: thiết kế, trang bị, vận hành, giá cả và chi phí vận hành.',
                'reading_time': 15,
                'views': 23450
            },
            {
                'title': 'Tại sao cần thay dầu động cơ định kỳ?',
                'tier': 'chi-tiet',
                'category': 'bao-duong',
                'excerpt': 'Dầu động cơ đảm bảo bôi trơn, làm mát, làm sạch và chống gỉ. Nếu không thay định kỳ sẽ gây mòn động cơ, tăng tiêu hao nhiên liệu.',
                'reading_time': 6,
                'views': 8920
            },
            {
                'title': 'Hệ thống treo độc lập vs treo phụ thuộc: Nên chọn loại nào?',
                'tier': 'chung',
                'category': 'he-thong-treo',
                'excerpt': 'Giải thích chi tiết cách hoạt động, ưu nhược điểm của treo độc lập và treo phụ thuộc - giúp chọn xe phù hợp với nhu cầu.',
                'reading_time': 9,
                'views': 11200
            },
            {
                'title': 'Lốp Run-flat là gì? Có nên sử dụng?',
                'tier': 'chi-tiet',
                'category': 'lop-xe',
                'excerpt': 'Lốp run-flat cho phép chạy 80km sau khi bị thủng. Phân tích ưu nhược điểm, giá thành và khả năng sử dụng ở Việt Nam.',
                'reading_time': 7,
                'views': 7650
            }
        ],
        'pet': [
            {
                'title': 'Lịch tiêm phòng cho chó con từ 0-12 tháng tuổi',
                'tier': 'chung',
                'category': 'suc-khoe',
                'excerpt': 'Lịch trình tiêm phòng đầy đủ cho chó con: vắc-xin 6 trong 1, dại, viêm gan... Chi phí và lưu ý khi tiêm.',
                'reading_time': 8,
                'views': 18230
            },
            {
                'title': 'Chó Corgi vs Shiba vs Pomeranian: Nên nuôi giống nào?',
                'tier': 'nganh',
                'category': 'giong-cho',
                'excerpt': 'So sánh 3 giống chó cảnh phổ biến: tính cách, kích thước, chăm sóc, giá cả và phù hợp với không gian sống.',
                'reading_time': 12,
                'views': 25670
            },
            {
                'title': 'Mèo rụng lông nhiều: Nguyên nhân và cách khắc phục',
                'tier': 'chi-tiet',
                'category': 'suc-khoe',
                'excerpt': 'Phân tích nguyên nhân rụng lông: thay mùa, thiếu dinh dưỡng, stress, dị ứng. Cách bổ sung Omega-3 hiệu quả.',
                'reading_time': 6,
                'views': 14520
            },
            {
                'title': 'Thức ăn hạt vs thức ăn ướt cho mèo: Loại nào tốt hơn?',
                'tier': 'chung',
                'category': 'dinh-duong',
                'excerpt': 'So sánh ưu nhược điểm của thức ăn khô và ướt: dinh dưỡng, giá thành, bảo quản và phù hợp với từng giống mèo.',
                'reading_time': 10,
                'views': 16890
            },
            {
                'title': 'Cách huấn luyện chó đi vệ sinh đúng chỗ trong 2 tuần',
                'tier': 'chi-tiet',
                'category': 'huan-luyen',
                'excerpt': 'Phương pháp huấn luyện từng bước, kiên nhẫn và nhất quán - giúp chó con học đi vệ sinh đúng chỗ nhanh chóng.',
                'reading_time': 9,
                'views': 22340
            }
        ],
        'travel': [
            {
                'title': 'So sánh Agoda vs Booking.com vs Traveloka — Đặt ở đâu rẻ nhất?',
                'tier': 'nganh',
                'category': 'dat-phong',
                'excerpt': 'So sánh 3 OTA lớn nhất: Agoda, Booking.com, Traveloka. Giá, ưu đãi, chính sách hủy, và meo chọn nền tảng phù hợp.',
                'reading_time': 7,
                'views': 34520
            },
            {
                'title': 'Review InterContinental Đà Nẵng Sun Peninsula — Có đáng giá 5-15 triệu/đêm?',
                'tier': 'chi-tiet',
                'category': 'review-resort',
                'excerpt': 'Review chi tiết InterContinental Đà Nẵng: phòng, view, F&B, spa, pool — và liệu giá 5-15 triệu/đêm có xứng đáng?',
                'reading_time': 8,
                'views': 28670
            },
            {
                'title': 'Visa du lịch — Hướng dẫn xin visa các nước phổ biến',
                'tier': 'chung',
                'category': 'visa',
                'excerpt': 'Hướng dẫn xin visa du lịch: Nhật, Hàn, Schengen, Mỹ, Úc. Điều kiện, hồ sơ, và mẹo đậu visa dễ dàng.',
                'reading_time': 10,
                'views': 19880
            },
            {
                'title': 'Bảo hiểm du lịch — Có cần thiết không? Chọn gói nào?',
                'tier': 'chi-tiet',
                'category': 'bao-hiem',
                'excerpt': 'Phân tích bảo hiểm du lịch: tai nạn, y tế, hủy chuyến, mất hành lý. Gợi ý gói phù hợp với từng loại hình du lịch.',
                'reading_time': 6,
                'views': 12450
            },
            {
                'title': 'Cách lên kế hoạch du lịch tiết kiệm — Hướng dẫn A-Z',
                'tier': 'chung',
                'category': 'ke-hoach',
                'excerpt': 'Lên kế hoạch chi tiết: chọn điểm đến, bay giờ rẻ, ở đâu, ăn gì, di chuyển thế nào - tối ưu ngân sách nhưng vẫn trọn vẹn.',
                'reading_time': 15,
                'views': 27890
            }
        ]
    }

    for vertical in verticals:
        if vertical.slug not in article_templates:
            continue

        templates = article_templates[vertical.slug]

        for i, template in enumerate(templates):
            # Check if article already exists
            existing = Article.query.filter_by(
                vertical_slug=vertical.slug,
                title=template['title']
            ).first()

            if existing:
                print(f'  - Article already exists: {template["title"][:50]}...')
                continue

            # Create slug
            slug = template['title'].lower()
            for old, new in [(':', ''), ('?', ''), (' — ', ' '), ('  ', ' '), (' ', '-')]:
                slug = slug.replace(old, new)

            # Generate content (lorem ipsum style)
            content = f'''<p>{template['excerpt']}</p>

<h2>Giới thiệu</h2>
<p>Trong bài viết này, chúng ta sẽ tìm hiểu chi tiết về {template['title'].lower()}. Đây là kiến thức quan trọng giúp bạn hiểu rõ hơn về lĩnh vực {vertical.name}.</p>

<h2>Phân tích chi tiết</h2>
<p>Để hiểu rõ vấn đề, chúng ta cần xem xét nhiều góc độ khác nhau. Mỗi khía cạnh đều có những đặc điểm riêng, ưu điểm và nhược điểm cần cân nhắc.</p>

<h3>Ưu điểm</h3>
<ul>
<li>Hiệu quả cao trong điều kiện sử dụng phù hợp</li>
<li>Tiết kiệm chi phí so với các phương án khác</li>
<li>Dễ dàng bảo trì và nâng cấp</li>
<li>Phù hợp với nhiều đối tượng người dùng</li>
</ul>

<h3>Nhược điểm</h3>
<ul>
<li>Yêu cầu đầu tư ban đầu tương đối cao</li>
<li>Cần có kiến thức chuyên môn để sử dụng tối ưu</li>
<li>Không phù hợp với mọi trường hợp</li>
</ul>

<h2>Lời khuyên từ chuyên gia</h2>
<p>Dựa trên kinh nghiệm thực tế, chúng tôi khuyên bạn nên cân nhắc kỹ lưỡng trước khi quyết định. Mỗi trường hợp cụ thể sẽ có yêu cầu khác nhau.</p>

<h2>Kết luận</h2>
<p>Hiểu rõ về {template['title'].lower()} sẽ giúp bạn đưa ra quyết định đúng đắn. Hy vọng bài viết này đã cung cấp thông tin hữu ích cho bạn.</p>
'''

            # Random creation time (last 30 days)
            days_ago = random.randint(0, 30)
            created_at = datetime.utcnow() - timedelta(days=days_ago)

            article = Article(
                vertical_slug=vertical.slug,
                title=template['title'],
                slug=slug,
                excerpt=template['excerpt'],
                content=content,
                tier=template['tier'],
                category=template['category'],
                tags=f"{vertical.slug}, {template['category']}, kiến thức",
                reading_time=template['reading_time'],
                views=template['views'],
                status='published',
                ai_generated=False,
                created_at=created_at
            )

            db.session.add(article)
            print(f'  ✓ Created: {article.title[:60]}...')

    db.session.commit()
    print(f'[✓] Articles seeded successfully!')


def seed_banners():
    """Create sidebar banner ads"""
    print('[+] Seeding banner ads...')

    verticals = Vertical.query.all()

    banner_templates = [
        {
            'name': 'Shopee Affiliate - Top Banner',
            'placement': 'sidebar',
            'position': 1,
            'vertical_slug': '',  # Global - all verticals
            'html_code': '''<div style="background: linear-gradient(135deg, #ee4d2d, #ff6433); padding: 24px; border-radius: 8px; text-align: center; color: white;">
    <div style="font-size: 24px; font-weight: 800; margin-bottom: 8px;">🛍️ SHOPEE SALE</div>
    <div style="font-size: 14px; margin-bottom: 16px;">Giảm đến 50% - Freeship toàn quốc</div>
    <a href="https://shopee.vn" target="_blank" rel="nofollow sponsored" style="display: inline-block; background: white; color: #ee4d2d; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 700;">
        XEM NGAY →
    </a>
</div>'''
        },
        {
            'name': 'Lazada Affiliate - Bottom Banner',
            'placement': 'sidebar',
            'position': 2,
            'vertical_slug': '',  # Global
            'html_code': '''<div style="background: linear-gradient(135deg, #0f146d, #1a1f8f); padding: 24px; border-radius: 8px; text-align: center; color: white;">
    <div style="font-size: 20px; font-weight: 700; margin-bottom: 8px;">⚡ LAZADA FLASH SALE</div>
    <div style="font-size: 13px; margin-bottom: 16px;">Deal hot giờ vàng - Voucher 500K</div>
    <a href="https://lazada.vn" target="_blank" rel="nofollow sponsored" style="display: inline-block; background: #ff9800; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 600;">
        MUA NGAY
    </a>
</div>'''
        },
        {
            'name': 'Bike Banner - Decathlon',
            'placement': 'sidebar',
            'position': 1,
            'vertical_slug': 'bike',
            'html_code': '''<div style="background: linear-gradient(135deg, #0082c3, #00a0e3); padding: 20px; border-radius: 8px; text-align: center; color: white;">
    <div style="font-size: 18px; font-weight: 700; margin-bottom: 6px;">🚴 DECATHLON</div>
    <div style="font-size: 12px; margin-bottom: 12px;">Phụ kiện xe đạp chính hãng</div>
    <a href="#" target="_blank" rel="nofollow" style="display: inline-block; background: white; color: #0082c3; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-weight: 600; font-size: 13px;">
        XEM NGAY
    </a>
</div>'''
        },
        {
            'name': 'Travel Banner - Agoda',
            'placement': 'sidebar',
            'position': 1,
            'vertical_slug': 'travel',
            'html_code': '''<div style="background: linear-gradient(135deg, #d32f2f, #f44336); padding: 20px; border-radius: 8px; text-align: center; color: white;">
    <div style="font-size: 18px; font-weight: 700; margin-bottom: 6px;">🏨 AGODA</div>
    <div style="font-size: 12px; margin-bottom: 12px;">Đặt phòng khách sạn - Giảm 20%</div>
    <a href="#" target="_blank" rel="nofollow sponsored" style="display: inline-block; background: white; color: #d32f2f; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-weight: 600; font-size: 13px;">
        ĐẶT NGAY
    </a>
</div>'''
        }
    ]

    for template in banner_templates:
        # Check if banner already exists
        existing = Banner.query.filter_by(name=template['name']).first()
        if existing:
            print(f'  - Banner already exists: {template["name"]}')
            continue

        banner = Banner(
            name=template['name'],
            placement=template['placement'],
            position=template['position'],
            vertical_slug=template['vertical_slug'],
            html_code=template['html_code'],
            is_active=True,
            impressions=random.randint(1000, 10000),
            clicks=random.randint(50, 500)
        )

        db.session.add(banner)
        print(f'  ✓ Created: {banner.name}')

    db.session.commit()
    print(f'[✓] Banners seeded successfully!')


def main():
    with app.app_context():
        print('='*60)
        print('SEEDING SIDEBAR DATA')
        print('='*60)

        run_migrations()
        print()
        seed_articles()
        print()
        seed_banners()

        print()
        print('='*60)
        print('✓ ALL DATA SEEDED SUCCESSFULLY!')
        print('='*60)
        print()
        print('Sidebar should now display:')
        print('  - Featured articles (top by views)')
        print('  - Related articles (same category/tier)')
        print('  - Banner ads (position 1 & 2)')
        print()
        print('Refresh your vertical pages to see the changes!')


if __name__ == '__main__':
    main()
