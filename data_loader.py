"""
Module đọc và xử lý data từ folder knowledge.
Hỗ trợ đọc các file .txt chứa văn bản pháp luật chứng khoán Việt Nam.
"""
import os
import glob
from typing import List

from langchain_core.documents import Document


# Mapping tên file -> tên văn bản đầy đủ
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


def load_text_files(knowledge_dir: str) -> List[Document]:
    """
    Đọc tất cả file .txt trong thư mục knowledge.

    Args:
        knowledge_dir: Đường dẫn tới thư mục chứa các file văn bản pháp luật.

    Returns:
        Danh sách Document objects, mỗi document chứa nội dung 1 file
        kèm metadata (tên văn bản, số hiệu, loại văn bản).
    """
    documents = []
    txt_files = glob.glob(os.path.join(knowledge_dir, "*.txt"))

    if not txt_files:
        print(f"⚠️  Không tìm thấy file .txt nào trong: {knowledge_dir}")
        return documents

    for file_path in sorted(txt_files):
        filename = os.path.basename(file_path)

        # Đọc nội dung file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except UnicodeDecodeError:
            # Thử encoding khác nếu UTF-8 không được
            with open(file_path, "r", encoding="utf-8-sig") as f:
                content = f.read().strip()

        if not content:
            print(f"⚠️  File trống: {filename}")
            continue

        # Lấy metadata cho file
        metadata = FILE_METADATA.get(filename, {
            "ten_van_ban": filename.replace(".txt", ""),
            "so_hieu": filename.replace(".txt", ""),
            "loai_van_ban": "Không xác định",
        })
        metadata["source"] = filename

        doc = Document(page_content=content, metadata=metadata)
        documents.append(doc)
        print(f"✅ Đã đọc: {metadata['ten_van_ban']} ({len(content):,} ký tự)")

    print(f"\n📚 Tổng cộng: {len(documents)} văn bản được đọc")
    return documents


if __name__ == "__main__":
    from config import KNOWLEDGE_DIR
    docs = load_text_files(KNOWLEDGE_DIR)
    for doc in docs:
        print(f"  - {doc.metadata['ten_van_ban']}: {len(doc.page_content):,} chars")
