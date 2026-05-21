# 🏛️ Hướng Dẫn Cài Đặt - RAG Chatbot Chứng Khoán Việt Nam

## Yêu Cầu Hệ Thống

- **Python**: 3.9 trở lên
- **Docker Desktop**: để chạy Milvus database
- **RAM**: tối thiểu 8GB (khuyến nghị 16GB)
- **Disk**: ~5GB cho Docker images + model

---

## Bước 1: Cài Đặt Docker Desktop

1. Tải Docker Desktop từ: https://www.docker.com/products/docker-desktop
2. Cài đặt và khởi động Docker Desktop
3. Kiểm tra Docker đã chạy:

```bash
docker --version
docker-compose --version
```

---

## Bước 2: Khởi Động Milvus Database

Mở terminal tại thư mục project và chạy:

```bash
# Khởi động Milvus (lần đầu sẽ tải images, mất ~5-10 phút)
docker-compose up -d

# Kiểm tra trạng thái (đợi ~30 giây cho Milvus sẵn sàng)
docker-compose ps

# Kiểm tra health
curl http://localhost:9091/healthz
```

**Lưu ý:** Milvus cần ~30-60 giây để khởi động hoàn tất.

Khi muốn dừng:
```bash
docker-compose down
```

---

## Bước 3: Tạo Python Virtual Environment

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt (Windows)
.\venv\Scripts\activate

# Kích hoạt (macOS/Linux)
source venv/bin/activate
```

---

## Bước 4: Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

**Lưu ý:** Lần đầu cài `torch` và `sentence-transformers` sẽ mất thời gian (~5-10 phút).

---

## Bước 5: Cấu Hình Môi Trường

```bash
# Copy file cấu hình mẫu
copy .env.example .env
```

Mở file `.env` và chỉnh sửa:

```env
# Thêm Gemini API key (lấy từ https://aistudio.google.com/apikey)
GEMINI_API_KEY=your_actual_api_key_here

# Các cấu hình khác giữ nguyên mặc định
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

> ⚠️ Nếu chưa có Gemini API key, chatbot vẫn hoạt động ở chế độ **retrieval-only** (chỉ trả về context liên quan).

---

## Bước 6: Xử Lý Data và Lưu Vào Milvus

```bash
python ingest.py
```

Kết quả mong đợi:
```
✅ Đã đọc: Luật Chứng khoán 2019 (336,411 ký tự)
✅ Đã đọc: Luật Doanh nghiệp 2020 (430,551 ký tự)
...
📚 Tổng cộng: 10 văn bản được đọc
✂️  Tổng cộng: ~500+ chunks
💾 Đã lưu thành công vào Milvus!
```

---

## Bước 7: Chạy Chatbot

```bash
python app.py
```

Thử hỏi:
```
👤 Câu hỏi: Công ty đại chúng là gì?
👤 Câu hỏi: Điều kiện chào bán chứng khoán ra công chúng?
👤 Câu hỏi: Quy định về chứng khoán phái sinh?
```

Gõ `exit` để thoát, `help` để xem hướng dẫn.

---

## Bước 8: Thêm Gemini API Key (Tùy Chọn)

1. Truy cập: https://aistudio.google.com/apikey
2. Tạo API key mới
3. Mở file `.env` và thay thế:
   ```
   GEMINI_API_KEY=AIzaSy...your_key_here
   ```
4. Khởi động lại chatbot: `python app.py`

---

## Cấu Trúc Project

```
Chatbot_Stock/
├── docker-compose.yml      # Milvus Docker setup
├── requirements.txt        # Python dependencies
├── .env.example           # Template biến môi trường
├── .env                   # Cấu hình thực tế (tự tạo)
├── config.py              # Cấu hình chung
├── data_loader.py         # Đọc data từ knowledge folder
├── chunking.py            # Chia chunks theo Điều
├── embedding.py           # Vietnamese embedding model
├── milvus_store.py        # Milvus vector store
├── prompts.py             # Prompt tiếng Việt
├── rag_chain.py           # LangChain RAG pipeline
├── ingest.py              # Script xử lý data
├── app.py                 # Chatbot CLI
├── SETUP_GUIDE.md         # File hướng dẫn này
└── datasets/
    └── ViSecQA/
        └── knowledge/     # 10 file .txt văn bản pháp luật
```

---

## Xử Lý Lỗi Thường Gặp

### Lỗi kết nối Milvus
```
❌ Lỗi kết nối Milvus: Connection refused
```
**Giải pháp:**
```bash
docker-compose up -d
# Đợi 30-60 giây
docker-compose ps  # Kiểm tra trạng thái = running
```

### Lỗi thiếu memory khi load model
```
RuntimeError: CUDA out of memory
```
**Giải pháp:** Model sẽ tự động chạy trên CPU. Nếu vẫn thiếu RAM, hãy đóng các ứng dụng khác.

### Lỗi import module
```
ModuleNotFoundError: No module named 'langchain'
```
**Giải pháp:**
```bash
pip install -r requirements.txt
```
