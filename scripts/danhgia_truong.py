import os
import json
from google import genai
from google.genai import types

# Khởi tạo client. Nó sẽ tự động đọc biến môi trường GEMINI_API_KEY
# export GEMINI_API_KEY="your_api_key_here"
GEMINI_API_KEY = "AIzaSyB7P5nmxkM8mH4jXjLASFEtsZRXcJxQWH8"
client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_university_data(university_query: str, gpa: str, address_query: str = "N/A"):
    # 1. Tạo Prompt — không có ngành, lấy điểm chuẩn tiêu biểu các ngành trong trường
    prompt = f"""
      User Input:
      1. University: "{university_query}"
      2. GPA: "{gpa}"
      
      Task A (University):
      - Identify the university in Vietnam.
      - Get the latest admission score (thang 30), convert to scale 100.
      - List highlightMajors: top 3-5 representative majors with their typical admission scores.
      - Estimate Tuition Average (number in VND).
      - Provide a rating for this university.
      - Answer in Vietnamese
    """

    # 2. Ràng buộc chuẩn Schema JSON — flat object theo mẫu TypeScript
    university_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "name": types.Schema(type=types.Type.STRING, description="Official name of the university/college"),
            "location": types.Schema(type=types.Type.STRING, description="City or Province of the university"),
            "description": types.Schema(type=types.Type.STRING, description="Short description of the institution"),
            "admissionYear": types.Schema(type=types.Type.STRING, description="Year of data"),
            "scoreScale": types.Schema(type=types.Type.NUMBER, description="Original score scale"),
            "schoolScore100": types.Schema(type=types.Type.NUMBER, description="Converted score 0-100"),
            "rating": types.Schema(
                type=types.Type.STRING,
                enum=["Top", "Tốt", "Khá", "Trung bình", "Kém"]
            ),
            "tuition": types.Schema(type=types.Type.STRING),
            "tuitionAvg": types.Schema(type=types.Type.NUMBER),
            "highlightMajors": types.Schema(
                type=types.Type.ARRAY,
                description="Top 3-5 representative majors with typical admission scores",
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "majorName": types.Schema(type=types.Type.STRING),
                        "score": types.Schema(type=types.Type.STRING, description="Typical admission score, e.g. '25.5/30'")
                    },
                    required=["majorName", "score"]
                )
            ),
            "locationAnalysis": types.Schema(
                type=types.Type.OBJECT,
                nullable=True,
                properties={
                    "region": types.Schema(
                        type=types.Type.STRING,
                        enum=["urban", "suburban", "rural"],
                        description="Urban=City Center/Developed, Suburban=Outskirts, Rural=Countryside"
                    ),
                    "position": types.Schema(
                        type=types.Type.STRING,
                        enum=["main_street", "alley", "deep_alley"],
                        description="main_street=Mặt tiền/Đường lớn, alley=Hẻm xe hơi/Hẻm thông, deep_alley=Hẻm sâu/Nhiều xẹc/Hẻm cụt"
                    ),
                    "estimatedValue": types.Schema(type=types.Type.STRING, description="Brief assessment of real estate value"),
                    "riskAssessment": types.Schema(type=types.Type.STRING, description="Risk comment regarding asset liquidation or accessibility."),
                    "scoreModifier": types.Schema(type=types.Type.NUMBER, description="Suggested score 0-20 based on location value.")
                },
                required=["region", "position", "estimatedValue", "riskAssessment"]
            )
        },
        required=["name", "location", "schoolScore100", "rating", "highlightMajors", "tuition", "tuitionAvg"]
    )

    try:
        # 3. Gửi Request và Ép kiểu JSON
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=university_schema,
                temperature=0.2
            ),
        )

        # 4. JSON trả về có sẵn trong thẻ text. Parse nó
        if response.text:
            data = json.loads(response.text)
            return data
        else:
            return None

    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")
        return None

def fetch_university_data_vn(university_query: str, gpa: str, address_query: str = "N/A"):
    # 1. Tạo Prompt giống hệt của TypeScript
    prompt = f"""
      Dữ liệu đầu vào:
      1. Tên trường: "{university_query}"
      2. Địa chỉ sinh viên: "{address_query}"
      
      Nhiệm vụ A (Thông tin trường đại học):
      - Xác định trường đại học tại Việt Nam.
      - Lấy điểm chuẩn tuyển sinh, quy đổi sang thang 100.
      - Ước tính học phí trung bình (đơn vị VNĐ).
      - Trả lời bằng tiếng Việt.
      
      Nhiệm vụ B (Phân tích địa chỉ — CHỈ khi có địa chỉ):
      - Phân tích chuỗi "Địa chỉ sinh viên" để đánh giá tiềm năng/rủi ro bất động sản.
      - region: 'urban' (Trung tâm TP, Quận lớn), 'suburban' (Huyện, Ven đô), 'rural' (Tỉnh lẻ, Nông thôn).
      - position: 'main_street' (Không có từ khóa hẻm, ngõ, ngách), 'alley' (Hẻm xe hơi, Ngõ rộng), 'deep_alley' (Hẻm sâu, nhiều xẹc, ngách nhỏ, hẻm cụt).
      - Đánh giá rủi ro: Nhận xét về khả năng thanh khoản hoặc giá trị dựa theo vị trí.
      - Nếu địa chỉ bị thiếu hoặc không rõ nghĩa, trả về null cho locationAnalysis.
      - Trả lời bằng tiếng Việt.
    """


    # 2. Ràng buộc chuẩn Schema JSON đồ sộ
    university_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "name": types.Schema(type=types.Type.STRING, description="Official name of the university/college"),
            "location": types.Schema(type=types.Type.STRING, description="City or Province of the university"),
            "description": types.Schema(type=types.Type.STRING, description="Short description of the institution"),
            "admissionYear": types.Schema(type=types.Type.STRING, description="Year of data"),
            "scoreScale": types.Schema(type=types.Type.NUMBER, description="Original score scale"),
            "schoolScore100": types.Schema(type=types.Type.NUMBER, description="Converted score 0-100"),
            "rating": types.Schema(
                type=types.Type.STRING, 
                enum=["Top", "Tốt", "Khá", "Trung bình", "Kém"]
            ),
            "tuition": types.Schema(type=types.Type.STRING),
            "tuitionAvg": types.Schema(type=types.Type.NUMBER),
            "highlightMajors": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "majorName": types.Schema(type=types.Type.STRING),
                        "score": types.Schema(type=types.Type.STRING)
                    }
                )
            ),
            "locationAnalysis": types.Schema(
                type=types.Type.OBJECT,
                nullable=True,
                properties={
                    "region": types.Schema(
                        type=types.Type.STRING, 
                        enum=["urban", "suburban", "rural"], 
                        description="Urban=City Center/Developed, Suburban=Outskirts, Rural=Countryside"
                    ),
                    "position": types.Schema(
                        type=types.Type.STRING, 
                        enum=["main_street", "alley", "deep_alley"], 
                        description="main_street=Mặt tiền/Đường lớn, alley=Hẻm xe hơi/Hẻm thông, deep_alley=Hẻm sâu/Nhiều xẹc/Hẻm cụt"
                    ),
                    "estimatedValue": types.Schema(type=types.Type.STRING, description="Brief assessment of real estate value"),
                    "riskAssessment": types.Schema(type=types.Type.STRING, description="Risk comment regarding asset liquidation or accessibility."),
                    "scoreModifier": types.Schema(type=types.Type.NUMBER, description="Suggested score 0-20 based on location value.")
                },
                required=["region", "position", "estimatedValue", "riskAssessment"]
            )
        },
        required=["name", "location", "schoolScore100", "rating", "highlightMajors", "tuition", "tuitionAvg"]
    )

    try:
        # 3. Gửi Request và Ép kiểu JSON 
        response = client.models.generate_content(
            model="gemini-2.5-flash", # Thay model thành 2.5 flash tương tự model preview bên kia
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", 
                response_schema=university_schema,
                temperature=0.2 # Điểm số nên được kiểm soát, tránh ảo giác quá lớn
            ),
        )

        # 4. JSON trả về có sẵn trong thẻ text. Parse nó bằng file config:
        if response.text:
            data = json.loads(response.text)
            return data
        else:
            return None
            
    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")
        return None

# --- CHẠY THỬ CODE ---
if __name__ == "__main__":
    result = fetch_university_data(
        university_query="Trường Cao đẳng Kỹ nghệ II", 
        gpa="17",
    )
    
    if result:
        # In ra màn hình định dạng JSON đẹp
        print(json.dumps(result, indent=2, ensure_ascii=False))
