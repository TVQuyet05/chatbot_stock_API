"""
Module chia chunks tối ưu cho văn bản pháp luật Việt Nam.

Chiến lược:
- Chia theo Điều (Article) - đơn vị pháp lý cơ bản
- Các Điều quá dài sẽ được chia nhỏ theo khoản (1, 2, 3...)
- Gắn metadata đầy đủ: tên văn bản, số Điều, số hiệu
"""
import re
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import MAX_CHUNK_SIZE, CHUNK_OVERLAP


def split_by_articles(document: Document) -> List[Document]:
    """
    Chia văn bản pháp luật theo Điều (Article).

    Mỗi Điều trở thành một chunk riêng biệt. Nếu một Điều quá dài
    (vượt MAX_CHUNK_SIZE), sẽ được chia nhỏ hơn bằng
    RecursiveCharacterTextSplitter.

    Args:
        document: Document chứa toàn bộ nội dung 1 văn bản pháp luật.

    Returns:
        Danh sách các Document chunks đã được chia.
    """
    content = document.page_content
    base_metadata = document.metadata.copy()

    # Pattern nhận diện đầu mỗi Điều
    # Ví dụ: "Điều 1.", "Điều 15.", "Điều 100."
    article_pattern = re.compile(r'(?=Điều\s+\d+[\.\:])')

    # Chia văn bản theo Điều
    parts = article_pattern.split(content)
    chunks = []

    # Fallback splitter cho các chunks quá dài, giờ thêm việc cắt theo khoản
    fallback_splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n(?=\d+\.)", "\n(?=[a-z]\))", "\n", ". ", " "],
        is_separator_regex=True
    )

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Trích số Điều từ text
        article_match = re.match(r'Điều\s+(\d+)[\.\:]?\s*(.*)', part, re.DOTALL)
        if article_match:
            article_num = article_match.group(1)
            # Lấy tên Điều (dòng đầu tiên sau số Điều)
            first_line = part.split('\n')[0].strip()
            article_title = first_line
        else:
            article_num = "0"
            article_title = "Phần mở đầu / Mục"

        # Tạo metadata cho chunk
        chunk_metadata = base_metadata.copy()
        chunk_metadata["dieu_so"] = article_num
        chunk_metadata["tieu_de_dieu"] = article_title

        # Nếu chunk quá dài, chia nhỏ hơn
        if len(part) > MAX_CHUNK_SIZE:
            sub_docs = fallback_splitter.create_documents(
                texts=[part],
                metadatas=[chunk_metadata],
            )
            # Đánh số thứ tự cho các sub-chunks
            for i, sub_doc in enumerate(sub_docs):
                sub_doc.metadata["phan"] = f"{i + 1}/{len(sub_docs)}"
                sub_doc.metadata["tieu_de_dieu"] = article_title
            chunks.extend(sub_docs)
        else:
            if len(part) < 50:
                # Bỏ qua các đoạn quá ngắn (tiêu đề mục, etc.)
                continue
            doc = Document(page_content=part, metadata=chunk_metadata)
            chunks.append(doc)

    return chunks


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Chia tất cả documents thành chunks tối ưu.

    Args:
        documents: Danh sách Document đã đọc từ data_loader.

    Returns:
        Danh sách tất cả chunks đã được chia.
    """
    all_chunks = []

    for doc in documents:
        doc_name = doc.metadata.get("ten_van_ban", "Unknown")
        chunks = split_by_articles(doc)
        all_chunks.extend(chunks)
        print(f"📄 {doc_name}: {len(chunks)} chunks")

    print(f"\n🔢 Tổng cộng: {len(all_chunks)} chunks")

    # Thống kê kích thước chunks
    sizes = [len(c.page_content) for c in all_chunks]
    if sizes:
        avg_size = sum(sizes) / len(sizes)
        print(f"📊 Kích thước trung bình: {avg_size:.0f} ký tự")
        print(f"📊 Nhỏ nhất: {min(sizes)} | Lớn nhất: {max(sizes)} ký tự")

    return all_chunks


if __name__ == "__main__":
    from config import KNOWLEDGE_DIR
    from data_loader import load_text_files

    docs = load_text_files(KNOWLEDGE_DIR)
    chunks = chunk_documents(docs)

    # Hiển thị 3 chunks mẫu
    print("\n" + "=" * 60)
    print("📝 MẪU 3 CHUNKS ĐẦU TIÊN:")
    print("=" * 60)
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i + 1} ---")
        print(f"Văn bản: {chunk.metadata.get('ten_van_ban', 'N/A')}")
        print(f"Điều: {chunk.metadata.get('dieu_so', 'N/A')}")
        print(f"Nội dung ({len(chunk.page_content)} chars):")
        print(chunk.page_content[:300] + "...")
