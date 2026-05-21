"""
System prompts and constant templates for the RAG pipeline.
"""

SYSTEM_PROMPT = (
    "Bạn là một chuyên gia tư vấn pháp luật chứng khoán Việt Nam. "
    "Nhiệm vụ của bạn là trả lời các câu hỏi liên quan đến luật chứng khoán, "
    "quy định thị trường chứng khoán, và các văn bản pháp luật liên quan tại Việt Nam.\n\n"
    "NGUYÊN TẮC TRẢ LỜI:\n"
    "1. Chỉ trả lời dựa trên thông tin được cung cấp trong phần \"Tài liệu tham khảo\".\n"
    "2. Nếu thông tin không có trong tài liệu, hãy nói rõ.\n"
    "3. Trích dẫn rõ ràng nguồn tham khảo (tên văn bản, số Điều).\n"
    "4. Trả lời bằng tiếng Việt, rõ ràng, dễ hiểu.\n"
    "5. Nếu câu hỏi mơ hồ, hãy yêu cầu người dùng làm rõ.\n"
    "6. Phân biệt rõ giữa \"quy định bắt buộc\" và \"khuyến nghị\".\n"
    "7. Sử dụng ngôn ngữ chuyên nghiệp nhưng dễ tiếp cận.\n\n"
    "LƯU Ý: Đây là thông tin tham khảo, KHÔNG phải tư vấn pháp lý chính thức."
)

RAG_PROMPT_TEMPLATE = """Bạn là chuyên gia tư vấn pháp luật chứng khoán Việt Nam. \
Hãy trả lời câu hỏi dựa trên các tài liệu tham khảo được cung cấp.

===== TÀI LIỆU THAM KHẢO =====
{context}
===== HẾT TÀI LIỆU THAM KHẢO =====

CÂU HỎI: {question}

HƯỚNG DẪN TRẢ LỜI:
1. Trả lời chính xác dựa trên tài liệu tham khảo ở trên.
2. Trích dẫn rõ tên văn bản pháp luật và số Điều khi có.
3. Nếu tài liệu không chứa thông tin liên quan, hãy nói rõ.
4. Trả lời bằng tiếng Việt, rõ ràng và chuyên nghiệp.
5. Cuối câu trả lời, liệt kê các nguồn tham khảo đã sử dụng.

TRẢ LỜI:"""

NO_CONTEXT_RESPONSE = (
    "Xin lỗi, tôi không tìm thấy thông tin phù hợp trong "
    "các văn bản pháp luật chứng khoán hiện có để trả lời câu hỏi của bạn.\n\n"
    "Bạn có thể:\n"
    "1. Thử diễn đạt câu hỏi theo cách khác.\n"
    "2. Hỏi về các chủ đề cụ thể.\n"
    "3. Tham khảo trực tiếp tại website của Ủy ban Chứng khoán Nhà nước (www.ssc.gov.vn)."
)

CONTEXT_TEMPLATE = "[Nguồn: {source} - Điều {article}]\n{content}\n"

# Mapping file names → legal document metadata
FILE_METADATA = {
    "59_2019_QH14.txt": {
        "ten_van_ban": "Luật Chứng khoán 2019",
        "so_hieu": "59/2019/QH14",
        "loai_van_ban": "Luật",
    },
    "59_2020_QH14.txt": {
        "ten_van_ban": "Luật Doanh nghiệp 2020",
        "so_hieu": "59/2020/QH14",
        "loai_van_ban": "Luật",
    },
    "61_2020_QH14.txt": {
        "ten_van_ban": "Luật Đầu tư 2020",
        "so_hieu": "61/2020/QH14",
        "loai_van_ban": "Luật",
    },
    "158_2020_ND_CP.txt": {
        "ten_van_ban": "Nghị định 158/2020/NĐ-CP về chứng khoán phái sinh",
        "so_hieu": "158/2020/NĐ-CP",
        "loai_van_ban": "Nghị định",
    },
    "155_2020_ND_CP.txt": {
        "ten_van_ban": "Nghị định 155/2020/NĐ-CP hướng dẫn Luật Chứng khoán",
        "so_hieu": "155/2020/NĐ-CP",
        "loai_van_ban": "Nghị định",
    },
    "96_2020_TT_BTC.txt": {
        "ten_van_ban": "Thông tư 96/2020/TT-BTC hướng dẫn công bố thông tin",
        "so_hieu": "96/2020/TT-BTC",
        "loai_van_ban": "Thông tư",
    },
    "121_2020_TT_BTC.txt": {
        "ten_van_ban": "Thông tư 121/2020/TT-BTC quy định hoạt động công ty chứng khoán",
        "so_hieu": "121/2020/TT-BTC",
        "loai_van_ban": "Thông tư",
    },
    "109_QD_VSD.txt": {
        "ten_van_ban": "Quyết định 109/QĐ-VSD của Trung tâm Lưu ký Chứng khoán",
        "so_hieu": "109/QĐ-VSD",
        "loai_van_ban": "Quyết định",
    },
    "15_QD_HDTV.txt": {
        "ten_van_ban": "Quyết định 15/QĐ-HĐTV quy chế giao dịch chứng khoán phái sinh",
        "so_hieu": "15/QĐ-HĐTV",
        "loai_van_ban": "Quyết định",
    },
    "39_QD_HDTV.txt": {
        "ten_van_ban": "Quyết định 39/QĐ-HĐTV quy chế hoạt động bù trừ",
        "so_hieu": "39/QĐ-HĐTV",
        "loai_van_ban": "Quyết định",
    },
}
