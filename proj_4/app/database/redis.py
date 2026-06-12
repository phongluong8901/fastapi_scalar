from redis.asyncio import Redis         # Nhập thư viện Redis hỗ trợ lập trình bất đồng bộ (async)
from app.config import db_settings      # Nhập cấu hình kết nối Redis (Host, Port...)

# Khởi tạo kết nối tới Redis
_token_blacklist = Redis(
    host=db_settings.REDIS_HOST,        # Địa chỉ server Redis
    port=db_settings.REDIS_PORT,        # Cổng kết nối Redis
    db=0,                               # Chọn database 0 (mặc định)
)

# Hàm thêm JTI vào danh sách đen (khi người dùng đăng xuất)
async def add_jti_to_blacklist(jti: str):
    # Lưu JTI vào Redis với giá trị là "blacklisted"
    # JTI (JWT ID) là định danh duy nhất của mỗi token
    await _token_blacklist.set(jti, "blacklisted")

# Hàm kiểm tra xem JTI có bị liệt vào danh sách đen không
async def is_jti_blacklisted(jti: str) -> bool:
    # Kiểm tra xem khóa jti có tồn tại trong Redis không
    return await _token_blacklist.exists(jti)

#---
# Đoạn code này là một phần trong hệ thống Quản lý đăng xuất (Logout) hoặc Thu hồi Token bằng cách sử dụng Redis làm kho lưu trữ nhanh (In-memory store).