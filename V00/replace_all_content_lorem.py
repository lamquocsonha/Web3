"""
Replace ALL content fields in seed_data.py and database with Lorem Ipsum.
Handles both Article.content and Part.content.
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# ── Lorem Ipsum paragraphs pool ──
LOREM_PARAGRAPHS = [
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
    'Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit.',
    'Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam.',
    'Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur? At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti.',
    'Similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus.',
    'Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur.',
    'Donec vel sapien augue. Praesent malesuada, lacus at vehicula congue, ligula ante tincidunt risus, at volutpat ipsum magna nec mi. Fusce euismod massa vel augue cursus, at gravida nunc porttitor. Vivamus vel justo et nulla volutpat lacinia.',
    'Cras ultricies ligula sed magna dictum porta. Curabitur aliquet quam id dui posuere blandit. Nulla quis lorem ut libero malesuada feugiat. Praesent sapien massa, convallis a pellentesque nec, egestas non nisi. Mauris blandit aliquet elit, eget tincidunt nibh pulvinar a.',
    'Vivamus magna justo, lacinia eget consectetur sed, convallis at tellus. Curabitur arcu erat, accumsan id imperdiet et, porttitor at sem. Nulla porttitor accumsan tincidunt. Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui.',
    'Praesent commodo cursus magna, vel scelerisque nisl consectetur et. Vivamus sagittis lacus vel augue laoreet rutrum faucibus dolor auctor. Maecenas sed diam eget risus varius blandit sit amet non magna.',
    'Aenean lacinia bibendum nulla sed consectetur. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Maecenas faucibus mollis interdum. Etiam porta sem malesuada magna mollis euismod.',
    'Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh, ut fermentum massa justo sit amet risus. Donec id elit non mi porta gravida at eget metus. Aenean eu leo quam. Pellentesque ornare sem lacinia quam venenatis vestibulum.',
]

LOREM_HEADINGS = [
    'Lorem Ipsum', 'Neque Porro Quisquam', 'Similique Sunt in Culpa',
    'Donec Vel Sapien', 'Vivamus Magna Justo', 'Etiam Sit Amet',
    'Maecenas Efficitur', 'Praesent Commodo', 'Aenean Lacinia', 'Conclusion',
]


def generate_lorem_html(size='medium'):
    """Generate Lorem Ipsum HTML content.
    size: 'small' (~150 words), 'medium' (~400 words), 'large' (~1000 words)
    """
    if size == 'small':
        sections = 1
        paras_per = 2
    elif size == 'large':
        sections = 5
        paras_per = 2
    else:  # medium
        sections = 3
        paras_per = 2

    html = ''
    for i in range(sections):
        heading = LOREM_HEADINGS[i % len(LOREM_HEADINGS)]
        html += f'<h2>{heading}</h2>\n'
        for j in range(paras_per):
            idx = (i * paras_per + j) % len(LOREM_PARAGRAPHS)
            html += f'<p>{LOREM_PARAGRAPHS[idx]}</p>\n'
    return html.strip()


def replace_in_seed_data():
    """Replace all 'content' field values in seed_data.py with Lorem Ipsum."""
    seed_file = os.path.join(os.path.dirname(__file__), 'seed_data.py')

    with open(seed_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern 1: 'content': '''...''' (triple-quoted, multiline)
    pattern_triple = r"('content'\s*:\s*)('''[\s\S]*?''')"
    # Pattern 2: 'content':'...' (single-quoted, single line)
    pattern_single = r"('content'\s*:\s*)('[^']*(?:\\'[^']*)*')"

    small_lorem = generate_lorem_html('small').replace("'", "\\'")
    medium_lorem = generate_lorem_html('medium').replace("'", "\\'")

    count = 0

    def replace_triple(match):
        nonlocal count
        count += 1
        prefix = match.group(1)
        return f"{prefix}'''{medium_lorem}'''"

    def replace_single(match):
        nonlocal count
        count += 1
        prefix = match.group(1)
        return f"{prefix}'{small_lorem}'"

    # Replace triple-quoted first (more specific)
    content = re.sub(pattern_triple, replace_triple, content)
    # Then single-quoted
    content = re.sub(pattern_single, replace_single, content)

    with open(seed_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'[SEED] Replaced {count} content fields in seed_data.py')
    return count


def replace_in_database():
    """Replace all Article and Part content in database with Lorem Ipsum."""
    from app import app
    from models import db, Article, Part

    large_lorem = generate_lorem_html('large')
    medium_lorem = generate_lorem_html('medium')

    with app.app_context():
        # Replace Article content
        articles = Article.query.all()
        for a in articles:
            a.content = large_lorem
            a.reading_time = 5
        print(f'[DB] Replaced {len(articles)} Article contents')

        # Replace Part content
        parts = Part.query.all()
        part_count = 0
        for p in parts:
            if p.content:
                p.content = medium_lorem
                part_count += 1
        print(f'[DB] Replaced {part_count} Part contents (of {len(parts)} total)')

        db.session.commit()
        print('[DB] Committed successfully')


if __name__ == '__main__':
    print('=== Replacing ALL content with Lorem Ipsum ===\n')

    print('--- Step 1: seed_data.py ---')
    replace_in_seed_data()

    print('\n--- Step 2: Database ---')
    replace_in_database()

    print('\n=== Done! All content is now Lorem Ipsum ===')
