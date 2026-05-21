"""
Module xây dựng RAG chain sử dụng LangChain.
Kết hợp retriever (Milvus) + LLM (Gemini) để trả lời câu hỏi.
"""
from typing import Optional

from langchain_classic.chains import RetrievalQA  # still valid in langchain
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import Milvus

from config import GEMINI_API_KEY, GEMINI_MODEL, TOP_K
from prompts import RAG_PROMPT_TEMPLATE, NO_CONTEXT_RESPONSE, format_context
from milvus_store import search_similar


def get_llm():
    """
    Khởi tạo LLM (Google Gemini).

    Returns:
        ChatGoogleGenerativeAI instance hoặc None nếu chưa có API key.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        print("⚠️  Chưa cấu hình GEMINI_API_KEY trong file .env")
        print("💡 Chatbot sẽ chạy ở chế độ retrieval-only (chỉ trả về context)")
        return None

    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=0.3,
        max_output_tokens=2048,
    )
    print(f"✅ Đã kết nối Gemini model: {GEMINI_MODEL}")
    return llm


def create_rag_chain(vector_store: Milvus):
    """
    Tạo RAG chain kết hợp retriever + LLM.

    Args:
        vector_store: Milvus vector store đã kết nối.

    Returns:
        RetrievalQA chain hoặc None nếu không có LLM.
    """
    llm = get_llm()
    if llm is None:
        return None

    # Tạo retriever từ vector store
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )

    # Tạo prompt template
    prompt = PromptTemplate(
        template=RAG_PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )

    # Tạo RAG chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )

    print("✅ RAG chain đã sẵn sàng!")
    return chain


def ask_question(
    query: str,
    vector_store: Milvus,
    rag_chain=None,
) -> dict:
    """
    Xử lý câu hỏi và trả về câu trả lời.

    Nếu có RAG chain (Gemini), sử dụng LLM để generate answer.
    Nếu không, chỉ trả về context từ retrieval.

    Args:
        query: Câu hỏi từ người dùng.
        vector_store: Milvus vector store.
        rag_chain: RAG chain (None nếu chưa có LLM).

    Returns:
        Dict chứa "answer" và "sources".
    """
    if rag_chain:
        # Chế độ RAG đầy đủ với LLM
        result = rag_chain.invoke({"query": query})
        answer = result["result"]
        source_docs = result.get("source_documents", [])
    else:
        # Chế độ retrieval-only
        source_docs = search_similar(vector_store, query, top_k=TOP_K)

        if not source_docs:
            answer = NO_CONTEXT_RESPONSE
        else:
            context = format_context(source_docs)
            answer = (
                "📋 **Chế độ Retrieval-Only** (chưa có Gemini API key)\n"
                "Dưới đây là các đoạn văn bản pháp luật liên quan đến câu hỏi của bạn:\n\n"
                f"{context}\n\n"
                "💡 Thêm GEMINI_API_KEY vào file .env để nhận câu trả lời tổng hợp từ AI."
            )

    # Format nguồn tham khảo
    sources = []
    for doc in source_docs:
        source_info = {
            "van_ban": doc.metadata.get("ten_van_ban", "N/A"),
            "dieu": doc.metadata.get("dieu_so", "N/A"),
            "score": doc.metadata.get("similarity_score", "N/A"),
        }
        sources.append(source_info)

    return {
        "answer": answer,
        "sources": sources,
    }
