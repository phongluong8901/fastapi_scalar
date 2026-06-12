from datetime import datetime, timedelta, timezone

import jwt

from app.config import security_settings


def generate_access_token(
    data: dict,
    expiry: timedelta = timedelta(days=7),
) -> str:
    return jwt.encode(
        payload={
            **data,
            "exp": datetime.now(timezone.utc) + expiry,
        },
        algorithm=security_settings.JWT_ALGORITHM,
        key=security_settings.JWT_SECRET,
    )


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            jwt=token,
            key=security_settings.JWT_SECRET,
            algorithms=[security_settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None
    
#---
# 1. Cơ chế hoạt động: Từ dữ liệu thành Token
# Khi bạn gọi generate_access_token trong hàm token(...), nó thực hiện hai việc quan trọng:

# Gộp dữ liệu (Payload):

# Dữ liệu bạn truyền vào ("user": {"name": ..., "id": ...}) được đặt cạnh một key cực kỳ quan trọng là exp (Expiration).

# datetime.now(timezone.utc) + expiry: Dòng này tự động tính toán thời điểm token sẽ hết hạn (7 ngày kể từ lúc tạo).

# Ký số (Signing):

# jwt.encode không chỉ lưu dữ liệu, nó "ký" vào token bằng JWT_SECRET.

# Đây là "chữ ký" đảm bảo rằng nếu ai đó cố tình sửa đổi id hoặc name bên trong token sau khi nó được tạo ra, hệ thống sẽ biết ngay vì chữ ký sẽ không còn khớp với JWT_SECRET nữa.

# 2. Ý nghĩa của các tham số trong decode_access_token
# Khi bạn cần kiểm tra xem người dùng có phải là người thật hay không, bạn dùng hàm decode:

# jwt=token: Chuỗi token mà client gửi lên.

# key=security_settings.JWT_SECRET: Phải dùng đúng cái Secret đã dùng để tạo ra nó thì mới mở được.

# algorithms=[...]: Đây là bước bảo mật. Nó ép buộc chỉ chấp nhận các loại thuật toán mã hóa mà bạn tin tưởng (ví dụ HS256).