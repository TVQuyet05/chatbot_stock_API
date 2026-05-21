"""
Module quản lý kết nối và thao tác với Milvus vector database.
Sử dụng langchain_community.vectorstores.Milvus để đạt độ ổn định cao hơn
trong môi trường local standalone.
"""
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import Milvus
from pymilvus import connections, utility

from config import (
    MILVUS_HOST,
    MILVUS_PORT,
    MILVUS_COLLECTION,
    TOP_K,
)


def create_milvus_store(
    embeddings,
    documents: Optional[List[Document]] = None,
    collection_name: str = MILVUS_COLLECTION,
) -> Milvus:
    """
    Tạo hoặc kết nối tới Milvus vector store.
    """
    print(f"🔗 Kết nối Milvus: {MILVUS_HOST}:{MILVUS_PORT}")

    # 1. Luôn đảm bảo kết nối 'default' được thiết lập
    try:
        if "default" not in connections.list_connections():
            connections.connect(
                alias="default",
                host=MILVUS_HOST,
                port=str(MILVUS_PORT)
            )
            print("✅ Đã thiết lập kết nối 'default' thành công.")
    except Exception as e:
        print(f"⚠️ Lỗi khi kết nối pymilvus: {e}")

    if documents:
        print(f"📦 Đang lưu {len(documents)} chunks vào Milvus...")
        
        # 2. Xóa collection cũ thủ công (langchain_community version ít lỗi drop hơn)
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)
            print(f"🗑️ Đã xóa collection cũ: {collection_name}")

        # 3. Sử dụng from_documents của langchain_community
        # Đây là bản ổn định nhất, tự động handle ID và schema tốt
        vector_store = Milvus.from_documents(
            documents=documents,
            embedding=embeddings,
            collection_name=collection_name,
            connection_args={
                "host": MILVUS_HOST,
                "port": str(MILVUS_PORT)
            }
        )
        print(f"✅ Đã lưu thành công {len(documents)} chunks!")
    else:
        # Chế độ kết nối để query
        vector_store = Milvus(
            embedding_function=embeddings,
            collection_name=collection_name,
            connection_args={
                "host": MILVUS_HOST,
                "port": str(MILVUS_PORT)
            }
        )
        print("✅ Đã kết nối tới Milvus!")

    return vector_store


def search_similar(
    vector_store: Milvus,
    query: str,
    top_k: int = TOP_K,
) -> List[Document]:
    """
    Tìm kiếm semantic search.
    """
    results = vector_store.similarity_search_with_score(
        query=query,
        k=top_k,
    )

    filtered = []
    for doc, score in results:
        doc.metadata["similarity_score"] = round(score, 4)
        filtered.append(doc)

    return filtered
