import json
import logging
from google import genai
from typing import List, Optional
from fastapi import File, UploadFile, Form, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from scripts.gemini_client import extract_student_info, load_image
from scripts.danhgia_truong import fetch_university_data
from scripts.danhgia_truong_nganh import fetch_university_and_major_data

from models import ExtractionRequest, ExtractionResponse, ImageResult, StudentInfo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Gemini client
GEMINI_API_KEY = "AIzaSyAaMC9fnBnKXfpM9CJMTsk3NBIHRMH4a-8"
client = genai.Client(api_key=GEMINI_API_KEY)

# FastAPI app
app = FastAPI(
    title="Student Info Extraction API",
    description=(
        "API trích xuất thông tin sinh viên (Tên trường, Ngành học, GPA) "
        "từ ảnh bảng điểm/giấy tờ sinh viên sử dụng Google Gemini OCR.\n\n"
        "**Input**: Danh sách URL hoặc đường dẫn file ảnh.\n"
        "**Output**: Tên trường, ngành học, GPA cho từng ảnh."
    ),
    version="1.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend/
FRONTEND_DIR = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/", include_in_schema=False)
async def serve_ui():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/evaluate", include_in_schema=False)
async def serve_evaluate():
    return FileResponse(FRONTEND_DIR / "evaluate.html")

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "student-info-extraction"}

"""
test with param
curl "http://0.0.0.0:8188/api/extract?images=https://viet-tin-production.s3.hn-1.cloud.cmctelecom.vn/Images/689c78fcdce991a403d5e012.jpeg&images=https://viet-tin-production.s3.hn-1.cloud.cmctelecom.vn/Images/689c7926dce991a403d5e013.jpeg"
"""
async def _process_extraction(
    image_urls: List[str],
    uploaded_files: Optional[List[UploadFile]] = None,
) -> ExtractionResponse:
    """Shared extraction logic for both GET and POST endpoints."""
    loaded_images = []
    failed_sources = []
    all_sources = list(image_urls)

    # Load from URL list
    for source in all_sources:
        try:
            logger.info(f"Loading image from URL: {source}")
            image_bytes, mime_type = await load_image(source)
            loaded_images.append((image_bytes, mime_type))
        except Exception as e:
            logger.warning(f"❌ Failed to load {source}: {e}")
            failed_sources.append({"source": source, "error": str(e)})

    # Load from uploaded files
    if uploaded_files:
        for f in uploaded_files:
            try:
                logger.info(f"Loading uploaded file: {f.filename}")
                content = await f.read()
                mime = f.content_type or "image/jpeg"
                loaded_images.append((content, mime))
                all_sources.append(f.filename)
            except Exception as e:
                logger.warning(f"❌ Failed to read uploaded file {f.filename}: {e}")
                failed_sources.append({"source": f.filename, "error": str(e)})

    # Nếu không tải được ảnh nào
    if not loaded_images:
        results = [
            ImageResult(source=fs["source"], success=False, data=None, error=fs["error"])
            for fs in failed_sources
        ]
        return ExtractionResponse(
            success=False,
            total=len(all_sources),
            results=results,
            message="Không thể tải được bất kỳ ảnh nào",
        )

    try:
        # Gọi Gemini OCR với TẤT CẢ các ảnh trong 1 request
        student_info = await extract_student_info(loaded_images)
        school_name = student_info.school_name
        major = student_info.major
        gpa = student_info.gpa
        if major is None:
            major = ""
        if gpa is None:
            gpa = ""

        if school_name and major:
            university_data = fetch_university_and_major_data(client, school_name, major, gpa)
        elif school_name:
            raw = fetch_university_data(client, school_name, gpa)
            # Normalize flat → nested để frontend dùng chung 1 UI
            if raw:
                university_data = {
                    "university": {
                        "name": raw.get("name"),
                        "location": raw.get("location"),
                        "description": raw.get("description"),
                        "rating": raw.get("rating"),
                        "schoolScore100": raw.get("schoolScore100"),
                        "tuition": raw.get("tuition"),
                        "tuitionAvg": raw.get("tuitionAvg"),
                    },
                    "highlightMajors": raw.get("highlightMajors", []),
                }
            else:
                university_data = None
        else:
            university_data = None

        success_sources = [s for s in all_sources if not any(fs["source"] == s for fs in failed_sources)]

        # Kết quả chập (merged) từ tất cả ảnh thành công
        results = [
            ImageResult(
                source=", ".join(success_sources),
                success=True,
                data=student_info,
                error=None,
            )
        ]

        # Thêm các kết quả lỗi load ảnh (nếu có)
        for fs in failed_sources:
            results.append(
                ImageResult(
                    source=fs["source"],
                    success=False,
                    data=None,
                    error=fs["error"],
                )
            )

        logger.info(f"✅ Extracted successfully: {student_info}")
        logger.info(f"✅ Analyzed successfully: {university_data}")

        return ExtractionResponse(
            success=True,
            total=len(all_sources),
            results=results,
            message=f"Xử lý thành công {len(loaded_images)}/{len(all_sources)} ảnh",
            university_data=university_data,
        )

    except Exception as e:
        logger.error(f"❌ Gemini extraction failed: {e}")
        return ExtractionResponse(
            success=False,
            total=len(all_sources),
            results=[
                ImageResult(
                    source=", ".join(all_sources),
                    success=False,
                    data=None,
                    error=str(e),
                )
            ],
            message="Lỗi API trích xuất ảnh",
        )


@app.get(
    "/api/extract",
    response_model=ExtractionResponse,
    tags=["Extraction"],
    summary="Trích xuất thông tin sinh viên từ URL ảnh (GET)",
    description=(
        "Nhận danh sách URL ảnh qua query parameter 'images'.\n\n"
        "Ví dụ: `/api/extract?images=url1&images=url2`"
    ),
)
async def extract_info_get(
    images: List[str] = Query(..., description="Danh sách URL ảnh cần trích xuất"),
):
    return await _process_extraction(image_urls=images)


@app.post(
    "/api/extract",
    response_model=ExtractionResponse,
    tags=["Extraction"],
    summary="Trích xuất thông tin sinh viên từ nhiều ảnh cùng lúc (POST)",
    description=(
        "Nhận danh sách URL/đường dẫn file ảnh (qua form field 'images') "
        "hoặc upload file trực tiếp (qua form field 'files')."
    ),
)
async def extract_info_post(
    images: Optional[List[str]] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
):
    return await _process_extraction(
        image_urls=images or [],
        uploaded_files=files,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8188, reload=True)
