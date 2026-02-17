"""
Pad all articles to ~1000 words with structured Vietnamese lorem ipsum.
Content is organized with <h2> headings and <p> paragraphs so that
the carousel split (at midpoint of </p> tags) looks natural.
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from models import db, Article

# Structured lorem ipsum SECTIONS — each has a heading + 2-3 paragraphs (~150-200 words per section)
LOREM_SECTIONS = [
    {
        'heading': 'Tổng quan thị trường',
        'paragraphs': [
            'Trong bối cảnh thị trường ngày càng phát triển, người tiêu dùng Việt Nam đang có nhiều lựa chọn hơn bao giờ hết. Việc tìm hiểu kỹ thông tin trước khi quyết định mua sắm không chỉ giúp tiết kiệm chi phí mà còn đảm bảo chất lượng sản phẩm phù hợp với nhu cầu thực tế. Các chuyên gia khuyến cáo rằng việc so sánh giá cả từ nhiều nguồn khác nhau, đọc đánh giá từ người dùng thực tế, và tham khảo ý kiến từ cộng đồng là những bước quan trọng không nên bỏ qua.',
            'Công nghệ sản xuất hiện đại đã mang đến những cải tiến đáng kể về chất lượng và độ bền của sản phẩm. Các nhà sản xuất liên tục đầu tư vào nghiên cứu và phát triển để cho ra đời những sản phẩm đáp ứng tiêu chuẩn quốc tế. Điều này đồng nghĩa với việc người tiêu dùng có thể tiếp cận được những sản phẩm chất lượng cao với mức giá hợp lý hơn so với trước đây, đặc biệt khi mua hàng qua các kênh thương mại điện tử uy tín.',
        ]
    },
    {
        'heading': 'Hướng dẫn lựa chọn sản phẩm',
        'paragraphs': [
            'Một trong những yếu tố quan trọng nhất khi lựa chọn sản phẩm là hiểu rõ thông số kỹ thuật và cách sử dụng đúng cách. Việc sử dụng sai cách hoặc không tuân thủ hướng dẫn của nhà sản xuất có thể dẫn đến hư hỏng sớm, giảm hiệu suất hoạt động, và thậm chí gây nguy hiểm cho người sử dụng. Do đó, hãy luôn đọc kỹ hướng dẫn sử dụng và tham khảo ý kiến chuyên gia khi cần thiết.',
            'So sánh sản phẩm là bước không thể thiếu trong quá trình mua sắm thông minh. Khi so sánh, hãy chú ý đến những tiêu chí quan trọng như chất lượng vật liệu, thông số kỹ thuật, xuất xứ sản xuất, chính sách bảo hành, và đánh giá từ người dùng thực tế. Đừng chỉ dựa vào giá cả làm tiêu chí duy nhất, vì sản phẩm rẻ nhất không phải lúc nào cũng là lựa chọn tiết kiệm nhất khi tính đến chi phí sở hữu tổng thể.',
        ]
    },
    {
        'heading': 'Bảo dưỡng và chăm sóc',
        'paragraphs': [
            'Bảo dưỡng định kỳ là chìa khóa để kéo dài tuổi thọ và duy trì hiệu suất hoạt động ổn định. Nhiều người thường bỏ qua việc bảo dưỡng cho đến khi sản phẩm gặp sự cố, dẫn đến chi phí sửa chữa cao hơn nhiều so với chi phí bảo dưỡng định kỳ. Các chuyên gia khuyến nghị nên lập lịch bảo dưỡng cụ thể và tuân thủ nghiêm ngặt để tránh những hỏng hóc không đáng có.',
            'Bảo quản đúng cách là yếu tố quyết định tuổi thọ của nhiều loại sản phẩm. Điều kiện nhiệt độ, độ ẩm, ánh sáng, và môi trường xung quanh đều có thể ảnh hưởng đến chất lượng sản phẩm theo thời gian. Hãy tuân thủ hướng dẫn bảo quản của nhà sản xuất, tránh để sản phẩm tiếp xúc với các yếu tố gây hại, và kiểm tra định kỳ tình trạng sản phẩm để phát hiện sớm các dấu hiệu xuống cấp.',
        ]
    },
    {
        'heading': 'Kinh nghiệm mua sắm online',
        'paragraphs': [
            'Xu hướng mua sắm trực tuyến đang ngày càng phổ biến tại Việt Nam, với sự phát triển mạnh mẽ của các sàn thương mại điện tử như Shopee, Lazada, và Tiki. Người tiêu dùng có thể dễ dàng so sánh giá, đọc đánh giá, và đặt hàng chỉ với vài thao tác trên điện thoại. Tuy nhiên, cần lưu ý chọn mua từ các shop uy tín, kiểm tra kỹ thông tin sản phẩm và chính sách đổi trả để tránh mua phải hàng kém chất lượng.',
            'Thương mại điện tử đã thay đổi hoàn toàn cách người tiêu dùng mua sắm và tiếp cận sản phẩm. Từ việc phải đến cửa hàng trực tiếp, giờ đây bạn có thể duyệt hàng ngàn sản phẩm, đọc hàng trăm đánh giá, và đặt hàng giao tận nhà chỉ trong vài phút. Các chương trình khuyến mãi như flash sale, mã giảm giá, và freeship cũng giúp người tiêu dùng tiết kiệm đáng kể.',
        ]
    },
    {
        'heading': 'Chi phí và giá trị dài hạn',
        'paragraphs': [
            'Chi phí sở hữu tổng thể (Total Cost of Ownership) là một khái niệm quan trọng mà nhiều người thường bỏ qua. Giá mua ban đầu chỉ là một phần trong tổng chi phí — bạn còn cần tính đến chi phí lắp đặt, vận hành, bảo dưỡng, và thay thế linh kiện trong suốt vòng đời sản phẩm. Một sản phẩm có giá mua cao hơn nhưng bền bỉ và ít chi phí bảo dưỡng có thể tiết kiệm hơn lâu dài.',
            'Kinh nghiệm thực tế cho thấy rằng việc đầu tư vào sản phẩm chất lượng từ đầu luôn là quyết định khôn ngoan. Sản phẩm tốt không chỉ mang lại hiệu suất vượt trội mà còn ít gặp sự cố, giảm thời gian ngừng hoạt động, và tạo sự yên tâm cho người sử dụng. Hãy coi việc mua sắm như một khoản đầu tư chứ không chỉ là chi phí.',
        ]
    },
    {
        'heading': 'Dịch vụ và bảo hành',
        'paragraphs': [
            'Chất lượng dịch vụ sau bán hàng là một tiêu chí quan trọng không kém chất lượng sản phẩm. Một nhà cung cấp tốt sẽ luôn sẵn sàng hỗ trợ khách hàng từ tư vấn trước mua, hướng dẫn sử dụng, đến bảo hành và sửa chữa. Khi chọn mua sản phẩm, hãy ưu tiên những thương hiệu và đại lý có chính sách bảo hành rõ ràng, đội ngũ hỗ trợ kỹ thuật chuyên nghiệp.',
            'Việc lắp đặt và cài đặt đúng cách ảnh hưởng trực tiếp đến hiệu suất và tuổi thọ của sản phẩm. Nhiều sản phẩm yêu cầu quy trình lắp đặt chuyên nghiệp để đảm bảo hoạt động tối ưu và duy trì bảo hành. Nếu bạn không có kinh nghiệm hoặc dụng cụ phù hợp, hãy tìm đến các dịch vụ lắp đặt chuyên nghiệp thay vì tự làm.',
        ]
    },
    {
        'heading': 'An toàn và tiêu chuẩn chất lượng',
        'paragraphs': [
            'An toàn luôn là ưu tiên hàng đầu trong mọi lĩnh vực. Việc sử dụng sản phẩm chất lượng, đúng tiêu chuẩn không chỉ bảo vệ bản thân mà còn bảo vệ những người xung quanh. Các cơ quan quản lý ngày càng siết chặt tiêu chuẩn chất lượng, buộc nhà sản xuất phải tuân thủ nghiêm ngặt các quy định về an toàn. Người tiêu dùng nên tìm hiểu các chứng nhận chất lượng như ISO, TCVN.',
            'Kiến thức chuyên môn đóng vai trò then chốt trong việc đưa ra quyết định đúng đắn. Khi bạn hiểu rõ về sản phẩm, bạn có thể tự tin hơn trong việc lựa chọn, sử dụng và bảo dưỡng. Điều này không chỉ giúp tiết kiệm thời gian và tiền bạc mà còn giúp bạn tránh được những rủi ro không đáng có.',
        ]
    },
    {
        'heading': 'Xu hướng và đổi mới',
        'paragraphs': [
            'Đổi mới sáng tạo là động lực chính thúc đẩy sự phát triển của ngành công nghiệp. Các công nghệ mới như trí tuệ nhân tạo, Internet vạn vật (IoT), và vật liệu tiên tiến đang được ứng dụng ngày càng rộng rãi, mang đến những sản phẩm thông minh hơn, hiệu quả hơn, và tiện lợi hơn cho người sử dụng. Việc cập nhật và nắm bắt các xu hướng công nghệ mới sẽ giúp bạn có lựa chọn tốt nhất.',
            'Môi trường và phát triển bền vững đang ngày càng trở thành mối quan tâm lớn của cả nhà sản xuất lẫn người tiêu dùng. Nhiều thương hiệu đã chuyển sang sử dụng vật liệu thân thiện với môi trường, quy trình sản xuất xanh, và bao bì có thể tái chế. Người tiêu dùng có thể đóng góp vào việc bảo vệ môi trường bằng cách lựa chọn sản phẩm bền vững.',
        ]
    },
    {
        'heading': 'Cộng đồng và đánh giá',
        'paragraphs': [
            'Cộng đồng người dùng là nguồn thông tin vô cùng giá trị. Thông qua các diễn đàn, nhóm Facebook, và kênh YouTube chuyên ngành, bạn có thể học hỏi kinh nghiệm từ những người đã sử dụng sản phẩm, tìm hiểu về những vấn đề thường gặp và cách khắc phục. Nhiều thành viên trong cộng đồng sẵn sàng chia sẻ kiến thức và hỗ trợ lẫn nhau.',
            'Phản hồi và đánh giá từ người dùng là tài sản quý giá cho cả nhà sản xuất lẫn người mua tiềm năng. Khi bạn chia sẻ trải nghiệm sử dụng sản phẩm một cách trung thực, bạn không chỉ giúp người khác đưa ra quyết định tốt hơn mà còn tạo áp lực để nhà sản xuất liên tục cải thiện chất lượng sản phẩm và dịch vụ.',
        ]
    },
    {
        'heading': 'Kết luận và khuyến nghị',
        'paragraphs': [
            'Thị trường Việt Nam đang trong giai đoạn chuyển đổi mạnh mẽ với sự gia nhập của nhiều thương hiệu quốc tế và sự trưởng thành của các thương hiệu nội địa. Sự cạnh tranh lành mạnh này mang đến lợi ích trực tiếp cho người tiêu dùng thông qua giá cả hợp lý hơn, chất lượng sản phẩm tốt hơn, và dịch vụ khách hàng ngày càng chuyên nghiệp.',
            'Trong thời đại số hóa, việc tiếp cận thông tin trở nên dễ dàng hơn bao giờ hết. Tuy nhiên, điều này cũng đồng nghĩa với việc có rất nhiều thông tin sai lệch và quảng cáo gây hiểu lầm trên internet. Người tiêu dùng thông minh cần có khả năng phân biệt giữa thông tin đáng tin cậy và những nội dung được tạo ra chỉ nhằm mục đích bán hàng. Hãy luôn kiểm chứng thông tin từ nhiều nguồn.',
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


def pad_article(content, target_words=1000):
    """Replace article content: keep original + add structured lorem sections to reach target."""
    current_words = count_words(content)
    if current_words >= target_words:
        return content, current_words, 0

    padded = content.rstrip()
    added = 0
    idx = 0

    while count_words(padded) < target_words and idx < len(LOREM_SECTIONS):
        padded += build_section(LOREM_SECTIONS[idx])
        idx += 1
        added += 1

    # If still not enough, cycle through
    while count_words(padded) < target_words:
        padded += build_section(LOREM_SECTIONS[idx % len(LOREM_SECTIONS)])
        idx += 1
        added += 1

    final_words = count_words(padded)
    return padded, final_words, added


def get_original_content(content):
    """Strip previously appended lorem ipsum sections to get original content.
    Detects both old format (plain <p> only) and new format (<h2> sections)."""
    # New format: detect section headings
    markers = [s['heading'] for s in LOREM_SECTIONS]
    earliest_pos = len(content)
    for marker in markers:
        tag = f'<h2>{marker}</h2>'
        pos = content.find(tag)
        if pos != -1 and pos < earliest_pos:
            earliest_pos = pos

    # Old format: detect the first old lorem ipsum paragraph
    old_markers = [
        'Trong bối cảnh thị trường ngày càng phát triển, người tiêu dùng Việt Nam',
        'Công nghệ sản xuất hiện đại đã mang đến những cải tiến',
        'Một trong những yếu tố quan trọng nhất khi lựa chọn sản phẩm',
    ]
    for marker in old_markers:
        pos = content.find(marker)
        if pos != -1:
            # Find the start of the <p> tag containing this text
            p_start = content.rfind('<p>', 0, pos)
            if p_start != -1 and p_start < earliest_pos:
                earliest_pos = p_start

    if earliest_pos < len(content):
        return content[:earliest_pos].rstrip()
    return content


def main():
    with app.app_context():
        articles = Article.query.all()
        print(f'Found {len(articles)} articles total\n')

        updated = 0
        for article in articles:
            if not article.content:
                continue

            # Strip any previously appended lorem ipsum
            original = get_original_content(article.content)
            original_words = count_words(original)

            new_content, new_words, sections_added = pad_article(original, target_words=1000)
            article.content = new_content

            # Update reading time based on ~200 words/min
            article.reading_time = max(5, new_words // 200)

            updated += 1
            print(f'  [PAD] "{article.title[:50]}..." {original_words} → {new_words} words (+{sections_added} sections)')

        db.session.commit()
        print(f'\nDone! Updated {updated}/{len(articles)} articles to ~1000 words.')
        print('Each section has <h2> heading + <p> paragraphs for proper carousel split.')


if __name__ == '__main__':
    main()
