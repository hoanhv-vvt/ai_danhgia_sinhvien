import os
from dotenv import load_dotenv

load_dotenv()

# Gemini Configuration
# GEMINI_API_KEY: str = "AIzaSyB7P5nmxkM8mH4jXjLASFEtsZRXcJxQWH8"
GEMINI_API_KEY: str = "AIzaSyBygyI0ObjzetiVyA3_S_4FSt_R1Z1_UOU"
# GEMINI_API_KEY: str = "AIzaSyDnb5CbZ5oZ-N2A5z_ZgnLkH7XGspJAPyU"
# GEMINI_API_KEY: str = "AIzaSyACsUMsJE-cUTmr84iYO_hihSQrDTjZQO8"
GEMINI_MODEL: str = "gemini-2.5-flash"

# Upload Configuration
MAX_FILE_SIZE_MB: int = 10
MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_MIME_TYPES: set[str] = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}
ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
