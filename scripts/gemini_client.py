import json
import logging
import mimetypes
import os
from pathlib import Path

import httpx
from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES
from models import StudentInfo

logger = logging.getLogger(__name__)

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

EXTRACTION_PROMPT = """Bạn là một chuyên gia OCR và trích xuất thông tin từ giấy tờ sinh viên Việt Nam.

Hãy phân tích ảnh được cung cấp và trích xuất các thông tin sau:

1. **school_name**: Tên trường học / đại học (ví dụ: "Đại học Bách Khoa Hà Nội", "Đại học Kinh tế Quốc dân")
2. **major**: Tên ngành học / chuyên ngành (ví dụ: "Công nghệ thông tin", "Quản trị kinh doanh")
3. **gpa**: Điểm trung bình tích lũy (GPA) - là một số thực, ví dụ 3.45

Lưu ý:
- Nếu không tìm thấy thông tin nào, trả về null cho trường đó.
- GPA có thể theo thang 4.0. Trả về đúng giá trị gốc trên giấy tờ.
- Tên trường có thể viết tắt, hãy trả về tên đầy đủ nếu có thể nhận biết.
- Ảnh có thể là: bảng điểm, giấy chứng nhận sinh viên, thẻ sinh viên, bằng tốt nghiệp, transcript, v.v.

Trả về kết quả dưới dạng JSON với đúng format sau:
{
  "school_name": "string hoặc null",
  "major": "string hoặc null",
  "gpa": number hoặc null
}

CHỈ trả về JSON, không thêm bất kỳ text nào khác."""


def _is_url(source: str) -> bool:
    """Kiểm tra xem source có phải URL không."""
    return source.startswith("http://") or source.startswith("https://")


async def _load_image_from_url(url: str) -> tuple[bytes, str]:
    """
    Tải ảnh từ URL.

    Returns:
        Tuple (image_bytes, mime_type)
    """
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        response = await http_client.get(url)
        response.raise_for_status()

    content_type = response.headers.get("content-type", "").split(";")[0].strip()

    # Fallback: guess MIME type từ URL nếu header không rõ ràng
    if not content_type or content_type == "application/octet-stream":
        guessed, _ = mimetypes.guess_type(url)
        content_type = guessed or "image/jpeg"

    return response.content, content_type


def _load_image_from_path(file_path: str) -> tuple[bytes, str]:
    """
    Đọc ảnh từ file path.

    Returns:
        Tuple (image_bytes, mime_type)
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File không tồn tại: {file_path}")

    if not path.is_file():
        raise ValueError(f"Đường dẫn không phải file: {file_path}")

    ext = path.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Định dạng file không hỗ trợ: '{ext}'. "
            f"Chấp nhận: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    file_size = path.stat().st_size
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"File quá lớn ({file_size / 1024 / 1024:.1f}MB). "
            f"Giới hạn: {MAX_FILE_SIZE_BYTES / 1024 / 1024:.0f}MB"
        )

    image_bytes = path.read_bytes()
    mime_type, _ = mimetypes.guess_type(file_path)
    return image_bytes, mime_type or "image/jpeg"


async def load_image(source: str) -> tuple[bytes, str]:
    """
    Load ảnh từ URL hoặc file path.

    Args:
        source: URL hoặc đường dẫn file ảnh.

    Returns:
        Tuple (image_bytes, mime_type)
    """
    if _is_url(source):
        return await _load_image_from_url(source)
    else:
        return _load_image_from_path(source)


async def extract_student_info(images: list[tuple[bytes, str]]) -> StudentInfo:
    """
    Gửi ảnh tới Gemini và trích xuất thông tin sinh viên.

    Args:
        images: Danh sách các tuple (image_bytes, mime_type).

    Returns:
        StudentInfo: Thông tin sinh viên trích xuất được.

    Raises:
        ValueError: Nếu không thể parse response từ Gemini.
        Exception: Nếu có lỗi khi gọi Gemini API.
    """
    logger.info(f"Sending {len(images)} images to Gemini...")

    parts = []
    for image_bytes, mime_type in images:
        parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
    
    parts.append(types.Part.from_text(text=EXTRACTION_PROMPT))

    import asyncio
    response = await asyncio.to_thread(
        client.models.generate_content,
        model=GEMINI_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=parts,
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=StudentInfo,
        ),
    )

    response_text = response.text
    logger.info(f"Gemini response: {response_text}")

    if not response_text:
        raise ValueError("Gemini trả về response rỗng")

    try:
        data = json.loads(response_text)
        return StudentInfo(**data)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Failed to parse Gemini response: {response_text}")
        raise ValueError(f"Không thể parse response từ Gemini: {e}")
