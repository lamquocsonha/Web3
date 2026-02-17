"""
Pad all articles to ~1000 words with Vietnamese lorem ipsum paragraphs.
This ensures enough <p> blocks for the product carousel to split nicely in the middle.
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from models import db, Article

# Vietnamese lorem ipsum paragraphs (each ~80-120 words)
LOREM_PARAGRAPHS = [
    '<p>Trong bối cảnh thị trường ngày càng phát triển, người tiêu dùng Việt Nam đang có nhiều lựa chọn hơn bao giờ hết. Việc tìm hiểu kỹ thông tin trước khi quyết định mua sắm không chỉ giúp tiết kiệm chi phí mà còn đảm bảo chất lượng sản phẩm phù hợp với nhu cầu thực tế. Các chuyên gia khuyến cáo rằng việc so sánh giá cả từ nhiều nguồn khác nhau, đọc đánh giá từ người dùng thực tế, và tham khảo ý kiến từ cộng đồng là những bước quan trọng không nên bỏ qua trong quá trình ra quyết định.</p>',

    '<p>Công nghệ sản xuất hiện đại đã mang đến những cải tiến đáng kể về chất lượng và độ bền của sản phẩm. Các nhà sản xuất liên tục đầu tư vào nghiên cứu và phát triển để cho ra đời những sản phẩm đáp ứng tiêu chuẩn quốc tế. Điều này đồng nghĩa với việc người tiêu dùng có thể tiếp cận được những sản phẩm chất lượng cao với mức giá hợp lý hơn so với trước đây, đặc biệt khi mua hàng qua các kênh thương mại điện tử uy tín.</p>',

    '<p>Một trong những yếu tố quan trọng nhất khi lựa chọn sản phẩm là hiểu rõ thông số kỹ thuật và cách sử dụng đúng cách. Việc sử dụng sai cách hoặc không tuân thủ hướng dẫn của nhà sản xuất có thể dẫn đến hư hỏng sớm, giảm hiệu suất hoạt động, và thậm chí gây nguy hiểm cho người sử dụng. Do đó, hãy luôn đọc kỹ hướng dẫn sử dụng và tham khảo ý kiến chuyên gia khi cần thiết để đảm bảo an toàn và hiệu quả tối đa.</p>',

    '<p>Bảo dưỡng định kỳ là chìa khóa để kéo dài tuổi thọ và duy trì hiệu suất hoạt động ổn định của bất kỳ sản phẩm nào. Nhiều người thường bỏ qua việc bảo dưỡng cho đến khi sản phẩm gặp sự cố, dẫn đến chi phí sửa chữa cao hơn nhiều so với chi phí bảo dưỡng định kỳ. Các chuyên gia khuyến nghị nên lập lịch bảo dưỡng cụ thể và tuân thủ nghiêm ngặt để tránh những hỏng hóc không đáng có và tiết kiệm chi phí dài hạn.</p>',

    '<p>Xu hướng mua sắm trực tuyến đang ngày càng phổ biến tại Việt Nam, với sự phát triển mạnh mẽ của các sàn thương mại điện tử như Shopee, Lazada, và Tiki. Người tiêu dùng có thể dễ dàng so sánh giá, đọc đánh giá, và đặt hàng chỉ với vài thao tác trên điện thoại. Tuy nhiên, cần lưu ý chọn mua từ các shop uy tín, kiểm tra kỹ thông tin sản phẩm và chính sách đổi trả để tránh mua phải hàng kém chất lượng hoặc hàng nhái.</p>',

    '<p>Kiến thức chuyên môn đóng vai trò then chốt trong việc đưa ra quyết định đúng đắn. Khi bạn hiểu rõ về sản phẩm, bạn có thể tự tin hơn trong việc lựa chọn, sử dụng và bảo dưỡng. Điều này không chỉ giúp tiết kiệm thời gian và tiền bạc mà còn giúp bạn tránh được những rủi ro không đáng có. Hãy dành thời gian tìm hiểu thông qua các nguồn tài liệu uy tín, diễn đàn chuyên ngành, và ý kiến từ những người có kinh nghiệm thực tế.</p>',

    '<p>Chất lượng dịch vụ sau bán hàng là một tiêu chí quan trọng không kém chất lượng sản phẩm. Một nhà cung cấp tốt sẽ luôn sẵn sàng hỗ trợ khách hàng từ tư vấn trước mua, hướng dẫn sử dụng, đến bảo hành và sửa chữa. Khi chọn mua sản phẩm, hãy ưu tiên những thương hiệu và đại lý có chính sách bảo hành rõ ràng, đội ngũ hỗ trợ kỹ thuật chuyên nghiệp, và mạng lưới dịch vụ rộng khắp để đảm bảo quyền lợi lâu dài.</p>',

    '<p>An toàn luôn là ưu tiên hàng đầu trong mọi lĩnh vực. Việc sử dụng sản phẩm chất lượng, đúng tiêu chuẩn không chỉ bảo vệ bản thân mà còn bảo vệ những người xung quanh. Các cơ quan quản lý ngày càng siết chặt tiêu chuẩn chất lượng, buộc nhà sản xuất phải tuân thủ nghiêm ngặt các quy định về an toàn. Người tiêu dùng nên tìm hiểu các chứng nhận chất lượng như ISO, TCVN và các tiêu chuẩn ngành để đảm bảo sản phẩm đáp ứng yêu cầu.</p>',

    '<p>Chi phí sở hữu tổng thể (Total Cost of Ownership) là một khái niệm quan trọng mà nhiều người thường bỏ qua. Giá mua ban đầu chỉ là một phần trong tổng chi phí, bạn còn cần tính đến chi phí lắp đặt, vận hành, bảo dưỡng, và thay thế linh kiện trong suốt vòng đời sản phẩm. Một sản phẩm có giá mua cao hơn nhưng bền bỉ và ít chi phí bảo dưỡng có thể tiết kiệm hơn so với sản phẩm rẻ nhưng nhanh hỏng và tốn kém khi sửa chữa.</p>',

    '<p>Cộng đồng người dùng là nguồn thông tin vô cùng giá trị. Thông qua các diễn đàn, nhóm Facebook, và kênh YouTube chuyên ngành, bạn có thể học hỏi kinh nghiệm từ những người đã sử dụng sản phẩm, tìm hiểu về những vấn đề thường gặp và cách khắc phục. Nhiều thành viên trong cộng đồng sẵn sàng chia sẻ kiến thức và hỗ trợ lẫn nhau, tạo nên một mạng lưới hỗ trợ đáng tin cậy cho người tiêu dùng.</p>',

    '<p>Trong thời đại số hóa, việc tiếp cận thông tin trở nên dễ dàng hơn bao giờ hết. Tuy nhiên, điều này cũng đồng nghĩa với việc có rất nhiều thông tin sai lệch và quảng cáo gây hiểu lầm trên internet. Người tiêu dùng thông minh cần có khả năng phân biệt giữa thông tin đáng tin cậy và những nội dung được tạo ra chỉ nhằm mục đích bán hàng. Hãy luôn kiểm chứng thông tin từ nhiều nguồn trước khi đưa ra quyết định mua sắm quan trọng.</p>',

    '<p>Môi trường và phát triển bền vững đang ngày càng trở thành mối quan tâm lớn của cả nhà sản xuất lẫn người tiêu dùng. Nhiều thương hiệu đã chuyển sang sử dụng vật liệu thân thiện với môi trường, quy trình sản xuất xanh, và bao bì có thể tái chế. Người tiêu dùng có thể đóng góp vào việc bảo vệ môi trường bằng cách lựa chọn sản phẩm bền vững, sử dụng sản phẩm đúng cách để kéo dài tuổi thọ, và tái chế khi sản phẩm hết hạn sử dụng.</p>',

    '<p>Đổi mới sáng tạo là động lực chính thúc đẩy sự phát triển của ngành công nghiệp. Các công nghệ mới như trí tuệ nhân tạo, Internet vạn vật (IoT), và vật liệu tiên tiến đang được ứng dụng ngày càng rộng rãi, mang đến những sản phẩm thông minh hơn, hiệu quả hơn, và tiện lợi hơn cho người sử dụng. Việc cập nhật và nắm bắt các xu hướng công nghệ mới sẽ giúp bạn có những lựa chọn tốt nhất khi mua sắm.</p>',

    '<p>Kinh nghiệm thực tế cho thấy rằng việc đầu tư vào sản phẩm chất lượng từ đầu luôn là quyết định khôn ngoan về lâu dài. Sản phẩm tốt không chỉ mang lại hiệu suất vượt trội mà còn ít gặp sự cố, giảm thời gian ngừng hoạt động, và tạo sự yên tâm cho người sử dụng. Hãy coi việc mua sắm như một khoản đầu tư chứ không chỉ là chi phí, và bạn sẽ thấy giá trị thực sự mà sản phẩm chất lượng mang lại theo thời gian.</p>',

    '<p>Thị trường Việt Nam đang trong giai đoạn chuyển đổi mạnh mẽ với sự gia nhập của nhiều thương hiệu quốc tế và sự trưởng thành của các thương hiệu nội địa. Sự cạnh tranh lành mạnh này mang đến lợi ích trực tiếp cho người tiêu dùng thông qua giá cả hợp lý hơn, chất lượng sản phẩm tốt hơn, và dịch vụ khách hàng ngày càng chuyên nghiệp. Đây là thời điểm tốt để người tiêu dùng tận dụng các ưu đãi và lựa chọn sản phẩm phù hợp nhất với nhu cầu của mình.</p>',

    '<p>Việc lắp đặt và cài đặt đúng cách ảnh hưởng trực tiếp đến hiệu suất và tuổi thọ của sản phẩm. Nhiều sản phẩm yêu cầu quy trình lắp đặt chuyên nghiệp để đảm bảo hoạt động tối ưu và duy trì bảo hành. Nếu bạn không có kinh nghiệm hoặc dụng cụ phù hợp, hãy tìm đến các dịch vụ lắp đặt chuyên nghiệp thay vì tự làm để tránh rủi ro hư hỏng sản phẩm hoặc mất bảo hành do lắp đặt không đúng kỹ thuật.</p>',

    '<p>So sánh sản phẩm là bước không thể thiếu trong quá trình mua sắm thông minh. Khi so sánh, hãy chú ý đến những tiêu chí quan trọng như chất lượng vật liệu, thông số kỹ thuật, xuất xứ sản xuất, chính sách bảo hành, và đánh giá từ người dùng thực tế. Đừng chỉ dựa vào giá cả làm tiêu chí duy nhất, vì sản phẩm rẻ nhất không phải lúc nào cũng là lựa chọn tiết kiệm nhất khi tính đến chi phí sở hữu tổng thể trong dài hạn.</p>',

    '<p>Thương mại điện tử đã thay đổi hoàn toàn cách người tiêu dùng mua sắm và tiếp cận sản phẩm. Từ việc phải đến cửa hàng trực tiếp, giờ đây bạn có thể duyệt hàng ngàn sản phẩm, đọc hàng trăm đánh giá, và đặt hàng giao tận nhà chỉ trong vài phút. Các chương trình khuyến mãi như flash sale, mã giảm giá, và freeship cũng giúp người tiêu dùng tiết kiệm đáng kể. Tuy nhiên, cần tỉnh táo trước những ưu đãi quá hấp dẫn để tránh mua sắm impulsive.</p>',

    '<p>Phản hồi và đánh giá từ người dùng là tài sản quý giá cho cả nhà sản xuất lẫn người mua tiềm năng. Khi bạn chia sẻ trải nghiệm sử dụng sản phẩm một cách trung thực, bạn không chỉ giúp người khác đưa ra quyết định tốt hơn mà còn tạo áp lực để nhà sản xuất liên tục cải thiện chất lượng. Hãy dành thời gian viết đánh giá chi tiết sau khi sử dụng sản phẩm, bao gồm cả ưu điểm lẫn nhược điểm mà bạn trải nghiệm được.</p>',

    '<p>Bảo quản đúng cách là yếu tố quyết định tuổi thọ của nhiều loại sản phẩm. Điều kiện nhiệt độ, độ ẩm, ánh sáng, và môi trường xung quanh đều có thể ảnh hưởng đến chất lượng sản phẩm theo thời gian. Hãy tuân thủ hướng dẫn bảo quản của nhà sản xuất, tránh để sản phẩm tiếp xúc với các yếu tố gây hại, và kiểm tra định kỳ tình trạng sản phẩm để phát hiện sớm các dấu hiệu xuống cấp và có biện pháp xử lý kịp thời.</p>',
]


def count_words(html_text):
    """Count words in HTML text (strip tags first)."""
    clean = re.sub(r'<[^>]+>', ' ', html_text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return len(clean.split())


def pad_article(content, target_words=1000):
    """Pad article content with lorem ipsum paragraphs until reaching target word count."""
    current_words = count_words(content)
    if current_words >= target_words:
        return content, current_words, 0

    # Add a transition heading before lorem ipsum
    padded = content.rstrip()

    # Add lorem paragraphs
    added = 0
    idx = 0
    while count_words(padded) < target_words and idx < len(LOREM_PARAGRAPHS):
        padded += '\n\n' + LOREM_PARAGRAPHS[idx]
        idx += 1
        added += 1

    # If still not enough, cycle through again
    while count_words(padded) < target_words:
        padded += '\n\n' + LOREM_PARAGRAPHS[idx % len(LOREM_PARAGRAPHS)]
        idx += 1
        added += 1

    final_words = count_words(padded)
    return padded, final_words, added


def main():
    with app.app_context():
        articles = Article.query.all()
        print(f'Found {len(articles)} articles total\n')

        updated = 0
        for article in articles:
            old_words = count_words(article.content) if article.content else 0
            if old_words >= 950:
                print(f'  [SKIP] "{article.title[:50]}..." already {old_words} words')
                continue

            new_content, new_words, paragraphs_added = pad_article(
                article.content or '', target_words=1000
            )
            article.content = new_content

            # Update reading time based on ~200 words/min
            article.reading_time = max(5, new_words // 200)

            updated += 1
            print(f'  [PAD] "{article.title[:50]}..." {old_words} → {new_words} words (+{paragraphs_added} paragraphs)')

        db.session.commit()
        print(f'\nDone! Updated {updated}/{len(articles)} articles to ~1000 words.')


if __name__ == '__main__':
    main()
