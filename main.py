import json
import logging
from typing import List, Optional
from fastapi import File, UploadFile, Form, FastAPI, HTTPException
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


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "student-info-extraction"}


@app.post(
    "/api/extract",
    response_model=ExtractionResponse,
    tags=["Extraction"],
    summary="Trích xuất thông tin sinh viên từ nhiều ảnh cùng lúc",
    description=(
        "Nhận danh sách URL/đường dẫn file ảnh (qua form field 'images') "
        "hoặc upload file trực tiếp (qua form field 'files')."
    ),
)
async def extract_info(
    images: Optional[List[str]] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
):
    loaded_images = []
    failed_sources = []
    all_sources = images or []

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
    if files:
        for f in files:
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

        # school_name = "Đại học Công Nghiệp Hà Nội"
        # major = "Du lịch (Tiếng Anh)"
        # major = ""
        # gpa = "3.5"
        # student_info = StudentInfo(school_name=school_name, major=major or None, gpa=gpa or None)


        if school_name and major:
            university_data = fetch_university_and_major_data(school_name, major, gpa)

            # university_data = {
            #     "university": {
            #         "name": "Đại học Công Nghiệp Hà Nội",
            #         "location": "Hà Nội",
            #         "description": "Đại học Công Nghiệp Hà Nội là một trường đại học công lập lớn, đa ngành, có truyền thống lâu đời tại Việt Nam, chuyên đào tạo nguồn nhân lực chất lượng cao trong các lĩnh vực công nghiệp, kỹ thuật, kinh tế và dịch vụ.",
            #         "rating": "Tốt",
            #         "schoolScore100": 78,
            #     },
            #     "major": {
            #         "name": "Du lịch (Tiếng Anh)",
            #         "description": "Chương trình Du lịch (Tiếng Anh) tại Đại học Công Nghiệp Hà Nội đào tạo sinh viên có kiến thức chuyên sâu về ngành du lịch, quản lý lữ hành, khách sạn và dịch vụ, đồng thời trang bị khả năng sử dụng tiếng Anh thành thạo trong môi trường làm việc quốc tế.",
            #         "admissionScores": [
            #         {
            #             "year": "2023",
            #             "score": 23.5
            #         },
            #         {
            #             "year": "2022",
            #             "score": 23.5
            #         },
            #         {
            #             "year": "2021",
            #             "score": 23.65
            #         }
            #         ],
            #         "tuition": "Học phí trung bình khoảng 20.000.000 VNĐ/năm học, có thể điều chỉnh theo quy định của nhà nước và trường qua từng năm.",
            #         "tuitionAvg": 20000000,
            #         "majorScore100": 60,
            #         "rating": "Khá"
            #     }
            #     }
            
        elif school_name:
            # print(">> GO IN HERE")
            # raw = {
            #     "name": "Trường Cao đẳng Kỹ nghệ II",
            #     "location": "Thành phố Hồ Chí Minh",
            #     "schoolScore100": 51.7,
            #     "rating": "Trung bình",
            #     "highlightMajors": [
            #         {"majorName": "Công nghệ ô tô", "score": "15.0/30"},
            #         {"majorName": "Công nghệ thông tin", "score": "15.0/30"},
            #         {"majorName": "Kỹ thuật điện", "score": "15.0/30"},
            #         {"majorName": "Kế toán", "score": "15.0/30"},
            #         {"majorName": "Quản trị kinh doanh", "score": "15.0/30"}
            #     ],
            #     "tuition": "Khoảng 12.000.000 - 16.000.000 VNĐ/năm học",
            #     "tuitionAvg": 14000000,
            #     "admissionYear": "2023",
            #     "description": "Trường Cao đẳng Kỹ nghệ II là cơ sở đào tạo nghề uy tín tại Thành phố Hồ Chí Minh.",
            #     "scoreScale": 30
            # }

            raw = fetch_university_data(school_name, gpa)

            # Normalize flat → nested để frontend dùng chung 1 UI
            university_data = {
                "university": {
                    "name": raw.get("name"),
                    "location": raw.get("location"),
                    "description": raw.get("description"),
                    "admissionYear": raw.get("admissionYear"),
                    "schoolScore100": raw.get("schoolScore100"),
                    "rating": raw.get("rating"),
                    "tuition": raw.get("tuition"),
                    "tuitionAvg": raw.get("tuitionAvg"),
                },
                "highlightMajors": raw.get("highlightMajors", []),
            }
        else:
            logger.info(">> NO SCHOOL AND NO MAJOR")
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8188, reload=True)
