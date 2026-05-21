# 🏛️ Stock Law Advisory API Service

Dịch vụ API tư vấn pháp luật chứng khoán Việt Nam sử dụng RAG (Retrieval-Augmented Generation), Milvus, và Gemini AI.

## 🚀 Tính năng
- **RAG Pipeline**: Truy vấn chính xác dựa trên 10+ văn bản pháp luật chứng khoán.
- **FastAPI**: Backend hiệu năng cao với async support.
- **Auth**: OAuth2 Client Credentials Flow với PostgreSQL.
- **Kong Gateway**: Quản lý lưu lượng, rate limiting và bảo mật.
- **Monitoring**: Dashboard Prometheus & Grafana tích hợp.
- **Developer Portal**: Giao diện giới thiệu và tài liệu API hiện đại.

## 🛠️ Yêu cầu
- Docker Desktop
- Python 3.11+
- Gemini API Key (từ Google AI Studio)

## 🏗️ Cài đặt nhanh
1. **Cấu hình môi trường**:
   ```bash
   copy .env.example .env
   # Sửa GEMINI_API_KEY trong .env
   ```
2. **Khởi động toàn bộ hệ thống**:
   ```bash
   docker-compose up -d
   ```
3. **Ingest dữ liệu (Chạy 1 lần)**:
   ```bash
   docker-compose exec api python -m src.data.ingest
   ```

## 📚 Sử dụng
- **Developer Portal**: `http://localhost:8000/`
- **Swagger UI**: `http://localhost:8000/docs`
- **Kong Proxy**: `http://localhost:8005/api/v1/ask`
- **Grafana Dashboards**: `http://localhost:3000` (admin/admin)

## 🧪 Chạy Tests
```bash
# Unit tests
pytest tests/unit

# Integration tests (yêu cầu Docker running)
pytest tests/integration
```

## 🚢 Deployment (AWS)
Dự án được cấu hình sẵn để deploy lên **AWS ECS Fargate** thông qua GitHub Actions. Vui lòng xem `implementation_plan.md` phần Phase 8 để biết hướng dẫn setup AWS chi tiết.
