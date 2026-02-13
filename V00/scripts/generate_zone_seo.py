"""
Generate SEO content for all Zone pages
100-200 lines with H3-H4 headings for SEO
"""

import random

def generate_zone_seo_content(zone_name, zone_description):
    """Generate 100-200 line SEO content with H3-H4 headings"""

    lorem_paragraphs = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.",
        "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.",
        "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga.",
        "Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint.",
    ]

    content = f"<h2>Tất cả về {zone_name}</h2>\n\n"
    content += f"<p>{zone_description} Đây là hệ thống quan trọng cần được hiểu rõ để bảo dưỡng và sửa chữa hiệu quả.</p>\n\n"

    # Main sections with H3
    main_sections = [
        ("Giới thiệu tổng quan", 4),
        ("Cấu tạo và nguyên lý hoạt động", 5),
        ("Các bộ phận quan trọng", 4),
        ("Dấu hiệu hư hỏng và cách nhận biết", 4),
        ("Bảo dưỡng định kỳ", 3),
        ("Chi phí sửa chữa và thay thế", 3),
        ("Lời khuyên từ chuyên gia", 3),
    ]

    line_count = 2  # Already have 2 lines

    for section_title, num_subsections in main_sections:
        content += f"<h3>{section_title}</h3>\n"
        line_count += 1

        # Add 2-3 paragraphs
        for _ in range(random.randint(2, 3)):
            para = random.choice(lorem_paragraphs)
            content += f"<p>{para}</p>\n\n"
            # Count lines (each paragraph is ~4-5 lines when wrapped)
            line_count += 5

        # Add H4 subsections
        for i in range(num_subsections):
            content += f"<h4>{section_title} - Phần {i+1}</h4>\n"
            line_count += 1

            # Add 1-2 paragraphs per subsection
            for _ in range(random.randint(1, 2)):
                para = random.choice(lorem_paragraphs)
                content += f"<p>{para}</p>\n\n"
                line_count += 4

        # Add a list
        content += "<ul>\n"
        line_count += 1
        for i in range(5):
            content += f"<li>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt.</li>\n"
            line_count += 1
        content += "</ul>\n\n"
        line_count += 1

        if line_count >= 150:  # Target ~150 lines
            break

    # Add FAQ section at the end
    content += "<h3>Câu hỏi thường gặp (FAQ)</h3>\n"
    line_count += 1

    faqs = [
        ("Khi nào cần bảo dưỡng?", "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Thường xuyên kiểm tra sau 10,000km hoặc 6 tháng."),
        ("Chi phí bao nhiêu?", "Chi phí dao động từ 500,000đ đến 5,000,000đ tùy mức độ hư hỏng."),
        ("Có thể tự làm tại nhà không?", "Một số công việc đơn giản có thể tự làm, nhưng nên đến garage chuyên nghiệp."),
        ("Dấu hiệu cần thay thế?", "Khi xuất hiện tiếng kêu bất thường, rung lắc, hoặc giảm hiệu suất."),
    ]

    for q, a in faqs:
        content += f"<h4>Q: {q}</h4>\n"
        content += f"<p><strong>A:</strong> {a}</p>\n\n"
        line_count += 3

    content += f"<p><em>Bài viết về {zone_name} được biên soạn dựa trên kinh nghiệm thực tế và tài liệu kỹ thuật. Nội dung mang tính chất tham khảo.</em></p>\n"
    line_count += 2

    return content, line_count


# Test
if __name__ == "__main__":
    test_content, lines = generate_zone_seo_content(
        "Hệ thống treo",
        "Hệ thống treo bao gồm phuộc, lò xo, cao su, rotuyn, thanh cân bằng — giữ xe êm ái trên mọi cung đường."
    )

    print(f"✅ Generated SEO content")
    print(f"Lines: ~{lines}")
    print(f"Length: {len(test_content)} characters")
    print(f"\nPreview:\n{test_content[:500]}...")
