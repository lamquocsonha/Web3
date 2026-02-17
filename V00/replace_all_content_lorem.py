"""
Replace ALL content fields in seed_data.py and database with Lorem Ipsum.
Handles both Article.content and Part.content.
Uses proper quoting to avoid SyntaxError.
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Single-line Lorem Ipsum (no newlines - safe for any Python string quoting)
LOREM_SHORT = '<h2>Lorem Ipsum</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>'

# Multi-line Lorem Ipsum for database (Articles get more content)
LOREM_LARGE = """<h2>Lorem Ipsum</h2>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
<p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.</p>

<h2>Neque Porro Quisquam</h2>
<p>Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur.</p>
<p>Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur? At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident.</p>

<h2>Similique Sunt in Culpa</h2>
<p>Similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus.</p>
<p>Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat.</p>

<h2>Donec Vel Sapien</h2>
<p>Donec vel sapien augue. Praesent malesuada, lacus at vehicula congue, ligula ante tincidunt risus, at volutpat ipsum magna nec mi. Fusce euismod massa vel augue cursus, at gravida nunc porttitor. Vivamus vel justo et nulla volutpat lacinia. Proin hendrerit fringilla augue nec accumsan. Suspendisse potenti.</p>
<p>Cras ultricies ligula sed magna dictum porta. Curabitur aliquet quam id dui posuere blandit. Nulla quis lorem ut libero malesuada feugiat. Praesent sapien massa, convallis a pellentesque nec, egestas non nisi. Mauris blandit aliquet elit, eget tincidunt nibh pulvinar a. Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui.</p>

<h2>Vivamus Magna Justo</h2>
<p>Vivamus magna justo, lacinia eget consectetur sed, convallis at tellus. Curabitur arcu erat, accumsan id imperdiet et, porttitor at sem. Nulla porttitor accumsan tincidunt. Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui. Proin eget tortor risus. Vivamus suscipit tortor eget felis porttitor volutpat.</p>
<p>Mauris blandit aliquet elit, eget tincidunt nibh pulvinar a. Curabitur non nulla sit amet nisl tempus convallis quis ac lectus. Sed porttitor lectus nibh. Nulla porttitor accumsan tincidunt. Donec rutrum congue leo eget malesuada. Praesent sapien massa, convallis a pellentesque nec, egestas non nisi.</p>"""


def replace_in_seed_data():
    """Replace all 'content' field values in seed_data.py with Lorem Ipsum.
    Uses single-line Lorem to avoid quoting issues."""
    seed_file = os.path.join(os.path.dirname(__file__), 'seed_data.py')

    with open(seed_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Strategy: find each 'content': and replace the value that follows
    # Handle both triple-quoted and single-quoted strings
    result = []
    i = 0
    count = 0

    while i < len(text):
        # Look for 'content' followed by : and optional whitespace
        match = re.match(r"'content'\s*:\s*", text[i:])
        if match:
            result.append(match.group(0))
            i += match.end()

            # Determine quote style
            if text[i:i+3] == "'''":
                # Triple single-quote — find closing '''
                end = text.find("'''", i + 3)
                if end == -1:
                    # Broken, just skip
                    result.append(text[i])
                    i += 1
                    continue
                end += 3  # include closing '''
                # Replace with triple-quoted Lorem
                result.append(f"'''{LOREM_SHORT}'''")
                i = end
                count += 1
            elif text[i] == "'":
                # Single quote — find closing ' (handle escaped \')
                j = i + 1
                while j < len(text):
                    if text[j] == '\\':
                        j += 2  # skip escaped char
                    elif text[j] == "'":
                        break
                    else:
                        j += 1
                j += 1  # include closing '
                result.append(f"'{LOREM_SHORT}'")
                i = j
                count += 1
            elif text[i:i+3] == '"""':
                # Triple double-quote
                end = text.find('"""', i + 3)
                if end == -1:
                    result.append(text[i])
                    i += 1
                    continue
                end += 3
                result.append(f'"""{LOREM_SHORT}"""')
                i = end
                count += 1
            elif text[i] == '"':
                # Double quote
                j = i + 1
                while j < len(text):
                    if text[j] == '\\':
                        j += 2
                    elif text[j] == '"':
                        break
                    else:
                        j += 1
                j += 1
                result.append(f'"{LOREM_SHORT}"')
                i = j
                count += 1
            else:
                result.append(text[i])
                i += 1
        else:
            result.append(text[i])
            i += 1

    output = ''.join(result)

    with open(seed_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f'[SEED] Replaced {count} content fields in seed_data.py')
    return count


def replace_in_database():
    """Replace all Article and Part content in database with Lorem Ipsum."""
    from app import app
    from models import db, Article, Part

    with app.app_context():
        articles = Article.query.all()
        for a in articles:
            a.content = LOREM_LARGE
            a.reading_time = 5
        print(f'[DB] Replaced {len(articles)} Article contents')

        parts = Part.query.all()
        part_count = 0
        for p in parts:
            if p.content:
                p.content = LOREM_SHORT
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
