"""
Replace all article content with classic Lorem Ipsum placeholder text.
Each article gets ~1000 words of structured Lorem Ipsum with <h2>/<p> tags
so the carousel split looks natural.
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from models import db, Article

# Classic Lorem Ipsum sections — each has a heading + 2-3 paragraphs
LOREM_SECTIONS = [
    {
        'heading': 'Lorem Ipsum',
        'paragraphs': [
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
            'Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.',
        ]
    },
    {
        'heading': 'Neque Porro Quisquam',
        'paragraphs': [
            'Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur.',
            'Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur? At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident.',
        ]
    },
    {
        'heading': 'Similique Sunt in Culpa',
        'paragraphs': [
            'Similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus.',
            'Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat.',
        ]
    },
    {
        'heading': 'Donec Vel Sapien',
        'paragraphs': [
            'Donec vel sapien augue. Praesent malesuada, lacus at vehicula congue, ligula ante tincidunt risus, at volutpat ipsum magna nec mi. Fusce euismod massa vel augue cursus, at gravida nunc porttitor. Vivamus vel justo et nulla volutpat lacinia. Proin hendrerit fringilla augue nec accumsan. Suspendisse potenti. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae.',
            'Cras ultricies ligula sed magna dictum porta. Curabitur aliquet quam id dui posuere blandit. Nulla quis lorem ut libero malesuada feugiat. Praesent sapien massa, convallis a pellentesque nec, egestas non nisi. Mauris blandit aliquet elit, eget tincidunt nibh pulvinar a. Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui.',
            'Pellentesque in ipsum id orci porta dapibus. Curabitur non nulla sit amet nisl tempus convallis quis ac lectus. Donec sollicitudin molestie malesuada. Quisque velit nisi, pretium ut lacinia in, elementum id enim.',
        ]
    },
    {
        'heading': 'Vivamus Magna Justo',
        'paragraphs': [
            'Vivamus magna justo, lacinia eget consectetur sed, convallis at tellus. Curabitur arcu erat, accumsan id imperdiet et, porttitor at sem. Nulla porttitor accumsan tincidunt. Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui. Proin eget tortor risus. Vivamus suscipit tortor eget felis porttitor volutpat.',
            'Mauris blandit aliquet elit, eget tincidunt nibh pulvinar a. Curabitur non nulla sit amet nisl tempus convallis quis ac lectus. Sed porttitor lectus nibh. Nulla porttitor accumsan tincidunt. Donec rutrum congue leo eget malesuada. Praesent sapien massa, convallis a pellentesque nec, egestas non nisi.',
        ]
    },
    {
        'heading': 'Etiam Sit Amet',
        'paragraphs': [
            'Etiam sit amet nisl purus in mollis nunc sed id semper. Faucibus et molestie ac feugiat sed lectus vestibulum mattis. Eget gravida cum sociis natoque penatibus et magnis dis parturient montes nascetur ridiculus mus. Amet nisl suscipit adipiscing bibendum est ultricies integer quis auctor elit sed vulputate mi sit amet mauris commodo.',
            'Turpis massa tincidunt dui ut ornare lectus sit amet est placerat in egestas erat imperdiet sed euismod nisi porta lorem mollis aliquam ut porttitor leo a diam sollicitudin tempor id eu nisl nunc mi ipsum faucibus vitae aliquet nec ullamcorper sit amet risus nullam eget felis eget nunc lobortis mattis aliquam faucibus purus in massa tempor nec.',
        ]
    },
    {
        'heading': 'Maecenas Efficitur',
        'paragraphs': [
            'Maecenas efficitur luctus arcu vitae auctor. Nam condimentum, tortor sed pellentesque aliquet, diam ante blandit purus, id volutpat ante ante vitae dolor. Integer fringilla orci sit amet libero euismod semper. Aenean lacinia bibendum nulla sed consectetur. Cras mattis consectetur purus sit amet fermentum. Nullam id dolor id nibh ultricies vehicula ut id elit.',
            'Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh, ut fermentum massa justo sit amet risus. Donec id elit non mi porta gravida at eget metus. Aenean eu leo quam. Pellentesque ornare sem lacinia quam venenatis vestibulum. Morbi leo risus, porta ac consectetur ac, vestibulum at eros.',
        ]
    },
    {
        'heading': 'Praesent Commodo',
        'paragraphs': [
            'Praesent commodo cursus magna, vel scelerisque nisl consectetur et. Vivamus sagittis lacus vel augue laoreet rutrum faucibus dolor auctor. Maecenas sed diam eget risus varius blandit sit amet non magna. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec ullamcorper nulla non metus auctor fringilla.',
            'Duis mollis, est non commodo luctus, nisi erat porttitor ligula, eget lacinia odio sem nec elit. Cras justo odio, dapibus ut facilisis in, egestas eget quam. Nullam quis risus eget urna mollis ornare vel eu leo. Integer posuere erat a ante venenatis dapibus posuere velit aliquet.',
        ]
    },
    {
        'heading': 'Aenean Lacinia',
        'paragraphs': [
            'Aenean lacinia bibendum nulla sed consectetur. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Maecenas faucibus mollis interdum. Etiam porta sem malesuada magna mollis euismod. Donec sed odio dui. Vestibulum id ligula porta felis euismod semper.',
            'Nulla vitae elit libero, a pharetra augue. Cras mattis consectetur purus sit amet fermentum. Sed posuere consectetur est at lobortis. Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh, ut fermentum massa justo sit amet risus. Maecenas sed diam eget risus varius blandit sit amet non magna.',
        ]
    },
    {
        'heading': 'Conclusion',
        'paragraphs': [
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Lectus proin nibh nisl condimentum id venenatis a condimentum vitae. Tincidunt augue interdum velit euismod in pellentesque massa placerat duis. Nibh cras pulvinar mattis nunc sed blandit libero volutpat sed.',
            'Pharetra et ultrices neque ornare aenean euismod elementum nisi quis eleifend quam adipiscing vitae proin sagittis nisl rhoncus mattis rhoncus urna neque viverra justo nec ultrices dui sapien eget mi proin sed libero enim sed faucibus turpis in eu mi bibendum neque egestas congue quisque egestas diam in arcu cursus euismod.',
        ]
    },
]


def count_words(html_text):
    """Count words in HTML text (strip tags first)."""
    clean = re.sub(r'<[^>]+>', ' ', html_text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return len(clean.split())


def build_section(section):
    """Build HTML section with heading and paragraphs."""
    html = f'\n\n<h2>{section["heading"]}</h2>'
    for p in section['paragraphs']:
        html += f'\n<p>{p}</p>'
    return html


def generate_lorem_content(target_words=1000):
    """Generate pure Lorem Ipsum HTML content to reach target word count."""
    content = ''
    idx = 0

    while count_words(content) < target_words and idx < len(LOREM_SECTIONS):
        content += build_section(LOREM_SECTIONS[idx])
        idx += 1

    # Cycle through if still not enough
    while count_words(content) < target_words:
        content += build_section(LOREM_SECTIONS[idx % len(LOREM_SECTIONS)])
        idx += 1

    return content.strip()


def main():
    with app.app_context():
        articles = Article.query.all()
        print(f'Found {len(articles)} articles total\n')

        updated = 0
        for article in articles:
            # Generate fresh Lorem Ipsum content for every article
            lorem_content = generate_lorem_content(target_words=1000)
            word_count = count_words(lorem_content)

            article.content = lorem_content
            article.reading_time = max(5, word_count // 200)

            updated += 1
            print(f'  [LOREM] "{article.title[:50]}..." → {word_count} words')

        db.session.commit()
        print(f'\nDone! Replaced {updated}/{len(articles)} articles with Lorem Ipsum.')


if __name__ == '__main__':
    main()
