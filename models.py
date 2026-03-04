from pydantic import BaseModel, Field


class StudentInfo(BaseModel):
    """Thông tin sinh viên trích xuất từ ảnh."""

    school_name: str | None = Field(
        default=None,
        description="Tên trường học / đại học",
    )
    major: str | None = Field(
        default=None,
        description="Tên ngành học / chuyên ngành",
    )
    gpa: float | None = Field(
        default=None,
        description="Điểm trung bình tích lũy (GPA)",
    )


class ImageResult(BaseModel):
    """Kết quả trích xuất cho từng ảnh."""

    source: str = Field(description="URL hoặc path của ảnh gốc")
    success: bool = Field(description="Trạng thái xử lý ảnh này")
    data: StudentInfo | None = Field(
        default=None, description="Thông tin sinh viên trích xuất được"
    )
    error: str | None = Field(
        default=None, description="Thông báo lỗi nếu thất bại"
    )


class ExtractionRequest(BaseModel):
    """Request body cho API trích xuất."""

    images: list[str] = Field(
        description="Danh sách URL hoặc đường dẫn file ảnh",
        examples=[
            [
                "https://example.com/bangdiem.jpg",
                "/home/user/documents/transcript.png",
            ]
        ],
    )


class ExtractionResponse(BaseModel):
    """Response wrapper cho API trích xuất."""

    success: bool = Field(description="Trạng thái xử lý tổng thể")
    total: int = Field(description="Tổng số ảnh được xử lý")
    results: list[ImageResult] = Field(
        default_factory=list, description="Kết quả trích xuất cho từng ảnh"
    )
    message: str | None = Field(
        default=None, description="Thông báo bổ sung"
    )
    university_data: dict | None = Field(
        default=None, description="Kết quả phân tích trường/ngành từ Gemini"
    )

