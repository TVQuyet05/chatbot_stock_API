"""
Module embedding sử dụng vietnamese-bi-encoder cho tiếng Việt.
Cập nhật sử dụng langchain-huggingface thay cho langchain-community.
"""
from langchain_huggingface import HuggingFaceEmbeddings

from config import EMBEDDING_MODEL


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Khởi tạo và trả về model embedding tiếng Việt.
    """
    print(f"🔄 Đang tải model embedding: {EMBEDDING_MODEL}")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"}, 
        encode_kwargs={
            "normalize_embeddings": True,
            "batch_size": 32,
        },
    )

    print("✅ Model embedding đã sẵn sàng!")
    return embeddings


if __name__ == "__main__":
    model = get_embedding_model()
    test_texts = ["Công ty đại chúng là gì?"]
    vectors = model.embed_documents(test_texts)
    print(f"✅ Dimension: {len(vectors[0])}")
