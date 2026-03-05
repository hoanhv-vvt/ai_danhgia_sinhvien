# Student Info Extraction API

API trích xuất thông tin sinh viên từ ảnh sử dụng Google Gemini OCR.

## Features

- Upload ảnh bảng điểm / giấy tờ sinh viên
- Tự động OCR và trích xuất: **Tên trường**, **Ngành học**, **GPA**
- Sử dụng Gemini 2.0 Flash cho độ chính xác cao

## Quick Start

```bash
# 1. Tạo virtual environment
python -m venv venv
source venv/bin/activate

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. Cấu hình API key
cp .env.example .env
# Sửa file .env, thay thế GEMINI_API_KEY bằng key thật

# 4. Chạy server
python main.py
```

## API Endpoints

### `POST /api/extract`
Upload ảnh và trích xuất thông tin sinh viên.

```bash
curl -X POST http://localhost:8000/api/extract \
  -F "file=@bangdiem.jpg"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "school_name": "Đại học Bách Khoa Hà Nội",
    "major": "Công nghệ thông tin",
    "gpa": 3.45
  },
  "message": "Trích xuất thông tin thành công"
}
```

### `GET /health`
Health check.

## Swagger Docs

Truy cập `http://localhost:8000/docs` sau khi chạy server.
# ai_danhgia_sinhvien
# ai_danhgia_sinhvien
