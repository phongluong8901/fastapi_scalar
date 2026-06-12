from uuid import UUID
from redis.asyncio import Redis

from app.config import db_settings


_token_blacklist = Redis(
    host=db_settings.REDIS_HOST,
    port=db_settings.REDIS_PORT,
    db=0,
)
_shipment_verification_codes = Redis(
    host=db_settings.REDIS_HOST,
    port=db_settings.REDIS_PORT,
    db=1,
    decode_responses=True,
)

async def add_jti_to_blacklist(jti: str):
    await _token_blacklist.set(jti, "blacklisted")


async def is_jti_blacklisted(jti: str) -> bool:
    return await _token_blacklist.exists(jti)

async def add_shipment_verification_code(id: UUID, code: int):
    await _shipment_verification_codes.set(str(id), code)

async def get_shipment_verification_code(id: UUID) -> str:

    return str(await _shipment_verification_codes.get(str(id)))

# A. Quản lý Token (JTI Blacklist)
# jti: Là một ID duy nhất của một Token (JSON Web Token).

# add_jti_to_blacklist: Khi ai đó Logout, ta đẩy cái jti đó vào Redis với giá trị là "blacklisted".

# is_jti_blacklisted: Mỗi khi có request gửi lên, hệ thống sẽ kiểm tra Redis xem jti này có nằm trong "danh sách đen" không. Nếu có -> Chặn ngay lập tức.

# Tại sao dùng Redis? Vì việc kiểm tra này xảy ra hàng nghìn lần mỗi giây, Redis phản hồi trong micro-giây, nhanh hơn hàng trăm lần so với việc truy vấn vào SQL.

# B. Quản lý Mã xác thực đơn hàng (Shipment Verification Code)
# add_shipment_verification_code: Khi Shipper cần mã để giao hàng, bạn tạo mã đó và lưu vào Redis.

# get_shipment_verification_code: Khi Shipper nhập mã, bạn lấy từ Redis ra để so sánh.