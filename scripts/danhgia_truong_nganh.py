import os
import json
from google import genai
from google.genai import types

# Khởi tạo client. Nó sẽ tự động đọc biến môi trường GEMINI_API_KEY
# export GEMINI_API_KEY="your_api_key_here"
GEMINI_API_KEY = "AIzaSyBygyI0ObjzetiVyA3_S_4FSt_R1Z1_UOU"
client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_university_and_major_data(university_query: str, major_query: str, gpa: str):
    # 1. Tạo Prompt kết hợp cả trường và ngành
    prompt = f"""
      User Input:
      1. University: "{university_query}"
      2. Major: "{major_query}"
      3. GPA: "{gpa}"
      
      Task A (University & Major):
      - Identify the university in Vietnam.
      - Identify the major and its reputation/standing at this specific university.
      - Get admission scores for this major of latest 3 years in scale of 30.
      - Estimate Tuition Average for this major (number in VND).
      - Provide a rating for this university (Top/Tốt/Khá/Trung bình/Kém).
      - Provide a rating for this major at this university (Top/Tốt/Khá/Trung bình/Kém).
      - Provide schoolScore100: a score for the university on a 100-point scale based on admission scores.
      - Provide majorScore100: a score for this specific major at this university on a 100-point scale.
      - Answer in Vietnamese
    """

    # 2. Ràng buộc chuẩn Schema JSON đồ sộ có cả object university và major
    evaluation_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "university": types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "name": types.Schema(type=types.Type.STRING, description="Official name of the university/college"),
                    "location": types.Schema(type=types.Type.STRING, description="City or Province of the university"),
                    "description": types.Schema(type=types.Type.STRING, description="Short description of the institution"),
                    "rating": types.Schema(
                        type=types.Type.STRING, 
                        enum=["Top", "Tốt", "Khá", "Trung bình", "Kém"],
                        description="General rating of this university"
                    ),
                    "schoolScore100": types.Schema(type=types.Type.NUMBER, description="Score for the university on a 100-point scale based on admission scores")
                },
                required=["name", "location", "rating", "schoolScore100"]
            ),
            "major": types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "name": types.Schema(type=types.Type.STRING, description="Official name of the major"),
                    "description": types.Schema(type=types.Type.STRING, description="Short description of this major at this university"),
                    "admissionScores": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "year": types.Schema(type=types.Type.STRING, description="Admission year, e.g. '2023'"),
                                "score": types.Schema(type=types.Type.NUMBER, description="Admission score on scale of 30")
                            },
                            required=["year", "score"]
                        ),
                        description="Admission scores for the latest 3 years on scale of 30"
                    ),
                    "tuition": types.Schema(type=types.Type.STRING, description="Tuition fee description"),
                    "tuitionAvg": types.Schema(type=types.Type.NUMBER, description="Numeric average tuition fee per year"),
                    "rating": types.Schema(
                        type=types.Type.STRING, 
                        enum=["Top", "Tốt", "Khá", "Trung bình", "Kém"],
                        description="Rating of this specific major at this specific university"
                    ),
                    "majorScore100": types.Schema(type=types.Type.NUMBER, description="Score for this specific major at this university on a 100-point scale")
                },
                required=["name", "admissionScores", "tuitionAvg", "rating", "majorScore100"]
            )
        },
        required=["university", "major"]
    )

    try:
        # 3. Gửi Request và Ép kiểu JSON 
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", 
                response_schema=evaluation_schema,
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

# --- CHẠY THỬ CODE ---
if __name__ == "__main__":
    result = fetch_university_and_major_data(
        university_query="Đại học Công Nghiệp Hà Nội", 
        major_query="Du lịch (Tiếng Anh)",
        gpa="3.5"
    )
    
    if result:
        # In ra màn hình định dạng JSON đẹp
        print(json.dumps(result, indent=2, ensure_ascii=False))
