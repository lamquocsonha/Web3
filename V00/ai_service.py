"""
AI Content Generation Service
Supports OpenAI GPT-4o and compatible providers.
Generates articles per tier (chi-tiet / chung / nganh) with Vietnamese SEO focus.
"""
import json, re, os
from datetime import datetime

# ─── Provider Config ────────────────────────────────────────────
DEFAULT_PROVIDER = 'openai'
DEFAULT_MODEL = 'gpt-4o-mini'

def _get_openai_client():
    """Get OpenAI client using API key from env or SiteSettings"""
    import openai
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        try:
            from models import SiteSettings
            api_key = SiteSettings.get('openai_api_key', '')
        except:
            pass
    if not api_key:
        raise ValueError('OPENAI_API_KEY not set. Add it in Settings or environment.')
    return openai.OpenAI(api_key=api_key)


# ─── Prompt Templates ──────────────────────────────────────────

SYSTEM_PROMPT = """Bạn là chuyên gia viết bài SEO tiếng Việt cho website affiliate.
Quy tắc:
- Viết bằng tiếng Việt tự nhiên, dễ hiểu, không máy móc
- Dùng HTML (h2, h3, p, ul/li, strong) — KHÔNG dùng markdown
- Mỗi bài phải có: mở bài hấp dẫn, thân bài chi tiết, kết luận + CTA
- Tự nhiên chèn keywords vào heading và paragraph
- Không bịa số liệu cụ thể (giá chính xác, %) trừ khi được cung cấp
- Không dùng emoji trong bài viết
- Trả về JSON với format: {"title": "...", "content": "<html>...", "excerpt": "...", "tags": "tag1,tag2,tag3"}"""

TIER_PROMPTS = {
    # ── Chi tiết: Review / hướng dẫn 1 sản phẩm cụ thể ──
    'chi-tiet': """Viết bài REVIEW CHI TIẾT về sản phẩm/chủ đề sau.

Vertical: {vertical_name}
Segment: {segment_name}
Zone: {zone_name}
Sản phẩm: {part_name} ({part_name_en})
Mô tả: {part_description}
OEM Code: {oem_code}

Sản phẩm liên quan trong cùng zone:
{related_parts}

Yêu cầu:
- Độ dài: 800-1200 từ
- Cấu trúc: {part_name} là gì → Vai trò/chức năng → Dấu hiệu cần thay → Cách chọn mua → Lưu ý lắp đặt/sử dụng
- Đề cập OEM code nếu có
- SEO keywords tự nhiên trong headings
- Kết bài: gợi ý xem thêm sản phẩm liên quan

Tags gợi ý: {suggested_tags}""",

    # ── Chung: So sánh / hướng dẫn chọn trong 1 zone ──
    'chung': """Viết bài HƯỚNG DẪN TỔNG HỢP cho zone/chủ đề sau.

Vertical: {vertical_name}
Segment: {segment_name}
Zone: {zone_name}
Mô tả zone: {zone_description}

Các sản phẩm trong zone:
{all_parts}

Yêu cầu:
- Độ dài: 1500-2000 từ
- Cấu trúc: Giới thiệu {zone_name} → Tổng quan các thành phần → So sánh / tiêu chí chọn → Bảng so sánh (dùng HTML table) → Lịch bảo dưỡng → FAQ
- Đề cập từng sản phẩm trong zone một cách tự nhiên
- SEO-friendly headings

Tags gợi ý: {suggested_tags}""",

    # ── Ngành: Xu hướng, tổng quan thị trường 1 segment ──
    'nganh': """Viết bài PHÂN TÍCH NGÀNH / XU HƯỚNG cho segment sau.

Vertical: {vertical_name}
Segment: {segment_name}
Mô tả: {segment_description}

Các zone trong segment:
{all_zones}

Số lượng sản phẩm: {total_parts}

Yêu cầu:
- Độ dài: 2000-3000 từ
- Cấu trúc: Tổng quan {segment_name} trong {vertical_name} → Xu hướng hiện tại → Các hệ thống/zone quan trọng → Chi phí bảo dưỡng tổng thể → Lời khuyên cho người dùng → Kết luận
- Góc nhìn chuyên gia, phân tích sâu
- Liên kết logic giữa các zone

Tags gợi ý: {suggested_tags}""",

    # ── Event: Bài theo sự kiện / mùa ──
    'event': """Viết bài THEO SỰ KIỆN / MÙA VỤ sau.

Vertical: {vertical_name}
Sự kiện: {event_name}
Loại: {event_type}
Keywords: {event_keywords}

Bối cảnh vertical:
{vertical_context}

Yêu cầu:
- Độ dài: 1000-1500 từ
- Gắn sự kiện với sản phẩm/dịch vụ của vertical
- Tạo cảm giác cấp bách / thời điểm phù hợp
- CTA rõ ràng

Tags gợi ý: {suggested_tags}""",

    # ── Custom: Bài theo topic tự do ──
    'custom': """Viết bài về chủ đề sau.

Vertical: {vertical_name}
Chủ đề: {topic}
Keywords: {keywords}
Tone: {tone}

Yêu cầu:
- Độ dài: {word_count} từ
- Viết theo tone đã chỉ định
- SEO-optimized cho keywords đã cho
- Cấu trúc rõ ràng với H2, H3

Tags gợi ý: {suggested_tags}"""
}


# ─── Context Builder ────────────────────────────────────────────

def build_context_for_part(part):
    """Build context dict for a chi-tiet article about a Part"""
    from models import Zone, Segment, Vertical, Part as PartModel
    zone = Zone.query.get(part.zone_id)
    segment = Segment.query.get(zone.segment_id)
    vertical = Vertical.query.get(segment.vertical_id)

    # Related parts in same zone
    related = PartModel.query.filter(
        PartModel.zone_id == zone.id,
        PartModel.id != part.id
    ).limit(10).all()
    related_text = '\n'.join([f"- {p.name_vi} ({p.name_en}): {p.description[:100]}" for p in related]) or '(Chưa có sản phẩm liên quan)'

    return {
        'vertical_name': vertical.name,
        'segment_name': segment.name,
        'zone_name': zone.name,
        'zone_description': zone.description,
        'part_name': part.name_vi,
        'part_name_en': part.name_en or '',
        'part_description': part.description or '',
        'oem_code': part.oem_code or 'N/A',
        'related_parts': related_text,
        'suggested_tags': part.tags or f"{part.name_vi},{zone.name},{segment.name}",
    }


def build_context_for_zone(zone):
    """Build context dict for a chung article about a Zone"""
    from models import Segment, Vertical, Part
    segment = Segment.query.get(zone.segment_id)
    vertical = Vertical.query.get(segment.vertical_id)

    parts = Part.query.filter_by(zone_id=zone.id).all()
    parts_text = '\n'.join([f"- {p.name_vi} ({p.name_en}): {p.description[:120]}" for p in parts]) or '(Chưa có sản phẩm)'

    return {
        'vertical_name': vertical.name,
        'segment_name': segment.name,
        'zone_name': zone.name,
        'zone_description': zone.description or '',
        'all_parts': parts_text,
        'suggested_tags': f"{zone.name},{segment.name},{vertical.name}",
    }


def build_context_for_segment(segment):
    """Build context dict for a nganh article about a Segment"""
    from models import Vertical, Zone, Part
    vertical = Vertical.query.get(segment.vertical_id)

    zones = Zone.query.filter_by(segment_id=segment.id).all()
    zones_text = '\n'.join([f"- {z.icon} {z.name}: {z.description[:100]}" for z in zones]) or '(Chưa có zone)'

    total_parts = 0
    for z in zones:
        total_parts += Part.query.filter_by(zone_id=z.id).count()

    return {
        'vertical_name': vertical.name,
        'segment_name': segment.name,
        'segment_description': segment.description or '',
        'all_zones': zones_text,
        'total_parts': total_parts,
        'suggested_tags': f"{segment.name},{vertical.name},xu hướng,thị trường",
    }


def build_context_for_event(event, vertical):
    """Build context dict for an event-based article"""
    from models import Segment
    segments = Segment.query.filter_by(vertical_id=vertical.id).all()
    ctx = '\n'.join([f"- {s.name}: {s.description[:80]}" for s in segments]) or '(Chưa có segment)'

    return {
        'vertical_name': vertical.name,
        'event_name': event.name,
        'event_type': event.event_type,
        'event_keywords': event.keywords or '',
        'vertical_context': ctx,
        'suggested_tags': f"{event.name},{vertical.name},{event.keywords}",
    }


def build_context_custom(vertical_name, topic, keywords='', tone='seo', word_count='1200'):
    """Build context dict for a custom topic article"""
    return {
        'vertical_name': vertical_name,
        'topic': topic,
        'keywords': keywords,
        'tone': tone,
        'word_count': word_count,
        'suggested_tags': keywords or topic,
    }


# ─── Generation ─────────────────────────────────────────────────

def generate_article(tier, context, provider=None, model=None):
    """
    Generate article content using LLM.

    Args:
        tier: 'chi-tiet' | 'chung' | 'nganh' | 'event' | 'custom'
        context: dict from build_context_* functions
        provider: 'openai' (default)
        model: model name override

    Returns:
        dict: {title, content, excerpt, tags, tokens_used, cost_vnd}
    """
    provider = provider or DEFAULT_PROVIDER
    model = model or DEFAULT_MODEL

    # Build prompt from template
    template = TIER_PROMPTS.get(tier, TIER_PROMPTS['custom'])
    user_prompt = template.format(**context)

    if provider == 'openai':
        return _generate_openai(user_prompt, model)
    else:
        raise ValueError(f'Unsupported provider: {provider}')


def _generate_openai(user_prompt, model):
    """Call OpenAI API and parse response"""
    client = _get_openai_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=4000,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    tokens_used = response.usage.total_tokens if response.usage else 0

    # Cost estimate (GPT-4o-mini pricing approx)
    cost_per_1k = 0.15  # USD per 1K tokens (input) — rough estimate
    cost_usd = (tokens_used / 1000) * cost_per_1k
    cost_vnd = cost_usd * 25500  # ~25,500 VND/USD

    # Parse JSON response
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: try to extract from raw text
        data = {
            'title': 'Untitled',
            'content': raw,
            'excerpt': raw[:200],
            'tags': '',
        }

    # Calculate reading time (~200 words/min for Vietnamese)
    word_count = len(re.sub(r'<[^>]+>', '', data.get('content', '')).split())
    reading_time = max(1, round(word_count / 200))

    return {
        'title': data.get('title', 'Untitled'),
        'content': data.get('content', ''),
        'excerpt': data.get('excerpt', ''),
        'tags': data.get('tags', ''),
        'tokens_used': tokens_used,
        'cost_vnd': round(cost_vnd),
        'word_count': word_count,
        'reading_time': reading_time,
    }


# ─── Gap Scanner ────────────────────────────────────────────────

def scan_vertical_gaps(vertical):
    """
    Scan a vertical for content gaps. Returns prioritized list of missing content.

    Returns:
        dict: {
            'vertical': Vertical,
            'total_possible': int,
            'existing_articles': int,
            'coverage_pct': float,
            'tier_breakdown': {tier: {total, existing, missing, items:[]}},
            'priority_score': float (0-100, higher = needs more content),
            'top_gaps': [{tier, target_type, target_id, target_name, priority}]
        }
    """
    from models import Segment, Zone, Part, Article

    segments = Segment.query.filter_by(vertical_id=vertical.id).all()

    tier_data = {
        'nganh': {'total': 0, 'existing': 0, 'missing': 0, 'items': []},
        'chung': {'total': 0, 'existing': 0, 'missing': 0, 'items': []},
        'chi-tiet': {'total': 0, 'existing': 0, 'missing': 0, 'items': []},
    }

    # Existing articles indexed by related slugs
    existing_articles = Article.query.filter_by(
        vertical_slug=vertical.slug, status='published'
    ).all()
    article_segments = set()
    article_zones = set()
    article_categories = set()
    for a in existing_articles:
        if a.related_segment_slug:
            article_segments.add(a.related_segment_slug)
        if a.related_zone_slug:
            article_zones.add(a.related_zone_slug)
        if a.category:
            article_categories.add(a.category)
        if a.tier == 'nganh':
            article_segments.add(a.related_segment_slug or '')
        elif a.tier == 'chung':
            article_zones.add(a.related_zone_slug or '')

    top_gaps = []

    for seg in segments:
        # Nganh tier: 1 article per segment
        tier_data['nganh']['total'] += 1
        if seg.slug in article_segments:
            tier_data['nganh']['existing'] += 1
        else:
            tier_data['nganh']['missing'] += 1
            tier_data['nganh']['items'].append({
                'name': seg.name, 'slug': seg.slug, 'type': 'segment', 'id': seg.id
            })
            top_gaps.append({
                'tier': 'nganh', 'target_type': 'segment',
                'target_id': seg.id, 'target_name': f"{vertical.name} > {seg.name}",
                'priority': 90,  # High priority — top-level content
            })

        zones = Zone.query.filter_by(segment_id=seg.id).all()
        for z in zones:
            # Chung tier: 1 article per zone
            tier_data['chung']['total'] += 1
            if z.slug in article_zones or z.slug in article_categories:
                tier_data['chung']['existing'] += 1
            else:
                tier_data['chung']['missing'] += 1
                tier_data['chung']['items'].append({
                    'name': z.name, 'slug': z.slug, 'type': 'zone', 'id': z.id,
                    'segment': seg.name,
                })
                top_gaps.append({
                    'tier': 'chung', 'target_type': 'zone',
                    'target_id': z.id, 'target_name': f"{seg.name} > {z.name}",
                    'priority': 70,
                })

            # Chi-tiet tier: 1 article per part (optional, lower priority)
            parts = Part.query.filter_by(zone_id=z.id).all()
            for p in parts:
                tier_data['chi-tiet']['total'] += 1
                # Check if part has a detailed article
                has_article = Article.query.filter(
                    Article.vertical_slug == vertical.slug,
                    Article.tier == 'chi-tiet',
                    Article.slug.contains(p.slug)
                ).first()
                if has_article:
                    tier_data['chi-tiet']['existing'] += 1
                else:
                    tier_data['chi-tiet']['missing'] += 1
                    tier_data['chi-tiet']['items'].append({
                        'name': p.name_vi, 'slug': p.slug, 'type': 'part', 'id': p.id,
                        'zone': z.name, 'segment': seg.name,
                    })
                    top_gaps.append({
                        'tier': 'chi-tiet', 'target_type': 'part',
                        'target_id': p.id, 'target_name': f"{z.name} > {p.name_vi}",
                        'priority': 50,
                    })

    total_possible = sum(t['total'] for t in tier_data.values())
    total_existing = sum(t['existing'] for t in tier_data.values())
    coverage_pct = round(total_existing / total_possible * 100, 1) if total_possible > 0 else 0

    # Priority score: higher = needs more content
    priority_score = round(100 - coverage_pct, 1)

    # Sort gaps by priority desc
    top_gaps.sort(key=lambda x: x['priority'], reverse=True)

    return {
        'vertical': vertical,
        'total_possible': total_possible,
        'existing_articles': len(existing_articles),
        'coverage_pct': coverage_pct,
        'tier_breakdown': tier_data,
        'priority_score': priority_score,
        'top_gaps': top_gaps[:20],  # Top 20 gaps
    }


def scan_all_gaps():
    """Scan all published verticals and return sorted by priority"""
    from models import Vertical
    verticals = Vertical.query.filter_by(status='published').all()
    results = []
    for v in verticals:
        results.append(scan_vertical_gaps(v))
    # Sort: highest priority (most gaps) first
    results.sort(key=lambda x: x['priority_score'], reverse=True)
    return results


# ─── Auto-Fill Pipeline ────────────────────────────────────────

def auto_fill_queue(vertical_id=None, max_items=10):
    """
    Scan gaps and auto-populate ContentQueue with missing articles.
    Respects AutoContentRule settings per vertical.

    Returns:
        list of created ContentQueue items
    """
    from models import db, Vertical, Segment, Zone, Part, ContentQueue, AutoContentRule
    from datetime import datetime, timedelta

    if vertical_id:
        verticals = [Vertical.query.get(vertical_id)]
    else:
        verticals = Vertical.query.filter_by(status='published').all()

    created = []
    for v in verticals:
        if not v:
            continue

        # Check if auto-rule exists and is active
        rule = AutoContentRule.query.filter_by(vertical_id=v.id, is_active=True).first()
        tone = rule.tone if rule else 'seo'
        topics_to_avoid = (rule.topics_to_avoid or '').lower().split(',') if rule else []

        gaps = scan_vertical_gaps(v)

        items_added = 0
        for gap in gaps['top_gaps']:
            if items_added >= max_items:
                break

            # Check if already in queue
            existing = ContentQueue.query.filter_by(
                vertical_id=v.id,
                topic=gap['target_name'],
            ).first()
            if existing:
                continue

            # Check topics to avoid
            skip = False
            for avoid in topics_to_avoid:
                if avoid.strip() and avoid.strip() in gap['target_name'].lower():
                    skip = True
                    break
            if skip:
                continue

            # Map tier to knowledge layer
            layer_map = {'nganh': 'L1', 'chung': 'L2', 'chi-tiet': 'L3'}

            # Build descriptive topic
            if gap['tier'] == 'chi-tiet':
                topic = f"Review chi tiết: {gap['target_name']}"
            elif gap['tier'] == 'chung':
                topic = f"Hướng dẫn tổng hợp: {gap['target_name']}"
            else:
                topic = f"Phân tích xu hướng: {gap['target_name']}"

            item = ContentQueue(
                vertical_id=v.id,
                topic=topic,
                keywords=f"{gap['target_name']},{v.name}",
                knowledge_layer=layer_map.get(gap['tier'], 'L2'),
                source_type='ai',
                status='pending',
                scheduled_at=datetime.utcnow() + timedelta(hours=items_added),
            )
            db.session.add(item)
            created.append(item)
            items_added += 1

    db.session.commit()
    return created


def generate_from_queue_item(queue_item):
    """
    Generate article content from a ContentQueue item.
    Detects the appropriate tier and context from the topic.

    Returns:
        dict: generated article data
    """
    from models import db, Vertical, Segment, Zone, Part

    vertical = Vertical.query.get(queue_item.vertical_id)
    if not vertical:
        raise ValueError(f'Vertical not found: {queue_item.vertical_id}')

    # Detect tier from knowledge_layer
    layer_to_tier = {'L1': 'nganh', 'L2': 'chung', 'L3': 'chi-tiet', 'L4': 'chi-tiet'}
    tier = layer_to_tier.get(queue_item.knowledge_layer, 'custom')

    # Try to find matching entity for rich context
    context = None

    if tier == 'custom' or not context:
        # Fallback: use custom context
        context = build_context_custom(
            vertical_name=vertical.name,
            topic=queue_item.topic,
            keywords=queue_item.keywords or '',
            tone='seo',
            word_count='1500',
        )
        tier = 'custom'

    # Update queue status
    queue_item.status = 'generating'
    db.session.commit()

    try:
        result = generate_article(tier, context)

        # Update queue item
        queue_item.generated_content = json.dumps(result, ensure_ascii=False)
        queue_item.word_count = result.get('word_count', 0)
        queue_item.status = 'review'
        db.session.commit()

        return result
    except Exception as e:
        queue_item.status = 'pending'  # Reset on failure
        db.session.commit()
        raise


def publish_queue_item(queue_item):
    """
    Convert a generated ContentQueue item into a published Article.

    Returns:
        Article instance
    """
    from models import db, Article, Vertical
    import re

    if not queue_item.generated_content:
        raise ValueError('No generated content to publish')

    data = json.loads(queue_item.generated_content)
    vertical = Vertical.query.get(queue_item.vertical_id)

    # Generate slug from title
    title = data.get('title', queue_item.topic)

    # Simple slug generation
    slug = _make_slug(title)

    # Ensure unique slug
    base_slug = slug
    counter = 1
    while Article.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Map knowledge layer to tier
    layer_to_tier = {'L1': 'nganh', 'L2': 'chung', 'L3': 'chi-tiet', 'L4': 'chi-tiet'}

    article = Article(
        vertical_slug=vertical.slug if vertical else '',
        title=title,
        slug=slug,
        excerpt=data.get('excerpt', ''),
        content=data.get('content', ''),
        tier=layer_to_tier.get(queue_item.knowledge_layer, 'chung'),
        tags=data.get('tags', ''),
        ai_generated=True,
        status='published',
        reading_time=data.get('reading_time', 5),
    )
    db.session.add(article)

    queue_item.status = 'published'
    queue_item.published_at = datetime.utcnow()
    db.session.commit()

    return article


def _make_slug(text):
    """Convert Vietnamese text to URL-friendly slug"""
    import unicodedata
    vietnamese_map = {
        'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
        'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
        'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
        'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
        'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
        'đ': 'd', 'Đ': 'd',
    }
    result = text.lower()
    for vi_char, ascii_char in vietnamese_map.items():
        result = result.replace(vi_char, ascii_char)
    result = unicodedata.normalize('NFKD', result).encode('ascii', 'ignore').decode('ascii')
    result = re.sub(r'[^a-z0-9\s-]', '', result)
    result = re.sub(r'[\s-]+', '-', result).strip('-')
    return result
