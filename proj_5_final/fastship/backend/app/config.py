from pathlib import Path                   # Dùng để xử lý đường dẫn file/thư mục một cách thông minh
from pydantic_settings import BaseSettings, SettingsConfigDict # Thư viện Pydantic để quản lý cấu hình
from urllib.parse import quote_plus        # Dùng để mã hóa các ký tự đặc biệt trong URL (như mật khẩu DB)

# Lấy đường dẫn của file hiện tại, rồi lấy cha của cha (parent.parent) để ra thư mục gốc dự án
PROJECT_DIR = Path(__file__).resolve().parent.parent


_base_config = SettingsConfigDict(
    env_file=PROJECT_DIR / ".env",  # Chỉ định file chứa các biến môi trường
    # env_file="/home/mbw2025/fastapi_2/proj_5_final/backend/.env",
    env_ignore_empty=True,          # Bỏ qua các biến môi trường không có giá trị
    extra="ignore",                 # Nếu file .env có biến lạ không được định nghĩa trong class thì bỏ qua
)


class AppSettings(BaseSettings):
    APP_NAME: str = "FastShip"      # Tên ứng dụng, có giá trị mặc định
    APP_DOMAIN: str = "localhost:8000" # Domain mặc định


class DatabaseSettings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: str

    model_config = _base_config

    @property                       # Biến thành thuộc tính (truy cập bằng .POSTGRES_URL)
    def POSTGRES_URL(self):         # Tạo chuỗi kết nối DB tự động
        user = quote_plus(self.POSTGRES_USER) # Mã hóa username để tránh lỗi ký tự đặc biệt
        pwd = quote_plus(self.POSTGRES_PASSWORD) # Mã hóa mật khẩu
        return f"postgresql+asyncpg://{user}:{pwd}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def REDIS_URL(self, db):        # Hàm tạo URL Redis cho một DB cụ thể
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{db}"


class SecuritySettings(BaseSettings):

    JWT_SECRET: str
    JWT_ALGORITHM: str

    model_config = _base_config


class NotificationSettings(BaseSettings):
    # Các cấu hình cho Email (SMTP) và SMS (Twilio)
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    TWILIO_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_NUMBER: str

    model_config = _base_config

# Nạp dữ liệu từ file .env vào các đối tượng cụ thể
app_settings = AppSettings()
db_settings = DatabaseSettings()
security_settings = SecuritySettings()
notification_settings = NotificationSettings()

#---
# Trong Python, @property là một "decorator" giúp bạn biến một phương thức (hàm) thành một thuộc tính (biến).

# Thông thường, khi muốn lấy giá trị từ một hàm, bạn phải gọi nó kèm theo dấu ngoặc đơn (). Nhưng với @property, bạn có thể gọi nó giống như gọi một biến thông thường (không cần ngoặc).

# 1. Sự khác biệt cụ thể
# Hãy xem ví dụ so sánh dưới đây:

# Cách thông thường (không dùng @property):

# Python


# class DatabaseSettings:
#     def get_url(self):
#         return "postgresql://user:pass@localhost:5432/db"

# db = DatabaseSettings()
# print(db.get_url())  # Phải có dấu () để gọi hàm
# Cách dùng @property (như trong code của bạn):

# Python


# class DatabaseSettings:
#     @property
#     def POSTGRES_URL(self):
#         return "postgresql://user:pass@localhost:5432/db"

# db = DatabaseSettings()
# print(db.POSTGRES_URL) # Không cần (), trông giống như một biến bình thường