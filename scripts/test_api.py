import requests
import json

url = "http://localhost:8188/api/extract"

# Gửi URL trên mạng hoặc đường dẫn file cục bộ vào mảng này
payload = {
    "images": [
        "SV/sv_14_1.jpeg",
        "SV/sv_14_2.jpeg",
        # "SV/sv_8_3.jpeg",

        # "SV/sv_8_4.jpeg",
        # "SV/sv_8_5.jpeg",
        # "SV/sv_8_6.jpeg",
    ]
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print("Status Code:", response.status_code)
print("Response Body:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
