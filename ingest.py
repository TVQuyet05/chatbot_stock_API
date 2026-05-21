"""
Script xử lý data và lưu vào Milvus.
Chạy một lần để: load data → chunk → embed → lưu vào Milvus.

Sử dụng:
    python ingest.py
"""
import sys
import time

from config import KNOWLEDGE_DIR, MILVUS_COLLECTION
from data_loader import load_text_files
from chunking import chunk_documents
from embedding import get_embedding_model
from milvus_store import create_milvus_store


def main():
    """Pipeline chính: load → chunk → embed → store."""
    print("=" * 60)
    print("🚀 BẮT ĐẦU XỬ LÝ DATA VÀ LƯU VÀO MILVUS")
    print("=" * 60)

    start_time = time.time()

    # ========================================
    # BƯỚC 1: Đọc dữ liệu
    # ========================================
    print("\n📖 BƯỚC 1: Đọc dữ liệu từ folder knowledge...")
    print("-" * 40)
    documents = load_text_files(KNOWLEDGE_DIR)

    if not documents:
        print("❌ Không tìm thấy dữ liệu nào. Kiểm tra lại đường dẫn KNOWLEDGE_DIR.")
        sys.exit(1)

    # ========================================
    # BƯỚC 2: Chia chunks
    # ========================================
    print("\n✂️  BƯỚC 2: Chia văn bản thành chunks...")
    print("-" * 40)
    chunks = chunk_documents(documents)

    if not chunks:
        print("❌ Không tạo được chunk nào từ dữ liệu.")
        sys.exit(1)

    # ========================================
    # BƯỚC 3: Khởi tạo embedding model
    # ========================================
    print("\n🧠 BƯỚC 3: Khởi tạo embedding model...")
    print("-" * 40)
    embeddings = get_embedding_model()

    # ========================================
    # BƯỚC 4: Lưu vào Milvus
    # ========================================
    print("\n💾 BƯỚC 4: Lưu vectors vào Milvus...")
    print("-" * 40)

    try:
        vector_store = create_milvus_store(
            embeddings=embeddings,
            documents=chunks,
            collection_name=MILVUS_COLLECTION,
        )
    except Exception as e:
        print(f"\n❌ Lỗi kết nối Milvus: {e}")
        print("\n💡 Hướng dẫn khắc phục:")
        print("  1. Kiểm tra Docker đang chạy: docker ps")
        print("  2. Chạy Milvus: docker-compose up -d")
        print("  3. Đợi ~30 giây cho Milvus khởi động")
        print("  4. Chạy lại: python ingest.py")
        sys.exit(1)

    # ========================================
    # KẾT QUẢ
    # ========================================
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("✅ HOÀN THÀNH XỬ LÝ DATA!")
    print("=" * 60)
    print(f"📚 Số văn bản đã xử lý: {len(documents)}")
    print(f"🔢 Số chunks đã tạo: {len(chunks)}")
    print(f"📁 Collection: {MILVUS_COLLECTION}")
    print(f"⏱️  Thời gian: {elapsed:.1f} giây")
    print("\n🎯 Tiếp theo: chạy 'python app.py' để sử dụng chatbot!")


if __name__ == "__main__":
    main()
